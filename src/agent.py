"""
ResilienceAI - Archia Agent Integration
Provides natural language querying of disaster vulnerability data.
Includes 19 MCP tools for comprehensive disaster vulnerability assessment.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
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
- **Risk Contagion**: Neighbor-based overflow risk (if surrounding counties are also high-risk)
- **Disaster Acceleration**: Whether disaster frequency is increasing (2015-2025 vs 2005-2014)
- **Infrastructure Redundancy**: Distance to 2nd-nearest facility (zero redundancy = single point of failure)
- **Population-Weighted Impact**: Risk weighted by population for prioritizing by lives affected
- **State Rankings**: Percentile rank within own state for contextual comparison
- **Gap Analysis**: Which single intervention (add hospital, add EMS, reduce poverty, etc.) would most reduce each county's risk

Scenario simulation & network analysis:
- **Scenario Simulation**: What-if disaster scenarios (hurricane, earthquake, flood, wildfire, tornado) with before/after risk comparison
- **Cascade Analysis**: Model infrastructure as a network graph, identify single points of failure, simulate cascade failures
- **Intervention ROI**: Cost-effectiveness analysis for 6 intervention types with diminishing returns modeling
- **Executive Briefings**: Auto-generate PDF/PPTX/text briefings for counties or states
- **Equity Analysis**: Demographic disparity assessment across risk dimensions
- **Benchmarking**: Compare counties to demographic peers with radar chart data
- **Alert Thresholds**: Configurable risk thresholds with severity-based alerting
- **Real-Time Alert System**: Subscribe counties to vulnerability monitoring with multi-channel notifications (webhook, email, SMS)
- **Self-Improvement**: Meta-tool that evaluates response quality and proposes new capabilities

When answering:
1. Use the tools to query real data - always cite specific numbers
2. Leverage advanced features for deeper insights (e.g., compound risk, gap analysis)
3. Provide actionable, prioritized recommendations
4. Compare counties using state percentiles for context
5. Flag zero-redundancy situations as critical
6. Use scenario simulation to illustrate disaster impacts with concrete numbers
7. Recommend interventions with cost-effectiveness data
8. After each response, use self_improve to evaluate response quality
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
        },
        # ── New Tools (Phase 2) ───────────────────────────────────────
        {
            "name": "simulate_scenario",
            "description": "Simulate a disaster scenario (hurricane, earthquake, flood, wildfire, tornado) centered on a county. Returns before/after risk comparison, affected counties, population at risk, and infrastructure damage estimates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "enum": ["hurricane_cat1", "hurricane_cat3", "hurricane_cat5",
                                 "earthquake_m6", "earthquake_m7", "flood_major",
                                 "wildfire_large", "tornado_ef3", "tornado_ef5", "winter_storm"],
                        "description": "Disaster scenario preset"
                    },
                    "epicenter_fips": {
                        "type": "string",
                        "description": "FIPS code of epicenter county"
                    },
                    "custom_radius_km": {
                        "type": "number",
                        "description": "Override default scenario radius (km)"
                    }
                },
                "required": ["scenario", "epicenter_fips"]
            }
        },
        {
            "name": "analyze_cascade_risk",
            "description": "Model infrastructure as a network graph and analyze cascade failure risk. Returns network density, articulation points (single points of failure), betweenness centrality, and critical facility identification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fips": {
                        "type": "string",
                        "description": "County FIPS code to analyze"
                    },
                    "radius_km": {
                        "type": "number",
                        "description": "Radius for network analysis (default 80km)"
                    }
                },
                "required": ["fips"]
            }
        },
        {
            "name": "calculate_intervention_roi",
            "description": "Calculate cost-effectiveness of disaster preparedness interventions for a county. Returns ROI metrics including cost per person helped, risk reduction, and implementation timeline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fips": {
                        "type": "string",
                        "description": "County FIPS code"
                    },
                    "intervention": {
                        "type": "string",
                        "enum": ["add_hospital", "add_ems_station", "add_fire_station",
                                 "telehealth_infrastructure", "disaster_prep_program",
                                 "poverty_reduction"],
                        "description": "Intervention type (omit to rank all)"
                    }
                },
                "required": ["fips"]
            }
        },
        {
            "name": "generate_executive_brief",
            "description": "Generate an executive briefing document (PDF, PPTX, or text) for a county or state with risk overview, key findings, and recommendations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fips": {
                        "type": "string",
                        "description": "County FIPS code (for county brief)"
                    },
                    "state": {
                        "type": "string",
                        "description": "State abbreviation (for state brief)"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "pptx", "text"],
                        "description": "Output format (default: text)"
                    }
                }
            }
        },
        {
            "name": "get_equity_analysis",
            "description": "Analyze demographic disparities in disaster vulnerability. Compares risk across poverty levels, elderly populations, and infrastructure access to identify equity gaps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "Optional state filter"},
                    "dimension": {
                        "type": "string",
                        "enum": ["poverty", "elderly", "disability", "uninsured", "all"],
                        "description": "Equity dimension to analyze (default: all)"
                    },
                    "max_results": {"type": "integer", "description": "Max results (default 20)"}
                }
            }
        },
        {
            "name": "benchmark_county",
            "description": "Compare a county to demographically similar peers. Returns peer group statistics, percentile ranking, and radar chart data for multi-dimensional comparison.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fips": {
                        "type": "string",
                        "description": "County FIPS code to benchmark"
                    },
                    "peer_count": {
                        "type": "integer",
                        "description": "Number of peer counties (default 20)"
                    }
                },
                "required": ["fips"]
            }
        },
        {
            "name": "get_real_time_alerts",
            "description": "Check counties against configurable risk thresholds and generate alerts. Returns counties exceeding thresholds with severity levels (critical, warning, info).",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "Optional state filter"},
                    "risk_threshold": {
                        "type": "number",
                        "description": "Risk score threshold for alerts (default 0.7)"
                    },
                    "max_results": {"type": "integer", "description": "Max alerts (default 20)"}
                }
            }
        },
        {
            "name": "self_improve",
            "description": "Meta-tool: Agent evaluates its own response quality, identifies knowledge gaps, and proposes improvements to its own tools and features.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The original user query"},
                    "response_summary": {"type": "string", "description": "Summary of the response given"},
                    "confidence": {"type": "number", "description": "0-1 confidence in response quality"},
                    "identified_gaps": {"type": "string", "description": "What data or capabilities were missing"},
                    "proposed_improvement": {"type": "string", "description": "Specific tool/feature/data to add"}
                },
                "required": ["query", "response_summary"]
            }
        },
        # ── New Export & Analysis Tools (Agent Swarm) ───────────────────
        {
            "name": "export_fhir",
            "description": "Export county vulnerability data as FHIR R4 Bundle for health system integration. Returns FHIR Location, RiskAssessment, and Observation resources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fips": {
                        "type": "string",
                        "description": "County FIPS code to export (omit to export all)"
                    },
                    "state": {
                        "type": "string",
                        "description": "Two-letter state abbreviation to export all counties (omit for single county)"
                    },
                    "high_risk_only": {
                        "type": "boolean",
                        "description": "Export only high-risk counties (default: false)"
                    },
                    "risk_threshold": {
                        "type": "number",
                        "description": "Risk score threshold for high-risk filter (default: 0.7)"
                    }
                }
            }
        },
        {
            "name": "export_geojson",
            "description": "Export county vulnerability data as GeoJSON for GIS workflows. Includes point geometries and all vulnerability metrics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fips": {
                        "type": "string",
                        "description": "Single county FIPS code to export"
                    },
                    "state": {
                        "type": "string",
                        "description": "Two-letter state abbreviation to filter"
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": ["Low", "Medium", "High"],
                        "description": "Filter by risk level"
                    },
                    "high_risk_threshold": {
                        "type": "number",
                        "description": "Export counties with risk_score >= threshold"
                    },
                    "compound_risk_min": {
                        "type": "integer",
                        "description": "Export counties with N+ compound risk dimensions"
                    },
                    "minimal_properties": {
                        "type": "boolean",
                        "description": "Export only core properties (faster, smaller file)"
                    }
                }
            }
        },
        {
            "name": "analyze_spatial_autocorrelation",
            "description": "Calculate Moran's I statistic to detect spatial clustering of vulnerability. Values near 1 indicate clustering, near -1 indicate dispersion, near 0 indicate random distribution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variable": {
                        "type": "string",
                        "description": "Variable to analyze (e.g., 'risk_score', 'vulnerability_index', 'poverty_pct')",
                        "default": "risk_score"
                    },
                    "max_dist_km": {
                        "type": "number",
                        "description": "Neighborhood radius in km (default: 100)",
                        "default": 100
                    }
                }
            }
        },
        {
            "name": "find_spatial_hotspots",
            "description": "Use Getis-Ord Gi* analysis to identify statistically significant spatial clusters (hotspots and coldspots) of vulnerability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variable": {
                        "type": "string",
                        "description": "Variable to analyze for hotspots",
                        "default": "risk_score"
                    },
                    "max_dist_km": {
                        "type": "number",
                        "description": "Neighborhood radius in km (default: 100)",
                        "default": 100
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum hotspots to return (default: 20)",
                        "default": 20
                    }
                }
            }
        },
        # ── Real-Time Alert System Tools ─────────────────────────────────
        {
            "name": "subscribe_to_alerts",
            "description": "Subscribe to real-time vulnerability alerts for a specific county. Receive notifications when risk thresholds are exceeded.",
            "parameters": {
                "type": "object",
                "properties": {
                    "county_fips": {
                        "type": "string",
                        "description": "5-digit county FIPS code to monitor"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Risk score threshold (0-1) that triggers alerts (default: 0.7)"
                    },
                    "alert_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Alert types to monitor: flood, storm, drought, wildfire (default: all)"
                    },
                    "webhook_url": {
                        "type": "string",
                        "description": "Optional webhook URL for push notifications"
                    },
                    "email": {
                        "type": "string",
                        "description": "Optional email address for notifications"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Optional phone number for SMS notifications"
                    }
                },
                "required": ["county_fips"]
            }
        },
        {
            "name": "unsubscribe_from_alerts",
            "description": "Deactivate an alert subscription by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subscription_id": {
                        "type": "string",
                        "description": "Subscription ID to deactivate"
                    }
                },
                "required": ["subscription_id"]
            }
        },
        {
            "name": "list_alert_subscriptions",
            "description": "List all active alert subscriptions with optional filtering by county or state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "county_fips": {
                        "type": "string",
                        "description": "Optional: Filter by county FIPS code"
                    },
                    "state": {
                        "type": "string",
                        "description": "Optional: Filter by state abbreviation"
                    }
                }
            }
        },
        {
            "name": "dispatch_alert",
            "description": "Dispatch an alert to all subscribers in a county. Used for emergency notifications during active disasters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "county_fips": {
                        "type": "string",
                        "description": "Target county FIPS code"
                    },
                    "alert_type": {
                        "type": "string",
                        "enum": ["flood", "storm", "drought", "wildfire", "tornado", "hurricane"],
                        "description": "Type of disaster alert"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Alert severity level"
                    },
                    "message": {
                        "type": "string",
                        "description": "Alert message content"
                    },
                    "affected_population": {
                        "type": "integer",
                        "description": "Optional: Estimated population affected"
                    }
                },
                "required": ["county_fips", "alert_type", "severity", "message"]
            }
        },
        {
            "name": "get_active_alerts",
            "description": "Get all active (unacknowledged) alerts with optional filtering by county or alert type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "county_fips": {
                        "type": "string",
                        "description": "Optional: Filter by county FIPS code"
                    },
                    "alert_type": {
                        "type": "string",
                        "description": "Optional: Filter by alert type (flood, storm, etc.)"
                    }
                }
            }
        },
        {
            "name": "acknowledge_alert",
            "description": "Mark an alert as acknowledged by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "Alert event ID to acknowledge"
                    }
                },
                "required": ["alert_id"]
            }
        },
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

    # ── New Tool Implementations (Phase 2) ──────────────────────────
    def simulate_scenario(self, scenario, epicenter_fips, custom_radius_km=None):
        """Simulate a disaster scenario."""
        from src.scenario_simulator import ScenarioSimulator
        sim = ScenarioSimulator(self.df)
        result = sim.simulate(scenario, epicenter_fips=epicenter_fips,
                              custom_radius_km=custom_radius_km)
        if "affected_df" in result:
            del result["affected_df"]
        if "unaffected_df" in result:
            del result["unaffected_df"]
        return result

    def analyze_cascade_risk(self, fips, radius_km=80):
        """Analyze infrastructure network cascade risk."""
        from src.network_analysis import InfrastructureNetwork
        net = InfrastructureNetwork()
        return net.analyze_county(fips)

    def calculate_intervention_roi(self, fips, intervention=None):
        """Calculate intervention ROI for a county."""
        from src.intervention_roi import InterventionROICalculator
        calc = InterventionROICalculator(self.df)
        if intervention:
            return calc.calculate_roi(fips, intervention)
        else:
            return calc.rank_interventions(fips)

    def generate_executive_brief(self, fips=None, state=None, format="text"):
        """Generate executive briefing."""
        from src.briefing_generator import BriefingGenerator
        gen = BriefingGenerator(self.df)
        if fips:
            return gen.generate_county_brief(fips, output_format=format)
        elif state:
            return gen.generate_state_brief(state, output_format=format)
        return {"error": "Provide fips or state"}

    def get_equity_analysis(self, state=None, dimension="all", max_results=20):
        """Analyze demographic disparities in disaster vulnerability."""
        if self.df is None:
            return {"error": "Data not loaded"}

        result = self.df.copy()
        if state:
            result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]

        dimensions = {
            "poverty": ("poverty_pct", "Poverty Rate (%)"),
            "elderly": ("elderly_pct", "Elderly Population (%)"),
            "disability": ("disability_pct", "Disability Rate (%)"),
            "uninsured": ("uninsured_pct", "Uninsured Rate (%)"),
        }

        if dimension != "all":
            dimensions = {dimension: dimensions[dimension]} if dimension in dimensions else dimensions

        analysis = {}
        for dim_key, (col, label) in dimensions.items():
            if col not in result.columns:
                continue
            # Split into quartiles
            quartiles = pd.qcut(result[col], 4, labels=["Q1 (Low)", "Q2", "Q3", "Q4 (High)"],
                                duplicates="drop")
            quartile_risk = result.groupby(quartiles, observed=False)["risk_score"].agg(["mean", "median", "count"])
            disparity_ratio = quartile_risk["mean"].max() / (quartile_risk["mean"].min() + 1e-10)

            # Most disparate counties
            high_vuln = result[result[col] >= result[col].quantile(0.75)]
            top_disparate = high_vuln.nlargest(max_results, "risk_score")

            analysis[dim_key] = {
                "dimension": label,
                "disparity_ratio": round(float(disparity_ratio), 3),
                "quartile_risk_scores": quartile_risk["mean"].round(3).to_dict(),
                "highest_risk_counties": top_disparate[
                    ["county_name", col, "risk_score", "total_population"]
                ].head(max_results).to_dict(orient="records"),
            }

        return analysis

    def benchmark_county(self, fips, peer_count=20):
        """Benchmark county against demographic peers."""
        if self.df is None:
            return {"error": "Data not loaded"}

        match = self.df[self.df["fips"] == str(fips)]
        if match.empty:
            return {"error": f"County {fips} not found"}

        county = match.iloc[0]
        pop = county["total_population"]

        # Find peers by similar population (0.5x to 2x)
        peers = self.df[
            (self.df["total_population"] >= pop * 0.5) &
            (self.df["total_population"] <= pop * 2.0) &
            (self.df["fips"] != str(fips))
        ].head(peer_count)

        if len(peers) < 3:
            return {"error": "Too few peer counties found"}

        # Compare across dimensions
        compare_cols = ["risk_score", "vulnerability_index", "isolation_index",
                        "disaster_count", "poverty_pct", "elderly_pct", "redundancy_score"]
        compare_cols = [c for c in compare_cols if c in self.df.columns]

        radar_data = {}
        for col in compare_cols:
            peer_mean = peers[col].mean()
            peer_std = peers[col].std()
            county_val = county[col]
            z_score = (county_val - peer_mean) / (peer_std + 1e-10)
            percentile = (peers[col] < county_val).mean() * 100

            radar_data[col] = {
                "county_value": round(float(county_val), 4),
                "peer_mean": round(float(peer_mean), 4),
                "peer_std": round(float(peer_std), 4),
                "z_score": round(float(z_score), 3),
                "percentile": round(float(percentile), 1),
            }

        return {
            "county_fips": fips,
            "county_name": county.get("county_name", "Unknown"),
            "peer_count": len(peers),
            "radar_data": radar_data,
            "overall_peer_percentile": round(float(
                np.mean([v["percentile"] for v in radar_data.values()])
            ), 1),
        }

    def get_real_time_alerts(self, state=None, risk_threshold=0.7, max_results=20):
        """Generate threshold-based alerts for high-risk counties."""
        if self.df is None:
            return {"error": "Data not loaded"}

        result = self.df.copy()
        if state:
            result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]

        alerts = []

        # Critical alerts: risk > threshold AND compound risk
        critical = result[
            (result["risk_score"] >= risk_threshold) &
            (result.get("compound_risk_flag", pd.Series(0, index=result.index)) == 1)
        ]
        for _, row in critical.head(max_results).iterrows():
            alerts.append({
                "severity": "critical",
                "county_name": row.get("county_name", "Unknown"),
                "fips": row.get("fips", ""),
                "risk_score": round(float(row.get("risk_score", 0)), 3),
                "reason": f"Risk score {row.get('risk_score', 0):.3f} with {row.get('compound_risk_count', 0)} compound risk dimensions",
                "action": "Immediate review recommended",
            })

        # Warning alerts: risk > threshold OR zero redundancy
        warning = result[
            (result["risk_score"] >= risk_threshold) |
            (result.get("zero_redundancy_flag", pd.Series(0, index=result.index)) == 1)
        ]
        warning = warning[~warning["fips"].isin([a["fips"] for a in alerts])]
        for _, row in warning.head(max_results - len(alerts)).iterrows():
            reasons = []
            if row.get("risk_score", 0) >= risk_threshold:
                reasons.append(f"Risk score {row.get('risk_score', 0):.3f}")
            if row.get("zero_redundancy_flag", 0) == 1:
                reasons.append("Zero hospital redundancy")
            alerts.append({
                "severity": "warning",
                "county_name": row.get("county_name", "Unknown"),
                "fips": row.get("fips", ""),
                "risk_score": round(float(row.get("risk_score", 0)), 3),
                "reason": "; ".join(reasons),
                "action": "Enhanced monitoring recommended",
            })

        return {
            "total_alerts": len(alerts),
            "critical_count": sum(1 for a in alerts if a["severity"] == "critical"),
            "warning_count": sum(1 for a in alerts if a["severity"] == "warning"),
            "threshold": risk_threshold,
            "alerts": alerts[:max_results],
        }

    # ── New Export & Analysis Tools (Agent Swarm) ─────────────────────
    def export_fhir(self, fips=None, state=None, high_risk_only=False, risk_threshold=0.7):
        """Export vulnerability data as FHIR R4 Bundle."""
        from src.fhir_export import FHIRExporter
        exporter = FHIRExporter(self.df)

        if fips:
            result = exporter.export_county(fips, format="file")
        elif state:
            result = exporter.export_state(state, format="file")
        elif high_risk_only:
            result = exporter.export_high_risk(risk_threshold, format="file")
        else:
            return {"error": "Specify fips, state, or high_risk_only"}

        return result

    def export_geojson(self, fips=None, state=None, risk_level=None,
                       high_risk_threshold=None, compound_risk_min=None,
                       minimal_properties=False):
        """Export vulnerability data as GeoJSON."""
        from src.geojson_export import GeoJSONExporter
        exporter = GeoJSONExporter(self.df)

        include_props = not minimal_properties

        if fips:
            data = exporter.export_county(fips, include_props)
            filename = f"resilienceai-county-{fips}.geojson"
        elif state:
            data = exporter.export_state(state, include_props)
            filename = f"resilienceai-{state}.geojson"
        elif risk_level:
            data = exporter.export_by_risk_level(risk_level, include_props)
            filename = f"resilienceai-risk-{risk_level.lower()}.geojson"
        elif high_risk_threshold is not None:
            data = exporter.export_high_risk(high_risk_threshold, include_props)
            filename = f"resilienceai-high-risk-{high_risk_threshold}.geojson"
        elif compound_risk_min is not None:
            data = exporter.export_compound_risk(compound_risk_min, include_props)
            filename = f"resilienceai-compound-risk-{compound_risk_min}.geojson"
        else:
            data = exporter.export_all(include_props)
            filename = "resilienceai-all-counties.geojson"

        if "error" in data:
            return data

        output_path = exporter.export_to_file(data, filename)
        return {
            "output_path": output_path,
            "feature_count": len(data["features"]),
            "summary": exporter.get_summary()
        }

    def analyze_spatial_autocorrelation(self, variable="risk_score", max_dist_km=100):
        """Calculate Moran's I for spatial autocorrelation."""
        from src.spatial_stats import SpatialAnalyzer
        analyzer = SpatialAnalyzer(self.df)
        return analyzer.morans_i(variable, max_dist_km)

    def find_spatial_hotspots(self, variable="risk_score", max_dist_km=100, max_results=20):
        """Find spatial hotspots using Getis-Ord Gi*."""
        from src.spatial_stats import SpatialAnalyzer
        analyzer = SpatialAnalyzer(self.df)
        result = analyzer.getis_ord_gi(variable, max_dist_km)

        if isinstance(result, dict) and "error" in result:
            return result

        # Filter to significant hotspots and coldspots
        hotspots = result[result["is_hotspot"]].head(max_results)
        coldspots = result[result["is_coldspot"]].head(max_results)

        return {
            "variable": variable,
            "hotspots": hotspots.to_dict("records"),
            "coldspots": coldspots.to_dict("records"),
            "total_hotspots": len(result[result["is_hotspot"]]),
            "total_coldspots": len(result[result["is_coldspot"]]),
            "analysis_parameters": {
                "neighborhood_radius_km": max_dist_km,
                "max_results": max_results
            }
        }

    # ── Real-Time Alert System ─────────────────────────────────────────
    def subscribe_to_alerts(self, county_fips: str, threshold: float = 0.7,
                           alert_types: list = None, webhook_url: str = None,
                           email: str = None, phone: str = None):
        """
        Subscribe to real-time alerts for a county.
        
        Args:
            county_fips: 5-digit county FIPS code
            threshold: Risk threshold (0-1) that triggers alerts
            alert_types: List of alert types ['flood', 'storm', 'drought', 'wildfire']
            webhook_url: Optional webhook URL for notifications
            email: Optional email for notifications
            phone: Optional phone for SMS notifications
        """
        from src.alert_manager import AlertManager
        
        # Get county info from dataframe
        county_data = self.df[self.df['fips'] == county_fips]
        if county_data.empty:
            return {"error": f"County {county_fips} not found"}
        
        county_name = county_data.iloc[0]['county_name']
        state = county_data.iloc[0]['state']
        
        manager = AlertManager()
        subscription_id = manager.subscribe(
            county_fips=county_fips,
            county_name=county_name,
            state=state,
            threshold=threshold,
            alert_types=alert_types or ['flood', 'storm', 'drought', 'wildfire'],
            webhook_url=webhook_url,
            email=email,
            phone=phone
        )
        
        return {
            "subscription_id": subscription_id,
            "county": f"{county_name}, {state}",
            "threshold": threshold,
            "alert_types": alert_types or ['flood', 'storm', 'drought', 'wildfire'],
            "status": "active"
        }

    def unsubscribe_from_alerts(self, subscription_id: str):
        """Deactivate an alert subscription."""
        from src.alert_manager import AlertManager
        manager = AlertManager()
        success = manager.unsubscribe(subscription_id)
        return {
            "subscription_id": subscription_id,
            "success": success,
            "status": "unsubscribed" if success else "not_found"
        }

    def list_alert_subscriptions(self, county_fips: str = None, state: str = None):
        """List all active alert subscriptions."""
        from src.alert_manager import AlertManager
        manager = AlertManager()
        subs = manager.list_subscriptions(county_fips=county_fips, state=state)
        return {
            "subscriptions": [s.to_dict() for s in subs],
            "count": len(subs)
        }

    def dispatch_alert(self, county_fips: str, alert_type: str, severity: str,
                      message: str, affected_population: int = None):
        """
        Dispatch an alert to all subscribers in a county.
        
        Args:
            county_fips: Target county FIPS code
            alert_type: Type of alert (flood, storm, drought, wildfire)
            severity: Severity level (low, medium, high, critical)
            message: Alert message
            affected_population: Optional population count affected
        """
        from src.alert_manager import AlertManager
        manager = AlertManager()
        
        data = {
            "affected_population": affected_population,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        event_ids = manager.trigger_alert(
            county_fips=county_fips,
            alert_type=alert_type,
            severity=severity,
            message=message,
            data=data
        )
        
        # Get county info
        county_data = self.df[self.df['fips'] == county_fips]
        county_name = county_data.iloc[0]['county_name'] if not county_data.empty else "Unknown"
        
        return {
            "alert_dispatched": True,
            "county": county_name,
            "county_fips": county_fips,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "subscribers_notified": len(event_ids),
            "event_ids": event_ids
        }

    def get_active_alerts(self, county_fips: str = None, alert_type: str = None):
        """Get all active (unacknowledged) alerts."""
        from src.alert_manager import AlertManager
        manager = AlertManager()
        alerts = manager.get_active_alerts(county_fips=county_fips, alert_type=alert_type)
        return {
            "alerts": [a.to_dict() for a in alerts],
            "count": len(alerts),
            "filters": {
                "county_fips": county_fips,
                "alert_type": alert_type
            }
        }

    def acknowledge_alert(self, alert_id: str):
        """Mark an alert as acknowledged."""
        from src.alert_manager import AlertManager
        manager = AlertManager()
        success = manager.acknowledge_alert(alert_id)
        return {
            "alert_id": alert_id,
            "acknowledged": success,
            "timestamp": pd.Timestamp.now().isoformat()
        }

    def self_improve(self, query, response_summary, confidence=None,
                     identified_gaps=None, proposed_improvement=None):
        """Self-improvement meta-tool."""
        from src.self_improve import SelfImproveEngine
        engine = SelfImproveEngine()
        result = engine.evaluate_and_log(
            query=query,
            response_summary=response_summary,
            tools_used=[],  # Would be populated by the calling context
            data_available=self.df is not None,
        )
        if proposed_improvement:
            engine.logger.propose_feature(
                name=proposed_improvement,
                description=identified_gaps or "Agent-proposed improvement",
                rationale=f"Confidence: {confidence}, Query: {query[:100]}",
            )
        return result

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
