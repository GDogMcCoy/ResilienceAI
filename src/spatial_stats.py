"""
ResilienceAI - Spatial Statistics Module
Spatial autocorrelation and hotspot analysis for vulnerability data.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.stats import norm
from config import PROCESSED_DIR


class SpatialAnalyzer:
    """Spatial statistics for disaster vulnerability analysis."""

    def __init__(self, df=None):
        if df is None:
            path = PROCESSED_DIR / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
            else:
                self.df = None
        else:
            self.df = df

    def _build_distance_matrix(self, coords, max_dist_km=100):
        """Build distance matrix and weight matrix for spatial analysis."""
        # Convert to radians for haversine
        R = 6371  # Earth radius in km
        lat_rad = np.radians(coords[:, 0])
        lon_rad = np.radians(coords[:, 1])

        # Haversine distance matrix
        n = len(coords)
        dist_matrix = np.zeros((n, n))

        for i in range(n):
            dlat = lat_rad - lat_rad[i]
            dlon = lon_rad - lon_rad[i]
            a = np.sin(dlat/2)**2 + np.cos(lat_rad) * np.cos(lat_rad[i]) * np.sin(dlon/2)**2
            dist_matrix[i] = R * 2 * np.arcsin(np.sqrt(a))

        # Binary weights (1 if within max_dist_km, 0 otherwise)
        w = (dist_matrix <= max_dist_km).astype(float)
        np.fill_diagonal(w, 0)  # No self-weight

        # Row-standardize weights
        row_sums = w.sum(axis=1)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        w = w / row_sums[:, np.newaxis]

        return dist_matrix, w

    def morans_i(self, variable, max_dist_km=100):
        """
        Calculate Moran's I for spatial autocorrelation.

        Moran's I ranges from -1 (dispersed) to 1 (clustered).
        Values near 0 indicate random spatial distribution.

        Args:
            variable: Column name to analyze
            max_dist_km: Distance threshold for neighborhood (default 100km)

        Returns:
            dict with Moran's I statistic, z-score, and p-value
        """
        if self.df is None:
            return {"error": "Data not loaded"}

        if variable not in self.df.columns:
            return {"error": f"Variable {variable} not found"}

        # Get valid data
        data = self.df[["latitude", "longitude", variable]].dropna()
        if len(data) < 10:
            return {"error": "Insufficient data for spatial analysis"}

        coords = data[["latitude", "longitude"]].values
        y = data[variable].values

        # Standardize variable
        y_std = (y - y.mean()) / y.std()

        # Build weight matrix
        _, w = self._build_distance_matrix(coords, max_dist_km)

        n = len(y_std)

        # Calculate Moran's I
        numerator = 0
        denominator = np.sum(y_std ** 2)

        for i in range(n):
            for j in range(n):
                numerator += w[i, j] * y_std[i] * y_std[j]

        # Row-standardized weights sum to n, so divide by n
        I = (n / w.sum()) * (numerator / denominator)

        # Expected value under null hypothesis
        E_I = -1 / (n - 1)

        # Variance under null (simplified - assumes normality)
        S1 = np.sum((w + w.T) ** 2) / 2
        S2 = np.sum((w.sum(axis=1) + w.sum(axis=0)) ** 2)
        S3 = np.sum(y_std ** 4) / (np.sum(y_std ** 2) ** 2)

        var_I = (n * S1 - S2) / ((n - 1) * (n - 2) * (n - 3)) * (n * S3 - 3)
        var_I += (S1 - S2) / ((n - 1) * (n - 2) * (n - 3)) * (n - 1)

        # Z-score
        z_score = (I - E_I) / np.sqrt(var_I)

        # Two-tailed p-value
        p_value = 2 * (1 - norm.cdf(abs(z_score)))

        # Interpretation
        if p_value > 0.05:
            interpretation = "No significant spatial autocorrelation (random distribution)"
        elif I > 0:
            interpretation = "Significant spatial clustering (similar values near each other)"
        else:
            interpretation = "Significant spatial dispersion (dissimilar values near each other)"

        return {
            "variable": variable,
            "morans_i": round(I, 4),
            "expected_i": round(E_I, 4),
            "variance": round(var_I, 6),
            "z_score": round(z_score, 4),
            "p_value": round(p_value, 6),
            "significant": p_value < 0.05,
            "interpretation": interpretation,
            "n_counties": n,
            "neighborhood_radius_km": max_dist_km,
            "spatial_pattern": "clustered" if I > 0.1 and p_value < 0.05 else
                              "dispersed" if I < -0.1 and p_value < 0.05 else
                              "random"
        }

    def getis_ord_gi(self, variable, max_dist_km=100):
        """
        Calculate Getis-Ord Gi* hotspot analysis.

        Identifies statistically significant spatial clusters (hotspots and coldspots).
        High positive z-scores indicate hotspots (high values clustered).
        High negative z-scores indicate coldspots (low values clustered).

        Args:
            variable: Column name to analyze
            max_dist_km: Distance threshold for neighborhood

        Returns:
            DataFrame with Gi* statistics for each county
        """
        if self.df is None:
            return {"error": "Data not loaded"}

        if variable not in self.df.columns:
            return {"error": f"Variable {variable} not found"}

        # Get valid data with indices
        data = self.df[["fips", "county_name", "latitude", "longitude", variable]].copy()
        data = data.dropna()

        if len(data) < 10:
            return {"error": "Insufficient data for hotspot analysis"}

        coords = data[["latitude", "longitude"]].values
        y = data[variable].values
        n = len(y)

        # Build weight matrix (not row-standardized for Gi*)
        _, w_dist = self._build_distance_matrix(coords, max_dist_km)
        w = (w_dist > 0).astype(float)  # Binary weights
        np.fill_diagonal(w, 0)

        # Global statistics
        y_mean = y.mean()
        y_var = y.var()

        # Calculate Gi* for each location
        results = []
        for i in range(n):
            # Sum of weighted values (including self)
            w_ii = 1  # Include self
            sum_w = w[i].sum() + w_ii
            sum_wy = np.sum(w[i] * y) + w_ii * y[i]

            # Expected value
            E_G = sum_w * y_mean

            # Variance
            S = np.sqrt(y_var)
            var_G = S**2 * (n * sum_w - sum_w**2) / (n - 1)

            # Gi* statistic
            Gi_star = sum_wy

            # Z-score
            if var_G > 0:
                z_score = (Gi_star - E_G) / np.sqrt(var_G)
            else:
                z_score = 0

            # Classification
            if z_score >= 2.58:
                classification = "Hotspot (99% confidence)"
            elif z_score >= 1.96:
                classification = "Hotspot (95% confidence)"
            elif z_score <= -2.58:
                classification = "Coldspot (99% confidence)"
            elif z_score <= -1.96:
                classification = "Coldspot (95% confidence)"
            else:
                classification = "Not significant"

            results.append({
                "fips": data.iloc[i]["fips"],
                "county_name": data.iloc[i]["county_name"],
                "value": float(y[i]),
                "gi_star": round(Gi_star, 4),
                "z_score": round(z_score, 4),
                "classification": classification,
                "is_hotspot": z_score >= 1.96,
                "is_coldspot": z_score <= -1.96,
            })

        return pd.DataFrame(results)

    def spatial_summary(self, variables=None, max_dist_km=100):
        """
        Generate spatial statistics summary for multiple variables.

        Args:
            variables: List of variables to analyze (default: key risk metrics)
            max_dist_km: Neighborhood radius

        Returns:
            dict with Moran's I for each variable
        """
        if self.df is None:
            return {"error": "Data not loaded"}

        if variables is None:
            variables = ["risk_score", "vulnerability_index", "isolation_index",
                        "poverty_pct", "disaster_count"]

        results = {}
        for var in variables:
            if var in self.df.columns:
                results[var] = self.morans_i(var, max_dist_km)

        return results

    def find_spatial_clusters(self, variable="risk_score", max_dist_km=100, min_cluster_size=3):
        """
        Identify spatial clusters using Gi* hotspot analysis.

        Args:
            variable: Variable to analyze
            max_dist_km: Neighborhood radius
            min_cluster_size: Minimum counties to form a cluster

        Returns:
            dict with hotspot and coldspot counties grouped by proximity
        """
        gi_results = self.getis_ord_gi(variable, max_dist_km)

        if isinstance(gi_results, dict) and "error" in gi_results:
            return gi_results

        # Get significant hotspots and coldspots
        hotspots = gi_results[gi_results["is_hotspot"]]
        coldspots = gi_results[gi_results["is_coldspot"]]

        return {
            "variable": variable,
            "total_counties": len(gi_results),
            "hotspot_count": len(hotspots),
            "coldspot_count": len(coldspots),
            "hotspots": hotspots.sort_values("z_score", ascending=False).to_dict("records"),
            "coldspots": coldspots.sort_values("z_score").to_dict("records"),
            "analysis_parameters": {
                "neighborhood_radius_km": max_dist_km,
                "min_cluster_size": min_cluster_size
            }
        }


def main():
    """CLI for spatial analysis."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Spatial statistics for ResilienceAI")
    parser.add_argument("--moran", metavar="VAR", help="Calculate Moran's I for variable")
    parser.add_argument("--hotspots", metavar="VAR", help="Getis-Ord Gi* hotspot analysis")
    parser.add_argument("--radius", type=float, default=100, help="Neighborhood radius in km")
    parser.add_argument("--summary", action="store_true", help="Summary for all key variables")
    parser.add_argument("--output", "-o", help="Output JSON file")

    args = parser.parse_args()

    analyzer = SpatialAnalyzer()

    if analyzer.df is None:
        print("Error: County data not found. Run pipeline first.")
        return

    results = {}

    if args.moran:
        results = analyzer.morans_i(args.moran, args.radius)
    elif args.hotspots:
        df = analyzer.getis_ord_gi(args.hotspots, args.radius)
        if isinstance(df, pd.DataFrame):
            results = df.to_dict("records")
        else:
            results = df
    elif args.summary:
        results = analyzer.spatial_summary(max_dist_km=args.radius)
    else:
        print("Usage: python spatial_stats.py --moran risk_score | --hotspots risk_score | --summary")
        return

    if "error" in results:
        print(f"Error: {results['error']}")
        return

    output = json.dumps(results, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
