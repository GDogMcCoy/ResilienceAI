"""
Ollama Provider for ResilienceAI

Uses Ollama's HTTP API for local LLM inference.
Default: ollama run mistral:7b
"""

import json
import logging
from typing import AsyncIterator, Dict, List, Optional, Union, Any
import aiohttp

from ..llm_interface import BaseLLMProvider, LLMConfig, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation."""
    
    DEFAULT_BASE_URL = "http://localhost:11434"
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or self.DEFAULT_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    @property
    def name(self) -> str:
        return "ollama"
    
    async def initialize(self) -> bool:
        """Initialize the HTTP session."""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Ollama session: {e}")
            return False
    
    async def is_available(self) -> bool:
        """Check if Ollama server is running."""
        if not self.session:
            return False
        
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    logger.debug(f"Ollama available with models: {models}")
                    return True
                return False
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    async def generate(
        self, 
        messages: List[LLMMessage], 
        stream: bool = False
    ) -> Union[LLMResponse, AsyncIterator[str]]:
        """Generate response via Ollama API."""
        if not self.session:
            raise RuntimeError("Provider not initialized")
        
        # Convert messages to Ollama format
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        payload = {
            "model": self.config.model,
            "messages": ollama_messages,
            "stream": stream,
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
            }
        }
        
        if self.config.max_tokens:
            payload["options"]["num_predict"] = self.config.max_tokens
        
        if stream:
            return self._stream_generate(payload)
        
        async with self.session.post(
            f"{self.base_url}/api/chat",
            json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"Ollama API error: {resp.status} - {error_text}")
            
            data = await resp.json()
            
            return LLMResponse(
                content=data.get("message", {}).get("content", ""),
                model=self.config.model,
                finish_reason="stop" if data.get("done") else None,
                metadata={
                    "total_duration": data.get("total_duration"),
                    "load_duration": data.get("load_duration"),
                    "prompt_eval_count": data.get("prompt_eval_count"),
                    "eval_count": data.get("eval_count"),
                }
            )
    
    async def _stream_generate(self, payload: Dict) -> AsyncIterator[str]:
        """Stream generate response."""
        async with self.session.post(
            f"{self.base_url}/api/chat",
            json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"Ollama API error: {resp.status} - {error_text}")
            
            async for line in resp.content:
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
                    
                    if data.get("done"):
                        break
                        
                except json.JSONDecodeError:
                    continue
    
    async def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        status = {
            "provider": self.name,
            "initialized": self._initialized,
            "available": False,
            "model": self.config.model,
            "base_url": self.base_url
        }
        
        if self._initialized:
            status["available"] = await self.is_available()
        
        return status
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
        await super().close()
    
    async def list_models(self) -> List[str]:
        """List available models."""
        if not self.session:
            return []
        
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [m.get("name") for m in data.get("models", [])]
                return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry."""
        if not self.session:
            return False
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name, "stream": False}
            ) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
