# ResilienceAI Graph Database Integration Design

## Executive Summary

This document provides a comprehensive design for graph database capabilities in ResilienceAI, enabling sophisticated relationship analysis, network analytics, and knowledge graph functionality for county-level infrastructure resilience assessment.

---

## Table of Contents

1. [Graph Database Architecture](#1-graph-database-architecture)
2. [Data Models](#2-data-models)
3. [Neo4j Integration](#3-neo4j-integration)
4. [Cypher Queries](#4-cypher-queries)
5. [Graph Algorithms](#5-graph-algorithms)
6. [Knowledge Graphs](#6-knowledge-graphs)
7. [Graph Visualization](#7-graph-visualization)
8. [Graph ML Integration](#8-graph-ml-integration)
9. [Temporal Graphs](#9-temporal-graphs)
10. [Graph Versioning](#10-graph-versioning)
11. [Implementation Priority](#11-implementation-priority)

---

## 1. Graph Database Architecture

### 1.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESILIENCEAI GRAPH LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Query     │  │  Analytics  │  │    ML       │  │   Visualization     │ │
│  │   Engine    │  │   Engine    │  │  Pipeline   │  │      Engine         │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                │                    │            │
│  ┌──────┴────────────────┴────────────────┴────────────────────┴──────────┐ │
│  │                    Graph Database Abstraction Layer                      │ │
│  │         (Connection Pooling, Transaction Management, Caching)           │ │
│  └─────────────────────────────────┬──────────────────────────────────────┘ │
│                                    │                                         │
│  ┌─────────────────────────────────┴──────────────────────────────────────┐ │
│  │                         Neo4j Cluster                                   │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │   Core 1    │  │   Core 2    │  │   Core 3    │  │  Read Rep   │    │ │
│  │  │  (Leader)   │  │  (Follower) │  │  (Follower) │  │   (RR1)     │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Deployment Architecture

```yaml
# docker-compose.yml for Neo4j Cluster
version: '3.8'

services:
  neo4j-core-1:
    image: neo4j:5.14-enterprise
    container_name: neo4j-core-1
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_dbms_mode=CORE
      - NEO4J_causal__clustering_discovery__type=LIST
      - NEO4J_causal__clustering_initial__discovery__members=neo4j-core-1:5000,neo4j-core-2:5000,neo4j-core-3:5000
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_dbms_memory_heap_initial__size=4G
      - NEO4J_dbms_memory_heap_max__size=4G
      - NEO4J_dbms_memory_pagecache_size=2G
      - NEO4J_PLUGINS=["apoc", "gds", "n10s"]
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j-data-1:/data
      - neo4j-logs-1:/logs
      - ./plugins:/plugins
    networks:
      - neo4j-cluster

  neo4j-core-2:
    image: neo4j:5.14-enterprise
    container_name: neo4j-core-2
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_dbms_mode=CORE
      - NEO4J_causal__clustering_discovery__type=LIST
      - NEO4J_causal__clustering_initial__discovery__members=neo4j-core-1:5000,neo4j-core-2:5000,neo4j-core-3:5000
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
    ports:
      - "7475:7474"
      - "7688:7687"
    volumes:
      - neo4j-data-2:/data
      - neo4j-logs-2:/logs
    networks:
      - neo4j-cluster

  neo4j-core-3:
    image: neo4j:5.14-enterprise
    container_name: neo4j-core-3
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_dbms_mode=CORE
      - NEO4J_causal__clustering_discovery__type=LIST
      - NEO4J_causal__clustering_initial__discovery__members=neo4j-core-1:5000,neo4j-core-2:5000,neo4j-core-3:5000
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
    ports:
      - "7476:7474"
      - "7689:7687"
    volumes:
      - neo4j-data-3:/data
      - neo4j-logs-3:/logs
    networks:
      - neo4j-cluster

  neo4j-read-replica:
    image: neo4j:5.14-enterprise
    container_name: neo4j-read-replica
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_dbms_mode=READ_REPLICA
      - NEO4J_causal__clustering_discovery__type=LIST
      - NEO4J_causal__clustering_initial__discovery__members=neo4j-core-1:5000,neo4j-core-2:5000,neo4j-core-3:5000
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
    ports:
      - "7477:7474"
      - "7690:7687"
    volumes:
      - neo4j-data-rr:/data
      - neo4j-logs-rr:/logs
    networks:
      - neo4j-cluster

volumes:
  neo4j-data-1:
  neo4j-data-2:
  neo4j-data-3:
  neo4j-data-rr:
  neo4j-logs-1:
  neo4j-logs-2:
  neo4j-logs-3:
  neo4j-logs-rr:

networks:
  neo4j-cluster:
    driver: bridge
```

### 1.3 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Graph Database | Neo4j 5.14 Enterprise | Core graph storage and processing |
| Graph Algorithms | GDS (Graph Data Science) | Analytics and ML algorithms |
| Query Language | Cypher | Graph querying |
| Python Driver | neo4j-python-driver | Application integration |
| Visualization | D3.js/vis.js/Neo4j Bloom | Interactive graph visualization |
| ML Framework | PyTorch Geometric/DGL | Graph neural networks |
| ETL | Apache Airflow | Data pipeline orchestration |
| Caching | Redis | Query result caching |

---

## 2. Data Models

### 2.1 Core Node Types

```cypher
// County Node
CREATE CONSTRAINT county_fips IF NOT EXISTS
FOR (c:County) REQUIRE c.fips_code IS UNIQUE;

CREATE INDEX county_name IF NOT EXISTS
FOR (c:County) ON (c.name);

CREATE INDEX county_state IF NOT EXISTS
FOR (c:County) ON (c.state);

// Facility Node
CREATE CONSTRAINT facility_id IF NOT EXISTS
FOR (f:Facility) REQUIRE f.facility_id IS UNIQUE;

CREATE INDEX facility_type IF NOT EXISTS
FOR (f:Facility) ON (f.facility_type);

CREATE INDEX facility_risk_level IF NOT EXISTS
FOR (f:Facility) ON (f.risk_level);

// Infrastructure Node
CREATE CONSTRAINT infrastructure_id IF NOT EXISTS
FOR (i:Infrastructure) REQUIRE i.infrastructure_id IS UNIQUE;

// Hazard Node
CREATE CONSTRAINT hazard_id IF NOT EXISTS
FOR (h:Hazard) REQUIRE h.hazard_id IS UNIQUE;

// Organization Node
CREATE CONSTRAINT org_id IF NOT EXISTS
FOR (o:Organization) REQUIRE o.org_id IS UNIQUE;

// Event Node (for temporal graphs)
CREATE CONSTRAINT event_id IF NOT EXISTS
FOR (e:Event) REQUIRE e.event_id IS UNIQUE;

// Metric Node
CREATE CONSTRAINT metric_id IF NOT EXISTS
FOR (m:Metric) REQUIRE m.metric_id IS UNIQUE;
```

### 2.2 Node Property Schemas

```cypher
// County Properties
{
  fips_code: string,           // Unique identifier (e.g., "06037")
  name: string,                // County name
  state: string,               // State abbreviation
  state_fips: string,          // State FIPS code
  population: integer,         // Population count
  area_sq_miles: float,        // Geographic area
  latitude: float,             // Centroid latitude
  longitude: float,            // Centroid longitude
  geometry: string,            // WKT polygon
  risk_score: float,           // Overall risk score (0-1)
  resilience_score: float,     // Resilience score (0-1)
  social_vulnerability_index: float,
  created_at: datetime,        // Node creation timestamp
  updated_at: datetime,        // Last update timestamp
  version: integer             // Version for temporal tracking
}

// Facility Properties
{
  facility_id: string,         // Unique identifier
  name: string,                // Facility name
  facility_type: string,       // Type (hospital, school, etc.)
  category: string,            // Broader category
  latitude: float,
  longitude: float,
  address: string,
  capacity: integer,           // Capacity metric
  criticality_level: integer,  // 1-5 criticality scale
  risk_level: string,          // LOW, MEDIUM, HIGH, CRITICAL
  operational_status: string,  // ACTIVE, INACTIVE, DAMAGED
  construction_year: integer,
  last_inspection_date: date,
  replacement_value: float,    // Dollar value
  dependencies: [string],      // List of required services
  created_at: datetime,
  updated_at: datetime,
  version: integer
}

// Infrastructure Properties
{
  infrastructure_id: string,
  name: string,
  infrastructure_type: string, // road, bridge, power_line, etc.
  category: string,            // transportation, energy, water, etc.
  geometry: string,            // WKT line or polygon
  length_miles: float,
  capacity: float,
  condition_rating: float,     // 0-100 condition score
  age_years: integer,
  maintenance_priority: string,
  owner: string,
  risk_level: string,
  created_at: datetime,
  updated_at: datetime,
  version: integer
}

// Hazard Properties
{
  hazard_id: string,
  hazard_type: string,         // flood, earthquake, hurricane, etc.
  name: string,
  severity: string,            // LOW, MEDIUM, HIGH, EXTREME
  probability: float,          // Annual probability
  return_period: integer,      // Years (e.g., 100-year flood)
  affected_geometry: string,   // WKT of affected area
  intensity_measure: float,
  source: string,              // Data source
  created_at: datetime,
  updated_at: datetime
}

// Organization Properties
{
  org_id: string,
  name: string,
  org_type: string,            // government, utility, emergency, etc.
  jurisdiction_level: string,  // federal, state, county, local
  contact_info: map,
  capabilities: [string],      // Response capabilities
  resources: map,              // Available resources
  created_at: datetime,
  updated_at: datetime
}

// Event Properties (Temporal)
{
  event_id: string,
  event_type: string,          // disaster, inspection, maintenance
  name: string,
  start_time: datetime,
  end_time: datetime,
  severity: string,
  description: string,
  impact_assessment: map,
  source: string,
  created_at: datetime
}

// Metric Properties
{
  metric_id: string,
  metric_name: string,
  metric_type: string,         // risk, resilience, performance
  value: float,
  unit: string,
  timestamp: datetime,
  source: string,
  confidence: float,           // Confidence level (0-1)
  metadata: map                // Additional context
}
```

### 2.3 Relationship Types

```cypher
// Geographic Relationships
(:County)-[:ADJACENT_TO]->(:County)
(:County)-[:CONTAINS]->(:Facility)
(:County)-[:CONTAINS]->(:Infrastructure)

// Infrastructure Relationships
(:Facility)-[:DEPENDS_ON]->(:Facility)
(:Facility)-[:CONNECTED_BY]->(:Infrastructure)
(:Infrastructure)-[:INTERSECTS]->(:Infrastructure)
(:Infrastructure)-[:FLOWS_TO]->(:Infrastructure)

// Hazard Relationships
(:Hazard)-[:THREATENS]->(:County)
(:Hazard)-[:THREATENS]->(:Facility)
(:Hazard)-[:THREATENS]->(:Infrastructure)
(:Hazard)-[:TRIGGERS]->(:Hazard)  // Cascading hazards

// Organizational Relationships
(:Organization)-[:OPERATES]->(:Facility)
(:Organization)-[:MAINTAINS]->(:Infrastructure)
(:Organization)-[:RESPONDS_TO]->(:Hazard)
(:Organization)-[:COLLABORATES_WITH]->(:Organization)

// Temporal Relationships
(:Event)-[:AFFECTS]->(:County)
(:Event)-[:AFFECTS]->(:Facility)
(:Event)-[:AFFECTS]->(:Infrastructure)
(:Event)-[:FOLLOWS]->(:Event)  // Event sequence
(:County)-[:HAS_VERSION]->(:County)  // Temporal versioning

// Metric Relationships
(:County)-[:HAS_METRIC]->(:Metric)
(:Facility)-[:HAS_METRIC]->(:Metric)
(:Infrastructure)-[:HAS_METRIC]->(:Metric)

// Similarity Relationships (ML-generated)
(:County)-[:SIMILAR_TO {score: float}]->(:County)
(:Facility)-[:SIMILAR_TO {score: float}]->(:Facility)
```

### 2.4 Relationship Properties

```cypher
// ADJACENT_TO Properties
{
  border_length_miles: float,
  shared_population: integer,
  shared_facilities: integer,
  connectivity_score: float
}

// DEPENDS_ON Properties
{
  dependency_type: string,     // power, water, communication, etc.
  criticality: string,         // CRITICAL, IMPORTANT, NORMAL
  redundancy: boolean,         // Has backup?
  max_downtime_minutes: integer,
  distance_miles: float
}

// THREATENS Properties
{
  probability: float,          // Conditional probability
  impact_score: float,         // 0-1 impact severity
  exposure_value: float,       // Dollar exposure
  affected_population: integer
}

// CONNECTED_BY Properties
{
  distance_miles: float,
  travel_time_minutes: float,
  route_geometry: string       // WKT linestring
}

// SIMILAR_TO Properties (ML-generated)
{
  similarity_score: float,     // 0-1 similarity
  similarity_dimensions: [string], // Which features matched
  algorithm: string,           // Algorithm used
  computed_at: datetime
}
```

---

## 3. Neo4j Integration

### 3.1 Python Connection Manager

```python
# /app/infrastructure/graph/neo4j_manager.py

"""
Neo4j Connection Manager for ResilienceAI
Provides connection pooling, transaction management, and query execution.
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from functools import wraps

from neo4j import GraphDatabase, Driver, Session, Transaction
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from neo4j.graph import Node, Relationship

logger = logging.getLogger(__name__)


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j connection."""
    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "password"
    database: str = "neo4j"
    max_connection_pool_size: int = 50
    connection_timeout: int = 30
    max_transaction_retry_time: int = 30
    encrypted: bool = True


class Neo4jConnectionManager:
    """Manages Neo4j connections with pooling and retry logic."""
    
    _instance: Optional['Neo4jConnectionManager'] = None
    _driver: Optional[Driver] = None
    
    def __new__(cls, config: Optional[Neo4jConfig] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = config or Neo4jConfig()
            cls._instance._initialize_driver()
        return cls._instance
    
    def _initialize_driver(self) -> None:
        """Initialize the Neo4j driver with connection pooling."""
        try:
            self._driver = GraphDatabase.driver(
                self._config.uri,
                auth=(self._config.user, self._config.password),
                max_connection_pool_size=self._config.max_connection_pool_size,
                connection_timeout=self._config.connection_timeout,
                max_transaction_retry_time=self._config.max_transaction_retry_time,
                encrypted=self._config.encrypted
            )
            self._driver.verify_connectivity()
            logger.info(f"Neo4j driver initialized: {self._config.uri}")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    @property
    def driver(self) -> Driver:
        if self._driver is None:
            self._initialize_driver()
        return self._driver
    
    @contextmanager
    def session(self, database: Optional[str] = None):
        """Context manager for Neo4j sessions."""
        db = database or self._config.database
        session = self.driver.session(database=db)
        try:
            yield session
        finally:
            session.close()
    
    def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute a read query and return results."""
        with self.session(database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute a write query within a transaction."""
        def _execute_tx(tx: Transaction):
            result = tx.run(query, parameters or {})
            return [record.data() for record in result]
        
        with self.session(database) as session:
            return session.execute_write(_execute_tx)
    
    def bulk_insert(
        self,
        query: str,
        batch_data: List[Dict[str, Any]],
        batch_size: int = 1000,
        database: Optional[str] = None
    ) -> int:
        """Efficiently insert data in batches using UNWIND."""
        total_inserted = 0
        for i in range(0, len(batch_data), batch_size):
            batch = batch_data[i:i + batch_size]
            result = self.execute_write(query, {"batch": batch}, database)
            total_inserted += len(batch)
        return total_inserted
    
    def close(self) -> None:
        """Close the Neo4j driver and release resources."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j driver closed")


def get_neo4j_manager(config: Optional[Neo4jConfig] = None) -> Neo4jConnectionManager:
    """Get or create Neo4j connection manager instance."""
    return Neo4jConnectionManager(config)
```

### 3.2 Repository Pattern

```python
# /app/infrastructure/graph/repositories/county_repository.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class County:
    fips_code: str
    name: str
    state: str
    population: int = 0
    area_sq_miles: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    risk_score: float = 0.0
    resilience_score: float = 0.0


class CountyRepository:
    """Repository for County graph operations."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def create(self, county: County) -> County:
        query = """
        CREATE (c:County {
            fips_code: $fips_code,
            name: $name,
            state: $state,
            population: $population,
            risk_score: $risk_score,
            resilience_score: $resilience_score,
            created_at: datetime(),
            version: 1
        })
        RETURN c
        """
        result = self.manager.execute_write(query, {
            "fips_code": county.fips_code,
            "name": county.name,
            "state": county.state,
            "population": county.population,
            "risk_score": county.risk_score,
            "resilience_score": county.resilience_score
        })
        return county
    
    def find_by_id(self, fips_code: str) -> Optional[County]:
        query = "MATCH (c:County {fips_code: $fips_code}) RETURN c"
        result = self.manager.execute_read(query, {"fips_code": fips_code})
        if result:
            node = result[0]['c']
            return County(
                fips_code=node['fips_code'],
                name=node['name'],
                state=node['state'],
                population=node.get('population', 0),
                risk_score=node.get('risk_score', 0.0),
                resilience_score=node.get('resilience_score', 0.0)
            )
        return None
    
    def find_adjacent_counties(self, fips_code: str) -> List[County]:
        query = """
        MATCH (c:County {fips_code: $fips_code})-[:ADJACENT_TO]-(adjacent:County)
        RETURN adjacent
        """
        result = self.manager.execute_read(query, {"fips_code": fips_code})
        return [
            County(
                fips_code=r['adjacent']['fips_code'],
                name=r['adjacent']['name'],
                state=r['adjacent']['state']
            )
            for r in result
        ]
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        query = """
        MATCH (c:County)
        RETURN {
            total_counties: count(c),
            avg_risk_score: avg(c.risk_score),
            high_risk_count: count(CASE WHEN c.risk_score > 0.7 THEN 1 END)
        } AS stats
        """
        result = self.manager.execute_read(query)
        return result[0]['stats'] if result else {}
```

---

## 4. Cypher Queries

### 4.1 Basic Operations

```cypher
// Create County
CREATE (c:County {
    fips_code: $fips_code,
    name: $name,
    state: $state,
    population: $population,
    risk_score: $risk_score,
    created_at: datetime(),
    version: 1
})
RETURN c

// Read County by FIPS
MATCH (c:County {fips_code: $fips_code})
RETURN c

// Update County
MATCH (c:County {fips_code: $fips_code})
SET c += $updates,
    c.updated_at = datetime(),
    c.version = c.version + 1
RETURN c

// Delete County (with cascade)
MATCH (c:County {fips_code: $fips_code})
DETACH DELETE c

// Bulk Create Counties
UNWIND $batch AS county
CREATE (c:County)
SET c = county,
    c.created_at = datetime(),
    c.version = 1
RETURN count(c) AS created
```

### 4.2 Advanced Queries

```cypher
// Find cascade risk for a facility
MATCH (f:Facility {facility_id: $facility_id})<-[:DEPENDS_ON*0..]-(dependent:Facility)
OPTIONAL MATCH (h:Hazard)-[t:THREATENS]->(dependent)
RETURN 
    dependent.facility_id AS facility_id,
    dependent.name AS name,
    sum(COALESCE(t.impact_score, 0) * dependent.criticality_level) AS cascade_risk_score
ORDER BY cascade_risk_score DESC

// Find high-risk counties with critical facilities
MATCH (c:County)
WHERE c.risk_score > $risk_threshold
MATCH (c)-[:CONTAINS]->(f:Facility)
WHERE f.criticality_level >= 4
RETURN 
    c.fips_code AS county_fips,
    c.name AS county_name,
    count(f) AS critical_facility_count,
    sum(f.replacement_value) AS total_exposure
ORDER BY c.risk_score DESC

// Find shortest path between counties
MATCH (start:County {fips_code: $start_fips})
MATCH (end:County {fips_code: $end_fips})
CALL gds.shortestPath.dijkstra.stream('county-network', {
    sourceNode: id(start),
    targetNode: id(end)
})
YIELD nodeIds, totalCost
RETURN 
    [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS route,
    totalCost

// Calculate PageRank for counties
CALL gds.pageRank.stream('county-network')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS county,
       score AS influence
ORDER BY score DESC
LIMIT 20

// Community detection
CALL gds.louvain.stream('county-network')
YIELD nodeId, communityId
RETURN communityId,
       count(*) AS county_count,
       collect(gds.util.asNode(nodeId).name) AS counties
ORDER BY county_count DESC
```

---

## 5. Graph Algorithms

### 5.1 Shortest Path Service

```python
# /app/domain/analytics/graph_algorithms/shortest_path.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class PathResult:
    path: List[str]
    total_cost: float
    node_count: int
    edge_count: int
    algorithm: str


class ShortestPathService:
    """Service for shortest path calculations."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def find_shortest_path(
        self,
        start_id: str,
        end_id: str,
        node_label: str = "County",
        id_property: str = "fips_code"
    ) -> Optional[PathResult]:
        """Find shortest path between two nodes."""
        query = """
        MATCH (start:%s {%s: $start_id})
        MATCH (end:%s {%s: $end_id})
        CALL apoc.algo.dijkstra(start, end, 'ADJACENT_TO', 'distance')
        YIELD path, weight
        RETURN 
            [node IN nodes(path) | node.%s] AS path_nodes,
            weight AS total_cost,
            length(path) AS edge_count
        """ % (node_label, id_property, node_label, id_property, id_property)
        
        result = self.manager.execute_read(query, {
            "start_id": start_id, 
            "end_id": end_id
        })
        
        if not result:
            return None
        
        record = result[0]
        return PathResult(
            path=record['path_nodes'],
            total_cost=record['total_cost'],
            node_count=len(record['path_nodes']),
            edge_count=record['edge_count'],
            algorithm="dijkstra"
        )
    
    def find_k_shortest_paths(
        self,
        start_id: str,
        end_id: str,
        k: int = 3
    ) -> List[PathResult]:
        """Find K shortest paths using Yen's algorithm."""
        query = """
        MATCH (start:County {fips_code: $start_id})
        MATCH (end:County {fips_code: $end_id})
        CALL gds.shortestPath.yens.stream('county-network', {
            sourceNode: id(start),
            targetNode: id(end),
            k: $k
        })
        YIELD index, totalCost, nodeIds
        RETURN 
            index AS path_index,
            totalCost AS cost,
            [nodeId IN nodeIds | gds.util.asNode(nodeId).fips_code] AS path
        ORDER BY path_index
        """
        
        results = self.manager.execute_read(query, {
            "start_id": start_id,
            "end_id": end_id,
            "k": k
        })
        
        return [
            PathResult(
                path=r['path'],
                total_cost=r['cost'],
                node_count=len(r['path']),
                edge_count=len(r['path']) - 1,
                algorithm="yen"
            )
            for r in results
        ]
```

### 5.2 Centrality Analysis

```python
# /app/domain/analytics/graph_algorithms/centrality.py

from typing import List, Dict, Any
from dataclasses import dataclass
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class CentralityResult:
    node_id: str
    node_name: str
    score: float
    rank: int
    algorithm: str


class CentralityService:
    """Service for centrality analysis."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def calculate_pagerank(
        self,
        graph_name: str = "county-network",
        top_k: int = 20
    ) -> List[CentralityResult]:
        """Calculate PageRank scores."""
        query = """
        CALL gds.pageRank.stream($graph_name)
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS node, score
        ORDER BY score DESC
        LIMIT $top_k
        RETURN 
            node.fips_code AS node_id,
            node.name AS node_name,
            score
        """
        
        results = self.manager.execute_read(query, {
            "graph_name": graph_name,
            "top_k": top_k
        })
        
        return [
            CentralityResult(
                node_id=r['node_id'],
                node_name=r['node_name'],
                score=r['score'],
                rank=idx + 1,
                algorithm="pageRank"
            )
            for idx, r in enumerate(results)
        ]
    
    def calculate_betweenness(
        self,
        graph_name: str = "county-network",
        top_k: int = 20
    ) -> List[CentralityResult]:
        """Calculate betweenness centrality."""
        query = """
        CALL gds.betweenness.stream($graph_name)
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS node, score
        ORDER BY score DESC
        LIMIT $top_k
        RETURN 
            node.fips_code AS node_id,
            node.name AS node_name,
            score
        """
        
        results = self.manager.execute_read(query, {
            "graph_name": graph_name,
            "top_k": top_k
        })
        
        return [
            CentralityResult(
                node_id=r['node_id'],
                node_name=r['node_name'],
                score=r['score'],
                rank=idx + 1,
                algorithm="betweenness"
            )
            for idx, r in enumerate(results)
        ]
    
    def find_critical_nodes(self, graph_name: str = "county-network") -> Dict[str, Any]:
        """Find critical nodes based on multiple centrality measures."""
        query = """
        CALL gds.pageRank.stream($graph_name) YIELD nodeId, score AS pagerank
        WITH nodeId, pagerank ORDER BY pagerank DESC
        WITH collect({nodeId: nodeId, score: pagerank}) AS pageranks
        
        CALL gds.betweenness.stream($graph_name) YIELD nodeId, score AS betweenness
        WITH nodeId, betweenness, pageranks ORDER BY betweenness DESC
        WITH collect({nodeId: nodeId, score: betweenness}) AS betweennesses, pageranks
        
        UNWIND pageranks AS pr
        WITH pr, [b IN betweennesses WHERE b.nodeId = pr.nodeId][0].score AS bt
        WHERE pr.score > 0.01 OR bt > 0
        
        RETURN 
            gds.util.asNode(pr.nodeId).fips_code AS node_id,
            gds.util.asNode(pr.nodeId).name AS node_name,
            pr.score AS pagerank,
            bt AS betweenness,
            (pr.score + COALESCE(bt, 0)) / 2 AS combined_score
        ORDER BY combined_score DESC
        LIMIT 50
        """
        
        return self.manager.execute_read(query, {"graph_name": graph_name})
```

### 5.3 Community Detection

```python
# /app/domain/analytics/graph_algorithms/community_detection.py

from typing import List, Dict, Any
from dataclasses import dataclass
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class CommunityResult:
    community_id: int
    size: int
    members: List[Dict[str, Any]]
    avg_risk_score: float


class CommunityDetectionService:
    """Service for community detection analysis."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def detect_communities(
        self,
        graph_name: str = "county-network",
        min_size: int = 3
    ) -> List[CommunityResult]:
        """Detect communities using Louvain algorithm."""
        query = """
        CALL gds.louvain.stream($graph_name)
        YIELD nodeId, communityId
        WITH gds.util.asNode(nodeId) AS node, communityId
        WITH communityId,
             collect({
                 fips_code: node.fips_code,
                 name: node.name,
                 risk_score: node.risk_score
             }) AS members
        WHERE size(members) >= $min_size
        RETURN communityId,
               members,
               size(members) AS community_size,
               avg(members[0].risk_score) AS avg_risk
        ORDER BY community_size DESC
        """
        
        results = self.manager.execute_read(query, {
            "graph_name": graph_name,
            "min_size": min_size
        })
        
        return [
            CommunityResult(
                community_id=r['communityId'],
                size=r['community_size'],
                members=r['members'],
                avg_risk_score=r['avg_risk']
            )
            for r in results
        ]
```

---

## 6. Knowledge Graphs

### 6.1 Knowledge Graph Schema

```cypher
// Concept Node
(:Concept {
    concept_id: string,
    name: string,
    description: string,
    concept_type: string,
    category: string,
    synonyms: [string],
    confidence: float
})

// Document Node
(:Document {
    document_id: string,
    title: string,
    document_type: string,
    source_url: string,
    keywords: [string]
})

// Knowledge Relationships
(:Concept)-[:IS_A]->(:Concept)
(:Concept)-[:RELATED_TO]->(:Concept)
(:Document)-[:MENTIONS]->(:Concept)
(:Document)-[:CITES]->(:Document)
```

### 6.2 Knowledge Graph Builder

```python
# /app/domain/knowledge_graph/knowledge_graph_builder.py

from typing import List, Dict, Any
from dataclasses import dataclass
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


@dataclass
class Concept:
    concept_id: str
    name: str
    description: str
    concept_type: str
    category: str


class KnowledgeGraphBuilder:
    """Builds and manages the knowledge graph."""
    
    HAZARD_CONCEPTS = {
        "flood": {"synonyms": ["flooding"], "category": "natural_hazard"},
        "earthquake": {"synonyms": ["seismic"], "category": "natural_hazard"},
        "hurricane": {"synonyms": ["typhoon"], "category": "natural_hazard"},
    }
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def initialize_knowledge_base(self) -> Dict[str, int]:
        """Initialize knowledge graph with core concepts."""
        stats = {"concepts": 0}
        
        for concept_name, data in self.HAZARD_CONCEPTS.items():
            query = """
            MERGE (c:Concept {concept_id: $concept_id})
            SET c.name = $name,
                c.description = $description,
                c.concept_type = 'hazard',
                c.category = $category,
                c.synonyms = $synonyms
            """
            self.manager.execute_write(query, {
                "concept_id": f"hazard_{concept_name}",
                "name": concept_name.title(),
                "description": f"Natural hazard: {concept_name}",
                "category": data["category"],
                "synonyms": data["synonyms"]
            })
            stats["concepts"] += 1
        
        return stats
    
    def query_knowledge(self, query_text: str, max_results: int = 10) -> List[Dict]:
        """Query knowledge graph for relevant information."""
        search_query = """
        MATCH (d:Document)
        WHERE d.title CONTAINS $query OR ANY(k IN d.keywords WHERE k CONTAINS $query)
        OPTIONAL MATCH (d)-[:MENTIONS]->(c:Concept)
        RETURN d.document_id AS doc_id,
               d.title AS title,
               collect(DISTINCT c.name) AS concepts
        LIMIT $max_results
        """
        
        return self.manager.execute_read(search_query, {
            "query": query_text,
            "max_results": max_results
        })
```

---

## 7. Graph Visualization

### 7.1 D3.js Visualization

```javascript
// /app/static/js/graph-visualization.js

class ResilienceGraphVisualization {
    constructor(containerId, options = {}) {
        this.container = d3.select(`#${containerId}`);
        this.width = options.width || 800;
        this.height = options.height || 600;
        this.init();
    }
    
    init() {
        this.svg = this.container.append('svg')
            .attr('width', this.width)
            .attr('height', this.height);
        
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });
        
        this.svg.call(this.zoom);
        this.g = this.svg.append('g');
    }
    
    render(data, options = {}) {
        const { nodes, links } = data;
        const colorBy = options.colorBy || 'risk_score';
        
        this.simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2));
        
        // Render links
        this.linkElements = this.g.append('g')
            .selectAll('line')
            .data(links)
            .enter().append('line')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6);
        
        // Render nodes
        this.nodeElements = this.g.append('g')
            .selectAll('circle')
            .data(nodes)
            .enter().append('circle')
            .attr('r', d => Math.sqrt((d.population || 0) / 10000) + 5)
            .attr('fill', d => d3.interpolateReds(d.risk_score || 0))
            .call(d3.drag()
                .on('start', (e, d) => this.dragstarted(e, d))
                .on('drag', (e, d) => this.dragged(e, d))
                .on('end', (e, d) => this.dragended(e, d)));
        
        this.simulation.on('tick', () => this.ticked());
    }
    
    ticked() {
        this.linkElements
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        this.nodeElements
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
    }
    
    dragstarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    dragended(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}
```

### 7.2 Python Visualization API

```python
# /app/api/graph_visualization.py

from fastapi import APIRouter, Query
from typing import Dict, Any, Optional
import json

router = APIRouter(prefix="/api/v1/graph", tags=["graph-visualization"])


@router.get("/county-network")
async def get_county_network(
    state: Optional[str] = Query(None),
    min_risk: float = Query(0.0),
    max_nodes: int = Query(100)
):
    """Get county network data for visualization."""
    from app.infrastructure.graph.neo4j_manager import get_neo4j_manager
    
    manager = get_neo4j_manager()
    
    where_clause = "WHERE c.risk_score >= $min_risk"
    if state:
        where_clause += " AND c.state = $state"
    
    query = f"""
    MATCH (c:County)
    {where_clause}
    WITH c LIMIT $max_nodes
    OPTIONAL MATCH (c)-[r:ADJACENT_TO]-(other:County)
    WHERE other.risk_score >= $min_risk
    RETURN 
        collect(DISTINCT {{
            id: c.fips_code,
            name: c.name,
            risk_score: c.risk_score,
            population: c.population,
            type: 'County'
        }}) AS nodes,
        collect(DISTINCT {{
            source: c.fips_code,
            target: other.fips_code,
            weight: r.connectivity_score
        }}) AS links
    """
    
    result = manager.execute_read(query, {
        "state": state,
        "min_risk": min_risk,
        "max_nodes": max_nodes
    })
    
    if result:
        return {
            "nodes": result[0]['nodes'],
            "links": [l for l in result[0]['links'] if l['target']]
        }
    return {"nodes": [], "links": []}


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
            risk_level: f.risk_level,
            criticality: f.criticality_level
        }) AS nodes,
        collect(DISTINCT CASE WHEN other IS NOT NULL THEN {
            source: f.facility_id,
            target: other.facility_id,
            type: r.dependency_type
        } END) AS links
    """
    
    result = manager.execute_read(query, {"fips_code": county_fips})
    
    if result:
        return {
            "nodes": result[0]['nodes'],
            "links": [l for l in result[0]['links'] if l]
        }
    return {"nodes": [], "links": []}
```

---

## 8. Graph ML Integration

### 8.1 Node Embeddings

```python
# /app/domain/ml/graph_embeddings.py

import numpy as np
from typing import List, Dict, Any, Tuple
import torch
import torch.nn as nn
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


class GraphEmbeddingService:
    """Generate and manage graph embeddings."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def generate_fastRP_embeddings(
        self,
        graph_name: str = "county-network",
        embedding_dim: int = 128
    ) -> List[Dict[str, Any]]:
        """Generate FastRP node embeddings."""
        query = """
        CALL gds.fastRP.stream($graph_name, {
            embeddingDimension: $dim,
            iterationWeights: [0.0, 1.0, 1.0]
        })
        YIELD nodeId, embedding
        RETURN 
            gds.util.asNode(nodeId).fips_code AS node_id,
            gds.util.asNode(nodeId).name AS name,
            embedding
        """
        
        return self.manager.execute_read(query, {
            "graph_name": graph_name,
            "dim": embedding_dim
        })
    
    def generate_graphSAGE_embeddings(
        self,
        graph_name: str = "county-network",
        model_name: str = "county-sage-model",
        embedding_dim: int = 64
    ) -> List[Dict[str, Any]]:
        """Generate GraphSAGE embeddings."""
        # Train model if not exists
        train_query = """
        CALL gds.beta.graphSage.train($graph_name, {
            modelName: $model_name,
            featureProperties: ['risk_score', 'population', 'resilience_score'],
            embeddingDimension: $dim,
            aggregator: 'mean',
            activationFunction: 'sigmoid'
        })
        YIELD modelInfo
        RETURN modelInfo
        """
        
        try:
            self.manager.execute_write(train_query, {
                "graph_name": graph_name,
                "model_name": model_name,
                "dim": embedding_dim
            })
        except:
            pass  # Model may already exist
        
        # Generate embeddings
        embed_query = """
        CALL gds.beta.graphSage.stream($graph_name, {
            modelName: $model_name
        })
        YIELD nodeId, embedding
        RETURN 
            gds.util.asNode(nodeId).fips_code AS node_id,
            embedding
        """
        
        return self.manager.execute_read(embed_query, {
            "graph_name": graph_name,
            "model_name": model_name
        })
    
    def find_similar_nodes(
        self,
        node_id: str,
        embedding_type: str = "fastRP",
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar nodes using embeddings."""
        # Get embedding for target node
        query = """
        MATCH (c:County {fips_code: $node_id})
        RETURN c.embedding AS embedding
        """
        
        result = self.manager.execute_read(query, {"node_id": node_id})
        if not result or not result[0]['embedding']:
            return []
        
        target_embedding = np.array(result[0]['embedding'])
        
        # Find similar nodes using cosine similarity
        similarity_query = """
        MATCH (c:County)
        WHERE c.fips_code <> $node_id AND c.embedding IS NOT NULL
        RETURN 
            c.fips_code AS fips,
            c.name AS name,
            c.embedding AS embedding,
            gds.similarity.cosine($target_embedding, c.embedding) AS similarity
        ORDER BY similarity DESC
        LIMIT $top_k
        """
        
        return self.manager.execute_read(similarity_query, {
            "node_id": node_id,
            "target_embedding": target_embedding.tolist(),
            "top_k": top_k
        })


class GraphNeuralNetwork(nn.Module):
    """PyTorch Geometric GNN for node classification."""
    
    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int):
        super().__init__()
        self.conv1 = nn.Linear(in_channels, hidden_channels)
        self.conv2 = nn.Linear(hidden_channels, out_channels)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x, edge_index):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.conv2(x)
        return x
```

### 8.2 Link Prediction

```python
# /app/domain/ml/link_prediction.py

from typing import List, Dict, Any
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


class LinkPredictionService:
    """Predict potential links in the graph."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def predict_county_connections(
        self,
        graph_name: str = "county-network",
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Predict potential county connections."""
        query = """
        CALL gds.linkprediction.adamicAdar.stream($graph_name)
        YIELD node1, node2, score
        WHERE score >= $min_score
        RETURN 
            gds.util.asNode(node1).fips_code AS county1_fips,
            gds.util.asNode(node1).name AS county1_name,
            gds.util.asNode(node2).fips_code AS county2_fips,
            gds.util.asNode(node2).name AS county2_name,
            score AS connection_probability
        ORDER BY score DESC
        LIMIT 50
        """
        
        return self.manager.execute_read(query, {
            "graph_name": graph_name,
            "min_score": min_score
        })
    
    def predict_facility_dependencies(
        self,
        county_fips: str,
        min_probability: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Predict potential facility dependencies."""
        query = """
        MATCH (c:County {fips_code: $fips_code})-[:CONTAINS]->(f1:Facility)
        MATCH (c)-[:CONTAINS]->(f2:Facility)
        WHERE f1 <> f2
        AND NOT (f1)-[:DEPENDS_ON]-(f2)
        
        // Calculate similarity based on properties
        WITH f1, f2,
             CASE WHEN f1.facility_type = f2.facility_type THEN 0.3 ELSE 0 END +
             (1 - abs(f1.risk_score - f2.risk_score)) * 0.4 +
             (1 - abs(f1.criticality_level - f2.criticality_level) / 5.0) * 0.3 AS similarity
        WHERE similarity >= $min_prob
        
        RETURN 
            f1.facility_id AS facility1_id,
            f1.name AS facility1_name,
            f2.facility_id AS facility2_id,
            f2.name AS facility2_name,
            similarity AS dependency_probability
        ORDER BY similarity DESC
        LIMIT 20
        """
        
        return self.manager.execute_read(query, {
            "fips_code": county_fips,
            "min_prob": min_probability
        })
```

---

## 9. Temporal Graphs

### 9.1 Temporal Data Model

```cypher
// Event Node for temporal tracking
(:Event {
    event_id: string,
    event_type: string,        // disaster, inspection, maintenance, update
    name: string,
    start_time: datetime,
    end_time: datetime,
    severity: string,
    description: string,
    impact_data: map
})

// Versioned Entity Pattern
(:County)-[:HAS_VERSION]->(:CountyVersion)
(:CountyVersion)-[:PREVIOUS_VERSION]->(:CountyVersion)
(:CountyVersion)-[:CHANGED_BY]->(:Event)
```

### 9.2 Temporal Queries

```cypher
// Get entity state at specific time
MATCH (c:County {fips_code: $fips_code})-[:HAS_VERSION]->(v:CountyVersion)
WHERE v.valid_from <= datetime($timestamp) 
  AND (v.valid_to IS NULL OR v.valid_to > datetime($timestamp))
RETURN v

// Track changes over time
MATCH (c:County {fips_code: $fips_code})-[:HAS_VERSION]->(v:CountyVersion)
MATCH (v)-[:CHANGED_BY]->(e:Event)
WHERE v.valid_from >= datetime($start_date)
  AND v.valid_from <= datetime($end_date)
RETURN 
    v.valid_from AS timestamp,
    e.event_type AS change_type,
    v.risk_score AS risk_score,
    v.resilience_score AS resilience_score
ORDER BY v.valid_from

// Find events affecting a county
MATCH (c:County {fips_code: $fips_code})<-[:AFFECTS]-(e:Event)
WHERE e.start_time >= datetime($start_date)
RETURN e
ORDER BY e.start_time DESC
```

### 9.3 Temporal Service

```python
# /app/domain/temporal/temporal_graph_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


class TemporalGraphService:
    """Service for temporal graph operations."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def create_versioned_entity(
        self,
        entity_type: str,
        entity_id: str,
        properties: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> None:
        """Create a versioned entity."""
        query = f"""
        MATCH (e:{entity_type} {{{self._get_id_property(entity_type)}: $entity_id}})
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
        query = f"""
        MATCH (e:{entity_type} {{{self._get_id_property(entity_type)}: $entity_id}})
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
        query = f"""
        MATCH (e:{entity_type} {{{self._get_id_property(entity_type)}: $entity_id}})
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
    
    def _get_id_property(self, entity_type: str) -> str:
        """Get the ID property name for an entity type."""
        id_properties = {
            "County": "fips_code",
            "Facility": "facility_id",
            "Infrastructure": "infrastructure_id"
        }
        return id_properties.get(entity_type, "id")
```

---

## 10. Graph Versioning

### 10.1 Versioning Schema

```cypher
// Version Node
(:GraphVersion {
    version_id: string,
    version_number: integer,
    created_at: datetime,
    created_by: string,
    description: string,
    change_summary: map,
    is_active: boolean
})

// Snapshot relationship
(:GraphVersion)-[:CONTAINS]->(:County)
(:GraphVersion)-[:CONTAINS]->(:Facility)
```

### 10.2 Versioning Service

```python
# /app/domain/versioning/graph_versioning.py

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


class GraphVersioningService:
    """Service for graph versioning and snapshots."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def create_snapshot(
        self,
        version_name: str,
        description: str,
        created_by: str
    ) -> str:
        """Create a new graph snapshot."""
        version_id = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        query = """
        // Create version node
        CREATE (v:GraphVersion {
            version_id: $version_id,
            version_name: $version_name,
            description: $description,
            created_at: datetime(),
            created_by: $created_by,
            is_active: true
        })
        
        // Link all current entities
        WITH v
        MATCH (c:County)
        CREATE (v)-[:CONTAINS {entity_type: 'County'}]->(c)
        
        WITH v
        MATCH (f:Facility)
        CREATE (v)-[:CONTAINS {entity_type: 'Facility'}]->(f)
        
        RETURN v.version_id
        """
        
        result = self.manager.execute_write(query, {
            "version_id": version_id,
            "version_name": version_name,
            "description": description,
            "created_by": created_by
        })
        
        return result[0]['v.version_id'] if result else version_id
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all graph versions."""
        query = """
        MATCH (v:GraphVersion)
        OPTIONAL MATCH (v)-[:CONTAINS]->(c:County)
        OPTIONAL MATCH (v)-[:CONTAINS]->(f:Facility)
        RETURN {
            version_id: v.version_id,
            version_name: v.version_name,
            description: v.description,
            created_at: v.created_at,
            created_by: v.created_by,
            is_active: v.is_active,
            county_count: count(DISTINCT c),
            facility_count: count(DISTINCT f)
        } AS version
        ORDER BY v.created_at DESC
        """
        
        result = self.manager.execute_read(query)
        return [r['version'] for r in result]
    
    def restore_version(self, version_id: str) -> bool:
        """Restore graph to a specific version."""
        query = """
        // Deactivate current version
        MATCH (current:GraphVersion {is_active: true})
        SET current.is_active = false
        
        // Activate target version
        WITH current
        MATCH (target:GraphVersion {version_id: $version_id})
        SET target.is_active = true
        
        RETURN target.version_id AS restored_version
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
        
        OPTIONAL MATCH (v1)-[:CONTAINS]->(c1:County)
        WITH v1, v2, collect(DISTINCT c1.fips_code) AS counties_v1
        
        OPTIONAL MATCH (v2)-[:CONTAINS]->(c2:County)
        WITH v1, v2, counties_v1, collect(DISTINCT c2.fips_code) AS counties_v2
        
        RETURN {
            version_1: v1.version_id,
            version_2: v2.version_id,
            counties_in_v1_only: [c IN counties_v1 WHERE NOT c IN counties_v2],
            counties_in_v2_only: [c IN counties_v2 WHERE NOT c IN counties_v1],
            counties_in_both: [c IN counties_v1 WHERE c IN counties_v2],
            total_counties_v1: size(counties_v1),
            total_counties_v2: size(counties_v2)
        } AS comparison
        """
        
        result = self.manager.execute_read(query, {
            "v1": version_id_1,
            "v2": version_id_2
        })
        
        return result[0]['comparison'] if result else {}
```

---

## 11. Implementation Priority

### 11.1 Phase 1: Foundation (Weeks 1-4)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 1 | Neo4j cluster setup | Medium | High |
| 2 | Core data models (County, Facility) | Medium | High |
| 3 | Connection manager & repositories | Medium | High |
| 4 | Basic CRUD Cypher queries | Low | High |
| 5 | Schema initialization | Low | Medium |

### 11.2 Phase 2: Analytics (Weeks 5-8)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 1 | GDS graph projections | Medium | High |
| 2 | Centrality algorithms | Medium | High |
| 3 | Community detection | Medium | Medium |
| 4 | Shortest path algorithms | Medium | High |
| 5 | Path analysis service | Medium | Medium |

### 11.3 Phase 3: Advanced Features (Weeks 9-12)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 1 | Knowledge graph | High | Medium |
| 2 | Graph visualization API | Medium | Medium |
| 3 | Node embeddings | High | Medium |
| 4 | Link prediction | High | Low |
| 5 | Temporal graphs | High | Medium |

### 11.4 Phase 4: Production (Weeks 13-16)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 1 | Graph versioning | Medium | Low |
| 2 | Performance optimization | Medium | High |
| 3 | Monitoring & alerting | Medium | High |
| 4 | Documentation | Low | Medium |
| 5 | Integration testing | High | High |

---

## File Locations

All code referenced in this document should be created at:

```
/mnt/okcomputer/output/resilience_ai_analysis/
├── 43_graph_database.md (this file)
├── graph_db_code/
│   ├── docker-compose.yml
│   ├── infrastructure/
│   │   └── graph/
│   │       ├── neo4j_manager.py
│   │       └── repositories/
│   │           ├── base_repository.py
│   │           ├── county_repository.py
│   │           └── facility_repository.py
│   ├── domain/
│   │   ├── analytics/
│   │   │   └── graph_algorithms/
│   │   │       ├── shortest_path.py
│   │   │       ├── centrality.py
│   │   │       └── community_detection.py
│   │   ├── knowledge_graph/
│   │   │   └── knowledge_graph_builder.py
│   │   ├── ml/
│   │   │   ├── graph_embeddings.py
│   │   │   └── link_prediction.py
│   │   ├── temporal/
│   │   │   └── temporal_graph_service.py
│   │   └── versioning/
│   │       └── graph_versioning.py
│   ├── api/
│   │   └── graph_visualization.py
│   └── static/
│       └── js/
│           └── graph-visualization.js
```

---

## Summary

This comprehensive graph database design provides ResilienceAI with:

1. **Scalable Architecture**: Neo4j cluster with read replicas for high availability
2. **Rich Data Models**: Complete node and relationship schemas for counties, facilities, infrastructure
3. **Advanced Analytics**: Centrality, community detection, shortest path algorithms
4. **Knowledge Graph**: Semantic relationships and concept extraction
5. **Machine Learning**: Node embeddings and link prediction
6. **Temporal Support**: Version tracking and time-series analysis
7. **Visualization**: Interactive D3.js components with Python API
8. **Versioning**: Snapshot and rollback capabilities

The implementation follows a phased approach, prioritizing foundational components before advancing to complex analytics and ML features.
