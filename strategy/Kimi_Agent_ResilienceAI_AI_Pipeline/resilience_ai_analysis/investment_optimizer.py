"""
ResilienceAI Infrastructure Analysis - Investment Optimizer
ROI-based infrastructure investment optimization with multi-objective support
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class InvestmentOption:
    """Infrastructure investment option"""
    location_lat: float
    location_lon: float
    county_fips: str
    facility_type: str
    estimated_cost: float
    population_served: int
    coverage_improvement: float
    risk_reduction: float
    priority_score: float


class InvestmentOptimizer:
    """
    Optimize infrastructure investments using:
    - Cost-benefit analysis
    - Coverage maximization
    - Risk reduction
    - Budget constraints
    """
    
    # Estimated costs by facility type (in millions USD)
    FACILITY_COSTS = {
        'hospitals': 50.0,
        'hospital': 50.0,
        'fire_stations': 2.5,
        'fire_station': 2.5,
        'ems_stations': 1.5,
        'ems_station': 1.5,
        'nursing_homes': 10.0,
        'nursing_home': 10.0,
        'urgent_care': 3.0,
        'clinic': 1.0,
        'pharmacy': 0.5,
        'shelter': 1.0,
    }
    
    # Annual operating costs as % of capital cost
    OPERATING_COST_PCT = {
        'hospitals': 0.15,
        'hospital': 0.15,
        'fire_stations': 0.10,
        'fire_station': 0.10,
        'ems_stations': 0.12,
        'ems_station': 0.12,
        'nursing_homes': 0.20,
        'nursing_home': 0.20,
        'urgent_care': 0.15,
        'clinic': 0.12,
        'pharmacy': 0.10,
        'shelter': 0.08,
    }
    
    # Benefit per person served (annual, in USD)
    BENEFIT_PER_PERSON = {
        'hospitals': 500,
        'hospital': 500,
        'fire_stations': 200,
        'fire_station': 200,
        'ems_stations': 300,
        'ems_station': 300,
        'nursing_homes': 400,
        'nursing_home': 400,
        'urgent_care': 250,
        'clinic': 150,
        'pharmacy': 100,
        'shelter': 150,
    }
    
    def __init__(self, budget_millions: float = 100.0,
                 time_horizon_years: int = 10,
                 discount_rate: float = 0.05,
                 facility_costs: Optional[Dict[str, float]] = None):
        self.budget = budget_millions
        self.time_horizon = time_horizon_years
        self.discount_rate = discount_rate
        self.facility_costs = facility_costs or self.FACILITY_COSTS
        self.investment_options: List[InvestmentOption] = []
        
    def add_investment_option(self, gap, facility_costs: Optional[Dict] = None) -> None:
        """Convert coverage gap to investment option"""
        costs = facility_costs or self.facility_costs
        
        facility_type = gap.gap_type
        base_cost = costs.get(facility_type, 1.0)
        
        # Scale cost by number of facilities needed
        total_cost = base_cost * gap.recommended_facilities
        
        # Calculate coverage improvement
        coverage_improvement = self._calculate_coverage_improvement(gap)
        
        # Calculate risk reduction
        risk_reduction = self._calculate_risk_reduction(gap)
        
        option = InvestmentOption(
            location_lat=gap.location_lat,
            location_lon=gap.location_lon,
            county_fips=gap.county_fips,
            facility_type=facility_type,
            estimated_cost=total_cost,
            population_served=gap.population_affected,
            coverage_improvement=coverage_improvement,
            risk_reduction=risk_reduction,
            priority_score=gap.priority_score
        )
        
        self.investment_options.append(option)
    
    def add_custom_option(self, location_lat: float, location_lon: float,
                         county_fips: str, facility_type: str,
                         population_served: int,
                         coverage_improvement: float = 0.5,
                         risk_reduction: float = 0.3,
                         priority_score: float = 1.0) -> None:
        """Add a custom investment option"""
        cost = self.facility_costs.get(facility_type, 1.0)
        
        option = InvestmentOption(
            location_lat=location_lat,
            location_lon=location_lon,
            county_fips=county_fips,
            facility_type=facility_type,
            estimated_cost=cost,
            population_served=population_served,
            coverage_improvement=coverage_improvement,
            risk_reduction=risk_reduction,
            priority_score=priority_score
        )
        
        self.investment_options.append(option)
    
    def _calculate_coverage_improvement(self, gap) -> float:
        """Calculate coverage improvement from investment"""
        if gap.nearest_facility_distance_km <= gap.benchmark_distance_km:
            return 0.0
        
        # Improvement is proportional to how much closer we're getting
        current_distance = gap.nearest_facility_distance_km
        target_distance = gap.benchmark_distance_km
        
        # If we build a new facility, assume it will be within benchmark
        improvement = (current_distance - target_distance) / current_distance
        return min(improvement, 1.0)
    
    def _calculate_risk_reduction(self, gap) -> float:
        """Calculate disaster risk reduction from investment"""
        # Higher population + greater distance = higher risk reduction potential
        population_factor = min(np.log1p(gap.population_affected) / 15, 1.0)
        distance_factor = min(gap.nearest_facility_distance_km / 100, 1.0)
        
        return population_factor * distance_factor
    
    def optimize_investments(self, 
                            objective: str = 'coverage',
                            constraints: Optional[Dict] = None) -> Dict:
        """
        Optimize infrastructure investments
        
        Args:
            objective: Optimization objective ('coverage', 'risk', 'roi', 'balanced')
            constraints: Optional constraints dict
            
        Returns:
            Optimization results with selected investments
        """
        if not self.investment_options:
            return {'error': 'No investment options available'}
        
        # Filter options within budget
        affordable = [opt for opt in self.investment_options 
                     if opt.estimated_cost <= self.budget]
        
        if not affordable:
            return {'error': 'No affordable investment options within budget'}
        
        # Sort by objective
        sorted_options = self._sort_by_objective(affordable, objective)
        
        # Apply additional constraints if provided
        if constraints:
            sorted_options = self._apply_constraints(sorted_options, constraints)
        
        # Greedy selection within budget
        selected = []
        remaining_budget = self.budget
        
        for option in sorted_options:
            if option.estimated_cost <= remaining_budget:
                selected.append(option)
                remaining_budget -= option.estimated_cost
        
        # Calculate aggregate metrics
        total_investment = self.budget - remaining_budget
        
        return {
            'objective': objective,
            'total_budget': self.budget,
            'total_investment': round(total_investment, 2),
            'remaining_budget': round(remaining_budget, 2),
            'investments_count': len(selected),
            'population_served': sum(opt.population_served for opt in selected),
            'coverage_improvement': sum(opt.coverage_improvement for opt in selected),
            'risk_reduction': sum(opt.risk_reduction for opt in selected),
            'roi_metrics': self._calculate_roi_metrics(selected, total_investment),
            'recommended_investments': [
                {
                    'county_fips': opt.county_fips,
                    'facility_type': opt.facility_type,
                    'cost_millions': opt.estimated_cost,
                    'population_served': opt.population_served,
                    'coverage_improvement': round(opt.coverage_improvement, 4),
                    'risk_reduction': round(opt.risk_reduction, 4),
                    'location': (round(opt.location_lat, 4), round(opt.location_lon, 4))
                }
                for opt in selected
            ]
        }
    
    def _sort_by_objective(self, options: List[InvestmentOption], 
                          objective: str) -> List[InvestmentOption]:
        """Sort investment options by objective"""
        if objective == 'coverage':
            # Maximize population coverage
            return sorted(options, 
                         key=lambda x: x.coverage_improvement * x.population_served, 
                         reverse=True)
        elif objective == 'risk':
            # Maximize risk reduction
            return sorted(options, key=lambda x: x.risk_reduction, reverse=True)
        elif objective == 'roi':
            # Maximize return on investment
            return sorted(options, 
                         key=lambda x: (x.coverage_improvement * x.population_served) / 
                                       (x.estimated_cost + 0.01), 
                         reverse=True)
        elif objective == 'balanced':
            # Multi-criteria: priority score weighted by cost efficiency
            return sorted(options, 
                         key=lambda x: x.priority_score * (x.population_served / (x.estimated_cost + 0.01)), 
                         reverse=True)
        else:
            # Default: priority score
            return sorted(options, key=lambda x: x.priority_score, reverse=True)
    
    def _apply_constraints(self, options: List[InvestmentOption],
                          constraints: Dict) -> List[InvestmentOption]:
        """Apply additional constraints to filter options"""
        filtered = options
        
        # Minimum population constraint
        if 'min_population' in constraints:
            filtered = [opt for opt in filtered 
                       if opt.population_served >= constraints['min_population']]
        
        # Maximum cost per facility
        if 'max_cost_per_facility' in constraints:
            filtered = [opt for opt in filtered 
                       if opt.estimated_cost <= constraints['max_cost_per_facility']]
        
        # Required facility types
        if 'required_types' in constraints:
            filtered = [opt for opt in filtered 
                       if opt.facility_type in constraints['required_types']]
        
        # Excluded counties
        if 'excluded_counties' in constraints:
            filtered = [opt for opt in filtered 
                       if opt.county_fips not in constraints['excluded_counties']]
        
        return filtered
    
    def _calculate_roi_metrics(self, investments: List[InvestmentOption],
                               total_cost: float) -> Dict:
        """Calculate comprehensive ROI metrics"""
        if not investments or total_cost == 0:
            return {
                'people_served_per_million': 0,
                'coverage_improvement_per_million': 0,
                'risk_reduction_per_million': 0,
                'net_present_value_millions': 0,
                'benefit_cost_ratio': 0,
                'payback_period_years': float('inf')
            }
        
        # People served per million
        total_population = sum(opt.population_served for opt in investments)
        people_per_million = total_population / total_cost
        
        # Coverage improvement per million
        total_coverage = sum(opt.coverage_improvement for opt in investments)
        coverage_per_million = total_coverage / total_cost
        
        # Risk reduction per million
        total_risk = sum(opt.risk_reduction for opt in investments)
        risk_per_million = total_risk / total_cost
        
        # Calculate NPV
        annual_benefit = 0
        annual_operating = 0
        
        for opt in investments:
            benefit_rate = self.BENEFIT_PER_PERSON.get(opt.facility_type, 200)
            annual_benefit += opt.population_served * benefit_rate / 1_000_000  # Convert to millions
            
            operating_pct = self.OPERATING_COST_PCT.get(opt.facility_type, 0.1)
            annual_operating += opt.estimated_cost * operating_pct
        
        # NPV calculation
        npv = -total_cost
        for year in range(1, self.time_horizon + 1):
            npv += (annual_benefit - annual_operating) / ((1 + self.discount_rate) ** year)
        
        # Benefit-cost ratio
        total_benefits = annual_benefit * self.time_horizon
        total_costs = total_cost + annual_operating * self.time_horizon
        bc_ratio = total_benefits / total_costs if total_costs > 0 else 0
        
        # Payback period
        annual_net = annual_benefit - annual_operating
        payback = total_cost / annual_net if annual_net > 0 else float('inf')
        
        return {
            'people_served_per_million': round(people_per_million, 2),
            'coverage_improvement_per_million': round(coverage_per_million, 4),
            'risk_reduction_per_million': round(risk_per_million, 4),
            'net_present_value_millions': round(npv, 2),
            'benefit_cost_ratio': round(bc_ratio, 2),
            'payback_period_years': round(payback, 2) if payback != float('inf') else None
        }
    
    def compare_objectives(self) -> pd.DataFrame:
        """Compare different optimization objectives"""
        objectives = ['coverage', 'risk', 'roi', 'balanced']
        comparisons = []
        
        for obj in objectives:
            result = self.optimize_investments(objective=obj)
            if 'error' not in result:
                comparisons.append({
                    'objective': obj,
                    'investments': result['investments_count'],
                    'total_cost': result['total_investment'],
                    'population_served': result['population_served'],
                    'coverage_improvement': result['coverage_improvement'],
                    'risk_reduction': result['risk_reduction'],
                    'bc_ratio': result['roi_metrics']['benefit_cost_ratio']
                })
        
        return pd.DataFrame(comparisons)
    
    def sensitivity_analysis(self, budget_range: Tuple[float, float, float] = (50, 200, 25),
                            objective: str = 'balanced') -> pd.DataFrame:
        """
        Perform sensitivity analysis on budget
        
        Args:
            budget_range: (min, max, step) for budget in millions
            objective: Optimization objective to use
            
        Returns:
            DataFrame with sensitivity results
        """
        results = []
        original_budget = self.budget
        
        for budget in np.arange(budget_range[0], budget_range[1] + budget_range[2], budget_range[2]):
            self.budget = budget
            result = self.optimize_investments(objective=objective)
            
            if 'error' not in result:
                results.append({
                    'budget_millions': budget,
                    'investments': result['investments_count'],
                    'population_served': result['population_served'],
                    'coverage_improvement': result['coverage_improvement'],
                    'risk_reduction': result['risk_reduction'],
                    'people_per_million': result['roi_metrics']['people_served_per_million'],
                    'bc_ratio': result['roi_metrics']['benefit_cost_ratio']
                })
        
        self.budget = original_budget
        return pd.DataFrame(results)
