"""
ResilienceAI - Tool Registry
Central registry for all MCP tools with versioning and deprecation.
"""
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import inspect
import hashlib
import json


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
        
        # Build required list
        required = []
        for param_name, param_info in tool.metadata.parameters.items():
            if param_info.get("required", False):
                required.append(param_name)
        
        return {
            "type": "function",
            "function": {
                "name": tool.metadata.name,
                "description": tool.metadata.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.metadata.parameters,
                    "required": required
                }
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
    
    def get_cache_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Generate cache key for tool execution."""
        # Sort params for consistent hashing
        param_str = json.dumps(params, sort_keys=True)
        hash_input = f"{tool_name}:{param_str}"
        return hashlib.sha256(hash_input.encode()).hexdigest()


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
                "type": "string",
                "description": f"Parameter {param_name}"
            }
            
            # Infer type from annotation
            if param.annotation != inspect.Parameter.empty:
                type_map = {
                    str: "string",
                    int: "integer",
                    float: "number",
                    bool: "boolean",
                    list: "array",
                    dict: "object"
                }
                param_info["type"] = type_map.get(param.annotation, "string")
            
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
