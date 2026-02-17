"""
ResilienceAI - True Agentic Orchestrator
LLM-powered reasoning loop using GPT-OSS 20B via LM Studio.

The LLM decides which tools to call, reads results, chains multi-step
analysis, and synthesizes novel insights from real data.
"""
import json
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
    ]


# ── System Prompt ────────────────────────────────────────────────────

AGENTIC_SYSTEM_PROMPT = """You are ResilienceAI, a disaster vulnerability intelligence agent with {n_counties} US counties and {n_features} features per county (FEMA, Census ACS, HIFLD, CMS).

RULES:
- Use tools to get real data. NEVER make up numbers.
- Chain tools when needed (1-3 calls typical). Stop when you have enough.
- Missouri (MO, FIPS 29xxx) is the focus state with 115 counties.
- risk_score: higher = more vulnerable. risk_level: Low/Medium/High.
- Answer concisely: key finding, supporting numbers, 1-2 recommendations.
"""


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
        max_tool_rounds: int = 3,
        temperature: float = 0.2,
    ):
        self.base_url = lm_studio_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.max_tool_rounds = max_tool_rounds
        self._max_tokens = 1024
        self.temperature = temperature

        # Initialize the data agent
        self.agent = None
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
        if not self.agent:
            return {}
        executors = {
            "query_counties": lambda **kw: self.agent.query_counties(**kw),
            "get_county_detail": lambda **kw: self.agent.get_county_detail(**kw),
            "get_state_rankings": lambda **kw: self.agent.get_state_rankings(**kw),
            "analyze_risk_contagion": lambda **kw: self.agent.analyze_risk_contagion(**kw),
            "calculate_pop_weighted_impact": lambda **kw: self.agent.calculate_pop_weighted_impact(**kw),
            "get_infrastructure_density": lambda **kw: self.agent.get_infrastructure_density(**kw),
            "get_mo_health_disparities": lambda **kw: self.agent.get_mo_health_disparities(**kw),
            "calculate_intervention_roi": lambda **kw: self.agent.calculate_intervention_roi(**kw),
            "simulate_scenario": lambda **kw: self.agent.simulate_scenario(**kw),
        }
        # Wire climate tools if ClimateAgent is available
        if self.climate_agent:
            executors["get_climate_trends"] = lambda **kw: self.climate_agent.execute_tool("get_climate_trends", kw)
            executors["get_hazard_risk_profile"] = lambda **kw: self.climate_agent.execute_tool("get_hazard_risk_profile", kw)
        return executors

    def _call_llm(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """Make a request to LM Studio's OpenAI-compatible endpoint."""
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

        resp = requests.post(
            f"{self.base_url}/v1/chat/completions",
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

    def _execute_tool(self, tool_name: str, tool_args: Dict) -> Any:
        """Execute a tool and return the result."""
        executor = self._tool_executors.get(tool_name)
        if not executor:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            result = executor(**tool_args)
            return self._slim_result(result)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

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
            "Low": "\nIMPORTANT: Be fast. Use 1 tool at most. Give a brief 2-3 sentence answer.",
            "Medium": "",
            "High": "\nIMPORTANT: Be thorough. Use multiple tools to cross-reference data. Compare counties, check infrastructure AND demographics. Provide detailed analysis with specific numbers and rankings.",
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

            # If no tool calls, this is the final answer
            if not tool_calls or choice.get("finish_reason") == "stop":
                steps.append(AgenticStep(
                    step_num=round_num + 1,
                    reasoning=reasoning or "Final synthesis",
                ))

                final_answer = content or reasoning or "I was unable to generate a response."
                # Strip model control tokens that GPT-OSS 20B sometimes emits
                final_answer = re.sub(r'<\|[^|]*\|>', '', final_answer).strip()

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
                # Truncate to keep LLM context lean
                if len(result_str) > 2000:
                    result_str = result_str[:2000] + '...(truncated)'

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": result_str,
                })

        # Max rounds reached - ask LLM to synthesize what it has
        messages.append({
            "role": "user",
            "content": "Please synthesize your findings into a final answer based on the data you've gathered."
        })

        try:
            final_resp = self._call_llm(messages, tools=None)  # No tools, force text response
            final_answer = final_resp["choices"][0]["message"].get("content", "Analysis complete but synthesis failed.")
            final_answer = re.sub(r'<\|[^|]*\|>', '', final_answer).strip()
            total_tokens += final_resp.get("usage", {}).get("total_tokens", 0)
        except Exception:
            final_answer = "Reached maximum analysis depth. See reasoning trace for partial results."

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
        api_key="sk-lm-17g8iJ72:Jkqk55kdkSVRwtUfklSj",
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
