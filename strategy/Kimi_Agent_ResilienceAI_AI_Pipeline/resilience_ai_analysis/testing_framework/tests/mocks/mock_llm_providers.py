"""
Mock LLM providers for testing

Provides mock implementations of LLM providers for reliable,
fast tests without requiring actual LLM infrastructure.
"""
from unittest.mock import Mock
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime


class MockLLMResponse:
    """Mock LLM response object."""
    
    def __init__(self, content: str, model: str = "mock-model", 
                 usage: Dict = None, metadata: Dict = None):
        self.content = content
        self.model = model
        self.usage = usage or {
            "prompt_tokens": 10,
            "completion_tokens": len(content.split()),
            "total_tokens": 10 + len(content.split())
        }
        self.metadata = metadata or {}
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()


class MockLLMMessage:
    """Mock LLM message."""
    
    def __init__(self, role: str, content: str, metadata: Dict = None):
        self.role = role
        self.content = content
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata
        }


class MockOllamaProvider:
    """Mock Ollama provider for testing."""
    
    def __init__(self, model: str = "mistral:7b", **kwargs):
        self.model = model
        self.base_url = kwargs.get('base_url', 'http://localhost:11434')
        self.call_count = 0
        self.responses: List[str] = []
        self.call_history: List[Dict] = []
        self.response_delay = kwargs.get('delay', 0)
    
    def set_responses(self, responses: List[str]):
        """Set predefined responses."""
        self.responses = responses
    
    def add_response(self, response: str):
        """Add a response to the queue."""
        self.responses.append(response)
    
    def generate(self, messages: List[MockLLMMessage], **kwargs) -> MockLLMResponse:
        """Generate mock response."""
        import time
        
        if self.response_delay > 0:
            time.sleep(self.response_delay)
        
        self.call_count += 1
        
        # Record call history
        self.call_history.append({
            'call_number': self.call_count,
            'messages': [m.to_dict() for m in messages],
            'kwargs': kwargs,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get response from queue or generate default
        if self.responses:
            content = self.responses[(self.call_count - 1) % len(self.responses)]
        else:
            # Generate default response based on last message
            last_message = messages[-1].content if messages else ""
            content = self._generate_default_response(last_message)
        
        return MockLLMResponse(
            content=content,
            model=self.model,
            usage={
                "prompt_tokens": sum(len(m.content.split()) for m in messages),
                "completion_tokens": len(content.split()),
                "total_tokens": sum(len(m.content.split()) for m in messages) + len(content.split())
            },
            metadata={
                "call_count": self.call_count,
                "provider": "ollama"
            }
        )
    
    def _generate_default_response(self, query: str) -> str:
        """Generate a default response based on query."""
        if "vulnerability" in query.lower():
            return json.dumps({
                "action": "assess_vulnerability",
                "county": self._extract_county(query),
                "confidence": 0.95
            })
        elif "weather" in query.lower() or "alert" in query.lower():
            return json.dumps({
                "action": "get_weather_alerts",
                "location": self._extract_location(query),
            })
        elif "risk" in query.lower():
            return json.dumps({
                "action": "assess_risk",
                "factors": ["flood", "tornado", "earthquake"],
            })
        else:
            return "I understand your query about disaster resilience."
    
    def _extract_county(self, query: str) -> Optional[str]:
        """Extract county name from query."""
        import re
        match = re.search(r'(\w+)\s+county', query, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_location(self, query: str) -> str:
        """Extract location from query."""
        import re
        match = re.search(r'for\s+(\w+)', query, re.IGNORECASE)
        return match.group(1) if match else "Missouri"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model info."""
        return {
            "name": self.model,
            "provider": "ollama",
            "capabilities": ["text-generation", "json-mode"],
            "call_count": self.call_count
        }
    
    def health_check(self) -> bool:
        """Mock health check."""
        return True


class MockHuggingFaceProvider:
    """Mock HuggingFace provider for testing."""
    
    def __init__(self, model: str = "gpt2", **kwargs):
        self.model = model
        self.api_key = kwargs.get('api_key', 'mock-key')
        self.pipeline = Mock()
        self.call_count = 0
    
    def generate(self, messages: List[MockLLMMessage], **kwargs) -> MockLLMResponse:
        """Generate mock response."""
        self.call_count += 1
        
        return MockLLMResponse(
            content="Mock HF response: " + messages[-1].content[:50],
            model=self.model,
            usage={"prompt_tokens": 5, "completion_tokens": 5}
        )
    
    def health_check(self) -> bool:
        """Mock health check."""
        return True


class MockOpenAIProvider:
    """Mock OpenAI provider for testing."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        self.model = model
        self.api_key = kwargs.get('api_key', 'mock-key')
        self.call_count = 0
    
    def generate(self, messages: List[MockLLMMessage], **kwargs) -> MockLLMResponse:
        """Generate mock response."""
        self.call_count += 1
        
        # Simulate function calling if tools are provided
        tools = kwargs.get('tools', [])
        if tools:
            return MockLLMResponse(
                content="",
                model=self.model,
                usage={"prompt_tokens": 20, "completion_tokens": 30},
                metadata={
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "function": {
                                "name": tools[0]["name"],
                                "arguments": json.dumps({"location": "St. Louis"})
                            }
                        }
                    ]
                }
            )
        
        return MockLLMResponse(
            content="Mock OpenAI response",
            model=self.model,
            usage={"prompt_tokens": 10, "completion_tokens": 10}
        )
    
    def health_check(self) -> bool:
        """Mock health check."""
        return True


class MockLLMManager:
    """Mock LLM Manager for testing."""
    
    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self.default_provider: Optional[str] = None
        self.call_history: List[Dict] = []
    
    def register_provider(self, name: str, provider: Any):
        """Register a provider."""
        self.providers[name] = provider
        if self.default_provider is None:
            self.default_provider = name
    
    def set_default_provider(self, name: str):
        """Set default provider."""
        if name in self.providers:
            self.default_provider = name
    
    def generate(self, messages: List[MockLLMMessage], provider: str = None, **kwargs) -> MockLLMResponse:
        """Generate using specified or default provider."""
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        provider_instance = self.providers[provider_name]
        response = provider_instance.generate(messages, **kwargs)
        
        self.call_history.append({
            'provider': provider_name,
            'messages': [m.to_dict() for m in messages],
            'response': response.content,
            'timestamp': datetime.now().isoformat()
        })
        
        return response
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about all providers."""
        return {
            name: provider.get_model_info() if hasattr(provider, 'get_model_info') else {}
            for name, provider in self.providers.items()
        }


# pytest fixture for mock LLM manager
import pytest

@pytest.fixture
def mock_llm_manager():
    """Create mock LLM manager with pre-configured providers."""
    manager = MockLLMManager()
    
    # Register mock Ollama provider
    mock_ollama = MockOllamaProvider()
    mock_ollama.set_responses([
        json.dumps({"action": "assess_vulnerability", "county": "St. Louis", "confidence": 0.95}),
        json.dumps({"action": "get_weather", "location": "Missouri"}),
        "This is a general response about disaster resilience.",
        json.dumps({"action": "analyze_risk", "risk_level": "high", "factors": ["flood", "tornado"]})
    ])
    
    manager.register_provider("mock_ollama", mock_ollama)
    manager.set_default_provider("mock_ollama")
    
    return manager


@pytest.fixture
def mock_ollama_provider():
    """Create a standalone mock Ollama provider."""
    provider = MockOllamaProvider()
    provider.set_responses([
        "Test response 1",
        "Test response 2",
        json.dumps({"action": "test", "value": 123})
    ])
    return provider
