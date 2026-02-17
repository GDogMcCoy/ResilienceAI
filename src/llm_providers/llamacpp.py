"""
llama.cpp Provider for ResilienceAI

Uses llama-cpp-python for GGUF model inference.
Optimized for edge deployment.
"""

import logging
import os
from typing import AsyncIterator, Dict, List, Optional, Union, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..llm_interface import BaseLLMProvider, LLMConfig, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class LlamaCppProvider(BaseLLMProvider):
    """llama.cpp LLM provider implementation for GGUF models."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.llm = None
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._n_ctx = config.context_window
        self._n_gpu_layers = -1  # Auto-detect GPU layers
    
    @property
    def name(self) -> str:
        return "llamacpp"
    
    async def initialize(self) -> bool:
        """Initialize the llama.cpp model."""
        try:
            from llama_cpp import Llama
            
            model_path = self.config.model
            
            # Check if model path exists
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                # Try to find in common locations
                alt_paths = [
                    f"models/{model_path}",
                    f"models/{model_path}.gguf",
                    f"~/.models/{model_path}",
                    f"~/.models/{model_path}.gguf",
                ]
                for alt in alt_paths:
                    expanded = os.path.expanduser(alt)
                    if os.path.exists(expanded):
                        model_path = expanded
                        logger.info(f"Found model at: {model_path}")
                        break
                else:
                    logger.error(f"Could not find model file: {model_path}")
                    return False
            
            logger.info(f"Loading llama.cpp model: {model_path}")
            
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _load():
                return Llama(
                    model_path=model_path,
                    n_ctx=self._n_ctx,
                    n_gpu_layers=self._n_gpu_layers,
                    verbose=False
                )
            
            self.llm = await loop.run_in_executor(self._executor, _load)
            
            self._initialized = True
            logger.info(f"Successfully loaded model with context: {self._n_ctx}")
            return True
            
        except ImportError as e:
            logger.error(f"llama-cpp-python not installed: {e}")
            logger.error("Install with: pip install llama-cpp-python")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize llama.cpp provider: {e}")
            return False
    
    async def is_available(self) -> bool:
        """Check if model is loaded."""
        return self._initialized and self.llm is not None
    
    async def generate(
        self, 
        messages: List[LLMMessage], 
        stream: bool = False
    ) -> Union[LLMResponse, AsyncIterator[str]]:
        """Generate response using llama.cpp."""
        if not self._initialized or not self.llm:
            raise RuntimeError("Provider not initialized")
        
        # Format messages into a chat prompt
        prompt = self._format_chat_prompt(messages)
        
        if stream:
            return self._stream_generate(prompt)
        
        # Generate in thread pool
        loop = asyncio.get_event_loop()
        
        def _generate():
            output = self.llm(
                prompt,
                max_tokens=self.config.max_tokens or 512,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                stop=["User:", "System:", "<|im_end|>", "</s>"],
                echo=False
            )
            return output
        
        result = await loop.run_in_executor(self._executor, _generate)
        
        generated_text = result.get("choices", [{}])[0].get("text", "")
        usage = result.get("usage", {})
        
        return LLMResponse(
            content=generated_text.strip(),
            model=os.path.basename(self.config.model),
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            },
            finish_reason="stop",
            metadata={
                "context_window": self._n_ctx,
                "model_path": self.config.model
            }
        )
    
    async def _stream_generate(self, prompt: str) -> AsyncIterator[str]:
        """Stream generate response."""
        loop = asyncio.get_event_loop()
        
        def _generate():
            return self.llm(
                prompt,
                max_tokens=self.config.max_tokens or 512,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                stop=["User:", "System:", "<|im_end|>", "</s>"],
                echo=False,
                stream=True
            )
        
        stream = await loop.run_in_executor(self._executor, _generate)
        
        for chunk in stream:
            text = chunk.get("choices", [{}])[0].get("text", "")
            if text:
                yield text
            
            # Check for completion
            if chunk.get("choices", [{}])[0].get("finish_reason"):
                break
            
            # Small yield to allow other tasks
            await asyncio.sleep(0)
    
    def _format_chat_prompt(self, messages: List[LLMMessage]) -> str:
        """Format messages into a chat prompt using ChatML format."""
        formatted = []
        
        for msg in messages:
            if msg.role == "system":
                formatted.append(f"<|im_start|>system\n{msg.content}<|im_end|>")
            elif msg.role == "user":
                formatted.append(f"<|im_start|>user\n{msg.content}<|im_end|>")
            elif msg.role == "assistant":
                formatted.append(f"<|im_start|>assistant\n{msg.content}<|im_end|>")
        
        formatted.append("<|im_start|>assistant\n")
        return "\n".join(formatted)
    
    async def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        status = {
            "provider": self.name,
            "initialized": self._initialized,
            "available": await self.is_available(),
            "model": os.path.basename(self.config.model) if self.config.model else None,
            "context_window": self._n_ctx,
            "model_path": self.config.model
        }
        
        if self.llm:
            try:
                status["vocab_size"] = self.llm.n_vocab()
                status["context_size"] = self.llm.n_ctx()
            except Exception:
                pass
        
        return status
    
    async def close(self):
        """Clean up resources."""
        if self.llm:
            # llama-cpp doesn't have explicit cleanup, just delete reference
            del self.llm
            self.llm = None
        
        self._executor.shutdown(wait=True)
        await super().close()
    
    def set_gpu_layers(self, n_layers: int):
        """Set number of GPU layers to offload. -1 for all."""
        self._n_gpu_layers = n_layers
    
    def set_context_window(self, n_ctx: int):
        """Set context window size."""
        self._n_ctx = n_ctx
    
    def tokenize(self, text: str) -> List[int]:
        """Tokenize text and return token IDs."""
        if not self.llm:
            return []
        return self.llm.tokenize(text.encode("utf-8"))
    
    def detokenize(self, tokens: List[int]) -> str:
        """Convert token IDs back to text."""
        if not self.llm:
            return ""
        return self.llm.detokenize(tokens).decode("utf-8", errors="ignore")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenize(text))
