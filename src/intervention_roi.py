"""
ResilienceAI - Intervention ROI Calculator
Estimates cost-effectiveness of disaster preparedness interventions.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from config import PROCESSED_DIR


# Intervention database: (base_cost_usd, base_risk_reduction_pct, category)
INTERVENTIONS = {
    "add_hospital": {
        "label": "Build New Hospital (50-bed)",
        "base_cost": 50_000_000,
        "base_risk_reduction": 0.12,
        "category": "healthcare",
        "implementation_years": 5,
    },
    "add_ems_station": {
        "label": "Build EMS Station",
        "base_cost": 2_000_000,
        "base_risk_reduction": 0.06,
        "category": "emergency",
        "implementation_years": 1,
    },
    "add_fire_station": {
        "label": "Build Fire Station",
        "base_cost": 3_000_000,
        "base_risk_reduction": 0.05,
        "category": "emergency",
        "implementation_years": 2,
    },
    "telehealth_infrastructure": {
        "label": "Deploy Telehealth Infrastructure",
        "base_cost": 250_000,
        "base_risk_reduction": 0.08,
        "category": "healthcare",
        "implementation_years": 1,
    },
    "disaster_prep_program": {
        "label": "Community Disaster Preparedness Program",
        "base_cost": 500_000,
        "base_risk_reduction": 0.10,
        "category": "preparedness",
        "implementation_years": 1,
    },
    "poverty_reduction": {
        "label": "Economic Development / Poverty Reduction",
        "base_cost": 10_000_000,
        "base_risk_reduction": 0.15,
        "category": "social",
        "implementation_years": 5,
    },
}


class InterventionROICalculator:
    """Calculate ROI for disaster preparedness interventions per county."""

    def __init__(self, df=None):
        if df is None:
            path = PROCESSED_DIR / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
            else:
                self.df = None
        else:
            self.df = df

    def get_available_interventions(self):
        """Return list of available interventions."""
        return {k: v["label"] for k, v in INTERVENTIONS.items()}

    def calculate_roi(self, fips, intervention_key, investment_multiplier=1.0):
        """
        Calculate ROI for a specific intervention in a specific county.

        Args:
            fips: County FIPS code
            intervention_key: Key from INTERVENTIONS
            investment_multiplier: Scale investment (1.0 = base, 2.0 = double)

        Returns:
            dict with ROI metrics
        """
        if self.df is None:
            return {"error": "Data not loaded"}

        intervention = INTERVENTIONS.get(intervention_key)
        if not intervention:
            return {"error": f"Unknown intervention: {intervention_key}"}

        match = self.df[self.df["fips"] == str(fips)]
        if match.empty:
            return {"error": f"County {fips} not found"}

        county = match.iloc[0]
        pop = county.get("total_population", 10000)
        current_risk = county.get("risk_score", 0.5)

        # Scale cost by investment multiplier
        cost = intervention["base_cost"] * investment_multiplier

        # Diminishing returns: effectiveness = base * (1 - e^(-multiplier)) / (1 - e^(-1))
        diminishing_factor = (1 - np.exp(-investment_multiplier)) / (1 - np.exp(-1))
        risk_reduction = intervention["base_risk_reduction"] * diminishing_factor

        # Adjust reduction based on county characteristics
        # Counties with higher current risk benefit more from intervention
        risk_adjustment = 0.5 + current_risk  # 0.5x to 1.5x
        adjusted_reduction = risk_reduction * risk_adjustment

        # Population scaling: smaller counties get less absolute benefit
        pop_factor = min(pop / 50000, 1.5)  # Cap at 1.5x for large counties
        pop_factor = max(pop_factor, 0.3)  # Floor at 0.3x for tiny counties

        effective_reduction = adjusted_reduction * pop_factor
        new_risk = max(0, current_risk - effective_reduction)
        actual_reduction = current_risk - new_risk

        # Cost-effectiveness metrics
        cost_per_risk_point = cost / (actual_reduction + 1e-10)
        people_helped = int(pop * actual_reduction)
        cost_per_person = cost / (people_helped + 1)

        return {
            "county_fips": fips,
            "county_name": county.get("county_name", "Unknown"),
            "intervention": intervention["label"],
            "intervention_key": intervention_key,
            "investment": cost,
            "investment_multiplier": investment_multiplier,
            "current_risk_score": round(float(current_risk), 4),
            "projected_risk_score": round(float(new_risk), 4),
            "risk_reduction": round(float(actual_reduction), 4),
            "risk_reduction_pct": round(float(actual_reduction / (current_risk + 1e-10) * 100), 1),
            "population_affected": int(pop),
            "people_helped": people_helped,
            "cost_per_risk_point_reduced": round(cost_per_risk_point, 0),
            "cost_per_person_helped": round(cost_per_person, 2),
            "implementation_years": intervention["implementation_years"],
            "category": intervention["category"],
        }

    def rank_interventions(self, fips, top_n=None):
        """Rank all interventions for a county by cost-effectiveness."""
        results = []
        for key in INTERVENTIONS:
            roi = self.calculate_roi(fips, key)
            if "error" not in roi:
                results.append(roi)

        results.sort(key=lambda x: x["cost_per_person_helped"])
        if top_n:
            results = results[:top_n]
        return results

    def find_best_counties(self, intervention_key, max_results=20):
        """Find counties where an intervention would have the most impact."""
        if self.df is None:
            return {"error": "Data not loaded"}

        results = []
        for _, row in self.df.iterrows():
            roi = self.calculate_roi(row["fips"], intervention_key)
            if "error" not in roi and roi["risk_reduction"] > 0:
                results.append(roi)

        results.sort(key=lambda x: x["risk_reduction"], reverse=True)
        return results[:max_results]


if __name__ == "__main__":
    calc = InterventionROICalculator()
    if calc.df is not None:
        fips = calc.df.iloc[0]["fips"]
        print(f"Intervention ROI for {calc.df.iloc[0]['county_name']}:")
        rankings = calc.rank_interventions(fips)
        for r in rankings:
            print(f"  {r['intervention']}: {r['risk_reduction_pct']:.1f}% reduction, "
                  f"${r['investment']:,.0f}, ${r['cost_per_person_helped']:.2f}/person")
    else:
        print("Run pipeline first.")
