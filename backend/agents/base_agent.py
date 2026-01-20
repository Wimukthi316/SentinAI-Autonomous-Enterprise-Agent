"""Base agent class for SentinAI."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """Abstract base class for all SentinAI agents."""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.memory: list = []
    
    @abstractmethod
    async def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process input and return a response."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent with necessary resources."""
        pass
    
    def add_to_memory(self, message: str, role: str = "user") -> None:
        """Add a message to the agent's memory."""
        self.memory.append({"role": role, "content": message})
    
    def clear_memory(self) -> None:
        """Clear the agent's memory."""
        self.memory = []
