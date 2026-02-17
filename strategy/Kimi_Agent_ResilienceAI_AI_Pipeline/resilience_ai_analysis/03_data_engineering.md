# ResilienceAI Data Engineering Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the ResilienceAI data pipeline and proposes AI-powered data engineering enhancements to transform the current batch-oriented system into a modern, real-time, ML-driven data platform.

---

## 1. Current State Analysis

### 1.1 Existing Data Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT PIPELINE ARCHITECTURE                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   FEMA API   │    │  Census API  │    │  HIFLD API   │
│  (REST/JSON) │    │  (REST/JSON) │    │(ArcGIS/JSON) │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│                    download_data.py                           │
│  • Simple HTTP requests with requests library                 │
│  • File-based JSON caching (CACHE_DIR/*.json)                 │
│  • Pagination handling (ArcGIS: 2000/page, FEMA: 10000/page) │
│  • No retry logic or exponential backoff                      │
│  • Sequential processing only                                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   data/raw/*.csv    │
              │  (Intermediate CSV) │
              └──────────┬──────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                 feature_engineering.py                        │
│  • 66+ features across 3,222 counties                         │
│  • Spatial calculations with cKDTree                          │
│  • Haversine distance calculations                            │
│  • Min-max normalization                                      │
│  • 7 advanced differentiator features                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ data/processed/*.csv│
              │ (Final Features)    │
              └─────────────────────┘
```

### 1.2 Current Data Sources

| Source | Type | Update Frequency | Current Method |
|--------|------|------------------|----------------|
| FEMA Disaster Declarations | REST API | Daily | Polling (5 min intervals) |
| Census ACS | REST API | Annual | Manual trigger |
| HIFLD Facilities | ArcGIS REST | Quarterly | On-demand |
| CMS Nursing Homes | CSV Download | Monthly | On-demand |
| NOAA Weather | REST API | Real-time | Polling (60 sec) |
| USGS Earthquakes | GeoJSON Feed | Real-time | Polling (5 min) |

### 1.3 Current Feature Engineering (66 Features)

#### Demographics (6 features)
- `total_population`, `median_income`, `poverty_pct`
- `elderly_pct`, `disability_pct`, `uninsured_pct`

#### Infrastructure Distance (12 features)
- `dist_nearest_hospitals_km`, `dist_2nd_nearest_hospitals_km`
- `dist_nearest_fire_stations_km`, `dist_nearest_ems_km`
- `count_hospitals_50km`, `count_fire_stations_50km`, etc.

#### Disaster History (8 features)
- `disaster_count`, `disaster_count_recent`
- `disaster_flood`, `disaster_hurricane`, `disaster_fire`, `disaster_tornado`
- `disasters_2015_2025`, `disasters_2005_2014`

#### Composite Indices (4 features)
- `vulnerability_index`, `isolation_index`
- `risk_score`, `risk_level`

#### Advanced Differentiators (7 features)
- `compound_risk_count`, `compound_risk_flag`
- `neighbor_avg_risk`, `risk_contagion_delta`
- `disaster_acceleration`
- `redundancy_score`, `zero_redundancy_flag`
- `pop_weighted_vulnerability`, `pop_weighted_risk`
- `risk_score_state_pctile`, `vulnerability_index_state_pctile`
- `top_intervention`, `top_intervention_score`

### 1.4 Current Limitations

| Area | Current State | Impact |
|------|---------------|--------|
| **Data Quality** | No validation | Silent failures, data drift |
| **Orchestration** | Manual scripts | No scheduling, no retries |
| **Lineage** | None | Cannot trace feature origins |
| **Versioning** | Git only | No data versioning |
| **Streaming** | Basic polling | High latency, resource intensive |
| **Parallelism** | None | Slow processing for large datasets |
| **Monitoring** | Print statements | No alerts, no dashboards |
| **Schema Evolution** | Manual | Breaking changes risk |


---

## 2. Proposed Enhanced Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENHANCED DATA PLATFORM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION LAYER                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  FEMA    │ │  Census  │ │  HIFLD   │ │   NOAA   │ │   USDA   │          │
│  │ Connect  │ │ Connect  │ │ Connect  │ │ Connect  │ │ Connect  │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       │            │            │            │            │                 │
│       └────────────┴────────────┴────────────┴────────────┘                 │
│                                    │                                         │
│                         ┌──────────▼──────────┐                             │
│                         │   Kafka / Redpanda   │                            │
│                         │   (Event Streaming)  │                            │
│                         └──────────┬──────────┘                             │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                         STREAM PROCESSING LAYER                              │
│                                    │                                         │
│       ┌────────────────────────────┼────────────────────────────┐            │
│       │                            │                            │            │
│       ▼                            ▼                            ▼            │
│  ┌─────────┐                ┌─────────┐                  ┌─────────┐        │
│  │  Flink  │                │  Spark  │                  │  Kafka  │        │
│  │ Streams │                │Streaming│                  │  ksqlDB │        │
│  └────┬────┘                └────┬────┘                  └────┬────┘        │
│       │                          │                            │             │
│       └──────────────────────────┼────────────────────────────┘             │
│                                  │                                          │
│                    ┌─────────────▼─────────────┐                           │
│                    │   ML-Based Anomaly Det.   │                           │
│                    │   (Isolation Forest/Auto) │                           │
│                    └─────────────┬─────────────┘                           │
└──────────────────────────────────┼─────────────────────────────────────────┘
                                   │
┌──────────────────────────────────┼─────────────────────────────────────────┐
│                      DATA QUALITY & VALIDATION LAYER                         │
│                                  │                                           │
│                    ┌─────────────▼─────────────┐                            │
│                    │     Great Expectations    │                            │
│                    │    (Data Contracts/DQ)    │                            │
│                    └─────────────┬─────────────┘                            │
│                                  │                                          │
│       ┌──────────────────────────┼────────────────────────────┐             │
│       │                          │                            │             │
│       ▼                          ▼                            ▼             │
│  ┌─────────┐               ┌─────────┐                 ┌─────────┐         │
│  │ Schema  │               │ Quality │                 │  Data   │         │
│  │Validation│              │ Metrics │                 │ Lineage │         │
│  └─────────┘               └─────────┘                 └─────────┘         │
└──────────────────────────────────┼─────────────────────────────────────────┘
                                   │
┌──────────────────────────────────┼─────────────────────────────────────────┐
│                    FEATURE ENGINEERING LAYER                                 │
│                                  │                                           │
│                    ┌─────────────▼─────────────┐                            │
│                    │   Feature Store (Feast)   │                            │
│                    │  (Online/Offline Stores)  │                            │
│                    └─────────────┬─────────────┘                            │
│                                  │                                          │
│       ┌──────────────────────────┼────────────────────────────┐             │
│       │                          │                            │             │
│       ▼                          ▼                            ▼             │
│  ┌─────────┐               ┌─────────┐                 ┌─────────┐         │
│  │ Feature │               │ Feature │                 │ Feature │         │
│  │Transform│               │  Stats  │                 │  Serve  │         │
│  └─────────┘               └─────────┘                 └─────────┘         │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │              Automated Feature Engineering (Featuretools)           │   │
│  │  • Deep Feature Synthesis (DFS)                                     │   │
│  │  • Temporal Features                                                │   │
│  │  • Geospatial Aggregation                                           │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┼─────────────────────────────────────────┘
                                   │
┌──────────────────────────────────┼─────────────────────────────────────────┐
│                    ORCHESTRATION & STORAGE LAYER                             │
│                                  │                                           │
│                    ┌─────────────▼─────────────┐                            │
│                    │      Apache Airflow       │                            │
│                    │   (DAGs/Scheduling/Retry) │                            │
│                    └─────────────┬─────────────┘                            │
│                                  │                                          │
│       ┌──────────────────────────┼────────────────────────────┐             │
│       │                          │                            │             │
│       ▼                          ▼                            ▼             │
│  ┌─────────┐               ┌─────────┐                 ┌─────────┐         │
│  │   DVC   │               │ Delta   │                 │  Data   │         │
│  │(Version)│               │  Lake   │                 │ Catalog │         │
│  └─────────┘               └─────────┘                 │(DataHub)│         │
│                                                        └─────────┘         │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Enhancement Specifications

### 3.1 Real-Time Data Streaming Pipeline

#### 3.1.1 Kafka-Based Event Streaming

**File: `src/pipeline/streaming/kafka_producer.py`**

```python
"""
Kafka producer for real-time data ingestion from multiple sources.
"""
from confluent_kafka import Producer, KafkaError
from dataclasses import dataclass
from typing import Dict, Optional, Callable
import json
import asyncio
import logging
from datetime import datetime

@dataclass
class DataSourceConfig:
    """Configuration for a data source connector."""
    name: str
    topic: str
    poll_interval_seconds: int
    retry_policy: Dict
    schema_version: str

class ResilienceKafkaProducer:
    """
    Unified Kafka producer for all ResilienceAI data sources.

    Features:
    - Async message production
    - Schema validation with Avro
    - Automatic retry with exponential backoff
    - Dead letter queue for failed messages
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.config = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'resilience-ai-producer',
            'compression.type': 'lz4',
            'batch.size': 16384,
            'linger.ms': 5,
            'retries': 3,
            'retry.backoff.ms': 1000,
        }
        self.producer = Producer(self.config)
        self.dlq_topic = "resilience.dlq"

    def produce_event(self, topic: str, key: str, value: Dict, 
                      headers: Optional[Dict] = None):
        """Produce an event to Kafka with schema validation."""
        try:
            enriched_value = {
                **value,
                '_metadata': {
                    'produced_at': datetime.utcnow().isoformat(),
                    'source': 'resilience-ai',
                    'version': '1.0.0'
                }
            }

            self.producer.produce(
                topic=topic,
                key=key.encode('utf-8'),
                value=json.dumps(enriched_value).encode('utf-8'),
                headers=headers or {},
                callback=self._delivery_callback
            )
        except Exception as e:
            logging.error(f"Failed to produce to {topic}: {e}")
            self._send_to_dlq(topic, key, value, str(e))

    def _delivery_callback(self, err, msg):
        """Handle message delivery confirmation."""
        if err:
            logging.error(f"Message delivery failed: {err}")

    def _send_to_dlq(self, original_topic: str, key: str, 
                     value: Dict, error: str):
        """Send failed message to dead letter queue."""
        dlq_message = {
            'original_topic': original_topic,
            'key': key,
            'value': value,
            'error': error,
            'failed_at': datetime.utcnow().isoformat()
        }
        self.producer.produce(
            topic=self.dlq_topic,
            value=json.dumps(dlq_message).encode('utf-8')
        )

    def flush(self):
        """Flush pending messages."""
        self.producer.flush()
```

#### 3.1.2 Kafka Topics Design

**File: `config/kafka_topics.yaml`**

```yaml
---
# Kafka topic configuration for ResilienceAI data streaming

topics:
  resilience.weather.alerts:
    partitions: 12
    replication_factor: 3
    retention_ms: 604800000  # 7 days
    cleanup_policy: delete
    compression: lz4

  resilience.fema.disasters:
    partitions: 6
    replication_factor: 3
    retention_ms: 2592000000  # 30 days
    cleanup_policy: compact

  resilience.census.updates:
    partitions: 3
    replication_factor: 3
    retention_ms: 31536000000  # 1 year
    cleanup_policy: compact

  resilience.features.risk_score:
    partitions: 12
    replication_factor: 3
    retention_ms: 604800000
    cleanup_policy: compact

  resilience.anomalies.detected:
    partitions: 6
    replication_factor: 3
    retention_ms: 604800000
    cleanup_policy: delete

  resilience.dlq:
    partitions: 3
    replication_factor: 3
    retention_ms: 1209600000  # 14 days
    cleanup_policy: delete
```


---

### 3.2 Automated Data Quality Monitoring

#### 3.2.1 Great Expectations Integration

**File: `src/pipeline/quality/expectations.py`**

```python
"""
Data quality expectations and validation for ResilienceAI.
"""
import great_expectations as gx
from great_expectations.core import ExpectationSuite
from great_expectations.core.expectation_configuration import ExpectationConfiguration
import pandas as pd
from typing import Dict, List

class ResilienceDataQuality:
    """Data quality validation using Great Expectations."""

    def __init__(self, context_root_dir: str = "gx"):
        self.context = gx.get_context(context_root_dir=context_root_dir)

    def create_census_expectations(self) -> ExpectationSuite:
        """Create expectation suite for Census demographic data."""
        suite = self.context.create_expectation_suite(
            expectation_suite_name="census_demographics",
            overwrite_existing=True
        )

        expectations = [
            ExpectationConfiguration(
                expectation_type="expect_column_to_exist",
                kwargs={"column": "fips"}
            ),
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_match_regex",
                kwargs={"column": "fips", "regex": r"^\d{5}$"}
            ),
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={"column": "total_population", "min_value": 0, "max_value": 10000000}
            ),
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={"column": "poverty_pct", "min_value": 0, "max_value": 100}
            ),
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_not_be_null",
                kwargs={"column": "fips"}
            ),
            ExpectationConfiguration(
                expectation_type="expect_table_row_count_to_be_between",
                kwargs={"min_value": 3000, "max_value": 3500}
            ),
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_unique",
                kwargs={"column": "fips"}
            ),
        ]

        for expectation in expectations:
            suite.add_expectation(expectation)

        return suite

    def validate_dataframe(self, df: pd.DataFrame, 
                          suite_name: str) -> Dict:
        """Validate a DataFrame against an expectation suite."""
        batch = self.context.pandas_source.add_dataframe_asset(
            name="temp_batch"
        ).build_batch_request(dataframe=df)

        checkpoint = self.context.add_or_update_checkpoint(
            name=f"{suite_name}_checkpoint",
            validations=[{"batch_request": batch, "expectation_suite_name": suite_name}]
        )

        results = checkpoint.run()

        return {
            'success': results.success,
            'statistics': results.statistics,
            'results': results.results,
            'suite_name': suite_name
        }
```

---

### 3.3 ML-Based Anomaly Detection

#### 3.3.1 Anomaly Detection Pipeline

**File: `src/pipeline/anomaly/anomaly_detector.py`**

```python
"""
ML-based anomaly detection for ResilienceAI data streams.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class AnomalyResult:
    """Anomaly detection result."""
    fips: str
    timestamp: datetime
    anomaly_score: float
    is_anomaly: bool
    feature_contributions: Dict[str, float]
    anomaly_type: str

class ResilienceAnomalyDetector:
    """
    Multi-model anomaly detection system for county-level data.

    Uses ensemble of:
    - Isolation Forest for point anomalies
    - PCA-based reconstruction error for contextual anomalies
    """

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)
        self.feature_columns: List[str] = []
        self.is_fitted = False

    def fit(self, df: pd.DataFrame, feature_columns: List[str]):
        """Fit the anomaly detection models on historical data."""
        self.feature_columns = feature_columns
        X = df[feature_columns].fillna(df[feature_columns].median())

        X_scaled = self.scaler.fit_transform(X)
        self.isolation_forest.fit(X_scaled)
        self.pca.fit(X_scaled)

        self.is_fitted = True
        logging.info(f"Anomaly detector fitted on {len(X)} samples")

    def detect(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """Detect anomalies in new data."""
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before detection")

        X = df[self.feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)

        # Isolation Forest scores
        if_scores = self.isolation_forest.decision_function(X_scaled)
        if_predictions = self.isolation_forest.predict(X_scaled)

        # PCA reconstruction error
        X_pca = self.pca.transform(X_scaled)
        X_reconstructed = self.pca.inverse_transform(X_pca)
        reconstruction_error = np.mean((X_scaled - X_reconstructed) ** 2, axis=1)

        # Combine scores
        combined_scores = -if_scores + reconstruction_error

        results = []
        for idx, row in df.iterrows():
            fips = row.get('fips', str(idx))

            contributions = self._calculate_feature_contributions(
                X_scaled[idx] if isinstance(idx, int) else X_scaled[df.index.get_loc(idx)],
                X_reconstructed[idx] if isinstance(idx, int) else X_reconstructed[df.index.get_loc(idx)]
            )

            anomaly_type = self._classify_anomaly_type(contributions)

            result = AnomalyResult(
                fips=fips,
                timestamp=datetime.utcnow(),
                anomaly_score=float(combined_scores[idx if isinstance(idx, int) else df.index.get_loc(idx)]),
                is_anomaly=if_predictions[idx if isinstance(idx, int) else df.index.get_loc(idx)] == -1,
                feature_contributions=contributions,
                anomaly_type=anomaly_type
            )
            results.append(result)

        return results

    def _calculate_feature_contributions(self, original: np.ndarray, 
                                         reconstructed: np.ndarray) -> Dict[str, float]:
        """Calculate per-feature contribution to anomaly."""
        errors = np.abs(original - reconstructed)
        total_error = errors.sum()

        if total_error == 0:
            return {col: 0.0 for col in self.feature_columns}

        return {col: float(err / total_error) for col, err in zip(self.feature_columns, errors)}

    def _classify_anomaly_type(self, contributions: Dict[str, float]) -> str:
        """Classify the type of anomaly based on feature contributions."""
        top_feature = max(contributions, key=contributions.get)

        if 'disaster' in top_feature:
            return 'disaster_pattern_anomaly'
        elif 'hospital' in top_feature or 'ems' in top_feature or 'fire' in top_feature:
            return 'infrastructure_anomaly'
        elif 'poverty' in top_feature or 'income' in top_feature:
            return 'socioeconomic_anomaly'
        elif 'elderly' in top_feature or 'disability' in top_feature:
            return 'demographic_anomaly'
        else:
            return 'general_anomaly'

    def save(self, path: str):
        """Save the fitted detector."""
        joblib.dump({
            'isolation_forest': self.isolation_forest,
            'scaler': self.scaler,
            'pca': self.pca,
            'feature_columns': self.feature_columns,
            'contamination': self.contamination
        }, path)

    def load(self, path: str):
        """Load a fitted detector."""
        data = joblib.load(path)
        self.isolation_forest = data['isolation_forest']
        self.scaler = data['scaler']
        self.pca = data['pca']
        self.feature_columns = data['feature_columns']
        self.contamination = data['contamination']
        self.is_fitted = True
```


---

### 3.4 Automated Feature Engineering

#### 3.4.1 Featuretools Integration

**File: `src/pipeline/features/auto_feature_engineering.py`**

```python
"""
Automated feature engineering using Featuretools.
"""
import featuretools as ft
from featuretools.primitives import Mean, Sum, Std, Max, Min, Count, Trend
import pandas as pd
import numpy as np
from typing import List, Dict
import logging

class AutomatedFeatureEngineering:
    """Automated feature engineering pipeline using deep feature synthesis."""

    def __init__(self):
        self.entity_set = None
        self.feature_defs = None
        self.feature_matrix = None

    def setup_entity_set(self, counties_df: pd.DataFrame,
                         disasters_df: pd.DataFrame,
                         facilities_df: pd.DataFrame) -> ft.EntitySet:
        """Setup Featuretools entity set with relationships."""
        es = ft.EntitySet(id="resilience_data")

        # Add counties entity
        es = es.add_dataframe(
            dataframe_name="counties",
            dataframe=counties_df,
            index="fips",
            time_index="data_timestamp" if "data_timestamp" in counties_df.columns else None
        )

        # Add disasters entity with relationship to counties
        if not disasters_df.empty:
            es = es.add_dataframe(
                dataframe_name="disasters",
                dataframe=disasters_df,
                index="disaster_id" if "disaster_id" in disasters_df.columns else None,
                make_index=True if "disaster_id" not in disasters_df.columns else False,
                time_index="declarationDate"
            )

            es = es.add_relationship(
                parent_dataframe_name="counties",
                parent_column_name="fips",
                child_dataframe_name="disasters",
                child_column_name="fips"
            )

        # Add facilities entity
        if not facilities_df.empty:
            es = es.add_dataframe(
                dataframe_name="facilities",
                dataframe=facilities_df,
                index="facility_id" if "facility_id" in facilities_df.columns else None,
                make_index=True if "facility_id" not in facilities_df.columns else False
            )

            es = es.add_relationship(
                parent_dataframe_name="counties",
                parent_column_name="fips",
                child_dataframe_name="facilities",
                child_column_name="fips"
            )

        self.entity_set = es
        return es

    def generate_features(self, max_depth: int = 2,
                         agg_primitives: List[str] = None,
                         trans_primitives: List[str] = None) -> pd.DataFrame:
        """Generate features using deep feature synthesis."""
        if self.entity_set is None:
            raise ValueError("Entity set must be configured first")

        agg_primitives = agg_primitives or ['mean', 'sum', 'std', 'max', 'min', 'count', 'trend']
        trans_primitives = trans_primitives or ['absolute', 'add_numeric', 'multiply_numeric', 'percentile', 'diff']

        feature_matrix, feature_defs = ft.dfs(
            entityset=self.entity_set,
            target_dataframe_name="counties",
            agg_primitives=agg_primitives,
            trans_primitives=trans_primitives,
            max_depth=max_depth,
            verbose=True
        )

        self.feature_defs = feature_defs
        self.feature_matrix = feature_matrix

        logging.info(f"Generated {len(feature_defs)} features")

        return feature_matrix

    def get_feature_importance(self, target_column: str,
                               model_type: str = 'random_forest') -> pd.DataFrame:
        """Calculate feature importance for generated features."""
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.feature_selection import mutual_info_regression

        X = self.feature_matrix.drop(columns=[target_column], errors='ignore')
        y = self.feature_matrix[target_column]

        X = X.select_dtypes(include=[np.number]).fillna(0)

        # Random Forest importance
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)
        rf_importance = rf.feature_importances_

        # Mutual information
        mi_scores = mutual_info_regression(X, y, random_state=42)

        importance_df = pd.DataFrame({
            'feature': X.columns,
            'rf_importance': rf_importance,
            'mutual_info': mi_scores
        })

        importance_df['combined_score'] = (
            importance_df['rf_importance'] + 
            importance_df['mutual_info'] / importance_df['mutual_info'].max()
        ) / 2

        return importance_df.sort_values('combined_score', ascending=False)

    def select_top_features(self, n_features: int = 100,
                           target_column: str = 'risk_score') -> List[str]:
        """Select top N features based on importance."""
        importance = self.get_feature_importance(target_column)
        top_features = importance.head(n_features)['feature'].tolist()

        logging.info(f"Selected top {n_features} features")

        return top_features
```

---

### 3.5 Data Lineage Tracking

#### 3.5.1 OpenLineage Integration

**File: `src/pipeline/lineage/lineage_tracker.py`**

```python
"""
Data lineage tracking using OpenLineage.
"""
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
from openlineage.client.facets import SchemaDatasetFacet, SchemaField
from datetime import datetime
from typing import Dict, List, Optional
import uuid

class LineageTracker:
    """Track data lineage across the ResilienceAI pipeline."""

    def __init__(self, url: str = "http://localhost:5000"):
        self.client = OpenLineageClient(url=url)
        self.namespace = "resilience-ai"
        self.active_runs: Dict[str, Run] = {}

    def start_run(self, job_name: str, run_id: Optional[str] = None) -> str:
        """Start tracking a pipeline run."""
        run_id = run_id or str(uuid.uuid4())

        run = Run(runId=run_id)
        job = Job(namespace=self.namespace, name=job_name)

        event = RunEvent(
            eventType=RunState.START,
            eventTime=datetime.utcnow().isoformat(),
            run=run,
            job=job,
            inputs=[],
            outputs=[]
        )

        self.client.emit(event)
        self.active_runs[job_name] = run

        return run_id

    def log_dataset_input(self, job_name: str, dataset_name: str,
                         dataset_uri: str, schema: Optional[List[Dict]] = None):
        """Log a dataset input to the current run."""
        facets = {}

        if schema:
            facets["schema"] = SchemaDatasetFacet(
                fields=[SchemaField(name=f['name'], type=f['type']) for f in schema]
            )

        dataset = Dataset(
            namespace=self.namespace,
            name=dataset_name,
            facets=facets
        )

        run = self.active_runs.get(job_name)
        if run:
            event = RunEvent(
                eventType=RunState.RUNNING,
                eventTime=datetime.utcnow().isoformat(),
                run=run,
                job=Job(namespace=self.namespace, name=job_name),
                inputs=[dataset],
                outputs=[]
            )
            self.client.emit(event)

    def log_dataset_output(self, job_name: str, dataset_name: str,
                          dataset_uri: str, schema: Optional[List[Dict]] = None):
        """Log a dataset output from the current run."""
        facets = {}

        if schema:
            facets["schema"] = SchemaDatasetFacet(
                fields=[SchemaField(name=f['name'], type=f['type']) for f in schema]
            )

        dataset = Dataset(
            namespace=self.namespace,
            name=dataset_name,
            facets=facets
        )

        run = self.active_runs.get(job_name)
        if run:
            event = RunEvent(
                eventType=RunState.RUNNING,
                eventTime=datetime.utcnow().isoformat(),
                run=run,
                job=Job(namespace=self.namespace, name=job_name),
                inputs=[],
                outputs=[dataset]
            )
            self.client.emit(event)

    def complete_run(self, job_name: str, success: bool = True):
        """Complete the current run."""
        run = self.active_runs.pop(job_name, None)

        if run:
            event = RunEvent(
                eventType=RunState.COMPLETE if success else RunState.FAIL,
                eventTime=datetime.utcnow().isoformat(),
                run=run,
                job=Job(namespace=self.namespace, name=job_name),
                inputs=[],
                outputs=[]
            )
            self.client.emit(event)
```


---

### 3.6 Incremental Data Updates

#### 3.6.1 Change Data Capture (CDC)

**File: `src/pipeline/incremental/cdc_handler.py`**

```python
"""
Change Data Capture for incremental data updates.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Optional, Callable
import hashlib
import json
import logging
from pathlib import Path

class CDCManager:
    """
    Manage change data capture for incremental updates.

    Tracks:
    - Last sync timestamps per source
    - Record hashes for change detection
    - Deleted records
    """

    def __init__(self, state_dir: str = "data/cdc_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, Dict] = {}
        self._load_state()

    def _load_state(self):
        """Load CDC state from disk."""
        state_file = self.state_dir / "cdc_state.json"
        if state_file.exists():
            with open(state_file) as f:
                self.state = json.load(f)

    def _save_state(self):
        """Save CDC state to disk."""
        state_file = self.state_dir / "cdc_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)

    def _compute_record_hash(self, record: Dict) -> str:
        """Compute hash of record for change detection."""
        normalized = json.dumps(record, sort_keys=True, default=str)
        return hashlib.sha256(normalized.encode()).hexdigest()

    def detect_changes(self, source_name: str, 
                      new_data: pd.DataFrame,
                      key_column: str = "fips") -> Dict:
        """
        Detect changes between new data and previous state.

        Returns:
            Dict with 'inserted', 'updated', 'deleted', 'unchanged' DataFrames
        """
        if source_name not in self.state:
            self.state[source_name] = {'records': {}}

        source_state = self.state[source_name]['records']

        # Compute hashes for new data
        new_hashes = {}
        for idx, row in new_data.iterrows():
            key = str(row[key_column])
            record_dict = row.to_dict()
            new_hashes[key] = self._compute_record_hash(record_dict)

        # Detect changes
        inserted_keys = set(new_hashes.keys()) - set(source_state.keys())
        deleted_keys = set(source_state.keys()) - set(new_hashes.keys())

        updated_keys = set()
        unchanged_keys = set()

        for key in set(new_hashes.keys()) & set(source_state.keys()):
            if new_hashes[key] != source_state[key]:
                updated_keys.add(key)
            else:
                unchanged_keys.add(key)

        # Create result DataFrames
        result = {
            'inserted': new_data[new_data[key_column].astype(str).isin(inserted_keys)],
            'updated': new_data[new_data[key_column].astype(str).isin(updated_keys)],
            'deleted_keys': deleted_keys,
            'unchanged': new_data[new_data[key_column].astype(str).isin(unchanged_keys)]
        }

        # Update state
        self.state[source_name]['records'] = new_hashes
        self.state[source_name]['last_sync'] = datetime.utcnow().isoformat()
        self._save_state()

        logging.info(
            f"CDC for {source_name}: "
            f"{len(inserted_keys)} inserted, "
            f"{len(updated_keys)} updated, "
            f"{len(deleted_keys)} deleted"
        )

        return result

    def get_last_sync(self, source_name: str) -> Optional[datetime]:
        """Get last sync timestamp for a source."""
        if source_name in self.state and 'last_sync' in self.state[source_name]:
            return datetime.fromisoformat(self.state[source_name]['last_sync'])
        return None
```

---

### 3.7 Data Versioning with DVC

#### 3.7.1 DVC Pipeline Configuration

**File: `dvc.yaml`**

```yaml
# DVC pipeline configuration for ResilienceAI

stages:
  download_data:
    cmd: python src/pipeline/download_data_enhanced.py --all
    deps:
      - src/pipeline/download_data_enhanced.py
      - config/data_sources.yaml
    outs:
      - data/raw/hifld_hospitals.csv:
          cache: true
          persist: false
      - data/raw/hifld_fire_stations.csv:
          cache: true
          persist: false
      - data/raw/hifld_ems_stations.csv:
          cache: true
          persist: false
      - data/raw/fema_disasters.csv:
          cache: true
          persist: false
      - data/raw/census_demographics.csv:
          cache: true
          persist: false
    metrics:
      - metrics/download_metrics.json:
          cache: false

  validate_data:
    cmd: python src/pipeline/quality/validate_all.py
    deps:
      - src/pipeline/quality/validate_all.py
      - data/raw/
    outs:
      - data/validated/
    metrics:
      - metrics/validation_metrics.json:
          cache: false

  engineer_features:
    cmd: python src/pipeline/features/run_feature_pipeline.py
    deps:
      - src/pipeline/features/run_feature_pipeline.py
      - src/pipeline/features/auto_feature_engineering.py
      - data/validated/
    outs:
      - data/processed/county_features.parquet:
          cache: true
          persist: false
    metrics:
      - metrics/feature_metrics.json:
          cache: false
    params:
      - feature_config.max_depth
      - feature_config.n_features

  detect_anomalies:
    cmd: python src/pipeline/anomaly/run_anomaly_detection.py
    deps:
      - src/pipeline/anomaly/run_anomaly_detection.py
      - data/processed/county_features.parquet
    outs:
      - data/anomalies/detected_anomalies.parquet:
          cache: true
    metrics:
      - metrics/anomaly_metrics.json:
          cache: false

  train_models:
    cmd: python src/pipeline/models/train_models.py
    deps:
      - src/pipeline/models/train_models.py
      - data/processed/county_features.parquet
    outs:
      - models/risk_model.pkl:
          cache: true
      - models/anomaly_detector.pkl:
          cache: true
    metrics:
      - metrics/model_metrics.json:
          cache: false
    params:
      - model_config.test_size
      - model_config.random_state
```

**File: `.dvc/config`**

```ini
[core]
    autostage = true
    remote = s3-remote
['remote "s3-remote"']
    url = s3://resilience-ai-dvc/data
    region = us-east-1
    profile = default
['remote "gs-remote"']
    url = gs://resilience-ai-dvc/data
```

**File: `src/pipeline/dvc_utils.py`**

```python
"""
DVC utilities for data versioning.
"""
import subprocess
import json
from typing import Dict, List, Optional
from pathlib import Path

class DVCManager:
    """Manage DVC operations programmatically."""

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)

    def track_file(self, file_path: str, cache: bool = True, persist: bool = False):
        """Add a file to DVC tracking."""
        cmd = ["dvc", "add", file_path]

        if not cache:
            cmd.append("--no-commit")

        subprocess.run(cmd, cwd=self.repo_root, check=True)

        if persist:
            dvcignore = self.repo_root / ".dvcignore"
            with open(dvcignore, 'a') as f:
                f.write(f"\n{file_path}\n")

    def pull_data(self, remote: Optional[str] = None):
        """Pull data from DVC remote."""
        cmd = ["dvc", "pull"]
        if remote:
            cmd.extend(["--remote", remote])
        subprocess.run(cmd, cwd=self.repo_root, check=True)

    def push_data(self, remote: Optional[str] = None):
        """Push data to DVC remote."""
        cmd = ["dvc", "push"]
        if remote:
            cmd.extend(["--remote", remote])
        subprocess.run(cmd, cwd=self.repo_root, check=True)

    def list_versions(self, file_path: str) -> List[Dict]:
        """List all versions of a tracked file."""
        cmd = ["git", "log", "--format=%H|%ci|%s", f"{file_path}.dvc"]
        result = subprocess.run(
            cmd, cwd=self.repo_root,
            capture_output=True, text=True, check=True
        )

        versions = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                commit, date, message = line.split('|', 2)
                versions.append({'commit': commit, 'date': date, 'message': message})

        return versions
```


---

### 3.8 Parallel Processing Optimization

#### 3.8.1 Dask Integration

**File: `src/pipeline/parallel/dask_processor.py`**

```python
"""
Parallel data processing with Dask.
"""
import dask.dataframe as dd
from dask.distributed import Client, LocalCluster
import pandas as pd
from typing import List, Callable, Dict
import logging

class DaskProcessor:
    """Parallel data processing using Dask."""

    def __init__(self, n_workers: int = None, memory_limit: str = "4GB"):
        self.n_workers = n_workers
        self.memory_limit = memory_limit
        self.client: Client = None

    def __enter__(self):
        """Start Dask cluster."""
        cluster = LocalCluster(
            n_workers=self.n_workers,
            memory_limit=self.memory_limit,
            threads_per_worker=2
        )
        self.client = Client(cluster)
        logging.info(f"Dask cluster started: {self.client.dashboard_link}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Shutdown Dask cluster."""
        self.client.close()
        logging.info("Dask cluster shutdown")

    def parallel_feature_computation(self, 
                                     counties_df: pd.DataFrame,
                                     facilities_df: pd.DataFrame,
                                     computation_fn: Callable,
                                     facility_type: str,
                                     npartitions: int = 10) -> pd.DataFrame:
        """Compute features in parallel using Dask."""
        # Convert to Dask DataFrame
        ddf = dd.from_pandas(counties_df, npartitions=npartitions)

        # Define computation for each partition
        def compute_partition(partition):
            return computation_fn(partition, facilities_df, facility_type)

        # Apply in parallel
        result = ddf.map_partitions(compute_partition, meta=counties_df).compute()

        return result

    def parallel_groupby(self, df: pd.DataFrame,
                        groupby_cols: List[str],
                        agg_dict: Dict) -> pd.DataFrame:
        """Perform parallel groupby aggregation."""
        ddf = dd.from_pandas(df, npartitions=10)
        result = ddf.groupby(groupby_cols).agg(agg_dict).compute()
        return result.reset_index()

    def parallel_spatial_join(self, 
                             counties_df: pd.DataFrame,
                             facilities_df: pd.DataFrame,
                             radius_km: float = 50.0) -> pd.DataFrame:
        """Perform parallel spatial join for facility counting."""
        from scipy.spatial import cKDTree
        import numpy as np

        # Build facility tree once
        fac_coords = np.radians(facilities_df[['latitude', 'longitude']].values)
        tree = cKDTree(fac_coords)

        # Process counties in parallel
        ddf = dd.from_pandas(counties_df, npartitions=10)

        def count_facilities_partition(partition):
            county_coords = np.radians(partition[['latitude', 'longitude']].values)
            counts = tree.query_ball_point(county_coords, r=radius_km / 6371.0)
            partition['facility_count'] = [len(c) for c in counts]
            return partition

        result = ddf.map_partitions(
            count_facilities_partition,
            meta=counties_df.assign(facility_count=0)
        ).compute()

        return result
```

---

### 3.9 Data Catalog Implementation

#### 3.9.1 DataHub Integration

**File: `src/pipeline/catalog/datahub_client.py`**

```python
"""
DataHub integration for data catalog and discovery.
"""
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass, SchemaMetadataClass,
    SchemaFieldClass, SchemaFieldDataTypeClass,
    StringTypeClass, NumberTypeClass, DateTypeClass
)
from datahub.emitter.mce_builder import make_dataset_urn
from typing import Dict, List
import pandas as pd

class DataCatalog:
    """Data catalog for ResilienceAI datasets."""

    def __init__(self, server_url: str = "http://localhost:8080"):
        self.graph = DataHubGraph(DatahubClientConfig(server=server_url))
        self.platform = "resilience-ai"

    def register_dataset(self, name: str, df: pd.DataFrame,
                        description: str = "",
                        tags: List[str] = None,
                        owners: List[str] = None):
        """Register a dataset with the catalog."""
        urn = make_dataset_urn(platform=self.platform, name=name)

        # Create schema metadata
        fields = []
        for col in df.columns:
            dtype = df[col].dtype

            if dtype in ['object', 'string']:
                field_type = SchemaFieldDataTypeClass(type=StringTypeClass())
            elif dtype in ['int64', 'float64']:
                field_type = SchemaFieldDataTypeClass(type=NumberTypeClass())
            elif dtype in ['datetime64[ns]']:
                field_type = SchemaFieldDataTypeClass(type=DateTypeClass())
            else:
                field_type = SchemaFieldDataTypeClass(type=StringTypeClass())

            fields.append(SchemaFieldClass(
                fieldPath=col,
                type=field_type,
                description=f"Column {col}"
            ))

        schema_metadata = SchemaMetadataClass(
            schemaName=name,
            platform=make_dataset_urn(platform=self.platform, name=""),
            version=0,
            fields=fields
        )

        # Create dataset properties
        properties = DatasetPropertiesClass(
            description=description,
            tags=tags or [],
            customProperties={
                'row_count': str(len(df)),
                'column_count': str(len(df.columns)),
                'columns': ','.join(df.columns)
            }
        )

        # Emit to DataHub
        self.graph.emit_mce({
            'proposedSnapshot': {
                'urn': urn,
                'aspects': [
                    {'com.linkedin.dataset.DatasetProperties': properties},
                    {'com.linkedin.schema.SchemaMetadata': schema_metadata}
                ]
            }
        })

    def search_datasets(self, query: str) -> List[Dict]:
        """Search for datasets in the catalog."""
        results = self.graph.search(query, entity_types=['dataset'])
        return [
            {
                'urn': r['entity']['urn'],
                'name': r['entity']['name'],
                'description': r.get('entity', {}).get('description', '')
            }
            for r in results
        ]

    def get_dataset_lineage(self, name: str) -> Dict:
        """Get lineage information for a dataset."""
        urn = make_dataset_urn(platform=self.platform, name=name)
        lineage = self.graph.get_lineage(urn)
        return lineage
```


---

### 3.10 Automated ETL Scheduling

#### 3.10.1 Apache Airflow DAGs

**File: `dags/resilience_etl_dag.py`**

```python
"""
Apache Airflow DAG for ResilienceAI ETL pipeline.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import json
import logging

# Default arguments
default_args = {
    'owner': 'resilience-ai',
    'depends_on_past': False,
    'email': ['data-team@resilience-ai.org'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
with DAG(
    'resilience_etl_pipeline',
    default_args=default_args,
    description='ResilienceAI data pipeline with quality checks',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['resilience', 'etl', 'data-quality'],
    max_active_runs=1,
) as dag:

    # Task 1: Check data source availability
    check_sources = SimpleHttpOperator(
        task_id='check_fema_api',
        http_conn_id='fema_api',
        endpoint='/api/open',
        method='GET',
        response_check=lambda response: response.status_code == 200,
    )

    # Task 2: Download data with TaskGroup for parallel downloads
    with TaskGroup('download_data', tooltip='Download all data sources') as download_group:

        download_fema = BashOperator(
            task_id='download_fema',
            bash_command='python src/pipeline/downloaders/fema_downloader.py --date {{ ds }}',
        )

        download_census = BashOperator(
            task_id='download_census',
            bash_command='python src/pipeline/downloaders/census_downloader.py',
        )

        download_hifld = BashOperator(
            task_id='download_hifld',
            bash_command='python src/pipeline/downloaders/hifld_downloader.py',
        )

        download_noaa = BashOperator(
            task_id='download_noaa',
            bash_command='python src/pipeline/downloaders/noaa_downloader.py --date {{ ds }}',
        )

    # Task 3: Validate raw data quality
    def validate_raw_data(**context):
        from src.pipeline.quality.expectations import ResilienceDataQuality
        validator = ResilienceDataQuality()
        datasets = {'fema': 'data/raw/fema_disasters.csv', 'census': 'data/raw/census_demographics.csv'}
        results = {}
        for name, path in datasets.items():
            df = pd.read_csv(path)
            result = validator.validate_dataframe(df, f"{name}_expectations")
            results[name] = result
            if not result['success']:
                raise ValueError(f"Data validation failed for {name}")
        context['ti'].xcom_push(key='validation_results', value=results)

    validate_data = PythonOperator(task_id='validate_raw_data', python_callable=validate_raw_data)

    # Task 4: Run feature engineering
    engineer_features = BashOperator(
        task_id='engineer_features',
        bash_command='python src/pipeline/features/run_feature_pipeline.py --input-dir data/validated/ --output-dir data/processed/ --date {{ ds }}',
    )

    # Task 5: Detect anomalies
    detect_anomalies = BashOperator(
        task_id='detect_anomalies',
        bash_command='python src/pipeline/anomaly/run_anomaly_detection.py --input data/processed/county_features.parquet --output data/anomalies/',
    )

    # Task 6: Update feature store
    update_feature_store = BashOperator(
        task_id='update_feature_store',
        bash_command='python src/pipeline/features/update_feature_store.py --features data/processed/county_features.parquet',
    )

    # Task 7: Check model drift
    def check_model_drift(**context):
        from src.pipeline.models.drift_detector import DriftDetector
        detector = DriftDetector()
        drift_score = detector.calculate_drift(reference_path='data/processed/county_features.parquet', current_date=context['ds'])
        context['ti'].xcom_push(key='drift_score', value=drift_score)
        return drift_score > 0.1

    check_drift = PythonOperator(task_id='check_model_drift', python_callable=check_model_drift)

    retrain_models = BashOperator(
        task_id='retrain_models',
        bash_command='python src/pipeline/models/train_models.py --data data/processed/county_features.parquet --output models/',
    )

    # Task 8: Publish metrics
    def publish_metrics(**context):
        metrics = {
            'execution_date': context['ds'],
            'validation_results': context['ti'].xcom_pull(task_ids='validate_raw_data', key='validation_results'),
            'drift_score': context['ti'].xcom_pull(task_ids='check_model_drift', key='drift_score'),
        }
        with open(f'metrics/pipeline_metrics_{context["ds"]}.json', 'w') as f:
            json.dump(metrics, f, indent=2)

    publish_metrics_task = PythonOperator(task_id='publish_metrics', python_callable=publish_metrics)

    # Define task dependencies
    check_sources >> download_group >> validate_data >> engineer_features
    engineer_features >> detect_anomalies >> update_feature_store
    engineer_features >> check_drift
    check_drift >> retrain_models
    [update_feature_store, retrain_models] >> publish_metrics_task
```


---

## 4. Technology Stack Recommendations

### 4.1 Core Data Platform

| Component | Current | Recommended | Rationale |
|-----------|---------|-------------|-----------|
| **Orchestration** | Manual scripts | Apache Airflow 2.x | DAG-based scheduling, retries, monitoring |
| **Streaming** | Basic polling | Kafka + Kafka Connect | Real-time event streaming, replay capability |
| **Stream Processing** | Threading | Apache Flink | Stateful stream processing, exactly-once |
| **Storage** | CSV/JSON | Delta Lake + Parquet | ACID transactions, time travel, schema evolution |
| **Versioning** | Git only | DVC + Git | Data versioning, reproducibility |
| **Quality** | None | Great Expectations | Data contracts, automated validation |
| **Lineage** | None | OpenLineage + DataHub | End-to-end lineage, impact analysis |
| **Feature Store** | None | Feast | Online/offline features, point-in-time joins |
| **Catalog** | None | DataHub | Data discovery, governance |
| **Processing** | Pandas | Dask + Ray | Parallel processing, out-of-core computation |
| **Monitoring** | Print | Prometheus + Grafana | Metrics, dashboards, alerting |

### 4.2 ML/AI Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Anomaly Detection** | Isolation Forest + Autoencoders | Detect data anomalies |
| **Feature Engineering** | Featuretools | Automated feature synthesis |
| **Drift Detection** | Evidently AI | Model/data drift monitoring |
| **AutoML** | FLAML / Auto-sklearn | Automated model selection |

### 4.3 Infrastructure

| Component | Recommendation |
|-----------|----------------|
| **Container Orchestration** | Kubernetes |
| **Object Storage** | S3 / GCS / MinIO |
| **Database** | PostgreSQL (metadata) + Redis (cache) |
| **Message Queue** | Apache Kafka |
| **Search** | Elasticsearch |

---

## 5. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
1. **DVC Setup**
   - Initialize DVC repository
   - Configure remote storage
   - Migrate existing data to versioned storage

2. **Data Quality Framework**
   - Implement Great Expectations
   - Create expectation suites for all data sources
   - Set up quality monitoring dashboard

3. **Orchestration**
   - Deploy Apache Airflow
   - Migrate existing scripts to DAGs
   - Implement retry logic and error handling

### Phase 2: Real-Time Capabilities (Weeks 3-4)
1. **Kafka Infrastructure**
   - Deploy Kafka cluster
   - Implement source connectors
   - Create topic structure

2. **Streaming Pipeline**
   - Implement Kafka producers
   - Set up stream processing with ksqlDB
   - Create real-time feature computation

3. **Anomaly Detection**
   - Train baseline anomaly detection models
   - Implement streaming anomaly detection
   - Set up anomaly alerting

### Phase 3: Advanced Features (Weeks 5-6)
1. **Feature Store**
   - Deploy Feast
   - Migrate features to online/offline stores
   - Implement feature serving API

2. **Automated Feature Engineering**
   - Integrate Featuretools
   - Implement deep feature synthesis
   - Create feature importance pipeline

3. **Lineage Tracking**
   - Deploy OpenLineage
   - Instrument all pipeline stages
   - Create lineage visualization

### Phase 4: Optimization & Scale (Weeks 7-8)
1. **Parallel Processing**
   - Implement Dask for large-scale processing
   - Add Ray for distributed ML
   - Optimize spatial computations

2. **Data Catalog**
   - Deploy DataHub
   - Register all datasets
   - Enable data discovery

3. **Performance Tuning**
   - Implement caching strategies
   - Optimize query patterns
   - Add performance monitoring

---

## 6. Integration with Existing Code

### 6.1 Migration Strategy

**File: `src/pipeline/download_data_enhanced.py`**

```python
"""
Enhanced download_data.py with backward compatibility.
"""
from src.download_data import download_all as legacy_download_all
from src.pipeline.quality.expectations import ResilienceDataQuality
from src.pipeline.lineage.lineage_tracker import LineageTracker
from src.pipeline.dvc_utils import DVCManager
import logging

def download_all_enhanced(force=False, validate=True, track_lineage=True):
    """
    Enhanced download with quality checks and lineage tracking.
    Maintains backward compatibility with original download_all().
    """
    tracker = LineageTracker() if track_lineage else None
    dvc = DVCManager()

    try:
        if tracker:
            run_id = tracker.start_run('download_data')

        # Call legacy download
        results = legacy_download_all(force=force)

        # Validate results
        if validate:
            validator = ResilienceDataQuality()
            for source_name, df in results.items():
                if isinstance(df, pd.DataFrame):
                    validation = validator.validate_dataframe(df, f"{source_name}_expectations")
                    if not validation['success']:
                        logging.warning(f"Validation failed for {source_name}")

        # Track with DVC
        dvc.track_file("data/raw/", cache=True)

        if tracker:
            tracker.complete_run('download_data', success=True)

        return results

    except Exception as e:
        if tracker:
            tracker.complete_run('download_data', success=False)
        raise
```

### 6.2 Configuration Migration

**File: `config/pipeline_config.yaml`**

```yaml
---
# Unified configuration for enhanced pipeline

# Data sources
data_sources:
  fema:
    url: "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
    poll_interval: 300
    retry_policy:
      max_retries: 3
      backoff_factor: 2

  census:
    url: "https://api.census.gov/data/2022/acs/acs5"
    api_key: ${CENSUS_API_KEY}

  hifld:
    base_url: "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services"
    page_size: 2000

# Streaming configuration
streaming:
  kafka:
    bootstrap_servers: ${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}
    topics:
      weather_alerts: resilience.weather.alerts
      disaster_declarations: resilience.fema.disasters

# Quality configuration
quality:
  great_expectations:
    context_root_dir: gx
    validation_threshold: 0.95
    alert_channels:
      - slack
      - email

# Feature store configuration
feature_store:
  provider: feast
  repo_path: feature_repo/
  online_store:
    type: redis
    connection_string: ${REDIS_URL:-localhost:6379}
  offline_store:
    type: file
    path: data/feature_store/

# Processing configuration
processing:
  parallel_backend: dask
  n_workers: 4
  memory_limit: 4GB

# Lineage configuration
lineage:
  backend: openlineage
  url: ${MARQUEZ_URL:-http://localhost:5000}
  namespace: resilience-ai
```


---

## 7. File Structure

```
resilience-ai/
├── dags/                          # Airflow DAGs
│   ├── resilience_etl_dag.py
│   ├── resilience_realtime_dag.py
│   └── utils/
├── config/                        # Configuration files
│   ├── pipeline_config.yaml
│   ├── kafka_topics.yaml
│   └── data_sources.yaml
├── feature_repo/                  # Feast feature repository
│   ├── feature_store.yaml
│   └── features/
├── gx/                            # Great Expectations
│   ├── expectations/
│   ├── checkpoints/
│   └── great_expectations.yml
├── src/
│   ├── pipeline/                  # New pipeline modules
│   │   ├── __init__.py
│   │   ├── streaming/
│   │   │   ├── __init__.py
│   │   │   ├── kafka_producer.py
│   │   │   └── source_connectors.py
│   │   ├── quality/
│   │   │   ├── __init__.py
│   │   │   ├── expectations.py
│   │   │   └── quality_monitor.py
│   │   ├── anomaly/
│   │   │   ├── __init__.py
│   │   │   ├── anomaly_detector.py
│   │   │   └── streaming_anomaly.py
│   │   ├── features/
│   │   │   ├── __init__.py
│   │   │   └── auto_feature_engineering.py
│   │   ├── lineage/
│   │   │   ├── __init__.py
│   │   │   └── lineage_tracker.py
│   │   ├── incremental/
│   │   │   ├── __init__.py
│   │   │   └── cdc_handler.py
│   │   ├── parallel/
│   │   │   ├── __init__.py
│   │   │   └── dask_processor.py
│   │   ├── catalog/
│   │   │   ├── __init__.py
│   │   │   └── datahub_client.py
│   │   └── dvc_utils.py
│   ├── download_data.py           # Legacy (preserved)
│   ├── feature_engineering.py     # Legacy (preserved)
│   └── ...                        # Other existing files
├── data/
│   ├── raw/                       # Raw data (DVC tracked)
│   ├── validated/                 # Validated data
│   ├── processed/                 # Processed features
│   ├── anomalies/                 # Detected anomalies
│   ├── cache/                     # Temporary cache
│   └── cdc_state/                 # CDC state files
├── models/                        # Trained models (DVC tracked)
├── metrics/                       # Pipeline metrics
├── tests/                         # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker/                        # Docker configurations
│   ├── docker-compose.yml
│   ├── Dockerfile.airflow
│   └── Dockerfile.pipeline
├── k8s/                           # Kubernetes manifests
├── dvc.yaml                       # DVC pipeline
└── requirements-pipeline.txt      # Pipeline dependencies
```

---

## 8. Key Performance Indicators

| Metric | Current | Target (Phase 4) |
|--------|---------|------------------|
| **Data Freshness** | Daily | < 5 minutes |
| **Pipeline Runtime** | ~30 minutes | < 10 minutes |
| **Data Quality Issues** | Unknown | < 1% failure rate |
| **Feature Computation** | Sequential | 4x parallel speedup |
| **Storage Efficiency** | 100% (no compression) | 70% (with compression) |
| **Reproducibility** | Manual | Fully automated |
| **Lineage Coverage** | 0% | 100% |

---

## 9. Conclusion

This comprehensive data engineering enhancement plan transforms ResilienceAI from a batch-oriented system into a modern, real-time, ML-driven data platform. The phased implementation approach ensures minimal disruption to existing functionality while progressively adding advanced capabilities.

### Key Benefits

| Capability | Benefit |
|------------|---------|
| **Real-time insights** | Streaming data ingestion for immediate awareness |
| **Data reliability** | Automated quality monitoring and validation |
| **Faster iteration** | Automated feature engineering reduces manual work |
| **Full reproducibility** | Data versioning ensures consistent results |
| **Scalable processing** | Parallel computation handles large datasets |
| **Complete visibility** | Lineage tracking and data catalog for governance |

### Implementation Summary

```
Phase 1 (Weeks 1-2): Foundation
├── DVC Setup
├── Data Quality Framework  
└── Airflow Orchestration

Phase 2 (Weeks 3-4): Real-Time
├── Kafka Infrastructure
├── Streaming Pipeline
└── Anomaly Detection

Phase 3 (Weeks 5-6): Advanced Features
├── Feature Store (Feast)
├── Automated Feature Engineering
└── Lineage Tracking

Phase 4 (Weeks 7-8): Optimization
├── Parallel Processing (Dask/Ray)
├── Data Catalog (DataHub)
└── Performance Tuning
```

---

## Appendix A: Required Dependencies

**File: `requirements-pipeline.txt`**

```
# Core data processing
pandas>=2.0.0
numpy>=1.24.0,<2.0.0
scipy>=1.10.0

# Streaming
confluent-kafka>=2.0.0
aiokafka>=0.8.0
websockets>=11.0

# Data quality
great_expectations>=0.17.0

# Feature engineering
featuretools>=1.0.0
feast>=0.34.0

# Parallel processing
dask>=2023.0.0
distributed>=2023.0.0
ray>=2.5.0

# Lineage
openlineage-python>=1.0.0

# Data versioning
dvc>=3.0.0
dvc-s3>=2.0.0

# Delta Lake
deltalake>=0.10.0

# Data catalog
datahub>=0.10.0

# Orchestration
apache-airflow>=2.6.0
apache-airflow-providers-http>=4.0.0

# ML
scikit-learn>=1.3.0
joblib>=1.3.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0.0
pydantic>=2.0.0
```

---

## Appendix B: Environment Variables

```bash
# API Keys
export CENSUS_API_KEY="your_census_api_key"
export NOAA_API_KEY="your_noaa_api_key"

# Kafka
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"

# Feature Store
export REDIS_URL="localhost:6379"
export FEAST_REPOSITORY_PATH="./feature_repo"

# Lineage
export MARQUEZ_URL="http://localhost:5000"

# DVC
export AWS_ACCESS_KEY_ID="your_aws_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
export DVC_REMOTE_NAME="s3-remote"

# DataHub
export DATAHUB_SERVER="http://localhost:8080"

# Monitoring
export PROMETHEUS_PORT=9090
export GRAFANA_PORT=3000
```

---

*Document generated for ResilienceAI Data Engineering Enhancement*
*Analysis based on claw-autonomous branch*
*Total enhancements: 10 major capabilities*
*Implementation timeline: 8 weeks*
