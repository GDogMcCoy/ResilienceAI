"""
Digital Twin Simulation Engine for ResilienceAI
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import numpy as np


class ScenarioType(Enum):
    """Types of simulation scenarios"""
    FLOOD = "flood"
    HURRICANE = "hurricane"
    EARTHQUAKE = "earthquake"
    WILDFIRE = "wildfire"
    POWER_OUTAGE = "power_outage"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    EXTREME_HEAT = "extreme_heat"


@dataclass
class SimulationResult:
    """Result of a simulation run"""
    simulation_id: str
    scenario_type: ScenarioType
    start_time: datetime
    end_time: datetime
    affected_assets: List[str] = field(default_factory=list)
    damaged_assets: List[str] = field(default_factory=list)
    service_disruptions: List[str] = field(default_factory=list)
    estimated_damage_cost: float = 0.0
    recovery_cost: float = 0.0
    economic_impact: float = 0.0
    time_to_impact_hours: float = 0.0
    estimated_recovery_days: int = 0
    resilience_score_before: float = 0.0
    resilience_score_after: float = 0.0


class ScenarioEngine:
    """Simulation scenario engine"""
    
    def __init__(self, county_twin: Any):
        self.county_twin = county_twin
        self.active_simulations: Dict[str, SimulationResult] = {}
    
    def run_simulation(self, scenario_type: ScenarioType, 
                       intensity: float, duration_hours: int) -> SimulationResult:
        """Run a simulation scenario"""
        sim_id = f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        initial_resilience = self.county_twin.calculate_resilience_index()
        start_time = datetime.now()
        
        if scenario_type == ScenarioType.FLOOD:
            impact = self._simulate_flood(intensity, duration_hours)
        elif scenario_type == ScenarioType.HURRICANE:
            impact = self._simulate_hurricane(intensity, duration_hours)
        elif scenario_type == ScenarioType.EARTHQUAKE:
            impact = self._simulate_earthquake(intensity)
        elif scenario_type == ScenarioType.WILDFIRE:
            impact = self._simulate_wildfire(intensity, duration_hours)
        elif scenario_type == ScenarioType.POWER_OUTAGE:
            impact = self._simulate_power_outage(intensity, duration_hours)
        elif scenario_type == ScenarioType.EXTREME_HEAT:
            impact = self._simulate_extreme_heat(intensity, duration_hours)
        else:
            impact = {"affected_assets": [], "damaged_assets": []}
        
        end_time = datetime.now()
        
        result = SimulationResult(
            simulation_id=sim_id,
            scenario_type=scenario_type,
            start_time=start_time,
            end_time=end_time,
            affected_assets=impact.get("affected_assets", []),
            damaged_assets=impact.get("damaged_assets", []),
            service_disruptions=impact.get("disruptions", []),
            estimated_damage_cost=impact.get("damage_cost", 0),
            recovery_cost=impact.get("recovery_cost", 0),
            economic_impact=impact.get("economic_impact", 0),
            time_to_impact_hours=impact.get("time_to_impact", 0),
            estimated_recovery_days=impact.get("recovery_days", 0),
            resilience_score_before=initial_resilience["overall"],
            resilience_score_after=impact.get("resilience_after", 0)
        )
        
        self.active_simulations[sim_id] = result
        return result
    
    def _simulate_flood(self, intensity: float, duration_hours: int) -> Dict:
        """Simulate flood scenario"""
        affected = []
        damaged = []
        disruptions = []
        
        for asset_id, asset in self.county_twin.assets.items():
            elevation = asset.get("elevation", 100)
            flood_risk = asset.get("flood_risk", 0.5)
            flood_depth = 5 * intensity  # 5m base depth
            
            if elevation < flood_depth * 10:
                affected.append(asset_id)
                damage_prob = flood_risk * intensity
                if np.random.random() < damage_prob:
                    damaged.append(asset_id)
                    if asset.get("criticality_score", 0) > 0.7:
                        disruptions.append(f"{asset_id}_service")
        
        damage_cost = len(damaged) * 500000
        recovery_cost = damage_cost * 1.5
        
        return {
            "affected_assets": affected,
            "damaged_assets": damaged,
            "disruptions": disruptions,
            "damage_cost": damage_cost,
            "recovery_cost": recovery_cost,
            "economic_impact": recovery_cost * 2,
            "time_to_impact": duration_hours * 0.2,
            "recovery_days": int(len(damaged) / 5) + 30,
            "resilience_after": max(0, 0.8 - len(damaged) * 0.01)
        }
    
    def _simulate_hurricane(self, intensity: float, duration_hours: int) -> Dict:
        """Simulate hurricane scenario"""
        affected = []
        damaged = []
        disruptions = []
        wind_speed = 100 * intensity
        
        for asset_id, asset in self.county_twin.assets.items():
            wind_vuln = asset.get("wind_vulnerability", 0.5)
            if wind_speed > 74:
                affected.append(asset_id)
                damage_prob = wind_vuln * (wind_speed / 150) * intensity
                if np.random.random() < damage_prob:
                    damaged.append(asset_id)
                    if asset.get("asset_type") in ["power_line", "communication_tower"]:
                        disruptions.append(f"{asset_id}_service")
        
        damage_cost = len(damaged) * 750000
        recovery_cost = damage_cost * 1.8
        
        return {
            "affected_assets": affected,
            "damaged_assets": damaged,
            "disruptions": list(set(disruptions)),
            "damage_cost": damage_cost,
            "recovery_cost": recovery_cost,
            "economic_impact": recovery_cost * 3,
            "time_to_impact": 6,
            "recovery_days": int(len(damaged) / 3) + 45
        }
    
    def _simulate_earthquake(self, intensity: float) -> Dict:
        """Simulate earthquake scenario"""
        magnitude = 7.0 * intensity
        affected = []
        damaged = []
        
        for asset_id, asset in self.county_twin.assets.items():
            seismic_vuln = asset.get("seismic_vulnerability", 0.5)
            if magnitude > 4.0:
                affected.append(asset_id)
                mmi = min(12, magnitude * 1.5)
                damage_prob = seismic_vuln * (mmi / 12) * intensity
                if np.random.random() < damage_prob:
                    damaged.append(asset_id)
        
        return {
            "affected_assets": affected,
            "damaged_assets": damaged,
            "disruptions": [f"{d}_service" for d in damaged[:10]],
            "damage_cost": len(damaged) * 1000000,
            "recovery_cost": len(damaged) * 1500000,
            "economic_impact": len(damaged) * 3000000,
            "time_to_impact": 0.1,
            "recovery_days": int(len(damaged) / 2) + 60
        }
    
    def _simulate_wildfire(self, intensity: float, duration_hours: int) -> Dict:
        """Simulate wildfire scenario"""
        affected = []
        damaged = []
        
        for asset_id, asset in self.county_twin.assets.items():
            fire_risk = asset.get("wildfire_risk", 0.3)
            vegetation = asset.get("vegetation_proximity", 0.5)
            combined_risk = fire_risk * vegetation * intensity
            
            if combined_risk > 0.4:
                affected.append(asset_id)
                if np.random.random() < combined_risk:
                    damaged.append(asset_id)
        
        return {
            "affected_assets": affected,
            "damaged_assets": damaged,
            "disruptions": [],
            "damage_cost": len(damaged) * 400000,
            "recovery_cost": len(damaged) * 600000,
            "economic_impact": len(damaged) * 1200000,
            "time_to_impact": duration_hours * 0.5,
            "recovery_days": int(len(damaged) / 4) + 90
        }
    
    def _simulate_power_outage(self, intensity: float, duration_hours: int) -> Dict:
        """Simulate power outage scenario"""
        power_assets = [
            aid for aid, a in self.county_twin.assets.items()
            if a.get("asset_type") in ["power_station", "substation", "transformer"]
        ]
        
        affected = power_assets.copy()
        disruptions = ["power_grid"]
        
        water_assets = [
            aid for aid, a in self.county_twin.assets.items()
            if a.get("asset_type") in ["water_pump", "water_treatment"]
        ]
        affected.extend(water_assets[:int(len(water_assets) * intensity)])
        disruptions.append("water_system")
        
        return {
            "affected_assets": affected,
            "damaged_assets": power_assets[:int(len(power_assets) * 0.3)],
            "disruptions": disruptions,
            "damage_cost": len(power_assets) * 200000,
            "recovery_cost": len(power_assets) * 100000,
            "economic_impact": duration_hours * 100000,
            "time_to_impact": 0,
            "recovery_days": int(duration_hours / 24) + 1
        }
    
    def _simulate_extreme_heat(self, intensity: float, duration_hours: int) -> Dict:
        """Simulate extreme heat scenario"""
        temp = 110 * intensity
        affected = []
        disruptions = []
        
        if temp > 100:
            power_assets = [
                aid for aid, a in self.county_twin.assets.items()
                if a.get("asset_type") in ["power_line", "transformer"]
            ]
            affected.extend(power_assets)
            disruptions.append("power_grid_strain")
        
        road_assets = [
            aid for aid, a in self.county_twin.assets.items()
            if a.get("asset_type") == "road"
        ]
        affected.extend(road_assets[:int(len(road_assets) * 0.1)])
        
        return {
            "affected_assets": affected,
            "damaged_assets": [],
            "disruptions": disruptions,
            "damage_cost": len(affected) * 50000,
            "recovery_cost": 0,
            "economic_impact": duration_hours * 50000,
            "time_to_impact": duration_hours * 0.3,
            "recovery_days": 1
        }
