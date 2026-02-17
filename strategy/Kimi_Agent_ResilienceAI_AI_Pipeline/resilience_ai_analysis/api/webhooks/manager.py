"""
Webhook Management System for ResilienceAI
Supports event-driven notifications for vulnerability alerts

File: src/api/webhooks/manager.py
"""
import asyncio
import hashlib
import hmac
import json
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid

import aiohttp
from aiohttp import ClientTimeout

# Optional Redis support
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class WebhookEvent(Enum):
    """Webhook event types"""
    VULNERABILITY_ALERT = "vulnerability.alert"
    WEATHER_ALERT = "weather.alert"
    CLIMATE_THRESHOLD = "climate.threshold"
    DATA_UPDATE = "data.update"
    PREDICTION_READY = "prediction.ready"
    INTERVENTION_RECOMMENDED = "intervention.recommended"


@dataclass
class WebhookSubscription:
    """Webhook subscription configuration"""
    id: str
    url: str
    events: List[str]
    secret: Optional[str]  # For HMAC signature
    headers: Dict[str, str]
    created_at: datetime
    last_delivered: Optional[datetime]
    delivery_count: int
    failure_count: int
    is_active: bool
    
    # Filtering
    county_fips: Optional[str] = None
    min_severity: Optional[str] = None
    state: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "url": self.url,
            "events": self.events,
            "headers": self.headers,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "county_fips": self.county_fips,
            "min_severity": self.min_severity,
            "state": self.state
        }


@dataclass
class WebhookDelivery:
    """Webhook delivery attempt record"""
    id: str
    subscription_id: str
    event: str
    payload: Dict
    attempted_at: datetime
    response_status: Optional[int]
    response_body: Optional[str]
    success: bool
    retry_count: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "subscription_id": self.subscription_id,
            "event": self.event,
            "attempted_at": self.attempted_at.isoformat(),
            "response_status": self.response_status,
            "success": self.success,
            "retry_count": self.retry_count
        }


class WebhookManager:
    """
    Manages webhook subscriptions and deliveries
    Features: Retry logic, HMAC signatures, delivery tracking, filtering
    
    Usage:
        async with WebhookManager() as manager:
            sub = await manager.create_subscription(
                url="https://example.com/webhook",
                events=["vulnerability.alert"]
            )
            await manager.trigger_event(
                WebhookEvent.VULNERABILITY_ALERT,
                {"county_fips": "29189", "risk_level": "high"}
            )
    """
    
    def __init__(self, redis_url: str = None):
        self.redis = None
        if redis_url and REDIS_AVAILABLE:
            self.redis = aioredis.from_url(redis_url)
        
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delays = [5, 30, 300]  # seconds
        
        # Failure threshold
        self.max_failures = 100
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=ClientTimeout(total=30)
        )
        
        # Load subscriptions from Redis if available
        if self.redis:
            await self._load_subscriptions()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
        if self.redis:
            await self.redis.close()
    
    async def _load_subscriptions(self):
        """Load subscriptions from Redis"""
        if not self.redis:
            return
        
        subs_data = await self.redis.hgetall("webhooks:subscriptions")
        for sub_id, sub_json in subs_data.items():
            try:
                data = json.loads(sub_json)
                self.subscriptions[sub_id] = WebhookSubscription(
                    id=data["id"],
                    url=data["url"],
                    events=data["events"],
                    secret=data.get("secret"),
                    headers=data.get("headers", {}),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    last_delivered=datetime.fromisoformat(data["last_delivered"]) if data.get("last_delivered") else None,
                    delivery_count=data.get("delivery_count", 0),
                    failure_count=data.get("failure_count", 0),
                    is_active=data.get("is_active", True),
                    county_fips=data.get("county_fips"),
                    min_severity=data.get("min_severity"),
                    state=data.get("state")
                )
            except Exception as e:
                print(f"Error loading subscription {sub_id}: {e}")
    
    async def create_subscription(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
        headers: Dict[str, str] = None,
        county_fips: Optional[str] = None,
        min_severity: Optional[str] = None,
        state: Optional[str] = None
    ) -> WebhookSubscription:
        """
        Create new webhook subscription
        
        Args:
            url: Webhook endpoint URL
            events: List of event types to subscribe to
            secret: Optional secret for HMAC signature
            headers: Optional custom headers
            county_fips: Optional county filter
            min_severity: Optional minimum severity filter
            state: Optional state filter
        """
        subscription = WebhookSubscription(
            id=str(uuid.uuid4()),
            url=url,
            events=events,
            secret=secret,
            headers=headers or {},
            created_at=datetime.utcnow(),
            last_delivered=None,
            delivery_count=0,
            failure_count=0,
            is_active=True,
            county_fips=county_fips,
            min_severity=min_severity,
            state=state
        )
        
        # Store subscription
        self.subscriptions[subscription.id] = subscription
        
        if self.redis:
            await self.redis.hset(
                "webhooks:subscriptions",
                subscription.id,
                json.dumps(self._subscription_to_dict(subscription))
            )
        
        return subscription
    
    async def delete_subscription(self, subscription_id: str) -> bool:
        """Delete webhook subscription"""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            
            if self.redis:
                await self.redis.hdel("webhooks:subscriptions", subscription_id)
            
            return True
        return False
    
    async def get_subscription(self, subscription_id: str) -> Optional[WebhookSubscription]:
        """Get subscription by ID"""
        return self.subscriptions.get(subscription_id)
    
    async def list_subscriptions(
        self,
        event_type: Optional[str] = None,
        county_fips: Optional[str] = None,
        active_only: bool = True
    ) -> List[WebhookSubscription]:
        """List subscriptions with optional filtering"""
        subs = self.subscriptions.values()
        
        if active_only:
            subs = [s for s in subs if s.is_active]
        
        if event_type:
            subs = [s for s in subs if event_type in s.events]
        
        if county_fips:
            subs = [s for s in subs if s.county_fips == county_fips or s.county_fips is None]
        
        return list(subs)
    
    async def trigger_event(
        self,
        event: WebhookEvent,
        payload: Dict,
        county_fips: Optional[str] = None,
        severity: Optional[str] = None,
        state: Optional[str] = None
    ) -> List[WebhookDelivery]:
        """
        Trigger event to all matching subscriptions
        
        Args:
            event: Event type
            payload: Event data
            county_fips: County FIPS for filtering
            severity: Severity level for filtering
            state: State code for filtering
            
        Returns:
            List of delivery results
        """
        # Find matching subscriptions
        matching = [
            sub for sub in self.subscriptions.values()
            if sub.is_active
            and event.value in sub.events
            and self._matches_filters(sub, county_fips, severity, state)
        ]
        
        # Deliver to all matching subscriptions concurrently
        tasks = [
            self._deliver_webhook(sub, event, payload)
            for sub in matching
        ]
        
        deliveries = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            d if not isinstance(d, Exception) else None
            for d in deliveries
        ]
    
    def _matches_filters(
        self,
        sub: WebhookSubscription,
        county_fips: Optional[str],
        severity: Optional[str],
        state: Optional[str]
    ) -> bool:
        """Check if subscription matches event filters"""
        # County filter
        if sub.county_fips and sub.county_fips != county_fips:
            return False
        
        # State filter
        if sub.state and sub.state != state:
            return False
        
        # Severity filter
        if sub.min_severity and severity:
            severity_order = ["minimal", "low", "moderate", "high", "critical"]
            try:
                if severity_order.index(severity) < severity_order.index(sub.min_severity):
                    return False
            except ValueError:
                pass
        
        return True
    
    async def _deliver_webhook(
        self,
        subscription: WebhookSubscription,
        event: WebhookEvent,
        payload: Dict
    ) -> WebhookDelivery:
        """Deliver webhook with retry logic"""
        delivery_id = str(uuid.uuid4())
        
        # Build webhook payload
        webhook_payload = {
            "event": event.value,
            "timestamp": datetime.utcnow().isoformat(),
            "subscription_id": subscription.id,
            "data": payload
        }
        
        # Add signature if secret configured
        headers = dict(subscription.headers)
        headers["Content-Type"] = "application/json"
        headers["X-Webhook-Event"] = event.value
        headers["X-Webhook-ID"] = delivery_id
        headers["X-Webhook-Timestamp"] = str(int(datetime.utcnow().timestamp()))
        
        if subscription.secret:
            signature = self._generate_signature(
                subscription.secret,
                json.dumps(webhook_payload, sort_keys=True)
            )
            headers["X-Webhook-Signature"] = signature
        
        # Attempt delivery with retries
        delivery = None
        for attempt, delay in enumerate([0] + self.retry_delays):
            if attempt > 0:
                await asyncio.sleep(delay)
            
            try:
                async with self._session.post(
                    subscription.url,
                    json=webhook_payload,
                    headers=headers
                ) as response:
                    success = 200 <= response.status < 300
                    
                    delivery = WebhookDelivery(
                        id=delivery_id,
                        subscription_id=subscription.id,
                        event=event.value,
                        payload=webhook_payload,
                        attempted_at=datetime.utcnow(),
                        response_status=response.status,
                        response_body=await response.text() if not success else None,
                        success=success,
                        retry_count=attempt
                    )
                    
                    if success:
                        subscription.last_delivered = datetime.utcnow()
                        subscription.delivery_count += 1
                        break
                    else:
                        subscription.failure_count += 1
                        
            except Exception as e:
                delivery = WebhookDelivery(
                    id=delivery_id,
                    subscription_id=subscription.id,
                    event=event.value,
                    payload=webhook_payload,
                    attempted_at=datetime.utcnow(),
                    response_status=None,
                    response_body=str(e),
                    success=False,
                    retry_count=attempt
                )
                subscription.failure_count += 1
        
        # Store delivery record
        await self._store_delivery(delivery)
        
        # Update subscription in Redis
        if self.redis:
            await self.redis.hset(
                "webhooks:subscriptions",
                subscription.id,
                json.dumps(self._subscription_to_dict(subscription))
            )
        
        # Disable subscription if too many failures
        if subscription.failure_count > self.max_failures:
            subscription.is_active = False
            print(f"Disabled webhook {subscription.id} due to excessive failures")
        
        return delivery
    
    def _generate_signature(self, secret: str, payload: str) -> str:
        """Generate HMAC signature for webhook"""
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    async def _store_delivery(self, delivery: WebhookDelivery):
        """Store delivery record"""
        if self.redis:
            # Store in list with TTL
            await self.redis.lpush(
                f"webhooks:deliveries:{delivery.subscription_id}",
                json.dumps(delivery.to_dict())
            )
            # Trim to last 100 deliveries
            await self.redis.ltrim(f"webhooks:deliveries:{delivery.subscription_id}", 0, 99)
            # Set expiration on list
            await self.redis.expire(
                f"webhooks:deliveries:{delivery.subscription_id}",
                86400 * 30  # 30 days
            )
    
    async def get_delivery_history(
        self,
        subscription_id: str,
        limit: int = 100
    ) -> List[WebhookDelivery]:
        """Get delivery history for subscription"""
        if not self.redis:
            return []
        
        deliveries_data = await self.redis.lrange(
            f"webhooks:deliveries:{subscription_id}",
            0,
            limit - 1
        )
        
        deliveries = []
        for data in deliveries_data:
            try:
                d = json.loads(data)
                deliveries.append(WebhookDelivery(
                    id=d["id"],
                    subscription_id=d["subscription_id"],
                    event=d["event"],
                    payload=d.get("payload", {}),
                    attempted_at=datetime.fromisoformat(d["attempted_at"]),
                    response_status=d.get("response_status"),
                    response_body=d.get("response_body"),
                    success=d["success"],
                    retry_count=d["retry_count"]
                ))
            except Exception as e:
                print(f"Error parsing delivery: {e}")
        
        return deliveries
    
    def _subscription_to_dict(self, sub: WebhookSubscription) -> Dict:
        """Convert subscription to dictionary"""
        return {
            "id": sub.id,
            "url": sub.url,
            "events": sub.events,
            "secret": sub.secret,
            "headers": sub.headers,
            "created_at": sub.created_at.isoformat(),
            "last_delivered": sub.last_delivered.isoformat() if sub.last_delivered else None,
            "delivery_count": sub.delivery_count,
            "failure_count": sub.failure_count,
            "is_active": sub.is_active,
            "county_fips": sub.county_fips,
            "min_severity": sub.min_severity,
            "state": sub.state
        }
    
    async def get_stats(self) -> Dict:
        """Get webhook statistics"""
        total = len(self.subscriptions)
        active = sum(1 for s in self.subscriptions.values() if s.is_active)
        total_deliveries = sum(s.delivery_count for s in self.subscriptions.values())
        total_failures = sum(s.failure_count for s in self.subscriptions.values())
        
        return {
            "total_subscriptions": total,
            "active_subscriptions": active,
            "total_deliveries": total_deliveries,
            "total_failures": total_failures,
            "success_rate": (
                (total_deliveries - total_failures) / total_deliveries * 100
                if total_deliveries > 0 else 0
            )
        }


# Event builder helpers
class WebhookEventBuilder:
    """Helper class for building webhook event payloads"""
    
    @staticmethod
    def vulnerability_alert(
        county_fips: str,
        county_name: str,
        previous_risk: str,
        current_risk: str,
        risk_score: float,
        factors: List[str]
    ) -> Dict:
        """Build vulnerability alert payload"""
        return {
            "county_fips": county_fips,
            "county_name": county_name,
            "alert_type": "vulnerability_change",
            "previous_risk": previous_risk,
            "current_risk": current_risk,
            "risk_score": risk_score,
            "factors": factors,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def weather_alert(
        alert_id: str,
        county_fips: str,
        event: str,
        severity: str,
        headline: str,
        description: str
    ) -> Dict:
        """Build weather alert payload"""
        return {
            "alert_id": alert_id,
            "county_fips": county_fips,
            "event": event,
            "severity": severity,
            "headline": headline,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def data_update(
        data_source: str,
        update_type: str,
        affected_counties: List[str],
        changes: Dict
    ) -> Dict:
        """Build data update payload"""
        return {
            "data_source": data_source,
            "update_type": update_type,
            "affected_counties": affected_counties,
            "changes": changes,
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    async def test_webhooks():
        async with WebhookManager() as manager:
            # Create subscription
            sub = await manager.create_subscription(
                url="https://httpbin.org/post",
                events=["vulnerability.alert", "weather.alert"],
                county_fips="29189",
                min_severity="high"
            )
            print(f"Created subscription: {sub.id}")
            
            # Trigger event
            payload = WebhookEventBuilder.vulnerability_alert(
                county_fips="29189",
                county_name="St. Louis County",
                previous_risk="moderate",
                current_risk="high",
                risk_score=75.5,
                factors=["Increased poverty rate", "Healthcare access decline"]
            )
            
            deliveries = await manager.trigger_event(
                WebhookEvent.VULNERABILITY_ALERT,
                payload,
                county_fips="29189",
                severity="high",
                state="MO"
            )
            
            print(f"Deliveries: {len(deliveries)}")
            for d in deliveries:
                if d:
                    print(f"  Success: {d.success}, Status: {d.response_status}")
            
            # Get stats
            stats = await manager.get_stats()
            print(f"Stats: {stats}")
    
    asyncio.run(test_webhooks())
