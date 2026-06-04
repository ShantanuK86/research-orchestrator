from backend.core.gemini_client import GeminiClient
from backend.core.models import SupervisorPlan

SYSTEM_PROMPT = """You are the Writer Agent in a multi-agent research system.
Synthesize the provided research findings into a polished, professional report.

Format your response in clean Markdown:

## [Compelling Title]

### Executive Summary
(2-3 sentence overview)

### Key Findings
(Bullet points with specific data and facts)

### Analysis
(Deep-dive with context, trends, implications)

### Conclusion
(Forward-looking summary with takeaways)

Guidelines:
- Use **bold** for important terms and statistics
- Use > blockquotes for key insights or quotes
- Use `code` for technical terms
- Be authoritative, specific, and evidence-based
- Target 600-800 words
- Do NOT include phrases like "Based on the research provided" — write as an expert"""


async def run_writer(
    plan: SupervisorPlan,
    research_content: str,
    iterations_taken: int,
    client: GeminiClient,
) -> dict:
    """
    Produce the final structured research report.
    Returns {"text": str, "tokens": int}.
    """
    user_message = (
        f"Topic: {plan.topic}\n\n"
        f"Research data (refined over {iterations_taken} iteration(s)):\n\n"
        f"{research_content}\n\n"
        f"Write a comprehensive, professional research report on this topic."
    )
    return await client.generate(SYSTEM_PROMPT, user_message)
