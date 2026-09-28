# Claude SDK Workshop: Build a Multi-Agent Fact-Checking Team

In this 45-minute hands-on session you'll build a small team of Claude agents with the Claude SDK, then break it on purpose to see the multi-agent antipatterns you're most likely to meet in the Claude certification exams.

```
                 question ──▶  ORCHESTRATOR  ──▶ briefing + lineage table
                               │          ▲
                  research brief          claim IDs
                               ▼          │
                     WEB-RESEARCHER    POLICY-REVIEWER
                    (Tavily search)    (knowledge base + review policy)
                     the two specialists never talk to each other
```

- **Orchestrator:** breaks your question into facts, delegates, and weighs up the results.
- **Web researcher:** searches the web and records every fact as a *claim* with its source and a quote taken from the page it retrieved.
- **Policy reviewer:** checks each claim against an internal knowledge base (FAISS vector search) and a written review policy.

Along the way you'll see: the agentic loop (`stop_reason`), tool design and tool descriptions, how many tools each agent should get, passing state between agents, verification and lineage, and the antipatterns that break all of these.

---

## Before the session (10 minutes)

### 1. What you need
- **Python 3.10–3.13**
- **Jupyter** or **VS Code** with the Python and Jupyter extensions
- An **OpenRouter API key** with a little credit on it. A full run of the notebook costs roughly US$0.15–0.30.
- *(Optional)* A free **Tavily** key from [app.tavily.com](https://app.tavily.com) for live web search. Without one, the web researcher uses a saved snapshot of real search results, and everything still works.

### 2. Get the code and install
```bash
git clone https://github.com/digital-futures-academy/claude_basics/tree/main
cd claude_basics

python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Add your keys
Copy the example file, then open `.env` and paste in your keys:
```bash
copy .env.example .env        # Windows
cp .env.example .env          # macOS / Linux
```
```
OPENROUTER_API_KEY=sk-or-v1-...
TAVILY_API_KEY=tvly-...        # optional
```
> Create or edit `.env` in **VS Code**, not in Notepad or PowerShell, which can save it in an encoding Python won't read. Never commit `.env` (it's already in `.gitignore`).

### 4. Check it works
Open **`multi_agent_workshop_STUDENT.ipynb`**, pick your `.venv` kernel, and run the first few cells. You should see:
```
OpenRouter key : set
Tavily key     : set            (or: missing -> web_search uses the offline cache)
...
Knowledge base: 9 docs, 67 chunks | embedded 67 chunks with mistralai/mistral-embed-2312
```
The first run builds the search index (a few seconds and a fraction of a cent). Later runs load it from `.cache/`.

---

## During the session

Work in **`multi_agent_workshop_STUDENT.ipynb`**. There are three ✏️ **GAP** cells. Each is mostly written already; you fill in the `____` blanks (or, in GAP 1, the missing sentence):

| Gap | What you'll add | Why it matters |
|---|---|---|
| **1** | The opening sentence of the reviewer's main tool description | Claude picks tools from their descriptions alone |
| **2** | Three blanks in the agentic loop | The loop is the core of every Claude agent |
| **3** | The fields passed from the researcher to the reviewer | What you pass between agents decides what they can do |

🆘 **Stuck or behind?** Each gap has a commented-out line that imports the reference answer. Uncomment it and carry on.

When you reach a 💡 **Let's talk** cell, pause. That's where we discuss as a group.

| # | Section |
|---|---|
| 1 | Setup and a first API call |
| 2 | The knowledge base and FAISS |
| 3 | Tools: small, specialised, well described (**GAP 1**) |
| 4 | The agentic loop (**GAP 2**) |
| 5 | Specialists and handoffs (**GAP 3**) |
| 6 | Run the whole team |
| 7 | Lineage and verification: who's right? |
| 8 | Antipattern lab |
| 9 | The same team built with the **Claude Agent SDK** (instructor demo) |

---

## What's in the repo

| Path | What it is |
|---|---|
| `multi_agent_workshop_STUDENT.ipynb` | **The notebook you work in** |
| `multi_agent_workshop_SOLUTION.ipynb` | The completed notebook. Try not to peek until after the session. |
| `agent_sdk_version.py` | The same system rebuilt with the Claude Agent SDK (subagents, `@tool`, hooks) |
| `knowledge_base/` | 9 profiles of AI organisations: the reviewer's "ground truth" |
| `review_policy.md` | The rules the reviewer applies: provenance, source tiers, recency, tolerances |
| `data/search_cache.json` | Saved web-search results, used when Tavily isn't available |
| `workshop_lib/` | Supporting code: config, search index, tool implementations, tracing, and the reference solution |

**Models** (all through OpenRouter; you can change them in `.env`):
- Orchestrator: `anthropic/claude-sonnet-5`
- Specialists: `anthropic/claude-haiku-4.5`
- Embeddings: `mistralai/mistral-embed-2312`

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `OpenRouter key : MISSING` | Check that `.env` sits in the repo's top folder and the line reads `OPENROUTER_API_KEY=...` with no quotes or spaces. Restart the kernel after editing. |
| `ModuleNotFoundError: workshop_lib` | Open the notebook from the repo's top folder, and make sure the kernel is your `.venv`. |
| `Knowledge base: ... keyword fallback` | The embeddings call failed (key, credit or network). The notebook still runs with simpler keyword search. Fix the key and re-run the cell. |
| `NameError: name '____' is not defined` | You've reached a gap that isn't filled in yet. Fill the blanks, or use the 🆘 line. |
| `401` / `402` errors from OpenRouter | The key is wrong or has no credit left. |
| Section 9 fails on **Windows** | The Agent SDK needs the Claude Code CLI installed separately on Windows. It's an instructor demo, so you can just watch. |

---

## After the session
- Try the other questions suggested in section 6, and see which knowledge-base entries get challenged.
- Add a live Tavily key and compare the results with the cached ones.
- Stretch goal: some rules are only *requested* in a prompt. Move one of them into code, for example set `kb_possibly_wrong` inside the `submit_review` handler, and see what changes.
