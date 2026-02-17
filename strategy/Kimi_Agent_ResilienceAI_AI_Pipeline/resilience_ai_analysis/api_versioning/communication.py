"""
Client Communication Management

Handles client communications for API versioning events.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import hmac
import json


class NotificationChannel(Enum):
    """Notification channels for client communication."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SLACK = "slack"
    SMS = "sms"


class NotificationType(Enum):
    """Types of version-related notifications."""
    DEPRECATION = "deprecation"
    SUNSET_WARNING = "sunset_warning"
    FINAL_WARNING = "final_warning"
    RETIREMENT = "retirement"
    NEW_VERSION = "new_version"
    BREAKING_CHANGE = "breaking_change"


@dataclass
class ClientNotification:
    """Client notification record."""
    client_id: str
    channel: NotificationChannel
    notification_type: NotificationType
    version: str
    sent_at: datetime
    opened_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    content: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookSubscription:
    """Webhook subscription configuration."""
    url: str
    events: List[str]
    secret: str
    registered_at: datetime
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    failure_count: int = 0


class ClientCommunicationManager:
    """
    Manages client communications for API versioning.
    
    Supports:
    - Email notifications
    - Webhook events
    - In-app notifications
    - Slack notifications
    """
    
    def __init__(self):
        self.notifications: List[ClientNotification] = []
        self.webhook_subscriptions: Dict[str, List[WebhookSubscription]] = {}
        self.email_templates: Dict[str, callable] = {}
        self.notification_preferences: Dict[str, Dict[str, Any]] = {}
    
    def register_webhook(
        self,
        client_id: str,
        webhook_url: str,
        events: List[str],
        secret: Optional[str] = None
    ):
        """
        Register a webhook for version-related events.
        
        Args:
            client_id: Client identifier
            webhook_url: Webhook endpoint URL
            events: List of events to subscribe to
            secret: Optional secret for signature verification
        """
        if client_id not in self.webhook_subscriptions:
            self.webhook_subscriptions[client_id] = []
        
        subscription = WebhookSubscription(
            url=webhook_url,
            events=events,
            secret=secret or self._generate_secret(),
            registered_at=datetime.utcnow()
        )
        
        self.webhook_subscriptions[client_id].append(subscription)
    
    def _generate_secret(self) -> str:
        """Generate a webhook secret."""
        return hashlib.sha256(
            datetime.utcnow().isoformat().encode()
        ).hexdigest()[:32]
    
    def set_notification_preferences(
        self,
        client_id: str,
        channels: List[NotificationChannel],
        email: Optional[str] = None,
        slack_webhook: Optional[str] = None
    ):
        """
        Set notification preferences for a client.
        
        Args:
            client_id: Client identifier
            channels: Preferred notification channels
            email: Email address for notifications
            slack_webhook: Slack webhook URL
        """
        self.notification_preferences[client_id] = {
            "channels": [c.value for c in channels],
            "email": email,
            "slack_webhook": slack_webhook,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def send_notification(
        self,
        client_id: str,
        notification_type: NotificationType,
        version: str,
        data: Dict[str, Any],
        channels: Optional[List[NotificationChannel]] = None
    ) -> Dict[str, Any]:
        """
        Send a notification to a client.
        
        Args:
            client_id: Client identifier
            notification_type: Type of notification
            version: API version related to notification
            data: Notification data
            channels: Optional override for channels
            
        Returns:
            Notification results
        """
        # Get client's preferred channels
        if channels is None:
            prefs = self.notification_preferences.get(client_id, {})
            channel_values = prefs.get("channels", [NotificationChannel.EMAIL.value])
            channels = [NotificationChannel(c) for c in channel_values]
        
        results = {
            "client_id": client_id,
            "notification_type": notification_type.value,
            "channels_attempted": [],
            "channels_succeeded": [],
            "channels_failed": []
        }
        
        for channel in channels:
            results["channels_attempted"].append(channel.value)
            
            try:
                if channel == NotificationChannel.WEBHOOK:
                    self._send_webhook_notification(client_id, notification_type, version, data)
                elif channel == NotificationChannel.EMAIL:
                    self._send_email_notification(client_id, notification_type, version, data)
                elif channel == NotificationChannel.SLACK:
                    self._send_slack_notification(client_id, notification_type, version, data)
                
                results["channels_succeeded"].append(channel.value)
                
                # Record notification
                self._record_notification(
                    client_id, channel, notification_type, version, data
                )
                
            except Exception as e:
                results["channels_failed"].append({
                    "channel": channel.value,
                    "error": str(e)
                })
        
        return results
    
    def _send_webhook_notification(
        self,
        client_id: str,
        notification_type: NotificationType,
        version: str,
        data: Dict[str, Any]
    ):
        """Send webhook notification."""
        import requests
        
        subscriptions = self.webhook_subscriptions.get(client_id, [])
        
        for subscription in subscriptions:
            if notification_type.value in subscription.events:
                payload = {
                    "event": notification_type.value,
                    "version": version,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": data
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "X-ResilienceAI-Event": notification_type.value,
                    "X-ResilienceAI-Signature": self._sign_payload(
                        payload, subscription.secret
                    )
                }
                
                try:
                    response = requests.post(
                        subscription.url,
                        json=payload,
                        headers=headers,
                        timeout=10
                    )
                    response.raise_for_status()
                    subscription.last_success = datetime.utcnow()
                    
                except Exception as e:
                    subscription.last_failure = datetime.utcnow()
                    subscription.failure_count += 1
                    raise e
    
    def _sign_payload(self, payload: Dict[str, Any], secret: str) -> str:
        """
        Sign webhook payload for verification.
        
        Args:
            payload: Webhook payload
            secret: Webhook secret
            
        Returns:
            HMAC signature
        """
        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _send_email_notification(
        self,
        client_id: str,
        notification_type: NotificationType,
        version: str,
        data: Dict[str, Any]
    ):
        """Send email notification."""
        prefs = self.notification_preferences.get(client_id, {})
        email = prefs.get("email")
        
        if not email:
            raise ValueError(f"No email configured for client {client_id}")
        
        # Generate email content
        subject, body, html = self._generate_email_content(
            notification_type, version, data
        )
        
        # Send email (integration with email service)
        # This is a placeholder - integrate with your email service
        print(f"Sending email to {email}: {subject}")
    
    def _generate_email_content(
        self,
        notification_type: NotificationType,
        version: str,
        data: Dict[str, Any]
    ) -> tuple:
        """Generate email content for notification type."""
        templates = {
            NotificationType.DEPRECATION: self._deprecation_email_template,
            NotificationType.SUNSET_WARNING: self._sunset_warning_email_template,
            NotificationType.FINAL_WARNING: self._final_warning_email_template,
            NotificationType.RETIREMENT: self._retirement_email_template,
        }
        
        template = templates.get(notification_type, self._default_email_template)
        return template(version, data)
    
    def _deprecation_email_template(self, version: str, data: Dict[str, Any]) -> tuple:
        """Generate deprecation email."""
        sunset_date = data.get("sunset_date", "TBD")
        replacement = data.get("replacement", "latest version")
        
        subject = f"Action Required: ResilienceAI API {version} Deprecation Notice"
        
        body = f"""
Dear ResilienceAI API User,

We are writing to inform you that API version {version} will be deprecated.

Key Dates:
- Deprecation Date: {data.get('deprecated_date', 'Now')}
- Sunset Date: {sunset_date}

What You Need to Do:
1. Review the migration guide: {data.get('migration_guide_url', '')}
2. Update your API calls to use {replacement}
3. Test your integration in our sandbox environment

Need Help?
- Migration Guide: {data.get('migration_guide_url', '')}
- Support: migration@resilienceai.com

Best regards,
The ResilienceAI Team
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head><title>API Deprecation Notice</title></head>
<body>
    <h1>API Version {version} Deprecation Notice</h1>
    <p>API version {version} will be deprecated on <strong>{sunset_date}</strong>.</p>
    <p>Please migrate to {replacement} as soon as possible.</p>
</body>
</html>
"""
        
        return subject, body, html
    
    def _sunset_warning_email_template(self, version: str, data: Dict[str, Any]) -> tuple:
        """Generate sunset warning email."""
        days_remaining = data.get("days_remaining", 0)
        
        subject = f"Warning: ResilienceAI API {version} Sunset in {days_remaining} Days"
        
        body = f"""
Dear ResilienceAI API User,

This is a reminder that API version {version} will be sunset in {days_remaining} days.

Please complete your migration to avoid service disruption.

Migration Guide: {data.get('migration_guide_url', '')}

Best regards,
The ResilienceAI Team
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head><title>Sunset Warning</title></head>
<body>
    <h1>API Version {version} Sunset Warning</h1>
    <p>Your API version will be retired in <strong>{days_remaining} days</strong>.</p>
</body>
</html>
"""
        
        return subject, body, html
    
    def _final_warning_email_template(self, version: str, data: Dict[str, Any]) -> tuple:
        """Generate final warning email."""
        days_remaining = data.get("days_remaining", 0)
        
        subject = f"URGENT: ResilienceAI API {version} Sunset in {days_remaining} Days"
        
        body = f"""
URGENT: API Version {version} Sunset Notice

Your integration is using ResilienceAI API {version}, which will be retired in {days_remaining} days.

IMMEDIATE ACTION REQUIRED:
1. Migrate to the latest version immediately
2. Test your integration
3. Deploy before the sunset date

After retirement, all {version} requests will return 410 Gone.

This is your final warning before API retirement.
"""
        
        return subject, body, ""
    
    def _retirement_email_template(self, version: str, data: Dict[str, Any]) -> tuple:
        """Generate retirement notice email."""
        subject = f"ResilienceAI API {version} Has Been Retired"
        
        body = f"""
API Version {version} Has Been Retired

As of today, ResilienceAI API {version} has been permanently retired.

All requests to {version} endpoints now return 410 Gone.

To restore service:
1. Update your API integration to the latest version
2. Follow the migration guide: {data.get('migration_guide_url', '')}
3. Contact support for assistance: migration@resilienceai.com

We apologize for any inconvenience and are here to help with your migration.
"""
        
        return subject, body, ""
    
    def _default_email_template(self, version: str, data: Dict[str, Any]) -> tuple:
        """Default email template."""
        return (
            f"ResilienceAI API {version} Notification",
            str(data),
            ""
        )
    
    def _send_slack_notification(
        self,
        client_id: str,
        notification_type: NotificationType,
        version: str,
        data: Dict[str, Any]
    ):
        """Send Slack notification."""
        prefs = self.notification_preferences.get(client_id, {})
        slack_webhook = prefs.get("slack_webhook")
        
        if not slack_webhook:
            raise ValueError(f"No Slack webhook configured for client {client_id}")
        
        import requests
        
        message = {
            "text": f"ResilienceAI API {version} - {notification_type.value}",
            "attachments": [{
                "color": "warning" if notification_type != NotificationType.RETIREMENT else "danger",
                "fields": [
                    {"title": "Version", "value": version, "short": True},
                    {"title": "Type", "value": notification_type.value, "short": True},
                    {"title": "Details", "value": json.dumps(data, indent=2), "short": False}
                ]
            }]
        }
        
        requests.post(slack_webhook, json=message, timeout=10)
    
    def _record_notification(
        self,
        client_id: str,
        channel: NotificationChannel,
        notification_type: NotificationType,
        version: str,
        content: Dict[str, Any]
    ):
        """Record a notification."""
        notification = ClientNotification(
            client_id=client_id,
            channel=channel,
            notification_type=notification_type,
            version=version,
            sent_at=datetime.utcnow(),
            content=content
        )
        
        self.notifications.append(notification)
    
    def get_client_notification_history(
        self,
        client_id: str,
        notification_type: Optional[NotificationType] = None,
        version: Optional[str] = None
    ) -> List[ClientNotification]:
        """
        Get notification history for a client.
        
        Args:
            client_id: Client identifier
            notification_type: Optional filter by type
            version: Optional filter by version
            
        Returns:
            List of notifications
        """
        notifications = [
            n for n in self.notifications
            if n.client_id == client_id
        ]
        
        if notification_type:
            notifications = [
                n for n in notifications
                if n.notification_type == notification_type
            ]
        
        if version:
            notifications = [
                n for n in notifications
                if n.version == version
            ]
        
        return notifications
    
    def get_notification_summary(self) -> Dict[str, Any]:
        """Get summary of all notifications sent."""
        summary = {
            "total_notifications": len(self.notifications),
            "by_channel": {},
            "by_type": {},
            "by_version": {}
        }
        
        for notification in self.notifications:
            channel = notification.channel.value
            notif_type = notification.notification_type.value
            version = notification.version
            
            summary["by_channel"][channel] = summary["by_channel"].get(channel, 0) + 1
            summary["by_type"][notif_type] = summary["by_type"].get(notif_type, 0) + 1
            summary["by_version"][version] = summary["by_version"].get(version, 0) + 1
        
        return summary


# Webhook event types
WEBHOOK_EVENTS = {
    "api_version.deprecated": "API version has been deprecated",
    "api_version.sunset_warning": "Sunset warning for API version",
    "api_version.final_warning": "Final warning before API retirement",
    "api_version.retired": "API version has been retired",
    "api_version.released": "New API version released",
    "api_version.breaking_change": "Breaking change announced"
}
