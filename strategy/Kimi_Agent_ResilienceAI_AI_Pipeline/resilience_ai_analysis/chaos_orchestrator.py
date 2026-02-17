"""
Chaos Orchestrator for ResilienceAI
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import uuid

class ExperimentStatus(Enum):
    """Status of chaos experiment"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ROLLING_BACK = "rolling_back"

class SafetyStatus(Enum):
    """Safety status during experiment"""
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class BlastRadius:
    """Define blast radius for experiment"""
    max_affected_services: int
    max_affected_users_percentage: float
    max_affected_regions: int
    max_duration_seconds: int
    can_affect_production: bool = False
    requires_approval: bool = True
    
    def validate_scope(self, scope: Dict[str, Any]) -> bool:
        """Validate if scope is within blast radius"""
        return (
            scope.get("affected_services", 0) <= self.max_affected_services and
            scope.get("affected_users_percentage", 0) <= self.max_affected_users_percentage and
            scope.get("affected_regions", 0) <= self.max_affected_regions and
            scope.get("duration_seconds", 0) <= self.max_duration_seconds
        )

@dataclass
class SafetyControls:
    """Safety controls for chaos experiments"""
    circuit_breaker_threshold: float = 0.1
    max_latency_increase_percentage: float = 50.0
    min_availability_threshold: float = 99.0
    auto_abort_on_critical: bool = True
    notification_channels: List[str] = field(default_factory=list)
    emergency_contacts: List[str] = field(default_factory=list)
    
    def check_safety(self, metrics: Dict[str, float]) -> SafetyStatus:
        """Check safety status based on metrics"""
        if (metrics.get("error_rate", 0) > self.circuit_breaker_threshold * 2 or
            metrics.get("availability", 100) < 95.0):
            return SafetyStatus.EMERGENCY
        
        if (metrics.get("error_rate", 0) > self.circuit_breaker_threshold or
            metrics.get("latency_increase", 0) > self.max_latency_increase_percentage):
            return SafetyStatus.CRITICAL
        
        if (metrics.get("error_rate", 0) > self.circuit_breaker_threshold * 0.5 or
            metrics.get("latency_increase", 0) > self.max_latency_increase_percentage * 0.5):
            return SafetyStatus.WARNING
        
        return SafetyStatus.SAFE

@dataclass
class ChaosExperiment(ABC):
    """Base class for chaos experiments"""
    id: Optional[str] = None
    name: str = ""
    description: str = ""
    scope: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: int = 60
    approved: bool = False
    status: ExperimentStatus = ExperimentStatus.PENDING
    safety_status: SafetyStatus = SafetyStatus.SAFE
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None
    abort_reason: Optional[str] = None
    
    @abstractmethod
    async def execute(self):
        """Execute the experiment"""
        pass
    
    @abstractmethod
    async def rollback(self):
        """Rollback the experiment effects"""
        pass
    
    def get_results(self) -> Dict[str, Any]:
        """Get experiment results"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "safety_status": self.safety_status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else None,
            "error": self.error,
            "abort_reason": self.abort_reason
        }

class ChaosOrchestrator:
    """Main orchestrator for chaos experiments"""
    
    def __init__(self):
        self.experiments: Dict[str, ChaosExperiment] = {}
        self.safety_controls = SafetyControls()
        self.blast_radius_config = BlastRadius(
            max_affected_services=1,
            max_affected_users_percentage=1.0,
            max_affected_regions=1,
            max_duration_seconds=300,
            can_affect_production=False,
            requires_approval=True
        )
        self.running = False
        self._lock = asyncio.Lock()
    
    async def register_experiment(self, experiment: ChaosExperiment) -> str:
        """Register a new experiment"""
        experiment_id = str(uuid.uuid4())
        experiment.id = experiment_id
        async with self._lock:
            self.experiments[experiment_id] = experiment
        return experiment_id
    
    async def start_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Start a chaos experiment"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return {"error": "Experiment not found"}
        
        if not self.blast_radius_config.validate_scope(experiment.scope):
            return {"error": "Experiment scope exceeds blast radius"}
        
        if self.blast_radius_config.requires_approval and not experiment.approved:
            return {"error": "Experiment requires approval"}
        
        experiment.status = ExperimentStatus.RUNNING
        experiment.start_time = datetime.utcnow()
        
        asyncio.create_task(self._monitor_experiment(experiment))
        asyncio.create_task(self._execute_experiment(experiment))
        
        return {
            "experiment_id": experiment_id,
            "status": experiment.status.value,
            "started_at": experiment.start_time.isoformat()
        }
    
    async def _monitor_experiment(self, experiment: ChaosExperiment):
        """Monitor experiment and check safety"""
        while experiment.status == ExperimentStatus.RUNNING:
            metrics = await self._collect_metrics(experiment)
            safety_status = self.safety_controls.check_safety(metrics)
            
            if safety_status == SafetyStatus.EMERGENCY and self.safety_controls.auto_abort_on_critical:
                await self.abort_experiment(experiment.id, "Emergency safety threshold breached")
                break
            
            experiment.safety_status = safety_status
            experiment.current_metrics = metrics
            
            await asyncio.sleep(5)
    
    async def _execute_experiment(self, experiment: ChaosExperiment):
        """Execute the experiment"""
        try:
            await experiment.execute()
            experiment.status = ExperimentStatus.COMPLETED
        except Exception as e:
            experiment.status = ExperimentStatus.FAILED
            experiment.error = str(e)
        finally:
            experiment.end_time = datetime.utcnow()
            await self._store_results(experiment)
    
    async def abort_experiment(self, experiment_id: str, reason: str):
        """Abort a running experiment"""
        experiment = self.experiments.get(experiment_id)
        if experiment and experiment.status == ExperimentStatus.RUNNING:
            experiment.status = ExperimentStatus.ABORTED
            experiment.abort_reason = reason
            await experiment.rollback()
    
    async def _collect_metrics(self, experiment: ChaosExperiment) -> Dict[str, float]:
        """Collect metrics for experiment monitoring"""
        return {
            "error_rate": 0.0,
            "latency_increase": 0.0,
            "availability": 100.0
        }
    
    async def _store_results(self, experiment: ChaosExperiment):
        """Store experiment results"""
        pass


class NetworkLatencyExperiment(ChaosExperiment):
    """Network latency chaos experiment"""
    
    def __init__(self, target_service: str, latency_ms: int, duration_seconds: int):
        super().__init__()
        self.name = f"Network Latency - {target_service}"
        self.description = f"Inject {latency_ms}ms latency into {target_service}"
        self.duration_seconds = duration_seconds
        self.target_service = target_service
        self.latency_ms = latency_ms
    
    async def execute(self):
        """Execute network latency experiment"""
        print(f"Injecting {self.latency_ms}ms latency into {self.target_service}")
        await asyncio.sleep(self.duration_seconds)
    
    async def rollback(self):
        """Rollback network latency"""
        print(f"Removing latency from {self.target_service}")


class InstanceFailureExperiment(ChaosExperiment):
    """Instance failure chaos experiment"""
    
    def __init__(self, target_instance: str, duration_seconds: int):
        super().__init__()
        self.name = f"Instance Failure - {target_instance}"
        self.description = f"Simulate failure of {target_instance}"
        self.duration_seconds = duration_seconds
        self.target_instance = target_instance
    
    async def execute(self):
        """Execute instance failure experiment"""
        print(f"Simulating failure of {self.target_instance}")
        await asyncio.sleep(self.duration_seconds)
    
    async def rollback(self):
        """Restore instance"""
        print(f"Restoring {self.target_instance}")


async def main():
    """Example usage"""
    print("Chaos Orchestrator Demo")
    print("=" * 50)
    
    orchestrator = ChaosOrchestrator()
    
    # Create and register experiment
    experiment = NetworkLatencyExperiment(
        target_service="ml-inference",
        latency_ms=200,
        duration_seconds=10
    )
    experiment.approved = True
    
    experiment_id = await orchestrator.register_experiment(experiment)
    print(f"Registered experiment: {experiment_id}")
    
    # Start experiment
    result = await orchestrator.start_experiment(experiment_id)
    print(f"Start result: {result}")
    
    # Wait for completion
    await asyncio.sleep(12)
    
    # Get results
    final_results = experiment.get_results()
    print(f"Final results: {final_results}")


if __name__ == "__main__":
    asyncio.run(main())
