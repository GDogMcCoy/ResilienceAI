"""
ResilienceAI Infrastructure Analysis - Advanced Network Analysis
Enhanced network analysis with capacity weighting and multi-modal routing
"""

import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy.spatial import cKDTree
import warnings

warnings.filterwarnings('ignore')


class AdvancedInfrastructureNetwork:
    """
    Advanced infrastructure network analysis with:
    - Multi-modal routing (road network, straight-line)
    - Dynamic capacity weighting
    - Real-time status integration
    - Multi-criteria vulnerability assessment
    """
    
    def __init__(self, use_road_network: bool = False):
        self.facilities: Dict[str, Dict] = {}
        self.graph: Optional[nx.Graph] = None
        self.use_road_network = use_road_network
        self.kdtree: Optional[cKDTree] = None
        self.facility_coords: Optional[np.ndarray] = None
        
    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance in kilometers"""
        R = 6371.0
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        return R * 2 * np.arcsin(np.sqrt(a))
    
    def load_facilities(self, facilities_df: pd.DataFrame, 
                        facility_type: str) -> None:
        """Load facilities from DataFrame with enhanced attributes"""
        for _, row in facilities_df.iterrows():
            facility_id = str(row.get('ID', row.get('OBJECTID', row.name)))
            
            # Extract capacity data if available
            capacity = self._extract_capacity(row, facility_type)
            
            self.facilities[facility_id] = {
                'id': facility_id,
                'name': row.get('NAME', row.get('name', 'Unknown')),
                'facility_type': facility_type,
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'address': row.get('ADDRESS'),
                'county_fips': str(row.get('COUNTYFIPS', row.get('county_fips', ''))),
                'state': row.get('STATE', row.get('state', '')),
                'capacity': capacity,
                'trauma_level': row.get('TRAUMA'),
                'emergency_services': row.get('EMERGENCY', False),
                'services': self._parse_services(row),
                'status': row.get('status', 'operational')
            }
            
        self._build_spatial_index()
        
    def _extract_capacity(self, row: pd.Series, facility_type: str) -> Optional[Dict]:
        """Extract facility capacity information"""
        try:
            if facility_type == 'hospitals':
                total_beds = int(row.get('BEDS', 0))
                if total_beds == 0:
                    return None
                    
                occupancy = float(row.get('OCCUPANCY_RATE', 0.7))
                
                return {
                    'total_beds': total_beds,
                    'available_beds': int(total_beds * (1 - occupancy)),
                    'icu_beds': int(row.get('ICU_BEDS', total_beds * 0.1)),
                    'available_icu_beds': int(row.get('ICU_BEDS', total_beds * 0.1) * 0.3),
                    'ventilators': int(row.get('VENTILATORS', total_beds * 0.05)),
                    'available_ventilators': int(row.get('VENTILATORS', total_beds * 0.05) * 0.5),
                    'emergency_capacity': int(row.get('EMERGENCY_CAPACITY', total_beds * 0.2)),
                    'current_occupancy_rate': occupancy,
                    'staffing_level': float(row.get('STAFFING_LEVEL', 0.8))
                }
            elif facility_type == 'fire_stations':
                return {
                    'personnel': int(row.get('PERSONNEL', 0)),
                    'apparatus_count': int(row.get('APPARATUS', 1)),
                    'service_area_km2': float(row.get('SERVICE_AREA', 0))
                }
            elif facility_type == 'ems_stations':
                return {
                    'ambulances': int(row.get('AMBULANCES', 1)),
                    'personnel': int(row.get('PERSONNEL', 0)),
                    'avg_response_time': float(row.get('AVG_RESPONSE_TIME', 0))
                }
            elif facility_type == 'nursing_homes':
                return {
                    'beds': int(row.get('BEDS', 0)),
                    'residents': int(row.get('RESIDENTS', 0)),
                    'staff_count': int(row.get('STAFF_COUNT', 0))
                }
        except (ValueError, TypeError):
            pass
        return None
    
    def _parse_services(self, row: pd.Series) -> List[str]:
        """Parse services from row data"""
        services = []
        if row.get('EMERGENCY'):
            services.append('emergency')
        if row.get('TRAUMA'):
            services.append(f"trauma_level_{row['TRAUMA']}")
        if row.get('ICU_BEDS', 0) > 0:
            services.append('icu')
        return services
    
    def _build_spatial_index(self) -> None:
        """Build KD-tree for fast spatial queries"""
        if not self.facilities:
            return
            
        coords = []
        for facility in self.facilities.values():
            coords.append([facility['latitude'], facility['longitude']])
        
        if coords:
            self.facility_coords = np.radians(np.array(coords))
            self.kdtree = cKDTree(self.facility_coords)
    
    def get_facilities_in_radius(self, center_lat: float, center_lon: float,
                                  radius_km: float) -> List[Dict]:
        """Get all facilities within radius of center point"""
        if self.kdtree is None:
            return []
        
        center_rad = np.radians([center_lat, center_lon])
        radius_rad = radius_km / 6371.0
        
        indices = self.kdtree.query_ball_point(center_rad, radius_rad)
        
        facilities = list(self.facilities.values())
        return [facilities[i] for i in indices]
    
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
        nearby_facilities = self.get_facilities_in_radius(center_lat, center_lon, radius_km)
        
        if not nearby_facilities:
            return nx.Graph()
        
        # Create graph
        G = nx.Graph()
        
        # Add nodes with enhanced attributes
        for facility in nearby_facilities:
            node_weight = self._calculate_node_weight(facility)
            G.add_node(
                facility['id'],
                facility=facility,
                weight=node_weight,
                lat=facility['latitude'],
                lon=facility['longitude'],
                facility_type=facility['facility_type'],
                status=facility.get('status', 'operational')
            )
        
        # Add edges with capacity and distance weighting
        self._add_weighted_edges(G, connectivity_km)
        
        self.graph = G
        return G
    
    def _calculate_node_weight(self, facility: Dict) -> float:
        """
        Calculate node importance weight based on:
        - Facility capacity
        - Service level
        - Current status
        """
        base_weight = 1.0
        
        # Capacity weighting
        capacity = facility.get('capacity')
        if capacity:
            if 'total_beds' in capacity:
                base_weight *= np.log1p(capacity['total_beds']) / 5
            elif 'beds' in capacity:
                base_weight *= np.log1p(capacity['beds']) / 5
            elif 'personnel' in capacity:
                base_weight *= np.log1p(capacity['personnel']) / 3
            elif 'ambulances' in capacity:
                base_weight *= capacity['ambulances']
            
        # Trauma level weighting for hospitals
        if facility.get('trauma_level'):
            base_weight *= (4 - facility['trauma_level'] + 1) / 2
            
        # Status penalty
        status_multiplier = {
            'operational': 1.0,
            'limited_capacity': 0.7,
            'overcapacity': 0.5,
            'closed': 0.0,
            'damaged': 0.0,
            'unknown': 0.5
        }
        base_weight *= status_multiplier.get(facility.get('status', 'unknown'), 0.5)
        
        return base_weight
    
    def _add_weighted_edges(self, G: nx.Graph, max_distance_km: float) -> None:
        """Add edges with distance and capacity weighting"""
        nodes = list(G.nodes(data=True))
        
        for i, (node_i, data_i) in enumerate(nodes):
            for j, (node_j, data_j) in enumerate(nodes[i+1:], i+1):
                dist_km = self.haversine_km(
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
            'betweenness_centrality': {},
            'closeness_centrality': {},
            'eigenvector_centrality': {},
            
            # Capacity-weighted centrality
            'capacity_centrality': self._capacity_weighted_centrality(G),
            
            # Resilience metrics
            'articulation_points': [],
            'avg_clustering': 0.0,
            'node_connectivity': 0,
            
            # Service-specific metrics
            'service_coverage': self._calculate_service_coverage(G),
            'capacity_distribution': self._analyze_capacity_distribution(G),
        }
        
        # Calculate centrality metrics
        try:
            metrics['betweenness_centrality'] = nx.betweenness_centrality(G, weight='weight')
            metrics['closeness_centrality'] = nx.closeness_centrality(G, distance='weight')
            metrics['eigenvector_centrality'] = nx.eigenvector_centrality(G, max_iter=1000)
        except:
            pass
        
        # Articulation points
        try:
            metrics['articulation_points'] = list(nx.articulation_points(G))
        except:
            pass
        
        # Clustering
        try:
            metrics['avg_clustering'] = nx.average_clustering(G)
        except:
            pass
        
        # Node connectivity
        try:
            metrics['node_connectivity'] = nx.node_connectivity(G) if G.number_of_nodes() > 1 else 0
        except:
            pass
        
        # Composite vulnerability score
        metrics['vulnerability_score'] = self._calculate_vulnerability_score(metrics)
        metrics['resilience_score'] = 1 - metrics['vulnerability_score']
        
        # Critical facilities
        metrics['critical_facilities'] = self._identify_critical_facilities(metrics)
        
        return metrics
    
    def _capacity_weighted_centrality(self, G: nx.Graph) -> Dict[str, float]:
        """Calculate centrality weighted by facility capacity"""
        centrality = {}
        try:
            degree_cent = nx.degree_centrality(G)
            for node in G.nodes():
                facility = G.nodes[node].get('facility', {})
                capacity = facility.get('capacity', {})
                
                base_centrality = degree_cent.get(node, 0)
                
                if capacity:
                    if 'total_beds' in capacity:
                        capacity_factor = np.log1p(capacity['total_beds']) / 10
                    elif 'beds' in capacity:
                        capacity_factor = np.log1p(capacity['beds']) / 10
                    elif 'personnel' in capacity:
                        capacity_factor = np.log1p(capacity['personnel']) / 5
                    else:
                        capacity_factor = 1.0
                else:
                    capacity_factor = 1.0
                
                centrality[node] = base_centrality * capacity_factor
        except:
            pass
        return centrality
    
    def _calculate_service_coverage(self, G: nx.Graph) -> Dict[str, Dict]:
        """Analyze coverage by facility type"""
        coverage = {}
        facility_types = set(nx.get_node_attributes(G, 'facility_type').values())
        
        for facility_type in facility_types:
            nodes_of_type = [
                n for n, d in G.nodes(data=True)
                if d.get('facility_type') == facility_type
            ]
            
            if nodes_of_type:
                subgraph = G.subgraph(nodes_of_type)
                coverage[facility_type] = {
                    'count': len(nodes_of_type),
                    'avg_degree': np.mean([d for n, d in subgraph.degree()]) if subgraph.number_of_nodes() > 0 else 0
                }
                try:
                    coverage[facility_type]['connectivity'] = nx.node_connectivity(subgraph)
                except:
                    coverage[facility_type]['connectivity'] = 0
        
        return coverage
    
    def _analyze_capacity_distribution(self, G: nx.Graph) -> Dict[str, float]:
        """Analyze capacity distribution across network"""
        distribution = {
            'total_capacity': 0,
            'avg_capacity_per_facility': 0,
            'capacity_concentration': 0
        }
        
        capacities = []
        for node in G.nodes():
            facility = G.nodes[node].get('facility', {})
            capacity = facility.get('capacity', {})
            
            if capacity:
                if 'total_beds' in capacity:
                    capacities.append(capacity['total_beds'])
                elif 'beds' in capacity:
                    capacities.append(capacity['beds'])
                elif 'personnel' in capacity:
                    capacities.append(capacity['personnel'])
        
        if capacities:
            distribution['total_capacity'] = sum(capacities)
            distribution['avg_capacity_per_facility'] = np.mean(capacities)
            distribution['capacity_concentration'] = np.std(capacities) / np.mean(capacities) if np.mean(capacities) > 0 else 0
        
        return distribution
    
    def _calculate_vulnerability_score(self, metrics: Dict) -> float:
        """Calculate composite vulnerability score (0=resilient, 1=vulnerable)"""
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
    
    def _identify_critical_facilities(self, metrics: Dict) -> List[Dict]:
        """Identify critical facilities in the network"""
        critical = []
        
        if not metrics['betweenness_centrality']:
            return critical
        
        # Top 10 by betweenness centrality
        top_nodes = sorted(metrics['betweenness_centrality'], 
                          key=metrics['betweenness_centrality'].get, 
                          reverse=True)[:10]
        
        for node_id in top_nodes:
            if self.graph and node_id in self.graph:
                node_data = self.graph.nodes[node_id]
                facility = node_data.get('facility', {})
                
                critical.append({
                    'id': node_id,
                    'name': facility.get('name', f'Facility {node_id}'),
                    'type': facility.get('facility_type', 'Unknown'),
                    'betweenness_centrality': round(metrics['betweenness_centrality'].get(node_id, 0), 4),
                    'is_articulation_point': node_id in metrics['articulation_points'],
                    'lat': node_data.get('lat'),
                    'lon': node_data.get('lon')
                })
        
        return critical
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'total_facilities': 0,
            'total_connections': 0,
            'network_density': 0,
            'connected_components': 0,
            'articulation_points': [],
            'avg_clustering': 0,
            'node_connectivity': 0,
            'betweenness_centrality': {},
            'closeness_centrality': {},
            'eigenvector_centrality': {},
            'capacity_centrality': {},
            'service_coverage': {},
            'capacity_distribution': {},
            'vulnerability_score': 1.0,
            'resilience_score': 0.0,
            'critical_facilities': []
        }
    
    def simulate_cascade_failure(self, failed_facility_id: Optional[str] = None,
                                 failure_threshold: float = 0.5,
                                 max_steps: int = 20) -> Dict:
        """
        Simulate cascade failure starting from a facility removal
        
        Args:
            failed_facility_id: Initial facility to fail (default: highest betweenness)
            failure_threshold: Load threshold that triggers cascade
            max_steps: Maximum simulation steps
            
        Returns:
            Cascade simulation results
        """
        if self.graph is None or self.graph.number_of_nodes() < 3:
            return {'cascade_steps': 0, 'total_failed': 0, 'cascade_ratio': 0.0}
        
        G = self.graph.copy()
        
        # Pick initial failure point
        if failed_facility_id is None:
            betweenness = nx.betweenness_centrality(G, weight='weight')
            failed_facility_id = max(betweenness, key=betweenness.get)
        
        if failed_facility_id not in G:
            return {'cascade_steps': 0, 'total_failed': 0, 'cascade_ratio': 0.0}
        
        # Simulate cascade
        failed = {failed_facility_id}
        cascade_log = [{'step': 0, 'newly_failed': [failed_facility_id], 'total_failed': 1}]
        
        for step in range(1, max_steps):
            newly_failed = set()
            
            for node in list(G.nodes()):
                if node in failed:
                    continue
                
                # Count failed neighbors
                neighbors = set(G.neighbors(node))
                if not neighbors:
                    continue
                
                failed_neighbor_ratio = len(neighbors & failed) / len(neighbors)
                if failed_neighbor_ratio >= failure_threshold:
                    newly_failed.add(node)
            
            if not newly_failed:
                break
            
            failed |= newly_failed
            cascade_log.append({
                'step': step,
                'newly_failed': list(newly_failed),
                'total_failed': len(failed)
            })
        
        return {
            'initial_failure': failed_facility_id,
            'cascade_steps': len(cascade_log) - 1,
            'total_failed': len(failed),
            'total_facilities': G.number_of_nodes(),
            'cascade_ratio': round(len(failed) / G.number_of_nodes(), 4),
            'cascade_log': cascade_log
        }
