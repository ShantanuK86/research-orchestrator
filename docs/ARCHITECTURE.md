# Architecture

## Overview

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
│                                                         │
│  POST /api/v1/research/stream  (SSE streaming)          │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Orchestration Engine                │   │
│  │                                                  │   │
│  │  1. Supervisor Agent                             │   │
│  │     └─ Generates research plan (JSON)            │   │
│  │                                                  │   │
│  │  2. Research Loop (up to 3 iterations)           │   │
│  │     ├─ Search Agent  → synthesizes knowledge     │   │
│  │     └─ Critic Agent  → scores 0-10, approve?     │   │
│  │           │                                      │   │
│  │           ├─ score ≥ 7  → proceed to Writer      │   │
│  │           └─ score < 7  → loop back to Search    │   │
│  │                                                  │   │
│  │  3. Writer Agent                                 │   │
│  │     └─ Produces final Markdown report            │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
    │  SSE events (AgentEvent JSON)
    ▼
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Vanilla JS)                  │
│                                                         │
│  api.js   → SSE stream reader                           │
│  ui.js    → DOM updates (pipeline nodes, log, metrics)  │
│  main.js  → Connects API events → UI state              │
└─────────────────────────────────────────────────────────┘
```

## Agent Prompts

Each agent has a fixed system prompt in its module under `backend/agents/`:

| Agent      | File             | Output format     |
|------------|------------------|-------------------|
| Supervisor | supervisor.py    | JSON plan         |
| Search     | search_agent.py  | Markdown text     |
| Critic     | critic.py        | JSON evaluation   |
| Writer     | writer.py        | Markdown report   |

## SSE Event Schema

```json
{
  "agent":   "supervisor | search | critic | writer | system",
  "type":    "log | status | metric | result",
  "message": "Human-readable message",
  "thinking": false,
  "data":    { "optional": "payload" }
}
```

## Environment Variables

See `.env.example` for full list.
Key ones: `GEMINI_API_KEY`, `MAX_ITERATIONS`, `QUALITY_THRESHOLD`.
