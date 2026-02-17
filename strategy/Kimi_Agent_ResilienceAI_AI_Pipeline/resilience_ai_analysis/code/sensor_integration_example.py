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
