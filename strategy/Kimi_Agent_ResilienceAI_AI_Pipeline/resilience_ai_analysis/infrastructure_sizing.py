"""
Infrastructure Sizing Calculator
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class InstanceFamily(Enum):
    GENERAL = "general"  # T3, M5
    COMPUTE = "compute"  # C5, C6
    MEMORY = "memory"    # R5, R6
    BURST = "burst"      # T3


@dataclass
class InstanceSpec:
    """Instance specification"""
    name: str
    family: InstanceFamily
    vcpu: int
    memory_gb: float
    network_gbps: float
    ebs_optimized: bool
    cost_per_hour: float
    
    @property
    def cost_per_month(self) -> float:
        return self.cost_per_hour * 24 * 30


@dataclass
class SizingRecommendation:
    """Infrastructure sizing recommendation"""
    service_name: str
    
    # Current sizing
    current_instance_type: str
    current_instance_count: int
    
    # Recommended sizing
    recommended_instance_type: str
    recommended_instance_count: int
    
    # Rationale
    sizing_reason: str
    
    # Cost impact
    current_monthly_cost: float
    recommended_monthly_cost: float
    cost_difference: float
    cost_difference_percent: float
    
    # Performance expectations
    expected_cpu_utilization: float
    expected_memory_utilization: float
    expected_headroom_percent: float


class InfrastructureSizingCalculator:
    """Calculate optimal infrastructure sizing"""
    
    def __init__(self):
        self.instance_catalog = self._initialize_instance_catalog()
        
    def _initialize_instance_catalog(self) -> Dict[str, InstanceSpec]:
        """Initialize instance catalog"""
        return {
            # General purpose
            't3.micro': InstanceSpec('t3.micro', InstanceFamily.BURST, 2, 1, 5, False, 0.0104),
            't3.small': InstanceSpec('t3.small', InstanceFamily.BURST, 2, 2, 5, False, 0.0208),
            't3.medium': InstanceSpec('t3.medium', InstanceFamily.BURST, 2, 4, 5, False, 0.0416),
            't3.large': InstanceSpec('t3.large', InstanceFamily.BURST, 2, 8, 5, False, 0.0832),
            'm5.large': InstanceSpec('m5.large', InstanceFamily.GENERAL, 2, 8, 10, True, 0.096),
            'm5.xlarge': InstanceSpec('m5.xlarge', InstanceFamily.GENERAL, 4, 16, 10, True, 0.192),
            'm5.2xlarge': InstanceSpec('m5.2xlarge', InstanceFamily.GENERAL, 8, 32, 10, True, 0.384),
            
            # Compute optimized
            'c5.large': InstanceSpec('c5.large', InstanceFamily.COMPUTE, 2, 4, 10, True, 0.085),
            'c5.xlarge': InstanceSpec('c5.xlarge', InstanceFamily.COMPUTE, 4, 8, 10, True, 0.17),
            'c5.2xlarge': InstanceSpec('c5.2xlarge', InstanceFamily.COMPUTE, 8, 16, 10, True, 0.34),
            
            # Memory optimized
            'r5.large': InstanceSpec('r5.large', InstanceFamily.MEMORY, 2, 16, 10, True, 0.126),
            'r5.xlarge': InstanceSpec('r5.xlarge', InstanceFamily.MEMORY, 4, 32, 10, True, 0.252),
        }
    
    def calculate_optimal_sizing(
        self,
        service_name: str,
        workload_profile: Dict,
        constraints: Optional[Dict] = None
    ) -> SizingRecommendation:
        """Calculate optimal infrastructure sizing"""
        
        constraints = constraints or {}
        
        # Extract workload requirements
        required_rps = workload_profile.get('required_rps', 100)
        peak_rps = workload_profile.get('peak_rps', required_rps * 2)
        cpu_per_request = workload_profile.get('cpu_ms_per_request', 10)
        memory_per_request = workload_profile.get('memory_mb_per_request', 5)
        
        target_cpu_util = constraints.get('target_cpu_utilization', 70)
        target_memory_util = constraints.get('target_memory_utilization', 75)
        max_cost_per_month = constraints.get('max_cost_per_month', float('inf'))
        
        # Calculate total resource requirements
        total_cpu_required = (peak_rps * cpu_per_request) / 1000
        total_memory_required = peak_rps * memory_per_request
        
        # Find suitable instance types
        candidates = self._find_suitable_instances(
            total_cpu_required,
            total_memory_required,
            target_cpu_util,
            target_memory_util
        )
        
        # Select optimal configuration
        best_config = self._select_optimal_config(
            candidates,
            total_cpu_required,
            total_memory_required,
            max_cost_per_month
        )
        
        # Calculate expected utilization
        expected_cpu = (total_cpu_required / best_config['total_vcpu']) * 100
        expected_memory = (total_memory_required / (best_config['total_memory_gb'] * 1024)) * 100
        
        return SizingRecommendation(
            service_name=service_name,
            current_instance_type=workload_profile.get('current_instance_type', 'unknown'),
            current_instance_count=workload_profile.get('current_instance_count', 1),
            recommended_instance_type=best_config['instance_type'],
            recommended_instance_count=best_config['instance_count'],
            sizing_reason=best_config['reason'],
            current_monthly_cost=workload_profile.get('current_monthly_cost', 0),
            recommended_monthly_cost=best_config['monthly_cost'],
            cost_difference=best_config['monthly_cost'] - workload_profile.get('current_monthly_cost', 0),
            cost_difference_percent=(
                (best_config['monthly_cost'] - workload_profile.get('current_monthly_cost', 0)) /
                workload_profile.get('current_monthly_cost', 1) * 100
            ) if workload_profile.get('current_monthly_cost', 0) > 0 else 0,
            expected_cpu_utilization=expected_cpu,
            expected_memory_utilization=expected_memory,
            expected_headroom_percent=100 - max(expected_cpu, expected_memory)
        )
    
    def _find_suitable_instances(
        self,
        cpu_required: float,
        memory_required: float,
        target_cpu_util: float,
        target_memory_util: float
    ) -> List[Dict]:
        """Find instance configurations that meet requirements"""
        
        candidates = []
        
        for name, spec in self.instance_catalog.items():
            # Calculate how many instances needed
            cpu_capacity_per_instance = spec.vcpu * (target_cpu_util / 100)
            memory_capacity_per_instance = spec.memory_gb * 1024 * (target_memory_util / 100)
            
            import math
            instances_for_cpu = math.ceil(cpu_required / cpu_capacity_per_instance)
            instances_for_memory = math.ceil(memory_required / memory_capacity_per_instance)
            instance_count = max(instances_for_cpu, instances_for_memory, 1)
            
            total_vcpu = spec.vcpu * instance_count
            total_memory = spec.memory_gb * instance_count
            monthly_cost = spec.cost_per_month * instance_count
            
            candidates.append({
                'instance_type': name,
                'instance_count': instance_count,
                'total_vcpu': total_vcpu,
                'total_memory_gb': total_memory,
                'monthly_cost': monthly_cost,
                'spec': spec
            })
        
        return candidates
    
    def _select_optimal_config(
        self,
        candidates: List[Dict],
        cpu_required: float,
        memory_required: float,
        max_cost: float
    ) -> Dict:
        """Select optimal configuration from candidates"""
        
        # Filter by cost
        affordable = [c for c in candidates if c['monthly_cost'] <= max_cost]
        
        if not affordable:
            return min(candidates, key=lambda x: x['monthly_cost'])
        
        # Score candidates based on efficiency and cost
        scored = []
        for config in affordable:
            # Efficiency score
            cpu_efficiency = cpu_required / config['total_vcpu']
            memory_efficiency = memory_required / (config['total_memory_gb'] * 1024)
            efficiency = (cpu_efficiency + memory_efficiency) / 2
            
            # Cost efficiency
            cost_per_vcpu = config['monthly_cost'] / config['total_vcpu']
            
            # Combined score (lower is better)
            score = cost_per_vcpu / efficiency
            
            scored.append((config, score))
        
        # Select best scoring configuration
        best = min(scored, key=lambda x: x[1])[0]
        best['reason'] = f"Optimal balance of cost (${best['monthly_cost']:.2f}/month) and resource efficiency"
        
        return best
    
    def generate_sizing_report(
        self,
        services: List[str],
        workload_profiles: Dict[str, Dict]
    ) -> Dict:
        """Generate sizing report for multiple services"""
        
        from datetime import datetime
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'services': [],
            'total_current_cost': 0,
            'total_recommended_cost': 0,
            'potential_savings': 0
        }
        
        for service in services:
            profile = workload_profiles.get(service, {})
            recommendation = self.calculate_optimal_sizing(service, profile)
            
            report['services'].append({
                'name': service,
                'current': {
                    'instance_type': recommendation.current_instance_type,
                    'instance_count': recommendation.current_instance_count,
                    'monthly_cost': recommendation.current_monthly_cost
                },
                'recommended': {
                    'instance_type': recommendation.recommended_instance_type,
                    'instance_count': recommendation.recommended_instance_count,
                    'monthly_cost': recommendation.recommended_monthly_cost,
                    'reason': recommendation.sizing_reason
                },
                'expected_utilization': {
                    'cpu': recommendation.expected_cpu_utilization,
                    'memory': recommendation.expected_memory_utilization,
                    'headroom': recommendation.expected_headroom_percent
                },
                'cost_impact': {
                    'difference': recommendation.cost_difference,
                    'difference_percent': recommendation.cost_difference_percent
                }
            })
            
            report['total_current_cost'] += recommendation.current_monthly_cost
            report['total_recommended_cost'] += recommendation.recommended_monthly_cost
        
        report['potential_savings'] = report['total_current_cost'] - report['total_recommended_cost']
        
        return report
