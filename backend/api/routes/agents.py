"""Agent-related API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class AgentRequest(BaseModel):
    """Request model for agent interactions."""
    message: str
    context: Optional[str] = None


class AgentResponse(BaseModel):
    """Response model for agent interactions."""
    response: str
    agent_id: str
    status: str


@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentRequest):
    """
    Send a message to the AI agent and get a response.
    This endpoint will be connected to LangChain and Gemini API.
    """
    # TODO: Integrate with LangChain and Gemini API
    return AgentResponse(
        response=f"Received: {request.message}",
        agent_id="sentinai-001",
        status="success"
    )


@router.get("/status")
async def get_agent_status():
    """Get the current status of the AI agent."""
    return {
        "agent_id": "sentinai-001",
        "status": "ready",
        "capabilities": ["chat", "voice-transcription", "task-automation"]
    }
