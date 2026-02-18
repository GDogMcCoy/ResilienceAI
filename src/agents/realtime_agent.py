"""
ResilienceAI - Real-Time Operations Agent
Weather alerts, alert subscription management, and real-time monitoring.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Any, Optional
from src.agents.base_agent import BaseAgent
from src.agent import ResilienceAgent, get_mcp_tools


class RealtimeAgent(BaseAgent):
    """Real-time operations specialist - weather alerts, subscriptions, and monitoring."""

    name = "realtime_agent"
    description = "Real-time weather monitoring, alert management, and emergency dispatch"
    version = "3.2.0"
    
    intent_keywords = [
        "alert", "weather alert", "noaa", "subscribe", "dispatch", "real-time",
        "monitoring", "acknowledge", "severe weather warning", "watch", "warning",
        "live", "active alert", "notification", "current weather", "emergency",
        " tornado warning", "flood warning", "storm warning", "active now"
    ]

    OWNED_TOOLS = {
        "get_weather_alerts", "correlate_weather_with_vulnerability",
        "get_high_impact_weather", "should_trigger_weather_alert",
        "subscribe_to_alerts", "unsubscribe_from_alerts",
        "list_alert_subscriptions", "dispatch_alert",
        "get_active_alerts", "acknowledge_alert", "get_real_time_alerts",
    }

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
        super().__init__()
        self.agent = ResilienceAgent()

    def _register_tool_handlers(self) -> None:
        """Register tool handlers - tools are dispatched to ResilienceAgent."""
        pass  # Tools are dispatched dynamically in execute_tool

    def get_tools(self) -> List[Dict[str, Any]]:
        return [t for t in get_mcp_tools() if t["name"] in self.OWNED_TOOLS]

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self.OWNED_TOOLS:
            return {"error": f"Tool '{tool_name}' not owned by RealtimeAgent"}
        method = getattr(self.agent, tool_name, None)
        if method:
            return method(**params)
        return {"error": f"Method '{tool_name}' not found on ResilienceAgent"}

    def _extract_insight(self, tool_name: str, data: Dict[str, Any]) -> Optional[str]:
        """Extract key real-time insights."""
        if "error" in data:
            return None
            
        if tool_name == "get_weather_alerts":
            count = data.get("alert_count", 0)
            if count > 0:
                return f"{count} active weather alerts for specified area"
                
        elif tool_name == "get_high_impact_weather":
            count = data.get("alert_count", 0)
            severity = data.get("min_severity", "Severe")
            if count > 0:
                return f"{count} high-impact weather alerts ({severity}+) nationwide"
                
        elif tool_name == "correlate_weather_with_vulnerability":
            enhanced_risk = data.get("enhanced_risk_score")
            if enhanced_risk is not None:
                return f"Enhanced risk score combining weather and vulnerability: {enhanced_risk:.2f}"
                
        elif tool_name == "get_active_alerts":
            count = data.get("count", 0)
            if count > 0:
                return f"{count} unacknowledged active alerts"
                
        elif tool_name == "should_trigger_weather_alert":
            should_trigger = data.get("should_trigger", False)
            if should_trigger:
                return "Weather conditions meet threshold for vulnerability-based alerting"
                
        return None
