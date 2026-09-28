"""Configuration and API clients for the workshop.

Everything goes through OpenRouter:
  * Claude models are called through OpenRouter's Anthropic-compatible Messages API, so we
    use the official `anthropic` SDK with base_url="https://openrouter.ai/api".
  * Embeddings (mistral-embed) are called through OpenRouter's OpenAI-compatible
    /api/v1/embeddings endpoint.
"""
from __future__ import annotations

import datetime as _dt
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(find_dotenv(usecwd=True) or ROOT / ".env")
for _k in [k for k in os.environ if k.startswith("\ufeff")]:    # .env saved with a BOM (old Notepad)
    os.environ.setdefault(_k.lstrip("\ufeff"), os.environ[_k])

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api")         # the anthropic SDK appends /v1/messages
OPENROUTER_API_KEY = next((os.environ[k].strip() for k in ("OPENROUTER_API_KEY", "OPENROUTER_KEY", "OPEN_ROUTER_API_KEY")
                           if os.environ.get(k, "").strip()), "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

# Model tiering: a capable model coordinates; cheaper, faster models do the narrow specialist work.
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "anthropic/claude-sonnet-5")
SPECIALIST_MODEL = os.getenv("SPECIALIST_MODEL", "anthropic/claude-haiku-4.5")
EMBED_MODEL = os.getenv("EMBED_MODEL", "mistralai/mistral-embed-2312")

# USD per million tokens (input, output) on OpenRouter, checked 2026-09-28. Used only for the cost read-out.
PRICES = {
    "anthropic/claude-opus-5.5": (4.0, 20.0),
    "anthropic/claude-sonnet-5": (2.0, 10.0),
    "anthropic/claude-haiku-4.5": (1.0, 5.0),
    "anthropic/claude-sonnet-4.6": (3.0, 15.0),
}

KB_DIR = ROOT / "knowledge_base"
DATA_DIR = ROOT / "data"
CACHE_DIR = ROOT / ".cache"
POLICY_PATH = ROOT / "review_policy.md"

TODAY = _dt.date.today().isoformat()


def get_client():
    """Anthropic SDK client pointed at OpenRouter."""
    import anthropic

    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Add it to your .env file (see .env.example).")
    return anthropic.Anthropic(
        base_url=OPENROUTER_BASE_URL,
        auth_token=OPENROUTER_API_KEY,        # sent as "Authorization: Bearer ...", which OpenRouter expects
        api_key=None,
        max_retries=3,
        default_headers={"X-Title": "Claude SDK multi-agent workshop"},
    )


def status() -> str:
    lines = [
        f"OpenRouter key : {'set' if OPENROUTER_API_KEY else 'MISSING'}",
        f"Tavily key     : {'set' if TAVILY_API_KEY else 'missing -> web_search uses the offline cache'}",
        f"Orchestrator   : {ORCHESTRATOR_MODEL}",
        f"Specialists    : {SPECIALIST_MODEL}",
        f"Embeddings     : {EMBED_MODEL}",
        f"Today          : {TODAY}",
    ]
    return "\n".join(lines)
