# 🔬 Research Orchestrator

A multi-agent AI system where a **Supervisor** orchestrates Search, Critic, and Writer agents in an iterative loop — streaming every decision live to a terminal-style UI.

Built this because single-pass LLM research is unreliable. Agents that argue with each other produce better output.

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-3.5_Flash-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## why I built this

Most "AI research tools" are just one fat prompt. They hallucinate, miss contradictions, and have no idea what they don't know.

This system uses four agents that actually check each other's work:

```
Your query
    │
    ▼
Supervisor        ← breaks down the topic, writes the research plan
    │
    ▼
Search Agent      ← synthesizes knowledge across multiple angles
    │
    ▼
Critic Agent      ← scores 0–10, flags gaps, decides: approve or loop back?
    │
    ├── score < 7 → back to Search (with specific gaps to fix)
    │
    └── score ≥ 7 → Writer Agent → final structured report
```

The Critic loop runs up to 3 times. In testing, most queries needed 2 passes before approval. The final output is noticeably more accurate than a single-shot prompt.

---

## what it looks like

- Live pipeline nodes pulse as each agent activates
- Every agent message streams into a real-time communication log
- Iteration tracker shows exactly how many research loops ran
- Metrics panel: iterations, elapsed time, messages, token count
- Final report downloads as a clean `.md` file

---

## project structure

```
research-orchestrator/
│
├── backend/
│   ├── agents/
│   │   ├── supervisor.py       # query → JSON research plan
│   │   ├── search_agent.py     # multi-angle knowledge synthesis
│   │   ├── critic.py           # quality scorer, gap detector
│   │   └── writer.py           # final markdown report
│   │
│   ├── api/
│   │   └── routes.py           # SSE streaming endpoint
│   │
│   └── core/
│       ├── config.py           # env vars
│       ├── gemini_client.py    # async Gemini wrapper
│       └── models.py           # Pydantic schemas
│
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── api.js              # SSE reader
│       ├── ui.js               # all DOM updates
│       └── main.js             # wires API → UI
│
├── docs/ARCHITECTURE.md
├── main.py                     # FastAPI entry
├── requirements.txt
└── .env.example
```

---

## running it locally

**1. clone and set up**

```bash
git clone https://github.com/shantanukumar/research-orchestrator.git
cd research-orchestrator

# recommended: use uv (way faster than pip)
brew install uv
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

**2. add your API key**

```bash
cp .env.example .env
# open .env and set GEMINI_API_KEY=AIza...
```

Free key at [aistudio.google.com](https://aistudio.google.com) — no credit card needed.

**3. start the server**

```bash
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000` and run your first query.

---

## API

### `POST /api/v1/research/stream`

Streams SSE events as agents work. Each event is a JSON object:

```json
{
  "agent":   "supervisor | search | critic | writer | system",
  "type":    "log | status | metric | result",
  "message": "what the agent is doing",
  "thinking": false,
  "data":    {}
}
```

Stream ends with `data: [DONE]`.

**Request body:**
```json
{
  "query": "Impact of MCP protocol on AI tooling in 2025",
  "api_key": "AIza...",
  "max_iterations": 3
}
```

### `GET /api/v1/health`
```json
{ "status": "ok", "service": "research-orchestrator" }
```

---

## config

| Variable            | Default            | What it does                          |
|---------------------|--------------------|---------------------------------------|
| `GEMINI_API_KEY`    | —                  | required                              |
| `GEMINI_MODEL`      | `gemini-3.5-flash` | swap to pro if you want heavier runs  |
| `GEMINI_MAX_TOKENS` | `1500`             | per agent call                        |
| `MAX_ITERATIONS`    | `3`                | critic loop ceiling                   |
| `QUALITY_THRESHOLD` | `7`                | critic score needed to pass (0–10)    |

---

## stack

| what         | how                          |
|--------------|------------------------------|
| backend      | Python 3.12, FastAPI, Uvicorn |
| AI           | Gemini 3.5 Flash (4 agents)  |
| streaming    | Server-Sent Events           |
| frontend     | Vanilla JS ES Modules, CSS3  |
| HTTP client  | httpx async                  |
| validation   | Pydantic v2                  |

No framework bloat on the frontend. No webpack. Just ES modules and a `<script type="module">`.

---

## things I want to add

- [ ] web search tool for Search Agent (real-time Serper/Tavily)
- [ ] LangSmith tracing integration
- [ ] persistent run history (SQLite)
- [ ] export report as PDF
- [ ] swap model per-agent (e.g. pro for Critic, flash for Search)

PRs welcome.

---

built by **Shantanu Kumar** — AI engineer
working with multi-agent systems, MCP, and LLMs.

[![GitHub](https://img.shields.io/badge/GitHub-shantanukumar-black?style=flat-square&logo=github)](https://github.com/shantanuk86)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-shantanukumar-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/shantanuk86)

---

MIT license. use it, fork it, build on it.
