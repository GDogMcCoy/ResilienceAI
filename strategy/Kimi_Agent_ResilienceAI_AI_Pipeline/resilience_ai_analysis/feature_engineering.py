"""
ResilienceAI - Feature Engineering Pipeline
Creates 40+ features from raw data for disaster vulnerability modeling.
Includes 7 advanced differentiator features for agentic AI insight exploration.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from pathlib import Path
from config import RAW_DIR, PROCESSED_DIR, COL_FIPS, FOCUS_STATES


# ── Spatial Distance Calculations ─────────────────────────────────────
def haversine_km(lat1, lon1, lat2, lon2):
    """Vectorized haversine distance in km."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


def nearest_facility_distance(county_df, facility_df, facility_name):
    """Compute distance from each county centroid to nearest (and 2nd nearest) facility."""
    # Filter facilities with valid coordinates
    fac = facility_df.dropna(subset=["latitude", "longitude"])
    if len(fac) == 0:
        county_df[f"dist_nearest_{facility_name}_km"] = np.nan
        county_df[f"dist_2nd_nearest_{facility_name}_km"] = np.nan
        county_df[f"count_{facility_name}_50km"] = 0
        return county_df

    # Build KD-tree from facility coordinates (convert to radians for tree)
    fac_coords = np.radians(fac[["latitude", "longitude"]].values)
    tree = cKDTree(fac_coords)

    county_coords = np.radians(county_df[["latitude", "longitude"]].values)

    # Query nearest 2 for redundancy scoring
    k = min(2, len(fac))
    dists, indices = tree.query(county_coords, k=k)
    if k == 1:
        county_df[f"dist_nearest_{facility_name}_km"] = dists * 6371.0
        county_df[f"dist_2nd_nearest_{facility_name}_km"] = np.nan
    else:
        county_df[f"dist_nearest_{facility_name}_km"] = dists[:, 0] * 6371.0
        county_df[f"dist_2nd_nearest_{facility_name}_km"] = dists[:, 1] * 6371.0

    # Count facilities within 50km
    counts = tree.query_ball_point(county_coords, r=50 / 6371.0)
    county_df[f"count_{facility_name}_50km"] = [len(c) for c in counts]

    return county_df


# ── FEMA Disaster Features ────────────────────────────────────────────
def compute_disaster_features(county_df, fema_df):
    """Compute disaster frequency and type features per county FIPS."""
    print("  Computing disaster features...")

    # Standardize FIPS in FEMA data
    if "fipsStateCode" in fema_df.columns and "fipsCountyCode" in fema_df.columns:
        fema_df["fips"] = (
            fema_df["fipsStateCode"].astype(str).str.zfill(2)
            + fema_df["fipsCountyCode"].astype(str).str.zfill(3)
        )

    # Total disaster count per county
    disaster_counts = fema_df.groupby("fips").size().reset_index(name="disaster_count")
    county_df = county_df.merge(disaster_counts, on="fips", how="left")
    county_df["disaster_count"] = county_df["disaster_count"].fillna(0).astype(int)

    # Disaster type breakdown
    if "incidentType" in fema_df.columns:
        type_counts = fema_df.groupby(["fips", "incidentType"]).size().unstack(fill_value=0)
        # Top disaster types
        for dtype in ["Flood", "Severe Storm(s)", "Hurricane", "Fire", "Tornado"]:
            col_name = f"disaster_{dtype.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
            if dtype in type_counts.columns:
                county_df = county_df.merge(
                    type_counts[[dtype]].rename(columns={dtype: col_name}).reset_index(),
                    on="fips", how="left"
                )
                county_df[col_name] = county_df[col_name].fillna(0).astype(int)
            else:
                county_df[col_name] = 0

    # Recent disasters (last 10 years)
    if "declarationDate" in fema_df.columns:
        fema_df["year"] = pd.to_datetime(fema_df["declarationDate"], errors="coerce").dt.year
        recent = fema_df[fema_df["year"] >= 2015]
        recent_counts = recent.groupby("fips").size().reset_index(name="disaster_count_recent")
        county_df = county_df.merge(recent_counts, on="fips", how="left")
        county_df["disaster_count_recent"] = county_df["disaster_count_recent"].fillna(0).astype(int)

    return county_df


# ── Vulnerability Composite Index ─────────────────────────────────────
def compute_vulnerability_index(df):
    """Create composite vulnerability index from demographic factors."""
    print("  Computing vulnerability composite index...")

    components = []
    for col in ["elderly_pct", "poverty_pct", "disability_pct", "uninsured_pct"]:
        if col in df.columns:
            # Min-max normalize each component
            vals = df[col].fillna(0)
            vmin, vmax = vals.min(), vals.max()
            if vmax > vmin:
                normalized = (vals - vmin) / (vmax - vmin)
            else:
                normalized = pd.Series(0.0, index=df.index)
            components.append(normalized)

    if components:
        df["vulnerability_index"] = sum(components) / len(components)
    else:
        df["vulnerability_index"] = 0.0

    return df


# ── Infrastructure Density ────────────────────────────────────────────
def compute_infrastructure_density(df):
    """Compute facilities per 10k population."""
    print("  Computing infrastructure density...")

    facility_cols = [c for c in df.columns if c.startswith("count_") and c.endswith("_50km")]
    for col in facility_cols:
        name = col.replace("count_", "").replace("_50km", "")
        density_col = f"density_{name}_per10k"
        pop = df["total_population"].replace(0, np.nan)
        df[density_col] = (df[col] / pop * 10000).round(4)

    return df


# ── Spatial Isolation ─────────────────────────────────────────────────
def compute_isolation_index(df):
    """Compute spatial isolation: avg distance to all facility types."""
    print("  Computing isolation index...")
    dist_cols = [c for c in df.columns if c.startswith("dist_nearest_") and c.endswith("_km")]
    if dist_cols:
        # Normalize each distance column, then average
        normalized = []
        for col in dist_cols:
            vals = df[col].fillna(df[col].max())
            vmin, vmax = vals.min(), vals.max()
            if vmax > vmin:
                normalized.append((vals - vmin) / (vmax - vmin))
        if normalized:
            df["isolation_index"] = sum(normalized) / len(normalized)
        else:
            df["isolation_index"] = 0.0
    else:
        df["isolation_index"] = 0.0
    return df


# ── Composite Risk Score (Target Variable) ────────────────────────────
def compute_risk_score(df):
    """
    Compute composite risk score as target variable.
    Combines vulnerability, infrastructure gaps, and disaster exposure.
    """
    print("  Computing composite risk score (target)...")

    components = {}

    # Vulnerability (40% weight)
    if "vulnerability_index" in df.columns:
        components["vulnerability"] = df["vulnerability_index"] * 0.40

    # Infrastructure gap / isolation (30% weight)
    if "isolation_index" in df.columns:
        components["isolation"] = df["isolation_index"] * 0.30

    # Disaster exposure (30% weight)
    if "disaster_count" in df.columns:
        dc = df["disaster_count"].fillna(0)
        dc_norm = (dc - dc.min()) / (dc.max() - dc.min() + 1e-10)
        components["disaster"] = dc_norm * 0.30

    raw_score = sum(components.values())

    # Normalize risk score to 0-1 range using min-max
    score_min = raw_score.min()
    score_max = raw_score.max()
    if score_max > score_min:
        df["risk_score"] = ((raw_score - score_min) / (score_max - score_min)).round(4)
    else:
        df["risk_score"] = 0.5

    # Classify into risk levels using tercile-based thresholds
    low_thresh = df["risk_score"].quantile(0.33)
    high_thresh = df["risk_score"].quantile(0.67)
    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-0.01, low_thresh, high_thresh, 1.01],
        labels=["Low", "Medium", "High"]
    )

    return df


# ── ADVANCED FEATURE 1: Compound Risk Clusters ───────────────────────
def compute_compound_risk_clusters(df):
    """
    Identify counties that are HIGH on 3+ risk dimensions simultaneously.
    Dimensions: vulnerability, isolation, disaster exposure, infrastructure deficit.
    Outputs a compound_risk_count (0-4) and boolean compound_risk_flag.
    """
    print("  [ADV] Computing compound risk clusters...")
    dims = []
    for col in ["vulnerability_index", "isolation_index"]:
        if col in df.columns:
            dims.append(df[col] >= df[col].quantile(0.75))
    if "disaster_count" in df.columns:
        dims.append(df["disaster_count"] >= df["disaster_count"].quantile(0.75))
    # Infrastructure deficit = low facility density
    density_cols = [c for c in df.columns if c.startswith("density_") and c.endswith("_per10k")]
    if density_cols:
        avg_density = df[density_cols].mean(axis=1)
        dims.append(avg_density <= avg_density.quantile(0.25))

    if dims:
        df["compound_risk_count"] = sum(d.astype(int) for d in dims)
        df["compound_risk_flag"] = (df["compound_risk_count"] >= 3).astype(int)
    else:
        df["compound_risk_count"] = 0
        df["compound_risk_flag"] = 0
    print(f"    Compound risk counties (3+ dims): {df['compound_risk_flag'].sum()}")
    return df


# ── ADVANCED FEATURE 2: Nearest-Neighbor Risk Contagion ──────────────
def compute_risk_contagion(df):
    """
    For each county, compute the average risk_score of its K nearest
    geographic neighbors. If your neighbors are all high-risk, overflow
    capacity is limited -> contagion effect.
    """
    print("  [ADV] Computing risk contagion from neighbors...")
    valid = df.dropna(subset=["latitude", "longitude", "risk_score"])
    if len(valid) < 5:
        df["neighbor_avg_risk"] = np.nan
        df["risk_contagion_delta"] = 0.0
        return df

    coords = np.radians(valid[["latitude", "longitude"]].values)
    tree = cKDTree(coords)
    K = 5
    dists, indices = tree.query(coords, k=K + 1)  # +1 because self is included

    neighbor_risk = np.array([
        valid["risk_score"].iloc[idx[1:]].mean() for idx in indices
    ])
    df.loc[valid.index, "neighbor_avg_risk"] = np.round(neighbor_risk, 4)
    df.loc[valid.index, "risk_contagion_delta"] = np.round(
        neighbor_risk - valid["risk_score"].values, 4
    )
    # Fill any missing
    df["neighbor_avg_risk"] = df["neighbor_avg_risk"].fillna(df["risk_score"])
    df["risk_contagion_delta"] = df["risk_contagion_delta"].fillna(0.0)
    print(f"    Mean contagion delta: {df['risk_contagion_delta'].mean():.4f}")
    return df


# ── ADVANCED FEATURE 3: Temporal Disaster Acceleration ───────────────
def compute_disaster_acceleration(df, fema_df):
    """
    Compare disaster frequency in recent decade (2015-2025) vs prior decade
    (2005-2014). Acceleration ratio > 1 means disasters are increasing.
    """
    print("  [ADV] Computing temporal disaster acceleration...")
    if "fipsStateCode" in fema_df.columns and "fipsCountyCode" in fema_df.columns:
        fema_df = fema_df.copy()
        fema_df["fips"] = (
            fema_df["fipsStateCode"].astype(str).str.zfill(2)
            + fema_df["fipsCountyCode"].astype(str).str.zfill(3)
        )
    fema_df = fema_df.copy()
    fema_df["year"] = pd.to_datetime(fema_df["declarationDate"], errors="coerce").dt.year

    recent = fema_df[(fema_df["year"] >= 2015) & (fema_df["year"] <= 2025)]
    prior = fema_df[(fema_df["year"] >= 2005) & (fema_df["year"] <= 2014)]

    recent_ct = recent.groupby("fips").size().reset_index(name="disasters_2015_2025")
    prior_ct = prior.groupby("fips").size().reset_index(name="disasters_2005_2014")

    df = df.merge(recent_ct, on="fips", how="left")
    df = df.merge(prior_ct, on="fips", how="left")
    df["disasters_2015_2025"] = df["disasters_2015_2025"].fillna(0)
    df["disasters_2005_2014"] = df["disasters_2005_2014"].fillna(0)

    # Acceleration ratio (add 1 to denominator to avoid div/0)
    df["disaster_acceleration"] = np.round(
        df["disasters_2015_2025"] / (df["disasters_2005_2014"] + 1), 4
    )
    accelerating = (df["disaster_acceleration"] > 1.0).sum()
    print(f"    Counties with accelerating disasters: {accelerating}")
    return df


# ── ADVANCED FEATURE 4: Infrastructure Redundancy Score ──────────────
def compute_infrastructure_redundancy(df):
    """
    How far is the 2nd-nearest facility? If it's very far, there's zero
    redundancy: one facility failure = complete loss of access.
    """
    print("  [ADV] Computing infrastructure redundancy...")
    dist2_cols = [c for c in df.columns if c.startswith("dist_2nd_nearest_")]
    if not dist2_cols:
        df["redundancy_score"] = 0.5
        df["zero_redundancy_flag"] = 0
        return df

    # Normalize each 2nd-nearest distance and average (inverted: low distance = high redundancy)
    normalized = []
    for col in dist2_cols:
        vals = df[col].fillna(df[col].max())
        vmin, vmax = vals.min(), vals.max()
        if vmax > vmin:
            normalized.append(1.0 - (vals - vmin) / (vmax - vmin))
    if normalized:
        df["redundancy_score"] = np.round(sum(normalized) / len(normalized), 4)
    else:
        df["redundancy_score"] = 0.5

    # Zero redundancy: 2nd nearest hospital is > 100km away
    hosp_col = "dist_2nd_nearest_hospitals_km"
    if hosp_col in df.columns:
        df["zero_redundancy_flag"] = (df[hosp_col].fillna(999) > 100).astype(int)
    else:
        df["zero_redundancy_flag"] = 0
    print(f"    Zero-redundancy counties (2nd hospital >100km): {df['zero_redundancy_flag'].sum()}")
    return df


# ── ADVANCED FEATURE 5: Population-Weighted Vulnerability ────────────
def compute_population_weighted(df):
    """
    Weight vulnerability by population so the agent can prioritize
    interventions by total lives impacted, not just per-capita rates.
    """
    print("  [ADV] Computing population-weighted vulnerability...")
    pop = df["total_population"].fillna(0)

    if "vulnerability_index" in df.columns:
        df["pop_weighted_vulnerability"] = np.round(
            df["vulnerability_index"] * pop, 2
        )
    if "risk_score" in df.columns:
        df["pop_weighted_risk"] = np.round(df["risk_score"] * pop, 2)

    # Normalize to 0-1 for comparability
    for col in ["pop_weighted_vulnerability", "pop_weighted_risk"]:
        if col in df.columns:
            vals = df[col]
            vmin, vmax = vals.min(), vals.max()
            if vmax > vmin:
                df[f"{col}_norm"] = np.round((vals - vmin) / (vmax - vmin), 4)
    print(f"    Top pop-weighted county: {df.nlargest(1, 'pop_weighted_risk')[['fips', 'county_name', 'pop_weighted_risk']].to_string(index=False)}")
    return df


# ── ADVANCED FEATURE 6: State-Level Ranking ──────────────────────────
def compute_state_rankings(df):
    """
    Percentile rank within own state for risk_score and vulnerability.
    Enables agent to say 'worst county in Texas' or 'top 10% in Florida'.
    """
    print("  [ADV] Computing state-level rankings...")
    df["state_fips"] = df["fips"].str[:2]

    for metric in ["risk_score", "vulnerability_index", "isolation_index"]:
        if metric in df.columns:
            col_name = f"{metric}_state_pctile"
            df[col_name] = df.groupby("state_fips")[metric].rank(pct=True).round(4)

    # Count of counties per state for context
    state_sizes = df.groupby("state_fips").size().reset_index(name="counties_in_state")
    df = df.merge(state_sizes, on="state_fips", how="left")
    print(f"    States covered: {df['state_fips'].nunique()}")
    return df


# ── ADVANCED FEATURE 7: Gap Analysis Matrix ──────────────────────────
def compute_gap_analysis(df):
    """
    For each county, estimate which single intervention would most
    reduce its risk score. Categories: add_hospital, add_ems, add_fire,
    reduce_poverty, disaster_prep.
    """
    print("  [ADV] Computing gap analysis matrix...")

    # Score each gap dimension (higher = bigger gap = more impact from fixing)
    gap_cols = {}

    # Hospital gap: normalized distance to nearest hospital
    if "dist_nearest_hospitals_km" in df.columns:
        vals = df["dist_nearest_hospitals_km"].fillna(0)
        vmin, vmax = vals.min(), vals.max()
        gap_cols["gap_hospital"] = (vals - vmin) / (vmax - vmin + 1e-10)

    # EMS gap
    if "dist_nearest_ems_stations_km" in df.columns:
        vals = df["dist_nearest_ems_stations_km"].fillna(0)
        vmin, vmax = vals.min(), vals.max()
        gap_cols["gap_ems"] = (vals - vmin) / (vmax - vmin + 1e-10)

    # Fire station gap
    if "dist_nearest_fire_stations_km" in df.columns:
        vals = df["dist_nearest_fire_stations_km"].fillna(0)
        vmin, vmax = vals.min(), vals.max()
        gap_cols["gap_fire"] = (vals - vmin) / (vmax - vmin + 1e-10)

    # Poverty gap (vulnerability driver)
    if "poverty_pct" in df.columns:
        vals = df["poverty_pct"].fillna(0)
        vmin, vmax = vals.min(), vals.max()
        gap_cols["gap_poverty"] = (vals - vmin) / (vmax - vmin + 1e-10)

    # Disaster preparedness gap (high disaster count + low recent response)
    if "disaster_count" in df.columns:
        vals = df["disaster_count"].fillna(0)
        vmin, vmax = vals.min(), vals.max()
        gap_cols["gap_disaster_prep"] = (vals - vmin) / (vmax - vmin + 1e-10)

    for col_name, series in gap_cols.items():
        df[col_name] = np.round(series, 4)

    # Determine the top intervention per county
    if gap_cols:
        gap_df = pd.DataFrame(gap_cols, index=df.index)
        df["top_intervention"] = gap_df.idxmax(axis=1).str.replace("gap_", "add_", 1)
        df["top_intervention_score"] = np.round(gap_df.max(axis=1), 4)
        print(f"    Top interventions distribution:")
        print(f"    {df['top_intervention'].value_counts().to_string()}")
    else:
        df["top_intervention"] = "unknown"
        df["top_intervention_score"] = 0.0

    return df


# ── Main Pipeline ─────────────────────────────────────────────────────
def run_feature_engineering():
    """Run the full feature engineering pipeline."""
    print("=" * 60)
    print("ResilienceAI - Feature Engineering Pipeline")
    print("=" * 60)

    # Load raw data
    print("\nLoading raw data...")
    census = pd.read_csv(RAW_DIR / "census_demographics.csv", dtype={"fips": str})
    centroids = pd.read_csv(RAW_DIR / "county_centroids.csv", dtype={"fips": str})
    fema = pd.read_csv(RAW_DIR / "fema_disasters.csv")

    # Merge census with centroids
    df = census.merge(centroids[["fips", "latitude", "longitude"]], on="fips", how="left")
    print(f"  Base counties: {len(df)}")

    # Filter to focus states if configured
    if FOCUS_STATES:
        state_fips = df["fips"].str[:2]
        # Would need state FIPS mapping - skip for now
        pass

    # Drop counties without coordinates
    df = df.dropna(subset=["latitude", "longitude"])
    print(f"  Counties with coordinates: {len(df)}")

    # Compute facility distances for each HIFLD layer
    print("\nComputing facility distances...")
    for facility_type in ["hospitals", "fire_stations", "ems_stations", "nursing_homes"]:
        csv_path = RAW_DIR / f"hifld_{facility_type}.csv"
        if csv_path.exists():
            fac_df = pd.read_csv(csv_path)
            df = nearest_facility_distance(df, fac_df, facility_type)
            print(f"  {facility_type}: distance + count features added")
        else:
            print(f"  [SKIP] {facility_type} data not found")

    # FEMA disaster features
    df = compute_disaster_features(df, fema)

    # Vulnerability composite
    df = compute_vulnerability_index(df)

    # Infrastructure density
    df = compute_infrastructure_density(df)

    # Spatial isolation
    df = compute_isolation_index(df)

    # Risk score (target variable)
    df = compute_risk_score(df)

    # ── Advanced Differentiator Features ──────────────────────────────
    print("\nComputing advanced differentiator features...")

    # ADV 1: Compound Risk Clusters
    df = compute_compound_risk_clusters(df)

    # ADV 2: Risk Contagion (needs risk_score computed first)
    df = compute_risk_contagion(df)

    # ADV 3: Temporal Disaster Acceleration
    df = compute_disaster_acceleration(df, fema)

    # ADV 4: Infrastructure Redundancy (uses 2nd-nearest distances)
    df = compute_infrastructure_redundancy(df)

    # ADV 5: Population-Weighted Vulnerability
    df = compute_population_weighted(df)

    # ADV 6: State-Level Rankings
    df = compute_state_rankings(df)

    # ADV 7: Gap Analysis Matrix
    df = compute_gap_analysis(df)

    # Save processed dataset
    output_path = PROCESSED_DIR / "county_features.csv"
    df.to_csv(output_path, index=False)

    print(f"\n{'=' * 60}")
    print(f"Feature engineering complete!")
    print(f"  Counties: {len(df)}")
    print(f"  Features: {len(df.columns)}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Risk distribution:")
    if "risk_level" in df.columns:
        print(df["risk_level"].value_counts().to_string())
    print(f"  Output: {output_path}")
    print(f"{'=' * 60}")

    return df


if __name__ == "__main__":
    run_feature_engineering()
