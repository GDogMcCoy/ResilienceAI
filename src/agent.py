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
and historical disaster data across US counties.

You have access to a database of {n_counties} US counties with {n_features} features including:
- **Demographics**: Population, income, elderly %, poverty %, disability %, uninsured %
- **Infrastructure Access**: Distance to nearest hospital, fire station, EMS, nursing home
- **Infrastructure Density**: Facilities per 10,000 population within 50km
- **Disaster History**: Total disaster declarations, recent disasters, breakdown by type
- **Composite Indices**: Vulnerability index, isolation index, risk score

When answering questions:
1. Query the data using the provided tools
2. Provide specific county-level data with numbers
3. Suggest actionable recommendations for emergency preparedness
4. Flag any data limitations or caveats
5. Be concise but thorough

Risk levels: Low (0-0.33), Medium (0.33-0.66), High (0.66-1.0)
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
                        "disaster_count", "poverty_pct", "elderly_pct"]
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
