"""
Backup Policies Configuration for ResilienceAI Disaster Recovery
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class BackupType(Enum):
    """Types of backup operations."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    CONTINUOUS = "continuous"
    SNAPSHOT = "snapshot"


class RetentionPolicy(Enum):
    """Backup retention policies."""
    DAILY_7 = "daily_7"          # Keep 7 daily backups
    WEEKLY_4 = "weekly_4"        # Keep 4 weekly backups
    MONTHLY_12 = "monthly_12"    # Keep 12 monthly backups
    YEARLY_7 = "yearly_7"        # Keep 7 yearly backups


@dataclass
class BackupPolicy:
    """Defines a backup policy configuration."""
    name: str
    backup_type: BackupType
    frequency: str              # cron expression
    retention: RetentionPolicy
    encryption: bool = True
    compression: bool = True
    cross_region: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.backup_type.value,
            "frequency": self.frequency,
            "retention": self.retention.value,
            "encryption": self.encryption,
            "compression": self.compression,
            "cross_region": self.cross_region
        }


# Define backup policies for different data types
BACKUP_POLICIES: Dict[str, BackupPolicy] = {
    "database": BackupPolicy(
        name="database_backup",
        backup_type=BackupType.CONTINUOUS,
        frequency="*/5 * * * *",  # Every 5 minutes
        retention=RetentionPolicy.DAILY_7,
        encryption=True,
        cross_region=True
    ),
    "models": BackupPolicy(
        name="model_artifacts",
        backup_type=BackupType.INCREMENTAL,
        frequency="0 */6 * * *",  # Every 6 hours
        retention=RetentionPolicy.WEEKLY_4,
        encryption=True,
        cross_region=True
    ),
    "configuration": BackupPolicy(
        name="config_backup",
        backup_type=BackupType.FULL,
        frequency="0 * * * *",  # Every hour
        retention=RetentionPolicy.DAILY_7,
        encryption=True,
        cross_region=True
    ),
    "logs": BackupPolicy(
        name="log_backup",
        backup_type=BackupType.INCREMENTAL,
        frequency="0 */2 * * *",  # Every 2 hours
        retention=RetentionPolicy.MONTHLY_12,
        encryption=True,
        cross_region=False
    ),
    "user_data": BackupPolicy(
        name="user_data_backup",
        backup_type=BackupType.CONTINUOUS,
        frequency="*/1 * * * *",  # Every minute
        retention=RetentionPolicy.DAILY_7,
        encryption=True,
        cross_region=True
    )
}


def get_policy(name: str) -> Optional[BackupPolicy]:
    """Get a backup policy by name."""
    return BACKUP_POLICIES.get(name)


def list_policies() -> Dict[str, BackupPolicy]:
    """List all backup policies."""
    return BACKUP_POLICIES.copy()


__all__ = [
    'BackupPolicy',
    'BackupType',
    'RetentionPolicy',
    'BACKUP_POLICIES',
    'get_policy',
    'list_policies'
]
