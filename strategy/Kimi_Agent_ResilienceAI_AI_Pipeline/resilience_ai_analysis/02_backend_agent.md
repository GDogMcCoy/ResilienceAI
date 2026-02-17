# ResilienceAI Backend & MCP Agent Enhancement Design

## Executive Summary

This document provides a comprehensive analysis of the ResilienceAI agent architecture and proposes advanced backend enhancements for a production-ready multi-agent MCP system. The current system has 45+ MCP tools with basic orchestration; this design introduces async processing, advanced tool chaining, LLM provider abstraction, agent memory, and auto-scaling capabilities.

---

## 1. Current Architecture Analysis

### 1.1 Existing Components

```
ResilienceAI/claw-autonomous
├── src/
│   ├── agent.py                    # Main ResilienceAgent with 45+ MCP tools
│   ├── agent_orchestrator.py       # Basic orchestration layer
│   ├── agents/
│   │   ├── base_agent.py           # Abstract base class
│   │   ├── climate_agent.py        # Climate-specific agent
│   │   ├── planning_agent.py       # Planning agent
│   │   ├── realtime_agent.py       # Real-time monitoring agent
│   │   ├── vulnerability_agent.py  # Vulnerability analysis agent
│   │   ├── orchestrator.py         # Multi-agent orchestrator
│   │   └── langgraph_flow.py       # LangGraph workflow integration
│   ├── llm_providers/              # LLM provider implementations
│   │   ├── ollama.py
│   │   ├── lmstudio.py
│   │   ├── huggingface.py
│   │   └── llamacpp.py
│   └── [45+ tool modules]
```

### 1.2 Current Agent Architecture Patterns

**ResilienceAgent (src/agent.py)**
- Single monolithic agent with 45+ tools
- Synchronous tool execution
- Basic intent parsing via keyword matching
- Direct pandas DataFrame operations
- Tool result formatting with `_format_and_improve()`

**AgentOrchestrator (src/agent_orchestrator.py)**
- Tool-based architecture with `ToolResult` dataclass
- API-free tool integrations (NOAA, USGS, Nominatim)
- Intent parsing with keyword extraction
- Response crafting from tool results
- Hyperdimensional insight generation

**BaseAgent (src/agents/base_agent.py)**
- Abstract base class for specialized agents
- `AgentStatus` enum for execution tracking
- `ToolResult` and `AgentOutput` dataclasses
- Intent keyword routing
- Tool ownership model

### 1.3 Current Limitations

1. **Synchronous Execution**: All tools execute synchronously, blocking the main thread
2. **No Tool Chaining**: Tools cannot be composed into workflows
3. **Limited Error Handling**: Basic try/except without retry logic
4. **No Caching**: Repeated identical queries recompute results
5. **Single Agent**: No true multi-agent collaboration
6. **No Memory**: Context is lost between queries
7. **No LLM Integration**: Missing LLM-based intent parsing and response generation
8. **No Monitoring**: No performance metrics or observability

---

## 2. Proposed Multi-Agent System Design

### 2.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESILIENCEAI MULTI-AGENT SYSTEM                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   API Layer  │  │  WebSocket   │  │   GraphQL    │  │   Webhooks   │    │
│  │   (FastAPI)  │  │   Gateway    │  │   Endpoint   │  │   Handler    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         └─────────────────┴─────────────────┴─────────────────┘              │
│                                    │                                         │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐   │
│  │                    AGENT ORCHESTRATION LAYER                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   Router    │  │   Planner   │  │   Memory    │  │   Monitor   │  │   │
│  │  │   Agent     │  │   Agent     │  │   Manager   │  │   Agent     │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │   │
│  │         └─────────────────┴─────────────────┴─────────────────┘        │   │
│  └─────────────────────────────────┬─────────────────────────────────────┘   │
│                                    │                                         │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐   │
│  │                    SPECIALIZED AGENT POOL                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │ Vulnera- │ │ Climate  │ │ Realtime │ │ Planning │ │ Executive│    │   │
│  │  │ bility   │ │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │    │   │
│  │  │  Agent   │ │          │ │          │ │          │ │          │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  └─────────────────────────────────┬─────────────────────────────────────┘   │
│                                    │                                         │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐   │
│  │                      TOOL EXECUTION LAYER                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │  Async   │ │  Tool    │ │  Cache   │ │  Retry   │ │  Tool    │    │   │
│  │  │ Executor │ │  Chain   │ │  Layer   │ │  Engine  │ │ Registry │    │   │
│  │  │ (Celery) │ │  Engine  │ │ (Redis)  │ │          │ │          │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                    INFRASTRUCTURE LAYER                                │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │  LLM     │ │  Vector  │ │  Event   │ │  Metrics │ │  Config  │    │   │
│  │  │ Provider │ │  Store   │ │  Bus     │ │  (Prom.) │ │  Manager │    │   │
│  │  │  Abstr.  │ │(ChromaDB)│ │(RabbitMQ)│ │          │ │          │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Proposed Folder Structure

```
resilienceai_backend/
├── src/
│   ├── agents/                          # Multi-agent system
│   │   ├── __init__.py
│   │   ├── base.py                      # Enhanced BaseAgent
│   │   ├── router.py                    # Intent routing agent
│   │   ├── planner.py                   # Task planning agent
│   │   ├── vulnerability.py             # Vulnerability analysis agent
│   │   ├── climate.py                   # Climate risk agent
│   │   ├── realtime.py                  # Real-time monitoring agent
│   │   ├── planning.py                  # Strategic planning agent
│   │   ├── executive.py                 # Executive briefing agent
│   │   └── memory.py                    # Agent memory manager
│   │
│   ├── core/                            # Core infrastructure
│   │   ├── __init__.py
│   │   ├── config.py                    # Configuration management
│   │   ├── events.py                    # Event bus system
│   │   ├── exceptions.py                # Custom exceptions
│   │   ├── logging.py                   # Structured logging
│   │   └── metrics.py                   # Prometheus metrics
│   │
│   ├── execution/                       # Tool execution layer
│   │   ├── __init__.py
│   │   ├── async_executor.py            # Async task executor
│   │   ├── tool_chain.py                # Tool chaining engine
│   │   ├── tool_registry.py             # Tool registration & discovery
│   │   ├── retry_engine.py              # Retry with backoff
│   │   └── circuit_breaker.py           # Circuit breaker pattern
│   │
│   ├── llm/                             # LLM provider abstraction
│   │   ├── __init__.py
│   │   ├── base.py                      # Base LLM provider
│   │   ├── manager.py                   # LLM manager with fallback
│   │   ├── providers/                   # Provider implementations
│   │   │   ├── __init__.py
│   │   │   ├── archia.py                # Archia Cloud
│   │   │   ├── openai.py                # OpenAI
│   │   │   ├── anthropic.py             # Anthropic
│   │   │   ├── ollama.py                # Ollama (local)
│   │   │   └── azure.py                 # Azure OpenAI
│   │   ├── prompts/                     # Prompt templates
│   │   │   ├── __init__.py
│   │   │   ├── router.j2                # Router prompts
│   │   │   ├── planner.j2               # Planner prompts
│   │   │   └── response.j2              # Response prompts
│   │   └── embeddings.py                # Embedding models
│   │
│   ├── memory/                          # Agent memory system
│   │   ├── __init__.py
│   │   ├── base.py                      # Base memory interface
│   │   ├── short_term.py                # In-memory/conversation
│   │   ├── long_term.py                 # Vector store memory
│   │   ├── entity.py                    # Entity extraction & storage
│   │   └── context.py                   # Context window management
│   │
│   ├── orchestration/                   # Orchestration layer
│   │   ├── __init__.py
│   │   ├── supervisor.py                # Agent supervisor
│   │   ├── workflow.py                  # Workflow definitions
│   │   ├── state_machine.py             # Agent state management
│   │   └── load_balancer.py             # Agent load balancing
│   │
│   ├── tools/                           # Tool definitions
│   │   ├── __init__.py
│   │   ├── definitions/                 # MCP tool definitions
│   │   │   ├── __init__.py
│   │   │   ├── data_query.py            # Data query tools
│   │   │   ├── analysis.py              # Analysis tools
│   │   │   ├── visualization.py         # Visualization tools
│   │   │   ├── export.py                # Export tools
│   │   │   └── alert.py                 # Alert tools
│   │   ├── implementations/             # Tool implementations
│   │   └── versioning.py                # Tool versioning
│   │
│   ├── cache/                           # Caching layer
│   │   ├── __init__.py
│   │   ├── base.py                      # Base cache interface
│   │   ├── redis_cache.py               # Redis implementation
│   │   ├── memory_cache.py              # In-memory cache
│   │   └── strategies.py                # Cache strategies
│   │
│   ├── api/                             # API layer
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI application
│   │   ├── routes/                      # API routes
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                 # Agent endpoints
│   │   │   ├── tools.py                 # Tool endpoints
│   │   │   ├── queries.py               # Query endpoints
│   │   │   ├── health.py                # Health check
│   │   │   └── metrics.py               # Metrics endpoint
│   │   ├── middleware/                  # API middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                  # Authentication
│   │   │   ├── rate_limit.py            # Rate limiting
│   │   │   └── logging.py               # Request logging
│   │   └── models/                      # Pydantic models
│   │       ├── __init__.py
│   │       ├── requests.py              # Request models
│   │       └── responses.py             # Response models
│   │
│   └── workers/                         # Background workers
│       ├── __init__.py
│       ├── celery_app.py                # Celery configuration
│       ├── tasks.py                     # Background tasks
│       └── schedulers.py                # Scheduled jobs
│
├── tests/                               # Test suite
├── docs/                                # Documentation
├── scripts/                             # Utility scripts
├── docker/                              # Docker configurations
├── helm/                                # Kubernetes charts
├── pyproject.toml                       # Project config
├── requirements.txt                     # Dependencies
└── README.md                            # Project readme
```

---

## 3. Core Component Designs

### 3.1 Enhanced BaseAgent Class

```python
# src/agents/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import uuid
import time

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
    
    # Intent classification for routing
    intent_keywords: List[str] = []
    intent_patterns: List[str] = []  # Regex patterns
    
    # Tool ownership
    owned_tools: set = set()
    tool_dependencies: Dict[str, List[str]] = {}  # Tool -> Dependencies
    
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
        # Default implementation - override for true streaming
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
            
        prompt = f"""Rate how relevant this query is for a {self.name} agent (0-10):
Query: {query}
Agent capabilities: {[c.value for c in self.capabilities]}

Respond with only a number."""
        
        try:
            response = await self.llm_manager.generate_simple(prompt)
            score = float(response.strip()) / 10.0
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
                # Chain failed - stop or continue based on config
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
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, tool, **params)
        
        try:
            data = await _execute()
            return ToolResult(
                tool_name=tool_name,
                success=True,
                data=data,
                retry_count=max_retries - 1  # Simplified
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
```

### 3.2 LLM Provider Abstraction Layer

```python
# src/llm/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncIterator, Callable
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

# src/llm/manager.py
from typing import List, Dict, Any, Optional, AsyncIterator
import asyncio
import time

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
        self._lock = asyncio.Lock()
        
    async def initialize(self) -> bool:
        """Initialize all providers."""
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
        from .providers import (
            ArchiaProvider, OpenAIProvider, AnthropicProvider,
            AzureProvider, OllamaProvider
        )
        
        provider_map = {
            LLMProviderType.ARCHIA: ArchiaProvider,
            LLMProviderType.OPENAI: OpenAIProvider,
            LLMProviderType.ANTHROPIC: AnthropicProvider,
            LLMProviderType.AZURE: AzureProvider,
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
            # Shuffle for load balancing
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
```

### 3.3 Agent Memory System

```python
# src/memory/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class MemoryType(Enum):
    """Types of memory storage."""
    SHORT_TERM = "short_term"      # Conversation context
    LONG_TERM = "long_term"        # Persistent knowledge
    EPISODIC = "episodic"          # Specific events/experiences
    SEMANTIC = "semantic"          # Facts and concepts
    PROCEDURAL = "procedural"      # How-to knowledge

@dataclass
class MemoryEntry:
    """Single memory entry."""
    key: str
    value: Any
    memory_type: MemoryType
    created_at: datetime
    accessed_at: Optional[datetime] = None
    access_count: int = 0
    importance: float = 0.5  # 0-1 importance score
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

class BaseMemory(ABC):
    """Abstract base for memory implementations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        ttl: Optional[int] = None,
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> None:
        """Store a memory entry."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memories by semantic similarity."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a memory entry."""
        pass
    
    @abstractmethod
    async def clear(self, memory_type: Optional[MemoryType] = None) -> None:
        """Clear memories."""
        pass

# src/memory/manager.py
from typing import Dict, List, Any, Optional
import hashlib
import json

class MemoryManager:
    """
    Unified memory manager for agents.
    
    Features:
    - Multi-tier memory (short-term, long-term)
    - Vector-based semantic search
    - Automatic memory consolidation
    - Importance-based retention
    """
    
    def __init__(
        self,
        short_term: BaseMemory,
        long_term: BaseMemory,
        embedding_model: Optional[Any] = None,
        max_short_term: int = 100,
        consolidation_threshold: int = 50
    ):
        self.short_term = short_term
        self.long_term = long_term
        self.embedding_model = embedding_model
        self.max_short_term = max_short_term
        self.consolidation_threshold = consolidation_threshold
        
        # Conversation context
        self._conversation_history: List[Dict[str, Any]] = []
        self._current_context: Dict[str, Any] = {}
    
    async def get(
        self,
        key: str,
        check_long_term: bool = True
    ) -> Any:
        """Get value from memory (short-term first, then long-term)."""
        # Check short-term
        entry = await self.short_term.get(key)
        if entry:
            await self._update_access(entry)
            return entry.value
        
        # Check long-term
        if check_long_term:
            entry = await self.long_term.get(key)
            if entry:
                # Promote to short-term
                await self.short_term.set(
                    key, entry.value, MemoryType.SHORT_TERM
                )
                return entry.value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        ttl: Optional[int] = None,
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> None:
        """Store value in memory."""
        # Generate embedding if model available
        embedding = None
        if self.embedding_model:
            embedding = await self._generate_embedding(str(value))
        
        if memory_type == MemoryType.SHORT_TERM:
            await self.short_term.set(
                key, value, memory_type, ttl, importance, tags
            )
            
            # Check if consolidation needed
            await self._maybe_consolidate()
        else:
            await self.long_term.set(
                key, value, memory_type, ttl, importance, tags
            )
    
    async def search_relevant(
        self,
        query: str,
        context: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories."""
        results = []
        
        # Search short-term
        stm_results = await self.short_term.search(query, limit=limit)
        results.extend([{"source": "short_term", "entry": e} for e in stm_results])
        
        # Search long-term
        ltm_results = await self.long_term.search(query, limit=limit)
        results.extend([{"source": "long_term", "entry": e} for e in ltm_results])
        
        # Sort by relevance (simplified)
        results.sort(key=lambda x: x["entry"].importance, reverse=True)
        
        return [
            {
                "key": r["entry"].key,
                "value": r["entry"].value,
                "source": r["source"],
                "importance": r["entry"].importance
            }
            for r in results[:limit]
        ]
    
    async def add_to_conversation(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self._conversation_history.append(message)
        
        # Store in short-term memory
        key = f"conv_{len(self._conversation_history)}"
        await self.short_term.set(
            key, message, MemoryType.EPISODIC, importance=0.7
        )
    
    async def get_conversation_context(
        self,
        window_size: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversation context."""
        return self._conversation_history[-window_size:]
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract and store entities from text."""
        # Simple entity extraction (can be enhanced with NER model)
        entities = []
        
        # County mentions
        import re
        county_pattern = r'(\w+)\s+County'
        counties = re.findall(county_pattern, text, re.IGNORECASE)
        for county in counties:
            entity_key = f"entity_county_{county.lower()}"
            await self.set(
                entity_key,
                {"type": "county", "name": county, "mentions": 1},
                MemoryType.SEMANTIC,
                importance=0.8,
                tags=["entity", "county"]
            )
            entities.append({"type": "county", "name": county})
        
        return entities
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not self.embedding_model:
            return []
        
        # Use embedding model
        return await self.embedding_model.embed(text)
    
    async def _update_access(self, entry: MemoryEntry) -> None:
        """Update access metadata."""
        entry.accessed_at = datetime.utcnow()
        entry.access_count += 1
    
    async def _maybe_consolidate(self) -> None:
        """Consolidate short-term to long-term if needed."""
        # Check short-term size
        # If exceeds threshold, move least important to long-term
        pass
```

### 3.4 Async Tool Execution & Chaining

```python
# src/execution/async_executor.py
import asyncio
from typing import Dict, List, Any, Optional, Callable, Coroutine
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import time

@dataclass
class Task:
    """Async task definition."""
    task_id: str
    coro: Coroutine
    priority: int = 5  # 1-10, lower = higher priority
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None

@dataclass
class TaskResult:
    """Task execution result."""
    task_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0

class AsyncExecutor:
    """
    Async task executor with priority queue and dependency management.
    
    Features:
    - Priority-based execution
    - Dependency resolution
    - Timeout handling
    - Concurrent execution limits
    - Progress tracking
    """
    
    def __init__(
        self,
        max_workers: int = 10,
        max_concurrent: int = 5,
        thread_pool_size: int = 4
    ):
        self.max_workers = max_workers
        self.max_concurrent = max_concurrent
        
        # Task queues
        self._pending: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._running: Dict[str, asyncio.Task] = {}
        self._completed: Dict[str, TaskResult] = {}
        self._failed: Dict[str, TaskResult] = {}
        
        # Thread pool for sync functions
        self._thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)
        
        # Semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # Event for task completion
        self._completion_event = asyncio.Event()
        
    async def submit(
        self,
        task_id: str,
        coro: Coroutine,
        priority: int = 5,
        timeout: Optional[float] = None,
        dependencies: Optional[List[str]] = None,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Submit a task for execution.
        
        Args:
            task_id: Unique task identifier
            coro: Coroutine to execute
            priority: Task priority (1-10)
            timeout: Timeout in seconds
            dependencies: List of task IDs that must complete first
            callback: Callback function on completion
            
        Returns:
            Task ID
        """
        task = Task(
            task_id=task_id,
            coro=coro,
            priority=priority,
            timeout=timeout,
            dependencies=dependencies or [],
            callback=callback
        )
        
        # Add to priority queue (lower priority number = higher priority)
        await self._pending.put((priority, time.time(), task))
        
        return task_id
    
    async def submit_sync(
        self,
        task_id: str,
        func: Callable,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
        priority: int = 5,
        timeout: Optional[float] = None
    ) -> str:
        """Submit a synchronous function for execution."""
        async def wrapper():
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._thread_pool,
                func,
                *args,
                **(kwargs or {})
            )
        
        return await self.submit(task_id, wrapper(), priority, timeout)
    
    async def run(self) -> None:
        """Main execution loop."""
        while True:
            # Get next task
            try:
                _, _, task = await asyncio.wait_for(
                    self._pending.get(),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                continue
            
            # Check dependencies
            if task.dependencies:
                deps_complete = all(
                    dep in self._completed or dep in self._failed
                    for dep in task.dependencies
                )
                if not deps_complete:
                    # Re-queue with same priority
                    await self._pending.put((task.priority, time.time(), task))
                    continue
                
                # Check if any dependency failed
                deps_failed = any(dep in self._failed for dep in task.dependencies)
                if deps_failed:
                    self._failed[task.task_id] = TaskResult(
                        task_id=task.task_id,
                        success=False,
                        error="Dependency failed"
                    )
                    continue
            
            # Execute task
            async with self._semaphore:
                asyncio.create_task(self._execute_task(task))
    
    async def _execute_task(self, task: Task) -> None:
        """Execute a single task."""
        start_time = time.time()
        
        try:
            # Create asyncio task
            asyncio_task = asyncio.create_task(task.coro)
            self._running[task.task_id] = asyncio_task
            
            # Wait with timeout
            if task.timeout:
                result = await asyncio.wait_for(
                    asyncio_task,
                    timeout=task.timeout
                )
            else:
                result = await asyncio_task
            
            execution_time = (time.time() - start_time) * 1000
            
            task_result = TaskResult(
                task_id=task.task_id,
                success=True,
                data=result,
                execution_time_ms=execution_time
            )
            
            self._completed[task.task_id] = task_result
            
        except asyncio.TimeoutError:
            task_result = TaskResult(
                task_id=task.task_id,
                success=False,
                error=f"Timeout after {task.timeout}s"
            )
            self._failed[task.task_id] = task_result
            
        except Exception as e:
            task_result = TaskResult(
                task_id=task.task_id,
                success=False,
                error=str(e)
            )
            self._failed[task.task_id] = task_result
        
        finally:
            if task.task_id in self._running:
                del self._running[task.task_id]
            
            # Call callback if provided
            if task.callback:
                try:
                    task.callback(task_result)
                except Exception as e:
                    print(f"Callback error: {e}")
    
    async def wait_for(
        self,
        task_id: str,
        timeout: Optional[float] = None
    ) -> TaskResult:
        """Wait for a specific task to complete."""
        start = time.time()
        
        while True:
            if task_id in self._completed:
                return self._completed[task_id]
            
            if task_id in self._failed:
                return self._failed[task_id]
            
            if timeout and (time.time() - start) > timeout:
                raise TimeoutError(f"Wait for task {task_id} timed out")
            
            await asyncio.sleep(0.1)
    
    async def wait_for_all(
        self,
        task_ids: Optional[List[str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, TaskResult]:
        """Wait for all tasks to complete."""
        if task_ids is None:
            task_ids = list(self._running.keys())
        
        results = {}
        for task_id in task_ids:
            try:
                results[task_id] = await self.wait_for(task_id, timeout)
            except TimeoutError:
                results[task_id] = TaskResult(
                    task_id=task_id,
                    success=False,
                    error="Wait timeout"
                )
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get executor status."""
        return {
            "pending": self._pending.qsize(),
            "running": len(self._running),
            "completed": len(self._completed),
            "failed": len(self._failed)
        }
    
    async def cancel(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self._running:
            self._running[task_id].cancel()
            return True
        return False
    
    async def shutdown(self) -> None:
        """Shutdown the executor."""
        # Cancel all running tasks
        for task in self._running.values():
            task.cancel()
        
        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True)

# src/execution/tool_chain.py
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import json

@dataclass
class ChainStep:
    """Single step in a tool chain."""
    step_id: str
    tool_name: str
    params: Dict[str, Any] = field(default_factory=dict)
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    condition: Optional[str] = None  # Conditional execution
    required: bool = True
    retry_count: int = 3
    timeout: float = 30.0

@dataclass
class ChainDefinition:
    """Tool chain definition."""
    name: str
    description: str
    steps: List[ChainStep]
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)

class ToolChainEngine:
    """
    Engine for executing tool chains.
    
    Features:
    - Sequential and parallel step execution
    - Data flow between steps
    - Conditional branching
    - Error handling and retry
    - Chain composition
    """
    
    def __init__(
        self,
        tool_registry: 'ToolRegistry',
        executor: AsyncExecutor
    ):
        self.tool_registry = tool_registry
        self.executor = executor
        self._chains: Dict[str, ChainDefinition] = {}
    
    def register_chain(self, chain: ChainDefinition) -> None:
        """Register a tool chain."""
        self._chains[chain.name] = chain
    
    async def execute_chain(
        self,
        chain_name: str,
        initial_params: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a registered chain.
        
        Args:
            chain_name: Name of the chain to execute
            initial_params: Initial parameters
            context: Execution context
            
        Returns:
            Chain execution results
        """
        if chain_name not in self._chains:
            raise ValueError(f"Chain {chain_name} not found")
        
        chain = self._chains[chain_name]
        shared_data = initial_params or {}
        step_results = []
        
        for step in chain.steps:
            # Check condition
            if step.condition:
                if not self._evaluate_condition(step.condition, shared_data):
                    continue
            
            # Prepare parameters with input mapping
            params = step.params.copy()
            for param_key, data_key in step.input_mapping.items():
                if data_key in shared_data:
                    params[param_key] = shared_data[data_key]
            
            # Execute tool
            task_id = f"{chain_name}_{step.step_id}"
            
            async def execute_tool():
                tool = self.tool_registry.get_tool(step.tool_name)
                if asyncio.iscoroutinefunction(tool):
                    return await tool(**params)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, tool, **params)
            
            await self.executor.submit(
                task_id,
                execute_tool(),
                timeout=step.timeout
            )
            
            result = await self.executor.wait_for(task_id)
            step_results.append(result)
            
            if not result.success:
                if step.required:
                    return {
                        "success": False,
                        "failed_step": step.step_id,
                        "error": result.error,
                        "step_results": step_results
                    }
                continue
            
            # Map outputs
            for output_key, data_key in step.output_mapping.items():
                if isinstance(result.data, dict) and output_key in result.data:
                    shared_data[data_key] = result.data[output_key]
        
        return {
            "success": True,
            "data": shared_data,
            "step_results": step_results
        }
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        try:
            # Simple condition evaluation (can be enhanced)
            # Example: "risk_score > 0.7"
            for key, value in data.items():
                condition = condition.replace(key, str(value))
            return eval(condition)
        except:
            return False
    
    def compose_chains(
        self,
        chain_names: List[str],
        new_name: str,
        data_flow: Optional[Dict[str, str]] = None
    ) -> ChainDefinition:
        """
        Compose multiple chains into a new chain.
        
        Args:
            chain_names: Chains to compose
            new_name: Name for the composed chain
            data_flow: Mapping of output->input between chains
            
        Returns:
            Composed chain definition
        """
        all_steps = []
        
        for chain_name in chain_names:
            if chain_name not in self._chains:
                raise ValueError(f"Chain {chain_name} not found")
            
            chain = self._chains[chain_name]
            all_steps.extend(chain.steps)
        
        return ChainDefinition(
            name=new_name,
            description=f"Composed chain: {', '.join(chain_names)}",
            steps=all_steps
        )
```

### 3.5 Agent Router & Orchestrator

```python
# src/orchestration/supervisor.py
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import asyncio

@dataclass
class RoutingDecision:
    """Agent routing decision."""
    agent_name: str
    confidence: float
    reasoning: str
    fallback_agents: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_time_ms: float = 0.0

class AgentSupervisor:
    """
    Supervises multi-agent orchestration.
    
    Features:
    - Intelligent query routing
    - Agent selection with confidence scoring
    - Fallback management
    - Load balancing
    - Performance monitoring
    """
    
    def __init__(
        self,
        agents: Dict[str, BaseAgent],
        llm_manager: Optional['LLMManager'] = None,
        router_agent: Optional['RouterAgent'] = None
    ):
        self.agents = agents
        self.llm_manager = llm_manager
        self.router_agent = router_agent
        
        # Performance tracking
        self._agent_performance: Dict[str, Dict[str, Any]] = {
            name: {"calls": 0, "success": 0, "avg_time_ms": 0}
            for name in agents
        }
        
    async def route(
        self,
        query: str,
        context: Optional[AgentContext] = None,
        require_confidence: float = 0.5
    ) -> RoutingDecision:
        """
        Route query to appropriate agent.
        
        Args:
            query: Natural language query
            context: Execution context
            require_confidence: Minimum confidence threshold
            
        Returns:
            RoutingDecision
        """
        # Get confidence scores from all agents
        agent_scores = await self._get_agent_scores(query)
        
        # Sort by confidence
        sorted_agents = sorted(
            agent_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        if not sorted_agents or sorted_agents[0][1] < require_confidence:
            # No agent confident enough - use LLM router
            if self.router_agent:
                return await self.router_agent.route(query, context)
            
            # Fallback to general agent
            return RoutingDecision(
                agent_name="general",
                confidence=0.0,
                reasoning="No confident agent found, using fallback"
            )
        
        primary_agent = sorted_agents[0][0]
        fallback_agents = [a[0] for a in sorted_agents[1:3]]
        
        return RoutingDecision(
            agent_name=primary_agent,
            confidence=sorted_agents[0][1],
            reasoning=f"Agent {primary_agent} has highest confidence",
            fallback_agents=fallback_agents,
            estimated_cost=self._estimate_cost(primary_agent),
            estimated_time_ms=self._estimate_time(primary_agent)
        )
    
    async def _get_agent_scores(self, query: str) -> Dict[str, float]:
        """Get confidence scores from all agents."""
        scores = {}
        
        # Parallel scoring
        tasks = []
        for name, agent in self.agents.items():
            task = asyncio.create_task(agent.can_handle(query))
            tasks.append((name, task))
        
        for name, task in tasks:
            try:
                scores[name] = await asyncio.wait_for(task, timeout=2.0)
            except:
                scores[name] = 0.0
        
        return scores
    
    async def execute(
        self,
        query: str,
        context: Optional[AgentContext] = None,
        use_fallback: bool = True
    ) -> AgentOutput:
        """
        Execute query with routing and fallback.
        
        Args:
            query: Natural language query
            context: Execution context
            use_fallback: Whether to use fallback agents
            
        Returns:
            AgentOutput
        """
        routing = await self.route(query, context)
        
        # Try primary agent
        primary_agent = self.agents.get(routing.agent_name)
        if not primary_agent:
            return AgentOutput(
                agent_name="supervisor",
                agent_id="supervisor",
                status=AgentStatus.FAILED,
                error=f"Agent {routing.agent_name} not found"
            )
        
        try:
            output = await primary_agent.execute(query, context)
            
            # Update performance metrics
            self._update_performance(routing.agent_name, output)
            
            if output.status == AgentStatus.COMPLETED:
                return output
            
            # Try fallbacks if enabled
            if use_fallback and routing.fallback_agents:
                for fallback_name in routing.fallback_agents:
                    fallback_agent = self.agents.get(fallback_name)
                    if fallback_agent:
                        output = await fallback_agent.execute(query, context)
                        if output.status == AgentStatus.COMPLETED:
                            return output
            
            return output
            
        except Exception as e:
            return AgentOutput(
                agent_name=routing.agent_name,
                agent_id=primary_agent.agent_id,
                status=AgentStatus.FAILED,
                error=str(e)
            )
    
    def _estimate_cost(self, agent_name: str) -> float:
        """Estimate execution cost for agent."""
        # Simplified cost estimation
        return 0.01  # $0.01 per call
    
    def _estimate_time(self, agent_name: str) -> float:
        """Estimate execution time for agent."""
        perf = self._agent_performance.get(agent_name, {})
        return perf.get("avg_time_ms", 1000)
    
    def _update_performance(
        self,
        agent_name: str,
        output: AgentOutput
    ) -> None:
        """Update agent performance metrics."""
        perf = self._agent_performance[agent_name]
        perf["calls"] += 1
        if output.status == AgentStatus.COMPLETED:
            perf["success"] += 1
        
        # Update average time
        if output.execution_time_ms > 0:
            perf["avg_time_ms"] = (
                (perf["avg_time_ms"] * (perf["calls"] - 1) + output.execution_time_ms)
                / perf["calls"]
            )
    
    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all agents."""
        return self._agent_performance.copy()

# src/orchestration/workflow.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class WorkflowStepType(Enum):
    """Types of workflow steps."""
    AGENT = "agent"
    TOOL = "tool"
    CONDITION = "condition"
    PARALLEL = "parallel"
    LOOP = "loop"
    WAIT = "wait"

@dataclass
class WorkflowStep:
    """Single workflow step."""
    step_id: str
    step_type: WorkflowStepType
    config: Dict[str, Any] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)
    on_error: Optional[str] = None

@dataclass
class Workflow:
    """Workflow definition."""
    name: str
    description: str
    steps: Dict[str, WorkflowStep]
    start_step: str
    version: str = "1.0.0"

class WorkflowEngine:
    """
    Executes complex multi-agent workflows.
    
    Features:
    - DAG-based workflow execution
    - Conditional branching
    - Parallel execution
    - Error handling
    - State persistence
    """
    
    def __init__(
        self,
        supervisor: AgentSupervisor,
        executor: AsyncExecutor
    ):
        self.supervisor = supervisor
        self.executor = executor
        self._workflows: Dict[str, Workflow] = {}
        self._executions: Dict[str, Dict[str, Any]] = {}
    
    def register_workflow(self, workflow: Workflow) -> None:
        """Register a workflow."""
        self._workflows[workflow.name] = workflow
    
    async def execute(
        self,
        workflow_name: str,
        input_data: Dict[str, Any],
        execution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_name: Name of the workflow
            input_data: Input data
            execution_id: Optional execution ID for resuming
            
        Returns:
            Workflow results
        """
        if workflow_name not in self._workflows:
            raise ValueError(f"Workflow {workflow_name} not found")
        
        workflow = self._workflows[workflow_name]
        execution_id = execution_id or str(uuid.uuid4())
        
        # Initialize execution state
        state = {
            "execution_id": execution_id,
            "workflow_name": workflow_name,
            "data": input_data.copy(),
            "completed_steps": [],
            "current_step": workflow.start_step,
            "status": "running"
        }
        
        self._executions[execution_id] = state
        
        # Execute workflow
        while state["current_step"]:
            step_id = state["current_step"]
            step = workflow.steps.get(step_id)
            
            if not step:
                state["status"] = "failed"
                state["error"] = f"Step {step_id} not found"
                break
            
            try:
                result = await self._execute_step(step, state)
                state["completed_steps"].append(step_id)
                
                # Determine next step
                if result.get("next_step"):
                    state["current_step"] = result["next_step"]
                elif step.next_steps:
                    state["current_step"] = step.next_steps[0]
                else:
                    state["current_step"] = None
                    state["status"] = "completed"
                    
            except Exception as e:
                if step.on_error:
                    state["current_step"] = step.on_error
                else:
                    state["status"] = "failed"
                    state["error"] = str(e)
                    break
        
        return {
            "execution_id": execution_id,
            "status": state["status"],
            "data": state["data"],
            "completed_steps": state["completed_steps"],
            "error": state.get("error")
        }
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        if step.step_type == WorkflowStepType.AGENT:
            # Execute agent
            query = step.config.get("query", "")
            context = step.config.get("context", {})
            
            output = await self.supervisor.execute(query, context)
            
            # Update state with results
            if output.results:
                state["data"].update({
                    f"{step.step_id}_result": output.results[0].data
                })
            
            return {"success": True}
        
        elif step.step_type == WorkflowStepType.TOOL:
            # Execute tool
            tool_name = step.config.get("tool_name")
            params = step.config.get("params", {})
            
            # Resolve parameter values from state
            resolved_params = self._resolve_params(params, state["data"])
            
            # Execute via executor
            task_id = f"workflow_{state['execution_id']}_{step.step_id}"
            # ... tool execution
            
            return {"success": True}
        
        elif step.step_type == WorkflowStepType.CONDITION:
            # Evaluate condition
            condition = step.config.get("condition", "")
            result = self._evaluate_condition(condition, state["data"])
            
            return {"success": True, "next_step": step.next_steps[0] if result else step.next_steps[1]}
        
        elif step.step_type == WorkflowStepType.PARALLEL:
            # Execute parallel steps
            parallel_steps = step.config.get("steps", [])
            tasks = []
            
            for parallel_step in parallel_steps:
                task = asyncio.create_task(
                    self._execute_step(parallel_step, state)
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            return {"success": True}
        
        return {"success": True}
    
    def _resolve_params(
        self,
        params: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve parameter values from workflow data."""
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$"):
                # Reference to workflow data
                data_key = value[1:]
                resolved[key] = data.get(data_key)
            else:
                resolved[key] = value
        
        return resolved
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Evaluate a condition."""
        try:
            for key, value in data.items():
                condition = condition.replace(f"${key}", str(value))
            return eval(condition)
        except:
            return False
```

### 3.6 Tool Registry & Versioning

```python
# src/tools/tool_registry.py
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import inspect

class ToolStatus(Enum):
    """Tool status."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    DISABLED = "disabled"

@dataclass
class ToolMetadata:
    """Tool metadata."""
    name: str
    description: str
    version: str
    author: str
    created_at: datetime
    updated_at: datetime
    status: ToolStatus = ToolStatus.ACTIVE
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    deprecation_notice: Optional[str] = None
    replacement_tool: Optional[str] = None

@dataclass
class Tool:
    """Registered tool."""
    metadata: ToolMetadata
    implementation: Callable
    is_async: bool = False
    timeout: float = 30.0
    cache_enabled: bool = True
    cache_ttl: int = 300  # seconds

class ToolRegistry:
    """
    Central registry for all MCP tools.
    
    Features:
    - Tool registration and discovery
    - Version management
    - Deprecation handling
    - Dependency resolution
    - Performance tracking
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[str, List[str]] = {}
        self._performance: Dict[str, Dict[str, Any]] = {}
    
    def register(
        self,
        name: str,
        implementation: Callable,
        description: str,
        version: str = "1.0.0",
        author: str = "",
        tags: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        returns: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict]] = None,
        dependencies: Optional[List[str]] = None,
        timeout: float = 30.0,
        cache_enabled: bool = True,
        cache_ttl: int = 300
    ) -> Tool:
        """
        Register a new tool.
        
        Args:
            name: Unique tool name
            implementation: Function or coroutine
            description: Tool description
            version: Tool version
            author: Tool author
            tags: Categorization tags
            parameters: Parameter schema
            returns: Return schema
            examples: Usage examples
            dependencies: Required dependencies
            timeout: Execution timeout
            cache_enabled: Enable caching
            cache_ttl: Cache TTL in seconds
            
        Returns:
            Registered Tool
        """
        metadata = ToolMetadata(
            name=name,
            description=description,
            version=version,
            author=author,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=tags or [],
            parameters=parameters or {},
            returns=returns or {},
            examples=examples or [],
            dependencies=dependencies or []
        )
        
        tool = Tool(
            metadata=metadata,
            implementation=implementation,
            is_async=asyncio.iscoroutinefunction(implementation),
            timeout=timeout,
            cache_enabled=cache_enabled,
            cache_ttl=cache_ttl
        )
        
        self._tools[name] = tool
        
        # Add to categories
        for tag in metadata.tags:
            if tag not in self._categories:
                self._categories[tag] = []
            self._categories[tag].append(name)
        
        # Initialize performance tracking
        self._performance[name] = {
            "calls": 0,
            "success": 0,
            "avg_time_ms": 0
        }
        
        return tool
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get tool implementation by name."""
        tool = self._tools.get(name)
        if not tool:
            return None
        
        if tool.metadata.status == ToolStatus.DISABLED:
            raise ValueError(f"Tool {name} is disabled")
        
        if tool.metadata.status == ToolStatus.DEPRECATED:
            # Log deprecation warning
            print(f"Warning: Tool {name} is deprecated")
            if tool.metadata.replacement_tool:
                print(f"Use {tool.metadata.replacement_tool} instead")
        
        return tool.implementation
    
    def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get tool metadata."""
        tool = self._tools.get(name)
        return tool.metadata if tool else None
    
    def list_tools(
        self,
        category: Optional[str] = None,
        status: Optional[ToolStatus] = None,
        tag: Optional[str] = None
    ) -> List[ToolMetadata]:
        """List tools with optional filtering."""
        tools = []
        
        for name, tool in self._tools.items():
            # Apply filters
            if category and name not in self._categories.get(category, []):
                continue
            
            if status and tool.metadata.status != status:
                continue
            
            if tag and tag not in tool.metadata.tags:
                continue
            
            tools.append(tool.metadata)
        
        return tools
    
    def deprecate(
        self,
        name: str,
        replacement: Optional[str] = None,
        notice: Optional[str] = None
    ) -> None:
        """Mark a tool as deprecated."""
        tool = self._tools.get(name)
        if tool:
            tool.metadata.status = ToolStatus.DEPRECATED
            tool.metadata.replacement_tool = replacement
            tool.metadata.deprecation_notice = notice
            tool.metadata.updated_at = datetime.utcnow()
    
    def disable(self, name: str) -> None:
        """Disable a tool."""
        tool = self._tools.get(name)
        if tool:
            tool.metadata.status = ToolStatus.DISABLED
            tool.metadata.updated_at = datetime.utcnow()
    
    def get_mcp_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get MCP tool schema for a tool."""
        tool = self._tools.get(name)
        if not tool:
            return None
        
        return {
            "name": tool.metadata.name,
            "description": tool.metadata.description,
            "parameters": {
                "type": "object",
                "properties": tool.metadata.parameters,
                "required": [
                    k for k, v in tool.metadata.parameters.items()
                    if v.get("required", False)
                ]
            }
        }
    
    def get_all_mcp_schemas(self) -> List[Dict[str, Any]]:
        """Get MCP schemas for all active tools."""
        schemas = []
        
        for name, tool in self._tools.items():
            if tool.metadata.status in [ToolStatus.ACTIVE, ToolStatus.EXPERIMENTAL]:
                schema = self.get_mcp_schema(name)
                if schema:
                    schemas.append(schema)
        
        return schemas
    
    def record_performance(
        self,
        name: str,
        success: bool,
        execution_time_ms: float
    ) -> None:
        """Record tool performance."""
        if name not in self._performance:
            return
        
        perf = self._performance[name]
        perf["calls"] += 1
        if success:
            perf["success"] += 1
        
        # Update average
        perf["avg_time_ms"] = (
            (perf["avg_time_ms"] * (perf["calls"] - 1) + execution_time_ms)
            / perf["calls"]
        )
    
    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all tools."""
        return self._performance.copy()

# Decorator for easy tool registration
def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    version: str = "1.0.0",
    tags: Optional[List[str]] = None,
    cache_enabled: bool = True,
    timeout: float = 30.0
):
    """Decorator for registering tools."""
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or ""
        
        # Extract parameter schema from function signature
        sig = inspect.signature(func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            param_info = {
                "type": "string",  # Default type
                "description": f"Parameter {param_name}"
            }
            
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
            else:
                param_info["required"] = True
            
            parameters[param_name] = param_info
        
        # Store registration info on function
        func._tool_info = {
            "name": tool_name,
            "description": tool_description,
            "version": version,
            "tags": tags or [],
            "parameters": parameters,
            "cache_enabled": cache_enabled,
            "timeout": timeout
        }
        
        return func
    
    return decorator
```

---

## 4. API Specifications

### 4.1 REST API Endpoints

```yaml
# API Specification
openapi: 3.0.0
info:
  title: ResilienceAI Agent API
  version: 2.0.0
  description: Multi-agent MCP orchestration API

paths:
  /api/v2/agents/query:
    post:
      summary: Submit a query to the agent system
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                session_id:
                  type: string
                context:
                  type: object
                preferred_agent:
                  type: string
                streaming:
                  type: boolean
      responses:
        200:
          description: Query response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentResponse'

  /api/v2/agents/stream:
    post:
      summary: Stream agent response
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                session_id:
                  type: string
      responses:
        200:
          description: Streamed response
          content:
            text/event-stream:
              schema:
                type: string

  /api/v2/agents/{agent_id}/execute:
    post:
      summary: Execute specific agent
      parameters:
        - name: agent_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                tools:
                  type: array
                  items:
                    type: string
      responses:
        200:
          description: Agent execution result

  /api/v2/tools:
    get:
      summary: List all available tools
      parameters:
        - name: category
          in: query
          schema:
            type: string
        - name: status
          in: query
          schema:
            type: string
            enum: [active, deprecated, experimental]
      responses:
        200:
          description: List of tools
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ToolMetadata'

  /api/v2/tools/{tool_name}/execute:
    post:
      summary: Execute a specific tool
      parameters:
        - name: tool_name
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        200:
          description: Tool execution result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ToolResult'

  /api/v2/workflows:
    get:
      summary: List registered workflows
      responses:
        200:
          description: List of workflows

  /api/v2/workflows/{workflow_name}/execute:
    post:
      summary: Execute a workflow
      parameters:
        - name: workflow_name
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                input_data:
                  type: object
      responses:
        200:
          description: Workflow execution result

  /api/v2/memory/{session_id}:
    get:
      summary: Get session memory
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Session memory

  /api/v2/health:
    get:
      summary: Health check
      responses:
        200:
          description: System health status
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthStatus'

  /api/v2/metrics:
    get:
      summary: Get system metrics
      responses:
        200:
          description: System metrics
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SystemMetrics'

components:
  schemas:
    AgentResponse:
      type: object
      properties:
        response:
          type: string
        agent_name:
          type: string
        confidence:
          type: number
        tool_calls:
          type: array
          items:
            type: object
        execution_time_ms:
          type: number
        session_id:
          type: string

    ToolMetadata:
      type: object
      properties:
        name:
          type: string
        description:
          type: string
        version:
          type: string
        status:
          type: string
        tags:
          type: array
          items:
            type: string

    ToolResult:
      type: object
      properties:
        tool_name:
          type: string
        success:
          type: boolean
        data:
          type: object
        error:
          type: string
        execution_time_ms:
          type: number
        cached:
          type: boolean

    HealthStatus:
      type: object
      properties:
        status:
          type: string
        agents:
          type: object
        llm_providers:
          type: object
        uptime_seconds:
          type: number

    SystemMetrics:
      type: object
      properties:
        total_queries:
          type: integer
        avg_response_time_ms:
          type: number
        agent_utilization:
          type: object
        token_usage:
          type: object
```

---

## 5. Integration Points

### 5.1 Existing Code Integration

```python
# Integration with existing src/agent.py
from src.agent import ResilienceAgent, get_mcp_tools
from src.agent_orchestrator import AgentOrchestrator, ToolResult

class LegacyAgentAdapter(BaseAgent):
    """
    Adapter for existing ResilienceAgent.
    Wraps the monolithic agent in the new multi-agent framework.
    """
    
    name = "legacy_resilience"
    description = "Legacy ResilienceAgent with 45+ MCP tools"
    capabilities = [
        AgentCapability.DATA_QUERY,
        AgentCapability.VULNERABILITY_ANALYSIS,
        AgentCapability.SCENARIO_SIMULATION
    ]
    
    intent_keywords = [
        "county", "risk", "vulnerability", "disaster",
        "infrastructure", "hospital", "emergency"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._legacy_agent = ResilienceAgent()
        self._orchestrator = AgentOrchestrator()
    
    @property
    def system_prompt(self) -> str:
        return self._legacy_agent.get_system_prompt()
    
    async def execute(
        self,
        query: str,
        context: Optional[AgentContext] = None,
        tools: Optional[List[str]] = None
    ) -> AgentOutput:
        """Execute using legacy agent."""
        start_time = time.time()
        
        try:
            # Use legacy query method
            result = self._legacy_agent.query(query)
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentOutput(
                agent_name=self.name,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                results=[
                    ToolResult(
                        tool_name="legacy_query",
                        success=True,
                        data=result.get("data"),
                        execution_time_ms=execution_time
                    )
                ],
                insights=[result.get("answer", "")],
                confidence=0.8,
                execution_time_ms=execution_time,
                context=context
            )
            
        except Exception as e:
            return AgentOutput(
                agent_name=self.name,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )

# Migration path for existing tools
def migrate_legacy_tools(registry: ToolRegistry) -> None:
    """Migrate existing tools to new registry."""
    
    # Get existing MCP tool definitions
    mcp_tools = get_mcp_tools()
    
    for tool_def in mcp_tools:
        tool_name = tool_def["name"]
        
        # Create wrapper function
        def create_wrapper(name: str):
            async def wrapper(**kwargs):
                # Call legacy agent method
                agent = ResilienceAgent()
                method = getattr(agent, name, None)
                if method:
                    if asyncio.iscoroutinefunction(method):
                        return await method(**kwargs)
                    else:
                        return method(**kwargs)
                raise ValueError(f"Tool {name} not found")
            return wrapper
        
        # Register with new registry
        registry.register(
            name=tool_name,
            implementation=create_wrapper(tool_name),
            description=tool_def.get("description", ""),
            version="1.0.0",
            tags=["legacy", "mcp"],
            parameters=tool_def.get("parameters", {}).get("properties", {})
        )
```

---

## 6. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
1. **Core Infrastructure**
   - Set up project structure
   - Implement configuration management
   - Set up structured logging
   - Implement metrics collection

2. **Base Components**
   - Enhanced BaseAgent class
   - ToolRegistry with versioning
   - AsyncExecutor for task management

3. **LLM Abstraction**
   - BaseLLMProvider interface
   - LLMManager with fallback
   - Archia provider implementation

### Phase 2: Agent System (Weeks 3-4)
1. **Memory System**
   - Short-term memory (Redis)
   - Long-term memory (vector store)
   - Entity extraction
   - Context management

2. **Specialized Agents**
   - RouterAgent for intent classification
   - VulnerabilityAgent
   - ClimateAgent
   - RealtimeAgent

3. **Orchestration**
   - AgentSupervisor
   - Basic workflow engine
   - Load balancing

### Phase 3: Advanced Features (Weeks 5-6)
1. **Tool Execution**
   - ToolChainEngine
   - Retry with exponential backoff
   - Circuit breaker pattern
   - Caching layer

2. **Workflow System**
   - DAG-based workflows
   - Conditional branching
   - Parallel execution
   - State persistence

3. **Monitoring**
   - Performance metrics
   - Health checks
   - Distributed tracing

### Phase 4: API & Integration (Weeks 7-8)
1. **API Layer**
   - FastAPI application
   - REST endpoints
   - WebSocket streaming
   - Authentication middleware

2. **Legacy Integration**
   - LegacyAgentAdapter
   - Tool migration scripts
   - Backward compatibility

3. **Deployment**
   - Docker containers
   - Kubernetes manifests
   - CI/CD pipeline

---

## 7. Performance Considerations

### 7.1 Caching Strategy

```python
# Cache configuration
cache_config = {
    "tiers": [
        {
            "name": "memory",
            "type": "in_memory",
            "ttl": 60,
            "max_size": 1000
        },
        {
            "name": "redis",
            "type": "redis",
            "ttl": 300,
            "host": "localhost",
            "port": 6379
        }
    ],
    "strategies": {
        "tool_results": {
            "tiers": ["memory", "redis"],
            "key_pattern": "tool:{tool_name}:{params_hash}",
            "ttl": 300
        },
        "agent_responses": {
            "tiers": ["memory"],
            "key_pattern": "agent:{agent_name}:{query_hash}",
            "ttl": 60
        },
        "llm_responses": {
            "tiers": ["redis"],
            "key_pattern": "llm:{provider}:{prompt_hash}",
            "ttl": 3600
        }
    }
}
```

### 7.2 Concurrency Limits

```python
# Concurrency configuration
concurrency_config = {
    "async_executor": {
        "max_workers": 20,
        "max_concurrent": 10,
        "thread_pool_size": 4
    },
    "agent_limits": {
        "vulnerability_agent": 5,
        "climate_agent": 3,
        "realtime_agent": 10,
        "planning_agent": 2
    },
    "llm_limits": {
        "archia": 10,
        "openai": 20,
        "anthropic": 15
    }
}
```

### 7.3 Auto-scaling Configuration

```yaml
# Kubernetes HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: resilienceai-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: resilienceai-agent
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: agent_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

---

## 8. Monitoring & Observability

### 8.1 Metrics

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, Info

# Request metrics
agent_requests_total = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['agent_name', 'status']
)

agent_request_duration = Histogram(
    'agent_request_duration_seconds',
    'Agent request duration',
    ['agent_name'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Tool metrics
tool_executions_total = Counter(
    'tool_executions_total',
    'Total tool executions',
    ['tool_name', 'status']
)

tool_execution_duration = Histogram(
    'tool_execution_duration_seconds',
    'Tool execution duration',
    ['tool_name']
)

# LLM metrics
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['provider', 'model', 'status']
)

llm_tokens_used = Counter(
    'llm_tokens_used_total',
    'Total LLM tokens used',
    ['provider', 'type']  # type: prompt, completion
)

# System metrics
active_agents = Gauge(
    'active_agents',
    'Number of active agents',
    ['agent_name']
)

memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    ['type']  # short_term, long_term
)
```

### 8.2 Distributed Tracing

```python
# OpenTelemetry tracing
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

tracer = trace.get_tracer(__name__)

# Example traced function
@tracer.start_as_current_span("agent_execute")
async def execute_agent(query: str, context: AgentContext) -> AgentOutput:
    with tracer.start_as_current_span("intent_classification"):
        intent = await classify_intent(query)
    
    with tracer.start_as_current_span("tool_execution") as span:
        span.set_attribute("tool_count", len(intent.tools))
        results = await execute_tools(intent.tools)
    
    with tracer.start_as_current_span("response_generation"):
        response = await generate_response(results)
    
    return response
```

---

## 9. Conclusion

This design provides a comprehensive blueprint for enhancing the ResilienceAI backend into a production-ready multi-agent MCP system. Key improvements include:

1. **Async Architecture**: Full async support for all tools and agents
2. **Multi-Agent System**: Specialized agents with intelligent routing
3. **LLM Abstraction**: Provider-agnostic LLM integration with fallback
4. **Memory System**: Short-term and long-term memory for context
5. **Tool Chaining**: Complex workflow support with data flow
6. **Observability**: Comprehensive metrics and distributed tracing
7. **Auto-scaling**: Kubernetes-native scaling based on demand

The phased implementation approach allows for incremental migration from the existing codebase while maintaining backward compatibility.
