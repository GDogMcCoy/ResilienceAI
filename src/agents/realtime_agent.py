"""
ResilienceAI - Real-Time Operations Agent
Weather alerts, alert subscription management, and real-time monitoring.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Any
from src.agents.base_agent import BaseAgent
from src.agent import ResilienceAgent, get_mcp_tools


class RealtimeAgent(BaseAgent):
    """Real-time operations specialist - weather alerts, subscriptions, and monitoring."""

    OWNED_TOOLS = {
        "get_weather_alerts", "correlate_weather_with_vulnerability",
        "get_high_impact_weather", "should_trigger_weather_alert",
        "subscribe_to_alerts", "unsubscribe_from_alerts",
        "list_alert_subscriptions", "dispatch_alert",
        "get_active_alerts", "acknowledge_alert", "get_real_time_alerts",
    }

    @property
    def name(self) -> str:
        return "realtime_agent"

    @property
    def description(self) -> str:
        return "Real-time weather monitoring, alert management, and emergency dispatch"

    @property
    def system_prompt(self) -> str:
        return """You are the Real-Time Operations specialist for ResilienceAI.
You monitor live weather conditions, manage alert subscriptions, and coordinate
emergency notifications for county-level disaster response.

Your capabilities include:
- NOAA NWS real-time weather alerts by state and county
- Weather-vulnerability correlation (composite risk scoring)
- Alert subscription management (subscribe, unsubscribe, list)
- Alert dispatch and acknowledgment for emergency notifications
- Threshold-based risk alerting with severity levels

When answering:
1. Prioritize by severity (Extreme > Severe > Moderate > Minor)
2. Cross-reference weather with county vulnerability scores
3. Recommend alert triggers for high-vulnerability counties under severe weather
4. Track active alerts and subscription status"""

    def __init__(self):
        self.agent = ResilienceAgent()

    def get_tools(self) -> List[Dict[str, Any]]:
        return [t for t in get_mcp_tools() if t["name"] in self.OWNED_TOOLS]

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self.OWNED_TOOLS:
            return {"error": f"Tool '{tool_name}' not owned by RealtimeAgent"}
        method = getattr(self.agent, tool_name, None)
        if method:
            return method(**params)
        return {"error": f"Method '{tool_name}' not found on ResilienceAgent"}
