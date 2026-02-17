"""
Edge Monitoring for ResilienceAI
================================
Comprehensive monitoring of edge nodes and infrastructure.
"""

import psutil
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class MetricThreshold:
    """Threshold configuration for metrics"""
    warning: float
    critical: float
    direction: str = "above"


class EdgeMonitor:
    """Monitors edge node health and performance"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.metrics_history = []
        self.max_history_size = 1000
        self.thresholds = self._default_thresholds()
        self.alert_handlers = []
        
    def _default_thresholds(self) -> Dict[str, MetricThreshold]:
        """Define default metric thresholds"""
        return {
            "cpu_percent": MetricThreshold(70, 90),
            "memory_percent": MetricThreshold(80, 95),
            "disk_percent": MetricThreshold(85, 95),
            "temperature_celsius": MetricThreshold(70, 85),
            "network_latency_ms": MetricThreshold(100, 500),
            "inference_latency_ms": MetricThreshold(100, 500),
        }
        
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": self.node_id,
            "system": self._collect_system_metrics(),
            "network": self._collect_network_metrics(),
            "application": self._collect_application_metrics()
        }
        
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
            
        await self._check_thresholds(metrics)
        return metrics
        
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "used_gb": psutil.virtual_memory().used / (1024**3),
                "available_gb": psutil.virtual_memory().available / (1024**3)
            },
            "disk": {
                "percent": psutil.disk_usage('/').percent,
                "used_gb": psutil.disk_usage('/').used / (1024**3),
                "free_gb": psutil.disk_usage('/').free / (1024**3)
            },
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        }
        
    def _collect_network_metrics(self) -> Dict[str, Any]:
        """Collect network metrics"""
        net_io = psutil.net_io_counters()
        
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "connections": len(psutil.net_connections()),
        }
        
    def _collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics"""
        return {
            "active_inferences": 0,
            "queue_depth": 0,
            "cache_hit_rate": 0,
            "sync_pending_count": 0,
            "models_loaded": []
        }
        
    async def _check_thresholds(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and trigger alerts"""
        alerts = []
        system = metrics.get("system", {})
        
        cpu = system.get("cpu_percent", 0)
        if self._is_threshold_breached("cpu_percent", cpu):
            alerts.append({
                "metric": "cpu_percent",
                "value": cpu,
                "severity": "critical" if cpu > self.thresholds["cpu_percent"].critical else "warning"
            })
            
        memory = system.get("memory", {})
        mem_percent = memory.get("percent", 0)
        if self._is_threshold_breached("memory_percent", mem_percent):
            alerts.append({
                "metric": "memory_percent",
                "value": mem_percent,
                "severity": "critical" if mem_percent > self.thresholds["memory_percent"].critical else "warning"
            })
            
        disk = system.get("disk", {})
        disk_percent = disk.get("percent", 0)
        if self._is_threshold_breached("disk_percent", disk_percent):
            alerts.append({
                "metric": "disk_percent",
                "value": disk_percent,
                "severity": "critical" if disk_percent > self.thresholds["disk_percent"].critical else "warning"
            })
            
        for alert in alerts:
            for handler in self.alert_handlers:
                await handler(alert)
                
    def _is_threshold_breached(self, metric_name: str, value: float) -> bool:
        """Check if metric breaches threshold"""
        if metric_name not in self.thresholds:
            return False
        threshold = self.thresholds[metric_name]
        if threshold.direction == "above":
            return value > threshold.warning
        else:
            return value < threshold.warning
            
    def register_alert_handler(self, handler: callable):
        """Register an alert handler"""
        self.alert_handlers.append(handler)
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        if not self.metrics_history:
            return {"status": HealthStatus.OFFLINE.value}
            
        latest = self.metrics_history[-1]
        system = latest.get("system", {})
        
        critical_count = 0
        warning_count = 0
        
        for metric_name, threshold in self.thresholds.items():
            if metric_name in system:
                value = system[metric_name]
                if self._is_threshold_breached(metric_name, value):
                    if value > threshold.critical:
                        critical_count += 1
                    else:
                        warning_count += 1
                        
        if critical_count > 0:
            status = HealthStatus.CRITICAL
        elif warning_count > 0:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY
            
        return {
            "status": status.value,
            "timestamp": latest["timestamp"],
            "critical_alerts": critical_count,
            "warning_alerts": warning_count,
            "metrics": latest
        }
        
    def get_metrics_trend(self, metric_name: str, duration_minutes: int = 60) -> List[Dict]:
        """Get metric trend over time"""
        cutoff = datetime.utcnow() - timedelta(minutes=duration_minutes)
        
        trend = []
        for metrics in self.metrics_history:
            metrics_time = datetime.fromisoformat(metrics["timestamp"])
            if metrics_time >= cutoff:
                value = metrics.get("system", {}).get(metric_name)
                if value is not None:
                    trend.append({
                        "timestamp": metrics["timestamp"],
                        "value": value
                    })
                    
        return trend


class DistributedMonitor:
    """Monitors multiple edge nodes in a distributed deployment"""
    
    def __init__(self):
        self.nodes: Dict[str, EdgeMonitor] = {}
        self.aggregated_metrics = []
        
    def register_node(self, node_id: str, monitor: EdgeMonitor):
        """Register an edge node for monitoring"""
        self.nodes[node_id] = monitor
        
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all nodes"""
        all_metrics = {}
        
        for node_id, monitor in self.nodes.items():
            try:
                metrics = await monitor.collect_metrics()
                all_metrics[node_id] = metrics
            except Exception as e:
                all_metrics[node_id] = {"error": str(e)}
                
        aggregated = self._aggregate_metrics(all_metrics)
        self.aggregated_metrics.append(aggregated)
        
        return {
            "nodes": all_metrics,
            "aggregated": aggregated
        }
        
    def _aggregate_metrics(self, all_metrics: Dict) -> Dict[str, Any]:
        """Aggregate metrics across all nodes"""
        cpu_values = []
        memory_values = []
        
        for node_id, metrics in all_metrics.items():
            if "error" in metrics:
                continue
            system = metrics.get("system", {})
            cpu_values.append(system.get("cpu_percent", 0))
            memory_values.append(system.get("memory", {}).get("percent", 0))
            
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_nodes": len(self.nodes),
            "reporting_nodes": len([m for m in all_metrics.values() if "error" not in m]),
            "avg_cpu": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "avg_memory": sum(memory_values) / len(memory_values) if memory_values else 0,
            "max_cpu": max(cpu_values) if cpu_values else 0,
            "max_memory": max(memory_values) if memory_values else 0
        }
        
    def get_cluster_health(self) -> Dict[str, Any]:
        """Get overall cluster health"""
        node_statuses = {}
        
        for node_id, monitor in self.nodes.items():
            health = monitor.get_health_status()
            node_statuses[node_id] = health["status"]
            
        status_counts = {}
        for status in node_statuses.values():
            status_counts[status] = status_counts.get(status, 0) + 1
            
        return {
            "overall_status": "critical" if status_counts.get("critical", 0) > 0 else 
                            "degraded" if status_counts.get("degraded", 0) > 0 else "healthy",
            "node_count": len(self.nodes),
            "status_breakdown": status_counts,
            "node_details": node_statuses
        }
