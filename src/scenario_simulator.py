"""
ResilienceAI - Disaster Scenario Simulation Engine
Provides what-if analysis for disaster impact on counties.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from config import PROCESSED_DIR


# Scenario presets: (risk_multiplier, damage_pct, affected_radius_km)
SCENARIO_PRESETS = {
    "hurricane_cat1": {"label": "Hurricane Category 1", "risk_mult": 1.3, "damage_pct": 0.15, "radius_km": 150},
    "hurricane_cat3": {"label": "Hurricane Category 3", "risk_mult": 1.8, "damage_pct": 0.35, "radius_km": 200},
    "hurricane_cat5": {"label": "Hurricane Category 5", "risk_mult": 2.5, "damage_pct": 0.60, "radius_km": 300},
    "earthquake_m6":  {"label": "Earthquake M6.0", "risk_mult": 2.0, "damage_pct": 0.40, "radius_km": 80},
    "earthquake_m7":  {"label": "Earthquake M7.0", "risk_mult": 3.0, "damage_pct": 0.65, "radius_km": 150},
    "flood_major":    {"label": "Major Flood", "risk_mult": 2.2, "damage_pct": 0.45, "radius_km": 100},
    "wildfire_large":  {"label": "Large Wildfire", "risk_mult": 1.9, "damage_pct": 0.30, "radius_km": 60},
    "tornado_ef3":    {"label": "EF3 Tornado", "risk_mult": 2.8, "damage_pct": 0.55, "radius_km": 30},
    "tornado_ef5":    {"label": "EF5 Tornado", "risk_mult": 3.5, "damage_pct": 0.80, "radius_km": 50},
    "winter_storm":   {"label": "Severe Winter Storm", "risk_mult": 1.5, "damage_pct": 0.20, "radius_km": 250},
}


def haversine_km(lat1, lon1, lat2, lon2):
    """Vectorized haversine distance in km."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


class ScenarioSimulator:
    """Simulate disaster scenarios and compute before/after impact."""

    def __init__(self, df=None):
        if df is None:
            path = PROCESSED_DIR / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
            else:
                self.df = None
        else:
            self.df = df

    def get_presets(self):
        """Return available scenario presets."""
        return {k: v["label"] for k, v in SCENARIO_PRESETS.items()}

    def simulate(self, scenario_key, epicenter_fips=None, epicenter_lat=None,
                 epicenter_lon=None, custom_radius_km=None, custom_multiplier=None):
        """
        Run a scenario simulation.

        Args:
            scenario_key: Key from SCENARIO_PRESETS
            epicenter_fips: FIPS code for epicenter county (alternative to lat/lon)
            epicenter_lat/lon: Epicenter coordinates
            custom_radius_km: Override default radius
            custom_multiplier: Override default risk multiplier

        Returns:
            dict with before/after comparison, affected counties, summary stats
        """
        if self.df is None:
            return {"error": "Data not loaded"}

        preset = SCENARIO_PRESETS.get(scenario_key)
        if preset is None:
            return {"error": f"Unknown scenario: {scenario_key}. Available: {list(SCENARIO_PRESETS.keys())}"}

        radius = custom_radius_km or preset["radius_km"]
        multiplier = custom_multiplier or preset["risk_mult"]
        damage_pct = preset["damage_pct"]

        # Resolve epicenter
        if epicenter_fips:
            match = self.df[self.df["fips"] == str(epicenter_fips)]
            if match.empty:
                return {"error": f"County FIPS {epicenter_fips} not found"}
            epicenter_lat = match.iloc[0]["latitude"]
            epicenter_lon = match.iloc[0]["longitude"]
        elif epicenter_lat is None or epicenter_lon is None:
            return {"error": "Provide epicenter_fips or epicenter_lat/lon"}

        # Compute distances from epicenter
        df = self.df.dropna(subset=["latitude", "longitude"]).copy()
        df["dist_to_epicenter_km"] = haversine_km(
            epicenter_lat, epicenter_lon,
            df["latitude"].values, df["longitude"].values
        )

        # Determine affected counties (within radius)
        affected = df[df["dist_to_epicenter_km"] <= radius].copy()
        unaffected = df[df["dist_to_epicenter_km"] > radius].copy()

        if len(affected) == 0:
            return {"error": "No counties within scenario radius"}

        # Compute impact with distance decay
        # Counties closer to epicenter get higher multiplier
        affected["impact_factor"] = 1.0 - (affected["dist_to_epicenter_km"] / radius)
        affected["impact_factor"] = affected["impact_factor"].clip(0, 1)

        # Before scores
        affected["risk_score_before"] = affected["risk_score"]
        affected["risk_level_before"] = affected["risk_level"]

        # After scores: apply multiplier with distance decay
        affected["risk_score_after"] = (
            affected["risk_score"] * (1 + (multiplier - 1) * affected["impact_factor"])
        ).clip(0, 1)

        # Estimate infrastructure damage
        affected["infrastructure_damage_pct"] = (
            damage_pct * affected["impact_factor"] * 100
        ).round(1)

        # Estimate population at risk
        affected["population_at_risk"] = (
            affected["total_population"] * affected["impact_factor"]
        ).astype(int)

        # New risk levels
        low_thresh = self.df["risk_score"].quantile(0.33)
        high_thresh = self.df["risk_score"].quantile(0.67)
        affected["risk_level_after"] = pd.cut(
            affected["risk_score_after"],
            bins=[-0.01, low_thresh, high_thresh, 1.01],
            labels=["Low", "Medium", "High"]
        )

        # Risk level changes
        affected["risk_escalated"] = affected["risk_level_before"] != affected["risk_level_after"]

        # Summary
        summary = {
            "scenario": preset["label"],
            "scenario_key": scenario_key,
            "epicenter_lat": float(epicenter_lat),
            "epicenter_lon": float(epicenter_lon),
            "radius_km": radius,
            "risk_multiplier": multiplier,
            "damage_pct": damage_pct,
            "counties_affected": len(affected),
            "total_population_at_risk": int(affected["population_at_risk"].sum()),
            "avg_risk_before": float(affected["risk_score_before"].mean()),
            "avg_risk_after": float(affected["risk_score_after"].mean()),
            "risk_increase_pct": float(
                (affected["risk_score_after"].mean() - affected["risk_score_before"].mean())
                / (affected["risk_score_before"].mean() + 1e-10) * 100
            ),
            "counties_escalated": int(affected["risk_escalated"].sum()),
            "max_infrastructure_damage_pct": float(affected["infrastructure_damage_pct"].max()),
        }

        # Top affected counties
        top_affected = affected.nlargest(15, "impact_factor")
        display_cols = ["fips", "county_name", "risk_score_before", "risk_score_after",
                        "risk_level_before", "risk_level_after", "infrastructure_damage_pct",
                        "population_at_risk", "dist_to_epicenter_km"]
        display_cols = [c for c in display_cols if c in top_affected.columns]
        top_counties = top_affected[display_cols].round(3).to_dict(orient="records")

        return {
            "summary": summary,
            "top_affected_counties": top_counties,
            "affected_df": affected,  # Full dataframe for visualization
            "unaffected_df": unaffected,
        }

    def compare_scenarios(self, scenarios, epicenter_fips):
        """Compare multiple scenarios for the same epicenter."""
        results = {}
        for key in scenarios:
            results[key] = self.simulate(key, epicenter_fips=epicenter_fips)
        return results


if __name__ == "__main__":
    sim = ScenarioSimulator()
    if sim.df is not None:
        print("Available scenarios:")
        for k, v in sim.get_presets().items():
            print(f"  {k}: {v}")
        # Test with first county
        fips = sim.df.iloc[0]["fips"]
        result = sim.simulate("hurricane_cat3", epicenter_fips=fips)
        if "error" not in result:
            s = result["summary"]
            print(f"\nScenario: {s['scenario']}")
            print(f"Counties affected: {s['counties_affected']}")
            print(f"Population at risk: {s['total_population_at_risk']:,}")
            print(f"Risk increase: {s['risk_increase_pct']:.1f}%")
    else:
        print("Run pipeline first.")
