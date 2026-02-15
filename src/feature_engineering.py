"""
ResilienceAI - Feature Engineering Pipeline
Creates 15+ features from raw data for disaster vulnerability modeling.
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
    """Compute distance from each county centroid to nearest facility."""
    # Filter facilities with valid coordinates
    fac = facility_df.dropna(subset=["latitude", "longitude"])
    if len(fac) == 0:
        county_df[f"dist_nearest_{facility_name}_km"] = np.nan
        county_df[f"count_{facility_name}_50km"] = 0
        return county_df

    # Build KD-tree from facility coordinates (convert to radians for tree)
    fac_coords = np.radians(fac[["latitude", "longitude"]].values)
    tree = cKDTree(fac_coords)

    county_coords = np.radians(county_df[["latitude", "longitude"]].values)

    # Query nearest
    dists, indices = tree.query(county_coords, k=1)
    # Convert radian distance to km (approximate using Earth radius)
    county_df[f"dist_nearest_{facility_name}_km"] = dists * 6371.0

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
