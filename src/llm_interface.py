"""
Abstract LLM Interface for ResilienceAI

Provides a unified interface for multiple local LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional, Union, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMMessage:
    """Represents a message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: str = "ollama"  # "ollama", "lmstudio", "huggingface", "llamacpp"
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 0.9
    timeout: int = 60
    # Provider-specific settings
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    device: Optional[str] = None  # for HuggingFace
    context_window: int = 4096
    
    def __post_init__(self):
        # Set default models per provider
        if self.model is None:
            defaults = {
                "ollama": "mistral:7b",
                "lmstudio": "local-model",
                "huggingface": "microsoft/DialoGPT-medium",
                "llamacpp": "models/default.gguf"
            }
            self.model = defaults.get(self.provider, "mistral:7b")


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._initialized = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider. Returns True if successful."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available/ready."""
        pass
    
    @abstractmethod
    async def generate(
        self, 
        messages: List[LLMMessage], 
        stream: bool = False
    ) -> Union[LLMResponse, AsyncIterator[str]]:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of conversation messages
            stream: If True, return an async iterator of text chunks
            
        Returns:
            LLMResponse if stream=False, AsyncIterator[str] if stream=True
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Return health status of the provider."""
        pass
    
    async def close(self):
        """Clean up resources. Override if needed."""
        self._initialized = False


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: type):
        """Register a provider class."""
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered LLM provider: {name}")
    
    @classmethod
    def create(cls, config: LLMConfig) -> BaseLLMProvider:
        """Create a provider instance from config."""
        provider_name = config.provider.lower()
        
        if provider_name not in cls._providers:
            available = list(cls._providers.keys())
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available: {available}"
            )
        
        provider_class = cls._providers[provider_name]
        return provider_class(config)
    
    @classmethod
    def available_providers(cls) -> List[str]:
        """List all registered provider names."""
        return list(cls._providers.keys())


class LLMManager:
    """
    High-level manager for LLM operations.
    Handles provider selection, auto-detection, and insight generation.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self._provider: Optional[BaseLLMProvider] = None
        self._fallback_chain: List[str] = []
    
    async def initialize(self, fallback_chain: Optional[List[str]] = None) -> bool:
        """
        Initialize with auto-detection and fallback support.
        
        Args:
            fallback_chain: Ordered list of providers to try
        """
        if fallback_chain is None:
            fallback_chain = ["ollama", "lmstudio", "huggingface", "llamacpp"]
        
        self._fallback_chain = fallback_chain
        
        # Try primary config provider first
        providers_to_try = [self.config.provider] + [
            p for p in fallback_chain if p != self.config.provider
        ]
        
        for provider_name in providers_to_try:
            if provider_name not in LLMProviderFactory.available_providers():
                logger.warning(f"Provider {provider_name} not registered, skipping")
                continue
            
            try:
                config = LLMConfig(
                    provider=provider_name,
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    base_url=self.config.base_url,
                    device=self.config.device
                )
                
                provider = LLMProviderFactory.create(config)
                
                if await provider.initialize():
                    if await provider.is_available():
                        self._provider = provider
                        logger.info(f"Successfully initialized {provider_name}")
                        return True
                    else:
                        await provider.close()
                        logger.warning(f"{provider_name} initialized but not available")
                else:
                    logger.warning(f"Failed to initialize {provider_name}")
                    
            except Exception as e:
                logger.warning(f"Error initializing {provider_name}: {e}")
                continue
        
        logger.error("No LLM providers available")
        return False
    
    @property
    def provider(self) -> Optional[BaseLLMProvider]:
        """Get the current active provider."""
        return self._provider
    
    @property
    def provider_name(self) -> Optional[str]:
        """Get the name of the current provider."""
        return self._provider.name if self._provider else None
    
    async def generate(
        self, 
        messages: List[LLMMessage], 
        stream: bool = False
    ) -> Union[LLMResponse, AsyncIterator[str]]:
        """Generate response using active provider."""
        if self._provider is None:
            raise RuntimeError("LLM not initialized. Call initialize() first.")
        return await self._provider.generate(messages, stream)
    
    async def generate_insight(
        self,
        data: Dict[str, Any],
        context: Optional[str] = None,
        insight_type: str = "analysis"
    ) -> str:
        """
        Generate natural language insights from structured data.
        
        Args:
            data: Structured data to analyze
            context: Additional context about the data
            insight_type: Type of insight (analysis, summary, alert, recommendation)
        """
        system_prompt = self._get_insight_prompt(insight_type)
        
        user_content = f"Context: {context}\n\nData: {data}" if context else f"Data: {data}"
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_content)
        ]
        
        response = await self.generate(messages)
        return response.content if isinstance(response, LLMResponse) else str(response)
    
    async def craft_response(
        self,
        agent_output: Dict[str, Any],
        tone: str = "professional",
        audience: str = "general"
    ) -> str:
        """
        Craft human-readable response from agent outputs.
        
        Args:
            agent_output: Raw output from agents
            tone: Response tone (professional, casual, urgent, empathetic)
            audience: Target audience (general, technical, executive)
        """
        system_prompt = f"""You are a response crafting assistant. Transform structured agent outputs into 
natural, human-readable responses. Use a {tone} tone appropriate for a {audience} audience.
Be concise but informative. Focus on actionable insights."""
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=f"Agent output: {agent_output}")
        ]
        
        response = await self.generate(messages)
        return response.content if isinstance(response, LLMResponse) else str(response)
    
    def _get_insight_prompt(self, insight_type: str) -> str:
        """Get system prompt for insight generation."""
        prompts = {
            "analysis": """You are a data analysis assistant. Analyze the provided data and generate 
insightful observations. Identify patterns, anomalies, and key metrics. Be specific and data-driven.""",
            
            "summary": """You are a summarization assistant. Create a concise summary of the provided data.
Highlight the most important points. Use bullet points for clarity when appropriate.""",
            
            "alert": """You are an alert generation assistant. Analyze the data for critical issues 
requiring immediate attention. Be direct and action-oriented. If no alerts are needed, state that clearly.""",
            
            "recommendation": """You are a recommendation assistant. Based on the provided data, 
generate actionable recommendations. Prioritize by impact and feasibility. Be specific about next steps.""",
            
            "trend": """You are a trend analysis assistant. Identify trends and patterns in the data.
Compare current state to historical norms if available. Highlight significant changes."""
        }
        return prompts.get(insight_type, prompts["analysis"])
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the current provider."""
        if self._provider is None:
            return {"status": "not_initialized", "provider": None}
        return await self._provider.health_check()
    
    async def close(self):
        """Clean up resources."""
        if self._provider:
            await self._provider.close()
            self._provider = None


# Convenience functions for quick usage
async def quick_generate(
    prompt: str,
    provider: str = "ollama",
    model: Optional[str] = None,
    system: Optional[str] = None
) -> str:
    """Quick one-off generation without managing state."""
    config = LLMConfig(provider=provider, model=model)
    manager = LLMManager(config)
    
    if not await manager.initialize():
        raise RuntimeError(f"Could not initialize {provider}")
    
    messages = []
    if system:
        messages.append(LLMMessage(role="system", content=system))
    messages.append(LLMMessage(role="user", content=prompt))
    
    response = await manager.generate(messages)
    result = response.content if isinstance(response, LLMResponse) else str(response)
    
    await manager.close()
    return result
