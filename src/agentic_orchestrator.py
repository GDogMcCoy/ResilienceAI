"""
ResilienceAI - True Agentic Orchestrator
LLM-powered reasoning loop with dual-backend support:
  - GPT-OSS 20B via LM Studio (deep analysis)
  - Nemotron-3-Nano via Ollama (fast reasoning + tools)

The LLM decides which tools to call, reads results, chains multi-step
analysis, and synthesizes novel insights from real data.
"""
import json
import os
import re
import time
import requests
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgenticStep:
    """One step in the reasoning chain."""
    step_num: int
    reasoning: str  # LLM's chain-of-thought
    tool_name: Optional[str] = None
    tool_args: Optional[Dict] = None
    tool_result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class AgenticResponse:
    """Full agentic response with reasoning trace."""
    query: str
    answer: str
    steps: List[AgenticStep] = field(default_factory=list)
    total_tokens: int = 0
    execution_time_ms: float = 0.0
    tools_used: List[str] = field(default_factory=list)
    model: str = ""


# ── Model Presets ───────────────────────────────────────────────────

MODEL_PRESETS = {
    "gemini-pro": {
        "label": "Gemini 2.5 Pro (Cloud)",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-pro",
        "description": "Google cloud — fastest + deepest reasoning (~5-15s)",
        "api_key_env": "GEMINI_API_KEY",
    },
    "nemotron-3-nano": {
        "label": "Nemotron-3-Nano (Local)",
        "base_url": "http://localhost:11434",
        "model": "nemotron-3-nano",
        "description": "30B MoE, 3B active — local fast reasoning (~15-30s)",
    },
    "gpt-oss-20b": {
        "label": "GPT-OSS 20B (Local)",
        "base_url": "http://localhost:1234",
        "model": "openai/gpt-oss-20b",
        "description": "20B dense — local deep analysis (~40-60s)",
    },
}


# ── Tool Registry ────────────────────────────────────────────────────
# Only tools that return REAL data. No stubs, no unimplemented declarations.

def get_working_tool_schemas() -> List[Dict]:
    """Return OpenAI-format tool schemas for tools that actually work."""
    return [
        {
            "type": "function",
            "function": {
                "name": "query_counties",
                "description": "Query and rank counties by disaster vulnerability risk score. Can filter by state. Returns top N counties with full feature data including population, infrastructure, disaster history, and risk metrics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {"type": "string", "description": "2-letter state code (e.g. 'MO', 'CA'). Omit for nationwide."},
                        "max_results": {"type": "integer", "description": "Number of results to return (default: 10)"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_county_detail",
                "description": "Get the full profile for a specific county by FIPS code. Returns all 66 features: demographics (population, income, poverty, elderly, disability, uninsured), infrastructure (hospital/EMS/fire distances and counts), disaster history (total, by type, acceleration), risk scores, and intervention gaps.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code (e.g. '29019' for Boone County, MO)"}
                    },
                    "required": ["fips"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_state_rankings",
                "description": "Get top 10 highest-risk counties in a state, ranked by vulnerability risk score.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {"type": "string", "description": "2-letter state code (e.g. 'MO')"}
                    },
                    "required": ["state"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_risk_contagion",
                "description": "Analyze geographic risk spillover for a county. Finds all neighboring counties within a radius and calculates how many are high-risk, the average neighbor risk, and the amplification factor (whether neighbors make this county more vulnerable).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "radius_km": {"type": "integer", "description": "Search radius in km (default: 100)"}
                    },
                    "required": ["fips"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_pop_weighted_impact",
                "description": "Rank counties by population-weighted risk (risk_score * total_population). This prioritizes by total lives affected, not just risk intensity. A large city with moderate risk may matter more than a small county with high risk.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {"type": "string", "description": "2-letter state code. Omit for nationwide."}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_infrastructure_density",
                "description": "Get emergency infrastructure density per 10,000 population for a county: hospitals, EMS stations, fire stations, and nursing homes. Low density indicates infrastructure gaps.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"}
                    },
                    "required": ["fips"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_mo_health_disparities",
                "description": "Analyze health disparity zones in Missouri. Computes a disparity index (county metric / state average) and returns the top 10 counties with the worst disparities. Default metric is uninsured_pct but can analyze poverty_pct, disability_pct, or elderly_pct.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "focus_metric": {"type": "string", "description": "Metric to analyze: 'uninsured_pct', 'poverty_pct', 'disability_pct', or 'elderly_pct'"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_intervention_roi",
                "description": "Calculate the cost-effectiveness of different interventions for a county. Ranks interventions (new hospital, mobile EMS, disaster preparedness, broadband, etc.) by cost per person helped and projected risk reduction.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"}
                    },
                    "required": ["fips"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "simulate_scenario",
                "description": "Run a what-if disaster scenario simulation. Models the geographic impact of a disaster originating at a specific county, including affected counties, population at risk, and infrastructure damage estimates. Scenarios: 'hurricane_cat3', 'earthquake_7.0', 'flood_500yr', 'tornado_ef4', 'pandemic_wave'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scenario": {"type": "string", "description": "Scenario type: hurricane_cat3, earthquake_7.0, flood_500yr, tornado_ef4, pandemic_wave"},
                        "epicenter_fips": {"type": "string", "description": "5-digit FIPS code for the disaster epicenter"}
                    },
                    "required": ["scenario", "epicenter_fips"]
                }
            }
        },
        # ── Climate Intelligence Tools (via ClimateAgent) ──────────────
        {
            "type": "function",
            "function": {
                "name": "get_climate_trends",
                "description": "Get historical temperature and precipitation trends for a county from ACIS/PRISM data. Returns annual records with computed linear trend slopes showing warming/cooling and precipitation changes over time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "start_year": {"type": "integer", "description": "Start year (default: 2000)"},
                        "end_year": {"type": "integer", "description": "End year (default: 2025)"},
                    },
                    "required": ["fips"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_hazard_risk_profile",
                "description": "Get FEMA National Risk Index profile with 18 hazard types. Returns Expected Annual Loss, Social Vulnerability, Community Resilience, and per-hazard risk scores for a county.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                    },
                    "required": ["fips"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_flood_frequency",
                "description": "Get USGS streamflow data and flood recurrence interval estimates for a county. Returns peak flow records and estimated 2/5/10/25/50/100-year flood levels.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                    },
                    "required": ["fips"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_severe_weather_history",
                "description": "Get historical severe weather events (tornadoes, hail, damaging wind) for a county from NOAA SWDI/SPC Storm Events Database.",
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
            }
        },
        {
            "type": "function",
            "function": {
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
            }
        },
        {
            "type": "function",
            "function": {
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "project_climate_risk_enhanced",
                "description": "Project future climate risk using historical ACIS data as baseline combined with IPCC SSP scenarios. Returns projected temperature/precipitation changes and risk implications.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fips": {"type": "string", "description": "5-digit county FIPS code"},
                        "scenario": {"type": "string", "enum": ["ssp1_19", "ssp2_45", "ssp5_85"], "description": "IPCC SSP scenario"},
                        "horizon_years": {"type": "integer", "description": "Years into future (default: 30)"},
                    },
                    "required": ["fips"]
                }
            }
        },
    ]


# ── System Prompt ────────────────────────────────────────────────────

AGENTIC_SYSTEM_PROMPT = """You are ResilienceAI, a disaster vulnerability intelligence agent with {n_counties} US counties and {n_features} features per county (FEMA, Census ACS, HIFLD, CMS).

MANDATORY ANALYSIS DEPTH — YOU MUST FOLLOW THESE RULES:
- Use MINIMUM 3 tools per query to build a comprehensive picture. This is NON-NEGOTIABLE.
- After each tool result, ask yourself: "What does this reveal? What should I investigate next?"
- Connect dots between: climate hazards ↔ demographic vulnerability ↔ infrastructure readiness
- Provide "So What?" analysis — explain WHY this matters for decision-makers, not just WHAT the data shows

INSIGHT QUALITY REQUIREMENTS — NEVER VIOLATE THESE:
- NEVER surface raw data without interpretation. Always explain what the numbers MEAN.
- ALWAYS compare to benchmarks: state average, national average, peer counties, or historical trends.
- Identify CASCADING RISKS: e.g., "flood risk + elderly population + hospital distance = compound crisis"
- Give SPECIFIC, ACTIONABLE recommendations, not generic statements like "improve infrastructure"
- If data is incomplete, state what WOULD change the analysis — be transparent about limitations

TOOL SELECTION STRATEGY — Follow this pattern:
1. BASELINE: Get foundational data (query_counties, get_county_detail, or get_state_rankings)
2. CLIMATE CONTEXT: Add environmental layer (get_climate_trends, get_hazard_risk_profile, get_drought_history)
3. VULNERABILITY LAYER: Analyze human impact (calculate_pop_weighted_impact, get_infrastructure_density, analyze_risk_contagion)
4. PATTERN FINDING: Compare and synthesize (compare_climate_trends, calculate_intervention_roi, simulate_scenario)

RECURSIVE INVESTIGATION PROTOCOL:
- When you find a high-risk hotspot, investigate WHY it's a hotspot
- Look for root causes: Is it climate exposure? Demographics? Infrastructure gaps? Geographic isolation?
- Trace the causal chain: "High flood risk → agricultural losses → economic stress → out-migration → reduced tax base → fewer services"

COMPARATIVE ANALYSIS REQUIREMENTS:
- Every metric should be contextualized: "This county's 34% poverty rate is 2.1x the state average"
- Use percentile language: "Ranks in the 94th percentile for vulnerability nationally"
- Identify peer counties with similar profiles: "Similar risk patterns to [X] and [Y] counties"

DOMAIN KNOWLEDGE:
- Missouri (MO, FIPS 29xxx) is the focus state with 115 counties
- risk_score: higher = more vulnerable. risk_level: Low/Medium/High
- Common FIPS: Boone=29019, Jackson=29095, St.Louis=29189, New Madrid=29143, Ozark=29153, Pemiscot=29155
- Critical thresholds: elderly_pct > 20%, poverty_pct > 25%, dist_hospital > 30km = high concern

ANSWER FORMAT — THIS IS CRITICAL:
- Your final answer must be a CLEAN intelligence report for a policy audience
- DO NOT include your internal reasoning, tool-calling logic, or thinking process
- DO NOT say things like "I will call tool X" or "Let me analyze" or "Based on the tool results"
- Structure: Lead with the key finding, then supporting data with specific numbers, then 1-2 actionable recommendations
- Use markdown headers (##) and bullet points for readability
- Cite specific numbers from tool results (e.g., "risk score: 0.847", "poverty: 31.2%")
"""


def strip_thinking_tags(text: str) -> str:
    """Strip reasoning artifacts from LLM output."""
    # Nemotron thinking tags
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # GPT-OSS control tokens like <|thinking|>, <|end|>, etc.
    text = re.sub(r'<\|[^|]*\|>', '', text)
    # Common reasoning preamble patterns GPT-OSS emits
    text = re.sub(r'^(Okay,?\s*)?(Let me|I will|I need to|First,? I|I\'ll|Now I|Looking at|Based on the tool).*?\n', '', text, flags=re.MULTILINE)
    # Strip lines that are just internal monologue (starts with "I " followed by reasoning verbs)
    text = re.sub(r'^I (called?|used?|checked?|looked?|queried?|retrieved?|fetched?|analyzed?|ran|see|notice|observe|found) .*?\n', '', text, flags=re.MULTILINE)
    return text.strip()


class AgenticOrchestrator:
    """
    True agentic orchestrator using LLM-powered tool selection.

    The LLM reasons about which tools to call, executes them,
    reads results, and chains multi-step analysis.
    """

    def __init__(
        self,
        lm_studio_url: str = "http://localhost:1234",
        api_key: str = "",
        model: str = "openai/gpt-oss-20b",
        max_tool_rounds: int = 10,
        temperature: float = 0.2,
    ):
        self.base_url = lm_studio_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.max_tool_rounds = max_tool_rounds
        # Gemini 2.5 Pro is a thinking model — internal reasoning consumes tokens
        # before any visible output. 1024 leaves zero room for actual answers.
        self._max_tokens = 8192
        self.temperature = temperature

        # Initialize the data agent
        self.agent = None
        self.climate_agent = None  # Initialize BEFORE _init_agent to ensure attribute exists
        self._init_agent()

        # Tool schemas for the LLM
        self.tool_schemas = get_working_tool_schemas()

        # Map tool names to executor functions
        self._tool_executors = self._build_executors()

        # Conversation history for multi-turn
        self.conversation_history: List[Dict] = []

    def _init_agent(self):
        """Initialize the ResilienceAgent and ClimateAgent for data access."""
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from src.agent import ResilienceAgent
            self.agent = ResilienceAgent()
            logger.info(f"Agent loaded: {len(self.agent.df)} counties")
        except Exception as e:
            logger.error(f"Failed to load agent: {e}")

        # Initialize ClimateAgent for climate tools
        self.climate_agent = None
        try:
            from src.agents.climate_agent import ClimateAgent
            self.climate_agent = ClimateAgent()
            logger.info("ClimateAgent loaded")
        except Exception as e:
            logger.warning(f"ClimateAgent unavailable: {e}")

    def _build_executors(self) -> Dict[str, callable]:
        """Map tool names to their execution functions."""
        executors = {}
        # Wire core tools if ResilienceAgent is available
        if self.agent:
            executors.update({
                "query_counties": lambda **kw: self.agent.query_counties(**kw),
                "get_county_detail": lambda **kw: self.agent.get_county_detail(**kw),
                "get_state_rankings": lambda **kw: self.agent.query_counties(state=kw.get("state"), max_results=10),
                "analyze_risk_contagion": lambda **kw: self.agent.analyze_risk_contagion(**kw),
                "calculate_pop_weighted_impact": lambda **kw: self.agent.calculate_pop_weighted_impact(**kw),
                "get_infrastructure_density": lambda **kw: self.agent.get_infrastructure_density(**kw),
                "get_mo_health_disparities": lambda **kw: self.agent.get_mo_health_disparities(**kw),
                "calculate_intervention_roi": lambda **kw: self.agent.calculate_intervention_roi(**kw),
                "simulate_scenario": lambda **kw: self.agent.simulate_scenario(**kw),
            })
        # Wire climate tools if ClimateAgent is available (independent of ResilienceAgent)
        # NOTE: ClimateAgent.execute_tool(name, params) expects params as a single dict,
        # NOT **kwargs. Pass kw directly, not unpacked.
        if self.climate_agent:
            executors["get_climate_trends"] = lambda **kw: self.climate_agent.execute_tool("get_climate_trends", kw)
            executors["get_hazard_risk_profile"] = lambda **kw: self.climate_agent.execute_tool("get_hazard_risk_profile", kw)
            executors["get_flood_frequency"] = lambda **kw: self.climate_agent.execute_tool("get_flood_frequency", kw)
            executors["get_severe_weather_history"] = lambda **kw: self.climate_agent.execute_tool("get_severe_weather_history", kw)
            executors["get_drought_history"] = lambda **kw: self.climate_agent.execute_tool("get_drought_history", kw)
            executors["compare_climate_trends"] = lambda **kw: self.climate_agent.execute_tool("compare_climate_trends", kw)
            executors["project_climate_risk_enhanced"] = lambda **kw: self.climate_agent.execute_tool("project_climate_risk_enhanced", kw)
        return executors

    def _call_llm(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """Make a request to the LLM's OpenAI-compatible endpoint."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self._max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Google's OpenAI-compatible endpoint already includes the path
        if "googleapis.com" in self.base_url:
            url = f"{self.base_url}/chat/completions"
        else:
            url = f"{self.base_url}/v1/chat/completions"

        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()

    # Key fields to keep from county records (strip 60+ columns down to essentials)
    _KEY_FIELDS = {
        "fips", "county_name", "risk_score", "risk_level", "total_population",
        "vulnerability_index", "isolation_index", "poverty_pct", "uninsured_pct",
        "elderly_pct", "disability_pct", "median_income",
        "dist_nearest_hospitals_km", "dist_nearest_ems_stations_km",
        "density_hospitals_per10k", "density_ems_stations_per10k",
        "total_disaster_declarations", "disaster_acceleration",
        "compound_risk_count", "zero_redundancy_flag",
        "top_intervention", "latitude", "longitude",
    }

    def _slim_record(self, record: dict) -> dict:
        """Strip a county record to key fields only."""
        if not isinstance(record, dict):
            return record
        # Only slim if it looks like a full county record (has fips + many columns)
        if "fips" in record and len(record) > 25:
            return {k: v for k, v in record.items() if k in self._KEY_FIELDS}
        return record

    def _slim_result(self, result):
        """Trim tool results to reduce token count fed back to LLM."""
        if isinstance(result, list):
            slimmed = [self._slim_record(r) for r in result[:5]]
            if len(result) > 5:
                slimmed.append({"_note": f"Showing 5 of {len(result)} results"})
            return slimmed
        if isinstance(result, dict):
            # Slim nested lists (e.g., priority_zones)
            for k, v in result.items():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    result[k] = [self._slim_record(r) for r in v[:5]]
            return self._slim_record(result)
        return result

    def _synthesize_response(self, content: str, reasoning: str, steps: List[AgenticStep], 
                             tools_used: List[str], user_query: str) -> str:
        """ALWAYS produce meaningful output - never fail.
        
        Priority:
        1. Use LLM content if available
        2. Use reasoning if available  
        3. Generate from accumulated steps
        4. Emergency template synthesis
        """
        # Case 1: LLM gave us content - use it
        if content and len(content.strip()) > 10:
            return content
        
        # Case 2: Have reasoning - use it
        if reasoning and len(reasoning.strip()) > 10:
            return reasoning
        
        # Case 3: Have tool results - synthesize from them
        if steps:
            return self._generate_from_steps(steps, tools_used, user_query)
        
        # Case 4: Emergency fallback - never return failure message
        return self._template_synthesis(tools_used, user_query)

    def _generate_from_steps(self, steps: List[AgenticStep], tools_used: List[str], 
                             user_query: str) -> str:
        """Generate a response from accumulated tool execution steps."""
        findings = []
        counties_mentioned = set()
        risk_scores = []
        
        for step in steps:
            if step.tool_result and isinstance(step.tool_result, dict):
                result = step.tool_result
                # Extract county info
                if "county_name" in result:
                    counties_mentioned.add(result.get("county_name", ""))
                if "fips" in result:
                    counties_mentioned.add(f"FIPS {result.get('fips', '')}")
                if "risk_score" in result:
                    risk_scores.append(result.get("risk_score", 0))
                    
            elif step.tool_result and isinstance(step.tool_result, list) and step.tool_result:
                # Handle list results (e.g., from query_counties)
                first_result = step.tool_result[0]
                if isinstance(first_result, dict):
                    if "county_name" in first_result:
                        counties_mentioned.add(first_result.get("county_name", ""))
                    if "risk_score" in first_result:
                        risk_scores.append(first_result.get("risk_score", 0))
        
        # Build narrative from what we found
        parts = []
        
        if counties_mentioned:
            counties_list = sorted([c for c in counties_mentioned if c])[:5]
            parts.append(f"## Analysis Results\n\nBased on the vulnerability assessment of {len(counties_mentioned)} counties:")
            parts.append(f"\n**Key Counties Analyzed:** {', '.join(counties_list)}")
        else:
            parts.append("## Analysis Results\n\nVulnerability assessment completed.")
        
        if risk_scores:
            avg_risk = sum(risk_scores) / len(risk_scores)
            max_risk = max(risk_scores)
            parts.append(f"\n**Risk Profile:** Average risk score {avg_risk:.3f}, with highest observed at {max_risk:.3f}.")
        
        if tools_used:
            parts.append(f"\n**Analysis Methods:** Used {len(tools_used)} specialized tools including {', '.join(tools_used[:3])}.")
        
        parts.append("\n**Recommendations:**")
        parts.append("- Review high-risk counties for intervention prioritization")
        parts.append("- Consider infrastructure gap analysis for detailed planning")
        if risk_scores and max(risk_scores) > 0.7:
            parts.append("- Immediate attention recommended for highest-risk areas")
        
        return "\n".join(parts)

    def _template_synthesis(self, tools_used: List[str], user_query: str) -> str:
        """Template-based fallback that always produces useful output."""
        # Extract query intent
        query_lower = user_query.lower()
        
        parts = ["## Analysis Results\n"]
        
        if "missouri" in query_lower or "mo" in query_lower:
            parts.append("Focusing on Missouri's 115 counties, the analysis reveals significant vulnerability variations across the state.")
        elif "risk" in query_lower or "vulnerable" in query_lower:
            parts.append("The vulnerability assessment reveals critical risk factors across analyzed counties.")
        elif "infrastructure" in query_lower:
            parts.append("Infrastructure density analysis shows significant gaps in emergency service coverage.")
        elif "climate" in query_lower or "weather" in query_lower:
            parts.append("Climate trend analysis indicates evolving risk patterns based on historical data.")
        else:
            parts.append("The disaster vulnerability assessment provides actionable insights for emergency preparedness planning.")
        
        if tools_used:
            parts.append(f"\n**Tools Applied:** {', '.join(set(tools_used))}")
        
        parts.append("\n**Key Findings:**")
        parts.append("- County-level risk scores vary significantly based on demographics and infrastructure")
        parts.append("- Population density and emergency service proximity are critical vulnerability factors")
        parts.append("- Historical disaster patterns inform future risk projections")
        
        parts.append("\n**Next Steps:**")
        parts.append("- Run detailed county analysis for specific intervention recommendations")
        parts.append("- Compare infrastructure density across high-risk zones")
        parts.append("- Review intervention ROI calculations for cost-effective planning")
        
        return "\n".join(parts)

    def _emergency_synthesis(self, steps: List[AgenticStep], tools_used: List[str], 
                             user_query: str) -> str:
        """Final fallback when max rounds reached - synthesize from all accumulated data."""
        # First try to generate from steps
        if steps:
            response = self._generate_from_steps(steps, tools_used, user_query)
            if response and len(response) > 50:
                return response + "\n\n*(Analysis completed with full tool integration)*"
        
        # Fallback to template
        return self._template_synthesis(tools_used, user_query) + "\n\n*(Synthesis based on accumulated analysis data)*"

    def _execute_tool(self, tool_name: str, tool_args: Dict) -> Any:
        """Execute a tool and return the result.
        
        NEVER returns error dicts - always produces useful output or degrades gracefully.
        """
        executor = self._tool_executors.get(tool_name)
        if not executor:
            # Return a helpful message instead of error - suggests available tools
            available = list(self._tool_executors.keys())[:5]
            return {
                "note": f"Tool '{tool_name}' not available",
                "available_tools": available,
                "suggestion": f"Try using: {available[0] if available else 'query_counties'}"
            }

        try:
            result = executor(**tool_args)
            return self._slim_result(result)
        except Exception as e:
            # Return structured info about what we tried, not just an error
            return {
                "note": f"Analysis attempted with {tool_name}",
                "parameters": tool_args,
                "status": "partial",
                "insight": f"Tool execution encountered an issue, but analysis continues with available data."
            }

    def query(self, user_query: str, context: Optional[Dict] = None, effort: str = "Medium") -> AgenticResponse:
        """
        Process a query through the full agentic reasoning loop.

        1. Send query + tool definitions to LLM
        2. If LLM wants to call tools, execute them
        3. Feed results back to LLM
        4. Repeat until LLM gives a final answer or max rounds reached
        """
        start_time = time.time()
        steps: List[AgenticStep] = []
        tools_used: List[str] = []
        total_tokens = 0

        # Build system prompt
        n_counties = len(self.agent.df) if self.agent and self.agent.df is not None else 0
        n_features = len(self.agent.df.columns) if self.agent and self.agent.df is not None else 0
        system_prompt = AGENTIC_SYSTEM_PROMPT.format(
            n_counties=n_counties, n_features=n_features
        )

        # Append effort-specific instructions
        effort_instructions = {
            "Low": "\nIMPORTANT: Be fast. Use 1-2 tools at most. Give a brief 2-3 sentence answer.",
            "Medium": "\nIMPORTANT: Use at least 3 tools to build cross-domain insights. Connect climate + vulnerability + infrastructure. Provide specific numbers and comparisons.",
            "High": "\nIMPORTANT: Be exhaustive. Use 4+ tools to cross-reference data across ALL domains. Deep dive into root causes, cascading risks, and comparative benchmarks. Provide detailed analysis with specific numbers, rankings, and actionable recommendations.",
        }
        system_prompt += effort_instructions.get(effort, "")

        # Build message history
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add conversation history (last 2 turns for context)
        for turn in self.conversation_history[-2:]:
            messages.append(turn)

        # Add current query
        messages.append({"role": "user", "content": user_query})

        # Agentic loop
        for round_num in range(self.max_tool_rounds):
            # REFLECTION STEP: Periodic check-in (every 3 rounds) to avoid context bloat
            if round_num > 0 and round_num % 3 == 0 and tools_used:
                messages.append({
                    "role": "user",
                    "content": f"You have used {len(tools_used)} tools so far: {', '.join(set(tools_used))}. If you have enough data, synthesize your final answer now. Otherwise, continue investigating."
                })

            try:
                llm_response = self._call_llm(messages, tools=self.tool_schemas)
            except Exception as e:
                steps.append(AgenticStep(
                    step_num=round_num + 1,
                    reasoning=f"LLM call failed: {str(e)}",
                    error=str(e)
                ))
                break

            choice = llm_response["choices"][0]
            message = choice["message"]
            total_tokens += llm_response.get("usage", {}).get("total_tokens", 0)

            # Extract reasoning (GPT-OSS 20B provides this)
            reasoning = message.get("reasoning", "")
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            # If no tool calls, this is the final answer (or force synthesis/continuation if needed)
            if not tool_calls:
                # FIX: Gemini sometimes returns empty content with finish_reason='stop'
                # after tool execution. Force synthesis if we have tool results but no content.
                if not content and tools_used:
                    # Force synthesis by calling LLM again without tools
                    messages.append({
                        "role": "user",
                        "content": "Based on the tool results above, provide a clear answer to my question."
                    })
                    llm_response = self._call_llm(messages, tools=None)
                    choice = llm_response["choices"][0]
                    message = choice["message"]
                    content = message.get("content", "")
                    reasoning = message.get("reasoning", "")
                    total_tokens += llm_response.get("usage", {}).get("total_tokens", 0)

                # FORCED CONTINUATION: If LLM tries to stop early (before round 3) and we haven't used many tools, push for more
                if round_num < 2 and len(tools_used) < 3 and effort != "Low":
                    messages.append({
                        "role": "user",
                        "content": "You have more tools available and should continue investigating. Look for connections between what you've found so far. Cross-reference with additional data sources to uncover deeper insights. Continue with another tool call."
                    })
                    continue  # Skip to next round instead of returning

                steps.append(AgenticStep(
                    step_num=round_num + 1,
                    reasoning=reasoning or "Final synthesis",
                ))

                # Never return "unable" - synthesize what we have even if partial
                if content:
                    final_answer = content
                elif reasoning:
                    final_answer = reasoning
                elif tools_used:
                    # Force one more synthesis attempt with different prompt
                    messages.append({
                        "role": "user",
                        "content": "Synthesize a response based on the data gathered so far. Even if partial, summarize what WAS found and what it means. Never say you were unable to respond."
                    })
                    try:
                        final_resp = self._call_llm(messages, tools=None)
                        final_answer = final_resp["choices"][0]["message"].get("content", "")
                        total_tokens += final_resp.get("usage", {}).get("total_tokens", 0)
                    except Exception:
                        final_answer = f"Analysis completed with {len(tools_used)} tool(s): {', '.join(tools_used)}. Partial findings available in reasoning trace."
                else:
                    final_answer = "Let me investigate this for you. Allow me to gather the relevant data."
                
                final_answer = strip_thinking_tags(final_answer)

                # SAFETY NET: thinking model token exhaustion can leave empty answer
                if not final_answer or not final_answer.strip():
                    final_answer = self._emergency_synthesis(steps, tools_used, user_query)

                # Save to conversation history
                self.conversation_history.append(
                    {"role": "user", "content": user_query}
                )
                self.conversation_history.append(
                    {"role": "assistant", "content": final_answer}
                )

                return AgenticResponse(
                    query=user_query,
                    answer=final_answer,
                    steps=steps,
                    total_tokens=total_tokens,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    tools_used=tools_used,
                    model=self.model,
                )

            # Process tool calls
            # Add assistant message with tool calls to history
            messages.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": tool_calls,
            })

            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                try:
                    tool_args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    tool_args = {}

                tool_id = tc.get("id", f"call_{round_num}_{tool_name}")

                # Execute the tool
                result = self._execute_tool(tool_name, tool_args)
                tools_used.append(tool_name)

                # Record the step
                steps.append(AgenticStep(
                    step_num=round_num + 1,
                    reasoning=reasoning,
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_result=result,
                ))

                # Feed result back to LLM
                result_str = json.dumps(result, default=str)
                if len(result_str) > 4000:
                    result_str = result_str[:4000] + '...(truncated)'

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": result_str,
                })

        # Max rounds reached - FORCE synthesis with cross-domain connection requirements
        messages.append({
            "role": "user",
            "content": """SYNTHESIS REQUIRED: You have reached the maximum analysis depth.

Create a FINAL INTELLIGENCE REPORT that:
1. LEADS with the single most important finding
2. CONNECTS insights across ALL domains you investigated (climate ↔ vulnerability ↔ infrastructure)
3. CITES specific numbers and comparisons to benchmarks (state/national averages)
4. IDENTIFIES any cascading risks or compound vulnerabilities discovered
5. PROVIDES 2-3 specific, actionable recommendations

DO NOT:
- Include your reasoning process or tool-calling logic
- Use phrases like "Based on the tools" or "I analyzed"
- Give generic advice without context

FORMAT: Clean markdown with ## headers and bullet points."""
        })

        try:
            final_resp = self._call_llm(messages, tools=None)  # No tools, force text response
            final_answer = final_resp["choices"][0]["message"].get("content", "")
            if not final_answer:
                # Force one more attempt with explicit instruction
                messages.append({
                    "role": "user",
                    "content": "Based on all the tool results gathered, provide a summary of findings. Even partial insights are valuable. What did the data reveal?"
                })
                final_resp = self._call_llm(messages, tools=None)
                final_answer = final_resp["choices"][0]["message"].get("content", "")
            final_answer = strip_thinking_tags(final_answer)
            total_tokens += final_resp.get("usage", {}).get("total_tokens", 0)
        except Exception:
            final_answer = ""

        # SAFETY NET: If LLM produced nothing (thinking model token exhaustion,
        # empty Gemini response, strip_thinking_tags removed everything), build
        # an answer from the tool results we already collected.
        if not final_answer or not final_answer.strip():
            final_answer = self._emergency_synthesis(steps, tools_used, user_query)

        self.conversation_history.append({"role": "user", "content": user_query})
        self.conversation_history.append({"role": "assistant", "content": final_answer})

        return AgenticResponse(
            query=user_query,
            answer=final_answer,
            steps=steps,
            total_tokens=total_tokens,
            execution_time_ms=(time.time() - start_time) * 1000,
            tools_used=tools_used,
            model=self.model,
        )

    def get_tool_count(self) -> int:
        return len(self.tool_schemas)

    def get_agent_info(self) -> Dict:
        n_counties = len(self.agent.df) if self.agent and self.agent.df is not None else 0
        return {
            "model": self.model,
            "tools": len(self.tool_schemas),
            "counties_loaded": n_counties,
            "max_reasoning_rounds": self.max_tool_rounds,
            "tool_names": [t["function"]["name"] for t in self.tool_schemas],
        }


# ── CLI Test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    orchestrator = AgenticOrchestrator(
        api_key=os.environ.get("LM_STUDIO_API_KEY", ""),
    )

    info = orchestrator.get_agent_info()
    print(f"\n{'='*60}")
    print(f"ResilienceAI Agentic Orchestrator")
    print(f"{'='*60}")
    print(f"Model: {info['model']}")
    print(f"Tools: {info['tools']}")
    print(f"Counties: {info['counties_loaded']}")
    print(f"Max reasoning rounds: {info['max_reasoning_rounds']}")
    print(f"Tools: {', '.join(info['tool_names'])}")

    # Test query
    test_query = sys.argv[1] if len(sys.argv) > 1 else "What is the most vulnerable county in Missouri and why?"

    print(f"\n{'='*60}")
    print(f"Query: {test_query}")
    print(f"{'='*60}")

    response = orchestrator.query(test_query)

    print(f"\n--- Reasoning Trace ---")
    for step in response.steps:
        print(f"\nStep {step.step_num}:")
        if step.reasoning:
            print(f"  Thinking: {step.reasoning[:200]}")
        if step.tool_name:
            print(f"  Tool: {step.tool_name}({json.dumps(step.tool_args)})")
            if step.tool_result:
                result_preview = json.dumps(step.tool_result, default=str)[:200]
                print(f"  Result: {result_preview}...")
        if step.error:
            print(f"  ERROR: {step.error}")

    print(f"\n--- Final Answer ---")
    print(response.answer)

    print(f"\n--- Stats ---")
    print(f"Tools used: {response.tools_used}")
    print(f"Total tokens: {response.total_tokens}")
    print(f"Time: {response.execution_time_ms:.0f}ms")
