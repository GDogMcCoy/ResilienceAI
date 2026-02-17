"""
ResilienceAI - Agent Supervisor
Supervises multi-agent orchestration with intelligent routing.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import asyncio
import time

from ..agents.base import BaseAgent, AgentContext, AgentOutput, AgentStatus


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
        router_agent: Optional['BaseAgent'] = None
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
            # No agent confident enough - use router agent
            if self.router_agent:
                return await self._router_decision(query, context)
            
            # Fallback to general agent
            return RoutingDecision(
                agent_name="general",
                confidence=0.0,
                reasoning="No confident agent found, using fallback"
            )
        
        primary_agent = sorted_agents[0][0]
        fallback_agents = [a[0] for a in sorted_agents[1:3] if a[1] > 0.3]
        
        return RoutingDecision(
            agent_name=primary_agent,
            confidence=sorted_agents[0][1],
            reasoning=f"Agent {primary_agent} has highest confidence ({sorted_agents[0][1]:.2f})",
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
    
    async def _router_decision(
        self,
        query: str,
        context: Optional[AgentContext]
    ) -> RoutingDecision:
        """Get routing decision from router agent."""
        if not self.router_agent:
            return RoutingDecision(
                agent_name="general",
                confidence=0.0,
                reasoning="No router agent available"
            )
        
        # Execute router agent
        output = await self.router_agent.execute(query, context)
        
        # Parse routing decision from output
        if output.results and output.results[0].data:
            data = output.results[0].data
            if isinstance(data, dict):
                return RoutingDecision(
                    agent_name=data.get("agent_name", "general"),
                    confidence=data.get("confidence", 0.5),
                    reasoning=data.get("reasoning", "Router decision"),
                    fallback_agents=data.get("fallback_agents", [])
                )
        
        return RoutingDecision(
            agent_name="general",
            confidence=0.0,
            reasoning="Router failed to provide decision"
        )
    
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
    
    async def execute_parallel(
        self,
        query: str,
        agent_names: List[str],
        context: Optional[AgentContext] = None
    ) -> List[AgentOutput]:
        """
        Execute query on multiple agents in parallel.
        
        Args:
            query: Natural language query
            agent_names: List of agent names to execute
            context: Execution context
            
        Returns:
            List of AgentOutputs
        """
        tasks = []
        for name in agent_names:
            agent = self.agents.get(name)
            if agent:
                task = asyncio.create_task(agent.execute(query, context))
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        outputs = []
        for result in results:
            if isinstance(result, Exception):
                outputs.append(AgentOutput(
                    agent_name="unknown",
                    agent_id="unknown",
                    status=AgentStatus.FAILED,
                    error=str(result)
                ))
            else:
                outputs.append(result)
        
        return outputs
    
    def _estimate_cost(self, agent_name: str) -> float:
        """Estimate execution cost for agent."""
        # Simplified cost estimation
        perf = self._agent_performance.get(agent_name, {})
        avg_tokens = perf.get("avg_tokens", 1000)
        return avg_tokens * 0.00001  # $0.01 per 1K tokens
    
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
        
        # Update token usage
        total_tokens = sum(output.tokens_used.values())
        if total_tokens > 0:
            perf["avg_tokens"] = (
                (perf.get("avg_tokens", 0) * (perf["calls"] - 1) + total_tokens)
                / perf["calls"]
            )
    
    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all agents."""
        return self._agent_performance.copy()
    
    def get_best_agent(self, capability: str) -> Optional[str]:
        """Get best performing agent for a capability."""
        best_agent = None
        best_score = 0.0
        
        for name, agent in self.agents.items():
            if capability in [c.value for c in agent.capabilities]:
                perf = self._agent_performance.get(name, {})
                success_rate = perf.get("success", 0) / max(perf.get("calls", 1), 1)
                
                if success_rate > best_score:
                    best_score = success_rate
                    best_agent = name
        
        return best_agent
