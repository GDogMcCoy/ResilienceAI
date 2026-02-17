# /mnt/okcomputer/output/resilience_ai_analysis/code/retrieval_service.py
"""
Retrieval Service for ResilienceAI
Manages data retrieval from archive with priority-based queuing.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import asyncio
import uuid


class RetrievalPriority(Enum):
    """Retrieval priority levels."""
    EXPEDITED = "expedited"    # 1-5 minutes (Glacier), milliseconds (IA)
    STANDARD = "standard"      # 3-5 hours (Glacier), milliseconds (IA)
    BULK = "bulk"              # 5-12 hours (Glacier), milliseconds (IA)


class RetrievalStatus(Enum):
    """Retrieval status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    RESTORING = "restoring"
    AVAILABLE = "available"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class RetrievalRequest:
    """Data retrieval request."""
    request_id: str
    data_id: str
    priority: RetrievalPriority
    requested_by: str
    reason: str
    status: RetrievalStatus
    created_at: datetime
    estimated_completion: Optional[datetime]
    completed_at: Optional[datetime]
    notification_email: Optional[str]


class RetrievalService:
    """Service for managing data retrieval from archive."""
    
    # Retrieval time estimates by tier and priority (in minutes)
    RETRIEVAL_TIMES = {
        'STANDARD_IA': {
            RetrievalPriority.EXPEDITED: 0,      # Immediate
            RetrievalPriority.STANDARD: 0,       # Immediate
            RetrievalPriority.BULK: 0            # Immediate
        },
        'GLACIER_IR': {
            RetrievalPriority.EXPEDITED: 0,      # Immediate
            RetrievalPriority.STANDARD: 0,       # Immediate
            RetrievalPriority.BULK: 0            # Immediate
        },
        'GLACIER': {
            RetrievalPriority.EXPEDITED: 5,      # 1-5 minutes
            RetrievalPriority.STANDARD: 180,     # 3-5 hours
            RetrievalPriority.BULK: 720          # 5-12 hours
        },
        'DEEP_ARCHIVE': {
            RetrievalPriority.EXPEDITED: None,   # Not available
            RetrievalPriority.STANDARD: 720,     # 12 hours
            RetrievalPriority.BULK: 2880         # 48 hours
        }
    }
    
    def __init__(self, cold_storage_manager):
        self.cold_storage = cold_storage_manager
        self.requests: Dict[str, RetrievalRequest] = {}
        self.request_queue: List[RetrievalRequest] = []
        self.audit_log: List[Dict] = []
    
    def submit_retrieval_request(self, data_id: str, 
                                 priority: RetrievalPriority,
                                 requested_by: str,
                                 reason: str,
                                 notification_email: Optional[str] = None) -> RetrievalRequest:
        """Submit a new retrieval request."""
        request_id = str(uuid.uuid4())
        
        # Get storage tier for data
        storage_tier = self._get_storage_tier(data_id)
        
        # Calculate estimated completion
        retrieval_minutes = self.RETRIEVAL_TIMES.get(storage_tier, {}).get(priority)
        estimated_completion = None
        if retrieval_minutes is not None:
            estimated_completion = datetime.now() + timedelta(minutes=retrieval_minutes)
        
        request = RetrievalRequest(
            request_id=request_id,
            data_id=data_id,
            priority=priority,
            requested_by=requested_by,
            reason=reason,
            status=RetrievalStatus.PENDING,
            created_at=datetime.now(),
            estimated_completion=estimated_completion,
            completed_at=None,
            notification_email=notification_email
        )
        
        self.requests[request_id] = request
        
        # Log audit entry
        self._log_audit(request, "request_submitted")
        
        # Queue for processing
        self._queue_request(request)
        
        return request
    
    def _queue_request(self, request: RetrievalRequest):
        """Add request to processing queue based on priority."""
        request.status = RetrievalStatus.QUEUED
        
        # Insert based on priority (lower enum value = higher priority)
        insert_index = 0
        for i, queued_request in enumerate(self.request_queue):
            if queued_request.priority.value > request.priority.value:
                insert_index = i
                break
            insert_index = i + 1
        
        self.request_queue.insert(insert_index, request)
    
    async def process_retrieval_queue(self):
        """Process queued retrieval requests."""
        while self.request_queue:
            request = self.request_queue.pop(0)
            await self._process_retrieval(request)
    
    async def _process_retrieval(self, request: RetrievalRequest):
        """Process a single retrieval request."""
        request.status = RetrievalStatus.IN_PROGRESS
        
        # Check if data is already available
        storage_tier = self._get_storage_tier(request.data_id)
        
        if storage_tier in ['STANDARD_IA', 'GLACIER_IR']:
            # Immediately available
            request.status = RetrievalStatus.AVAILABLE
            request.completed_at = datetime.now()
            self._log_audit(request, "retrieval_completed")
        else:
            # Need to restore from Glacier/Deep Archive
            request.status = RetrievalStatus.RESTORING
            
            # Initiate restore
            restore_result = self.cold_storage.initiate_retrieval(
                bucket=self._get_bucket(request.data_id),
                key=self._get_key(request.data_id),
                tier=request.priority.value
            )
            
            if restore_result['status'] == 'retrieval_initiated':
                # Wait for restore to complete (async)
                await self._wait_for_restore(request)
            else:
                request.status = RetrievalStatus.FAILED
                self._log_audit(request, "retrieval_failed")
    
    async def _wait_for_restore(self, request: RetrievalRequest):
        """Wait for Glacier restore to complete."""
        max_wait_minutes = 2880  # 48 hours
        check_interval = 300     # 5 minutes
        waited_minutes = 0
        
        while waited_minutes < max_wait_minutes:
            await asyncio.sleep(check_interval)
            waited_minutes += check_interval / 60
            
            status = self.cold_storage.check_restore_status(
                bucket=self._get_bucket(request.data_id),
                key=self._get_key(request.data_id)
            )
            
            if status['status'] == 'restored':
                request.status = RetrievalStatus.AVAILABLE
                request.completed_at = datetime.now()
                self._log_audit(request, "retrieval_completed")
                
                # Send notification
                if request.notification_email:
                    self._send_notification(request)
                return
            
            elif status['status'] == 'error':
                request.status = RetrievalStatus.FAILED
                self._log_audit(request, "retrieval_failed")
                return
        
        # Timeout
        request.status = RetrievalStatus.FAILED
        self._log_audit(request, "retrieval_timeout")
    
    def get_request_status(self, request_id: str) -> Dict:
        """Get status of a retrieval request."""
        if request_id not in self.requests:
            return {"status": "error", "message": "Request not found"}
        
        request = self.requests[request_id]
        
        return {
            "request_id": request.request_id,
            "data_id": request.data_id,
            "status": request.status.value,
            "priority": request.priority.value,
            "requested_by": request.requested_by,
            "reason": request.reason,
            "created_at": request.created_at.isoformat(),
            "estimated_completion": request.estimated_completion.isoformat() if request.estimated_completion else None,
            "completed_at": request.completed_at.isoformat() if request.completed_at else None
        }
    
    def _log_audit(self, request: RetrievalRequest, action: str):
        """Log audit entry for retrieval."""
        self.audit_log.append({
            "request_id": request.request_id,
            "data_id": request.data_id,
            "action": action,
            "performed_by": request.requested_by,
            "timestamp": datetime.now().isoformat(),
            "reason": request.reason
        })
    
    def _get_storage_tier(self, data_id: str) -> str:
        """Get storage tier for data (placeholder)."""
        # Implementation would query metadata store
        return "GLACIER"
    
    def _get_bucket(self, data_id: str) -> str:
        """Get S3 bucket for data (placeholder)."""
        return "resilienceai-archive"
    
    def _get_key(self, data_id: str) -> str:
        """Get S3 key for data (placeholder)."""
        return f"archive/{data_id}"
    
    def _send_notification(self, request: RetrievalRequest):
        """Send notification that retrieval is complete (placeholder)."""
        # Implementation would send email/SMS
        pass


if __name__ == "__main__":
    # Example usage
    from cold_storage import ColdStorageManager
    
    cold_storage = ColdStorageManager()
    service = RetrievalService(cold_storage)
    
    # Submit retrieval request
    request = service.submit_retrieval_request(
        data_id="INC-2024-001",
        priority=RetrievalPriority.STANDARD,
        requested_by="analyst@resilienceai.com",
        reason="Incident investigation",
        notification_email="analyst@resilienceai.com"
    )
    
    print(f"Retrieval request submitted: {request.request_id}")
    print(f"Estimated completion: {request.estimated_completion}")
    
    # Check status
    status = service.get_request_status(request.request_id)
    print(f"\nRequest status: {status}")
