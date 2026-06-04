import json
from backend.core.gemini_client import GeminiClient
from backend.core.models import SupervisorPlan

SYSTEM_PROMPT = """You are the Supervisor agent in a multi-agent research orchestration system.
Your role is to analyze a research topic and create a structured research plan.

Respond ONLY in this exact JSON format, no markdown fences:
{
  "topic": "cleaned research topic",
  "plan": "2-3 sentence research strategy",
  "search_queries": ["query1", "query2", "query3"],
  "quality_criteria": ["criterion1", "criterion2", "criterion3"],
  "max_iterations": 3
}

Be specific and actionable. Search queries should cover distinct angles on the topic."""


async def run_supervisor(query: str, client: GeminiClient) -> SupervisorPlan:
    """
    Parse the research query into a structured plan.
    Falls back to a safe default if Gemini returns malformed JSON.
    """
    result = await client.generate(SYSTEM_PROMPT, f"Research topic: {query}")
    raw = result["text"].replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(raw)
        return SupervisorPlan(**data)
    except Exception:
        return SupervisorPlan(
            topic=query,
            plan="Direct research with iterative refinement.",
            search_queries=[query, f"{query} analysis", f"{query} impact and future"],
            quality_criteria=["accuracy", "comprehensiveness", "recency"],
            max_iterations=3,
        )
