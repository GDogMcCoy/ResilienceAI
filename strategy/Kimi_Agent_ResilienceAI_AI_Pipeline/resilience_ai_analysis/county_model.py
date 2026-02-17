"""
County-Level Digital Twin Model
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np


@dataclass
class InfrastructureNetwork:
    """Network of interconnected infrastructure"""
    network_id: str
    network_type: str
    edges: List[Dict] = field(default_factory=list)
    nodes: List[Dict] = field(default_factory=list)
    
    def add_node(self, node_id: str, location: Tuple[float, float], 
                 attributes: Dict) -> None:
        """Add node to network"""
        self.nodes.append({
            "id": node_id,
            "location": location,
            "attributes": attributes
        })
    
    def add_edge(self, from_node: str, to_node: str, 
                 attributes: Dict) -> None:
        """Add edge between nodes"""
        self.edges.append({
            "from": from_node,
            "to": to_node,
            "attributes": attributes
        })
    
    def calculate_connectivity(self) -> float:
        """Calculate network connectivity score"""
        if len(self.nodes) < 2:
            return 0.0
        return min(1.0, len(self.edges) / (len(self.nodes) - 1))


class CountyDigitalTwin:
    """Complete county digital twin model"""
    
    def __init__(self, county_fips: str, county_name: str, state: str):
        self.county_fips = county_fips
        self.county_name = county_name
        self.state = state
        self.networks: Dict[str, InfrastructureNetwork] = {}
        self.assets: Dict[str, Dict] = {}
        self.demographics: Dict = {}
        self.environmental_baseline: Dict = {}
        self.event_history: List[Dict] = []
        
    def initialize_networks(self):
        """Initialize all infrastructure networks"""
        network_types = ["road", "water", "power", "communication", "emergency"]
        for net_type in network_types:
            self.networks[net_type] = InfrastructureNetwork(
                network_id=f"{self.county_fips}_{net_type}",
                network_type=net_type
            )
    
    def register_asset(self, asset_data: Dict) -> str:
        """Register asset in county twin"""
        asset_id = asset_data.get("asset_id", f"asset_{len(self.assets)}")
        self.assets[asset_id] = {
            **asset_data,
            "registered_at": datetime.now().isoformat(),
            "county_fips": self.county_fips
        }
        network_type = asset_data.get("network_type")
        if network_type and network_type in self.networks:
            self.networks[network_type].add_node(
                asset_id,
                (asset_data["latitude"], asset_data["longitude"]),
                asset_data
            )
        return asset_id
    
    def calculate_resilience_index(self) -> Dict[str, float]:
        """Calculate comprehensive county resilience index"""
        infra_health = self._calculate_infrastructure_health()
        connectivity = self._calculate_network_connectivity()
        emergency_prep = self._calculate_emergency_preparedness()
        env_risk = self._calculate_environmental_risk()
        
        resilience_score = (
            infra_health * 0.40 +
            connectivity * 0.25 +
            emergency_prep * 0.20 +
            (1 - env_risk) * 0.15
        )
        
        return {
            "overall": round(resilience_score, 3),
            "infrastructure_health": round(infra_health, 3),
            "network_connectivity": round(connectivity, 3),
            "emergency_preparedness": round(emergency_prep, 3),
            "environmental_risk": round(env_risk, 3)
        }
    
    def _calculate_infrastructure_health(self) -> float:
        """Calculate infrastructure health score"""
        if not self.assets:
            return 0.0
        health_scores = []
        for asset in self.assets.values():
            condition = asset.get("condition_index", 0.5)
            age_factor = self._calculate_age_factor(asset)
            health_scores.append(condition * age_factor)
        return np.mean(health_scores)
    
    def _calculate_age_factor(self, asset: Dict) -> float:
        """Calculate age degradation factor"""
        installed = asset.get("installed_date")
        if not installed:
            return 1.0
        try:
            install_date = datetime.fromisoformat(installed)
            age_years = (datetime.now() - install_date).days / 365.25
            return max(0.3, 1 - (age_years / 100))
        except:
            return 1.0
    
    def _calculate_network_connectivity(self) -> float:
        """Calculate average network connectivity"""
        if not self.networks:
            return 0.0
        scores = [net.calculate_connectivity() for net in self.networks.values()]
        return np.mean(scores)
    
    def _calculate_emergency_preparedness(self) -> float:
        """Calculate emergency preparedness score"""
        emergency_assets = sum(
            1 for a in self.assets.values() 
            if a.get("asset_type") in ["hospital", "fire_station", "police_station", "shelter"]
        )
        if not self.demographics.get("population"):
            return 0.5
        ratio = emergency_assets / (self.demographics["population"] / 10000)
        return min(1.0, ratio)
    
    def _calculate_environmental_risk(self) -> float:
        """Calculate environmental risk score"""
        risk_factors = []
        flood_risk = self.environmental_baseline.get("flood_risk_score", 0.5)
        risk_factors.append(flood_risk)
        climate_risk = self.environmental_baseline.get("climate_vulnerability", 0.5)
        risk_factors.append(climate_risk)
        disaster_freq = min(1.0, len(self.event_history) / 10)
        risk_factors.append(disaster_freq)
        return np.mean(risk_factors)
    
    def export_to_geojson(self) -> Dict:
        """Export county twin to GeoJSON format"""
        features = []
        for asset_id, asset in self.assets.items():
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [asset.get("longitude"), asset.get("latitude")]
                },
                "properties": {
                    "asset_id": asset_id,
                    **{k: v for k, v in asset.items() if k not in ["latitude", "longitude"]}
                }
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "county_fips": self.county_fips,
            "county_name": self.county_name,
            "features": features
        }
