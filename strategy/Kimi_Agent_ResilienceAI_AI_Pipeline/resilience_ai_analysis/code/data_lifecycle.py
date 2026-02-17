# /mnt/okcomputer/output/resilience_ai_analysis/code/data_lifecycle.py
"""
Data Lifecycle Management for ResilienceAI
Manages data transitions between storage tiers based on age and access patterns.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, List
import json


class StorageTier(Enum):
    """Storage tier enumeration."""
    HOT = "hot"           # Primary SSD - Active data
    WARM = "warm"         # SSD Cache - Recently accessed
    COLD = "cold"         # Object Storage - Infrequently accessed
    FROZEN = "frozen"     # Glacier - Archive only
    DELETED = "deleted"   # Marked for deletion


class DataCategory(Enum):
    """Data category enumeration."""
    INCIDENT_DATA = "incident_data"
    SENSOR_TELEMETRY = "sensor_telemetry"
    AI_MODEL_OUTPUTS = "ai_model_outputs"
    USER_ACTIVITY = "user_activity"
    AUDIT_LOGS = "audit_logs"
    SYSTEM_METRICS = "system_metrics"
    TRAINING_DATA = "training_data"
    COMPLIANCE_REPORTS = "compliance_reports"


@dataclass
class RetentionPolicy:
    """Retention policy for a data category."""
    category: DataCategory
    hot_days: int
    warm_days: int
    cold_days: int
    frozen_years: int
    compliance_requirement: str
    encryption_required: bool
    
    def get_tier_for_age(self, age_days: int) -> StorageTier:
        """Determine appropriate storage tier based on data age."""
        if age_days <= self.hot_days:
            return StorageTier.HOT
        elif age_days <= self.hot_days + self.warm_days:
            return StorageTier.WARM
        elif age_days <= self.hot_days + self.warm_days + self.cold_days:
            return StorageTier.COLD
        elif age_days <= (self.hot_days + self.warm_days + self.cold_days + 
                         (self.frozen_years * 365)):
            return StorageTier.FROZEN
        else:
            return StorageTier.DELETED


# Define retention policies for each data category
RETENTION_POLICIES: Dict[DataCategory, RetentionPolicy] = {
    DataCategory.INCIDENT_DATA: RetentionPolicy(
        category=DataCategory.INCIDENT_DATA,
        hot_days=30,
        warm_days=60,
        cold_days=2555,  # ~7 years
        frozen_years=10,
        compliance_requirement="SOX/ISO27001 - 7 years minimum",
        encryption_required=True
    ),
    DataCategory.SENSOR_TELEMETRY: RetentionPolicy(
        category=DataCategory.SENSOR_TELEMETRY,
        hot_days=30,
        warm_days=60,
        cold_days=995,  # ~2.7 years
        frozen_years=3,
        compliance_requirement="Operational - 3 years",
        encryption_required=True
    ),
    DataCategory.AI_MODEL_OUTPUTS: RetentionPolicy(
        category=DataCategory.AI_MODEL_OUTPUTS,
        hot_days=30,
        warm_days=60,
        cold_days=3650,  # ~10 years
        frozen_years=10,
        compliance_requirement="AI Governance - 10 years",
        encryption_required=True
    ),
    DataCategory.USER_ACTIVITY: RetentionPolicy(
        category=DataCategory.USER_ACTIVITY,
        hot_days=30,
        warm_days=60,
        cold_days=635,  # ~1.7 years
        frozen_years=0,  # Delete after cold
        compliance_requirement="GDPR - 2 years maximum",
        encryption_required=True
    ),
    DataCategory.AUDIT_LOGS: RetentionPolicy(
        category=DataCategory.AUDIT_LOGS,
        hot_days=30,
        warm_days=60,
        cold_days=2555,
        frozen_years=10,
        compliance_requirement="SOX/ISO27001 - 7 years minimum",
        encryption_required=True
    ),
    DataCategory.SYSTEM_METRICS: RetentionPolicy(
        category=DataCategory.SYSTEM_METRICS,
        hot_days=30,
        warm_days=60,
        cold_days=0,
        frozen_years=0,
        compliance_requirement="Operational - 90 days",
        encryption_required=False
    ),
    DataCategory.TRAINING_DATA: RetentionPolicy(
        category=DataCategory.TRAINING_DATA,
        hot_days=30,
        warm_days=60,
        cold_days=36500,  # ~100 years
        frozen_years=100,
        compliance_requirement="AI Governance - Permanent",
        encryption_required=True
    ),
    DataCategory.COMPLIANCE_REPORTS: RetentionPolicy(
        category=DataCategory.COMPLIANCE_REPORTS,
        hot_days=30,
        warm_days=60,
        cold_days=3650,
        frozen_years=10,
        compliance_requirement="Regulatory - 10 years",
        encryption_required=True
    )
}


class DataLifecycleManager:
    """Manages data lifecycle transitions and retention policies."""
    
    def __init__(self):
        self.policies = RETENTION_POLICIES
        self.transition_history: List[Dict] = []
    
    def evaluate_data_tier(self, data_id: str, category: DataCategory, 
                          created_at: datetime, last_accessed: datetime,
                          current_tier: StorageTier) -> StorageTier:
        """Evaluate if data should transition to a different tier."""
        age_days = (datetime.now() - created_at).days
        policy = self.policies[category]
        recommended_tier = policy.get_tier_for_age(age_days)
        
        # Check access patterns for warm data
        if current_tier == StorageTier.WARM:
            days_since_access = (datetime.now() - last_accessed).days
            if days_since_access < 7:  # Recently accessed
                return StorageTier.HOT  # Promote back to hot
        
        return recommended_tier
    
    def schedule_transition(self, data_id: str, from_tier: StorageTier, 
                           to_tier: StorageTier, scheduled_time: datetime):
        """Schedule a data tier transition."""
        transition = {
            "data_id": data_id,
            "from_tier": from_tier.value,
            "to_tier": to_tier.value,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "scheduled"
        }
        self.transition_history.append(transition)
        return transition
    
    def get_compliance_status(self, category: DataCategory) -> Dict:
        """Get compliance status for a data category."""
        policy = self.policies[category]
        return {
            "category": category.value,
            "retention_hot_days": policy.hot_days,
            "retention_warm_days": policy.warm_days,
            "retention_cold_days": policy.cold_days,
            "retention_frozen_years": policy.frozen_years,
            "compliance_requirement": policy.compliance_requirement,
            "encryption_required": policy.encryption_required,
            "total_retention_days": (policy.hot_days + policy.warm_days + 
                                    policy.cold_days + (policy.frozen_years * 365))
        }


if __name__ == "__main__":
    # Example usage
    manager = DataLifecycleManager()
    
    # Check compliance status for incident data
    status = manager.get_compliance_status(DataCategory.INCIDENT_DATA)
    print(f"Incident Data Compliance: {json.dumps(status, indent=2)}")
    
    # Evaluate data tier for 100-day old incident data
    from datetime import datetime, timedelta
    created = datetime.now() - timedelta(days=100)
    last_accessed = datetime.now() - timedelta(days=20)
    
    recommended_tier = manager.evaluate_data_tier(
        "INC-001", DataCategory.INCIDENT_DATA,
        created, last_accessed, StorageTier.HOT
    )
    print(f"Recommended tier for 100-day old incident: {recommended_tier.value}")
