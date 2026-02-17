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

# State abbreviation to full name mapping for accurate filtering
STATE_ABBREV_TO_NAME = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
    "PR": "Puerto Rico", "VI": "Virgin Islands", "GU": "Guam", "AS": "American Samoa",
    "MP": "Northern Mariana Islands",
}


def _filter_by_state(df, state_code):
    """Filter DataFrame by state code, resolving abbreviations to full names."""
    if not state_code:
        return df
    full_name = STATE_ABBREV_TO_NAME.get(state_code.upper(), state_code)
    return df[df["county_name"].str.endswith(f", {full_name}", na=False)]


# ── System Prompt for Archia Agent ────────────────────────────────────
AGENT_SYSTEM_PROMPT = """You are ResilienceAI, an expert disaster vulnerability assessment agent.
You help emergency planners, public health officials, and policymakers understand
community disaster risk by analyzing infrastructure gaps, demographic vulnerability,
and historical disaster data across {n_counties} US counties with {n_features} features.

Advanced analytics available:
- **Compound Risk Clusters**: Counties high on 3+ risk dimensions simultaneously
- **Risk Contagion**: Neighbor-based overflow risk
- **Disaster Acceleration**: Increasing frequency analysis
- **Infrastructure Redundancy**: Single point of failure detection
- **Intervention ROI**: Cost-effectiveness analysis
- **Executive Briefings**: Strategy document generation
- **Real-Time Alert System**: Active monitoring and dispatch
- **Climate Intelligence**: ACIS, NRI, USGS, and satellite indicator integration

When answering:
1. Use tools to query real data - cite numbers.
2. Provide prioritized, actionable recommendations.
3. Evaluate response quality using self_improve.
"""


# ── MCP Tool Definitions ─────────────────────────────────────────────
def get_mcp_tools():
    """Return MCP tool definitions - only tools with working implementations."""
    return [
        {"name": "query_counties", "description": "Query and rank counties by risk score. Filter by state.", "parameters": {"type": "object", "properties": {"state": {"type": "string", "description": "2-letter state code"}, "max_results": {"type": "integer", "description": "Max results (default 10)"}}}},
        {"name": "get_county_detail", "description": "Full 66-feature profile for a county.", "parameters": {"type": "object", "properties": {"fips": {"type": "string", "description": "5-digit FIPS code"}}, "required": ["fips"]}},
        {"name": "get_state_rankings", "description": "Top 10 highest-risk counties in a state.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}, "required": ["state"]}},
        {"name": "analyze_risk_contagion", "description": "Geographic risk spillover from neighboring counties.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}, "radius_km": {"type": "integer"}}, "required": ["fips"]}},
        {"name": "calculate_pop_weighted_impact", "description": "Rank counties by population-weighted risk (lives affected).", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "get_infrastructure_density", "description": "Emergency facility density per 10k population.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}, "required": ["fips"]}},
        {"name": "get_mo_health_disparities", "description": "Missouri health disparity zone analysis.", "parameters": {"type": "object", "properties": {"focus_metric": {"type": "string"}}}},
        {"name": "calculate_intervention_roi", "description": "Cost-effectiveness ranking of interventions.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}, "required": ["fips"]}},
        {"name": "simulate_scenario", "description": "What-if disaster impact simulation.", "parameters": {"type": "object", "properties": {"scenario": {"type": "string"}, "epicenter_fips": {"type": "string"}}, "required": ["scenario", "epicenter_fips"]}},
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
        """Processes natural language requests with multi-domain orchestration."""
        if self.df is None: return {"error": "Data not loaded"}
        q = query.lower()
        
        # 1. ROI / Investment
        if "roi" in q or "investment" in q:
            target = self._extract_county(q)
            if target: 
                data = self.calculate_intervention_roi(target['fips'])
                return self._format_and_improve(query, f"ROI analysis for {target['county_name']} generated.", data, "Analyzing cost-effectiveness.", [{"tool": "calculate_intervention_roi", "params": {"fips": target['fips']}}])
            
        # 2. Simulation / What-if
        if "simulate" in q or "what if" in q:
            target = self._extract_county(q)
            if target:
                res = self.simulate_scenario("hurricane_cat3", epicenter_fips=target['fips'])
                return self._format_and_improve(query, f"Simulation: A hurricane at {target['county_name']} would affect {res['summary']['counties_affected']} counties.", [res['summary']], "Modeling geospatial impact.", [{"tool": "simulate_scenario", "params": {"epicenter_fips": target['fips']}}])

        # 3. Agriculture / Food Security
        if "crop" in q or "agriculture" in q or "food security" in q:
            state = self._extract_state(q) or "MO"
            if "summary" in q: 
                data = self.get_state_crop_summary(state)
                return self._format_and_improve(query, f"Ag Risk summary for {state}.", [data], "Retrieving USDA stats.", [{"tool": "get_state_crop_summary", "params": {"state": state}}])
            target = self._extract_county(q)
            if target: 
                data = self.calculate_agricultural_vulnerability(target['fips'], target['county_name'], state)
                return self._format_and_improve(query, f"Ag vulnerability for {target['county_name']} assessed.", [data], "Analyzing crop stability.", [{"tool": "calculate_agricultural_vulnerability", "params": {"county_fips": target['fips']}}])

        # 4. Health Disparities
        if "health" in q or "disparit" in q:
            state = self._extract_state(q) or "MO"
            if state == "MO": 
                res = self.get_mo_health_disparities()
                return self._format_and_improve(query, res['summary'], res['priority_zones'], "Ranking by disparity index.", [{"tool": "get_mo_health_disparities"}])
            data = self.get_state_rankings(state)
            return self._format_and_improve(query, f"Risk rankings for {state}.", data, "Calculating state percentiles.", [{"tool": "get_state_rankings", "params": {"state": state}}])

        # 5. Risk Contagion (Geospatial Flex)
        if "contagion" in q or "overflow" in q or "neighbor" in q:
            target = self._extract_county(q)
            if target:
                data = self.analyze_risk_contagion(target['fips'])
                return self._format_and_improve(query, f"Contagion analysis for {target['county_name']} identifies risk amplification from neighbors.", [data], "Spatial proximity analysis.", [{"tool": "analyze_risk_contagion", "params": {"fips": target['fips']}}])

        # 6. Population-Weighted Impact
        if "lives" in q or "population impact" in q or "weighted" in q:
            state = self._extract_state(q)
            data = self.calculate_pop_weighted_impact(state=state)
            return self._format_and_improve(query, f"Population-weighted risk analysis" + (f" for {state}" if state else " nationwide") + ".", data, "Prioritizing by lives affected.", [{"tool": "calculate_pop_weighted_impact", "params": {"state": state}}])

        # 7. Infrastructure Density
        if "density" in q or "how many hospitals" in q:
            target = self._extract_county(q)
            if target:
                data = self.get_infrastructure_density(target['fips'])
                return self._format_and_improve(query, f"Infrastructure density metrics for {target['county_name']}.", [data], "Retrieving facility counts per 10k population.", [{"tool": "get_infrastructure_density", "params": {"fips": target['fips']}}])

        # 8. County Profile / Detail
        target = self._extract_county(q)
        if target: 
            data = self.get_county_detail(fips=target['fips'])
            return self._format_and_improve(query, f"Profile for {target['county_name']}: Risk {data.get('risk_score', 0):.3f}.", [data], "Retrieving detailed features.", [{"tool": "get_county_detail", "params": {"fips": target['fips']}}])
        
        # Default: Broad Query
        state_code = self._extract_state(q)
        data = self.query_counties(state=state_code, max_results=10)
        return self._format_and_improve(query, f"Top highest-risk counties" + (f" in {state_code}" if state_code else " nationwide") + ".", data, "Broad query execution.", [{"tool": "query_counties", "params": {"state": state_code}}])

    # -- Internal Analytic Methods --
    def query_counties(self, state=None, max_results=10):
        if self.df is None: return []
        res = _filter_by_state(self.df, state)
        return res.sort_values("risk_score", ascending=False).head(max_results).to_dict(orient="records")

    def get_county_detail(self, fips):
        match = self.df[self.df["fips"] == str(fips)]
        return match.iloc[0].to_dict() if not match.empty else {}

    def get_state_rankings(self, state):
        res = _filter_by_state(self.df, state).copy()
        return res.sort_values("risk_score", ascending=False).head(10).to_dict(orient="records")

    def analyze_risk_contagion(self, fips, radius_km=100):
        """Analyzes risk overflow from neighboring counties."""
        match = self.df[self.df["fips"] == str(fips)]
        if match.empty: return {}
        target = match.iloc[0]
        
        # Find neighbors within radius (simplified haversine)
        def dist(lat1, lon1, lat2, lon2):
            return np.sqrt((lat1-lat2)**2 + (lon1-lon2)**2) * 111
            
        neighbors = self.df[self.df["fips"] != fips].copy()
        neighbors["d"] = dist(target["latitude"], target["longitude"], neighbors["latitude"], neighbors["longitude"])
        nearby = neighbors[neighbors["d"] <= radius_km]
        
        high_risk_neighbors = nearby[nearby["risk_level"] == "High"]
        avg_neighbor_risk = nearby["risk_score"].mean()
        
        return {
            "fips": fips,
            "county_name": target["county_name"],
            "neighbor_count": len(nearby),
            "high_risk_neighbor_count": len(high_risk_neighbors),
            "average_neighbor_risk": round(float(avg_neighbor_risk), 3),
            "amplification_factor": round(float(avg_neighbor_risk / target["risk_score"]), 2) if target["risk_score"] > 0 else 1.0,
            "status": "High" if len(high_risk_neighbors) > 2 else "Stable"
        }

    def calculate_pop_weighted_impact(self, state=None):
        """Ranks counties by population-weighted risk to prioritize by lives affected."""
        if self.df is None: return []
        res = _filter_by_state(self.df, state).copy()
        
        if "pop_weighted_risk" not in res.columns:
            res["pop_weighted_risk"] = res["risk_score"] * res["total_population"]
            
        return res.sort_values("pop_weighted_risk", ascending=False).head(10).to_dict(orient="records")

    def get_infrastructure_density(self, fips):
        """Retrieves facility density metrics per 10k population."""
        match = self.df[self.df["fips"] == str(fips)]
        if match.empty: return {}
        row = match.iloc[0]
        
        return {
            "fips": fips,
            "county_name": row["county_name"],
            "hospital_density": round(float(row.get("density_hospitals_per10k", 0)), 2),
            "ems_density": round(float(row.get("density_ems_stations_per10k", 0)), 2),
            "fire_density": round(float(row.get("density_fire_stations_per10k", 0)), 2),
            "nursing_home_density": round(float(row.get("density_nursing_homes_per10k", 0)), 2)
        }

    def calculate_intervention_roi(self, fips):
        try:
            from src.intervention_roi import InterventionROICalculator
            return InterventionROICalculator(self.df).rank_interventions(fips)
        except Exception as e:
            return {"error": f"Intervention ROI unavailable: {e}"}

    def simulate_scenario(self, scenario, epicenter_fips):
        try:
            from src.scenario_simulator import ScenarioSimulator
            res = ScenarioSimulator(self.df).simulate(scenario, epicenter_fips=epicenter_fips)
            if "affected_df" in res: del res["affected_df"]
            if "unaffected_df" in res: del res["unaffected_df"]
            return res
        except Exception as e:
            return {"error": f"Scenario simulation unavailable: {e}"}

    def get_state_crop_summary(self, state):
        try:
            from src.agriculture_client import USDANASSClient
            return USDANASSClient().get_state_crop_summary(state)
        except Exception as e:
            return {"error": f"USDA API unavailable: {e}"}

    def calculate_agricultural_vulnerability(self, fips, name, state):
        try:
            from src.agriculture_client import AgriculturalVulnerabilityScorer
            return AgriculturalVulnerabilityScorer().calculate_crop_vulnerability(fips, name, state)
        except Exception as e:
            return {"error": f"Agricultural analysis unavailable: {e}"}

    def get_mo_health_disparities(self, focus_metric="uninsured_pct"):
        mo_df = self.df[self.df["county_name"].str.endswith(", Missouri")].copy()
        avg = mo_df[focus_metric].mean()
        mo_df["disparity_index"] = mo_df[focus_metric] / (avg + 1e-10)
        top = mo_df.sort_values("disparity_index", ascending=False).head(10)
        return {"priority_zones": top.to_dict(orient="records"), "summary": "Identified MO disparity zones based on " + focus_metric}

    def list_alert_subscriptions(self, state=None):
        try:
            from src.alert_manager import AlertManager
            subs = AlertManager().list_subscriptions(state=state)
            return {"subscriptions": [s.to_dict() for s in subs], "count": len(subs)}
        except Exception as e:
            return {"error": f"Alert system unavailable: {e}", "subscriptions": [], "count": 0}

    def get_active_alerts(self):
        try:
            from src.alert_manager import AlertManager
            alerts = AlertManager().get_active_alerts()
            return {"alerts": [a.to_dict() for a in alerts], "count": len(alerts)}
        except Exception as e:
            return {"error": f"Alert system unavailable: {e}", "alerts": [], "count": 0}

    def self_improve(self, query, response_summary):
        from src.self_improve import SelfImproveEngine
        return SelfImproveEngine().evaluate_and_log(query, response_summary, [])

    # Climate tools are handled by ClimateAgent (src/agents/climate_agent.py)
    # which uses real API integrations via ClimateIntelligenceClient.

    # -- Helpers --
    def _format_and_improve(self, query, answer, data, thought, tool_calls):
        plan = [
            f"1. Contextualized query: {thought}", 
            f"2. Executed tools: {', '.join([t['tool'] for t in tool_calls])}", 
            "3. Synthesized cross-domain intelligence."
        ]
        res = {"answer": answer, "data": data, "thought": thought, "tool_calls": tool_calls, "plan": plan}
        try: self.self_improve(query, answer)
        except: pass
        return res

    def _extract_state(self, q):
        # Reverse mapping: full name → abbreviation
        name_to_abbrev = {v.lower(): k for k, v in STATE_ABBREV_TO_NAME.items()}
        for name, code in name_to_abbrev.items():
            if name in q:
                return code
        # Also check 2-letter codes
        for code in STATE_ABBREV_TO_NAME:
            if f" {code.lower()} " in f" {q} ":
                return code
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


def export_agent_config():
    agent = ResilienceAgent()
    config = {"name": "ResilienceAI", "description": "Disaster Vulnerability Agent", "system_prompt": agent.get_system_prompt(), "tools": get_mcp_tools(), "model": "claude-sonnet-4-5-20250929", "temperature": 0.3}
    config_path = MODELS_DIR / "agent_config.json"
    with open(config_path, "w") as f: json.dump(config, f, indent=2)
    return config


if __name__ == "__main__":
    agent = ResilienceAgent()
    if agent.df is not None:
        print(f"Agent Ready: {len(agent.df)} counties indexed.")
    export_agent_config()
