"""
ResilienceAI - Strategic Intelligence Dashboard
Disaster vulnerability assessment with multi-agent orchestration and climate intelligence.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests

try:
    import streamlit_antd_components as sac
    SAC_AVAILABLE = True
except ImportError:
    SAC_AVAILABLE = False

# Import ResilienceAgent
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
try:
    from agent import ResilienceAgent, get_mcp_tools
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

# Import modern UI
try:
    from modern_ui import (
        apply_modern_theme, render_modern_header, render_metric_card,
        render_status_indicator, apply_plotly_theme, COLORS, render_risk_badge
    )
    MODERN_UI_AVAILABLE = True
except ImportError:
    MODERN_UI_AVAILABLE = False

# Import multi-agent orchestrator
try:
    from agents.orchestrator import AgentOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

# Import climate client
try:
    from climate_client import ClimateIntelligenceClient
    CLIMATE_AVAILABLE = True
except ImportError:
    CLIMATE_AVAILABLE = False

# Import geospatial
try:
    from geo_visualizations import GeoVisualizer
    GEO_VIZ_AVAILABLE = True
except ImportError:
    GEO_VIZ_AVAILABLE = False

# ── Plotly Theme ─────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=40, b=40),
)

# ── Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="ResilienceAI | Strategic Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if MODERN_UI_AVAILABLE:
    apply_modern_theme()

# ── Session State ────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "agent_config": {
            "archia_url": "https://api.archia.app/v1",
            "api_key": os.environ.get("ARCHIA_API_KEY", ""),
            "model": "claude-sonnet-4-5-20250929",
            "use_local_agent": True,
        },
        "agent_history": [],
        "df": None,
        "local_agent": None,
        "orchestrator": None,
        "climate_client": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# ── Load Data ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        path = Path(__file__).parent.parent / "data" / "processed" / "county_features.csv"
        if path.exists():
            return pd.read_csv(path, dtype={"fips": str})
    except Exception as e:
        st.error(f"Data load error: {e}")
    return None

@st.cache_data
def load_zip_to_fips():
    """Load ZIP-to-county FIPS mapping from HUD USPS crosswalk or cached file."""
    cache_path = Path(__file__).parent.parent / "data" / "cache" / "zip_county_crosswalk.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path, dtype=str)
    # Build from Census ZCTA-County Relationship File
    try:
        url = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        raw = pd.read_csv(
            __import__("io").StringIO(resp.text), sep="|", dtype=str,
            encoding_errors="ignore",
        )
        # Strip BOM and whitespace from column names
        raw.columns = [c.strip().lstrip("\ufeff") for c in raw.columns]
        raw = raw[["GEOID_ZCTA5_20", "GEOID_COUNTY_20", "NAMELSAD_COUNTY_20"]]
        raw = raw.rename(columns={
            "GEOID_ZCTA5_20": "zip", "GEOID_COUNTY_20": "fips",
            "NAMELSAD_COUNTY_20": "county_name"
        })
        # Keep primary (first) mapping per ZIP
        raw = raw.drop_duplicates(subset="zip", keep="first")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        raw.to_csv(cache_path, index=False)
        return raw
    except Exception:
        return None

def zip_to_fips(zip_code: str, crosswalk=None) -> dict:
    """Look up county FIPS and name from a ZIP code."""
    if crosswalk is None:
        crosswalk = load_zip_to_fips()
    if crosswalk is None:
        return {"error": "ZIP crosswalk not available"}
    match = crosswalk[crosswalk["zip"] == str(zip_code).zfill(5)]
    if match.empty:
        return {"error": f"No county found for ZIP {zip_code}"}
    row = match.iloc[0]
    return {"fips": row["fips"], "county_name": row["county_name"], "zip": row["zip"]}

def county_picker(df, key_prefix, label="Find County"):
    """Reusable county picker: search by ZIP or select by name. Returns FIPS string."""
    search_mode = st.radio(label, ["By Name", "By ZIP Code"], horizontal=True, key=f"{key_prefix}_mode")
    if search_mode == "By ZIP Code":
        zip_input = st.text_input("ZIP Code", max_chars=5, key=f"{key_prefix}_zip",
                                  placeholder="e.g. 65201")
        if zip_input and len(zip_input) == 5:
            result = zip_to_fips(zip_input)
            if "error" not in result:
                st.caption(f"Mapped to **{result['county_name']}** (FIPS: {result['fips']})")
                return result["fips"]
            else:
                st.warning(result["error"])
                return None
        return None
    else:
        if df is None:
            return None
        mo_counties = df[df["county_name"].str.endswith(", Missouri")][["county_name", "fips"]].sort_values("county_name")
        if mo_counties.empty:
            mo_counties = df[["county_name", "fips"]].sort_values("county_name")
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

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ResilienceAI")
    st.caption("Strategic Intelligence for Disaster Resilience")
    st.divider()

    if df is not None:
        st.success(f"System Ready: {len(df):,} counties indexed")
        if ORCHESTRATOR_AVAILABLE:
            summary = st.session_state.orchestrator.get_agent_summary()
            st.info(f"Agents: {summary['total_agents']} | Tools: {summary['total_tools']}")
    else:
        st.error("System Offline: Data not loaded")

    st.divider()
    st.markdown("### Agent Config")
    st.session_state.agent_config["use_local_agent"] = not st.toggle(
        "Archia Cloud Mode", value=False
    )
    st.divider()
    st.caption("MUIDSI Hackathon 2026")

# ── Header ───────────────────────────────────────────────────────────
if MODERN_UI_AVAILABLE:
    render_modern_header("RESILIENCE AI", "Predictive Vulnerability Intelligence & Climate Analytics")

if SAC_AVAILABLE:
    sac.steps(
        items=[
            sac.StepsItem(title="DATA", subtitle="READY", icon="database-fill-check"),
            sac.StepsItem(title="AGENTS", subtitle=f"{'4 ACTIVE' if ORCHESTRATOR_AVAILABLE else 'LOADING'}", icon="robot"),
            sac.StepsItem(title="CLIMATE", subtitle=f"{'5 SOURCES' if CLIMATE_AVAILABLE else 'OFFLINE'}", icon="cloud-sun"),
        ],
        variant="circle", color="purple", size="sm"
    )

# ── Tabs ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Missouri Command Center",
    "National Vulnerability Map",
    "Climate Intelligence",
    "Agent Console",
    "Resilience Planner",
    "Live Operations",
])

# ── Tab 1: Missouri Command Center ──────────────────────────────────
with tab1:
    if df is not None:
        mo_df = df[df["county_name"].str.endswith(", Missouri")].copy()

        if not mo_df.empty:
            avg_risk = mo_df["risk_score"].mean()
            high_risk_count = len(mo_df[mo_df["risk_level"] == "High"])
            avg_uninsured = mo_df["uninsured_pct"].mean()
            avg_poverty = mo_df["poverty_pct"].mean()

            # KPI row
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Missouri Risk Index", f"{avg_risk:.3f}", delta=None)
            c2.metric("High-Risk Counties", high_risk_count, delta=None)
            c3.metric("Avg Uninsured %", f"{avg_uninsured:.1f}%", delta=None)
            c4.metric("Avg Poverty %", f"{avg_poverty:.1f}%", delta=None)

            st.divider()

            col_map, col_table = st.columns([3, 2])

            with col_map:
                st.subheader("Risk Distribution")
                fig = px.scatter(
                    mo_df, x="vulnerability_index", y="isolation_index",
                    size="total_population", color="risk_score",
                    hover_name="county_name",
                    color_continuous_scale="RdYlGn_r",
                    labels={"vulnerability_index": "Vulnerability", "isolation_index": "Isolation"},
                )
                fig.update_layout(**PLOTLY_LAYOUT, title="Vulnerability vs Isolation (size=population)")
                st.plotly_chart(fig, use_container_width=True)

            with col_table:
                st.subheader("Highest Risk Counties")
                top_mo = mo_df.nlargest(15, "risk_score")[
                    ["county_name", "risk_score", "risk_level", "vulnerability_index",
                     "isolation_index", "disaster_count"]
                ].reset_index(drop=True)
                top_mo.index += 1
                st.dataframe(top_mo, use_container_width=True)

            # Disparity analysis
            st.subheader("Health Disparity Matrix")
            if AGENT_AVAILABLE and st.session_state.local_agent:
                try:
                    res = st.session_state.local_agent.get_mo_health_disparities(
                        focus_metric="uninsured_pct", max_results=15
                    )
                    df_zones = pd.DataFrame(res["priority_zones"])
                    fig = px.bar(
                        df_zones, x="county_name", y="disparity_index",
                        color="disparity_index", color_continuous_scale="Purples",
                    )
                    fig.update_layout(**PLOTLY_LAYOUT, title="Priority Disparity Zones")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Disparity analysis unavailable: {e}")
    else:
        st.info("Load county data to view Missouri assessment.")

# ── Tab 2: National Vulnerability Map ────────────────────────────────
with tab2:
    if df is not None:
        st.subheader("National Vulnerability Explorer")

        col_filter, col_viz = st.columns([1, 3])

        with col_filter:
            # State filter
            states = sorted(df["county_name"].str.split(", ").str[-1].dropna().unique())
            selected_state = st.selectbox("Filter by State", ["All States"] + list(states))

            metric_choice = st.selectbox("Color by Metric", [
                "risk_score", "vulnerability_index", "isolation_index",
                "poverty_pct", "elderly_pct", "uninsured_pct", "disaster_count"
            ])

            risk_filter = st.multiselect("Risk Level", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])

        with col_viz:
            viz_df = df[df["risk_level"].isin(risk_filter)].copy()
            if selected_state != "All States":
                viz_df = viz_df[viz_df["county_name"].str.endswith(f", {selected_state}")]

            if not viz_df.empty:
                fig = px.scatter(
                    viz_df.sample(min(500, len(viz_df))),
                    x="vulnerability_index", y="risk_score",
                    color=metric_choice, size="total_population",
                    hover_name="county_name",
                    color_continuous_scale="Turbo",
                )
                fig.update_layout(**PLOTLY_LAYOUT, height=500,
                                  title=f"Vulnerability Explorer ({len(viz_df):,} counties)")
                st.plotly_chart(fig, use_container_width=True)

        # Summary statistics
        st.subheader("Summary Statistics")
        if not viz_df.empty:
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Counties", f"{len(viz_df):,}")
            sc2.metric("Avg Risk Score", f"{viz_df['risk_score'].mean():.3f}")
            sc3.metric("High Risk", f"{len(viz_df[viz_df['risk_level'] == 'High']):,}")
            sc4.metric("Population", f"{viz_df['total_population'].sum():,.0f}")

            with st.expander("View Data Table"):
                st.dataframe(
                    viz_df[["county_name", "fips", "risk_score", "risk_level",
                            "vulnerability_index", "total_population"]].sort_values("risk_score", ascending=False).head(50),
                    use_container_width=True
                )
    else:
        st.info("Load county data to explore vulnerabilities.")

# ── Tab 3: Climate Intelligence ──────────────────────────────────────
with tab3:
    st.subheader("Climate Intelligence Dashboard")

    if df is not None and CLIMATE_AVAILABLE:
        # County selector — by name or ZIP code
        selected_fips = county_picker(df, key_prefix="climate", label="Find County")
        if selected_fips is None:
            st.info("Enter a ZIP code or select a county to view climate data.")

        ci1, ci2, ci3, ci4, ci5, ci6 = st.tabs([
            "Temperature & Precipitation",
            "Hazard Risk Profile",
            "Drought Timeline",
            "Severe Weather",
            "Climate Projections",
            "Satellite Intelligence",
        ])

        # Sub-tab 1: Climate Trends
        with ci1:
            try:
                climate = st.session_state.climate_client
                trends = climate.acis.get_climate_trends(selected_fips, 2000, 2024)

                if "error" not in trends and trends.get("records"):
                    records = trends["records"]
                    df_climate = pd.DataFrame(records)

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_climate["year"], y=df_climate["max_temp_f"],
                        name="Max Temp (F)", line=dict(color="#ef4444", width=2)
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_climate["year"], y=df_climate["min_temp_f"],
                        name="Min Temp (F)", line=dict(color="#3b82f6", width=2)
                    ))
                    fig.add_trace(go.Bar(
                        x=df_climate["year"], y=df_climate["total_precip_in"],
                        name="Precipitation (in)", yaxis="y2",
                        marker_color="rgba(147, 197, 253, 0.4)"
                    ))
                    fig.update_layout(
                        **PLOTLY_LAYOUT, height=450,
                        title=f"Climate Trends: {selected_county}",
                        yaxis=dict(title="Temperature (F)"),
                        yaxis2=dict(title="Precipitation (in)", overlaying="y", side="right"),
                        legend=dict(x=0, y=1.1, orientation="h"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Trend summary
                    trend_data = trends.get("trends", {})
                    if trend_data:
                        tc1, tc2, tc3 = st.columns(3)
                        for col, key, label in [(tc1, "max_temp", "Max Temp"), (tc2, "min_temp", "Min Temp"), (tc3, "precip", "Precipitation")]:
                            t = trend_data.get(key, {})
                            col.metric(
                                f"{label} Trend",
                                f"{t.get('slope_per_decade', 0):+.2f}/decade",
                                delta=t.get("direction", "unknown"),
                            )
                else:
                    st.warning("Climate data not available for this county. ACIS API may be temporarily unavailable.")
            except Exception as e:
                st.warning(f"Climate trends unavailable: {e}")

        # Sub-tab 2: Hazard Risk Profile
        with ci2:
            try:
                profile = st.session_state.climate_client.nri.get_hazard_risk_profile(selected_fips)
                if "error" not in profile:
                    hc1, hc2, hc3 = st.columns(3)
                    hc1.metric("Risk Rating", profile.get("risk_rating", "N/A"))
                    hc2.metric("Expected Annual Loss", f"${profile.get('expected_annual_loss', 0):,.0f}")
                    hc3.metric("Social Vulnerability", f"{profile.get('social_vulnerability', 0):.2f}")

                    # Hazard heatmap
                    hazards = profile.get("hazard_scores", {})
                    if hazards:
                        hz_data = []
                        for name, scores in hazards.items():
                            hz_data.append({"Hazard": name, "Risk Score": scores.get("risk_score", 0),
                                           "Expected Annual Loss": scores.get("expected_annual_loss", 0)})
                        hz_df = pd.DataFrame(hz_data).sort_values("Risk Score", ascending=True)
                        fig = px.bar(hz_df, x="Risk Score", y="Hazard", orientation="h",
                                     color="Risk Score", color_continuous_scale="YlOrRd")
                        fig.update_layout(**PLOTLY_LAYOUT, height=500,
                                          title=f"18-Hazard Risk Profile: {selected_county}")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("FEMA NRI data not yet downloaded. Run: `python src/climate_client.py --fips 29019 --source nri`")
            except Exception as e:
                st.warning(f"Hazard profile unavailable: {e}")

        # Sub-tab 3: Drought Timeline
        with ci3:
            try:
                drought = st.session_state.climate_client.drought.get_drought_history(
                    selected_fips, start_date="2015-01-01"
                )
                if drought.get("records"):
                    df_drought = pd.DataFrame(drought["records"])
                    fig = go.Figure()
                    colors = {"d0_pct": "#fde68a", "d1_pct": "#fbbf24", "d2_pct": "#f59e0b",
                              "d3_pct": "#d97706", "d4_pct": "#92400e"}
                    labels = {"d0_pct": "D0 Abnormal", "d1_pct": "D1 Moderate", "d2_pct": "D2 Severe",
                              "d3_pct": "D3 Extreme", "d4_pct": "D4 Exceptional"}
                    for col, color in colors.items():
                        fig.add_trace(go.Scatter(
                            x=df_drought["date"], y=df_drought[col],
                            name=labels[col], fill="tonexty" if col != "d0_pct" else "tozeroy",
                            line=dict(width=0.5, color=color),
                            fillcolor=color.replace(")", ",0.5)") if "rgba" in color else color,
                        ))
                    fig.update_layout(**PLOTLY_LAYOUT, height=400,
                                      title=f"Drought Timeline: {selected_county}",
                                      yaxis_title="% Area")
                    st.plotly_chart(fig, use_container_width=True)

                    # Summary
                    summary = drought.get("summary", {})
                    if summary:
                        dc1, dc2, dc3 = st.columns(3)
                        dc1.metric("Total Weeks Tracked", summary.get("total_weeks", 0))
                        dc2.metric("Weeks in Drought", summary.get("weeks_any_drought", 0))
                        dc3.metric("Drought Frequency", f"{summary.get('drought_frequency_pct', 0):.1f}%")
                else:
                    st.info("Drought data loading... US Drought Monitor API may take a moment.")
            except Exception as e:
                st.warning(f"Drought data unavailable: {e}")

        # Sub-tab 4: Severe Weather
        with ci4:
            try:
                severe = st.session_state.climate_client.severe.get_severe_weather_history(selected_fips)
                st.metric("Total Events (2000-2025)", severe.get("total_events", 0))

                event_counts = severe.get("event_type_counts", {})
                if event_counts:
                    fig = px.pie(
                        values=list(event_counts.values()),
                        names=list(event_counts.keys()),
                        title=f"Severe Weather Events: {selected_county}",
                    )
                    fig.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Severe weather history requires bulk SPC data download for full coverage. Summary statistics are available via FEMA disaster declarations in the vulnerability tab.")
            except Exception as e:
                st.warning(f"Severe weather data unavailable: {e}")

        # Sub-tab 5: Climate Projections
        with ci5:
            try:
                scenario_choice = st.select_slider(
                    "SSP Scenario",
                    options=["ssp1_19", "ssp2_45", "ssp5_85"],
                    value="ssp2_45",
                    format_func=lambda x: {"ssp1_19": "SSP1-1.9 (Low)", "ssp2_45": "SSP2-4.5 (Medium)", "ssp5_85": "SSP5-8.5 (High)"}[x]
                )
                horizon = st.slider("Projection Horizon (years)", 10, 80, 30)

                if ORCHESTRATOR_AVAILABLE:
                    result = st.session_state.orchestrator.execute_tool(
                        "project_climate_risk_enhanced",
                        {"fips": selected_fips, "scenario": scenario_choice, "horizon_years": horizon}
                    )

                    if "error" not in result:
                        baseline = result.get("baseline", {})
                        proj = result.get("projection", {})
                        risk = result.get("risk_implications", {})

                        pc1, pc2, pc3 = st.columns(3)
                        pc1.metric("Current Mean Temp", f"{baseline.get('mean_temp_f', 0):.1f}F",
                                  delta=f"{proj.get('temp_change_f', 0):+.1f}F projected")
                        pc2.metric("Extreme Weather", f"{proj.get('extreme_event_multiplier', 1)}x",
                                  delta="vs current frequency")
                        pc3.metric("Heat Stress Risk", risk.get("heat_stress", "Unknown"))

                        # Comparison chart across all 3 scenarios
                        all_scenarios = []
                        for sc in ["ssp1_19", "ssp2_45", "ssp5_85"]:
                            r = st.session_state.orchestrator.execute_tool(
                                "project_climate_risk_enhanced",
                                {"fips": selected_fips, "scenario": sc, "horizon_years": horizon}
                            )
                            if "error" not in r:
                                all_scenarios.append({
                                    "Scenario": sc.upper().replace("_", "-"),
                                    "Projected Temp (F)": r["projection"]["projected_mean_temp_f"],
                                    "Temp Change (F)": r["projection"]["temp_change_f"],
                                    "Extreme Multiplier": r["projection"]["extreme_event_multiplier"],
                                })

                        if all_scenarios:
                            sc_df = pd.DataFrame(all_scenarios)
                            fig = px.bar(sc_df, x="Scenario", y="Temp Change (F)",
                                        color="Extreme Multiplier", color_continuous_scale="OrRd",
                                        text="Projected Temp (F)")
                            fig.update_layout(**PLOTLY_LAYOUT, title=f"Scenario Comparison: {selected_county} ({horizon}yr horizon)")
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Projection requires historical climate data. Run ACIS data fetch first.")
                else:
                    st.info("Multi-agent orchestrator not available.")
            except Exception as e:
                st.warning(f"Climate projections unavailable: {e}")

        # ── Subtab 6: Satellite Intelligence ────────────────────────────
        with ci6:
            st.markdown("**Satellite-derived indicators from Google Earth Engine (cached)**")

            try:
                from src.gee_client import GEEClient, GEE_CACHE_DIR

                sat_year = st.number_input("Satellite Data Year", 2020, 2025, 2024, key="sat_year")
                state_fips = "29"  # Missouri

                # Check cache status
                cache_status = GEEClient.get_cache_status(state_fips, sat_year)
                cached_count = sum(1 for v in cache_status.values() if v.get("cached"))

                if cached_count == 0:
                    st.warning(
                        f"No satellite data cached for state {state_fips}, year {sat_year}. "
                        f"Run: `python src/pipeline/gee_fetch.py --state {state_fips} --year {sat_year}`"
                    )
                    # Show cache status table
                    status_rows = []
                    for key, info in cache_status.items():
                        status_rows.append({
                            "Indicator": key.upper(),
                            "Status": "Cached" if info.get("cached") else "Not cached",
                            "Description": info.get("description", ""),
                        })
                    st.dataframe(pd.DataFrame(status_rows), use_container_width=True)
                else:
                    # Show freshness
                    st.success(f"{cached_count}/6 indicators cached for state {state_fips}, year {sat_year}")

                    cached_data = GEEClient.load_all_cached(state_fips, sat_year)

                    # LST choropleth
                    if "lst" in cached_data:
                        lst_df = cached_data["lst"]
                        if not lst_df.empty and "lst_fahrenheit" in lst_df.columns:
                            fig_lst = px.bar(
                                lst_df.sort_values("lst_fahrenheit", ascending=False).head(20),
                                x="county_name", y="lst_fahrenheit",
                                title=f"Land Surface Temperature — Top 20 Hottest Counties ({sat_year})",
                                labels={"lst_fahrenheit": "LST (°F)", "county_name": "County"},
                                color="lst_fahrenheit", color_continuous_scale="YlOrRd",
                            )
                            fig_lst.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-45)
                            st.plotly_chart(fig_lst, use_container_width=True)

                    # NDVI vegetation health
                    if "ndvi" in cached_data:
                        ndvi_df = cached_data["ndvi"]
                        if not ndvi_df.empty and "ndvi" in ndvi_df.columns:
                            fig_ndvi = px.bar(
                                ndvi_df.sort_values("ndvi").head(20),
                                x="county_name", y="ndvi",
                                title=f"Vegetation Health (NDVI) — 20 Most Stressed Counties ({sat_year})",
                                labels={"ndvi": "NDVI (0-1)", "county_name": "County"},
                                color="ndvi", color_continuous_scale="RdYlGn",
                            )
                            fig_ndvi.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-45)
                            st.plotly_chart(fig_ndvi, use_container_width=True)

                    # PDSI drought
                    if "pdsi" in cached_data:
                        pdsi_df = cached_data["pdsi"]
                        if not pdsi_df.empty and "pdsi" in pdsi_df.columns:
                            fig_pdsi = px.bar(
                                pdsi_df.sort_values("pdsi").head(20),
                                x="county_name", y="pdsi",
                                title=f"Palmer Drought Severity Index — 20 Driest Counties ({sat_year})",
                                labels={"pdsi": "PDSI", "county_name": "County"},
                                color="pdsi", color_continuous_scale="BrBG",
                            )
                            fig_pdsi.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-45)
                            st.plotly_chart(fig_pdsi, use_container_width=True)

                    # Nighttime lights
                    if "nightlights" in cached_data:
                        nl_df = cached_data["nightlights"]
                        if not nl_df.empty and "avg_radiance" in nl_df.columns:
                            fig_nl = px.bar(
                                nl_df.sort_values("avg_radiance", ascending=False).head(20),
                                x="county_name", y="avg_radiance",
                                title=f"Nighttime Lights (Infrastructure Proxy) — Top 20 ({sat_year})",
                                labels={"avg_radiance": "Radiance (nW/cm²/sr)", "county_name": "County"},
                                color="avg_radiance", color_continuous_scale="Viridis",
                            )
                            fig_nl.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-45)
                            st.plotly_chart(fig_nl, use_container_width=True)

                    # Cache freshness details
                    with st.expander("Cache Details"):
                        for key, info in cache_status.items():
                            if info.get("cached"):
                                st.text(f"{key:12s}  {info['rows']:4d} rows  updated {info['last_updated']}")
                            else:
                                st.text(f"{key:12s}  NOT CACHED")

            except ImportError:
                st.info("GEE client not available. Ensure `src/gee_client.py` exists.")
            except Exception as e:
                st.warning(f"Satellite data error: {e}")

    elif not CLIMATE_AVAILABLE:
        st.info("Climate Intelligence module not loaded. Ensure `src/climate_client.py` is available.")
    else:
        st.info("Load county data to access climate intelligence.")

# ── Tab 4: Agent Console ─────────────────────────────────────────────
with tab4:
    st.subheader("Multi-Agent Intelligence Console")

    if ORCHESTRATOR_AVAILABLE:
        # Agent status
        summary = st.session_state.orchestrator.get_agent_summary()
        agent_cols = st.columns(4)
        for i, (key, info) in enumerate(summary["agents"].items()):
            agent_cols[i].metric(info["name"].replace("_", " ").title(), f"{info['tool_count']} tools")

        st.divider()

        # Query interface
        query_text = st.text_area("Natural Language Query",
                                   placeholder="e.g., What are the climate trends and flood risk for Boone County, Missouri?",
                                   height=80)

        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            submit = st.button("Execute Query", type="primary", use_container_width=True)

        if submit and query_text:
            with st.spinner("Routing to specialist agent..."):
                # Route query
                routing = st.session_state.orchestrator.execute_query(query_text)
                st.session_state.agent_history.append({
                    "query": query_text, "routing": routing, "time": datetime.now().isoformat()
                })

                st.success(f"Routed to: **{routing['agent_name']}**")
                st.caption(f"Available tools: {', '.join(routing['available_tools'][:8])}...")

                # Try to auto-execute if we can determine the tool
                with col_info:
                    st.info(routing["message"])

        # Direct tool execution
        st.divider()
        st.subheader("Direct Tool Execution")

        all_tools = st.session_state.orchestrator.get_all_tools()
        tool_names = [t["name"] for t in all_tools]
        selected_tool = st.selectbox("Select Tool", tool_names)

        # Show tool description
        tool_def = next((t for t in all_tools if t["name"] == selected_tool), None)
        if tool_def:
            st.caption(tool_def.get("description", ""))

            # Build parameter inputs
            params = {}
            props = tool_def.get("parameters", {}).get("properties", {})
            required = tool_def.get("parameters", {}).get("required", [])

            if props:
                param_cols = st.columns(min(len(props), 3))
                for i, (pname, pdef) in enumerate(props.items()):
                    col = param_cols[i % len(param_cols)]
                    ptype = pdef.get("type", "string")
                    label = f"{pname}{'*' if pname in required else ''}"

                    if "enum" in pdef:
                        val = col.selectbox(label, pdef["enum"], key=f"param_{selected_tool}_{pname}")
                    elif ptype == "integer":
                        val = col.number_input(label, step=1, key=f"param_{selected_tool}_{pname}")
                    elif ptype == "number":
                        val = col.number_input(label, step=0.1, key=f"param_{selected_tool}_{pname}")
                    elif ptype == "boolean":
                        val = col.checkbox(label, key=f"param_{selected_tool}_{pname}")
                    elif ptype == "array":
                        val = col.text_input(label, placeholder="comma-separated", key=f"param_{selected_tool}_{pname}")
                        if val:
                            val = [v.strip() for v in val.split(",")]
                    else:
                        val = col.text_input(label, key=f"param_{selected_tool}_{pname}")

                    if val or pname in required:
                        params[pname] = val

            if st.button("Execute Tool", key="exec_tool"):
                # Filter empty params
                clean_params = {k: v for k, v in params.items() if v not in (None, "", 0, [])}
                with st.spinner(f"Executing {selected_tool}..."):
                    try:
                        result = st.session_state.orchestrator.execute_tool(selected_tool, clean_params)
                        st.json(result)
                    except Exception as e:
                        st.error(f"Tool execution error: {e}")

        # Conversation history
        if st.session_state.agent_history:
            st.divider()
            st.subheader("Session History")
            for entry in reversed(st.session_state.agent_history[-10:]):
                with st.expander(f"{entry.get('time', '')[:19]} - {entry['query'][:60]}..."):
                    st.json(entry["routing"])

    else:
        st.warning("Multi-agent orchestrator not available.")
        if AGENT_AVAILABLE:
            st.info("Falling back to single-agent mode.")

# ── Tab 5: Resilience Planner ────────────────────────────────────────
with tab5:
    st.subheader("Strategic Resource Allocation")

    if df is not None:
        plan_col1, plan_col2 = st.columns([2, 1])

        with plan_col1:
            # Risk-resource scatter
            mo_df = df[df["county_name"].str.endswith(", Missouri")].copy()
            plot_df = mo_df if not mo_df.empty else df.sample(min(200, len(df)))

            fig = px.scatter(
                plot_df, x="uninsured_pct", y="risk_score",
                size="total_population", color="risk_level",
                hover_name="county_name",
                color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"},
            )
            fig.update_layout(**PLOTLY_LAYOUT, title="Risk vs Healthcare Gap",
                              xaxis_title="Uninsured %", yaxis_title="Risk Score")
            st.plotly_chart(fig, use_container_width=True)

        with plan_col2:
            # Intervention ROI lookup
            st.subheader("Intervention ROI")
            if AGENT_AVAILABLE and st.session_state.local_agent:
                roi_fips = county_picker(df, key_prefix="roi", label="Select County for ROI")
                if roi_fips and st.button("Calculate ROI"):
                    with st.spinner("Analyzing interventions..."):
                        try:
                            result = st.session_state.local_agent.calculate_intervention_roi(roi_fips)
                            if "error" not in result:
                                st.json(result)
                            else:
                                st.warning(result["error"])
                        except Exception as e:
                            st.warning(f"ROI analysis unavailable: {e}")

        # Gap analysis
        st.divider()
        st.subheader("Gap Analysis - Top Interventions")
        if AGENT_AVAILABLE and st.session_state.local_agent:
            try:
                gaps = st.session_state.local_agent.get_gap_analysis(state="MO", max_results=10)
                if gaps:
                    df_gaps = pd.DataFrame(gaps)
                    st.dataframe(df_gaps, use_container_width=True)
            except Exception as e:
                st.warning(f"Gap analysis unavailable: {e}")
    else:
        st.info("Load county data for resilience planning.")

# ── Tab 6: Live Operations ───────────────────────────────────────────
with tab6:
    st.subheader("Live Weather & Alert Operations")

    live_col1, live_col2 = st.columns([2, 1])

    with live_col1:
        state_input = st.text_input("State Code", value="MO", max_chars=2, key="live_state")

        if st.button("Fetch Active Alerts", key="fetch_alerts"):
            if AGENT_AVAILABLE and st.session_state.local_agent:
                with st.spinner(f"Querying NOAA NWS for {state_input}..."):
                    try:
                        alerts = st.session_state.local_agent.get_weather_alerts(state=state_input)
                        if alerts and "error" not in alerts:
                            st.success(f"Found {alerts.get('total_alerts', 0)} active alerts")
                            for alert in alerts.get("alerts", [])[:10]:
                                severity = alert.get("severity", "Unknown")
                                color = {"Extreme": "red", "Severe": "orange", "Moderate": "yellow"}.get(severity, "blue")
                                st.markdown(f"**:{color}[{severity}]** {alert.get('event', 'Unknown')} - {alert.get('headline', '')[:100]}")
                        else:
                            st.info("No active weather alerts for this state.")
                    except Exception as e:
                        st.warning(f"Weather API unavailable: {e}")

    with live_col2:
        st.subheader("System Status")
        st.metric("Counties Indexed", f"{len(df):,}" if df is not None else "0")
        st.metric("Agent Mode", "Local" if st.session_state.agent_config["use_local_agent"] else "Archia Cloud")
        st.metric("MCP Tools", f"{len(get_mcp_tools()) if AGENT_AVAILABLE else 0}")
        st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))

        if st.button("Refresh", key="refresh_live"):
            st.rerun()

# ── Footer ───────────────────────────────────────────────────────────
st.divider()
st.caption("ResilienceAI v2.0 | 4 Specialist Agents | 52 MCP Tools | 5 Climate Data Sources | MUIDSI Hackathon 2026")
