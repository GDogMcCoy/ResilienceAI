"""
ResilienceAI - Multi-Criteria Decision Analysis (MCDA) Module
Prioritization algorithms including AHP, TOPSIS, and PROMETHEE.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import warnings


@dataclass
class Criterion:
    """Decision criterion definition."""
    name: str
    weight: float
    direction: str = "maximize"  # "maximize" or "minimize"

    def __post_init__(self):
        if self.direction not in ["maximize", "minimize"]:
            raise ValueError("Direction must be 'maximize' or 'minimize'")


class MCDAPrioritizer:
    """
    Multi-Criteria Decision Analysis for intervention prioritization.

    Supports:
    - AHP (Analytic Hierarchy Process) for weight determination
    - TOPSIS for ranking
    - PROMETHEE for pairwise comparison
    """

    def __init__(self, criteria: List[Criterion]):
        """
        Initialize MCDA prioritizer.

        Args:
            criteria: List of decision criteria
        """
        self.criteria = criteria

        # Normalize weights
        total_weight = sum(c.weight for c in criteria)
        for c in self.criteria:
            c.weight = c.weight / total_weight

    def ahp_weights(
        self,
        comparison_matrix: np.ndarray,
        check_consistency: bool = True
    ) -> Tuple[np.ndarray, float]:
        """
        Calculate criteria weights using AHP.

        Args:
            comparison_matrix: Pairwise comparison matrix
            check_consistency: Whether to check consistency ratio

        Returns:
            Tuple of (weights, consistency_ratio)
        """
        n = len(comparison_matrix)

        # Normalize comparison matrix
        col_sums = comparison_matrix.sum(axis=0)
        normalized = comparison_matrix / col_sums

        # Calculate eigenvector (weights)
        weights = normalized.mean(axis=1)

        # Calculate consistency
        if check_consistency:
            # Calculate lambda_max
            weighted_sum = comparison_matrix @ weights
            lambda_max = (weighted_sum / weights).mean()

            # Consistency Index
            ci = (lambda_max - n) / (n - 1)

            # Random Index values
            ri_values = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 
                        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
            ri = ri_values.get(n, 1.49)

            # Consistency Ratio
            cr = ci / ri if ri > 0 else 0

            if cr > 0.1:
                warnings.warn(f"Inconsistent comparison matrix (CR={cr:.3f})")
        else:
            cr = 0

        return weights, cr

    def topsis_ranking(
        self,
        alternatives: pd.DataFrame,
        normalize: bool = True
    ) -> pd.DataFrame:
        """
        TOPSIS (Technique for Order Preference by Similarity to Ideal Solution).

        Args:
            alternatives: DataFrame with criteria as columns
            normalize: Whether to normalize the decision matrix

        Returns:
            DataFrame with rankings and scores
        """
        # Get criterion names
        criterion_names = [c.name for c in self.criteria]

        # Validate columns
        missing = set(criterion_names) - set(alternatives.columns)
        if missing:
            raise ValueError(f"Missing criteria columns: {missing}")

        # Extract decision matrix
        decision_matrix = alternatives[criterion_names].copy()

        # Handle minimize criteria
        for criterion in self.criteria:
            if criterion.direction == "minimize":
                decision_matrix[criterion.name] = -decision_matrix[criterion.name]

        # Normalize
        if normalize:
            for col in criterion_names:
                norm = np.sqrt((decision_matrix[col] ** 2).sum())
                if norm > 0:
                    decision_matrix[col] = decision_matrix[col] / norm

        # Weight normalized matrix
        weights = np.array([c.weight for c in self.criteria])
        weighted = decision_matrix * weights

        # Determine ideal and anti-ideal solutions
        ideal = weighted.max()
        anti_ideal = weighted.min()

        # Calculate distances
        d_ideal = np.sqrt(((weighted - ideal) ** 2).sum(axis=1))
        d_anti_ideal = np.sqrt(((weighted - anti_ideal) ** 2).sum(axis=1))

        # Calculate closeness coefficient
        closeness = d_anti_ideal / (d_ideal + d_anti_ideal)

        # Create results
        result = alternatives.copy()
        result["closeness"] = closeness
        result["rank"] = closeness.rank(ascending=False).astype(int)
        result["d_ideal"] = d_ideal
        result["d_anti_ideal"] = d_anti_ideal

        return result.sort_values("rank")

    def promethee_ranking(
        self,
        alternatives: pd.DataFrame,
        preference_function: str = "usual",
        preference_threshold: float = 0.0
    ) -> pd.DataFrame:
        """
        PROMETHEE (Preference Ranking Organization Method for Enrichment Evaluations).

        Args:
            alternatives: DataFrame with criteria as columns
            preference_function: "usual", "linear", "gaussian", "level"
            preference_threshold: Threshold for preference function

        Returns:
            DataFrame with rankings and flows
        """
        criterion_names = [c.name for c in self.criteria]
        n = len(alternatives)

        # Initialize preference matrix
        preference_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    # Calculate aggregated preference
                    pref = 0
                    for criterion in self.criteria:
                        name = criterion.name

                        if criterion.direction == "maximize":
                            diff = alternatives.iloc[i][name] - alternatives.iloc[j][name]
                        else:
                            diff = alternatives.iloc[j][name] - alternatives.iloc[i][name]

                        pref += criterion.weight * self._preference(
                            diff, preference_function, preference_threshold
                        )

                    preference_matrix[i, j] = pref

        # Calculate positive and negative flows
        positive_flow = preference_matrix.sum(axis=1) / (n - 1)
        negative_flow = preference_matrix.sum(axis=0) / (n - 1)

        # Net flow
        net_flow = positive_flow - negative_flow

        # Create results
        result = alternatives.copy()
        result["positive_flow"] = positive_flow
        result["negative_flow"] = negative_flow
        result["net_flow"] = net_flow
        result["rank"] = net_flow.rank(ascending=False).astype(int)

        return result.sort_values("rank")

    def _preference(
        self,
        diff: float,
        function: str,
        threshold: float
    ) -> float:
        """
        Calculate preference function value.

        Args:
            diff: Difference between alternatives
            function: Preference function type
            threshold: Preference threshold

        Returns:
            Preference value (0-1)
        """
        if function == "usual":
            return 1.0 if diff > 0 else 0.0

        elif function == "linear":
            if diff <= 0:
                return 0.0
            elif diff >= threshold:
                return 1.0
            else:
                return diff / threshold

        elif function == "gaussian":
            if diff <= 0:
                return 0.0
            else:
                return 1 - np.exp(-(diff ** 2) / (2 * threshold ** 2))

        elif function == "level":
            if diff <= 0:
                return 0.0
            elif diff <= threshold:
                return 0.5
            else:
                return 1.0

        return 0.0

    def weighted_sum_ranking(
        self,
        alternatives: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Simple weighted sum ranking.

        Args:
            alternatives: DataFrame with criteria as columns

        Returns:
            DataFrame with rankings
        """
        criterion_names = [c.name for c in self.criteria]

        # Calculate weighted sum
        scores = np.zeros(len(alternatives))
        for criterion in self.criteria:
            values = alternatives[criterion.name].values

            # Normalize to 0-1
            min_val = values.min()
            max_val = values.max()

            if max_val > min_val:
                normalized = (values - min_val) / (max_val - min_val)
            else:
                normalized = np.ones_like(values) * 0.5

            # Apply direction
            if criterion.direction == "minimize":
                normalized = 1 - normalized

            scores += criterion.weight * normalized

        # Create results
        result = alternatives.copy()
        result["score"] = scores
        result["rank"] = scores.rank(ascending=False).astype(int)

        return result.sort_values("rank")


class DynamicPrioritizer:
    """Dynamic prioritization based on real-time conditions."""

    def __init__(self, base_priorities: pd.DataFrame):
        """
        Initialize dynamic prioritizer.

        Args:
            base_priorities: Base priority scores DataFrame
        """
        self.base_priorities = base_priorities.copy()

        # Adjustment factors for different conditions
        self.adjustment_factors = {
            "weather_alert": 1.5,
            "resource_surge": 1.3,
            "funding_increase": 1.2,
            "emergency_declaration": 2.0,
            "low_resources": 0.7
        }

    def adjust_for_weather(
        self,
        weather_forecast: Dict[str, List[str]]
    ) -> pd.DataFrame:
        """
        Adjust priorities based on weather forecast.

        Args:
            weather_forecast: Dict with "affected_areas" (list of county FIPS)

        Returns:
            Adjusted priorities DataFrame
        """
        adjusted = self.base_priorities.copy()
        affected = weather_forecast.get("affected_areas", [])

        for idx, row in adjusted.iterrows():
            county = row.get("county_fips")

            if county in affected:
                # Boost emergency response interventions
                if row.get("category") == "emergency":
                    adjusted.loc[idx, "priority"] *= self.adjustment_factors["weather_alert"]

                # Boost healthcare preparedness
                if row.get("category") == "healthcare":
                    adjusted.loc[idx, "priority"] *= 1.3

                # Boost preparedness
                if row.get("category") == "preparedness":
                    adjusted.loc[idx, "priority"] *= 1.2

        return adjusted.sort_values("priority", ascending=False)

    def adjust_for_resource_availability(
        self,
        available_resources: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Adjust priorities based on resource availability.

        Args:
            available_resources: Dict mapping intervention types to availability (0-1)

        Returns:
            Adjusted priorities DataFrame
        """
        adjusted = self.base_priorities.copy()

        for idx, row in adjusted.iterrows():
            intervention_type = row.get("intervention_type")

            if intervention_type in available_resources:
                availability = available_resources[intervention_type]

                # Reduce priority if resources scarce
                if availability < 0.3:
                    adjusted.loc[idx, "priority"] *= self.adjustment_factors["low_resources"]
                # Boost if resources abundant
                elif availability > 0.8:
                    adjusted.loc[idx, "priority"] *= 1.1

        return adjusted.sort_values("priority", ascending=False)

    def adjust_for_equity(
        self,
        equity_weight: float = 0.3
    ) -> pd.DataFrame:
        """
        Adjust priorities for equity considerations.

        Args:
            equity_weight: Weight for equity (0-1)

        Returns:
            Adjusted priorities DataFrame
        """
        adjusted = self.base_priorities.copy()

        if "svi" in adjusted.columns:
            # Social Vulnerability Index adjustment
            svi = adjusted["svi"].fillna(0.5)
            adjusted["priority"] *= (1 + equity_weight * svi)

        if "poverty_rate" in adjusted.columns:
            # Poverty rate adjustment
            poverty = adjusted["poverty_rate"].fillna(0.15)
            adjusted["priority"] *= (1 + equity_weight * poverty / 0.5)

        return adjusted.sort_values("priority", ascending=False)


def create_ahp_comparison_matrix(
    criteria_names: List[str],
    comparisons: Dict[Tuple[str, str], float]
) -> np.ndarray:
    """
    Create AHP comparison matrix from pairwise comparisons.

    Args:
        criteria_names: List of criterion names
        comparisons: Dict of (criterion1, criterion2) -> comparison value

    Returns:
        Comparison matrix
    """
    n = len(criteria_names)
    matrix = np.ones((n, n))

    name_to_idx = {name: i for i, name in enumerate(criteria_names)}

    for (name1, name2), value in comparisons.items():
        i = name_to_idx[name1]
        j = name_to_idx[name2]
        matrix[i, j] = value
        matrix[j, i] = 1 / value

    return matrix


# Example AHP scale
AHP_SCALE = {
    "equal": 1,
    "slightly_better": 3,
    "better": 5,
    "much_better": 7,
    "absolutely_better": 9
}


if __name__ == "__main__":
    # Example usage
    criteria = [
        Criterion("cost_effectiveness", 0.3, "maximize"),
        Criterion("lives_saved", 0.4, "maximize"),
        Criterion("implementation_time", 0.2, "minimize"),
        Criterion("equity_impact", 0.1, "maximize")
    ]

    prioritizer = MCDAPrioritizer(criteria)

    # Example alternatives
    alternatives = pd.DataFrame({
        "name": ["Hospital", "EMS", "Fire", "Telehealth", "Prep Program"],
        "cost_effectiveness": [0.7, 0.9, 0.8, 0.95, 0.85],
        "lives_saved": [10, 5, 4, 3, 6],
        "implementation_time": [5, 1, 2, 1, 1],
        "equity_impact": [0.8, 0.7, 0.6, 0.9, 0.85]
    })

    # TOPSIS ranking
    topsis_result = prioritizer.topsis_ranking(alternatives)
    print("TOPSIS Ranking:")
    print(topsis_result[["name", "closeness", "rank"]].to_string())

    # PROMETHEE ranking
    promethee_result = prioritizer.promethee_ranking(alternternatives)
    print("\nPROMETHEE Ranking:")
    print(promethee_result[["name", "net_flow", "rank"]].to_string())
