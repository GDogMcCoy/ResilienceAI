"""
Battery Optimization Module for ResilienceAI
Implements power management strategies for sensor devices
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class PowerMode(Enum):
    """Power modes for device operation"""
    NORMAL = "normal"           # Full operation
    ECO = "eco"                 # Reduced sampling
    POWER_SAVE = "power_save"   # Minimal operation
    EMERGENCY = "emergency"     # Critical battery - essential only


@dataclass
class PowerProfile:
    """Power consumption profile for a device"""
    # Current consumption (mA)
    active_current: float = 50.0
    sleep_current: float = 0.01
    transmission_current: float = 120.0
    sensor_reading_current: float = 20.0
    
    # Timing (seconds)
    wake_time: float = 0.5
    transmission_time: float = 2.0
    sensor_warmup_time: float = 1.0
    
    # Battery
    battery_capacity_mah: float = 2000.0  # 18650 Li-ion
    min_operating_voltage: float = 3.0
    
    def estimate_battery_life(
        self,
        samples_per_hour: int,
        transmissions_per_hour: int
    ) -> float:
        """Estimate battery life in days"""
        # Calculate average current consumption
        sample_interval = 3600 / samples_per_hour
        transmission_interval = 3600 / transmissions_per_hour
        
        # Time spent in each state per hour
        reading_time = samples_per_hour * (self.sensor_warmup_time + 0.1)
        tx_time = transmissions_per_hour * self.transmission_time
        active_time = reading_time + tx_time
        sleep_time = 3600 - active_time
        
        # Average current (mA)
        avg_current = (
            (reading_time * self.sensor_reading_current) +
            (tx_time * self.transmission_current) +
            (sleep_time * self.sleep_current)
        ) / 3600
        
        # Battery life in days
        return self.battery_capacity_mah / (avg_current * 24)


@dataclass
class SamplingSchedule:
    """Adaptive sampling schedule"""
    base_interval: int = 60  # seconds
    min_interval: int = 10
    max_interval: int = 3600
    
    # Adaptive factors
    high_activity_multiplier: float = 0.5  # Sample more frequently
    low_activity_multiplier: float = 2.0   # Sample less frequently
    
    # Battery-aware adjustments
    eco_battery_threshold: float = 50.0
    power_save_threshold: float = 20.0
    emergency_threshold: float = 10.0


class AdaptiveSampler:
    """Adaptive sampling based on activity and battery level"""
    
    def __init__(
        self,
        schedule: SamplingSchedule,
        power_profile: PowerProfile
    ):
        self.schedule = schedule
        self.power_profile = power_profile
        
        self.current_interval = schedule.base_interval
        self.last_readings: Dict[str, float] = {}
        self.activity_history: List[float] = []
    
    def calculate_next_interval(
        self,
        battery_level: float,
        current_readings: Dict[str, float]
    ) -> int:
        """Calculate optimal sampling interval"""
        
        # 1. Battery-based adjustment
        if battery_level < self.schedule.emergency_threshold:
            return self.schedule.max_interval  # Emergency mode
        elif battery_level < self.schedule.power_save_threshold:
            base = self.schedule.base_interval * 3
        elif battery_level < self.schedule.eco_battery_threshold:
            base = self.schedule.base_interval * 1.5
        else:
            base = self.schedule.base_interval
        
        # 2. Activity-based adjustment
        if self.last_readings:
            activity = self._calculate_activity(current_readings)
            self.activity_history.append(activity)
            
            # Keep only recent history
            if len(self.activity_history) > 10:
                self.activity_history.pop(0)
            
            avg_activity = sum(self.activity_history) / len(self.activity_history)
            
            if avg_activity > 0.5:  # High activity
                base *= self.schedule.high_activity_multiplier
            elif avg_activity < 0.1:  # Low activity
                base *= self.schedule.low_activity_multiplier
        
        # Update last readings
        self.last_readings = current_readings.copy()
        
        # Clamp to valid range
        interval = max(
            self.schedule.min_interval,
            min(self.schedule.max_interval, int(base))
        )
        
        self.current_interval = interval
        return interval
    
    def _calculate_activity(self, readings: Dict[str, float]) -> float:
        """Calculate activity level based on reading changes"""
        if not self.last_readings:
            return 0.5
        
        changes = []
        for key, value in readings.items():
            if key in self.last_readings and isinstance(value, (int, float)):
                prev = self.last_readings[key]
                if prev != 0:
                    change = abs(value - prev) / abs(prev)
                    changes.append(min(change, 1.0))  # Cap at 100%
        
        return sum(changes) / len(changes) if changes else 0.5


class TransmissionOptimizer:
    """Optimize data transmission for power efficiency"""
    
    def __init__(
        self,
        max_batch_size: int = 100,
        max_batch_age_seconds: int = 300,
        priority_threshold: float = 0.8
    ):
        self.max_batch_size = max_batch_size
        self.max_batch_age = max_batch_age_seconds
        self.priority_threshold = priority_threshold
        
        self.batch: List[Dict] = []
        self.batch_start_time: Optional[datetime] = None
    
    def should_transmit(
        self,
        reading: Dict,
        battery_level: float
    ) -> tuple[bool, List[Dict]]:
        """
        Determine if transmission should occur
        Returns: (should_transmit, data_to_transmit)
        """
        # Check for high-priority data
        priority = reading.get('priority', 0)
        if priority >= self.priority_threshold:
            # Transmit immediately with any batched data
            data = self.batch + [reading]
            self.batch = []
            self.batch_start_time = None
            return True, data
        
        # Add to batch
        self.batch.append(reading)
        
        if self.batch_start_time is None:
            self.batch_start_time = datetime.utcnow()
        
        # Check batch conditions
        batch_age = (datetime.utcnow() - self.batch_start_time).seconds
        
        should_tx = (
            len(self.batch) >= self.max_batch_size or
            batch_age >= self.max_batch_age or
            battery_level < 15  # Low battery - send what we have
        )
        
        if should_tx:
            data = self.batch
            self.batch = []
            self.batch_start_time = None
            return True, data
        
        return False, []
    
    def force_transmit(self) -> List[Dict]:
        """Force transmission of pending batch"""
        data = self.batch
        self.batch = []
        self.batch_start_time = None
        return data


class PowerManager:
    """Main power management class"""
    
    def __init__(
        self,
        power_profile: PowerProfile,
        sampling_schedule: SamplingSchedule
    ):
        self.profile = power_profile
        self.sampler = AdaptiveSampler(sampling_schedule, power_profile)
        self.transmission_optimizer = TransmissionOptimizer()
        
        self.current_mode = PowerMode.NORMAL
        self.battery_level = 100.0
        self.last_sample_time: Optional[datetime] = None
        self.last_transmission_time: Optional[datetime] = None
        
        # Statistics
        self.stats = {
            "samples_taken": 0,
            "transmissions": 0,
            "sleep_time_seconds": 0,
            "estimated_battery_days": 0.0
        }
    
    def update_battery_level(self, level: float):
        """Update battery level and adjust mode"""
        self.battery_level = level
        
        # Adjust power mode based on battery
        if level < 10:
            self.current_mode = PowerMode.EMERGENCY
        elif level < 20:
            self.current_mode = PowerMode.POWER_SAVE
        elif level < 50:
            self.current_mode = PowerMode.ECO
        else:
            self.current_mode = PowerMode.NORMAL
    
    def should_sample(self) -> bool:
        """Determine if it's time to take a sample"""
        if self.last_sample_time is None:
            return True
        
        interval = self.sampler.current_interval
        elapsed = (datetime.utcnow() - self.last_sample_time).seconds
        
        return elapsed >= interval
    
    def record_sample(self, readings: Dict):
        """Record a sample and update scheduling"""
        self.last_sample_time = datetime.utcnow()
        self.stats["samples_taken"] += 1
        
        # Update adaptive sampling
        new_interval = self.sampler.calculate_next_interval(
            self.battery_level,
            readings
        )
        
        logger.debug(f"Next sample in {new_interval} seconds")
    
    def should_transmit(self, reading: Dict) -> tuple[bool, List[Dict]]:
        """Determine if transmission should occur"""
        should_tx, data = self.transmission_optimizer.should_transmit(
            reading,
            self.battery_level
        )
        
        if should_tx:
            self.last_transmission_time = datetime.utcnow()
            self.stats["transmissions"] += 1
        
        return should_tx, data
    
    def get_power_mode_config(self) -> Dict:
        """Get configuration for current power mode"""
        configs = {
            PowerMode.NORMAL: {
                "sampling_interval": 60,
                "transmission_interval": 300,
                "sensors_active": ["all"],
                "features_enabled": ["all"]
            },
            PowerMode.ECO: {
                "sampling_interval": 120,
                "transmission_interval": 600,
                "sensors_active": ["essential"],
                "features_enabled": ["basic"]
            },
            PowerMode.POWER_SAVE: {
                "sampling_interval": 300,
                "transmission_interval": 1800,
                "sensors_active": ["critical"],
                "features_enabled": ["minimal"]
            },
            PowerMode.EMERGENCY: {
                "sampling_interval": 1800,
                "transmission_interval": 3600,
                "sensors_active": ["battery", "status"],
                "features_enabled": ["heartbeat_only"]
            }
        }
        
        return configs.get(self.current_mode, configs[PowerMode.NORMAL])
    
    def estimate_remaining_life(self) -> float:
        """Estimate remaining battery life in days"""
        config = self.get_power_mode_config()
        
        samples_per_hour = 3600 / config["sampling_interval"]
        transmissions_per_hour = 3600 / config["transmission_interval"]
        
        total_life = self.profile.estimate_battery_life(
            samples_per_hour,
            transmissions_per_hour
        )
        
        # Adjust for current battery level
        remaining = total_life * (self.battery_level / 100.0)
        
        self.stats["estimated_battery_days"] = remaining
        return remaining
    
    def get_status(self) -> Dict:
        """Get power management status"""
        return {
            "battery_level": self.battery_level,
            "power_mode": self.current_mode.value,
            "sampling_interval": self.sampler.current_interval,
            "estimated_days_remaining": self.estimate_remaining_life(),
            "stats": self.stats.copy(),
            "config": self.get_power_mode_config()
        }


# Example usage
if __name__ == "__main__":
    # Create power profile for typical sensor node
    profile = PowerProfile(
        active_current=45.0,
        sleep_current=0.008,
        transmission_current=100.0,
        sensor_reading_current=15.0,
        battery_capacity_mah=2600.0
    )
    
    # Create sampling schedule
    schedule = SamplingSchedule(
        base_interval=60,
        min_interval=30,
        max_interval=1800
    )
    
    # Initialize power manager
    pm = PowerManager(profile, schedule)
    
    # Simulate operation
    print("Battery Optimization Demo")
    print("=" * 50)
    
    for battery in [100, 75, 50, 25, 15, 5]:
        pm.update_battery_level(battery)
        
        # Simulate readings
        readings = {"temperature": 22.5, "humidity": 60}
        pm.record_sample(readings)
        
        status = pm.get_status()
        print(f"\nBattery: {battery}%")
        print(f"  Mode: {status['power_mode']}")
        print(f"  Sampling Interval: {status['sampling_interval']}s")
        print(f"  Est. Life: {status['estimated_days_remaining']:.1f} days")
        print(f"  Active Sensors: {status['config']['sensors_active']}")
    
    # Estimate battery life at different configurations
    print("\n\nBattery Life Estimates:")
    print("-" * 50)
    
    for samples in [1, 6, 12, 30, 60]:
        for tx in [1, 6, 12]:
            life = profile.estimate_battery_life(samples, tx)
            print(f"  {samples}/hr samples, {tx}/hr TX: {life:.1f} days")
