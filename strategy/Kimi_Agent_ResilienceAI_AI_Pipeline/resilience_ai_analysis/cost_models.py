"""
ResilienceAI - Advanced Cost Models Module
Comprehensive cost modeling with regional adjustments, economies of scale, and multi-period budgets.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CostCategory(Enum):
    """Intervention cost categories."""
    CAPITAL = "capital"
    OPERATING = "operating"
    INDIRECT = "indirect"
    CONTINGENCY = "contingency"


# Regional cost indices by state (relative to national average = 1.0)
REGIONAL_COST_INDEX = {
    # Northeast
    "CT": 1.25, "ME": 1.10, "MA": 1.35, "NH": 1.15, "RI": 1.20, "VT": 1.10,
    "NJ": 1.30, "NY": 1.40, "PA": 1.05,
    # Midwest
    "IL": 1.10, "IN": 0.95, "MI": 0.95, "OH": 0.90, "WI": 0.95,
    "IA": 0.85, "KS": 0.85, "MN": 1.00, "MO": 0.85, "NE": 0.85, "ND": 0.80, "SD": 0.80,
    # South
    "DE": 1.05, "FL": 1.00, "GA": 0.90, "MD": 1.15, "NC": 0.90, "SC": 0.85, 
    "VA": 1.00, "WV": 0.80,
    "AL": 0.80, "KY": 0.80, "MS": 0.75, "TN": 0.85,
    "AR": 0.75, "LA": 0.80, "OK": 0.75, "TX": 0.90,
    # West
    "AZ": 0.95, "CO": 1.05, "ID": 0.90, "MT": 0.85, "NV": 1.00, "NM": 0.80, 
    "UT": 0.90, "WY": 0.85,
    "AK": 1.30, "CA": 1.35, "HI": 1.50, "OR": 1.05, "WA": 1.10
}


@dataclass
class CostComponents:
    """Detailed cost components for interventions."""

    # Capital Costs (one-time)
    construction_cost: float = 0.0
    equipment_cost: float = 0.0
    land_acquisition: float = 0.0
    permitting_cost: float = 0.0
    design_cost: float = 0.0

    # Operating Costs (annual)
    personnel_cost: float = 0.0
    maintenance_cost: float = 0.0
    utilities_cost: float = 0.0
    supplies_cost: float = 0.0
    insurance_cost: float = 0.0

    # Indirect Costs
    training_cost: float = 0.0
    administrative_cost: float = 0.0
    marketing_cost: float = 0.0

    # Contingency (as fraction of subtotal)
    contingency_rate: float = 0.15

    def calculate_capital_cost(self) -> float:
        """Calculate total capital cost."""
        subtotal = (self.construction_cost + self.equipment_cost + 
                   self.land_acquisition + self.permitting_cost + self.design_cost)
        return subtotal * (1 + self.contingency_rate)

    def calculate_annual_operating_cost(self) -> float:
        """Calculate annual operating cost."""
        return (self.personnel_cost + self.maintenance_cost + 
                self.utilities_cost + self.supplies_cost + self.insurance_cost)

    def calculate_annual_indirect_cost(self) -> float:
        """Calculate annual indirect cost."""
        return self.training_cost + self.administrative_cost + self.marketing_cost

    def calculate_total_annual_cost(self) -> float:
        """Calculate total annual cost."""
        return self.calculate_annual_operating_cost() + self.calculate_annual_indirect_cost()


@dataclass
class InterventionCost:
    """Comprehensive cost model for interventions."""

    components: CostComponents
    implementation_years: int = 1
    operational_lifetime: int = 20
    discount_rate: float = 0.03
    state_code: Optional[str] = None
    inflation_rate: float = 0.025

    def get_regional_multiplier(self) -> float:
        """Get cost multiplier for region."""
        if self.state_code and self.state_code in REGIONAL_COST_INDEX:
            return REGIONAL_COST_INDEX[self.state_code]
        return 1.0

    def calculate_npv_cost(self) -> float:
        """
        Calculate Net Present Value of total costs.

        Includes capital costs (upfront) and NPV of operating costs.
        """
        regional_mult = self.get_regional_multiplier()

        # Capital costs (incurred during implementation)
        capital = self.components.calculate_capital_cost() * regional_mult

        # Annual costs with inflation
        annual_costs = []
        for year in range(1, self.operational_lifetime + 1):
            base_annual = self.components.calculate_total_annual_cost() * regional_mult
            inflated = base_annual * ((1 + self.inflation_rate) ** year)
            annual_costs.append(inflated)

        # NPV of operating costs
        operating_npv = sum(
            cost / ((1 + self.discount_rate) ** t)
            for t, cost in enumerate(annual_costs, 1)
        )

        return capital + operating_npv

    def calculate_annual_cost_schedule(self) -> List[float]:
        """
        Generate annual cost schedule over operational lifetime.

        Returns:
            List of annual costs (year 0 = capital cost)
        """
        regional_mult = self.get_regional_multiplier()

        # Year 0: Capital cost
        schedule = [self.components.calculate_capital_cost() * regional_mult]

        # Years 1+: Operating costs with inflation
        for year in range(1, self.operational_lifetime + 1):
            base_annual = self.components.calculate_total_annual_cost() * regional_mult
            inflated = base_annual * ((1 + self.inflation_rate) ** year)
            schedule.append(inflated)

        return schedule

    def calculate_lifecycle_cost(self) -> float:
        """Calculate total lifecycle cost (undiscounted)."""
        return sum(self.calculate_annual_cost_schedule())

    def get_cost_breakdown(self) -> Dict[str, float]:
        """Get detailed cost breakdown."""
        regional_mult = self.get_regional_multiplier()

        return {
            "capital_construction": self.components.construction_cost * regional_mult,
            "capital_equipment": self.components.equipment_cost * regional_mult,
            "capital_land": self.components.land_acquisition * regional_mult,
            "capital_permitting": self.components.permitting_cost * regional_mult,
            "annual_personnel": self.components.personnel_cost * regional_mult,
            "annual_maintenance": self.components.maintenance_cost * regional_mult,
            "annual_utilities": self.components.utilities_cost * regional_mult,
            "annual_supplies": self.components.supplies_cost * regional_mult,
            "annual_training": self.components.training_cost * regional_mult,
            "annual_admin": self.components.administrative_cost * regional_mult,
            "npv_total": self.calculate_npv_cost(),
            "lifecycle_total": self.calculate_lifecycle_cost()
        }


class EconomiesOfScale:
    """Model economies of scale for intervention costs."""

    def __init__(
        self, 
        base_cost: float, 
        scale_factor: float = 0.85,
        min_quantity: int = 1
    ):
        """
        Initialize economies of scale model.

        Args:
            base_cost: Cost for baseline quantity
            scale_factor: Cost multiplier per doubling (0.85 = 15% reduction)
            min_quantity: Minimum quantity for scaling
        """
        self.base_cost = base_cost
        self.scale_factor = scale_factor
        self.min_quantity = min_quantity

    def calculate_scaled_cost(self, quantity: int) -> float:
        """
        Calculate cost with economies of scale.

        Args:
            quantity: Number of units

        Returns:
            Total cost with scale adjustments
        """
        if quantity <= 0:
            return 0.0

        quantity = max(quantity, self.min_quantity)

        # Calculate number of doublings from base
        doublings = max(0, np.log2(quantity / self.min_quantity))

        # Apply scale factor
        scale_multiplier = self.scale_factor ** doublings

        return self.base_cost * quantity * scale_multiplier

    def calculate_marginal_cost(self, quantity: int) -> float:
        """
        Calculate marginal cost at given quantity.

        Args:
            quantity: Current quantity

        Returns:
            Cost of adding one more unit
        """
        cost_n = self.calculate_scaled_cost(quantity)
        cost_n_plus_1 = self.calculate_scaled_cost(quantity + 1)
        return cost_n_plus_1 - cost_n

    def calculate_average_cost(self, quantity: int) -> float:
        """
        Calculate average cost per unit.

        Args:
            quantity: Number of units

        Returns:
            Average cost per unit
        """
        if quantity <= 0:
            return 0.0

        total_cost = self.calculate_scaled_cost(quantity)
        return total_cost / quantity


class MultiPeriodBudget:
    """Model budget constraints across multiple time periods."""

    def __init__(
        self,
        annual_budgets: List[float],
        carryover_rate: float = 0.0,
        borrowing_limit: float = 0.0,
        interest_rate: float = 0.05
    ):
        """
        Initialize multi-period budget.

        Args:
            annual_budgets: Budget for each year
            carryover_rate: Fraction of unused budget that carries over
            borrowing_limit: Maximum borrowing from future years
            interest_rate: Interest rate on borrowed funds
        """
        self.annual_budgets = annual_budgets
        self.carryover_rate = carryover_rate
        self.borrowing_limit = borrowing_limit
        self.interest_rate = interest_rate
        self.n_periods = len(annual_budgets)

    def simulate_budget_flow(
        self,
        expenditures: List[float]
    ) -> pd.DataFrame:
        """
        Simulate budget flow over time.

        Args:
            expenditures: Planned expenditures per period

        Returns:
            DataFrame with budget simulation results
        """
        results = []
        carryover = 0.0
        debt = 0.0

        for t in range(self.n_periods):
            # Available funds
            budget = self.annual_budgets[t] if t < len(self.annual_budgets) else 0
            available = budget + carryover - debt

            # Expenditure with borrowing if needed
            expenditure = expenditures[t] if t < len(expenditures) else 0
            max_spend = available + self.borrowing_limit
            actual_spend = min(expenditure, max_spend)

            # Update carryover
            unused = available - actual_spend
            carryover = max(0, unused) * self.carryover_rate

            # Update debt
            if actual_spend > available:
                new_debt = actual_spend - available
                debt = (debt + new_debt) * (1 + self.interest_rate)
            else:
                debt = max(0, debt * (1 + self.interest_rate) - unused)

            results.append({
                "year": t,
                "budget": budget,
                "available": available,
                "planned_expenditure": expenditure,
                "actual_expenditure": actual_spend,
                "unused": unused,
                "carryover": carryover,
                "debt": debt,
                "budget_status": "surplus" if unused > 0 else "deficit" if debt > 0 else "balanced"
            })

        return pd.DataFrame(results)

    def calculate_funding_gap(
        self,
        required_expenditures: List[float]
    ) -> Dict:
        """
        Calculate funding gap analysis.

        Args:
            required_expenditures: Required expenditures per period

        Returns:
            Dictionary with funding gap analysis
        """
        simulation = self.simulate_budget_flow(required_expenditures)

        total_required = sum(required_expenditures)
        total_available = sum(self.annual_budgets)

        deficits = simulation[simulation["budget_status"] == "deficit"]

        return {
            "total_required": total_required,
            "total_available": total_available,
            "funding_gap": max(0, total_required - total_available),
            "n_deficit_years": len(deficits),
            "max_debt": simulation["debt"].max(),
            "simulation": simulation
        }


class StochasticBudget:
    """Model budget uncertainty with probability distributions."""

    def __init__(
        self,
        base_budget: float,
        uncertainty_type: str = "normal",
        uncertainty_params: Optional[Dict] = None
    ):
        """
        Initialize stochastic budget model.

        Args:
            base_budget: Expected budget amount
            uncertainty_type: "normal", "uniform", "triangular", "lognormal"
            uncertainty_params: Distribution parameters
        """
        self.base_budget = base_budget
        self.uncertainty_type = uncertainty_type
        self.params = uncertainty_params or self._default_params()

    def _default_params(self) -> Dict:
        """Generate default uncertainty parameters."""
        if self.uncertainty_type == "normal":
            return {"std": self.base_budget * 0.1}
        elif self.uncertainty_type == "uniform":
            return {"low": self.base_budget * 0.8, "high": self.base_budget * 1.2}
        elif self.uncertainty_type == "triangular":
            return {
                "low": self.base_budget * 0.8,
                "mode": self.base_budget,
                "high": self.base_budget * 1.2
            }
        elif self.uncertainty_type == "lognormal":
            return {"sigma": 0.2}
        return {}

    def sample_budget(self, n_samples: int = 1000) -> np.ndarray:
        """
        Generate budget samples from distribution.

        Args:
            n_samples: Number of samples to generate

        Returns:
            Array of budget samples
        """
        if self.uncertainty_type == "normal":
            return np.random.normal(
                self.base_budget,
                self.params.get("std", self.base_budget * 0.1),
                n_samples
            )
        elif self.uncertainty_type == "uniform":
            return np.random.uniform(
                self.params.get("low", self.base_budget * 0.8),
                self.params.get("high", self.base_budget * 1.2),
                n_samples
            )
        elif self.uncertainty_type == "triangular":
            return np.random.triangular(
                self.params.get("low", self.base_budget * 0.8),
                self.params.get("mode", self.base_budget),
                self.params.get("high", self.base_budget * 1.2),
                n_samples
            )
        elif self.uncertainty_type == "lognormal":
            mu = np.log(self.base_budget)
            sigma = self.params.get("sigma", 0.2)
            return np.random.lognormal(mu, sigma, n_samples)
        else:
            return np.full(n_samples, self.base_budget)

    def feasibility_probability(
        self,
        required_budget: float,
        n_samples: int = 10000
    ) -> float:
        """
        Calculate probability that budget will be sufficient.

        Args:
            required_budget: Required budget amount
            n_samples: Number of Monte Carlo samples

        Returns:
            Probability (0-1) that budget >= required
        """
        samples = self.sample_budget(n_samples)
        return np.mean(samples >= required_budget)

    def calculate_value_at_risk(
        self,
        required_budget: float,
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Value at Risk for budget shortfall.

        Args:
            required_budget: Required budget amount
            confidence_level: Confidence level (e.g., 0.95 for 95%)

        Returns:
            VaR amount (positive = shortfall risk)
        """
        samples = self.sample_budget(10000)
        shortfalls = np.maximum(0, required_budget - samples)
        return np.percentile(shortfalls, confidence_level * 100)


# Pre-defined cost templates for common interventions
INTERVENTION_COST_TEMPLATES = {
    "hospital_50bed": {
        "construction_cost": 40_000_000,
        "equipment_cost": 8_000_000,
        "land_acquisition": 1_000_000,
        "permitting_cost": 500_000,
        "personnel_cost": 5_000_000,
        "maintenance_cost": 1_000_000,
        "utilities_cost": 500_000,
        "supplies_cost": 2_000_000,
        "implementation_years": 5,
        "operational_lifetime": 30
    },
    "ems_station": {
        "construction_cost": 1_500_000,
        "equipment_cost": 400_000,
        "land_acquisition": 100_000,
        "personnel_cost": 800_000,
        "maintenance_cost": 100_000,
        "utilities_cost": 50_000,
        "implementation_years": 1,
        "operational_lifetime": 25
    },
    "fire_station": {
        "construction_cost": 2_500_000,
        "equipment_cost": 400_000,
        "land_acquisition": 100_000,
        "personnel_cost": 1_200_000,
        "maintenance_cost": 150_000,
        "utilities_cost": 75_000,
        "implementation_years": 2,
        "operational_lifetime": 25
    },
    "telehealth": {
        "equipment_cost": 200_000,
        "design_cost": 50_000,
        "personnel_cost": 100_000,
        "maintenance_cost": 30_000,
        "utilities_cost": 10_000,
        "implementation_years": 1,
        "operational_lifetime": 10
    },
    "disaster_prep_program": {
        "personnel_cost": 300_000,
        "supplies_cost": 150_000,
        "training_cost": 50_000,
        "implementation_years": 1,
        "operational_lifetime": 5
    }
}


def create_intervention_cost(
    intervention_type: str,
    state_code: Optional[str] = None,
    custom_params: Optional[Dict] = None
) -> InterventionCost:
    """
    Create intervention cost model from template.

    Args:
        intervention_type: Type of intervention (from templates)
        state_code: State code for regional adjustment
        custom_params: Custom parameters to override template

    Returns:
        InterventionCost object
    """
    template = INTERVENTION_COST_TEMPLATES.get(intervention_type, {})

    if custom_params:
        template.update(custom_params)

    components = CostComponents(
        construction_cost=template.get("construction_cost", 0),
        equipment_cost=template.get("equipment_cost", 0),
        land_acquisition=template.get("land_acquisition", 0),
        permitting_cost=template.get("permitting_cost", 0),
        design_cost=template.get("design_cost", 0),
        personnel_cost=template.get("personnel_cost", 0),
        maintenance_cost=template.get("maintenance_cost", 0),
        utilities_cost=template.get("utilities_cost", 0),
        supplies_cost=template.get("supplies_cost", 0),
        training_cost=template.get("training_cost", 0)
    )

    return InterventionCost(
        components=components,
        implementation_years=template.get("implementation_years", 1),
        operational_lifetime=template.get("operational_lifetime", 20),
        state_code=state_code
    )


if __name__ == "__main__":
    # Example usage
    cost = create_intervention_cost("hospital_50bed", state_code="CA")

    print("Cost Breakdown:")
    breakdown = cost.get_cost_breakdown()
    for key, value in breakdown.items():
        print(f"  {key}: ${value:,.0f}")

    print(f"\nRegional multiplier: {cost.get_regional_multiplier()}")
    print(f"NPV Cost: ${cost.calculate_npv_cost():,.0f}")
