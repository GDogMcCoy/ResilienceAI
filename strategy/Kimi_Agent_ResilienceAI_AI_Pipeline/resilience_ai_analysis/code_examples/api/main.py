"""
ResilienceAI - FastAPI Application
Main API entry point for the multi-agent system.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import asyncio
import json
import time

from ..agents.base import AgentContext, AgentStatus
from ..orchestration.supervisor import AgentSupervisor
from ..execution.async_executor import AsyncExecutor
from ..tools.tool_registry import ToolRegistry


# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    preferred_agent: Optional[str] = None
    streaming: bool = False


class QueryResponse(BaseModel):
    response: str
    agent_name: str
    confidence: float
    tool_calls: List[Dict[str, Any]]
    execution_time_ms: float
    session_id: str


class ToolExecuteRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any]
    use_cache: bool = True


class ToolExecuteResponse(BaseModel):
    tool_name: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float
    cached: bool = False


class WorkflowExecuteRequest(BaseModel):
    workflow_name: str
    input_data: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    agents: Dict[str, str]
    llm_providers: Dict[str, str]
    uptime_seconds: float


# Create FastAPI app
app = FastAPI(
    title="ResilienceAI Agent API",
    description="Multi-agent MCP orchestration API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class AppState:
    def __init__(self):
        self.supervisor: Optional[AgentSupervisor] = None
        self.executor: Optional[AsyncExecutor] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self.start_time: float = time.time()
        
    async def initialize(self):
        """Initialize all components."""
        # Initialize executor
        self.executor = AsyncExecutor(max_workers=20, max_concurrent=10)
        await self.executor.start()
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        
        # Register tools
        await self._register_tools()
        
        # Initialize supervisor
        # self.supervisor = AgentSupervisor(agents=..., ...)
        
    async def _register_tools(self):
        """Register all available tools."""
        # Import and register tools
        from ..tools.definitions import data_query, analysis, visualization
        
        # Register data query tools
        for tool_func in data_query.get_tools():
            self.tool_registry.register(
                name=tool_func._tool_info["name"],
                implementation=tool_func,
                description=tool_func._tool_info["description"],
                tags=tool_func._tool_info.get("tags", []),
                parameters=tool_func._tool_info.get("parameters", {})
            )
    
    async def shutdown(self):
        """Shutdown all components."""
        if self.executor:
            await self.executor.shutdown()


app_state = AppState()


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    await app_state.initialize()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    await app_state.shutdown()


# API Routes
@app.post("/api/v2/agents/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Submit a query to the agent system."""
    if not app_state.supervisor:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    start_time = time.time()
    
    # Create context
    context = AgentContext(
        session_id=request.session_id or f"session_{int(time.time())}",
        user_id=request.user_id,
        metadata=request.context or {}
    )
    
    try:
        # Execute query
        output = await app_state.supervisor.execute(
            query=request.query,
            context=context
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        return QueryResponse(
            response=output.insights[0] if output.insights else "",
            agent_name=output.agent_name,
            confidence=output.confidence,
            tool_calls=[
                {
                    "tool": r.tool_name,
                    "success": r.success,
                    "execution_time_ms": r.execution_time_ms
                }
                for r in output.results
            ],
            execution_time_ms=execution_time,
            session_id=context.session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/agents/stream")
async def stream_query(request: QueryRequest):
    """Stream agent response."""
    if not app_state.supervisor:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    async def generate_stream():
        context = AgentContext(
            session_id=request.session_id or f"session_{int(time.time())}",
            user_id=request.user_id
        )
        
        agent = app_state.supervisor.agents.get(request.preferred_agent or "general")
        if not agent:
            yield f"data: {json.dumps({'error': 'Agent not found'})}\n\n"
            return
        
        async for chunk in agent.execute_stream(request.query, context):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )


@app.get("/api/v2/tools")
async def list_tools(
    category: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None
):
    """List all available tools."""
    if not app_state.tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")
    
    from ..tools.tool_registry import ToolStatus
    
    status_enum = None
    if status:
        try:
            status_enum = ToolStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    tools = app_state.tool_registry.list_tools(
        category=category,
        status=status_enum,
        tag=tag
    )
    
    return [
        {
            "name": t.name,
            "description": t.description,
            "version": t.version,
            "status": t.status.value,
            "tags": t.tags
        }
        for t in tools
    ]


@app.post("/api/v2/tools/{tool_name}/execute", response_model=ToolExecuteResponse)
async def execute_tool(tool_name: str, request: ToolExecuteRequest):
    """Execute a specific tool."""
    if not app_state.tool_registry or not app_state.executor:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Get tool
    tool = app_state.tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
    
    # Submit to executor
    task_id = f"tool_{tool_name}_{int(time.time())}"
    
    async def execute():
        if asyncio.iscoroutinefunction(tool):
            return await tool(**request.params)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: tool(**request.params))
    
    await app_state.executor.submit(task_id, execute())
    result = await app_state.executor.wait_for(task_id)
    
    return ToolExecuteResponse(
        tool_name=tool_name,
        success=result.success,
        data=result.data,
        error=result.error,
        execution_time_ms=result.execution_time_ms,
        cached=False
    )


@app.get("/api/v2/tools/schemas")
async def get_mcp_schemas():
    """Get all MCP tool schemas."""
    if not app_state.tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")
    
    return app_state.tool_registry.get_all_mcp_schemas()


@app.get("/api/v2/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    agents_status = {}
    if app_state.supervisor:
        for name, agent in app_state.supervisor.agents.items():
            agents_status[name] = agent.status.value
    
    llm_status = {}
    # Add LLM provider health checks
    
    uptime = time.time() - app_state.start_time
    
    return HealthResponse(
        status="healthy",
        agents=agents_status,
        llm_providers=llm_status,
        uptime_seconds=uptime
    )


@app.get("/api/v2/metrics")
async def get_metrics():
    """Get system metrics."""
    metrics = {
        "executor": app_state.executor.get_status() if app_state.executor else {},
        "tool_performance": app_state.tool_registry.get_performance_stats() if app_state.tool_registry else {},
        "agent_performance": app_state.supervisor.get_agent_stats() if app_state.supervisor else {}
    }
    
    return metrics


# WebSocket for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time agent communication."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            query = data.get("query", "")
            session_id = data.get("session_id")
            
            # Create context
            context = AgentContext(
                session_id=session_id or f"ws_session_{int(time.time())}"
            )
            
            # Execute
            if app_state.supervisor:
                output = await app_state.supervisor.execute(query, context)
                
                # Send response
                await websocket.send_json({
                    "type": "response",
                    "content": output.insights[0] if output.insights else "",
                    "agent": output.agent_name,
                    "confidence": output.confidence
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Agent system not initialized"
                })
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Handle generic exceptions."""
    return {
        "error": "Internal server error",
        "message": str(exc)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
