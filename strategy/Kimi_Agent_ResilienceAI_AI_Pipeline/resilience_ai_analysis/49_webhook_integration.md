# ResilienceAI Webhook Integration System

## Executive Summary

This document provides a comprehensive design for the ResilienceAI webhook integration system, enabling real-time event notifications to external systems. The system supports event subscriptions, secure payload delivery, intelligent retry mechanisms, delivery tracking, and batch processing capabilities.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Webhook Endpoint Design](#webhook-endpoint-design)
3. [Event Subscription Management](#event-subscription-management)
4. [Payload Signing & Verification](#payload-signing--verification)
5. [Retry Mechanisms](#retry-mechanisms)
6. [Delivery Tracking](#delivery-tracking)
7. [Security Considerations](#security-considerations)
8. [Idempotency Handling](#idempotency-handling)
9. [Batch Webhooks](#batch-webhooks)
10. [Custom Webhook Templates](#custom-webhook-templates)
11. [External System Integrations](#external-system-integrations)
12. [Testing Approach](#testing-approach)
13. [Integration Guide](#integration-guide)
14. [Implementation Priority](#implementation-priority)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ResilienceAI Webhook System                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Event      │───▶│   Webhook    │───▶│   Delivery   │                  │
│  │   Source     │    │   Router     │    │   Queue      │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                   │                          │
│         ▼                   ▼                   ▼                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │ Subscription │    │   Payload    │    │   Retry      │                  │
│  │   Manager    │    │   Signer     │    │   Handler    │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                   │                          │
│         ▼                   ▼                   ▼                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Template   │    │  Idempotency │    │   Delivery   │                  │
│  │   Engine     │    │   Store      │    │   Tracker    │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         External Subscriber Endpoints                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  CRM     │  │  Slack   │  │  Email   │  │  Custom  │  │  SIEM    │      │
│  │ Systems  │  │  Teams   │  │ Service  │  │  Apps    │  │  Tools   │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Event Flow

```
1. Event Generated → 2. Filter Subscriptions → 3. Apply Templates
        ↓
4. Sign Payload → 5. Queue Delivery → 6. HTTP POST
        ↓
7. Track Response → 8. Retry if Needed → 9. Update Status
```

---

## Webhook Endpoint Design

### Core Endpoints

#### 1. Webhook Management API

```python
# /app/api/webhooks.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])
security = HTTPBearer()

class WebhookEventType(str, Enum):
    """Supported webhook event types for ResilienceAI"""
    # Risk Events
    RISK_CREATED = "risk.created"
    RISK_UPDATED = "risk.updated"
    RISK_DELETED = "risk.deleted"
    RISK_STATUS_CHANGED = "risk.status_changed"
    RISK_ESCALATED = "risk.escalated"
    
    # Incident Events
    INCIDENT_CREATED = "incident.created"
    INCIDENT_UPDATED = "incident.updated"
    INCIDENT_RESOLVED = "incident.resolved"
    INCIDENT_ASSIGNED = "incident.assigned"
    
    # Assessment Events
    ASSESSMENT_STARTED = "assessment.started"
    ASSESSMENT_COMPLETED = "assessment.completed"
    ASSESSMENT_FINDING = "assessment.finding"
    
    # Compliance Events
    COMPLIANCE_VIOLATION = "compliance.violation"
    COMPLIANCE_REMEDIATION = "compliance.remediation"
    AUDIT_LOG_CREATED = "audit_log.created"
    
    # Workflow Events
    WORKFLOW_TRIGGERED = "workflow.triggered"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    
    # System Events
    SYSTEM_ALERT = "system.alert"
    SYSTEM_MAINTENANCE = "system.maintenance"
    USER_ACTION = "user.action"

class WebhookStatus(str, Enum):
    """Webhook subscription status"""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    FAILED = "failed"

class WebhookConfig(BaseModel):
    """Webhook configuration model"""
    url: HttpUrl = Field(..., description="Target URL for webhook delivery")
    events: List[WebhookEventType] = Field(..., description="Events to subscribe to")
    secret: Optional[str] = Field(None, description="Secret for HMAC signature")
    description: Optional[str] = Field(None, max_length=500)
    
    # Delivery configuration
    retry_policy: Dict[str, Any] = Field(
        default_factory=lambda: {
            "max_retries": 3,
            "initial_delay": 5,
            "max_delay": 300,
            "backoff_multiplier": 2.0
        }
    )
    
    # Filtering
    filters: Optional[Dict[str, Any]] = Field(None, description="Event filtering rules")
    
    # Batch configuration
    batch_config: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "enabled": False,
            "max_size": 100,
            "max_wait_seconds": 30
        }
    )
    
    # Custom headers
    custom_headers: Optional[Dict[str, str]] = Field(None)
    
    # Timeout configuration
    timeout_seconds: int = Field(default=30, ge=5, le=300)

class WebhookResponse(BaseModel):
    """Webhook subscription response"""
    id: str
    url: HttpUrl
    events: List[WebhookEventType]
    status: WebhookStatus
    created_at: datetime
    updated_at: datetime
    last_delivery_at: Optional[datetime] = None
    delivery_count: int = 0
    failure_count: int = 0

class WebhookDelivery(BaseModel):
    """Webhook delivery record"""
    id: str
    webhook_id: str
    event_type: WebhookEventType
    event_id: str
    status: Literal["pending", "delivered", "failed", "retrying"]
    http_status: Optional[int] = None
    response_body: Optional[str] = None
    attempt_count: int = 0
    next_retry_at: Optional[datetime] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
```

#### 2. Webhook Registration Endpoint

```python
@router.post("/subscriptions", response_model=WebhookResponse)
async def create_webhook_subscription(
    config: WebhookConfig,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new webhook subscription."""
    # Validate URL accessibility
    validator = WebhookValidator()
    validation_result = await validator.validate_endpoint(str(config.url))
    
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid webhook URL: {validation_result.error_message}"
        )
    
    # Generate webhook ID and secret if not provided
    webhook_id = f"wh_{uuid.uuid4().hex[:16]}"
    secret = config.secret or generate_webhook_secret()
    
    # Create webhook record
    webhook = WebhookSubscription(
        id=webhook_id,
        tenant_id=current_user["tenant_id"],
        created_by=current_user["id"],
        url=str(config.url),
        events=[e.value for e in config.events],
        secret=secret,
        description=config.description,
        retry_policy=config.retry_policy,
        filters=config.filters,
        batch_config=config.batch_config,
        custom_headers=config.custom_headers,
        timeout_seconds=config.timeout_seconds,
        status=WebhookStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(webhook)
    await db.commit()
    
    # Send verification webhook in background
    background_tasks.add_task(
        send_verification_webhook,
        webhook_id=webhook_id,
        url=str(config.url),
        secret=secret
    )
    
    return WebhookResponse(
        id=webhook_id,
        url=config.url,
        events=config.events,
        status=WebhookStatus.ACTIVE,
        created_at=webhook.created_at,
        updated_at=webhook.updated_at
    )
```

---

## Payload Signing & Verification

### HMAC Signature Implementation

```python
# /app/services/webhook/signature.py
import hmac
import hashlib
import base64
import json
from typing import Dict, Any, Optional
from datetime import datetime

class WebhookSignature:
    """HMAC signature generation and verification for webhooks"""
    
    SIGNATURE_VERSION = "v1"
    SIGNATURE_ALGORITHM = "sha256"
    
    @classmethod
    def generate_signature(
        cls,
        payload: Dict[str, Any],
        secret: str,
        timestamp: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate HMAC signature for webhook payload."""
        timestamp = timestamp or str(int(datetime.utcnow().timestamp()))
        
        # Create signed payload
        payload_bytes = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
        signed_payload = f"{timestamp}.{payload_bytes.decode('utf-8')}"
        
        # Generate HMAC
        signature = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "X-Webhook-Signature": f"{cls.SIGNATURE_VERSION}={signature}",
            "X-Webhook-Timestamp": timestamp,
            "X-Webhook-Version": cls.SIGNATURE_VERSION
        }
    
    @classmethod
    def verify_signature(
        cls,
        payload: bytes,
        signature_header: str,
        secret: str,
        timestamp_header: str,
        max_age_seconds: int = 300
    ) -> bool:
        """Verify webhook signature."""
        try:
            # Verify timestamp to prevent replay attacks
            timestamp = int(timestamp_header)
            current_time = int(datetime.utcnow().timestamp())
            
            if abs(current_time - timestamp) > max_age_seconds:
                return False
            
            # Extract version and signature
            if "=" not in signature_header:
                return False
            
            version, received_sig = signature_header.split("=", 1)
            
            if version != cls.SIGNATURE_VERSION:
                return False
            
            # Recreate signed payload
            signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
            
            # Compute expected signature
            expected_sig = hmac.new(
                secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Constant-time comparison to prevent timing attacks
            return hmac.compare_digest(received_sig, expected_sig)
            
        except (ValueError, TypeError, UnicodeDecodeError):
            return False
```

---

## Retry Mechanisms

### Exponential Backoff Retry

```python
# /app/services/webhook/retry_handler.py
import asyncio
from typing import Optional, Callable
from datetime import datetime, timedelta
import random

class RetryPolicy:
    """Configurable retry policy for webhook deliveries"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 5.0,
        max_delay: float = 300.0,
        backoff_multiplier: float = 2.0,
        retryable_status_codes: list = None,
        retryable_exceptions: tuple = None
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.retryable_status_codes = retryable_status_codes or [408, 429, 500, 502, 503, 504]
        self.retryable_exceptions = retryable_exceptions or (
            asyncio.TimeoutError,
            ConnectionError,
            ConnectionRefusedError,
            ConnectionResetError
        )
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter"""
        # Exponential backoff
        delay = self.initial_delay * (self.backoff_multiplier ** attempt)
        
        # Cap at max delay
        delay = min(delay, self.max_delay)
        
        # Add jitter (+/-25%) to prevent thundering herd
        jitter = delay * 0.25
        delay = delay + random.uniform(-jitter, jitter)
        
        return max(0, delay)
    
    def should_retry(self, attempt: int, exception: Optional[Exception] = None, 
                     status_code: Optional[int] = None) -> bool:
        """Determine if delivery should be retried"""
        if attempt >= self.max_retries:
            return False
        
        if status_code is not None:
            return status_code in self.retryable_status_codes
        
        if exception is not None:
            return isinstance(exception, self.retryable_exceptions)
        
        return True
```

---

## Security Considerations

### Comprehensive Security Implementation

```python
# /app/services/webhook/security.py
from fastapi import HTTPException, Request
from typing import Optional, List, Set
import ipaddress
import re

class WebhookSecurity:
    """Security controls for webhook system"""
    
    # Blocked URL patterns (SSRF protection)
    BLOCKED_HOSTS = {
        "localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]",
    }
    
    BLOCKED_IP_RANGES = [
        ipaddress.ip_network("10.0.0.0/8"),      # Private
        ipaddress.ip_network("172.16.0.0/12"),   # Private
        ipaddress.ip_network("192.168.0.0/16"),  # Private
        ipaddress.ip_network("169.254.0.0/16"),  # Link-local
        ipaddress.ip_network("127.0.0.0/8"),     # Loopback
        ipaddress.ip_network("fc00::/7"),        # IPv6 private
        ipaddress.ip_network("fe80::/10"),       # IPv6 link-local
    ]
    
    # Allowed protocols
    ALLOWED_PROTOCOLS = {"https"}
    
    URL_PATTERN = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, Optional[str]]:
        """Validate webhook URL for security."""
        # Basic format validation
        if not cls.URL_PATTERN.match(url):
            return False, "Invalid URL format"
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            
            # Protocol check
            if parsed.scheme not in cls.ALLOWED_PROTOCOLS:
                return False, f"Protocol '{parsed.scheme}' not allowed. Use HTTPS only."
            
            # Host check
            hostname = parsed.hostname
            if not hostname:
                return False, "Invalid hostname"
            
            # Check blocked hosts
            if hostname.lower() in cls.BLOCKED_HOSTS:
                return False, "Blocked hostname"
            
            # Check if hostname is IP address
            try:
                ip = ipaddress.ip_address(hostname)
                for network in cls.BLOCKED_IP_RANGES:
                    if ip in network:
                        return False, "Blocked IP range"
            except ValueError:
                pass
            
            # Port check
            if parsed.port:
                if parsed.port < 1 or parsed.port > 65535:
                    return False, "Invalid port number"
                if parsed.port in [22, 23, 25, 53, 110, 143, 3306, 5432, 6379, 9200]:
                    return False, "Port not allowed"
            
            return True, None
            
        except Exception as e:
            return False, f"URL validation error: {str(e)}"
```

---

## Idempotency Handling

### Idempotency Implementation

```python
# /app/services/webhook/idempotency.py
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import json

class IdempotencyManager:
    """Manage idempotency for webhook deliveries"""
    
    def __init__(self, redis: Redis, key_prefix: str = "idempotency"):
        self.redis = redis
        self.key_prefix = key_prefix
        self.default_ttl = 86400  # 24 hours
    
    def generate_key(
        self,
        webhook_id: str,
        event_id: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate idempotency key for a delivery."""
        key_data = f"{webhook_id}:{event_id}"
        
        # Optionally include payload hash for stricter deduplication
        if payload:
            payload_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode()
            ).hexdigest()[:16]
            key_data = f"{key_data}:{payload_hash}"
        
        return f"{self.key_prefix}:{key_data}"
    
    async def check_idempotency(
        self,
        webhook_id: str,
        event_id: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[Dict[str, Any]]]:
        """Check if delivery has already been processed."""
        key = self.generate_key(webhook_id, event_id, payload)
        
        cached = await self.redis.get(key)
        
        if cached:
            result = json.loads(cached)
            return True, result
        
        return False, None
    
    async def store_result(
        self,
        webhook_id: str,
        event_id: str,
        result: Dict[str, Any],
        payload: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None
    ):
        """Store delivery result for idempotency"""
        key = self.generate_key(webhook_id, event_id, payload)
        ttl = ttl_seconds or self.default_ttl
        
        result_with_timestamp = {
            **result,
            "stored_at": datetime.utcnow().isoformat()
        }
        
        await self.redis.setex(key, ttl, json.dumps(result_with_timestamp))
```

---

## Batch Webhooks

### Batch Processing System

```python
# /app/services/webhook/batch_processor.py
from typing import List, Dict, Any
from datetime import datetime, timedelta
import asyncio

class BatchConfig:
    """Configuration for batch webhook processing"""
    
    def __init__(
        self,
        max_size: int = 100,
        max_wait_seconds: float = 30.0,
        flush_on_shutdown: bool = True
    ):
        self.max_size = max_size
        self.max_wait_seconds = max_wait_seconds
        self.flush_on_shutdown = flush_on_shutdown

class BatchWebhookProcessor:
    """Process webhooks in batches for efficiency"""
    
    def __init__(
        self,
        delivery_service: WebhookDeliveryService,
        redis: Redis,
        metrics: MetricsCollector
    ):
        self.delivery_service = delivery_service
        self.redis = redis
        self.metrics = metrics
        
        # Batches in memory
        self._batches: Dict[str, List[Dict]] = {}
        self._batch_timers: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
    
    async def add_to_batch(self, webhook: WebhookSubscription, event: WebhookEvent):
        """Add event to batch for webhook"""
        batch_key = f"batch:{webhook.id}"
        config = BatchConfig(**(webhook.batch_config or {}))
        
        async with self._lock:
            # Initialize batch if needed
            if batch_key not in self._batches:
                self._batches[batch_key] = []
                
                # Start timer for max wait
                self._batch_timers[batch_key] = asyncio.create_task(
                    self._flush_after_delay(batch_key, config.max_wait_seconds)
                )
            
            # Add event to batch
            self._batches[batch_key].append({
                "event_id": event.id,
                "event_type": event.type,
                "timestamp": event.timestamp,
                "data": event.data
            })
            
            current_size = len(self._batches[batch_key])
            
            # Check if batch is full
            if current_size >= config.max_size:
                # Cancel timer and flush immediately
                if batch_key in self._batch_timers:
                    self._batch_timers[batch_key].cancel()
                    del self._batch_timers[batch_key]
                
                batch = self._batches.pop(batch_key)
                asyncio.create_task(self._flush_batch(webhook, batch))
```

---

## Custom Webhook Templates

### Template System

```python
# /app/services/webhook/templates.py
from typing import Dict, Any, Optional, Callable
from jinja2 import Template, Environment, BaseLoader
import json

class WebhookTemplate:
    """Customizable webhook payload template"""
    
    def __init__(
        self,
        template_id: str,
        name: str,
        event_types: List[str],
        payload_template: str,
        headers_template: Optional[Dict[str, str]] = None,
        content_type: str = "application/json"
    ):
        self.template_id = template_id
        self.name = name
        self.event_types = event_types
        self.payload_template = payload_template
        self.headers_template = headers_template or {}
        self.content_type = content_type
        
        # Compile template
        self._jinja_env = Environment(loader=BaseLoader())
        self._payload_template = self._jinja_env.from_string(payload_template)
        self._header_templates = {
            k: self._jinja_env.from_string(v)
            for k, v in self.headers_template.items()
        }
    
    def render(self, event: WebhookEvent, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Render template with event data."""
        template_context = {
            "event": {
                "id": event.id,
                "type": event.type,
                "timestamp": event.timestamp,
                "data": event.data
            },
            "context": context or {},
            "utils": {
                "to_json": json.dumps,
                "from_json": json.loads,
                "now": datetime.utcnow().isoformat
            }
        }
        
        # Render payload
        rendered_payload = self._payload_template.render(**template_context)
        
        # Parse based on content type
        if self.content_type == "application/json":
            payload = json.loads(rendered_payload)
        else:
            payload = rendered_payload
        
        # Render headers
        headers = {}
        for key, template in self._header_templates.items():
            headers[key] = template.render(**template_context)
        
        return {
            "payload": payload,
            "headers": headers,
            "content_type": self.content_type
        }
```

---

## External System Integrations

### Integration Adapters

```python
# /app/services/webhook/integrations.py
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class WebhookIntegration(ABC):
    """Base class for external system integrations"""
    
    @abstractmethod
    async def transform_payload(self, event: WebhookEvent, config: Dict[str, Any]) -> Dict[str, Any]:
        """Transform ResilienceAI event to external system format"""
        pass
    
    @abstractmethod
    async def handle_response(self, response: Any) -> Dict[str, Any]:
        """Handle response from external system"""
        pass
    
    @abstractmethod
    def get_auth_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Get authentication headers for external system"""
        pass


class SlackIntegration(WebhookIntegration):
    """Slack webhook integration"""
    
    async def transform_payload(self, event: WebhookEvent, config: Dict[str, Any]) -> Dict[str, Any]:
        """Transform event to Slack message format"""
        severity_colors = {
            "critical": "#FF0000",
            "high": "#FF8C00",
            "medium": "#FFD700",
            "low": "#00FF00",
            "info": "#808080"
        }
        
        color = severity_colors.get(event.data.get("severity", ""), "#0078D7")
        
        return {
            "attachments": [
                {
                    "color": color,
                    "title": event.data.get("title", "ResilienceAI Alert"),
                    "text": event.data.get("description", ""),
                    "fields": [
                        {"title": "Event Type", "value": event.type, "short": True},
                        {"title": "Severity", "value": event.data.get("severity", "Unknown"), "short": True}
                    ],
                    "footer": "ResilienceAI",
                    "ts": int(datetime.utcnow().timestamp())
                }
            ]
        }
    
    async def handle_response(self, response: Any) -> Dict[str, Any]:
        if response == "ok":
            return {"success": True}
        return {"success": False, "error": response}
    
    def get_auth_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        return {"Content-Type": "application/json"}


class PagerDutyIntegration(WebhookIntegration):
    """PagerDuty integration"""
    
    async def transform_payload(self, event: WebhookEvent, config: Dict[str, Any]) -> Dict[str, Any]:
        """Transform event to PagerDuty v2 event format"""
        severity_map = {
            "critical": "critical",
            "high": "error",
            "medium": "warning",
            "low": "info"
        }
        
        return {
            "routing_key": config.get("integration_key"),
            "event_action": "trigger",
            "dedup_key": event.data.get("id", event.id),
            "payload": {
                "summary": event.data.get("title", "ResilienceAI Alert"),
                "severity": severity_map.get(event.data.get("severity"), "warning"),
                "source": "ResilienceAI",
                "component": event.data.get("component", "risk-management"),
                "custom_details": event.data
            }
        }
    
    async def handle_response(self, response: Any) -> Dict[str, Any]:
        if response.status == 202:
            return {"success": True}
        return {"success": False, "error": f"HTTP {response.status}"}
    
    def get_auth_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Token token={config.get('api_token', '')}"
        }


class IntegrationRegistry:
    """Registry for webhook integrations"""
    
    INTEGRATIONS = {
        "slack": SlackIntegration,
        "teams": TeamsIntegration,
        "pagerduty": PagerDutyIntegration,
        "servicenow": ServiceNowIntegration,
        "jira": JiraIntegration
    }
    
    @classmethod
    def get_integration(cls, name: str) -> Optional[WebhookIntegration]:
        """Get integration by name"""
        integration_class = cls.INTEGRATIONS.get(name.lower())
        if integration_class:
            return integration_class()
        return None
```

---

## Testing Approach

### Webhook Testing Framework

```python
# /app/tests/webhook/test_webhooks.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import hmac
import hashlib
import json

class TestWebhookSignature:
    """Test webhook signature generation and verification"""
    
    def test_generate_signature(self):
        """Test HMAC signature generation"""
        payload = {"event": "test", "data": {"id": "123"}}
        secret = "test_secret"
        
        headers = WebhookSignature.generate_signature(payload, secret)
        
        assert "X-Webhook-Signature" in headers
        assert "X-Webhook-Timestamp" in headers
        assert headers["X-Webhook-Version"] == "v1"
    
    def test_verify_signature(self):
        """Test HMAC signature verification"""
        payload = {"event": "test", "data": {"id": "123"}}
        secret = "test_secret"
        timestamp = "1234567890"
        
        headers = WebhookSignature.generate_signature(payload, secret, timestamp)
        signature = headers["X-Webhook-Signature"]
        
        payload_bytes = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode()
        
        is_valid = WebhookSignature.verify_signature(
            payload_bytes, signature, secret, timestamp
        )
        
        assert is_valid is True
    
    def test_verify_signature_invalid_secret(self):
        """Test signature verification with wrong secret"""
        payload = {"event": "test"}
        secret = "correct_secret"
        wrong_secret = "wrong_secret"
        timestamp = "1234567890"
        
        headers = WebhookSignature.generate_signature(payload, secret, timestamp)
        
        payload_bytes = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode()
        
        is_valid = WebhookSignature.verify_signature(
            payload_bytes, headers["X-Webhook-Signature"], wrong_secret, timestamp
        )
        
        assert is_valid is False


class TestRetryMechanism:
    """Test retry mechanism"""
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        policy = RetryPolicy(
            initial_delay=5.0,
            backoff_multiplier=2.0,
            max_delay=300.0
        )
        
        # Test delay increases exponentially
        assert policy.calculate_delay(0) >= 3.75  # 5 * 0.75 (with jitter)
        assert policy.calculate_delay(1) >= 7.5   # 10 * 0.75
        assert policy.calculate_delay(2) >= 15    # 20 * 0.75
    
    @pytest.mark.asyncio
    async def test_should_retry_status_codes(self):
        """Test retry decision based on status codes"""
        policy = RetryPolicy(max_retries=3)
        
        # Should retry
        assert policy.should_retry(0, status_code=500) is True
        assert policy.should_retry(0, status_code=503) is True
        assert policy.should_retry(0, status_code=429) is True
        
        # Should not retry
        assert policy.should_retry(0, status_code=200) is False
        assert policy.should_retry(0, status_code=400) is False
        
        # Max retries exceeded
        assert policy.should_retry(3, status_code=500) is False
```

---

## Integration Guide

### Quick Start Guide

#### 1. Register a Webhook

```bash
# Create webhook subscription
curl -X POST https://api.resilienceai.io/api/v1/webhooks/subscriptions \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/resilience-ai",
    "events": ["risk.created", "incident.created"],
    "description": "Production webhook",
    "retry_policy": {
      "max_retries": 5,
      "initial_delay": 10
    }
  }'
```

#### 2. Verify Webhook Signature (Python)

```python
import hmac
import hashlib
import json
from flask import Flask, request

app = Flask(__name__)
WEBHOOK_SECRET = "your_webhook_secret"

@app.route('/webhooks/resilience-ai', methods=['POST'])
def handle_webhook():
    # Get headers
    signature = request.headers.get('X-Webhook-Signature')
    timestamp = request.headers.get('X-Webhook-Timestamp')
    
    # Verify signature
    payload = request.get_data()
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    
    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature.replace('v1=', ''), expected_sig):
        return 'Invalid signature', 401
    
    # Process event
    event = request.json
    print(f"Received event: {event['type']}")
    
    return 'OK', 200
```

#### 3. Verify Webhook Signature (Node.js)

```javascript
const crypto = require('crypto');
const express = require('express');
const app = express();

const WEBHOOK_SECRET = 'your_webhook_secret';

app.post('/webhooks/resilience-ai', express.json(), (req, res) => {
    const signature = req.headers['x-webhook-signature'];
    const timestamp = req.headers['x-webhook-timestamp'];
    
    // Verify signature
    const payload = JSON.stringify(req.body);
    const signedPayload = `${timestamp}.${payload}`;
    
    const expectedSig = crypto
        .createHmac('sha256', WEBHOOK_SECRET)
        .update(signedPayload)
        .digest('hex');
    
    if (signature !== `v1=${expectedSig}`) {
        return res.status(401).send('Invalid signature');
    }
    
    console.log(`Received event: ${req.body.type}`);
    res.send('OK');
});
```

### Event Types Reference

| Event Type | Description | Payload Example |
|------------|-------------|-----------------|
| `risk.created` | New risk identified | `{ "id": "risk_123", "title": "...", "severity": "high" }` |
| `risk.updated` | Risk modified | `{ "id": "risk_123", "changes": {...} }` |
| `risk.escalated` | Risk escalated | `{ "id": "risk_123", "previous_severity": "medium", "new_severity": "high" }` |
| `incident.created` | New incident | `{ "id": "inc_456", "title": "...", "severity": "critical" }` |
| `incident.resolved` | Incident resolved | `{ "id": "inc_456", "resolution": "..." }` |
| `assessment.completed` | Assessment finished | `{ "id": "asm_789", "findings": [...] }` |
| `compliance.violation` | Compliance issue | `{ "control_id": "...", "violation": "..." }` |

### Best Practices

1. **Always verify signatures** - Protect against spoofed requests
2. **Respond quickly** - Return 2xx within 30 seconds
3. **Handle retries** - Same event may be delivered multiple times
4. **Use idempotency** - Prevent duplicate processing
5. **Implement circuit breakers** - Fail fast on repeated errors
6. **Log deliveries** - Track and monitor webhook activity
7. **Test endpoints** - Use test events before production

---

## Implementation Priority

### Phase 1: Core Infrastructure (Weeks 1-2)
1. **Webhook endpoint design** - API routes and models
2. **Event subscription management** - Subscribe/unsubscribe
3. **Basic delivery service** - HTTP POST with timeout
4. **Database schema** - Subscriptions and delivery tracking

### Phase 2: Security & Reliability (Weeks 3-4)
1. **Payload signing** - HMAC-SHA256 implementation
2. **Retry mechanism** - Exponential backoff
3. **Delivery tracking** - Status and history
4. **URL validation** - SSRF protection

### Phase 3: Advanced Features (Weeks 5-6)
1. **Idempotency handling** - Duplicate prevention
2. **Batch webhooks** - Efficient bulk delivery
3. **Custom templates** - Integration formats
4. **Filtering engine** - Event routing rules

### Phase 4: Integrations & Monitoring (Weeks 7-8)
1. **External integrations** - Slack, Teams, PagerDuty
2. **Real-time monitoring** - Dashboard and alerts
3. **Analytics** - Delivery statistics
4. **Documentation** - Integration guides

---

## File Structure

```
/app
├── api/
│   └── webhooks.py              # Webhook API endpoints
├── services/
│   └── webhook/
│       ├── __init__.py
│       ├── subscription_manager.py
│       ├── event_router.py
│       ├── signature.py
│       ├── retry_handler.py
│       ├── delivery_tracker.py
│       ├── security.py
│       ├── idempotency.py
│       ├── batch_processor.py
│       ├── templates.py
│       └── integrations.py
├── models/
│   └── webhook.py               # Database models
├── tests/
│   └── webhook/
│       └── test_webhooks.py     # Test suite
└── workers/
    └── webhook_worker.py        # Background delivery worker
```

---

## Configuration

```yaml
# config/webhook.yaml
webhook:
  # Delivery settings
  default_timeout_seconds: 30
  max_payload_size_mb: 1
  
  # Retry settings
  retry:
    max_retries: 5
    initial_delay_seconds: 5
    max_delay_seconds: 300
    backoff_multiplier: 2.0
  
  # Batch settings
  batch:
    enabled: true
    max_size: 100
    max_wait_seconds: 30
  
  # Security settings
  security:
    allowed_protocols: ["https"]
    require_signature: true
    signature_ttl_seconds: 300
    rate_limit_per_minute: 100
  
  # Monitoring
  monitoring:
    enable_real_time: true
    alert_on_failure_rate: 0.1
    alert_on_latency_ms: 5000
```

---

## Summary

This comprehensive webhook integration system for ResilienceAI provides:

- **Secure delivery** with HMAC-SHA256 signature verification
- **Reliable delivery** with exponential backoff retry
- **Flexible subscriptions** with event filtering
- **Batch processing** for high-volume scenarios
- **Idempotency guarantees** to prevent duplicates
- **Rich integrations** with popular platforms
- **Comprehensive monitoring** and analytics
- **Production-ready** with circuit breakers and rate limiting

The system is designed to handle enterprise-scale webhook delivery while maintaining security, reliability, and observability.
