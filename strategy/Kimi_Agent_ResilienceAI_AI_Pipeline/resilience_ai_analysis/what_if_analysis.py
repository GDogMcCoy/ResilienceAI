"""
What-If Analysis Framework for Digital Twin
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from copy import deepcopy
import numpy as np


@dataclass
class ScenarioConfig:
    """Configuration for what-if scenario"""
    name: str
    description: str
    interventions: List[Dict]
    budget_constraint: Optional[float] = None
    time_horizon_years: int = 5


@dataclass
class WhatIfResult:
    """Result of what-if analysis"""
    scenario_name: str
    baseline_metrics: Dict[str, float]
    scenario_metrics: Dict[str, float]
    delta_metrics: Dict[str, float]
    cost_estimate: float
    roi: float
    implementation_timeline: List[Dict]
    risk_mitigation: Dict[str, float]


class WhatIfAnalysisEngine:
    """Engine for what-if scenario analysis"""
    
    def __init__(self, county_twin: Any):
        self.county_twin = county_twin
        self.baseline_state = None
    
    def capture_baseline(self):
        """Capture current state as baseline"""
        self.baseline_state = {
            "assets": deepcopy(self.county_twin.assets),
            "networks": deepcopy(self.county_twin.networks),
            "resilience": self.county_twin.calculate_resilience_index()
        }
    
    def run_scenario(self, config: ScenarioConfig) -> WhatIfResult:
        """Run what-if scenario"""
        if not self.baseline_state:
            self.capture_baseline()
        
        scenario_twin = self._create_scenario_twin(config)
        baseline_metrics = self._extract_metrics(self.baseline_state)
        scenario_metrics = self._extract_metrics_from_twin(scenario_twin)
        
        delta_metrics = {
            k: scenario_metrics.get(k, 0) - baseline_metrics.get(k, 0)
            for k in set(baseline_metrics.keys()) | set(scenario_metrics.keys())
        }
        
        cost_estimate = self._estimate_cost(config)
        roi = self._calculate_roi(delta_metrics, cost_estimate)
        risk_mitigation = self._calculate_risk_mitigation(config)
        
        return WhatIfResult(
            scenario_name=config.name,
            baseline_metrics=baseline_metrics,
            scenario_metrics=scenario_metrics,
            delta_metrics=delta_metrics,
            cost_estimate=cost_estimate,
            roi=roi,
            implementation_timeline=self._create_timeline(config),
            risk_mitigation=risk_mitigation
        )
    
    def _create_scenario_twin(self, config: ScenarioConfig) -> Any:
        """Create modified twin for scenario"""
        scenario_twin = deepcopy(self.county_twin)
        
        for intervention in config.interventions:
            intervention_type = intervention.get("type")
            
            if intervention_type == "asset_upgrade":
                self._apply_asset_upgrade(scenario_twin, intervention)
            elif intervention_type == "network_improvement":
                self._apply_network_improvement(scenario_twin, intervention)
            elif intervention_type == "new_construction":
                self._apply_new_construction(scenario_twin, intervention)
            elif intervention_type == "maintenance_increase":
                self._apply_maintenance_increase(scenario_twin, intervention)
        
        return scenario_twin
    
    def _apply_asset_upgrade(self, twin: Any, intervention: Dict):
        """Apply asset upgrade intervention"""
        asset_ids = intervention.get("asset_ids", [])
        upgrade_level = intervention.get("upgrade_level", 0.2)
        
        for asset_id in asset_ids:
            if asset_id in twin.assets:
                twin.assets[asset_id]["condition_index"] = min(
                    1.0, twin.assets[asset_id].get("condition_index", 0.5) + upgrade_level
                )
                twin.assets[asset_id]["upgraded"] = True
    
    def _apply_network_improvement(self, twin: Any, intervention: Dict):
        """Apply network improvement intervention"""
        network_type = intervention.get("network_type")
        improvement = intervention.get("improvement", 0.2)
        
        if network_type in twin.networks:
            network = twin.networks[network_type]
            current_edges = len(network.edges)
            target_edges = int(current_edges * (1 + improvement))
            
            for i in range(target_edges - current_edges):
                if len(network.nodes) >= 2:
                    from_node = network.nodes[i % len(network.nodes)]["id"]
                    to_node = network.nodes[(i + 2) % len(network.nodes)]["id"]
                    network.add_edge(from_node, to_node, {"redundancy": True})
    
    def _apply_new_construction(self, twin: Any, intervention: Dict):
        """Apply new construction intervention"""
        new_assets = intervention.get("new_assets", [])
        for asset_data in new_assets:
            asset_id = twin.register_asset(asset_data)
            twin.assets[asset_id]["new_construction"] = True
    
    def _apply_maintenance_increase(self, twin: Any, intervention: Dict):
        """Apply increased maintenance intervention"""
        increase_factor = intervention.get("increase_factor", 1.5)
        
        for asset in twin.assets.values():
            current_maintenance = asset.get("maintenance_frequency", 1)
            asset["maintenance_frequency"] = current_maintenance * increase_factor
            asset["condition_index"] = min(1.0, asset.get("condition_index", 0.5) + 0.1)
    
    def _extract_metrics(self, state: Dict) -> Dict[str, float]:
        """Extract metrics from state"""
        resilience = state.get("resilience", {})
        return {
            "overall_resilience": resilience.get("overall", 0),
            "infrastructure_health": resilience.get("infrastructure_health", 0),
            "network_connectivity": resilience.get("network_connectivity", 0),
            "emergency_preparedness": resilience.get("emergency_preparedness", 0),
            "environmental_risk": resilience.get("environmental_risk", 0),
            "asset_count": len(state.get("assets", {})),
            "critical_assets": sum(
                1 for a in state.get("assets", {}).values()
                if a.get("criticality_score", 0) > 0.8
            )
        }
    
    def _extract_metrics_from_twin(self, twin: Any) -> Dict[str, float]:
        """Extract metrics from twin"""
        resilience = twin.calculate_resilience_index()
        return {
            "overall_resilience": resilience.get("overall", 0),
            "infrastructure_health": resilience.get("infrastructure_health", 0),
            "network_connectivity": resilience.get("network_connectivity", 0),
            "emergency_preparedness": resilience.get("emergency_preparedness", 0),
            "environmental_risk": resilience.get("environmental_risk", 0),
            "asset_count": len(twin.assets),
            "critical_assets": sum(
                1 for a in twin.assets.values()
                if a.get("criticality_score", 0) > 0.8
            )
        }
    
    def _estimate_cost(self, config: ScenarioConfig) -> float:
        """Estimate implementation cost"""
        total_cost = 0
        
        for intervention in config.interventions:
            intervention_type = intervention.get("type")
            
            if intervention_type == "asset_upgrade":
                asset_count = len(intervention.get("asset_ids", []))
                total_cost += asset_count * 500000
            elif intervention_type == "network_improvement":
                improvement = intervention.get("improvement", 0.2)
                total_cost += improvement * 2000000
            elif intervention_type == "new_construction":
                new_assets = intervention.get("new_assets", [])
                total_cost += len(new_assets) * 2000000
            elif intervention_type == "maintenance_increase":
                increase_factor = intervention.get("increase_factor", 1.5)
                total_cost += (increase_factor - 1) * 1000000
        
        return total_cost
    
    def _calculate_roi(self, delta_metrics: Dict[str, float], cost: float) -> float:
        """Calculate return on investment"""
        resilience_value = delta_metrics.get("overall_resilience", 0) * 10000000
        risk_value = -delta_metrics.get("environmental_risk", 0) * 5000000
        total_value = resilience_value + risk_value
        
        if cost == 0:
            return 0
        return (total_value - cost) / cost
    
    def _calculate_risk_mitigation(self, config: ScenarioConfig) -> Dict[str, float]:
        """Calculate risk mitigation achieved"""
        mitigation = {}
        for intervention in config.interventions:
            intervention_type = intervention.get("type")
            if intervention_type == "flood_mitigation":
                mitigation["flood_risk"] = 0.3
            elif intervention_type == "seismic_retrofit":
                mitigation["seismic_risk"] = 0.25
            elif intervention_type == "asset_upgrade":
                mitigation["infrastructure_failure"] = 0.2
        return mitigation
    
    def _create_timeline(self, config: ScenarioConfig) -> List[Dict]:
        """Create implementation timeline"""
        timeline = []
        current_year = datetime.now().year
        
        for i, intervention in enumerate(config.interventions):
            timeline.append({
                "phase": i + 1,
                "year": current_year + i,
                "intervention": intervention.get("type"),
                "description": intervention.get("description", ""),
                "estimated_cost": self._estimate_single_intervention(intervention)
            })
        
        return timeline
    
    def _estimate_single_intervention(self, intervention: Dict) -> float:
        """Estimate cost of single intervention"""
        intervention_type = intervention.get("type")
        if intervention_type == "asset_upgrade":
            return len(intervention.get("asset_ids", [])) * 500000
        elif intervention_type == "network_improvement":
            return intervention.get("improvement", 0.2) * 2000000
        elif intervention_type == "new_construction":
            return len(intervention.get("new_assets", [])) * 2000000
        elif intervention_type == "maintenance_increase":
            return (intervention.get("increase_factor", 1.5) - 1) * 1000000
        return 0
    
    def compare_scenarios(self, scenarios: List[WhatIfResult]) -> Dict:
        """Compare multiple what-if scenarios"""
        if not scenarios:
            return {}
        
        return {
            "scenarios_compared": len(scenarios),
            "best_roi": max(scenarios, key=lambda x: x.roi).scenario_name,
            "highest_resilience": max(scenarios, key=lambda x: x.scenario_metrics.get("overall_resilience", 0)).scenario_name,
            "lowest_cost": min(scenarios, key=lambda x: x.cost_estimate).scenario_name,
            "comparison_table": [
                {
                    "name": s.scenario_name,
                    "cost": s.cost_estimate,
                    "roi": s.roi,
                    "resilience_improvement": s.delta_metrics.get("overall_resilience", 0),
                    "risk_reduction": -s.delta_metrics.get("environmental_risk", 0)
                }
                for s in scenarios
            ]
        }
