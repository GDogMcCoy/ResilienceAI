"""
Alert Generation and Management System

Provides comprehensive alerting capabilities for anomaly detection.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

from .architecture import AnomalyScore, AlertSeverity, AnomalyType

logger = logging.getLogger(__name__)


class AlertChannel(Enum):
    """Supported alert channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    CONSOLE = "console"
    DATABASE = "database"


@dataclass
class Alert:
    """Represents an anomaly alert."""
    id: str
    timestamp: datetime
    severity: AlertSeverity
    anomaly_type: AnomalyType
    score: float
    confidence: float
    title: str
    description: str
    source: str
    affected_metrics: List[str]
    recommended_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'anomaly_type': self.anomaly_type.value,
            'score': self.score,
            'confidence': self.confidence,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'affected_metrics': self.affected_metrics,
            'recommended_actions': self.recommended_actions,
            'metadata': self.metadata,
            'acknowledged': self.acknowledged,
            'resolved': self.resolved,
            'resolution_time': self.resolution_time.isoformat() if self.resolution_time else None
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class AlertRule:
    """Rule for generating alerts from anomaly scores."""
    
    def __init__(self,
                 name: str,
                 severity_threshold: AlertSeverity,
                 min_score: float,
                 min_confidence: float = 0.5,
                 cooldown_minutes: int = 15,
                 channels: List[AlertChannel] = None,
                 filters: Dict[str, Any] = None):
        self.name = name
        self.severity_threshold = severity_threshold
        self.min_score = min_score
        self.min_confidence = min_confidence
        self.cooldown_minutes = cooldown_minutes
        self.channels = channels or [AlertChannel.CONSOLE]
        self.filters = filters or {}
        
        self.last_alert_time: Optional[datetime] = None
        self.alert_count: int = 0
        
    def should_alert(self, anomaly_score: AnomalyScore) -> bool:
        """Check if this rule should generate an alert."""
        # Check severity
        severity_order = [AlertSeverity.LOW, AlertSeverity.MEDIUM, 
                         AlertSeverity.HIGH, AlertSeverity.CRITICAL]
        if severity_order.index(anomaly_score.severity) < \
           severity_order.index(self.severity_threshold):
            return False
        
        # Check score threshold
        if anomaly_score.score < self.min_score:
            return False
        
        # Check confidence
        if anomaly_score.confidence < self.min_confidence:
            return False
        
        # Check cooldown
        if self.last_alert_time:
            elapsed = datetime.now() - self.last_alert_time
            if elapsed < timedelta(minutes=self.cooldown_minutes):
                return False
        
        # Apply filters
        for key, value in self.filters.items():
            if key in anomaly_score.metadata:
                if anomaly_score.metadata[key] != value:
                    return False
        
        return True
    
    def record_alert(self):
        """Record that an alert was generated."""
        self.last_alert_time = datetime.now()
        self.alert_count += 1


class AlertManager:
    """
    Centralized alert management system.
    """
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alert_history: List[Alert] = []
        self.channel_handlers: Dict[AlertChannel, Callable] = {}
        self.suppression_rules: List[Callable] = []
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default alert channel handlers."""
        self.channel_handlers[AlertChannel.CONSOLE] = self._send_console_alert
        self.channel_handlers[AlertChannel.DATABASE] = self._send_database_alert
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove an alert rule."""
        self.rules = [r for r in self.rules if r.name != rule_name]
    
    def register_channel_handler(self, 
                                  channel: AlertChannel, 
                                  handler: Callable):
        """Register a handler for an alert channel."""
        self.channel_handlers[channel] = handler
    
    def add_suppression_rule(self, rule: Callable):
        """Add a suppression rule."""
        self.suppression_rules.append(rule)
    
    def process_anomaly(self, anomaly_score: AnomalyScore,
                       source: str = "unknown") -> List[Alert]:
        """
        Process an anomaly score and generate alerts.
        
        Returns:
            List of generated alerts
        """
        # Check suppression rules
        for rule in self.suppression_rules:
            if rule(anomaly_score):
                logger.debug(f"Alert suppressed for anomaly: {anomaly_score}")
                return []
        
        generated_alerts = []
        
        # Check each rule
        for rule in self.rules:
            if rule.should_alert(anomaly_score):
                # Generate alert
                alert = self._create_alert(anomaly_score, source, rule)
                
                # Send to channels
                for channel in rule.channels:
                    self._send_alert(alert, channel)
                
                rule.record_alert()
                generated_alerts.append(alert)
                self.alert_history.append(alert)
        
        return generated_alerts
    
    def _create_alert(self, 
                     anomaly_score: AnomalyScore,
                     source: str,
                     rule: AlertRule) -> Alert:
        """Create an alert from anomaly score."""
        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(self.alert_history)}"
        
        # Generate title and description
        title = self._generate_title(anomaly_score)
        description = self._generate_description(anomaly_score)
        
        # Get affected metrics
        affected_metrics = list(anomaly_score.feature_contributions.keys())
        
        # Generate recommendations
        recommendations = self._generate_recommendations(anomaly_score)
        
        return Alert(
            id=alert_id,
            timestamp=anomaly_score.timestamp,
            severity=anomaly_score.severity,
            anomaly_type=anomaly_score.anomaly_type,
            score=anomaly_score.score,
            confidence=anomaly_score.confidence,
            title=title,
            description=description,
            source=source,
            affected_metrics=affected_metrics,
            recommended_actions=recommendations,
            metadata={
                'rule': rule.name,
                **anomaly_score.metadata
            }
        )
    
    def _generate_title(self, anomaly_score: AnomalyScore) -> str:
        """Generate alert title."""
        severity_str = anomaly_score.severity.value.upper()
        type_str = anomaly_score.anomaly_type.value
        
        return f"[{severity_str}] {type_str} Anomaly Detected (Score: {anomaly_score.score:.2f})"
    
    def _generate_description(self, anomaly_score: AnomalyScore) -> str:
        """Generate alert description."""
        lines = [
            f"Anomaly detected with score {anomaly_score.score:.4f} "
            f"and confidence {anomaly_score.confidence:.2%}",
            "",
            "Top contributing features:"
        ]
        
        # Add top features
        sorted_features = sorted(
            anomaly_score.feature_contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for feature, contribution in sorted_features:
            lines.append(f"  - {feature}: {contribution:.2%}")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, anomaly_score: AnomalyScore) -> List[str]:
        """Generate recommended actions based on anomaly."""
        recommendations = []
        
        if anomaly_score.severity == AlertSeverity.CRITICAL:
            recommendations.extend([
                "Immediately investigate the affected metrics",
                "Consider pausing related data pipelines",
                "Notify on-call engineer"
            ])
        elif anomaly_score.severity == AlertSeverity.HIGH:
            recommendations.extend([
                "Investigate within 30 minutes",
                "Check related systems for issues",
                "Monitor for recurrence"
            ])
        elif anomaly_score.severity == AlertSeverity.MEDIUM:
            recommendations.extend([
                "Review during next business day",
                "Add to monitoring dashboard",
                "Document for pattern analysis"
            ])
        else:
            recommendations.extend([
                "Log for future reference",
                "Include in weekly report"
            ])
        
        return recommendations
    
    def _send_alert(self, alert: Alert, channel: AlertChannel):
        """Send alert to specified channel."""
        handler = self.channel_handlers.get(channel)
        
        if handler:
            try:
                handler(alert)
                logger.info(f"Alert {alert.id} sent to {channel.value}")
            except Exception as e:
                logger.error(f"Failed to send alert to {channel.value}: {e}")
        else:
            logger.warning(f"No handler for channel: {channel.value}")
    
    def _send_console_alert(self, alert: Alert):
        """Send alert to console."""
        print(f"\n{'='*60}")
        print(f"ALERT: {alert.title}")
        print(f"{'='*60}")
        print(f"ID: {alert.id}")
        print(f"Severity: {alert.severity.value}")
        print(f"Score: {alert.score:.4f}")
        print(f"Source: {alert.source}")
        print(f"\n{alert.description}")
        print(f"\nRecommended Actions:")
        for action in alert.recommended_actions:
            print(f"  - {action}")
        print(f"{'='*60}\n")
    
    def _send_database_alert(self, alert: Alert):
        """Store alert in database."""
        # Placeholder for database storage
        logger.info(f"Alert {alert.id} stored in database")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        if not self.alert_history:
            return {'total_alerts': 0}
        
        df = pd.DataFrame([a.to_dict() for a in self.alert_history])
        
        return {
            'total_alerts': len(self.alert_history),
            'alerts_by_severity': df['severity'].value_counts().to_dict(),
            'alerts_by_type': df['anomaly_type'].value_counts().to_dict(),
            'acknowledged_rate': df['acknowledged'].mean(),
            'resolved_rate': df['resolved'].mean(),
            'avg_resolution_time_minutes': self._avg_resolution_time()
        }
    
    def _avg_resolution_time(self) -> Optional[float]:
        """Calculate average resolution time in minutes."""
        resolved = [a for a in self.alert_history 
                   if a.resolved and a.resolution_time]
        
        if not resolved:
            return None
        
        times = [(a.resolution_time - a.timestamp).total_seconds() / 60 
                for a in resolved]
        
        return np.mean(times)


# Export classes
__all__ = [
    'AlertChannel', 'Alert', 'AlertRule', 'AlertManager'
]
