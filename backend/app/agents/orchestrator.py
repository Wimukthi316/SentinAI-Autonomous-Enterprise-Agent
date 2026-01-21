"""
SentinAIOrchestrator module for SentinAI.
Handles autonomous agent orchestration using LangChain and Google Gemini.
"""

import os
from typing import Any, Dict, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool, StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from ..processors.audio_processor import AudioProcessor
from ..processors.document_processor import DocumentProcessor
from ..models.ticket_classifier import TicketClassifier


class AudioTranscribeInput(BaseModel):
    """Input schema for audio transcription tool."""
    file_path: str = Field(description="Path to the audio file to transcribe")


class DocumentQueryInput(BaseModel):
    """Input schema for document query tool."""
    file_path: str = Field(description="Path to the document file (PDF or image)")
    query: str = Field(description="Question to ask about the document")


class TicketClassifyInput(BaseModel):
    """Input schema for ticket classification tool."""
    text: str = Field(description="Support ticket text to classify")


class SentinAIOrchestrator:
    """
    Production-ready agent orchestrator for SentinAI.
    Coordinates AudioProcessor, DocumentProcessor, and TicketClassifier
    using LangChain and Google Gemini for intelligent task routing.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SentinAIOrchestrator.
        
        Args:
            api_key: Google API key. If None, uses GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.audio_processor: Optional[AudioProcessor] = None
        self.document_processor: Optional[DocumentProcessor] = None
        self.ticket_classifier: Optional[TicketClassifier] = None
        self.llm: Optional[ChatGoogleGenerativeAI] = None
        self.agent_executor: Optional[AgentExecutor] = None
        self._initialized = False

    def _initialize_processors(self) -> None:
        """Initialize all processor components."""
        self.audio_processor = AudioProcessor()
        self.document_processor = DocumentProcessor()
        self.ticket_classifier = TicketClassifier()
        
        if not hasattr(self.ticket_classifier.pipeline, "classes_"):
            self.ticket_classifier.train_default_model()

    def _create_tools(self) -> list:
        """Create LangChain tools from processors."""
        
        def transcribe_audio(file_path: str) -> str:
            result = self.audio_processor.transcribe(file_path)
            if result["status"] == "success":
                return f"Transcription: {result['text']} (Language: {result['language']})"
            return f"Error: {result['message']}"

        def query_document(file_path: str, query: str) -> str:
            result = self.document_processor.extract_info(file_path, query)
            if result["status"] == "success":
                return f"Answer: {result['answer']} (Confidence: {result['confidence_score']:.2%})"
            return f"Error: {result['message']}"

        def classify_ticket(text: str) -> str:
            result = self.ticket_classifier.predict(text)
            if result["status"] == "success":
                return f"Category: {result['category']} (Probability: {result['probability']:.2%})"
            return f"Error: {result['message']}"

        tools = [
            StructuredTool.from_function(
                func=transcribe_audio,
                name="transcribe_audio",
                description="Transcribe speech from an audio file to text using Whisper AI. "
                           "Use this when given an audio file path (.mp3, .wav, .m4a, etc.).",
                args_schema=AudioTranscribeInput
            ),
            StructuredTool.from_function(
                func=query_document,
                name="query_document",
                description="Extract information from a document (PDF or image) by asking questions. "
                           "Use this when given a document file path and a question about its contents.",
                args_schema=DocumentQueryInput
            ),
            StructuredTool.from_function(
                func=classify_ticket,
                name="classify_ticket",
                description="Classify a support ticket into categories: Billing, Technical, or Account. "
                           "Use this when given text that appears to be a customer support request.",
                args_schema=TicketClassifyInput
            )
        ]

        return tools

    def _create_agent(self, tools: list) -> AgentExecutor:
        """Create the LangChain agent with tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are SentinAI, an autonomous AI assistant with access to specialized tools.
            
Your capabilities:
1. transcribe_audio: Convert speech in audio files to text
2. query_document: Extract information from PDFs and images
3. classify_ticket: Categorize support tickets

Analyze the user's input and determine the appropriate tool to use:
- If given an audio file path, use transcribe_audio
- If given a document file path with a question, use query_document
- If given text that looks like a support request, use classify_ticket
- If the input is ambiguous, ask for clarification

Always provide clear, helpful responses based on the tool outputs."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_tool_calling_agent(self.llm, tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    def initialize(self) -> Dict[str, str]:
        """
        Initialize all components of the orchestrator.
        
        Returns:
            Dictionary with status and message.
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "Google API key not provided. Set GOOGLE_API_KEY environment variable."
            }

        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=self.api_key,
                temperature=0.1,
                convert_system_message_to_human=True
            )

            self._initialize_processors()
            tools = self._create_tools()
            self.agent_executor = self._create_agent(tools)
            self._initialized = True

            return {
                "status": "success",
                "message": "SentinAI Orchestrator initialized successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize orchestrator: {str(e)}"
            }

    def execute(self, input_data: str, chat_history: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute the autonomous workflow based on input data.
        
        Args:
            input_data: User input (text query, file path, or support ticket).
            chat_history: Optional conversation history for context.
            
        Returns:
            Dictionary containing:
                - status: 'success' or 'error'
                - response: Agent response (on success)
                - message: Error message (on error)
        """
        if not self._initialized:
            init_result = self.initialize()
            if init_result["status"] == "error":
                return init_result

        if not input_data or not input_data.strip():
            return {
                "status": "error",
                "message": "Input data cannot be empty"
            }

        try:
            invoke_input = {"input": input_data}
            if chat_history:
                invoke_input["chat_history"] = chat_history

            result = self.agent_executor.invoke(invoke_input)

            return {
                "status": "success",
                "response": result.get("output", "No response generated"),
                "intermediate_steps": str(result.get("intermediate_steps", []))
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Execution failed: {str(e)}"
            }
