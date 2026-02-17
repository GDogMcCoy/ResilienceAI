"""
ResilienceAI - Sensitivity Analysis Module
Sensitivity analysis and uncertainty quantification for ROI calculations.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Callable, Optional, Tuple
from dataclasses import dataclass
import warnings


@dataclass
class SensitivityResult:
    """Container for sensitivity analysis results."""
    parameter: str
    base_value: float
    range: Tuple[float, float]
    npv_sensitivity: float
    bcr_sensitivity: float
    tornado_score: float
    rank: int


class SensitivityAnalyzer:
    """
    Sensitivity analysis for ROI calculations.

    Supports:
    - One-way sensitivity analysis (tornado diagrams)
    - Two-way sensitivity analysis
    - Scenario analysis
    - Monte Carlo simulation
    """

    def __init__(
        self,
        base_case: Dict,
        parameter_ranges: Dict[str, Tuple[float, float]]
    ):
        """
        Initialize sensitivity analyzer.

        Args:
            base_case: Base case parameter values
            parameter_ranges: Dict of parameter -> (min, max) ranges
        """
        self.base_case = base_case
        self.parameter_ranges = parameter_ranges

    def one_way_sensitivity(
        self,
        calc_function: Callable,
        parameter: str,
        n_points: int = 21
    ) -> pd.DataFrame:
        """
        One-way sensitivity analysis for a single parameter.

        Args:
            calc_function: Function that takes parameters and returns NPV, BCR
            parameter: Parameter to vary
            n_points: Number of evaluation points

        Returns:
            DataFrame with sensitivity results
        """
        param_min, param_max = self.parameter_ranges[parameter]
        values = np.linspace(param_min, param_max, n_points)

        results = []
        for value in values:
            params = self.base_case.copy()
            params[parameter] = value

            npv, bcr = calc_function(params)

            results.append({
                parameter: value,
                "npv": npv,
                "bcr": bcr
            })

        return pd.DataFrame(results)

    def tornado_analysis(
        self,
        calc_function: Callable,
        output_metric: str = "npv"
    ) -> pd.DataFrame:
        """
        Generate tornado diagram data.

        Args:
            calc_function: Function that calculates NPV/BCR from parameters
            output_metric: "npv" or "bcr"

        Returns:
            DataFrame with tornado analysis results
        """
        results = []

        # Calculate base case
        base_npv, base_bcr = calc_function(self.base_case)
        base_output = base_npv if output_metric == "npv" else base_bcr

        for parameter, (pmin, pmax) in self.parameter_ranges.items():
            # Low value
            params_low = self.base_case.copy()
            params_low[parameter] = pmin
            npv_low, bcr_low = calc_function(params_low)
            output_low = npv_low if output_metric == "npv" else bcr_low

            # High value
            params_high = self.base_case.copy()
            params_high[parameter] = pmax
            npv_high, bcr_high = calc_function(params_high)
            output_high = npv_high if output_metric == "npv" else bcr_high

            # Calculate sensitivity
            swing = abs(output_high - output_low)

            results.append({
                "parameter": parameter,
                "base_value": self.base_case[parameter],
                "range_low": pmin,
                "range_high": pmax,
                f"{output_metric}_low": output_low,
                f"{output_metric}_high": output_high,
                f"{output_metric}_swing": swing,
                "tornado_score": swing
            })

        # Rank by swing
        df = pd.DataFrame(results)
        df["rank"] = df["tornado_score"].rank(ascending=False).astype(int)

        return df.sort_values("tornado_score", ascending=False)

    def two_way_sensitivity(
        self,
        calc_function: Callable,
        param1: str,
        param2: str,
        n_points: int = 11
    ) -> pd.DataFrame:
        """
        Two-way sensitivity analysis.

        Args:
            calc_function: Function that calculates NPV/BCR
            param1: First parameter to vary
            param2: Second parameter to vary
            n_points: Number of points per dimension

        Returns:
            DataFrame with 2D sensitivity grid
        """
        p1_min, p1_max = self.parameter_ranges[param1]
        p2_min, p2_max = self.parameter_ranges[param2]

        values1 = np.linspace(p1_min, p1_max, n_points)
        values2 = np.linspace(p2_min, p2_max, n_points)

        results = []
        for v1 in values1:
            for v2 in values2:
                params = self.base_case.copy()
                params[param1] = v1
                params[param2] = v2

                npv, bcr = calc_function(params)

                results.append({
                    param1: v1,
                    param2: v2,
                    "npv": npv,
                    "bcr": bcr,
                    "profitable": npv > 0
                })

        return pd.DataFrame(results)

    def scenario_analysis(
        self,
        calc_function: Callable,
        scenarios: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Scenario-based sensitivity analysis.

        Args:
            calc_function: Function that calculates NPV/BCR
            scenarios: Dict of scenario_name -> parameter values

        Returns:
            DataFrame with scenario results
        """
        results = []

        for scenario_name, scenario_params in scenarios.items():
            params = self.base_case.copy()
            params.update(scenario_params)

            npv, bcr = calc_function(params)

            results.append({
                "scenario": scenario_name,
                "npv": npv,
                "bcr": bcr,
                "profitable": npv > 0,
                **scenario_params
            })

        return pd.DataFrame(results)


class MonteCarloSimulator:
    """
    Monte Carlo simulation for uncertainty quantification.
    """

    def __init__(
        self,
        parameter_distributions: Dict[str, Dict],
        n_iterations: int = 10000,
        random_seed: int = 42
    ):
        """
        Initialize Monte Carlo simulator.

        Args:
            parameter_distributions: Dict of parameter -> distribution spec
            n_iterations: Number of Monte Carlo iterations
            random_seed: Random seed for reproducibility
        """
        self.parameter_distributions = parameter_distributions
        self.n_iterations = n_iterations
        self.random_seed = random_seed

        np.random.seed(random_seed)

    def sample_parameters(self) -> Dict[str, float]:
        """
        Sample parameters from their distributions.

        Returns:
            Dictionary of sampled parameter values
        """
        samples = {}

        for param, dist_spec in self.parameter_distributions.items():
            dist_type = dist_spec.get("type", "normal")

            if dist_type == "normal":
                mean = dist_spec["mean"]
                std = dist_spec["std"]
                samples[param] = np.random.normal(mean, std)

            elif dist_type == "uniform":
                low = dist_spec["low"]
                high = dist_spec["high"]
                samples[param] = np.random.uniform(low, high)

            elif dist_type == "triangular":
                low = dist_spec["low"]
                mode = dist_spec["mode"]
                high = dist_spec["high"]
                samples[param] = np.random.triangular(low, mode, high)

            elif dist_type == "lognormal":
                mean = dist_spec["mean"]
                sigma = dist_spec["sigma"]
                samples[param] = np.random.lognormal(mean, sigma)

            elif dist_type == "beta":
                alpha = dist_spec["alpha"]
                beta = dist_spec["beta"]
                samples[param] = np.random.beta(alpha, beta)

            else:
                raise ValueError(f"Unknown distribution type: {dist_type}")

        return samples

    def run_simulation(
        self,
        calc_function: Callable
    ) -> pd.DataFrame:
        """
        Run Monte Carlo simulation.

        Args:
            calc_function: Function that calculates outputs from parameters

        Returns:
            DataFrame with simulation results
        """
        results = []

        for i in range(self.n_iterations):
            params = self.sample_parameters()

            try:
                outputs = calc_function(params)

                result = {"iteration": i}
                result.update(params)

                if isinstance(outputs, dict):
                    result.update(outputs)
                else:
                    result["output"] = outputs

                results.append(result)
            except Exception as e:
                warnings.warn(f"Iteration {i} failed: {e}")

        return pd.DataFrame(results)

    def calculate_statistics(
        self,
        results: pd.DataFrame,
        output_column: str = "npv"
    ) -> Dict:
        """
        Calculate summary statistics from simulation results.

        Args:
            results: Simulation results DataFrame
            output_column: Column to analyze

        Returns:
            Dictionary with statistics
        """
        values = results[output_column].dropna()

        return {
            "mean": values.mean(),
            "median": values.median(),
            "std": values.std(),
            "min": values.min(),
            "max": values.max(),
            "ci_95": (values.quantile(0.025), values.quantile(0.975)),
            "ci_90": (values.quantile(0.05), values.quantile(0.95)),
            "p_positive": (values > 0).mean(),
            "p_profitable": (values > 0).mean(),
            "var_95": values.quantile(0.05),  # Value at Risk
            "cvar_95": values[values <= values.quantile(0.05)].mean()  # Conditional VaR
        }

    def calculate_probabilistic_sensitivity(
        self,
        results: pd.DataFrame,
        output_column: str = "npv"
    ) -> pd.DataFrame:
        """
        Calculate probabilistic sensitivity measures (PRCC).

        Args:
            results: Simulation results DataFrame
            output_column: Output column to analyze

        Returns:
            DataFrame with PRCC values
        """
        from scipy.stats import spearmanr

        output = results[output_column]

        prcc_results = []
        for param in self.parameter_distributions.keys():
            if param in results.columns:
                param_values = results[param]

                # Calculate partial rank correlation
                corr, pvalue = spearmanr(param_values, output)

                prcc_results.append({
                    "parameter": param,
                    "prcc": corr,
                    "pvalue": pvalue,
                    "significant": pvalue < 0.05,
                    "abs_prcc": abs(corr)
                })

        df = pd.DataFrame(prcc_results)
        df = df.sort_values("abs_prcc", ascending=False)
        df["rank"] = range(1, len(df) + 1)

        return df


class ICERAnalyzer:
    """
    Incremental Cost-Effectiveness Ratio (ICER) analysis.
    """

    def __init__(self, willingness_to_pay: float = 50_000):
        """
        Initialize ICER analyzer.

        Args:
            willingness_to_pay: Willingness-to-pay threshold
        """
        self.wtp = willingness_to_pay

    def calculate_icers(
        self,
        interventions: List[Dict]
    ) -> pd.DataFrame:
        """
        Calculate ICERs for intervention comparisons.

        Args:
            interventions: List of intervention dicts with cost and effectiveness

        Returns:
            DataFrame with ICERs and dominance information
        """
        df = pd.DataFrame(interventions)

        # Sort by effectiveness (ascending)
        df = df.sort_values("effectiveness").reset_index(drop=True)

        # Calculate incremental costs and effects
        df["incremental_cost"] = df["cost"].diff().fillna(df["cost"])
        df["incremental_effect"] = df["effectiveness"].diff().fillna(df["effectiveness"])

        # Calculate ICER
        df["icer"] = df["incremental_cost"] / df["incremental_effect"]

        # Identify dominated interventions
        df["dominated"] = False
        df["extended_dominated"] = False

        for i in range(1, len(df)):
            # Strongly dominated
            if df.loc[i, "cost"] >= df.loc[i-1, "cost"]:
                df.loc[i, "dominated"] = True

            # Extended dominance
            if i > 1 and not df.loc[i, "dominated"]:
                icer_i = df.loc[i, "icer"]
                icer_i_minus_1 = df.loc[i-1, "icer"]
                if icer_i > icer_i_minus_1:
                    df.loc[i, "extended_dominated"] = True

        # Determine cost-effectiveness
        df["cost_effective"] = (df["icer"] < self.wtp) & (~df["dominated"]) & (~df["extended_dominated"])

        return df

    def create_acceptability_curve(
        self,
        interventions: List[Dict],
        wtp_range: Optional[np.ndarray] = None
    ) -> pd.DataFrame:
        """
        Create cost-effectiveness acceptability curve.

        Args:
            interventions: List of interventions
            wtp_range: Range of WTP values to evaluate

        Returns:
            DataFrame with acceptability curve data
        """
        if wtp_range is None:
            wtp_range = np.linspace(0, 150_000, 100)

        results = []
        original_wtp = self.wtp

        for wtp in wtp_range:
            self.wtp = wtp
            df = self.calculate_icers(interventions)

            n_ce = df["cost_effective"].sum()

            results.append({
                "wtp": wtp,
                "n_cost_effective": n_ce,
                "probability_optimal": n_ce / len(interventions) if interventions else 0
            })

        self.wtp = original_wtp

        return pd.DataFrame(results)


if __name__ == "__main__":
    # Example usage

    # Sensitivity analysis
    base_case = {
        "cost": 50_000_000,
        "effectiveness": 100,
        "discount_rate": 0.03,
        "implementation_time": 5
    }

    parameter_ranges = {
        "cost": (40_000_000, 60_000_000),
        "effectiveness": (80, 120),
        "discount_rate": (0.01, 0.05),
        "implementation_time": (3, 7)
    }

    analyzer = SensitivityAnalyzer(base_case, parameter_ranges)

    def calc_npv(params):
        cost = params["cost"]
        effectiveness = params["effectiveness"]
        discount_rate = params["discount_rate"]
        years = params["implementation_time"]

        # Simple NPV calculation
        annual_benefit = effectiveness * 100_000  # $100k per effectiveness unit
        npv = -cost + sum(annual_benefit / ((1 + discount_rate) ** t) for t in range(1, 21))
        bcr = (npv + cost) / cost if cost > 0 else 0

        return npv, bcr

    # Tornado analysis
    tornado = analyzer.tornado_analysis(calc_npv)
    print("Tornado Analysis:")
    print(tornado[["parameter", "npv_swing", "rank"]].to_string())
