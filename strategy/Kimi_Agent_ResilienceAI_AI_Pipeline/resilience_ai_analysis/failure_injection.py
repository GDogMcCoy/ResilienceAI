"""
Failure Injection Framework for ResilienceAI
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
from enum import Enum, auto
from abc import ABC, abstractmethod
import asyncio
import random
import time
from datetime import datetime

class FailureType(Enum):
    """Types of failures that can be injected"""
    # Compute Failures
    INSTANCE_FAILURE = auto()
    CPU_STRESS = auto()
    MEMORY_STRESS = auto()
    DISK_STRESS = auto()
    PROCESS_KILL = auto()
    
    # Network Failures
    NETWORK_LATENCY = auto()
    NETWORK_PACKET_LOSS = auto()
    NETWORK_PARTITION = auto()
    DNS_FAILURE = auto()
    BANDWIDTH_LIMIT = auto()
    
    # Dependency Failures
    SERVICE_UNAVAILABLE = auto()
    TIMEOUT = auto()
    ERROR_RESPONSE = auto()
    DEGRADED_RESPONSE = auto()
    
    # Resource Failures
    RESOURCE_EXHAUSTION = auto()
    CONNECTION_POOL_EXHAUSTION = auto()
    THREAD_POOL_EXHAUSTION = auto()
    FILE_DESCRIPTOR_EXHAUSTION = auto()
    
    # State Failures
    DATABASE_CORRUPTION = auto()
    CACHE_INVALIDATION = auto()
    SESSION_LOSS = auto()
    CONFIGURATION_DRIFT = auto()

class FailureSeverity(Enum):
    """Severity levels for failures"""
    LOW = "low"           # Minimal impact
    MEDIUM = "medium"     # Noticeable impact
    HIGH = "high"         # Significant impact
    CRITICAL = "critical" # Severe impact

@dataclass
class FailureConfig:
    """Configuration for a failure injection"""
    failure_type: FailureType
    severity: FailureSeverity
    target_service: str
    duration_seconds: int
    probability: float = 1.0  # 1.0 = always, 0.0 = never
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

class FailureInjector(ABC):
    """Base class for failure injectors"""
    
    def __init__(self, config: FailureConfig):
        self.config = config
        self.active = False
        self.start_time: Optional[datetime] = None
    
    @abstractmethod
    async def inject(self):
        """Inject the failure"""
        pass
    
    @abstractmethod
    async def restore(self):
        """Restore normal operation"""
        pass
    
    async def run(self):
        """Run the failure injection"""
        if random.random() > self.config.probability:
            return {"status": "skipped", "reason": "Probability check failed"}
        
        self.active = True
        self.start_time = datetime.utcnow()
        
        try:
            await self.inject()
            await asyncio.sleep(self.config.duration_seconds)
        finally:
            await self.restore()
            self.active = False
        
        return {
            "status": "completed",
            "failure_type": self.config.failure_type.name,
            "duration": self.config.duration_seconds
        }

# ==================== COMPUTE FAILURES ====================

class CPUStressInjector(FailureInjector):
    """Inject CPU stress"""
    
    async def inject(self):
        """Start CPU stress"""
        load_percentage = self.config.parameters.get("load_percentage", 80)
        cores = self.config.parameters.get("cores", "all")
        
        print(f"Injecting CPU stress: {load_percentage}% on cores {cores}")
        
        self._stress_tasks = []
        num_cores = 4 if cores == "all" else int(cores)
        
        for _ in range(num_cores):
            task = asyncio.create_task(self._cpu_stress_task(load_percentage))
            self._stress_tasks.append(task)
    
    async def _cpu_stress_task(self, load_percentage: float):
        """Task to generate CPU load"""
        while self.active:
            busy_time = load_percentage / 100.0 * 0.1
            sleep_time = 0.1 - busy_time
            
            start = time.time()
            while time.time() - start < busy_time:
                pass
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    async def restore(self):
        """Stop CPU stress"""
        for task in getattr(self, '_stress_tasks', []):
            task.cancel()
        print("CPU stress restored")

class MemoryStressInjector(FailureInjector):
    """Inject memory stress"""
    
    async def inject(self):
        """Start memory stress"""
        memory_mb = self.config.parameters.get("memory_mb", 1024)
        
        print(f"Injecting memory stress: {memory_mb}MB")
        self._memory_hog = bytearray(memory_mb * 1024 * 1024)
    
    async def restore(self):
        """Release memory"""
        if hasattr(self, '_memory_hog'):
            del self._memory_hog
        print("Memory stress restored")

class ProcessKillInjector(FailureInjector):
    """Inject process kills"""
    
    async def inject(self):
        """Kill target processes"""
        process_pattern = self.config.parameters.get("process_pattern", "*")
        kill_probability = self.config.parameters.get("kill_probability", 0.5)
        
        print(f"Injecting process kills: pattern={process_pattern}, prob={kill_probability}")
        
    async def restore(self):
        """Processes are already dead, may need restart"""
        auto_restart = self.config.parameters.get("auto_restart", True)
        if auto_restart:
            print("Auto-restarting killed processes")
        print("Process kill injection completed")

# ==================== NETWORK FAILURES ====================

class NetworkLatencyInjector(FailureInjector):
    """Inject network latency"""
    
    async def inject(self):
        """Add latency to network calls"""
        latency_ms = self.config.parameters.get("latency_ms", 100)
        jitter_ms = self.config.parameters.get("jitter_ms", 10)
        target_services = self.config.parameters.get("target_services", ["*"])
        
        print(f"Injecting network latency: {latency_ms}ms (±{jitter_ms}ms) to {target_services}")
        
        self._latency_proxy = LatencyProxy(latency_ms, jitter_ms, target_services)
        await self._latency_proxy.start()
    
    async def restore(self):
        """Remove network latency"""
        if hasattr(self, '_latency_proxy'):
            await self._latency_proxy.stop()
        print("Network latency restored")

class LatencyProxy:
    """Proxy that adds latency to requests"""
    
    def __init__(self, latency_ms: float, jitter_ms: float, target_services: List[str]):
        self.latency_ms = latency_ms
        self.jitter_ms = jitter_ms
        self.target_services = target_services
    
    async def start(self):
        """Start the latency proxy"""
        pass
    
    async def stop(self):
        """Stop the latency proxy"""
        pass

class NetworkPartitionInjector(FailureInjector):
    """Inject network partitions"""
    
    async def inject(self):
        """Create network partition"""
        partition_groups = self.config.parameters.get("partition_groups", [])
        
        print(f"Injecting network partition: {partition_groups}")
        
        for i, group in enumerate(partition_groups):
            print(f"Partition group {i}: {group}")
    
    async def restore(self):
        """Remove network partition"""
        print("Network partition restored")

class PacketLossInjector(FailureInjector):
    """Inject packet loss"""
    
    async def inject(self):
        """Add packet loss"""
        loss_percentage = self.config.parameters.get("loss_percentage", 10)
        correlation = self.config.parameters.get("correlation", 25)
        
        print(f"Injecting packet loss: {loss_percentage}% (correlation: {correlation}%)")
    
    async def restore(self):
        """Remove packet loss"""
        print("Packet loss restored")

# ==================== DEPENDENCY FAILURES ====================

class ServiceUnavailableInjector(FailureInjector):
    """Make dependencies unavailable"""
    
    async def inject(self):
        """Make service unavailable"""
        service_name = self.config.parameters.get("service_name", "unknown")
        error_code = self.config.parameters.get("error_code", 503)
        
        print(f"Making service unavailable: {service_name} (HTTP {error_code})")
        
        self._unavailable_services = [service_name]
    
    async def restore(self):
        """Restore service availability"""
        print("Service availability restored")

class TimeoutInjector(FailureInjector):
    """Inject timeouts"""
    
    async def inject(self):
        """Add timeouts to calls"""
        timeout_ms = self.config.parameters.get("timeout_ms", 5000)
        target_services = self.config.parameters.get("target_services", ["*"])
        
        print(f"Injecting timeouts: {timeout_ms}ms for {target_services}")
    
    async def restore(self):
        """Remove timeouts"""
        print("Timeout injection restored")

class ErrorResponseInjector(FailureInjector):
    """Inject error responses"""
    
    async def inject(self):
        """Return error responses"""
        error_rate = self.config.parameters.get("error_rate", 0.5)
        error_codes = self.config.parameters.get("error_codes", [500, 502, 503])
        target_endpoints = self.config.parameters.get("target_endpoints", ["*"])
        
        print(f"Injecting errors: {error_rate*100}% with codes {error_codes}")
    
    async def restore(self):
        """Stop error responses"""
        print("Error response injection restored")

# ==================== FACTORY ====================

class FailureInjectorFactory:
    """Factory for creating failure injectors"""
    
    _injectors = {
        FailureType.CPU_STRESS: CPUStressInjector,
        FailureType.MEMORY_STRESS: MemoryStressInjector,
        FailureType.PROCESS_KILL: ProcessKillInjector,
        FailureType.NETWORK_LATENCY: NetworkLatencyInjector,
        FailureType.NETWORK_PARTITION: NetworkPartitionInjector,
        FailureType.NETWORK_PACKET_LOSS: PacketLossInjector,
        FailureType.SERVICE_UNAVAILABLE: ServiceUnavailableInjector,
        FailureType.TIMEOUT: TimeoutInjector,
        FailureType.ERROR_RESPONSE: ErrorResponseInjector,
    }
    
    @classmethod
    def create_injector(cls, config: FailureConfig) -> FailureInjector:
        """Create a failure injector"""
        injector_class = cls._injectors.get(config.failure_type)
        if not injector_class:
            raise ValueError(f"Unknown failure type: {config.failure_type}")
        return injector_class(config)
    
    @classmethod
    def register_injector(cls, failure_type: FailureType, injector_class: type):
        """Register a custom injector"""
        cls._injectors[failure_type] = injector_class
    
    @classmethod
    def get_available_failures(cls) -> List[FailureType]:
        """Get list of available failure types"""
        return list(cls._injectors.keys())

# ==================== FAILURE SCENARIOS ====================

class FailureScenario:
    """Define a complete failure scenario"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.failures: List[FailureConfig] = []
        self.sequence: List[Dict[str, Any]] = []
    
    def add_failure(self, config: FailureConfig, delay_seconds: int = 0):
        """Add a failure to the scenario"""
        self.failures.append(config)
        self.sequence.append({
            "failure": config,
            "delay_seconds": delay_seconds
        })
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the failure scenario"""
        results = []
        
        for step in self.sequence:
            if step["delay_seconds"] > 0:
                await asyncio.sleep(step["delay_seconds"])
            
            injector = FailureInjectorFactory.create_injector(step["failure"])
            result = await injector.run()
            results.append(result)
        
        return {
            "scenario": self.name,
            "results": results,
            "completed_at": datetime.utcnow().isoformat()
        }

# Pre-defined failure scenarios for ResilienceAI
DATABASE_FAILURE_SCENARIO = FailureScenario(
    name="Database Degradation",
    description="Simulate database performance degradation"
)
DATABASE_FAILURE_SCENARIO.add_failure(
    FailureConfig(
        failure_type=FailureType.NETWORK_LATENCY,
        severity=FailureSeverity.MEDIUM,
        target_service="database",
        duration_seconds=60,
        parameters={"latency_ms": 200, "target_services": ["database"]}
    ),
    delay_seconds=0
)
DATABASE_FAILURE_SCENARIO.add_failure(
    FailureConfig(
        failure_type=FailureType.TIMEOUT,
        severity=FailureSeverity.HIGH,
        target_service="database",
        duration_seconds=30,
        parameters={"timeout_ms": 3000, "target_services": ["database"]}
    ),
    delay_seconds=30
)

CASCADING_FAILURE_SCENARIO = FailureScenario(
    name="Cascading Service Failure",
    description="Simulate cascading failures across services"
)
CASCADING_FAILURE_SCENARIO.add_failure(
    FailureConfig(
        failure_type=FailureType.SERVICE_UNAVAILABLE,
        severity=FailureSeverity.HIGH,
        target_service="auth-service",
        duration_seconds=120,
        parameters={"service_name": "auth-service", "error_code": 503}
    ),
    delay_seconds=0
)
CASCADING_FAILURE_SCENARIO.add_failure(
    FailureConfig(
        failure_type=FailureType.ERROR_RESPONSE,
        severity=FailureSeverity.MEDIUM,
        target_service="api-gateway",
        duration_seconds=90,
        parameters={"error_rate": 0.3, "error_codes": [502, 504]}
    ),
    delay_seconds=30
)


async def main():
    """Example usage"""
    print("Failure Injection Framework Demo")
    print("=" * 50)
    
    # Create a simple failure config
    config = FailureConfig(
        failure_type=FailureType.CPU_STRESS,
        severity=FailureSeverity.MEDIUM,
        target_service="test-service",
        duration_seconds=5,
        parameters={"load_percentage": 50}
    )
    
    # Create injector and run
    injector = FailureInjectorFactory.create_injector(config)
    result = await injector.run()
    print(f"Result: {result}")
    
    # Run a scenario
    print("\nRunning database failure scenario...")
    scenario_result = await DATABASE_FAILURE_SCENARIO.execute()
    print(f"Scenario result: {scenario_result}")


if __name__ == "__main__":
    asyncio.run(main())
