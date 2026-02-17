"""
IoT Integration for Digital Twin
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass


@dataclass
class IoTDevice:
    """IoT device definition"""
    device_id: str
    asset_id: str
    device_type: str
    sensor_types: List[str]
    location: Dict[str, float]
    installation_date: datetime
    last_calibration: datetime
    status: str = "active"
    battery_level: float = 100.0
    
    def to_dict(self) -> Dict:
        return {
            "device_id": self.device_id,
            "asset_id": self.asset_id,
            "device_type": self.device_type,
            "sensor_types": self.sensor_types,
            "location": self.location,
            "status": self.status,
            "battery_level": self.battery_level
        }


class IoTIntegrationManager:
    """Manage IoT device integration"""
    
    def __init__(self, county_fips: str):
        self.county_fips = county_fips
        self.devices: Dict[str, IoTDevice] = {}
        self.data_processors: Dict[str, Callable] = {}
        self.alert_handlers: List[Callable] = []
        self.metrics = {
            "messages_received": 0,
            "messages_processed": 0,
            "devices_online": 0,
            "devices_offline": 0,
            "alerts_triggered": 0
        }
    
    def register_device(self, device: IoTDevice) -> bool:
        """Register IoT device"""
        if device.device_id in self.devices:
            return False
        self.devices[device.device_id] = device
        self.metrics["devices_online"] += 1
        return True
    
    def process_sensor_data(self, device_id: str, data: Dict):
        """Process sensor data from device"""
        device = self.devices.get(device_id)
        if not device:
            return
        
        enriched_data = {
            "device_id": device_id,
            "asset_id": device.asset_id,
            "county_fips": self.county_fips,
            "timestamp": datetime.now().isoformat(),
            "location": device.location,
            "readings": data
        }
        
        for processor in self.data_processors.values():
            processor(enriched_data)
        
        self._check_alert_conditions(device, data)
        self.metrics["messages_processed"] += 1
    
    def _check_alert_conditions(self, device: IoTDevice, data: Dict):
        """Check if sensor data triggers alerts"""
        alerts = []
        
        for sensor_type, value in data.items():
            if sensor_type == "temperature" and value > 100:
                alerts.append({
                    "type": "extreme_temperature",
                    "severity": "critical",
                    "message": f"Extreme heat detected: {value}F",
                    "device_id": device.device_id,
                    "asset_id": device.asset_id
                })
            elif sensor_type == "vibration" and value > 5.0:
                alerts.append({
                    "type": "structural_anomaly",
                    "severity": "high",
                    "message": f"Unusual vibration detected: {value}",
                    "device_id": device.device_id,
                    "asset_id": device.asset_id
                })
            elif sensor_type == "water_level" and value > 10:
                alerts.append({
                    "type": "flood_warning",
                    "severity": "critical",
                    "message": f"High water level: {value}ft",
                    "device_id": device.device_id,
                    "asset_id": device.asset_id
                })
            elif sensor_type == "air_quality_index" and value > 150:
                alerts.append({
                    "type": "air_quality_alert",
                    "severity": "high" if value > 200 else "medium",
                    "message": f"Poor air quality: AQI {value}",
                    "device_id": device.device_id,
                    "asset_id": device.asset_id
                })
        
        for alert in alerts:
            self.metrics["alerts_triggered"] += 1
            for handler in self.alert_handlers:
                handler(alert)
    
    def register_data_processor(self, name: str, processor: Callable):
        """Register data processor"""
        self.data_processors[name] = processor
    
    def register_alert_handler(self, handler: Callable):
        """Register alert handler"""
        self.alert_handlers.append(handler)
    
    def get_device_status(self) -> Dict:
        """Get status of all devices"""
        return {
            "total_devices": len(self.devices),
            "online": self.metrics["devices_online"],
            "offline": self.metrics["devices_offline"],
            "by_type": self._get_devices_by_type(),
            "low_battery": self._get_low_battery_devices()
        }
    
    def _get_devices_by_type(self) -> Dict[str, int]:
        """Count devices by type"""
        counts = {}
        for device in self.devices.values():
            counts[device.device_type] = counts.get(device.device_type, 0) + 1
        return counts
    
    def _get_low_battery_devices(self) -> List[str]:
        """Get devices with low battery"""
        return [d.device_id for d in self.devices.values() if d.battery_level < 20]


class SensorSimulator:
    """Simulate IoT sensor data for testing"""
    
    def __init__(self, county_fips: str):
        self.county_fips = county_fips
        self.running = False
    
    async def start_simulation(self, devices: List[IoTDevice], callback: Callable):
        """Start sensor simulation"""
        self.running = True
        import random
        
        while self.running:
            for device in devices:
                readings = self._generate_readings(device, random)
                await callback({
                    "device_id": device.device_id,
                    "timestamp": datetime.now().isoformat(),
                    "readings": readings
                })
            await asyncio.sleep(5)
    
    def _generate_readings(self, device: IoTDevice, random) -> Dict:
        """Generate simulated sensor readings"""
        readings = {}
        for sensor_type in device.sensor_types:
            if sensor_type == "temperature":
                readings[sensor_type] = random.uniform(60, 85)
            elif sensor_type == "humidity":
                readings[sensor_type] = random.uniform(30, 80)
            elif sensor_type == "vibration":
                readings[sensor_type] = random.uniform(0, 2)
            elif sensor_type == "water_level":
                readings[sensor_type] = random.uniform(0, 5)
            elif sensor_type == "air_quality_index":
                readings[sensor_type] = random.uniform(20, 100)
            elif sensor_type == "structural_strain":
                readings[sensor_type] = random.uniform(0, 100)
            elif sensor_type == "power_consumption":
                readings[sensor_type] = random.uniform(100, 1000)
        return readings
    
    def stop_simulation(self):
        """Stop sensor simulation"""
        self.running = False
