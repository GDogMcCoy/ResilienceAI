"""
County repository for graph operations.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class County:
    """County entity."""
    fips_code: str
    name: str
    state: str
    population: int = 0
    area_sq_miles: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    risk_score: float = 0.0
    resilience_score: float = 0.0
    social_vulnerability_index: float = 0.0
    geometry: Optional[str] = None


class CountyRepository:
    """Repository for County nodes."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
        self.node_label = "County"
        self.primary_key = "fips_code"
    
    def create(self, county: County) -> County:
        """Create a new county node."""
        query = """
        CREATE (c:County {
            fips_code: $fips_code,
            name: $name,
            state: $state,
            population: $population,
            area_sq_miles: $area_sq_miles,
            latitude: $latitude,
            longitude: $longitude,
            risk_score: $risk_score,
            resilience_score: $resilience_score,
            social_vulnerability_index: $svi,
            geometry: $geometry,
            created_at: datetime(),
            updated_at: datetime(),
            version: 1
        })
        RETURN c
        """
        
        result = self.manager.execute_write(query, {
            "fips_code": county.fips_code,
            "name": county.name,
            "state": county.state,
            "population": county.population,
            "area_sq_miles": county.area_sq_miles,
            "latitude": county.latitude,
            "longitude": county.longitude,
            "risk_score": county.risk_score,
            "resilience_score": county.resilience_score,
            "svi": county.social_vulnerability_index,
            "geometry": county.geometry
        })
        
        return county
    
    def create_many(self, counties: List[County], batch_size: int = 1000) -> int:
        """Bulk create counties using UNWIND."""
        batch = []
        now = datetime.now().isoformat()
        
        for county in counties:
            batch.append({
                "fips_code": county.fips_code,
                "name": county.name,
                "state": county.state,
                "population": county.population,
                "area_sq_miles": county.area_sq_miles,
                "latitude": county.latitude,
                "longitude": county.longitude,
                "risk_score": county.risk_score,
                "resilience_score": county.resilience_score,
                "social_vulnerability_index": county.social_vulnerability_index,
                "geometry": county.geometry,
                "created_at": now,
                "updated_at": now,
                "version": 1
            })
        
        query = """
        UNWIND $batch AS props
        CREATE (c:County)
        SET c = props
        RETURN count(c) AS created_count
        """
        
        return self.manager.bulk_insert(query, batch, batch_size)
    
    def find_by_id(self, fips_code: str) -> Optional[County]:
        """Find county by FIPS code."""
        query = """
        MATCH (c:County {fips_code: $fips_code})
        RETURN c
        """
        
        result = self.manager.execute_read(query, {"fips_code": fips_code})
        
        if result:
            node = result[0]['c']
            return self._node_to_county(node)
        return None
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[County]:
        """Find all counties with pagination."""
        query = """
        MATCH (c:County)
        RETURN c
        ORDER BY c.name
        SKIP $offset
        LIMIT $limit
        """
        
        result = self.manager.execute_read(query, {"limit": limit, "offset": offset})
        return [self._node_to_county(r['c']) for r in result]
    
    def update(self, fips_code: str, updates: Dict[str, Any]) -> Optional[County]:
        """Update county properties."""
        updates['updated_at'] = datetime.now().isoformat()
        
        query = """
        MATCH (c:County {fips_code: $fips_code})
        SET c += $updates
        SET c.version = coalesce(c.version, 0) + 1
        RETURN c
        """
        
        result = self.manager.execute_write(query, {
            "fips_code": fips_code,
            "updates": updates
        })
        
        if result:
            return self._node_to_county(result[0]['c'])
        return None
    
    def delete(self, fips_code: str) -> bool:
        """Delete county by FIPS code."""
        query = """
        MATCH (c:County {fips_code: $fips_code})
        DETACH DELETE c
        RETURN count(c) AS deleted
        """
        
        result = self.manager.execute_write(query, {"fips_code": fips_code})
        return result[0]['deleted'] > 0 if result else False
    
    def find_adjacent_counties(self, fips_code: str) -> List[County]:
        """Find all counties adjacent to the given county."""
        query = """
        MATCH (c:County {fips_code: $fips_code})-[:ADJACENT_TO]-(adjacent:County)
        RETURN adjacent
        ORDER BY adjacent.name
        """
        
        result = self.manager.execute_read(query, {"fips_code": fips_code})
        return [self._node_to_county(r['adjacent']) for r in result]
    
    def find_counties_by_risk_level(
        self, 
        min_risk: float, 
        max_risk: float,
        limit: int = 100
    ) -> List[County]:
        """Find counties within risk score range."""
        query = """
        MATCH (c:County)
        WHERE c.risk_score >= $min_risk AND c.risk_score <= $max_risk
        RETURN c
        ORDER BY c.risk_score DESC
        LIMIT $limit
        """
        
        result = self.manager.execute_read({
            "min_risk": min_risk,
            "max_risk": max_risk,
            "limit": limit
        })
        return [self._node_to_county(r['c']) for r in result]
    
    def find_counties_by_state(self, state: str) -> List[County]:
        """Find all counties in a state."""
        query = """
        MATCH (c:County {state: $state})
        RETURN c
        ORDER BY c.name
        """
        
        result = self.manager.execute_read(query, {"state": state})
        return [self._node_to_county(r['c']) for r in result]
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """Get aggregate risk statistics for all counties."""
        query = """
        MATCH (c:County)
        RETURN {
            total_counties: count(c),
            avg_risk_score: avg(c.risk_score),
            max_risk_score: max(c.risk_score),
            min_risk_score: min(c.risk_score),
            high_risk_count: count(CASE WHEN c.risk_score > 0.7 THEN 1 END),
            medium_risk_count: count(CASE WHEN c.risk_score > 0.4 AND c.risk_score <= 0.7 THEN 1 END),
            low_risk_count: count(CASE WHEN c.risk_score <= 0.4 THEN 1 END),
            total_population: sum(c.population),
            avg_resilience: avg(c.resilience_score)
        } AS stats
        """
        
        result = self.manager.execute_read(query)
        return result[0]['stats'] if result else {}
    
    def find_similar_counties(self, fips_code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find counties similar to the given county based on properties."""
        query = """
        MATCH (target:County {fips_code: $fips_code})
        MATCH (c:County)
        WHERE c.fips_code <> $fips_code
        WITH c, target,
             abs(c.population - target.population) / toFloat(target.population + 1) AS pop_diff,
             abs(c.risk_score - target.risk_score) AS risk_diff,
             abs(c.resilience_score - target.resilience_score) AS resilience_diff
        WITH c, (1 - pop_diff) * 0.3 + (1 - risk_diff) * 0.4 + (1 - resilience_diff) * 0.3 AS similarity
        RETURN c.fips_code AS fips_code,
               c.name AS name,
               c.state AS state,
               c.risk_score AS risk_score,
               similarity
        ORDER BY similarity DESC
        LIMIT $limit
        """
        
        return self.manager.execute_read(query, {
            "fips_code": fips_code,
            "limit": limit
        })
    
    def create_adjacent_relationship(
        self,
        fips_code_1: str,
        fips_code_2: str,
        border_length: Optional[float] = None,
        connectivity_score: Optional[float] = None
    ) -> bool:
        """Create ADJACENT_TO relationship between two counties."""
        query = """
        MATCH (c1:County {fips_code: $fips1})
        MATCH (c2:County {fips_code: $fips2})
        CREATE (c1)-[:ADJACENT_TO {
            border_length_miles: $border_length,
            connectivity_score: $connectivity_score,
            created_at: datetime()
        }]->(c2)
        RETURN count(*) AS created
        """
        
        result = self.manager.execute_write(query, {
            "fips1": fips_code_1,
            "fips2": fips_code_2,
            "border_length": border_length,
            "connectivity_score": connectivity_score
        })
        
        return result[0]['created'] > 0 if result else False
    
    def _node_to_county(self, node: Dict[str, Any]) -> County:
        """Convert node properties to County entity."""
        return County(
            fips_code=node.get("fips_code", ""),
            name=node.get("name", ""),
            state=node.get("state", ""),
            population=node.get("population", 0),
            area_sq_miles=node.get("area_sq_miles", 0.0),
            latitude=node.get("latitude", 0.0),
            longitude=node.get("longitude", 0.0),
            risk_score=node.get("risk_score", 0.0),
            resilience_score=node.get("resilience_score", 0.0),
            social_vulnerability_index=node.get("social_vulnerability_index", 0.0),
            geometry=node.get("geometry")
        )
