"""
Cost Optimization for ResilienceAI Edge
=======================================
Analyzes and optimizes edge deployment costs.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json


class CostTier(Enum):
    """Cost tiers for edge deployment"""
    BUDGET = "budget"
    STANDARD = "standard"
    PERFORMANCE = "performance"
    ENTERPRISE = "enterprise"


@dataclass
class EdgeDeviceSpec:
    """Edge device specification"""
    name: str
    compute_units: int
    memory_gb: float
    storage_gb: float
    gpu_enabled: bool
    power_consumption_watts: float
    unit_cost_usd: float
    monthly_operational_cost_usd: float


@dataclass
class WorkloadProfile:
    """Workload characteristics"""
    name: str
    inference_requests_per_day: int
    avg_inference_latency_ms: float
    data_storage_gb: float
    network_egress_gb_per_day: float
    availability_required: float


class CostAnalyzer:
    """Analyzes costs for edge deployment scenarios"""
    
    DEVICE_SPECS = {
        "raspberry_pi_4": EdgeDeviceSpec(
            name="Raspberry Pi 4",
            compute_units=4,
            memory_gb=8,
            storage_gb=128,
            gpu_enabled=False,
            power_consumption_watts=7.5,
            unit_cost_usd=150,
            monthly_operational_cost_usd=5
        ),
        "nvidia_jetson_nano": EdgeDeviceSpec(
            name="NVIDIA Jetson Nano",
            compute_units=4,
            memory_gb=4,
            storage_gb=64,
            gpu_enabled=True,
            power_consumption_watts=10,
            unit_cost_usd=300,
            monthly_operational_cost_usd=8
        ),
        "nvidia_jetson_xavier": EdgeDeviceSpec(
            name="NVIDIA Jetson Xavier NX",
            compute_units=6,
            memory_gb=8,
            storage_gb=256,
            gpu_enabled=True,
            power_consumption_watts=15,
            unit_cost_usd=600,
            monthly_operational_cost_usd=12
        ),
        "intel_nuc": EdgeDeviceSpec(
            name="Intel NUC",
            compute_units=8,
            memory_gb=32,
            storage_gb=512,
            gpu_enabled=False,
            power_consumption_watts=65,
            unit_cost_usd=800,
            monthly_operational_cost_usd=20
        ),
        "edge_server": EdgeDeviceSpec(
            name="Edge Server",
            compute_units=32,
            memory_gb=128,
            storage_gb=2000,
            gpu_enabled=True,
            power_consumption_watts=300,
            unit_cost_usd=5000,
            monthly_operational_cost_usd=100
        )
    }
    
    CLOUD_COSTS = {
        "inference_per_1k_requests": 0.20,
        "storage_per_gb_month": 0.023,
        "data_transfer_per_gb": 0.09,
        "compute_per_hour": 0.10
    }
    
    def __init__(self):
        self.scenarios = []
        
    def calculate_edge_cost(self, device_spec: EdgeDeviceSpec, node_count: int, deployment_months: int) -> Dict[str, float]:
        """Calculate total edge deployment cost"""
        capex = device_spec.unit_cost_usd * node_count
        
        monthly_opex = (
            device_spec.monthly_operational_cost_usd * node_count +
            self._calculate_power_cost(device_spec, node_count) +
            self._calculate_maintenance_cost(device_spec, node_count)
        )
        
        total_opex = monthly_opex * deployment_months
        total_cost = capex + total_opex
        
        return {
            "capex_usd": capex,
            "monthly_opex_usd": monthly_opex,
            "total_opex_usd": total_opex,
            "total_cost_usd": total_cost,
            "cost_per_node_per_month": total_cost / node_count / deployment_months
        }
        
    def _calculate_power_cost(self, device_spec: EdgeDeviceSpec, node_count: int) -> float:
        """Calculate monthly power cost"""
        kwh_per_month = (device_spec.power_consumption_watts * 24 * 30) / 1000
        return kwh_per_month * 0.12 * node_count
        
    def _calculate_maintenance_cost(self, device_spec: EdgeDeviceSpec, node_count: int) -> float:
        """Calculate monthly maintenance cost"""
        annual_maintenance = device_spec.unit_cost_usd * 0.10
        return (annual_maintenance / 12) * node_count
        
    def calculate_cloud_cost(self, workload: WorkloadProfile, deployment_months: int) -> Dict[str, float]:
        """Calculate equivalent cloud-only cost"""
        monthly_inferences = workload.inference_requests_per_day * 30
        inference_cost = (monthly_inferences / 1000) * self.CLOUD_COSTS["inference_per_1k_requests"]
        
        storage_cost = workload.data_storage_gb * self.CLOUD_COSTS["storage_per_gb_month"]
        data_transfer_cost = workload.network_egress_gb_per_day * 30 * self.CLOUD_COSTS["data_transfer_per_gb"]
        
        compute_hours = 730
        compute_cost = compute_hours * self.CLOUD_COSTS["compute_per_hour"]
        
        monthly_cost = inference_cost + storage_cost + data_transfer_cost + compute_cost
        
        return {
            "monthly_inference_cost": inference_cost,
            "monthly_storage_cost": storage_cost,
            "monthly_data_transfer_cost": data_transfer_cost,
            "monthly_compute_cost": compute_cost,
            "monthly_total": monthly_cost,
            "total_cost": monthly_cost * deployment_months
        }
        
    def compare_scenarios(self, workload: WorkloadProfile, deployment_months: int = 36) -> List[Dict[str, Any]]:
        """Compare different deployment scenarios"""
        scenarios = []
        
        cloud_cost = self.calculate_cloud_cost(workload, deployment_months)
        scenarios.append({
            "name": "Cloud-Only",
            "type": "cloud",
            "total_cost": cloud_cost["total_cost"],
            "monthly_cost": cloud_cost["monthly_total"],
            "latency_ms": 150,
            "availability": 0.999,
            "details": cloud_cost
        })
        
        for device_key, device_spec in self.DEVICE_SPECS.items():
            node_count = self._estimate_node_count(device_spec, workload)
            edge_cost = self.calculate_edge_cost(device_spec, node_count, deployment_months)
            hybrid_cost = self._calculate_hybrid_cost(edge_cost, cloud_cost, workload)
            
            scenarios.append({
                "name": f"Edge-{device_spec.name}",
                "type": "edge",
                "device": device_key,
                "node_count": node_count,
                "total_cost": edge_cost["total_cost_usd"],
                "monthly_cost": edge_cost["monthly_opex_usd"],
                "latency_ms": workload.avg_inference_latency_ms if device_spec.gpu_enabled else workload.avg_inference_latency_ms * 2,
                "availability": 0.95 + (0.01 * node_count),
                "details": edge_cost
            })
            
            scenarios.append({
                "name": f"Hybrid-{device_spec.name}",
                "type": "hybrid",
                "device": device_key,
                "node_count": node_count,
                "total_cost": hybrid_cost["total"],
                "monthly_cost": hybrid_cost["monthly"],
                "latency_ms": workload.avg_inference_latency_ms,
                "availability": 0.995,
                "details": hybrid_cost
            })
            
        scenarios.sort(key=lambda x: x["total_cost"])
        return scenarios
        
    def _estimate_node_count(self, device_spec: EdgeDeviceSpec, workload: WorkloadProfile) -> int:
        """Estimate required node count for workload"""
        requests_per_day_per_node = device_spec.compute_units * 10000
        if device_spec.gpu_enabled:
            requests_per_day_per_node *= 5
            
        required_nodes = workload.inference_requests_per_day / requests_per_day_per_node
        return max(1, int(required_nodes * 1.5))
        
    def _calculate_hybrid_cost(self, edge_cost: Dict[str, float], cloud_cost: Dict[str, float], workload: WorkloadProfile) -> Dict[str, float]:
        """Calculate hybrid deployment cost"""
        edge_monthly = edge_cost["monthly_opex_usd"]
        cloud_monthly = cloud_cost["monthly_total"] * 0.2
        
        return {
            "edge_monthly": edge_monthly,
            "cloud_monthly": cloud_monthly,
            "monthly": edge_monthly + cloud_monthly,
            "total": (edge_monthly + cloud_monthly) * 36 + edge_cost["capex_usd"]
        }
        
    def recommend_deployment(self, workload: WorkloadProfile, max_budget_monthly: Optional[float] = None,
                            max_latency_ms: Optional[float] = None, min_availability: Optional[float] = None) -> Dict[str, Any]:
        """Recommend optimal deployment based on constraints"""
        scenarios = self.compare_scenarios(workload)
        
        valid_scenarios = scenarios
        
        if max_budget_monthly:
            valid_scenarios = [s for s in valid_scenarios if s["monthly_cost"] <= max_budget_monthly]
        if max_latency_ms:
            valid_scenarios = [s for s in valid_scenarios if s["latency_ms"] <= max_latency_ms]
        if min_availability:
            valid_scenarios = [s for s in valid_scenarios if s["availability"] >= min_availability]
            
        if not valid_scenarios:
            return {
                "recommendation": None,
                "reason": "No scenarios meet all constraints",
                "alternatives": scenarios[:3]
            }
            
        best = valid_scenarios[0]
        
        return {
            "recommendation": best,
            "alternatives": valid_scenarios[1:4],
            "all_scenarios": scenarios,
            "savings_vs_cloud": scenarios[0]["total_cost"] - best["total_cost"] if scenarios[0]["type"] == "cloud" else None
        }


if __name__ == "__main__":
    analyzer = CostAnalyzer()
    
    workload = WorkloadProfile(
        name="Disaster Response Site",
        inference_requests_per_day=50000,
        avg_inference_latency_ms=100,
        data_storage_gb=500,
        network_egress_gb_per_day=10,
        availability_required=0.99
    )
    
    recommendation = analyzer.recommend_deployment(
        workload,
        max_budget_monthly=500,
        max_latency_ms=150,
        min_availability=0.95
    )
    
    print(json.dumps(recommendation, indent=2))
