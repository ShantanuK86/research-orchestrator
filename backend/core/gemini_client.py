import httpx
from backend.core.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_MAX_TOKENS,
    GEMINI_TEMPERATURE,
)


class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key

    async def generate(self, system_prompt: str, user_message: str) -> dict:
        """
        Call Gemini and return {"text": str, "tokens": int}.
        Raises httpx.HTTPStatusError on API errors.
        """
        url = f"{self.BASE_URL}/{GEMINI_MODEL}:generateContent?key={self.api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_message}]}],
            "generationConfig": {
                "maxOutputTokens": GEMINI_MAX_TOKENS,
                "temperature": GEMINI_TEMPERATURE,
            },
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        tokens = data.get("usageMetadata", {}).get("candidatesTokenCount", len(text) // 4)
        return {"text": text, "tokens": tokens}
