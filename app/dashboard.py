"""
ResilienceAI - Streamlit Dashboard
Interactive disaster vulnerability assessment with maps and agent interface.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import joblib
from pathlib import Path
from config import PROCESSED_DIR, MODELS_DIR, FIGURES_DIR

try:
    import pydeck as pdk
    HAS_PYDECK = True
except ImportError:
    HAS_PYDECK = False

try:
    from src.visualization_3d import Visualization3D, get_visualization_help, HAS_PYDECK as VIZ_HAS_PYDECK, HAS_PLOTLY as VIZ_HAS_PLOTLY
    HAS_ADVANCED_VIZ = True
except ImportError:
    HAS_ADVANCED_VIZ = False

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResilienceAI - Disaster Vulnerability Assessment",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Branded header */
.main-header {
    background: linear-gradient(135deg, #0D1B2A 0%, #1B2838 50%, #0D1B2A 100%);
    border-left: 4px solid #4FC3F7;
    padding: 1.5rem 2rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 1.5rem;
}
.main-header h1 {
    color: #4FC3F7;
    font-size: 2.2rem;
    margin: 0 0 0.3rem 0;
    font-weight: 700;
    letter-spacing: 1px;
}
.main-header p {
    color: #B0BEC5;
    margin: 0;
    font-size: 0.95rem;
}
.main-header .subtitle {
    color: #E0E0E0;
    font-size: 1.1rem;
    margin-bottom: 0.2rem;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1A1F2E, #151A28);
    border-left: 3px solid #4FC3F7;
    padding: 0.8rem 1rem;
    border-radius: 0 6px 6px 0;
}
div[data-testid="stMetric"] label {
    text-transform: uppercase;
    font-size: 0.75rem !important;
    letter-spacing: 0.5px;
    color: #90A4AE !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #E0E0E0 !important;
    font-weight: 600;
}

/* Tab styling */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 3px solid #4FC3F7 !important;
    color: #4FC3F7 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0D1117 !important;
}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #4FC3F7 !important;
}

/* Dataframes */
div[data-testid="stDataFrame"] {
    border: 1px solid #1E293B;
    border-radius: 6px;
}

/* Footer */
.footer-badge {
    text-align: center;
    padding: 1.5rem;
    margin-top: 2rem;
    border-top: 1px solid #1E293B;
    color: #546E7A;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ── Global Plotly Layout ──────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E0E0E0"),
    hoverlabel=dict(bgcolor="#1A1F2E", font_size=13, font_color="#E0E0E0"),
    margin=dict(l=40, r=20, t=50, b=40),
)

MAPBOX_CONFIG = {"scrollZoom": True}


@st.cache_data
def load_data():
    """Load processed county features."""
    path = PROCESSED_DIR / "county_features.csv"
    if not path.exists():
        return None
    return pd.read_csv(path, dtype={"fips": str})


@st.cache_resource
def load_model():
    """Load trained model."""
    model_path = MODELS_DIR / "best_model.pkl"
    if not model_path.exists():
        return None, None, None, None
    model = joblib.load(model_path)
    scaler = joblib.load(MODELS_DIR / "scaler.pkl")
    le = joblib.load(MODELS_DIR / "label_encoder.pkl")
    features = joblib.load(MODELS_DIR / "feature_names.pkl")
    return model, scaler, le, features


def style_risk_table(df, columns=None):
    """Apply conditional formatting to risk-related tables."""
    if columns is None:
        columns = df.columns.tolist()
    styler = df.style

    # Color risk_level cells
    if "risk_level" in columns:
        risk_colors = {"Low": "#27ae60", "Medium": "#f39c12", "High": "#e74c3c"}
        styler = styler.map(
            lambda v: f"background-color: {risk_colors.get(v, 'transparent')}; color: white; font-weight: 600; border-radius: 3px; padding: 2px 6px"
            if v in risk_colors else "",
            subset=["risk_level"]
        )

    # Gradient on risk_score
    if "risk_score" in columns:
        styler = styler.background_gradient(subset=["risk_score"], cmap="RdYlGn_r", vmin=0, vmax=1)

    # Format numeric columns
    float_cols = [c for c in columns if c in df.columns and df[c].dtype in ['float64', 'float32']]
    for col in float_cols:
        if "pct" in col or "pctile" in col:
            styler = styler.format({col: "{:.1f}"})
        elif "score" in col or "index" in col or "acceleration" in col:
            styler = styler.format({col: "{:.3f}"})
        elif "population" in col:
            styler = styler.format({col: "{:,.0f}"})
        elif col.startswith("dist_"):
            styler = styler.format({col: "{:.1f}"})

    return styler


def main():
    # ── Branded Header ────────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>ResilienceAI</h1>
        <p class="subtitle">Disaster Vulnerability & Health Infrastructure Gap Assessment</p>
        <p>MUIDSI 2026 &nbsp;|&nbsp; 3,222 US Counties &nbsp;|&nbsp; 66 Features &nbsp;|&nbsp; 19 MCP Tools &nbsp;|&nbsp; 7 Federal Data Sources</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    if df is None:
        st.error("Data not found. Run the pipeline first: `python run_pipeline.py`")
        return

    model, scaler, le, feature_names = load_model()

    # ── Sidebar ───────────────────────────────────────────────────────
    st.sidebar.markdown("### ResilienceAI")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filters**")

    # State filter
    if "county_name" in df.columns:
        states = sorted(df["county_name"].str.extract(r", (\w+)$")[0].dropna().unique())
        selected_states = st.sidebar.multiselect("States", states, default=[])
        if selected_states:
            pattern = "|".join([f", {s}$" for s in selected_states])
            df_filtered = df[df["county_name"].str.contains(pattern, regex=True, na=False)]
        else:
            df_filtered = df
    else:
        df_filtered = df

    # Risk level filter
    risk_levels = st.sidebar.multiselect("Risk Level", ["Low", "Medium", "High"],
                                         default=["Low", "Medium", "High"])
    if "risk_level" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["risk_level"].isin(risk_levels)]

    # Population filter
    if "total_population" in df_filtered.columns:
        pop_min = int(df_filtered["total_population"].min())
        pop_max = int(df_filtered["total_population"].max())
        pop_range = st.sidebar.slider("Population Range",
                                       pop_min, min(pop_max, 1000000),
                                       (pop_min, min(pop_max, 1000000)))
        df_filtered = df_filtered[
            (df_filtered["total_population"] >= pop_range[0]) &
            (df_filtered["total_population"] <= pop_range[1])
        ]

    st.sidebar.markdown(f"**Showing {len(df_filtered):,} of {len(df):,} counties**")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Data Sources**")
    st.sidebar.caption("FEMA OpenData | CMS Medicare | US Census ACS | FEMA ArcGIS Hub")

    # ── Tabs ──────────────────────────────────────────────────────────
    (tab_overview, tab_map, tab_3d, tab_scenario, tab_infra, tab_insights,
     tab_gaps, tab_alerts, tab_benchmark, tab_model, tab_agent) = st.tabs([
        "Overview", "Risk Map", "3D Tower Map", "Scenario Sim",
        "Infrastructure", "Advanced Insights", "Gap Analysis",
        "Alert Center", "Benchmarking",
        "Model Performance", "Agent Query"
    ])

    # ── Tab: Overview ─────────────────────────────────────────────────
    with tab_overview:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Counties Analyzed", f"{len(df_filtered):,}")
        with col2:
            if "risk_score" in df_filtered.columns:
                st.metric("Avg Risk Score", f"{df_filtered['risk_score'].mean():.3f}")
        with col3:
            if "risk_level" in df_filtered.columns:
                high_risk = (df_filtered["risk_level"] == "High").sum()
                st.metric("High Risk Counties", f"{high_risk:,}")
        with col4:
            if "disaster_count" in df_filtered.columns:
                st.metric("Total Disasters", f"{df_filtered['disaster_count'].sum():,.0f}")

        st.markdown("---")

        # Risk distribution
        col1, col2 = st.columns(2)
        with col1:
            if "risk_score" in df_filtered.columns:
                fig = px.histogram(df_filtered, x="risk_score", nbins=50,
                                   color="risk_level",
                                   color_discrete_map={"Low": "#27ae60", "Medium": "#f39c12", "High": "#e74c3c"},
                                   title="Risk Score Distribution")
                fig.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "risk_level" in df_filtered.columns:
                counts = df_filtered["risk_level"].value_counts().reindex(["Low", "Medium", "High"])
                fig = px.pie(values=counts.values, names=counts.index,
                             color=counts.index,
                             color_discrete_map={"Low": "#27ae60", "Medium": "#f39c12", "High": "#e74c3c"},
                             title="Risk Level Distribution")
                fig.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

        # Top risk counties table
        st.subheader("Top 20 Highest Risk Counties")
        display_cols = ["county_name", "risk_score", "risk_level", "total_population",
                        "poverty_pct", "elderly_pct", "disaster_count", "vulnerability_index"]
        display_cols = [c for c in display_cols if c in df_filtered.columns]
        top_risk = df_filtered.nlargest(20, "risk_score")[display_cols] if "risk_score" in df_filtered.columns else df_filtered.head(20)
        st.dataframe(style_risk_table(top_risk, display_cols), use_container_width=True, hide_index=True)

    # ── Tab: Risk Map ─────────────────────────────────────────────────
    with tab_map:
        st.subheader("Geographic Risk Map")

        if "latitude" in df_filtered.columns and "longitude" in df_filtered.columns:
            map_df = df_filtered.dropna(subset=["latitude", "longitude", "risk_score"])
            # Continental US filter
            map_df = map_df[
                (map_df["latitude"] > 24) & (map_df["latitude"] < 50) &
                (map_df["longitude"] > -130) & (map_df["longitude"] < -65)
            ]

            if len(map_df) > 0:
                fig = px.scatter_mapbox(
                    map_df, lat="latitude", lon="longitude",
                    color="risk_score", size="total_population" if "total_population" in map_df.columns else None,
                    color_continuous_scale="RdYlGn_r",
                    hover_name="county_name" if "county_name" in map_df.columns else None,
                    hover_data={"risk_score": ":.3f", "risk_level": True,
                                "disaster_count": True, "poverty_pct": ":.1f"},
                    mapbox_style="carto-darkmatter",
                    zoom=3, center={"lat": 39.5, "lon": -98.35},
                    title="County-Level Disaster Vulnerability",
                    height=600,
                    size_max=15,
                )
                fig.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True, config=MAPBOX_CONFIG)
            else:
                st.warning("No counties with valid coordinates in current filter.")
        else:
            st.warning("Geographic data not available.")

    # ── Tab: 3D Tower Map ──────────────────────────────────────────────
    with tab_3d:
        st.subheader("🗼 3D Vulnerability Tower Map")
        
        if HAS_ADVANCED_VIZ and "latitude" in df_filtered.columns:
            viz = Visualization3D(df_filtered)
            
            if len(viz.df) > 0:
                # View selection
                view_col1, view_col2 = st.columns([3, 2])
                with view_col1:
                    viz_mode = st.selectbox(
                        "Visualization Mode",
                        ["County Heatmap", "County Scatter Map", "State Choropleth", "Regional Hexbins"],
                        key="viz_mode"
                    )
                with view_col2:
                    st.markdown("##### Legend")
                    st.markdown("🟢 Low Risk (< 0.33)")
                    st.markdown("🟡 Medium Risk (0.33 - 0.67)")
                    st.markdown("🔴 High Risk (> 0.67)")
                
                st.markdown("---")
                
                # Render selected visualization
                if viz_mode == "County Heatmap":
                    fig = viz.create_county_heatmap()
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Could not create heatmap.")
                    
                    with st.expander("📊 Heatmap Guide", expanded=False):
                        st.markdown("""
                        **County-Level Risk Heatmap**
                        - **Color intensity** shows risk concentration
                        - **Brighter/Redder** = Higher risk areas
                        - **Zoom in** to see county-level details
                        - **Hover** for exact risk scores
                        """)
                        
                elif viz_mode == "County Scatter Map":
                    fig = viz.create_county_scatter_map()
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Could not create scatter map.")
                    
                    with st.expander("📊 Scatter Map Guide", expanded=False):
                        st.markdown("""
                        **County Scatter Map**
                        - **Each dot** = one county
                        - **Color** = Risk score (Green→Yellow→Red)
                        - **Size** = Population (larger = more populous)
                        - **State borders** shown as blue lines
                        """)
                        
                elif viz_mode == "State Choropleth":
                    fig = viz.create_state_choropleth()
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Could not create choropleth.")
                    
                    with st.expander("📊 Choropleth Guide", expanded=False):
                        st.markdown("""
                        **State-Level Average Risk**
                        - **Color** = Average risk score across all counties in state
                        - **Hover** for exact values and county counts
                        - Good for high-level regional comparison
                        """)
                        
                elif viz_mode == "Regional Hexbins":
                    fig = viz.create_hexbin_map()
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Could not create hexbin map.")
                    
                    with st.expander("📊 Hexbin Guide", expanded=False):
                        st.markdown("""
                        **Regional Risk Hexbins**
                        - **Hexagons** aggregate nearby counties
                        - **Color** = Average risk in that region
                        - Good for identifying regional patterns
                        """)
                
                # Stats summary
                st.markdown("---")
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                with stats_col1:
                    st.metric("Counties Shown", len(viz.df))
                with stats_col2:
                    high_risk_count = len(viz.df[viz.df["risk_score"] > 0.67])
                    st.metric("High Risk Counties", high_risk_count)
                with stats_col3:
                    avg_risk = viz.df["risk_score"].mean()
                    st.metric("Average Risk", f"{avg_risk:.3f}")
                    
            else:
                st.warning("No counties with valid coordinates in current filter.")
                
        elif not HAS_ADVANCED_VIZ:
            st.info("Install required packages: `pip install pydeck plotly scipy`")
        else:
            st.warning("Geographic data not available.")

    # ── Tab: Scenario Simulation ──────────────────────────────────────
    with tab_scenario:
        st.subheader("Disaster Scenario Simulation")
        st.markdown("Simulate what-if disaster scenarios and see before/after risk impact.")

        from src.scenario_simulator import ScenarioSimulator, SCENARIO_PRESETS
        sim = ScenarioSimulator(df)

        col1, col2, col3 = st.columns(3)
        with col1:
            scenario_key = st.selectbox("Scenario Type",
                list(SCENARIO_PRESETS.keys()),
                format_func=lambda k: SCENARIO_PRESETS[k]["label"])
        with col2:
            # Pick epicenter county
            county_options = df_filtered.sort_values("risk_score", ascending=False)["county_name"].head(200).tolist()
            epicenter_county = st.selectbox("Epicenter County", county_options)
        with col3:
            custom_radius = st.number_input("Custom Radius (km)", min_value=10, max_value=500,
                                             value=SCENARIO_PRESETS[scenario_key]["radius_km"])

        if st.button("Run Simulation", type="primary"):
            # Find FIPS for selected county
            epic_match = df[df["county_name"] == epicenter_county]
            if not epic_match.empty:
                epic_fips = epic_match.iloc[0]["fips"]
                result = sim.simulate(scenario_key, epicenter_fips=epic_fips,
                                       custom_radius_km=custom_radius)

                if "error" in result:
                    st.error(result["error"])
                else:
                    s = result["summary"]

                    # Summary metrics
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    with mc1:
                        st.metric("Counties Affected", f"{s['counties_affected']:,}")
                    with mc2:
                        st.metric("Population at Risk", f"{s['total_population_at_risk']:,}")
                    with mc3:
                        st.metric("Avg Risk Before", f"{s['avg_risk_before']:.3f}")
                    with mc4:
                        st.metric("Avg Risk After", f"{s['avg_risk_after']:.3f}",
                                  delta=f"+{s['risk_increase_pct']:.1f}%")

                    st.markdown(f"**{s['counties_escalated']}** counties escalated to higher risk level. "
                                f"Max infrastructure damage: **{s['max_infrastructure_damage_pct']:.1f}%**")

                    # Affected counties table
                    st.markdown("#### Most Affected Counties")
                    top_df = pd.DataFrame(result["top_affected_counties"])
                    if len(top_df) > 0:
                        st.dataframe(style_risk_table(top_df), use_container_width=True, hide_index=True)

                    # Before/after visualization
                    affected = result.get("affected_df")
                    if affected is not None and len(affected) > 0:
                        fig = go.Figure()
                        top_vis = affected.nlargest(20, "impact_factor")
                        fig.add_trace(go.Bar(name="Before", x=top_vis["county_name"],
                                             y=top_vis["risk_score_before"],
                                             marker_color="#4FC3F7"))
                        fig.add_trace(go.Bar(name="After", x=top_vis["county_name"],
                                             y=top_vis["risk_score_after"],
                                             marker_color="#e74c3c"))
                        fig.update_layout(barmode="group", title="Before vs After Risk Scores",
                                          xaxis_tickangle=-45, **PLOTLY_LAYOUT)
                        st.plotly_chart(fig, use_container_width=True)

    # ── Tab: Infrastructure ───────────────────────────────────────────
    with tab_infra:
        st.subheader("Infrastructure Access Analysis")

        dist_cols = [c for c in df_filtered.columns if c.startswith("dist_nearest_")]
        if dist_cols:
            col1, col2 = st.columns(2)
            with col1:
                selected_facility = st.selectbox("Facility Type",
                    [c.replace("dist_nearest_", "").replace("_km", "").replace("_", " ").title()
                     for c in dist_cols])
                col_name = f"dist_nearest_{'_'.join(selected_facility.lower().split())}_km"

                if col_name in df_filtered.columns:
                    fig = px.histogram(df_filtered, x=col_name, nbins=50,
                                       title=f"Distance to Nearest {selected_facility}",
                                       labels={col_name: "Distance (km)"})
                    fig.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Infrastructure gap: counties > 50km from nearest facility
                if col_name in df_filtered.columns:
                    gaps = df_filtered[df_filtered[col_name] > 50]
                    st.metric(f"Counties > 50km from {selected_facility}", len(gaps))

                    if len(gaps) > 0:
                        gap_display = gaps.nlargest(10, col_name)[["county_name", col_name, "total_population", "risk_score"]]
                        st.dataframe(
                            style_risk_table(gap_display),
                            use_container_width=True, hide_index=True
                        )

        # Vulnerability scatter
        st.subheader("Vulnerability vs Infrastructure Access")
        if "vulnerability_index" in df_filtered.columns and "isolation_index" in df_filtered.columns:
            fig = px.scatter(
                df_filtered, x="isolation_index", y="vulnerability_index",
                color="risk_level",
                color_discrete_map={"Low": "#27ae60", "Medium": "#f39c12", "High": "#e74c3c"},
                hover_name="county_name" if "county_name" in df_filtered.columns else None,
                size="total_population" if "total_population" in df_filtered.columns else None,
                size_max=20,
                title="Vulnerability Index vs Infrastructure Isolation",
                labels={"isolation_index": "Infrastructure Isolation Index",
                        "vulnerability_index": "Demographic Vulnerability Index"},
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab: Advanced Insights ────────────────────────────────────────
    with tab_insights:
        st.subheader("Advanced Risk Analytics")

        # Compound Risk Clusters
        st.markdown("#### Compound Risk Hotspots")
        st.markdown("Counties simultaneously high on 3+ risk dimensions (vulnerability, isolation, disaster exposure, infrastructure deficit)")
        if "compound_risk_count" in df_filtered.columns:
            col1, col2 = st.columns([1, 2])
            with col1:
                compound = df_filtered[df_filtered["compound_risk_flag"] == 1] if "compound_risk_flag" in df_filtered.columns else df_filtered[df_filtered["compound_risk_count"] >= 3]
                st.metric("Compound Risk Counties", len(compound))
                st.metric("Avg Population (compound)", f"{compound['total_population'].mean():,.0f}" if len(compound) > 0 else "N/A")

                # Green-to-red gradient bar chart for compound risk
                risk_counts = df_filtered["compound_risk_count"].value_counts().sort_index()
                max_dims = risk_counts.index.max() if len(risk_counts) > 0 else 4
                colors = []
                for dim in risk_counts.index:
                    t = dim / max(max_dims, 1)
                    r = int(39 + (231 - 39) * t)   # green(39) -> red(231)
                    g = int(174 + (76 - 174) * t)   # green(174) -> red(76)
                    b = int(96 + (60 - 96) * t)     # green(96) -> red(60)
                    colors.append(f"rgb({r},{g},{b})")

                fig = go.Figure(go.Bar(
                    x=risk_counts.index, y=risk_counts.values,
                    marker_color=colors,
                    hovertemplate="Dimensions: %{x}<br>Counties: %{y}<extra></extra>"
                ))
                fig.update_layout(
                    title="Risk Dimensions per County",
                    xaxis_title="# High-Risk Dimensions",
                    yaxis_title="Number of Counties",
                    **PLOTLY_LAYOUT
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Map compound risk counties
                map_df = df_filtered.dropna(subset=["latitude", "longitude"]).copy()
                map_df = map_df[(map_df["latitude"] > 24) & (map_df["latitude"] < 50) &
                                (map_df["longitude"] > -130) & (map_df["longitude"] < -65)]
                if len(map_df) > 0:
                    fig = px.scatter_mapbox(
                        map_df, lat="latitude", lon="longitude",
                        color="compound_risk_count",
                        color_continuous_scale="YlOrRd",
                        hover_name="county_name",
                        hover_data={"compound_risk_count": True, "risk_score": ":.3f"},
                        mapbox_style="carto-darkmatter",
                        zoom=3, center={"lat": 39.5, "lon": -98.35},
                        title="Compound Risk Clusters (3+ dimensions = critical)",
                        height=500, size_max=12,
                    )
                    fig.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig, use_container_width=True, config=MAPBOX_CONFIG)

        st.markdown("---")

        # Disaster Acceleration
        st.markdown("#### Disaster Acceleration Trends")
        st.markdown("Counties where disaster frequency is increasing (2015-2025 vs 2005-2014)")
        if "disaster_acceleration" in df_filtered.columns:
            col1, col2 = st.columns(2)
            with col1:
                accel = df_filtered[df_filtered["disaster_acceleration"] > 1.0]
                st.metric("Counties with Increasing Disasters", len(accel))
                fig = px.histogram(df_filtered[df_filtered["disaster_acceleration"] > 0],
                                   x="disaster_acceleration", nbins=50,
                                   title="Disaster Acceleration Ratio Distribution",
                                   labels={"disaster_acceleration": "Acceleration Ratio (>1 = increasing)"})
                fig.add_vline(x=1.0, line_dash="dash", line_color="#e74c3c", annotation_text="No change",
                              annotation_font_color="#E0E0E0")
                fig.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                # Top accelerating counties
                top_accel = df_filtered.nlargest(15, "disaster_acceleration")
                display = ["county_name", "disaster_acceleration", "disasters_2015_2025",
                           "disasters_2005_2014", "risk_score"]
                display = [c for c in display if c in top_accel.columns]
                st.markdown("**Top 15 Accelerating Counties:**")
                st.dataframe(style_risk_table(top_accel[display], display), use_container_width=True, hide_index=True)

        st.markdown("---")

        # Infrastructure Redundancy
        st.markdown("#### Infrastructure Redundancy & Single Points of Failure")
        if "zero_redundancy_flag" in df_filtered.columns:
            col1, col2 = st.columns(2)
            with col1:
                zero_red = df_filtered[df_filtered["zero_redundancy_flag"] == 1]
                st.metric("Zero-Redundancy Counties", len(zero_red))
                st.markdown("*2nd nearest hospital is >100km away*")
                if len(zero_red) > 0:
                    display = ["county_name", "dist_nearest_hospitals_km", "dist_2nd_nearest_hospitals_km",
                               "redundancy_score", "total_population"]
                    display = [c for c in display if c in zero_red.columns]
                    st.dataframe(style_risk_table(zero_red.nlargest(15, "dist_2nd_nearest_hospitals_km")[display], display),
                                 use_container_width=True, hide_index=True)
            with col2:
                if "redundancy_score" in df_filtered.columns:
                    fig = px.histogram(df_filtered, x="redundancy_score", nbins=50,
                                       title="Infrastructure Redundancy Score Distribution",
                                       labels={"redundancy_score": "Redundancy Score (0=none, 1=high)"},
                                       color_discrete_sequence=["#4FC3F7"])
                    fig.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Risk Contagion
        st.markdown("#### Neighbor Risk Contagion")
        st.markdown("Counties surrounded by high-risk neighbors have limited overflow capacity")
        if "neighbor_avg_risk" in df_filtered.columns and "risk_score" in df_filtered.columns:
            fig = px.scatter(
                df_filtered, x="risk_score", y="neighbor_avg_risk",
                color="risk_level",
                color_discrete_map={"Low": "#27ae60", "Medium": "#f39c12", "High": "#e74c3c"},
                hover_name="county_name",
                title="County Risk vs Neighbor Average Risk",
                labels={"risk_score": "County Risk Score", "neighbor_avg_risk": "Avg Neighbor Risk"},
                opacity=0.6,
            )
            fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                          line=dict(dash="dash", color="#546E7A"))
            fig.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("*Points above the diagonal: neighbors are higher-risk than the county itself (contagion risk)*")

    # ── Tab: Gap Analysis ─────────────────────────────────────────────
    with tab_gaps:
        st.subheader("Intervention Gap Analysis")
        st.markdown("Which single intervention would most reduce each county's risk?")

        if "top_intervention" in df_filtered.columns:
            col1, col2 = st.columns(2)
            with col1:
                # Intervention type distribution
                intervention_counts = df_filtered["top_intervention"].value_counts()
                fig = px.bar(x=intervention_counts.index, y=intervention_counts.values,
                             title="Top Recommended Interventions Across Counties",
                             labels={"x": "Intervention Type", "y": "Number of Counties"},
                             color=intervention_counts.index)
                fig.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Map by intervention type
                map_df = df_filtered.dropna(subset=["latitude", "longitude"]).copy()
                map_df = map_df[(map_df["latitude"] > 24) & (map_df["latitude"] < 50) &
                                (map_df["longitude"] > -130) & (map_df["longitude"] < -65)]
                if len(map_df) > 0:
                    fig = px.scatter_mapbox(
                        map_df, lat="latitude", lon="longitude",
                        color="top_intervention",
                        hover_name="county_name",
                        hover_data={"top_intervention_score": ":.3f", "risk_score": ":.3f"},
                        mapbox_style="carto-darkmatter",
                        zoom=3, center={"lat": 39.5, "lon": -98.35},
                        title="Geographic Distribution of Recommended Interventions",
                        height=500,
                    )
                    fig.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig, use_container_width=True, config=MAPBOX_CONFIG)

            st.markdown("---")

            # Gap dimension breakdown
            st.markdown("#### Gap Score Breakdown")
            gap_cols = [c for c in df_filtered.columns if c.startswith("gap_")]
            if gap_cols:
                # Average gap scores
                avg_gaps = df_filtered[gap_cols].mean().sort_values(ascending=False)
                fig = px.bar(x=avg_gaps.index, y=avg_gaps.values,
                             title="Average Gap Scores by Dimension",
                             labels={"x": "Gap Dimension", "y": "Average Gap Score (0-1)"},
                             color=avg_gaps.index)
                fig.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

            # Filterable table
            st.markdown("#### Counties by Intervention Type")
            intervention_filter = st.selectbox("Filter by intervention:",
                                                ["All"] + list(df_filtered["top_intervention"].unique()))
            table_df = df_filtered if intervention_filter == "All" else df_filtered[df_filtered["top_intervention"] == intervention_filter]
            table_df = table_df.sort_values("top_intervention_score", ascending=False).head(25)
            display = ["county_name", "top_intervention", "top_intervention_score",
                        "risk_score", "total_population"] + gap_cols
            display = [c for c in display if c in table_df.columns]
            st.dataframe(style_risk_table(table_df[display], display), use_container_width=True, hide_index=True)

        # State rankings
        st.markdown("---")
        st.markdown("#### State-Level County Rankings")
        if "risk_score_state_pctile" in df_filtered.columns:
            states_avail = sorted(df_filtered["county_name"].str.extract(r", (\w+)$")[0].dropna().unique())
            rank_state = st.selectbox("Select state:", states_avail, index=0 if states_avail else None)
            if rank_state:
                state_df = df_filtered[df_filtered["county_name"].str.contains(f", {rank_state}$", regex=True, na=False)]
                state_df = state_df.sort_values("risk_score_state_pctile", ascending=False)
                display = ["county_name", "risk_score", "risk_score_state_pctile",
                            "vulnerability_index_state_pctile", "compound_risk_count",
                            "top_intervention", "total_population"]
                display = [c for c in display if c in state_df.columns]
                st.dataframe(style_risk_table(state_df[display], display), use_container_width=True, hide_index=True)

    # ── Tab: Alert Center ─────────────────────────────────────────────
    with tab_alerts:
        st.subheader("Alert Command Center")
        st.markdown("Monitor counties exceeding risk thresholds.")

        alert_col1, alert_col2 = st.columns([1, 3])
        with alert_col1:
            risk_thresh = st.slider("Risk Threshold", 0.0, 1.0, 0.7, 0.05, key="alert_thresh")
            show_critical_only = st.checkbox("Critical Only", value=False)

        with alert_col2:
            from src.agent import ResilienceAgent
            _agent = ResilienceAgent()
            alerts_result = _agent.get_real_time_alerts(
                state=selected_states[0] if selected_states else None,
                risk_threshold=risk_thresh,
            )

            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                st.metric("Total Alerts", alerts_result["total_alerts"])
            with ac2:
                st.metric("Critical", alerts_result["critical_count"])
            with ac3:
                st.metric("Warning", alerts_result["warning_count"])

            for alert in alerts_result["alerts"]:
                if show_critical_only and alert["severity"] != "critical":
                    continue
                severity_colors = {"critical": "#DC2626", "warning": "#F59E0B", "info": "#3B82F6"}
                color = severity_colors.get(alert["severity"], "#3B82F6")
                st.markdown(
                    f'<div style="border-left: 4px solid {color}; padding: 8px 12px; '
                    f'margin: 4px 0; background: rgba(0,0,0,0.2); border-radius: 0 4px 4px 0;">'
                    f'<strong style="color: {color};">[{alert["severity"].upper()}]</strong> '
                    f'<strong>{alert["county_name"]}</strong> '
                    f'(Risk: {alert["risk_score"]:.3f})<br/>'
                    f'<span style="color: #90A4AE;">{alert["reason"]}</span>'
                    f'</div>', unsafe_allow_html=True
                )

    # ── Tab: Benchmarking ─────────────────────────────────────────────
    with tab_benchmark:
        st.subheader("County Benchmarking & Peer Comparison")
        st.markdown("Compare a county against demographically similar peers.")

        bench_counties = df_filtered.sort_values("risk_score", ascending=False)["county_name"].head(200).tolist()
        bench_county = st.selectbox("Select County to Benchmark", bench_counties, key="bench_select")

        if bench_county:
            bench_match = df[df["county_name"] == bench_county]
            if not bench_match.empty:
                from src.agent import ResilienceAgent
                _bench_agent = ResilienceAgent()
                bench_result = _bench_agent.benchmark_county(bench_match.iloc[0]["fips"])

                if "error" in bench_result:
                    st.error(bench_result["error"])
                else:
                    st.markdown(f"**{bench_result['county_name']}** vs **{bench_result['peer_count']}** similar-population peers")
                    st.metric("Overall Peer Percentile", f"{bench_result['overall_peer_percentile']:.1f}%")

                    # Radar chart
                    radar = bench_result["radar_data"]
                    categories = list(radar.keys())
                    county_vals = [radar[c]["percentile"] / 100 for c in categories]
                    peer_vals = [0.5] * len(categories)  # Peer mean = 50th percentile

                    labels = [c.replace("_", " ").title() for c in categories]

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=county_vals + [county_vals[0]],
                        theta=labels + [labels[0]],
                        fill="toself", name=bench_county,
                        fillcolor="rgba(79, 195, 247, 0.2)",
                        line_color="#4FC3F7",
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=peer_vals + [peer_vals[0]],
                        theta=labels + [labels[0]],
                        fill="toself", name="Peer Average",
                        fillcolor="rgba(144, 164, 174, 0.1)",
                        line_color="#546E7A",
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 1]),
                            bgcolor="rgba(0,0,0,0)",
                        ),
                        title=f"Peer Comparison: {bench_county}",
                        **PLOTLY_LAYOUT,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Detail table
                    detail_rows = []
                    for col, data in radar.items():
                        detail_rows.append({
                            "Metric": col.replace("_", " ").title(),
                            "County Value": f"{data['county_value']:.3f}",
                            "Peer Mean": f"{data['peer_mean']:.3f}",
                            "Z-Score": f"{data['z_score']:+.2f}",
                            "Percentile": f"{data['percentile']:.1f}%",
                        })
                    st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

    # ── Tab: Model Performance ────────────────────────────────────────
    with tab_model:
        st.subheader("Model Performance")

        # Show saved figures
        perf_images = [
            ("Model Comparison", "model_comparison.png"),
            ("Confusion Matrices", "confusion_matrices.png"),
            ("ROC Curves", "roc_curves.png"),
            ("Feature Importance (Random Forest)", "feature_importance_random_forest.png"),
            ("Feature Importance (Gradient Boosting)", "feature_importance_gradient_boosting.png"),
        ]

        for title, filename in perf_images:
            img_path = FIGURES_DIR / filename
            if img_path.exists():
                st.image(str(img_path), caption=title, use_container_width=True)

        # Model results table
        results_path = FIGURES_DIR / "model_results_summary.csv"
        if results_path.exists():
            results = pd.read_csv(results_path)
            st.subheader("Model Comparison Summary")
            st.dataframe(results, use_container_width=True, hide_index=True)

    # ── Tab: Agent Query ──────────────────────────────────────────────
    with tab_agent:
        st.subheader("Ask ResilienceAI")
        st.markdown("""
        Ask questions about disaster vulnerability in natural language.
        This interface simulates the Archia-powered agent experience.

        **Example queries:**
        - "Which Missouri counties have the highest disaster risk?"
        - "Compare St. Louis County and Jackson County vulnerability"
        - "What are the most flood-prone areas with poor hospital access?"
        - "Which counties have zero hospital redundancy?"
        - "Where are disasters accelerating fastest?"
        - "What intervention does Jackson County need most?"
        - "Simulate a Category 3 hurricane hitting Miami-Dade"
        - "What's the ROI of building a hospital in rural Kansas?"
        - "Show me equity gaps in disaster vulnerability"
        - "Benchmark Cook County against its peers"
        """)

        query = st.text_input("Your question:", placeholder="e.g., Show me high-risk counties in Missouri")

        if query and df is not None:
            st.markdown("---")
            # Simple keyword-based query processing (demo mode)
            response = process_demo_query(query, df)
            st.markdown(response)

    # ── Footer ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="footer-badge">
        ResilienceAI &nbsp;|&nbsp; MUIDSI 2026 &nbsp;|&nbsp; Built on 100% real federal data
    </div>
    """, unsafe_allow_html=True)


def process_demo_query(query, df):
    """Simple keyword-based query processor for demo purposes."""
    query_lower = query.lower()
    results = df.copy()

    # State detection
    state_abbrevs = {
        "missouri": "MO", "california": "CA", "texas": "TX", "florida": "FL",
        "new york": "NY", "illinois": "IL", "ohio": "OH", "georgia": "GA",
        "pennsylvania": "PA", "north carolina": "NC", "michigan": "MI",
        "kansas": "KS", "arkansas": "AR", "oklahoma": "OK", "iowa": "IA",
        "nebraska": "NE", "louisiana": "LA", "mississippi": "MS",
        "alabama": "AL", "tennessee": "TN", "kentucky": "KY",
    }
    detected_state = None
    for state_name, abbrev in state_abbrevs.items():
        if state_name in query_lower or abbrev.lower() in query_lower.split():
            detected_state = abbrev
            results = results[results["county_name"].str.contains(f", {abbrev}", na=False)]
            break

    # Risk level detection
    if "high risk" in query_lower or "highest risk" in query_lower or "most vulnerable" in query_lower:
        results = results.sort_values("risk_score", ascending=False)
    elif "low risk" in query_lower or "safest" in query_lower:
        results = results.sort_values("risk_score", ascending=True)

    # Disaster type detection
    for dtype in ["flood", "tornado", "hurricane", "fire", "storm"]:
        if dtype in query_lower:
            col = f"disaster_{dtype}"
            if col in results.columns:
                results = results[results[col] > 0].sort_values(col, ascending=False)

    # Advanced feature queries
    if "redundancy" in query_lower or "single point" in query_lower or "zero redundancy" in query_lower:
        if "zero_redundancy_flag" in results.columns:
            results = results[results["zero_redundancy_flag"] == 1].sort_values("dist_2nd_nearest_hospitals_km", ascending=False)
            display_cols = ["county_name", "dist_nearest_hospitals_km", "dist_2nd_nearest_hospitals_km",
                            "redundancy_score", "total_population", "risk_score"]
            display_cols = [c for c in display_cols if c in results.columns]
            top = results.head(15)
            return f"**Zero-Redundancy Counties** (2nd hospital >100km):\n\n{top[display_cols].to_markdown(index=False)}\n\n**{len(results)} total counties** with zero hospital redundancy."

    if "accelerat" in query_lower or "increasing disaster" in query_lower or "disaster trend" in query_lower:
        if "disaster_acceleration" in results.columns:
            results = results[results["disaster_acceleration"] > 1.5].sort_values("disaster_acceleration", ascending=False)
            display_cols = ["county_name", "disaster_acceleration", "disasters_2015_2025",
                            "disasters_2005_2014", "risk_score"]
            display_cols = [c for c in display_cols if c in results.columns]
            top = results.head(15)
            return f"**Counties with Accelerating Disasters:**\n\n{top[display_cols].to_markdown(index=False)}"

    if "intervention" in query_lower or "gap" in query_lower or "what does" in query_lower and "need" in query_lower:
        if "top_intervention" in results.columns:
            results = results.sort_values("top_intervention_score", ascending=False)
            display_cols = ["county_name", "top_intervention", "top_intervention_score", "risk_score"]
            display_cols = [c for c in display_cols if c in results.columns]
            top = results.head(15)
            return f"**Top Recommended Interventions:**\n\n{top[display_cols].to_markdown(index=False)}"

    if "compound" in query_lower or "hotspot" in query_lower or "multiple risk" in query_lower:
        if "compound_risk_count" in results.columns:
            results = results[results["compound_risk_count"] >= 3].sort_values("compound_risk_count", ascending=False)
            display_cols = ["county_name", "compound_risk_count", "risk_score", "vulnerability_index",
                            "isolation_index", "disaster_count"]
            display_cols = [c for c in display_cols if c in results.columns]
            top = results.head(15)
            return f"**Compound Risk Hotspots** (3+ risk dimensions):\n\n{top[display_cols].to_markdown(index=False)}"

    # Compare detection
    if "compare" in query_lower:
        # Try to extract county names
        parts = query_lower.replace("compare", "").replace(" and ", ",").split(",")
        compare_results = []
        for part in parts:
            part = part.strip()
            if part:
                match = df[df["county_name"].str.contains(part, case=False, na=False)]
                if not match.empty:
                    compare_results.append(match.iloc[0])
        if compare_results:
            comp_df = pd.DataFrame(compare_results)
            display_cols = ["county_name", "risk_score", "risk_level", "total_population",
                            "vulnerability_index", "isolation_index", "disaster_count",
                            "poverty_pct", "elderly_pct"]
            display_cols = [c for c in display_cols if c in comp_df.columns]
            return f"**Comparison Results:**\n\n{comp_df[display_cols].to_markdown(index=False)}"

    # Format response
    top = results.head(10)
    if len(top) == 0:
        return "No counties found matching your query. Try a broader search."

    state_label = f" in {detected_state}" if detected_state else ""
    display_cols = ["county_name", "risk_score", "risk_level", "total_population",
                    "disaster_count", "poverty_pct", "elderly_pct"]
    display_cols = [c for c in display_cols if c in top.columns]

    response = f"**Top results{state_label}:**\n\n"
    response += top[display_cols].to_markdown(index=False)

    # Add summary
    if "risk_score" in top.columns:
        response += f"\n\n**Summary:** Average risk score: {top['risk_score'].mean():.3f}"
    if "total_population" in top.columns:
        response += f" | Total population affected: {top['total_population'].sum():,.0f}"

    return response


if __name__ == "__main__":
    main()
