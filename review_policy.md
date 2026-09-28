# Review Policy — Claim Verification (v1.2)

This policy tells the **policy-reviewer** agent how to judge claims that the web-researcher collected.
The knowledge base (KB) in `knowledge_base/` is the reference ground truth. The rules below are applied
partly by the model and partly by deterministic tools (`check_source_policy`, `compare_figures`).
Rules that *can* be checked in code *are* checked in code.

## Verdicts (use exactly one per claim)

| Verdict | Meaning |
|---|---|
| `SUPPORTED` | The KB states the same fact (numbers within the RP-4 tolerance). |
| `MINOR_DIFFERENCE` | Same fact, small numeric gap (RP-4), rounding, or a different "as of" date. |
| `CONTRADICTED` | The KB states a materially different value for the same fact. |
| `UNVERIFIED` | The KB has nothing on this fact. Not the same as false. |
| `POLICY_VIOLATION` | The claim fails a hard rule (RP-1) and must not be used, whatever the KB says. |

## Rules

**RP-1 Provenance (hard rule).** Every claim must carry a source URL, a source title and a supporting
quote taken from the retrieved page. A claim whose quote could not be verified against the retrieved
text (`quote_verified = false`), or that has no URL, is a `POLICY_VIOLATION`.

**RP-2 Source tiers.**
- Tier 1: primary sources (the organisation's own site, investor relations, regulatory filings, official press releases).
- Tier 2: established news organisations (Reuters, Bloomberg, FT, CNBC, TechCrunch, The Verge, and similar).
- Tier 3: everything else (Wikipedia, blogs, aggregators, investment commentary, course sites).

A financial or user-metric claim supported *only* by a tier-3 source is flagged `needs_corroboration`.

**RP-3 Recency.** Funding, valuation, revenue and user-number claims older than **12 months** (relative to
today) are flagged `stale`. Compare the claim's publication date with the KB document's `last_verified`
date: when a source is newer than the KB, the KB may be out of date.

**RP-4 Numeric tolerance.** Use `compare_figures`, never mental arithmetic.
- Difference of 2% or less: `SUPPORTED`
- More than 2% and up to 10%: `MINOR_DIFFERENCE`
- More than 10%: `CONTRADICTED`
- Different currencies or units: report `UNIT_MISMATCH` in the explanation and do not convert.

**RP-5 Do not silently correct.** The reviewer never overwrites or "fixes" a value. For every
`CONTRADICTED` claim, report both values, the KB chunk id and the source URL. The KB is a curated
*secondary* summary: when a **tier-1 or tier-2 source** contradicts it, set `kb_possibly_wrong = true`
so a human can check the KB. A contradiction from a tier-3 source alone does not set this flag.

**RP-6 Hedged language.** If the source calls a figure "reported", "estimated" or "according to people
familiar", the claim must keep that hedge. Dropping it counts as a `MINOR_DIFFERENCE` at best.

**RP-7 Scope.** The reviewer checks the claims it is given. It does not search the web, add new claims
or talk to the researcher. If more evidence is needed, it says so in its summary and the orchestrator
decides.
