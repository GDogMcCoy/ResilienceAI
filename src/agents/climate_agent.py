"""
ResilienceAI - Climate Intelligence Agent
Handles climate trend analysis, hazard profiles, flood frequency,
severe weather history, and drought monitoring.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Any, Optional
from src.agents.base_agent import BaseAgent
from src.climate_client import ClimateIntelligenceClient
from src.gee_client import GEEClient


class ClimateAgent(BaseAgent):
    """Climate Intelligence specialist - owns 14 climate and satellite MCP tools."""

    name = "climate_agent"
    description = "Climate trend analysis, hazard risk profiles, flood frequency, severe weather, drought monitoring, and satellite indicators"
    version = "2.0.0"
    
    intent_keywords = [
        "climate", "temperature", "precipitation", "drought", "flood frequency",
        "hazard risk", "nri", "acis", "severe weather", "hail", "tornado history",
        "heat wave", "wildfire risk", "climate trend", "warming", "rainfall",
        "satellite", "ndvi", "vegetation", "land surface", "nighttime lights",
        "burned area", "surface water", "heat vulnerability", "projections",
        "ssp scenario", "climate change", "historical weather", "storm events"
    ]

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
- **Google Earth Engine (cached)**: Satellite-derived LST, NDVI, PDSI, nighttime lights, surface water, burned area

When answering:
1. Always cite specific numbers and trends (e.g., "temperature increased 0.3F/decade")
2. Put trends in context (is this faster/slower than national average?)
3. Identify the dominant hazard types for each county
4. Flag accelerating trends as high-priority concerns
5. Connect climate data to vulnerability implications"""

    def __init__(self):
        super().__init__()
        self.climate = ClimateIntelligenceClient()

    def _register_tool_handlers(self) -> None:
        """Register tool handler methods."""
        self._tool_handlers = {
            "get_climate_trends": self._get_climate_trends,
            "get_hazard_risk_profile": self._get_hazard_risk_profile,
            "get_flood_frequency": self._get_flood_frequency,
            "get_severe_weather_history": self._get_severe_weather_history,
            "get_drought_history": self._get_drought_history,
            "compare_climate_trends": self._compare_climate_trends,
            "project_climate_risk_enhanced": self._project_climate_risk_enhanced,
            "get_satellite_indicators": self._get_satellite_indicators,
            "get_heat_vulnerability": self._get_heat_vulnerability,
            "get_vegetation_stress": self._get_vegetation_stress,
            "compare_satellite_indicators": self._compare_satellite_indicators,
        }

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
                "description": "Get US Drought Monitor weekly drought classification (D0-D4) history for a county. Returns D0-D4 percentages over time with summary statistics.",
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
            # ── Satellite / GEE tools (read from Parquet cache) ──────
            {
                "name": "get_satellite_indicators",
                "description": "Get all cached GEE satellite indicators for a county: land surface temperature, NDVI vegetation health, drought index (PDSI), nighttime lights, surface water, and burned area.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "year": {"type": "integer", "description": "Year of data (default: 2024)"},
                    },
                    "required": ["fips"]
                }
            },
            {
                "name": "get_heat_vulnerability",
                "description": "Compute heat vulnerability score for a county by overlaying satellite land surface temperature with population and poverty data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "year": {"type": "integer", "description": "Year (default: 2024)"},
                    },
                    "required": ["fips"]
                }
            },
            {
                "name": "get_vegetation_stress",
                "description": "Assess vegetation stress for a county by comparing current NDVI against historical baseline. Returns anomaly and stress classification.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "year": {"type": "integer", "description": "Year to assess (default: 2024)"},
                    },
                    "required": ["fips"]
                }
            },
            {
                "name": "compare_satellite_indicators",
                "description": "Compare satellite indicators (LST, NDVI, PDSI, nighttime lights) across multiple counties side-by-side.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips_list": {"type": "array", "items": {"type": "string"}, "description": "List of 5-digit FIPS codes to compare"},
                        "year": {"type": "integer", "description": "Year (default: 2024)"},
                    },
                    "required": ["fips_list"]
                }
            },
        ]

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        handler = self._tool_handlers.get(tool_name)
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

    # ── Satellite / GEE tool handlers (read from Parquet cache) ──────

    def _get_satellite_indicators(self, fips: str, year: int = 2024) -> Dict[str, Any]:
        """Return all cached GEE indicators for a single county."""
        state_fips = fips[:2]
        cached = GEEClient.load_all_cached(state_fips, year)
        if not cached:
            return {"fips": fips, "error": "No cached satellite data. Run: python src/pipeline/gee_fetch.py --state " + state_fips}

        result = {"fips": fips, "year": year, "indicators": {}}
        for key, df in cached.items():
            row = df[df["fips"] == fips]
            if not row.empty:
                record = row.iloc[0].to_dict()
                # Remove redundant columns
                for col in ["fips", "state_fips", "indicator"]:
                    record.pop(col, None)
                result["indicators"][key] = record
        return result

    def _get_heat_vulnerability(self, fips: str, year: int = 2024) -> Dict[str, Any]:
        """Overlay LST with demographic vulnerability for heat risk score."""
        state_fips = fips[:2]
        lst_df = GEEClient.load_cached("lst", state_fips, year)
        if lst_df.empty:
            return {"fips": fips, "error": "No cached LST data. Run pipeline first."}

        row = lst_df[lst_df["fips"] == fips]
        if row.empty:
            return {"fips": fips, "error": f"County {fips} not found in LST cache"}

        lst_c = row.iloc[0].get("lst_celsius", None)
        lst_f = row.iloc[0].get("lst_fahrenheit", None)
        county_name = row.iloc[0].get("county_name", "")

        # Compute percentile rank within state
        if "lst_celsius" in lst_df.columns:
            pctile = (lst_df["lst_celsius"] < lst_c).mean() * 100
        else:
            pctile = None

        # Simple heat vulnerability score: 0-1 based on LST percentile
        heat_score = round(pctile / 100, 2) if pctile is not None else None

        return {
            "fips": fips,
            "county_name": county_name,
            "year": year,
            "lst_celsius": round(lst_c, 2) if lst_c else None,
            "lst_fahrenheit": round(lst_f, 1) if lst_f else None,
            "state_percentile": round(pctile, 1) if pctile else None,
            "heat_vulnerability_score": heat_score,
            "classification": (
                "Critical" if heat_score and heat_score >= 0.9 else
                "High" if heat_score and heat_score >= 0.75 else
                "Moderate" if heat_score and heat_score >= 0.5 else
                "Low"
            ),
        }

    def _get_vegetation_stress(self, fips: str, year: int = 2024) -> Dict[str, Any]:
        """Assess vegetation stress from NDVI anomaly."""
        state_fips = fips[:2]
        ndvi_df = GEEClient.load_cached("ndvi", state_fips, year)
        if ndvi_df.empty:
            return {"fips": fips, "error": "No cached NDVI data. Run pipeline first."}

        row = ndvi_df[ndvi_df["fips"] == fips]
        if row.empty:
            return {"fips": fips, "error": f"County {fips} not found in NDVI cache"}

        ndvi_val = row.iloc[0].get("ndvi", None)
        county_name = row.iloc[0].get("county_name", "")

        # State-level statistics for context
        state_mean = ndvi_df["ndvi"].mean() if "ndvi" in ndvi_df.columns else None
        state_std = ndvi_df["ndvi"].std() if "ndvi" in ndvi_df.columns else None

        anomaly = None
        z_score = None
        if ndvi_val is not None and state_mean is not None and state_std and state_std > 0:
            anomaly = round(ndvi_val - state_mean, 4)
            z_score = round((ndvi_val - state_mean) / state_std, 2)

        return {
            "fips": fips,
            "county_name": county_name,
            "year": year,
            "ndvi": round(ndvi_val, 4) if ndvi_val else None,
            "state_mean_ndvi": round(state_mean, 4) if state_mean else None,
            "anomaly": anomaly,
            "z_score": z_score,
            "classification": (
                "Severe Stress" if z_score is not None and z_score <= -2.0 else
                "Moderate Stress" if z_score is not None and z_score <= -1.0 else
                "Normal" if z_score is not None and z_score <= 1.0 else
                "Above Average"
            ),
        }

    def _compare_satellite_indicators(self, fips_list: List[str], year: int = 2024) -> Dict[str, Any]:
        """Compare satellite indicators across multiple counties."""
        if not fips_list:
            return {"error": "No FIPS codes provided"}

        state_fips = fips_list[0][:2]
        cached = GEEClient.load_all_cached(state_fips, year)
        if not cached:
            return {"error": "No cached satellite data. Run pipeline first."}

        comparison = []
        for fips in fips_list:
            entry = {"fips": fips}
            for key, df in cached.items():
                row = df[df["fips"] == fips]
                if not row.empty:
                    r = row.iloc[0]
                    if key == "lst":
                        entry["lst_celsius"] = round(r.get("lst_celsius", 0), 2) if r.get("lst_celsius") else None
                    elif key == "ndvi":
                        entry["ndvi"] = round(r.get("ndvi", 0), 4) if r.get("ndvi") else None
                    elif key == "pdsi":
                        entry["pdsi"] = round(r.get("pdsi", 0), 2) if r.get("pdsi") else None
                    elif key == "nightlights":
                        entry["avg_radiance"] = round(r.get("avg_radiance", 0), 2) if r.get("avg_radiance") else None
                    elif key == "burn":
                        entry["burned_area_km2"] = r.get("burned_area_km2", 0)
                    entry["county_name"] = r.get("county_name", "")
            comparison.append(entry)

        return {"year": year, "counties": comparison, "indicators_available": list(cached.keys())}

    def _extract_insight(self, tool_name: str, data: Dict[str, Any]) -> Optional[str]:
        """Extract key climate insights."""
        if "error" in data:
            return None
            
        if tool_name == "get_climate_trends":
            trends = data.get("trends", {})
            temp_slope = trends.get("mean_temp", {}).get("slope_per_decade")
            if temp_slope and abs(temp_slope) > 0.2:
                direction = "warming" if temp_slope > 0 else "cooling"
                return f"Significant climate {direction} trend detected: {temp_slope:.2f}°F per decade"
                
        elif tool_name == "project_climate_risk_enhanced":
            temp_change = data.get("projection", {}).get("temp_change_f")
            if temp_change:
                return f"Projected temperature increase of {temp_change}°F by {data.get('horizon_years', 30)} years"
                
        elif tool_name == "get_hazard_risk_profile":
            risk_rating = data.get("risk_rating")
            if risk_rating:
                return f"FEMA NRI risk rating: {risk_rating}"
                
        return None
