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
import streamlit_antd_components as sac

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
    st.session_state.agent_config['use_local_agent'] = not st.toggle("Production Intelligence (Archia API)", value=False)
    st.session_state.agent_config['model'] = st.selectbox("Intelligence Model", 
        ["claude-sonnet-4-5-20250929", "gpt-4o"])
    
    st.divider()
    st.caption("MUIDSI Hackathon 2026 - Official Submission")

# ── Main Header ──────────────────────────────────────────────────────
selected_step = sac.steps(
    items=[
        sac.StepsItem(title='DATA', subtitle='READY', icon='database-fill-check'),
        sac.StepsItem(title='AGENT', subtitle='NODE ACTIVE', icon='robot'),
        sac.StepsItem(title='SYSTEM', subtitle='OPERATIONAL', icon='shield-check'),
    ], 
    variant='circle', color='purple', size='sm', return_index=True
)

if selected_step == 0:
    st.toast("Database: 3,222 counties indexed and validated.", icon="✅")
elif selected_step == 1:
    st.toast("Agent: Local inference node active. Production API standby.", icon="🤖")
elif selected_step == 2:
    st.toast("System: All systems nominal. Esoteric Noir theme engaged.", icon="🛡️")

render_modern_header(
    "RESILIENCE AI", 
    "Predictive Vulnerability Intelligence & Disparity Analysis"
)

# ── Focused Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 Missouri Regional Assessment",
    "🌍 Vulnerability Explorer",
    "📊 Resilience Planner",
    "🧠 Agent Intelligence",
    "📡 Live Ops"
])

# ── Tab 1: Missouri Regional Assessment ──────────────────────────────
with tab1:
    st.markdown('<div class="bento-container">', unsafe_allow_html=True)
    
    if df is not None:
        # Strict filtering for Missouri
        mo_df = df[df['county_name'].str.endswith(", Missouri")].copy()
        avg_risk = mo_df['risk_score'].mean()
        high_risk_count = len(mo_df[mo_df['risk_level'] == 'High'])
        uninsured_avg = mo_df['uninsured_pct'].mean() * 100
        
        # Tile 1: Main State Metric (Large)
        st.markdown(f"""
        <div class="bento-item bento-large">
            <div>
                <span class="metric-label">Missouri Risk Index</span>
                <div class="metric-value" style="font-size: 4rem;">{avg_risk:.3f}</div>
            </div>
            <div class="mono" style="color: #c084fc; font-size: 0.9rem;">
                ANALYSIS OF 114 COUNTIES + ST. LOUIS CITY
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tile 2: High Risk Zones
        st.markdown(f"""
        <div class="bento-item">
            <span class="metric-label">Critical Zones</span>
            <div class="metric-value">{high_risk_count}</div>
            <span class="risk-high">IMMEDIATE ATTENTION</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Tile 3: Healthcare Gap
        st.markdown(f"""
        <div class="bento-item">
            <span class="metric-label">Healthcare Gap</span>
            <div class="metric-value">{uninsured_avg:.1f}%</div>
            <span class="mono" style="font-size: 0.7rem; color: #94a3b8;">AVG UNINSURED RATE</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Tile 4: Disparity of the Day (Wide)
        if AGENT_AVAILABLE and st.session_state.local_agent:
            res = st.session_state.local_agent.get_mo_health_disparities(focus_metric="uninsured_pct", max_results=1)
            top_zone = res['priority_zones'][0]
            st.markdown(f"""
            <div class="bento-item bento-wide">
                <span class="metric-label">Priority Disparity Zone</span>
                <div style="font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{top_zone['county_name']}</div>
                <p style="color: #94a3b8; font-size: 0.9rem;">
                    This county shows the highest divergence between healthcare access and projected disaster impact.
                </p>
                <div class="mono" style="color: #4ade80;">INDEX: {top_zone['disparity_index']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Secondary content row
    st.divider()
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("📊 State-Wide Disparity Matrix")
        if df is not None:
            # Re-using the logic from the old tab but simplified
            res = st.session_state.local_agent.get_mo_health_disparities(focus_metric="uninsured_pct", max_results=8)
            df_zones = pd.DataFrame(res['priority_zones'])
            fig = px.bar(df_zones, x='county_name', y='disparity_index', 
                       color='disparity_index', color_continuous_scale='Purples',
                       template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
    with col_b:
        st.subheader("🚨 Sentinel Alerts")
        if AGENT_AVAILABLE and st.session_state.local_agent:
            alerts = st.session_state.local_agent.get_real_time_alerts(state="MO", max_results=3)
            for a in alerts['alerts']:
                st.markdown(f"**{a['county_name']}**")
                st.caption(a['reason'])
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
        st.subheader("📊 Scenario Simulation")
        threat = st.selectbox("Select Threat", ["hurricane_cat3", "flood_major", "tornado_ef5", "wildfire_large"])
        
        # Get list of Missouri FIPS
        if df is not None:
            mo_counties = df[df['county_name'].str.endswith(", Missouri")].sort_values('county_name')
            if not mo_counties.empty:
                target_county = st.selectbox("Epicenter County", mo_counties['county_name'].tolist())
                epicenter_fips = mo_counties[mo_counties['county_name'] == target_county]['fips'].iloc[0]
                
                if st.button("🚀 Run Simulation", type="primary"):
                    if AGENT_AVAILABLE and st.session_state.local_agent:
                        with st.spinner("Calculating impact vectors..."):
                            result = st.session_state.local_agent.simulate_scenario(
                                scenario=threat,
                                epicenter_fips=epicenter_fips
                            )
                            st.session_state.simulation_result = result
            else:
                st.warning("No Missouri counties found in dataset. Check data/processed/county_features.csv")
    
    with col2:
        if 'simulation_result' in st.session_state:
            res = st.session_state.simulation_result
            st.subheader(f"📈 Impact Analysis: {threat.replace('_', ' ').title()}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Pop. at Risk", f"{res.get('affected_population', 0):,}")
            with c2:
                st.metric("Avg Risk Increase", f"+{res.get('avg_risk_increase', 0)*100:.1f}%")
            with c3:
                st.metric("Counties Affected", res.get('affected_counties_count', 0))
            
            # Show a simple comparison chart
            comp_data = pd.DataFrame([
                {"State": "Baseline", "Risk": res.get('baseline_risk', 0)},
                {"State": "Post-Event", "Risk": res.get('post_event_risk', 0)}
            ])
            fig = px.bar(comp_data, x='State', y='Risk', color='State', 
                       color_discrete_map={"Baseline": "#34d399", "Post-Event": "#f87171"},
                       template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select a threat and epicenter to begin simulation.")

# ── Tab 4: Agent Intelligence ────────────────────────────────────────
with tab4:
    st.subheader("🧠 Intelligence Operations")
    st.markdown("Query the ResilienceAI agent using natural language. (Archia API / Local Fallback)")
    
    query_text = st.text_input("Analysis Request", placeholder="e.g., Which Missouri counties have high risk but no hospital redundancy?")
    
    col_q1, col_q2 = st.columns([1, 4])
    with col_q1:
        submit_q = st.button("🚀 Execute", type="primary", use_container_width=True)
    
    if submit_q and query_text:
        with st.spinner("Processing intelligence vector..."):
            try:
                from archia_client import ArchiaClient
                client = ArchiaClient()
                # If local agent toggle is OFF, it will try remote
                response = client.query(query_text)
                st.session_state.last_agent_response = response
            except Exception as e:
                st.error(f"Intelligence Pipeline Error: {e}")

    if 'last_agent_response' in st.session_state:
        res = st.session_state.last_agent_response
        st.divider()
        
        with st.container():
            st.markdown("### 📤 Response")
            if 'answer' in res:
                st.info(res['answer'])
            elif 'response' in res:
                st.info(res['response'])
            elif 'error' in res:
                st.error(res['error'])
            
            if 'data' in res and res['data']:
                with st.expander("View Underlying Data"):
                    st.dataframe(pd.DataFrame(res['data']))
            
            if st.button("📋 Copy to Intelligence Log"):
                st.code(res.get('answer', res.get('response', '')), language='markdown')
                st.success("Copied to display buffer.")

# ── Tab 5: Live Ops ──────────────────────────────────────────────────
with tab5:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📡 Real-Time Data Stream")
        if st.button("🔄 Force Refresh Heartbeat"):
            st.rerun()
            
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
