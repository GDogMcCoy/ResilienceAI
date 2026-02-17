"""
ResilienceAI - Base Agent
Abstract base class for all specialized agents with Archia integration.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ToolResult:
    """Result from tool execution."""
    tool_name: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentOutput:
    """Output from agent execution."""
    agent_name: str
    status: AgentStatus
    results: List[ToolResult] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    error: Optional[str] = None


class BaseAgent(ABC):
    """Abstract base for a specialized ResilienceAI agent with full MCP support."""

    # Agent metadata
    name: str = "base_agent"
    description: str = "Base agent class"
    version: str = "1.0.0"
    
    # Intent classification keywords for routing
    intent_keywords: List[str] = []
    
    # Tools owned by this agent
    owned_tools: set = set()

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

    def __init__(self):
        """Initialize the agent."""
        self._tool_handlers: Dict[str, Callable] = {}
        self._register_tool_handlers()
        self._execution_history: List[Dict] = []

    def _register_tool_handlers(self) -> None:
        """Register tool handler methods. Override in subclasses."""
        pass

    def get_tool_names(self) -> List[str]:
        """Return list of tool names owned by this agent."""
        return [t["name"] for t in self.get_tools()]

    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Return tool schemas indexed by name."""
        return {t["name"]: t for t in self.get_tools()}

    def can_handle_tool(self, tool_name: str) -> bool:
        """Check if this agent can handle a specific tool."""
        return tool_name in self.get_tool_names()

    def calculate_intent_match(self, query: str) -> float:
        """Calculate intent match score (0-1) for a query."""
        if not self.intent_keywords:
            return 0.0
        
        query_lower = query.lower()
        matches = sum(1 for kw in self.intent_keywords if kw.lower() in query_lower)
        
        # Normalize by keyword count but cap at 1.0
        # Use a sigmoid-like curve for better discrimination
        import math
        raw_score = matches / max(len(self.intent_keywords) * 0.3, 1.0)
        return min(1.0, raw_score)

    def execute(self, tools: List[Dict[str, Any]], context: Dict[str, Any] = None) -> AgentOutput:
        """
        Execute multiple tools and return aggregated output.
        
        Args:
            tools: List of {"name": str, "params": dict} to execute
            context: Additional execution context
            
        Returns:
            AgentOutput with results and insights
        """
        start_time = time.time()
        results = []
        insights = []
        
        for tool_spec in tools:
            tool_name = tool_spec.get("name")
            params = tool_spec.get("params", {})
            
            tool_start = time.time()
            try:
                data = self.execute_tool(tool_name, params)
                success = "error" not in data
                error = data.get("error") if not success else None
                
                # Extract insights from result
                if success and isinstance(data, dict):
                    insight = self._extract_insight(tool_name, data)
                    if insight:
                        insights.append(insight)
                
                results.append(ToolResult(
                    tool_name=tool_name,
                    success=success,
                    data=data if success else None,
                    error=error,
                    execution_time_ms=(time.time() - tool_start) * 1000
                ))
            except Exception as e:
                results.append(ToolResult(
                    tool_name=tool_name,
                    success=False,
                    error=str(e),
                    execution_time_ms=(time.time() - tool_start) * 1000
                ))
        
        execution_time = (time.time() - start_time) * 1000
        
        # Calculate overall confidence based on success rate
        success_rate = sum(1 for r in results if r.success) / max(len(results), 1)
        
        return AgentOutput(
            agent_name=self.name,
            status=AgentStatus.COMPLETED if success_rate > 0.5 else AgentStatus.FAILED,
            results=results,
            insights=insights,
            confidence=success_rate,
            execution_time_ms=execution_time
        )

    def _extract_insight(self, tool_name: str, data: Dict[str, Any]) -> Optional[str]:
        """Extract a key insight from tool result. Override for custom insights."""
        return None

    def get_archia_config(self) -> Dict[str, Any]:
        """Export agent config in Archia-compatible format."""
        return {
            "agent": {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "system_prompt": self.system_prompt,
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

    def get_health(self) -> Dict[str, Any]:
        """Get agent health status."""
        return {
            "agent": self.name,
            "status": "healthy",
            "tool_count": len(self.get_tools()),
            "version": self.version,
            "last_error": self._execution_history[-1].get("error") if self._execution_history else None
        }

    def _log_execution(self, tool_name: str, params: Dict, result: Dict, duration_ms: float) -> None:
        """Log tool execution for monitoring."""
        self._execution_history.append({
            "timestamp": time.time(),
            "tool": tool_name,
            "params": params,
            "success": "error" not in result,
            "duration_ms": duration_ms
        })
        # Keep only last 100 executions
        self._execution_history = self._execution_history[-100:]
