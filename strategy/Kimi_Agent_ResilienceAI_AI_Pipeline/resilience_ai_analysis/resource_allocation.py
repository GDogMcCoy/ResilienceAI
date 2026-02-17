"""
Resource Allocation Optimization for ResilienceAI
Optimizes distribution of resources across counties and interventions
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class AllocationObjective(Enum):
    """Objectives for resource allocation"""
    MAXIMIZE_COVERAGE = "maximize_coverage"
    MAXIMIZE_IMPACT = "maximize_impact"
    MINIMIZE_COST = "minimize_cost"
    EQUITY = "equity"
    RISK_REDUCTION = "risk_reduction"


@dataclass
class ResourceConstraint:
    """Resource constraint definition"""
    resource_type: str
    total_amount: float
    min_per_county: Optional[float] = None
    max_per_county: Optional[float] = None


@dataclass
class AllocationResult:
    """Resource allocation result"""
    county_allocations: Dict[str, Dict[str, float]]
    intervention_allocations: Dict[str, Dict[str, float]]
    total_cost: float
    expected_impact: float
    coverage: float
    equity_score: float
    objective_value: float


class ResourceAllocationOptimizer:
    """Optimizer for resource allocation across counties and interventions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.objective = AllocationObjective(config.get('objective', 'maximize_impact'))
        self.constraints: List[ResourceConstraint] = []
        self.county_data: Optional[pd.DataFrame] = None
        self.intervention_data: Optional[pd.DataFrame] = None
        self.effectiveness_matrix: Optional[np.ndarray] = None
    
    def set_constraints(self, constraints: List[ResourceConstraint]) -> None:
        """Set resource constraints"""
        self.constraints = constraints
    
    def fit(
        self,
        county_data: pd.DataFrame,
        intervention_data: pd.DataFrame,
        effectiveness_matrix: np.ndarray
    ) -> None:
        """Initialize optimizer with data"""
        
        self.county_data = county_data.copy()
        self.intervention_data = intervention_data.copy()
        self.effectiveness_matrix = effectiveness_matrix
        
        self.n_counties = len(county_data)
        self.n_interventions = len(intervention_data)
    
    def optimize(
        self,
        total_budget: float,
        equity_weight: float = 0.3,
        min_county_allocation: Optional[float] = None
    ) -> AllocationResult:
        """Optimize resource allocation"""
        
        if self.objective == AllocationObjective.MAXIMIZE_IMPACT:
            return self._optimize_maximize_impact(total_budget, equity_weight)
        elif self.objective == AllocationObjective.MAXIMIZE_COVERAGE:
            return self._optimize_maximize_coverage(total_budget)
        elif self.objective == AllocationObjective.EQUITY:
            return self._optimize_equity(total_budget)
        elif self.objective == AllocationObjective.RISK_REDUCTION:
            return self._optimize_risk_reduction(total_budget)
        else:
            return self._optimize_maximize_impact(total_budget, equity_weight)
    
    def _optimize_maximize_impact(
        self,
        total_budget: float,
        equity_weight: float
    ) -> AllocationResult:
        """Optimize for maximum impact with equity consideration using greedy approach"""
        
        n_counties = self.n_counties
        n_interventions = self.n_interventions
        
        allocation_matrix = np.zeros((n_counties, n_interventions))
        remaining_budget = total_budget
        
        costs = self.intervention_data['cost'].values
        
        # Calculate cost-effectiveness
        cost_effectiveness = self.effectiveness_matrix / (costs + 1)
        
        # Greedy allocation
        flat_indices = np.argsort(cost_effectiveness.flatten())[::-1]
        
        for flat_idx in flat_indices:
            county_idx = flat_idx // n_interventions
            intervention_idx = flat_idx % n_interventions
            
            cost = costs[intervention_idx]
            
            if cost <= remaining_budget:
                allocation_matrix[county_idx, intervention_idx] += cost
                remaining_budget -= cost
        
        return self._build_allocation_result(allocation_matrix, costs)
    
    def _optimize_maximize_coverage(
        self,
        total_budget: float
    ) -> AllocationResult:
        """Optimize for maximum county coverage"""
        
        n_counties = self.n_counties
        n_interventions = self.n_interventions
        
        allocation_matrix = np.zeros((n_counties, n_interventions))
        remaining_budget = total_budget
        
        costs = self.intervention_data['cost'].values
        
        # Prioritize covering all counties first
        min_allocation = total_budget / n_counties / 2
        
        for county_idx in range(n_counties):
            # Find best intervention for this county
            best_intervention = np.argmax(self.effectiveness_matrix[county_idx] / (costs + 1))
            cost = costs[best_intervention]
            
            if cost <= remaining_budget and cost <= min_allocation * 2:
                allocation_matrix[county_idx, best_intervention] = min(min_allocation, cost)
                remaining_budget -= min(min_allocation, cost)
        
        # Allocate remaining budget greedily
        cost_effectiveness = self.effectiveness_matrix / (costs + 1)
        flat_indices = np.argsort(cost_effectiveness.flatten())[::-1]
        
        for flat_idx in flat_indices:
            county_idx = flat_idx // n_interventions
            intervention_idx = flat_idx % n_interventions
            
            cost = costs[intervention_idx]
            
            if cost <= remaining_budget:
                allocation_matrix[county_idx, intervention_idx] += cost
                remaining_budget -= cost
        
        return self._build_allocation_result(allocation_matrix, costs)
    
    def _optimize_equity(
        self,
        total_budget: float
    ) -> AllocationResult:
        """Optimize for equitable distribution"""
        
        n_counties = self.n_counties
        n_interventions = self.n_interventions
        
        allocation_matrix = np.zeros((n_counties, n_interventions))
        
        costs = self.intervention_data['cost'].values
        
        # Equal per-county allocation
        equal_per_county = total_budget / n_counties
        
        for county_idx in range(n_counties):
            remaining = equal_per_county
            
            # Sort interventions by effectiveness for this county
            sorted_interventions = np.argsort(self.effectiveness_matrix[county_idx])[::-1]
            
            for intervention_idx in sorted_interventions:
                cost = costs[intervention_idx]
                
                if cost <= remaining:
                    allocation_matrix[county_idx, intervention_idx] = cost
                    remaining -= cost
                    
                    if remaining < min(costs):
                        break
        
        return self._build_allocation_result(allocation_matrix, costs)
    
    def _optimize_risk_reduction(
        self,
        total_budget: float
    ) -> AllocationResult:
        """Optimize for maximum risk reduction"""
        
        # Get risk scores for each county
        risk_cols = [c for c in self.county_data.columns if c.startswith('risk_')]
        
        if risk_cols:
            county_risks = self.county_data[risk_cols].sum(axis=1).values
        else:
            county_risks = np.ones(self.n_counties)
        
        # Weight effectiveness by risk
        weighted_effectiveness = self.effectiveness_matrix * county_risks[:, np.newaxis]
        
        n_counties = self.n_counties
        n_interventions = self.n_interventions
        
        allocation_matrix = np.zeros((n_counties, n_interventions))
        remaining_budget = total_budget
        
        costs = self.intervention_data['cost'].values
        
        # Greedy allocation based on risk-weighted effectiveness
        cost_effectiveness = weighted_effectiveness / (costs + 1)
        flat_indices = np.argsort(cost_effectiveness.flatten())[::-1]
        
        for flat_idx in flat_indices:
            county_idx = flat_idx // n_interventions
            intervention_idx = flat_idx % n_interventions
            
            cost = costs[intervention_idx]
            
            if cost <= remaining_budget:
                allocation_matrix[county_idx, intervention_idx] += cost
                remaining_budget -= cost
        
        return self._build_allocation_result(allocation_matrix, costs)
    
    def _build_allocation_result(
        self,
        allocation_matrix: np.ndarray,
        costs: np.ndarray
    ) -> AllocationResult:
        """Build allocation result from matrix"""
        
        county_ids = self.county_data['county_id'].values
        intervention_ids = self.intervention_data['intervention_id'].values
        
        # County allocations
        county_allocations = {}
        for i, county_id in enumerate(county_ids):
            county_allocations[county_id] = {
                'total': float(np.sum(allocation_matrix[i, :])),
                'by_intervention': {
                    intervention_ids[j]: float(allocation_matrix[i, j])
                    for j in range(len(intervention_ids))
                    if allocation_matrix[i, j] > 0
                }
            }
        
        # Intervention allocations
        intervention_allocations = {}
        for j, intervention_id in enumerate(intervention_ids):
            intervention_allocations[intervention_id] = {
                'total': float(np.sum(allocation_matrix[:, j])),
                'by_county': {
                    county_ids[i]: float(allocation_matrix[i, j])
                    for i in range(len(county_ids))
                    if allocation_matrix[i, j] > 0
                }
            }
        
        # Calculate metrics
        total_cost = float(np.sum(allocation_matrix * costs))
        expected_impact = float(np.sum(allocation_matrix * self.effectiveness_matrix))
        
        # Coverage
        counties_with_allocation = np.sum(np.sum(allocation_matrix, axis=1) > 0)
        coverage = counties_with_allocation / len(county_ids)
        
        # Equity score (Gini coefficient)
        county_totals = np.sum(allocation_matrix, axis=1)
        county_pops = self.county_data['population'].values if 'population' in self.county_data.columns else np.ones(len(county_ids))
        per_capita = county_totals / (county_pops + 1)
        equity_score = 1 - self._gini_coefficient(per_capita)
        
        return AllocationResult(
            county_allocations=county_allocations,
            intervention_allocations=intervention_allocations,
            total_cost=total_cost,
            expected_impact=expected_impact,
            coverage=coverage,
            equity_score=equity_score,
            objective_value=expected_impact
        )
    
    def _gini_coefficient(self, x: np.ndarray) -> float:
        """Calculate Gini coefficient for equity measurement"""
        
        sorted_x = np.sort(x)
        n = len(x)
        cumsum = np.cumsum(sorted_x)
        
        if cumsum[-1] == 0:
            return 0
        
        return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
    
    def sensitivity_analysis(
        self,
        total_budget: float,
        budget_range: Tuple[float, float] = (0.5, 1.5),
        n_steps: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform sensitivity analysis on budget"""
        
        results = []
        budget_multipliers = np.linspace(budget_range[0], budget_range[1], n_steps)
        
        for mult in budget_multipliers:
            adjusted_budget = total_budget * mult
            allocation = self.optimize(adjusted_budget)
            
            results.append({
                'budget_multiplier': mult,
                'total_budget': adjusted_budget,
                'expected_impact': allocation.expected_impact,
                'coverage': allocation.coverage,
                'equity_score': allocation.equity_score
            })
        
        return results


# Example usage
if __name__ == "__main__":
    # Create sample data
    county_data = pd.DataFrame({
        'county_id': ['county_1', 'county_2', 'county_3', 'county_4'],
        'population': [100000, 150000, 80000, 120000],
        'risk_flood': [0.8, 0.6, 0.7, 0.5],
        'risk_wildfire': [0.3, 0.5, 0.2, 0.4]
    })
    
    intervention_data = pd.DataFrame({
        'intervention_id': ['int_1', 'int_2', 'int_3'],
        'cost': [100000, 150000, 80000],
        'effectiveness': [0.8, 0.7, 0.6]
    })
    
    # Create effectiveness matrix (counties x interventions)
    effectiveness_matrix = np.array([
        [0.9, 0.7, 0.6],  # county_1
        [0.7, 0.8, 0.5],  # county_2
        [0.8, 0.6, 0.7],  # county_3
        [0.6, 0.7, 0.8],  # county_4
    ])
    
    # Initialize and run optimizer
    config = {'objective': 'maximize_impact'}
    optimizer = ResourceAllocationOptimizer(config)
    optimizer.fit(county_data, intervention_data, effectiveness_matrix)
    
    total_budget = 500000
    result = optimizer.optimize(total_budget)
    
    print(f"Resource Allocation Results:")
    print(f"  Total Cost: ${result.total_cost:,.2f}")
    print(f"  Expected Impact: {result.expected_impact:.3f}")
    print(f"  Coverage: {result.coverage:.1%}")
    print(f"  Equity Score: {result.equity_score:.3f}")
    
    print(f"\nCounty Allocations:")
    for county_id, allocation in result.county_allocations.items():
        print(f"  {county_id}: ${allocation['total']:,.2f}")
