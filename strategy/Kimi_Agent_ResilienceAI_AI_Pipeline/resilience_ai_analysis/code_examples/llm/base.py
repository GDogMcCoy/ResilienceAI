"""
ResilienceAI - LLM Provider Abstraction Layer
Base classes for LLM provider integration.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
import time


class LLMProviderType(Enum):
    """Supported LLM providers."""
    ARCHIA = "archia"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    HUGGINGFACE = "huggingface"


@dataclass
class LLMMessage:
    """LLM message structure."""
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None  # For tool messages
    tool_calls: Optional[List[Dict]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM response structure."""
    content: str
    model: str
    provider: str
    tokens_used: Dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: LLMProviderType
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    retry_attempts: int = 3
    streaming: bool = False
    extra_params: Dict[str, Any] = field(default_factory=dict)


class BaseLLMProvider(ABC):
    """Abstract base for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict]] = None
    ) -> LLMResponse:
        """Generate a response."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict]] = None
    ) -> AsyncIterator[str]:
        """Generate a streaming response."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy."""
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass
    
    async def close(self) -> None:
        """Clean up resources."""
        pass


class LLMManager:
    """
    Manages multiple LLM providers with fallback support.
    
    Features:
    - Provider health monitoring
    - Automatic fallback
    - Load balancing
    - Token usage tracking
    """
    
    def __init__(
        self,
        configs: List[LLMConfig],
        fallback_enabled: bool = True,
        load_balance: bool = False
    ):
        self.configs = configs
        self.fallback_enabled = fallback_enabled
        self.load_balance = load_balance
        
        self._providers: Dict[LLMProviderType, BaseLLMProvider] = {}
        self._provider_health: Dict[LLMProviderType, bool] = {}
        self._token_usage: Dict[str, int] = {"prompt": 0, "completion": 0}
        self._lock = None  # Will be created in async context
        
    async def initialize(self) -> bool:
        """Initialize all providers."""
        import asyncio
        self._lock = asyncio.Lock()
        
        for config in self.configs:
            provider = self._create_provider(config)
            if provider:
                try:
                    healthy = await provider.initialize()
                    self._providers[config.provider] = provider
                    self._provider_health[config.provider] = healthy
                except Exception as e:
                    print(f"Failed to initialize {config.provider}: {e}")
                    self._provider_health[config.provider] = False
        
        return any(self._provider_health.values())
    
    def _create_provider(self, config: LLMConfig) -> Optional[BaseLLMProvider]:
        """Create provider instance based on type."""
        # Import providers here to avoid circular imports
        from .providers.archia import ArchiaProvider
        from .providers.openai import OpenAIProvider
        from .providers.anthropic import AnthropicProvider
        from .providers.ollama import OllamaProvider
        
        provider_map = {
            LLMProviderType.ARCHIA: ArchiaProvider,
            LLMProviderType.OPENAI: OpenAIProvider,
            LLMProviderType.ANTHROPIC: AnthropicProvider,
            LLMProviderType.OLLAMA: OllamaProvider,
        }
        
        provider_class = provider_map.get(config.provider)
        return provider_class(config) if provider_class else None
    
    async def generate(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict]] = None,
        preferred_provider: Optional[LLMProviderType] = None
    ) -> LLMResponse:
        """
        Generate with automatic fallback.
        
        Args:
            messages: List of messages
            tools: Available tools
            preferred_provider: Preferred provider (optional)
            
        Returns:
            LLMResponse
        """
        providers = self._get_provider_order(preferred_provider)
        
        last_error = None
        for provider_type in providers:
            provider = self._providers.get(provider_type)
            if not provider or not self._provider_health.get(provider_type):
                continue
            
            try:
                start_time = time.time()
                response = await provider.generate(messages, tools)
                response.latency_ms = (time.time() - start_time) * 1000
                
                # Update token usage
                if self._lock:
                    async with self._lock:
                        self._token_usage["prompt"] += response.tokens_used.get("prompt", 0)
                        self._token_usage["completion"] += response.tokens_used.get("completion", 0)
                
                return response
                
            except Exception as e:
                last_error = e
                self._provider_health[provider_type] = False
                if not self.fallback_enabled:
                    break
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    async def generate_simple(self, prompt: str) -> str:
        """Simple generation with single message."""
        messages = [LLMMessage(role="user", content=prompt)]
        response = await self.generate(messages)
        return response.content
    
    def _get_provider_order(
        self,
        preferred: Optional[LLMProviderType] = None
    ) -> List[LLMProviderType]:
        """Get provider order based on preference and health."""
        healthy = [p for p, h in self._provider_health.items() if h]
        
        if preferred and preferred in healthy:
            healthy.remove(preferred)
            return [preferred] + healthy
        
        if self.load_balance:
            import random
            random.shuffle(healthy)
        
        return healthy
    
    async def health_check_all(self) -> Dict[LLMProviderType, bool]:
        """Check health of all providers."""
        for provider_type, provider in self._providers.items():
            try:
                self._provider_health[provider_type] = await provider.health_check()
            except:
                self._provider_health[provider_type] = False
        
        return self._provider_health.copy()
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get total token usage."""
        return self._token_usage.copy()
    
    async def close(self):
        """Close all providers."""
        for provider in self._providers.values():
            await provider.close()
