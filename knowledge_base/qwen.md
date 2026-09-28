---
doc_id: qwen
title: Qwen — Knowledge Base Profile
kb_version: 2026.09
last_verified: 2026-09-28
---
# Qwen

## Overview
Qwen (from the Chinese name Tongyi Qianwen, 通义千问) is the family of large language and multimodal models developed by Alibaba Group, headquartered in Hangzhou, China. Qwen is not a separate company: it is built by the Qwen team within Alibaba's Tongyi Lab and distributed through Alibaba Cloud. The Qwen family spans open-weight dense and mixture-of-experts (MoE) models from under 1 billion to 2.4 trillion parameters, proprietary "Max" and "Plus" flagship models served via API, and a consumer Qwen app. By 2026 Qwen was the most-derived open model family on Hugging Face, and Alibaba had positioned Qwen as the centre of a "full-stack AI" strategy spanning chips, cloud and applications.

## Founding and leadership
Alibaba launched Tongyi Qianwen as a beta chatbot in April 2023 and made it publicly available in September 2023 after Chinese regulatory clearance; open-weight Qwen models (starting with Qwen-7B in 2023, followed by 72B and 1.8B weights in December 2023) established the Qwen brand internationally. Alibaba Group CEO Eddie Wu (Wu Yongming) oversees the AI strategy and personally approved key Qwen leadership changes. Junyang Lin (Lin Junyang), the long-time technical lead and public face of Qwen, resigned in early March 2026, shortly after the Qwen3.5 launch, amid reported internal disputes and a reorganisation; Alibaba approved the resignation around 5 March 2026 (reported by Pandaily and others). Following Lin's departure, Alibaba CTO and chief AI architect Zhou Jingren assumed control of Qwen, and Zhou Hao, formerly of Google DeepMind, joined to lead post-training. Wu Jia, an Alibaba vice-president, heads the Qwen consumer business group. A separate headcount for the Qwen team has not been officially disclosed.

## Funding, ownership and valuation
Qwen is wholly owned and funded by Alibaba Group Holding (NYSE: BABA; HKEX: 9988); it has no external funding rounds or standalone valuation. On 24 February 2025 Alibaba announced it would invest RMB 380 billion (about US$53 billion) in AI and cloud infrastructure over three years — more than its total AI and cloud spending over the previous decade — with Eddie Wu naming artificial general intelligence as the primary goal. In May 2026 Wu said Alibaba was likely to "overshoot" the RMB 380 billion target because of the cost of AI data-centre buildout (SCMP); by August 2026 SCMP described Alibaba as roughly halfway through the plan (which it converted as US$56 billion). Alibaba reported AI-related product revenue growing at triple digits for an 11th consecutive quarter (May 2026), and projected annualised recurring revenue from AI models and applications of RMB 30 billion (about US$4.42 billion) by year-end. Cloud Intelligence revenue grew 45% in the quarter to June 2026, its fastest pace in 22 quarters. At the Apsara Conference (22 September 2026) Alibaba set a target of more than 20 GW of global data-centre capacity by 2032. In August 2026 Alibaba signalled it would move some Qwen models towards a revenue-sharing licence for large commercial providers (see Research, safety and openness).

## Model and product timeline
| Date | Release | Notes |
|---|---|---|
| Apr 2023 | Tongyi Qianwen beta | Alibaba's first chatbot; public release Sept 2023 after regulatory approval |
| Dec 2023 | Qwen-72B / Qwen-1.8B | Open weights, extending the 2023 Qwen-7B/14B releases |
| 7 Jun 2024 | Qwen2 | 0.5B, 1.5B, 7B, 57B-A14B (MoE), 72B; up to 128K context; 27 extra languages; 72B under Qianwen licence, others Apache 2.0 |
| 19 Sep 2024 | Qwen2.5 | 0.5B–72B, plus Coder and Math; up to 18T training tokens; 128K context; Apache 2.0 except 3B and 72B |
| Nov 2024 (preview); 6 Mar 2025 | QwQ-32B | Open reasoning model (Apache 2.0); Qwen claims performance comparable to 671B-parameter DeepSeek-R1 |
| 29 Apr 2025 | Qwen3 | Dense 0.6B–32B plus MoE 30B-A3B and 235B-A22B (128 experts, 8 active); ~36T tokens; 119 languages; hybrid thinking modes; Apache 2.0 |
| 24 Sep 2025 | Qwen3-Max | Proprietary, over 1 trillion parameters, MoE; 262,144-token context |
| Nov 2025 | Qwen app (public beta) | Consumer assistant; 100M MAU by Jan 2026 |
| 17 Feb 2026 | Qwen3.5-397B-A17B | Open weights, Apache 2.0; 397B total / 17B active; native text-image-video; 262K context |
| 2 Apr / 17 Apr 2026 | Qwen3.6-Plus / Qwen3.6-35B-A3B | Plus hosted with 1M context; 35B-A3B open under Apache 2.0 |
| 3 Aug 2026 | Qwen3.8-Max (API) | 2.4T total / ~95B active MoE; 1M context; $2 / $6 per million input/output tokens |
| 12–14 Aug 2026 | Qwen3.8 open weights | Qwen3.8-2.4T-A95B (512 experts, custom Qwen3.8-Max licence) and dense multimodal Qwen3.8-27B (Apache 2.0, 262K native context) |
| 2 Sep 2026 | Qwen3.8-Max-0902 | Update focused on coding and agents |
| 22 Sep 2026 | Qwen 4 (announced in training) | Previewed at Apsara 2026; no release date, size or licence published; Qwen 4.5/5 roadmap targets 5–10T parameters |

## Products and distribution
Qwen models are distributed in three main ways. First, open weights are published on Hugging Face and Alibaba's ModelScope, typically with Apache 2.0 licences for small and mid-sized models. Second, proprietary and hosted models (Qwen-Max, Qwen-Plus, Qwen-Flash tiers) are sold via Alibaba Cloud Model Studio (Bailian) APIs; Qwen3.8-Max is priced at US$2.00 per million input tokens and US$6.00 per million output tokens. Third, the consumer Qwen app (Qianwen), launched in public beta in mid-November 2025, reached 100 million monthly active users by January 2026 (SCMP) and 167 million MAU in May 2026, second in China behind ByteDance's Doubao (382 million) and ahead of DeepSeek (130 million), according to QuestMobile. Other sources cite higher Qwen app figures (e.g. 234 million by May 2026 on Wikipedia); these are not QuestMobile figures and should be treated as unconfirmed. A January 2026 upgrade extended the Qwen app into voice-driven shopping, travel booking and other everyday tasks through deeper integration with Alibaba's ecosystem. At Apsara 2026 Alibaba unveiled hardware including a "Qwen Book" agentic computer and AI wearables, and reported 30 million users of QwenWork in its first month. Qwen also underpins third-party projects such as AI Singapore's Sea-Lion model (reported November 2025) and, reportedly, Apple Intelligence features in mainland China.

## Research, safety and openness
Qwen is one of the world's most prominent open-weight model families. Most small and mid-size releases since Qwen2 use the permissive Apache 2.0 licence, while some flagships (Qwen2-72B, Qwen2.5-3B and -72B) used the custom Qwen/Qianwen licence, and Max-class models were API-only until August 2026. The open release of Qwen3.8-2.4T-A95B, described as the first Qwen-Max-class open model, came with a custom Qwen3.8-Max Licence: products with over 100 million MAU or over US$20 million monthly revenue must display the model name prominently, and AI service businesses above US$50 million annual revenue must obtain a separate licence. Reporting in August 2026 (AI News) described Alibaba testing a revenue-sharing model for large model-as-a-service providers, with the rate not yet finalised. Hugging Face's "State of Open Models: Summer 2026" counted 151,448 Qwen derivatives on the Hub (2.6 times Meta's footprint), about 180–210 new Qwen-based repositories per day in 2026, and about 2.05 billion Qwen downloads in 2026. Notable research directions include hybrid thinking/non-thinking modes (Qwen3), MoE scaling to 512 experts, native multimodality, and, as described at Apsara 2026, recursive self-improvement experiments. Alibaba has not published a safety framework comparable to Western frontier-lab responsible scaling policies; Chinese-hosted Qwen services are subject to Chinese content regulation. Self-reported Qwen benchmark claims (for example Qwen3.8-27B at 61.7% on SWE-bench Pro) had not been independently verified at the time of release.

## Key figures at a glance
| Metric | Value | As of |
|---|---|---|
| Parent / HQ | Alibaba Group, Hangzhou, China | 2026 |
| First launch (Tongyi Qianwen beta) | April 2023 | 2023 |
| Alibaba AI and cloud capex pledge | RMB 380bn (~US$53bn) over 3 years | 24 Feb 2025 |
| Largest open-weight model | Qwen3.8-2.4T-A95B: 2.4T total, 95B active, 512 experts | Aug 2026 |
| Flagship API model | Qwen3.8-Max (1M-token context) | Sep 2026 |
| Qwen3.8-Max API price | US$2.00 in / US$6.00 out per million tokens | Aug 2026 |
| Qwen3 training data | ~36T tokens, 119 languages | Apr 2025 |
| Qwen derivatives on Hugging Face | 151,448 | Summer 2026 |
| Qwen downloads in 2026 | ~2.05 billion | Summer 2026 |
| Qwen app MAU (QuestMobile) | 167 million (No. 2 in China) | May 2026 |
| Qwen app MAU (first milestone) | 100 million | Jan 2026 |
| Next generation | Qwen 4 in training; 5–10T-parameter roadmap | 22 Sep 2026 |

## Sources
1. https://en.wikipedia.org/wiki/Qwen
2. https://qwenlm.github.io/blog/qwen2/
3. https://qwenlm.github.io/blog/qwen2.5/
4. https://qwenlm.github.io/blog/qwen3/
5. https://qwenlm.github.io/blog/qwq-32b/
6. https://cybernews.com/ai-news/alibaba-released-trillion-parameter-model-qwen3-max/
7. https://artificialanalysis.ai/articles/qwen3-5-397b-a17b-everything-you-need-to-know
8. https://www.noze.it/en/insights/qwen-3-6/
9. https://www.datacamp.com/blog/qwen3-8-max
10. https://sqmagazine.co.uk/qwen3-8-open-weights-two-licenses/
11. https://www.artificialintelligence-news.com/news/alibaba-qwen-open-source-ai-revenue-sharing/
12. https://huggingface.co/blog/state-of-open-models-summer-2026
13. https://www.alibabacloud.com/blog/alibaba-to-invest-rmb380-billion-in-ai-and-cloud-infrastructure-over-next-three-years_602007
14. https://www.scmp.com/tech/big-tech/article/3353451/alibaba-ai-revenue-logs-triple-digit-growth-11th-quarter-amid-strategic-reshuffle
15. https://www.scmp.com/tech/article/3364825/alibaba-signals-faster-ai-payoff-margin-gains-halfway-through-us56-billion-capex-plan
16. https://www.scmp.com/tech/tech-trends/article/3339968/alibabas-qwen-ai-app-hits-100-million-users-upgrade-broadens-role-daily-life
17. https://technode.com/2026/07/14/questmobile-chinas-ai-native-apps-reach-499-million-monthly-active-users/
18. https://pandaily.com/alibaba-approves-qwen-lead-lin-junyang-s-resignation-cto-zhou-jingren-assumes-control-deep-mind-s-zhou-hao-joins
19. https://www.alizila.com/aliviews-eddie-wu-shares-alibabas-strategic-full-stack-ai-roadmap-at-the-2026-apsara-conference/
20. https://www.alizila.com/alibaba-clouds-2026-apsara-conference-full-stack-ai-roadmap-along-with-global-market-expansion-plan/
21. https://www.versely.studio/blog/qwen-4-announced-at-apsara-2026
