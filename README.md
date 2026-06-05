# 🔬 Research Orchestrator

> **Multi-agent AI research system** — a Supervisor orchestrates Search, Critic, and Writer agents in an iterative loop, producing structured research reports with real-time observability.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## ✨ What It Does

A Supervisor agent receives your research query, generates a structured plan, and dynamically routes tasks to three specialized sub-agents:

```
User Query
    │
    ▼
Supervisor ──► Search Agent ──► Critic Agent
                  ▲                  │
                  │   score < 7      │   score ≥ 7
                  └──────────────────┘        │
                                              ▼
                                        Writer Agent
                                              │
                                              ▼
                                      Final Research Report
```

The **Critic Agent** scores each research pass (0–10). If quality is below the threshold (default 7), it sends the search query back with specific gaps to address. This loop runs up to 3 times before the **Writer Agent** synthesizes the final Markdown report.

---

## 🗂 Project Structure

```
research-orchestrator/
│
├── backend/
│   ├── agents/
│   │   ├── supervisor.py       # Parses query → research plan (JSON)
│   │   ├── search_agent.py     # Synthesizes research content
│   │   ├── critic.py           # Scores quality, approves or loops back
│   │   └── writer.py           # Produces final Markdown report
│   │
│   ├── api/
│   │   └── routes.py           # FastAPI SSE endpoint + health check
│   │
│   └── core/
│       ├── config.py           # Env vars + settings
│       ├── gemini_client.py    # Async Gemini API wrapper
│       └── models.py           # Pydantic schemas
│
├── frontend/
│   ├── index.html              # App shell (links to CSS + JS)
│   ├── css/
│   │   └── style.css           # All styles
│   └── js/
│       ├── api.js              # SSE stream client
│       ├── ui.js               # DOM state manager
│       └── main.js             # Orchestration controller
│
├── docs/
│   └── ARCHITECTURE.md         # System design + event schema
│
├── main.py                     # FastAPI app entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/shantanukumar/research-orchestrator.git
cd research-orchestrator

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com).

### 3. Run the backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open the frontend

Open `frontend/index.html` in your browser, or use Live Server (VS Code extension).

The frontend auto-detects `localhost` and points to `http://127.0.0.1:8000`.

---

## 🔌 API Reference

### `POST /api/v1/research/stream`

Streams Server-Sent Events (SSE) as agents process the query.

**Request body:**
```json
{
  "query": "Impact of LangGraph on enterprise AI adoption",
  "api_key": "AIza...",
  "max_iterations": 3
}
```

**SSE event format:**
```json
{
  "agent":   "supervisor | search | critic | writer | system",
  "type":    "log | status | metric | result",
  "message": "Human-readable message",
  "thinking": false,
  "data":    {}
}
```

Stream ends with `data: [DONE]`.

### `GET /api/v1/health`

```json
{ "status": "ok", "service": "research-orchestrator" }
```

---

## 🛠 Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3.11, FastAPI, Uvicorn     |
| AI Model  | Google Gemini 2.0 Flash           |
| Streaming | Server-Sent Events (SSE)          |
| Frontend  | Vanilla JS (ES Modules), CSS3     |
| HTTP      | httpx (async)                     |
| Validation| Pydantic v2                       |

---

## ⚙️ Configuration

| Variable            | Default              | Description                        |
|---------------------|----------------------|------------------------------------|
| `GEMINI_API_KEY`    | —                    | Your Gemini API key (required)     |
| `GEMINI_MODEL`      | `gemini-2.0-flash`   | Model name                         |
| `GEMINI_MAX_TOKENS` | `1500`               | Max tokens per agent call          |
| `MAX_ITERATIONS`    | `3`                  | Max research loops before Writer   |
| `QUALITY_THRESHOLD` | `7`                  | Critic score to approve (0–10)     |
| `CORS_ORIGINS`      | `localhost:3000,...` | Allowed frontend origins           |

---

## 👤 Author

**Shantanu Kumar** — AI Engineer
Building production multi-agent systems with AutoGen, LangGraph, and MCP.

[![GitHub](https://img.shields.io/badge/GitHub-shantanukumar-black?style=flat-square&logo=github)](https://github.com/shantanukumar)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-shantanukumar-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/shantanuk86)

---

## 📄 License

MIT — feel free to use, fork, and build on top of this.
