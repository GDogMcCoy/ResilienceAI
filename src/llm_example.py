"""
Example usage and configuration for ResilienceAI LLM Integration.

This file demonstrates how to use the plug-and-play LLM system.
"""

import asyncio
from llm_interface import (
    LLMManager, LLMConfig, LLMMessage,
    quick_generate
)

# Import providers to register them
import llm_providers


async def example_basic_usage():
    """Basic usage with auto-detection."""
    
    # Create manager with default config (Ollama)
    manager = LLMManager()
    
    # Initialize with auto-detection and fallback
    success = await manager.initialize()
    
    if not success:
        print("No LLM providers available!")
        return
    
    print(f"Using provider: {manager.provider_name}")
    
    # Generate a response
    messages = [
        LLMMessage(role="system", content="You are a helpful assistant."),
        LLMMessage(role="user", content="What is resilience engineering?")
    ]
    
    response = await manager.generate(messages)
    print(f"Response: {response.content}")
    
    await manager.close()


async def example_specific_provider():
    """Use a specific provider."""
    
    # Configure for LM Studio
    config = LLMConfig(
        provider="lmstudio",
        model="local-model",
        temperature=0.8,
        base_url="http://localhost:1234/v1"
    )
    
    manager = LLMManager(config)
    
    if await manager.initialize():
        messages = [LLMMessage(role="user", content="Hello!")]
        response = await manager.generate(messages)
        print(response.content)
    
    await manager.close()


async def example_ollama():
    """Use Ollama (default)."""
    
    config = LLMConfig(
        provider="ollama",
        model="mistral:7b",
        temperature=0.7
    )
    
    manager = LLMManager(config)
    
    if await manager.initialize():
        messages = [LLMMessage(role="user", content="Explain system resilience.")]
        response = await manager.generate(messages)
        print(response.content)
    
    await manager.close()


async def example_huggingface():
    """Use Hugging Face Transformers."""
    
    config = LLMConfig(
        provider="huggingface",
        model="microsoft/DialoGPT-medium",
        device="cuda"  # or "cpu"
    )
    
    manager = LLMManager(config)
    
    if await manager.initialize():
        messages = [LLMMessage(role="user", content="Hi there!")]
        response = await manager.generate(messages)
        print(response.content)
    
    await manager.close()


async def example_llamacpp():
    """Use llama.cpp with GGUF model."""
    
    config = LLMConfig(
        provider="llamacpp",
        model="models/mistral-7b-instruct.gguf",
        temperature=0.7,
        context_window=4096
    )
    
    manager = LLMManager(config)
    
    if await manager.initialize():
        messages = [LLMMessage(role="user", content="What is chaos engineering?")]
        response = await manager.generate(messages)
        print(response.content)
    
    await manager.close()


async def example_insight_generation():
    """Generate insights from structured data."""
    
    manager = LLMManager()
    
    if await manager.initialize():
        # System metrics data
        metrics = {
            "cpu_percent": 85.5,
            "memory_percent": 92.3,
            "disk_io": {"read_mb": 150, "write_mb": 200},
            "network_io": {"rx_mb": 50, "tx_mb": 75}
        }
        
        # Generate analysis insight
        insight = await manager.generate_insight(
            data=metrics,
            context="Server performance metrics from production environment",
            insight_type="analysis"
        )
        print("Analysis:", insight)
        
        # Generate alert if needed
        alert = await manager.generate_insight(
            data=metrics,
            context="Check for critical issues",
            insight_type="alert"
        )
        print("Alert check:", alert)
        
        # Get recommendations
        recommendations = await manager.generate_insight(
            data=metrics,
            context="High resource usage detected",
            insight_type="recommendation"
        )
        print("Recommendations:", recommendations)
    
    await manager.close()


async def example_response_crafting():
    """Craft human-readable responses from agent outputs."""
    
    manager = LLMManager()
    
    if await manager.initialize():
        # Raw agent output
        agent_output = {
            "incident_id": "INC-2024-001",
            "severity": "high",
            "affected_services": ["api-gateway", "user-service"],
            "root_cause": "database_connection_pool_exhaustion",
            "estimated_resolution": "30 minutes",
            "actions_taken": [
                "increased_connection pool size",
                "restarted affected services"
            ]
        }
        
        # Craft professional response for executives
        executive_response = await manager.craft_response(
            agent_output=agent_output,
            tone="professional",
            audience="executive"
        )
        print("Executive summary:", executive_response)
        
        # Craft technical response for engineers
        technical_response = await manager.craft_response(
            agent_output=agent_output,
            tone="technical",
            audience="technical"
        )
        print("Technical details:", technical_response)
    
    await manager.close()


async def example_streaming():
    """Stream responses for real-time output."""
    
    manager = LLMManager()
    
    if await manager.initialize():
        messages = [LLMMessage(role="user", content="Tell me a story about resilience.")]
        
        # Stream the response
        stream = await manager.generate(messages, stream=True)
        
        print("Streaming response: ", end="", flush=True)
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()
    
    await manager.close()


async def example_quick_generate():
    """Quick one-off generation without managing state."""
    
    # Simple one-time generation
    response = await quick_generate(
        prompt="What is the CAP theorem?",
        provider="ollama",
        model="mistral:7b"
    )
    print(response)
    
    # With system prompt
    response = await quick_generate(
        prompt="Explain microservices",
        provider="ollama",
        system="You are a cloud architecture expert. Be concise."
    )
    print(response)


async def example_health_check():
    """Check provider health status."""
    
    manager = LLMManager()
    
    if await manager.initialize():
        health = await manager.health_check()
        print(f"Health status: {health}")
    
    await manager.close()


async def example_fallback_chain():
    """Configure custom fallback chain."""
    
    # Try Ollama first, then LM Studio, then Hugging Face
    manager = LLMManager(LLMConfig(provider="ollama"))
    
    success = await manager.initialize(
        fallback_chain=["ollama", "lmstudio", "huggingface"]
    )
    
    if success:
        print(f"Connected to: {manager.provider_name}")
        
        messages = [LLMMessage(role="user", content="Hello!")]
        response = await manager.generate(messages)
        print(response.content)
    else:
        print("No providers available in fallback chain")
    
    await manager.close()


# Configuration examples
CONFIG_EXAMPLES = """
# ============================================
# Configuration Examples
# ============================================

# 1. Ollama (Recommended, easiest setup)
# Install: curl -fsSL https://ollama.com/install.sh | sh
# Run: ollama run mistral:7b
config = LLMConfig(
    provider="ollama",
    model="mistral:7b",  # or llama2:13b, codellama, etc.
    temperature=0.7
)

# 2. LM Studio (GUI-based, OpenAI-compatible)
# Download: https://lmstudio.ai/
# Load model and start server on port 1234
config = LLMConfig(
    provider="lmstudio",
    base_url="http://localhost:1234/v1",
    temperature=0.8
)

# 3. Hugging Face Transformers (Python library)
# Install: pip install transformers torch
config = LLMConfig(
    provider="huggingface",
    model="microsoft/DialoGPT-medium",
    device="cuda"  # or "cpu"
)

# 4. llama.cpp (GGUF models, edge deployment)
# Install: pip install llama-cpp-python
# Download GGUF model from Hugging Face
config = LLMConfig(
    provider="llamacpp",
    model="path/to/model.gguf",
    context_window=4096
)

# ============================================
# Environment Variables
# ============================================

# You can also use environment variables:
# RESILIENCE_LLM_PROVIDER=ollama
# RESILIENCE_LLM_MODEL=mistral:7b
# RESILIENCE_LLM_TEMPERATURE=0.7
# RESILIENCE_LLM_BASE_URL=http://localhost:11434

# ============================================
# Docker Compose Example
# ============================================

# services:
#   resilience-ai:
#     build: .
#     environment:
#       - RESILIENCE_LLM_PROVIDER=ollama
#       - RESILIENCE_LLM_MODEL=mistral:7b
#   
#   ollama:
#     image: ollama/ollama
#     volumes:
#       - ollama:/root/.ollama
#     ports:
#       - "11434:11434"

"""


if __name__ == "__main__":
    print(CONFIG_EXAMPLES)
    
    # Run examples
    print("\n" + "="*50)
    print("Running examples...")
    print("="*50 + "\n")
    
    # Uncomment to run specific examples:
    # asyncio.run(example_basic_usage())
    # asyncio.run(example_insight_generation())
    # asyncio.run(example_response_crafting())
    # asyncio.run(example_quick_generate())
    
    print("Examples defined. Uncomment the ones you want to run.")
