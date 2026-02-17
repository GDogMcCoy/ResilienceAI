"""
Centrality analysis for identifying critical nodes in the network.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time

from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


class CentralityAlgorithm(Enum):
    """Available centrality algorithms."""
    PAGERANK = "pageRank"
    BETWEENNESS = "betweenness"
    DEGREE = "degree"
    EIGENVECTOR = "eigenvector"
    CLOSENESS = "closeness"
    HARMONIC = "harmonic"


@dataclass
class CentralityResult:
    """Result container for centrality analysis."""
    node_id: str
    node_name: str
    score: float
    rank: int
    algorithm: str
    additional_properties: Dict[str, Any]


class CentralityService:
    """Service for centrality analysis."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def calculate_centrality(
        self,
        graph_name: str,
        algorithm: CentralityAlgorithm,
        node_label: str = "County",
        id_property: str = "fips_code",
        relationship_type: str = "ADJACENT_TO",
        weight_property: Optional[str] = None,
        top_k: int = 20
    ) -> List[CentralityResult]:
        """
        Calculate centrality scores for all nodes.
        
        Args:
            graph_name: Name of GDS graph projection
            algorithm: Centrality algorithm to use
            node_label: Node label
            id_property: ID property name
            relationship_type: Relationship type
            weight_property: Edge weight property
            top_k: Number of top results to return
            
        Returns:
            List of centrality results
        """
        # Ensure graph exists
        self._ensure_graph_projection(
            graph_name, node_label, relationship_type, weight_property
        )
        
        # Build algorithm configuration
        config = {}
        if weight_property:
            config["relationshipWeightProperty"] = weight_property
        
        query = f"""
        CALL gds.{algorithm.value}.stream($graph_name, $config)
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS node, score
        ORDER BY score DESC
        LIMIT $top_k
        RETURN 
            node.{id_property} AS node_id,
            node.name AS node_name,
            score,
            node {{.*}} AS properties
        """
        
        results = self.manager.execute_read(
            query,
            {
                "graph_name": graph_name,
                "config": config,
                "top_k": top_k
            }
        )
        
        return [
            CentralityResult(
                node_id=record['node_id'],
                node_name=record['node_name'],
                score=record['score'],
                rank=idx + 1,
                algorithm=algorithm.value,
                additional_properties=record['properties']
            )
            for idx, record in enumerate(results)
        ]
    
    def calculate_all_centralities(
        self,
        graph_name: str,
        node_label: str = "County",
        id_property: str = "fips_code"
    ) -> Dict[str, List[CentralityResult]]:
        """
        Calculate all centrality measures for comprehensive analysis.
        
        Args:
            graph_name: Name of GDS graph projection
            node_label: Node label
            id_property: ID property name
            
        Returns:
            Dictionary mapping algorithm names to results
        """
        results = {}
        
        for algorithm in CentralityAlgorithm:
            try:
                results[algorithm.value] = self.calculate_centrality(
                    graph_name=graph_name,
                    algorithm=algorithm,
                    node_label=node_label,
                    id_property=id_property
                )
            except Exception as e:
                results[algorithm.value] = []
                print(f"Failed to calculate {algorithm.value}: {e}")
        
        return results
    
    def find_critical_nodes(
        self,
        graph_name: str,
        node_label: str = "County",
        id_property: str = "fips_code",
        min_centrality_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find critical nodes based on multiple centrality measures.
        
        Args:
            graph_name: GDS graph name
            node_label: Node label
            id_property: ID property name
            min_centrality_threshold: Minimum score threshold
            
        Returns:
            List of critical nodes with combined scores
        """
        query = f"""
        // Calculate multiple centrality measures
        CALL gds.pageRank.stream($graph_name) YIELD nodeId, score AS pagerank
        WITH nodeId, pagerank
        ORDER BY pagerank DESC
        WITH collect({{nodeId: nodeId, score: pagerank}}) AS pageranks
        
        CALL gds.betweenness.stream($graph_name) YIELD nodeId, score AS betweenness
        WITH nodeId, betweenness, pageranks
        ORDER BY betweenness DESC
        WITH collect({{nodeId: nodeId, score: betweenness}}) AS betweennesses, pageranks
        
        CALL gds.degree.stream($graph_name) YIELD nodeId, score AS degree
        WITH nodeId, degree, pageranks, betweennesses
        ORDER BY degree DESC
        WITH collect({{nodeId: nodeId, score: degree}}) AS degrees, pageranks, betweennesses
        
        // Combine scores
        UNWIND pageranks AS pr
        WITH pr, 
             [b IN betweennesses WHERE b.nodeId = pr.nodeId][0].score AS bt,
             [d IN degrees WHERE d.nodeId = pr.nodeId][0].score AS dg
        WHERE pr.score > $threshold OR bt > $threshold
        
        RETURN 
            gds.util.asNode(pr.nodeId).{id_property} AS node_id,
            gds.util.asNode(pr.nodeId).name AS node_name,
            pr.score AS pagerank,
            bt AS betweenness,
            dg AS degree,
            (pr.score + bt + dg) / 3 AS combined_score
        ORDER BY combined_score DESC
        LIMIT 50
        """
        
        return self.manager.execute_read(
            query,
            {"graph_name": graph_name, "threshold": min_centrality_threshold}
        )
    
    def analyze_network_resilience(
        self,
        graph_name: str,
        node_label: str = "County",
        id_property: str = "fips_code"
    ) -> Dict[str, Any]:
        """
        Analyze network resilience by simulating node removal.
        
        Args:
            graph_name: GDS graph name
            node_label: Node label
            id_property: ID property name
            
        Returns:
            Resilience analysis results
        """
        # Get top central nodes
        central_nodes = self.calculate_centrality(
            graph_name=graph_name,
            algorithm=CentralityAlgorithm.BETWEENNESS,
            node_label=node_label,
            id_property=id_property,
            top_k=10
        )
        
        # Analyze impact of removing each critical node
        impact_analysis = []
        for node in central_nodes[:5]:
            impact = self._simulate_node_removal(
                graph_name, node.node_id, node_label, id_property
            )
            impact_analysis.append({
                "removed_node": node.node_id,
                "node_name": node.node_name,
                "centrality_score": node.score,
                "impact": impact
            })
        
        return {
            "critical_nodes": central_nodes,
            "impact_analysis": impact_analysis,
            "resilience_score": self._calculate_resilience_score(impact_analysis)
        }
    
    def _ensure_graph_projection(
        self,
        graph_name: str,
        node_label: str,
        relationship_type: str,
        weight_property: Optional[str]
    ) -> None:
        """Ensure GDS graph projection exists."""
        # Check if graph exists
        check_query = "CALL gds.graph.exists($graph_name) YIELD exists"
        result = self.manager.execute_read(check_query, {"graph_name": graph_name})
        
        if result and result[0]['exists']:
            return
        
        # Create graph projection
        weight_config = f", relationshipProperties: '{weight_property}'" if weight_property else ""
        
        create_query = f"""
        CALL gds.graph.project(
            $graph_name,
            '{node_label}',
            '{relationship_type}'
            {weight_config}
        )
        """
        
        self.manager.execute_write(
            create_query,
            {"graph_name": graph_name}
        )
    
    def _simulate_node_removal(
        self,
        graph_name: str,
        node_id: str,
        node_label: str,
        id_property: str
    ) -> Dict[str, Any]:
        """Simulate impact of removing a node from the network."""
        query = f"""
        // Get current network metrics
        CALL gds.graph.list($graph_name) YIELD nodeCount, relationshipCount
        WITH nodeCount AS original_nodes, relationshipCount AS original_edges
        
        // Find node to remove
        MATCH (n:{node_label} {{{id_property}: $node_id}})
        
        // Count affected relationships
        OPTIONAL MATCH (n)-[r]-()
        WITH original_nodes, original_edges, count(r) AS affected_relationships
        
        // Calculate connectivity impact
        RETURN {{
            original_node_count: original_nodes,
            original_edge_count: original_edges,
            affected_relationships: affected_relationships,
            connectivity_impact: affected_relationships / toFloat(original_edges)
        }} AS impact
        """
        
        result = self.manager.execute_read(
            query,
            {"graph_name": graph_name, "node_id": node_id}
        )
        
        return result[0]['impact'] if result else {}
    
    def _calculate_resilience_score(
        self,
        impact_analysis: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall network resilience score."""
        if not impact_analysis:
            return 1.0
        
        # Average connectivity impact
        avg_impact = sum(
            a['impact'].get('connectivity_impact', 0)
            for a in impact_analysis
        ) / len(impact_analysis)
        
        # Resilience is inverse of impact
        return max(0, 1 - avg_impact)


class CentralityComparison:
    """Compare centrality results across different time periods."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def compare_over_time(
        self,
        graph_name: str,
        time_points: List[str],
        algorithm: CentralityAlgorithm = CentralityAlgorithm.PAGERANK
    ) -> Dict[str, Any]:
        """
        Compare centrality scores across multiple time snapshots.
        
        Args:
            graph_name: Base graph name
            time_points: List of snapshot identifiers
            algorithm: Centrality algorithm to compare
            
        Returns:
            Comparison results
        """
        comparisons = []
        
        for time_point in time_points:
            snapshot_name = f"{graph_name}-{time_point}"
            
            try:
                results = self.calculate_centrality(
                    graph_name=snapshot_name,
                    algorithm=algorithm,
                    top_k=20
                )
                
                comparisons.append({
                    "time_point": time_point,
                    "top_nodes": [
                        {"id": r.node_id, "name": r.node_name, "score": r.score}
                        for r in results[:5]
                    ],
                    "avg_score": sum(r.score for r in results) / len(results) if results else 0
                })
            except Exception as e:
                comparisons.append({
                    "time_point": time_point,
                    "error": str(e)
                })
        
        return {
            "algorithm": algorithm.value,
            "time_points": time_points,
            "comparisons": comparisons
        }
