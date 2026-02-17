"""
API Deprecation Management

Handles the deprecation lifecycle for API versions and features.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum


class DeprecationStage(Enum):
    """Deprecation lifecycle stages."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"  # Final warning period
    RETIRED = "retired"


@dataclass
class DeprecationNotice:
    """Deprecation notice configuration."""
    feature: str
    stage: DeprecationStage
    deprecated_date: datetime
    sunset_date: datetime
    replacement: Optional[str]
    migration_guide_url: str
    breaking_changes: List[str]
    notification_history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.notification_history is None:
            self.notification_history = []


class DeprecationManager:
    """
    Manages API deprecation lifecycle.
    
    Provides:
    - Deprecation registration
    - Header generation
    - Status checking
    - Notification tracking
    """
    
    # Standard deprecation warning period
    DEPRECATION_WARNING_MONTHS = 12
    
    # Sunset grace period (final warning)
    SUNSET_GRACE_PERIOD_DAYS = 90
    
    # Final warning period
    FINAL_WARNING_DAYS = 30
    
    def __init__(self):
        self.deprecations: Dict[str, DeprecationNotice] = {}
    
    def register_deprecation(
        self,
        feature: str,
        deprecated_date: datetime,
        replacement: Optional[str] = None,
        migration_guide_url: str = "",
        breaking_changes: List[str] = None
    ) -> DeprecationNotice:
        """
        Register a new deprecation notice.
        
        Args:
            feature: Feature or version being deprecated
            deprecated_date: Date when deprecation was announced
            replacement: Replacement feature or version
            migration_guide_url: URL to migration guide
            breaking_changes: List of breaking changes
            
        Returns:
            DeprecationNotice instance
        """
        sunset_date = deprecated_date + timedelta(
            days=self.DEPRECATION_WARNING_MONTHS * 30
        )
        
        notice = DeprecationNotice(
            feature=feature,
            stage=DeprecationStage.DEPRECATED,
            deprecated_date=deprecated_date,
            sunset_date=sunset_date,
            replacement=replacement,
            migration_guide_url=migration_guide_url,
            breaking_changes=breaking_changes or []
        )
        
        self.deprecations[feature] = notice
        return notice
    
    def get_deprecation(self, feature: str) -> Optional[DeprecationNotice]:
        """Get deprecation notice for a feature."""
        return self.deprecations.get(feature)
    
    def get_deprecation_headers(
        self,
        feature: str,
        request_version: str
    ) -> Dict[str, str]:
        """
        Generate deprecation headers for HTTP responses.
        
        Follows RFC 8594 for deprecation headers.
        
        Args:
            feature: Feature being deprecated
            request_version: API version of the request
            
        Returns:
            Dictionary of HTTP headers
        """
        headers = {}
        
        if feature in self.deprecations:
            notice = self.deprecations[feature]
            
            # Standard deprecation headers (RFC 8594)
            headers["Deprecation"] = notice.deprecated_date.strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )
            headers["Sunset"] = notice.sunset_date.strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )
            
            # Custom ResilienceAI headers
            headers["X-API-Deprecation-Stage"] = notice.stage.value
            headers["X-API-Deprecation-Feature"] = notice.feature
            
            if notice.replacement:
                headers["X-API-Deprecation-Replacement"] = notice.replacement
            
            if notice.migration_guide_url:
                headers["Link"] = f'<{notice.migration_guide_url}>; rel="migration"'
        
        return headers
    
    def check_version_status(self, version: str) -> Dict[str, Any]:
        """
        Check the deprecation status of an API version.
        
        Args:
            version: API version to check
            
        Returns:
            Status information
        """
        now = datetime.utcnow()
        
        # Find version-specific deprecations
        version_deprecations = [
            d for d in self.deprecations.values()
            if d.feature.startswith(f"v{version}") or d.feature == f"{version}-api"
        ]
        
        status = {
            "version": version,
            "status": "active",
            "warnings": [],
            "errors": [],
            "notifications_required": False
        }
        
        for deprecation in version_deprecations:
            days_until_sunset = (deprecation.sunset_date - now).days
            
            if days_until_sunset <= 0:
                status["status"] = "retired"
                status["errors"].append({
                    "feature": deprecation.feature,
                    "message": f"This version has been retired. Please migrate to {deprecation.replacement}",
                    "migration_guide": deprecation.migration_guide_url
                })
                status["notifications_required"] = True
                
            elif days_until_sunset <= self.FINAL_WARNING_DAYS:
                status["status"] = "critical"
                status["warnings"].append({
                    "feature": deprecation.feature,
                    "message": f"URGENT: This version will be retired in {days_until_sunset} days",
                    "sunset_date": deprecation.sunset_date.isoformat(),
                    "days_remaining": days_until_sunset
                })
                status["notifications_required"] = True
                
            elif days_until_sunset <= self.SUNSET_GRACE_PERIOD_DAYS:
                status["status"] = "warning"
                status["warnings"].append({
                    "feature": deprecation.feature,
                    "message": f"This version will be retired on {deprecation.sunset_date.strftime('%Y-%m-%d')}",
                    "sunset_date": deprecation.sunset_date.isoformat(),
                    "days_remaining": days_until_sunset,
                    "replacement": deprecation.replacement
                })
                status["notifications_required"] = True
                
            else:
                status["warnings"].append({
                    "feature": deprecation.feature,
                    "message": f"This version is deprecated and will be retired on {deprecation.sunset_date.strftime('%Y-%m-%d')}",
                    "replacement": deprecation.replacement
                })
        
        return status
    
    def record_notification(
        self,
        feature: str,
        channel: str,
        recipient: str,
        sent_at: Optional[datetime] = None
    ):
        """Record that a deprecation notification was sent."""
        if feature in self.deprecations:
            notice = self.deprecations[feature]
            notice.notification_history.append({
                "channel": channel,
                "recipient": recipient,
                "sent_at": (sent_at or datetime.utcnow()).isoformat()
            })
    
    def get_notification_summary(self, feature: str) -> Dict[str, Any]:
        """Get notification history summary for a feature."""
        notice = self.deprecations.get(feature)
        if not notice:
            return {"error": "Feature not found"}
        
        channels = {}
        for notification in notice.notification_history:
            channel = notification["channel"]
            if channel not in channels:
                channels[channel] = 0
            channels[channel] += 1
        
        return {
            "feature": feature,
            "total_notifications": len(notice.notification_history),
            "by_channel": channels,
            "last_notification": notice.notification_history[-1] if notice.notification_history else None
        }
    
    def get_all_deprecations(self) -> List[Dict[str, Any]]:
        """Get all registered deprecations."""
        return [
            {
                "feature": notice.feature,
                "stage": notice.stage.value,
                "deprecated_date": notice.deprecated_date.isoformat(),
                "sunset_date": notice.sunset_date.isoformat(),
                "replacement": notice.replacement,
                "days_until_sunset": (notice.sunset_date - datetime.utcnow()).days,
                "breaking_changes": notice.breaking_changes
            }
            for notice in self.deprecations.values()
        ]


# Global deprecation manager instance
deprecation_manager = DeprecationManager()

# Register V1 deprecation
deprecation_manager.register_deprecation(
    feature="v1-api",
    deprecated_date=datetime(2024, 1, 10),
    replacement="v2",
    migration_guide_url="https://docs.resilienceai.com/migration/v1-to-v2",
    breaking_changes=[
        "Field 'incident_id' renamed to 'id'",
        "Field 'created_at' renamed to 'created_timestamp'",
        "Severity values changed from strings to P-levels",
        "Timestamp format changed to ISO 8601"
    ]
)
