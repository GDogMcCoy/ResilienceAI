"""
LLM Providers package for ResilienceAI.

Auto-registers all available providers.
"""

import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_interface import LLMProviderFactory

logger = logging.getLogger(__name__)

# Import and register providers
try:
    from .ollama import OllamaProvider
    LLMProviderFactory.register("ollama", OllamaProvider)
    logger.debug("Registered Ollama provider")
except ImportError as e:
    logger.debug(f"Ollama provider not available: {e}")

try:
    from .lmstudio import LMStudioProvider
    LLMProviderFactory.register("lmstudio", LMStudioProvider)
    logger.debug("Registered LM Studio provider")
except ImportError as e:
    logger.debug(f"LM Studio provider not available: {e}")

try:
    from .huggingface import HuggingFaceProvider
    LLMProviderFactory.register("huggingface", HuggingFaceProvider)
    logger.debug("Registered Hugging Face provider")
except ImportError as e:
    logger.debug(f"Hugging Face provider not available: {e}")

try:
    from .llamacpp import LlamaCppProvider
    LLMProviderFactory.register("llamacpp", LlamaCppProvider)
    logger.debug("Registered llama.cpp provider")
except ImportError as e:
    logger.debug(f"llama.cpp provider not available: {e}")

__all__ = [
    "OllamaProvider",
    "LMStudioProvider", 
    "HuggingFaceProvider",
    "LlamaCppProvider",
]
