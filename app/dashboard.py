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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Risk Map", "Infrastructure", "Model Performance", "Agent Query"
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
