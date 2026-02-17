"""
Async NOAA Weather Client with Circuit Breaker and Caching
Enhanced version of weather_client.py with async support

File: src/api/clients/async_weather_client.py
"""
import asyncio
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
from aiohttp import ClientTimeout

# Import gateway if available
try:
    from src.api.gateway import APIGateway, CircuitBreakerOpen, RateLimitExceeded
    GATEWAY_AVAILABLE = True
except ImportError:
    GATEWAY_AVAILABLE = False


@dataclass
class WeatherAlert:
    """Represents a NOAA weather alert"""
    id: str
    event: str
    severity: str
    certainty: str
    urgency: str
    headline: str
    description: str
    instruction: Optional[str]
    area_desc: str
    affected_counties: List[str]
    effective: datetime
    expires: datetime
    sender: str
    
    # Severity weights for risk correlation
    SEVERITY_WEIGHTS = {
        'Extreme': 1.0,
        'Severe': 0.8,
        'Moderate': 0.5,
        'Minor': 0.2,
        'Unknown': 0.0
    }
    
    @classmethod
    def from_noaa(cls, feature: Dict) -> "WeatherAlert":
        """Create WeatherAlert from NOAA API feature"""
        props = feature.get("properties", {})
        area_desc = props.get("areaDesc", "")
        
        # Parse dates
        effective_str = props.get("effective", "")
        expires_str = props.get("expires", "")
        
        try:
            effective = datetime.fromisoformat(effective_str.replace("Z", "+00:00"))
        except:
            effective = datetime.utcnow()
        
        try:
            expires = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
        except:
            expires = datetime.utcnow()
        
        return cls(
            id=feature.get("id", ""),
            event=props.get("event", "Unknown"),
            severity=props.get("severity", "Unknown"),
            certainty=props.get("certainty", "Unknown"),
            urgency=props.get("urgency", "Unknown"),
            headline=props.get("headline", ""),
            description=props.get("description", ""),
            instruction=props.get("instruction"),
            area_desc=area_desc,
            affected_counties=[c.strip() for c in area_desc.split(";") if c.strip()],
            effective=effective,
            expires=expires,
            sender=props.get("senderName", "")
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'event': self.event,
            'severity': self.severity,
            'certainty': self.certainty,
            'urgency': self.urgency,
            'headline': self.headline,
            'description': self.description,
            'instruction': self.instruction,
            'area_desc': self.area_desc,
            'affected_counties': self.affected_counties,
            'effective': self.effective.isoformat(),
            'expires': self.expires.isoformat(),
            'sender': self.sender
        }
    
    def get_severity_weight(self) -> float:
        """Get numeric severity weight for risk correlation"""
        return self.SEVERITY_WEIGHTS.get(self.severity, 0.0)
    
    def is_expired(self) -> bool:
        """Check if alert has expired"""
        return datetime.utcnow() > self.expires
    
    def time_until_expires(self) -> timedelta:
        """Get time remaining until expiration"""
        return self.expires - datetime.utcnow()


class AsyncNOAAWeatherClient:
    """
    Async NOAA Weather Service Client
    Features: Circuit breaker, caching, rate limiting, batch requests
    
    Usage:
        async with AsyncNOAAWeatherClient() as client:
            alerts = await client.get_active_alerts(state="MO")
    """
    
    BASE_URL = "https://api.weather.gov"
    
    # Events relevant to vulnerability assessment
    RELEVANT_EVENTS = {
        'Flood Warning', 'Flood Watch', 'Flash Flood Warning',
        'Severe Thunderstorm Warning', 'Severe Thunderstorm Watch',
        'Tornado Warning', 'Tornado Watch',
        'Winter Storm Warning', 'Winter Storm Watch',
        'Hurricane Warning', 'Hurricane Watch', 'Hurricane Local Statement',
        'Heat Advisory', 'Excessive Heat Warning', 'Excessive Heat Watch',
        'Drought', 'Extreme Fire Danger', 'Red Flag Warning',
        'High Wind Warning', 'High Wind Watch'
    }
    
    def __init__(self, gateway=None):
        self.gateway = gateway
        self._session: Optional[aiohttp.ClientSession] = None
        self._cached_alerts: Dict[str, tuple] = {}  # (alerts, timestamp)
    
    async def __aenter__(self):
        if not self.gateway or not GATEWAY_AVAILABLE:
            self._session = aiohttp.ClientSession(
                timeout=ClientTimeout(total=30),
                headers={
                    "User-Agent": "ResilienceAI/2.0 (async)",
                    "Accept": "application/geo+json"
                }
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def get_active_alerts(
        self,
        state: Optional[str] = None,
        severity: Optional[str] = None,
        event: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 60
    ) -> List[WeatherAlert]:
        """
        Get active weather alerts with filtering
        
        Args:
            state: Two-letter state code
            severity: Minimum severity level
            event: Specific event type
            use_cache: Whether to use cached results
            cache_ttl: Cache TTL in seconds
        """
        params = {}
        if state:
            params["area"] = state
        if severity:
            params["severity"] = severity
        if event:
            params["event"] = event
        
        # Check local cache
        cache_key = f"alerts:{state}:{severity}:{event}"
        if use_cache and cache_key in self._cached_alerts:
            alerts, timestamp = self._cached_alerts[cache_key]
            if datetime.utcnow().timestamp() - timestamp < cache_ttl:
                return [a for a in alerts if not a.is_expired()]
        
        try:
            if self.gateway and GATEWAY_AVAILABLE:
                result = await self.gateway.request(
                    service="noaa",
                    method="GET",
                    url=f"{self.BASE_URL}/alerts/active",
                    params=params,
                    cache_ttl=cache_ttl,
                    rate_limit_key="noaa"
                )
                data = result["data"]
            else:
                async with self._session.get(
                    f"{self.BASE_URL}/alerts/active",
                    params=params
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            features = data.get("features", [])
            alerts = [WeatherAlert.from_noaa(f) for f in features]
            
            # Filter to relevant events
            alerts = [a for a in alerts if a.event in self.RELEVANT_EVENTS]
            
            # Update cache
            if use_cache:
                self._cached_alerts[cache_key] = (alerts, datetime.utcnow().timestamp())
            
            return alerts
            
        except CircuitBreakerOpen:
            # Return cached alerts if circuit is open
            if cache_key in self._cached_alerts:
                alerts, _ = self._cached_alerts[cache_key]
                return [a for a in alerts if not a.is_expired()]
            return []
        except RateLimitExceeded:
            # Implement exponential backoff
            await asyncio.sleep(1)
            return await self.get_active_alerts(
                state, severity, event, use_cache=False
            )
    
    async def get_alerts_for_counties(
        self,
        county_names: List[str],
        state: str
    ) -> Dict[str, List[WeatherAlert]]:
        """
        Get alerts for multiple counties efficiently
        Uses batching to minimize API calls
        
        Args:
            county_names: List of county names
            state: State code
            
        Returns:
            Dict mapping county names to their alerts
        """
        # Get all alerts for state
        all_alerts = await self.get_active_alerts(state=state)
        
        # Group by county
        county_alerts: Dict[str, List[WeatherAlert]] = {
            name: [] for name in county_names
        }
        
        for alert in all_alerts:
            for county in county_names:
                if county.lower() in alert.area_desc.lower():
                    county_alerts[county].append(alert)
        
        return county_alerts
    
    async def get_alert_summary(
        self,
        state: str
    ) -> Dict[str, Any]:
        """
        Get summary of active alerts for state
        
        Args:
            state: State code
            
        Returns:
            Summary dict with counts and affected areas
        """
        alerts = await self.get_active_alerts(state=state)
        
        summary = {
            "total_alerts": len(alerts),
            "by_severity": {},
            "by_event": {},
            "highest_severity": None,
            "affected_counties": set(),
            "total_population_at_risk": 0  # Would need population data
        }
        
        for alert in alerts:
            # Count by severity
            summary["by_severity"][alert.severity] = summary["by_severity"].get(alert.severity, 0) + 1
            
            # Count by event
            summary["by_event"][alert.event] = summary["by_event"].get(alert.event, 0) + 1
            
            # Track affected counties
            summary["affected_counties"].update(alert.affected_counties)
        
        # Determine highest severity
        severity_order = ["Extreme", "Severe", "Moderate", "Minor", "Unknown"]
        for sev in severity_order:
            if sev in summary["by_severity"]:
                summary["highest_severity"] = sev
                break
        
        summary["affected_counties"] = sorted(list(summary["affected_counties"]))
        
        # Calculate risk score
        total_weight = sum(
            a.get_severity_weight() for a in alerts
        )
        summary["aggregate_risk_score"] = min(total_weight * 10, 100)
        
        return summary
    
    async def get_alerts_by_severity(
        self,
        min_severity: str = "Moderate",
        state: Optional[str] = None
    ) -> List[WeatherAlert]:
        """
        Get alerts with minimum severity level
        
        Args:
            min_severity: Minimum severity (Extreme, Severe, Moderate, Minor)
            state: Optional state filter
        """
        severity_order = ["Extreme", "Severe", "Moderate", "Minor", "Unknown"]
        min_index = severity_order.index(min_severity) if min_severity in severity_order else 2
        
        alerts = await self.get_active_alerts(state=state)
        
        return [
            a for a in alerts
            if severity_order.index(a.severity) <= min_index
        ]
    
    async def stream_alerts(
        self,
        state: str,
        poll_interval: int = 60
    ):
        """
        Async generator that yields alert updates
        For use with WebSocket subscriptions
        
        Args:
            state: State to monitor
            poll_interval: Seconds between polls
            
        Yields:
            Dict with new, expired, and all alerts
        """
        last_alert_ids: Set[str] = set()
        
        while True:
            try:
                alerts = await self.get_active_alerts(state=state)
                current_ids = {a.id for a in alerts}
                
                # Find new alerts
                new_ids = current_ids - last_alert_ids
                new_alerts = [a for a in alerts if a.id in new_ids]
                
                # Find expired alerts
                expired_ids = last_alert_ids - current_ids
                
                if new_alerts or expired_ids:
                    yield {
                        "timestamp": datetime.utcnow().isoformat(),
                        "new": [a.to_dict() for a in new_alerts],
                        "expired": list(expired_ids),
                        "all": [a.to_dict() for a in alerts],
                        "summary": {
                            "total": len(alerts),
                            "new_count": len(new_alerts),
                            "expired_count": len(expired_ids)
                        }
                    }
                
                last_alert_ids = current_ids
                
            except Exception as e:
                # Log error but continue polling
                print(f"Error polling alerts: {e}")
            
            await asyncio.sleep(poll_interval)
    
    async def get_zone_forecast(self, zone_id: str) -> Dict[str, Any]:
        """
        Get forecast for a specific NWS zone
        
        Args:
            zone_id: NWS zone identifier (e.g., "MOZ063")
        """
        url = f"{self.BASE_URL}/zones/forecast/{zone_id}/forecast"
        
        try:
            if self.gateway and GATEWAY_AVAILABLE:
                result = await self.gateway.request(
                    service="noaa",
                    method="GET",
                    url=url,
                    cache_ttl=3600  # 1 hour cache for forecasts
                )
                return result["data"]
            else:
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def get_point_forecast(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get forecast for a specific point
        
        Args:
            latitude: Point latitude
            longitude: Point longitude
        """
        # First get the grid point
        points_url = f"{self.BASE_URL}/points/{latitude},{longitude}"
        
        try:
            async with self._session.get(points_url) as response:
                response.raise_for_status()
                point_data = await response.json()
            
            # Get forecast from grid point
            forecast_url = point_data.get("properties", {}).get("forecast")
            if forecast_url:
                async with self._session.get(forecast_url) as response:
                    response.raise_for_status()
                    return await response.json()
            
            return {"error": "No forecast URL found"}
            
        except Exception as e:
            return {"error": str(e)}


# Backward compatibility wrapper
class NOAAWeatherClientSync:
    """
    Synchronous wrapper for AsyncNOAAWeatherClient
    Maintains compatibility with existing code
    """
    
    def __init__(self):
        self._client = None
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)
    
    def get_active_alerts(
        self,
        state: str = None,
        severity: str = None,
        event: str = None
    ) -> List[WeatherAlert]:
        """Synchronous wrapper"""
        async def _get():
            async with AsyncNOAAWeatherClient() as client:
                return await client.get_active_alerts(state, severity, event)
        
        return self._run_async(_get())
    
    def get_alert_summary(self, state: str) -> Dict[str, Any]:
        """Synchronous wrapper"""
        async def _get():
            async with AsyncNOAAWeatherClient() as client:
                return await client.get_alert_summary(state)
        
        return self._run_async(_get())


if __name__ == "__main__":
    # Test the client
    async def test_client():
        async with AsyncNOAAWeatherClient() as client:
            # Test alerts
            alerts = await client.get_active_alerts(state="MO")
            print(f"Found {len(alerts)} alerts for Missouri")
            
            if alerts:
                alert = alerts[0]
                print(f"\nFirst alert: {alert.headline}")
                print(f"Severity: {alert.severity}")
                print(f"Affects: {', '.join(alert.affected_counties[:3])}")
            
            # Test summary
            summary = await client.get_alert_summary("MO")
            print(f"\nAlert Summary:")
            print(f"  Total: {summary['total_alerts']}")
            print(f"  By severity: {summary['by_severity']}")
            print(f"  Highest severity: {summary['highest_severity']}")
    
    asyncio.run(test_client())
