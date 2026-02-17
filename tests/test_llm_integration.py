"""
Tests for LLM Integration in ResilienceAI
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import json

# Import the modules under test
import sys
sys.path.insert(0, '/root/.openclaw/workspace/ResilienceAI/src')

from llm_interface import (
    LLMMessage, LLMResponse, LLMConfig, 
    BaseLLMProvider, LLMProviderFactory, LLMManager,
    quick_generate
)


class TestLLMMessage:
    """Tests for LLMMessage dataclass."""
    
    def test_message_creation(self):
        msg = LLMMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
    
    def test_system_message(self):
        msg = LLMMessage(role="system", content="You are helpful")
        assert msg.role == "system"
        assert msg.content == "You are helpful"


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""
    
    def test_response_creation(self):
        resp = LLMResponse(
            content="Hello there",
            model="mistral:7b",
            usage={"prompt_tokens": 10, "completion_tokens": 5}
        )
        assert resp.content == "Hello there"
        assert resp.model == "mistral:7b"
        assert resp.usage["prompt_tokens"] == 10
    
    def test_response_with_metadata(self):
        resp = LLMResponse(
            content="Test",
            model="test-model",
            metadata={"key": "value"}
        )
        assert resp.metadata["key"] == "value"


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""
    
    def test_default_config(self):
        config = LLMConfig()
        assert config.provider == "ollama"
        assert config.model == "mistral:7b"
        assert config.temperature == 0.7
        assert config.top_p == 0.9
    
    def test_custom_config(self):
        config = LLMConfig(
            provider="lmstudio",
            model="custom-model",
            temperature=0.5
        )
        assert config.provider == "lmstudio"
        assert config.model == "custom-model"
        assert config.temperature == 0.5
    
    def test_provider_defaults(self):
        providers = {
            "ollama": "mistral:7b",
            "lmstudio": "local-model",
            "huggingface": "microsoft/DialoGPT-medium",
            "llamacpp": "models/default.gguf"
        }
        
        for provider, expected_model in providers.items():
            config = LLMConfig(provider=provider)
            assert config.model == expected_model


class MockProvider(BaseLLMProvider):
    """Mock provider for testing."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.mock_response = "Mock response"
    
    @property
    def name(self) -> str:
        return "mock"
    
    async def initialize(self) -> bool:
        self._initialized = True
        return True
    
    async def is_available(self) -> bool:
        return self._initialized
    
    async def generate(self, messages, stream=False):
        if stream:
            async def stream_gen():
                for word in self.mock_response.split():
                    yield word + " "
            return stream_gen()
        return LLMResponse(content=self.mock_response, model="mock-model")
    
    async def health_check(self):
        return {"status": "healthy"}


class TestLLMProviderFactory:
    """Tests for LLMProviderFactory."""
    
    def test_register_provider(self):
        LLMProviderFactory.register("mock", MockProvider)
        assert "mock" in LLMProviderFactory.available_providers()
    
    def test_create_provider(self):
        config = LLMConfig(provider="mock")
        provider = LLMProviderFactory.create(config)
        assert isinstance(provider, MockProvider)
    
    def test_unknown_provider(self):
        config = LLMConfig(provider="unknown")
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMProviderFactory.create(config)
    
    def test_available_providers_list(self):
        providers = LLMProviderFactory.available_providers()
        assert isinstance(providers, list)


class TestLLMManager:
    """Tests for LLMManager."""
    
    @pytest.fixture
    def mock_manager(self):
        manager = LLMManager(LLMConfig(provider="mock"))
        return manager
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_manager):
        LLMProviderFactory.register("mock", MockProvider)
        result = await mock_manager.initialize()
        assert result is True
        assert mock_manager.provider is not None
    
    @pytest.mark.asyncio
    async def test_initialize_fallback(self):
        # Create a mock provider that fails
        class FailingProvider(BaseLLMProvider):
            @property
            def name(self): return "failing"
            async def initialize(self): return False
            async def is_available(self): return False
            async def generate(self, messages, stream=False): pass
            async def health_check(self): return {}
        
        LLMProviderFactory.register("failing", FailingProvider)
        LLMProviderFactory.register("mock", MockProvider)
        
        config = LLMConfig(provider="failing")
        manager = LLMManager(config)
        
        result = await manager.initialize(fallback_chain=["mock"])
        assert result is True
        assert manager.provider_name == "mock"
    
    @pytest.mark.asyncio
    async def test_generate_not_initialized(self):
        manager = LLMManager(LLMConfig(provider="mock"))
        with pytest.raises(RuntimeError, match="not initialized"):
            await manager.generate([LLMMessage(role="user", content="Hi")])
    
    @pytest.mark.asyncio
    async def test_generate_success(self, mock_manager):
        LLMProviderFactory.register("mock", MockProvider)
        await mock_manager.initialize()
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await mock_manager.generate(messages)
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Mock response"
    
    @pytest.mark.asyncio
    async def test_generate_insight(self, mock_manager):
        LLMProviderFactory.register("mock", MockProvider)
        await mock_manager.initialize()
        
        data = {"cpu": 80, "memory": 90}
        insight = await mock_manager.generate_insight(
            data, 
            context="System metrics",
            insight_type="analysis"
        )
        
        assert isinstance(insight, str)
        assert len(insight) > 0
    
    @pytest.mark.asyncio
    async def test_craft_response(self, mock_manager):
        LLMProviderFactory.register("mock", MockProvider)
        await mock_manager.initialize()
        
        agent_output = {"status": "alert", "severity": "high"}
        response = await mock_manager.craft_response(
            agent_output,
            tone="professional",
            audience="technical"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_manager):
        LLMProviderFactory.register("mock", MockProvider)
        await mock_manager.initialize()
        
        health = await mock_manager.health_check()
        assert "provider" in health
        assert health["provider"] == "mock"
    
    @pytest.mark.asyncio
    async def test_close(self, mock_manager):
        LLMProviderFactory.register("mock", MockProvider)
        await mock_manager.initialize()
        
        await mock_manager.close()
        assert mock_manager.provider is None


class TestOllamaProvider:
    """Tests for OllamaProvider."""
    
    @pytest.mark.asyncio
    async def test_provider_name(self):
        from llm_providers.ollama import OllamaProvider
        config = LLMConfig(provider="ollama")
        provider = OllamaProvider(config)
        assert provider.name == "ollama"
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_initialize(self, mock_session):
        from llm_providers.ollama import OllamaProvider
        config = LLMConfig(provider="ollama")
        provider = OllamaProvider(config)
        
        result = await provider.initialize()
        assert result is True
        assert provider.session is not None
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_is_available(self, mock_session_class):
        from llm_providers.ollama import OllamaProvider
        
        # Setup mock
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"models": [{"name": "mistral:7b"}]}
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_session_class.return_value = mock_session
        
        config = LLMConfig(provider="ollama")
        provider = OllamaProvider(config)
        await provider.initialize()
        provider.session = mock_session
        
        result = await provider.is_available()
        assert result is True


class TestLMStudioProvider:
    """Tests for LMStudioProvider."""
    
    @pytest.mark.asyncio
    async def test_provider_name(self):
        from llm_providers.lmstudio import LMStudioProvider
        config = LLMConfig(provider="lmstudio")
        provider = LMStudioProvider(config)
        assert provider.name == "lmstudio"
    
    @pytest.mark.asyncio
    async def test_default_base_url(self):
        from llm_providers.lmstudio import LMStudioProvider
        config = LLMConfig(provider="lmstudio")
        provider = LMStudioProvider(config)
        assert provider.base_url == "http://localhost:1234/v1"


class TestHuggingFaceProvider:
    """Tests for HuggingFaceProvider."""
    
    @pytest.mark.asyncio
    async def test_provider_name(self):
        from llm_providers.huggingface import HuggingFaceProvider
        config = LLMConfig(provider="huggingface")
        provider = HuggingFaceProvider(config)
        assert provider.name == "huggingface"
    
    @pytest.mark.asyncio
    async def test_format_messages(self):
        from llm_providers.huggingface import HuggingFaceProvider
        config = LLMConfig(provider="huggingface")
        provider = HuggingFaceProvider(config)
        
        messages = [
            LLMMessage(role="system", content="Be helpful"),
            LLMMessage(role="user", content="Hello"),
        ]
        
        formatted = provider._format_messages(messages)
        assert "System: Be helpful" in formatted
        assert "User: Hello" in formatted
        assert "Assistant:" in formatted


class TestLlamaCppProvider:
    """Tests for LlamaCppProvider."""
    
    @pytest.mark.asyncio
    async def test_provider_name(self):
        from llm_providers.llamacpp import LlamaCppProvider
        config = LLMConfig(provider="llamacpp", model="test.gguf")
        provider = LlamaCppProvider(config)
        assert provider.name == "llamacpp"
    
    @pytest.mark.asyncio
    async def test_format_chat_prompt(self):
        from llm_providers.llamacpp import LlamaCppProvider
        config = LLMConfig(provider="llamacpp", model="test.gguf")
        provider = LlamaCppProvider(config)
        
        messages = [
            LLMMessage(role="system", content="Be helpful"),
            LLMMessage(role="user", content="Hello"),
        ]
        
        formatted = provider._format_chat_prompt(messages)
        assert "<|im_start|>system" in formatted
        assert "Be helpful" in formatted
        assert "<|im_start|>user" in formatted
        assert "Hello" in formatted
        assert "<|im_start|>assistant" in formatted


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow with mock provider."""
        LLMProviderFactory.register("mock", MockProvider)
        
        # Initialize manager
        config = LLMConfig(provider="mock")
        manager = LLMManager(config)
        
        success = await manager.initialize()
        assert success is True
        
        # Generate response
        messages = [
            LLMMessage(role="system", content="You are helpful"),
            LLMMessage(role="user", content="What is the weather?")
        ]
        response = await manager.generate(messages)
        assert isinstance(response, LLMResponse)
        
        # Generate insight
        data = {"temperature": 72, "humidity": 45}
        insight = await manager.generate_insight(data, context="Weather data")
        assert isinstance(insight, str)
        
        # Craft response
        agent_output = {"action": "notify", "message": "Weather is nice"}
        crafted = await manager.craft_response(agent_output)
        assert isinstance(crafted, str)
        
        # Cleanup
        await manager.close()
    
    @pytest.mark.asyncio
    async def test_provider_switching(self):
        """Test switching between providers."""
        LLMProviderFactory.register("mock1", MockProvider)
        LLMProviderFactory.register("mock2", MockProvider)
        
        # Use first provider
        config1 = LLMConfig(provider="mock1")
        manager1 = LLMManager(config1)
        await manager1.initialize()
        assert manager1.provider_name == "mock1"
        
        # Use second provider
        config2 = LLMConfig(provider="mock2")
        manager2 = LLMManager(config2)
        await manager2.initialize()
        assert manager2.provider_name == "mock2"
        
        await manager1.close()
        await manager2.close()


class TestAutoDetection:
    """Tests for provider auto-detection."""
    
    @pytest.mark.asyncio
    async def test_fallback_chain(self):
        """Test that fallback chain works correctly."""
        
        class UnavailableProvider(BaseLLMProvider):
            @property
            def name(self): return "unavailable"
            async def initialize(self): return True
            async def is_available(self): return False
            async def generate(self, messages, stream=False): pass
            async def health_check(self): return {}
        
        class AvailableProvider(BaseLLMProvider):
            @property
            def name(self): return "available"
            async def initialize(self): return True
            async def is_available(self): return True
            async def generate(self, messages, stream=False):
                return LLMResponse(content="Success", model="available")
            async def health_check(self): return {}
        
        LLMProviderFactory.register("unavailable", UnavailableProvider)
        LLMProviderFactory.register("available", AvailableProvider)
        
        config = LLMConfig(provider="unavailable")
        manager = LLMManager(config)
        
        success = await manager.initialize(fallback_chain=["available"])
        assert success is True
        assert manager.provider_name == "available"
        
        await manager.close()


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
