"""
Load Forecasting System for Capacity Planning
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
from enum import Enum


class ForecastModel(Enum):
    LINEAR = "linear"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    ENSEMBLE = "ensemble"


@dataclass
class ForecastResult:
    """Forecast result with confidence intervals"""
    timestamp: datetime
    forecast_value: float
    lower_bound: float
    upper_bound: float
    confidence: float
    model_used: ForecastModel


@dataclass
class LoadForecast:
    """Complete load forecast for multiple horizons"""
    service_name: str
    metric_name: str
    generated_at: datetime
    
    # Forecasts by horizon
    short_term: List[ForecastResult]  # Next 1 hour
    medium_term: List[ForecastResult]  # Next 24 hours
    long_term: List[ForecastResult]   # Next 7 days
    
    # Trend analysis
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_slope: float
    seasonality_detected: bool
    peak_times: List[datetime]


class LoadForecaster:
    """Multi-model load forecasting system"""
    
    def __init__(self):
        self.models = {
            ForecastModel.LINEAR: self._linear_forecast,
            ForecastModel.EXPONENTIAL_SMOOTHING: self._exponential_smoothing_forecast,
            ForecastModel.ENSEMBLE: self._ensemble_forecast,
        }
        self.historical_data: Dict[str, deque] = {}
        
    def _linear_forecast(
        self, 
        data: List[float], 
        horizon: int,
        confidence: float = 0.95
    ) -> List[Tuple[float, float, float]]:
        """Simple linear regression forecast"""
        if len(data) < 2:
            return [(data[-1] if data else 0, 0, 0) for _ in range(horizon)]
        
        x = np.arange(len(data))
        y = np.array(data)
        
        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate standard error
        predictions = slope * x + intercept
        residuals = y - predictions
        mse = np.mean(residuals ** 2)
        std_error = np.sqrt(mse)
        
        # Confidence interval multiplier (95% = 1.96)
        z_score = 1.96 if confidence == 0.95 else 1.645
        
        forecasts = []
        for i in range(1, horizon + 1):
            forecast_x = len(data) + i
            forecast_y = slope * forecast_x + intercept
            margin = z_score * std_error * np.sqrt(1 + 1/len(data))
            
            forecasts.append((
                max(0, forecast_y),
                max(0, forecast_y - margin),
                forecast_y + margin
            ))
        
        return forecasts
    
    def _exponential_smoothing_forecast(
        self, 
        data: List[float], 
        horizon: int,
        alpha: float = 0.3
    ) -> List[Tuple[float, float, float]]:
        """Exponential smoothing forecast"""
        if not data:
            return [(0, 0, 0) for _ in range(horizon)]
        
        # Initialize
        smoothed = [data[0]]
        
        # Apply smoothing
        for i in range(1, len(data)):
            smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[-1])
        
        # Forecast
        last_smoothed = smoothed[-1]
        
        # Calculate error for confidence intervals
        errors = [abs(data[i] - smoothed[i]) for i in range(len(data))]
        mae = np.mean(errors)
        
        forecasts = []
        for i in range(1, horizon + 1):
            forecast = last_smoothed
            margin = mae * (1 + 0.1 * i)  # Increasing uncertainty
            forecasts.append((
                max(0, forecast),
                max(0, forecast - margin),
                forecast + margin
            ))
        
        return forecasts
    
    def _ensemble_forecast(
        self, 
        data: List[float], 
        horizon: int
    ) -> List[Tuple[float, float, float]]:
        """Combine multiple forecasting models"""
        linear = self._linear_forecast(data, horizon)
        exp_smooth = self._exponential_smoothing_forecast(data, horizon)
        
        # Simple average ensemble
        ensemble = []
        for i in range(horizon):
            avg_point = (linear[i][0] + exp_smooth[i][0]) / 2
            avg_lower = (linear[i][1] + exp_smooth[i][1]) / 2
            avg_upper = (linear[i][2] + exp_smooth[i][2]) / 2
            ensemble.append((avg_point, avg_lower, avg_upper))
        
        return ensemble
    
    def forecast(
        self,
        service_name: str,
        metric_name: str,
        historical_data: List[float],
        timestamps: List[datetime],
        model: ForecastModel = ForecastModel.ENSEMBLE
    ) -> LoadForecast:
        """Generate comprehensive load forecast"""
        
        # Store historical data
        key = f"{service_name}:{metric_name}"
        if key not in self.historical_data:
            self.historical_data[key] = deque(maxlen=10080)
        
        for val, ts in zip(historical_data, timestamps):
            self.historical_data[key].append((ts, val))
        
        # Detect seasonality
        seasonality = self._detect_seasonality(historical_data)
        
        # Determine trend
        trend_direction, trend_slope = self._analyze_trend(historical_data)
        
        # Generate forecasts for different horizons
        forecast_fn = self.models.get(model, self._ensemble_forecast)
        
        # Short-term: 1 hour (60 points at 1-min intervals)
        short_term_raw = forecast_fn(historical_data, 60)
        short_term = self._create_forecast_results(
            short_term_raw, timestamps[-1], timedelta(minutes=1), model
        )
        
        # Medium-term: 24 hours (24 points at 1-hour intervals)
        hourly_data = self._aggregate_hourly(historical_data, timestamps)
        medium_term_raw = forecast_fn(hourly_data, 24)
        medium_term = self._create_forecast_results(
            medium_term_raw, timestamps[-1], timedelta(hours=1), model
        )
        
        # Long-term: 7 days (7 points at 1-day intervals)
        daily_data = self._aggregate_daily(historical_data, timestamps)
        long_term_raw = forecast_fn(daily_data, 7)
        long_term = self._create_forecast_results(
            long_term_raw, timestamps[-1], timedelta(days=1), model
        )
        
        # Identify peak times
        peak_times = self._identify_peak_times(historical_data, timestamps)
        
        return LoadForecast(
            service_name=service_name,
            metric_name=metric_name,
            generated_at=datetime.now(),
            short_term=short_term,
            medium_term=medium_term,
            long_term=long_term,
            trend_direction=trend_direction,
            trend_slope=trend_slope,
            seasonality_detected=seasonality.get('detected', False),
            peak_times=peak_times
        )
    
    def _create_forecast_results(
        self,
        forecasts: List[Tuple[float, float, float]],
        start_time: datetime,
        interval: timedelta,
        model: ForecastModel
    ) -> List[ForecastResult]:
        """Create ForecastResult objects from raw forecasts"""
        results = []
        for i, (point, lower, upper) in enumerate(forecasts):
            results.append(ForecastResult(
                timestamp=start_time + interval * (i + 1),
                forecast_value=point,
                lower_bound=lower,
                upper_bound=upper,
                confidence=0.95,
                model_used=model
            ))
        return results
    
    def _detect_seasonality(self, data: List[float]) -> Dict:
        """Detect seasonality patterns in data"""
        if len(data) < 24:
            return {'detected': False}
        return {'detected': True, 'period': 24}
    
    def _analyze_trend(self, data: List[float]) -> Tuple[str, float]:
        """Analyze trend direction and slope"""
        if len(data) < 2:
            return 'stable', 0.0
        
        x = np.arange(len(data))
        y = np.array(data)
        slope, _ = np.polyfit(x, y, 1)
        
        if slope > 0.01:
            return 'increasing', slope
        elif slope < -0.01:
            return 'decreasing', slope
        else:
            return 'stable', slope
    
    def _aggregate_hourly(self, data: List[float], timestamps: List[datetime]) -> List[float]:
        """Aggregate data to hourly averages"""
        from collections import defaultdict
        hourly = defaultdict(list)
        for val, ts in zip(data, timestamps):
            hour_key = ts.replace(minute=0, second=0, microsecond=0)
            hourly[hour_key].append(val)
        
        return [np.mean(hourly[k]) for k in sorted(hourly.keys())]
    
    def _aggregate_daily(self, data: List[float], timestamps: List[datetime]) -> List[float]:
        """Aggregate data to daily averages"""
        from collections import defaultdict
        daily = defaultdict(list)
        for val, ts in zip(data, timestamps):
            day_key = ts.date()
            daily[day_key].append(val)
        
        return [np.mean(daily[k]) for k in sorted(daily.keys())]
    
    def _identify_peak_times(self, data: List[float], timestamps: List[datetime]) -> List[datetime]:
        """Identify peak usage times"""
        if not data:
            return []
        
        threshold = np.percentile(data, 90)
        peaks = [timestamps[i] for i, val in enumerate(data) if val >= threshold]
        return peaks[:10]
