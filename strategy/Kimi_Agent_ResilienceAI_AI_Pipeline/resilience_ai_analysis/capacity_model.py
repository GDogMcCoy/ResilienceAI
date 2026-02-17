"""
Capacity Modeling and Simulation
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import numpy as np


class CapacityModelType(Enum):
    LINEAR = "linear"
    QUEUING = "queuing"
    SIMULATION = "simulation"


@dataclass
class CapacityRequirements:
    """Calculated capacity requirements"""
    service_name: str
    timestamp: datetime
    
    # Current capacity
    current_instances: int
    current_capacity_rps: float
    
    # Required capacity
    required_instances: int
    required_capacity_rps: float
    
    # Headroom
    headroom_percent: float
    recommended_headroom_percent: float
    
    # Bottleneck analysis
    limiting_factor: str
    bottleneck_severity: str
    
    # Cost
    current_monthly_cost: float
    projected_monthly_cost: float


@dataclass
class ServiceProfile:
    """Service capacity profile"""
    service_name: str
    
    # Capacity characteristics
    requests_per_second_per_instance: float
    cpu_per_request: float  # CPU milliseconds
    memory_per_request: float  # MB
    latency_p99_ms: float
    
    # Scaling characteristics
    scale_up_time_seconds: float
    scale_down_time_seconds: float
    
    # Resource limits
    max_cpu_percent: float
    max_memory_percent: float
    
    # Cost
    cost_per_instance_hour: float


class CapacityModel:
    """Capacity modeling and requirements calculation"""
    
    def __init__(self):
        self.service_profiles: Dict[str, ServiceProfile] = {}
        self.capacity_history: List[CapacityRequirements] = []
        
    def register_service_profile(self, profile: ServiceProfile):
        """Register a service capacity profile"""
        self.service_profiles[profile.service_name] = profile
    
    def calculate_capacity_requirements(
        self,
        service_name: str,
        current_metrics: Dict[str, float],
        forecasted_load: float,
        sla_requirements: Dict[str, float]
    ) -> CapacityRequirements:
        """Calculate capacity requirements for a service"""
        
        profile = self.service_profiles.get(service_name)
        if not profile:
            raise ValueError(f"No profile found for {service_name}")
        
        current_instances = current_metrics.get('instance_count', 1)
        current_rps = current_metrics.get('requests_per_second', 0)
        
        # Calculate current capacity
        current_capacity_rps = current_instances * profile.requests_per_second_per_instance
        
        # Calculate required capacity with headroom
        headroom_factor = 1 + (sla_requirements.get('headroom_percent', 30) / 100)
        required_capacity_rps = forecasted_load * headroom_factor
        
        # Calculate required instances
        required_instances = int(np.ceil(
            required_capacity_rps / profile.requests_per_second_per_instance
        ))
        
        # Determine limiting factor
        cpu_util = current_metrics.get('cpu_percent', 0)
        memory_util = current_metrics.get('memory_percent', 0)
        
        if cpu_util > memory_util:
            limiting_factor = 'cpu'
            bottleneck_severity = 'critical' if cpu_util > 90 else 'warning' if cpu_util > 75 else 'normal'
        else:
            limiting_factor = 'memory'
            bottleneck_severity = 'critical' if memory_util > 90 else 'warning' if memory_util > 75 else 'normal'
        
        # Calculate costs
        current_monthly_cost = current_instances * profile.cost_per_instance_hour * 24 * 30
        projected_monthly_cost = required_instances * profile.cost_per_instance_hour * 24 * 30
        
        # Calculate headroom
        if current_capacity_rps > 0:
            headroom_percent = ((current_capacity_rps - current_rps) / current_capacity_rps) * 100
        else:
            headroom_percent = 0
        
        requirements = CapacityRequirements(
            service_name=service_name,
            timestamp=datetime.now(),
            current_instances=current_instances,
            current_capacity_rps=current_capacity_rps,
            required_instances=required_instances,
            required_capacity_rps=required_capacity_rps,
            headroom_percent=headroom_percent,
            recommended_headroom_percent=sla_requirements.get('headroom_percent', 30),
            limiting_factor=limiting_factor,
            bottleneck_severity=bottleneck_severity,
            current_monthly_cost=current_monthly_cost,
            projected_monthly_cost=projected_monthly_cost
        )
        
        self.capacity_history.append(requirements)
        return requirements
    
    def simulate_capacity_scenario(
        self,
        service_name: str,
        load_scenario: List[float],
        initial_instances: int
    ) -> List[Dict]:
        """Simulate capacity under different load scenarios"""
        
        profile = self.service_profiles.get(service_name)
        if not profile:
            raise ValueError(f"No profile found for {service_name}")
        
        results = []
        instances = initial_instances
        
        for i, load in enumerate(load_scenario):
            capacity = instances * profile.requests_per_second_per_instance
            utilization = (load / capacity) * 100 if capacity > 0 else 0
            
            # Simulate scaling decisions
            if utilization > 80 and i > 0:
                instances += 1
            elif utilization < 40 and instances > 1:
                instances -= 1
            
            results.append({
                'time_step': i,
                'load_rps': load,
                'instances': instances,
                'capacity_rps': capacity,
                'utilization_percent': utilization,
                'latency_ms': self._estimate_latency(utilization, profile),
                'cost_per_hour': instances * profile.cost_per_instance_hour
            })
        
        return results
    
    def _estimate_latency(self, utilization: float, profile: ServiceProfile) -> float:
        """Estimate latency based on utilization (M/M/1 queue model)"""
        if utilization >= 100:
            return float('inf')
        
        base_latency = profile.latency_p99_ms
        queue_factor = 1 / (1 - utilization / 100)
        return base_latency * queue_factor
    
    def find_optimal_capacity(
        self,
        service_name: str,
        load_distribution: List[float],
        sla_latency_ms: float
    ) -> Dict:
        """Find optimal capacity configuration"""
        
        profile = self.service_profiles.get(service_name)
        if not profile:
            raise ValueError(f"No profile found for {service_name}")
        
        best_config = None
        best_cost = float('inf')
        
        # Try different instance counts
        for instances in range(1, 100):
            capacity = instances * profile.requests_per_second_per_instance
            total_cost = instances * profile.cost_per_instance_hour * 24 * 30
            
            # Check if SLA is met for all load points
            sla_met = True
            max_utilization = 0
            
            for load in load_distribution:
                utilization = (load / capacity) * 100 if capacity > 0 else 0
                max_utilization = max(max_utilization, utilization)
                
                estimated_latency = self._estimate_latency(utilization, profile)
                if estimated_latency > sla_latency_ms:
                    sla_met = False
                    break
            
            if sla_met and total_cost < best_cost:
                best_cost = total_cost
                best_config = {
                    'instances': instances,
                    'capacity_rps': capacity,
                    'monthly_cost': total_cost,
                    'max_utilization': max_utilization
                }
        
        return best_config or {'error': 'No configuration meets SLA'}
