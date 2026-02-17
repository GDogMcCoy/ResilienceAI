"""
ResilienceAI Capacity Planning Architecture
Core architecture and orchestration for capacity planning
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict


class ResourceType(Enum):
    """Types of resources that can be monitored"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE = "database"
    CACHE = "cache"


class ScalingType(Enum):
    """Types of scaling operations"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"


@dataclass
class ResourceMetrics:
    """Resource utilization metrics"""
    timestamp: datetime
    resource_type: ResourceType
    utilization_percent: float
    allocated: float
    used: float
    available: float
    peak_usage: float
    avg_usage: float
    
    @property
    def headroom_percent(self) -> float:
        return 100 - self.utilization_percent
    
    @property
    def is_overloaded(self) -> bool:
        return self.utilization_percent > 80


@dataclass
class CapacityPlan:
    """Capacity planning configuration"""
    service_name: str
    current_capacity: Dict[str, float]
    recommended_capacity: Dict[str, float]
    scaling_strategy: ScalingType
    trigger_threshold: float
    cooldown_period: int  # seconds
    max_instances: int
    min_instances: int
    cost_estimate: float
    implementation_timeline: timedelta


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


class CapacityPlanningOrchestrator:
    """Main orchestrator for capacity planning"""
    
    def __init__(self):
        self.resource_monitor = None
        self.load_forecaster = None
        self.scaling_engine = None
        self.capacity_manager = None
        self.bottleneck_detector = None
        self.cost_model = None
        
    async def run_capacity_planning_cycle(self):
        """Execute full capacity planning cycle"""
        # 1. Collect metrics
        metrics = await self.resource_monitor.collect_metrics()
        
        # 2. Forecast load
        forecasts = await self.load_forecaster.forecast(metrics)
        
        # 3. Detect bottlenecks
        bottlenecks = self.bottleneck_detector.identify(metrics, forecasts)
        
        # 4. Calculate capacity needs
        plans = self.capacity_manager.calculate_plans(
            metrics, forecasts, bottlenecks
        )
        
        # 5. Optimize costs
        optimized_plans = self.cost_model.optimize(plans)
        
        # 6. Execute scaling decisions
        await self.scaling_engine.execute(optimized_plans)
        
        return optimized_plans
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system capacity status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'operational',
            'components': {
                'resource_monitor': self.resource_monitor is not None,
                'load_forecaster': self.load_forecaster is not None,
                'scaling_engine': self.scaling_engine is not None,
                'capacity_manager': self.capacity_manager is not None,
                'bottleneck_detector': self.bottleneck_detector is not None,
                'cost_model': self.cost_model is not None,
            }
        }
