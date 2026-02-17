"""
API Version Analytics

Provides analytics and monitoring for API version usage.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


@dataclass
class VersionMetrics:
    """Metrics for an API version."""
    version: str
    total_requests: int = 0
    unique_clients: Set[str] = field(default_factory=set)
    endpoints: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    error_rates: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    response_times: List[float] = field(default_factory=list)
    last_seen: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    
    def add_request(
        self,
        client_id: str,
        endpoint: str,
        status_code: int,
        response_time_ms: float
    ):
        """Record a request metric."""
        self.total_requests += 1
        self.unique_clients.add(client_id)
        self.endpoints[endpoint] += 1
        self.error_rates[status_code] += 1
        self.response_times.append(response_time_ms)
        
        now = datetime.utcnow()
        self.last_seen = now
        if self.first_seen is None:
            self.first_seen = now
    
    def get_avg_response_time(self) -> float:
        """Get average response time."""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    def get_p95_response_time(self) -> float:
        """Get 95th percentile response time."""
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else max(self.response_times)
    
    def get_error_rate(self) -> float:
        """Get error rate percentage."""
        if self.total_requests == 0:
            return 0.0
        error_count = sum(
            count for code, count in self.error_rates.items()
            if code >= 400
        )
        return (error_count / self.total_requests) * 100


class VersionAnalytics:
    """
    Analytics collection for API versions.
    
    Tracks:
    - Request volume by version
    - Client adoption
    - Error rates
    - Response times
    - Migration progress
    """
    
    def __init__(self):
        self.metrics: Dict[str, VersionMetrics] = {}
        self.hourly_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(int))
        self.daily_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(int))
        self.client_versions: Dict[str, Set[str]] = defaultdict(set)
    
    def record_request(
        self,
        version: str,
        client_id: str,
        endpoint: str,
        status_code: int,
        response_time_ms: float
    ):
        """
        Record a request for analytics.
        
        Args:
            version: API version used
            client_id: Client identifier
            endpoint: API endpoint accessed
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
        """
        # Initialize metrics for version if needed
        if version not in self.metrics:
            self.metrics[version] = VersionMetrics(version=version)
        
        # Record metrics
        self.metrics[version].add_request(
            client_id, endpoint, status_code, response_time_ms
        )
        
        # Track client version usage
        self.client_versions[client_id].add(version)
        
        # Record hourly stats
        hour_key = datetime.utcnow().strftime("%Y-%m-%d-%H")
        self.hourly_stats[hour_key][version] += 1
        
        # Record daily stats
        day_key = datetime.utcnow().strftime("%Y-%m-%d")
        self.daily_stats[day_key][version] += 1
    
    def get_version_adoption(self) -> Dict[str, Any]:
        """
        Get version adoption statistics.
        
        Returns:
            Adoption statistics
        """
        total_requests = sum(m.total_requests for m in self.metrics.values())
        total_clients = len(self.client_versions)
        
        adoption = {}
        for version, metrics in self.metrics.items():
            adoption[version] = {
                "requests": metrics.total_requests,
                "percentage": (
                    (metrics.total_requests / total_requests * 100)
                    if total_requests > 0 else 0
                ),
                "unique_clients": len(metrics.unique_clients),
                "client_percentage": (
                    (len(metrics.unique_clients) / total_clients * 100)
                    if total_clients > 0 else 0
                ),
                "avg_response_time_ms": round(metrics.get_avg_response_time(), 2),
                "p95_response_time_ms": round(metrics.get_p95_response_time(), 2),
                "error_rate": round(metrics.get_error_rate(), 2),
                "last_seen": (
                    metrics.last_seen.isoformat()
                    if metrics.last_seen else None
                ),
                "first_seen": (
                    metrics.first_seen.isoformat()
                    if metrics.first_seen else None
                )
            }
        
        # Calculate adoption velocity
        latest_version = max(adoption.keys()) if adoption else None
        latest_adoption = adoption.get(latest_version, {}).get("percentage", 0)
        
        return {
            "total_requests": total_requests,
            "total_clients": total_clients,
            "versions": adoption,
            "latest_version_adoption": round(latest_adoption, 2),
            "adoption_velocity": self._calculate_adoption_velocity(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_adoption_velocity(self) -> Dict[str, float]:
        """Calculate adoption velocity (change per day)."""
        if len(self.daily_stats) < 2:
            return {"daily_change": 0.0}
        
        # Get last two days
        days = sorted(self.daily_stats.keys())[-2:]
        if len(days) < 2:
            return {"daily_change": 0.0}
        
        day1, day2 = days
        total1 = sum(self.daily_stats[day1].values())
        total2 = sum(self.daily_stats[day2].values())
        
        if total1 == 0:
            return {"daily_change": 0.0}
        
        daily_change = ((total2 - total1) / total1) * 100
        
        return {"daily_change": round(daily_change, 2)}
    
    def get_deprecated_version_usage(self) -> List[Dict[str, Any]]:
        """
        Get usage statistics for deprecated versions.
        
        Returns:
            List of deprecated version usage stats
        """
        deprecated = []
        
        # List of deprecated versions
        deprecated_versions = ["v1"]  # Update as needed
        
        for version in deprecated_versions:
            metrics = self.metrics.get(version)
            if not metrics:
                continue
            
            # Get top endpoints
            top_endpoints = sorted(
                metrics.endpoints.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            deprecated.append({
                "version": version,
                "requests_24h": self._get_requests_last_24h(version),
                "total_requests": metrics.total_requests,
                "unique_clients": len(metrics.unique_clients),
                "top_endpoints": [
                    {"endpoint": ep, "requests": count}
                    for ep, count in top_endpoints
                ],
                "clients_to_migrate": list(metrics.unique_clients),
                "estimated_migration_effort": self._estimate_migration_effort(
                    metrics.total_requests,
                    len(metrics.unique_clients)
                ),
                "last_activity": (
                    metrics.last_seen.isoformat()
                    if metrics.last_seen else None
                )
            })
        
        return deprecated
    
    def _get_requests_last_24h(self, version: str) -> int:
        """Get request count for version in last 24 hours."""
        now = datetime.utcnow()
        yesterday = now - timedelta(hours=24)
        
        count = 0
        for hour_key, stats in self.hourly_stats.items():
            hour_time = datetime.strptime(hour_key, "%Y-%m-%d-%H")
            if yesterday <= hour_time <= now:
                count += stats.get(version, 0)
        
        return count
    
    def _estimate_migration_effort(
        self,
        request_volume: int,
        client_count: int
    ) -> Dict[str, Any]:
        """
        Estimate migration effort for deprecated version users.
        
        Args:
            request_volume: Total request volume
            client_count: Number of unique clients
            
        Returns:
            Migration effort estimate
        """
        if request_volume < 1000 and client_count < 5:
            effort = "low"
            estimated_days = 7
            priority = "low"
        elif request_volume < 10000 and client_count < 20:
            effort = "medium"
            estimated_days = 30
            priority = "medium"
        else:
            effort = "high"
            estimated_days = 90
            priority = "high"
        
        return {
            "level": effort,
            "estimated_days": estimated_days,
            "priority": priority,
            "recommendation": f"Allocate {estimated_days} days for migration"
        }
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive migration report.
        
        Returns:
            Migration report
        """
        deprecated_usage = self.get_deprecated_version_usage()
        
        total_deprecated_requests = sum(
            d["requests_24h"] for d in deprecated_usage
        )
        total_clients_to_migrate = sum(
            len(d["clients_to_migrate"]) for d in deprecated_usage
        )
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_deprecated_requests_24h": total_deprecated_requests,
                "total_clients_to_migrate": total_clients_to_migrate,
                "overall_risk": self._calculate_migration_risk(deprecated_usage),
                "estimated_completion": self._estimate_completion_date(
                    deprecated_usage
                )
            },
            "deprecated_versions": deprecated_usage,
            "recommendations": self._generate_recommendations(deprecated_usage),
            "client_breakdown": self._get_client_breakdown()
        }
    
    def _calculate_migration_risk(
        self,
        deprecated_usage: List[Dict[str, Any]]
    ) -> str:
        """
        Calculate overall migration risk level.
        
        Args:
            deprecated_usage: List of deprecated version usage stats
            
        Returns:
            Risk level: "critical", "high", "medium", or "low"
        """
        total_requests = sum(d.get("requests_24h", 0) for d in deprecated_usage)
        total_clients = sum(len(d.get("clients_to_migrate", [])) for d in deprecated_usage)
        
        if total_requests > 100000 or total_clients > 50:
            return "critical"
        elif total_requests > 10000 or total_clients > 20:
            return "high"
        elif total_requests > 1000 or total_clients > 5:
            return "medium"
        return "low"
    
    def _estimate_completion_date(
        self,
        deprecated_usage: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Estimate when migration will be complete."""
        if not deprecated_usage:
            return None
        
        max_days = max(
            d["estimated_migration_effort"]["estimated_days"]
            for d in deprecated_usage
        )
        
        completion_date = datetime.utcnow() + timedelta(days=max_days)
        return completion_date.strftime("%Y-%m-%d")
    
    def _generate_recommendations(
        self,
        deprecated_usage: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate migration recommendations."""
        recommendations = []
        
        total_requests = sum(d.get("requests_24h", 0) for d in deprecated_usage)
        
        if total_requests > 10000:
            recommendations.append({
                "priority": "high",
                "action": "Schedule direct outreach to top 10 API consumers",
                "rationale": "High volume of deprecated API usage"
            })
        
        recommendations.append({
            "priority": "medium",
            "action": "Enable enhanced deprecation headers for all deprecated version responses",
            "rationale": "Increase visibility of deprecation warnings"
        })
        
        recommendations.append({
            "priority": "medium",
            "action": "Schedule office hours for migration support",
            "rationale": "Provide direct assistance to migrating clients"
        })
        
        return recommendations
    
    def _get_client_breakdown(self) -> Dict[str, Any]:
        """Get breakdown of clients by version usage."""
        multi_version_clients = 0
        single_version_clients = 0
        
        for client_id, versions in self.client_versions.items():
            if len(versions) > 1:
                multi_version_clients += 1
            else:
                single_version_clients += 1
        
        return {
            "total_clients": len(self.client_versions),
            "multi_version_clients": multi_version_clients,
            "single_version_clients": single_version_clients,
            "migration_in_progress": multi_version_clients
        }
    
    def get_trending_data(self, days: int = 7) -> Dict[str, Any]:
        """
        Get trending data for the specified number of days.
        
        Args:
            days: Number of days to include
            
        Returns:
            Trending data
        """
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)
        
        trend_data = defaultdict(lambda: defaultdict(int))
        
        for day_key, stats in self.daily_stats.items():
            day_time = datetime.strptime(day_key, "%Y-%m-%d")
            if start_date <= day_time <= now:
                for version, count in stats.items():
                    trend_data[day_key][version] = count
        
        return {
            "period_days": days,
            "data": dict(trend_data),
            "versions": list(self.metrics.keys())
        }


# Global analytics instance
version_analytics = VersionAnalytics()
