"""
Predictive Scaling based on load forecasts
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio


@dataclass
class PredictiveScalingPlan:
    """Predictive scaling plan"""
    service_name: str
    scheduled_at: datetime
    execute_at: datetime
    action: str
    target_instances: int
    predicted_load: float
    confidence: float
    reason: str


class PredictiveScalingEngine:
    """Predictive scaling based on forecasted load"""
    
    def __init__(self, scaling_engine):
        self.scaling_engine = scaling_engine
        self.scheduled_plans: List[PredictiveScalingPlan] = []
        self.execution_history: List[PredictiveScalingPlan] = []
        
    async def generate_predictive_plan(
        self,
        service_name: str,
        forecast,
        current_instances: int,
        capacity_per_instance: float
    ) -> List[PredictiveScalingPlan]:
        """Generate predictive scaling plan from forecast"""
        
        plans = []
        policy = self.scaling_engine.policies.get(service_name)
        
        if not policy or not policy.enable_predictive:
            return plans
        
        import math
        
        # Analyze forecast for scaling needs
        for result in forecast.medium_term:
            predicted_load = result.forecast_value
            required_instances = math.ceil(predicted_load / capacity_per_instance)
            
            # Clamp to policy limits
            required_instances = max(
                policy.min_instances,
                min(policy.max_instances, required_instances)
            )
            
            if required_instances != current_instances:
                # Schedule scaling before predicted load
                execute_time = result.timestamp - timedelta(
                    minutes=policy.predictive_window_minutes
                )
                
                if execute_time > datetime.now():
                    plan = PredictiveScalingPlan(
                        service_name=service_name,
                        scheduled_at=datetime.now(),
                        execute_at=execute_time,
                        action='scale_up' if required_instances > current_instances else 'scale_down',
                        target_instances=required_instances,
                        predicted_load=predicted_load,
                        confidence=result.confidence,
                        reason=f"Predicted load {predicted_load:.1f} at {result.timestamp}"
                    )
                    plans.append(plan)
                    current_instances = required_instances
        
        self.scheduled_plans.extend(plans)
        return plans
    
    async def execute_scheduled_plans(self):
        """Execute plans that are due"""
        from scaling_engine import ScalingDecision, ScalingAction, ScalingTrigger
        
        now = datetime.now()
        due_plans = [p for p in self.scheduled_plans if p.execute_at <= now]
        
        for plan in due_plans:
            decision = ScalingDecision(
                timestamp=now,
                service_name=plan.service_name,
                action=ScalingAction.SCALE_UP if plan.action == 'scale_up' else ScalingAction.SCALE_DOWN,
                current_instances=self.scaling_engine.current_instances.get(plan.service_name, 1),
                target_instances=plan.target_instances,
                trigger=ScalingTrigger.CUSTOM,
                trigger_value=plan.predicted_load,
                threshold=0,
                confidence=plan.confidence,
                reason=f"Predictive: {plan.reason}",
                estimated_cost_impact=0,
                cooldown_seconds=0
            )
            
            await self.scaling_engine.execute_scaling(decision)
            self.execution_history.append(plan)
            self.scheduled_plans.remove(plan)
