"""
Failover Controller for ResilienceAI Disaster Recovery
Manages automated and manual failover operations between regions.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
import aiohttp
import boto3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FailoverStatus(Enum):
    """Failover operation status."""
    HEALTHY = auto()
    DEGRADED = auto()
    FAILOVER_IN_PROGRESS = auto()
    FAILOVER_COMPLETE = auto()
    FAILBACK_IN_PROGRESS = auto()
    ERROR = auto()


class FailoverTrigger(Enum):
    """Failover trigger types."""
    MANUAL = "manual"
    HEALTH_CHECK_FAILED = "health_check_failed"
    HIGH_ERROR_RATE = "high_error_rate"
    HIGH_LATENCY = "high_latency"
    DATABASE_FAILURE = "database_failure"
    REGION_FAILURE = "region_failure"
    AUTOMATED_TEST = "automated_test"


@dataclass
class HealthStatus:
    """Health check status for a region."""
    region: str
    healthy: bool
    response_time_ms: float
    error_rate: float
    last_check: datetime
    details: Dict = field(default_factory=dict)


@dataclass
class FailoverEvent:
    """Failover event record."""
    event_id: str
    timestamp: datetime
    trigger: FailoverTrigger
    source_region: str
    target_region: str
    status: FailoverStatus
    initiated_by: str
    duration_seconds: Optional[float] = None
    details: Dict = field(default_factory=dict)


class FailoverController:
    """
    Centralized failover controller for ResilienceAI.
    Manages automated and manual failover operations.
    """
    
    def __init__(
        self,
        primary_region: str = "us-east-1",
        dr_region: str = "us-west-2",
        health_check_interval: int = 10,
        failover_threshold: int = 3
    ):
        self.primary_region = primary_region
        self.dr_region = dr_region
        self.health_check_interval = health_check_interval
        self.failover_threshold = failover_threshold
        
        self.current_region = primary_region
        self.status = FailoverStatus.HEALTHY
        self.health_checks: Dict[str, HealthStatus] = {}
        self.consecutive_failures = 0
        self.event_history: List[FailoverEvent] = []
        
        # AWS clients
        self.route53 = boto3.client('route53')
        self.rds = boto3.client('rds', region_name=primary_region)
        self.rds_dr = boto3.client('rds', region_name=dr_region)
        self.eks = boto3.client('eks', region_name=primary_region)
        self.eks_dr = boto3.client('eks', region_name=dr_region)
        
        # Callbacks
        self.pre_failover_callbacks: List[Callable] = []
        self.post_failover_callbacks: List[Callable] = []
        self.alert_callbacks: List[Callable] = []
        
        self._running = False
    
    def register_pre_failover_callback(self, callback: Callable):
        """Register callback to execute before failover."""
        self.pre_failover_callbacks.append(callback)
    
    def register_post_failover_callback(self, callback: Callable):
        """Register callback to execute after failover."""
        self.post_failover_callbacks.append(callback)
    
    def register_alert_callback(self, callback: Callable):
        """Register alert callback."""
        self.alert_callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start health monitoring."""
        self._running = True
        logger.info("Starting failover monitoring")
        
        while self._running:
            try:
                await self._health_check_cycle()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _health_check_cycle(self):
        """Execute one health check cycle."""
        # Check primary region
        primary_health = await self._check_region_health(self.primary_region)
        self.health_checks[self.primary_region] = primary_health
        
        # Check DR region
        dr_health = await self._check_region_health(self.dr_region)
        self.health_checks[self.dr_region] = dr_health
        
        # Evaluate failover need
        if self.current_region == self.primary_region:
            if not primary_health.healthy:
                self.consecutive_failures += 1
                logger.warning(
                    f"Primary region unhealthy "
                    f"({self.consecutive_failures}/{self.failover_threshold})"
                )
                
                if self.consecutive_failures >= self.failover_threshold:
                    await self._trigger_failover(FailoverTrigger.HEALTH_CHECK_FAILED)
            else:
                self.consecutive_failures = 0
    
    async def _check_region_health(self, region: str) -> HealthStatus:
        """Check health of a region."""
        endpoints = self._get_health_endpoints(region)
        
        total_response_time = 0
        failed_checks = 0
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    start = datetime.utcnow()
                    async with session.get(
                        endpoint,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        response_time = (datetime.utcnow() - start).total_seconds() * 1000
                        total_response_time += response_time
                        
                        if response.status != 200:
                            failed_checks += 1
                except Exception as e:
                    logger.debug(f"Health check failed for {endpoint}: {e}")
                    failed_checks += 1
        
        total_checks = len(endpoints)
        error_rate = failed_checks / total_checks if total_checks > 0 else 1.0
        avg_response_time = total_response_time / total_checks if total_checks > 0 else 0
        
        healthy = error_rate < 0.5 and avg_response_time < 2000
        
        return HealthStatus(
            region=region,
            healthy=healthy,
            response_time_ms=avg_response_time,
            error_rate=error_rate,
            last_check=datetime.utcnow()
        )
    
    def _get_health_endpoints(self, region: str) -> List[str]:
        """Get health check endpoints for a region."""
        base_urls = {
            self.primary_region: "https://api-primary.resilienceai.io",
            self.dr_region: "https://api-dr.resilienceai.io"
        }
        
        base_url = base_urls.get(region, base_urls[self.primary_region])
        
        return [
            f"{base_url}/health",
            f"{base_url}/health/ready",
            f"{base_url}/health/deep"
        ]
    
    async def _trigger_failover(self, trigger: FailoverTrigger):
        """Trigger failover process."""
        logger.info(f"Triggering failover: {trigger.value}")
        
        event_id = f"failover-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        event = FailoverEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            trigger=trigger,
            source_region=self.current_region,
            target_region=self.dr_region if self.current_region == self.primary_region else self.primary_region,
            status=FailoverStatus.FAILOVER_IN_PROGRESS,
            initiated_by="automated" if trigger != FailoverTrigger.MANUAL else "manual"
        )
        
        self.event_history.append(event)
        self.status = FailoverStatus.FAILOVER_IN_PROGRESS
        
        # Execute pre-failover callbacks
        for callback in self.pre_failover_callbacks:
            try:
                await callback(event)
            except Exception as e:
                logger.error(f"Pre-failover callback failed: {e}")
        
        # Send alert
        await self._send_alert(
            "CRITICAL",
            f"Failover initiated from {event.source_region} to {event.target_region}"
        )
        
        # Execute failover steps
        start_time = datetime.utcnow()
        
        try:
            await self._update_dns(event.target_region)
            
            if event.target_region == self.dr_region:
                await self._promote_dr_database()
            
            await self._scale_dr_region()
            await self._verify_failover(event.target_region)
            
            event.duration_seconds = (datetime.utcnow() - start_time).total_seconds()
            event.status = FailoverStatus.FAILOVER_COMPLETE
            self.status = FailoverStatus.FAILOVER_COMPLETE
            self.current_region = event.target_region
            self.consecutive_failures = 0
            
            logger.info(f"Failover completed in {event.duration_seconds:.2f} seconds")
            
            for callback in self.post_failover_callbacks:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Post-failover callback failed: {e}")
            
            await self._send_alert(
                "INFO",
                f"Failover completed successfully in {event.duration_seconds:.2f}s"
            )
        except Exception as e:
            logger.error(f"Failover failed: {e}")
            event.status = FailoverStatus.ERROR
            self.status = FailoverStatus.ERROR
            await self._send_alert("CRITICAL", f"Failover failed: {str(e)}")
            raise
    
    async def _update_dns(self, target_region: str):
        """Update Route53 DNS to point to target region."""
        logger.info(f"Updating DNS to point to {target_region}")
        # Implementation would update Route53 records
    
    async def _promote_dr_database(self):
        """Promote DR database to primary."""
        logger.info("Promoting DR database to primary")
        self.rds_dr.promote_read_replica(DBInstanceIdentifier='resilienceai-dr-db')
    
    async def _scale_dr_region(self):
        """Scale up DR region resources."""
        logger.info("Scaling up DR region")
        # Implementation would scale EKS node groups
    
    async def _verify_failover(self, target_region: str):
        """Verify failover was successful."""
        logger.info(f"Verifying failover to {target_region}")
        # Implementation would verify health checks
    
    async def _send_alert(self, severity: str, message: str):
        """Send alert notification."""
        alert = {
            "severity": severity,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "component": "failover_controller"
        }
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    async def initiate_manual_failover(self, reason: str) -> Dict:
        """Manually initiate failover."""
        logger.info(f"Manual failover initiated: {reason}")
        await self._trigger_failover(FailoverTrigger.MANUAL)
        return {
            "success": True,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get current failover status."""
        return {
            "current_region": self.current_region,
            "status": self.status.name,
            "health_checks": {
                region: {
                    "healthy": hc.healthy,
                    "response_time_ms": hc.response_time_ms,
                    "error_rate": hc.error_rate
                }
                for region, hc in self.health_checks.items()
            },
            "consecutive_failures": self.consecutive_failures
        }
    
    def stop_monitoring(self):
        """Stop health monitoring."""
        self._running = False
        logger.info("Failover monitoring stopped")


if __name__ == "__main__":
    controller = FailoverController()
    status = controller.get_status()
    print(json.dumps(status, indent=2))
