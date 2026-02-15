"""
ResilienceAI - Archia Agent Integration
Provides natural language querying of disaster vulnerability data.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from config import PROCESSED_DIR, MODELS_DIR


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
- **Risk Contagion**: Neighbor-based overflow risk (if surrounding counties are also high-risk)
- **Disaster Acceleration**: Whether disaster frequency is increasing (2015-2025 vs 2005-2014)
- **Infrastructure Redundancy**: Distance to 2nd-nearest facility (zero redundancy = single point of failure)
- **Population-Weighted Impact**: Risk weighted by population for prioritizing by lives affected
- **State Rankings**: Percentile rank within own state for contextual comparison
- **Gap Analysis**: Which single intervention (add hospital, add EMS, reduce poverty, etc.) would most reduce each county's risk

When answering:
1. Use the tools to query real data - always cite specific numbers
2. Leverage advanced features for deeper insights (e.g., compound risk, gap analysis)
3. Provide actionable, prioritized recommendations
4. Compare counties using state percentiles for context
5. Flag zero-redundancy situations as critical
"""


# ── MCP Tool Definitions ─────────────────────────────────────────────
def get_mcp_tools():
    """Return MCP tool definitions for Archia agent."""
    return [
        {
            "name": "query_counties",
            "description": "Query county vulnerability data with filters. Returns matching counties with their risk scores and features.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "Two-letter state abbreviation to filter by (e.g., 'MO', 'CA')"
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": ["Low", "Medium", "High"],
                        "description": "Filter by risk level"
                    },
                    "min_risk_score": {
                        "type": "number",
                        "description": "Minimum risk score (0-1)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default 10)"
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Column to sort results by (default: risk_score)"
                    },
                    "ascending": {
                        "type": "boolean",
                        "description": "Sort ascending (default: false, highest risk first)"
                    }
                }
            }
        },
        {
            "name": "get_county_detail",
            "description": "Get detailed vulnerability profile for a specific county by name or FIPS code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "county_name": {
                        "type": "string",
                        "description": "County name (partial match supported)"
                    },
                    "fips": {
                        "type": "string",
                        "description": "5-digit FIPS code"
                    }
                }
            }
        },
        {
            "name": "compare_counties",
            "description": "Compare vulnerability profiles of two or more counties side by side.",
            "parameters": {
                "type": "object",
                "properties": {
                    "county_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of county names to compare"
                    }
                },
                "required": ["county_names"]
            }
        },
        {
            "name": "get_statistics",
            "description": "Get summary statistics for a feature across all counties or a filtered subset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "feature": {
                        "type": "string",
                        "description": "Feature column name (e.g., 'risk_score', 'poverty_pct')"
                    },
                    "state": {
                        "type": "string",
                        "description": "Optional state filter"
                    },
                    "risk_level": {
                        "type": "string",
                        "description": "Optional risk level filter"
                    }
                },
                "required": ["feature"]
            }
        },
        {
            "name": "predict_risk",
            "description": "Predict risk level for a hypothetical community with given characteristics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "total_population": {"type": "number"},
                    "median_income": {"type": "number"},
                    "elderly_pct": {"type": "number"},
                    "poverty_pct": {"type": "number"},
                    "dist_nearest_hospital_km": {"type": "number"},
                    "disaster_count": {"type": "number"}
                }
            }
        },
        {
            "name": "find_compound_risk_counties",
            "description": "Find counties that are simultaneously high-risk across 3+ dimensions (vulnerability, isolation, disaster exposure, infrastructure deficit). These are critical hotspots.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "Optional state filter"},
                    "min_dimensions": {"type": "integer", "description": "Minimum risk dimensions (default 3, max 4)"},
                    "max_results": {"type": "integer", "description": "Max results (default 20)"}
                }
            }
        },
        {
            "name": "get_gap_analysis",
            "description": "Get the top recommended intervention for counties. Shows which single action (add hospital, add EMS, reduce poverty, disaster preparedness) would most reduce risk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "Optional state filter"},
                    "intervention_type": {"type": "string", "description": "Filter by intervention type (e.g., 'add_hospital', 'add_ems', 'add_poverty')"},
                    "max_results": {"type": "integer", "description": "Max results (default 20)"}
                }
            }
        },
        {
            "name": "get_disaster_trends",
            "description": "Find counties where disasters are accelerating (increasing frequency). Compares 2015-2025 vs 2005-2014.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "Optional state filter"},
                    "min_acceleration": {"type": "number", "description": "Minimum acceleration ratio (default 2.0 = doubled)"},
                    "max_results": {"type": "integer", "description": "Max results (default 20)"}
                }
            }
        },
        {
            "name": "find_zero_redundancy",
            "description": "Find counties with zero infrastructure redundancy - where the 2nd nearest hospital is over 100km away. These are single-point-of-failure communities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "Optional state filter"},
                    "max_results": {"type": "integer", "description": "Max results (default 20)"}
                }
            }
        },
        {
            "name": "get_state_rankings",
            "description": "Get county rankings within a specific state. Shows worst/best counties by risk, vulnerability, or isolation percentile.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "State abbreviation (required)"},
                    "metric": {"type": "string", "description": "Metric to rank by: risk_score, vulnerability_index, isolation_index (default: risk_score)"},
                    "worst_first": {"type": "boolean", "description": "Show worst first (default true)"},
                    "max_results": {"type": "integer", "description": "Max results (default 10)"}
                },
                "required": ["state"]
            }
        },
        {
            "name": "prioritize_by_impact",
            "description": "Rank counties by population-weighted risk to prioritize interventions affecting the most lives.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "Optional state filter"},
                    "risk_level": {"type": "string", "description": "Optional risk level filter"},
                    "max_results": {"type": "integer", "description": "Max results (default 20)"}
                }
            }
        }
    ]


# ── Tool Execution ────────────────────────────────────────────────────
class ResilienceAgent:
    """Local agent for processing queries against the vulnerability database."""

    def __init__(self):
        self.df = None
        self.model = None
        self.scaler = None
        self.le = None
        self.feature_names = None
        self._load_data()

    def _load_data(self):
        """Load processed data and trained model."""
        features_path = PROCESSED_DIR / "county_features.csv"
        if features_path.exists():
            self.df = pd.read_csv(features_path, dtype={"fips": str})
            print(f"Loaded {len(self.df)} counties")

        model_path = MODELS_DIR / "best_model.pkl"
        if model_path.exists():
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(MODELS_DIR / "scaler.pkl")
            self.le = joblib.load(MODELS_DIR / "label_encoder.pkl")
            self.feature_names = joblib.load(MODELS_DIR / "feature_names.pkl")
            print("Loaded trained model")

    def query_counties(self, state=None, risk_level=None, min_risk_score=None,
                       max_results=10, sort_by="risk_score", ascending=False):
        """Query counties with filters."""
        if self.df is None:
            return {"error": "Data not loaded"}

        result = self.df.copy()

        if state:
            # Extract state from county_name (format: "County Name, State")
            result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]

        if risk_level:
            result = result[result["risk_level"] == risk_level]

        if min_risk_score is not None:
            result = result[result["risk_score"] >= min_risk_score]

        result = result.sort_values(sort_by, ascending=ascending).head(max_results)

        display_cols = ["fips", "county_name", "total_population", "risk_score",
                        "risk_level", "vulnerability_index", "isolation_index",
                        "disaster_count", "poverty_pct", "elderly_pct",
                        "compound_risk_count", "disaster_acceleration",
                        "top_intervention", "redundancy_score"]
        display_cols = [c for c in display_cols if c in result.columns]

        return result[display_cols].to_dict(orient="records")

    def get_county_detail(self, county_name=None, fips=None):
        """Get detailed profile for a county."""
        if self.df is None:
            return {"error": "Data not loaded"}

        if fips:
            match = self.df[self.df["fips"] == str(fips)]
        elif county_name:
            match = self.df[self.df["county_name"].str.contains(county_name, case=False, na=False)]
        else:
            return {"error": "Provide county_name or fips"}

        if match.empty:
            return {"error": f"No county found matching '{county_name or fips}'"}

        row = match.iloc[0]
        return row.to_dict()

    def compare_counties(self, county_names):
        """Compare multiple counties."""
        results = []
        for name in county_names:
            detail = self.get_county_detail(county_name=name)
            if "error" not in detail:
                results.append(detail)
        return results

    def get_statistics(self, feature, state=None, risk_level=None):
        """Get summary statistics for a feature."""
        if self.df is None:
            return {"error": "Data not loaded"}
        if feature not in self.df.columns:
            return {"error": f"Feature '{feature}' not found. Available: {list(self.df.columns)}"}

        subset = self.df.copy()
        if state:
            subset = subset[subset["county_name"].str.contains(f", {state}", case=False, na=False)]
        if risk_level:
            subset = subset[subset["risk_level"] == risk_level]

        stats = subset[feature].describe().to_dict()
        stats["feature"] = feature
        stats["n_counties"] = len(subset)
        return stats

    def find_compound_risk_counties(self, state=None, min_dimensions=3, max_results=20):
        """Find counties high on multiple risk dimensions simultaneously."""
        if self.df is None:
            return {"error": "Data not loaded"}
        result = self.df[self.df["compound_risk_count"] >= min_dimensions].copy()
        if state:
            result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]
        result = result.sort_values("compound_risk_count", ascending=False).head(max_results)
        cols = ["fips", "county_name", "compound_risk_count", "risk_score",
                "vulnerability_index", "isolation_index", "disaster_count", "total_population"]
        return result[[c for c in cols if c in result.columns]].to_dict(orient="records")

    def get_gap_analysis(self, state=None, intervention_type=None, max_results=20):
        """Get top recommended interventions per county."""
        if self.df is None:
            return {"error": "Data not loaded"}
        result = self.df.copy()
        if state:
            result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]
        if intervention_type:
            result = result[result["top_intervention"] == intervention_type]
        result = result.sort_values("top_intervention_score", ascending=False).head(max_results)
        cols = ["fips", "county_name", "top_intervention", "top_intervention_score",
                "risk_score", "gap_hospital", "gap_ems", "gap_fire", "gap_poverty", "gap_disaster_prep"]
        return result[[c for c in cols if c in result.columns]].to_dict(orient="records")

    def get_disaster_trends(self, state=None, min_acceleration=2.0, max_results=20):
        """Find counties with accelerating disaster frequency."""
        if self.df is None:
            return {"error": "Data not loaded"}
        result = self.df[self.df["disaster_acceleration"] >= min_acceleration].copy()
        if state:
            result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]
        result = result.sort_values("disaster_acceleration", ascending=False).head(max_results)
        cols = ["fips", "county_name", "disaster_acceleration", "disasters_2015_2025",
                "disasters_2005_2014", "disaster_count", "risk_score"]
        return result[[c for c in cols if c in result.columns]].to_dict(orient="records")

    def find_zero_redundancy(self, state=None, max_results=20):
        """Find counties with zero infrastructure redundancy."""
        if self.df is None:
            return {"error": "Data not loaded"}
        result = self.df[self.df["zero_redundancy_flag"] == 1].copy()
        if state:
            result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]
        result = result.sort_values("dist_2nd_nearest_hospitals_km", ascending=False).head(max_results)
        cols = ["fips", "county_name", "dist_nearest_hospitals_km", "dist_2nd_nearest_hospitals_km",
                "redundancy_score", "risk_score", "total_population"]
        return result[[c for c in cols if c in result.columns]].to_dict(orient="records")

    def get_state_rankings(self, state, metric="risk_score", worst_first=True, max_results=10):
        """Get county rankings within a state."""
        if self.df is None:
            return {"error": "Data not loaded"}
        result = self.df[self.df["county_name"].str.contains(f", {state}", case=False, na=False)].copy()
        if result.empty:
            return {"error": f"No counties found for state '{state}'"}
        pctile_col = f"{metric}_state_pctile"
        sort_col = pctile_col if pctile_col in result.columns else metric
        result = result.sort_values(sort_col, ascending=not worst_first).head(max_results)
        cols = ["fips", "county_name", metric, pctile_col, "total_population",
                "top_intervention", "compound_risk_count"]
        return result[[c for c in cols if c in result.columns]].to_dict(orient="records")

    def prioritize_by_impact(self, state=None, risk_level=None, max_results=20):
        """Rank counties by population-weighted risk."""
        if self.df is None:
            return {"error": "Data not loaded"}
        result = self.df.copy()
        if state:
            result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]
        if risk_level:
            result = result[result["risk_level"] == risk_level]
        result = result.sort_values("pop_weighted_risk", ascending=False).head(max_results)
        cols = ["fips", "county_name", "total_population", "risk_score", "pop_weighted_risk",
                "pop_weighted_risk_norm", "top_intervention", "compound_risk_flag"]
        return result[[c for c in cols if c in result.columns]].to_dict(orient="records")

    def get_system_prompt(self):
        """Get formatted system prompt with data stats."""
        n_counties = len(self.df) if self.df is not None else 0
        n_features = len(self.df.columns) if self.df is not None else 0
        return AGENT_SYSTEM_PROMPT.format(n_counties=n_counties, n_features=n_features)


def export_agent_config():
    """Export agent configuration for Archia platform."""
    agent = ResilienceAgent()

    config = {
        "name": "ResilienceAI",
        "description": "Disaster Vulnerability & Health Infrastructure Gap Assessment Agent",
        "system_prompt": agent.get_system_prompt(),
        "tools": get_mcp_tools(),
        "model": "claude-sonnet-4-5-20250929",
        "temperature": 0.3,
    }

    config_path = MODELS_DIR / "agent_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Agent config exported to {config_path}")

    return config


if __name__ == "__main__":
    # Quick test
    agent = ResilienceAgent()
    if agent.df is not None:
        print("\nTop 5 highest risk counties:")
        top = agent.query_counties(max_results=5)
        for c in top:
            print(f"  {c.get('county_name', 'N/A')}: risk={c.get('risk_score', 'N/A'):.3f} ({c.get('risk_level', 'N/A')})")
    else:
        print("Run the pipeline first to generate data.")
    export_agent_config()
