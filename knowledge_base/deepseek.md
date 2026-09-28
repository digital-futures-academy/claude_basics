---
doc_id: deepseek
title: DeepSeek — Knowledge Base Profile
kb_version: 2026.09
last_verified: 2026-09-28
---
# DeepSeek

## Overview

DeepSeek (Hangzhou DeepSeek Artificial Intelligence Basic Technology Research Co., Ltd.) is a Chinese artificial intelligence company that develops open-weight large language models and the DeepSeek chatbot. DeepSeek is headquartered in Hangzhou, Zhejiang, China, and was spun out of, and long funded by, the quantitative hedge fund High-Flyer. DeepSeek became globally prominent in January 2025 when its DeepSeek-R1 reasoning model and app triggered a sell-off in US technology stocks, a moment Marc Andreessen called "AI's Sputnik moment". DeepSeek is privately held and controlled by its founder, Liang Wenfeng; in 2026 DeepSeek took external investment for the first time and began preparing for an onshore stock-market listing.

## Founding and leadership

DeepSeek was founded on 17 July 2023 by Liang Wenfeng, who co-founded the hedge fund High-Flyer in 2015 and serves as DeepSeek's chief executive. DeepSeek grew out of High-Flyer's AI research effort, which had built the Fire-Flyer GPU clusters (Fire-Flyer 2, from 2021, used about 5,000 Nvidia A100 GPUs) and reportedly acquired around 10,000 A100 GPUs before US export controls took effect. Liang Wenfeng personally held about 84% of DeepSeek through holding entities as of May 2024. DeepSeek had about 160 employees in 2025, a small headcount for a frontier lab, and is known for hiring young graduates and people from non-computer-science backgrounds. DeepSeek keeps a low public profile and rarely gives interviews or press briefings.

## Funding, ownership and valuation

DeepSeek was funded internally by High-Flyer until 2026 and did not take venture capital; Liang Wenfeng said in 2023 that "money has never been the problem for us; bans on shipments of advanced chips are the problem".

- **April 2026 (reported):** DeepSeek was reported to be seeking about $300 million at a $10 billion valuation.
- **June 2026 (reported by The Information and Reuters, not officially announced):** DeepSeek's first external round raised more than 50 billion yuan (about $7.4 billion) at a valuation of about $50 billion or more. Liang Wenfeng was the largest investor at about 20 billion yuan; Tencent (about 10 billion yuan), CATL (about 5 billion yuan), China's state-backed National AI Industry Investment Fund, NetEase, JD.com and IDG Capital also participated. Most investors bought into a limited partnership controlled by Liang, with no voting rights and a five-year lock-up; the state AI fund invested directly with voting rights.
- **16 July 2026:** A Chinese stock-exchange filing by Anhui Korrun (2.90 billion yuan for a 0.8265% indirect stake) implied a DeepSeek valuation of about 350.88 billion yuan ($51.82 billion), per Reuters.
- **July 2026 (reported by Reuters):** DeepSeek was said to be planning to raise up to a further 50 billion yuan at about 500 billion yuan ($74 billion), ahead of a planned IPO on Shanghai's STAR Market, with an internal target of filing in 2026. TechCrunch, citing Bloomberg on 14 July 2026, separately reported talks to raise $1.5 billion at a $71 billion valuation, with an IPO planned for 2027 or possibly late 2026. Reported figures differ between outlets, and none of these plans has been confirmed by DeepSeek.

DeepSeek does not publish revenue figures.

## Model and product timeline

| Date | Release | Notes |
|---|---|---|
| 2 Nov 2023 | DeepSeek Coder | 1.3B–33B code models, 16k context |
| 29 Nov 2023 | DeepSeek LLM | 7B and 67B, base and chat |
| Jan 2024 | DeepSeek-MoE | 16B total / 2.7B active mixture-of-experts |
| May 2024 | DeepSeek-V2 | 236B total / 21B active, 128k context; introduced multi-head latent attention (MLA) |
| Dec 2024 | DeepSeek-V3 | 671B total / 37B active MoE, 128k context, MIT licence; final training run reported at 2.788M H800 GPU hours (~$5.6m) |
| 10 Jan 2025 | DeepSeek app | iOS and Android chatbot app |
| 20 Jan 2025 | DeepSeek-R1 | Open reasoning model (MIT) plus distilled 1.5B–70B versions; app topped the US App Store by 27 Jan 2025 |
| 24 Mar 2025 | DeepSeek-V3-0324 | V3 update; AIME score up from 39.6 to 59.4 |
| 28 May 2025 | DeepSeek-R1-0528 | AIME 2025 score up from 70.0 to 87.5 |
| 21 Aug 2025 | DeepSeek-V3.1 | Hybrid thinking/non-thinking modes; 66.0 SWE-bench Verified |
| 29 Sep 2025 | DeepSeek-V3.2-Exp | Introduced DeepSeek Sparse Attention (DSA) |
| 1 Dec 2025 | DeepSeek-V3.2 | Plus temporary V3.2-Speciale reasoning variant |
| 24 Apr 2026 | DeepSeek-V4 preview | V4-Pro: 1.6T total / 49B active; V4-Flash: 284B / 13B active; 1M-token context; MIT licence |
| 31 Jul / 13 Aug 2026 | V4-Flash update / V4-Pro general release | Enhanced agent capabilities; OpenAI Responses API support; off-peak pricing at 50% |
| 10 Sep 2026 | DeepSeek-V4.1-Flash | Native multimodal visual understanding; replaced V4-Flash and V4-Flash-Vision-Exp |

## Products and distribution

DeepSeek offers a free chatbot at chat.deepseek.com and in iOS and Android apps, and a low-priced developer API compatible with the OpenAI ChatCompletions and Anthropic API formats, so DeepSeek models can be used inside agent tools such as Claude Code and OpenCode. With the V4 launch, a 1-million-token context window became standard across DeepSeek's official services, and the legacy `deepseek-chat` and `deepseek-reasoner` API names were retired after 24 July 2026. DeepSeek's open weights are published on Hugging Face and are widely hosted by third-party clouds and adopted by Chinese chipmakers such as Huawei and Cambricon.

DeepSeek user numbers: by 27 January 2025 the DeepSeek app had overtaken ChatGPT as the most-downloaded free iOS app in the United States. According to QuestMobile, DeepSeek had about 130 million monthly active users in May 2026, ranking third among Chinese AI-native apps behind Doubao (382 million) and Qwen (167 million).

DeepSeek faces restrictions abroad: Italy's data-protection authority blocked the app in January 2025; South Korea suspended new downloads in February 2025; Australia, Taiwan and Canada banned it on government devices; several US agencies prohibited its use, and the US Fiscal 2026 National Defense Authorization Act barred the Department of Defense and intelligence community from using DeepSeek AI. The DeepSeek chatbot censors topics sensitive to the Chinese government, such as Tiananmen Square and Taiwan.

## Research, safety and openness

DeepSeek is one of the most prominent open-weight developers: DeepSeek-V3, R1 and V4 are released under the permissive MIT licence, with detailed technical reports. DeepSeek's notable research includes multi-head latent attention, fine-grained mixture-of-experts, multi-token prediction, FP8 training, reinforcement learning for reasoning (R1-Zero), DeepSeek Sparse Attention and, in V4, a hybrid compressed attention mechanism that needs only 27% of the single-token inference FLOPs and 10% of the KV cache of V3.2, trained on more than 32 trillion tokens with the Muon optimiser. In September 2025 the DeepSeek-R1 paper appeared in Nature, reportedly the first major LLM to pass peer review in a leading journal; it disclosed that R1's reasoning-specific training cost about $2.94 million using 512 Nvidia H800 GPUs, excluding the roughly $5.6 million base-model cost. Critics say DeepSeek's headline cost figures omit research, staff and hardware costs.

DeepSeek has published little on safety frameworks, and independent evaluators have criticised weak safeguards. In February 2026 Anthropic accused DeepSeek of using fraudulent accounts to generate large volumes of Claude conversations for training (an allegation, not a legal finding). The New York Times has reported links between some DeepSeek researchers and People's Liberation Army-affiliated laboratories.

## Key figures at a glance

| Metric | Value | As of |
|---|---|---|
| Founded | 17 July 2023 | 2023 |
| Headquarters | Hangzhou, Zhejiang, China | 2026 |
| Founder and CEO | Liang Wenfeng (also co-founder of High-Flyer) | Sep 2026 |
| Employees | ~160 | 2025 |
| First external round | ~$7.4bn (50bn+ yuan), reported | Jun 2026 |
| Filing-implied valuation | ~$51.82bn (350.88bn yuan) | 16 Jul 2026 |
| Reported next-round target valuation | ~$74bn (500bn yuan) | Jul 2026 |
| Monthly active users (China, QuestMobile) | ~130 million | May 2026 |
| Flagship model | DeepSeek-V4-Pro: 1.6T total / 49B active parameters | Apr 2026 |
| Context window | 1 million tokens | Apr 2026 |
| DeepSeek-V3 size | 671B total / 37B active | Dec 2024 |
| R1 reasoning training cost (Nature) | ~$2.94 million on 512 H800 GPUs | Sep 2025 |

## Sources

1. https://en.wikipedia.org/wiki/DeepSeek
2. https://en.wikipedia.org/wiki/DeepSeek_(chatbot)
3. https://api-docs.deepseek.com/news/news260424/
4. https://api-docs.deepseek.com/updates/
5. https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro
6. https://the-decoder.com/deepseek-takes-outside-money-for-the-first-time-at-a-50-billion-valuation/
7. https://www.forbes.com/sites/anishasircar/2026/06/17/deepseek-just-raised-74-billion-heres-the-catch/
8. https://www.investing.com/news/stock-market-news/chinese-filing-implies-deepseek-valuation-of-around-52-billion-4796314
9. https://www.investing.com/news/stock-market-news/chinas-deepseek-to-raise-fresh-capital-at-74-billion-valuation-ahead-of-onshore-ipo-sources-say-4799575
10. https://techcrunch.com/2026/07/14/deepseek-reportedly-in-talks-to-raise-1-5b-then-ipo/
11. https://www.theregister.com/2025/09/19/deepseek_cost_train/
12. https://technode.com/2026/07/14/questmobile-chinas-ai-native-apps-reach-499-million-monthly-active-users/
13. https://www.aljazeera.com/economy/2026/4/24/chinas-deepseek-unveils-latest-model-a-year-after-upending-global-tech
