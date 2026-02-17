"""
Temporal graph operations for ResilienceAI.
Supports versioning, time-series analysis, and historical queries.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class TemporalEvent:
    """Temporal event data."""
    event_id: str
    event_type: str
    name: str
    start_time: datetime
    end_time: Optional[datetime]
    severity: str
    description: str
    affected_entities: List[str]


class TemporalGraphService:
    """Service for temporal graph operations."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def create_event(self, event: TemporalEvent) -> str:
        """
        Create a temporal event node.
        
        Args:
            event: Event data
            
        Returns:
            Event ID
        """
        query = """
        CREATE (e:Event {
            event_id: $event_id,
            event_type: $event_type,
            name: $name,
            start_time: datetime($start_time),
            end_time: CASE WHEN $end_time IS NULL THEN NULL ELSE datetime($end_time) END,
            severity: $severity,
            description: $description,
            created_at: datetime()
        })
        RETURN e.event_id
        """
        
        result = self.manager.execute_write(query, {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "name": event.name,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "severity": event.severity,
            "description": event.description
        })
        
        # Link to affected entities
        for entity_id in event.affected_entities:
            self._link_event_to_entity(event.event_id, entity_id)
        
        return result[0]['e.event_id'] if result else event.event_id
    
    def _link_event_to_entity(self, event_id: str, entity_id: str) -> None:
        """Link an event to an affected entity."""
        # Try County first
        query = """
        MATCH (e:Event {event_id: $event_id})
        MATCH (c:County {fips_code: $entity_id})
        CREATE (e)-[:AFFECTS {impact_type: 'direct'}]->(c)
        """
        result = self.manager.execute_write(query, {
            "event_id": event_id,
            "entity_id": entity_id
        })
        
        if not result:
            # Try Facility
            query = """
            MATCH (e:Event {event_id: $event_id})
            MATCH (f:Facility {facility_id: $entity_id})
            CREATE (e)-[:AFFECTS {impact_type: 'direct'}]->(f)
            """
            self.manager.execute_write(query, {
                "event_id": event_id,
                "entity_id": entity_id
            })
    
    def create_versioned_entity(
        self,
        entity_type: str,
        entity_id: str,
        properties: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> None:
        """Create a versioned entity."""
        id_property = self._get_id_property(entity_type)
        
        query = f"""
        MATCH (e:{entity_type} {{{id_property}: $entity_id}})
        OPTIONAL MATCH (e)-[:HAS_VERSION]->(latest:Version)
        WHERE latest.valid_to IS NULL
        
        // Close previous version
        WITH e, latest
        FOREACH (l IN CASE WHEN latest IS NOT NULL THEN [latest] ELSE [] END |
            SET l.valid_to = datetime()
        )
        
        // Create new version
        CREATE (v:Version)
        SET v = $properties,
            v.valid_from = datetime(),
            v.valid_to = NULL,
            v.version_number = COALESCE(latest.version_number, 0) + 1
        CREATE (e)-[:HAS_VERSION]->(v)
        
        // Link to event if provided
        WITH v
        MATCH (event:Event {{event_id: $event_id}})
        WHERE $event_id IS NOT NULL
        CREATE (v)-[:CHANGED_BY]->(event)
        """
        
        self.manager.execute_write(query, {
            "entity_id": entity_id,
            "properties": properties,
            "event_id": event_id
        })
    
    def get_entity_at_time(
        self,
        entity_type: str,
        entity_id: str,
        timestamp: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get entity state at a specific time."""
        id_property = self._get_id_property(entity_type)
        
        query = f"""
        MATCH (e:{entity_type} {{{id_property}: $entity_id}})
              -[:HAS_VERSION]->(v:Version)
        WHERE v.valid_from <= datetime($timestamp)
          AND (v.valid_to IS NULL OR v.valid_to > datetime($timestamp))
        RETURN v
        """
        
        result = self.manager.execute_read(query, {
            "entity_id": entity_id,
            "timestamp": timestamp.isoformat()
        })
        
        return result[0]['v'] if result else None
    
    def get_change_history(
        self,
        entity_type: str,
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get change history for an entity."""
        id_property = self._get_id_property(entity_type)
        
        query = f"""
        MATCH (e:{entity_type} {{{id_property}: $entity_id}})
              -[:HAS_VERSION]->(v:Version)
        OPTIONAL MATCH (v)-[:CHANGED_BY]->(event:Event)
        WHERE ($start_date IS NULL OR v.valid_from >= datetime($start_date))
          AND ($end_date IS NULL OR v.valid_from <= datetime($end_date))
        RETURN {{
            version: v.version_number,
            valid_from: v.valid_from,
            valid_to: v.valid_to,
            properties: apoc.map.removeKeys(v, ['version_number', 'valid_from', 'valid_to']),
            change_event: event {{.event_id, .event_type, .name}}
        }} AS history
        ORDER BY v.valid_from
        """
        
        result = self.manager.execute_read(query, {
            "entity_id": entity_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        })
        
        return [r['history'] for r in result]
    
    def get_risk_timeline(
        self,
        entity_id: str,
        metric_name: str = "risk_score",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get risk timeline for an entity."""
        query = """
        MATCH (c:County {fips_code: $entity_id})-[:HAS_VERSION]->(v:Version)
        WHERE v.valid_from >= datetime($start_date)
          AND v.valid_from <= datetime($end_date)
        RETURN {
            timestamp: v.valid_from,
            risk_score: v.risk_score,
            resilience_score: v.resilience_score,
            version: v.version_number
        } AS data_point
        ORDER BY v.valid_from
        """
        
        return self.manager.execute_read(query, {
            "entity_id": entity_id,
            "start_date": (start_date or datetime(2020, 1, 1)).isoformat(),
            "end_date": (end_date or datetime.now()).isoformat()
        })
    
    def find_events_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        event_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find events within a time period."""
        type_filter = "AND e.event_type = $event_type" if event_type else ""
        severity_filter = "AND e.severity = $severity" if severity else ""
        
        query = f"""
        MATCH (e:Event)
        WHERE e.start_time >= datetime($start_date)
          AND e.start_time <= datetime($end_date)
          {type_filter}
          {severity_filter}
        OPTIONAL MATCH (e)-[:AFFECTS]->(affected)
        RETURN {{
            event_id: e.event_id,
            name: e.name,
            event_type: e.event_type,
            severity: e.severity,
            start_time: e.start_time,
            end_time: e.end_time,
            affected_count: count(affected),
            affected_entities: collect(DISTINCT affected.name)
        }} AS event
        ORDER BY e.start_time DESC
        """
        
        return self.manager.execute_read(query, {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "event_type": event_type,
            "severity": severity
        })
    
    def compare_snapshots(
        self,
        entity_type: str,
        entity_id: str,
        timestamp1: datetime,
        timestamp2: datetime
    ) -> Dict[str, Any]:
        """Compare entity state at two different times."""
        id_property = self._get_id_property(entity_type)
        
        query = f"""
        MATCH (e:{entity_type} {{{id_property}: $entity_id}})
        
        // Get state at time 1
        OPTIONAL MATCH (e)-[:HAS_VERSION]->(v1:Version)
        WHERE v1.valid_from <= datetime($timestamp1)
          AND (v1.valid_to IS NULL OR v1.valid_to > datetime($timestamp1))
        
        // Get state at time 2
        OPTIONAL MATCH (e)-[:HAS_VERSION]->(v2:Version)
        WHERE v2.valid_from <= datetime($timestamp2)
          AND (v2.valid_to IS NULL OR v2.valid_to > datetime($timestamp2))
        
        RETURN {{
            entity_id: $entity_id,
            timestamp1: $timestamp1,
            timestamp2: $timestamp2,
            state1: v1 {{.risk_score, .resilience_score, .population}},
            state2: v2 {{.risk_score, .resilience_score, .population}},
            risk_change: v2.risk_score - v1.risk_score,
            resilience_change: v2.resilience_score - v1.resilience_score
        }} AS comparison
        """
        
        result = self.manager.execute_read(query, {
            "entity_id": entity_id,
            "timestamp1": timestamp1.isoformat(),
            "timestamp2": timestamp2.isoformat()
        })
        
        return result[0]['comparison'] if result else {}
    
    def _get_id_property(self, entity_type: str) -> str:
        """Get the ID property name for an entity type."""
        id_properties = {
            "County": "fips_code",
            "Facility": "facility_id",
            "Infrastructure": "infrastructure_id"
        }
        return id_properties.get(entity_type, "id")


class TemporalQueryBuilder:
    """Builder for complex temporal queries."""
    
    def __init__(self):
        self.conditions = []
        self.parameters = {}
    
    def with_time_range(
        self,
        start: datetime,
        end: datetime
    ) -> 'TemporalQueryBuilder':
        """Add time range condition."""
        self.conditions.append("e.start_time >= datetime($start_time)")
        self.conditions.append("e.start_time <= datetime($end_time)")
        self.parameters["start_time"] = start.isoformat()
        self.parameters["end_time"] = end.isoformat()
        return self
    
    def with_event_type(self, event_type: str) -> 'TemporalQueryBuilder':
        """Add event type filter."""
        self.conditions.append("e.event_type = $event_type")
        self.parameters["event_type"] = event_type
        return self
    
    def with_severity(self, severity: str) -> 'TemporalQueryBuilder':
        """Add severity filter."""
        self.conditions.append("e.severity = $severity")
        self.parameters["severity"] = severity
        return self
    
    def build(self) -> Tuple[str, Dict[str, Any]]:
        """Build the query."""
        where_clause = " AND ".join(self.conditions) if self.conditions else ""
        
        query = f"""
        MATCH (e:Event)
        {f'WHERE {where_clause}' if where_clause else ''}
        RETURN e
        ORDER BY e.start_time DESC
        """
        
        return query, self.parameters
