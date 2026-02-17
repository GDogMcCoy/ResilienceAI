# ResilienceAI Background Job System

## Executive Summary

This document provides a comprehensive design for the ResilienceAI background job system using Celery, a distributed task queue. The system handles async processing, long-running tasks, and scheduled jobs with robust retry mechanisms, monitoring, and dead letter queues.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Task Queue Design](#task-queue-design)
3. [Task Definitions](#task-definitions)
4. [Scheduling System](#scheduling-system)
5. [Retry Mechanisms](#retry-mechanisms)
6. [Monitoring & Observability](#monitoring--observability)
7. [Task Priorities](#task-priorities)
8. [Task Chains & Groups](#task-chains--groups)
9. [Result Backends](#result-backends)
10. [Task Routing](#task-routing)
11. [Dead Letter Queues](#dead-letter-queues)
12. [Implementation Guide](#implementation-guide)
13. [Deployment Configuration](#deployment-configuration)

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ResilienceAI Background Job System                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Web API    │    │  Scheduler   │    │   Workers    │                  │
│  │   (FastAPI)  │    │  (Beat)      │    │  (Celery)    │                  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│         │                   │                   │                          │
│         │  enqueue_task()   │  schedule_task()  │  process_task()          │
│         │                   │                   │                          │
│         ▼                   ▼                   ▼                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Message Broker (Redis/RabbitMQ)                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │   default   │  │   high      │  │   low       │  │   beat     │  │   │
│  │  │   queue     │  │   priority  │  │   priority  │  │   schedule │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                   │                   │                          │
│         ▼                   ▼                   ▼                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Result Backend (Redis)                        │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │  task_id    │  │  status     │  │  result     │                  │   │
│  │  │  → result   │  │  → state    │  │  → data     │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                  │
│         ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Dead Letter Queue (MongoDB)                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │  failed     │  │  retry      │  │  permanent  │                  │   │
│  │  │  tasks      │  │  exhausted  │  │  failures   │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Technology | Purpose |
|-----------|------------|---------|
| Message Broker | Redis 7.x / RabbitMQ 3.12 | Task queue storage and distribution |
| Task Workers | Celery 5.3+ | Task execution engine |
| Scheduler | Celery Beat | Periodic task scheduling |
| Result Backend | Redis 7.x | Task result storage |
| Dead Letter Queue | MongoDB | Failed task persistence |
| Monitoring | Flower + Prometheus | Task monitoring and metrics |

---

## Task Queue Design

### Queue Architecture

```python
# File: /app/core/celery_config.py
"""
Celery configuration for ResilienceAI background job system.
"""

from celery import Celery
from kombu import Queue, Exchange
from datetime import timedelta
import os

# Initialize Celery app
celery_app = Celery('resilienceai')

# Configure from object
celery_app.config_from_object('app.core.celery_settings')

# Define task queues with priorities
CELERY_QUEUES = (
    # High priority queue for critical tasks
    Queue(
        'high_priority',
        Exchange('high_priority'),
        routing_key='high_priority',
        queue_arguments={'x-max-priority': 10}
    ),
    
    # Default queue for normal tasks
    Queue(
        'default',
        Exchange('default'),
        routing_key='default',
        queue_arguments={'x-max-priority': 5}
    ),
    
    # Low priority queue for background tasks
    Queue(
        'low_priority',
        Exchange('low_priority'),
        routing_key='low_priority',
        queue_arguments={'x-max-priority': 3}
    ),
    
    # Specialized queues
    Queue('ml_inference', Exchange('ml_inference'), routing_key='ml_inference'),
    Queue('data_processing', Exchange('data_processing'), routing_key='data_processing'),
    Queue('notifications', Exchange('notifications'), routing_key='notifications'),
    Queue('reports', Exchange('reports'), routing_key='reports'),
)

# Task routes for automatic routing
def route_task(name, args, kwargs, options, task=None, **kw):
    """Dynamic task routing based on task name."""
    if 'ml' in name or 'inference' in name or 'model' in name:
        return {'queue': 'ml_inference', 'priority': 8}
    elif 'notification' in name or 'email' in name or 'alert' in name:
        return {'queue': 'notifications', 'priority': 6}
    elif 'report' in name or 'analytics' in name:
        return {'queue': 'reports', 'priority': 2}
    elif 'data' in name or 'process' in name or 'etl' in name:
        return {'queue': 'data_processing', 'priority': 4}
    return {'queue': 'default', 'priority': 5}

# Celery configuration
celery_app.conf.update(
    # Broker settings
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_transport_options={
        'visibility_timeout': 43200,  # 12 hours
        'queue_order_strategy': 'priority',
    },
    
    # Result backend settings
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
    result_expires=timedelta(days=7),
    result_extended=True,
    result_backend_always_retry=True,
    result_backend_max_retries=10,
    
    # Task settings
    task_serializer='json',
    accept_content=['json', 'pickle'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max execution time
    task_soft_time_limit=3300,  # 55 minutes soft limit
    task_always_eager=False,
    task_store_eager_result=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_max_memory_per_child=500000,  # 500MB max memory per worker
    
    # Acknowledgment settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_acks_on_failure_or_timeout=False,
    
    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,
    task_retry_backoff=True,
    task_retry_backoff_max=600,
    task_retry_jitter=True,
    
    # Queue settings
    task_default_queue='default',
    task_queues=CELERY_QUEUES,
    task_routes=(route_task,),
    
    # Event settings
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Beat scheduler settings
    beat_schedule_filename='/var/lib/celery/beat-schedule',
    beat_max_loop_interval=300,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.tasks'])
```

---

## Task Definitions

### Base Task Class

```python
# File: /app/tasks/base.py
"""
Base task class with common functionality for all ResilienceAI tasks.
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime
from celery import Task
from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded

from app.core.monitoring import metrics
from app.core.dead_letter_queue import DeadLetterQueue

logger = logging.getLogger(__name__)
dlq = DeadLetterQueue()


class ResilienceAITask(Task):
    """Base task class for ResilienceAI with enhanced error handling."""
    
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    max_retries = 3
    default_retry_delay = 60
    _start_time: Optional[datetime] = None
    
    def __call__(self, *args, **kwargs):
        """Execute the task with monitoring and error handling."""
        self._start_time = datetime.utcnow()
        
        self.update_state(
            state='STARTED',
            meta={
                'start_time': self._start_time.isoformat(),
                'args': str(args),
                'kwargs': str(kwargs),
            }
        )
        
        try:
            result = self.run(*args, **kwargs)
            self._record_success()
            return result
        except SoftTimeLimitExceeded:
            logger.error(f"Task {self.request.id} exceeded soft time limit")
            self._record_failure('time_limit_exceeded')
            raise
        except MaxRetriesExceededError:
            logger.error(f"Task {self.request.id} exceeded max retries")
            self._send_to_dlq(args, kwargs, 'max_retries_exceeded')
            raise
        except Exception as exc:
            logger.exception(f"Task {self.request.id} failed: {exc}")
            self._record_failure(type(exc).__name__)
            raise
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry."""
        logger.warning(f"Task {task_id} retrying ({self.request.retries}/{self.max_retries}): {exc}")
        metrics.increment('task_retry_count', labels={
            'task_name': self.name,
            'retry_count': str(self.request.retries)
        })
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Task {task_id} failed permanently: {exc}")
        self._send_to_dlq(args, kwargs, type(exc).__name__, str(exc), einfo)
        self._record_failure(type(exc).__name__)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        duration = (datetime.utcnow() - self._start_time).total_seconds() if self._start_time else 0
        logger.info(f"Task {task_id} completed successfully in {duration:.2f}s")
        metrics.timing('task_duration', duration, labels={'task_name': self.name})
        metrics.increment('task_success_count', labels={'task_name': self.name})
    
    def _record_success(self):
        metrics.increment('task_success_total', labels={'task_name': self.name})
    
    def _record_failure(self, error_type: str):
        metrics.increment('task_failure_total', labels={'task_name': self.name, 'error_type': error_type})
    
    def _send_to_dlq(self, args, kwargs, error_type: str, error_message: str = None, einfo=None):
        """Send failed task to dead letter queue."""
        dlq.store_failed_task(
            task_id=self.request.id,
            task_name=self.name,
            args=args,
            kwargs=kwargs,
            error_type=error_type,
            error_message=error_message,
            traceback=einfo.traceback if einfo else None,
            retry_count=self.request.retries,
            timestamp=datetime.utcnow()
        )


class MLTask(ResilienceAITask):
    """Base class for ML inference tasks."""
    max_retries = 5
    default_retry_delay = 30
    time_limit = 600
    soft_time_limit = 540


class DataProcessingTask(ResilienceAITask):
    """Base class for data processing tasks."""
    max_retries = 3
    default_retry_delay = 120
    time_limit = 3600
    soft_time_limit = 3300


class NotificationTask(ResilienceAITask):
    """Base class for notification tasks."""
    max_retries = 5
    default_retry_delay = 10
    time_limit = 60
    soft_time_limit = 50
    ignore_result = True


class ReportTask(ResilienceAITask):
    """Base class for report generation tasks."""
    max_retries = 2
    default_retry_delay = 300
    time_limit = 7200
    soft_time_limit = 6600
```

### Task Implementations

```python
# File: /app/tasks/ml_tasks.py
"""Machine learning related background tasks."""

import logging
from typing import Dict, List, Any
from app.core.celery_config import celery_app
from app.tasks.base import MLTask

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=MLTask, queue='ml_inference')
def run_model_inference(self, model_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run ML model inference on input data."""
    from app.services.model_registry import ModelRegistry
    
    logger.info(f"Running inference with model {model_id}")
    model = ModelRegistry().get_model(model_id)
    processed_input = model.preprocess(input_data)
    predictions = model.predict(processed_input)
    result = model.postprocess(predictions)
    
    return {
        'model_id': model_id,
        'predictions': result,
        'confidence': result.get('confidence', 0.0),
        'timestamp': self._start_time.isoformat() if self._start_time else None,
    }


@celery_app.task(bind=True, base=MLTask, queue='ml_inference')
def batch_inference(self, model_id: str, batch_data: List[Dict]) -> Dict[str, Any]:
    """Run batch inference on multiple inputs."""
    from app.services.model_registry import ModelRegistry
    
    logger.info(f"Running batch inference with model {model_id}, batch size: {len(batch_data)}")
    model = ModelRegistry().get_model(model_id)
    
    chunk_size = 100
    all_predictions = []
    
    for i in range(0, len(batch_data), chunk_size):
        chunk = batch_data[i:i + chunk_size]
        processed = [model.preprocess(d) for d in chunk]
        predictions = model.predict_batch(processed)
        all_predictions.extend(model.postprocess_batch(predictions))
    
    return {'model_id': model_id, 'batch_size': len(batch_data), 'predictions': all_predictions}


@celery_app.task(bind=True, base=MLTask, queue='ml_inference')
def evaluate_model(self, model_id: str, dataset_id: str) -> Dict[str, Any]:
    """Evaluate model performance on a dataset."""
    from app.services.model_registry import ModelRegistry
    from app.services.dataset_service import DatasetService
    from app.services.evaluation_service import EvaluationService
    
    logger.info(f"Evaluating model {model_id} on dataset {dataset_id}")
    model = ModelRegistry().get_model(model_id)
    dataset = DatasetService.load_dataset(dataset_id)
    metrics = model.evaluate(dataset)
    EvaluationService.store_results(model_id, dataset_id, metrics)
    
    return {'model_id': model_id, 'dataset_id': dataset_id, 'metrics': metrics}


@celery_app.task(bind=True, base=MLTask, queue='ml_inference')
def retrain_model(self, model_id: str, training_config: Dict[str, Any]) -> Dict[str, Any]:
    """Retrain a model with new data."""
    from app.services.training_service import TrainingService
    
    logger.info(f"Retraining model {model_id}")
    trainer = TrainingService()
    result = trainer.train(model_id, training_config)
    
    return {
        'model_id': model_id,
        'training_id': result['training_id'],
        'status': result['status'],
        'metrics': result.get('metrics'),
    }
```

---

## Scheduling System

### Periodic Task Configuration

```python
# File: /app/tasks/periodic_tasks.py
"""Periodic task definitions for Celery Beat."""

import logging
from datetime import datetime, timedelta
from app.core.celery_config import celery_app
from celery.schedules import crontab

logger = logging.getLogger(__name__)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up periodic tasks for Celery Beat."""
    
    # Health check every 5 minutes
    sender.add_periodic_task(300.0, health_check.s(), name='health-check', queue='high_priority')
    
    # Process daily metrics every hour
    sender.add_periodic_task(3600.0, process_daily_metrics.s(), name='process-daily-metrics', queue='data_processing')
    
    # Cleanup old results daily at 2 AM
    sender.add_periodic_task(crontab(hour=2, minute=0), cleanup_old_results.s(), name='cleanup-old-results', queue='low_priority')
    
    # Generate daily report at 6 AM
    sender.add_periodic_task(crontab(hour=6, minute=0), generate_daily_report.s(), name='generate-daily-report', queue='reports')
    
    # Check model performance every 30 minutes
    sender.add_periodic_task(1800.0, check_model_performance.s(), name='check-model-performance', queue='ml_inference')


@celery_app.task(queue='high_priority')
def health_check() -> Dict[str, Any]:
    """Perform system health check."""
    from app.services.health_service import HealthService
    from app.tasks.notification_tasks import send_alert
    
    health_service = HealthService()
    status = health_service.check_all()
    
    if not status['healthy']:
        send_alert.delay(
            alert_config={'channels': ['email', 'slack']},
            alert_data={'alert_name': 'System Health Check Failed', 'severity': 'critical', 'details': status}
        )
    
    return status


@celery_app.task(queue='data_processing')
def process_daily_metrics() -> Dict[str, Any]:
    """Process daily metrics aggregation."""
    from app.services.metrics_service import MetricsService
    
    metrics_service = MetricsService()
    yesterday = datetime.utcnow() - timedelta(days=1)
    result = metrics_service.process_daily_metrics(yesterday)
    
    return {'date': yesterday.date().isoformat(), 'metrics_processed': result['count']}


@celery_app.task(queue='low_priority')
def cleanup_old_results() -> Dict[str, Any]:
    """Clean up old task results from result backend."""
    from app.services.task_service import TaskService
    
    logger.info("Cleaning up old task results")
    task_service = TaskService()
    deleted = task_service.cleanup_old_tasks(days=30)
    
    return {'deleted_count': deleted}


@celery_app.task(queue='reports')
def generate_daily_report() -> Dict[str, Any]:
    """Generate daily system report."""
    from app.tasks.report_tasks import generate_analytics_report
    
    yesterday = datetime.utcnow() - timedelta(days=1)
    return generate_analytics_report.delay({
        'name': f'Daily Report - {yesterday.date()}',
        'time_range': {
            'start': yesterday.replace(hour=0, minute=0, second=0).isoformat(),
            'end': yesterday.replace(hour=23, minute=59, second=59).isoformat(),
        },
        'format': 'pdf',
    }).get()


@celery_app.task(queue='ml_inference')
def check_model_performance() -> Dict[str, Any]:
    """Check ML model performance and alert if degraded."""
    from app.services.model_monitoring_service import ModelMonitoringService
    from app.tasks.notification_tasks import send_alert
    
    monitoring = ModelMonitoringService()
    issues = monitoring.check_all_models()
    
    if issues:
        send_alert.delay(
            alert_config={'channels': ['email', 'slack']},
            alert_data={'alert_name': 'Model Performance Degraded', 'severity': 'warning', 'details': issues}
        )
    
    return {'issues_found': len(issues), 'issues': issues}
```

---

## Retry Mechanisms

```python
# File: /app/core/retry_config.py
"""Retry configuration and strategies for background tasks."""

import random
from typing import Callable, List
from functools import wraps
from celery.exceptions import MaxRetriesExceededError


class RetryStrategy:
    """Base class for retry strategies."""
    def get_delay(self, retry_count: int, base_delay: float) -> float:
        raise NotImplementedError


class ExponentialBackoffStrategy(RetryStrategy):
    """Exponential backoff with optional jitter."""
    def __init__(self, max_delay: float = 600, jitter: bool = True):
        self.max_delay = max_delay
        self.jitter = jitter
    
    def get_delay(self, retry_count: int, base_delay: float) -> float:
        delay = min(base_delay * (2 ** retry_count), self.max_delay)
        if self.jitter:
            delay = delay * (0.75 + random.random() * 0.5)
        return delay


class CustomBackoffStrategy(RetryStrategy):
    """Custom backoff with specific delays."""
    def __init__(self, delays: List[float]):
        self.delays = delays
    
    def get_delay(self, retry_count: int, base_delay: float) -> float:
        if retry_count < len(self.delays):
            return self.delays[retry_count]
        return self.delays[-1] if self.delays else base_delay


# Predefined retry strategies
RETRY_STRATEGIES = {
    'exponential': ExponentialBackoffStrategy(),
    'ml_inference': CustomBackoffStrategy([30, 60, 120, 300, 600]),
    'notification': CustomBackoffStrategy([10, 30, 60, 120, 300]),
    'data_processing': CustomBackoffStrategy([60, 120, 300, 600, 1800]),
}


class CircuitBreaker:
    """Circuit breaker pattern for preventing cascade failures."""
    
    STATE_CLOSED = 'closed'
    STATE_OPEN = 'open'
    STATE_HALF_OPEN = 'half_open'
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60, half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
    
    def can_execute(self) -> bool:
        if self.state == self.STATE_CLOSED:
            return True
        if self.state == self.STATE_OPEN:
            import time
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = self.STATE_HALF_OPEN
                self.success_count = 0
                return True
            return False
        if self.state == self.STATE_HALF_OPEN:
            return self.success_count < self.half_open_max_calls
        return False
    
    def record_success(self):
        self.failure_count = 0
        if self.state == self.STATE_HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                self.state = self.STATE_CLOSED
                self.success_count = 0
    
    def record_failure(self):
        self.failure_count += 1
        import time
        self.last_failure_time = time.time()
        if self.state == self.STATE_HALF_OPEN:
            self.state = self.STATE_OPEN
        elif self.failure_count >= self.failure_threshold:
            self.state = self.STATE_OPEN
```

---

## Monitoring & Observability

```python
# File: /app/core/monitoring.py
"""Monitoring and metrics collection for background jobs."""

import logging
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, start_http_server

logger = logging.getLogger(__name__)

# Prometheus metrics
TASK_COUNTER = Counter('celery_task_total', 'Total number of Celery tasks', ['task_name', 'status'])
TASK_DURATION = Histogram('celery_task_duration_seconds', 'Task execution duration', ['task_name'])
TASK_RETRY_COUNTER = Counter('celery_task_retry_total', 'Total number of task retries', ['task_name', 'retry_count'])
QUEUE_SIZE = Gauge('celery_queue_size', 'Current size of Celery queues', ['queue_name'])


class MetricsCollector:
    """Collect and expose metrics for background jobs."""
    
    def __init__(self, port: int = 9090):
        self.port = port
        self._started = False
    
    def start(self):
        if not self._started:
            start_http_server(self.port)
            self._started = True
            logger.info(f"Metrics server started on port {self.port}")
    
    def increment(self, metric_name: str, labels: Dict[str, str] = None, value: int = 1):
        if metric_name == 'task_total':
            TASK_COUNTER.labels(**labels).inc(value)
        elif metric_name == 'task_retry_count':
            TASK_RETRY_COUNTER.labels(**labels).inc(value)
    
    def timing(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        if metric_name == 'task_duration':
            TASK_DURATION.labels(**labels).observe(value)
    
    def gauge(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        if metric_name == 'queue_size':
            QUEUE_SIZE.labels(**labels).set(value)
    
    @contextmanager
    def timer(self, metric_name: str, labels: Dict[str, str] = None):
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.timing(metric_name, duration, labels)


# Global metrics instance
metrics = MetricsCollector()
```

---

## Task Priorities

```python
# File: /app/core/priority_config.py
"""Task priority configuration for ResilienceAI."""

from enum import IntEnum
from typing import Dict, Any


class TaskPriority(IntEnum):
    """Task priority levels (higher = more important)."""
    CRITICAL = 10
    HIGH = 8
    NORMAL = 5
    LOW = 3
    BACKGROUND = 1


PRIORITY_QUEUES = {
    TaskPriority.CRITICAL: 'high_priority',
    TaskPriority.HIGH: 'high_priority',
    TaskPriority.NORMAL: 'default',
    TaskPriority.LOW: 'low_priority',
    TaskPriority.BACKGROUND: 'low_priority',
}


def get_queue_for_priority(priority: TaskPriority) -> str:
    return PRIORITY_QUEUES.get(priority, 'default')


def apply_priority(task_options: Dict[str, Any], priority: TaskPriority = None) -> Dict[str, Any]:
    """Apply priority settings to task options."""
    options = task_options.copy()
    if priority is None:
        priority = TaskPriority.NORMAL
    options['priority'] = int(priority)
    options['queue'] = get_queue_for_priority(priority)
    return options
```

---

## Task Chains & Groups

```python
# File: /app/core/workflows.py
"""Task workflow patterns using Celery chains and groups."""

import logging
from typing import List, Dict, Any
from celery import chain, group, chord, signature

logger = logging.getLogger(__name__)


class WorkflowBuilder:
    """Builder for creating complex task workflows."""
    
    def __init__(self):
        self.tasks = []
    
    def add_task(self, task_name: str, args: tuple = None, kwargs: dict = None, options: dict = None):
        sig = signature(task_name, args=args, kwargs=kwargs, options=options)
        self.tasks.append(sig)
        return self
    
    def add_parallel(self, tasks: List[Dict[str, Any]]):
        signatures = [signature(t['name'], args=t.get('args'), kwargs=t.get('kwargs')) for t in tasks]
        self.tasks.append(group(signatures))
        return self
    
    def build_chain(self):
        if not self.tasks:
            raise ValueError("No tasks added to workflow")
        return chain(*self.tasks)
    
    def run(self):
        workflow = self.build_chain()
        return workflow.apply_async()


# Predefined workflows
class MLWorkflows:
    """Machine learning specific workflows."""
    
    @staticmethod
    def inference_pipeline(model_id: str, input_data: Dict, notification_emails: List[str] = None):
        """Complete ML inference pipeline with notifications."""
        workflow = chain(
            signature('app.tasks.ml_tasks.run_model_inference', args=[model_id, input_data]),
            signature('app.tasks.data_tasks.process_inference_results'),
            signature('app.tasks.data_tasks.store_results'),
        )
        
        if notification_emails:
            workflow = chain(workflow, signature('app.tasks.notification_tasks.send_email',
                                                 args=[notification_emails, 'Inference Complete', '']))
        
        return workflow.apply_async()
    
    @staticmethod
    def batch_evaluation(model_ids: List[str], dataset_id: str):
        """Evaluate multiple models on a dataset in parallel."""
        eval_tasks = group(signature('app.tasks.ml_tasks.evaluate_model', args=[m, dataset_id]) for m in model_ids)
        callback = signature('app.tasks.report_tasks.generate_comparison_report', args=[dataset_id])
        return chord(eval_tasks)(callback)


class DataWorkflows:
    """Data processing workflows."""
    
    @staticmethod
    def etl_pipeline(source_config: Dict, transform_config: Dict, destination_config: Dict):
        """Complete ETL pipeline."""
        return chain(
            signature('app.tasks.data_tasks.extract_data', args=[source_config]),
            signature('app.tasks.data_tasks.transform_data', args=[transform_config]),
            signature('app.tasks.data_tasks.load_data', args=[destination_config]),
            signature('app.tasks.data_tasks.validate_loaded_data'),
        ).apply_async()
```

---

## Result Backends

```python
# File: /app/core/result_backend.py
"""Result backend configuration and utilities."""

import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from app.core.celery_config import celery_app


class ResultBackendManager:
    """Manager for task result backend operations."""
    
    def __init__(self):
        self.backend = celery_app.backend
    
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        result = self.backend.get_task_meta(task_id)
        if result:
            return {
                'task_id': task_id,
                'status': result.get('status'),
                'result': result.get('result'),
                'traceback': result.get('traceback'),
                'date_done': result.get('date_done'),
            }
        return None
    
    def delete_result(self, task_id: str):
        self.backend.forget(task_id)


class ResultCache:
    """Cache for frequently accessed task results."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, task_id: str) -> Optional[Any]:
        if task_id in self._cache:
            entry = self._cache[task_id]
            if datetime.utcnow() < entry['expires_at']:
                return entry['result']
            del self._cache[task_id]
        return None
    
    def set(self, task_id: str, result: Any):
        self._cache[task_id] = {
            'result': result,
            'expires_at': datetime.utcnow() + timedelta(seconds=self.ttl),
        }


result_backend = ResultBackendManager()
result_cache = ResultCache()
```

---

## Dead Letter Queues

```python
# File: /app/core/dead_letter_queue.py
"""Dead Letter Queue implementation for failed tasks."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pymongo import MongoClient, ASCENDING, DESCENDING

logger = logging.getLogger(__name__)


@dataclass
class FailedTask:
    """Represents a failed task."""
    task_id: str
    task_name: str
    args: tuple
    kwargs: dict
    error_type: str
    error_message: str
    traceback: str
    retry_count: int
    timestamp: datetime
    status: str = 'pending'
    resolution: str = None
    resolved_at: datetime = None
    resolved_by: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeadLetterQueue:
    """Dead Letter Queue for storing and managing failed tasks."""
    
    def __init__(self, mongo_uri: str = None, db_name: str = 'resilienceai'):
        self.mongo_uri = mongo_uri or 'mongodb://localhost:27017'
        self.db_name = db_name
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        self.collection = self.db['dead_letter_queue']
        self._create_indexes()
    
    def _create_indexes(self):
        self.collection.create_index([('task_id', ASCENDING)], unique=True)
        self.collection.create_index([('status', ASCENDING)])
        self.collection.create_index([('timestamp', DESCENDING)])
    
    def store_failed_task(self, task_id: str, task_name: str, args: tuple, kwargs: dict,
                          error_type: str, error_message: str, traceback: str,
                          retry_count: int, timestamp: datetime) -> str:
        """Store a failed task in the dead letter queue."""
        failed_task = FailedTask(
            task_id=task_id, task_name=task_name, args=args, kwargs=kwargs,
            error_type=error_type, error_message=error_message, traceback=traceback,
            retry_count=retry_count, timestamp=timestamp
        )
        result = self.collection.insert_one(failed_task.to_dict())
        logger.info(f"Stored failed task {task_id} in DLQ")
        return str(result.inserted_id)
    
    def retry_task(self, task_id: str, user: str = None) -> str:
        """Retry a failed task."""
        from app.core.celery_config import celery_app
        
        failed_task = self.collection.find_one({'task_id': task_id})
        if not failed_task:
            raise ValueError(f"Task {task_id} not found in DLQ")
        
        result = celery_app.send_task(
            failed_task['task_name'],
            args=failed_task['args'],
            kwargs=failed_task['kwargs'],
            queue=failed_task.get('queue', 'default')
        )
        
        self.collection.update_one(
            {'task_id': task_id},
            {'$set': {'status': 'pending', 'resolution': 'retry_initiated', 
                      'resolved_at': datetime.utcnow(), 'resolved_by': user}}
        )
        
        logger.info(f"Retried task {task_id}, new task ID: {result.id}")
        return result.id
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get DLQ statistics."""
        pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}]
        status_counts = list(self.collection.aggregate(pipeline))
        return {
            'status_counts': {item['_id']: item['count'] for item in status_counts},
            'total_tasks': self.collection.count_documents({}),
        }
```

---

## Implementation Guide

### Project Structure

```
resilienceai/
├── app/
│   ├── core/
│   │   ├── celery_config.py          # Main Celery configuration
│   │   ├── celery_settings.py        # Environment-specific settings
│   │   ├── retry_config.py           # Retry strategies
│   │   ├── priority_config.py        # Task priorities
│   │   ├── task_router.py            # Task routing
│   │   ├── result_backend.py         # Result backend utilities
│   │   ├── dead_letter_queue.py      # DLQ implementation
│   │   ├── monitoring.py             # Metrics collection
│   │   └── workflows.py              # Workflow patterns
│   ├── tasks/
│   │   ├── base.py                   # Base task classes
│   │   ├── ml_tasks.py               # ML-related tasks
│   │   ├── data_tasks.py             # Data processing tasks
│   │   ├── notification_tasks.py     # Notification tasks
│   │   ├── report_tasks.py           # Report generation tasks
│   │   └── periodic_tasks.py         # Scheduled tasks
│   └── services/
│       ├── scheduler_service.py      # Dynamic scheduling
│       └── workflow_service.py       # Workflow management
├── docker/
│   ├── Dockerfile.worker
│   ├── Dockerfile.beat
│   └── Dockerfile.flower
└── docker-compose.yml
```

### Installation & Setup

```bash
# requirements.txt
celery[redis]>=5.3.0
redis>=4.5.0
pymongo>=4.5.0
prometheus-client>=0.17.0
flower>=2.0.0
```

### Running Workers

```bash
# Start worker for default queue
celery -A app.core.celery_config worker -Q default -l info

# Start worker for multiple queues
celery -A app.core.celery_config worker -Q high_priority,default,low_priority -l info

# Start specialized ML worker
celery -A app.core.celery_config worker -Q ml_inference -c 2 -l info

# Start worker with autoscaling
celery -A app.core.celery_config worker -Q default --autoscale=10,2 -l info
```

### Running Scheduler

```bash
# Start Celery Beat
celery -A app.core.celery_config beat -l info
```

### Running Flower

```bash
# Start Flower
celery -A app.core.celery_config flower --port=5555
```

---

## Deployment Configuration

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  worker-default:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    command: celery -A app.core.celery_config worker -Q default,notifications -l info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
      - mongodb

  worker-ml:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    command: celery -A app.core.celery_config worker -Q ml_inference,high_priority -c 2 -l info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1

  beat:
    build:
      context: .
      dockerfile: docker/Dockerfile.beat
    command: celery -A app.core.celery_config beat -l info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0

  flower:
    build:
      context: .
      dockerfile: docker/Dockerfile.flower
    command: celery -A app.core.celery_config flower --port=5555
    ports:
      - "5555:5555"

volumes:
  redis_data:
  mongo_data:
```

---

## Implementation Priority Order

### Phase 1: Core Infrastructure (Week 1-2)
1. **Celery Configuration** - Basic setup with Redis broker
2. **Base Task Classes** - ResilienceAITask with error handling
3. **Task Definitions** - Core ML, data, notification tasks
4. **Retry Mechanisms** - Basic retry with exponential backoff

### Phase 2: Scheduling & Routing (Week 3)
1. **Periodic Tasks** - Celery Beat configuration
2. **Task Routing** - Queue-based routing
3. **Priority System** - Task priority implementation
4. **Dynamic Scheduling** - Scheduler service

### Phase 3: Monitoring & Reliability (Week 4)
1. **Monitoring Setup** - Prometheus metrics + Flower
2. **Health Checks** - System health monitoring
3. **Dead Letter Queue** - MongoDB-based DLQ
4. **Result Backend** - Extended result storage

### Phase 4: Advanced Features (Week 5-6)
1. **Workflow Patterns** - Chains, groups, chords
2. **Circuit Breaker** - Failure protection
3. **Advanced Retries** - Conditional retry strategies
4. **Performance Optimization** - Worker tuning

---

## Summary

This comprehensive background job system for ResilienceAI provides:

| Feature | Implementation | Status |
|---------|---------------|--------|
| Task Queue | Celery + Redis | Ready |
| Task Definitions | Modular task modules | Ready |
| Scheduling | Celery Beat + Dynamic | Ready |
| Retry Mechanisms | Multiple strategies | Ready |
| Monitoring | Prometheus + Flower | Ready |
| Priorities | 5-level priority system | Ready |
| Chains & Groups | Workflow patterns | Ready |
| Result Backends | Redis + Extended | Ready |
| Routing | Dynamic task routing | Ready |
| Dead Letter Queues | MongoDB-based | Ready |

The system is designed for scalability, reliability, and observability, with comprehensive error handling and monitoring capabilities.
