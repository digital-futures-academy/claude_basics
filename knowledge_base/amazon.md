---
doc_id: amazon
title: Amazon — Knowledge Base Profile
kb_version: 2026.09
last_verified: 2026-09-28
---
# Amazon

## Overview
Amazon.com, Inc. is a US public company (Nasdaq: AMZN) headquartered in Seattle, Washington, whose artificial intelligence activity is concentrated in Amazon Web Services (AWS), the world's largest cloud provider. Amazon's AI strategy spans three layers: custom AI chips (Trainium for training and inference, Inferentia for inference), the Amazon Bedrock managed model platform and agent tooling, and applications such as Alexa+, the Kiro coding tool and Amazon's own Nova foundation models. Amazon is also one of the largest strategic investors in frontier AI labs, holding major stakes in both Anthropic and OpenAI. This profile covers Amazon as an AI organisation rather than its retail business.

## Founding and leadership
Amazon was founded by Jeff Bezos in 1994 in Bellevue/Seattle, Washington; AWS launched its first public cloud services in 2006. Andy Jassy, who built AWS, has been Amazon's CEO since July 2021, and Matt Garman is CEO of AWS. In December 2025 Amazon reorganised its AI leadership: Rohit Prasad, SVP and head of Amazon's artificial general intelligence (AGI) group, left at the end of 2025, and Peter DeSantis, a 27-year Amazon veteran who previously ran AWS infrastructure, took charge of a unified organisation combining the Nova models and model research, custom silicon (Graviton, Trainium, Nitro) and quantum computing, reporting directly to Jassy. Robotics researcher Pieter Abbeel leads Amazon's frontier model research team within that AGI organisation. Panos Panay leads Amazon Devices & Services, including Alexa+. Amazon employed approximately 1.576 million people (full- and part-time) at the end of 2025.

## Funding, ownership and valuation
As a public company, Amazon's AI "funding" is best measured through capital expenditure, AWS revenue and strategic investments.
- **Capex:** Amazon's purchases of property and equipment were about $128.3 billion in 2025. In February 2026 Amazon guided to roughly $100 billion of 2026 capex, mostly for AWS and AI infrastructure; on 30 July 2026 Andy Jassy raised the 2026 plan to about $120 billion, citing higher memory costs, and said capacity would still not meet 2026 demand. AWS expects to double its power capacity by the end of 2027 versus 2025.
- **AWS revenue:** In Q4 2025 AWS revenue was $35.6 billion (+24% year on year). In Q2 2026 (reported 30 July 2026) AWS revenue was $42.2 billion (+37%, its fastest growth in 18 quarters), with a $169 billion annualised run rate, $16.6 billion operating income and a backlog of about $496 billion (up from $244 billion at end-2025). Amazon said its AI business and its chips business each exceeded a $25 billion annual revenue run rate, both growing at triple-digit percentages.
- **Anthropic:** Amazon invested $4 billion in Anthropic in 2023–24 and a further $4 billion in November 2024 ($8 billion in total). On 20 April 2026 Amazon announced a further $5 billion, with up to $20 billion more tied to commercial milestones (up to $33 billion in total); Anthropic in turn committed to spend more than $100 billion over ten years on AWS technologies for up to 5 gigawatts of capacity. Amazon's Q2 2026 net income of $62.6 billion included a $53.4 billion pre-tax non-operating gain on its Anthropic investment.
- **OpenAI:** After a $38 billion AWS compute deal in November 2025, Amazon announced on 27 February 2026 a $50 billion investment in OpenAI ($15 billion initially, $35 billion conditional) as part of a $110 billion OpenAI round at a reported $730 billion pre-money valuation, alongside an expanded $100 billion, eight-year AWS agreement and an OpenAI commitment to consume 2 gigawatts of Trainium capacity. PYMNTS reported that Amazon completed the full $50 billion by 31 July 2026; the conditions for the second tranche were reportedly tied to an OpenAI IPO or AGI, and Amazon did not say why it paid early.

## Model and product timeline
| Date | Release | Notes |
|---|---|---|
| Sep 2023 | Amazon Bedrock GA | Managed API for third-party and Amazon foundation models |
| Dec 2023 | Trainium2 announced | Later used in Project Rainier |
| 3 Dec 2024 | Amazon Nova (Micro, Lite, Pro, Canvas, Reel) | Micro 128K context; Lite and Pro 300K context |
| 26 Feb 2025 | Alexa+ unveiled | Generative-AI Alexa; $19.99/month or free with Prime |
| 31 Mar 2025 | Nova Act | Browser-automation agent model |
| 8 Apr 2025 | Nova Sonic | Speech-to-speech model |
| 30 Apr 2025 | Nova Premier | 1M-token context; teacher model for distillation |
| Oct 2025 | Project Rainier live | Anthropic cluster of roughly 500,000 Trainium2 chips |
| 2 Dec 2025 | Nova 2 (Lite, Pro, Sonic, Omni) and Nova Forge | 1M-token context; Nova 2 Lite GA, Pro and Omni in preview; Forge builds custom models from Nova checkpoints |
| 2 Dec 2025 | Trainium3 UltraServers GA; Trainium4 previewed | 3nm; up to 144 chips per UltraServer; 4.4x compute of Trn2; Trainium4 to support NVIDIA NVLink Fusion |
| 4 Feb 2026 | Alexa+ opens to all US users | Free for Prime members; $19.99/month otherwise |
| 27 Feb 2026 | OpenAI partnership | OpenAI models to be offered via Bedrock |
| 20 Apr 2026 | Claude Platform on AWS | Native Anthropic console accessible through AWS accounts |
| Mar and May 2026 | Nova 2 Sonic refreshes | May update cut speech hallucinations by 88% |
| Q2 2026 | Alexa+ international expansion | Germany, Austria, France and Brazil |

## Products and distribution
Amazon distributes AI mainly through AWS. **Amazon Bedrock** offers models from Anthropic (Claude), Meta, Mistral, OpenAI, Amazon Nova and others; Amazon said Bedrock has "hundreds of thousands of customers" and that customers spent more on Bedrock in Q2 2026 than in all prior quarters combined. **Bedrock AgentCore** provides infrastructure for deploying autonomous agents and added Payments, Web Search and Harness features in Q2 2026. **Amazon SageMaker** covers model training. **Kiro**, Amazon's spec-driven agentic coding tool, tripled usage quarter on quarter in Q2 2026. **Trainium** chips are rented through EC2 (Trn2 and Trn3 UltraServers), with commitments from Anthropic, OpenAI, Uber and Pinterest; at end-2025 about 1.4 million Trainium2 chips were deployed. On the consumer side, **Alexa+** became available to everyone in the US on 4 February 2026 (free for Prime members, $19.99/month otherwise); Amazon has said "tens of millions" joined its early-access programme but has not published a current user figure. Amazon's Rufus shopping assistant also uses generative AI.

## Research, safety and openness
Amazon's Nova models are proprietary and available only as hosted services on Bedrock, rather than as open weights; Nova Forge lets enterprises build custom variants from Nova checkpoints. Amazon published its Frontier Model Safety Framework on 9 February 2025 (updated September 2026), committing not to deploy frontier models that exceed critical-risk thresholds without appropriate safeguards, and it has published evaluations of Nova Premier and Nova 2.0 Lite (January 2026) under that framework. Amazon endorsed the Seoul (Korea) Frontier AI Safety Commitments. Research is published through Amazon Science. Amazon's largest research bet is arguably compute: Project Rainier and Trainium3/Trainium4 are designed to reduce reliance on NVIDIA GPUs, and Amazon's investments make it a major infrastructure provider to Anthropic, whose Claude models it also resells.

## Key figures at a glance
| Metric | Value | As of |
|---|---|---|
| Founded | 1994 (AWS 2006) | — |
| Headquarters | Seattle, Washington, USA | 2026 |
| CEO | Andy Jassy (AWS CEO: Matt Garman) | Sep 2026 |
| Employees | ~1.576 million | End 2025 |
| 2026 capex plan | ~$120 billion (raised from ~$100 billion) | 30 Jul 2026 |
| AWS quarterly revenue | $42.2 billion (+37% YoY) | Q2 2026 |
| AWS annualised run rate | $169 billion | Q2 2026 |
| AWS backlog | ~$496 billion | Q2 2026 |
| AI business run rate | >$25 billion | Q2 2026 |
| Anthropic investment | $8 billion + $5 billion (up to $20 billion more) | Apr 2026 |
| OpenAI investment | $50 billion | Feb–Jul 2026 |
| Flagship model / context | Nova 2 Pro / 1M tokens | Dec 2025 |
| Latest AI chip | Trainium3 (3nm, 144 chips per UltraServer) | Dec 2025 |

## Sources
1. https://www.aboutamazon.com/news/company-news/amazon-earnings-q2-2026-report
2. https://fortune.com/2026/07/30/andy-jassy-amazon-capex-demand-aws-pga-tour/
3. https://futurumgroup.com/insights/amazon-q4-fy-2025-revenue-beat-aws-24-amid-200b-capex-plan/
4. https://www.aboutamazon.com/news/company-news/amazon-invests-additional-5-billion-anthropic-ai
5. https://www.geekwire.com/2026/amazon-invests-50b-in-openai-deepens-aws-partnership-with-expanded-100b-cloud-deal/
6. https://www.pymnts.com/news/artificial-intelligence/2026/amazon-completes-50-billion-dollar-investment-openai/
7. https://www.geekwire.com/2025/amazon-ai-chief-rohit-prasad-leaving-infrastructure-exec-peter-desantis-to-lead-unified-ai-group/
8. https://hidekazu-konishi.com/entry/amazon_nova_model_release_timeline.html
9. https://docs.aws.amazon.com/nova/latest/nova2-userguide/release-notes.html
10. https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost
11. https://www.aboutamazon.com/news/devices/alexa-plus-available-free-prime-members-us
12. https://www.thestreet.com/retail/amazon-employees
13. https://www.amazon.science/publications/amazons-frontier-model-safety-framework
