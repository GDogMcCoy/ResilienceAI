# /mnt/okcomputer/output/resilience_ai_analysis/code/archival_policy.py
"""
Archival Policy Engine for ResilienceAI
Manages archival policies and evaluates data for archival.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Callable
from enum import Enum
import hashlib


class ArchivalTrigger(Enum):
    """Archival trigger types."""
    TIME_BASED = "time_based"
    ACCESS_BASED = "access_based"
    SIZE_BASED = "size_based"
    EVENT_BASED = "event_based"
    COMPOSITE = "composite"


@dataclass
class ArchivalCriteria:
    """Criteria for determining when data should be archived."""
    min_age_days: Optional[int] = None
    max_size_mb: Optional[int] = None
    last_accessed_days: Optional[int] = None
    custom_condition: Optional[Callable] = None
    priority: int = 5  # 1-10, lower = higher priority


@dataclass
class ArchivalPolicy:
    """Complete archival policy definition."""
    name: str
    data_category: str
    trigger: ArchivalTrigger
    source_tier: str
    target_tier: str
    criteria: ArchivalCriteria
    compression_enabled: bool
    encryption_enabled: bool
    metadata_preservation: bool
    verification_required: bool
    
    def should_archive(self, data_metadata: dict) -> bool:
        """Determine if data meets archival criteria."""
        if self.criteria.min_age_days:
            age_days = (datetime.now() - 
                       datetime.fromisoformat(data_metadata['created_at'])).days
            if age_days < self.criteria.min_age_days:
                return False
        
        if self.criteria.max_size_mb:
            size_mb = data_metadata.get('size_bytes', 0) / (1024 * 1024)
            if size_mb > self.criteria.max_size_mb:
                return True  # Large files archive immediately
        
        if self.criteria.last_accessed_days:
            last_access = datetime.fromisoformat(data_metadata.get('last_accessed', 
                                                                   data_metadata['created_at']))
            days_since_access = (datetime.now() - last_access).days
            if days_since_access < self.criteria.last_accessed_days:
                return False
        
        if self.criteria.custom_condition:
            return self.criteria.custom_condition(data_metadata)
        
        return True


class ArchivalPolicyEngine:
    """Engine for managing and executing archival policies."""
    
    def __init__(self):
        self.policies: List[ArchivalPolicy] = []
        self.archival_history: List[dict] = []
    
    def register_policy(self, policy: ArchivalPolicy):
        """Register a new archival policy."""
        self.policies.append(policy)
        self.policies.sort(key=lambda p: p.criteria.priority)
    
    def evaluate_data(self, data_id: str, data_metadata: dict) -> Optional[ArchivalPolicy]:
        """Evaluate data against all policies and return matching policy."""
        for policy in self.policies:
            if policy.should_archive(data_metadata):
                return policy
        return None
    
    def get_default_policies(self) -> List[ArchivalPolicy]:
        """Get default archival policies for ResilienceAI."""
        return [
            ArchivalPolicy(
                name="incident_data_archival",
                data_category="incident_data",
                trigger=ArchivalTrigger.TIME_BASED,
                source_tier="hot",
                target_tier="cold",
                criteria=ArchivalCriteria(min_age_days=90, priority=3),
                compression_enabled=True,
                encryption_enabled=True,
                metadata_preservation=True,
                verification_required=True
            ),
            ArchivalPolicy(
                name="sensor_telemetry_archival",
                data_category="sensor_telemetry",
                trigger=ArchivalTrigger.COMPOSITE,
                source_tier="hot",
                target_tier="cold",
                criteria=ArchivalCriteria(
                    min_age_days=30,
                    last_accessed_days=7,
                    priority=4
                ),
                compression_enabled=True,
                encryption_enabled=True,
                metadata_preservation=True,
                verification_required=True
            ),
            ArchivalPolicy(
                name="large_file_immediate_archival",
                data_category="any",
                trigger=ArchivalTrigger.SIZE_BASED,
                source_tier="hot",
                target_tier="cold",
                criteria=ArchivalCriteria(max_size_mb=1024, priority=1),
                compression_enabled=True,
                encryption_enabled=True,
                metadata_preservation=True,
                verification_required=True
            ),
            ArchivalPolicy(
                name="audit_log_archival",
                data_category="audit_logs",
                trigger=ArchivalTrigger.TIME_BASED,
                source_tier="warm",
                target_tier="frozen",
                criteria=ArchivalCriteria(min_age_days=90, priority=2),
                compression_enabled=True,
                encryption_enabled=True,
                metadata_preservation=True,
                verification_required=True
            ),
            ArchivalPolicy(
                name="old_data_glacier",
                data_category="any",
                trigger=ArchivalTrigger.TIME_BASED,
                source_tier="cold",
                target_tier="frozen",
                criteria=ArchivalCriteria(min_age_days=2555, priority=5),  # 7 years
                compression_enabled=True,
                encryption_enabled=True,
                metadata_preservation=True,
                verification_required=True
            )
        ]


if __name__ == "__main__":
    # Example usage
    engine = ArchivalPolicyEngine()
    
    # Register default policies
    for policy in engine.get_default_policies():
        engine.register_policy(policy)
    
    # Evaluate sample data
    sample_data = {
        "data_id": "INC-2024-001",
        "created_at": (datetime.now() - timedelta(days=100)).isoformat(),
        "last_accessed": (datetime.now() - timedelta(days=10)).isoformat(),
        "size_bytes": 1024 * 1024 * 50,  # 50MB
        "category": "incident_data"
    }
    
    matching_policy = engine.evaluate_data("INC-2024-001", sample_data)
    if matching_policy:
        print(f"Data should be archived using policy: {matching_policy.name}")
        print(f"Target tier: {matching_policy.target_tier}")
    else:
        print("No archival policy matched")
