"""
Digital Twin Architecture for ResilienceAI
County-Level Implementation Framework
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from enum import Enum
import asyncio
from collections import defaultdict


class TwinLayer(Enum):
    """Digital Twin Architecture Layers"""
    PHYSICAL = "physical"
    DATA = "data"
    DIGITAL = "digital"
    SERVICE = "service"


class AssetType(Enum):
    """County Infrastructure Asset Types"""
    ROAD = "road"
    BRIDGE = "bridge"
    BUILDING = "building"
    WATER_FACILITY = "water_facility"
    POWER_STATION = "power_station"
    COMMUNICATION = "communication"
    EMERGENCY = "emergency"
    HOSPITAL = "hospital"
    SCHOOL = "school"


@dataclass
class GeoLocation:
    """Geographic coordinates for county assets"""
    latitude: float
    longitude: float
    elevation: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "lat": self.latitude,
            "lon": self.longitude,
            "elevation": self.elevation
        }


@dataclass
class CountyAsset:
    """Base class for county infrastructure assets"""
    asset_id: str
    name: str
    asset_type: AssetType
    location: GeoLocation
    county_fips: str
    installed_date: datetime
    lifecycle_stage: str = "operational"
    criticality_score: float = 0.5
    condition_index: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)
    twin_synchronization_rate: int = 60
    sensor_count: int = 0
    simulation_enabled: bool = True
    
    def get_resilience_score(self) -> float:
        """Calculate asset resilience score"""
        return (
            self.condition_index * 0.4 + 
            (1 - self.criticality_score * 0.3) + 
            (self.sensor_count / 10) * 0.3
        )


@dataclass
class DigitalTwinState:
    """Current state of the digital twin"""
    timestamp: datetime
    assets: Dict[str, CountyAsset]
    environmental_conditions: Dict[str, Any]
    simulation_mode: bool = False
    sync_status: str = "synchronized"
    
    def get_asset_count_by_type(self) -> Dict[str, int]:
        """Count assets by type"""
        counts = defaultdict(int)
        for asset in self.assets.values():
            counts[asset.asset_type.value] += 1
        return dict(counts)


class DigitalTwinCore:
    """Core digital twin engine for county modeling"""
    
    def __init__(self, county_fips: str, county_name: str):
        self.county_fips = county_fips
        self.county_name = county_name
        self.assets: Dict[str, CountyAsset] = {}
        self.state_history: List[DigitalTwinState] = []
        self.current_state: Optional[DigitalTwinState] = None
        self.sensors: Dict[str, Any] = {}
        self.simulation_engine = None
        self.sync_interval = 60
        self._running = False
        
    def register_asset(self, asset: CountyAsset) -> bool:
        """Register a new asset in the digital twin"""
        if asset.asset_id in self.assets:
            return False
        self.assets[asset.asset_id] = asset
        return True
    
    def update_asset_state(self, asset_id: str, updates: Dict[str, Any]) -> bool:
        """Update asset state with new sensor data"""
        if asset_id not in self.assets:
            return False
        asset = self.assets[asset_id]
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        asset.last_updated = datetime.now()
        return True
    
    def capture_state(self) -> DigitalTwinState:
        """Capture current digital twin state"""
        state = DigitalTwinState(
            timestamp=datetime.now(),
            assets=self.assets.copy(),
            environmental_conditions=self._get_environmental_conditions()
        )
        self.state_history.append(state)
        self.current_state = state
        if len(self.state_history) > 1000:
            self.state_history = self.state_history[-1000:]
        return state
    
    def _get_environmental_conditions(self) -> Dict[str, Any]:
        """Get current environmental conditions"""
        return {
            "temperature": None,
            "humidity": None,
            "precipitation": None,
            "wind_speed": None,
            "flood_level": None,
            "air_quality": None
        }
    
    async def start_synchronization(self):
        """Start real-time synchronization loop"""
        self._running = True
        while self._running:
            self.capture_state()
            await asyncio.sleep(self.sync_interval)
    
    def stop_synchronization(self):
        """Stop synchronization loop"""
        self._running = False
    
    def get_county_health_score(self) -> Dict[str, Any]:
        """Calculate overall county infrastructure health"""
        if not self.assets:
            return {"score": 0, "status": "no_data"}
        
        total_score = sum(a.get_resilience_score() for a in self.assets.values())
        avg_score = total_score / len(self.assets)
        
        return {
            "score": round(avg_score, 3),
            "total_assets": len(self.assets),
            "status": "healthy" if avg_score > 0.7 else "at_risk" if avg_score > 0.4 else "critical",
            "critical_assets": sum(1 for a in self.assets.values() if a.criticality_score > 0.8),
            "last_updated": datetime.now().isoformat()
        }
