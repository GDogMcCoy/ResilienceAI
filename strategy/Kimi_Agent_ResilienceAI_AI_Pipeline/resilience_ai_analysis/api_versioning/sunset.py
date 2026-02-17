"""
API Version Sunset Management

Handles the sunset lifecycle for retired API versions.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException

from .versions import APIVersion, VERSION_REGISTRY


class SunsetManager:
    """
    Manages API version sunset lifecycle.
    
    Provides:
    - Sunset scheduling
    - Status checking
    - Header generation
    - Enforcement (410 Gone)
    """
    
    # Warning thresholds
    SUNSET_WARNING_DAYS = 90
    FINAL_WARNING_DAYS = 30
    CRITICAL_WARNING_DAYS = 7
    
    def __init__(self):
        self.sunset_schedule: Dict[APIVersion, Dict[str, Any]] = {}
    
    def schedule_sunset(
        self,
        version: APIVersion,
        sunset_date: datetime,
        replacement_version: APIVersion,
        notification_schedule: Optional[List[int]] = None
    ):
        """
        Schedule a version for sunset.
        
        Args:
            version: API version to sunset
            sunset_date: Date when version will be retired
            replacement_version: Version to migrate to
            notification_schedule: Days before sunset to send notifications
        """
        if notification_schedule is None:
            notification_schedule = [365, 180, 90, 30, 7, 1]
        
        self.sunset_schedule[version] = {
            "date": sunset_date,
            "replacement": replacement_version,
            "notification_schedule": notification_schedule,
            "notifications_sent": [],
            "scheduled_at": datetime.utcnow()
        }
    
    def check_sunset_status(self, version: APIVersion) -> Dict[str, Any]:
        """
        Check sunset status for a version.
        
        Args:
            version: API version to check
            
        Returns:
            Sunset status information
        """
        now = datetime.utcnow()
        version_info = VERSION_REGISTRY.get(version)
        
        if not version_info or not version_info.sunset_date:
            return {
                "version": version.value,
                "status": "active",
                "sunset_scheduled": False
            }
        
        days_until_sunset = (version_info.sunset_date - now).days
        
        if days_until_sunset <= 0:
            return {
                "version": version.value,
                "status": "retired",
                "sunset_scheduled": True,
                "days_overdue": abs(days_until_sunset),
                "action_required": "Migrate immediately",
                "migration_url": version_info.migration_guide_url,
                "latest_version": APIVersion.get_latest().value
            }
        
        elif days_until_sunset <= self.CRITICAL_WARNING_DAYS:
            return {
                "version": version.value,
                "status": "critical",
                "sunset_scheduled": True,
                "days_remaining": days_until_sunset,
                "action_required": f"URGENT: Migrate within {days_until_sunset} days",
                "migration_url": version_info.migration_guide_url,
                "latest_version": APIVersion.get_latest().value
            }
        
        elif days_until_sunset <= self.FINAL_WARNING_DAYS:
            return {
                "version": version.value,
                "status": "final_warning",
                "sunset_scheduled": True,
                "days_remaining": days_until_sunset,
                "action_required": f"CRITICAL: Migrate within {days_until_sunset} days",
                "migration_url": version_info.migration_guide_url,
                "latest_version": APIVersion.get_latest().value
            }
        
        elif days_until_sunset <= self.SUNSET_WARNING_DAYS:
            return {
                "version": version.value,
                "status": "warning",
                "sunset_scheduled": True,
                "days_remaining": days_until_sunset,
                "action_required": "Plan migration soon",
                "migration_url": version_info.migration_guide_url,
                "latest_version": APIVersion.get_latest().value
            }
        
        else:
            return {
                "version": version.value,
                "status": "deprecated",
                "sunset_scheduled": True,
                "days_remaining": days_until_sunset,
                "action_required": "Monitor for updates",
                "migration_url": version_info.migration_guide_url,
                "latest_version": APIVersion.get_latest().value
            }
    
    def get_sunset_headers(self, version: APIVersion) -> Dict[str, str]:
        """
        Get sunset-related headers for HTTP responses.
        
        Args:
            version: API version
            
        Returns:
            Dictionary of HTTP headers
        """
        status = self.check_sunset_status(version)
        headers = {}
        
        if status["sunset_scheduled"]:
            version_info = VERSION_REGISTRY.get(version)
            if version_info and version_info.sunset_date:
                headers["Sunset"] = version_info.sunset_date.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                )
                headers["X-API-Sunset-Status"] = status["status"]
                headers["X-API-Sunset-Days-Remaining"] = str(
                    status.get("days_remaining", 0)
                )
                
                if version_info.migration_guide_url:
                    headers["Link"] = (
                        f'<{version_info.migration_guide_url}>; rel="migration"'
                    )
        
        return headers
    
    def enforce_sunset(self, version: APIVersion):
        """
        Enforce sunset - raise 410 Gone for retired versions.
        
        Args:
            version: API version to check
            
        Raises:
            HTTPException: 410 Gone if version is retired
        """
        status = self.check_sunset_status(version)
        
        if status["status"] == "retired":
            version_info = VERSION_REGISTRY.get(version)
            
            detail = {
                "error": "Gone",
                "message": f"API version {version.value} has been retired",
                "retired_date": version_info.sunset_date.isoformat() if version_info and version_info.sunset_date else None,
                "latest_version": APIVersion.get_latest().value,
                "support_email": "migration@resilienceai.com"
            }
            
            headers = {
                "Sunset": version_info.sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT") if version_info and version_info.sunset_date else "",
            }
            
            if version_info and version_info.migration_guide_url:
                headers["Link"] = f'<{version_info.migration_guide_url}>; rel="migration"'
                detail["migration_guide"] = version_info.migration_guide_url
            
            raise HTTPException(
                status_code=410,
                detail=detail,
                headers=headers
            )
    
    def should_send_notification(self, version: APIVersion) -> Optional[Dict[str, Any]]:
        """
        Check if a notification should be sent for a version.
        
        Args:
            version: API version to check
            
        Returns:
            Notification info or None
        """
        status = self.check_sunset_status(version)
        
        if not status["sunset_scheduled"]:
            return None
        
        days_remaining = status.get("days_remaining", 0)
        
        # Check if we're at a notification threshold
        schedule = self.sunset_schedule.get(version, {}).get(
            "notification_schedule",
            [365, 180, 90, 30, 7, 1]
        )
        
        notifications_sent = self.sunset_schedule.get(version, {}).get(
            "notifications_sent",
            []
        )
        
        for threshold in schedule:
            if days_remaining <= threshold and threshold not in notifications_sent:
                return {
                    "version": version.value,
                    "days_remaining": days_remaining,
                    "threshold": threshold,
                    "urgency": self._get_urgency(days_remaining),
                    "status": status["status"]
                }
        
        return None
    
    def _get_urgency(self, days_remaining: int) -> str:
        """Get urgency level based on days remaining."""
        if days_remaining <= self.CRITICAL_WARNING_DAYS:
            return "critical"
        elif days_remaining <= self.FINAL_WARNING_DAYS:
            return "high"
        elif days_remaining <= self.SUNSET_WARNING_DAYS:
            return "medium"
        return "low"
    
    def record_notification_sent(
        self,
        version: APIVersion,
        threshold: int,
        channel: str
    ):
        """Record that a notification was sent."""
        if version in self.sunset_schedule:
            self.sunset_schedule[version]["notifications_sent"].append({
                "threshold": threshold,
                "channel": channel,
                "sent_at": datetime.utcnow().isoformat()
            })
    
    def get_sunset_summary(self) -> Dict[str, Any]:
        """Get summary of all scheduled sunsets."""
        summary = {
            "total_scheduled": len(self.sunset_schedule),
            "by_status": {},
            "upcoming_notifications": []
        }
        
        for version, schedule in self.sunset_schedule.items():
            status = self.check_sunset_status(version)
            status_name = status["status"]
            
            if status_name not in summary["by_status"]:
                summary["by_status"][status_name] = []
            
            summary["by_status"][status_name].append({
                "version": version.value,
                "sunset_date": schedule["date"].isoformat(),
                "replacement": schedule["replacement"].value,
                "days_remaining": status.get("days_remaining", 0)
            })
            
            # Check for upcoming notifications
            notification = self.should_send_notification(version)
            if notification:
                summary["upcoming_notifications"].append(notification)
        
        return summary


# Global sunset manager instance
sunset_manager = SunsetManager()

# Configure sunset for V1
sunset_manager.schedule_sunset(
    version=APIVersion.V1,
    sunset_date=datetime(2025, 6, 30),
    replacement_version=APIVersion.V2,
    notification_schedule=[365, 180, 90, 30, 14, 7, 1]
)
