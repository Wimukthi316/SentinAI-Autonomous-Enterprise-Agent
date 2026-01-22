"""
SentinAI - Main FastAPI Application
An autonomous AI agent powered by LangChain, Google Gemini API, and Whisper AI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app.api.routes import agents
from api.routes import health

app = FastAPI(
    title="SentinAI API",
    description="Autonomous AI Agent Backend API",
    version="1.0.0",
)

# CORS configuration for local frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "SentinAI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    # Change to the backend directory for proper module resolution
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
