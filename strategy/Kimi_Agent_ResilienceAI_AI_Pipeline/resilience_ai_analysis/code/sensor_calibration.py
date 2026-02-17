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
