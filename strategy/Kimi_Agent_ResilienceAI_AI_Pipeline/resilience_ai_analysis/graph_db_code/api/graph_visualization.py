"""
FastAPI endpoints for graph visualization.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional, List
import json

router = APIRouter(prefix="/api/v1/graph", tags=["graph-visualization"])


@router.get("/county-network")
async def get_county_network(
    state: Optional[str] = Query(None, description="Filter by state"),
    min_risk: float = Query(0.0, ge=0.0, le=1.0, description="Minimum risk score"),
    max_nodes: int = Query(100, ge=1, le=500, description="Maximum nodes to return")
):
    """Get county network data for visualization."""
    from app.infrastructure.graph.neo4j_manager import get_neo4j_manager
    
    manager = get_neo4j_manager()
    
    where_clauses = ["c.risk_score >= $min_risk"]
    if state:
        where_clauses.append("c.state = $state")
    
    where_clause = " AND ".join(where_clauses)
    
    query = f"""
    MATCH (c:County)
    WHERE {where_clause}
    WITH c LIMIT $max_nodes
    OPTIONAL MATCH (c)-[r:ADJACENT_TO]-(other:County)
    WHERE other.risk_score >= $min_risk
    RETURN 
        collect(DISTINCT {{
            id: c.fips_code,
            name: c.name,
            state: c.state,
            risk_score: c.risk_score,
            resilience_score: c.resilience_score,
            population: c.population,
            type: 'County'
        }}) AS nodes,
        collect(DISTINCT CASE WHEN other IS NOT NULL THEN {{
            source: c.fips_code,
            target: other.fips_code,
            weight: r.connectivity_score,
            distance: r.border_length_miles
        }} END) AS links
    """
    
    result = manager.execute_read(query, {
        "state": state,
        "min_risk": min_risk,
        "max_nodes": max_nodes
    })
    
    if result:
        return {
            "nodes": result[0]['nodes'],
            "links": [l for l in result[0]['links'] if l],
            "metadata": {
                "total_nodes": len(result[0]['nodes']),
                "total_links": len([l for l in result[0]['links'] if l]),
                "filters": {"state": state, "min_risk": min_risk}
            }
        }
    return {"nodes": [], "links": [], "metadata": {}}


@router.get("/facility-network/{county_fips}")
async def get_facility_network(county_fips: str):
    """Get facility dependency network for a county."""
    from app.infrastructure.graph.neo4j_manager import get_neo4j_manager
    
    manager = get_neo4j_manager()
    
    query = """
    MATCH (c:County {fips_code: $fips_code})-[:CONTAINS]->(f:Facility)
    OPTIONAL MATCH (f)-[r:DEPENDS_ON]-(other:Facility)
    WHERE EXISTS((c)-[:CONTAINS]->(other))
    RETURN 
        collect(DISTINCT {
            id: f.facility_id,
            name: f.name,
            type: f.facility_type,
            category: f.category,
            risk_level: f.risk_level,
            criticality: f.criticality_level,
            operational_status: f.operational_status
        }) AS nodes,
        collect(DISTINCT CASE WHEN other IS NOT NULL THEN {
            source: f.facility_id,
            target: other.facility_id,
            dependency_type: r.dependency_type,
            criticality: r.criticality
        } END) AS links
    """
    
    result = manager.execute_read(query, {"fips_code": county_fips})
    
    if result:
        return {
            "county_fips": county_fips,
            "nodes": result[0]['nodes'],
            "links": [l for l in result[0]['links'] if l],
            "metadata": {
                "total_facilities": len(result[0]['nodes']),
                "total_dependencies": len([l for l in result[0]['links'] if l])
            }
        }
    return {"county_fips": county_fips, "nodes": [], "links": [], "metadata": {}}


@router.get("/hazard-network/{hazard_id}")
async def get_hazard_network(hazard_id: str):
    """Get hazard impact network."""
    from app.infrastructure.graph.neo4j_manager import get_neo4j_manager
    
    manager = get_neo4j_manager()
    
    query = """
    MATCH (h:Hazard {hazard_id: $hazard_id})
    OPTIONAL MATCH (h)-[t:THREATENS]->(c:County)
    OPTIONAL MATCH (h)-[tf:THREATENS]->(f:Facility)
    OPTIONAL MATCH (c)-[:CONTAINS]->(f2:Facility)
    RETURN 
        h.hazard_id AS hazard_id,
        h.hazard_type AS hazard_type,
        h.severity AS severity,
        collect(DISTINCT {
            id: c.fips_code,
            name: c.name,
            type: 'County',
            threat_probability: t.probability,
            impact_score: t.impact_score
        }) AS threatened_counties,
        collect(DISTINCT {
            id: f.facility_id,
            name: f.name,
            type: f.facility_type,
            county: c.fips_code,
            threat_probability: tf.probability
        }) AS threatened_facilities
    """
    
    result = manager.execute_read(query, {"hazard_id": hazard_id})
    
    if result:
        return {
            "hazard": {
                "id": result[0]['hazard_id'],
                "type": result[0]['hazard_type'],
                "severity": result[0]['severity']
            },
            "threatened_counties": result[0]['threatened_counties'],
            "threatened_facilities": result[0]['threatened_facilities']
        }
    raise HTTPException(status_code=404, detail="Hazard not found")


@router.get("/shortest-path")
async def get_shortest_path(
    start_fips: str = Query(..., description="Starting county FIPS"),
    end_fips: str = Query(..., description="Ending county FIPS"),
    algorithm: str = Query("dijkstra", description="Pathfinding algorithm")
):
    """Find shortest path between two counties."""
    from app.domain.analytics.graph_algorithms.shortest_path import ShortestPathService
    
    service = ShortestPathService()
    
    result = service.find_shortest_path(
        start_id=start_fips,
        end_id=end_fips,
        node_label="County",
        id_property="fips_code"
    )
    
    if result:
        return {
            "path": result.path,
            "total_cost": result.total_cost,
            "node_count": result.node_count,
            "edge_count": result.edge_count,
            "algorithm": result.algorithm,
            "execution_time_ms": result.execution_time_ms
        }
    return {"path": [], "message": "No path found"}


@router.get("/centrality/{metric}")
async def get_centrality(
    metric: str,
    graph_name: str = Query("county-network"),
    top_k: int = Query(20, ge=1, le=100)
):
    """Get centrality scores for counties."""
    from app.domain.analytics.graph_algorithms.centrality import (
        CentralityService, CentralityAlgorithm
    )
    
    service = CentralityService()
    
    algorithm_map = {
        "pagerank": CentralityAlgorithm.PAGERANK,
        "betweenness": CentralityAlgorithm.BETWEENNESS,
        "degree": CentralityAlgorithm.DEGREE,
        "eigenvector": CentralityAlgorithm.EIGENVECTOR
    }
    
    if metric not in algorithm_map:
        raise HTTPException(status_code=400, detail=f"Unknown metric: {metric}")
    
    results = service.calculate_centrality(
        graph_name=graph_name,
        algorithm=algorithm_map[metric],
        top_k=top_k
    )
    
    return {
        "metric": metric,
        "graph_name": graph_name,
        "results": [
            {
                "rank": r.rank,
                "node_id": r.node_id,
                "node_name": r.node_name,
                "score": r.score
            }
            for r in results
        ]
    }


@router.get("/communities")
async def get_communities(
    graph_name: str = Query("county-network"),
    algorithm: str = Query("louvain"),
    min_size: int = Query(3, ge=1)
):
    """Get community detection results."""
    from app.domain.analytics.graph_algorithms.community_detection import (
        CommunityDetectionService, CommunityAlgorithm
    )
    
    service = CommunityDetectionService()
    
    algorithm_map = {
        "louvain": CommunityAlgorithm.LOUVAIN,
        "label_propagation": CommunityAlgorithm.LABEL_PROPAGATION
    }
    
    if algorithm not in algorithm_map:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {algorithm}")
    
    results = service.detect_communities(
        graph_name=graph_name,
        algorithm=algorithm_map[algorithm],
        min_community_size=min_size
    )
    
    return {
        "algorithm": algorithm,
        "graph_name": graph_name,
        "community_count": len(results),
        "communities": [
            {
                "community_id": r.community_id,
                "size": r.size,
                "avg_risk_score": r.avg_risk_score,
                "avg_resilience_score": r.avg_resilience_score,
                "total_population": r.total_population,
                "members": r.members[:10]  # Limit members in response
            }
            for r in results
        ]
    }


@router.get("/similar-counties/{fips_code}")
async def get_similar_counties(
    fips_code: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Find counties similar to the given county."""
    from app.infrastructure.graph.repositories.county_repository import CountyRepository
    
    repo = CountyRepository()
    
    results = repo.find_similar_counties(fips_code, limit=limit)
    
    return {
        "reference_county": fips_code,
        "similar_counties": results
    }


@router.get("/stats")
async def get_graph_stats():
    """Get overall graph statistics."""
    from app.infrastructure.graph.neo4j_manager import get_neo4j_manager
    
    manager = get_neo4j_manager()
    
    query = """
    MATCH (c:County)
    OPTIONAL MATCH (f:Facility)
    OPTIONAL MATCH (i:Infrastructure)
    OPTIONAL MATCH (h:Hazard)
    OPTIONAL MATCH (c)-[r:ADJACENT_TO]-()
    RETURN {
        counties: count(DISTINCT c),
        facilities: count(DISTINCT f),
        infrastructure: count(DISTINCT i),
        hazards: count(DISTINCT h),
        county_adjacencies: count(DISTINCT r),
        avg_risk_score: avg(c.risk_score),
        avg_resilience_score: avg(c.resilience_score),
        total_population: sum(c.population)
    } AS stats
    """
    
    result = manager.execute_read(query)
    
    return result[0]['stats'] if result else {}
