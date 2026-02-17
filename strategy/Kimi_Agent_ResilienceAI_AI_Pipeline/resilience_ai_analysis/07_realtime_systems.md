# ResilienceAI Real-Time Systems Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of ResilienceAI's current real-time capabilities and proposes a production-grade, AI-powered real-time event-driven architecture. The enhancements include WebSocket-based live updates, Kafka event streaming, complex event processing, ML-powered alert classification, and multi-channel notification systems.

---

## 1. Current State Analysis

### 1.1 Existing Real-Time Components

#### 1.1.1 Weather Client (`src/weather_client.py`)
```python
# Current capabilities:
- NOAA National Weather Service API integration
- WeatherAlert dataclass with severity mapping
- Rate-limited API requests (0.5s delay)
- SEVERITY_WEIGHTS: {'Extreme': 1.0, 'Severe': 0.8, 'Moderate': 0.5, 'Minor': 0.2}
- RELEVANT_EVENTS filter for disaster-related alerts
- Basic error handling and retry logic
```

**Strengths:**
- Clean dataclass-based alert representation
- Proper rate limiting for NOAA API
- Severity weight mapping for risk correlation

**Limitations:**
- Synchronous polling only
- No event streaming capability
- Limited alert correlation with vulnerability data
- No ML-based severity classification

#### 1.1.2 Alert Manager (`src/alert_manager.py`)
```python
# Current capabilities:
- SQLite-based subscription storage
- AlertSubscription dataclass with webhook/email/phone support
- AlertEvent tracking with status management
- Thread-safe operations with locking
- Basic CRUD operations for subscriptions
```

**Strengths:**
- Multi-channel notification support (webhook, email, SMS)
- Subscription-based alert filtering
- Event acknowledgment tracking

**Limitations:**
- SQLite not suitable for high-throughput real-time processing
- No message queue integration
- No event replay capability
- Limited scalability

#### 1.1.3 Real-Time Pipeline (`src/realtime_pipeline.py`)
```python
# Current capabilities:
- WebSocket server implementation (websockets library)
- DataEvent dataclass for event streaming
- Event subscription pattern with callbacks
- NOAA stream worker with 60-second polling
- Async WebSocket handler
```

**Strengths:**
- WebSocket support for live updates
- Async event handling
- Multi-source data integration (NOAA, FEMA, USGS)

**Limitations:**
- No message persistence
- No event replay or dead letter queue
- Limited fault tolerance
- No stream processing capabilities
- Missing circuit breaker pattern

### 1.2 Current Architecture Diagram

```
+-------------------------------------------------------------+
|                 CURRENT REAL-TIME ARCHITECTURE              |
+-------------------------------------------------------------+
|                                                             |
|  +------------+      +------------+      +------------+    |
|  |  NOAA API  |----->|weather_cli |----->|alert_manag |    |
|  +------------+      +------------+      |  (SQLite)  |    |
|       |                   |              +------------+    |
|       |                   |                     |          |
|       |                   v                     v          |
|       |            +------------+      +------------+      |
|       |            |realtime_pip|----->| WebSocket  |      |
|       |            |  (basic)   |      |  Server    |      |
|       |            +------------+      +------------+      |
|       |                   ^                     |          |
|       |                   |                     v          |
|       +-------------------+              +------------+    |
|                                          | Dashboard  |    |
|                                          |(Streamlit) |    |
|                                          +------------+    |
+-------------------------------------------------------------+
```

---

## 2. Proposed Event-Driven Architecture

### 2.1 Enhanced Architecture Overview

```
+------------------------------------------------------------------------+
|              PROPOSED REAL-TIME EVENT-DRIVEN ARCHITECTURE              |
+------------------------------------------------------------------------+
|                                                                        |
|  +---------------------------------------------------------------+   |
|  |                      DATA SOURCE LAYER                         |   |
|  |  +--------+ +--------+ +--------+ +--------+ +--------+       |   |
|  |  |NOAA NWS| |FEMA API| |USGS EQ | |NASA    | |IoT     |       |   |
|  |  +---+----+ +---+----+ +---+----+ +---+----+ +---+----+       |   |
|  +------+----------+----------+----------+----------+-------------+   |
|         |          |          |          |          |                |
|         v          v          v          v          v                |
|  +---------------------------------------------------------------+   |
|  |                   INGESTION LAYER (Kafka Connect)              |   |
|  |  +------------+ +------------+ +------------+ +------------+  |   |
|  |  |NOAA Source | |FEMA Source | |USGS Source | |Custom      |  |   |
|  |  | Connector  | | Connector  | | Connector  | | Connectors  |  |   |
|  |  +------+-----+ +------+-----+ +------+-----+ +------+-----+  |   |
|  +--------+-------------+-------------+-------------+-------------+   |
|           |             |             |             |                |
|           v             v             v             v                |
|  +---------------------------------------------------------------+   |
|  |                   MESSAGE BROKER LAYER (Kafka)                 |   |
|  |  +-----------+ +-----------+ +-----------+ +-----------+      |   |
|  |  |raw.weather| |raw.disast | |raw.seismic| |raw.sensor |      |   |
|  |  |  .alerts  | |.declaratns| |  .events  | |  .data    |      |   |
|  |  +-----+-----+ +-----+-----+ +-----+-----+ +-----+-----+      |   |
|  |        |             |             |             |             |   |
|  |        v             v             v             v             |   |
|  |  +--------------------------------------------------------+   |   |
|  |  |           STREAM PROCESSING (Kafka Streams/Flink)      |   |   |
|  |  |  +------------+ +------------+ +------------+         |   |   |
|  |  |  |Alert       | |Risk        | |ML          |         |   |   |
|  |  |  |Enricher    | |Correlator  | |Classifier  |         |   |   |
|  |  |  +------+-----+ +------+-----+ +------+-----+         |   |   |
|  |  +---------+-------------+-------------+-----------------+   |   |
|  +------------+-------------+-------------+----------------------+   |
|               |             |             |                          |
|               v             v             v                          |
|  +---------------------------------------------------------------+   |
|  |                   EVENT PROCESSING LAYER                       |   |
|  |  +-----------+ +-----------+ +-----------+ +-----------+      |   |
|  |  |processed. | |processed. | |processed. | |processed. |      |   |
|  |  |alerts.high| |alerts.med | |alerts.low | |notificatns|      |   |
|  |  +-----+-----+ +-----+-----+ +-----+-----+ +-----+-----+      |   |
|  +--------+-----+-------+-----+-------+-----+-------+-------------+   |
|           |             |             |             |                |
|           v             v             v             v                |
|  +---------------------------------------------------------------+   |
|  |                   NOTIFICATION LAYER                           |   |
|  |  +--------+ +--------+ +--------+ +--------+ +--------+       |   |
|  |  |WebSockt| | Email  | |  SMS   | |Webhook | | Push   |       |   |
|  |  | Server | |Service | |Service | |Service | |Service |       |   |
|  |  +--------+ +--------+ +--------+ +--------+ +--------+       |   |
|  +---------------------------------------------------------------+   |
|                                                                        |
|  +---------------------------------------------------------------+   |
|  |                   STATE MANAGEMENT (Redis)                     |   |
|  |  +--------+ +--------+ +--------+ +--------+                  |   |
|  |  | Alert  | | Session| |  Rate  | | Cache  |                  |   |
|  |  | State  | | Store  | |Limiter | | Layer  |                  |   |
|  |  +--------+ +--------+ +--------+ +--------+                  |   |
|  +---------------------------------------------------------------+   |
+------------------------------------------------------------------------+
```

---

## 3. Technology Stack

### 3.1 Core Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Message Broker | Apache Kafka | Event streaming, persistence, replay |
| Stream Processing | Kafka Streams / Flink | Real-time event processing |
| State Management | Redis | Session state, caching, rate limiting |
| WebSocket Server | FastAPI + WebSockets | Live client connections |
| API Gateway | Kong / Envoy | Routing, rate limiting, auth |
| Monitoring | Prometheus + Grafana | Metrics and observability |
| Logging | ELK Stack | Centralized logging |
| Tracing | Jaeger | Distributed tracing |

### 3.2 Python Libraries

```txt
# requirements-realtime.txt

# Message Streaming
confluent-kafka>=2.3.0
kafka-python>=2.0.2
aiokafka>=0.9.0

# WebSocket & Async
websockets>=12.0
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-socketio>=5.11.0

# Redis
redis>=5.0.0
aioredis>=2.0.0

# Stream Processing
faust-streaming>=0.10.0

# Circuit Breaker
pybreaker>=1.2.0

# Notifications
twilio>=8.12.0
sendgrid>=6.11.0
firebase-admin>=6.3.0

# ML for Alert Classification
transformers>=4.36.0
torch>=2.1.0

# Monitoring
prometheus-client>=0.19.0
opentelemetry-api>=1.21.0

# Data Validation
pydantic>=2.5.0

# Async Utilities
aiohttp>=3.9.0
aiocron>=1.8.0
```

---

## 4. Implementation Components

### 4.1 Folder Structure

```
resilience-ai/
├── src/
│   ├── realtime/
│   │   ├── __init__.py
│   │   ├── config.py                    # Real-time configuration
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── events.py                # Event dataclasses
│   │   │   ├── alerts.py                # Alert models
│   │   │   └── subscriptions.py         # Subscription models
│   │   ├── kafka/
│   │   │   ├── __init__.py
│   │   │   ├── producer.py              # Kafka producer
│   │   │   ├── consumer.py              # Kafka consumer base
│   │   │   ├── streams.py               # Kafka Streams apps
│   │   │   └── admin.py                 # Topic management
│   │   ├── websocket/
│   │   │   ├── __init__.py
│   │   │   ├── server.py                # WebSocket server
│   │   │   ├── manager.py               # Connection manager
│   │   │   └── handlers.py              # Event handlers
│   │   ├── processing/
│   │   │   ├── __init__.py
│   │   │   ├── enricher.py              # Event enrichment
│   │   │   ├── correlator.py            # Alert correlation
│   │   │   ├── classifier.py            # ML classification
│   │   │   └── cep.py                   # Complex event processing
│   │   ├── notifications/
│   │   │   ├── __init__.py
│   │   │   ├── dispatcher.py            # Multi-channel dispatcher
│   │   │   ├── email_service.py         # Email notifications
│   │   │   ├── sms_service.py           # SMS notifications
│   │   │   ├── push_service.py          # Push notifications
│   │   │   └── webhook_service.py       # Webhook notifications
│   │   ├── sources/
│   │   │   ├── __init__.py
│   │   │   ├── noaa_source.py           # NOAA connector
│   │   │   ├── fema_source.py           # FEMA connector
│   │   │   ├── usgs_source.py           # USGS connector
│   │   │   └── base_source.py           # Base connector class
│   │   ├── state/
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py          # Redis connection
│   │   │   ├── session_store.py         # Session management
│   │   │   └── alert_state.py           # Alert state tracking
│   │   ├── circuit_breaker/
│   │   │   ├── __init__.py
│   │   │   └── breaker.py               # Circuit breaker implementation
│   │   └── monitoring/
│   │       ├── __init__.py
│       │   ├── metrics.py               # Prometheus metrics
│       │   └── tracing.py               # Distributed tracing
│   └── ...
├── tests/
│   └── realtime/
│       ├── test_kafka.py
│       ├── test_websocket.py
│       ├── test_processing.py
│       └── test_notifications.py
├── docker/
│   ├── docker-compose.kafka.yml
│   ├── docker-compose.redis.yml
│   └── Dockerfile.realtime
└── docs/
    └── realtime/
        ├── architecture.md
        ├── deployment.md
        └── api.md
```

---

## 5. Core Implementation Code

### 5.1 Event Models (`src/realtime/models/events.py`)

```python
"""Event models for real-time data pipeline"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import json


class EventType(str, Enum):
    """Event types for the real-time pipeline"""
    WEATHER_ALERT = "weather_alert"
    DISASTER_DECLARATION = "disaster_declaration"
    SEISMIC_EVENT = "seismic_event"
    SENSOR_READING = "sensor_reading"
    SYSTEM_METRIC = "system_metric"
    CORRELATED_EVENT = "correlated_event"


class SeverityLevel(str, Enum):
    """Severity levels for events"""
    EXTREME = "extreme"
    SEVERE = "severe"
    MODERATE = "moderate"
    MINOR = "minor"
    UNKNOWN = "unknown"


class EventStatus(str, Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    ENRICHED = "enriched"
    CLASSIFIED = "classified"
    NOTIFIED = "notified"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FAILED = "failed"


@dataclass
class GeoLocation:
    """Geographic location data"""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AffectedRegion:
    """Affected region information"""
    county_fips: str
    county_name: str
    state: str
    population: Optional[int] = None
    vulnerability_score: Optional[float] = None
    geometry: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BaseEvent:
    """Base event class"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.SYSTEM_METRIC
    source: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    received_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: EventStatus = EventStatus.PENDING
    version: str = "1.0"
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "timestamp": self.timestamp,
            "received_at": self.received_at,
            "status": self.status.value,
            "version": self.version
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class WeatherAlertEvent(BaseEvent):
    """Weather alert event from NOAA"""
    event_type: EventType = EventType.WEATHER_ALERT
    source: str = "NOAA"
    
    # Alert details
    alert_id: str = ""
    event: str = ""
    severity: SeverityLevel = SeverityLevel.UNKNOWN
    certainty: str = ""
    urgency: str = ""
    headline: str = ""
    description: str = ""
    instruction: str = ""
    
    # Timing
    effective: str = ""
    expires: str = ""
    onset: Optional[str] = None
    ends: Optional[str] = None
    
    # Geographic
    area_description: str = ""
    affected_regions: List[AffectedRegion] = field(default_factory=list)
    polygon: Optional[List[GeoLocation]] = None
    
    # Enrichment data
    vulnerability_correlation: Optional[Dict] = None
    ml_severity_score: Optional[float] = None
    predicted_impact: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        base = super().to_dict()
        base.update({
            "alert_id": self.alert_id,
            "event": self.event,
            "severity": self.severity.value,
            "certainty": self.certainty,
            "urgency": self.urgency,
            "headline": self.headline,
            "description": self.description,
            "instruction": self.instruction,
            "effective": self.effective,
            "expires": self.expires,
            "area_description": self.area_description,
            "affected_regions": [r.to_dict() for r in self.affected_regions],
            "vulnerability_correlation": self.vulnerability_correlation,
            "ml_severity_score": self.ml_severity_score,
            "predicted_impact": self.predicted_impact
        })
        return base


@dataclass
class CorrelatedEvent(BaseEvent):
    """Multi-source correlated event"""
    event_type: EventType = EventType.CORRELATED_EVENT
    source: str = "correlation_engine"
    
    correlation_id: str = ""
    correlation_type: str = ""  # "temporal", "spatial", "causal"
    correlation_score: float = 0.0
    source_events: List[str] = field(default_factory=list)
    source_event_types: List[str] = field(default_factory=list)
    combined_severity: SeverityLevel = SeverityLevel.UNKNOWN
    combined_risk_score: float = 0.0
    affected_population: Optional[int] = None
    recommended_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        base = super().to_dict()
        base.update({
            "correlation_id": self.correlation_id,
            "correlation_type": self.correlation_type,
            "correlation_score": self.correlation_score,
            "source_events": self.source_events,
            "source_event_types": self.source_event_types,
            "combined_severity": self.combined_severity.value,
            "combined_risk_score": self.combined_risk_score,
            "affected_population": self.affected_population,
            "recommended_actions": self.recommended_actions
        })
        return base


@dataclass
class NotificationEvent(BaseEvent):
    """Notification event for dispatch"""
    event_type: EventType = EventType.SYSTEM_METRIC
    source: str = "notification_service"
    
    notification_id: str = ""
    channel: str = ""  # "email", "sms", "push", "webhook", "websocket"
    recipient: str = ""
    recipient_type: str = ""  # "user", "subscription", "group"
    subject: str = ""
    body: str = ""
    html_body: Optional[str] = None
    data: Dict = field(default_factory=dict)
    source_event_id: str = ""
    source_event_type: str = ""
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    opened_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict:
        base = super().to_dict()
        base.update({
            "notification_id": self.notification_id,
            "channel": self.channel,
            "recipient": self.recipient,
            "recipient_type": self.recipient_type,
            "subject": self.subject,
            "body": self.body,
            "html_body": self.html_body,
            "data": self.data,
            "source_event_id": self.source_event_id,
            "source_event_type": self.source_event_type,
            "sent_at": self.sent_at,
            "delivered_at": self.delivered_at,
            "opened_at": self.opened_at,
            "error_message": self.error_message,
            "retry_count": self.retry_count
        })
        return base
```

---

## 6. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
1. **Kafka Infrastructure Setup**
   - Deploy Kafka cluster with Docker Compose
   - Create standard topics
   - Implement Kafka producer/consumer

2. **Redis State Management**
   - Deploy Redis cluster
   - Implement session store
   - Add caching layer

3. **Event Model Refactoring**
   - Implement new event dataclasses
   - Add serialization/deserialization
   - Create event validation

### Phase 2: Core Pipeline (Weeks 3-4)
1. **Stream Processing**
   - Implement event enricher
   - Add alert correlation engine
   - Create Faust/Kafka Streams apps

2. **WebSocket Server**
   - Implement FastAPI WebSocket server
   - Add connection management
   - Create channel-based pub/sub

3. **Circuit Breaker**
   - Implement circuit breaker pattern
   - Add to all external API calls
   - Create monitoring dashboard

### Phase 3: Intelligence (Weeks 5-6)
1. **ML Classification**
   - Implement alert classifier
   - Add risk scoring
   - Create recommendation engine

2. **Notification System**
   - Implement multi-channel dispatcher
   - Add email/SMS/push services
   - Create notification templates

3. **Complex Event Processing**
   - Implement pattern matching
   - Add temporal correlation
   - Create causal inference

### Phase 4: Integration (Weeks 7-8)
1. **Existing Code Integration**
   - Integrate with weather_client.py
   - Update alert_manager.py
   - Connect to dashboard

2. **Monitoring & Observability**
   - Add Prometheus metrics
   - Create Grafana dashboards
   - Implement distributed tracing

3. **Testing & Optimization**
   - Load testing
   - Performance optimization
   - Fault tolerance testing

---

## 7. Summary

This comprehensive real-time systems enhancement provides ResilienceAI with:

1. **Scalable Event Streaming**: Kafka-based message broker for high-throughput event processing
2. **Real-Time Communication**: WebSocket server for live dashboard updates
3. **Intelligent Processing**: ML-based alert classification and risk scoring
4. **Fault Tolerance**: Circuit breaker pattern for resilient external API calls
5. **Multi-Channel Notifications**: Email, SMS, push, and webhook notifications
6. **Complex Event Processing**: Temporal, spatial, and causal alert correlation
7. **Observability**: Comprehensive monitoring with Prometheus and Grafana

The proposed architecture transforms ResilienceAI from a basic polling-based system to a production-grade, event-driven platform capable of processing thousands of alerts per second with sub-second latency for critical notifications.

---

## Generated Files

- `/mnt/okcomputer/output/resilience_ai_analysis/07_realtime_systems.md`



---

## Appendix A: Kafka Producer Implementation

```python
# src/realtime/kafka/producer.py
"""Kafka producer for real-time event streaming"""
import json
import asyncio
from typing import Dict, Optional, Any, List
from datetime import datetime
from confluent_kafka import Producer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
import logging

from ..models.events import BaseEvent, EventType

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    """High-performance Kafka producer for event streaming"""
    
    def __init__(self, config=None):
        self.config = config
        self.producer: Optional[Producer] = None
        self.delivery_callbacks: Dict[str, asyncio.Future] = {}
        self._pending_messages = 0
        self._stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_failed": 0,
            "bytes_sent": 0
        }
    
    def connect(self, bootstrap_servers: str = "localhost:9092") -> None:
        """Initialize Kafka producer connection"""
        producer_config = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'resilienceai-producer',
            'acks': 'all',
            'retries': 3,
            'retry.backoff.ms': 1000,
            'batch.size': 16384,
            'linger.ms': 5,
            'compression.type': 'lz4',
            'max.in.flight.requests.per.connection': 5,
            'enable.idempotence': True,
        }
        self.producer = Producer(producer_config)
        logger.info(f"Kafka producer connected to {bootstrap_servers}")
    
    def _delivery_callback(self, err: Optional[KafkaError], msg) -> None:
        """Handle message delivery confirmation"""
        if err:
            logger.error(f"Message delivery failed: {err}")
            self._stats["messages_failed"] += 1
        else:
            logger.debug(f"Message delivered to {msg.topic()}")
            self._stats["messages_delivered"] += 1
            self._stats["bytes_sent"] += len(msg.value())
        self._pending_messages -= 1
    
    async def send_event(
        self,
        event: BaseEvent,
        topic: Optional[str] = None,
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send an event to Kafka"""
        if not self.producer:
            raise RuntimeError("Producer not connected")
        
        # Derive topic from event type
        if topic is None:
            topic = self._get_topic_for_event(event)
        
        event_json = json.dumps(event.to_dict(), default=str)
        key = key or event.event_id
        
        try:
            self.producer.produce(
                topic=topic,
                key=key.encode('utf-8'),
                value=event_json.encode('utf-8'),
                callback=self._delivery_callback
            )
            self._pending_messages += 1
            self._stats["messages_sent"] += 1
            self.producer.poll(0)
            return True
        except BufferError:
            self.producer.poll(1)
            return await self.send_event(event, topic, key, headers)
        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            self._stats["messages_failed"] += 1
            return False
    
    def _get_topic_for_event(self, event: BaseEvent) -> str:
        """Get the appropriate Kafka topic for an event"""
        topic_mapping = {
            EventType.WEATHER_ALERT: "raw.weather.alerts",
            EventType.DISASTER_DECLARATION: "raw.disaster.declarations",
            EventType.SEISMIC_EVENT: "raw.seismic.events",
            EventType.SENSOR_READING: "raw.sensor.data",
            EventType.CORRELATED_EVENT: "processed.correlated.events",
            EventType.SYSTEM_METRIC: "internal.metrics"
        }
        return topic_mapping.get(event.event_type, "raw.unknown.events")
    
    def flush(self, timeout: float = 30.0) -> int:
        """Flush pending messages"""
        if self.producer:
            return self.producer.flush(timeout)
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get producer statistics"""
        return {**self._stats, "pending_messages": self._pending_messages}
    
    def close(self) -> None:
        """Close producer connection"""
        if self.producer:
            self.flush()
            self.producer = None


class TopicManager:
    """Manage Kafka topics"""
    
    def __init__(self, bootstrap_servers: str):
        self.admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    
    def create_topic(
        self,
        topic_name: str,
        num_partitions: int = 6,
        replication_factor: int = 1,
        retention_ms: int = 7 * 24 * 60 * 60 * 1000
    ) -> None:
        """Create a Kafka topic with configuration"""
        topic_config = {
            'retention.ms': str(retention_ms),
            'cleanup.policy': 'delete',
            'compression.type': 'lz4',
        }
        new_topic = NewTopic(
            topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
            config=topic_config
        )
        fs = self.admin_client.create_topics([new_topic])
        for topic, f in fs.items():
            try:
                f.result()
                logger.info(f"Topic '{topic}' created")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info(f"Topic '{topic}' already exists")
                else:
                    logger.error(f"Failed to create topic: {e}")
    
    def create_standard_topics(self) -> None:
        """Create standard ResilienceAI topics"""
        topics = [
            ("raw.weather.alerts", 6),
            ("raw.disaster.declarations", 3),
            ("raw.seismic.events", 3),
            ("raw.sensor.data", 12),
            ("processed.enriched.events", 6),
            ("processed.correlated.events", 6),
            ("processed.classified.events", 6),
            ("notifications.high", 3),
            ("notifications.medium", 3),
            ("notifications.low", 3),
            ("internal.metrics", 3),
            ("dead.letter.queue", 3),
        ]
        for topic_name, partitions in topics:
            self.create_topic(topic_name, partitions)
```

---

## Appendix B: WebSocket Server Implementation

```python
# src/realtime/websocket/server.py
"""WebSocket server for real-time client connections"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional, Callable, Any
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

from ..models.events import BaseEvent, EventType

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections with channel-based subscriptions"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
        self.connection_channels: Dict[str, Set[str]] = {}
        self.redis = redis_client
        self._message_handlers: Dict[str, Callable] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        connection_id: Optional[str] = None,
        client_info: Optional[Dict] = None
    ) -> str:
        """Accept new WebSocket connection"""
        await websocket.accept()
        conn_id = connection_id or str(uuid.uuid4())[:8]
        self.active_connections[conn_id] = websocket
        self.connection_channels[conn_id] = set()
        
        logger.info(f"Client {conn_id} connected. Total: {len(self.active_connections)}")
        
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": conn_id,
            "timestamp": datetime.utcnow().isoformat()
        }, conn_id)
        return conn_id
    
    def disconnect(self, connection_id: str) -> None:
        """Handle client disconnection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        channels = self.connection_channels.get(connection_id, set())
        for channel in channels:
            if channel in self.subscriptions:
                self.subscriptions[channel].discard(connection_id)
        if connection_id in self.connection_channels:
            del self.connection_channels[connection_id]
        logger.info(f"Client {connection_id} disconnected")
    
    async def subscribe(self, connection_id: str, channel: str) -> bool:
        """Subscribe connection to a channel"""
        if connection_id not in self.active_connections:
            return False
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()
        self.subscriptions[channel].add(connection_id)
        self.connection_channels[connection_id].add(channel)
        logger.debug(f"Client {connection_id} subscribed to {channel}")
        return True
    
    async def broadcast_to_channel(
        self, channel: str, message: Dict, exclude: Optional[Set[str]] = None
    ) -> int:
        """Broadcast message to all subscribers of a channel"""
        if channel not in self.subscriptions:
            return 0
        sent_count = 0
        disconnected = []
        for conn_id in self.subscriptions[channel]:
            if exclude and conn_id in exclude:
                continue
            try:
                await self.send_personal_message(message, conn_id)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send to {conn_id}: {e}")
                disconnected.append(conn_id)
        for conn_id in disconnected:
            self.disconnect(conn_id)
        return sent_count
    
    async def send_personal_message(self, message: Dict, connection_id: str) -> bool:
        """Send message to specific connection"""
        if connection_id not in self.active_connections:
            return False
        websocket = self.active_connections[connection_id]
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Register a message handler"""
        self._message_handlers[message_type] = handler
    
    async def handle_message(self, connection_id: str, message: Dict) -> None:
        """Handle incoming WebSocket message"""
        msg_type = message.get("type", "unknown")
        if msg_type in self._message_handlers:
            await self._message_handlers[msg_type](connection_id, message)
        else:
            await self.send_personal_message({
                "type": "error",
                "error": f"Unknown message type: {msg_type}"
            }, connection_id)


class RealtimeWebSocketServer:
    """FastAPI-based WebSocket server for real-time updates"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = FastAPI(title="ResilienceAI Real-Time API")
        self.manager: Optional[ConnectionManager] = None
        self.redis: Optional[redis.Redis] = None
        self.redis_url = redis_url
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._setup_routes()
    
    async def startup(self):
        """Initialize connections on startup"""
        self.redis = await redis.from_url(self.redis_url)
        self.manager = ConnectionManager(self.redis)
        self._register_handlers()
        logger.info("WebSocket server started")
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        if self.redis:
            await self.redis.close()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.websocket("/ws/realtime")
        async def websocket_endpoint(websocket: WebSocket):
            client_info = {"headers": dict(websocket.headers), "query_params": dict(websocket.query_params)}
            connection_id = await self.manager.connect(websocket, client_info=client_info)
            try:
                while True:
                    data = await websocket.receive_json()
                    await self.manager.handle_message(connection_id, data)
            except WebSocketDisconnect:
                self.manager.disconnect(connection_id)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.manager.disconnect(connection_id)
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
        
        @self.app.get("/stats")
        async def get_stats():
            if not self.manager:
                return {"error": "Server not initialized"}
            return {"timestamp": datetime.utcnow().isoformat()}
    
    def _register_handlers(self):
        """Register WebSocket message handlers"""
        async def handle_subscribe(conn_id: str, message: Dict):
            channel = message.get("channel", "all")
            success = await self.manager.subscribe(conn_id, channel)
            await self.manager.send_personal_message({
                "type": "subscription_confirmed", "channel": channel, "success": success
            }, conn_id)
        
        async def handle_ping(conn_id: str, message: Dict):
            await self.manager.send_personal_message({
                "type": "pong", "timestamp": datetime.utcnow().isoformat()
            }, conn_id)
        
        self.manager.register_handler("subscribe", handle_subscribe)
        self.manager.register_handler("ping", handle_ping)
    
    async def publish_event(self, event: BaseEvent, channels: Optional[list] = None):
        """Publish event to WebSocket channels"""
        if not self.manager:
            return
        message = {
            "type": "event",
            "event_type": event.event_type.value,
            "data": event.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        if channels:
            for channel in channels:
                await self.manager.broadcast_to_channel(channel, message)
        else:
            for channel in ["all", f"events.{event.event_type.value}"]:
                await self.manager.broadcast_to_channel(channel, message)
    
    def run(self):
        """Run the WebSocket server"""
        import uvicorn
        @self.app.on_event("startup")
        async def on_startup():
            await self.startup()
        @self.app.on_event("shutdown")
        async def on_shutdown():
            await self.shutdown()
        uvicorn.run(self.app, host=self.host, port=self.port)
```

---

## Appendix C: Circuit Breaker Implementation

```python
# src/realtime/circuit_breaker/breaker.py
"""Circuit breaker pattern for fault tolerance"""
import asyncio
import logging
from typing import Callable, Optional, Any
from datetime import datetime
from enum import Enum
import functools

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3,
        expected_exception: type = Exception
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.expected_exception = expected_exception
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection"""
        async with self._lock:
            await self._update_state()
            if self.state == CircuitState.OPEN:
                raise CircuitBreakerOpen(f"Circuit '{self.name}' is OPEN")
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerOpen(f"Circuit '{self.name}' HALF_OPEN limit reached")
                self.half_open_calls += 1
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            raise
    
    async def _update_state(self):
        if self.state == CircuitState.OPEN and self.last_failure_time:
            elapsed = (datetime.utcnow() - self.last_failure_time).seconds
            if elapsed >= self.recovery_timeout:
                await self._transition_to(CircuitState.HALF_OPEN)
    
    async def _on_success(self):
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_max_calls:
                    await self._transition_to(CircuitState.CLOSED)
            else:
                self.failure_count = 0
    
    async def _on_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            if self.state == CircuitState.HALF_OPEN:
                await self._transition_to(CircuitState.OPEN)
            elif self.failure_count >= self.failure_threshold:
                await self._transition_to(CircuitState.OPEN)
    
    async def _transition_to(self, new_state: CircuitState):
        old_state = self.state
        self.state = new_state
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.half_open_calls = 0
            self.success_count = 0
        logger.info(f"Circuit '{self.name}' transitioned: {old_state.value} -> {new_state.value}")


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open"""
    pass


# Global registry
registry = {}


def circuit_breaker(name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
    """Decorator for adding circuit breaker to function"""
    def decorator(func: Callable) -> Callable:
        if name not in registry:
            registry[name] = CircuitBreaker(name, failure_threshold, recovery_timeout)
        breaker = registry[name]
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
```

---

## Appendix D: Docker Compose Configurations

### Kafka Infrastructure

```yaml
# docker/docker-compose.kafka.yml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "29092:29092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  kafdrop:
    image: obsidiandynamics/kafdrop:4.0.1
    depends_on:
      - kafka
    ports:
      - "9000:9000"
    environment:
      KAFKA_BROKERCONNECT: 'kafka:29092'
```

### Redis Infrastructure

```yaml
# docker/docker-compose.redis.yml
version: '3.8'

services:
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  redis-commander:
    image: rediscommander/redis-commander:latest
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8082:8081"
    depends_on:
      - redis

volumes:
  redis-data:
```

---

## Appendix E: Prometheus Metrics

```python
# src/realtime/monitoring/metrics.py
"""Prometheus metrics for real-time system monitoring"""
from prometheus_client import Counter, Histogram, Gauge, Info

# Event processing metrics
EVENTS_PROCESSED = Counter(
    'resilienceai_events_processed_total',
    'Total events processed',
    ['event_type', 'status']
)

EVENT_PROCESSING_DURATION = Histogram(
    'resilienceai_event_processing_duration_seconds',
    'Event processing duration',
    ['event_type', 'stage']
)

# Kafka metrics
KAFKA_MESSAGES_SENT = Counter(
    'resilienceai_kafka_messages_sent_total',
    'Total Kafka messages sent',
    ['topic', 'status']
)

KAFKA_MESSAGES_CONSUMED = Counter(
    'resilienceai_kafka_messages_consumed_total',
    'Total Kafka messages consumed',
    ['topic', 'consumer_group']
)

# WebSocket metrics
WEBSOCKET_CONNECTIONS = Gauge(
    'resilienceai_websocket_connections',
    'Current WebSocket connections',
    ['channel']
)

# Notification metrics
NOTIFICATIONS_SENT = Counter(
    'resilienceai_notifications_sent_total',
    'Total notifications sent',
    ['channel', 'priority', 'status']
)

# Circuit breaker metrics
CIRCUIT_BREAKER_STATE = Gauge(
    'resilienceai_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=half-open, 2=open)',
    ['name']
)
```

---

*Document generated for ResilienceAI Real-Time Systems Enhancement*
