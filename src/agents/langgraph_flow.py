"""
ResilienceAI - LangGraph State Machine
Sophisticated agent routing and orchestration using LangGraph patterns.
"""
from typing import Dict, List, Any, Optional, Callable, TypedDict, Annotated
from dataclasses import dataclass, field
from enum import Enum
import operator
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class RoutingDecision(Enum):
    """Possible routing decisions."""
    CLIMATE = "climate"
    VULNERABILITY = "vulnerability"
    REALTIME = "realtime"
    PLANNING = "planning"
    MULTI = "multi"  # Requires multiple agents
    UNKNOWN = "unknown"


class ExecutionMode(Enum):
    """Execution mode for agents."""
    SEQUENTIAL = "sequential"  # Execute agents one by one
    PARALLEL = "parallel"      # Execute agents concurrently
    HYBRID = "hybrid"          # Some parallel, some sequential


class OrchestratorState(TypedDict):
    """LangGraph state definition for the orchestrator."""
    # Input
    query: str
    context: Dict[str, Any]
    
    # Intent classification
    intent_scores: Dict[str, float]
    primary_intent: str
    confidence: float
    
    # Routing
    selected_agents: List[str]
    execution_mode: str
    dependencies: Dict[str, List[str]]  # agent -> list of dependencies
    
    # Execution
    agent_outputs: Dict[str, Any]
    tool_results: List[Dict]
    errors: Annotated[List[str], operator.add]
    
    # Synthesis
    synthesized_response: Optional[str]
    insights: List[str]
    follow_up_queries: List[str]
    
    # Metadata
    execution_time_ms: float
    completed: bool


@dataclass
class IntentClassification:
    """Result of intent classification."""
    scores: Dict[str, float]  # agent -> confidence score
    primary: str
    confidence: float
    secondary: List[str] = field(default_factory=list)
    
    def requires_multi_agent(self, threshold: float = 0.3) -> bool:
        """Check if multiple agents should be invoked."""
        if not self.scores:
            return False
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_scores) < 2:
            return False
        # Multi-agent if secondary is within threshold of primary
        return (sorted_scores[0][1] - sorted_scores[1][1]) < threshold


@dataclass
class AgentNode:
    """Node in the execution graph representing an agent invocation."""
    agent_name: str
    tools: List[Dict[str, Any]]
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0  # Higher = execute first
    
    def can_execute(self, completed_agents: set) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep in completed_agents for dep in self.dependencies)


class LangGraphFlow:
    """
    LangGraph-inspired state machine for agent orchestration.
    
    Handles:
    - Intent classification with confidence scores
    - Parallel vs sequential execution decisions
    - Dependency management between agents
    - State transitions and error handling
    """

    def __init__(self, agents: Dict[str, Any]):
        """
        Initialize the flow with available agents.
        
        Args:
            agents: Dictionary of agent_name -> agent_instance
        """
        self.agents = agents
        self.execution_graph: Dict[str, AgentNode] = {}
        self.state: OrchestratorState = self._init_state()
        
        # Intent classification thresholds
        self.intent_threshold = 0.2  # Minimum score to consider an agent
        self.multi_agent_threshold = 0.15  # Gap threshold for multi-agent
        
        # Define agent dependencies (which agents need others to run first)
        self.agent_dependencies = {
            "planning": ["climate", "vulnerability"],  # Planning may need data from others
        }

    def _init_state(self) -> OrchestratorState:
        """Initialize empty state."""
        return {
            "query": "",
            "context": {},
            "intent_scores": {},
            "primary_intent": "",
            "confidence": 0.0,
            "selected_agents": [],
            "execution_mode": ExecutionMode.PARALLEL.value,
            "dependencies": {},
            "agent_outputs": {},
            "tool_results": [],
            "errors": [],
            "synthesized_response": None,
            "insights": [],
            "follow_up_queries": [],
            "execution_time_ms": 0.0,
            "completed": False
        }

    def classify_intent(self, query: str) -> IntentClassification:
        """
        Classify query intent across all agents.
        
        Returns:
            IntentClassification with scores for each agent
        """
        scores = {}
        
        for agent_name, agent in self.agents.items():
            score = agent.calculate_intent_match(query)
            if score >= self.intent_threshold:
                scores[agent_name] = round(score, 3)
        
        if not scores:
            # Default to vulnerability agent for unknown queries
            return IntentClassification(
                scores={"vulnerability": 0.5},
                primary="vulnerability",
                confidence=0.5,
                secondary=[]
            )
        
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_scores[0][0]
        confidence = sorted_scores[0][1]
        
        # Determine secondary agents (within multi_agent_threshold of primary)
        secondary = [
            name for name, score in sorted_scores[1:]
            if (confidence - score) < self.multi_agent_threshold
        ]
        
        return IntentClassification(
            scores=scores,
            primary=primary,
            confidence=confidence,
            secondary=secondary
        )

    def build_execution_graph(self, intent: IntentClassification, 
                              query: str,
                              context: Dict[str, Any] = None) -> Dict[str, AgentNode]:
        """
        Build the execution graph based on intent classification.
        
        Args:
            intent: Intent classification result
            query: Original query
            context: Additional context
            
        Returns:
            Dictionary of agent_name -> AgentNode
        """
        graph = {}
        
        # Determine which agents to invoke
        agents_to_invoke = [intent.primary]
        if intent.requires_multi_agent(self.multi_agent_threshold):
            agents_to_invoke.extend(intent.secondary[:2])  # Max 3 agents total
        
        # Create nodes for each agent
        for i, agent_name in enumerate(agents_to_invoke):
            agent = self.agents.get(agent_name)
            if not agent:
                continue
            
            # Determine tools to invoke based on query
            tools = self._select_tools_for_agent(agent, query, context)
            
            # Determine dependencies
            deps = self.agent_dependencies.get(agent_name, [])
            # Filter to only agents that will actually run
            deps = [d for d in deps if d in agents_to_invoke]
            
            graph[agent_name] = AgentNode(
                agent_name=agent_name,
                tools=tools,
                dependencies=deps,
                priority=len(agents_to_invoke) - i  # Primary gets highest priority
            )
        
        self.execution_graph = graph
        return graph

    def _select_tools_for_agent(self, agent: Any, query: str, 
                                 context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Select appropriate tools for an agent based on query.
        
        This uses keyword matching and context to determine which tools
        should be invoked for a given query.
        """
        tools = []
        query_lower = query.lower()
        
        # Get all available tools for this agent
        available_tools = agent.get_tools()
        
        for tool in available_tools:
            tool_name = tool.get("name", "")
            description = tool.get("description", "").lower()
            
            # Score how relevant this tool is to the query
            relevance = 0
            
            # Check if tool name appears in query
            if tool_name.replace("_", " ") in query_lower:
                relevance += 0.5
            
            # Check description keywords
            desc_words = set(description.split())
            query_words = set(query_lower.split())
            overlap = len(desc_words & query_words)
            relevance += min(overlap * 0.1, 0.3)
            
            # Context-based selection
            if context:
                if tool_name in context.get("required_tools", []):
                    relevance += 0.5
            
            if relevance > 0.2:
                # Extract parameters from query or use defaults
                params = self._extract_tool_params(tool, query, context)
                tools.append({
                    "name": tool_name,
                    "params": params,
                    "relevance": relevance
                })
        
        # Sort by relevance and take top tools
        tools.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Limit to most relevant tools
        max_tools = 3 if len(tools) > 5 else len(tools)
        return [{"name": t["name"], "params": t["params"]} for t in tools[:max_tools]]

    def _extract_tool_params(self, tool: Dict[str, Any], query: str,
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract tool parameters from query and context."""
        params = {}
        schema = tool.get("parameters", {})
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        query_lower = query.lower()
        
        # Extract FIPS codes
        import re
        fips_matches = re.findall(r'\b\d{5}\b', query)
        if fips_matches and "fips" in properties:
            params["fips"] = fips_matches[0]
        
        # Extract state codes
        state_pattern = r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b'
        state_matches = re.findall(state_pattern, query_upper := query.upper())
        if state_matches:
            if "state" in properties:
                params["state"] = state_matches[0]
        
        # Extract numbers for common parameters
        if "max_results" in properties:
            num_match = re.search(r'(\d+)\s*(?:counties|results)', query_lower)
            if num_match:
                params["max_results"] = int(num_match.group(1))
            else:
                params["max_results"] = 10
        
        # Context overrides
        if context:
            for key in properties:
                if key in context:
                    params[key] = context[key]
        
        # Fill required params with defaults if missing
        for req in required:
            if req not in params:
                if req == "fips" and context and "fips" in context:
                    params[req] = context["fips"]
                elif req == "max_results":
                    params[req] = 10
                elif req == "state":
                    params[req] = "MO"  # Default
        
        return params

    def execute_graph(self, max_workers: int = 4) -> Dict[str, Any]:
        """
        Execute the execution graph.
        
        Handles parallel execution where dependencies allow,
        sequential where required.
        
        Args:
            max_workers: Maximum parallel workers
            
        Returns:
            Dictionary of agent_name -> AgentOutput
        """
        results = {}
        completed = set()
        errors = []
        
        # Determine execution order based on dependencies
        execution_order = self._topological_sort()
        
        # Group by dependency levels for parallel execution
        levels = self._group_by_dependency_level(execution_order)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for level in levels:
                # Submit all agents at this level in parallel
                futures = {}
                for agent_name in level:
                    node = self.execution_graph.get(agent_name)
                    if not node:
                        continue
                    
                    agent = self.agents.get(agent_name)
                    if not agent:
                        errors.append(f"Agent {agent_name} not found")
                        continue
                    
                    # Submit for execution
                    future = executor.submit(agent.execute, node.tools, {})
                    futures[future] = agent_name
                
                # Collect results as they complete
                for future in as_completed(futures):
                    agent_name = futures[future]
                    try:
                        output = future.result(timeout=30)
                        results[agent_name] = output
                        completed.add(agent_name)
                    except Exception as e:
                        errors.append(f"Agent {agent_name} failed: {str(e)}")
                        results[agent_name] = {
                            "agent_name": agent_name,
                            "status": "failed",
                            "error": str(e)
                        }
        
        return {
            "results": results,
            "completed": list(completed),
            "errors": errors
        }

    def _topological_sort(self) -> List[str]:
        """Sort agents by dependencies using topological sort."""
        visited = set()
        temp_mark = set()
        result = []
        
        def visit(node_name: str):
            if node_name in temp_mark:
                raise ValueError(f"Circular dependency detected involving {node_name}")
            if node_name in visited:
                return
            
            temp_mark.add(node_name)
            node = self.execution_graph.get(node_name)
            if node:
                for dep in node.dependencies:
                    visit(dep)
            temp_mark.remove(node_name)
            visited.add(node_name)
            result.append(node_name)
        
        for name in self.execution_graph:
            if name not in visited:
                visit(name)
        
        return result

    def _group_by_dependency_level(self, sorted_agents: List[str]) -> List[List[str]]:
        """Group agents by dependency level for parallel execution."""
        levels = []
        completed = set()
        
        remaining = set(sorted_agents)
        
        while remaining:
            # Find agents with all dependencies satisfied
            current_level = []
            for agent_name in list(remaining):
                node = self.execution_graph.get(agent_name)
                if node and node.can_execute(completed):
                    current_level.append(agent_name)
            
            if not current_level:
                # Should not happen with valid dependencies
                current_level = list(remaining)
            
            levels.append(current_level)
            completed.update(current_level)
            remaining -= set(current_level)
        
        return levels

    def run(self, query: str, context: Dict[str, Any] = None) -> OrchestratorState:
        """
        Run the complete LangGraph flow.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Final orchestrator state
        """
        start_time = time.time()
        
        # Initialize state
        self.state = self._init_state()
        self.state["query"] = query
        self.state["context"] = context or {}
        
        # Step 1: Intent Classification
        intent = self.classify_intent(query)
        self.state["intent_scores"] = intent.scores
        self.state["primary_intent"] = intent.primary
        self.state["confidence"] = intent.confidence
        
        # Step 2: Build Execution Graph
        graph = self.build_execution_graph(intent, query, context)
        self.state["selected_agents"] = list(graph.keys())
        self.state["execution_mode"] = (
            ExecutionMode.PARALLEL.value 
            if len(graph) > 1 and not any(node.dependencies for node in graph.values())
            else ExecutionMode.HYBRID.value
        )
        self.state["dependencies"] = {
            name: node.dependencies for name, node in graph.items()
        }
        
        # Step 3: Execute
        if graph:
            execution_result = self.execute_graph()
            self.state["agent_outputs"] = execution_result["results"]
            self.state["errors"] = execution_result["errors"]
        
        # Step 4: Synthesize (placeholder - actual synthesis in orchestrator)
        self.state["execution_time_ms"] = (time.time() - start_time) * 1000
        self.state["completed"] = True
        
        return self.state

    def get_execution_plan(self) -> Dict[str, Any]:
        """Get the current execution plan for inspection."""
        return {
            "agents": {
                name: {
                    "tools": [t["name"] for t in node.tools],
                    "dependencies": node.dependencies,
                    "priority": node.priority
                }
                for name, node in self.execution_graph.items()
            },
            "parallel_groups": self._group_by_dependency_level(
                self._topological_sort()
            ) if self.execution_graph else []
        }
