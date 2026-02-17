# ResilienceAI Search Engine Integration Design

## Executive Summary

This document provides a comprehensive design for integrating Elasticsearch into ResilienceAI, enabling powerful full-text search, faceted search, and geospatial search capabilities. The design covers architecture, implementation, and operational aspects of the search infrastructure.

---

## Table of Contents

1. [Search Architecture Overview](#1-search-architecture-overview)
2. [Elasticsearch Integration](#2-elasticsearch-integration)
3. [Index Mapping Design](#3-index-mapping-design)
4. [Full-Text Search Implementation](#4-full-text-search-implementation)
5. [Faceted Search Design](#5-faceted-search-design)
6. [Geospatial Search](#6-geospatial-search)
7. [Query DSL Reference](#7-query-dsl-reference)
8. [Search Relevance Tuning](#8-search-relevance-tuning)
9. [Autocomplete Implementation](#9-autocomplete-implementation)
10. [Search Analytics](#10-search-analytics)
11. [Index Management](#11-index-management)
12. [Implementation Priority](#12-implementation-priority)

---

## 1. Search Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ResilienceAI Search Architecture                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Web App    │    │  Mobile App  │    │   API Clients│                   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                   │                            │
│         └───────────────────┼───────────────────┘                            │
│                             │                                                │
│                    ┌────────▼────────┐                                       │
│                    │  API Gateway    │                                       │
│                    │  (Rate Limiting)│                                       │
│                    └────────┬────────┘                                       │
│                             │                                                │
│         ┌───────────────────┼───────────────────┐                           │
│         │                   │                   │                            │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐                      │
│  │   Search    │    │  Suggest    │    │  Analytics  │                      │
│  │   Service   │    │   Service   │    │   Service   │                      │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                      │
│         │                   │                   │                            │
│         └───────────────────┼───────────────────┘                            │
│                             │                                                │
│                    ┌────────▼────────┐                                       │
│                    │ Search Client   │                                       │
│                    │   (Python)      │                                       │
│                    └────────┬────────┘                                       │
│                             │                                                │
│         ┌───────────────────┼───────────────────┐                           │
│         │                   │                   │                            │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐                      │
│  │Elasticsearch│    │Elasticsearch│    │Elasticsearch│                      │
│  │  Cluster    │    │   ML Node   │    │  Monitor    │                      │
│  │  (3 nodes)  │    │  (Inference)│    │   (APM)     │                      │
│  └─────────────┘    └─────────────┘    └─────────────┘                      │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         Data Pipeline                                    ││
│  │  PostgreSQL → Debezium → Kafka → Logstash → Elasticsearch              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Search Service | Handle search requests, query building | Python/FastAPI |
| Suggest Service | Autocomplete, type-ahead suggestions | Elasticsearch |
| Analytics Service | Search analytics, click tracking | Elasticsearch + Kibana |
| Search Client | Elasticsearch connection management | `elasticsearch-py` |
| Data Pipeline | Sync data from primary DB to ES | Debezium + Kafka + Logstash |

### 1.3 Cluster Configuration

```yaml
# elasticsearch-cluster.yml
cluster:
  name: resilience-ai-search
  routing:
    allocation:
      awareness:
        attributes: zone
      disk:
        watermark:
          low: "85%"
          high: "90%"
          flood_stage: "95%"

node:
  master: true
  data: true
  ingest: true
  ml: true

path:
  data: /var/lib/elasticsearch
  logs: /var/log/elasticsearch

network:
  host: 0.0.0.0

http:
  port: 9200
  cors:
    enabled: true
    allow-origin: "*"

discovery:
  seed_hosts:
    - es-node-1:9300
    - es-node-2:9300
    - es-node-3:9300
  
xpack:
  security:
    enabled: true
  monitoring:
    enabled: true
  ml:
    enabled: true
```

---

## 2. Elasticsearch Integration

### 2.1 Python Client Configuration

```python
# /app/search/elasticsearch_client.py
"""
Elasticsearch client configuration and connection management for ResilienceAI.
"""

from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch.helpers import bulk, parallel_bulk
from functools import lru_cache
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ElasticsearchConfig:
    """Configuration for Elasticsearch connection."""
    
    HOSTS = ["http://localhost:9200"]  # Production: use env vars
    USERNAME = "elastic"
    PASSWORD = "changeme"  # Use secrets manager in production
    
    # Connection pool settings
    MAX_CONNECTIONS = 20
    MAX_CONNECTIONS_PER_HOST = 10
    
    # Timeout settings
    REQUEST_TIMEOUT = 30
    RETRY_ON_TIMEOUT = True
    MAX_RETRIES = 3
    
    # Performance settings
    COMPRESSION = True
    SNIFF_ON_START = True
    SNIFF_ON_CONNECTION_FAIL = True
    SNIFFER_TIMEOUT = 60


class ElasticsearchClient:
    """Singleton Elasticsearch client with connection pooling."""
    
    _instance: Optional[Elasticsearch] = None
    _async_instance: Optional[AsyncElasticsearch] = None
    
    @classmethod
    def get_client(cls) -> Elasticsearch:
        """Get or create singleton Elasticsearch client."""
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance
    
    @classmethod
    def get_async_client(cls) -> AsyncElasticsearch:
        """Get or create singleton async Elasticsearch client."""
        if cls._async_instance is None:
            cls._async_instance = cls._create_async_client()
        return cls._async_instance
    
    @classmethod
    def _create_client(cls) -> Elasticsearch:
        """Create synchronous Elasticsearch client."""
        config = ElasticsearchConfig
        
        client = Elasticsearch(
            hosts=config.HOSTS,
            basic_auth=(config.USERNAME, config.PASSWORD),
            maxsize=config.MAX_CONNECTIONS,
            timeout=config.REQUEST_TIMEOUT,
            retry_on_timeout=config.RETRY_ON_TIMEOUT,
            max_retries=config.MAX_RETRIES,
            compression=config.COMPRESSION,
            sniff_on_start=config.SNIFF_ON_START,
            sniff_on_connection_fail=config.SNIFF_ON_CONNECTION_FAIL,
            sniffer_timeout=config.SNIFFER_TIMEOUT,
        )
        
        # Verify connection
        if not client.ping():
            raise ConnectionError("Failed to connect to Elasticsearch")
        
        logger.info(f"Connected to Elasticsearch cluster: {client.info()['cluster_name']}")
        return client
    
    @classmethod
    def _create_async_client(cls) -> AsyncElasticsearch:
        """Create asynchronous Elasticsearch client."""
        config = ElasticsearchConfig
        
        client = AsyncElasticsearch(
            hosts=config.HOSTS,
            basic_auth=(config.USERNAME, config.PASSWORD),
            maxsize=config.MAX_CONNECTIONS,
            timeout=config.REQUEST_TIMEOUT,
            retry_on_timeout=config.RETRY_ON_TIMEOUT,
            max_retries=config.MAX_RETRIES,
            compression=config.COMPRESSION,
        )
        
        logger.info("Created async Elasticsearch client")
        return client
    
    @classmethod
    def close(cls):
        """Close all client connections."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
        if cls._async_instance:
            cls._async_instance = None


# Health check utility
def check_elasticsearch_health() -> Dict[str, Any]:
    """Check Elasticsearch cluster health."""
    client = ElasticsearchClient.get_client()
    
    health = client.cluster.health()
    stats = client.cluster.stats()
    
    return {
        "status": health["status"],
        "cluster_name": health["cluster_name"],
        "number_of_nodes": health["number_of_nodes"],
        "active_shards": health["active_shards"],
        "relocating_shards": health["relocating_shards"],
        "unassigned_shards": health["unassigned_shards"],
        "indices_count": stats["indices"]["count"],
        "docs_count": stats["indices"]["docs"]["count"],
        "store_size": stats["indices"]["store"]["size_in_bytes"],
    }
```

### 2.2 Connection Manager with Circuit Breaker

```python
# /app/search/connection_manager.py
"""
Connection manager with circuit breaker pattern for resilient Elasticsearch access.
"""

from elasticsearch import TransportError, ConnectionError
from functools import wraps
from typing import Callable, Any
import time
import logging

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for Elasticsearch operations."""
    
    FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = 30  # seconds
    HALF_OPEN_MAX_CALLS = 3
    
    def __init__(self):
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.RECOVERY_TIMEOUT:
                self.state = "HALF_OPEN"
                self.half_open_calls = 0
                logger.info("Circuit breaker entering HALF_OPEN state")
                return True
            return False
        
        if self.state == "HALF_OPEN":
            if self.half_open_calls < self.HALF_OPEN_MAX_CALLS:
                self.half_open_calls += 1
                return True
            return False
        
        return True
    
    def record_success(self):
        """Record successful operation."""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failures = 0
            self.half_open_calls = 0
            logger.info("Circuit breaker CLOSED")
        else:
            self.failures = max(0, self.failures - 1)
    
    def record_failure(self):
        """Record failed operation."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            logger.warning("Circuit breaker OPENED (half-open failure)")
        elif self.failures >= self.FAILURE_THRESHOLD:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker OPENED ({self.failures} failures)")


def with_circuit_breaker(circuit_breaker: CircuitBreaker):
    """Decorator to apply circuit breaker to Elasticsearch operations."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not circuit_breaker.can_execute():
                raise ConnectionError("Circuit breaker is OPEN - Elasticsearch unavailable")
            
            try:
                result = func(*args, **kwargs)
                circuit_breaker.record_success()
                return result
            except (TransportError, ConnectionError) as e:
                circuit_breaker.record_failure()
                raise e
        
        return wrapper
    return decorator


# Global circuit breaker instance
search_circuit_breaker = CircuitBreaker()
```

---

## 3. Index Mapping Design

### 3.1 Core Index Mappings

```python
# /app/search/index_mappings.py
"""
Elasticsearch index mappings for ResilienceAI search indices.
"""

from typing import Dict, Any


class IndexMappings:
    """Central repository for all Elasticsearch index mappings."""
    
    # Common analysis settings
    ANALYSIS_SETTINGS = {
        "analysis": {
            "analyzer": {
                # Standard analyzer with English stop words
                "resilience_standard": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer"
                    ]
                },
                # Autocomplete analyzer
                "autocomplete": {
                    "type": "custom",
                    "tokenizer": "autocomplete_tokenizer",
                    "filter": ["lowercase"]
                },
                # Autocomplete search analyzer
                "autocomplete_search": {
                    "type": "custom",
                    "tokenizer": "lowercase"
                },
                # N-gram analyzer for partial matching
                "ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "ngram_tokenizer",
                    "filter": ["lowercase"]
                },
                # Synonym-aware analyzer
                "synonym_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "synonym_filter",
                        "english_stemmer"
                    ]
                }
            },
            "tokenizer": {
                "autocomplete_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 20,
                    "token_chars": ["letter", "digit"]
                },
                "ngram_tokenizer": {
                    "type": "ngram",
                    "min_gram": 3,
                    "max_gram": 4,
                    "token_chars": ["letter", "digit"]
                }
            },
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "synonym_filter": {
                    "type": "synonym_graph",
                    "synonyms_path": "analysis/synonyms.txt",
                    "updateable": True
                }
            }
        }
    }
    
    # Incident index mapping
    @staticmethod
    def get_incident_mapping() -> Dict[str, Any]:
        return {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "refresh_interval": "5s",
                **IndexMappings.ANALYSIS_SETTINGS
            },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    # Core fields
                    "id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "resilience_standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {
                                "type": "text",
                                "analyzer": "autocomplete",
                                "search_analyzer": "autocomplete_search"
                            }
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "resilience_standard"
                    },
                    "status": {
                        "type": "keyword",
                        "fields": {
                            "text": {"type": "text"}
                        }
                    },
                    "severity": {
                        "type": "keyword",
                        "fields": {
                            "level": {"type": "byte"}
                        }
                    },
                    "category": {"type": "keyword"},
                    "subcategory": {"type": "keyword"},
                    
                    # Timestamps
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "resolved_at": {"type": "date"},
                    "occurred_at": {"type": "date"},
                    
                    # Location (geo-point for geo-search)
                    "location": {"type": "geo_point"},
                    "location_bounding_box": {"type": "geo_shape"},
                    "address": {
                        "properties": {
                            "street": {"type": "text"},
                            "city": {"type": "keyword"},
                            "state": {"type": "keyword"},
                            "country": {"type": "keyword"},
                            "postal_code": {"type": "keyword"}
                        }
                    },
                    
                    # Tags and labels
                    "tags": {
                        "type": "keyword",
                        "fields": {
                            "text": {"type": "text"}
                        }
                    },
                    "labels": {"type": "keyword"},
                    
                    # Relationships
                    "assigned_to": {"type": "keyword"},
                    "reported_by": {"type": "keyword"},
                    "organization_id": {"type": "keyword"},
                    "team_id": {"type": "keyword"},
                    
                    # Impact metrics
                    "impact_score": {"type": "float"},
                    "affected_users": {"type": "integer"},
                    "estimated_cost": {"type": "scaled_float", "scaling_factor": 100},
                    
                    # Nested objects
                    "comments": {
                        "type": "nested",
                        "properties": {
                            "id": {"type": "keyword"},
                            "text": {"type": "text", "analyzer": "resilience_standard"},
                            "author": {"type": "keyword"},
                            "created_at": {"type": "date"}
                        }
                    },
                    "attachments": {
                        "type": "nested",
                        "properties": {
                            "id": {"type": "keyword"},
                            "filename": {"type": "keyword"},
                            "content_type": {"type": "keyword"},
                            "size": {"type": "long"}
                        }
                    },
                    
                    # ML features
                    "ml_vector": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    },
                    "sentiment_score": {"type": "float"},
                    "priority_score": {"type": "float"}
                }
            }
        }
    
    # Resource index mapping
    @staticmethod
    def get_resource_mapping() -> Dict[str, Any]:
        return {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
                "refresh_interval": "10s",
                **IndexMappings.ANALYSIS_SETTINGS
            },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "analyzer": "resilience_standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {
                                "type": "text",
                                "analyzer": "autocomplete",
                                "search_analyzer": "autocomplete_search"
                            }
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "resilience_standard"
                    },
                    "type": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "availability_status": {"type": "keyword"},
                    "capacity": {"type": "integer"},
                    "current_utilization": {"type": "float"},
                    "location": {"type": "geo_point"},
                    "service_area": {"type": "geo_shape"},
                    "contact_info": {
                        "properties": {
                            "phone": {"type": "keyword"},
                            "email": {"type": "keyword"},
                            "website": {"type": "keyword"}
                        }
                    },
                    "operating_hours": {
                        "type": "nested",
                        "properties": {
                            "day": {"type": "keyword"},
                            "open": {"type": "keyword"},
                            "close": {"type": "keyword"},
                            "is_24h": {"type": "boolean"}
                        }
                    },
                    "capabilities": {"type": "keyword"},
                    "specializations": {"type": "keyword"},
                    "rating": {"type": "float"},
                    "review_count": {"type": "integer"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }
```

    # KB article mapping
    @staticmethod
    def get_kb_article_mapping() -> Dict[str, Any]:
        return {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
                "refresh_interval": "30s",
                **IndexMappings.ANALYSIS_SETTINGS
            },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "resilience_standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {
                                "type": "text",
                                "analyzer": "autocomplete",
                                "search_analyzer": "autocomplete_search"
                            }
                        }
                    },
                    "content": {"type": "text", "analyzer": "resilience_standard"},
                    "summary": {"type": "text", "analyzer": "resilience_standard"},
                    "slug": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "subcategory": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "author": {"type": "keyword"},
                    "organization_id": {"type": "keyword"},
                    "visibility": {"type": "keyword"},
                    "view_count": {"type": "long"},
                    "helpful_count": {"type": "integer"},
                    "not_helpful_count": {"type": "integer"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "published_at": {"type": "date"},
                    "related_articles": {"type": "keyword"},
                    "related_incidents": {"type": "keyword"},
                    "ml_vector": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
    
    # User mapping
    @staticmethod
    def get_user_mapping() -> Dict[str, Any]:
        return {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
                "refresh_interval": "10s",
                **IndexMappings.ANALYSIS_SETTINGS
            },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "email": {"type": "keyword"},
                    "username": {
                        "type": "text",
                        "analyzer": "resilience_standard",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "first_name": {
                        "type": "text",
                        "analyzer": "resilience_standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {"type": "text", "analyzer": "autocomplete"}
                        }
                    },
                    "last_name": {
                        "type": "text",
                        "analyzer": "resilience_standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {"type": "text", "analyzer": "autocomplete"}
                        }
                    },
                    "full_name": {
                        "type": "text",
                        "analyzer": "resilience_standard",
                        "fields": {
                            "suggest": {"type": "text", "analyzer": "autocomplete"}
                        }
                    },
                    "role": {"type": "keyword"},
                    "department": {"type": "keyword"},
                    "organization_id": {"type": "keyword"},
                    "team_ids": {"type": "keyword"},
                    "skills": {"type": "keyword"},
                    "location": {"type": "geo_point"},
                    "timezone": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "last_active_at": {"type": "date"}
                }
            }
        }


# Index configuration registry
INDEX_CONFIGS = {
    "incidents": IndexMappings.get_incident_mapping(),
    "resources": IndexMappings.get_resource_mapping(),
    "kb_articles": IndexMappings.get_kb_article_mapping(),
    "users": IndexMappings.get_user_mapping(),
}
```

### 3.2 Index Manager

```python
# /app/search/index_manager.py
"""Index management utilities for creating and managing Elasticsearch indices."""

from elasticsearch import Elasticsearch
from typing import Dict, Any, List, Optional
import logging

from .elasticsearch_client import ElasticsearchClient
from .index_mappings import INDEX_CONFIGS

logger = logging.getLogger(__name__)


class IndexManager:
    """Manage Elasticsearch indices lifecycle."""
    
    def __init__(self, client: Optional[Elasticsearch] = None):
        self.client = client or ElasticsearchClient.get_client()
    
    def create_index(self, index_name: str, mapping_config: Dict[str, Any]) -> bool:
        """Create a new index with specified mapping."""
        try:
            if self.client.indices.exists(index=index_name):
                logger.warning(f"Index '{index_name}' already exists")
                return False
            
            self.client.indices.create(index=index_name, body=mapping_config)
            logger.info(f"Created index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index '{index_name}': {e}")
            raise
    
    def create_all_indices(self) -> Dict[str, bool]:
        """Create all configured indices."""
        results = {}
        for index_name, mapping in INDEX_CONFIGS.items():
            results[index_name] = self.create_index(index_name, mapping)
        return results
    
    def delete_index(self, index_name: str) -> bool:
        """Delete an index."""
        try:
            if not self.client.indices.exists(index=index_name):
                logger.warning(f"Index '{index_name}' does not exist")
                return False
            
            self.client.indices.delete(index=index_name)
            logger.info(f"Deleted index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete index '{index_name}': {e}")
            raise
    
    def update_mapping(self, index_name: str, new_properties: Dict[str, Any]) -> bool:
        """Update index mapping with new properties."""
        try:
            self.client.indices.put_mapping(
                index=index_name,
                body={"properties": new_properties}
            )
            logger.info(f"Updated mapping for index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update mapping for '{index_name}': {e}")
            raise
    
    def get_mapping(self, index_name: str) -> Dict[str, Any]:
        """Get current mapping for an index."""
        return self.client.indices.get_mapping(index=index_name)
    
    def reindex(self, source_index: str, dest_index: str, 
                query: Optional[Dict] = None) -> Dict[str, Any]:
        """Reindex data from source to destination."""
        body = {
            "source": {"index": source_index},
            "dest": {"index": dest_index}
        }
        
        if query:
            body["source"]["query"] = query
        
        result = self.client.reindex(body=body, wait_for_completion=True)
        logger.info(f"Reindexed from '{source_index}' to '{dest_index}'")
        return result
    
    def optimize_index(self, index_name: str) -> None:
        """Optimize index settings for search performance."""
        self.client.indices.forcemerge(index=index_name, max_num_segments=1)
        self.client.indices.refresh(index=index_name)
        self.client.indices.clear_cache(index=index_name)
        logger.info(f"Optimized index: {index_name}")
    
    def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Get detailed statistics for an index."""
        stats = self.client.indices.stats(index=index_name)
        return {
            "docs_count": stats["indices"][index_name]["total"]["docs"]["count"],
            "store_size": stats["indices"][index_name]["total"]["store"]["size_in_bytes"],
            "indexing_rate": stats["indices"][index_name]["total"]["indexing"]["index_total"],
            "search_rate": stats["indices"][index_name]["total"]["search"]["query_total"],
        }
```

---

## 4. Full-Text Search Implementation

### 4.1 Search Service

```python
# /app/search/search_service.py
"""Full-text search service for ResilienceAI."""

from elasticsearch import Elasticsearch
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

from .elasticsearch_client import ElasticsearchClient
from .query_builder import QueryBuilder

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Standardized search result."""
    id: str
    score: float
    source: Dict[str, Any]
    highlights: Optional[Dict[str, List[str]]] = None


@dataclass
class SearchResponse:
    """Complete search response with metadata."""
    total: int
    took_ms: int
    results: List[SearchResult]
    aggregations: Optional[Dict[str, Any]] = None
    suggestions: Optional[Dict[str, Any]] = None
    page: int = 1
    per_page: int = 20


class SearchService:
    """Main search service for all ResilienceAI entities."""
    
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    def __init__(self, client: Optional[Elasticsearch] = None):
        self.client = client or ElasticsearchClient.get_client()
        self.query_builder = QueryBuilder()
    
    def search_incidents(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        page: int = 1,
        per_page: int = DEFAULT_PAGE_SIZE,
        highlight: bool = True,
        aggregations: Optional[Dict[str, Any]] = None
    ) -> SearchResponse:
        """Search incidents with full-text and faceted capabilities."""
        search_body = self.query_builder.build_search_query(
            query=query,
            filters=filters,
            sort=sort or [{"created_at": "desc"}],
            highlight_fields=["title", "description"] if highlight else None,
            aggregations=aggregations
        )
        
        from_offset = (page - 1) * min(per_page, self.MAX_PAGE_SIZE)
        
        response = self.client.search(
            index="incidents",
            body=search_body,
            from_=from_offset,
            size=min(per_page, self.MAX_PAGE_SIZE),
            track_total_hits=True
        )
        
        return self._parse_response(response, page, per_page)
    
    def search_resources(
        self,
        query: Optional[str] = None,
        location: Optional[Tuple[float, float]] = None,
        radius_km: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = DEFAULT_PAGE_SIZE
    ) -> SearchResponse:
        """Search resources with optional geo-filtering."""
        search_body = self.query_builder.build_resource_query(
            query=query,
            location=location,
            radius_km=radius_km,
            filters=filters
        )
        
        from_offset = (page - 1) * min(per_page, self.MAX_PAGE_SIZE)
        
        response = self.client.search(
            index="resources",
            body=search_body,
            from_=from_offset,
            size=min(per_page, self.MAX_PAGE_SIZE),
            track_total_hits=True
        )
        
        return self._parse_response(response, page, per_page)
    
    def search_kb_articles(
        self,
        query: str,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = DEFAULT_PAGE_SIZE
    ) -> SearchResponse:
        """Search knowledge base articles."""
        filters = {"category": category} if category else None
        
        search_body = self.query_builder.build_search_query(
            query=query,
            filters=filters,
            sort=[{"_score": "desc"}, {"view_count": "desc"}],
            highlight_fields=["title", "content", "summary"]
        )
        
        from_offset = (page - 1) * min(per_page, self.MAX_PAGE_SIZE)
        
        response = self.client.search(
            index="kb_articles",
            body=search_body,
            from_=from_offset,
            size=min(per_page, self.MAX_PAGE_SIZE),
            track_total_hits=True
        )
        
        return self._parse_response(response, page, per_page)
    
    def semantic_search(
        self,
        query_vector: List[float],
        index: str = "kb_articles",
        k: int = 10,
        min_score: float = 0.7
    ) -> SearchResponse:
        """Perform semantic search using vector similarity."""
        search_body = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'ml_vector') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            },
            "min_score": min_score
        }
        
        response = self.client.search(
            index=index,
            body=search_body,
            size=k,
            track_total_hits=True
        )
        
        return self._parse_response(response, 1, k)
    
    def multi_search(
        self,
        query: str,
        indices: List[str] = None
    ) -> Dict[str, SearchResponse]:
        """Search across multiple indices simultaneously."""
        indices = indices or ["incidents", "resources", "kb_articles"]
        
        msearch_body = []
        for index in indices:
            msearch_body.append({"index": index})
            msearch_body.append({
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "description", "content", "tags"],
                        "type": "best_fields"
                    }
                },
                "size": 5
            })
        
        responses = self.client.msearch(body=msearch_body)
        
        results = {}
        for i, index in enumerate(indices):
            response = responses["responses"][i]
            results[index] = self._parse_response(response, 1, 5)
        
        return results
    
    def _parse_response(
        self,
        response: Dict[str, Any],
        page: int,
        per_page: int
    ) -> SearchResponse:
        """Parse Elasticsearch response into SearchResponse."""
        hits = response.get("hits", {})
        total = hits.get("total", {}).get("value", 0)
        
        results = []
        for hit in hits.get("hits", []):
            result = SearchResult(
                id=hit["_id"],
                score=hit["_score"],
                source=hit["_source"],
                highlights=hit.get("highlight")
            )
            results.append(result)
        
        return SearchResponse(
            total=total,
            took_ms=response.get("took", 0),
            results=results,
            aggregations=response.get("aggregations"),
            suggestions=response.get("suggest"),
            page=page,
            per_page=per_page
        )
```

### 4.2 Query Builder

```python
# /app/search/query_builder.py
"""Query builder for constructing Elasticsearch queries."""

from typing import Dict, Any, List, Optional, Tuple


class QueryBuilder:
    """Build complex Elasticsearch queries."""
    
    def build_search_query(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        highlight_fields: Optional[List[str]] = None,
        aggregations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build a complete search query."""
        search_body = {}
        
        if query:
            search_body["query"] = self._build_text_query(query)
        else:
            search_body["query"] = {"match_all": {}}
        
        if filters:
            filter_clauses = self._build_filters(filters)
            if filter_clauses:
                search_body["query"] = {
                    "bool": {
                        "must": search_body["query"],
                        "filter": filter_clauses
                    }
                }
        
        if sort:
            search_body["sort"] = sort
        
        if highlight_fields:
            search_body["highlight"] = self._build_highlight(highlight_fields)
        
        if aggregations:
            search_body["aggs"] = aggregations
        
        return search_body
    
    def _build_text_query(self, query: str) -> Dict[str, Any]:
        """Build full-text query with boosting."""
        return {
            "multi_match": {
                "query": query,
                "fields": [
                    "title^5",
                    "title.suggest^3",
                    "description^2",
                    "content",
                    "tags^2",
                    "comments.text"
                ],
                "type": "best_fields",
                "fuzziness": "AUTO",
                "prefix_length": 2,
                "max_expansions": 50
            }
        }
    
    def _build_filters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build filter clauses from filter dictionary."""
        filter_clauses = []
        
        for field, value in filters.items():
            if value is None:
                continue
            
            if field == "date_range":
                filter_clauses.append(self._build_date_range_filter(value))
            elif field == "geo_distance":
                filter_clauses.append(self._build_geo_filter(value))
            elif field == "geo_bounding_box":
                filter_clauses.append(self._build_geo_bounding_filter(value))
            elif isinstance(value, list):
                filter_clauses.append({"terms": {field: value}})
            elif isinstance(value, dict):
                filter_clauses.append({"range": {field: value}})
            else:
                filter_clauses.append({"term": {field: value}})
        
        return filter_clauses
    
    def _build_date_range_filter(self, date_range: Dict[str, Any]) -> Dict[str, Any]:
        """Build date range filter."""
        field = date_range.get("field", "created_at")
        range_spec = {}
        if "from" in date_range:
            range_spec["gte"] = date_range["from"]
        if "to" in date_range:
            range_spec["lte"] = date_range["to"]
        return {"range": {field: range_spec}}
    
    def _build_geo_filter(self, geo_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Build geo-distance filter."""
        return {
            "geo_distance": {
                "distance": geo_spec.get("distance", "10km"),
                "location": {
                    "lat": geo_spec["lat"],
                    "lon": geo_spec["lon"]
                }
            }
        }
    
    def _build_geo_bounding_filter(self, bbox: Dict[str, Any]) -> Dict[str, Any]:
        """Build geo-bounding box filter."""
        return {
            "geo_bounding_box": {
                "location": {
                    "top_left": {"lat": bbox["top"], "lon": bbox["left"]},
                    "bottom_right": {"lat": bbox["bottom"], "lon": bbox["right"]}
                }
            }
        }
    
    def _build_highlight(self, fields: List[str]) -> Dict[str, Any]:
        """Build highlight configuration."""
        highlight_fields = {}
        for field in fields:
            highlight_fields[field] = {
                "fragment_size": 150,
                "number_of_fragments": 3,
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"]
            }
        
        return {
            "fields": highlight_fields,
            "require_field_match": False,
            "max_analyzed_offset": 1000000
        }
    
    def build_resource_query(
        self,
        query: Optional[str] = None,
        location: Optional[Tuple[float, float]] = None,
        radius_km: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build query for resource search with geo support."""
        search_body = {}
        must_clauses = []
        filter_clauses = []
        
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["name^4", "description^2", "capabilities", "specializations"],
                    "type": "best_fields"
                }
            })
        
        if location and radius_km:
            filter_clauses.append({
                "geo_distance": {
                    "distance": f"{radius_km}km",
                    "location": {"lat": location[0], "lon": location[1]}
                }
            })
        
        if filters:
            filter_clauses.extend(self._build_filters(filters))
        
        if must_clauses or filter_clauses:
            search_body["query"] = {"bool": {}}
            if must_clauses:
                search_body["query"]["bool"]["must"] = must_clauses
            if filter_clauses:
                search_body["query"]["bool"]["filter"] = filter_clauses
        else:
            search_body["query"] = {"match_all": {}}
        
        if location:
            search_body["sort"] = [
                {
                    "_geo_distance": {
                        "location": {"lat": location[0], "lon": location[1]},
                        "order": "asc",
                        "unit": "km"
                    }
                },
                "_score"
            ]
        
        return search_body
```


---

## 5. Faceted Search Design

### 5.1 Facet Configuration

```python
# /app/search/faceted_search.py
"""Faceted search implementation for ResilienceAI."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class FacetValue:
    """Single facet value with count."""
    value: str
    count: int
    selected: bool = False


@dataclass
class Facet:
    """Facet definition with values."""
    name: str
    field: str
    type: str
    values: List[FacetValue]
    multi_select: bool = False


class FacetConfiguration:
    """Predefined facet configurations for each entity type."""
    
    INCIDENT_FACETS = {
        "status": {
            "type": "terms",
            "field": "status",
            "size": 10,
            "multi_select": False
        },
        "severity": {
            "type": "terms",
            "field": "severity",
            "size": 5,
            "order": {"_key": "asc"},
            "multi_select": False
        },
        "category": {
            "type": "terms",
            "field": "category",
            "size": 20,
            "multi_select": True
        },
        "tags": {
            "type": "terms",
            "field": "tags",
            "size": 30,
            "multi_select": True
        },
        "created_date": {
            "type": "date_histogram",
            "field": "created_at",
            "calendar_interval": "day",
            "format": "yyyy-MM-dd"
        },
        "assigned_to": {
            "type": "terms",
            "field": "assigned_to",
            "size": 20
        },
        "impact_score_range": {
            "type": "range",
            "field": "impact_score",
            "ranges": [
                {"to": 25, "key": "low"},
                {"from": 25, "to": 50, "key": "medium"},
                {"from": 50, "to": 75, "key": "high"},
                {"from": 75, "key": "critical"}
            ]
        }
    }
    
    RESOURCE_FACETS = {
        "type": {"type": "terms", "field": "type", "size": 15},
        "category": {"type": "terms", "field": "category", "size": 20},
        "availability_status": {"type": "terms", "field": "availability_status", "size": 5},
        "capabilities": {"type": "terms", "field": "capabilities", "size": 30, "multi_select": True},
        "rating_range": {
            "type": "range",
            "field": "rating",
            "ranges": [
                {"to": 2, "key": "below_2"},
                {"from": 2, "to": 3, "key": "2_to_3"},
                {"from": 3, "to": 4, "key": "3_to_4"},
                {"from": 4, "key": "above_4"}
            ]
        },
        "geo_distance": {
            "type": "geo_distance",
            "field": "location",
            "origin": None,
            "unit": "km",
            "ranges": [
                {"to": 5, "key": "within_5km"},
                {"from": 5, "to": 25, "key": "5_to_25km"},
                {"from": 25, "to": 50, "key": "25_to_50km"},
                {"from": 50, "key": "over_50km"}
            ]
        }
    }
    
    KB_ARTICLE_FACETS = {
        "category": {"type": "terms", "field": "category", "size": 20},
        "tags": {"type": "terms", "field": "tags", "size": 30, "multi_select": True},
        "author": {"type": "terms", "field": "author", "size": 20},
        "visibility": {"type": "terms", "field": "visibility", "size": 5},
        "published_date": {
            "type": "date_histogram",
            "field": "published_at",
            "calendar_interval": "month",
            "format": "yyyy-MM"
        }
    }


class FacetedSearchService:
    """Service for executing faceted searches."""
    
    def __init__(self, client):
        self.client = client
    
    def build_facet_aggregations(
        self,
        facet_configs: Dict[str, Any],
        active_filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build aggregation queries for facets."""
        aggregations = {}
        
        for facet_name, config in facet_configs.items():
            agg_type = config["type"]
            field = config["field"]
            
            if agg_type == "terms":
                aggregations[facet_name] = {
                    "terms": {
                        "field": field,
                        "size": config.get("size", 10),
                        **({"order": config["order"]} if "order" in config else {})
                    }
                }
            elif agg_type == "range":
                aggregations[facet_name] = {
                    "range": {"field": field, "ranges": config["ranges"]}
                }
            elif agg_type == "date_histogram":
                aggregations[facet_name] = {
                    "date_histogram": {
                        "field": field,
                        "calendar_interval": config["calendar_interval"],
                        "format": config.get("format", "yyyy-MM-dd")
                    }
                }
            elif agg_type == "geo_distance" and config.get("origin"):
                aggregations[facet_name] = {
                    "geo_distance": {
                        "field": field,
                        "origin": config["origin"],
                        "unit": config.get("unit", "km"),
                        "ranges": config["ranges"]
                    }
                }
        
        return aggregations
    
    def parse_facet_results(
        self,
        aggregations: Dict[str, Any],
        active_filters: Optional[Dict[str, List[str]]] = None
    ) -> List[Facet]:
        """Parse aggregation results into Facet objects."""
        facets = []
        active_filters = active_filters or {}
        
        for facet_name, agg_result in aggregations.items():
            values = []
            
            if "buckets" in agg_result:
                for bucket in agg_result["buckets"]:
                    value = bucket.get("key_as_string", bucket["key"])
                    count = bucket["doc_count"]
                    selected = value in active_filters.get(facet_name, [])
                    values.append(FacetValue(value, count, selected))
            
            facet = Facet(
                name=facet_name,
                field=facet_name,
                type="terms",
                values=values
            )
            facets.append(facet)
        
        return facets
    
    def search_with_facets(
        self,
        index: str,
        query: Optional[str],
        facet_configs: Dict[str, Any],
        active_filters: Optional[Dict[str, List[str]]] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Execute search with faceted navigation."""
        aggregations = self.build_facet_aggregations(facet_configs, active_filters)
        
        post_filter = None
        if active_filters:
            filter_clauses = []
            for field, values in active_filters.items():
                if values:
                    filter_clauses.append({"terms": {field: values}})
            
            if filter_clauses:
                post_filter = {"bool": {"must": filter_clauses}}
        
        search_body = {"aggs": aggregations}
        
        if query:
            search_body["query"] = {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "description", "content"],
                    "type": "best_fields"
                }
            }
        else:
            search_body["query"] = {"match_all": {}}
        
        if post_filter:
            search_body["post_filter"] = post_filter
        
        response = self.client.search(
            index=index,
            body=search_body,
            from_=(page - 1) * per_page,
            size=per_page,
            track_total_hits=True
        )
        
        facets = self.parse_facet_results(
            response.get("aggregations", {}),
            active_filters
        )
        
        return {
            "total": response["hits"]["total"]["value"],
            "results": [hit["_source"] for hit in response["hits"]["hits"]],
            "facets": facets,
            "page": page,
            "per_page": per_page
        }
```

---

## 6. Geospatial Search

### 6.1 Geo Search Service

```python
# /app/search/geo_search.py
"""Geospatial search capabilities for ResilienceAI."""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class GeoPoint:
    """Geographic point with latitude and longitude."""
    lat: float
    lon: float


@dataclass
class GeoBoundingBox:
    """Geographic bounding box."""
    top_left: GeoPoint
    bottom_right: GeoPoint


@dataclass
class GeoSearchResult:
    """Geo search result with distance."""
    id: str
    source: Dict[str, Any]
    distance_km: float
    location: GeoPoint


class GeoSearchService:
    """Service for geospatial search operations."""
    
    EARTH_RADIUS_KM = 6371
    
    def __init__(self, client):
        self.client = client
    
    def search_nearby(
        self,
        index: str,
        location: GeoPoint,
        radius_km: float = 10,
        query: Optional[str] = None,
        size: int = 50
    ) -> List[GeoSearchResult]:
        """Search for items within a radius of a location."""
        search_body = {
            "query": {
                "bool": {
                    "must": {"match_all": {}},
                    "filter": {
                        "geo_distance": {
                            "distance": f"{radius_km}km",
                            "location": {"lat": location.lat, "lon": location.lon}
                        }
                    }
                }
            },
            "sort": [
                {
                    "_geo_distance": {
                        "location": {"lat": location.lat, "lon": location.lon},
                        "order": "asc",
                        "unit": "km"
                    }
                }
            ]
        }
        
        if query:
            search_body["query"]["bool"]["must"] = {
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "description", "capabilities"]
                }
            }
        
        response = self.client.search(index=index, body=search_body, size=size)
        
        results = []
        for hit in response["hits"]["hits"]:
            distance_km = hit.get("sort", [0])[0]
            
            result = GeoSearchResult(
                id=hit["_id"],
                source=hit["_source"],
                distance_km=distance_km,
                location=GeoPoint(
                    lat=hit["_source"]["location"]["lat"],
                    lon=hit["_source"]["location"]["lon"]
                )
            )
            results.append(result)
        
        return results
    
    def search_in_bounding_box(
        self,
        index: str,
        bbox: GeoBoundingBox,
        query: Optional[str] = None,
        size: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for items within a bounding box."""
        search_body = {
            "query": {
                "bool": {
                    "must": {"match_all": {}},
                    "filter": {
                        "geo_bounding_box": {
                            "location": {
                                "top_left": {"lat": bbox.top_left.lat, "lon": bbox.top_left.lon},
                                "bottom_right": {"lat": bbox.bottom_right.lat, "lon": bbox.bottom_right.lon}
                            }
                        }
                    }
                }
            }
        }
        
        if query:
            search_body["query"]["bool"]["must"] = {
                "multi_match": {"query": query, "fields": ["name^3", "description"]}
            }
        
        response = self.client.search(index=index, body=search_body, size=size)
        return [hit["_source"] for hit in response["hits"]["hits"]]
    
    def search_in_polygon(
        self,
        index: str,
        polygon_points: List[GeoPoint],
        query: Optional[str] = None,
        size: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for items within a polygon."""
        coordinates = [[p.lon, p.lat] for p in polygon_points]
        coordinates.append(coordinates[0])  # Close the polygon
        
        search_body = {
            "query": {
                "bool": {
                    "must": {"match_all": {}},
                    "filter": {"geo_polygon": {"location": {"points": coordinates}}}
                }
            }
        }
        
        if query:
            search_body["query"]["bool"]["must"] = {
                "multi_match": {"query": query, "fields": ["name^3", "description"]}
            }
        
        response = self.client.search(index=index, body=search_body, size=size)
        return [hit["_source"] for hit in response["hits"]["hits"]]
    
    def get_distance_aggregation(
        self,
        index: str,
        location: GeoPoint,
        ranges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get count of items in distance ranges from a point."""
        search_body = {
            "size": 0,
            "aggs": {
                "distance_ranges": {
                    "geo_distance": {
                        "field": "location",
                        "origin": {"lat": location.lat, "lon": location.lon},
                        "unit": "km",
                        "ranges": ranges
                    }
                }
            }
        }
        
        response = self.client.search(index=index, body=search_body)
        return response["aggregations"]["distance_ranges"]
    
    def get_geohash_grid(
        self,
        index: str,
        precision: int = 5,
        bbox: Optional[GeoBoundingBox] = None
    ) -> List[Dict[str, Any]]:
        """Get geohash grid aggregation for clustering."""
        search_body = {
            "size": 0,
            "aggs": {
                "grid": {
                    "geohash_grid": {"field": "location", "precision": precision},
                    "aggs": {"center": {"geo_centroid": {"field": "location"}}}
                }
            }
        }
        
        if bbox:
            search_body["query"] = {
                "geo_bounding_box": {
                    "location": {
                        "top_left": {"lat": bbox.top_left.lat, "lon": bbox.top_left.lon},
                        "bottom_right": {"lat": bbox.bottom_right.lat, "lon": bbox.bottom_right.lon}
                    }
                }
            }
        
        response = self.client.search(index=index, body=search_body)
        
        buckets = []
        for bucket in response["aggregations"]["grid"]["buckets"]:
            buckets.append({
                "geohash": bucket["key"],
                "count": bucket["doc_count"],
                "center": {
                    "lat": bucket["center"]["location"]["lat"],
                    "lon": bucket["center"]["location"]["lon"]
                }
            })
        
        return buckets
    
    @staticmethod
    def calculate_distance(point1: GeoPoint, point2: GeoPoint) -> float:
        """Calculate distance between two points using Haversine formula."""
        lat1, lon1 = math.radians(point1.lat), math.radians(point1.lon)
        lat2, lon2 = math.radians(point2.lat), math.radians(point2.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return GeoSearchService.EARTH_RADIUS_KM * c
```

---

## 7. Query DSL Reference

### 7.1 Common Query Patterns

```python
# /app/search/query_dsl_reference.py
"""Query DSL reference and common patterns for ResilienceAI search."""

from typing import Dict, Any, List, Optional


class QueryDSLPatterns:
    """Common Elasticsearch query patterns."""
    
    @staticmethod
    def match_query(field: str, value: str, operator: str = "or") -> Dict[str, Any]:
        """Basic match query."""
        return {"match": {field: {"query": value, "operator": operator}}}
    
    @staticmethod
    def multi_match_query(query: str, fields: List[str], query_type: str = "best_fields") -> Dict[str, Any]:
        """Multi-field match query."""
        return {"multi_match": {"query": query, "fields": fields, "type": query_type}}
    
    @staticmethod
    def match_phrase_query(field: str, phrase: str, slop: int = 0) -> Dict[str, Any]:
        """Match phrase query for exact phrase matching."""
        return {"match_phrase": {field: {"query": phrase, "slop": slop}}}
    
    @staticmethod
    def term_query(field: str, value: Any) -> Dict[str, Any]:
        """Exact term query."""
        return {"term": {field: value}}
    
    @staticmethod
    def terms_query(field: str, values: List[Any]) -> Dict[str, Any]:
        """Multiple terms query."""
        return {"terms": {field: values}}
    
    @staticmethod
    def range_query(
        field: str,
        gte: Optional[Any] = None,
        gt: Optional[Any] = None,
        lte: Optional[Any] = None,
        lt: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Range query."""
        range_spec = {}
        if gte is not None: range_spec["gte"] = gte
        if gt is not None: range_spec["gt"] = gt
        if lte is not None: range_spec["lte"] = lte
        if lt is not None: range_spec["lt"] = lt
        return {"range": {field: range_spec}}
    
    @staticmethod
    def bool_query(
        must: Optional[List[Dict]] = None,
        should: Optional[List[Dict]] = None,
        must_not: Optional[List[Dict]] = None,
        filter: Optional[List[Dict]] = None,
        minimum_should_match: Optional[int] = None
    ) -> Dict[str, Any]:
        """Boolean query combining multiple clauses."""
        bool_query = {}
        if must: bool_query["must"] = must
        if should: bool_query["should"] = should
        if must_not: bool_query["must_not"] = must_not
        if filter: bool_query["filter"] = filter
        if minimum_should_match is not None: bool_query["minimum_should_match"] = minimum_should_match
        return {"bool": bool_query}
    
    @staticmethod
    def geo_distance_query(field: str, lat: float, lon: float, distance: str) -> Dict[str, Any]:
        """Geo distance query."""
        return {"geo_distance": {"distance": distance, field: {"lat": lat, "lon": lon}}}
    
    @staticmethod
    def geo_bounding_box_query(field: str, top_left: Dict[str, float], bottom_right: Dict[str, float]) -> Dict[str, Any]:
        """Geo bounding box query."""
        return {"geo_bounding_box": {field: {"top_left": top_left, "bottom_right": bottom_right}}}
    
    @staticmethod
    def nested_query(path: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Nested document query."""
        return {"nested": {"path": path, "query": query}}
    
    @staticmethod
    def query_string_query(query: str, fields: Optional[List[str]] = None, default_operator: str = "OR") -> Dict[str, Any]:
        """Query string query for advanced search syntax."""
        qs = {"query_string": {"query": query, "default_operator": default_operator}}
        if fields: qs["query_string"]["fields"] = fields
        return qs
    
    @staticmethod
    def script_score_query(query: Dict[str, Any], script: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Script score query for custom scoring."""
        script_score = {"script_score": {"query": query, "script": {"source": script}}}
        if params: script_score["script_score"]["script"]["params"] = params
        return script_score
```


---

## 8. Search Relevance Tuning

### 8.1 Relevance Configuration

```python
# /app/search/relevance_tuning.py
"""Search relevance tuning for ResilienceAI."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class FieldBoost:
    """Field boost configuration."""
    field: str
    boost: float
    match_type: str = "best_fields"


class RelevanceConfig:
    """Relevance tuning configurations."""
    
    INCIDENT_FIELD_BOOSTS = [
        FieldBoost("title", 5.0),
        FieldBoost("title.suggest", 3.0),
        FieldBoost("description", 2.0),
        FieldBoost("tags", 2.0),
        FieldBoost("comments.text", 1.0),
    ]
    
    RESOURCE_FIELD_BOOSTS = [
        FieldBoost("name", 4.0),
        FieldBoost("description", 2.0),
        FieldBoost("capabilities", 1.5),
        FieldBoost("specializations", 1.5),
        FieldBoost("address.city", 1.0),
    ]
    
    KB_ARTICLE_FIELD_BOOSTS = [
        FieldBoost("title", 5.0),
        FieldBoost("summary", 3.0),
        FieldBoost("content", 1.0),
        FieldBoost("tags", 2.0),
    ]
    
    FUNCTION_SCORES = {
        "recency_boost": {
            "gauss": {
                "created_at": {
                    "origin": "now",
                    "scale": "7d",
                    "offset": "1d",
                    "decay": 0.5
                }
            }
        },
        "popularity_boost": {
            "field_value_factor": {
                "field": "view_count",
                "factor": 1.2,
                "modifier": "log1p",
                "missing": 1
            }
        },
        "rating_boost": {
            "field_value_factor": {
                "field": "rating",
                "factor": 1.5,
                "modifier": "sqrt",
                "missing": 3
            }
        }
    }


class RelevanceTuner:
    """Tune search relevance dynamically."""
    
    def __init__(self):
        self.config = RelevanceConfig()
    
    def build_boosted_query(self, query: str, field_boosts: List[FieldBoost], fuzziness: str = "AUTO") -> Dict[str, Any]:
        """Build a multi-match query with field boosts."""
        fields = [f"{fb.field}^{fb.boost}" for fb in field_boosts]
        
        return {
            "multi_match": {
                "query": query,
                "fields": fields,
                "type": "best_fields",
                "fuzziness": fuzziness,
                "prefix_length": 2,
                "max_expansions": 50
            }
        }
    
    def build_function_score_query(
        self,
        query: Dict[str, Any],
        functions: List[Dict[str, Any]],
        score_mode: str = "sum",
        boost_mode: str = "multiply"
    ) -> Dict[str, Any]:
        """Build a function score query."""
        return {
            "function_score": {
                "query": query,
                "functions": functions,
                "score_mode": score_mode,
                "boost_mode": boost_mode
            }
        }
    
    def build_incident_search_query(
        self,
        query: str,
        include_recency_boost: bool = True,
        include_popularity_boost: bool = False
    ) -> Dict[str, Any]:
        """Build optimized incident search query."""
        base_query = self.build_boosted_query(query, self.config.INCIDENT_FIELD_BOOSTS)
        
        functions = []
        if include_recency_boost:
            functions.append(self.config.FUNCTION_SCORES["recency_boost"])
        if include_popularity_boost:
            functions.append(self.config.FUNCTION_SCORES["popularity_boost"])
        
        if functions:
            return self.build_function_score_query(base_query, functions)
        
        return base_query
    
    def build_resource_search_query(
        self,
        query: str,
        location: Optional[tuple] = None,
        radius_km: float = 50
    ) -> Dict[str, Any]:
        """Build optimized resource search query with geo boost."""
        base_query = self.build_boosted_query(query, self.config.RESOURCE_FIELD_BOOSTS)
        
        functions = [self.config.FUNCTION_SCORES["rating_boost"]]
        
        if location:
            functions.append({
                "gauss": {
                    "location": {
                        "origin": {"lat": location[0], "lon": location[1]},
                        "scale": f"{radius_km}km",
                        "decay": 0.33
                    }
                }
            })
        
        return self.build_function_score_query(base_query, functions)
    
    def get_search_explanation(self, client, index: str, query: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        """Get explanation of why a document matched."""
        response = client.explain(index=index, id=doc_id, body={"query": query})
        
        return {
            "matched": response["matched"],
            "explanation": response["explanation"],
            "value": response.get("explanation", {}).get("value", 0)
        }
```

---

## 9. Autocomplete Implementation

### 9.1 Suggest Service

```python
# /app/search/suggest_service.py
"""Autocomplete and suggestion service for ResilienceAI."""

from elasticsearch import Elasticsearch
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SuggestService:
    """Service for autocomplete and search suggestions."""
    
    def __init__(self, client: Elasticsearch):
        self.client = client
    
    def autocomplete_incidents(self, prefix: str, size: int = 10) -> List[Dict[str, Any]]:
        """Autocomplete incident titles."""
        search_body = {
            "suggest": {
                "incident-suggest": {
                    "prefix": prefix,
                    "completion": {
                        "field": "title.suggest",
                        "size": size,
                        "fuzzy": {"fuzziness": "AUTO", "min_length": 3}
                    }
                }
            }
        }
        
        response = self.client.search(index="incidents", body=search_body)
        
        suggestions = []
        for option in response["suggest"]["incident-suggest"][0]["options"]:
            suggestions.append({
                "text": option["text"],
                "score": option["_score"],
                "source": option.get("_source", {})
            })
        
        return suggestions
    
    def search_as_you_type(
        self,
        query: str,
        index: str = "incidents",
        fields: List[str] = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Search-as-you-type using edge n-grams."""
        fields = fields or ["title.suggest", "name.suggest"]
        
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": fields,
                    "type": "phrase_prefix"
                }
            },
            "_source": ["title", "name", "id", "status"],
            "size": size
        }
        
        response = self.client.search(index=index, body=search_body)
        
        return [
            {"id": hit["_id"], "score": hit["_score"], **hit["_source"]}
            for hit in response["hits"]["hits"]
        ]
    
    def get_search_suggestions(
        self,
        query: str,
        indices: List[str] = None,
        size_per_index: int = 5
    ) -> Dict[str, List[Dict]]:
        """Get suggestions from multiple indices."""
        indices = indices or ["incidents", "resources", "kb_articles"]
        
        msearch_body = []
        for idx in indices:
            msearch_body.append({"index": idx})
            msearch_body.append({
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^2", "name^2", "tags"],
                        "type": "best_fields"
                    }
                },
                "_source": ["title", "name", "id", "category"],
                "size": size_per_index
            })
        
        responses = self.client.msearch(body=msearch_body)
        
        results = {}
        for i, idx in enumerate(indices):
            response = responses["responses"][i]
            results[idx] = [
                {
                    "id": hit["_id"],
                    "text": hit["_source"].get("title") or hit["_source"].get("name"),
                    "category": hit["_source"].get("category"),
                    "score": hit["_score"]
                }
                for hit in response["hits"]["hits"]
            ]
        
        return results
    
    def get_did_you_mean(self, query: str, index: str = "incidents") -> Optional[str]:
        """Suggest corrected spelling using phrase suggester."""
        search_body = {
            "suggest": {
                "text": query,
                "did-you-mean": {
                    "phrase": {
                        "field": "title",
                        "size": 1,
                        "direct_generator": [
                            {"field": "title", "suggest_mode": "always", "min_word_length": 3}
                        ],
                        "highlight": {"pre_tag": "<em>", "post_tag": "</em>"}
                    }
                }
            }
        }
        
        response = self.client.search(index=index, body=search_body)
        
        suggestions = response["suggest"]["did-you-mean"][0]["options"]
        if suggestions:
            return suggestions[0]["text"]
        
        return None
    
    def get_category_suggestions(self, query: str, size: int = 5) -> List[Dict[str, Any]]:
        """Suggest categories based on query."""
        search_body = {
            "query": {
                "multi_match": {"query": query, "fields": ["title", "description", "tags"]}
            },
            "aggs": {"categories": {"terms": {"field": "category", "size": size}}},
            "size": 0
        }
        
        response = self.client.search(index="incidents", body=search_body)
        
        return [
            {"category": bucket["key"], "count": bucket["doc_count"]}
            for bucket in response["aggregations"]["categories"]["buckets"]
        ]
```

---

## 10. Search Analytics

### 10.1 Analytics Service

```python
# /app/search/analytics_service.py
"""Search analytics and monitoring for ResilienceAI."""

from elasticsearch import Elasticsearch
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SearchEvent:
    """Search event for analytics."""
    timestamp: datetime
    query: str
    user_id: Optional[str]
    session_id: str
    results_count: int
    response_time_ms: int
    clicked_results: List[str]
    filters_used: Dict[str, Any]
    index: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "query": self.query,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "results_count": self.results_count,
            "response_time_ms": self.response_time_ms,
            "clicked_results": self.clicked_results,
            "filters_used": self.filters_used,
            "index": self.index
        }


class SearchAnalyticsService:
    """Service for tracking and analyzing search behavior."""
    
    ANALYTICS_INDEX = "search_analytics"
    
    def __init__(self, client: Elasticsearch):
        self.client = client
        self._ensure_index()
    
    def _ensure_index(self):
        """Ensure analytics index exists."""
        if not self.client.indices.exists(index=self.ANALYTICS_INDEX):
            mapping = {
                "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "query": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "user_id": {"type": "keyword"},
                        "session_id": {"type": "keyword"},
                        "results_count": {"type": "integer"},
                        "response_time_ms": {"type": "integer"},
                        "clicked_results": {"type": "keyword"},
                        "filters_used": {"type": "object"},
                        "index": {"type": "keyword"}
                    }
                }
            }
            self.client.indices.create(index=self.ANALYTICS_INDEX, body=mapping)
    
    def track_search(self, event: SearchEvent) -> None:
        """Track a search event."""
        try:
            self.client.index(index=self.ANALYTICS_INDEX, body=event.to_dict())
        except Exception as e:
            logger.error(f"Failed to track search event: {e}")
    
    def track_click(
        self,
        query: str,
        doc_id: str,
        position: int,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """Track a click on a search result."""
        click_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "click",
            "query": query,
            "doc_id": doc_id,
            "position": position,
            "user_id": user_id,
            "session_id": session_id
        }
        
        try:
            self.client.index(index=self.ANALYTICS_INDEX, body=click_event)
        except Exception as e:
            logger.error(f"Failed to track click event: {e}")
    
    def get_popular_queries(self, days: int = 7, size: int = 20) -> List[Dict[str, Any]]:
        """Get most popular search queries."""
        search_body = {
            "query": {"range": {"timestamp": {"gte": f"now-{days}d/d"}}},
            "aggs": {
                "popular_queries": {
                    "terms": {"field": "query.keyword", "size": size, "order": {"_count": "desc"}}
                }
            },
            "size": 0
        }
        
        response = self.client.search(index=self.ANALYTICS_INDEX, body=search_body)
        
        return [
            {"query": bucket["key"], "count": bucket["doc_count"]}
            for bucket in response["aggregations"]["popular_queries"]["buckets"]
        ]
    
    def get_zero_result_queries(self, days: int = 7, size: int = 20) -> List[Dict[str, Any]]:
        """Get queries with zero results."""
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": f"now-{days}d/d"}}},
                        {"term": {"results_count": 0}}
                    ]
                }
            },
            "aggs": {"zero_result_queries": {"terms": {"field": "query.keyword", "size": size}}},
            "size": 0
        }
        
        response = self.client.search(index=self.ANALYTICS_INDEX, body=search_body)
        
        return [
            {"query": bucket["key"], "count": bucket["doc_count"]}
            for bucket in response["aggregations"]["zero_result_queries"]["buckets"]
        ]
    
    def get_click_through_rate(self, days: int = 7) -> Dict[str, float]:
        """Calculate click-through rate metrics."""
        search_body = {
            "query": {"range": {"timestamp": {"gte": f"now-{days}d/d"}}},
            "aggs": {
                "searches": {"filter": {"term": {"event_type": "search"}}},
                "clicks": {"filter": {"term": {"event_type": "click"}}}
            },
            "size": 0
        }
        
        response = self.client.search(index=self.ANALYTICS_INDEX, body=search_body)
        
        searches = response["aggregations"]["searches"]["doc_count"]
        clicks = response["aggregations"]["clicks"]["doc_count"]
        ctr = (clicks / searches * 100) if searches > 0 else 0
        
        return {
            "searches": searches,
            "clicks": clicks,
            "click_through_rate": round(ctr, 2)
        }
    
    def get_average_response_time(self, days: int = 7) -> Dict[str, float]:
        """Get average search response time."""
        search_body = {
            "query": {"range": {"timestamp": {"gte": f"now-{days}d/d"}}},
            "aggs": {
                "avg_response_time": {"avg": {"field": "response_time_ms"}},
                "percentiles_response_time": {
                    "percentiles": {"field": "response_time_ms", "percents": [50, 90, 95, 99]}
                }
            },
            "size": 0
        }
        
        response = self.client.search(index=self.ANALYTICS_INDEX, body=search_body)
        
        return {
            "average_ms": response["aggregations"]["avg_response_time"]["value"],
            "percentiles": response["aggregations"]["percentiles_response_time"]["values"]
        }
    
    def get_search_dashboard_data(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive search analytics dashboard data."""
        return {
            "popular_queries": self.get_popular_queries(days),
            "zero_result_queries": self.get_zero_result_queries(days),
            "click_through_rate": self.get_click_through_rate(days),
            "response_time": self.get_average_response_time(days),
            "query_volume_by_day": self._get_query_volume_by_day(days),
            "top_filters": []
        }
    
    def _get_query_volume_by_day(self, days: int) -> List[Dict[str, Any]]:
        """Get search volume by day."""
        search_body = {
            "query": {"range": {"timestamp": {"gte": f"now-{days}d/d"}}},
            "aggs": {
                "by_day": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "day",
                        "format": "yyyy-MM-dd"
                    }
                }
            },
            "size": 0
        }
        
        response = self.client.search(index=self.ANALYTICS_INDEX, body=search_body)
        
        return [
            {"date": bucket["key_as_string"], "count": bucket["doc_count"]}
            for bucket in response["aggregations"]["by_day"]["buckets"]
        ]
```


---

## 11. Index Management

### 11.1 Data Pipeline

```python
# /app/search/data_pipeline.py
"""Data pipeline for syncing data to Elasticsearch."""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, parallel_bulk
from typing import Dict, Any, List, Optional, Iterator
import logging

logger = logging.getLogger(__name__)


class DataSyncPipeline:
    """Pipeline for syncing data from primary DB to Elasticsearch."""
    
    BATCH_SIZE = 1000
    
    def __init__(self, client: Elasticsearch):
        self.client = client
    
    def index_document(
        self,
        index: str,
        doc_id: str,
        document: Dict[str, Any],
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Index a single document."""
        return self.client.index(
            index=index,
            id=doc_id,
            body=document,
            refresh="true" if refresh else "false"
        )
    
    def bulk_index(
        self,
        index: str,
        documents: List[Dict[str, Any]],
        id_field: str = "id"
    ) -> Dict[str, Any]:
        """Bulk index documents."""
        actions = []
        for doc in documents:
            action = {
                "_index": index,
                "_id": doc.get(id_field),
                "_source": doc
            }
            actions.append(action)
        
        success, errors = bulk(
            self.client,
            actions,
            chunk_size=self.BATCH_SIZE,
            raise_on_error=False
        )
        
        return {"success": success, "errors": errors, "total": len(documents)}
    
    def parallel_bulk_index(
        self,
        index: str,
        documents: Iterator[Dict[str, Any]],
        id_field: str = "id",
        thread_count: int = 4
    ) -> Iterator[Dict[str, Any]]:
        """Parallel bulk index for large datasets."""
        def generate_actions():
            for doc in documents:
                yield {
                    "_index": index,
                    "_id": doc.get(id_field),
                    "_source": doc
                }
        
        for success, info in parallel_bulk(
            self.client,
            generate_actions(),
            thread_count=thread_count,
            chunk_size=self.BATCH_SIZE
        ):
            yield {"success": success, "info": info}
    
    def update_document(
        self,
        index: str,
        doc_id: str,
        updates: Dict[str, Any],
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Update specific fields of a document."""
        return self.client.update(
            index=index,
            id=doc_id,
            body={"doc": updates},
            refresh="true" if refresh else "false"
        )
    
    def delete_document(self, index: str, doc_id: str, refresh: bool = False) -> Dict[str, Any]:
        """Delete a document."""
        return self.client.delete(
            index=index,
            id=doc_id,
            refresh="true" if refresh else "false"
        )
    
    def bulk_delete(self, index: str, doc_ids: List[str]) -> Dict[str, Any]:
        """Bulk delete documents."""
        actions = [
            {"_op_type": "delete", "_index": index, "_id": doc_id}
            for doc_id in doc_ids
        ]
        
        success, errors = bulk(
            self.client,
            actions,
            chunk_size=self.BATCH_SIZE,
            raise_on_error=False
        )
        
        return {"success": success, "errors": errors, "total": len(doc_ids)}


class CDCEventHandler:
    """Handle CDC events from primary database."""
    
    def __init__(self, pipeline: DataSyncPipeline):
        self.pipeline = pipeline
    
    def handle_insert(self, index: str, document: Dict[str, Any]) -> None:
        """Handle insert event."""
        doc_id = document.get("id")
        self.pipeline.index_document(index, doc_id, document)
        logger.info(f"Indexed new document: {index}/{doc_id}")
    
    def handle_update(self, index: str, doc_id: str, changes: Dict[str, Any]) -> None:
        """Handle update event."""
        self.pipeline.update_document(index, doc_id, changes)
        logger.info(f"Updated document: {index}/{doc_id}")
    
    def handle_delete(self, index: str, doc_id: str) -> None:
        """Handle delete event."""
        self.pipeline.delete_document(index, doc_id)
        logger.info(f"Deleted document: {index}/{doc_id}")


class IndexMaintenance:
    """Index maintenance operations."""
    
    def __init__(self, client: Elasticsearch):
        self.client = client
    
    def optimize_index(self, index: str) -> None:
        """Optimize index for search performance."""
        self.client.indices.forcemerge(index=index, max_num_segments=1, wait_for_completion=False)
        self.client.indices.refresh(index=index)
        self.client.indices.clear_cache(index=index)
        logger.info(f"Optimized index: {index}")
    
    def reindex_with_mapping(
        self,
        source_index: str,
        target_index: str,
        new_mapping: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Reindex with new mapping."""
        if new_mapping:
            self.client.indices.create(index=target_index, body=new_mapping)
        
        result = self.client.reindex(
            body={"source": {"index": source_index}, "dest": {"index": target_index}},
            wait_for_completion=True
        )
        
        logger.info(f"Reindexed {result['total']} documents from {source_index} to {target_index}")
        return result
    
    def alias_switch(self, alias: str, old_index: str, new_index: str) -> None:
        """Atomically switch alias to new index."""
        self.client.indices.update_aliases(body={
            "actions": [
                {"remove": {"index": old_index, "alias": alias}},
                {"add": {"index": new_index, "alias": alias}}
            ]
        })
        logger.info(f"Switched alias '{alias}' from {old_index} to {new_index}")
    
    def get_index_size(self, index: str) -> Dict[str, Any]:
        """Get index size information."""
        stats = self.client.indices.stats(index=index)
        
        return {
            "doc_count": stats["indices"][index]["total"]["docs"]["count"],
            "store_size_bytes": stats["indices"][index]["total"]["store"]["size_in_bytes"],
            "store_size_mb": round(
                stats["indices"][index]["total"]["store"]["size_in_bytes"] / (1024 * 1024), 2
            ),
            "index_total": stats["indices"][index]["total"]["indexing"]["index_total"],
            "search_total": stats["indices"][index]["total"]["search"]["query_total"]
        }
```

---

## 12. Implementation Priority

### 12.1 Priority Matrix

| Component | Priority | Effort | Impact | Phase |
|-----------|----------|--------|--------|-------|
| Elasticsearch Setup | P0 | Medium | High | 1 |
| Index Mappings | P0 | Medium | High | 1 |
| Basic Full-Text Search | P0 | Low | High | 1 |
| Search Service | P0 | Medium | High | 1 |
| Query Builder | P0 | Medium | High | 1 |
| Faceted Search | P1 | Medium | High | 2 |
| Geo Search | P1 | Medium | High | 2 |
| Autocomplete | P1 | Low | Medium | 2 |
| Search Analytics | P2 | Medium | Medium | 3 |
| Relevance Tuning | P2 | High | Medium | 3 |
| Semantic Search | P3 | High | Medium | 4 |
| Advanced Analytics | P3 | Medium | Low | 4 |

### 12.2 Phase 1: Foundation (Weeks 1-2)

```python
# /app/search/__init__.py
"""ResilienceAI Search Module - Phase 1 Implementation."""

from .elasticsearch_client import ElasticsearchClient, check_elasticsearch_health
from .index_mappings import IndexMappings, INDEX_CONFIGS
from .index_manager import IndexManager
from .search_service import SearchService, SearchResponse, SearchResult
from .query_builder import QueryBuilder

__all__ = [
    "ElasticsearchClient",
    "check_elasticsearch_health",
    "IndexMappings",
    "INDEX_CONFIGS",
    "IndexManager",
    "SearchService",
    "SearchResponse",
    "SearchResult",
    "QueryBuilder",
]

__version__ = "1.0.0"
```

### 12.3 Phase 2: Enhanced Search (Weeks 3-4)

```python
# Phase 2 additions
from .faceted_search import FacetedSearchService, FacetConfiguration
from .geo_search import GeoSearchService, GeoPoint
from .suggest_service import SuggestService
```

### 12.4 Phase 3: Analytics & Tuning (Weeks 5-6)

```python
# Phase 3 additions
from .analytics_service import SearchAnalyticsService, SearchEvent
from .relevance_tuning import RelevanceTuner
```

### 12.5 Phase 4: Advanced Features (Weeks 7-8)

```python
# Phase 4 additions
from .data_pipeline import DataSyncPipeline, CDCEventHandler
```

---

## Appendix: Configuration Files

### docker-compose.yml

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: es-node-1
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - cluster.name=resilience-ai-search
      - node.name=es-node-1
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - es-data:/usr/share/elasticsearch/data
    networks:
      - elastic

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - elastic

volumes:
  es-data:
    driver: local

networks:
  elastic:
    driver: bridge
```

### requirements.txt

```
elasticsearch>=8.11.0
elasticsearch-dsl>=8.11.0
```

---

## Summary

This document provides a comprehensive design for integrating Elasticsearch into ResilienceAI. The implementation is organized into phases, starting with foundational components and progressively adding advanced features like faceted search, geospatial capabilities, and analytics.

### Key Design Decisions:

1. **Modular architecture** with separate services for each capability
2. **Circuit breaker pattern** for resilient connections
3. **Comprehensive mappings** with support for full-text, geo, and ML features
4. **Faceted search** with post-filtering for accurate counts
5. **Geo-search** with multiple query types and clustering
6. **Analytics** for monitoring and improving search quality

### Index Summary:

| Index | Purpose | Key Features |
|-------|---------|--------------|
| incidents | Incident search | Full-text, geo, nested comments, ML vectors |
| resources | Resource directory | Full-text, geo, availability tracking |
| kb_articles | Knowledge base | Full-text, semantic search, engagement metrics |
| users | User search | Full-text, geo, skills matching |
| search_analytics | Search tracking | Query analysis, CTR, response time |

### Query Types Supported:

- Full-text search with boosting
- Fuzzy search for typo tolerance
- Geo-distance search
- Geo-bounding box search
- Geo-polygon search
- Faceted navigation
- Semantic/vector search
- Autocomplete/suggestions
- Multi-index search

---

*Document Version: 1.0*
*Last Updated: 2024*
