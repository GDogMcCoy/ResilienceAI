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
