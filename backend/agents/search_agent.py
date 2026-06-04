from backend.core.gemini_client import GeminiClient
from backend.core.models import SupervisorPlan

SYSTEM_PROMPT = """You are the Search Agent in a multi-agent research system.
Given a research topic and search queries, synthesize a comprehensive knowledge base.

Cover:
- Key facts, definitions, and background
- Recent developments and current state
- Expert perspectives and debates
- Statistics, benchmarks, or comparisons where relevant
- Practical use cases and real-world examples

Structure your response with clear sections using markdown headings.
Be thorough and accurate. Target 500-700 words."""


async def run_search(
    plan: SupervisorPlan,
    iteration: int,
    previous_gaps: list[str],
    client: GeminiClient,
) -> dict:
    """
    Perform a research pass. On subsequent iterations, focus on identified gaps.
    Returns {"text": str, "tokens": int}.
    """
    if iteration == 1:
        queries_fmt = "\n".join(f"{i+1}. {q}" for i, q in enumerate(plan.search_queries))
        user_message = (
            f"Topic: {plan.topic}\n\n"
            f"Research angles to cover:\n{queries_fmt}\n\n"
            f"Research strategy: {plan.plan}"
        )
    else:
        gaps_fmt = "\n".join(f"- {g}" for g in previous_gaps) if previous_gaps else "- Improve overall depth"
        user_message = (
            f"Topic: {plan.topic}\n\n"
            f"This is refinement pass #{iteration}. The Critic Agent flagged these gaps:\n"
            f"{gaps_fmt}\n\n"
            f"Please provide a comprehensive response that specifically addresses these gaps "
            f"while maintaining coverage of the core topic."
        )

    return await client.generate(SYSTEM_PROMPT, user_message)
