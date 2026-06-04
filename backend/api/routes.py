import json
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.core.models import ResearchRequest, ResearchResponse, AgentEvent
from backend.core.gemini_client import GeminiClient
from backend.core.config import MAX_ITERATIONS
from backend.agents.supervisor import run_supervisor
from backend.agents.search_agent import run_search
from backend.agents.critic import run_critic
from backend.agents.writer import run_writer

router = APIRouter(prefix="/api/v1", tags=["orchestration"])


def sse(event: AgentEvent) -> str:
    """Format an AgentEvent as a Server-Sent Events data line."""
    return f"data: {json.dumps(event.model_dump())}\n\n"


async def orchestrate_stream(req: ResearchRequest):
    """
    Core orchestration generator — yields SSE strings.
    Pipeline: Supervisor → [Search → Critic] × N → Writer
    """
    api_key = req.api_key
    client = GeminiClient(api_key=api_key)
    start = time.time()
    total_tokens = 0

    # ── SUPERVISOR ────────────────────────────────────────
    yield sse(AgentEvent(agent="supervisor", type="status", message="active"))
    yield sse(AgentEvent(agent="supervisor", type="log",
                         message=f'Received query: "{req.query}"'))
    yield sse(AgentEvent(agent="supervisor", type="log",
                         message="Generating research plan...", thinking=True))

    try:
        plan = await run_supervisor(req.query, client)
    except Exception as e:
        yield sse(AgentEvent(agent="system", type="log", message=f"Supervisor error: {e}"))
        return

    yield sse(AgentEvent(agent="supervisor", type="log",
                         message=f"Plan ready. {len(plan.search_queries)} search angles identified."))
    yield sse(AgentEvent(agent="supervisor", type="log",
                         message=f"Quality criteria: {', '.join(plan.quality_criteria)}"))
    yield sse(AgentEvent(agent="supervisor", type="status", message="done",
                         data={"label": "plan ready"}))

    # ── RESEARCH LOOP ─────────────────────────────────────
    research_content = ""
    approved = False
    iteration = 0
    max_iter = min(req.max_iterations or plan.max_iterations, MAX_ITERATIONS)
    final_score = 0
    gaps: list[str] = []

    while not approved and iteration < max_iter:
        iteration += 1
        yield sse(AgentEvent(agent="system", type="metric",
                             message="", data={"iteration": iteration}))

        # Dispatch to Search
        yield sse(AgentEvent(agent="supervisor", type="status", message="active"))
        yield sse(AgentEvent(agent="supervisor", type="log",
                             message=f"Dispatching Search Agent — pass {iteration}/{max_iter}"))
        yield sse(AgentEvent(agent="supervisor", type="status", message="done"))

        yield sse(AgentEvent(agent="search", type="status", message="active"))
        yield sse(AgentEvent(agent="search", type="log",
                             message=f"Starting research pass {iteration}...", thinking=True))
        yield sse(AgentEvent(agent="search", type="log",
                             message=f"Angles: {' · '.join(plan.search_queries[:2])}"))

        try:
            search_result = await run_search(plan, iteration, gaps, client)
        except Exception as e:
            yield sse(AgentEvent(agent="system", type="log", message=f"Search error: {e}"))
            break

        research_content = search_result["text"]
        total_tokens += search_result["tokens"]
        word_count = len(research_content.split())
        yield sse(AgentEvent(agent="search", type="log",
                             message=f"Pass {iteration} complete — {word_count} words gathered."))
        yield sse(AgentEvent(agent="search", type="status", message="done",
                             data={"label": f"iter {iteration}"}))
        yield sse(AgentEvent(agent="system", type="metric",
                             message="", data={"tokens": total_tokens}))

        # Route to Critic
        yield sse(AgentEvent(agent="supervisor", type="status", message="active"))
        yield sse(AgentEvent(agent="supervisor", type="log",
                             message="Routing to Critic Agent for quality evaluation..."))
        yield sse(AgentEvent(agent="supervisor", type="status", message="done"))

        yield sse(AgentEvent(agent="critic", type="status", message="active"))
        yield sse(AgentEvent(agent="critic", type="log",
                             message="Evaluating research quality...", thinking=True))
        yield sse(AgentEvent(agent="critic", type="log",
                             message=f"Criteria: {', '.join(plan.quality_criteria)}"))

        try:
            critique = await run_critic(plan, research_content, client)
        except Exception as e:
            yield sse(AgentEvent(agent="system", type="log", message=f"Critic error: {e}"))
            approved = True
            break

        total_tokens += 100  # critic response tokens (estimate)
        final_score = critique.quality_score
        gaps = critique.gaps

        yield sse(AgentEvent(agent="critic", type="log",
                             message=f"Score: {critique.quality_score}/10 — {'✓ Approved' if critique.approve else '✗ Needs improvement'}",
                             data={"score": critique.quality_score, "approve": critique.approve}))
        if critique.critique:
            yield sse(AgentEvent(agent="critic", type="log", message=critique.critique))
        if not critique.approve and gaps:
            yield sse(AgentEvent(agent="critic", type="log",
                                 message=f"Gaps: {'; '.join(gaps)}"))

        yield sse(AgentEvent(agent="critic", type="status", message="done",
                             data={"label": f"score: {critique.quality_score}/10"}))
        yield sse(AgentEvent(agent="system", type="metric",
                             message="", data={"tokens": total_tokens}))

        approved = critique.approve
        if not approved and iteration < max_iter:
            yield sse(AgentEvent(agent="supervisor", type="status", message="active"))
            yield sse(AgentEvent(agent="supervisor", type="log",
                                 message=f"Quality below threshold. Initiating pass {iteration + 1}..."))
            yield sse(AgentEvent(agent="supervisor", type="status", message="done"))

    # ── WRITER ────────────────────────────────────────────
    yield sse(AgentEvent(agent="supervisor", type="status", message="active"))
    yield sse(AgentEvent(agent="supervisor", type="log",
                         message=f"Research approved after {iteration} iteration(s). Dispatching Writer..."))
    yield sse(AgentEvent(agent="supervisor", type="status", message="done"))

    yield sse(AgentEvent(agent="writer", type="status", message="active"))
    yield sse(AgentEvent(agent="writer", type="log",
                         message="Synthesizing final report...", thinking=True))
    yield sse(AgentEvent(agent="writer", type="log",
                         message="Structure: Executive Summary → Key Findings → Analysis → Conclusion"))

    try:
        writer_result = await run_writer(plan, research_content, iteration, client)
    except Exception as e:
        yield sse(AgentEvent(agent="system", type="log", message=f"Writer error: {e}"))
        return

    report = writer_result["text"]
    total_tokens += writer_result["tokens"]
    elapsed = round(time.time() - start, 1)

    yield sse(AgentEvent(agent="writer", type="log",
                         message=f"Report complete — {len(report.split())} words."))
    yield sse(AgentEvent(agent="writer", type="status", message="done",
                         data={"label": "report ready"}))

    # Final metrics
    yield sse(AgentEvent(agent="supervisor", type="status", message="active"))
    yield sse(AgentEvent(agent="supervisor", type="log",
                         message=f"✓ Complete — {iteration} iteration(s) · {total_tokens} tokens · {elapsed}s"))
    yield sse(AgentEvent(agent="supervisor", type="status", message="done",
                         data={"label": "complete"}))
    yield sse(AgentEvent(agent="system", type="metric",
                         message="", data={"tokens": total_tokens, "elapsed": elapsed}))

    # Emit final report
    yield sse(AgentEvent(
        agent="writer",
        type="result",
        message="",
        data={
            "topic": plan.topic,
            "report": report,
            "iterations": iteration,
            "total_tokens": total_tokens,
            "elapsed_seconds": elapsed,
            "quality_score": final_score,
        }
    ))

    yield "data: [DONE]\n\n"


@router.post("/research/stream")
async def research_stream(req: ResearchRequest):
    """SSE endpoint — streams agent events in real time."""
    if not req.api_key:
        from backend.core.config import GEMINI_API_KEY
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=400, detail="Gemini API key required.")
        req.api_key = GEMINI_API_KEY

    return StreamingResponse(
        orchestrate_stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "research-orchestrator"}
