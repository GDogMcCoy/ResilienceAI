"""
Bottleneck Detection and Analysis
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class BottleneckType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    APPLICATION = "application"
    EXTERNAL = "external"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Bottleneck:
    """Identified bottleneck"""
    timestamp: datetime
    service_name: str
    bottleneck_type: BottleneckType
    severity: Severity
    
    # Metrics
    current_value: float
    threshold: float
    utilization_percent: float
    
    # Impact
    affected_requests: int
    latency_impact_ms: float
    error_rate_impact: float
    
    # Root cause
    root_cause: str
    contributing_factors: List[str]
    
    # Recommendations
    recommendations: List[str]
    estimated_fix_time: timedelta


class BottleneckDetector:
    """Advanced bottleneck detection system"""
    
    def __init__(self):
        self.thresholds = {
            'cpu_critical': 90,
            'cpu_warning': 75,
            'memory_critical': 90,
            'memory_warning': 80,
            'disk_io_critical': 85,
            'disk_io_warning': 70,
            'network_critical': 90,
            'network_warning': 75,
            'latency_critical': 1000,  # ms
            'latency_warning': 500,
            'error_rate_critical': 5,  # percent
            'error_rate_warning': 2,
        }
        self.bottleneck_history: List[Bottleneck] = []
        
    def identify_bottlenecks(
        self,
        service_name: str,
        metrics: Dict[str, float],
        request_metrics: Optional[Dict] = None
    ) -> List[Bottleneck]:
        """Identify bottlenecks from metrics"""
        
        bottlenecks = []
        
        # Check CPU bottleneck
        cpu_bottleneck = self._check_cpu_bottleneck(service_name, metrics)
        if cpu_bottleneck:
            bottlenecks.append(cpu_bottleneck)
        
        # Check memory bottleneck
        memory_bottleneck = self._check_memory_bottleneck(service_name, metrics)
        if memory_bottleneck:
            bottlenecks.append(memory_bottleneck)
        
        # Check disk I/O bottleneck
        disk_bottleneck = self._check_disk_bottleneck(service_name, metrics)
        if disk_bottleneck:
            bottlenecks.append(disk_bottleneck)
        
        # Check network bottleneck
        network_bottleneck = self._check_network_bottleneck(service_name, metrics)
        if network_bottleneck:
            bottlenecks.append(network_bottleneck)
        
        # Check application-level bottlenecks
        if request_metrics:
            app_bottleneck = self._check_application_bottleneck(service_name, request_metrics)
            if app_bottleneck:
                bottlenecks.append(app_bottleneck)
        
        self.bottleneck_history.extend(bottlenecks)
        return bottlenecks
    
    def _check_cpu_bottleneck(self, service_name: str, metrics: Dict[str, float]) -> Optional[Bottleneck]:
        """Check for CPU bottleneck"""
        cpu_percent = metrics.get('cpu_percent', 0)
        
        if cpu_percent < self.thresholds['cpu_warning']:
            return None
        
        severity = Severity.CRITICAL if cpu_percent > self.thresholds['cpu_critical'] else Severity.HIGH
        
        return Bottleneck(
            timestamp=datetime.now(),
            service_name=service_name,
            bottleneck_type=BottleneckType.CPU,
            severity=severity,
            current_value=cpu_percent,
            threshold=self.thresholds['cpu_critical'],
            utilization_percent=cpu_percent,
            affected_requests=int(metrics.get('requests_per_second', 0) * 0.3),
            latency_impact_ms=metrics.get('p95_latency_ms', 0) * 0.5,
            error_rate_impact=metrics.get('error_rate', 0) * 2,
            root_cause="CPU saturation from high request volume or inefficient processing",
            contributing_factors=["High request rate", "CPU-intensive operations", "Insufficient instance sizing"],
            recommendations=["Scale up CPU resources", "Optimize CPU-intensive code paths", "Implement caching"],
            estimated_fix_time=timedelta(minutes=5)
        )
    
    def _check_memory_bottleneck(self, service_name: str, metrics: Dict[str, float]) -> Optional[Bottleneck]:
        """Check for memory bottleneck"""
        memory_percent = metrics.get('memory_percent', 0)
        
        if memory_percent < self.thresholds['memory_warning']:
            return None
        
        severity = Severity.CRITICAL if memory_percent > self.thresholds['memory_critical'] else Severity.HIGH
        
        return Bottleneck(
            timestamp=datetime.now(),
            service_name=service_name,
            bottleneck_type=BottleneckType.MEMORY,
            severity=severity,
            current_value=memory_percent,
            threshold=self.thresholds['memory_critical'],
            utilization_percent=memory_percent,
            affected_requests=int(metrics.get('requests_per_second', 0) * 0.2),
            latency_impact_ms=metrics.get('p95_latency_ms', 0) * 0.3,
            error_rate_impact=metrics.get('error_rate', 0) * 1.5,
            root_cause="Memory pressure from high object allocation or memory leaks",
            contributing_factors=["High memory allocation rate", "Potential memory leaks", "Large data structures"],
            recommendations=["Scale up memory resources", "Profile memory usage", "Implement object pooling"],
            estimated_fix_time=timedelta(minutes=10)
        )
    
    def _check_disk_bottleneck(self, service_name: str, metrics: Dict[str, float]) -> Optional[Bottleneck]:
        """Check for disk I/O bottleneck"""
        disk_util = metrics.get('disk_utilization', 0)
        disk_queue_depth = metrics.get('disk_queue_depth', 0)
        
        if disk_util < self.thresholds['disk_io_warning'] and disk_queue_depth < 10:
            return None
        
        severity = Severity.CRITICAL if disk_util > self.thresholds['disk_io_critical'] else Severity.HIGH
        
        return Bottleneck(
            timestamp=datetime.now(),
            service_name=service_name,
            bottleneck_type=BottleneckType.DISK_IO,
            severity=severity,
            current_value=disk_util,
            threshold=self.thresholds['disk_io_critical'],
            utilization_percent=disk_util,
            affected_requests=int(metrics.get('requests_per_second', 0) * 0.4),
            latency_impact_ms=metrics.get('p95_latency_ms', 0) * 0.8,
            error_rate_impact=metrics.get('error_rate', 0) * 1.2,
            root_cause="Disk I/O saturation from high read/write operations",
            contributing_factors=["High disk queue depth", "Slow disk I/O operations", "Insufficient IOPS"],
            recommendations=["Upgrade to higher IOPS storage", "Implement caching layer", "Optimize database queries"],
            estimated_fix_time=timedelta(minutes=15)
        )
    
    def _check_network_bottleneck(self, service_name: str, metrics: Dict[str, float]) -> Optional[Bottleneck]:
        """Check for network bottleneck"""
        network_util = metrics.get('network_utilization', 0)
        
        if network_util < self.thresholds['network_warning']:
            return None
        
        severity = Severity.CRITICAL if network_util > self.thresholds['network_critical'] else Severity.HIGH
        
        return Bottleneck(
            timestamp=datetime.now(),
            service_name=service_name,
            bottleneck_type=BottleneckType.NETWORK,
            severity=severity,
            current_value=network_util,
            threshold=self.thresholds['network_critical'],
            utilization_percent=network_util,
            affected_requests=int(metrics.get('requests_per_second', 0) * 0.5),
            latency_impact_ms=metrics.get('p95_latency_ms', 0) * 0.6,
            error_rate_impact=metrics.get('error_rate', 0) * 1.0,
            root_cause="Network bandwidth saturation",
            contributing_factors=["High data transfer volume", "Large payload sizes", "Network latency"],
            recommendations=["Upgrade network bandwidth", "Compress data payloads", "Implement CDN"],
            estimated_fix_time=timedelta(minutes=20)
        )
    
    def _check_application_bottleneck(self, service_name: str, metrics: Dict[str, float]) -> Optional[Bottleneck]:
        """Check for application-level bottleneck"""
        latency = metrics.get('p95_latency_ms', 0)
        error_rate = metrics.get('error_rate', 0)
        
        if latency < self.thresholds['latency_warning'] and error_rate < self.thresholds['error_rate_warning']:
            return None
        
        if latency > self.thresholds['latency_critical']:
            severity = Severity.CRITICAL
        elif error_rate > self.thresholds['error_rate_critical']:
            severity = Severity.CRITICAL
        else:
            severity = Severity.HIGH
        
        return Bottleneck(
            timestamp=datetime.now(),
            service_name=service_name,
            bottleneck_type=BottleneckType.APPLICATION,
            severity=severity,
            current_value=max(latency, error_rate * 100),
            threshold=self.thresholds['latency_critical'],
            utilization_percent=0,
            affected_requests=int(metrics.get('total_requests', 0) * error_rate / 100),
            latency_impact_ms=latency,
            error_rate_impact=error_rate,
            root_cause="Application-level performance degradation",
            contributing_factors=["Inefficient code paths", "Database query performance", "External service latency"],
            recommendations=["Profile application for hotspots", "Optimize database queries", "Add caching"],
            estimated_fix_time=timedelta(hours=2)
        )
    
    def analyze_bottleneck_patterns(
        self,
        service_name: Optional[str] = None,
        days: int = 7
    ) -> Dict:
        """Analyze bottleneck patterns over time"""
        
        since = datetime.now() - timedelta(days=days)
        history = [b for b in self.bottleneck_history if b.timestamp >= since]
        
        if service_name:
            history = [b for b in history if b.service_name == service_name]
        
        if not history:
            return {'message': 'No bottlenecks found in the specified period'}
        
        # Count by type
        by_type = {}
        by_severity = {}
        by_hour = {}
        
        for bottleneck in history:
            bt = bottleneck.bottleneck_type.value
            by_type[bt] = by_type.get(bt, 0) + 1
            
            sev = bottleneck.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
            hour = bottleneck.timestamp.hour
            by_hour[hour] = by_hour.get(hour, 0) + 1
        
        return {
            'total_bottlenecks': len(history),
            'by_type': by_type,
            'by_severity': by_severity,
            'by_hour': by_hour,
            'most_common_type': max(by_type.items(), key=lambda x: x[1])[0] if by_type else None,
            'peak_bottleneck_hour': max(by_hour.items(), key=lambda x: x[1])[0] if by_hour else None
        }
