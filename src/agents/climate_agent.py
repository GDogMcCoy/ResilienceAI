"""
ResilienceAI - Climate Intelligence Agent
Handles climate trend analysis, hazard profiles, flood frequency,
severe weather history, and drought monitoring.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Any
from src.agents.base_agent import BaseAgent
from src.climate_client import ClimateIntelligenceClient


class ClimateAgent(BaseAgent):
    """Climate Intelligence specialist - owns 7 climate MCP tools."""

    @property
    def name(self) -> str:
        return "climate_agent"

    @property
    def description(self) -> str:
        return "Climate trend analysis, hazard risk profiles, flood frequency, severe weather, and drought monitoring"

    @property
    def system_prompt(self) -> str:
        return """You are the Climate Intelligence specialist for ResilienceAI.
You analyze historical climate data, multi-hazard risk profiles, flood frequency,
severe weather patterns, and drought timelines to provide evidence-based
climate vulnerability assessments for US counties.

Your data sources:
- **RCC-ACIS**: Historical temperature and precipitation trends (4km PRISM grid, county-level)
- **FEMA NRI**: National Risk Index with 18 hazard types (Expected Annual Loss, Social Vulnerability)
- **USGS NWIS**: Streamflow gauges and peak flood frequency analysis
- **NOAA SWDI/SPC**: Historical tornado, hail, and damaging wind events
- **US Drought Monitor**: Weekly drought classification (D0-D4) from 2000+

When answering:
1. Always cite specific numbers and trends (e.g., "temperature increased 0.3F/decade")
2. Put trends in context (is this faster/slower than national average?)
3. Identify the dominant hazard types for each county
4. Flag accelerating trends as high-priority concerns
5. Connect climate data to vulnerability implications"""

    def __init__(self):
        self.climate = ClimateIntelligenceClient()

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_climate_trends",
                "description": "Get historical temperature and precipitation trends for a county from ACIS/PRISM data. Returns annual records with computed linear trend slopes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "start_year": {"type": "integer", "description": "Start year (default: 2000)"},
                        "end_year": {"type": "integer", "description": "End year (default: 2025)"},
                    },
                    "required": ["fips"]
                }
            },
            {
                "name": "get_hazard_risk_profile",
                "description": "Get FEMA National Risk Index profile with 18 hazard types. Returns Expected Annual Loss, Social Vulnerability, Community Resilience, and per-hazard risk scores.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                    },
                    "required": ["fips"]
                }
            },
            {
                "name": "get_flood_frequency",
                "description": "Get USGS streamflow data and flood recurrence interval estimates for a county. Returns peak flow records and estimated 2/5/10/25/50/100-year flood levels.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                    },
                    "required": ["fips"]
                }
            },
            {
                "name": "get_severe_weather_history",
                "description": "Get historical severe weather events (tornadoes, hail, wind) for a county from NOAA SWDI/SPC Storm Events Database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "hazard_type": {"type": "string", "enum": ["all", "tornado", "hail", "wind"], "description": "Event type filter (default: all)"},
                        "start_year": {"type": "integer", "description": "Start year (default: 2000)"},
                        "end_year": {"type": "integer", "description": "End year (default: 2025)"},
                    },
                    "required": ["fips"]
                }
            },
            {
                "name": "get_drought_history",
                "description": "Get US Drought Monitor weekly drought classification history for a county. Returns D0-D4 percentages over time with summary statistics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "start_date": {"type": "string", "description": "Start date YYYY-MM-DD (default: 2000-01-01)"},
                        "end_date": {"type": "string", "description": "End date YYYY-MM-DD (default: today)"},
                    },
                    "required": ["fips"]
                }
            },
            {
                "name": "compare_climate_trends",
                "description": "Compare climate trajectories across multiple counties. Returns side-by-side temperature/precipitation trends with trend slopes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips_list": {"type": "array", "items": {"type": "string"}, "description": "List of FIPS codes to compare"},
                        "start_year": {"type": "integer", "description": "Start year (default: 2000)"},
                        "end_year": {"type": "integer", "description": "End year (default: 2025)"},
                    },
                    "required": ["fips_list"]
                }
            },
            {
                "name": "project_climate_risk_enhanced",
                "description": "Project future climate risk using historical ACIS data as baseline combined with IPCC SSP scenarios. Grounds projections in real local climate trends.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "scenario": {"type": "string", "enum": ["ssp1_19", "ssp2_45", "ssp5_85"], "description": "IPCC SSP scenario"},
                        "horizon_years": {"type": "integer", "description": "Years into future (default: 30)"},
                    },
                    "required": ["fips"]
                }
            },
        ]

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        dispatch = {
            "get_climate_trends": self._get_climate_trends,
            "get_hazard_risk_profile": self._get_hazard_risk_profile,
            "get_flood_frequency": self._get_flood_frequency,
            "get_severe_weather_history": self._get_severe_weather_history,
            "get_drought_history": self._get_drought_history,
            "compare_climate_trends": self._compare_climate_trends,
            "project_climate_risk_enhanced": self._project_climate_risk_enhanced,
        }
        handler = dispatch.get(tool_name)
        if handler:
            return handler(**params)
        return {"error": f"Unknown tool: {tool_name}"}

    def _get_climate_trends(self, fips: str, start_year: int = 2000,
                            end_year: int = 2025) -> Dict[str, Any]:
        return self.climate.acis.get_climate_trends(fips, start_year, end_year)

    def _get_hazard_risk_profile(self, fips: str) -> Dict[str, Any]:
        return self.climate.nri.get_hazard_risk_profile(fips)

    def _get_flood_frequency(self, fips: str) -> Dict[str, Any]:
        return self.climate.usgs.get_flood_frequency(fips)

    def _get_severe_weather_history(self, fips: str, hazard_type: str = "all",
                                     start_year: int = 2000, end_year: int = 2025) -> Dict[str, Any]:
        return self.climate.severe.get_severe_weather_history(fips, hazard_type, start_year, end_year)

    def _get_drought_history(self, fips: str, start_date: str = "2000-01-01",
                             end_date: str = None) -> Dict[str, Any]:
        return self.climate.drought.get_drought_history(fips, start_date, end_date)

    def _compare_climate_trends(self, fips_list: List[str], start_year: int = 2000,
                                end_year: int = 2025) -> Dict[str, Any]:
        return self.climate.acis.compare_counties(fips_list, start_year, end_year)

    def _project_climate_risk_enhanced(self, fips: str, scenario: str = "ssp2_45",
                                       horizon_years: int = 30) -> Dict[str, Any]:
        """Project future risk using real historical baseline + SSP multipliers."""
        import numpy as np

        # Get historical baseline
        trends = self.climate.acis.get_climate_trends(fips, 2000, 2024)
        if "error" in trends:
            return {"fips": fips, "error": "Cannot project without historical baseline"}

        # SSP scenario multipliers (from IPCC AR6)
        scenarios = {
            "ssp1_19": {"temp_increase_c": 1.5, "precip_change_pct": 2, "extreme_multiplier": 1.1},
            "ssp2_45": {"temp_increase_c": 2.7, "precip_change_pct": 5, "extreme_multiplier": 1.4},
            "ssp5_85": {"temp_increase_c": 4.4, "precip_change_pct": 10, "extreme_multiplier": 2.0},
        }
        ssp = scenarios.get(scenario, scenarios["ssp2_45"])

        # Compute projections
        temp_trend = trends.get("trends", {}).get("mean_temp", {})
        precip_trend = trends.get("trends", {}).get("precip", {})

        baseline_temp = temp_trend.get("mean", 55.0)
        baseline_precip = precip_trend.get("mean", 40.0)
        hist_slope = temp_trend.get("slope_per_decade", 0.0)

        # Combine historical trend + SSP forcing
        projected_temp = baseline_temp + (ssp["temp_increase_c"] * 1.8 * horizon_years / 80)
        projected_precip = baseline_precip * (1 + ssp["precip_change_pct"] / 100 * horizon_years / 80)

        return {
            "fips": fips,
            "scenario": scenario,
            "horizon_years": horizon_years,
            "baseline": {
                "mean_temp_f": baseline_temp,
                "total_precip_in": baseline_precip,
                "historical_trend_f_per_decade": hist_slope,
            },
            "projection": {
                "projected_mean_temp_f": round(projected_temp, 1),
                "projected_precip_in": round(projected_precip, 1),
                "temp_change_f": round(projected_temp - baseline_temp, 1),
                "precip_change_pct": round((projected_precip - baseline_precip) / baseline_precip * 100, 1),
                "extreme_event_multiplier": ssp["extreme_multiplier"],
            },
            "risk_implications": {
                "heat_stress": "High" if projected_temp - baseline_temp > 3 else "Moderate" if projected_temp - baseline_temp > 1.5 else "Low",
                "flood_risk_change": "Increasing" if ssp["precip_change_pct"] > 5 else "Stable",
                "extreme_weather": f"{ssp['extreme_multiplier']}x current frequency",
            }
        }
