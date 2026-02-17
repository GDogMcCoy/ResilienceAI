"""
ResilienceAI - Multi-Agent Orchestrator
Routes queries to specialized agents, dispatches tool calls, and combines results.
Integrates with Archia cloud runtime with local fallback.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import time
import json

from src.agents.base_agent import BaseAgent, AgentOutput
from src.agents.climate_agent import ClimateAgent
from src.agents.vulnerability_agent import VulnerabilityAgent
from src.agents.realtime_agent import RealtimeAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.langgraph_flow import LangGraphFlow, OrchestratorState, IntentClassification


@dataclass
class OrchestratedResponse:
    """Final response from the orchestrator."""
    query: str
    response: str
    insights: List[str] = field(default_factory=list)
    agent_outputs: Dict[str, Any] = field(default_factory=dict)
    tools_executed: List[Dict] = field(default_factory=list)
    follow_up_queries: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    confidence: float = 0.0
    routing_path: List[str] = field(default_factory=list)
    archia_mode: str = "local"  # "cloud" or "local"
    errors: List[str] = field(default_factory=list)


class AgentOrchestrator:
    """
    Routes natural language queries and tool calls to specialized agents.
    
    4 specialist agents:
    - ClimateAgent: Climate trends, hazard profiles, drought, flood, severe weather
    - VulnerabilityAgent: County risk, infrastructure, demographics, spatial analysis
    - RealtimeAgent: Weather alerts, subscriptions, emergency dispatch
    - PlanningAgent: Intervention ROI, forecasting, briefings, agriculture
    
    Features:
    - LangGraph state machine for sophisticated routing
    - Intent classification with confidence scores
    - Parallel agent execution where possible
    - Sequential dependencies handled correctly
    - Archia cloud integration with local fallback
    """

    def __init__(self, use_archia_cloud: bool = False, archia_config: Dict = None):
        """
        Initialize the orchestrator.
        
        Args:
            use_archia_cloud: Whether to try Archia cloud first
            archia_config: Configuration for Archia cloud connection
        """
        self.agents = {
            "climate": ClimateAgent(),
            "vulnerability": VulnerabilityAgent(),
            "realtime": RealtimeAgent(),
            "planning": PlanningAgent(),
        }
        
        # LangGraph flow for sophisticated orchestration
        self.flow = LangGraphFlow(self.agents)
        
        # Tool index for direct tool execution
        self._tool_index = self._build_tool_index()
        
        # Conversation history
        self.conversation_history: List[Dict] = []
        
        # Archia integration
        self.use_archia_cloud = use_archia_cloud
        self.archia_config = archia_config or {}
        self._archia_client = None
        
        if use_archia_cloud:
            self._init_archia_client()

    def _init_archia_client(self):
        """Initialize Archia cloud client."""
        try:
            from src.archia_client import ArchiaClient, ArchiaConfig
            config = ArchiaConfig(
                base_url=self.archia_config.get("base_url", "https://api.archia.app/v1"),
                api_key=self.archia_config.get("api_key"),
                timeout=self.archia_config.get("timeout", 30)
            )
            self._archia_client = ArchiaClient(config)
        except Exception as e:
            print(f"Warning: Could not initialize Archia client: {e}")
            self._archia_client = None

    def _build_tool_index(self) -> Dict[str, str]:
        """Map tool names to owning agent keys."""
        index = {}
        for agent_key, agent in self.agents.items():
            for tool_name in agent.get_tool_names():
                index[tool_name] = agent_key
        return index

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Determine which agent(s) should handle a natural language query.
        
        Uses LangGraph flow for sophisticated intent classification.
        
        Returns:
            Dictionary with routing decision and confidence scores
        """
        intent = self.flow.classify_intent(query)
        
        return {
            "primary_agent": intent.primary,
            "confidence": intent.confidence,
            "scores": intent.scores,
            "secondary_agents": intent.secondary,
            "multi_agent": intent.requires_multi_agent(),
            "recommended_mode": "parallel" if intent.requires_multi_agent() else "single"
        }

    def execute_tool(self, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a specific MCP tool, auto-routing to the owning agent.
        
        Args:
            tool_name: Name of the tool to execute
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        agent_key = self._tool_index.get(tool_name)
        if not agent_key:
            return {"error": f"Tool '{tool_name}' not found in any agent"}
        
        agent = self.agents[agent_key]
        
        try:
            start_time = time.time()
            result = agent.execute_tool(tool_name, params or {})
            execution_time = (time.time() - start_time) * 1000
            
            # Log execution
            self._log_execution({
                "tool": tool_name,
                "agent": agent_key,
                "params": params,
                "success": "error" not in result,
                "execution_time_ms": execution_time
            })
            
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    def execute_query(self, query: str, context: Dict[str, Any] = None) -> OrchestratedResponse:
        """
        Execute a natural language query using the full orchestration pipeline.
        
        This is the main entry point for query processing.
        
        Args:
            query: Natural language query
            context: Additional context (e.g., fips codes, state filters)
            
        Returns:
            OrchestratedResponse with synthesized results
        """
        start_time = time.time()
        
        # Try Archia cloud if enabled
        if self.use_archia_cloud and self._archia_client:
            try:
                cloud_response = self._try_archia_cloud(query, context)
                if cloud_response and "error" not in cloud_response:
                    return self._format_cloud_response(query, cloud_response, start_time)
            except Exception as e:
                # Fall through to local execution
                pass
        
        # Local execution with LangGraph flow
        return self._execute_local(query, context, start_time)

    def _try_archia_cloud(self, query: str, context: Dict[str, Any] = None) -> Optional[Dict]:
        """Try to execute query via Archia cloud."""
        if not self._archia_client:
            return None
        
        # Check health first
        health = self._archia_client.health_check()
        if health.get("status") != "healthy":
            return None
        
        # Execute query
        result = self._archia_client.query(query)
        return result

    def _execute_local(self, query: str, context: Dict[str, Any] = None,
                       start_time: float = None) -> OrchestratedResponse:
        """Execute query locally using LangGraph flow."""
        if start_time is None:
            start_time = time.time()
        
        # Run LangGraph flow
        state = self.flow.run(query, context)
        
        # Synthesize results
        synthesized = self._synthesize_results(state)
        
        # Generate follow-up queries
        follow_ups = self._generate_follow_up_queries(query, state)
        
        # Extract insights
        insights = self._extract_hyperdimensional_insights(state)
        
        execution_time = (time.time() - start_time) * 1000
        
        # Log to conversation history
        self.conversation_history.append({
            "role": "user",
            "query": query,
            "routing": state["primary_intent"],
            "agents_invoked": state["selected_agents"],
            "timestamp": time.time()
        })
        
        return OrchestratedResponse(
            query=query,
            response=synthesized,
            insights=insights,
            agent_outputs=state["agent_outputs"],
            tools_executed=state["tool_results"],
            follow_up_queries=follow_ups,
            execution_time_ms=execution_time,
            confidence=state["confidence"],
            routing_path=state["selected_agents"],
            archia_mode="local",
            errors=state["errors"]
        )

    def _format_cloud_response(self, query: str, cloud_response: Dict,
                               start_time: float) -> OrchestratedResponse:
        """Format Archia cloud response."""
        execution_time = (time.time() - start_time) * 1000
        
        return OrchestratedResponse(
            query=query,
            response=cloud_response.get("response", "No response from cloud"),
            insights=cloud_response.get("insights", []),
            agent_outputs=cloud_response.get("agent_outputs", {}),
            tools_executed=cloud_response.get("tool_calls", []),
            follow_up_queries=cloud_response.get("follow_up_queries", []),
            execution_time_ms=execution_time,
            confidence=cloud_response.get("confidence", 0.8),
            routing_path=["cloud"],
            archia_mode="cloud",
            errors=[]
        )

    def _synthesize_results(self, state: OrchestratorState) -> str:
        """
        Synthesize multi-agent outputs into a coherent response.
        
        Args:
            state: Final orchestrator state
            
        Returns:
            Synthesized response string
        """
        query = state["query"]
        outputs = state["agent_outputs"]
        
        if not outputs:
            return "I couldn't find relevant information for your query. Please try rephrasing or ask about a specific county or state."
        
        # Build response sections
        sections = []
        
        # Primary agent output
        primary = state["primary_intent"]
        if primary in outputs:
            primary_output = outputs[primary]
            if isinstance(primary_output, AgentOutput):
                sections.append(self._format_agent_output(primary, primary_output))
            elif isinstance(primary_output, dict):
                sections.append(self._format_dict_output(primary, primary_output))
        
        # Secondary agent outputs (if multi-agent)
        for agent_name, output in outputs.items():
            if agent_name != primary:
                if isinstance(output, AgentOutput):
                    sections.append(self._format_agent_output(agent_name, output, secondary=True))
                elif isinstance(output, dict):
                    sections.append(self._format_dict_output(agent_name, output, secondary=True))
        
        # Combine sections
        response = "\n\n".join(sections)
        
        # Add confidence indicator
        if state["confidence"] < 0.5:
            response += "\n\n_Note: I'm less confident about this response. Consider providing more specific details like a county name or FIPS code._"
        
        return response

    def _format_agent_output(self, agent_name: str, output: AgentOutput,
                             secondary: bool = False) -> str:
        """Format an AgentOutput for display."""
        prefix = "### " if not secondary else "#### "
        
        agent_label = {
            "climate": "🌡️ Climate Analysis",
            "vulnerability": "🏥 Vulnerability Assessment",
            "realtime": "⚠️ Real-Time Alerts",
            "planning": "📊 Planning & Forecasting"
        }.get(agent_name, agent_name.title())
        
        lines = [f"{prefix}{agent_label}"]
        
        if output.error:
            lines.append(f"_Error: {output.error}_")
            return "\n".join(lines)
        
        # Add insights
        for insight in output.insights[:3]:  # Top 3 insights
            lines.append(f"• {insight}")
        
        # Add tool results summary
        successful_tools = [r for r in output.results if r.success]
        if successful_tools:
            lines.append(f"\n_Used {len(successful_tools)} data sources_")
        
        return "\n".join(lines)

    def _format_dict_output(self, agent_name: str, output: Dict,
                            secondary: bool = False) -> str:
        """Format a dictionary output for display."""
        prefix = "### " if not secondary else "#### "
        
        agent_label = {
            "climate": "🌡️ Climate Analysis",
            "vulnerability": "🏥 Vulnerability Assessment",
            "realtime": "⚠️ Real-Time Alerts",
            "planning": "📊 Planning & Forecasting"
        }.get(agent_name, agent_name.title())
        
        lines = [f"{prefix}{agent_label}"]
        
        if "error" in output:
            lines.append(f"_Error: {output['error']}_")
            return "\n".join(lines)
        
        # Extract key findings based on agent type
        if agent_name == "climate":
            if "trends" in output:
                lines.append(f"• Temperature trend: {output['trends'].get('mean_temp', {}).get('slope_per_decade', 'N/A')}°F per decade")
            if "projection" in output:
                lines.append(f"• Projected change: {output['projection'].get('temp_change_f', 'N/A')}°F")
        
        elif agent_name == "vulnerability":
            if isinstance(output, list):
                lines.append(f"• Found {len(output)} matching counties")
            elif "risk_score" in output:
                lines.append(f"• Risk score: {output['risk_score']:.3f}")
        
        elif agent_name == "realtime":
            if "alerts" in output:
                lines.append(f"• {len(output['alerts'])} active alerts")
        
        elif agent_name == "planning":
            if "roi" in output or "interventions" in output:
                lines.append("• Cost-effectiveness analysis available")
        
        return "\n".join(lines)

    def _extract_hyperdimensional_insights(self, state: OrchestratorState) -> List[str]:
        """
        Extract cross-domain insights from multi-agent outputs.
        
        These are insights that emerge from combining outputs
        from multiple specialized agents.
        
        Returns:
            List of insight strings
        """
        insights = []
        outputs = state["agent_outputs"]
        
        # Climate + Vulnerability = Compound risk insight
        if "climate" in outputs and "vulnerability" in outputs:
            insights.append("Cross-domain analysis: Climate projections combined with current vulnerability patterns reveal potential compound risk scenarios.")
        
        # Realtime + Vulnerability = Alert prioritization
        if "realtime" in outputs and "vulnerability" in outputs:
            insights.append("Alert prioritization: Weather alerts are weighted by underlying county vulnerability for enhanced risk assessment.")
        
        # Planning + Climate = Adaptation pathways
        if "planning" in outputs and "climate" in outputs:
            insights.append("Strategic foresight: Climate scenarios inform long-term intervention planning and ROI projections.")
        
        # All four agents = Comprehensive assessment
        if len(outputs) >= 3:
            insights.append("Comprehensive assessment: Multi-dimensional analysis spanning climate, vulnerability, real-time conditions, and planning horizons.")
        
        return insights

    def _generate_follow_up_queries(self, query: str, state: OrchestratorState) -> List[str]:
        """
        Generate suggested follow-up queries based on the current query and results.
        
        Returns:
            List of suggested follow-up query strings
        """
        suggestions = []
        primary = state["primary_intent"]
        
        # Context-aware suggestions
        if "county" in query.lower():
            if primary == "vulnerability":
                suggestions.append("What interventions would be most cost-effective for this county?")
                suggestions.append("How does this county compare to state averages?")
            elif primary == "climate":
                suggestions.append("What are the projected climate risks for this county by 2050?")
                suggestions.append("How does this county's climate vulnerability compare to neighbors?")
            elif primary == "realtime":
                suggestions.append("What is this county's baseline vulnerability profile?")
            elif primary == "planning":
                suggestions.append("What climate trends should inform this planning analysis?")
        
        if "state" in query.lower():
            suggestions.append("Which counties in this state have the highest compound risk?")
            suggestions.append("Show me the top 10 most vulnerable counties in this state.")
        
        if not suggestions:
            suggestions = [
                "Which counties have the highest compound risk?",
                "Show me counties with zero hospital redundancy.",
                "What are the current weather alerts for Missouri?"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions

    def _log_execution(self, record: Dict) -> None:
        """Log execution for monitoring."""
        # Could write to file, database, or monitoring system
        pass

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get combined tool catalog from all agents."""
        all_tools = []
        for agent in self.agents.values():
            all_tools.extend(agent.get_tools())
        return all_tools

    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of all agents and their capabilities."""
        summary = {}
        for key, agent in self.agents.items():
            summary[key] = {
                "name": agent.name,
                "description": agent.description,
                "tool_count": len(agent.get_tool_names()),
                "tools": agent.get_tool_names(),
                "version": getattr(agent, "version", "1.0.0")
            }
        
        return {
            "total_agents": len(self.agents),
            "total_tools": len(self._tool_index),
            "agents": summary,
            "archia_mode": "cloud" if (self.use_archia_cloud and self._archia_client) else "local"
        }

    def export_archia_configs(self) -> Dict[str, Any]:
        """Export all agent configurations in Archia-compatible format."""
        configs = {}
        for key, agent in self.agents.items():
            configs[key] = agent.get_archia_config()
        return configs

    def get_execution_plan(self, query: str) -> Dict[str, Any]:
        """
        Preview the execution plan for a query without executing.
        
        Useful for debugging and understanding routing decisions.
        """
        intent = self.flow.classify_intent(query)
        graph = self.flow.build_execution_graph(intent, query)
        plan = self.flow.get_execution_plan()
        
        return {
            "query": query,
            "intent_classification": {
                "primary": intent.primary,
                "confidence": intent.confidence,
                "scores": intent.scores,
                "multi_agent": intent.requires_multi_agent()
            },
            "execution_plan": plan
        }


# ── CLI Testing ──────────────────────────────────────────────────────

if __name__ == "__main__":
    orchestrator = AgentOrchestrator(use_archia_cloud=False)

    # Print summary
    summary = orchestrator.get_agent_summary()
    print(f"\n{'='*60}")
    print(f"ResilienceAI Multi-Agent System")
    print(f"{'='*60}")
    print(f"Total agents: {summary['total_agents']}")
    print(f"Total tools: {summary['total_tools']}")
    print(f"Mode: {summary['archia_mode']}")
    print()

    for key, info in summary["agents"].items():
        print(f"  [{key}] {info['name']} v{info['version']}")
        print(f"    {info['description']}")
        print(f"    Tools ({info['tool_count']}): {', '.join(info['tools'][:5])}{'...' if info['tool_count'] > 5 else ''}")
        print()

    # Test routing with execution plan preview
    test_queries = [
        "What are the climate trends in Boone County, Missouri?",
        "Show me the most vulnerable counties in Missouri",
        "Are there any active weather alerts for MO?",
        "What intervention would be most cost-effective for county 29019?",
        "Compare climate and vulnerability for county 29189",
    ]

    print("\n" + "="*60)
    print("Query Routing Tests")
    print("="*60)
    
    for q in test_queries:
        print(f"\n📝 Query: {q}")
        print("-" * 40)
        
        # Show routing
        routing = orchestrator.route_query(q)
        print(f"   Primary: {routing['primary_agent']} (confidence: {routing['confidence']:.2f})")
        print(f"   Multi-agent: {routing['multi_agent']}")
        print(f"   Scores: {routing['scores']}")
        
        # Show execution plan
        plan = orchestrator.get_execution_plan(q)
        print(f"   Agents: {plan['execution_plan']['agents']}")
        print(f"   Parallel groups: {plan['execution_plan']['parallel_groups']}")

    # Full execution test
    print("\n" + "="*60)
    print("Full Execution Test")
    print("="*60)
    
    test_query = "What are the most vulnerable counties in Missouri?"
    print(f"\n📝 Query: {test_query}")
    
    response = orchestrator.execute_query(test_query, context={"state": "MO"})
    
    print(f"\n✅ Response:")
    print(f"{response.response}")
    
    print(f"\n💡 Insights:")
    for insight in response.insights:
        print(f"   • {insight}")
    
    print(f"\n🔍 Follow-up suggestions:")
    for suggestion in response.follow_up_queries:
        print(f"   • {suggestion}")
    
    print(f"\n⏱️  Execution time: {response.execution_time_ms:.1f}ms")
    print(f"🎯 Confidence: {response.confidence:.2f}")
    print(f"🔧 Mode: {response.archia_mode}")
