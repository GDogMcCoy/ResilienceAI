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

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import plotly.express as px
import plotly.graph_objects as go
import requests as _requests

# ── Constants ─────────────────────────────────────────────────────────
EXCLUDED_STATE_FIPS = {"02", "15"}  # Alaska/Hawaii skew continental views

STATE_CENTERS = {
    "01": {"lat": 32.8, "lon": -86.8},  "04": {"lat": 34.3, "lon": -111.7},
    "05": {"lat": 34.8, "lon": -92.4},  "06": {"lat": 37.2, "lon": -119.5},
    "08": {"lat": 39.0, "lon": -105.5}, "09": {"lat": 41.6, "lon": -72.7},
    "10": {"lat": 39.0, "lon": -75.5},  "11": {"lat": 38.9, "lon": -77.0},
    "12": {"lat": 28.6, "lon": -82.4},  "13": {"lat": 32.7, "lon": -83.4},
    "16": {"lat": 44.4, "lon": -114.6}, "17": {"lat": 40.0, "lon": -89.2},
    "18": {"lat": 39.9, "lon": -86.3},  "19": {"lat": 42.0, "lon": -93.5},
    "20": {"lat": 38.5, "lon": -98.3},  "21": {"lat": 37.8, "lon": -85.3},
    "22": {"lat": 31.0, "lon": -92.0},  "23": {"lat": 45.4, "lon": -69.2},
    "24": {"lat": 39.0, "lon": -76.7},  "25": {"lat": 42.2, "lon": -71.8},
    "26": {"lat": 44.3, "lon": -84.6},  "27": {"lat": 46.3, "lon": -94.3},
    "28": {"lat": 32.7, "lon": -89.7},  "29": {"lat": 38.4, "lon": -92.5},
    "30": {"lat": 47.1, "lon": -109.6}, "31": {"lat": 41.5, "lon": -99.8},
    "32": {"lat": 39.4, "lon": -116.6}, "33": {"lat": 43.7, "lon": -71.6},
    "34": {"lat": 40.1, "lon": -74.7},  "35": {"lat": 34.4, "lon": -106.1},
    "36": {"lat": 42.9, "lon": -75.5},  "37": {"lat": 35.6, "lon": -79.8},
    "38": {"lat": 47.4, "lon": -100.5}, "39": {"lat": 40.4, "lon": -82.8},
    "40": {"lat": 35.6, "lon": -97.5},  "41": {"lat": 44.0, "lon": -120.5},
    "42": {"lat": 41.0, "lon": -77.6},  "44": {"lat": 41.7, "lon": -71.5},
    "45": {"lat": 33.9, "lon": -80.9},  "46": {"lat": 44.4, "lon": -100.2},
    "47": {"lat": 35.9, "lon": -86.4},  "48": {"lat": 31.5, "lon": -99.3},
    "49": {"lat": 39.3, "lon": -111.7}, "50": {"lat": 44.1, "lon": -72.6},
    "51": {"lat": 37.5, "lon": -79.0},  "53": {"lat": 47.4, "lon": -120.5},
    "54": {"lat": 38.6, "lon": -80.6},  "55": {"lat": 44.6, "lon": -89.7},
    "56": {"lat": 43.0, "lon": -107.6},
}

# Map tool names to their primary color metric for choropleth
TOOL_COLOR_MAP = {
    "query_counties": "risk_score",
    "get_state_rankings": "risk_score",
    "get_mo_health_disparities": "poverty_pct",
    "get_hazard_risk_profile": "risk_score",
    "get_climate_trends": "risk_score",
    "calculate_pop_weighted_impact": "risk_score",
    "get_county_detail": "risk_score",
    "get_infrastructure_density": "risk_score",
    "analyze_risk_contagion": "risk_score",
    "simulate_scenario": "risk_score",
}

# ── GeoJSON Cache ─────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading county boundaries...")
def load_counties_geojson():
    """Load US county boundaries GeoJSON (cached per session, ~17MB one-time download)."""
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    resp = _requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

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
    .metric-row { padding: 10px 0; }
</style>
""", unsafe_allow_html=True)

# -- Initialize Session State -------------------------------------------
def init_session_state():
    defaults = {
        'agent_config': {
            'lm_key': os.environ.get("LM_STUDIO_API_KEY", ""),
            'gemini_key': os.environ.get("GEMINI_API_KEY", ""),
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
# HELPERS — Continental filter + 3-D dot-matrix builder
# ═══════════════════════════════════════════════════════════════════════

def _filter_continental(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop Alaska / Hawaii rows so maps stay on the continental US."""
    if "fips" in frame.columns:
        return frame[~frame["fips"].str[:2].isin(EXCLUDED_STATE_FIPS)].copy()
    return frame


def render_3d_dot_matrix(
    county_df: pd.DataFrame,
    highlighted_fips: set,
    color_col: str = "risk_score",
    title: str = "County Risk Landscape",
):
    """
    3-D interactive dot matrix — draggable, rotatable, scroll-zoomable.
    X = longitude, Y = latitude, Z = metric value.
    Dot size = population. Color = heatmap on metric.
    """
    plot_df = _filter_continental(county_df).dropna(subset=["latitude", "longitude"]).copy()
    if color_col not in plot_df.columns:
        color_col = "risk_score"
    plot_df = plot_df.dropna(subset=[color_col])
    if plot_df.empty:
        return

    # Population → dot size (clamped 3–22)
    if "total_population" in plot_df.columns:
        pop = plot_df["total_population"].fillna(1000)
        q95 = pop.quantile(0.95)
        plot_df["_sz"] = np.clip(pop / (q95 if q95 > 0 else 1) * 14, 3, 22)
    else:
        plot_df["_sz"] = 6

    is_hl = plot_df["fips"].isin(highlighted_fips) if ("fips" in plot_df.columns and highlighted_fips) else pd.Series(False, index=plot_df.index)

    fig = go.Figure()

    # Background counties (lower opacity)
    bg = plot_df[~is_hl]
    if not bg.empty:
        fig.add_trace(go.Scatter3d(
            x=bg["longitude"], y=bg["latitude"], z=bg[color_col],
            mode="markers",
            marker=dict(
                size=bg["_sz"], color=bg[color_col], colorscale="RdYlGn_r",
                opacity=0.45, line=dict(width=0),
                colorbar=dict(title=color_col.replace("_", " ").title(), thickness=12, len=0.6),
            ),
            text=bg.get("county_name", bg.get("fips", "")),
            hovertemplate="<b>%{text}</b><br>" + color_col + ": %{z:.3f}<extra></extra>",
            name="Counties",
        ))

    # Highlighted counties (full opacity, white outline)
    hl = plot_df[is_hl]
    if not hl.empty:
        fig.add_trace(go.Scatter3d(
            x=hl["longitude"], y=hl["latitude"], z=hl[color_col],
            mode="markers+text",
            marker=dict(
                size=hl["_sz"] * 1.5, color=hl[color_col], colorscale="RdYlGn_r",
                opacity=1.0, line=dict(width=2, color="white"),
            ),
            text=hl["county_name"].str.split(",").str[0] if "county_name" in hl.columns else hl.get("fips", ""),
            textposition="top center",
            textfont=dict(size=9, color="white"),
            hovertemplate="<b>%{text}</b><br>" + color_col + ": %{z:.3f}<extra>Analyzed</extra>",
            name="Analyzed",
        ))

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        title=dict(text=title, font=dict(size=14)),
        height=500, margin=dict(l=0, r=0, t=35, b=0),
        scene=dict(
            xaxis=dict(title="Longitude", backgroundcolor="rgba(0,0,0,0)", gridcolor="#2d3748"),
            yaxis=dict(title="Latitude", backgroundcolor="rgba(0,0,0,0)", gridcolor="#2d3748"),
            zaxis=dict(title=color_col.replace("_", " ").title(), backgroundcolor="rgba(0,0,0,0)", gridcolor="#2d3748"),
            bgcolor="rgba(14,17,23,1)",
        ),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0.5)"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# CHOROPLETH MAP — County-level heatmap rendered once per intelligence report
# ═══════════════════════════════════════════════════════════════════════

def _extract_fips_from_result(data):
    """Extract all FIPS codes from a tool result dict or list."""
    fips_set = set()
    if isinstance(data, dict):
        fip = data.get("fips")
        if fip:
            fips_set.add(str(fip).zfill(5))
        for key in ("counties", "rankings", "priority_zones", "disparities",
                     "affected_counties", "neighbors"):
            items = data.get(key, [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and "fips" in item:
                        fips_set.add(str(item["fips"]).zfill(5))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "fips" in item:
                fips_set.add(str(item["fips"]).zfill(5))
    return fips_set


def render_choropleth_report_map(highlighted_fips, color_col="risk_score", title="County Risk Map", scope_df=None):
    """
    Render ONE choropleth map at the end of an intelligence report.

    - Background: ALL counties in relevant state(s) colored by color_col
    - Highlight: Analyzed counties outlined in cyan
    - Overlay: Red X markers for infrastructure gaps (>30km to hospital)
    - Auto-zoom: fitbounds to state extent

    Parameters
    ----------
    highlighted_fips : set  – FIPS codes that get a cyan border highlight
    color_col : str         – column to color the heatmap
    title : str             – chart title
    scope_df : DataFrame    – optional pre-filtered county DataFrame
                              (skip session-state lookup & state scoping)
    """
    if scope_df is not None:
        # Caller provided the data directly (e.g. Data Explorer Panel 1)
        scope_df = _filter_continental(scope_df.copy())
        if scope_df.empty:
            return
    else:
        # Agentic report path: pull full dataset and scope by states in highlighted_fips
        full_df = st.session_state.get("df")
        if full_df is None or not highlighted_fips:
            return
        state_fips_set = {f[:2] for f in highlighted_fips if len(f) >= 5}
        state_fips_set -= EXCLUDED_STATE_FIPS
        if not state_fips_set:
            return
        scope_df = full_df[full_df["fips"].str[:2].isin(state_fips_set)].copy()
        if scope_df.empty:
            return

    try:
        geojson = load_counties_geojson()
    except Exception:
        return  # Silently fail if GeoJSON unavailable

    if color_col not in scope_df.columns:
        color_col = "risk_score"

    # ── Background choropleth: all counties in scope colored by metric ──
    hover_data = {"risk_score": ":.3f", "total_population": ":,", "fips": False}
    if color_col != "risk_score":
        hover_data[color_col] = ":.3f"
    fig = px.choropleth(
        scope_df,
        geojson=geojson, locations="fips",
        color=color_col, color_continuous_scale="RdYlGn_r",
        hover_name="county_name",
        hover_data=hover_data,
        title=title,
    )

    # ── Highlight layer: bright cyan border on analyzed counties ─────────
    highlight_df = scope_df[scope_df["fips"].isin(highlighted_fips)]
    if not highlight_df.empty:
        fig.add_trace(go.Choropleth(
            geojson=geojson,
            locations=highlight_df["fips"].tolist(),
            z=[1] * len(highlight_df),
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
            marker_line_color="#00ffff", marker_line_width=3,
            showscale=False, hoverinfo="skip",
        ))

    # ── Infrastructure gap overlay: red X for >30km to hospital ─────────
    if "dist_nearest_hospitals_km" in scope_df.columns:
        infra_gaps = scope_df[
            (scope_df["dist_nearest_hospitals_km"] > 30) &
            scope_df["latitude"].notna() & scope_df["longitude"].notna()
        ]
        if len(infra_gaps) > 0:
            fig.add_trace(go.Scattergeo(
                lat=infra_gaps["latitude"], lon=infra_gaps["longitude"],
                marker=dict(size=8, symbol="x", color="red", opacity=0.9),
                text=infra_gaps.apply(
                    lambda r: f"{r['county_name']}<br>Hospital: {r['dist_nearest_hospitals_km']:.0f}km", axis=1),
                hovertemplate="%{text}<extra>Infrastructure Gap</extra>",
                name=f"Infra Gaps ({len(infra_gaps)})",
            ))

    # ── Layout: auto-zoom to data extent ────────────────────────────────
    fig.update_geos(
        scope="usa", fitbounds="locations", visible=True,
        showland=True, landcolor="#1a202c",
        showlakes=True, lakecolor="#2d3748", bgcolor="rgba(0,0,0,0)",
        showsubunits=True, subunitcolor="#2d3748",
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=450, margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(x=0.01, y=0.01, bgcolor="rgba(0,0,0,0.5)"),
        coloraxis_colorbar=dict(title=color_col.replace("_", " ").title(), thickness=15),
    )
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# TOOL VISUALIZATION — Auto-render charts from agentic tool results
# ═══════════════════════════════════════════════════════════════════════

def render_tool_visuals(steps):
    """
    Scan AgenticSteps and render inline charts for each tool result,
    then render a single choropleth + 3-D dot-matrix map at the end
    covering ALL counties encountered across every tool step.
    """
    # Track seen items to avoid duplicates across multiple tool calls
    seen_counties = set()  # county_name + tool_type fingerprint
    seen_hazards = set()

    # ── Accumulate data for the end-of-report map ──────────────────
    all_highlighted_fips: set = set()
    best_color_col = "risk_score"  # updated as we see tools

    ESSENTIAL_COLS = ["county_name", "risk_score", "risk_level", "total_population", "poverty_pct"]

    for step in steps:
        if not step.tool_name or not step.tool_result:
            continue
        data = step.tool_result
        name = step.tool_name

        # --- Collect FIPS from every tool step for the end map ---
        all_highlighted_fips |= _extract_fips_from_result(data)

        # --- Auto-detect best color column from TOOL_COLOR_MAP ---
        if name in TOOL_COLOR_MAP:
            best_color_col = TOOL_COLOR_MAP[name]

        try:
            # ── County rankings: metric cards + table (map moved to end) ──
            if name in ("query_counties", "get_state_rankings"):
                records = data if isinstance(data, list) else data.get("counties", data.get("rankings", []))
                records = [r for r in records if isinstance(r, dict) and "county_name" in r and "risk_score" in r]

                record_fingerprint = tuple(sorted([r.get("county_name") for r in records[:3]]))
                if record_fingerprint in seen_counties:
                    continue
                seen_counties.add(record_fingerprint)

                if records:
                    rdf = pd.DataFrame(records)

                    # Compact metrics row for top county
                    top_county = rdf.loc[rdf['risk_score'].idxmax()]
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Highest Risk", top_county.get('county_name', 'N/A').split(',')[0])
                    m2.metric("Risk Score", f"{top_county.get('risk_score', 0):.3f}")
                    m3.metric("Population", f"{top_county.get('total_population', 0):,}" if isinstance(top_county.get('total_population'), (int, float)) else "N/A")
                    m4.metric("Poverty", f"{top_county.get('poverty_pct', 0):.1f}%" if isinstance(top_county.get('poverty_pct'), (int, float)) else "N/A")

                    # Collapsible full table
                    if len(rdf) > 0:
                        with st.expander(f"View All {len(rdf)} Counties", expanded=False):
                            show_cols = [c for c in ESSENTIAL_COLS if c in rdf.columns]
                            st.dataframe(rdf[show_cols].sort_values("risk_score", ascending=False),
                                        use_container_width=True, hide_index=True)

            # ── County detail: metric cards (already optimized) ────────
            elif name == "get_county_detail":
                if isinstance(data, dict) and "error" not in data:
                    county_key = data.get("county_name", "")
                    if county_key in seen_counties:
                        continue
                    seen_counties.add(county_key)
                    
                    cname = data.get("county_name", "County")
                    st.markdown(f"**📍 {cname}**")
                    c1, c2, c3, c4, c5, c6 = st.columns(6)
                    c1.metric("Population", f"{data.get('total_population', 'N/A'):,}" if isinstance(data.get('total_population'), (int, float)) else "N/A")
                    c2.metric("Risk Score", f"{data.get('risk_score', 'N/A'):.3f}" if isinstance(data.get('risk_score'), (int, float)) else "N/A")
                    c3.metric("Risk Level", data.get("risk_level", "N/A"))
                    c4.metric("Poverty", f"{data.get('poverty_pct', 'N/A'):.1f}%" if isinstance(data.get('poverty_pct'), (int, float)) else "N/A")
                    c5.metric("Uninsured", f"{data.get('uninsured_pct', 'N/A'):.1f}%" if isinstance(data.get('uninsured_pct'), (int, float)) else "N/A")
                    hosp = data.get("dist_nearest_hospitals_km")
                    c6.metric("Hospital Dist", f"{hosp:.1f} km" if isinstance(hosp, (int, float)) else "N/A")

            # ── Infrastructure density: compact cards ──────────────────
            elif name == "get_infrastructure_density":
                if isinstance(data, dict) and "error" not in data:
                    cname = data.get('county_name', data.get('fips', ''))
                    st.markdown(f"**🏥 Infrastructure Density** — {cname}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Hospitals/10k", f"{data.get('hospitals_per_10k', data.get('density_hospitals_per10k', 0)):.2f}")
                    c2.metric("EMS/10k", f"{data.get('ems_per_10k', data.get('density_ems_stations_per10k', 0)):.2f}")
                    c3.metric("Fire/10k", f"{data.get('fire_per_10k', data.get('density_fire_stations_per10k', 0)):.2f}")

            # ── Risk contagion: compact summary ────────────────────────
            elif name == "analyze_risk_contagion":
                if isinstance(data, dict) and "error" not in data:
                    county_key = data.get('county_name', data.get('fips', ''))
                    if f"contagion_{county_key}" in seen_counties:
                        continue
                    seen_counties.add(f"contagion_{county_key}")
                    
                    st.markdown(f"**🔗 Risk Contagion** — {county_key}")
                    c1, c2, c3 = st.columns(3)
                    neighbors = data.get("neighbor_count", data.get("neighbors_in_radius", "N/A"))
                    high_risk = data.get("high_risk_neighbors", "N/A")
                    amplification = data.get("amplification_factor", data.get("risk_amplification", "N/A"))
                    c1.metric("Neighbors", neighbors)
                    c2.metric("High-Risk", high_risk)
                    c3.metric("Amplification", f"{amplification}x" if isinstance(amplification, (int, float)) else amplification)
                    
                    # Show neighbor list in expander if available
                    neighbor_list = data.get("neighbors", [])
                    if neighbor_list and isinstance(neighbor_list, list):
                        with st.expander(f"View {len(neighbor_list)} Neighboring Counties", expanded=False):
                            st.write(", ".join([n.get("county_name", str(n)) for n in neighbor_list[:10]]) + 
                                     (f" ... and {len(neighbor_list) - 10} more" if len(neighbor_list) > 10 else ""))

            # ── Health disparities: bar chart (top 5 only) ─────────────
            elif name == "get_mo_health_disparities":
                zones = data if isinstance(data, list) else data.get("priority_zones", data.get("disparities", []))
                zones = [z for z in zones if isinstance(z, dict) and "county_name" in z]
                
                # Deduplicate
                zone_fingerprint = tuple(sorted([z.get("county_name") for z in zones[:3]]))
                if zone_fingerprint in seen_counties:
                    continue
                seen_counties.add(zone_fingerprint)
                
                if zones:
                    zdf = pd.DataFrame(zones)
                    metric_col = next((c for c in ["disparity_index", "uninsured_pct", "poverty_pct"] if c in zdf.columns), None)
                    if metric_col:
                        # Show top 5 only
                        zdf_top = zdf.sort_values(metric_col, ascending=False).head(5).sort_values(metric_col, ascending=True)
                        remaining = len(zdf) - 5
                        
                        fig = px.bar(zdf_top,
                                     x=metric_col, y="county_name", orientation="h",
                                     color=metric_col, color_continuous_scale="Reds",
                                     title=f"Top {len(zdf_top)} Health Disparity Zones")
                        fig.update_layout(
                            template="plotly_dark", 
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)", 
                            height=200,
                            margin=dict(l=10, r=10, t=30, b=10),
                            yaxis_title="", 
                            xaxis_title=metric_col.replace("_", " ").title(),
                            coloraxis_showscale=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        if remaining > 0:
                            with st.expander(f"View All {len(zdf)} Disparity Zones", expanded=False):
                                show_cols = [c for c in ["county_name", metric_col, "risk_score", "poverty_pct"] if c in zdf.columns]
                                st.dataframe(zdf[show_cols].sort_values(metric_col, ascending=False), 
                                            use_container_width=True, hide_index=True)

            # ── Intervention ROI: bar chart (top 5) ────────────────────
            elif name == "calculate_intervention_roi":
                interventions = data if isinstance(data, list) else data.get("interventions", data.get("ranked_interventions", []))
                interventions = [i for i in interventions if isinstance(i, dict)]
                
                # Deduplicate
                int_fingerprint = tuple(sorted([i.get("intervention", i.get("name", str(i))) for i in interventions[:3]]))
                if int_fingerprint in seen_hazards:
                    continue
                seen_hazards.add(int_fingerprint)
                
                if interventions:
                    idf = pd.DataFrame(interventions)
                    name_col = next((c for c in ["intervention", "name", "type"] if c in idf.columns), None)
                    val_col = next((c for c in ["cost_per_person", "roi_score", "cost_effectiveness"] if c in idf.columns), None)
                    if name_col and val_col:
                        # Show top 5
                        idf_top = idf.sort_values(val_col).head(5)
                        
                        fig = px.bar(idf_top, x=val_col, y=name_col, orientation="h",
                                     color=val_col, color_continuous_scale="Viridis",
                                     title="Top 5 Interventions by Cost-Effectiveness")
                        fig.update_layout(
                            template="plotly_dark", 
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)", 
                            height=200,
                            margin=dict(l=10, r=10, t=30, b=10),
                            yaxis_title="", 
                            xaxis_title=val_col.replace("_", " ").title(),
                            coloraxis_showscale=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        if len(idf) > 5:
                            with st.expander(f"View All {len(idf)} Interventions", expanded=False):
                                show_cols = [c for c in [name_col, val_col, "roi_score", "effectiveness"] if c in idf.columns]
                                st.dataframe(idf[show_cols].sort_values(val_col), 
                                            use_container_width=True, hide_index=True)

            # ── Scenario simulation: compact metrics ───────────────────
            elif name == "simulate_scenario":
                if isinstance(data, dict) and "error" not in data:
                    scenario_key = data.get('scenario', 'simulation')
                    if scenario_key in seen_hazards:
                        continue
                    seen_hazards.add(scenario_key)
                    
                    st.markdown(f"**🌊 Scenario: {data.get('scenario', 'Simulation')}**")
                    c1, c2, c3 = st.columns(3)
                    pop_affected = data.get('total_population_affected', data.get('population_at_risk', 0))
                    counties_affected = data.get("counties_affected", data.get("affected_county_count", "N/A"))
                    damage = data.get("estimated_damage", data.get("infrastructure_damage_estimate", "N/A"))
                    c1.metric("Population at Risk", f"{pop_affected:,}" if isinstance(pop_affected, (int, float)) else str(pop_affected))
                    c2.metric("Counties Affected", counties_affected)
                    c3.metric("Est. Damage", damage if isinstance(damage, str) else f"${damage:,}")
                    
                    affected = data.get("affected_counties", [])
                    if affected and isinstance(affected[0], dict):
                        with st.expander(f"View {len(affected)} Affected Counties", expanded=False):
                            adf = pd.DataFrame(affected)
                            show_cols = [c for c in ["county_name", "population_affected", "damage_estimate", "risk_level"] if c in adf.columns]
                            st.dataframe(adf[show_cols][:10], use_container_width=True, hide_index=True)
                            if len(adf) > 10:
                                st.caption(f"... and {len(adf) - 10} more counties")

            # ── Pop-weighted impact: top 5 bar chart ───────────────────
            elif name == "calculate_pop_weighted_impact":
                records = data if isinstance(data, list) else data.get("rankings", data.get("counties", []))
                records = [r for r in records if isinstance(r, dict) and "county_name" in r]
                
                # Deduplicate
                pw_fingerprint = tuple(sorted([r.get("county_name") for r in records[:3]]))
                if pw_fingerprint in seen_counties:
                    continue
                seen_counties.add(pw_fingerprint)
                
                if records:
                    rdf = pd.DataFrame(records)
                    score_col = next((c for c in ["weighted_impact", "pop_weighted_risk", "impact_score"] if c in rdf.columns), "risk_score")
                    if score_col in rdf.columns:
                        # Top 5 only
                        rdf_top = rdf.sort_values(score_col, ascending=False).head(5).sort_values(score_col, ascending=True)
                        remaining = len(rdf) - 5
                        
                        fig = px.bar(rdf_top,
                                     x=score_col, y="county_name", orientation="h",
                                     color=score_col, color_continuous_scale="RdYlGn_r",
                                     title=f"Top 5 Population-Weighted Risk Impact")
                        fig.update_layout(
                            template="plotly_dark", 
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)", 
                            height=200,
                            margin=dict(l=10, r=10, t=30, b=10),
                            yaxis_title="", 
                            xaxis_title="Weighted Impact",
                            coloraxis_showscale=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        if remaining > 0:
                            with st.expander(f"View All {len(rdf)} Counties", expanded=False):
                                show_cols = [c for c in ["county_name", score_col, "risk_score", "total_population"] if c in rdf.columns]
                                st.dataframe(rdf[show_cols].sort_values(score_col, ascending=False), 
                                            use_container_width=True, hide_index=True)

            # ── Climate trends: summary metrics (compact) ───────────────
            elif name == "get_climate_trends":
                if isinstance(data, dict) and "error" not in data:
                    fips = data.get('fips', '')
                    if f"climate_{fips}" in seen_counties:
                        continue
                    seen_counties.add(f"climate_{fips}")
                    
                    trends = data.get("trends", {})
                    
                    # Handle both structures: trends as dict (correct) or trends as list (legacy/transformed)
                    if isinstance(trends, dict):
                        # Correct structure from climate_client.py: trends is a dict with mean_temp, precip keys
                        temp_info = trends.get("mean_temp", {})
                        precip_info = trends.get("precip", {})
                        avg_temp = temp_info.get("mean")
                        temp_trend = temp_info.get("slope_per_decade")
                        avg_precip = precip_info.get("mean")
                    elif isinstance(trends, list) and trends:
                        # Legacy/transformed structure: trends is a list, use summary instead
                        summary = data.get("summary", {})
                        avg_temp = summary.get("avg_temp")
                        temp_trend = summary.get("temp_trend")
                        avg_precip = summary.get("avg_precip")
                    else:
                        avg_temp = temp_trend = avg_precip = None
                    
                    county_name = data.get("county_name", f"FIPS {fips}")
                    st.markdown(f"**🌡️ Climate Trends** — {county_name}")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Avg Temp", f"{avg_temp:.1f}°F" if isinstance(avg_temp, (int, float)) else "N/A")
                    c2.metric("Temp Trend", f"{temp_trend:+.3f}°F/dec" if isinstance(temp_trend, (int, float)) else "N/A")
                    c3.metric("Avg Precip", f"{avg_precip:.1f}\"" if isinstance(avg_precip, (int, float)) else "N/A")
                    pop = data.get("total_population")
                    c4.metric("Population", f"{pop:,}" if isinstance(pop, (int, float)) else "N/A")

            # ── Hazard risk profile: top hazards bar chart ─────────────
            elif name == "get_hazard_risk_profile":
                if isinstance(data, dict) and "error" not in data:
                    fips = data.get('fips', '')
                    if f"hazard_{fips}" in seen_counties:
                        continue
                    seen_counties.add(f"hazard_{fips}")

                    county_name = data.get("county_name", f"FIPS {fips}")
                    st.markdown(f"**⚠️ FEMA Hazard Risk Profile** — {county_name}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Risk Rating", data.get("risk_rating", "N/A"))
                    eal = data.get("expected_annual_loss", 0)
                    c2.metric("Expected Annual Loss", f"${eal:,.0f}" if isinstance(eal, (int, float)) else "N/A")
                    svi = data.get("social_vulnerability", data.get("sovi_rating", "N/A"))
                    c3.metric("Social Vulnerability", f"{svi:.1f}" if isinstance(svi, (int, float)) else svi)

                    # Handle hazard_scores dict structure from NRI
                    hazard_scores = data.get("hazard_scores", {})
                    if isinstance(hazard_scores, dict) and hazard_scores:
                        # Convert to list, filter out zero/not-applicable hazards
                        hazard_list = [
                            {"hazard": name_h, "risk_score": v.get("risk_score", 0),
                             "expected_annual_loss": v.get("expected_annual_loss", 0),
                             "risk_rating": v.get("risk_rating", "")}
                            for name_h, v in hazard_scores.items()
                            if v.get("risk_score", 0) > 0
                        ]
                        if hazard_list:
                            hdf = pd.DataFrame(hazard_list).sort_values("risk_score", ascending=False)
                            # Top 5 hazards bar chart
                            hdf_top = hdf.head(5).sort_values("risk_score", ascending=True)
                            fig = px.bar(hdf_top, x="risk_score", y="hazard", orientation="h",
                                         color="risk_score", color_continuous_scale="YlOrRd",
                                         title=f"Top Hazards — {county_name}")
                            fig.update_layout(
                                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)", height=200,
                                margin=dict(l=10, r=10, t=30, b=10),
                                yaxis_title="", xaxis_title="NRI Risk Score",
                                coloraxis_showscale=False)
                            st.plotly_chart(fig, use_container_width=True)

                            if len(hdf) > 5:
                                with st.expander(f"View All {len(hdf)} Active Hazards", expanded=False):
                                    st.dataframe(hdf[["hazard", "risk_score", "risk_rating", "expected_annual_loss"]],
                                                use_container_width=True, hide_index=True)
                    else:
                        # Legacy list format
                        hazards = data.get("hazards", data.get("top_hazards", []))
                        if hazards and isinstance(hazards, list) and isinstance(hazards[0], dict):
                            hdf = pd.DataFrame(hazards[:5])
                            show_cols = [c for c in ["hazard", "risk_score", "frequency", "severity"] if c in hdf.columns]
                            if show_cols:
                                st.dataframe(hdf[show_cols], use_container_width=True, hide_index=True)

            # ── Flood frequency: compact table ─────────────────────────
            elif name == "get_flood_frequency":
                if isinstance(data, dict) and "error" not in data:
                    fips = data.get('fips', '')
                    if f"flood_{fips}" in seen_counties:
                        continue
                    seen_counties.add(f"flood_{fips}")
                    
                    st.markdown(f"**🌊 Flood Frequency Analysis** — FIPS {fips}")
                    intervals = data.get("recurrence_intervals", data.get("flood_levels", {}))
                    if isinstance(intervals, dict) and intervals:
                        idf = pd.DataFrame([{"Return Period": k, "Flow (cfs)": v} for k, v in intervals.items()])
                        c1, c2, c3, c4 = st.columns(4)
                        for col, (_, row) in zip([c1, c2, c3, c4], idf.head(4).iterrows()):
                            col.metric(row["Return Period"], f"{row['Flow (cfs)']:,}")
                        if len(idf) > 4:
                            with st.expander("View All Return Periods", expanded=False):
                                st.dataframe(idf, use_container_width=True, hide_index=True)

            # ── Severe weather history: compact metrics ────────────────
            elif name == "get_severe_weather_history":
                if isinstance(data, dict) and "error" not in data:
                    fips = data.get('fips', '')
                    if f"weather_{fips}" in seen_counties:
                        continue
                    seen_counties.add(f"weather_{fips}")
                    
                    st.markdown(f"**⛈️ Severe Weather History** — FIPS {fips}")
                    summary = data.get("summary", {})
                    if summary:
                        cols = st.columns(min(len(summary), 4))
                        for col, (k, v) in zip(cols, list(summary.items())[:4]):
                            col.metric(k.replace("_", " ").title(), v)

            # ── Drought history: compact metrics ───────────────────────
            elif name == "get_drought_history":
                if isinstance(data, dict) and "error" not in data:
                    fips = data.get('fips', '')
                    if f"drought_{fips}" in seen_counties:
                        continue
                    seen_counties.add(f"drought_{fips}")
                    
                    st.markdown(f"**🏜️ Drought History** — FIPS {fips}")
                    summary = data.get("summary", data.get("statistics", {}))
                    if isinstance(summary, dict):
                        cols = st.columns(min(len(summary), 4))
                        for col, (k, v) in zip(cols, list(summary.items())[:4]):
                            col.metric(k.replace("_", " ").title(), v)

            # ── Climate projections: compact metrics ───────────────────
            elif name == "project_climate_risk_enhanced":
                if isinstance(data, dict) and "error" not in data:
                    proj_key = f"{data.get('fips', '')}_{data.get('scenario', '')}"
                    if proj_key in seen_counties:
                        continue
                    seen_counties.add(proj_key)
                    
                    proj = data.get("projection", {})
                    st.markdown(f"**📈 Climate Projection** — {data.get('scenario', 'SSP2-4.5')} ({data.get('horizon_years', 30)}yr)")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Temp Change", f"+{proj.get('temp_change_f', 'N/A')}°F" if isinstance(proj.get('temp_change_f'), (int, float)) else "N/A")
                    c2.metric("Precip Change", f"{proj.get('precip_change_pct', 'N/A')}%" if isinstance(proj.get('precip_change_pct'), (int, float)) else "N/A")
                    c3.metric("Extreme Events", f"{proj.get('extreme_event_multiplier', 'N/A')}x")

        except Exception:
            pass  # Malformed data — skip silently

    # ═══════════════════════════════════════════════════════════════
    # END-OF-REPORT MAP — single choropleth covering all tool steps
    # ═══════════════════════════════════════════════════════════════
    valid_fips = {f for f in all_highlighted_fips if len(f) == 5 and f.isdigit()}
    if valid_fips:
        tool_names = [s.tool_name for s in steps if s.tool_name]
        if any(t in tool_names for t in ("get_mo_health_disparities",)):
            map_title = "Health Disparity Analysis — County Heatmap"
        elif any(t in tool_names for t in ("get_hazard_risk_profile",)):
            map_title = "Natural Hazard Risk — County Heatmap"
        elif any(t in tool_names for t in ("simulate_scenario",)):
            map_title = "Scenario Impact — County Heatmap"
        else:
            map_title = "Vulnerability Assessment — County Heatmap"

        st.divider()
        render_choropleth_report_map(valid_fips, color_col=best_color_col, title=map_title)


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
            st.session_state.agent_config['lm_url'] = preset["base_url"]  # Update URL for selected model
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
            lm_key = st.text_input("LM Studio Key", value=st.session_state.agent_config['lm_key'], type="password")
            st.session_state.agent_config['lm_key'] = lm_key
            st.session_state.agent_config['lm_url'] = lm_url
        preset = {"base_url": st.session_state.agent_config['lm_url'], "model": "openai/gpt-oss-20b"}
        selected_key = "gpt-oss-20b"

    # Initialize orchestrator with selected model
    # FIX: Always use preset URL (not stale session state), sync after init
    if st.session_state.agentic_orchestrator is None and AGENTIC_AVAILABLE:
        try:
            correct_url = preset["base_url"]
            st.session_state.agentic_orchestrator = AgenticOrchestrator(
                lm_studio_url=correct_url,
                api_key=active_api_key,
                model=preset["model"],
            )
            st.session_state.agent_config['lm_url'] = correct_url  # Sync to session state
        except Exception as e:
            st.sidebar.error(f"Connection failed: {str(e)[:100]}")
            import logging
            logging.exception("Orchestrator init failed")

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
    st.caption("MUIDSI Hackathon 2026 | v3.2.0")


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
        ("Climate Trends", "Get climate trends for Boone County, MO (FIPS 29019). Show temperature and precipitation patterns from ACIS data."),
        ("Hazard Risk Profile", "Get the FEMA National Risk Index hazard profile for New Madrid County, MO (FIPS 29143). Show all natural hazards and expected annual losses."),
        ("Drought History", "Get drought history for Ozark County, MO (FIPS 29153) from the US Drought Monitor. Show frequency and severity trends."),
        ("Flood Frequency", "Get USGS flood frequency analysis for Jackson County, MO (FIPS 29095). Show recurrence intervals and gauge data."),
        ("Severe Weather", "Get severe weather history for St. Louis County, MO (FIPS 29189) from NOAA Storm Events. Show tornado and storm patterns."),
        ("Climate Projection", "Project future climate risk for Greene County, MO (FIPS 29077) under SSP2-4.5 scenario through 2050."),
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
                    st.rerun()  # Refresh to show the populated query in the text box

# Show indicator if a preset was selected
if st.session_state.get('query_input'):
    st.info("👆 Preset query loaded. Edit if needed, then click **Analyze**.")

# Query form (Enter key works)
with st.form("query_form", clear_on_submit=True):
    query_text = st.text_input(
        "Ask ResilienceAI",
        value=st.session_state.get('query_input', ""),
        placeholder="e.g., Which counties have accelerating disaster frequency and no hospital within 50km?"
    )
    submit_q = st.form_submit_button("Analyze", type="primary", use_container_width=True)

# Note: Preset buttons now only populate the text box without auto-submitting.
# The user can review/edit the prompt before manually clicking "Analyze".

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

    # Get filtered data based on sidebar state picker (always exclude AK/HI)
    fs = st.session_state.agent_config.get('focus_state', 'All States')
    focus_df = df if fs == "All States" else df[df["county_name"].str.endswith(f", {fs}")]
    focus_df = _filter_continental(focus_df)
    state_label = fs if fs != "All States" else "National"

    # ── Panel 1: Multi-Layer Vulnerability Map ──────────────────────────
    with st.expander(f"🗺️ Vulnerability Map — {state_label} ({len(focus_df):,} counties)", expanded=False):
        color_by = st.selectbox("Color by", ["risk_score", "vulnerability_index", "poverty_pct", "uninsured_pct", "elderly_pct", "disability_pct"], key="map_color")
        show_infra = st.checkbox("Overlay infrastructure gaps", value=True, key="map_infra")

        map_tab_choro, map_tab_3d = st.tabs(["Choropleth", "3-D Landscape"])

        with map_tab_choro:
            # Choropleth with filled county polygons
            infra_fips = set()
            if show_infra and "dist_nearest_hospitals_km" in focus_df.columns:
                infra_fips = set(focus_df[focus_df["dist_nearest_hospitals_km"] > 30]["fips"])
            render_choropleth_report_map(
                highlighted_fips=infra_fips,
                color_col=color_by,
                title=f"{color_by.replace('_', ' ').title()} — {state_label}",
                scope_df=focus_df,
            )

        with map_tab_3d:
            render_3d_dot_matrix(
                focus_df, set(),
                color_col=color_by,
                title=f"3-D {color_by.replace('_', ' ').title()} — {state_label}",
            )

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
st.caption("ResilienceAI v3.2.0 | MUIDSI Hackathon 2026 | Gemini + Local LLM Backends | 45+ MCP Tools")
