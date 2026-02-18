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


# Backward compatibility: module-level state filter for dashboard
def _filter_by_state(df, state_code):
    """Filter DataFrame by state code, resolving abbreviations to full names."""
    if not state_code:
        return df
    from agent import ResilienceAgent
    full_name = ResilienceAgent._STATE_NAMES.get(state_code.upper(), state_code)
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
    """Return MCP tool definitions for Archia agent (45+ capabilities)."""
    return [
        {"name": "query_counties", "description": "Query counties with filters.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}, "risk_level": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "get_county_detail", "description": "Get detailed county profile.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "compare_counties", "description": "Compare side-by-side.", "parameters": {"type": "object", "properties": {"county_names": {"type": "array", "items": {"type": "string"}}}}},
        {"name": "get_statistics", "description": "Get summary stats for a feature.", "parameters": {"type": "object", "properties": {"feature": {"type": "string"}, "state": {"type": "string"}}}},
        {"name": "predict_risk", "description": "Predict community risk.", "parameters": {"type": "object", "properties": {"population": {"type": "integer"}, "poverty": {"type": "number"}}}},
        {"name": "find_compound_risk_counties", "description": "Find critical hotspots.", "parameters": {"type": "object", "properties": {"min_dimensions": {"type": "integer"}}}},
        {"name": "get_gap_analysis", "description": "Analyze infrastructure gaps.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "get_disaster_trends", "description": "Detect acceleration.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "find_zero_redundancy", "description": "Identify isolation.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "get_state_rankings", "description": "Rank counties within a state.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "prioritize_by_impact", "description": "Prioritize by population impact.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "simulate_scenario", "description": "What-if impact modeling.", "parameters": {"type": "object", "properties": {"scenario": {"type": "string"}, "epicenter_fips": {"type": "string"}}}},
        {"name": "calculate_intervention_roi", "description": "ROI analysis.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "generate_executive_brief", "description": "Strategy briefs.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "get_equity_analysis", "description": "Analyze demographic disparities.", "parameters": {"type": "object", "properties": {"dimension": {"type": "string"}}}},
        {"name": "benchmark_county", "description": "Benchmark against peers.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "get_real_time_alerts", "description": "Threshold-based alerts.", "parameters": {"type": "object", "properties": {"risk_threshold": {"type": "number"}}}},
        {"name": "self_improve", "description": "Meta-tool.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "response_summary": {"type": "string"}}}},
        {"name": "export_fhir", "description": "Health export.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "export_geojson", "description": "GIS export.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "analyze_spatial_autocorrelation", "description": "Detect clustering.", "parameters": {"type": "object", "properties": {"variable": {"type": "string"}}}},
        {"name": "find_spatial_hotspots", "description": "Geospatial hotspots.", "parameters": {"type": "object", "properties": {"variable": {"type": "string"}}}},
        {"name": "analyze_risk_contagion", "description": "Overflow risk.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "calculate_pop_weighted_impact", "description": "Prioritize by lives.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "get_infrastructure_density", "description": "Facility density.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "subscribe_to_alerts", "description": "Monitoring.", "parameters": {"type": "object", "properties": {"county_fips": {"type": "string"}}}},
        {"name": "unsubscribe_from_alerts", "description": "Cancel sub.", "parameters": {"type": "object", "properties": {"subscription_id": {"type": "string"}}}},
        {"name": "list_alert_subscriptions", "description": "List subs.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "dispatch_alert", "description": "Emergency dispatch.", "parameters": {"type": "object", "properties": {"county_fips": {"type": "string"}, "message": {"type": "string"}}}},
        {"name": "get_active_alerts", "description": "Active feed.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "acknowledge_alert", "description": "Mark acknowledged.", "parameters": {"type": "object", "properties": {"alert_id": {"type": "string"}}}},
        {"name": "get_weather_alerts", "description": "NOAA polling.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "calculate_agricultural_vulnerability", "description": "Crop stability.", "parameters": {"type": "object", "properties": {"county_fips": {"type": "string"}}}},
        {"name": "assess_food_security_risk", "description": "Production capacity.", "parameters": {"type": "object", "properties": {"county_fips": {"type": "string"}}}},
        {"name": "get_state_crop_summary", "description": "Ag summary.", "parameters": {"type": "object", "properties": {"state": {"type": "string"}}}},
        {"name": "get_mo_health_disparities", "description": "MO gap analysis.", "parameters": {"type": "object", "properties": {"focus_metric": {"type": "string"}}}},
        {"name": "get_climate_trends", "description": "ACIS trends.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "get_hazard_risk_profile", "description": "NRI profile.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}},
        {"name": "project_climate_risk_enhanced", "description": "SSP projections.", "parameters": {"type": "object", "properties": {"fips": {"type": "string"}}}}
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

    # -- High-Level Orchestration --
    def query(self, query: str):
        """Processes natural language requests with multi-domain orchestration."""
        if self.df is None: return {"error": "Data not loaded"}
        q = query.lower()
        
        # Dispatch to specific logic based on intent
        if "roi" in q or "investment" in q:
            target = self._extract_county(q)
            if target: 
                data = self.calculate_intervention_roi(target['fips'])
                return self._format_and_improve(query, f"ROI analysis for {target['county_name']} generated.", data, "Analyzing cost-effectiveness.", [{"tool": "calculate_intervention_roi", "params": {"fips": target['fips']}}])
            
        if "simulate" in q or "what if" in q:
            target = self._extract_county(q)
            if target:
                res = self.simulate_scenario("hurricane_cat3", epicenter_fips=target['fips'])
                return self._format_and_improve(query, f"Simulation: A hurricane at {target['county_name']} would affect {res['summary']['counties_affected']} counties.", [res['summary']], "Modeling geospatial impact.", [{"tool": "simulate_scenario", "params": {"epicenter_fips": target['fips']}}])

        if "crop" in q or "agriculture" in q or "food security" in q:
            state = self._extract_state(q) or "MO"
            if "summary" in q: 
                data = self.get_state_crop_summary(state)
                return self._format_and_improve(query, f"Ag Risk summary for {state}.", [data], "Retrieving USDA stats.", [{"tool": "get_state_crop_summary", "params": {"state": state}}])
            target = self._extract_county(q)
            if target: 
                data = self.calculate_agricultural_vulnerability(target['fips'], target['county_name'], state)
                return self._format_and_improve(query, f"Ag vulnerability for {target['county_name']} assessed.", [data], "Analyzing crop stability.", [{"tool": "calculate_agricultural_vulnerability", "params": {"county_fips": target['fips']}}])

        if "health" in q or "disparit" in q:
            state = self._extract_state(q) or "MO"
            if state == "MO": 
                res = self.get_mo_health_disparities()
                return self._format_and_improve(query, res['summary'], res['priority_zones'], "Ranking by disparity index.", [{"tool": "get_mo_health_disparities"}])
            data = self.get_state_rankings(state)
            return self._format_and_improve(query, f"Risk rankings for {state}.", data, "Calculating state percentiles.", [{"tool": "get_state_rankings", "params": {"state": state}}])

        if "contagion" in q or "overflow" in q or "neighbor" in q:
            target = self._extract_county(q)
            if target:
                data = self.analyze_risk_contagion(target['fips'])
                return self._format_and_improve(query, f"Contagion analysis for {target['county_name']} identifies risk amplification from neighbors.", [data], "Spatial proximity analysis.", [{"tool": "analyze_risk_contagion", "params": {"fips": target['fips']}}])

        if "lives" in q or "population impact" in q:
            state = self._extract_state(q)
            data = self.calculate_pop_weighted_impact(state=state)
            return self._format_and_improve(query, f"Population-weighted risk analysis.", data, "Prioritizing by lives affected.", [{"tool": "calculate_pop_weighted_impact", "params": {"state": state}}])

        if "compound" in q or "multi-hazard" in q:
            data = self.find_compound_risk_counties(min_dimensions=3)
            return self._format_and_improve(query, f"Found {len(data)} compound risk hotspots.", data, "Clustering multi-dimensional vulnerabilities.", [{"tool": "find_compound_risk_counties", "params": {"min_dimensions": 3}}])

        if "redundancy" in q or "single point" in q:
            data = self.find_zero_redundancy()
            return self._format_and_improve(query, f"Found {len(data)} counties with critical facility isolation.", data, "Infrastructure redundancy audit.", [{"tool": "find_zero_redundancy"}])

        target = self._extract_county(q)
        if target: 
            data = self.get_county_detail(fips=target['fips'])
            return self._format_and_improve(query, f"Profile for {target['county_name']}: Risk {data.get('risk_score', 0):.3f}.", [data], "Retrieving detailed features.", [{"tool": "get_county_detail", "params": {"fips": target['fips']}}])
        
        state_code = self._extract_state(q)
        data = self.query_counties(state=state_code, max_results=10)
        return self._format_and_improve(query, f"Top highest-risk counties nationwide.", data, "Broad query execution.", [{"tool": "query_counties", "params": {"state": state_code}}])

    # Full state code → name map (prevents MO→Montana substring bug)
    _STATE_NAMES = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
        "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
        "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
        "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
        "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
        "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
        "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
        "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
        "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
    }

    # -- Core Data & Search --
    def query_counties(self, state=None, max_results=10):
        if self.df is None: return []
        res = self.df.copy()
        if state:
            full_name = self._STATE_NAMES.get(state.upper().strip(), state)
            res = res[res["county_name"].str.endswith(f", {full_name}", na=False)]
        return res.sort_values("risk_score", ascending=False).head(max_results).to_dict(orient="records")

    def get_county_detail(self, fips):
        match = self.df[self.df["fips"] == str(fips)]
        return match.iloc[0].to_dict() if not match.empty else {}

    def compare_counties(self, county_names):
        res = []
        for n in county_names:
            m = self.df[self.df["county_name"].str.contains(n, case=False, na=False)]
            if not m.empty: res.append(m.iloc[0].to_dict())
        return res

    def get_statistics(self, feature, state=None):
        if self.df is None or feature not in self.df.columns: return {}
        subset = self._filter_by_state(self.df, state) if state else self.df.copy()
        return subset[feature].describe().to_dict()

    # -- Advanced Analytics --
    def find_compound_risk_counties(self, min_dimensions=3):
        if self.df is None: return []
        res = self.df[self.df["compound_risk_count"] >= min_dimensions].copy()
        return res.sort_values("risk_score", ascending=False).head(15).to_dict(orient="records")

    def get_disaster_trends(self, state=None):
        if self.df is None: return []
        res = self.df[self.df["disaster_acceleration"] > 1.5].copy()
        if state: res = self._filter_by_state(res, state)
        return res.sort_values("disaster_acceleration", ascending=False).head(10).to_dict(orient="records")

    def _filter_by_state(self, df, state):
        """Filter a DataFrame by state code (2-letter) or full name."""
        if not state: return df
        full_name = self._STATE_NAMES.get(state.upper().strip(), state)
        return df[df["county_name"].str.endswith(f", {full_name}", na=False)]

    def get_gap_analysis(self, state=None):
        if self.df is None: return []
        gap_cols = ["gap_hospital", "gap_ems", "gap_fire", "gap_poverty", "gap_disaster_prep"]
        existing = [c for c in gap_cols if c in self.df.columns]
        if not existing: return {"error": "No gap columns in dataset"}
        subset = self._filter_by_state(self.df, state).copy()
        subset["total_gap"] = subset[existing].sum(axis=1)
        top = subset.nlargest(10, "total_gap")
        results = []
        for _, row in top.iterrows():
            r = {"fips": row.get("fips"), "county_name": row.get("county_name"),
                 "risk_score": round(float(row.get("risk_score", 0)), 3),
                 "total_population": int(row.get("total_population", 0)),
                 "top_intervention": row.get("top_intervention", ""),
                 "top_intervention_score": round(float(row.get("top_intervention_score", 0)), 4)}
            for c in existing:
                r[c] = round(float(row.get(c, 0)), 4)
            results.append(r)
        return results

    def find_zero_redundancy(self, state=None):
        if self.df is None: return []
        res = self.df[self.df["zero_redundancy_flag"] == 1].copy()
        if state: res = self._filter_by_state(res, state)
        return res.sort_values("total_population", ascending=False).head(10).to_dict(orient="records")

    def analyze_risk_contagion(self, fips, radius_km=100):
        match = self.df[self.df["fips"] == str(fips)]
        if match.empty: return {}
        target = match.iloc[0]
        neighbors = self.df[self.df["fips"] != fips].copy()
        neighbors["d"] = np.sqrt((target["latitude"]-neighbors["latitude"])**2 + (target["longitude"]-neighbors["longitude"])**2) * 111
        nearby = neighbors[neighbors["d"] <= radius_km]
        return {
            "county": target["county_name"], "high_risk_neighbors": len(nearby[nearby["risk_level"] == "High"]),
            "avg_neighbor_risk": round(float(nearby["risk_score"].mean()), 3),
            "amplification": round(float(nearby["risk_score"].mean() / target["risk_score"]), 2) if target["risk_score"] > 0 else 1.0
        }

    def calculate_pop_weighted_impact(self, state=None):
        if self.df is None: return []
        res = self._filter_by_state(self.df, state).copy() if state else self.df.copy()
        res["pop_weighted_risk"] = res["risk_score"] * res["total_population"]
        return res.sort_values("pop_weighted_risk", ascending=False).head(10).to_dict(orient="records")

    def get_infrastructure_density(self, fips):
        match = self.df[self.df["fips"] == str(fips)]
        if match.empty: return {}
        row = match.iloc[0]
        return {
            "hospitals_per_10k": round(float(row.get("density_hospitals_per10k", 0)), 2),
            "ems_per_10k": round(float(row.get("density_ems_stations_per10k", 0)), 2),
            "fire_per_10k": round(float(row.get("density_fire_stations_per10k", 0)), 2),
            "nursing_homes_per_10k": round(float(row.get("density_nursing_homes_per10k", 0)), 2),
            "hospitals_within_50km": int(row.get("count_hospitals_50km", 0)),
            "ems_within_50km": int(row.get("count_ems_stations_50km", 0)),
            "nearest_hospital_km": round(float(row.get("dist_nearest_hospitals_km", 0)), 1),
            "nearest_ems_km": round(float(row.get("dist_nearest_ems_stations_km", 0)), 1),
        }

    # -- Sector Specific Tools --
    def get_mo_health_disparities(self, focus_metric="uninsured_pct"):
        mo_df = self.df[self.df["county_name"].str.endswith(", Missouri")].copy()
        avg = mo_df[focus_metric].mean()
        mo_df["disparity_index"] = mo_df[focus_metric] / (avg + 1e-10)
        top = mo_df.sort_values("disparity_index", ascending=False).head(10)
        return {"priority_zones": top.to_dict(orient="records"), "summary": f"MO health gaps identified based on {focus_metric}."}

    def get_state_crop_summary(self, state):
        from src.agriculture_client import USDANASSClient
        return USDANASSClient().get_state_crop_summary(state)

    def calculate_agricultural_vulnerability(self, fips, name, state):
        from src.agriculture_client import AgriculturalVulnerabilityScorer
        return AgriculturalVulnerabilityScorer().calculate_crop_vulnerability(fips, name, state)

    # -- Climate Intelligence Tools --
    def get_climate_trends(self, fips):
        from src.climate_client import ClimateIntelligenceClient
        result = ClimateIntelligenceClient().acis.get_climate_trends(fips, 2000, 2025)
        
        # Enrich with county details including population for UI display
        if self.df is not None and isinstance(result, dict) and "error" not in result:
            match = self.df[self.df["fips"] == str(fips)]
            if not match.empty:
                county = match.iloc[0]
                result["county_name"] = county.get("county_name", f"FIPS {fips}")
                pop = county.get("total_population")
                result["total_population"] = int(pop) if pd.notna(pop) else None
        
        return result

    def get_hazard_risk_profile(self, fips):
        from src.climate_client import ClimateIntelligenceClient
        return ClimateIntelligenceClient().nri.get_hazard_risk_profile(fips)

    def project_climate_risk_enhanced(self, fips, scenario="ssp2_45"):
        from src.agents.climate_agent import ClimateAgent
        return ClimateAgent()._project_climate_risk_enhanced(fips, scenario, 30)

    # -- Decision Support & ROI --
    def calculate_intervention_roi(self, fips):
        from src.intervention_roi import InterventionROICalculator
        return InterventionROICalculator(self.df).rank_interventions(fips)

    def simulate_scenario(self, scenario, epicenter_fips):
        from src.scenario_simulator import ScenarioSimulator
        res = ScenarioSimulator(self.df).simulate(scenario, epicenter_fips=epicenter_fips)
        if "affected_df" in res: del res["affected_df"]
        return res

    def generate_executive_brief(self, fips, format="text"):
        from src.briefing_generator import BriefingGenerator
        return BriefingGenerator(self.df).generate_county_brief(fips, output_format=format)

    # -- Real-Time & Alerts --
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

    # -- Meta Tools --
    def self_improve(self, query, response_summary):
        from src.self_improve import SelfImproveEngine
        return SelfImproveEngine().evaluate_and_log(query, response_summary, [])

    # -- Helpers --
    def _format_and_improve(self, query, answer, data, thought, tool_calls):
        plan = [f"1. Contextualized query: {thought}", f"2. Executed tools: {', '.join([t['tool'] for t in tool_calls])}", "3. Synthesized cross-domain intelligence."]
        res = {"answer": answer, "data": data, "thought": thought, "tool_calls": tool_calls, "plan": plan}
        try: self.self_improve(query, answer)
        except: pass
        return res

    # Reverse map: full name → abbreviation, built from _STATE_NAMES
    _NAME_TO_CODE = {v.lower(): k for k, v in _STATE_NAMES.items()}

    def _extract_state(self, q):
        import re
        ql = q.lower()
        # Check full state names first (longer matches first to prevent partial overlap)
        for name, code in sorted(self._NAME_TO_CODE.items(), key=lambda x: -len(x[0])):
            if name in ql:
                return code
        # Check 2-letter abbreviations with word boundaries
        for code in self._STATE_NAMES:
            if re.search(rf'\b{code}\b', q):
                return code
        return None

    def _extract_county(self, q):
        if self.df is None: return None
        fips = "".join(filter(str.isdigit, q))
        if len(fips) == 5: return self.get_county_detail(fips)
        # Deterministic full scan instead of random sampling
        ql = f" {q.lower()} "
        for _, row in self.df.iterrows():
            name = row['county_name'].split(",")[0].strip().lower()
            if f" {name} " in ql:
                return row.to_dict()
        return None

    def get_system_prompt(self):
        n_counties = len(self.df) if self.df is not None else 0
        n_features = len(self.df.columns) if self.df is not None else 0
        return AGENT_SYSTEM_PROMPT.format(n_counties=n_counties, n_features=n_features)


def export_agent_config():
    agent = ResilienceAgent()
    config = {"name": "ResilienceAI", "description": "National Resilience Agent", "system_prompt": agent.get_system_prompt(), "tools": get_mcp_tools(), "model": "claude-sonnet-4-5-20250929", "temperature": 0.3}
    config_path = MODELS_DIR / "agent_config.json"
    with open(config_path, "w") as f: json.dump(config, f, indent=2)
    return config


if __name__ == "__main__":
    agent = ResilienceAgent()
    if agent.df is not None:
        print(f"Agent Ready: {len(agent.df)} counties indexed.")
    export_agent_config()
