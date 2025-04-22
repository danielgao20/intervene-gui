"""
config.py - Configuration loading and management
"""
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.2")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:3")

# Server configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8001"))
DEBUG = os.getenv("DEBUG", "True").lower() in ["true", "1", "yes"]

# Logging configuration
LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_ollama_config():
    """Get Ollama configuration as a dictionary"""
    return {
        "base_url": OLLAMA_BASE_URL,
        "llm_model": OLLAMA_LLM_MODEL,
        "vision_model": OLLAMA_VISION_MODEL
    }

def log_config():
    """Log the current configuration"""
    logger = logging.getLogger(__name__)
    logger.info(f"Ollama Base URL: {OLLAMA_BASE_URL}")
    logger.info(f"Ollama LLM Model: {OLLAMA_LLM_MODEL}")
    logger.info(f"Ollama Vision Model: {OLLAMA_VISION_MODEL}")
    logger.info(f"Server: {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"Debug Mode: {DEBUG}")