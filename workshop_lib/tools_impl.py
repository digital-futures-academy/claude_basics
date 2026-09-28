"""Tool implementations: the Python that runs when Claude calls a tool.

The JSON *schemas and descriptions* Claude sees are written in the notebook, because writing them
is part of the lesson. This module only holds the code behind them.

Conventions every tool follows:
  * Return a JSON-serialisable dict.
  * Errors are returned as structured data, not raised:
        {"isError": True, "errorCategory": "...", "isRetryable": bool, "message": "..."}
    so the agent can decide whether to retry, change approach or report the gap.
"""
from __future__ import annotations

import json
import re
import datetime as dt
from dataclasses import asdict, dataclass, field
from urllib.parse import urlparse

from . import config


def tool_error(category: str, message: str, retryable: bool = False, **extra) -> dict:
    return {"isError": True, "errorCategory": category, "isRetryable": retryable, "message": message, **extra}


# =============================================================================== web research
class SearchSession:
    """Remembers every search result an agent has seen, so claims can be checked against real text."""

    def __init__(self):
        self.seen: dict[str, dict] = {}      # url -> result
        self.log: list[dict] = []            # (query, mode, n_results)


_CACHE = None


def _load_cache() -> dict:
    global _CACHE
    if _CACHE is None:
        _CACHE = json.loads((config.DATA_DIR / "search_cache.json").read_text(encoding="utf-8"))
    return _CACHE


def _cache_search(query: str, max_results: int) -> list[dict]:
    q = f" {query.lower()} "
    qwords = set(re.findall(r"[a-z0-9]+", q))
    scored = []
    for slug, entry in _load_cache()["entries"].items():
        if not any(re.search(rf"(?<![a-z0-9]){re.escape(a.strip())}(?![a-z])", q) for a in entry["aliases"]):
            continue
        for r in entry["results"]:
            overlap = len(qwords & set(re.findall(r"[a-z0-9]+", (r["title"] + " " + r["content"]).lower())))
            scored.append((overlap, r))
    scored.sort(key=lambda x: -x[0])
    return [r for _, r in scored[:max_results]]


def parse_date(value: str | None, url: str = "") -> str | None:
    """Best-effort ISO date (YYYY-MM-DD) from ISO strings, RFC-2822 ('Mon, 22 Sep 2026 10:00:00 GMT') or the URL."""
    from email.utils import parsedate_to_datetime

    if value:
        v = str(value).strip()
        try:
            return dt.date.fromisoformat(v[:10]).isoformat()
        except ValueError:
            pass
        try:
            return parsedate_to_datetime(v).date().isoformat()
        except (TypeError, ValueError):
            pass
    m = re.search(r"/(20\d{2})/(\d{1,2})/(\d{1,2})/", url or "")
    if m:
        try:
            return dt.date(int(m[1]), int(m[2]), int(m[3])).isoformat()
        except ValueError:
            return None
    return None


def web_search(session: SearchSession, query: str, max_results: int = 5) -> dict:
    query = (query or "").strip()
    if not query:
        return tool_error("validation", "query must be a non-empty string")
    max_results = max(1, min(int(max_results or 5), 8))
    mode, results, note = "tavily", [], None
    if config.TAVILY_API_KEY:
        try:
            from tavily import TavilyClient

            resp = TavilyClient(api_key=config.TAVILY_API_KEY).search(
                query=query, max_results=max_results, search_depth="basic")
            results = [{"title": r.get("title"), "url": r.get("url"), "content": r.get("content") or "",
                        "published_date": parse_date(r.get("published_date"), r.get("url", ""))}
                       for r in resp.get("results", []) if r.get("url")]
        except Exception as e:
            mode, note = "cache", f"Tavily failed ({type(e).__name__}); served offline cache instead"
    else:
        mode, note = "cache", "No TAVILY_API_KEY; served offline cache (captured 2026-09-28)"
    if mode == "cache":
        results = _cache_search(query, max_results)
    for r in results:
        r["source_tier"] = score_source(r["url"])["tier"]
        session.seen[r["url"]] = r
    session.log.append({"query": query, "mode": mode, "n_results": len(results)})
    out = {"query": query, "mode": mode, "retrieved_at": dt.datetime.now().isoformat(timespec="seconds"),
           "results": results}
    if note:
        out["note"] = note
    if not results:
        out["note"] = (note or "") + " | No results. Try a more specific query naming the organisation."
    return out


TIER1 = ["anthropic.com", "openai.com", "mistral.ai", "deepseek.com", "ai.meta.com", "about.fb.com",
         "research.meta.ai", "llama.com", "aboutamazon.com", "aws.amazon.com", "amazon.science", "blog.google",
         "deepmind.google", "abc.xyz", "q4cdn.com", "qwenlm.github.io", "qwen.ai", "alibabacloud.com",
         "alibabagroup.com", "sec.gov", "prnewswire.com", "businesswire.com", "huggingface.co/blog"]
TIER2 = ["reuters.com", "bloomberg.com", "ft.com", "cnbc.com", "techcrunch.com", "theverge.com", "wsj.com",
         "nytimes.com", "axios.com", "geekwire.com", "theregister.com", "venturebeat.com", "fortune.com",
         "forbes.com", "theinformation.com", "technode.com", "the-decoder.com", "investing.com", "wired.com",
         "arstechnica.com", "bbc.co.uk", "bbc.com", "theguardian.com", "economist.com", "scmp.com", "semafor.com"]


def score_source(url: str) -> dict:
    """Deterministic credibility tier for a URL (see review_policy.md, RP-2)."""
    if not url or not url.startswith("http"):
        return tool_error("validation", "url must be an absolute http(s) URL", tier=None)
    p = urlparse(url)
    host = p.netloc.lower().removeprefix("www.")
    full = host + p.path.lower()
    if any(host == d or host.endswith("." + d) or ("/" in d and (full + "/").startswith(d + "/")) for d in TIER1):
        return {"url": url, "domain": host, "tier": 1, "label": "primary source"}
    if any(host == d or host.endswith("." + d) for d in TIER2):
        return {"url": url, "domain": host, "tier": 2, "label": "established news outlet"}
    return {"url": url, "domain": host, "tier": 3, "label": "secondary / unvetted (wiki, blog, aggregator)"}


# =============================================================================== figures
_MULT = {"thousand": 1e3, "k": 1e3, "million": 1e6, "mn": 1e6, "m": 1e6, "billion": 1e9, "bn": 1e9, "b": 1e9,
         "trillion": 1e12, "tn": 1e12, "t": 1e12}
_CUR_SYM = {"us$": "USD", "$": "USD", "€": "EUR", "£": "GBP", "¥": "CNY"}
_CUR_WORD = {"usd": "USD", "dollar": "USD", "dollars": "USD", "eur": "EUR", "euro": "EUR", "euros": "EUR",
             "gbp": "GBP", "pound": "GBP", "pounds": "GBP", "rmb": "CNY", "cny": "CNY", "yuan": "CNY"}
_UNITS = {"tokens": "tokens", "token": "tokens", "parameters": "parameters", "params": "parameters",
          "users": "users", "mau": "users", "wau": "users", "gpus": "gpus", "gpu": "gpus", "downloads": "downloads",
          "%": "%", "percent": "%", "gw": "gw", "employees": "employees"}
_NUM = re.compile(r"(?P<pre>us\$|\$|€|£|¥|\b(?:usd|eur|gbp|rmb|cny)\b)?\s*(?P<num>\d+(?:\.\d+)?)\s*"
                  r"(?P<mult>thousand|trillion|billion|million|bn|mn|tn|k|m|b|t)?(?![a-z])\s*(?P<post>€|\$|£|¥)?")


def normalise_figure(value: str) -> dict:
    """'$965bn' -> {'amount': 9.65e11, 'currency': 'USD'}; '10M-token' -> {'amount': 1e7, 'unit': 'tokens'}.
    If the text holds several numbers, the first one with a currency or multiplier wins (so years such as
    '2026' are skipped). Pass the figure alone when you can."""
    if value is None or not str(value).strip():
        return tool_error("validation", "value must be a non-empty string such as '$965 billion' or '1.6T'")
    s = str(value).strip().lower().replace(",", "").replace("~", "").replace("≈", "")
    matches = list(_NUM.finditer(s))
    if not matches:
        return tool_error("validation", f"could not find a number in {value!r}")
    m = next((m for m in matches if m["pre"] or m["mult"] or m["post"]), matches[0])
    amount = round(float(m["num"]) * _MULT.get(m["mult"] or "", 1), 4)
    sym = m["pre"] or m["post"] or ""
    cur = _CUR_SYM.get(sym) or _CUR_WORD.get(sym.strip())
    rest = s[m.end():]
    if not cur:
        w = re.match(r"\s*-?\s*([a-z]+)", rest)
        cur = _CUR_WORD.get(w[1]) if w else None
    unit = None
    for word in re.findall(r"[a-z]+|%", rest[:40]):
        if word in _UNITS:
            unit = _UNITS[word]
            break
    out = {"input": value, "amount": amount, "currency": cur, "unit": unit,
           "pretty": f"{amount:,.0f}" if amount >= 1000 else str(amount)}
    if len(matches) > 1:
        out["note"] = f"{len(matches)} numbers found; used {m.group(0).strip()!r}. Pass one figure at a time."
    return out


def compare_figures(claim_value: str, kb_value: str) -> dict:
    """Deterministic comparison using the RP-4 tolerance bands (2% / 10%)."""
    a, b = normalise_figure(claim_value), normalise_figure(kb_value)
    for side, r in (("claim_value", a), ("kb_value", b)):
        if r.get("isError"):
            return tool_error("validation", f"{side}: {r['message']}")
    kind_a, kind_b = a["currency"] or a["unit"], b["currency"] or b["unit"]
    if kind_a and kind_b and kind_a != kind_b:
        return {"band": "UNIT_MISMATCH", "claim": a, "kb": b,
                "message": f"Units/currencies differ ({kind_a} vs {kind_b}); do not convert, report both."}
    if b["amount"] == 0:
        return tool_error("validation", "kb_value is zero; cannot compute a relative difference")
    pct = abs(a["amount"] - b["amount"]) / abs(b["amount"]) * 100
    band = "SUPPORTED" if pct <= 2 else "MINOR_DIFFERENCE" if pct <= 10 else "CONTRADICTED"
    return {"band": band, "pct_difference": round(pct, 2), "claim_amount": a["amount"], "kb_amount": b["amount"]}


# =============================================================================== claim ledger (lineage)
@dataclass
class Claim:
    claim_id: str
    entity: str
    attribute: str
    value: str
    normalised: dict
    source_url: str
    source_title: str
    source_tier: int | None
    published_date: str | None
    quote: str
    quote_verified: bool
    hedged: bool
    search_mode: str | None
    recorded_by: str = "web-researcher"
    recorded_at: str = field(default_factory=lambda: dt.datetime.now().isoformat(timespec="seconds"))


class ClaimLedger:
    """Append-only record of every claim, with where it came from. Shared state lives in code,
    not in a model's context window."""

    def __init__(self):
        self.claims: dict[str, Claim] = {}
        self.verdicts: dict[str, dict] = {}

    def as_rows(self) -> list[dict]:
        rows = []
        for cid, c in self.claims.items():
            v = self.verdicts.get(cid, {})
            rows.append({"claim_id": cid, "entity": c.entity, "attribute": c.attribute, "web_value": c.value,
                         "source": urlparse(c.source_url).netloc.removeprefix("www."), "tier": c.source_tier,
                         "quote_ok": c.quote_verified, "verdict": v.get("verdict", "-"),
                         "kb_value": v.get("kb_value", "-"), "kb_chunk": v.get("kb_chunk_id", "-"),
                         "kb_possibly_wrong": v.get("kb_possibly_wrong", False)})
        return rows


_PUNCT = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
                        "−": "-", " ": " "})


def _norm_ws(s: str) -> str:
    """Normalise text for the quote check: unicode form, curly quotes and dashes, whitespace, case,
    and quote marks or ellipses wrapped around the quote."""
    import unicodedata

    s = unicodedata.normalize("NFKC", s or "").translate(_PUNCT)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s.strip(" \"'.…")


def record_claim(ledger: ClaimLedger, session: SearchSession, entity: str, attribute: str, value: str,
                 source_url: str, quote: str, hedged: bool = False) -> dict:
    missing = [k for k, v in {"entity": entity, "attribute": attribute, "value": value,
                              "source_url": source_url, "quote": quote}.items() if not v]
    if missing:
        return tool_error("validation", f"missing required fields: {missing}")
    src = session.seen.get(source_url)
    if src is None:
        return tool_error("validation", "source_url was not returned by any web_search in this session. "
                          "Only record claims from pages you actually retrieved.", retryable=True)
    # Programmatic grounding check: is the quote really in the retrieved text?
    verified = _norm_ws(quote) in _norm_ws(src.get("content", "") + " " + src.get("title", ""))
    cid = f"C-{len(ledger.claims) + 1:03d}"
    claim = Claim(claim_id=cid, entity=entity, attribute=attribute, value=value,
                  normalised={k: v for k, v in normalise_figure(value).items() if k in ("amount", "currency", "unit")},
                  source_url=source_url, source_title=src.get("title") or "", source_tier=src.get("source_tier"),
                  published_date=src.get("published_date"), quote=quote, quote_verified=verified,
                  hedged=hedged if isinstance(hedged, bool) else str(hedged).lower() in ("true", "1", "yes"),
                  search_mode=next((l["mode"] for l in reversed(session.log)), None))
    ledger.claims[cid] = claim
    out = {"claim_id": cid, "quote_verified": verified}
    if not verified:
        out["warning"] = ("Quote not found verbatim in the retrieved text. Copy an exact sentence fragment from the "
                          "result's content, or the reviewer will reject this claim (RP-1).")
    return out


# =============================================================================== policy checks
FINANCIAL = {"financial", "user_metric"}


def check_source_policy(source_url: str, published_date: str | None, claim_type: str,
                        quote_verified: bool, hedged: bool = False) -> dict:
    if isinstance(quote_verified, str):
        quote_verified = quote_verified.lower() == "true"
    """Apply the machine-checkable rules of review_policy.md (RP-1, RP-2, RP-3)."""
    flags, violations = [], []
    if not source_url:
        violations.append("RP-1: no source URL")
    if not quote_verified:
        violations.append("RP-1: supporting quote not verified against retrieved text")
    tier = score_source(source_url).get("tier") if source_url else None
    if claim_type in FINANCIAL and tier == 3:
        flags.append("RP-2: needs_corroboration (financial/user claim backed only by a tier-3 source)")
    age_days = None
    if published_date:
        try:
            iso = parse_date(published_date)
            if iso is None:
                raise ValueError(published_date)
            age_days = (dt.date.fromisoformat(config.TODAY) - dt.date.fromisoformat(iso)).days
            if claim_type in FINANCIAL and age_days > 365:
                flags.append(f"RP-3: stale ({age_days} days old)")
        except ValueError:
            flags.append("RP-3: unparseable published_date")
    else:
        flags.append("RP-3: no publication date; recency unknown")
    return {"passes_hard_rules": not violations, "violations": violations, "flags": flags,
            "source_tier": tier, "age_days": age_days, "today": config.TODAY}
