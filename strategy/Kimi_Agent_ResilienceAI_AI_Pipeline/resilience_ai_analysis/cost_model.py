"""
Cost Modeling for Capacity Planning
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class ResourceUnit(Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    LOAD_BALANCER = "load_balancer"


@dataclass
class CostComponent:
    """Individual cost component"""
    name: str
    unit_type: ResourceUnit
    unit_cost: float
    unit_name: str
    current_units: float
    projected_units: float
    
    @property
    def current_monthly_cost(self) -> float:
        return self.unit_cost * self.current_units
    
    @property
    def projected_monthly_cost(self) -> float:
        return self.unit_cost * self.projected_units
    
    @property
    def cost_difference(self) -> float:
        return self.projected_monthly_cost - self.current_monthly_cost


@dataclass
class CostModelResult:
    """Complete cost model for a service"""
    service_name: str
    timestamp: datetime
    
    # Cost components
    components: List[CostComponent]
    
    # Totals
    current_monthly_total: float
    projected_monthly_total: float
    
    # Optimization
    potential_savings: float
    optimization_recommendations: List[str]
    
    # Breakdown
    cost_by_resource_type: Dict[str, float]


class CostModelingEngine:
    """Cost modeling and optimization engine"""
    
    def __init__(self):
        self.pricing_catalog = self._initialize_pricing()
        self.cost_history: List[CostModelResult] = []
        
    def _initialize_pricing(self) -> Dict:
        """Initialize pricing catalog"""
        return {
            'aws': {
                'ec2': {
                    't3.micro': {'hourly': 0.0104, 'monthly': 7.49},
                    't3.small': {'hourly': 0.0208, 'monthly': 14.98},
                    't3.medium': {'hourly': 0.0416, 'monthly': 29.96},
                    't3.large': {'hourly': 0.0832, 'monthly': 59.92},
                    'm5.large': {'hourly': 0.096, 'monthly': 69.12},
                    'm5.xlarge': {'hourly': 0.192, 'monthly': 138.24},
                    'c5.large': {'hourly': 0.085, 'monthly': 61.20},
                    'c5.xlarge': {'hourly': 0.17, 'monthly': 122.40},
                },
                'rds': {
                    'db.t3.micro': {'hourly': 0.017, 'monthly': 12.24},
                    'db.t3.small': {'hourly': 0.034, 'monthly': 24.48},
                    'db.m5.large': {'hourly': 0.192, 'monthly': 138.24},
                },
                'elasticache': {
                    'cache.t3.micro': {'hourly': 0.0128, 'monthly': 9.22},
                    'cache.t3.small': {'hourly': 0.0256, 'monthly': 18.43},
                },
                'storage': {
                    'gp3': {'gb_month': 0.08},
                    's3_standard': {'gb_month': 0.023},
                },
                'data_transfer': {
                    'internet_out': {'gb': 0.09},
                }
            }
        }
    
    def create_cost_model(
        self,
        service_name: str,
        infrastructure_config: Dict,
        cloud_provider: str = 'aws'
    ) -> CostModelResult:
        """Create cost model from infrastructure configuration"""
        
        components = []
        cost_by_type = {}
        
        # Compute costs
        compute_cost = self._calculate_compute_cost(
            infrastructure_config.get('compute', {}),
            cloud_provider
        )
        components.append(compute_cost)
        cost_by_type['compute'] = compute_cost.current_monthly_cost
        
        # Database costs
        db_cost = self._calculate_database_cost(
            infrastructure_config.get('database', {}),
            cloud_provider
        )
        components.append(db_cost)
        cost_by_type['database'] = db_cost.current_monthly_cost
        
        # Storage costs
        storage_cost = self._calculate_storage_cost(
            infrastructure_config.get('storage', {}),
            cloud_provider
        )
        components.append(storage_cost)
        cost_by_type['storage'] = storage_cost.current_monthly_cost
        
        # Network costs
        network_cost = self._calculate_network_cost(
            infrastructure_config.get('network', {}),
            cloud_provider
        )
        components.append(network_cost)
        cost_by_type['network'] = network_cost.current_monthly_cost
        
        # Calculate totals
        current_total = sum(c.current_monthly_cost for c in components)
        projected_total = sum(c.projected_monthly_cost for c in components)
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(
            components, infrastructure_config
        )
        
        # Calculate potential savings
        potential_savings = self._calculate_potential_savings(components, recommendations)
        
        model = CostModelResult(
            service_name=service_name,
            timestamp=datetime.now(),
            components=components,
            current_monthly_total=current_total,
            projected_monthly_total=projected_total,
            potential_savings=potential_savings,
            optimization_recommendations=recommendations,
            cost_by_resource_type=cost_by_type
        )
        
        self.cost_history.append(model)
        return model
    
    def _calculate_compute_cost(self, config: Dict, provider: str) -> CostComponent:
        """Calculate compute costs"""
        instance_type = config.get('instance_type', 't3.medium')
        instance_count = config.get('instance_count', 1)
        
        pricing = self.pricing_catalog[provider]['ec2'].get(instance_type, {'monthly': 50})
        
        return CostComponent(
            name='Compute (EC2)',
            unit_type=ResourceUnit.COMPUTE,
            unit_cost=pricing['monthly'],
            unit_name='instance',
            current_units=instance_count,
            projected_units=config.get('projected_instance_count', instance_count)
        )
    
    def _calculate_database_cost(self, config: Dict, provider: str) -> CostComponent:
        """Calculate database costs"""
        instance_type = config.get('instance_type', 'db.t3.medium')
        instance_count = config.get('instance_count', 1)
        storage_gb = config.get('storage_gb', 100)
        
        pricing = self.pricing_catalog[provider]['rds'].get(instance_type, {'monthly': 50})
        storage_pricing = self.pricing_catalog[provider]['storage']['gp3']
        
        instance_cost = pricing['monthly'] * instance_count
        storage_cost = storage_pricing['gb_month'] * storage_gb
        
        return CostComponent(
            name='Database (RDS)',
            unit_type=ResourceUnit.DATABASE,
            unit_cost=instance_cost + storage_cost,
            unit_name='instance+storage',
            current_units=1,
            projected_units=1
        )
    
    def _calculate_storage_cost(self, config: Dict, provider: str) -> CostComponent:
        """Calculate storage costs"""
        storage_gb = config.get('total_gb', 500)
        storage_type = config.get('type', 'gp3')
        
        pricing = self.pricing_catalog[provider]['storage'].get(storage_type, {'gb_month': 0.08})
        
        return CostComponent(
            name='Storage (EBS/S3)',
            unit_type=ResourceUnit.STORAGE,
            unit_cost=pricing['gb_month'],
            unit_name='GB',
            current_units=storage_gb,
            projected_units=config.get('projected_gb', storage_gb)
        )
    
    def _calculate_network_cost(self, config: Dict, provider: str) -> CostComponent:
        """Calculate network costs"""
        data_out_gb = config.get('data_transfer_out_gb', 1000)
        
        pricing = self.pricing_catalog[provider]['data_transfer']['internet_out']
        
        return CostComponent(
            name='Data Transfer',
            unit_type=ResourceUnit.NETWORK,
            unit_cost=pricing['gb'],
            unit_name='GB',
            current_units=data_out_gb,
            projected_units=config.get('projected_gb', data_out_gb)
        )
    
    def _generate_optimization_recommendations(
        self, components: List[CostComponent], config: Dict
    ) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        for component in components:
            if component.unit_type == ResourceUnit.COMPUTE:
                utilization = config.get('compute', {}).get('avg_utilization', 50)
                if utilization < 30:
                    recommendations.append(
                        f"Consider downsizing compute instances - utilization only {utilization:.0f}%"
                    )
                if component.current_units > 2:
                    recommendations.append(
                        "Consider Reserved Instances for predictable workloads - potential 30-60% savings"
                    )
            
            if component.unit_type == ResourceUnit.DATABASE:
                if config.get('database', {}).get('read_replicas', 0) == 0:
                    recommendations.append("Consider read replicas to offload primary database")
            
            if component.unit_type == ResourceUnit.STORAGE:
                if component.current_units > 1000:
                    recommendations.append("Consider S3 Intelligent-Tiering for cost optimization")
        
        return recommendations
    
    def _calculate_potential_savings(
        self, components: List[CostComponent], recommendations: List[str]
    ) -> float:
        """Calculate potential savings from recommendations"""
        savings = 0
        
        for component in components:
            if component.unit_type == ResourceUnit.COMPUTE:
                # Reserved instance savings
                savings += component.current_monthly_cost * 0.40
        
        return savings
    
    def compare_scenarios(self, service_name: str, scenarios: Dict[str, Dict]) -> Dict:
        """Compare cost across different scenarios"""
        comparison = {
            'service_name': service_name,
            'scenarios': {}
        }
        
        for scenario_name, config in scenarios.items():
            model = self.create_cost_model(service_name, config)
            comparison['scenarios'][scenario_name] = {
                'monthly_cost': model.current_monthly_total,
                'components': {c.name: c.current_monthly_cost for c in model.components}
            }
        
        # Find cheapest scenario
        if comparison['scenarios']:
            cheapest = min(comparison['scenarios'].items(), key=lambda x: x[1]['monthly_cost'])
            comparison['cheapest_scenario'] = cheapest[0]
        
        return comparison
