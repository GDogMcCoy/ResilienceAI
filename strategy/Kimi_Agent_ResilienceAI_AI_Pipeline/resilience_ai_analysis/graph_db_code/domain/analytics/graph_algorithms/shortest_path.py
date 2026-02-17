"""
Shortest path algorithms for ResilienceAI graph analytics.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


class PathAlgorithm(Enum):
    """Available shortest path algorithms."""
    DIJKSTRA = "dijkstra"
    A_STAR = "astar"
    BFS = "bfs"
    YEN = "yen"


@dataclass
class PathResult:
    """Result container for pathfinding operations."""
    path: List[str]  # Node IDs in path
    total_cost: float
    node_count: int
    edge_count: int
    algorithm: str
    execution_time_ms: float


@dataclass
class PathSegment:
    """Individual segment of a path."""
    from_node: str
    to_node: str
    cost: float
    relationship_type: str
    properties: Dict[str, Any]


class ShortestPathService:
    """Service for shortest path calculations."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def find_shortest_path(
        self,
        start_id: str,
        end_id: str,
        node_label: str = "County",
        id_property: str = "fips_code",
        relationship_type: str = "ADJACENT_TO",
        weight_property: Optional[str] = None,
        algorithm: PathAlgorithm = PathAlgorithm.DIJKSTRA
    ) -> Optional[PathResult]:
        """
        Find shortest path between two nodes.
        
        Args:
            start_id: Starting node ID
            end_id: Target node ID
            node_label: Node label to match
            id_property: Property containing node ID
            relationship_type: Relationship type to traverse
            weight_property: Property to use for edge weights
            algorithm: Pathfinding algorithm to use
            
        Returns:
            PathResult if path found, None otherwise
        """
        weight_clause = f"{{costProperty: '{weight_property}'}}" if weight_property else ""
        
        query = f"""
        MATCH (start:{node_label} {{{id_property}: $start_id}})
        MATCH (end:{node_label} {{{id_property}: $end_id}})
        CALL apoc.algo.dijkstra(start, end, '{relationship_type}', 'distance') {weight_clause}
        YIELD path, weight
        RETURN 
            [node IN nodes(path) | node.{id_property}] AS path_nodes,
            weight AS total_cost,
            length(path) AS edge_count,
            size(nodes(path)) AS node_count
        """
        
        start_time = time.time()
        
        result = self.manager.execute_read(
            query, 
            {"start_id": start_id, "end_id": end_id}
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        if not result:
            return None
        
        record = result[0]
        return PathResult(
            path=record['path_nodes'],
            total_cost=record['total_cost'],
            node_count=record['node_count'],
            edge_count=record['edge_count'],
            algorithm=algorithm.value,
            execution_time_ms=execution_time
        )
    
    def find_k_shortest_paths(
        self,
        start_id: str,
        end_id: str,
        k: int = 3,
        node_label: str = "County",
        id_property: str = "fips_code",
        relationship_type: str = "ADJACENT_TO"
    ) -> List[PathResult]:
        """
        Find K shortest paths using Yen's algorithm.
        
        Args:
            start_id: Starting node ID
            end_id: Target node ID
            k: Number of paths to find
            node_label: Node label
            id_property: ID property name
            relationship_type: Relationship type
            
        Returns:
            List of PathResult objects
        """
        graph_name = f"{node_label.lower()}-network"
        
        # Use GDS Yen's algorithm
        query = f"""
        MATCH (start:{node_label} {{{id_property}: $start_id}})
        MATCH (end:{node_label} {{{id_property}: $end_id}})
        CALL gds.shortestPath.yens.stream($graph_name, {{
            sourceNode: id(start),
            targetNode: id(end),
            k: $k
        }})
        YIELD index, totalCost, nodeIds
        RETURN 
            index AS path_index,
            totalCost AS cost,
            [nodeId IN nodeIds | gds.util.asNode(nodeId).{id_property}] AS path
        ORDER BY path_index
        """
        
        start_time = time.time()
        
        results = self.manager.execute_read(
            query,
            {
                "start_id": start_id,
                "end_id": end_id,
                "k": k,
                "graph_name": graph_name
            }
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        paths = []
        for record in results:
            paths.append(PathResult(
                path=record['path'],
                total_cost=record['cost'],
                node_count=len(record['path']),
                edge_count=len(record['path']) - 1,
                algorithm="yen",
                execution_time_ms=execution_time / len(results) if results else 0
            ))
        
        return paths
    
    def find_reachable_nodes(
        self,
        start_id: str,
        max_depth: int = 5,
        node_label: str = "County",
        id_property: str = "fips_code",
        relationship_type: str = "ADJACENT_TO"
    ) -> List[Dict[str, Any]]:
        """
        Find all nodes reachable within max_depth hops.
        
        Args:
            start_id: Starting node ID
            max_depth: Maximum traversal depth
            node_label: Node label
            id_property: ID property name
            relationship_type: Relationship type
            
        Returns:
            List of reachable nodes with distance
        """
        query = f"""
        MATCH (start:{node_label} {{{id_property}: $start_id}})
        CALL apoc.path.subgraphNodes(start, {{
            relationshipFilter: '{relationship_type}',
            minLevel: 1,
            maxLevel: $max_depth
        }}) YIELD node
        WITH node, start
        CALL apoc.algo.dijkstra(start, node, '{relationship_type}') 
        YIELD path, weight
        RETURN 
            node.{id_property} AS node_id,
            node.name AS name,
            length(path) AS hops,
            weight AS distance
        ORDER BY hops, distance
        """
        
        return self.manager.execute_read(
            query,
            {"start_id": start_id, "max_depth": max_depth}
        )
    
    def find_critical_facilities_path(
        self,
        start_facility_id: str,
        end_facility_id: str,
        avoid_high_risk: bool = True
    ) -> Optional[PathResult]:
        """
        Find path between facilities considering risk levels.
        
        Args:
            start_facility_id: Starting facility ID
            end_facility_id: Target facility ID
            avoid_high_risk: Whether to avoid high-risk nodes
            
        Returns:
            PathResult if path found
        """
        risk_filter = "WHERE ALL(f IN nodes(path) WHERE f.risk_level <> 'CRITICAL')" if avoid_high_risk else ""
        
        query = f"""
        MATCH (start:Facility {{facility_id: $start_id}})
        MATCH (end:Facility {{facility_id: $end_id}})
        MATCH path = shortestPath(
            (start)-[:DEPENDS_ON|CONNECTED_BY*]-(end)
        )
        {risk_filter}
        RETURN 
            [node IN nodes(path) | node.facility_id] AS path_nodes,
            length(path) AS edge_count,
            size(nodes(path)) AS node_count,
            reduce(total_risk = 0, n IN nodes(path) | 
                total_risk + CASE n.risk_level 
                    WHEN 'CRITICAL' THEN 4 
                    WHEN 'HIGH' THEN 3 
                    WHEN 'MEDIUM' THEN 2 
                    ELSE 1 
                END
            ) AS total_risk_score
        """
        
        result = self.manager.execute_read(
            query,
            {"start_id": start_facility_id, "end_id": end_facility_id}
        )
        
        if not result:
            return None
        
        record = result[0]
        return PathResult(
            path=record['path_nodes'],
            total_cost=record['total_risk_score'],
            node_count=record['node_count'],
            edge_count=record['edge_count'],
            algorithm="risk-aware-bfs",
            execution_time_ms=0
        )
    
    def find_evacuation_routes(
        self,
        county_fips: str,
        max_distance: float = 100.0
    ) -> List[Dict[str, Any]]:
        """
        Find evacuation routes from a county to adjacent safe counties.
        
        Args:
            county_fips: County FIPS code
            max_distance: Maximum route distance in miles
            
        Returns:
            List of evacuation routes
        """
        query = """
        MATCH (c:County {fips_code: $fips_code})
        MATCH (c)-[r:ADJACENT_TO]-(adjacent:County)
        WHERE adjacent.risk_score < c.risk_score
        RETURN 
            adjacent.fips_code AS target_fips,
            adjacent.name AS target_name,
            adjacent.risk_score AS target_risk,
            r.border_length_miles AS distance,
            c.risk_score - adjacent.risk_score AS risk_reduction
        ORDER BY risk_reduction DESC, distance ASC
        """
        
        return self.manager.execute_read(query, {"fips_code": county_fips})


class PathAnalyzer:
    """Analyze path characteristics and vulnerabilities."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def analyze_path_vulnerability(
        self,
        path_node_ids: List[str],
        node_label: str = "County",
        id_property: str = "fips_code"
    ) -> Dict[str, Any]:
        """
        Analyze vulnerability of a given path.
        
        Args:
            path_node_ids: List of node IDs in path
            node_label: Node label
            id_property: ID property name
            
        Returns:
            Vulnerability analysis results
        """
        query = f"""
        UNWIND $path_ids AS node_id
        MATCH (n:{node_label} {{{id_property}: node_id}})
        OPTIONAL MATCH (n)-[:CONTAINS]->(f:Facility)
        OPTIONAL MATCH (h:Hazard)-[t:THREATENS]->(n)
        RETURN {{
            node_id: node_id,
            name: n.name,
            risk_score: n.risk_score,
            critical_facilities: collect(DISTINCT {{
                id: f.facility_id,
                name: f.name,
                criticality: f.criticality_level
            }}),
            hazards: collect(DISTINCT {{
                type: h.hazard_type,
                probability: t.probability,
                impact: t.impact_score
            }}),
            vulnerability_score: n.risk_score * count(DISTINCT f)
        }} AS node_analysis
        """
        
        results = self.manager.execute_read(query, {"path_ids": path_node_ids})
        
        node_analyses = [r['node_analysis'] for r in results]
        
        # Calculate aggregate metrics
        total_vulnerability = sum(n['vulnerability_score'] for n in node_analyses)
        avg_risk = sum(n['risk_score'] for n in node_analyses) / len(node_analyses) if node_analyses else 0
        critical_facilities = sum(
            len([f for f in n['critical_facilities'] if f['criticality'] >= 4])
            for n in node_analyses
        )
        
        return {
            "path_length": len(path_node_ids),
            "total_vulnerability_score": total_vulnerability,
            "average_risk_score": avg_risk,
            "critical_facilities_count": critical_facilities,
            "node_analyses": node_analyses,
            "bottleneck_nodes": sorted(
                node_analyses,
                key=lambda x: x['vulnerability_score'],
                reverse=True
            )[:3]
        }
    
    def find_alternative_paths(
        self,
        start_id: str,
        end_id: str,
        excluded_nodes: List[str],
        node_label: str = "County",
        id_property: str = "fips_code"
    ) -> List[PathResult]:
        """
        Find alternative paths excluding certain nodes.
        
        Args:
            start_id: Starting node ID
            end_id: Target node ID
            excluded_nodes: List of node IDs to exclude
            node_label: Node label
            id_property: ID property name
            
        Returns:
            List of alternative paths
        """
        query = f"""
        MATCH (start:{node_label} {{{id_property}: $start_id}})
        MATCH (end:{node_label} {{{id_property}: $end_id}})
        MATCH path = (start)-[:ADJACENT_TO*1..10]-(end)
        WHERE ALL(n IN nodes(path) WHERE NOT n.{id_property} IN $excluded OR n = start OR n = end)
        WITH path, length(path) AS path_length
        ORDER BY path_length
        LIMIT 5
        RETURN 
            [n IN nodes(path) | n.{id_property}] AS path_nodes,
            path_length,
            reduce(total_risk = 0.0, n IN nodes(path) | total_risk + n.risk_score) AS total_risk
        """
        
        results = self.manager.execute_read(
            query,
            {"start_id": start_id, "end_id": end_id, "excluded": excluded_nodes}
        )
        
        paths = []
        for record in results:
            paths.append(PathResult(
                path=record['path_nodes'],
                total_cost=record['total_risk'],
                node_count=len(record['path_nodes']),
                edge_count=record['path_length'],
                algorithm="alternative-path",
                execution_time_ms=0
            ))
        
        return paths
