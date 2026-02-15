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

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResilienceAI - Disaster Vulnerability Assessment",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


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


def main():
    # Header
    st.title("ResilienceAI")
    st.markdown("### Disaster Vulnerability & Health Infrastructure Gap Assessment")
    st.markdown("---")

    df = load_data()
    if df is None:
        st.error("Data not found. Run the pipeline first: `python run_pipeline.py`")
        return

    model, scaler, le, feature_names = load_model()

    # Sidebar filters
    st.sidebar.header("Filters")

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

    # ── Tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab6, tab7, tab4, tab5 = st.tabs([
        "Overview", "Risk Map", "Infrastructure",
        "Advanced Insights", "Gap Analysis",
        "Model Performance", "Agent Query"
    ])

    # ── Tab 1: Overview ───────────────────────────────────────────────
    with tab1:
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
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "risk_level" in df_filtered.columns:
                counts = df_filtered["risk_level"].value_counts().reindex(["Low", "Medium", "High"])
                fig = px.pie(values=counts.values, names=counts.index,
                             color=counts.index,
                             color_discrete_map={"Low": "#27ae60", "Medium": "#f39c12", "High": "#e74c3c"},
                             title="Risk Level Distribution")
                st.plotly_chart(fig, use_container_width=True)

        # Top risk counties table
        st.subheader("Top 20 Highest Risk Counties")
        display_cols = ["county_name", "risk_score", "risk_level", "total_population",
                        "poverty_pct", "elderly_pct", "disaster_count", "vulnerability_index"]
        display_cols = [c for c in display_cols if c in df_filtered.columns]
        top_risk = df_filtered.nlargest(20, "risk_score")[display_cols] if "risk_score" in df_filtered.columns else df_filtered.head(20)
        st.dataframe(top_risk, use_container_width=True, hide_index=True)

    # ── Tab 2: Risk Map ───────────────────────────────────────────────
    with tab2:
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
                    mapbox_style="carto-positron",
                    zoom=3, center={"lat": 39.5, "lon": -98.35},
                    title="County-Level Disaster Vulnerability",
                    height=600,
                    size_max=15,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No counties with valid coordinates in current filter.")
        else:
            st.warning("Geographic data not available.")

    # ── Tab 3: Infrastructure ─────────────────────────────────────────
    with tab3:
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
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Infrastructure gap: counties > 50km from nearest facility
                if col_name in df_filtered.columns:
                    gaps = df_filtered[df_filtered[col_name] > 50]
                    st.metric(f"Counties > 50km from {selected_facility}", len(gaps))

                    if len(gaps) > 0:
                        st.dataframe(
                            gaps.nlargest(10, col_name)[["county_name", col_name, "total_population", "risk_score"]],
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
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab 6: Advanced Insights ──────────────────────────────────────
    with tab6:
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

                # Distribution of compound risk counts
                fig = px.histogram(df_filtered, x="compound_risk_count",
                                   title="Risk Dimensions per County",
                                   labels={"compound_risk_count": "# High-Risk Dimensions"},
                                   color_discrete_sequence=["#e74c3c"])
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
                        mapbox_style="carto-positron",
                        zoom=3, center={"lat": 39.5, "lon": -98.35},
                        title="Compound Risk Clusters (3+ dimensions = critical)",
                        height=500, size_max=12,
                    )
                    st.plotly_chart(fig, use_container_width=True)

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
                fig.add_vline(x=1.0, line_dash="dash", line_color="red", annotation_text="No change")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                # Top accelerating counties
                top_accel = df_filtered.nlargest(15, "disaster_acceleration")
                display = ["county_name", "disaster_acceleration", "disasters_2015_2025",
                           "disasters_2005_2014", "risk_score"]
                display = [c for c in display if c in top_accel.columns]
                st.markdown("**Top 15 Accelerating Counties:**")
                st.dataframe(top_accel[display], use_container_width=True, hide_index=True)

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
                    st.dataframe(zero_red.nlargest(15, "dist_2nd_nearest_hospitals_km")[display],
                                 use_container_width=True, hide_index=True)
            with col2:
                if "redundancy_score" in df_filtered.columns:
                    fig = px.histogram(df_filtered, x="redundancy_score", nbins=50,
                                       title="Infrastructure Redundancy Score Distribution",
                                       labels={"redundancy_score": "Redundancy Score (0=none, 1=high)"},
                                       color_discrete_sequence=["#3498db"])
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
                          line=dict(dash="dash", color="gray"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("*Points above the diagonal: neighbors are higher-risk than the county itself (contagion risk)*")

    # ── Tab 7: Gap Analysis ────────────────────────────────────────────
    with tab7:
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
                        mapbox_style="carto-positron",
                        zoom=3, center={"lat": 39.5, "lon": -98.35},
                        title="Geographic Distribution of Recommended Interventions",
                        height=500,
                    )
                    st.plotly_chart(fig, use_container_width=True)

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
            st.dataframe(table_df[display], use_container_width=True, hide_index=True)

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
                st.dataframe(state_df[display], use_container_width=True, hide_index=True)

    # ── Tab 4: Model Performance ──────────────────────────────────────
    with tab4:
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

    # ── Tab 5: Agent Query ────────────────────────────────────────────
    with tab5:
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
        """)

        query = st.text_input("Your question:", placeholder="e.g., Show me high-risk counties in Missouri")

        if query and df is not None:
            st.markdown("---")
            # Simple keyword-based query processing (demo mode)
            response = process_demo_query(query, df)
            st.markdown(response)


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
