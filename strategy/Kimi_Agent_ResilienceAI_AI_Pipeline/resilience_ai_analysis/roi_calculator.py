"""
ResilienceAI - Advanced ROI Calculator Module
Core ROI calculation framework with NPV, IRR, BCR, and cost-effectiveness metrics.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy_financial as npf


@dataclass
class ROIMetrics:
    """Container for comprehensive ROI metrics."""
    npv: float
    irr: Optional[float]
    bcr: float
    payback_period: float
    roi_score: float
    cost_effectiveness: Dict[str, float]
    confidence_interval: Tuple[float, float]


class ROICalculator:
    """
    Calculate comprehensive ROI metrics for disaster preparedness interventions.

    Supports NPV, IRR, BCR, cost-effectiveness ratios, and composite ROI scoring.
    """

    def __init__(self, discount_rate: float = 0.03, time_horizon: int = 20):
        """
        Initialize ROI Calculator.

        Args:
            discount_rate: Annual discount rate (default 3%)
            time_horizon: Analysis time horizon in years (default 20)
        """
        self.discount_rate = discount_rate
        self.time_horizon = time_horizon

        # Benchmarks for cost-effectiveness
        self.ce_benchmarks = {
            "lives_saved": 10_000_000,              # VSL (Value of Statistical Life)
            "dalys_averted": 50_000,                 # WHO cost-effectiveness threshold
            "qalys_gained": 50_000,                  # NICE threshold
            "hospitalizations_prevented": 15_000,    # Average hospitalization cost
            "er_visits_prevented": 1_500,            # Average ER visit cost
            "disasters_mitigated": 1_000_000_000,    # Average disaster cost
            "people_protected": 10_000,              # Cost per person protected
        }

    def calculate_npv(
        self,
        costs: List[float],
        benefits: List[float],
        years: Optional[int] = None
    ) -> float:
        """
        Calculate Net Present Value.

        Args:
            costs: List of annual costs (first year typically includes capital costs)
            benefits: List of annual benefits
            years: Number of years (defaults to length of costs)

        Returns:
            Net Present Value in currency units
        """
        if years is None:
            years = len(costs)

        npv = 0.0
        for t in range(years):
            cost = costs[t] if t < len(costs) else 0
            benefit = benefits[t] if t < len(benefits) else 0
            net = benefit - cost
            npv += net / ((1 + self.discount_rate) ** t)

        return npv

    def calculate_irr(
        self,
        costs: List[float],
        benefits: List[float],
        years: Optional[int] = None
    ) -> Optional[float]:
        """
        Calculate Internal Rate of Return.

        Args:
            costs: List of annual costs
            benefits: List of annual benefits
            years: Number of years

        Returns:
            IRR as decimal (e.g., 0.08 for 8%) or None if cannot be calculated
        """
        if years is None:
            years = max(len(costs), len(benefits))

        # Build cash flow vector
        cash_flows = []
        for t in range(years):
            cost = costs[t] if t < len(costs) else 0
            benefit = benefits[t] if t < len(benefits) else 0

            if t == 0:
                cash_flows.append(-cost)  # Initial investment
            else:
                cash_flows.append(benefit - cost)

        try:
            irr = npf.irr(cash_flows)
            return irr if not np.isnan(irr) else None
        except:
            return None

    def calculate_benefit_cost_ratio(
        self,
        costs: List[float],
        benefits: List[float],
        years: Optional[int] = None
    ) -> float:
        """
        Calculate Benefit-Cost Ratio.

        Args:
            costs: List of annual costs
            benefits: List of annual benefits
            years: Number of years

        Returns:
            BCR (benefits / costs). Values > 1 indicate cost-effective.
        """
        if years is None:
            years = max(len(costs), len(benefits))

        pv_benefits = sum(
            (benefits[t] if t < len(benefits) else 0) / ((1 + self.discount_rate) ** t)
            for t in range(years)
        )

        pv_costs = sum(
            (costs[t] if t < len(costs) else 0) / ((1 + self.discount_rate) ** t)
            for t in range(years)
        )

        return pv_benefits / pv_costs if pv_costs > 0 else float('inf')

    def calculate_payback_period(
        self,
        costs: List[float],
        benefits: List[float],
        years: Optional[int] = None
    ) -> float:
        """
        Calculate discounted payback period.

        Args:
            costs: List of annual costs
            benefits: List of annual benefits
            years: Number of years

        Returns:
            Payback period in years (inf if never pays back)
        """
        if years is None:
            years = max(len(costs), len(benefits))

        cumulative = 0
        for t in range(years):
            cost = costs[t] if t < len(costs) else 0
            benefit = benefits[t] if t < len(benefits) else 0

            net = (benefit - cost) / ((1 + self.discount_rate) ** t)
            cumulative += net

            if cumulative >= 0:
                return t

        return float('inf')

    def calculate_cost_effectiveness(
        self,
        total_cost: float,
        effectiveness_units: float,
        effectiveness_type: str = "lives_saved"
    ) -> Dict[str, float]:
        """
        Calculate cost-effectiveness metrics.

        Args:
            total_cost: Total intervention cost
            effectiveness_units: Units of effectiveness achieved
            effectiveness_type: Type of effectiveness measure

        Returns:
            Dictionary with CE ratio, benchmark comparison, and value assessment
        """
        if effectiveness_units <= 0:
            return {
                "ce_ratio": float('inf'),
                "benchmark": self.ce_benchmarks.get(effectiveness_type, float('inf')),
                "is_cost_effective": False,
                "value_for_money": 0
            }

        ce_ratio = total_cost / effectiveness_units
        benchmark = self.ce_benchmarks.get(effectiveness_type, float('inf'))
        is_cost_effective = ce_ratio < benchmark

        return {
            "ce_ratio": ce_ratio,
            "benchmark": benchmark,
            "is_cost_effective": is_cost_effective,
            "value_for_money": benchmark / ce_ratio if ce_ratio > 0 else 0,
            "interpretation": self._interpret_ce_ratio(ce_ratio, benchmark)
        }

    def _interpret_ce_ratio(self, ce_ratio: float, benchmark: float) -> str:
        """Generate interpretation of cost-effectiveness ratio."""
        ratio = ce_ratio / benchmark

        if ratio < 0.5:
            return "Highly cost-effective"
        elif ratio < 1.0:
            return "Cost-effective"
        elif ratio < 2.0:
            return "Moderately cost-effective"
        else:
            return "Not cost-effective"

    def calculate_roi_score(
        self,
        npv: float,
        total_investment: float,
        payback_period: float,
        risk_reduction: float,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate composite ROI score (0-100).

        Args:
            npv: Net Present Value
            total_investment: Total investment amount
            payback_period: Payback period in years
            risk_reduction: Risk reduction score (0-1)
            weights: Custom weights for components

        Returns:
            Composite ROI score (0-100)
        """
        if weights is None:
            weights = {
                "npv": 0.35,
                "payback": 0.25,
                "risk": 0.40
            }

        # NPV component (normalized by investment)
        npv_normalized = npv / total_investment if total_investment > 0 else 0
        npv_component = min(35, max(0, npv_normalized * 17.5)) * weights["npv"] / 0.35

        # Payback component (shorter is better, max 10 years)
        payback_component = max(0, 25 - payback_period * 2.5) * weights["payback"] / 0.25

        # Risk component
        risk_component = risk_reduction * 40 * weights["risk"] / 0.40

        return npv_component + payback_component + risk_component

    def calculate_comprehensive_roi(
        self,
        intervention_data: Dict
    ) -> ROIMetrics:
        """
        Calculate all ROI metrics comprehensively.

        Args:
            intervention_data: Dictionary with costs, benefits, and metadata

        Returns:
            ROIMetrics object with all calculated metrics
        """
        costs = intervention_data.get("costs", [])
        benefits = intervention_data.get("benefits", [])
        effectiveness = intervention_data.get("effectiveness_units", 0)
        effectiveness_type = intervention_data.get("effectiveness_type", "lives_saved")

        # Calculate all metrics
        npv = self.calculate_npv(costs, benefits)
        irr = self.calculate_irr(costs, benefits)
        bcr = self.calculate_benefit_cost_ratio(costs, benefits)
        payback = self.calculate_payback_period(costs, benefits)

        total_cost = sum(costs)
        ce_metrics = self.calculate_cost_effectiveness(
            total_cost, effectiveness, effectiveness_type
        )

        risk_reduction = intervention_data.get("risk_reduction", 0)
        roi_score = self.calculate_roi_score(npv, total_cost, payback, risk_reduction)

        # Calculate confidence interval (simplified)
        ci_lower = npv * 0.8
        ci_upper = npv * 1.2

        return ROIMetrics(
            npv=npv,
            irr=irr,
            bcr=bcr,
            payback_period=payback,
            roi_score=roi_score,
            cost_effectiveness=ce_metrics,
            confidence_interval=(ci_lower, ci_upper)
        )

    def compare_interventions(
        self,
        interventions: List[Dict]
    ) -> pd.DataFrame:
        """
        Compare multiple interventions on ROI metrics.

        Args:
            interventions: List of intervention data dictionaries

        Returns:
            DataFrame with comparison metrics
        """
        results = []

        for inv in interventions:
            metrics = self.calculate_comprehensive_roi(inv)

            results.append({
                "intervention": inv.get("name", "Unknown"),
                "npv": metrics.npv,
                "irr": metrics.irr if metrics.irr else 0,
                "bcr": metrics.bcr,
                "payback_years": metrics.payback_period,
                "roi_score": metrics.roi_score,
                "ce_ratio": metrics.cost_effectiveness["ce_ratio"],
                "is_cost_effective": metrics.cost_effectiveness["is_cost_effective"],
                "total_cost": sum(inv.get("costs", [])),
                "total_benefits": sum(inv.get("benefits", []))
            })

        return pd.DataFrame(results)


class PortfolioROI:
    """Calculate ROI for intervention portfolios with synergy effects."""

    # Synergy effects between intervention categories
    SYNERGY_EFFECTS = {
        ("healthcare", "emergency"): 0.15,
        ("emergency", "healthcare"): 0.15,
        ("preparedness", "emergency"): 0.20,
        ("emergency", "preparedness"): 0.20,
        ("social", "healthcare"): 0.10,
        ("healthcare", "social"): 0.10,
        ("infrastructure", "healthcare"): 0.12,
        ("healthcare", "infrastructure"): 0.12,
    }

    def __init__(self, interventions: List[Dict]):
        """
        Initialize portfolio calculator.

        Args:
            interventions: List of intervention dictionaries with ROI data
        """
        self.interventions = interventions

    def calculate_portfolio_npv(self) -> float:
        """Calculate combined NPV of all interventions."""
        return sum(inv.get("npv", 0) for inv in self.interventions)

    def calculate_portfolio_cost(self) -> float:
        """Calculate total portfolio cost."""
        return sum(sum(inv.get("costs", [])) for inv in self.interventions)

    def calculate_synergy_effects(self) -> Dict[str, float]:
        """
        Calculate synergy effects between interventions.

        Returns:
            Dictionary with synergy multiplier and value
        """
        total_synergy = 0.0
        categories = [inv.get("category", "other") for inv in self.interventions]

        # Check all pairs
        for i, cat1 in enumerate(categories):
            for j, cat2 in enumerate(categories):
                if i < j:  # Avoid double counting
                    synergy = self.SYNERGY_EFFECTS.get((cat1, cat2), 0)
                    total_synergy += synergy

        portfolio_npv = self.calculate_portfolio_npv()

        return {
            "synergy_multiplier": 1 + total_synergy,
            "synergy_value": total_synergy * portfolio_npv,
            "total_synergy": total_synergy,
            "adjusted_npv": portfolio_npv * (1 + total_synergy)
        }

    def calculate_diversification_benefit(self) -> Dict[str, float]:
        """
        Calculate risk diversification benefit.

        More categories = better diversification.

        Returns:
            Dictionary with diversification metrics
        """
        categories = set(inv.get("category", "other") for inv in self.interventions)
        n_categories = len(categories)

        # Diversification score (0-1)
        diversification_score = min(1.0, n_categories / 5)

        # Risk reduction from diversification (max 15%)
        risk_reduction = min(0.15, diversification_score * 0.05)

        return {
            "n_categories": n_categories,
            "categories": list(categories),
            "diversification_score": diversification_score,
            "risk_reduction": risk_reduction,
            "portfolio_risk_adjustment": 1 - risk_reduction
        }

    def calculate_portfolio_metrics(self) -> Dict:
        """
        Calculate comprehensive portfolio metrics.

        Returns:
            Dictionary with all portfolio metrics
        """
        base_npv = self.calculate_portfolio_npv()
        synergy = self.calculate_synergy_effects()
        diversification = self.calculate_diversification_benefit()

        adjusted_npv = base_npv * synergy["synergy_multiplier"] * diversification["portfolio_risk_adjustment"]

        return {
            "base_npv": base_npv,
            "adjusted_npv": adjusted_npv,
            "total_cost": self.calculate_portfolio_cost(),
            "synergy": synergy,
            "diversification": diversification,
            "portfolio_bcr": adjusted_npv / self.calculate_portfolio_cost() if self.calculate_portfolio_cost() > 0 else 0,
            "n_interventions": len(self.interventions)
        }


# Utility functions
def calculate_break_even(
    fixed_costs: float,
    variable_cost_per_unit: float,
    benefit_per_unit: float
) -> float:
    """
    Calculate break-even point.

    Args:
        fixed_costs: Fixed costs
        variable_cost_per_unit: Variable cost per unit
        benefit_per_unit: Benefit per unit

    Returns:
        Break-even quantity
    """
    if benefit_per_unit <= variable_cost_per_unit:
        return float('inf')

    return fixed_costs / (benefit_per_unit - variable_cost_per_unit)


def calculate_marginal_roi(
    additional_cost: float,
    additional_benefit: float
) -> float:
    """
    Calculate marginal ROI for incremental investment.

    Args:
        additional_cost: Additional cost
        additional_benefit: Additional benefit

    Returns:
        Marginal ROI ratio
    """
    if additional_cost <= 0:
        return float('inf')

    return (additional_benefit - additional_cost) / additional_cost


if __name__ == "__main__":
    # Example usage
    calculator = ROICalculator(discount_rate=0.03)

    # Example intervention
    intervention = {
        "name": "Hospital Expansion",
        "costs": [50_000_000, 2_000_000, 2_000_000, 2_000_000, 2_000_000],
        "benefits": [0, 15_000_000, 15_000_000, 15_000_000, 15_000_000],
        "effectiveness_units": 5,  # Lives saved per year
        "effectiveness_type": "lives_saved",
        "risk_reduction": 0.15
    }

    metrics = calculator.calculate_comprehensive_roi(intervention)

    print("ROI Metrics:")
    print(f"  NPV: ${metrics.npv:,.0f}")
    print(f"  IRR: {metrics.irr:.2%}" if metrics.irr else "  IRR: N/A")
    print(f"  BCR: {metrics.bcr:.2f}")
    print(f"  Payback: {metrics.payback_period:.1f} years")
    print(f"  ROI Score: {metrics.roi_score:.1f}/100")
    print(f"  Cost-Effective: {metrics.cost_effectiveness['is_cost_effective']}")
