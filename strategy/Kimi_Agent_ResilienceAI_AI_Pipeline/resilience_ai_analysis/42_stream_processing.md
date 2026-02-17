# ResilienceAI Stream Processing Architecture

## Executive Summary

This document presents a comprehensive stream processing architecture for ResilienceAI, designed to handle real-time data ingestion, processing, and analytics at enterprise scale. The architecture leverages Apache Kafka as the primary streaming platform with Redis Streams for high-speed caching and state management.

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           RESILIENCEAI STREAM PLATFORM                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Sources    │    │   Sources    │    │   Sources    │    │   Sources    │  │
│  │  IoT Sensors │    │   APIs       │    │   Logs       │    │   Metrics    │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │                   │          │
│         └───────────────────┴───────────────────┴───────────────────┘          │
│                                     │                                           │
│                              ┌──────┴──────┐                                    │
│                              │    Kafka    │                                    │
│                              │   Cluster   │                                    │
│                              └──────┬──────┘                                    │
│                                     │                                           │
│         ┌───────────────────────────┼───────────────────────────┐               │
│         │                           │                           │               │
│  ┌──────┴──────┐            ┌──────┴──────┐            ┌──────┴──────┐         │
│  │  Stream     │            │   Stream    │            │   Stream    │         │
│  │ Processing  │            │  Analytics  │            │     CEP     │         │
│  │   Layer     │            │   Engine    │            │   Engine    │         │
│  └──────┬──────┘            └──────┬──────┘            └──────┬──────┘         │
│         │                           │                           │               │
│         └───────────────────────────┼───────────────────────────┘               │
│                                     │                                           │
│                              ┌──────┴──────┐                                    │
│                              │    Redis    │                                    │
│                              │   Streams   │                                    │
│                              └──────┬──────┘                                    │
│                                     │                                           │
│         ┌───────────────────────────┼───────────────────────────┐               │
│         │                           │                           │               │
│  ┌──────┴──────┐            ┌──────┴──────┐            ┌──────┴──────┐         │
│  │  Storage    │            │  Real-time  │            │  Monitoring │         │
│  │  (TSDB)     │            │   APIs      │            │  & Alerts   │         │
│  └─────────────┘            └─────────────┘            └─────────────┘         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        STREAM PROCESSING LAYERS                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      INGESTION LAYER                                   │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │ │
│  │  │ Kafka   │  │ Kafka   │  │ Kafka   │  │ Schema  │  │ Dead    │      │ │
│  │  │ Connect │  │ Producers│  │ Topics  │  │ Registry│  │ Letter  │      │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    PROCESSING LAYER (Kafka Streams/Flink)              │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │ │
│  │  │ Filter  │  │  Map    │  │ Window  │  │  Join   │  │ Aggregate│      │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │ │
│  │  │ Enrich  │  │ Transform│  │ Branch  │  │  CEP    │  │  Sink   │      │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      STATE LAYER (Redis)                               │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │ │
│  │  │ Streams │  │  State  │  │  Cache  │  │ Pub/Sub │  │  Locks  │      │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     ANALYTICS LAYER                                    │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │ │
│  │  │ Real-time│  │ Windowed│  │ Pattern │  │ Anomaly │  │ Predict │      │ │
│  │  │ Metrics │  │ Analytics│  │ Detect  │  │ Detect  │  │  ive    │      │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     SERVING LAYER                                      │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │ │
│  │  │ Query   │  │  API    │  │ WebSocket│  │  SSE    │  │ Dashboard│      │ │
│  │  │ Engine  │  │ Gateway │  │  Server  │  │ Server  │  │  API    │      │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Selection

### 2.1 Technology Stack

| Component | Technology | Purpose | Justification |
|-----------|-----------|---------|---------------|
| **Streaming Platform** | Apache Kafka | Event streaming backbone | Industry standard, high throughput, excellent ecosystem |
| **Stream Processing** | Kafka Streams / Flink | Real-time processing | Native Kafka integration, exactly-once semantics |
| **Fast Cache/State** | Redis Streams | High-speed state & caching | Sub-millisecond latency, rich data structures |
| **Schema Management** | Confluent Schema Registry | Data governance | Avro/Protobuf/JSON Schema support |
| **Monitoring** | Prometheus + Grafana | Metrics & visualization | Native Kafka metrics, customizable dashboards |
| **Storage** | TimescaleDB / ClickHouse | Time-series analytics | Optimized for time-series, SQL interface |
| **CEP Engine** | Siddhi / Flink CEP | Complex event processing | Pattern matching, temporal reasoning |

### 2.2 Technology Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STREAM PROCESSING TECHNOLOGY COMPARISON                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Kafka Streams vs Apache Flink vs Spark Streaming                           │
│                                                                             │
│  ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐ │
│  │    Criteria     │  Kafka Streams  │  Apache Flink   │ Spark Streaming │ │
│  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤ │
│  │ Latency         │    ~100ms       │    ~10ms        │    ~1s          │ │
│  │ Throughput      │    High         │    Very High    │    High         │ │
│  │ Exactly-Once    │    Yes          │    Yes          │    Yes          │ │
│  │ State Mgmt      │    Built-in     │    Advanced     │    Basic        │ │
│  │ Windowing       │    Good         │    Excellent    │    Good         │ │
│  │ CEP Support     │    Limited      │    Excellent    │    Limited      │ │
│  │ Learning Curve  │    Low          │    Medium       │    Medium       │ │
│  │ Kafka Native    │    Yes          │    Connector    │    Connector    │ │
│  │ Deployment      │    Embedded     │    Cluster      │    Cluster      │ │
│  └─────────────────┴─────────────────┴─────────────────┴─────────────────┘ │
│                                                                             │
│  RECOMMENDATION: Use Kafka Streams for standard processing, Flink for CEP   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Kafka Architecture Design

### 3.1 Topic Design

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/config/topics.py
"""
Kafka Topic Configuration for ResilienceAI
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class TopicCategory(Enum):
    RAW = "raw"
    PROCESSED = "processed"
    AGGREGATED = "aggregated"
    ALERTS = "alerts"
    COMMANDS = "commands"
    EVENTS = "events"

@dataclass
class TopicConfig:
    name: str
    partitions: int
    replication_factor: int
    retention_ms: int
    cleanup_policy: str
    compression_type: str
    category: TopicCategory
    description: str

# Topic Definitions
TOPICS = {
    # Raw Data Topics
    "raw.iot.sensors": TopicConfig(
        name="raw.iot.sensors",
        partitions=12,
        replication_factor=3,
        retention_ms=86400000,  # 24 hours
        cleanup_policy="delete",
        compression_type="lz4",
        category=TopicCategory.RAW,
        description="Raw IoT sensor readings"
    ),
    "raw.system.metrics": TopicConfig(
        name="raw.system.metrics",
        partitions=8,
        replication_factor=3,
        retention_ms=86400000,
        cleanup_policy="delete",
        compression_type="lz4",
        category=TopicCategory.RAW,
        description="Raw system metrics"
    ),
    "raw.application.logs": TopicConfig(
        name="raw.application.logs",
        partitions=16,
        replication_factor=3,
        retention_ms=604800000,  # 7 days
        cleanup_policy="delete",
        compression_type="lz4",
        category=TopicCategory.RAW,
        description="Application log events"
    ),
    "raw.security.events": TopicConfig(
        name="raw.security.events",
        partitions=6,
        replication_factor=3,
        retention_ms=2592000000,  # 30 days
        cleanup_policy="compact,delete",
        compression_type="lz4",
        category=TopicCategory.RAW,
        description="Security-related events"
    ),
    
    # Processed Topics
    "processed.sensor.enriched": TopicConfig(
        name="processed.sensor.enriched",
        partitions=12,
        replication_factor=3,
        retention_ms=86400000,
        cleanup_policy="delete",
        compression_type="lz4",
        category=TopicCategory.PROCESSED,
        description="Enriched sensor data with metadata"
    ),
    "processed.metrics.normalized": TopicConfig(
        name="processed.metrics.normalized",
        partitions=8,
        replication_factor=3,
        retention_ms=86400000,
        cleanup_policy="delete",
        compression_type="lz4",
        category=TopicCategory.PROCESSED,
        description="Normalized and cleaned metrics"
    ),
    
    # Aggregated Topics
    "aggregated.metrics.1min": TopicConfig(
        name="aggregated.metrics.1min",
        partitions=8,
        replication_factor=3,
        retention_ms=604800000,  # 7 days
        cleanup_policy="compact,delete",
        compression_type="lz4",
        category=TopicCategory.AGGREGATED,
        description="1-minute metric aggregations"
    ),
    "aggregated.metrics.5min": TopicConfig(
        name="aggregated.metrics.5min",
        partitions=8,
        replication_factor=3,
        retention_ms=2592000000,  # 30 days
        cleanup_policy="compact,delete",
        compression_type="lz4",
        category=TopicCategory.AGGREGATED,
        description="5-minute metric aggregations"
    ),
    "aggregated.metrics.1hour": TopicConfig(
        name="aggregated.metrics.1hour",
        partitions=8,
        replication_factor=3,
        retention_ms=7776000000,  # 90 days
        cleanup_policy="compact,delete",
        compression_type="lz4",
        category=TopicCategory.AGGREGATED,
        description="1-hour metric aggregations"
    ),
    
    # Alert Topics
    "alerts.critical": TopicConfig(
        name="alerts.critical",
        partitions=4,
        replication_factor=3,
        retention_ms=2592000000,  # 30 days
        cleanup_policy="compact",
        compression_type="none",  # Minimize latency
        category=TopicCategory.ALERTS,
        description="Critical alerts requiring immediate action"
    ),
    "alerts.warning": TopicConfig(
        name="alerts.warning",
        partitions=4,
        replication_factor=3,
        retention_ms=2592000000,
        cleanup_policy="compact",
        compression_type="lz4",
        category=TopicCategory.ALERTS,
        description="Warning alerts"
    ),
    "alerts.info": TopicConfig(
        name="alerts.info",
        partitions=4,
        replication_factor=3,
        retention_ms=604800000,
        cleanup_policy="delete",
        compression_type="lz4",
        category=TopicCategory.ALERTS,
        description="Informational alerts"
    ),
    
    # Command Topics
    "commands.device.control": TopicConfig(
        name="commands.device.control",
        partitions=6,
        replication_factor=3,
        retention_ms=86400000,
        cleanup_policy="compact",
        compression_type="lz4",
        category=TopicCategory.COMMANDS,
        description="Device control commands"
    ),
    
    # Event Topics
    "events.anomaly.detected": TopicConfig(
        name="events.anomaly.detected",
        partitions=8,
        replication_factor=3,
        retention_ms=2592000000,
        cleanup_policy="compact,delete",
        compression_type="lz4",
        category=TopicCategory.EVENTS,
        description="Anomaly detection events"
    ),
    "events.pattern.matched": TopicConfig(
        name="events.pattern.matched",
        partitions=8,
        replication_factor=3,
        retention_ms=2592000000,
        cleanup_policy="compact,delete",
        compression_type="lz4",
        category=TopicCategory.EVENTS,
        description="Complex pattern match events"
    ),
}

def get_topic_config(topic_name: str) -> Optional[TopicConfig]:
    """Get configuration for a specific topic."""
    return TOPICS.get(topic_name)

def get_topics_by_category(category: TopicCategory) -> List[TopicConfig]:
    """Get all topics for a specific category."""
    return [config for config in TOPICS.values() if config.category == category]


### 3.2 Consumer Group Design

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/config/consumer_groups.py
"""
Consumer Group Configuration for ResilienceAI
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ConsumerGroupConfig:
    group_id: str
    topics: List[str]
    parallelism: int
    auto_offset_reset: str
    enable_auto_commit: bool
    max_poll_records: int
    session_timeout_ms: int
    heartbeat_interval_ms: int
    max_poll_interval_ms: int
    description: str

CONSUMER_GROUPS = {
    # Sensor Data Processing
    "sensor-processor": ConsumerGroupConfig(
        group_id="sensor-processor",
        topics=["raw.iot.sensors"],
        parallelism=12,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        max_poll_records=500,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        max_poll_interval_ms=300000,
        description="Processes raw sensor data with enrichment"
    ),
    
    # Metrics Aggregation
    "metrics-aggregator-1min": ConsumerGroupConfig(
        group_id="metrics-aggregator-1min",
        topics=["processed.metrics.normalized"],
        parallelism=8,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        max_poll_records=1000,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        max_poll_interval_ms=300000,
        description="1-minute window aggregation"
    ),
    
    "metrics-aggregator-5min": ConsumerGroupConfig(
        group_id="metrics-aggregator-5min",
        topics=["aggregated.metrics.1min"],
        parallelism=8,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        max_poll_records=500,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        max_poll_interval_ms=300000,
        description="5-minute window aggregation"
    ),
    
    # Anomaly Detection
    "anomaly-detector": ConsumerGroupConfig(
        group_id="anomaly-detector",
        topics=["processed.metrics.normalized", "processed.sensor.enriched"],
        parallelism=8,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        max_poll_records=500,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        max_poll_interval_ms=300000,
        description="Real-time anomaly detection"
    ),
    
    # Complex Event Processing
    "cep-engine": ConsumerGroupConfig(
        group_id="cep-engine",
        topics=["raw.security.events", "processed.sensor.enriched"],
        parallelism=6,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        max_poll_records=200,
        session_timeout_ms=45000,
        heartbeat_interval_ms=15000,
        max_poll_interval_ms=600000,
        description="Complex event pattern matching"
    ),
    
    # Alert Processing
    "alert-processor": ConsumerGroupConfig(
        group_id="alert-processor",
        topics=["alerts.critical", "alerts.warning", "alerts.info"],
        parallelism=4,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        max_poll_records=100,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        max_poll_interval_ms=300000,
        description="Alert routing and notification"
    ),
    
    # Log Processing
    "log-processor": ConsumerGroupConfig(
        group_id="log-processor",
        topics=["raw.application.logs"],
        parallelism=16,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        max_poll_records=1000,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        max_poll_interval_ms=300000,
        description="Log parsing and analysis"
    ),
    
    # Command Handler
    "command-handler": ConsumerGroupConfig(
        group_id="command-handler",
        topics=["commands.device.control"],
        parallelism=6,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        max_poll_records=50,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        max_poll_interval_ms=300000,
        description="Device command processing"
    ),
}

def get_consumer_config(group_id: str) -> Optional[ConsumerGroupConfig]:
    """Get configuration for a specific consumer group."""
    return CONSUMER_GROUPS.get(group_id)

def get_all_groups() -> Dict[str, ConsumerGroupConfig]:
    """Get all consumer group configurations."""
    return CONSUMER_GROUPS.copy()
```

---

## 4. Stream Processing Implementation

### 4.1 Kafka Streams Core Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/core/kafka_streams_app.py
"""
Kafka Streams Application for ResilienceAI
"""

import json
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import partial

from confluent_kafka import Consumer, Producer, KafkaError, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic

logger = logging.getLogger(__name__)

@dataclass
class StreamRecord:
    """Standard stream record format."""
    key: Optional[str]
    value: Dict[str, Any]
    timestamp: int
    topic: str
    partition: int
    offset: int
    headers: Optional[Dict[str, str]] = None
    
    @classmethod
    def from_kafka_message(cls, msg):
        """Create StreamRecord from Kafka message."""
        try:
            value = json.loads(msg.value().decode('utf-8'))
        except (json.JSONDecodeError, AttributeError):
            value = {"raw": msg.value().decode('utf-8') if msg.value() else None}
        
        headers = {}
        if msg.headers():
            for header in msg.headers():
                headers[header[0]] = header[1].decode('utf-8') if header[1] else None
        
        return cls(
            key=msg.key().decode('utf-8') if msg.key() else None,
            value=value,
            timestamp=msg.timestamp()[1] if msg.timestamp() else int(datetime.now().timestamp() * 1000),
            topic=msg.topic(),
            partition=msg.partition(),
            offset=msg.offset(),
            headers=headers
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class KafkaStreamsApp:
    """
    Main Kafka Streams application class.
    Provides DSL-like API for stream processing.
    """
    
    def __init__(self, app_id: str, config: Dict[str, Any]):
        self.app_id = app_id
        self.config = config
        self.topology = []
        self.processors: Dict[str, Callable] = {}
        self.state_stores: Dict[str, Any] = {}
        self.running = False
        
        # Initialize Kafka clients
        self._init_kafka_clients()
    
    def _init_kafka_clients(self):
        """Initialize Kafka consumer and producer."""
        consumer_config = {
            'bootstrap.servers': self.config.get('bootstrap.servers', 'localhost:9092'),
            'group.id': self.app_id,
            'auto.offset.reset': self.config.get('auto.offset.reset', 'earliest'),
            'enable.auto.commit': self.config.get('enable.auto.commit', False),
            'max.poll.records': self.config.get('max.poll.records', 500),
            'session.timeout.ms': self.config.get('session.timeout.ms', 30000),
            'heartbeat.interval.ms': self.config.get('heartbeat.interval.ms', 10000),
            'isolation.level': 'read_committed',  # For exactly-once
        }
        
        producer_config = {
            'bootstrap.servers': self.config.get('bootstrap.servers', 'localhost:9092'),
            'acks': 'all',
            'retries': 10,
            'max.in.flight.requests.per.connection': 5,
            'enable.idempotence': True,  # Exactly-once producer
            'compression.type': 'lz4',
        }
        
        self.consumer = Consumer(consumer_config)
        self.producer = Producer(producer_config)
    
    def stream(self, topic: str) -> 'KStream':
        """Create a stream from a topic."""
        return KStream(self, topic)
    
    def table(self, topic: str, store_name: str) -> 'KTable':
        """Create a table from a topic with state store."""
        return KTable(self, topic, store_name)
    
    def add_processor(self, name: str, processor: Callable):
        """Add a processor to the topology."""
        self.processors[name] = processor
    
    def start(self):
        """Start the streams application."""
        self.running = True
        logger.info(f"Starting Kafka Streams application: {self.app_id}")
        
        # Subscribe to all input topics
        input_topics = self._get_input_topics()
        if input_topics:
            self.consumer.subscribe(input_topics)
            logger.info(f"Subscribed to topics: {input_topics}")
    
    def stop(self):
        """Stop the streams application."""
        self.running = False
        self.consumer.close()
        self.producer.flush()
        logger.info(f"Stopped Kafka Streams application: {self.app_id}")
    
    def _get_input_topics(self) -> list:
        """Get all input topics from topology."""
        topics = set()
        for node in self.topology:
            if isinstance(node, (KStream, KTable)):
                topics.add(node.topic)
        return list(topics)
    
    def poll(self, timeout: float = 1.0) -> Optional[StreamRecord]:
        """Poll for records."""
        if not self.running:
            return None
        
        msg = self.consumer.poll(timeout)
        if msg is None:
            return None
        
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logger.debug(f"Reached end of partition {msg.topic()}[{msg.partition()}]")
            else:
                logger.error(f"Error: {msg.error()}")
            return None
        
        return StreamRecord.from_kafka_message(msg)
    
    def produce(self, topic: str, key: str, value: Dict[str, Any], 
                headers: Optional[Dict[str, str]] = None):
        """Produce a record to a topic."""
        try:
            kafka_headers = [(k, v.encode('utf-8')) for k, v in (headers or {}).items()]
            self.producer.produce(
                topic=topic,
                key=key.encode('utf-8') if key else None,
                value=json.dumps(value).encode('utf-8'),
                headers=kafka_headers
            )
        except Exception as e:
            logger.error(f"Error producing to {topic}: {e}")
            raise
    
    def commit(self):
        """Commit offsets synchronously."""
        self.consumer.commit()


class KStream:
    """Represents a stream of records."""
    
    def __init__(self, app: KafkaStreamsApp, topic: str, 
                 parent: Optional['KStream'] = None):
        self.app = app
        self.topic = topic
        self.parent = parent
        self.operations = []
        
        if parent is None:
            app.topology.append(self)
    
    def filter(self, predicate: Callable[[StreamRecord], bool]) -> 'KStream':
        """Filter records based on predicate."""
        new_stream = KStream(self.app, self.topic, self)
        new_stream.operations = self.operations + [('filter', predicate)]
        return new_stream
    
    def map(self, mapper: Callable[[StreamRecord], StreamRecord]) -> 'KStream':
        """Transform each record."""
        new_stream = KStream(self.app, self.topic, self)
        new_stream.operations = self.operations + [('map', mapper)]
        return new_stream
    
    def map_values(self, mapper: Callable[[Dict], Dict]) -> 'KStream':
        """Transform values only."""
        def value_mapper(record: StreamRecord) -> StreamRecord:
            new_value = mapper(record.value)
            return StreamRecord(
                key=record.key,
                value=new_value,
                timestamp=record.timestamp,
                topic=record.topic,
                partition=record.partition,
                offset=record.offset,
                headers=record.headers
            )
        
        new_stream = KStream(self.app, self.topic, self)
        new_stream.operations = self.operations + [('map_values', value_mapper)]
        return new_stream
    
    def flat_map(self, mapper: Callable[[StreamRecord], list]) -> 'KStream':
        """Transform each record to zero or more records."""
        new_stream = KStream(self.app, self.topic, self)
        new_stream.operations = self.operations + [('flat_map', mapper)]
        return new_stream
    
    def branch(self, *predicates: Callable[[StreamRecord], bool]) -> list:
        """Branch stream into multiple streams based on predicates."""
        branches = []
        for i, predicate in enumerate(predicates):
            new_stream = KStream(self.app, self.topic, self)
            new_stream.operations = self.operations + [('branch', predicate, i)]
            branches.append(new_stream)
        return branches
    
    def peek(self, action: Callable[[StreamRecord], None]) -> 'KStream':
        """Perform side effect without modifying stream."""
        new_stream = KStream(self.app, self.topic, self)
        new_stream.operations = self.operations + [('peek', action)]
        return new_stream
    
    def foreach(self, action: Callable[[StreamRecord], None]):
        """Terminal operation - perform action on each record."""
        self.operations.append(('foreach', action))
    
    def to(self, topic: str):
        """Terminal operation - write to topic."""
        self.operations.append(('to', topic))
    
    def group_by_key(self) -> 'KGroupedStream':
        """Group records by key for aggregation."""
        return KGroupedStream(self.app, self, self.operations)
    
    def join(self, other: 'KStream', joiner: Callable, 
             window: 'JoinWindow') -> 'KStream':
        """Join with another stream."""
        new_stream = KStream(self.app, f"{self.topic}_join_{other.topic}", self)
        new_stream.operations = self.operations + [('join', other, joiner, window)]
        return new_stream
    
    def left_join(self, other: 'KTable', joiner: Callable) -> 'KStream':
        """Left join with a table."""
        new_stream = KStream(self.app, self.topic, self)
        new_stream.operations = self.operations + [('left_join', other, joiner)]
        return new_stream
    
    def process(self, record: StreamRecord) -> Optional[list]:
        """Process a record through the operation chain."""
        records = [record]
        
        for op_name, *op_args in self.operations:
            if op_name == 'filter':
                predicate = op_args[0]
                records = [r for r in records if predicate(r)]
            
            elif op_name == 'map':
                mapper = op_args[0]
                records = [mapper(r) for r in records]
            
            elif op_name == 'map_values':
                mapper = op_args[0]
                records = [mapper(r) for r in records]
            
            elif op_name == 'flat_map':
                mapper = op_args[0]
                new_records = []
                for r in records:
                    new_records.extend(mapper(r))
                records = new_records
            
            elif op_name == 'branch':
                predicate, branch_index = op_args
                records = [r for r in records if predicate(r)]
            
            elif op_name == 'peek':
                action = op_args[0]
                for r in records:
                    action(r)
            
            elif op_name == 'foreach':
                action = op_args[0]
                for r in records:
                    action(r)
                return None
            
            elif op_name == 'to':
                topic = op_args[0]
                for r in records:
                    self.app.produce(topic, r.key, r.value, r.headers)
                return None
        
        return records


class KTable:
    """Represents a changelog stream (table)."""
    
    def __init__(self, app: KafkaStreamsApp, topic: str, store_name: str):
        self.app = app
        self.topic = topic
        self.store_name = store_name
        self.state: Dict[str, Any] = {}
        app.state_stores[store_name] = self.state
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        return self.state.get(key)
    
    def put(self, key: str, value: Any):
        """Put value by key."""
        self.state[key] = value
    
    def filter(self, predicate: Callable[[str, Any], bool]) -> 'KTable':
        """Filter table entries."""
        new_table = KTable(self.app, self.topic, f"{self.store_name}_filtered")
        new_table.state = {k: v for k, v in self.state.items() if predicate(k, v)}
        return new_table
    
    def map_values(self, mapper: Callable[[Any], Any]) -> 'KTable':
        """Transform values."""
        new_table = KTable(self.app, self.topic, f"{self.store_name}_mapped")
        new_table.state = {k: mapper(v) for k, v in self.state.items()}
        return new_table
    
    def to_stream(self) -> KStream:
        """Convert table to stream."""
        stream = KStream(self.app, self.topic)
        return stream


class KGroupedStream:
    """Grouped stream for aggregations."""
    
    def __init__(self, app: KafkaStreamsApp, source: KStream, operations: list):
        self.app = app
        self.source = source
        self.operations = operations
    
    def windowed_by(self, window: 'TimeWindow') -> 'WindowedStream':
        """Apply time window."""
        return WindowedStream(self.app, self.source, self.operations, window)
    
    def aggregate(self, initializer: Callable, aggregator: Callable,
                  store_name: str) -> KTable:
        """Aggregate grouped records."""
        table = KTable(self.app, self.source.topic, store_name)
        self.operations.append(('aggregate', initializer, aggregator, table))
        return table
    
    def count(self, store_name: str) -> KTable:
        """Count records per key."""
        return self.aggregate(
            initializer=lambda: 0,
            aggregator=lambda key, value, aggregate: aggregate + 1,
            store_name=store_name
        )
    
    def reduce(self, reducer: Callable, store_name: str) -> KTable:
        """Reduce grouped records."""
        return self.aggregate(
            initializer=lambda: None,
            aggregator=lambda key, value, aggregate: reducer(aggregate, value),
            store_name=store_name
        )


class WindowedStream:
    """Stream with time window applied."""
    
    def __init__(self, app: KafkaStreamsApp, source: KStream, 
                 operations: list, window: 'TimeWindow'):
        self.app = app
        self.source = source
        self.operations = operations
        self.window = window
        self.windows: Dict[str, Dict[str, Any]] = {}
    
    def aggregate(self, initializer: Callable, aggregator: Callable,
                  store_name: str) -> KTable:
        """Aggregate windowed records."""
        table = KTable(self.app, self.source.topic, store_name)
        self.operations.append(('windowed_aggregate', initializer, aggregator, 
                               table, self.window))
        return table
    
    def count(self, store_name: str) -> KTable:
        """Count records per window."""
        return self.aggregate(
            initializer=lambda: 0,
            aggregator=lambda key, value, aggregate: aggregate + 1,
            store_name=store_name
        )
    
    def reduce(self, reducer: Callable, store_name: str) -> KTable:
        """Reduce windowed records."""
        return self.aggregate(
            initializer=lambda: None,
            aggregator=lambda key, value, aggregate: reducer(aggregate, value),
            store_name=store_name
        )


class TimeWindow:
    """Base class for time windows."""
    
    def __init__(self, size_ms: int, grace_ms: int = 0):
        self.size_ms = size_ms
        self.grace_ms = grace_ms
    
    def get_window_start(self, timestamp: int) -> int:
        """Get window start for timestamp."""
        return (timestamp // self.size_ms) * self.size_ms
    
    def get_window_end(self, timestamp: int) -> int:
        """Get window end for timestamp."""
        return self.get_window_start(timestamp) + self.size_ms


class TumblingWindow(TimeWindow):
    """Tumbling (fixed) time window."""
    
    def __init__(self, size_ms: int, grace_ms: int = 0):
        super().__init__(size_ms, grace_ms)
    
    @classmethod
    def of_minutes(cls, minutes: int, grace_ms: int = 0):
        return cls(minutes * 60 * 1000, grace_ms)
    
    @classmethod
    def of_seconds(cls, seconds: int, grace_ms: int = 0):
        return cls(seconds * 1000, grace_ms)


class SlidingWindow(TimeWindow):
    """Sliding time window with overlap."""
    
    def __init__(self, size_ms: int, advance_ms: int, grace_ms: int = 0):
        super().__init__(size_ms, grace_ms)
        self.advance_ms = advance_ms


class SessionWindow:
    """Session window based on activity gaps."""
    
    def __init__(self, inactivity_gap_ms: int):
        self.inactivity_gap_ms = inactivity_gap_ms
        self.sessions: Dict[str, Dict] = {}


class JoinWindow:
    """Window for stream joins."""
    
    def __init__(self, before_ms: int, after_ms: int):
        self.before_ms = before_ms
        self.after_ms = after_ms
```


### 4.2 Windowing Operations Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/core/windowing.py
"""
Windowing Operations for Stream Processing
"""

import time
import threading
from typing import Dict, List, Callable, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field
from heapq import heappush, heappop
import logging

logger = logging.getLogger(__name__)


@dataclass
class WindowResult:
    """Result of a window aggregation."""
    window_start: int
    window_end: int
    key: str
    value: Any
    record_count: int
    is_final: bool = False


@dataclass
class WindowState:
    """State for a single window."""
    start_time: int
    end_time: int
    records: List[Any] = field(default_factory=list)
    aggregated_value: Any = None
    is_closed: bool = False


class WindowStore:
    """In-memory window state store."""
    
    def __init__(self, retention_ms: int = 3600000):
        self.windows: Dict[str, Dict[int, WindowState]] = defaultdict(dict)
        self.retention_ms = retention_ms
        self._lock = threading.RLock()
    
    def get_or_create(self, key: str, window_start: int, 
                      window_end: int) -> WindowState:
        """Get or create window state."""
        with self._lock:
            if window_start not in self.windows[key]:
                self.windows[key][window_start] = WindowState(
                    start_time=window_start,
                    end_time=window_end
                )
            return self.windows[key][window_start]
    
    def add_record(self, key: str, window_start: int, 
                   window_end: int, record: Any):
        """Add record to window."""
        with self._lock:
            window = self.get_or_create(key, window_start, window_end)
            if not window.is_closed:
                window.records.append(record)
    
    def get_window(self, key: str, window_start: int) -> Optional[WindowState]:
        """Get window state."""
        with self._lock:
            return self.windows.get(key, {}).get(window_start)
    
    def close_window(self, key: str, window_start: int):
        """Close a window."""
        with self._lock:
            if key in self.windows and window_start in self.windows[key]:
                self.windows[key][window_start].is_closed = True
    
    def remove_window(self, key: str, window_start: int):
        """Remove a window."""
        with self._lock:
            if key in self.windows and window_start in self.windows[key]:
                del self.windows[key][window_start]
    
    def get_expired_windows(self, current_time: int) -> List[tuple]:
        """Get windows that have exceeded retention."""
        expired = []
        with self._lock:
            for key, windows in self.windows.items():
                for start_time, window in list(windows.items()):
                    if current_time - window.end_time > self.retention_ms:
                        expired.append((key, start_time))
        return expired
    
    def cleanup(self, current_time: int):
        """Clean up expired windows."""
        expired = self.get_expired_windows(current_time)
        for key, start_time in expired:
            self.remove_window(key, start_time)
            logger.debug(f"Cleaned up window: {key}:{start_time}")


class TumblingWindowProcessor:
    """
    Tumbling window processor with event-time processing.
    """
    
    def __init__(self, window_size_ms: int, grace_period_ms: int = 0,
                 late_data_handling: str = 'drop'):
        self.window_size_ms = window_size_ms
        self.grace_period_ms = grace_period_ms
        self.late_data_handling = late_data_handling  # 'drop', 'include', 'side_output'
        self.store = WindowStore()
        self.emit_callbacks: List[Callable] = []
        self.late_data_callbacks: List[Callable] = []
        self._running = False
        self._cleanup_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start the window processor."""
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop)
        self._cleanup_thread.daemon = True
        self._cleanup_thread.start()
        logger.info(f"Started tumbling window processor: {self.window_size_ms}ms")
    
    def stop(self):
        """Stop the window processor."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
    
    def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            time.sleep(60)  # Cleanup every minute
            current_time = int(time.time() * 1000)
            self.store.cleanup(current_time)
    
    def get_window_bounds(self, timestamp: int) -> tuple:
        """Get window start and end for timestamp."""
        window_start = (timestamp // self.window_size_ms) * self.window_size_ms
        window_end = window_start + self.window_size_ms
        return window_start, window_end
    
    def process_record(self, key: str, value: Any, 
                       event_timestamp: int) -> Optional[WindowResult]:
        """
        Process a record with event timestamp.
        
        Returns WindowResult if window is ready to emit.
        """
        window_start, window_end = self.get_window_bounds(event_timestamp)
        current_time = int(time.time() * 1000)
        
        # Check for late data
        if current_time > window_end + self.grace_period_ms:
            # Late data
            if self.late_data_handling == 'drop':
                logger.debug(f"Dropping late record: {key}@{event_timestamp}")
                return None
            elif self.late_data_handling == 'side_output':
                for callback in self.late_data_callbacks:
                    callback(key, value, event_timestamp, window_start, window_end)
                return None
            # 'include' - process anyway
        
        # Add record to window
        self.store.add_record(key, window_start, window_end, 
                             {'value': value, 'timestamp': event_timestamp})
        
        # Check if window should be emitted
        if current_time >= window_end + self.grace_period_ms:
            return self._emit_window(key, window_start, window_end)
        
        return None
    
    def _emit_window(self, key: str, window_start: int, 
                     window_end: int) -> Optional[WindowResult]:
        """Emit a completed window."""
        window = self.store.get_window(key, window_start)
        if not window or window.is_closed:
            return None
        
        # Mark window as closed
        self.store.close_window(key, window_start)
        
        result = WindowResult(
            window_start=window_start,
            window_end=window_end,
            key=key,
            value=window.aggregated_value,
            record_count=len(window.records),
            is_final=True
        )
        
        # Notify callbacks
        for callback in self.emit_callbacks:
            callback(result)
        
        return result
    
    def on_emit(self, callback: Callable[[WindowResult], None]):
        """Register emit callback."""
        self.emit_callbacks.append(callback)
    
    def on_late_data(self, callback: Callable):
        """Register late data callback."""
        self.late_data_callbacks.append(callback)
    
    def force_emit(self, key: str, window_start: int) -> Optional[WindowResult]:
        """Force emit a window."""
        window_end = window_start + self.window_size_ms
        return self._emit_window(key, window_start, window_end)


class SlidingWindowProcessor:
    """
    Sliding window processor with overlapping windows.
    """
    
    def __init__(self, window_size_ms: int, slide_interval_ms: int,
                 grace_period_ms: int = 0):
        self.window_size_ms = window_size_ms
        self.slide_interval_ms = slide_interval_ms
        self.grace_period_ms = grace_period_ms
        self.store = WindowStore()
        self.emit_callbacks: List[Callable] = []
    
    def get_window_bounds_list(self, timestamp: int) -> List[tuple]:
        """Get all window bounds that contain the timestamp."""
        windows = []
        # Find all windows that contain this timestamp
        first_window_start = ((timestamp - self.window_size_ms) // 
                             self.slide_interval_ms + 1) * self.slide_interval_ms
        
        window_start = first_window_start
        while window_start <= timestamp:
            window_end = window_start + self.window_size_ms
            if window_end > timestamp:
                windows.append((window_start, window_end))
            window_start += self.slide_interval_ms
        
        return windows
    
    def process_record(self, key: str, value: Any, 
                       event_timestamp: int) -> List[WindowResult]:
        """Process a record - may belong to multiple windows."""
        windows = self.get_window_bounds_list(event_timestamp)
        results = []
        
        for window_start, window_end in windows:
            self.store.add_record(key, window_start, window_end,
                                 {'value': value, 'timestamp': event_timestamp})
            
            current_time = int(time.time() * 1000)
            if current_time >= window_end + self.grace_period_ms:
                result = self._emit_window(key, window_start, window_end)
                if result:
                    results.append(result)
        
        return results
    
    def _emit_window(self, key: str, window_start: int, 
                     window_end: int) -> Optional[WindowResult]:
        """Emit a completed window."""
        window = self.store.get_window(key, window_start)
        if not window or window.is_closed:
            return None
        
        self.store.close_window(key, window_start)
        
        result = WindowResult(
            window_start=window_start,
            window_end=window_end,
            key=key,
            value=window.aggregated_value,
            record_count=len(window.records),
            is_final=True
        )
        
        for callback in self.emit_callbacks:
            callback(result)
        
        return result
    
    def on_emit(self, callback: Callable[[WindowResult], None]):
        """Register emit callback."""
        self.emit_callbacks.append(callback)


class SessionWindowProcessor:
    """
    Session window processor based on inactivity gaps.
    """
    
    def __init__(self, inactivity_gap_ms: int):
        self.inactivity_gap_ms = inactivity_gap_ms
        self.sessions: Dict[str, Dict] = {}
        self.emit_callbacks: List[Callable] = []
        self._lock = threading.RLock()
    
    def process_record(self, key: str, value: Any, 
                       event_timestamp: int) -> Optional[WindowResult]:
        """Process a record and manage sessions."""
        with self._lock:
            if key not in self.sessions:
                # Start new session
                self.sessions[key] = {
                    'start': event_timestamp,
                    'end': event_timestamp,
                    'records': [{'value': value, 'timestamp': event_timestamp}],
                    'last_activity': event_timestamp
                }
                return None
            
            session = self.sessions[key]
            
            # Check if this extends current session
            if event_timestamp <= session['end'] + self.inactivity_gap_ms:
                # Extend session
                session['records'].append({'value': value, 'timestamp': event_timestamp})
                session['end'] = max(session['end'], event_timestamp)
                session['last_activity'] = event_timestamp
                return None
            else:
                # Session gap - emit current session and start new one
                result = self._emit_session(key)
                
                # Start new session
                self.sessions[key] = {
                    'start': event_timestamp,
                    'end': event_timestamp,
                    'records': [{'value': value, 'timestamp': event_timestamp}],
                    'last_activity': event_timestamp
                }
                
                return result
    
    def _emit_session(self, key: str) -> Optional[WindowResult]:
        """Emit a completed session."""
        if key not in self.sessions:
            return None
        
        session = self.sessions[key]
        
        result = WindowResult(
            window_start=session['start'],
            window_end=session['end'],
            key=key,
            value=None,  # Would be aggregated
            record_count=len(session['records']),
            is_final=True
        )
        
        del self.sessions[key]
        
        for callback in self.emit_callbacks:
            callback(result)
        
        return result
    
    def check_expired_sessions(self, current_time: int) -> List[WindowResult]:
        """Check and emit expired sessions."""
        expired = []
        with self._lock:
            for key in list(self.sessions.keys()):
                session = self.sessions[key]
                if current_time > session['last_activity'] + self.inactivity_gap_ms:
                    result = self._emit_session(key)
                    if result:
                        expired.append(result)
        return expired
    
    def on_emit(self, callback: Callable[[WindowResult], None]):
        """Register emit callback."""
        self.emit_callbacks.append(callback)


class WindowAggregator:
    """
    Helper class for window aggregations.
    """
    
    @staticmethod
    def count(window_state: WindowState) -> int:
        """Count records in window."""
        return len(window_state.records)
    
    @staticmethod
    def sum(window_state: WindowState, field: str) -> float:
        """Sum values in window."""
        total = 0.0
        for record in window_state.records:
            value = record['value']
            if isinstance(value, dict) and field in value:
                total += float(value[field])
            elif isinstance(value, (int, float)):
                total += float(value)
        return total
    
    @staticmethod
    def avg(window_state: WindowState, field: str) -> float:
        """Calculate average in window."""
        if not window_state.records:
            return 0.0
        total = WindowAggregator.sum(window_state, field)
        return total / len(window_state.records)
    
    @staticmethod
    def min_value(window_state: WindowState, field: str) -> Optional[float]:
        """Find minimum value in window."""
        values = []
        for record in window_state.records:
            value = record['value']
            if isinstance(value, dict) and field in value:
                values.append(float(value[field]))
            elif isinstance(value, (int, float)):
                values.append(float(value))
        return min(values) if values else None
    
    @staticmethod
    def max_value(window_state: WindowState, field: str) -> Optional[float]:
        """Find maximum value in window."""
        values = []
        for record in window_state.records:
            value = record['value']
            if isinstance(value, dict) and field in value:
                values.append(float(value[field]))
            elif isinstance(value, (int, float)):
                values.append(float(value))
        return max(values) if values else None
    
    @staticmethod
    def percentile(window_state: WindowState, field: str, 
                   p: float) -> Optional[float]:
        """Calculate percentile in window."""
        values = []
        for record in window_state.records:
            value = record['value']
            if isinstance(value, dict) and field in value:
                values.append(float(value[field]))
            elif isinstance(value, (int, float)):
                values.append(float(value))
        
        if not values:
            return None
        
        values.sort()
        k = (len(values) - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < len(values) else f
        
        if f == c:
            return values[f]
        return values[f] * (c - k) + values[c] * (k - f)
```


### 4.3 Stream Joins Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/core/stream_joins.py
"""
Stream Join Operations for ResilienceAI
"""

import time
import threading
from typing import Dict, List, Callable, Optional, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class JoinRecord:
    """Record for join operations."""
    key: str
    value: Dict[str, Any]
    timestamp: int
    topic: str
    headers: Optional[Dict[str, str]] = None


@dataclass
class JoinResult:
    """Result of a join operation."""
    key: str
    left_value: Dict[str, Any]
    right_value: Dict[str, Any]
    left_timestamp: int
    right_timestamp: int
    join_timestamp: int


class StreamBuffer:
    """Buffer for stream records with time-based eviction."""
    
    def __init__(self, retention_ms: int):
        self.retention_ms = retention_ms
        self.records: Dict[str, List[JoinRecord]] = defaultdict(list)
        self._lock = threading.RLock()
    
    def add(self, record: JoinRecord):
        """Add record to buffer."""
        with self._lock:
            self.records[record.key].append(record)
    
    def get(self, key: str) -> List[JoinRecord]:
        """Get records by key."""
        with self._lock:
            return self.records.get(key, []).copy()
    
    def remove(self, key: str, record: JoinRecord):
        """Remove specific record."""
        with self._lock:
            if key in self.records:
                try:
                    self.records[key].remove(record)
                except ValueError:
                    pass
    
    def cleanup(self, current_time: int):
        """Remove expired records."""
        with self._lock:
            for key in list(self.records.keys()):
                self.records[key] = [
                    r for r in self.records[key]
                    if current_time - r.timestamp <= self.retention_ms
                ]
                if not self.records[key]:
                    del self.records[key]


class StreamStreamJoin:
    """
    Stream-Stream join with time window.
    """
    
    def __init__(self, join_window_ms: int, left_topic: str, right_topic: str):
        self.join_window_ms = join_window_ms
        self.left_topic = left_topic
        self.right_topic = right_topic
        self.left_buffer = StreamBuffer(join_window_ms * 2)
        self.right_buffer = StreamBuffer(join_window_ms * 2)
        self.join_callback: Optional[Callable[[JoinResult], None]] = None
        self._running = False
        self._cleanup_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start the join processor."""
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop)
        self._cleanup_thread.daemon = True
        self._cleanup_thread.start()
        logger.info(f"Started stream-stream join: {self.left_topic} <-> {self.right_topic}")
    
    def stop(self):
        """Stop the join processor."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
    
    def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            time.sleep(30)
            current_time = int(time.time() * 1000)
            self.left_buffer.cleanup(current_time)
            self.right_buffer.cleanup(current_time)
    
    def process_left(self, key: str, value: Dict[str, Any], 
                     timestamp: int, headers: Optional[Dict] = None):
        """Process record from left stream."""
        record = JoinRecord(key, value, timestamp, self.left_topic, headers)
        self.left_buffer.add(record)
        
        # Try to join with right buffer
        self._attempt_join(record, self.right_buffer, is_left=True)
    
    def process_right(self, key: str, value: Dict[str, Any], 
                      timestamp: int, headers: Optional[Dict] = None):
        """Process record from right stream."""
        record = JoinRecord(key, value, timestamp, self.right_topic, headers)
        self.right_buffer.add(record)
        
        # Try to join with left buffer
        self._attempt_join(record, self.left_buffer, is_left=False)
    
    def _attempt_join(self, record: JoinRecord, other_buffer: StreamBuffer, 
                      is_left: bool):
        """Attempt to join with records from other buffer."""
        candidates = other_buffer.get(record.key)
        current_time = int(time.time() * 1000)
        
        for candidate in candidates:
            time_diff = abs(record.timestamp - candidate.timestamp)
            
            if time_diff <= self.join_window_ms:
                # Join condition met
                if is_left:
                    result = JoinResult(
                        key=record.key,
                        left_value=record.value,
                        right_value=candidate.value,
                        left_timestamp=record.timestamp,
                        right_timestamp=candidate.timestamp,
                        join_timestamp=current_time
                    )
                else:
                    result = JoinResult(
                        key=record.key,
                        left_value=candidate.value,
                        right_value=record.value,
                        left_timestamp=candidate.timestamp,
                        right_timestamp=record.timestamp,
                        join_timestamp=current_time
                    )
                
                if self.join_callback:
                    self.join_callback(result)
    
    def on_join(self, callback: Callable[[JoinResult], None]):
        """Register join callback."""
        self.join_callback = callback


class StreamTableJoin:
    """
    Stream-Table join (left join with lookup table).
    """
    
    def __init__(self, table: Dict[str, Dict[str, Any]]):
        self.table = table
        self.join_callback: Optional[Callable] = None
        self._lock = threading.RLock()
    
    def update_table(self, key: str, value: Optional[Dict[str, Any]]):
        """Update table entry (None to delete)."""
        with self._lock:
            if value is None:
                self.table.pop(key, None)
            else:
                self.table[key] = value
    
    def process_stream(self, key: str, value: Dict[str, Any], 
                       timestamp: int, headers: Optional[Dict] = None):
        """Process stream record and join with table."""
        with self._lock:
            table_value = self.table.get(key)
        
        result = {
            'key': key,
            'stream_value': value,
            'table_value': table_value,
            'timestamp': timestamp,
            'headers': headers
        }
        
        if self.join_callback:
            self.join_callback(result)
        
        return result
    
    def on_join(self, callback: Callable):
        """Register join callback."""
        self.join_callback = callback


class TableTableJoin:
    """
    Table-Table join (KTable-KTable join).
    """
    
    def __init__(self):
        self.left_table: Dict[str, Dict[str, Any]] = {}
        self.right_table: Dict[str, Dict[str, Any]] = {}
        self.result_table: Dict[str, Dict[str, Any]] = {}
        self.join_callback: Optional[Callable] = None
        self._lock = threading.RLock()
    
    def update_left(self, key: str, value: Optional[Dict[str, Any]]):
        """Update left table and recompute join."""
        with self._lock:
            if value is None:
                self.left_table.pop(key, None)
                self.result_table.pop(key, None)
            else:
                self.left_table[key] = value
                self._recompute_join(key)
    
    def update_right(self, key: str, value: Optional[Dict[str, Any]]):
        """Update right table and recompute join."""
        with self._lock:
            if value is None:
                self.right_table.pop(key, None)
                self.result_table.pop(key, None)
            else:
                self.right_table[key] = value
                self._recompute_join(key)
    
    def _recompute_join(self, key: str):
        """Recompute join result for key."""
        left_value = self.left_table.get(key)
        right_value = self.right_table.get(key)
        
        if left_value and right_value:
            self.result_table[key] = {
                'key': key,
                'left': left_value,
                'right': right_value,
                'joined_at': int(time.time() * 1000)
            }
            
            if self.join_callback:
                self.join_callback(self.result_table[key])
    
    def get_result(self, key: str) -> Optional[Dict[str, Any]]:
        """Get join result for key."""
        with self._lock:
            return self.result_table.get(key)
    
    def on_join(self, callback: Callable):
        """Register join callback."""
        self.join_callback = callback


class IntervalJoin:
    """
    Interval join with custom time bounds.
    """
    
    def __init__(self, lower_bound_ms: int, upper_bound_ms: int):
        self.lower_bound_ms = lower_bound_ms
        self.upper_bound_ms = upper_bound_ms
        self.left_buffer = StreamBuffer(abs(lower_bound_ms) + upper_bound_ms)
        self.right_buffer = StreamBuffer(abs(lower_bound_ms) + upper_bound_ms)
        self.join_callback: Optional[Callable[[JoinResult], None]] = None
    
    def process_left(self, key: str, value: Dict[str, Any], 
                     timestamp: int, headers: Optional[Dict] = None):
        """Process record from left stream."""
        record = JoinRecord(key, value, timestamp, "left", headers)
        self.left_buffer.add(record)
        
        # Find matching records in right buffer
        candidates = self.right_buffer.get(key)
        for candidate in candidates:
            time_diff = timestamp - candidate.timestamp
            if self.lower_bound_ms <= time_diff <= self.upper_bound_ms:
                result = JoinResult(
                    key=key,
                    left_value=value,
                    right_value=candidate.value,
                    left_timestamp=timestamp,
                    right_timestamp=candidate.timestamp,
                    join_timestamp=int(time.time() * 1000)
                )
                if self.join_callback:
                    self.join_callback(result)
    
    def process_right(self, key: str, value: Dict[str, Any], 
                      timestamp: int, headers: Optional[Dict] = None):
        """Process record from right stream."""
        record = JoinRecord(key, value, timestamp, "right", headers)
        self.right_buffer.add(record)
        
        # Find matching records in left buffer
        candidates = self.left_buffer.get(key)
        for candidate in candidates:
            time_diff = candidate.timestamp - timestamp
            if self.lower_bound_ms <= time_diff <= self.upper_bound_ms:
                result = JoinResult(
                    key=key,
                    left_value=candidate.value,
                    right_value=value,
                    left_timestamp=candidate.timestamp,
                    right_timestamp=timestamp,
                    join_timestamp=int(time.time() * 1000)
                )
                if self.join_callback:
                    self.join_callback(result)
    
    def on_join(self, callback: Callable[[JoinResult], None]):
        """Register join callback."""
        self.join_callback = callback


class CoGroupJoin:
    """
    Co-group multiple streams by key.
    """
    
    def __init__(self, streams: List[str], window_ms: int):
        self.streams = streams
        self.window_ms = window_ms
        self.buffers: Dict[str, StreamBuffer] = {
            stream: StreamBuffer(window_ms * 2) for stream in streams
        }
        self.cogroup_callback: Optional[Callable] = None
    
    def process(self, stream_name: str, key: str, value: Dict[str, Any], 
                timestamp: int):
        """Process record from any stream."""
        if stream_name not in self.buffers:
            return
        
        record = JoinRecord(key, value, timestamp, stream_name)
        self.buffers[stream_name].add(record)
        
        # Check if we have records from all streams for this key
        self._attempt_cogroup(key, timestamp)
    
    def _attempt_cogroup(self, key: str, timestamp: int):
        """Attempt to co-group records from all streams."""
        # Get all records for this key within window
        all_records = {}
        for stream_name, buffer in self.buffers.items():
            records = buffer.get(key)
            # Filter by window
            windowed = [
                r for r in records
                if abs(r.timestamp - timestamp) <= self.window_ms
            ]
            if windowed:
                all_records[stream_name] = windowed
        
        # If we have records from all streams, emit co-group
        if len(all_records) == len(self.streams):
            result = {
                'key': key,
                'timestamp': timestamp,
                'streams': all_records
            }
            if self.cogroup_callback:
                self.cogroup_callback(result)
    
    def on_cogroup(self, callback: Callable):
        """Register co-group callback."""
        self.cogroup_callback = callback
```


### 4.4 Exactly-Once Semantics Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/core/exactly_once.py
"""
Exactly-Once Semantics Implementation for ResilienceAI
"""

import json
import hashlib
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import redis

logger = logging.getLogger(__name__)


@dataclass
class ProcessedRecord:
    """Track processed records for deduplication."""
    record_id: str
    topic: str
    partition: int
    offset: int
    processed_at: int
    output_topics: List[str]
    transaction_id: str


class IdempotentProducer:
    """
    Idempotent producer with sequence numbers for exactly-once delivery.
    """
    
    def __init__(self, producer_id: str, redis_client: redis.Redis):
        self.producer_id = producer_id
        self.redis = redis_client
        self.sequence_numbers: Dict[str, int] = {}
        self._lock = threading.RLock()
    
    def _get_sequence_key(self, topic: str, partition: int) -> str:
        """Get Redis key for sequence number."""
        return f"eos:seq:{self.producer_id}:{topic}:{partition}"
    
    def get_next_sequence(self, topic: str, partition: int) -> int:
        """Get next sequence number for topic-partition."""
        with self._lock:
            key = self._get_sequence_key(topic, partition)
            sequence = self.redis.incr(key)
            return sequence
    
    def is_duplicate(self, topic: str, partition: int, 
                     sequence: int) -> bool:
        """Check if message is a duplicate."""
        key = self._get_sequence_key(topic, partition)
        last_sequence = self.redis.get(key)
        if last_sequence is None:
            return False
        return sequence <= int(last_sequence)


class TransactionManager:
    """
    Manages transactions for exactly-once processing.
    """
    
    def __init__(self, redis_client: redis.Redis, 
                 transaction_timeout_ms: int = 60000):
        self.redis = redis_client
        self.transaction_timeout_ms = transaction_timeout_ms
        self.active_transactions: Dict[str, Dict] = {}
        self._lock = threading.RLock()
    
    def _get_txn_key(self, transaction_id: str) -> str:
        """Get Redis key for transaction."""
        return f"eos:txn:{transaction_id}"
    
    def begin_transaction(self, transaction_id: str) -> bool:
        """Begin a new transaction."""
        with self._lock:
            key = self._get_txn_key(transaction_id)
            
            # Check if transaction already exists
            if self.redis.exists(key):
                txn_data = self.redis.hgetall(key)
                if txn_data.get(b'status') == b'committed':
                    logger.warning(f"Transaction {transaction_id} already committed")
                    return False
                elif txn_data.get(b'status') == b'aborted':
                    logger.warning(f"Transaction {transaction_id} was aborted")
                    return False
            
            # Create new transaction
            txn_data = {
                'status': 'active',
                'started_at': int(datetime.now().timestamp() * 1000),
                'inputs': json.dumps([]),
                'outputs': json.dumps([])
            }
            self.redis.hset(key, mapping=txn_data)
            self.redis.expire(key, self.transaction_timeout_ms // 1000)
            
            self.active_transactions[transaction_id] = {
                'inputs': [],
                'outputs': []
            }
            
            logger.debug(f"Began transaction: {transaction_id}")
            return True
    
    def add_input(self, transaction_id: str, topic: str, 
                  partition: int, offset: int):
        """Add input record to transaction."""
        with self._lock:
            if transaction_id not in self.active_transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            self.active_transactions[transaction_id]['inputs'].append({
                'topic': topic,
                'partition': partition,
                'offset': offset
            })
    
    def add_output(self, transaction_id: str, topic: str, 
                   key: str, value: Dict):
        """Add output record to transaction."""
        with self._lock:
            if transaction_id not in self.active_transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            self.active_transactions[transaction_id]['outputs'].append({
                'topic': topic,
                'key': key,
                'value': value
            })
    
    def commit_transaction(self, transaction_id: str) -> bool:
        """Commit transaction."""
        with self._lock:
            if transaction_id not in self.active_transactions:
                return False
            
            key = self._get_txn_key(transaction_id)
            
            # Update transaction status
            txn_data = self.redis.hgetall(key)
            if txn_data.get(b'status') != b'active':
                logger.error(f"Cannot commit transaction {transaction_id}: status is {txn_data.get(b'status')}")
                return False
            
            # Store inputs and outputs
            txn_info = self.active_transactions[transaction_id]
            self.redis.hset(key, mapping={
                'status': 'committed',
                'committed_at': int(datetime.now().timestamp() * 1000),
                'inputs': json.dumps(txn_info['inputs']),
                'outputs': json.dumps(txn_info['outputs'])
            })
            
            # Clean up
            del self.active_transactions[transaction_id]
            
            logger.debug(f"Committed transaction: {transaction_id}")
            return True
    
    def abort_transaction(self, transaction_id: str):
        """Abort transaction."""
        with self._lock:
            key = self._get_txn_key(transaction_id)
            
            self.redis.hset(key, mapping={
                'status': 'aborted',
                'aborted_at': int(datetime.now().timestamp() * 1000)
            })
            
            if transaction_id in self.active_transactions:
                del self.active_transactions[transaction_id]
            
            logger.debug(f"Aborted transaction: {transaction_id}")
    
    def is_committed(self, transaction_id: str) -> bool:
        """Check if transaction is committed."""
        key = self._get_txn_key(transaction_id)
        txn_data = self.redis.hgetall(key)
        return txn_data.get(b'status') == b'committed'


class DeduplicationStore:
    """
    Deduplication store using Redis.
    """
    
    def __init__(self, redis_client: redis.Redis, 
                 retention_hours: int = 24):
        self.redis = redis_client
        self.retention_hours = retention_hours
    
    def _get_dedup_key(self, topic: str, partition: int) -> str:
        """Get Redis key for deduplication."""
        return f"eos:dedup:{topic}:{partition}"
    
    def generate_record_id(self, topic: str, partition: int, 
                           offset: int, value: Dict) -> str:
        """Generate unique record ID."""
        content = f"{topic}:{partition}:{offset}:{json.dumps(value, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def is_processed(self, topic: str, partition: int, 
                     offset: int) -> bool:
        """Check if record has been processed."""
        key = self._get_dedup_key(topic, partition)
        return self.redis.sismember(key, offset)
    
    def mark_processed(self, topic: str, partition: int, 
                       offset: int):
        """Mark record as processed."""
        key = self._get_dedup_key(topic, partition)
        self.redis.sadd(key, offset)
        self.redis.expire(key, self.retention_hours * 3600)
    
    def get_processed_offsets(self, topic: str, partition: int) -> set:
        """Get all processed offsets for a partition."""
        key = self._get_dedup_key(topic, partition)
        offsets = self.redis.smembers(key)
        return {int(o) for o in offsets}


class ExactlyOnceProcessor:
    """
    Main exactly-once processor combining all components.
    """
    
    def __init__(self, app_id: str, redis_client: redis.Redis,
                 transaction_timeout_ms: int = 60000):
        self.app_id = app_id
        self.transaction_manager = TransactionManager(
            redis_client, transaction_timeout_ms
        )
        self.deduplication_store = DeduplicationStore(redis_client)
        self.idempotent_producer = IdempotentProducer(app_id, redis_client)
        self.processed_callback: Optional[Callable] = None
    
    def process_with_eos(self, transaction_id: str, topic: str,
                         partition: int, offset: int, value: Dict,
                         processor: Callable[[Dict], List[tuple]]) -> bool:
        """
        Process record with exactly-once semantics.
        
        Args:
            transaction_id: Unique transaction ID
            topic: Input topic
            partition: Input partition
            offset: Input offset
            value: Record value
            processor: Function that takes value and returns list of (topic, key, value)
        
        Returns:
            True if processed successfully
        """
        # Check for duplicates
        if self.deduplication_store.is_processed(topic, partition, offset):
            logger.debug(f"Skipping duplicate: {topic}:{partition}:{offset}")
            return True
        
        # Check if transaction already committed
        if self.transaction_manager.is_committed(transaction_id):
            logger.debug(f"Transaction already committed: {transaction_id}")
            return True
        
        # Begin transaction
        if not self.transaction_manager.begin_transaction(transaction_id):
            return False
        
        try:
            # Add input to transaction
            self.transaction_manager.add_input(
                transaction_id, topic, partition, offset
            )
            
            # Process record
            outputs = processor(value)
            
            # Add outputs to transaction
            for output_topic, key, output_value in outputs:
                self.transaction_manager.add_output(
                    transaction_id, output_topic, key, output_value
                )
            
            # Commit transaction
            if self.transaction_manager.commit_transaction(transaction_id):
                # Mark as processed
                self.deduplication_store.mark_processed(
                    topic, partition, offset
                )
                
                if self.processed_callback:
                    self.processed_callback(transaction_id, outputs)
                
                return True
            else:
                self.transaction_manager.abort_transaction(transaction_id)
                return False
        
        except Exception as e:
            logger.error(f"Error processing record: {e}")
            self.transaction_manager.abort_transaction(transaction_id)
            raise
    
    def on_processed(self, callback: Callable):
        """Register callback for processed records."""
        self.processed_callback = callback


class CheckpointManager:
    """
    Manages checkpoints for state recovery.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def _get_checkpoint_key(self, app_id: str) -> str:
        """Get Redis key for checkpoint."""
        return f"eos:checkpoint:{app_id}"
    
    def save_checkpoint(self, app_id: str, topic_offsets: Dict[str, Dict[int, int]],
                       state: Dict[str, Any]):
        """Save checkpoint."""
        key = self._get_checkpoint_key(app_id)
        checkpoint = {
            'timestamp': int(datetime.now().timestamp() * 1000),
            'topic_offsets': json.dumps(topic_offsets),
            'state': json.dumps(state)
        }
        self.redis.hset(key, mapping=checkpoint)
    
    def load_checkpoint(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint."""
        key = self._get_checkpoint_key(app_id)
        checkpoint = self.redis.hgetall(key)
        
        if not checkpoint:
            return None
        
        return {
            'timestamp': int(checkpoint[b'timestamp']),
            'topic_offsets': json.loads(checkpoint[b'topic_offsets']),
            'state': json.loads(checkpoint[b'state'])
        }
    
    def get_last_offset(self, app_id: str, topic: str, 
                        partition: int) -> Optional[int]:
        """Get last committed offset."""
        checkpoint = self.load_checkpoint(app_id)
        if not checkpoint:
            return None
        
        topic_offsets = checkpoint['topic_offsets']
        return topic_offsets.get(topic, {}).get(str(partition))
```


### 4.5 Backpressure Handling Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/core/backpressure.py
"""
Backpressure Handling for ResilienceAI Stream Processing
"""

import time
import threading
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BackpressureStrategy(Enum):
    """Backpressure handling strategies."""
    DROP = "drop"                    # Drop new records
    BUFFER = "buffer"                # Buffer with size limit
    BLOCK = "block"                  # Block producer
    SHED_LOAD = "shed_load"          # Shed load (sample)
    SCALE_UP = "scale_up"            # Signal to scale up


@dataclass
class QueueMetrics:
    """Metrics for a processing queue."""
    queue_name: str
    current_size: int
    max_size: int
    arrival_rate: float           # records per second
    processing_rate: float        # records per second
    avg_processing_time_ms: float
    wait_time_ms: float
    dropped_count: int = 0
    blocked_count: int = 0
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter based on queue metrics.
    """
    
    def __init__(self, initial_rate: float = 1000.0,
                 min_rate: float = 100.0,
                 max_rate: float = 10000.0,
                 adjustment_factor: float = 0.1):
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.adjustment_factor = adjustment_factor
        self._lock = threading.Lock()
    
    def get_rate(self) -> float:
        """Get current rate limit."""
        with self._lock:
            return self.current_rate
    
    def increase_rate(self):
        """Increase rate limit."""
        with self._lock:
            new_rate = self.current_rate * (1 + self.adjustment_factor)
            self.current_rate = min(new_rate, self.max_rate)
            logger.debug(f"Increased rate to {self.current_rate}")
    
    def decrease_rate(self):
        """Decrease rate limit."""
        with self._lock:
            new_rate = self.current_rate * (1 - self.adjustment_factor)
            self.current_rate = max(new_rate, self.min_rate)
            logger.debug(f"Decreased rate to {self.current_rate}")
    
    def adapt(self, metrics: QueueMetrics):
        """Adapt rate based on metrics."""
        utilization = metrics.current_size / metrics.max_size if metrics.max_size > 0 else 0
        
        if utilization > 0.8:
            # Queue is filling up - decrease rate
            self.decrease_rate()
        elif utilization < 0.3 and metrics.processing_rate > metrics.arrival_rate:
            # Queue is draining - can increase rate
            self.increase_rate()


class BackpressuredQueue:
    """
    Queue with built-in backpressure handling.
    """
    
    def __init__(self, name: str, max_size: int = 10000,
                 strategy: BackpressureStrategy = BackpressureStrategy.BUFFER,
                 rate_limiter: Optional[AdaptiveRateLimiter] = None):
        self.name = name
        self.max_size = max_size
        self.strategy = strategy
        self.rate_limiter = rate_limiter
        self.queue: deque = deque()
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)
        
        # Metrics
        self.metrics = QueueMetrics(
            queue_name=name,
            current_size=0,
            max_size=max_size,
            arrival_rate=0.0,
            processing_rate=0.0,
            avg_processing_time_ms=0.0,
            wait_time_ms=0.0
        )
        self._arrival_count = 0
        self._processing_count = 0
        self._last_metrics_time = time.time()
        self._dropped_count = 0
        self._blocked_count = 0
        self._processing_times: deque = deque(maxlen=100)
    
    def put(self, item: Any, timeout: Optional[float] = None) -> bool:
        """
        Put item into queue with backpressure handling.
        
        Returns:
            True if item was added, False if dropped/blocked
        """
        with self._lock:
            # Check rate limit
            if self.rate_limiter:
                rate = self.rate_limiter.get_rate()
                current_time = time.time()
                time_since_last = current_time - self._last_metrics_time
                if time_since_last > 0:
                    current_arrival_rate = self._arrival_count / time_since_last
                    if current_arrival_rate > rate:
                        # Rate limit exceeded
                        if self.strategy == BackpressureStrategy.DROP:
                            self._dropped_count += 1
                            return False
                        elif self.strategy == BackpressureStrategy.BLOCK:
                            self._blocked_count += 1
                            # Will block below
        
            # Check queue capacity
            if len(self.queue) >= self.max_size:
                if self.strategy == BackpressureStrategy.DROP:
                    self._dropped_count += 1
                    logger.warning(f"Queue {self.name} full, dropping item")
                    return False
                elif self.strategy == BackpressureStrategy.SHED_LOAD:
                    # Random sampling - drop with probability
                    import random
                    if random.random() < 0.5:
                        self._dropped_count += 1
                        return False
                # BUFFER and BLOCK will wait
            
            # Wait for space if needed
            if len(self.queue) >= self.max_size:
                if self.strategy == BackpressureStrategy.BLOCK:
                    self._blocked_count += 1
                    if not self._not_full.wait(timeout=timeout):
                        return False  # Timeout
                else:
                    # Remove oldest for BUFFER strategy
                    self.queue.popleft()
                    self._dropped_count += 1
            
            # Add item
            self.queue.append(item)
            self._arrival_count += 1
            self._not_empty.notify()
            return True
    
    def get(self, timeout: Optional[float] = None) -> Optional[Any]:
        """Get item from queue."""
        with self._lock:
            while not self.queue:
                if not self._not_empty.wait(timeout=timeout):
                    return None
            
            item = self.queue.popleft()
            self._processing_count += 1
            self._not_full.notify()
            return item
    
    def get_batch(self, max_items: int, 
                  timeout: Optional[float] = None) -> List[Any]:
        """Get batch of items from queue."""
        with self._lock:
            while not self.queue:
                if not self._not_empty.wait(timeout=timeout):
                    return []
            
            batch_size = min(max_items, len(self.queue))
            items = [self.queue.popleft() for _ in range(batch_size)]
            self._processing_count += batch_size
            self._not_full.notify()
            return items
    
    def record_processing_time(self, processing_time_ms: float):
        """Record processing time for metrics."""
        self._processing_times.append(processing_time_ms)
    
    def update_metrics(self) -> QueueMetrics:
        """Update and return current metrics."""
        with self._lock:
            current_time = time.time()
            time_delta = current_time - self._last_metrics_time
            
            if time_delta > 0:
                self.metrics.arrival_rate = self._arrival_count / time_delta
                self.metrics.processing_rate = self._processing_count / time_delta
            
            self.metrics.current_size = len(self.queue)
            self.metrics.dropped_count = self._dropped_count
            self.metrics.blocked_count = self._blocked_count
            
            if self._processing_times:
                self.metrics.avg_processing_time_ms = sum(self._processing_times) / len(self._processing_times)
            
            # Reset counters
            self._arrival_count = 0
            self._processing_count = 0
            self._last_metrics_time = current_time
            
            return self.metrics
    
    def size(self) -> int:
        """Get current queue size."""
        with self._lock:
            return len(self.queue)
    
    def is_full(self) -> bool:
        """Check if queue is full."""
        with self._lock:
            return len(self.queue) >= self.max_size


class CircuitBreaker:
    """
    Circuit breaker for fault tolerance.
    """
    
    class State(Enum):
        CLOSED = "closed"      # Normal operation
        OPEN = "open"          # Failing, reject requests
        HALF_OPEN = "half_open"  # Testing if recovered
    
    def __init__(self, failure_threshold: int = 5,
                 recovery_timeout_ms: int = 30000,
                 success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_ms = recovery_timeout_ms
        self.success_threshold = success_threshold
        
        self.state = self.State.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self._lock = threading.Lock()
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        with self._lock:
            if self.state == self.State.CLOSED:
                return True
            elif self.state == self.State.OPEN:
                if time.time() * 1000 - self.last_failure_time > self.recovery_timeout_ms:
                    self.state = self.State.HALF_OPEN
                    self.success_count = 0
                    logger.info("Circuit breaker entering HALF_OPEN state")
                    return True
                return False
            else:  # HALF_OPEN
                return True
    
    def record_success(self):
        """Record successful execution."""
        with self._lock:
            if self.state == self.State.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = self.State.CLOSED
                    self.failure_count = 0
                    logger.info("Circuit breaker CLOSED")
            elif self.state == self.State.CLOSED:
                self.failure_count = 0
    
    def record_failure(self):
        """Record failed execution."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time() * 1000
            
            if self.state == self.State.HALF_OPEN:
                self.state = self.State.OPEN
                logger.warning("Circuit breaker OPEN (recovery failed)")
            elif self.state == self.State.CLOSED and self.failure_count >= self.failure_threshold:
                self.state = self.State.OPEN
                logger.warning(f"Circuit breaker OPEN ({self.failure_count} failures)")
    
    def get_state(self) -> State:
        """Get current circuit state."""
        with self._lock:
            return self.state


class BackpressureController:
    """
    Central backpressure controller managing multiple queues.
    """
    
    def __init__(self, check_interval_ms: int = 5000):
        self.queues: Dict[str, BackpressuredQueue] = {}
        self.rate_limiters: Dict[str, AdaptiveRateLimiter] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.check_interval_ms = check_interval_ms
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
    
    def register_queue(self, name: str, queue: BackpressuredQueue):
        """Register a queue for monitoring."""
        self.queues[name] = queue
        
        # Create rate limiter if using adaptive strategy
        if queue.rate_limiter is None:
            queue.rate_limiter = AdaptiveRateLimiter()
        self.rate_limiters[name] = queue.rate_limiter
    
    def register_circuit_breaker(self, name: str, 
                                  circuit_breaker: CircuitBreaker):
        """Register a circuit breaker."""
        self.circuit_breakers[name] = circuit_breaker
    
    def start(self):
        """Start the backpressure controller."""
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        logger.info("Backpressure controller started")
    
    def stop(self):
        """Stop the backpressure controller."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Monitor loop for backpressure."""
        while self._running:
            time.sleep(self.check_interval_ms / 1000)
            
            all_metrics = {}
            for name, queue in self.queues.items():
                metrics = queue.update_metrics()
                all_metrics[name] = metrics
                
                # Adapt rate limiter
                if name in self.rate_limiters:
                    self.rate_limiters[name].adapt(metrics)
                
                # Check for critical conditions
                utilization = metrics.current_size / metrics.max_size
                if utilization > 0.9:
                    logger.error(f"CRITICAL: Queue {name} at {utilization*100:.1f}% capacity")
                    self._notify_critical(name, metrics)
                elif utilization > 0.7:
                    logger.warning(f"WARNING: Queue {name} at {utilization*100:.1f}% capacity")
            
            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(all_metrics)
                except Exception as e:
                    logger.error(f"Error in backpressure callback: {e}")
    
    def _notify_critical(self, queue_name: str, metrics: QueueMetrics):
        """Notify critical backpressure condition."""
        for callback in self._callbacks:
            try:
                callback({'critical': True, 'queue': queue_name, 'metrics': metrics})
            except Exception as e:
                logger.error(f"Error in critical callback: {e}")
    
    def on_metrics(self, callback: Callable):
        """Register metrics callback."""
        self._callbacks.append(callback)
    
    def get_all_metrics(self) -> Dict[str, QueueMetrics]:
        """Get metrics for all queues."""
        return {name: queue.update_metrics() for name, queue in self.queues.items()}
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        metrics = self.get_all_metrics()
        
        total_size = sum(m.current_size for m in metrics.values())
        total_max = sum(m.max_size for m in metrics.values())
        total_dropped = sum(m.dropped_count for m in metrics.values())
        total_blocked = sum(m.blocked_count for m in metrics.values())
        
        utilization = total_size / total_max if total_max > 0 else 0
        
        circuit_states = {name: cb.get_state().value for name, cb in self.circuit_breakers.items()}
        
        return {
            'overall_utilization': utilization,
            'total_queued': total_size,
            'total_capacity': total_max,
            'total_dropped': total_dropped,
            'total_blocked': total_blocked,
            'circuit_breakers': circuit_states,
            'healthy': utilization < 0.8 and all(s == 'closed' for s in circuit_states.values()),
            'timestamp': int(time.time() * 1000)
        }
```


### 4.6 Complex Event Processing (CEP) Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/core/cep_engine.py
"""
Complex Event Processing (CEP) Engine for ResilienceAI
"""

import time
import re
from typing import Dict, List, Callable, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import threading
import logging

logger = logging.getLogger(__name__)


class PatternOperator(Enum):
    """Pattern matching operators."""
    FOLLOWED_BY = "followed_by"           # A -> B
    FOLLOWED_BY_ANY = "followed_by_any"   # A -> B (any match)
    NEXT = "next"                         # A next B
    WITHIN = "within"                     # Pattern within time
    OR = "or"                             # A or B
    AND = "and"                           # A and B
    ONE_OR_MORE = "one_or_more"           # A+
    TIMES = "times"                       # A{3}
    OPTIONAL = "optional"                 # A?


@dataclass
class Event:
    """Represents an event in the CEP engine."""
    event_type: str
    timestamp: int
    data: Dict[str, Any]
    source: Optional[str] = None
    
    def get(self, field: str, default=None):
        """Get field from event data."""
        return self.data.get(field, default)
    
    def matches(self, condition: 'EventCondition') -> bool:
        """Check if event matches condition."""
        return condition.evaluate(self)


@dataclass
class MatchResult:
    """Result of a pattern match."""
    pattern_name: str
    events: List[Event]
    match_start: int
    match_end: int
    match_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventCondition:
    """Condition for matching events."""
    
    def __init__(self, field: Optional[str] = None, 
                 operator: str = "exists",
                 value: Any = None):
        self.field = field
        self.operator = operator
        self.value = value
        self.sub_conditions: List['EventCondition'] = []
    
    @classmethod
    def eq(cls, field: str, value: Any) -> 'EventCondition':
        """Equality condition."""
        return cls(field, "eq", value)
    
    @classmethod
    def gt(cls, field: str, value: Any) -> 'EventCondition':
        """Greater than condition."""
        return cls(field, "gt", value)
    
    @classmethod
    def lt(cls, field: str, value: Any) -> 'EventCondition':
        """Less than condition."""
        return cls(field, "lt", value)
    
    @classmethod
    def gte(cls, field: str, value: Any) -> 'EventCondition':
        """Greater than or equal condition."""
        return cls(field, "gte", value)
    
    @classmethod
    def lte(cls, field: str, value: Any) -> 'EventCondition':
        """Less than or equal condition."""
        return cls(field, "lte", value)
    
    @classmethod
    def contains(cls, field: str, value: Any) -> 'EventCondition':
        """Contains condition."""
        return cls(field, "contains", value)
    
    @classmethod
    def regex(cls, field: str, pattern: str) -> 'EventCondition':
        """Regex match condition."""
        return cls(field, "regex", pattern)
    
    @classmethod
    def and_(cls, *conditions: 'EventCondition') -> 'EventCondition':
        """Combine conditions with AND."""
        cond = cls(operator="and")
        cond.sub_conditions = list(conditions)
        return cond
    
    @classmethod
    def or_(cls, *conditions: 'EventCondition') -> 'EventCondition':
        """Combine conditions with OR."""
        cond = cls(operator="or")
        cond.sub_conditions = list(conditions)
        return cond
    
    def evaluate(self, event: Event) -> bool:
        """Evaluate condition against event."""
        if self.operator == "exists":
            return self.field is None or event.get(self.field) is not None
        
        if self.operator == "and":
            return all(c.evaluate(event) for c in self.sub_conditions)
        
        if self.operator == "or":
            return any(c.evaluate(event) for c in self.sub_conditions)
        
        field_value = event.get(self.field)
        if field_value is None:
            return False
        
        if self.operator == "eq":
            return field_value == self.value
        elif self.operator == "gt":
            return field_value > self.value
        elif self.operator == "lt":
            return field_value < self.value
        elif self.operator == "gte":
            return field_value >= self.value
        elif self.operator == "lte":
            return field_value <= self.value
        elif self.operator == "contains":
            return self.value in field_value if isinstance(field_value, (list, str)) else False
        elif self.operator == "regex":
            return bool(re.match(self.value, str(field_value)))
        
        return False


class Pattern:
    """
    CEP Pattern definition.
    """
    
    def __init__(self, name: str, event_type: str,
                 condition: Optional[EventCondition] = None):
        self.name = name
        self.event_type = event_type
        self.condition = condition or EventCondition()
        self.next_pattern: Optional['Pattern'] = None
        self.operator: PatternOperator = PatternOperator.FOLLOWED_BY
        self.time_window_ms: Optional[int] = None
        self.times_count: Optional[int] = None
        self.is_optional = False
        self.sub_patterns: List['Pattern'] = []
    
    def where(self, condition: EventCondition) -> 'Pattern':
        """Add condition to pattern."""
        self.condition = condition
        return self
    
    def followed_by(self, pattern: 'Pattern') -> 'Pattern':
        """Add followed-by pattern."""
        self.next_pattern = pattern
        self.operator = PatternOperator.FOLLOWED_BY
        return pattern
    
    def next(self, pattern: 'Pattern') -> 'Pattern':
        """Add next pattern (consecutive)."""
        self.next_pattern = pattern
        self.operator = PatternOperator.NEXT
        return pattern
    
    def or_(self, pattern: 'Pattern') -> 'Pattern':
        """Add OR pattern."""
        self.sub_patterns.append(pattern)
        self.operator = PatternOperator.OR
        return self
    
    def and_(self, pattern: 'Pattern') -> 'Pattern':
        """Add AND pattern."""
        self.sub_patterns.append(pattern)
        self.operator = PatternOperator.AND
        return self
    
    def one_or_more(self) -> 'Pattern':
        """Mark pattern as one or more."""
        self.operator = PatternOperator.ONE_OR_MORE
        return self
    
    def times(self, count: int) -> 'Pattern':
        """Set exact times to match."""
        self.times_count = count
        self.operator = PatternOperator.TIMES
        return self
    
    def optional(self) -> 'Pattern':
        """Mark pattern as optional."""
        self.is_optional = True
        return self
    
    def within(self, milliseconds: int) -> 'Pattern':
        """Set time window."""
        self.time_window_ms = milliseconds
        return self
    
    def matches_start(self, event: Event) -> bool:
        """Check if event matches pattern start."""
        return event.event_type == self.event_type and event.matches(self.condition)


class PatternMatch:
    """In-progress pattern match."""
    
    def __init__(self, pattern: Pattern, start_time: int):
        self.pattern = pattern
        self.events: List[Event] = []
        self.start_time = start_time
        self.current_pattern = pattern
        self.match_id = f"{start_time}_{id(self)}"
        self.is_complete = False
    
    def add_event(self, event: Event) -> bool:
        """Add event to match. Returns True if match is complete."""
        self.events.append(event)
        
        if self.current_pattern.next_pattern:
            self.current_pattern = self.current_pattern.next_pattern
            return False
        else:
            self.is_complete = True
            return True
    
    def can_accept(self, event: Event) -> bool:
        """Check if match can accept event."""
        if not self.current_pattern:
            return False
        
        # Check time window
        if self.pattern.time_window_ms:
            if event.timestamp - self.start_time > self.pattern.time_window_ms:
                return False
        
        return (event.event_type == self.current_pattern.event_type and 
                event.matches(self.current_pattern.condition))
    
    def to_result(self) -> MatchResult:
        """Convert to match result."""
        return MatchResult(
            pattern_name=self.pattern.name,
            events=self.events,
            match_start=self.start_time,
            match_end=self.events[-1].timestamp if self.events else self.start_time,
            match_id=self.match_id
        )


class CEPEngine:
    """
    Complex Event Processing Engine.
    """
    
    def __init__(self, event_buffer_size: int = 10000):
        self.patterns: Dict[str, Pattern] = {}
        self.active_matches: Dict[str, List[PatternMatch]] = defaultdict(list)
        self.event_buffer: deque = deque(maxlen=event_buffer_size)
        self.match_callbacks: List[Callable[[MatchResult], None]] = []
        self._lock = threading.RLock()
        self._running = False
    
    def register_pattern(self, pattern: Pattern):
        """Register a pattern for matching."""
        self.patterns[pattern.name] = pattern
        logger.info(f"Registered pattern: {pattern.name}")
    
    def process_event(self, event: Event):
        """Process an event through all patterns."""
        with self._lock:
            # Add to buffer
            self.event_buffer.append(event)
            
            # Try to match with existing matches
            self._continue_matches(event)
            
            # Try to start new matches
            self._start_new_matches(event)
            
            # Clean up expired matches
            self._cleanup_expired_matches(event.timestamp)
    
    def _start_new_matches(self, event: Event):
        """Start new pattern matches."""
        for pattern in self.patterns.values():
            if pattern.matches_start(event):
                match = PatternMatch(pattern, event.timestamp)
                match.add_event(event)
                
                if match.is_complete:
                    # Single-event pattern
                    self._emit_match(match.to_result())
                else:
                    self.active_matches[pattern.name].append(match)
    
    def _continue_matches(self, event: Event):
        """Continue existing pattern matches."""
        for pattern_name, matches in list(self.active_matches.items()):
            for match in matches:
                if match.can_accept(event):
                    is_complete = match.add_event(event)
                    
                    if is_complete:
                        self._emit_match(match.to_result())
                        matches.remove(match)
    
    def _cleanup_expired_matches(self, current_timestamp: int):
        """Remove expired pattern matches."""
        for pattern_name, matches in list(self.active_matches.items()):
            pattern = self.patterns.get(pattern_name)
            if pattern and pattern.time_window_ms:
                expired = [
                    m for m in matches 
                    if current_timestamp - m.start_time > pattern.time_window_ms
                ]
                for m in expired:
                    matches.remove(m)
    
    def _emit_match(self, result: MatchResult):
        """Emit pattern match result."""
        logger.info(f"Pattern matched: {result.pattern_name} with {len(result.events)} events")
        
        for callback in self.match_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Error in match callback: {e}")
    
    def on_match(self, callback: Callable[[MatchResult], None]):
        """Register match callback."""
        self.match_callbacks.append(callback)
    
    def get_active_match_count(self) -> int:
        """Get number of active pattern matches."""
        with self._lock:
            return sum(len(matches) for matches in self.active_matches.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        with self._lock:
            return {
                'patterns': len(self.patterns),
                'active_matches': self.get_active_match_count(),
                'buffered_events': len(self.event_buffer),
                'pattern_names': list(self.patterns.keys())
            }


# Pre-built patterns for ResilienceAI
class ResiliencePatterns:
    """Common patterns for resilience monitoring."""
    
    @staticmethod
    def failure_cascade_pattern() -> Pattern:
        """
        Detect failure cascade: Multiple service failures in short time.
        Pattern: 3+ service failures within 30 seconds
        """
        failure = Pattern("failure_cascade", "service_failure")
        failure.where(EventCondition.eq("severity", "critical"))
        failure.one_or_more()
        failure.within(30000)
        return failure
    
    @staticmethod
    def slow_recovery_pattern() -> Pattern:
        """
        Detect slow recovery: Service fails, then takes too long to recover.
        Pattern: failure -> (no recovery within 5 minutes)
        """
        failure = Pattern("slow_recovery_start", "service_failure")
        recovery = Pattern("slow_recovery_end", "service_recovery")
        failure.followed_by(recovery)
        failure.within(300000)  # 5 minutes
        return failure
    
    @staticmethod
    def threshold_breach_pattern(metric: str, threshold: float) -> Pattern:
        """
        Detect threshold breach: Metric exceeds threshold 3 times.
        """
        breach = Pattern(f"threshold_breach_{metric}", "metric_alert")
        breach.where(
            EventCondition.and_(
                EventCondition.eq("metric", metric),
                EventCondition.gt("value", threshold)
            )
        )
        breach.times(3)
        breach.within(60000)  # 1 minute
        return breach
    
    @staticmethod
    def anomaly_spike_pattern() -> Pattern:
        """
        Detect anomaly spike: Sudden increase in anomalies.
        Pattern: normal -> anomaly -> anomaly -> anomaly
        """
        normal = Pattern("spike_start", "system_status")
        normal.where(EventCondition.eq("status", "normal"))
        
        anomaly = Pattern("spike_anomaly", "anomaly_detected")
        anomaly.times(3)
        
        normal.followed_by(anomaly)
        normal.within(60000)
        return normal
    
    @staticmethod
    def circuit_breaker_pattern() -> Pattern:
        """
        Detect circuit breaker pattern: High error rate followed by recovery.
        Pattern: errors > threshold -> circuit_open -> circuit_closed
        """
        errors = Pattern("cb_errors", "error_rate")
        errors.where(EventCondition.gt("rate", 0.5))
        
        open_cb = Pattern("cb_open", "circuit_breaker")
        open_cb.where(EventCondition.eq("state", "open"))
        
        closed_cb = Pattern("cb_closed", "circuit_breaker")
        closed_cb.where(EventCondition.eq("state", "closed"))
        
        errors.followed_by(open_cb)
        open_cb.followed_by(closed_cb)
        errors.within(300000)  # 5 minutes
        return errors
    
    @staticmethod
    def resource_exhaustion_pattern() -> Pattern:
        """
        Detect resource exhaustion: CPU/Memory climbing to critical.
        Pattern: warning -> critical (within 2 minutes)
        """
        warning = Pattern("resource_warning", "resource_alert")
        warning.where(EventCondition.eq("level", "warning"))
        
        critical = Pattern("resource_critical", "resource_alert")
        critical.where(EventCondition.eq("level", "critical"))
        
        warning.followed_by(critical)
        warning.within(120000)
        return warning


# Example usage
if __name__ == "__main__":
    # Create CEP engine
    cep = CEPEngine()
    
    # Register patterns
    cep.register_pattern(ResiliencePatterns.failure_cascade_pattern())
    cep.register_pattern(ResiliencePatterns.threshold_breach_pattern("cpu_usage", 90.0))
    
    # Add match handler
    def on_match(result: MatchResult):
        print(f"Pattern '{result.pattern_name}' matched!")
        for event in result.events:
            print(f"  - {event.event_type} at {event.timestamp}")
    
    cep.on_match(on_match)
    
    # Process events
    events = [
        Event("service_failure", int(time.time() * 1000), 
              {"service": "api", "severity": "critical"}),
        Event("service_failure", int(time.time() * 1000) + 1000, 
              {"service": "db", "severity": "critical"}),
        Event("service_failure", int(time.time() * 1000) + 2000, 
              {"service": "cache", "severity": "critical"}),
    ]
    
    for event in events:
        cep.process_event(event)
```


### 4.7 Redis Streams Integration

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/core/redis_streams.py
"""
Redis Streams Integration for ResilienceAI
"""

import json
import time
import redis
from typing import Dict, List, Optional, Any, Callable, Iterator
from dataclasses import dataclass
from enum import Enum
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class RedisStreamRecord:
    """Redis Stream record."""
    stream_id: str
    fields: Dict[str, Any]
    timestamp: int


class RedisStreamConsumer:
    """
    Redis Streams consumer with consumer groups.
    """
    
    def __init__(self, redis_client: redis.Redis, stream_name: str,
                 group_name: str, consumer_name: str,
                 auto_ack: bool = False):
        self.redis = redis_client
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.auto_ack = auto_ack
        self._running = False
        self.message_callbacks: List[Callable[[RedisStreamRecord], None]] = []
    
    def create_group(self, mkstream: bool = True) -> bool:
        """Create consumer group if not exists."""
        try:
            self.redis.xgroup_create(
                self.stream_name, 
                self.group_name,
                id='0',
                mkstream=mkstream
            )
            logger.info(f"Created consumer group: {self.group_name}")
            return True
        except redis.ResponseError as e:
            if "already exists" in str(e):
                return True
            logger.error(f"Failed to create group: {e}")
            return False
    
    def consume(self, count: int = 100, block_ms: int = 5000,
                start_id: str = '>') -> List[RedisStreamRecord]:
        """
        Consume messages from stream.
        
        Args:
            count: Maximum number of messages to read
            block_ms: Block timeout in milliseconds
            start_id: Start ID ('>' for new messages, '0' for pending)
        
        Returns:
            List of RedisStreamRecord
        """
        try:
            messages = self.redis.xreadgroup(
                groupname=self.group_name,
                consumername=self.consumer_name,
                streams={self.stream_name: start_id},
                count=count,
                block=block_ms
            )
            
            records = []
            for stream_name, msgs in messages:
                for msg_id, fields in msgs:
                    record = RedisStreamRecord(
                        stream_id=msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                        fields={
                            k.decode() if isinstance(k, bytes) else k: 
                            json.loads(v.decode() if isinstance(v, bytes) else v)
                            for k, v in fields.items()
                        },
                        timestamp=int(time.time() * 1000)
                    )
                    records.append(record)
                    
                    if self.auto_ack:
                        self.ack(record.stream_id)
            
            return records
        
        except Exception as e:
            logger.error(f"Error consuming from {self.stream_name}: {e}")
            return []
    
    def ack(self, stream_id: str):
        """Acknowledge message processing."""
        try:
            self.redis.xack(self.stream_name, self.group_name, stream_id)
        except Exception as e:
            logger.error(f"Error acknowledging message {stream_id}: {e}")
    
    def claim_pending(self, min_idle_ms: int = 60000,
                      count: int = 100) -> List[RedisStreamRecord]:
        """Claim pending messages from other consumers."""
        try:
            # Get pending messages
            pending = self.redis.xpending_range(
                self.stream_name,
                self.group_name,
                min='-',
                max='+',
                count=count
            )
            
            if not pending:
                return []
            
            # Claim messages idle for min_idle_ms
            message_ids = [p['message_id'] for p in pending 
                          if p['time_since_delivered'] > min_idle_ms]
            
            if not message_ids:
                return []
            
            claimed = self.redis.xclaim(
                self.stream_name,
                self.group_name,
                self.consumer_name,
                min_idle_time=min_idle_ms,
                message_ids=message_ids
            )
            
            records = []
            for msg_id, fields in claimed:
                record = RedisStreamRecord(
                    stream_id=msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                    fields={
                        k.decode() if isinstance(k, bytes) else k: 
                        json.loads(v.decode() if isinstance(v, bytes) else v)
                        for k, v in fields.items()
                    },
                    timestamp=int(time.time() * 1000)
                )
                records.append(record)
            
            return records
        
        except Exception as e:
            logger.error(f"Error claiming pending messages: {e}")
            return []
    
    def get_pending_info(self) -> Dict[str, Any]:
        """Get pending messages info."""
        try:
            info = self.redis.xpending(
                self.stream_name,
                self.group_name
            )
            return {
                'pending_count': info['pending'],
                'min_id': info['min'],
                'max_id': info['max'],
                'consumers': info['consumers']
            }
        except Exception as e:
            logger.error(f"Error getting pending info: {e}")
            return {}
    
    def start_consuming(self, poll_interval_ms: int = 100):
        """Start continuous consuming in background thread."""
        self._running = True
        
        def consume_loop():
            while self._running:
                records = self.consume(count=100, block_ms=poll_interval_ms)
                for record in records:
                    for callback in self.message_callbacks:
                        try:
                            callback(record)
                        except Exception as e:
                            logger.error(f"Error in message callback: {e}")
        
        thread = threading.Thread(target=consume_loop)
        thread.daemon = True
        thread.start()
    
    def stop_consuming(self):
        """Stop continuous consuming."""
        self._running = False
    
    def on_message(self, callback: Callable[[RedisStreamRecord], None]):
        """Register message callback."""
        self.message_callbacks.append(callback)


class RedisStreamProducer:
    """
    Redis Streams producer with batching and retry.
    """
    
    def __init__(self, redis_client: redis.Redis,
                 max_batch_size: int = 100,
                 flush_interval_ms: int = 100):
        self.redis = redis_client
        self.max_batch_size = max_batch_size
        self.flush_interval_ms = flush_interval_ms
        self.batch: Dict[str, List[Dict]] = {}
        self._lock = threading.Lock()
        self._flush_thread: Optional[threading.Thread] = None
        self._running = False
    
    def produce(self, stream_name: str, data: Dict[str, Any],
                stream_id: str = '*') -> Optional[str]:
        """
        Produce message to stream.
        
        Args:
            stream_name: Target stream name
            data: Message data (will be JSON serialized)
            stream_id: Stream ID ('*' for auto-generated)
        
        Returns:
            Stream ID if successful
        """
        try:
            fields = {k: json.dumps(v) for k, v in data.items()}
            result = self.redis.xadd(stream_name, fields, id=stream_id)
            return result.decode() if isinstance(result, bytes) else result
        except Exception as e:
            logger.error(f"Error producing to {stream_name}: {e}")
            return None
    
    def produce_batch(self, stream_name: str, 
                      messages: List[Dict[str, Any]]) -> List[str]:
        """Produce multiple messages to stream."""
        ids = []
        pipe = self.redis.pipeline()
        
        for msg in messages:
            fields = {k: json.dumps(v) for k, v in msg.items()}
            pipe.xadd(stream_name, fields)
        
        try:
            results = pipe.execute()
            return [r.decode() if isinstance(r, bytes) else r for r in results]
        except Exception as e:
            logger.error(f"Error in batch produce: {e}")
            return []
    
    def add_to_batch(self, stream_name: str, data: Dict[str, Any]):
        """Add message to batch for later flushing."""
        with self._lock:
            if stream_name not in self.batch:
                self.batch[stream_name] = []
            self.batch[stream_name].append(data)
            
            if len(self.batch[stream_name]) >= self.max_batch_size:
                self._flush_stream(stream_name)
    
    def _flush_stream(self, stream_name: str):
        """Flush batch for specific stream."""
        with self._lock:
            if stream_name in self.batch and self.batch[stream_name]:
                messages = self.batch[stream_name]
                self.batch[stream_name] = []
                self.produce_batch(stream_name, messages)
    
    def flush_all(self):
        """Flush all pending batches."""
        with self._lock:
            for stream_name in list(self.batch.keys()):
                self._flush_stream(stream_name)
    
    def start_auto_flush(self):
        """Start automatic batch flushing."""
        self._running = True
        
        def flush_loop():
            while self._running:
                time.sleep(self.flush_interval_ms / 1000)
                self.flush_all()
        
        self._flush_thread = threading.Thread(target=flush_loop)
        self._flush_thread.daemon = True
        self._flush_thread.start()
    
    def stop_auto_flush(self):
        """Stop automatic batch flushing."""
        self._running = False
        if self._flush_thread:
            self._flush_thread.join(timeout=5)
        self.flush_all()


class RedisStreamManager:
    """
    Manager for Redis Streams operations.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def create_stream(self, stream_name: str, 
                      max_length: Optional[int] = None,
                      approximate: bool = True) -> bool:
        """Create a new stream."""
        try:
            # Add a dummy entry and delete it to create stream
            entry_id = self.redis.xadd(stream_name, {'_init': 'true'})
            self.redis.xdel(stream_name, entry_id)
            
            if max_length:
                self.redis.xtrim(stream_name, maxlen=max_length, approximate=approximate)
            
            logger.info(f"Created stream: {stream_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating stream {stream_name}: {e}")
            return False
    
    def delete_stream(self, stream_name: str) -> bool:
        """Delete a stream."""
        try:
            self.redis.delete(stream_name)
            logger.info(f"Deleted stream: {stream_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting stream {stream_name}: {e}")
            return False
    
    def get_stream_info(self, stream_name: str) -> Dict[str, Any]:
        """Get stream information."""
        try:
            info = self.redis.xinfo_stream(stream_name)
            return {
                'length': info['length'],
                'radix_tree_keys': info['radix-tree-keys'],
                'radix_tree_nodes': info['radix-tree-nodes'],
                'groups': info['groups'],
                'last_generated_id': info['last-generated-id'],
                'first_entry': info.get('first-entry'),
                'last_entry': info.get('last-entry')
            }
        except Exception as e:
            logger.error(f"Error getting stream info: {e}")
            return {}
    
    def get_group_info(self, stream_name: str) -> List[Dict[str, Any]]:
        """Get consumer group information."""
        try:
            groups = self.redis.xinfo_groups(stream_name)
            return [
                {
                    'name': g['name'].decode() if isinstance(g['name'], bytes) else g['name'],
                    'consumers': g['consumers'],
                    'pending': g['pending'],
                    'last_delivered_id': g['last-delivered-id']
                }
                for g in groups
            ]
        except Exception as e:
            logger.error(f"Error getting group info: {e}")
            return []
    
    def get_consumer_info(self, stream_name: str, 
                          group_name: str) -> List[Dict[str, Any]]:
        """Get consumer information for a group."""
        try:
            consumers = self.redis.xinfo_consumers(stream_name, group_name)
            return [
                {
                    'name': c['name'].decode() if isinstance(c['name'], bytes) else c['name'],
                    'pending': c['pending'],
                    'idle': c['idle']
                }
                for c in consumers
            ]
        except Exception as e:
            logger.error(f"Error getting consumer info: {e}")
            return []
    
    def trim_stream(self, stream_name: str, max_length: int,
                    approximate: bool = True) -> int:
        """Trim stream to maximum length."""
        try:
            return self.redis.xtrim(stream_name, maxlen=max_length, approximate=approximate)
        except Exception as e:
            logger.error(f"Error trimming stream: {e}")
            return 0
    
    def read_range(self, stream_name: str, start: str = '-',
                   end: str = '+', count: Optional[int] = None) -> List[RedisStreamRecord]:
        """Read messages from stream range."""
        try:
            messages = self.redis.xrange(stream_name, min=start, max=end, count=count)
            
            records = []
            for msg_id, fields in messages:
                record = RedisStreamRecord(
                    stream_id=msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                    fields={
                        k.decode() if isinstance(k, bytes) else k: 
                        json.loads(v.decode() if isinstance(v, bytes) else v)
                        for k, v in fields.items()
                    },
                    timestamp=int(time.time() * 1000)
                )
                records.append(record)
            
            return records
        except Exception as e:
            logger.error(f"Error reading stream range: {e}")
            return []


# Integration with Kafka for hybrid architecture
class KafkaRedisBridge:
    """
    Bridge between Kafka and Redis Streams.
    """
    
    def __init__(self, kafka_producer, redis_client: redis.Redis):
        self.kafka_producer = kafka_producer
        self.redis = redis_client
        self.redis_producer = RedisStreamProducer(redis_client)
    
    def kafka_to_redis(self, kafka_topic: str, redis_stream: str,
                       message_transform: Optional[Callable] = None):
        """
        Forward messages from Kafka to Redis Streams.
        
        Usage: Connect to Kafka consumer and forward to Redis.
        """
        def forward(message):
            data = message.value()
            if message_transform:
                data = message_transform(data)
            self.redis_producer.produce(redis_stream, data)
        
        return forward
    
    def redis_to_kafka(self, redis_stream: str, kafka_topic: str,
                       message_transform: Optional[Callable] = None):
        """
        Forward messages from Redis Streams to Kafka.
        
        Usage: Register as Redis consumer callback.
        """
        def forward(record: RedisStreamRecord):
            data = record.fields
            if message_transform:
                data = message_transform(data)
            self.kafka_producer.produce(kafka_topic, data)
        
        return forward


# Example usage
if __name__ == "__main__":
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # Create stream manager
    manager = RedisStreamManager(r)
    
    # Create stream
    manager.create_stream("resilience:events", max_length=10000)
    
    # Create producer
    producer = RedisStreamProducer(r)
    
    # Produce messages
    producer.produce("resilience:events", {
        "event_type": "metric_alert",
        "service": "api-gateway",
        "metric": "cpu_usage",
        "value": 85.5,
        "timestamp": int(time.time() * 1000)
    })
    
    # Create consumer
    consumer = RedisStreamConsumer(
        r, "resilience:events", 
        "analytics-group", "consumer-1"
    )
    consumer.create_group()
    
    # Consume messages
    records = consumer.consume(count=10)
    for record in records:
        print(f"Received: {record.fields}")
        consumer.ack(record.stream_id)
```


### 4.8 Stream Monitoring Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/monitoring/stream_monitor.py
"""
Stream Processing Monitoring for ResilienceAI
"""

import time
import json
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from collections import deque, defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class StreamMetrics:
    """Metrics for a stream."""
    stream_name: str
    messages_in: int = 0
    messages_out: int = 0
    bytes_in: int = 0
    bytes_out: int = 0
    processing_time_ms: float = 0.0
    errors: int = 0
    lag: int = 0
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass
class ConsumerGroupMetrics:
    """Metrics for a consumer group."""
    group_id: str
    topic: str
    active_consumers: int = 0
    total_lag: int = 0
    partitions: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass
class PipelineMetrics:
    """Metrics for a processing pipeline."""
    pipeline_name: str
    stage_metrics: Dict[str, StreamMetrics] = field(default_factory=dict)
    throughput_per_sec: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p99_ms: float = 0.0
    error_rate: float = 0.0
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))


class MetricsCollector:
    """
    Collects and aggregates stream processing metrics.
    """
    
    def __init__(self, window_size_seconds: int = 60):
        self.window_size_seconds = window_size_seconds
        self.stream_metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=window_size_seconds)
        )
        self.latency_histograms: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self._lock = threading.Lock()
        self._running = False
        self._aggregator_thread: Optional[threading.Thread] = None
    
    def record_message_in(self, stream_name: str, bytes_size: int = 0):
        """Record incoming message."""
        with self._lock:
            self._ensure_current_minute(stream_name)
            current = self.stream_metrics[stream_name][-1]
            current.messages_in += 1
            current.bytes_in += bytes_size
    
    def record_message_out(self, stream_name: str, bytes_size: int = 0):
        """Record outgoing message."""
        with self._lock:
            self._ensure_current_minute(stream_name)
            current = self.stream_metrics[stream_name][-1]
            current.messages_out += 1
            current.bytes_out += bytes_size
    
    def record_processing_time(self, stream_name: str, time_ms: float):
        """Record message processing time."""
        with self._lock:
            self._ensure_current_minute(stream_name)
            current = self.stream_metrics[stream_name][-1]
            current.processing_time_ms += time_ms
            
            # Add to latency histogram
            self.latency_histograms[stream_name].append(time_ms)
    
    def record_error(self, stream_name: str):
        """Record processing error."""
        with self._lock:
            self._ensure_current_minute(stream_name)
            current = self.stream_metrics[stream_name][-1]
            current.errors += 1
    
    def record_lag(self, stream_name: str, lag: int):
        """Record consumer lag."""
        with self._lock:
            self._ensure_current_minute(stream_name)
            current = self.stream_metrics[stream_name][-1]
            current.lag = lag
    
    def _ensure_current_minute(self, stream_name: str):
        """Ensure we have a metric entry for current minute."""
        current_minute = int(time.time()) // 60 * 60 * 1000
        
        if (not self.stream_metrics[stream_name] or 
            self.stream_metrics[stream_name][-1].timestamp < current_minute):
            self.stream_metrics[stream_name].append(
                StreamMetrics(stream_name=stream_name, timestamp=current_minute)
            )
    
    def get_stream_stats(self, stream_name: str, 
                         duration_minutes: int = 5) -> Dict[str, Any]:
        """Get statistics for a stream."""
        with self._lock:
            if stream_name not in self.stream_metrics:
                return {}
            
            metrics_list = list(self.stream_metrics[stream_name])[-duration_minutes:]
            
            if not metrics_list:
                return {}
            
            total_in = sum(m.messages_in for m in metrics_list)
            total_out = sum(m.messages_out for m in metrics_list)
            total_errors = sum(m.errors for m in metrics_list)
            total_bytes_in = sum(m.bytes_in for m in metrics_list)
            total_bytes_out = sum(m.bytes_out for m in metrics_list)
            avg_processing_time = (
                sum(m.processing_time_ms for m in metrics_list) / max(total_in, 1)
            )
            latest_lag = metrics_list[-1].lag if metrics_list else 0
            
            # Calculate latency percentiles
            latencies = list(self.latency_histograms[stream_name])
            latency_p50 = self._percentile(latencies, 50) if latencies else 0
            latency_p99 = self._percentile(latencies, 99) if latencies else 0
            
            return {
                'stream_name': stream_name,
                'duration_minutes': duration_minutes,
                'messages_in': total_in,
                'messages_out': total_out,
                'messages_per_sec': total_in / (duration_minutes * 60),
                'bytes_in': total_bytes_in,
                'bytes_out': total_bytes_out,
                'errors': total_errors,
                'error_rate': total_errors / max(total_in, 1),
                'avg_processing_time_ms': avg_processing_time,
                'latency_p50_ms': latency_p50,
                'latency_p99_ms': latency_p99,
                'current_lag': latest_lag,
                'timestamp': int(time.time() * 1000)
            }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all streams."""
        with self._lock:
            return {
                name: self.get_stream_stats(name)
                for name in self.stream_metrics.keys()
            }
    
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self.stream_metrics.clear()
            self.latency_histograms.clear()


class StreamHealthChecker:
    """
    Health checking for stream processing components.
    """
    
    def __init__(self):
        self.health_checks: Dict[str, Callable[[], Dict[str, Any]]] = {}
        self.health_status: Dict[str, str] = {}
        self.last_check: Dict[str, int] = {}
    
    def register_check(self, name: str, 
                       check_fn: Callable[[], Dict[str, Any]]):
        """Register a health check."""
        self.health_checks[name] = check_fn
    
    def check_health(self, name: str) -> Dict[str, Any]:
        """Run a specific health check."""
        if name not in self.health_checks:
            return {'status': 'unknown', 'error': 'Check not registered'}
        
        try:
            result = self.health_checks[name]()
            result['timestamp'] = int(time.time() * 1000)
            
            # Determine status
            if result.get('healthy', True):
                self.health_status[name] = 'healthy'
            else:
                self.health_status[name] = 'unhealthy'
            
            self.last_check[name] = int(time.time() * 1000)
            return result
        
        except Exception as e:
            self.health_status[name] = 'error'
            self.last_check[name] = int(time.time() * 1000)
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': int(time.time() * 1000)
            }
    
    def check_all(self) -> Dict[str, Dict[str, Any]]:
        """Run all health checks."""
        return {name: self.check_health(name) for name in self.health_checks.keys()}
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        all_checks = self.check_all()
        
        healthy_count = sum(1 for r in all_checks.values() if r.get('healthy', False))
        total_count = len(all_checks)
        
        return {
            'overall_status': 'healthy' if healthy_count == total_count else 'degraded',
            'healthy_components': healthy_count,
            'total_components': total_count,
            'components': all_checks,
            'timestamp': int(time.time() * 1000)
        }


class AlertManager:
    """
    Alert management for stream processing.
    """
    
    def __init__(self):
        self.alert_rules: List[Dict[str, Any]] = []
        self.alert_handlers: List[Callable[[Dict], None]] = []
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.alert_history: deque = deque(maxlen=1000)
    
    def add_rule(self, name: str, condition: Callable[[Dict[str, Any]], bool],
                 severity: str = 'warning', cooldown_ms: int = 60000):
        """Add an alert rule."""
        self.alert_rules.append({
            'name': name,
            'condition': condition,
            'severity': severity,
            'cooldown_ms': cooldown_ms,
            'last_triggered': 0
        })
    
    def evaluate_rules(self, metrics: Dict[str, Any]):
        """Evaluate all alert rules against metrics."""
        current_time = int(time.time() * 1000)
        
        for rule in self.alert_rules:
            # Check cooldown
            if current_time - rule['last_triggered'] < rule['cooldown_ms']:
                continue
            
            try:
                if rule['condition'](metrics):
                    alert = {
                        'name': rule['name'],
                        'severity': rule['severity'],
                        'timestamp': current_time,
                        'metrics': metrics
                    }
                    
                    self._trigger_alert(alert)
                    rule['last_triggered'] = current_time
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule['name']}: {e}")
    
    def _trigger_alert(self, alert: Dict[str, Any]):
        """Trigger an alert."""
        alert_id = f"{alert['name']}:{alert['timestamp']}"
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        logger.warning(f"ALERT: {alert['name']} - {alert['severity']}")
        
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def resolve_alert(self, alert_id: str):
        """Resolve an active alert."""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
    
    def on_alert(self, handler: Callable[[Dict], None]):
        """Register alert handler."""
        self.alert_handlers.append(handler)
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history."""
        return list(self.alert_history)[-limit:]


class StreamMonitor:
    """
    Main stream monitoring component.
    """
    
    def __init__(self, metrics_collector: MetricsCollector,
                 health_checker: StreamHealthChecker,
                 alert_manager: AlertManager):
        self.metrics = metrics_collector
        self.health = health_checker
        self.alerts = alert_manager
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def start(self, interval_seconds: int = 30):
        """Start monitoring."""
        self._running = True
        
        def monitor_loop():
            while self._running:
                time.sleep(interval_seconds)
                
                # Collect all stats
                all_stats = self.metrics.get_all_stats()
                
                # Check health
                health_status = self.health.get_overall_health()
                
                # Evaluate alert rules
                for stream_name, stats in all_stats.items():
                    self.alerts.evaluate_rules(stats)
                
                # Log summary
                logger.info(f"Monitor check: {len(all_stats)} streams, "
                           f"health: {health_status['overall_status']}")
        
        self._monitor_thread = threading.Thread(target=monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        logger.info("Stream monitor started")
    
    def stop(self):
        """Stop monitoring."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard."""
        return {
            'metrics': self.metrics.get_all_stats(),
            'health': self.health.get_overall_health(),
            'alerts': {
                'active': self.alerts.get_active_alerts(),
                'recent': self.alerts.get_alert_history(10)
            },
            'timestamp': int(time.time() * 1000)
        }


# Common alert rules
class CommonAlertRules:
    """Common alert rules for stream processing."""
    
    @staticmethod
    def high_lag_rule(threshold: int = 10000):
        """Alert on high consumer lag."""
        return lambda metrics: metrics.get('current_lag', 0) > threshold
    
    @staticmethod
    def high_error_rate_rule(threshold: float = 0.05):
        """Alert on high error rate."""
        return lambda metrics: metrics.get('error_rate', 0) > threshold
    
    @staticmethod
    def high_latency_rule(threshold_ms: float = 1000.0):
        """Alert on high latency."""
        return lambda metrics: metrics.get('latency_p99_ms', 0) > threshold_ms
    
    @staticmethod
    def no_messages_rule(duration_minutes: int = 5):
        """Alert when no messages received."""
        return lambda metrics: (
            metrics.get('messages_in', 0) == 0 and 
            metrics.get('duration_minutes', 0) >= duration_minutes
        )
    
    @staticmethod
    def processing_stalled_rule(threshold_ratio: float = 0.5):
        """Alert when processing is stalled (out < in * threshold)."""
        return lambda metrics: (
            metrics.get('messages_out', 0) < 
            metrics.get('messages_in', 0) * threshold_ratio
        )


# Example usage
if __name__ == "__main__":
    # Create components
    metrics = MetricsCollector()
    health = StreamHealthChecker()
    alerts = AlertManager()
    monitor = StreamMonitor(metrics, health, alerts)
    
    # Register health checks
    health.register_check("kafka", lambda: {
        'healthy': True,
        'brokers': 3,
        'topics': 10
    })
    
    # Add alert rules
    alerts.add_rule(
        "high-lag",
        CommonAlertRules.high_lag_rule(5000),
        severity="warning"
    )
    alerts.add_rule(
        "high-error-rate",
        CommonAlertRules.high_error_rate_rule(0.01),
        severity="critical"
    )
    
    # Register alert handler
    def on_alert(alert):
        print(f"ALERT: {alert['name']} - {alert['severity']}")
    
    alerts.on_alert(on_alert)
    
    # Start monitoring
    monitor.start(interval_seconds=10)
    
    # Simulate metrics
    for i in range(100):
        metrics.record_message_in("test-stream")
        metrics.record_processing_time("test-stream", 50 + i % 100)
        if i % 10 == 0:
            metrics.record_error("test-stream")
    
    # Get dashboard data
    print(json.dumps(monitor.get_dashboard_data(), indent=2))
```


### 4.9 Event Time Processing Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/core/event_time.py
"""
Event Time Processing for ResilienceAI
Handles out-of-order events and watermarks.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimestampedEvent:
    """Event with event timestamp."""
    event_timestamp: int  # Event time (when event occurred)
    processing_timestamp: int  # Processing time (when event was processed)
    data: Dict[str, Any]
    key: Optional[str] = None
    watermark: int = 0  # Associated watermark


class WatermarkStrategy:
    """Base class for watermark strategies."""
    
    def get_watermark(self, event: TimestampedEvent, 
                      current_watermark: int) -> int:
        """Calculate new watermark based on event."""
        raise NotImplementedError


class BoundedOutOfOrdernessStrategy(WatermarkStrategy):
    """
    Watermark strategy with bounded out-of-orderness.
    Allows events to be late by up to max_out_of_orderness_ms.
    """
    
    def __init__(self, max_out_of_orderness_ms: int = 5000):
        self.max_out_of_orderness_ms = max_out_of_orderness_ms
        self.max_seen_timestamp = 0
    
    def get_watermark(self, event: TimestampedEvent, 
                      current_watermark: int) -> int:
        """Calculate watermark with bounded out-of-orderness."""
        self.max_seen_timestamp = max(self.max_seen_timestamp, 
                                       event.event_timestamp)
        return self.max_seen_timestamp - self.max_out_of_orderness_ms


class MonotonousWatermarkStrategy(WatermarkStrategy):
    """
    Simple monotonous watermark strategy.
    Watermark is always the maximum seen timestamp.
    """
    
    def get_watermark(self, event: TimestampedEvent, 
                      current_watermark: int) -> int:
        """Calculate monotonous watermark."""
        return max(current_watermark, event.event_timestamp)


class IdleTimeoutStrategy(WatermarkStrategy):
    """
    Watermark strategy with idle timeout.
    Advances watermark when no events received for timeout period.
    """
    
    def __init__(self, base_strategy: WatermarkStrategy,
                 idle_timeout_ms: int = 30000):
        self.base_strategy = base_strategy
        self.idle_timeout_ms = idle_timeout_ms
        self.last_event_time = 0
    
    def get_watermark(self, event: TimestampedEvent, 
                      current_watermark: int) -> int:
        """Calculate watermark with idle timeout."""
        self.last_event_time = time.time() * 1000
        return self.base_strategy.get_watermark(event, current_watermark)
    
    def get_idle_watermark(self, current_watermark: int) -> int:
        """Get watermark when idle."""
        idle_time = time.time() * 1000 - self.last_event_time
        if idle_time > self.idle_timeout_ms:
            return int(time.time() * 1000)
        return current_watermark


class WatermarkEmitter:
    """
    Emits watermarks periodically.
    """
    
    def __init__(self, emit_interval_ms: int = 200):
        self.emit_interval_ms = emit_interval_ms
        self.current_watermark = 0
        self.watermark_callbacks: List[Callable[[int], None]] = []
        self._lock = threading.Lock()
        self._running = False
        self._emitter_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start watermark emission."""
        self._running = True
        
        def emit_loop():
            while self._running:
                time.sleep(self.emit_interval_ms / 1000)
                with self._lock:
                    for callback in self.watermark_callbacks:
                        try:
                            callback(self.current_watermark)
                        except Exception as e:
                            logger.error(f"Error in watermark callback: {e}")
        
        self._emitter_thread = threading.Thread(target=emit_loop)
        self._emitter_thread.daemon = True
        self._emitter_thread.start()
    
    def stop(self):
        """Stop watermark emission."""
        self._running = False
        if self._emitter_thread:
            self._emitter_thread.join(timeout=5)
    
    def update_watermark(self, watermark: int):
        """Update current watermark."""
        with self._lock:
            if watermark > self.current_watermark:
                self.current_watermark = watermark
                logger.debug(f"Watermark updated to {watermark}")
    
    def on_watermark(self, callback: Callable[[int], None]):
        """Register watermark callback."""
        self.watermark_callbacks.append(callback)
    
    def get_current_watermark(self) -> int:
        """Get current watermark."""
        with self._lock:
            return self.current_watermark


class EventTimeBuffer:
    """
    Buffer for out-of-order events with event time processing.
    """
    
    def __init__(self, watermark_strategy: WatermarkStrategy,
                 max_buffer_size: int = 10000,
                 late_data_handler: Optional[Callable] = None):
        self.watermark_strategy = watermark_strategy
        self.max_buffer_size = max_buffer_size
        self.late_data_handler = late_data_handler
        self.buffer: deque = deque()
        self.watermark_emitter = WatermarkEmitter()
        self._lock = threading.Lock()
        self.process_callbacks: List[Callable[[TimestampedEvent], None]] = []
    
    def start(self):
        """Start event time processing."""
        self.watermark_emitter.start()
        self.watermark_emitter.on_watermark(self._on_watermark)
    
    def stop(self):
        """Stop event time processing."""
        self.watermark_emitter.stop()
    
    def add_event(self, event: TimestampedEvent):
        """
        Add event to buffer.
        
        Events are sorted by event timestamp.
        Late events (below watermark) are handled separately.
        """
        with self._lock:
            current_watermark = self.watermark_emitter.get_current_watermark()
            
            # Check if event is late
            if event.event_timestamp < current_watermark:
                if self.late_data_handler:
                    self.late_data_handler(event)
                else:
                    logger.debug(f"Dropping late event: {event.event_timestamp}")
                return
            
            # Add to buffer in sorted order
            inserted = False
            for i, existing in enumerate(self.buffer):
                if event.event_timestamp < existing.event_timestamp:
                    self.buffer.insert(i, event)
                    inserted = True
                    break
            
            if not inserted:
                self.buffer.append(event)
            
            # Trim buffer if too large
            while len(self.buffer) > self.max_buffer_size:
                removed = self.buffer.pop()
                logger.warning(f"Buffer full, dropped event: {removed.event_timestamp}")
            
            # Update watermark
            new_watermark = self.watermark_strategy.get_watermark(
                event, current_watermark
            )
            self.watermark_emitter.update_watermark(new_watermark)
    
    def _on_watermark(self, watermark: int):
        """Process events when watermark advances."""
        with self._lock:
            # Process all events below watermark
            events_to_process = []
            remaining = []
            
            for event in self.buffer:
                if event.event_timestamp <= watermark:
                    events_to_process.append(event)
                else:
                    remaining.append(event)
            
            self.buffer = deque(remaining)
        
        # Process events outside lock
        for event in events_to_process:
            for callback in self.process_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
    
    def on_process(self, callback: Callable[[TimestampedEvent], None]):
        """Register process callback."""
        self.process_callbacks.append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        with self._lock:
            if not self.buffer:
                return {
                    'buffer_size': 0,
                    'watermark': self.watermark_emitter.get_current_watermark(),
                    'min_event_time': None,
                    'max_event_time': None
                }
            
            return {
                'buffer_size': len(self.buffer),
                'watermark': self.watermark_emitter.get_current_watermark(),
                'min_event_time': self.buffer[0].event_timestamp,
                'max_event_time': self.buffer[-1].event_timestamp
            }


class EventTimeWindowProcessor:
    """
    Window processor with event time semantics.
    """
    
    def __init__(self, window_size_ms: int,
                 watermark_strategy: WatermarkStrategy,
                 allowed_lateness_ms: int = 0):
        self.window_size_ms = window_size_ms
        self.watermark_strategy = watermark_strategy
        self.allowed_lateness_ms = allowed_lateness_ms
        self.windows: Dict[str, Dict[int, List[TimestampedEvent]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.completed_windows: Dict[str, Dict[int, List[TimestampedEvent]]] = defaultdict(dict)
        self.watermark = 0
        self.window_callbacks: List[Callable] = []
        self._lock = threading.Lock()
    
    def get_window_start(self, timestamp: int) -> int:
        """Get window start for timestamp."""
        return (timestamp // self.window_size_ms) * self.window_size_ms
    
    def process_event(self, event: TimestampedEvent):
        """Process event into appropriate window."""
        with self._lock:
            window_start = self.get_window_start(event.event_timestamp)
            key = event.key or "default"
            
            # Check if window already completed
            if window_start in self.completed_windows.get(key, {}):
                if self.allowed_lateness_ms > 0:
                    if event.event_timestamp <= window_start + self.window_size_ms + self.allowed_lateness_ms:
                        # Late but allowed
                        self.windows[key][window_start].append(event)
                        logger.debug(f"Added late event to window {window_start}")
                else:
                    logger.debug(f"Dropping event for completed window {window_start}")
                return
            
            # Add to window
            self.windows[key][window_start].append(event)
            
            # Update watermark
            self.watermark = self.watermark_strategy.get_watermark(event, self.watermark)
            
            # Check for completed windows
            self._check_completed_windows(key)
    
    def _check_completed_windows(self, key: str):
        """Check and emit completed windows."""
        completed = []
        
        for window_start in list(self.windows[key].keys()):
            window_end = window_start + self.window_size_ms
            
            # Window is complete if watermark has passed window end + lateness
            if self.watermark >= window_end + self.allowed_lateness_ms:
                events = self.windows[key][window_start]
                completed.append((key, window_start, events))
                
                # Move to completed
                self.completed_windows[key][window_start] = events
                del self.windows[key][window_start]
        
        # Emit completed windows
        for key, window_start, events in completed:
            result = {
                'key': key,
                'window_start': window_start,
                'window_end': window_start + self.window_size_ms,
                'events': events,
                'event_count': len(events),
                'watermark': self.watermark
            }
            
            for callback in self.window_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    logger.error(f"Error in window callback: {e}")
    
    def on_window_complete(self, callback: Callable):
        """Register window completion callback."""
        self.window_callbacks.append(callback)
    
    def get_pending_windows(self) -> Dict[str, Any]:
        """Get pending (incomplete) windows."""
        with self._lock:
            pending = {}
            for key, windows in self.windows.items():
                pending[key] = {
                    window_start: len(events)
                    for window_start, events in windows.items()
                }
            return pending
    
    def force_emit(self, key: str, window_start: int):
        """Force emit a window (for cleanup)."""
        with self._lock:
            if key in self.windows and window_start in self.windows[key]:
                events = self.windows[key][window_start]
                result = {
                    'key': key,
                    'window_start': window_start,
                    'window_end': window_start + self.window_size_ms,
                    'events': events,
                    'event_count': len(events),
                    'watermark': self.watermark,
                    'forced': True
                }
                
                self.completed_windows[key][window_start] = events
                del self.windows[key][window_start]
                
                for callback in self.window_callbacks:
                    try:
                        callback(result)
                    except Exception as e:
                        logger.error(f"Error in forced window callback: {e}")


# Example usage
if __name__ == "__main__":
    # Create watermark strategy
    watermark_strategy = BoundedOutOfOrdernessStrategy(max_out_of_orderness_ms=5000)
    
    # Create event time buffer
    buffer = EventTimeBuffer(watermark_strategy, max_buffer_size=1000)
    
    # Add process handler
    def on_process(event):
        print(f"Processing event at {event.event_timestamp}")
    
    buffer.on_process(on_process)
    
    # Start processing
    buffer.start()
    
    # Add events (simulating out-of-order)
    current_time = int(time.time() * 1000)
    
    events = [
        TimestampedEvent(current_time + 3000, current_time, {"value": 1}),
        TimestampedEvent(current_time + 1000, current_time, {"value": 2}),
        TimestampedEvent(current_time + 5000, current_time, {"value": 3}),
        TimestampedEvent(current_time + 2000, current_time, {"value": 4}),  # Out of order
    ]
    
    for event in events:
        buffer.add_event(event)
        time.sleep(0.1)
    
    # Get stats
    print(f"Buffer stats: {buffer.get_stats()}")
    
    # Stop
    time.sleep(1)
    buffer.stop()
```


---

## 5. Complete Pipeline Examples

### 5.1 Sensor Data Processing Pipeline

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/pipelines/sensor_pipeline.py
"""
Sensor Data Processing Pipeline for ResilienceAI
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from confluent_kafka import Consumer, Producer, KafkaError
import redis

from ..core.kafka_streams_app import KafkaStreamsApp, StreamRecord
from ..core.windowing import TumblingWindowProcessor, WindowAggregator
from ..core.exactly_once import ExactlyOnceProcessor
from ..monitoring.stream_monitor import MetricsCollector

logger = logging.getLogger(__name__)


class SensorDataPipeline:
    """
    Complete pipeline for processing IoT sensor data.
    
    Flow:
    raw.iot.sensors -> Enrich -> Validate -> Window (1min) -> Aggregate -> Store
    """
    
    def __init__(self, kafka_config: Dict[str, str], redis_client: redis.Redis):
        self.kafka_config = kafka_config
        self.redis = redis_client
        self.metrics = MetricsCollector()
        self.eos_processor: Optional[ExactlyOnceProcessor] = None
        self.window_processor: Optional[TumblingWindowProcessor] = None
        self._running = False
    
    def initialize(self):
        """Initialize pipeline components."""
        # Initialize exactly-once processor
        self.eos_processor = ExactlyOnceProcessor(
            app_id="sensor-pipeline",
            redis_client=self.redis
        )
        
        # Initialize window processor (1-minute tumbling windows)
        self.window_processor = TumblingWindowProcessor(
            window_size_ms=60000,
            grace_period_ms=5000,
            late_data_handling='include'
        )
        
        # Set up window emission handler
        self.window_processor.on_emit(self._on_window_emit)
        
        # Initialize Kafka consumer
        consumer_config = {
            'bootstrap.servers': self.kafka_config['bootstrap.servers'],
            'group.id': 'sensor-processor',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
            'isolation.level': 'read_committed',
        }
        self.consumer = Consumer(consumer_config)
        self.consumer.subscribe(['raw.iot.sensors'])
        
        # Initialize Kafka producer
        producer_config = {
            'bootstrap.servers': self.kafka_config['bootstrap.servers'],
            'acks': 'all',
            'enable.idempotence': True,
            'compression.type': 'lz4',
        }
        self.producer = Producer(producer_config)
        
        logger.info("Sensor pipeline initialized")
    
    def _enrich_sensor_data(self, record: StreamRecord) -> StreamRecord:
        """Enrich sensor data with metadata."""
        value = record.value.copy()
        
        # Add processing timestamp
        value['processed_at'] = int(datetime.now().timestamp() * 1000)
        
        # Add sensor location from cache
        sensor_id = value.get('sensor_id')
        if sensor_id:
            location = self.redis.hget(f"sensor:{sensor_id}", "location")
            if location:
                value['location'] = location.decode()
        
        # Calculate derived metrics
        if 'temperature' in value and 'humidity' in value:
            # Heat index calculation
            temp = value['temperature']
            humidity = value['humidity']
            value['heat_index'] = self._calculate_heat_index(temp, humidity)
        
        return StreamRecord(
            key=record.key,
            value=value,
            timestamp=record.timestamp,
            topic=record.topic,
            partition=record.partition,
            offset=record.offset,
            headers=record.headers
        )
    
    def _calculate_heat_index(self, temp: float, humidity: float) -> float:
        """Calculate heat index from temperature and humidity."""
        # Simplified heat index formula
        return temp + 0.5555 * (6.11 * (humidity / 100) ** 0.5 - 10)
    
    def _validate_sensor_data(self, record: StreamRecord) -> bool:
        """Validate sensor data."""
        value = record.value
        
        # Check required fields
        if 'sensor_id' not in value or 'timestamp' not in value:
            return False
        
        # Check value ranges
        if 'temperature' in value:
            if not -50 <= value['temperature'] <= 100:
                return False
        
        if 'humidity' in value:
            if not 0 <= value['humidity'] <= 100:
                return False
        
        return True
    
    def _on_window_emit(self, window_result):
        """Handle window emission."""
        logger.info(f"Window emitted: {window_result.key} "
                   f"[{window_result.window_start} - {window_result.window_end}] "
                   f"({window_result.record_count} records)")
        
        # Produce aggregated results
        output = {
            'sensor_id': window_result.key,
            'window_start': window_result.window_start,
            'window_end': window_result.window_end,
            'record_count': window_result.record_count,
            'aggregations': window_result.value,
            'emitted_at': int(datetime.now().timestamp() * 1000)
        }
        
        self.producer.produce(
            topic='aggregated.sensor.1min',
            key=window_result.key,
            value=json.dumps(output).encode('utf-8')
        )
        
        self.producer.poll(0)  # Non-blocking flush
    
    def _process_record(self, msg) -> bool:
        """Process a single record with exactly-once semantics."""
        record = StreamRecord.from_kafka_message(msg)
        
        # Generate transaction ID
        transaction_id = f"{msg.topic()}:{msg.partition()}:{msg.offset()}"
        
        def processor(value: Dict) -> list:
            # Enrich
            enriched = self._enrich_sensor_data(record)
            
            # Validate
            if not self._validate_sensor_data(enriched):
                logger.warning(f"Invalid record: {record.key}")
                return []
            
            # Extract sensor ID for windowing
            sensor_id = enriched.value.get('sensor_id', 'unknown')
            event_timestamp = enriched.value.get('timestamp', record.timestamp)
            
            # Add to window processor
            self.window_processor.process_record(
                key=sensor_id,
                value=enriched.value,
                event_timestamp=event_timestamp
            )
            
            # Produce enriched data
            return [(
                'processed.sensor.enriched',
                sensor_id,
                enriched.value
            )]
        
        return self.eos_processor.process_with_eos(
            transaction_id=transaction_id,
            topic=msg.topic(),
            partition=msg.partition(),
            offset=msg.offset(),
            value=record.value,
            processor=processor
        )
    
    def run(self):
        """Run the pipeline."""
        self._running = True
        self.window_processor.start()
        
        logger.info("Sensor pipeline started")
        
        try:
            while self._running:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug(f"End of partition: {msg.topic()}[{msg.partition()}]")
                    else:
                        logger.error(f"Error: {msg.error()}")
                    continue
                
                # Process record
                start_time = datetime.now().timestamp()
                
                try:
                    success = self._process_record(msg)
                    if success:
                        self.metrics.record_message_in('sensor_pipeline')
                        self.consumer.commit(msg)
                except Exception as e:
                    logger.error(f"Error processing record: {e}")
                    self.metrics.record_error('sensor_pipeline')
                
                processing_time = (datetime.now().timestamp() - start_time) * 1000
                self.metrics.record_processing_time('sensor_pipeline', processing_time)
        
        except KeyboardInterrupt:
            logger.info("Pipeline interrupted")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the pipeline."""
        self._running = False
        self.window_processor.stop()
        self.consumer.close()
        self.producer.flush()
        logger.info("Sensor pipeline stopped")


# Pipeline configuration
SENSOR_PIPELINE_CONFIG = {
    'input_topic': 'raw.iot.sensors',
    'output_topic': 'processed.sensor.enriched',
    'aggregation_topic': 'aggregated.sensor.1min',
    'window_size_minutes': 1,
    'grace_period_seconds': 5,
    'allowed_lateness_seconds': 30,
    'enable_exactly_once': True,
    'metrics_enabled': True,
}
```

### 5.2 Anomaly Detection Pipeline

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/pipelines/anomaly_pipeline.py
"""
Anomaly Detection Pipeline for ResilienceAI
"""

import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from collections import deque
from datetime import datetime

from confluent_kafka import Consumer, Producer
import redis

from ..core.cep_engine import CEPEngine, ResiliencePatterns, Event, MatchResult
from ..monitoring.stream_monitor import MetricsCollector

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Real-time anomaly detection using statistical methods.
    """
    
    def __init__(self, window_size: int = 100, threshold_sigma: float = 3.0):
        self.window_size = window_size
        self.threshold_sigma = threshold_sigma
        self.values: deque = deque(maxlen=window_size)
        self.mean = 0.0
        self.std = 0.0
    
    def update(self, value: float) -> Dict[str, Any]:
        """Update detector with new value and check for anomaly."""
        self.values.append(value)
        
        if len(self.values) < 10:
            return {'is_anomaly': False, 'reason': 'insufficient_data'}
        
        # Calculate statistics
        self.mean = np.mean(self.values)
        self.std = np.std(self.values)
        
        if self.std == 0:
            return {'is_anomaly': False, 'reason': 'no_variance'}
        
        # Check for anomaly
        z_score = abs(value - self.mean) / self.std
        is_anomaly = z_score > self.threshold_sigma
        
        return {
            'is_anomaly': is_anomaly,
            'z_score': z_score,
            'mean': self.mean,
            'std': self.std,
            'threshold': self.threshold_sigma,
            'value': value
        }


class AnomalyDetectionPipeline:
    """
    Complete anomaly detection pipeline.
    
    Combines statistical anomaly detection with CEP for pattern matching.
    """
    
    def __init__(self, kafka_config: Dict[str, str], redis_client: redis.Redis):
        self.kafka_config = kafka_config
        self.redis = redis_client
        self.metrics = MetricsCollector()
        self.cep_engine = CEPEngine()
        self.detectors: Dict[str, AnomalyDetector] = {}
        self._running = False
    
    def initialize(self):
        """Initialize pipeline components."""
        # Initialize CEP engine with patterns
        self._register_cep_patterns()
        
        # Initialize anomaly detectors for each metric
        self.detectors = {
            'cpu_usage': AnomalyDetector(window_size=100, threshold_sigma=3.0),
            'memory_usage': AnomalyDetector(window_size=100, threshold_sigma=3.0),
            'response_time': AnomalyDetector(window_size=100, threshold_sigma=3.0),
            'error_rate': AnomalyDetector(window_size=100, threshold_sigma=2.5),
        }
        
        # Initialize Kafka consumer
        consumer_config = {
            'bootstrap.servers': self.kafka_config['bootstrap.servers'],
            'group.id': 'anomaly-detector',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        }
        self.consumer = Consumer(consumer_config)
        self.consumer.subscribe(['processed.metrics.normalized'])
        
        # Initialize Kafka producer
        producer_config = {
            'bootstrap.servers': self.kafka_config['bootstrap.servers'],
            'acks': 'all',
            'enable.idempotence': True,
        }
        self.producer = Producer(producer_config)
        
        logger.info("Anomaly detection pipeline initialized")
    
    def _register_cep_patterns(self):
        """Register CEP patterns for anomaly detection."""
        # Failure cascade pattern
        self.cep_engine.register_pattern(
            ResiliencePatterns.failure_cascade_pattern()
        )
        
        # Threshold breach pattern for CPU
        self.cep_engine.register_pattern(
            ResiliencePatterns.threshold_breach_pattern('cpu_usage', 90.0)
        )
        
        # Anomaly spike pattern
        self.cep_engine.register_pattern(
            ResiliencePatterns.anomaly_spike_pattern()
        )
        
        # Add CEP match handler
        self.cep_engine.on_match(self._on_cep_match)
    
    def _on_cep_match(self, result: MatchResult):
        """Handle CEP pattern match."""
        logger.warning(f"CEP Pattern matched: {result.pattern_name}")
        
        # Produce CEP event
        event = {
            'pattern_name': result.pattern_name,
            'match_id': result.match_id,
            'match_start': result.match_start,
            'match_end': result.match_end,
            'event_count': len(result.events),
            'events': [
                {
                    'event_type': e.event_type,
                    'timestamp': e.timestamp,
                    'data': e.data
                }
                for e in result.events
            ],
            'detected_at': int(datetime.now().timestamp() * 1000)
        }
        
        self.producer.produce(
            topic='events.pattern.matched',
            key=result.pattern_name,
            value=json.dumps(event).encode('utf-8')
        )
    
    def _detect_anomaly(self, metric_name: str, value: float) -> Optional[Dict]:
        """Detect anomaly for a metric."""
        if metric_name not in self.detectors:
            return None
        
        result = self.detectors[metric_name].update(value)
        
        if result['is_anomaly']:
            return {
                'metric': metric_name,
                'value': value,
                'z_score': result['z_score'],
                'mean': result['mean'],
                'std': result['std'],
                'severity': 'critical' if result['z_score'] > 4 else 'warning'
            }
        
        return None
    
    def _process_record(self, record: Dict[str, Any]):
        """Process a single record."""
        service_id = record.get('service_id', 'unknown')
        timestamp = record.get('timestamp', int(datetime.now().timestamp() * 1000))
        
        # Check each metric for anomalies
        anomalies = []
        for metric_name in self.detectors.keys():
            if metric_name in record:
                anomaly = self._detect_anomaly(metric_name, float(record[metric_name]))
                if anomaly:
                    anomalies.append(anomaly)
        
        # Produce anomalies
        for anomaly in anomalies:
            anomaly_event = {
                'service_id': service_id,
                'timestamp': timestamp,
                'detected_at': int(datetime.now().timestamp() * 1000),
                **anomaly
            }
            
            self.producer.produce(
                topic='events.anomaly.detected',
                key=service_id,
                value=json.dumps(anomaly_event).encode('utf-8')
            )
            
            # Also send to CEP engine
            cep_event = Event(
                event_type='anomaly_detected',
                timestamp=timestamp,
                data=anomaly_event
            )
            self.cep_engine.process_event(cep_event)
            
            logger.warning(f"Anomaly detected: {anomaly['metric']} = {anomaly['value']} "
                          f"(z-score: {anomaly['z_score']:.2f})")
        
        # Send to CEP engine for pattern matching
        for metric_name, value in record.items():
            if isinstance(value, (int, float)):
                cep_event = Event(
                    event_type='metric_update',
                    timestamp=timestamp,
                    data={
                        'service_id': service_id,
                        'metric': metric_name,
                        'value': value
                    }
                )
                self.cep_engine.process_event(cep_event)
    
    def run(self):
        """Run the pipeline."""
        self._running = True
        logger.info("Anomaly detection pipeline started")
        
        try:
            while self._running:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    logger.error(f"Error: {msg.error()}")
                    continue
                
                try:
                    record = json.loads(msg.value().decode('utf-8'))
                    self._process_record(record)
                    self.metrics.record_message_in('anomaly_pipeline')
                    self.consumer.commit(msg)
                except Exception as e:
                    logger.error(f"Error processing record: {e}")
                    self.metrics.record_error('anomaly_pipeline')
        
        except KeyboardInterrupt:
            logger.info("Pipeline interrupted")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the pipeline."""
        self._running = False
        self.consumer.close()
        self.producer.flush()
        logger.info("Anomaly detection pipeline stopped")


# Pipeline configuration
ANOMALY_PIPELINE_CONFIG = {
    'input_topic': 'processed.metrics.normalized',
    'output_topic': 'events.anomaly.detected',
    'cep_output_topic': 'events.pattern.matched',
    'detection_methods': ['statistical', 'cep'],
    'threshold_sigma': 3.0,
    'window_size': 100,
}
```


---

## 6. Deployment Configuration

### 6.1 Docker Compose Configuration

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/docker-compose.yml
version: '3.8'

services:
  # Zookeeper for Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    hostname: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log

  # Kafka Broker
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "29092:29092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    volumes:
      - kafka-data:/var/lib/kafka/data

  # Kafka Schema Registry
  schema-registry:
    image: confluentinc/cp-schema-registry:7.5.0
    hostname: schema-registry
    depends_on:
      - kafka
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:29092
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081

  # Kafka Connect
  kafka-connect:
    image: confluentinc/cp-kafka-connect:7.5.0
    hostname: kafka-connect
    depends_on:
      - kafka
      - schema-registry
    ports:
      - "8083:8083"
    environment:
      CONNECT_BOOTSTRAP_SERVERS: kafka:29092
      CONNECT_REST_ADVERTISED_HOST_NAME: kafka-connect
      CONNECT_REST_PORT: 8083
      CONNECT_GROUP_ID: compose-connect-group
      CONNECT_CONFIG_STORAGE_TOPIC: docker-connect-configs
      CONNECT_OFFSET_STORAGE_TOPIC: docker-connect-offsets
      CONNECT_STATUS_STORAGE_TOPIC: docker-connect-status
      CONNECT_CONFIG_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_OFFSET_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_STATUS_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_KEY_CONVERTER: org.apache.kafka.connect.storage.StringConverter
      CONNECT_VALUE_CONVERTER: io.confluent.connect.avro.AvroConverter
      CONNECT_VALUE_CONVERTER_SCHEMA_REGISTRY_URL: http://schema-registry:8081
      CONNECT_PLUGIN_PATH: /usr/share/java

  # Kafka UI
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8080:8080"
    depends_on:
      - kafka
      - schema-registry
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
      KAFKA_CLUSTERS_0_SCHEMAREGISTRY: http://schema-registry:8081

  # Redis
  redis:
    image: redis:7-alpine
    hostname: redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru

  # Redis Insight (UI)
  redis-insight:
    image: redis/redisinsight:latest
    ports:
      - "5540:5540"
    depends_on:
      - redis
    volumes:
      - redis-insight-data:/db

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin

  # Sensor Pipeline
  sensor-pipeline:
    build:
      context: .
      dockerfile: Dockerfile.pipeline
    depends_on:
      - kafka
      - redis
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      REDIS_HOST: redis
      REDIS_PORT: 6379
      PIPELINE_TYPE: sensor
    deploy:
      replicas: 2
    restart: unless-stopped

  # Anomaly Pipeline
  anomaly-pipeline:
    build:
      context: .
      dockerfile: Dockerfile.pipeline
    depends_on:
      - kafka
      - redis
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      REDIS_HOST: redis
      REDIS_PORT: 6379
      PIPELINE_TYPE: anomaly
    deploy:
      replicas: 2
    restart: unless-stopped

  # Aggregation Pipeline
  aggregation-pipeline:
    build:
      context: .
      dockerfile: Dockerfile.pipeline
    depends_on:
      - kafka
      - redis
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      REDIS_HOST: redis
      REDIS_PORT: 6379
      PIPELINE_TYPE: aggregation
    deploy:
      replicas: 2
    restart: unless-stopped

volumes:
  zookeeper-data:
  zookeeper-logs:
  kafka-data:
  redis-data:
  redis-insight-data:
  prometheus-data:
  grafana-data:
```

### 6.2 Kubernetes Deployment

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/k8s/kafka-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
  namespace: resilience-ai
spec:
  serviceName: kafka-headless
  replicas: 3
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
      - name: kafka
        image: confluentinc/cp-kafka:7.5.0
        ports:
        - containerPort: 9092
          name: internal
        - containerPort: 9093
          name: external
        env:
        - name: KAFKA_BROKER_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: KAFKA_ZOOKEEPER_CONNECT
          value: "zookeeper:2181"
        - name: KAFKA_LISTENERS
          value: "INTERNAL://:9092,EXTERNAL://:9093"
        - name: KAFKA_ADVERTISED_LISTENERS
          value: "INTERNAL://$(POD_NAME).kafka-headless:9092,EXTERNAL://$(NODE_IP):$(NODE_PORT)"
        - name: KAFKA_LISTENER_SECURITY_PROTOCOL_MAP
          value: "INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT"
        - name: KAFKA_INTER_BROKER_LISTENER_NAME
          value: "INTERNAL"
        - name: KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR
          value: "3"
        - name: KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR
          value: "3"
        - name: KAFKA_TRANSACTION_STATE_LOG_MIN_ISR
          value: "2"
        - name: KAFKA_DEFAULT_REPLICATION_FACTOR
          value: "3"
        - name: KAFKA_MIN_INSYNC_REPLICAS
          value: "2"
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: NODE_IP
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: NODE_PORT
          value: "30092"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: kafka-data
          mountPath: /var/lib/kafka/data
  volumeClaimTemplates:
  - metadata:
      name: kafka-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: kafka-headless
  namespace: resilience-ai
spec:
  clusterIP: None
  selector:
    app: kafka
  ports:
  - port: 9092
    name: internal
---
apiVersion: v1
kind: Service
metadata:
  name: kafka-external
  namespace: resilience-ai
spec:
  type: NodePort
  selector:
    app: kafka
  ports:
  - port: 9093
    targetPort: 9093
    nodePort: 30092
    name: external
```

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/k8s/pipeline-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sensor-pipeline
  namespace: resilience-ai
  labels:
    app: sensor-pipeline
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sensor-pipeline
  template:
    metadata:
      labels:
        app: sensor-pipeline
    spec:
      containers:
      - name: pipeline
        image: resilience-ai/sensor-pipeline:latest
        ports:
        - containerPort: 8080
          name: metrics
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka-headless:9092"
        - name: REDIS_HOST
          value: "redis"
        - name: REDIS_PORT
          value: "6379"
        - name: PIPELINE_TYPE
          value: "sensor"
        - name: CONSUMER_GROUP
          value: "sensor-processor"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
      volumes:
      - name: config
        configMap:
          name: pipeline-config
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sensor-pipeline-hpa
  namespace: resilience-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sensor-pipeline
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### 6.3 Prometheus Configuration

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Kafka metrics
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka:9090']
    metrics_path: /metrics

  # Kafka JMX Exporter
  - job_name: 'kafka-jmx'
    static_configs:
      - targets: ['kafka:7071']

  # Kafka Connect
  - job_name: 'kafka-connect'
    static_configs:
      - targets: ['kafka-connect:8083']
    metrics_path: /

  # Pipeline metrics
  - job_name: 'sensor-pipeline'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - resilience-ai
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: sensor-pipeline
      - source_labels: [__meta_kubernetes_pod_container_port_name]
        action: keep
        regex: metrics
      - source_labels: [__meta_kubernetes_pod_ip]
        action: replace
        target_label: __address__
        regex: (.+)
        replacement: ${1}:8080

  # Redis metrics
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']

  # Node exporter
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

---

## 7. Integration Points

### 7.1 API Integration

```python
# /mnt/okcomputer/output/resilience_ai_analysis/stream_processing/api/stream_api.py
"""
Stream Processing API for ResilienceAI
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, List
import asyncio
import json
from datetime import datetime

app = FastAPI(title="ResilienceAI Stream API")

# In-memory state (replace with Redis in production)
active_streams: Dict[str, Any] = {}
connected_websockets: List[WebSocket] = []


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_streams": len(active_streams),
        "websocket_connections": len(connected_websockets)
    }


@app.get("/streams")
async def list_streams():
    """List all active streams."""
    return {
        "streams": [
            {
                "name": name,
                "status": info.get("status"),
                "started_at": info.get("started_at")
            }
            for name, info in active_streams.items()
        ]
    }


@app.get("/streams/{stream_name}/metrics")
async def get_stream_metrics(stream_name: str):
    """Get metrics for a specific stream."""
    if stream_name not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    return active_streams[stream_name].get("metrics", {})


@app.post("/streams/{stream_name}/start")
async def start_stream(stream_name: str, config: Dict[str, Any]):
    """Start a new stream."""
    if stream_name in active_streams:
        raise HTTPException(status_code=409, detail="Stream already exists")
    
    active_streams[stream_name] = {
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "config": config,
        "metrics": {}
    }
    
    return {"message": f"Stream {stream_name} started"}


@app.post("/streams/{stream_name}/stop")
async def stop_stream(stream_name: str):
    """Stop a stream."""
    if stream_name not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    active_streams[stream_name]["status"] = "stopped"
    
    return {"message": f"Stream {stream_name} stopped"}


@app.websocket("/ws/stream/{stream_name}")
async def websocket_stream(websocket: WebSocket, stream_name: str):
    """WebSocket endpoint for real-time stream data."""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process message (example: echo back)
            response = {
                "stream": stream_name,
                "received": message,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_json(response)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connected_websockets.remove(websocket)


@app.get("/events/stream")
async def event_stream():
    """Server-Sent Events endpoint."""
    async def generate_events():
        while True:
            event = {
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat(),
                "data": {"status": "active"}
            }
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(5)
    
    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream"
    )


@app.get("/topics")
async def list_topics():
    """List Kafka topics."""
    # This would integrate with Kafka AdminClient
    return {
        "topics": [
            "raw.iot.sensors",
            "raw.system.metrics",
            "processed.sensor.enriched",
            "aggregated.metrics.1min",
            "alerts.critical"
        ]
    }


@app.get("/consumer-groups")
async def list_consumer_groups():
    """List Kafka consumer groups."""
    return {
        "consumer_groups": [
            {
                "group_id": "sensor-processor",
                "state": "Stable",
                "members": 3
            },
            {
                "group_id": "metrics-aggregator",
                "state": "Stable",
                "members": 2
            }
        ]
    }


@app.get("/consumer-groups/{group_id}/lag")
async def get_consumer_lag(group_id: str):
    """Get consumer lag for a group."""
    # This would integrate with Kafka consumer
    return {
        "group_id": group_id,
        "lag": {
            "raw.iot.sensors": {
                "0": {"current_offset": 1000, "end_offset": 1500, "lag": 500},
                "1": {"current_offset": 2000, "end_offset": 2200, "lag": 200}
            }
        }
    }
```

---

## 8. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
1. **Kafka Infrastructure Setup**
   - Deploy Kafka cluster (3 brokers)
   - Configure topics with proper partitioning
   - Set up Schema Registry

2. **Basic Stream Processing**
   - Implement Kafka consumer/producer
   - Create simple filter/map operations
   - Set up Redis for caching

3. **Monitoring Foundation**
   - Deploy Prometheus and Grafana
   - Basic metrics collection
   - Health check endpoints

### Phase 2: Core Processing (Weeks 3-4)
1. **Windowing Implementation**
   - Tumbling windows
   - Sliding windows
   - Session windows

2. **Stream Joins**
   - Stream-Stream joins
   - Stream-Table joins
   - KTable operations

3. **Exactly-Once Semantics**
   - Transaction management
   - Deduplication
   - Checkpointing

### Phase 3: Advanced Features (Weeks 5-6)
1. **Complex Event Processing**
   - Pattern matching
   - Temporal reasoning
   - CEP engine integration

2. **Event Time Processing**
   - Watermark strategies
   - Out-of-order handling
   - Late data management

3. **Backpressure Handling**
   - Adaptive rate limiting
   - Queue management
   - Circuit breakers

### Phase 4: Production Hardening (Weeks 7-8)
1. **Scalability**
   - Horizontal pod autoscaling
   - Partition rebalancing
   - Performance optimization

2. **Reliability**
   - Dead letter queues
   - Retry mechanisms
   - Failure recovery

3. **Observability**
   - Distributed tracing
   - Advanced alerting
   - Dashboard creation

---

## 9. Summary

This document provides a comprehensive stream processing architecture for ResilienceAI, including:

### Key Components Implemented:
1. **Kafka Streams Core** - Full DSL implementation with filter, map, join operations
2. **Windowing Operations** - Tumbling, sliding, and session windows with event time
3. **Stream Joins** - Stream-Stream, Stream-Table, and Table-Table joins
4. **Exactly-Once Semantics** - Transaction management and deduplication
5. **Backpressure Handling** - Adaptive rate limiting and circuit breakers
6. **Complex Event Processing** - Pattern matching and temporal reasoning
7. **Redis Streams Integration** - High-speed caching and state management
8. **Stream Monitoring** - Metrics collection, health checks, and alerting
9. **Event Time Processing** - Watermark strategies and out-of-order handling

### File Structure:
```
/mnt/okcomputer/output/resilience_ai_analysis/stream_processing/
├── config/
│   ├── topics.py              # Kafka topic configurations
│   └── consumer_groups.py     # Consumer group configurations
├── core/
│   ├── kafka_streams_app.py   # Kafka Streams DSL implementation
│   ├── windowing.py           # Windowing operations
│   ├── stream_joins.py        # Stream join operations
│   ├── exactly_once.py        # Exactly-once semantics
│   ├── backpressure.py        # Backpressure handling
│   ├── cep_engine.py          # Complex event processing
│   ├── redis_streams.py       # Redis Streams integration
│   └── event_time.py          # Event time processing
├── pipelines/
│   ├── sensor_pipeline.py     # Sensor data pipeline
│   └── anomaly_pipeline.py    # Anomaly detection pipeline
├── monitoring/
│   └── stream_monitor.py      # Stream monitoring
├── api/
│   └── stream_api.py          # REST API
├── docker-compose.yml         # Docker deployment
├── k8s/                       # Kubernetes manifests
└── monitoring/                # Prometheus/Grafana configs
```

### Next Steps:
1. Deploy Kafka and Redis infrastructure
2. Implement core stream processing pipelines
3. Set up monitoring and alerting
4. Test with production-like load
5. Optimize for performance and reliability
