"""
Resource Monitoring System for Capacity Planning
"""

import psutil
import time
import asyncio
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, AsyncIterator
from datetime import datetime, timedelta
from collections import deque
import json
import logging


@dataclass
class SystemMetrics:
    """Comprehensive system metrics"""
    timestamp: datetime
    
    # CPU Metrics
    cpu_percent: float
    cpu_count_physical: int
    cpu_count_logical: int
    cpu_freq_mhz: float
    cpu_load_avg_1m: float
    cpu_load_avg_5m: float
    cpu_load_avg_15m: float
    
    # Memory Metrics
    memory_percent: float
    memory_total_gb: float
    memory_available_gb: float
    memory_used_gb: float
    memory_cached_gb: float
    memory_buffers_gb: float
    
    # Disk Metrics
    disk_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_free_gb: float
    disk_read_mbps: float
    disk_write_mbps: float
    disk_iops: float
    
    # Network Metrics
    network_sent_mbps: float
    network_recv_mbps: float
    network_packets_sent: int
    network_packets_recv: int
    network_errors_in: int
    network_errors_out: int
    
    # Process Metrics
    process_count: int
    thread_count: int


class ResourceMonitor:
    """Advanced resource monitoring with historical tracking"""
    
    def __init__(self, history_size: int = 10080):  # 1 week at 1-minute intervals
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.alert_thresholds = {
            'cpu_critical': 90,
            'cpu_warning': 75,
            'memory_critical': 90,
            'memory_warning': 80,
            'disk_critical': 90,
            'disk_warning': 80,
        }
        self.logger = logging.getLogger(__name__)
        
    async def collect_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count_physical = psutil.cpu_count(logical=False) or 0
        cpu_count_logical = psutil.cpu_count(logical=True) or 0
        cpu_freq = psutil.cpu_freq()
        cpu_load_avg = psutil.getloadavg()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Process metrics
        process_count = len(psutil.pids())
        thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']))
        
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            cpu_count_physical=cpu_count_physical,
            cpu_count_logical=cpu_count_logical,
            cpu_freq_mhz=cpu_freq.current if cpu_freq else 0,
            cpu_load_avg_1m=cpu_load_avg[0],
            cpu_load_avg_5m=cpu_load_avg[1],
            cpu_load_avg_15m=cpu_load_avg[2],
            memory_percent=memory.percent,
            memory_total_gb=memory.total / (1024**3),
            memory_available_gb=memory.available / (1024**3),
            memory_used_gb=memory.used / (1024**3),
            memory_cached_gb=getattr(memory, 'cached', 0) / (1024**3),
            memory_buffers_gb=getattr(memory, 'buffers', 0) / (1024**3),
            disk_percent=disk.percent,
            disk_total_gb=disk.total / (1024**3),
            disk_used_gb=disk.used / (1024**3),
            disk_free_gb=disk.free / (1024**3),
            disk_read_mbps=(disk_io.read_bytes / (1024**2)) if disk_io else 0,
            disk_write_mbps=(disk_io.write_bytes / (1024**2)) if disk_io else 0,
            disk_iops=(disk_io.read_count + disk_io.write_count) if disk_io else 0,
            network_sent_mbps=(network.bytes_sent / (1024**2)) if network else 0,
            network_recv_mbps=(network.bytes_recv / (1024**2)) if network else 0,
            network_packets_sent=network.packets_sent if network else 0,
            network_packets_recv=network.packets_recv if network else 0,
            network_errors_in=network.errin if network else 0,
            network_errors_out=network.errout if network else 0,
            process_count=process_count,
            thread_count=thread_count
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    async def stream_metrics(self, interval_seconds: int = 60) -> AsyncIterator[SystemMetrics]:
        """Stream metrics continuously"""
        while True:
            metrics = await self.collect_metrics()
            yield metrics
            await asyncio.sleep(interval_seconds)
    
    def get_historical_metrics(
        self, 
        duration: timedelta,
        metric_type: Optional[str] = None
    ) -> List[SystemMetrics]:
        """Retrieve historical metrics for analysis"""
        cutoff_time = datetime.now() - duration
        filtered = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        return filtered
    
    def calculate_statistics(self, duration: timedelta) -> Dict[str, Dict[str, float]]:
        """Calculate statistical summaries of metrics"""
        metrics = self.get_historical_metrics(duration)
        
        if not metrics:
            return {}
        
        stats = {}
        fields = [
            'cpu_percent', 'memory_percent', 'disk_percent',
            'network_sent_mbps', 'network_recv_mbps'
        ]
        
        for field in fields:
            values = [getattr(m, field) for m in metrics]
            if values:
                stats[field] = {
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'p50': sorted(values)[len(values) // 2],
                    'p95': sorted(values)[int(len(values) * 0.95)] if len(values) > 1 else values[0],
                    'p99': sorted(values)[int(len(values) * 0.99)] if len(values) > 1 else values[0],
                }
        
        return stats
    
    def check_alerts(self) -> List[Dict]:
        """Check for resource threshold violations"""
        if not self.metrics_history:
            return []
        
        latest = self.metrics_history[-1]
        alerts = []
        
        if latest.cpu_percent > self.alert_thresholds['cpu_critical']:
            alerts.append({
                'severity': 'critical',
                'resource': 'cpu',
                'value': latest.cpu_percent,
                'threshold': self.alert_thresholds['cpu_critical'],
                'message': f'CPU usage critical: {latest.cpu_percent:.1f}%'
            })
        elif latest.cpu_percent > self.alert_thresholds['cpu_warning']:
            alerts.append({
                'severity': 'warning',
                'resource': 'cpu',
                'value': latest.cpu_percent,
                'threshold': self.alert_thresholds['cpu_warning'],
                'message': f'CPU usage warning: {latest.cpu_percent:.1f}%'
            })
        
        if latest.memory_percent > self.alert_thresholds['memory_critical']:
            alerts.append({
                'severity': 'critical',
                'resource': 'memory',
                'value': latest.memory_percent,
                'threshold': self.alert_thresholds['memory_critical'],
                'message': f'Memory usage critical: {latest.memory_percent:.1f}%'
            })
        elif latest.memory_percent > self.alert_thresholds['memory_warning']:
            alerts.append({
                'severity': 'warning',
                'resource': 'memory',
                'value': latest.memory_percent,
                'threshold': self.alert_thresholds['memory_warning'],
                'message': f'Memory usage warning: {latest.memory_percent:.1f}%'
            })
        
        return alerts
