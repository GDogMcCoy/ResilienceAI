"""
Scaling Engine for Capacity Planning
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging


class ScalingAction(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    EMERGENCY_SCALE = "emergency_scale"


class ScalingTrigger(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    REQUEST_RATE = "request_rate"
    LATENCY = "latency"
    QUEUE_DEPTH = "queue_depth"
    CUSTOM = "custom"


@dataclass
class ScalingDecision:
    """Scaling decision with justification"""
    timestamp: datetime
    service_name: str
    action: ScalingAction
    current_instances: int
    target_instances: int
    trigger: ScalingTrigger
    trigger_value: float
    threshold: float
    confidence: float
    reason: str
    estimated_cost_impact: float
    cooldown_seconds: int


@dataclass
class ScalingPolicy:
    """Scaling policy configuration"""
    service_name: str
    
    # Instance limits
    min_instances: int
    max_instances: int
    
    # Scale up triggers
    scale_up_threshold: float
    scale_up_increment: int
    scale_up_cooldown: int  # seconds
    
    # Scale down triggers
    scale_down_threshold: float
    scale_down_decrement: int
    scale_down_cooldown: int  # seconds
    
    # Emergency scaling
    emergency_threshold: float
    emergency_increment: int
    
    # Custom metrics
    custom_metrics: Optional[Dict[str, Dict]] = None
    
    # Predictive scaling
    enable_predictive: bool = False
    predictive_window_minutes: int = 30


class ScalingEngine:
    """Intelligent auto-scaling engine"""
    
    def __init__(self):
        self.policies: Dict[str, ScalingPolicy] = {}
        self.scaling_history: List[ScalingDecision] = []
        self.last_scale_time: Dict[str, datetime] = {}
        self.current_instances: Dict[str, int] = {}
        self.logger = logging.getLogger(__name__)
        
        # Scaling hooks (to be implemented by infrastructure)
        self.scale_up_hook: Optional[Callable] = None
        self.scale_down_hook: Optional[Callable] = None
        
    def register_policy(self, policy: ScalingPolicy):
        """Register a scaling policy for a service"""
        self.policies[policy.service_name] = policy
        self.current_instances[policy.service_name] = policy.min_instances
        
    async def evaluate_scaling(
        self,
        service_name: str,
        metrics: Dict[str, float]
    ) -> Optional[ScalingDecision]:
        """Evaluate if scaling is needed based on metrics"""
        
        if service_name not in self.policies:
            self.logger.warning(f"No scaling policy for {service_name}")
            return None
        
        policy = self.policies[service_name]
        current_instances = self.current_instances.get(service_name, policy.min_instances)
        
        # Check cooldown
        if service_name in self.last_scale_time:
            elapsed = (datetime.now() - self.last_scale_time[service_name]).total_seconds()
            if elapsed < min(policy.scale_up_cooldown, policy.scale_down_cooldown):
                return None
        
        # Evaluate triggers
        cpu = metrics.get('cpu_percent', 0)
        memory = metrics.get('memory_percent', 0)
        
        # Emergency scale up
        if cpu > policy.emergency_threshold or memory > policy.emergency_threshold:
            return self._create_decision(
                service_name=service_name,
                action=ScalingAction.EMERGENCY_SCALE,
                current=current_instances,
                target=min(current_instances + policy.emergency_increment, policy.max_instances),
                trigger=ScalingTrigger.CPU if cpu > memory else ScalingTrigger.MEMORY,
                trigger_value=max(cpu, memory),
                threshold=policy.emergency_threshold,
                reason=f"Emergency: CPU={cpu:.1f}%, Memory={memory:.1f}%",
                policy=policy
            )
        
        # Normal scale up
        if cpu > policy.scale_up_threshold or memory > policy.scale_up_threshold:
            return self._create_decision(
                service_name=service_name,
                action=ScalingAction.SCALE_UP,
                current=current_instances,
                target=min(current_instances + policy.scale_up_increment, policy.max_instances),
                trigger=ScalingTrigger.CPU if cpu > memory else ScalingTrigger.MEMORY,
                trigger_value=max(cpu, memory),
                threshold=policy.scale_up_threshold,
                reason=f"High utilization: CPU={cpu:.1f}%, Memory={memory:.1f}%",
                policy=policy
            )
        
        # Scale down
        if (cpu < policy.scale_down_threshold and 
            memory < policy.scale_down_threshold and
            current_instances > policy.min_instances):
            return self._create_decision(
                service_name=service_name,
                action=ScalingAction.SCALE_DOWN,
                current=current_instances,
                target=max(current_instances - policy.scale_down_decrement, policy.min_instances),
                trigger=ScalingTrigger.CPU,
                trigger_value=cpu,
                threshold=policy.scale_down_threshold,
                reason=f"Low utilization: CPU={cpu:.1f}%, Memory={memory:.1f}%",
                policy=policy
            )
        
        return None
    
    def _create_decision(
        self,
        service_name: str,
        action: ScalingAction,
        current: int,
        target: int,
        trigger: ScalingTrigger,
        trigger_value: float,
        threshold: float,
        reason: str,
        policy: ScalingPolicy
    ) -> ScalingDecision:
        """Create a scaling decision"""
        
        # Calculate cost impact (simplified)
        instance_diff = target - current
        cost_per_instance_hour = 0.10  # $0.10 per instance hour
        estimated_cost = instance_diff * cost_per_instance_hour
        
        # Calculate confidence based on how far above/below threshold
        confidence = min(1.0, abs(trigger_value - threshold) / threshold + 0.5)
        
        return ScalingDecision(
            timestamp=datetime.now(),
            service_name=service_name,
            action=action,
            current_instances=current,
            target_instances=target,
            trigger=trigger,
            trigger_value=trigger_value,
            threshold=threshold,
            confidence=confidence,
            reason=reason,
            estimated_cost_impact=estimated_cost,
            cooldown_seconds=policy.scale_up_cooldown if action == ScalingAction.SCALE_UP else policy.scale_down_cooldown
        )
    
    async def execute_scaling(self, decision: ScalingDecision) -> bool:
        """Execute a scaling decision"""
        
        self.logger.info(f"Executing scaling: {decision.action.value} for {decision.service_name}")
        
        try:
            if decision.action in [ScalingAction.SCALE_UP, ScalingAction.EMERGENCY_SCALE]:
                if self.scale_up_hook:
                    await self.scale_up_hook(decision.service_name, decision.target_instances)
            elif decision.action == ScalingAction.SCALE_DOWN:
                if self.scale_down_hook:
                    await self.scale_down_hook(decision.service_name, decision.target_instances)
            
            # Update state
            self.current_instances[decision.service_name] = decision.target_instances
            self.last_scale_time[decision.service_name] = datetime.now()
            self.scaling_history.append(decision)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Scaling execution failed: {e}")
            return False
    
    def get_scaling_history(
        self, 
        service_name: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[ScalingDecision]:
        """Get scaling history"""
        history = self.scaling_history
        
        if service_name:
            history = [d for d in history if d.service_name == service_name]
        
        if since:
            history = [d for d in history if d.timestamp >= since]
        
        return history
    
    def get_scaling_statistics(self, days: int = 7) -> Dict:
        """Get scaling statistics"""
        since = datetime.now() - timedelta(days=days)
        history = [d for d in self.scaling_history if d.timestamp >= since]
        
        scale_up_count = sum(1 for d in history if d.action == ScalingAction.SCALE_UP)
        scale_down_count = sum(1 for d in history if d.action == ScalingAction.SCALE_DOWN)
        emergency_count = sum(1 for d in history if d.action == ScalingAction.EMERGENCY_SCALE)
        
        total_cost_impact = sum(d.estimated_cost_impact for d in history)
        
        return {
            'total_scaling_events': len(history),
            'scale_up_events': scale_up_count,
            'scale_down_events': scale_down_count,
            'emergency_events': emergency_count,
            'total_cost_impact': total_cost_impact,
            'average_confidence': (
                sum(d.confidence for d in history) / len(history) if history else 0
            )
        }
