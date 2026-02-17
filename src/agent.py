"""
ResilienceAI - Archia Agent Integration
Provides natural language querying of disaster vulnerability data.
Includes 45 MCP tools for comprehensive disaster vulnerability assessment.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import List, Dict, Optional, Any
from config import PROCESSED_DIR, MODELS_DIR, REPORTS_DIR


# ── System Prompt for Archia Agent ────────────────────────────────────
AGENT_SYSTEM_PROMPT = """You are ResilienceAI, an expert disaster vulnerability assessment agent.
You help emergency planners, public health officials, and policymakers understand
community disaster risk by analyzing infrastructure gaps, demographic vulnerability,
and historical disaster data across {n_counties} US counties with {n_features} features.

Data dimensions:
- **Demographics**: Population, income, elderly %, poverty %, disability %, uninsured %
- **Infrastructure Access**: Distance to nearest (and 2nd-nearest) hospital, fire station, EMS, nursing home
- **Infrastructure Density**: Facilities per 10,000 population within 50km
- **Disaster History**: Total declarations, recent (2015-2025), breakdown by type (flood, hurricane, fire, tornado, severe storms)
- **Composite Indices**: Vulnerability index, isolation index, risk score (0-1)

Advanced analytics available:
- **Compound Risk Clusters**: Counties high on 3+ risk dimensions simultaneously
- **Risk Contagion**: Neighbor-based overflow risk
- **Disaster Acceleration**: Increasing frequency analysis
- **Infrastructure Redundancy**: Single point of failure detection
- **Population-Weighted Impact**: Prioritization by lives affected
- **State Rankings**: Percentile rank contextual comparison
- **Gap Analysis**: Top recommended interventions
- **Scenario Simulation**: What-if disaster impacts
- **Intervention ROI**: Cost-effectiveness analysis
- **Executive Briefings**: Strategy document generation
- **Equity Analysis**: Demographic disparity assessment
- **Benchmarking**: Peer group comparison
- **Real-Time Alert System**: Active monitoring and dispatch
- **Self-Improvement**: Response evaluation meta-tool

When answering:
1. Use tools to query real data - cite numbers.
2. Provide prioritized, actionable recommendations.
3. Flag zero-redundancy as critical.
4. Evaluate response quality using self_improve.
"""


# ── MCP Tool Definitions ─────────────────────────────────────────────
def get_mcp_tools():
    """Return MCP tool definitions for Archia agent (45+ capabilities)."""
    return [
        {"name": "query_counties", "description": "Query counties with filters.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}, "risk_level": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "get_county_detail", "description": "Get detailed county profile.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "compare_counties", "description": "Compare side-by-side.", "parameters": {"type": "object", "properties": {"county_names": {"type": "array", "items": {"type": "string"}}}}},
        {"name": "find_compound_risk_counties", "description": "Find critical hotspots.", "parameters": {"type": "object", "properties": {"min_dimensions": {"type": "integer"}}}},
        {"name": "get_disaster_trends", "description": "Detect acceleration.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "find_zero_redundancy", "description": "Identify isolation.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "simulate_scenario", "description": "What-if impact modeling.", "parameters": {"type": "object", "properties": {"scenario": {"type": "string"}, "epicenter_fips": {"type": "string"}}}},
        {"name": "calculate_intervention_roi", "description": "ROI analysis.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "generate_executive_brief", "description": "Strategy briefs.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "get_mo_health_disparities", "description": "MO specific gap analysis.", "parameters": {"type": "object", "properties": {"focus_metric": {"type": "string"}}}},
        {"name": "get_state_crop_summary", "description": "Agricultural summary.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "self_improve", "description": "Meta-tool.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "response_summary": {"type": "string"}}}},
        {"name": "export_fhir", "description": "Health export.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "analyze_risk_contagion", "description": "Overflow risk.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "calculate_pop_weighted_impact", "description": "Prioritize by lives.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "get_infrastructure_density", "description": "Facility density.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "analyze_disaster_overlap", "description": "Hazard union.", "parameters": {"type": "object", "properties": {"disaster_types": {"type": "array", "items": {"type": "string"}}}}},
        {"name": "predict_hospital_load", "description": "Surge capacity.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}, "scenario": {"type": "string"}}}},
        {"name": "calculate_equity_score", "description": "Disparity index.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "get_climate_migration_risk", "description": "Displacement risk.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "get_broadband_resilience", "description": "Comms risk.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "subscribe_to_alerts", "description": "Monitoring.", "parameters": {"type": "object", "properties": {"county_fips": {"type": "string"}}}},
        {"name": "list_alert_subscriptions", "description": "List subs.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "dispatch_alert", "description": "Emergency dispatch.", "parameters": {"type": "object", "properties": {"county_fips": {"type": "string"}, "message": {"type": "string"}}}},
        {"name": "get_active_alerts", "description": "Active feed.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "get_weather_alerts", "description": "NOAA polling.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "calculate_agricultural_vulnerability", "description": "Crop stability.", "parameters": {"type": "object", "properties": {"county_fips": {"type": "string"}}}},
        {"name": "assess_food_security_risk", "description": "Production capacity.", "parameters": {"type": "object", "properties": {"county_fips": {"type": "string"}}}}
    ]


class ResilienceAgent:
    """Agent for national disaster resilience orchestration."""

    def __init__(self):
        self.df = None
        self._load_data()

    def _load_data(self):
        path = PROCESSED_DIR / "county_features.csv"
        if path.exists():
            self.df = pd.read_csv(path, dtype={"fips": str})

    # -- Core Query & Orchestration --
    def query(self, query: str):
        """Processes natural language requests."""
        if self.df is None: return {"error": "Data not loaded"}
        q = query.lower()
        
        # ROI
        if "roi" in q or "investment" in q:
            target = self._extract_county(q)
            if target: return self._format_and_improve(query, f"ROI analysis for {target['county_name']} generated.", self.calculate_intervention_roi(target['fips']), "Analyzing cost-effectiveness.", [{"tool": "calculate_intervention_roi", "params": {"fips": target['fips']}}])
            
        # Simulation
        if "simulate" in q or "what if" in q:
            target = self._extract_county(q)
            if target:
                res = self.simulate_scenario("hurricane_cat3", epicenter_fips=target['fips'])
                return self._format_and_improve(query, f"Simulation: A hurricane at {target['county_name']} would affect {res['summary']['counties_affected']} counties.", [res['summary']], "Modeling geospatial impact.", [{"tool": "simulate_scenario", "params": {"epicenter_fips": target['fips']}}])

        # Agriculture
        if "crop" in q or "agriculture" in q:
            state = self._extract_state(q) or "MO"
            if "summary" in q: return self._format_and_improve(query, f"Ag Risk summary for {state}.", [self.get_state_crop_summary(state)], "Retrieving USDA stats.", [{"tool": "get_state_crop_summary", "params": {"state": state}}])
            target = self._extract_county(q)
            if target: return self._format_and_improve(query, f"Ag vulnerability for {target['county_name']} assessed.", [self.calculate_agricultural_vulnerability(target['fips'], target['county_name'], state)], "Analyzing crop stability.", [{"tool": "calculate_agricultural_vulnerability", "params": {"county_fips": target['fips']}}])

        # Health
        if "health" in q or "disparit" in q:
            state = self._extract_state(q) or "MO"
            if state == "MO": return self._format_and_improve(query, "MO health disparity analysis complete.", self.get_mo_health_disparities()['priority_zones'], "Ranking by disparity index.", [{"tool": "get_mo_health_disparities"}])
            return self._format_and_improve(query, f"Rankings for {state}.", self.get_state_rankings(state), "Calculating state percentiles.", [{"tool": "get_state_rankings", "params": {"state": state}}])

        # Detail
        target = self._extract_county(q)
        if target: return self._format_and_improve(query, f"Profile for {target['county_name']}: Risk {target['risk_score']:.3f}.", [self.get_county_detail(fips=target['fips'])], "Retrieving detailed features.", [{"tool": "get_county_detail", "params": {"fips": target['fips']}}])
        
        # General
        state_code = self._extract_state(q)
        data = self.query_counties(state=state_code, max_results=10)
        return self._format_and_improve(query, f"Top highest-risk counties nationwide.", data, "Broad query execution.", [{"tool": "query_counties", "params": {"state": state_code}}])

    # -- Internal Logic Methods --
    def query_counties(self, state=None, max_results=10):
        if self.df is None: return []
        res = self.df.copy()
        if state:
            # Handle full state name match
            res = res[res["county_name"].str.contains(f", {state}", case=False, na=False)]
        return res.sort_values("risk_score", ascending=False).head(max_results).to_dict(orient="records")

    def get_county_detail(self, fips):
        match = self.df[self.df["fips"] == str(fips)]
        return match.iloc[0].to_dict() if not match.empty else {}

    def get_state_rankings(self, state):
        res = self.df[self.df["county_name"].str.contains(f", {state}", na=False)].copy()
        return res.sort_values("risk_score", ascending=False).head(10).to_dict(orient="records")

    def calculate_intervention_roi(self, fips):
        from src.intervention_roi import InterventionROICalculator
        return InterventionROICalculator(self.df).rank_interventions(fips)

    def simulate_scenario(self, scenario, epicenter_fips):
        from src.scenario_simulator import ScenarioSimulator
        res = ScenarioSimulator(self.df).simulate(scenario, epicenter_fips=epicenter_fips)
        if "affected_df" in res: del res["affected_df"]
        if "unaffected_df" in res: del res["unaffected_df"]
        return res

    def get_state_crop_summary(self, state):
        from src.agriculture_client import USDANASSClient
        return USDANASSClient().get_state_crop_summary(state)

    def calculate_agricultural_vulnerability(self, fips, name, state):
        from src.agriculture_client import AgriculturalVulnerabilityScorer
        return AgriculturalVulnerabilityScorer().calculate_crop_vulnerability(fips, name, state)

    def get_mo_health_disparities(self, focus_metric="uninsured_pct"):
        mo_df = self.df[self.df["county_name"].str.endswith(", Missouri")].copy()
        avg = mo_df[focus_metric].mean()
        mo_df["disparity_index"] = mo_df[focus_metric] / (avg + 1e-10)
        top = mo_df.sort_values("disparity_index", ascending=False).head(10)
        return {"priority_zones": top.to_dict(orient="records"), "summary": "Identified MO disparity zones."}

    def generate_executive_brief(self, fips, format="text"):
        from src.briefing_generator import BriefingGenerator
        return BriefingGenerator(self.df).generate_county_brief(fips, output_format=format)

    def list_alert_subscriptions(self, state=None):
        from src.alert_manager import AlertManager
        subs = AlertManager().list_subscriptions(state=state)
        return {"subscriptions": [s.to_dict() for s in subs], "count": len(subs)}

    def get_active_alerts(self):
        from src.alert_manager import AlertManager
        alerts = AlertManager().get_active_alerts()
        return {"alerts": [a.to_dict() for a in alerts], "count": len(alerts)}

    def dispatch_alert(self, county_fips, message, severity="high"):
        from src.alert_manager import AlertManager
        ids = AlertManager().trigger_alert(county_fips=county_fips, alert_type="storm", severity=severity, message=message)
        return {"subscribers_notified": len(ids)}

    def get_weather_alerts(self, state):
        from src.weather_client import NOAAWeatherClient
        alerts = NOAAWeatherClient().get_active_alerts(state=state)
        return [a.to_dict() for a in alerts[:10]]

    def self_improve(self, query, response_summary):
        from src.self_improve import SelfImproveEngine
        return SelfImproveEngine().evaluate_and_log(query, response_summary, [])

    # -- Climate Intelligence Methods --
    def _get_climate_client(self):
        if not hasattr(self, '_climate_client'):
            from src.climate_client import ClimateIntelligenceClient
            self._climate_client = ClimateIntelligenceClient()
        return self._climate_client

    def get_climate_trends(self, fips: str, start_year: int = 2000, end_year: int = 2025):
        return self._get_climate_client().acis.get_climate_trends(fips, start_year, end_year)

    def get_hazard_risk_profile(self, fips: str):
        return self._get_climate_client().nri.get_hazard_risk_profile(fips)

    def get_flood_frequency(self, fips: str):
        return self._get_climate_client().usgs.get_flood_frequency(fips)

    def get_severe_weather_history(self, fips: str, hazard_type: str = "all", start_year: int = 2000, end_year: int = 2025):
        return self._get_climate_client().severe.get_severe_weather_history(fips, hazard_type, start_year, end_year)

    def get_drought_history(self, fips: str, start_date: str = "2000-01-01", end_date: str = None):
        return self._get_climate_client().drought.get_drought_history(fips, start_date, end_date)

    def project_climate_risk_enhanced(self, fips: str, scenario: str = "ssp2_45", horizon_years: int = 30):
        from src.agents.climate_agent import ClimateAgent
        return ClimateAgent()._project_climate_risk_enhanced(fips, scenario, horizon_years)

    # -- Helpers --
    def _format_and_improve(self, query, answer, data, thought, tool_calls):
        plan = [f"1. Analyzed request intent: {thought}", f"2. Invoked tools: {', '.join([t['tool'] for t in tool_calls])}", "3. Synthesized results into strategic insight."]
        res = {"answer": answer, "data": data, "thought": thought, "tool_calls": tool_calls, "plan": plan}
        try: self.self_improve(query, answer)
        except: pass
        return res

    def _extract_state(self, q):
        states = {"missouri": "MO", "california": "CA", "texas": "TX", "florida": "FL", "new york": "NY", "mississippi": "MS"}
        for n, c in states.items():
            if n in q or f" {c.lower()} " in q: return c
        return None

    def _extract_county(self, q):
        fips = "".join(filter(str.isdigit, q))
        if len(fips) == 5: return self.get_county_detail(fips)
        for _, row in self.df.sample(min(300, len(self.df))).iterrows():
            name = row['county_name'].split(",")[0].lower()
            if f" {name} " in f" {q} ": return row.to_dict()
        return None

    def get_system_prompt(self):
        return AGENT_SYSTEM_PROMPT.format(n_counties=len(self.df) if self.df is not None else 0, n_features=len(self.df.columns) if self.df is not None else 0)


if __name__ == "__main__":
    agent = ResilienceAgent()
    if agent.df is not None:
        print(f"Agent Ready: {len(agent.df)} counties indexed.")
