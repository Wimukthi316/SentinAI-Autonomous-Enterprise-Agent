"""
Agents API routes for SentinAI.
Handles agent interaction and autonomous workflow processing.
"""

import os
import tempfile
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ...agents.orchestrator import SentinAIOrchestrator


router = APIRouter()

orchestrator: Optional[SentinAIOrchestrator] = None


def get_orchestrator() -> SentinAIOrchestrator:
    """Get or create the orchestrator singleton (lazy initialization)."""
    global orchestrator
    if orchestrator is None:
        orchestrator = SentinAIOrchestrator()
    
    # Initialize only when first needed (not on import)
    if not orchestrator._initialized and not orchestrator._rate_limit_hit:
        init_result = orchestrator.initialize()
        if init_result["status"] == "error":
            # Don't raise exception for rate limit - let the execute method handle it gracefully
            if "quota" in init_result["message"].lower():
                return orchestrator
            raise HTTPException(status_code=500, detail=init_result["message"])
    return orchestrator


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    agent_id: str
    status: str


class ProcessResponse(BaseModel):
    """Response model for process endpoint."""
    status: str
    response: str
    file_processed: Optional[str] = None
    intermediate_steps: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Send a message to the AI agent and get a response.
    """
    try:
        agent = get_orchestrator()
        result = agent.execute(request.message)
        
        if result["status"] == "error":
            return ChatResponse(
                response=result["message"],
                agent_id="sentinai-orchestrator",
                status="error"
            )
        
        return ChatResponse(
            response=result["response"],
            agent_id="sentinai-orchestrator",
            status="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        return ChatResponse(
            response=f"Error processing request: {str(e)}",
            agent_id="sentinai-orchestrator",
            status="error"
        )


@router.get("/status")
async def get_agent_status():
    """Get the current status of the AI agent."""
    global orchestrator
    is_initialized = orchestrator is not None and orchestrator._initialized
    
    return {
        "agent_id": "sentinai-orchestrator",
        "status": "ready" if is_initialized else "not_initialized",
        "capabilities": [
            "audio-transcription",
            "document-analysis",
            "ticket-classification",
            "autonomous-reasoning"
        ],
        "tools": [
            "AudioProcessor (Whisper AI)",
            "DocumentProcessor (LayoutLM)",
            "TicketClassifier (RandomForest)",
            "Gemini 1.5 Pro (LLM)"
        ]
    }


@router.post("/process", response_model=ProcessResponse)
async def process_input(
    file: Optional[UploadFile] = File(None),
    query: str = Form(...)
):
    """
    Process an input with optional file attachment.
    
    The orchestrator will automatically determine the appropriate action:
    - Audio files: Transcription via Whisper
    - Documents (PDF/images): Information extraction via LayoutLM
    - Text queries: Ticket classification or general response
    
    Args:
        file: Optional file upload (audio, PDF, or image)
        query: Text query or question about the file
        
    Returns:
        ProcessResponse with the agent's response
    """
    try:
        agent = get_orchestrator()
        file_path: Optional[str] = None
        temp_file_path: Optional[str] = None

        if file and file.filename:
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            # Use absolute path for data directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            data_dir = os.path.join(backend_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=file_extension,
                dir=data_dir
            ) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
                file_path = temp_file_path

            if file_extension in {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"}:
                input_data = f"Transcribe the audio file at: {file_path}"
            elif file_extension in {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff"}:
                input_data = f"Extract information from the document at {file_path}. Question: {query}"
            else:
                input_data = query
        else:
            input_data = query

        result = agent.execute(input_data)

        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass

        if result["status"] == "error":
            return ProcessResponse(
                status="error",
                response=result["message"],
                file_processed=file.filename if file else None
            )

        return ProcessResponse(
            status="success",
            response=result["response"],
            file_processed=file.filename if file else None,
            intermediate_steps=result.get("intermediate_steps")
        )

    except HTTPException:
        raise
    except Exception as e:
        return ProcessResponse(
            status="error",
            response=f"Processing failed: {str(e)}",
            file_processed=file.filename if file else None
        )


@router.post("/initialize")
async def initialize_orchestrator():
    """
    Explicitly initialize the orchestrator.
    Useful for pre-warming the agent before first request.
    """
    try:
        agent = get_orchestrator()
        return {
            "status": "success",
            "message": "Orchestrator initialized and ready"
        }
    except HTTPException as e:
        return {
            "status": "error",
            "message": str(e.detail)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Initialization failed: {str(e)}"
        }
