# ResilienceAI Local LLM Integration

A plug-and-play local LLM integration supporting multiple providers: **Ollama**, **LM Studio**, **Hugging Face Transformers**, and **llama.cpp**.

## Quick Start

```python
from llm_interface import LLMManager, LLMConfig, LLMMessage
import llm_providers  # Registers all providers

async def main():
    # Create manager with your preferred provider
    config = LLMConfig(provider="ollama", model="mistral:7b")
    manager = LLMManager(config)
    
    # Initialize with auto-detection and fallback
    if await manager.initialize():
        # Generate response
        messages = [
            LLMMessage(role="system", content="You are helpful."),
            LLMMessage(role="user", content="What is resilience engineering?")
        ]
        response = await manager.generate(messages)
        print(response.content)
    
    await manager.close()

asyncio.run(main())
```

## Providers

### 1. Ollama (Default, Recommended)

Easiest setup for local LLMs.

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Run a model
ollama run mistral:7b
```

```python
config = LLMConfig(
    provider="ollama",
    model="mistral:7b",  # or llama2, codellama, etc.
    temperature=0.7
)
```

### 2. LM Studio (OpenAI-compatible)

GUI-based with OpenAI-compatible API.

```python
config = LLMConfig(
    provider="lmstudio",
    base_url="http://localhost:1234/v1",
    temperature=0.8
)
```

### 3. Hugging Face Transformers

Direct Python model loading.

```bash
pip install transformers torch
```

```python
config = LLMConfig(
    provider="huggingface",
    model="microsoft/DialoGPT-medium",
    device="cuda"  # or "cpu"
)
```

### 4. llama.cpp (GGUF, Edge Deployment)

Optimized for edge devices.

```bash
pip install llama-cpp-python
```

```python
config = LLMConfig(
    provider="llamacpp",
    model="path/to/model.gguf",
    context_window=4096
)
```

## Features

### Auto-Detection & Fallback

```python
manager = LLMManager(LLMConfig(provider="ollama"))

# Try Ollama first, fallback to LM Studio, then Hugging Face
success = await manager.initialize(
    fallback_chain=["ollama", "lmstudio", "huggingface"]
)
```

### Insight Generation

```python
# Generate insights from structured data
metrics = {"cpu": 85.5, "memory": 92.3}

insight = await manager.generate_insight(
    data=metrics,
    context="Server performance metrics",
    insight_type="analysis"  # or "alert", "recommendation", "summary"
)
```

### Response Crafting

```python
# Craft human-readable responses from agent outputs
agent_output = {
    "incident_id": "INC-001",
    "severity": "high",
    "affected_services": ["api-gateway"]
}

response = await manager.craft_response(
    agent_output=agent_output,
    tone="professional",  # or "casual", "urgent", "empathetic"
    audience="executive"  # or "technical", "general"
)
```

### Streaming

```python
stream = await manager.generate(messages, stream=True)

async for chunk in stream:
    print(chunk, end="", flush=True)
```

## File Structure

```
ResilienceAI/src/
├── llm_interface.py           # Abstract interface & manager
├── llm_providers/
│   ├── __init__.py           # Auto-registers providers
│   ├── ollama.py             # Ollama provider
│   ├── lmstudio.py           # LM Studio provider
│   ├── huggingface.py        # Hugging Face provider
│   └── llamacpp.py           # llama.cpp provider
└── llm_example.py            # Usage examples

ResilienceAI/tests/
└── test_llm_integration.py   # Test suite
```

## Configuration

### Via Code

```python
config = LLMConfig(
    provider="ollama",
    model="mistral:7b",
    temperature=0.7,
    max_tokens=512,
    top_p=0.9,
    base_url="http://localhost:11434",  # Provider-specific
    device="cuda"  # For Hugging Face
)
```

### Via Environment Variables

```bash
export RESILIENCE_LLM_PROVIDER=ollama
export RESILIENCE_LLM_MODEL=mistral:7b
export RESILIENCE_LLM_TEMPERATURE=0.7
export RESILIENCE_LLM_BASE_URL=http://localhost:11434
```

## Testing

```bash
cd /root/.openclaw/workspace/ResilienceAI
pytest tests/test_llm_integration.py -v
```

## Requirements

- Python 3.8+
- `aiohttp` (for HTTP-based providers)
- Provider-specific dependencies:
  - Ollama: None (external service)
  - LM Studio: None (external service)
  - Hugging Face: `transformers`, `torch`
  - llama.cpp: `llama-cpp-python`

## Architecture

```
┌─────────────────────────────────────────┐
│           LLMManager                    │
│  (High-level operations, auto-detect)   │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────────┐
│ Ollama  │   │LM Studio│   │Hugging Face │
│Provider │   │Provider │   │  Provider   │
└─────────┘   └─────────┘   └─────────────┘
    │               │               │
    └───────────────┴───────────────┘
                    │
           ┌────────┴────────┐
           │  BaseLLMProvider │
           │  (Abstract Base) │
           └─────────────────┘
```

## License

MIT
