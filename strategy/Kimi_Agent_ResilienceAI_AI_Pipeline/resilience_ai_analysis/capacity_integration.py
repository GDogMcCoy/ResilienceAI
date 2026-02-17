"""
Capacity Planning System Integration
Main integration module for all capacity planning components
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging


class CapacityPlanningSystem:
    """Integrated capacity planning system"""
    
    def __init__(self):
        self.resource_monitor = None
        self.load_forecaster = None
        self.scaling_engine = None
        self.capacity_model = None
        self.bottleneck_detector = None
        self.cost_model = None
        self.growth_projector = None
        self.baseline_manager = None
        self.sizing_calculator = None
        self.seasonal_planner = None
        
        self.logger = logging.getLogger(__name__)
        self.running = False
        
    async def initialize(self):
        """Initialize the capacity planning system"""
        self.logger.info("Initializing Capacity Planning System...")
        
        # Import components
        from resource_monitor import ResourceMonitor
        from load_forecaster import LoadForecaster
        from scaling_engine import ScalingEngine, ScalingPolicy
        from bottleneck_detector import BottleneckDetector
        from cost_model import CostModelingEngine
        from growth_projections import GrowthProjector
        from performance_baselines import BaselineManager
        from infrastructure_sizing import InfrastructureSizingCalculator
        from seasonal_planning import SeasonalCapacityPlanner
        from capacity_model import CapacityModel
        
        # Initialize components
        self.resource_monitor = ResourceMonitor()
        self.load_forecaster = LoadForecaster()
        self.scaling_engine = ScalingEngine()
        self.bottleneck_detector = BottleneckDetector()
        self.cost_model = CostModelingEngine()
        self.growth_projector = GrowthProjector()
        self.baseline_manager = BaselineManager()
        self.sizing_calculator = InfrastructureSizingCalculator()
        self.seasonal_planner = SeasonalCapacityPlanner()
        self.capacity_model = CapacityModel()
        
        # Register default scaling policies
        default_policy = ScalingPolicy(
            service_name="default",
            min_instances=2,
            max_instances=20,
            scale_up_threshold=75,
            scale_up_increment=2,
            scale_up_cooldown=300,
            scale_down_threshold=40,
            scale_down_decrement=1,
            scale_down_cooldown=600,
            emergency_threshold=90,
            emergency_increment=5,
            enable_predictive=True,
            predictive_window_minutes=30
        )
        self.scaling_engine.register_policy(default_policy)
        
        self.logger.info("Capacity Planning System initialized")
    
    async def run_continuous_monitoring(self, interval_seconds: int = 60):
        """Run continuous capacity monitoring"""
        self.running = True
        
        while self.running:
            try:
                await self._execute_planning_cycle()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"Error in planning cycle: {e}")
                await asyncio.sleep(10)
    
    async def _execute_planning_cycle(self):
        """Execute a single capacity planning cycle"""
        cycle_start = datetime.now()
        
        # 1. Collect metrics
        metrics = await self.resource_monitor.collect_metrics()
        
        # 2. Check for bottlenecks
        bottlenecks = self.bottleneck_detector.identify_bottlenecks(
            "system",
            {
                'cpu_percent': metrics.cpu_percent,
                'memory_percent': metrics.memory_percent,
                'disk_utilization': metrics.disk_percent
            }
        )
        
        # 3. Evaluate scaling needs
        for service_name in self.scaling_engine.policies.keys():
            scaling_decision = await self.scaling_engine.evaluate_scaling(
                service_name,
                {
                    'cpu_percent': metrics.cpu_percent,
                    'memory_percent': metrics.memory_percent,
                    'requests_per_second': 0
                }
            )
            
            if scaling_decision and scaling_decision.confidence > 0.7:
                await self.scaling_engine.execute_scaling(scaling_decision)
        
        # 4. Check alerts
        alerts = self.resource_monitor.check_alerts()
        for alert in alerts:
            self.logger.warning(f"Alert: {alert['message']}")
        
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        self.logger.debug(f"Planning cycle completed in {cycle_duration:.2f}s")
    
    async def generate_capacity_report(self) -> Dict[str, Any]:
        """Generate comprehensive capacity report"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'current_metrics': self._get_current_metrics_summary(),
            'scaling_statistics': self.scaling_engine.get_scaling_statistics(),
            'bottleneck_analysis': self.bottleneck_detector.analyze_bottleneck_patterns(),
            'baseline_report': self.baseline_manager.get_baseline_report(),
            'recommendations': []
        }
        
        # Add recommendations
        report['recommendations'] = self._generate_recommendations()
        
        return report
    
    def _get_current_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics"""
        if not self.resource_monitor.metrics_history:
            return {'status': 'no_data'}
        
        latest = self.resource_monitor.metrics_history[-1]
        stats = self.resource_monitor.calculate_statistics(timedelta(hours=1))
        
        return {
            'timestamp': latest.timestamp.isoformat(),
            'cpu': {
                'current': latest.cpu_percent,
                '1h_avg': stats.get('cpu_percent', {}).get('mean', 0)
            },
            'memory': {
                'current': latest.memory_percent,
                '1h_avg': stats.get('memory_percent', {}).get('mean', 0)
            },
            'disk': {
                'current': latest.disk_percent,
                '1h_avg': stats.get('disk_percent', {}).get('mean', 0)
            }
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate capacity recommendations"""
        recommendations = []
        
        # Check for chronic high utilization
        stats = self.resource_monitor.calculate_statistics(timedelta(days=7))
        
        cpu_stats = stats.get('cpu_percent', {})
        if cpu_stats.get('p95', 0) > 85:
            recommendations.append(
                "CPU utilization consistently high (P95 > 85%). Consider scaling up or optimizing."
            )
        
        memory_stats = stats.get('memory_percent', {})
        if memory_stats.get('p95', 0) > 85:
            recommendations.append(
                "Memory utilization consistently high (P95 > 85%). Consider scaling up."
            )
        
        # Check scaling frequency
        scaling_stats = self.scaling_engine.get_scaling_statistics(days=7)
        if scaling_stats['total_scaling_events'] > 50:
            recommendations.append(
                f"High scaling frequency ({scaling_stats['total_scaling_events']} events/week). "
                "Consider adjusting scaling thresholds or implementing predictive scaling."
            )
        
        return recommendations
    
    def stop(self):
        """Stop the capacity planning system"""
        self.running = False
        self.logger.info("Capacity Planning System stopped")


# Example usage and initialization
async def main():
    """Main entry point for capacity planning system"""
    
    # Initialize system
    system = CapacityPlanningSystem()
    await system.initialize()
    
    # Start continuous monitoring
    monitoring_task = asyncio.create_task(
        system.run_continuous_monitoring(interval_seconds=60)
    )
    
    # Generate initial report
    report = await system.generate_capacity_report()
    print(f"Capacity Report: {report}")
    
    # Run for a while
    await asyncio.sleep(3600)  # 1 hour
    
    # Stop system
    system.stop()
    monitoring_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
