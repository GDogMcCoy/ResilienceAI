"""
Trend analysis for load testing results
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics
import numpy as np


@dataclass
class TrendResult:
    """Trend analysis result"""
    metric_name: str
    trend_direction: str  # increasing, decreasing, stable
    slope: float
    r_squared: float
    confidence: float
    forecast: List[float]
    anomaly_points: List[int]


class TrendAnalyzer:
    """
    Analyze performance trends from load test results
    """
    
    def __init__(self):
        self.history: Dict[str, List[Dict]] = {}
    
    def add_data_point(self, metric_name: str, timestamp: datetime, value: float):
        """Add a data point for analysis"""
        if metric_name not in self.history:
            self.history[metric_name] = []
        
        self.history[metric_name].append({
            'timestamp': timestamp,
            'value': value,
        })
    
    def analyze_trend(self, metric_name: str, 
                      window_size: int = 10) -> Optional[TrendResult]:
        """
        Analyze trend for a specific metric
        
        Args:
            metric_name: Name of the metric
            window_size: Number of data points to analyze
        
        Returns:
            TrendResult if enough data, None otherwise
        """
        if metric_name not in self.history:
            return None
        
        data = self.history[metric_name]
        if len(data) < window_size:
            return None
        
        # Get recent window
        recent_data = data[-window_size:]
        values = [d['value'] for d in recent_data]
        
        # Perform linear regression
        x = list(range(len(values)))
        slope, intercept, r_value = self._linear_regression(x, values)
        
        # Determine trend direction
        trend_direction = self._classify_trend(slope, values)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(values)
        
        # Generate forecast
        forecast = self._forecast(values, slope, steps=5)
        
        return TrendResult(
            metric_name=metric_name,
            trend_direction=trend_direction,
            slope=slope,
            r_squared=r_value ** 2,
            confidence=abs(r_value),
            forecast=forecast,
            anomaly_points=anomalies,
        )
    
    def _linear_regression(self, x: List[float], 
                           y: List[float]) -> Tuple[float, float, float]:
        """
        Perform simple linear regression
        
        Returns:
            Tuple of (slope, intercept, correlation_coefficient)
        """
        n = len(x)
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        # Calculate slope
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0, y_mean, 0
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Calculate correlation coefficient
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        if ss_tot == 0:
            r_value = 0
        else:
            r_value = (1 - ss_res / ss_tot) ** 0.5
        
        return slope, intercept, r_value
    
    def _classify_trend(self, slope: float, values: List[float]) -> str:
        """Classify trend direction based on slope"""
        if not values:
            return "stable"
        
        y_mean = statistics.mean(values)
        relative_change = abs(slope) / max(y_mean, 1)
        
        if relative_change < 0.05:  # Less than 5% change
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _detect_anomalies(self, values: List[float], 
                          threshold: float = 2.0) -> List[int]:
        """
        Detect anomalous data points using z-score
        
        Args:
            values: List of values
            threshold: Z-score threshold
        
        Returns:
            List of indices of anomalous points
        """
        if len(values) < 3:
            return []
        
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        
        if std == 0:
            return []
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = abs((value - mean) / std)
            if z_score > threshold:
                anomalies.append(i)
        
        return anomalies
    
    def _forecast(self, values: List[float], slope: float, 
                  steps: int = 5) -> List[float]:
        """
        Generate simple forecast based on trend
        
        Args:
            values: Historical values
            slope: Trend slope
            steps: Number of steps to forecast
        
        Returns:
            List of forecasted values
        """
        if not values:
            return []
        
        last_value = values[-1]
        forecast = []
        
        for i in range(1, steps + 1):
            forecasted = last_value + slope * i
            forecast.append(max(0, forecasted))  # Don't forecast negative values
        
        return forecast
    
    def detect_performance_regression(self, 
                                      baseline: Dict[str, float],
                                      current: Dict[str, float],
                                      thresholds: Dict[str, float] = None) -> Dict:
        """
        Detect performance regression between baseline and current
        
        Args:
            baseline: Baseline metrics
            current: Current metrics
            thresholds: Regression thresholds
        
        Returns:
            Regression analysis
        """
        if thresholds is None:
            thresholds = {
                'response_time': 1.2,  # 20% increase
                'error_rate': 5.0,      # 5x increase
                'throughput': 0.8,      # 20% decrease
            }
        
        regressions = []
        
        for metric, threshold in thresholds.items():
            if metric in baseline and metric in current:
                baseline_value = baseline[metric]
                current_value = current[metric]
                
                if baseline_value == 0:
                    continue
                
                ratio = current_value / baseline_value
                
                if metric == 'throughput':
                    # For throughput, decrease is regression
                    if ratio < threshold:
                        regressions.append({
                            'metric': metric,
                            'baseline': baseline_value,
                            'current': current_value,
                            'change_percent': (1 - ratio) * 100,
                            'severity': self._get_regression_severity(ratio, threshold),
                        })
                else:
                    # For others, increase is regression
                    if ratio > threshold:
                        regressions.append({
                            'metric': metric,
                            'baseline': baseline_value,
                            'current': current_value,
                            'change_percent': (ratio - 1) * 100,
                            'severity': self._get_regression_severity(ratio, threshold),
                        })
        
        return {
            'has_regression': len(regressions) > 0,
            'regressions': regressions,
            'summary': f"Found {len(regressions)} performance regressions" if regressions else "No regressions detected",
        }
    
    def _get_regression_severity(self, ratio: float, threshold: float) -> str:
        """Determine regression severity"""
        if ratio > threshold * 2:
            return "critical"
        elif ratio > threshold * 1.5:
            return "high"
        elif ratio > threshold * 1.2:
            return "medium"
        else:
            return "low"
    
    def generate_trend_report(self) -> Dict:
        """Generate comprehensive trend report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics_analyzed': list(self.history.keys()),
            'trends': {},
            'anomalies': {},
            'forecasts': {},
        }
        
        for metric_name in self.history:
            trend = self.analyze_trend(metric_name)
            if trend:
                report['trends'][metric_name] = {
                    'direction': trend.trend_direction,
                    'slope': trend.slope,
                    'confidence': trend.confidence,
                }
                report['anomalies'][metric_name] = trend.anomaly_points
                report['forecasts'][metric_name] = trend.forecast
        
        return report
