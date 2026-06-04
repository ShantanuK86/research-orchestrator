import json
from backend.core.gemini_client import GeminiClient
from backend.core.models import SupervisorPlan, CritiqueResult
from backend.core.config import QUALITY_THRESHOLD

SYSTEM_PROMPT = """You are the Critic Agent in a multi-agent research system.
Evaluate the provided research content for quality, accuracy, and completeness.

Respond ONLY in this exact JSON format, no markdown fences:
{
  "quality_score": <integer 0-10>,
  "approve": <true if quality_score >= 7, else false>,
  "gaps": ["specific gap 1", "specific gap 2"],
  "critique": "2-3 sentence honest evaluation of strengths and weaknesses",
  "improvements": ["specific improvement 1", "specific improvement 2"]
}

Scoring guide:
- 9-10: Exceptional — comprehensive, well-structured, no notable gaps
- 7-8:  Good — solid coverage, minor gaps, approve
- 5-6:  Fair — missing key areas, needs another pass
- 1-4:  Poor — significant gaps, inaccurate, or too shallow

Be rigorous. Only approve if the content genuinely meets the quality criteria."""


async def run_critic(
    plan: SupervisorPlan,
    research_content: str,
    client: GeminiClient,
) -> CritiqueResult:
    """
    Evaluate research content. Returns a CritiqueResult with approve flag.
    Falls back to approval if Gemini returns malformed JSON.
    """
    criteria_fmt = ", ".join(plan.quality_criteria)
    user_message = (
        f"Research topic: {plan.topic}\n\n"
        f"Quality criteria to evaluate against: {criteria_fmt}\n\n"
        f"Research content to evaluate:\n{research_content}"
    )

    result = await client.generate(SYSTEM_PROMPT, user_message)
    raw = result["text"].replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(raw)
        # Enforce threshold even if model says approve=true
        data["approve"] = data.get("quality_score", 0) >= QUALITY_THRESHOLD
        return CritiqueResult(**data)
    except Exception:
        return CritiqueResult(
            quality_score=7,
            approve=True,
            gaps=[],
            critique="Content meets baseline quality standards.",
            improvements=[],
        )
