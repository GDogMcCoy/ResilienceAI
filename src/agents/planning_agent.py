"""
ResilienceAI - Resilience Planning Agent
Intervention ROI, executive briefings, predictive modeling, and adaptation planning.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Any
from src.agents.base_agent import BaseAgent
from src.agent import ResilienceAgent, get_mcp_tools


class PlanningAgent(BaseAgent):
    """Resilience planning specialist - forecasting, ROI, briefings, and adaptation."""

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
    def name(self) -> str:
        return "planning_agent"

    @property
    def description(self) -> str:
        return "Intervention planning, cost-effectiveness analysis, forecasting, and executive briefings"

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
        self.agent = ResilienceAgent()

    def get_tools(self) -> List[Dict[str, Any]]:
        return [t for t in get_mcp_tools() if t["name"] in self.OWNED_TOOLS]

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self.OWNED_TOOLS:
            return {"error": f"Tool '{tool_name}' not owned by PlanningAgent"}
        method = getattr(self.agent, tool_name, None)
        if method:
            return method(**params)
        return {"error": f"Method '{tool_name}' not found on ResilienceAgent"}
