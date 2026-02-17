# ResilienceAI Logging & Observability Design

## Executive Summary

This document provides a comprehensive logging and observability architecture for ResilienceAI, a distributed AI-powered resilience management platform. The design emphasizes structured logging, distributed tracing, and centralized observability to enable effective debugging, performance monitoring, and security auditing across all services.

---

## 1. Logging Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ResilienceAI Logging Architecture                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐
│   API GW    │  │  Resilience │  │   Alert     │  │  Recovery   │  │  ML     │
│   Service   │  │   Engine    │  │   Service   │  │  Service    │  │ Service │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬────┘
       │                │                │                │              │
       │  JSON Logs     │  JSON Logs     │  JSON Logs     │  JSON Logs   │
       │  + Trace ID    │  + Trace ID    │  + Trace ID    │  + Trace ID  │
       ▼                ▼                ▼                ▼              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Log Aggregation Layer                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Fluentd   │───▶│   Kafka     │───▶│  Logstash   │───▶│Elasticsearch│  │
│  │   Agents    │    │   (Buffer)  │    │  (Parse)    │    │  (Store)    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                                                        │          │
│         └────────────────────────────────────────────────────────┘          │
│                              ▼                                               │
│                        ┌─────────────┐                                       │
│                        │    Kibana   │  (Visualization & Analysis)           │
│                        └─────────────┘                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Distributed Tracing Layer                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Jaeger    │◀───│   OpenTel   │◀───│   Service   │◀───│   Service   │  │
│  │   (UI/API)  │    │   SDK       │    │   A         │    │   B         │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Metrics & Alerting Layer                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  Prometheus │◀───│  Exporters  │◀───│   Grafana   │◀───│   Alert     │  │
│  │  (Metrics)  │    │  (/metrics) │    │ (Dashboards)│    │  Manager    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Core Principles

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Structured Logging** | All logs in JSON format for machine parsing | Python `structlog` library |
| **Correlation IDs** | Unique IDs tracking requests across services | Middleware injection |
| **Context Propagation** | Context flows through async operations | `contextvars` + middleware |
| **Log Levels** | Appropriate granularity for different environments | DEBUG → INFO → WARNING → ERROR → CRITICAL |
| **Sensitive Data** | Automatic redaction of PII/secrets | Custom processors |
| **Performance** | Async logging to avoid blocking | `aiologger` + batching |

---

## 2. Structured Logging Implementation

### 2.1 Core Logger Configuration

**File:** `/app/logging/logger_config.py`

```python
"""
ResilienceAI Structured Logging Configuration
Provides centralized logging setup with structured JSON output.
"""

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

import structlog
from structlog.processors import JSONRenderer
from structlog.stdlib import BoundLogger, filter_by_level

# Context variables for correlation tracking
REQUEST_ID: ContextVar[str] = ContextVar('request_id', default='')
TRACE_ID: ContextVar[str] = ContextVar('trace_id', default='')
SPAN_ID: ContextVar[str] = ContextVar('span_id', default='')
USER_ID: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
ORGANIZATION_ID: ContextVar[Optional[str]] = ContextVar('organization_id', default=None)
SERVICE_NAME: ContextVar[str] = ContextVar('service_name', default='unknown')
ENVIRONMENT: ContextVar[str] = ContextVar('environment', default='development')


class SensitiveDataFilter:
    """Filter sensitive data from logs."""
    
    SENSITIVE_KEYS = {
        'password', 'token', 'secret', 'api_key', 'apikey',
        'authorization', 'auth_token', 'access_token', 'refresh_token',
        'credit_card', 'ssn', 'social_security', 'private_key',
        'credential', 'passwd', 'pwd', 'secret_key'
    }
    
    MASK = '***REDACTED***'
    
    @classmethod
    def filter_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively filter sensitive keys from dictionary."""
        if not isinstance(data, dict):
            return data
        
        filtered = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in cls.SENSITIVE_KEYS):
                filtered[key] = cls.MASK
            elif isinstance(value, dict):
                filtered[key] = cls.filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [
                    cls.filter_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value
        return filtered


class ContextualProcessor:
    """Add context variables to log entries."""
    
    def __call__(self, logger, method_name, event_dict):
        """Add context to event dict."""
        event_dict['timestamp'] = datetime.now(timezone.utc).isoformat()
        event_dict['service'] = SERVICE_NAME.get()
        event_dict['environment'] = ENVIRONMENT.get()
        event_dict['request_id'] = REQUEST_ID.get() or str(uuid.uuid4())[:8]
        event_dict['trace_id'] = TRACE_ID.get() or ''
        event_dict['span_id'] = SPAN_ID.get() or ''
        
        user_id = USER_ID.get()
        if user_id:
            event_dict['user_id'] = user_id
        
        org_id = ORGANIZATION_ID.get()
        if org_id:
            event_dict['organization_id'] = org_id
        
        # Filter sensitive data
        if 'event' in event_dict and isinstance(event_dict['event'], dict):
            event_dict['event'] = SensitiveDataFilter.filter_dict(event_dict['event'])
        
        return event_dict


def configure_logging(
    service_name: str,
    environment: str = 'development',
    log_level: str = 'INFO',
    json_output: bool = True
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        service_name: Name of the service
        environment: Deployment environment
        log_level: Minimum log level
        json_output: Whether to output JSON format
    """
    # Set context variables
    SERVICE_NAME.set(service_name)
    ENVIRONMENT.set(environment)
    
    # Configure standard library logging
    logging.basicConfig(
        format='%(message)s',
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Shared processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt='iso'),
        ContextualProcessor(),
    ]
    
    # Environment-specific processors
    if environment == 'development':
        # Pretty print in development
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # JSON in production
        renderer = JSONRenderer(serializer=json.dumps)
    
    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


# Convenience function for correlation context
def set_correlation_context(
    request_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None
) -> Dict[str, Any]:
    """Set correlation context for current execution."""
    tokens = {}
    
    if request_id:
        tokens['request_id'] = REQUEST_ID.set(request_id)
    if trace_id:
        tokens['trace_id'] = TRACE_ID.set(trace_id)
    if span_id:
        tokens['span_id'] = SPAN_ID.set(span_id)
    if user_id:
        tokens['user_id'] = USER_ID.set(user_id)
    if organization_id:
        tokens['organization_id'] = ORGANIZATION_ID.set(organization_id)
    
    return tokens


def reset_correlation_context(tokens: Dict[str, Any]) -> None:
    """Reset correlation context using tokens."""
    for key, token in tokens.items():
        var = globals()[key.upper()]
        var.reset(token)
```

### 2.2 Async Logger Implementation

**File:** `/app/logging/async_logger.py`

```python
"""
Asynchronous logging for non-blocking log operations.
"""

import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import aiohttp

from .logger_config import get_logger, REQUEST_ID, TRACE_ID

logger = get_logger(__name__)


@dataclass
class LogEntry:
    """Represents a single log entry."""
    timestamp: datetime
    level: str
    message: str
    service: str
    request_id: str
    trace_id: str
    extra: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
            'service': self.service,
            'request_id': self.request_id,
            'trace_id': self.trace_id,
            **self.extra
        }


class AsyncLogBuffer:
    """Buffer for batching async log operations."""
    
    def __init__(
        self,
        max_size: int = 100,
        flush_interval: float = 5.0,
        endpoint: Optional[str] = None
    ):
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.endpoint = endpoint
        self.buffer: List[LogEntry] = []
        self._lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        """Start the background flush task."""
        self._session = aiohttp.ClientSession()
        self._flush_task = asyncio.create_task(self._periodic_flush())
    
    async def stop(self):
        """Stop the buffer and flush remaining logs."""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        await self.flush()
        
        if self._session:
            await self._session.close()
    
    async def add(self, entry: LogEntry):
        """Add a log entry to the buffer."""
        async with self._lock:
            self.buffer.append(entry)
            
            if len(self.buffer) >= self.max_size:
                await self._flush_unlocked()
    
    async def _periodic_flush(self):
        """Periodically flush the buffer."""
        while True:
            await asyncio.sleep(self.flush_interval)
            await self.flush()
    
    async def flush(self):
        """Flush all buffered logs."""
        async with self._lock:
            await self._flush_unlocked()
    
    async def _flush_unlocked(self):
        """Internal flush without locking."""
        if not self.buffer:
            return
        
        logs_to_send = self.buffer.copy()
        self.buffer.clear()
        
        if self.endpoint and self._session:
            try:
                await self._send_logs(logs_to_send)
            except Exception as e:
                logger.error(
                    'Failed to send logs to endpoint',
                    endpoint=self.endpoint,
                    error=str(e),
                    log_count=len(logs_to_send)
                )
    
    async def _send_logs(self, logs: List[LogEntry]):
        """Send logs to external endpoint."""
        payload = [log.to_dict() for log in logs]
        
        async with self._session.post(
            self.endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'}
        ) as response:
            if response.status >= 400:
                raise Exception(f'HTTP {response.status}: {await response.text()}')


class AsyncLogger:
    """Asynchronous logger with buffering capabilities."""
    
    def __init__(self, service_name: str, buffer: Optional[AsyncLogBuffer] = None):
        self.service_name = service_name
        self.buffer = buffer
        self._logger = get_logger(__name__)
    
    async def log(
        self,
        level: str,
        message: str,
        **extra: Any
    ):
        """Log a message asynchronously."""
        entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level.upper(),
            message=message,
            service=self.service_name,
            request_id=REQUEST_ID.get(),
            trace_id=TRACE_ID.get(),
            extra=extra
        )
        
        if self.buffer:
            await self.buffer.add(entry)
        
        # Also log to standard logger
        log_method = getattr(self._logger, level.lower())
        log_method(message, **extra)
    
    async def debug(self, message: str, **extra: Any):
        await self.log('DEBUG', message, **extra)
    
    async def info(self, message: str, **extra: Any):
        await self.log('INFO', message, **extra)
    
    async def warning(self, message: str, **extra: Any):
        await self.log('WARNING', message, **extra)
    
    async def error(self, message: str, **extra: Any):
        await self.log('ERROR', message, **extra)
    
    async def critical(self, message: str, **extra: Any):
        await self.log('CRITICAL', message, **extra)
```

---

## 3. Log Levels and Categories

### 3.1 Log Level Definitions

**File:** `/app/logging/log_levels.py`

```python
"""
Log level definitions and categorization for ResilienceAI.
"""

from enum import Enum
from typing import Dict, List, Optional


class LogLevel(Enum):
    """Standard log levels with descriptions."""
    DEBUG = ('DEBUG', 10, 'Detailed debugging information')
    INFO = ('INFO', 20, 'General informational messages')
    WARNING = ('WARNING', 30, 'Potential issues, non-critical')
    ERROR = ('ERROR', 40, 'Errors that affect functionality')
    CRITICAL = ('CRITICAL', 50, 'Severe errors requiring immediate attention')
    AUDIT = ('AUDIT', 25, 'Security and compliance audit events')
    PERFORMANCE = ('PERF', 15, 'Performance metrics and timing')
    
    def __init__(self, name: str, level: int, description: str):
        self.level_name = name
        self.level = level
        self.description = description


class LogCategory(Enum):
    """Log categories for different types of events."""
    
    # Application Lifecycle
    STARTUP = 'startup'
    SHUTDOWN = 'shutdown'
    CONFIG = 'config'
    
    # Request/Response
    HTTP_REQUEST = 'http_request'
    HTTP_RESPONSE = 'http_response'
    WEBSOCKET = 'websocket'
    
    # Business Logic
    RESILIENCE_ANALYSIS = 'resilience_analysis'
    RISK_ASSESSMENT = 'risk_assessment'
    RECOVERY_ACTION = 'recovery_action'
    ALERT = 'alert'
    NOTIFICATION = 'notification'
    
    # Data Operations
    DATABASE = 'database'
    CACHE = 'cache'
    MESSAGE_QUEUE = 'message_queue'
    
    # ML/AI Operations
    ML_INFERENCE = 'ml_inference'
    ML_TRAINING = 'ml_training'
    FEATURE_EXTRACTION = 'feature_extraction'
    
    # Infrastructure
    KUBERNETES = 'kubernetes'
    DOCKER = 'docker'
    NETWORK = 'network'
    
    # Security
    AUTHENTICATION = 'authentication'
    AUTHORIZATION = 'authorization'
    AUDIT = 'audit'
    SECURITY_EVENT = 'security_event'
    
    # Performance
    PERFORMANCE = 'performance'
    TIMING = 'timing'
    RESOURCE_USAGE = 'resource_usage'
    
    # Errors
    EXCEPTION = 'exception'
    TIMEOUT = 'timeout'
    CIRCUIT_BREAKER = 'circuit_breaker'
    RETRY = 'retry'


class LogLevelConfig:
    """Configuration for log levels by environment and category."""
    
    DEFAULT_CONFIG: Dict[str, Dict[str, str]] = {
        'development': {
            'default': 'DEBUG',
            LogCategory.HTTP_REQUEST.value: 'DEBUG',
            LogCategory.DATABASE.value: 'DEBUG',
            LogCategory.ML_INFERENCE.value: 'INFO',
            LogCategory.PERFORMANCE.value: 'DEBUG',
            LogCategory.AUDIT.value: 'INFO',
        },
        'staging': {
            'default': 'INFO',
            LogCategory.HTTP_REQUEST.value: 'INFO',
            LogCategory.DATABASE.value: 'WARNING',
            LogCategory.ML_INFERENCE.value: 'INFO',
            LogCategory.PERFORMANCE.value: 'INFO',
            LogCategory.AUDIT.value: 'INFO',
        },
        'production': {
            'default': 'WARNING',
            LogCategory.HTTP_REQUEST.value: 'WARNING',
            LogCategory.DATABASE.value: 'ERROR',
            LogCategory.ML_INFERENCE.value: 'INFO',
            LogCategory.PERFORMANCE.value: 'INFO',
            LogCategory.AUDIT.value: 'INFO',
            LogCategory.EXCEPTION.value: 'ERROR',
            LogCategory.SECURITY_EVENT.value: 'WARNING',
        }
    }
    
    @classmethod
    def get_level(
        cls,
        environment: str,
        category: Optional[LogCategory] = None
    ) -> str:
        """Get log level for environment and category."""
        config = cls.DEFAULT_CONFIG.get(environment, cls.DEFAULT_CONFIG['production'])
        
        if category:
            return config.get(category.value, config.get('default', 'INFO'))
        
        return config.get('default', 'INFO')
    
    @classmethod
    def should_log(
        cls,
        level: LogLevel,
        environment: str,
        category: Optional[LogCategory] = None
    ) -> bool:
        """Check if a log level should be logged for given environment/category."""
        config_level_name = cls.get_level(environment, category)
        config_level = getattr(LogLevel, config_level_name)
        
        return level.level >= config_level.level
```

### 3.2 Category-Based Logger

**File:** `/app/logging/category_logger.py`

```python
"""
Category-based logging with automatic level configuration.
"""

from typing import Any, Dict, Optional
from contextlib import contextmanager
import time

from .logger_config import get_logger, ENVIRONMENT
from .log_levels import LogCategory, LogLevel, LogLevelConfig


class CategoryLogger:
    """Logger that automatically applies category-based log levels."""
    
    def __init__(self, category: LogCategory, service_name: Optional[str] = None):
        self.category = category
        self.service_name = service_name
        self._logger = get_logger(f"{service_name}.{category.value}" if service_name else category.value)
        self._environment = ENVIRONMENT.get()
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if this log should be emitted."""
        return LogLevelConfig.should_log(level, self._environment, self.category)
    
    def _log(self, level: LogLevel, message: str, **kwargs: Any):
        """Internal log method with category injection."""
        if not self._should_log(level):
            return
        
        extra = {
            'category': self.category.value,
            **kwargs
        }
        
        log_method = getattr(self._logger, level.level_name.lower())
        log_method(message, **extra)
    
    def debug(self, message: str, **kwargs: Any):
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs: Any):
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any):
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs: Any):
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs: Any):
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    def audit(self, message: str, **kwargs: Any):
        """Log audit events (security/compliance)."""
        self._log(LogLevel.AUDIT, message, **kwargs)
    
    def performance(self, message: str, **kwargs: Any):
        """Log performance metrics."""
        self._log(LogLevel.PERFORMANCE, message, **kwargs)
    
    @contextmanager
    def timed_operation(self, operation: str, **extra: Any):
        """Context manager for timing operations."""
        start_time = time.perf_counter()
        try:
            yield self
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.performance(
                f"Operation {operation} completed",
                operation=operation,
                duration_ms=round(duration_ms, 2),
                **extra
            )


# Convenience functions for common categories
def get_resilience_logger(service_name: Optional[str] = None) -> CategoryLogger:
    """Get logger for resilience analysis events."""
    return CategoryLogger(LogCategory.RESILIENCE_ANALYSIS, service_name)


def get_ml_logger(service_name: Optional[str] = None) -> CategoryLogger:
    """Get logger for ML/AI events."""
    return CategoryLogger(LogCategory.ML_INFERENCE, service_name)


def get_security_logger(service_name: Optional[str] = None) -> CategoryLogger:
    """Get logger for security events."""
    return CategoryLogger(LogCategory.SECURITY_EVENT, service_name)


def get_performance_logger(service_name: Optional[str] = None) -> CategoryLogger:
    """Get logger for performance events."""
    return CategoryLogger(LogCategory.PERFORMANCE, service_name)


def get_audit_logger(service_name: Optional[str] = None) -> CategoryLogger:
    """Get logger for audit events."""
    return CategoryLogger(LogCategory.AUDIT, service_name)
```


---

## 4. Correlation IDs and Context Propagation

### 4.1 Correlation ID Middleware

**File:** `/app/logging/correlation_middleware.py`

```python
"""
FastAPI middleware for correlation ID management.
"""

import uuid
from typing import Optional, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logger_config import (
    REQUEST_ID, TRACE_ID, SPAN_ID, USER_ID, ORGANIZATION_ID,
    set_correlation_context
)
from .logger_config import get_logger

logger = get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to manage correlation IDs across HTTP requests.
    
    Extracts or generates:
    - X-Request-ID: Unique per-request ID
    - X-Trace-ID: Spans multiple requests (distributed tracing)
    - X-Span-ID: Current span within a trace
    """
    
    def __init__(
        self,
        app: ASGIApp,
        header_request_id: str = 'X-Request-ID',
        header_trace_id: str = 'X-Trace-ID',
        header_span_id: str = 'X-Span-ID',
        header_user_id: str = 'X-User-ID',
        header_org_id: str = 'X-Organization-ID'
    ):
        super().__init__(app)
        self.header_request_id = header_request_id
        self.header_trace_id = header_trace_id
        self.header_span_id = header_span_id
        self.header_user_id = header_user_id
        self.header_org_id = header_org_id
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with correlation IDs."""
        # Extract or generate IDs
        request_id = self._get_or_generate_id(
            request.headers.get(self.header_request_id)
        )
        trace_id = self._get_or_generate_id(
            request.headers.get(self.header_trace_id)
        )
        span_id = self._generate_span_id()
        
        user_id = request.headers.get(self.header_user_id)
        org_id = request.headers.get(self.header_org_id)
        
        # Set context
        tokens = set_correlation_context(
            request_id=request_id,
            trace_id=trace_id,
            span_id=span_id,
            user_id=user_id,
            organization_id=org_id
        )
        
        try:
            # Log incoming request
            logger.info(
                'HTTP request started',
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params),
                client_host=request.client.host if request.client else None,
                user_agent=request.headers.get('user-agent'),
            )
            
            # Process request
            response = await call_next(request)
            
            # Add correlation headers to response
            response.headers[self.header_request_id] = request_id
            response.headers[self.header_trace_id] = trace_id
            response.headers[self.header_span_id] = span_id
            
            # Log response
            logger.info(
                'HTTP request completed',
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=getattr(request.state, 'duration_ms', None)
            )
            
            return response
            
        except Exception as e:
            logger.error(
                'HTTP request failed',
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
            
        finally:
            # Reset context
            from .logger_config import reset_correlation_context
            reset_correlation_context(tokens)
    
    def _get_or_generate_id(self, existing_id: Optional[str]) -> str:
        """Use existing ID or generate new one."""
        if existing_id:
            return existing_id
        return self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())
    
    def _generate_span_id(self) -> str:
        """Generate a span ID (shorter for readability)."""
        return str(uuid.uuid4())[:16]


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request timing."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import time
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        request.state.duration_ms = round(duration_ms, 2)
        
        # Add timing header
        response.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"
        
        return response


# gRPC Interceptor for correlation IDs
class CorrelationIdInterceptor:
    """gRPC interceptor for correlation ID propagation."""
    
    def intercept_service(self, continuation, handler_call_details):
        """Intercept gRPC service calls."""
        from .logger_config import set_correlation_context
        
        # Extract metadata
        metadata = dict(handler_call_details.invocation_metadata or [])
        
        request_id = metadata.get('x-request-id') or str(uuid.uuid4())
        trace_id = metadata.get('x-trace-id') or str(uuid.uuid4())
        span_id = str(uuid.uuid4())[:16]
        
        tokens = set_correlation_context(
            request_id=request_id,
            trace_id=trace_id,
            span_id=span_id
        )
        
        try:
            return continuation(handler_call_details)
        finally:
            from .logger_config import reset_correlation_context
            reset_correlation_context(tokens)


# Celery task correlation
class CeleryCorrelationMixin:
    """Mixin for Celery tasks to propagate correlation IDs."""
    
    def apply_async(self, args=None, kwargs=None, **options):
        """Override to include correlation IDs in task headers."""
        from .logger_config import REQUEST_ID, TRACE_ID, SPAN_ID, USER_ID
        
        headers = options.get('headers', {})
        headers.update({
            'X-Request-ID': REQUEST_ID.get(),
            'X-Trace-ID': TRACE_ID.get(),
            'X-Parent-Span-ID': SPAN_ID.get(),
            'X-User-ID': USER_ID.get(),
        })
        options['headers'] = headers
        
        return super().apply_async(args, kwargs, **options)
    
    def __call__(self, *args, **kwargs):
        """Restore correlation context when task runs."""
        from .logger_config import set_correlation_context, reset_correlation_context
        
        request = self.request
        headers = request.headers if hasattr(request, 'headers') else {}
        
        tokens = set_correlation_context(
            request_id=headers.get('X-Request-ID'),
            trace_id=headers.get('X-Trace-ID'),
            span_id=str(uuid.uuid4())[:16],
            user_id=headers.get('X-User-ID')
        )
        
        try:
            return self.run(*args, **kwargs)
        finally:
            reset_correlation_context(tokens)
```

### 4.2 Context Propagation for Async Operations

**File:** `/app/logging/context_propagation.py`

```python
"""
Context propagation for async operations and background tasks.
"""

import asyncio
import functools
from contextvars import copy_context
from typing import Any, Callable, Coroutine, TypeVar

from .logger_config import (
    REQUEST_ID, TRACE_ID, SPAN_ID, USER_ID, ORGANIZATION_ID,
    SERVICE_NAME, ENVIRONMENT
)

T = TypeVar('T')


class ContextSnapshot:
    """Snapshot of context variables for later restoration."""
    
    def __init__(self):
        self.request_id = REQUEST_ID.get()
        self.trace_id = TRACE_ID.get()
        self.span_id = SPAN_ID.get()
        self.user_id = USER_ID.get()
        self.organization_id = ORGANIZATION_ID.get()
        self.service_name = SERVICE_NAME.get()
        self.environment = ENVIRONMENT.get()
    
    def restore(self):
        """Restore context variables from snapshot."""
        tokens = {}
        
        if self.request_id:
            tokens['request_id'] = REQUEST_ID.set(self.request_id)
        if self.trace_id:
            tokens['trace_id'] = TRACE_ID.set(self.trace_id)
        if self.span_id:
            tokens['span_id'] = SPAN_ID.set(self.span_id)
        if self.user_id:
            tokens['user_id'] = USER_ID.set(self.user_id)
        if self.organization_id:
            tokens['organization_id'] = ORGANIZATION_ID.set(self.organization_id)
        if self.service_name:
            tokens['service_name'] = SERVICE_NAME.set(self.service_name)
        if self.environment:
            tokens['environment'] = ENVIRONMENT.set(self.environment)
        
        return tokens


def preserve_context(coro: Coroutine[Any, Any, T]) -> Coroutine[Any, Any, T]:
    """
    Decorator to preserve context across async boundaries.
    
    Usage:
        @preserve_context
        async def my_async_function():
            logger.info("This will have the correct context")
    """
    snapshot = ContextSnapshot()
    
    async def wrapper(*args, **kwargs) -> T:
        tokens = snapshot.restore()
        try:
            return await coro(*args, **kwargs)
        finally:
            from .logger_config import reset_correlation_context
            reset_correlation_context(tokens)
    
    return wrapper


def run_in_context(coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
    """
    Run a coroutine with preserved context.
    
    Usage:
        task = run_in_context(background_task())
    """
    snapshot = ContextSnapshot()
    
    async def wrapped():
        tokens = snapshot.restore()
        try:
            return await coro
        finally:
            from .logger_config import reset_correlation_context
            reset_correlation_context(tokens)
    
    return asyncio.create_task(wrapped())


class ContextPropagatingTask(asyncio.Task):
    """Custom Task class that preserves context."""
    
    def __init__(self, coro, *, loop=None, **kwargs):
        self._context_snapshot = ContextSnapshot()
        
        async def wrapped_coro():
            tokens = self._context_snapshot.restore()
            try:
                return await coro
            finally:
                from .logger_config import reset_correlation_context
                reset_correlation_context(tokens)
        
        super().__init__(wrapped_coro(), loop=loop, **kwargs)


def create_task(coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
    """Create a task with context preservation."""
    return run_in_context(coro)


# Thread pool executor with context propagation
from concurrent.futures import ThreadPoolExecutor


class ContextPropagatingExecutor(ThreadPoolExecutor):
    """ThreadPoolExecutor that propagates context to worker threads."""
    
    def submit(self, fn: Callable[..., T], *args, **kwargs):
        """Submit function with context preservation."""
        snapshot = ContextSnapshot()
        
        @functools.wraps(fn)
        def wrapped(*args, **kwargs) -> T:
            tokens = snapshot.restore()
            try:
                return fn(*args, **kwargs)
            finally:
                from .logger_config import reset_correlation_context
                reset_correlation_context(tokens)
        
        return super().submit(wrapped, *args, **kwargs)


# Decorator for functions that need context
def with_context(fn: Callable[..., T]) -> Callable[..., T]:
    """Decorator to preserve context in function calls."""
    snapshot = ContextSnapshot()
    
    @functools.wraps(fn)
    def wrapper(*args, **kwargs) -> T:
        tokens = snapshot.restore()
        try:
            return fn(*args, **kwargs)
        finally:
            from .logger_config import reset_correlation_context
            reset_correlation_context(tokens)
    
    return wrapper


# Context manager for temporary context changes
from contextlib import contextmanager


@contextmanager
def temporary_context(**kwargs):
    """
    Temporarily modify context variables.
    
    Usage:
        with temporary_context(user_id='admin'):
            logger.info("Running as admin")
    """
    tokens = {}
    
    for key, value in kwargs.items():
        var = globals().get(key.upper())
        if var:
            tokens[key] = var.set(value)
    
    try:
        yield
    finally:
        from .logger_config import reset_correlation_context
        reset_correlation_context(tokens)
```

---

## 5. Distributed Tracing

### 5.1 OpenTelemetry Integration

**File:** `/app/logging/tracing.py`

```python
"""
OpenTelemetry distributed tracing configuration.
"""

from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager
import functools

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.trace import Status, StatusCode

from .logger_config import get_logger, REQUEST_ID, TRACE_ID, SPAN_ID

logger = get_logger(__name__)


class TracingConfig:
    """Configuration for distributed tracing."""
    
    def __init__(
        self,
        service_name: str,
        service_version: str = '1.0.0',
        environment: str = 'development',
        jaeger_host: str = 'jaeger-agent',
        jaeger_port: int = 6831,
        otlp_endpoint: Optional[str] = None,
        sample_rate: float = 1.0,
        console_export: bool = False
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.jaeger_host = jaeger_host
        self.jaeger_port = jaeger_port
        self.otlp_endpoint = otlp_endpoint
        self.sample_rate = sample_rate
        self.console_export = console_export


def configure_tracing(config: TracingConfig) -> TracerProvider:
    """
    Configure OpenTelemetry tracing.
    
    Args:
        config: Tracing configuration
        
    Returns:
        Configured TracerProvider
    """
    # Create resource
    resource = Resource.create({
        SERVICE_NAME: config.service_name,
        SERVICE_VERSION: config.service_version,
        DEPLOYMENT_ENVIRONMENT: config.environment,
    })
    
    # Create provider
    provider = TracerProvider(
        resource=resource,
        sampler=trace.sampling.TraceIdRatioBased(config.sample_rate)
    )
    
    # Set global provider
    trace.set_tracer_provider(provider)
    
    # Add Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=config.jaeger_host,
        agent_port=config.jaeger_port,
    )
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    
    # Add OTLP exporter if configured
    if config.otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=config.otlp_endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Console exporter for debugging
    if config.console_export:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    logger.info(
        'Tracing configured',
        service_name=config.service_name,
        jaeger_host=config.jaeger_host,
        sample_rate=config.sample_rate
    )
    
    return provider


def instrument_fastapi(app):
    """Instrument FastAPI application for tracing."""
    FastAPIInstrumentor.instrument_app(app)
    logger.info('FastAPI instrumented for tracing')


def instrument_redis():
    """Instrument Redis for tracing."""
    RedisInstrumentor().instrument()
    logger.info('Redis instrumented for tracing')


def instrument_sqlalchemy(engine):
    """Instrument SQLAlchemy for tracing."""
    SQLAlchemyInstrumentor().instrument(
        engine=engine,
        enable_commenter=True,
        commenter_options={}
    )
    logger.info('SQLAlchemy instrumented for tracing')


def instrument_celery():
    """Instrument Celery for tracing."""
    CeleryInstrumentor().instrument()
    logger.info('Celery instrumented for tracing')


def instrument_aiohttp():
    """Instrument aiohttp client for tracing."""
    AioHttpClientInstrumentor().instrument()
    logger.info('aiohttp client instrumented for tracing')


class TracedSpan:
    """Wrapper for OpenTelemetry spans with additional functionality."""
    
    def __init__(self, span: trace.Span):
        self.span = span
    
    def set_attribute(self, key: str, value: Any):
        """Set a span attribute."""
        self.span.set_attribute(key, value)
    
    def set_attributes(self, attributes: Dict[str, Any]):
        """Set multiple span attributes."""
        for key, value in attributes.items():
            self.span.set_attribute(key, value)
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to the span."""
        self.span.add_event(name, attributes)
    
    def set_error(self, exception: Exception):
        """Mark span as error with exception details."""
        self.span.set_status(Status(StatusCode.ERROR, str(exception)))
        self.span.record_exception(exception)
    
    def update_correlation_ids(self):
        """Update correlation IDs in context."""
        trace_id = format(self.span.get_span_context().trace_id, '032x')
        span_id = format(self.span.get_span_context().span_id, '016x')
        
        TRACE_ID.set(trace_id)
        SPAN_ID.set(span_id)
        
        self.span.set_attribute('request_id', REQUEST_ID.get())


@contextmanager
def start_span(
    name: str,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Context manager for starting a new span.
    
    Usage:
        with start_span('process_data', attributes={'data_id': '123'}) as span:
            process_data()
    """
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span(name, kind=kind) as otel_span:
        span = TracedSpan(otel_span)
        
        if attributes:
            span.set_attributes(attributes)
        
        span.update_correlation_ids()
        
        try:
            yield span
        except Exception as e:
            span.set_error(e)
            raise


def traced(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Decorator to trace function execution.
    
    Usage:
        @traced(attributes={'operation': 'analyze'})
        async def analyze_data(data_id: str):
            # Function body
    """
    def decorator(func: Callable) -> Callable:
        span_name = name or func.__name__
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with start_span(span_name, attributes=attributes) as span:
                # Add function arguments as attributes
                span.set_attribute('function.args_count', len(args))
                span.set_attribute('function.kwargs_keys', list(kwargs.keys()))
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with start_span(span_name, attributes=attributes) as span:
                span.set_attribute('function.args_count', len(args))
                span.set_attribute('function.kwargs_keys', list(kwargs.keys()))
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Import asyncio for decorator check
import asyncio


class TraceContext:
    """Helper class for managing trace context."""
    
    @staticmethod
    def get_current_trace_id() -> Optional[str]:
        """Get current trace ID."""
        span = trace.get_current_span()
        if span:
            return format(span.get_span_context().trace_id, '032x')
        return None
    
    @staticmethod
    def get_current_span_id() -> Optional[str]:
        """Get current span ID."""
        span = trace.get_current_span()
        if span:
            return format(span.get_span_context().span_id, '016x')
        return None
    
    @staticmethod
    def inject_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """Inject trace context into headers for outbound requests."""
        from opentelemetry.propagate import inject
        
        carrier = {}
        inject(carrier)
        headers.update(carrier)
        
        return headers
    
    @staticmethod
    def extract_headers(headers: Dict[str, str]):
        """Extract trace context from headers."""
        from opentelemetry.propagate import extract
        
        return extract(headers)


# FastAPI dependency for trace context
from fastapi import Request


async def get_trace_context(request: Request) -> Dict[str, Any]:
    """FastAPI dependency to get trace context."""
    span = trace.get_current_span()
    
    if span:
        context = span.get_span_context()
        return {
            'trace_id': format(context.trace_id, '032x'),
            'span_id': format(context.span_id, '016x'),
            'is_remote': context.is_remote,
            'trace_flags': str(context.trace_flags),
        }
    
    return {}
```

### 5.2 Custom Span Processors

**File:** `/app/logging/span_processors.py`

```python
"""
Custom span processors for specialized tracing needs.
"""

from typing import Optional
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan
from opentelemetry.trace import StatusCode

from .logger_config import get_logger

logger = get_logger(__name__)


class ErrorLoggingSpanProcessor(SpanProcessor):
    """Span processor that logs errors to the application logger."""
    
    def on_start(self, span, parent_context=None):
        """Called when a span starts."""
        pass
    
    def on_end(self, span: ReadableSpan):
        """Called when a span ends - log if error."""
        if span.status.status_code == StatusCode.ERROR:
            logger.error(
                'Span completed with error',
                span_name=span.name,
                trace_id=format(span.context.trace_id, '032x'),
                span_id=format(span.context.span_id, '016x'),
                error_description=span.status.description,
                duration_ns=span.end_time - span.start_time if span.end_time else None
            )
    
    def shutdown(self):
        """Shutdown the processor."""
        pass
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush spans."""
        return True


class PerformanceSpanProcessor(SpanProcessor):
    """Span processor that logs slow spans."""
    
    def __init__(self, slow_threshold_ms: float = 1000.0):
        self.slow_threshold_ms = slow_threshold_ms
    
    def on_start(self, span, parent_context=None):
        pass
    
    def on_end(self, span: ReadableSpan):
        """Log slow spans."""
        if span.end_time and span.start_time:
            duration_ms = (span.end_time - span.start_time) / 1_000_000
            
            if duration_ms > self.slow_threshold_ms:
                logger.warning(
                    'Slow span detected',
                    span_name=span.name,
                    duration_ms=round(duration_ms, 2),
                    threshold_ms=self.slow_threshold_ms,
                    trace_id=format(span.context.trace_id, '032x')
                )
    
    def shutdown(self):
        pass
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


class AttributeEnrichingSpanProcessor(SpanProcessor):
    """Span processor that enriches spans with additional attributes."""
    
    def __init__(self, default_attributes: Optional[dict] = None):
        self.default_attributes = default_attributes or {}
    
    def on_start(self, span, parent_context=None):
        """Add default attributes to new spans."""
        for key, value in self.default_attributes.items():
            span.set_attribute(key, value)
        
        # Add service info
        from .logger_config import SERVICE_NAME, ENVIRONMENT
        span.set_attribute('service.name', SERVICE_NAME.get())
        span.set_attribute('deployment.environment', ENVIRONMENT.get())
    
    def on_end(self, span: ReadableSpan):
        pass
    
    def shutdown(self):
        pass
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


---

## 6. Log Aggregation (ELK Stack + Fluentd)

### 6.1 Fluentd Configuration

**File:** `/app/logging/fluentd/fluent.conf`

```
# Fluentd Configuration for ResilienceAI
# Collects logs from all services and forwards to Kafka/Elasticsearch

# System settings
<system>
  log_level info
  workers 4
</system>

# Source: Application logs via HTTP
<source>
  @type http
  @id input_http
  port 9880
  bind 0.0.0.0
  body_size_limit 32m
  keepalive_timeout 10s
  <parse>
    @type json
  </parse>
</source>

# Source: Application logs via TCP (for high throughput)
<source>
  @type forward
  @id input_forward
  port 24224
  bind 0.0.0.0
</source>

# Source: Container logs (Docker)
<source>
  @type tail
  @id container_logs
  path /var/lib/docker/containers/*/*.log
  pos_file /var/log/fluentd-docker.pos
  tag docker.*
  <parse>
    @type json
    time_format %Y-%m-%dT%H:%M:%S.%NZ
  </parse>
</source>

# Source: Kubernetes logs
<source>
  @type tail
  @id kubernetes_logs
  path /var/log/containers/*.log
  pos_file /var/log/fluentd-k8s.pos
  tag kubernetes.*
  <parse>
    @type multi_format
    <pattern>
      format json
      time_key timestamp
      time_format %Y-%m-%dT%H:%M:%S.%NZ
      keep_time_key true
    </pattern>
    <pattern>
      format regexp
      expression /^(?<time>.+) (?<stream>stdout|stderr) [^ ]* (?<log>.*)$/
      time_format %Y-%m-%dT%H:%M:%S.%N%:z
    </pattern>
  </parse>
</source>

# Source: System logs
<source>
  @type tail
  @id system_logs
  path /var/log/syslog
  pos_file /var/log/fluentd-syslog.pos
  tag system.syslog
  <parse>
    @type syslog
  </parse>
</source>

# Filter: Add metadata to all logs
<filter **>
  @type record_transformer
  @id add_metadata
  <record>
    fluentd_host ${hostname}
    fluentd_timestamp ${time}
    collector_version 1.0.0
  </record>
</filter>

# Filter: Parse ResilienceAI service logs
<filter kubernetes.**>
  @type parser
  @id parse_resilienceai
  format json
  key_name log
  reserve_data true
  <parse>
    @type json
  </parse>
</filter>

# Filter: Enrich with Kubernetes metadata
<filter kubernetes.**>
  @type kubernetes_metadata
  @id k8s_metadata
  kubernetes_url https://kubernetes.default.svc
  verify_ssl true
  ca_file /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
  bearer_token_file /var/run/secrets/kubernetes.io/serviceaccount/token
</filter>

# Filter: Add environment-specific tags
<filter **>
  @type record_transformer
  @id add_env_tags
  enable_ruby true
  <record>
    environment ${ENV['ENVIRONMENT'] || 'unknown'}
    cluster ${ENV['CLUSTER_NAME'] || 'unknown'}
    datacenter ${ENV['DATACENTER'] || 'unknown'}
  </record>
</filter>

# Filter: Redact sensitive data
<filter **>
  @type record_transformer
  @id redact_sensitive
  enable_ruby true
  <record>
    message ${record['message'].to_s.gsub(/password[=:]\s*\S+/i, 'password=[REDACTED]')}
    message ${record['message'].to_s.gsub(/token[=:]\s*\S+/i, 'token=[REDACTED]')}
    message ${record['message'].to_s.gsub(/api[_-]?key[=:]\s*\S+/i, 'api_key=[REDACTED]')}
  </record>
</filter>

# Match: Route to Kafka (for buffering and reliability)
<match kubernetes.**>
  @type kafka2
  @id output_kafka
  brokers kafka-0.kafka:9092,kafka-1.kafka:9092,kafka-2.kafka:9092
  default_topic resilienceai-logs
  
  <format>
    @type json
  </format>
  
  <buffer topic>
    @type file
    path /var/log/fluentd-buffers/kafka
    flush_interval 5s
    retry_type exponential_backoff
    retry_wait 1s
    retry_max_interval 60s
    retry_forever true
    total_limit_size 10GB
    chunk_limit_size 8MB
    queue_limit_length 256
  </buffer>
</match>

# Match: Route critical logs directly to Elasticsearch
<match **.critical **.error>
  @type elasticsearch
  @id output_es_critical
  host elasticsearch-logging
  port 9200
  logstash_format true
  logstash_prefix resilienceai-critical
  include_tag_key true
  type_name _doc
  
  # Index template
  template_name resilienceai_critical
  template_file /fluentd/etc/es_template_critical.json
  
  <buffer>
    @type file
    path /var/log/fluentd-buffers/es-critical
    flush_interval 1s
    retry_type exponential_backoff
    retry_max_interval 30s
    retry_forever true
  </buffer>
</match>

# Match: Route all logs to Elasticsearch
<match **>
  @type elasticsearch
  @id output_es
  host elasticsearch-logging
  port 9200
  logstash_format true
  logstash_prefix resilienceai
  include_tag_key true
  type_name _doc
  
  # Index lifecycle
  index_date_pattern now/d
  
  # Authentication (if enabled)
  # user elastic
  # password ${ENV['ES_PASSWORD']}
  
  # SSL/TLS
  # ssl_verify true
  # ca_file /path/to/ca.crt
  
  <buffer>
    @type file
    path /var/log/fluentd-buffers/es
    flush_interval 10s
    retry_type exponential_backoff
    retry_wait 2s
    retry_max_interval 60s
    retry_forever true
    total_limit_size 50GB
    chunk_limit_size 10MB
    queue_limit_length 512
  </buffer>
</match>

# Match: Archive to S3 (for long-term storage)
<match **>
  @type s3
  @id output_s3_archive
  aws_key_id ${ENV['AWS_ACCESS_KEY_ID']}
  aws_sec_key ${ENV['AWS_SECRET_ACCESS_KEY']}
  s3_bucket resilienceai-logs-archive
  s3_region us-east-1
  path logs/%Y/%m/%d/
  time_slice_format %Y%m%d%H
  
  <format>
    @type json
  </format>
  
  <buffer time>
    @type file
    path /var/log/fluentd-buffers/s3
    timekey 3600
    timekey_wait 10m
    timekey_use_utc true
    chunk_limit_size 256MB
  </buffer>
</match>
```

### 6.2 Elasticsearch Index Templates

**File:** `/app/logging/elasticsearch/template.json`

```json
{
  "index_patterns": ["resilienceai-*"],
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "index.refresh_interval": "5s",
    "index.mapping.total_fields.limit": 10000,
    "index.lifecycle.name": "resilienceai-logs-policy",
    "index.lifecycle.rollover_alias": "resilienceai"
  },
  "mappings": {
    "dynamic_templates": [
      {
        "strings_as_keywords": {
          "match_mapping_type": "string",
          "mapping": {
            "type": "keyword",
            "ignore_above": 1024
          }
        }
      }
    ],
    "properties": {
      "@timestamp": {
        "type": "date"
      },
      "timestamp": {
        "type": "date"
      },
      "level": {
        "type": "keyword"
      },
      "message": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 32766
          }
        }
      },
      "service": {
        "type": "keyword"
      },
      "environment": {
        "type": "keyword"
      },
      "request_id": {
        "type": "keyword"
      },
      "trace_id": {
        "type": "keyword"
      },
      "span_id": {
        "type": "keyword"
      },
      "user_id": {
        "type": "keyword"
      },
      "organization_id": {
        "type": "keyword"
      },
      "category": {
        "type": "keyword"
      },
      "duration_ms": {
        "type": "float"
      },
      "status_code": {
        "type": "integer"
      },
      "kubernetes": {
        "properties": {
          "pod_name": {
            "type": "keyword"
          },
          "namespace_name": {
            "type": "keyword"
          },
          "container_name": {
            "type": "keyword"
          },
          "host": {
            "type": "keyword"
          }
        }
      },
      "geoip": {
        "properties": {
          "location": {
            "type": "geo_point"
          }
        }
      }
    }
  },
  "aliases": {
    "resilienceai-logs": {}
  }
}
```

### 6.3 Index Lifecycle Policy

**File:** `/app/logging/elasticsearch/ilm_policy.json`

```json
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_primary_shard_size": "50GB",
            "max_age": "1d",
            "max_docs": 100000000
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "3d",
        "actions": {
          "set_priority": {
            "priority": 50
          },
          "shrink": {
            "number_of_shards": 1
          },
          "forcemerge": {
            "max_num_segments": 1
          },
          "allocate": {
            "require": {
              "data": "warm"
            }
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "set_priority": {
            "priority": 0
          },
          "freeze": {},
          "allocate": {
            "require": {
              "data": "cold"
            }
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

### 6.4 Logstash Pipeline Configuration

**File:** `/app/logging/logstash/pipeline.conf`

```ruby
# Logstash Pipeline for ResilienceAI
# Processes logs from Kafka and sends to Elasticsearch

input {
  kafka {
    bootstrap_servers => "kafka-0.kafka:9092,kafka-1.kafka:9092,kafka-2.kafka:9092"
    topics => ["resilienceai-logs", "resilienceai-metrics"]
    group_id => "logstash-resilienceai"
    codec => json
    auto_offset_reset => "latest"
    consumer_threads => 4
    decorate_events => true
  }
}

filter {
  # Parse timestamp
  if [timestamp] {
    date {
      match => ["timestamp", "ISO8601"]
      target => "@timestamp"
    }
  }
  
  # Add parsed fields
  mutate {
    add_field => {
      "[parsed][hour_of_day]" => "%{+HH}"
      "[parsed][day_of_week]" => "%{+EEE}"
      "[parsed][service_environment]" => "%{[service]}-%{[environment]}"
    }
  }
  
  # Parse request paths for analysis
  if [path] {
    grok {
      match => {
        "path" => [
          "/api/v%{API_VERSION:api_version}/%{WORD:resource}/%{DATA:action}",
          "/api/%{WORD:resource}/%{DATA:action}"
        ]
      }
      tag_on_failure => ["_grokparsefailure_path"]
    }
  }
  
  # Categorize log levels
  if [level] {
    translate {
      field => "level"
      destination => "[parsed][level_numeric]"
      dictionary => {
        "DEBUG" => 10
        "INFO" => 20
        "WARNING" => 30
        "ERROR" => 40
        "CRITICAL" => 50
        "AUDIT" => 25
        "PERF" => 15
      }
      fallback => 0
    }
  }
  
  # Extract error details
  if [error] and [error][stack_trace] {
    ruby {
      code => '
        stack = event.get("[error][stack_trace]")
        if stack
          lines = stack.split("\n")
          event.set("[error][stack_lines]", lines.length)
          event.set("[error][first_line]", lines.first)
          
          # Extract file and line
          if lines.first =~ /File "([^"]+)", line (\d+)/
            event.set("[error][file]", $1)
            event.set("[error][line]", $2.to_i)
          end
        end
      '
    }
  }
  
  # Performance metrics extraction
  if [duration_ms] {
    ruby {
      code => '
        duration = event.get("duration_ms")
        if duration
          if duration < 100
            event.set("[performance][tier]", "fast")
          elsif duration < 500
            event.set("[performance][tier]", "normal")
          elsif duration < 1000
            event.set("[performance][tier]", "slow")
          else
            event.set("[performance][tier]", "very_slow")
          end
        end
      '
    }
  }
  
  # GeoIP enrichment for client IPs
  if [client_ip] {
    geoip {
      source => "client_ip"
      target => "geoip"
      database => "/usr/share/logstash/GeoLite2-City.mmdb"
    }
  }
  
  # User agent parsing
  if [user_agent] {
    useragent {
      source => "user_agent"
      target => "user_agent_parsed"
    }
  }
  
  # Drop debug logs in production after 7 days
  if [level] == "DEBUG" and [environment] == "production" {
    ruby {
      code => '
        timestamp = event.get("@timestamp")
        if timestamp && (Time.now - timestamp.to_time) > 604800
          event.cancel
        end
      '
    }
  }
}

output {
  # Route to different indices based on log level
  if [level] == "CRITICAL" or [level] == "ERROR" {
    elasticsearch {
      hosts => ["elasticsearch-logging:9200"]
      index => "resilienceai-errors-%{+YYYY.MM.dd}"
      template_name => "resilienceai_errors"
      template => "/usr/share/logstash/templates/errors_template.json"
      template_overwrite => true
    }
  }
  
  # Performance logs
  else if [category] == "performance" or [category] == "timing" {
    elasticsearch {
      hosts => ["elasticsearch-logging:9200"]
      index => "resilienceai-performance-%{+YYYY.MM.dd}"
    }
  }
  
  # Security/audit logs
  else if [category] == "audit" or [category] == "security_event" {
    elasticsearch {
      hosts => ["elasticsearch-logging:9200"]
      index => "resilienceai-audit-%{+YYYY.MM}"
    }
  }
  
  # Default application logs
  else {
    elasticsearch {
      hosts => ["elasticsearch-logging:9200"]
      index => "resilienceai-%{+YYYY.MM.dd}"
      ilm_enabled => true
      ilm_rollover_alias => "resilienceai"
      ilm_pattern => "{now/d}-000001"
      ilm_policy => "resilienceai-logs-policy"
    }
  }
  
  # Also output to stdout for debugging
  if [environment] == "development" {
    stdout {
      codec => rubydebug
    }
  }
}
```

---

## 7. Performance Logging

### 7.1 Performance Metrics Collector

**File:** `/app/logging/performance.py`

```python
"""
Performance logging and metrics collection for ResilienceAI.
"""

import time
import functools
import asyncio
from typing import Any, Callable, Dict, List, Optional, TypeVar
from contextlib import contextmanager
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

from .logger_config import get_logger
from .category_logger import get_performance_logger

logger = get_logger(__name__)
perf_logger = get_performance_logger()

T = TypeVar('T')


@dataclass
class PerformanceSnapshot:
    """Snapshot of performance metrics."""
    operation: str
    count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    durations: List[float] = field(default_factory=list)
    errors: int = 0
    
    @property
    def avg_duration_ms(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total_duration_ms / self.count
    
    @property
    def p50_duration_ms(self) -> float:
        if not self.durations:
            return 0.0
        return statistics.median(self.durations)
    
    @property
    def p95_duration_ms(self) -> float:
        if not self.durations:
            return 0.0
        sorted_durations = sorted(self.durations)
        idx = int(len(sorted_durations) * 0.95)
        return sorted_durations[min(idx, len(sorted_durations) - 1)]
    
    @property
    def p99_duration_ms(self) -> float:
        if not self.durations:
            return 0.0
        sorted_durations = sorted(self.durations)
        idx = int(len(sorted_durations) * 0.99)
        return sorted_durations[min(idx, len(sorted_durations) - 1)]
    
    def record(self, duration_ms: float, error: bool = False):
        """Record a measurement."""
        self.count += 1
        self.total_duration_ms += duration_ms
        self.min_duration_ms = min(self.min_duration_ms, duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)
        self.durations.append(duration_ms)
        
        # Keep only last 1000 measurements for memory efficiency
        if len(self.durations) > 1000:
            self.durations = self.durations[-1000:]
        
        if error:
            self.errors += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation': self.operation,
            'count': self.count,
            'total_duration_ms': round(self.total_duration_ms, 2),
            'avg_duration_ms': round(self.avg_duration_ms, 2),
            'min_duration_ms': round(self.min_duration_ms, 2),
            'max_duration_ms': round(self.max_duration_ms, 2),
            'p50_duration_ms': round(self.p50_duration_ms, 2),
            'p95_duration_ms': round(self.p95_duration_ms, 2),
            'p99_duration_ms': round(self.p99_duration_ms, 2),
            'errors': self.errors,
            'error_rate': round(self.errors / self.count, 4) if self.count > 0 else 0.0
        }


class PerformanceCollector:
    """Collects and reports performance metrics."""
    
    def __init__(self, max_operations: int = 1000):
        self._metrics: Dict[str, PerformanceSnapshot] = defaultdict(
            lambda key: PerformanceSnapshot(operation=key)
        )
        self._max_operations = max_operations
        self._lock = asyncio.Lock()
    
    async def record(
        self,
        operation: str,
        duration_ms: float,
        error: bool = False,
        **extra: Any
    ):
        """Record a performance metric."""
        async with self._lock:
            if operation not in self._metrics:
                if len(self._metrics) >= self._max_operations:
                    # Remove oldest operation
                    oldest = min(self._metrics.keys(), 
                               key=lambda k: self._metrics[k].count)
                    del self._metrics[oldest]
            
            self._metrics[operation].record(duration_ms, error)
        
        # Log slow operations
        if duration_ms > 1000:
            perf_logger.warning(
                'Slow operation detected',
                operation=operation,
                duration_ms=round(duration_ms, 2),
                **extra
            )
    
    async def get_snapshot(self, operation: str) -> Optional[PerformanceSnapshot]:
        """Get snapshot for a specific operation."""
        async with self._lock:
            return self._metrics.get(operation)
    
    async def get_all_snapshots(self) -> Dict[str, Dict[str, Any]]:
        """Get all performance snapshots."""
        async with self._lock:
            return {
                op: snapshot.to_dict()
                for op, snapshot in self._metrics.items()
            }
    
    async def reset(self, operation: Optional[str] = None):
        """Reset metrics for an operation or all operations."""
        async with self._lock:
            if operation:
                if operation in self._metrics:
                    del self._metrics[operation]
            else:
                self._metrics.clear()


# Global collector instance
collector = PerformanceCollector()


class PerformanceTimer:
    """Timer for measuring operation performance."""
    
    def __init__(
        self,
        operation: str,
        log_on_complete: bool = True,
        slow_threshold_ms: float = 1000.0,
        **extra: Any
    ):
        self.operation = operation
        self.log_on_complete = log_on_complete
        self.slow_threshold_ms = slow_threshold_ms
        self.extra = extra
        self.start_time: Optional[float] = None
        self.duration_ms: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000
        
        # Record in collector
        asyncio.create_task(collector.record(
            self.operation,
            self.duration_ms,
            error=exc_type is not None,
            **self.extra
        ))
        
        if self.log_on_complete:
            level = 'warning' if self.duration_ms > self.slow_threshold_ms else 'info'
            log_method = getattr(perf_logger, level)
            log_method(
                f'Operation {self.operation} completed',
                operation=self.operation,
                duration_ms=round(self.duration_ms, 2),
                slow=self.duration_ms > self.slow_threshold_ms,
                error=exc_type is not None,
                **self.extra
            )
    
    async def __aenter__(self):
        self.start_time = time.perf_counter()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000
        
        await collector.record(
            self.operation,
            self.duration_ms,
            error=exc_type is not None,
            **self.extra
        )
        
        if self.log_on_complete:
            level = 'warning' if self.duration_ms > self.slow_threshold_ms else 'info'
            log_method = getattr(perf_logger, level)
            log_method(
                f'Operation {self.operation} completed',
                operation=self.operation,
                duration_ms=round(self.duration_ms, 2),
                slow=self.duration_ms > self.slow_threshold_ms,
                error=exc_type is not None,
                **self.extra
            )


def timed(
    operation: Optional[str] = None,
    log_on_complete: bool = True,
    slow_threshold_ms: float = 1000.0
):
    """
    Decorator to time function execution.
    
    Usage:
        @timed(operation='analyze_resilience', slow_threshold_ms=500)
        async def analyze_resilience(data):
            # Function body
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        op_name = operation or func.__name__
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            with PerformanceTimer(
                op_name,
                log_on_complete,
                slow_threshold_ms,
                function=func.__name__
            ):
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            with PerformanceTimer(
                op_name,
                log_on_complete,
                slow_threshold_ms,
                function=func.__name__
            ):
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Resource usage monitoring
import psutil
import os


class ResourceMonitor:
    """Monitor system resource usage."""
    
    def __init__(self, interval_seconds: float = 60.0):
        self.interval_seconds = interval_seconds
        self._process = psutil.Process(os.getpid())
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current resource metrics."""
        # Memory
        memory_info = self._process.memory_info()
        memory_percent = self._process.memory_percent()
        
        # CPU
        cpu_percent = self._process.cpu_percent(interval=0.1)
        
        # System-wide
        system_memory = psutil.virtual_memory()
        system_cpu = psutil.cpu_percent(interval=0.1)
        disk_usage = psutil.disk_usage('/')
        
        # Network
        net_io = psutil.net_io_counters()
        
        # Open files and connections
        open_files = len(self._process.open_files())
        connections = len(self._process.connections())
        
        # Threads
        threads = self._process.num_threads()
        
        return {
            'process': {
                'memory_rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'memory_vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                'memory_percent': round(memory_percent, 2),
                'cpu_percent': round(cpu_percent, 2),
                'open_files': open_files,
                'connections': connections,
                'threads': threads,
            },
            'system': {
                'memory_percent': round(system_memory.percent, 2),
                'memory_available_mb': round(system_memory.available / 1024 / 1024, 2),
                'cpu_percent': round(system_cpu, 2),
                'disk_percent': round(disk_usage.percent, 2),
                'disk_free_gb': round(disk_usage.free / 1024 / 1024 / 1024, 2),
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
            }
        }
    
    async def start_monitoring(self):
        """Start periodic resource monitoring."""
        while True:
            metrics = self.get_metrics()
            perf_logger.info(
                'Resource metrics',
                **metrics
            )
            await asyncio.sleep(self.interval_seconds)


# Prometheus metrics integration
from prometheus_client import Counter, Histogram, Gauge, Info


class PrometheusMetrics:
    """Prometheus metrics for ResilienceAI."""
    
    # Request metrics
    HTTP_REQUESTS_TOTAL = Counter(
        'resilienceai_http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status_code']
    )
    
    HTTP_REQUEST_DURATION = Histogram(
        'resilienceai_http_request_duration_seconds',
        'HTTP request duration',
        ['method', 'endpoint'],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    )
    
    # Business metrics
    RESILIENCE_ANALYSES_TOTAL = Counter(
        'resilienceai_resilience_analyses_total',
        'Total resilience analyses performed',
        ['organization_id', 'status']
    )
    
    RISK_SCORE = Gauge(
        'resilienceai_risk_score',
        'Current risk score',
        ['organization_id', 'risk_type']
    )
    
    RECOVERY_ACTIONS_TOTAL = Counter(
        'resilienceai_recovery_actions_total',
        'Total recovery actions executed',
        ['action_type', 'status']
    )
    
    # ML metrics
    ML_INFERENCE_DURATION = Histogram(
        'resilienceai_ml_inference_duration_seconds',
        'ML inference duration',
        ['model_name'],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
    )
    
    ML_PREDICTION_CONFIDENCE = Gauge(
        'resilienceai_ml_prediction_confidence',
        'ML prediction confidence',
        ['model_name', 'prediction_type']
    )
    
    # System metrics
    ACTIVE_CONNECTIONS = Gauge(
        'resilienceai_active_connections',
        'Number of active connections'
    )
    
    QUEUE_SIZE = Gauge(
        'resilienceai_queue_size',
        'Current queue size',
        ['queue_name']
    )
    
    # Service info
    SERVICE_INFO = Info(
        'resilienceai_service',
        'Service information'
    )
    
    @classmethod
    def set_service_info(cls, name: str, version: str, environment: str):
        """Set service information."""
        cls.SERVICE_INFO.info({
            'name': name,
            'version': version,
            'environment': environment
        })


---

## 8. Error Logging

### 8.1 Error Handler and Logger

**File:** `/app/logging/error_handler.py`

```python
"""
Comprehensive error logging and handling for ResilienceAI.
"""

import sys
import traceback
import hashlib
import json
from typing import Any, Dict, Optional, Type, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import asyncio

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .logger_config import get_logger, REQUEST_ID, TRACE_ID, USER_ID
from .category_logger import CategoryLogger, LogCategory

logger = get_logger(__name__)
error_logger = CategoryLogger(LogCategory.EXCEPTION)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = 'low'           # Non-critical, can continue
    MEDIUM = 'medium'     # Affects functionality but recoverable
    HIGH = 'high'         # Significant impact, requires attention
    CRITICAL = 'critical' # System-wide impact, immediate action needed


class ErrorCategory(Enum):
    """Categories of errors."""
    VALIDATION = 'validation'
    AUTHENTICATION = 'authentication'
    AUTHORIZATION = 'authorization'
    NOT_FOUND = 'not_found'
    CONFLICT = 'conflict'
    RATE_LIMIT = 'rate_limit'
    TIMEOUT = 'timeout'
    EXTERNAL_SERVICE = 'external_service'
    DATABASE = 'database'
    ML_INFERENCE = 'ml_inference'
    INTERNAL = 'internal'
    CONFIGURATION = 'configuration'


@dataclass
class ErrorContext:
    """Context information for an error."""
    request_id: str
    trace_id: str
    user_id: Optional[str]
    timestamp: str
    endpoint: Optional[str]
    method: Optional[str]
    user_agent: Optional[str]
    client_ip: Optional[str]
    
    @classmethod
    def from_request(cls, request: Optional[Request] = None) -> 'ErrorContext':
        """Create error context from request."""
        if request:
            return cls(
                request_id=REQUEST_ID.get(),
                trace_id=TRACE_ID.get(),
                user_id=USER_ID.get(),
                timestamp=datetime.utcnow().isoformat(),
                endpoint=str(request.url.path),
                method=request.method,
                user_agent=request.headers.get('user-agent'),
                client_ip=request.client.host if request.client else None
            )
        
        return cls(
            request_id=REQUEST_ID.get(),
            trace_id=TRACE_ID.get(),
            user_id=USER_ID.get(),
            timestamp=datetime.utcnow().isoformat(),
            endpoint=None,
            method=None,
            user_agent=None,
            client_ip=None
        )


@dataclass
class ErrorDetails:
    """Detailed error information."""
    error_id: str
    error_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    stack_trace: Optional[str]
    context: ErrorContext
    additional_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_id': self.error_id,
            'error_type': self.error_type,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'stack_trace': self.stack_trace,
            'context': asdict(self.context),
            'additional_data': self.additional_data
        }
    
    def compute_hash(self) -> str:
        """Compute hash for error deduplication."""
        content = f"{self.error_type}:{self.message}:{self.context.endpoint}"
        return hashlib.md5(content.encode()).hexdigest()[:12]


class ErrorLogger:
    """Centralized error logging system."""
    
    def __init__(self):
        self._error_counts: Dict[str, int] = {}
        self._lock = asyncio.Lock()
    
    async def log_error(
        self,
        exception: Exception,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        request: Optional[Request] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> ErrorDetails:
        """Log an error with full context."""
        
        # Extract stack trace
        stack_trace = None
        if hasattr(exception, '__traceback__'):
            stack_trace = ''.join(traceback.format_exception(
                type(exception), exception, exception.__traceback__
            ))
        
        # Create error details
        error_details = ErrorDetails(
            error_id=str(hash(exception) % 1000000),
            error_type=type(exception).__name__,
            message=str(exception),
            severity=severity,
            category=category,
            stack_trace=stack_trace,
            context=ErrorContext.from_request(request),
            additional_data=additional_data or {}
        )
        
        # Compute deduplication hash
        error_hash = error_details.compute_hash()
        
        async with self._lock:
            self._error_counts[error_hash] = self._error_counts.get(error_hash, 0) + 1
            count = self._error_counts[error_hash]
        
        # Log based on severity
        log_data = {
            'error_id': error_details.error_id,
            'error_hash': error_hash,
            'error_type': error_details.error_type,
            'category': category.value,
            'severity': severity.value,
            'message': error_details.message,
            'endpoint': error_details.context.endpoint,
            'count': count,
            'trace_id': error_details.context.trace_id,
            'stack_trace': stack_trace if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else None
        }
        
        if severity == ErrorSeverity.CRITICAL:
            error_logger.critical('Critical error occurred', **log_data)
        elif severity == ErrorSeverity.HIGH:
            error_logger.error('High severity error', **log_data)
        elif severity == ErrorSeverity.MEDIUM:
            error_logger.error('Error occurred', **log_data)
        else:
            error_logger.warning('Low severity error', **log_data)
        
        # Send to external error tracking (e.g., Sentry)
        await self._send_to_external_tracker(error_details)
        
        return error_details
    
    async def _send_to_external_tracker(self, error_details: ErrorDetails):
        """Send error to external tracking service."""
        # Integration with Sentry, Rollbar, etc.
        try:
            import sentry_sdk
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('error_category', error_details.category.value)
                scope.set_tag('error_severity', error_details.severity.value)
                scope.set_extra('error_context', asdict(error_details.context))
                scope.set_extra('additional_data', error_details.additional_data)
                
                sentry_sdk.capture_exception(
                    Exception(error_details.message),
                    scope=scope
                )
        except ImportError:
            pass
    
    async def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        async with self._lock:
            return {
                'unique_errors': len(self._error_counts),
                'total_occurrences': sum(self._error_counts.values()),
                'top_errors': sorted(
                    self._error_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }


# Global error logger instance
error_logger_instance = ErrorLogger()


# Exception to error category mapping
EXCEPTION_CATEGORY_MAP: Dict[Type[Exception], ErrorCategory] = {
    ValueError: ErrorCategory.VALIDATION,
    TypeError: ErrorCategory.VALIDATION,
    KeyError: ErrorCategory.VALIDATION,
    IndexError: ErrorCategory.VALIDATION,
    PermissionError: ErrorCategory.AUTHORIZATION,
    FileNotFoundError: ErrorCategory.NOT_FOUND,
    TimeoutError: ErrorCategory.TIMEOUT,
    ConnectionError: ErrorCategory.EXTERNAL_SERVICE,
    ConnectionRefusedError: ErrorCategory.EXTERNAL_SERVICE,
    ConnectionResetError: ErrorCategory.EXTERNAL_SERVICE,
}


def get_error_category(exception: Exception) -> ErrorCategory:
    """Determine error category from exception type."""
    exception_type = type(exception)
    return EXCEPTION_CATEGORY_MAP.get(exception_type, ErrorCategory.INTERNAL)


def get_error_severity(exception: Exception) -> ErrorSeverity:
    """Determine error severity from exception."""
    # Critical exceptions
    if isinstance(exception, (MemoryError, RecursionError, SystemError)):
        return ErrorSeverity.CRITICAL
    
    # High severity
    if isinstance(exception, (ConnectionError, TimeoutError)):
        return ErrorSeverity.HIGH
    
    # Default
    return ErrorSeverity.MEDIUM


# FastAPI exception handlers

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            'field': '.'.join(str(x) for x in error['loc']),
            'message': error['msg'],
            'type': error['type']
        })
    
    await error_logger_instance.log_error(
        exception=exc,
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.LOW,
        request=request,
        additional_data={'validation_errors': errors}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'error': 'Validation Error',
            'error_id': REQUEST_ID.get(),
            'details': errors
        }
    )


async def http_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle HTTP exceptions."""
    from starlette.exceptions import HTTPException
    
    if isinstance(exc, HTTPException):
        # Map status codes to categories
        category_map = {
            400: ErrorCategory.VALIDATION,
            401: ErrorCategory.AUTHENTICATION,
            403: ErrorCategory.AUTHORIZATION,
            404: ErrorCategory.NOT_FOUND,
            409: ErrorCategory.CONFLICT,
            429: ErrorCategory.RATE_LIMIT,
            500: ErrorCategory.INTERNAL,
            502: ErrorCategory.EXTERNAL_SERVICE,
            503: ErrorCategory.EXTERNAL_SERVICE,
            504: ErrorCategory.TIMEOUT,
        }
        
        category = category_map.get(exc.status_code, ErrorCategory.INTERNAL)
        severity = ErrorSeverity.HIGH if exc.status_code >= 500 else ErrorSeverity.MEDIUM
        
        await error_logger_instance.log_error(
            exception=exc,
            category=category,
            severity=severity,
            request=request,
            additional_data={'status_code': exc.status_code}
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                'error': exc.detail if hasattr(exc, 'detail') else 'Error',
                'error_id': REQUEST_ID.get()
            }
        )
    
    # Default handler
    return await general_exception_handler(request, exc)


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle general exceptions."""
    error_details = await error_logger_instance.log_error(
        exception=exc,
        category=get_error_category(exc),
        severity=get_error_severity(exc),
        request=request
    )
    
    # Return safe error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'error': 'Internal Server Error',
            'error_id': error_details.error_id,
            'message': 'An unexpected error occurred. Please try again later.'
        }
    )


# Register exception handlers
def register_exception_handlers(app):
    """Register all exception handlers with FastAPI app."""
    from starlette.exceptions import HTTPException as StarletteHTTPException
    
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info('Exception handlers registered')


# Circuit breaker integration
class CircuitBreakerError(Exception):
    """Error when circuit breaker is open."""
    pass


async def log_circuit_breaker_event(
    service_name: str,
    state: str,
    failure_count: int,
    last_error: Optional[str] = None
):
    """Log circuit breaker state changes."""
    error_logger.info(
        'Circuit breaker state changed',
        service_name=service_name,
        state=state,
        failure_count=failure_count,
        last_error=last_error,
        category=LogCategory.CIRCUIT_BREAKER.value
    )


# Retry logging
async def log_retry_attempt(
    operation: str,
    attempt: int,
    max_attempts: int,
    exception: Optional[Exception] = None,
    delay: Optional[float] = None
):
    """Log retry attempts."""
    log_data = {
        'operation': operation,
        'attempt': attempt,
        'max_attempts': max_attempts,
        'category': LogCategory.RETRY.value
    }
    
    if exception:
        log_data['error'] = str(exception)
        log_data['error_type'] = type(exception).__name__
    
    if delay:
        log_data['delay_seconds'] = delay
    
    if attempt >= max_attempts:
        error_logger.error('Retry exhausted', **log_data)
    else:
        error_logger.warning('Retry attempt', **log_data)
```

---

## 9. Security Logging

### 9.1 Security Event Logger

**File:** `/app/logging/security.py`

```python
"""
Security logging for ResilienceAI - authentication, authorization, and audit events.
"""

import hashlib
import hmac
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

from fastapi import Request

from .logger_config import get_logger, REQUEST_ID, USER_ID, ORGANIZATION_ID
from .category_logger import CategoryLogger, LogCategory

logger = get_logger(__name__)
security_logger = CategoryLogger(LogCategory.SECURITY_EVENT)
audit_logger = CategoryLogger(LogCategory.AUDIT)


class SecurityEventType(Enum):
    """Types of security events."""
    # Authentication
    LOGIN_SUCCESS = 'login_success'
    LOGIN_FAILURE = 'login_failure'
    LOGOUT = 'logout'
    TOKEN_REFRESH = 'token_refresh'
    TOKEN_REVOKED = 'token_revoked'
    MFA_ENABLED = 'mfa_enabled'
    MFA_DISABLED = 'mfa_disabled'
    MFA_CHALLENGE = 'mfa_challenge'
    PASSWORD_CHANGED = 'password_changed'
    PASSWORD_RESET_REQUESTED = 'password_reset_requested'
    PASSWORD_RESET_COMPLETED = 'password_reset_completed'
    
    # Authorization
    ACCESS_DENIED = 'access_denied'
    PERMISSION_GRANTED = 'permission_granted'
    PERMISSION_REVOKED = 'permission_revoked'
    ROLE_ASSIGNED = 'role_assigned'
    ROLE_REMOVED = 'role_removed'
    
    # Data Access
    DATA_ACCESS = 'data_access'
    DATA_EXPORT = 'data_export'
    DATA_MODIFICATION = 'data_modification'
    DATA_DELETION = 'data_deletion'
    BULK_OPERATION = 'bulk_operation'
    
    # API Security
    RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded'
    SUSPICIOUS_REQUEST = 'suspicious_request'
    INVALID_TOKEN = 'invalid_token'
    EXPIRED_TOKEN = 'expired_token'
    
    # System Security
    CONFIGURATION_CHANGE = 'configuration_change'
    SECURITY_ALERT = 'security_alert'
    ANOMALY_DETECTED = 'anomaly_detected'


class SecuritySeverity(Enum):
    """Security event severity levels."""
    INFO = 'info'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


@dataclass
class SecurityEvent:
    """Security event data structure."""
    event_type: SecurityEventType
    severity: SecuritySeverity
    user_id: Optional[str]
    organization_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: Optional[str]
    result: str
    details: Dict[str, Any]
    timestamp: str
    request_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'user_id': self._hash_sensitive(self.user_id),
            'organization_id': self.organization_id,
            'ip_address': self._hash_ip(self.ip_address),
            'user_agent': self.user_agent,
            'resource': self.resource,
            'action': self.action,
            'result': self.result,
            'details': self._sanitize_details(self.details),
            'timestamp': self.timestamp,
            'request_id': self.request_id
        }
    
    def _hash_sensitive(self, value: Optional[str]) -> Optional[str]:
        """Hash sensitive values for privacy."""
        if not value:
            return None
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    
    def _hash_ip(self, ip: Optional[str]) -> Optional[str]:
        """Hash IP address (preserve first octet for geo analysis)."""
        if not ip:
            return None
        parts = ip.split('.')
        if len(parts) == 4:
            # Keep first octet for rough geo analysis
            hashed = hashlib.sha256('.'.join(parts[1:]).encode()).hexdigest()[:8]
            return f"{parts[0]}.xxx.xxx.{hashed}"
        return self._hash_sensitive(ip)
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from details."""
        sanitized = {}
        sensitive_keys = {'password', 'token', 'secret', 'api_key', 'credit_card'}
        
        for key, value in details.items():
            if any(s in key.lower() for s in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_details(value)
            else:
                sanitized[key] = value
        
        return sanitized


class SecurityLogger:
    """Security event logging system."""
    
    # Severity mapping for event types
    EVENT_SEVERITY: Dict[SecurityEventType, SecuritySeverity] = {
        SecurityEventType.LOGIN_SUCCESS: SecuritySeverity.INFO,
        SecurityEventType.LOGIN_FAILURE: SecuritySeverity.MEDIUM,
        SecurityEventType.LOGOUT: SecuritySeverity.INFO,
        SecurityEventType.ACCESS_DENIED: SecuritySeverity.HIGH,
        SecurityEventType.RATE_LIMIT_EXCEEDED: SecuritySeverity.MEDIUM,
        SecurityEventType.SUSPICIOUS_REQUEST: SecuritySeverity.HIGH,
        SecurityEventType.ANOMALY_DETECTED: SecuritySeverity.CRITICAL,
        SecurityEventType.DATA_EXPORT: SecuritySeverity.MEDIUM,
        SecurityEventType.BULK_OPERATION: SecuritySeverity.MEDIUM,
    }
    
    def __init__(self):
        self._alert_handlers: List[Callable] = []
    
    def register_alert_handler(self, handler: Callable):
        """Register a handler for critical security alerts."""
        self._alert_handlers.append(handler)
    
    async def log_event(
        self,
        event_type: SecurityEventType,
        result: str = 'success',
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        severity: Optional[SecuritySeverity] = None
    ):
        """Log a security event."""
        
        # Extract request info
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get('user-agent')
        
        # Determine severity
        event_severity = severity or self.EVENT_SEVERITY.get(
            event_type, SecuritySeverity.INFO
        )
        
        # Create event
        event = SecurityEvent(
            event_type=event_type,
            severity=event_severity,
            user_id=user_id or USER_ID.get(),
            organization_id=organization_id or ORGANIZATION_ID.get(),
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            timestamp=datetime.utcnow().isoformat(),
            request_id=REQUEST_ID.get()
        )
        
        # Log based on severity
        log_data = event.to_dict()
        
        if event_severity == SecuritySeverity.CRITICAL:
            security_logger.critical(f'Critical security event: {event_type.value}', **log_data)
            await self._send_alert(event)
        elif event_severity == SecuritySeverity.HIGH:
            security_logger.error(f'High severity security event: {event_type.value}', **log_data)
            await self._send_alert(event)
        elif event_severity == SecuritySeverity.MEDIUM:
            security_logger.warning(f'Security event: {event_type.value}', **log_data)
        else:
            security_logger.info(f'Security event: {event_type.value}', **log_data)
        
        # Always log audit events
        if event_type in [
            SecurityEventType.DATA_ACCESS,
            SecurityEventType.DATA_MODIFICATION,
            SecurityEventType.DATA_DELETION,
            SecurityEventType.DATA_EXPORT
        ]:
            audit_logger.info(
                'Data access audit',
                **log_data
            )
    
    async def _send_alert(self, event: SecurityEvent):
        """Send alert for critical security events."""
        for handler in self._alert_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f'Alert handler failed: {e}')
    
    # Convenience methods for common events
    
    async def log_login(
        self,
        success: bool,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        mfa_used: bool = False,
        request: Optional[Request] = None,
        failure_reason: Optional[str] = None
    ):
        """Log login attempt."""
        event_type = SecurityEventType.LOGIN_SUCCESS if success else SecurityEventType.LOGIN_FAILURE
        details = {'mfa_used': mfa_used}
        if failure_reason:
            details['failure_reason'] = failure_reason
        
        await self.log_event(
            event_type=event_type,
            result='success' if success else 'failure',
            user_id=user_id,
            organization_id=organization_id,
            resource='authentication',
            action='login',
            details=details,
            request=request
        )
    
    async def log_access_denied(
        self,
        resource: str,
        action: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        reason: Optional[str] = None,
        request: Optional[Request] = None
    ):
        """Log access denied event."""
        await self.log_event(
            event_type=SecurityEventType.ACCESS_DENIED,
            result='denied',
            user_id=user_id,
            organization_id=organization_id,
            resource=resource,
            action=action,
            details={'reason': reason} if reason else {},
            request=request,
            severity=SecuritySeverity.HIGH
        )
    
    async def log_data_access(
        self,
        resource_type: str,
        resource_id: str,
        action: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        request: Optional[Request] = None
    ):
        """Log data access event."""
        await self.log_event(
            event_type=SecurityEventType.DATA_ACCESS,
            result='success',
            user_id=user_id,
            organization_id=organization_id,
            resource=f"{resource_type}:{resource_id}",
            action=action,
            request=request
        )
    
    async def log_rate_limit(
        self,
        endpoint: str,
        limit: int,
        window: str,
        request: Optional[Request] = None
    ):
        """Log rate limit exceeded event."""
        await self.log_event(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            result='blocked',
            resource=endpoint,
            action='request',
            details={'limit': limit, 'window': window},
            request=request
        )
    
    async def log_suspicious_activity(
        self,
        activity_type: str,
        details: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log suspicious activity."""
        await self.log_event(
            event_type=SecurityEventType.SUSPICIOUS_REQUEST,
            result='detected',
            details={'activity_type': activity_type, **details},
            request=request,
            severity=SecuritySeverity.HIGH
        )


# Global security logger instance
security_logger_instance = SecurityLogger()


# Audit log compliance helpers

class AuditLog:
    """Compliance-focused audit logging."""
    
    REQUIRED_FIELDS = [
        'timestamp',
        'user_id',
        'action',
        'resource',
        'result'
    ]
    
    @staticmethod
    def validate_entry(entry: Dict[str, Any]) -> bool:
        """Validate audit log entry has required fields."""
        return all(field in entry for field in AuditLog.REQUIRED_FIELDS)
    
    @staticmethod
    def sign_entry(entry: Dict[str, Any], secret_key: str) -> str:
        """Create HMAC signature for audit entry integrity."""
        entry_str = json.dumps(entry, sort_keys=True)
        return hmac.new(
            secret_key.encode(),
            entry_str.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_signature(entry: Dict[str, Any], signature: str, secret_key: str) -> bool:
        """Verify audit entry signature."""
        computed = AuditLog.sign_entry(entry, secret_key)
        return hmac.compare_digest(computed, signature)


# Middleware for automatic security logging

class SecurityLoggingMiddleware:
    """Middleware to automatically log security-relevant events."""
    
    SENSITIVE_ENDPOINTS = [
        '/api/auth/login',
        '/api/auth/logout',
        '/api/auth/refresh',
        '/api/users',
        '/api/permissions',
        '/api/export',
    ]
    
    async def __call__(self, request: Request, call_next):
        from starlette.middleware.base import BaseHTTPMiddleware
        
        response = await call_next(request)
        
        # Log access to sensitive endpoints
        if any(request.url.path.startswith(endpoint) for endpoint in self.SENSITIVE_ENDPOINTS):
            await security_logger_instance.log_data_access(
                resource_type='endpoint',
                resource_id=request.url.path,
                action=request.method,
                request=request
            )
        
        return response


---

## 10. Log Retention and Archival

### 10.1 Retention Policy Configuration

**File:** `/app/logging/retention.py`

```python
"""
Log retention and archival policies for ResilienceAI.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio

from .logger_config import get_logger

logger = get_logger(__name__)


class RetentionTier(Enum):
    """Log retention tiers."""
    HOT = 'hot'       # Fast access, SSD storage
    WARM = 'warm'     # Slower access, HDD storage
    COLD = 'cold'     # Archive, compressed
    DELETE = 'delete' # Permanently removed


@dataclass
class RetentionRule:
    """Log retention rule configuration."""
    name: str
    log_categories: List[str]
    tiers: Dict[RetentionTier, timedelta]
    compression: bool = True
    encryption: bool = True
    
    def get_tier_for_age(self, age: timedelta) -> RetentionTier:
        """Determine retention tier for log age."""
        sorted_tiers = sorted(
            self.tiers.items(),
            key=lambda x: x[1]
        )
        
        for tier, threshold in sorted_tiers:
            if age < threshold:
                return tier
        
        return RetentionTier.DELETE


class RetentionPolicy:
    """Centralized log retention policy manager."""
    
    # Default retention rules
    DEFAULT_RULES: List[RetentionRule] = [
        # Application logs
        RetentionRule(
            name='application_logs',
            log_categories=['application', 'http_request', 'http_response'],
            tiers={
                RetentionTier.HOT: timedelta(days=7),
                RetentionTier.WARM: timedelta(days=30),
                RetentionTier.COLD: timedelta(days=90),
            },
            compression=True,
            encryption=True
        ),
        # Error logs - longer retention
        RetentionRule(
            name='error_logs',
            log_categories=['error', 'exception', 'critical'],
            tiers={
                RetentionTier.HOT: timedelta(days=30),
                RetentionTier.WARM: timedelta(days=90),
                RetentionTier.COLD: timedelta(days=365),
            },
            compression=True,
            encryption=True
        ),
        # Security/audit logs - longest retention for compliance
        RetentionRule(
            name='security_logs',
            log_categories=['audit', 'security_event', 'authentication'],
            tiers={
                RetentionTier.HOT: timedelta(days=30),
                RetentionTier.WARM: timedelta(days=90),
                RetentionTier.COLD: timedelta(days=2555),  # 7 years
            },
            compression=True,
            encryption=True
        ),
        # Performance logs
        RetentionRule(
            name='performance_logs',
            log_categories=['performance', 'timing', 'metrics'],
            tiers={
                RetentionTier.HOT: timedelta(days=3),
                RetentionTier.WARM: timedelta(days=14),
                RetentionTier.COLD: timedelta(days=90),
            },
            compression=True,
            encryption=False
        ),
        # Debug logs - shortest retention
        RetentionRule(
            name='debug_logs',
            log_categories=['debug'],
            tiers={
                RetentionTier.HOT: timedelta(hours=24),
                RetentionTier.WARM: timedelta(days=7),
            },
            compression=True,
            encryption=False
        ),
    ]
    
    def __init__(self, rules: Optional[List[RetentionRule]] = None):
        self.rules = rules or self.DEFAULT_RULES
        self._rule_map: Dict[str, RetentionRule] = {}
        self._build_rule_map()
    
    def _build_rule_map(self):
        """Build category to rule mapping."""
        for rule in self.rules:
            for category in rule.log_categories:
                self._rule_map[category] = rule
    
    def get_rule_for_category(self, category: str) -> Optional[RetentionRule]:
        """Get retention rule for a log category."""
        return self._rule_map.get(category)
    
    def should_retain(
        self,
        category: str,
        log_timestamp: datetime,
        tier: RetentionTier
    ) -> bool:
        """Check if logs should be retained in given tier."""
        rule = self.get_rule_for_category(category)
        if not rule:
            return False
        
        age = datetime.utcnow() - log_timestamp
        current_tier = rule.get_tier_for_age(age)
        
        # Check if current tier is at or before requested tier
        tier_order = [RetentionTier.HOT, RetentionTier.WARM, RetentionTier.COLD]
        
        if tier not in tier_order:
            return current_tier != RetentionTier.DELETE
        
        requested_idx = tier_order.index(tier)
        
        for t in tier_order[:requested_idx + 1]:
            if current_tier == t:
                return True
        
        return False


class LogArchiver:
    """Archives logs to long-term storage."""
    
    def __init__(
        self,
        s3_bucket: str,
        s3_prefix: str = 'logs/',
        compression_format: str = 'gzip'
    ):
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.compression_format = compression_format
        self._archive_handlers: List[Callable] = []
    
    def register_handler(self, handler: Callable):
        """Register an archive handler."""
        self._archive_handlers.append(handler)
    
    async def archive_logs(
        self,
        logs: List[Dict],
        category: str,
        date: datetime
    ):
        """Archive logs to S3."""
        import boto3
        import gzip
        import json
        
        # Format logs
        log_data = '\n'.join(json.dumps(log) for log in logs)
        
        # Compress
        if self.compression_format == 'gzip':
            compressed = gzip.compress(log_data.encode())
        else:
            compressed = log_data.encode()
        
        # Generate S3 key
        key = f"{self.s3_prefix}{category}/{date.strftime('%Y/%m/%d')}/logs.json.gz"
        
        # Upload to S3
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=self.s3_bucket,
            Key=key,
            Body=compressed,
            ContentType='application/gzip',
            Metadata={
                'category': category,
                'date': date.isoformat(),
                'log-count': str(len(logs))
            }
        )
        
        logger.info(
            'Logs archived to S3',
            bucket=self.s3_bucket,
            key=key,
            category=category,
            log_count=len(logs)
        )
        
        # Notify handlers
        for handler in self._archive_handlers:
            try:
                await handler(category, date, key)
            except Exception as e:
                logger.error(f'Archive handler failed: {e}')
    
    async def restore_logs(
        self,
        category: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Restore archived logs from S3."""
        import boto3
        import gzip
        import json
        
        s3 = boto3.client('s3')
        logs = []
        
        # List objects in date range
        current = start_date
        while current <= end_date:
            prefix = f"{self.s3_prefix}{category}/{current.strftime('%Y/%m/%d')}/"
            
            response = s3.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=prefix
            )
            
            for obj in response.get('Contents', []):
                # Download and decompress
                response = s3.get_object(
                    Bucket=self.s3_bucket,
                    Key=obj['Key']
                )
                
                compressed = response['Body'].read()
                decompressed = gzip.decompress(compressed)
                
                # Parse logs
                for line in decompressed.decode().strip().split('\n'):
                    logs.append(json.loads(line))
            
            current += timedelta(days=1)
        
        return logs


class RetentionEnforcer:
    """Enforces log retention policies."""
    
    def __init__(
        self,
        policy: RetentionPolicy,
        elasticsearch_host: str = 'elasticsearch-logging:9200'
    ):
        self.policy = policy
        self.elasticsearch_host = elasticsearch_host
    
    async def enforce_retention(self):
        """Enforce retention policies on Elasticsearch indices."""
        from elasticsearch import Elasticsearch
        
        es = Elasticsearch([self.elasticsearch_host])
        
        # Get all indices
        indices = es.indices.get_alias(index='resilienceai-*')
        
        for index_name in indices:
            # Extract date from index name
            try:
                date_str = index_name.split('-')[-1]  # resilienceai-2024.01.15
                index_date = datetime.strptime(date_str, '%Y.%m.%d')
            except (ValueError, IndexError):
                continue
            
            # Determine category from index name
            category = self._extract_category(index_name)
            rule = self.policy.get_rule_for_category(category)
            
            if not rule:
                continue
            
            # Check age
            age = datetime.utcnow() - index_date
            tier = rule.get_tier_for_age(age)
            
            # Apply retention action
            if tier == RetentionTier.DELETE:
                await self._delete_index(es, index_name)
            elif tier == RetentionTier.COLD:
                await self._move_to_cold(es, index_name)
            elif tier == RetentionTier.WARM:
                await self._move_to_warm(es, index_name)
    
    def _extract_category(self, index_name: str) -> str:
        """Extract category from index name."""
        if 'error' in index_name:
            return 'error'
        elif 'audit' in index_name or 'security' in index_name:
            return 'audit'
        elif 'performance' in index_name:
            return 'performance'
        return 'application'
    
    async def _delete_index(self, es, index_name: str):
        """Delete an index."""
        try:
            es.indices.delete(index=index_name)
            logger.info(f'Deleted index {index_name} per retention policy')
        except Exception as e:
            logger.error(f'Failed to delete index {index_name}: {e}')
    
    async def _move_to_warm(self, es, index_name: str):
        """Move index to warm tier."""
        try:
            es.indices.put_settings(
                index=index_name,
                body={
                    'index.routing.allocation.require.data': 'warm',
                    'index.number_of_replicas': 0
                }
            )
            logger.info(f'Moved index {index_name} to warm tier')
        except Exception as e:
            logger.error(f'Failed to move index {index_name} to warm: {e}')
    
    async def _move_to_cold(self, es, index_name: str):
        """Move index to cold tier."""
        try:
            # Freeze index
            es.indices.freeze(index=index_name)
            
            # Move to cold nodes
            es.indices.put_settings(
                index=index_name,
                body={
                    'index.routing.allocation.require.data': 'cold'
                }
            )
            
            logger.info(f'Moved index {index_name} to cold tier')
        except Exception as e:
            logger.error(f'Failed to move index {index_name} to cold: {e}')


# Retention schedule runner
async def run_retention_schedule(
    enforcer: RetentionEnforcer,
    interval_hours: float = 24.0
):
    """Run retention enforcement on schedule."""
    while True:
        try:
            await enforcer.enforce_retention()
            logger.info('Retention enforcement completed')
        except Exception as e:
            logger.error(f'Retention enforcement failed: {e}')
        
        await asyncio.sleep(interval_hours * 3600)
```

---

## 11. Log Analysis and Alerting

### 11.1 Log Analysis Engine

**File:** `/app/logging/analysis.py`

```python
"""
Log analysis and anomaly detection for ResilienceAI.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import asyncio
import re
import statistics

from .logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class LogPattern:
    """Detected log pattern."""
    pattern: str
    regex: str
    count: int
    first_seen: datetime
    last_seen: datetime
    examples: List[str]
    severity: str


@dataclass
class Anomaly:
    """Detected anomaly."""
    anomaly_type: str
    severity: str
    description: str
    affected_service: Optional[str]
    metric_name: str
    metric_value: float
    expected_range: tuple
    timestamp: datetime
    related_logs: List[str]


class PatternDetector:
    """Detect patterns in logs."""
    
    # Common error patterns
    ERROR_PATTERNS = [
        (r'Database connection.*failed', 'database_connection_failure', 'high'),
        (r'Timeout.*exceeded', 'timeout_error', 'medium'),
        (r'Rate limit.*exceeded', 'rate_limit_hit', 'medium'),
        (r'Memory.*exceeded', 'memory_error', 'critical'),
        (r'Authentication.*failed', 'auth_failure', 'high'),
        (r'Permission.*denied', 'permission_denied', 'high'),
    ]
    
    def __init__(self):
        self._patterns: Dict[str, LogPattern] = {}
        self._lock = asyncio.Lock()
    
    async def analyze_logs(self, logs: List[Dict[str, Any]]) -> List[LogPattern]:
        """Analyze logs for patterns."""
        async with self._lock:
            for log in logs:
                message = log.get('message', '')
                
                for pattern_regex, pattern_name, severity in self.ERROR_PATTERNS:
                    if re.search(pattern_regex, message, re.IGNORECASE):
                        if pattern_name not in self._patterns:
                            self._patterns[pattern_name] = LogPattern(
                                pattern=pattern_name,
                                regex=pattern_regex,
                                count=0,
                                first_seen=datetime.utcnow(),
                                last_seen=datetime.utcnow(),
                                examples=[],
                                severity=severity
                            )
                        
                        pattern = self._patterns[pattern_name]
                        pattern.count += 1
                        pattern.last_seen = datetime.utcnow()
                        
                        if len(pattern.examples) < 5:
                            pattern.examples.append(message[:200])
            
            return list(self._patterns.values())
    
    async def get_trending_patterns(
        self,
        min_count: int = 10,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[LogPattern]:
        """Get patterns trending in recent time window."""
        cutoff = datetime.utcnow() - time_window
        
        async with self._lock:
            return [
                p for p in self._patterns.values()
                if p.count >= min_count and p.last_seen > cutoff
            ]


class AnomalyDetector:
    """Detect anomalies in log metrics."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self._metrics_history: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def record_metric(self, metric_name: str, value: float):
        """Record a metric value."""
        async with self._lock:
            self._metrics_history[metric_name].append(value)
            
            # Keep only recent values
            if len(self._metrics_history[metric_name]) > self.window_size:
                self._metrics_history[metric_name] = \
                    self._metrics_history[metric_name][-self.window_size:]
    
    async def detect_anomalies(
        self,
        metric_name: str,
        current_value: float,
        threshold_std: float = 3.0
    ) -> Optional[Anomaly]:
        """Detect if current value is anomalous."""
        async with self._lock:
            history = self._metrics_history.get(metric_name, [])
            
            if len(history) < 10:
                return None
            
            mean = statistics.mean(history)
            std = statistics.stdev(history) if len(history) > 1 else 0
            
            if std == 0:
                return None
            
            z_score = abs(current_value - mean) / std
            
            if z_score > threshold_std:
                # Determine severity
                if z_score > 5:
                    severity = 'critical'
                elif z_score > 4:
                    severity = 'high'
                else:
                    severity = 'medium'
                
                return Anomaly(
                    anomaly_type='statistical_outlier',
                    severity=severity,
                    description=f'{metric_name} is {z_score:.2f} standard deviations from mean',
                    affected_service=None,
                    metric_name=metric_name,
                    metric_value=current_value,
                    expected_range=(mean - threshold_std * std, mean + threshold_std * std),
                    timestamp=datetime.utcnow(),
                    related_logs=[]
                )
            
            return None


class LogAggregator:
    """Aggregate logs for analysis."""
    
    def __init__(self):
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._service_counts: Dict[str, int] = defaultdict(int)
        self._level_counts: Dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()
    
    async def aggregate(self, logs: List[Dict[str, Any]]):
        """Aggregate log statistics."""
        async with self._lock:
            for log in logs:
                # Count by error type
                error_type = log.get('error_type')
                if error_type:
                    self._error_counts[error_type] += 1
                
                # Count by service
                service = log.get('service', 'unknown')
                self._service_counts[service] += 1
                
                # Count by level
                level = log.get('level', 'INFO')
                self._level_counts[level] += 1
    
    async def get_summary(self) -> Dict[str, Any]:
        """Get aggregation summary."""
        async with self._lock:
            return {
                'error_counts': dict(self._error_counts),
                'service_counts': dict(self._service_counts),
                'level_counts': dict(self._level_counts),
                'total_errors': sum(self._error_counts.values()),
                'top_errors': Counter(self._error_counts).most_common(10),
                'top_services': Counter(self._service_counts).most_common(10)
            }
    
    async def reset(self):
        """Reset aggregation counters."""
        async with self._lock:
            self._error_counts.clear()
            self._service_counts.clear()
            self._level_counts.clear()


class AlertRule:
    """Alert rule configuration."""
    
    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: str,
        notification_channels: List[str],
        cooldown_minutes: int = 15
    ):
        self.name = name
        self.condition = condition
        self.severity = severity
        self.notification_channels = notification_channels
        self.cooldown_minutes = cooldown_minutes
        self._last_triggered: Optional[datetime] = None
    
    def should_trigger(self, data: Dict[str, Any]) -> bool:
        """Check if alert should trigger."""
        # Check cooldown
        if self._last_triggered:
            cooldown = timedelta(minutes=self.cooldown_minutes)
            if datetime.utcnow() - self._last_triggered < cooldown:
                return False
        
        # Check condition
        if self.condition(data):
            self._last_triggered = datetime.utcnow()
            return True
        
        return False


class AlertManager:
    """Manage and evaluate alert rules."""
    
    def __init__(self):
        self._rules: List[AlertRule] = []
        self._handlers: Dict[str, Callable] = {}
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self._rules.append(rule)
    
    def register_handler(self, channel: str, handler: Callable):
        """Register notification handler."""
        self._handlers[channel] = handler
    
    async def evaluate(self, data: Dict[str, Any]):
        """Evaluate all alert rules."""
        for rule in self._rules:
            if rule.should_trigger(data):
                await self._send_alert(rule, data)
    
    async def _send_alert(self, rule: AlertRule, data: Dict[str, Any]):
        """Send alert through configured channels."""
        alert = {
            'rule_name': rule.name,
            'severity': rule.severity,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        for channel in rule.notification_channels:
            handler = self._handlers.get(channel)
            if handler:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f'Alert handler failed for {channel}: {e}')


# Pre-configured alert rules

def create_default_alert_rules() -> List[AlertRule]:
    """Create default alert rules."""
    
    # High error rate alert
    def high_error_rate(data):
        total = data.get('total_logs', 1)
        errors = data.get('level_counts', {}).get('ERROR', 0)
        return (errors / total) > 0.1  # 10% error rate
    
    # Service down alert
    def service_down(data):
        service_health = data.get('service_health', {})
        return any(not healthy for healthy in service_health.values())
    
    # Slow response alert
    def slow_responses(data):
        p95_latency = data.get('latency_p95', 0)
        return p95_latency > 5000  # 5 seconds
    
    return [
        AlertRule(
            name='high_error_rate',
            condition=high_error_rate,
            severity='high',
            notification_channels=['slack', 'pagerduty'],
            cooldown_minutes=5
        ),
        AlertRule(
            name='service_down',
            condition=service_down,
            severity='critical',
            notification_channels=['slack', 'pagerduty', 'email'],
            cooldown_minutes=1
        ),
        AlertRule(
            name='slow_responses',
            condition=slow_responses,
            severity='medium',
            notification_channels=['slack'],
            cooldown_minutes=15
        ),
    ]


# Notification handlers

async def slack_notification_handler(alert: Dict[str, Any]):
    """Send alert to Slack."""
    import aiohttp
    
    webhook_url = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    
    color_map = {
        'critical': '#FF0000',
        'high': '#FF8C00',
        'medium': '#FFD700',
        'low': '#00FF00'
    }
    
    payload = {
        'attachments': [{
            'color': color_map.get(alert['severity'], '#808080'),
            'title': f"Alert: {alert['rule_name']}",
            'text': f"Severity: {alert['severity']}",
            'fields': [
                {
                    'title': 'Timestamp',
                    'value': alert['timestamp'],
                    'short': True
                },
                {
                    'title': 'Details',
                    'value': json.dumps(alert['data'], indent=2)[:500],
                    'short': False
                }
            ],
            'footer': 'ResilienceAI Monitoring',
            'ts': int(datetime.utcnow().timestamp())
        }]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload) as response:
            if response.status != 200:
                logger.error(f'Failed to send Slack notification: {response.status}')


async def pagerduty_notification_handler(alert: Dict[str, Any]):
    """Send alert to PagerDuty."""
    import aiohttp
    
    api_key = 'YOUR_PAGERDUTY_API_KEY'
    service_key = 'YOUR_SERVICE_KEY'
    
    severity_map = {
        'critical': 'critical',
        'high': 'error',
        'medium': 'warning',
        'low': 'info'
    }
    
    payload = {
        'routing_key': service_key,
        'event_action': 'trigger',
        'dedup_key': alert['rule_name'],
        'payload': {
            'summary': f"ResilienceAI Alert: {alert['rule_name']}",
            'severity': severity_map.get(alert['severity'], 'warning'),
            'source': 'resilienceai-monitoring',
            'custom_details': alert['data']
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://events.pagerduty.com/v2/enqueue',
            json=payload,
            headers={'Authorization': f'Token token={api_key}'}
        ) as response:
            if response.status != 202:
                logger.error(f'Failed to send PagerDuty notification: {response.status}')


---

## 12. Monitoring Setup

### 12.1 Grafana Dashboards

**File:** `/app/logging/grafana/dashboard.json`

```json
{
  "dashboard": {
    "id": null,
    "title": "ResilienceAI - Logging & Observability",
    "tags": ["logging", "observability", "resilienceai"],
    "timezone": "utc",
    "schemaVersion": 36,
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "title": "Log Volume",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(resilienceai_logs_total[5m])) by (level)",
            "legendFormat": "{{level}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Error Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(resilienceai_logs_total{level=~\"ERROR|CRITICAL\"}[5m])) / sum(rate(resilienceai_logs_total[5m])) * 100",
            "legendFormat": "Error %"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 5},
                {"color": "red", "value": 10}
              ]
            },
            "unit": "percent"
          }
        }
      },
      {
        "id": 3,
        "title": "Request Latency (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(resilienceai_http_request_duration_seconds_bucket[5m])) by (le, endpoint))",
            "legendFormat": "{{endpoint}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Active Traces",
        "type": "stat",
        "targets": [
          {
            "expr": "jaeger_traces_received_total",
            "legendFormat": "Traces"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 4}
      },
      {
        "id": 5,
        "title": "Top Error Types",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, sum by (error_type) (resilienceai_errors_total))",
            "format": "table"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      },
      {
        "id": 6,
        "title": "Security Events",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(resilienceai_security_events_total[5m])) by (event_type)",
            "legendFormat": "{{event_type}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
      },
      {
        "id": 7,
        "title": "Log Retention Status",
        "type": "table",
        "targets": [
          {
            "expr": "elasticsearch_indices_store_size_bytes / 1024 / 1024 / 1024",
            "legendFormat": "{{index}}",
            "format": "table"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
      },
      {
        "id": 8,
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"resilienceai-.*\"}",
            "legendFormat": "{{job}}"
          }
        ],
        "gridPos": {"h": 4, "w": 24, "x": 0, "y": 24},
        "fieldConfig": {
          "defaults": {
            "mappings": [
              {"options": {"0": {"text": "Down"}}, "type": "value"},
              {"options": {"1": {"text": "Up"}}, "type": "value"}
            ],
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      }
    ]
  }
}
```

### 12.2 Prometheus Rules

**File:** `/app/logging/prometheus/alerts.yml`

```yaml
groups:
  - name: resilienceai-logging
    interval: 30s
    rules:
      # High error rate alert
      - alert: HighErrorRate
        expr: |
          sum(rate(resilienceai_logs_total{level=~"ERROR|CRITICAL"}[5m])) 
          / 
          sum(rate(resilienceai_logs_total[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} over the last 5 minutes"

      # Critical log spike
      - alert: CriticalLogSpike
        expr: |
          sum(rate(resilienceai_logs_total{level="CRITICAL"}[5m])) > 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Critical log spike detected"
          description: "{{ $value }} critical logs per second"

      # Slow requests
      - alert: SlowRequests
        expr: |
          histogram_quantile(0.95, 
            sum(rate(resilienceai_http_request_duration_seconds_bucket[5m])) by (le)
          ) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow requests detected"
          description: "p95 latency is {{ $value }}s"

      # Missing logs
      - alert: NoLogsReceived
        expr: |
          sum(rate(resilienceai_logs_total[5m])) == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "No logs being received"
          description: "Log stream has stopped"

      # Security event spike
      - alert: SecurityEventSpike
        expr: |
          sum(rate(resilienceai_security_events_total[5m])) > 50
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Security event spike detected"
          description: "{{ $value }} security events per second"

      # Logstash lag
      - alert: LogstashProcessingLag
        expr: |
          logstash_pipeline_events_out < logstash_pipeline_events_in
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Logstash processing lag"
          description: "Events are accumulating in Logstash"

      # Elasticsearch disk usage
      - alert: ElasticsearchDiskHigh
        expr: |
          elasticsearch_filesystem_data_available_bytes / elasticsearch_filesystem_data_size_bytes < 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Elasticsearch disk usage high"
          description: "Disk usage is above 80%"

      # Jaeger trace drops
      - alert: JaegerTraceDrops
        expr: |
          rate(jaeger_dropped_spans_total[5m]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Jaeger dropping traces"
          description: "Traces are being dropped due to capacity"
```

---

## 13. Deployment Guide

### 13.1 Kubernetes Deployment

**File:** `/app/logging/k8s/logging-stack.yaml`

```yaml
# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: logging
  labels:
    name: logging

---
# Elasticsearch StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch-logging
  namespace: logging
spec:
  serviceName: elasticsearch-logging
  replicas: 3
  selector:
    matchLabels:
      app: elasticsearch-logging
  template:
    metadata:
      labels:
        app: elasticsearch-logging
    spec:
      containers:
        - name: elasticsearch
          image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
          resources:
            requests:
              memory: "4Gi"
              cpu: "1000m"
            limits:
              memory: "8Gi"
              cpu: "2000m"
          ports:
            - containerPort: 9200
              name: http
            - containerPort: 9300
              name: transport
          env:
            - name: cluster.name
              value: resilienceai-logging
            - name: node.name
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: discovery.seed_hosts
              value: "elasticsearch-logging-0.elasticsearch-logging,elasticsearch-logging-1.elasticsearch-logging,elasticsearch-logging-2.elasticsearch-logging"
            - name: cluster.initial_master_nodes
              value: "elasticsearch-logging-0,elasticsearch-logging-1,elasticsearch-logging-2"
            - name: ES_JAVA_OPTS
              value: "-Xms2g -Xmx2g"
            - name: xpack.security.enabled
              value: "false"
          volumeMounts:
            - name: elasticsearch-data
              mountPath: /usr/share/elasticsearch/data
  volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 500Gi

---
# Elasticsearch Service
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch-logging
  namespace: logging
spec:
  selector:
    app: elasticsearch-logging
  ports:
    - port: 9200
      name: http
    - port: 9300
      name: transport
  clusterIP: None

---
# Kibana Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kibana-logging
  namespace: logging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: kibana-logging
  template:
    metadata:
      labels:
        app: kibana-logging
    spec:
      containers:
        - name: kibana
          image: docker.elastic.co/kibana/kibana:8.11.0
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          ports:
            - containerPort: 5601
          env:
            - name: ELASTICSEARCH_HOSTS
              value: "http://elasticsearch-logging:9200"
            - name: SERVER_NAME
              value: "kibana.logging.svc.cluster.local"

---
# Kibana Service
apiVersion: v1
kind: Service
metadata:
  name: kibana-logging
  namespace: logging
spec:
  selector:
    app: kibana-logging
  ports:
    - port: 5601
      targetPort: 5601
  type: ClusterIP

---
# Fluentd DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-logging
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluentd-logging
  template:
    metadata:
      labels:
        app: fluentd-logging
    spec:
      serviceAccountName: fluentd
      containers:
        - name: fluentd
          image: fluent/fluentd-kubernetes-daemonset:v1.16-debian-elasticsearch8-1
          resources:
            requests:
              memory: "512Mi"
              cpu: "200m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          volumeMounts:
            - name: varlog
              mountPath: /var/log
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
            - name: fluentd-config
              mountPath: /fluentd/etc
          env:
            - name: FLUENT_ELASTICSEARCH_HOST
              value: "elasticsearch-logging"
            - name: FLUENT_ELASTICSEARCH_PORT
              value: "9200"
            - name: ENVIRONMENT
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
      volumes:
        - name: varlog
          hostPath:
            path: /var/log
        - name: varlibdockercontainers
          hostPath:
            path: /var/lib/docker/containers
        - name: fluentd-config
          configMap:
            name: fluentd-config

---
# Fluentd ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluentd
  namespace: logging

---
# Fluentd ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fluentd
rules:
  - apiGroups: [""]
    resources:
      - pods
      - namespaces
    verbs:
      - get
      - list
      - watch

---
# Fluentd ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: fluentd
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: fluentd
subjects:
  - kind: ServiceAccount
    name: fluentd
    namespace: logging

---
# Jaeger Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one:1.50
          resources:
            requests:
              memory: "2Gi"
              cpu: "500m"
            limits:
              memory: "4Gi"
              cpu: "1000m"
          ports:
            - containerPort: 16686
              name: ui
            - containerPort: 14268
              name: collector
            - containerPort: 14250
              name: grpc
          env:
            - name: COLLECTOR_OTLP_ENABLED
              value: "true"

---
# Jaeger Service
apiVersion: v1
kind: Service
metadata:
  name: jaeger
  namespace: logging
spec:
  selector:
    app: jaeger
  ports:
    - port: 16686
      name: ui
    - port: 14268
      name: collector
    - port: 14250
      name: grpc

---
# Prometheus Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:v2.48.0
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: prometheus-config
              mountPath: /etc/prometheus
            - name: prometheus-storage
              mountPath: /prometheus
      volumes:
        - name: prometheus-config
          configMap:
            name: prometheus-config
        - name: prometheus-storage
          emptyDir: {}

---
# Prometheus Service
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: logging
spec:
  selector:
    app: prometheus
  ports:
    - port: 9090

---
# Grafana Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
        - name: grafana
          image: grafana/grafana:10.2.0
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "200m"
          ports:
            - containerPort: 3000
          env:
            - name: GF_SECURITY_ADMIN_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: grafana-credentials
                  key: admin-password
          volumeMounts:
            - name: grafana-datasources
              mountPath: /etc/grafana/provisioning/datasources
            - name: grafana-dashboards
              mountPath: /etc/grafana/provisioning/dashboards
      volumes:
        - name: grafana-datasources
          configMap:
            name: grafana-datasources
        - name: grafana-dashboards
          configMap:
            name: grafana-dashboards

---
# Grafana Service
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: logging
spec:
  selector:
    app: grafana
  ports:
    - port: 3000
```

### 13.2 Docker Compose for Local Development

**File:** `/app/logging/docker-compose.logging.yml`

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: resilienceai-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - logging

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: resilienceai-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - logging

  fluentd:
    build:
      context: ./fluentd
      dockerfile: Dockerfile
    container_name: resilienceai-fluentd
    ports:
      - "24224:24224"
      - "24224:24224/udp"
      - "9880:9880"
    volumes:
      - ./fluentd/conf:/fluentd/etc
      - /var/log:/var/log:ro
    depends_on:
      - elasticsearch
    networks:
      - logging

  jaeger:
    image: jaegertracing/all-in-one:1.50
    container_name: resilienceai-jaeger
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
    networks:
      - logging

  prometheus:
    image: prom/prometheus:v2.48.0
    container_name: resilienceai-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml
      - prometheus-data:/prometheus
    networks:
      - logging

  grafana:
    image: grafana/grafana:10.2.0
    container_name: resilienceai-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
      - elasticsearch
    networks:
      - logging

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: resilienceai-kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper
    networks:
      - logging

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: resilienceai-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    networks:
      - logging

volumes:
  elasticsearch-data:
  prometheus-data:
  grafana-data:

networks:
  logging:
    driver: bridge
```

---

## 14. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 1 | Structured logging setup | 2 days | Critical |
| 2 | Correlation ID middleware | 1 day | Critical |
| 3 | Basic log aggregation (ELK) | 3 days | High |
| 4 | Log levels and categories | 1 day | Medium |
| 5 | Error logging framework | 2 days | Critical |

**Deliverables:**
- JSON structured logs from all services
- Correlation IDs propagated across requests
- Logs visible in Kibana
- Basic error tracking

### Phase 2: Observability (Weeks 3-4)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 6 | Distributed tracing (Jaeger) | 3 days | High |
| 7 | Performance logging | 2 days | High |
| 8 | Security logging | 2 days | Critical |
| 9 | Prometheus metrics | 2 days | High |
| 10 | Grafana dashboards | 2 days | Medium |

**Deliverables:**
- Request traces across services
- Performance metrics and alerts
- Security event logging
- Real-time dashboards

### Phase 3: Advanced Features (Weeks 5-6)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 11 | Log analysis and patterns | 3 days | Medium |
| 12 | Anomaly detection | 3 days | Medium |
| 13 | Alert management | 2 days | High |
| 14 | Log retention policies | 2 days | Medium |
| 15 | Log archival to S3 | 2 days | Low |

**Deliverables:**
- Automated pattern detection
- Proactive alerting
- Cost-effective log storage
- Compliance-ready audit logs

### Phase 4: Optimization (Weeks 7-8)

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 16 | Async logging optimization | 2 days | Medium |
| 17 | Log sampling for high volume | 2 days | Medium |
| 18 | Custom span processors | 2 days | Low |
| 19 | Advanced Kibana visualizations | 2 days | Low |
| 20 | Documentation and runbooks | 3 days | Medium |

**Deliverables:**
- Optimized logging performance
- Reduced log volume costs
- Comprehensive documentation

---

## 15. Quick Start Guide

### 15.1 Service Integration

**File:** `/app/logging/integration.py`

```python
"""
Quick integration guide for ResilienceAI services.
"""

from fastapi import FastAPI

from .logger_config import configure_logging
from .correlation_middleware import CorrelationIdMiddleware, TimingMiddleware
from .error_handler import register_exception_handlers
from .tracing import configure_tracing, TracingConfig, instrument_fastapi
from .performance import PrometheusMetrics


def setup_logging_for_service(
    app: FastAPI,
    service_name: str,
    environment: str = 'development'
):
    """
    Complete logging setup for a ResilienceAI service.
    
    Usage:
        from fastapi import FastAPI
        from logging.integration import setup_logging_for_service
        
        app = FastAPI()
        setup_logging_for_service(app, 'resilience-engine', 'production')
    """
    # 1. Configure structured logging
    configure_logging(
        service_name=service_name,
        environment=environment,
        log_level='INFO',
        json_output=(environment != 'development')
    )
    
    # 2. Add correlation ID middleware
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(TimingMiddleware)
    
    # 3. Register exception handlers
    register_exception_handlers(app)
    
    # 4. Configure distributed tracing (if not development)
    if environment != 'development':
        tracing_config = TracingConfig(
            service_name=service_name,
            environment=environment,
            jaeger_host='jaeger-agent.logging.svc.cluster.local',
            sample_rate=0.1 if environment == 'production' else 1.0
        )
        configure_tracing(tracing_config)
        instrument_fastapi(app)
    
    # 5. Set Prometheus service info
    PrometheusMetrics.set_service_info(
        name=service_name,
        version='1.0.0',
        environment=environment
    )
    
    # 6. Add metrics endpoint
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    app.mount('/metrics', metrics_app)
    
    return app


# Example usage in a service
"""
# main.py
from fastapi import FastAPI
from logging.integration import setup_logging_for_service

app = FastAPI(title="Resilience Engine Service")

# Setup logging
setup_logging_for_service(
    app=app,
    service_name='resilience-engine',
    environment='production'
)

@app.get('/health')
async def health():
    return {'status': 'healthy'}

@app.get('/analyze/{organization_id}')
async def analyze_resilience(organization_id: str):
    # Your business logic here
    # Logging is automatic via middleware
    return {'organization_id': organization_id, 'resilience_score': 85}
"""
```

---

## 16. Summary

This comprehensive logging and observability design for ResilienceAI provides:

### Key Features
1. **Structured JSON Logging** - Machine-parseable logs with consistent schema
2. **Correlation IDs** - Request tracking across distributed services
3. **Distributed Tracing** - End-to-end request visibility with Jaeger/OpenTelemetry
4. **Log Aggregation** - ELK stack with Fluentd for centralized log management
5. **Performance Monitoring** - Metrics, timing, and resource usage tracking
6. **Error Handling** - Comprehensive error logging with categorization
7. **Security Logging** - Audit trails and security event tracking
8. **Log Retention** - Tiered storage with automated lifecycle management
9. **Analysis & Alerting** - Pattern detection and proactive monitoring

### Architecture Benefits
- **Debuggability**: Full request context across services
- **Performance**: Async logging and efficient log aggregation
- **Security**: Comprehensive audit trails and security monitoring
- **Compliance**: Configurable retention policies and archival
- **Scalability**: Distributed architecture with buffering
- **Cost-Effectiveness**: Tiered storage and log sampling

### Integration Points
- FastAPI middleware for automatic instrumentation
- Prometheus metrics for monitoring
- OpenTelemetry for distributed tracing
- Kubernetes-native deployment
- Cloud storage integration for archival

---

## Appendix A: File Structure

```
/app/logging/
├── __init__.py
├── logger_config.py          # Core logging configuration
├── async_logger.py           # Async logging implementation
├── log_levels.py             # Log level definitions
├── category_logger.py        # Category-based logging
├── correlation_middleware.py # Correlation ID middleware
├── context_propagation.py    # Context preservation
├── tracing.py                # OpenTelemetry tracing
├── span_processors.py        # Custom span processors
├── performance.py            # Performance logging
├── error_handler.py          # Error logging
├── security.py               # Security logging
├── retention.py              # Log retention policies
├── analysis.py               # Log analysis
├── integration.py            # Quick integration guide
├── fluentd/
│   ├── fluent.conf           # Fluentd configuration
│   └── Dockerfile
├── elasticsearch/
│   ├── template.json         # Index template
│   └── ilm_policy.json       # Lifecycle policy
├── logstash/
│   └── pipeline.conf         # Logstash pipeline
├── grafana/
│   ├── dashboard.json        # Dashboard definition
│   └── datasources.yml       # Data sources
├── prometheus/
│   ├── prometheus.yml        # Prometheus config
│   └── alerts.yml            # Alert rules
└── k8s/
    └── logging-stack.yaml    # Kubernetes manifests
```

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Engineering Team*
