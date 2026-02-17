# ResilienceAI Message Queue Integration Design

## Executive Summary

This document provides a comprehensive message queue architecture for ResilienceAI, enabling async processing, event-driven architecture, and decoupled microservices. The design supports both RabbitMQ (for complex routing) and Apache Kafka (for high-throughput streaming), with implementation patterns for producer/consumer, dead letter queues, event sourcing, and saga patterns.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Message Queue Selection](#2-message-queue-selection)
3. [RabbitMQ Integration](#3-rabbitmq-integration)
4. [Apache Kafka Integration](#4-apache-kafka-integration)
5. [Producer/Consumer Patterns](#5-producerconsumer-patterns)
6. [Message Routing](#6-message-routing)
7. [Dead Letter Queues](#7-dead-letter-queues)
8. [Message Persistence](#8-message-persistence)
9. [Scalability Patterns](#9-scalability-patterns)
10. [Monitoring & Observability](#10-monitoring--observability)
11. [Event Sourcing](#11-event-sourcing)
12. [Saga Patterns](#12-saga-patterns)
13. [Deployment Guide](#13-deployment-guide)
14. [Implementation Priority](#14-implementation-priority)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ResilienceAI Message Queue Layer                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   API Gateway │───▶│  Message     │───▶│  RabbitMQ    │                   │
│  │              │    │  Router      │    │  Cluster     │                   │
│  └──────────────┘    └──────────────┘    └──────┬───────┘                   │
│                                                  │                           │
│  ┌──────────────┐    ┌──────────────┐           │    ┌──────────────┐        │
│  │  Event       │◀───│  Kafka       │◀──────────┘    │  DLQ         │        │
│  │  Store       │    │  Cluster     │                │  Handler     │        │
│  └──────────────┘    └──────┬───────┘                └──────────────┘        │
│                             │                                                │
│  ┌──────────────┐    ┌──────┴───────┐    ┌──────────────┐                   │
│  │  Analytics   │◀───│  Consumer    │◀───│  Consumer    │                   │
│  │  Service     │    │  Group A     │    │  Group B     │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      Saga Orchestrator                               │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │    │
│  │  │ Service │─▶│ Service │─▶│ Service │─▶│ Service │─▶│ Service │   │    │
│  │  │   A     │  │   B     │  │   C     │  │   D     │  │   E     │   │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Message Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Message Flow Patterns                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Pattern 1: Simple Queue (Task Processing)                                   │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                                  │
│  │Producer │───▶│  Queue  │───▶│Consumer │                                  │
│  └─────────┘    └─────────┘    └─────────┘                                  │
│                                                                              │
│  Pattern 2: Pub/Sub (Event Broadcasting)                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                                  │
│  │Producer │───▶│ Exchange│───▶│Queue 1  │───▶ Consumer A                   │
│  └─────────┘    │ (Fanout)│    ├─────────┤                                  │
│                 │         │───▶│Queue 2  │───▶ Consumer B                   │
│                 └─────────┘    ├─────────┤                                  │
│                                │Queue 3  │───▶ Consumer C                   │
│                                └─────────┘                                  │
│                                                                              │
│  Pattern 3: Topic Routing (Selective Delivery)                               │
│  ┌─────────┐    ┌─────────┐    ┌─────────────────┐                          │
│  │Producer │───▶│ Topic   │───▶│ *.critical.*    │───▶ Alert Service        │
│  │(routing │    │ Exchange│    ├─────────────────┤                          │
│  │  key)   │    │         │───▶│ #.analytics     │───▶ Analytics Service    │
│  └─────────┘    │         │    ├─────────────────┤                          │
│                 │         │───▶│ logs.*.error    │───▶ Error Handler        │
│                 └─────────┘    └─────────────────┘                          │
│                                                                              │
│  Pattern 4: Request/Reply (Synchronous over Async)                           │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐                   │
│  │ Client  │───▶│ Request │───▶│ Server  │───▶│ Response│───▶ Client         │
│  │         │    │  Queue  │    │         │    │  Queue  │                   │
│  │         │◀────────────────────────────────────────────│                   │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Service Integration Map

| Service | Queue Type | Patterns Used | Priority |
|---------|-----------|---------------|----------|
| Incident Processor | RabbitMQ | Work Queue, DLQ | High |
| Alert Manager | RabbitMQ | Pub/Sub, Routing | High |
| Analytics Engine | Kafka | Stream Processing | High |
| Notification Service | RabbitMQ | Topic Exchange | Medium |
| Report Generator | RabbitMQ | Work Queue | Medium |
| Audit Logger | Kafka | Event Sourcing | High |
| ML Prediction Service | RabbitMQ | RPC Pattern | Medium |
| Workflow Orchestrator | RabbitMQ | Saga Pattern | High |

---

## 2. Message Queue Selection

### 2.1 RabbitMQ vs Kafka Comparison

| Feature | RabbitMQ | Apache Kafka |
|---------|----------|--------------|
| **Best For** | Complex routing, RPC, task queues | High throughput, stream processing |
| **Throughput** | ~50K msg/sec | ~1M+ msg/sec |
| **Message Ordering** | Per queue | Per partition (guaranteed) |
| **Persistence** | Optional (to disk) | Always (to log) |
| **Replay Capability** | Limited | Full replay from offset |
| **Routing** | Advanced (exchanges) | Simple (topics) |
| **Latency** | Sub-millisecond | ~10ms |
| **Retention** | Until consumed | Time/size based |

### 2.2 ResilienceAI Queue Strategy

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/queue_selector.py
"""
Message Queue Selection Strategy for ResilienceAI
"""
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class QueueType(Enum):
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"


@dataclass
class MessageCharacteristics:
    """Characteristics to determine optimal queue type"""
    throughput_required: int  # messages per second
    requires_routing: bool
    requires_ordering: bool
    requires_replay: bool
    latency_sensitive: bool
    retention_hours: int
    message_size_kb: int


class QueueSelector:
    """
    Intelligent queue selection based on message characteristics.
    """
    
    # Thresholds for queue selection
    HIGH_THROUGHPUT_THRESHOLD = 100000  # 100K msg/sec
    LARGE_MESSAGE_THRESHOLD = 512  # 512 KB
    LONG_RETENTION_THRESHOLD = 24  # 24 hours
    
    @classmethod
    def select_queue(cls, characteristics: MessageCharacteristics) -> QueueType:
        """
        Select optimal message queue based on characteristics.
        
        Decision Matrix:
        - High throughput (>100K/sec) → Kafka
        - Requires replay → Kafka
        - Complex routing needed → RabbitMQ
        - Low latency critical → RabbitMQ
        - Long retention (>24h) → Kafka
        """
        kafka_score = 0
        rabbitmq_score = 0
        
        # Throughput analysis
        if characteristics.throughput_required > cls.HIGH_THROUGHPUT_THRESHOLD:
            kafka_score += 3
        else:
            rabbitmq_score += 1
        
        # Routing complexity
        if characteristics.requires_routing:
            rabbitmq_score += 3
        
        # Replay requirement
        if characteristics.requires_replay:
            kafka_score += 3
        
        # Ordering requirement
        if characteristics.requires_ordering:
            kafka_score += 1  # Kafka has better ordering guarantees
        
        # Latency sensitivity
        if characteristics.latency_sensitive:
            rabbitmq_score += 2
        
        # Retention needs
        if characteristics.retention_hours > cls.LONG_RETENTION_THRESHOLD:
            kafka_score += 2
        
        # Message size
        if characteristics.message_size_kb > cls.LARGE_MESSAGE_THRESHOLD:
            kafka_score += 1  # Kafka handles large messages better
        
        return QueueType.KAFKA if kafka_score >= rabbitmq_score else QueueType.RABBITMQ
    
    @classmethod
    def get_recommended_config(cls, queue_type: QueueType) -> Dict[str, Any]:
        """Get recommended configuration for selected queue type."""
        configs = {
            QueueType.RABBITMQ: {
                "cluster_nodes": 3,
                "queues_per_node": 10,
                "mirror_queues": True,
                "ha_mode": "exactly",
                "ha_params": 2,
                "max_length": 100000,
                "message_ttl": 86400000,  # 24 hours
                "delivery_mode": 2,  # persistent
            },
            QueueType.KAFKA: {
                "brokers": 3,
                "replication_factor": 3,
                "min_isr": 2,
                "partitions": 12,
                "retention_ms": 604800000,  # 7 days
                "segment_bytes": 1073741824,  # 1GB
                "compression": "lz4",
            }
        }
        return configs.get(queue_type, {})


# Predefined configurations for ResilienceAI services
SERVICE_QUEUE_CONFIGS = {
    "incident_processor": {
        "queue_type": QueueType.RABBITMQ,
        "characteristics": MessageCharacteristics(
            throughput_required=10000,
            requires_routing=True,
            requires_ordering=False,
            requires_replay=False,
            latency_sensitive=True,
            retention_hours=24,
            message_size_kb=10
        )
    },
    "analytics_engine": {
        "queue_type": QueueType.KAFKA,
        "characteristics": MessageCharacteristics(
            throughput_required=500000,
            requires_routing=False,
            requires_ordering=True,
            requires_replay=True,
            latency_sensitive=False,
            retention_hours=168,
            message_size_kb=50
        )
    },
    "audit_logger": {
        "queue_type": QueueType.KAFKA,
        "characteristics": MessageCharacteristics(
            throughput_required=100000,
            requires_routing=False,
            requires_ordering=True,
            requires_replay=True,
            latency_sensitive=False,
            retention_hours=720,  # 30 days
            message_size_kb=5
        )
    },
    "notification_service": {
        "queue_type": QueueType.RABBITMQ,
        "characteristics": MessageCharacteristics(
            throughput_required=5000,
            requires_routing=True,
            requires_ordering=False,
            requires_replay=False,
            latency_sensitive=True,
            retention_hours=1,
            message_size_kb=2
        )
    }
}
```

---

## 3. RabbitMQ Integration

### 3.1 Core RabbitMQ Client

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/rabbitmq_client.py
"""
RabbitMQ Client for ResilienceAI
Provides robust connection management, publishing, and consuming capabilities.
"""
import json
import asyncio
import logging
from typing import Dict, Any, Callable, Optional, List, Union
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from enum import Enum

import aio_pika
from aio_pika import ExchangeType, DeliveryMode
from aio_pika.abc import AbstractChannel, AbstractQueue, AbstractExchange


logger = logging.getLogger(__name__)


class ExchangeType(Enum):
    DIRECT = "direct"
    FANOUT = "fanout"
    TOPIC = "topic"
    HEADERS = "headers"


@dataclass
class RabbitMQConfig:
    """RabbitMQ connection configuration"""
    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    virtual_host: str = "/"
    heartbeat: int = 600
    connection_timeout: int = 30
    max_channels: int = 100
    prefetch_count: int = 10
    
    @property
    def connection_url(self) -> str:
        return (
            f"amqp://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.virtual_host}"
        )


@dataclass
class QueueDeclaration:
    """Queue declaration parameters"""
    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "durable": self.durable,
            "exclusive": self.exclusive,
            "auto_delete": self.auto_delete,
            "arguments": self.arguments or {}
        }


@dataclass
class ExchangeDeclaration:
    """Exchange declaration parameters"""
    name: str
    type: ExchangeType = ExchangeType.DIRECT
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    arguments: Optional[Dict[str, Any]] = None


@dataclass
class BindingConfig:
    """Queue-Exchange binding configuration"""
    queue_name: str
    exchange_name: str
    routing_key: str = ""
    arguments: Optional[Dict[str, Any]] = None


@dataclass
class MessageMetadata:
    """Message metadata for tracking and routing"""
    message_id: str
    correlation_id: Optional[str] = None
    timestamp: Optional[str] = None
    source_service: Optional[str] = None
    event_type: Optional[str] = None
    priority: int = 0
    headers: Optional[Dict[str, Any]] = None


class RabbitMQConnectionPool:
    """
    Connection pool for RabbitMQ connections.
    Manages connection lifecycle and provides channel pooling.
    """
    
    def __init__(self, config: RabbitMQConfig, pool_size: int = 5):
        self.config = config
        self.pool_size = pool_size
        self._connections: List[aio_pika.RobustConnection] = []
        self._channels: List[AbstractChannel] = []
        self._lock = asyncio.Lock()
        self._closed = True
    
    async def initialize(self):
        """Initialize connection pool"""
        async with self._lock:
            if not self._closed:
                return
            
            for _ in range(self.pool_size):
                connection = await aio_pika.connect_robust(
                    self.config.connection_url,
                    heartbeat=self.config.heartbeat,
                    timeout=self.config.connection_timeout
                )
                self._connections.append(connection)
            
            self._closed = False
            logger.info(f"RabbitMQ connection pool initialized with {self.pool_size} connections")
    
    @asynccontextmanager
    async def acquire_channel(self) -> AbstractChannel:
        """Acquire a channel from the pool"""
        async with self._lock:
            if self._closed:
                raise RuntimeError("Connection pool is closed")
            
            # Round-robin channel selection
            connection = self._connections[len(self._channels) % len(self._connections)]
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=self.config.prefetch_count)
            
        try:
            yield channel
        finally:
            await channel.close()
    
    async def close(self):
        """Close all connections"""
        async with self._lock:
            self._closed = True
            for connection in self._connections:
                await connection.close()
            self._connections.clear()
            logger.info("RabbitMQ connection pool closed")


class RabbitMQClient:
    """
    High-level RabbitMQ client for ResilienceAI.
    Provides publish/subscribe, RPC, and work queue patterns.
    """
    
    def __init__(self, config: RabbitMQConfig):
        self.config = config
        self.pool = RabbitMQConnectionPool(config)
        self._exchanges: Dict[str, AbstractExchange] = {}
        self._queues: Dict[str, AbstractQueue] = {}
        self._consumers: Dict[str, asyncio.Task] = {}
    
    async def connect(self):
        """Initialize connection to RabbitMQ"""
        await self.pool.initialize()
    
    async def disconnect(self):
        """Clean up resources"""
        # Cancel all consumers
        for task in self._consumers.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        await self.pool.close()
    
    async def declare_exchange(
        self,
        name: str,
        exchange_type: ExchangeType = ExchangeType.DIRECT,
        durable: bool = True,
        **kwargs
    ) -> AbstractExchange:
        """Declare an exchange"""
        async with self.pool.acquire_channel() as channel:
            exchange = await channel.declare_exchange(
                name=name,
                type=exchange_type.value,
                durable=durable,
                **kwargs
            )
            self._exchanges[name] = exchange
            logger.debug(f"Exchange declared: {name} ({exchange_type.value})")
            return exchange
    
    async def declare_queue(
        self,
        name: str,
        durable: bool = True,
        exclusive: bool = False,
        auto_delete: bool = False,
        arguments: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AbstractQueue:
        """Declare a queue with optional arguments"""
        async with self.pool.acquire_channel() as channel:
            queue = await channel.declare_queue(
                name=name,
                durable=durable,
                exclusive=exclusive,
                auto_delete=auto_delete,
                arguments=arguments,
                **kwargs
            )
            self._queues[name] = queue
            logger.debug(f"Queue declared: {name}")
            return queue
    
    async def bind_queue(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str = "",
        arguments: Optional[Dict[str, Any]] = None
    ):
        """Bind a queue to an exchange"""
        async with self.pool.acquire_channel() as channel:
            queue = await channel.get_queue(queue_name)
            exchange = await channel.get_exchange(exchange_name)
            await queue.bind(exchange, routing_key=routing_key, arguments=arguments)
            logger.debug(f"Bound queue {queue_name} to {exchange_name} with key '{routing_key}'")
    
    async def publish(
        self,
        exchange_name: str,
        routing_key: str,
        message: Dict[str, Any],
        metadata: Optional[MessageMetadata] = None,
        mandatory: bool = False,
        expiration: Optional[int] = None
    ):
        """
        Publish a message to an exchange.
        
        Args:
            exchange_name: Target exchange
            routing_key: Routing key for message
            message: Message payload
            metadata: Message metadata
            mandatory: Require message to be routed to a queue
            expiration: Message TTL in milliseconds
        """
        async with self.pool.acquire_channel() as channel:
            exchange = await channel.get_exchange(exchange_name)
            
            # Build message properties
            properties = {
                "delivery_mode": DeliveryMode.PERSISTENT,
                "content_type": "application/json",
            }
            
            if metadata:
                properties.update({
                    "message_id": metadata.message_id,
                    "correlation_id": metadata.correlation_id,
                    "timestamp": metadata.timestamp,
                    "priority": metadata.priority,
                    "headers": {
                        **(metadata.headers or {}),
                        "source_service": metadata.source_service,
                        "event_type": metadata.event_type,
                    }
                })
            
            if expiration:
                properties["expiration"] = expiration
            
            # Publish message
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    **properties
                ),
                routing_key=routing_key,
                mandatory=mandatory
            )
            
            logger.debug(f"Published message to {exchange_name}/{routing_key}")
    
    async def consume(
        self,
        queue_name: str,
        handler: Callable[[Dict[str, Any], MessageMetadata], asyncio.Coroutine],
        auto_ack: bool = False,
        consumer_tag: Optional[str] = None
    ) -> str:
        """
        Start consuming messages from a queue.
        
        Args:
            queue_name: Queue to consume from
            handler: Async callback for message processing
            auto_ack: Automatically acknowledge messages
            consumer_tag: Optional consumer identifier
            
        Returns:
            Consumer tag
        """
        async def _consume():
            async with self.pool.acquire_channel() as channel:
                queue = await channel.get_queue(queue_name)
                
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            try:
                                # Parse message body
                                body = json.loads(message.body.decode())
                                
                                # Extract metadata
                                metadata = MessageMetadata(
                                    message_id=message.message_id or "",
                                    correlation_id=message.correlation_id,
                                    timestamp=str(message.timestamp) if message.timestamp else None,
                                    priority=message.priority or 0,
                                    headers=dict(message.headers) if message.headers else {}
                                )
                                
                                # Call handler
                                await handler(body, metadata)
                                
                            except Exception as e:
                                logger.exception(f"Error processing message: {e}")
                                if not auto_ack:
                                    # Reject message and requeue
                                    await message.reject(requeue=True)
        
        # Start consumer task
        tag = consumer_tag or f"consumer_{queue_name}_{id(handler)}"
        self._consumers[tag] = asyncio.create_task(_consume())
        logger.info(f"Started consumer {tag} on queue {queue_name}")
        return tag
    
    async def stop_consumer(self, consumer_tag: str):
        """Stop a running consumer"""
        if consumer_tag in self._consumers:
            self._consumers[consumer_tag].cancel()
            try:
                await self._consumers[consumer_tag]
            except asyncio.CancelledError:
                pass
            del self._consumers[consumer_tag]
            logger.info(f"Stopped consumer {consumer_tag}")


class RabbitMQRPCClient:
    """
    RPC client implementation over RabbitMQ.
    Enables synchronous-style calls over async messaging.
    """
    
    def __init__(self, client: RabbitMQClient):
        self.client = client
        self._response_queues: Dict[str, asyncio.Queue] = {}
        self._consumer_tag: Optional[str] = None
    
    async def initialize(self):
        """Initialize RPC client"""
        # Create response queue
        await self.client.declare_queue(
            "rpc_responses",
            exclusive=True,
            auto_delete=True
        )
        
        # Start response consumer
        self._consumer_tag = await self.client.consume(
            "rpc_responses",
            self._handle_response
        )
    
    async def _handle_response(self, message: Dict[str, Any], metadata: MessageMetadata):
        """Handle RPC response"""
        correlation_id = metadata.correlation_id
        if correlation_id and correlation_id in self._response_queues:
            await self._response_queues[correlation_id].put(message)
    
    async def call(
        self,
        exchange_name: str,
        routing_key: str,
        request: Dict[str, Any],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Make an RPC call.
        
        Args:
            exchange_name: Target exchange
            routing_key: Routing key for RPC service
            request: Request payload
            timeout: Maximum wait time for response
            
        Returns:
            Response from RPC service
        """
        import uuid
        
        correlation_id = str(uuid.uuid4())
        response_queue = asyncio.Queue()
        self._response_queues[correlation_id] = response_queue
        
        try:
            # Publish request
            metadata = MessageMetadata(
                message_id=str(uuid.uuid4()),
                correlation_id=correlation_id,
                source_service="rpc_client",
                headers={"reply_to": "rpc_responses"}
            )
            
            await self.client.publish(
                exchange_name=exchange_name,
                routing_key=routing_key,
                message=request,
                metadata=metadata
            )
            
            # Wait for response
            return await asyncio.wait_for(
                response_queue.get(),
                timeout=timeout
            )
            
        finally:
            del self._response_queues[correlation_id]
```

### 3.2 RabbitMQ Configuration

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/rabbitmq_config.py
"""
RabbitMQ Configuration for ResilienceAI Services
"""
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class QueueConfig:
    """Queue configuration with DLQ setup"""
    name: str
    durable: bool = True
    arguments: Dict[str, Any] = field(default_factory=dict)
    dlq_enabled: bool = True
    dlq_name: str = ""
    dlx_name: str = ""
    max_retries: int = 3
    retry_ttl: int = 5000  # 5 seconds
    message_ttl: int = 86400000  # 24 hours
    max_length: int = 100000


@dataclass
class ExchangeConfig:
    """Exchange configuration"""
    name: str
    type: str = "direct"
    durable: bool = True
    auto_delete: bool = False


# ResilienceAI RabbitMQ Topology
RESILIENCE_AI_RABBITMQ_CONFIG = {
    "exchanges": [
        # Main exchanges
        ExchangeConfig(name="resilience.direct", type="direct"),
        ExchangeConfig(name="resilience.topic", type="topic"),
        ExchangeConfig(name="resilience.fanout", type="fanout"),
        ExchangeConfig(name="resilience.headers", type="headers"),
        
        # Dead letter exchange
        ExchangeConfig(name="resilience.dlx", type="topic"),
        
        # Delayed message exchange
        ExchangeConfig(name="resilience.delayed", type="x-delayed-message"),
        
        # Service-specific exchanges
        ExchangeConfig(name="incidents.direct", type="direct"),
        ExchangeConfig(name="alerts.topic", type="topic"),
        ExchangeConfig(name="notifications.fanout", type="fanout"),
        ExchangeConfig(name="analytics.topic", type="topic"),
    ],
    
    "queues": [
        # Incident Processing Queues
        QueueConfig(
            name="incidents.new",
            arguments={
                "x-max-priority": 10,
                "x-message-ttl": 300000,  # 5 minutes
            },
            dlq_name="incidents.new.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="incidents.processing",
            arguments={
                "x-max-priority": 10,
            },
            dlq_name="incidents.processing.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="incidents.resolved",
            dlq_name="incidents.resolved.dlq",
            dlx_name="resilience.dlx"
        ),
        
        # Alert Management Queues
        QueueConfig(
            name="alerts.critical",
            arguments={
                "x-max-priority": 10,
                "x-message-ttl": 60000,  # 1 minute - critical alerts must be processed quickly
            },
            dlq_name="alerts.critical.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="alerts.warning",
            arguments={
                "x-max-priority": 5,
            },
            dlq_name="alerts.warning.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="alerts.info",
            dlq_name="alerts.info.dlq",
            dlx_name="resilience.dlx"
        ),
        
        # Notification Queues
        QueueConfig(
            name="notifications.email",
            arguments={
                "x-max-length": 50000,
            },
            dlq_name="notifications.email.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="notifications.sms",
            arguments={
                "x-max-length": 10000,
            },
            dlq_name="notifications.sms.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="notifications.push",
            dlq_name="notifications.push.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="notifications.slack",
            dlq_name="notifications.slack.dlq",
            dlx_name="resilience.dlx"
        ),
        
        # Report Generation Queues
        QueueConfig(
            name="reports.requests",
            arguments={
                "x-message-ttl": 3600000,  # 1 hour
            },
            dlq_name="reports.requests.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="reports.completed",
            dlq_name="reports.completed.dlq",
            dlx_name="resilience.dlx"
        ),
        
        # ML Prediction Queues
        QueueConfig(
            name="ml.predictions",
            arguments={
                "x-max-length": 10000,
            },
            dlq_name="ml.predictions.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="ml.training",
            arguments={
                "x-message-ttl": 86400000,  # 24 hours
            },
            dlq_name="ml.training.dlq",
            dlx_name="resilience.dlx"
        ),
        
        # Workflow/Saga Queues
        QueueConfig(
            name="saga.commands",
            dlq_name="saga.commands.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="saga.events",
            dlq_name="saga.events.dlq",
            dlx_name="resilience.dlx"
        ),
        QueueConfig(
            name="saga.compensations",
            dlq_name="saga.compensations.dlq",
            dlx_name="resilience.dlx"
        ),
        
        # Dead Letter Queues
        QueueConfig(
            name="dlq.main",
            arguments={
                "x-message-ttl": 604800000,  # 7 days
                "x-max-length": 1000000,
            },
            dlq_enabled=False
        ),
        QueueConfig(
            name="dlq.critical",
            arguments={
                "x-message-ttl": 2592000000,  # 30 days
            },
            dlq_enabled=False
        ),
    ],
    
    "bindings": [
        # Incident bindings
        {"queue": "incidents.new", "exchange": "incidents.direct", "routing_key": "incident.new"},
        {"queue": "incidents.processing", "exchange": "incidents.direct", "routing_key": "incident.process"},
        {"queue": "incidents.resolved", "exchange": "incidents.direct", "routing_key": "incident.resolved"},
        
        # Alert bindings with topic routing
        {"queue": "alerts.critical", "exchange": "alerts.topic", "routing_key": "alert.critical.*"},
        {"queue": "alerts.warning", "exchange": "alerts.topic", "routing_key": "alert.warning.*"},
        {"queue": "alerts.info", "exchange": "alerts.topic", "routing_key": "alert.info.*"},
        {"queue": "alerts.critical", "exchange": "alerts.topic", "routing_key": "alert.#.critical"},
        
        # Notification bindings
        {"queue": "notifications.email", "exchange": "notifications.fanout"},
        {"queue": "notifications.sms", "exchange": "notifications.fanout"},
        {"queue": "notifications.push", "exchange": "notifications.fanout"},
        {"queue": "notifications.slack", "exchange": "notifications.fanout"},
        
        # DLQ bindings
        {"queue": "dlq.main", "exchange": "resilience.dlx", "routing_key": "#"},
        {"queue": "dlq.critical", "exchange": "resilience.dlx", "routing_key": "*.critical.#"},
    ]
}


def get_queue_arguments(config: QueueConfig) -> Dict[str, Any]:
    """Generate queue arguments including DLQ configuration"""
    args = dict(config.arguments)
    
    if config.dlq_enabled and config.dlx_name:
        args["x-dead-letter-exchange"] = config.dlx_name
        if config.dlq_name:
            args["x-dead-letter-routing-key"] = config.dlq_name
    
    if config.max_length:
        args["x-max-length"] = config.max_length
    
    if config.message_ttl:
        args["x-message-ttl"] = config.message_ttl
    
    return args
```



---

## 4. Apache Kafka Integration

### 4.1 Core Kafka Client

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/kafka_client.py
"""
Apache Kafka Client for ResilienceAI
Provides producer, consumer, and stream processing capabilities.
"""
import json
import asyncio
import logging
from typing import Dict, Any, Callable, Optional, List, Union, Set
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError


logger = logging.getLogger(__name__)


@dataclass
class KafkaConfig:
    """Kafka connection configuration"""
    bootstrap_servers: List[str] = None
    client_id: str = "resilience-ai"
    
    # Producer settings
    acks: str = "all"
    retries: int = 3
    retry_backoff_ms: int = 1000
    batch_size: int = 16384
    linger_ms: int = 5
    compression_type: str = "lz4"
    max_request_size: int = 1048576  # 1MB
    
    # Consumer settings
    group_id: str = "resilience-ai-consumer"
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 5000
    max_poll_records: int = 500
    max_poll_interval_ms: int = 300000
    session_timeout_ms: int = 10000
    heartbeat_interval_ms: int = 3000
    
    # Security
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None
    ssl_cafile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    
    def __post_init__(self):
        if self.bootstrap_servers is None:
            self.bootstrap_servers = ["localhost:9092"]
    
    @property
    def producer_config(self) -> Dict[str, Any]:
        """Get producer configuration"""
        config = {
            "bootstrap_servers": self.bootstrap_servers,
            "client_id": f"{self.client_id}-producer",
            "acks": self.acks,
            "retries": self.retries,
            "retry_backoff_ms": self.retry_backoff_ms,
            "batch_size": self.batch_size,
            "linger_ms": self.linger_ms,
            "compression_type": self.compression_type,
            "max_request_size": self.max_request_size,
            "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
            "key_serializer": lambda k: k.encode("utf-8") if k else None,
        }
        
        if self.security_protocol != "PLAINTEXT":
            config["security_protocol"] = self.security_protocol
            if self.sasl_mechanism:
                config["sasl_mechanism"] = self.sasl_mechanism
                config["sasl_plain_username"] = self.sasl_username
                config["sasl_plain_password"] = self.sasl_password
        
        return config
    
    @property
    def consumer_config(self) -> Dict[str, Any]:
        """Get consumer configuration"""
        config = {
            "bootstrap_servers": self.bootstrap_servers,
            "client_id": f"{self.client_id}-consumer",
            "group_id": self.group_id,
            "auto_offset_reset": self.auto_offset_reset,
            "enable_auto_commit": self.enable_auto_commit,
            "auto_commit_interval_ms": self.auto_commit_interval_ms,
            "max_poll_records": self.max_poll_records,
            "max_poll_interval_ms": self.max_poll_interval_ms,
            "session_timeout_ms": self.session_timeout_ms,
            "heartbeat_interval_ms": self.heartbeat_interval_ms,
            "value_deserializer": lambda v: json.loads(v.decode("utf-8")),
            "key_deserializer": lambda k: k.decode("utf-8") if k else None,
        }
        
        if self.security_protocol != "PLAINTEXT":
            config["security_protocol"] = self.security_protocol
            if self.sasl_mechanism:
                config["sasl_mechanism"] = self.sasl_mechanism
                config["sasl_plain_username"] = self.sasl_username
                config["sasl_plain_password"] = self.sasl_password
        
        return config


@dataclass
class TopicConfig:
    """Kafka topic configuration"""
    name: str
    num_partitions: int = 6
    replication_factor: int = 3
    retention_ms: int = 604800000  # 7 days
    retention_bytes: int = -1  # No limit
    segment_bytes: int = 1073741824  # 1GB
    cleanup_policy: str = "delete"
    compression_type: str = "lz4"
    min_isr: int = 2
    
    def to_kafka_config(self) -> Dict[str, Any]:
        """Convert to Kafka topic configuration"""
        return {
            "retention.ms": str(self.retention_ms),
            "retention.bytes": str(self.retention_bytes),
            "segment.bytes": str(self.segment_bytes),
            "cleanup.policy": self.cleanup_policy,
            "compression.type": self.compression_type,
            "min.insync.replicas": str(self.min_isr),
        }


class KafkaTopicManager:
    """Manages Kafka topics lifecycle"""
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self._admin_client: Optional[KafkaAdminClient] = None
    
    def connect(self):
        """Initialize admin client"""
        self._admin_client = KafkaAdminClient(
            bootstrap_servers=self.config.bootstrap_servers,
            client_id=f"{self.config.client_id}-admin"
        )
    
    def disconnect(self):
        """Close admin client"""
        if self._admin_client:
            self._admin_client.close()
            self._admin_client = None
    
    def create_topic(
        self,
        topic_config: TopicConfig,
        ignore_exists: bool = True
    ) -> bool:
        """Create a Kafka topic"""
        try:
            new_topic = NewTopic(
                name=topic_config.name,
                num_partitions=topic_config.num_partitions,
                replication_factor=topic_config.replication_factor,
                topic_configs=topic_config.to_kafka_config()
            )
            
            self._admin_client.create_topics([new_topic])
            logger.info(f"Created topic: {topic_config.name}")
            return True
            
        except TopicAlreadyExistsError:
            if ignore_exists:
                logger.debug(f"Topic {topic_config.name} already exists")
                return True
            raise
        except Exception as e:
            logger.exception(f"Failed to create topic {topic_config.name}: {e}")
            raise
    
    def create_topics(self, topic_configs: List[TopicConfig]) -> Dict[str, bool]:
        """Create multiple topics"""
        results = {}
        for config in topic_configs:
            try:
                results[config.name] = self.create_topic(config)
            except Exception as e:
                logger.exception(f"Failed to create topic {config.name}: {e}")
                results[config.name] = False
        return results
    
    def delete_topic(self, topic_name: str) -> bool:
        """Delete a Kafka topic"""
        try:
            self._admin_client.delete_topics([topic_name])
            logger.info(f"Deleted topic: {topic_name}")
            return True
        except Exception as e:
            logger.exception(f"Failed to delete topic {topic_name}: {e}")
            return False
    
    def list_topics(self) -> List[str]:
        """List all topics"""
        return list(self._admin_client.list_topics())
    
    def describe_topic(self, topic_name: str) -> Dict[str, Any]:
        """Get topic description"""
        return self._admin_client.describe_topics([topic_name])
    
    def alter_topic_config(self, topic_name: str, config: Dict[str, Any]) -> bool:
        """Alter topic configuration"""
        try:
            # Convert config values to strings
            str_config = {k: str(v) for k, v in config.items()}
            self._admin_client.alter_configs({topic_name: str_config})
            return True
        except Exception as e:
            logger.exception(f"Failed to alter topic {topic_name} config: {e}")
            return False


class KafkaProducerWrapper:
    """
    Async wrapper for Kafka producer with enhanced features.
    """
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self._producer: Optional[KafkaProducer] = None
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def connect(self):
        """Initialize producer"""
        self._producer = KafkaProducer(**self.config.producer_config)
        logger.info("Kafka producer connected")
    
    def disconnect(self):
        """Close producer"""
        if self._producer:
            self._producer.close()
            self._producer = None
        self._executor.shutdown(wait=True)
        logger.info("Kafka producer disconnected")
    
    async def send(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None
    ) -> Any:
        """
        Send a message to Kafka topic.
        
        Args:
            topic: Target topic
            value: Message value
            key: Message key for partitioning
            headers: Message headers
            partition: Specific partition (optional)
            timestamp_ms: Message timestamp
            
        Returns:
            RecordMetadata
        """
        loop = asyncio.get_event_loop()
        
        # Convert headers to Kafka format
        kafka_headers = [(k, v.encode()) for k, v in headers.items()] if headers else None
        
        future = self._producer.send(
            topic=topic,
            value=value,
            key=key,
            headers=kafka_headers,
            partition=partition,
            timestamp_ms=timestamp_ms
        )
        
        # Run in executor for async operation
        return await loop.run_in_executor(self._executor, future.get)
    
    async def send_batch(
        self,
        topic: str,
        messages: List[Dict[str, Any]],
        key_extractor: Optional[Callable[[Dict], str]] = None
    ) -> List[Any]:
        """
        Send multiple messages in batch.
        
        Args:
            topic: Target topic
            messages: List of messages
            key_extractor: Function to extract key from message
            
        Returns:
            List of RecordMetadata
        """
        futures = []
        for msg in messages:
            key = key_extractor(msg) if key_extractor else None
            future = self._producer.send(topic, value=msg, key=key)
            futures.append(future)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: [f.get() for f in futures]
        )
    
    def flush(self):
        """Flush pending messages"""
        self._producer.flush()


class KafkaConsumerWrapper:
    """
    Async wrapper for Kafka consumer with enhanced features.
    """
    
    def __init__(
        self,
        config: KafkaConfig,
        topics: List[str],
        group_id: Optional[str] = None
    ):
        self.config = config
        self.topics = topics
        self.group_id = group_id or config.group_id
        self._consumer: Optional[KafkaConsumer] = None
        self._running = False
        self._executor = ThreadPoolExecutor(max_workers=2)
    
    def connect(self):
        """Initialize consumer"""
        consumer_config = self.config.consumer_config
        consumer_config["group_id"] = self.group_id
        
        self._consumer = KafkaConsumer(
            *self.topics,
            **consumer_config
        )
        logger.info(f"Kafka consumer connected to topics: {self.topics}")
    
    def disconnect(self):
        """Close consumer"""
        self._running = False
        if self._consumer:
            self._consumer.close()
            self._consumer = None
        self._executor.shutdown(wait=True)
        logger.info("Kafka consumer disconnected")
    
    async def consume(
        self,
        handler: Callable[[Dict[str, Any], Dict[str, Any]], asyncio.Coroutine],
        error_handler: Optional[Callable[[Exception], None]] = None
    ):
        """
        Consume messages with async handler.
        
        Args:
            handler: Async callback(message, metadata)
            error_handler: Error callback(exception)
        """
        self._running = True
        loop = asyncio.get_event_loop()
        
        while self._running:
            try:
                # Poll for messages (blocking in executor)
                records = await loop.run_in_executor(
                    self._executor,
                    lambda: self._consumer.poll(timeout_ms=1000)
                )
                
                for topic_partition, messages in records.items():
                    for message in messages:
                        metadata = {
                            "topic": message.topic,
                            "partition": message.partition,
                            "offset": message.offset,
                            "timestamp": message.timestamp,
                            "key": message.key,
                            "headers": dict(message.headers) if message.headers else {},
                        }
                        
                        try:
                            await handler(message.value, metadata)
                        except Exception as e:
                            logger.exception(f"Error processing message: {e}")
                            if error_handler:
                                error_handler(e)
                
            except Exception as e:
                logger.exception(f"Error in consumer loop: {e}")
                if error_handler:
                    error_handler(e)
    
    def pause(self, partitions: Optional[List[TopicPartition]] = None):
        """Pause consumption"""
        if partitions:
            self._consumer.pause(*partitions)
        else:
            self._consumer.pause(*self._consumer.assignment())
    
    def resume(self, partitions: Optional[List[TopicPartition]] = None):
        """Resume consumption"""
        if partitions:
            self._consumer.resume(*partitions)
        else:
            self._consumer.resume(*self._consumer.assignment())
    
    def seek_to_beginning(self, partitions: Optional[List[TopicPartition]] = None):
        """Seek to beginning of partitions"""
        if partitions:
            self._consumer.seek_to_beginning(*partitions)
        else:
            self._consumer.seek_to_beginning()
    
    def seek_to_end(self, partitions: Optional[List[TopicPartition]] = None):
        """Seek to end of partitions"""
        if partitions:
            self._consumer.seek_to_end(*partitions)
        else:
            self._consumer.seek_to_end()
    
    def commit_sync(self):
        """Synchronous commit"""
        self._consumer.commit_sync()


class KafkaClient:
    """
    Unified Kafka client for ResilienceAI.
    Combines producer, consumer, and admin functionality.
    """
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.topic_manager = KafkaTopicManager(config)
        self.producer: Optional[KafkaProducerWrapper] = None
        self._consumers: Dict[str, KafkaConsumerWrapper] = {}
    
    def connect(self):
        """Initialize all components"""
        self.topic_manager.connect()
        
        self.producer = KafkaProducerWrapper(self.config)
        self.producer.connect()
        
        logger.info("Kafka client connected")
    
    def disconnect(self):
        """Clean up all components"""
        for consumer in self._consumers.values():
            consumer.disconnect()
        self._consumers.clear()
        
        if self.producer:
            self.producer.disconnect()
            self.producer = None
        
        self.topic_manager.disconnect()
        logger.info("Kafka client disconnected")
    
    def create_consumer(
        self,
        name: str,
        topics: List[str],
        group_id: Optional[str] = None
    ) -> KafkaConsumerWrapper:
        """Create and register a consumer"""
        consumer = KafkaConsumerWrapper(
            self.config,
            topics,
            group_id
        )
        consumer.connect()
        self._consumers[name] = consumer
        return consumer
    
    def remove_consumer(self, name: str):
        """Remove and close a consumer"""
        if name in self._consumers:
            self._consumers[name].disconnect()
            del self._consumers[name]


# ResilienceAI Kafka Topics Configuration
RESILIENCE_AI_KAFKA_TOPICS = {
    # Event Sourcing Topics
    "events.incidents": TopicConfig(
        name="events.incidents",
        num_partitions=12,
        replication_factor=3,
        retention_ms=2592000000,  # 30 days
        cleanup_policy="compact,delete",
    ),
    "events.alerts": TopicConfig(
        name="events.alerts",
        num_partitions=6,
        replication_factor=3,
        retention_ms=604800000,  # 7 days
    ),
    "events.system": TopicConfig(
        name="events.system",
        num_partitions=3,
        replication_factor=3,
        retention_ms=86400000,  # 1 day
    ),
    
    # Audit Log Topics
    "audit.commands": TopicConfig(
        name="audit.commands",
        num_partitions=6,
        replication_factor=3,
        retention_ms=7776000000,  # 90 days
    ),
    "audit.queries": TopicConfig(
        name="audit.queries",
        num_partitions=6,
        replication_factor=3,
        retention_ms=2592000000,  # 30 days
    ),
    
    # Analytics Topics
    "analytics.metrics": TopicConfig(
        name="analytics.metrics",
        num_partitions=12,
        replication_factor=3,
        retention_ms=604800000,  # 7 days
    ),
    "analytics.events": TopicConfig(
        name="analytics.events",
        num_partitions=24,
        replication_factor=3,
        retention_ms=86400000,  # 1 day
    ),
    
    # Stream Processing Topics
    "streams.incident-enrichment": TopicConfig(
        name="streams.incident-enrichment",
        num_partitions=12,
        replication_factor=3,
        retention_ms=3600000,  # 1 hour - intermediate topic
    ),
    "streams.alert-aggregation": TopicConfig(
        name="streams.alert-aggregation",
        num_partitions=6,
        replication_factor=3,
        retention_ms=3600000,
    ),
}
```

### 4.2 Kafka Streams Processing

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/kafka_streams.py
"""
Kafka Streams-style processing for ResilienceAI
Implements stream processing patterns using Kafka.
"""
import json
import asyncio
import logging
from typing import Dict, Any, Callable, Optional, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime, timedelta

from kafka import KafkaConsumer, KafkaProducer


logger = logging.getLogger(__name__)


@dataclass
class StreamConfig:
    """Stream processing configuration"""
    application_id: str
    bootstrap_servers: List[str]
    input_topics: List[str]
    output_topic: Optional[str] = None
    group_id: Optional[str] = None
    processing_guarantee: str = "at_least_once"
    commit_interval_ms: int = 30000
    cache_max_bytes_buffering: int = 10485760  # 10MB


class KStream:
    """
    Kafka Streams-style stream abstraction.
    Provides functional stream processing operations.
    """
    
    def __init__(self, topic: str, config: StreamConfig):
        self.topic = topic
        self.config = config
        self._operations: List[Callable] = []
        self._consumer: Optional[KafkaConsumer] = None
        self._producer: Optional[KafkaProducer] = None
    
    def filter(self, predicate: Callable[[Dict], bool]) -> "KStream":
        """Filter messages based on predicate"""
        self._operations.append(("filter", predicate))
        return self
    
    def map(self, mapper: Callable[[Dict], Dict]) -> "KStream":
        """Transform each message"""
        self._operations.append(("map", mapper))
        return self
    
    def flat_map(self, mapper: Callable[[Dict], List[Dict]]) -> "KStream":
        """Transform each message to multiple messages"""
        self._operations.append(("flat_map", mapper))
        return self
    
    def peek(self, action: Callable[[Dict], None]) -> "KStream":
        """Perform side effect without modifying message"""
        self._operations.append(("peek", action))
        return self
    
    def branch(
        self,
        *predicates: Callable[[Dict], bool]
    ) -> List["KStream"]:
        """Branch stream based on predicates"""
        branches = [KStream(self.topic, self.config) for _ in predicates]
        self._operations.append(("branch", predicates, branches))
        return branches
    
    def to(self, topic: str):
        """Send output to topic"""
        self._operations.append(("to", topic))
    
    def foreach(self, action: Callable[[Dict], None]):
        """Perform action for each message"""
        self._operations.append(("foreach", action))
    
    def process(self, processor: Callable[[Dict, Dict], None]):
        """Custom processor with metadata"""
        self._operations.append(("process", processor))


class KTable:
    """
    Kafka Streams-style table abstraction.
    Provides stateful stream processing with changelog.
    """
    
    def __init__(self, name: str, config: StreamConfig):
        self.name = name
        self.config = config
        self._state: Dict[str, Any] = {}
        self._changelog_topic = f"{name}-changelog"
    
    def get(self, key: str) -> Any:
        """Get value by key"""
        return self._state.get(key)
    
    def put(self, key: str, value: Any):
        """Put value by key"""
        self._state[key] = value
        # TODO: Write to changelog
    
    def delete(self, key: str):
        """Delete key"""
        if key in self._state:
            del self._state[key]
            # TODO: Write tombstone to changelog


class StreamProcessor:
    """
    Stream processor for ResilienceAI.
    Implements common stream processing patterns.
    """
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self._streams: List[KStream] = []
        self._tables: Dict[str, KTable] = {}
        self._running = False
    
    def stream(self, topic: str) -> KStream:
        """Create a new stream from topic"""
        kstream = KStream(topic, self.config)
        self._streams.append(kstream)
        return kstream
    
    def table(self, name: str) -> KTable:
        """Create or get a table"""
        if name not in self._tables:
            self._tables[name] = KTable(name, self.config)
        return self._tables[name]
    
    async def start(self):
        """Start stream processing"""
        self._running = True
        
        # Initialize consumers and producers
        for stream in self._streams:
            await self._process_stream(stream)
    
    async def _process_stream(self, stream: KStream):
        """Process a single stream"""
        consumer = KafkaConsumer(
            stream.topic,
            bootstrap_servers=self.config.bootstrap_servers,
            group_id=self.config.group_id or f"{self.config.application_id}-group",
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))
        )
        
        producer = KafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        
        try:
            while self._running:
                records = consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in records.items():
                    for message in messages:
                        value = message.value
                        
                        # Apply operations
                        for op_name, *op_args in stream._operations:
                            value = await self._apply_operation(
                                op_name, op_args, value, producer
                            )
                            
                            if value is None:
                                break  # Message filtered out
        
        finally:
            consumer.close()
            producer.close()
    
    async def _apply_operation(
        self,
        op_name: str,
        op_args: List,
        value: Dict,
        producer: KafkaProducer
    ) -> Optional[Dict]:
        """Apply a single operation"""
        if op_name == "filter":
            predicate = op_args[0]
            return value if predicate(value) else None
        
        elif op_name == "map":
            mapper = op_args[0]
            return mapper(value)
        
        elif op_name == "flat_map":
            mapper = op_args[0]
            return mapper(value)  # Returns list
        
        elif op_name == "peek":
            action = op_args[0]
            action(value)
            return value
        
        elif op_name == "to":
            topic = op_args[0]
            producer.send(topic, value)
            return value
        
        elif op_name == "foreach":
            action = op_args[0]
            action(value)
            return None
        
        return value
    
    def stop(self):
        """Stop stream processing"""
        self._running = False


class WindowedAggregation:
    """
    Windowed aggregation for stream processing.
    Supports tumbling, hopping, and session windows.
    """
    
    def __init__(self, window_size_ms: int, advance_ms: Optional[int] = None):
        self.window_size_ms = window_size_ms
        self.advance_ms = advance_ms or window_size_ms
        self._windows: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._window_start_times: Dict[str, int] = {}
    
    def add(self, key: str, value: Any, timestamp_ms: int):
        """Add value to appropriate window"""
        window_key = self._get_window_key(timestamp_ms)
        
        if window_key not in self._windows[key]:
            self._windows[key][window_key] = []
        
        self._windows[key][window_key].append({
            "value": value,
            "timestamp": timestamp_ms
        })
    
    def _get_window_key(self, timestamp_ms: int) -> str:
        """Get window key for timestamp"""
        window_start = (timestamp_ms // self.window_size_ms) * self.window_size_ms
        return str(window_start)
    
    def get_window(self, key: str, window_key: str) -> List[Dict]:
        """Get values in a specific window"""
        return self._windows[key].get(window_key, [])
    
    def get_closed_windows(self, current_timestamp_ms: int) -> List[Tuple[str, str]]:
        """Get windows that have closed"""
        closed = []
        for key, windows in self._windows.items():
            for window_key in list(windows.keys()):
                window_end = int(window_key) + self.window_size_ms
                if window_end < current_timestamp_ms:
                    closed.append((key, window_key))
        return closed
    
    def remove_window(self, key: str, window_key: str):
        """Remove a closed window"""
        if window_key in self._windows[key]:
            del self._windows[key][window_key]


# Example: Incident Aggregation Stream
class IncidentAggregationProcessor(StreamProcessor):
    """
    Stream processor for aggregating incidents.
    Demonstrates windowed aggregation pattern.
    """
    
    def __init__(self, config: StreamConfig):
        super().__init__(config)
        self.aggregation = WindowedAggregation(
            window_size_ms=60000,  # 1 minute windows
            advance_ms=30000  # 30 second advance
        )
    
    def setup(self):
        """Setup incident aggregation pipeline"""
        # Create input stream
        incident_stream = self.stream("events.incidents")
        
        # Filter critical incidents
        critical_stream = incident_stream.filter(
            lambda msg: msg.get("severity") == "CRITICAL"
        )
        
        # Enrich with metadata
        enriched_stream = critical_stream.map(self._enrich_incident)
        
        # Aggregate by service
        enriched_stream.process(self._aggregate_by_service)
        
        # Output to analytics topic
        enriched_stream.to("analytics.incident-metrics")
    
    def _enrich_incident(self, incident: Dict) -> Dict:
        """Enrich incident with additional metadata"""
        return {
            **incident,
            "enriched_at": datetime.utcnow().isoformat(),
            "processing_version": "1.0.0",
        }
    
    def _aggregate_by_service(self, incident: Dict, metadata: Dict):
        """Aggregate incidents by service"""
        service = incident.get("service")
        timestamp = metadata.get("timestamp", 0)
        
        self.aggregation.add(service, incident, timestamp)
        
        # Check for closed windows
        closed = self.aggregation.get_closed_windows(timestamp)
        for key, window_key in closed:
            values = self.aggregation.get_window(key, window_key)
            
            # Emit aggregated metrics
            metrics = {
                "service": key,
                "window_start": window_key,
                "incident_count": len(values),
                "severities": self._count_by_severity(values),
            }
            
            # TODO: Send to output topic
            
            self.aggregation.remove_window(key, window_key)
    
    def _count_by_severity(self, values: List[Dict]) -> Dict[str, int]:
        """Count incidents by severity"""
        counts = defaultdict(int)
        for v in values:
            severity = v["value"].get("severity", "UNKNOWN")
            counts[severity] += 1
        return dict(counts)
```

---

## 5. Producer/Consumer Patterns

### 5.1 Producer Patterns

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/producer_patterns.py
"""
Producer Patterns for ResilienceAI
Implements various message publishing patterns.
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class PublishPattern(Enum):
    """Available publish patterns"""
    SIMPLE = "simple"
    BATCH = "batch"
    TRANSACTIONAL = "transactional"
    REQUEST_REPLY = "request_reply"
    PRIORITY = "priority"
    DELAYED = "delayed"


@dataclass
class PublishResult:
    """Result of publish operation"""
    success: bool
    message_id: str
    timestamp: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageProducer:
    """
    Base message producer with multiple publishing patterns.
    """
    
    def __init__(self, client, default_exchange: str = ""):
        self.client = client
        self.default_exchange = default_exchange
        self._publish_handlers: Dict[PublishPattern, Callable] = {
            PublishPattern.SIMPLE: self._publish_simple,
            PublishPattern.BATCH: self._publish_batch,
            PublishPattern.PRIORITY: self._publish_priority,
            PublishPattern.DELAYED: self._publish_delayed,
        }
    
    async def publish(
        self,
        message: Dict[str, Any],
        routing_key: str,
        pattern: PublishPattern = PublishPattern.SIMPLE,
        exchange: Optional[str] = None,
        **kwargs
    ) -> PublishResult:
        """
        Publish message using specified pattern.
        
        Args:
            message: Message payload
            routing_key: Routing key
            pattern: Publishing pattern
            exchange: Target exchange (uses default if not specified)
            **kwargs: Pattern-specific options
            
        Returns:
            PublishResult with status and metadata
        """
        exchange = exchange or self.default_exchange
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        try:
            handler = self._publish_handlers.get(pattern)
            if not handler:
                raise ValueError(f"Unknown publish pattern: {pattern}")
            
            await handler(message, routing_key, exchange, **kwargs)
            
            return PublishResult(
                success=True,
                message_id=message_id,
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.exception(f"Failed to publish message: {e}")
            return PublishResult(
                success=False,
                message_id=message_id,
                timestamp=timestamp,
                error=str(e)
            )
    
    async def _publish_simple(
        self,
        message: Dict[str, Any],
        routing_key: str,
        exchange: str,
        **kwargs
    ):
        """Simple publish pattern"""
        metadata = MessageMetadata(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            source_service=kwargs.get("source_service", "unknown"),
            event_type=kwargs.get("event_type")
        )
        
        await self.client.publish(
            exchange_name=exchange,
            routing_key=routing_key,
            message=message,
            metadata=metadata
        )
    
    async def _publish_batch(
        self,
        messages: List[Dict[str, Any]],
        routing_key: str,
        exchange: str,
        batch_size: int = 100,
        **kwargs
    ):
        """Batch publish pattern"""
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            
            # Publish batch
            for msg in batch:
                await self._publish_simple(msg, routing_key, exchange, **kwargs)
            
            # Small delay between batches
            await asyncio.sleep(0.01)
    
    async def _publish_priority(
        self,
        message: Dict[str, Any],
        routing_key: str,
        exchange: str,
        priority: int = 5,
        **kwargs
    ):
        """Priority publish pattern"""
        metadata = MessageMetadata(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            source_service=kwargs.get("source_service", "unknown"),
            event_type=kwargs.get("event_type"),
            priority=priority
        )
        
        await self.client.publish(
            exchange_name=exchange,
            routing_key=routing_key,
            message=message,
            metadata=metadata
        )
    
    async def _publish_delayed(
        self,
        message: Dict[str, Any],
        routing_key: str,
        exchange: str,
        delay_ms: int = 0,
        **kwargs
    ):
        """Delayed publish pattern"""
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000)
        
        await self._publish_simple(message, routing_key, exchange, **kwargs)


class EventPublisher:
    """
    Domain event publisher for ResilienceAI.
    Publishes business events with proper routing.
    """
    
    EVENT_EXCHANGE = "resilience.topic"
    
    # Event type to routing key mapping
    EVENT_ROUTING_KEYS = {
        # Incident events
        "incident.created": "incident.created",
        "incident.updated": "incident.updated",
        "incident.resolved": "incident.resolved",
        "incident.escalated": "incident.escalated",
        "incident.assigned": "incident.assigned",
        
        # Alert events
        "alert.triggered": "alert.triggered",
        "alert.acknowledged": "alert.acknowledged",
        "alert.resolved": "alert.resolved",
        "alert.suppressed": "alert.suppressed",
        
        # System events
        "system.startup": "system.startup",
        "system.shutdown": "system.shutdown",
        "system.error": "system.error",
        "system.metric": "system.metric",
        
        # User events
        "user.login": "user.login",
        "user.logout": "user.logout",
        "user.action": "user.action",
    }
    
    def __init__(self, client):
        self.client = client
        self.producer = MessageProducer(client, self.EVENT_EXCHANGE)
    
    async def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        priority: int = 0
    ) -> PublishResult:
        """
        Publish a domain event.
        
        Args:
            event_type: Type of event (must be in EVENT_ROUTING_KEYS)
            payload: Event payload
            correlation_id: Optional correlation ID
            priority: Message priority (0-10)
            
        Returns:
            PublishResult
        """
        routing_key = self.EVENT_ROUTING_KEYS.get(event_type)
        if not routing_key:
            raise ValueError(f"Unknown event type: {event_type}")
        
        # Build event envelope
        event = {
            "event_type": event_type,
            "payload": payload,
            "metadata": {
                "published_at": datetime.utcnow().isoformat(),
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "event_id": str(uuid.uuid4()),
                "version": "1.0"
            }
        }
        
        pattern = PublishPattern.PRIORITY if priority > 0 else PublishPattern.SIMPLE
        
        return await self.producer.publish(
            message=event,
            routing_key=routing_key,
            pattern=pattern,
            priority=priority,
            source_service="resilience-ai",
            event_type=event_type
        )
    
    async def publish_incident_created(
        self,
        incident_id: str,
        service: str,
        severity: str,
        description: str,
        **kwargs
    ) -> PublishResult:
        """Publish incident created event"""
        return await self.publish_event(
            event_type="incident.created",
            payload={
                "incident_id": incident_id,
                "service": service,
                "severity": severity,
                "description": description,
                **kwargs
            },
            priority=5 if severity == "CRITICAL" else 0
        )
    
    async def publish_alert_triggered(
        self,
        alert_id: str,
        rule_id: str,
        severity: str,
        message: str,
        **kwargs
    ) -> PublishResult:
        """Publish alert triggered event"""
        return await self.publish_event(
            event_type="alert.triggered",
            payload={
                "alert_id": alert_id,
                "rule_id": rule_id,
                "severity": severity,
                "message": message,
                **kwargs
            },
            priority=10 if severity == "CRITICAL" else 5
        )


class CommandPublisher:
    """
    Command publisher for saga orchestration.
    Publishes commands to services.
    """
    
    COMMAND_EXCHANGE = "resilience.direct"
    
    def __init__(self, client):
        self.client = client
        self.producer = MessageProducer(client, self.COMMAND_EXCHANGE)
    
    async def send_command(
        self,
        service: str,
        command: str,
        payload: Dict[str, Any],
        saga_id: Optional[str] = None,
        step_id: Optional[str] = None,
        timeout_ms: int = 30000
    ) -> PublishResult:
        """
        Send a command to a service.
        
        Args:
            service: Target service name
            command: Command name
            payload: Command payload
            saga_id: Associated saga ID
            step_id: Saga step ID
            timeout_ms: Command timeout
            
        Returns:
            PublishResult
        """
        routing_key = f"{service}.command.{command}"
        
        command_message = {
            "command": command,
            "service": service,
            "payload": payload,
            "saga_id": saga_id,
            "step_id": step_id,
            "timeout_ms": timeout_ms,
            "sent_at": datetime.utcnow().isoformat(),
            "command_id": str(uuid.uuid4())
        }
        
        return await self.producer.publish(
            message=command_message,
            routing_key=routing_key,
            pattern=PublishPattern.SIMPLE,
            source_service="saga-orchestrator"
        )


# Import for type hints
from .rabbitmq_client import MessageMetadata
```

### 5.2 Consumer Patterns

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/consumer_patterns.py
"""
Consumer Patterns for ResilienceAI
Implements various message consumption patterns.
"""
import asyncio
import logging
from typing import Dict, Any, Callable, Optional, List, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import traceback


logger = logging.getLogger(__name__)

T = TypeVar('T')


class ConsumerPattern(Enum):
    """Available consumer patterns"""
    SIMPLE = "simple"
    COMPETING = "competing"
    PUB_SUB = "pub_sub"
    WORKER_POOL = "worker_pool"
    CIRCUIT_BREAKER = "circuit_breaker"
    RATE_LIMITED = "rate_limited"


@dataclass
class ConsumeResult:
    """Result of message consumption"""
    success: bool
    message_id: str
    processing_time_ms: float
    error: Optional[str] = None
    retry_count: int = 0


class MessageHandler(ABC):
    """Abstract base class for message handlers"""
    
    @abstractmethod
    async def handle(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """
        Handle a message.
        
        Args:
            message: Message payload
            metadata: Message metadata
            
        Returns:
            True if handled successfully
        """
        pass
    
    async def on_error(
        self,
        message: Dict[str, Any],
        metadata: Dict[str, Any],
        error: Exception
    ):
        """Called when handling fails"""
        logger.exception(f"Error handling message: {error}")


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.
    """
    
    class State(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._state = self.State.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> State:
        return self._state
    
    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            if self._state == self.State.OPEN:
                if self._should_attempt_reset():
                    self._state = self.State.HALF_OPEN
                    self._half_open_calls = 0
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")
            
            if self._state == self.State.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerOpenError("Circuit breaker HALF_OPEN limit reached")
                self._half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self._last_failure_time is None:
            return True
        elapsed = (datetime.utcnow() - self._last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            if self._state == self.State.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.half_open_max_calls:
                    self._state = self.State.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    logger.info("Circuit breaker CLOSED")
            else:
                self._failure_count = 0
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.utcnow()
            
            if self._state == self.State.HALF_OPEN:
                self._state = self.State.OPEN
                logger.warning("Circuit breaker OPEN (half-open failure)")
            elif self._failure_count >= self.failure_threshold:
                self._state = self.State.OPEN
                logger.warning(f"Circuit breaker OPEN ({self._failure_count} failures)")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class RateLimiter:
    """
    Token bucket rate limiter.
    """
    
    def __init__(self, rate: float, burst: int):
        """
        Initialize rate limiter.
        
        Args:
            rate: Tokens per second
            burst: Maximum bucket size
        """
        self.rate = rate
        self.burst = burst
        self._tokens = burst
        self._last_update = datetime.utcnow()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token, waiting if necessary"""
        while True:
            async with self._lock:
                now = datetime.utcnow()
                elapsed = (now - self._last_update).total_seconds()
                self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
                self._last_update = now
                
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
            
            # Wait before retrying
            await asyncio.sleep(0.1)


class Consumer:
    """
    Message consumer with pattern support.
    """
    
    def __init__(
        self,
        client,
        queue_name: str,
        handler: MessageHandler,
        pattern: ConsumerPattern = ConsumerPattern.SIMPLE,
        **kwargs
    ):
        self.client = client
        self.queue_name = queue_name
        self.handler = handler
        self.pattern = pattern
        self.options = kwargs
        
        self._consumer_tag: Optional[str] = None
        self._running = False
        self._circuit_breaker: Optional[CircuitBreaker] = None
        self._rate_limiter: Optional[RateLimiter] = None
        
        # Initialize pattern-specific components
        self._setup_pattern()
    
    def _setup_pattern(self):
        """Setup pattern-specific components"""
        if self.pattern == ConsumerPattern.CIRCUIT_BREAKER:
            self._circuit_breaker = CircuitBreaker(
                failure_threshold=self.options.get("failure_threshold", 5),
                recovery_timeout=self.options.get("recovery_timeout", 30.0)
            )
        
        elif self.pattern == ConsumerPattern.RATE_LIMITED:
            self._rate_limiter = RateLimiter(
                rate=self.options.get("rate", 100.0),
                burst=self.options.get("burst", 100)
            )
        
        elif self.pattern == ConsumerPattern.WORKER_POOL:
            self._worker_count = self.options.get("worker_count", 5)
            self._worker_queue: Optional[asyncio.Queue] = None
    
    async def start(self):
        """Start consuming messages"""
        self._running = True
        
        if self.pattern == ConsumerPattern.WORKER_POOL:
            await self._start_worker_pool()
        else:
            self._consumer_tag = await self.client.consume(
                queue_name=self.queue_name,
                handler=self._wrap_handler
            )
    
    async def stop(self):
        """Stop consuming messages"""
        self._running = False
        if self._consumer_tag:
            await self.client.stop_consumer(self._consumer_tag)
    
    async def _wrap_handler(
        self,
        message: Dict[str, Any],
        metadata: Any
    ):
        """Wrap handler with pattern-specific logic"""
        start_time = datetime.utcnow()
        
        try:
            # Apply rate limiting
            if self._rate_limiter:
                await self._rate_limiter.acquire()
            
            # Apply circuit breaker
            if self._circuit_breaker:
                success = await self._circuit_breaker.call(
                    self.handler.handle, message, metadata
                )
            else:
                success = await self.handler.handle(message, metadata)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ConsumeResult(
                success=success,
                message_id=getattr(metadata, 'message_id', 'unknown'),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            await self.handler.on_error(message, metadata, e)
            
            return ConsumeResult(
                success=False,
                message_id=getattr(metadata, 'message_id', 'unknown'),
                processing_time_ms=processing_time,
                error=str(e)
            )
    
    async def _start_worker_pool(self):
        """Start worker pool pattern"""
        self._worker_queue = asyncio.Queue(maxsize=self._worker_count * 2)
        
        # Start workers
        workers = [
            asyncio.create_task(self._worker_loop())
            for _ in range(self._worker_count)
        ]
        
        # Start message consumer
        self._consumer_tag = await self.client.consume(
            queue_name=self.queue_name,
            handler=self._enqueue_message
        )
        
        # Wait for workers
        await asyncio.gather(*workers)
    
    async def _enqueue_message(self, message: Dict, metadata: Any):
        """Enqueue message for worker processing"""
        await self._worker_queue.put((message, metadata))
    
    async def _worker_loop(self):
        """Worker loop for processing messages"""
        while self._running:
            try:
                message, metadata = await asyncio.wait_for(
                    self._worker_queue.get(),
                    timeout=1.0
                )
                await self._wrap_handler(message, metadata)
            except asyncio.TimeoutError:
                continue


class CompetingConsumerGroup:
    """
    Competing consumer pattern for load balancing.
    Multiple consumers process messages from the same queue.
    """
    
    def __init__(
        self,
        client_factory,
        queue_name: str,
        handler: MessageHandler,
        consumer_count: int = 3
    ):
        self.client_factory = client_factory
        self.queue_name = queue_name
        self.handler = handler
        self.consumer_count = consumer_count
        self._consumers: List[Consumer] = []
    
    async def start(self):
        """Start all consumers in the group"""
        for i in range(self.consumer_count):
            client = self.client_factory()
            await client.connect()
            
            consumer = Consumer(
                client=client,
                queue_name=self.queue_name,
                handler=self.handler,
                pattern=ConsumerPattern.SIMPLE
            )
            
            await consumer.start()
            self._consumers.append(consumer)
        
        logger.info(f"Started {self.consumer_count} competing consumers on {self.queue_name}")
    
    async def stop(self):
        """Stop all consumers"""
        for consumer in self._consumers:
            await consumer.stop()
        self._consumers.clear()


# Import for type hints
from .rabbitmq_client import MessageMetadata
```

---

## 6. Message Routing

### 6.1 Router Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/message_router.py
"""
Message Router for ResilienceAI
Implements intelligent message routing with content-based routing.
"""
import re
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Available routing strategies"""
    DIRECT = "direct"
    TOPIC = "topic"
    HEADER = "header"
    CONTENT = "content"
    PRIORITY = "priority"
    LOAD_BALANCE = "load_balance"


@dataclass
class Route:
    """Route definition"""
    target_exchange: str
    routing_key: str
    priority: int = 0
    conditions: Optional[List[Dict[str, Any]]] = None
    transformations: Optional[List[Dict[str, Any]]] = None


class RouteCondition(ABC):
    """Abstract base class for route conditions"""
    
    @abstractmethod
    def evaluate(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Evaluate condition against message"""
        pass


class HeaderCondition(RouteCondition):
    """Condition based on message headers"""
    
    def __init__(self, header: str, value: Any, operator: str = "equals"):
        self.header = header
        self.value = value
        self.operator = operator
    
    def evaluate(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        headers = metadata.get("headers", {})
        actual_value = headers.get(self.header)
        
        if self.operator == "equals":
            return actual_value == self.value
        elif self.operator == "contains":
            return self.value in str(actual_value)
        elif self.operator == "regex":
            return bool(re.match(self.value, str(actual_value)))
        elif self.operator == "in":
            return actual_value in self.value
        
        return False


class ContentCondition(RouteCondition):
    """Condition based on message content"""
    
    def __init__(self, path: str, value: Any, operator: str = "equals"):
        self.path = path
        self.value = value
        self.operator = operator
    
    def evaluate(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        actual_value = self._get_nested_value(message, self.path)
        
        if self.operator == "equals":
            return actual_value == self.value
        elif self.operator == "gt":
            return actual_value > self.value
        elif self.operator == "gte":
            return actual_value >= self.value
        elif self.operator == "lt":
            return actual_value < self.value
        elif self.operator == "lte":
            return actual_value <= self.value
        elif self.operator == "in":
            return actual_value in self.value
        elif self.operator == "contains":
            return self.value in str(actual_value)
        elif self.operator == "exists":
            return actual_value is not None
        
        return False
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get nested dictionary value by dot-separated path"""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value


class CompositeCondition(RouteCondition):
    """Composite condition with AND/OR logic"""
    
    def __init__(self, conditions: List[RouteCondition], operator: str = "and"):
        self.conditions = conditions
        self.operator = operator
    
    def evaluate(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        if self.operator == "and":
            return all(c.evaluate(message, metadata) for c in self.conditions)
        elif self.operator == "or":
            return any(c.evaluate(message, metadata) for c in self.conditions)
        
        return False


class MessageTransformer(ABC):
    """Abstract base class for message transformers"""
    
    @abstractmethod
    def transform(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Transform message"""
        pass


class FieldMapper(MessageTransformer):
    """Map fields from one structure to another"""
    
    def __init__(self, mappings: Dict[str, str]):
        """
        Initialize field mapper.
        
        Args:
            mappings: Dict of {source_path: target_path}
        """
        self.mappings = mappings
    
    def transform(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for source_path, target_path in self.mappings.items():
            value = self._get_nested_value(message, source_path)
            self._set_nested_value(result, target_path, value)
        return result
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _set_nested_value(self, data: Dict, path: str, value: Any):
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value


class Enricher(MessageTransformer):
    """Enrich message with additional data"""
    
    def __init__(self, enrichments: Dict[str, Any]):
        self.enrichments = enrichments
    
    def transform(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {**message, **self.enrichments}


class FilterFields(MessageTransformer):
    """Filter message fields"""
    
    def __init__(self, fields: List[str], mode: str = "include"):
        """
        Initialize field filter.
        
        Args:
            fields: List of field paths
            mode: "include" or "exclude"
        """
        self.fields = fields
        self.mode = mode
    
    def transform(self, message: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        if self.mode == "include":
            result = {}
            for field in self.fields:
                value = self._get_nested_value(message, field)
                self._set_nested_value(result, field, value)
            return result
        else:  # exclude
            result = dict(message)
            for field in self.fields:
                keys = field.split(".")
                self._delete_nested_value(result, keys)
            return result
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _set_nested_value(self, data: Dict, path: str, value: Any):
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _delete_nested_value(self, data: Dict, keys: List[str]):
        if len(keys) == 1:
            data.pop(keys[0], None)
        elif keys[0] in data:
            self._delete_nested_value(data[keys[0]], keys[1:])


class MessageRouter:
    """
    Intelligent message router for ResilienceAI.
    Routes messages based on content, headers, and priority.
    """
    
    def __init__(self, client):
        self.client = client
        self._routes: List[Route] = []
        self._condition_registry: Dict[str, Callable] = {
            "header": HeaderCondition,
            "content": ContentCondition,
            "composite": CompositeCondition,
        }
        self._transformer_registry: Dict[str, Callable] = {
            "field_mapper": FieldMapper,
            "enricher": Enricher,
            "filter_fields": FilterFields,
        }
    
    def add_route(self, route: Route):
        """Add a route to the router"""
        self._routes.append(route)
        # Sort by priority (highest first)
        self._routes.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_route(self, target_exchange: str, routing_key: str):
        """Remove a route"""
        self._routes = [
            r for r in self._routes
            if not (r.target_exchange == target_exchange and r.routing_key == routing_key)
        ]
    
    async def route(
        self,
        message: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[Route]:
        """
        Route a message to appropriate targets.
        
        Args:
            message: Message payload
            metadata: Message metadata
            
        Returns:
            List of matching routes
        """
        matched_routes = []
        
        for route in self._routes:
            if self._matches_route(route, message, metadata):
                # Apply transformations
                transformed_message = self._apply_transformations(
                    route, message, metadata
                )
                
                # Publish to target
                await self.client.publish(
                    exchange_name=route.target_exchange,
                    routing_key=route.routing_key,
                    message=transformed_message
                )
                
                matched_routes.append(route)
        
        return matched_routes
    
    def _matches_route(
        self,
        route: Route,
        message: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> bool:
        """Check if message matches route conditions"""
        if not route.conditions:
            return True
        
        for condition_def in route.conditions:
            condition = self._build_condition(condition_def)
            if not condition.evaluate(message, metadata):
                return False
        
        return True
    
    def _build_condition(self, condition_def: Dict[str, Any]) -> RouteCondition:
        """Build condition from definition"""
        condition_type = condition_def.get("type", "content")
        condition_class = self._condition_registry.get(condition_type)
        
        if condition_type == "composite":
            sub_conditions = [
                self._build_condition(c) for c in condition_def.get("conditions", [])
            ]
            return condition_class(sub_conditions, condition_def.get("operator", "and"))
        
        return condition_class(
            condition_def.get("path") or condition_def.get("header"),
            condition_def.get("value"),
            condition_def.get("operator", "equals")
        )
    
    def _apply_transformations(
        self,
        route: Route,
        message: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply transformations to message"""
        if not route.transformations:
            return message
        
        result = dict(message)
        for transform_def in route.transformations:
            transformer = self._build_transformer(transform_def)
            result = transformer.transform(result, metadata)
        
        return result
    
    def _build_transformer(self, transform_def: Dict[str, Any]) -> MessageTransformer:
        """Build transformer from definition"""
        transform_type = transform_def.get("type", "enricher")
        transformer_class = self._transformer_registry.get(transform_type)
        
        if transform_type == "field_mapper":
            return transformer_class(transform_def.get("mappings", {}))
        elif transform_type == "enricher":
            return transformer_class(transform_def.get("enrichments", {}))
        elif transform_type == "filter_fields":
            return transformer_class(
                transform_def.get("fields", []),
                transform_def.get("mode", "include")
            )
        
        return transformer_class({})


# ResilienceAI Routing Configuration
RESILIENCE_AI_ROUTES = [
    # Critical incident routing
    Route(
        target_exchange="alerts.topic",
        routing_key="alert.critical.incident",
        priority=10,
        conditions=[
            {"type": "content", "path": "severity", "value": "CRITICAL", "operator": "equals"},
            {"type": "content", "path": "type", "value": "incident", "operator": "equals"},
        ],
        transformations=[
            {"type": "enricher", "enrichments": {"routing_reason": "critical_incident"}}
        ]
    ),
    
    # High priority alert routing
    Route(
        target_exchange="notifications.fanout",
        routing_key="",
        priority=9,
        conditions=[
            {"type": "content", "path": "priority", "value": "HIGH", "operator": "gte"},
        ],
    ),
    
    # Analytics routing
    Route(
        target_exchange="analytics.topic",
        routing_key="analytics.all",
        priority=1,
        conditions=[],
        transformations=[
            {"type": "filter_fields", "fields": ["timestamp", "type", "metrics"], "mode": "include"}
        ]
    ),
    
    # Service-specific routing
    Route(
        target_exchange="resilience.direct",
        routing_key="service.notification",
        priority=5,
        conditions=[
            {"type": "header", "header": "target_service", "value": "notification", "operator": "equals"},
        ],
    ),
]
```



---

## 7. Dead Letter Queues

### 7.1 DLQ Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/dead_letter_queue.py
"""
Dead Letter Queue Implementation for ResilienceAI
Handles message failures with retry and archival.
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


logger = logging.getLogger(__name__)


class DLQReason(Enum):
    """Reasons for message rejection"""
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    PROCESSING_ERROR = "processing_error"
    INVALID_MESSAGE = "invalid_message"
    TIMEOUT = "timeout"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    ROUTING_ERROR = "routing_error"
    REJECTED_BY_CONSUMER = "rejected_by_consumer"


@dataclass
class DLQMessage:
    """Dead letter message structure"""
    original_message: Dict[str, Any]
    original_metadata: Dict[str, Any]
    reason: str
    error_details: Optional[str] = None
    retry_count: int = 0
    first_failure_time: Optional[str] = None
    last_failure_time: Optional[str] = None
    stack_trace: Optional[str] = None
    dead_lettered_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DLQMessage":
        return cls(**data)


@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    max_retries: int = 3
    retry_delays: List[int] = None  # Delays in milliseconds
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0
    max_delay_ms: int = 300000  # 5 minutes
    
    def __post_init__(self):
        if self.retry_delays is None:
            if self.exponential_backoff:
                self.retry_delays = [
                    min(1000 * (self.backoff_multiplier ** i), self.max_delay_ms)
                    for i in range(self.max_retries)
                ]
            else:
                self.retry_delays = [5000] * self.max_retries  # 5 seconds fixed
    
    def get_delay_for_retry(self, retry_number: int) -> int:
        """Get delay for specific retry number"""
        if retry_number < len(self.retry_delays):
            return self.retry_delays[retry_number]
        return self.max_delay_ms


class DeadLetterQueue:
    """
    Dead Letter Queue handler for ResilienceAI.
    Manages failed messages with retry and archival.
    """
    
    DLQ_EXCHANGE = "resilience.dlx"
    DLQ_QUEUE = "dlq.main"
    RETRY_EXCHANGE = "resilience.retry"
    
    def __init__(self, client, retry_policy: Optional[RetryPolicy] = None):
        self.client = client
        self.retry_policy = retry_policy or RetryPolicy()
        self._retry_handlers: Dict[str, Callable] = {}
        self._archival_enabled = True
    
    async def initialize(self):
        """Initialize DLQ infrastructure"""
        # Declare DLQ exchange
        await self.client.declare_exchange(
            name=self.DLQ_EXCHANGE,
            exchange_type="topic",
            durable=True
        )
        
        # Declare retry exchange
        await self.client.declare_exchange(
            name=self.RETRY_EXCHANGE,
            exchange_type="direct",
            durable=True
        )
        
        # Declare main DLQ
        await self.client.declare_queue(
            name=self.DLQ_QUEUE,
            durable=True,
            arguments={
                "x-message-ttl": 604800000,  # 7 days
                "x-max-length": 1000000,
            }
        )
        
        # Declare retry queues with TTL
        for i in range(self.retry_policy.max_retries):
            delay = self.retry_policy.get_delay_for_retry(i)
            queue_name = f"retry.delay.{delay}ms"
            
            await self.client.declare_queue(
                name=queue_name,
                durable=True,
                arguments={
                    "x-message-ttl": delay,
                    "x-dead-letter-exchange": self.RETRY_EXCHANGE,
                }
            )
        
        logger.info("DLQ infrastructure initialized")
    
    async def dead_letter(
        self,
        message: Dict[str, Any],
        metadata: Dict[str, Any],
        reason: DLQReason,
        error: Optional[Exception] = None,
        retry_count: int = 0
    ):
        """
        Send message to dead letter queue.
        
        Args:
            message: Original message
            metadata: Original metadata
            reason: Reason for rejection
            error: Exception that caused rejection
            retry_count: Number of retry attempts
        """
        now = datetime.utcnow().isoformat()
        
        dlq_message = DLQMessage(
            original_message=message,
            original_metadata=metadata,
            reason=reason.value,
            error_details=str(error) if error else None,
            retry_count=retry_count,
            first_failure_time=metadata.get("first_failure_time") or now,
            last_failure_time=now,
            stack_trace=self._get_stack_trace(error) if error else None,
            dead_lettered_at=now
        )
        
        # Determine routing key based on reason
        routing_key = f"dlq.{reason.value}"
        
        await self.client.publish(
            exchange_name=self.DLQ_EXCHANGE,
            routing_key=routing_key,
            message=dlq_message.to_dict()
        )
        
        logger.warning(
            f"Message dead-lettered: reason={reason.value}, "
            f"retry_count={retry_count}, message_id={metadata.get('message_id')}"
        )
    
    async def retry_message(
        self,
        message: Dict[str, Any],
        metadata: Dict[str, Any],
        target_exchange: str,
        target_routing_key: str,
        retry_count: int = 0
    ) -> bool:
        """
        Schedule message for retry.
        
        Args:
            message: Message to retry
            metadata: Message metadata
            target_exchange: Exchange to retry to
            target_routing_key: Routing key for retry
            retry_count: Current retry count
            
        Returns:
            True if retry scheduled, False if max retries exceeded
        """
        if retry_count >= self.retry_policy.max_retries:
            await self.dead_letter(
                message=message,
                metadata=metadata,
                reason=DLQReason.MAX_RETRIES_EXCEEDED,
                retry_count=retry_count
            )
            return False
        
        # Get delay for this retry
        delay = self.retry_policy.get_delay_for_retry(retry_count)
        queue_name = f"retry.delay.{delay}ms"
        
        # Add retry metadata
        message_with_retry = {
            **message,
            "__retry_metadata__": {
                "retry_count": retry_count + 1,
                "target_exchange": target_exchange,
                "target_routing_key": target_routing_key,
                "first_failure_time": metadata.get("first_failure_time") or datetime.utcnow().isoformat(),
            }
        }
        
        # Send to retry queue (will be dead-lettered after TTL)
        await self.client.publish(
            exchange_name="",  # Default exchange
            routing_key=queue_name,
            message=message_with_retry
        )
        
        logger.info(
            f"Message scheduled for retry: retry_count={retry_count + 1}, "
            f"delay={delay}ms, message_id={metadata.get('message_id')}"
        )
        return True
    
    async def process_retry_message(
        self,
        message: Dict[str, Any],
        metadata: Dict[str, Any]
    ):
        """
        Process a message coming from retry queue.
        Routes to original target.
        """
        retry_metadata = message.pop("__retry_metadata__", {})
        target_exchange = retry_metadata.get("target_exchange")
        target_routing_key = retry_metadata.get("target_routing_key")
        
        if not target_exchange or not target_routing_key:
            logger.error("Retry message missing target information")
            await self.dead_letter(
                message=message,
                metadata=metadata,
                reason=DLQReason.ROUTING_ERROR
            )
            return
        
        # Forward to original target
        await self.client.publish(
            exchange_name=target_exchange,
            routing_key=target_routing_key,
            message=message,
            metadata=metadata
        )
        
        logger.debug(f"Retry message forwarded to {target_exchange}/{target_routing_key}")
    
    async def reprocess_dlq_message(
        self,
        dlq_message: DLQMessage,
        target_exchange: str,
        target_routing_key: str
    ) -> bool:
        """
        Manually reprocess a message from DLQ.
        
        Args:
            dlq_message: Message from DLQ
            target_exchange: Target exchange
            target_routing_key: Target routing key
            
        Returns:
            True if reprocessed successfully
        """
        try:
            await self.client.publish(
                exchange_name=target_exchange,
                routing_key=target_routing_key,
                message=dlq_message.original_message,
                metadata=dlq_message.original_metadata
            )
            
            logger.info(f"DLQ message reprocessed: {dlq_message.original_metadata.get('message_id')}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to reprocess DLQ message: {e}")
            return False
    
    def _get_stack_trace(self, error: Exception) -> str:
        """Get formatted stack trace"""
        import traceback
        return traceback.format_exc()


class DLQMonitor:
    """
    Monitor for Dead Letter Queue.
    Provides alerting and metrics.
    """
    
    def __init__(self, client, dlq: DeadLetterQueue):
        self.client = client
        self.dlq = dlq
        self._alert_threshold = 100  # Alert if DLQ size exceeds this
        self._alert_handlers: List[Callable] = []
    
    def add_alert_handler(self, handler: Callable[[str, int], None]):
        """Add alert handler"""
        self._alert_handlers.append(handler)
    
    async def check_dlq_size(self) -> int:
        """Check current DLQ size"""
        # This would use RabbitMQ management API
        # For now, return placeholder
        return 0
    
    async def monitor_loop(self):
        """Continuous monitoring loop"""
        while True:
            try:
                size = await self.check_dlq_size()
                
                if size > self._alert_threshold:
                    await self._trigger_alert(
                        f"DLQ size ({size}) exceeds threshold ({self._alert_threshold})"
                    )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.exception(f"Error in DLQ monitor: {e}")
                await asyncio.sleep(60)
    
    async def _trigger_alert(self, message: str):
        """Trigger alert handlers"""
        for handler in self._alert_handlers:
            try:
                handler(message, self._alert_threshold)
            except Exception as e:
                logger.exception(f"Alert handler failed: {e}")
    
    async def get_dlq_stats(self) -> Dict[str, Any]:
        """Get DLQ statistics"""
        return {
            "queue_name": self.dlq.DLQ_QUEUE,
            "alert_threshold": self._alert_threshold,
            # Additional stats would come from management API
        }
```

---

## 8. Message Persistence

### 8.1 Persistence Layer

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/persistence.py
"""
Message Persistence Layer for ResilienceAI
Ensures message durability and recovery.
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class PersistenceStrategy(Enum):
    """Persistence strategies"""
    IMMEDIATE = "immediate"
    BATCH = "batch"
    ASYNC = "async"
    WAL = "wal"  # Write-ahead logging


@dataclass
class PersistedMessage:
    """Persisted message record"""
    message_id: str
    topic: str
    partition: int
    offset: int
    payload: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: str
    persisted_at: str


class MessageStore(ABC):
    """Abstract message store"""
    
    @abstractmethod
    async def save(self, message: PersistedMessage) -> bool:
        """Save a message"""
        pass
    
    @abstractmethod
    async def get(self, message_id: str) -> Optional[PersistedMessage]:
        """Get message by ID"""
        pass
    
    @abstractmethod
    async def get_by_topic(
        self,
        topic: str,
        start_offset: int = 0,
        limit: int = 100
    ) -> List[PersistedMessage]:
        """Get messages by topic"""
        pass
    
    @abstractmethod
    async def delete(self, message_id: str) -> bool:
        """Delete a message"""
        pass


class InMemoryMessageStore(MessageStore):
    """In-memory message store for testing"""
    
    def __init__(self):
        self._messages: Dict[str, PersistedMessage] = {}
        self._topic_index: Dict[str, List[str]] = {}
    
    async def save(self, message: PersistedMessage) -> bool:
        self._messages[message.message_id] = message
        
        if message.topic not in self._topic_index:
            self._topic_index[message.topic] = []
        self._topic_index[message.topic].append(message.message_id)
        
        return True
    
    async def get(self, message_id: str) -> Optional[PersistedMessage]:
        return self._messages.get(message_id)
    
    async def get_by_topic(
        self,
        topic: str,
        start_offset: int = 0,
        limit: int = 100
    ) -> List[PersistedMessage]:
        message_ids = self._topic_index.get(topic, [])
        return [
            self._messages[mid]
            for mid in message_ids[start_offset:start_offset + limit]
        ]
    
    async def delete(self, message_id: str) -> bool:
        if message_id in self._messages:
            message = self._messages[message_id]
            del self._messages[message_id]
            
            if message.topic in self._topic_index:
                self._topic_index[message.topic].remove(message_id)
            
            return True
        return False


class PersistenceManager:
    """
    Manages message persistence for ResilienceAI.
    """
    
    def __init__(
        self,
        store: MessageStore,
        strategy: PersistenceStrategy = PersistenceStrategy.IMMEDIATE
    ):
        self.store = store
        self.strategy = strategy
        self._batch: List[PersistedMessage] = []
        self._batch_size = 100
        self._batch_timeout_ms = 1000
        self._wal_buffer: List[Dict[str, Any]] = []
        self._running = False
    
    async def start(self):
        """Start persistence manager"""
        self._running = True
        
        if self.strategy == PersistenceStrategy.BATCH:
            asyncio.create_task(self._batch_flush_loop())
        elif self.strategy == PersistenceStrategy.WAL:
            asyncio.create_task(self._wal_flush_loop())
    
    async def stop(self):
        """Stop persistence manager"""
        self._running = False
        
        # Flush remaining messages
        if self.strategy == PersistenceStrategy.BATCH:
            await self._flush_batch()
        elif self.strategy == PersistenceStrategy.WAL:
            await self._flush_wal()
    
    async def persist(
        self,
        message_id: str,
        topic: str,
        partition: int,
        offset: int,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> bool:
        """
        Persist a message.
        
        Args:
            message_id: Unique message identifier
            topic: Message topic/queue
            partition: Partition number
            offset: Message offset
            payload: Message payload
            headers: Message headers
            
        Returns:
            True if persisted successfully
        """
        persisted_message = PersistedMessage(
            message_id=message_id,
            topic=topic,
            partition=partition,
            offset=offset,
            payload=payload,
            headers=headers,
            timestamp=datetime.utcnow().isoformat(),
            persisted_at=datetime.utcnow().isoformat()
        )
        
        if self.strategy == PersistenceStrategy.IMMEDIATE:
            return await self.store.save(persisted_message)
        
        elif self.strategy == PersistenceStrategy.BATCH:
            self._batch.append(persisted_message)
            if len(self._batch) >= self._batch_size:
                await self._flush_batch()
            return True
        
        elif self.strategy == PersistenceStrategy.ASYNC:
            asyncio.create_task(self.store.save(persisted_message))
            return True
        
        elif self.strategy == PersistenceStrategy.WAL:
            self._wal_buffer.append(persisted_message.to_dict())
            if len(self._wal_buffer) >= self._batch_size:
                await self._flush_wal()
            return True
        
        return False
    
    async def _batch_flush_loop(self):
        """Periodic batch flush"""
        while self._running:
            await asyncio.sleep(self._batch_timeout_ms / 1000)
            if self._batch:
                await self._flush_batch()
    
    async def _flush_batch(self):
        """Flush batch to store"""
        if not self._batch:
            return
        
        batch = self._batch
        self._batch = []
        
        for message in batch:
            try:
                await self.store.save(message)
            except Exception as e:
                logger.exception(f"Failed to persist message: {e}")
    
    async def _wal_flush_loop(self):
        """Periodic WAL flush"""
        while self._running:
            await asyncio.sleep(self._batch_timeout_ms / 1000)
            if self._wal_buffer:
                await self._flush_wal()
    
    async def _flush_wal(self):
        """Flush WAL buffer"""
        if not self._wal_buffer:
            return
        
        buffer = self._wal_buffer
        self._wal_buffer = []
        
        # Write to WAL file
        try:
            with open("/tmp/messaging.wal", "a") as f:
                for entry in buffer:
                    f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.exception(f"Failed to write WAL: {e}")
    
    async def recover(self) -> List[PersistedMessage]:
        """Recover messages from WAL"""
        messages = []
        
        try:
            with open("/tmp/messaging.wal", "r") as f:
                for line in f:
                    data = json.loads(line.strip())
                    messages.append(PersistedMessage(**data))
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.exception(f"Failed to recover from WAL: {e}")
        
        return messages


class MessageJournal:
    """
    Message journal for audit and replay.
    """
    
    def __init__(self, store: MessageStore):
        self.store = store
        self._journal_enabled = True
    
    async def journal(
        self,
        message: Dict[str, Any],
        metadata: Dict[str, Any],
        action: str
    ):
        """
        Journal a message action.
        
        Args:
            message: Message content
            metadata: Message metadata
            action: Action performed (e.g., "published", "consumed", "failed")
        """
        if not self._journal_enabled:
            return
        
        journal_entry = PersistedMessage(
            message_id=metadata.get("message_id", "unknown"),
            topic=metadata.get("topic", "unknown"),
            partition=metadata.get("partition", 0),
            offset=metadata.get("offset", 0),
            payload={
                "action": action,
                "message": message,
            },
            headers=metadata.get("headers", {}),
            timestamp=metadata.get("timestamp", datetime.utcnow().isoformat()),
            persisted_at=datetime.utcnow().isoformat()
        )
        
        await self.store.save(journal_entry)
    
    async def get_journal(
        self,
        topic: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[PersistedMessage]:
        """Get journal entries for topic"""
        messages = await self.store.get_by_topic(topic, limit=10000)
        
        if start_time:
            messages = [m for m in messages if m.timestamp >= start_time]
        if end_time:
            messages = [m for m in messages if m.timestamp <= end_time]
        
        return messages
    
    async def replay(
        self,
        topic: str,
        producer: Callable[[Dict[str, Any]], None],
        start_time: Optional[str] = None
    ):
        """
        Replay messages from journal.
        
        Args:
            topic: Topic to replay
            producer: Function to produce replayed messages
            start_time: Optional start time filter
        """
        messages = await self.get_journal(topic, start_time)
        
        for message in messages:
            payload = message.payload
            if payload.get("action") == "published":
                original_message = payload.get("message", {})
                producer(original_message)
```

---

## 9. Scalability Patterns

### 9.1 Scalability Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/scalability.py
"""
Scalability Patterns for ResilienceAI Message Queue
Implements horizontal scaling and load balancing.
"""
import asyncio
import hashlib
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random


logger = logging.getLogger(__name__)


class PartitionStrategy(Enum):
    """Message partitioning strategies"""
    ROUND_ROBIN = "round_robin"
    HASH = "hash"
    RANGE = "range"
    CUSTOM = "custom"


@dataclass
class PartitionConfig:
    """Partition configuration"""
    partition_count: int = 12
    replication_factor: int = 3
    strategy: PartitionStrategy = PartitionStrategy.HASH
    partition_key_extractor: Optional[Callable] = None


class Partitioner:
    """
    Message partitioner for distributing messages across partitions.
    """
    
    def __init__(self, config: PartitionConfig):
        self.config = config
        self._round_robin_counter = 0
    
    def get_partition(
        self,
        message: Dict[str, Any],
        key: Optional[str] = None
    ) -> int:
        """
        Determine partition for message.
        
        Args:
            message: Message payload
            key: Optional partition key
            
        Returns:
            Partition number
        """
        if self.config.strategy == PartitionStrategy.ROUND_ROBIN:
            return self._round_robin()
        
        elif self.config.strategy == PartitionStrategy.HASH:
            partition_key = key or self._extract_key(message)
            return self._hash_partition(partition_key)
        
        elif self.config.strategy == PartitionStrategy.RANGE:
            partition_key = key or self._extract_key(message)
            return self._range_partition(partition_key)
        
        elif self.config.strategy == PartitionStrategy.CUSTOM:
            if self.config.partition_key_extractor:
                partition_key = self.config.partition_key_extractor(message)
                return self._hash_partition(partition_key)
        
        return self._round_robin()
    
    def _round_robin(self) -> int:
        """Round-robin partition selection"""
        partition = self._round_robin_counter % self.config.partition_count
        self._round_robin_counter += 1
        return partition
    
    def _hash_partition(self, key: str) -> int:
        """Hash-based partition selection"""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return hash_value % self.config.partition_count
    
    def _range_partition(self, key: str) -> int:
        """Range-based partition selection"""
        # Assuming key is numeric or can be converted
        try:
            numeric_key = int(key)
            partition_size = 2**32 // self.config.partition_count
            return numeric_key // partition_size
        except (ValueError, TypeError):
            return self._hash_partition(key)
    
    def _extract_key(self, message: Dict[str, Any]) -> str:
        """Extract partition key from message"""
        # Try common key fields
        for field in ["id", "key", "partition_key", "entity_id"]:
            if field in message:
                return str(message[field])
        
        # Fall back to message hash
        return str(hash(str(message)))


class LoadBalancer:
    """
    Load balancer for consumer groups.
    """
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self._consumers: List[str] = []
        self._counter = 0
        self._weights: Dict[str, int] = {}
    
    def add_consumer(self, consumer_id: str, weight: int = 1):
        """Add a consumer"""
        self._consumers.append(consumer_id)
        self._weights[consumer_id] = weight
    
    def remove_consumer(self, consumer_id: str):
        """Remove a consumer"""
        if consumer_id in self._consumers:
            self._consumers.remove(consumer_id)
            del self._weights[consumer_id]
    
    def select_consumer(self, key: Optional[str] = None) -> Optional[str]:
        """Select a consumer for message processing"""
        if not self._consumers:
            return None
        
        if self.strategy == "round_robin":
            consumer = self._consumers[self._counter % len(self._consumers)]
            self._counter += 1
            return consumer
        
        elif self.strategy == "random":
            return random.choice(self._consumers)
        
        elif self.strategy == "weighted":
            return self._weighted_select()
        
        elif self.strategy == "hash":
            if key:
                idx = hash(key) % len(self._consumers)
                return self._consumers[idx]
            return self._consumers[0]
        
        return self._consumers[0]
    
    def _weighted_select(self) -> str:
        """Weighted random selection"""
        total_weight = sum(self._weights.values())
        r = random.randint(1, total_weight)
        
        cumulative = 0
        for consumer, weight in self._weights.items():
            cumulative += weight
            if r <= cumulative:
                return consumer
        
        return self._consumers[-1]


class ConsumerGroup:
    """
    Consumer group for scalable message consumption.
    """
    
    def __init__(
        self,
        group_id: str,
        partitioner: Partitioner,
        load_balancer: LoadBalancer
    ):
        self.group_id = group_id
        self.partitioner = partitioner
        self.load_balancer = load_balancer
        self._consumers: Dict[str, Dict[str, Any]] = {}
        self._partition_assignments: Dict[int, str] = {}
        self._rebalance_lock = asyncio.Lock()
    
    async def join(self, consumer_id: str, topics: List[str]):
        """
        Add consumer to group.
        
        Args:
            consumer_id: Unique consumer identifier
            topics: Topics to subscribe to
        """
        async with self._rebalance_lock:
            self._consumers[consumer_id] = {
                "topics": topics,
                "assigned_partitions": []
            }
            self.load_balancer.add_consumer(consumer_id)
            
            await self._rebalance()
            
            logger.info(f"Consumer {consumer_id} joined group {self.group_id}")
    
    async def leave(self, consumer_id: str):
        """Remove consumer from group"""
        async with self._rebalance_lock:
            if consumer_id in self._consumers:
                del self._consumers[consumer_id]
                self.load_balancer.remove_consumer(consumer_id)
                
                await self._rebalance()
                
                logger.info(f"Consumer {consumer_id} left group {self.group_id}")
    
    async def _rebalance(self):
        """Rebalance partitions across consumers"""
        if not self._consumers:
            self._partition_assignments.clear()
            return
        
        consumer_ids = list(self._consumers.keys())
        partition_count = self.partitioner.config.partition_count
        
        # Simple round-robin assignment
        for partition in range(partition_count):
            consumer_idx = partition % len(consumer_ids)
            self._partition_assignments[partition] = consumer_ids[consumer_idx]
        
        # Update consumer assignments
        for consumer_id in consumer_ids:
            self._consumers[consumer_id]["assigned_partitions"] = [
                p for p, c in self._partition_assignments.items() if c == consumer_id
            ]
        
        logger.info(f"Rebalanced group {self.group_id}: {self._partition_assignments}")
    
    def get_partition_owner(self, partition: int) -> Optional[str]:
        """Get consumer assigned to partition"""
        return self._partition_assignments.get(partition)
    
    def get_consumer_partitions(self, consumer_id: str) -> List[int]:
        """Get partitions assigned to consumer"""
        if consumer_id in self._consumers:
            return self._consumers[consumer_id]["assigned_partitions"]
        return []


class AutoScaler:
    """
    Auto-scaler for consumer groups.
    Scales consumers based on queue depth and processing rate.
    """
    
    def __init__(
        self,
        consumer_group: ConsumerGroup,
        min_consumers: int = 1,
        max_consumers: int = 10,
        scale_up_threshold: int = 1000,
        scale_down_threshold: int = 100,
        cooldown_seconds: int = 60
    ):
        self.consumer_group = consumer_group
        self.min_consumers = min_consumers
        self.max_consumers = max_consumers
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.cooldown_seconds = cooldown_seconds
        
        self._current_consumer_count = min_consumers
        self._last_scale_time: Optional[datetime] = None
        self._running = False
    
    async def start(self):
        """Start auto-scaler"""
        self._running = True
        while self._running:
            await self._evaluate_scaling()
            await asyncio.sleep(30)  # Check every 30 seconds
    
    def stop(self):
        """Stop auto-scaler"""
        self._running = False
    
    async def _evaluate_scaling(self):
        """Evaluate and apply scaling decisions"""
        # Check cooldown
        if self._last_scale_time:
            elapsed = (datetime.utcnow() - self._last_scale_time).total_seconds()
            if elapsed < self.cooldown_seconds:
                return
        
        # Get current metrics (placeholder)
        queue_depth = await self._get_queue_depth()
        processing_rate = await self._get_processing_rate()
        
        # Scale up if queue depth is high
        if queue_depth > self.scale_up_threshold:
            if self._current_consumer_count < self.max_consumers:
                await self._scale_up()
        
        # Scale down if queue depth is low
        elif queue_depth < self.scale_down_threshold:
            if self._current_consumer_count > self.min_consumers:
                await self._scale_down()
    
    async def _get_queue_depth(self) -> int:
        """Get current queue depth"""
        # Would integrate with queue management API
        return 0
    
    async def _get_processing_rate(self) -> float:
        """Get current processing rate"""
        # Would calculate from metrics
        return 0.0
    
    async def _scale_up(self):
        """Scale up consumer count"""
        new_count = min(self._current_consumer_count + 1, self.max_consumers)
        
        # Start new consumers
        for i in range(self._current_consumer_count, new_count):
            consumer_id = f"consumer-{i}"
            await self.consumer_group.join(consumer_id, ["default-topic"])
        
        self._current_consumer_count = new_count
        self._last_scale_time = datetime.utcnow()
        
        logger.info(f"Scaled up to {new_count} consumers")
    
    async def _scale_down(self):
        """Scale down consumer count"""
        new_count = max(self._current_consumer_count - 1, self.min_consumers)
        
        # Remove consumers
        for i in range(new_count, self._current_consumer_count):
            consumer_id = f"consumer-{i}"
            await self.consumer_group.leave(consumer_id)
        
        self._current_consumer_count = new_count
        self._last_scale_time = datetime.utcnow()
        
        logger.info(f"Scaled down to {new_count} consumers")


class BackpressureController:
    """
    Backpressure controller for flow control.
    """
    
    def __init__(
        self,
        high_watermark: int = 1000,
        low_watermark: int = 100,
        check_interval: float = 1.0
    ):
        self.high_watermark = high_watermark
        self.low_watermark = low_watermark
        self.check_interval = check_interval
        
        self._pending_count = 0
        self._paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Initially not paused
    
    async def acquire(self):
        """Acquire permission to process message"""
        await self._pause_event.wait()
        self._pending_count += 1
        
        if self._pending_count >= self.high_watermark and not self._paused:
            await self._pause()
    
    def release(self):
        """Release processing slot"""
        self._pending_count -= 1
        
        if self._pending_count <= self.low_watermark and self._paused:
            asyncio.create_task(self._resume())
    
    async def _pause(self):
        """Pause message consumption"""
        self._paused = True
        self._pause_event.clear()
        logger.warning(f"Backpressure: paused consumption (pending: {self._pending_count})")
    
    async def _resume(self):
        """Resume message consumption"""
        self._paused = False
        self._pause_event.set()
        logger.info(f"Backpressure: resumed consumption (pending: {self._pending_count})")
    
    @property
    def is_paused(self) -> bool:
        """Check if consumption is paused"""
        return self._paused
```

---

## 10. Monitoring & Observability

### 10.1 Monitoring Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/monitoring.py
"""
Monitoring and Observability for ResilienceAI Message Queue
Provides metrics, tracing, and health checks.
"""
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import json


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: str
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_prometheus(self) -> str:
        """Convert to Prometheus format"""
        labels_str = ",".join(f'{k}="{v}"' for k, v in self.labels.items())
        if labels_str:
            return f'{name}{{{labels_str}}} {value}'
        return f'{name} {value}'


class MetricsCollector:
    """
    Metrics collector for message queue operations.
    """
    
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        self._labels: Dict[str, Dict[str, str]] = {}
        self._lock = asyncio.Lock()
    
    def counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment counter"""
        key = self._make_key(name, labels)
        self._counters[key] += value
    
    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set gauge value"""
        key = self._make_key(name, labels)
        self._gauges[key] = value
    
    def histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record histogram value"""
        key = self._make_key(name, labels)
        self._histograms[key].append(value)
    
    def timer(self, name: str, duration_ms: float, labels: Optional[Dict[str, str]] = None):
        """Record timer value"""
        key = self._make_key(name, labels)
        self._timers[key].append(duration_ms)
    
    @contextmanager
    def time_operation(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager for timing operations"""
        start = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start) * 1000
            self.timer(name, duration_ms, labels)
    
    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create metric key"""
        if labels:
            labels_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}:{labels_str}"
        return name
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        async with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "avg": sum(v) / len(v) if v else 0,
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                        "p50": self._percentile(v, 50) if v else 0,
                        "p95": self._percentile(v, 95) if v else 0,
                        "p99": self._percentile(v, 99) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
                "timers": {
                    k: {
                        "count": len(v),
                        "avg_ms": sum(v) / len(v) if v else 0,
                        "p50_ms": self._percentile(v, 50) if v else 0,
                        "p95_ms": self._percentile(v, 95) if v else 0,
                        "p99_ms": self._percentile(v, 99) if v else 0,
                    }
                    for k, v in self._timers.items()
                },
            }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def to_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Counters
        for key, value in self._counters.items():
            name, labels = self._parse_key(key)
            lines.append(f"# TYPE {name} counter")
            lines.append(Metric(name, value, MetricType.COUNTER, "", labels).to_prometheus())
        
        # Gauges
        for key, value in self._gauges.items():
            name, labels = self._parse_key(key)
            lines.append(f"# TYPE {name} gauge")
            lines.append(Metric(name, value, MetricType.GAUGE, "", labels).to_prometheus())
        
        return "\n".join(lines)
    
    def _parse_key(self, key: str) -> tuple:
        """Parse metric key into name and labels"""
        if ":" in key:
            name, labels_str = key.split(":", 1)
            labels = {}
            for part in labels_str.split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    labels[k] = v
            return name, labels
        return key, {}


class MessageTracer:
    """
    Distributed tracing for messages.
    """
    
    def __init__(self):
        self._spans: Dict[str, Dict[str, Any]] = {}
        self._trace_context = {}
    
    def start_trace(
        self,
        trace_id: str,
        span_name: str,
        parent_span_id: Optional[str] = None
    ) -> str:
        """Start a new trace span"""
        span_id = self._generate_span_id()
        
        self._spans[span_id] = {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "name": span_name,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None,
            "tags": {},
            "logs": []
        }
        
        return span_id
    
    def end_trace(self, span_id: str):
        """End a trace span"""
        if span_id in self._spans:
            self._spans[span_id]["end_time"] = datetime.utcnow().isoformat()
    
    def add_tag(self, span_id: str, key: str, value: str):
        """Add tag to span"""
        if span_id in self._spans:
            self._spans[span_id]["tags"][key] = value
    
    def add_log(self, span_id: str, message: str, fields: Optional[Dict] = None):
        """Add log to span"""
        if span_id in self._spans:
            self._spans[span_id]["logs"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "fields": fields or {}
            })
    
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get all spans for a trace"""
        return [s for s in self._spans.values() if s["trace_id"] == trace_id]
    
    def _generate_span_id(self) -> str:
        """Generate unique span ID"""
        import uuid
        return str(uuid.uuid4())[:16]


class HealthChecker:
    """
    Health checker for message queue components.
    """
    
    class Status(Enum):
        HEALTHY = "healthy"
        DEGRADED = "degraded"
        UNHEALTHY = "unhealthy"
    
    def __init__(self):
        self._checks: Dict[str, Callable] = {}
        self._status: Dict[str, Any] = {}
    
    def register_check(self, name: str, check_func: Callable):
        """Register a health check"""
        self._checks[name] = check_func
    
    async def check_health(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_status = self.Status.HEALTHY
        
        for name, check_func in self._checks.items():
            try:
                result = await check_func()
                results[name] = result
                
                if result.get("status") == self.Status.UNHEALTHY.value:
                    overall_status = self.Status.UNHEALTHY
                elif result.get("status") == self.Status.DEGRADED.value and overall_status != self.Status.UNHEALTHY:
                    overall_status = self.Status.DEGRADED
                    
            except Exception as e:
                results[name] = {
                    "status": self.Status.UNHEALTHY.value,
                    "error": str(e)
                }
                overall_status = self.Status.UNHEALTHY
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }


class QueueMonitor:
    """
    Monitor for message queue health and metrics.
    """
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        health_checker: HealthChecker,
        message_tracer: MessageTracer
    ):
        self.metrics = metrics_collector
        self.health = health_checker
        self.tracer = message_tracer
        self._alert_handlers: List[Callable] = []
    
    def add_alert_handler(self, handler: Callable[[str, Dict], None]):
        """Add alert handler"""
        self._alert_handlers.append(handler)
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous monitoring"""
        while True:
            try:
                # Collect metrics
                metrics = await self.metrics.get_metrics()
                
                # Run health checks
                health = await self.health.check_health()
                
                # Check for alerts
                await self._check_alerts(metrics, health)
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.exception(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def _check_alerts(self, metrics: Dict, health: Dict):
        """Check for alert conditions"""
        alerts = []
        
        # Check queue depth
        counters = metrics.get("counters", {})
        if counters.get("messages_pending", 0) > 10000:
            alerts.append({
                "severity": "warning",
                "message": "High queue depth detected",
                "value": counters.get("messages_pending")
            })
        
        # Check error rate
        errors = counters.get("messages_failed", 0)
        total = counters.get("messages_consumed", 1)
        error_rate = errors / total
        if error_rate > 0.1:  # 10% error rate
            alerts.append({
                "severity": "critical",
                "message": "High error rate detected",
                "value": error_rate
            })
        
        # Check health status
        if health.get("status") == "unhealthy":
            alerts.append({
                "severity": "critical",
                "message": "System unhealthy",
                "details": health
            })
        
        # Trigger alert handlers
        for alert in alerts:
            for handler in self._alert_handlers:
                try:
                    handler(alert["message"], alert)
                except Exception as e:
                    logger.exception(f"Alert handler failed: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        return {
            "metrics": self.metrics.get_metrics(),
            "health": self.health.check_health(),
            "timestamp": datetime.utcnow().isoformat()
        }


# Predefined metrics for ResilienceAI
RESILIENCE_AI_METRICS = {
    # Message metrics
    "messages_published_total": "Total messages published",
    "messages_consumed_total": "Total messages consumed",
    "messages_failed_total": "Total message processing failures",
    "messages_pending": "Current pending messages",
    "messages_dlq_total": "Total messages sent to DLQ",
    
    # Performance metrics
    "publish_latency_ms": "Message publish latency",
    "consume_latency_ms": "Message consume latency",
    "processing_time_ms": "Message processing time",
    "queue_depth": "Current queue depth",
    
    # Consumer metrics
    "consumers_active": "Number of active consumers",
    "consumer_lag": "Consumer lag by partition",
    "rebalances_total": "Total consumer rebalances",
    
    # Connection metrics
    "connections_active": "Active connections",
    "channels_active": "Active channels",
    "connection_errors_total": "Total connection errors",
}
```

---

## 11. Event Sourcing

### 11.1 Event Store Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/event_sourcing.py
"""
Event Sourcing Implementation for ResilienceAI
Provides event store and projection capabilities.
"""
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types for ResilienceAI"""
    # Incident events
    INCIDENT_CREATED = "incident.created"
    INCIDENT_UPDATED = "incident.updated"
    INCIDENT_ASSIGNED = "incident.assigned"
    INCIDENT_ESCALATED = "incident.escalated"
    INCIDENT_RESOLVED = "incident.resolved"
    INCIDENT_CLOSED = "incident.closed"
    
    # Alert events
    ALERT_TRIGGERED = "alert.triggered"
    ALERT_ACKNOWLEDGED = "alert.acknowledged"
    ALERT_SUPPRESSED = "alert.suppressed"
    ALERT_RESOLVED = "alert.resolved"
    
    # System events
    SYSTEM_STARTED = "system.started"
    SYSTEM_STOPPED = "system.stopped"
    SYSTEM_ERROR = "system.error"
    
    # User events
    USER_LOGGED_IN = "user.logged_in"
    USER_ACTION = "user.action"


@dataclass
class DomainEvent:
    """Domain event structure"""
    event_id: str
    event_type: str
    aggregate_id: str
    aggregate_type: str
    version: int
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        return cls(**data)


class EventStore(ABC):
    """Abstract event store"""
    
    @abstractmethod
    async def append(self, event: DomainEvent) -> bool:
        """Append event to store"""
        pass
    
    @abstractmethod
    async def get_events(
        self,
        aggregate_id: str,
        from_version: int = 0
    ) -> List[DomainEvent]:
        """Get events for aggregate"""
        pass
    
    @abstractmethod
    async def get_all_events(
        self,
        event_types: Optional[List[str]] = None,
        after_position: int = 0,
        limit: int = 100
    ) -> List[DomainEvent]:
        """Get all events"""
        pass
    
    @abstractmethod
    async def get_current_version(self, aggregate_id: str) -> int:
        """Get current version for aggregate"""
        pass


class InMemoryEventStore(EventStore):
    """In-memory event store for testing"""
    
    def __init__(self):
        self._events: Dict[str, List[DomainEvent]] = {}
        self._all_events: List[DomainEvent] = []
        self._position = 0
    
    async def append(self, event: DomainEvent) -> bool:
        if event.aggregate_id not in self._events:
            self._events[event.aggregate_id] = []
        
        self._events[event.aggregate_id].append(event)
        self._all_events.append(event)
        self._position += 1
        
        return True
    
    async def get_events(
        self,
        aggregate_id: str,
        from_version: int = 0
    ) -> List[DomainEvent]:
        events = self._events.get(aggregate_id, [])
        return [e for e in events if e.version >= from_version]
    
    async def get_all_events(
        self,
        event_types: Optional[List[str]] = None,
        after_position: int = 0,
        limit: int = 100
    ) -> List[DomainEvent]:
        events = self._all_events[after_position:]
        
        if event_types:
            events = [e for e in events if e.event_type in event_types]
        
        return events[:limit]
    
    async def get_current_version(self, aggregate_id: str) -> int:
        events = self._events.get(aggregate_id, [])
        if events:
            return max(e.version for e in events)
        return 0


class AggregateRoot(ABC):
    """
    Base class for aggregate roots in event sourcing.
    """
    
    def __init__(self, aggregate_id: str):
        self._id = aggregate_id
        self._version = 0
        self._uncommitted_events: List[DomainEvent] = []
        self._is_replaying = False
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def version(self) -> int:
        return self._version
    
    @property
    def uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)
    
    def apply_event(self, event: DomainEvent):
        """Apply event to aggregate"""
        handler = getattr(self, f"_on_{event.event_type.replace('.', '_')}", None)
        
        if handler:
            handler(event.payload)
        
        if not self._is_replaying:
            self._uncommitted_events.append(event)
        
        self._version = event.version
    
    def create_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> DomainEvent:
        """Create a new domain event"""
        import uuid
        
        return DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            aggregate_id=self._id,
            aggregate_type=self.__class__.__name__,
            version=self._version + 1,
            payload=payload,
            metadata=metadata or {},
            timestamp=datetime.utcnow().isoformat(),
            correlation_id=str(uuid.uuid4())
        )
    
    def load_from_history(self, events: List[DomainEvent]):
        """Load aggregate from event history"""
        self._is_replaying = True
        try:
            for event in events:
                self.apply_event(event)
        finally:
            self._is_replaying = False
        
        self._uncommitted_events.clear()
    
    def mark_committed(self):
        """Mark uncommitted events as committed"""
        self._uncommitted_events.clear()


class IncidentAggregate(AggregateRoot):
    """
    Incident aggregate for event sourcing.
    """
    
    def __init__(self, incident_id: str):
        super().__init__(incident_id)
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.severity: Optional[str] = None
        self.status: str = "open"
        self.assigned_to: Optional[str] = None
        self.created_at: Optional[str] = None
        self.resolved_at: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        incident_id: str,
        title: str,
        description: str,
        severity: str,
        reported_by: str
    ) -> "IncidentAggregate":
        """Factory method to create new incident"""
        incident = cls(incident_id)
        
        event = incident.create_event(
            event_type=EventType.INCIDENT_CREATED.value,
            payload={
                "title": title,
                "description": description,
                "severity": severity,
                "reported_by": reported_by,
            },
            metadata={"source": "api"}
        )
        
        incident.apply_event(event)
        return incident
    
    def assign(self, user_id: str):
        """Assign incident to user"""
        event = self.create_event(
            event_type=EventType.INCIDENT_ASSIGNED.value,
            payload={"assigned_to": user_id}
        )
        self.apply_event(event)
    
    def escalate(self, reason: str):
        """Escalate incident"""
        event = self.create_event(
            event_type=EventType.INCIDENT_ESCALATED.value,
            payload={"reason": reason, "previous_severity": self.severity}
        )
        self.apply_event(event)
    
    def resolve(self, resolution: str, resolved_by: str):
        """Resolve incident"""
        event = self.create_event(
            event_type=EventType.INCIDENT_RESOLVED.value,
            payload={
                "resolution": resolution,
                "resolved_by": resolved_by
            }
        )
        self.apply_event(event)
    
    # Event handlers
    def _on_incident_created(self, payload: Dict[str, Any]):
        self.title = payload.get("title")
        self.description = payload.get("description")
        self.severity = payload.get("severity")
        self.created_at = datetime.utcnow().isoformat()
    
    def _on_incident_assigned(self, payload: Dict[str, Any]):
        self.assigned_to = payload.get("assigned_to")
    
    def _on_incident_escalated(self, payload: Dict[str, Any]):
        # Increase severity
        severity_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        current_idx = severity_levels.index(self.severity) if self.severity in severity_levels else 0
        if current_idx < len(severity_levels) - 1:
            self.severity = severity_levels[current_idx + 1]
    
    def _on_incident_resolved(self, payload: Dict[str, Any]):
        self.status = "resolved"
        self.resolved_at = datetime.utcnow().isoformat()


class Projection(ABC):
    """
    Abstract projection for read models.
    """
    
    @abstractmethod
    async def handle_event(self, event: DomainEvent):
        """Handle a domain event"""
        pass
    
    @abstractmethod
    async def reset(self):
        """Reset projection state"""
        pass


class IncidentListProjection(Projection):
    """
    Projection for incident list view.
    """
    
    def __init__(self):
        self._incidents: Dict[str, Dict[str, Any]] = {}
    
    async def handle_event(self, event: DomainEvent):
        """Handle domain event"""
        handlers = {
            EventType.INCIDENT_CREATED.value: self._on_created,
            EventType.INCIDENT_ASSIGNED.value: self._on_assigned,
            EventType.INCIDENT_RESOLVED.value: self._on_resolved,
        }
        
        handler = handlers.get(event.event_type)
        if handler:
            await handler(event)
    
    async def _on_created(self, event: DomainEvent):
        self._incidents[event.aggregate_id] = {
            "id": event.aggregate_id,
            "title": event.payload.get("title"),
            "severity": event.payload.get("severity"),
            "status": "open",
            "created_at": event.timestamp,
        }
    
    async def _on_assigned(self, event: DomainEvent):
        if event.aggregate_id in self._incidents:
            self._incidents[event.aggregate_id]["assigned_to"] = event.payload.get("assigned_to")
    
    async def _on_resolved(self, event: DomainEvent):
        if event.aggregate_id in self._incidents:
            self._incidents[event.aggregate_id]["status"] = "resolved"
            self._incidents[event.aggregate_id]["resolved_at"] = event.timestamp
    
    async def reset(self):
        self._incidents.clear()
    
    def get_incidents(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get incidents with optional filtering"""
        incidents = list(self._incidents.values())
        
        if status:
            incidents = [i for i in incidents if i.get("status") == status]
        if severity:
            incidents = [i for i in incidents if i.get("severity") == severity]
        
        return incidents


class EventPublisher:
    """
    Publishes events to message queue.
    """
    
    def __init__(self, client, event_store: EventStore):
        self.client = client
        self.event_store = event_store
    
    async def publish(self, event: DomainEvent):
        """Publish event to store and message queue"""
        # Store event
        await self.event_store.append(event)
        
        # Publish to message queue
        await self.client.publish(
            exchange_name="resilience.topic",
            routing_key=event.event_type,
            message=event.to_dict()
        )


class EventSourcedRepository:
    """
    Repository for event sourced aggregates.
    """
    
    def __init__(
        self,
        event_store: EventStore,
        event_publisher: EventPublisher,
        aggregate_class: type
    ):
        self.event_store = event_store
        self.event_publisher = event_publisher
        self.aggregate_class = aggregate_class
    
    async def get_by_id(self, aggregate_id: str) -> Optional[AggregateRoot]:
        """Get aggregate by ID"""
        events = await self.event_store.get_events(aggregate_id)
        
        if not events:
            return None
        
        aggregate = self.aggregate_class(aggregate_id)
        aggregate.load_from_history(events)
        
        return aggregate
    
    async def save(self, aggregate: AggregateRoot):
        """Save aggregate changes"""
        for event in aggregate.uncommitted_events:
            # Store event
            await self.event_store.append(event)
            
            # Publish event
            await self.event_publisher.publish(event)
        
        aggregate.mark_committed()
```



---

## 12. Saga Patterns

### 12.1 Saga Orchestrator Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/saga_orchestrator.py
"""
Saga Pattern Implementation for ResilienceAI
Provides distributed transaction coordination.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from abc import ABC, abstractmethod
import uuid


logger = logging.getLogger(__name__)


class SagaStatus(Enum):
    """Saga execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class StepStatus(Enum):
    """Saga step status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    """Saga step definition"""
    name: str
    action: Callable[[Dict[str, Any]], Coroutine[Any, Any, Dict[str, Any]]]
    compensation: Optional[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = None
    status: StepStatus = StepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class SagaInstance:
    """Saga instance state"""
    saga_id: str
    saga_type: str
    status: SagaStatus
    steps: List[SagaStep]
    context: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    current_step_index: int = 0


class Saga(ABC):
    """
    Abstract base class for sagas.
    """
    
    def __init__(self, name: str):
        self.name = name
        self._steps: List[SagaStep] = []
    
    def step(
        self,
        name: str,
        action: Callable[[Dict[str, Any]], Coroutine[Any, Any, Dict[str, Any]]],
        compensation: Optional[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = None
    ) -> "Saga":
        """Add a step to the saga"""
        self._steps.append(SagaStep(
            name=name,
            action=action,
            compensation=compensation
        ))
        return self
    
    def build(self, context: Optional[Dict[str, Any]] = None) -> SagaInstance:
        """Build saga instance"""
        return SagaInstance(
            saga_id=str(uuid.uuid4()),
            saga_type=self.name,
            status=SagaStatus.PENDING,
            steps=[SagaStep(
                name=s.name,
                action=s.action,
                compensation=s.compensation
            ) for s in self._steps],
            context=context or {}
        )


class SagaOrchestrator:
    """
    Orchestrates saga execution with compensation support.
    """
    
    def __init__(self, client):
        self.client = client
        self._sagas: Dict[str, Saga] = {}
        self._instances: Dict[str, SagaInstance] = {}
        self._running = False
    
    def register_saga(self, saga: Saga):
        """Register a saga definition"""
        self._sagas[saga.name] = saga
    
    async def start_saga(
        self,
        saga_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new saga instance.
        
        Args:
            saga_name: Name of registered saga
            context: Initial context data
            
        Returns:
            Saga instance ID
        """
        saga_def = self._sagas.get(saga_name)
        if not saga_def:
            raise ValueError(f"Unknown saga: {saga_name}")
        
        instance = saga_def.build(context)
        instance.status = SagaStatus.RUNNING
        instance.started_at = datetime.utcnow().isoformat()
        
        self._instances[instance.saga_id] = instance
        
        # Start execution
        asyncio.create_task(self._execute_saga(instance.saga_id))
        
        logger.info(f"Started saga {saga_name} with ID {instance.saga_id}")
        return instance.saga_id
    
    async def _execute_saga(self, saga_id: str):
        """Execute saga steps"""
        instance = self._instances.get(saga_id)
        if not instance:
            logger.error(f"Saga instance not found: {saga_id}")
            return
        
        try:
            for i, step in enumerate(instance.steps):
                instance.current_step_index = i
                
                # Update step status
                step.status = StepStatus.EXECUTING
                step.started_at = datetime.utcnow().isoformat()
                
                logger.info(f"Executing saga step: {step.name}")
                
                try:
                    # Execute step
                    result = await step.action(instance.context)
                    
                    # Update step status
                    step.status = StepStatus.COMPLETED
                    step.result = result
                    step.completed_at = datetime.utcnow().isoformat()
                    
                    # Update context with result
                    instance.context[f"{step.name}_result"] = result
                    
                    logger.info(f"Saga step completed: {step.name}")
                    
                except Exception as e:
                    logger.exception(f"Saga step failed: {step.name}")
                    
                    step.status = StepStatus.FAILED
                    step.error = str(e)
                    
                    # Trigger compensation
                    await self._compensate_saga(saga_id)
                    return
            
            # All steps completed
            instance.status = SagaStatus.COMPLETED
            instance.completed_at = datetime.utcnow().isoformat()
            
            logger.info(f"Saga completed: {saga_id}")
            
        except Exception as e:
            logger.exception(f"Saga execution failed: {e}")
            instance.status = SagaStatus.FAILED
    
    async def _compensate_saga(self, saga_id: str):
        """Execute compensation for failed saga"""
        instance = self._instances.get(saga_id)
        if not instance:
            return
        
        instance.status = SagaStatus.COMPENSATING
        
        logger.info(f"Starting compensation for saga: {saga_id}")
        
        # Compensate in reverse order
        for step in reversed(instance.steps[:instance.current_step_index + 1]):
            if step.compensation and step.status == StepStatus.COMPLETED:
                step.status = StepStatus.COMPENSATING
                
                try:
                    await step.compensation(instance.context)
                    step.status = StepStatus.COMPENSATED
                    
                    logger.info(f"Compensation completed for step: {step.name}")
                    
                except Exception as e:
                    logger.exception(f"Compensation failed for step {step.name}: {e}")
                    # Log but continue - compensation failures need manual intervention
        
        instance.status = SagaStatus.COMPENSATED
        instance.completed_at = datetime.utcnow().isoformat()
        
        logger.info(f"Saga compensation completed: {saga_id}")
    
    def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Get saga instance status"""
        instance = self._instances.get(saga_id)
        if not instance:
            return None
        
        return {
            "saga_id": instance.saga_id,
            "saga_type": instance.saga_type,
            "status": instance.status.value,
            "current_step": instance.steps[instance.current_step_index].name if instance.current_step_index < len(instance.steps) else None,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "error": s.error,
                    "started_at": s.started_at,
                    "completed_at": s.completed_at
                }
                for s in instance.steps
            ],
            "started_at": instance.started_at,
            "completed_at": instance.completed_at
        }


# Example: Incident Resolution Saga
class IncidentResolutionSaga:
    """
    Saga for incident resolution workflow.
    
    Steps:
    1. Create incident
    2. Notify on-call team
    3. Create alert
    4. Update monitoring dashboard
    5. Send acknowledgment to reporter
    """
    
    @staticmethod
    def create(client) -> Saga:
        """Create incident resolution saga"""
        saga = Saga("incident_resolution")
        
        # Step 1: Create incident
        saga.step(
            name="create_incident",
            action=IncidentResolutionSaga._create_incident,
            compensation=IncidentResolutionSaga._compensate_create_incident
        )
        
        # Step 2: Notify on-call team
        saga.step(
            name="notify_oncall",
            action=IncidentResolutionSaga._notify_oncall,
            compensation=IncidentResolutionSaga._compensate_notify_oncall
        )
        
        # Step 3: Create alert
        saga.step(
            name="create_alert",
            action=IncidentResolutionSaga._create_alert,
            compensation=IncidentResolutionSaga._compensate_create_alert
        )
        
        # Step 4: Update dashboard
        saga.step(
            name="update_dashboard",
            action=IncidentResolutionSaga._update_dashboard
        )
        
        # Step 5: Send acknowledgment
        saga.step(
            name="send_acknowledgment",
            action=IncidentResolutionSaga._send_acknowledgment
        )
        
        return saga
    
    @staticmethod
    async def _create_incident(context: Dict[str, Any]) -> Dict[str, Any]:
        """Create incident in system"""
        # Simulate incident creation
        incident_id = str(uuid.uuid4())
        logger.info(f"Created incident: {incident_id}")
        return {"incident_id": incident_id}
    
    @staticmethod
    async def _compensate_create_incident(context: Dict[str, Any]):
        """Compensate incident creation"""
        incident_id = context.get("create_incident_result", {}).get("incident_id")
        logger.info(f"Compensating incident creation: {incident_id}")
        # Delete incident
    
    @staticmethod
    async def _notify_oncall(context: Dict[str, Any]) -> Dict[str, Any]:
        """Notify on-call team"""
        incident_id = context.get("create_incident_result", {}).get("incident_id")
        logger.info(f"Notifying on-call team for incident: {incident_id}")
        return {"notification_sent": True}
    
    @staticmethod
    async def _compensate_notify_oncall(context: Dict[str, Any]):
        """Compensate notification"""
        logger.info("Compensating notification")
        # Send cancellation notification
    
    @staticmethod
    async def _create_alert(context: Dict[str, Any]) -> Dict[str, Any]:
        """Create alert"""
        incident_id = context.get("create_incident_result", {}).get("incident_id")
        alert_id = str(uuid.uuid4())
        logger.info(f"Created alert {alert_id} for incident: {incident_id}")
        return {"alert_id": alert_id}
    
    @staticmethod
    async def _compensate_create_alert(context: Dict[str, Any]):
        """Compensate alert creation"""
        alert_id = context.get("create_alert_result", {}).get("alert_id")
        logger.info(f"Compensating alert creation: {alert_id}")
        # Delete alert
    
    @staticmethod
    async def _update_dashboard(context: Dict[str, Any]) -> Dict[str, Any]:
        """Update monitoring dashboard"""
        logger.info("Updating dashboard")
        return {"dashboard_updated": True}
    
    @staticmethod
    async def _send_acknowledgment(context: Dict[str, Any]) -> Dict[str, Any]:
        """Send acknowledgment to reporter"""
        incident_id = context.get("create_incident_result", {}).get("incident_id")
        logger.info(f"Sending acknowledgment for incident: {incident_id}")
        return {"acknowledgment_sent": True}


# Example: Alert Escalation Saga
class AlertEscalationSaga:
    """
    Saga for alert escalation workflow.
    
    Steps:
    1. Escalate alert severity
    2. Notify higher-level team
    3. Create incident if needed
    4. Update SLA tracking
    """
    
    @staticmethod
    def create(client) -> Saga:
        """Create alert escalation saga"""
        saga = Saga("alert_escalation")
        
        saga.step(
            name="escalate_alert",
            action=AlertEscalationSaga._escalate_alert,
            compensation=AlertEscalationSaga._compensate_escalate
        )
        
        saga.step(
            name="notify_team",
            action=AlertEscalationSaga._notify_team
        )
        
        saga.step(
            name="create_incident_if_needed",
            action=AlertEscalationSaga._create_incident_if_needed
        )
        
        saga.step(
            name="update_sla",
            action=AlertEscalationSaga._update_sla
        )
        
        return saga
    
    @staticmethod
    async def _escalate_alert(context: Dict[str, Any]) -> Dict[str, Any]:
        alert_id = context.get("alert_id")
        new_severity = context.get("new_severity", "HIGH")
        logger.info(f"Escalating alert {alert_id} to {new_severity}")
        return {"escalated": True, "previous_severity": "MEDIUM"}
    
    @staticmethod
    async def _compensate_escalate(context: Dict[str, Any]):
        alert_id = context.get("alert_id")
        logger.info(f"Reverting escalation for alert {alert_id}")
    
    @staticmethod
    async def _notify_team(context: Dict[str, Any]) -> Dict[str, Any]:
        alert_id = context.get("alert_id")
        logger.info(f"Notifying team for escalated alert {alert_id}")
        return {"notified": True}
    
    @staticmethod
    async def _create_incident_if_needed(context: Dict[str, Any]) -> Dict[str, Any]:
        alert_id = context.get("alert_id")
        new_severity = context.get("new_severity")
        
        if new_severity == "CRITICAL":
            incident_id = str(uuid.uuid4())
            logger.info(f"Created incident {incident_id} for critical alert {alert_id}")
            return {"incident_created": True, "incident_id": incident_id}
        
        return {"incident_created": False}
    
    @staticmethod
    async def _update_sla(context: Dict[str, Any]) -> Dict[str, Any]:
        alert_id = context.get("alert_id")
        logger.info(f"Updating SLA for alert {alert_id}")
        return {"sla_updated": True}
```

---

## 13. Deployment Guide

### 13.1 Docker Compose Configuration

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/docker-compose.yml
version: '3.8'

services:
  # RabbitMQ Cluster
  rabbitmq-1:
    image: rabbitmq:3.12-management-alpine
    hostname: rabbitmq-1
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_ERLANG_COOKIE: "resilience-ai-cluster-cookie"
      RABBITMQ_DEFAULT_USER: "admin"
      RABBITMQ_DEFAULT_PASS: "admin"
    volumes:
      - rabbitmq-1-data:/var/lib/rabbitmq
      - ./rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf
      - ./rabbitmq/definitions.json:/etc/rabbitmq/definitions.json
    networks:
      - messaging-network

  rabbitmq-2:
    image: rabbitmq:3.12-management-alpine
    hostname: rabbitmq-2
    environment:
      RABBITMQ_ERLANG_COOKIE: "resilience-ai-cluster-cookie"
      RABBITMQ_DEFAULT_USER: "admin"
      RABBITMQ_DEFAULT_PASS: "admin"
    volumes:
      - rabbitmq-2-data:/var/lib/rabbitmq
      - ./rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf
    networks:
      - messaging-network

  rabbitmq-3:
    image: rabbitmq:3.12-management-alpine
    hostname: rabbitmq-3
    environment:
      RABBITMQ_ERLANG_COOKIE: "resilience-ai-cluster-cookie"
      RABBITMQ_DEFAULT_USER: "admin"
      RABBITMQ_DEFAULT_PASS: "admin"
    volumes:
      - rabbitmq-3-data:/var/lib/rabbitmq
      - ./rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf
    networks:
      - messaging-network

  # Kafka Cluster
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log
    networks:
      - messaging-network

  kafka-1:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka-1
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_NUM_PARTITIONS: 12
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
      KAFKA_COMPRESSION_TYPE: lz4
    volumes:
      - kafka-1-data:/var/lib/kafka/data
    networks:
      - messaging-network
    depends_on:
      - zookeeper

  kafka-2:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka-2
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-2:29092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
    volumes:
      - kafka-2-data:/var/lib/kafka/data
    networks:
      - messaging-network
    depends_on:
      - zookeeper

  kafka-3:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka-3
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-3:29092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
    volumes:
      - kafka-3-data:/var/lib/kafka/data
    networks:
      - messaging-network
    depends_on:
      - zookeeper

  # Kafka UI
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: resilience-ai
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka-1:29092,kafka-2:29092,kafka-3:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    networks:
      - messaging-network
    depends_on:
      - kafka-1
      - kafka-2
      - kafka-3

  # Prometheus for monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - messaging-network

  # Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - messaging-network
    depends_on:
      - prometheus

  # ResilienceAI Messaging Service
  messaging-service:
    build:
      context: .
      dockerfile: Dockerfile.messaging
    environment:
      RABBITMQ_HOST: rabbitmq-1
      RABBITMQ_PORT: 5672
      RABBITMQ_USER: admin
      RABBITMQ_PASS: admin
      KAFKA_BOOTSTRAP_SERVERS: kafka-1:29092,kafka-2:29092,kafka-3:29092
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    networks:
      - messaging-network
    depends_on:
      - rabbitmq-1
      - kafka-1

volumes:
  rabbitmq-1-data:
  rabbitmq-2-data:
  rabbitmq-3-data:
  zookeeper-data:
  zookeeper-logs:
  kafka-1-data:
  kafka-2-data:
  kafka-3-data:
  prometheus-data:
  grafana-data:

networks:
  messaging-network:
    driver: bridge
```

### 13.2 Kubernetes Deployment

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/k8s/rabbitmq-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: rabbitmq
  namespace: resilience-ai
spec:
  serviceName: rabbitmq
  replicas: 3
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
      - name: rabbitmq
        image: rabbitmq:3.12-management-alpine
        ports:
        - containerPort: 5672
          name: amqp
        - containerPort: 15672
          name: management
        env:
        - name: RABBITMQ_ERLANG_COOKIE
          valueFrom:
            secretKeyRef:
              name: rabbitmq-secret
              key: erlang-cookie
        - name: RABBITMQ_DEFAULT_USER
          valueFrom:
            secretKeyRef:
              name: rabbitmq-secret
              key: username
        - name: RABBITMQ_DEFAULT_PASS
          valueFrom:
            secretKeyRef:
              name: rabbitmq-secret
              key: password
        volumeMounts:
        - name: rabbitmq-data
          mountPath: /var/lib/rabbitmq
        - name: rabbitmq-config
          mountPath: /etc/rabbitmq/rabbitmq.conf
          subPath: rabbitmq.conf
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - rabbitmq-diagnostics
            - ping
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          exec:
            command:
            - rabbitmq-diagnostics
            - status
          initialDelaySeconds: 10
          periodSeconds: 10
  volumeClaimTemplates:
  - metadata:
      name: rabbitmq-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq
  namespace: resilience-ai
spec:
  selector:
    app: rabbitmq
  ports:
  - port: 5672
    name: amqp
  - port: 15672
    name: management
  clusterIP: None
---
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq-management
  namespace: resilience-ai
spec:
  selector:
    app: rabbitmq
  ports:
  - port: 15672
    targetPort: 15672
  type: LoadBalancer
```

```yaml
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/k8s/kafka-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
  namespace: resilience-ai
spec:
  serviceName: kafka
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
          name: kafka
        env:
        - name: KAFKA_BROKER_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: KAFKA_ZOOKEEPER_CONNECT
          value: "zookeeper:2181"
        - name: KAFKA_ADVERTISED_LISTENERS
          value: "PLAINTEXT://$(POD_NAME).kafka:9092"
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR
          value: "3"
        - name: KAFKA_DEFAULT_REPLICATION_FACTOR
          value: "3"
        - name: KAFKA_MIN_INSYNC_REPLICAS
          value: "2"
        - name: KAFKA_NUM_PARTITIONS
          value: "12"
        volumeMounts:
        - name: kafka-data
          mountPath: /var/lib/kafka/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "4000m"
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
  name: kafka
  namespace: resilience-ai
spec:
  selector:
    app: kafka
  ports:
  - port: 9092
    name: kafka
  clusterIP: None
```

### 13.3 Configuration Files

```ini
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/config/rabbitmq.conf
# RabbitMQ Configuration for ResilienceAI

# Network
listeners.tcp.default = 5672
management.tcp.port = 15672

# Memory and Disk
vm_memory_high_watermark.relative = 0.7
vm_memory_high_watermark_paging_ratio = 0.5
disk_free_limit.absolute = 2GB

# Queues
queue_master_locator = min-masters
lazy_queue_explicit_gc_run_operation_threshold = 1000

# Clustering
cluster_partition_handling = autoheal
cluster_keepalive_interval = 10000

# Mnesia
mnesia_table_loading_retry_timeout = 15000
mnesia_table_loading_retry_limit = 10

# Logging
log.console = true
log.console.level = info
log.file.level = debug

# Heartbeat
heartbeat = 600

# Consumer timeout
consumer_timeout = 1800000
```

```json
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/config/rabbitmq-definitions.json
{
  "rabbit_version": "3.12.0",
  "rabbitmq_version": "3.12.0",
  "product_name": "RabbitMQ",
  "product_version": "3.12.0",
  "users": [
    {
      "name": "admin",
      "password_hash": "...",
      "hashing_algorithm": "rabbit_password_hashing_sha256",
      "tags": "administrator"
    },
    {
      "name": "resilience-ai",
      "password_hash": "...",
      "hashing_algorithm": "rabbit_password_hashing_sha256",
      "tags": ""
    }
  ],
  "vhosts": [
    {
      "name": "/"
    }
  ],
  "permissions": [
    {
      "user": "admin",
      "vhost": "/",
      "configure": ".*",
      "write": ".*",
      "read": ".*"
    },
    {
      "user": "resilience-ai",
      "vhost": "/",
      "configure": "^resilience\\..*|^incidents\\..*|^alerts\\..*|^notifications\\..*",
      "write": "^resilience\\..*|^incidents\\..*|^alerts\\..*|^notifications\\..*",
      "read": "^resilience\\..*|^incidents\\..*|^alerts\\..*|^notifications\\..*"
    }
  ],
  "exchanges": [
    {
      "name": "resilience.direct",
      "vhost": "/",
      "type": "direct",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {}
    },
    {
      "name": "resilience.topic",
      "vhost": "/",
      "type": "topic",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {}
    },
    {
      "name": "resilience.dlx",
      "vhost": "/",
      "type": "topic",
      "durable": true,
      "auto_delete": false,
      "internal": false,
      "arguments": {}
    }
  ],
  "queues": [
    {
      "name": "dlq.main",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-message-ttl": 604800000,
        "x-max-length": 1000000
      }
    }
  ],
  "bindings": [
    {
      "source": "resilience.dlx",
      "vhost": "/",
      "destination": "dlq.main",
      "destination_type": "queue",
      "routing_key": "#",
      "arguments": {}
    }
  ]
}
```

---

## 14. Implementation Priority

### 14.1 Phase 1: Core Infrastructure (Weeks 1-2)

| Priority | Component | Effort | Dependencies |
|----------|-----------|--------|--------------|
| P0 | RabbitMQ Client | 3 days | None |
| P0 | Basic Producer/Consumer | 2 days | RabbitMQ Client |
| P0 | Queue Configuration | 1 day | RabbitMQ Client |
| P0 | Dead Letter Queue | 2 days | RabbitMQ Client |
| P1 | Message Routing | 2 days | RabbitMQ Client |
| P1 | Basic Monitoring | 2 days | RabbitMQ Client |

### 14.2 Phase 2: Advanced Patterns (Weeks 3-4)

| Priority | Component | Effort | Dependencies |
|----------|-----------|--------|--------------|
| P1 | Kafka Integration | 3 days | None |
| P1 | Consumer Patterns | 2 days | RabbitMQ Client |
| P1 | Scalability Patterns | 3 days | Consumer Patterns |
| P2 | Event Sourcing | 3 days | Kafka Integration |
| P2 | Persistence Layer | 2 days | Event Sourcing |

### 14.3 Phase 3: Enterprise Features (Weeks 5-6)

| Priority | Component | Effort | Dependencies |
|----------|-----------|--------|--------------|
| P1 | Saga Patterns | 3 days | RabbitMQ Client |
| P2 | Advanced Monitoring | 2 days | Basic Monitoring |
| P2 | Stream Processing | 3 days | Kafka Integration |
| P3 | Auto-scaling | 2 days | Scalability Patterns |
| P3 | Multi-region | 3 days | All above |

### 14.4 Implementation Checklist

```python
# /mnt/okcomputer/output/resilience_ai_analysis/messaging/implementation_checklist.py
"""
Implementation Checklist for ResilienceAI Message Queue
"""

IMPLEMENTATION_CHECKLIST = {
    "Phase 1: Core Infrastructure": {
        "RabbitMQ Client": {
            "Connection Pool": False,
            "Channel Management": False,
            "Error Handling": False,
            "Reconnection Logic": False,
        },
        "Producer Patterns": {
            "Simple Publish": False,
            "Batch Publish": False,
            "Priority Messages": False,
            "Delayed Messages": False,
        },
        "Consumer Patterns": {
            "Basic Consumer": False,
            "Competing Consumers": False,
            "Circuit Breaker": False,
            "Rate Limiting": False,
        },
        "Dead Letter Queue": {
            "DLQ Infrastructure": False,
            "Retry Logic": False,
            "Retry Queues": False,
            "DLQ Monitoring": False,
        },
        "Message Routing": {
            "Direct Routing": False,
            "Topic Routing": False,
            "Header Routing": False,
            "Content-Based Routing": False,
        },
    },
    "Phase 2: Advanced Patterns": {
        "Kafka Integration": {
            "Producer": False,
            "Consumer": False,
            "Admin Client": False,
            "Topic Management": False,
        },
        "Stream Processing": {
            "KStream Abstraction": False,
            "KTable Abstraction": False,
            "Windowed Aggregation": False,
            "Stream Joins": False,
        },
        "Event Sourcing": {
            "Event Store": False,
            "Aggregate Roots": False,
            "Projections": False,
            "Event Replay": False,
        },
        "Scalability": {
            "Partitioning": False,
            "Load Balancing": False,
            "Consumer Groups": False,
            "Backpressure": False,
        },
    },
    "Phase 3: Enterprise Features": {
        "Saga Patterns": {
            "Saga Orchestrator": False,
            "Compensation Logic": False,
            "Saga Monitoring": False,
            "Saga Recovery": False,
        },
        "Monitoring": {
            "Metrics Collection": False,
            "Health Checks": False,
            "Distributed Tracing": False,
            "Alerting": False,
        },
        "Operations": {
            "Docker Compose": False,
            "Kubernetes Manifests": False,
            "Configuration Management": False,
            "Documentation": False,
        },
    },
}


def print_checklist():
    """Print implementation checklist"""
    for phase, components in IMPLEMENTATION_CHECKLIST.items():
        print(f"\n{'='*60}")
        print(f"{phase}")
        print('='*60)
        
        for component, items in components.items():
            print(f"\n  {component}:")
            for item, completed in items.items():
                status = "[x]" if completed else "[ ]"
                print(f"    {status} {item}")


def get_completion_percentage() -> float:
    """Get overall completion percentage"""
    total = 0
    completed = 0
    
    for phase, components in IMPLEMENTATION_CHECKLIST.items():
        for component, items in components.items():
            for item, done in items.items():
                total += 1
                if done:
                    completed += 1
    
    return (completed / total * 100) if total > 0 else 0


if __name__ == "__main__":
    print_checklist()
    print(f"\nOverall Completion: {get_completion_percentage():.1f}%")
```

---

## Summary

This document provides a comprehensive message queue integration design for ResilienceAI, covering:

1. **Architecture Overview**: High-level design with RabbitMQ and Kafka integration
2. **RabbitMQ Integration**: Complete client implementation with connection pooling
3. **Kafka Integration**: Producer, consumer, and stream processing capabilities
4. **Producer/Consumer Patterns**: Multiple patterns for different use cases
5. **Message Routing**: Intelligent routing with conditions and transformations
6. **Dead Letter Queues**: Comprehensive DLQ implementation with retry logic
7. **Message Persistence**: Event journaling and recovery capabilities
8. **Scalability Patterns**: Partitioning, load balancing, and auto-scaling
9. **Monitoring**: Metrics, tracing, and health checks
10. **Event Sourcing**: Complete event store and projection system
11. **Saga Patterns**: Distributed transaction coordination
12. **Deployment Guide**: Docker Compose and Kubernetes configurations
13. **Implementation Priority**: Phased approach for incremental delivery

### Key Files Created

- `/mnt/okcomputer/output/resilience_ai_analysis/55_message_queue.md` - This comprehensive document
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/queue_selector.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/rabbitmq_client.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/rabbitmq_config.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/kafka_client.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/kafka_streams.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/producer_patterns.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/consumer_patterns.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/message_router.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/dead_letter_queue.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/persistence.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/scalability.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/monitoring.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/event_sourcing.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/saga_orchestrator.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/docker-compose.yml`
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/k8s/` - Kubernetes manifests
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/config/` - Configuration files
- `/mnt/okcomputer/output/resilience_ai_analysis/messaging/implementation_checklist.py`

### Next Steps

1. Implement Phase 1 components (Core Infrastructure)
2. Set up RabbitMQ and Kafka clusters using provided Docker Compose
3. Implement basic producer/consumer patterns
4. Add monitoring and alerting
5. Progress through Phase 2 and Phase 3 based on requirements
