"""
Community detection algorithms for identifying county clusters.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


class CommunityAlgorithm(Enum):
    """Available community detection algorithms."""
    LOUVAIN = "louvain"
    LABEL_PROPAGATION = "labelPropagation"
    MODULARITY_OPTIMIZATION = "modularityOptimization"
    WCC = "wcc"  # Weakly Connected Components
    SCC = "scc"  # Strongly Connected Components


@dataclass
class CommunityResult:
    """Result container for community detection."""
    community_id: int
    size: int
    members: List[Dict[str, Any]]
    avg_risk_score: float
    avg_resilience_score: float
    total_population: int
    modularity: float


class CommunityDetectionService:
    """Service for community detection analysis."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def detect_communities(
        self,
        graph_name: str,
        algorithm: CommunityAlgorithm = CommunityAlgorithm.LOUVAIN,
        node_label: str = "County",
        id_property: str = "fips_code",
        relationship_type: str = "ADJACENT_TO",
        weight_property: Optional[str] = None,
        min_community_size: int = 3
    ) -> List[CommunityResult]:
        """
        Detect communities in the graph.
        
        Args:
            graph_name: GDS graph name
            algorithm: Community detection algorithm
            node_label: Node label
            id_property: ID property name
            relationship_type: Relationship type
            weight_property: Edge weight property
            min_community_size: Minimum community size
            
        Returns:
            List of detected communities
        """
        # Ensure graph exists
        self._ensure_graph_projection(graph_name, node_label, relationship_type, weight_property)
        
        config = {}
        if weight_property:
            config["relationshipWeightProperty"] = weight_property
        
        query = f"""
        CALL gds.{algorithm.value}.stream($graph_name, $config)
        YIELD nodeId, communityId
        WITH gds.util.asNode(nodeId) AS node, communityId
        WITH communityId,
             collect({{
                 {id_property}: node.{id_property},
                 name: node.name,
                 risk_score: node.risk_score,
                 resilience_score: node.resilience_score,
                 population: node.population
             }}) AS members
        WHERE size(members) >= $min_size
        RETURN communityId,
               members,
               size(members) AS community_size,
               avg(members[0].risk_score) AS avg_risk,
               avg(members[0].resilience_score) AS avg_resilience,
               sum(members[0].population) AS total_population
        ORDER BY community_size DESC
        """
        
        results = self.manager.execute_read(
            query,
            {
                "graph_name": graph_name,
                "config": config,
                "min_size": min_community_size
            }
        )
        
        return [
            CommunityResult(
                community_id=record['communityId'],
                size=record['community_size'],
                members=record['members'],
                avg_risk_score=record['avg_risk'],
                avg_resilience_score=record['avg_resilience'],
                total_population=record['total_population'],
                modularity=0.0  # Would need separate calculation
            )
            for record in results
        ]
    
    def analyze_community_characteristics(
        self,
        graph_name: str,
        community_id: int,
        node_label: str = "County",
        id_property: str = "fips_code"
    ) -> Dict[str, Any]:
        """
        Analyze characteristics of a specific community.
        
        Args:
            graph_name: GDS graph name
            community_id: Community ID to analyze
            node_label: Node label
            id_property: ID property name
            
        Returns:
            Community characteristics
        """
        query = f"""
        CALL gds.louvain.stream($graph_name)
        YIELD nodeId, communityId
        WITH gds.util.asNode(nodeId) AS node, communityId
        WHERE communityId = $community_id
        
        // Get community members
        WITH collect(node) AS members
        
        // Calculate internal connectivity
        UNWIND members AS m1
        UNWIND members AS m2
        WITH m1, m2, members
        WHERE id(m1) < id(m2)
        OPTIONAL MATCH (m1)-[r:ADJACENT_TO]-(m2)
        
        // Calculate statistics
        WITH members,
             count(r) AS internal_edges,
             count(DISTINCT m1) AS node_count
        
        RETURN {{
            community_id: $community_id,
            member_count: node_count,
            internal_edges: internal_edges,
            density: CASE WHEN node_count > 1 
                     THEN internal_edges / (node_count * (node_count - 1) / 2.0) 
                     ELSE 0 END,
            avg_risk: avg(m.risk_score FOR m IN members),
            avg_resilience: avg(m.resilience_score FOR m IN members),
            total_population: sum(m.population FOR m IN members),
            member_ids: [m.{id_property} FOR m IN members],
            member_names: [m.name FOR m IN members]
        }} AS characteristics
        """
        
        result = self.manager.execute_read(query, {
            "graph_name": graph_name,
            "community_id": community_id
        })
        
        return result[0]['characteristics'] if result else {}
    
    def find_inter_community_connections(
        self,
        graph_name: str,
        node_label: str = "County",
        relationship_type: str = "ADJACENT_TO"
    ) -> List[Dict[str, Any]]:
        """
        Find connections between different communities.
        
        Args:
            graph_name: GDS graph name
            node_label: Node label
            relationship_type: Relationship type
            
        Returns:
            List of inter-community connections
        """
        query = f"""
        CALL gds.louvain.stream($graph_name)
        YIELD nodeId, communityId
        WITH gds.util.asNode(nodeId) AS node, communityId
        
        // Find edges between communities
        MATCH (node)-[r:{relationship_type}]-(other)
        WHERE node <> other
        WITH node, other, r, communityId AS c1
        CALL gds.louvain.stream($graph_name)
        YIELD nodeId AS otherId, communityId AS c2
        WHERE otherId = id(other) AND c1 <> c2
        
        RETURN c1 AS community_1,
               c2 AS community_2,
               count(*) AS connection_count,
               avg(r.connectivity_score) AS avg_connection_strength
        ORDER BY connection_count DESC
        """
        
        return self.manager.execute_read(
            query,
            {"graph_name": graph_name}
        )
    
    def compare_community_algorithms(
        self,
        graph_name: str,
        node_label: str = "County",
        id_property: str = "fips_code"
    ) -> Dict[str, Any]:
        """
        Compare results from different community detection algorithms.
        
        Args:
            graph_name: GDS graph name
            node_label: Node label
            id_property: ID property name
            
        Returns:
            Comparison results
        """
        results = {}
        
        for algorithm in CommunityAlgorithm:
            try:
                communities = self.detect_communities(
                    graph_name=graph_name,
                    algorithm=algorithm,
                    node_label=node_label,
                    id_property=id_property
                )
                
                results[algorithm.value] = {
                    "community_count": len(communities),
                    "avg_community_size": sum(c.size for c in communities) / len(communities) if communities else 0,
                    "largest_community_size": max((c.size for c in communities), default=0),
                    "smallest_community_size": min((c.size for c in communities), default=0),
                    "communities": [
                        {
                            "id": c.community_id,
                            "size": c.size,
                            "avg_risk": c.avg_risk_score,
                            "avg_resilience": c.avg_resilience_score
                        }
                        for c in communities
                    ]
                }
            except Exception as e:
                results[algorithm.value] = {"error": str(e)}
        
        return results
    
    def find_risk_clusters(
        self,
        graph_name: str = "county-network",
        risk_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find clusters of high-risk counties.
        
        Args:
            graph_name: GDS graph name
            risk_threshold: Minimum risk score for inclusion
            
        Returns:
            List of high-risk clusters
        """
        query = """
        CALL gds.louvain.stream($graph_name)
        YIELD nodeId, communityId
        WITH gds.util.asNode(nodeId) AS node, communityId
        WHERE node.risk_score >= $threshold
        WITH communityId,
             collect({
                 fips: node.fips_code,
                 name: node.name,
                 risk_score: node.risk_score
             }) AS high_risk_members,
             avg(node.risk_score) AS avg_risk
        WHERE size(high_risk_members) >= 2
        RETURN communityId,
               high_risk_members,
               size(high_risk_members) AS cluster_size,
               avg_risk
        ORDER BY cluster_size DESC, avg_risk DESC
        """
        
        return self.manager.execute_read(query, {
            "graph_name": graph_name,
            "threshold": risk_threshold
        })
    
    def _ensure_graph_projection(
        self,
        graph_name: str,
        node_label: str,
        relationship_type: str,
        weight_property: Optional[str]
    ) -> None:
        """Ensure GDS graph projection exists."""
        check_query = "CALL gds.graph.exists($graph_name) YIELD exists"
        result = self.manager.execute_read(check_query, {"graph_name": graph_name})
        
        if result and result[0]['exists']:
            return
        
        weight_config = f", relationshipProperties: '{weight_property}'" if weight_property else ""
        
        create_query = f"""
        CALL gds.graph.project(
            $graph_name,
            '{node_label}',
            '{relationship_type}'
            {weight_config}
        )
        """
        
        self.manager.execute_write(create_query, {"graph_name": graph_name})
