# ResilienceAI Database Architecture Enhancement

## Executive Summary

This document provides a comprehensive database architecture design for ResilienceAI, transitioning from CSV-based storage to a robust, scalable multi-database architecture. The proposed solution handles 3,222 counties × 66 features with support for real-time analytics, geospatial queries, vector similarity search, and time-series forecasting.

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Proposed Architecture Overview](#2-proposed-architecture-overview)
3. [PostgreSQL/PostGIS Schema Design](#3-postgresqlpostgis-schema-design)
4. [TimescaleDB Time-Series Schema](#4-timescaledb-time-series-schema)
5. [Vector Database Design (Pinecone/Weaviate)](#5-vector-database-design)
6. [Redis Caching Strategy](#6-redis-caching-strategy)
7. [Data Warehouse (BigQuery)](#7-data-warehouse-bigquery)
8. [Indexing and Partitioning Strategies](#8-indexing-and-partitioning-strategies)
9. [Connection Pooling](#9-connection-pooling)
10. [Backup and Recovery](#10-backup-and-recovery)
11. [Data Retention Policies](#11-data-retention-policies)
12. [Migration Strategy](#12-migration-strategy)
13. [Implementation Priority](#13-implementation-priority)

---

## 1. Current State Analysis

### 1.1 Existing Data Storage Patterns

```
ResilienceAI Current Architecture:
├── data/
│   ├── processed/
│   │   └── county_features.csv      # 3,222 counties × 66 features
│   ├── dashboard_activity.log       # Activity logs
│   └── improvement_log.json         # Self-improvement tracking
├── src/
│   ├── vector_space.py              # FAISS vector indexing (384-dim)
│   ├── alert_manager.py             # SQLite for alerts
│   ├── predictive_models.py         # Time-series forecasting
│   └── realtime_pipeline.py         # WebSocket events
└── models/                          # Trained ML models
```

### 1.2 Data Characteristics

| Aspect | Current | Projected Growth |
|--------|---------|------------------|
| Counties | 3,222 | 3,222 (static) |
| Features | 66 | 100+ (expanding) |
| Historical Years | 20+ | 50+ |
| Vector Dimensions | 384 | 768-1536 |
| Real-time Events | 100/day | 10,000/day |
| Alert Subscriptions | 1,000 | 100,000+ |

### 1.3 Identified Limitations

1. **CSV-based storage**: No concurrent access, slow queries
2. **In-memory FAISS**: No persistence, limited scalability
3. **SQLite alerts**: Single-writer bottleneck
4. **No data versioning**: Cannot track feature changes over time
5. **Limited geospatial queries**: No spatial indexing
6. **No caching layer**: Repeated expensive computations

---

## 2. Proposed Architecture Overview

### 2.1 Multi-Database Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ResilienceAI Database Architecture                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   PostgreSQL │  │  TimescaleDB │  │   Pinecone   │  │    Redis     │    │
│  │   + PostGIS  │  │  (Time-Series)│  │   (Vectors)  │  │   (Cache)    │    │
│  │              │  │              │  │              │  │              │    │
│  │ • Counties   │  │ • Historical │  │ • County     │  │ • Hot data   │    │
│  │ • Features   │  │   metrics    │  │   embeddings │  │ • Sessions   │    │
│  │ • Geospatial │  │ • Forecasts  │  │ • Similarity │  │ • Rate limit │    │
│  │ • Alerts     │  │ • Events     │  │   search     │  │ • Pub/Sub    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         └─────────────────┴─────────────────┴─────────────────┘             │
│                                   │                                         │
│                         ┌─────────┴─────────┐                               │
│                         │  Connection Pool  │                               │
│                         │    (PgBouncer)    │                               │
│                         └─────────┬─────────┘                               │
│                                   │                                         │
│  ┌────────────────────────────────┼────────────────────────────────┐       │
│  │                    Application Layer                              │       │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │       │
│  │  │ Dashboard│ │  Agents  │ │  Alerts  │ │  Vector  │ │Predict │ │       │
│  │  │   API    │ │Orchestr. │ │  Manager │ │  Search  │ │ Models │ │       │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                   │                                         │
│                         ┌─────────┴─────────┐                               │
│                         │   Data Warehouse   │                              │
│                         │    (BigQuery)      │                              │
│                         │                    │                              │
│                         │ • Analytics        │                              │
│                         │ • ML Training      │                              │
│                         │ • Reporting        │                              │
│                         └────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Database Selection Rationale

| Database | Purpose | Why Selected |
|----------|---------|--------------|
| PostgreSQL + PostGIS | Primary datastore, geospatial | ACID compliance, mature, excellent geospatial support |
| TimescaleDB | Time-series data | PostgreSQL extension, hypertables, continuous aggregates |
| Pinecone | Vector similarity search | Managed service, high performance, metadata filtering |
| Redis | Caching, sessions, pub/sub | Sub-millisecond latency, versatile data structures |
| BigQuery | Data warehouse, analytics | Serverless, petabyte-scale, ML integration |

---

## 3. PostgreSQL/PostGIS Schema Design

### 3.1 Core Schema Overview

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS btree_gist;   -- For GiST indexes
CREATE EXTENSION IF NOT EXISTS uuid-ossp;    -- For UUID generation
```

### 3.2 Counties Table (Geospatial Core)

```sql
-- File: /mnt/okcomputer/output/resilience_ai_analysis/sql/01_counties_schema.sql

CREATE TABLE counties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fips_code VARCHAR(5) UNIQUE NOT NULL,           -- 5-digit FIPS (State + County)
    state_fips VARCHAR(2) NOT NULL,                  -- 2-digit State FIPS
    county_fips VARCHAR(3) NOT NULL,                 -- 3-digit County FIPS
    state_name VARCHAR(100) NOT NULL,
    state_abbrev VARCHAR(2) NOT NULL,
    county_name VARCHAR(200) NOT NULL,
    
    -- Geospatial data
    centroid GEOMETRY(POINT, 4326) NOT NULL,         -- County centroid
    boundary GEOMETRY(MULTIPOLYGON, 4326),           -- County boundary
    bounding_box GEOMETRY(POLYGON, 4326),            -- For quick intersection tests
    
    -- Derived metrics (cached for performance)
    area_sq_km DECIMAL(12, 4),
    population INTEGER,
    population_density DECIMAL(10, 4),
    
    -- Metadata
    data_quality_score DECIMAL(3, 2) DEFAULT 1.0,    -- 0.0 to 1.0
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_fips CHECK (LENGTH(fips_code) = 5),
    CONSTRAINT valid_state_abbrev CHECK (LENGTH(state_abbrev) = 2)
);

-- Geospatial indexes
CREATE INDEX idx_counties_centroid ON counties USING GIST(centroid);
CREATE INDEX idx_counties_boundary ON counties USING GIST(boundary);
CREATE INDEX idx_counties_bounding_box ON counties USING GIST(bounding_box);

-- Standard indexes
CREATE INDEX idx_counties_fips ON counties(fips_code);
CREATE INDEX idx_counties_state ON counties(state_abbrev);
CREATE INDEX idx_counties_state_fips ON counties(state_fips);
CREATE INDEX idx_counties_name_trgm ON counties USING GIN(county_name gin_trgm_ops);

-- Composite index for common queries
CREATE INDEX idx_counties_state_population ON counties(state_abbrev, population DESC);
```

### 3.3 Features Tables (Normalized Design)

```sql
-- File: /mnt/okcomputer/output/resilience_ai_analysis/sql/02_features_schema.sql

-- Feature categories lookup
CREATE TABLE feature_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    domain VARCHAR(20) NOT NULL CHECK (domain IN ('climate', 'health', 'infrastructure', 'socioeconomic', 'agriculture')),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual feature definitions
CREATE TABLE feature_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feature_key VARCHAR(100) UNIQUE NOT NULL,        -- Machine name (e.g., 'disaster_count')
    display_name VARCHAR(200) NOT NULL,               -- Human-readable name
    description TEXT,
    category_id INTEGER REFERENCES feature_categories(id),
    
    -- Data type and units
    data_type VARCHAR(20) NOT NULL CHECK (data_type IN ('integer', 'float', 'percentage', 'count', 'distance', 'currency')),
    unit VARCHAR(50),                                  -- e.g., 'km', '%', 'USD'
    precision_digits INTEGER DEFAULT 2,               -- Decimal places for display
    
    -- Value ranges for validation
    min_value DECIMAL(20, 8),
    max_value DECIMAL(20, 8),
    
    -- Source tracking
    data_source VARCHAR(100),                          -- e.g., 'FEMA', 'CDC', 'Census'
    source_url TEXT,
    update_frequency VARCHAR(20),                      -- 'daily', 'weekly', 'monthly', 'yearly'
    
    -- Metadata
    is_calculated BOOLEAN DEFAULT FALSE,              -- Derived from other features?
    calculation_formula TEXT,                          -- If calculated, store formula
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- County feature values (current snapshot)
CREATE TABLE county_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    county_id UUID NOT NULL REFERENCES counties(id) ON DELETE CASCADE,
    feature_id UUID NOT NULL REFERENCES feature_definitions(id) ON DELETE CASCADE,
    
    -- Value storage (flexible for different types)
    numeric_value DECIMAL(20, 8),
    text_value TEXT,
    json_value JSONB,
    
    -- Data quality
    confidence_score DECIMAL(3, 2) DEFAULT 1.0,       -- 0.0 to 1.0
    data_quality_flags TEXT[],                        -- Array of quality issues
    
    -- Timestamps
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_county_feature_date UNIQUE (county_id, feature_id, effective_date),
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Indexes for county features
CREATE INDEX idx_county_features_county ON county_features(county_id);
CREATE INDEX idx_county_features_feature ON county_features(feature_id);
CREATE INDEX idx_county_features_date ON county_features(effective_date);
CREATE INDEX idx_county_features_value ON county_features(numeric_value) WHERE numeric_value IS NOT NULL;
CREATE INDEX idx_county_features_json ON county_features USING GIN(json_value);

-- Composite index for common query pattern
CREATE INDEX idx_county_features_county_feature ON county_features(county_id, feature_id, effective_date DESC);
```

### 3.4 Alert Management Tables

```sql
-- File: /mnt/okcomputer/output/resilience_ai_analysis/sql/03_alerts_schema.sql

-- Alert types and severities
CREATE TYPE alert_severity AS ENUM ('info', 'low', 'medium', 'high', 'critical');
CREATE TYPE alert_status AS ENUM ('active', 'acknowledged', 'resolved', 'dismissed');
CREATE TYPE alert_type AS ENUM (
    'weather_warning', 'disaster_declaration', 'risk_threshold', 
    'infrastructure_failure', 'health_emergency', 'agricultural_threat'
);

-- Alert subscriptions
CREATE TABLE alert_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    county_id UUID NOT NULL REFERENCES counties(id) ON DELETE CASCADE,
    
    -- Subscription configuration
    alert_types alert_type[] NOT NULL,
    severity_threshold alert_severity DEFAULT 'medium',
    risk_threshold DECIMAL(5, 4),                     -- Trigger when risk score exceeds
    
    -- Notification channels
    email VARCHAR(255),
    phone VARCHAR(20),
    webhook_url TEXT,
    slack_channel VARCHAR(100),
    
    -- Metadata
    subscription_name VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),                          -- User or system identifier
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_triggered TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0
);

-- Alert events
CREATE TABLE alert_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID REFERENCES alert_subscriptions(id) ON DELETE SET NULL,
    county_id UUID NOT NULL REFERENCES counties(id) ON DELETE CASCADE,
    
    -- Alert details
    alert_type alert_type NOT NULL,
    severity alert_severity NOT NULL,
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    
    -- Associated data
    risk_score DECIMAL(5, 4),
    affected_features UUID[],                         -- Related feature IDs
    source_data JSONB,                                -- Original triggering data
    
    -- Status tracking
    status alert_status DEFAULT 'active',
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    
    -- Geospatial impact (if applicable)
    impact_area GEOMETRY(POLYGON, 4326),
    
    -- Timestamps
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,              -- Auto-expire old alerts
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alert delivery log
CREATE TABLE alert_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_event_id UUID NOT NULL REFERENCES alert_events(id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL,                      -- 'email', 'sms', 'webhook', 'slack'
    recipient TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,                       -- 'pending', 'sent', 'delivered', 'failed'
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_alert_subscriptions_county ON alert_subscriptions(county_id);
CREATE INDEX idx_alert_subscriptions_active ON alert_subscriptions(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_alert_events_county ON alert_events(county_id);
CREATE INDEX idx_alert_events_status ON alert_events(status);
CREATE INDEX idx_alert_events_triggered ON alert_events(triggered_at DESC);
CREATE INDEX idx_alert_events_expires ON alert_events(expires_at);
CREATE INDEX idx_alert_deliveries_alert ON alert_deliveries(alert_event_id);
```

### 3.5 Infrastructure and Health Facilities

```sql
-- File: /mnt/okcomputer/output/resilience_ai_analysis/sql/04_facilities_schema.sql

CREATE TYPE facility_type AS ENUM ('hospital', 'clinic', 'nursing_home', 'fire_station', 'ems_station', 'pharmacy');

CREATE TABLE facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100),                          -- ID from source system
    facility_type facility_type NOT NULL,
    
    -- Basic info
    name VARCHAR(500) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    county_id UUID REFERENCES counties(id),
    
    -- Geospatial
    location GEOMETRY(POINT, 4326) NOT NULL,
    
    -- Facility-specific attributes (JSONB for flexibility)
    attributes JSONB DEFAULT '{}',
    
    -- For hospitals
    bed_count INTEGER,
    trauma_level INTEGER,                              -- 1-5 for trauma centers
    emergency_services BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(100),
    
    -- Timestamps
    last_verified TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Facility service areas (for coverage analysis)
CREATE TABLE facility_service_areas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    service_area GEOMETRY(POLYGON, 4326) NOT NULL,
    travel_time_minutes INTEGER,                       -- Drive time to boundary
    population_served INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_facilities_location ON facilities USING GIST(location);
CREATE INDEX idx_facilities_type ON facilities(facility_type);
CREATE INDEX idx_facilities_county ON facilities(county_id);
CREATE INDEX idx_facilities_active ON facilities(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_facilities_attributes ON facilities USING GIN(attributes);
CREATE INDEX idx_facility_service_areas ON facility_service_areas USING GIST(service_area);
```

---

## 4. TimescaleDB Time-Series Schema

### 4.1 Historical County Metrics

```sql
-- File: /mnt/okcomputer/output/resilience_ai_analysis/sql/05_timescale_schema.sql

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Historical feature values (time-series)
CREATE TABLE county_metrics_history (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    county_id UUID NOT NULL REFERENCES counties(id),
    feature_id UUID NOT NULL REFERENCES feature_definitions(id),
    
    -- Value
    value DECIMAL(20, 8) NOT NULL,
    value_type VARCHAR(20) DEFAULT 'measured',        -- 'measured', 'interpolated', 'forecasted'
    
    -- Data quality
    confidence DECIMAL(3, 2) DEFAULT 1.0,
    data_source VARCHAR(100),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Convert to hypertable (partitioned by time)
SELECT create_hypertable('county_metrics_history', 'time', 
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- Create continuous aggregates for common time ranges
CREATE MATERIALIZED VIEW county_metrics_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS bucket,
    county_id,
    feature_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count
FROM county_metrics_history
GROUP BY bucket, county_id, feature_id
WITH NO DATA;

CREATE MATERIALIZED VIEW county_metrics_monthly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 month', time) AS bucket,
    county_id,
    feature_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count
FROM county_metrics_history
GROUP BY bucket, county_id, feature_id
WITH NO DATA;

-- Add retention policy (keep raw data for 2 years, aggregates forever)
SELECT add_retention_policy('county_metrics_history', INTERVAL '2 years');

-- Indexes
CREATE INDEX idx_county_metrics_history_county ON county_metrics_history(county_id, time DESC);
CREATE INDEX idx_county_metrics_history_feature ON county_metrics_history(feature_id, time DESC);
```

### 4.2 Real-Time Events

```sql
-- Real-time event stream
CREATE TABLE realtime_events (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    event_id UUID DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,                   -- 'weather_alert', 'disaster_declaration', etc.
    source VARCHAR(50) NOT NULL,                       -- 'NOAA', 'FEMA', 'USGS'
    
    -- Location
    county_id UUID REFERENCES counties(id),
    location GEOMETRY(POINT, 4326),
    
    -- Event data
    severity VARCHAR(20),
    title TEXT,
    description TEXT,
    raw_data JSONB,
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processing_timestamp TIMESTAMP WITH TIME ZONE
);

-- Convert to hypertable
SELECT create_hypertable('realtime_events', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Retention: Keep events for 90 days
SELECT add_retention_policy('realtime_events', INTERVAL '90 days');

-- Indexes
CREATE INDEX idx_realtime_events_type ON realtime_events(event_type, time DESC);
CREATE INDEX idx_realtime_events_county ON realtime_events(county_id, time DESC);
CREATE INDEX idx_realtime_events_unprocessed ON realtime_events(processed) WHERE processed = FALSE;
CREATE INDEX idx_realtime_events_location ON realtime_events USING GIST(location);
```

### 4.3 Forecasts and Predictions

```sql
-- Model predictions and forecasts
CREATE TABLE predictions (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    county_id UUID NOT NULL REFERENCES counties(id),
    model_id VARCHAR(100) NOT NULL,                    -- Identifier for the model used
    
    -- Prediction details
    prediction_type VARCHAR(50),                       -- 'risk_score', 'disaster_probability', etc.
    target_date DATE,                                  -- What date is this prediction for?
    
    -- Values
    predicted_value DECIMAL(20, 8),
    confidence_lower DECIMAL(20, 8),                   -- Lower bound of confidence interval
    confidence_upper DECIMAL(20, 8),                   -- Upper bound
    confidence_level DECIMAL(3, 2) DEFAULT 0.95,       -- e.g., 0.95 for 95% CI
    
    -- Model metadata
    model_version VARCHAR(50),
    feature_importance JSONB,                          -- Which features contributed most
    
    -- Validation (filled in later when actual values known)
    actual_value DECIMAL(20, 8),
    prediction_error DECIMAL(20, 8),
    validated_at TIMESTAMP WITH TIME ZONE
);

-- Convert to hypertable
SELECT create_hypertable('predictions', 'time',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

-- Indexes
CREATE INDEX idx_predictions_county ON predictions(county_id, time DESC);
CREATE INDEX idx_predictions_model ON predictions(model_id, time DESC);
CREATE INDEX idx_predictions_target ON predictions(target_date);
CREATE INDEX idx_predictions_unvalidated ON predictions(validated_at) WHERE validated_at IS NULL;
```

---

## 5. Vector Database Design

### 5.1 Pinecone Schema

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/python/vector_db_pinecone.py

"""
Pinecone Vector Database Integration for ResilienceAI
Manages county embeddings for similarity search and clustering.
"""

import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from pinecone import Pinecone, ServerlessSpec

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
INDEX_NAME = "resilienceai-counties"
VECTOR_DIMENSION = 384  # Matches sentence-transformers 'all-MiniLM-L6-v2'


@dataclass
class CountyVector:
    """Represents a county's vector embedding with metadata"""
    id: str                          # county_fips
    values: List[float]              # Embedding vector
    metadata: Dict                   # Associated metadata
    
    
class PineconeVectorStore:
    """Vector database operations for county embeddings"""
    
    def __init__(self, index_name: str = INDEX_NAME):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index_name = index_name
        self.index = self._get_or_create_index()
        
    def _get_or_create_index(self):
        """Get existing index or create new one"""
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=VECTOR_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=PINECONE_ENVIRONMENT
                )
            )
        return self.pc.Index(self.index_name)
    
    def upsert_counties(self, counties: List[CountyVector], namespace: str = ""):
        """Upsert county vectors in batches"""
        vectors = [
            {
                "id": c.id,
                "values": c.values,
                "metadata": c.metadata
            }
            for c in counties
        ]
        
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch, namespace=namespace)
    
    def search_similar(
        self, 
        query_vector: List[float], 
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: str = ""
    ) -> List[Dict]:
        """Search for similar counties"""
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict,
            namespace=namespace
        )
        return results.matches
    
    def search_by_county_fips(
        self, 
        county_fips: str, 
        top_k: int = 10,
        namespace: str = ""
    ) -> List[Dict]:
        """Find counties similar to a given county"""
        # Fetch the vector for the reference county
        result = self.index.fetch(ids=[county_fips], namespace=namespace)
        if county_fips not in result.vectors:
            return []
        
        vector = result.vectors[county_fips].values
        return self.search_similar(vector, top_k=top_k, namespace=namespace)
    
    def delete_county(self, county_fips: str, namespace: str = ""):
        """Delete a county's vector"""
        self.index.delete(ids=[county_fips], namespace=namespace)
    
    def get_namespace_stats(self, namespace: str = "") -> Dict:
        """Get statistics for a namespace"""
        stats = self.index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension
        }


# Domain-specific namespaces
NAMESPACES = {
    "climate": "Climate vulnerability embeddings",
    "health": "Health infrastructure embeddings",
    "infrastructure": "Infrastructure resilience embeddings",
    "socioeconomic": "Socioeconomic vulnerability embeddings",
    "agriculture": "Agricultural vulnerability embeddings",
    "comprehensive": "All-domain combined embeddings"
}
```

### 5.2 Weaviate Alternative Schema

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/python/vector_db_weaviate.py

"""
Weaviate Vector Database Integration (Alternative to Pinecone)
Self-hosted option with more flexibility.
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from typing import List, Dict, Optional
import os

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")


class WeaviateVectorStore:
    """Weaviate-based vector store for county embeddings"""
    
    def __init__(self):
        self.client = weaviate.connect_to_wcs(
            cluster_url=WEAVIATE_URL,
            auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY) if WEAVIATE_API_KEY else None
        )
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create County collection if it doesn't exist"""
        if not self.client.collections.exists("County"):
            self.client.collections.create(
                name="County",
                vectorizer_config=Configure.Vectorizer.none(),  # We'll provide vectors
                properties=[
                    Property(name="fips_code", data_type=DataType.TEXT),
                    Property(name="county_name", data_type=DataType.TEXT),
                    Property(name="state", data_type=DataType.TEXT),
                    Property(name="population", data_type=DataType.INT),
                    Property(name="risk_score", data_type=DataType.NUMBER),
                    Property(name="domain", data_type=DataType.TEXT),  # climate, health, etc.
                    Property(name="features", data_type=DataType.OBJECT),
                ]
            )
    
    def upsert_county(self, county_data: Dict, vector: List[float]):
        """Add or update a county with its vector"""
        collection = self.client.collections.get("County")
        collection.data.insert(
            properties=county_data,
            vector=vector
        )
    
    def search_similar(
        self, 
        query_vector: List[float], 
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar counties"""
        collection = self.client.collections.get("County")
        
        query = collection.query.near_vector(
            near_vector=query_vector,
            limit=limit,
            return_metadata=["distance", "certainty"]
        )
        
        return [
            {
                "id": obj.uuid,
                "properties": obj.properties,
                "distance": obj.metadata.distance,
                "certainty": obj.metadata.certainty
            }
            for obj in query.objects
        ]
```

---

## 6. Redis Caching Strategy

### 6.1 Cache Configuration

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/python/redis_cache.py

"""
Redis Caching Layer for ResilienceAI
Implements multi-tier caching strategy.
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
import redis
from redis.connection import ConnectionPool
import os

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Cache TTL configurations (in seconds)
CACHE_TTL = {
    "county_features": 300,           # 5 minutes
    "county_list": 600,               # 10 minutes
    "vector_search": 60,              # 1 minute
    "predictions": 180,               # 3 minutes
    "dashboard_data": 30,             # 30 seconds
    "aggregations": 120,              # 2 minutes
    "geospatial": 300,                # 5 minutes
    "alerts": 60,                     # 1 minute
    "sessions": 3600,                 # 1 hour
    "rate_limits": 60,                # 1 minute
}


class ResilienceCache:
    """Redis cache manager with tiered caching"""
    
    def __init__(self):
        self.pool = ConnectionPool.from_url(REDIS_URL)
        self.redis = redis.Redis(connection_pool=self.pool)
        
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = f"{prefix}:{json.dumps(args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.redis.get(key)
        if value is None:
            return None
        return pickle.loads(value)
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL"""
        serialized = pickle.dumps(value)
        self.redis.setex(key, ttl, serialized)
    
    def delete(self, key: str):
        """Delete key from cache"""
        self.redis.delete(key)
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)
    
    def cached(self, prefix: str, ttl: Optional[int] = None):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self._generate_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache_ttl = ttl or CACHE_TTL.get(prefix, 300)
                self.set(cache_key, result, cache_ttl)
                
                return result
            return wrapper
        return decorator
    
    # Specific cache operations
    
    def cache_county_features(self, fips: str, features: Dict):
        """Cache county features"""
        key = f"county:features:{fips}"
        self.set(key, features, CACHE_TTL["county_features"])
    
    def get_cached_county_features(self, fips: str) -> Optional[Dict]:
        """Get cached county features"""
        return self.get(f"county:features:{fips}")
    
    def invalidate_county(self, fips: str):
        """Invalidate all cache entries for a county"""
        self.delete_pattern(f"county:*:{fips}")
    
    # Rate limiting
    
    def check_rate_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is within rate limit"""
        current = self.redis.get(key)
        if current is None:
            self.redis.setex(key, window, 1)
            return True
        
        count = int(current)
        if count >= limit:
            return False
        
        self.redis.incr(key)
        return True
    
    # Pub/Sub for real-time updates
    
    def publish_alert(self, channel: str, message: Dict):
        """Publish alert to subscribers"""
        self.redis.publish(channel, json.dumps(message))
    
    def subscribe_alerts(self, channels: list, callback: Callable):
        """Subscribe to alert channels"""
        pubsub = self.redis.pubsub()
        pubsub.subscribe(*channels)
        
        for message in pubsub.listen():
            if message["type"] == "message":
                callback(json.loads(message["data"]))


# Global cache instance
cache = ResilienceCache()
```

### 6.2 Session and Rate Limiting

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/python/redis_sessions.py

"""
Session management and rate limiting with Redis
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from redis_cache import cache, CACHE_TTL


class SessionManager:
    """User session management"""
    
    def create_session(self, user_id: str, metadata: Optional[Dict] = None) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        key = f"session:{session_id}"
        cache.set(key, session_data, CACHE_TTL["sessions"])
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        key = f"session:{session_id}"
        session = cache.get(key)
        
        if session:
            # Update last accessed
            session["last_accessed"] = datetime.utcnow().isoformat()
            cache.set(key, session, CACHE_TTL["sessions"])
        
        return session
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        cache.delete(f"session:{session_id}")


class RateLimiter:
    """API rate limiting"""
    
    def __init__(self):
        self.limits = {
            "anonymous": (100, 3600),      # 100 requests/hour
            "authenticated": (1000, 3600), # 1000 requests/hour
            "premium": (10000, 3600),      # 10000 requests/hour
        }
    
    def is_allowed(self, identifier: str, tier: str = "anonymous") -> bool:
        """Check if request is allowed"""
        limit, window = self.limits.get(tier, self.limits["anonymous"])
        key = f"rate_limit:{tier}:{identifier}"
        return cache.check_rate_limit(key, limit, window)
    
    def get_remaining(self, identifier: str, tier: str = "anonymous") -> int:
        """Get remaining requests in window"""
        limit, _ = self.limits.get(tier, self.limits["anonymous"])
        key = f"rate_limit:{tier}:{identifier}"
        current = cache.redis.get(key)
        
        if current is None:
            return limit
        
        return max(0, limit - int(current))
```

---

## 7. Data Warehouse (BigQuery)

### 7.1 BigQuery Schema

```sql
-- File: /mnt/okcomputer/output/resilience_ai_analysis/sql/06_bigquery_schema.sql

-- Dataset: resilienceai_analytics

-- Counties dimension table
CREATE OR REPLACE TABLE resilienceai_analytics.dim_counties (
    county_sk INT64,                    -- Surrogate key
    fips_code STRING NOT NULL,
    state_fips STRING,
    county_fips STRING,
    state_name STRING,
    state_abbrev STRING,
    county_name STRING,
    centroid GEOGRAPHY,
    boundary GEOGRAPHY,
    area_sq_km FLOAT64,
    population INT64,
    population_density FLOAT64,
    
    -- SCD Type 2 columns
    effective_date DATE,
    expiration_date DATE,
    is_current BOOLEAN,
    
    -- Metadata
    data_quality_score FLOAT64,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Features dimension
CREATE OR REPLACE TABLE resilienceai_analytics.dim_features (
    feature_sk INT64,
    feature_key STRING NOT NULL,
    display_name STRING,
    description STRING,
    category STRING,
    domain STRING,
    data_type STRING,
    unit STRING,
    data_source STRING,
    is_calculated BOOLEAN,
    created_at TIMESTAMP
);

-- Time dimension
CREATE OR REPLACE TABLE resilienceai_analytics.dim_time (
    date_sk INT64,
    full_date DATE,
    year INT64,
    quarter INT64,
    month INT64,
    month_name STRING,
    day INT64,
    day_of_week INT64,
    day_name STRING,
    week_of_year INT64,
    is_weekend BOOLEAN,
    fiscal_year INT64,
    fiscal_quarter INT64
);

-- Facts: County metrics (partitioned by date)
CREATE OR REPLACE TABLE resilienceai_analytics.fact_county_metrics (
    metric_sk INT64,
    date_sk INT64,
    county_sk INT64,
    feature_sk INT64,
    
    -- Measures
    value FLOAT64,
    value_type STRING,                  -- 'measured', 'interpolated', 'forecasted'
    confidence FLOAT64,
    
    -- Metadata
    data_source STRING,
    ingestion_timestamp TIMESTAMP
)
PARTITION BY DATE(_PARTITIONTIME)
CLUSTER BY county_sk, feature_sk;

-- Facts: Predictions
CREATE OR REPLACE TABLE resilienceai_analytics.fact_predictions (
    prediction_sk INT64,
    prediction_date_sk INT64,
    target_date_sk INT64,
    county_sk INT64,
    model_id STRING,
    prediction_type STRING,
    
    -- Measures
    predicted_value FLOAT64,
    confidence_lower FLOAT64,
    confidence_upper FLOAT64,
    confidence_level FLOAT64,
    
    -- Validation
    actual_value FLOAT64,
    prediction_error FLOAT64,
    is_validated BOOLEAN
)
PARTITION BY DATE(_PARTITIONTIME)
CLUSTER BY county_sk, model_id;

-- Facts: Alert events
CREATE OR REPLACE TABLE resilienceai_analytics.fact_alerts (
    alert_sk INT64,
    triggered_date_sk INT64,
    county_sk INT64,
    alert_type STRING,
    severity STRING,
    
    -- Measures
    response_time_minutes INT64,        -- Time to acknowledge
    resolution_time_minutes INT64,      -- Time to resolve
    
    -- Status
    status STRING,
    was_ignored BOOLEAN
)
PARTITION BY DATE(_PARTITIONTIME);
```

### 7.2 BigQuery Python Client

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/python/bigquery_client.py

"""
BigQuery client for analytics and ML workloads
"""

from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, SourceFormat
from typing import List, Dict, Optional, Iterator
import pandas as pd
import os

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "resilienceai-prod")
DATASET_ID = "resilienceai_analytics"


class BigQueryAnalytics:
    """BigQuery analytics operations"""
    
    def __init__(self):
        self.client = bigquery.Client(project=PROJECT_ID)
        self.dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    
    def query_county_metrics(
        self, 
        fips_codes: List[str], 
        feature_keys: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Query county metrics for analysis"""
        query = f"""
        SELECT 
            c.county_name,
            c.state_abbrev,
            f.feature_key,
            f.display_name,
            t.full_date,
            m.value,
            m.confidence
        FROM `{self.dataset_ref}.fact_county_metrics` m
        JOIN `{self.dataset_ref}.dim_counties` c ON m.county_sk = c.county_sk
        JOIN `{self.dataset_ref}.dim_features` f ON m.feature_sk = f.feature_sk
        JOIN `{self.dataset_ref}.dim_time` t ON m.date_sk = t.date_sk
        WHERE c.fips_code IN UNNEST(@fips_codes)
          AND f.feature_key IN UNNEST(@feature_keys)
          AND t.full_date BETWEEN @start_date AND @end_date
        ORDER BY t.full_date, c.county_name, f.feature_key
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("fips_codes", "STRING", fips_codes),
                bigquery.ArrayQueryParameter("feature_keys", "STRING", feature_keys),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            ]
        )
        
        return self.client.query(query, job_config=job_config).to_dataframe()
    
    def get_prediction_accuracy(
        self, 
        model_id: str,
        days_back: int = 30
    ) -> Dict:
        """Get prediction accuracy metrics"""
        query = f"""
        SELECT 
            prediction_type,
            COUNT(*) as total_predictions,
            AVG(ABS(prediction_error)) as mae,
            AVG(POW(prediction_error, 2)) as mse,
            SQRT(AVG(POW(prediction_error, 2))) as rmse,
            AVG(CASE WHEN ABS(prediction_error) < 0.1 THEN 1 ELSE 0 END) as accuracy_within_10pct
        FROM `{self.dataset_ref}.fact_predictions`
        WHERE model_id = @model_id
          AND is_validated = TRUE
          AND DATE(_PARTITIONTIME) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days_back DAY)
        GROUP BY prediction_type
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("model_id", "STRING", model_id),
                bigquery.ScalarQueryParameter("days_back", "INT64", days_back),
            ]
        )
        
        df = self.client.query(query, job_config=job_config).to_dataframe()
        return df.to_dict('records')
    
    def export_to_gcs(
        self, 
        table_name: str, 
        gcs_path: str,
        format: str = "parquet"
    ):
        """Export table to Google Cloud Storage"""
        destination = f"gs://{gcs_path}/{table_name}.{format}"
        
        job_config = bigquery.ExtractJobConfig(
            destination_format=getattr(bigquery.DestinationFormat, format.upper())
        )
        
        table_ref = f"{self.dataset_ref}.{table_name}"
        extract_job = self.client.extract_table(
            table_ref, destination, job_config=job_config
        )
        extract_job.result()
        
        return destination
    
    def load_from_dataframe(
        self, 
        df: pd.DataFrame, 
        table_name: str,
        write_disposition: str = "WRITE_APPEND"
    ):
        """Load DataFrame to BigQuery"""
        table_ref = f"{self.dataset_ref}.{table_name}"
        
        job_config = LoadJobConfig(
            write_disposition=getattr(bigquery.WriteDisposition, write_disposition),
            source_format=SourceFormat.PARQUET
        )
        
        job = self.client.load_table_from_dataframe(
            df, table_ref, job_config=job_config
        )
        job.result()
        
        return job.output_rows
```

---

## 8. Indexing and Partitioning Strategies

### 8.1 Index Strategy Summary

```sql
-- File: /mnt/okcomputer/output/resilience_ai_analysis/sql/07_indexing_strategy.sql

-- ============================================
-- INDEXING STRATEGY FOR RESILIENCEAI
-- ============================================

-- 1. PRIMARY ACCESS PATTERNS
--    - Query by FIPS code (most common)
--    - Query by state
--    - Geospatial queries (within radius, intersection)
--    - Time-range queries
--    - Feature value range queries

-- 2. INDEX CATEGORIES

-- A. B-Tree Indexes (Equality and range queries)
-- For: Exact matches, range scans, sorting

CREATE INDEX idx_counties_fips ON counties(fips_code);
CREATE INDEX idx_counties_state ON counties(state_abbrev);
CREATE INDEX idx_features_key ON feature_definitions(feature_key);
CREATE INDEX idx_county_features_value ON county_features(numeric_value);

-- B. GiST Indexes (Geospatial)
-- For: Spatial relationships, nearest neighbor

CREATE INDEX idx_counties_centroid ON counties USING GIST(centroid);
CREATE INDEX idx_counties_boundary ON counties USING GIST(boundary);
CREATE INDEX idx_facilities_location ON facilities USING GIST(location);

-- C. GIN Indexes (Full-text, JSONB, Arrays)
-- For: Text search, JSON containment, array operations

CREATE INDEX idx_counties_name_trgm ON counties USING GIN(county_name gin_trgm_ops);
CREATE INDEX idx_county_features_json ON county_features USING GIN(json_value);
CREATE INDEX idx_alert_events_affected ON alert_events USING GIN(affected_features);

-- D. BRIN Indexes (Block Range - for large time-series)
-- For: Time-series data where values correlate with insertion order

CREATE INDEX idx_metrics_history_brin ON county_metrics_history USING BRIN(time);

-- E. Partial Indexes (Filtered subsets)
-- For: Frequently queried subsets

CREATE INDEX idx_counties_mo ON counties(state_abbrev) WHERE state_abbrev = 'MO';
CREATE INDEX idx_alerts_active ON alert_events(status) WHERE status = 'active';
CREATE INDEX idx_facilities_hospitals ON facilities(facility_type) WHERE facility_type = 'hospital';

-- F. Composite Indexes (Multi-column)
-- For: Queries with multiple WHERE conditions

CREATE INDEX idx_county_features_county_feature_date 
    ON county_features(county_id, feature_id, effective_date DESC);

CREATE INDEX idx_predictions_county_model 
    ON predictions(county_id, model_id, time DESC);

-- 3. INDEX MAINTENANCE

-- Analyze tables for query planner
ANALYZE counties;
ANALYZE county_features;
ANALYZE feature_definitions;

-- Monitor index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Identify unused indexes (candidates for removal)
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%pkey%'
ORDER BY schemaname, tablename;
```

### 8.2 Partitioning Strategy

```sql
-- File: /mnt/okcomputer/output/resilience_ai_analysis/sql/08_partitioning_strategy.sql

-- ============================================
-- PARTITIONING STRATEGY
-- ============================================

-- 1. TIME-SERIES PARTITIONING (TimescaleDB Hypertables)
-- Already configured in TimescaleDB section

-- 2. RANGE PARTITIONING FOR LARGE TABLES

-- County features by effective date (if not using TimescaleDB)
CREATE TABLE county_features_partitioned (
    id UUID DEFAULT uuid_generate_v4(),
    county_id UUID NOT NULL,
    feature_id UUID NOT NULL,
    numeric_value DECIMAL(20, 8),
    effective_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id, effective_date)
) PARTITION BY RANGE (effective_date);

-- Create partitions by year
CREATE TABLE county_features_2024 PARTITION OF county_features_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE county_features_2025 PARTITION OF county_features_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Automate partition creation
CREATE OR REPLACE FUNCTION create_county_features_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_date := DATE_TRUNC('year', CURRENT_DATE + INTERVAL '1 year');
    partition_name := 'county_features_' || EXTRACT(YEAR FROM partition_date);
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 year';
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF county_features_partitioned
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;

-- 3. LIST PARTITIONING BY STATE

-- For state-specific queries
CREATE TABLE county_metrics_by_state (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    county_id UUID NOT NULL,
    state_abbrev VARCHAR(2) NOT NULL,
    feature_id UUID NOT NULL,
    value DECIMAL(20, 8)
) PARTITION BY LIST (state_abbrev);

-- Create partitions for high-priority states
CREATE TABLE county_metrics_mo PARTITION OF county_metrics_by_state
    FOR VALUES IN ('MO');

CREATE TABLE county_metrics_ca PARTITION OF county_metrics_by_state
    FOR VALUES IN ('CA');

CREATE TABLE county_metrics_tx PARTITION OF county_metrics_by_state
    FOR VALUES IN ('TX');

CREATE TABLE county_metrics_other PARTITION OF county_metrics_by_state
    DEFAULT;
```

---

## 9. Connection Pooling

### 9.1 PgBouncer Configuration

```ini
; File: /mnt/okcomputer/output/resilience_ai_analysis/config/pgbouncer.ini

; PgBouncer Configuration for ResilienceAI
; Place in: /etc/pgbouncer/pgbouncer.ini

[databases]
; Map connection names to actual databases
resilienceai = host=localhost port=5432 dbname=resilienceai
resilienceai_timescale = host=localhost port=5432 dbname=resilienceai

[pgbouncer]
; Connection settings
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; Pool settings - optimized for ResilienceAI workload
pool_mode = transaction           ; Best for web applications
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3

; Timeouts
server_idle_timeout = 600
server_lifetime = 3600
server_connect_timeout = 15
query_timeout = 0
query_wait_timeout = 120
client_idle_timeout = 0
client_login_timeout = 60

; Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
stats_period = 60

; Admin console
admin_users = postgres, pgbouncer_admin
stats_users = stats_collector

; TLS settings (for production)
; client_tls_sslmode = require
; client_tls_key_file = /etc/ssl/private/pgbouncer.key
; client_tls_cert_file = /etc/ssl/certs/pgbouncer.crt
```

### 9.2 Application Connection Pool

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/python/db_connection.py

"""
Database connection management with connection pooling
"""

from contextlib import contextmanager
from typing import Generator, Optional
import os
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "6432"),  # PgBouncer port
    "database": os.getenv("DB_NAME", "resilienceai"),
    "user": os.getenv("DB_USER", "resilienceai_app"),
    "password": os.getenv("DB_PASSWORD"),
}

# Connection pool settings
POOL_CONFIG = {
    "minconn": 5,
    "maxconn": 50,
}


class DatabasePool:
    """Thread-safe database connection pool"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._pool = pool.ThreadedConnectionPool(
                **POOL_CONFIG,
                **DB_CONFIG
            )
        return cls._instance
    
    @contextmanager
    def get_connection(self) -> Generator:
        """Get connection from pool with automatic return"""
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor) -> Generator:
        """Get cursor with automatic cleanup"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute(self, query: str, params: Optional[tuple] = None) -> list:
        """Execute query and return results"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_many(self, query: str, params_list: list):
        """Execute query with multiple parameter sets"""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
    
    def close_all(self):
        """Close all connections in pool"""
        if self._pool:
            self._pool.closeall()


# Global pool instance
db_pool = DatabasePool()


# Convenience functions for common operations

def get_county_by_fips(fips_code: str) -> Optional[dict]:
    """Get county by FIPS code"""
    query = """
    SELECT * FROM counties 
    WHERE fips_code = %s
    """
    results = db_pool.execute(query, (fips_code,))
    return results[0] if results else None


def get_county_features(fips_code: str, feature_keys: Optional[list] = None) -> list:
    """Get features for a county"""
    if feature_keys:
        query = """
        SELECT f.feature_key, f.display_name, cf.numeric_value, cf.confidence_score
        FROM counties c
        JOIN county_features cf ON c.id = cf.county_id
        JOIN feature_definitions f ON cf.feature_id = f.id
        WHERE c.fips_code = %s AND f.feature_key = ANY(%s)
        ORDER BY f.display_name
        """
        return db_pool.execute(query, (fips_code, feature_keys))
    else:
        query = """
        SELECT f.feature_key, f.display_name, cf.numeric_value, cf.confidence_score
        FROM counties c
        JOIN county_features cf ON c.id = cf.county_id
        JOIN feature_definitions f ON cf.feature_id = f.id
        WHERE c.fips_code = %s
        ORDER BY f.display_name
        """
        return db_pool.execute(query, (fips_code,))


def get_counties_in_radius(
    lat: float, 
    lon: float, 
    radius_km: float
) -> list:
    """Get counties within radius of point"""
    query = """
    SELECT 
        c.*,
        ST_Distance(c.centroid, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) / 1000 as distance_km
    FROM counties c
    WHERE ST_DWithin(
        c.centroid::geography,
        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
        %s * 1000
    )
    ORDER BY distance_km
    """
    return db_pool.execute(query, (lon, lat, lon, lat, radius_km))
```

---

## 10. Backup and Recovery

### 10.1 Backup Strategy

```bash
#!/bin/bash
# File: /mnt/okcomputer/output/resilience_ai_analysis/scripts/backup.sh

# ============================================
# BACKUP SCRIPT FOR RESILIENCEAI DATABASES
# ============================================

set -e

# Configuration
BACKUP_DIR="/backup/resilienceai"
S3_BUCKET="s3://resilienceai-backups"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

# Database credentials
DB_NAME="resilienceai"
DB_USER="backup_user"
DB_HOST="localhost"

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 1. PostgreSQL Full Backup (Weekly)
backup_postgres_full() {
    log "Starting PostgreSQL full backup..."
    
    pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
        --format=custom \
        --compress=9 \
        --file="$BACKUP_DIR/$DATE/postgres_full.dump"
    
    log "PostgreSQL full backup completed"
}

# 2. PostgreSQL Incremental (Daily - using WAL archiving)
backup_postgres_incremental() {
    log "Starting PostgreSQL incremental backup..."
    
    # Trigger WAL switch to ensure all changes are archived
    psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT pg_switch_wal();"
    
    # Backup WAL files
    tar -czf "$BACKUP_DIR/$DATE/wal_archive.tar.gz" /var/lib/postgresql/wal_archive/
    
    log "PostgreSQL incremental backup completed"
}

# 3. Schema-only backup
backup_schema() {
    log "Starting schema backup..."
    
    pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
        --schema-only \
        --file="$BACKUP_DIR/$DATE/schema.sql"
    
    log "Schema backup completed"
}

# 4. Specific table backups (high-value tables)
backup_critical_tables() {
    log "Starting critical table backups..."
    
    TABLES=("counties" "county_features" "alert_events" "feature_definitions")
    
    for table in "${TABLES[@]}"; do
        pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
            --table="$table" \
            --format=custom \
            --file="$BACKUP_DIR/$DATE/table_${table}.dump"
        log "Backed up table: $table"
    done
}

# 5. TimescaleDB backup
backup_timescaledb() {
    log "Starting TimescaleDB backup..."
    
    # Use timescaledb-backup tool if available
    if command -v timescaledb-backup &> /dev/null; then
        timescaledb-backup dump \
            --db-name="$DB_NAME" \
            --output="$BACKUP_DIR/$DATE/timescaledb"
    else
        # Fallback to regular pg_dump with TimescaleDB options
        pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
            --format=custom \
            --file="$BACKUP_DIR/$DATE/timescaledb.dump" \
            --exclude-table='_timescaledb_internal.*'
    fi
    
    log "TimescaleDB backup completed"
}

# 6. Redis backup
backup_redis() {
    log "Starting Redis backup..."
    
    redis-cli BGSAVE
    
    # Wait for background save to complete
    while redis-cli INFO persistence | grep -q "rdb_bgsave_in_progress:1"; do
        sleep 1
    done
    
    cp /var/lib/redis/dump.rdb "$BACKUP_DIR/$DATE/redis.rdb"
    
    log "Redis backup completed"
}

# 7. Compress and upload to S3
upload_to_s3() {
    log "Compressing and uploading to S3..."
    
    cd "$BACKUP_DIR"
    tar -czf "$DATE.tar.gz" "$DATE"
    
    aws s3 cp "$DATE.tar.gz" "$S3_BUCKET/daily/"
    
    # Also copy to latest for quick access
    aws s3 cp "$DATE.tar.gz" "$S3_BUCKET/latest/backup.tar.gz"
    
    rm -rf "$DATE" "$DATE.tar.gz"
    
    log "Upload to S3 completed"
}

# 8. Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up old backups..."
    
    aws s3 ls "$S3_BUCKET/daily/" | \
        awk '{print $4}' | \
        while read -r file; do
            date_str=$(echo "$file" | grep -oP '^\d{8}')
            file_date=$(date -d "$date_str" +%s 2>/dev/null || echo 0)
            cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%s)
            
            if [ "$file_date" -lt "$cutoff_date" ]; then
                aws s3 rm "$S3_BUCKET/daily/$file"
                log "Deleted old backup: $file"
            fi
        done
    
    log "Cleanup completed"
}

# Main execution
main() {
    log "Starting backup process..."
    
    case "${1:-full}" in
        full)
            backup_postgres_full
            backup_schema
            backup_critical_tables
            backup_timescaledb
            backup_redis
            upload_to_s3
            cleanup_old_backups
            ;;
        incremental)
            backup_postgres_incremental
            upload_to_s3
            ;;
        schema)
            backup_schema
            upload_to_s3
            ;;
        *)
            echo "Usage: $0 {full|incremental|schema}"
            exit 1
            ;;
    esac
    
    log "Backup process completed successfully"
}

main "$@"
```

### 10.2 Recovery Procedures

```bash
#!/bin/bash
# File: /mnt/okcomputer/output/resilience_ai_analysis/scripts/restore.sh

# ============================================
# RESTORE SCRIPT FOR RESILIENCEAI DATABASES
# ============================================

set -e

# Configuration
S3_BUCKET="s3://resilienceai-backups"
RESTORE_DIR="/tmp/restore"
DB_NAME="resilienceai"
DB_USER="postgres"
DB_HOST="localhost"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 1. List available backups
list_backups() {
    log "Available backups:"
    aws s3 ls "$S3_BUCKET/daily/" | tail -20
}

# 2. Download backup from S3
download_backup() {
    local backup_file=$1
    
    log "Downloading backup: $backup_file"
    
    mkdir -p "$RESTORE_DIR"
    aws s3 cp "$S3_BUCKET/daily/$backup_file" "$RESTORE_DIR/"
    
    cd "$RESTORE_DIR"
    tar -xzf "$backup_file"
    
    log "Backup downloaded and extracted"
}

# 3. Restore PostgreSQL full backup
restore_postgres_full() {
    local backup_date=$1
    
    log "Restoring PostgreSQL full backup from $backup_date..."
    
    # Drop and recreate database
    psql -h "$DB_HOST" -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;"
    psql -h "$DB_HOST" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"
    
    # Restore from backup
    pg_restore -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
        --verbose \
        --no-owner \
        --no-privileges \
        "$RESTORE_DIR/$backup_date/postgres_full.dump"
    
    log "PostgreSQL full restore completed"
}

# 4. Restore specific table
restore_table() {
    local backup_date=$1
    local table_name=$2
    
    log "Restoring table: $table_name"
    
    # Truncate existing table
    psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "TRUNCATE TABLE $table_name CASCADE;"
    
    # Restore table data
    pg_restore -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
        --table="$table_name" \
        --data-only \
        "$RESTORE_DIR/$backup_date/table_${table_name}.dump"
    
    log "Table restore completed: $table_name"
}

# 5. Point-in-time recovery (PITR)
restore_pitr() {
    local target_timestamp=$1
    
    log "Performing point-in-time recovery to: $target_timestamp"
    
    # Stop PostgreSQL
    systemctl stop postgresql
    
    # Clean data directory
    rm -rf /var/lib/postgresql/data/*
    
    # Restore base backup
    pg_basebackup -h "$DB_HOST" -U "$DB_USER" -D /var/lib/postgresql/data/ -Fp -Xs -P
    
    # Create recovery signal
    touch /var/lib/postgresql/data/recovery.signal
    
    # Configure recovery
    cat >> /var/lib/postgresql/data/postgresql.conf << EOF
restore_command = 'aws s3 cp $S3_BUCKET/wal/%f %p'
recovery_target_time = '$target_timestamp'
recovery_target_action = 'promote'
EOF
    
    # Start PostgreSQL for recovery
    systemctl start postgresql
    
    log "Point-in-time recovery initiated"
}

# 6. Restore Redis
restore_redis() {
    local backup_date=$1
    
    log "Restoring Redis..."
    
    # Stop Redis
    systemctl stop redis
    
    # Restore dump file
    cp "$RESTORE_DIR/$backup_date/redis.rdb" /var/lib/redis/dump.rdb
    chown redis:redis /var/lib/redis/dump.rdb
    
    # Start Redis
    systemctl start redis
    
    log "Redis restore completed"
}

# 7. Verify restore
verify_restore() {
    log "Verifying restore..."
    
    # Check table counts
    psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" << EOF
SELECT 
    'counties' as table_name, COUNT(*) as row_count FROM counties
UNION ALL
SELECT 'county_features', COUNT(*) FROM county_features
UNION ALL
SELECT 'feature_definitions', COUNT(*) FROM feature_definitions
UNION ALL
SELECT 'alert_events', COUNT(*) FROM alert_events;
EOF
    
    log "Verification completed"
}

# Main execution
main() {
    local command=$1
    local backup_date=$2
    
    case "$command" in
        list)
            list_backups
            ;;
        full)
            if [ -z "$backup_date" ]; then
                echo "Usage: $0 full <backup_date>"
                exit 1
            fi
            download_backup "${backup_date}.tar.gz"
            restore_postgres_full "$backup_date"
            restore_redis "$backup_date"
            verify_restore
            ;;
        table)
            local table_name=$3
            if [ -z "$backup_date" ] || [ -z "$table_name" ]; then
                echo "Usage: $0 table <backup_date> <table_name>"
                exit 1
            fi
            download_backup "${backup_date}.tar.gz"
            restore_table "$backup_date" "$table_name"
            ;;
        pitr)
            local target_timestamp=$2
            if [ -z "$target_timestamp" ]; then
                echo "Usage: $0 pitr <target_timestamp>"
                exit 1
            fi
            restore_pitr "$target_timestamp"
            ;;
        *)
            echo "Usage: $0 {list|full|table|pitr}"
            exit 1
            ;;
    esac
    
    # Cleanup
    rm -rf "$RESTORE_DIR"
    
    log "Restore process completed"
}

main "$@"
```

---

## 11. Data Retention Policies

### 11.1 Retention Configuration

```sql
-- File: /mnt/okcomputer/output/resilience_ai_analysis/sql/09_retention_policies.sql

-- ============================================
-- DATA RETENTION POLICIES
-- ============================================

-- 1. TimescaleDB Retention Policies (Automated)

-- County metrics: Keep raw data for 2 years
SELECT add_retention_policy('county_metrics_history', INTERVAL '2 years');

-- Real-time events: Keep for 90 days
SELECT add_retention_policy('realtime_events', INTERVAL '90 days');

-- Predictions: Keep for 1 year (validate then archive)
SELECT add_retention_policy('predictions', INTERVAL '1 year');

-- 2. Custom Retention Functions

-- Archive old county features to cold storage
CREATE OR REPLACE FUNCTION archive_old_county_features()
RETURNS void AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- Move data older than 5 years to archive table
    INSERT INTO county_features_archive
    SELECT * FROM county_features
    WHERE effective_date < CURRENT_DATE - INTERVAL '5 years'
    ON CONFLICT DO NOTHING;
    
    GET DIAGNOSTICS archived_count = ROW_COUNT;
    
    -- Delete archived data from main table
    DELETE FROM county_features
    WHERE effective_date < CURRENT_DATE - INTERVAL '5 years';
    
    RAISE NOTICE 'Archived % rows', archived_count;
END;
$$ LANGUAGE plpgsql;

-- Clean up old alert events
CREATE OR REPLACE FUNCTION cleanup_old_alerts()
RETURNS void AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete resolved alerts older than 1 year
    DELETE FROM alert_events
    WHERE status = 'resolved'
      AND resolved_at < NOW() - INTERVAL '1 year';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % old resolved alerts', deleted_count;
    
    -- Delete dismissed alerts older than 6 months
    DELETE FROM alert_events
    WHERE status = 'dismissed'
      AND triggered_at < NOW() - INTERVAL '6 months';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % old dismissed alerts', deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Clean up old alert deliveries
CREATE OR REPLACE FUNCTION cleanup_old_deliveries()
RETURNS void AS $$
BEGIN
    DELETE FROM alert_deliveries
    WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- 3. Partition Management for Time-Series

-- Automatically drop old partitions
CREATE OR REPLACE FUNCTION drop_old_partitions(
    table_name TEXT,
    retention_months INTEGER
)
RETURNS void AS $$
DECLARE
    partition RECORD;
    cutoff_date DATE;
BEGIN
    cutoff_date := CURRENT_DATE - (retention_months || ' months')::INTERVAL;
    
    FOR partition IN
        SELECT inhrelid::regclass AS partition_name
        FROM pg_inherits
        WHERE inhparent = table_name::regclass
    LOOP
        -- Extract date from partition name (assumes naming convention)
        -- This is a simplified example - adjust for your naming convention
        IF partition.partition_name::TEXT ~ '\\d{4}_\\d{2}' THEN
            -- Parse partition date from name
            DECLARE
                partition_date DATE;
            BEGIN
                partition_date := TO_DATE(
                    SUBSTRING(partition.partition_name::TEXT FROM '\\d{4}_\\d{2}'),
                    'YYYY_MM'
                );
                
                IF partition_date < cutoff_date THEN
                    EXECUTE format('DROP TABLE IF EXISTS %I', partition.partition_name);
                    RAISE NOTICE 'Dropped partition: %', partition.partition_name;
                END IF;
            END;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 4. Scheduled Cleanup Job (using pg_cron)

-- Install pg_cron extension if available
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule daily cleanup at 3 AM
SELECT cron.schedule('daily-cleanup', '0 3 * * *', $$
    SELECT archive_old_county_features();
    SELECT cleanup_old_alerts();
    SELECT cleanup_old_deliveries();
$$);

-- Schedule weekly partition maintenance on Sundays at 4 AM
SELECT cron.schedule('weekly-partition-maintenance', '0 4 * * 0', $$
    SELECT drop_old_partitions('county_metrics_history', 24);  -- 2 years
$$);

-- 5. Data Compression (TimescaleDB)

-- Enable compression on hypertables
ALTER TABLE county_metrics_history SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'county_id, feature_id'
);

-- Add compression policy (compress chunks older than 7 days)
SELECT add_compression_policy('county_metrics_history', INTERVAL '7 days');

-- 6. Retention Policy Summary View

CREATE OR REPLACE VIEW data_retention_summary AS
SELECT 
    'county_metrics_history' as table_name,
    'TimescaleDB retention' as policy_type,
    '2 years' as retention_period,
    (SELECT COUNT(*) FROM timescaledb_information.jobs WHERE application_name = 'Retention Policy [1]') as active
UNION ALL
SELECT 
    'realtime_events',
    'TimescaleDB retention',
    '90 days',
    (SELECT COUNT(*) FROM timescaledb_information.jobs WHERE application_name = 'Retention Policy [2]')
UNION ALL
SELECT 
    'predictions',
    'TimescaleDB retention',
    '1 year',
    (SELECT COUNT(*) FROM timescaledb_information.jobs WHERE application_name = 'Retention Policy [3]')
UNION ALL
SELECT 
    'alert_events',
    'Custom function',
    '1 year (resolved)',
    (SELECT COUNT(*) FROM cron.job WHERE jobname = 'daily-cleanup');
```

---

## 12. Migration Strategy

### 12.1 Migration Plan

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/python/migration.py

"""
Data Migration Script: CSV to Multi-Database Architecture
Migrates ResilienceAI from CSV-based storage to PostgreSQL/TimescaleDB/Redis/Pinecone
"""

import pandas as pd
import numpy as np
from typing import Iterator
import logging
from datetime import datetime
import os

from db_connection import db_pool
from redis_cache import cache
from vector_db_pinecone import PineconeVectorStore, CountyVector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataMigrator:
    """Handles migration from CSV to database architecture"""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.vector_store = PineconeVectorStore()
        
    def load_csv(self) -> pd.DataFrame:
        """Load county features CSV"""
        logger.info(f"Loading CSV from {self.csv_path}")
        df = pd.read_csv(self.csv_path)
        logger.info(f"Loaded {len(df)} counties with {len(df.columns)} features")
        return df
    
    def migrate_counties(self, df: pd.DataFrame, batch_size: int = 100):
        """Migrate counties to PostgreSQL"""
        logger.info("Migrating counties...")
        
        # Extract unique counties
        counties_data = []
        for _, row in df.iterrows():
            counties_data.append({
                'fips_code': str(row['fips']).zfill(5),
                'state_fips': str(row['fips'])[:2].zfill(2),
                'county_fips': str(row['fips'])[2:].zfill(3),
                'county_name': row.get('county_name', ''),
                'state_name': row.get('state_name', ''),
                'state_abbrev': row.get('state', ''),
                'population': row.get('population', 0),
            })
        
        # Insert in batches
        insert_query = """
        INSERT INTO counties (
            fips_code, state_fips, county_fips, county_name, 
            state_name, state_abbrev, population
        ) VALUES (
            %(fips_code)s, %(state_fips)s, %(county_fips)s, %(county_name)s,
            %(state_name)s, %(state_abbrev)s, %(population)s
        ) ON CONFLICT (fips_code) DO UPDATE SET
            county_name = EXCLUDED.county_name,
            population = EXCLUDED.population,
            last_updated = NOW()
        """
        
        for i in range(0, len(counties_data), batch_size):
            batch = counties_data[i:i + batch_size]
            with db_pool.get_cursor() as cursor:
                cursor.executemany(insert_query, batch)
            logger.info(f"Migrated {min(i + batch_size, len(counties_data))}/{len(counties_data)} counties")
        
        logger.info("County migration completed")
    
    def migrate_features(self, df: pd.DataFrame, feature_mapping: dict):
        """Migrate feature definitions"""
        logger.info("Migrating feature definitions...")
        
        # Insert feature definitions
        insert_query = """
        INSERT INTO feature_definitions (
            feature_key, display_name, category_id, data_type, unit
        ) VALUES (
            %(feature_key)s, %(display_name)s, %(category_id)s, %(data_type)s, %(unit)s
        ) ON CONFLICT (feature_key) DO NOTHING
        """
        
        with db_pool.get_cursor() as cursor:
            cursor.executemany(insert_query, list(feature_mapping.values()))
        
        logger.info(f"Migrated {len(feature_mapping)} feature definitions")
    
    def migrate_county_features(self, df: pd.DataFrame, batch_size: int = 500):
        """Migrate county feature values"""
        logger.info("Migrating county feature values...")
        
        # Get feature mappings
        with db_pool.get_cursor() as cursor:
            cursor.execute("SELECT id, feature_key FROM feature_definitions")
            feature_ids = {row['feature_key']: row['id'] for row in cursor.fetchall()}
            
            cursor.execute("SELECT id, fips_code FROM counties")
            county_ids = {row['fips_code']: row['id'] for row in cursor.fetchall()}
        
        # Prepare feature values
        feature_values = []
        feature_columns = [c for c in df.columns if c not in ['fips', 'county_name', 'state']]
        
        for _, row in df.iterrows():
            county_fips = str(row['fips']).zfill(5)
            county_id = county_ids.get(county_fips)
            
            if not county_id:
                continue
            
            for feature_key in feature_columns:
                feature_id = feature_ids.get(feature_key)
                if not feature_id:
                    continue
                
                value = row.get(feature_key)
                if pd.isna(value):
                    continue
                
                feature_values.append({
                    'county_id': county_id,
                    'feature_id': feature_id,
                    'numeric_value': float(value),
                    'effective_date': datetime.now().date()
                })
        
        # Insert in batches
        insert_query = """
        INSERT INTO county_features (county_id, feature_id, numeric_value, effective_date)
        VALUES (%(county_id)s, %(feature_id)s, %(numeric_value)s, %(effective_date)s)
        ON CONFLICT (county_id, feature_id, effective_date) DO UPDATE SET
            numeric_value = EXCLUDED.numeric_value,
            calculated_at = NOW()
        """
        
        for i in range(0, len(feature_values), batch_size):
            batch = feature_values[i:i + batch_size]
            with db_pool.get_cursor() as cursor:
                cursor.executemany(insert_query, batch)
            
            if i % (batch_size * 10) == 0:
                logger.info(f"Migrated {min(i + batch_size, len(feature_values))}/{len(feature_values)} feature values")
        
        logger.info("County feature values migration completed")
    
    def migrate_vectors(self, df: pd.DataFrame, vector_columns: list):
        """Migrate vector embeddings to Pinecone"""
        logger.info("Migrating vector embeddings...")
        
        vectors = []
        for _, row in df.iterrows():
            county_fips = str(row['fips']).zfill(5)
            
            # Extract vector values
            vector_values = [float(row.get(col, 0)) for col in vector_columns if not pd.isna(row.get(col))]
            
            # Pad or truncate to VECTOR_DIMENSION
            if len(vector_values) < 384:
                vector_values.extend([0.0] * (384 - len(vector_values)))
            vector_values = vector_values[:384]
            
            vectors.append(CountyVector(
                id=county_fips,
                values=vector_values,
                metadata={
                    'county_name': row.get('county_name', ''),
                    'state': row.get('state', ''),
                    'population': int(row.get('population', 0))
                }
            ))
            
            # Upsert in batches
            if len(vectors) >= 100:
                self.vector_store.upsert_counties(vectors)
                vectors = []
        
        # Upsert remaining
        if vectors:
            self.vector_store.upsert_counties(vectors)
        
        logger.info("Vector migration completed")
    
    def migrate_all(self):
        """Run full migration"""
        logger.info("Starting full migration...")
        
        df = self.load_csv()
        
        # Step 1: Migrate counties
        self.migrate_counties(df)
        
        # Step 2: Migrate feature definitions (requires manual mapping)
        feature_mapping = self._create_feature_mapping(df.columns)
        self.migrate_features(df, feature_mapping)
        
        # Step 3: Migrate county feature values
        self.migrate_county_features(df)
        
        # Step 4: Migrate vectors (if vector columns exist)
        vector_columns = [c for c in df.columns if 'vector' in c.lower() or 'embedding' in c.lower()]
        if vector_columns:
            self.migrate_vectors(df, vector_columns)
        
        logger.info("Migration completed successfully!")
    
    def _create_feature_mapping(self, columns: list) -> dict:
        """Create feature mapping from CSV columns"""
        mapping = {}
        
        # Define category mappings
        category_keywords = {
            'climate': ['disaster', 'flood', 'storm', 'weather', 'climate'],
            'health': ['hospital', 'health', 'elderly', 'disability', 'uninsured'],
            'infrastructure': ['facility', 'station', 'infrastructure'],
            'socioeconomic': ['income', 'poverty', 'population', 'education']
        }
        
        for col in columns:
            if col in ['fips', 'county_name', 'state', 'state_name']:
                continue
            
            # Determine category
            category = 'other'
            for cat, keywords in category_keywords.items():
                if any(kw in col.lower() for kw in keywords):
                    category = cat
                    break
            
            mapping[col] = {
                'feature_key': col,
                'display_name': col.replace('_', ' ').title(),
                'category_id': 1,  # Would lookup actual category ID
                'data_type': 'float',
                'unit': None
            }
        
        return mapping


def main():
    """Main entry point"""
    csv_path = os.getenv('COUNTY_FEATURES_CSV', 'data/processed/county_features.csv')
    
    migrator = DataMigrator(csv_path)
    migrator.migrate_all()


if __name__ == '__main__':
    main()
```

---

## 13. Implementation Priority

### 13.1 Phase 1: Foundation (Weeks 1-2)

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| 1 | Set up PostgreSQL + PostGIS | 2 days | Critical |
| 2 | Create core schema (counties, features) | 3 days | Critical |
| 3 | Implement connection pooling | 1 day | High |
| 4 | Migrate CSV data to PostgreSQL | 2 days | Critical |
| 5 | Set up Redis caching | 1 day | High |
| 6 | Basic backup configuration | 1 day | High |

### 13.2 Phase 2: Time-Series (Weeks 3-4)

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| 1 | Set up TimescaleDB | 2 days | Critical |
| 2 | Create time-series schema | 2 days | Critical |
| 3 | Implement historical data migration | 3 days | High |
| 4 | Set up continuous aggregates | 1 day | Medium |
| 5 | Configure retention policies | 1 day | Medium |

### 13.3 Phase 3: Advanced Features (Weeks 5-6)

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| 1 | Set up Pinecone/Weaviate | 2 days | High |
| 2 | Migrate vector embeddings | 2 days | High |
| 3 | Implement vector search API | 2 days | High |
| 4 | Set up BigQuery data warehouse | 2 days | Medium |
| 5 | Configure data pipeline to BigQuery | 2 days | Medium |

### 13.4 Phase 4: Production Hardening (Weeks 7-8)

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| 1 | Implement comprehensive backup strategy | 2 days | Critical |
| 2 | Set up monitoring and alerting | 2 days | High |
| 3 | Performance tuning and indexing | 3 days | High |
| 4 | Disaster recovery testing | 2 days | Critical |
| 5 | Documentation and runbooks | 2 days | Medium |

---

## Appendix A: File Structure

```
/mnt/okcomputer/output/resilience_ai_analysis/
├── 10_database_architecture.md       # This document
├── sql/
│   ├── 01_counties_schema.sql        # County geospatial schema
│   ├── 02_features_schema.sql        # Features and definitions
│   ├── 03_alerts_schema.sql          # Alert management
│   ├── 04_facilities_schema.sql      # Infrastructure facilities
│   ├── 05_timescale_schema.sql       # Time-series schema
│   ├── 06_bigquery_schema.sql        # Data warehouse schema
│   ├── 07_indexing_strategy.sql      # Index definitions
│   ├── 08_partitioning_strategy.sql  # Partitioning setup
│   └── 09_retention_policies.sql     # Data retention
├── python/
│   ├── vector_db_pinecone.py         # Pinecone integration
│   ├── vector_db_weaviate.py         # Weaviate integration
│   ├── redis_cache.py                # Redis caching
│   ├── redis_sessions.py             # Session management
│   ├── bigquery_client.py            # BigQuery operations
│   ├── db_connection.py              # Connection pooling
│   └── migration.py                  # Data migration script
├── config/
│   └── pgbouncer.ini                 # PgBouncer configuration
└── scripts/
    ├── backup.sh                     # Backup automation
    └── restore.sh                    # Recovery procedures
```

---

## Appendix B: Environment Variables

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=6432
DB_NAME=resilienceai
DB_USER=resilienceai_app
DB_PASSWORD=your_secure_password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1

# Google Cloud/BigQuery
GCP_PROJECT_ID=resilienceai-prod
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# AWS (for backups)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Migration
COUNTY_FEATURES_CSV=data/processed/county_features.csv
```

---

## Summary

This comprehensive database architecture provides ResilienceAI with:

1. **Scalability**: Multi-database approach handles current 3,222 counties × 66 features with room for 100x growth
2. **Performance**: Connection pooling, caching, and optimized indexes ensure sub-second query times
3. **Reliability**: Automated backups, point-in-time recovery, and disaster recovery procedures
4. **Flexibility**: Support for geospatial queries, time-series analysis, and vector similarity search
5. **Cost-effectiveness**: Tiered storage with hot (Redis), warm (PostgreSQL), and cold (BigQuery) data

The migration path is designed to be incremental, allowing the system to transition from CSV-based storage to a production-ready multi-database architecture over 8 weeks.
