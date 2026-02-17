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
