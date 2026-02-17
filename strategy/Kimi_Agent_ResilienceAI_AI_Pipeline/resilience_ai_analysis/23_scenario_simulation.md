# ResilienceAI Scenario Simulation Enhancement Design

## Executive Summary

This document provides a comprehensive design for enhancing the ResilienceAI scenario simulation capabilities. The current `scenario_simulator.py` provides basic what-if analysis with 10 disaster presets and simple distance-based impact calculations. This enhancement introduces advanced multi-dimensional simulation engines covering disaster modeling, impact assessment, resource estimation, evacuation planning, economic modeling, infrastructure cascading, population displacement, recovery estimation, and intervention effectiveness analysis.

---

## 1. Current State Analysis

### 1.1 Existing Capabilities (scenario_simulator.py)

```python
# Current implementation summary
SCENARIO_PRESETS = {
    "hurricane_cat1": {"risk_mult": 1.3, "damage_pct": 0.15, "radius_km": 150},
    "hurricane_cat3": {"risk_mult": 1.8, "damage_pct": 0.35, "radius_km": 200},
    # ... 8 more presets
}

class ScenarioSimulator:
    - Basic distance-based impact calculation
    - Simple risk score multiplication
    - Infrastructure damage percentage estimation
    - Population at risk calculation
    - Before/after comparison
```

### 1.2 Limitations of Current System

| Limitation | Impact | Priority |
|------------|--------|----------|
| Static scenario presets | Cannot model compound/multi-hazard events | High |
| Simple distance decay | No terrain/elevation/building type considerations | High |
| No resource modeling | Cannot estimate emergency resource needs | High |
| No evacuation modeling | Missing critical life-safety planning | Critical |
| No economic impact | Cannot assess financial consequences | High |
| No infrastructure cascading | Missing interdependency analysis | Critical |
| No recovery modeling | Cannot estimate restoration timelines | Medium |
| No intervention simulation | Cannot evaluate mitigation effectiveness | High |

### 1.3 Related Existing Components

- **intervention_roi.py**: Cost-effectiveness calculations for preparedness interventions
- **network_analysis.py**: Infrastructure network graph modeling
- **predictive_models.py**: Time-series forecasting with Prophet/ARIMA
- **feature_engineering.py**: 66 vulnerability features including isolation scores

---

## 2. Proposed Simulation Engine Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI SIMULATION FRAMEWORK                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │  SCENARIO   │  │   IMPACT    │  │  RESOURCE   │                         │
│  │  MODELING   │  │ ASSESSMENT  │  │ ESTIMATION  │                         │
│  │   ENGINE    │  │   ENGINE    │  │   ENGINE    │                         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                         │
│         │                │                │                                 │
│         └────────────────┼────────────────┘                                 │
│                          ▼                                                  │
│         ┌──────────────────────────────────┐                               │
│         │      SIMULATION ORCHESTRATOR     │                               │
│         └──────────────────────────────────┘                               │
│                          │                                                  │
│         ┌────────────────┼────────────────┐                                 │
│         ▼                ▼                ▼                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │  EVACUATION │  │  ECONOMIC   │  │ INFRASTRUCTURE                       │
│  │  PLANNING   │  │   IMPACT    │  │  CASCADING  │                         │
│  │   ENGINE    │  │   ENGINE    │  │   ENGINE    │                         │
│  └─────────────┘  └─────────────┘  └─────────────┘                         │
│         │                │                │                                 │
│         ▼                ▼                ▼                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │ POPULATION  │  │  RECOVERY   │  │ INTERVENTION                         │
│  │DISPLACEMENT │  │    TIME     │  │EFFECTIVENESS│                         │
│  │   ENGINE    │  │ ESTIMATION  │  │   ENGINE    │                         │
│  └─────────────┘  └─────────────┘  └─────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 File Structure

```
src/simulation/
├── __init__.py                           # Package initialization
├── core/
│   ├── simulation_orchestrator.py        # Main orchestration engine
│   ├── base_engine.py                    # Abstract base class
│   └── scenario_state.py                 # Scenario state management
├── scenarios/
│   ├── disaster_models.py                # Disaster scenario definitions
│   ├── compound_events.py                # Multi-hazard event modeling
│   └── temporal_scenarios.py             # Time-evolving scenarios
├── impact/
│   ├── physical_impact.py                # Physical damage assessment
│   ├── health_impact.py                  # Health consequence modeling
│   └── social_impact.py                  # Social vulnerability impact
├── resources/
│   ├── resource_calculator.py            # Resource requirement estimation
│   ├── deployment_optimizer.py           # Optimal deployment planning
│   └── supply_chain.py                   # Supply chain impact modeling
├── evacuation/
│   ├── evacuation_model.py               # Evacuation simulation
│   ├── route_optimizer.py                # Optimal route calculation
│   └── shelter_allocator.py              # Shelter capacity planning
├── economic/
│   ├── direct_damage.py                  # Direct economic losses
│   ├── business_interruption.py          # Indirect economic impacts
│   └── reconstruction_cost.py            # Recovery cost estimation
├── infrastructure/
│   ├── cascade_model.py                  # Failure cascade simulation
│   ├── interdependency.py                # Infrastructure dependencies
│   └── restoration_model.py              # Restoration time estimation
├── population/
│   ├── displacement_model.py             # Population displacement
│   ├── demographics.py                   # Demographic impact analysis
│   └── needs_assessment.py               # Humanitarian needs estimation
├── recovery/
│   ├── recovery_timeline.py              # Recovery time estimation
│   ├── milestone_tracker.py              # Recovery milestone tracking
│   └── resilience_metrics.py             # Post-disaster resilience
└── intervention/
    ├── effectiveness_model.py            # Intervention effectiveness
    ├── cost_benefit.py                   # Cost-benefit analysis
    └── optimization.py                   # Intervention optimization
```

---

## 3. Detailed Engine Specifications

### 3.1 Advanced Disaster Scenario Modeling Engine

**File**: `src/simulation/scenarios/disaster_models.py`

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum, auto
import numpy as np
from datetime import datetime, timedelta

class DisasterCategory(Enum):
    HYDROLOGICAL = auto()      # Floods, tsunamis
    METEOROLOGICAL = auto()    # Hurricanes, tornadoes, winter storms
    GEOLOGICAL = auto()        # Earthquakes, landslides, volcanic
    CLIMATOLOGICAL = auto()    # Droughts, wildfires, heat waves
    BIOLOGICAL = auto()        # Pandemics, epidemics
    TECHNOLOGICAL = auto()     # Industrial accidents
    CONFLICT = auto()          # Civil unrest, terrorism

class HazardIntensity(Enum):
    MINOR = 1
    MODERATE = 2
    SIGNIFICANT = 3
    SEVERE = 4
    EXTREME = 5
    CATASTROPHIC = 6

@dataclass
class DisasterScenario:
    """Base class for all disaster scenarios."""
    scenario_id: str
    name: str
    category: DisasterCategory
    intensity: HazardIntensity
    epicenter_lat: float
    epicenter_lon: float
    affected_area_km2: float
    primary_radius_km: float
    secondary_radius_km: float
    onset_time: datetime
    duration_hours: float
    warning_time_hours: float
    base_damage_factor: float  # 0-1 scale
    fatality_rate: float  # per 100,000 population
    injury_rate: float  # per 100,000 population
    displacement_rate: float  # percentage of population
    secondary_hazards: List[str] = field(default_factory=list)
    
    def get_intensity_at_distance(self, distance_km: float) -> float:
        raise NotImplementedError

@dataclass  
class HurricaneScenario(DisasterScenario):
    """Hurricane-specific scenario parameters."""
    category_saffir_simpson: int  # 1-5
    max_wind_speed_mph: float
    central_pressure_mb: float
    storm_surge_m: float
    forward_speed_mph: float
    radius_max_wind_km: float
    radius_gale_force_km: float
    max_rainfall_inches: float
    rainfall_duration_hours: float
    
    def get_intensity_at_distance(self, distance_km: float) -> float:
        """Holland wind field model for hurricane intensity."""
        if distance_km <= self.radius_max_wind_km:
            return 1.0
        elif distance_km <= self.radius_gale_force_km:
            decay = np.exp(-(distance_km - self.radius_max_wind_km) / 50)
            return decay
        else:
            return 0.0

@dataclass
class EarthquakeScenario(DisasterScenario):
    """Earthquake-specific scenario parameters."""
    magnitude: float
    depth_km: float
    fault_type: str
    peak_ground_acceleration_g: float
    spectral_acceleration_1s: float
    duration_strong_shaking_s: float
    liquefaction_susceptibility: str
    tsunami_potential: bool
    tsunami_height_m: Optional[float] = None
    
    def get_intensity_at_distance(self, distance_km: float) -> float:
        """Joyner-Boore distance attenuation model."""
        attenuation = np.exp(-0.5 * distance_km / 50)
        return attenuation

@dataclass
class FloodScenario(DisasterScenario):
    """Flood-specific scenario parameters."""
    flood_type: str  # riverine, flash, coastal, urban
    return_period_years: int
    peak_flow_cms: float
    flood_depth_m: float
    flood_duration_hours: float
    flood_extent_km2: float
    flow_velocity_ms: float
    contamination_level: str
    
    def get_intensity_at_distance(self, distance_km: float) -> float:
        if distance_km < 1:
            return 1.0
        else:
            return np.exp(-distance_km / 5)

@dataclass
class WildfireScenario(DisasterScenario):
    """Wildfire-specific scenario parameters."""
    fire_size_acres: float
    fire_behavior: str
    rate_of_spread_ch_per_hour: float
    flame_length_m: float
    fuel_moisture_percent: float
    wind_speed_mph: float
    smoke_impact_radius_km: float
    air_quality_index: int
    
    def get_intensity_at_distance(self, distance_km: float) -> float:
        fire_radius_km = np.sqrt(self.fire_size_acres * 0.004047)
        if distance_km < fire_radius_km:
            return 1.0
        elif distance_km < self.smoke_impact_radius_km:
            return 0.3  # Smoke impact
        else:
            return 0.0
```

### 3.2 Compound Event Modeling

```python
@dataclass
class CompoundEventScenario:
    """Model for multi-hazard compound events."""
    scenario_id: str
    name: str
    primary_hazard: DisasterScenario
    secondary_hazards: List[DisasterScenario]
    time_lags_hours: Dict[str, float]
    interaction_matrix: np.ndarray
    cascading_thresholds: Dict[str, float]
    
    def calculate_compound_impact(self, base_impacts: Dict[str, float]) -> float:
        total_impact = base_impacts.get(self.primary_hazard.scenario_id, 0)
        for hazard in self.secondary_hazards:
            hazard_impact = base_impacts.get(hazard.scenario_id, 0)
            idx_primary = self._get_hazard_index(self.primary_hazard)
            idx_hazard = self._get_hazard_index(hazard)
            interaction = self.interaction_matrix[idx_primary, idx_hazard]
            total_impact += hazard_impact * interaction
        return total_impact
```

### 3.3 Resource Requirement Estimation Engine

**File**: `src/simulation/resources/resource_calculator.py`

```python
@dataclass
class ResourceRequirements:
    hospital_beds_needed: int
    icu_beds_needed: int
    ambulances_needed: int
    medical_staff_needed: int
    fire_units_needed: int
    police_units_needed: int
    search_rescue_teams_needed: int
    shelter_capacity_needed: int
    food_meals_per_day: int
    water_gallons_per_day: int
    heavy_equipment_needed: int
    generators_needed: int
    temporary_housing_units: int
    emergency_management_staff: int
    volunteers_needed: int
    immediate_response_cost: float
    short_term_recovery_cost: float
    long_term_recovery_cost: float

class ResourceCalculator:
    RESOURCE_MULTIPLIERS = {
        'hospital_beds_per_1000': 5,
        'icu_beds_per_1000': 1,
        'ambulances_per_1000': 0.5,
        'shelter_capacity_per_1000': 100,
        'food_meals_per_person_per_day': 3,
        'water_gallons_per_person_per_day': 1,
    }
    
    def calculate_requirements(self, affected_population: int,
                               injury_distribution: Dict[str, int],
                               infrastructure_damage: Dict[str, float],
                               scenario_type: str) -> ResourceRequirements:
        medical = self._calculate_medical_resources(affected_population, injury_distribution)
        emergency = self._calculate_emergency_resources(affected_population, infrastructure_damage)
        shelter = self._calculate_shelter_needs(affected_population, infrastructure_damage)
        financial = self._calculate_financial_requirements(affected_population, infrastructure_damage, scenario_type)
        
        return ResourceRequirements(
            hospital_beds_needed=medical['hospital_beds'],
            icu_beds_needed=medical['icu_beds'],
            shelter_capacity_needed=shelter['capacity'],
            immediate_response_cost=financial['immediate'],
            # ... other fields
        )
```

### 3.4 Economic Impact Modeling Engine

**File**: `src/simulation/economic/direct_damage.py`

```python
@dataclass
class EconomicImpact:
    residential_damage: float
    commercial_damage: float
    industrial_damage: float
    public_infrastructure_damage: float
    business_interruption: float
    lost_productivity: float
    supply_chain_disruption: float
    emergency_response_cost: float
    debris_removal_cost: float
    temporary_housing_cost: float
    total_direct_damage: float
    total_indirect_damage: float
    total_economic_impact: float
    insured_losses: float
    uninsured_losses: float
    impact_per_capita: float

class EconomicImpactModel:
    REPLACEMENT_COSTS = {
        'residential_single_family': 150,
        'commercial_office': 250,
        'industrial': 180,
        'public_hospital': 500,
    }
    
    def calculate_economic_impact(self, scenario: DisasterScenario,
                                   physical_damage: Dict,
                                   affected_counties: List[str]) -> EconomicImpact:
        residential = self._calculate_residential_damage(scenario, physical_damage, affected_counties)
        commercial = self._calculate_commercial_damage(scenario, physical_damage, affected_counties)
        business_interruption = self._calculate_business_interruption(commercial, affected_counties)
        total_direct = residential + commercial + business_interruption
        
        return EconomicImpact(
            residential_damage=residential,
            commercial_damage=commercial,
            business_interruption=business_interruption,
            total_direct_damage=total_direct,
            # ... other fields
        )
```

### 3.5 Infrastructure Failure Cascading Engine

**File**: `src/simulation/infrastructure/cascade_model.py`

```python
class CascadeSimulator:
    def __init__(self):
        self.networks: Dict[InfrastructureType, nx.DiGraph] = {}
        self.interdependencies: nx.DiGraph = nx.DiGraph()
        self.nodes: Dict[str, InfrastructureNode] = {}
    
    def simulate_cascade(self, initial_failures: List[str], max_iterations: int = 10) -> Dict:
        results = {
            'initial_failures': initial_failures.copy(),
            'cascade_steps': [],
            'total_failed_nodes': set(initial_failures),
            'affected_infrastructure': {}
        }
        failed_this_step = set(initial_failures)
        
        for iteration in range(max_iterations):
            if not failed_this_step:
                break
            next_failures = set()
            for node_id, node in self.nodes.items():
                if node_id in results['total_failed_nodes']:
                    continue
                failed_deps = [d for d in node.depends_on if d in results['total_failed_nodes']]
                if failed_deps:
                    failure_prob = self._calculate_failure_probability(node, failed_deps)
                    if np.random.random() < failure_prob:
                        next_failures.add(node_id)
            results['total_failed_nodes'].update(next_failures)
            failed_this_step = next_failures
        
        return results
```

### 3.6 Population Displacement Modeling Engine

**File**: `src/simulation/population/displacement_model.py`

```python
class PopulationDisplacementModel:
    def __init__(self, county_data: pd.DataFrame, demographic_data: pd.DataFrame):
        self.county_data = county_data
        self.demographic_data = demographic_data
        self.displacement_factors = {
            'renter': 1.5, 'elderly': 1.3, 'low_income': 1.2,
            'single_parent': 1.4, 'disabled': 1.3
        }
    
    def estimate_displacement(self, scenario: DisasterScenario,
                               housing_damage: Dict[str, float],
                               utility_status: Dict[str, bool],
                               affected_counties: List[str]) -> Dict:
        results = {
            'total_displaced': 0,
            'displacement_by_county': {},
            'displacement_timeline': {},
            'destination_distribution': {},
            'shelter_needs': 0
        }
        
        for county_fips in affected_counties:
            county_pop = self.county_data[self.county_data['fips'] == county_fips]['total_population'].iloc[0]
            base_rate = self._calculate_base_displacement_rate(county_fips, housing_damage, utility_status)
            county_displaced = int(county_pop * base_rate)
            results['displacement_by_county'][county_fips] = {
                'total_displaced': county_displaced,
                'displacement_rate': county_displaced / county_pop if county_pop > 0 else 0
            }
            results['total_displaced'] += county_displaced
        
        results['shelter_needs'] = int(results['total_displaced'] * 0.3)
        return results
```

### 3.7 Recovery Time Estimation Engine

**File**: `src/simulation/recovery/recovery_timeline.py`

```python
class RecoveryTimelineModel:
    RECOVERY_MILESTONES = {
        'emergency_response': {'typical_days': 7, 'min_days': 3, 'max_days': 14},
        'damage_assessment': {'typical_days': 14, 'min_days': 7, 'max_days': 30},
        'debris_removal': {'typical_days': 60, 'min_days': 30, 'max_days': 180},
        'utility_restoration': {'typical_days': 30, 'min_days': 7, 'max_days': 90},
        'housing_temporary': {'typical_days': 45, 'min_days': 14, 'max_days': 90},
        'business_reopening': {'typical_days': 90, 'min_days': 30, 'max_days': 180},
        'infrastructure_repair': {'typical_days': 180, 'min_days': 90, 'max_days': 365},
        'housing_permanent': {'typical_days': 365, 'min_days': 180, 'max_days': 730},
        'economic_recovery': {'typical_days': 730, 'min_days': 365, 'max_days': 1825},
    }
    
    def estimate_recovery_timeline(self, scenario: DisasterScenario,
                                   damage_assessment: Dict,
                                   economic_impact: any,
                                   resource_availability: Dict,
                                   affected_counties: List[str]) -> Dict:
        damage_severity = self._calculate_damage_severity(damage_assessment)
        resource_factor = self._calculate_resource_factor(resource_availability)
        
        results = {'milestones': {}, 'critical_path': [], 'estimated_completion': {}}
        
        for milestone_id, milestone in self.RECOVERY_MILESTONES.items():
            estimated_days = self._estimate_milestone_duration(milestone, damage_severity, resource_factor)
            results['milestones'][milestone_id] = {
                'estimated_days': estimated_days,
                'min_days': int(estimated_days * 0.7),
                'max_days': int(estimated_days * 1.5)
            }
        
        total_days = sum(m['estimated_days'] for m in results['milestones'].values())
        results['estimated_completion'] = {
            'total_days': total_days,
            'total_years': round(total_days / 365, 1)
        }
        return results
```

### 3.8 Intervention Effectiveness Engine

**File**: `src/simulation/intervention/effectiveness_model.py`

```python
@dataclass
class Intervention:
    intervention_id: str
    name: str
    type: InterventionType
    capital_cost: float
    annual_maintenance_cost: float
    implementation_years: float
    damage_reduction_percent: float
    fatality_reduction_percent: float
    economic_loss_reduction_percent: float
    recovery_time_reduction_percent: float
    applicable_hazards: List[str]
    co_benefits: Dict[str, float]

class InterventionEffectivenessModel:
    INTERVENTIONS = {
        'seismic_retrofit': Intervention(
            intervention_id='seismic_retrofit',
            name='Building Seismic Retrofit Program',
            type=InterventionType.STRUCTURAL,
            capital_cost=50_000_000,
            annual_maintenance_cost=500_000,
            implementation_years=5,
            damage_reduction_percent=40,
            fatality_reduction_percent=60,
            economic_loss_reduction_percent=35,
            recovery_time_reduction_percent=25,
            applicable_hazards=['earthquake'],
            co_benefits={'property_value_increase': 0.15}
        ),
        'early_warning_system': Intervention(
            intervention_id='early_warning_system',
            name='Multi-Hazard Early Warning System',
            type=InterventionType.NON_STRUCTURAL,
            capital_cost=10_000_000,
            annual_maintenance_cost=2_000_000,
            implementation_years=2,
            damage_reduction_percent=15,
            fatality_reduction_percent=50,
            economic_loss_reduction_percent=10,
            recovery_time_reduction_percent=5,
            applicable_hazards=['tornado', 'flood', 'hurricane', 'wildfire'],
            co_benefits={'public_awareness_increase': 0.30}
        ),
        'flood_mitigation': Intervention(
            intervention_id='flood_mitigation',
            name='Flood Mitigation Infrastructure',
            type=InterventionType.STRUCTURAL,
            capital_cost=100_000_000,
            annual_maintenance_cost=3_000_000,
            implementation_years=7,
            damage_reduction_percent=70,
            fatality_reduction_percent=80,
            economic_loss_reduction_percent=60,
            recovery_time_reduction_percent=50,
            applicable_hazards=['flood'],
            co_benefits={'recreational_value': 5_000_000}
        ),
    }
    
    def evaluate_intervention(self, intervention_id: str, target_counties: List[str]) -> Dict:
        intervention = self.INTERVENTIONS.get(intervention_id)
        baseline = self._calculate_baseline_metrics(target_counties)
        
        total_cost = intervention.capital_cost + intervention.annual_maintenance_cost * 20
        annual_benefit = baseline['estimated_annual_damage'] * intervention.damage_reduction_percent / 100
        total_benefit = annual_benefit * 20
        
        return {
            'intervention': intervention,
            'total_cost_20yr': total_cost,
            'total_benefit_20yr': total_benefit,
            'net_benefit': total_benefit - total_cost,
            'benefit_cost_ratio': total_benefit / total_cost if total_cost > 0 else 0,
            'payback_period_years': intervention.capital_cost / annual_benefit if annual_benefit > 0 else float('inf')
        }
```

### 3.9 Multi-Scenario Comparison Engine

**File**: `src/simulation/core/simulation_orchestrator.py`

```python
@dataclass
class SimulationResult:
    scenario_id: str
    scenario_name: str
    physical_impact: Dict
    economic_impact: any
    resource_requirements: any
    infrastructure_cascade: Dict
    displacement: Dict
    recovery_timeline: Dict
    computation_time_seconds: float

class SimulationOrchestrator:
    def __init__(self, county_data: pd.DataFrame, infrastructure_data: pd.DataFrame):
        self.county_data = county_data
        self.infrastructure_data = infrastructure_data
        self.impact_engine = PhysicalImpactAssessment()
        self.resource_engine = ResourceCalculator(county_data)
        self.economic_engine = EconomicImpactModel(county_data, infrastructure_data)
        self.cascade_engine = CascadeSimulator()
        self.displacement_engine = PopulationDisplacementModel(county_data, pd.DataFrame())
        self.recovery_engine = RecoveryTimelineModel(county_data, infrastructure_data)
        self.intervention_engine = InterventionEffectivenessModel(county_data, pd.DataFrame())
    
    def run_single_scenario(self, scenario: DisasterScenario, epicenter_fips: str) -> SimulationResult:
        import time
        start_time = time.time()
        
        affected_counties = self._get_affected_counties(scenario)
        physical_impact = self.impact_engine.assess_damage(scenario, affected_counties)
        
        affected_pop = sum(self.county_data[self.county_data['fips'] == f]['total_population'].iloc[0] for f in affected_counties)
        resource_reqs = self.resource_engine.calculate_requirements(
            affected_pop, {'minor': 100, 'major': 20, 'critical': 5}, physical_impact, scenario.category.name.lower())
        
        economic_impact = self.economic_engine.calculate_economic_impact(scenario, physical_impact, affected_counties)
        cascade_results = self.cascade_engine.simulate_cascade(self._identify_initial_failures(physical_impact))
        displacement = self.displacement_engine.estimate_displacement(scenario, physical_impact.get('housing', {}), {}, affected_counties)
        recovery = self.recovery_engine.estimate_recovery_timeline(scenario, physical_impact, economic_impact, {'funding_percent_of_need': 60}, affected_counties)
        
        return SimulationResult(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            physical_impact=physical_impact,
            economic_impact=economic_impact,
            resource_requirements=resource_reqs,
            infrastructure_cascade=cascade_results,
            displacement=displacement,
            recovery_timeline=recovery,
            computation_time_seconds=time.time() - start_time
        )
    
    def run_scenario_comparison(self, scenarios: List[DisasterScenario], epicenter_fips: str) -> Dict:
        results = {s.scenario_id: self.run_single_scenario(s, epicenter_fips) for s in scenarios}
        comparison = {'scenarios': {}, 'rankings': {}}
        
        for metric in ['population_at_risk', 'economic_impact', 'recovery_time']:
            comparison['rankings'][metric] = self._rank_by_metric(results, metric)
        
        return comparison
    
    def run_sensitivity_analysis(self, base_scenario: DisasterScenario, 
                                  parameter_ranges: Dict[str, Tuple[float, float, int]],
                                  epicenter_fips: str) -> Dict:
        results = {'parameter_sensitivities': {}, 'critical_parameters': []}
        
        for param_name, (min_val, max_val, steps) in parameter_ranges.items():
            param_results = []
            for value in np.linspace(min_val, max_val, steps):
                modified = self._modify_scenario_parameter(base_scenario, param_name, value)
                sim_result = self.run_single_scenario(modified, epicenter_fips)
                param_results.append({
                    'parameter_value': value,
                    'economic_impact': sim_result.economic_impact.total_economic_impact
                })
            results['parameter_sensitivities'][param_name] = param_results
        
        return results
```

---

## 4. Mathematical Models Reference

### 4.1 Impact Decay Models

| Hazard Type | Decay Function |
|-------------|----------------|
| Hurricane | $V(r) = V_{max} \cdot \sqrt{\frac{R_{max}}{r} \cdot e^{1-\frac{R_{max}}{r}}}$ |
| Earthquake | $PGA(d) = PGA_0 \cdot e^{-0.5d/50}$ |
| Flood | $D(d) = D_0 \cdot e^{-d/5}$ |
| Wildfire | $I(d) = 1$ if $d < r_{fire}$, $0.3$ if $d < r_{smoke}$ |

### 4.2 Resource Requirement Formulas

```
Hospital Beds = Major_Injuries + 0.2 × Minor_Injuries
ICU Beds = Critical_Injuries + 0.1 × Major_Injuries
Ambulances = max(2, Total_Transports / 10)
Shelter Capacity = 0.1 × Affected_Population
Food (meals/day) = 3 × Displaced_Population
Water (gallons/day) = 1 × Displaced_Population
```

### 4.3 Recovery Time Estimation

```
Recovery_Days = Base_Days × (1 + Damage_Severity × 0.5) × (1.5 - Resource_Factor) × (1 + Vulnerability × 0.3)
```

---

## 5. Implementation Priority Order

### Phase 1: Core Infrastructure (Weeks 1-2)

| Priority | Component | Effort |
|----------|-----------|--------|
| 1 | Base engine classes | 2 days |
| 2 | Enhanced disaster models | 3 days |
| 3 | Physical impact engine | 3 days |
| 4 | Resource calculator | 2 days |
| 5 | Orchestrator integration | 3 days |

### Phase 2: Advanced Capabilities (Weeks 3-4)

| Priority | Component | Effort |
|----------|-----------|--------|
| 6 | Economic impact modeling | 4 days |
| 7 | Infrastructure cascading | 4 days |
| 8 | Population displacement | 3 days |
| 9 | Recovery time estimation | 3 days |

### Phase 3: Specialized Engines (Weeks 5-6)

| Priority | Component | Effort |
|----------|-----------|--------|
| 10 | Evacuation planning | 4 days |
| 11 | Intervention effectiveness | 4 days |
| 12 | Compound events | 2 days |
| 13 | Multi-scenario comparison | 2 days |

### Phase 4: Integration & Testing (Week 7)

| Priority | Component | Effort |
|----------|-----------|--------|
| 14 | Backward compatibility | 2 days |
| 15 | Unit tests | 3 days |
| 16 | Integration tests | 2 days |
| 17 | Documentation | 2 days |

---

## 6. Usage Examples

### Example 1: Basic Scenario Simulation

```python
from simulation import SimulationOrchestrator
from simulation.scenarios.disaster_models import HurricaneScenario, HazardIntensity
import pandas as pd

county_data = pd.read_csv('data/processed/county_features.csv')
orchestrator = SimulationOrchestrator(county_data, infrastructure_data=pd.DataFrame())

hurricane = HurricaneScenario(
    scenario_id='hurricane_test_001',
    name='Category 3 Hurricane Test',
    category='hurricane',
    intensity=HazardIntensity.SIGNIFICANT,
    epicenter_lat=29.95, epicenter_lon=-90.07,
    primary_radius_km=200, secondary_radius_km=300,
    onset_time=pd.Timestamp('2026-06-01'),
    duration_hours=48, warning_time_hours=48,
    base_damage_factor=0.35, fatality_rate=0.5,
    category_saffir_simpson=3, max_wind_speed_mph=120,
    storm_surge_m=3.0, radius_gale_force_km=200
)

result = orchestrator.run_single_scenario(hurricane, epicenter_fips='22071')
print(f"Total Economic Impact: ${result.economic_impact.total_economic_impact:,.0f}")
print(f"Population Displaced: {result.displacement['total_displaced']:,}")
```

### Example 2: Intervention Effectiveness Analysis

```python
from simulation.intervention.effectiveness_model import InterventionEffectivenessModel

intervention_model = InterventionEffectivenessModel(county_data, baseline_risk)
evaluation = intervention_model.evaluate_intervention(
    intervention_id='flood_mitigation',
    target_counties=['22071', '22051', '22075']
)
print(f"Benefit-Cost Ratio: {evaluation['benefit_cost_ratio']:.2f}")
print(f"Net Benefit: ${evaluation['net_benefit']:,.0f}")
```

---

## 7. Summary

This comprehensive scenario simulation enhancement design provides ResilienceAI with:

1. **10 specialized simulation engines** covering all aspects of disaster impact assessment
2. **Backward compatibility** with existing `scenario_simulator.py` API
3. **Modular architecture** allowing independent engine development and testing
4. **Rich mathematical models** for realistic impact estimation
5. **Multi-scenario comparison** capabilities for decision support
6. **Intervention effectiveness** analysis for mitigation planning

---

## Generated Files

| File Path | Description |
|-----------|-------------|
| `/mnt/okcomputer/output/resilience_ai_analysis/23_scenario_simulation.md` | Comprehensive design document |

---

*Document Version: 1.0*
*Generated for: ResilienceAI Scenario Simulation Enhancement*
*Repository: https://github.com/GDogMcCoy/ResilienceAI (claw-autonomous branch)*
