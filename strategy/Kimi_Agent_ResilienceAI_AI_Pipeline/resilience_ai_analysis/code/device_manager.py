"""
IoT Device Management for ResilienceAI
Handles provisioning, monitoring, and lifecycle management
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class DeviceStatus(Enum):
    """Device lifecycle statuses"""
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"
    ERROR = "error"


class DeviceType(Enum):
    """Types of sensor devices"""
    AIR_QUALITY = "air_quality"
    WEATHER = "weather"
    SEISMIC = "seismic"
    FLOOD = "flood"
    FIRE = "fire"
    MULTI_SENSOR = "multi_sensor"
    GATEWAY = "gateway"


@dataclass
class DeviceConfig:
    """Device configuration"""
    sampling_interval: int = 60  # seconds
    transmission_interval: int = 300  # seconds
    batch_size: int = 10
    compression_enabled: bool = True
    encryption_enabled: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    calibration_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Device:
    """IoT Device representation"""
    device_id: str
    device_type: DeviceType
    status: DeviceStatus
    
    # Identity
    serial_number: str
    hardware_version: str
    firmware_version: str
    
    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    region_id: str = "default"
    
    # Connectivity
    last_seen: Optional[datetime] = None
    ip_address: Optional[str] = None
    signal_strength: Optional[int] = None
    
    # Health
    battery_level: Optional[float] = None
    temperature: Optional[float] = None
    uptime_seconds: int = 0
    error_count: int = 0
    
    # Configuration
    config: DeviceConfig = field(default_factory=DeviceConfig)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Certificates
    certificate_arn: Optional[str] = None
    certificate_pem: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["device_type"] = self.device_type.value
        data["status"] = self.status.value
        return data
    
    def is_online(self, timeout_seconds: int = 300) -> bool:
        """Check if device is considered online"""
        if not self.last_seen:
            return False
        return (datetime.utcnow() - self.last_seen).seconds < timeout_seconds
    
    def needs_maintenance(self) -> bool:
        """Check if device needs maintenance"""
        if self.battery_level is not None and self.battery_level < 10:
            return True
        if self.error_count > 10:
            return True
        if self.temperature is not None and self.temperature > 70:
            return True
        return False


class DeviceRegistry:
    """Central device registry"""
    
    def __init__(self, storage_path: str = "devices.json"):
        self.storage_path = storage_path
        self.devices: Dict[str, Device] = {}
        self.load_devices()
    
    def load_devices(self):
        """Load devices from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                for device_data in data:
                    device = Device(
                        device_id=device_data["device_id"],
                        device_type=DeviceType(device_data["device_type"]),
                        status=DeviceStatus(device_data["status"]),
                        serial_number=device_data["serial_number"],
                        hardware_version=device_data["hardware_version"],
                        firmware_version=device_data["firmware_version"],
                        latitude=device_data.get("latitude"),
                        longitude=device_data.get("longitude"),
                        altitude=device_data.get("altitude"),
                        region_id=device_data.get("region_id", "default"),
                        last_seen=datetime.fromisoformat(device_data["last_seen"]) if device_data.get("last_seen") else None,
                        ip_address=device_data.get("ip_address"),
                        signal_strength=device_data.get("signal_strength"),
                        battery_level=device_data.get("battery_level"),
                        temperature=device_data.get("temperature"),
                        uptime_seconds=device_data.get("uptime_seconds", 0),
                        error_count=device_data.get("error_count", 0),
                        config=DeviceConfig(**device_data.get("config", {})),
                        created_at=datetime.fromisoformat(device_data["created_at"]),
                        updated_at=datetime.fromisoformat(device_data["updated_at"]),
                        certificate_arn=device_data.get("certificate_arn"),
                        certificate_pem=device_data.get("certificate_pem")
                    )
                    self.devices[device.device_id] = device
            logger.info(f"Loaded {len(self.devices)} devices")
        except FileNotFoundError:
            logger.info("No existing device registry found")
    
    def save_devices(self):
        """Save devices to storage"""
        data = [device.to_dict() for device in self.devices.values()]
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def register_device(
        self,
        device_type: DeviceType,
        serial_number: str,
        hardware_version: str,
        firmware_version: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        region_id: str = "default"
    ) -> Device:
        """Register a new device"""
        
        # Generate device ID
        device_id = self._generate_device_id(serial_number, device_type)
        
        device = Device(
            device_id=device_id,
            device_type=device_type,
            status=DeviceStatus.PROVISIONING,
            serial_number=serial_number,
            hardware_version=hardware_version,
            firmware_version=firmware_version,
            latitude=latitude,
            longitude=longitude,
            region_id=region_id
        )
        
        self.devices[device_id] = device
        self.save_devices()
        
        logger.info(f"Registered new device: {device_id}")
        return device
    
    def _generate_device_id(
        self,
        serial_number: str,
        device_type: DeviceType
    ) -> str:
        """Generate unique device ID"""
        prefix = device_type.value[:3].upper()
        hash_input = f"{serial_number}{datetime.utcnow().isoformat()}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"{prefix}-{hash_suffix}"
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def update_device_status(
        self,
        device_id: str,
        status: DeviceStatus
    ) -> bool:
        """Update device status"""
        device = self.devices.get(device_id)
        if not device:
            return False
        
        device.status = status
        device.updated_at = datetime.utcnow()
        self.save_devices()
        
        logger.info(f"Device {device_id} status changed to {status.value}")
        return True
    
    def update_device_health(
        self,
        device_id: str,
        battery_level: Optional[float] = None,
        signal_strength: Optional[int] = None,
        temperature: Optional[float] = None,
        error_count: Optional[int] = None
    ) -> bool:
        """Update device health metrics"""
        device = self.devices.get(device_id)
        if not device:
            return False
        
        if battery_level is not None:
            device.battery_level = battery_level
        if signal_strength is not None:
            device.signal_strength = signal_strength
        if temperature is not None:
            device.temperature = temperature
        if error_count is not None:
            device.error_count = error_count
        
        device.last_seen = datetime.utcnow()
        device.updated_at = datetime.utcnow()
        
        self.save_devices()
        return True
    
    def update_device_config(
        self,
        device_id: str,
        config: DeviceConfig
    ) -> bool:
        """Update device configuration"""
        device = self.devices.get(device_id)
        if not device:
            return False
        
        device.config = config
        device.updated_at = datetime.utcnow()
        self.save_devices()
        
        logger.info(f"Updated config for device {device_id}")
        return True
    
    def list_devices(
        self,
        status: Optional[DeviceStatus] = None,
        device_type: Optional[DeviceType] = None,
        region_id: Optional[str] = None
    ) -> List[Device]:
        """List devices with optional filtering"""
        devices = list(self.devices.values())
        
        if status:
            devices = [d for d in devices if d.status == status]
        if device_type:
            devices = [d for d in devices if d.device_type == device_type]
        if region_id:
            devices = [d for d in devices if d.region_id == region_id]
        
        return devices
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        total = len(self.devices)
        online = sum(1 for d in self.devices.values() if d.is_online())
        needs_maintenance = sum(1 for d in self.devices.values() if d.needs_maintenance())
        
        by_status = {}
        for status in DeviceStatus:
            count = sum(1 for d in self.devices.values() if d.status == status)
            by_status[status.value] = count
        
        by_type = {}
        for dtype in DeviceType:
            count = sum(1 for d in self.devices.values() if d.device_type == dtype)
            by_type[dtype.value] = count
        
        low_battery = [
            {"device_id": d.device_id, "battery": d.battery_level}
            for d in self.devices.values()
            if d.battery_level is not None and d.battery_level < 20
        ]
        
        return {
            "total_devices": total,
            "online": online,
            "offline": total - online,
            "needs_maintenance": needs_maintenance,
            "by_status": by_status,
            "by_type": by_type,
            "low_battery_devices": low_battery
        }
    
    def decommission_device(self, device_id: str) -> bool:
        """Decommission a device"""
        device = self.devices.get(device_id)
        if not device:
            return False
        
        device.status = DeviceStatus.DECOMMISSIONED
        device.updated_at = datetime.utcnow()
        self.save_devices()
        
        logger.info(f"Decommissioned device: {device_id}")
        return True


class OTAUpdateManager:
    """Over-the-air firmware update manager"""
    
    def __init__(self, device_registry: DeviceRegistry):
        self.registry = device_registry
        self.firmware_versions: Dict[str, str] = {}
        self.update_queue: Dict[str, Dict] = {}  # device_id -> update info
    
    def register_firmware(
        self,
        device_type: DeviceType,
        version: str,
        download_url: str,
        checksum: str
    ):
        """Register a new firmware version"""
        self.firmware_versions[device_type.value] = {
            "version": version,
            "url": download_url,
            "checksum": checksum,
            "released_at": datetime.utcnow().isoformat()
        }
    
    def schedule_update(
        self,
        device_id: str,
        target_version: str,
        scheduled_time: Optional[datetime] = None
    ) -> bool:
        """Schedule firmware update for device"""
        device = self.registry.get_device(device_id)
        if not device:
            return False
        
        if device.firmware_version == target_version:
            logger.info(f"Device {device_id} already at version {target_version}")
            return False
        
        self.update_queue[device_id] = {
            "device_id": device_id,
            "from_version": device.firmware_version,
            "to_version": target_version,
            "scheduled_time": scheduled_time or datetime.utcnow(),
            "status": "pending"
        }
        
        logger.info(f"Scheduled update for {device_id} to {target_version}")
        return True
    
    def get_pending_updates(self, device_id: str) -> Optional[Dict]:
        """Get pending update for device"""
        return self.update_queue.get(device_id)
    
    def confirm_update(self, device_id: str, success: bool):
        """Confirm update completion"""
        if device_id in self.update_queue:
            self.update_queue[device_id]["status"] = "completed" if success else "failed"
            self.update_queue[device_id]["completed_at"] = datetime.utcnow().isoformat()
            
            if success:
                # Update device firmware version
                update_info = self.update_queue[device_id]
                device = self.registry.get_device(device_id)
                if device:
                    device.firmware_version = update_info["to_version"]
                    self.registry.save_devices()


# Example usage
if __name__ == "__main__":
    # Initialize registry
    registry = DeviceRegistry("/tmp/devices.json")
    
    # Register a new device
    device = registry.register_device(
        device_type=DeviceType.AIR_QUALITY,
        serial_number="AQ-2024-001",
        hardware_version="1.0",
        firmware_version="1.2.3",
        latitude=37.7749,
        longitude=-122.4194,
        region_id="san_francisco"
    )
    
    print(f"Registered device: {device.device_id}")
    
    # Update health metrics
    registry.update_device_health(
        device_id=device.device_id,
        battery_level=85.5,
        signal_strength=-65,
        temperature=25.3
    )
    
    # Activate device
    registry.update_device_status(device.device_id, DeviceStatus.ACTIVE)
    
    # Get health summary
    summary = registry.get_health_summary()
    print(f"\nHealth Summary: {json.dumps(summary, indent=2)}")
    
    # Initialize OTA manager
    ota = OTAUpdateManager(registry)
    ota.register_firmware(
        device_type=DeviceType.AIR_QUALITY,
        version="1.3.0",
        download_url="https://firmware.resilienceai.io/aq/1.3.0.bin",
        checksum="abc123..."
    )
    
    ota.schedule_update(device.device_id, "1.3.0")
