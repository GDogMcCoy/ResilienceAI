"""
ResilienceAI - Enhanced Base Agent
Abstract base class for all specialized agents with full MCP support.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, AsyncIterator, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import uuid
import time

if TYPE_CHECKING:
    from ..memory.base import MemoryManager
    from ..llm.base import LLMManager
    from ..tools.tool_registry import ToolRegistry
    from ..core.events import EventBus
    from ..core.metrics import MetricsCollector


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class AgentCapability(Enum):
    """Agent capabilities for routing."""
    VULNERABILITY_ANALYSIS = "vulnerability_analysis"
    CLIMATE_RISK = "climate_risk"
    REALTIME_MONITORING = "realtime_monitoring"
    STRATEGIC_PLANNING = "strategic_planning"
    EXECUTIVE_BRIEFING = "executive_briefing"
    DATA_QUERY = "data_query"
    SCENARIO_SIMULATION = "scenario_simulation"
    AGRICULTURAL_ANALYSIS = "agricultural_analysis"
    HEALTH_DISPARITY = "health_disparity"


@dataclass
class ToolResult:
    """Enhanced tool execution result."""
    tool_name: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    cached: bool = False
    retry_count: int = 0
    tool_version: str = "1.0.0"


@dataclass
class AgentContext:
    """Agent execution context."""
    session_id: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentOutput:
    """Enhanced agent output."""
    agent_name: str
    agent_id: str
    status: AgentStatus
    results: List[ToolResult] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    context: Optional[AgentContext] = None
    subtask_outputs: List['AgentOutput'] = field(default_factory=list)
    tokens_used: Dict[str, int] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Enhanced abstract base for ResilienceAI agents.
    
    Features:
    - Async tool execution
    - Tool chaining support
    - Memory integration
    - Event emission
    - Performance monitoring
    """
    
    # Agent metadata
    name: str = "base_agent"
    description: str = "Base agent class"
    version: str = "1.0.0"
    capabilities: List[AgentCapability] = []
    
    # Intent classification keywords for routing
    intent_keywords: List[str] = []
    intent_patterns: List[str] = []
    
    # Tools owned by this agent
    owned_tools: set = set()
    tool_dependencies: Dict[str, List[str]] = {}
    
    def __init__(
        self,
        memory_manager: Optional['MemoryManager'] = None,
        llm_manager: Optional['LLMManager'] = None,
        tool_registry: Optional['ToolRegistry'] = None,
        event_bus: Optional['EventBus'] = None,
        metrics_collector: Optional['MetricsCollector'] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = str(uuid.uuid4())
        self.status = AgentStatus.IDLE
        self.memory_manager = memory_manager
        self.llm_manager = llm_manager
        self.tool_registry = tool_registry
        self.event_bus = event_bus
        self.metrics_collector = metrics_collector
        self.config = config or {}
        
        # Execution tracking
        self._current_tasks: Dict[str, asyncio.Task] = {}
        self._execution_history: List[Dict[str, Any]] = []
        
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt for LLM-based interaction."""
        pass
    
    @abstractmethod
    async def execute(
        self,
        query: str,
        context: Optional[AgentContext] = None,
        tools: Optional[List[str]] = None
    ) -> AgentOutput:
        """
        Execute agent with given query.
        
        Args:
            query: Natural language query
            context: Execution context
            tools: Specific tools to use (None = all available)
            
        Returns:
            AgentOutput with results
        """
        pass
    
    async def execute_stream(
        self,
        query: str,
        context: Optional[AgentContext] = None
    ) -> AsyncIterator[str]:
        """
        Stream agent execution results.
        
        Yields:
            Chunks of the response as they're generated
        """
        output = await self.execute(query, context)
        yield output.insights[0] if output.insights else ""
    
    async def can_handle(self, query: str, intent_score: float = 0.0) -> float:
        """
        Determine if this agent can handle the query.
        
        Args:
            query: Natural language query
            intent_score: Pre-computed intent score
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        if intent_score > 0:
            return intent_score
            
        query_lower = query.lower()
        
        # Keyword matching
        keyword_matches = sum(1 for kw in self.intent_keywords if kw in query_lower)
        keyword_score = min(keyword_matches / max(len(self.intent_keywords), 1), 1.0)
        
        # Pattern matching
        import re
        pattern_matches = sum(
            1 for pattern in self.intent_patterns 
            if re.search(pattern, query_lower)
        )
        pattern_score = min(pattern_matches / max(len(self.intent_patterns), 1), 1.0)
        
        # LLM-based classification (if available)
        llm_score = await self._llm_classify(query)
        
        # Weighted combination
        return 0.4 * keyword_score + 0.3 * pattern_score + 0.3 * llm_score
    
    async def _llm_classify(self, query: str) -> float:
        """Use LLM to classify query relevance."""
        if not self.llm_manager:
            return 0.0
            
        from ..llm.base import LLMMessage
        
        prompt = f"""Rate how relevant this query is for a {self.name} agent (0-10):
Query: {query}
Agent capabilities: {[c.value for c in self.capabilities]}

Respond with only a number."""
        
        try:
            messages = [LLMMessage(role="user", content=prompt)]
            response = await self.llm_manager.generate(messages)
            score = float(response.content.strip()) / 10.0
            return max(0.0, min(1.0, score))
        except:
            return 0.0
    
    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: Optional[AgentContext] = None,
        use_cache: bool = True
    ) -> ToolResult:
        """
        Execute a single tool with retry and caching.
        
        Args:
            tool_name: Name of the tool to execute
            params: Tool parameters
            context: Execution context
            use_cache: Whether to use caching
            
        Returns:
            ToolResult
        """
        if not self.tool_registry:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error="Tool registry not available"
            )
        
        start_time = time.time()
        
        # Check cache if enabled
        if use_cache:
            cached = await self._check_cache(tool_name, params)
            if cached:
                cached.execution_time_ms = (time.time() - start_time) * 1000
                cached.cached = True
                return cached
        
        # Execute with retry
        result = await self._execute_with_retry(tool_name, params)
        result.execution_time_ms = (time.time() - start_time) * 1000
        
        # Cache result if successful
        if result.success and use_cache:
            await self._cache_result(tool_name, params, result)
        
        # Emit event
        if self.event_bus:
            await self.event_bus.emit("tool_executed", {
                "tool_name": tool_name,
                "success": result.success,
                "execution_time_ms": result.execution_time_ms,
                "agent_id": self.agent_id
            })
        
        # Record metrics
        if self.metrics_collector:
            self.metrics_collector.record_tool_execution(
                tool_name=tool_name,
                success=result.success,
                duration_ms=result.execution_time_ms
            )
        
        return result
    
    async def execute_tool_chain(
        self,
        chain: List[Dict[str, Any]],
        context: Optional[AgentContext] = None
    ) -> List[ToolResult]:
        """
        Execute a chain of tools with data flow between them.
        
        Args:
            chain: List of {tool_name, params, output_mapping}
            context: Execution context
            
        Returns:
            List of ToolResults
        """
        results = []
        shared_data = {}
        
        for step in chain:
            tool_name = step["tool_name"]
            params = step.get("params", {}).copy()
            
            # Inject data from previous steps
            for key, source in step.get("input_mapping", {}).items():
                if source in shared_data:
                    params[key] = shared_data[source]
            
            # Execute tool
            result = await self.execute_tool(tool_name, params, context)
            results.append(result)
            
            if not result.success:
                if step.get("required", True):
                    break
                continue
            
            # Map outputs for next steps
            for key, target in step.get("output_mapping", {}).items():
                if isinstance(result.data, dict) and key in result.data:
                    shared_data[target] = result.data[key]
        
        return results
    
    async def _execute_with_retry(
        self,
        tool_name: str,
        params: Dict[str, Any],
        max_retries: int = 3
    ) -> ToolResult:
        """Execute tool with exponential backoff retry."""
        from tenacity import retry, stop_after_attempt, wait_exponential
        
        @retry(stop=stop_after_attempt(max_retries), 
               wait=wait_exponential(multiplier=1, min=4, max=10))
        async def _execute():
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Tool {tool_name} not found")
            
            if asyncio.iscoroutinefunction(tool):
                return await tool(**params)
            else:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: tool(**params))
        
        try:
            data = await _execute()
            return ToolResult(
                tool_name=tool_name,
                success=True,
                data=data,
                retry_count=max_retries - 1
            )
        except Exception as e:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=str(e),
                retry_count=max_retries
            )
    
    async def _check_cache(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Optional[ToolResult]:
        """Check if result is cached."""
        # Implementation depends on cache backend
        return None
    
    async def _cache_result(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: ToolResult
    ) -> None:
        """Cache tool result."""
        # Implementation depends on cache backend
        pass
    
    async def get_memory(self, key: str) -> Any:
        """Retrieve from agent memory."""
        if self.memory_manager:
            return await self.memory_manager.get(key)
        return None
    
    async def set_memory(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store in agent memory."""
        if self.memory_manager:
            await self.memory_manager.set(key, value, ttl)
    
    def cancel(self) -> None:
        """Cancel current execution."""
        for task_id, task in self._current_tasks.items():
            if not task.done():
                task.cancel()
        self.status = AgentStatus.CANCELLED
