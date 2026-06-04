from pydantic import BaseModel, Field
from typing import Optional


# ── Request ──────────────────────────────────────────────
class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=500, description="Research topic")
    api_key: Optional[str] = Field(None, description="Override Gemini API key (optional if set in .env)")
    max_iterations: Optional[int] = Field(None, ge=1, le=5)


# ── Agent outputs ─────────────────────────────────────────
class SupervisorPlan(BaseModel):
    topic: str
    plan: str
    search_queries: list[str]
    quality_criteria: list[str]
    max_iterations: int


class CritiqueResult(BaseModel):
    quality_score: int
    approve: bool
    gaps: list[str]
    critique: str
    improvements: list[str]


# ── SSE event payload ─────────────────────────────────────
class AgentEvent(BaseModel):
    agent: str          # supervisor | search | critic | writer | system
    type: str           # log | status | metric | result
    message: str
    thinking: bool = False
    data: Optional[dict] = None


# ── Final response (non-streaming) ───────────────────────
class ResearchResponse(BaseModel):
    topic: str
    report: str
    iterations: int
    total_tokens: int
    elapsed_seconds: float
    quality_score: int
