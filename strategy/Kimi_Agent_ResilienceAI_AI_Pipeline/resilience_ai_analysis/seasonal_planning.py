"""
Seasonal Capacity Planning
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class SeasonalEvent(Enum):
    BLACK_FRIDAY = "black_friday"
    CYBER_MONDAY = "cyber_monday"
    CHRISTMAS = "christmas"
    NEW_YEAR = "new_year"
    SUMMER_SALE = "summer_sale"
    BACK_TO_SCHOOL = "back_to_school"
    PRODUCT_LAUNCH = "product_launch"
    CUSTOM = "custom"


@dataclass
class SeasonalPlan:
    """Seasonal capacity plan"""
    event_name: str
    event_type: SeasonalEvent
    start_date: datetime
    end_date: datetime
    
    # Expected load
    expected_peak_multiplier: float
    expected_duration_hours: int
    
    # Capacity adjustments
    pre_scaling_instances: int
    peak_scaling_instances: int
    post_scaling_instances: int
    
    # Timeline
    scale_up_before_hours: int
    scale_down_after_hours: int
    
    # Cost
    estimated_additional_cost: float
    
    # Monitoring
    alert_thresholds: Dict[str, float]


class SeasonalCapacityPlanner:
    """Plan capacity for seasonal events"""
    
    def __init__(self):
        self.event_templates = self._initialize_event_templates()
        self.planned_events: List[SeasonalPlan] = []
        
    def _initialize_event_templates(self) -> Dict[SeasonalEvent, Dict]:
        """Initialize seasonal event templates"""
        return {
            SeasonalEvent.BLACK_FRIDAY: {
                'peak_multiplier': 5.0,
                'duration_hours': 72,
                'scale_up_before_hours': 24,
                'scale_down_after_hours': 12,
                'headroom_percent': 50
            },
            SeasonalEvent.CYBER_MONDAY: {
                'peak_multiplier': 4.0,
                'duration_hours': 24,
                'scale_up_before_hours': 12,
                'scale_down_after_hours': 12,
                'headroom_percent': 50
            },
            SeasonalEvent.CHRISTMAS: {
                'peak_multiplier': 3.0,
                'duration_hours': 168,  # 1 week
                'scale_up_before_hours': 48,
                'scale_down_after_hours': 24,
                'headroom_percent': 40
            },
            SeasonalEvent.SUMMER_SALE: {
                'peak_multiplier': 2.5,
                'duration_hours': 168,
                'scale_up_before_hours': 24,
                'scale_down_after_hours': 24,
                'headroom_percent': 35
            },
            SeasonalEvent.PRODUCT_LAUNCH: {
                'peak_multiplier': 3.0,
                'duration_hours': 48,
                'scale_up_before_hours': 6,
                'scale_down_after_hours': 24,
                'headroom_percent': 45
            },
        }
    
    def create_seasonal_plan(
        self,
        event_name: str,
        event_type: SeasonalEvent,
        start_date: datetime,
        service_config: Dict,
        custom_multiplier: Optional[float] = None
    ) -> SeasonalPlan:
        """Create a seasonal capacity plan"""
        
        import math
        
        template = self.event_templates.get(event_type, {
            'peak_multiplier': 2.0,
            'duration_hours': 24,
            'scale_up_before_hours': 12,
            'scale_down_after_hours': 12,
            'headroom_percent': 30
        })
        
        peak_multiplier = custom_multiplier or template['peak_multiplier']
        
        # Calculate instance requirements
        baseline_instances = service_config.get('baseline_instances', 2)
        capacity_per_instance = service_config.get('capacity_per_instance_rps', 100)
        baseline_rps = service_config.get('baseline_rps', 200)
        
        peak_rps = baseline_rps * peak_multiplier
        headroom_factor = 1 + (template['headroom_percent'] / 100)
        
        pre_scaling = baseline_instances
        peak_scaling = math.ceil((peak_rps * headroom_factor) / capacity_per_instance)
        post_scaling = baseline_instances
        
        # Calculate duration
        duration = timedelta(hours=template['duration_hours'])
        end_date = start_date + duration
        
        # Calculate additional cost
        instance_cost_per_hour = service_config.get('instance_cost_per_hour', 0.10)
        additional_instances = peak_scaling - baseline_instances
        peak_duration_hours = template['duration_hours']
        additional_cost = additional_instances * instance_cost_per_hour * peak_duration_hours
        
        # Set alert thresholds
        alert_thresholds = {
            'cpu_warning': 60,
            'cpu_critical': 75,
            'memory_warning': 70,
            'memory_critical': 80,
            'latency_warning': 500,
            'latency_critical': 1000
        }
        
        plan = SeasonalPlan(
            event_name=event_name,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            expected_peak_multiplier=peak_multiplier,
            expected_duration_hours=template['duration_hours'],
            pre_scaling_instances=pre_scaling,
            peak_scaling_instances=peak_scaling,
            post_scaling_instances=post_scaling,
            scale_up_before_hours=template['scale_up_before_hours'],
            scale_down_after_hours=template['scale_down_after_hours'],
            estimated_additional_cost=additional_cost,
            alert_thresholds=alert_thresholds
        )
        
        self.planned_events.append(plan)
        return plan
    
    def get_scaling_schedule(self, plan: SeasonalPlan) -> List[Dict]:
        """Get detailed scaling schedule for a seasonal plan"""
        
        schedule = []
        
        # Pre-scaling
        scale_up_time = plan.start_date - timedelta(hours=plan.scale_up_before_hours)
        schedule.append({
            'time': scale_up_time,
            'action': 'scale_up',
            'target_instances': plan.peak_scaling_instances,
            'reason': f"Pre-scale for {plan.event_name}"
        })
        
        # Event start
        schedule.append({
            'time': plan.start_date,
            'action': 'monitor',
            'target_instances': plan.peak_scaling_instances,
            'reason': f"{plan.event_name} begins - peak monitoring"
        })
        
        # Event end
        schedule.append({
            'time': plan.end_date,
            'action': 'monitor',
            'target_instances': plan.peak_scaling_instances,
            'reason': f"{plan.event_name} ends - monitoring for cooldown"
        })
        
        # Post-scaling
        scale_down_time = plan.end_date + timedelta(hours=plan.scale_down_after_hours)
        schedule.append({
            'time': scale_down_time,
            'action': 'scale_down',
            'target_instances': plan.post_scaling_instances,
            'reason': f"Post-scale down after {plan.event_name}"
        })
        
        return schedule
    
    def analyze_historical_events(
        self,
        event_type: SeasonalEvent,
        historical_data: List[Dict]
    ) -> Dict:
        """Analyze historical event data to improve planning"""
        
        if not historical_data:
            return {'message': 'No historical data available'}
        
        multipliers = [d.get('peak_multiplier', 1) for d in historical_data]
        durations = [d.get('duration_hours', 24) for d in historical_data]
        
        import numpy as np
        
        return {
            'event_type': event_type.value,
            'historical_events_analyzed': len(historical_data),
            'average_peak_multiplier': np.mean(multipliers),
            'max_peak_multiplier': max(multipliers),
            'p95_peak_multiplier': np.percentile(multipliers, 95),
            'average_duration_hours': np.mean(durations),
            'recommended_multiplier': np.percentile(multipliers, 90),
            'recommended_headroom_percent': 50
        }
    
    def generate_annual_calendar(self, year: int, service_config: Dict) -> List[SeasonalPlan]:
        """Generate annual seasonal capacity calendar"""
        
        events = []
        
        # Black Friday (4th Friday of November)
        nov = datetime(year, 11, 1)
        black_friday = nov + timedelta(days=(25 - nov.weekday()) % 7 + 21)
        events.append(self.create_seasonal_plan(
            f"Black Friday {year}",
            SeasonalEvent.BLACK_FRIDAY,
            black_friday,
            service_config
        ))
        
        # Cyber Monday (Monday after Black Friday)
        cyber_monday = black_friday + timedelta(days=3)
        events.append(self.create_seasonal_plan(
            f"Cyber Monday {year}",
            SeasonalEvent.CYBER_MONDAY,
            cyber_monday,
            service_config
        ))
        
        # Christmas season
        christmas = datetime(year, 12, 20)
        events.append(self.create_seasonal_plan(
            f"Christmas Season {year}",
            SeasonalEvent.CHRISTMAS,
            christmas,
            service_config
        ))
        
        return events
