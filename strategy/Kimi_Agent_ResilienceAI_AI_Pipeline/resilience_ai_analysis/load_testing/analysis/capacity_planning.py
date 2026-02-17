"""
Capacity planning framework for ResilienceAI
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class ResourceRequirements:
    """Resource requirements for a given load"""
    cpu_cores: float
    memory_gb: float
    gpu_count: int
    storage_gb: float
    network_mbps: float


@dataclass
class CapacityPlan:
    """Capacity planning result"""
    current_capacity: ResourceRequirements
    recommended_capacity: ResourceRequirements
    headroom_percent: float
    scaling_factor: float
    cost_estimate: Dict[str, float]
    recommendations: List[str]


class CapacityPlanner:
    """
    Capacity planning for ResilienceAI infrastructure
    """
    
    # Resource usage per unit of load
    BASELINE_RESOURCES = {
        "predict_request": {
            "cpu_ms": 50,      # CPU milliseconds per request
            "memory_mb": 10,   # Memory per concurrent request
            "gpu_ms": 0,       # GPU milliseconds (if applicable)
        },
        "batch_request": {
            "cpu_ms": 500,
            "memory_mb": 100,
            "gpu_ms": 0,
        },
        "model_load": {
            "cpu_ms": 10000,
            "memory_mb": 512,  # Per model
            "gpu_memory_mb": 1024,  # If using GPU
        },
    }
    
    # Overhead factors
    OVERHEAD_FACTOR = 1.3  # 30% overhead for system operations
    HEADROOM_FACTOR = 1.5  # 50% headroom for growth
    
    def __init__(self):
        self.current_metrics: Dict[str, float] = {}
        self.projected_growth: Dict[str, float] = {}
    
    def calculate_capacity(
        self,
        current_rps: float,
        target_rps: float,
        current_resources: ResourceRequirements,
        growth_rate_monthly: float = 0.1,  # 10% monthly growth
        planning_horizon_months: int = 6
    ) -> CapacityPlan:
        """
        Calculate required capacity for target load
        
        Args:
            current_rps: Current requests per second
            target_rps: Target requests per second
            current_resources: Current resource allocation
            growth_rate_monthly: Expected monthly growth rate
            planning_horizon_months: Planning time horizon
        
        Returns:
            CapacityPlan with recommendations
        """
        # Calculate scaling factor
        scaling_factor = target_rps / max(current_rps, 1)
        
        # Apply growth projection
        projected_growth = (1 + growth_rate_monthly) ** planning_horizon_months
        total_scaling = scaling_factor * projected_growth * self.HEADROOM_FACTOR
        
        # Calculate recommended resources
        recommended = ResourceRequirements(
            cpu_cores=current_resources.cpu_cores * total_scaling * self.OVERHEAD_FACTOR,
            memory_gb=current_resources.memory_gb * total_scaling * self.OVERHEAD_FACTOR,
            gpu_count=math.ceil(current_resources.gpu_count * scaling_factor),
            storage_gb=current_resources.storage_gb * math.sqrt(total_scaling),  # Sub-linear
            network_mbps=current_resources.network_mbps * scaling_factor * self.OVERHEAD_FACTOR,
        )
        
        # Generate cost estimate
        cost_estimate = self._estimate_cost(recommended)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            current_resources, recommended, scaling_factor
        )
        
        return CapacityPlan(
            current_capacity=current_resources,
            recommended_capacity=recommended,
            headroom_percent=(self.HEADROOM_FACTOR - 1) * 100,
            scaling_factor=total_scaling,
            cost_estimate=cost_estimate,
            recommendations=recommendations,
        )
    
    def _estimate_cost(self, resources: ResourceRequirements) -> Dict[str, float]:
        """Estimate monthly cost for resources"""
        # Simplified cost model (AWS-like pricing)
        costs = {
            "compute": resources.cpu_cores * 50,  # $50 per vCPU/month
            "memory": resources.memory_gb * 8,    # $8 per GB/month
            "gpu": resources.gpu_count * 2000,    # $2000 per GPU/month
            "storage": resources.storage_gb * 0.1,  # $0.10 per GB/month
            "network": resources.network_mbps * 10,  # $10 per Mbps/month
        }
        costs["total"] = sum(costs.values())
        return costs
    
    def _generate_recommendations(
        self,
        current: ResourceRequirements,
        recommended: ResourceRequirements,
        scaling_factor: float
    ) -> List[str]:
        """Generate capacity planning recommendations"""
        recommendations = []
        
        if scaling_factor > 3:
            recommendations.append(
                "Consider horizontal scaling with load balancer for better fault tolerance"
            )
        
        if recommended.cpu_cores > 32:
            recommendations.append(
                "Consider containerization with Kubernetes for better resource utilization"
            )
        
        if recommended.memory_gb > 128:
            recommendations.append(
                "Implement memory caching layer (Redis/Memcached) to reduce memory pressure"
            )
        
        if recommended.gpu_count > 2:
            recommendations.append(
                "Consider GPU cluster with job queue for efficient GPU utilization"
            )
        
        recommendations.append(
            f"Implement auto-scaling policies with target CPU: 70%, Memory: 80%"
        )
        
        recommendations.append(
            f"Set up monitoring alerts at 80% of recommended capacity"
        )
        
        return recommendations
    
    def analyze_peak_capacity(
        self,
        daily_peak_multiplier: float = 3.0,
        seasonal_peak_multiplier: float = 5.0,
        event_peak_multiplier: float = 10.0
    ) -> Dict[str, Dict]:
        """
        Analyze capacity for different peak scenarios
        
        Returns:
            Dictionary with capacity analysis for each scenario
        """
        scenarios = {
            "normal": {"multiplier": 1.0, "description": "Normal operations"},
            "daily_peak": {"multiplier": daily_peak_multiplier, "description": "Daily peak hours"},
            "seasonal_peak": {"multiplier": seasonal_peak_multiplier, "description": "Seasonal peak (holidays)"},
            "event_peak": {"multiplier": event_peak_multiplier, "description": "Special events/launches"},
        }
        
        results = {}
        for name, config in scenarios.items():
            results[name] = {
                "description": config["description"],
                "load_multiplier": config["multiplier"],
                "recommended_instances": math.ceil(config["multiplier"]),
                "scaling_strategy": self._get_scaling_strategy(config["multiplier"]),
            }
        
        return results
    
    def _get_scaling_strategy(self, multiplier: float) -> str:
        """Determine scaling strategy based on load multiplier"""
        if multiplier <= 1.5:
            return "vertical_scaling"
        elif multiplier <= 3.0:
            return "horizontal_scaling"
        elif multiplier <= 5.0:
            return "auto_scaling_with_warm_pool"
        else:
            return "event_driven_serverless"
    
    def calculate_breaking_point(
        self,
        current_rps: float,
        current_resources: ResourceRequirements,
        resource_limit: ResourceRequirements
    ) -> Dict:
        """
        Calculate the breaking point where system will fail
        
        Args:
            current_rps: Current requests per second
            current_resources: Current resource allocation
            resource_limit: Maximum available resources
        
        Returns:
            Breaking point analysis
        """
        # Calculate resource headroom
        cpu_headroom = resource_limit.cpu_cores / current_resources.cpu_cores
        memory_headroom = resource_limit.memory_gb / current_resources.memory_gb
        network_headroom = resource_limit.network_mbps / current_resources.network_mbps
        
        # Breaking point is the minimum headroom
        breaking_multiplier = min(cpu_headroom, memory_headroom, network_headroom)
        breaking_rps = current_rps * breaking_multiplier
        
        return {
            "current_rps": current_rps,
            "breaking_point_rps": breaking_rps,
            "breaking_multiplier": breaking_multiplier,
            "limiting_resource": self._get_limiting_resource(
                cpu_headroom, memory_headroom, network_headroom
            ),
            "recommendations": [
                f"Current system can handle up to {breaking_rps:.0f} RPS",
                f"Scale {self._get_limiting_resource(cpu_headroom, memory_headroom, network_headroom)} first",
            ],
        }
    
    def _get_limiting_resource(self, cpu: float, memory: float, network: float) -> str:
        """Determine which resource will be the bottleneck"""
        limits = {"cpu": cpu, "memory": memory, "network": network}
        return min(limits, key=limits.get)


# Capacity Planning Scenarios
CAPACITY_SCENARIOS = {
    "current_state": {
        "rps": 50,
        "resources": ResourceRequirements(
            cpu_cores=4,
            memory_gb=16,
            gpu_count=0,
            storage_gb=100,
            network_mbps=100,
        ),
    },
    "6_month_target": {
        "rps": 200,
        "growth_rate": 0.15,  # 15% monthly growth
        "horizon_months": 6,
    },
    "12_month_target": {
        "rps": 500,
        "growth_rate": 0.12,  # 12% monthly growth
        "horizon_months": 12,
    },
    "enterprise_scale": {
        "rps": 2000,
        "growth_rate": 0.10,  # 10% monthly growth
        "horizon_months": 12,
    },
}
