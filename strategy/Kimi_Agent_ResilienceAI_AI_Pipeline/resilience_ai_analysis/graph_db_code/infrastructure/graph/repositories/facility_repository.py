"""
Facility repository for graph operations.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import date

from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class Facility:
    """Facility entity."""
    facility_id: str
    name: str
    facility_type: str
    category: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    capacity: int = 0
    criticality_level: int = 1
    risk_level: str = "LOW"
    operational_status: str = "ACTIVE"
    construction_year: Optional[int] = None
    replacement_value: float = 0.0
    dependencies: List[str] = None
    county_fips: Optional[str] = None


class FacilityRepository:
    """Repository for Facility nodes."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
        self.node_label = "Facility"
        self.primary_key = "facility_id"
    
    def create(self, facility: Facility) -> Facility:
        """Create a new facility node."""
        query = """
        CREATE (f:Facility {
            facility_id: $facility_id,
            name: $name,
            facility_type: $facility_type,
            category: $category,
            latitude: $latitude,
            longitude: $longitude,
            address: $address,
            capacity: $capacity,
            criticality_level: $criticality_level,
            risk_level: $risk_level,
            operational_status: $operational_status,
            construction_year: $construction_year,
            replacement_value: $replacement_value,
            dependencies: $dependencies,
            created_at: datetime(),
            updated_at: datetime(),
            version: 1
        })
        RETURN f
        """
        
        result = self.manager.execute_write(query, {
            "facility_id": facility.facility_id,
            "name": facility.name,
            "facility_type": facility.facility_type,
            "category": facility.category,
            "latitude": facility.latitude,
            "longitude": facility.longitude,
            "address": facility.address,
            "capacity": facility.capacity,
            "criticality_level": facility.criticality_level,
            "risk_level": facility.risk_level,
            "operational_status": facility.operational_status,
            "construction_year": facility.construction_year,
            "replacement_value": facility.replacement_value,
            "dependencies": facility.dependencies or []
        })
        
        # Link to county if specified
        if facility.county_fips:
            self._link_to_county(facility.facility_id, facility.county_fips)
        
        return facility
    
    def _link_to_county(self, facility_id: str, county_fips: str) -> None:
        """Link facility to a county."""
        query = """
        MATCH (f:Facility {facility_id: $facility_id})
        MATCH (c:County {fips_code: $county_fips})
        CREATE (c)-[:CONTAINS]->(f)
        """
        
        self.manager.execute_write(query, {
            "facility_id": facility_id,
            "county_fips": county_fips
        })
    
    def find_by_id(self, facility_id: str) -> Optional[Facility]:
        """Find facility by ID."""
        query = """
        MATCH (f:Facility {facility_id: $facility_id})
        OPTIONAL MATCH (c:County)-[:CONTAINS]->(f)
        RETURN f, c.fips_code AS county_fips
        """
        
        result = self.manager.execute_read(query, {"facility_id": facility_id})
        
        if result:
            return self._node_to_facility(result[0]['f'], result[0].get('county_fips'))
        return None
    
    def find_by_county(self, county_fips: str) -> List[Facility]:
        """Find all facilities within a county."""
        query = """
        MATCH (c:County {fips_code: $county_fips})-[:CONTAINS]->(f:Facility)
        RETURN f
        """
        
        result = self.manager.execute_read(query, {"county_fips": county_fips})
        return [self._node_to_facility(r['f'], county_fips) for r in result]
    
    def find_critical_facilities(
        self, 
        min_criticality: int = 4,
        limit: int = 100
    ) -> List[Facility]:
        """Find facilities with high criticality levels."""
        query = """
        MATCH (f:Facility)
        WHERE f.criticality_level >= $min_criticality
        RETURN f
        ORDER BY f.criticality_level DESC, f.risk_level DESC
        LIMIT $limit
        """
        
        result = self.manager.execute_read({
            "min_criticality": min_criticality,
            "limit": limit
        })
        return [self._node_to_facility(r['f']) for r in result]
    
    def find_by_risk_level(
        self,
        risk_levels: List[str],
        limit: int = 100
    ) -> List[Facility]:
        """Find facilities by risk level."""
        query = """
        MATCH (f:Facility)
        WHERE f.risk_level IN $risk_levels
        RETURN f
        ORDER BY f.criticality_level DESC
        LIMIT $limit
        """
        
        result = self.manager.execute_read(query, {
            "risk_levels": risk_levels,
            "limit": limit
        })
        return [self._node_to_facility(r['f']) for r in result]
    
    def find_dependent_facilities(self, facility_id: str) -> List[Dict[str, Any]]:
        """Find facilities that depend on the given facility."""
        query = """
        MATCH (f:Facility {facility_id: $facility_id})<-[r:DEPENDS_ON]-(dependent:Facility)
        RETURN dependent {
            .*,
            dependency_type: r.dependency_type,
            criticality: r.criticality
        }
        """
        
        return self.manager.execute_read(query, {"facility_id": facility_id})
    
    def find_facilities_by_hazard(self, hazard_id: str) -> List[Dict[str, Any]]:
        """Find facilities threatened by a specific hazard."""
        query = """
        MATCH (h:Hazard {hazard_id: $hazard_id})-[t:THREATENS]->(f:Facility)
        RETURN f {.*, threat_probability: t.probability, impact_score: t.impact_score}
        ORDER BY t.impact_score DESC
        """
        
        return self.manager.execute_read(query, {"hazard_id": hazard_id})
    
    def create_dependency(
        self,
        dependent_id: str,
        provider_id: str,
        dependency_type: str,
        criticality: str = "IMPORTANT",
        redundancy: bool = False,
        max_downtime_minutes: int = 60
    ) -> bool:
        """Create DEPENDS_ON relationship between facilities."""
        query = """
        MATCH (dependent:Facility {facility_id: $dependent_id})
        MATCH (provider:Facility {facility_id: $provider_id})
        CREATE (dependent)-[:DEPENDS_ON {
            dependency_type: $dependency_type,
            criticality: $criticality,
            redundancy: $redundancy,
            max_downtime_minutes: $max_downtime_minutes,
            created_at: datetime()
        }]->(provider)
        RETURN count(*) AS created
        """
        
        result = self.manager.execute_write(query, {
            "dependent_id": dependent_id,
            "provider_id": provider_id,
            "dependency_type": dependency_type,
            "criticality": criticality,
            "redundancy": redundancy,
            "max_downtime_minutes": max_downtime_minutes
        })
        
        return result[0]['created'] > 0 if result else False
    
    def get_facility_risk_summary(self) -> Dict[str, Any]:
        """Get summary statistics for facility risks."""
        query = """
        MATCH (f:Facility)
        RETURN {
            total_facilities: count(f),
            by_risk_level: {
                critical: count(CASE WHEN f.risk_level = 'CRITICAL' THEN 1 END),
                high: count(CASE WHEN f.risk_level = 'HIGH' THEN 1 END),
                medium: count(CASE WHEN f.risk_level = 'MEDIUM' THEN 1 END),
                low: count(CASE WHEN f.risk_level = 'LOW' THEN 1 END)
            },
            by_criticality: {
                level_5: count(CASE WHEN f.criticality_level = 5 THEN 1 END),
                level_4: count(CASE WHEN f.criticality_level = 4 THEN 1 END),
                level_3: count(CASE WHEN f.criticality_level = 3 THEN 1 END),
                level_2: count(CASE WHEN f.criticality_level = 2 THEN 1 END),
                level_1: count(CASE WHEN f.criticality_level = 1 THEN 1 END)
            },
            by_status: {
                active: count(CASE WHEN f.operational_status = 'ACTIVE' THEN 1 END),
                inactive: count(CASE WHEN f.operational_status = 'INACTIVE' THEN 1 END),
                damaged: count(CASE WHEN f.operational_status = 'DAMAGED' THEN 1 END)
            },
            total_value: sum(f.replacement_value)
        } AS summary
        """
        
        result = self.manager.execute_read(query)
        return result[0]['summary'] if result else {}
    
    def update(self, facility_id: str, updates: Dict[str, Any]) -> Optional[Facility]:
        """Update facility properties."""
        from datetime import datetime
        updates['updated_at'] = datetime.now().isoformat()
        
        query = """
        MATCH (f:Facility {facility_id: $facility_id})
        SET f += $updates
        SET f.version = coalesce(f.version, 0) + 1
        RETURN f
        """
        
        result = self.manager.execute_write(query, {
            "facility_id": facility_id,
            "updates": updates
        })
        
        if result:
            return self._node_to_facility(result[0]['f'])
        return None
    
    def delete(self, facility_id: str) -> bool:
        """Delete facility by ID."""
        query = """
        MATCH (f:Facility {facility_id: $facility_id})
        DETACH DELETE f
        RETURN count(f) AS deleted
        """
        
        result = self.manager.execute_write(query, {"facility_id": facility_id})
        return result[0]['deleted'] > 0 if result else False
    
    def _node_to_facility(self, node: Dict[str, Any], county_fips: Optional[str] = None) -> Facility:
        """Convert node properties to Facility entity."""
        return Facility(
            facility_id=node.get("facility_id", ""),
            name=node.get("name", ""),
            facility_type=node.get("facility_type", ""),
            category=node.get("category", ""),
            latitude=node.get("latitude", 0.0),
            longitude=node.get("longitude", 0.0),
            address=node.get("address"),
            capacity=node.get("capacity", 0),
            criticality_level=node.get("criticality_level", 1),
            risk_level=node.get("risk_level", "LOW"),
            operational_status=node.get("operational_status", "ACTIVE"),
            construction_year=node.get("construction_year"),
            replacement_value=node.get("replacement_value", 0.0),
            dependencies=node.get("dependencies", []),
            county_fips=county_fips
        )
