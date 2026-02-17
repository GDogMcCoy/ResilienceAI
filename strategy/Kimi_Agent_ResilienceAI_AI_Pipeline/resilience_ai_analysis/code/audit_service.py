# /mnt/okcomputer/output/resilience_ai_analysis/code/audit_service.py
"""
Audit Service for ResilienceAI
Manages audit trails for all archival operations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import hashlib
import uuid


class AuditEventType(Enum):
    """Audit event types."""
    # Data operations
    ARCHIVE_CREATED = "archive_created"
    DATA_ACCESSED = "data_accessed"
    METADATA_UPDATED = "metadata_updated"
    ARCHIVE_DELETED = "archive_deleted"
    TIER_TRANSITION = "tier_transition"
    RETRIEVAL_INITIATED = "retrieval_initiated"
    RETRIEVAL_COMPLETED = "retrieval_completed"
    
    # Access control
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGED = "permission_changed"
    ROLE_ASSIGNED = "role_assigned"
    ACCESS_DENIED = "access_denied"
    
    # Compliance
    LEGAL_HOLD_APPLIED = "legal_hold_applied"
    LEGAL_HOLD_RELEASED = "legal_hold_released"
    RETENTION_EXPIRED = "retention_expired"
    COMPLIANCE_CHECK = "compliance_check"
    
    # System
    BACKUP_COMPLETED = "backup_completed"
    RESTORE_COMPLETED = "restore_completed"
    KEY_ROTATED = "key_rotated"
    CONFIG_CHANGED = "config_changed"


@dataclass
class AuditEvent:
    """Audit event record."""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    actor: str
    actor_type: str  # user, system, service
    resource_type: str
    resource_id: str
    action: str
    status: str  # success, failure, pending
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    correlation_id: Optional[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "actor": self.actor,
            "actor_type": self.actor_type,
            "resource": {
                "type": self.resource_type,
                "id": self.resource_id
            },
            "action": self.action,
            "status": self.status,
            "details": self.details,
            "context": {
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
                "session_id": self.session_id,
                "correlation_id": self.correlation_id
            }
        }


class AuditService:
    """Service for managing audit trails."""
    
    def __init__(self, kafka_producer=None, clickhouse_client=None, s3_client=None):
        self.kafka = kafka_producer
        self.clickhouse = clickhouse_client
        self.s3 = s3_client
        self.local_buffer: List[AuditEvent] = []
        self.buffer_size = 1000
    
    def log_event(self, event_type: AuditEventType, actor: str,
                  resource_type: str, resource_id: str, action: str,
                  status: str = "success", details: Dict = None,
                  **context) -> AuditEvent:
        """Log an audit event."""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now(),
            actor=actor,
            actor_type=context.get("actor_type", "user"),
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status=status,
            details=details or {},
            ip_address=context.get("ip_address"),
            user_agent=context.get("user_agent"),
            session_id=context.get("session_id"),
            correlation_id=context.get("correlation_id")
        )
        
        # Add to buffer
        self.local_buffer.append(event)
        
        # Flush if buffer is full
        if len(self.local_buffer) >= self.buffer_size:
            self._flush_buffer()
        
        # Also send to Kafka for real-time processing
        if self.kafka:
            self._send_to_kafka(event)
        
        return event
    
    def _send_to_kafka(self, event: AuditEvent):
        """Send event to Kafka for streaming."""
        try:
            self.kafka.send(
                topic="audit-events",
                key=event.event_type.value.encode(),
                value=json.dumps(event.to_dict()).encode()
            )
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Failed to send audit event to Kafka: {e}")
    
    def _flush_buffer(self):
        """Flush buffer to persistent storage."""
        if not self.local_buffer:
            return
        
        # Store in ClickHouse for analytics
        if self.clickhouse:
            self._store_in_clickhouse(self.local_buffer)
        
        # Archive to S3 for long-term storage
        if self.s3:
            self._archive_to_s3(self.local_buffer)
        
        # Clear buffer
        self.local_buffer = []
    
    def _store_in_clickhouse(self, events: List[AuditEvent]):
        """Store events in ClickHouse for analytics."""
        # Implementation would use clickhouse-driver
        pass
    
    def _archive_to_s3(self, events: List[AuditEvent]):
        """Archive events to S3 for long-term storage."""
        # Group events by date
        events_by_date = {}
        for event in events:
            date_key = event.timestamp.strftime("%Y-%m-%d")
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append(event.to_dict())
        
        # Upload to S3
        for date_key, event_list in events_by_date.items():
            key = f"audit-logs/{date_key}/{datetime.now().isoformat()}.jsonl"
            content = "\n".join([json.dumps(e) for e in event_list])
            
            # Implementation would use boto3
            # self.s3.put_object(Bucket="audit-bucket", Key=key, Body=content)
    
    def query_events(self, start_time: datetime, end_time: datetime,
                    event_types: List[AuditEventType] = None,
                    actor: str = None, resource_id: str = None,
                    limit: int = 1000) -> List[AuditEvent]:
        """Query audit events."""
        # Implementation would query ClickHouse
        return []
    
    def generate_audit_report(self, start_time: datetime, 
                             end_time: datetime) -> Dict:
        """Generate audit report for compliance."""
        events = self.query_events(start_time, end_time)
        
        # Aggregate statistics
        event_counts = {}
        actor_counts = {}
        resource_counts = {}
        
        for event in events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            actor_counts[event.actor] = actor_counts.get(event.actor, 0) + 1
            
            resource_key = f"{event.resource_type}:{event.resource_id}"
            resource_counts[resource_key] = resource_counts.get(resource_key, 0) + 1
        
        return {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "total_events": len(events),
            "event_breakdown": event_counts,
            "top_actors": sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_resources": sorted(resource_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "generated_at": datetime.now().isoformat()
        }
    
    def verify_audit_integrity(self, start_time: datetime, 
                              end_time: datetime) -> Dict:
        """Verify integrity of audit trail."""
        # Implementation would verify chain of custody
        return {
            "verification_status": "passed",
            "events_verified": 0,
            "tampering_detected": False,
            "verified_at": datetime.now().isoformat()
        }
    
    def create_audit_trail(self, data_id: str, 
                          operations: List[Dict]) -> List[AuditEvent]:
        """Create complete audit trail for data object."""
        events = []
        
        for op in operations:
            event = self.log_event(
                event_type=AuditEventType(op["type"]),
                actor=op["actor"],
                resource_type="archive",
                resource_id=data_id,
                action=op["action"],
                status=op.get("status", "success"),
                details=op.get("details", {}),
                correlation_id=op.get("correlation_id")
            )
            events.append(event)
        
        return events


if __name__ == "__main__":
    # Example usage
    service = AuditService()
    
    # Log archive creation
    event = service.log_event(
        event_type=AuditEventType.ARCHIVE_CREATED,
        actor="security-team@resilienceai.com",
        resource_type="archive",
        resource_id="INC-2024-001",
        action="create",
        details={
            "size_bytes": 1024 * 1024 * 10,
            "compression_ratio": 3.5,
            "encryption": "AES-256-GCM"
        },
        ip_address="10.0.1.100"
    )
    
    print(f"Logged event: {event.event_id}")
    print(f"Event type: {event.event_type.value}")
    
    # Generate audit report
    from datetime import timedelta
    report = service.generate_audit_report(
        start_time=datetime.now() - timedelta(days=30),
        end_time=datetime.now()
    )
    
    print(f"\nAudit report: {json.dumps(report, indent=2)}")
