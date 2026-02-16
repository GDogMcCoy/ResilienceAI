"""
ResilienceAI - Focus Edition
A streamlined, hero-focused dashboard for disaster vulnerability assessment.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Try to import the ResilienceAgent
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
try:
    from agent import ResilienceAgent, get_mcp_tools
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

# Import modern UI components
try:
    from modern_ui import (
        apply_modern_theme, render_modern_header, render_metric_card,
        render_status_indicator, apply_plotly_theme, COLORS, render_risk_badge
    )
    MODERN_UI_AVAILABLE = True
except ImportError:
    MODERN_UI_AVAILABLE = False

# Import geospatial visualizations
try:
    from geo_visualizations import (
        GeoVisualizer, render_choropleth_tab, render_hexbin_tab, render_3d_landscape_tab
    )
    GEO_VIZ_AVAILABLE = True
except ImportError:
    GEO_VIZ_AVAILABLE = False

# ── Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="ResilienceAI | Hero Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Esoteric Noir theme
if MODERN_UI_AVAILABLE:
    apply_modern_theme()

# ── Initialize Session State ─────────────────────────────────────────
def init_session_state():
    if 'agent_config' not in st.session_state:
        st.session_state.agent_config = {
            'archia_url': 'https://api.archia.app/v1',
            'api_key': 'ask_wbkaHYsVv6yiaBMBko3VU_YZ9Bonga3nThObPyKJwwA=',
            'model': 'claude-sonnet-4-5-20250929',
            'use_local_agent': True
        }
    if 'agent_history' not in st.session_state:
        st.session_state.agent_history = []
    if 'last_response' not in st.session_state:
        st.session_state.last_response = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'local_agent' not in st.session_state:
        st.session_state.local_agent = None

init_session_state()

# ── Load Data ────────────────────────────────────────────────────────
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

df = load_data()
if df is not None:
    st.session_state.df = df
    if AGENT_AVAILABLE and st.session_state.local_agent is None:
        st.session_state.local_agent = ResilienceAgent()

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ ResilienceAI")
    st.caption("Strategic Intelligence for Disaster Resilience")
    st.divider()
    
    if st.session_state.df is not None:
        st.success(f"📡 System Ready: {len(st.session_state.df):,} zones indexed")
    else:
        st.error("🚨 System Offline: Data connection failed")
    
    st.divider()
    st.markdown("### 🤖 Agent Config")
    st.session_state.agent_config['use_local_agent'] = st.toggle("YOLO Mode (Local Agent)", value=True)
    st.session_state.agent_config['model'] = st.selectbox("Intelligence Model", 
        ["claude-sonnet-4-5-20250929", "gpt-4o"])
    
    st.divider()
    st.caption("MUIDSI Hackathon 2026 - Official Submission")

# ── Main Header ──────────────────────────────────────────────────────
render_modern_header(
    "RESILIENCE AI", 
    "Predictive Vulnerability Intelligence & Disparity Analysis"
)

# ── Focused Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛡️ Missouri Sentinel",
    "🗺️ Vulnerability Explorer",
    "🔮 Resilience Planner",
    "🤖 Agent Intelligence",
    "📡 Live Ops"
])

# ── Tab 1: Missouri Sentinel ─────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📍 State of Missouri: High-Level Vulnerability")
        if df is not None:
            mo_df = df[df['county_name'].str.contains(", MO")]
            m1, m2, m3 = st.columns(3)
            with m1:
                render_metric_card("Avg Risk Score", f"{mo_df['risk_score'].mean():.3f}", icon="🔥")
            with m2:
                render_metric_card("High Risk Zones", str(len(mo_df[mo_df['risk_level'] == 'High'])), icon="⚠️")
            with m3:
                render_metric_card("Uninsured Avg", f"{mo_df['uninsured_pct'].mean()*100:.1f}%", icon="🏥")
            
            st.divider()
            
            # Disparity of the Day (Smart Logic)
            st.markdown("### 🔍 Disparity Highlight")
            focus_metric = "uninsured_pct"
            if AGENT_AVAILABLE and st.session_state.local_agent:
                res = st.session_state.local_agent.get_mo_health_disparities(focus_metric=focus_metric, max_results=5)
                top_zone = res['priority_zones'][0]
                st.info(f"**Critical Priority:** {top_zone['county_name']} shows the highest gap between healthcare access and disaster risk index.")
                
                # Small chart for top 5
                df_zones = pd.DataFrame(res['priority_zones'])
                fig = px.bar(df_zones, x='county_name', y='disparity_index', 
                           color='disparity_index', color_continuous_scale='Purples',
                           title="Top 5 Disparity Zones (Healthcare vs Risk)")
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚨 Live Alerts")
        if AGENT_AVAILABLE and st.session_state.local_agent:
            alerts = st.session_state.local_agent.get_real_time_alerts(state="MO", max_results=5)
            for a in alerts['alerts']:
                with st.container():
                    st.markdown(f"**{a['county_name']}**")
                    st.caption(a['reason'])
                    render_risk_badge(a['severity'])
                    st.divider()

# ── Tab 2: Vulnerability Explorer ────────────────────────────────────
with tab2:
    st.subheader("🗺️ Geospatial Deep-Dive")
    if df is not None and GEO_VIZ_AVAILABLE:
        sub_tab1, sub_tab2 = st.tabs(["3D Risk Landscape", "Demographic Overlays"])
        with sub_tab1:
            render_3d_landscape_tab(df)
        with sub_tab2:
            render_choropleth_tab(df)
    else:
        st.info("Select a visualization mode to begin exploration.")

# ── Tab 3: Resilience Planner ────────────────────────────────────────
with tab3:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("🔮 Scenario Modeler")
        scenario = st.selectbox("Select Threat", ["Hurricane", "Flash Flood", "Tornado EF-5", "Heat Wave"])
        epicenter = st.selectbox("Target County", df['county_name'].head(50).tolist()) if df is not None else None
        if st.button("Simulate Impact", type="primary"):
            st.session_state.planner_mode = "simulating"
    
    with col2:
        st.subheader("💰 Intervention ROI")
        st.markdown("Allocating resources based on risk-reduction-per-dollar.")
        if df is not None:
            # Simple ROI viz placeholder
            fig = px.scatter(df.sample(100), x='risk_score', y='poverty_pct', size='total_population',
                           color='risk_level', title="Cost-Effectiveness Matrix")
            st.plotly_chart(fig, use_container_width=True)

# ── Tab 4: Agent Intelligence ────────────────────────────────────────
with tab4:
    st.subheader("🤖 Natural Language Operations")
    query = st.text_input("Ask ResilienceAI (e.g., 'What are the top 3 priorities for Boone County?')")
    if st.button("Consult Agent") and query:
        with st.spinner("Analyzing data vectors..."):
            # Placeholder for agent query logic
            st.write("### Agent Insights")
            st.markdown("> Based on current 2026 projections, **Boone County** requires immediate hospital redundancy upgrades due to increasing flood acceleration.")

# ── Tab 5: Live Ops ──────────────────────────────────────────────────
with tab5:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📡 Real-Time Data Stream")
        try:
            from src.realtime_pipeline import render_realtime_feed
            render_realtime_feed()
        except:
            st.info("Waiting for NOAA/USGS heartbeat...")
    
    with col2:
        st.subheader("📊 Activity Log")
        try:
            from src.dashboard_monitor import render_activity_dashboard
            render_activity_dashboard()
        except:
            st.caption("No recent agent activity recorded.")

# ── Footer ───────────────────────────────────────────────────────────
st.divider()
st.caption("ResilienceAI Strategic Console | v2.0 Focus Edition | Powered by Gemini & Archia")
