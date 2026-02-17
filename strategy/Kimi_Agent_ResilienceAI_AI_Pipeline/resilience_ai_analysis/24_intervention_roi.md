# ResilienceAI Intervention ROI Analysis & Enhancement Design

## Executive Summary

This document provides a comprehensive analysis of the current intervention ROI capabilities in ResilienceAI and designs a next-generation ROI optimization platform. The analysis covers advanced cost modeling, benefit quantification, optimization algorithms, and resource allocation frameworks for disaster preparedness interventions.

---

## 1. Current State Analysis

### 1.1 Existing ROI Implementation (`src/intervention_roi.py`)

**Current Capabilities:**
- Basic intervention database with 6 intervention types
- Simple cost-benefit calculation per county
- Risk reduction estimation with diminishing returns
- Population-scaled benefit calculation
- County-level intervention ranking
- Best county identification for interventions

**Current Intervention Database:**
| Intervention | Base Cost | Risk Reduction | Category | Implementation |
|--------------|-----------|----------------|----------|----------------|
| Build New Hospital (50-bed) | $50M | 12% | healthcare | 5 years |
| Build EMS Station | $2M | 6% | emergency | 1 year |
| Build Fire Station | $3M | 5% | emergency | 2 years |
| Telehealth Infrastructure | $250K | 8% | healthcare | 1 year |
| Disaster Prep Program | $500K | 10% | preparedness | 1 year |
| Poverty Reduction | $10M | 15% | social | 5 years |

**Current ROI Formula:**
```
Cost per person helped = Investment / (Population × Risk Reduction)
Risk adjustment = 0.5 + current_risk (0.5x to 1.5x)
Population factor = clamp(pop / 50000, 0.3, 1.5)
Diminishing returns = (1 - e^(-multiplier)) / (1 - e^(-1))
```

### 1.2 Current Limitations

1. **Limited Intervention Types**: Only 6 interventions; real-world scenarios require 50+
2. **Static Cost Model**: No regional cost variations, inflation, or economies of scale
3. **Simplistic Benefit Quantification**: Only risk reduction; missing lives saved, economic impact
4. **No Time Value**: Missing NPV, discount rates, multi-year cash flows
5. **No Budget Constraints**: Cannot optimize under limited budgets
6. **No Synergies**: Interventions treated independently
7. **No Uncertainty**: Point estimates only; no confidence intervals
8. **Limited Optimization**: Simple ranking; no combinatorial optimization
9. **No Equity Considerations**: Missing distributional impact analysis
10. **No Dynamic Updates**: Static models; no learning from outcomes

---

## 2. Proposed ROI Optimization Platform Architecture

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI ROI OPTIMIZATION PLATFORM                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Cost Model   │  │ Benefit      │  │ Optimization │  │ Visualization│   │
│  │ Engine       │  │ Quantifier   │  │ Engine       │  │ & Reporting  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │           │
│  ┌──────┴─────────────────┴─────────────────┴─────────────────┴───────┐   │
│  │                    ROI Calculation Framework                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │   │
│  │  │ NPV     │ │ IRR     │ │ BCR     │ │ CE      │ │ ROI     │      │   │
│  │  │ Model   │ │ Model   │ │ Model   │ │ Model   │ │ Score   │      │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘      │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│         │                                                                 │
│  ┌──────┴────────────────────────────────────────────────────────────┐   │
│  │                    Decision Support Layer                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │   │
│  │  │ Budget   │ │ Multi-   │ │ Sensitivity│ │ Scenario │              │   │
│  │  │ Optimizer│ │ Criteria │ │ Analysis │ │ Planner  │              │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Module Structure

```
src/roi/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── cost_models.py          # Advanced cost modeling
│   ├── benefit_models.py       # Benefit quantification
│   ├── roi_calculator.py       # Core ROI calculations
│   └── time_value.py           # NPV, discounting
├── optimization/
│   ├── __init__.py
│   ├── budget_optimizer.py     # Budget constraint optimization
│   ├── portfolio_optimizer.py  # Multi-intervention optimization
│   ├── prioritization.py       # Prioritization algorithms
│   └── multi_criteria.py       # MCDA framework
├── analysis/
│   ├── __init__.py
│   ├── sensitivity.py          # Sensitivity analysis
│   ├── uncertainty.py          # Monte Carlo simulation
│   ├── equity.py               # Equity impact analysis
│   └── scenarios.py            # Scenario modeling
├── data/
│   ├── __init__.py
│   ├── interventions.py        # Intervention database
│   ├── cost_data.py            # Regional cost data
│   └── effectiveness.py        # Effectiveness evidence
├── visualization/
│   ├── __init__.py
│   ├── roi_charts.py           # ROI visualizations
│   ├── dashboards.py           # Interactive dashboards
│   └── reports.py              # Report generation
└── integration/
    ├── __init__.py
    ├── pipeline.py             # Pipeline integration
    └── api.py                  # API endpoints
```

---

## 3. Advanced Cost Modeling Framework

### 3.1 Cost Component Model

```python
@dataclass
class InterventionCost:
    """Comprehensive cost model for interventions."""
    
    # Capital Costs
    construction_cost: float          # Building/infrastructure
    equipment_cost: float             # Equipment and technology
    land_acquisition: float           # Land and property
    permitting_cost: float            # Permits and regulatory
    
    # Operating Costs (annual)
    personnel_cost: float             # Staff salaries and benefits
    maintenance_cost: float           # Maintenance and repairs
    utilities_cost: float             # Utilities and services
    supplies_cost: float              # Supplies and consumables
    
    # Indirect Costs
    training_cost: float              # Training and development
    administrative_cost: float        # Overhead and administration
    contingency: float                # Risk contingency (typically 10-20%)
    
    # Temporal Parameters
    implementation_years: int         # Years to implement
    operational_lifetime: int         # Years of operation
    discount_rate: float = 0.03       # Annual discount rate
    
    # Regional Adjustments
    region_code: str = None           # Geographic region
    cost_index: float = 1.0           # Regional cost multiplier
    
    def calculate_npv_cost(self) -> float:
        """Calculate net present value of total costs."""
        # Capital costs (upfront)
        capital = (self.construction_cost + self.equipment_cost + 
                   self.land_acquisition + self.permitting_cost)
        
        # Annual operating costs
        annual_operating = (self.personnel_cost + self.maintenance_cost + 
                           self.utilities_cost + self.supplies_cost +
                           self.training_cost + self.administrative_cost)
        
        # NPV of operating costs
        operating_npv = sum(
            annual_operating / ((1 + self.discount_rate) ** t)
            for t in range(1, self.operational_lifetime + 1)
        )
        
        # Add contingency
        total = (capital + operating_npv) * (1 + self.contingency)
        
        # Apply regional adjustment
        return total * self.cost_index
```

### 3.2 Regional Cost Index Database

```python
REGIONAL_COST_INDEX = {
    # US Census Regions
    "Northeast": {
        "New England": {"CT": 1.25, "ME": 1.10, "MA": 1.35, "NH": 1.15, 
                        "RI": 1.20, "VT": 1.10},
        "Mid-Atlantic": {"NJ": 1.30, "NY": 1.40, "PA": 1.05}
    },
    "Midwest": {
        "East North Central": {"IL": 1.10, "IN": 0.95, "MI": 0.95, 
                               "OH": 0.90, "WI": 0.95},
        "West North Central": {"IA": 0.85, "KS": 0.85, "MN": 1.00, 
                               "MO": 0.85, "NE": 0.85, "ND": 0.80, "SD": 0.80}
    },
    "South": {
        "South Atlantic": {"DE": 1.05, "FL": 1.00, "GA": 0.90, "MD": 1.15,
                          "NC": 0.90, "SC": 0.85, "VA": 1.00, "WV": 0.80},
        "East South Central": {"AL": 0.80, "KY": 0.80, "MS": 0.75, "TN": 0.85},
        "West South Central": {"AR": 0.75, "LA": 0.80, "OK": 0.75, "TX": 0.90}
    },
    "West": {
        "Mountain": {"AZ": 0.95, "CO": 1.05, "ID": 0.90, "MT": 0.85,
                     "NV": 1.00, "NM": 0.80, "UT": 0.90, "WY": 0.85},
        "Pacific": {"AK": 1.30, "CA": 1.35, "HI": 1.50, "OR": 1.05, "WA": 1.10}
    }
}
```

### 3.3 Economies of Scale Model

```python
class EconomiesOfScale:
    """Model economies of scale for intervention costs."""
    
    def __init__(self, base_cost: float, scale_factor: float = 0.85):
        """
        Args:
            base_cost: Cost for baseline scale (e.g., 1 unit)
            scale_factor: Cost reduction per doubling (0.85 = 15% reduction)
        """
        self.base_cost = base_cost
        self.scale_factor = scale_factor
    
    def calculate_scaled_cost(self, quantity: int) -> float:
        """Calculate cost with economies of scale."""
        if quantity <= 0:
            return 0
        
        # Calculate number of doublings
        doublings = max(0, np.log2(quantity))
        
        # Apply scale factor
        scale_multiplier = self.scale_factor ** doublings
        
        return self.base_cost * quantity * scale_multiplier
    
    def calculate_marginal_cost(self, quantity: int) -> float:
        """Calculate marginal cost at given quantity."""
        cost_n = self.calculate_scaled_cost(quantity)
        cost_n_minus_1 = self.calculate_scaled_cost(quantity - 1)
        return cost_n - cost_n_minus_1
```

---

## 4. Benefit Quantification Framework

### 4.1 Multi-Dimensional Benefit Model

```python
@dataclass
class InterventionBenefits:
    """Comprehensive benefit quantification model."""
    
    # Health Benefits
    lives_saved: float                # Lives saved per year
    dalys_averted: float              # Disability-adjusted life years
    hospitalizations_prevented: int   # Hospitalizations avoided
    er_visits_prevented: int          # ER visits avoided
    
    # Economic Benefits
    property_damage_avoided: float    # Property damage prevented ($)
    business_interruption_avoided: float  # Business losses prevented ($)
    infrastructure_damage_avoided: float  # Infrastructure savings ($)
    
    # Social Benefits
    displacement_prevented: int       # People not displaced
    jobs_protected: int               # Jobs protected
    community_resilience_score: float # Resilience improvement (0-1)
    
    # System Benefits
    response_time_improvement: float  # Minutes improved
    capacity_increase: float          # Service capacity increase (%)
    coordination_improvement: float   # Coordination score improvement
    
    # Valuation Parameters
    value_of_statistical_life: float = 10_000_000  # VSL in USD
    cost_per_daly: float = 50_000                  # Cost-effectiveness threshold
    
    def calculate_total_value(self) -> Dict[str, float]:
        """Calculate total monetary value of benefits."""
        
        # Health value
        health_value = (
            self.lives_saved * self.value_of_statistical_life +
            self.dalys_averted * self.cost_per_daly +
            self.hospitalizations_prevented * 15_000 +  # Avg hospitalization cost
            self.er_visits_prevented * 1_500             # Avg ER visit cost
        )
        
        # Economic value
        economic_value = (
            self.property_damage_avoided +
            self.business_interruption_avoided +
            self.infrastructure_damage_avoided
        )
        
        # Social value (using shadow prices)
        social_value = (
            self.displacement_prevented * 5_000 +       # Cost per displacement
            self.jobs_protected * 50_000                # Avg annual wage
        )
        
        return {
            "health_value": health_value,
            "economic_value": economic_value,
            "social_value": social_value,
            "total_value": health_value + economic_value + social_value
        }
```

### 4.2 Risk Reduction Effectiveness Model

```python
class RiskReductionModel:
    """Model risk reduction effectiveness with uncertainty."""
    
    def __init__(
        self,
        baseline_effectiveness: float,
        effectiveness_std: float,
        risk_type_weights: Dict[str, float]
    ):
        self.baseline = baseline_effectiveness
        self.std = effectiveness_std
        self.risk_weights = risk_type_weights
    
    def calculate_adjusted_effectiveness(
        self,
        county_risk_profile: Dict[str, float],
        implementation_quality: float = 1.0
    ) -> Dict[str, float]:
        """Calculate effectiveness adjusted for local risk profile."""
        
        # Weighted average based on local risk composition
        weighted_effectiveness = sum(
            self.baseline * self.risk_weights.get(risk_type, 0) * risk_level
            for risk_type, risk_level in county_risk_profile.items()
        )
        
        # Adjust for implementation quality (0.5 to 1.5)
        adjusted = weighted_effectiveness * implementation_quality
        
        # Calculate confidence interval
        ci_lower = max(0, adjusted - 1.96 * self.std)
        ci_upper = min(1, adjusted + 1.96 * self.std)
        
        return {
            "point_estimate": adjusted,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "std": self.std
        }
```

---

## 5. ROI Calculation Framework

### 5.1 Comprehensive ROI Metrics

```python
class ROICalculator:
    """Calculate comprehensive ROI metrics."""
    
    def __init__(self, discount_rate: float = 0.03):
        self.discount_rate = discount_rate
    
    def calculate_npv(
        self,
        costs: List[float],
        benefits: List[float],
        years: int
    ) -> float:
        """Calculate Net Present Value."""
        npv = 0
        for t in range(years):
            net = benefits[t] - costs[t]
            npv += net / ((1 + self.discount_rate) ** t)
        return npv
    
    def calculate_irr(
        self,
        costs: List[float],
        benefits: List[float],
        years: int
    ) -> Optional[float]:
        """Calculate Internal Rate of Return."""
        cash_flows = [-costs[0]] + [benefits[t] - costs[t] for t in range(1, years)]
        
        try:
            return npf.irr(cash_flows)
        except:
            return None
    
    def calculate_benefit_cost_ratio(
        self,
        costs: List[float],
        benefits: List[float],
        years: int
    ) -> float:
        """Calculate Benefit-Cost Ratio."""
        pv_benefits = sum(
            benefits[t] / ((1 + self.discount_rate) ** t)
            for t in range(years)
        )
        pv_costs = sum(
            costs[t] / ((1 + self.discount_rate) ** t)
            for t in range(years)
        )
        return pv_benefits / pv_costs if pv_costs > 0 else float('inf')
    
    def calculate_cost_effectiveness(
        self,
        total_cost: float,
        effectiveness_units: float,
        effectiveness_type: str = "lives_saved"
    ) -> Dict[str, float]:
        """Calculate cost-effectiveness metrics."""
        
        ce_ratio = total_cost / effectiveness_units if effectiveness_units > 0 else float('inf')
        
        # Compare to benchmarks
        benchmarks = {
            "lives_saved": 10_000_000,           # VSL
            "dalys_averted": 50_000,             # WHO threshold
            "qalys_gained": 50_000,              # NICE threshold
            "hospitalizations_prevented": 15_000,  # Avg cost
            "disasters_mitigated": 1_000_000_000   # Avg disaster cost
        }
        
        benchmark = benchmarks.get(effectiveness_type, float('inf'))
        is_cost_effective = ce_ratio < benchmark
        
        return {
            "ce_ratio": ce_ratio,
            "benchmark": benchmark,
            "is_cost_effective": is_cost_effective,
            "value_for_money": benchmark / ce_ratio if ce_ratio > 0 else float('inf')
        }
    
    def calculate_roi_score(
        self,
        npv: float,
        total_investment: float,
        payback_period: float,
        risk_score: float
    ) -> float:
        """Calculate composite ROI score (0-100)."""
        
        # NPV component (40% weight)
        npv_component = min(40, max(0, npv / total_investment * 20))
        
        # Payback component (30% weight) - shorter is better
        payback_component = max(0, 30 - payback_period * 3)
        
        # Risk component (30% weight) - higher risk reduction is better
        risk_component = risk_score * 30
        
        return npv_component + payback_component + risk_component
```

### 5.2 Intervention Portfolio ROI

```python
class PortfolioROI:
    """Calculate ROI for intervention portfolios."""
    
    def __init__(self, interventions: List[Dict]):
        self.interventions = interventions
    
    def calculate_portfolio_npv(self) -> float:
        """Calculate combined NPV of all interventions."""
        return sum(inv.get("npv", 0) for inv in self.interventions)
    
    def calculate_synergy_effects(self) -> Dict[str, float]:
        """Calculate synergy effects between interventions."""
        
        synergies = {
            "healthcare_emergency": 0.15,    # Hospitals + EMS
            "preparedness_response": 0.20,   # Prep + Response capacity
            "social_healthcare": 0.10,       # Poverty reduction + Health
            "infrastructure_tech": 0.12,     # Infrastructure + Telehealth
        }
        
        total_synergy = 0
        categories = [inv["category"] for inv in self.interventions]
        
        for pair, effect in synergies.items():
            cat1, cat2 = pair.split("_")
            if cat1 in categories and cat2 in categories:
                total_synergy += effect
        
        return {
            "synergy_multiplier": 1 + total_synergy,
            "synergy_value": total_synergy * self.calculate_portfolio_npv()
        }
    
    def calculate_diversification_benefit(self) -> float:
        """Calculate risk diversification benefit."""
        
        # More categories = better diversification
        categories = set(inv["category"] for inv in self.interventions)
        diversification_score = len(categories) / 5  # Normalize to 5 categories
        
        # Risk reduction from diversification
        return min(0.15, diversification_score * 0.05)
```

---

## 6. Resource Allocation Optimization

### 6.1 Budget-Constrained Optimization

```python
from scipy.optimize import minimize, differential_evolution
import numpy as np

class BudgetOptimizer:
    """Optimize intervention allocation under budget constraints."""
    
    def __init__(
        self,
        interventions: List[Dict],
        counties: pd.DataFrame,
        budget: float
    ):
        self.interventions = interventions
        self.counties = counties
        self.budget = budget
        self.n_interventions = len(interventions)
        self.n_counties = len(counties)
    
    def optimize_knapsack(
        self,
        objective: str = "lives_saved",
        equity_weight: float = 0.2
    ) -> Dict:
        """
        Solve budget allocation as 0-1 knapsack problem.
        
        Args:
            objective: "lives_saved", "risk_reduction", "npv", "equity"
            equity_weight: Weight for equity considerations (0-1)
        """
        
        # Generate all feasible intervention-county combinations
        items = []
        for i, intervention in enumerate(self.interventions):
            for j, (_, county) in enumerate(self.counties.iterrows()):
                roi = self._calculate_roi(intervention, county)
                
                items.append({
                    "intervention_idx": i,
                    "county_idx": j,
                    "cost": roi["cost"],
                    "benefit": roi[objective],
                    "equity_score": self._calculate_equity_score(county),
                    "roi_data": roi
                })
        
        # Sort by benefit-to-cost ratio
        items.sort(key=lambda x: x["benefit"] / x["cost"], reverse=True)
        
        # Greedy knapsack selection
        selected = []
        remaining_budget = self.budget
        
        for item in items:
            if item["cost"] <= remaining_budget:
                # Check for conflicts (same county, similar intervention)
                if not self._has_conflict(selected, item):
                    selected.append(item)
                    remaining_budget -= item["cost"]
        
        return {
            "selected_interventions": selected,
            "total_cost": self.budget - remaining_budget,
            "total_benefit": sum(item["benefit"] for item in selected),
            "budget_utilization": (self.budget - remaining_budget) / self.budget,
            "counties_covered": len(set(item["county_idx"] for item in selected))
        }
    
    def optimize_milp(
        self,
        objective: str = "lives_saved",
        constraints: Dict = None
    ) -> Dict:
        """
        Solve using Mixed Integer Linear Programming.
        
        More sophisticated than knapsack; handles complex constraints.
        """
        try:
            from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpBinary
        except ImportError:
            return {"error": "PuLP required for MILP optimization"}
        
        # Create problem
        prob = LpProblem("Intervention_Allocation", LpMaximize)
        
        # Decision variables: x[i,j] = 1 if intervention i in county j
        x = LpVariable.dicts(
            "x",
            ((i, j) for i in range(self.n_interventions) 
                    for j in range(self.n_counties)),
            cat=LpBinary
        )
        
        # Objective function
        prob += lpSum(
            x[i, j] * self._calculate_benefit(i, j, objective)
            for i in range(self.n_interventions)
            for j in range(self.n_counties)
        )
        
        # Budget constraint
        prob += lpSum(
            x[i, j] * self._calculate_cost(i, j)
            for i in range(self.n_interventions)
            for j in range(self.n_counties)
        ) <= self.budget
        
        # One intervention per county constraint (optional)
        if constraints and constraints.get("one_per_county"):
            for j in range(self.n_counties):
                prob += lpSum(x[i, j] for i in range(self.n_interventions)) <= 1
        
        # Minimum coverage constraint
        if constraints and "min_counties" in constraints:
            prob += lpSum(
                x[i, j]
                for i in range(self.n_interventions)
                for j in range(self.n_counties)
            ) >= constraints["min_counties"]
        
        # Solve
        prob.solve()
        
        # Extract solution
        selected = [
            {"intervention": i, "county": j}
            for i in range(self.n_interventions)
            for j in range(self.n_counties)
            if x[i, j].value() == 1
        ]
        
        return {
            "selected_interventions": selected,
            "objective_value": prob.objective.value(),
            "status": prob.status
        }
    
    def _calculate_roi(self, intervention: Dict, county: pd.Series) -> Dict:
        """Calculate ROI for intervention-county pair."""
        # Implementation from InterventionROICalculator
        pass
    
    def _calculate_equity_score(self, county: pd.Series) -> float:
        """Calculate equity score for county (higher = more disadvantaged)."""
        svi = county.get("svi", 0.5)
        poverty_rate = county.get("poverty_rate", 0.15)
        return (svi + poverty_rate) / 2
    
    def _has_conflict(self, selected: List[Dict], new_item: Dict) -> bool:
        """Check if new item conflicts with already selected items."""
        for item in selected:
            # Same county, same category
            if (item["county_idx"] == new_item["county_idx"] and
                item["intervention_idx"] == new_item["intervention_idx"]):
                return True
        return False
```

### 6.2 Multi-Objective Optimization

```python
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

class MultiObjectiveOptimizer:
    """Multi-objective optimization for intervention allocation."""
    
    def __init__(self, interventions: List[Dict], counties: pd.DataFrame):
        self.interventions = interventions
        self.counties = counties
    
    def optimize_nsga2(
        self,
        budget: float,
        objectives: List[str] = ["lives_saved", "equity", "cost_efficiency"]
    ) -> Dict:
        """
        NSGA-II multi-objective optimization.
        
        Returns Pareto frontier of solutions.
        """
        
        class InterventionProblem(Problem):
            def __init__(self, n_interventions, n_counties, budget):
                super().__init__(
                    n_var=n_interventions * n_counties,
                    n_obj=len(objectives),
                    n_constr=1,
                    xl=0,
                    xu=1,
                    vtype=bool
                )
                self.budget = budget
            
            def _evaluate(self, x, out, *args, **kwargs):
                # Reshape decision variables
                allocation = x.reshape(n_interventions, n_counties)
                
                # Calculate objectives
                f = np.zeros((x.shape[0], len(objectives)))
                
                for i, obj in enumerate(objectives):
                    f[:, i] = self._calculate_objective(allocation, obj)
                
                # Budget constraint
                g = np.sum(allocation * costs) - self.budget
                
                out["F"] = f
                out["G"] = g
        
        problem = InterventionProblem(
            len(self.interventions),
            len(self.counties),
            budget
        )
        
        algorithm = NSGA2(pop_size=100)
        
        res = minimize(
            problem,
            algorithm,
            ("n_gen", 200),
            seed=42,
            verbose=False
        )
        
        return {
            "pareto_front": res.F,
            "solutions": res.X,
            "n_solutions": len(res.F)
        }
```

---

## 7. Prioritization Algorithms

### 7.1 Multi-Criteria Decision Analysis (MCDA)

```python
class MCDAPrioritizer:
    """Multi-criteria decision analysis for intervention prioritization."""
    
    def __init__(self, criteria: List[Dict]):
        """
        Args:
            criteria: List of criterion dicts with 'name', 'weight', 'direction'
        """
        self.criteria = criteria
        self.weights = np.array([c["weight"] for c in criteria])
        self.weights = self.weights / self.weights.sum()  # Normalize
    
    def ahp_weights(self, comparison_matrix: np.ndarray) -> np.ndarray:
        """Calculate criteria weights using Analytic Hierarchy Process."""
        
        # Normalize comparison matrix
        col_sums = comparison_matrix.sum(axis=0)
        normalized = comparison_matrix / col_sums
        
        # Calculate eigenvector (weights)
        weights = normalized.mean(axis=1)
        
        # Calculate consistency ratio
        n = len(weights)
        lambda_max = (comparison_matrix @ weights).sum() / weights.sum()
        ci = (lambda_max - n) / (n - 1)
        ri = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}
        cr = ci / ri.get(n, 1.49)
        
        if cr > 0.1:
            print(f"Warning: Inconsistent comparison matrix (CR={cr:.3f})")
        
        return weights
    
    def topsis_ranking(
        self,
        alternatives: pd.DataFrame
    ) -> pd.DataFrame:
        """
        TOPSIS (Technique for Order Preference by Similarity to Ideal Solution).
        """
        
        # Normalize decision matrix
        normalized = alternatives.copy()
        for col in normalized.columns:
            norm = np.sqrt((normalized[col] ** 2).sum())
            if norm > 0:
                normalized[col] = normalized[col] / norm
        
        # Weight normalized matrix
        weighted = normalized * self.weights
        
        # Determine ideal and anti-ideal solutions
        ideal = weighted.max()
        anti_ideal = weighted.min()
        
        # Calculate distances
        d_ideal = np.sqrt(((weighted - ideal) ** 2).sum(axis=1))
        d_anti_ideal = np.sqrt(((weighted - anti_ideal) ** 2).sum(axis=1))
        
        # Calculate closeness coefficient
        closeness = d_anti_ideal / (d_ideal + d_anti_ideal)
        
        # Rank alternatives
        result = alternatives.copy()
        result["closeness"] = closeness
        result["rank"] = closeness.rank(ascending=False)
        
        return result.sort_values("rank")
    
    def promethee_ranking(
        self,
        alternatives: pd.DataFrame,
        preference_function: str = "usual"
    ) -> pd.DataFrame:
        """
        PROMETHEE (Preference Ranking Organization Method).
        """
        
        n = len(alternatives)
        preference_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Calculate preference
                    pref = 0
                    for k, criterion in enumerate(self.criteria):
                        diff = alternatives.iloc[i, k] - alternatives.iloc[j, k]
                        
                        if criterion["direction"] == "maximize":
                            pref += self.weights[k] * self._preference(diff, preference_function)
                        else:
                            pref += self.weights[k] * self._preference(-diff, preference_function)
                    
                    preference_matrix[i, j] = pref
        
        # Calculate positive and negative flows
        positive_flow = preference_matrix.sum(axis=1) / (n - 1)
        negative_flow = preference_matrix.sum(axis=0) / (n - 1)
        
        # Net flow
        net_flow = positive_flow - negative_flow
        
        result = alternatives.copy()
        result["net_flow"] = net_flow
        result["rank"] = net_flow.rank(ascending=False)
        
        return result.sort_values("rank")
    
    def _preference(self, diff: float, function: str) -> float:
        """Calculate preference function value."""
        if function == "usual":
            return 1 if diff > 0 else 0
        elif function == "linear":
            return max(0, min(1, diff))
        elif function == "gaussian":
            return 1 - np.exp(-diff ** 2 / 2)
        return 0
```

### 7.2 Dynamic Prioritization

```python
class DynamicPrioritizer:
    """Dynamic prioritization based on real-time conditions."""
    
    def __init__(self, base_priorities: pd.DataFrame):
        self.base_priorities = base_priorities
        self.adjustment_factors = {
            "weather_alert": 1.5,
            "resource_surge": 1.3,
            "funding_increase": 1.2,
            "emergency_declaration": 2.0
        }
    
    def adjust_for_weather(
        self,
        priorities: pd.DataFrame,
        weather_forecast: Dict
    ) -> pd.DataFrame:
        """Adjust priorities based on weather forecast."""
        
        adjusted = priorities.copy()
        
        # Increase priority for areas in forecast path
        for idx, row in adjusted.iterrows():
            county = row["county_fips"]
            
            if county in weather_forecast.get("affected_areas", []):
                # Boost emergency response interventions
                if row["category"] == "emergency":
                    adjusted.loc[idx, "priority"] *= self.adjustment_factors["weather_alert"]
                
                # Boost healthcare preparedness
                if row["category"] == "healthcare":
                    adjusted.loc[idx, "priority"] *= 1.3
        
        return adjusted.sort_values("priority", ascending=False)
    
    def adjust_for_resource_availability(
        self,
        priorities: pd.DataFrame,
        available_resources: Dict
    ) -> pd.DataFrame:
        """Adjust priorities based on resource availability."""
        
        adjusted = priorities.copy()
        
        # Deprioritize if resources unavailable
        for idx, row in adjusted.iterrows():
            intervention_type = row["intervention_key"]
            
            if intervention_type in available_resources:
                availability = available_resources[intervention_type]
                
                # Reduce priority if resources scarce
                if availability < 0.3:
                    adjusted.loc[idx, "priority"] *= 0.7
                # Boost if resources abundant
                elif availability > 0.8:
                    adjusted.loc[idx, "priority"] *= 1.1
        
        return adjusted.sort_values("priority", ascending=False)
```

---

## 8. Cost-Effectiveness Analysis

### 8.1 Incremental Cost-Effectiveness Ratio (ICER)

```python
class ICERAnalyzer:
    """Calculate Incremental Cost-Effectiveness Ratios."""
    
    def __init__(self, willingness_to_pay: float = 50_000):
        self.wtp = willingness_to_pay
    
    def calculate_icers(
        self,
        interventions: List[Dict]
    ) -> pd.DataFrame:
        """
        Calculate ICERs for intervention comparisons.
        
        Returns:
            DataFrame with ICERs and dominance information
        """
        
        # Create comparison dataframe
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
        for i in range(1, len(df)):
            # Strongly dominated if higher cost and lower effectiveness
            if df.loc[i, "cost"] >= df.loc[i-1, "cost"]:
                df.loc[i, "dominated"] = True
            
            # Extended dominance check
            if i > 1:
                icer_i = df.loc[i, "icer"]
                icer_i_minus_1 = df.loc[i-1, "icer"]
                if icer_i > icer_i_minus_1:
                    df.loc[i, "dominated"] = True
        
        # Determine cost-effectiveness
        df["cost_effective"] = df["icer"] < self.wtp
        
        return df
    
    def create_acceptability_curve(
        self,
        interventions: List[Dict],
        wtp_range: np.ndarray = None
    ) -> pd.DataFrame:
        """Create cost-effectiveness acceptability curve."""
        
        if wtp_range is None:
            wtp_range = np.linspace(0, 150_000, 100)
        
        results = []
        for wtp in wtp_range:
            self.wtp = wtp
            df = self.calculate_icers(interventions)
            
            # Count cost-effective interventions
            n_ce = df["cost_effective"].sum()
            
            results.append({
                "wtp": wtp,
                "n_cost_effective": n_ce,
                "probability_optimal": n_ce / len(interventions)
            })
        
        return pd.DataFrame(results)
```

### 8.2 Cost-Effectiveness Plane

```python
class CostEffectivenessPlane:
    """Generate cost-effectiveness plane visualizations."""
    
    def __init__(self, reference_intervention: Dict = None):
        self.reference = reference_intervention or {"cost": 0, "effectiveness": 0}
    
    def plot_plane(
        self,
        interventions: List[Dict],
        wtp_thresholds: List[float] = None
    ) -> Dict:
        """
        Generate cost-effectiveness plane data.
        
        Returns:
            Dictionary with plot data and annotations
        """
        
        if wtp_thresholds is None:
            wtp_thresholds = [30_000, 50_000, 100_000]
        
        # Calculate incremental values relative to reference
        plot_data = []
        for inv in interventions:
            incr_cost = inv["cost"] - self.reference["cost"]
            incr_effect = inv["effectiveness"] - self.reference["effectiveness"]
            
            plot_data.append({
                "intervention": inv["name"],
                "incremental_cost": incr_cost,
                "incremental_effectiveness": incr_effect,
                "icer": incr_cost / incr_effect if incr_effect > 0 else float('inf'),
                "category": inv.get("category", "other")
            })
        
        # Generate WTP lines
        wtp_lines = []
        for wtp in wtp_thresholds:
            # Line from origin with slope = WTP
            x_max = max(d["incremental_effectiveness"] for d in plot_data) * 1.1
            wtp_lines.append({
                "wtp": wtp,
                "x": [0, x_max],
                "y": [0, x_max * wtp]
            })
        
        return {
            "interventions": plot_data,
            "wtp_lines": wtp_lines,
            "quadrants": {
                "ne": "More effective, more costly",
                "nw": "Less effective, more costly (dominated)",
                "se": "More effective, less costly (dominant)",
                "sw": "Less effective, less costly"
            }
        }
```

---

## 9. Budget Constraint Modeling

### 9.1 Multi-Period Budget Model

```python
class MultiPeriodBudget:
    """Model budget constraints across multiple time periods."""
    
    def __init__(
        self,
        annual_budgets: List[float],
        carryover_rate: float = 0.0,
        borrowing_limit: float = 0.0
    ):
        """
        Args:
            annual_budgets: Budget for each year
            carryover_rate: Fraction of unused budget that carries over
            borrowing_limit: Maximum borrowing from future years
        """
        self.annual_budgets = annual_budgets
        self.carryover_rate = carryover_rate
        self.borrowing_limit = borrowing_limit
        self.n_periods = len(annual_budgets)
    
    def simulate_budget_flow(
        self,
        expenditures: List[float]
    ) -> pd.DataFrame:
        """Simulate budget flow over time."""
        
        results = []
        carryover = 0
        debt = 0
        
        for t in range(self.n_periods):
            available = self.annual_budgets[t] + carryover - debt
            spent = min(expenditures[t], available + self.borrowing_limit)
            
            # Update carryover
            unused = available - spent
            carryover = max(0, unused) * self.carryover_rate
            
            # Update debt
            if spent > available:
                debt += spent - available
            
            results.append({
                "year": t,
                "budget": self.annual_budgets[t],
                "available": available,
                "expenditure": spent,
                "unused": unused,
                "carryover": carryover,
                "debt": debt
            })
        
        return pd.DataFrame(results)
    
    def optimize_intertemporal_allocation(
        self,
        intervention_options: List[Dict],
        discount_rate: float = 0.03
    ) -> Dict:
        """
        Optimize allocation across time periods.
        
        Uses dynamic programming to find optimal timing.
        """
        
        # Value function: V(t, budget) = max value from t onwards
        memo = {}
        
        def V(t: int, remaining_budget: float) -> float:
            if t >= self.n_periods:
                return 0
            
            if (t, remaining_budget) in memo:
                return memo[(t, remaining_budget)]
            
            max_value = 0
            
            # Try each possible intervention
            for inv in intervention_options:
                cost = inv["cost"]
                value = inv["npv"] / ((1 + discount_rate) ** t)
                
                if cost <= remaining_budget:
                    future_value = V(t + 1, remaining_budget - cost)
                    total_value = value + future_value
                    max_value = max(max_value, total_value)
            
            # Option to defer
            future_value = V(t + 1, remaining_budget)
            max_value = max(max_value, future_value)
            
            memo[(t, remaining_budget)] = max_value
            return max_value
        
        return {
            "optimal_value": V(0, self.annual_budgets[0]),
            "memo": memo
        }
```

### 9.2 Stochastic Budget Model

```python
class StochasticBudget:
    """Model budget uncertainty with probability distributions."""
    
    def __init__(
        self,
        base_budget: float,
        uncertainty_type: str = "normal",
        uncertainty_params: Dict = None
    ):
        self.base_budget = base_budget
        self.uncertainty_type = uncertainty_type
        self.params = uncertainty_params or {"std": base_budget * 0.1}
    
    def sample_budget(self, n_samples: int = 1000) -> np.ndarray:
        """Generate budget samples from distribution."""
        
        if self.uncertainty_type == "normal":
            return np.random.normal(
                self.base_budget,
                self.params["std"],
                n_samples
            )
        elif self.uncertainty_type == "uniform":
            return np.random.uniform(
                self.params["low"],
                self.params["high"],
                n_samples
            )
        elif self.uncertainty_type == "triangular":
            return np.random.triangular(
                self.params["low"],
                self.params["mode"],
                self.params["high"],
                n_samples
            )
        else:
            return np.full(n_samples, self.base_budget)
    
    def feasibility_probability(
        self,
        required_budget: float,
        n_samples: int = 10000
    ) -> float:
        """Calculate probability that budget will be sufficient."""
        
        samples = self.sample_budget(n_samples)
        return np.mean(samples >= required_budget)
```

---

## 10. Intervention Impact Tracking

### 10.1 Impact Monitoring Framework

```python
class ImpactTracker:
    """Track actual intervention outcomes vs. projections."""
    
    def __init__(self, intervention_id: str, projected_outcomes: Dict):
        self.intervention_id = intervention_id
        self.projected = projected_outcomes
        self.actuals = []
        self.metrics = {}
    
    def record_outcome(
        self,
        timestamp: datetime,
        metric_name: str,
        value: float,
        context: Dict = None
    ):
        """Record an actual outcome."""
        
        self.actuals.append({
            "timestamp": timestamp,
            "metric": metric_name,
            "value": value,
            "context": context or {}
        })
    
    def calculate_variance(self, metric_name: str) -> Dict:
        """Calculate variance between projected and actual."""
        
        projected = self.projected.get(metric_name)
        actual_values = [
            a["value"] for a in self.actuals 
            if a["metric"] == metric_name
        ]
        
        if not actual_values or projected is None:
            return {"error": "Insufficient data"}
        
        actual_mean = np.mean(actual_values)
        
        return {
            "metric": metric_name,
            "projected": projected,
            "actual_mean": actual_mean,
            "absolute_variance": actual_mean - projected,
            "percentage_variance": (actual_mean - projected) / projected * 100,
            "variance_direction": "over" if actual_mean > projected else "under"
        }
    
    def generate_learning_report(self) -> Dict:
        """Generate report for model improvement."""
        
        variances = []
        for metric in self.projected.keys():
            var = self.calculate_variance(metric)
            if "error" not in var:
                variances.append(var)
        
        # Identify systematic biases
        overestimates = [v for v in variances if v["variance_direction"] == "over"]
        underestimates = [v for v in variances if v["variance_direction"] == "under"]
        
        return {
            "intervention_id": self.intervention_id,
            "n_metrics_tracked": len(variances),
            "mean_percentage_variance": np.mean([v["percentage_variance"] 
                                                  for v in variances]),
            "overestimation_rate": len(overestimates) / len(variances) if variances else 0,
            "underestimation_rate": len(underestimates) / len(variances) if variances else 0,
            "recommendations": self._generate_recommendations(variances)
        }
    
    def _generate_recommendations(self, variances: List[Dict]) -> List[str]:
        """Generate recommendations based on variance analysis."""
        
        recommendations = []
        
        # Check for systematic over/under estimation
        mean_var = np.mean([v["percentage_variance"] for v in variances])
        
        if mean_var > 20:
            recommendations.append(
                "Model consistently underestimates outcomes. "
                "Consider increasing effectiveness factors."
            )
        elif mean_var < -20:
            recommendations.append(
                "Model consistently overestimates outcomes. "
                "Consider decreasing effectiveness factors."
            )
        
        return recommendations
```

### 10.2 Feedback Loop Integration

```python
class FeedbackLoop:
    """Integrate impact tracking into model improvement."""
    
    def __init__(self, roi_calculator, impact_tracker):
        self.calculator = roi_calculator
        self.tracker = impact_tracker
        self.learning_rate = 0.1
    
    def update_effectiveness_factors(self) -> Dict:
        """Update effectiveness factors based on actual outcomes."""
        
        report = self.tracker.generate_learning_report()
        
        # Calculate adjustment factor
        mean_variance = report["mean_percentage_variance"]
        adjustment = 1 + (mean_variance / 100) * self.learning_rate
        
        # Apply adjustment
        updated_factors = {}
        for intervention_id, factor in self.calculator.effectiveness_factors.items():
            updated_factors[intervention_id] = factor * adjustment
        
        return {
            "adjustment_factor": adjustment,
            "updated_factors": updated_factors,
            "confidence": 1 - abs(mean_variance) / 100
        }
    
    def calibrate_uncertainty(self) -> Dict:
        """Calibrate uncertainty estimates based on prediction accuracy."""
        
        variances = []
        for metric in self.tracker.projected.keys():
            var = self.tracker.calculate_variance(metric)
            if "error" not in var:
                variances.append(abs(var["percentage_variance"]))
        
        # Update standard deviation
        new_std = np.std(variances) if variances else 0.2
        
        return {
            "calibrated_std": new_std,
            "previous_std": self.calculator.uncertainty_std,
            "improvement": new_std < self.calculator.uncertainty_std
        }
```

---

## 11. ROI Visualization & Reporting

### 11.1 Interactive ROI Dashboard

```python
class ROIDashboard:
    """Generate interactive ROI visualizations."""
    
    def __init__(self, roi_data: pd.DataFrame):
        self.data = roi_data
    
    def create_roi_heatmap(self) -> Dict:
        """Create ROI heatmap by county and intervention."""
        
        pivot = self.data.pivot(
            index="county_name",
            columns="intervention",
            values="roi_score"
        )
        
        return {
            "type": "heatmap",
            "data": pivot.to_dict(),
            "colorscale": "RdYlGn",
            "title": "ROI Score by County and Intervention"
        }
    
    def create_efficiency_frontier(self) -> Dict:
        """Create cost-effectiveness efficiency frontier."""
        
        # Sort by cost
        sorted_data = self.data.sort_values("cost")
        
        # Find efficient points
        efficient = []
        max_effectiveness = 0
        
        for _, row in sorted_data.iterrows():
            if row["effectiveness"] > max_effectiveness:
                efficient.append(row.to_dict())
                max_effectiveness = row["effectiveness"]
        
        return {
            "type": "scatter",
            "all_points": self.data[["cost", "effectiveness"]].to_dict("records"),
            "efficient_points": efficient,
            "title": "Cost-Effectiveness Efficiency Frontier"
        }
    
    def create_budget_allocation_chart(self, allocation: Dict) -> Dict:
        """Create budget allocation visualization."""
        
        return {
            "type": "sunburst",
            "data": {
                "labels": ["Total Budget"] + 
                         [f"{inv['intervention']} - {inv['county']}" 
                          for inv in allocation["selected_interventions"]],
                "parents": [""] + ["Total Budget"] * len(allocation["selected_interventions"]),
                "values": [allocation["total_cost"]] + 
                         [inv["cost"] for inv in allocation["selected_interventions"]]
            },
            "title": "Budget Allocation by Intervention"
        }
    
    def create_uncertainty_distribution(self, metric: str = "npv") -> Dict:
        """Create uncertainty distribution visualization."""
        
        # Monte Carlo samples
        samples = self.data[metric].values
        
        return {
            "type": "histogram",
            "data": samples.tolist(),
            "statistics": {
                "mean": np.mean(samples),
                "median": np.median(samples),
                "std": np.std(samples),
                "ci_95": [np.percentile(samples, 2.5), np.percentile(samples, 97.5)]
            },
            "title": f"{metric.upper()} Uncertainty Distribution"
        }
```

### 11.2 Automated Report Generation

```python
class ROIReportGenerator:
    """Generate comprehensive ROI reports."""
    
    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir
    
    def generate_executive_summary(
        self,
        optimization_result: Dict,
        budget: float,
        timeframe: int
    ) -> str:
        """Generate executive summary report."""
        
        report = f"""
# Intervention ROI Analysis - Executive Summary

## Key Findings

**Budget:** ${budget:,.0f}
**Timeframe:** {timeframe} years
**Counties Covered:** {optimization_result.get("counties_covered", "N/A")}

### Optimal Allocation

| Metric | Value |
|--------|-------|
| Total Investment | ${optimization_result.get("total_cost", 0):,.0f} |
| Total Benefit | {optimization_result.get("total_benefit", 0):,.0f} lives saved |
| Budget Utilization | {optimization_result.get("budget_utilization", 0):.1%} |
| Cost per Life Saved | ${budget / optimization_result.get("total_benefit", 1):,.0f} |

### Top Interventions

"""
        
        for i, inv in enumerate(optimization_result.get("selected_interventions", [])[:5]):
            report += f"{i+1}. {inv.get('intervention', 'Unknown')}"
            report += f" - ROI: {inv.get('roi', 0):.2f}\\n"
        
        return report
    
    def generate_detailed_report(
        self,
        county_analysis: pd.DataFrame,
        intervention_analysis: pd.DataFrame,
        sensitivity_results: Dict
    ) -> str:
        """Generate detailed technical report."""
        
        report = """
# Detailed ROI Analysis Report

## County-Level Analysis

"""
        
        # Add county table
        report += county_analysis.to_markdown()
        
        report += """

## Intervention Analysis

"""
        
        # Add intervention table
        report += intervention_analysis.to_markdown()
        
        report += """

## Sensitivity Analysis

"""
        
        # Add sensitivity results
        for param, results in sensitivity_results.items():
            report += f"\\n### {param}\\n"
            report += f"- Range: {results['range']}\\n"
            report += f"- Impact on NPV: {results['npv_impact']:.1%}\\n"
        
        return report
    
    def export_to_formats(
        self,
        report_data: Dict,
        formats: List[str] = ["pdf", "html", "json"]
    ) -> Dict[str, str]:
        """Export report to multiple formats."""
        
        outputs = {}
        
        for fmt in formats:
            if fmt == "json":
                outputs["json"] = json.dumps(report_data, indent=2)
            elif fmt == "html":
                outputs["html"] = self._generate_html(report_data)
            elif fmt == "pdf":
                outputs["pdf"] = self._generate_pdf(report_data)
        
        return outputs
    
    def _generate_html(self, data: Dict) -> str:
        """Generate HTML report."""
        return f"""
<!DOCTYPE html>
<html>
<head><title>ROI Analysis Report</title></head>
<body>
<h1>Intervention ROI Analysis</h1>
<pre>{json.dumps(data, indent=2)}</pre>
</body>
</html>
"""
    
    def _generate_pdf(self, data: Dict) -> str:
        """Generate PDF report (placeholder)."""
        # Would use reportlab or weasyprint
        return "PDF generation requires additional libraries"
```

---

## 12. Implementation Roadmap

### 12.1 Phase 1: Foundation (Weeks 1-4)

**Deliverables:**
1. Enhanced cost model with regional adjustments
2. Expanded intervention database (50+ interventions)
3. Basic NPV/IRR calculations
4. Simple budget optimizer

**Files to Create:**
- `src/roi/core/cost_models.py`
- `src/roi/data/interventions.py`
- `src/roi/core/roi_calculator.py`
- `src/roi/optimization/budget_optimizer.py`

### 12.2 Phase 2: Advanced Analytics (Weeks 5-8)

**Deliverables:**
1. Multi-criteria decision analysis
2. Sensitivity analysis framework
3. Uncertainty quantification (Monte Carlo)
4. Cost-effectiveness analysis

**Files to Create:**
- `src/roi/optimization/multi_criteria.py`
- `src/roi/analysis/sensitivity.py`
- `src/roi/analysis/uncertainty.py`
- `src/roi/analysis/cost_effectiveness.py`

### 12.3 Phase 3: Optimization (Weeks 9-12)

**Deliverables:**
1. MILP optimization solver
2. Multi-objective optimization (NSGA-II)
3. Portfolio optimization
4. Dynamic prioritization

**Files to Create:**
- `src/roi/optimization/milp_solver.py`
- `src/roi/optimization/multi_objective.py`
- `src/roi/optimization/portfolio.py`
- `src/roi/optimization/prioritization.py`

### 12.4 Phase 4: Integration (Weeks 13-16)

**Deliverables:**
1. Dashboard integration
2. API endpoints
3. Automated reporting
4. Feedback loop implementation

**Files to Create:**
- `src/roi/visualization/dashboard.py`
- `src/roi/integration/api.py`
- `src/roi/integration/pipeline.py`
- `src/roi/analysis/feedback.py`

---

## 13. Integration Points

### 13.1 Existing Code Integration

```python
# Integration with existing intervention_roi.py

from src.roi.core.roi_calculator import AdvancedROICalculator
from src.roi.optimization.budget_optimizer import BudgetOptimizer
from src.roi.analysis.sensitivity import SensitivityAnalyzer

class EnhancedInterventionROICalculator:
    """Enhanced calculator wrapping existing functionality."""
    
    def __init__(self, df=None):
        # Import existing calculator
        from src.intervention_roi import InterventionROICalculator
        self.base_calculator = InterventionROICalculator(df)
        
        # Initialize advanced components
        self.advanced_calculator = AdvancedROICalculator(df)
        self.budget_optimizer = BudgetOptimizer(df)
        self.sensitivity_analyzer = SensitivityAnalyzer()
    
    def calculate_advanced_roi(self, fips, intervention_key, **kwargs):
        """Calculate ROI with advanced features."""
        
        # Get base ROI
        base_roi = self.base_calculator.calculate_roi(fips, intervention_key)
        
        # Enhance with advanced calculations
        advanced = self.advanced_calculator.calculate_comprehensive_roi(
            fips, intervention_key, **kwargs
        )
        
        # Merge results
        return {**base_roi, **advanced}
```

### 13.2 Dashboard Integration

```python
# Streamlit dashboard integration

import streamlit as st
from src.roi.visualization.dashboard import ROIDashboard

def render_roi_tab():
    """Render ROI analysis tab in dashboard."""
    
    st.header("Intervention ROI Analysis")
    
    # Budget input
    budget = st.number_input(
        "Total Budget ($)",
        min_value=1_000_000,
        max_value=10_000_000_000,
        value=100_000_000,
        step=10_000_000
    )
    
    # Optimization
    if st.button("Optimize Allocation"):
        with st.spinner("Optimizing..."):
            optimizer = BudgetOptimizer(interventions, counties, budget)
            result = optimizer.optimize_knapsack()
            
            # Display results
            st.subheader("Optimal Allocation")
            st.write(f"Budget Utilization: {result['budget_utilization']:.1%}")
            st.write(f"Counties Covered: {result['counties_covered']}")
            
            # Visualization
            dashboard = ROIDashboard(pd.DataFrame(result['selected_interventions']))
            fig = dashboard.create_budget_allocation_chart(result)
            st.plotly_chart(fig)
```

---

## 14. Testing Strategy

### 14.1 Unit Tests

```python
# tests/test_roi_calculator.py

import pytest
from src.roi.core.roi_calculator import ROICalculator

class TestROICalculator:
    def test_npv_calculation(self):
        calc = ROICalculator(discount_rate=0.03)
        costs = [100, 10, 10, 10]
        benefits = [0, 50, 50, 50]
        npv = calc.calculate_npv(costs, benefits, 4)
        assert npv > 0  # Should be positive for profitable investment
    
    def test_bcr_calculation(self):
        calc = ROICalculator(discount_rate=0.03)
        costs = [100, 10, 10]
        benefits = [0, 60, 60]
        bcr = calc.calculate_benefit_cost_ratio(costs, benefits, 3)
        assert bcr > 1  # Benefits should exceed costs
```

### 14.2 Integration Tests

```python
# tests/test_optimization.py

import pytest
from src.roi.optimization.budget_optimizer import BudgetOptimizer

class TestBudgetOptimizer:
    def test_knapsack_optimization(self):
        interventions = [
            {"name": "A", "cost": 50, "benefit": 100},
            {"name": "B", "cost": 30, "benefit": 60},
            {"name": "C", "cost": 20, "benefit": 40}
        ]
        
        optimizer = BudgetOptimizer(interventions, None, budget=70)
        result = optimizer.optimize_knapsack()
        
        # Should select A and C (best benefit-to-cost ratio)
        assert result["total_cost"] <= 70
        assert len(result["selected_interventions"]) > 0
```

---

## 15. Conclusion

This comprehensive intervention ROI analysis framework provides ResilienceAI with:

1. **Advanced Cost Modeling**: Regional adjustments, economies of scale, multi-period budgets
2. **Comprehensive Benefit Quantification**: Health, economic, social, and system benefits
3. **Sophisticated ROI Metrics**: NPV, IRR, BCR, cost-effectiveness ratios
4. **Powerful Optimization**: Knapsack, MILP, multi-objective optimization
5. **Robust Prioritization**: MCDA with AHP, TOPSIS, PROMETHEE
6. **Uncertainty Handling**: Monte Carlo simulation, sensitivity analysis
7. **Impact Tracking**: Real-time monitoring and feedback loops
8. **Rich Visualization**: Interactive dashboards and automated reporting

The implementation follows a phased approach, building from foundational capabilities to advanced optimization and integration features. This ensures a robust, scalable, and maintainable ROI analysis platform that significantly enhances ResilienceAI's decision support capabilities.

---

## Appendix A: Complete File Structure

```
src/roi/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── cost_models.py          (400 lines)
│   ├── benefit_models.py       (350 lines)
│   ├── roi_calculator.py       (500 lines)
│   └── time_value.py           (200 lines)
├── optimization/
│   ├── __init__.py
│   ├── budget_optimizer.py     (450 lines)
│   ├── portfolio_optimizer.py  (300 lines)
│   ├── prioritization.py       (400 lines)
│   ├── multi_criteria.py       (350 lines)
│   ├── milp_solver.py          (250 lines)
│   └── multi_objective.py      (300 lines)
├── analysis/
│   ├── __init__.py
│   ├── sensitivity.py          (300 lines)
│   ├── uncertainty.py          (250 lines)
│   ├── equity.py               (200 lines)
│   ├── scenarios.py            (250 lines)
│   ├── cost_effectiveness.py   (300 lines)
│   └── feedback.py             (200 lines)
├── data/
│   ├── __init__.py
│   ├── interventions.py        (500 lines)
│   ├── cost_data.py            (300 lines)
│   └── effectiveness.py        (250 lines)
├── visualization/
│   ├── __init__.py
│   ├── roi_charts.py           (400 lines)
│   ├── dashboards.py           (350 lines)
│   └── reports.py              (300 lines)
└── integration/
    ├── __init__.py
    ├── pipeline.py             (200 lines)
    └── api.py                  (250 lines)

tests/roi/
├── test_cost_models.py
├── test_roi_calculator.py
├── test_optimization.py
├── test_multi_criteria.py
└── test_sensitivity.py

docs/roi/
├── API_REFERENCE.md
├── USER_GUIDE.md
├── METHODOLOGY.md
└── EXAMPLES.md
```

## Appendix B: Key Performance Indicators

| Metric | Target | Measurement |
|--------|--------|-------------|
| ROI Calculation Accuracy | ±10% | vs. actual outcomes |
| Optimization Runtime | <30s | for 100 counties, 50 interventions |
| Budget Utilization | >90% | in optimized allocations |
| Coverage Equity | Gini <0.3 | across population groups |
| User Satisfaction | >4.0/5.0 | dashboard usability |

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: Intervention ROI Analysis Team*
