# ResilienceAI Network Analysis Enhancement Design

## Executive Summary

This document provides a comprehensive design for enhancing the network analysis capabilities of the ResilienceAI platform. The current implementation in `src/network_analysis.py` provides basic graph modeling and limited network metrics. This enhancement introduces a full-featured network analysis platform with advanced graph algorithms, resilience metrics, cascading failure modeling, and sophisticated visualization capabilities.

---

## 1. Analysis of Current Network Capabilities

### 1.1 Current Implementation (`src/network_analysis.py`)

**File Location:** `/src/network_analysis.py` (276 lines, 233 loc, 10.2 KB)

**Current Features:**
- Basic NetworkX graph construction from facility data
- Haversine distance calculations for geographic networks
- Simple facility network building within radius
- Basic network metrics:
  - Network density
  - Connected components count
  - Betweenness centrality
  - Articulation points identification
  - Average clustering coefficient
- Composite vulnerability scoring
- Simple cascade failure simulation
- County-level network analysis

**Current Limitations:**
1. **Limited Graph Types:** Only undirected graphs supported
2. **Basic Centrality:** Only betweenness centrality implemented
3. **No Shortest Path Analysis:** Missing critical path identification
4. **Simple Cascade Model:** Neighbor-based failure only, no load redistribution
5. **No Community Detection:** Missing cluster analysis for facility groups
6. **Limited Resilience Metrics:** No percolation or robustness measures
7. **No Multi-layer Networks:** Cannot model interdependent infrastructure
8. **Basic Visualization:** No integrated network visualization

---

## 2. Proposed Network Analysis Platform Architecture

### 2.1 Module Structure

```
src/network/
├── __init__.py                          # Module exports
├── core/
│   ├── __init__.py
│   ├── base_graph.py                    # Base graph classes
│   ├── infrastructure_graph.py          # Infrastructure-specific graphs
│   └── multi_layer_graph.py             # Multi-layer network support
├── analysis/
│   ├── __init__.py
│   ├── centrality.py                    # Centrality analysis suite
│   ├── connectivity.py                  # Connectivity assessment
│   ├── paths.py                         # Shortest path algorithms
│   ├── communities.py                   # Community detection
│   └── resilience.py                    # Resilience metrics
├── simulation/
│   ├── __init__.py
│   ├── cascade_failure.py               # Cascading failure models
│   ├── percolation.py                   # Percolation analysis
│   └── attack_strategies.py             # Network attack simulations
├── visualization/
│   ├── __init__.py
│   ├── network_plots.py                 # Static network plots
│   ├── interactive_viz.py               # Interactive visualizations
│   └── geospatial_network.py            # Geo-network visualization
├── utils/
│   ├── __init__.py
│   ├── graph_io.py                      # Graph import/export
│   ├── metrics.py                       # Utility metrics
│   └── validators.py                    # Input validation
└── tests/
    ├── __init__.py
    ├── test_centrality.py
    ├── test_cascade.py
    └── test_resilience.py
```

### 2.2 Integration Points with Existing Code

| Existing Module | Integration Point | New Capability |
|----------------|-------------------|----------------|
| `network_analysis.py` | Refactor to use new core classes | Backward compatibility layer |
| `spatial_stats.py` | Shared distance calculations | Spatial network analysis |
| `geo_visualizations.py` | Network overlay on maps | Geospatial network viz |
| `scenario_simulator.py` | Cascade simulation integration | Enhanced failure modeling |
| `predictive_models.py` | Network features for ML | Graph-based predictions |
| `agent_orchestrator.py` | Network analysis MCP tools | Agent-accessible network ops |

---

## 3. Graph Modeling Framework

### 3.1 Core Graph Classes

**File:** `src/network/core/base_graph.py`

```python
"""
ResilienceAI - Base Graph Classes
Core graph abstractions for infrastructure network modeling.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    import graph_tool.all as gt
    HAS_GRAPHTOOL = True
except ImportError:
    HAS_GRAPHTOOL = False


class NodeType(Enum):
    """Types of infrastructure nodes."""
    HOSPITAL = "hospital"
    FIRE_STATION = "fire_station"
    EMS_STATION = "ems_station"
    NURSING_HOME = "nursing_home"
    SHELTER = "shelter"
    POWER_PLANT = "power_plant"
    SUBSTATION = "substation"
    WATER_PLANT = "water_plant"
    COMMUNICATION = "communication"
    TRANSPORTATION = "transportation"
    GENERIC = "generic"


class EdgeType(Enum):
    """Types of infrastructure edges."""
    PHYSICAL = "physical"
    COMMUNICATION = "communication"
    POWER = "power"
    WATER = "water"
    TRANSPORT = "transport"
    DEPENDENCY = "dependency"
    PROXIMITY = "proximity"


@dataclass
class NodeAttributes:
    """Standardized node attributes for infrastructure nodes."""
    node_id: str
    node_type: NodeType
    name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    capacity: float = 1.0
    current_load: float = 0.0
    resilience_score: float = 1.0
    population_served: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'node_type': self.node_type.value,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'capacity': self.capacity,
            'current_load': self.current_load,
            'resilience_score': self.resilience_score,
            'population_served': self.population_served,
            'metadata': self.metadata
        }


@dataclass
class EdgeAttributes:
    """Standardized edge attributes for infrastructure edges."""
    edge_type: EdgeType
    weight: float = 1.0
    capacity: float = 1.0
    latency: float = 0.0
    reliability: float = 1.0
    distance_km: float = 0.0
    bidirectional: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'edge_type': self.edge_type.value,
            'weight': self.weight,
            'capacity': self.capacity,
            'latency': self.latency,
            'reliability': self.reliability,
            'distance_km': self.distance_km,
            'bidirectional': self.bidirectional,
            'metadata': self.metadata
        }


class BaseInfrastructureGraph(ABC):
    """Abstract base class for infrastructure network graphs."""
    
    def __init__(self, name: str = "infrastructure_network"):
        self.name = name
        self._nodes: Dict[str, NodeAttributes] = {}
        self._edges: Dict[Tuple[str, str], EdgeAttributes] = {}
        self._node_type_index: Dict[NodeType, Set[str]] = {}
        self._edge_type_index: Dict[EdgeType, Set[Tuple[str, str]]] = {}
    
    @abstractmethod
    def add_node(self, node_id: str, attrs: NodeAttributes) -> bool:
        """Add a node to the graph."""
        pass
    
    @abstractmethod
    def add_edge(self, source: str, target: str, attrs: EdgeAttributes) -> bool:
        """Add an edge to the graph."""
        pass
    
    @abstractmethod
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the graph."""
        pass
    
    @abstractmethod
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighboring nodes."""
        pass
    
    @abstractmethod
    def to_networkx(self) -> 'nx.Graph':
        """Convert to NetworkX graph."""
        pass
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[str]:
        """Get all nodes of a specific type."""
        return list(self._node_type_index.get(node_type, set()))
    
    def get_edges_by_type(self, edge_type: EdgeType) -> List[Tuple[str, str]]:
        """Get all edges of a specific type."""
        return list(self._edge_type_index.get(edge_type, set()))
    
    def get_node_attributes(self, node_id: str) -> Optional[NodeAttributes]:
        """Get attributes for a specific node."""
        return self._nodes.get(node_id)
    
    def get_edge_attributes(self, source: str, target: str) -> Optional[EdgeAttributes]:
        """Get attributes for a specific edge."""
        return self._edges.get((source, target))


class NetworkXInfrastructureGraph(BaseInfrastructureGraph):
    """NetworkX-based implementation of infrastructure graph."""
    
    def __init__(self, name: str = "infrastructure_network", directed: bool = False):
        super().__init__(name)
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required. Install with: pip install networkx")
        
        self._graph = nx.DiGraph() if directed else nx.Graph()
        self._directed = directed
    
    def add_node(self, node_id: str, attrs: NodeAttributes) -> bool:
        if node_id in self._nodes:
            return False
        
        self._nodes[node_id] = attrs
        self._graph.add_node(node_id, **attrs.to_dict())
        
        # Update type index
        if attrs.node_type not in self._node_type_index:
            self._node_type_index[attrs.node_type] = set()
        self._node_type_index[attrs.node_type].add(node_id)
        
        return True
    
    def add_edge(self, source: str, target: str, attrs: EdgeAttributes) -> bool:
        if source not in self._nodes or target not in self._nodes:
            return False
        
        edge_key = (source, target)
        self._edges[edge_key] = attrs
        self._graph.add_edge(source, target, **attrs.to_dict())
        
        # Update type index
        if attrs.edge_type not in self._edge_type_index:
            self._edge_type_index[attrs.edge_type] = set()
        self._edge_type_index[attrs.edge_type].add(edge_key)
        
        return True
    
    def remove_node(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        
        # Remove from type index
        node_type = self._nodes[node_id].node_type
        self._node_type_index[node_type].discard(node_id)
        
        # Remove connected edges from edge index
        for neighbor in self.get_neighbors(node_id):
            edge_key = (node_id, neighbor) if node_id < neighbor else (neighbor, node_id)
            if edge_key in self._edges:
                edge_type = self._edges[edge_key].edge_type
                self._edge_type_index[edge_type].discard(edge_key)
                del self._edges[edge_key]
        
        del self._nodes[node_id]
        self._graph.remove_node(node_id)
        
        return True
    
    def get_neighbors(self, node_id: str) -> List[str]:
        if node_id not in self._graph:
            return []
        return list(self._graph.neighbors(node_id))
    
    def to_networkx(self) -> 'nx.Graph':
        return self._graph.copy()
    
    def get_graph(self) -> 'nx.Graph':
        """Get the underlying NetworkX graph."""
        return self._graph
    
    @property
    def num_nodes(self) -> int:
        return self._graph.number_of_nodes()
    
    @property
    def num_edges(self) -> int:
        return self._graph.number_of_edges()
```

### 3.2 Infrastructure-Specific Graph Builder

**File:** `src/network/core/infrastructure_graph.py`

```python
"""
ResilienceAI - Infrastructure Graph Builder
Specialized graph construction for disaster resilience infrastructure.
"""
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from pathlib import Path

from .base_graph import (
    NetworkXInfrastructureGraph, NodeAttributes, EdgeAttributes,
    NodeType, EdgeType
)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate haversine distance between two points in kilometers."""
    R = 6371.0  # Earth's radius in km
    lat1_rad, lon1_rad = np.radians([lat1, lon1])
    lat2_rad, lon2_rad = np.radians([lat2, lon2])
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c


class InfrastructureGraphBuilder:
    """Build infrastructure networks from various data sources."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir
        self._facility_loaders = {
            'hospitals': self._load_hifld_facilities,
            'fire_stations': self._load_hifld_facilities,
            'ems_stations': self._load_hifld_facilities,
            'nursing_homes': self._load_hifld_facilities,
            'shelters': self._load_hifld_facilities,
            'power_plants': self._load_hifld_facilities,
            'substations': self._load_hifld_facilities,
        }
    
    def build_from_facilities(
        self,
        facilities_df: pd.DataFrame,
        facility_type_col: str = 'facility_type',
        lat_col: str = 'latitude',
        lon_col: str = 'longitude',
        name_col: str = 'name',
        connect_by_proximity: bool = True,
        proximity_threshold_km: float = 50.0,
        directed: bool = False
    ) -> NetworkXInfrastructureGraph:
        """
        Build infrastructure graph from facilities DataFrame.
        
        Args:
            facilities_df: DataFrame with facility information
            facility_type_col: Column name for facility type
            lat_col: Column name for latitude
            lon_col: Column name for longitude
            name_col: Column name for facility name
            connect_by_proximity: Whether to add edges based on proximity
            proximity_threshold_km: Maximum distance for edge creation
            directed: Whether to create a directed graph
        
        Returns:
            NetworkXInfrastructureGraph instance
        """
        graph = NetworkXInfrastructureGraph(directed=directed)
        
        # Map facility types to NodeType
        type_mapping = {
            'hospital': NodeType.HOSPITAL,
            'hospitals': NodeType.HOSPITAL,
            'fire_station': NodeType.FIRE_STATION,
            'fire_stations': NodeType.FIRE_STATION,
            'ems': NodeType.EMS_STATION,
            'ems_station': NodeType.EMS_STATION,
            'ems_stations': NodeType.EMS_STATION,
            'nursing_home': NodeType.NURSING_HOME,
            'nursing_homes': NodeType.NURSING_HOME,
            'shelter': NodeType.SHELTER,
            'shelters': NodeType.SHELTER,
            'power_plant': NodeType.POWER_PLANT,
            'power_plants': NodeType.POWER_PLANT,
            'substation': NodeType.SUBSTATION,
            'substations': NodeType.SUBSTATION,
        }
        
        # Add nodes
        for idx, row in facilities_df.iterrows():
            facility_type_str = str(row.get(facility_type_col, 'generic')).lower()
            node_type = type_mapping.get(facility_type_str, NodeType.GENERIC)
            
            node_id = f"{facility_type_str}_{idx}"
            attrs = NodeAttributes(
                node_id=node_id,
                node_type=node_type,
                name=str(row.get(name_col, f"Facility {idx}")),
                latitude=float(row.get(lat_col, 0.0)),
                longitude=float(row.get(lon_col, 0.0)),
                metadata=row.to_dict()
            )
            graph.add_node(node_id, attrs)
        
        # Add proximity edges
        if connect_by_proximity:
            self._add_proximity_edges(graph, proximity_threshold_km)
        
        return graph
    
    def _add_proximity_edges(
        self,
        graph: NetworkXInfrastructureGraph,
        threshold_km: float
    ) -> None:
        """Add edges between facilities within proximity threshold."""
        nodes = list(graph._nodes.keys())
        coords = [
            (graph._nodes[n].latitude, graph._nodes[n].longitude)
            for n in nodes
        ]
        
        # Build distance matrix efficiently
        n = len(nodes)
        for i in range(n):
            lat1, lon1 = coords[i]
            for j in range(i + 1, n):
                lat2, lon2 = coords[j]
                dist = haversine_distance(lat1, lon1, lat2, lon2)
                
                if dist <= threshold_km:
                    edge_attrs = EdgeAttributes(
                        edge_type=EdgeType.PROXIMITY,
                        weight=1.0 / (dist + 1),  # Inverse distance weighting
                        distance_km=dist,
                        bidirectional=True
                    )
                    graph.add_edge(nodes[i], nodes[j], edge_attrs)
    
    def build_regional_network(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float = 80.0,
        facility_types: Optional[List[str]] = None
    ) -> NetworkXInfrastructureGraph:
        """
        Build a regional infrastructure network around a center point.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius to include facilities
            facility_types: List of facility types to include
        
        Returns:
            Regional infrastructure network graph
        """
        if facility_types is None:
            facility_types = ['hospitals', 'fire_stations', 'ems_stations', 'nursing_homes']
        
        all_facilities = []
        
        for ftype in facility_types:
            loader = self._facility_loaders.get(ftype)
            if loader:
                df = loader(ftype)
                if df is not None:
                    # Filter by distance
                    df = df.dropna(subset=['latitude', 'longitude'])
                    df['distance_to_center'] = df.apply(
                        lambda row: haversine_distance(
                            center_lat, center_lon,
                            row['latitude'], row['longitude']
                        ),
                        axis=1
                    )
                    df = df[df['distance_to_center'] <= radius_km].copy()
                    df['facility_type'] = ftype
                    all_facilities.append(df)
        
        if not all_facilities:
            return NetworkXInfrastructureGraph()
        
        combined_df = pd.concat(all_facilities, ignore_index=True)
        return self.build_from_facilities(combined_df)
    
    def _load_hifld_facilities(self, facility_type: str) -> Optional[pd.DataFrame]:
        """Load HIFLD facility data."""
        if self.data_dir is None:
            return None
        
        filepath = self.data_dir / f"hifld_{facility_type}.csv"
        if filepath.exists():
            return pd.read_csv(filepath)
        return None
```

---

## 4. Network Centrality Analysis Module

### 4.1 Comprehensive Centrality Suite

**File:** `src/network/analysis/centrality.py`

```python
"""
ResilienceAI - Network Centrality Analysis
Comprehensive centrality metrics for infrastructure vulnerability assessment.
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class CentralityType(Enum):
    """Types of centrality measures."""
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    CLOSENESS = "closeness"
    EIGENVECTOR = "eigenvector"
    PAGERANK = "pagerank"
    KATZ = "katz"
    HARMONIC = "harmonic"
    LOAD = "load"
    SUBGRAPH = "subgraph"
    INFORMATION = "information"


@dataclass
class CentralityResult:
    """Result container for centrality analysis."""
    node_id: str
    centrality_type: CentralityType
    value: float
    rank: int
    percentile: float
    is_critical: bool


class CentralityAnalyzer:
    """Comprehensive centrality analysis for infrastructure networks."""
    
    def __init__(self, graph: 'nx.Graph'):
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required")
        self.graph = graph
        self._cached_results: Dict[CentralityType, Dict[str, float]] = {}
    
    def compute_all_centralities(
        self,
        weight: Optional[str] = 'weight',
        normalized: bool = True,
        top_k: int = 10
    ) -> Dict[CentralityType, List[CentralityResult]]:
        """
        Compute all centrality measures.
        
        Args:
            weight: Edge attribute to use as weight
            normalized: Whether to normalize results
            top_k: Number of top nodes to return for each measure
        
        Returns:
            Dictionary mapping centrality types to sorted results
        """
        results = {}
        
        for cent_type in CentralityType:
            try:
                cent_results = self.compute_centrality(
                    cent_type, weight, normalized
                )
                # Sort and get top k
                sorted_results = sorted(
                    cent_results.values(),
                    key=lambda x: x.value,
                    reverse=True
                )[:top_k]
                results[cent_type] = sorted_results
            except Exception as e:
                print(f"Warning: Could not compute {cent_type.value}: {e}")
                results[cent_type] = []
        
        return results
    
    def compute_centrality(
        self,
        centrality_type: CentralityType,
        weight: Optional[str] = 'weight',
        normalized: bool = True
    ) -> Dict[str, CentralityResult]:
        """
        Compute a specific centrality measure.
        
        Args:
            centrality_type: Type of centrality to compute
            weight: Edge attribute to use as weight
            normalized: Whether to normalize results
        
        Returns:
            Dictionary mapping node IDs to centrality results
        """
        if centrality_type in self._cached_results:
            values = self._cached_results[centrality_type]
        else:
            values = self._compute_centrality_values(
                centrality_type, weight, normalized
            )
            self._cached_results[centrality_type] = values
        
        # Create ranked results
        sorted_nodes = sorted(values.items(), key=lambda x: x[1], reverse=True)
        total_nodes = len(sorted_nodes)
        
        results = {}
        for rank, (node_id, value) in enumerate(sorted_nodes, 1):
            percentile = (total_nodes - rank + 1) / total_nodes * 100
            is_critical = rank <= max(1, total_nodes * 0.1)  # Top 10%
            
            results[node_id] = CentralityResult(
                node_id=node_id,
                centrality_type=centrality_type,
                value=value,
                rank=rank,
                percentile=percentile,
                is_critical=is_critical
            )
        
        return results
    
    def _compute_centrality_values(
        self,
        centrality_type: CentralityType,
        weight: Optional[str],
        normalized: bool
    ) -> Dict[str, float]:
        """Compute raw centrality values."""
        G = self.graph
        
        if centrality_type == CentralityType.DEGREE:
            if weight:
                return dict(nx.degree(G, weight=weight))
            return dict(nx.degree(G))
        
        elif centrality_type == CentralityType.BETWEENNESS:
            return nx.betweenness_centrality(
                G, weight=weight, normalized=normalized
            )
        
        elif centrality_type == CentralityType.CLOSENESS:
            return nx.closeness_centrality(G, distance=weight)
        
        elif centrality_type == CentralityType.EIGENVECTOR:
            try:
                return nx.eigenvector_centrality(
                    G, weight=weight, max_iter=1000
                )
            except nx.PowerIterationFailedConvergence:
                # Fallback to simpler method
                return nx.eigenvector_centrality_numpy(G, weight=weight)
        
        elif centrality_type == CentralityType.PAGERANK:
            return nx.pagerank(G, weight=weight)
        
        elif centrality_type == CentralityType.KATZ:
            try:
                return nx.katz_centrality(G, weight=weight)
            except:
                # Use numpy version for better convergence
                return nx.katz_centrality_numpy(G, weight=weight)
        
        elif centrality_type == CentralityType.HARMONIC:
            return nx.harmonic_centrality(G, distance=weight)
        
        elif centrality_type == CentralityType.LOAD:
            return nx.load_centrality(G, weight=weight)
        
        elif centrality_type == CentralityType.SUBGRAPH:
            return nx.subgraph_centrality(G)
        
        elif centrality_type == CentralityType.INFORMATION:
            return nx.information_centrality(G, weight=weight)
        
        else:
            raise ValueError(f"Unknown centrality type: {centrality_type}")
    
    def identify_critical_nodes(
        self,
        methods: Optional[List[CentralityType]] = None,
        consensus_threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        Identify critical nodes using multiple centrality methods.
        
        Args:
            methods: List of centrality methods to use
            consensus_threshold: Fraction of methods that must agree
        
        Returns:
            List of (node_id, consensus_score) tuples
        """
        if methods is None:
            methods = [
                CentralityType.BETWEENNESS,
                CentralityType.DEGREE,
                CentralityType.EIGENVECTOR,
                CentralityType.CLOSENESS
            ]
        
        # Get top nodes from each method
        top_nodes_per_method = {}
        for method in methods:
            results = self.compute_centrality(method)
            critical = [r.node_id for r in results.values() if r.is_critical]
            top_nodes_per_method[method] = set(critical)
        
        # Count occurrences across methods
        node_votes: Dict[str, int] = {}
        for method_nodes in top_nodes_per_method.values():
            for node in method_nodes:
                node_votes[node] = node_votes.get(node, 0) + 1
        
        # Calculate consensus scores
        consensus_scores = {
            node: votes / len(methods)
            for node, votes in node_votes.items()
        }
        
        # Filter by threshold and sort
        critical_nodes = [
            (node, score)
            for node, score in consensus_scores.items()
            if score >= consensus_threshold
        ]
        
        return sorted(critical_nodes, key=lambda x: x[1], reverse=True)
    
    def compute_group_centrality(
        self,
        node_groups: Dict[str, List[str]],
        centrality_type: CentralityType = CentralityType.BETWEENNESS
    ) -> Dict[str, float]:
        """
        Compute group centrality for sets of nodes.
        
        Args:
            node_groups: Dictionary mapping group names to node lists
            centrality_type: Centrality measure to use
        
        Returns:
            Dictionary mapping group names to centrality scores
        """
        group_scores = {}
        
        for group_name, nodes in node_groups.items():
            # Filter to existing nodes
            valid_nodes = [n for n in nodes if n in self.graph]
            
            if not valid_nodes:
                group_scores[group_name] = 0.0
                continue
            
            # Compute group betweenness
            if centrality_type == CentralityType.BETWEENNESS:
                score = self._group_betweenness(valid_nodes)
            else:
                # Use average of individual centralities
                individual = self.compute_centrality(centrality_type)
                score = np.mean([
                    individual[n].value for n in valid_nodes if n in individual
                ]) if individual else 0.0
            
            group_scores[group_name] = score
        
        return group_scores
    
    def _group_betweenness(self, nodes: List[str]) -> float:
        """Compute group betweenness centrality."""
        G = self.graph
        nodes_set = set(nodes)
        
        betweenness = 0.0
        for source in G.nodes():
            if source in nodes_set:
                continue
            for target in G.nodes():
                if target in nodes_set or source >= target:
                    continue
                
                # Count shortest paths going through group
                try:
                    paths = list(nx.all_shortest_paths(G, source, target))
                    total_paths = len(paths)
                    through_group = sum(
                        1 for p in paths if any(n in nodes_set for n in p[1:-1])
                    )
                    betweenness += through_group / total_paths if total_paths > 0 else 0
                except nx.NetworkXNoPath:
                    continue
        
        return betweenness


def compare_centrality_distributions(
    graph1: 'nx.Graph',
    graph2: 'nx.Graph',
    centrality_type: CentralityType = CentralityType.BETWEENNESS
) -> Dict[str, Any]:
    """
    Compare centrality distributions between two graphs.
    
    Args:
        graph1: First graph
        graph2: Second graph
        centrality_type: Centrality measure to compare
    
    Returns:
        Dictionary with comparison statistics
    """
    analyzer1 = CentralityAnalyzer(graph1)
    analyzer2 = CentralityAnalyzer(graph2)
    
    cent1 = analyzer1.compute_centrality(centrality_type)
    cent2 = analyzer2.compute_centrality(centrality_type)
    
    values1 = [r.value for r in cent1.values()]
    values2 = [r.value for r in cent2.values()]
    
    return {
        'graph1_mean': np.mean(values1),
        'graph1_std': np.std(values1),
        'graph2_mean': np.mean(values2),
        'graph2_std': np.std(values2),
        'difference_mean': np.mean(values1) - np.mean(values2),
        'ratio': np.mean(values1) / np.mean(values2) if np.mean(values2) > 0 else float('inf'),
        'graph1_max': max(values1) if values1 else 0,
        'graph2_max': max(values2) if values2 else 0,
    }
```

---

## 5. Connectivity Assessment Module

### 5.1 Comprehensive Connectivity Analysis

**File:** `src/network/analysis/connectivity.py`

```python
"""
ResilienceAI - Network Connectivity Assessment
Comprehensive connectivity metrics for infrastructure resilience.
"""
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class ConnectivityMetric(Enum):
    """Types of connectivity metrics."""
    ALGEBRAIC_CONNECTIVITY = "algebraic_connectivity"
    EFFECTIVE_RESISTANCE = "effective_resistance"
    NODE_CONNECTIVITY = "node_connectivity"
    EDGE_CONNECTIVITY = "edge_connectivity"
    AVERAGE_NODE_CONNECTIVITY = "average_node_connectivity"
    DIAMETER = "diameter"
    RADIUS = "radius"
    PERCOLATION_THRESHOLD = "percolation_threshold"


@dataclass
class ConnectivityResult:
    """Result container for connectivity analysis."""
    metric: ConnectivityMetric
    value: float
    interpretation: str
    critical_nodes: Optional[List[str]] = None
    critical_edges: Optional[List[Tuple[str, str]]] = None


@dataclass
class ComponentAnalysis:
    """Analysis of connected components."""
    component_id: int
    nodes: List[str]
    size: int
    diameter: int
    center: Optional[str]
    periphery: List[str]
    is_giant_component: bool
    density: float


class ConnectivityAnalyzer:
    """Comprehensive connectivity analysis for infrastructure networks."""
    
    def __init__(self, graph: 'nx.Graph'):
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required")
        self.graph = graph
        self._is_connected = nx.is_connected(graph) if graph.number_of_nodes() > 0 else False
    
    def compute_all_metrics(self) -> Dict[ConnectivityMetric, ConnectivityResult]:
        """Compute all connectivity metrics."""
        metrics = {}
        
        for metric_type in ConnectivityMetric:
            try:
                result = self.compute_metric(metric_type)
                metrics[metric_type] = result
            except Exception as e:
                print(f"Warning: Could not compute {metric_type.value}: {e}")
        
        return metrics
    
    def compute_metric(self, metric: ConnectivityMetric) -> ConnectivityResult:
        """Compute a specific connectivity metric."""
        G = self.graph
        
        if metric == ConnectivityMetric.ALGEBRAIC_CONNECTIVITY:
            value = nx.algebraic_connectivity(G, weight='weight')
            interpretation = (
                "Higher values indicate better connectivity and faster diffusion. "
                f"Value {value:.4f} suggests " +
                ("strong connectivity" if value > 0.5 else 
                 "moderate connectivity" if value > 0.1 else "weak connectivity")
            )
            return ConnectivityResult(metric, value, interpretation)
        
        elif metric == ConnectivityMetric.NODE_CONNECTIVITY:
            value = nx.node_connectivity(G)
            interpretation = (
                f"Network remains connected after removing any {value-1} nodes. "
                f"Value {value} indicates " +
                ("high resilience" if value >= 3 else 
                 "moderate resilience" if value == 2 else "low resilience")
            )
            # Find minimum node cut
            if value < G.number_of_nodes():
                try:
                    cut = nx.minimum_node_cut(G)
                    critical_nodes = list(cut)
                except:
                    critical_nodes = []
            else:
                critical_nodes = []
            return ConnectivityResult(metric, value, interpretation, critical_nodes)
        
        elif metric == ConnectivityMetric.EDGE_CONNECTIVITY:
            value = nx.edge_connectivity(G)
            interpretation = (
                f"Network remains connected after removing any {value-1} edges. "
                f"Value {value} indicates " +
                ("high edge resilience" if value >= 3 else 
                 "moderate edge resilience" if value == 2 else "low edge resilience")
            )
            # Find minimum edge cut
            try:
                cut = nx.minimum_edge_cut(G)
                critical_edges = list(cut)
            except:
                critical_edges = []
            return ConnectivityResult(metric, value, interpretation, None, critical_edges)
        
        elif metric == ConnectivityMetric.AVERAGE_NODE_CONNECTIVITY:
            value = nx.average_node_connectivity(G)
            interpretation = (
                f"Average of {value:.2f} node-independent paths between node pairs. "
                "Higher values indicate better overall connectivity."
            )
            return ConnectivityResult(metric, value, interpretation)
        
        elif metric == ConnectivityMetric.DIAMETER:
            if self._is_connected:
                value = nx.diameter(G)
                interpretation = (
                    f"Maximum shortest path length is {value}. " +
                    ("Efficient network" if value <= 5 else 
                     "Moderate efficiency" if value <= 10 else "Inefficient network")
                )
            else:
                # Use largest component
                largest = max(nx.connected_components(G), key=len)
                subgraph = G.subgraph(largest)
                value = nx.diameter(subgraph)
                interpretation = f"Diameter of largest component is {value}"
            return ConnectivityResult(metric, value, interpretation)
        
        elif metric == ConnectivityMetric.RADIUS:
            if self._is_connected:
                value = nx.radius(G)
                interpretation = f"Minimum eccentricity is {value}"
            else:
                largest = max(nx.connected_components(G), key=len)
                subgraph = G.subgraph(largest)
                value = nx.radius(subgraph)
                interpretation = f"Radius of largest component is {value}"
            return ConnectivityResult(metric, value, interpretation)
        
        elif metric == ConnectivityMetric.EFFECTIVE_RESISTANCE:
            # Approximate using Laplacian pseudoinverse
            try:
                L = nx.laplacian_matrix(G).toarray()
                L_pinv = np.linalg.pinv(L)
                # Average effective resistance
                n = G.number_of_nodes()
                value = 2 * np.trace(L_pinv) / (n * (n - 1)) if n > 1 else 0
                interpretation = (
                    f"Average effective resistance is {value:.4f}. " +
                    "Lower values indicate better connectivity."
                )
            except:
                value = float('inf')
                interpretation = "Could not compute effective resistance"
            return ConnectivityResult(metric, value, interpretation)
        
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def analyze_components(self) -> List[ComponentAnalysis]:
        """Analyze all connected components."""
        G = self.graph
        components = []
        
        for idx, comp_nodes in enumerate(nx.connected_components(G), 1):
            subgraph = G.subgraph(comp_nodes)
            nodes_list = list(comp_nodes)
            
            # Compute component properties
            if len(nodes_list) > 1:
                diameter = nx.diameter(subgraph)
                center = nx.center(subgraph)[0]
                periphery = nx.periphery(subgraph)
            else:
                diameter = 0
                center = nodes_list[0] if nodes_list else None
                periphery = nodes_list
            
            density = nx.density(subgraph)
            
            # Determine if giant component
            total_nodes = G.number_of_nodes()
            is_giant = len(nodes_list) > total_nodes * 0.5 if total_nodes > 0 else False
            
            components.append(ComponentAnalysis(
                component_id=idx,
                nodes=nodes_list,
                size=len(nodes_list),
                diameter=diameter,
                center=center,
                periphery=periphery,
                is_giant_component=is_giant,
                density=density
            ))
        
        # Sort by size (descending)
        components.sort(key=lambda x: x.size, reverse=True)
        return components
    
    def find_articulation_points(self) -> Dict[str, Any]:
        """Find and analyze articulation points (cut vertices)."""
        G = self.graph
        
        articulation_points = list(nx.articulation_points(G))
        
        # Analyze impact of each articulation point
        impact_analysis = {}
        for ap in articulation_points:
            # Remove node and count resulting components
            G_temp = G.copy()
            G_temp.remove_node(ap)
            num_components = nx.number_connected_components(G_temp)
            
            # Find sizes of resulting components
            component_sizes = [
                len(c) for c in nx.connected_components(G_temp)
            ]
            
            impact_analysis[ap] = {
                'num_components_after_removal': num_components,
                'largest_component_size': max(component_sizes) if component_sizes else 0,
                'smallest_component_size': min(component_sizes) if component_sizes else 0,
                'nodes_disconnected': G.number_of_nodes() - 1 - sum(component_sizes)
            }
        
        return {
            'articulation_points': articulation_points,
            'count': len(articulation_points),
            'fraction': len(articulation_points) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0,
            'impact_analysis': impact_analysis
        }
    
    def find_bridges(self) -> Dict[str, Any]:
        """Find and analyze bridges (cut edges)."""
        G = self.graph
        
        bridges = list(nx.bridges(G))
        
        # Analyze impact of each bridge
        impact_analysis = {}
        for u, v in bridges:
            # Remove edge and check connectivity
            G_temp = G.copy()
            G_temp.remove_edge(u, v)
            
            # Check if nodes are still connected
            still_connected = nx.has_path(G_temp, u, v)
            
            if not still_connected:
                # Find component sizes
                comp_u = nx.node_connected_component(G_temp, u)
                comp_v = nx.node_connected_component(G_temp, v)
                
                impact_analysis[f"{u}-{v}"] = {
                    'disconnects_graph': True,
                    'component_1_size': len(comp_u),
                    'component_2_size': len(comp_v),
                    'edge_weight': G[u][v].get('weight', 1.0)
                }
            else:
                impact_analysis[f"{u}-{v}"] = {
                    'disconnects_graph': False,
                    'alternative_path_length': nx.shortest_path_length(G_temp, u, v)
                }
        
        return {
            'bridges': bridges,
            'count': len(bridges),
            'fraction': len(bridges) / G.number_of_edges() if G.number_of_edges() > 0 else 0,
            'impact_analysis': impact_analysis
        }
    
    def compute_vulnerability_matrix(self) -> pd.DataFrame:
        """
        Compute vulnerability matrix showing impact of node removal.
        
        Returns:
            DataFrame with vulnerability scores for each node
        """
        G = self.graph
        nodes = list(G.nodes())
        
        vulnerability_data = []
        
        for node in nodes:
            # Remove node
            G_temp = G.copy()
            G_temp.remove_node(node)
            
            # Compute metrics after removal
            num_components = nx.number_connected_components(G_temp)
            
            if G_temp.number_of_nodes() > 0:
                largest_comp = max(nx.connected_components(G_temp), key=len)
                largest_size = len(largest_comp)
                
                # Compute algebraic connectivity of largest component
                if len(largest_comp) > 1:
                    subgraph = G_temp.subgraph(largest_comp)
                    try:
                        alg_conn = nx.algebraic_connectivity(subgraph)
                    except:
                        alg_conn = 0
                else:
                    alg_conn = 0
            else:
                largest_size = 0
                alg_conn = 0
            
            vulnerability_data.append({
                'node': node,
                'num_components_after_removal': num_components,
                'largest_component_size': largest_size,
                'nodes_disconnected': G.number_of_nodes() - 1 - largest_size,
                'algebraic_connectivity': alg_conn,
                'vulnerability_score': num_components / max(G.number_of_nodes() - 1, 1)
            })
        
        return pd.DataFrame(vulnerability_data)


def compare_connectivity(
    graph1: 'nx.Graph',
    graph2: 'nx.Graph'
) -> Dict[str, Any]:
    """
    Compare connectivity between two graphs.
    
    Args:
        graph1: First graph
        graph2: Second graph
    
    Returns:
        Dictionary with comparison results
    """
    analyzer1 = ConnectivityAnalyzer(graph1)
    analyzer2 = ConnectivityAnalyzer(graph2)
    
    metrics1 = analyzer1.compute_all_metrics()
    metrics2 = analyzer2.compute_all_metrics()
    
    comparison = {}
    
    for metric in ConnectivityMetric:
        if metric in metrics1 and metric in metrics2:
            val1 = metrics1[metric].value
            val2 = metrics2[metric].value
            comparison[metric.value] = {
                'graph1': val1,
                'graph2': val2,
                'difference': val1 - val2,
                'ratio': val1 / val2 if val2 != 0 else float('inf'),
                'better_graph': 'graph1' if val1 > val2 else 'graph2' if val2 > val1 else 'equal'
            }
    
    return comparison
```

---

## 6. Critical Path Identification

### 6.1 Shortest Path Algorithms Module

**File:** `src/network/analysis/paths.py`

```python
"""
ResilienceAI - Critical Path Identification
Shortest path algorithms and critical path analysis for infrastructure networks.
"""
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from dataclasses import dataclass
from heapq import heappush, heappop
from collections import defaultdict
import numpy as np
import pandas as pd

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


@dataclass
class PathResult:
    """Result container for path analysis."""
    source: str
    target: str
    path: List[str]
    length: float
    num_hops: int
    edges: List[Tuple[str, str]]
    reliability: float


@dataclass
class MultiPathResult:
    """Result container for multiple path analysis."""
    source: str
    target: str
    paths: List[PathResult]
    total_paths: int
    node_disjoint_paths: int
    edge_disjoint_paths: int
    min_cut_size: int


class PathAnalyzer:
    """Comprehensive path analysis for infrastructure networks."""
    
    def __init__(self, graph: 'nx.Graph'):
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required")
        self.graph = graph
        self._precomputed_paths: Dict[Tuple[str, str], List[PathResult]] = {}
    
    def shortest_path(
        self,
        source: str,
        target: str,
        weight: Optional[str] = 'weight',
        method: str = 'dijkstra'
    ) -> Optional[PathResult]:
        """
        Find shortest path between two nodes.
        
        Args:
            source: Source node
            target: Target node
            weight: Edge weight attribute
            method: Algorithm ('dijkstra', 'bellman-ford', 'astar')
        
        Returns:
            PathResult or None if no path exists
        """
        G = self.graph
        
        try:
            if method == 'dijkstra':
                path = nx.dijkstra_path(G, source, target, weight=weight)
                length = nx.dijkstra_path_length(G, source, target, weight=weight)
            elif method == 'bellman-ford':
                path = nx.bellman_ford_path(G, source, target, weight=weight)
                length = nx.bellman_ford_path_length(G, source, target, weight=weight)
            elif method == 'astar':
                # Use geographic heuristic if coordinates available
                heuristic = self._geographic_heuristic if self._has_coordinates() else None
                path = nx.astar_path(G, source, target, heuristic=heuristic, weight=weight)
                length = sum(G[path[i]][path[i+1]].get(weight, 1) for i in range(len(path)-1))
            else:
                raise ValueError(f"Unknown method: {method}")
            
            edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            reliability = self._compute_path_reliability(edges)
            
            return PathResult(
                source=source,
                target=target,
                path=path,
                length=length,
                num_hops=len(path) - 1,
                edges=edges,
                reliability=reliability
            )
        
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def all_shortest_paths(
        self,
        source: str,
        target: str,
        weight: Optional[str] = 'weight'
    ) -> List[PathResult]:
        """Find all shortest paths between two nodes."""
        G = self.graph
        
        try:
            paths = list(nx.all_shortest_paths(G, source, target, weight=weight))
            
            results = []
            for path in paths:
                edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                length = sum(G[u][v].get(weight, 1) for u, v in edges)
                reliability = self._compute_path_reliability(edges)
                
                results.append(PathResult(
                    source=source,
                    target=target,
                    path=path,
                    length=length,
                    num_hops=len(path) - 1,
                    edges=edges,
                    reliability=reliability
                ))
            
            return results
        
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def k_shortest_paths(
        self,
        source: str,
        target: str,
        k: int = 5,
        weight: str = 'weight'
    ) -> List[PathResult]:
        """
        Find k shortest paths using Yen's algorithm.
        
        Args:
            source: Source node
            target: Target node
            k: Number of paths to find
            weight: Edge weight attribute
        
        Returns:
            List of k shortest paths
        """
        return self._yen_k_shortest_paths(source, target, k, weight)
    
    def _yen_k_shortest_paths(
        self,
        source: str,
        target: str,
        k: int,
        weight: str
    ) -> List[PathResult]:
        """Yen's algorithm for k shortest paths."""
        G = self.graph
        
        # Find initial shortest path
        initial_path = self.shortest_path(source, target, weight)
        if initial_path is None:
            return []
        
        paths = [initial_path]
        candidates = []
        
        for i in range(k - 1):
            for j in range(len(paths[-1].path) - 1):
                spur_node = paths[-1].path[j]
                root_path = paths[-1].path[:j + 1]
                
                # Remove edges from previous paths that share root path
                G_temp = G.copy()
                for p in paths:
                    if p.path[:j + 1] == root_path:
                        if j + 1 < len(p.path):
                            u, v = p.path[j], p.path[j + 1]
                            if G_temp.has_edge(u, v):
                                G_temp.remove_edge(u, v)
                
                # Remove root path nodes (except spur node)
                for node in root_path[:-1]:
                    if G_temp.has_node(node):
                        G_temp.remove_node(node)
                
                # Find spur path
                spur_path_result = self._shortest_path_in_graph(
                    G_temp, spur_node, target, weight
                )
                
                if spur_path_result:
                    total_path = root_path[:-1] + spur_path_result.path
                    total_edges = [(total_path[i], total_path[i+1]) 
                                   for i in range(len(total_path)-1)]
                    total_length = sum(G[u][v].get(weight, 1) for u, v in total_edges)
                    
                    # Check if path is unique
                    is_unique = all(p.path != total_path for p in paths)
                    is_new = all(c.path != total_path for c in candidates)
                    
                    if is_unique and is_new:
                        candidates.append(PathResult(
                            source=source,
                            target=target,
                            path=total_path,
                            length=total_length,
                            num_hops=len(total_path) - 1,
                            edges=total_edges,
                            reliability=self._compute_path_reliability(total_edges)
                        ))
            
            if not candidates:
                break
            
            # Select best candidate
            candidates.sort(key=lambda x: x.length)
            paths.append(candidates.pop(0))
        
        return paths
    
    def _shortest_path_in_graph(
        self,
        G: 'nx.Graph',
        source: str,
        target: str,
        weight: str
    ) -> Optional[PathResult]:
        """Find shortest path in a specific graph instance."""
        try:
            path = nx.dijkstra_path(G, source, target, weight=weight)
            edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            length = sum(G[u][v].get(weight, 1) for u, v in edges)
            
            return PathResult(
                source=source,
                target=target,
                path=path,
                length=length,
                num_hops=len(path) - 1,
                edges=edges,
                reliability=1.0
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def node_disjoint_paths(
        self,
        source: str,
        target: str,
        weight: Optional[str] = None
    ) -> MultiPathResult:
        """
        Find node-disjoint paths between source and target.
        
        Args:
            source: Source node
            target: Target node
            weight: Edge weight attribute
        
        Returns:
            MultiPathResult with node-disjoint paths
        """
        G = self.graph
        
        try:
            paths_iter = nx.node_disjoint_paths(G, source, target)
            paths_list = list(paths_iter)
            
            path_results = []
            for path in paths_list:
                edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                length = sum(G[u][v].get(weight, 1) for u, v in edges) if weight else len(edges)
                
                path_results.append(PathResult(
                    source=source,
                    target=target,
                    path=path,
                    length=length,
                    num_hops=len(path) - 1,
                    edges=edges,
                    reliability=self._compute_path_reliability(edges)
                ))
            
            min_cut = nx.minimum_node_cut(G, source, target)
            
            return MultiPathResult(
                source=source,
                target=target,
                paths=path_results,
                total_paths=len(path_results),
                node_disjoint_paths=len(path_results),
                edge_disjoint_paths=0,  # Would need separate calculation
                min_cut_size=len(min_cut)
            )
        
        except nx.NetworkXNoPath:
            return MultiPathResult(source, target, [], 0, 0, 0, 0)
    
    def edge_disjoint_paths(
        self,
        source: str,
        target: str,
        weight: Optional[str] = None
    ) -> MultiPathResult:
        """Find edge-disjoint paths between source and target."""
        G = self.graph
        
        try:
            paths_iter = nx.edge_disjoint_paths(G, source, target)
            paths_list = list(paths_iter)
            
            path_results = []
            for path in paths_list:
                edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                length = sum(G[u][v].get(weight, 1) for u, v in edges) if weight else len(edges)
                
                path_results.append(PathResult(
                    source=source,
                    target=target,
                    path=path,
                    length=length,
                    num_hops=len(path) - 1,
                    edges=edges,
                    reliability=self._compute_path_reliability(edges)
                ))
            
            min_cut = nx.minimum_edge_cut(G, source, target)
            
            return MultiPathResult(
                source=source,
                target=target,
                paths=path_results,
                total_paths=len(path_results),
                node_disjoint_paths=0,  # Would need separate calculation
                edge_disjoint_paths=len(path_results),
                min_cut_size=len(min_cut)
            )
        
        except nx.NetworkXNoPath:
            return MultiPathResult(source, target, [], 0, 0, 0, 0)
    
    def critical_path_analysis(
        self,
        source_groups: Dict[str, List[str]],
        target_groups: Dict[str, List[str]],
        weight: str = 'weight'
    ) -> pd.DataFrame:
        """
        Analyze critical paths between groups of nodes.
        
        Args:
            source_groups: Dictionary of source node groups
            target_groups: Dictionary of target node groups
            weight: Edge weight attribute
        
        Returns:
            DataFrame with critical path analysis
        """
        results = []
        
        for source_name, sources in source_groups.items():
            for target_name, targets in target_groups.items():
                paths_found = []
                total_length = 0
                min_length = float('inf')
                max_length = 0
                
                for source in sources:
                    for target in targets:
                        path = self.shortest_path(source, target, weight)
                        if path:
                            paths_found.append(path)
                            total_length += path.length
                            min_length = min(min_length, path.length)
                            max_length = max(max_length, path.length)
                
                if paths_found:
                    avg_length = total_length / len(paths_found)
                    
                    # Find most critical edges (appear in many shortest paths)
                    edge_counts = defaultdict(int)
                    for p in paths_found:
                        for edge in p.edges:
                            edge_counts[edge] += 1
                    
                    most_critical_edge = max(edge_counts.items(), key=lambda x: x[1])
                    
                    results.append({
                        'source_group': source_name,
                        'target_group': target_name,
                        'num_paths': len(paths_found),
                        'avg_path_length': avg_length,
                        'min_path_length': min_length,
                        'max_path_length': max_length,
                        'most_critical_edge': most_critical_edge[0],
                        'critical_edge_frequency': most_critical_edge[1]
                    })
        
        return pd.DataFrame(results)
    
    def _compute_path_reliability(self, edges: List[Tuple[str, str]]) -> float:
        """Compute reliability of a path given its edges."""
        G = self.graph
        reliability = 1.0
        
        for u, v in edges:
            if G.has_edge(u, v):
                edge_reliability = G[u][v].get('reliability', 0.95)
                reliability *= edge_reliability
        
        return reliability
    
    def _has_coordinates(self) -> bool:
        """Check if nodes have coordinate attributes."""
        G = self.graph
        if G.number_of_nodes() == 0:
            return False
        
        first_node = list(G.nodes())[0]
        return 'latitude' in G.nodes[first_node] and 'longitude' in G.nodes[first_node]
    
    def _geographic_heuristic(self, u: str, v: str) -> float:
        """A* heuristic using geographic distance."""
        G = self.graph
        
        if not self._has_coordinates():
            return 0
        
        lat1 = G.nodes[u].get('latitude', 0)
        lon1 = G.nodes[u].get('longitude', 0)
        lat2 = G.nodes[v].get('latitude', 0)
        lon2 = G.nodes[v].get('longitude', 0)
        
        # Haversine distance
        R = 6371
        lat1_rad, lon1_rad = np.radians([lat1, lon1])
        lat2_rad, lon2_rad = np.radians([lat2, lon2])
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
        return R * 2 * np.arcsin(np.sqrt(a))


def compute_all_pairs_shortest_paths(
    graph: 'nx.Graph',
    weight: str = 'weight',
    cutoff: Optional[float] = None
) -> Dict[Tuple[str, str], float]:
    """
    Compute all-pairs shortest paths efficiently.
    
    Args:
        graph: NetworkX graph
        weight: Edge weight attribute
        cutoff: Maximum path length to consider
    
    Returns:
        Dictionary mapping (source, target) to path length
    """
    lengths = dict(nx.all_pairs_dijkstra_path_length(graph, weight=weight, cutoff=cutoff))
    
    # Flatten to single dictionary
    all_lengths = {}
    for source, targets in lengths.items():
        for target, length in targets.items():
            if source != target:
                all_lengths[(source, target)] = length
    
    return all_lengths


---

## 7. Network Resilience Metrics

### 7.1 Comprehensive Resilience Analysis

**File:** `src/network/analysis/resilience.py`

```python
"""
ResilienceAI - Network Resilience Metrics
Comprehensive resilience assessment for infrastructure networks.
"""
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from scipy import stats

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class ResilienceDimension(Enum):
    """Dimensions of network resilience."""
    ROBUSTNESS = "robustness"
    REDUNDANCY = "redundancy"
    RESOURCEFULNESS = "resourcefulness"
    RAPIDITY = "rapidity"
    ADAPTABILITY = "adaptability"


@dataclass
class ResilienceScore:
    """Resilience score for a specific dimension."""
    dimension: ResilienceDimension
    score: float  # 0-1 scale
    confidence: float  # 0-1 scale
    contributing_metrics: Dict[str, float]
    interpretation: str


@dataclass
class RobustnessProfile:
    """Network robustness profile under various attack scenarios."""
    random_attack_curve: List[Tuple[float, float]]  # (fraction_removed, giant_component_size)
    targeted_attack_curve: List[Tuple[float, float]]
    degree_attack_curve: List[Tuple[float, float]]
    betweenness_attack_curve: List[Tuple[float, float]]
    robustness_integral: float
    critical_threshold: float


class ResilienceAnalyzer:
    """Comprehensive resilience analysis for infrastructure networks."""
    
    def __init__(self, graph: 'nx.Graph'):
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required")
        self.graph = graph
        self._original_graph = graph.copy()
    
    def compute_resilience_profile(
        self,
        attack_fractions: np.ndarray = np.linspace(0, 0.5, 21)
    ) -> Dict[ResilienceDimension, ResilienceScore]:
        """
        Compute comprehensive resilience profile across all dimensions.
        
        Args:
            attack_fractions: Fractions of nodes to remove for robustness testing
        
        Returns:
            Dictionary mapping resilience dimensions to scores
        """
        profile = {}
        
        # Robustness
        profile[ResilienceDimension.ROBUSTNESS] = self._assess_robustness(attack_fractions)
        
        # Redundancy
        profile[ResilienceDimension.REDUNDANCY] = self._assess_redundancy()
        
        # Resourcefulness
        profile[ResilienceDimension.RESOURCEFULNESS] = self._assess_resourcefulness()
        
        # Rapidity
        profile[ResilienceDimension.RAPIDITY] = self._assess_rapidity()
        
        # Adaptability
        profile[ResilienceDimension.ADAPTABILITY] = self._assess_adaptability()
        
        return profile
    
    def _assess_robustness(
        self,
        attack_fractions: np.ndarray
    ) -> ResilienceScore:
        """Assess network robustness under attacks."""
        G = self.graph
        n = G.number_of_nodes()
        
        # Random attack
        random_curve = []
        for f in attack_fractions:
            G_temp = G.copy()
            nodes_to_remove = int(n * f)
            removed = np.random.choice(list(G_temp.nodes()), 
                                      size=min(nodes_to_remove, G_temp.number_of_nodes()),
                                      replace=False)
            G_temp.remove_nodes_from(removed)
            
            if G_temp.number_of_nodes() > 0:
                giant_size = len(max(nx.connected_components(G_temp), key=len))
                random_curve.append((f, giant_size / n))
            else:
                random_curve.append((f, 0))
        
        # Targeted attack (highest degree)
        degree_curve = []
        degrees = dict(G.degree())
        sorted_nodes = sorted(degrees.keys(), key=lambda x: degrees[x], reverse=True)
        
        for f in attack_fractions:
            nodes_to_remove = int(n * f)
            removed = set(sorted_nodes[:nodes_to_remove])
            
            G_temp = G.copy()
            G_temp.remove_nodes_from(removed)
            
            if G_temp.number_of_nodes() > 0:
                giant_size = len(max(nx.connected_components(G_temp), key=len))
                degree_curve.append((f, giant_size / n))
            else:
                degree_curve.append((f, 0))
        
        # Compute robustness integral (area under curve)
        random_integral = np.trapz([y for _, y in random_curve], 
                                   [x for x, _ in random_curve])
        degree_integral = np.trapz([y for _, y in degree_curve],
                                   [x for x, _ in degree_curve])
        
        # Critical threshold (where giant component drops below 50%)
        critical_threshold = 0.5
        for f, size in degree_curve:
            if size < 0.5:
                critical_threshold = f
                break
        
        # Score calculation
        robustness_score = (random_integral + degree_integral) / 2
        
        contributing = {
            'random_attack_robustness': random_integral,
            'targeted_attack_robustness': degree_integral,
            'critical_threshold': critical_threshold
        }
        
        interpretation = (
            f"Robustness score: {robustness_score:.3f}. "
            f"Network maintains {random_integral:.1%} connectivity under random attacks. "
            f"Critical threshold at {critical_threshold:.1%} node removal."
        )
        
        return ResilienceScore(
            dimension=ResilienceDimension.ROBUSTNESS,
            score=robustness_score,
            confidence=0.85,
            contributing_metrics=contributing,
            interpretation=interpretation
        )
    
    def _assess_redundancy(self) -> ResilienceScore:
        """Assess network redundancy through alternative paths."""
        G = self.graph
        
        # Average node connectivity
        try:
            avg_connectivity = nx.average_node_connectivity(G)
        except:
            avg_connectivity = 1.0
        
        # Edge connectivity statistics
        edge_connectivities = []
        nodes = list(G.nodes())
        sample_size = min(100, len(nodes) * (len(nodes) - 1) // 2)
        
        import random
        random.seed(42)
        pairs = [(u, v) for i, u in enumerate(nodes) for v in nodes[i+1:]]
        sampled_pairs = random.sample(pairs, min(sample_size, len(pairs)))
        
        for u, v in sampled_pairs:
            try:
                conn = nx.node_connectivity(G, u, v)
                edge_connectivities.append(conn)
            except:
                pass
        
        avg_edge_conn = np.mean(edge_connectivities) if edge_connectivities else 1.0
        
        # Redundancy ratio (alternative paths / direct connections)
        redundancy_ratio = avg_connectivity / max(avg_edge_conn, 1e-6)
        
        # Score calculation
        redundancy_score = min(avg_connectivity / 5.0, 1.0)  # Normalize to 5 as max
        
        contributing = {
            'average_node_connectivity': avg_connectivity,
            'average_edge_connectivity': avg_edge_conn,
            'redundancy_ratio': redundancy_ratio
        }
        
        interpretation = (
            f"Redundancy score: {redundancy_score:.3f}. "
            f"Average of {avg_connectivity:.2f} node-independent paths. "
            f"Network has {'high' if redundancy_score > 0.7 else 'moderate' if redundancy_score > 0.4 else 'low'} redundancy."
        )
        
        return ResilienceScore(
            dimension=ResilienceDimension.REDUNDANCY,
            score=redundancy_score,
            confidence=0.80,
            contributing_metrics=contributing,
            interpretation=interpretation
        )
    
    def _assess_resourcefulness(self) -> ResilienceScore:
        """Assess network resourcefulness (available capacity)."""
        G = self.graph
        
        # Node capacity utilization
        node_utilizations = []
        for node in G.nodes():
            capacity = G.nodes[node].get('capacity', 1.0)
            load = G.nodes[node].get('current_load', 0.0)
            utilization = load / capacity if capacity > 0 else 1.0
            node_utilizations.append(utilization)
        
        avg_node_util = np.mean(node_utilizations) if node_utilizations else 0.5
        spare_capacity = 1.0 - avg_node_util
        
        # Edge capacity utilization
        edge_utilizations = []
        for u, v in G.edges():
            capacity = G[u][v].get('capacity', 1.0)
            load = G[u][v].get('current_load', 0.0)
            utilization = load / capacity if capacity > 0 else 1.0
            edge_utilizations.append(utilization)
        
        avg_edge_util = np.mean(edge_utilizations) if edge_utilizations else 0.5
        spare_edge_capacity = 1.0 - avg_edge_util
        
        # Score calculation
        resourcefulness_score = (spare_capacity + spare_edge_capacity) / 2
        
        contributing = {
            'average_node_utilization': avg_node_util,
            'average_edge_utilization': avg_edge_util,
            'spare_node_capacity': spare_capacity,
            'spare_edge_capacity': spare_edge_capacity
        }
        
        interpretation = (
            f"Resourcefulness score: {resourcefulness_score:.3f}. "
            f"Nodes at {avg_node_util:.1%} capacity, edges at {avg_edge_util:.1%} capacity. "
            f"{'Abundant' if resourcefulness_score > 0.7 else 'Limited' if resourcefulness_score < 0.3 else 'Moderate'} spare capacity available."
        )
        
        return ResilienceScore(
            dimension=ResilienceDimension.RESOURCEFULNESS,
            score=resourcefulness_score,
            confidence=0.75,
            contributing_metrics=contributing,
            interpretation=interpretation
        )
    
    def _assess_rapidity(self) -> ResilienceScore:
        """Assess network rapidity (speed of recovery)."""
        G = self.graph
        
        # Diameter-based metric (smaller = faster recovery)
        if nx.is_connected(G):
            diameter = nx.diameter(G)
            radius = nx.radius(G)
        else:
            largest = max(nx.connected_components(G), key=len)
            subgraph = G.subgraph(largest)
            diameter = nx.diameter(subgraph)
            radius = nx.radius(subgraph)
        
        # Average shortest path length
        avg_path_length = nx.average_shortest_path_length(G) if nx.is_connected(G) else diameter / 2
        
        # Rapidity score (inverse of characteristic path length)
        rapidity_score = 1.0 / (1.0 + avg_path_length / 10.0)
        
        contributing = {
            'network_diameter': diameter,
            'network_radius': radius,
            'average_path_length': avg_path_length
        }
        
        interpretation = (
            f"Rapidity score: {rapidity_score:.3f}. "
            f"Network diameter: {diameter}, average path: {avg_path_length:.2f}. "
            f"{'Fast' if rapidity_score > 0.7 else 'Slow' if rapidity_score < 0.3 else 'Moderate'} information/resource flow."
        )
        
        return ResilienceScore(
            dimension=ResilienceDimension.RAPIDITY,
            score=rapidity_score,
            confidence=0.70,
            contributing_metrics=contributing,
            interpretation=interpretation
        )
    
    def _assess_adaptability(self) -> ResilienceScore:
        """Assess network adaptability (ability to reconfigure)."""
        G = self.graph
        
        # Clustering coefficient (local adaptability)
        avg_clustering = nx.average_clustering(G)
        
        # Transitivity (global adaptability)
        transitivity = nx.transitivity(G)
        
        # Number of alternative paths
        adaptability_score = (avg_clustering + transitivity) / 2
        
        contributing = {
            'average_clustering': avg_clustering,
            'transitivity': transitivity,
            'triadic_closure': transitivity
        }
        
        interpretation = (
            f"Adaptability score: {adaptability_score:.3f}. "
            f"Clustering: {avg_clustering:.3f}, Transitivity: {transitivity:.3f}. "
            f"Network has {'high' if adaptability_score > 0.7 else 'low' if adaptability_score < 0.3 else 'moderate'} reconfiguration potential."
        )
        
        return ResilienceScore(
            dimension=ResilienceDimension.ADAPTABILITY,
            score=adaptability_score,
            confidence=0.65,
            contributing_metrics=contributing,
            interpretation=interpretation
        )
    
    def compute_integrated_resilience_index(self) -> float:
        """
        Compute integrated resilience index across all dimensions.
        
        Returns:
            Integrated resilience score (0-1)
        """
        profile = self.compute_resilience_profile()
        
        # Weighted average of dimensions
        weights = {
            ResilienceDimension.ROBUSTNESS: 0.30,
            ResilienceDimension.REDUNDANCY: 0.25,
            ResilienceDimension.RESOURCEFULNESS: 0.20,
            ResilienceDimension.RAPIDITY: 0.15,
            ResilienceDimension.ADAPTABILITY: 0.10
        }
        
        integrated_score = sum(
            profile[dim].score * weights[dim]
            for dim in ResilienceDimension
        )
        
        return integrated_score
    
    def percolation_analysis(
        self,
        num_simulations: int = 100,
        occupation_probs: np.ndarray = np.linspace(0, 1, 21)
    ) -> Dict[str, Any]:
        """
        Perform bond and site percolation analysis.
        
        Args:
            num_simulations: Number of Monte Carlo simulations
            occupation_probs: Probabilities to test
        
        Returns:
            Percolation analysis results
        """
        G = self.graph
        n = G.number_of_nodes()
        m = G.number_of_edges()
        
        # Site percolation
        site_percolation = []
        for p in occupation_probs:
            giant_sizes = []
            for _ in range(num_simulations):
                G_temp = G.copy()
                # Remove nodes with probability (1-p)
                nodes_to_remove = [node for node in G_temp.nodes() 
                                  if np.random.random() > p]
                G_temp.remove_nodes_from(nodes_to_remove)
                
                if G_temp.number_of_nodes() > 0:
                    giant_size = len(max(nx.connected_components(G_temp), key=len))
                    giant_sizes.append(giant_size / n)
                else:
                    giant_sizes.append(0)
            
            site_percolation.append({
                'occupation_prob': p,
                'mean_giant_size': np.mean(giant_sizes),
                'std_giant_size': np.std(giant_sizes)
            })
        
        # Find percolation threshold
        percolation_threshold = 0.5
        for result in site_percolation:
            if result['mean_giant_size'] > 0.5:
                percolation_threshold = result['occupation_prob']
                break
        
        return {
            'site_percolation': site_percolation,
            'percolation_threshold': percolation_threshold,
            'critical_probability': percolation_threshold,
            'num_simulations': num_simulations
        }


def compare_resilience(
    graph1: 'nx.Graph',
    graph2: 'nx.Graph'
) -> Dict[str, Any]:
    """
    Compare resilience between two networks.
    
    Args:
        graph1: First graph
        graph2: Second graph
    
    Returns:
        Comparison results
    """
    analyzer1 = ResilienceAnalyzer(graph1)
    analyzer2 = ResilienceAnalyzer(graph2)
    
    profile1 = analyzer1.compute_resilience_profile()
    profile2 = analyzer2.compute_resilience_profile()
    
    comparison = {}
    
    for dim in ResilienceDimension:
        score1 = profile1[dim].score
        score2 = profile2[dim].score
        
        comparison[dim.value] = {
            'graph1_score': score1,
            'graph2_score': score2,
            'difference': score1 - score2,
            'ratio': score1 / score2 if score2 > 0 else float('inf'),
            'more_resilient': 'graph1' if score1 > score2 else 'graph2' if score2 > score1 else 'equal'
        }
    
    # Integrated index comparison
    integrated1 = analyzer1.compute_integrated_resilience_index()
    integrated2 = analyzer2.compute_integrated_resilience_index()
    
    comparison['integrated_resilience_index'] = {
        'graph1': integrated1,
        'graph2': integrated2,
        'difference': integrated1 - integrated2,
        'more_resilient': 'graph1' if integrated1 > integrated2 else 'graph2'
    }
    
    return comparison
```

---

## 8. Cascading Failure Modeling

### 8.1 Advanced Cascade Simulation

**File:** `src/network/simulation/cascade_failure.py`

```python
"""
ResilienceAI - Cascading Failure Simulation
Advanced models for cascading failure in infrastructure networks.
"""
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class CascadeModel(Enum):
    """Types of cascading failure models."""
    LOAD_REDISTRIBUTION = "load_redistribution"  # Classic load redistribution
    EPIDEMIC = "epidemic"  # Epidemic-style spreading
    PERCOLATION = "percolation"  # Percolation-based
    SANDPILE = "sandpile"  # Self-organized criticality
    CAPACITY_OVERLOAD = "capacity_overload"  # Capacity-based failure


@dataclass
class CascadeStep:
    """Single step in cascade progression."""
    step_number: int
    newly_failed: List[str]
    failed_load: float
    redistributed_load: float
    network_efficiency: float
    giant_component_size: int


@dataclass
class CascadeResult:
    """Complete cascade simulation result."""
    model: CascadeModel
    initial_failure: List[str]
    total_steps: int
    final_failed: Set[str]
    final_functional: Set[str]
    cascade_steps: List[CascadeStep]
    total_impact: float
    cascade_size_distribution: Dict[int, int]
    critical_nodes: List[str]
    recovery_recommendations: List[str]


class LoadRedistributionCascade:
    """
    Load redistribution cascade model.
    
    Based on the classic model where failed node load is redistributed
    to neighbors proportionally to their capacity.
    """
    
    def __init__(
        self,
        graph: 'nx.Graph',
        tolerance_parameter: float = 1.0,
        redistribution_rule: str = 'proportional'
    ):
        self.original_graph = graph.copy()
        self.tolerance_parameter = tolerance_parameter
        self.redistribution_rule = redistribution_rule
        self._initialize_loads()
    
    def _initialize_loads(self):
        """Initialize node loads and capacities."""
        G = self.original_graph
        
        for node in G.nodes():
            # Default capacity
            if 'capacity' not in G.nodes[node]:
                G.nodes[node]['capacity'] = 1.0
            
            # Initial load based on degree (can be customized)
            if 'initial_load' not in G.nodes[node]:
                degree = G.degree(node)
                G.nodes[node]['initial_load'] = degree * 0.1
            
            G.nodes[node]['current_load'] = G.nodes[node]['initial_load']
            G.nodes[node]['failed'] = False
    
    def simulate(
        self,
        initial_failures: List[str],
        max_steps: int = 100,
        early_stop: bool = True
    ) -> CascadeResult:
        """
        Simulate cascading failure.
        
        Args:
            initial_failures: List of initially failing nodes
            max_steps: Maximum simulation steps
            early_stop: Stop if no new failures
        
        Returns:
            CascadeResult with full simulation details
        """
        G = self.original_graph.copy()
        failed = set(initial_failures)
        cascade_steps = []
        
        # Mark initial failures
        for node in initial_failures:
            if node in G:
                G.nodes[node]['failed'] = True
        
        for step in range(max_steps):
            newly_failed = self._cascade_step(G, failed)
            
            if not newly_failed and early_stop:
                break
            
            failed.update(newly_failed)
            
            # Record step
            step_result = CascadeStep(
                step_number=step,
                newly_failed=list(newly_failed),
                failed_load=sum(G.nodes[n]['current_load'] for n in newly_failed if n in G),
                redistributed_load=self._compute_redistributed_load(G, newly_failed),
                network_efficiency=self._compute_network_efficiency(G, failed),
                giant_component_size=self._giant_component_size(G, failed)
            )
            cascade_steps.append(step_result)
        
        # Analyze results
        final_failed = failed
        final_functional = set(G.nodes()) - failed
        
        return CascadeResult(
            model=CascadeModel.LOAD_REDISTRIBUTION,
            initial_failure=initial_failures,
            total_steps=len(cascade_steps),
            final_failed=final_failed,
            final_functional=final_functional,
            cascade_steps=cascade_steps,
            total_impact=len(final_failed) / G.number_of_nodes(),
            cascade_size_distribution=self._size_distribution(cascade_steps),
            critical_nodes=self._identify_critical_nodes(G, cascade_steps),
            recovery_recommendations=self._generate_recommendations(G, cascade_steps)
        )
    
    def _cascade_step(self, G: 'nx.Graph', already_failed: Set[str]) -> Set[str]:
        """Execute one cascade step."""
        newly_failed = set()
        
        # Redistribute load from failed nodes
        for failed_node in already_failed:
            if failed_node not in G:
                continue
            
            neighbors = list(G.neighbors(failed_node))
            if not neighbors:
                continue
            
            failed_load = G.nodes[failed_node].get('current_load', 0)
            
            # Calculate redistribution
            if self.redistribution_rule == 'proportional':
                total_capacity = sum(
                    G.nodes[n].get('capacity', 1) for n in neighbors 
                    if n not in already_failed
                )
                
                for neighbor in neighbors:
                    if neighbor in already_failed:
                        continue
                    
                    neighbor_capacity = G.nodes[neighbor].get('capacity', 1)
                    share = (neighbor_capacity / total_capacity) * failed_load if total_capacity > 0 else 0
                    G.nodes[neighbor]['current_load'] += share
                    
                    # Check for failure
                    capacity = G.nodes[neighbor].get('capacity', 1)
                    tolerance = capacity * self.tolerance_parameter
                    
                    if G.nodes[neighbor]['current_load'] > tolerance:
                        newly_failed.add(neighbor)
                        G.nodes[neighbor]['failed'] = True
        
        return newly_failed
    
    def _compute_redistributed_load(self, G: 'nx.Graph', newly_failed: Set[str]) -> float:
        """Compute total redistributed load."""
        return sum(G.nodes[n].get('current_load', 0) for n in newly_failed if n in G)
    
    def _compute_network_efficiency(self, G: 'nx.Graph', failed: Set[str]) -> float:
        """Compute network efficiency after failures."""
        functional = [n for n in G.nodes() if n not in failed]
        if len(functional) < 2:
            return 0.0
        
        subgraph = G.subgraph(functional)
        if subgraph.number_of_edges() == 0:
            return 0.0
        
        try:
            return nx.global_efficiency(subgraph)
        except:
            return 0.0
    
    def _giant_component_size(self, G: 'nx.Graph', failed: Set[str]) -> int:
        """Get size of largest connected component."""
        functional = [n for n in G.nodes() if n not in failed]
        if not functional:
            return 0
        
        subgraph = G.subgraph(functional)
        if subgraph.number_of_nodes() == 0:
            return 0
        
        return len(max(nx.connected_components(subgraph), key=len))
    
    def _size_distribution(self, cascade_steps: List[CascadeStep]) -> Dict[int, int]:
        """Compute cascade size distribution."""
        sizes = [len(step.newly_failed) for step in cascade_steps]
        distribution = defaultdict(int)
        for size in sizes:
            distribution[size] += 1
        return dict(distribution)
    
    def _identify_critical_nodes(
        self,
        G: 'nx.Graph',
        cascade_steps: List[CascadeStep]
    ) -> List[str]:
        """Identify critical nodes that triggered cascades."""
        # Nodes that caused many subsequent failures
        node_impact = defaultdict(int)
        
        for i, step in enumerate(cascade_steps):
            for node in step.newly_failed:
                # Count subsequent failures
                subsequent = sum(len(cascade_steps[j].newly_failed) 
                               for j in range(i+1, len(cascade_steps)))
                node_impact[node] = subsequent
        
        # Return top critical nodes
        sorted_nodes = sorted(node_impact.items(), key=lambda x: x[1], reverse=True)
        return [node for node, _ in sorted_nodes[:10]]
    
    def _generate_recommendations(
        self,
        G: 'nx.Graph',
        cascade_steps: List[CascadeStep]
    ) -> List[str]:
        """Generate recovery recommendations."""
        recommendations = []
        
        if not cascade_steps:
            return ["No cascade occurred - network is stable"]
        
        # Analyze cascade pattern
        total_failed = sum(len(step.newly_failed) for step in cascade_steps)
        
        if total_failed > G.number_of_nodes() * 0.5:
            recommendations.append(
                "CRITICAL: Large-scale cascade detected. Implement immediate load shedding."
            )
        
        # Check for early saturation
        if len(cascade_steps) > 0 and len(cascade_steps[0].newly_failed) > 10:
            recommendations.append(
                "Rapid initial cascade suggests critical hub failure. Consider redundancy upgrades."
            )
        
        # Capacity recommendations
        avg_load_increase = np.mean([
            step.redistributed_load / max(len(step.newly_failed), 1)
            for step in cascade_steps
        ]) if cascade_steps else 0
        
        if avg_load_increase > 0.5:
            recommendations.append(
                f"High load redistribution ({avg_load_increase:.2f}). Increase node capacities."
            )
        
        recommendations.append(
            f"Total impact: {total_failed} nodes ({total_failed/G.number_of_nodes():.1%})"
        )
        
        return recommendations


class EpidemicCascade:
    """
    Epidemic-style cascade model.
    
    Models failure spreading like an epidemic with infection probability.
    """
    
    def __init__(
        self,
        graph: 'nx.Graph',
        infection_prob: float = 0.3,
        recovery_prob: float = 0.1,
        immunization_prob: float = 0.0
    ):
        self.graph = graph
        self.infection_prob = infection_prob
        self.recovery_prob = recovery_prob
        self.immunization_prob = immunization_prob
    
    def simulate(
        self,
        initial_infected: List[str],
        max_steps: int = 100
    ) -> CascadeResult:
        """Simulate epidemic cascade."""
        G = self.graph
        
        infected = set(initial_infected)
        recovered = set()
        susceptible = set(G.nodes()) - infected
        
        cascade_steps = []
        
        for step in range(max_steps):
            newly_infected = set()
            newly_recovered = set()
            
            # Infection phase
            for node in susceptible:
                neighbors = set(G.neighbors(node))
                infected_neighbors = neighbors & infected
                
                # SIS model: infection probability increases with infected neighbors
                prob = 1 - (1 - self.infection_prob) ** len(infected_neighbors)
                
                if np.random.random() < prob:
                    newly_infected.add(node)
            
            # Recovery phase
            for node in infected:
                if np.random.random() < self.recovery_prob:
                    newly_recovered.add(node)
            
            # Update sets
            infected = (infected - newly_recovered) | newly_infected
            susceptible = susceptible - newly_infected
            recovered = recovered | newly_recovered
            
            # Record step
            cascade_steps.append(CascadeStep(
                step_number=step,
                newly_failed=list(newly_infected),
                failed_load=len(newly_infected),
                redistributed_load=0,
                network_efficiency=1 - len(infected) / G.number_of_nodes(),
                giant_component_size=G.number_of_nodes() - len(infected)
            ))
            
            # Stop if no change
            if not newly_infected and not newly_recovered:
                break
        
        return CascadeResult(
            model=CascadeModel.EPIDEMIC,
            initial_failure=initial_infected,
            total_steps=len(cascade_steps),
            final_failed=infected,
            final_functional=susceptible | recovered,
            cascade_steps=cascade_steps,
            total_impact=len(infected) / G.number_of_nodes(),
            cascade_size_distribution={},
            critical_nodes=list(initial_infected),
            recovery_recommendations=[
                f"Epidemic cascade with R0 approx {self.infection_prob/self.recovery_prob:.2f}"
            ]
        )


class CascadeSimulator:
    """Unified interface for cascade simulation."""
    
    def __init__(self, graph: 'nx.Graph'):
        self.graph = graph
        self.models = {
            CascadeModel.LOAD_REDISTRIBUTION: LoadRedistributionCascade,
            CascadeModel.EPIDEMIC: EpidemicCascade,
        }
    
    def simulate(
        self,
        model: CascadeModel,
        initial_failures: List[str],
        **model_params
    ) -> CascadeResult:
        """
        Simulate cascade with specified model.
        
        Args:
            model: Cascade model to use
            initial_failures: Initially failing nodes
            **model_params: Model-specific parameters
        
        Returns:
            CascadeResult
        """
        model_class = self.models.get(model)
        if model_class is None:
            raise ValueError(f"Unknown cascade model: {model}")
        
        simulator = model_class(self.graph, **model_params)
        return simulator.simulate(initial_failures)
    
    def compare_models(
        self,
        initial_failures: List[str],
        models: Optional[List[CascadeModel]] = None
    ) -> Dict[CascadeModel, CascadeResult]:
        """
        Compare different cascade models.
        
        Args:
            initial_failures: Initially failing nodes
            models: List of models to compare
        
        Returns:
            Dictionary mapping models to results
        """
        if models is None:
            models = list(self.models.keys())
        
        results = {}
        for model in models:
            try:
                results[model] = self.simulate(model, initial_failures)
            except Exception as e:
                print(f"Error simulating {model}: {e}")
        
        return results
    
    def vulnerability_scan(
        self,
        model: CascadeModel = CascadeModel.LOAD_REDISTRIBUTION,
        top_k: int = 10
    ) -> pd.DataFrame:
        """
        Scan all nodes for cascade vulnerability.
        
        Args:
            model: Cascade model to use
            top_k: Number of most vulnerable nodes to return
        
        Returns:
            DataFrame with vulnerability scores
        """
        G = self.graph
        results = []
        
        for node in G.nodes():
            cascade = self.simulate(model, [node])
            
            results.append({
                'node': node,
                'cascade_size': len(cascade.final_failed),
                'cascade_impact': cascade.total_impact,
                'num_steps': cascade.total_steps,
                'final_efficiency': cascade.cascade_steps[-1].network_efficiency if cascade.cascade_steps else 1.0
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('cascade_impact', ascending=False)
        
        return df.head(top_k)
```

---

## 9. Community Detection Module

### 9.1 Community Detection Algorithms

**File:** `src/network/analysis/communities.py`

```python
"""
ResilienceAI - Community Detection
Community detection algorithms for infrastructure network clustering.
"""
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    import community as community_louvain
    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False


class CommunityAlgorithm(Enum):
    """Community detection algorithms."""
    LOUVAIN = "louvain"
    GREEDY_MODULARITY = "greedy_modularity"
    LABEL_PROPAGATION = "label_propagation"
    ASYN_LPA = "asyn_lpa"
    K_CLIQUE = "k_clique"
    GIRVAN_NEWMAN = "girvan_newman"
    SPECTRAL = "spectral"


@dataclass
class CommunityResult:
    """Result container for community detection."""
    algorithm: CommunityAlgorithm
    communities: Dict[int, List[str]]
    node_assignments: Dict[str, int]
    modularity: float
    num_communities: int
    community_sizes: List[int]
    silhouette_score: Optional[float] = None


class CommunityDetector:
    """Community detection for infrastructure networks."""
    
    def __init__(self, graph: 'nx.Graph'):
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required")
        self.graph = graph
    
    def detect_communities(
        self,
        algorithm: CommunityAlgorithm = CommunityAlgorithm.LOUVAIN,
        **params
    ) -> CommunityResult:
        """
        Detect communities using specified algorithm.
        
        Args:
            algorithm: Community detection algorithm
            **params: Algorithm-specific parameters
        
        Returns:
            CommunityResult
        """
        if algorithm == CommunityAlgorithm.LOUVAIN:
            return self._louvain(**params)
        elif algorithm == CommunityAlgorithm.GREEDY_MODULARITY:
            return self._greedy_modularity(**params)
        elif algorithm == CommunityAlgorithm.LABEL_PROPAGATION:
            return self._label_propagation(**params)
        elif algorithm == CommunityAlgorithm.ASYN_LPA:
            return self._asyn_lpa(**params)
        elif algorithm == CommunityAlgorithm.K_CLIQUE:
            return self._k_clique(**params)
        elif algorithm == CommunityAlgorithm.GIRVAN_NEWMAN:
            return self._girvan_newman(**params)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def _louvain(
        self,
        weight: str = 'weight',
        resolution: float = 1.0,
        random_state: int = 42
    ) -> CommunityResult:
        """Louvain community detection."""
        if not HAS_LOUVAIN:
            # Fallback to greedy modularity
            return self._greedy_modularity(weight)
        
        partition = community_louvain.best_partition(
            self.graph,
            weight=weight,
            resolution=resolution,
            random_state=random_state
        )
        
        # Convert to communities dict
        communities = defaultdict(list)
        for node, comm_id in partition.items():
            communities[comm_id].append(node)
        
        modularity = community_louvain.modularity(
            partition, self.graph, weight=weight
        )
        
        return CommunityResult(
            algorithm=CommunityAlgorithm.LOUVAIN,
            communities=dict(communities),
            node_assignments=partition,
            modularity=modularity,
            num_communities=len(communities),
            community_sizes=[len(c) for c in communities.values()]
        )
    
    def _greedy_modularity(self, weight: str = 'weight') -> CommunityResult:
        """Greedy modularity maximization."""
        communities = nx.community.greedy_modularity_communities(
            self.graph, weight=weight
        )
        
        # Convert to dict format
        comm_dict = {i: list(c) for i, c in enumerate(communities)}
        node_assignments = {}
        for comm_id, nodes in comm_dict.items():
            for node in nodes:
                node_assignments[node] = comm_id
        
        # Compute modularity
        modularity = nx.community.modularity(
            self.graph, communities, weight=weight
        )
        
        return CommunityResult(
            algorithm=CommunityAlgorithm.GREEDY_MODULARITY,
            communities=comm_dict,
            node_assignments=node_assignments,
            modularity=modularity,
            num_communities=len(comm_dict),
            community_sizes=[len(c) for c in comm_dict.values()]
        )
    
    def _label_propagation(self) -> CommunityResult:
        """Label propagation algorithm."""
        communities = nx.community.label_propagation_communities(self.graph)
        
        comm_dict = {i: list(c) for i, c in enumerate(communities)}
        node_assignments = {}
        for comm_id, nodes in comm_dict.items():
            for node in nodes:
                node_assignments[node] = comm_id
        
        # Compute modularity
        comm_sets = [set(c) for c in comm_dict.values()]
        modularity = nx.community.modularity(self.graph, comm_sets)
        
        return CommunityResult(
            algorithm=CommunityAlgorithm.LABEL_PROPAGATION,
            communities=comm_dict,
            node_assignments=node_assignments,
            modularity=modularity,
            num_communities=len(comm_dict),
            community_sizes=[len(c) for c in comm_dict.values()]
        )
    
    def _asyn_lpa(self) -> CommunityResult:
        """Asynchronous label propagation."""
        communities = nx.community.asyn_lpa_communities(self.graph)
        
        comm_dict = {i: list(c) for i, c in enumerate(communities)}
        node_assignments = {}
        for comm_id, nodes in comm_dict.items():
            for node in nodes:
                node_assignments[node] = comm_id
        
        comm_sets = [set(c) for c in comm_dict.values()]
        modularity = nx.community.modularity(self.graph, comm_sets)
        
        return CommunityResult(
            algorithm=CommunityAlgorithm.ASYN_LPA,
            communities=comm_dict,
            node_assignments=node_assignments,
            modularity=modularity,
            num_communities=len(comm_dict),
            community_sizes=[len(c) for c in comm_dict.values()]
        )
    
    def _k_clique(self, k: int = 3) -> CommunityResult:
        """K-clique percolation."""
        communities = list(nx.community.k_clique_communities(self.graph, k))
        
        comm_dict = {i: list(c) for i, c in enumerate(communities)}
        node_assignments = {}
        for comm_id, nodes in comm_dict.items():
            for node in nodes:
                node_assignments[node] = comm_id
        
        comm_sets = [set(c) for c in comm_dict.values()]
        modularity = nx.community.modularity(self.graph, comm_sets)
        
        return CommunityResult(
            algorithm=CommunityAlgorithm.K_CLIQUE,
            communities=comm_dict,
            node_assignments=node_assignments,
            modularity=modularity,
            num_communities=len(comm_dict),
            community_sizes=[len(c) for c in comm_dict.values()]
        )
    
    def _girvan_newman(self, k: int = 5) -> CommunityResult:
        """Girvan-Newman algorithm."""
        comp = nx.community.girvan_newman(self.graph)
        
        # Get k communities
        for _ in range(k - 1):
            try:
                next(comp)
            except StopIteration:
                break
        
        try:
            communities = next(comp)
        except StopIteration:
            communities = [{n} for n in self.graph.nodes()]
        
        comm_dict = {i: list(c) for i, c in enumerate(communities)}
        node_assignments = {}
        for comm_id, nodes in comm_dict.items():
            for node in nodes:
                node_assignments[node] = comm_id
        
        comm_sets = [set(c) for c in comm_dict.values()]
        modularity = nx.community.modularity(self.graph, comm_sets)
        
        return CommunityResult(
            algorithm=CommunityAlgorithm.GIRVAN_NEWMAN,
            communities=comm_dict,
            node_assignments=node_assignments,
            modularity=modularity,
            num_communities=len(comm_dict),
            community_sizes=[len(c) for c in comm_dict.values()]
        )
    
    def compare_algorithms(
        self,
        algorithms: Optional[List[CommunityAlgorithm]] = None
    ) -> pd.DataFrame:
        """
        Compare different community detection algorithms.
        
        Args:
            algorithms: List of algorithms to compare
        
        Returns:
            DataFrame with comparison results
        """
        if algorithms is None:
            algorithms = [
                CommunityAlgorithm.LOUVAIN,
                CommunityAlgorithm.GREEDY_MODULARITY,
                CommunityAlgorithm.LABEL_PROPAGATION
            ]
        
        results = []
        for alg in algorithms:
            try:
                result = self.detect_communities(alg)
                results.append({
                    'algorithm': alg.value,
                    'num_communities': result.num_communities,
                    'modularity': result.modularity,
                    'avg_community_size': np.mean(result.community_sizes),
                    'max_community_size': max(result.community_sizes),
                    'min_community_size': min(result.community_sizes)
                })
            except Exception as e:
                print(f"Error with {alg}: {e}")
        
        return pd.DataFrame(results)
    
    def analyze_community_structure(
        self,
        result: CommunityResult
    ) -> Dict[str, Any]:
        """
        Analyze community structure in detail.
        
        Args:
            result: Community detection result
        
        Returns:
            Detailed analysis
        """
        G = self.graph
        
        analysis = {
            'num_communities': result.num_communities,
            'modularity': result.modularity,
            'community_statistics': {}
        }
        
        for comm_id, nodes in result.communities.items():
            subgraph = G.subgraph(nodes)
            
            analysis['community_statistics'][comm_id] = {
                'size': len(nodes),
                'density': nx.density(subgraph),
                'avg_degree': np.mean([d for _, d in subgraph.degree()]),
                'clustering': nx.average_clustering(subgraph),
                'internal_edges': subgraph.number_of_edges(),
                'boundary_edges': self._count_boundary_edges(nodes, result.node_assignments)
            }
        
        # Inter-community connections
        analysis['inter_community_density'] = self._inter_community_density(
            result.communities, result.node_assignments
        )
        
        return analysis
    
    def _count_boundary_edges(
        self,
        nodes: List[str],
        assignments: Dict[str, int]
    ) -> int:
        """Count edges from community to other communities."""
        G = self.graph
        comm_id = assignments[nodes[0]]
        boundary = 0
        
        for node in nodes:
            for neighbor in G.neighbors(node):
                if assignments.get(neighbor) != comm_id:
                    boundary += 1
        
        return boundary
    
    def _inter_community_density(
        self,
        communities: Dict[int, List[str]],
        assignments: Dict[str, int]
    ) -> float:
        """Compute density of inter-community connections."""
        G = self.graph
        inter_edges = 0
        total_possible = 0
        
        comm_ids = list(communities.keys())
        for i, comm1 in enumerate(comm_ids):
            for comm2 in comm_ids[i+1:]:
                nodes1 = set(communities[comm1])
                nodes2 = set(communities[comm2])
                
                # Count actual edges
                for n1 in nodes1:
                    for n2 in nodes2:
                        if G.has_edge(n1, n2):
                            inter_edges += 1
                
                total_possible += len(nodes1) * len(nodes2)
        
        return inter_edges / total_possible if total_possible > 0 else 0


def detect_facility_communities(
    graph: 'nx.Graph',
    facility_type_attr: str = 'facility_type'
) -> Dict[str, List[Set[str]]]:
    """
    Detect communities within each facility type.
    
    Args:
        graph: Infrastructure network graph
        facility_type_attr: Node attribute for facility type
    
    Returns:
        Dictionary mapping facility types to communities
    """
    # Group nodes by facility type
    type_nodes = defaultdict(list)
    for node in graph.nodes():
        ftype = graph.nodes[node].get(facility_type_attr, 'unknown')
        type_nodes[ftype].append(node)
    
    # Detect communities for each type
    type_communities = {}
    for ftype, nodes in type_nodes.items():
        if len(nodes) < 3:
            continue
        
        subgraph = graph.subgraph(nodes)
        detector = CommunityDetector(subgraph)
        
        try:
            result = detector.detect_communities(CommunityAlgorithm.LOUVAIN)
            type_communities[ftype] = [
                set(nodes) for nodes in result.communities.values()
            ]
        except:
            pass
    
    return type_communities
```

---

## 10. Advanced Network Visualization

### 10.1 Network Visualization Module

**File:** `src/network/visualization/network_plots.py`

```python
"""
ResilienceAI - Network Visualization
Advanced visualization for infrastructure networks.
"""
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.colors import LinearSegmentedColormap
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class NetworkVisualizer:
    """Advanced network visualization for infrastructure analysis."""
    
    def __init__(self, graph: 'nx.Graph'):
        if not HAS_NETWORKX or not HAS_MATPLOTLIB:
            raise ImportError("NetworkX and Matplotlib are required")
        self.graph = graph
        self._default_figsize = (14, 10)
    
    def plot_network(
        self,
        node_color_by: Optional[str] = None,
        node_size_by: Optional[str] = None,
        edge_color_by: Optional[str] = None,
        layout: str = 'spring',
        figsize: Optional[Tuple[int, int]] = None,
        title: Optional[str] = None,
        show_labels: bool = False,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot network with customizable styling.
        
        Args:
            node_color_by: Node attribute for coloring
            node_size_by: Node attribute for sizing
            edge_color_by: Edge attribute for coloring
            layout: Layout algorithm ('spring', 'circular', 'kamada_kawai', 'spectral')
            figsize: Figure size
            title: Plot title
            show_labels: Whether to show node labels
            save_path: Path to save figure
        
        Returns:
            Matplotlib figure
        """
        G = self.graph
        fig, ax = plt.subplots(figsize=figsize or self._default_figsize)
        
        # Compute layout
        pos = self._compute_layout(layout)
        
        # Node colors
        if node_color_by and node_color_by in G.nodes[list(G.nodes())[0]]:
            node_colors = [G.nodes[n].get(node_color_by, 0) for n in G.nodes()]
        else:
            node_colors = 'skyblue'
        
        # Node sizes
        if node_size_by and node_size_by in G.nodes[list(G.nodes())[0]]:
            node_sizes = [G.nodes[n].get(node_size_by, 1) * 300 for n in G.nodes()]
        else:
            node_sizes = 300
        
        # Edge colors
        if edge_color_by:
            edge_colors = [G[u][v].get(edge_color_by, 0.5) for u, v in G.edges()]
        else:
            edge_colors = 'gray'
        
        # Draw network
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, alpha=0.5, ax=ax)
        nodes = nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=node_sizes,
            cmap='viridis', ax=ax
        )
        
        if show_labels:
            nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
        
        # Add colorbar for node colors
        if isinstance(node_colors, list):
            plt.colorbar(nodes, ax=ax, label=node_color_by or 'Node Value')
        
        ax.set_title(title or 'Infrastructure Network')
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_centrality_heatmap(
        self,
        centrality_values: Dict[str, float],
        layout: str = 'spring',
        figsize: Optional[Tuple[int, int]] = None,
        title: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot network with centrality heatmap.
        
        Args:
            centrality_values: Dictionary mapping nodes to centrality values
            layout: Layout algorithm
            figsize: Figure size
            title: Plot title
            save_path: Path to save figure
        
        Returns:
            Matplotlib figure
        """
        G = self.graph
        fig, ax = plt.subplots(figsize=figsize or self._default_figsize)
        
        pos = self._compute_layout(layout)
        
        # Get centrality values for all nodes
        values = [centrality_values.get(n, 0) for n in G.nodes()]
        
        # Node sizes proportional to centrality
        node_sizes = [v * 1000 + 100 for v in values]
        
        # Draw
        nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
        nodes = nx.draw_networkx_nodes(
            G, pos, node_color=values, node_size=node_sizes,
            cmap='YlOrRd', ax=ax
        )
        
        plt.colorbar(nodes, ax=ax, label='Centrality')
        ax.set_title(title or 'Centrality Heatmap')
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_communities(
        self,
        community_assignments: Dict[str, int],
        layout: str = 'spring',
        figsize: Optional[Tuple[int, int]] = None,
        title: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot network with community coloring.
        
        Args:
            community_assignments: Dictionary mapping nodes to community IDs
            layout: Layout algorithm
            figsize: Figure size
            title: Plot title
            save_path: Path to save figure
        
        Returns:
            Matplotlib figure
        """
        G = self.graph
        fig, ax = plt.subplots(figsize=figsize or self._default_figsize)
        
        pos = self._compute_layout(layout)
        
        # Get community assignments
        communities = [community_assignments.get(n, 0) for n in G.nodes()]
        num_communities = len(set(communities))
        
        # Use distinct colors for communities
        cmap = plt.cm.get_cmap('tab20', num_communities)
        
        # Draw
        nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
        nodes = nx.draw_networkx_nodes(
            G, pos, node_color=communities, cmap=cmap,
            node_size=300, ax=ax
        )
        
        ax.set_title(title or f'Network Communities (n={num_communities})')
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_cascade_progression(
        self,
        cascade_steps: List[Any],
        figsize: Optional[Tuple[int, int]] = None,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot cascade progression over time.
        
        Args:
            cascade_steps: List of cascade step results
            figsize: Figure size
            save_path: Path to save figure
        
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=figsize or (14, 10))
        
        steps = list(range(len(cascade_steps)))
        
        # Failed nodes over time
        failed = [len(step.newly_failed) for step in cascade_steps]
        axes[0, 0].plot(steps, failed, marker='o', color='red')
        axes[0, 0].set_xlabel('Step')
        axes[0, 0].set_ylabel('Newly Failed Nodes')
        axes[0, 0].set_title('Cascade Progression')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Cumulative failed
        cumulative = np.cumsum(failed)
        axes[0, 1].plot(steps, cumulative, marker='s', color='darkred')
        axes[0, 1].set_xlabel('Step')
        axes[0, 1].set_ylabel('Cumulative Failed Nodes')
        axes[0, 1].set_title('Cumulative Impact')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Network efficiency
        efficiency = [step.network_efficiency for step in cascade_steps]
        axes[1, 0].plot(steps, efficiency, marker='^', color='blue')
        axes[1, 0].set_xlabel('Step')
        axes[1, 0].set_ylabel('Network Efficiency')
        axes[1, 0].set_title('Efficiency Degradation')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Giant component size
        giant_size = [step.giant_component_size for step in cascade_steps]
        axes[1, 1].plot(steps, giant_size, marker='d', color='green')
        axes[1, 1].set_xlabel('Step')
        axes[1, 1].set_ylabel('Giant Component Size')
        axes[1, 1].set_title('Connectivity Loss')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_attack_robustness(
        self,
        robustness_profile: Any,
        figsize: Optional[Tuple[int, int]] = None,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot robustness under different attack strategies.
        
        Args:
            robustness_profile: RobustnessProfile object
            figsize: Figure size
            save_path: Path to save figure
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize or (10, 7))
        
        # Extract curves
        random_x = [x for x, _ in robustness_profile.random_attack_curve]
        random_y = [y for _, y in robustness_profile.random_attack_curve]
        
        degree_x = [x for x, _ in robustness_profile.degree_attack_curve]
        degree_y = [y for _, y in robustness_profile.degree_attack_curve]
        
        # Plot
        ax.plot(random_x, random_y, 'b-', label='Random Attack', linewidth=2)
        ax.plot(degree_x, degree_y, 'r-', label='Targeted (Degree)', linewidth=2)
        
        # Reference line
        ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='50% Threshold')
        
        ax.set_xlabel('Fraction of Nodes Removed', fontsize=12)
        ax.set_ylabel('Relative Size of Giant Component', fontsize=12)
        ax.set_title('Network Robustness Under Attack', fontsize=14)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.5)
        ax.set_ylim(0, 1)
        
        # Add robustness integral annotation
        ax.text(0.25, 0.8, f'Robustness: {robustness_profile.robustness_integral:.3f}',
                fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_resilience_dashboard(
        self,
        resilience_profile: Dict[Any, Any],
        figsize: Optional[Tuple[int, int]] = None,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot comprehensive resilience dashboard.
        
        Args:
            resilience_profile: Dictionary of ResilienceScore objects
            figsize: Figure size
            save_path: Path to save figure
        
        Returns:
            Matplotlib figure
        """
        fig = plt.figure(figsize=figsize or (16, 12))
        
        # Create grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Dimension scores radar chart
        ax1 = fig.add_subplot(gs[0, :2], projection='polar')
        self._plot_resilience_radar(resilience_profile, ax1)
        
        # Score bar chart
        ax2 = fig.add_subplot(gs[0, 2])
        self._plot_resilience_bars(resilience_profile, ax2)
        
        # Contributing metrics
        ax3 = fig.add_subplot(gs[1, :])
        self._plot_contributing_metrics(resilience_profile, ax3)
        
        # Interpretation text
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('off')
        interpretations = [
            f"{score.dimension.value}: {score.interpretation}"
            for score in resilience_profile.values()
        ]
        ax4.text(0.05, 0.95, '\n\n'.join(interpretations),
                transform=ax4.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _plot_resilience_radar(
        self,
        profile: Dict[Any, Any],
        ax: plt.Axes
    ):
        """Plot resilience radar chart."""
        dimensions = list(profile.keys())
        scores = [profile[d].score for d in dimensions]
        
        # Close the polygon
        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
        scores_plot = scores + [scores[0]]
        angles += angles[:1]
        
        ax.plot(angles, scores_plot, 'o-', linewidth=2, color='blue')
        ax.fill(angles, scores_plot, alpha=0.25, color='blue')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([d.value for d in dimensions], size=10)
        ax.set_ylim(0, 1)
        ax.set_title('Resilience Dimensions', fontsize=12, pad=20)
    
    def _plot_resilience_bars(
        self,
        profile: Dict[Any, Any],
        ax: plt.Axes
    ):
        """Plot resilience score bars."""
        dimensions = [d.value for d in profile.keys()]
        scores = [profile[d].score for d in profile.keys()]
        
        colors = ['green' if s > 0.7 else 'orange' if s > 0.4 else 'red' for s in scores]
        
        ax.barh(dimensions, scores, color=colors, alpha=0.7)
        ax.set_xlim(0, 1)
        ax.set_xlabel('Score')
        ax.set_title('Resilience Scores')
    
    def _plot_contributing_metrics(
        self,
        profile: Dict[Any, Any],
        ax: plt.Axes
    ):
        """Plot contributing metrics."""
        metrics_data = []
        for dim, score in profile.items():
            for metric, value in score.contributing_metrics.items():
                metrics_data.append({
                    'dimension': dim.value,
                    'metric': metric,
                    'value': value
                })
        
        df = pd.DataFrame(metrics_data)
        
        # Create grouped bar chart
        pivot = df.pivot(index='metric', columns='dimension', values='value')
        pivot.plot(kind='bar', ax=ax, width=0.8)
        
        ax.set_title('Contributing Metrics by Dimension')
        ax.set_xlabel('Metric')
        ax.set_ylabel('Value')
        ax.legend(title='Dimension', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    def _compute_layout(self, layout: str) -> Dict[str, np.ndarray]:
        """Compute network layout."""
        G = self.graph
        
        if layout == 'spring':
            return nx.spring_layout(G, k=2/np.sqrt(G.number_of_nodes()), iterations=50)
        elif layout == 'circular':
            return nx.circular_layout(G)
        elif layout == 'kamada_kawai':
            return nx.kamada_kawai_layout(G)
        elif layout == 'spectral':
            return nx.spectral_layout(G)
        elif layout == 'shell':
            return nx.shell_layout(G)
        else:
            return nx.spring_layout(G)


def create_interactive_network(
    graph: 'nx.Graph',
    output_path: str,
    node_attributes: Optional[List[str]] = None
) -> str:
    """
    Create interactive HTML network visualization using PyVis.
    
    Args:
        graph: NetworkX graph
        output_path: Output HTML file path
        node_attributes: Node attributes to display
    
    Returns:
        Path to output file
    """
    try:
        from pyvis.network import Network
    except ImportError:
        print("PyVis not installed. Install with: pip install pyvis")
        return ""
    
    net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='black')
    
    # Add nodes
    for node in graph.nodes():
        title = f"Node: {node}"
        if node_attributes:
            for attr in node_attributes:
                if attr in graph.nodes[node]:
                    title += f"<br>{attr}: {graph.nodes[node][attr]}"
        
        net.add_node(node, title=title)
    
    # Add edges
    for u, v in graph.edges():
        net.add_edge(u, v)
    
    # Enable physics
    net.toggle_physics(True)
    
    # Save
    net.save_graph(output_path)
    
    return output_path
```

---

## 11. Integration and Usage Examples

### 11.1 Complete Analysis Pipeline

**File:** `src/network/examples/complete_pipeline.py`

```python
"""
ResilienceAI - Complete Network Analysis Pipeline
Example of using all network analysis capabilities together.
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Import network modules
from network.core.infrastructure_graph import InfrastructureGraphBuilder
from network.analysis.centrality import CentralityAnalyzer, CentralityType
from network.analysis.connectivity import ConnectivityAnalyzer
from network.analysis.paths import PathAnalyzer
from network.analysis.resilience import ResilienceAnalyzer
from network.analysis.communities import CommunityDetector, CommunityAlgorithm
from network.simulation.cascade_failure import CascadeSimulator, CascadeModel
from network.visualization.network_plots import NetworkVisualizer


def run_complete_analysis(
    facilities_df: pd.DataFrame,
    output_dir: str = './network_analysis_output'
):
    """
    Run complete network analysis pipeline.
    
    Args:
        facilities_df: DataFrame with facility data
        output_dir: Directory for output files
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("ResilienceAI Network Analysis Pipeline")
    print("=" * 60)
    
    # Step 1: Build Network
    print("\n[1/8] Building infrastructure network...")
    builder = InfrastructureGraphBuilder()
    graph = builder.build_from_facilities(
        facilities_df,
        connect_by_proximity=True,
        proximity_threshold_km=50.0
    )
    print(f"  Created graph with {graph.num_nodes} nodes and {graph.num_edges} edges")
    
    nx_graph = graph.to_networkx()
    
    # Step 2: Centrality Analysis
    print("\n[2/8] Computing centrality metrics...")
    centrality_analyzer = CentralityAnalyzer(nx_graph)
    all_centralities = centrality_analyzer.compute_all_centralities(top_k=10)
    
    print("  Top 5 nodes by betweenness centrality:")
    for result in all_centralities[CentralityType.BETWEENNESS][:5]:
        print(f"    {result.node_id}: {result.value:.4f}")
    
    # Step 3: Connectivity Analysis
    print("\n[3/8] Analyzing connectivity...")
    conn_analyzer = ConnectivityAnalyzer(nx_graph)
    metrics = conn_analyzer.compute_all_metrics()
    
    for metric, result in metrics.items():
        print(f"  {metric.value}: {result.value:.4f}")
    
    # Step 4: Path Analysis
    print("\n[4/8] Analyzing critical paths...")
    path_analyzer = PathAnalyzer(nx_graph)
    
    # Find critical nodes
    critical_nodes = centrality_analyzer.identify_critical_nodes()
    print(f"  Identified {len(critical_nodes)} critical nodes")
    
    # Step 5: Resilience Analysis
    print("\n[5/8] Computing resilience profile...")
    resilience_analyzer = ResilienceAnalyzer(nx_graph)
    resilience_profile = resilience_analyzer.compute_resilience_profile()
    
    integrated_index = resilience_analyzer.compute_integrated_resilience_index()
    print(f"  Integrated Resilience Index: {integrated_index:.3f}")
    
    for dim, score in resilience_profile.items():
        print(f"  {dim.value}: {score.score:.3f}")
    
    # Step 6: Community Detection
    print("\n[6/8] Detecting communities...")
    community_detector = CommunityDetector(nx_graph)
    communities = community_detector.detect_communities(CommunityAlgorithm.LOUVAIN)
    
    print(f"  Found {communities.num_communities} communities")
    print(f"  Modularity: {communities.modularity:.4f}")
    
    # Step 7: Cascade Simulation
    print("\n[7/8] Simulating cascade failures...")
    cascade_sim = CascadeSimulator(nx_graph)
    
    # Simulate from most critical node
    if critical_nodes:
        initial_failure = [critical_nodes[0][0]]
        cascade_result = cascade_sim.simulate(
            CascadeModel.LOAD_REDISTRIBUTION,
            initial_failure
        )
        print(f"  Cascade impact: {cascade_result.total_impact:.1%} of network")
        print(f"  Cascade steps: {cascade_result.total_steps}")
    
    # Step 8: Visualization
    print("\n[8/8] Creating visualizations...")
    viz = NetworkVisualizer(nx_graph)
    
    # Network plot
    viz.plot_network(
        node_color_by='facility_type',
        title='Infrastructure Network',
        save_path=f'{output_dir}/network_overview.png'
    )
    
    # Centrality heatmap
    betweenness = centrality_analyzer.compute_centrality(CentralityType.BETWEENNESS)
    betweenness_values = {n: r.value for n, r in betweenness.items()}
    viz.plot_centrality_heatmap(
        betweenness_values,
        title='Betweenness Centrality',
        save_path=f'{output_dir}/centrality_heatmap.png'
    )
    
    # Community visualization
    viz.plot_communities(
        communities.node_assignments,
        title='Network Communities',
        save_path=f'{output_dir}/communities.png'
    )
    
    # Cascade progression
    if critical_nodes:
        viz.plot_cascade_progression(
            cascade_result.cascade_steps,
            save_path=f'{output_dir}/cascade_progression.png'
        )
    
    # Resilience dashboard
    viz.plot_resilience_dashboard(
        resilience_profile,
        save_path=f'{output_dir}/resilience_dashboard.png'
    )
    
    print(f"\n✓ Analysis complete. Results saved to {output_dir}/")
    
    return {
        'graph': graph,
        'centralities': all_centralities,
        'connectivity_metrics': metrics,
        'resilience_profile': resilience_profile,
        'integrated_resilience_index': integrated_index,
        'communities': communities,
        'cascade_result': cascade_result if critical_nodes else None
    }


if __name__ == '__main__':
    # Example with sample data
    sample_data = {
        'facility_type': ['hospital', 'hospital', 'fire_station', 'fire_station', 
                         'ems_station', 'ems_station', 'nursing_home', 'nursing_home'],
        'latitude': [38.6, 38.7, 38.65, 38.75, 38.62, 38.72, 38.68, 38.78],
        'longitude': [-90.2, -90.3, -90.25, -90.35, -90.22, -90.32, -90.28, -90.38],
        'name': ['Hospital A', 'Hospital B', 'Fire Station 1', 'Fire Station 2',
                'EMS Station 1', 'EMS Station 2', 'Nursing Home A', 'Nursing Home B'],
        'capacity': [100, 150, 50, 60, 30, 40, 80, 90]
    }
    
    df = pd.DataFrame(sample_data)
    results = run_complete_analysis(df)
```

---

## 12. Implementation Priority Order

### Phase 1: Core Foundation (Weeks 1-2)
1. **Base Graph Classes** (`src/network/core/`)
   - `base_graph.py`: Core graph abstractions
   - `infrastructure_graph.py`: Infrastructure-specific builders
   
2. **Enhanced Network Analysis** (Refactor `src/network_analysis.py`)
   - Integrate new base classes
   - Maintain backward compatibility
   - Add new metrics

### Phase 2: Analysis Modules (Weeks 3-4)
3. **Centrality Analysis** (`src/network/analysis/centrality.py`)
   - All centrality measures
   - Critical node identification
   
4. **Connectivity Assessment** (`src/network/analysis/connectivity.py`)
   - Comprehensive connectivity metrics
   - Vulnerability matrix
   
5. **Path Analysis** (`src/network/analysis/paths.py`)
   - Shortest path algorithms
   - Critical path identification

### Phase 3: Advanced Features (Weeks 5-6)
6. **Resilience Metrics** (`src/network/analysis/resilience.py`)
   - Five-dimension resilience model
   - Percolation analysis
   
7. **Cascade Simulation** (`src/network/simulation/cascade_failure.py`)
   - Load redistribution model
   - Epidemic model
   
8. **Community Detection** (`src/network/analysis/communities.py`)
   - Multiple algorithms
   - Comparative analysis

### Phase 4: Visualization & Integration (Weeks 7-8)
9. **Network Visualization** (`src/network/visualization/`)
   - Static plots
   - Interactive visualizations
   
10. **Agent Integration**
    - MCP tools for network analysis
    - Dashboard integration

---

## 13. Dependencies and Requirements

### Core Dependencies
```
networkx>=3.0
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
matplotlib>=3.7.0
```

### Optional Dependencies
```
graph-tool>=2.45      # High-performance graph algorithms
python-louvain>=0.16  # Community detection
pyvis>=0.3.0          # Interactive visualization
plotly>=5.14.0        # Interactive plots
seaborn>=0.12.0       # Enhanced plotting
```

### Installation
```bash
# Core installation
pip install networkx numpy pandas scipy matplotlib

# Full installation
pip install networkx numpy pandas scipy matplotlib graph-tool python-louvain pyvis plotly seaborn
```

---

## 14. Summary

This comprehensive network analysis enhancement provides ResilienceAI with state-of-the-art graph analysis capabilities:

| Capability | Current | Enhanced |
|------------|---------|----------|
| Graph Types | Undirected only | Directed, Multi-layer |
| Centrality | Betweenness only | 10+ measures |
| Connectivity | Basic | Comprehensive |
| Path Analysis | None | Full suite |
| Resilience | Single score | 5-dimension model |
| Cascade | Simple neighbor | Load redistribution |
| Communities | None | 6+ algorithms |
| Visualization | None | Static + Interactive |

**Key Benefits:**
- **Enhanced Vulnerability Assessment**: Identify critical infrastructure points
- **Improved Resilience Planning**: Quantify resilience across multiple dimensions
- **Better Cascade Prediction**: Model realistic failure propagation
- **Community-Aware Analysis**: Understand facility clusters
- **Professional Visualization**: Communicate findings effectively

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: Network Analysis Engineering Team*
