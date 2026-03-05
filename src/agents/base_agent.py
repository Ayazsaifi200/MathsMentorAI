# -*- coding: utf-8 -*-
"""
Base Agent for Math Mentor AI
Provides common functionality for all agents with LLM integration
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import different LLM providers
GEMINI_AVAILABLE = False
GROQ_AVAILABLE = False
OLLAMA_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    ollama = None

logger = logging.getLogger(__name__)


@dataclass
class AgentCapability:
    """Define agent capabilities"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    dependencies: List[str]
    confidence_threshold: float


class BaseAgent(ABC):
    """Base class for all AI agents with LLM integration"""
    
    def __init__(self):
        """Initialize base agent with LLM (tries multiple providers)"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.capabilities = self._define_capabilities()
        
        # Initialize LLM (try multiple providers in order of preference)
        self.llm = None
        self.llm_available = False
        self.llm_provider = None
        
        # Try Groq first (fastest and most reliable free option)
        if GROQ_AVAILABLE:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    # Initialize Groq with minimal parameters (fix for httpx proxies issue)
                    self.llm = Groq(api_key=api_key)
                    self.llm_available = True
                    self.llm_provider = "groq"
                    self.logger.info(f"{self.capabilities.name} initialized with Groq (Llama 3.3 70B)")
                    return
                except Exception as e:
                    self.logger.warning(f"Groq initialization failed: {e}")
        
        # Try Ollama (local, unlimited free usage)
        if OLLAMA_AVAILABLE:
            try:
                # Test if Ollama is running
                ollama.list()
                self.llm = ollama
                self.llm_available = True
                self.llm_provider = "ollama"
                self.logger.info(f"{self.capabilities.name} initialized with Ollama (Local)")
                return
            except Exception as e:
                self.logger.warning(f"Ollama not available: {e}")
        
        # Fallback to Gemini
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.llm = genai.GenerativeModel('gemini-2.0-flash-exp')
                    self.llm_available = True
                    self.llm_provider = "gemini"
                    self.logger.info(f"{self.capabilities.name} initialized with Gemini AI")
                    return
                except Exception as e:
                    self.logger.warning(f"Gemini initialization failed: {e}")
        
        self.logger.warning("No LLM provider available - install: pip install groq OR ollama OR google-generativeai")
    
    @abstractmethod
    def _define_capabilities(self) -> AgentCapability:
        """Define the agent's capabilities"""
        pass
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process input using AI and return output
        
        Args:
            input_data: Dictionary containing input data
            **kwargs: Additional optional parameters
            
        Returns:
            Dictionary containing processing results
        """
        pass
    
    def call_llm(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """
        Call the LLM with a prompt (supports multiple providers)
        
        Args:
            prompt: The prompt to send to LLM
            max_retries: Number of retry attempts
            
        Returns:
            LLM response text or None if failed
        """
        if not self.llm_available or not self.llm:
            self.logger.error("LLM not available")
            return None
        
        for attempt in range(max_retries):
            try:
                # Groq API
                if self.llm_provider == "groq":
                    response = self.llm.chat.completions.create(
                        model="llama-3.3-70b-versatile",  # Best free model
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=2048
                    )
                    return response.choices[0].message.content
                
                # Ollama (local)
                elif self.llm_provider == "ollama":
                    response = self.llm.generate(
                        model="llama3.1:8b",  # Fast and good for math
                        prompt=prompt
                    )
                    return response['response']
                
                # Gemini
                elif self.llm_provider == "gemini":
                    response = self.llm.generate_content(prompt)
                    return response.text
                
                else:
                    self.logger.error(f"Unknown provider: {self.llm_provider}")
                    return None
                    
            except Exception as e:
                error_msg = str(e)
                # Check if it's a rate limit error
                if "429" in error_msg or "rate_limit" in error_msg.lower():
                    self.logger.error(f"QUOTA EXCEEDED (attempt {attempt + 1}/{max_retries}): Groq API daily token limit reached. Wait for quota reset or upgrade at https://console.groq.com/settings/billing")
                else:
                    self.logger.error(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
        
        return None
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data format"""
        if not isinstance(input_data, dict):
            self.logger.error("Input must be a dictionary")
            return False
        return True
    
    def create_success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standardized success response"""
        return {
            "success": True,
            "agent": self.capabilities.name,
            **data
        }
    
    def create_error_response(self, error: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a standardized error response"""
        response = {
            "success": False,
            "error": error,
            "agent": self.capabilities.name
        }
        if details:
            response["details"] = details
        return response
