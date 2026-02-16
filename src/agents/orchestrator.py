"""
ResilienceAI - Multi-Agent Orchestrator
Routes queries to specialized agents, dispatches tool calls, and combines results.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Any, Optional
from src.agents.climate_agent import ClimateAgent
from src.agents.vulnerability_agent import VulnerabilityAgent
from src.agents.realtime_agent import RealtimeAgent
from src.agents.planning_agent import PlanningAgent


class AgentOrchestrator:
    """Routes natural language queries and tool calls to specialized agents.

    4 specialist agents:
    - ClimateAgent: Climate trends, hazard profiles, drought, flood, severe weather
    - VulnerabilityAgent: County risk, infrastructure, demographics, spatial analysis
    - RealtimeAgent: Weather alerts, subscriptions, emergency dispatch
    - PlanningAgent: Intervention ROI, forecasting, briefings, agriculture
    """

    ROUTING_KEYWORDS = {
        "climate": [
            "climate", "temperature", "precipitation", "drought", "flood frequency",
            "hazard risk", "nri", "acis", "severe weather", "hail", "tornado history",
            "heat wave", "wildfire risk", "climate trend", "warming", "rainfall",
        ],
        "vulnerability": [
            "vulnerability", "county", "risk score", "compound risk", "infrastructure",
            "equity", "disparity", "hotspot", "spatial", "fips", "hospital", "ems",
            "redundancy", "isolation", "poverty", "uninsured", "demographics",
            "geojson", "fhir", "export", "missouri health",
        ],
        "realtime": [
            "alert", "weather alert", "noaa", "subscribe", "dispatch", "real-time",
            "monitoring", "acknowledge", "severe weather warning", "watch", "warning",
            "live", "active alert", "notification",
        ],
        "planning": [
            "intervention", "roi", "briefing", "forecast", "predict", "trajectory",
            "climate scenario", "ssp", "adaptation", "budget", "cost", "crop",
            "agricultural", "food security", "executive", "self-improve",
            "acceleration", "probability",
        ],
    }

    def __init__(self):
        self.agents = {
            "climate": ClimateAgent(),
            "vulnerability": VulnerabilityAgent(),
            "realtime": RealtimeAgent(),
            "planning": PlanningAgent(),
        }
        self._tool_index = self._build_tool_index()
        self.conversation_history: List[Dict] = []

    def _build_tool_index(self) -> Dict[str, str]:
        """Map tool names to owning agent keys."""
        index = {}
        for agent_key, agent in self.agents.items():
            for tool_name in agent.get_tool_names():
                index[tool_name] = agent_key
        return index

    def route_query(self, query: str) -> str:
        """Determine which agent should handle a natural language query."""
        query_lower = query.lower()
        scores = {}
        for agent_key, keywords in self.ROUTING_KEYWORDS.items():
            scores[agent_key] = sum(1 for kw in keywords if kw in query_lower)

        if max(scores.values()) == 0:
            return "vulnerability"  # Default fallback
        return max(scores, key=scores.get)

    def execute_tool(self, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a specific MCP tool, auto-routing to the owning agent."""
        agent_key = self._tool_index.get(tool_name)
        if not agent_key:
            return {"error": f"Tool '{tool_name}' not found in any agent"}
        return self.agents[agent_key].execute_tool(tool_name, params or {})

    def execute_query(self, query: str) -> Dict[str, Any]:
        """Route a natural language query to the appropriate specialist."""
        target = self.route_query(query)
        agent = self.agents[target]

        self.conversation_history.append({
            "role": "user",
            "query": query,
            "routed_to": target,
        })

        return {
            "routed_to": target,
            "agent_name": agent.name,
            "agent_description": agent.description,
            "available_tools": agent.get_tool_names(),
            "system_prompt": agent.system_prompt,
            "message": f"Query routed to {agent.name}. Available tools: {', '.join(agent.get_tool_names())}",
        }

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
            }
        return {
            "total_agents": len(self.agents),
            "total_tools": len(self._tool_index),
            "agents": summary,
        }

    def export_archia_configs(self) -> Dict[str, Any]:
        """Export all agent configurations in Archia-compatible format."""
        configs = {}
        for key, agent in self.agents.items():
            configs[key] = agent.get_archia_config()
        return configs


# ── CLI Testing ──────────────────────────────────────────────────────

if __name__ == "__main__":
    orchestrator = AgentOrchestrator()

    # Print summary
    summary = orchestrator.get_agent_summary()
    print(f"\nResilienceAI Multi-Agent System")
    print(f"Total agents: {summary['total_agents']}")
    print(f"Total tools: {summary['total_tools']}")
    print()

    for key, info in summary["agents"].items():
        print(f"  [{key}] {info['name']}: {info['tool_count']} tools")
        print(f"    {info['description']}")
        print(f"    Tools: {', '.join(info['tools'][:5])}...")
        print()

    # Test routing
    test_queries = [
        "What are the climate trends in Boone County, Missouri?",
        "Show me the most vulnerable counties in Missouri",
        "Are there any active weather alerts for MO?",
        "What intervention would be most cost-effective for county 29019?",
    ]

    print("=== Query Routing Test ===")
    for q in test_queries:
        result = orchestrator.execute_query(q)
        print(f"  Q: {q[:60]}...")
        print(f"  -> {result['agent_name']} ({len(result['available_tools'])} tools)")
        print()
