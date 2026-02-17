"""
Graph versioning and snapshot management for ResilienceAI.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class GraphVersion:
    """Graph version metadata."""
    version_id: str
    version_name: str
    description: str
    created_at: datetime
    created_by: str
    is_active: bool


class GraphVersioningService:
    """Service for graph versioning and snapshots."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def create_snapshot(
        self,
        version_name: str,
        description: str,
        created_by: str,
        include_metrics: bool = True
    ) -> str:
        """
        Create a new graph snapshot.
        
        Args:
            version_name: Name for this version
            description: Version description
            created_by: User creating the snapshot
            include_metrics: Whether to include metrics in snapshot
            
        Returns:
            Version ID
        """
        version_id = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        query = """
        // Create version node
        CREATE (v:GraphVersion {
            version_id: $version_id,
            version_name: $version_name,
            description: $description,
            created_at: datetime(),
            created_by: $created_by,
            is_active: true,
            include_metrics: $include_metrics
        })
        
        // Link all current entities
        WITH v
        MATCH (c:County)
        CREATE (v)-[:CONTAINS {entity_type: 'County', entity_id: c.fips_code}]->(c)
        
        WITH v
        MATCH (f:Facility)
        CREATE (v)-[:CONTAINS {entity_type: 'Facility', entity_id: f.facility_id}]->(f)
        
        WITH v
        MATCH (i:Infrastructure)
        CREATE (v)-[:CONTAINS {entity_type: 'Infrastructure', entity_id: i.infrastructure_id}]->(i)
        
        RETURN v.version_id
        """
        
        result = self.manager.execute_write(query, {
            "version_id": version_id,
            "version_name": version_name,
            "description": description,
            "created_by": created_by,
            "include_metrics": include_metrics
        })
        
        return result[0]['v.version_id'] if result else version_id
    
    def list_versions(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """List all graph versions."""
        where_clause = "" if include_inactive else "WHERE v.is_active = true"
        
        query = f"""
        MATCH (v:GraphVersion)
        {where_clause}
        OPTIONAL MATCH (v)-[:CONTAINS]->(c:County)
        OPTIONAL MATCH (v)-[:CONTAINS]->(f:Facility)
        OPTIONAL MATCH (v)-[:CONTAINS]->(i:Infrastructure)
        RETURN {{
            version_id: v.version_id,
            version_name: v.version_name,
            description: v.description,
            created_at: v.created_at,
            created_by: v.created_by,
            is_active: v.is_active,
            county_count: count(DISTINCT c),
            facility_count: count(DISTINCT f),
            infrastructure_count: count(DISTINCT i)
        }} AS version
        ORDER BY v.created_at DESC
        """
        
        result = self.manager.execute_read(query)
        return [r['version'] for r in result]
    
    def get_version_details(self, version_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific version."""
        query = """
        MATCH (v:GraphVersion {version_id: $version_id})
        OPTIONAL MATCH (v)-[r:CONTAINS]->(entity)
        RETURN {
            version_id: v.version_id,
            version_name: v.version_name,
            description: v.description,
            created_at: v.created_at,
            created_by: v.created_by,
            is_active: v.is_active,
            entities: collect({
                type: r.entity_type,
                id: r.entity_id,
                name: entity.name
            })
        } AS details
        """
        
        result = self.manager.execute_read(query, {"version_id": version_id})
        return result[0]['details'] if result else {}
    
    def activate_version(self, version_id: str) -> bool:
        """Activate a specific version."""
        query = """
        // Deactivate all versions
        MATCH (v:GraphVersion)
        WHERE v.is_active = true
        SET v.is_active = false
        
        // Activate target version
        WITH count(*) AS deactivated
        MATCH (target:GraphVersion {version_id: $version_id})
        SET target.is_active = true
        
        RETURN target.version_id AS activated_version
        """
        
        result = self.manager.execute_write(query, {"version_id": version_id})
        return len(result) > 0
    
    def delete_version(self, version_id: str) -> bool:
        """Delete a version (soft delete by marking inactive)."""
        query = """
        MATCH (v:GraphVersion {version_id: $version_id})
        SET v.is_active = false,
            v.deleted_at = datetime()
        RETURN v.version_id
        """
        
        result = self.manager.execute_write(query, {"version_id": version_id})
        return len(result) > 0
    
    def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """Compare two graph versions."""
        query = """
        MATCH (v1:GraphVersion {version_id: $v1})
        MATCH (v2:GraphVersion {version_id: $v2})
        
        // Get counties in each version
        OPTIONAL MATCH (v1)-[:CONTAINS]->(c1:County)
        WITH v1, v2, collect(DISTINCT c1.fips_code) AS counties_v1
        
        OPTIONAL MATCH (v2)-[:CONTAINS]->(c2:County)
        WITH v1, v2, counties_v1, collect(DISTINCT c2.fips_code) AS counties_v2
        
        // Get facilities in each version
        OPTIONAL MATCH (v1)-[:CONTAINS]->(f1:Facility)
        WITH v1, v2, counties_v1, counties_v2, collect(DISTINCT f1.facility_id) AS facilities_v1
        
        OPTIONAL MATCH (v2)-[:CONTAINS]->(f2:Facility)
        WITH v1, v2, counties_v1, counties_v2, facilities_v1, collect(DISTINCT f2.facility_id) AS facilities_v2
        
        RETURN {
            version_1: v1.version_id,
            version_1_name: v1.version_name,
            version_2: v2.version_id,
            version_2_name: v2.version_name,
            counties: {
                in_v1_only: [c IN counties_v1 WHERE NOT c IN counties_v2],
                in_v2_only: [c IN counties_v2 WHERE NOT c IN counties_v1],
                in_both: [c IN counties_v1 WHERE c IN counties_v2],
                total_v1: size(counties_v1),
                total_v2: size(counties_v2)
            },
            facilities: {
                in_v1_only: [f IN facilities_v1 WHERE NOT f IN facilities_v2],
                in_v2_only: [f IN facilities_v2 WHERE NOT f IN facilities_v1],
                in_both: [f IN facilities_v1 WHERE f IN facilities_v2],
                total_v1: size(facilities_v1),
                total_v2: size(facilities_v2)
            }
        } AS comparison
        """
        
        result = self.manager.execute_read(query, {
            "v1": version_id_1,
            "v2": version_id_2
        })
        
        return result[0]['comparison'] if result else {}
    
    def export_version(
        self,
        version_id: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export a version to a portable format."""
        query = """
        MATCH (v:GraphVersion {version_id: $version_id})
        OPTIONAL MATCH (v)-[:CONTAINS]->(c:County)
        OPTIONAL MATCH (v)-[:CONTAINS]->(f:Facility)
        OPTIONAL MATCH (c)-[r:ADJACENT_TO]-(other:County)
        WHERE other IN [(v)-[:CONTAINS]->(:County) | endNode(rel)]
        
        RETURN {
            version_id: v.version_id,
            version_name: v.version_name,
            created_at: v.created_at,
            counties: [c in collect(DISTINCT c) | c {.*}],
            facilities: [f in collect(DISTINCT f) | f {.*}],
            relationships: [r in collect(DISTINCT r) | {
                type: type(r),
                from: startNode(r).fips_code,
                to: endNode(r).fips_code,
                properties: properties(r)
            }]
        } AS export
        """
        
        result = self.manager.execute_read(query, {"version_id": version_id})
        return result[0]['export'] if result else {}
    
    def import_version(
        self,
        version_data: Dict[str, Any],
        created_by: str
    ) -> str:
        """Import a version from exported data."""
        # Create new version
        version_id = self.create_snapshot(
            version_name=f"imported_{version_data.get('version_name', 'unknown')}",
            description=f"Imported from export of {version_data.get('version_id')}",
            created_by=created_by
        )
        
        # Import counties
        counties = version_data.get('counties', [])
        for county in counties:
            query = """
            MATCH (v:GraphVersion {version_id: $version_id})
            MERGE (c:County {fips_code: $fips_code})
            SET c += $properties
            CREATE (v)-[:CONTAINS {entity_type: 'County'}]->(c)
            """
            self.manager.execute_write(query, {
                "version_id": version_id,
                "fips_code": county.get('fips_code'),
                "properties": county
            })
        
        return version_id


class VersionDiffAnalyzer:
    """Analyze differences between graph versions."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def analyze_property_changes(
        self,
        version_id_1: str,
        version_id_2: str,
        entity_type: str = "County",
        property_name: str = "risk_score"
    ) -> List[Dict[str, Any]]:
        """Analyze how a property changed between versions."""
        query = """
        MATCH (v1:GraphVersion {version_id: $v1})-[:CONTAINS]->(e1:County)
        MATCH (v2:GraphVersion {version_id: $v2})-[:CONTAINS]->(e2:County)
        WHERE e1.fips_code = e2.fips_code
        RETURN {
            entity_id: e1.fips_code,
            entity_name: e1.name,
            value_v1: e1[$property],
            value_v2: e2[$property],
            change: e2[$property] - e1[$property],
            percent_change: CASE WHEN e1[$property] <> 0 
                            THEN (e2[$property] - e1[$property]) / e1[$property] * 100 
                            ELSE NULL END
        } AS change
        ORDER BY ABS(change) DESC
        """
        
        return self.manager.execute_read(query, {
            "v1": version_id_1,
            "v2": version_id_2,
            "property": property_name
        })
    
    def find_new_entities(
        self,
        version_id_1: str,
        version_id_2: str,
        entity_type: str = "Facility"
    ) -> List[Dict[str, Any]]:
        """Find entities added in version 2."""
        query = """
        MATCH (v2:GraphVersion {version_id: $v2})-[:CONTAINS]->(e2:Facility)
        WHERE NOT EXISTS {
            MATCH (v1:GraphVersion {version_id: $v1})-[:CONTAINS]->(e1:Facility)
            WHERE e1.facility_id = e2.facility_id
        }
        RETURN {
            facility_id: e2.facility_id,
            name: e2.name,
            facility_type: e2.facility_type,
            added_in_version: $v2
        } AS new_entity
        """
        
        return self.manager.execute_read(query, {
            "v1": version_id_1,
            "v2": version_id_2
        })
    
    def find_removed_entities(
        self,
        version_id_1: str,
        version_id_2: str,
        entity_type: str = "Facility"
    ) -> List[Dict[str, Any]]:
        """Find entities removed in version 2."""
        query = """
        MATCH (v1:GraphVersion {version_id: $v1})-[:CONTAINS]->(e1:Facility)
        WHERE NOT EXISTS {
            MATCH (v2:GraphVersion {version_id: $v2})-[:CONTAINS]->(e2:Facility)
            WHERE e2.facility_id = e1.facility_id
        }
        RETURN {
            facility_id: e1.facility_id,
            name: e1.name,
            facility_type: e1.facility_type,
            removed_after_version: $v1
        } AS removed_entity
        """
        
        return self.manager.execute_read(query, {
            "v1": version_id_1,
            "v2": version_id_2
        })
