"""
SentinAIOrchestrator module for SentinAI.
Handles autonomous agent orchestration using LangChain and Google Gemini.
"""

import os
import time
import logging
from typing import Any, Dict, Optional, List
from functools import lru_cache

from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool, StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from google.api_core.exceptions import ResourceExhausted
# Use langchain's pydantic v1 for tool schema compatibility
from langchain_core.pydantic_v1 import BaseModel, Field

logger = logging.getLogger(__name__)

from ..processors.audio_processor import AudioProcessor
from ..processors.document_processor import DocumentProcessor
from ..models.ticket_classifier import TicketClassifier
from ..db.vector_store import VectorStoreManager


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
        self.vector_store: Optional[VectorStoreManager] = None
        self.llm: Optional[ChatGoogleGenerativeAI] = None
        self.agent_executor: Optional[AgentExecutor] = None
        self._initialized = False
        self._last_tool_results: Dict[str, Any] = {}
        # Rate limiting tracking
        self._rate_limit_until: float = 0
        self._request_count: int = 0
        self._last_request_time: float = 0
        self._rate_limit_hit: bool = False

    def _initialize_processors(self) -> None:
        """Initialize all processor components."""
        self.audio_processor = AudioProcessor()
        self.document_processor = DocumentProcessor()
        self.ticket_classifier = TicketClassifier()
        self.vector_store = VectorStoreManager(api_key=self.api_key)
        
        # Initialize vector store
        self.vector_store.initialize()
        
        # Train classifier if needed
        if not hasattr(self.ticket_classifier.pipeline, "classes_"):
            self.ticket_classifier.train_default_model()

    def _create_tools(self) -> list:
        """Create LangChain tools from processors."""
        
        def transcribe_audio(file_path: str) -> str:
            """Transcribe audio file to text using Whisper AI."""
            try:
                result = self.audio_processor.transcribe(file_path)
                self._last_tool_results['transcribe_audio'] = result
                
                if result["status"] == "success":
                    text = result['text']
                    language = result['language']
                    
                    # Save to vector store for memory
                    if self.vector_store:
                        self.vector_store.add_documents(
                            texts=[text],
                            metadatas=[{"source": "audio_transcription", "file": file_path, "language": language}]
                        )
                    
                    return (
                        f"TRANSCRIPTION SUCCESSFUL\n"
                        f"Detected Language: {language}\n"
                        f"Transcribed Text: {text}\n\n"
                        f"The audio has been transcribed and saved to memory."
                    )
                else:
                    return (
                        f"TRANSCRIPTION FAILED\n"
                        f"Error: {result['message']}\n"
                        f"Possible reasons: File not found, unsupported format, or corrupted audio file."
                    )
            except Exception as e:
                return f"TRANSCRIPTION ERROR: {str(e)}"

        def query_document(file_path: str, query: str) -> str:
            """Extract information from PDF or image documents using LayoutLM."""
            try:
                result = self.document_processor.extract_info(file_path, query)
                self._last_tool_results['query_document'] = result
                
                if result["status"] == "success":
                    answer = result['answer']
                    confidence = result['confidence_score']
                    
                    # Save to vector store for memory
                    if self.vector_store:
                        self.vector_store.add_documents(
                            texts=[f"Question: {query}\nAnswer: {answer}"],
                            metadatas=[{"source": "document_qa", "file": file_path, "confidence": confidence}]
                        )
                    
                    return (
                        f"DOCUMENT ANALYSIS SUCCESSFUL\n"
                        f"Question: {query}\n"
                        f"Answer: {answer}\n"
                        f"Confidence Score: {confidence:.2%}\n\n"
                        f"The information has been extracted and saved to memory."
                    )
                else:
                    return (
                        f"DOCUMENT ANALYSIS FAILED\n"
                        f"Error: {result['message']}\n"
                        f"Possible reasons: File not found, unsupported format, or model error."
                    )
            except Exception as e:
                return f"DOCUMENT ANALYSIS ERROR: {str(e)}"

        def classify_ticket(text: str) -> str:
            """Classify support ticket into Billing, Technical, or Account categories."""
            try:
                result = self.ticket_classifier.predict(text)
                self._last_tool_results['classify_ticket'] = result
                
                if result["status"] == "success":
                    category = result['category']
                    probability = result['probability']
                    
                    # Save to vector store for memory
                    if self.vector_store:
                        self.vector_store.add_documents(
                            texts=[text],
                            metadatas=[{"source": "ticket_classification", "category": category, "probability": probability}]
                        )
                    
                    return (
                        f"TICKET CLASSIFICATION SUCCESSFUL\n"
                        f"Ticket Text: {text}\n"
                        f"Category: {category}\n"
                        f"Confidence: {probability:.2%}\n\n"
                        f"This ticket has been categorized and saved to memory."
                    )
                else:
                    return (
                        f"TICKET CLASSIFICATION FAILED\n"
                        f"Error: {result['message']}\n"
                        f"Possible reasons: Model not trained or invalid input text."
                    )
            except Exception as e:
                return f"TICKET CLASSIFICATION ERROR: {str(e)}"

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
        
        # System message for the structured chat agent
        system_message = """You are SentinAI, an autonomous enterprise AI agent with access to specialized processing tools.

Your capabilities:
1. transcribe_audio: Convert speech from audio files to text using Whisper AI
2. query_document: Extract information from PDF or image documents using LayoutLM  
3. classify_ticket: Categorize support tickets into Billing, Technical, or Account categories

IMPORTANT INSTRUCTIONS:
- When a tool returns results, YOU MUST include the actual data in your response to the user
- DO NOT give generic responses like "I processed your request"
- Extract key information from tool outputs and present it clearly
- If a tool returns an error, explain what went wrong and suggest solutions
- For transcriptions: Quote the transcribed text
- For document queries: Provide the extracted answer and confidence score
- For ticket classification: State the category and confidence level

Analyze the user's input and select the appropriate tool:
- Audio file path (.mp3, .wav, .m4a, etc.) → use transcribe_audio
- Document file path (.pdf, .jpg, .png, etc.) with a question → use query_document
- Text that appears to be a customer support request → use classify_ticket

Always provide detailed, informative responses based on the actual tool outputs.

You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
```"""

        human_message = """{input}

{agent_scratchpad}"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", human_message)
        ])

        agent = create_structured_chat_agent(self.llm, tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15,
            max_execution_time=120,
            return_intermediate_steps=True
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
            # Use gemini-2.5-flash-lite - separate quota bucket from gemini-2.5-flash
            # Each model has its own 20 RPD quota on free tier
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",  # Different model = different quota
                google_api_key=self.api_key,
                temperature=0.1,
                convert_system_message_to_human=True,
                max_retries=2,  # Reduce retries to fail faster on quota exceeded
            )

            self._initialize_processors()
            tools = self._create_tools()
            self.agent_executor = self._create_agent(tools)
            self._initialized = True
            self._rate_limit_hit = False  # Reset rate limit flag on successful init

            return {
                "status": "success",
                "message": "SentinAI Orchestrator initialized successfully"
            }
        except ResourceExhausted as e:
            self._rate_limit_hit = True
            self._rate_limit_until = time.time() + 60  # Wait at least 60 seconds
            logger.warning(f"Rate limit hit during initialization: {e}")
            return {
                "status": "error",
                "message": "Gemini API quota exceeded. Free tier limit is 20 requests/day. Please wait or upgrade to a paid plan."
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
                # Try fallback mode if rate limited
                if self._rate_limit_hit:
                    return self._execute_fallback(input_data)
                return init_result

        if not input_data or not input_data.strip():
            return {
                "status": "error",
                "message": "Input data cannot be empty"
            }

        # Check if we're in a rate limit cooldown period - use fallback mode
        if self._rate_limit_hit and time.time() < self._rate_limit_until:
            return self._execute_fallback(input_data)

        try:
            invoke_input = {"input": input_data}
            if chat_history:
                invoke_input["chat_history"] = chat_history

            result = self.agent_executor.invoke(invoke_input)
            
            # Reset rate limit flag on successful execution
            self._rate_limit_hit = False

            return {
                "status": "success",
                "response": result.get("output", "No response generated"),
                "intermediate_steps": str(result.get("intermediate_steps", []))
            }
        except ResourceExhausted as e:
            self._rate_limit_hit = True
            self._rate_limit_until = time.time() + 60
            logger.warning(f"Rate limit hit: {e}")
            return self._execute_fallback(input_data)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                self._rate_limit_hit = True
                self._rate_limit_until = time.time() + 60
                return self._execute_fallback(input_data)
            return {
                "status": "error",
                "message": f"Execution failed: {error_msg}"
            }

    def _execute_fallback(self, input_data: str) -> Dict[str, Any]:
        """
        Execute in fallback mode without LLM when rate limited.
        Uses simple pattern matching to route to appropriate tools.
        """
        input_lower = input_data.lower()
        
        # Initialize processors if not already done
        if self.audio_processor is None:
            try:
                self._initialize_processors()
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"⚠️ Gemini API quota exceeded & fallback initialization failed: {str(e)}"
                }
        
        # Pattern-based routing for audio files
        audio_extensions = ('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm')
        if any(ext in input_lower for ext in audio_extensions):
            # Extract file path from input
            import re
            path_match = re.search(r'[a-zA-Z]:[\\\/][^\s]+|\/[^\s]+', input_data)
            if path_match:
                file_path = path_match.group()
                try:
                    result = self.audio_processor.transcribe(file_path)
                    if result["status"] == "success":
                        return {
                            "status": "success",
                            "response": f"🎤 **Audio Transcription (Fallback Mode)**\n\n**Language:** {result['language']}\n\n**Transcription:**\n{result['text']}\n\n_Note: Running in fallback mode due to API quota limits._",
                            "intermediate_steps": "[('transcribe_audio', 'fallback')]"
                        }
                    return {"status": "error", "message": result['message']}
                except Exception as e:
                    return {"status": "error", "message": f"Transcription failed: {str(e)}"}
        
        # Pattern-based routing for documents
        doc_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        if any(ext in input_lower for ext in doc_extensions):
            import re
            path_match = re.search(r'[a-zA-Z]:[\\\/][^\s]+|\/[^\s]+', input_data)
            if path_match:
                file_path = path_match.group()
                # Extract question after common patterns
                question_patterns = [r'question:\s*(.+)', r'query:\s*(.+)', r'\?\s*(.+)']
                query = "Extract all text from this document"
                for pattern in question_patterns:
                    match = re.search(pattern, input_data, re.IGNORECASE)
                    if match:
                        query = match.group(1)
                        break
                try:
                    result = self.document_processor.extract_info(file_path, query)
                    if result["status"] == "success":
                        return {
                            "status": "success", 
                            "response": f"📄 **Document Analysis (Fallback Mode)**\n\n**Question:** {query}\n\n**Answer:** {result['answer']}\n\n**Confidence:** {result['confidence_score']:.2%}\n\n_Note: Running in fallback mode due to API quota limits._",
                            "intermediate_steps": "[('query_document', 'fallback')]"
                        }
                    return {"status": "error", "message": result['message']}
                except Exception as e:
                    return {"status": "error", "message": f"Document processing failed: {str(e)}"}
        
        # Pattern-based routing for ticket classification
        ticket_keywords = ['issue', 'problem', 'help', 'support', 'ticket', 'billing', 'account', 'technical', 'error', 'not working', 'broken', 'charge', 'payment', 'refund', 'password', 'login']
        if any(keyword in input_lower for keyword in ticket_keywords):
            try:
                result = self.ticket_classifier.predict(input_data)
                if result["status"] == "success":
                    return {
                        "status": "success",
                        "response": f"🏷️ **Ticket Classification (Fallback Mode)**\n\n**Text:** {input_data}\n\n**Category:** {result['category']}\n\n**Confidence:** {result['probability']:.2%}\n\n_Note: Running in fallback mode due to API quota limits._",
                        "intermediate_steps": "[('classify_ticket', 'fallback')]"
                    }
                return {"status": "error", "message": result['message']}
            except Exception as e:
                return {"status": "error", "message": f"Classification failed: {str(e)}"}
        
        # Default fallback response
        return {
            "status": "error",
            "message": "⚠️ **Gemini API quota exceeded** (20 requests/day on free tier)\n\n**Your options:**\n1. Wait until tomorrow for quota reset\n2. Upgrade at https://ai.google.dev/pricing\n3. Use a different API key\n\n**Available in fallback mode:**\n- Audio transcription (include file path)\n- Document analysis (include file path)\n- Ticket classification (describe your issue)"
        }
