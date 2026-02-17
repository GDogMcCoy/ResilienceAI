# ResilienceAI Alert & Notification System Enhancement

## Executive Summary

This document provides a comprehensive analysis of the current ResilienceAI alert system and designs a production-ready, enterprise-grade alert and notification platform. The enhanced system will support multi-channel notifications, intelligent alert correlation, escalation procedures, and real-time streaming capabilities.

---

## 1. Current State Analysis

### 1.1 Existing Alert Manager (`src/alert_manager.py`)

The current implementation provides basic alert functionality:

**Strengths:**
- SQLite-based persistence for subscriptions and alert events
- Dataclass-based models for `AlertSubscription` and `AlertEvent`
- Thread-safe operations with locking
- Basic CRUD operations for subscriptions
- Alert triggering with severity levels
- Simple notification channel placeholders (webhook, email, SMS)

**Current Data Models:**
```python
@dataclass
class AlertSubscription:
    id: str
    county_fips: str
    county_name: str
    state: str
    threshold: float
    alert_types: List[str]
    webhook_url: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: str
    last_triggered: Optional[str]
    is_active: bool

@dataclass
class AlertEvent:
    id: str
    subscription_id: str
    county_fips: str
    alert_type: str
    severity: str
    message: str
    data: Dict[str, Any]
    triggered_at: str
    acknowledged_at: Optional[str]
    status: str  # 'active', 'acknowledged', 'resolved'
```

**Limitations:**
1. **No actual notification implementations** - Only mock logging for webhook/email/SMS
2. **Limited severity classification** - No standardized severity levels or color coding
3. **No alert correlation** - Each alert is independent; no grouping or deduplication
4. **No escalation procedures** - Alerts don't escalate if unacknowledged
5. **No notification templates** - All alerts use the same format
6. **No user preference management** - Limited customization options
7. **No real-time streaming** - No WebSocket or SSE support
8. **No alert history analytics** - Limited querying and reporting capabilities
9. **No rate limiting** - Potential for alert fatigue
10. **No geographic aggregation** - County-level only, no region/state grouping

---

## 2. Proposed Alert Management Platform

### 2.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ALERT MANAGEMENT PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │ Alert Ingest │───▶│  Correlation │───▶│   Dispatch   │                  │
│  │   Pipeline   │    │   Engine     │    │   Engine     │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                   │                          │
│         ▼                   ▼                   ▼                          │
│  ┌──────────────────────────────────────────────────────┐                 │
│  │              ALERT PROCESSING LAYER                   │                 │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │                 │
│  │  │ Severity   │  │ Duplicate  │  │  Template  │     │                 │
│  │  │Classifier  │  │ Detection  │  │  Engine    │     │                 │
│  │  └────────────┘  └────────────┘  └────────────┘     │                 │
│  └──────────────────────────────────────────────────────┘                 │
│                          │                                                  │
│                          ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐                 │
│  │           NOTIFICATION CHANNEL LAYER                  │                 │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │                 │
│  │  │ Email  │ │  SMS   │ │ Push   │ │Webhook │        │                 │
│  │  │Service │ │Service │ │Service │ │Service │        │                 │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │                 │
│  └──────────────────────────────────────────────────────┘                 │
│                          │                                                  │
│                          ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐                 │
│  │              ESCALATION & AUDIT LAYER                 │                 │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │                 │
│  │  │ Escalation │  │   Audit    │  │  History   │     │                 │
│  │  │  Engine    │  │   Logger   │  │   Store    │     │                 │
│  │  └────────────┘  └────────────┘  └────────────┘     │                 │
│  └──────────────────────────────────────────────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Enhanced Folder Structure

```
resilience_ai/
├── src/
│   ├── alerts/                          # NEW: Alert system package
│   │   ├── __init__.py
│   │   ├── core/                        # Core alert functionality
│   │   │   ├── __init__.py
│   │   │   ├── alert_manager.py         # Enhanced alert manager
│   │   │   ├── alert_models.py          # Data models
│   │   │   ├── severity_classifier.py   # Severity classification
│   │   │   └── correlation_engine.py    # Alert correlation & dedup
│   │   ├── channels/                    # Notification channels
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # Base channel interface
│   │   │   ├── email_channel.py         # Email notifications
│   │   │   ├── sms_channel.py           # SMS notifications
│   │   │   ├── push_channel.py          # Push notifications
│   │   │   ├── webhook_channel.py       # Webhook notifications
│   │   │   └── slack_channel.py         # Slack integration
│   │   ├── templates/                   # Notification templates
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # Template base class
│   │   │   ├── email_templates/         # Email-specific templates
│   │   │   ├── sms_templates/           # SMS-specific templates
│   │   │   └── push_templates/          # Push notification templates
│   │   ├── dispatch/                    # Alert dispatching
│   │   │   ├── __init__.py
│   │   │   ├── dispatch_engine.py       # Main dispatch logic
│   │   │   ├── rate_limiter.py          # Rate limiting
│   │   │   └── batch_processor.py       # Batch processing
│   │   ├── escalation/                  # Escalation procedures
│   │   │   ├── __init__.py
│   │   │   ├── escalation_engine.py     # Escalation logic
│   │   │   └── escalation_policies.py   # Policy definitions
│   │   ├── streaming/                   # Real-time streaming
│   │   │   ├── __init__.py
│   │   │   ├── websocket_server.py      # WebSocket server
│   │   │   ├── sse_handler.py           # Server-Sent Events
│   │   │   └── stream_manager.py        # Stream management
│   │   ├── preferences/                 # User preferences
│   │   │   ├── __init__.py
│   │   │   ├── preference_manager.py    # Preference management
│   │   │   └── notification_settings.py # Settings models
│   │   ├── audit/                       # Audit & history
│   │   │   ├── __init__.py
│   │   │   ├── audit_logger.py          # Audit logging
│   │   │   └── history_manager.py       # History management
│   │   └── api/                         # Alert API
│   │       ├── __init__.py
│   │       ├── rest_api.py              # REST endpoints
│   │       └── graphql_schema.py        # GraphQL schema
│   └── ...
├── config/
│   └── alert_config.py                  # Alert-specific configuration
├── templates/
│   └── alerts/                          # HTML/email templates
├── tests/
│   └── alerts/                          # Alert system tests
└── docs/
    └── alerts/                          # Alert system documentation
```

---

## 3. Enhanced Data Models

### 3.1 Core Alert Models

```python
# src/alerts/core/alert_models.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum, auto
import uuid
import json


class AlertSeverity(Enum):
    """Standardized alert severity levels"""
    CRITICAL = "critical"      # Red - Immediate action required
    HIGH = "high"              # Orange - Urgent attention needed
    MEDIUM = "medium"          # Yellow - Important, timely response
    LOW = "low"                # Blue - Informational, monitor
    INFO = "info"              # Green - General information


class AlertStatus(Enum):
    """Alert lifecycle statuses"""
    PENDING = "pending"           # Alert created, not yet dispatched
    DISPATCHED = "dispatched"     # Notification sent
    DELIVERED = "delivered"       # Notification confirmed delivered
    ACKNOWLEDGED = "acknowledged" # User acknowledged
    ESCALATED = "escalated"       # Escalated to next level
    RESOLVED = "resolved"         # Issue resolved
    SUPPRESSED = "suppressed"     # Intentionally suppressed
    EXPIRED = "expired"           # Alert expired without action


class AlertCategory(Enum):
    """Alert categories for classification"""
    WEATHER = "weather"
    DISASTER = "disaster"
    HEALTH = "health"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    SYSTEM = "system"


class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    PAGERDUTY = "pagerduty"


@dataclass
class GeographicLocation:
    """Geographic location for alerts"""
    county_fips: str
    county_name: str
    state: str
    state_fips: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None  # Custom region grouping
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "county_fips": self.county_fips,
            "county_name": self.county_name,
            "state": self.state,
            "state_fips": self.state_fips,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "region": self.region
        }


@dataclass
class AlertSource:
    """Source of the alert"""
    name: str                    # e.g., "NOAA", "FEMA", "ResilienceAI"
    type: str                    # e.g., "weather", "disaster", "prediction"
    confidence: float = 1.0      # Confidence score (0-1)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertMetrics:
    """Metrics associated with an alert"""
    risk_score: float
    affected_population: Optional[int] = None
    affected_area_km2: Optional[float] = None
    economic_impact_usd: Optional[float] = None
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertEvent:
    """Enhanced alert event model"""
    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None  # Groups related alerts
    parent_id: Optional[str] = None       # For alert hierarchies
    
    # Classification
    alert_type: str                       # e.g., "flood", "storm", "drought"
    category: AlertCategory = AlertCategory.DISASTER
    severity: AlertSeverity = AlertSeverity.MEDIUM
    
    # Content
    title: str
    message: str
    description: Optional[str] = None
    recommended_actions: List[str] = field(default_factory=list)
    
    # Location
    location: GeographicLocation
    affected_regions: List[GeographicLocation] = field(default_factory=list)
    
    # Source & Metrics
    source: AlertSource
    metrics: Optional[AlertMetrics] = None
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    effective_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Status
    status: AlertStatus = AlertStatus.PENDING
    
    # Data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    # Audit
    created_by: Optional[str] = None
    acknowledged_by: Optional[str] = None
    
    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def time_to_expiry(self) -> Optional[timedelta]:
        if self.expires_at:
            return self.expires_at - datetime.utcnow()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "correlation_id": self.correlation_id,
            "parent_id": self.parent_id,
            "alert_type": self.alert_type,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "description": self.description,
            "recommended_actions": self.recommended_actions,
            "location": self.location.to_dict(),
            "affected_regions": [r.to_dict() for r in self.affected_regions],
            "source": {
                "name": self.source.name,
                "type": self.source.type,
                "confidence": self.source.confidence
            },
            "metrics": {
                "risk_score": self.metrics.risk_score if self.metrics else None,
                "affected_population": self.metrics.affected_population if self.metrics else None
            } if self.metrics else None,
            "created_at": self.created_at.isoformat(),
            "effective_at": self.effective_at.isoformat() if self.effective_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.value,
            "tags": list(self.tags)
        }


@dataclass
class NotificationDelivery:
    """Tracks notification delivery status"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str
    channel: NotificationChannel
    recipient: str
    
    # Status tracking
    status: str = "pending"  # pending, sent, delivered, failed, bounced
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Content
    subject: Optional[str] = None
    body_preview: Optional[str] = None
    
    # Metadata
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "channel": self.channel.value,
            "recipient": self.recipient,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "retry_count": self.retry_count
        }


@dataclass
class AlertSubscription:
    """Enhanced alert subscription model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Subscriber info
    subscriber_type: str  # "user", "system", "organization"
    subscriber_id: str
    subscriber_name: Optional[str] = None
    
    # Geographic scope
    locations: List[GeographicLocation] = field(default_factory=list)
    include_adjacent_counties: bool = False
    radius_km: Optional[float] = None
    
    # Alert filters
    alert_types: List[str] = field(default_factory=list)
    categories: List[AlertCategory] = field(default_factory=list)
    min_severity: AlertSeverity = AlertSeverity.LOW
    
    # Thresholds
    risk_threshold: float = 0.7
    
    # Notification preferences
    channels: List[NotificationChannel] = field(default_factory=lambda: [NotificationChannel.EMAIL])
    channel_preferences: Dict[NotificationChannel, Dict[str, Any]] = field(default_factory=dict)
    
    # Quiet hours
    quiet_hours_start: Optional[int] = None  # Hour (0-23)
    quiet_hours_end: Optional[int] = None
    timezone: str = "UTC"
    
    # Rate limiting
    max_notifications_per_hour: int = 10
    batch_notifications: bool = False
    batch_interval_minutes: int = 15
    
    # Status
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def should_notify_now(self) -> bool:
        """Check if notifications should be sent based on quiet hours"""
        if self.quiet_hours_start is None or self.quiet_hours_end is None:
            return True
        
        import pytz
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        current_hour = now.hour
        
        if self.quiet_hours_start <= self.quiet_hours_end:
            return not (self.quiet_hours_start <= current_hour < self.quiet_hours_end)
        else:  # Wraps around midnight
            return not (current_hour >= self.quiet_hours_start or current_hour < self.quiet_hours_end)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "subscriber_type": self.subscriber_type,
            "subscriber_id": self.subscriber_id,
            "subscriber_name": self.subscriber_name,
            "locations": [l.to_dict() for l in self.locations],
            "alert_types": self.alert_types,
            "categories": [c.value for c in self.categories],
            "min_severity": self.min_severity.value,
            "risk_threshold": self.risk_threshold,
            "channels": [c.value for c in self.channels],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
```

---

## 4. Severity Classification System

### 4.1 Severity Classifier Implementation

```python
# src/alerts/core/severity_classifier.py

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .alert_models import AlertSeverity, AlertMetrics, AlertCategory


@dataclass
class SeverityRule:
    """Rule for determining alert severity"""
    name: str
    condition: str  # Python expression
    severity: AlertSeverity
    priority: int  # Higher = evaluated first


class SeverityClassifier:
    """
    Intelligent severity classification for alerts
    Uses multiple factors: risk score, population affected, historical data
    """
    
    # Default severity thresholds
    DEFAULT_THRESHOLDS = {
        "risk_score": {
            AlertSeverity.CRITICAL: 0.9,
            AlertSeverity.HIGH: 0.75,
            AlertSeverity.MEDIUM: 0.5,
            AlertSeverity.LOW: 0.25
        },
        "population_affected": {
            AlertSeverity.CRITICAL: 100000,
            AlertSeverity.HIGH: 50000,
            AlertSeverity.MEDIUM: 10000,
            AlertSeverity.LOW: 1000
        }
    }
    
    # Severity multipliers by category
    CATEGORY_MULTIPLIERS = {
        AlertCategory.DISASTER: 1.2,
        AlertCategory.HEALTH: 1.1,
        AlertCategory.WEATHER: 1.0,
        AlertCategory.INFRASTRUCTURE: 0.9,
        AlertCategory.SECURITY: 1.15,
        AlertCategory.SYSTEM: 0.8
    }
    
    def __init__(self, custom_rules: Optional[list] = None):
        self.rules = custom_rules or self._default_rules()
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def _default_rules(self) -> list:
        """Define default severity classification rules"""
        return [
            # Critical rules
            SeverityRule(
                name="extreme_risk",
                condition="risk_score >= 0.95",
                severity=AlertSeverity.CRITICAL,
                priority=100
            ),
            SeverityRule(
                name="mass_casualty",
                condition="affected_population >= 100000",
                severity=AlertSeverity.CRITICAL,
                priority=95
            ),
            SeverityRule(
                name="infrastructure_critical",
                condition="category == 'infrastructure' and risk_score >= 0.85",
                severity=AlertSeverity.CRITICAL,
                priority=90
            ),
            
            # High severity rules
            SeverityRule(
                name="high_risk",
                condition="risk_score >= 0.75",
                severity=AlertSeverity.HIGH,
                priority=80
            ),
            SeverityRule(
                name="significant_population",
                condition="affected_population >= 50000",
                severity=AlertSeverity.HIGH,
                priority=75
            ),
            
            # Medium severity rules
            SeverityRule(
                name="medium_risk",
                condition="risk_score >= 0.5",
                severity=AlertSeverity.MEDIUM,
                priority=50
            ),
            SeverityRule(
                name="moderate_population",
                condition="affected_population >= 10000",
                severity=AlertSeverity.MEDIUM,
                priority=45
            ),
            
            # Low severity rules
            SeverityRule(
                name="low_risk",
                condition="risk_score >= 0.25",
                severity=AlertSeverity.LOW,
                priority=25
            ),
            
            # Default
            SeverityRule(
                name="default",
                condition="True",
                severity=AlertSeverity.INFO,
                priority=0
            )
        ]
    
    def classify(
        self,
        risk_score: float,
        category: AlertCategory,
        metrics: Optional[AlertMetrics] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AlertSeverity:
        """
        Classify alert severity based on multiple factors
        
        Args:
            risk_score: Base risk score (0-1)
            category: Alert category
            metrics: Optional alert metrics
            context: Additional context for classification
            
        Returns:
            Classified severity level
        """
        context = context or {}
        
        # Build evaluation context
        eval_context = {
            "risk_score": risk_score,
            "category": category.value,
            "affected_population": metrics.affected_population if metrics else 0,
            "affected_area_km2": metrics.affected_area_km2 if metrics else 0,
            **context
        }
        
        # Evaluate rules in priority order
        for rule in self.rules:
            try:
                if eval(rule.condition, {"__builtins__": {}}, eval_context):
                    # Apply category multiplier to adjust severity
                    adjusted_severity = self._adjust_for_category(
                        rule.severity, category, risk_score
                    )
                    return adjusted_severity
            except Exception as e:
                # Log error but continue to next rule
                continue
        
        return AlertSeverity.INFO
    
    def _adjust_for_category(
        self,
        base_severity: AlertSeverity,
        category: AlertCategory,
        risk_score: float
    ) -> AlertSeverity:
        """Adjust severity based on category multiplier"""
        multiplier = self.CATEGORY_MULTIPLIERS.get(category, 1.0)
        adjusted_score = risk_score * multiplier
        
        # Map back to severity level
        thresholds = self.DEFAULT_THRESHOLDS["risk_score"]
        
        if adjusted_score >= thresholds[AlertSeverity.CRITICAL]:
            return AlertSeverity.CRITICAL
        elif adjusted_score >= thresholds[AlertSeverity.HIGH]:
            return AlertSeverity.HIGH
        elif adjusted_score >= thresholds[AlertSeverity.MEDIUM]:
            return AlertSeverity.MEDIUM
        elif adjusted_score >= thresholds[AlertSeverity.LOW]:
            return AlertSeverity.LOW
        
        return AlertSeverity.INFO
    
    def get_severity_color(self, severity: AlertSeverity) -> str:
        """Get color code for severity level"""
        colors = {
            AlertSeverity.CRITICAL: "#DC2626",  # Red
            AlertSeverity.HIGH: "#EA580C",      # Orange
            AlertSeverity.MEDIUM: "#CA8A04",    # Yellow
            AlertSeverity.LOW: "#2563EB",       # Blue
            AlertSeverity.INFO: "#059669"       # Green
        }
        return colors.get(severity, "#6B7280")
    
    def get_severity_icon(self, severity: AlertSeverity) -> str:
        """Get icon identifier for severity level"""
        icons = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.HIGH: "⚠️",
            AlertSeverity.MEDIUM: "⚡",
            AlertSeverity.LOW: "ℹ️",
            AlertSeverity.INFO: "📢"
        }
        return icons.get(severity, "📋")
```

---

## 5. Alert Correlation & Deduplication

### 5.1 Correlation Engine Implementation

```python
# src/alerts/core/correlation_engine.py

import hashlib
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import json

from .alert_models import AlertEvent, AlertSeverity, GeographicLocation


@dataclass
class CorrelationGroup:
    """Group of correlated alerts"""
    id: str
    root_alert_id: str
    alert_ids: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    severity: AlertSeverity = AlertSeverity.LOW
    status: str = "active"
    
    def add_alert(self, alert_id: str, severity: AlertSeverity):
        self.alert_ids.add(alert_id)
        self.updated_at = datetime.utcnow()
        # Update severity to highest in group
        if severity.value > self.severity.value:
            self.severity = severity


@dataclass
class CorrelationRule:
    """Rule for correlating alerts"""
    name: str
    match_fields: List[str]
    time_window_minutes: int
    geographic_radius_km: Optional[float] = None
    severity_boost: bool = True


class CorrelationEngine:
    """
    Correlates and deduplicates alerts
    Groups related alerts to reduce noise and provide context
    """
    
    def __init__(self, correlation_window_minutes: int = 60):
        self.correlation_window = timedelta(minutes=correlation_window_minutes)
        self.correlation_groups: Dict[str, CorrelationGroup] = {}
        self.alert_fingerprints: Dict[str, str] = {}  # fingerprint -> alert_id
        self.recent_alerts: List[AlertEvent] = []
        self.max_recent_alerts = 1000
        
        # Default correlation rules
        self.rules = [
            CorrelationRule(
                name="same_location_type",
                match_fields=["location.county_fips", "alert_type"],
                time_window_minutes=60,
                geographic_radius_km=50
            ),
            CorrelationRule(
                name="same_event",
                match_fields=["source.name", "alert_type", "correlation_id"],
                time_window_minutes=120,
                geographic_radius_km=None
            ),
            CorrelationRule(
                name="adjacent_areas",
                match_fields=["alert_type", "severity"],
                time_window_minutes=30,
                geographic_radius_km=100
            )
        ]
    
    def process_alert(self, alert: AlertEvent) -> Tuple[AlertEvent, Optional[CorrelationGroup]]:
        """
        Process a new alert for correlation and deduplication
        
        Returns:
            Tuple of (processed_alert, correlation_group)
        """
        # Check for exact duplicates
        fingerprint = self._generate_fingerprint(alert)
        if fingerprint in self.alert_fingerprints:
            # Duplicate detected - suppress this alert
            alert.status = "suppressed"
            return alert, None
        
        self.alert_fingerprints[fingerprint] = alert.id
        
        # Find existing correlation group
        group = self._find_correlation_group(alert)
        
        if group:
            # Add to existing group
            group.add_alert(alert.id, alert.severity)
            alert.correlation_id = group.id
        else:
            # Create new correlation group
            group = self._create_correlation_group(alert)
            alert.correlation_id = group.id
        
        # Store for future correlation
        self._store_alert(alert)
        
        return alert, group
    
    def _generate_fingerprint(self, alert: AlertEvent) -> str:
        """Generate unique fingerprint for deduplication"""
        # Include key fields that would indicate a duplicate
        fingerprint_data = {
            "type": alert.alert_type,
            "location": alert.location.county_fips,
            "severity": alert.severity.value,
            "title": alert.title,
            # Round to 10-minute window for temporal deduplication
            "time_bucket": alert.created_at.replace(
                minute=(alert.created_at.minute // 10) * 10,
                second=0,
                microsecond=0
            ).isoformat()
        }
        
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
    
    def _find_correlation_group(self, alert: AlertEvent) -> Optional[CorrelationGroup]:
        """Find an existing correlation group for the alert"""
        for group in self.correlation_groups.values():
            if group.status != "active":
                continue
            
            # Check time window
            if datetime.utcnow() - group.updated_at > self.correlation_window:
                continue
            
            # Get root alert for comparison
            root_alert = self._get_alert(group.root_alert_id)
            if not root_alert:
                continue
            
            # Check if alerts correlate
            if self._alerts_correlate(alert, root_alert):
                return group
        
        return None
    
    def _alerts_correlate(self, alert1: AlertEvent, alert2: AlertEvent) -> bool:
        """Check if two alerts should be correlated"""
        for rule in self.rules:
            if self._matches_rule(alert1, alert2, rule):
                return True
        return False
    
    def _matches_rule(
        self,
        alert1: AlertEvent,
        alert2: AlertEvent,
        rule: CorrelationRule
    ) -> bool:
        """Check if two alerts match a correlation rule"""
        # Check time window
        time_diff = abs((alert1.created_at - alert2.created_at).total_seconds())
        if time_diff > rule.time_window_minutes * 60:
            return False
        
        # Check geographic proximity
        if rule.geographic_radius_km:
            distance = self._calculate_distance(
                alert1.location, alert2.location
            )
            if distance > rule.geographic_radius_km:
                return False
        
        # Check field matches
        for field in rule.match_fields:
            if not self._field_matches(alert1, alert2, field):
                return False
        
        return True
    
    def _field_matches(
        self,
        alert1: AlertEvent,
        alert2: AlertEvent,
        field: str
    ) -> bool:
        """Compare a field between two alerts"""
        parts = field.split(".")
        
        val1 = alert1
        val2 = alert2
        
        for part in parts:
            val1 = getattr(val1, part, None)
            val2 = getattr(val2, part, None)
            if val1 is None or val2 is None:
                return False
        
        return val1 == val2
    
    def _calculate_distance(
        self,
        loc1: GeographicLocation,
        loc2: GeographicLocation
    ) -> float:
        """Calculate distance between two locations in km"""
        if not (loc1.latitude and loc1.longitude and loc2.latitude and loc2.longitude):
            return float('inf')
        
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1 = radians(loc1.latitude), radians(loc1.longitude)
        lat2, lon2 = radians(loc2.latitude), radians(loc2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _create_correlation_group(self, alert: AlertEvent) -> CorrelationGroup:
        """Create a new correlation group"""
        group = CorrelationGroup(
            id=f"corr_{alert.id}",
            root_alert_id=alert.id,
            severity=alert.severity
        )
        group.alert_ids.add(alert.id)
        self.correlation_groups[group.id] = group
        return group
    
    def _store_alert(self, alert: AlertEvent):
        """Store alert for future correlation"""
        self.recent_alerts.append(alert)
        
        # Trim old alerts
        cutoff = datetime.utcnow() - self.correlation_window
        self.recent_alerts = [
            a for a in self.recent_alerts
            if a.created_at > cutoff
        ]
        
        # Limit size
        if len(self.recent_alerts) > self.max_recent_alerts:
            self.recent_alerts = self.recent_alerts[-self.max_recent_alerts:]
    
    def _get_alert(self, alert_id: str) -> Optional[AlertEvent]:
        """Retrieve alert by ID"""
        for alert in self.recent_alerts:
            if alert.id == alert_id:
                return alert
        return None
    
    def get_correlated_alerts(self, correlation_id: str) -> List[AlertEvent]:
        """Get all alerts in a correlation group"""
        group = self.correlation_groups.get(correlation_id)
        if not group:
            return []
        
        return [
            a for a in self.recent_alerts
            if a.id in group.alert_ids
        ]
    
    def get_alert_summary(self, correlation_id: str) -> Dict:
        """Get summary of correlated alerts"""
        group = self.correlation_groups.get(correlation_id)
        if not group:
            return {}
        
        alerts = self.get_correlated_alerts(correlation_id)
        
        return {
            "group_id": group.id,
            "alert_count": len(alerts),
            "severity": group.severity.value,
            "status": group.status,
            "created_at": group.created_at.isoformat(),
            "updated_at": group.updated_at.isoformat(),
            "affected_regions": list(set(
                a.location.county_name for a in alerts
            )),
            "alert_types": list(set(a.alert_type for a in alerts)),
            "time_range": {
                "first": min(a.created_at for a in alerts).isoformat(),
                "last": max(a.created_at for a in alerts).isoformat()
            }
        }
```

---

## 6. Multi-Channel Notification System

### 6.1 Base Channel Interface

```python
# src/alerts/channels/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..core.alert_models import AlertEvent, NotificationChannel


@dataclass
class ChannelResult:
    """Result of a notification attempt"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    delivered_at: Optional[datetime] = None
    retryable: bool = False


class NotificationChannelBase(ABC):
    """Base class for all notification channels"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.channel_type: NotificationChannel = None
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self):
        """Validate channel configuration"""
        pass
    
    @abstractmethod
    async def send(
        self,
        alert: AlertEvent,
        recipient: str,
        template_data: Optional[Dict[str, Any]] = None
    ) -> ChannelResult:
        """
        Send notification to recipient
        
        Args:
            alert: The alert event to send
            recipient: Recipient address/identifier
            template_data: Optional template customization data
            
        Returns:
            ChannelResult with delivery status
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if channel is healthy and available"""
        pass
    
    def format_recipient(self, recipient: str) -> str:
        """Format/normalize recipient identifier"""
        return recipient.strip()
    
    def get_rate_limit(self) -> Dict[str, int]:
        """Get rate limit configuration for this channel"""
        return {
            "requests_per_second": 10,
            "requests_per_minute": 100,
            "requests_per_hour": 1000
        }
```

### 6.2 Email Channel Implementation

```python
# src/alerts/channels/email_channel.py

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
from jinja2 import Template

from .base import NotificationChannelBase, ChannelResult
from ..core.alert_models import AlertEvent, NotificationChannel


class EmailChannel(NotificationChannelBase):
    """Email notification channel using SMTP or email API"""
    
    def __init__(self, config: Dict[str, Any]):
        self.channel_type = NotificationChannel.EMAIL
        super().__init__(config)
        
        # Initialize email client
        self.provider = config.get("provider", "smtp")  # smtp, sendgrid, ses
        self.from_address = config["from_address"]
        self.from_name = config.get("from_name", "ResilienceAI Alerts")
        
        if self.provider == "smtp":
            self._init_smtp(config)
        elif self.provider == "sendgrid":
            self._init_sendgrid(config)
        elif self.provider == "ses":
            self._init_ses(config)
    
    def _validate_config(self):
        required = ["from_address"]
        if self.config.get("provider") == "smtp":
            required.extend(["smtp_host", "smtp_port"])
        elif self.config.get("provider") == "sendgrid":
            required.append("api_key")
        
        missing = [f for f in required if f not in self.config]
        if missing:
            raise ValueError(f"Missing email config: {missing}")
    
    def _init_smtp(self, config: Dict[str, Any]):
        """Initialize SMTP connection"""
        import aiosmtplib
        self.smtp_host = config["smtp_host"]
        self.smtp_port = config["smtp_port"]
        self.smtp_user = config.get("smtp_user")
        self.smtp_password = config.get("smtp_password")
        self.use_tls = config.get("use_tls", True)
    
    def _init_sendgrid(self, config: Dict[str, Any]):
        """Initialize SendGrid client"""
        self.api_key = config["api_key"]
        self.api_url = "https://api.sendgrid.com/v3/mail/send"
    
    def _init_ses(self, config: Dict[str, Any]):
        """Initialize AWS SES client"""
        import boto3
        self.ses_client = boto3.client(
            'ses',
            region_name=config.get("region", "us-east-1"),
            aws_access_key_id=config.get("aws_access_key"),
            aws_secret_access_key=config.get("aws_secret_key")
        )
    
    async def send(
        self,
        alert: AlertEvent,
        recipient: str,
        template_data: Optional[Dict[str, Any]] = None
    ) -> ChannelResult:
        """Send email notification"""
        try:
            # Build email content
            subject, html_body, text_body = self._build_email_content(
                alert, template_data
            )
            
            if self.provider == "smtp":
                return await self._send_smtp(recipient, subject, html_body, text_body)
            elif self.provider == "sendgrid":
                return await self._send_sendgrid(recipient, subject, html_body, text_body)
            elif self.provider == "ses":
                return await self._send_ses(recipient, subject, html_body, text_body)
            
        except Exception as e:
            return ChannelResult(
                success=False,
                error=str(e),
                retryable=True
            )
    
    def _build_email_content(
        self,
        alert: AlertEvent,
        template_data: Optional[Dict[str, Any]]
    ) -> tuple:
        """Build email subject and body"""
        # Severity-based subject prefix
        severity_prefixes = {
            "critical": "🚨 CRITICAL",
            "high": "⚠️ HIGH",
            "medium": "⚡ MEDIUM",
            "low": "ℹ️ LOW",
            "info": "📢 INFO"
        }
        prefix = severity_prefixes.get(alert.severity.value, "")
        subject = f"{prefix}: {alert.title} - {alert.location.county_name}"
        
        # HTML template
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background: {{ severity_color }}; color: white; padding: 20px; }
                .content { padding: 20px; }
                .alert-box { border-left: 4px solid {{ severity_color }}; padding-left: 15px; margin: 20px 0; }
                .metrics { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                .actions { background: #e8f4f8; padding: 15px; border-radius: 5px; margin-top: 20px; }
                .footer { color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ severity_icon }} {{ title }}</h1>
                <p>{{ location }}</p>
            </div>
            <div class="content">
                <div class="alert-box">
                    <p><strong>Type:</strong> {{ alert_type }}</p>
                    <p><strong>Severity:</strong> {{ severity }}</p>
                    <p><strong>Source:</strong> {{ source }}</p>
                    <p><strong>Time:</strong> {{ timestamp }}</p>
                </div>
                
                <h2>Alert Details</h2>
                <p>{{ message }}</p>
                
                {% if description %}
                <p>{{ description }}</p>
                {% endif %}
                
                {% if metrics %}
                <div class="metrics">
                    <h3>Risk Metrics</h3>
                    <p><strong>Risk Score:</strong> {{ metrics.risk_score }}</p>
                    {% if metrics.affected_population %}
                    <p><strong>Affected Population:</strong> {{ metrics.affected_population:, }}</p>
                    {% endif %}
                </div>
                {% endif %}
                
                {% if recommended_actions %}
                <div class="actions">
                    <h3>Recommended Actions</h3>
                    <ul>
                    {% for action in recommended_actions %}
                        <li>{{ action }}</li>
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
            <div class="footer">
                <p>This alert was generated by ResilienceAI</p>
                <p>Alert ID: {{ alert_id }}</p>
            </div>
        </body>
        </html>
        """)
        
        from ..core.severity_classifier import SeverityClassifier
        classifier = SeverityClassifier()
        
        html = html_template.render(
            severity_color=classifier.get_severity_color(alert.severity),
            severity_icon=classifier.get_severity_icon(alert.severity),
            title=alert.title,
            location=f"{alert.location.county_name}, {alert.location.state}",
            alert_type=alert.alert_type,
            severity=alert.severity.value.upper(),
            source=alert.source.name,
            timestamp=alert.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            message=alert.message,
            description=alert.description,
            metrics=alert.metrics,
            recommended_actions=alert.recommended_actions,
            alert_id=alert.id,
            **(template_data or {})
        )
        
        # Plain text version
        text_body = f"""
{alert.severity.value.upper()}: {alert.title}
Location: {alert.location.county_name}, {alert.location.state}

{alert.message}

Alert ID: {alert.id}
        """.strip()
        
        return subject, html, text_body
    
    async def _send_smtp(
        self,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> ChannelResult:
        """Send via SMTP"""
        import aiosmtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.from_address}>"
        msg['To'] = recipient
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        await aiosmtplib.send(
            msg.as_string(),
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_user,
            password=self.smtp_password,
            use_tls=self.use_tls
        )
        
        return ChannelResult(success=True, delivered_at=datetime.utcnow())
    
    async def _send_sendgrid(
        self,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> ChannelResult:
        """Send via SendGrid API"""
        payload = {
            "personalizations": [{
                "to": [{"email": recipient}]
            }],
            "from": {"email": self.from_address, "name": self.from_name},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text_body},
                {"type": "text/html", "value": html_body}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            ) as response:
                if response.status == 202:
                    return ChannelResult(success=True, delivered_at=datetime.utcnow())
                else:
                    error_text = await response.text()
                    return ChannelResult(
                        success=False,
                        error=f"SendGrid error: {error_text}",
                        retryable=response.status >= 500
                    )
    
    async def _send_ses(
        self,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> ChannelResult:
        """Send via AWS SES"""
        response = self.ses_client.send_email(
            Source=self.from_address,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': text_body},
                    'Html': {'Data': html_body}
                }
            }
        )
        
        return ChannelResult(
            success=True,
            message_id=response['MessageId'],
            delivered_at=datetime.utcnow()
        )
    
    async def health_check(self) -> bool:
        """Check email channel health"""
        try:
            if self.provider == "smtp":
                import aiosmtplib
                await aiosmtplib.connect(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=self.use_tls
                )
                return True
            elif self.provider == "sendgrid":
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://api.sendgrid.com/v3/user/profile",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    ) as response:
                        return response.status == 200
            return True
        except Exception:
            return False
```

---

## 7. Implementation Priority Order

### Phase 1: Core Foundation (Weeks 1-2)
1. **Enhanced Data Models** (`alert_models.py`)
   - Implement new AlertEvent, AlertSubscription models
   - Add enums for Severity, Status, Category, Channels

2. **Severity Classifier** (`severity_classifier.py`)
   - Rule-based severity classification
   - Color and icon mapping

3. **Basic Alert Manager Enhancement**
   - Extend existing `alert_manager.py` with new models
   - Maintain backward compatibility

### Phase 2: Notification Channels (Weeks 3-4)
1. **Email Channel** (`email_channel.py`)
   - SMTP, SendGrid, SES support
   - HTML template system

2. **SMS Channel** (`sms_channel.py`)
   - Twilio, AWS SNS support

3. **Webhook Channel** (`webhook_channel.py`)
   - Generic webhook delivery

### Phase 3: Intelligence Features (Weeks 5-6)
1. **Correlation Engine** (`correlation_engine.py`)
   - Alert deduplication
   - Geographic correlation

2. **Dispatch Engine** (`dispatch_engine.py`)
   - Multi-channel dispatch
   - Rate limiting

3. **Rate Limiter** (`rate_limiter.py`)
   - Per-channel rate limiting
   - User-level quotas

### Phase 4: Advanced Features (Weeks 7-8)
1. **Escalation Engine** (`escalation_engine.py`)
   - Time-based escalation
   - Policy management

2. **Preference Manager** (`preference_manager.py`)
   - User notification settings
   - Quiet hours

3. **Audit Logger** (`audit_logger.py`)
   - Comprehensive audit trail
   - Compliance reporting

### Phase 5: Real-Time Streaming (Weeks 9-10)
1. **WebSocket Server** (`websocket_server.py`)
   - Real-time alert streaming
   - Client subscription management

2. **SSE Handler** (`sse_handler.py`)
   - HTTP-based streaming
   - FastAPI integration

### Phase 6: Integration & Testing (Weeks 11-12)
1. **Integration Module** (`integration.py`)
   - Connect to existing pipeline
   - API endpoints

2. **Testing & Documentation**
   - Unit tests for all components
   - Integration tests
   - API documentation

---

## 8. Integration with Existing ResilienceAI Code

### 8.1 Integration Points

```python
# src/alerts/integration.py

"""
Integration module for connecting alerts to existing ResilienceAI components
"""

from typing import Dict, Any, Optional
import asyncio

from .core.alert_models import AlertEvent, AlertSeverity, GeographicLocation, AlertSource
from .core.severity_classifier import SeverityClassifier
from .core.correlation_engine import CorrelationEngine
from .dispatch.dispatch_engine import AlertDispatchEngine, DispatchConfig
from .escalation.escalation_engine import EscalationEngine
from .streaming.websocket_server import AlertWebSocketServer
from .preferences.preference_manager import PreferenceManager
from .audit.audit_logger import AuditLogger, AuditEventType


class AlertSystemIntegration:
    """
    Main integration point for the alert system
    Connects alerts to the existing ResilienceAI pipeline
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # Initialize components
        self.severity_classifier = SeverityClassifier()
        self.correlation_engine = CorrelationEngine()
        self.dispatch_engine = AlertDispatchEngine(DispatchConfig())
        self.escalation_engine = EscalationEngine()
        self.preference_manager = PreferenceManager()
        self.audit_logger = AuditLogger()
        self.websocket_server: Optional[AlertWebSocketServer] = None
        
        # Register escalation callback
        self.escalation_engine.register_callback(self._on_escalation)
    
    async def initialize(self):
        """Initialize the alert system"""
        from config.alert_config import ALERT_CONFIG
        
        ws_config = ALERT_CONFIG.get("streaming", {}).get("websocket", {})
        if ws_config.get("enabled", True):
            self.websocket_server = AlertWebSocketServer(
                host=ws_config.get("host", "0.0.0.0"),
                port=ws_config.get("port", 8765)
            )
            asyncio.create_task(self.websocket_server.start())
        
        # Start escalation loop
        asyncio.create_task(
            self.escalation_engine.run_escalation_loop(
                ALERT_CONFIG.get("escalation", {}).get("check_interval_seconds", 60)
            )
        )
    
    async def process_risk_alert(
        self,
        county_fips: str,
        county_name: str,
        state: str,
        risk_score: float,
        alert_type: str,
        source_data: Dict[str, Any]
    ) -> Optional[AlertEvent]:
        """Process a risk-based alert from the existing pipeline"""
        # Classify severity
        severity = self.severity_classifier.classify(
            risk_score=risk_score,
            category=source_data.get("category", "disaster"),
            metrics=source_data.get("metrics")
        )
        
        # Create alert event
        location = GeographicLocation(
            county_fips=county_fips,
            county_name=county_name,
            state=state
        )
        
        alert = AlertEvent(
            title=f"{alert_type.replace('_', ' ').title()} Risk Alert",
            message=source_data.get("message", f"Risk score of {risk_score:.2f} detected"),
            alert_type=alert_type,
            severity=severity,
            location=location,
            source=AlertSource(
                name=source_data.get("source", "ResilienceAI"),
                type=source_data.get("source_type", "prediction"),
                confidence=source_data.get("confidence", 1.0)
            ),
            raw_data=source_data
        )
        
        # Process through correlation engine
        alert, correlation_group = self.correlation_engine.process_alert(alert)
        
        # Log audit event
        self.audit_logger.log(
            AuditEventType.ALERT_CREATED,
            alert_id=alert.id,
            details=alert.to_dict()
        )
        
        # Get matching subscriptions
        subscriptions = self._get_matching_subscriptions(alert)
        
        # Dispatch to subscribers
        if subscriptions:
            deliveries = await self.dispatch_engine.dispatch(alert, subscriptions)
            
            # Log dispatch
            self.audit_logger.log(
                AuditEventType.ALERT_DISPATCHED,
                alert_id=alert.id,
                details={"delivery_count": len(deliveries)}
            )
        
        # Broadcast to WebSocket clients
        if self.websocket_server:
            await self.websocket_server.broadcast_alert(alert)
        
        # Start escalation if critical/high
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            self.escalation_engine.start_escalation(alert)
        
        return alert
    
    def _get_matching_subscriptions(self, alert: AlertEvent) -> list:
        """Get subscriptions that match this alert"""
        # Get all active subscriptions
        all_subs = self.preference_manager.get_all_active_subscriptions()
        
        matching = []
        for sub in all_subs:
            # Check location match
            location_match = any(
                loc.county_fips == alert.location.county_fips
                for loc in sub.locations
            )
            
            # Check alert type match
            type_match = (
                "*" in sub.alert_types or
                alert.alert_type in sub.alert_types
            )
            
            # Check severity match
            severity_match = alert.severity.value >= sub.min_severity.value
            
            if location_match and type_match and severity_match:
                matching.append(sub)
        
        return matching
    
    def _on_escalation(self, escalation_data: Dict[str, Any]):
        """Handle escalation events"""
        # Log escalation
        self.audit_logger.log(
            AuditEventType.ALERT_ESCALATED,
            alert_id=escalation_data.get("alert", {}).get("id"),
            details=escalation_data
        )
        
        # Could trigger additional notifications here
        # e.g., PagerDuty, phone calls, etc.


# Singleton instance
alert_system = AlertSystemIntegration()


# Usage in existing pipeline
async def on_risk_detected(
    county_fips: str,
    county_name: str,
    state: str,
    risk_score: float,
    alert_type: str = "risk_threshold"
):
    """Called when risk threshold is exceeded in existing pipeline"""
    await alert_system.process_risk_alert(
        county_fips=county_fips,
        county_name=county_name,
        state=state,
        risk_score=risk_score,
        alert_type=alert_type,
        source_data={
            "source": "ResilienceAI Risk Model",
            "source_type": "prediction",
            "confidence": risk_score,
            "category": "disaster"
        }
    )
```

---

## 9. Summary

This comprehensive alert and notification enhancement provides:

1. **Enhanced Alert Models** - Standardized severity levels, status tracking, and rich metadata
2. **Intelligent Classification** - Rule-based severity classification with category multipliers
3. **Alert Correlation** - Deduplication and grouping of related alerts
4. **Multi-Channel Notifications** - Email, SMS, Push, Webhook, Slack support
5. **Escalation Procedures** - Time-based escalation with configurable policies
6. **Real-Time Streaming** - WebSocket and SSE for live alert updates
7. **User Preferences** - Granular notification settings with quiet hours
8. **Audit & History** - Comprehensive logging for compliance and debugging
9. **Rate Limiting** - Prevent alert fatigue with intelligent throttling
10. **Integration Layer** - Seamless connection to existing ResilienceAI pipeline

### Key Files Created:

| File Path | Description |
|-----------|-------------|
| `/mnt/okcomputer/output/resilience_ai_analysis/28_alert_notification.md` | This comprehensive document |

### Implementation Files to Create:

| File Path | Description |
|-----------|-------------|
| `src/alerts/core/alert_models.py` | Enhanced data models |
| `src/alerts/core/severity_classifier.py` | Severity classification |
| `src/alerts/core/correlation_engine.py` | Alert correlation |
| `src/alerts/channels/base.py` | Channel base class |
| `src/alerts/channels/email_channel.py` | Email notifications |
| `src/alerts/channels/sms_channel.py` | SMS notifications |
| `src/alerts/channels/push_channel.py` | Push notifications |
| `src/alerts/dispatch/dispatch_engine.py` | Alert dispatch |
| `src/alerts/escalation/escalation_engine.py` | Escalation logic |
| `src/alerts/streaming/websocket_server.py` | WebSocket server |
| `src/alerts/preferences/preference_manager.py` | User preferences |
| `src/alerts/audit/audit_logger.py` | Audit logging |
| `src/alerts/integration.py` | Integration module |
| `config/alert_config.py` | Configuration |

---

*Document generated for ResilienceAI Alert & Notification System Enhancement*
