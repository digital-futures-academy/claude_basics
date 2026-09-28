"""Knowledge-base retrieval: markdown -> section chunks -> mistral-embed -> FAISS.

The index is cached in .cache/ and rebuilt automatically when any KB file changes,
so the embedding cost is paid once (about 150 chunks, a fraction of a cent).

If the embeddings API cannot be reached, a keyword (TF-IDF) fallback keeps the demo running.
Every result says which retrieval mode produced it, so learners can see it.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from . import config


@dataclass
class Chunk:
    chunk_id: str        # e.g. "anthropic#funding-ownership-and-valuation"
    doc_id: str
    title: str
    section: str
    kb_version: str
    last_verified: str
    text: str


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _front_matter(md: str) -> tuple[dict, str]:
    meta = {}
    if md.startswith("---"):
        _, fm, body = md.split("---", 2)
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        return meta, body
    return meta, md


def load_chunks(kb_dir: Path = config.KB_DIR, max_words: int = 320) -> list[Chunk]:
    """Split every KB doc on '## ' headings. Long sections are split on paragraph boundaries."""
    chunks: list[Chunk] = []
    for path in sorted(Path(kb_dir).glob("*.md")):
        meta, body = _front_matter(path.read_text(encoding="utf-8"))
        doc_id = meta.get("doc_id", path.stem)
        title = meta.get("title", doc_id)
        org = title.split("—")[0].strip()
        for block in re.split(r"\n(?=## )", body):
            block = block.strip()
            if not block.startswith("## "):
                continue
            heading, _, content = block.partition("\n")
            section = heading[3:].strip()
            if section.lower() == "sources":
                continue                      # URLs only: poor retrieval targets
            paras, parts, cur = content.strip().split("\n\n"), [], []
            for p in paras:
                if cur and len(" ".join(cur + [p]).split()) > max_words:
                    parts.append("\n\n".join(cur)); cur = []
                cur.append(p)
            if cur:
                parts.append("\n\n".join(cur))
            for i, part in enumerate(parts):
                suffix = f"-{i+1}" if len(parts) > 1 else ""
                chunks.append(Chunk(
                    chunk_id=f"{doc_id}#{_slug(section)}{suffix}",
                    doc_id=doc_id, title=title, section=section,
                    kb_version=meta.get("kb_version", "?"), last_verified=meta.get("last_verified", "?"),
                    # Prefix the org + section so a chunk makes sense on its own (helps embeddings too).
                    text=f"{org} — {section}\n{part}",
                ))
    return chunks


# ----------------------------------------------------------------------------- embeddings
def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    import httpx

    if not config.OPENROUTER_API_KEY:
        raise RuntimeError("no OpenRouter key")
    vecs = []
    with httpx.Client(timeout=60) as http:
        for i in range(0, len(texts), batch_size):
            r = http.post(
                f"{config.OPENROUTER_BASE_URL}/v1/embeddings",
                headers={"Authorization": f"Bearer {config.OPENROUTER_API_KEY}"},
                json={"model": config.EMBED_MODEL, "input": texts[i:i + batch_size]},
            )
            r.raise_for_status()
            data = sorted(r.json()["data"], key=lambda d: d["index"])
            vecs.extend(d["embedding"] for d in data)
    arr = np.asarray(vecs, dtype="float32")
    arr /= np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12     # cosine similarity via inner product
    return arr


class _KeywordIndex:
    """Tiny TF-IDF fallback so retrieval still works with no embeddings API."""

    def __init__(self, texts: list[str]):
        self.docs = [Counter(self._tok(t)) for t in texts]
        df = Counter(w for d in self.docs for w in d)
        n = len(texts)
        self.idf = {w: math.log((n + 1) / (c + 0.5)) for w, c in df.items()}

    @staticmethod
    def _tok(t: str) -> list[str]:
        return re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", t.lower())

    def search(self, q: str, k: int) -> list[tuple[int, float]]:
        qt = self._tok(q)
        scores = []
        for i, d in enumerate(self.docs):
            s = sum(self.idf.get(w, 0) * (1 + math.log(d[w])) for w in qt if d[w])
            scores.append((i, s / (1 + math.log(1 + sum(d.values())))))
        scores.sort(key=lambda x: -x[1])
        return scores[:k]


class KnowledgeBase:
    def __init__(self, kb_dir: Path = config.KB_DIR, force_rebuild: bool = False, verbose: bool = True):
        self.chunks = load_chunks(kb_dir)
        self.mode = "faiss"
        self._kw = _KeywordIndex([c.text for c in self.chunks])
        fingerprint = hashlib.sha256(
            (config.EMBED_MODEL + "".join(c.chunk_id + c.text for c in self.chunks)).encode()
        ).hexdigest()[:16]
        config.CACHE_DIR.mkdir(exist_ok=True)
        idx_path = config.CACHE_DIR / f"kb_{fingerprint}.faiss"
        try:
            import faiss

            if idx_path.exists() and not force_rebuild:
                # (de)serialise via bytes: faiss's own file I/O breaks on non-ASCII Windows paths
                self.index = faiss.deserialize_index(np.frombuffer(idx_path.read_bytes(), dtype="uint8"))
                how = "loaded cached index"
            else:
                vecs = embed_texts([c.text for c in self.chunks])
                self.index = faiss.IndexFlatIP(vecs.shape[1])
                self.index.add(vecs)
                idx_path.write_bytes(faiss.serialize_index(self.index).tobytes())
                how = f"embedded {len(self.chunks)} chunks with {config.EMBED_MODEL}"
        except Exception as e:  # network or key problem: degrade, but say so loudly
            self.index, self.mode = None, "keyword-fallback"
            how = f"EMBEDDINGS UNAVAILABLE ({type(e).__name__}: {str(e)[:80]}) -> using keyword fallback"
        if verbose:
            docs = sorted({c.doc_id for c in self.chunks})
            print(f"Knowledge base: {len(docs)} docs, {len(self.chunks)} chunks | {how}")

    def documents(self) -> list[dict]:
        seen = {}
        for c in self.chunks:
            d = seen.setdefault(c.doc_id, {"doc_id": c.doc_id, "title": c.title, "kb_version": c.kb_version,
                                           "last_verified": c.last_verified, "sections": []})
            if c.section not in d["sections"]:
                d["sections"].append(c.section)
        return list(seen.values())

    def search(self, query: str, k: int = 4, doc_id: str | None = None) -> list[dict]:
        pool = k * 6 if doc_id else k
        mode = self.mode
        hits = None
        if self.index is not None:
            try:
                qv = embed_texts([query])
                scores, ids = self.index.search(qv, min(pool, len(self.chunks)))
                hits = list(zip(ids[0].tolist(), scores[0].tolist()))
            except Exception:           # embeddings API hiccup mid-demo: degrade, and label it
                mode = "keyword-fallback"
        if hits is None:
            hits = self._kw.search(query, pool)
        out = []
        for i, s in hits:
            c = self.chunks[i]
            if doc_id and c.doc_id != doc_id:
                continue
            out.append({**asdict(c), "score": round(float(s), 3), "retrieval_mode": mode})
            if len(out) == k:
                break
        return out
