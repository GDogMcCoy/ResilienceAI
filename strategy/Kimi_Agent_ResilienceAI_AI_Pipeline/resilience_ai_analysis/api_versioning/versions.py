"""
API Version Registry and Metadata

This module defines the supported API versions and their metadata.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


class APIVersion(str, Enum):
    """Supported API versions for ResilienceAI."""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"  # Future version placeholder
    
    @classmethod
    def get_latest(cls) -> "APIVersion":
        """Get the latest stable API version."""
        return cls.V2
    
    @classmethod
    def get_supported(cls) -> list:
        """Get list of supported API versions."""
        return [cls.V1, cls.V2]
    
    @classmethod
    def get_active(cls) -> list:
        """Get list of active (non-deprecated) API versions."""
        return [
            v for v in cls.get_supported()
            if VERSION_REGISTRY.get(v) and VERSION_REGISTRY[v].status == "active"
        ]
    
    @classmethod
    def get_deprecated(cls) -> list:
        """Get list of deprecated API versions."""
        return [
            v for v in cls.get_supported()
            if VERSION_REGISTRY.get(v) and VERSION_REGISTRY[v].status == "deprecated"
        ]


@dataclass
class VersionInfo:
    """Version metadata and lifecycle information."""
    version: APIVersion
    release_date: datetime
    status: str  # "active", "deprecated", "sunset", "retired"
    sunset_date: Optional[datetime]
    documentation_url: str
    changelog_url: str
    breaking_changes: list = None
    migration_guide_url: str = ""
    
    def __post_init__(self):
        if self.breaking_changes is None:
            self.breaking_changes = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version.value,
            "release_date": self.release_date.isoformat(),
            "status": self.status,
            "sunset_date": self.sunset_date.isoformat() if self.sunset_date else None,
            "documentation_url": self.documentation_url,
            "changelog_url": self.changelog_url,
            "breaking_changes": self.breaking_changes,
            "migration_guide_url": self.migration_guide_url
        }


# Version registry with metadata for all API versions
VERSION_REGISTRY: Dict[APIVersion, VersionInfo] = {
    APIVersion.V1: VersionInfo(
        version=APIVersion.V1,
        release_date=datetime(2023, 1, 15),
        status="deprecated",
        sunset_date=datetime(2025, 6, 30),
        documentation_url="/docs/api/v1",
        changelog_url="/docs/api/v1/changelog",
        breaking_changes=[
            "Field 'incident_id' renamed to 'id' in V2",
            "Field 'created_at' renamed to 'created_timestamp' in V2",
            "Severity values changed from strings ('low', 'medium', 'high', 'critical') to P-levels ('P4', 'P3', 'P2', 'P1')",
            "Timestamp format changed to ISO 8601"
        ],
        migration_guide_url="/docs/migration/v1-to-v2"
    ),
    APIVersion.V2: VersionInfo(
        version=APIVersion.V2,
        release_date=datetime(2024, 1, 10),
        status="active",
        sunset_date=None,
        documentation_url="/docs/api/v2",
        changelog_url="/docs/api/v2/changelog",
        breaking_changes=[],
        migration_guide_url=""
    ),
    APIVersion.V3: VersionInfo(
        version=APIVersion.V3,
        release_date=datetime(2025, 1, 1),  # Planned
        status="preview",  # Future version in preview
        sunset_date=None,
        documentation_url="/docs/api/v3",
        changelog_url="/docs/api/v3/changelog",
        breaking_changes=[],
        migration_guide_url=""
    )
}


def get_version_info(version: APIVersion) -> Optional[VersionInfo]:
    """Get metadata for a specific API version."""
    return VERSION_REGISTRY.get(version)


def is_version_supported(version: APIVersion) -> bool:
    """Check if a version is supported."""
    return version in VERSION_REGISTRY and VERSION_REGISTRY[version].status != "retired"


def is_version_deprecated(version: APIVersion) -> bool:
    """Check if a version is deprecated."""
    info = VERSION_REGISTRY.get(version)
    return info is not None and info.status == "deprecated"


def get_version_lifecycle(version: APIVersion) -> Dict[str, Any]:
    """Get complete lifecycle information for a version."""
    info = VERSION_REGISTRY.get(version)
    if not info:
        return {"error": "Version not found"}
    
    now = datetime.utcnow()
    
    lifecycle = {
        "version": version.value,
        "current_status": info.status,
        "release_date": info.release_date.isoformat(),
    }
    
    if info.sunset_date:
        days_until_sunset = (info.sunset_date - now).days
        lifecycle["sunset_date"] = info.sunset_date.isoformat()
        lifecycle["days_until_sunset"] = max(0, days_until_sunset)
        lifecycle["is_sunset"] = days_until_sunset <= 0
    
    return lifecycle
