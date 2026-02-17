# ResilienceAI Data Governance Framework

## Executive Summary

This document provides a comprehensive data governance framework for ResilienceAI, designed to ensure data quality, security, compliance, and accessibility across all data assets. The framework addresses the unique challenges of AI-driven disaster resilience platforms, including multi-source data integration, real-time processing requirements, and strict regulatory compliance.

---

## Table of Contents

1. [Data Governance Framework Overview](#1-data-governance-framework-overview)
2. [Data Catalog Implementation](#2-data-catalog-implementation)
3. [Data Lineage Tracking](#3-data-lineage-tracking)
4. [Data Dictionary Management](#4-data-dictionary-management)
5. [Metadata Management](#5-metadata-management)
6. [Data Quality Rules](#6-data-quality-rules)
7. [Access Control Policies](#7-access-control-policies)
8. [Data Retention Policies](#8-data-retention-policies)
9. [Compliance Tracking](#9-compliance-tracking)
10. [Data Stewardship](#10-data-stewardship)
11. [Governance Workflows](#11-governance-workflows)
12. [Tool Selection & Implementation](#12-tool-selection--implementation)
13. [Monitoring & Auditing](#13-monitoring--auditing)
14. [Implementation Roadmap](#14-implementation-roadmap)

---

## 1. Data Governance Framework Overview

### 1.1 Governance Principles

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Accountability** | Clear ownership of data assets | Data stewards assigned per domain |
| **Transparency** | Visible data practices | Public documentation, audit trails |
| **Integrity** | Accurate, consistent data | Quality checks, validation rules |
| **Security** | Protected data assets | Encryption, access controls |
| **Compliance** | Regulatory adherence | Automated compliance monitoring |
| **Usability** | Accessible, well-documented data | Data catalog, clear metadata |

### 1.2 Governance Organization Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA GOVERNANCE COUNCIL                   │
│         (Executive sponsorship, strategic decisions)          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Data Stewards │    │ Data Custodians│    │ Data Users    │
│  (Business)    │    │  (Technical)   │    │  (Consumers)  │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Domain Owners  │    │  Data Engineers│    │  Data Analysts│
└───────────────┘    └───────────────┘    └───────────────┘
```

### 1.3 Data Domains

| Domain | Description | Owner | Criticality |
|--------|-------------|-------|-------------|
| **Geospatial** | Maps, satellite imagery, coordinates | Geo Team | Critical |
| **Sensor Data** | IoT readings, weather stations | IoT Team | Critical |
| **Incident Reports** | Disaster events, damage assessments | Operations | Critical |
| **Demographics** | Population data, vulnerable groups | Analytics | High |
| **Infrastructure** | Buildings, roads, utilities | Planning | High |
| **Historical** | Past events, lessons learned | Research | Medium |
| **External APIs** | Third-party data feeds | Integration | High |

### 1.4 Governance Policies Framework

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/config/governance_policies.yaml
governance_framework:
  version: "1.0.0"
  last_updated: "2024-01-15"
  
  policies:
    data_classification:
      levels:
        - name: "Public"
          description: "Data available to all users"
          examples: ["published reports", "aggregated statistics"]
        - name: "Internal"
          description: "Data for internal use only"
          examples: ["operational dashboards", "internal analytics"]
        - name: "Confidential"
          description: "Sensitive data requiring protection"
          examples: ["personal information", "vulnerability assessments"]
        - name: "Restricted"
          description: "Highly sensitive data with strict controls"
          examples: ["security protocols", "emergency response plans"]
    
    data_quality:
      dimensions:
        - accuracy: "Data correctly represents real-world values"
        - completeness: "All required data is present"
        - consistency: "Data is uniform across systems"
        - timeliness: "Data is current and up-to-date"
        - validity: "Data conforms to defined formats"
        - uniqueness: "No duplicate records exist"
    
    data_retention:
      default_retention: "7_years"
      categories:
        - type: "incident_data"
          retention: "10_years"
          justification: "Regulatory requirement for disaster records"
        - type: "sensor_data"
          retention: "3_years"
          justification: "High volume, aggregated for long-term"
        - type: "personal_data"
          retention: "2_years_after_relationship_end"
          justification: "Privacy regulations"
```

---

## 2. Data Catalog Implementation

### 2.1 Catalog Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                      DATA CATALOG PLATFORM                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Metadata   │  │   Search &   │  │   Lineage    │              │
│  │   Store      │  │   Discovery  │  │   Engine     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Data       │  │   Quality    │  │   Access     │              │
│  │   Profiling  │  │   Dashboard  │  │   Control    │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Data Sources  │    │  Data Assets   │    │   Data Users   │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 2.2 Catalog Data Model

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/data_catalog/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class DataAssetType(str, Enum):
    TABLE = "table"
    VIEW = "view"
    DATASET = "dataset"
    MODEL = "model"
    REPORT = "report"
    API = "api"
    FILE = "file"
    STREAM = "stream"

class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class DataAsset(BaseModel):
    """Core data asset model for the catalog"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Asset name")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Detailed description")
    asset_type: DataAssetType
    classification: DataClassification
    
    # Ownership
    owner: str = Field(..., description="Data steward/owner")
    domain: str = Field(..., description="Business domain")
    team: str = Field(..., description="Responsible team")
    
    # Location
    source_system: str
    database: Optional[str] = None
    schema: Optional[str] = None
    location: str = Field(..., description="Physical location/path")
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    last_profiled: Optional[datetime] = None
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    
    # Tags and labels
    tags: List[str] = []
    labels: Dict[str, str] = {}
    
    # Quality metrics
    quality_score: Optional[float] = Field(None, ge=0, le=100)
    quality_status: Optional[str] = None
    
    # Lineage
    upstream_assets: List[str] = []
    downstream_assets: List[str] = []
    
    # Access
    access_level: str = "restricted"
    access_request_url: Optional[str] = None
    
    # Compliance
    pii_detected: bool = False
    retention_policy: Optional[str] = None
    compliance_tags: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "id": "geo-satellite-imagery-001",
                "name": "satellite_imagery",
                "display_name": "Satellite Imagery Dataset",
                "description": "High-resolution satellite imagery for disaster monitoring",
                "asset_type": "dataset",
                "classification": "internal",
                "owner": "geo-team@resilience.ai",
                "domain": "geospatial",
                "team": "geospatial",
                "source_system": "aws-s3",
                "location": "s3://resilience-ai-data/satellite/",
                "tags": ["imagery", "satellite", "disaster"],
                "quality_score": 95.5
            }
        }

class ColumnMetadata(BaseModel):
    """Column-level metadata"""
    name: str
    data_type: str
    description: str
    is_nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_pii: bool = False
    is_sensitive: bool = False
    sample_values: List[Any] = []
    distinct_count: Optional[int] = None
    null_count: Optional[int] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    patterns: List[str] = []  # Regex patterns for validation

class DataAssetDetail(DataAsset):
    """Extended asset with column-level details"""
    columns: List[ColumnMetadata] = []
    sample_data: List[Dict[str, Any]] = []
    schema_version: str = "1.0"
    schema_changes: List[Dict[str, Any]] = []
    
    # Business context
    business_terms: List[str] = []
    kpis: List[str] = []
    related_reports: List[str] = []
    data_steward_notes: str = ""

class SearchResult(BaseModel):
    """Catalog search result"""
    asset: DataAsset
    score: float
    matched_fields: List[str]
    highlights: Dict[str, str]
```

### 2.3 Catalog Service Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/data_catalog/catalog_service.py

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import elasticsearch
from sqlalchemy import create_engine, text
from .models import DataAsset, DataAssetDetail, ColumnMetadata, SearchResult

class DataCatalogService:
    """
    Central data catalog service for ResilienceAI
    Manages metadata, search, and discovery of data assets
    """
    
    def __init__(self, 
                 es_host: str = "localhost:9200",
                 db_connection: str = None):
        self.es = elasticsearch.Elasticsearch([es_host])
        self.db_engine = create_engine(db_connection) if db_connection else None
        self.index_name = "resilienceai-data-catalog"
    
    def register_asset(self, asset: DataAsset) -> bool:
        """Register a new data asset in the catalog"""
        try:
            # Index in Elasticsearch for search
            self.es.index(
                index=self.index_name,
                id=asset.id,
                body=asset.dict()
            )
            
            # Store in relational DB for structured queries
            if self.db_engine:
                self._store_in_database(asset)
            
            return True
        except Exception as e:
            print(f"Error registering asset: {e}")
            return False
    
    def search_assets(self, 
                      query: str,
                      filters: Optional[Dict[str, Any]] = None,
                      size: int = 20) -> List[SearchResult]:
        """Search for data assets"""
        
        # Build Elasticsearch query
        es_query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "name^3",
                                "display_name^3", 
                                "description^2",
                                "tags^2",
                                "domain",
                                "team"
                            ],
                            "type": "best_fields",
                            "fuzziness": "AUTO"
                        }
                    }
                ],
                "filter": []
            }
        }
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                es_query["bool"]["filter"].append({"term": {key: value}})
        
        response = self.es.search(
            index=self.index_name,
            body={
                "query": es_query,
                "size": size,
                "highlight": {
                    "fields": {
                        "name": {},
                        "description": {},
                        "tags": {}
                    }
                }
            }
        )
        
        results = []
        for hit in response["hits"]["hits"]:
            asset = DataAsset(**hit["_source"])
            result = SearchResult(
                asset=asset,
                score=hit["_score"],
                matched_fields=list(hit.get("highlight", {}).keys()),
                highlights=hit.get("highlight", {})
            )
            results.append(result)
        
        return results
    
    def get_asset_by_id(self, asset_id: str) -> Optional[DataAssetDetail]:
        """Get detailed information about a specific asset"""
        try:
            response = self.es.get(index=self.index_name, id=asset_id)
            return DataAssetDetail(**response["_source"])
        except elasticsearch.NotFoundError:
            return None
    
    def get_assets_by_domain(self, domain: str) -> List[DataAsset]:
        """Get all assets for a specific domain"""
        response = self.es.search(
            index=self.index_name,
            body={
                "query": {"term": {"domain": domain}},
                "size": 1000
            }
        )
        return [DataAsset(**hit["_source"]) for hit in response["hits"]["hits"]]
    
    def update_quality_score(self, asset_id: str, score: float, status: str):
        """Update quality metrics for an asset"""
        self.es.update(
            index=self.index_name,
            id=asset_id,
            body={
                "doc": {
                    "quality_score": score,
                    "quality_status": status,
                    "last_quality_check": datetime.utcnow().isoformat()
                }
            }
        )
    
    def get_data_lineage(self, asset_id: str) -> Dict[str, List[DataAsset]]:
        """Get upstream and downstream lineage for an asset"""
        asset = self.get_asset_by_id(asset_id)
        if not asset:
            return {"upstream": [], "downstream": []}
        
        upstream = []
        downstream = []
        
        for up_id in asset.upstream_assets:
            up_asset = self.get_asset_by_id(up_id)
            if up_asset:
                upstream.append(up_asset)
        
        for down_id in asset.downstream_assets:
            down_asset = self.get_asset_by_id(down_id)
            if down_asset:
                downstream.append(down_asset)
        
        return {"upstream": upstream, "downstream": downstream}
    
    def _store_in_database(self, asset: DataAsset):
        """Store asset metadata in relational database"""
        with self.db_engine.connect() as conn:
            query = text("""
                INSERT INTO data_catalog.assets 
                (id, name, display_name, description, asset_type, classification,
                 owner, domain, team, source_system, location, tags, quality_score,
                 created_at, updated_at)
                VALUES 
                (:id, :name, :display_name, :description, :asset_type, :classification,
                 :owner, :domain, :team, :source_system, :location, :tags, :quality_score,
                 :created_at, :updated_at)
                ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                display_name = EXCLUDED.display_name,
                description = EXCLUDED.description,
                quality_score = EXCLUDED.quality_score,
                updated_at = EXCLUDED.updated_at
            """)
            conn.execute(query, asset.dict())
            conn.commit()
    
    def get_popular_assets(self, limit: int = 10) -> List[DataAsset]:
        """Get most accessed assets"""
        response = self.es.search(
            index=self.index_name,
            body={
                "sort": [{"access_count": {"order": "desc"}}],
                "size": limit
            }
        )
        return [DataAsset(**hit["_source"]) for hit in response["hits"]["hits"]]
    
    def get_assets_by_quality_status(self, status: str) -> List[DataAsset]:
        """Get assets filtered by quality status"""
        response = self.es.search(
            index=self.index_name,
            body={
                "query": {"term": {"quality_status": status}},
                "size": 1000
            }
        )
        return [DataAsset(**hit["_source"]) for hit in response["hits"]["hits"]]
```

### 2.4 Catalog UI API

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/data_catalog/api.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .catalog_service import DataCatalogService
from .models import DataAsset, DataAssetDetail, SearchResult

app = FastAPI(title="ResilienceAI Data Catalog API")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize catalog service
catalog = DataCatalogService(
    es_host="elasticsearch:9200",
    db_connection="postgresql://user:pass@postgres/catalog"
)

@app.get("/api/v1/search", response_model=List[SearchResult])
async def search(
    q: str = Query(..., description="Search query"),
    domain: Optional[str] = None,
    classification: Optional[str] = None,
    asset_type: Optional[str] = None,
    size: int = 20
):
    """Search the data catalog"""
    filters = {}
    if domain:
        filters["domain"] = domain
    if classification:
        filters["classification"] = classification
    if asset_type:
        filters["asset_type"] = asset_type
    
    return catalog.search_assets(q, filters, size)

@app.get("/api/v1/assets/{asset_id}", response_model=DataAssetDetail)
async def get_asset(asset_id: str):
    """Get detailed asset information"""
    asset = catalog.get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@app.get("/api/v1/domains/{domain}/assets", response_model=List[DataAsset])
async def get_domain_assets(domain: str):
    """Get all assets in a domain"""
    return catalog.get_assets_by_domain(domain)

@app.get("/api/v1/assets/{asset_id}/lineage")
async def get_lineage(asset_id: str):
    """Get data lineage for an asset"""
    return catalog.get_data_lineage(asset_id)

@app.get("/api/v1/domains")
async def get_domains():
    """Get list of all domains"""
    return [
        {"id": "geospatial", "name": "Geospatial", "asset_count": 45},
        {"id": "sensor", "name": "Sensor Data", "asset_count": 128},
        {"id": "incident", "name": "Incident Reports", "asset_count": 67},
        {"id": "demographics", "name": "Demographics", "asset_count": 23},
        {"id": "infrastructure", "name": "Infrastructure", "asset_count": 89},
        {"id": "historical", "name": "Historical Data", "asset_count": 34}
    ]

@app.get("/api/v1/stats")
async def get_catalog_stats():
    """Get catalog statistics"""
    return {
        "total_assets": 386,
        "by_type": {
            "table": 145,
            "dataset": 98,
            "api": 67,
            "model": 45,
            "report": 31
        },
        "by_classification": {
            "public": 45,
            "internal": 234,
            "confidential": 89,
            "restricted": 18
        },
        "quality_summary": {
            "excellent": 245,
            "good": 98,
            "needs_attention": 32,
            "critical": 11
        }
    }
```

---

## 3. Data Lineage Tracking

### 3.1 Lineage Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA LINEAGE PLATFORM                            │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   Lineage    │    │   Impact     │    │   Data       │          │
│   │   Graph      │    │   Analysis   │    │   Flow       │          │
│   │   (Neo4j)    │    │   Engine     │    │   Visualizer │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   Open       │    │   Custom     │    │   ML Model   │          │
│   │   Lineage    │    │   Parsers    │    │   Lineage    │          │
│   │   Integration│    │              │    │   Tracker    │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Lineage Models

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/lineage/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class NodeType(str, Enum):
    DATASET = "dataset"
    TABLE = "table"
    COLUMN = "column"
    JOB = "job"
    MODEL = "model"
    REPORT = "report"
    API = "api"
    FILE = "file"

class EdgeType(str, Enum):
    DERIVED_FROM = "derived_from"
    CONSUMES = "consumes"
    PRODUCES = "produces"
    TRANSFORMS = "transforms"
    COPIES = "copies"
    REFERENCES = "references"

class LineageNode(BaseModel):
    """Node in the lineage graph"""
    id: str
    name: str
    node_type: NodeType
    platform: str  # e.g., "bigquery", "s3", "spark", "airflow"
    location: str
    
    # Metadata
    owner: str
    domain: str
    description: Optional[str] = None
    tags: List[str] = []
    
    # Temporal
    created_at: datetime
    updated_at: datetime
    
    # Additional properties
    properties: Dict[str, Any] = {}

class LineageEdge(BaseModel):
    """Edge connecting nodes in lineage graph"""
    source_id: str
    target_id: str
    edge_type: EdgeType
    
    # Transformation details
    transformation_logic: Optional[str] = None
    transformation_sql: Optional[str] = None
    
    # Metadata
    created_at: datetime
    confidence: float = Field(1.0, ge=0, le=1)
    
    # Additional context
    properties: Dict[str, Any] = {}

class LineageGraph(BaseModel):
    """Complete lineage subgraph"""
    root_node: LineageNode
    upstream_nodes: List[LineageNode]
    downstream_nodes: List[LineageNode]
    edges: List[LineageEdge]
    
    # Analysis
    depth_upstream: int
    depth_downstream: int
    total_nodes: int

class ImpactAnalysis(BaseModel):
    """Impact analysis result"""
    source_node: LineageNode
    affected_nodes: List[LineageNode]
    critical_paths: List[List[str]]  # Node ID paths
    blast_radius: int  # Total affected nodes
    
    # Categorization
    affected_datasets: List[str]
    affected_reports: List[str]
    affected_models: List[str]
    
    # Risk assessment
    risk_level: str  # "low", "medium", "high", "critical"
    estimated_recovery_time: Optional[str] = None

class DataFlow(BaseModel):
    """Data flow visualization data"""
    nodes: List[Dict[str, Any]]  # For D3.js/vis.js
    edges: List[Dict[str, Any]]
    layout: str = "hierarchical"
```

### 3.3 Lineage Service Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/lineage/lineage_service.py

from neo4j import GraphDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import LineageNode, LineageEdge, LineageGraph, ImpactAnalysis

class LineageService:
    """
    Data lineage tracking service using Neo4j graph database
    Tracks data flow from source to consumption
    """
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_node(self, node: LineageNode):
        """Create or update a lineage node"""
        with self.driver.session() as session:
            session.run("""
                MERGE (n:LineageNode {id: $id})
                SET n.name = $name,
                    n.node_type = $node_type,
                    n.platform = $platform,
                    n.location = $location,
                    n.owner = $owner,
                    n.domain = $domain,
                    n.description = $description,
                    n.tags = $tags,
                    n.created_at = $created_at,
                    n.updated_at = $updated_at
            """, **node.dict())
    
    def create_edge(self, edge: LineageEdge):
        """Create a lineage relationship"""
        with self.driver.session() as session:
            session.run("""
                MATCH (source:LineageNode {id: $source_id})
                MATCH (target:LineageNode {id: $target_id})
                MERGE (source)-[r:LINEAGE {edge_type: $edge_type}]->(target)
                SET r.transformation_logic = $transformation_logic,
                    r.transformation_sql = $transformation_sql,
                    r.created_at = $created_at,
                    r.confidence = $confidence
            """, **edge.dict())
    
    def get_lineage(self, node_id: str, 
                    upstream_depth: int = 5,
                    downstream_depth: int = 5) -> LineageGraph:
        """Get complete lineage for a node"""
        with self.driver.session() as session:
            # Get root node
            root_result = session.run("""
                MATCH (n:LineageNode {id: $node_id})
                RETURN n
            """, node_id=node_id).single()
            
            if not root_result:
                raise ValueError(f"Node {node_id} not found")
            
            root_node = LineageNode(**root_result["n"])
            
            # Get upstream lineage
            upstream_result = session.run("""
                MATCH path = (upstream:LineageNode)-[:LINEAGE*1..$depth]->(n:LineageNode {id: $node_id})
                RETURN upstream, relationships(path) as edges
            """, node_id=node_id, depth=upstream_depth)
            
            upstream_nodes = []
            upstream_edges = []
            for record in upstream_result:
                upstream_nodes.append(LineageNode(**record["upstream"]))
                for edge_data in record["edges"]:
                    upstream_edges.append(LineageEdge(
                        source_id=edge_data.start_node["id"],
                        target_id=edge_data.end_node["id"],
                        edge_type=edge_data["edge_type"],
                        created_at=edge_data["created_at"],
                        confidence=edge_data.get("confidence", 1.0)
                    ))
            
            # Get downstream lineage
            downstream_result = session.run("""
                MATCH path = (n:LineageNode {id: $node_id})-[:LINEAGE*1..$depth]->(downstream:LineageNode)
                RETURN downstream, relationships(path) as edges
            """, node_id=node_id, depth=downstream_depth)
            
            downstream_nodes = []
            downstream_edges = []
            for record in downstream_result:
                downstream_nodes.append(LineageNode(**record["downstream"]))
                for edge_data in record["edges"]:
                    downstream_edges.append(LineageEdge(
                        source_id=edge_data.start_node["id"],
                        target_id=edge_data.end_node["id"],
                        edge_type=edge_data["edge_type"],
                        created_at=edge_data["created_at"],
                        confidence=edge_data.get("confidence", 1.0)
                    ))
            
            return LineageGraph(
                root_node=root_node,
                upstream_nodes=upstream_nodes,
                downstream_nodes=downstream_nodes,
                edges=upstream_edges + downstream_edges,
                depth_upstream=len(set(n.id for n in upstream_nodes)),
                depth_downstream=len(set(n.id for n in downstream_nodes)),
                total_nodes=1 + len(upstream_nodes) + len(downstream_nodes)
            )
    
    def analyze_impact(self, node_id: str) -> ImpactAnalysis:
        """Analyze impact of changing a node"""
        with self.driver.session() as session:
            # Get source node
            source_result = session.run("""
                MATCH (n:LineageNode {id: $node_id})
                RETURN n
            """, node_id=node_id).single()
            
            if not source_result:
                raise ValueError(f"Node {node_id} not found")
            
            source_node = LineageNode(**source_result["n"])
            
            # Get all downstream nodes
            downstream_result = session.run("""
                MATCH path = (n:LineageNode {id: $node_id})-[:LINEAGE*]->(downstream:LineageNode)
                RETURN downstream, length(path) as distance
                ORDER BY distance DESC
            """, node_id=node_id)
            
            affected_nodes = []
            affected_datasets = []
            affected_reports = []
            affected_models = []
            
            for record in downstream_result:
                node = LineageNode(**record["downstream"])
                affected_nodes.append(node)
                
                if node.node_type.value == "dataset":
                    affected_datasets.append(node.id)
                elif node.node_type.value == "report":
                    affected_reports.append(node.id)
                elif node.node_type.value == "model":
                    affected_models.append(node.id)
            
            # Determine risk level
            blast_radius = len(affected_nodes)
            if blast_radius == 0:
                risk_level = "low"
            elif blast_radius < 10:
                risk_level = "medium"
            elif blast_radius < 50:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            # Find critical paths (longest paths to most critical nodes)
            critical_paths = self._find_critical_paths(session, node_id)
            
            return ImpactAnalysis(
                source_node=source_node,
                affected_nodes=affected_nodes,
                critical_paths=critical_paths,
                blast_radius=blast_radius,
                affected_datasets=affected_datasets,
                affected_reports=affected_reports,
                affected_models=affected_models,
                risk_level=risk_level
            )
    
    def _find_critical_paths(self, session, node_id: str) -> List[List[str]]:
        """Find critical paths in the lineage"""
        result = session.run("""
            MATCH path = (n:LineageNode {id: $node_id})-[:LINEAGE*]->(end:LineageNode)
            WHERE NOT (end)-[:LINEAGE]->()
            RETURN [node in nodes(path) | node.id] as path_ids
            ORDER BY length(path) DESC
            LIMIT 5
        """, node_id=node_id)
        
        return [record["path_ids"] for record in result]
    
    def get_column_lineage(self, table_id: str, column_name: str) -> Dict[str, Any]:
        """Get column-level lineage"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (col:Column {table_id: $table_id, name: $column_name})
                OPTIONAL MATCH (col)-[:DERIVED_FROM*]->(source:Column)
                OPTIONAL MATCH (col)<-[:DERIVED_FROM*]-(target:Column)
                RETURN col, collect(DISTINCT source) as sources, collect(DISTINCT target) as targets
            """, table_id=table_id, column_name=column_name)
            
            record = result.single()
            if not record:
                return None
            
            return {
                "column": dict(record["col"]),
                "upstream_columns": [dict(c) for c in record["sources"]],
                "downstream_columns": [dict(c) for c in record["targets"]]
            }
    
    def auto_discover_lineage(self, platform: str, config: Dict[str, Any]):
        """Auto-discover lineage from platform metadata"""
        if platform == "bigquery":
            return self._discover_bigquery_lineage(config)
        elif platform == "airflow":
            return self._discover_airflow_lineage(config)
        elif platform == "dbt":
            return self._discover_dbt_lineage(config)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def _discover_bigquery_lineage(self, config: Dict[str, Any]):
        """Discover lineage from BigQuery audit logs"""
        from google.cloud import bigquery
        
        client = bigquery.Client(project=config["project_id"])
        
        # Query INFORMATION_SCHEMA for table dependencies
        query = """
        SELECT 
            referenced_table.dataset_id as source_dataset,
            referenced_table.table_id as source_table,
            destination_table.dataset_id as target_dataset,
            destination_table.table_id as target_table,
            query
        FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
        WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        AND statement_type = 'INSERT'
        AND referenced_tables IS NOT NULL
        """
        
        results = client.query(query).result()
        
        for row in results:
            # Create nodes and edges
            source_id = f"bigquery:{row.source_dataset}.{row.source_table}"
            target_id = f"bigquery:{row.target_dataset}.{row.target_table}"
            
            self.create_node(LineageNode(
                id=source_id,
                name=row.source_table,
                node_type=NodeType.TABLE,
                platform="bigquery",
                location=f"{config['project_id']}.{row.source_dataset}.{row.source_table}",
                owner="auto-discovered",
                domain="unknown",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ))
            
            self.create_node(LineageNode(
                id=target_id,
                name=row.target_table,
                node_type=NodeType.TABLE,
                platform="bigquery",
                location=f"{config['project_id']}.{row.target_dataset}.{row.target_table}",
                owner="auto-discovered",
                domain="unknown",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ))
            
            self.create_edge(LineageEdge(
                source_id=source_id,
                target_id=target_id,
                edge_type=EdgeType.DERIVED_FROM,
                transformation_sql=row.query,
                created_at=datetime.utcnow()
            ))
```

---

## 4. Data Dictionary Management

### 4.1 Dictionary Schema

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/dictionary/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    JSON = "json"
    ARRAY = "array"
    GEOGRAPHY = "geography"

class BusinessTerm(BaseModel):
    """Business glossary term"""
    id: str
    term: str
    definition: str
    category: str
    synonyms: List[str] = []
    related_terms: List[str] = []
    owner: str
    status: str = "approved"  # draft, approved, deprecated
    created_at: datetime
    updated_at: datetime
    examples: List[str] = []
    usage_guidelines: Optional[str] = None

class DataElement(BaseModel):
    """Data dictionary element (column/field)"""
    id: str
    name: str
    display_name: str
    description: str
    
    # Technical specs
    data_type: DataType
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    is_nullable: bool = True
    default_value: Optional[str] = None
    
    # Business context
    business_term_id: Optional[str] = None
    business_definition: Optional[str] = None
    business_rules: List[str] = []
    
    # Data quality
    validation_rules: List[Dict[str, Any]] = []
    allowed_values: List[str] = []
    value_ranges: Optional[Dict[str, Any]] = None
    
    # Metadata
    is_pii: bool = False
    is_sensitive: bool = False
    is_primary_key: bool = False
    is_foreign_key: bool = False
    
    # Usage
    source_system: Optional[str] = None
    used_in_reports: List[str] = []
    used_in_models: List[str] = []
    
    # Stewardship
    steward: str
    created_at: datetime
    updated_at: datetime

class DataDictionary(BaseModel):
    """Complete data dictionary for a dataset/table"""
    id: str
    name: str
    description: str
    version: str
    
    # Ownership
    owner: str
    domain: str
    
    # Elements
    elements: List[DataElement]
    
    # Relationships
    related_dictionaries: List[str] = []
    parent_dictionary: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Status
    status: str = "draft"  # draft, review, approved, deprecated

class DataDictionaryVersion(BaseModel):
    """Version history for data dictionary"""
    dictionary_id: str
    version: str
    changes: List[Dict[str, Any]]
    changed_by: str
    changed_at: datetime
    change_reason: str
```

### 4.2 Dictionary Service

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/dictionary/dictionary_service.py

from sqlalchemy import create_engine, text
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import DataDictionary, DataElement, BusinessTerm

class DataDictionaryService:
    """
    Data dictionary management service
    Maintains business and technical definitions of data elements
    """
    
    def __init__(self, db_connection: str):
        self.engine = create_engine(db_connection)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize dictionary tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS business_terms (
                    id VARCHAR(255) PRIMARY KEY,
                    term VARCHAR(255) NOT NULL UNIQUE,
                    definition TEXT NOT NULL,
                    category VARCHAR(100),
                    synonyms JSON,
                    related_terms JSON,
                    owner VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'approved',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    examples JSON,
                    usage_guidelines TEXT
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS data_elements (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255),
                    description TEXT,
                    data_type VARCHAR(50),
                    length INT,
                    precision INT,
                    scale INT,
                    is_nullable BOOLEAN DEFAULT TRUE,
                    default_value VARCHAR(255),
                    business_term_id VARCHAR(255),
                    business_definition TEXT,
                    business_rules JSON,
                    validation_rules JSON,
                    allowed_values JSON,
                    value_ranges JSON,
                    is_pii BOOLEAN DEFAULT FALSE,
                    is_sensitive BOOLEAN DEFAULT FALSE,
                    is_primary_key BOOLEAN DEFAULT FALSE,
                    is_foreign_key BOOLEAN DEFAULT FALSE,
                    source_system VARCHAR(255),
                    used_in_reports JSON,
                    used_in_models JSON,
                    steward VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS data_dictionaries (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    version VARCHAR(50),
                    owner VARCHAR(255),
                    domain VARCHAR(100),
                    elements JSON,
                    related_dictionaries JSON,
                    parent_dictionary VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_by VARCHAR(255),
                    approved_at TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'draft'
                )
            """))
            
            conn.commit()
    
    def create_business_term(self, term: BusinessTerm) -> bool:
        """Create a new business term"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO business_terms 
                (id, term, definition, category, synonyms, related_terms, owner, 
                 status, created_at, updated_at, examples, usage_guidelines)
                VALUES 
                (:id, :term, :definition, :category, :synonyms, :related_terms, :owner,
                 :status, :created_at, :updated_at, :examples, :usage_guidelines)
            """), term.dict())
            conn.commit()
            return True
    
    def get_business_term(self, term_id: str) -> Optional[BusinessTerm]:
        """Get a business term by ID"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM business_terms WHERE id = :id
            """), {"id": term_id}).fetchone()
            
            if result:
                return BusinessTerm(**dict(result))
            return None
    
    def search_business_terms(self, query: str) -> List[BusinessTerm]:
        """Search business terms"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT * FROM business_terms 
                WHERE term LIKE :query OR definition LIKE :query
                ORDER BY term
            """), {"query": f"%{query}%"}).fetchall()
            
            return [BusinessTerm(**dict(r)) for r in results]
    
    def create_data_dictionary(self, dictionary: DataDictionary) -> bool:
        """Create a new data dictionary"""
        with self.engine.connect() as conn:
            # Store dictionary
            conn.execute(text("""
                INSERT INTO data_dictionaries
                (id, name, description, version, owner, domain, elements,
                 related_dictionaries, parent_dictionary, created_at, updated_at,
                 approved_by, approved_at, status)
                VALUES
                (:id, :name, :description, :version, :owner, :domain, :elements,
                 :related_dictionaries, :parent_dictionary, :created_at, :updated_at,
                 :approved_by, :approved_at, :status)
            """), {
                **dictionary.dict(exclude={'elements'}),
                "elements": [e.dict() for e in dictionary.elements]
            })
            
            # Store individual elements
            for element in dictionary.elements:
                conn.execute(text("""
                    INSERT INTO data_elements
                    (id, name, display_name, description, data_type, length, precision,
                     scale, is_nullable, default_value, business_term_id, business_definition,
                     business_rules, validation_rules, allowed_values, value_ranges,
                     is_pii, is_sensitive, is_primary_key, is_foreign_key,
                     source_system, used_in_reports, used_in_models, steward,
                     created_at, updated_at)
                    VALUES
                    (:id, :name, :display_name, :description, :data_type, :length, :precision,
                     :scale, :is_nullable, :default_value, :business_term_id, :business_definition,
                     :business_rules, :validation_rules, :allowed_values, :value_ranges,
                     :is_pii, :is_sensitive, :is_primary_key, :is_foreign_key,
                     :source_system, :used_in_reports, :used_in_models, :steward,
                     :created_at, :updated_at)
                    ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    display_name = EXCLUDED.display_name,
                    description = EXCLUDED.description,
                    updated_at = EXCLUDED.updated_at
                """), element.dict())
            
            conn.commit()
            return True
    
    def get_data_dictionary(self, dictionary_id: str) -> Optional[DataDictionary]:
        """Get a data dictionary by ID"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM data_dictionaries WHERE id = :id
            """), {"id": dictionary_id}).fetchone()
            
            if result:
                data = dict(result)
                data["elements"] = [DataElement(**e) for e in data["elements"]]
                return DataDictionary(**data)
            return None
    
    def auto_generate_dictionary(self, 
                                  table_name: str,
                                  database_connection: str,
                                  schema: str = "public") -> DataDictionary:
        """Auto-generate dictionary from database schema"""
        from sqlalchemy import inspect
        
        engine = create_engine(database_connection)
        inspector = inspect(engine)
        
        elements = []
        for column in inspector.get_columns(table_name, schema=schema):
            element = DataElement(
                id=f"{table_name}.{column['name']}",
                name=column['name'],
                display_name=column['name'].replace('_', ' ').title(),
                description=f"Auto-generated description for {column['name']}",
                data_type=self._map_sql_type(column['type']),
                is_nullable=column.get('nullable', True),
                default_value=str(column.get('default')) if column.get('default') else None,
                steward="auto-generated",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            elements.append(element)
        
        dictionary = DataDictionary(
            id=f"dict-{table_name}",
            name=table_name,
            description=f"Data dictionary for {table_name}",
            version="1.0",
            owner="auto-generated",
            domain="unknown",
            elements=elements,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status="draft"
        )
        
        return dictionary
    
    def _map_sql_type(self, sql_type) -> str:
        """Map SQL type to DataType enum"""
        type_str = str(sql_type).lower()
        
        if 'varchar' in type_str or 'char' in type_str or 'text' in type_str:
            return "string"
        elif 'int' in type_str:
            return "integer"
        elif 'float' in type_str or 'double' in type_str or 'numeric' in type_str or 'decimal' in type_str:
            return "float"
        elif 'bool' in type_str:
            return "boolean"
        elif 'timestamp' in type_str:
            return "timestamp"
        elif 'date' in type_str:
            return "date"
        elif 'json' in type_str:
            return "json"
        else:
            return "string"
    
    def export_to_markdown(self, dictionary_id: str) -> str:
        """Export dictionary to markdown format"""
        dictionary = self.get_data_dictionary(dictionary_id)
        if not dictionary:
            return ""
        
        md = f"# {dictionary.name}\n\n"
        md += f"**Version:** {dictionary.version}  \n"
        md += f"**Owner:** {dictionary.owner}  \n"
        md += f"**Domain:** {dictionary.domain}  \n"
        md += f"**Status:** {dictionary.status}  \n\n"
        md += f"## Description\n\n{dictionary.description}\n\n"
        md += "## Data Elements\n\n"
        md += "| Name | Type | Nullable | Description | PII |\n"
        md += "|------|------|----------|-------------|-----|\n"
        
        for element in dictionary.elements:
            pii_flag = "Yes" if element.is_pii else "No"
            nullable = "Yes" if element.is_nullable else "No"
            md += f"| {element.name} | {element.data_type} | {nullable} | {element.description} | {pii_flag} |\n"
        
        return md
```

---

## 5. Metadata Management

### 5.1 Metadata Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    METADATA MANAGEMENT PLATFORM                      │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Technical   │  │  Business    │  │  Operational │               │
│  │  Metadata    │  │  Metadata    │  │  Metadata    │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Metadata    │  │  Schema      │  │  Profiling   │               │
│  │  Repository  │  │  Registry    │  │  Engine      │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Metadata Models

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/metadata/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class MetadataType(str, Enum):
    TECHNICAL = "technical"
    BUSINESS = "business"
    OPERATIONAL = "operational"
    GOVERNANCE = "governance"

class TechnicalMetadata(BaseModel):
    """Technical metadata for data assets"""
    # Schema information
    schema_name: str
    table_name: str
    column_count: int
    partition_columns: List[str] = []
    clustering_columns: List[str] = []
    
    # Storage
    format: str  # parquet, csv, json, etc.
    compression: Optional[str] = None
    location: str
    size_bytes: int
    row_count: int
    
    # Performance
    last_modified: datetime
    created_at: datetime
    
    # Constraints
    primary_keys: List[str] = []
    foreign_keys: List[Dict[str, str]] = []
    indexes: List[str] = []
    
    # Data types
    column_types: Dict[str, str]

class BusinessMetadata(BaseModel):
    """Business metadata for data assets"""
    # Ownership
    data_owner: str
    data_steward: str
    business_domain: str
    
    # Description
    business_description: str
    business_purpose: str
    key_business_questions: List[str] = []
    
    # Usage
    report_owners: List[str] = []
    downstream_systems: List[str] = []
    sla_requirements: Optional[str] = None
    
    # Classification
    data_classification: str
    regulatory_scope: List[str] = []
    
    # Metrics
    criticality: str  # low, medium, high, critical
    usage_frequency: str  # daily, weekly, monthly, ad-hoc

class OperationalMetadata(BaseModel):
    """Operational metadata for data assets"""
    # Pipeline info
    ingestion_job: str
    transformation_jobs: List[str] = []
    
    # Scheduling
    refresh_frequency: str
    last_refresh: datetime
    next_scheduled_refresh: datetime
    
    # Quality
    last_quality_check: datetime
    quality_score: float
    quality_issues: List[Dict[str, Any]] = []
    
    # Performance
    avg_query_time_ms: Optional[int] = None
    query_count_24h: int = 0
    
    # Dependencies
    upstream_dependencies: List[str] = []
    downstream_consumers: List[str] = []

class GovernanceMetadata(BaseModel):
    """Governance metadata for data assets"""
    # Compliance
    pii_fields: List[str] = []
    sensitive_fields: List[str] = []
    compliance_frameworks: List[str] = []
    
    # Policies
    retention_policy: str
    access_policy: str
    sharing_policy: str
    
    # Audit
    created_by: str
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    
    # Reviews
    last_review_date: datetime
    next_review_date: datetime
    review_status: str  # current, pending_review, expired

class UnifiedMetadata(BaseModel):
    """Unified metadata combining all types"""
    asset_id: str
    asset_name: str
    asset_type: str
    
    technical: Optional[TechnicalMetadata] = None
    business: Optional[BusinessMetadata] = None
    operational: Optional[OperationalMetadata] = None
    governance: Optional[GovernanceMetadata] = None
    
    # Custom tags
    tags: List[str] = []
    custom_properties: Dict[str, Any] = {}
    
    # Versioning
    version: str = "1.0"
    created_at: datetime
    updated_at: datetime
```

### 5.3 Metadata Service

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/metadata/metadata_service.py

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
import boto3
from .models import UnifiedMetadata, TechnicalMetadata, BusinessMetadata, OperationalMetadata, GovernanceMetadata

class MetadataService:
    """
    Central metadata management service
    Collects, stores, and serves metadata from various sources
    """
    
    def __init__(self, db_connection: str, aws_region: str = "us-east-1"):
        self.engine = create_engine(db_connection)
        self.glue_client = boto3.client('glue', region_name=aws_region)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize metadata tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS unified_metadata (
                    asset_id VARCHAR(255) PRIMARY KEY,
                    asset_name VARCHAR(255) NOT NULL,
                    asset_type VARCHAR(100),
                    technical JSON,
                    business JSON,
                    operational JSON,
                    governance JSON,
                    tags JSON,
                    custom_properties JSON,
                    version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
    
    def extract_from_aws_glue(self, database_name: str, table_name: str) -> TechnicalMetadata:
        """Extract technical metadata from AWS Glue"""
        response = self.glue_client.get_table(
            DatabaseName=database_name,
            Name=table_name
        )
        
        table = response['Table']
        storage = table.get('StorageDescriptor', {})
        
        # Extract column information
        column_types = {}
        for col in storage.get('Columns', []):
            column_types[col['Name']] = col['Type']
        
        # Extract partition columns
        partition_columns = [p['Name'] for p in table.get('PartitionKeys', [])]
        
        # Extract parameters
        params = table.get('Parameters', {})
        
        return TechnicalMetadata(
            schema_name=database_name,
            table_name=table_name,
            column_count=len(storage.get('Columns', [])),
            partition_columns=partition_columns,
            clustering_columns=params.get('clustering_columns', '').split(',') if params.get('clustering_columns') else [],
            format=storage.get('InputFormat', '').split('.')[-1] if storage.get('InputFormat') else 'unknown',
            compression=params.get('compression', 'none'),
            location=storage.get('Location', ''),
            size_bytes=int(params.get('sizeKey', 0)),
            row_count=int(params.get('recordCount', 0)),
            last_modified=table.get('UpdateTime', datetime.utcnow()),
            created_at=table.get('CreateTime', datetime.utcnow()),
            column_types=column_types
        )
    
    def extract_from_bigquery(self, project: str, dataset: str, table: str) -> TechnicalMetadata:
        """Extract technical metadata from BigQuery"""
        from google.cloud import bigquery
        
        client = bigquery.Client(project=project)
        table_ref = f"{project}.{dataset}.{table}"
        bq_table = client.get_table(table_ref)
        
        # Extract column types
        column_types = {}
        for field in bq_table.schema:
            column_types[field.name] = field.field_type
        
        return TechnicalMetadata(
            schema_name=dataset,
            table_name=table,
            column_count=len(bq_table.schema),
            partition_columns=[f.name for f in bq_table.schema if f.name in (bq_table.time_partitioning.field if bq_table.time_partitioning else [])],
            clustering_columns=bq_table.clustering_fields if bq_table.clustering_fields else [],
            format="bigquery",
            location=table_ref,
            size_bytes=bq_table.num_bytes,
            row_count=bq_table.num_rows,
            last_modified=bq_table.modified,
            created_at=bq_table.created,
            column_types=column_types
        )
    
    def store_metadata(self, metadata: UnifiedMetadata):
        """Store unified metadata"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO unified_metadata
                (asset_id, asset_name, asset_type, technical, business, operational, governance,
                 tags, custom_properties, version, created_at, updated_at)
                VALUES
                (:asset_id, :asset_name, :asset_type, :technical, :business, :operational, :governance,
                 :tags, :custom_properties, :version, :created_at, :updated_at)
                ON CONFLICT (asset_id) DO UPDATE SET
                asset_name = EXCLUDED.asset_name,
                technical = EXCLUDED.technical,
                business = EXCLUDED.business,
                operational = EXCLUDED.operational,
                governance = EXCLUDED.governance,
                tags = EXCLUDED.tags,
                custom_properties = EXCLUDED.custom_properties,
                version = EXCLUDED.version,
                updated_at = EXCLUDED.updated_at
            """), {
                "asset_id": metadata.asset_id,
                "asset_name": metadata.asset_name,
                "asset_type": metadata.asset_type,
                "technical": json.dumps(metadata.technical.dict()) if metadata.technical else None,
                "business": json.dumps(metadata.business.dict()) if metadata.business else None,
                "operational": json.dumps(metadata.operational.dict()) if metadata.operational else None,
                "governance": json.dumps(metadata.governance.dict()) if metadata.governance else None,
                "tags": json.dumps(metadata.tags),
                "custom_properties": json.dumps(metadata.custom_properties),
                "version": metadata.version,
                "created_at": metadata.created_at,
                "updated_at": metadata.updated_at
            })
            conn.commit()
    
    def get_metadata(self, asset_id: str) -> Optional[UnifiedMetadata]:
        """Retrieve unified metadata"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM unified_metadata WHERE asset_id = :asset_id
            """), {"asset_id": asset_id}).fetchone()
            
            if result:
                data = dict(result)
                return UnifiedMetadata(
                    asset_id=data["asset_id"],
                    asset_name=data["asset_name"],
                    asset_type=data["asset_type"],
                    technical=TechnicalMetadata(**json.loads(data["technical"])) if data["technical"] else None,
                    business=BusinessMetadata(**json.loads(data["business"])) if data["business"] else None,
                    operational=OperationalMetadata(**json.loads(data["operational"])) if data["operational"] else None,
                    governance=GovernanceMetadata(**json.loads(data["governance"])) if data["governance"] else None,
                    tags=json.loads(data["tags"]) if data["tags"] else [],
                    custom_properties=json.loads(data["custom_properties"]) if data["custom_properties"] else {},
                    version=data["version"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"]
                )
            return None
    
    def search_metadata(self, query: str, metadata_type: Optional[str] = None) -> List[UnifiedMetadata]:
        """Search metadata"""
        with self.engine.connect() as conn:
            sql = """
                SELECT * FROM unified_metadata 
                WHERE asset_name ILIKE :query OR asset_id ILIKE :query
            """
            if metadata_type:
                sql += f" AND {metadata_type} IS NOT NULL"
            
            results = conn.execute(text(sql), {"query": f"%{query}%"}).fetchall()
            
            metadata_list = []
            for result in results:
                data = dict(result)
                metadata_list.append(UnifiedMetadata(
                    asset_id=data["asset_id"],
                    asset_name=data["asset_name"],
                    asset_type=data["asset_type"],
                    tags=json.loads(data["tags"]) if data["tags"] else [],
                    version=data["version"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"]
                ))
            
            return metadata_list
    
    def sync_from_source(self, source_type: str, config: Dict[str, Any]):
        """Sync metadata from external source"""
        if source_type == "glue":
            return self._sync_from_glue(config)
        elif source_type == "bigquery":
            return self._sync_from_bigquery(config)
        elif source_type == "postgres":
            return self._sync_from_postgres(config)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    def _sync_from_glue(self, config: Dict[str, Any]):
        """Sync metadata from AWS Glue"""
        databases = self.glue_client.get_databases()
        
        for db in databases['DatabaseList']:
            db_name = db['Name']
            tables = self.glue_client.get_tables(DatabaseName=db_name)
            
            for table in tables['TableList']:
                table_name = table['Name']
                technical = self.extract_from_aws_glue(db_name, table_name)
                
                metadata = UnifiedMetadata(
                    asset_id=f"glue:{db_name}.{table_name}",
                    asset_name=table_name,
                    asset_type="table",
                    technical=technical,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self.store_metadata(metadata)
    
    def _sync_from_postgres(self, config: Dict[str, Any]):
        """Sync metadata from PostgreSQL"""
        from sqlalchemy import inspect
        
        engine = create_engine(config["connection_string"])
        inspector = inspect(engine)
        
        for schema in inspector.get_schema_names():
            for table_name in inspector.get_table_names(schema=schema):
                columns = inspector.get_columns(table_name, schema=schema)
                
                column_types = {c['name']: str(c['type']) for c in columns}
                
                technical = TechnicalMetadata(
                    schema_name=schema,
                    table_name=table_name,
                    column_count=len(columns),
                    partition_columns=[c['name'] for c in columns if c.get('autoincrement')],
                    format="postgresql",
                    location=f"{config['host']}/{schema}/{table_name}",
                    size_bytes=0,  # Would need to query pg_class
                    row_count=0,  # Would need to run COUNT
                    last_modified=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    column_types=column_types
                )
                
                metadata = UnifiedMetadata(
                    asset_id=f"postgres:{schema}.{table_name}",
                    asset_name=table_name,
                    asset_type="table",
                    technical=technical,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self.store_metadata(metadata)
```



---

## 6. Data Quality Rules

### 6.1 Quality Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA QUALITY FRAMEWORK                            │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   Quality    │    │   Rule       │    │   Quality    │          │
│   │   Rules      │    │   Engine     │    │   Dashboard  │          │
│   │   Engine     │    │   (Great     │    │   (Grafana)  │          │
│   │   (DBT)      │    │   Expectations│    │              │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   Data       │    │   Anomaly    │    │   Quality    │          │
│   │   Profiling  │    │   Detection  │    │   Alerts     │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Quality Rule Models

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/quality/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class RuleType(str, Enum):
    COMPLETENESS = "completeness"
    VALIDITY = "validity"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    UNIQUENESS = "uniqueness"
    ACCURACY = "accuracy"
    CUSTOM = "custom"

class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class QualityRule(BaseModel):
    """Data quality rule definition"""
    id: str
    name: str
    description: str
    rule_type: RuleType
    severity: Severity
    
    # Target
    target_dataset: str
    target_column: Optional[str] = None
    
    # Rule configuration
    rule_config: Dict[str, Any]
    
    # Thresholds
    warning_threshold: float = Field(0.9, ge=0, le=1)
    error_threshold: float = Field(0.8, ge=0, le=1)
    critical_threshold: float = Field(0.5, ge=0, le=1)
    
    # Scheduling
    schedule: str = "0 */6 * * *"  # Cron expression
    
    # Metadata
    owner: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    # Actions
    on_failure: List[str] = []  # alert, quarantine, notify

class QualityCheckResult(BaseModel):
    """Result of a quality check"""
    rule_id: str
    execution_id: str
    executed_at: datetime
    
    # Results
    passed: bool
    score: float = Field(..., ge=0, le=1)
    records_checked: int
    records_failed: int
    
    # Details
    failures: List[Dict[str, Any]] = []
    failure_sample: List[Dict[str, Any]] = []
    
    # Classification
    severity: Severity
    status: str  # passed, warning, failed
    
    # Performance
    execution_time_ms: int

class QualityDimensionScore(BaseModel):
    """Quality score for a dimension"""
    dimension: RuleType
    score: float
    weight: float
    rule_count: int
    passed_rules: int
    failed_rules: int

class DatasetQualityScore(BaseModel):
    """Overall quality score for a dataset"""
    dataset_id: str
    overall_score: float
    
    # Dimension scores
    dimension_scores: List[QualityDimensionScore]
    
    # Summary
    total_rules: int
    passed_rules: int
    warning_rules: int
    failed_rules: int
    critical_rules: int
    
    # History
    last_checked: datetime
    trend: str  # improving, stable, declining

class QualityIncident(BaseModel):
    """Quality incident for tracking"""
    id: str
    rule_id: str
    dataset_id: str
    
    # Incident details
    severity: Severity
    description: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    
    # Impact
    affected_records: int
    affected_downstream: List[str] = []
    
    # Resolution
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    status: str = "open"  # open, investigating, resolved, closed
```

### 6.3 Quality Rule Engine

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/quality/rule_engine.py

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import great_expectations as gx
from great_expectations.core import ExpectationSuite
from .models import QualityRule, QualityCheckResult, Severity

class QualityRuleEngine:
    """
    Data quality rule engine using Great Expectations
    Validates data against defined quality rules
    """
    
    def __init__(self, context_root_dir: str = "/gx"):
        self.context = gx.get_context(context_root_dir=context_root_dir)
    
    def create_expectation_suite(self, dataset_name: str, rules: List[QualityRule]) -> ExpectationSuite:
        """Create Great Expectations suite from quality rules"""
        suite_name = f"{dataset_name}_quality_suite"
        
        try:
            suite = self.context.suites.add(ExpectationSuite(name=suite_name))
        except Exception:
            suite = self.context.suites.get(name=suite_name)
        
        for rule in rules:
            expectation = self._convert_rule_to_expectation(rule)
            if expectation:
                suite.add_expectation(expectation)
        
        return suite
    
    def _convert_rule_to_expectation(self, rule: QualityRule):
        """Convert quality rule to Great Expectations expectation"""
        config = rule.rule_config
        
        if rule.rule_type.value == "completeness":
            return gx.expectations.ExpectColumnValuesToNotBeNull(
                column=rule.target_column or config.get("column"),
                mostly=config.get("mostly", 0.95)
            )
        
        elif rule.rule_type.value == "validity":
            if "regex" in config:
                return gx.expectations.ExpectColumnValuesToMatchRegex(
                    column=rule.target_column or config.get("column"),
                    regex=config["regex"],
                    mostly=config.get("mostly", 0.95)
                )
            elif "set" in config:
                return gx.expectations.ExpectColumnValuesToBeInSet(
                    column=rule.target_column or config.get("column"),
                    value_set=config["set"],
                    mostly=config.get("mostly", 0.95)
                )
            elif "range" in config:
                return gx.expectations.ExpectColumnValuesToBeBetween(
                    column=rule.target_column or config.get("column"),
                    min_value=config["range"][0],
                    max_value=config["range"][1]
                )
        
        elif rule.rule_type.value == "uniqueness":
            return gx.expectations.ExpectColumnValuesToBeUnique(
                column=rule.target_column or config.get("column")
            )
        
        elif rule.rule_type.value == "consistency":
            if "regex" in config:
                return gx.expectations.ExpectColumnValuesToMatchRegex(
                    column=rule.target_column or config.get("column"),
                    regex=config["regex"]
                )
        
        elif rule.rule_type.value == "timeliness":
            # Custom expectation for freshness
            return gx.expectations.ExpectColumnMaxToBeBetween(
                column=rule.target_column or config.get("column"),
                min_value=config.get("min_date"),
                max_value=config.get("max_date")
            )
        
        return None
    
    def validate_dataset(self, 
                         dataset: pd.DataFrame,
                         rules: List[QualityRule],
                         dataset_name: str) -> List[QualityCheckResult]:
        """Validate a dataset against quality rules"""
        results = []
        
        for rule in rules:
            if not rule.is_active:
                continue
            
            start_time = datetime.utcnow()
            
            try:
                result = self._execute_rule(dataset, rule)
            except Exception as e:
                result = QualityCheckResult(
                    rule_id=rule.id,
                    execution_id=f"{rule.id}_{start_time.isoformat()}",
                    executed_at=start_time,
                    passed=False,
                    score=0.0,
                    records_checked=len(dataset),
                    records_failed=len(dataset),
                    severity=Severity.CRITICAL,
                    status="failed",
                    execution_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                    failures=[{"error": str(e)}]
                )
            
            results.append(result)
        
        return results
    
    def _execute_rule(self, dataset: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
        """Execute a single quality rule"""
        start_time = datetime.utcnow()
        config = rule.rule_config
        column = rule.target_column or config.get("column")
        
        records_checked = len(dataset)
        records_failed = 0
        failures = []
        
        if rule.rule_type.value == "completeness":
            null_count = dataset[column].isnull().sum()
            records_failed = null_count
            passed = null_count <= (1 - rule.warning_threshold) * records_checked
            score = 1 - (null_count / records_checked) if records_checked > 0 else 0
        
        elif rule.rule_type.value == "validity":
            if "regex" in config:
                pattern = re.compile(config["regex"])
                invalid_mask = ~dataset[column].astype(str).str.match(pattern)
                records_failed = invalid_mask.sum()
                score = 1 - (records_failed / records_checked) if records_checked > 0 else 0
                passed = score >= rule.warning_threshold
            elif "set" in config:
                invalid_mask = ~dataset[column].isin(config["set"])
                records_failed = invalid_mask.sum()
                score = 1 - (records_failed / records_checked) if records_checked > 0 else 0
                passed = score >= rule.warning_threshold
            elif "range" in config:
                min_val, max_val = config["range"]
                invalid_mask = ~dataset[column].between(min_val, max_val)
                records_failed = invalid_mask.sum()
                score = 1 - (records_failed / records_checked) if records_checked > 0 else 0
                passed = score >= rule.warning_threshold
            else:
                score = 1.0
                passed = True
        
        elif rule.rule_type.value == "uniqueness":
            duplicate_count = dataset[column].duplicated().sum()
            records_failed = duplicate_count
            score = 1 - (duplicate_count / records_checked) if records_checked > 0 else 0
            passed = score >= rule.warning_threshold
        
        elif rule.rule_type.value == "timeliness":
            if column in dataset.columns:
                max_date = pd.to_datetime(dataset[column]).max()
                threshold_date = datetime.utcnow() - timedelta(hours=config.get("max_age_hours", 24))
                passed = max_date >= threshold_date
                score = 1.0 if passed else 0.0
                records_failed = 0 if passed else records_checked
        
        else:
            score = 1.0
            passed = True
        
        # Determine status and severity
        if passed:
            status = "passed"
            severity = Severity.INFO
        elif score >= rule.warning_threshold:
            status = "warning"
            severity = Severity.WARNING
        elif score >= rule.error_threshold:
            status = "failed"
            severity = Severity.ERROR
        else:
            status = "critical"
            severity = Severity.CRITICAL
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return QualityCheckResult(
            rule_id=rule.id,
            execution_id=f"{rule.id}_{start_time.isoformat()}",
            executed_at=start_time,
            passed=passed,
            score=score,
            records_checked=records_checked,
            records_failed=int(records_failed),
            severity=severity,
            status=status,
            execution_time_ms=execution_time,
            failures=failures[:10]  # Limit failure details
        )
    
    def calculate_overall_score(self, results: List[QualityCheckResult]) -> Dict[str, Any]:
        """Calculate overall quality score from individual results"""
        if not results:
            return {"overall_score": 0, "status": "unknown"}
        
        total_rules = len(results)
        passed_rules = sum(1 for r in results if r.passed)
        warning_rules = sum(1 for r in results if r.status == "warning")
        failed_rules = sum(1 for r in results if r.status == "failed")
        critical_rules = sum(1 for r in results if r.status == "critical")
        
        # Weighted score
        weights = {
            "passed": 1.0,
            "warning": 0.7,
            "failed": 0.3,
            "critical": 0.0
        }
        
        total_weight = sum(weights[r.status] for r in results)
        overall_score = total_weight / total_rules if total_rules > 0 else 0
        
        # Determine status
        if critical_rules > 0:
            status = "critical"
        elif failed_rules > 0:
            status = "failed"
        elif warning_rules > 0:
            status = "warning"
        else:
            status = "passed"
        
        return {
            "overall_score": round(overall_score, 2),
            "status": status,
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "warning_rules": warning_rules,
            "failed_rules": failed_rules,
            "critical_rules": critical_rules
        }

# Pre-defined quality rules for ResilienceAI
RESILIENCE_AI_QUALITY_RULES = {
    "geospatial": [
        QualityRule(
            id="geo-coords-valid",
            name="Valid Coordinates",
            description="Latitude and longitude must be within valid ranges",
            rule_type=RuleType.VALIDITY,
            severity=Severity.CRITICAL,
            target_dataset="geospatial.locations",
            target_column="latitude",
            rule_config={"range": [-90, 90]},
            warning_threshold=0.99,
            error_threshold=0.95,
            owner="geo-team@resilience.ai",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        QualityRule(
            id="geo-coords-complete",
            name="Complete Coordinates",
            description="All location records must have coordinates",
            rule_type=RuleType.COMPLETENESS,
            severity=Severity.ERROR,
            target_dataset="geospatial.locations",
            target_column="latitude",
            rule_config={},
            warning_threshold=0.98,
            error_threshold=0.95,
            owner="geo-team@resilience.ai",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
    ],
    "sensor_data": [
        QualityRule(
            id="sensor-timestamp-fresh",
            name="Fresh Sensor Data",
            description="Sensor data should be no older than 1 hour",
            rule_type=RuleType.TIMELINESS,
            severity=Severity.WARNING,
            target_dataset="sensor.readings",
            target_column="timestamp",
            rule_config={"max_age_hours": 1},
            warning_threshold=0.95,
            error_threshold=0.90,
            owner="iot-team@resilience.ai",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        QualityRule(
            id="sensor-values-in-range",
            name="Valid Sensor Values",
            description="Sensor values must be within expected ranges",
            rule_type=RuleType.VALIDITY,
            severity=Severity.ERROR,
            target_dataset="sensor.readings",
            target_column="value",
            rule_config={"range": [-100, 1000]},
            warning_threshold=0.99,
            error_threshold=0.95,
            owner="iot-team@resilience.ai",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
    ],
    "incident_reports": [
        QualityRule(
            id="incident-id-unique",
            name="Unique Incident IDs",
            description="Each incident must have a unique identifier",
            rule_type=RuleType.UNIQUENESS,
            severity=Severity.CRITICAL,
            target_dataset="incidents.reports",
            target_column="incident_id",
            rule_config={},
            warning_threshold=1.0,
            error_threshold=1.0,
            owner="ops-team@resilience.ai",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        QualityRule(
            id="incident-status-valid",
            name="Valid Incident Status",
            description="Incident status must be from allowed values",
            rule_type=RuleType.VALIDITY,
            severity=Severity.ERROR,
            target_dataset="incidents.reports",
            target_column="status",
            rule_config={"set": ["open", "in_progress", "resolved", "closed"]},
            warning_threshold=0.99,
            error_threshold=0.95,
            owner="ops-team@resilience.ai",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
    ]
}
```

### 6.4 Quality Monitoring Dashboard

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/quality/monitoring.py

from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from sqlalchemy import create_engine, text

class QualityMonitor:
    """
    Quality monitoring and alerting service
    Tracks quality metrics over time and generates alerts
    """
    
    def __init__(self, db_connection: str):
        self.engine = create_engine(db_connection)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize monitoring tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS quality_results (
                    id SERIAL PRIMARY KEY,
                    rule_id VARCHAR(255),
                    execution_id VARCHAR(255),
                    dataset_id VARCHAR(255),
                    executed_at TIMESTAMP,
                    passed BOOLEAN,
                    score FLOAT,
                    records_checked INT,
                    records_failed INT,
                    severity VARCHAR(50),
                    status VARCHAR(50),
                    execution_time_ms INT,
                    failures JSON
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS quality_incidents (
                    id VARCHAR(255) PRIMARY KEY,
                    rule_id VARCHAR(255),
                    dataset_id VARCHAR(255),
                    severity VARCHAR(50),
                    description TEXT,
                    detected_at TIMESTAMP,
                    resolved_at TIMESTAMP,
                    affected_records INT,
                    affected_downstream JSON,
                    assigned_to VARCHAR(255),
                    resolution_notes TEXT,
                    status VARCHAR(50)
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS quality_alerts (
                    id SERIAL PRIMARY KEY,
                    incident_id VARCHAR(255),
                    alert_type VARCHAR(100),
                    recipients JSON,
                    sent_at TIMESTAMP,
                    acknowledged_at TIMESTAMP,
                    acknowledged_by VARCHAR(255)
                )
            """))
            
            conn.commit()
    
    def store_result(self, result: Dict[str, Any]):
        """Store quality check result"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO quality_results
                (rule_id, execution_id, dataset_id, executed_at, passed, score,
                 records_checked, records_failed, severity, status, execution_time_ms, failures)
                VALUES
                (:rule_id, :execution_id, :dataset_id, :executed_at, :passed, :score,
                 :records_checked, :records_failed, :severity, :status, :execution_time_ms, :failures)
            """), result)
            conn.commit()
    
    def get_quality_trend(self, dataset_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get quality score trend over time"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT 
                    DATE(executed_at) as date,
                    AVG(score) as avg_score,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN passed THEN 1 ELSE 0 END) as passed_checks
                FROM quality_results
                WHERE dataset_id = :dataset_id
                AND executed_at >= NOW() - INTERVAL ':days days'
                GROUP BY DATE(executed_at)
                ORDER BY date
            """), {"dataset_id": dataset_id, "days": days}).fetchall()
            
            return [dict(r) for r in results]
    
    def get_dataset_quality_summary(self) -> List[Dict[str, Any]]:
        """Get quality summary for all datasets"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT 
                    dataset_id,
                    AVG(score) as avg_score,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN passed THEN 1 ELSE 0 END) as passed,
                    SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) as warnings,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failures,
                    SUM(CASE WHEN status = 'critical' THEN 1 ELSE 0 END) as critical
                FROM quality_results
                WHERE executed_at >= NOW() - INTERVAL '24 hours'
                GROUP BY dataset_id
                ORDER BY avg_score ASC
            """)).fetchall()
            
            return [dict(r) for r in results]
    
    def create_incident(self, incident: Dict[str, Any]):
        """Create a quality incident"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO quality_incidents
                (id, rule_id, dataset_id, severity, description, detected_at,
                 affected_records, affected_downstream, status)
                VALUES
                (:id, :rule_id, :dataset_id, :severity, :description, :detected_at,
                 :affected_records, :affected_downstream, :status)
            """), incident)
            conn.commit()
    
    def get_open_incidents(self) -> List[Dict[str, Any]]:
        """Get all open quality incidents"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT * FROM quality_incidents
                WHERE status IN ('open', 'investigating')
                ORDER BY detected_at DESC
            """)).fetchall()
            
            return [dict(r) for r in results]
    
    def send_alert(self, incident_id: str, alert_type: str, recipients: List[str]):
        """Send quality alert"""
        # In production, integrate with email/Slack/PagerDuty
        print(f"ALERT [{alert_type}]: Incident {incident_id} - Recipients: {recipients}")
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO quality_alerts
                (incident_id, alert_type, recipients, sent_at)
                VALUES
                (:incident_id, :alert_type, :recipients, NOW())
            """), {
                "incident_id": incident_id,
                "alert_type": alert_type,
                "recipients": json.dumps(recipients)
            })
            conn.commit()
```

---

## 7. Access Control Policies

### 7.1 Access Control Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ACCESS CONTROL FRAMEWORK                          │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   Identity   │    │   Policy     │    │   Attribute  │          │
│   │   Provider   │    │   Engine     │    │   Based      │          │
│   │   (Keycloak) │    │   (OPA)      │    │   Access     │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   Role       │    │   Data       │    │   Audit      │          │
│   │   Management │    │   Masking    │    │   Logging    │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Access Control Models

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/access/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class AccessLevel(str, Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class User(BaseModel):
    """User model for access control"""
    id: str
    email: str
    name: str
    department: str
    job_title: str
    
    # Security
    clearance_level: str
    data_access_training_completed: bool
    last_security_training: datetime
    
    # Status
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class Role(BaseModel):
    """Role definition"""
    id: str
    name: str
    description: str
    
    # Permissions
    permissions: List[str]  # List of permission strings
    
    # Scope
    allowed_domains: List[str] = []
    allowed_classifications: List[DataClassification] = []
    
    # Constraints
    requires_approval: bool = False
    max_access_duration_hours: Optional[int] = None
    requires_mfa: bool = False

class AccessPolicy(BaseModel):
    """Access policy definition"""
    id: str
    name: str
    description: str
    
    # Subject
    users: List[str] = []  # User IDs
    roles: List[str] = []  # Role IDs
    groups: List[str] = []  # Group IDs
    
    # Resource
    resources: List[str]  # Dataset/asset IDs or patterns
    resource_tags: List[str] = []
    
    # Action
    actions: List[str]  # read, write, delete, admin
    
    # Conditions
    conditions: Dict[str, Any] = {}  # Time, location, device, etc.
    
    # Effect
    effect: str = "allow"  # allow, deny
    
    # Metadata
    priority: int = 100
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True

class AccessRequest(BaseModel):
    """Access request model"""
    id: str
    user_id: str
    resource_id: str
    requested_access: AccessLevel
    
    # Request details
    justification: str
    business_need: str
    duration_days: int
    
    # Status
    status: str = "pending"  # pending, approved, denied, expired
    requested_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    
    # Granted access
    granted_access: Optional[AccessLevel] = None
    granted_from: Optional[datetime] = None
    granted_until: Optional[datetime] = None

class AccessLog(BaseModel):
    """Access audit log entry"""
    id: str
    timestamp: datetime
    user_id: str
    resource_id: str
    action: str
    
    # Context
    ip_address: str
    user_agent: str
    session_id: str
    
    # Result
    access_granted: bool
    denial_reason: Optional[str] = None
    
    # Data access details
    rows_accessed: Optional[int] = None
    columns_accessed: List[str] = []
    query_text: Optional[str] = None
    
    # Additional context
    request_context: Dict[str, Any] = {}
```

### 7.3 Access Control Service

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/access/access_service.py

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import jwt
from sqlalchemy import create_engine, text
from .models import User, Role, AccessPolicy, AccessRequest, AccessLog, AccessLevel

class AccessControlService:
    """
    Access control service implementing RBAC and ABAC
    Manages permissions, policies, and access decisions
    """
    
    def __init__(self, db_connection: str, jwt_secret: str):
        self.engine = create_engine(db_connection)
        self.jwt_secret = jwt_secret
        self._init_tables()
    
    def _init_tables(self):
        """Initialize access control tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(255) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    department VARCHAR(100),
                    job_title VARCHAR(100),
                    clearance_level VARCHAR(50),
                    data_access_training_completed BOOLEAN DEFAULT FALSE,
                    last_security_training TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS roles (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    description TEXT,
                    permissions JSON,
                    allowed_domains JSON,
                    allowed_classifications JSON,
                    requires_approval BOOLEAN DEFAULT FALSE,
                    max_access_duration_hours INT,
                    requires_mfa BOOLEAN DEFAULT FALSE
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS access_policies (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255),
                    description TEXT,
                    users JSON,
                    roles JSON,
                    groups JSON,
                    resources JSON,
                    resource_tags JSON,
                    actions JSON,
                    conditions JSON,
                    effect VARCHAR(50),
                    priority INT DEFAULT 100,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS access_requests (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255),
                    resource_id VARCHAR(255),
                    requested_access VARCHAR(50),
                    justification TEXT,
                    business_need TEXT,
                    duration_days INT,
                    status VARCHAR(50) DEFAULT 'pending',
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    reviewed_by VARCHAR(255),
                    review_notes TEXT,
                    granted_access VARCHAR(50),
                    granted_from TIMESTAMP,
                    granted_until TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id VARCHAR(255) PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id VARCHAR(255),
                    resource_id VARCHAR(255),
                    action VARCHAR(100),
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    session_id VARCHAR(255),
                    access_granted BOOLEAN,
                    denial_reason TEXT,
                    rows_accessed INT,
                    columns_accessed JSON,
                    query_text TEXT,
                    request_context JSON
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_id VARCHAR(255),
                    role_id VARCHAR(255),
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_by VARCHAR(255),
                    expires_at TIMESTAMP,
                    PRIMARY KEY (user_id, role_id)
                )
            """))
            
            conn.commit()
    
    def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token"""
        # In production, verify password hash
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, email, name, department, clearance_level, is_active
                FROM users WHERE email = :email
            """), {"email": email}).fetchone()
            
            if not result or not result.is_active:
                return None
            
            # Update last login
            conn.execute(text("""
                UPDATE users SET last_login = NOW() WHERE id = :id
            """), {"id": result.id})
            conn.commit()
            
            # Generate JWT
            token = jwt.encode({
                "user_id": result.id,
                "email": result.email,
                "name": result.name,
                "department": result.department,
                "clearance_level": result.clearance_level,
                "exp": datetime.utcnow() + timedelta(hours=24)
            }, self.jwt_secret, algorithm="HS256")
            
            return token
    
    def check_access(self, 
                     user_id: str, 
                     resource_id: str, 
                     action: str,
                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check if user has access to resource"""
        context = context or {}
        
        # Get user details
        user = self._get_user(user_id)
        if not user:
            return {"granted": False, "reason": "User not found"}
        
        # Get user's roles
        roles = self._get_user_roles(user_id)
        
        # Get applicable policies
        policies = self._get_applicable_policies(user_id, roles, resource_id, action)
        
        # Evaluate policies
        for policy in policies:
            if self._evaluate_policy(policy, user, context):
                if policy.effect == "deny":
                    return {"granted": False, "reason": "Access denied by policy"}
                else:
                    return {
                        "granted": True,
                        "access_level": self._determine_access_level(action),
                        "policy_id": policy.id
                    }
        
        return {"granted": False, "reason": "No matching policy found"}
    
    def _get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM users WHERE id = :id
            """), {"id": user_id}).fetchone()
            
            if result:
                return User(**dict(result))
            return None
    
    def _get_user_roles(self, user_id: str) -> List[Role]:
        """Get roles assigned to user"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT r.* FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = :user_id
                AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
            """), {"user_id": user_id}).fetchall()
            
            return [Role(**dict(r)) for r in results]
    
    def _get_applicable_policies(self, 
                                  user_id: str, 
                                  roles: List[Role], 
                                  resource_id: str, 
                                  action: str) -> List[AccessPolicy]:
        """Get policies applicable to this access request"""
        role_ids = [r.id for r in roles]
        
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT * FROM access_policies
                WHERE is_active = TRUE
                AND (expires_at IS NULL OR expires_at > NOW())
                AND (
                    users ? :user_id
                    OR roles ?| :role_ids
                    OR resources ?| :resource_patterns
                )
                AND actions ? :action
                ORDER BY priority ASC
            """), {
                "user_id": user_id,
                "role_ids": role_ids,
                "resource_patterns": [resource_id, "*"],
                "action": action
            }).fetchall()
            
            return [AccessPolicy(**dict(r)) for r in results]
    
    def _evaluate_policy(self, policy: AccessPolicy, user: User, context: Dict[str, Any]) -> bool:
        """Evaluate policy conditions"""
        conditions = policy.conditions
        
        # Check time-based conditions
        if "allowed_hours" in conditions:
            current_hour = datetime.utcnow().hour
            if current_hour not in conditions["allowed_hours"]:
                return False
        
        # Check location-based conditions
        if "allowed_ip_ranges" in conditions:
            user_ip = context.get("ip_address", "")
            if not any(self._ip_in_range(user_ip, r) for r in conditions["allowed_ip_ranges"]):
                return False
        
        # Check device conditions
        if "requires_device_registration" in conditions:
            if not context.get("device_registered", False):
                return False
        
        return True
    
    def _ip_in_range(self, ip: str, range_str: str) -> bool:
        """Check if IP is in range"""
        import ipaddress
        try:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(range_str)
        except:
            return False
    
    def _determine_access_level(self, action: str) -> AccessLevel:
        """Map action to access level"""
        action_map = {
            "read": AccessLevel.READ,
            "write": AccessLevel.WRITE,
            "delete": AccessLevel.ADMIN,
            "admin": AccessLevel.ADMIN
        }
        return action_map.get(action, AccessLevel.READ)
    
    def request_access(self, request: AccessRequest) -> str:
        """Submit access request"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO access_requests
                (id, user_id, resource_id, requested_access, justification,
                 business_need, duration_days, status, requested_at)
                VALUES
                (:id, :user_id, :resource_id, :requested_access, :justification,
                 :business_need, :duration_days, :status, :requested_at)
            """), request.dict())
            conn.commit()
        
        return request.id
    
    def approve_access_request(self, 
                                request_id: str, 
                                approver_id: str, 
                                notes: str,
                                granted_access: AccessLevel = None):
        """Approve an access request"""
        granted = granted_access.value if granted_access else None
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                UPDATE access_requests
                SET status = 'approved',
                    reviewed_at = NOW(),
                    reviewed_by = :approver_id,
                    review_notes = :notes,
                    granted_access = :granted_access,
                    granted_from = NOW(),
                    granted_until = NOW() + INTERVAL '1 day' * duration_days
                WHERE id = :request_id
            """), {
                "request_id": request_id,
                "approver_id": approver_id,
                "notes": notes,
                "granted_access": granted
            })
            conn.commit()
    
    def log_access(self, log_entry: AccessLog):
        """Log access attempt"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO access_logs
                (id, timestamp, user_id, resource_id, action, ip_address,
                 user_agent, session_id, access_granted, denial_reason,
                 rows_accessed, columns_accessed, query_text, request_context)
                VALUES
                (:id, :timestamp, :user_id, :resource_id, :action, :ip_address,
                 :user_agent, :session_id, :access_granted, :denial_reason,
                 :rows_accessed, :columns_accessed, :query_text, :request_context)
            """), log_entry.dict())
            conn.commit()
    
    def get_access_report(self, user_id: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Generate access report"""
        with self.engine.connect() as conn:
            query = """
                SELECT 
                    user_id,
                    resource_id,
                    action,
                    COUNT(*) as access_count,
                    SUM(CASE WHEN access_granted THEN 1 ELSE 0 END) as granted_count,
                    SUM(CASE WHEN NOT access_granted THEN 1 ELSE 0 END) as denied_count,
                    MAX(timestamp) as last_access
                FROM access_logs
                WHERE timestamp >= NOW() - INTERVAL ':days days'
            """
            params = {"days": days}
            
            if user_id:
                query += " AND user_id = :user_id"
                params["user_id"] = user_id
            
            query += " GROUP BY user_id, resource_id, action ORDER BY access_count DESC"
            
            results = conn.execute(text(query), params).fetchall()
            return [dict(r) for r in results]
```

### 7.4 OPA Policy Examples

```rego
# /mnt/okcomputer/output/resilience_ai_analysis/policies/data_access.rego

package resilienceai.dataaccess

import future.keywords.if
import future.keywords.in

# Default deny
default allow := false

# Allow if user has required clearance and all conditions met
allow if {
    user.clearance_level >= data.required_clearance[data.classification]
    user.data_access_training_completed
    user.department in data.allowed_departments
    check_time_restrictions
    check_location_restrictions
}

# Role-based permissions
allow if {
    user.roles[_] == "data_admin"
}

allow if {
    user.roles[_] == "data_steward"
    input.action == "read"
}

# Dataset-specific rules
allow if {
    input.dataset == "incident_reports"
    user.department == "operations"
    input.action in ["read", "write"]
}

allow if {
    input.dataset == "sensor_data"
    user.department == "iot_team"
    input.action == "read"
}

# PII data restrictions
allow if {
    input.contains_pii
    user.clearance_level >= 3
    input.purpose == "authorized_use"
    input.action == "read"
}

# Time-based restrictions
check_time_restrictions if {
    not data.time_restrictions.enabled
}

check_time_restrictions if {
    data.time_restrictions.enabled
    to_number(format(now, "15")) >= data.time_restrictions.start_hour
    to_number(format(now, "15")) < data.time_restrictions.end_hour
}

# Location-based restrictions
check_location_restrictions if {
    not data.location_restrictions.enabled
}

check_location_restrictions if {
    data.location_restrictions.enabled
    net.cidr_contains(data.location_restrictions.allowed_ranges[_], input.ip_address)
}

# Data masking rules
mask_field(field, user) := "***" if {
    field.sensitivity == "high"
    user.clearance_level < 3
}

mask_field(field, user) := field.value if {
    not field.sensitivity == "high"
}

mask_field(field, user) := field.value if {
    field.sensitivity == "high"
    user.clearance_level >= 3
}

# Row-level security
allowed_row(row, user) if {
    not row.restricted
}

allowed_row(row, user) if {
    row.restricted
    user.department == row.owner_department
}

# Audit logging requirements
audit_required if {
    input.dataset in data.sensitive_datasets
}

audit_required if {
    input.contains_pii
}

audit_required if {
    input.action in ["write", "delete"]
}
```



---

## 8. Data Retention Policies

### 8.1 Retention Framework

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/retention/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class RetentionAction(str, Enum):
    ARCHIVE = "archive"
    DELETE = "delete"
    ANONYMIZE = "anonymize"
    COMPRESS = "compress"
    MOVE_TO_COLD = "move_to_cold"

class RetentionPolicy(BaseModel):
    """Data retention policy definition"""
    id: str
    name: str
    description: str
    
    # Scope
    applies_to: List[str]  # Dataset IDs or patterns
    data_classification: Optional[str] = None
    
    # Retention periods (in days)
    active_retention_days: int  # How long to keep in active storage
    archive_retention_days: Optional[int] = None  # How long to keep in archive
    total_retention_days: int  # Total retention including archive
    
    # Actions
    active_to_archive_action: Optional[RetentionAction] = None
    archive_to_delete_action: RetentionAction = RetentionAction.DELETE
    
    # Legal hold
    legal_hold_possible: bool = True
    legal_hold_duration_days: Optional[int] = None
    
    # Metadata
    regulatory_framework: List[str] = []  # GDPR, CCPA, etc.
    business_justification: str
    owner: str
    approved_by: str
    approved_at: datetime
    
    # Status
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class RetentionSchedule(BaseModel):
    """Scheduled retention job"""
    id: str
    policy_id: str
    
    # Target
    dataset_id: str
    
    # Schedule
    scheduled_date: datetime
    action: RetentionAction
    
    # Status
    status: str = "scheduled"  # scheduled, in_progress, completed, failed
    executed_at: Optional[datetime] = None
    execution_result: Optional[str] = None
    
    # Details
    records_affected: Optional[int] = None
    storage_freed_bytes: Optional[int] = None

class LegalHold(BaseModel):
    """Legal hold on data"""
    id: str
    name: str
    description: str
    
    # Scope
    affected_datasets: List[str]
    affected_records_query: Optional[str] = None
    
    # Timing
    issued_at: datetime
    issued_by: str
    expires_at: Optional[datetime] = None
    
    # Status
    status: str = "active"  # active, released, expired
    released_at: Optional[datetime] = None
    released_by: Optional[str] = None
    
    # Legal reference
    case_number: Optional[str] = None
    legal_counsel: Optional[str] = None

class RetentionAuditLog(BaseModel):
    """Audit log for retention actions"""
    id: str
    timestamp: datetime
    action: str
    policy_id: str
    dataset_id: str
    
    # Details
    records_affected: int
    storage_impact_bytes: int
    
    # Context
    triggered_by: str  # scheduled, manual, legal_hold
    legal_hold_id: Optional[str] = None
    
    # Verification
    verification_status: str = "pending"  # pending, verified, failed
    verification_method: Optional[str] = None
```

### 8.2 Retention Service

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/retention/retention_service.py

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
import boto3
from google.cloud import bigquery
from .models import RetentionPolicy, RetentionSchedule, LegalHold, RetentionAction

class RetentionService:
    """
    Data retention management service
    Enforces retention policies and manages data lifecycle
    """
    
    def __init__(self, db_connection: str):
        self.engine = create_engine(db_connection)
        self.s3_client = boto3.client('s3')
        self._init_tables()
    
    def _init_tables(self):
        """Initialize retention tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS retention_policies (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255),
                    description TEXT,
                    applies_to JSON,
                    data_classification VARCHAR(50),
                    active_retention_days INT,
                    archive_retention_days INT,
                    total_retention_days INT,
                    active_to_archive_action VARCHAR(50),
                    archive_to_delete_action VARCHAR(50),
                    legal_hold_possible BOOLEAN DEFAULT TRUE,
                    legal_hold_duration_days INT,
                    regulatory_framework JSON,
                    business_justification TEXT,
                    owner VARCHAR(255),
                    approved_by VARCHAR(255),
                    approved_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS retention_schedules (
                    id VARCHAR(255) PRIMARY KEY,
                    policy_id VARCHAR(255),
                    dataset_id VARCHAR(255),
                    scheduled_date DATE,
                    action VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'scheduled',
                    executed_at TIMESTAMP,
                    execution_result TEXT,
                    records_affected INT,
                    storage_freed_bytes BIGINT
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS legal_holds (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255),
                    description TEXT,
                    affected_datasets JSON,
                    affected_records_query TEXT,
                    issued_at TIMESTAMP,
                    issued_by VARCHAR(255),
                    expires_at TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active',
                    released_at TIMESTAMP,
                    released_by VARCHAR(255),
                    case_number VARCHAR(255),
                    legal_counsel VARCHAR(255)
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS retention_audit_log (
                    id VARCHAR(255) PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action VARCHAR(100),
                    policy_id VARCHAR(255),
                    dataset_id VARCHAR(255),
                    records_affected INT,
                    storage_impact_bytes BIGINT,
                    triggered_by VARCHAR(100),
                    legal_hold_id VARCHAR(255),
                    verification_status VARCHAR(50),
                    verification_method VARCHAR(100)
                )
            """))
            
            conn.commit()
    
    def create_policy(self, policy: RetentionPolicy) -> str:
        """Create a new retention policy"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO retention_policies
                (id, name, description, applies_to, data_classification,
                 active_retention_days, archive_retention_days, total_retention_days,
                 active_to_archive_action, archive_to_delete_action,
                 legal_hold_possible, legal_hold_duration_days,
                 regulatory_framework, business_justification, owner,
                 approved_by, approved_at, is_active, created_at, updated_at)
                VALUES
                (:id, :name, :description, :applies_to, :data_classification,
                 :active_retention_days, :archive_retention_days, :total_retention_days,
                 :active_to_archive_action, :archive_to_delete_action,
                 :legal_hold_possible, :legal_hold_duration_days,
                 :regulatory_framework, :business_justification, :owner,
                 :approved_by, :approved_at, :is_active, :created_at, :updated_at)
            """), policy.dict())
            conn.commit()
        
        return policy.id
    
    def apply_retention_policy(self, policy_id: str, dataset_id: str):
        """Apply retention policy to a dataset"""
        policy = self._get_policy(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        # Check for legal holds
        if self._has_legal_hold(dataset_id):
            print(f"Dataset {dataset_id} has active legal hold, skipping retention")
            return
        
        # Calculate retention dates
        now = datetime.utcnow()
        archive_date = now - timedelta(days=policy.active_retention_days)
        delete_date = now - timedelta(days=policy.total_retention_days)
        
        # Schedule archive if applicable
        if policy.active_to_archive_action and policy.archive_retention_days:
            self._schedule_action(
                policy_id=policy_id,
                dataset_id=dataset_id,
                action=policy.active_to_archive_action,
                scheduled_date=archive_date
            )
        
        # Schedule deletion
        self._schedule_action(
            policy_id=policy_id,
            dataset_id=dataset_id,
            action=policy.archive_to_delete_action,
            scheduled_date=delete_date
        )
    
    def _schedule_action(self, policy_id: str, dataset_id: str, 
                         action: RetentionAction, scheduled_date: datetime):
        """Schedule a retention action"""
        schedule_id = f"{dataset_id}_{action.value}_{scheduled_date.strftime('%Y%m%d')}"
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO retention_schedules
                (id, policy_id, dataset_id, scheduled_date, action, status)
                VALUES
                (:id, :policy_id, :dataset_id, :scheduled_date, :action, 'scheduled')
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": schedule_id,
                "policy_id": policy_id,
                "dataset_id": dataset_id,
                "scheduled_date": scheduled_date,
                "action": action.value
            })
            conn.commit()
    
    def execute_scheduled_actions(self, date: datetime = None):
        """Execute retention actions scheduled for a date"""
        date = date or datetime.utcnow()
        
        with self.engine.connect() as conn:
            schedules = conn.execute(text("""
                SELECT * FROM retention_schedules
                WHERE scheduled_date <= :date
                AND status = 'scheduled'
            """), {"date": date}).fetchall()
        
        for schedule in schedules:
            self._execute_action(dict(schedule))
    
    def _execute_action(self, schedule: Dict[str, Any]):
        """Execute a single retention action"""
        dataset_id = schedule["dataset_id"]
        action = RetentionAction(schedule["action"])
        
        # Check legal hold again at execution time
        if self._has_legal_hold(dataset_id):
            self._update_schedule_status(schedule["id"], "skipped", "Legal hold in effect")
            return
        
        try:
            if action == RetentionAction.ARCHIVE:
                result = self._archive_data(dataset_id)
            elif action == RetentionAction.DELETE:
                result = self._delete_data(dataset_id)
            elif action == RetentionAction.ANONYMIZE:
                result = self._anonymize_data(dataset_id)
            elif action == RetentionAction.COMPRESS:
                result = self._compress_data(dataset_id)
            elif action == RetentionAction.MOVE_TO_COLD:
                result = self._move_to_cold_storage(dataset_id)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            self._update_schedule_status(
                schedule["id"], 
                "completed", 
                "Success",
                result.get("records_affected"),
                result.get("storage_freed_bytes")
            )
            
            # Log audit
            self._log_audit(schedule, result)
            
        except Exception as e:
            self._update_schedule_status(schedule["id"], "failed", str(e))
    
    def _archive_data(self, dataset_id: str) -> Dict[str, Any]:
        """Archive data to long-term storage"""
        # Implementation depends on storage backend
        # Example for S3:
        source_bucket = "resilience-ai-active"
        archive_bucket = "resilience-ai-archive"
        
        # Move objects to archive
        response = self.s3_client.list_objects_v2(
            Bucket=source_bucket,
            Prefix=dataset_id
        )
        
        records_affected = 0
        for obj in response.get('Contents', []):
            # Copy to archive
            self.s3_client.copy_object(
                CopySource={'Bucket': source_bucket, 'Key': obj['Key']},
                Bucket=archive_bucket,
                Key=obj['Key'],
                StorageClass='GLACIER'
            )
            # Delete from source
            self.s3_client.delete_object(
                Bucket=source_bucket,
                Key=obj['Key']
            )
            records_affected += 1
        
        return {
            "records_affected": records_affected,
            "storage_freed_bytes": sum(o['Size'] for o in response.get('Contents', []))
        }
    
    def _delete_data(self, dataset_id: str) -> Dict[str, Any]:
        """Permanently delete data"""
        # Implementation depends on storage backend
        # Example for BigQuery:
        client = bigquery.Client()
        
        # Get table info before deletion
        table_ref = dataset_id
        table = client.get_table(table_ref)
        row_count = table.num_rows
        size_bytes = table.num_bytes
        
        # Delete table
        client.delete_table(table_ref)
        
        return {
            "records_affected": row_count,
            "storage_freed_bytes": size_bytes
        }
    
    def _anonymize_data(self, dataset_id: str) -> Dict[str, Any]:
        """Anonymize personal data"""
        # Implementation using data masking/anonymization
        # This is a placeholder - actual implementation would use
        # techniques like k-anonymity, differential privacy, etc.
        return {
            "records_affected": 0,
            "storage_freed_bytes": 0
        }
    
    def _compress_data(self, dataset_id: str) -> Dict[str, Any]:
        """Compress data to save storage"""
        # Implementation for compression
        return {
            "records_affected": 0,
            "storage_freed_bytes": 0
        }
    
    def _move_to_cold_storage(self, dataset_id: str) -> Dict[str, Any]:
        """Move data to cold storage tier"""
        # Implementation for cold storage
        return {
            "records_affected": 0,
            "storage_freed_bytes": 0
        }
    
    def _has_legal_hold(self, dataset_id: str) -> bool:
        """Check if dataset has active legal hold"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count FROM legal_holds
                WHERE affected_datasets ? :dataset_id
                AND status = 'active'
                AND (expires_at IS NULL OR expires_at > NOW())
            """), {"dataset_id": dataset_id}).fetchone()
            
            return result.count > 0
    
    def create_legal_hold(self, hold: LegalHold) -> str:
        """Create a legal hold"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO legal_holds
                (id, name, description, affected_datasets, affected_records_query,
                 issued_at, issued_by, expires_at, status, case_number, legal_counsel)
                VALUES
                (:id, :name, :description, :affected_datasets, :affected_records_query,
                 :issued_at, :issued_by, :expires_at, :status, :case_number, :legal_counsel)
            """), hold.dict())
            conn.commit()
        
        return hold.id
    
    def release_legal_hold(self, hold_id: str, released_by: str):
        """Release a legal hold"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                UPDATE legal_holds
                SET status = 'released',
                    released_at = NOW(),
                    released_by = :released_by
                WHERE id = :hold_id
            """), {"hold_id": hold_id, "released_by": released_by})
            conn.commit()
    
    def get_retention_report(self) -> Dict[str, Any]:
        """Generate retention status report"""
        with self.engine.connect() as conn:
            # Policy summary
            policies = conn.execute(text("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active
                FROM retention_policies
            """)).fetchone()
            
            # Scheduled actions
            scheduled = conn.execute(text("""
                SELECT status, COUNT(*) as count
                FROM retention_schedules
                GROUP BY status
            """)).fetchall()
            
            # Legal holds
            holds = conn.execute(text("""
                SELECT status, COUNT(*) as count
                FROM legal_holds
                GROUP BY status
            """)).fetchall()
            
            # Storage impact
            storage = conn.execute(text("""
                SELECT 
                    SUM(storage_freed_bytes) as total_freed,
                    SUM(records_affected) as total_records
                FROM retention_audit_log
                WHERE timestamp >= NOW() - INTERVAL '30 days'
            """)).fetchone()
        
        return {
            "policies": {"total": policies.total, "active": policies.active},
            "scheduled_actions": {r.status: r.count for r in scheduled},
            "legal_holds": {h.status: h.count for h in holds},
            "storage_impact_30d": {
                "bytes_freed": storage.total_freed or 0,
                "records_affected": storage.total_records or 0
            }
        }
    
    def _get_policy(self, policy_id: str) -> Optional[RetentionPolicy]:
        """Get policy by ID"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM retention_policies WHERE id = :id
            """), {"id": policy_id}).fetchone()
            
            if result:
                return RetentionPolicy(**dict(result))
            return None
    
    def _update_schedule_status(self, schedule_id: str, status: str, 
                                 result: str, records: int = None, storage: int = None):
        """Update schedule execution status"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                UPDATE retention_schedules
                SET status = :status,
                    executed_at = NOW(),
                    execution_result = :result,
                    records_affected = :records,
                    storage_freed_bytes = :storage
                WHERE id = :schedule_id
            """), {
                "schedule_id": schedule_id,
                "status": status,
                "result": result,
                "records": records,
                "storage": storage
            })
            conn.commit()
    
    def _log_audit(self, schedule: Dict[str, Any], result: Dict[str, Any]):
        """Log retention action to audit"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO retention_audit_log
                (id, action, policy_id, dataset_id, records_affected,
                 storage_impact_bytes, triggered_by, verification_status)
                VALUES
                (:id, :action, :policy_id, :dataset_id, :records_affected,
                 :storage_impact_bytes, :triggered_by, :verification_status)
            """), {
                "id": f"audit_{schedule['id']}_{datetime.utcnow().isoformat()}",
                "action": schedule["action"],
                "policy_id": schedule["policy_id"],
                "dataset_id": schedule["dataset_id"],
                "records_affected": result.get("records_affected", 0),
                "storage_impact_bytes": result.get("storage_freed_bytes", 0),
                "triggered_by": "scheduled",
                "verification_status": "pending"
            })
            conn.commit()

# Default retention policies for ResilienceAI
DEFAULT_RETENTION_POLICIES = [
    RetentionPolicy(
        id="policy-incident-data",
        name="Incident Data Retention",
        description="Retention policy for disaster incident data",
        applies_to=["incidents.*", "damage_assessments.*"],
        active_retention_days=2555,  # 7 years
        total_retention_days=3650,  # 10 years
        archive_retention_days=1095,  # 3 years in archive
        active_to_archive_action=RetentionAction.ARCHIVE,
        archive_to_delete_action=RetentionAction.DELETE,
        regulatory_framework=["FEMA", "State_Emergency_Management"],
        business_justification="Regulatory requirement for disaster records",
        owner="data-governance@resilience.ai",
        approved_by="cto@resilience.ai",
        approved_at=datetime.utcnow()
    ),
    RetentionPolicy(
        id="policy-sensor-data",
        name="Sensor Data Retention",
        description="Retention policy for IoT sensor readings",
        applies_to=["sensor.*", "weather.*"],
        active_retention_days=90,  # 3 months active
        total_retention_days=1095,  # 3 years total
        archive_retention_days=1000,
        active_to_archive_action=RetentionAction.COMPRESS,
        archive_to_delete_action=RetentionAction.DELETE,
        regulatory_framework=[],
        business_justification="High volume data, aggregated for long-term analysis",
        owner="iot-team@resilience.ai",
        approved_by="cto@resilience.ai",
        approved_at=datetime.utcnow()
    ),
    RetentionPolicy(
        id="policy-personal-data",
        name="Personal Data Retention",
        description="GDPR-compliant retention for personal data",
        applies_to=["users.*", "citizens.*"],
        data_classification="confidential",
        active_retention_days=730,  # 2 years
        total_retention_days=730,
        archive_retention_days=None,
        active_to_archive_action=None,
        archive_to_delete_action=RetentionAction.ANONYMIZE,
        legal_hold_possible=True,
        regulatory_framework=["GDPR", "CCPA"],
        business_justification="Privacy regulations require data minimization",
        owner="privacy-officer@resilience.ai",
        approved_by="legal@resilience.ai",
        approved_at=datetime.utcnow()
    ),
    RetentionPolicy(
        id="policy-logs",
        name="System Logs Retention",
        description="Retention policy for system and audit logs",
        applies_to=["logs.*", "audit.*"],
        active_retention_days=90,
        total_retention_days=2555,  # 7 years
        archive_retention_days=2465,
        active_to_archive_action=RetentionAction.COMPRESS,
        archive_to_delete_action=RetentionAction.DELETE,
        regulatory_framework=["SOX", "Security_Audit"],
        business_justification="Security and compliance audit requirements",
        owner="security@resilience.ai",
        approved_by="ciso@resilience.ai",
        approved_at=datetime.utcnow()
    )
]
```

---

## 9. Compliance Tracking

### 9.1 Compliance Framework

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/compliance/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class ComplianceFramework(str, Enum):
    GDPR = "GDPR"
    CCPA = "CCPA"
    HIPAA = "HIPAA"
    SOX = "SOX"
    FEMA = "FEMA"
    ISO27001 = "ISO27001"
    SOC2 = "SOC2"
    NIST = "NIST"

class ControlStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"
    IN_PROGRESS = "in_progress"

class ComplianceControl(BaseModel):
    """Compliance control definition"""
    id: str
    framework: ComplianceFramework
    control_id: str  # e.g., "GDPR-Article-17"
    name: str
    description: str
    
    # Requirements
    requirement: str
    implementation_guidance: str
    
    # Scope
    applicable_datasets: List[str] = []
    applicable_systems: List[str] = []
    
    # Evidence
    evidence_required: List[str] = []
    evidence_location: Optional[str] = None
    
    # Ownership
    owner: str
    reviewer: str
    
    # Status
    status: ControlStatus = ControlStatus.IN_PROGRESS
    last_assessed: Optional[datetime] = None
    next_assessment: Optional[datetime] = None
    
    # Risk
    risk_level: str = "medium"  # low, medium, high, critical
    
    # Notes
    assessment_notes: str = ""
    remediation_plan: Optional[str] = None

class ComplianceAssessment(BaseModel):
    """Compliance assessment record"""
    id: str
    control_id: str
    assessed_at: datetime
    assessed_by: str
    
    # Results
    status: ControlStatus
    findings: List[str] = []
    evidence_reviewed: List[str] = []
    
    # Gap analysis
    gaps_identified: List[str] = []
    risk_rating: str
    
    # Remediation
    remediation_required: bool
    remediation_plan: Optional[str] = None
    remediation_deadline: Optional[datetime] = None
    
    # Sign-off
    reviewed_by: Optional[str] = None
    review_date: Optional[datetime] = None

class ComplianceReport(BaseModel):
    """Compliance status report"""
    id: str
    framework: ComplianceFramework
    generated_at: datetime
    generated_by: str
    
    # Summary
    total_controls: int
    compliant_controls: int
    non_compliant_controls: int
    partial_controls: int
    not_applicable_controls: int
    
    # Details
    control_statuses: List[Dict[str, Any]] = []
    
    # Risk
    high_risk_findings: int
    medium_risk_findings: int
    low_risk_findings: int
    
    # Trends
    compliance_score: float
    score_change: float  # Change from last period
    
    # Actions
    open_remediations: int
    overdue_remediations: int

class DataSubjectRequest(BaseModel):
    """Data subject access request (DSAR)"""
    id: str
    request_type: str  # access, deletion, portability, rectification
    
    # Subject
    subject_id: str
    subject_email: str
    verification_status: str = "pending"
    
    # Request details
    requested_at: datetime
    description: str
    
    # Processing
    status: str = "received"  # received, verifying, processing, completed, rejected
    assigned_to: Optional[str] = None
    deadline: datetime
    
    # Completion
    completed_at: Optional[datetime] = None
    data_provided_location: Optional[str] = None
    notes: str = ""

class PrivacyImpactAssessment(BaseModel):
    """Privacy Impact Assessment (PIA/DPIA)"""
    id: str
    name: str
    description: str
    
    # Scope
    affected_systems: List[str]
    affected_data_subjects: int
    data_types: List[str]
    
    # Assessment
    high_risk_processing: bool
    necessity_assessment: str
    proportionality_assessment: str
    
    # Risks
    identified_risks: List[Dict[str, Any]] = []
    mitigation_measures: List[str] = []
    residual_risk: str
    
    # Approval
    assessed_by: str
    assessed_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Status
    status: str = "draft"  # draft, under_review, approved, rejected
```

### 9.2 Compliance Service

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/compliance/compliance_service.py

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
from .models import ComplianceControl, ComplianceAssessment, ComplianceReport, DataSubjectRequest, ComplianceFramework

class ComplianceService:
    """
    Compliance tracking and management service
    Monitors adherence to regulatory frameworks
    """
    
    def __init__(self, db_connection: str):
        self.engine = create_engine(db_connection)
        self._init_tables()
        self._load_default_controls()
    
    def _init_tables(self):
        """Initialize compliance tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS compliance_controls (
                    id VARCHAR(255) PRIMARY KEY,
                    framework VARCHAR(50),
                    control_id VARCHAR(100),
                    name VARCHAR(255),
                    description TEXT,
                    requirement TEXT,
                    implementation_guidance TEXT,
                    applicable_datasets JSON,
                    applicable_systems JSON,
                    evidence_required JSON,
                    evidence_location VARCHAR(500),
                    owner VARCHAR(255),
                    reviewer VARCHAR(255),
                    status VARCHAR(50),
                    last_assessed TIMESTAMP,
                    next_assessment TIMESTAMP,
                    risk_level VARCHAR(50),
                    assessment_notes TEXT,
                    remediation_plan TEXT
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS compliance_assessments (
                    id VARCHAR(255) PRIMARY KEY,
                    control_id VARCHAR(255),
                    assessed_at TIMESTAMP,
                    assessed_by VARCHAR(255),
                    status VARCHAR(50),
                    findings JSON,
                    evidence_reviewed JSON,
                    gaps_identified JSON,
                    risk_rating VARCHAR(50),
                    remediation_required BOOLEAN,
                    remediation_plan TEXT,
                    remediation_deadline TIMESTAMP,
                    reviewed_by VARCHAR(255),
                    review_date TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS compliance_reports (
                    id VARCHAR(255) PRIMARY KEY,
                    framework VARCHAR(50),
                    generated_at TIMESTAMP,
                    generated_by VARCHAR(255),
                    total_controls INT,
                    compliant_controls INT,
                    non_compliant_controls INT,
                    partial_controls INT,
                    not_applicable_controls INT,
                    control_statuses JSON,
                    high_risk_findings INT,
                    medium_risk_findings INT,
                    low_risk_findings INT,
                    compliance_score FLOAT,
                    score_change FLOAT,
                    open_remediations INT,
                    overdue_remediations INT
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS data_subject_requests (
                    id VARCHAR(255) PRIMARY KEY,
                    request_type VARCHAR(50),
                    subject_id VARCHAR(255),
                    subject_email VARCHAR(255),
                    verification_status VARCHAR(50),
                    requested_at TIMESTAMP,
                    description TEXT,
                    status VARCHAR(50),
                    assigned_to VARCHAR(255),
                    deadline TIMESTAMP,
                    completed_at TIMESTAMP,
                    data_provided_location VARCHAR(500),
                    notes TEXT
                )
            """))
            
            conn.commit()
    
    def _load_default_controls(self):
        """Load default compliance controls"""
        default_controls = [
            # GDPR Controls
            ComplianceControl(
                id="gdpr-article-17",
                framework=ComplianceFramework.GDPR,
                control_id="Article-17",
                name="Right to Erasure",
                description="Data subjects have the right to have their personal data erased",
                requirement="Implement mechanisms to delete personal data upon request",
                implementation_guidance="Use retention service with anonymization for personal data",
                applicable_datasets=["users.*", "citizens.*"],
                applicable_systems=["user-management", "data-platform"],
                evidence_required=["deletion_procedures", "audit_logs"],
                owner="privacy-officer@resilience.ai",
                reviewer="legal@resilience.ai",
                risk_level="high"
            ),
            ComplianceControl(
                id="gdpr-article-15",
                framework=ComplianceFramework.GDPR,
                control_id="Article-15",
                name="Right of Access",
                description="Data subjects can request access to their personal data",
                requirement="Provide mechanism for data subjects to access their data",
                implementation_guidance="Implement DSAR workflow with 30-day SLA",
                applicable_datasets=["users.*", "citizens.*"],
                applicable_systems=["user-management", "data-platform"],
                evidence_required=["dsar_procedures", "response_times"],
                owner="privacy-officer@resilience.ai",
                reviewer="legal@resilience.ai",
                risk_level="high"
            ),
            # FEMA Controls
            ComplianceControl(
                id="fema-records-retention",
                framework=ComplianceFramework.FEMA,
                control_id="FEMA-Records-Retention",
                name="Disaster Records Retention",
                description="Maintain disaster-related records for specified periods",
                requirement="Retain incident data for minimum 7 years",
                implementation_guidance="Use retention policy for incident data with 10-year retention",
                applicable_datasets=["incidents.*", "damage_assessments.*"],
                applicable_systems=["incident-management", "data-platform"],
                evidence_required=["retention_policies", "audit_logs"],
                owner="data-governance@resilience.ai",
                reviewer="compliance@resilience.ai",
                risk_level="critical"
            ),
            # Security Controls
            ComplianceControl(
                id="nist-access-control",
                framework=ComplianceFramework.NIST,
                control_id="AC-2",
                name="Account Management",
                description="Manage system accounts including creation and termination",
                requirement="Implement automated account management and access reviews",
                implementation_guidance="Use access control service with quarterly reviews",
                applicable_datasets=["*"],
                applicable_systems=["all"],
                evidence_required=["access_policies", "review_records"],
                owner="security@resilience.ai",
                reviewer="ciso@resilience.ai",
                risk_level="high"
            ),
        ]
        
        for control in default_controls:
            self.create_control(control)
    
    def create_control(self, control: ComplianceControl) -> str:
        """Create a compliance control"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO compliance_controls
                (id, framework, control_id, name, description, requirement,
                 implementation_guidance, applicable_datasets, applicable_systems,
                 evidence_required, evidence_location, owner, reviewer, status,
                 risk_level)
                VALUES
                (:id, :framework, :control_id, :name, :description, :requirement,
                 :implementation_guidance, :applicable_datasets, :applicable_systems,
                 :evidence_required, :evidence_location, :owner, :reviewer, :status,
                 :risk_level)
                ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                status = EXCLUDED.status
            """), {
                **control.dict(),
                "framework": control.framework.value,
                "status": control.status.value
            })
            conn.commit()
        
        return control.id
    
    def assess_control(self, assessment: ComplianceAssessment):
        """Record a compliance assessment"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO compliance_assessments
                (id, control_id, assessed_at, assessed_by, status, findings,
                 evidence_reviewed, gaps_identified, risk_rating,
                 remediation_required, remediation_plan, remediation_deadline,
                 reviewed_by, review_date)
                VALUES
                (:id, :control_id, :assessed_at, :assessed_by, :status, :findings,
                 :evidence_reviewed, :gaps_identified, :risk_rating,
                 :remediation_required, :remediation_plan, :remediation_deadline,
                 :reviewed_by, :review_date)
            """), {
                **assessment.dict(),
                "status": assessment.status.value,
                "findings": assessment.findings,
                "evidence_reviewed": assessment.evidence_reviewed,
                "gaps_identified": assessment.gaps_identified
            })
            
            # Update control status
            conn.execute(text("""
                UPDATE compliance_controls
                SET status = :status,
                    last_assessed = :assessed_at,
                    next_assessment = :next_assessment,
                    assessment_notes = :notes
                WHERE id = :control_id
            """), {
                "control_id": assessment.control_id,
                "status": assessment.status.value,
                "assessed_at": assessment.assessed_at,
                "next_assessment": assessment.assessed_at + timedelta(days=90),
                "notes": "; ".join(assessment.findings)
            })
            
            conn.commit()
    
    def generate_compliance_report(self, framework: ComplianceFramework) -> ComplianceReport:
        """Generate compliance report for a framework"""
        with self.engine.connect() as conn:
            # Get control counts
            counts = conn.execute(text("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    SUM(CASE WHEN risk_level = 'high' OR risk_level = 'critical' THEN 1 ELSE 0 END) as high_risk
                FROM compliance_controls
                WHERE framework = :framework
                GROUP BY status
            """), {"framework": framework.value}).fetchall()
        
        status_counts = {r.status: {"count": r.count, "high_risk": r.high_risk} for r in counts}
        
        total = sum(s["count"] for s in status_counts.values())
        compliant = status_counts.get("compliant", {}).get("count", 0)
        non_compliant = status_counts.get("non_compliant", {}).get("count", 0)
        partial = status_counts.get("partial", {}).get("count", 0)
        not_applicable = status_counts.get("not_applicable", {}).get("count", 0)
        
        high_risk = sum(s.get("high_risk", 0) for s in status_counts.values())
        
        # Calculate score
        if total > 0:
            compliance_score = (compliant + not_applicable) / total * 100
        else:
            compliance_score = 0
        
        report = ComplianceReport(
            id=f"report-{framework.value}-{datetime.utcnow().strftime('%Y%m%d')}",
            framework=framework,
            generated_at=datetime.utcnow(),
            generated_by="compliance-service",
            total_controls=total,
            compliant_controls=compliant,
            non_compliant_controls=non_compliant,
            partial_controls=partial,
            not_applicable_controls=not_applicable,
            high_risk_findings=high_risk,
            medium_risk_findings=0,
            low_risk_findings=0,
            compliance_score=compliance_score,
            score_change=0,  # Would compare with previous report
            open_remediations=non_compliant + partial,
            overdue_remediations=0
        )
        
        # Store report
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO compliance_reports
                (id, framework, generated_at, generated_by, total_controls,
                 compliant_controls, non_compliant_controls, partial_controls,
                 not_applicable_controls, control_statuses, high_risk_findings,
                 medium_risk_findings, low_risk_findings, compliance_score,
                 score_change, open_remediations, overdue_remediations)
                VALUES
                (:id, :framework, :generated_at, :generated_by, :total_controls,
                 :compliant_controls, :non_compliant_controls, :partial_controls,
                 :not_applicable_controls, :control_statuses, :high_risk_findings,
                 :medium_risk_findings, :low_risk_findings, :compliance_score,
                 :score_change, :open_remediations, :overdue_remediations)
            """), {
                **report.dict(),
                "framework": report.framework.value,
                "control_statuses": [{"status": k, **v} for k, v in status_counts.items()]
            })
            conn.commit()
        
        return report
    
    def create_data_subject_request(self, request: DataSubjectRequest) -> str:
        """Create a data subject request"""
        # Set deadline (30 days for GDPR)
        request.deadline = datetime.utcnow() + timedelta(days=30)
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO data_subject_requests
                (id, request_type, subject_id, subject_email, verification_status,
                 requested_at, description, status, deadline)
                VALUES
                (:id, :request_type, :subject_id, :subject_email, :verification_status,
                 :requested_at, :description, :status, :deadline)
            """), request.dict())
            conn.commit()
        
        return request.id
    
    def get_pending_dsars(self) -> List[DataSubjectRequest]:
        """Get pending data subject requests"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT * FROM data_subject_requests
                WHERE status NOT IN ('completed', 'rejected')
                ORDER BY deadline ASC
            """)).fetchall()
            
            return [DataSubjectRequest(**dict(r)) for r in results]
    
    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        with self.engine.connect() as conn:
            # Overall compliance by framework
            framework_stats = conn.execute(text("""
                SELECT 
                    framework,
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'compliant' THEN 1 ELSE 0 END) as compliant
                FROM compliance_controls
                GROUP BY framework
            """)).fetchall()
            
            # Recent assessments
            recent_assessments = conn.execute(text("""
                SELECT * FROM compliance_assessments
                ORDER BY assessed_at DESC
                LIMIT 10
            """)).fetchall()
            
            # Pending DSARs
            pending_dsars = conn.execute(text("""
                SELECT COUNT(*) as count,
                       SUM(CASE WHEN deadline < NOW() + INTERVAL '7 days' THEN 1 ELSE 0 END) as urgent
                FROM data_subject_requests
                WHERE status NOT IN ('completed', 'rejected')
            """)).fetchone()
        
        return {
            "framework_compliance": {
                r.framework: {
                    "total": r.total,
                    "compliant": r.compliant,
                    "score": round(r.compliant / r.total * 100, 1) if r.total > 0 else 0
                } for r in framework_stats
            },
            "recent_assessments": [dict(r) for r in recent_assessments],
            "pending_dsars": {
                "total": pending_dsars.count,
                "urgent": pending_dsars.urgent
            }
        }
```



---

## 10. Data Stewardship

### 10.1 Stewardship Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA STEWARDSHIP FRAMEWORK                        │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   Data       │    │   Steward    │    │   Data       │          │
│   │   Domain     │    │   Assignment │    │   Quality    │          │
│   │   Owners     │    │   Matrix     │    │   Reviews    │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   Metadata   │    │   Issue      │    │   Steward    │          │
│   │   Curation   │    │   Escalation │    │   Dashboard  │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.2 Stewardship Models

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/stewardship/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class StewardRole(str, Enum):
    DATA_OWNER = "data_owner"
    DATA_STEWARD = "data_steward"
    TECHNICAL_STEWARD = "technical_steward"
    BUSINESS_STEWARD = "business_steward"
    COMPLIANCE_STEWARD = "compliance_steward"

class Steward(BaseModel):
    """Data steward definition"""
    id: str
    user_id: str
    name: str
    email: str
    
    # Role
    role: StewardRole
    domain: str
    
    # Responsibilities
    assigned_datasets: List[str] = []
    responsibilities: List[str] = []
    
    # Qualifications
    certifications: List[str] = []
    training_completed: List[str] = []
    
    # Contact
    backup_steward: Optional[str] = None
    escalation_contact: str
    
    # Status
    is_active: bool = True
    assigned_at: datetime
    
    # Performance
    issues_resolved: int = 0
    avg_resolution_time_hours: Optional[float] = None

class StewardshipTask(BaseModel):
    """Task assigned to a data steward"""
    id: str
    title: str
    description: str
    task_type: str  # metadata_update, quality_review, access_review, compliance_check
    
    # Assignment
    assigned_to: str  # Steward ID
    assigned_by: str
    assigned_at: datetime
    
    # Target
    dataset_id: Optional[str] = None
    priority: str = "medium"  # low, medium, high, critical
    
    # Timeline
    due_date: datetime
    completed_at: Optional[datetime] = None
    
    # Status
    status: str = "open"  # open, in_progress, completed, escalated
    
    # Details
    acceptance_criteria: List[str] = []
    completion_notes: Optional[str] = None

class DataIssue(BaseModel):
    """Data quality or governance issue"""
    id: str
    title: str
    description: str
    issue_type: str  # quality, metadata, access, compliance, other
    severity: str  # low, medium, high, critical
    
    # Location
    dataset_id: str
    affected_records: Optional[int] = None
    
    # Reporting
    reported_by: str
    reported_at: datetime
    
    # Assignment
    assigned_to: Optional[str] = None
    assigned_at: Optional[datetime] = None
    
    # Resolution
    status: str = "open"  # open, investigating, resolved, closed
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None
    
    # Impact
    downstream_impact: List[str] = []
    
    # SLA
    sla_hours: int
    sla_breach: bool = False

class StewardshipMetrics(BaseModel):
    """Metrics for stewardship program"""
    steward_id: str
    period_start: datetime
    period_end: datetime
    
    # Task metrics
    tasks_assigned: int
    tasks_completed: int
    tasks_overdue: int
    avg_completion_time_hours: float
    
    # Issue metrics
    issues_assigned: int
    issues_resolved: int
    avg_resolution_time_hours: float
    
    # Quality metrics
    datasets_under_management: int
    quality_reviews_completed: int
    metadata_updates: int
    
    # Compliance metrics
    compliance_reviews_completed: int
    compliance_issues_identified: int
```

### 10.3 Stewardship Service

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/stewardship/stewardship_service.py

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
from .models import Steward, StewardshipTask, DataIssue, StewardRole

class StewardshipService:
    """
    Data stewardship management service
    Coordinates steward assignments, tasks, and metrics
    """
    
    def __init__(self, db_connection: str):
        self.engine = create_engine(db_connection)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize stewardship tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stewards (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255),
                    name VARCHAR(255),
                    email VARCHAR(255),
                    role VARCHAR(50),
                    domain VARCHAR(100),
                    assigned_datasets JSON,
                    responsibilities JSON,
                    certifications JSON,
                    training_completed JSON,
                    backup_steward VARCHAR(255),
                    escalation_contact VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    assigned_at TIMESTAMP,
                    issues_resolved INT DEFAULT 0,
                    avg_resolution_time_hours FLOAT
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stewardship_tasks (
                    id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(255),
                    description TEXT,
                    task_type VARCHAR(100),
                    assigned_to VARCHAR(255),
                    assigned_by VARCHAR(255),
                    assigned_at TIMESTAMP,
                    dataset_id VARCHAR(255),
                    priority VARCHAR(50),
                    due_date TIMESTAMP,
                    completed_at TIMESTAMP,
                    status VARCHAR(50),
                    acceptance_criteria JSON,
                    completion_notes TEXT
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS data_issues (
                    id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(255),
                    description TEXT,
                    issue_type VARCHAR(100),
                    severity VARCHAR(50),
                    dataset_id VARCHAR(255),
                    affected_records INT,
                    reported_by VARCHAR(255),
                    reported_at TIMESTAMP,
                    assigned_to VARCHAR(255),
                    assigned_at TIMESTAMP,
                    status VARCHAR(50),
                    resolution TEXT,
                    resolved_by VARCHAR(255),
                    resolved_at TIMESTAMP,
                    downstream_impact JSON,
                    sla_hours INT,
                    sla_breach BOOLEAN DEFAULT FALSE
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stewardship_metrics (
                    id SERIAL PRIMARY KEY,
                    steward_id VARCHAR(255),
                    period_start TIMESTAMP,
                    period_end TIMESTAMP,
                    tasks_assigned INT,
                    tasks_completed INT,
                    tasks_overdue INT,
                    avg_completion_time_hours FLOAT,
                    issues_assigned INT,
                    issues_resolved INT,
                    avg_resolution_time_hours FLOAT,
                    datasets_under_management INT,
                    quality_reviews_completed INT,
                    metadata_updates INT,
                    compliance_reviews_completed INT,
                    compliance_issues_identified INT
                )
            """))
            
            conn.commit()
    
    def create_steward(self, steward: Steward) -> str:
        """Create a new data steward"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO stewards
                (id, user_id, name, email, role, domain, assigned_datasets,
                 responsibilities, certifications, training_completed,
                 backup_steward, escalation_contact, is_active, assigned_at)
                VALUES
                (:id, :user_id, :name, :email, :role, :domain, :assigned_datasets,
                 :responsibilities, :certifications, :training_completed,
                 :backup_steward, :escalation_contact, :is_active, :assigned_at)
            """), {
                **steward.dict(),
                "role": steward.role.value
            })
            conn.commit()
        
        return steward.id
    
    def assign_steward_to_dataset(self, steward_id: str, dataset_id: str):
        """Assign a steward to a dataset"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                UPDATE stewards
                SET assigned_datasets = assigned_datasets || :dataset_id::jsonb
                WHERE id = :steward_id
            """), {
                "steward_id": steward_id,
                "dataset_id": f'["{dataset_id}"]'
            })
            conn.commit()
    
    def create_task(self, task: StewardshipTask) -> str:
        """Create a stewardship task"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO stewardship_tasks
                (id, title, description, task_type, assigned_to, assigned_by,
                 assigned_at, dataset_id, priority, due_date, status, acceptance_criteria)
                VALUES
                (:id, :title, :description, :task_type, :assigned_to, :assigned_by,
                 :assigned_at, :dataset_id, :priority, :due_date, :status, :acceptance_criteria)
            """), task.dict())
            conn.commit()
        
        # Notify steward
        self._notify_steward(task.assigned_to, f"New task assigned: {task.title}")
        
        return task.id
    
    def report_issue(self, issue: DataIssue) -> str:
        """Report a data issue"""
        # Auto-assign based on dataset
        steward = self._find_steward_for_dataset(issue.dataset_id)
        if steward:
            issue.assigned_to = steward
            issue.assigned_at = datetime.utcnow()
        
        # Set SLA based on severity
        sla_map = {"low": 168, "medium": 72, "high": 24, "critical": 4}
        issue.sla_hours = sla_map.get(issue.severity, 72)
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO data_issues
                (id, title, description, issue_type, severity, dataset_id,
                 affected_records, reported_by, reported_at, assigned_to,
                 assigned_at, status, downstream_impact, sla_hours, sla_breach)
                VALUES
                (:id, :title, :description, :issue_type, :severity, :dataset_id,
                 :affected_records, :reported_by, :reported_at, :assigned_to,
                 :assigned_at, :status, :downstream_impact, :sla_hours, :sla_breach)
            """), issue.dict())
            conn.commit()
        
        # Notify assigned steward
        if issue.assigned_to:
            self._notify_steward(issue.assigned_to, f"New issue assigned: {issue.title}")
        
        return issue.id
    
    def resolve_issue(self, issue_id: str, resolution: str, resolved_by: str):
        """Resolve a data issue"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                UPDATE data_issues
                SET status = 'resolved',
                    resolution = :resolution,
                    resolved_by = :resolved_by,
                    resolved_at = NOW()
                WHERE id = :issue_id
            """), {
                "issue_id": issue_id,
                "resolution": resolution,
                "resolved_by": resolved_by
            })
            conn.commit()
    
    def get_steward_dashboard(self, steward_id: str) -> Dict[str, Any]:
        """Get dashboard data for a steward"""
        with self.engine.connect() as conn:
            # Open tasks
            open_tasks = conn.execute(text("""
                SELECT * FROM stewardship_tasks
                WHERE assigned_to = :steward_id
                AND status IN ('open', 'in_progress')
                ORDER BY due_date ASC
            """), {"steward_id": steward_id}).fetchall()
            
            # Open issues
            open_issues = conn.execute(text("""
                SELECT * FROM data_issues
                WHERE assigned_to = :steward_id
                AND status IN ('open', 'investigating')
                ORDER BY reported_at DESC
            """), {"steward_id": steward_id}).fetchall()
            
            # Datasets under management
            datasets = conn.execute(text("""
                SELECT assigned_datasets FROM stewards WHERE id = :steward_id
            """), {"steward_id": steward_id}).fetchone()
            
            # Recent activity
            recent_activity = conn.execute(text("""
                SELECT 'task_completed' as type, title, completed_at as timestamp
                FROM stewardship_tasks
                WHERE assigned_to = :steward_id AND status = 'completed'
                AND completed_at > NOW() - INTERVAL '30 days'
                UNION ALL
                SELECT 'issue_resolved' as type, title, resolved_at as timestamp
                FROM data_issues
                WHERE assigned_to = :steward_id AND status = 'resolved'
                AND resolved_at > NOW() - INTERVAL '30 days'
                ORDER BY timestamp DESC
                LIMIT 10
            """), {"steward_id": steward_id}).fetchall()
        
        return {
            "open_tasks": [dict(t) for t in open_tasks],
            "open_issues": [dict(i) for i in open_issues],
            "datasets_managed": datasets.assigned_datasets if datasets else [],
            "recent_activity": [dict(a) for a in recent_activity],
            "stats": {
                "open_tasks_count": len(open_tasks),
                "open_issues_count": len(open_issues),
                "overdue_tasks": sum(1 for t in open_tasks if t.due_date < datetime.utcnow())
            }
        }
    
    def get_stewardship_program_metrics(self) -> Dict[str, Any]:
        """Get overall stewardship program metrics"""
        with self.engine.connect() as conn:
            # Steward counts
            steward_counts = conn.execute(text("""
                SELECT 
                    role,
                    COUNT(*) as count,
                    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active
                FROM stewards
                GROUP BY role
            """)).fetchall()
            
            # Issue metrics
            issue_metrics = conn.execute(text("""
                SELECT 
                    status,
                    severity,
                    COUNT(*) as count,
                    AVG(EXTRACT(EPOCH FROM (resolved_at - reported_at))/3600) as avg_resolution_hours
                FROM data_issues
                GROUP BY status, severity
            """)).fetchall()
            
            # Task metrics
            task_metrics = conn.execute(text("""
                SELECT 
                    status,
                    priority,
                    COUNT(*) as count
                FROM stewardship_tasks
                GROUP BY status, priority
            """)).fetchall()
            
            # SLA breaches
            sla_breaches = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM data_issues
                WHERE sla_breach = TRUE
                AND status NOT IN ('resolved', 'closed')
            """)).fetchone()
        
        return {
            "stewards": {
                r.role: {"total": r.count, "active": r.active} for r in steward_counts
            },
            "issues": {
                f"{r.status}_{r.severity}": {
                    "count": r.count,
                    "avg_resolution_hours": r.avg_resolution_hours
                } for r in issue_metrics
            },
            "tasks": {
                f"{r.status}_{r.priority}": r.count for r in task_metrics
            },
            "sla_breaches": sla_breaches.count if sla_breaches else 0
        }
    
    def _find_steward_for_dataset(self, dataset_id: str) -> Optional[str]:
        """Find appropriate steward for a dataset"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id FROM stewards
                WHERE assigned_datasets ? :dataset_id
                AND is_active = TRUE
                ORDER BY issues_resolved ASC
                LIMIT 1
            """), {"dataset_id": dataset_id}).fetchone()
            
            return result.id if result else None
    
    def _notify_steward(self, steward_id: str, message: str):
        """Notify steward (placeholder for actual notification)"""
        # In production, integrate with email/Slack
        print(f"[NOTIFICATION] Steward {steward_id}: {message}")
    
    def run_sla_check(self):
        """Check for SLA breaches and update status"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                UPDATE data_issues
                SET sla_breach = TRUE
                WHERE status NOT IN ('resolved', 'closed')
                AND reported_at + INTERVAL '1 hour' * sla_hours < NOW()
                AND sla_breach = FALSE
            """))
            conn.commit()

# Default stewardship assignments for ResilienceAI
DEFAULT_STEWARDSHIP_ASSIGNMENTS = [
    {
        "domain": "geospatial",
        "steward": {
            "id": "steward-geo-001",
            "user_id": "user-geo-001",
            "name": "Sarah Chen",
            "email": "s.chen@resilience.ai",
            "role": StewardRole.DATA_STEWARD,
            "domain": "geospatial",
            "responsibilities": [
                "Metadata management for geospatial datasets",
                "Quality monitoring for satellite imagery",
                "Coordinate system standardization",
                "Data lineage tracking"
            ],
            "escalation_contact": "geo-lead@resilience.ai"
        }
    },
    {
        "domain": "sensor_data",
        "steward": {
            "id": "steward-iot-001",
            "user_id": "user-iot-001",
            "name": "Michael Rodriguez",
            "email": "m.rodriguez@resilience.ai",
            "role": StewardRole.TECHNICAL_STEWARD,
            "domain": "sensor_data",
            "responsibilities": [
                "Sensor data quality monitoring",
                "Calibration data management",
                "IoT device metadata",
                "Real-time data validation"
            ],
            "escalation_contact": "iot-lead@resilience.ai"
        }
    },
    {
        "domain": "incident_reports",
        "steward": {
            "id": "steward-ops-001",
            "user_id": "user-ops-001",
            "name": "Jennifer Park",
            "email": "j.park@resilience.ai",
            "role": StewardRole.BUSINESS_STEWARD,
            "domain": "incident_reports",
            "responsibilities": [
                "Incident data quality",
                "Classification standardization",
                "Compliance with FEMA requirements",
                "Historical data accuracy"
            ],
            "escalation_contact": "ops-lead@resilience.ai"
        }
    },
    {
        "domain": "personal_data",
        "steward": {
            "id": "steward-privacy-001",
            "user_id": "user-privacy-001",
            "name": "David Kim",
            "email": "d.kim@resilience.ai",
            "role": StewardRole.COMPLIANCE_STEWARD,
            "domain": "personal_data",
            "responsibilities": [
                "GDPR compliance monitoring",
                "Data subject request handling",
                "Privacy impact assessments",
                "Retention policy enforcement"
            ],
            "escalation_contact": "legal@resilience.ai"
        }
    }
]
```

---

## 11. Governance Workflows

### 11.1 Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GOVERNANCE WORKFLOW ENGINE                        │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   Workflow   │    │   Approval   │    │   Notification│          │
│   │   Definitions│    │   Engine     │    │   Service     │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │   State      │    │   Task       │    │   Audit       │          │
│   │   Machine    │    │   Scheduler  │    │   Trail       │          │
│   └──────────────┘    └──────────────┘    └──────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

### 11.2 Workflow Definitions

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/workflows/models.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkflowStepType(str, Enum):
    APPROVAL = "approval"
    REVIEW = "review"
    TASK = "task"
    NOTIFICATION = "notification"
    CONDITIONAL = "conditional"
    AUTOMATED = "automated"

class WorkflowStep(BaseModel):
    """Individual step in a workflow"""
    id: str
    name: str
    description: str
    step_type: WorkflowStepType
    
    # Assignment
    assignee_role: Optional[str] = None
    assignee_users: List[str] = []
    
    # Configuration
    config: Dict[str, Any] = {}
    
    # Dependencies
    depends_on: List[str] = []  # Step IDs that must complete first
    
    # SLA
    sla_hours: Optional[int] = None
    
    # Actions
    on_approve: Optional[str] = None  # Next step ID
    on_reject: Optional[str] = None
    on_timeout: Optional[str] = None

class WorkflowDefinition(BaseModel):
    """Workflow template definition"""
    id: str
    name: str
    description: str
    version: str
    
    # Scope
    applies_to: List[str]  # Dataset types, actions, etc.
    
    # Steps
    steps: List[WorkflowStep]
    
    # Triggers
    auto_trigger_conditions: List[str] = []
    
    # Metadata
    owner: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class WorkflowInstance(BaseModel):
    """Running instance of a workflow"""
    id: str
    definition_id: str
    definition_version: str
    
    # Context
    context: Dict[str, Any]  # Dataset ID, request details, etc.
    
    # Status
    status: WorkflowStatus
    current_step: str
    
    # Timeline
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # Steps status
    step_statuses: Dict[str, str] = {}  # step_id -> status
    step_assignees: Dict[str, str] = {}  # step_id -> user_id
    step_completions: Dict[str, datetime] = {}  # step_id -> completion_time
    
    # Results
    outcome: Optional[str] = None
    notes: str = ""

class WorkflowAction(BaseModel):
    """Action taken in a workflow"""
    id: str
    workflow_id: str
    step_id: str
    
    # Actor
    user_id: str
    user_name: str
    
    # Action
    action: str  # approve, reject, comment, delegate
    comment: Optional[str] = None
    
    # Timestamp
    timestamp: datetime
    
    # Context
    attachments: List[str] = []
```

### 11.3 Workflow Engine

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/workflows/workflow_engine.py

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
from .models import WorkflowDefinition, WorkflowInstance, WorkflowStep, WorkflowAction, WorkflowStatus

class WorkflowEngine:
    """
    Governance workflow engine
    Manages approval workflows, reviews, and governance processes
    """
    
    def __init__(self, db_connection: str):
        self.engine = create_engine(db_connection)
        self._init_tables()
        self._load_default_workflows()
    
    def _init_tables(self):
        """Initialize workflow tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workflow_definitions (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255),
                    description TEXT,
                    version VARCHAR(50),
                    applies_to JSON,
                    steps JSON,
                    auto_trigger_conditions JSON,
                    owner VARCHAR(255),
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workflow_instances (
                    id VARCHAR(255) PRIMARY KEY,
                    definition_id VARCHAR(255),
                    definition_version VARCHAR(50),
                    context JSON,
                    status VARCHAR(50),
                    current_step VARCHAR(255),
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    step_statuses JSON,
                    step_assignees JSON,
                    step_completions JSON,
                    outcome VARCHAR(255),
                    notes TEXT
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workflow_actions (
                    id VARCHAR(255) PRIMARY KEY,
                    workflow_id VARCHAR(255),
                    step_id VARCHAR(255),
                    user_id VARCHAR(255),
                    user_name VARCHAR(255),
                    action VARCHAR(100),
                    comment TEXT,
                    timestamp TIMESTAMP,
                    attachments JSON
                )
            """))
            
            conn.commit()
    
    def _load_default_workflows(self):
        """Load default governance workflows"""
        default_workflows = [
            # Data Access Request Workflow
            WorkflowDefinition(
                id="wf-data-access-request",
                name="Data Access Request",
                description="Workflow for requesting access to data assets",
                version="1.0",
                applies_to=["access_request"],
                steps=[
                    WorkflowStep(
                        id="step-1",
                        name="Initial Review",
                        description="Data steward reviews the request",
                        step_type=WorkflowStepType.REVIEW,
                        assignee_role="data_steward",
                        sla_hours=24,
                        on_approve="step-2",
                        on_reject="step-rejected"
                    ),
                    WorkflowStep(
                        id="step-2",
                        name="Security Review",
                        description="Security team reviews for compliance",
                        step_type=WorkflowStepType.APPROVAL,
                        assignee_role="security_officer",
                        sla_hours=48,
                        on_approve="step-3",
                        on_reject="step-rejected"
                    ),
                    WorkflowStep(
                        id="step-3",
                        name="Data Owner Approval",
                        description="Data owner provides final approval",
                        step_type=WorkflowStepType.APPROVAL,
                        assignee_role="data_owner",
                        sla_hours=72,
                        on_approve="step-approved",
                        on_reject="step-rejected"
                    ),
                    WorkflowStep(
                        id="step-approved",
                        name="Access Granted",
                        description="Access has been granted",
                        step_type=WorkflowStepType.AUTOMATED,
                        config={"action": "grant_access"}
                    ),
                    WorkflowStep(
                        id="step-rejected",
                        name="Access Denied",
                        description="Access request has been denied",
                        step_type=WorkflowStepType.NOTIFICATION,
                        config={"notify": "requester"}
                    )
                ],
                owner="data-governance@resilience.ai",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            # Schema Change Workflow
            WorkflowDefinition(
                id="wf-schema-change",
                name="Schema Change Request",
                description="Workflow for proposing changes to data schemas",
                version="1.0",
                applies_to=["schema_change"],
                steps=[
                    WorkflowStep(
                        id="step-1",
                        name="Impact Analysis",
                        description="Analyze impact on downstream systems",
                        step_type=WorkflowStepType.TASK,
                        assignee_role="data_engineer",
                        sla_hours=48
                    ),
                    WorkflowStep(
                        id="step-2",
                        name="Steward Review",
                        description="Data steward reviews impact analysis",
                        step_type=WorkflowStepType.REVIEW,
                        assignee_role="data_steward",
                        depends_on=["step-1"],
                        sla_hours=24
                    ),
                    WorkflowStep(
                        id="step-3",
                        name="Downstream Notification",
                        description="Notify downstream consumers",
                        step_type=WorkflowStepType.NOTIFICATION,
                        config={"notify": "downstream_consumers"}
                    ),
                    WorkflowStep(
                        id="step-4",
                        name="Final Approval",
                        description="Data owner approves the change",
                        step_type=WorkflowStepType.APPROVAL,
                        assignee_role="data_owner",
                        depends_on=["step-2", "step-3"],
                        sla_hours=72
                    )
                ],
                owner="data-governance@resilience.ai",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            # Data Quality Issue Workflow
            WorkflowDefinition(
                id="wf-quality-issue",
                name="Data Quality Issue Resolution",
                description="Workflow for resolving data quality issues",
                version="1.0",
                applies_to=["quality_issue"],
                steps=[
                    WorkflowStep(
                        id="step-1",
                        name="Triage",
                        description="Initial triage and severity assessment",
                        step_type=WorkflowStepType.TASK,
                        assignee_role="data_steward",
                        sla_hours=4
                    ),
                    WorkflowStep(
                        id="step-2",
                        name="Investigation",
                        description="Investigate root cause",
                        step_type=WorkflowStepType.TASK,
                        assignee_role="data_engineer",
                        depends_on=["step-1"],
                        sla_hours=24
                    ),
                    WorkflowStep(
                        id="step-3",
                        name="Fix Implementation",
                        description="Implement fix for the issue",
                        step_type=WorkflowStepType.TASK,
                        assignee_role="data_engineer",
                        depends_on=["step-2"],
                        sla_hours=48
                    ),
                    WorkflowStep(
                        id="step-4",
                        name="Verification",
                        description="Verify the fix resolved the issue",
                        step_type=WorkflowStepType.REVIEW,
                        assignee_role="data_steward",
                        depends_on=["step-3"],
                        sla_hours=24
                    )
                ],
                auto_trigger_conditions=["quality_score_below_threshold"],
                owner="data-quality@resilience.ai",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            # New Dataset Onboarding Workflow
            WorkflowDefinition(
                id="wf-dataset-onboarding",
                name="New Dataset Onboarding",
                description="Workflow for onboarding new datasets",
                version="1.0",
                applies_to=["new_dataset"],
                steps=[
                    WorkflowStep(
                        id="step-1",
                        name="Metadata Documentation",
                        description="Document dataset metadata",
                        step_type=WorkflowStepType.TASK,
                        assignee_role="data_steward",
                        sla_hours=48
                    ),
                    WorkflowStep(
                        id="step-2",
                        name="Data Classification",
                        description="Classify data sensitivity",
                        step_type=WorkflowStepType.TASK,
                        assignee_role="data_steward",
                        sla_hours=24
                    ),
                    WorkflowStep(
                        id="step-3",
                        name="Quality Rules Setup",
                        description="Define and implement quality rules",
                        step_type=WorkflowStepType.TASK,
                        assignee_role="data_engineer",
                        sla_hours=72
                    ),
                    WorkflowStep(
                        id="step-4",
                        name="Access Control Configuration",
                        description="Configure access controls",
                        step_type=WorkflowStepType.TASK,
                        assignee_role="security_officer",
                        sla_hours=48
                    ),
                    WorkflowStep(
                        id="step-5",
                        name="Privacy Review",
                        description="Review for PII and privacy compliance",
                        step_type=WorkflowStepType.REVIEW,
                        assignee_role="privacy_officer",
                        sla_hours=48
                    ),
                    WorkflowStep(
                        id="step-6",
                        name="Final Approval",
                        description="Data owner approves onboarding",
                        step_type=WorkflowStepType.APPROVAL,
                        assignee_role="data_owner",
                        sla_hours=24
                    )
                ],
                owner="data-governance@resilience.ai",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        for workflow in default_workflows:
            self.create_workflow_definition(workflow)
    
    def create_workflow_definition(self, workflow: WorkflowDefinition):
        """Create a workflow definition"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO workflow_definitions
                (id, name, description, version, applies_to, steps,
                 auto_trigger_conditions, owner, created_at, updated_at, is_active)
                VALUES
                (:id, :name, :description, :version, :applies_to, :steps,
                 :auto_trigger_conditions, :owner, :created_at, :updated_at, :is_active)
                ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                steps = EXCLUDED.steps,
                updated_at = EXCLUDED.updated_at
            """), {
                **workflow.dict(),
                "steps": [s.dict() for s in workflow.steps]
            })
            conn.commit()
    
    def start_workflow(self, definition_id: str, context: Dict[str, Any]) -> str:
        """Start a new workflow instance"""
        # Get workflow definition
        definition = self._get_definition(definition_id)
        if not definition:
            raise ValueError(f"Workflow definition {definition_id} not found")
        
        # Find first step
        first_step = definition.steps[0] if definition.steps else None
        
        instance = WorkflowInstance(
            id=f"wf-instance-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            definition_id=definition_id,
            definition_version=definition.version,
            context=context,
            status=WorkflowStatus.IN_PROGRESS,
            current_step=first_step.id if first_step else None,
            started_at=datetime.utcnow()
        )
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO workflow_instances
                (id, definition_id, definition_version, context, status,
                 current_step, started_at, step_statuses, step_assignees, step_completions)
                VALUES
                (:id, :definition_id, :definition_version, :context, :status,
                 :current_step, :started_at, :step_statuses, :step_assignees, :step_completions)
            """), {
                **instance.dict(),
                "step_statuses": {first_step.id: "pending"} if first_step else {},
                "step_assignees": {},
                "step_completions": {}
            })
            conn.commit()
        
        # Notify assignee
        if first_step:
            self._notify_assignee(instance.id, first_step, context)
        
        return instance.id
    
    def take_action(self, workflow_id: str, step_id: str, action: WorkflowAction):
        """Process an action on a workflow step"""
        instance = self._get_instance(workflow_id)
        if not instance:
            raise ValueError(f"Workflow instance {workflow_id} not found")
        
        definition = self._get_definition(instance.definition_id)
        current_step = next((s for s in definition.steps if s.id == step_id), None)
        
        if not current_step:
            raise ValueError(f"Step {step_id} not found in workflow")
        
        # Record action
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO workflow_actions
                (id, workflow_id, step_id, user_id, user_name, action, comment, timestamp, attachments)
                VALUES
                (:id, :workflow_id, :step_id, :user_id, :user_name, :action, :comment, :timestamp, :attachments)
            """), action.dict())
            conn.commit()
        
        # Update step status
        new_status = "approved" if action.action == "approve" else "rejected" if action.action == "reject" else "completed"
        instance.step_statuses[step_id] = new_status
        instance.step_completions[step_id] = datetime.utcnow()
        
        # Determine next step
        next_step_id = None
        if action.action == "approve":
            next_step_id = current_step.on_approve
        elif action.action == "reject":
            next_step_id = current_step.on_reject
        
        # Update workflow
        if next_step_id:
            instance.current_step = next_step_id
            instance.step_statuses[next_step_id] = "pending"
            
            # Get next step details
            next_step = next((s for s in definition.steps if s.id == next_step_id), None)
            if next_step:
                self._notify_assignee(workflow_id, next_step, instance.context)
        else:
            # Workflow complete
            instance.status = WorkflowStatus.COMPLETED
            instance.completed_at = datetime.utcnow()
            instance.outcome = action.action
        
        # Save instance
        self._update_instance(instance)
        
        return instance
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow"""
        instance = self._get_instance(workflow_id)
        if not instance:
            return None
        
        definition = self._get_definition(instance.definition_id)
        
        # Get action history
        with self.engine.connect() as conn:
            actions = conn.execute(text("""
                SELECT * FROM workflow_actions
                WHERE workflow_id = :workflow_id
                ORDER BY timestamp ASC
            """), {"workflow_id": workflow_id}).fetchall()
        
        return {
            "instance": instance.dict(),
            "definition": {
                "name": definition.name,
                "description": definition.description
            },
            "current_step": next((s.dict() for s in definition.steps if s.id == instance.current_step), None),
            "step_statuses": instance.step_statuses,
            "action_history": [dict(a) for a in actions]
        }
    
    def get_pending_workflows(self, user_id: str = None, role: str = None) -> List[Dict[str, Any]]:
        """Get workflows pending action"""
        with self.engine.connect() as conn:
            query = """
                SELECT wi.*, wd.name as workflow_name
                FROM workflow_instances wi
                JOIN workflow_definitions wd ON wi.definition_id = wd.id
                WHERE wi.status = 'in_progress'
            """
            params = {}
            
            if user_id:
                query += " AND wi.step_assignees->>wi.current_step = :user_id"
                params["user_id"] = user_id
            
            results = conn.execute(text(query), params).fetchall()
        
        return [dict(r) for r in results]
    
    def _get_definition(self, definition_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM workflow_definitions WHERE id = :id
            """), {"id": definition_id}).fetchone()
            
            if result:
                data = dict(result)
                data["steps"] = [WorkflowStep(**s) for s in data["steps"]]
                return WorkflowDefinition(**data)
            return None
    
    def _get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM workflow_instances WHERE id = :id
            """), {"id": instance_id}).fetchone()
            
            if result:
                return WorkflowInstance(**dict(result))
            return None
    
    def _update_instance(self, instance: WorkflowInstance):
        """Update workflow instance"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                UPDATE workflow_instances
                SET status = :status,
                    current_step = :current_step,
                    step_statuses = :step_statuses,
                    step_completions = :step_completions,
                    completed_at = :completed_at,
                    outcome = :outcome
                WHERE id = :id
            """), instance.dict())
            conn.commit()
    
    def _notify_assignee(self, workflow_id: str, step: WorkflowStep, context: Dict[str, Any]):
        """Notify step assignee"""
        # In production, integrate with email/Slack
        print(f"[WORKFLOW NOTIFICATION] Workflow {workflow_id}: Step '{step.name}' assigned to {step.assignee_role}")
```



---

## 12. Tool Selection & Implementation

### 12.1 Recommended Tool Stack

| Component | Primary Tool | Alternative | Purpose |
|-----------|--------------|-------------|---------|
| **Data Catalog** | Apache Atlas / DataHub | Amundsen, Collibra | Metadata management & discovery |
| **Data Lineage** | OpenLineage + Marquez | DataHub Lineage | End-to-end lineage tracking |
| **Data Quality** | Great Expectations | dbt tests, Soda | Data validation & monitoring |
| **Access Control** | OPA (Open Policy Agent) | Apache Ranger | Policy-based access control |
| **Metadata Store** | PostgreSQL + Elasticsearch | Neo4j | Structured & search metadata |
| **Lineage Graph** | Neo4j | Amazon Neptune | Graph-based lineage |
| **Workflow Engine** | Apache Airflow | Prefect, Dagster | Governance workflow orchestration |
| **Monitoring** | Grafana + Prometheus | Datadog | Quality & compliance dashboards |
| **Identity** | Keycloak | Auth0, Okta | Identity & access management |

### 12.2 Tool Implementation Guide

#### Apache Atlas Setup

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/config/atlas-setup.yaml
# Apache Atlas configuration for ResilienceAI

atlas:
  application-properties: |
    # Atlas Configuration
    atlas.graph.storage.backend=hbase
    atlas.graph.storage.hostname=localhost
    atlas.graph.storage.hbase.table=atlas
    
    # Solr Configuration
    atlas.graph.index.search.backend=solr
    atlas.graph.index.search.solr.mode=cloud
    atlas.graph.index.search.solr.zookeeper-url=localhost:2181
    
    # Notification
    atlas.notification.embedded=true
    atlas.kafka.data=${sys:atlas.home}/data/kafka
    atlas.kafka.zookeeper.connect=localhost:2181
    atlas.kafka.bootstrap.servers=localhost:9092
    
    # Hook Notification
    atlas.hook.kafka.sasl.mechanism=PLAIN
    atlas.hook.kafka.security.protocol=SASL_SSL
    
    # Server Properties
    atlas.server.http.port=21000
    atlas.server.https.port=21443
    
    # Authentication
    atlas.authentication.method.kerberos=false
    atlas.authentication.method.ldap=false
    atlas.authentication.method.file=true
  
  # Custom Types for ResilienceAI
  types: |
    {
      "enumDefs": [],
      "structDefs": [],
      "classificationDefs": [
        {
          "name": "PII",
          "description": "Personally Identifiable Information",
          "attributeDefs": []
        },
        {
          "name": "Sensitive",
          "description": "Sensitive data requiring protection",
          "attributeDefs": []
        },
        {
          "name": "Public",
          "description": "Publicly available data",
          "attributeDefs": []
        }
      ],
      "entityDefs": [
        {
          "name": "resilienceai_dataset",
          "superTypes": ["DataSet"],
          "typeVersion": "1.0",
          "attributeDefs": [
            {
              "name": "domain",
              "typeName": "string",
              "isOptional": false
            },
            {
              "name": "qualityScore",
              "typeName": "float",
              "isOptional": true
            },
            {
              "name": "retentionPolicy",
              "typeName": "string",
              "isOptional": true
            },
            {
              "name": "dataSteward",
              "typeName": "string",
              "isOptional": false
            }
          ]
        },
        {
          "name": "resilienceai_incident",
          "superTypes": ["DataSet"],
          "typeVersion": "1.0",
          "attributeDefs": [
            {
              "name": "incidentType",
              "typeName": "string",
              "isOptional": false
            },
            {
              "name": "severity",
              "typeName": "string",
              "isOptional": false
            },
            {
              "name": "location",
              "typeName": "string",
              "isOptional": false
            },
            {
              "name": "occurredAt",
              "typeName": "date",
              "isOptional": false
            }
          ]
        }
      ]
    }
```

#### OpenLineage Configuration

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/config/openlineage.yaml
# OpenLineage configuration for lineage tracking

openlineage:
  # Transport configuration
  transport:
    type: http
    url: http://marquez:5000/api/v1/lineage
    timeout: 5000
    retry_interval: 1000
  
  # Namespace for ResilienceAI
  namespace: resilienceai-prod
  
  # Facets to collect
  facets:
    - schema
    - dataSource
    - documentation
    - ownership
    - quality
  
  # Integration points
  integrations:
    airflow:
      enabled: true
      dag_folder: /opt/airflow/dags
      extractors:
        - BigQueryExtractor
        - PostgresExtractor
        - S3Extractor
    
    dbt:
      enabled: true
      manifest_path: /dbt/target/manifest.json
      run_results_path: /dbt/target/run_results.json
    
    spark:
      enabled: true
      app_name: ResilienceAI-Spark
      extraListeners: io.openlineage.spark.agent.OpenLineageSparkListener
  
  # Custom facets for ResilienceAI
  custom_facets:
    resilienceai:
      - name: dataQuality
        fields:
          - score
          - lastValidated
          - validationRules
      - name: compliance
        fields:
          - classification
          - retentionPolicy
          - piiDetected
      - name: domain
        fields:
          - domainName
          - domainOwner
          - businessUnit
```

#### Great Expectations Configuration

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/config/great_expectations.yml
# Great Expectations configuration

datasources:
  resilienceai_bigquery:
    class_name: Datasource
    execution_engine:
      class_name: SqlAlchemyExecutionEngine
      connection_string: bigquery://resilience-ai-project/dataset
    data_connectors:
      default_inferred_data_connector_name:
        class_name: InferredAssetSqlDataConnector
        include_schema_name: true
      default_runtime_data_connector_name:
        class_name: RuntimeDataConnector
        batch_identifiers:
          - default_identifier_name

  resilienceai_s3:
    class_name: Datasource
    execution_engine:
      class_name: PandasExecutionEngine
    data_connectors:
      default_inferred_data_connector_name:
        class_name: InferredAssetS3DataConnector
        bucket: resilience-ai-data
        default_regex:
          pattern: (.*)/(.*)/(.*)\.parquet
          group_names:
            - domain
            - dataset
            - partition

config_variables_file_path: uncommitted/config_variables.yml

plugins_directory: plugins/

checkpoint_store_name: checkpoint_store
validations_store_name: validations_store
expectations_store_name: expectations_store
evaluation_parameter_store_name: evaluation_parameter_store

stores:
  expectations_store:
    class_name: ExpectationsStore
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: expectations/

  validations_store:
    class_name: ValidationsStore
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: uncommitted/validations/

  checkpoint_store:
    class_name: CheckpointStore
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: checkpoints/

  evaluation_parameter_store:
    class_name: EvaluationParameterStore

expectations_store_name: expectations_store
validations_store_name: validations_store
evaluation_parameter_store_name: evaluation_parameter_store
checkpoint_store_name: checkpoint_store

data_docs_sites:
  local_site:
    class_name: SiteBuilder
    show_how_to_buttons: true
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: uncommitted/data_docs/local_site/
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
  
  s3_site:
    class_name: SiteBuilder
    store_backend:
      class_name: TupleS3StoreBackend
      bucket: resilience-ai-docs
      prefix: data-docs/
    site_index_builder:
      class_name: DefaultSiteIndexBuilder

anonymous_usage_statistics:
  enabled: false
  data_context_id: resilienceai-ge-context
```

#### OPA Policy Configuration

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/config/opa.yaml
# Open Policy Agent configuration

opa:
  services:
    resilienceai:
      url: http://localhost:8181
      credentials:
        bearer:
          token: ${OPA_TOKEN}
  
  bundles:
    resilienceai:
      service: resilienceai
      resource: bundles/resilienceai.tar.gz
      polling:
        min_delay_seconds: 60
        max_delay_seconds: 120
  
  labels:
    app: resilienceai
    environment: production
  
  discovery:
    name: /resilienceai/discovery
    prefix: /bundles
    decision_logs:
      console: true
    
  # Decision logging
  decision_logs:
    console: true
    mask_decision: /system/log/mask
  
  # Status updates
  status:
    console: true
  
  # Default configuration
  default_decision: /resilienceai/dataaccess/allow
  default_authorization_decision: /system/authz/allow
  
  # Logging
  logging:
    level: info
    format: json
    
  # Server configuration
  server:
    addr: :8181
    tls_cert: /certs/opa.crt
    tls_key: /certs/opa.key
    
  # API configuration
  api:
    validate: true
    allow_undefined: false
```

### 12.3 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESILIENCEAI DATA GOVERNANCE                          │
│                              INTEGRATION LAYER                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ BigQuery │  │  S3/Data │  │PostgreSQL│  │  Kafka   │  │   APIs   │      │
│  │          │  │   Lake   │  │          │  │          │  │          │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼────────────┘
        │             │             │             │             │
        └─────────────┴─────────────┴─────────────┴─────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Apache Airflow / Dagster                          │   │
│  │         (Data pipeline orchestration with lineage hooks)             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  DATA CATALOG  │    │  DATA QUALITY  │    │  DATA LINEAGE  │
│  (Apache Atlas │    │  (Great         │    │  (OpenLineage  │
│   / DataHub)   │    │   Expectations) │    │   + Marquez)   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GOVERNANCE SERVICES                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Access    │  │  Retention  │  │ Compliance  │  │ Stewardship │        │
│  │   Control   │  │   Service   │  │   Service   │  │   Service   │        │
│  │    (OPA)    │  │             │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MONITORING & ALERTING                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Grafana + Prometheus + PagerDuty                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Monitoring & Auditing

### 13.1 Monitoring Dashboard Configuration

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/config/grafana-dashboards.yaml
# Grafana dashboard configuration for data governance

apiVersion: 1

providers:
  - name: 'ResilienceAI Governance'
    orgId: 1
    folder: 'Data Governance'
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards/governance

dashboards:
  - title: "Data Quality Overview"
    uid: "resilienceai-quality"
    panels:
      - title: "Overall Quality Score"
        type: stat
        targets:
          - expr: |
              avg(data_quality_score{job="resilienceai"})
        fieldConfig:
          defaults:
            thresholds:
              - color: red
                value: 0
              - color: yellow
                value: 70
              - color: green
                value: 90
      
      - title: "Quality by Domain"
        type: piechart
        targets:
          - expr: |
              avg by (domain) (data_quality_score{job="resilienceai"})
      
      - title: "Failed Quality Checks (24h)"
        type: graph
        targets:
          - expr: |
              sum(increase(quality_check_failures_total[24h]))
      
      - title: "Quality Trends"
        type: graph
        targets:
          - expr: |
              avg_over_time(data_quality_score[1d])

  - title: "Data Catalog Metrics"
    uid: "resilienceai-catalog"
    panels:
      - title: "Total Assets"
        type: stat
        targets:
          - expr: data_catalog_assets_total
      
      - title: "Assets by Classification"
        type: piechart
        targets:
          - expr: data_catalog_assets_by_classification
      
      - title: "Catalog Coverage"
        type: gauge
        targets:
          - expr: data_catalog_coverage_percent
      
      - title: "Recently Added Assets"
        type: table
        targets:
          - expr: data_catalog_recent_assets

  - title: "Compliance Status"
    uid: "resilienceai-compliance"
    panels:
      - title: "Overall Compliance Score"
        type: stat
        targets:
          - expr: compliance_score_overall
      
      - title: "Compliance by Framework"
        type: bar gauge
        targets:
          - expr: compliance_score_by_framework
      
      - title: "Open Issues by Severity"
        type: piechart
        targets:
          - expr: compliance_open_issues
      
      - title: "Pending DSARs"
        type: stat
        targets:
          - expr: dsar_pending_count

  - title: "Access Control"
    uid: "resilienceai-access"
    panels:
      - title: "Access Requests (24h)"
        type: stat
        targets:
          - expr: access_requests_total[24h]
      
      - title: "Access Denials"
        type: graph
        targets:
          - expr: access_denials_total
      
      - title: "Active Sessions"
        type: stat
        targets:
          - expr: active_user_sessions
      
      - title: "Privileged Access"
        type: table
        targets:
          - expr: privileged_access_list

  - title: "Data Stewardship"
    uid: "resilienceai-stewardship"
    panels:
      - title: "Open Tasks"
        type: stat
        targets:
          - expr: stewardship_open_tasks
      
      - title: "SLA Breaches"
        type: stat
        targets:
          - expr: stewardship_sla_breaches
      
      - title: "Issues by Steward"
        type: bar chart
        targets:
          - expr: issues_by_steward
      
      - title: "Resolution Time Trend"
        type: graph
        targets:
          - expr: avg_issue_resolution_time
```

### 13.2 Audit Logging

```python
# /mnt/okcomputer/output/resilience_ai_analysis/src/audit/audit_logger.py

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, text
import json

class AuditLogger:
    """
    Comprehensive audit logging for data governance
    Tracks all governance-related activities
    """
    
    def __init__(self, db_connection: str):
        self.engine = create_engine(db_connection)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize audit tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id BIGSERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    event_type VARCHAR(100),
                    event_category VARCHAR(100),
                    actor_id VARCHAR(255),
                    actor_type VARCHAR(50),
                    action VARCHAR(100),
                    resource_type VARCHAR(100),
                    resource_id VARCHAR(255),
                    resource_name VARCHAR(255),
                    before_state JSON,
                    after_state JSON,
                    change_summary TEXT,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    session_id VARCHAR(255),
                    request_id VARCHAR(255),
                    correlation_id VARCHAR(255),
                    outcome VARCHAR(50),
                    failure_reason TEXT,
                    metadata JSON,
                    retention_class VARCHAR(50)
                )
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
                CREATE INDEX idx_audit_actor ON audit_log(actor_id);
                CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id);
                CREATE INDEX idx_audit_event_type ON audit_log(event_type);
                CREATE INDEX idx_audit_correlation ON audit_log(correlation_id);
            """))
            
            conn.commit()
    
    def log(self,
            event_type: str,
            action: str,
            actor_id: str,
            resource_type: str,
            resource_id: str,
            before_state: Optional[Dict] = None,
            after_state: Optional[Dict] = None,
            event_category: str = "general",
            actor_type: str = "user",
            resource_name: str = None,
            ip_address: str = None,
            user_agent: str = None,
            session_id: str = None,
            request_id: str = None,
            correlation_id: str = None,
            outcome: str = "success",
            failure_reason: str = None,
            metadata: Dict = None,
            retention_class: str = "standard"):
        """Log an audit event"""
        
        # Calculate change summary
        change_summary = self._calculate_change_summary(before_state, after_state)
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO audit_log
                (timestamp, event_type, event_category, actor_id, actor_type, action,
                 resource_type, resource_id, resource_name, before_state, after_state,
                 change_summary, ip_address, user_agent, session_id, request_id,
                 correlation_id, outcome, failure_reason, metadata, retention_class)
                VALUES
                (NOW(), :event_type, :event_category, :actor_id, :actor_type, :action,
                 :resource_type, :resource_id, :resource_name, :before_state, :after_state,
                 :change_summary, :ip_address, :user_agent, :session_id, :request_id,
                 :correlation_id, :outcome, :failure_reason, :metadata, :retention_class)
            """), {
                "event_type": event_type,
                "event_category": event_category,
                "actor_id": actor_id,
                "actor_type": actor_type,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "before_state": json.dumps(before_state) if before_state else None,
                "after_state": json.dumps(after_state) if after_state else None,
                "change_summary": change_summary,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "session_id": session_id,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "outcome": outcome,
                "failure_reason": failure_reason,
                "metadata": json.dumps(metadata) if metadata else None,
                "retention_class": retention_class
            })
            conn.commit()
    
    def _calculate_change_summary(self, before: Dict, after: Dict) -> str:
        """Calculate human-readable change summary"""
        if not before and not after:
            return "No state change"
        
        if not before:
            return f"Created with {len(after)} fields"
        
        if not after:
            return "Deleted"
        
        changes = []
        all_keys = set(before.keys()) | set(after.keys())
        
        for key in all_keys:
            before_val = before.get(key)
            after_val = after.get(key)
            
            if before_val != after_val:
                if key not in before:
                    changes.append(f"+{key}")
                elif key not in after:
                    changes.append(f"-{key}")
                else:
                    changes.append(f"~{key}")
        
        return f"Changes: {', '.join(changes)}" if changes else "No changes"
    
    def query_audit_log(self,
                        start_time: datetime = None,
                        end_time: datetime = None,
                        actor_id: str = None,
                        resource_type: str = None,
                        resource_id: str = None,
                        event_type: str = None,
                        limit: int = 100) -> list:
        """Query audit log with filters"""
        
        conditions = []
        params = {}
        
        if start_time:
            conditions.append("timestamp >= :start_time")
            params["start_time"] = start_time
        
        if end_time:
            conditions.append("timestamp <= :end_time")
            params["end_time"] = end_time
        
        if actor_id:
            conditions.append("actor_id = :actor_id")
            params["actor_id"] = actor_id
        
        if resource_type:
            conditions.append("resource_type = :resource_type")
            params["resource_type"] = resource_type
        
        if resource_id:
            conditions.append("resource_id = :resource_id")
            params["resource_id"] = resource_id
        
        if event_type:
            conditions.append("event_type = :event_type")
            params["event_type"] = event_type
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self.engine.connect() as conn:
            results = conn.execute(text(f"""
                SELECT * FROM audit_log
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT :limit
            """), {**params, "limit": limit}).fetchall()
            
            return [dict(r) for r in results]
    
    def get_user_activity_summary(self, actor_id: str, days: int = 30) -> Dict:
        """Get activity summary for a user"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT 
                    event_type,
                    action,
                    COUNT(*) as count,
                    MAX(timestamp) as last_activity
                FROM audit_log
                WHERE actor_id = :actor_id
                AND timestamp >= NOW() - INTERVAL ':days days'
                GROUP BY event_type, action
                ORDER BY count DESC
            """), {"actor_id": actor_id, "days": days}).fetchall()
            
            total_actions = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM audit_log
                WHERE actor_id = :actor_id
                AND timestamp >= NOW() - INTERVAL ':days days'
            """), {"actor_id": actor_id, "days": days}).fetchone()
        
        return {
            "actor_id": actor_id,
            "period_days": days,
            "total_actions": total_actions.count if total_actions else 0,
            "activity_breakdown": [dict(r) for r in results]
        }

# Pre-configured audit event types
AUDIT_EVENT_TYPES = {
    # Data Access Events
    "DATA_ACCESS": "data_access",
    "DATA_EXPORT": "data_export",
    "DATA_QUERY": "data_query",
    
    # Data Modification Events
    "DATA_CREATE": "data_create",
    "DATA_UPDATE": "data_update",
    "DATA_DELETE": "data_delete",
    
    # Schema Events
    "SCHEMA_CREATE": "schema_create",
    "SCHEMA_ALTER": "schema_alter",
    "SCHEMA_DROP": "schema_drop",
    
    # Governance Events
    "POLICY_CREATE": "policy_create",
    "POLICY_UPDATE": "policy_update",
    "POLICY_DELETE": "policy_delete",
    
    # Access Control Events
    "ACCESS_GRANTED": "access_granted",
    "ACCESS_REVOKED": "access_revoked",
    "ACCESS_REQUESTED": "access_requested",
    
    # Quality Events
    "QUALITY_CHECK": "quality_check",
    "QUALITY_RULE_CREATE": "quality_rule_create",
    "QUALITY_RULE_UPDATE": "quality_rule_update",
    
    # Compliance Events
    "COMPLIANCE_REVIEW": "compliance_review",
    "DSAR_RECEIVED": "dsar_received",
    "DSAR_COMPLETED": "dsar_completed",
    
    # Metadata Events
    "METADATA_UPDATE": "metadata_update",
    "CATALOG_UPDATE": "catalog_update",
    "LINEAGE_UPDATE": "lineage_update"
}
```

---

## 14. Implementation Roadmap

### 14.1 Phase 1: Foundation (Months 1-2)

| Week | Activity | Deliverable | Owner |
|------|----------|-------------|-------|
| 1-2 | Set up governance infrastructure | Infrastructure deployed | Platform Team |
| 1-2 | Deploy data catalog (Apache Atlas) | Catalog accessible | Data Team |
| 2-3 | Implement basic metadata collection | 50% assets cataloged | Data Stewards |
| 3-4 | Set up data quality framework | Quality checks running | Data Quality Team |
| 4-6 | Deploy access control (OPA) | Policies defined | Security Team |
| 5-6 | Create initial data dictionary | Core datasets documented | Data Stewards |
| 6-8 | Implement audit logging | All events logged | Platform Team |

### 14.2 Phase 2: Enhancement (Months 3-4)

| Week | Activity | Deliverable | Owner |
|------|----------|-------------|-------|
| 9-10 | Deploy lineage tracking | Lineage for key pipelines | Data Engineering |
| 10-12 | Implement retention policies | Automated retention active | Data Governance |
| 11-13 | Set up compliance tracking | GDPR/FEMA controls active | Compliance Team |
| 12-14 | Deploy stewardship workflows | Assignment matrix complete | Data Governance |
| 13-15 | Create monitoring dashboards | Governance dashboards live | Platform Team |
| 14-16 | Implement advanced quality rules | Domain-specific rules active | Data Quality Team |

### 14.3 Phase 3: Optimization (Months 5-6)

| Week | Activity | Deliverable | Owner |
|------|----------|-------------|-------|
| 17-18 | Automate data discovery | Auto-cataloging enabled | Data Engineering |
| 18-20 | Implement ML-based quality | Anomaly detection active | Data Science |
| 19-21 | Deploy self-service catalog | User adoption > 70% | Data Governance |
| 20-22 | Optimize performance | < 2s query response | Platform Team |
| 21-24 | Complete compliance certification | Audit passed | Compliance Team |

### 14.4 Implementation Checklist

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/config/implementation-checklist.yaml

phase_1_foundation:
  infrastructure:
    - name: "Deploy PostgreSQL cluster"
      status: pending
      owner: platform-team
    - name: "Deploy Elasticsearch cluster"
      status: pending
      owner: platform-team
    - name: "Deploy Neo4j for lineage"
      status: pending
      owner: platform-team
    - name: "Set up monitoring stack"
      status: pending
      owner: platform-team
  
  data_catalog:
    - name: "Deploy Apache Atlas"
      status: pending
      owner: data-team
    - name: "Define custom types"
      status: pending
      owner: data-stewards
    - name: "Configure data sources"
      status: pending
      owner: data-engineering
    - name: "Catalog 50% of assets"
      status: pending
      owner: data-stewards
  
  data_quality:
    - name: "Deploy Great Expectations"
      status: pending
      owner: data-quality-team
    - name: "Define core quality rules"
      status: pending
      owner: data-stewards
    - name: "Set up quality dashboards"
      status: pending
      owner: data-quality-team
    - name: "Configure quality alerts"
      status: pending
      owner: data-quality-team
  
  access_control:
    - name: "Deploy OPA"
      status: pending
      owner: security-team
    - name: "Define access policies"
      status: pending
      owner: security-team
    - name: "Integrate with identity provider"
      status: pending
      owner: security-team
    - name: "Test access workflows"
      status: pending
      owner: security-team

phase_2_enhancement:
  lineage:
    - name: "Deploy OpenLineage"
      status: pending
      owner: data-engineering
    - name: "Deploy Marquez"
      status: pending
      owner: data-engineering
    - name: "Configure pipeline hooks"
      status: pending
      owner: data-engineering
    - name: "Validate lineage accuracy"
      status: pending
      owner: data-stewards
  
  retention:
    - name: "Define retention policies"
      status: pending
      owner: data-governance
    - name: "Implement retention service"
      status: pending
      owner: data-engineering
    - name: "Configure legal hold process"
      status: pending
      owner: legal-team
    - name: "Test retention workflows"
      status: pending
      owner: data-governance
  
  compliance:
    - name: "Map regulatory requirements"
      status: pending
      owner: compliance-team
    - name: "Define compliance controls"
      status: pending
      owner: compliance-team
    - name: "Implement DSAR workflow"
      status: pending
      owner: privacy-officer
    - name: "Set up compliance reporting"
      status: pending
      owner: compliance-team

phase_3_optimization:
  automation:
    - name: "Implement auto-discovery"
      status: pending
      owner: data-engineering
    - name: "Deploy ML-based quality"
      status: pending
      owner: data-science
    - name: "Automate metadata extraction"
      status: pending
      owner: data-engineering
  
  self_service:
    - name: "Enhance catalog UI"
      status: pending
      owner: frontend-team
    - name: "Implement data marketplace"
      status: pending
      owner: data-governance
    - name: "Create user documentation"
      status: pending
      owner: technical-writers
  
  certification:
    - name: "Internal audit"
      status: pending
      owner: compliance-team
    - name: "External audit preparation"
      status: pending
      owner: compliance-team
    - name: "Certification achieved"
      status: pending
      owner: compliance-team
```

### 14.5 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Catalog Coverage** | 100% of production datasets | Monthly scan |
| **Data Quality Score** | > 95% overall | Daily calculation |
| **Access Request SLA** | < 48 hours average | Weekly report |
| **Issue Resolution Time** | < 72 hours for high priority | Weekly report |
| **Compliance Score** | > 98% for all frameworks | Monthly assessment |
| **User Adoption** | > 80% of data users | Quarterly survey |
| **Audit Coverage** | 100% of governance events | Real-time |
| **SLA Breaches** | < 2 per month | Monthly report |

### 14.6 Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low user adoption | High | Early stakeholder engagement, training programs |
| Performance issues | Medium | Load testing, horizontal scaling |
| Integration complexity | High | Phased rollout, dedicated integration team |
| Data quality gaps | High | Incremental rule deployment, steward training |
| Compliance violations | Critical | Regular audits, automated compliance checks |
| Tool vendor changes | Low | Open source preference, abstraction layers |

---

## Appendix A: Configuration Files

### A.1 Docker Compose for Governance Stack

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/docker/docker-compose.governance.yml

version: '3.8'

services:
  # PostgreSQL for metadata storage
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: governance
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: governance
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  # Elasticsearch for catalog search
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
  
  # Neo4j for lineage
  neo4j:
    image: neo4j:5.14
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc", "gds"]'
    volumes:
      - neo4j_data:/data
    ports:
      - "7474:7474"
      - "7687:7687"
  
  # Apache Atlas
  atlas:
    image: apache/atlas:2.3.0
    environment:
      - ATLAS_PROVISION_EXAMPLES=false
    ports:
      - "21000:21000"
    depends_on:
      - postgres
      - elasticsearch
  
  # Marquez for lineage
  marquez:
    image: marquezproject/marquez:0.47.0
    ports:
      - "5000:5000"
      - "5001:5001"
    environment:
      - MARQUEZ_DB=postgres
      - MARQUEZ_DB_HOST=postgres
      - MARQUEZ_DB_PORT=5432
      - MARQUEZ_DB_NAME=marquez
      - MARQUEZ_DB_USER=marquez
      - MARQUEZ_DB_PASSWORD=${MARQUEZ_PASSWORD}
  
  # OPA for access control
  opa:
    image: openpolicyagent/opa:0.60.0
    command: "run --server --addr :8181 /policies"
    volumes:
      - ./policies:/policies:ro
    ports:
      - "8181:8181"
  
  # Grafana for monitoring
  grafana:
    image: grafana/grafana:10.2.0
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
  
  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:v2.48.0
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
  
  # Governance API
  governance-api:
    build:
      context: ../src
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://governance:${POSTGRES_PASSWORD}@postgres:5432/governance
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - NEO4J_URL=bolt://neo4j:7687
      - OPA_URL=http://opa:8181
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - elasticsearch
      - neo4j
      - opa

volumes:
  postgres_data:
  elasticsearch_data:
  neo4j_data:
  grafana_data:
  prometheus_data:
```

### A.2 Kubernetes Deployment

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/k8s/governance-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: governance-api
  namespace: data-governance
spec:
  replicas: 3
  selector:
    matchLabels:
      app: governance-api
  template:
    metadata:
      labels:
        app: governance-api
    spec:
      containers:
      - name: api
        image: resilienceai/governance-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: governance-secrets
              key: database-url
        - name: ELASTICSEARCH_URL
          value: "http://elasticsearch:9200"
        - name: NEO4J_URL
          value: "bolt://neo4j:7687"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: governance-api
  namespace: data-governance
spec:
  selector:
    app: governance-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: governance-api
  namespace: data-governance
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  tls:
  - hosts:
    - governance.resilience.ai
    secretName: governance-tls
  rules:
  - host: governance.resilience.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: governance-api
            port:
              number: 80
```

---

## Summary

This comprehensive data governance framework for ResilienceAI provides:

1. **Data Catalog** - Centralized metadata management with search and discovery
2. **Data Lineage** - End-to-end tracking of data flow using graph database
3. **Data Dictionary** - Business and technical definitions with stewardship
4. **Metadata Management** - Unified technical, business, and operational metadata
5. **Data Quality** - Rule-based validation with Great Expectations integration
6. **Access Control** - Policy-based access using OPA with RBAC and ABAC
7. **Retention Policies** - Automated lifecycle management with legal hold support
8. **Compliance Tracking** - GDPR, FEMA, and other regulatory framework support
9. **Data Stewardship** - Role-based stewardship with task and issue management
10. **Governance Workflows** - Approval and review workflows for governance processes

The implementation follows a phased approach over 6 months, with clear deliverables, ownership, and success metrics for each phase.

---

*Document Version: 1.0*
*Last Updated: January 2024*
*Author: ResilienceAI Data Governance Team*
