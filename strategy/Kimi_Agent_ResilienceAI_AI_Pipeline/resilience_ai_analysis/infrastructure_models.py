"""
ResilienceAI Infrastructure Analysis - Facility Data Models
Pydantic models for facility data with enhanced attributes
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from enum import Enum


class FacilityStatus(str, Enum):
    """Facility operational status"""
    OPERATIONAL = "operational"
    LIMITED = "limited_capacity"
    OVERCAPACITY = "overcapacity"
    CLOSED = "closed"
    DAMAGED = "damaged"
    UNKNOWN = "unknown"


class FacilityType(str, Enum):
    """Types of infrastructure facilities"""
    HOSPITAL = "hospital"
    FIRE_STATION = "fire_station"
    EMS_STATION = "ems_station"
    NURSING_HOME = "nursing_home"
    URGENT_CARE = "urgent_care"
    CLINIC = "clinic"
    PHARMACY = "pharmacy"
    SHELTER = "shelter"
    UTILITY = "utility"
    COMMUNICATIONS = "communications"


class GapSeverity(str, Enum):
    """Severity levels for coverage gaps"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class HospitalCapacity(BaseModel):
    """Hospital capacity metrics"""
    total_beds: int = Field(default=0, description="Total bed capacity")
    available_beds: int = Field(default=0, description="Currently available beds")
    icu_beds: int = Field(default=0, description="ICU bed capacity")
    available_icu_beds: int = Field(default=0, description="Available ICU beds")
    ventilators: int = Field(default=0, description="Total ventilators")
    available_ventilators: int = Field(default=0, description="Available ventilators")
    emergency_capacity: int = Field(default=0, description="Emergency department capacity")
    current_occupancy_rate: float = Field(default=0.0, ge=0, le=1, description="Current occupancy rate")
    staffing_level: float = Field(default=1.0, ge=0, le=1, description="Staffing level (0-1)")


class Facility(BaseModel):
    """Enhanced facility data model"""
    id: str = Field(..., description="Unique facility identifier")
    name: str = Field(..., description="Facility name")
    facility_type: FacilityType = Field(..., description="Type of facility")
    status: FacilityStatus = Field(default=FacilityStatus.UNKNOWN, description="Current status")
    
    # Location
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    address: Optional[str] = Field(default=None, description="Street address")
    county_fips: Optional[str] = Field(default=None, description="County FIPS code")
    state: Optional[str] = Field(default=None, description="State abbreviation")
    
    # Capacity (type-specific)
    capacity: Optional[HospitalCapacity] = Field(default=None, description="Capacity information")
    staff_count: Optional[int] = Field(default=None, description="Number of staff")
    
    # Services
    services: List[str] = Field(default_factory=list, description="Available services")
    trauma_level: Optional[int] = Field(default=None, ge=1, le=5, description="Trauma center level")
    emergency_services: bool = Field(default=False, description="Has emergency services")
    
    # Temporal
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    operating_hours: Optional[str] = Field(default=None, description="Operating hours")
    
    # Metadata
    source: str = Field(default="HIFLD", description="Data source")
    confidence_score: float = Field(default=1.0, ge=0, le=1, description="Data confidence")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CoverageGap(BaseModel):
    """Represents an infrastructure coverage gap"""
    location_lat: float = Field(..., description="Gap location latitude")
    location_lon: float = Field(..., description="Gap location longitude")
    county_fips: str = Field(..., description="County FIPS code")
    gap_type: str = Field(..., description="Type of facility needed")
    severity: GapSeverity = Field(..., description="Gap severity level")
    nearest_facility_distance_km: float = Field(..., description="Distance to nearest facility")
    nearest_facility_id: Optional[str] = Field(default=None, description="Nearest facility ID")
    population_affected: int = Field(..., description="Population in gap area")
    benchmark_distance_km: float = Field(..., description="Benchmark coverage distance")
    recommended_facilities: int = Field(default=1, description="Recommended new facilities")
    priority_score: float = Field(..., description="Remediation priority score")


class FacilityNetwork(BaseModel):
    """Network of facilities with analysis metadata"""
    center_lat: float = Field(..., description="Network center latitude")
    center_lon: float = Field(..., description="Network center longitude")
    radius_km: float = Field(..., description="Network radius in km")
    facilities: List[Facility] = Field(default_factory=list, description="Facilities in network")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    # Network metrics
    total_facilities: int = Field(default=0, description="Total facilities")
    network_density: float = Field(default=0.0, description="Network density")
    connected_components: int = Field(default=0, description="Number of connected components")
    vulnerability_score: float = Field(default=0.0, description="Vulnerability score (0-1)")
    resilience_score: float = Field(default=0.0, description="Resilience score (0-1)")


class NetworkMetrics(BaseModel):
    """Comprehensive network analysis metrics"""
    total_facilities: int = Field(default=0)
    total_connections: int = Field(default=0)
    network_density: float = Field(default=0.0)
    connected_components: int = Field(default=0)
    articulation_points: int = Field(default=0)
    max_betweenness_centrality: float = Field(default=0.0)
    avg_clustering_coefficient: float = Field(default=0.0)
    vulnerability_score: float = Field(default=0.0)
    resilience_score: float = Field(default=0.0)
    
    # Service coverage
    service_coverage: Dict[str, Dict] = Field(default_factory=dict)
    capacity_distribution: Dict[str, float] = Field(default_factory=dict)
    
    # Critical facilities
    critical_facilities: List[Dict] = Field(default_factory=list)


class InvestmentOption(BaseModel):
    """Infrastructure investment option"""
    location_lat: float = Field(..., description="Proposed location latitude")
    location_lon: float = Field(..., description="Proposed location longitude")
    county_fips: str = Field(..., description="County FIPS code")
    facility_type: str = Field(..., description="Type of facility to build")
    estimated_cost: float = Field(..., description="Estimated cost in millions")
    population_served: int = Field(..., description="Population to be served")
    coverage_improvement: float = Field(..., description="Expected coverage improvement")
    risk_reduction: float = Field(..., description="Expected risk reduction")
    priority_score: float = Field(..., description="Investment priority score")


class FacilityStatusUpdate(BaseModel):
    """Real-time facility status update"""
    facility_id: str = Field(..., description="Facility identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    status: str = Field(..., description="Current status")
    available_beds: Optional[int] = Field(default=None, description="Available beds")
    wait_time_minutes: Optional[int] = Field(default=None, description="Current wait time")
    emergency_capacity: Optional[int] = Field(default=None, description="Emergency capacity")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class InfrastructureAnalysisResult(BaseModel):
    """Complete infrastructure analysis result"""
    county_fips: str = Field(..., description="County FIPS code")
    county_name: str = Field(..., description="County name")
    network_analysis: NetworkMetrics = Field(..., description="Network metrics")
    coverage_gaps: List[Dict] = Field(default_factory=list, description="Identified gaps")
    investment_recommendations: List[Dict] = Field(default_factory=list, description="Investment options")
    vulnerability_score: float = Field(..., description="Overall vulnerability")
    resilience_score: float = Field(..., description="Overall resilience")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")


# Utility functions for model operations
def facility_to_geojson(facility: Facility) -> Dict:
    """Convert facility to GeoJSON format"""
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [facility.longitude, facility.latitude]
        },
        "properties": {
            "id": facility.id,
            "name": facility.name,
            "type": facility.facility_type.value,
            "status": facility.status.value,
            "trauma_level": facility.trauma_level,
            "emergency_services": facility.emergency_services
        }
    }


def gap_to_geojson(gap: CoverageGap) -> Dict:
    """Convert coverage gap to GeoJSON format"""
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [gap.location_lon, gap.location_lat]
        },
        "properties": {
            "county_fips": gap.county_fips,
            "gap_type": gap.gap_type,
            "severity": gap.severity.value,
            "nearest_facility_km": gap.nearest_facility_distance_km,
            "population_affected": gap.population_affected,
            "priority_score": gap.priority_score,
            "facilities_needed": gap.recommended_facilities
        }
    }
