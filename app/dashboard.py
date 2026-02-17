"""
ResilienceAI - Strategic Intelligence Dashboard
Comprehensive agentic platform for national disaster vulnerability and climate resilience.
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
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import streamlit_antd_components as sac

# Try to import internal modules
try:
    from agent import ResilienceAgent, get_mcp_tools
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

try:
    from agents.orchestrator import AgentOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

try:
    from climate_client import ClimateIntelligenceClient
    CLIMATE_AVAILABLE = True
except ImportError:
    CLIMATE_AVAILABLE = False

try:
    from modern_ui import (
        apply_modern_theme, render_modern_header, render_metric_card,
        render_status_indicator, COLORS, render_risk_badge
    )
    MODERN_UI_AVAILABLE = True
except ImportError:
    MODERN_UI_AVAILABLE = False

try:
    from geo_visualizations import render_3d_landscape_tab
    GEO_VIZ_AVAILABLE = True
except ImportError:
    GEO_VIZ_AVAILABLE = False

# -- Page Configuration -------------------------------------------------
st.set_page_config(
    page_title="ResilienceAI | Strategic Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Modern Theme
if MODERN_UI_AVAILABLE:
    apply_modern_theme()

# -- Initialize Session State -------------------------------------------
def init_session_state():
    if 'agent_config' not in st.session_state:
        st.session_state.agent_config = {
            'archia_url': 'https://registry.archia.app/v1',
            'api_key': os.environ.get('ARCHIA_TOKEN', ''),
            'agent_name': 'ResilienceAI',
            'use_local_agent': True
        }
    if 'last_agent_response' not in st.session_state:
        st.session_state.last_agent_response = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'local_agent' not in st.session_state:
        st.session_state.local_agent = None
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'climate_client' not in st.session_state:
        st.session_state.climate_client = None
    if 'query_input' not in st.session_state:
        st.session_state.query_input = ""
    if 'agent_history' not in st.session_state:
        st.session_state.agent_history = []

init_session_state()

# -- Load Data ----------------------------------------------------------
@st.cache_data
def load_data():
    try:
        processed_dir = Path(__file__).parent.parent / "data" / "processed"
        features_path = processed_dir / "county_features.csv"
        if features_path.exists():
            return pd.read_csv(features_path, dtype={"fips": str})
    except Exception as e:
        st.error(f"Data Load Error: {e}")
    return None

@st.cache_data
def load_zip_to_fips():
    """Load ZIP-to-county FIPS mapping."""
    cache_path = Path(__file__).parent.parent / "data" / "cache" / "zip_county_crosswalk.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path, dtype=str)
    return None

def zip_to_fips(zip_code: str, crosswalk=None) -> dict:
    if crosswalk is None: crosswalk = load_zip_to_fips()
    if crosswalk is None: return {"error": "ZIP crosswalk not available"}
    match = crosswalk[crosswalk["zip"] == str(zip_code).zfill(5)]
    if match.empty: return {"error": f"No county found for ZIP {zip_code}"}
    row = match.iloc[0]
    return {"fips": row["fips"], "county_name": row["county_name"], "zip": row["zip"]}

def county_picker(df, key_prefix, label="Find County"):
    search_mode = st.radio(label, ["By Name", "By ZIP Code"], horizontal=True, key=f"{key_prefix}_mode")
    if search_mode == "By ZIP Code":
        zip_input = st.text_input("ZIP Code", max_chars=5, key=f"{key_prefix}_zip", placeholder="e.g. 65201")
        if zip_input and len(zip_input) == 5:
            result = zip_to_fips(zip_input)
            if "error" not in result:
                st.caption(f"Mapped to **{result['county_name']}** (FIPS: {result['fips']})")
                return result["fips"]
            else:
                st.warning(result["error"])
        return None
    else:
        if df is None: return None
        mo_counties = df[df["county_name"].str.endswith(", Missouri")][["county_name", "fips"]].sort_values("county_name")
        if mo_counties.empty: mo_counties = df[["county_name", "fips"]].sort_values("county_name")
        options = dict(zip(mo_counties["county_name"], mo_counties["fips"]))
        default_idx = list(options.keys()).index("Boone, Missouri") if "Boone, Missouri" in options else 0
        selected = st.selectbox("County", list(options.keys()), index=default_idx, key=f"{key_prefix}_name")
        return options[selected]

df = load_data()
if df is not None:
    st.session_state.df = df
    if AGENT_AVAILABLE and st.session_state.local_agent is None:
        st.session_state.local_agent = ResilienceAgent()
    if ORCHESTRATOR_AVAILABLE and st.session_state.orchestrator is None:
        st.session_state.orchestrator = AgentOrchestrator()
    if CLIMATE_AVAILABLE and st.session_state.climate_client is None:
        st.session_state.climate_client = ClimateIntelligenceClient()

# -- Sidebar ------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ ResilienceAI")
    st.caption("Strategic Intelligence for Disaster Resilience")
    st.divider()
    
    if st.session_state.df is not None:
        st.success(f"📡 System Ready: {len(st.session_state.df):,} zones indexed")
    else:
        st.error("🚨 System Offline")
    
    st.divider()
    st.markdown("### 🤖 Intelligence Config")
    st.session_state.agent_config['use_local_agent'] = not st.toggle("Archia Cloud Mode", value=False)
    
    if not st.session_state.agent_config['use_local_agent']:
        st.session_state.agent_config['api_key'] = st.text_input("Archia Token", value=st.session_state.agent_config.get('api_key', ''), type="password")
        st.session_state.agent_config['agent_name'] = st.text_input("Agent Name", value=st.session_state.agent_config.get('agent_name', 'ResilienceAI'))
    else:
        st.info("Local Edge Node (Deterministic Intent Routing)")
    
    st.divider()
    st.caption("MUIDSI Hackathon 2026 Submission")

# -- Header -------------------------------------------------------------
render_modern_header("RESILIENCE AI", "Predictive Vulnerability Intelligence & Climate Analytics")

# -- Tabs ---------------------------------------------------------------
tabs = st.tabs([
    "🧠 Strategic Intelligence",
    "📍 Missouri Command",
    "🌍 Resilience Map",
    "🌪️ Scenario Simulator",
    "📈 Predictive Insights",
    "🌾 Agricultural Risk",
    "🚨 Emergency Ops",
    "📋 Strategic Roadmap",
    "📡 Live Feed"
])

tab_intel, tab_mo, tab_map, tab_sim, tab_pred, tab_ag, tab_ops, tab_road, tab_live = tabs

# -- Tab 1: Strategic Intelligence --------------------------------------
with tab_intel:
    st.subheader("🧠 Agentic Workflow Engine")
    st.markdown("Query the multi-domain resilience database using natural language.")
    
    col_pre1, col_pre2, col_pre3, col_pre4 = st.columns(4)
    with col_pre1:
        if st.button("🌾 Ag Risk Assessment", use_container_width=True): st.session_state.query_input = "Show me agricultural vulnerability for the Midwest"
    with col_pre2:
        if st.button("🏥 Redundancy Audit", use_container_width=True): st.session_state.query_input = "Which counties have zero hospital redundancy nationwide?"
    with col_pre3:
        if st.button("📈 Trend Analysis", use_container_width=True): st.session_state.query_input = "Where are disasters accelerating most significantly?"
    with col_pre4:
        if st.button("📋 ROI Comparison", use_container_width=True): st.session_state.query_input = "What is the best resilience investment for St. Louis, MO?"

    query_text = st.text_input("Strategic Request", value=st.session_state.get('query_input', ""), placeholder="e.g., Identify counties where increasing flood risk intersects with high poverty.")
    
    col_q1, col_q2 = st.columns([1, 4])
    with col_q1: submit_q = st.button("🚀 Execute", type="primary", use_container_width=True)
    
    if (submit_q or (st.session_state.query_input and st.session_state.query_input != "")) and query_text:
        st.session_state.query_input = ""
        with st.spinner("Orchestrating agent workflow..."):
            try:
                from archia_client import ArchiaClient, ArchiaConfig
                cfg = ArchiaConfig(base_url=st.session_state.agent_config['archia_url'], api_key=st.session_state.agent_config['api_key'])
                client = ArchiaClient(config=cfg)
                agent_name = st.session_state.agent_config.get('agent_name', 'ResilienceAI')
                response = client.query(query_text, agent_name=agent_name)
                st.session_state.last_agent_response = response
            except Exception as e: st.error(f"Intelligence Error: {e}")

    if 'last_agent_response' in st.session_state and st.session_state.last_agent_response:
        res = st.session_state.last_agent_response
        st.divider()
        with st.container():
            col_res_header, col_mode = st.columns([4, 1])
            with col_res_header: st.markdown("### 📤 Intelligence Response")
            with col_mode: st.markdown(f'<span class="status-badge status-online">{res.get("mode", "Edge")}</span>', unsafe_allow_html=True)
            if 'thought' in res:
                with st.expander("👁️ Reasoning & Strategy", expanded=True): st.markdown(f"*{res['thought']}*")
            if 'plan' in res:
                st.markdown("**📝 Strategic Execution Plan:**")
                for step in res['plan']: st.markdown(f"> {step}")
            if 'answer' in res: st.info(res['answer'])
            if 'data' in res and res['data']:
                with st.expander("📊 Extracted Data", expanded=True):
                    data_df = pd.DataFrame(res['data'])
                    st.dataframe(data_df, use_container_width=True)

# -- Tab 2: Missouri Command Center -------------------------------------
with tab_mo:
    if df is not None:
        mo_df = df[df["county_name"].str.endswith(", Missouri")].copy()
        if not mo_df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("MO Risk Index", f"{mo_df['risk_score'].mean():.3f}")
            c2.metric("High-Risk Zones", len(mo_df[mo_df['risk_level'] == 'High']))
            c3.metric("Avg Uninsured %", f"{mo_df['uninsured_pct'].mean():.1f}%")
            c4.metric("Avg Poverty %", f"{mo_df['poverty_pct'].mean():.1f}%")
            st.divider()
            col_m1, col_m2 = st.columns([3, 2])
            with col_m1:
                fig = px.scatter(mo_df, x="vulnerability_index", y="isolation_index", size="total_population", color="risk_score", hover_name="county_name", color_continuous_scale="RdYlGn_r")
                fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            with col_m2:
                st.dataframe(mo_df.nlargest(10, "risk_score")[["county_name", "risk_score", "risk_level"]], use_container_width=True)

# -- Tab 3: Resilience Map ----------------------------------------------
with tab_map:
    st.subheader("🗺️ National Geospatial Vulnerability")
    if df is not None and GEO_VIZ_AVAILABLE: render_3d_landscape_tab(df)
    else: st.info("Geospatial engine standby.")

# -- Tab 4: Scenario Simulator ------------------------------------------
with tab_sim:
    st.subheader("🌪️ Disaster Impact Simulation")
    if df is not None:
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            from scenario_simulator import SCENARIO_PRESETS
            scen_options = {v['label']: k for k, v in SCENARIO_PRESETS.items()}
            sel_label = st.selectbox("Scenario Type", list(scen_options.keys()))
            epic_fips = county_picker(df, "sim", "Epicenter")
            run_sim = st.button("🚀 Run Impact Analysis")
        with col_s2:
            if run_sim and epic_fips:
                from scenario_simulator import ScenarioSimulator
                sim = ScenarioSimulator(df)
                result = sim.simulate(scen_options[sel_label], epicenter_fips=epic_fips)
                if 'summary' in result:
                    s = result['summary']
                    st.markdown(f"### Impact: {s['scenario']}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Pop. at Risk", f"{s['total_population_at_risk']:,}")
                    c2.metric("Zones Affected", str(s['counties_affected']))
                    c3.metric("Risk Escalation", f"+{s['risk_increase_pct']:.1f}%")
                    st.table(pd.DataFrame(result['top_affected_counties'])[['county_name', 'risk_score_after', 'infrastructure_damage_pct']].head(10))

# -- Tab 5: Predictive Insights -----------------------------------------
with tab_pred:
    st.subheader("📈 Future Risk Trajectories")
    if df is not None:
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            p_fips = county_picker(df, "pred", "Target")
            scen_p = st.selectbox("Emissions Pathway", ["Sustainable (SSP1)", "Middle (SSP2)", "High (SSP5)"])
            run_p = st.button("📈 Predict 10yr Risk")
        with col_p2:
            if run_p and p_fips:
                with st.spinner("Prophet inference running..."):
                    s_key = "ssp2_45" if "SSP2" in scen_p else "ssp1_19" if "SSP1" in scen_p else "ssp5_85"
                    res = st.session_state.local_agent.analyze_risk_trajectory(p_fips, climate_scenario=s_key)
                    if 'climate_projection' in res:
                        cp = res['climate_projection']
                        st.metric("Projected 2035 Risk", f"{cp['final_risk_score']:.3f}", delta=f"+{cp['risk_increase_pct']:.1f}%")
                        st.markdown("#### Strategic Actions")
                        for r in res['recommendations']: st.write(f"- {r['action']} ({r['priority']})")

# -- Tab 6: Agricultural Risk -------------------------------------------
with tab_ag:
    st.subheader("🌾 National Food Security")
    if df is not None:
        col_ag1, col_ag2 = st.columns([1, 2])
        with col_ag1:
            st_pick = st.selectbox("Focus State", ["MO", "IA", "IL", "KS", "NE"])
            if st.button("Analyze State Ag-Resilience"):
                st.session_state.last_ag = st.session_state.local_agent.get_state_crop_summary(st_pick)
        with col_ag2:
            if 'last_ag' in st.session_state:
                ag = st.session_state.last_ag
                for c, m in ag['crops'].items(): st.metric(c, f"{m['average_yield_bu_per_acre']} BU/AC")

# -- Tab 7: Emergency Ops -----------------------------------------------
with tab_ops:
    st.subheader("🚨 Emergency Command Center")
    c_ops1, c_ops2 = st.columns([1, 2])
    with c_ops1:
        st.markdown("### 🔔 Active Subscriptions")
        subs = st.session_state.local_agent.list_alert_subscriptions()
        if subs['count'] > 0:
            for s in subs['subscriptions']: st.success(f"Monitoring: {s['county_name']}")
        else: st.caption("No active alerts.")
    with c_ops2:
        st.markdown("### 📺 Intelligence Feed")
        alerts = st.session_state.local_agent.get_active_alerts()
        if alerts['count'] > 0:
            for a in alerts['alerts']: st.warning(f"{a['severity'].upper()}: {a['message']}")
        else: st.info("No active emergency events.")

# -- Tab 8: Strategic Roadmap -------------------------------------------
with tab_road:
    st.subheader("📋 Policy & Optimization Roadmap")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("#### 🏥 Healthcare Expansion Targets")
        if df is not None:
            crit = df[(df['total_population'] > 100000) & (df['zero_redundancy_flag'] == 1)]
            st.dataframe(crit[['county_name', 'total_population', 'risk_score']], use_container_width=True)
    with col_r2:
        st.markdown("#### ⚡ Infrastructure Hardening Priority")
        if df is not None:
            accel = df[(df['disaster_acceleration'] > 2.0) & (df['risk_level'] == 'High')]
            st.dataframe(accel[['county_name', 'disaster_acceleration', 'risk_score']], use_container_width=True)

# -- Tab 9: Live Feed ---------------------------------------------------
with tab_live:
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        try:
            from realtime_pipeline import render_realtime_feed
            render_realtime_feed()
        except: st.info("NOAA/USGS stream initializing...")
    with col_l2:
        st.subheader("📊 Activity Log")
        try:
            from dashboard_monitor import render_activity_dashboard
            render_activity_dashboard()
        except: st.caption("Activity recording standby.")

# -- Footer -------------------------------------------------------------
st.divider()
st.caption("ResilienceAI Strategic Command | v3.0 Production Edition | Powered by Archia Cloud")
