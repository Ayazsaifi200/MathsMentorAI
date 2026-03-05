# -*- coding: utf-8 -*-
"""
Configuration module for Math Mentor AI
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any
import logging

# Load environment variables
load_dotenv()

# Streamlit Cloud injects secrets as env vars, but also try st.secrets as fallback
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        for key in st.secrets:
            if key not in os.environ:
                os.environ[key] = str(st.secrets[key])
except Exception:
    pass

class Config:
    """Configuration class for Math Mentor AI application"""
    
    # LLM Provider Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # groq, ollama, gemini
    
    # Groq Configuration (Primary LLM)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Ollama Configuration (Local fallback)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Google Gemini Configuration (Legacy - optional)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-pro")
    
    # LangSmith Configuration
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "math-mentor-ai")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/math_mentor.db")
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    AUDIO_CHUNK_SIZE = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))
    
    # OCR Configuration
    # Auto-detect Tesseract installation (Scoop or system PATH)
    _tesseract_scoop = os.path.join(os.path.expanduser("~"), "scoop", "apps", "tesseract", "current", "tesseract.exe")
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", 
                                _tesseract_scoop if os.path.exists(_tesseract_scoop) else "tesseract")
    
    # Set TESSDATA_PREFIX environment variable for Tesseract
    # TESSDATA_PREFIX should point to the tessdata folder itself
    _tessdata_folder = os.path.join(os.path.expanduser("~"), "scoop", "apps", "tesseract", "current", "tessdata")
    
    # Use environment variable if set, otherwise auto-detect
    TESSDATA_PREFIX = os.getenv("TESSDATA_PREFIX")
    if not TESSDATA_PREFIX and os.path.exists(_tessdata_folder):
        TESSDATA_PREFIX = _tessdata_folder
    
    # Set environment variable for Tesseract to find
    if TESSDATA_PREFIX and os.path.exists(TESSDATA_PREFIX):
        os.environ["TESSDATA_PREFIX"] = TESSDATA_PREFIX
    
    OCR_CONFIDENCE_THRESHOLD = int(os.getenv("OCR_CONFIDENCE_THRESHOLD", "60"))
    
    # Groq Vision Configuration (for image-to-text extraction)
    GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "llama-3.2-90b-vision-preview")
    USE_GROQ_VISION = os.getenv("USE_GROQ_VISION", "true").lower() == "true"
    GROQ_VISION_MAX_TOKENS = int(os.getenv("GROQ_VISION_MAX_TOKENS", "1024"))
    
    # RAG Configuration
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
    
    # Agent Configuration
    MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    
    # HITL Configuration
    HITL_CONFIDENCE_THRESHOLD = float(os.getenv("HITL_CONFIDENCE_THRESHOLD", "0.6"))
    ENABLE_AUTO_APPROVAL = os.getenv("ENABLE_AUTO_APPROVAL", "false").lower() == "true"
    
    # Web Search Configuration
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX", "")
    
    # Development Configuration
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Paths
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    KNOWLEDGE_BASE_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")
    LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        directories = [cls.DATA_DIR, cls.KNOWLEDGE_BASE_DIR, cls.LOGS_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_database_path(cls):
        """Get the full path to the database file"""
        cls.ensure_directories()
        if cls.DATABASE_URL.startswith("sqlite:///"):
            db_path = cls.DATABASE_URL.replace("sqlite:///", "")
            if not os.path.isabs(db_path):
                db_path = os.path.join(cls.PROJECT_ROOT, db_path)
            return db_path
        return cls.DATABASE_URL
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check LLM provider configuration
        if cls.LLM_PROVIDER == "groq":
            if not cls.GROQ_API_KEY:
                validation_results["errors"].append("GROQ_API_KEY is required when using Groq provider")
                validation_results["valid"] = False
        elif cls.LLM_PROVIDER == "gemini":
            if not cls.GOOGLE_API_KEY:
                validation_results["errors"].append("GOOGLE_API_KEY is required when using Gemini provider")
                validation_results["valid"] = False
        elif cls.LLM_PROVIDER == "ollama":
            validation_results["warnings"].append("Using Ollama - ensure Ollama is running locally")
        else:
            validation_results["warnings"].append(f"Unknown LLM provider: {cls.LLM_PROVIDER}")
        
        # Check optional configurations
        if not cls.LANGCHAIN_API_KEY and cls.LANGCHAIN_TRACING_V2:
            validation_results["warnings"].append("LangChain tracing enabled but no API key provided")
        
        if not cls.GOOGLE_SEARCH_API_KEY:
            validation_results["warnings"].append("Google Search API key not configured - web search will be disabled")
        
        # LLM provider fallback warnings
        if cls.LLM_PROVIDER == "groq" and not cls.OLLAMA_BASE_URL:
            validation_results["warnings"].append("No fallback LLM configured - consider setting up Ollama")
        
        return validation_results

# Global configuration instance
config = Config()

# Ensure directories exist on import
config.ensure_directories()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'math_mentor.log'), encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Validate configuration on import
validation = config.validate_config()
if not validation["valid"]:
    logger.error("Configuration validation failed:")
    for error in validation["errors"]:
        logger.error(f"  - {error}")

if validation["warnings"]:
    logger.warning("Configuration warnings:")
    for warning in validation["warnings"]:
        logger.warning(f"  - {warning}")

logger.info(f"Math Mentor AI configuration loaded successfully - LLM Provider: {config.LLM_PROVIDER.upper()}")
if config.LLM_PROVIDER == "groq" and config.GROQ_API_KEY:
    logger.info("Groq API configured and ready")
elif config.LLM_PROVIDER == "ollama":
    logger.info(f"Ollama configured at {config.OLLAMA_BASE_URL}")
elif config.LLM_PROVIDER == "gemini" and config.GOOGLE_API_KEY:
    logger.info("Google Gemini API configured and ready")