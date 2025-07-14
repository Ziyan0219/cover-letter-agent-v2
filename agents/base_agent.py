"""
Base Agent class for the cover letter generation system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os


class BaseAgent(ABC):
    """Base class for all agents in the cover letter generation system"""
    
    def __init__(self, model_name: str = "gpt-4.1-mini", temperature: float = 0.7):
        """
        Initialize the base agent
        
        Args:
            model_name: The OpenAI model to use
            temperature: Temperature for text generation
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE")
        )
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results"""
        pass
    
    def generate_response(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response using the LLM
        
        Args:
            user_prompt: The user's prompt
            system_prompt: Optional system prompt override
            
        Returns:
            Generated response text
        """
        if system_prompt is None:
            system_prompt = self.get_system_prompt()
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def validate_input(self, input_data: Dict[str, Any], required_keys: list) -> bool:
        """
        Validate that input data contains all required keys
        
        Args:
            input_data: Input data dictionary
            required_keys: List of required keys
            
        Returns:
            True if all required keys are present
        """
        return all(key in input_data for key in required_keys)

