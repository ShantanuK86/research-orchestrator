import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "1500"))
GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))

MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))
QUALITY_THRESHOLD: int = int(os.getenv("QUALITY_THRESHOLD", "7"))

CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:5500"
).split(",")
