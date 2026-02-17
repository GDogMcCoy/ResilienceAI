"""
Performance Baseline Management
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np


@dataclass
class PerformanceBaseline:
    """Performance baseline for a service/metric"""
    service_name: str
    metric_name: str
    
    # Baseline values
    baseline_value: float
    baseline_p50: float
    baseline_p95: float
    baseline_p99: float
    
    # Thresholds
    warning_threshold: float
    critical_threshold: float
    
    # Metadata
    established_at: datetime
    sample_size: int
    time_window_days: int
    
    # Seasonal adjustments
    has_seasonality: bool
    hourly_baselines: Optional[Dict[int, float]] = None
    daily_baselines: Optional[Dict[int, float]] = None


class BaselineManager:
    """Manage performance baselines"""
    
    def __init__(self):
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.historical_data: Dict[str, List[tuple]] = defaultdict(list)
        
    def collect_baseline_data(
        self,
        service_name: str,
        metric_name: str,
        value: float,
        timestamp: datetime
    ):
        """Collect data for baseline calculation"""
        key = f"{service_name}:{metric_name}"
        self.historical_data[key].append((timestamp, value))
    
    def establish_baseline(
        self,
        service_name: str,
        metric_name: str,
        time_window_days: int = 7,
        consider_seasonality: bool = True
    ) -> PerformanceBaseline:
        """Establish performance baseline from historical data"""
        
        key = f"{service_name}:{metric_name}"
        data = self.historical_data[key]
        
        # Filter to time window
        cutoff = datetime.now() - timedelta(days=time_window_days)
        window_data = [v for ts, v in data if ts >= cutoff]
        
        if len(window_data) < 10:
            raise ValueError(f"Insufficient data for baseline: {len(window_data)} samples")
        
        # Calculate statistics
        values = np.array(window_data)
        baseline_value = np.mean(values)
        p50 = np.percentile(values, 50)
        p95 = np.percentile(values, 95)
        p99 = np.percentile(values, 99)
        
        # Calculate thresholds
        warning_threshold = p95 * 1.5
        critical_threshold = p95 * 2.0
        
        # Detect seasonality
        hourly_baselines = None
        daily_baselines = None
        has_seasonality = False
        
        if consider_seasonality and len(window_data) >= 168:
            hourly_baselines = self._calculate_hourly_baselines(data, cutoff)
            daily_baselines = self._calculate_daily_baselines(data, cutoff)
            has_seasonality = self._detect_seasonality_pattern(hourly_baselines)
        
        baseline = PerformanceBaseline(
            service_name=service_name,
            metric_name=metric_name,
            baseline_value=baseline_value,
            baseline_p50=p50,
            baseline_p95=p95,
            baseline_p99=p99,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            established_at=datetime.now(),
            sample_size=len(window_data),
            time_window_days=time_window_days,
            has_seasonality=has_seasonality,
            hourly_baselines=hourly_baselines,
            daily_baselines=daily_baselines
        )
        
        self.baselines[key] = baseline
        return baseline
    
    def _calculate_hourly_baselines(self, data: List[tuple], cutoff: datetime) -> Dict[int, float]:
        """Calculate hourly baselines"""
        hourly_values = defaultdict(list)
        
        for ts, value in data:
            if ts >= cutoff:
                hour = ts.hour
                hourly_values[hour].append(value)
        
        return {hour: np.mean(values) for hour, values in hourly_values.items()}
    
    def _calculate_daily_baselines(self, data: List[tuple], cutoff: datetime) -> Dict[int, float]:
        """Calculate daily baselines"""
        daily_values = defaultdict(list)
        
        for ts, value in data:
            if ts >= cutoff:
                day = ts.weekday()
                daily_values[day].append(value)
        
        return {day: np.mean(values) for day, values in daily_values.items()}
    
    def _detect_seasonality_pattern(self, hourly_baselines: Dict[int, float]) -> bool:
        """Detect if there's a significant seasonal pattern"""
        if not hourly_baselines:
            return False
        
        values = list(hourly_baselines.values())
        if len(values) < 2:
            return False
        
        mean_val = np.mean(values)
        std_val = np.std(values)
        cv = std_val / mean_val if mean_val > 0 else 0
        
        return cv > 0.2
    
    def check_against_baseline(
        self,
        service_name: str,
        metric_name: str,
        current_value: float,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """Check current value against baseline"""
        
        key = f"{service_name}:{metric_name}"
        baseline = self.baselines.get(key)
        
        if not baseline:
            return {'status': 'unknown', 'message': 'No baseline established'}
        
        # Adjust for seasonality if applicable
        expected_value = baseline.baseline_value
        if baseline.has_seasonality and timestamp:
            hour_baseline = baseline.hourly_baselines.get(timestamp.hour)
            if hour_baseline:
                expected_value = hour_baseline
        
        # Calculate deviation
        deviation = ((current_value - expected_value) / expected_value * 100) if expected_value > 0 else 0
        
        # Determine status
        if current_value > baseline.critical_threshold:
            status = 'critical'
        elif current_value > baseline.warning_threshold:
            status = 'warning'
        elif deviation > 50:
            status = 'elevated'
        else:
            status = 'normal'
        
        return {
            'status': status,
            'current_value': current_value,
            'expected_value': expected_value,
            'deviation_percent': deviation,
            'baseline_p95': baseline.baseline_p95,
            'warning_threshold': baseline.warning_threshold,
            'critical_threshold': baseline.critical_threshold
        }
    
    def get_baseline_report(self) -> Dict:
        """Generate baseline report"""
        report = {
            'total_baselines': len(self.baselines),
            'baselines': []
        }
        
        for key, baseline in self.baselines.items():
            report['baselines'].append({
                'service': baseline.service_name,
                'metric': baseline.metric_name,
                'baseline_value': baseline.baseline_value,
                'p95': baseline.baseline_p95,
                'has_seasonality': baseline.has_seasonality,
                'established_at': baseline.established_at.isoformat(),
                'sample_size': baseline.sample_size
            })
        
        return report
