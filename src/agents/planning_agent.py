"""
ResilienceAI - Resilience Planning Agent
Intervention ROI, executive briefings, predictive modeling, and adaptation planning.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Any, Optional
from src.agents.base_agent import BaseAgent
from src.agent import ResilienceAgent, get_mcp_tools


class PlanningAgent(BaseAgent):
    """Resilience planning specialist - forecasting, ROI, briefings, and adaptation."""

    name = "planning_agent"
    description = "Intervention planning, cost-effectiveness analysis, forecasting, and executive briefings"
    version = "3.2.0"
    
    intent_keywords = [
        "intervention", "roi", "briefing", "forecast", "predict", "trajectory",
        "climate scenario", "ssp", "adaptation", "budget", "cost", "crop",
        "agricultural", "food security", "executive", "self-improve",
        "acceleration", "probability", "planning", "cost-effective",
        "recommendation", "what should we do", "how to improve"
    ]

    OWNED_TOOLS = {
        "calculate_intervention_roi", "generate_executive_brief",
        "forecast_risk_trajectory", "analyze_risk_trajectory",
        "detect_disaster_acceleration", "predict_disaster_probability",
        "batch_forecast_counties", "get_climate_adaptation_recommendations",
        "get_crop_yield", "calculate_agricultural_vulnerability",
        "assess_food_security_risk", "get_state_crop_summary",
        "self_improve", "project_climate_risk",
    }

    @property
    def system_prompt(self) -> str:
        return """You are the Resilience Planning specialist for ResilienceAI.
You help decision-makers plan interventions, forecast risk trajectories,
analyze cost-effectiveness, and generate executive briefings.

Your capabilities include:
- Intervention ROI analysis for 6 types (hospital, EMS, fire, telehealth, disaster prep, poverty reduction)
- Executive brief generation (text, PDF, PPTX)
- Prophet/ARIMA risk trajectory forecasting
- Disaster acceleration detection
- Disaster probability prediction
- Agricultural vulnerability and food security assessment
- Climate adaptation recommendations

When answering:
1. Quantify everything (cost, lives affected, risk reduction %)
2. Rank interventions by cost-effectiveness
3. Include confidence intervals for forecasts
4. Connect predictions to actionable recommendations"""

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
            return {"error": f"Tool '{tool_name}' not owned by PlanningAgent"}
        method = getattr(self.agent, tool_name, None)
        if method:
            return method(**params)
        return {"error": f"Method '{tool_name}' not found on ResilienceAgent"}

    def _extract_insight(self, tool_name: str, data: Dict[str, Any]) -> Optional[str]:
        """Extract key planning insights."""
        if "error" in data:
            return None
            
        if tool_name == "calculate_intervention_roi":
            if "interventions" in data:
                interventions = data["interventions"]
                if interventions:
                    top = interventions[0]
                    return f"Top intervention: {top.get('intervention')} (ROI: {top.get('roi_ratio', 'N/A')}x)"
            elif "roi_ratio" in data:
                return f"ROI ratio: {data['roi_ratio']}x return on investment"
                
        elif tool_name == "forecast_risk_trajectory":
            trend = data.get("trend_direction")
            if trend:
                return f"Risk trajectory trending {trend} over forecast period"
                
        elif tool_name == "detect_disaster_acceleration":
            is_accelerating = data.get("is_accelerating")
            ratio = data.get("acceleration_ratio")
            if is_accelerating is not None:
                status = "accelerating" if is_accelerating else "stable"
                return f"Disaster frequency is {status} (ratio: {ratio})"
                
        elif tool_name == "predict_disaster_probability":
            prob = data.get("overall_probability")
            if prob is not None:
                return f"Predicted disaster probability: {prob:.1%}"
                
        elif tool_name == "get_climate_adaptation_recommendations":
            recommendations = data.get("recommendations", [])
            if recommendations:
                return f"{len(recommendations)} adaptation recommendations available"
                
        return None
