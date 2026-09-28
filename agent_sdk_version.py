"""The same orchestrator + 2 specialists, built with the Claude Agent SDK.

Run from the notebook (section 9) or a terminal:
    python agent_sdk_version.py "Your question here"

What the SDK does for you, compared with the hand-written loop in the notebook:
  * The agent loop: calling tools, feeding results back, checking stop_reason. The SDK runs it.
  * Subagents: `AgentDefinition`. The orchestrator delegates through the built-in `Agent` tool,
    and each subagent gets a fresh context. Only its final message returns to the parent.
  * Custom tools: `@tool` functions, served in-process by `create_sdk_mcp_server`.
    Claude sees them as  mcp__<server>__<tool>.
  * Guardrails in code: a PreToolUse *hook* enforces which agent may call which tool.
    That is deterministic, not a request in the prompt.

Why a separate script rather than a notebook cell? The Agent SDK drives the Claude Code CLI as a
subprocess, and Jupyter's event loop on Windows cannot start asyncio subprocesses. A plain
`python` process works everywhere. On Windows, install the Claude Code CLI first
(https://code.claude.com/docs); on macOS and Linux the SDK wheel bundles it.
"""
from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import asdict

from claude_agent_sdk import (AgentDefinition, AssistantMessage, ClaudeAgentOptions, HookMatcher, ResultMessage,
                              TextBlock, ToolUseBlock, create_sdk_mcp_server, query, tool)

from workshop_lib import config
from workshop_lib.rag import KnowledgeBase
from workshop_lib.tools_impl import (ClaimLedger, SearchSession, check_source_policy, compare_figures,
                                     normalise_figure, record_claim, score_source, web_search)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # Windows pipes default to cp1252 (emoji crash)
LEDGER, SESSION = ClaimLedger(), SearchSession()
KB = KnowledgeBase(verbose=False)


def _ok(payload: dict) -> dict:
    """MCP tool result format. Structured errors are flagged with is_error so Claude can react to them."""
    return {"content": [{"type": "text", "text": json.dumps(payload, default=str)}],
            "is_error": bool(payload.get("isError"))}


# ------------------------------------------------------------------ research tools (web-researcher only)
@tool("web_search",
      "Search the public web (Tavily) for current facts about AI organisations. Returns results with title, url, "
      "content, published_date and source_tier (1 = primary, 2 = news, 3 = other). Use one focused query per fact. "
      "Does NOT verify anything. mode='cache' means the results come from an offline snapshot.",
      {"type": "object", "properties": {"query": {"type": "string"},
                                        "max_results": {"type": "integer", "minimum": 1, "maximum": 8}},
       "required": ["query"]})
async def t_web_search(args):
    return _ok(web_search(SESSION, args["query"], args.get("max_results", 5)))


@tool("score_source", "Credibility tier of a URL (1 primary, 2 news, 3 other). Judges the domain only.", {"url": str})
async def t_score_source(args):
    return _ok(score_source(args["url"]))


@tool("normalise_figure", "Convert '€21bn', '$965 billion', '1.6T' or '10M tokens' into a number plus currency or unit. "
      "Does not convert between currencies.", {"value": str})
async def t_normalise(args):
    return _ok(normalise_figure(args["value"]))


@tool("record_claim",
      "Save ONE atomic claim with its source to the claim ledger. This is the ONLY way findings reach the rest of the "
      "system. source_url must come from web_search in this run. quote must be copied exactly from that result, "
      "because it is checked in code. Set hedged=true for 'reported' or 'estimated' figures. Returns claim_id and quote_verified.",
      {"type": "object",
       "properties": {"entity": {"type": "string"}, "attribute": {"type": "string"}, "value": {"type": "string"},
                      "source_url": {"type": "string"}, "quote": {"type": "string"}, "hedged": {"type": "boolean"}},
       "required": ["entity", "attribute", "value", "source_url", "quote"]})
async def t_record_claim(args):
    return _ok(record_claim(LEDGER, SESSION, **args))


# ------------------------------------------------------------------ review tools (policy-reviewer only)
@tool("get_claims", "Fetch the full ledger records (value, source, quote, tier, date) for the given claim IDs. "
      "Claims are passed between agents BY REFERENCE, so this is how you get them.",
      {"type": "object", "properties": {"claim_ids": {"type": "array", "items": {"type": "string"}}},
       "required": ["claim_ids"]})
async def t_get_claims(args):
    return _ok({"claims": [asdict(LEDGER.claims[c]) for c in args["claim_ids"] if c in LEDGER.claims],
                "unknown": [c for c in args["claim_ids"] if c not in LEDGER.claims]})


@tool("search_knowledge_base",
      "Semantic search of the INTERNAL knowledge base (9 AI-organisation profiles, the reference ground truth). "
      "Returns chunks with chunk_id, doc_id, section, kb_version, last_verified and text. Optional doc_id: one of "
      "openai, anthropic, mistral, deepseek, meta, llama, amazon, google, qwen. Does NOT search the web.",
      {"type": "object", "properties": {"query": {"type": "string"}, "doc_id": {"type": "string"},
                                        "k": {"type": "integer"}}, "required": ["query"]})
async def t_search_kb(args):
    return _ok({"results": KB.search(args["query"], args.get("k", 4), args.get("doc_id"))})


@tool("compare_figures", "Deterministic comparison with RP-4 bands (2% / 10%). Always use this instead of doing "
      "arithmetic yourself.", {"claim_value": str, "kb_value": str})
async def t_compare(args):
    return _ok(compare_figures(args["claim_value"], args["kb_value"]))


@tool("check_source_policy", "Apply policy rules RP-1 to RP-3 to one claim. If passes_hard_rules is false, the "
      "verdict is POLICY_VIOLATION.",
      {"type": "object", "properties": {"source_url": {"type": "string"}, "published_date": {"type": ["string", "null"]},
                                        "claim_type": {"type": "string", "enum": ["financial", "user_metric", "model_spec",
                                                                                  "corporate", "other"]},
                                        "quote_verified": {"type": "boolean"}, "hedged": {"type": "boolean"}},
       "required": ["source_url", "published_date", "claim_type", "quote_verified"]})
async def t_policy(args):
    return _ok(check_source_policy(**args))


research_server = create_sdk_mcp_server("research", tools=[t_web_search, t_score_source, t_normalise, t_record_claim])
kb_server = create_sdk_mcp_server("kb", tools=[t_get_claims, t_search_kb, t_compare, t_policy])
R = [f"mcp__research__{n}" for n in ("web_search", "score_source", "normalise_figure", "record_claim")]
K = [f"mcp__kb__{n}" for n in ("get_claims", "search_knowledge_base", "compare_figures", "check_source_policy")]

# ------------------------------------------------------------------ hooks: guardrails enforced in code
TOOL_OWNER = {**{t: "web-researcher" for t in R}, **{t: "policy-reviewer" for t in K}}


async def guard(input_data, tool_use_id, context):
    tool_name = input_data["tool_name"]
    agent = input_data.get("agent_type")          # absent on the main thread, i.e. the orchestrator
    if tool_name in ("Agent", "Task"):
        # Make every delegation synchronous: the orchestrator needs each result before its next step.
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",
                                       "updatedInput": {**input_data["tool_input"], "run_in_background": False}}}
    owner = TOOL_OWNER.get(tool_name)
    if owner and agent != owner:
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": f"{tool_name} belongs to {owner}; "
                                                                   f"{agent or 'orchestrator'} must delegate instead."}}
    return {}


REVIEW_POLICY = config.POLICY_PATH.read_text(encoding="utf-8")

AGENTS = {
    "web-researcher": AgentDefinition(
        description="Web research specialist. Use it to find current, sourced facts about AI organisations. "
                    "Give it a self-contained brief listing the facts needed.",
        prompt=f"You are the web-researcher. Today is {config.TODAY}. For each fact: web_search with a focused query, "
               "prefer tier-1 and tier-2 sources, then record_claim with an exact quote (fix it if quote_verified is "
               "false). At most 8 searches. Finish with ONLY a JSON object: "
               '{"claim_ids": [...], "gaps": [...], "notes": "..."}',
        tools=R, model=config.SPECIALIST_MODEL, maxTurns=16),
    "policy-reviewer": AgentDefinition(
        description="Claim reviewer. Use it to verify claim IDs against the internal knowledge base and the "
                    "review policy. Pass it the claim IDs only.",
        prompt=f"You are the policy-reviewer. Today is {config.TODAY}. Call get_claims first. For EACH claim, call "
               "check_source_policy, then search_knowledge_base, then compare_figures when the claim is numeric. "
               "If a claim is CONTRADICTED and its source_tier is 1 or 2, set kb_possibly_wrong to true (RP-5). "
               "Finish with ONLY a JSON array of {claim_id, verdict, kb_value, kb_chunk_id, kb_possibly_wrong, "
               f"explanation}}.\n<review_policy>\n{REVIEW_POLICY}\n</review_policy>",
        tools=K, model=config.SPECIALIST_MODEL, maxTurns=30),
}

ORCHESTRATOR_PROMPT = f"""You are the orchestrator of a fact-checking team. Today is {config.TODAY}.
You cannot search or read the knowledge base yourself: delegate with the Agent tool.
1. Delegate to web-researcher with a self-contained brief listing every fact needed.
2. Delegate to policy-reviewer with ALL the claim IDs the researcher returned (IDs only).
3. Write the briefing: bullet points citing claim IDs, then a Discrepancies table
   (claim | web value | KB value | likely correct | why). Never resolve a CONTRADICTED claim silently.
   A tier-1 or tier-2 source that contradicts the KB usually wins; a lone tier-3 source usually does not.
   Base every judgement ONLY on the subagents' results, and never cite a source or figure you were not shown."""


async def main(question: str):
    options = ClaudeAgentOptions(
        model=config.ORCHESTRATOR_MODEL,
        system_prompt=ORCHESTRATOR_PROMPT,
        tools=["Agent"],                         # built-in tools: only the delegation tool
        mcp_servers={"research": research_server, "kb": kb_server},
        allowed_tools=["Agent", *R, *K],         # auto-approve these (no permission prompts)
        agents=AGENTS,
        hooks={"PreToolUse": [HookMatcher(matcher="Agent|Task|mcp__.*", hooks=[guard])]},
        setting_sources=[],                      # ignore local CLAUDE.md or settings, for reproducibility
        max_turns=12,
        max_budget_usd=1.00,                     # hard spend cap for the whole tree of agents
        env={
            "ANTHROPIC_BASE_URL": config.OPENROUTER_BASE_URL,
            "ANTHROPIC_AUTH_TOKEN": config.OPENROUTER_API_KEY,
            "ANTHROPIC_API_KEY": "",             # must be explicitly empty when routing via OpenRouter
            "ANTHROPIC_DEFAULT_SONNET_MODEL": config.ORCHESTRATOR_MODEL,
            "ANTHROPIC_DEFAULT_OPUS_MODEL": config.ORCHESTRATOR_MODEL,
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": config.SPECIALIST_MODEL,
            "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",   # specialists cannot spawn their own subagents
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        },
    )
    async for msg in query(prompt=question, options=options):
        who = "  [subagent]" if getattr(msg, "parent_tool_use_id", None) else "[orchestrator]"
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, ToolUseBlock):
                    arg = b.input.get("subagent_type") or json.dumps(b.input)[:110]
                    print(f"{who} 🔧 {b.name}: {arg}")
                elif isinstance(b, TextBlock) and b.text.strip() and who != "[orchestrator]":
                    print(f"{who} 💬 {b.text.strip()[:140]}")
        elif isinstance(msg, ResultMessage):
            print("\n" + "=" * 90 + f"\n{msg.result}\n" + "=" * 90)
            cost = f"${msg.total_cost_usd:.4f}" if msg.total_cost_usd is not None else "n/a"
            print(f"turns={msg.num_turns}  cost≈{cost} (as estimated by the SDK)  subtype={msg.subtype}")
    print("\nClaim ledger (lineage, filled in by the tools, not by the model):")
    for c in LEDGER.claims.values():
        print(f"  {c.claim_id} {c.entity:<12} {c.attribute:<26} {c.value:<18} tier={c.source_tier} "
              f"quote_ok={c.quote_verified}  {c.source_url}")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or ("What is Anthropic's latest post-money valuation, and what did Mistral AI raise "
                                   "in its Series C and at what valuation?")
    asyncio.run(main(q))
