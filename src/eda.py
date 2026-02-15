"""
ResilienceAI - Exploratory Data Analysis
Generates distributions, correlation heatmaps, and geographic visualizations.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from config import PROCESSED_DIR, RAW_DIR, FIGURES_DIR


def plot_risk_distribution(df):
    """Plot distribution of risk scores and levels."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Risk score histogram
    axes[0].hist(df["risk_score"].dropna(), bins=50, color="#e74c3c", edgecolor="white", alpha=0.8)
    axes[0].set_xlabel("Risk Score", fontsize=12)
    axes[0].set_ylabel("County Count", fontsize=12)
    axes[0].set_title("Distribution of Disaster Vulnerability Risk Scores", fontsize=13)
    axes[0].axvline(df["risk_score"].mean(), color="black", linestyle="--", label=f"Mean: {df['risk_score'].mean():.3f}")
    axes[0].legend()

    # Risk level bar chart
    if "risk_level" in df.columns:
        counts = df["risk_level"].value_counts().reindex(["Low", "Medium", "High"])
        colors = ["#27ae60", "#f39c12", "#e74c3c"]
        counts.plot(kind="bar", ax=axes[1], color=colors, edgecolor="white")
        axes[1].set_xlabel("Risk Level", fontsize=12)
        axes[1].set_ylabel("County Count", fontsize=12)
        axes[1].set_title("Counties by Risk Level", fontsize=13)
        axes[1].tick_params(axis="x", rotation=0)

        # Add count labels
        for i, (idx, val) in enumerate(counts.items()):
            if pd.notna(val):
                axes[1].text(i, val + 10, str(int(val)), ha="center", fontweight="bold")

    plt.tight_layout()
    path = FIGURES_DIR / "risk_distribution.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


def plot_vulnerability_components(df):
    """Plot demographic vulnerability component distributions."""
    cols = ["elderly_pct", "poverty_pct", "disability_pct", "uninsured_pct"]
    cols = [c for c in cols if c in df.columns]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    titles = {
        "elderly_pct": "Elderly Population (65+) %",
        "poverty_pct": "Poverty Rate %",
        "disability_pct": "Disability Rate %",
        "uninsured_pct": "Uninsured Rate %",
    }
    colors = ["#3498db", "#e67e22", "#9b59b6", "#1abc9c"]

    for i, col in enumerate(cols):
        ax = axes[i]
        data = df[col].dropna()
        ax.hist(data, bins=40, color=colors[i], edgecolor="white", alpha=0.8)
        ax.set_xlabel(titles.get(col, col), fontsize=11)
        ax.set_ylabel("County Count", fontsize=11)
        ax.set_title(titles.get(col, col), fontsize=12)
        ax.axvline(data.mean(), color="black", linestyle="--",
                   label=f"Mean: {data.mean():.1f}%")
        ax.axvline(data.median(), color="gray", linestyle=":",
                   label=f"Median: {data.median():.1f}%")
        ax.legend(fontsize=9)

    plt.suptitle("Demographic Vulnerability Components", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    path = FIGURES_DIR / "vulnerability_components.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


def plot_facility_distances(df):
    """Plot distributions of nearest-facility distances."""
    dist_cols = [c for c in df.columns if c.startswith("dist_nearest_") and c.endswith("_km")]

    if not dist_cols:
        print("  [SKIP] No distance columns found")
        return

    fig, axes = plt.subplots(1, len(dist_cols), figsize=(5 * len(dist_cols), 5))
    if len(dist_cols) == 1:
        axes = [axes]

    for i, col in enumerate(dist_cols):
        name = col.replace("dist_nearest_", "").replace("_km", "").replace("_", " ").title()
        data = df[col].dropna()
        # Cap at 99th percentile for visualization
        cap = data.quantile(0.99)
        axes[i].hist(data.clip(upper=cap), bins=40, color="#2c3e50", edgecolor="white", alpha=0.8)
        axes[i].set_xlabel("Distance (km)", fontsize=11)
        axes[i].set_ylabel("County Count", fontsize=11)
        axes[i].set_title(f"Distance to Nearest {name}", fontsize=12)
        axes[i].axvline(data.median(), color="#e74c3c", linestyle="--",
                       label=f"Median: {data.median():.1f} km")
        axes[i].legend(fontsize=9)

    plt.suptitle("Infrastructure Access: Distance to Nearest Facility", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    path = FIGURES_DIR / "facility_distances.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


def plot_correlation_heatmap(df):
    """Plot correlation heatmap of key features."""
    feature_cols = [c for c in df.columns if any(
        c.startswith(p) for p in ["dist_", "count_", "density_", "disaster_",
                                  "elderly", "poverty", "disability", "uninsured",
                                  "vulnerability", "isolation", "risk_score",
                                  "total_population", "median_income"]
    )]
    feature_cols = [c for c in feature_cols if df[c].dtype in ["float64", "int64", "float32", "int32"]]

    if len(feature_cols) < 3:
        print("  [SKIP] Too few numeric features for heatmap")
        return

    corr = df[feature_cols].corr()

    fig, ax = plt.subplots(figsize=(16, 12))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, square=True, linewidths=0.5, ax=ax,
                annot_kws={"size": 7}, vmin=-1, vmax=1)
    ax.set_title("Feature Correlation Matrix", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = FIGURES_DIR / "correlation_heatmap.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


def plot_disaster_frequency(df):
    """Plot disaster frequency distribution and top counties."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Distribution
    data = df["disaster_count"].dropna()
    axes[0].hist(data, bins=50, color="#8e44ad", edgecolor="white", alpha=0.8)
    axes[0].set_xlabel("Total Disaster Declarations", fontsize=11)
    axes[0].set_ylabel("County Count", fontsize=11)
    axes[0].set_title("Disaster Declaration Frequency by County", fontsize=12)
    axes[0].axvline(data.mean(), color="black", linestyle="--",
                   label=f"Mean: {data.mean():.1f}")
    axes[0].legend()

    # Top 20 counties
    top = df.nlargest(20, "disaster_count")[["county_name", "disaster_count"]]
    axes[1].barh(range(len(top)), top["disaster_count"].values, color="#8e44ad", alpha=0.8)
    axes[1].set_yticks(range(len(top)))
    axes[1].set_yticklabels(top["county_name"].str[:30].values, fontsize=8)
    axes[1].set_xlabel("Total Disaster Declarations", fontsize=11)
    axes[1].set_title("Top 20 Most Disaster-Affected Counties", fontsize=12)
    axes[1].invert_yaxis()

    plt.tight_layout()
    path = FIGURES_DIR / "disaster_frequency.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


def plot_geographic_scatter(df):
    """Plot geographic scatter of risk scores across US."""
    fig, ax = plt.subplots(figsize=(16, 10))

    valid = df.dropna(subset=["latitude", "longitude", "risk_score"])
    # Filter to continental US
    valid = valid[
        (valid["latitude"] > 24) & (valid["latitude"] < 50) &
        (valid["longitude"] > -130) & (valid["longitude"] < -65)
    ]

    scatter = ax.scatter(
        valid["longitude"], valid["latitude"],
        c=valid["risk_score"], cmap="RdYlGn_r",
        s=8, alpha=0.7, edgecolors="none"
    )
    plt.colorbar(scatter, ax=ax, label="Risk Score", shrink=0.6)
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    ax.set_title("Disaster Vulnerability Risk by County (Continental US)", fontsize=14, fontweight="bold")
    ax.set_facecolor("#f0f0f0")

    plt.tight_layout()
    path = FIGURES_DIR / "geographic_risk_map.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


def generate_summary_stats(df):
    """Generate and save summary statistics."""
    stats = df.describe().round(3)
    stats_path = FIGURES_DIR / "summary_statistics.csv"
    stats.to_csv(stats_path)
    print(f"  Saved: {stats_path.name}")

    # Print key insights
    print("\n  Key Insights:")
    print(f"    Total counties: {len(df)}")
    if "risk_score" in df.columns:
        print(f"    Risk score range: {df['risk_score'].min():.3f} - {df['risk_score'].max():.3f}")
        print(f"    Mean risk score: {df['risk_score'].mean():.3f}")
    if "disaster_count" in df.columns:
        print(f"    Max disasters (single county): {df['disaster_count'].max()}")
        print(f"    Counties with 0 disasters: {(df['disaster_count'] == 0).sum()}")
    if "total_population" in df.columns:
        print(f"    Total US population covered: {df['total_population'].sum():,.0f}")


def run_eda():
    """Run full EDA pipeline."""
    print("=" * 60)
    print("ResilienceAI - Exploratory Data Analysis")
    print("=" * 60)

    # Load processed features
    features_path = PROCESSED_DIR / "county_features.csv"
    if not features_path.exists():
        print("ERROR: county_features.csv not found. Run feature engineering first.")
        return

    df = pd.read_csv(features_path, dtype={"fips": str})
    print(f"\nLoaded {len(df)} counties with {len(df.columns)} features\n")

    print("Generating visualizations...")
    plot_risk_distribution(df)
    plot_vulnerability_components(df)
    plot_facility_distances(df)
    plot_correlation_heatmap(df)
    plot_disaster_frequency(df)
    plot_geographic_scatter(df)
    generate_summary_stats(df)

    print(f"\n{'=' * 60}")
    print(f"EDA complete! All figures saved to {FIGURES_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    run_eda()
