---
doc_id: llama
title: Llama — Knowledge Base Profile
kb_version: 2026.09
last_verified: 2026-09-28
---
# Llama

## Overview
Llama (originally "LLaMA", Large Language Model Meta AI) is the family of large language models developed and released by Meta Platforms, headquartered in Menlo Park, California. Llama models are distributed as downloadable weights under Meta's own community licences, which makes Llama "open-weight" or "source-available" rather than open source in the Open Source Initiative sense. From 2023 to 2025 Llama was the most widely downloaded open-weight model family, passing 1 billion downloads in March 2025. The latest generation is Llama 4 (April 2025); since April 2026 Meta's flagship models are the proprietary Muse series, and Llama is maintained rather than actively scaled. For Meta as a company (leadership, capex, Meta Superintelligence Labs) see the separate Meta profile.

## Origins and team behind the models
Llama originated in Meta's FAIR (Facebook AI Research) group, founded in 2013 under Yann LeCun. Llama 1 was announced on 24 February 2023 as a research release; its weights leaked online within about a week, which accelerated the open-weight ecosystem. Later Llama generations were built by Meta's generative AI organisation, with Meta CEO Mark Zuckerberg personally championing Llama in his July 2024 essay "Open Source AI is the Path Forward". After the lukewarm reception of Llama 4 in April 2025 and the delay of Llama 4 Behemoth, Meta created Meta Superintelligence Labs (MSL) on 30 June 2025 under Chief AI Officer Alexandr Wang; Llama work was absorbed into MSL. Yann LeCun left Meta in November 2025. MSL's first model, Muse Spark (8 April 2026), was built with new infrastructure, architecture and data pipelines rather than as a Llama successor.

## Ownership, licensing and investment
Llama is wholly owned by Meta Platforms and is funded from Meta's operating budget; it has no separate investors or valuation. Llama 1 weights were released under a non-commercial research licence on a case-by-case basis. From Llama 2 (18 July 2023) onward, models have been free for research and commercial use under a Llama Community Licence plus an Acceptable Use Policy. Key licence terms: companies whose products exceeded 700 million monthly active users must request a separate licence from Meta; derivatives must display "Built with Llama" and include "Llama" in model names; and the Llama 3.2 and Llama 4 licences restrict multimodal rights for entities domiciled in the EU. The Llama 3.1 licence (July 2024) first allowed Llama outputs to be used to improve other models. The Llama 4 Community Licence is dated 5 April 2025. The Open Source Initiative disputes that these licences are open source. Meta has also funded the ecosystem through Llama Impact Grants (over $1.5 million to ten recipients in the second round, April 2025). Muse Glimmer (August 2026), Meta's newest open-weight model, uses Apache 2.0 instead of a Llama licence.

## Model and product timeline
| Date | Release | Notes |
|---|---|---|
| 24 Feb 2023 | Llama 1 | 7B, 13B, 33B, 65B; 2,048-token context; 1.0–1.4T training tokens; research-only licence |
| 18 Jul 2023 | Llama 2 | 7B, 13B, 70B; 4,096-token context; 2T tokens; commercial use allowed; Microsoft preferred partner |
| 24 Aug 2023 | Code Llama | 7B, 13B, 34B (70B added Jan 2024); code-tuned Llama 2 |
| 18 Apr 2024 | Llama 3 | 8B, 70B; 8,192-token context; 15T+ tokens; 128K-token vocabulary; two 24K-GPU clusters |
| 23 Jul 2024 | Llama 3.1 | 8B, 70B, 405B; 128K context; 405B trained on 15T+ tokens with 16,000+ H100 GPUs; 8 languages |
| 25 Sep 2024 | Llama 3.2 | 1B, 3B text; 11B, 90B vision; 128K context; first multimodal Llama |
| Dec 2024 | Llama 3.3 | 70B text model; 128K context |
| 5 Apr 2025 | Llama 4 Scout | MoE: 17B active, 109B total, 16 experts; 1M-token context; fits one H100 (Int4) |
| 5 Apr 2025 | Llama 4 Maverick | MoE: 17B active, 400B total, 128 experts; 1M-token context |
| 5 Apr 2025 | Llama 4 Behemoth (preview) | 288B active, ~2T total, 16 experts; teacher model, never publicly released |
| 29 Apr 2025 | Llama API (preview) and Llama Guard 4 | Announced at first LlamaCon |
| 15 May 2025 | Behemoth delay reported | WSJ/Axios: pushed to autumn 2025 or later |
| 8 Apr 2026 | Muse Spark replaces Llama in Meta AI | Proprietary MSL model; Llama moves to maintenance |

## Products and distribution
Llama weights are distributed via llama.com (which now redirects to Meta's developer portal, dev.meta.ai) and Hugging Face, and through cloud partners including AWS, Microsoft Azure, Google Cloud, Databricks, Snowflake, IBM watsonx and NVIDIA NIM; Llama 3.1 launched on 25+ partner platforms. Meta reported 1 billion Llama downloads on 18 March 2025, and about 1.2 billion around LlamaCon (29 April 2025) as reported by press. The Llama API, launched in limited free preview at LlamaCon, offered one-click API keys, Python and TypeScript SDKs, OpenAI-SDK compatibility and fine-tuning of Llama 3.3 8B, with fast inference via Cerebras and Groq. Llama Stack distributions were built with NVIDIA, IBM, Red Hat and Dell. Llama powered the Meta AI assistant from September 2023 until Muse Spark replaced it in April 2026. Notable adopters cited by Meta include Spotify.

## Research, safety and openness
Llama models use a decoder-only transformer with SwiGLU activations, rotary positional embeddings (RoPE) and RMSNorm; Llama 4 introduced mixture-of-experts, native multimodality, FP8 training (390 TFLOPs per GPU on 32K GPUs), 30+ trillion pre-training tokens and data covering 200 languages. Llama 4 was controversial: Meta's LMArena ranking used an unreleased "experimental chat version", which LMArena said did not match its expectations of model providers. Meta's Llama safety tooling includes Llama Guard (versions 1–4), Prompt Guard 2, LlamaFirewall, CyberSecEval and the Llama Defenders Program. Llama's openness is contested: the OSI and others classify Llama as source-available owing to the MAU cap, use restrictions and EU multimodal limits. In December 2025 press reported Meta was shifting to closed models; in April 2026 Meta said existing Llama models remain available but would receive only incremental updates and maintenance. No Llama 5 has been officially announced by Meta as of September 2026; web pages claiming a Llama 5 release are unverified. Meta's open-weight line has instead continued with Muse Glimmer (30B, Apache 2.0, 10 August 2026).

## Key figures at a glance
| Metric | Value | As of |
|---|---|---|
| First release | Llama 1, 24 February 2023 | — |
| Developer | Meta Platforms (Menlo Park, California) | 2026 |
| Latest generation | Llama 4 (Scout, Maverick) | Apr 2025 |
| Largest released model | Llama 4 Maverick, 400B total / 17B active | Apr 2025 |
| Largest dense model | Llama 3.1 405B | Jul 2024 |
| Longest context window | 1 million tokens (Llama 4 Scout) | Apr 2025 |
| Llama 4 training data | 30+ trillion tokens | Apr 2025 |
| Llama 3 training data | 15+ trillion tokens | Apr 2024 |
| Downloads | 1 billion (≈1.2 billion reported late April 2025) | Mar–Apr 2025 |
| Licence MAU threshold | 700 million monthly active users | 2023–2026 |
| Behemoth (unreleased) | ~2 trillion total / 288B active parameters | Apr 2025 |
| Llama 5 | Not announced | Sep 2026 |

## Sources
1. https://en.wikipedia.org/wiki/Llama_(language_model)
2. https://ai.meta.com/blog/llama-2/
3. https://ai.meta.com/blog/meta-llama-3/
4. https://ai.meta.com/blog/meta-llama-3-1/
5. https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/
6. https://ai.meta.com/blog/llama-4-multimodal-intelligence/
7. https://dev.meta.ai/llama/llama4/license
8. https://about.fb.com/news/2025/03/celebrating-1-billion-downloads-llama/
9. https://ai.meta.com/blog/llamacon-llama-news/
10. https://www.axios.com/2025/05/15/meta-behemoth-llama-scaling-delays
11. https://thenewstack.io/meta-abandons-llama-spark/
12. https://www.engadget.com/ai/meta-is-reportedly-working-on-a-new-ai-model-called-avocado-and-it-might-not-be-open-source-215426778.html
13. https://www.techzine.eu/news/analytics/140250/meta-is-developing-open-source-versions-of-its-next-frontier-ai-models/
14. https://en.wikipedia.org/wiki/Meta_Superintelligence_Labs
15. https://research.meta.ai/blog/introducing-muse-glimmer-open-agentic-model
