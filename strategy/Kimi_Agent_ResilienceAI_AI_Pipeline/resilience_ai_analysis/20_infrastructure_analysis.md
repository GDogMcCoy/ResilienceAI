# ResilienceAI Infrastructure Analysis Enhancement Plan

## Executive Summary

This document provides a comprehensive analysis of the current infrastructure capabilities in the ResilienceAI platform and designs advanced enhancements for infrastructure intelligence, network modeling, and facility optimization. The proposed enhancements will transform the current basic HIFLD integration into a sophisticated infrastructure intelligence platform capable of real-time analysis, predictive modeling, and investment optimization.

---

## 1. Current Infrastructure Capabilities Analysis

### 1.1 Existing Infrastructure Components

#### Current Files and Locations

| Component | File Path | Purpose | Status |
|-----------|-----------|---------|--------|
| Network Analysis | `/src/network_analysis.py` | Facility network modeling | Basic |
| Feature Engineering | `/src/feature_engineering.py` | Infrastructure feature creation | Advanced |
| Data Download | `/src/download_data.py` | HIFLD data acquisition | Functional |
| HIFLD Hospitals | `/data/raw/hifld_hospitals.csv` | Hospital facility data | Static |
| HIFLD Fire Stations | `/data/raw/hifld_fire_stations.csv` | Fire station data | Static |
| HIFLD EMS Stations | `/data/raw/hifld_ems_stations.csv` | EMS facility data | Static |
| HIFLD Nursing Homes | `/data/raw/hifld_nursing_homes.csv` | Nursing home data | Static |

### 1.2 Current Network Analysis Capabilities

```python
# Current InfrastructureNetwork class capabilities
class InfrastructureNetwork:
    """
    Current capabilities:
    - Load facility data from HIFLD CSV files
    - Build facility networks within radius
    - Calculate network metrics (density, components)
    - Identify critical facilities via betweenness centrality
    - Find articulation points (single points of failure)
    - Simulate cascade failures
    - Basic vulnerability scoring
    """
```

#### Current Metrics Calculated:

| Metric | Description | Formula |
|--------|-------------|---------|
| Network Density | Edge connectivity | `nx.density(G)` |
| Connected Components | Network fragmentation | `nx.number_connected_components(G)` |
| Betweenness Centrality | Bottleneck identification | `nx.betweenness_centrality(G)` |
| Articulation Points | Single points of failure | `nx.articulation_points(G)` |
| Clustering Coefficient | Local connectivity | `nx.average_clustering(G)` |
| Vulnerability Score | Composite resilience metric | Weighted combination |

### 1.3 Current Limitations

1. **Static Data**: No real-time facility status updates
2. **Limited Facility Types**: Only 4 HIFLD facility types
3. **No Capacity Analysis**: Missing bed count, staffing, utilization
4. **Basic Distance Metrics**: Simple haversine distance only
5. **No Accessibility Scoring**: Missing travel time, road network
6. **Limited Gap Analysis**: No systematic gap identification
7. **No Investment Optimization**: Missing ROI calculations for infrastructure
8. **No Redundancy Scoring**: Limited backup facility analysis

---

## 2. Proposed Infrastructure Intelligence Platform

### 2.1 Platform Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE INTELLIGENCE PLATFORM                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Data Layer   │  │ Analysis     │  │ Intelligence │  │ Application │ │
│  │              │  │ Engine       │  │ Layer        │  │ Layer       │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├─────────────┤ │
│  │ HIFLD API    │  │ Network      │  │ Predictive   │  │ Dashboard   │ │
│  │ CMS Data     │  │ Analysis     │  │ Models       │  │ API         │ │
│  │ Real-time    │  │ Spatial      │  │ Optimization │  │ Alerts      │ │
│  │ Feeds        │  │ Statistics   │  │ Scenarios    │  │ Reports     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Enhanced File Structure

```
/src/
├── infrastructure/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── facility_loader.py          # Enhanced HIFLD data loading
│   │   ├── capacity_analyzer.py        # Hospital/facility capacity analysis
│   │   └── status_tracker.py           # Real-time facility status
│   ├── network/
│   │   ├── __init__.py
│   │   ├── advanced_network.py         # Extended network analysis
│   │   ├── redundancy_scorer.py        # Infrastructure redundancy metrics
│   │   ├── accessibility_model.py      # Travel time & accessibility
│   │   └── cascade_simulator.py        # Enhanced cascade modeling
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── gap_identifier.py           # Systematic gap identification
│   │   ├── coverage_optimizer.py       # Coverage optimization algorithms
│   │   ├── investment_optimizer.py     # Infrastructure investment ROI
│   │   └── vulnerability_assessor.py   # Comprehensive vulnerability scoring
│   ├── models/
│   │   ├── __init__.py
│   │   ├── facility_models.py          # Pydantic facility data models
│   │   ├── network_models.py           # Network graph models
│   │   └── scoring_models.py           # Scoring/weighting models
│   └── utils/
│       ├── __init__.py
│       ├── geo_utils.py                # Geographic utilities
│       ├── routing_engine.py           # Road network routing
│       └── data_sync.py                # Real-time data synchronization
├── agents/
│   └── infrastructure_agent.py         # Infrastructure analysis agent
└── pipeline/
    └── infrastructure_pipeline.py      # End-to-end pipeline

/data/
├── infrastructure/
│   ├── cache/
│   │   ├── facility_status/            # Real-time status cache
│   │   ├── network_graphs/             # Serialized network graphs
│   │   └── routing_cache/              # Route calculation cache
│   ├── processed/
│   │   ├── facility_capacity/          # Capacity analysis results
│   │   ├── accessibility_scores/       # Accessibility metrics
│   │   └── gap_analysis/               # Gap identification results
│   └── reference/
│       ├── facility_types.json         # Facility type definitions
│       ├── capacity_benchmarks.json    # Capacity benchmarks
│       └── investment_models.json      # Investment ROI models

/models/
├── infrastructure/
│   ├── capacity_predictor.pkl          # Capacity prediction model
│   ├── vulnerability_classifier.pkl    # Vulnerability classification
│   └── demand_forecaster.pkl           # Demand forecasting model
```

---

## 3. Core Infrastructure Components

### 3.1 Enhanced Facility Data Models

```python
# /src/infrastructure/models/facility_models.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from enum import Enum

class FacilityStatus(str, Enum):
    OPERATIONAL = "operational"
    LIMITED = "limited_capacity"
    OVERCAPACITY = "overcapacity"
    CLOSED = "closed"
    DAMAGED = "damaged"
    UNKNOWN = "unknown"

class FacilityType(str, Enum):
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

class HospitalCapacity(BaseModel):
    """Hospital capacity metrics"""
    total_beds: int
    available_beds: int
    icu_beds: int
    available_icu_beds: int
    ventilators: int
    available_ventilators: int
    emergency_capacity: int
    current_occupancy_rate: float
    staffing_level: float  # 0-1 scale
    
class Facility(BaseModel):
    """Enhanced facility data model"""
    id: str
    name: str
    facility_type: FacilityType
    status: FacilityStatus = FacilityStatus.UNKNOWN
    
    # Location
    latitude: float
    longitude: float
    address: Optional[str] = None
    county_fips: Optional[str] = None
    state: Optional[str] = None
    
    # Capacity (type-specific)
    capacity: Optional[HospitalCapacity] = None
    staff_count: Optional[int] = None
    
    # Services
    services: List[str] = Field(default_factory=list)
    trauma_level: Optional[int] = None  # For hospitals
    emergency_services: bool = False
    
    # Temporal
    last_updated: datetime = Field(default_factory=datetime.now)
    operating_hours: Optional[str] = None
    
    # Metadata
    source: str = "HIFLD"
    confidence_score: float = 1.0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FacilityNetwork(BaseModel):
    """Network of facilities with analysis metadata"""
    center_lat: float
    center_lon: float
    radius_km: float
    facilities: List[Facility]
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Network metrics
    total_facilities: int = 0
    network_density: float = 0.0
    connected_components: int = 0
    vulnerability_score: float = 0.0
```

### 3.2 Advanced Network Analysis Engine

```python
# /src/infrastructure/network/advanced_network.py

import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy.spatial import cKDTree
import osmnx as ox
from shapely.geometry import Point, Polygon

from ..models.facility_models import Facility, FacilityNetwork, FacilityType
from ..utils.geo_utils import haversine_km, travel_time_matrix

class AdvancedInfrastructureNetwork:
    """
    Advanced infrastructure network analysis with:
    - Multi-modal routing (road network, straight-line)
    - Dynamic capacity weighting
    - Real-time status integration
    - Multi-criteria vulnerability assessment
    """
    
    def __init__(self, use_road_network: bool = True):
        self.facilities: Dict[str, Facility] = {}
        self.graph: Optional[nx.Graph] = None
        self.road_graph: Optional[nx.MultiDiGraph] = None
        self.use_road_network = use_road_network
        self.kdtree: Optional[cKDTree] = None
        
    def load_facilities(self, facilities_df: pd.DataFrame, 
                        facility_type: FacilityType) -> None:
        """Load facilities from DataFrame with enhanced attributes"""
        for _, row in facilities_df.iterrows():
            facility = self._create_facility(row, facility_type)
            self.facilities[facility.id] = facility
            
        self._build_spatial_index()
        
    def _create_facility(self, row: pd.Series, 
                         facility_type: FacilityType) -> Facility:
        """Create Facility object from DataFrame row"""
        # Extract capacity data if available
        capacity = None
        if facility_type == FacilityType.HOSPITAL:
            capacity = self._extract_hospital_capacity(row)
            
        return Facility(
            id=str(row.get('ID', row.get('OBJECTID', row.name))),
            name=row.get('NAME', row.get('name', 'Unknown')),
            facility_type=facility_type,
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            address=row.get('ADDRESS'),
            county_fips=str(row.get('COUNTYFIPS', row.get('county_fips'))),
            state=row.get('STATE', row.get('state')),
            capacity=capacity,
            trauma_level=row.get('TRAUMA'),
            emergency_services=row.get('EMERGENCY', False),
            services=self._parse_services(row)
        )
    
    def _extract_hospital_capacity(self, row: pd.Series) -> Optional[HospitalCapacity]:
        """Extract hospital capacity information"""
        try:
            total_beds = int(row.get('BEDS', 0))
            if total_beds == 0:
                return None
                
            occupancy = float(row.get('OCCUPANCY_RATE', 0.7))
            
            return HospitalCapacity(
                total_beds=total_beds,
                available_beds=int(total_beds * (1 - occupancy)),
                icu_beds=int(row.get('ICU_BEDS', total_beds * 0.1)),
                available_icu_beds=int(row.get('ICU_BEDS', total_beds * 0.1) * 0.3),
                ventilators=int(row.get('VENTILATORS', total_beds * 0.05)),
                available_ventilators=int(row.get('VENTILATORS', total_beds * 0.05) * 0.5),
                emergency_capacity=int(row.get('EMERGENCY_CAPACITY', total_beds * 0.2)),
                current_occupancy_rate=occupancy,
                staffing_level=float(row.get('STAFFING_LEVEL', 0.8))
            )
        except (ValueError, TypeError):
            return None
    
    def build_network(self, center_lat: float, center_lon: float,
                      radius_km: float = 80,
                      connectivity_km: float = 50) -> nx.Graph:
        """
        Build enhanced facility network with:
        - Multi-type facility integration
        - Capacity-weighted edges
        - Status-aware node weights
        """
        # Filter facilities by radius
        nearby_facilities = self._get_facilities_in_radius(
            center_lat, center_lon, radius_km
        )
        
        # Create graph
        G = nx.Graph()
        
        # Add nodes with enhanced attributes
        for facility in nearby_facilities:
            node_weight = self._calculate_node_weight(facility)
            G.add_node(
                facility.id,
                facility=facility,
                weight=node_weight,
                lat=facility.latitude,
                lon=facility.longitude,
                facility_type=facility.facility_type.value,
                status=facility.status.value
            )
        
        # Add edges with capacity and distance weighting
        self._add_weighted_edges(G, connectivity_km)
        
        self.graph = G
        return G
    
    def _calculate_node_weight(self, facility: Facility) -> float:
        """
        Calculate node importance weight based on:
        - Facility capacity
        - Service level
        - Current status
        """
        base_weight = 1.0
        
        # Capacity weighting
        if facility.capacity:
            base_weight *= np.log1p(facility.capacity.total_beds) / 5
            
        # Trauma level weighting for hospitals
        if facility.trauma_level:
            base_weight *= (4 - facility.trauma_level + 1) / 2
            
        # Status penalty
        status_multiplier = {
            'operational': 1.0,
            'limited_capacity': 0.7,
            'overcapacity': 0.5,
            'closed': 0.0,
            'damaged': 0.0,
            'unknown': 0.5
        }
        base_weight *= status_multiplier.get(facility.status.value, 0.5)
        
        return base_weight
    
    def _add_weighted_edges(self, G: nx.Graph, max_distance_km: float) -> None:
        """Add edges with distance and capacity weighting"""
        nodes = list(G.nodes(data=True))
        
        for i, (node_i, data_i) in enumerate(nodes):
            for j, (node_j, data_j) in enumerate(nodes[i+1:], i+1):
                dist_km = haversine_km(
                    data_i['lat'], data_i['lon'],
                    data_j['lat'], data_j['lon']
                )
                
                if dist_km <= max_distance_km:
                    # Weight combines distance and node importance
                    weight = dist_km / (data_i['weight'] * data_j['weight'] + 0.1)
                    G.add_edge(node_i, node_j, weight=weight, distance_km=dist_km)
    
    def calculate_advanced_metrics(self) -> Dict:
        """
        Calculate comprehensive network metrics including:
        - Traditional graph metrics
        - Capacity-weighted centrality
        - Service coverage metrics
        - Resilience indicators
        """
        if self.graph is None or self.graph.number_of_nodes() < 2:
            return self._empty_metrics()
        
        G = self.graph
        
        metrics = {
            # Basic metrics
            'total_facilities': G.number_of_nodes(),
            'total_connections': G.number_of_edges(),
            'network_density': nx.density(G),
            'connected_components': nx.number_connected_components(G),
            
            # Centrality metrics
            'betweenness_centrality': nx.betweenness_centrality(G, weight='weight'),
            'closeness_centrality': nx.closeness_centrality(G, distance='weight'),
            'eigenvector_centrality': nx.eigenvector_centrality(G, max_iter=1000),
            
            # Capacity-weighted centrality
            'capacity_centrality': self._capacity_weighted_centrality(G),
            
            # Resilience metrics
            'articulation_points': list(nx.articulation_points(G)),
            'avg_clustering': nx.average_clustering(G),
            'node_connectivity': nx.node_connectivity(G) if G.number_of_nodes() > 1 else 0,
            
            # Service-specific metrics
            'service_coverage': self._calculate_service_coverage(G),
            'capacity_distribution': self._analyze_capacity_distribution(G),
        }
        
        # Composite vulnerability score
        metrics['vulnerability_score'] = self._calculate_vulnerability_score(metrics)
        metrics['resilience_score'] = 1 - metrics['vulnerability_score']
        
        return metrics
    
    def _capacity_weighted_centrality(self, G: nx.Graph) -> Dict[str, float]:
        """Calculate centrality weighted by facility capacity"""
        centrality = {}
        for node in G.nodes():
            facility = G.nodes[node].get('facility')
            if facility and facility.capacity:
                base_centrality = nx.degree_centrality(G)[node]
                capacity_factor = np.log1p(facility.capacity.total_beds) / 10
                centrality[node] = base_centrality * capacity_factor
            else:
                centrality[node] = nx.degree_centrality(G)[node]
        return centrality
    
    def _calculate_service_coverage(self, G: nx.Graph) -> Dict[str, Dict]:
        """Analyze coverage by facility type"""
        coverage = {}
        
        for facility_type in FacilityType:
            nodes_of_type = [
                n for n, d in G.nodes(data=True)
                if d.get('facility_type') == facility_type.value
            ]
            
            if nodes_of_type:
                subgraph = G.subgraph(nodes_of_type)
                coverage[facility_type.value] = {
                    'count': len(nodes_of_type),
                    'connectivity': nx.node_connectivity(subgraph) if len(nodes_of_type) > 1 else 0,
                    'avg_degree': np.mean([d for n, d in subgraph.degree()]) if subgraph.number_of_nodes() > 0 else 0
                }
        
        return coverage
    
    def _calculate_vulnerability_score(self, metrics: Dict) -> float:
        """
        Calculate composite vulnerability score (0=resilient, 1=vulnerable)
        """
        scores = []
        
        # Network density (lower = more vulnerable)
        scores.append(0.25 * (1 - metrics['network_density']))
        
        # Fragmentation (more components = more vulnerable)
        n_facilities = metrics['total_facilities']
        if n_facilities > 0:
            scores.append(0.20 * min(metrics['connected_components'] / max(n_facilities / 10, 1), 1))
        
        # Critical nodes (articulation points)
        if n_facilities > 0:
            scores.append(0.20 * len(metrics['articulation_points']) / n_facilities)
        
        # Clustering (lower = less resilient)
        scores.append(0.15 * (1 - metrics['avg_clustering']))
        
        # Betweenness concentration (high max = vulnerable to single point failure)
        if metrics['betweenness_centrality']:
            max_bc = max(metrics['betweenness_centrality'].values())
            scores.append(0.20 * max_bc)
        
        return min(sum(scores), 1.0)
```

---

## 4. Infrastructure Gap Analysis

### 4.1 Gap Identification Algorithm

```python
# /src/infrastructure/analysis/gap_identifier.py

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class GapSeverity(str, Enum):
    CRITICAL = "critical"      # No coverage within threshold
    HIGH = "high"              # Coverage below 50% of benchmark
    MEDIUM = "medium"          # Coverage below benchmark
    LOW = "low"                # Coverage slightly below benchmark

@dataclass
class CoverageGap:
    """Represents an infrastructure coverage gap"""
    location_lat: float
    location_lon: float
    county_fips: str
    gap_type: str  # facility type
    severity: GapSeverity
    nearest_facility_distance_km: float
    nearest_facility_id: Optional[str]
    population_affected: int
    benchmark_distance_km: float
    recommended_facilities: int
    priority_score: float

class GapIdentifier:
    """
    Systematic infrastructure gap identification using:
    - Population-weighted coverage analysis
    - Benchmark comparison
    - Multi-criteria prioritization
    """
    
    # Coverage benchmarks by facility type (km)
    DEFAULT_BENCHMARKS = {
        'hospital': 25,        # 25km for hospitals
        'fire_station': 15,    # 15km for fire stations
        'ems_station': 20,     # 20km for EMS
        'nursing_home': 30,    # 30km for nursing homes
        'urgent_care': 15,     # 15km for urgent care
        'clinic': 20,          # 20km for clinics
        'pharmacy': 10,        # 10km for pharmacies
        'shelter': 25,         # 25km for emergency shelters
    }
    
    def __init__(self, benchmarks: Optional[Dict[str, float]] = None):
        self.benchmarks = benchmarks or self.DEFAULT_BENCHMARKS
        self.facility_trees: Dict[str, cKDTree] = {}
        self.facility_data: Dict[str, pd.DataFrame] = {}
        
    def add_facility_type(self, facility_type: str, 
                          facilities_df: pd.DataFrame) -> None:
        """Add facility type for gap analysis"""
        clean_df = facilities_df.dropna(subset=['latitude', 'longitude']).copy()
        
        if len(clean_df) > 0:
            coords = np.radians(clean_df[['latitude', 'longitude']].values)
            self.facility_trees[facility_type] = cKDTree(coords)
            self.facility_data[facility_type] = clean_df
    
    def identify_gaps(self, county_df: pd.DataFrame,
                      population_col: str = 'population',
                      min_population: int = 1000) -> List[CoverageGap]:
        """
        Identify coverage gaps for all facility types
        """
        gaps = []
        
        for _, county in county_df.iterrows():
            if county.get(population_col, 0) < min_population:
                continue
                
            for facility_type, benchmark_km in self.benchmarks.items():
                if facility_type not in self.facility_trees:
                    continue
                    
                gap = self._analyze_coverage_gap(
                    county, facility_type, benchmark_km, population_col
                )
                
                if gap and gap.severity in [GapSeverity.CRITICAL, GapSeverity.HIGH]:
                    gaps.append(gap)
        
        # Sort by priority score
        gaps.sort(key=lambda g: g.priority_score, reverse=True)
        return gaps
    
    def _analyze_coverage_gap(self, county: pd.Series,
                              facility_type: str,
                              benchmark_km: float,
                              population_col: str) -> Optional[CoverageGap]:
        """Analyze coverage gap for a specific location and facility type"""
        
        lat, lon = county['latitude'], county['longitude']
        county_coords = np.radians([[lat, lon]])
        
        tree = self.facility_trees[facility_type]
        
        # Find nearest facility
        dist_rad, idx = tree.query(county_coords, k=1)
        dist_km = dist_rad[0][0] * 6371.0
        
        # Get nearest facility ID
        nearest_id = None
        if idx[0][0] < len(self.facility_data[facility_type]):
            nearest_id = str(self.facility_data[facility_type].iloc[idx[0][0]].get('ID', idx[0][0]))
        
        # Determine severity
        severity = self._determine_severity(dist_km, benchmark_km)
        
        # Calculate priority score
        population = county.get(population_col, 0)
        priority_score = self._calculate_priority_score(
            dist_km, benchmark_km, population, severity
        )
        
        # Recommend number of new facilities
        recommended = self._recommend_facilities(dist_km, benchmark_km, population)
        
        return CoverageGap(
            location_lat=lat,
            location_lon=lon,
            county_fips=str(county.get('fips', '')),
            gap_type=facility_type,
            severity=severity,
            nearest_facility_distance_km=round(dist_km, 2),
            nearest_facility_id=nearest_id,
            population_affected=int(population),
            benchmark_distance_km=benchmark_km,
            recommended_facilities=recommended,
            priority_score=round(priority_score, 4)
        )
    
    def _determine_severity(self, distance_km: float, 
                           benchmark_km: float) -> GapSeverity:
        """Determine gap severity based on distance vs benchmark"""
        ratio = distance_km / benchmark_km if benchmark_km > 0 else float('inf')
        
        if distance_km == float('inf') or ratio > 3:
            return GapSeverity.CRITICAL
        elif ratio > 2:
            return GapSeverity.HIGH
        elif ratio > 1.5:
            return GapSeverity.MEDIUM
        elif ratio > 1:
            return GapSeverity.LOW
        else:
            return None  # No gap
    
    def _calculate_priority_score(self, distance_km: float,
                                  benchmark_km: float,
                                  population: int,
                                  severity: GapSeverity) -> float:
        """
        Calculate priority score for gap remediation
        Higher score = higher priority
        """
        # Distance factor (further = higher priority)
        distance_factor = min(distance_km / benchmark_km, 5) if benchmark_km > 0 else 5
        
        # Population factor (more people = higher priority)
        population_factor = np.log1p(population) / 10
        
        # Severity multiplier
        severity_multipliers = {
            GapSeverity.CRITICAL: 2.0,
            GapSeverity.HIGH: 1.5,
            GapSeverity.MEDIUM: 1.2,
            GapSeverity.LOW: 1.0
        }
        severity_mult = severity_multipliers.get(severity, 1.0)
        
        return distance_factor * population_factor * severity_mult
    
    def _recommend_facilities(self, distance_km: float,
                             benchmark_km: float,
                             population: int) -> int:
        """Recommend number of new facilities needed"""
        if distance_km <= benchmark_km:
            return 0
        
        # Base recommendation on coverage area
        coverage_area = np.pi * (benchmark_km ** 2)
        uncovered_area = np.pi * (distance_km ** 2) - coverage_area
        
        # Population density factor
        facilities_needed = max(1, int(uncovered_area / (coverage_area * 2)))
        
        # Cap based on population
        max_facilities = max(1, int(population / 10000))
        
        return min(facilities_needed, max_facilities)
    
    def generate_gap_report(self, gaps: List[CoverageGap]) -> pd.DataFrame:
        """Generate structured gap report"""
        if not gaps:
            return pd.DataFrame()
        
        report_data = []
        for gap in gaps:
            report_data.append({
                'county_fips': gap.county_fips,
                'latitude': gap.location_lat,
                'longitude': gap.location_lon,
                'facility_type': gap.gap_type,
                'severity': gap.severity.value,
                'nearest_facility_km': gap.nearest_facility_distance_km,
                'population_affected': gap.population_affected,
                'benchmark_km': gap.benchmark_distance_km,
                'facilities_needed': gap.recommended_facilities,
                'priority_score': gap.priority_score
            })
        
        return pd.DataFrame(report_data)
```

---

## 5. Infrastructure Investment Optimization

### 5.1 ROI-Based Investment Optimizer

```python
# /src/infrastructure/analysis/investment_optimizer.py

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.optimize import minimize

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
    
    # Estimated costs by facility type (in millions)
    FACILITY_COSTS = {
        'hospital': 50.0,
        'fire_station': 2.5,
        'ems_station': 1.5,
        'nursing_home': 10.0,
        'urgent_care': 3.0,
        'clinic': 1.0,
        'pharmacy': 0.5,
        'shelter': 1.0,
    }
    
    # Annual operating costs as % of capital
    OPERATING_COST_PCT = {
        'hospital': 0.15,
        'fire_station': 0.10,
        'ems_station': 0.12,
        'nursing_home': 0.20,
        'urgent_care': 0.15,
        'clinic': 0.12,
        'pharmacy': 0.10,
        'shelter': 0.08,
    }
    
    def __init__(self, budget_millions: float = 100.0,
                 time_horizon_years: int = 10):
        self.budget = budget_millions
        self.time_horizon = time_horizon_years
        self.investment_options: List[InvestmentOption] = []
        
    def add_investment_option(self, gap: 'CoverageGap',
                              facility_costs: Optional[Dict] = None) -> None:
        """Convert coverage gap to investment option"""
        costs = facility_costs or self.FACILITY_COSTS
        
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
    
    def _calculate_coverage_improvement(self, gap: 'CoverageGap') -> float:
        """Calculate coverage improvement from investment"""
        # Improvement is inverse of current distance vs benchmark
        if gap.nearest_facility_distance_km <= gap.benchmark_distance_km:
            return 0.0
        
        improvement = (gap.nearest_facility_distance_km - gap.benchmark_distance_km) / gap.nearest_facility_distance_km
        return min(improvement, 1.0)
    
    def _calculate_risk_reduction(self, gap: 'CoverageGap') -> float:
        """Calculate disaster risk reduction from investment"""
        # Higher population + greater distance = higher risk reduction potential
        population_factor = np.log1p(gap.population_affected) / 15
        distance_factor = gap.nearest_facility_distance_km / 100
        
        return min(population_factor * distance_factor, 1.0)
    
    def optimize_investments(self, 
                            objective: str = 'coverage',
                            constraints: Optional[Dict] = None) -> Dict:
        """
        Optimize infrastructure investments
        
        Objectives:
        - 'coverage': Maximize population coverage
        - 'risk': Maximize risk reduction
        - 'roi': Maximize return on investment
        - 'balanced': Multi-objective optimization
        """
        if not self.investment_options:
            return {'error': 'No investment options available'}
        
        # Filter options within budget
        affordable = [opt for opt in self.investment_options 
                     if opt.estimated_cost <= self.budget]
        
        if not affordable:
            return {'error': 'No affordable investment options'}
        
        # Sort by objective
        if objective == 'coverage':
            affordable.sort(key=lambda x: x.coverage_improvement * x.population_served, 
                          reverse=True)
        elif objective == 'risk':
            affordable.sort(key=lambda x: x.risk_reduction, reverse=True)
        elif objective == 'roi':
            affordable.sort(key=lambda x: (x.coverage_improvement * x.population_served) / 
                                          (x.estimated_cost + 0.01), reverse=True)
        elif objective == 'balanced':
            affordable.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Greedy selection within budget
        selected = []
        remaining_budget = self.budget
        total_population = 0
        total_coverage_improvement = 0
        total_risk_reduction = 0
        
        for option in affordable:
            if option.estimated_cost <= remaining_budget:
                selected.append(option)
                remaining_budget -= option.estimated_cost
                total_population += option.population_served
                total_coverage_improvement += option.coverage_improvement
                total_risk_reduction += option.risk_reduction
        
        # Calculate ROI metrics
        total_investment = self.budget - remaining_budget
        roi_metrics = self._calculate_roi_metrics(selected, total_investment)
        
        return {
            'objective': objective,
            'total_budget': self.budget,
            'total_investment': total_investment,
            'remaining_budget': remaining_budget,
            'investments_count': len(selected),
            'population_served': total_population,
            'coverage_improvement': total_coverage_improvement,
            'risk_reduction': total_risk_reduction,
            'roi_metrics': roi_metrics,
            'recommended_investments': [
                {
                    'county_fips': opt.county_fips,
                    'facility_type': opt.facility_type,
                    'cost_millions': opt.estimated_cost,
                    'population_served': opt.population_served,
                    'coverage_improvement': opt.coverage_improvement,
                    'risk_reduction': opt.risk_reduction,
                    'location': (opt.location_lat, opt.location_lon)
                }
                for opt in selected
            ]
        }
    
    def _calculate_roi_metrics(self, investments: List[InvestmentOption],
                               total_cost: float) -> Dict:
        """Calculate comprehensive ROI metrics"""
        if not investments or total_cost == 0:
            return {}
        
        # People served per million
        total_population = sum(opt.population_served for opt in investments)
        people_per_million = total_population / total_cost
        
        # Coverage improvement per million
        total_coverage = sum(opt.coverage_improvement for opt in investments)
        coverage_per_million = total_coverage / total_cost
        
        # Risk reduction per million
        total_risk = sum(opt.risk_reduction for opt in investments)
        risk_per_million = total_risk / total_cost
        
        # NPV calculation (simplified)
        annual_benefit = total_population * 0.001  # $1000 benefit per person/year
        operating_costs = sum(
            opt.estimated_cost * self.OPERATING_COST_PCT.get(opt.facility_type, 0.1)
            for opt in investments
        )
        
        # NPV = -Initial + Sum(Benefits - Costs) / (1 + r)^t
        discount_rate = 0.05
        npv = -total_cost
        for year in range(1, self.time_horizon + 1):
            npv += (annual_benefit - operating_costs) / ((1 + discount_rate) ** year)
        
        return {
            'people_served_per_million': round(people_per_million, 2),
            'coverage_improvement_per_million': round(coverage_per_million, 4),
            'risk_reduction_per_million': round(risk_per_million, 4),
            'net_present_value_millions': round(npv, 2),
            'benefit_cost_ratio': round(npv / total_cost + 1, 2) if total_cost > 0 else 0,
            'payback_period_years': round(total_cost / (annual_benefit - operating_costs), 2) 
                                   if annual_benefit > operating_costs else float('inf')
        }
```

---

## 6. Real-Time Facility Status Integration

### 6.1 Facility Status Tracker

```python
# /src/infrastructure/core/status_tracker.py

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from dataclasses import dataclass, asdict

@dataclass
class FacilityStatusUpdate:
    """Real-time facility status update"""
    facility_id: str
    timestamp: datetime
    status: str
    available_beds: Optional[int] = None
    wait_time_minutes: Optional[int] = None
    emergency_capacity: Optional[int] = None
    notes: Optional[str] = None

class FacilityStatusTracker:
    """
    Track real-time facility status from multiple sources:
    - HIFLD updates
    - State health department APIs
    - EMS dispatch systems
    - Manual updates
    """
    
    def __init__(self, cache_duration_minutes: int = 15):
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.status_cache: Dict[str, FacilityStatusUpdate] = {}
        self.last_update: Dict[str, datetime] = {}
        self.data_sources: List[Dict] = []
        
    def register_data_source(self, name: str, url: str, 
                            api_key: Optional[str] = None,
                            update_interval: int = 300) -> None:
        """Register a new data source for facility status"""
        self.data_sources.append({
            'name': name,
            'url': url,
            'api_key': api_key,
            'update_interval': update_interval,
            'last_fetch': None
        })
    
    async def fetch_all_statuses(self) -> Dict[str, FacilityStatusUpdate]:
        """Fetch status updates from all registered sources"""
        tasks = []
        for source in self.data_sources:
            tasks.append(self._fetch_from_source(source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results
        all_updates = {}
        for result in results:
            if isinstance(result, dict):
                all_updates.update(result)
        
        # Update cache
        self.status_cache.update(all_updates)
        
        return all_updates
    
    async def _fetch_from_source(self, source: Dict) -> Dict[str, FacilityStatusUpdate]:
        """Fetch status from a single data source"""
        try:
            headers = {}
            if source.get('api_key'):
                headers['Authorization'] = f"Bearer {source['api_key']}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(source['url'], headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_status_data(data, source['name'])
        except Exception as e:
            print(f"Error fetching from {source['name']}: {e}")
        
        return {}
    
    def _parse_status_data(self, data: Dict, source_name: str) -> Dict[str, FacilityStatusUpdate]:
        """Parse status data from various formats"""
        updates = {}
        
        # Handle different API formats
        if 'facilities' in data:
            facilities = data['facilities']
        elif 'data' in data:
            facilities = data['data']
        else:
            facilities = [data]
        
        for facility in facilities:
            facility_id = str(facility.get('id', facility.get('facility_id', '')))
            if not facility_id:
                continue
            
            update = FacilityStatusUpdate(
                facility_id=facility_id,
                timestamp=datetime.now(),
                status=facility.get('status', 'unknown'),
                available_beds=facility.get('available_beds'),
                wait_time_minutes=facility.get('wait_time'),
                emergency_capacity=facility.get('emergency_capacity'),
                notes=facility.get('notes', f"Source: {source_name}")
            )
            
            updates[facility_id] = update
        
        return updates
    
    def get_facility_status(self, facility_id: str) -> Optional[FacilityStatusUpdate]:
        """Get cached status for a facility"""
        if facility_id in self.status_cache:
            update = self.status_cache[facility_id]
            # Check cache freshness
            if datetime.now() - update.timestamp < self.cache_duration:
                return update
        return None
    
    def get_overloaded_facilities(self) -> List[str]:
        """Get list of facilities that are at or over capacity"""
        overloaded = []
        for facility_id, status in self.status_cache.items():
            if status.status in ['overcapacity', 'critical', 'divert']:
                overloaded.append(facility_id)
        return overloaded
    
    def export_status_report(self) -> pd.DataFrame:
        """Export current status as DataFrame"""
        data = []
        for facility_id, status in self.status_cache.items():
            data.append({
                'facility_id': facility_id,
                'timestamp': status.timestamp,
                'status': status.status,
                'available_beds': status.available_beds,
                'wait_time_minutes': status.wait_time_minutes,
                'emergency_capacity': status.emergency_capacity,
                'notes': status.notes
            })
        
        return pd.DataFrame(data)
```

---

## 7. Infrastructure Agent Integration

### 7.1 Infrastructure Analysis Agent

```python
# /src/agents/infrastructure_agent.py

from typing import Dict, List, Any, Optional
import pandas as pd
import json

class InfrastructureAnalysisAgent:
    """
    Agent for comprehensive infrastructure analysis
    Integrates with ResilienceAI agent orchestration
    """
    
    def __init__(self, network_analyzer, gap_identifier, 
                 investment_optimizer, status_tracker):
        self.network_analyzer = network_analyzer
        self.gap_identifier = gap_identifier
        self.investment_optimizer = investment_optimizer
        self.status_tracker = status_tracker
        
    def analyze_county_infrastructure(self, county_fips: str,
                                      county_data: pd.DataFrame) -> Dict:
        """Comprehensive infrastructure analysis for a county"""
        
        # Get county info
        county = county_data[county_data['fips'] == county_fips]
        if county.empty:
            return {'error': f'County {county_fips} not found'}
        
        county_row = county.iloc[0]
        
        # Network analysis
        network_result = self.network_analyzer.analyze_network(
            county_row['latitude'],
            county_row['longitude'],
            radius_km=50
        )
        
        # Gap analysis
        gaps = self.gap_identifier.identify_gaps(county)
        
        # Investment recommendations
        for gap in gaps:
            self.investment_optimizer.add_investment_option(gap)
        
        investment_plan = self.investment_optimizer.optimize_investments(
            objective='balanced'
        )
        
        # Compile results
        return {
            'county_fips': county_fips,
            'county_name': county_row.get('county_name', 'Unknown'),
            'network_analysis': network_result,
            'coverage_gaps': [
                {
                    'type': gap.gap_type,
                    'severity': gap.severity.value,
                    'distance_km': gap.nearest_facility_distance_km,
                    'population_affected': gap.population_affected
                }
                for gap in gaps[:5]  # Top 5 gaps
            ],
            'investment_recommendations': investment_plan.get('recommended_investments', []),
            'vulnerability_score': network_result.get('vulnerability_score', 1.0),
            'resilience_score': network_result.get('resilience_score', 0.0)
        }
    
    def generate_infrastructure_briefing(self, state: str,
                                         analysis_results: List[Dict]) -> str:
        """Generate natural language briefing on infrastructure status"""
        
        # Aggregate metrics
        total_counties = len(analysis_results)
        avg_vulnerability = sum(r['vulnerability_score'] for r in analysis_results) / total_counties
        total_gaps = sum(len(r['coverage_gaps']) for r in analysis_results)
        
        # Critical counties
        critical_counties = [r for r in analysis_results if r['vulnerability_score'] > 0.7]
        
        briefing = f"""
# Infrastructure Analysis Briefing: {state}

## Executive Summary
- **Counties Analyzed**: {total_counties}
- **Average Vulnerability Score**: {avg_vulnerability:.2f} (0=resilient, 1=vulnerable)
- **Total Coverage Gaps Identified**: {total_gaps}
- **Critical Counties**: {len(critical_counties)}

## Key Findings

### Network Vulnerability
The infrastructure network in {state} shows varying levels of resilience:
- **High Resilience** (score < 0.3): {len([r for r in analysis_results if r['vulnerability_score'] < 0.3])} counties
- **Moderate Resilience** (0.3-0.6): {len([r for r in analysis_results if 0.3 <= r['vulnerability_score'] < 0.6])} counties  
- **Low Resilience** (score > 0.6): {len([r for r in analysis_results if r['vulnerability_score'] >= 0.6])} counties

### Coverage Gaps
Priority areas requiring infrastructure investment:
"""
        
        # Add gap details
        all_gaps = []
        for result in analysis_results:
            for gap in result['coverage_gaps']:
                all_gaps.append({
                    'county': result['county_name'],
                    'type': gap['type'],
                    'severity': gap['severity'],
                    'population': gap['population_affected']
                })
        
        # Sort by severity and population
        all_gaps.sort(key=lambda x: (x['severity'] != 'critical', -x['population']))
        
        for gap in all_gaps[:10]:
            briefing += f"- **{gap['county']}**: {gap['type']} gap affecting {gap['population']:,} people ({gap['severity']})\n"
        
        # Investment recommendations
        briefing += f"""
### Investment Recommendations
Based on gap analysis and ROI optimization:
"""
        
        all_investments = []
        for result in analysis_results:
            all_investments.extend(result.get('investment_recommendations', []))
        
        # Sort by priority
        all_investments.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        total_cost = sum(inv['cost_millions'] for inv in all_investments[:10])
        briefing += f"- **Estimated Investment Needed**: ${total_cost:.1f}M for top 10 priorities\n"
        briefing += f"- **People Served**: {sum(inv['population_served'] for inv in all_investments[:10]):,}\n\n"
        
        for i, inv in enumerate(all_investments[:5], 1):
            briefing += f"{i}. **{inv['facility_type'].replace('_', ' ').title()}** in {inv['county_fips']}: "
            briefing += f"${inv['cost_millions']:.1f}M (serves {inv['population_served']:,}, "
            briefing += f"coverage +{inv['coverage_improvement']:.1%})\n"
        
        return briefing
```

---

## 8. Integration with Existing Code

### 8.1 Pipeline Integration

```python
# /src/pipeline/infrastructure_pipeline.py

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import json

from ..infrastructure.core.facility_loader import FacilityLoader
from ..infrastructure.network.advanced_network import AdvancedInfrastructureNetwork
from ..infrastructure.analysis.gap_identifier import GapIdentifier
from ..infrastructure.analysis.investment_optimizer import InvestmentOptimizer
from ..infrastructure.core.status_tracker import FacilityStatusTracker
from ..agents.infrastructure_agent import InfrastructureAnalysisAgent

class InfrastructurePipeline:
    """
    End-to-end infrastructure analysis pipeline
    Integrates with existing ResilienceAI pipeline
    """
    
    def __init__(self, data_dir: Path, output_dir: Path):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.facility_loader = FacilityLoader(data_dir / 'raw')
        self.network_analyzer = AdvancedInfrastructureNetwork(use_road_network=False)
        self.gap_identifier = GapIdentifier()
        self.investment_optimizer = InvestmentOptimizer()
        self.status_tracker = FacilityStatusTracker()
        
        # Create agent
        self.agent = InfrastructureAnalysisAgent(
            self.network_analyzer,
            self.gap_identifier,
            self.investment_optimizer,
            self.status_tracker
        )
        
    def run_full_pipeline(self, county_df: pd.DataFrame,
                         state_filter: Optional[str] = None) -> Dict:
        """
        Run complete infrastructure analysis pipeline
        
        Steps:
        1. Load facility data
        2. Build networks for each county
        3. Identify coverage gaps
        4. Generate investment recommendations
        5. Compile results
        """
        print("=" * 60)
        print("Infrastructure Analysis Pipeline")
        print("=" * 60)
        
        # Step 1: Load facilities
        print("\n[1/5] Loading facility data...")
        self._load_facilities()
        
        # Step 2: Filter counties if needed
        if state_filter:
            county_df = county_df[county_df['state'] == state_filter]
        
        # Step 3: Analyze each county
        print(f"\n[2/5] Analyzing {len(county_df)} counties...")
        results = []
        for _, county in county_df.iterrows():
            result = self._analyze_county(county)
            results.append(result)
        
        # Step 4: Identify gaps
        print("\n[3/5] Identifying coverage gaps...")
        gaps = self.gap_identifier.identify_gaps(county_df)
        
        # Step 5: Generate investment plan
        print("\n[4/5] Generating investment recommendations...")
        for gap in gaps:
            self.investment_optimizer.add_investment_option(gap)
        
        investment_plan = self.investment_optimizer.optimize_investments()
        
        # Step 6: Save results
        print("\n[5/5] Saving results...")
        self._save_results(results, gaps, investment_plan)
        
        print("\n" + "=" * 60)
        print("Pipeline Complete!")
        print("=" * 60)
        
        return {
            'counties_analyzed': len(results),
            'gaps_identified': len(gaps),
            'investment_plan': investment_plan
        }
    
    def _load_facilities(self) -> None:
        """Load all facility types"""
        facility_types = ['hospitals', 'fire_stations', 'ems_stations', 'nursing_homes']
        
        for ftype in facility_types:
            df = self.facility_loader.load_facilities(ftype)
            if df is not None:
                self.gap_identifier.add_facility_type(ftype, df)
                print(f"  Loaded {len(df)} {ftype}")
    
    def _analyze_county(self, county: pd.Series) -> Dict:
        """Analyze infrastructure for a single county"""
        return self.agent.analyze_county_infrastructure(
            str(county['fips']),
            pd.DataFrame([county])
        )
    
    def _save_results(self, results: List[Dict], gaps: List,
                     investment_plan: Dict) -> None:
        """Save all results to output directory"""
        
        # Save county analyses
        with open(self.output_dir / 'county_infrastructure.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save gaps
        if gaps:
            gaps_df = self.gap_identifier.generate_gap_report(gaps)
            gaps_df.to_csv(self.output_dir / 'coverage_gaps.csv', index=False)
        
        # Save investment plan
        with open(self.output_dir / 'investment_plan.json', 'w') as f:
            json.dump(investment_plan, f, indent=2, default=str)
        
        print(f"  Results saved to {self.output_dir}")
```

---

## 9. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)

| Priority | Component | Files | Effort |
|----------|-----------|-------|--------|
| 1 | Enhanced Facility Models | `/src/infrastructure/models/facility_models.py` | 2 days |
| 2 | Advanced Network Analysis | `/src/infrastructure/network/advanced_network.py` | 3 days |
| 3 | Gap Identification | `/src/infrastructure/analysis/gap_identifier.py` | 2 days |
| 4 | Pipeline Integration | `/src/pipeline/infrastructure_pipeline.py` | 2 days |

### Phase 2: Intelligence (Weeks 3-4)

| Priority | Component | Files | Effort |
|----------|-----------|-------|--------|
| 5 | Investment Optimization | `/src/infrastructure/analysis/investment_optimizer.py` | 3 days |
| 6 | Redundancy Scoring | `/src/infrastructure/network/redundancy_scorer.py` | 2 days |
| 7 | Accessibility Model | `/src/infrastructure/network/accessibility_model.py` | 3 days |
| 8 | Infrastructure Agent | `/src/agents/infrastructure_agent.py` | 2 days |

### Phase 3: Real-Time (Weeks 5-6)

| Priority | Component | Files | Effort |
|----------|-----------|-------|--------|
| 9 | Status Tracker | `/src/infrastructure/core/status_tracker.py` | 3 days |
| 10 | Data Synchronization | `/src/infrastructure/utils/data_sync.py` | 2 days |
| 11 | Alert System | `/src/infrastructure/core/alert_manager.py` | 2 days |
| 12 | Dashboard Integration | `/app/infrastructure_dashboard.py` | 3 days |

### Phase 4: Advanced Features (Weeks 7-8)

| Priority | Component | Files | Effort |
|----------|-----------|-------|--------|
| 13 | Predictive Models | `/models/infrastructure/capacity_predictor.py` | 4 days |
| 14 | Scenario Simulation | `/src/infrastructure/analysis/scenario_simulator.py` | 3 days |
| 15 | Multi-Objective Optimization | `/src/infrastructure/analysis/multi_objective.py` | 3 days |
| 16 | Performance Monitoring | `/src/infrastructure/core/performance_monitor.py` | 2 days |

---

## 10. Key Metrics and KPIs

### Infrastructure Health Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Network Density | > 0.3 | Graph density calculation |
| Coverage Ratio | > 0.9 | Population within benchmark distance |
| Redundancy Score | > 0.7 | Multiple facility coverage |
| Response Time | < 15 min | Average travel time to nearest facility |
| Cascade Risk | < 0.3 | Vulnerability to cascade failures |

### Gap Analysis KPIs

| KPI | Target | Description |
|-----|--------|-------------|
| Critical Gaps | 0 | Counties with no facility coverage |
| High Priority Gaps | < 5% | Counties with severe coverage gaps |
| Population Affected | < 100K | People in coverage gap areas |
| Remediation Rate | > 80% | Gaps addressed per planning cycle |

### Investment Optimization KPIs

| KPI | Target | Description |
|-----|--------|-------------|
| ROI | > 2.0 | Benefit-cost ratio |
| People Served/$M | > 10K | Population served per million invested |
| Coverage Improvement | > 20% | Increase in coverage per investment |
| Payback Period | < 5 years | Time to recover investment |

---

## 11. Conclusion

The proposed infrastructure intelligence platform transforms ResilienceAI from a basic facility mapping tool into a comprehensive infrastructure analysis and optimization system. Key enhancements include:

1. **Advanced Network Analysis**: Multi-modal routing, capacity-weighted centrality, and dynamic status integration
2. **Systematic Gap Identification**: Population-weighted coverage analysis with benchmark comparison
3. **Investment Optimization**: ROI-based decision support with multi-objective optimization
4. **Real-Time Status Tracking**: Live facility status from multiple data sources
5. **Predictive Capabilities**: Demand forecasting and capacity prediction models

The phased implementation approach ensures incremental value delivery while building toward the complete infrastructure intelligence platform.

---

## Appendix A: Configuration Example

```python
# /config.py additions for infrastructure module

INFRASTRUCTURE_CONFIG = {
    'facility_types': ['hospitals', 'fire_stations', 'ems_stations', 
                      'nursing_homes', 'urgent_care', 'clinics'],
    'coverage_benchmarks': {
        'hospital': 25,
        'fire_station': 15,
        'ems_station': 20,
        'nursing_home': 30,
        'urgent_care': 15,
        'clinic': 20
    },
    'facility_costs': {
        'hospital': 50.0,
        'fire_station': 2.5,
        'ems_station': 1.5,
        'nursing_home': 10.0,
        'urgent_care': 3.0,
        'clinic': 1.0
    },
    'status_sources': [
        {
            'name': 'state_health_dept',
            'url': 'https://health.mo.gov/api/facility-status',
            'update_interval': 300
        }
    ],
    'network_analysis': {
        'default_radius_km': 80,
        'connectivity_km': 50,
        'use_road_network': False
    }
}
```

## Appendix B: API Endpoints

```python
# Proposed API endpoints for infrastructure module

INFRASTRUCTURE_ENDPOINTS = {
    'GET /api/v1/infrastructure/network/{county_fips}': {
        'description': 'Get network analysis for county',
        'response': 'Network metrics and critical facilities'
    },
    'GET /api/v1/infrastructure/gaps': {
        'description': 'Get all coverage gaps',
        'params': ['state', 'severity', 'facility_type'],
        'response': 'List of coverage gaps'
    },
    'POST /api/v1/infrastructure/optimize': {
        'description': 'Optimize infrastructure investments',
        'body': {'budget': float, 'objective': str},
        'response': 'Investment recommendations'
    },
    'GET /api/v1/infrastructure/status/{facility_id}': {
        'description': 'Get real-time facility status',
        'response': 'Facility status update'
    },
    'GET /api/v1/infrastructure/briefing/{state}': {
        'description': 'Get infrastructure briefing',
        'response': 'Natural language briefing'
    }
}
```

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: Infrastructure Analysis Team*
