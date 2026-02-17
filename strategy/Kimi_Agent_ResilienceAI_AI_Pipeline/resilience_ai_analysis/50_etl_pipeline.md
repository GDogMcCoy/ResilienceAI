# ResilienceAI ETL Pipeline Enhancement Design

## Executive Summary

This document provides a comprehensive analysis of the current ResilienceAI ETL implementation and designs enterprise-grade enhancements for data extraction, transformation, and loading workflows. The current implementation in `src/download_data.py` provides basic sequential processing with limited error handling. This design introduces a modern, scalable ETL architecture with incremental loading, change data capture, robust error handling, and comprehensive monitoring.

---

## 1. Current State Analysis

### 1.1 Existing ETL Implementation

**File:** `src/download_data.py` (383 lines, 13.3 KB)

#### Current Capabilities:
- **Data Sources:**
  - HIFLD Facilities (ArcGIS REST API with pagination)
  - CMS Nursing Homes (Medicare Provider Data API)
  - FEMA Disaster Declarations (OpenFEMA API)
  - Census ACS Demographics (Census API)
  - County Centroids (Census Gazetteer)

- **Features:**
  - Basic file-based caching (JSON)
  - Simple pagination handling
  - Sequential processing
  - Basic error handling (print statements)
  - Data transformation to CSV

#### Current Limitations:
```python
# Issues identified in current implementation:

# 1. No incremental loading - full downloads every time
# 2. Limited error recovery - breaks on first error
# 3. No data quality checks
# 4. Sequential processing - no parallelism
# 5. Basic caching - no cache invalidation strategy
# 6. No pipeline orchestration
# 7. Limited observability
# 8. No schema evolution handling
# 9. No data lineage tracking
# 10. Hard-coded configurations
```

### 1.2 Supporting Components

**File:** `src/feature_engineering.py` (548 lines, 21.9 KB)
- 66+ features for vulnerability modeling
- Spatial distance calculations (haversine, KD-tree)
- FEMA disaster features
- Demographic aggregations

**File:** `src/realtime_pipeline.py` (376 lines, 13.3 KB)
- WebSocket-based streaming
- Event-driven architecture
- Basic pub/sub pattern

---

## 2. Enhanced ETL Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESILIENCEAI ETL PLATFORM                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   INGESTION  │───▶│ TRANSFORM    │───▶│    LOAD      │                  │
│  │   LAYER      │    │    LAYER     │    │   LAYER      │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                   │                          │
│         ▼                   ▼                   ▼                          │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │              ORCHESTRATION & MONITORING              │                   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐  │                   │
│  │  │  DAG    │  │  CDC    │  │ Quality │  │ Lineage│  │                   │
│  │  │Engine   │  │ Tracker │  │ Checks  │  │  Graph │  │                   │
│  │  └─────────┘  └─────────┘  └─────────┘  └────────┘  │                   │
│  └─────────────────────────────────────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA SOURCES                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  HIFLD ArcGIS │ CMS API │ FEMA Open │ Census │ USGS │ NOAA │ GEE │ Custom  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTRACTION LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │ REST Client │  │  Streaming  │  │   Batch     │  │  Change Data Capture ││
│  │  (Async)    │  │   Client    │  │  Extractor  │  │      (CDC)          ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘│
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │ Rate Limiter│  │  Retry      │  │  Circuit    │  │   Schema Registry   ││
│  │             │  │  Handler    │  │   Breaker   │  │                     ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TRANSFORMATION LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │   Pandas    │  │   Spark     │  │  Feature    │  │   Data Quality      ││
│  │  Pipeline   │  │  Cluster    │  │  Engineering│  │     Engine          ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘│
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │  Geospatial │  │  Temporal   │  │  Statistical│  │   Anomaly Detect    ││
│  │   Engine    │  │  Windows    │  │  Aggregates │  │                     ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOAD LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │  Delta Lake │  │  Parquet    │  │   SQLite    │  │   Data Warehouse    ││
│  │  (Bronze)   │  │  (Silver)   │  │  (Gold)     │  │   (Postgres)        ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘│
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │  Time-Scale │  │   Vector    │  │   Cache     │  │   Feature Store     ││
│  │    DB       │  │    DB       │  │   Layer     │  │                     ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Implementation Design

### 3.1 Core ETL Framework

See full implementation in the code files section below.

Key components:
- `ETLComponent`: Abstract base class for all ETL components
- `Extractor`: Base class for data extractors with incremental support
- `Transformer`: Base class for data transformers with schema validation
- `Loader`: Base class for data loaders with validation

### 3.2 Change Data Capture (CDC) System

The CDC system tracks data changes using checksum-based detection:
- Supports multiple tracking strategies (timestamp, checksum, log-based)
- SQLite-backed state storage
- Change history tracking
- Configurable change handlers

### 3.3 Data Quality Engine

Multi-dimensional quality validation:
- Completeness, Accuracy, Consistency, Validity, Uniqueness, Timeliness
- Configurable validation rules
- Quality scoring with weighted dimensions
- Great Expectations integration
- Quality trend tracking

### 3.4 Pipeline Orchestrator

DAG-based workflow management:
- Dependency-based execution
- Parallel task execution with semaphore control
- Retry logic with exponential backoff
- Circuit breaker pattern for fault tolerance
- Execution visualization

---

## 4. Implementation Code

### 4.1 Core ETL Base Classes

```python
# src/etl/core/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Callable
import asyncio
import hashlib
import json
import logging
from pathlib import Path
import pandas as pd
import numpy as np

class ETLStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    RETRYING = "retrying"
    SKIPPED = "skipped"

@dataclass
class ETLMetadata:
    pipeline_id: str
    run_id: str = field(default_factory=lambda: hashlib.md5(
        datetime.now().isoformat().encode()
    ).hexdigest()[:12])
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: ETLStatus = ETLStatus.PENDING
    records_processed: int = 0
    records_failed: int = 0
    error_log: List[Dict] = field(default_factory=list)

@dataclass
class DataContract:
    name: str
    columns: Dict[str, str]
    required_columns: List[str]
    primary_key: Optional[str] = None
    version: str = "1.0"

class ETLComponent(ABC):
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self.metadata = ETLMetadata(pipeline_id=name)
        self._observers: List[Callable] = []
        
    def add_observer(self, callback: Callable):
        self._observers.append(callback)
        
    def notify_observers(self, event: str, data: Dict):
        for observer in self._observers:
            try:
                observer(event, data)
            except Exception as e:
                logging.error(f"Observer error: {e}")
    
    @abstractmethod
    async def execute(self, input_data: Optional[Any] = None) -> Any:
        pass
```

### 4.2 CDC Tracker Implementation

```python
# src/etl/cdc/tracker.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import hashlib
import json
import sqlite3
from pathlib import Path
import pandas as pd

class CDCOperation(Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"

@dataclass
class CDCRecord:
    table_name: str
    primary_key: str
    pk_value: str
    operation: CDCOperation
    before_data: Optional[Dict] = None
    after_data: Optional[Dict] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class CDCTracker:
    def __init__(self, storage_path: Path, strategy: str = "checksum"):
        self.storage_path = storage_path
        self.strategy = strategy
        self._db_path = storage_path / "cdc_state.db"
        self._init_storage()
    
    def _init_storage(self):
        self.storage_path.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cdc_checkpoints (
                    table_name TEXT PRIMARY KEY,
                    last_processed_at TEXT,
                    record_count INTEGER,
                    checksum TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cdc_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT,
                    pk_value TEXT,
                    operation TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def _compute_checksum(self, data: Dict) -> str:
        normalized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def detect_changes(self, table_name: str, current_data: pd.DataFrame,
                       primary_key: str) -> List[CDCRecord]:
        changes = []
        current_state = {str(row[primary_key]): row.to_dict() 
                        for _, row in current_data.iterrows()}
        
        # Load previous state
        prev_data_path = self.storage_path / f"{table_name}_snapshot.parquet"
        previous_state = {}
        if prev_data_path.exists():
            prev_df = pd.read_parquet(prev_data_path)
            previous_state = {str(row[primary_key]): row.to_dict() 
                            for _, row in prev_df.iterrows()}
        
        current_keys = set(current_state.keys())
        previous_keys = set(previous_state.keys())
        
        # Detect INSERTs
        for pk in current_keys - previous_keys:
            changes.append(CDCRecord(
                table_name=table_name, primary_key=primary_key,
                pk_value=pk, operation=CDCOperation.INSERT,
                after_data=current_state[pk]
            ))
        
        # Detect DELETEs
        for pk in previous_keys - current_keys:
            changes.append(CDCRecord(
                table_name=table_name, primary_key=primary_key,
                pk_value=pk, operation=CDCOperation.DELETE,
                before_data=previous_state[pk]
            ))
        
        # Detect UPDATEs
        for pk in current_keys & previous_keys:
            if self._compute_checksum(current_state[pk]) != \
               self._compute_checksum(previous_state[pk]):
                changes.append(CDCRecord(
                    table_name=table_name, primary_key=primary_key,
                    pk_value=pk, operation=CDCOperation.UPDATE,
                    before_data=previous_state[pk],
                    after_data=current_state[pk]
                ))
        
        # Save snapshot
        current_data.to_parquet(prev_data_path, index=False)
        return changes
```

### 4.3 Data Quality Engine

```python
# src/etl/quality/engine.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
import pandas as pd
import numpy as np

class QualityDimension(Enum):
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"

class QualitySeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class QualityRule:
    name: str
    dimension: QualityDimension
    severity: QualitySeverity
    check_function: Callable[[pd.DataFrame], bool]
    description: str
    threshold: float = 0.95

@dataclass
class QualityReport:
    dataset_name: str
    total_records: int
    total_columns: int
    overall_score: float
    dimension_scores: Dict[QualityDimension, float]
    passed_rules: List[str]
    failed_rules: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "dataset_name": self.dataset_name,
            "overall_score": self.overall_score,
            "dimension_scores": {k.value: v for k, v in self.dimension_scores.items()},
            "passed_rules": len(self.passed_rules),
            "failed_rules": len(self.failed_rules),
            "timestamp": self.timestamp.isoformat()
        }

class DataQualityEngine:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.rules: List[QualityRule] = []
        self._init_default_rules()
    
    def _init_default_rules(self):
        self.add_rule(QualityRule(
            name="valid_coordinates",
            dimension=QualityDimension.VALIDITY,
            severity=QualitySeverity.ERROR,
            check_function=lambda df: (
                df['latitude'].dropna().between(-90, 90).all() and
                df['longitude'].dropna().between(-180, 180).all()
            ) if 'latitude' in df.columns and 'longitude' in df.columns else True,
            description="Coordinates must be valid"
        ))
        
        self.add_rule(QualityRule(
            name="no_empty_columns",
            dimension=QualityDimension.COMPLETENESS,
            severity=QualitySeverity.ERROR,
            check_function=lambda df: not any(df[col].isna().all() for col in df.columns),
            description="No column should be completely empty"
        ))
    
    def add_rule(self, rule: QualityRule):
        self.rules.append(rule)
    
    def validate(self, df: pd.DataFrame, dataset_name: str) -> QualityReport:
        issues = []
        passed_rules = []
        failed_rules = []
        dimension_scores = {dim: [] for dim in QualityDimension}
        
        for rule in self.rules:
            try:
                passed = rule.check_function(df)
                if passed:
                    passed_rules.append(rule.name)
                    dimension_scores[rule.dimension].append(1.0)
                else:
                    failed_rules.append(rule.name)
                    dimension_scores[rule.dimension].append(0.0)
            except Exception as e:
                failed_rules.append(rule.name)
                dimension_scores[rule.dimension].append(0.0)
        
        avg_scores = {dim: np.mean(scores) if scores else 1.0 
                     for dim, scores in dimension_scores.items()}
        
        weights = {
            QualityDimension.COMPLETENESS: 0.25,
            QualityDimension.ACCURACY: 0.20,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.VALIDITY: 0.20,
            QualityDimension.UNIQUENESS: 0.15,
            QualityDimension.TIMELINESS: 0.05
        }
        
        overall_score = sum(avg_scores[dim] * weights[dim] for dim in QualityDimension)
        
        return QualityReport(
            dataset_name=dataset_name,
            total_records=len(df),
            total_columns=len(df.columns),
            overall_score=overall_score,
            dimension_scores=avg_scores,
            passed_rules=passed_rules,
            failed_rules=failed_rules
        )
```

---

## 5. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
1. **Core ETL Framework** (`src/etl/core/`)
   - Base classes and interfaces
   - Component abstractions
   - Configuration management

2. **Basic Extractors** (`src/etl/extractors/`)
   - Refactor existing download_data.py
   - Add async HTTP client
   - Implement basic caching

3. **Simple Pipeline Orchestrator**
   - Sequential execution
   - Basic error handling
   - Simple retry logic

### Phase 2: Reliability (Weeks 3-4)
4. **CDC System** (`src/etl/cdc/`)
   - Checksum-based change detection
   - State storage
   - Incremental extraction

5. **Data Quality Engine** (`src/etl/quality/`)
   - Validation rules
   - Quality scoring
   - Great Expectations integration

6. **Error Handling & Recovery**
   - Circuit breaker pattern
   - Exponential backoff
   - Dead letter queue

### Phase 3: Scalability (Weeks 5-6)
7. **Advanced Orchestrator** (`src/etl/orchestrator/`)
   - DAG-based execution
   - Parallel processing
   - Dependency management

8. **Multi-Layer Loader** (`src/etl/loaders/`)
   - Medallion architecture
   - Feature store
   - Partitioning strategy

9. **Advanced Transformers**
   - Feature engineering pipeline
   - Temporal aggregations
   - Geospatial computations

### Phase 4: Observability (Weeks 7-8)
10. **Monitoring System** (`src/etl/monitoring/`)
    - Metric collection
    - Alert management
    - Dashboard data

11. **Data Lineage** (`src/etl/lineage/`)
    - Asset tracking
    - Dependency graphs
    - Impact analysis

12. **Integration & Testing**
    - End-to-end pipeline tests
    - Performance benchmarks
    - Documentation

---

## 6. File Structure

```
src/etl/
├── __init__.py
├── core/
│   ├── __init__.py
│   └── base.py              # Base ETL classes
├── cdc/
│   ├── __init__.py
│   └── tracker.py           # Change data capture
├── quality/
│   ├── __init__.py
│   └── engine.py            # Data quality engine
├── orchestrator/
│   ├── __init__.py
│   └── dag.py               # Pipeline orchestration
├── extractors/
│   ├── __init__.py
│   └── hifld_extractor.py   # HIFLD data extraction
├── transformers/
│   ├── __init__.py
│   └── feature_transformer.py # Feature engineering
├── loaders/
│   ├── __init__.py
│   └── multi_layer_loader.py # Medallion architecture
├── monitoring/
│   ├── __init__.py
│   └── monitor.py           # Pipeline monitoring
├── lineage/
│   ├── __init__.py
│   └── tracker.py           # Data lineage tracking
└── pipeline/
    ├── __init__.py
    └── main_pipeline.py     # Main ETL pipeline
```

---

## 7. Key Improvements Summary

| Aspect | Current | Enhanced |
|--------|---------|----------|
| **Extraction** | Sequential, blocking | Async, parallel |
| **Incremental Loading** | None | CDC with checksums |
| **Error Handling** | Print statements | Circuit breaker, retry |
| **Data Quality** | None | Multi-dimensional scoring |
| **Orchestration** | Sequential functions | DAG-based with dependencies |
| **Monitoring** | Console output | Metrics, alerts, dashboards |
| **Lineage** | None | Full dependency tracking |
| **Schema Evolution** | None | Versioned contracts |

### Expected Benefits:

1. **Performance**: 3-5x faster with async/parallel processing
2. **Reliability**: 99.9% uptime with circuit breakers and retry
3. **Data Quality**: <1% error rate with comprehensive validation
4. **Observability**: Full visibility into pipeline health
5. **Maintainability**: Modular, testable components
6. **Scalability**: Horizontal scaling ready

---

## 8. Configuration Example

```yaml
# config/etl_config.yaml
etl:
  data_dir: "data"
  
  extraction:
    hifld:
      page_size: 2000
      rate_limit_delay: 0.3
      max_retries: 3
      timeout: 120
    
  cdc:
    enabled: true
    strategy: "checksum"
    storage_path: "data/cdc"
    
  quality:
    enabled: true
    min_score: 0.7
    fail_on_critical: true
    
  orchestration:
    max_parallel: 5
    retry_attempts: 3
    retry_delay: 2.0
    
  medallion:
    base_path: "data/medallion"
    partition_columns: ["year", "month"]
    
  monitoring:
    enabled: true
    storage_path: "data/monitoring"
    alert_thresholds:
      extraction_error_rate:
        max: 0.1
        severity: "warning"
      quality_score:
        min: 0.7
        severity: "error"
```

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: ETL Pipeline Engineering Team*
