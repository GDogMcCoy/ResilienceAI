"""
Incident Response Framework for ResilienceAI
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """Incident severity levels."""
    P1_CRITICAL = "P1-Critical"
    P2_HIGH = "P2-High"
    P3_MEDIUM = "P3-Medium"
    P4_LOW = "P4-Low"


class IncidentStatus(Enum):
    """Incident lifecycle status."""
    DETECTED = auto()
    ACKNOWLEDGED = auto()
    INVESTIGATING = auto()
    MITIGATING = auto()
    RESOLVED = auto()
    CLOSED = auto()


class IncidentType(Enum):
    """Types of incidents."""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    SECURITY = "security"
    DATA = "data"
    NETWORK = "network"
    DATABASE = "database"


@dataclass
class Incident:
    """Incident record."""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    incident_type: IncidentType
    status: IncidentStatus
    detected_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    commander: Optional[str] = None
    affected_services: List[str] = field(default_factory=list)
    timeline: List[Dict] = field(default_factory=list)
    communications: List[Dict] = field(default_factory=list)
    post_mortem: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "type": self.incident_type.value,
            "status": self.status.name,
            "detected_at": self.detected_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "assigned_to": self.assigned_to,
            "commander": self.commander,
            "affected_services": self.affected_services
        }


class IncidentResponseFramework:
    """
    Comprehensive incident response framework for ResilienceAI.
    """
    
    def __init__(self):
        self.active_incidents: Dict[str, Incident] = {}
        self.resolved_incidents: List[Incident] = []
        self.escalation_matrix = self._load_escalation_matrix()
        self.notification_handlers: List[Callable] = []
    
    def _load_escalation_matrix(self) -> Dict:
        """Load escalation matrix."""
        return {
            IncidentSeverity.P1_CRITICAL: {
                "immediate": ["on-call-engineer", "engineering-manager"],
                "5_minutes": ["cto", "vp-engineering"],
                "15_minutes": ["ceo", "incident-commander"]
            },
            IncidentSeverity.P2_HIGH: {
                "immediate": ["on-call-engineer"],
                "15_minutes": ["engineering-manager"],
                "30_minutes": ["cto"]
            },
            IncidentSeverity.P3_MEDIUM: {
                "immediate": ["on-call-engineer"],
                "1_hour": ["engineering-manager"]
            },
            IncidentSeverity.P4_LOW: {
                "immediate": ["on-call-engineer"]
            }
        }
    
    def register_notification_handler(self, handler: Callable):
        """Register notification handler."""
        self.notification_handlers.append(handler)
    
    async def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        incident_type: IncidentType,
        affected_services: List[str] = None
    ) -> Incident:
        """Create a new incident."""
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            incident_type=incident_type,
            status=IncidentStatus.DETECTED,
            detected_at=datetime.utcnow(),
            affected_services=affected_services or []
        )
        
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "Incident detected",
            "actor": "monitoring_system"
        })
        
        self.active_incidents[incident_id] = incident
        logger.info(f"Incident created: {incident_id} - {title}")
        
        await self._notify_incident_created(incident)
        asyncio.create_task(self._escalation_timer(incident))
        
        return incident
    
    async def acknowledge_incident(self, incident_id: str, acknowledged_by: str) -> Incident:
        """Acknowledge an incident."""
        incident = self.active_incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = datetime.utcnow()
        incident.assigned_to = acknowledged_by
        
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "Incident acknowledged",
            "actor": acknowledged_by
        })
        
        logger.info(f"Incident {incident_id} acknowledged by {acknowledged_by}")
        await self._notify_incident_acknowledged(incident)
        return incident
    
    async def assign_commander(self, incident_id: str, commander: str) -> Incident:
        """Assign incident commander."""
        incident = self.active_incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        incident.commander = commander
        incident.status = IncidentStatus.INVESTIGATING
        
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": f"Incident commander assigned: {commander}",
            "actor": "system"
        })
        
        logger.info(f"Incident commander assigned for {incident_id}: {commander}")
        return incident
    
    async def update_incident_status(
        self,
        incident_id: str,
        status: IncidentStatus,
        updated_by: str,
        notes: str = None
    ) -> Incident:
        """Update incident status."""
        incident = self.active_incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        old_status = incident.status
        incident.status = status
        
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": f"Status changed from {old_status.name} to {status.name}",
            "actor": updated_by,
            "notes": notes
        })
        
        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.utcnow()
            await self._notify_incident_resolved(incident)
        
        return incident
    
    async def close_incident(self, incident_id: str, closed_by: str, post_mortem: str = None) -> Incident:
        """Close an incident."""
        incident = self.active_incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        incident.status = IncidentStatus.CLOSED
        incident.post_mortem = post_mortem
        
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "Incident closed",
            "actor": closed_by
        })
        
        self.resolved_incidents.append(incident)
        del self.active_incidents[incident_id]
        
        logger.info(f"Incident {incident_id} closed")
        return incident
    
    async def _escalation_timer(self, incident: Incident):
        """Handle escalation timing."""
        await asyncio.sleep(60)
        if incident.status == IncidentStatus.DETECTED:
            await self._escalate_incident(incident, "not_acknowledged")
    
    async def _escalate_incident(self, incident: Incident, reason: str):
        """Escalate an incident."""
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": f"Incident escalated: {reason}",
            "actor": "system"
        })
        logger.warning(f"Incident {incident.incident_id} escalated: {reason}")
    
    async def _notify_incident_created(self, incident: Incident):
        """Notify about new incident."""
        notification = {
            "type": "incident_created",
            "incident": incident.to_dict()
        }
        for handler in self.notification_handlers:
            try:
                await handler(notification)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")
    
    async def _notify_incident_acknowledged(self, incident: Incident):
        """Notify about incident acknowledgment."""
        notification = {
            "type": "incident_acknowledged",
            "incident": incident.to_dict()
        }
        for handler in self.notification_handlers:
            try:
                await handler(notification)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")
    
    async def _notify_incident_resolved(self, incident: Incident):
        """Notify about incident resolution."""
        notification = {
            "type": "incident_resolved",
            "incident": incident.to_dict()
        }
        for handler in self.notification_handlers:
            try:
                await handler(notification)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")
    
    def get_incident_statistics(self) -> Dict:
        """Get incident statistics."""
        all_incidents = list(self.active_incidents.values()) + self.resolved_incidents
        
        severity_counts = {}
        for severity in IncidentSeverity:
            severity_counts[severity.value] = sum(1 for i in all_incidents if i.severity == severity)
        
        resolved = [i for i in self.resolved_incidents if i.resolved_at]
        mttr_seconds = sum(
            (i.resolved_at - i.detected_at).total_seconds()
            for i in resolved
        ) / len(resolved) if resolved else 0
        
        return {
            "total_incidents": len(all_incidents),
            "active_incidents": len(self.active_incidents),
            "resolved_incidents": len(self.resolved_incidents),
            "by_severity": severity_counts,
            "mttr_seconds": mttr_seconds,
            "mttr_minutes": mttr_seconds / 60
        }


if __name__ == "__main__":
    async def main():
        framework = IncidentResponseFramework()
        
        incident = await framework.create_incident(
            title="Database Connection Pool Exhausted",
            description="Application unable to acquire database connections",
            severity=IncidentSeverity.P2_HIGH,
            incident_type=IncidentType.DATABASE,
            affected_services=["api-service", "data-pipeline"]
        )
        
        print(f"Created: {json.dumps(incident.to_dict(), indent=2)}")
        
        await framework.acknowledge_incident(incident.incident_id, "john.doe")
        await framework.assign_commander(incident.incident_id, "jane.smith")
        
        stats = framework.get_incident_statistics()
        print(f"\nStats: {json.dumps(stats, indent=2)}")
    
    asyncio.run(main())
