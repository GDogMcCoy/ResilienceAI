"""
ResilienceAI - Base Agent
Abstract base class for all specialized agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseAgent(ABC):
    """Abstract base for a specialized ResilienceAI agent."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of this agent's role."""
        ...

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt for LLM-based interaction."""
        ...

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions owned by this agent."""
        ...

    @abstractmethod
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given parameters."""
        ...

    def get_tool_names(self) -> List[str]:
        """Return list of tool names owned by this agent."""
        return [t["name"] for t in self.get_tools()]

    def get_archia_config(self) -> Dict[str, Any]:
        """Export agent config in Archia-compatible format."""
        return {
            "agent": {
                "name": self.name,
                "description": self.description,
                "tools": [
                    {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "handler": f"{self.__class__.__name__}.{t['name']}",
                        "parameters": t.get("parameters", {}),
                    }
                    for t in self.get_tools()
                ]
            }
        }
