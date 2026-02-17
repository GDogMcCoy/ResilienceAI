"""
ResilienceAI - Agentic Intelligence Platform
Chat-first interface backed by 11 real-data tools, LLM reasoning, and 3,222 US counties.
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
import plotly.express as px
import plotly.graph_objects as go

# Try to import internal modules
try:
    from agent import ResilienceAgent, get_mcp_tools, _filter_by_state
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

try:
    from agentic_orchestrator import AgenticOrchestrator
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
            'use_agentic': True,
            'lm_key': os.environ.get("LM_STUDIO_API_KEY", "sk-lm-17g8iJ72:Jkqk55kdkSVRwtUfklSj"),
            'lm_url': 'http://localhost:1234',
            'reasoning_effort': 'Medium',
            'focus_state': 'Missouri',
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

    # Engine settings
    engine_mode = st.radio(
        "Engine",
        ["Agentic AI", "Deterministic"],
        index=0,
        horizontal=True,
    )
    use_agentic = engine_mode == "Agentic AI"
    st.session_state.agent_config['use_agentic'] = use_agentic

    if use_agentic:
        with st.expander("LM Studio", expanded=False):
            lm_url = st.text_input("URL", value=st.session_state.agent_config['lm_url'])
            lm_key = st.text_input("Key", value=st.session_state.agent_config['lm_key'], type="password")
            st.session_state.agent_config['lm_key'] = lm_key
            st.session_state.agent_config['lm_url'] = lm_url

        # Initialize orchestrator
        if st.session_state.agentic_orchestrator is None and AGENTIC_AVAILABLE:
            try:
                st.session_state.agentic_orchestrator = AgenticOrchestrator(
                    lm_studio_url=st.session_state.agent_config['lm_url'],
                    api_key=st.session_state.agent_config['lm_key'],
                )
            except Exception:
                pass

        if st.session_state.agentic_orchestrator:
            info = st.session_state.agentic_orchestrator.get_agent_info()
            st.success(f"{info['model'].split('/')[-1]} | {info['tools']} tools | {info['counties_loaded']:,} counties")
        else:
            st.warning("LLM unavailable")

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
    st.caption("MUIDSI Hackathon 2026 | v3.0")


# ═══════════════════════════════════════════════════════════════════════
# MAIN — Agentic Intelligence Interface
# ═══════════════════════════════════════════════════════════════════════

st.markdown("## ResilienceAI")
st.caption("Ask anything about disaster vulnerability, healthcare infrastructure, climate trends, or intervention planning across 3,222 US counties.")

# Preset query buttons — two rows for more options
row1 = st.columns(4)
presets = [
    ("🔍 Vulnerable Counties", "What are the top 5 most vulnerable counties in Missouri and why?"),
    ("🏥 Healthcare Deserts", "Which Missouri counties are healthcare deserts with the worst hospital and EMS density? Show me the numbers."),
    ("🌡️ Climate Risk", "What are the climate trends and hazard risks for Boone County, MO (FIPS 29019)?"),
    ("💰 Intervention ROI", "What is the most cost-effective intervention for Ozark County, Missouri (FIPS 29153)?"),
]
for col, (label, query) in zip(row1, presets):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state.query_input = query

row2 = st.columns(4)
presets2 = [
    ("🌪️ Simulate Disaster", "Simulate a Category 3 hurricane hitting New Madrid County, MO (FIPS 29143). What's the cascading impact?"),
    ("📊 Compare Counties", "Compare disaster risk, poverty, and infrastructure between Boone County and Jackson County in Missouri."),
    ("🗺️ Risk Contagion", "Analyze risk contagion for St. Louis County, MO (FIPS 29189) — how do its neighbors affect its vulnerability?"),
    ("⚕️ Health Disparities", "What are the worst health disparity zones in Missouri based on uninsured rates?"),
]
for col, (label, query) in zip(row2, presets2):
    with col:
        if st.button(label, use_container_width=True):
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
    use_agentic = st.session_state.agent_config.get('use_agentic', True)
    effort = st.session_state.agent_config.get('reasoning_effort', 'Medium')

    if use_agentic and st.session_state.agentic_orchestrator:
        orch = st.session_state.agentic_orchestrator
        # Apply effort settings
        effort_cfg = {"Low": (1, 512), "Medium": (2, 1024), "High": (3, 1024)}
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

    elif st.session_state.local_agent:
        with st.spinner("Running deterministic analysis..."):
            try:
                result = st.session_state.local_agent.query(query_text)
                st.session_state.last_agent_response = result
            except Exception as e:
                st.error(f"Query failed: {e}")

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
st.caption("ResilienceAI v3.0 | MUIDSI Hackathon 2026 | GPT-OSS 20B Agentic Framework | 11 MCP Tools")
