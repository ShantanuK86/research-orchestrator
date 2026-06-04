from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.api.routes import router
from backend.core.config import CORS_ORIGINS

app = FastAPI(
    title="Research Orchestrator",
    description="Multi-agent research system powered by Gemini 2.0 Flash",
    version="1.0.0",
)

# CORS — allow frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router)

# Serve frontend static files (production)
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.isdir(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))
