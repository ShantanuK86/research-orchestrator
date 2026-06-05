from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.api.routes import router

app = FastAPI(
    title="Research Orchestrator",
    description="Multi-agent research system powered by Gemini 2.0 Flash",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes first (before any static mounts)
app.include_router(router)

# Frontend paths
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")

# Serve index.html at root
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Mount css/ and js/ so browser requests for /css/style.css and /js/main.js resolve
app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
app.mount("/js",  StaticFiles(directory=os.path.join(frontend_path, "js")),  name="js")