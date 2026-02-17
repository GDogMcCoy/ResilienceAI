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
