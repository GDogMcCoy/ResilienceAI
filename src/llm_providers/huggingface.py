"""
Hugging Face Transformers Provider for ResilienceAI

Direct model loading using Hugging Face Transformers library.
"""

import logging
import os
from typing import AsyncIterator, Dict, List, Optional, Union, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..llm_interface import BaseLLMProvider, LLMConfig, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class HuggingFaceProvider(BaseLLMProvider):
    """Hugging Face Transformers LLM provider implementation."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._device = None
    
    @property
    def name(self) -> str:
        return "huggingface"
    
    async def initialize(self) -> bool:
        """Initialize the Hugging Face model and tokenizer."""
        try:
            # Import here to avoid dependency if not used
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            
            # Determine device
            if self.config.device:
                self._device = self.config.device
            elif torch.cuda.is_available():
                self._device = "cuda"
            elif torch.backends.mps.is_available():
                self._device = "mps"
            else:
                self._device = "cpu"
            
            logger.info(f"Loading Hugging Face model: {self.config.model} on {self._device}")
            
            # Load tokenizer and model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            self.tokenizer = await loop.run_in_executor(
                self._executor,
                lambda: AutoTokenizer.from_pretrained(self.config.model)
            )
            
            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = await loop.run_in_executor(
                self._executor,
                lambda: AutoModelForCausalLM.from_pretrained(
                    self.config.model,
                    torch_dtype=torch.float16 if self._device == "cuda" else torch.float32,
                    device_map="auto" if self._device == "cuda" else None,
                    low_cpu_mem_usage=True
                )
            )
            
            if self._device != "cuda":
                self.model = self.model.to(self._device)
            
            # Create pipeline for easier generation
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self._device == "cuda" else -1,
                torch_dtype=torch.float16 if self._device == "cuda" else torch.float32
            )
            
            self._initialized = True
            logger.info(f"Successfully loaded {self.config.model}")
            return True
            
        except ImportError as e:
            logger.error(f"Hugging Face dependencies not installed: {e}")
            logger.error("Install with: pip install transformers torch")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face provider: {e}")
            return False
    
    async def is_available(self) -> bool:
        """Check if model is loaded."""
        return self._initialized and self.model is not None and self.tokenizer is not None
    
    async def generate(
        self, 
        messages: List[LLMMessage], 
        stream: bool = False
    ) -> Union[LLMResponse, AsyncIterator[str]]:
        """Generate response using Hugging Face model."""
        if not self._initialized or not self.pipeline:
            raise RuntimeError("Provider not initialized")
        
        # Format messages into a prompt
        prompt = self._format_messages(messages)
        
        if stream:
            return self._stream_generate(prompt)
        
        # Generate in thread pool
        loop = asyncio.get_event_loop()
        
        def _generate():
            outputs = self.pipeline(
                prompt,
                max_new_tokens=self.config.max_tokens or 512,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                return_full_text=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
            return outputs[0]["generated_text"]
        
        generated_text = await loop.run_in_executor(self._executor, _generate)
        
        return LLMResponse(
            content=generated_text.strip(),
            model=self.config.model,
            usage=None,  # HF doesn't provide easy token counting
            finish_reason="stop",
            metadata={
                "device": self._device,
                "prompt_length": len(prompt)
            }
        )
    
    async def _stream_generate(self, prompt: str) -> AsyncIterator[str]:
        """Stream generate response (simulated via chunks)."""
        # HF doesn't natively support streaming, so we generate and yield chunks
        loop = asyncio.get_event_loop()
        
        def _generate():
            outputs = self.pipeline(
                prompt,
                max_new_tokens=self.config.max_tokens or 512,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                return_full_text=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
            return outputs[0]["generated_text"]
        
        generated_text = await loop.run_in_executor(self._executor, _generate)
        
        # Yield in chunks to simulate streaming
        chunk_size = 10
        for i in range(0, len(generated_text), chunk_size):
            yield generated_text[i:i + chunk_size]
            await asyncio.sleep(0.01)  # Small delay for natural feel
    
    def _format_messages(self, messages: List[LLMMessage]) -> str:
        """Format messages into a prompt string."""
        formatted = []
        
        for msg in messages:
            if msg.role == "system":
                formatted.append(f"System: {msg.content}")
            elif msg.role == "user":
                formatted.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                formatted.append(f"Assistant: {msg.content}")
        
        formatted.append("Assistant:")
        return "\n\n".join(formatted)
    
    async def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        import torch
        
        status = {
            "provider": self.name,
            "initialized": self._initialized,
            "available": await self.is_available(),
            "model": self.config.model,
            "device": self._device,
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
        }
        
        if torch.cuda.is_available():
            status["cuda_device"] = torch.cuda.get_device_name(0)
            status["cuda_memory_allocated"] = torch.cuda.memory_allocated() / 1e9
            status["cuda_memory_reserved"] = torch.cuda.memory_reserved() / 1e9
        
        return status
    
    async def close(self):
        """Clean up resources."""
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
        
        self._executor.shutdown(wait=True)
        
        # Clear CUDA cache if applicable
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        
        await super().close()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        try:
            import torch
            if torch.cuda.is_available():
                return {
                    "allocated_gb": torch.cuda.memory_allocated() / 1e9,
                    "reserved_gb": torch.cuda.memory_reserved() / 1e9,
                    "max_allocated_gb": torch.cuda.max_memory_allocated() / 1e9,
                }
        except ImportError:
            pass
        return {}
