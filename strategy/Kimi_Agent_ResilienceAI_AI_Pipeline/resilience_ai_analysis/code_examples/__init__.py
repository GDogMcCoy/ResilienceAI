"""
ResilienceAI Backend Enhancement Package

This package provides comprehensive backend enhancements for the ResilienceAI
multi-agent MCP system, including:

- Async tool execution
- Multi-agent orchestration
- LLM provider abstraction
- Agent memory management
- Tool versioning and deprecation
- Performance monitoring
- API layer
"""

__version__ = "2.0.0"

from .agents.base import BaseAgent, AgentContext, AgentOutput, AgentStatus, ToolResult
from .llm.base import LLMManager, LLMConfig, LLMMessage, LLMResponse
from .execution.async_executor import AsyncExecutor
from .tools.tool_registry import ToolRegistry, tool
from .orchestration.supervisor import AgentSupervisor
from .memory.base import MemoryManager

__all__ = [
    "BaseAgent",
    "AgentContext",
    "AgentOutput",
    "AgentStatus",
    "ToolResult",
    "LLMManager",
    "LLMConfig",
    "LLMMessage",
    "LLMResponse",
    "AsyncExecutor",
    "ToolRegistry",
    "tool",
    "AgentSupervisor",
    "MemoryManager",
]
