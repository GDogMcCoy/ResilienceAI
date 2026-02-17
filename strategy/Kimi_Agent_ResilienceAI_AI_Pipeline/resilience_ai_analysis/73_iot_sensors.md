# IoT Sensor Integration for ResilienceAI

## Executive Summary

This document provides a comprehensive analysis of IoT sensor integration for ResilienceAI's environmental monitoring and disaster resilience platform. The analysis covers architecture design, implementation patterns, security considerations, and cost-effective deployment strategies for sensor networks in challenging environments.

---

## 1. IoT Architecture Overview

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RESILIENCEAI IoT ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLOUD LAYER                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   AWS IoT   │  │  Azure IoT  │  │  GCP IoT    │  │  ResilienceAI       │ │
│  │   Core      │  │    Hub      │  │   Core      │  │  Analytics Engine   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────────────────────┘ │
│         │                │                │                                  │
│  ┌──────┴────────────────┴────────────────┴──────┐                           │
│  │              MQTT Broker Cluster               │                           │
│  │         (Mosquitto / EMQX / HiveMQ)           │                           │
│  └──────────────────────┬─────────────────────────┘                           │
└─────────────────────────┼────────────────────────────────────────────────────┘
                          │ HTTPS/WSS
┌─────────────────────────┼────────────────────────────────────────────────────┐
│                         ▼                                                    │
│                         │           EDGE LAYER                               │
│  ┌──────────────────────┴──────────────────────┐                             │
│  │           Edge Gateway Cluster               │                             │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐        │                             │
│  │  │ Edge 1  │ │ Edge 2  │ │ Edge N  │        │                             │
│  │  │(Raspberry│ │(NVIDIA  │ │(Custom  │        │                             │
│  │  │  Pi 4)  │ │ Jetson) │ │  MCU)   │        │                             │
│  │  └────┬────┘ └────┬────┘ └────┬────┘        │                             │
│  └───────┼───────────┼───────────┼─────────────┘                             │
│          │           │           │                                           │
│          │ LoRaWAN   │ LoRaWAN   │ LoRaWAN                                   │
│          │ WiFi      │ WiFi      │ WiFi                                      │
│          │ BLE       │ BLE       │ BLE                                       │
└──────────┼───────────┼───────────┼───────────────────────────────────────────┘
           │           │           │
┌──────────┼───────────┼───────────┼───────────────────────────────────────────┐
│          ▼           ▼           ▼           SENSOR LAYER                    │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐      │
│  │ Air Quality│ │  Weather  │ │ Seismic   │ │  Flood    │ │  Fire     │      │
│  │  Sensors   │ │  Station  │ │  Sensor   │ │  Sensor   │ │  Sensor   │      │
│  │(PM2.5,CO2) │ │(Temp,Hum) │ │(Accelerom)│ │(Ultrasonic│ │(Temp,Gas) │      │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘      │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐      │
│  │   Water   │ │   Soil    │ │   Wind    │ │  Radiation│ │  Noise    │      │
│  │  Quality  │ │  Moisture │ │   Speed   │ │  Monitor  │ │  Monitor  │      │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Layer | Components | Responsibilities |
|-------|-----------|------------------|
| **Cloud** | AWS IoT Core, Analytics Engine | Data storage, ML processing, alerting, dashboards |
| **Edge** | Raspberry Pi, NVIDIA Jetson | Local processing, protocol translation, offline buffering |
| **Sensor** | Various environmental sensors | Data collection, initial filtering, transmission |

---

## 2. IoT Platform Comparison

### 2.1 Platform Feature Matrix

| Feature | AWS IoT Core | Azure IoT Hub | GCP IoT Core | Custom MQTT |
|---------|-------------|---------------|--------------|-------------|
| **MQTT Support** | Native | Native | Native | Native |
| **Device Management** | Excellent | Excellent | Good | Manual |
| **ML Integration** | SageMaker | ML Studio | Vertex AI | External |
| **Pricing** | $1/million messages | $1-25/month/device | $0.0045/GB | Server costs |
| **Edge Computing** | Greengrass | IoT Edge | Edge TPU | Custom |
| **Security** | TLS 1.3, X.509 | TLS 1.3, X.509 | TLS 1.3, JWT | Configurable |
| **Scalability** | Unlimited | Unlimited | Unlimited | Limited |

### 2.2 Recommendation for ResilienceAI

**Primary: AWS IoT Core + Greengrass**
- Best integration with ML/AI services
- Robust device management for distributed sensors
- Excellent disaster recovery capabilities
- Cost-effective at scale

**Secondary: Custom MQTT Broker (Mosquitto/EMQX)**
- For offline/disconnected scenarios
- Lower latency for critical alerts
- Reduced cloud dependency

---

## 3. MQTT Protocol Implementation

### 3.1 MQTT Topic Structure

```
resilienceai/
├── sensors/
│   ├── {region_id}/
│   │   ├── {device_id}/
│   │   │   ├── telemetry/
│   │   │   │   ├── air_quality
│   │   │   │   ├── weather
│   │   │   │   ├── seismic
│   │   │   │   ├── flood
│   │   │   │   └── fire
│   │   │   ├── status/
│   │   │   │   ├── online
│   │   │   │   ├── battery
│   │   │   │   └── error
│   │   │   └── config/
│   │   │       ├── update
│   │   │       └── calibration
│   │   └── alerts/
│   │       ├── critical
│   │       ├── warning
│   │       └── info
│   └── aggregated/
│       ├── hourly
│       └── daily
├── commands/
│   └── {device_id}/
│       ├── restart
│       ├── calibrate
│       └── config
└── system/
    ├── health
    └── maintenance
```

### 3.2 MQTT QoS Levels

| QoS Level | Use Case | Description |
|-----------|----------|-------------|
| **0 (At most once)** | Non-critical telemetry | Fire and forget, no acknowledgment |
| **1 (At least once)** | Standard sensor data | Guaranteed delivery, may duplicate |
| **2 (Exactly once)** | Critical alerts, commands | Guaranteed single delivery |

### 3.3 MQTT Client Implementation (Python)

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/mqtt_client.py
"""
MQTT Client for ResilienceAI Sensor Integration
Supports AWS IoT Core and custom MQTT brokers
"""

import json
import ssl
import time
import logging
from dataclasses import dataclass, asdict
from typing import Callable, Optional, Dict, Any
from datetime import datetime
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SensorReading:
    """Standardized sensor reading format"""
    device_id: str
    sensor_type: str
    timestamp: str
    latitude: float
    longitude: float
    readings: Dict[str, Any]
    battery_level: Optional[float] = None
    signal_strength: Optional[int] = None
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


class ResilienceAIMQTTClient:
    """
    MQTT client for ResilienceAI sensor network
    Supports both AWS IoT Core and custom brokers
    """
    
    def __init__(
        self,
        broker_host: str,
        broker_port: int = 8883,
        client_id: str = None,
        use_tls: bool = True,
        cert_path: str = None,
        key_path: str = None,
        ca_path: str = None,
        username: str = None,
        password: str = None
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id or f"resilienceai_{int(time.time())}"
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=self.client_id)
        
        # Configure TLS if enabled
        if use_tls:
            if cert_path and key_path:
                # AWS IoT Core style authentication
                self.client.tls_set(
                    ca_certs=ca_path,
                    certfile=cert_path,
                    keyfile=key_path,
                    tls_version=ssl.PROTOCOL_TLSv1_2
                )
            else:
                # Standard TLS
                self.client.tls_set()
        
        # Username/password authentication
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        self.connected = False
        
    def _on_connect(self, client, userdata, flags, rc):
        """Connection callback"""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker: {self.broker_host}")
            # Subscribe to command topics
            self.client.subscribe(f"resilienceai/commands/{self.client_id}/#")
        else:
            logger.error(f"Connection failed with code: {rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        """Disconnection callback"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection (rc={rc})")
            
    def _on_message(self, client, userdata, msg):
        """Message received callback"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received message on {msg.topic}")
            
            # Route to appropriate handler
            for topic_pattern, handler in self.message_handlers.items():
                if mqtt.topic_matches_sub(topic_pattern, msg.topic):
                    handler(msg.topic, payload)
                    
        except json.JSONDecodeError:
            logger.warning(f"Received non-JSON message on {msg.topic}")
            
    def _on_publish(self, client, userdata, mid):
        """Publish callback"""
        logger.debug(f"Message {mid} published successfully")
        
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
            return self.connected
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from broker"""
        self.client.loop_stop()
        self.client.disconnect()
        
    def publish_sensor_reading(
        self,
        reading: SensorReading,
        region_id: str = "default",
        qos: int = 1
    ) -> bool:
        """Publish sensor reading to appropriate topic"""
        topic = f"resilienceai/sensors/{region_id}/{reading.device_id}/telemetry/{reading.sensor_type}"
        
        try:
            result = self.client.publish(
                topic,
                payload=reading.to_json(),
                qos=qos
            )
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Publish error: {e}")
            return False
            
    def publish_alert(
        self,
        device_id: str,
        alert_type: str,
        severity: str,
        message: str,
        region_id: str = "default",
        qos: int = 2
    ) -> bool:
        """Publish critical alert"""
        topic = f"resilienceai/sensors/{region_id}/alerts/{severity}"
        
        payload = {
            "device_id": device_id,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            result = self.client.publish(
                topic,
                payload=json.dumps(payload),
                qos=qos
            )
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Alert publish error: {e}")
            return False
            
    def register_handler(self, topic_pattern: str, handler: Callable):
        """Register message handler for topic pattern"""
        self.message_handlers[topic_pattern] = handler
        self.client.subscribe(topic_pattern)
        
    def publish_status(
        self,
        device_id: str,
        status: str,
        metadata: Dict[str, Any] = None,
        region_id: str = "default"
    ):
        """Publish device status update"""
        topic = f"resilienceai/sensors/{region_id}/{device_id}/status/online"
        
        payload = {
            "device_id": device_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.client.publish(topic, json.dumps(payload), qos=1)


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = ResilienceAIMQTTClient(
        broker_host="your-broker.amazonaws.com",
        broker_port=8883,
        client_id="sensor_node_001",
        cert_path="/path/to/certificate.pem.crt",
        key_path="/path/to/private.pem.key",
        ca_path="/path/to/AmazonRootCA1.pem"
    )
    
    # Connect
    if client.connect():
        # Create sample reading
        reading = SensorReading(
            device_id="sensor_node_001",
            sensor_type="air_quality",
            timestamp=datetime.utcnow().isoformat(),
            latitude=37.7749,
            longitude=-122.4194,
            readings={
                "pm25": 15.2,
                "pm10": 28.5,
                "co2": 420,
                "voc": 120
            },
            battery_level=87.5,
            signal_strength=-65
        )
        
        # Publish reading
        client.publish_sensor_reading(reading, region_id="san_francisco")
        
        # Publish status
        client.publish_status(
            device_id="sensor_node_001",
            status="online",
            metadata={"firmware_version": "1.2.3"}
        )
        
        time.sleep(2)
        client.disconnect()
```

---

## 4. Sensor Data Ingestion

### 4.1 Sensor Types for Environmental Monitoring

| Sensor Type | Parameters | Use Case | Typical Cost |
|-------------|-----------|----------|--------------|
| **Air Quality** | PM2.5, PM10, CO2, VOC, NO2 | Pollution monitoring, health alerts | $50-200 |
| **Weather** | Temperature, Humidity, Pressure | Climate analysis, flood prediction | $30-100 |
| **Seismic** | Acceleration, Vibration | Earthquake early warning | $200-1000 |
| **Water Level** | Ultrasonic, Pressure | Flood detection, river monitoring | $100-500 |
| **Fire Detection** | Temperature, Smoke, CO | Wildfire early detection | $50-300 |
| **Soil Moisture** | Capacitive, Resistive | Drought monitoring, agriculture | $20-80 |
| **Radiation** | Gamma, Beta | Nuclear incident detection | $500-2000 |
| **Noise** | dB levels | Urban planning, disaster assessment | $30-150 |

### 4.2 Data Ingestion Pipeline

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/sensor_ingestion.py
"""
Sensor Data Ingestion Pipeline for ResilienceAI
Handles multiple sensor protocols and data formats
"""

import json
import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class SensorProtocol(Enum):
    """Supported sensor communication protocols"""
    MQTT = "mqtt"
    HTTP = "http"
    COAP = "coap"
    LORAWAN = "lorawan"
    MODBUS = "modbus"
    I2C = "i2c"
    SPI = "spi"
    UART = "uart"


@dataclass
class RawSensorData:
    """Raw sensor data before processing"""
    device_id: str
    protocol: SensorProtocol
    raw_payload: bytes
    timestamp: datetime
    source_ip: Optional[str] = None
    rssi: Optional[int] = None


@dataclass
class ProcessedSensorData:
    """Processed and validated sensor data"""
    device_id: str
    sensor_type: str
    timestamp: datetime
    location: Dict[str, float]  # lat, lon, altitude
    readings: Dict[str, float]
    quality_score: float  # 0-1 data quality indicator
    is_valid: bool
    validation_errors: List[str]
    metadata: Dict[str, Any]


class SensorInterface(ABC):
    """Abstract base class for sensor interfaces"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to sensor/gateway"""
        pass
    
    @abstractmethod
    async def read_data(self) -> RawSensorData:
        """Read raw data from sensor"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close connection"""
        pass


class DataValidator:
    """Validates sensor readings against expected ranges"""
    
    # Valid ranges for different sensor types
    VALID_RANGES = {
        "temperature": {"min": -50, "max": 80, "unit": "celsius"},
        "humidity": {"min": 0, "max": 100, "unit": "percent"},
        "pressure": {"min": 800, "max": 1200, "unit": "hPa"},
        "pm25": {"min": 0, "max": 1000, "unit": "ug/m3"},
        "pm10": {"min": 0, "max": 2000, "unit": "ug/m3"},
        "co2": {"min": 300, "max": 10000, "unit": "ppm"},
        "voc": {"min": 0, "max": 5000, "unit": "ppb"},
        "battery": {"min": 0, "max": 100, "unit": "percent"},
        "water_level": {"min": 0, "max": 50, "unit": "meters"},
        "seismic": {"min": 0, "max": 10, "unit": "m/s2"},
    }
    
    @classmethod
    def validate_reading(
        cls,
        sensor_type: str,
        reading_name: str,
        value: float
    ) -> tuple[bool, Optional[str]]:
        """Validate a single reading"""
        if reading_name not in cls.VALID_RANGES:
            return True, None  # Unknown readings pass validation
            
        range_spec = cls.VALID_RANGES[reading_name]
        
        if value < range_spec["min"] or value > range_spec["max"]:
            return False, (
                f"{reading_name} value {value} {range_spec['unit']} "
                f"outside valid range [{range_spec['min']}, {range_spec['max']}]"
            )
        
        return True, None
    
    @classmethod
    def calculate_quality_score(
        cls,
        readings: Dict[str, float],
        rssi: Optional[int] = None
    ) -> float:
        """Calculate data quality score based on multiple factors"""
        scores = []
        
        # Check for missing/null values
        total_fields = len(readings)
        valid_fields = sum(1 for v in readings.values() if v is not None and not np.isnan(v))
        completeness_score = valid_fields / total_fields if total_fields > 0 else 0
        scores.append(completeness_score)
        
        # Signal strength factor
        if rssi is not None:
            # RSSI typically -30 (excellent) to -100 (poor)
            signal_score = max(0, min(1, (rssi + 100) / 70))
            scores.append(signal_score)
        
        # Check for outlier values (simple Z-score)
        for value in readings.values():
            if value is not None and not np.isnan(value):
                # This is simplified; real implementation would use historical data
                outlier_penalty = 0 if -3 < value < 3 else 0.2
                scores.append(1 - outlier_penalty)
        
        return np.mean(scores) if scores else 0.0


class SensorDataProcessor:
    """Main data processing pipeline"""
    
    def __init__(self):
        self.validators: List[Callable] = []
        self.transformers: List[Callable] = []
        self.output_handlers: List[Callable] = []
        
    def add_validator(self, validator: Callable):
        """Add validation function to pipeline"""
        self.validators.append(validator)
        
    def add_transformer(self, transformer: Callable):
        """Add data transformation function"""
        self.transformers.append(transformer)
        
    def add_output_handler(self, handler: Callable):
        """Add output handler for processed data"""
        self.output_handlers.append(handler)
        
    async def process(self, raw_data: RawSensorData) -> ProcessedSensorData:
        """Process raw sensor data through pipeline"""
        
        # Step 1: Parse raw payload
        try:
            parsed = self._parse_payload(raw_data)
        except Exception as e:
            logger.error(f"Failed to parse payload: {e}")
            return self._create_error_result(raw_data, [f"Parse error: {e}"])
        
        # Step 2: Validate readings
        validation_errors = []
        validated_readings = {}
        
        for name, value in parsed.get("readings", {}).items():
            is_valid, error = DataValidator.validate_reading(
                parsed.get("sensor_type", "unknown"),
                name,
                value
            )
            if is_valid:
                validated_readings[name] = value
            else:
                validation_errors.append(error)
        
        # Step 3: Calculate quality score
        quality_score = DataValidator.calculate_quality_score(
            validated_readings,
            raw_data.rssi
        )
        
        # Step 4: Apply transformations
        transformed_readings = validated_readings.copy()
        for transformer in self.transformers:
            try:
                transformed_readings = transformer(transformed_readings)
            except Exception as e:
                logger.warning(f"Transformer failed: {e}")
        
        # Step 5: Create processed data object
        processed = ProcessedSensorData(
            device_id=raw_data.device_id,
            sensor_type=parsed.get("sensor_type", "unknown"),
            timestamp=raw_data.timestamp,
            location=parsed.get("location", {"lat": 0, "lon": 0}),
            readings=transformed_readings,
            quality_score=quality_score,
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            metadata={
                "protocol": raw_data.protocol.value,
                "rssi": raw_data.rssi,
                "source_ip": raw_data.source_ip
            }
        )
        
        # Step 6: Send to output handlers
        for handler in self.output_handlers:
            try:
                await handler(processed)
            except Exception as e:
                logger.error(f"Output handler failed: {e}")
        
        return processed
    
    def _parse_payload(self, raw_data: RawSensorData) -> Dict:
        """Parse raw payload based on protocol"""
        payload_str = raw_data.raw_payload.decode('utf-8')
        
        if raw_data.protocol == SensorProtocol.MQTT:
            return json.loads(payload_str)
        elif raw_data.protocol == SensorProtocol.LORAWAN:
            # LoRaWAN often uses binary encoding
            return self._parse_lorawan_payload(raw_data.raw_payload)
        else:
            # Default to JSON
            return json.loads(payload_str)
    
    def _parse_lorawan_payload(self, payload: bytes) -> Dict:
        """Parse LoRaWAN binary payload"""
        # Example: Custom binary format
        # Byte 0: Sensor type
        # Byte 1-4: Latitude (float32)
        # Byte 5-8: Longitude (float32)
        # Byte 9+: Sensor readings
        
        import struct
        
        sensor_type = payload[0]
        lat = struct.unpack('f', payload[1:5])[0]
        lon = struct.unpack('f', payload[5:9])[0]
        
        readings = {}
        offset = 9
        
        # Parse based on sensor type
        if sensor_type == 0x01:  # Air quality
            readings["pm25"] = struct.unpack('H', payload[offset:offset+2])[0] / 10.0
            readings["pm10"] = struct.unpack('H', payload[offset+2:offset+4])[0] / 10.0
            readings["co2"] = struct.unpack('H', payload[offset+4:offset+6])[0]
        
        return {
            "sensor_type": "air_quality",
            "location": {"lat": lat, "lon": lon},
            "readings": readings
        }
    
    def _create_error_result(
        self,
        raw_data: RawSensorData,
        errors: List[str]
    ) -> ProcessedSensorData:
        """Create error result for failed processing"""
        return ProcessedSensorData(
            device_id=raw_data.device_id,
            sensor_type="unknown",
            timestamp=raw_data.timestamp,
            location={"lat": 0, "lon": 0},
            readings={},
            quality_score=0.0,
            is_valid=False,
            validation_errors=errors,
            metadata={"protocol": raw_data.protocol.value}
        )


# Example transformers
def celsius_to_fahrenheit(readings: Dict[str, float]) -> Dict[str, float]:
    """Convert temperature from Celsius to Fahrenheit"""
    if "temperature" in readings:
        readings["temperature_f"] = readings["temperature"] * 9/5 + 32
    return readings


def add_dew_point(readings: Dict[str, float]) -> Dict[str, float]:
    """Calculate dew point from temperature and humidity"""
    if "temperature" in readings and "humidity" in readings:
        T = readings["temperature"]
        RH = readings["humidity"]
        # Magnus formula
        a = 17.27
        b = 237.7
        alpha = ((a * T) / (b + T)) + np.log(RH/100.0)
        readings["dew_point"] = (b * alpha) / (a - alpha)
    return readings
```

---

## 5. Sensor Calibration

### 5.1 Calibration Strategies

| Strategy | Description | Best For | Frequency |
|----------|-------------|----------|-----------|
| **Factory Calibration** | Pre-shipping calibration | All sensors | Once |
| **Field Calibration** | On-site with reference instruments | Critical sensors | Monthly |
| **Auto-Calibration** | Self-calibration using known references | Stable sensors | Weekly |
| **Drift Correction** | Statistical drift detection | Long-term deployments | Continuous |

### 5.2 Calibration Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/sensor_calibration.py
"""
Sensor Calibration Module for ResilienceAI
Handles calibration, drift detection, and correction
"""

import json
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class CalibrationPoint:
    """Single calibration data point"""
    timestamp: datetime
    reference_value: float
    sensor_value: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None


@dataclass
class CalibrationModel:
    """Calibration model for a sensor"""
    device_id: str
    sensor_type: str
    reading_name: str
    # Linear calibration: corrected = (raw * gain) + offset
    gain: float = 1.0
    offset: float = 0.0
    # Temperature compensation
    temp_coefficient: float = 0.0
    # Quality metrics
    r_squared: float = 1.0
    rmse: float = 0.0
    last_calibrated: datetime = field(default_factory=datetime.utcnow)
    calibration_points: List[CalibrationPoint] = field(default_factory=list)
    
    def apply(self, raw_value: float, temperature: Optional[float] = None) -> float:
        """Apply calibration to raw reading"""
        # Basic linear calibration
        corrected = (raw_value * self.gain) + self.offset
        
        # Temperature compensation
        if temperature is not None and self.temp_coefficient != 0:
            temp_correction = self.temp_coefficient * (temperature - 20)  # 20°C reference
            corrected += temp_correction
        
        return corrected
    
    def needs_recalibration(self, max_age_days: int = 30) -> bool:
        """Check if calibration is outdated"""
        age = datetime.utcnow() - self.last_calibrated
        return age > timedelta(days=max_age_days)


class DriftDetector:
    """Detect and correct sensor drift over time"""
    
    def __init__(self, window_size: int = 168):  # 1 week at hourly readings
        self.window_size = window_size
        self.reading_history: Dict[str, deque] = {}
        
    def add_reading(self, device_id: str, reading_name: str, value: float):
        """Add reading to history"""
        key = f"{device_id}:{reading_name}"
        
        if key not in self.reading_history:
            self.reading_history[key] = deque(maxlen=self.window_size)
        
        self.reading_history[key].append({
            "timestamp": datetime.utcnow(),
            "value": value
        })
    
    def detect_drift(
        self,
        device_id: str,
        reading_name: str,
        current_value: float,
        threshold_std: float = 3.0
    ) -> Tuple[bool, Optional[float]]:
        """
        Detect if current reading shows significant drift
        Returns: (is_drift, expected_value)
        """
        key = f"{device_id}:{reading_name}"
        
        if key not in self.reading_history or len(self.reading_history[key]) < 24:
            return False, None
        
        history = list(self.reading_history[key])
        values = [h["value"] for h in history]
        
        mean = np.mean(values)
        std = np.std(values)
        
        # Check if current value is an outlier
        z_score = abs(current_value - mean) / std if std > 0 else 0
        
        is_drift = z_score > threshold_std
        
        return is_drift, mean


class CalibrationManager:
    """Manages calibration for all sensors"""
    
    def __init__(self, calibration_db_path: str = "calibrations.json"):
        self.calibration_db_path = calibration_db_path
        self.calibrations: Dict[str, CalibrationModel] = {}
        self.drift_detector = DriftDetector()
        self.load_calibrations()
    
    def load_calibrations(self):
        """Load calibration data from storage"""
        try:
            with open(self.calibration_db_path, 'r') as f:
                data = json.load(f)
                for cal_data in data:
                    cal = CalibrationModel(**cal_data)
                    key = f"{cal.device_id}:{cal.sensor_type}:{cal.reading_name}"
                    self.calibrations[key] = cal
            logger.info(f"Loaded {len(self.calibrations)} calibrations")
        except FileNotFoundError:
            logger.info("No existing calibration data found")
    
    def save_calibrations(self):
        """Save calibration data to storage"""
        data = []
        for cal in self.calibrations.values():
            cal_dict = {
                "device_id": cal.device_id,
                "sensor_type": cal.sensor_type,
                "reading_name": cal.reading_name,
                "gain": cal.gain,
                "offset": cal.offset,
                "temp_coefficient": cal.temp_coefficient,
                "r_squared": cal.r_squared,
                "rmse": cal.rmse,
                "last_calibrated": cal.last_calibrated.isoformat(),
                "calibration_points": [
                    {
                        "timestamp": cp.timestamp.isoformat(),
                        "reference_value": cp.reference_value,
                        "sensor_value": cp.sensor_value,
                        "temperature": cp.temperature,
                        "humidity": cp.humidity
                    }
                    for cp in cal.calibration_points
                ]
            }
            data.append(cal_dict)
        
        with open(self.calibration_db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_calibration(
        self,
        device_id: str,
        sensor_type: str,
        reading_name: str
    ) -> CalibrationModel:
        """Get or create calibration model for sensor"""
        key = f"{device_id}:{sensor_type}:{reading_name}"
        
        if key not in self.calibrations:
            self.calibrations[key] = CalibrationModel(
                device_id=device_id,
                sensor_type=sensor_type,
                reading_name=reading_name
            )
        
        return self.calibrations[key]
    
    def add_calibration_point(
        self,
        device_id: str,
        sensor_type: str,
        reading_name: str,
        reference_value: float,
        sensor_value: float,
        temperature: Optional[float] = None,
        humidity: Optional[float] = None
    ):
        """Add a calibration point"""
        cal = self.get_calibration(device_id, sensor_type, reading_name)
        
        point = CalibrationPoint(
            timestamp=datetime.utcnow(),
            reference_value=reference_value,
            sensor_value=sensor_value,
            temperature=temperature,
            humidity=humidity
        )
        
        cal.calibration_points.append(point)
        
        # Recalculate calibration if enough points
        if len(cal.calibration_points) >= 3:
            self._recalculate_calibration(cal)
    
    def _recalculate_calibration(self, cal: CalibrationModel):
        """Recalculate calibration coefficients from points"""
        points = cal.calibration_points[-20:]  # Use last 20 points
        
        x = np.array([p.sensor_value for p in points])
        y = np.array([p.reference_value for p in points])
        
        # Linear regression
        A = np.vstack([x, np.ones(len(x))]).T
        gain, offset = np.linalg.lstsq(A, y, rcond=None)[0]
        
        # Calculate R-squared
        y_pred = gain * x + offset
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 1
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean((y - y_pred) ** 2))
        
        # Update calibration model
        cal.gain = gain
        cal.offset = offset
        cal.r_squared = r_squared
        cal.rmse = rmse
        cal.last_calibrated = datetime.utcnow()
        
        logger.info(
            f"Updated calibration for {cal.device_id}:{cal.reading_name} "
            f"(R²={r_squared:.3f}, RMSE={rmse:.3f})"
        )
        
        self.save_calibrations()
    
    def apply_calibration(
        self,
        device_id: str,
        sensor_type: str,
        reading_name: str,
        raw_value: float,
        temperature: Optional[float] = None
    ) -> float:
        """Apply calibration to a raw reading"""
        cal = self.get_calibration(device_id, sensor_type, reading_name)
        
        # Check for drift
        self.drift_detector.add_reading(device_id, reading_name, raw_value)
        is_drift, expected = self.drift_detector.detect_drift(
            device_id, reading_name, raw_value
        )
        
        if is_drift:
            logger.warning(
                f"Possible drift detected for {device_id}:{reading_name} "
                f"(value={raw_value:.2f}, expected={expected:.2f})"
            )
        
        return cal.apply(raw_value, temperature)
    
    def get_calibration_status(
        self,
        device_id: str
    ) -> Dict[str, any]:
        """Get calibration status for a device"""
        device_cals = {
            k: v for k, v in self.calibrations.items()
            if v.device_id == device_id
        }
        
        return {
            "device_id": device_id,
            "total_sensors": len(device_cals),
            "needs_recalibration": sum(
                1 for c in device_cals.values() if c.needs_recalibration()
            ),
            "calibrations": [
                {
                    "sensor_type": c.sensor_type,
                    "reading_name": c.reading_name,
                    "last_calibrated": c.last_calibrated.isoformat(),
                    "r_squared": c.r_squared,
                    "rmse": c.rmse,
                    "needs_recalibration": c.needs_recalibration()
                }
                for c in device_cals.values()
            ]
        }


# Example usage
if __name__ == "__main__":
    # Initialize calibration manager
    cal_manager = CalibrationManager("/tmp/calibrations.json")
    
    # Add calibration points for a PM2.5 sensor
    for i in range(5):
        cal_manager.add_calibration_point(
            device_id="sensor_001",
            sensor_type="air_quality",
            reading_name="pm25",
            reference_value=10.0 + i * 5,  # Known reference values
            sensor_value=9.5 + i * 4.8,     # Sensor readings
            temperature=22.0
        )
    
    # Apply calibration to a new reading
    corrected = cal_manager.apply_calibration(
        device_id="sensor_001",
        sensor_type="air_quality",
        reading_name="pm25",
        raw_value=25.3,
        temperature=23.0
    )
    
    print(f"Corrected PM2.5 reading: {corrected:.2f} µg/m³")
    
    # Get calibration status
    status = cal_manager.get_calibration_status("sensor_001")
    print(f"Calibration status: {json.dumps(status, indent=2)}")
```



---

## 6. Edge Computing

### 6.1 Edge Computing Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EDGE COMPUTING NODE                                  │
│                    (Raspberry Pi 4 / NVIDIA Jetson)                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  Data Ingestion │  │  Local Storage  │  │  ML Inference   │             │
│  │    Service      │  │   (SQLite/TSDB) │  │    Engine       │             │
│  │                 │  │                 │  │                 │             │
│  │ • MQTT Broker   │  │ • Time-series   │  │ • TensorFlow    │             │
│  │ • Protocol      │  │   data          │  │   Lite          │             │
│  │   Translation   │  │ • Local cache   │  │ • ONNX Runtime  │             │
│  │ • Validation    │  │ • Offline queue │  │ • Edge TPU      │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│           └────────────────────┼────────────────────┘                       │
│                                │                                            │
│  ┌─────────────────────────────┼─────────────────────────────────────┐     │
│  │                    Edge Processing Pipeline                        │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │     │
│  │  │  Filter  │→ │ Aggregate│→ │  Detect  │→ │  Alert   │          │     │
│  │  │  & Clean │  │  & Stats │  │ Anomalies│  │  Local   │          │     │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                │                                            │
│  ┌─────────────────────────────┴─────────────────────────────────────┐     │
│  │                    Cloud Sync Service                               │     │
│  │  • Batch upload when connected                                      │     │
│  • Priority-based transmission                                       │     │
│  │  • Compression & encryption                                         │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Edge Node Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/edge_node.py
"""
Edge Computing Node for ResilienceAI
Runs on Raspberry Pi 4 or NVIDIA Jetson
"""

import json
import asyncio
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np
from pathlib import Path

# ML imports (optional, for inference)
try:
    import tensorflow as tf
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class EdgeAlert:
    """Alert generated at edge"""
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    device_id: str
    location: Dict[str, float]
    readings: Dict[str, float]
    confidence: float


class LocalDatabase:
    """SQLite-based local storage for edge node"""
    
    def __init__(self, db_path: str = "edge_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    sensor_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    readings TEXT,
                    quality_score REAL,
                    synced INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edge_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    timestamp TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    location TEXT,
                    readings TEXT,
                    confidence REAL,
                    synced INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_readings_timestamp 
                ON sensor_readings(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_readings_synced 
                ON sensor_readings(synced)
            """)
            
            conn.commit()
    
    def store_reading(self, reading: Dict[str, Any]):
        """Store sensor reading locally"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sensor_readings 
                (device_id, sensor_type, timestamp, latitude, longitude, readings, quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                reading["device_id"],
                reading["sensor_type"],
                reading["timestamp"],
                reading.get("latitude"),
                reading.get("longitude"),
                json.dumps(reading.get("readings", {})),
                reading.get("quality_score", 1.0)
            ))
            conn.commit()
    
    def store_alert(self, alert: EdgeAlert):
        """Store edge-generated alert"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO edge_alerts 
                (alert_type, severity, message, timestamp, device_id, location, readings, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_type,
                alert.severity,
                alert.message,
                alert.timestamp.isoformat(),
                alert.device_id,
                json.dumps(alert.location),
                json.dumps(alert.readings),
                alert.confidence
            ))
            conn.commit()
    
    def get_unsynced_readings(self, limit: int = 1000) -> List[Dict]:
        """Get readings that haven't been synced to cloud"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM sensor_readings 
                WHERE synced = 0 
                ORDER BY timestamp 
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_synced(self, ids: List[int], table: str = "sensor_readings"):
        """Mark records as synced"""
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ','.join('?' * len(ids))
            conn.execute(f"""
                UPDATE {table} 
                SET synced = 1 
                WHERE id IN ({placeholders})
            """, ids)
            conn.commit()
    
    def get_hourly_stats(
        self,
        device_id: str,
        sensor_type: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get hourly aggregated statistics"""
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT readings FROM sensor_readings
                WHERE device_id = ? AND sensor_type = ? AND timestamp > ?
            """, (device_id, sensor_type, since))
            
            all_readings = []
            for row in cursor.fetchall():
                readings = json.loads(row[0])
                all_readings.append(readings)
            
            if not all_readings:
                return {}
            
            # Aggregate by reading name
            stats = {}
            all_keys = set()
            for r in all_readings:
                all_keys.update(r.keys())
            
            for key in all_keys:
                values = [r[key] for r in all_readings if key in r and isinstance(r[key], (int, float))]
                if values:
                    stats[key] = {
                        "count": len(values),
                        "mean": np.mean(values),
                        "std": np.std(values),
                        "min": np.min(values),
                        "max": np.max(values)
                    }
            
            return stats


class AnomalyDetector:
    """Local anomaly detection at edge"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.history: Dict[str, deque] = {}
        self.thresholds: Dict[str, Dict] = {}
    
    def update_history(self, device_id: str, readings: Dict[str, float]):
        """Update reading history for anomaly detection"""
        for name, value in readings.items():
            key = f"{device_id}:{name}"
            
            if key not in self.history:
                self.history[key] = deque(maxlen=self.window_size)
            
            self.history[key].append(value)
            
            # Update thresholds periodically
            if len(self.history[key]) >= 30:
                self._update_thresholds(key)
    
    def _update_thresholds(self, key: str):
        """Update anomaly thresholds based on history"""
        values = list(self.history[key])
        
        mean = np.mean(values)
        std = np.std(values)
        
        self.thresholds[key] = {
            "mean": mean,
            "std": std,
            "upper": mean + 3 * std,
            "lower": mean - 3 * std
        }
    
    def detect_anomalies(
        self,
        device_id: str,
        readings: Dict[str, float]
    ) -> List[Dict]:
        """Detect anomalies in current readings"""
        anomalies = []
        
        for name, value in readings.items():
            key = f"{device_id}:{name}"
            
            if key not in self.thresholds:
                continue
            
            threshold = self.thresholds[key]
            
            if value > threshold["upper"] or value < threshold["lower"]:
                severity = "critical" if abs(value - threshold["mean"]) > 4 * threshold["std"] else "warning"
                
                anomalies.append({
                    "sensor": name,
                    "value": value,
                    "expected_range": [threshold["lower"], threshold["upper"]],
                    "severity": severity,
                    "z_score": abs(value - threshold["mean"]) / threshold["std"] if threshold["std"] > 0 else 0
                })
        
        return anomalies


class EdgeInferenceEngine:
    """ML inference at the edge"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path
        
        if ML_AVAILABLE and model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load TensorFlow Lite model"""
        if not ML_AVAILABLE:
            logger.warning("ML libraries not available")
            return
        
        try:
            self.model = tf.lite.Interpreter(model_path=model_path)
            self.model.allocate_tensors()
            logger.info(f"Loaded edge model: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def predict(self, features: np.ndarray) -> Optional[Dict]:
        """Run inference on features"""
        if self.model is None:
            return None
        
        try:
            input_details = self.model.get_input_details()
            output_details = self.model.get_output_details()
            
            # Prepare input
            input_shape = input_details[0]['shape']
            features = features.reshape(input_shape).astype(np.float32)
            
            self.model.set_tensor(input_details[0]['index'], features)
            self.model.invoke()
            
            # Get output
            output = self.model.get_tensor(output_details[0]['index'])
            
            return {
                "prediction": output.tolist(),
                "confidence": float(np.max(output))
            }
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return None


class EdgeNode:
    """Main edge computing node class"""
    
    def __init__(
        self,
        node_id: str,
        db_path: str = "edge_data.db",
        model_path: Optional[str] = None
    ):
        self.node_id = node_id
        self.db = LocalDatabase(db_path)
        self.anomaly_detector = AnomalyDetector()
        self.inference_engine = EdgeInferenceEngine(model_path)
        
        # Configuration
        self.config = {
            "batch_size": 100,
            "sync_interval": 300,  # 5 minutes
            "alert_threshold": 0.8,
            "compression_enabled": True
        }
        
        self.running = False
    
    async def process_reading(self, reading: Dict[str, Any]) -> Optional[EdgeAlert]:
        """Process a sensor reading through edge pipeline"""
        
        # 1. Store locally
        self.db.store_reading(reading)
        
        # 2. Update anomaly detection history
        device_id = reading["device_id"]
        readings = reading.get("readings", {})
        self.anomaly_detector.update_history(device_id, readings)
        
        # 3. Detect anomalies
        anomalies = self.anomaly_detector.detect_anomalies(device_id, readings)
        
        if anomalies:
            # Generate alert
            critical_anomalies = [a for a in anomalies if a["severity"] == "critical"]
            
            if critical_anomalies:
                alert = EdgeAlert(
                    alert_type="anomaly_detection",
                    severity="critical" if critical_anomalies else "warning",
                    message=f"Detected {len(anomalies)} anomalies: " + 
                            ", ".join([a["sensor"] for a in anomalies]),
                    timestamp=datetime.utcnow(),
                    device_id=device_id,
                    location={
                        "lat": reading.get("latitude", 0),
                        "lon": reading.get("longitude", 0)
                    },
                    readings=readings,
                    confidence=max([a["z_score"] / 5 for a in anomalies])
                )
                
                # Store alert locally
                self.db.store_alert(alert)
                
                return alert
        
        # 4. Run ML inference if model available
        if self.inference_engine.model:
            features = self._extract_features(reading)
            prediction = self.inference_engine.predict(features)
            
            if prediction and prediction["confidence"] > self.config["alert_threshold"]:
                alert = EdgeAlert(
                    alert_type="ml_prediction",
                    severity="warning",
                    message=f"ML model detected potential issue (confidence: {prediction['confidence']:.2f})",
                    timestamp=datetime.utcnow(),
                    device_id=device_id,
                    location={
                        "lat": reading.get("latitude", 0),
                        "lon": reading.get("longitude", 0)
                    },
                    readings=readings,
                    confidence=prediction["confidence"]
                )
                
                self.db.store_alert(alert)
                return alert
        
        return None
    
    def _extract_features(self, reading: Dict[str, Any]) -> np.ndarray:
        """Extract features for ML inference"""
        readings = reading.get("readings", {})
        
        # Example feature extraction
        features = []
        for key in ["temperature", "humidity", "pressure", "pm25", "co2"]:
            features.append(readings.get(key, 0))
        
        return np.array(features)
    
    async def sync_to_cloud(self, cloud_client) -> Dict[str, int]:
        """Sync local data to cloud"""
        stats = {"readings": 0, "alerts": 0}
        
        # Sync readings
        unsynced_readings = self.db.get_unsynced_readings(
            limit=self.config["batch_size"]
        )
        
        if unsynced_readings:
            synced_ids = []
            for reading in unsynced_readings:
                try:
                    # Send to cloud
                    success = await cloud_client.send_reading(reading)
                    if success:
                        synced_ids.append(reading["id"])
                except Exception as e:
                    logger.error(f"Sync error: {e}")
            
            if synced_ids:
                self.db.mark_synced(synced_ids, "sensor_readings")
                stats["readings"] = len(synced_ids)
        
        # Sync alerts (priority)
        # Similar process for alerts...
        
        return stats
    
    def get_stats(self) -> Dict[str, Any]:
        """Get edge node statistics"""
        return {
            "node_id": self.node_id,
            "config": self.config,
            "ml_available": ML_AVAILABLE and self.inference_engine.model is not None,
            "database": self.db.db_path
        }


# Example usage
async def main():
    # Initialize edge node
    edge = EdgeNode(
        node_id="edge_sf_001",
        db_path="/data/edge_data.db",
        model_path="/models/flood_prediction.tflite"
    )
    
    # Simulate processing readings
    sample_reading = {
        "device_id": "sensor_001",
        "sensor_type": "air_quality",
        "timestamp": datetime.utcnow().isoformat(),
        "latitude": 37.7749,
        "longitude": -122.4194,
        "readings": {
            "pm25": 150.0,  # Anomaly!
            "pm10": 200.0,
            "co2": 450
        },
        "quality_score": 0.95
    }
    
    alert = await edge.process_reading(sample_reading)
    
    if alert:
        print(f"Alert generated: {alert.message}")
    
    print(f"Edge stats: {edge.get_stats()}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 7. Real-Time Processing

### 7.1 Stream Processing Architecture

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/realtime_processor.py
"""
Real-Time Stream Processing for ResilienceAI
Uses Apache Kafka / AWS Kinesis style architecture
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)


class ProcessingWindow(Enum):
    """Time window types for aggregation"""
    TUMBLING = "tumbling"      # Fixed, non-overlapping windows
    SLIDING = "sliding"        # Overlapping windows
    SESSION = "session"        # Dynamic windows based on activity


@dataclass
class StreamEvent:
    """Event in the processing stream"""
    event_id: str
    timestamp: datetime
    device_id: str
    sensor_type: str
    readings: Dict[str, float]
    metadata: Dict[str, Any]


@dataclass
class AggregatedResult:
    """Result of windowed aggregation"""
    window_start: datetime
    window_end: datetime
    device_id: str
    sensor_type: str
    aggregations: Dict[str, Dict[str, float]]  # reading_name -> stats
    event_count: int


class WindowedAggregator:
    """Time-windowed aggregation for sensor streams"""
    
    def __init__(
        self,
        window_size_seconds: int = 60,
        window_type: ProcessingWindow = ProcessingWindow.TUMBLING
    ):
        self.window_size = window_size_seconds
        self.window_type = window_type
        self.windows: Dict[str, List[StreamEvent]] = defaultdict(list)
        self.last_window_end: Dict[str, datetime] = {}
    
    def _get_window_key(self, event: StreamEvent) -> str:
        """Generate key for window lookup"""
        return f"{event.device_id}:{event.sensor_type}"
    
    def _get_window_start(self, timestamp: datetime) -> datetime:
        """Calculate window start time"""
        seconds = timestamp.second + timestamp.microsecond / 1e6
        window_start_seconds = (int(seconds) // self.window_size) * self.window_size
        return timestamp.replace(second=window_start_seconds, microsecond=0)
    
    def add_event(self, event: StreamEvent) -> Optional[AggregatedResult]:
        """Add event to window, return result if window complete"""
        key = self._get_window_key(event)
        window_start = self._get_window_start(event.timestamp)
        
        # Check if we need to emit previous window
        if key in self.last_window_end:
            if event.timestamp >= self.last_window_end[key]:
                result = self._emit_window(key, self.last_window_end[key])
                self.windows[key] = []
                return result
        
        # Add to current window
        self.windows[key].append(event)
        
        # Update window end time
        self.last_window_end[key] = window_start + timedelta(seconds=self.window_size)
        
        return None
    
    def _emit_window(
        self,
        key: str,
        window_end: datetime
    ) -> Optional[AggregatedResult]:
        """Emit aggregated results for a window"""
        events = self.windows.get(key, [])
        
        if not events:
            return None
        
        device_id, sensor_type = key.split(":")
        window_start = self._get_window_start(events[0].timestamp)
        
        # Aggregate by reading name
        reading_values: Dict[str, List[float]] = defaultdict(list)
        
        for event in events:
            for name, value in event.readings.items():
                reading_values[name].append(value)
        
        aggregations = {}
        for name, values in reading_values.items():
            if values:
                aggregations[name] = {
                    "count": len(values),
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "median": np.median(values),
                    "p95": np.percentile(values, 95),
                    "p99": np.percentile(values, 99)
                }
        
        return AggregatedResult(
            window_start=window_start,
            window_end=window_end,
            device_id=device_id,
            sensor_type=sensor_type,
            aggregations=aggregations,
            event_count=len(events)
        )
    
    def flush_all(self) -> List[AggregatedResult]:
        """Force emit all pending windows"""
        results = []
        for key in list(self.windows.keys()):
            if key in self.last_window_end:
                result = self._emit_window(key, self.last_window_end[key])
                if result:
                    results.append(result)
                self.windows[key] = []
        return results


class RealTimeAlertEngine:
    """Real-time alerting based on stream processing"""
    
    def __init__(self):
        self.rules: List[Dict] = []
        self.alert_handlers: List[Callable] = []
    
    def add_rule(
        self,
        name: str,
        sensor_type: str,
        reading_name: str,
        condition: str,  # 'gt', 'lt', 'eq', 'range'
        threshold: float or tuple,
        severity: str = "warning",
        cooldown_seconds: int = 300
    ):
        """Add an alert rule"""
        self.rules.append({
            "name": name,
            "sensor_type": sensor_type,
            "reading_name": reading_name,
            "condition": condition,
            "threshold": threshold,
            "severity": severity,
            "cooldown_seconds": cooldown_seconds,
            "last_triggered": None
        })
    
    def evaluate(self, event: StreamEvent) -> List[Dict]:
        """Evaluate all rules against an event"""
        triggered = []
        
        for rule in self.rules:
            # Check sensor type match
            if rule["sensor_type"] != event.sensor_type:
                continue
            
            # Check if reading exists
            if rule["reading_name"] not in event.readings:
                continue
            
            value = event.readings[rule["reading_name"]]
            
            # Check cooldown
            if rule["last_triggered"]:
                cooldown = timedelta(seconds=rule["cooldown_seconds"])
                if datetime.utcnow() - rule["last_triggered"] < cooldown:
                    continue
            
            # Evaluate condition
            triggered_alert = self._evaluate_condition(
                value, rule["condition"], rule["threshold"]
            )
            
            if triggered_alert:
                rule["last_triggered"] = datetime.utcnow()
                triggered.append({
                    "rule_name": rule["name"],
                    "severity": rule["severity"],
                    "message": f"{rule['reading_name']} = {value:.2f} "
                               f"({rule['condition']} {rule['threshold']})",
                    "device_id": event.device_id,
                    "timestamp": event.timestamp,
                    "value": value
                })
        
        return triggered
    
    def _evaluate_condition(
        self,
        value: float,
        condition: str,
        threshold: any
    ) -> bool:
        """Evaluate a single condition"""
        if condition == "gt":
            return value > threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "eq":
            return value == threshold
        elif condition == "range":
            return threshold[0] <= value <= threshold[1]
        elif condition == "outside":
            return value < threshold[0] or value > threshold[1]
        return False
    
    def register_alert_handler(self, handler: Callable):
        """Register handler for triggered alerts"""
        self.alert_handlers.append(handler)
    
    async def process_alerts(self, alerts: List[Dict]):
        """Process triggered alerts"""
        for alert in alerts:
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler error: {e}")


class StreamProcessor:
    """Main stream processing pipeline"""
    
    def __init__(self):
        self.aggregator = WindowedAggregator(window_size_seconds=60)
        self.alert_engine = RealTimeAlertEngine()
        self.processors: List[Callable] = []
        self.output_handlers: List[Callable] = []
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "alerts_generated": 0,
            "windows_emitted": 0
        }
    
    def add_processor(self, processor: Callable):
        """Add custom processor to pipeline"""
        self.processors.append(processor)
    
    def add_output_handler(self, handler: Callable):
        """Add output handler"""
        self.output_handlers.append(handler)
    
    async def process_event(self, event: StreamEvent):
        """Process a single event through the pipeline"""
        
        # 1. Run custom processors
        for processor in self.processors:
            try:
                event = await processor(event)
                if event is None:
                    return  # Event filtered out
            except Exception as e:
                logger.error(f"Processor error: {e}")
        
        # 2. Add to windowed aggregator
        agg_result = self.aggregator.add_event(event)
        
        if agg_result:
            self.stats["windows_emitted"] += 1
            await self._emit_aggregation(agg_result)
        
        # 3. Evaluate alert rules
        alerts = self.alert_engine.evaluate(event)
        
        if alerts:
            self.stats["alerts_generated"] += len(alerts)
            await self.alert_engine.process_alerts(alerts)
        
        # 4. Send to output handlers
        for handler in self.output_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Output handler error: {e}")
        
        self.stats["events_processed"] += 1
    
    async def _emit_aggregation(self, result: AggregatedResult):
        """Emit aggregated window result"""
        for handler in self.output_handlers:
            try:
                await handler(result)
            except Exception as e:
                logger.error(f"Aggregation handler error: {e}")
    
    def get_stats(self) -> Dict:
        """Get processing statistics"""
        return self.stats.copy()


# Example usage
async def example():
    # Initialize processor
    processor = StreamProcessor()
    
    # Add alert rules
    processor.alert_engine.add_rule(
        name="high_pm25",
        sensor_type="air_quality",
        reading_name="pm25",
        condition="gt",
        threshold=35.0,  # EPA unhealthy threshold
        severity="warning",
        cooldown_seconds=600
    )
    
    processor.alert_engine.add_rule(
        name="critical_pm25",
        sensor_type="air_quality",
        reading_name="pm25",
        condition="gt",
        threshold=150.0,  # Very unhealthy
        severity="critical",
        cooldown_seconds=300
    )
    
    # Add alert handler
    async def print_alert(alert):
        print(f"ALERT [{alert['severity'].upper()}]: {alert['message']}")
    
    processor.alert_engine.register_alert_handler(print_alert)
    
    # Process sample events
    for i in range(10):
        event = StreamEvent(
            event_id=f"evt_{i}",
            timestamp=datetime.utcnow(),
            device_id="sensor_001",
            sensor_type="air_quality",
            readings={
                "pm25": 20.0 + i * 15,  # Increasing values
                "pm10": 30.0 + i * 20,
                "co2": 400 + i * 10
            },
            metadata={"quality": 0.95}
        )
        
        await processor.process_event(event)
        await asyncio.sleep(0.1)
    
    print(f"\nStats: {processor.get_stats()}")


if __name__ == "__main__":
    asyncio.run(example())
```

---

## 8. Device Management

### 8.1 Device Lifecycle Management

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/device_manager.py
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
```



---

## 9. Security Considerations

### 9.1 Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SECURITY LAYERS FOR RESILIENCEAI                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: DEVICE SECURITY                                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ • Secure Boot (verified firmware)                                       │ │
│  │ • Hardware Security Modules (HSM/TPM)                                  │ │
│  │ • Encrypted Storage (AES-256)                                          │ │
│  │ • Certificate-based Authentication (X.509)                             │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: COMMUNICATION SECURITY                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ • TLS 1.3 for all connections                                           │ │
│  │ • Certificate Pinning                                                   │ │
│  │ • MQTT over TLS (MQTTS)                                                │ │
│  │ • Perfect Forward Secrecy (ECDHE)                                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: NETWORK SECURITY                                                    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ • Network Segmentation (VLANs)                                          │ │
│  │ • Firewall Rules (iptables/nftables)                                   │ │
│  │ • Intrusion Detection (Snort/Suricata)                                 │ │
│  │ • VPN for remote management                                            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: APPLICATION SECURITY                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ • Input Validation & Sanitization                                       │ │
│  │ • Rate Limiting                                                         │ │
│  │ • API Authentication (JWT/OAuth2)                                      │ │
│  │ • Audit Logging                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: DATA SECURITY                                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ • Encryption at Rest (AES-256-GCM)                                      │ │
│  │ • Field-level Encryption for PII                                       │ │
│  │ • Data Anonymization                                                    │ │
│  │ • Secure Backup & Recovery                                             │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Security Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/security.py
"""
Security Module for ResilienceAI IoT
Implements encryption, authentication, and secure communication
"""

import os
import json
import base64
import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import jwt

logger = logging.getLogger(__name__)


@dataclass
class SecurityContext:
    """Security context for device communication"""
    device_id: str
    certificate_pem: Optional[str] = None
    private_key_pem: Optional[str] = None
    ca_certificate: Optional[str] = None
    shared_secret: Optional[bytes] = None
    token: Optional[str] = None
    token_expiry: Optional[datetime] = None


class DeviceCrypto:
    """Cryptographic operations for devices"""
    
    @staticmethod
    def generate_key_pair() -> Tuple[str, str]:
        """Generate RSA key pair for device"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        return private_pem, public_pem
    
    @staticmethod
    def encrypt_field(data: str, key: bytes) -> str:
        """Encrypt sensitive field data"""
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt_field(encrypted_data: str, key: bytes) -> str:
        """Decrypt sensitive field data"""
        f = Fernet(key)
        encrypted = base64.b64decode(encrypted_data.encode())
        return f.decrypt(encrypted).decode()
    
    @staticmethod
    def generate_device_secret(device_id: str, master_key: bytes) -> bytes:
        """Generate device-specific secret from master key"""
        return hmac.new(
            master_key,
            device_id.encode(),
            hashlib.sha256
        ).digest()


class SecureMQTTClient:
    """Secure MQTT client with certificate authentication"""
    
    def __init__(self, security_context: SecurityContext):
        self.security_context = security_context
        self.client = None
    
    def setup_tls(self, mqtt_client):
        """Configure TLS for MQTT client"""
        import ssl
        
        # Create SSL context
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        
        # Load certificates
        if self.security_context.ca_certificate:
            ssl_context.load_verify_locations(cadata=self.security_context.ca_certificate)
        
        if self.security_context.certificate_pem and self.security_context.private_key_pem:
            ssl_context.load_cert_chain(
                certfile=self._pem_to_temp_file(self.security_context.certificate_pem),
                keyfile=self._pem_to_temp_file(self.security_context.private_key_pem)
            )
        
        # Configure MQTT client
        mqtt_client.tls_set_context(ssl_context)
        mqtt_client.tls_insecure_set(False)
    
    def _pem_to_temp_file(self, pem_content: str) -> str:
        """Write PEM content to temporary file"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write(pem_content)
            return f.name


class PayloadEncryption:
    """Encrypt/decrypt sensor payloads"""
    
    def __init__(self, key: bytes):
        """Initialize with 256-bit key"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits)")
        self.key = key
    
    def encrypt(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """Encrypt payload"""
        # Generate nonce
        nonce = os.urandom(12)
        
        # Create AES-GCM cipher
        aesgcm = AESGCM(self.key)
        
        # Serialize and encrypt payload
        plaintext = json.dumps(payload).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        return {
            "encrypted": base64.b64encode(ciphertext).decode(),
            "nonce": base64.b64encode(nonce).decode()
        }
    
    def decrypt(self, encrypted_payload: Dict[str, str]) -> Dict[str, Any]:
        """Decrypt payload"""
        aesgcm = AESGCM(self.key)
        
        ciphertext = base64.b64decode(encrypted_payload["encrypted"])
        nonce = base64.b64decode(encrypted_payload["nonce"])
        
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode())


class JWTTokenManager:
    """Manage JWT tokens for API authentication"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(
        self,
        device_id: str,
        scopes: list,
        expires_hours: int = 24
    ) -> str:
        """Generate JWT token for device"""
        payload = {
            "sub": device_id,
            "scopes": scopes,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_hours)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None


class SecureStorage:
    """Secure storage for sensitive data"""
    
    def __init__(self, encryption_key: bytes):
        self.encryption_key = encryption_key
        self.fernet = Fernet(base64.urlsafe_b64encode(encryption_key[:32]))
    
    def store(self, key: str, data: Dict) -> str:
        """Encrypt and store data"""
        serialized = json.dumps(data)
        encrypted = self.fernet.encrypt(serialized.encode())
        return base64.b64encode(encrypted).decode()
    
    def retrieve(self, encrypted_data: str) -> Dict:
        """Retrieve and decrypt data"""
        encrypted = base64.b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())


class SecurityAudit:
    """Security audit logging"""
    
    def __init__(self, log_path: str = "security_audit.log"):
        self.log_path = log_path
        
        # Setup audit logger
        self.audit_logger = logging.getLogger("security_audit")
        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)
        self.audit_logger.setLevel(logging.INFO)
    
    def log_event(
        self,
        event_type: str,
        device_id: str,
        details: Dict,
        success: bool = True
    ):
        """Log security event"""
        event = {
            "event_type": event_type,
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "details": details
        }
        
        level = logging.INFO if success else logging.WARNING
        self.audit_logger.log(level, json.dumps(event))
    
    def log_authentication(
        self,
        device_id: str,
        method: str,
        success: bool,
        ip_address: Optional[str] = None
    ):
        """Log authentication attempt"""
        self.log_event(
            "authentication",
            device_id,
            {"method": method, "ip_address": ip_address},
            success
        )
    
    def log_data_access(
        self,
        device_id: str,
        resource: str,
        action: str,
        success: bool
    ):
        """Log data access event"""
        self.log_event(
            "data_access",
            device_id,
            {"resource": resource, "action": action},
            success
        )


# Security best practices checklist
SECURITY_CHECKLIST = {
    "device_security": [
        "Enable secure boot on all devices",
        "Use hardware security modules where available",
        "Implement certificate-based authentication",
        "Store private keys in secure elements",
        "Disable debug interfaces in production",
        "Implement firmware signing and verification"
    ],
    "communication_security": [
        "Use TLS 1.3 for all connections",
        "Implement certificate pinning",
        "Enable perfect forward secrecy",
        "Use strong cipher suites only",
        "Implement connection rate limiting"
    ],
    "network_security": [
        "Segment IoT devices into isolated VLANs",
        "Implement firewall rules for device traffic",
        "Deploy intrusion detection systems",
        "Use VPN for remote device management",
        "Monitor network traffic for anomalies"
    ],
    "application_security": [
        "Validate all input data",
        "Implement rate limiting on APIs",
        "Use parameterized queries for databases",
        "Implement proper error handling",
        "Regular security code reviews"
    ],
    "data_security": [
        "Encrypt data at rest (AES-256)",
        "Encrypt sensitive fields individually",
        "Implement data retention policies",
        "Regular backup with encryption",
        "Secure key management (KMS/HSM)"
    ]
}


# Example usage
if __name__ == "__main__":
    # Generate device key pair
    private_key, public_key = DeviceCrypto.generate_key_pair()
    print(f"Generated key pair for device")
    
    # Initialize payload encryption
    encryption_key = os.urandom(32)
    payload_crypto = PayloadEncryption(encryption_key)
    
    # Encrypt sample payload
    sample_payload = {
        "device_id": "sensor_001",
        "readings": {"temperature": 25.5, "humidity": 60},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    encrypted = payload_crypto.encrypt(sample_payload)
    print(f"Encrypted payload: {encrypted}")
    
    # Decrypt
    decrypted = payload_crypto.decrypt(encrypted)
    print(f"Decrypted payload: {decrypted}")
    
    # JWT token management
    token_manager = JWTTokenManager(secret_key="your-secret-key-here")
    token = token_manager.generate_token(
        device_id="sensor_001",
        scopes=["read", "write"],
        expires_hours=24
    )
    print(f"Generated token: {token[:50]}...")
    
    # Verify token
    verified = token_manager.verify_token(token)
    print(f"Token verified: {verified is not None}")
```

---

## 10. Data Compression

### 10.1 Compression Strategies

| Strategy | Compression Ratio | CPU Cost | Best For |
|----------|-------------------|----------|----------|
| **JSON Minification** | 10-20% | Low | All data |
| **MessagePack** | 30-50% | Low | Structured data |
| **CBOR** | 30-50% | Low | Constrained devices |
| **GZIP** | 60-80% | Medium | Batch uploads |
| **LZ4** | 40-60% | Very Low | Real-time streams |
| **Delta Encoding** | 50-70% | Low | Time-series data |

### 10.2 Compression Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/compression.py
"""
Data Compression Module for ResilienceAI
Optimizes payload sizes for bandwidth-constrained environments
"""

import json
import struct
import gzip
import lz4.frame
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from io import BytesIO

logger = logging.getLogger(__name__)


class JSONMinifier:
    """Minify JSON payloads by removing whitespace"""
    
    @staticmethod
    def compress(data: Dict) -> str:
        """Minify JSON data"""
        return json.dumps(data, separators=(',', ':'))
    
    @staticmethod
    def decompress(data: str) -> Dict:
        """Parse minified JSON"""
        return json.loads(data)


class MessagePackEncoder:
    """MessagePack encoding for efficient serialization"""
    
    try:
        import msgpack
        MSGPACK_AVAILABLE = True
    except ImportError:
        MSGPACK_AVAILABLE = False
    
    @classmethod
    def compress(cls, data: Dict) -> bytes:
        """Encode to MessagePack"""
        if not cls.MSGPACK_AVAILABLE:
            raise ImportError("msgpack not installed")
        return cls.msgpack.packb(data, use_bin_type=True)
    
    @classmethod
    def decompress(cls, data: bytes) -> Dict:
        """Decode from MessagePack"""
        if not cls.MSGPACK_AVAILABLE:
            raise ImportError("msgpack not installed")
        return cls.msgpack.unpackb(data, raw=False)


class CBOREncoder:
    """CBOR (Concise Binary Object Representation) encoding"""
    
    try:
        import cbor2
        CBOR_AVAILABLE = True
    except ImportError:
        CBOR_AVAILABLE = False
    
    @classmethod
    def compress(cls, data: Dict) -> bytes:
        """Encode to CBOR"""
        if not cls.CBOR_AVAILABLE:
            raise ImportError("cbor2 not installed")
        return cls.cbor2.dumps(data)
    
    @classmethod
    def decompress(cls, data: bytes) -> Dict:
        """Decode from CBOR"""
        if not cls.CBOR_AVAILABLE:
            raise ImportError("cbor2 not installed")
        return cls.cbor2.loads(data)


class DeltaEncoder:
    """Delta encoding for time-series data"""
    
    @staticmethod
    def compress(readings: List[Dict], base_timestamp: Optional[int] = None) -> bytes:
        """
        Compress time-series readings using delta encoding
        
        Format:
        - Base timestamp (4 bytes)
        - Number of readings (2 bytes)
        - For each reading:
          - Delta timestamp (1-2 bytes, variable)
          - Delta values for each sensor
        """
        if not readings:
            return b''
        
        # Sort by timestamp
        sorted_readings = sorted(readings, key=lambda r: r['timestamp'])
        
        # Use first timestamp as base
        base_ts = base_timestamp or int(sorted_readings[0]['timestamp'])
        
        buffer = BytesIO()
        
        # Write header
        buffer.write(struct.pack('I', base_ts))  # Base timestamp
        buffer.write(struct.pack('H', len(sorted_readings)))  # Count
        
        # Get sensor keys from first reading
        sensor_keys = [k for k in sorted_readings[0].keys() if k not in ['timestamp', 'device_id']]
        buffer.write(struct.pack('B', len(sensor_keys)))  # Number of sensors
        
        # Write sensor key names (for reconstruction)
        for key in sensor_keys:
            buffer.write(struct.pack('B', len(key)))
            buffer.write(key.encode())
        
        # Write delta-encoded readings
        prev_ts = base_ts
        prev_values = {k: 0 for k in sensor_keys}
        
        for reading in sorted_readings:
            # Delta timestamp (seconds since previous)
            ts_delta = int(reading['timestamp']) - prev_ts
            buffer.write(struct.pack('h', ts_delta))  # 2 bytes for delta
            prev_ts = int(reading['timestamp'])
            
            # Delta values
            for key in sensor_keys:
                value = reading.get(key, 0)
                if isinstance(value, (int, float)):
                    # Store as scaled integer (2 decimal places)
                    scaled = int(value * 100)
                    delta = scaled - prev_values[key]
                    buffer.write(struct.pack('h', delta))  # 2 bytes
                    prev_values[key] = scaled
        
        return buffer.getvalue()
    
    @staticmethod
    def decompress(data: bytes) -> List[Dict]:
        """Decompress delta-encoded readings"""
        buffer = BytesIO(data)
        
        # Read header
        base_ts = struct.unpack('I', buffer.read(4))[0]
        count = struct.unpack('H', buffer.read(2))[0]
        num_sensors = struct.unpack('B', buffer.read(1))[0]
        
        # Read sensor keys
        sensor_keys = []
        for _ in range(num_sensors):
            key_len = struct.unpack('B', buffer.read(1))[0]
            key = buffer.read(key_len).decode()
            sensor_keys.append(key)
        
        # Read delta-encoded readings
        readings = []
        current_ts = base_ts
        current_values = {k: 0 for k in sensor_keys}
        
        for _ in range(count):
            # Delta timestamp
            ts_delta = struct.unpack('h', buffer.read(2))[0]
            current_ts += ts_delta
            
            reading = {'timestamp': current_ts}
            
            # Delta values
            for key in sensor_keys:
                delta = struct.unpack('h', buffer.read(2))[0]
                current_values[key] += delta
                reading[key] = current_values[key] / 100.0  # Scale back
            
            readings.append(reading)
        
        return readings


class GZIPCompressor:
    """GZIP compression for batch data"""
    
    @staticmethod
    def compress(data: Union[str, bytes], level: int = 6) -> bytes:
        """Compress with GZIP"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return gzip.compress(data, compresslevel=level)
    
    @staticmethod
    def decompress(data: bytes) -> str:
        """Decompress GZIP data"""
        return gzip.decompress(data).decode('utf-8')


class LZ4Compressor:
    """LZ4 compression for real-time data"""
    
    @staticmethod
    def compress(data: Union[str, bytes]) -> bytes:
        """Compress with LZ4"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return lz4.frame.compress(data)
    
    @staticmethod
    def decompress(data: bytes) -> str:
        """Decompress LZ4 data"""
        return lz4.frame.decompress(data).decode('utf-8')


class CompressionManager:
    """Manage compression based on data type and constraints"""
    
    COMPRESSION_METHODS = {
        'json_minify': JSONMinifier,
        'msgpack': MessagePackEncoder,
        'cbor': CBOREncoder,
        'delta': DeltaEncoder,
        'gzip': GZIPCompressor,
        'lz4': LZ4Compressor
    }
    
    def __init__(self, default_method: str = 'msgpack'):
        self.default_method = default_method
    
    def compress(
        self,
        data: Any,
        method: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """Compress data using specified method"""
        method = method or self.default_method
        
        if method not in self.COMPRESSION_METHODS:
            raise ValueError(f"Unknown compression method: {method}")
        
        compressor = self.COMPRESSION_METHODS[method]
        
        try:
            if method == 'json_minify':
                return compressor.compress(data).encode()
            elif method == 'delta':
                return compressor.compress(data, **kwargs)
            else:
                return compressor.compress(data)
        except Exception as e:
            logger.error(f"Compression error: {e}")
            # Fallback to JSON
            return json.dumps(data).encode()
    
    def decompress(
        self,
        data: bytes,
        method: Optional[str] = None
    ) -> Any:
        """Decompress data using specified method"""
        method = method or self.default_method
        
        if method not in self.COMPRESSION_METHODS:
            raise ValueError(f"Unknown compression method: {method}")
        
        compressor = self.COMPRESSION_METHODS[method]
        
        try:
            if method == 'json_minify':
                return compressor.decompress(data.decode())
            else:
                return compressor.decompress(data)
        except Exception as e:
            logger.error(f"Decompression error: {e}")
            # Fallback to JSON
            return json.loads(data.decode())
    
    @staticmethod
    def benchmark(data: Dict, iterations: int = 1000) -> Dict[str, Dict]:
        """Benchmark compression methods"""
        import time
        
        results = {}
        
        for name, compressor in CompressionManager.COMPRESSION_METHODS.items():
            try:
                # Test compression
                start = time.time()
                for _ in range(iterations):
                    if name == 'json_minify':
                        compressed = compressor.compress(data).encode()
                    elif name == 'delta':
                        compressed = compressor.compress([data] * 10)
                    else:
                        compressed = compressor.compress(json.dumps(data))
                compress_time = (time.time() - start) / iterations
                
                # Test decompression
                start = time.time()
                for _ in range(iterations):
                    if name == 'json_minify':
                        compressor.decompress(compressed.decode())
                    elif name == 'delta':
                        compressor.decompress(compressed)
                    else:
                        compressor.decompress(compressed)
                decompress_time = (time.time() - start) / iterations
                
                # Calculate compression ratio
                original_size = len(json.dumps(data).encode())
                compressed_size = len(compressed)
                ratio = (1 - compressed_size / original_size) * 100
                
                results[name] = {
                    "compress_time_ms": compress_time * 1000,
                    "decompress_time_ms": decompress_time * 1000,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": f"{ratio:.1f}%"
                }
            except Exception as e:
                results[name] = {"error": str(e)}
        
        return results


# Example usage
if __name__ == "__main__":
    # Sample sensor reading
    sample_data = {
        "device_id": "sensor_001",
        "sensor_type": "air_quality",
        "timestamp": int(datetime.utcnow().timestamp()),
        "latitude": 37.7749,
        "longitude": -122.4194,
        "readings": {
            "pm25": 15.23,
            "pm10": 28.45,
            "co2": 420,
            "voc": 120.5,
            "temperature": 22.5,
            "humidity": 65.0
        }
    }
    
    # Test compression methods
    manager = CompressionManager()
    
    print("Compression Benchmark:")
    print("=" * 60)
    
    for method in ['json_minify', 'msgpack', 'cbor', 'gzip', 'lz4']:
        try:
            compressed = manager.compress(sample_data, method=method)
            decompressed = manager.decompress(compressed, method=method)
            
            original_size = len(json.dumps(sample_data).encode())
            compressed_size = len(compressed)
            ratio = (1 - compressed_size / original_size) * 100
            
            print(f"\n{method.upper()}:")
            print(f"  Original: {original_size} bytes")
            print(f"  Compressed: {compressed_size} bytes")
            print(f"  Ratio: {ratio:.1f}%")
            print(f"  Valid: {decompressed == sample_data or str(decompressed) == str(sample_data)}")
        except Exception as e:
            print(f"\n{method.upper()}: Error - {e}")
    
    # Test delta encoding with time series
    time_series = []
    base_time = int(datetime.utcnow().timestamp())
    for i in range(100):
        time_series.append({
            "timestamp": base_time + i * 60,
            "temperature": 20.0 + i * 0.1,
            "humidity": 60.0 + i * 0.05
        })
    
    delta_encoded = DeltaEncoder.compress(time_series)
    original_size = len(json.dumps(time_series).encode())
    
    print(f"\n\nDelta Encoding (Time Series):")
    print(f"  Original: {original_size} bytes")
    print(f"  Compressed: {len(delta_encoded)} bytes")
    print(f"  Ratio: {(1 - len(delta_encoded) / original_size) * 100:.1f}%")
    
    # Verify
    decoded = DeltaEncoder.decompress(delta_encoded)
    print(f"  Valid: {len(decoded) == len(time_series)}")
```

---

## 11. Battery Optimization

### 11.1 Power Management Strategies

| Strategy | Power Savings | Implementation Complexity | Best For |
|----------|--------------|---------------------------|----------|
| **Deep Sleep** | 90-99% | Low | Infrequent sampling |
| **Adaptive Sampling** | 30-50% | Medium | Variable conditions |
| **Data Batching** | 20-40% | Low | Regular transmissions |
| **Transmission Optimization** | 15-30% | Medium | All devices |
| **Sensor Power Cycling** | 10-25% | Low | Power-hungry sensors |
| **Low-Power Radio** | 40-60% | Medium | Remote deployments |

### 11.2 Battery Optimization Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/battery_optimization.py
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
```



---

## 12. Cost Analysis

### 12.1 Infrastructure Costs (Monthly Estimates)

| Component | Small Scale (100 devices) | Medium Scale (1,000 devices) | Large Scale (10,000 devices) |
|-----------|---------------------------|------------------------------|------------------------------|
| **AWS IoT Core** | $50 | $400 | $3,500 |
| **Data Storage (S3)** | $25 | $150 | $1,000 |
| **Database (DynamoDB)** | $30 | $200 | $1,500 |
| **Compute (EC2/Lambda)** | $100 | $500 | $3,000 |
| **Data Transfer** | $20 | $100 | $800 |
| **Monitoring (CloudWatch)** | $15 | $75 | $400 |
| **Total Cloud** | **$240** | **$1,425** | **$10,200** |

### 12.2 Hardware Costs (Per Device)

| Device Type | Components | Unit Cost | Annual Maintenance |
|-------------|-----------|-----------|-------------------|
| **Basic Air Quality** | PM2.5, Temp, Hum | $80-120 | $15 |
| **Weather Station** | Multi-sensor | $150-250 | $25 |
| **Seismic Monitor** | Accelerometer + Gateway | $500-800 | $50 |
| **Flood Sensor** | Ultrasonic + LoRa | $200-350 | $30 |
| **Fire Detection** | Multi-gas + Temp | $300-500 | $40 |
| **Edge Gateway** | Raspberry Pi 4 Kit | $150-200 | $20 |
| **Cellular Gateway** | 4G LTE + Edge | $400-600 | $50 |

### 12.3 Total Cost of Ownership (5-Year)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    5-YEAR TOTAL COST OF OWNERSHIP                            │
│                         (1,000 Device Deployment)                            │
└─────────────────────────────────────────────────────────────────────────────┘

Hardware (Initial):        $250,000  ████████████████████  35%
├── Air Quality Sensors:   $100,000
├── Weather Stations:       $50,000
├── Edge Gateways:          $60,000
├── Seismic Sensors:        $25,000
└── Installation:           $15,000

Cloud Services:            $85,500  ███████  12%
├── IoT Platform:          $24,000
├── Storage:                $9,000
├── Compute:               $30,000
└── Data Transfer:          $7,500

Connectivity:              $90,000  ███████  13%
├── Cellular Data:         $60,000
└── LoRaWAN Network:       $30,000

Maintenance:               $150,000  ████████████  21%
├── Hardware Replacement:  $75,000
├── Field Service:         $50,000
└── Calibration:           $25,000

Operations:                $130,000  ██████████  18%
├── Monitoring:            $40,000
├── Security Updates:      $30,000
└── Staff Time:            $60,000

─────────────────────────────────────────────────────────────────────────────
TOTAL 5-YEAR TCO:          $705,500
Annual Average:            $141,100
Cost per Device/Year:      $141
```

### 12.4 Cost Optimization Strategies

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| **Edge Processing** | 30-40% data transfer | Process data locally, send summaries |
| **Data Compression** | 50-70% bandwidth | Use MessagePack/CBOR + delta encoding |
| **Batch Transmission** | 20-30% connectivity | Accumulate readings, transmit batches |
| **Tiered Storage** | 40-50% storage costs | Hot (7d) → Warm (90d) → Cold (archive) |
| **Reserved Instances** | 30-40% compute | 1-3 year commitments for stable workloads |
| **Spot Instances** | 60-70% compute | For fault-tolerant batch processing |

---

## 13. Implementation Priority Order

### 13.1 Phase 1: Foundation (Months 1-3)

| Priority | Component | Effort | Business Value |
|----------|-----------|--------|----------------|
| **P0** | MQTT Infrastructure | 2 weeks | Critical - All communication |
| **P0** | Device Registration | 1 week | Critical - Device identity |
| **P0** | Basic Data Ingestion | 2 weeks | Critical - Data collection |
| **P1** | Security (TLS/Certs) | 2 weeks | High - Data protection |
| **P1** | Cloud Storage | 1 week | High - Data persistence |
| **P2** | Device Monitoring | 1 week | Medium - Operational visibility |

**Phase 1 Deliverables:**
- Secure MQTT broker cluster
- Device provisioning system
- Basic sensor data ingestion pipeline
- Encrypted communication channels
- Device health monitoring dashboard

### 13.2 Phase 2: Core Features (Months 4-6)

| Priority | Component | Effort | Business Value |
|----------|-----------|--------|----------------|
| **P0** | Edge Computing Nodes | 3 weeks | Critical - Local processing |
| **P0** | Real-time Alerting | 2 weeks | Critical - Disaster response |
| **P1** | Sensor Calibration | 2 weeks | High - Data accuracy |
| **P1** | Data Compression | 1 week | High - Bandwidth savings |
| **P2** | Battery Optimization | 2 weeks | Medium - Extended deployments |
| **P2** | OTA Updates | 2 weeks | Medium - Maintenance efficiency |

**Phase 2 Deliverables:**
- Edge gateway deployment
- Real-time anomaly detection
- Automated calibration system
- Compressed data transmission
- Power management for remote sensors
- Remote firmware update capability

### 13.3 Phase 3: Advanced Features (Months 7-9)

| Priority | Component | Effort | Business Value |
|----------|-----------|--------|----------------|
| **P1** | Stream Processing | 3 weeks | High - Real-time analytics |
| **P1** | ML at Edge | 4 weeks | High - Predictive capabilities |
| **P2** | Advanced Security | 2 weeks | Medium - Enhanced protection |
| **P2** | Multi-Protocol Support | 2 weeks | Medium - Device flexibility |
| **P3** | Historical Analytics | 2 weeks | Low - Trend analysis |

**Phase 3 Deliverables:**
- Kafka/Kinesis stream processing
- TensorFlow Lite inference on edge
- Hardware security module integration
- LoRaWAN/Modbus protocol support
- Long-term trend analysis dashboard

### 13.4 Phase 4: Scale & Optimize (Months 10-12)

| Priority | Component | Effort | Business Value |
|----------|-----------|--------|----------------|
| **P1** | Auto-scaling | 2 weeks | High - Handle growth |
| **P2** | Cost Optimization | 2 weeks | Medium - Reduce expenses |
| **P2** | Advanced Monitoring | 2 weeks | Medium - Operations |
| **P3** | Custom Dashboards | 2 weeks | Low - User experience |
| **P3** | API Gateway | 2 weeks | Low - External integration |

**Phase 4 Deliverables:**
- Auto-scaling infrastructure
- Cost monitoring and optimization
- Comprehensive observability stack
- Custom visualization dashboards
- Public API for third-party access

### 13.5 Implementation Roadmap

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI IoT IMPLEMENTATION ROADMAP                   │
└─────────────────────────────────────────────────────────────────────────────┘

MONTH:    1      2      3      4      5      6      7      8      9     10     11     12
          │      │      │      │      │      │      │      │      │      │      │      │
PHASE 1:  ├──────┴──────┤
          │ Foundation  │
          │             │
PHASE 2:                ├─────────────┴─────────────┤
                        │      Core Features        │
                        │                           │
PHASE 3:                                              ├─────────────┴─────────────┤
                                                      │    Advanced Features      │
                                                      │                           │
PHASE 4:                                                                            ├─────────────┴─────────────┤
                                                                                    │   Scale & Optimize        │

MILESTONES:
├── M1 (Mo 3): 100 devices online, basic ingestion working
├── M2 (Mo 6): 500 devices, edge processing, real-time alerts
├── M3 (Mo 9): 1,000 devices, ML inference, stream processing
└── M4 (Mo 12): 2,000+ devices, auto-scaling, cost-optimized
```

---

## 14. Use Case Analysis

### 14.1 Wildfire Early Detection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WILDFIRE EARLY DETECTION SYSTEM                           │
└─────────────────────────────────────────────────────────────────────────────┘

SENSOR NETWORK:
├── Temperature sensors (every 2km in high-risk areas)
├── Smoke/CO detectors (every 5km)
├── Air quality monitors (PM2.5, PM10)
└── Weather stations (wind, humidity)

DETECTION PIPELINE:
1. Edge nodes monitor temperature gradients
2. ML model detects anomalous heat patterns
3. Multi-sensor correlation confirms fire signature
4. Alert sent within 30 seconds of detection
5. Fire department notified with GPS coordinates

EXPECTED IMPACT:
├── Detection time: 15-30 minutes (vs 1-2 hours manual)
├── False positive rate: <5%
├── Coverage area: 10,000 sq km per 100 sensors
└── Cost per sq km: $2,500/year
```

### 14.2 Flood Monitoring System

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLOOD MONITORING SYSTEM                              │
└─────────────────────────────────────────────────────────────────────────────┘

SENSOR NETWORK:
├── Ultrasonic water level sensors (rivers, streams)
├── Rain gauges (watershed areas)
├── Soil moisture sensors
└── Weather stations (precipitation forecasting)

PREDICTION PIPELINE:
1. Real-time water level monitoring
2. Rainfall intensity analysis
3. Upstream/downstream correlation
4. Hydrological model predictions
5. Multi-hour advance warning

EXPECTED IMPACT:
├── Warning time: 2-6 hours advance notice
├── Accuracy: 85% for 4-hour predictions
├── Coverage: 50 river monitoring points
└── Cost per monitoring point: $3,000/year
```

### 14.3 Air Quality Monitoring

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AIR QUALITY MONITORING NETWORK                         │
└─────────────────────────────────────────────────────────────────────────────┘

SENSOR NETWORK:
├── PM2.5/PM10 sensors (urban areas, every 1km)
├── CO2/VOC sensors (industrial zones)
├── NO2/SO2 sensors (traffic corridors)
└── Weather data (wind, temperature, humidity)

ANALYTICS PIPELINE:
1. Continuous pollutant monitoring
2. Source attribution modeling
3. Health impact assessment
4. Public alert system
5. Regulatory compliance reporting

EXPECTED IMPACT:
├── Spatial resolution: 1km grid
├── Temporal resolution: 5-minute updates
├── Health alerts: Real-time AQI notifications
└── Cost per sensor: $150/year operational
```

---

## 15. Sensor Integration Examples

### 15.1 Air Quality Sensor (PMS5003 + BME280)

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/code/sensor_integration_example.py
"""
Example: Integrating PMS5003 Air Quality Sensor with BME280 Environmental Sensor
"""

import time
import struct
import serial
from dataclasses import dataclass
from typing import Optional, Dict
import board
import busio
import adafruit_bme280


@dataclass
class AirQualityReading:
    """Combined air quality and environmental reading"""
    pm10_standard: int
    pm25_standard: int
    pm100_standard: int
    pm10_env: int
    pm25_env: int
    pm100_env: int
    particles_03um: int
    particles_05um: int
    particles_10um: int
    particles_25um: int
    particles_50um: int
    particles_100um: int
    temperature: float
    humidity: float
    pressure: float
    timestamp: float


class PMS5003Sensor:
    """PMS5003 Particulate Matter Sensor Interface"""
    
    # PMS5003 data frame structure
    FRAME_START = b'\x42\x4d'
    FRAME_LENGTH = 32
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
    def connect(self) -> bool:
        """Connect to PMS5003 sensor"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2
            )
            return True
        except Exception as e:
            print(f"Failed to connect to PMS5003: {e}")
            return False
    
    def read(self) -> Optional[Dict]:
        """Read data from PMS5003"""
        if not self.serial:
            return None
        
        # Find frame start
        while True:
            byte = self.serial.read(1)
            if not byte:
                return None
            if byte == b'\x42':
                next_byte = self.serial.read(1)
                if next_byte == b'\x4d':
                    break
        
        # Read rest of frame
        data = self.serial.read(30)
        if len(data) != 30:
            return None
        
        # Parse frame
        values = struct.unpack('>HHHHHHHHHHHHH', data[:26])
        
        return {
            'pm10_standard': values[0],
            'pm25_standard': values[1],
            'pm100_standard': values[2],
            'pm10_env': values[3],
            'pm25_env': values[4],
            'pm100_env': values[5],
            'particles_03um': values[6],
            'particles_05um': values[7],
            'particles_10um': values[8],
            'particles_25um': values[9],
            'particles_50um': values[10],
            'particles_100um': values[11]
        }
    
    def close(self):
        """Close serial connection"""
        if self.serial:
            self.serial.close()


class BME280Sensor:
    """BME280 Temperature/Humidity/Pressure Sensor Interface"""
    
    def __init__(self, i2c_address: int = 0x77):
        self.i2c_address = i2c_address
        self.sensor = None
        
    def connect(self) -> bool:
        """Connect to BME280 sensor"""
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_bme280.Adafruit_BME280_I2C(
                i2c,
                address=self.i2c_address
            )
            # Configure sea level pressure for altitude calculation
            self.sensor.sea_level_pressure = 1013.25
            return True
        except Exception as e:
            print(f"Failed to connect to BME280: {e}")
            return False
    
    def read(self) -> Optional[Dict]:
        """Read data from BME280"""
        if not self.sensor:
            return None
        
        return {
            'temperature': self.sensor.temperature,
            'humidity': self.sensor.relative_humidity,
            'pressure': self.sensor.pressure,
            'altitude': self.sensor.altitude
        }


class CombinedAirQualityNode:
    """Combined air quality monitoring node"""
    
    def __init__(self, device_id: str, location: Dict[str, float]):
        self.device_id = device_id
        self.location = location
        self.pms5003 = PMS5003Sensor()
        self.bme280 = BME280Sensor()
        
    def initialize(self) -> bool:
        """Initialize all sensors"""
        pms_ok = self.pms5003.connect()
        bme_ok = self.bme280.connect()
        
        if pms_ok and bme_ok:
            print(f"Node {self.device_id} initialized successfully")
            return True
        else:
            print(f"Node {self.device_id} initialization failed")
            return False
    
    def read(self) -> Optional[AirQualityReading]:
        """Read combined sensor data"""
        pm_data = self.pms5003.read()
        env_data = self.bme280.read()
        
        if not pm_data or not env_data:
            return None
        
        return AirQualityReading(
            timestamp=time.time(),
            **pm_data,
            **env_data
        )
    
    def to_dict(self, reading: AirQualityReading) -> Dict:
        """Convert reading to dictionary for transmission"""
        return {
            'device_id': self.device_id,
            'timestamp': reading.timestamp,
            'location': self.location,
            'readings': {
                'pm25': reading.pm25_standard,
                'pm10': reading.pm10_standard,
                'pm100': reading.pm100_standard,
                'particles_03um': reading.particles_03um,
                'particles_05um': reading.particles_05um,
                'particles_10um': reading.particles_10um,
                'temperature': round(reading.temperature, 2),
                'humidity': round(reading.humidity, 2),
                'pressure': round(reading.pressure, 2)
            }
        }


# Example usage
if __name__ == "__main__":
    # Create sensor node
    node = CombinedAirQualityNode(
        device_id="AQ-SF-001",
        location={"lat": 37.7749, "lon": -122.4194}
    )
    
    # Initialize
    if node.initialize():
        # Take readings
        for i in range(5):
            reading = node.read()
            if reading:
                data = node.to_dict(reading)
                print(f"Reading {i+1}: {data}")
            time.sleep(5)
```

---

## 16. Summary and Recommendations

### 16.1 Key Findings

1. **Architecture**: A hybrid edge-cloud architecture provides the best balance of real-time responsiveness and cost efficiency
2. **Protocol**: MQTT with TLS 1.3 is the optimal choice for IoT communication
3. **Security**: Multi-layer security with certificate-based authentication is essential
4. **Cost**: Edge processing can reduce cloud costs by 30-40%
5. **Scalability**: The proposed architecture can scale to 100,000+ devices

### 16.2 Recommended Technology Stack

| Component | Recommended Technology |
|-----------|----------------------|
| **IoT Platform** | AWS IoT Core + Greengrass |
| **MQTT Broker** | EMQX or Mosquitto |
| **Edge Hardware** | Raspberry Pi 4 / NVIDIA Jetson Nano |
| **Stream Processing** | Apache Kafka + Kafka Streams |
| **Time-Series DB** | InfluxDB or TimescaleDB |
| **Analytics** | Apache Spark / AWS SageMaker |
| **Visualization** | Grafana + Custom Dashboards |

### 16.3 Critical Success Factors

1. **Reliable Connectivity**: Implement multiple connectivity options (cellular, LoRa, WiFi)
2. **Power Management**: Battery optimization is critical for remote deployments
3. **Data Quality**: Automated calibration and validation ensure reliable data
4. **Security**: Defense-in-depth approach with encryption at all layers
5. **Operations**: Comprehensive monitoring and remote management capabilities

### 16.4 Next Steps

1. **Proof of Concept**: Deploy 10-device pilot in controlled environment
2. **Security Audit**: Conduct thorough security review before production
3. **Performance Testing**: Validate system under expected load
4. **Cost Optimization**: Implement cost monitoring and optimization
5. **Documentation**: Create operational runbooks and troubleshooting guides

---

## Appendix A: File Structure

```
/mnt/okcomputer/output/resilience_ai_analysis/
├── 73_iot_sensors.md                    # This document
└── code/
    ├── mqtt_client.py                   # MQTT client implementation
    ├── sensor_ingestion.py              # Data ingestion pipeline
    ├── sensor_calibration.py            # Calibration management
    ├── edge_node.py                     # Edge computing node
    ├── realtime_processor.py            # Stream processing
    ├── device_manager.py                # Device lifecycle management
    ├── security.py                      # Security implementation
    ├── compression.py                   # Data compression
    ├── battery_optimization.py          # Power management
    └── sensor_integration_example.py    # Hardware integration example
```

## Appendix B: Additional Resources

- [AWS IoT Core Documentation](https://docs.aws.amazon.com/iot/)
- [MQTT Specification](https://mqtt.org/mqtt-specification/)
- [OWASP IoT Security](https://owasp.org/www-project-internet-of-things/)
- [LoRaWAN Specification](https://lora-alliance.org/about-lorawan/)

---

*Document generated for ResilienceAI IoT Sensor Integration Analysis*
*Version: 1.0 | Date: 2024*
