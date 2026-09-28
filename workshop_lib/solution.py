"""Reference implementation of the workshop's multi-agent system (Anthropic Messages API).

The SOLUTION notebook is generated from this file (each `# %% cell:` block becomes one cell),
so the notebook and this module never drift apart. Learners who get stuck on a gap in the
STUDENT notebook can import the finished piece from here instead.
"""
# %% cell: imports
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from urllib.parse import urlparse

from workshop_lib import config
from workshop_lib.rag import KnowledgeBase
from workshop_lib.tools_impl import (ClaimLedger, SearchSession, check_source_policy, compare_figures,
                                     normalise_figure, record_claim, score_source, tool_error, web_search)
from workshop_lib.tracing import Tracer, approx_tokens


@dataclass
class RunContext:
    """Everything one run shares. Specialists never share a context *window*: shared state lives here, in code."""
    client: object
    kb: KnowledgeBase
    tracer: Tracer
    ledger: ClaimLedger = field(default_factory=ClaimLedger)
    transcripts: dict = field(default_factory=lambda: {"web-researcher": [], "policy-reviewer": []})
    handoffs: list = field(default_factory=list)       # what was actually passed between agents


# %% cell: researcher_tools
# ---------------------------------------------------------------------------------------------
# WEB-RESEARCHER tools: 1 main tool (web_search) + 4 small programmatic helpers.
# Each description says what the tool does, when to use it, what it returns and what it does NOT do.
# ---------------------------------------------------------------------------------------------
RESEARCHER_TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Search the public web (Tavily) for current facts about AI organisations. Returns up to "
            "`max_results` results, each with title, url, content (a text snippet), published_date and "
            "source_tier (1 = primary source, 2 = established news outlet, 3 = other). "
            "Use one focused query per fact, naming the organisation and the fact "
            "(e.g. 'Anthropic Series H post-money valuation'), rather than one broad query. "
            "This tool does NOT verify anything: results can be wrong, stale or contradict each other. "
            "If the response has mode='cache', the results come from an offline snapshot."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Focused search query naming the organisation and the fact."},
                "max_results": {"type": "integer", "minimum": 1, "maximum": 8, "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "score_source",
        "description": (
            "Return the credibility tier of a URL: 1 = primary source (the organisation's own site, filings, "
            "press releases), 2 = established news outlet, 3 = wiki, blog or aggregator. Use it to choose "
            "between conflicting results: prefer tier 1, then tier 2. It judges the domain only, not the content."
        ),
        "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    },
    {
        "name": "normalise_figure",
        "description": (
            "Convert a figure written as text ('€21bn', '$965 billion', '1.6T', '10M tokens') into a number "
            "plus currency or unit. Use it when two results state the same figure in different formats and "
            "you need to know whether they agree. It does NOT convert between currencies."
        ),
        "input_schema": {"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
    },
    {
        "name": "record_claim",
        "description": (
            "Save ONE atomic factual claim, with its source, to the claim ledger. This is the ONLY way your "
            "findings reach the rest of the system: anything you do not record is lost. Requirements: "
            "(1) source_url must be a URL returned by web_search in this task; "
            "(2) quote must be an exact fragment copied from that result's content, because it is checked "
            "programmatically; (3) one fact per claim, so split 'raised $65bn at a $965bn valuation' into two "
            "claims. Set hedged=true if the source says 'reported', 'estimated' or similar. "
            "Returns claim_id and quote_verified. If quote_verified is false, record the claim again with an exact quote."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity": {"type": "string", "description": "Organisation or model family, e.g. 'Anthropic', 'Llama'."},
                "attribute": {"type": "string", "description": "snake_case fact name, e.g. post_money_valuation, "
                              "latest_round_amount, training_cost, context_window, monthly_active_users."},
                "value": {"type": "string", "description": "The figure as written, with currency and unit, e.g. '€1.7 billion'."},
                "source_url": {"type": "string"},
                "quote": {"type": "string", "description": "Exact text copied from the search result that states the fact."},
                "hedged": {"type": "boolean", "default": False},
            },
            "required": ["entity", "attribute", "value", "source_url", "quote"],
        },
    },
    {
        "name": "submit_research",
        "description": (
            "Finish your task. Call this exactly once, after every requested fact either has a recorded claim "
            "or you have established that it cannot be found. List the claim IDs you recorded and describe any "
            "gaps. Do not call any other tool afterwards."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "claim_ids": {"type": "array", "items": {"type": "string"}},
                "gaps": {"type": "array", "items": {"type": "string"},
                         "description": "Facts you could not find, and why."},
                "notes": {"type": "string", "description": "Conflicts between sources worth flagging (optional)."},
            },
            "required": ["claim_ids", "gaps"],
        },
    },
]


# %% cell: reviewer_tools
# ---------------------------------------------------------------------------------------------
# POLICY-REVIEWER tools: 1 main tool (RAG over the KB) + 4 small programmatic helpers.
# ---------------------------------------------------------------------------------------------
KB_DOC_IDS = ["openai", "anthropic", "mistral", "deepseek", "meta", "llama", "amazon", "google", "qwen"]

REVIEWER_TOOLS = [
    {
        "name": "search_knowledge_base",
        # >>> GAP 1 (student notebook): write this description <<<
        "description": (
            "Semantic search (FAISS over mistral-embed vectors) of the INTERNAL knowledge base: curated "
            "profiles of 9 AI organisations. This is the reference ground truth for checking claims. Returns "
            "the top-k chunks, each with chunk_id, doc_id, section, kb_version, last_verified and text. "
            "Query with the organisation and the fact in plain language (e.g. 'Mistral Series C valuation'). "
            "Set doc_id to restrict the search to one organisation. Each document's 'Key figures at a glance' "
            "section holds its headline numbers. This tool does NOT search the web, and a missing answer "
            "means the fact is not in the KB, not that it is false."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "doc_id": {"type": "string", "enum": KB_DOC_IDS, "description": "Optional: restrict to one organisation."},
                "k": {"type": "integer", "minimum": 1, "maximum": 8, "default": 4},
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_kb_documents",
        "description": (
            "List the knowledge-base documents with their doc_id, kb_version, last_verified date and section "
            "names. Use it to pick a doc_id, or to check how current the KB is before deciding whether a newer "
            "web source might be right (policy RP-3 and RP-5)."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "compare_figures",
        "description": (
            "Deterministically compare a claimed figure with the knowledge-base figure, using the policy's "
            "RP-4 tolerance bands. ALWAYS use this instead of doing the arithmetic yourself. Pass both figures "
            "as written, including currency and multiplier (e.g. '$865 billion', '€17.1bn'). Returns band "
            "(SUPPORTED if 2% or less, MINOR_DIFFERENCE if 10% or less, CONTRADICTED if more than 10%, or "
            "UNIT_MISMATCH) and pct_difference."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"claim_value": {"type": "string"}, "kb_value": {"type": "string"}},
            "required": ["claim_value", "kb_value"],
        },
    },
    {
        "name": "check_source_policy",
        "description": (
            "Apply the machine-checkable policy rules (RP-1 provenance, RP-2 source tier, RP-3 recency) to ONE "
            "claim. Call it once per claim, before deciding the verdict. Returns passes_hard_rules, violations "
            "and flags. If passes_hard_rules is false, the verdict must be POLICY_VIOLATION."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "source_url": {"type": "string"},
                "published_date": {"type": ["string", "null"]},
                "claim_type": {"type": "string", "enum": ["financial", "user_metric", "model_spec", "corporate", "other"]},
                "quote_verified": {"type": "boolean"},
                "hedged": {"type": "boolean"},
            },
            "required": ["source_url", "published_date", "claim_type", "quote_verified"],
        },
    },
    {
        "name": "submit_review",
        "description": (
            "Finish the review. Call this exactly once, with one verdict for EVERY claim_id you were given. "
            "The submission is validated: missing claim IDs or invalid verdicts are rejected, and you must resubmit."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "verdicts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "claim_id": {"type": "string"},
                            "verdict": {"type": "string", "enum": ["SUPPORTED", "MINOR_DIFFERENCE", "CONTRADICTED",
                                                                    "UNVERIFIED", "POLICY_VIOLATION"]},
                            "kb_value": {"type": ["string", "null"], "description": "Value the KB states, if any."},
                            "kb_chunk_id": {"type": ["string", "null"]},
                            "kb_possibly_wrong": {"type": "boolean"},
                            "policy_flags": {"type": "array", "items": {"type": "string"}},
                            "explanation": {"type": "string", "description": "Two sentences or fewer."},
                        },
                        "required": ["claim_id", "verdict", "kb_value", "kb_chunk_id", "kb_possibly_wrong", "explanation"],
                    },
                },
                "summary": {"type": "string"},
            },
            "required": ["verdicts", "summary"],
        },
    },
]


# %% cell: orchestrator_tools
# ---------------------------------------------------------------------------------------------
# ORCHESTRATOR tools: it only delegates. It cannot search or read the KB itself.
# ---------------------------------------------------------------------------------------------
ORCHESTRATOR_TOOLS = [
    {
        "name": "delegate_research",
        "description": (
            "Send a research brief to the web-researcher specialist, which searches the public web and records "
            "sourced claims. The specialist starts with NO knowledge of this conversation, so the brief must "
            "contain everything it needs. Returns a compact list of claims (claim_id, entity, attribute, value, "
            "source domain, tier) plus any gaps. Use this first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "brief": {"type": "string", "description": "What to find and why, in 1-3 sentences."},
                "entities": {"type": "array", "items": {"type": "string"}},
                "facts_needed": {"type": "array", "items": {"type": "string"},
                                 "description": "One line per fact, e.g. 'Anthropic: latest post-money valuation'."},
            },
            "required": ["brief", "entities", "facts_needed"],
        },
    },
    {
        "name": "delegate_review",
        "description": (
            "Send claims to the policy-reviewer specialist, which checks them against the internal knowledge "
            "base and the review policy. Pass claim IDs only: the system attaches the full claim records "
            "(value, source, quote) directly from the ledger, so you never retype figures. Returns one verdict per claim."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "claim_ids": {"type": "array", "items": {"type": "string"}},
                "focus": {"type": "string", "description": "Optional note on what matters most."},
            },
            "required": ["claim_ids"],
        },
    },
]


# %% cell: prompts
RESEARCHER_SYSTEM = f"""You are the web-researcher specialist in a multi-agent fact-checking system. Today is {config.TODAY}.

<role>
Find current, sourced facts for the brief you are given and record each one as an atomic claim.
You do not verify claims against internal data (another specialist does that), and you never contact other agents.
</role>

<process>
1. For each fact needed, run a focused web_search.
2. Prefer tier-1 sources, then tier-2. When results conflict, prefer the most recent reliable source and mention the conflict in `notes`.
3. Call record_claim for each fact, using an exact quote from the result. If quote_verified is false, fix the quote and record the claim again.
4. Call submit_research once, then stop.
</process>

<rules>
- One fact per claim. Never record a figure that is not in a retrieved result.
- Keep the source's hedging ("reported", "estimated") by setting hedged=true.
- Budget: at most 8 web searches.
</rules>"""

REVIEWER_SYSTEM = f"""You are the policy-reviewer specialist in a multi-agent fact-checking system. Today is {config.TODAY}.

<role>
Judge each claim you are given against the internal knowledge base (KB) and the review policy below.
You only see the claims in this message. You do not search the web and you never contact other agents.
</role>

<process>
For EACH claim:
1. check_source_policy. If passes_hard_rules is false, the verdict is POLICY_VIOLATION.
2. search_knowledge_base for the same fact (use doc_id to stay within the right organisation).
3. If the claim is numeric and the KB states a value, call compare_figures, and use its band as the verdict.
4. If the KB says nothing about the fact, the verdict is UNVERIFIED.
5. If the verdict is CONTRADICTED and the claim's source_tier is 1 or 2, set kb_possibly_wrong = true (RP-5).
Then call submit_review once with a verdict for every claim.
</process>

<review_policy>
{config.POLICY_PATH.read_text(encoding="utf-8")}
</review_policy>"""

ORCHESTRATOR_SYSTEM = f"""You are the orchestrator of a small fact-checking team. Today is {config.TODAY}.

<team>
You have two specialists, reachable ONLY through your tools:
- web-researcher (delegate_research): searches the web and records sourced claims.
- policy-reviewer (delegate_review): checks claims against the internal knowledge base and the review policy.
They cannot see this conversation or each other, and each call starts fresh. You are the only channel between them.
</team>

<workflow>
1. Break the user's question into specific, checkable facts.
2. Call delegate_research with a self-contained brief.
3. Call delegate_review with ALL the returned claim_ids.
4. Write the final briefing. If a specialist reports errors or gaps, you may re-delegate ONCE with a narrower brief; otherwise report the gap.
</workflow>

<interpreting_verdicts>
- SUPPORTED: state the fact.
- MINOR_DIFFERENCE: state it and note the difference.
- CONTRADICTED: never pick a winner silently. Show the web value and the KB value, with their sources and dates, then judge which is more credible. The KB is a curated secondary summary: a tier-1 or tier-2 source that contradicts it usually wins, while a lone tier-3 source usually does not. Base that judgement ONLY on evidence in your tool results, and never cite a source or figure you were not shown. When the reviewer set kb_possibly_wrong, recommend a KB correction for human sign-off.
- UNVERIFIED: present the fact as unverified web information.
- POLICY_VIOLATION: exclude the claim and say why.
</interpreting_verdicts>

<output_format>
## Briefing
Bullet points. Cite claim IDs for every fact, e.g. [C-003].
## Discrepancies
A markdown table with the columns: claim | web value (source) | KB value (chunk) | likely correct | why
## Gaps and caveats
</output_format>"""


# %% cell: run_agent
def _to_param(block) -> dict:
    """Convert a response content block back into a request param (only the fields the API needs)."""
    if block.type == "text":
        return {"type": "text", "text": block.text}
    if block.type == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    return block.model_dump(exclude_none=True)


def run_agent(ctx: RunContext, name: str, system: str, tools: list[dict], handlers: dict, user_content: str,
              model: str, max_turns: int = 10, depth: int = 0, terminal_tool: str | None = None,
              tool_choice: dict | None = None) -> dict:
    """The agentic loop. The loop is driven by `stop_reason`, not by parsing the model's text.

    - stop_reason == "tool_use": run every requested tool, send ALL results back in one user turn, loop.
    - stop_reason == "end_turn": the model is done, so return its text.
    - calling `terminal_tool` successfully also ends the loop (a structured "I'm done" signal).
    - max_turns is a hard safety limit, so a confused agent cannot loop forever.
    """
    messages = [{"role": "user", "content": user_content}]
    for turn in range(1, max_turns + 1):
        response = ctx.client.messages.create(model=model, max_tokens=4096, system=system, tools=tools,
                                              messages=messages, **({"tool_choice": tool_choice} if tool_choice else {}))
        ctx.tracer.turn(name, depth, turn, response)
        messages.append({"role": "assistant", "content": [_to_param(b) for b in response.content]})

        if response.stop_reason == "tool_use":
            tool_results, terminal_input = [], None
            for block in response.content:
                if block.type != "tool_use":
                    continue
                ctx.tracer.tool_call(name, depth, block.name, block.input)
                handler = handlers.get(block.name)
                try:
                    result = handler(**block.input) if handler else tool_error(
                        "validation", f"unknown tool {block.name!r}")
                except TypeError as e:          # the model sent bad arguments: tell it so it can fix them
                    result = tool_error("validation", f"bad arguments: {e}", retryable=True)
                except Exception as e:          # a bug or outage in our code: report it, don't crash the loop
                    result = tool_error("internal", f"{type(e).__name__}: {e}", retryable=False)
                is_error = isinstance(result, dict) and bool(result.get("isError"))
                ctx.tracer.tool_result(name, depth, block.name, result, is_error)
                if block.name == terminal_tool and not is_error:
                    terminal_input = block.input
                tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                     "content": json.dumps(result, default=str), "is_error": is_error})
            messages.append({"role": "user", "content": tool_results})
            if terminal_input is not None:
                return {"final_text": None, "terminal_input": terminal_input, "messages": messages,
                        "turns": turn, "stopped_reason": "terminal_tool"}
            continue

        text = "".join(b.text for b in response.content if b.type == "text")
        if response.stop_reason == "end_turn":
            return {"final_text": text, "terminal_input": None, "messages": messages, "turns": turn,
                    "stopped_reason": "end_turn"}
        # max_tokens, refusal, pause_turn, ...: surface it and stop rather than guessing
        ctx.tracer.note(name, depth, f"stopped with stop_reason={response.stop_reason}")
        return {"final_text": text, "terminal_input": None, "messages": messages, "turns": turn,
                "stopped_reason": response.stop_reason}

    ctx.tracer.note(name, depth, f"hit max_turns={max_turns}")
    return {"final_text": None, "terminal_input": None, "messages": messages, "turns": max_turns,
            "stopped_reason": "max_turns"}


# %% cell: build_review_payload
REVIEW_FIELDS = ["claim_id", "entity", "attribute", "value", "source_url", "source_title", "source_tier",
                 "published_date", "quote", "quote_verified", "hedged"]


def build_review_payload(ledger: ClaimLedger, claim_ids: list[str]) -> tuple[list[dict], list[str]]:
    """Pass the reviewer ONLY what it needs to judge each claim. Not the researcher's transcript,
    not the raw search results, not the orchestrator's conversation.
    Returns (payload, unknown_ids)."""
    payload, unknown = [], []
    for cid in claim_ids:
        claim = ledger.claims.get(cid)
        if claim is None:
            unknown.append(cid)
            continue
        record = asdict(claim)
        payload.append({k: record[k] for k in REVIEW_FIELDS})
    return payload, unknown


# %% cell: specialists
def delegate_research(ctx: RunContext, brief: str, entities: list[str], facts_needed: list[str]) -> dict:
    """Run the web-researcher in a FRESH context. It sees only the brief, never the orchestrator's history."""
    session = SearchSession()
    first_new = len(ctx.ledger.claims)

    def _submit(claim_ids, gaps, notes=""):
        unknown = [c for c in claim_ids if c not in ctx.ledger.claims]
        if unknown:
            return tool_error("validation", f"unknown claim ids {unknown}; use the ids record_claim returned", True)
        return {"accepted": len(claim_ids)}

    handlers = {
        "web_search": lambda query, max_results=5: web_search(session, query, max_results),
        "score_source": lambda url: score_source(url),
        "normalise_figure": lambda value: normalise_figure(value),
        "record_claim": lambda **kw: record_claim(ctx.ledger, session, **kw),
        "submit_research": _submit,
    }
    user = (f"<brief>{brief}</brief>\n<entities>{', '.join(entities)}</entities>\n<facts_needed>\n"
            + "\n".join(f"- {f}" for f in facts_needed) + "\n</facts_needed>")
    ctx.handoffs.append({"from": "orchestrator", "to": "web-researcher", "tokens": approx_tokens(user)})
    res = run_agent(ctx, "web-researcher", RESEARCHER_SYSTEM, RESEARCHER_TOOLS, handlers, user,
                    config.SPECIALIST_MODEL, max_turns=16, depth=1, terminal_tool="submit_research")
    ctx.transcripts["web-researcher"].append(res["messages"])

    sub = res["terminal_input"]
    if sub is None:   # graceful degradation: keep partial work, say clearly that it is partial
        ids = list(ctx.ledger.claims)[first_new:]
        sub = {"claim_ids": ids, "gaps": [f"researcher stopped early ({res['stopped_reason']}); results partial"]}
    claims = []
    for cid in sub["claim_ids"]:
        c = ctx.ledger.claims[cid]
        claims.append({"claim_id": cid, "entity": c.entity, "attribute": c.attribute, "value": c.value,
                       "source": urlparse(c.source_url).netloc.removeprefix("www."), "tier": c.source_tier,
                       "quote_verified": c.quote_verified})
    out = {"status": "complete" if res["stopped_reason"] == "terminal_tool" else "partial",
           "claims": claims, "gaps": sub.get("gaps", []), "notes": sub.get("notes", ""),
           "search_modes": sorted({l["mode"] for l in session.log})}
    ctx.handoffs.append({"from": "web-researcher", "to": "orchestrator", "tokens": approx_tokens(out)})
    return out


def delegate_review(ctx: RunContext, claim_ids: list[str], focus: str = "") -> dict:
    """Run the policy-reviewer in a FRESH context with a structured payload built from the ledger."""
    payload, unknown = build_review_payload(ctx.ledger, claim_ids)
    if not payload:
        return tool_error("validation", f"no known claim ids in {claim_ids}")
    expected = {p["claim_id"] for p in payload}

    def _submit(verdicts, summary):
        got = {v.get("claim_id") for v in verdicts}
        missing = sorted(expected - got)
        if missing:   # validation + retry: the model gets the error and resubmits
            return tool_error("validation", f"missing verdicts for {missing}; resubmit with all claims", True)
        for v in verdicts:
            ctx.ledger.verdicts[v["claim_id"]] = v
        return {"accepted": len(verdicts)}

    handlers = {
        "search_knowledge_base": lambda query, doc_id=None, k=4: {"results": ctx.kb.search(query, k, doc_id)},
        "list_kb_documents": lambda: {"documents": ctx.kb.documents()},
        "compare_figures": lambda claim_value, kb_value: compare_figures(claim_value, kb_value),
        "check_source_policy": lambda **kw: check_source_policy(**kw),
        "submit_review": _submit,
    }
    user = f"<claims>\n{json.dumps(payload, indent=1)}\n</claims>" + (f"\n<focus>{focus}</focus>" if focus else "")
    ctx.handoffs.append({"from": "orchestrator", "to": "policy-reviewer", "tokens": approx_tokens(user)})
    res = run_agent(ctx, "policy-reviewer", REVIEWER_SYSTEM, REVIEWER_TOOLS, handlers, user,
                    config.SPECIALIST_MODEL, max_turns=30, depth=1, terminal_tool="submit_review")
    ctx.transcripts["policy-reviewer"].append(res["messages"])
    if res["terminal_input"] is None:
        return tool_error("incomplete", f"reviewer stopped early ({res['stopped_reason']}); no verdicts", True)
    out = {"verdicts": [{k: v.get(k) for k in ("claim_id", "verdict", "kb_value", "kb_chunk_id",
                                                "kb_possibly_wrong", "explanation")}
                        for v in res["terminal_input"]["verdicts"]],
           "summary": res["terminal_input"]["summary"], "unknown_claim_ids": unknown}
    ctx.handoffs.append({"from": "policy-reviewer", "to": "orchestrator", "tokens": approx_tokens(out)})
    return out


# %% cell: orchestrator
def run_orchestrator(ctx: RunContext, question: str, max_turns: int = 8) -> dict:
    handlers = {
        "delegate_research": lambda **kw: delegate_research(ctx, **kw),
        "delegate_review": lambda **kw: delegate_review(ctx, **kw),
    }
    # One delegation at a time: the review depends on the research result, so no parallel tool calls here.
    return run_agent(ctx, "orchestrator", ORCHESTRATOR_SYSTEM, ORCHESTRATOR_TOOLS, handlers, question,
                     config.ORCHESTRATOR_MODEL, max_turns=max_turns, depth=0,
                     tool_choice={"type": "auto", "disable_parallel_tool_use": True})
