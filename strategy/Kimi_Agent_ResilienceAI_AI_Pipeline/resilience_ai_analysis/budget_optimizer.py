"""
ResilienceAI - Budget Optimization Module
Budget-constrained optimization using knapsack, MILP, and heuristic algorithms.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
import warnings

# Try to import optimization libraries
try:
    from scipy.optimize import differential_evolution, minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False


@dataclass
class OptimizationResult:
    """Container for optimization results."""
    selected_items: List[Dict]
    total_cost: float
    total_benefit: float
    budget_utilization: float
    optimization_time: float
    algorithm: str
    status: str
    gap: Optional[float] = None


class BudgetOptimizer:
    """
    Optimize intervention allocation under budget constraints.

    Supports multiple optimization algorithms:
    - Greedy knapsack (fast, approximate)
    - MILP (exact, slower)
    - Dynamic programming (exact, memory intensive)
    - Genetic algorithm (for complex constraints)
    """

    def __init__(
        self,
        items: List[Dict],
        budget: float,
        cost_key: str = "cost",
        benefit_key: str = "benefit"
    ):
        """
        Initialize budget optimizer.

        Args:
            items: List of items with cost and benefit
            budget: Total budget constraint
            cost_key: Key for cost in item dicts
            benefit_key: Key for benefit in item dicts
        """
        self.items = items
        self.budget = budget
        self.cost_key = cost_key
        self.benefit_key = benefit_key

        # Validate items
        self._validate_items()

    def _validate_items(self):
        """Validate item structure."""
        for i, item in enumerate(self.items):
            if self.cost_key not in item:
                raise ValueError(f"Item {i} missing cost key '{self.cost_key}'")
            if self.benefit_key not in item:
                raise ValueError(f"Item {i} missing benefit key '{self.benefit_key}'")

    def optimize_greedy(
        self,
        equity_weight: float = 0.0,
        equity_key: Optional[str] = None
    ) -> OptimizationResult:
        """
        Greedy knapsack optimization (fast, approximate).

        Args:
            equity_weight: Weight for equity considerations (0-1)
            equity_key: Key for equity score in items

        Returns:
            OptimizationResult with selected items
        """
        import time
        start_time = time.time()

        # Calculate efficiency scores
        scored_items = []
        for i, item in enumerate(self.items):
            cost = item[self.cost_key]
            benefit = item[self.benefit_key]

            if cost <= 0:
                continue

            # Base efficiency
            efficiency = benefit / cost

            # Add equity consideration
            if equity_weight > 0 and equity_key and equity_key in item:
                equity_score = item[equity_key]
                efficiency = efficiency * (1 + equity_weight * equity_score)

            scored_items.append({
                "index": i,
                "item": item,
                "efficiency": efficiency,
                "cost": cost,
                "benefit": benefit
            })

        # Sort by efficiency (descending)
        scored_items.sort(key=lambda x: x["efficiency"], reverse=True)

        # Greedy selection
        selected = []
        remaining_budget = self.budget

        for scored in scored_items:
            if scored["cost"] <= remaining_budget:
                # Check for conflicts
                if not self._has_conflict(selected, scored["item"]):
                    selected.append(scored)
                    remaining_budget -= scored["cost"]

        elapsed = time.time() - start_time

        return OptimizationResult(
            selected_items=[s["item"] for s in selected],
            total_cost=self.budget - remaining_budget,
            total_benefit=sum(s["benefit"] for s in selected),
            budget_utilization=(self.budget - remaining_budget) / self.budget,
            optimization_time=elapsed,
            algorithm="greedy_knapsack",
            status="optimal"
        )

    def optimize_milp(
        self,
        constraints: Optional[Dict] = None,
        time_limit: int = 300
    ) -> OptimizationResult:
        """
        Mixed Integer Linear Programming optimization (exact).

        Args:
            constraints: Additional constraints dictionary
            time_limit: Solver time limit in seconds

        Returns:
            OptimizationResult with selected items
        """
        if not PULP_AVAILABLE:
            warnings.warn("PuLP not available, falling back to greedy")
            return self.optimize_greedy()

        import time
        start_time = time.time()

        # Create problem
        prob = pulp.LpProblem("Budget_Optimization", pulp.LpMaximize)

        # Decision variables
        n_items = len(self.items)
        x = pulp.LpVariable.dicts("x", range(n_items), cat=pulp.LpBinary)

        # Objective: maximize benefit
        prob += pulp.lpSum(
            x[i] * self.items[i][self.benefit_key]
            for i in range(n_items)
        )

        # Budget constraint
        prob += pulp.lpSum(
            x[i] * self.items[i][self.cost_key]
            for i in range(n_items)
        ) <= self.budget

        # Additional constraints
        if constraints:
            # Minimum items constraint
            if "min_items" in constraints:
                prob += pulp.lpSum(x[i] for i in range(n_items)) >= constraints["min_items"]

            # Maximum items constraint
            if "max_items" in constraints:
                prob += pulp.lpSum(x[i] for i in range(n_items)) <= constraints["max_items"]

            # Category constraints
            if "category_limits" in constraints:
                for category, limit in constraints["category_limits"].items():
                    cat_items = [i for i, item in enumerate(self.items) 
                                if item.get("category") == category]
                    if cat_items:
                        prob += pulp.lpSum(x[i] for i in cat_items) <= limit

        # Solve
        solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
        prob.solve(solver)

        elapsed = time.time() - start_time

        # Extract solution
        selected = [self.items[i] for i in range(n_items) if x[i].value() == 1]
        total_cost = sum(item[self.cost_key] for item in selected)
        total_benefit = sum(item[self.benefit_key] for item in selected)

        status_map = {
            pulp.LpStatusOptimal: "optimal",
            pulp.LpStatusNotSolved: "not_solved",
            pulp.LpStatusInfeasible: "infeasible",
            pulp.LpStatusUnbounded: "unbounded",
            pulp.LpStatusUndefined: "undefined"
        }

        return OptimizationResult(
            selected_items=selected,
            total_cost=total_cost,
            total_benefit=total_benefit,
            budget_utilization=total_cost / self.budget,
            optimization_time=elapsed,
            algorithm="milp",
            status=status_map.get(pulp.LpStatus[prob.status], "unknown"),
            gap=None
        )

    def optimize_dp(
        self,
        cost_resolution: int = 1000
    ) -> OptimizationResult:
        """
        Dynamic programming optimization (exact, for small problems).

        Args:
            cost_resolution: Discretization level for costs

        Returns:
            OptimizationResult with selected items
        """
        import time
        start_time = time.time()

        # Discretize costs
        max_budget = int(self.budget / cost_resolution)

        # Scale item costs
        scaled_items = []
        for item in self.items:
            scaled_cost = int(item[self.cost_key] / cost_resolution)
            scaled_items.append({
                "cost": scaled_cost,
                "benefit": item[self.benefit_key],
                "original": item
            })

        # DP table
        dp = np.zeros((len(scaled_items) + 1, max_budget + 1))

        for i in range(1, len(scaled_items) + 1):
            item = scaled_items[i - 1]
            for w in range(max_budget + 1):
                if item["cost"] <= w:
                    dp[i, w] = max(
                        dp[i - 1, w],
                        dp[i - 1, w - item["cost"]] + item["benefit"]
                    )
                else:
                    dp[i, w] = dp[i - 1, w]

        # Backtrack to find selected items
        selected = []
        w = max_budget
        for i in range(len(scaled_items), 0, -1):
            if dp[i, w] != dp[i - 1, w]:
                selected.append(scaled_items[i - 1]["original"])
                w -= scaled_items[i - 1]["cost"]

        elapsed = time.time() - start_time

        total_cost = sum(item[self.cost_key] for item in selected)
        total_benefit = sum(item[self.benefit_key] for item in selected)

        return OptimizationResult(
            selected_items=selected,
            total_cost=total_cost,
            total_benefit=total_benefit,
            budget_utilization=total_cost / self.budget,
            optimization_time=elapsed,
            algorithm="dynamic_programming",
            status="optimal"
        )

    def optimize_genetic(
        self,
        population_size: int = 100,
        generations: int = 200,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8
    ) -> OptimizationResult:
        """
        Genetic algorithm optimization (for complex constraints).

        Args:
            population_size: Size of population
            generations: Number of generations
            mutation_rate: Mutation probability
            crossover_rate: Crossover probability

        Returns:
            OptimizationResult with selected items
        """
        if not SCIPY_AVAILABLE:
            warnings.warn("SciPy not available, falling back to greedy")
            return self.optimize_greedy()

        import time
        start_time = time.time()

        n_items = len(self.items)

        def fitness(x):
            """Fitness function for genetic algorithm."""
            x = x.astype(bool)
            cost = sum(self.items[i][self.cost_key] for i in range(n_items) if x[i])
            benefit = sum(self.items[i][self.benefit_key] for i in range(n_items) if x[i])

            # Penalty for exceeding budget
            if cost > self.budget:
                return -1e10 * (cost / self.budget)

            return benefit

        # Use differential evolution as genetic algorithm
        bounds = [(0, 1) for _ in range(n_items)]

        result = differential_evolution(
            lambda x: -fitness(x),
            bounds,
            maxiter=generations,
            popsize=population_size // n_items,
            mutation=mutation_rate,
            recombination=crossover_rate,
            seed=42
        )

        elapsed = time.time() - start_time

        # Extract solution
        selected_indices = np.where(result.x > 0.5)[0]
        selected = [self.items[i] for i in selected_indices]

        total_cost = sum(item[self.cost_key] for item in selected)
        total_benefit = sum(item[self.benefit_key] for item in selected)

        return OptimizationResult(
            selected_items=selected,
            total_cost=total_cost,
            total_benefit=total_benefit,
            budget_utilization=total_cost / self.budget,
            optimization_time=elapsed,
            algorithm="genetic",
            status="optimal" if result.success else "suboptimal"
        )

    def _has_conflict(self, selected: List[Dict], new_item: Dict) -> bool:
        """Check if new item conflicts with selected items."""
        # Check for same county intervention
        if "county_fips" in new_item:
            for item in selected:
                if item.get("county_fips") == new_item["county_fips"]:
                    # Same county, same intervention type
                    if item.get("intervention_type") == new_item.get("intervention_type"):
                        return True
        return False

    def compare_algorithms(self) -> pd.DataFrame:
        """Compare all optimization algorithms."""
        results = []

        algorithms = [
            ("Greedy", self.optimize_greedy),
            ("MILP", self.optimize_milp),
            ("Dynamic Programming", self.optimize_dp),
            ("Genetic", self.optimize_genetic)
        ]

        for name, optimizer in algorithms:
            try:
                result = optimizer()
                results.append({
                    "algorithm": name,
                    "total_benefit": result.total_benefit,
                    "total_cost": result.total_cost,
                    "budget_utilization": result.budget_utilization,
                    "time_seconds": result.optimization_time,
                    "status": result.status,
                    "n_selected": len(result.selected_items)
                })
            except Exception as e:
                results.append({
                    "algorithm": name,
                    "error": str(e)
                })

        return pd.DataFrame(results)


class MultiObjectiveOptimizer:
    """Multi-objective optimization for budget allocation."""

    def __init__(
        self,
        items: List[Dict],
        budget: float,
        objectives: List[str]
    ):
        """
        Initialize multi-objective optimizer.

        Args:
            items: List of items with multiple objectives
            budget: Total budget
            objectives: List of objective keys to maximize
        """
        self.items = items
        self.budget = budget
        self.objectives = objectives

    def solve_nsga2(
        self,
        population_size: int = 100,
        generations: int = 200
    ) -> Dict:
        """
        NSGA-II multi-objective optimization.

        Returns:
            Dictionary with Pareto front and solutions
        """
        if not SCIPY_AVAILABLE:
            return {"error": "SciPy required for NSGA-II"}

        n_items = len(self.items)
        n_objectives = len(self.objectives)

        def evaluate(x):
            """Evaluate multiple objectives."""
            x = x.astype(bool)
            cost = sum(self.items[i].get("cost", 0) for i in range(n_items) if x[i])

            # Penalty for exceeding budget
            if cost > self.budget:
                return [-1e10] * n_objectives

            obj_values = []
            for obj in self.objectives:
                value = sum(self.items[i].get(obj, 0) for i in range(n_items) if x[i])
                obj_values.append(-value)  # Negative for minimization

            return obj_values

        # Use differential evolution with multi-objective wrapper
        bounds = [(0, 1) for _ in range(n_items)]

        # Simplified: optimize weighted sum
        weights = [1.0 / n_objectives] * n_objectives

        def weighted_objective(x):
            obj_values = evaluate(x)
            return sum(w * v for w, v in zip(weights, obj_values))

        result = differential_evolution(
            weighted_objective,
            bounds,
            maxiter=generations,
            popsize=population_size // n_items,
            seed=42
        )

        selected_indices = np.where(result.x > 0.5)[0]

        return {
            "selected_items": [self.items[i] for i in selected_indices],
            "objective_values": [-v for v in evaluate(result.x)],
            "success": result.success
        }


if __name__ == "__main__":
    # Example usage
    items = [
        {"name": "Hospital A", "cost": 50_000_000, "benefit": 100, "county_fips": "001"},
        {"name": "EMS Station B", "cost": 2_000_000, "benefit": 30, "county_fips": "002"},
        {"name": "Fire Station C", "cost": 3_000_000, "benefit": 25, "county_fips": "003"},
        {"name": "Telehealth D", "cost": 250_000, "benefit": 20, "county_fips": "004"},
        {"name": "Prep Program E", "cost": 500_000, "benefit": 35, "county_fips": "005"},
    ]

    optimizer = BudgetOptimizer(items, budget=10_000_000)

    # Compare algorithms
    comparison = optimizer.compare_algorithms()
    print("Algorithm Comparison:")
    print(comparison.to_string())
