"""
Safety Mechanisms for Chaos Engineering
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
import asyncio

class SafetyLevel(Enum):
    """Safety levels for chaos experiments"""
    GREEN = "green"      # Safe to proceed
    YELLOW = "yellow"    # Caution advised
    RED = "red"          # Stop experiment
    BLACK = "black"      # Emergency stop

class AbortReason(Enum):
    """Reasons for aborting experiment"""
    MANUAL = "manual"
    THRESHOLD_BREACH = "threshold_breach"
    CUSTOMER_IMPACT = "customer_impact"
    ERROR_RATE_SPIKE = "error_rate_spike"
    LATENCY_SPIKE = "latency_spike"
    AVAILABILITY_DROP = "availability_drop"
    EXTERNAL_ALERT = "external_alert"
    TIMEOUT = "timeout"

@dataclass
class SafetyThreshold:
    """Safety threshold configuration"""
    metric_name: str
    warning_value: float
    critical_value: float
    emergency_value: float
    comparison: str = "above"  # above, below
    window_seconds: int = 60

@dataclass
class SafetyCheck:
    """Individual safety check"""
    name: str
    check_function: Callable[[], bool]
    level: SafetyLevel
    auto_abort: bool = False
    message: str = ""

@dataclass
class AbortDecision:
    """Decision to abort experiment"""
    timestamp: datetime
    reason: AbortReason
    level: SafetyLevel
    triggered_by: str
    metrics_at_abort: Dict[str, float]
    experiment_id: str
    rollback_initiated: bool = False

class SafetyMonitor:
    """Monitor safety during chaos experiments"""
    
    def __init__(self):
        self.thresholds: Dict[str, SafetyThreshold] = {}
        self.safety_checks: List[SafetyCheck] = []
        self.abort_handlers: List[Callable[[AbortDecision], None]] = []
        self.current_level = SafetyLevel.GREEN
        self.abort_history: List[AbortDecision] = []
        self.monitoring = False
        self.current_experiment_id: Optional[str] = None
    
    def add_threshold(self, threshold: SafetyThreshold):
        """Add a safety threshold"""
        self.thresholds[threshold.metric_name] = threshold
    
    def add_safety_check(self, check: SafetyCheck):
        """Add a custom safety check"""
        self.safety_checks.append(check)
    
    def register_abort_handler(self, handler: Callable[[AbortDecision], None]):
        """Register an abort handler"""
        self.abort_handlers.append(handler)
    
    async def start_monitoring(self, experiment_id: str):
        """Start safety monitoring"""
        self.monitoring = True
        self.current_experiment_id = experiment_id
        self.current_level = SafetyLevel.GREEN
        
        asyncio.create_task(self._safety_loop())
        print(f"Safety monitoring started for {experiment_id}")
    
    async def stop_monitoring(self):
        """Stop safety monitoring"""
        self.monitoring = False
        self.current_experiment_id = None
        self.current_level = SafetyLevel.GREEN
        print("Safety monitoring stopped")
    
    async def _safety_loop(self):
        """Main safety monitoring loop"""
        while self.monitoring:
            await self._check_thresholds()
            await self._run_safety_checks()
            await asyncio.sleep(5)
    
    async def _check_thresholds(self):
        """Check all configured thresholds"""
        for metric_name, threshold in self.thresholds.items():
            current_value = await self._get_metric_value(metric_name)
            
            level = self._evaluate_threshold(current_value, threshold)
            
            if level == SafetyLevel.EMERGENCY or level == SafetyLevel.RED:
                await self._trigger_abort(
                    reason=self._get_abort_reason(metric_name),
                    level=level,
                    triggered_by=f"threshold:{metric_name}",
                    metrics={metric_name: current_value}
                )
                return
            elif level == SafetyLevel.YELLOW:
                self.current_level = SafetyLevel.YELLOW
                print(f"WARNING: {metric_name} at {current_value}")
    
    def _evaluate_threshold(self, value: float, threshold: SafetyThreshold) -> SafetyLevel:
        """Evaluate value against threshold"""
        if threshold.comparison == "above":
            if value >= threshold.emergency_value:
                return SafetyLevel.EMERGENCY
            elif value >= threshold.critical_value:
                return SafetyLevel.RED
            elif value >= threshold.warning_value:
                return SafetyLevel.YELLOW
        else:
            if value <= threshold.emergency_value:
                return SafetyLevel.EMERGENCY
            elif value <= threshold.critical_value:
                return SafetyLevel.RED
            elif value <= threshold.warning_value:
                return SafetyLevel.YELLOW
        
        return SafetyLevel.GREEN
    
    def _get_abort_reason(self, metric_name: str) -> AbortReason:
        """Get abort reason for metric"""
        if "error" in metric_name.lower():
            return AbortReason.ERROR_RATE_SPIKE
        elif "latency" in metric_name.lower():
            return AbortReason.LATENCY_SPIKE
        elif "availability" in metric_name.lower():
            return AbortReason.AVAILABILITY_DROP
        return AbortReason.THRESHOLD_BREACH
    
    async def _run_safety_checks(self):
        """Run custom safety checks"""
        for check in self.safety_checks:
            try:
                passed = check.check_function()
                
                if not passed:
                    if check.auto_abort and check.level in [SafetyLevel.RED, SafetyLevel.EMERGENCY]:
                        await self._trigger_abort(
                            reason=AbortReason.MANUAL,
                            level=check.level,
                            triggered_by=f"check:{check.name}",
                            metrics={}
                        )
                        return
                    elif check.level == SafetyLevel.YELLOW:
                        self.current_level = SafetyLevel.YELLOW
                        print(f"WARNING: Safety check failed - {check.name}")
            except Exception as e:
                print(f"Safety check error: {check.name} - {e}")
    
    async def _get_metric_value(self, metric_name: str) -> float:
        """Get current metric value"""
        return 0.0
    
    async def _trigger_abort(self, reason: AbortReason, level: SafetyLevel,
                            triggered_by: str, metrics: Dict[str, float]):
        """Trigger experiment abort"""
        decision = AbortDecision(
            timestamp=datetime.utcnow(),
            reason=reason,
            level=level,
            triggered_by=triggered_by,
            metrics_at_abort=metrics,
            experiment_id=self.current_experiment_id,
            rollback_initiated=False
        )
        
        self.abort_history.append(decision)
        self.current_level = level
        
        for handler in self.abort_handlers:
            try:
                handler(decision)
            except Exception as e:
                print(f"Abort handler error: {e}")
        
        print(f"ABORT TRIGGERED: {reason.value} - {triggered_by}")
    
    async def manual_abort(self, reason: str = "Manual abort"):
        """Manual abort trigger"""
        await self._trigger_abort(
            reason=AbortReason.MANUAL,
            level=SafetyLevel.EMERGENCY,
            triggered_by="manual",
            metrics={}
        )

class CircuitBreaker:
    """Circuit breaker for chaos experiments"""
    
    def __init__(self, name: str):
        self.name = name
        self.state = "closed"
        self.failure_count = 0
        self.success_count = 0
        self.failure_threshold = 5
        self.success_threshold = 3
        self.timeout_seconds = 60
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.utcnow()
    
    def record_success(self):
        """Record a successful operation"""
        self.success_count += 1
        self.failure_count = 0
        
        if self.state == "half_open" and self.success_count >= self.success_threshold:
            self._transition_to("closed")
    
    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.success_count = 0
        self.last_failure_time = datetime.utcnow()
        
        if self.state == "closed" and self.failure_count >= self.failure_threshold:
            self._transition_to("open")
        elif self.state == "half_open":
            self._transition_to("open")
    
    def can_execute(self) -> bool:
        """Check if operation can execute"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self._transition_to("half_open")
                    return True
            return False
        elif self.state == "half_open":
            return True
        
        return False
    
    def _transition_to(self, new_state: str):
        """Transition to new state"""
        old_state = self.state
        self.state = new_state
        self.last_state_change = datetime.utcnow()
        print(f"Circuit breaker '{self.name}': {old_state} -> {new_state}")

class BlastRadiusController:
    """Control blast radius of chaos experiments"""
    
    def __init__(self):
        self.max_affected_services = 1
        self.max_affected_percentage = 5.0
        self.max_duration_minutes = 30
        self.production_restrictions = True
        self.current_scope: Dict[str, Any] = {}
    
    def validate_scope(self, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Validate experiment scope"""
        violations = []
        
        affected_services = scope.get("affected_services", [])
        if len(affected_services) > self.max_affected_services:
            violations.append(
                f"Too many services: {len(affected_services)} > {self.max_affected_services}"
            )
        
        affected_percentage = scope.get("affected_percentage", 0)
        if affected_percentage > self.max_affected_percentage:
            violations.append(
                f"Affected percentage too high: {affected_percentage}% > {self.max_affected_percentage}%"
            )
        
        duration_minutes = scope.get("duration_minutes", 0)
        if duration_minutes > self.max_duration_minutes:
            violations.append(
                f"Duration too long: {duration_minutes}min > {self.max_duration_minutes}min"
            )
        
        if self.production_restrictions and scope.get("environment") == "production":
            if not scope.get("approved_by"):
                violations.append("Production experiments require approval")
            if scope.get("duration_minutes", 0) > 15:
                violations.append("Production experiments limited to 15 minutes")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "scope": scope
        }
    
    def calculate_scope(self, experiment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate experiment scope"""
        scope = {
            "affected_services": experiment_config.get("target_services", []),
            "affected_percentage": experiment_config.get("percentage", 0),
            "duration_minutes": experiment_config.get("duration_seconds", 0) / 60,
            "environment": experiment_config.get("environment", "staging"),
            "blast_radius_score": 0
        }
        
        score = 0
        score += len(scope["affected_services"]) * 10
        score += scope["affected_percentage"] * 2
        score += scope["duration_minutes"] * 0.5
        
        if scope["environment"] == "production":
            score *= 2
        
        scope["blast_radius_score"] = score
        
        return scope

class KillSwitch:
    """Emergency kill switch for all chaos experiments"""
    
    def __init__(self):
        self.activated = False
        self.activated_at: Optional[datetime] = None
        self.activated_by: Optional[str] = None
        self.reason: Optional[str] = None
        self.handlers: List[Callable[[], None]] = []
    
    def activate(self, activated_by: str, reason: str):
        """Activate kill switch"""
        self.activated = True
        self.activated_at = datetime.utcnow()
        self.activated_by = activated_by
        self.reason = reason
        
        print(f"KILL SWITCH ACTIVATED by {activated_by}: {reason}")
        
        for handler in self.handlers:
            try:
                handler()
            except Exception as e:
                print(f"Kill switch handler error: {e}")
    
    def deactivate(self, deactivated_by: str):
        """Deactivate kill switch"""
        self.activated = False
        print(f"Kill switch deactivated by {deactivated_by}")
    
    def register_handler(self, handler: Callable[[], None]):
        """Register a handler"""
        self.handlers.append(handler)
    
    def check(self) -> bool:
        """Check if kill switch is active"""
        return self.activated


# Pre-configured safety thresholds
DEFAULT_SAFETY_THRESHOLDS = [
    SafetyThreshold(
        metric_name="error_rate",
        warning_value=0.01,
        critical_value=0.05,
        emergency_value=0.10,
        comparison="above",
        window_seconds=60
    ),
    SafetyThreshold(
        metric_name="p99_latency_ms",
        warning_value=500,
        critical_value=1000,
        emergency_value=5000,
        comparison="above",
        window_seconds=60
    ),
    SafetyThreshold(
        metric_name="availability_percent",
        warning_value=99.9,
        critical_value=99.0,
        emergency_value=95.0,
        comparison="below",
        window_seconds=30
    ),
    SafetyThreshold(
        metric_name="customer_impact_score",
        warning_value=1,
        critical_value=5,
        emergency_value=10,
        comparison="above",
        window_seconds=30
    )
]


async def main():
    """Example usage"""
    print("Safety Mechanisms Demo")
    print("=" * 50)
    
    # Create safety monitor
    monitor = SafetyMonitor()
    
    # Add default thresholds
    for threshold in DEFAULT_SAFETY_THRESHOLDS:
        monitor.add_threshold(threshold)
    
    # Create blast radius controller
    controller = BlastRadiusController()
    
    # Validate experiment scope
    scope = controller.calculate_scope({
        "target_services": ["service-a"],
        "percentage": 10,
        "duration_seconds": 600,
        "environment": "staging"
    })
    
    validation = controller.validate_scope(scope)
    print(f"Scope validation: {validation}")
    
    # Create kill switch
    kill_switch = KillSwitch()
    print(f"Kill switch active: {kill_switch.check()}")


if __name__ == "__main__":
    asyncio.run(main())
