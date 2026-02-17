"""
Digital Twin Optimization Engine
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from scipy.optimize import minimize, differential_evolution
import random


@dataclass
class OptimizationResult:
    """Optimization result"""
    objective_value: float
    decision_variables: Dict[str, Any]
    constraints_satisfied: bool
    iterations: int
    convergence_history: List[float]
    execution_time_seconds: float


class ResourceOptimizer:
    """Optimize resource allocation for infrastructure"""
    
    def __init__(self, county_twin: Any):
        self.county_twin = county_twin
    
    def optimize_maintenance_schedule(self, budget: float, 
                                      time_period_months: int) -> OptimizationResult:
        """Optimize maintenance schedule within budget"""
        assets_needing_maintenance = [
            (aid, a) for aid, a in self.county_twin.assets.items()
            if a.get("condition_index", 1) < 0.8
        ]
        
        n_assets = len(assets_needing_maintenance)
        if n_assets == 0:
            return OptimizationResult(
                objective_value=0,
                decision_variables={},
                constraints_satisfied=True,
                iterations=0,
                convergence_history=[],
                execution_time_seconds=0
            )
        
        def objective(x):
            total_improvement = 0
            for i, (aid, asset) in enumerate(assets_needing_maintenance):
                current_condition = asset.get("condition_index", 0.5)
                improvement = x[i] * (1 - current_condition)
                total_improvement += improvement * asset.get("criticality_score", 0.5)
            return -total_improvement
        
        def budget_constraint(x):
            total_cost = sum(x[i] * 50000 for i in range(n_assets))
            return budget - total_cost
        
        bounds = [(0, 1) for _ in range(n_assets)]
        constraints = [{'type': 'ineq', 'fun': budget_constraint}]
        x0 = np.ones(n_assets) * 0.5
        
        result = minimize(
            objective, x0, method='SLSQP',
            bounds=bounds, constraints=constraints,
            options={'maxiter': 1000}
        )
        
        schedule = {}
        for i, (aid, asset) in enumerate(assets_needing_maintenance):
            if result.x[i] > 0.1:
                schedule[aid] = {
                    "priority": result.x[i],
                    "scheduled_month": int(result.x[i] * time_period_months),
                    "estimated_cost": 50000 * result.x[i],
                    "expected_improvement": result.x[i] * (1 - asset.get("condition_index", 0.5))
                }
        
        return OptimizationResult(
            objective_value=-result.fun,
            decision_variables=schedule,
            constraints_satisfied=budget_constraint(result.x) >= 0,
            iterations=result.nit,
            convergence_history=[],
            execution_time_seconds=0
        )
    
    def optimize_emergency_resource_placement(self, n_facilities: int,
                                               coverage_radius_miles: float) -> OptimizationResult:
        """Optimize placement of emergency resources"""
        population_centers = [
            (a.get("latitude", 0), a.get("longitude", 0), a.get("population_served", 1000))
            for a in self.county_twin.assets.values()
            if a.get("asset_type") in ["hospital", "school", "community_center"]
        ]
        
        if not population_centers:
            return OptimizationResult(
                objective_value=0,
                decision_variables={},
                constraints_satisfied=False,
                iterations=0,
                convergence_history=[],
                execution_time_seconds=0
            )
        
        def objective(x):
            total_coverage = 0
            for pop_lat, pop_lon, population in population_centers:
                min_distance = float('inf')
                for i in range(n_facilities):
                    fac_lat, fac_lon = x[2*i], x[2*i + 1]
                    distance = np.sqrt((pop_lat - fac_lat)**2 + (pop_lon - fac_lon)**2)
                    min_distance = min(min_distance, distance)
                
                if min_distance <= coverage_radius_miles / 69:
                    coverage = population * (1 - min_distance / (coverage_radius_miles / 69))
                    total_coverage += coverage
            return -total_coverage
        
        lats = [p[0] for p in population_centers]
        lons = [p[1] for p in population_centers]
        
        bounds = []
        for _ in range(n_facilities):
            bounds.extend([(min(lats), max(lats)), (min(lons), max(lons))])
        
        result = differential_evolution(objective, bounds, maxiter=100, seed=42)
        
        facilities = []
        for i in range(n_facilities):
            facilities.append({
                "facility_id": f"emergency_facility_{i}",
                "latitude": result.x[2*i],
                "longitude": result.x[2*i + 1]
            })
        
        return OptimizationResult(
            objective_value=-result.fun,
            decision_variables={"facilities": facilities},
            constraints_satisfied=True,
            iterations=result.nit,
            convergence_history=[],
            execution_time_seconds=0
        )
    
    def optimize_investment_portfolio(self, total_budget: float,
                                      risk_tolerance: float) -> OptimizationResult:
        """Optimize investment across different infrastructure types"""
        categories = ["maintenance", "upgrade", "expansion", "resilience", "technology"]
        n_categories = len(categories)
        
        returns = np.array([0.08, 0.12, 0.15, 0.10, 0.18])
        risks = np.array([0.05, 0.10, 0.15, 0.08, 0.20])
        
        def objective(x):
            portfolio_return = np.sum(x * returns)
            portfolio_risk = np.sqrt(np.sum((x * risks)**2))
            if portfolio_risk == 0:
                return -portfolio_return
            return -(portfolio_return - 0.03) / portfolio_risk
        
        def risk_constraint(x):
            portfolio_risk = np.sqrt(np.sum((x * risks)**2))
            return risk_tolerance - portfolio_risk
        
        bounds = [(0, 1) for _ in range(n_categories)]
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'ineq', 'fun': risk_constraint}
        ]
        
        x0 = np.ones(n_categories) / n_categories
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        allocation = {cat: result.x[i] * total_budget for i, cat in enumerate(categories)}
        
        return OptimizationResult(
            objective_value=-result.fun,
            decision_variables=allocation,
            constraints_satisfied=risk_constraint(result.x) >= 0,
            iterations=result.nit,
            convergence_history=[],
            execution_time_seconds=0
        )


class MultiObjectiveOptimizer:
    """Multi-objective optimization for conflicting goals"""
    
    def __init__(self, county_twin: Any):
        self.county_twin = county_twin
    
    def nsga_ii_optimize(self, objectives: List[Any],
                        constraints: List[Any],
                        n_variables: int,
                        population_size: int = 100,
                        generations: int = 100) -> List[Dict]:
        """NSGA-II multi-objective optimization"""
        population = self._initialize_population(population_size, n_variables)
        
        for gen in range(generations):
            fitness = [[obj(ind) for obj in objectives] for ind in population]
            fronts = self._non_dominated_sort(population, fitness)
            offspring = self._create_offspring(population, fronts)
            combined = population + offspring
            population = self._environmental_selection(combined, fitness, population_size)
        
        final_fitness = [[obj(ind) for obj in objectives] for ind in population]
        pareto_front = self._get_pareto_front(population, final_fitness)
        
        return [{"solution": sol, "objectives": objs} for sol, objs in pareto_front]
    
    def _initialize_population(self, size: int, n_vars: int) -> List[List[float]]:
        return [[random.random() for _ in range(n_vars)] for _ in range(size)]
    
    def _non_dominated_sort(self, population: List, fitness: List) -> List[List[int]]:
        fronts = [[]]
        for i, (ind, fit) in enumerate(zip(population, fitness)):
            dominated = False
            for j, other_fit in enumerate(fitness):
                if i != j and self._dominates(other_fit, fit):
                    dominated = True
                    break
            if not dominated:
                fronts[0].append(i)
        return fronts
    
    def _dominates(self, fit1: List[float], fit2: List[float]) -> bool:
        better_in_all = all(f1 <= f2 for f1, f2 in zip(fit1, fit2))
        better_in_one = any(f1 < f2 for f1, f2 in zip(fit1, fit2))
        return better_in_all and better_in_one
    
    def _create_offspring(self, population: List, fronts: List) -> List:
        offspring = []
        for _ in range(len(population)):
            parent1 = random.choice(population)
            parent2 = random.choice(population)
            child = [(p1 + p2) / 2 for p1, p2 in zip(parent1, parent2)]
            child = [c + random.gauss(0, 0.1) for c in child]
            child = [max(0, min(1, c)) for c in child]
            offspring.append(child)
        return offspring
    
    def _environmental_selection(self, combined: List, fitness: List, size: int) -> List:
        return combined[:size]
    
    def _get_pareto_front(self, population: List, fitness: List) -> List[Tuple]:
        pareto = []
        for i, (ind, fit) in enumerate(zip(population, fitness)):
            dominated = False
            for j, other_fit in enumerate(fitness):
                if i != j and self._dominates(other_fit, fit):
                    dominated = True
                    break
            if not dominated:
                pareto.append((ind, fit))
        return pareto
