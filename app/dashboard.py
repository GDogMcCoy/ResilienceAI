"""
ResilienceAI - Agentic Intelligence Platform
Chat-first interface backed by 16 real-data tools, dual LLM backends,
and inline visualizations across 3,222 US counties.
"""

import sys
import os
from pathlib import Path

# Fix path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import plotly.express as px
import plotly.graph_objects as go

# Try to import internal modules
try:
    from agent import ResilienceAgent, get_mcp_tools, _filter_by_state
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

try:
    from agentic_orchestrator import AgenticOrchestrator, MODEL_PRESETS, strip_thinking_tags
    AGENTIC_AVAILABLE = True
except ImportError:
    AGENTIC_AVAILABLE = False

# -- Page Configuration -------------------------------------------------
st.set_page_config(
    page_title="ResilienceAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -- Minimal Dark Theme -------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    div[data-testid="stExpander"] { border: 1px solid #2d3748; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# -- Initialize Session State -------------------------------------------
def init_session_state():
    defaults = {
        'agent_config': {
            'lm_key': os.environ.get("LM_STUDIO_API_KEY", "sk-lm-17g8iJ72:Jkqk55kdkSVRwtUfklSj"),
            'gemini_key': os.environ.get("GEMINI_API_KEY", "AIzaSyCEw7kaEic59l7O3mMAw0ObtxCO5sztJ7o"),
            'lm_url': 'http://localhost:1234',
            'reasoning_effort': 'Medium',
            'focus_state': 'Missouri',
            'selected_model': 'gemini-pro',
        },
        'last_agent_response': None,
        'df': None,
        'local_agent': None,
        'query_input': "",
        'agentic_orchestrator': None,
        'chat_history': [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# -- Load Data ----------------------------------------------------------
@st.cache_data
def load_data():
    try:
        features_path = Path(__file__).parent.parent / "data" / "processed" / "county_features.csv"
        if features_path.exists():
            return pd.read_csv(features_path, dtype={"fips": str})
    except Exception as e:
        st.error(f"Data Load Error: {e}")
    return None

df = load_data()
if df is not None:
    st.session_state.df = df
    if AGENT_AVAILABLE and st.session_state.local_agent is None:
        st.session_state.local_agent = ResilienceAgent()


# ═══════════════════════════════════════════════════════════════════════
# TOOL VISUALIZATION — Auto-render charts from agentic tool results
# ═══════════════════════════════════════════════════════════════════════

def render_tool_visuals(steps):
    """Scan AgenticSteps and render inline charts for each tool result."""
    for step in steps:
        if not step.tool_name or not step.tool_result:
            continue
        data = step.tool_result
        name = step.tool_name

        try:
            # ── County rankings: bar chart + table ─────────────────────
            if name in ("query_counties", "get_state_rankings"):
                records = data if isinstance(data, list) else data.get("counties", data.get("rankings", []))
                records = [r for r in records if isinstance(r, dict) and "county_name" in r and "risk_score" in r]
                if records:
                    rdf = pd.DataFrame(records)
                    fig = px.bar(
                        rdf.sort_values("risk_score", ascending=True),
                        x="risk_score", y="county_name", orientation="h",
                        color="risk_score", color_continuous_scale="RdYlGn_r",
                        title=f"County Risk Rankings ({len(rdf)})"
                    )
                    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                      plot_bgcolor="rgba(0,0,0,0)", height=max(250, len(rdf)*35),
                                      yaxis_title="", xaxis_title="Risk Score")
                    st.plotly_chart(fig, use_container_width=True)
                    show_cols = [c for c in ["county_name", "risk_score", "risk_level", "total_population", "poverty_pct"] if c in rdf.columns]
                    st.dataframe(rdf[show_cols], use_container_width=True, hide_index=True)

            # ── County detail: metric cards ────────────────────────────
            elif name == "get_county_detail":
                if isinstance(data, dict) and "error" not in data:
                    cname = data.get("county_name", "County")
                    st.markdown(f"**{cname}**")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Population", f"{data.get('total_population', 'N/A'):,}" if isinstance(data.get('total_population'), (int, float)) else "N/A")
                    c2.metric("Risk Score", f"{data.get('risk_score', 'N/A'):.3f}" if isinstance(data.get('risk_score'), (int, float)) else "N/A")
                    c3.metric("Risk Level", data.get("risk_level", "N/A"))
                    c4, c5, c6 = st.columns(3)
                    c4.metric("Poverty", f"{data.get('poverty_pct', 'N/A'):.1f}%" if isinstance(data.get('poverty_pct'), (int, float)) else "N/A")
                    c5.metric("Uninsured", f"{data.get('uninsured_pct', 'N/A'):.1f}%" if isinstance(data.get('uninsured_pct'), (int, float)) else "N/A")
                    hosp = data.get("dist_nearest_hospitals_km")
                    c6.metric("Hospital Dist", f"{hosp:.1f} km" if isinstance(hosp, (int, float)) else "N/A")

            # ── Infrastructure density: 4 cards ────────────────────────
            elif name == "get_infrastructure_density":
                if isinstance(data, dict) and "error" not in data:
                    st.markdown(f"**Infrastructure Density** — {data.get('county_name', data.get('fips', ''))}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Hospitals/10k", f"{data.get('hospitals_per_10k', data.get('density_hospitals_per10k', 0)):.2f}")
                    c2.metric("EMS/10k", f"{data.get('ems_per_10k', data.get('density_ems_stations_per10k', 0)):.2f}")
                    c3.metric("Fire/10k", f"{data.get('fire_per_10k', data.get('density_fire_stations_per10k', 0)):.2f}")

            # ── Risk contagion: 3 metrics ──────────────────────────────
            elif name == "analyze_risk_contagion":
                if isinstance(data, dict) and "error" not in data:
                    st.markdown(f"**Risk Contagion Analysis** — {data.get('county_name', data.get('fips', ''))}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Neighbors", data.get("neighbor_count", data.get("neighbors_in_radius", "N/A")))
                    c2.metric("High-Risk Neighbors", data.get("high_risk_neighbors", "N/A"))
                    c3.metric("Amplification", f"{data.get('amplification_factor', data.get('risk_amplification', 'N/A'))}")

            # ── Health disparities: bar chart ──────────────────────────
            elif name == "get_mo_health_disparities":
                zones = data if isinstance(data, list) else data.get("priority_zones", data.get("disparities", []))
                zones = [z for z in zones if isinstance(z, dict) and "county_name" in z]
                if zones:
                    zdf = pd.DataFrame(zones)
                    metric_col = next((c for c in ["disparity_index", "uninsured_pct", "poverty_pct"] if c in zdf.columns), None)
                    if metric_col:
                        fig = px.bar(zdf.sort_values(metric_col, ascending=True),
                                     x=metric_col, y="county_name", orientation="h",
                                     color=metric_col, color_continuous_scale="Reds",
                                     title="Health Disparity Index by County")
                        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                          plot_bgcolor="rgba(0,0,0,0)", height=max(250, len(zdf)*35),
                                          yaxis_title="", xaxis_title=metric_col.replace("_", " ").title())
                        st.plotly_chart(fig, use_container_width=True)

            # ── Intervention ROI: bar chart ────────────────────────────
            elif name == "calculate_intervention_roi":
                interventions = data if isinstance(data, list) else data.get("interventions", data.get("ranked_interventions", []))
                interventions = [i for i in interventions if isinstance(i, dict)]
                if interventions:
                    idf = pd.DataFrame(interventions)
                    name_col = next((c for c in ["intervention", "name", "type"] if c in idf.columns), None)
                    val_col = next((c for c in ["cost_per_person", "roi_score", "cost_effectiveness"] if c in idf.columns), None)
                    if name_col and val_col:
                        fig = px.bar(idf.sort_values(val_col), x=val_col, y=name_col, orientation="h",
                                     color=val_col, color_continuous_scale="Viridis",
                                     title="Intervention Cost-Effectiveness")
                        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                          plot_bgcolor="rgba(0,0,0,0)", height=max(250, len(idf)*40),
                                          yaxis_title="", xaxis_title=val_col.replace("_", " ").title())
                        st.plotly_chart(fig, use_container_width=True)

            # ── Scenario simulation: impact metrics + affected table ───
            elif name == "simulate_scenario":
                if isinstance(data, dict) and "error" not in data:
                    st.markdown(f"**Scenario: {data.get('scenario', 'Simulation')}**")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Population at Risk", f"{data.get('total_population_affected', data.get('population_at_risk', 0)):,}")
                    c2.metric("Counties Affected", data.get("counties_affected", data.get("affected_county_count", "N/A")))
                    c3.metric("Est. Damage", data.get("estimated_damage", data.get("infrastructure_damage_estimate", "N/A")))
                    affected = data.get("affected_counties", [])
                    if affected and isinstance(affected[0], dict):
                        st.dataframe(pd.DataFrame(affected[:10]), use_container_width=True, hide_index=True)

            # ── Pop-weighted impact: bar chart ─────────────────────────
            elif name == "calculate_pop_weighted_impact":
                records = data if isinstance(data, list) else data.get("rankings", data.get("counties", []))
                records = [r for r in records if isinstance(r, dict) and "county_name" in r]
                if records:
                    rdf = pd.DataFrame(records)
                    score_col = next((c for c in ["weighted_impact", "pop_weighted_risk", "impact_score"] if c in rdf.columns), "risk_score")
                    if score_col in rdf.columns:
                        fig = px.bar(rdf.sort_values(score_col, ascending=True),
                                     x=score_col, y="county_name", orientation="h",
                                     color=score_col, color_continuous_scale="RdYlGn_r",
                                     title="Population-Weighted Risk Impact")
                        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                          plot_bgcolor="rgba(0,0,0,0)", height=max(250, len(rdf)*35),
                                          yaxis_title="", xaxis_title="Weighted Impact")
                        st.plotly_chart(fig, use_container_width=True)

            # ── Climate trends: summary metrics ────────────────────────
            elif name == "get_climate_trends":
                if isinstance(data, dict) and "error" not in data:
                    trends = data.get("trends", {})
                    st.markdown(f"**Climate Trends** — FIPS {data.get('fips', '')}")
                    c1, c2, c3 = st.columns(3)
                    temp_info = trends.get("mean_temp", {})
                    precip_info = trends.get("precip", {})
                    c1.metric("Avg Temp", f"{temp_info.get('mean', 'N/A')}°F" if isinstance(temp_info.get('mean'), (int, float)) else "N/A")
                    c2.metric("Temp Trend", f"{temp_info.get('slope_per_decade', 'N/A')}°F/decade" if isinstance(temp_info.get('slope_per_decade'), (int, float)) else "N/A")
                    c3.metric("Avg Precip", f"{precip_info.get('mean', 'N/A')} in" if isinstance(precip_info.get('mean'), (int, float)) else "N/A")

            # ── Hazard risk profile: top hazards ───────────────────────
            elif name == "get_hazard_risk_profile":
                if isinstance(data, dict) and "error" not in data:
                    st.markdown(f"**FEMA Hazard Risk Profile** — FIPS {data.get('fips', '')}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Risk Rating", data.get("risk_rating", "N/A"))
                    c2.metric("Expected Annual Loss", data.get("expected_annual_loss", "N/A"))
                    c3.metric("Social Vulnerability", data.get("social_vulnerability", data.get("sovi_rating", "N/A")))
                    hazards = data.get("hazards", data.get("top_hazards", []))
                    if hazards and isinstance(hazards, list) and isinstance(hazards[0], dict):
                        hdf = pd.DataFrame(hazards[:10])
                        st.dataframe(hdf, use_container_width=True, hide_index=True)

            # ── Flood frequency ────────────────────────────────────────
            elif name == "get_flood_frequency":
                if isinstance(data, dict) and "error" not in data:
                    st.markdown(f"**Flood Frequency Analysis** — FIPS {data.get('fips', '')}")
                    intervals = data.get("recurrence_intervals", data.get("flood_levels", {}))
                    if isinstance(intervals, dict) and intervals:
                        idf = pd.DataFrame([{"Return Period": k, "Flow (cfs)": v} for k, v in intervals.items()])
                        st.dataframe(idf, use_container_width=True, hide_index=True)

            # ── Severe weather history ─────────────────────────────────
            elif name == "get_severe_weather_history":
                if isinstance(data, dict) and "error" not in data:
                    st.markdown(f"**Severe Weather History** — FIPS {data.get('fips', '')}")
                    summary = data.get("summary", {})
                    if summary:
                        cols = st.columns(min(len(summary), 4))
                        for col, (k, v) in zip(cols, list(summary.items())[:4]):
                            col.metric(k.replace("_", " ").title(), v)

            # ── Drought history ────────────────────────────────────────
            elif name == "get_drought_history":
                if isinstance(data, dict) and "error" not in data:
                    st.markdown(f"**Drought History** — FIPS {data.get('fips', '')}")
                    summary = data.get("summary", data.get("statistics", {}))
                    if isinstance(summary, dict):
                        cols = st.columns(min(len(summary), 4))
                        for col, (k, v) in zip(cols, list(summary.items())[:4]):
                            col.metric(k.replace("_", " ").title(), v)

            # ── Climate projections ────────────────────────────────────
            elif name == "project_climate_risk_enhanced":
                if isinstance(data, dict) and "error" not in data:
                    proj = data.get("projection", {})
                    st.markdown(f"**Climate Projection** — {data.get('scenario', 'SSP2-4.5')} ({data.get('horizon_years', 30)}yr)")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Temp Change", f"+{proj.get('temp_change_f', 'N/A')}°F" if isinstance(proj.get('temp_change_f'), (int, float)) else "N/A")
                    c2.metric("Precip Change", f"{proj.get('precip_change_pct', 'N/A')}%" if isinstance(proj.get('precip_change_pct'), (int, float)) else "N/A")
                    c3.metric("Extreme Events", f"{proj.get('extreme_event_multiplier', 'N/A')}x")

        except Exception:
            pass  # Malformed data — skip silently


# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR — Controls & Context
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🛡️ ResilienceAI")
    st.divider()

    # State focus picker
    if df is not None:
        state_list = sorted(df['county_name'].str.extract(r', (.+)$')[0].dropna().unique())
        focus_state = st.selectbox(
            "Focus State",
            ["All States"] + list(state_list),
            index=list(["All States"] + list(state_list)).index("Missouri"),
            help="Filters data panels below. Agentic queries can ask about any state."
        )
        st.session_state.agent_config['focus_state'] = focus_state

    st.divider()

    # ── Model Selector ─────────────────────────────────────────────
    if AGENTIC_AVAILABLE:
        model_options = list(MODEL_PRESETS.keys())
        model_labels = [MODEL_PRESETS[m]["label"] for m in model_options]
        current_model = st.session_state.agent_config.get('selected_model', 'nemotron-3-nano')
        current_idx = model_options.index(current_model) if current_model in model_options else 0

        selected_label = st.radio(
            "LLM Backend",
            model_labels,
            index=current_idx,
            help="Nemotron: fast exploration (~15-30s). GPT-OSS: deep analysis (~40-60s)."
        )
        selected_key = model_options[model_labels.index(selected_label)]
        preset = MODEL_PRESETS[selected_key]

        # Detect model switch → reinitialize orchestrator
        if selected_key != st.session_state.agent_config.get('selected_model'):
            st.session_state.agent_config['selected_model'] = selected_key
            st.session_state.agentic_orchestrator = None  # force re-init

        # Per-model API key selection
        if selected_key == "gemini-pro":
            active_api_key = st.session_state.agent_config['gemini_key']
        else:
            active_api_key = st.session_state.agent_config['lm_key']

        # Advanced connection settings (collapsed)
        with st.expander("Connection Settings", expanded=False):
            lm_url = st.text_input("URL Override", value=preset["base_url"])
            if selected_key == "gemini-pro":
                gemini_key = st.text_input("Gemini API Key", value=st.session_state.agent_config['gemini_key'], type="password")
                st.session_state.agent_config['gemini_key'] = gemini_key
                active_api_key = gemini_key
            else:
                lm_key = st.text_input("LM Studio Key", value=st.session_state.agent_config['lm_key'], type="password")
                st.session_state.agent_config['lm_key'] = lm_key
                active_api_key = lm_key
            st.session_state.agent_config['lm_url'] = lm_url
    else:
        # Fallback if orchestrator module unavailable
        with st.expander("LM Studio", expanded=False):
            lm_url = st.text_input("URL", value=st.session_state.agent_config['lm_url'])
            lm_key = st.text_input("Key", value=st.session_state.agent_config['lm_key'], type="password")
            st.session_state.agent_config['lm_key'] = lm_key
            st.session_state.agent_config['lm_url'] = lm_url
        preset = {"base_url": st.session_state.agent_config['lm_url'], "model": "openai/gpt-oss-20b"}
        selected_key = "gpt-oss-20b"

    # Initialize orchestrator with selected model
    if st.session_state.agentic_orchestrator is None and AGENTIC_AVAILABLE:
        try:
            st.session_state.agentic_orchestrator = AgenticOrchestrator(
                lm_studio_url=st.session_state.agent_config.get('lm_url', preset["base_url"]),
                api_key=active_api_key,
                model=preset["model"],
            )
        except Exception:
            pass

    if st.session_state.agentic_orchestrator:
        info = st.session_state.agentic_orchestrator.get_agent_info()
        st.success(f"{info['model'].split('/')[-1]} | {info['tools']} tools | {info['counties_loaded']:,} counties")
    else:
        st.warning("LLM unavailable — check connection settings")

    effort = st.select_slider(
        "Reasoning Effort",
        options=["Low", "Medium", "High"],
        value=st.session_state.agent_config.get('reasoning_effort', 'Medium'),
    )
    st.session_state.agent_config['reasoning_effort'] = effort

    st.divider()

    # Quick context stats for focused state
    if df is not None:
        fs = st.session_state.agent_config.get('focus_state', 'All States')
        ctx_df = df if fs == "All States" else df[df["county_name"].str.endswith(f", {fs}")]
        if not ctx_df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Counties", f"{len(ctx_df):,}")
            c2.metric("High Risk", f"{len(ctx_df[ctx_df['risk_level'] == 'High'])}")
            c3, c4 = st.columns(2)
            c3.metric("Avg Risk", f"{ctx_df['risk_score'].mean():.3f}")
            c4.metric("Poverty", f"{ctx_df['poverty_pct'].mean():.1f}%")

    st.divider()
    st.caption("MUIDSI Hackathon 2026 | v3.1")


# ═══════════════════════════════════════════════════════════════════════
# MAIN — Agentic Intelligence Interface
# ═══════════════════════════════════════════════════════════════════════

st.markdown("## ResilienceAI")
st.caption("Ask anything about disaster vulnerability, healthcare infrastructure, climate trends, or intervention planning across 3,222 US counties.")

# ── Tabbed Example Prompts ─────────────────────────────────────────
EXAMPLE_PROMPTS = {
    "🔍 Vulnerability": [
        ("Top 5 Vulnerable Counties", "What are the top 5 most vulnerable counties in Missouri? For each, explain what combination of poverty, isolation, and disaster history drives their risk score."),
        ("Risk vs Population", "Which Missouri counties have the highest population-weighted risk? Compare how risk ranking changes when you weight by population vs raw risk score."),
        ("Cross-State Comparison", "Compare the top 3 most vulnerable counties in Missouri vs Arkansas. What structural differences explain the gap?"),
        ("Risk Contagion Clusters", "Analyze risk contagion for St. Louis County, MO (FIPS 29189). How do its high-risk neighbors amplify regional vulnerability?"),
    ],
    "🏥 Healthcare": [
        ("Healthcare Deserts", "Which Missouri counties are healthcare deserts? Show infrastructure density (hospitals, EMS per 10k) and identify counties where distance to the nearest hospital exceeds 50km."),
        ("Infrastructure vs Risk", "For the 5 highest-risk counties in Missouri, what is their emergency infrastructure density? Are the most vulnerable counties also the most underserved?"),
        ("Health Disparities", "What are the worst health disparity zones in Missouri? Compare uninsured rates against poverty rates and identify which counties need targeted intervention."),
        ("Rural Isolation", "Which Missouri counties combine high elderly populations (>20%) with the longest hospital distances? These are the most dangerous for emergency response."),
    ],
    "🌡️ Climate": [
        ("Climate + Vulnerability", "What are the climate trends for Boone County, MO (FIPS 29019)? How do temperature trends and hazard risks interact with its existing vulnerability profile?"),
        ("Flood + Seismic Risk", "What is the flood frequency and severe weather history for New Madrid County, MO (FIPS 29143)? How does this compound with its infrastructure gaps and seismic zone exposure?"),
        ("Drought Impact", "Analyze drought history for Ozark County, MO (FIPS 29153). How does chronic drought combine with poverty and isolation to create compounding risk?"),
        ("Climate Projection", "Project climate risk for Jackson County, MO (FIPS 29095) under SSP2-4.5 scenario. What does this mean for emergency planning over the next 30 years?"),
    ],
    "💡 Planning": [
        ("Intervention ROI", "What is the most cost-effective intervention for Ozark County, Missouri (FIPS 29153)? Compare all options and explain which addresses the root cause of vulnerability."),
        ("Disaster Simulation", "Simulate a 7.0 earthquake centered on New Madrid County, MO (FIPS 29143). How many people are affected, and which neighboring counties face cascading infrastructure failures?"),
        ("Triage Priority", "If Missouri had $10M for disaster resilience, which 3 counties should receive funding first? Use risk scores, population impact, and infrastructure gaps to justify your recommendation."),
        ("Scenario Comparison", "Compare the impact of a 500-year flood vs an EF4 tornado centered on Boone County, MO (FIPS 29019). Which scenario affects more people and infrastructure?"),
    ],
}

tab_names = list(EXAMPLE_PROMPTS.keys())
tabs = st.tabs(tab_names)
for tab, tab_name in zip(tabs, tab_names):
    with tab:
        prompts = EXAMPLE_PROMPTS[tab_name]
        cols = st.columns(len(prompts))
        for col, (label, query) in zip(cols, prompts):
            with col:
                if st.button(label, key=f"preset_{tab_name}_{label}", use_container_width=True):
                    st.session_state.query_input = query

# Query form (Enter key works)
with st.form("query_form", clear_on_submit=True):
    query_text = st.text_input(
        "Ask ResilienceAI",
        value=st.session_state.get('query_input', ""),
        placeholder="e.g., Which counties have accelerating disaster frequency and no hospital within 50km?"
    )
    submit_q = st.form_submit_button("Analyze", type="primary", use_container_width=True)

# Handle preset button clicks (outside form)
if st.session_state.query_input and not submit_q:
    query_text = st.session_state.query_input
    submit_q = True

# ── Execute Query ─────────────────────────────────────────────────────
should_run = submit_q and query_text
if should_run:
    st.session_state.query_input = ""
    effort = st.session_state.agent_config.get('reasoning_effort', 'Medium')

    if st.session_state.agentic_orchestrator:
        orch = st.session_state.agentic_orchestrator
        # Apply effort settings
        effort_cfg = {"Low": (2, 512), "Medium": (4, 1024), "High": (6, 2048)}
        orch.max_tool_rounds, orch._max_tokens = effort_cfg.get(effort, (2, 1024))

        with st.status(f"Reasoning ({effort.lower()})...", expanded=True) as status:
            st.write("Query sent to LLM...")
            try:
                response = orch.query(query_text, effort=effort)

                for step in response.steps:
                    if step.tool_name:
                        st.write(f"**Step {step.step_num}**: `{step.tool_name}({json.dumps(step.tool_args)})`")
                    if step.reasoning and step.reasoning != "Final synthesis":
                        st.write(f"*{step.reasoning[:200]}*")

                tools_str = ", ".join(response.tools_used) if response.tools_used else "direct"
                status.update(
                    label=f"Done — {len(response.steps)} steps, {len(response.tools_used)} tools ({tools_str}) in {response.execution_time_ms/1000:.1f}s",
                    state="complete"
                )

                st.session_state.last_agent_response = response
                st.session_state.chat_history.append({
                    "query": query_text,
                    "answer": response.answer,
                    "tools": response.tools_used,
                    "time_ms": response.execution_time_ms,
                    "steps": len(response.steps),
                })
            except Exception as e:
                status.update(label=f"Error: {e}", state="error")
    else:
        st.error("Agentic engine not available — check LLM connection in sidebar.")

# ── Display Response ──────────────────────────────────────────────────
if st.session_state.last_agent_response is not None:
    res = st.session_state.last_agent_response
    st.divider()

    if hasattr(res, 'answer'):
        # Agentic response
        col_h, col_stats = st.columns([3, 1])
        with col_h:
            st.markdown("### Intelligence Report")
        with col_stats:
            st.caption(f"{res.execution_time_ms/1000:.1f}s | {len(res.tools_used)} tools | {res.model.split('/')[-1]}")

        st.markdown(res.answer)

        # ── Inline Tool Visualizations ─────────────────────────────
        render_tool_visuals(res.steps)

        # Reasoning trace
        with st.expander(f"Reasoning Trace ({len(res.steps)} steps)", expanded=False):
            for step in res.steps:
                st.markdown(f"**Step {step.step_num}**")
                if step.reasoning:
                    st.markdown(f"> *{step.reasoning[:300]}*")
                if step.tool_name:
                    st.code(f"{step.tool_name}({json.dumps(step.tool_args, indent=2)})", language="json")
                    if step.tool_result:
                        result_str = json.dumps(step.tool_result, default=str, indent=2)
                        if len(result_str) > 1500:
                            result_str = result_str[:1500] + "\n... (truncated)"
                        st.code(result_str, language="json")
                st.divider()

    elif isinstance(res, dict):
        if 'answer' in res:
            st.info(res['answer'])
        if 'data' in res and res['data']:
            try:
                st.dataframe(pd.DataFrame(res['data']), use_container_width=True)
            except Exception:
                st.json(res['data'])

# ── Chat History ──────────────────────────────────────────────────────
if st.session_state.chat_history:
    with st.expander(f"Session History ({len(st.session_state.chat_history)} queries)", expanded=False):
        for i, h in enumerate(reversed(st.session_state.chat_history)):
            idx = len(st.session_state.chat_history) - i
            st.markdown(f"**Q{idx}**: {h['query']}")
            st.caption(f"{h.get('steps', '?')} steps | Tools: {', '.join(h.get('tools', []))} | {h.get('time_ms', 0)/1000:.1f}s")


# ═══════════════════════════════════════════════════════════════════════
# DATA EXPLORER — Collapsible panels below the main interface
# ═══════════════════════════════════════════════════════════════════════

if df is not None:
    st.divider()
    st.markdown("### Data Explorer")
    st.caption("Reference panels — the agentic engine queries this same data via tools.")

    # Get filtered data based on sidebar state picker
    fs = st.session_state.agent_config.get('focus_state', 'All States')
    focus_df = df if fs == "All States" else df[df["county_name"].str.endswith(f", {fs}")]
    state_label = fs if fs != "All States" else "National"

    # ── Panel 1: Vulnerability Map ─────────────────────────────────────
    with st.expander(f"🗺️ Vulnerability Map — {state_label} ({len(focus_df):,} counties)", expanded=False):
        color_by = st.selectbox("Color by", ["risk_score", "vulnerability_index", "poverty_pct", "uninsured_pct"], key="map_color")

        fig = px.scatter_geo(
            focus_df,
            lat="latitude", lon="longitude",
            color=color_by,
            size="total_population",
            hover_name="county_name",
            hover_data={"risk_score": ":.3f", "risk_level": True, "total_population": ":,"},
            color_continuous_scale="RdYlGn_r",
            size_max=15,
        )
        fig.update_geos(
            scope="usa",
            showland=True, landcolor="#1a202c",
            showlakes=True, lakecolor="#2d3748",
            bgcolor="rgba(0,0,0,0)",
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            height=500,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            focus_df.nlargest(15, "risk_score")[["county_name", "risk_score", "risk_level", "total_population", "vulnerability_index"]],
            use_container_width=True, hide_index=True
        )

    # ── Panel 2: Healthcare Infrastructure ─────────────────────────────
    with st.expander(f"🏥 Healthcare Infrastructure — {state_label}", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        zero_red = focus_df[focus_df['zero_redundancy_flag'] == 1] if 'zero_redundancy_flag' in focus_df.columns else pd.DataFrame()
        c1.metric("Zero-Redundancy", f"{len(zero_red):,}")
        c2.metric("Avg Hospital Dist", f"{focus_df['dist_nearest_hospitals_km'].mean():.1f} km")
        c3.metric("Avg EMS Dist", f"{focus_df['dist_nearest_ems_stations_km'].mean():.1f} km")
        c4.metric(">50km to Hospital", f"{len(focus_df[focus_df['dist_nearest_hospitals_km'] > 50]):,}")

        # Density metrics
        density_cols = {
            'density_hospitals_per10k': 'Hospitals/10k',
            'density_ems_stations_per10k': 'EMS/10k',
            'density_fire_stations_per10k': 'Fire/10k',
            'density_nursing_homes_per10k': 'Nursing/10k',
        }
        avail = {k: v for k, v in density_cols.items() if k in focus_df.columns}
        if avail:
            dcols = st.columns(len(avail))
            for col, (dcol, label) in zip(dcols, avail.items()):
                col.metric(label, f"{focus_df[dcol].mean():.2f}")

        col_chart, col_table = st.columns([3, 2])
        with col_chart:
            fig = px.scatter(
                focus_df.nlargest(150, 'dist_nearest_hospitals_km'),
                x="dist_nearest_hospitals_km", y="dist_nearest_ems_stations_km",
                size="total_population", color="risk_level",
                hover_name="county_name",
                color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"},
                title="Infrastructure Deserts"
            )
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Hospital Distance (km)", yaxis_title="EMS Distance (km)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            worst = focus_df.nlargest(10, 'dist_nearest_hospitals_km')[
                ['county_name', 'dist_nearest_hospitals_km', 'count_hospitals_50km', 'risk_level']
            ].copy()
            worst.columns = ['County', 'Hospital km', 'Hosp. in 50km', 'Risk']
            st.dataframe(worst, use_container_width=True, hide_index=True)

    # ── Panel 3: State Risk Profile ────────────────────────────────────
    with st.expander(f"📊 Risk Profile — {state_label}", expanded=False):
        col_chart2, col_table2 = st.columns([3, 2])
        with col_chart2:
            fig = px.scatter(
                focus_df, x="vulnerability_index", y="isolation_index",
                size="total_population", color="risk_score",
                hover_name="county_name",
                color_continuous_scale="RdYlGn_r",
                title="Vulnerability vs Isolation"
            )
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_table2:
            top = focus_df.nlargest(10, "risk_score")[
                ["county_name", "risk_score", "total_population", "poverty_pct", "uninsured_pct"]
            ].copy()
            top.columns = ["County", "Risk", "Population", "Poverty %", "Uninsured %"]
            st.dataframe(top, use_container_width=True, hide_index=True)

        # Disparity bar chart
        if len(focus_df) > 5:
            fig2 = px.bar(
                focus_df.nlargest(15, "uninsured_pct"),
                x="county_name", y="uninsured_pct",
                color="risk_level",
                color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"},
                title=f"Highest Uninsured Rates — {state_label}"
            )
            fig2.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig2, use_container_width=True)

# -- Footer -------------------------------------------------------------
st.divider()
st.caption("ResilienceAI v3.2 | MUIDSI Hackathon 2026 | Gemini + Local LLM Backends | 16 MCP Tools")
