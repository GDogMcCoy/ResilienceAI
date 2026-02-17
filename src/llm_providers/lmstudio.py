"""
LM Studio Provider for ResilienceAI

Uses LM Studio's OpenAI-compatible API.
Default: http://localhost:1234/v1
"""

import json
import logging
import sys
import os
from typing import AsyncIterator, Dict, List, Optional, Union, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_interface import BaseLLMProvider, LLMConfig, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class LMStudioProvider(BaseLLMProvider):
    """LM Studio LLM provider implementation (OpenAI-compatible)."""
    
    DEFAULT_BASE_URL = "http://localhost:1234/v1"
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or self.DEFAULT_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self._headers = {
            "Content-Type": "application/json"
        }
        if config.api_key:
            self._headers["Authorization"] = f"Bearer {config.api_key}"
    
    @property
    def name(self) -> str:
        return "lmstudio"
    
    async def initialize(self) -> bool:
        """Initialize the HTTP session."""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                headers=self._headers
            )
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LM Studio session: {e}")
            return False
    
    async def is_available(self) -> bool:
        """Check if LM Studio server is running."""
        if not self.session:
            return False
        
        try:
            async with self.session.get(f"{self.base_url}/models") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m.get("id") for m in data.get("data", [])]
                    logger.debug(f"LM Studio available with models: {models}")
                    return True
                return False
        except Exception as e:
            logger.debug(f"LM Studio not available: {e}")
            return False
    
    async def generate(
        self, 
        messages: List[LLMMessage], 
        stream: bool = False
    ) -> Union[LLMResponse, AsyncIterator[str]]:
        """Generate response via LM Studio OpenAI-compatible API."""
        if not self.session:
            raise RuntimeError("Provider not initialized")
        
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        payload = {
            "model": self.config.model,
            "messages": openai_messages,
            "stream": stream,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
        }
        
        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens
        
        if stream:
            return self._stream_generate(payload)
        
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"LM Studio API error: {resp.status} - {error_text}")
            
            data = await resp.json()
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            return LLMResponse(
                content=message.get("content", ""),
                model=data.get("model", self.config.model),
                usage=data.get("usage"),
                finish_reason=choice.get("finish_reason"),
                metadata={
                    "created": data.get("created"),
                    "system_fingerprint": data.get("system_fingerprint"),
                }
            )
    
    async def _stream_generate(self, payload: Dict) -> AsyncIterator[str]:
        """Stream generate response."""
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"LM Studio API error: {resp.status} - {error_text}")
            
            async for line in resp.content:
                line = line.decode("utf-8").strip()
                
                if not line or line == "data: [DONE]":
                    continue
                
                if line.startswith("data: "):
                    line = line[6:]
                
                try:
                    data = json.loads(line)
                    choice = data.get("choices", [{}])[0]
                    delta = choice.get("delta", {})
                    
                    if "content" in delta:
                        yield delta["content"]
                    
                    if choice.get("finish_reason"):
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
            
            # Try to get loaded model info
            try:
                async with self.session.get(f"{self.base_url}/models") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        status["loaded_models"] = [
                            m.get("id") for m in data.get("data", [])
                        ]
            except Exception:
                pass
        
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
            async with self.session.get(f"{self.base_url}/models") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [m.get("id") for m in data.get("data", [])]
                return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def get_model_info(self, model_id: Optional[str] = None) -> Optional[Dict]:
        """Get information about a loaded model."""
        if not self.session:
            return None
        
        model = model_id or self.config.model
        
        try:
            async with self.session.get(f"{self.base_url}/models/{model}") as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None
