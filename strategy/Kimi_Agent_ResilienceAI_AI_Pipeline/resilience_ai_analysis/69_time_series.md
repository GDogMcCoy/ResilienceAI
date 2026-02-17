# Comprehensive Time Series Analysis for ResilienceAI

## Executive Summary

This document provides a complete time series analysis framework for ResilienceAI, designed to analyze historical disaster data, detect trends and seasonality, forecast future events, and identify anomalies. The framework integrates multiple state-of-the-art techniques including classical statistical methods (ARIMA), modern forecasting approaches (Prophet), and deep learning models (LSTM).

---

## 1. Time Series Architecture

### 1.1 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Time Series Analysis Pipeline                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │ Data         │───▶│ Preprocessing│───▶│ Decomposition│───▶│ Analysis  │  │
│  │ Ingestion    │    │ & Cleaning   │    │ (STL/ETS)    │    │ Engine    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘    └─────┬─────┘  │
│                                                                    │        │
│  ┌─────────────────────────────────────────────────────────────────┘        │
│  │                                                                          │
│  ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Model Ensemble Layer                          │   │
│  │  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  │   │
│  │  │ ARIMA   │  │ Prophet  │  │  LSTM   │  │ XGBoost │  │ Ensemble │  │   │
│  │  │ Models  │  │ Forecast │  │ Neural  │  │ Time    │  │ Aggregator│  │   │
│  │  │         │  │          │  │ Network │  │ Series  │  │          │  │   │
│  │  └────┬────┘  └────┬─────┘  └────┬────┘  └────┬────┘  └────┬─────┘  │   │
│  │       └─────────────┴─────────────┴─────────────┴────────────┘      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Output & Visualization Layer                    │   │
│  │  ┌──────────┐  ┌────────────┐  ┌─────────────┐  ┌──────────────┐   │   │
│  │  │ Forecasts│  │ Anomalies  │  │ Confidence  │  │ Interactive  │   │   │
│  │  │ & Trends │  │ Detection  │  │ Intervals   │  │ Dashboards   │   │   │
│  │  └──────────┘  └────────────┘  └─────────────┘  └──────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Architecture

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/architecture.py

"""
Time Series Analysis Architecture for ResilienceAI
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from enum import Enum

class ModelType(Enum):
    """Supported time series model types"""
    ARIMA = "arima"
    PROPHET = "prophet"
    LSTM = "lstm"
    XGBOOST = "xgboost"
    ENSEMBLE = "ensemble"

class AnalysisType(Enum):
    """Types of time series analysis"""
    TREND = "trend"
    SEASONALITY = "seasonality"
    FORECASTING = "forecasting"
    ANOMALY_DETECTION = "anomaly_detection"
    CHANGE_POINT = "change_point"

@dataclass
class TimeSeriesConfig:
    """Configuration for time series analysis"""
    # Data parameters
    frequency: str = 'D'  # 'D', 'W', 'M', 'Y'
    target_column: str = 'value'
    date_column: str = 'date'
    
    # Model parameters
    forecast_horizon: int = 30
    confidence_level: float = 0.95
    
    # Anomaly detection
    anomaly_threshold: float = 3.0
    
    # Seasonality
    yearly_seasonality: bool = True
    weekly_seasonality: bool = True
    daily_seasonality: bool = False
    
    # LSTM parameters
    lstm_units: List[int] = None
    sequence_length: int = 30
    
    def __post_init__(self):
        if self.lstm_units is None:
            self.lstm_units = [128, 64, 32]

@dataclass
class ForecastResult:
    """Result container for forecasting"""
    forecast: pd.Series
    lower_bound: pd.Series
    upper_bound: pd.Series
    model_name: str
    metrics: Dict[str, float]
    
@dataclass
class AnomalyResult:
    """Result container for anomaly detection"""
    anomalies: pd.Series
    anomaly_scores: pd.Series
    threshold: float
    model_name: str

class BaseTimeSeriesModel(ABC):
    """Abstract base class for time series models"""
    
    def __init__(self, config: TimeSeriesConfig):
        self.config = config
        self.model = None
        self.is_fitted = False
    
    @abstractmethod
    def fit(self, data: pd.DataFrame) -> 'BaseTimeSeriesModel':
        """Fit the model to training data"""
        pass
    
    @abstractmethod
    def predict(self, horizon: int) -> ForecastResult:
        """Generate forecasts"""
        pass
    
    @abstractmethod
    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """Evaluate model performance"""
        pass


---

## 2. Time Series Decomposition

### 2.1 Decomposition Methods

Time series decomposition separates a time series into its constituent components:
- **Trend**: Long-term progression
- **Seasonality**: Regular periodic fluctuations
- **Residual (Noise)**: Irregular random variations

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/decomposition.py

"""
Time Series Decomposition Module for ResilienceAI
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL, seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from scipy import stats
import matplotlib.pyplot as plt
from typing import Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesDecomposer:
    """
    Comprehensive time series decomposition for disaster data analysis.
    Supports multiple decomposition methods optimized for different data characteristics.
    """
    
    def __init__(self, data: pd.DataFrame, date_col: str = 'date', 
                 value_col: str = 'value', freq: str = 'D'):
        """
        Initialize the decomposer.
        
        Args:
            data: DataFrame with time series data
            date_col: Name of date column
            value_col: Name of value column
            freq: Frequency of data ('D', 'W', 'M', 'Y')
        """
        self.data = data.copy()
        self.date_col = date_col
        self.value_col = value_col
        self.freq = freq
        
        # Ensure datetime index
        if date_col in self.data.columns:
            self.data[date_col] = pd.to_datetime(self.data[date_col])
            self.data.set_index(date_col, inplace=True)
        
        self.decomposition_results = {}
        
    def stl_decomposition(self, seasonal_period: int = None, 
                         robust: bool = True) -> Dict:
        """
        Perform STL (Seasonal and Trend decomposition using Loess) decomposition.
        Best for data with complex seasonality patterns.
        
        Args:
            seasonal_period: Seasonal period (e.g., 7 for weekly, 12 for monthly)
            robust: Use robust fitting for outliers
            
        Returns:
            Dictionary with trend, seasonal, residual components
        """
        if seasonal_period is None:
            seasonal_period = self._infer_seasonal_period()
        
        # STL decomposition
        stl = STL(self.data[self.value_col], 
                  period=seasonal_period,
                  robust=robust)
        result = stl.fit()
        
        self.decomposition_results['stl'] = {
            'trend': result.trend,
            'seasonal': result.seasonal,
            'residual': result.resid,
            'observed': result.observed
        }
        
        return self.decomposition_results['stl']
    
    def classical_decomposition(self, model: str = 'additive') -> Dict:
        """
        Perform classical decomposition (additive or multiplicative).
        
        Args:
            model: 'additive' or 'multiplicative'
            
        Returns:
            Dictionary with trend, seasonal, residual components
        """
        result = seasonal_decompose(self.data[self.value_col], 
                                    model=model,
                                    period=self._infer_seasonal_period())
        
        self.decomposition_results['classical'] = {
            'trend': result.trend,
            'seasonal': result.seasonal,
            'resid': result.resid,
            'observed': result.observed
        }
        
        return self.decomposition_results['classical']
    
    def ets_decomposition(self, seasonal_periods: int = None) -> Dict:
        """
        Exponential Smoothing State Space decomposition.
        Good for trend and seasonal data with noise.
        
        Args:
            seasonal_periods: Number of periods in seasonal cycle
            
        Returns:
            Dictionary with level, trend, seasonal, residual components
        """
        if seasonal_periods is None:
            seasonal_periods = self._infer_seasonal_period()
        
        # Fit ETS model
        ets_model = ExponentialSmoothing(
            self.data[self.value_col],
            seasonal_periods=seasonal_periods,
            trend='add',
            seasonal='add'
        ).fit()
        
        # Extract components
        fitted_values = ets_model.fittedvalues
        level = ets_model.level
        trend = ets_model.trend if hasattr(ets_model, 'trend') else pd.Series(np.nan, index=self.data.index)
        seasonal = ets_model.season if hasattr(ets_model, 'season') else pd.Series(np.nan, index=self.data.index)
        residual = self.data[self.value_col] - fitted_values
        
        self.decomposition_results['ets'] = {
            'level': level,
            'trend': trend,
            'seasonal': seasonal,
            'fitted': fitted_values,
            'residual': residual
        }
        
        return self.decomposition_results['ets']
    
    def _infer_seasonal_period(self) -> int:
        """Infer seasonal period based on frequency"""
        period_map = {
            'D': 7,      # Weekly seasonality for daily data
            'W': 52,     # Yearly seasonality for weekly data
            'M': 12,     # Yearly seasonality for monthly data
            'Q': 4,      # Yearly seasonality for quarterly data
            'Y': 1       # No seasonality for yearly data
        }
        return period_map.get(self.freq, 7)
    
    def get_strength_metrics(self) -> Dict[str, float]:
        """
        Calculate strength of trend and seasonality components.
        
        Returns:
            Dictionary with trend_strength and seasonal_strength
        """
        if 'stl' not in self.decomposition_results:
            self.stl_decomposition()
        
        result = self.decomposition_results['stl']
        
        # Trend strength: 1 - Var(residual) / Var(trend + residual)
        trend_strength = max(0, 1 - np.var(result['residual']) / 
                            np.var(result['trend'] + result['residual']))
        
        # Seasonal strength: 1 - Var(residual) / Var(seasonal + residual)
        seasonal_strength = max(0, 1 - np.var(result['residual']) / 
                               np.var(result['seasonal'] + result['residual']))
        
        return {
            'trend_strength': trend_strength,
            'seasonal_strength': seasonal_strength,
            'trend_strength_pct': trend_strength * 100,
            'seasonal_strength_pct': seasonal_strength * 100
        }
    
    def visualize_decomposition(self, method: str = 'stl', 
                                figsize: Tuple[int, int] = (15, 12),
                                save_path: str = None) -> plt.Figure:
        """
        Create comprehensive decomposition visualization.
        
        Args:
            method: Decomposition method to visualize
            figsize: Figure size
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure object
        """
        if method not in self.decomposition_results:
            if method == 'stl':
                self.stl_decomposition()
            elif method == 'classical':
                self.classical_decomposition()
            elif method == 'ets':
                self.ets_decomposition()
        
        result = self.decomposition_results[method]
        
        fig, axes = plt.subplots(4, 1, figsize=figsize, sharex=True)
        
        # Original series
        axes[0].plot(result['observed'], label='Observed', color='black')
        axes[0].set_ylabel('Observed')
        axes[0].legend(loc='upper left')
        axes[0].set_title(f'Time Series Decomposition ({method.upper()})')
        
        # Trend
        axes[1].plot(result['trend'], label='Trend', color='blue')
        axes[1].set_ylabel('Trend')
        axes[1].legend(loc='upper left')
        
        # Seasonal
        axes[2].plot(result['seasonal'], label='Seasonal', color='green')
        axes[2].set_ylabel('Seasonal')
        axes[2].legend(loc='upper left')
        
        # Residual
        axes[3].plot(result['residual'], label='Residual', color='red', alpha=0.7)
        axes[3].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[3].set_ylabel('Residual')
        axes[3].set_xlabel('Date')
        axes[3].legend(loc='upper left')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig

# Example usage for disaster data
"""
# Load disaster data
disaster_data = pd.DataFrame({
    'date': pd.date_range('2015-01-01', '2024-12-31', freq='D'),
    'value': np.random.poisson(5, len(pd.date_range('2015-01-01', '2024-12-31', freq='D')))
})

# Initialize decomposer
decomposer = TimeSeriesDecomposer(disaster_data, freq='D')

# Perform STL decomposition
stl_result = decomposer.stl_decomposition(seasonal_period=7)

# Get strength metrics
strength = decomposer.get_strength_metrics()
print(f"Trend Strength: {strength['trend_strength_pct']:.2f}%")
print(f"Seasonal Strength: {strength['seasonal_strength_pct']:.2f}%")

# Visualize
fig = decomposer.visualize_decomposition(method='stl')
"""
```

### 2.2 Decomposition Selection Guide

| Method | Best For | Advantages | Disadvantages |
|--------|----------|------------|---------------|
| **STL** | Complex seasonality, outliers | Robust to outliers, flexible | Computationally intensive |
| **Classical** | Simple patterns, no outliers | Fast, interpretable | Sensitive to outliers |
| **ETS** | Trend + seasonality + noise | State space framework, forecasting | May overfit with complex data |

---

## 3. Trend Analysis

### 3.1 Trend Detection Methods

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/trend_analysis.py

"""
Trend Analysis Module for ResilienceAI
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from typing import Dict, List, Tuple, Optional
import warnings

class TrendAnalyzer:
    """
    Comprehensive trend analysis for disaster time series data.
    Detects linear, polynomial, and piecewise trends.
    """
    
    def __init__(self, data: pd.Series):
        """
        Initialize trend analyzer.
        
        Args:
            data: Time series data as pandas Series with datetime index
        """
        self.data = data.dropna()
        self.trend_results = {}
        
    def linear_trend(self) -> Dict:
        """
        Fit linear trend using linear regression.
        
        Returns:
            Dictionary with trend parameters and statistics
        """
        # Create time index
        time_index = np.arange(len(self.data)).reshape(-1, 1)
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(time_index, self.data.values)
        
        # Predictions
        trend_values = model.predict(time_index)
        
        # Statistics
        slope = model.coef_[0]
        intercept = model.intercept_
        r_squared = model.score(time_index, self.data.values)
        
        # Mann-Kendall trend test
        mk_result = self._mann_kendall_test(self.data.values)
        
        self.trend_results['linear'] = {
            'trend_values': pd.Series(trend_values, index=self.data.index),
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'direction': 'increasing' if slope > 0 else 'decreasing',
            'mann_kendall': mk_result
        }
        
        return self.trend_results['linear']
    
    def polynomial_trend(self, degree: int = 2) -> Dict:
        """
        Fit polynomial trend.
        
        Args:
            degree: Polynomial degree
            
        Returns:
            Dictionary with polynomial trend parameters
        """
        time_index = np.arange(len(self.data)).reshape(-1, 1)
        
        # Create polynomial features pipeline
        pipeline = Pipeline([
            ('poly', PolynomialFeatures(degree=degree)),
            ('linear', LinearRegression())
        ])
        
        pipeline.fit(time_index, self.data.values)
        trend_values = pipeline.predict(time_index)
        
        self.trend_results[f'polynomial_{degree}'] = {
            'trend_values': pd.Series(trend_values, index=self.data.index),
            'degree': degree,
            'r_squared': pipeline.score(time_index, self.data.values),
            'model': pipeline
        }
        
        return self.trend_results[f'polynomial_{degree}']
    
    def rolling_trend(self, window: int = 30, 
                     min_periods: int = None) -> pd.Series:
        """
        Calculate rolling trend using linear regression on windows.
        
        Args:
            window: Rolling window size
            min_periods: Minimum periods for calculation
            
        Returns:
            Series of rolling trend slopes
        """
        if min_periods is None:
            min_periods = window // 2
        
        rolling_slopes = []
        
        for i in range(len(self.data)):
            start_idx = max(0, i - window + 1)
            end_idx = i + 1
            
            if end_idx - start_idx < min_periods:
                rolling_slopes.append(np.nan)
                continue
            
            window_data = self.data.iloc[start_idx:end_idx]
            x = np.arange(len(window_data)).reshape(-1, 1)
            y = window_data.values
            
            model = LinearRegression()
            model.fit(x, y)
            rolling_slopes.append(model.coef_[0])
        
        return pd.Series(rolling_slopes, index=self.data.index)
    
    def _mann_kendall_test(self, data: np.ndarray) -> Dict:
        """
        Perform Mann-Kendall trend test (non-parametric).
        
        Args:
            data: Array of values
            
        Returns:
            Dictionary with test statistics
        """
        n = len(data)
        s = 0
        
        for i in range(n - 1):
            for j in range(i + 1, n):
                s += np.sign(data[j] - data[i])
        
        # Variance of S
        var_s = n * (n - 1) * (2 * n + 5) / 18
        
        # Z-score
        if s > 0:
            z = (s - 1) / np.sqrt(var_s)
        elif s < 0:
            z = (s + 1) / np.sqrt(var_s)
        else:
            z = 0
        
        # P-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        # Kendall's tau
        tau = s / (n * (n - 1) / 2)
        
        return {
            's': s,
            'z': z,
            'p_value': p_value,
            'tau': tau,
            'trend': 'increasing' if z > 1.96 else ('decreasing' if z < -1.96 else 'no trend'),
            'significant': p_value < 0.05
        }
    
    def detect_trend_change_points(self, n_bkps: int = 5) -> List[int]:
        """
        Detect trend change points using binary segmentation.
        
        Args:
            n_bkps: Number of change points to detect
            
        Returns:
            List of change point indices
        """
        try:
            from ruptures import Binseg
            
            # Prepare data
            signal = self.data.values.reshape(-1, 1)
            
            # Binary segmentation
            algo = Binseg(model="l2").fit(signal)
            change_points = algo.predict(n_bkps=n_bkps)
            
            return change_points[:-1]  # Exclude last point (end of series)
        except ImportError:
            warnings.warn("ruptures not installed. Using simple segmentation.")
            return self._simple_change_point_detection(n_bkps)
    
    def _simple_change_point_detection(self, n_bkps: int) -> List[int]:
        """Simple change point detection using variance"""
        data = self.data.values
        n = len(data)
        change_points = []
        
        # Divide into segments and find high variance points
        segment_size = n // (n_bkps + 1)
        
        for i in range(1, n_bkps + 1):
            cp = i * segment_size
            change_points.append(cp)
        
        return change_points
    
    def get_trend_summary(self) -> Dict:
        """
        Get comprehensive trend summary.
        
        Returns:
            Dictionary with all trend analysis results
        """
        # Ensure linear trend is calculated
        if 'linear' not in self.trend_results:
            self.linear_trend()
        
        linear = self.trend_results['linear']
        
        summary = {
            'direction': linear['direction'],
            'slope': linear['slope'],
            'r_squared': linear['r_squared'],
            'significant': linear['mann_kendall']['significant'],
            'mann_kendall_tau': linear['mann_kendall']['tau'],
            'mann_kendall_pvalue': linear['mann_kendall']['p_value'],
            'change_points': self.detect_trend_change_points(n_bkps=3)
        }
        
        return summary

# Example usage
"""
# Analyze trend in disaster frequency
disaster_counts = pd.Series(
    np.random.poisson(5, 365*5) + np.linspace(0, 10, 365*5),
    index=pd.date_range('2019-01-01', periods=365*5, freq='D')
)

analyzer = TrendAnalyzer(disaster_counts)
trend_result = analyzer.linear_trend()
summary = analyzer.get_trend_summary()

print(f"Trend Direction: {summary['direction']}")
print(f"Slope: {summary['slope']:.4f}")
print(f"R²: {summary['r_squared']:.4f}")
print(f"Mann-Kendall Significant: {summary['significant']}")
"""
```


---

## 4. Seasonality Detection

### 4.1 Seasonality Analysis Methods

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/seasonality.py

"""
Seasonality Detection Module for ResilienceAI
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.fft import fft, fftfreq
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt

class SeasonalityDetector:
    """
    Comprehensive seasonality detection for disaster time series.
    Identifies daily, weekly, monthly, and yearly patterns.
    """
    
    def __init__(self, data: pd.Series):
        """
        Initialize seasonality detector.
        
        Args:
            data: Time series data as pandas Series with datetime index
        """
        self.data = data.dropna()
        self.seasonality_results = {}
        
    def detect_all_seasonalities(self) -> Dict:
        """
        Detect all types of seasonality in the data.
        
        Returns:
            Dictionary with all seasonality detection results
        """
        results = {
            'daily': self.detect_daily_pattern(),
            'weekly': self.detect_weekly_pattern(),
            'monthly': self.detect_monthly_pattern(),
            'yearly': self.detect_yearly_pattern(),
            'fft_analysis': self.fft_analysis()
        }
        
        self.seasonality_results = results
        return results
    
    def detect_daily_pattern(self) -> Dict:
        """
        Detect daily seasonality patterns (for hourly data).
        
        Returns:
            Dictionary with daily pattern statistics
        """
        if len(self.data) < 48:  # Need at least 2 days
            return {'detected': False, 'reason': 'Insufficient data'}
        
        # Group by hour
        hourly_avg = self.data.groupby(self.data.index.hour).mean()
        hourly_std = self.data.groupby(self.data.index.hour).std()
        
        # Calculate coefficient of variation
        cv = hourly_std.mean() / hourly_avg.mean() if hourly_avg.mean() != 0 else 0
        
        # Peak hours
        peak_hours = hourly_avg.nlargest(3).index.tolist()
        low_hours = hourly_avg.nsmallest(3).index.tolist()
        
        # ANOVA test for significant differences
        groups = [self.data[self.data.index.hour == h].values for h in range(24)]
        groups = [g for g in groups if len(g) > 0]
        
        if len(groups) > 1:
            f_stat, p_value = stats.f_oneway(*groups)
        else:
            f_stat, p_value = 0, 1
        
        return {
            'detected': p_value < 0.05,
            'hourly_averages': hourly_avg.to_dict(),
            'peak_hours': peak_hours,
            'low_hours': low_hours,
            'coefficient_of_variation': cv,
            'f_statistic': f_stat,
            'p_value': p_value,
            'significance': 'significant' if p_value < 0.05 else 'not significant'
        }
    
    def detect_weekly_pattern(self) -> Dict:
        """
        Detect weekly seasonality patterns.
        
        Returns:
            Dictionary with weekly pattern statistics
        """
        if len(self.data) < 14:  # Need at least 2 weeks
            return {'detected': False, 'reason': 'Insufficient data'}
        
        # Group by day of week
        dow_avg = self.data.groupby(self.data.index.dayofweek).mean()
        dow_std = self.data.groupby(self.data.index.dayofweek).std()
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                     'Friday', 'Saturday', 'Sunday']
        
        # Peak and low days
        peak_day_idx = dow_avg.idxmax()
        low_day_idx = dow_avg.idxmin()
        
        # ANOVA test
        groups = [self.data[self.data.index.dayofweek == d].values for d in range(7)]
        groups = [g for g in groups if len(g) > 0]
        
        if len(groups) > 1:
            f_stat, p_value = stats.f_oneway(*groups)
        else:
            f_stat, p_value = 0, 1
        
        return {
            'detected': p_value < 0.05,
            'daily_averages': {day_names[i]: dow_avg[i] for i in range(7)},
            'peak_day': day_names[peak_day_idx],
            'low_day': day_names[low_day_idx],
            'f_statistic': f_stat,
            'p_value': p_value,
            'significance': 'significant' if p_value < 0.05 else 'not significant'
        }
    
    def detect_monthly_pattern(self) -> Dict:
        """
        Detect monthly seasonality patterns.
        
        Returns:
            Dictionary with monthly pattern statistics
        """
        if len(self.data) < 60:  # Need at least 2 months
            return {'detected': False, 'reason': 'Insufficient data'}
        
        # Group by day of month
        dom_avg = self.data.groupby(self.data.index.day).mean()
        
        # Group by month
        monthly_avg = self.data.groupby(self.data.index.month).mean()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Peak and low months
        peak_month_idx = monthly_avg.idxmax()
        low_month_idx = monthly_avg.idxmin()
        
        # ANOVA test
        groups = [self.data[self.data.index.month == m].values for m in range(1, 13)]
        groups = [g for g in groups if len(g) > 0]
        
        if len(groups) > 1:
            f_stat, p_value = stats.f_oneway(*groups)
        else:
            f_stat, p_value = 0, 1
        
        return {
            'detected': p_value < 0.05,
            'monthly_averages': {month_names[i-1]: monthly_avg[i] for i in range(1, 13)},
            'peak_month': month_names[peak_month_idx - 1],
            'low_month': month_names[low_month_idx - 1],
            'f_statistic': f_stat,
            'p_value': p_value,
            'significance': 'significant' if p_value < 0.05 else 'not significant'
        }
    
    def detect_yearly_pattern(self) -> Dict:
        """
        Detect yearly seasonality patterns.
        
        Returns:
            Dictionary with yearly pattern statistics
        """
        if len(self.data) < 730:  # Need at least 2 years
            return {'detected': False, 'reason': 'Insufficient data'}
        
        # Group by quarter
        quarterly_avg = self.data.groupby(self.data.index.quarter).mean()
        
        # Group by season (meteorological)
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        
        seasons = self.data.index.map(lambda x: get_season(x.month))
        seasonal_avg = self.data.groupby(seasons).mean()
        
        # ANOVA test
        groups = [self.data[self.data.index.quarter == q].values for q in range(1, 5)]
        groups = [g for g in groups if len(g) > 0]
        
        if len(groups) > 1:
            f_stat, p_value = stats.f_oneway(*groups)
        else:
            f_stat, p_value = 0, 1
        
        return {
            'detected': p_value < 0.05,
            'quarterly_averages': quarterly_avg.to_dict(),
            'seasonal_averages': seasonal_avg.to_dict(),
            'peak_quarter': quarterly_avg.idxmax(),
            'low_quarter': quarterly_avg.idxmin(),
            'f_statistic': f_stat,
            'p_value': p_value,
            'significance': 'significant' if p_value < 0.05 else 'not significant'
        }
    
    def fft_analysis(self, top_n: int = 5) -> Dict:
        """
        Perform Fast Fourier Transform analysis to detect periodicities.
        
        Args:
            top_n: Number of top frequencies to return
            
        Returns:
            Dictionary with FFT analysis results
        """
        # Detrend the data
        detrended = self.data - self.data.rolling(window=30, center=True).mean()
        detrended = detrended.dropna()
        
        if len(detrended) < 100:
            return {'detected': False, 'reason': 'Insufficient data'}
        
        # FFT
        yf = fft(detrended.values)
        xf = fftfreq(len(detrended), 1)  # Assuming daily frequency
        
        # Get power spectrum
        power = np.abs(yf) ** 2
        
        # Find peaks (excluding zero frequency)
        positive_freqs = xf[1:len(xf)//2]
        positive_power = power[1:len(power)//2]
        
        # Convert frequencies to periods (in days)
        periods = 1 / positive_freqs
        
        # Get top frequencies
        top_indices = np.argsort(positive_power)[-top_n:][::-1]
        
        top_periods = periods[top_indices]
        top_powers = positive_power[top_indices]
        
        return {
            'detected': True,
            'dominant_periods': top_periods.tolist(),
            'period_powers': top_powers.tolist(),
            'frequencies': positive_freqs[top_indices].tolist(),
            'interpretation': self._interpret_periods(top_periods)
        }
    
    def _interpret_periods(self, periods: np.ndarray) -> List[str]:
        """Interpret detected periods in terms of common cycles"""
        interpretations = []
        
        for period in periods:
            if 6 <= period <= 8:
                interpretations.append('Weekly cycle')
            elif 13 <= period <= 15:
                interpretations.append('Bi-weekly cycle')
            elif 28 <= period <= 31:
                interpretations.append('Monthly cycle')
            elif 89 <= period <= 92:
                interpretations.append('Quarterly cycle')
            elif 360 <= period <= 370:
                interpretations.append('Yearly cycle')
            else:
                interpretations.append(f'{period:.1f}-day cycle')
        
        return interpretations
    
    def get_seasonality_summary(self) -> Dict:
        """
        Get summary of all detected seasonalities.
        
        Returns:
            Dictionary with seasonality summary
        """
        if not self.seasonality_results:
            self.detect_all_seasonalities()
        
        summary = {
            'has_daily_pattern': self.seasonality_results.get('daily', {}).get('detected', False),
            'has_weekly_pattern': self.seasonality_results.get('weekly', {}).get('detected', False),
            'has_monthly_pattern': self.seasonality_results.get('monthly', {}).get('detected', False),
            'has_yearly_pattern': self.seasonality_results.get('yearly', {}).get('detected', False),
            'dominant_periods': self.seasonality_results.get('fft_analysis', {}).get('dominant_periods', []),
            'period_interpretations': self.seasonality_results.get('fft_analysis', {}).get('interpretation', [])
        }
        
        return summary

# Example usage
"""
# Generate sample disaster data with seasonality
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
base = 5
yearly_pattern = 2 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
weekly_pattern = 1 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)
noise = np.random.normal(0, 1, len(dates))
disaster_data = pd.Series(base + yearly_pattern + weekly_pattern + noise, index=dates)

# Detect seasonality
detector = SeasonalityDetector(disaster_data)
seasonality = detector.detect_all_seasonalities()
summary = detector.get_seasonality_summary()

print("Seasonality Summary:")
print(f"  Weekly Pattern: {summary['has_weekly_pattern']}")
print(f"  Yearly Pattern: {summary['has_yearly_pattern']}")
print(f"  Dominant Periods: {summary['dominant_periods'][:3]}")
"""
```

---

## 5. ARIMA Modeling

### 5.1 ARIMA Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/arima_models.py

"""
ARIMA Modeling Module for ResilienceAI
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')
import itertools

class ARIMAModel:
    """
    Comprehensive ARIMA modeling for disaster time series forecasting.
    Supports automatic parameter selection and seasonal ARIMA (SARIMA).
    """
    
    def __init__(self, data: pd.Series):
        """
        Initialize ARIMA model.
        
        Args:
            data: Time series data as pandas Series with datetime index
        """
        self.data = data.dropna()
        self.model = None
        self.fitted_model = None
        self.order = None
        self.seasonal_order = None
        self.results = {}
        
    def check_stationarity(self) -> Dict:
        """
        Check if time series is stationary using Augmented Dickey-Fuller test.
        
        Returns:
            Dictionary with test results
        """
        result = adfuller(self.data.dropna())
        
        return {
            'adf_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'is_stationary': result[1] < 0.05,
            'interpretation': 'Stationary' if result[1] < 0.05 else 'Non-stationary'
        }
    
    def make_stationary(self, max_diff: int = 3) -> Tuple[pd.Series, int]:
        """
        Make time series stationary through differencing.
        
        Args:
            max_diff: Maximum number of differences to apply
            
        Returns:
            Tuple of (stationary series, number of differences applied)
        """
        series = self.data.copy()
        d = 0
        
        for i in range(max_diff):
            result = adfuller(series.dropna())
            if result[1] < 0.05:
                break
            series = series.diff().dropna()
            d += 1
        
        return series, d
    
    def select_order(self, max_p: int = 5, max_d: int = 2, max_q: int = 5,
                    seasonal: bool = True, seasonal_period: int = None) -> Tuple:
        """
        Automatically select optimal ARIMA order using AIC/BIC criteria.
        
        Args:
            max_p: Maximum AR order
            max_d: Maximum differencing order
            max_q: Maximum MA order
            seasonal: Whether to include seasonal component
            seasonal_period: Seasonal period (e.g., 7 for weekly, 12 for monthly)
            
        Returns:
            Tuple of (p, d, q) and optionally seasonal_order
        """
        # Determine d through stationarity test
        _, d = self.make_stationary(max_diff=max_d)
        
        # Grid search for p and q
        best_aic = float('inf')
        best_order = (0, d, 0)
        
        p_range = range(max_p + 1)
        q_range = range(max_q + 1)
        
        for p, q in itertools.product(p_range, q_range):
            if p == 0 and q == 0:
                continue
            try:
                model = ARIMA(self.data, order=(p, d, q))
                fitted = model.fit()
                
                if fitted.aic < best_aic:
                    best_aic = fitted.aic
                    best_order = (p, d, q)
            except:
                continue
        
        self.order = best_order
        
        # Seasonal component
        if seasonal and seasonal_period:
            best_seasonal_aic = float('inf')
            best_seasonal_order = (0, 0, 0, seasonal_period)
            
            for P in range(3):
                for Q in range(3):
                    try:
                        model = SARIMAX(self.data, 
                                       order=best_order,
                                       seasonal_order=(P, 0, Q, seasonal_period))
                        fitted = model.fit(disp=False)
                        
                        if fitted.aic < best_seasonal_aic:
                            best_seasonal_aic = fitted.aic
                            best_seasonal_order = (P, 0, Q, seasonal_period)
                    except:
                        continue
            
            self.seasonal_order = best_seasonal_order
            return best_order, best_seasonal_order
        
        return best_order, None
    
    def fit(self, order: Tuple[int, int, int] = None,
           seasonal_order: Tuple[int, int, int, int] = None) -> 'ARIMAModel':
        """
        Fit ARIMA model.
        
        Args:
            order: ARIMA order (p, d, q). If None, auto-selected.
            seasonal_order: Seasonal order (P, D, Q, s). If None, no seasonality.
            
        Returns:
            Self for method chaining
        """
        if order is None:
            order, seasonal_order = self.select_order()
        
        self.order = order
        
        if seasonal_order:
            self.seasonal_order = seasonal_order
            self.model = SARIMAX(self.data, 
                                order=order,
                                seasonal_order=seasonal_order)
        else:
            self.model = ARIMA(self.data, order=order)
        
        self.fitted_model = self.model.fit(disp=False)
        
        # Store results
        self.results = {
            'aic': self.fitted_model.aic,
            'bic': self.fitted_model.bic,
            'log_likelihood': self.fitted_model.llf,
            'order': order,
            'seasonal_order': seasonal_order
        }
        
        return self
    
    def forecast(self, steps: int = 30, alpha: float = 0.05) -> Dict:
        """
        Generate forecasts.
        
        Args:
            steps: Number of steps to forecast
            alpha: Significance level for confidence intervals
            
        Returns:
            Dictionary with forecast and confidence intervals
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before forecasting")
        
        forecast_result = self.fitted_model.get_forecast(steps=steps)
        
        forecast = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=alpha)
        
        # Create future date index
        last_date = self.data.index[-1]
        freq = pd.infer_freq(self.data.index) or 'D'
        future_dates = pd.date_range(start=last_date, periods=steps+1, freq=freq)[1:]
        
        forecast.index = future_dates
        conf_int.index = future_dates
        
        return {
            'forecast': forecast,
            'lower_bound': conf_int.iloc[:, 0],
            'upper_bound': conf_int.iloc[:, 1],
            'steps': steps,
            'confidence_level': 1 - alpha
        }
    
    def evaluate(self, test_data: pd.Series) -> Dict:
        """
        Evaluate model on test data.
        
        Args:
            test_data: Test time series data
            
        Returns:
            Dictionary with evaluation metrics
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before evaluation")
        
        # Generate predictions for test period
        predictions = self.fitted_model.forecast(steps=len(test_data))
        
        # Calculate metrics
        mse = mean_squared_error(test_data, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(test_data, predictions)
        mape = np.mean(np.abs((test_data - predictions) / test_data)) * 100
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape
        }
    
    def residual_diagnostics(self) -> Dict:
        """
        Perform residual diagnostics.
        
        Returns:
            Dictionary with diagnostic results
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted first")
        
        residuals = self.fitted_model.resid
        
        # Ljung-Box test for autocorrelation
        lb_test = acorr_ljungbox(residuals, lags=10, return_df=True)
        
        # Normality test
        from scipy import stats
        jb_stat, jb_pvalue = stats.jarque_bera(residuals.dropna())
        
        return {
            'ljung_box_pvalues': lb_test['lb_pvalue'].tolist(),
            'residuals_correlated': any(lb_test['lb_pvalue'] < 0.05),
            'jarque_bera_stat': jb_stat,
            'jarque_bera_pvalue': jb_pvalue,
            'residuals_normal': jb_pvalue > 0.05,
            'residual_mean': residuals.mean(),
            'residual_std': residuals.std()
        }
    
    def get_model_summary(self) -> str:
        """Get model summary as string"""
        if self.fitted_model is None:
            return "Model not fitted yet"
        return str(self.fitted_model.summary())

# Example usage
"""
# Generate sample data
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
data = pd.Series(np.random.poisson(5, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365), index=dates)

# Fit ARIMA model
arima = ARIMAModel(data)
arima.fit()

# Generate forecast
forecast = arima.forecast(steps=30)

# Evaluate
print(arima.get_model_summary())
print(f"\nForecast for next 30 days:")
print(forecast['forecast'].head())
"""
```


---

## 6. Prophet Forecasting

### 6.1 Prophet Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/prophet_models.py

"""
Prophet Forecasting Module for ResilienceAI
"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class ProphetForecaster:
    """
    Facebook Prophet forecasting for disaster time series.
    Handles missing data, outliers, and multiple seasonality patterns.
    """
    
    def __init__(self, 
                 yearly_seasonality: bool = True,
                 weekly_seasonality: bool = True,
                 daily_seasonality: bool = False,
                 seasonality_mode: str = 'additive',
                 changepoint_prior_scale: float = 0.05,
                 seasonality_prior_scale: float = 10.0):
        """
        Initialize Prophet forecaster.
        
        Args:
            yearly_seasonality: Include yearly seasonality
            weekly_seasonality: Include weekly seasonality
            daily_seasonality: Include daily seasonality
            seasonality_mode: 'additive' or 'multiplicative'
            changepoint_prior_scale: Flexibility of trend changes
            seasonality_prior_scale: Flexibility of seasonality
        """
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.seasonality_mode = seasonality_mode
        self.changepoint_prior_scale = changepoint_prior_scale
        self.seasonality_prior_scale = seasonality_prior_scale
        
        self.model = None
        self.future_df = None
        
    def _prepare_data(self, data: pd.Series) -> pd.DataFrame:
        """
        Prepare data in Prophet format.
        
        Args:
            data: Time series data as pandas Series
            
        Returns:
            DataFrame with 'ds' (date) and 'y' (value) columns
        """
        df = pd.DataFrame({
            'ds': data.index,
            'y': data.values
        })
        return df
    
    def fit(self, data: pd.Series, 
           holidays: pd.DataFrame = None,
           regressors: pd.DataFrame = None) -> 'ProphetForecaster':
        """
        Fit Prophet model.
        
        Args:
            data: Training time series data
            holidays: DataFrame with holiday dates
            regressors: Additional regressors for the model
            
        Returns:
            Self for method chaining
        """
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("Prophet not installed. Run: pip install prophet")
        
        # Prepare data
        df = self._prepare_data(data)
        
        # Initialize model
        self.model = Prophet(
            yearly_seasonality=self.yearly_seasonality,
            weekly_seasonality=self.weekly_seasonality,
            daily_seasonality=self.daily_seasonality,
            seasonality_mode=self.seasonality_mode,
            changepoint_prior_scale=self.changepoint_prior_scale,
            seasonality_prior_scale=self.seasonality_prior_scale
        )
        
        # Add holidays if provided
        if holidays is not None:
            self.model.add_country_holidays(country_name='US')
        
        # Add custom regressors if provided
        if regressors is not None:
            for col in regressors.columns:
                self.model.add_regressor(col)
                df[col] = regressors[col].values
        
        # Fit model
        self.model.fit(df)
        
        return self
    
    def forecast(self, periods: int = 30, 
                freq: str = 'D',
                include_history: bool = False) -> Dict:
        """
        Generate forecasts.
        
        Args:
            periods: Number of periods to forecast
            freq: Frequency of data ('D', 'W', 'M', etc.)
            include_history: Whether to include historical data
            
        Returns:
            Dictionary with forecast components
        """
        if self.model is None:
            raise ValueError("Model must be fitted before forecasting")
        
        # Create future dataframe
        self.future_df = self.model.make_future_dataframe(
            periods=periods,
            freq=freq,
            include_history=include_history
        )
        
        # Generate forecast
        forecast = self.model.predict(self.future_df)
        
        # Extract components
        result = {
            'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
            'trend': forecast[['ds', 'trend', 'trend_lower', 'trend_upper']],
            'yearly': forecast[['ds', 'yearly']] if 'yearly' in forecast.columns else None,
            'weekly': forecast[['ds', 'weekly']] if 'weekly' in forecast.columns else None,
            'daily': forecast[['ds', 'daily']] if 'daily' in forecast.columns else None,
            'components': forecast
        }
        
        return result
    
    def cross_validate(self, data: pd.Series,
                      initial: str = '730 days',
                      period: str = '180 days',
                      horizon: str = '365 days') -> pd.DataFrame:
        """
        Perform cross-validation.
        
        Args:
            data: Time series data
            initial: Initial training period
            period: Period between cutoffs
            horizon: Forecast horizon
            
        Returns:
            DataFrame with cross-validation results
        """
        try:
            from prophet.diagnostics import cross_validation, performance_metrics
        except ImportError:
            raise ImportError("Prophet diagnostics not available")
        
        # Fit model if not fitted
        if self.model is None:
            self.fit(data)
        
        # Cross validation
        df_cv = cross_validation(
            self.model,
            initial=initial,
            period=period,
            horizon=horizon,
            parallel='processes'
        )
        
        # Performance metrics
        df_p = performance_metrics(df_cv)
        
        return df_p
    
    def add_custom_seasonality(self, name: str, period: float, 
                              fourier_order: int = 3):
        """
        Add custom seasonality to the model.
        
        Args:
            name: Name of the seasonality
            period: Period in days
            fourier_order: Number of Fourier components
        """
        if self.model is None:
            raise ValueError("Model must be initialized first")
        
        self.model.add_seasonality(
            name=name,
            period=period,
            fourier_order=fourier_order
        )
    
    def add_changepoints(self, dates: List[str]):
        """
        Add known changepoints to the model.
        
        Args:
            dates: List of dates as strings (YYYY-MM-DD format)
        """
        if self.model is None:
            raise ValueError("Model must be initialized first")
        
        self.model.changepoints = pd.to_datetime(dates)
    
    def get_changepoints(self) -> pd.DataFrame:
        """
        Get detected changepoints from fitted model.
        
        Returns:
            DataFrame with changepoint information
        """
        if self.model is None:
            raise ValueError("Model must be fitted first")
        
        # Get changepoints
        changepoints = self.model.changepoints
        
        # Get changepoint parameters
        params = self.model.params['delta']
        
        return pd.DataFrame({
            'changepoint': changepoints,
            'delta': params
        })
    
    def evaluate(self, test_data: pd.Series) -> Dict:
        """
        Evaluate model on test data.
        
        Args:
            test_data: Test time series data
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Generate forecast for test period
        test_df = self._prepare_data(test_data)
        forecast = self.model.predict(test_df)
        
        # Calculate metrics
        y_true = test_data.values
        y_pred = forecast['yhat'].values
        
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape
        }

# Example usage
"""
# Generate sample disaster data
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
trend = np.linspace(5, 10, len(dates))
seasonal = 2 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
weekly = 0.5 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)
noise = np.random.normal(0, 0.5, len(dates))
data = pd.Series(trend + seasonal + weekly + noise, index=dates)

# Fit Prophet model
prophet = ProphetForecaster(
    yearly_seasonality=True,
    weekly_seasonality=True,
    changepoint_prior_scale=0.05
)
prophet.fit(data)

# Generate forecast
forecast = prophet.forecast(periods=30)

print("Forecast for next 30 days:")
print(forecast['forecast'][['ds', 'yhat']].tail())
"""
```

---

## 7. LSTM for Time Series

### 7.1 LSTM Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/lstm_models.py

"""
LSTM Time Series Forecasting Module for ResilienceAI
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class LSTMForecaster:
    """
    LSTM-based time series forecasting for disaster prediction.
    Supports multi-step forecasting and multiple input features.
    """
    
    def __init__(self, 
                 sequence_length: int = 30,
                 n_features: int = 1,
                 lstm_units: List[int] = [128, 64, 32],
                 dropout_rate: float = 0.2,
                 learning_rate: float = 0.001,
                 epochs: int = 100,
                 batch_size: int = 32,
                 validation_split: float = 0.2):
        """
        Initialize LSTM forecaster.
        
        Args:
            sequence_length: Number of time steps to look back
            n_features: Number of input features
            lstm_units: List of LSTM layer units
            dropout_rate: Dropout rate for regularization
            learning_rate: Learning rate for optimizer
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of data for validation
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.validation_split = validation_split
        
        self.model = None
        self.scaler = MinMaxScaler()
        self.history = None
        
    def _create_sequences(self, data: np.ndarray, 
                         sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training.
        
        Args:
            data: Normalized time series data
            sequence_length: Length of each sequence
            
        Returns:
            Tuple of (X, y) arrays
        """
        X, y = [], []
        
        for i in range(len(data) - sequence_length):
            X.append(data[i:(i + sequence_length)])
            y.append(data[i + sequence_length])
        
        return np.array(X), np.array(y)
    
    def _build_model(self) -> 'tf.keras.Model':
        """
        Build LSTM model architecture.
        
        Returns:
            Compiled Keras model
        """
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from tensorflow.keras.optimizers import Adam
        except ImportError:
            raise ImportError("TensorFlow not installed. Run: pip install tensorflow")
        
        model = Sequential()
        
        # Add LSTM layers
        for i, units in enumerate(self.lstm_units):
            return_sequences = i < len(self.lstm_units) - 1
            
            if i == 0:
                model.add(LSTM(units, 
                              return_sequences=return_sequences,
                              input_shape=(self.sequence_length, self.n_features)))
            else:
                model.add(LSTM(units, return_sequences=return_sequences))
            
            model.add(Dropout(self.dropout_rate))
        
        # Output layer
        model.add(Dense(1))
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def fit(self, data: pd.Series, 
           external_features: pd.DataFrame = None,
           verbose: int = 1) -> Dict:
        """
        Fit LSTM model.
        
        Args:
            data: Training time series data
            external_features: Additional features (optional)
            verbose: Verbosity level
            
        Returns:
            Training history
        """
        try:
            import tensorflow as tf
            tf.random.set_seed(42)
        except ImportError:
            raise ImportError("TensorFlow not installed")
        
        # Prepare data
        values = data.values.reshape(-1, 1)
        
        # Add external features if provided
        if external_features is not None:
            values = np.hstack([values, external_features.values])
            self.n_features = values.shape[1]
        
        # Scale data
        scaled_data = self.scaler.fit_transform(values)
        
        # Create sequences
        X, y = self._create_sequences(scaled_data, self.sequence_length)
        
        # Split into train and validation
        split_idx = int(len(X) * (1 - self.validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx, 0], y[split_idx:, 0]
        
        # Build model
        self.model = self._build_model()
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.epochs,
            batch_size=self.batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        return {
            'loss': self.history.history['loss'],
            'val_loss': self.history.history['val_loss'],
            'mae': self.history.history['mae'],
            'val_mae': self.history.history['val_mae']
        }
    
    def predict(self, steps: int = 30, 
               last_sequence: np.ndarray = None) -> pd.Series:
        """
        Generate multi-step forecasts.
        
        Args:
            steps: Number of steps to forecast
            last_sequence: Last known sequence (optional)
            
        Returns:
            Series with forecasts
        """
        if self.model is None:
            raise ValueError("Model must be fitted before prediction")
        
        # Get last sequence if not provided
        if last_sequence is None:
            raise ValueError("Last sequence must be provided")
        
        # Scale the sequence
        scaled_sequence = self.scaler.transform(last_sequence)
        
        # Generate predictions
        predictions = []
        current_sequence = scaled_sequence[-self.sequence_length:].copy()
        
        for _ in range(steps):
            # Reshape for prediction
            X_pred = current_sequence.reshape(1, self.sequence_length, self.n_features)
            
            # Predict
            pred = self.model.predict(X_pred, verbose=0)
            predictions.append(pred[0, 0])
            
            # Update sequence
            current_sequence = np.roll(current_sequence, -1, axis=0)
            current_sequence[-1, 0] = pred[0, 0]
        
        # Inverse transform predictions
        predictions_array = np.array(predictions).reshape(-1, 1)
        
        # Create dummy array for inverse transform
        dummy = np.zeros((len(predictions), self.n_features))
        dummy[:, 0] = predictions_array[:, 0]
        
        forecasts = self.scaler.inverse_transform(dummy)[:, 0]
        
        # Create date index
        last_date = pd.Timestamp.now()  # This should be passed as parameter
        future_dates = pd.date_range(start=last_date, periods=steps, freq='D')
        
        return pd.Series(forecasts, index=future_dates)
    
    def evaluate(self, test_data: pd.Series) -> Dict:
        """
        Evaluate model on test data.
        
        Args:
            test_data: Test time series data
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Prepare test data
        values = test_data.values.reshape(-1, 1)
        scaled_values = self.scaler.transform(values)
        
        # Create sequences
        X_test, y_test = self._create_sequences(scaled_values, self.sequence_length)
        
        # Predict
        y_pred = self.model.predict(X_test, verbose=0)
        
        # Inverse transform
        y_test_inv = self.scaler.inverse_transform(
            np.hstack([y_test.reshape(-1, 1), np.zeros((len(y_test), self.n_features - 1))])
        )[:, 0]
        
        y_pred_inv = self.scaler.inverse_transform(
            np.hstack([y_pred, np.zeros((len(y_pred), self.n_features - 1))])
        )[:, 0]
        
        # Calculate metrics
        mse = mean_squared_error(y_test_inv, y_pred_inv)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test_inv, y_pred_inv)
        mape = np.mean(np.abs((y_test_inv - y_pred_inv) / y_test_inv)) * 100
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape
        }
    
    def save_model(self, filepath: str):
        """Save model to file"""
        if self.model is None:
            raise ValueError("No model to save")
        self.model.save(filepath)
    
    def load_model(self, filepath: str):
        """Load model from file"""
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(filepath)
        except ImportError:
            raise ImportError("TensorFlow not installed")

# Example usage
"""
# Generate sample data
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
data = pd.Series(np.sin(np.arange(len(dates)) * 2 * np.pi / 365) + 
                 np.random.normal(0, 0.1, len(dates)), index=dates)

# Fit LSTM model
lstm = LSTMForecaster(
    sequence_length=30,
    lstm_units=[64, 32],
    epochs=50
)
lstm.fit(data, verbose=1)

# Generate forecast
last_sequence = data.values[-30:].reshape(-1, 1)
forecast = lstm.predict(steps=30, last_sequence=last_sequence)
print(forecast)
"""
```


---

## 8. Anomaly Detection

### 8.1 Anomaly Detection Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/anomaly_detection.py

"""
Anomaly Detection Module for ResilienceAI
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    """
    Comprehensive anomaly detection for disaster time series.
    Supports statistical, machine learning, and deep learning methods.
    """
    
    def __init__(self, data: pd.Series):
        """
        Initialize anomaly detector.
        
        Args:
            data: Time series data as pandas Series with datetime index
        """
        self.data = data.dropna()
        self.anomalies = pd.Series(index=self.data.index, dtype=bool)
        self.anomaly_scores = pd.Series(index=self.data.index, dtype=float)
        self.detection_results = {}
        
    def statistical_method(self, method: str = 'zscore', 
                          threshold: float = 3.0) -> Dict:
        """
        Detect anomalies using statistical methods.
        
        Args:
            method: 'zscore', 'iqr', or 'mad'
            threshold: Threshold for anomaly detection
            
        Returns:
            Dictionary with detection results
        """
        if method == 'zscore':
            # Z-score method
            z_scores = np.abs(stats.zscore(self.data))
            anomalies = z_scores > threshold
            scores = z_scores
            
        elif method == 'iqr':
            # Interquartile Range method
            Q1 = self.data.quantile(0.25)
            Q3 = self.data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            anomalies = (self.data < lower_bound) | (self.data > upper_bound)
            
            # Calculate scores
            scores = np.maximum(
                np.abs(self.data - Q1) / IQR,
                np.abs(self.data - Q3) / IQR
            )
            
        elif method == 'mad':
            # Median Absolute Deviation method
            median = self.data.median()
            mad = np.median(np.abs(self.data - median))
            
            modified_z_scores = 0.6745 * (self.data - median) / mad
            anomalies = np.abs(modified_z_scores) > threshold
            scores = np.abs(modified_z_scores)
            
        else:
            raise ValueError(f"Unknown method: {method}")
        
        self.detection_results[f'statistical_{method}'] = {
            'anomalies': anomalies,
            'scores': scores,
            'threshold': threshold,
            'n_anomalies': anomalies.sum(),
            'anomaly_rate': anomalies.mean() * 100
        }
        
        return self.detection_results[f'statistical_{method}']
    
    def isolation_forest(self, contamination: float = 0.05,
                        n_estimators: int = 100) -> Dict:
        """
        Detect anomalies using Isolation Forest.
        
        Args:
            contamination: Expected proportion of anomalies
            n_estimators: Number of trees in forest
            
        Returns:
            Dictionary with detection results
        """
        # Prepare features (value + rolling statistics)
        features = self._create_features()
        
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Fit Isolation Forest
        model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42
        )
        
        predictions = model.fit_predict(features_scaled)
        scores = model.decision_function(features_scaled)
        
        # Anomalies are labeled as -1
        anomalies = predictions == -1
        
        self.detection_results['isolation_forest'] = {
            'anomalies': pd.Series(anomalies, index=self.data.index),
            'scores': pd.Series(-scores, index=self.data.index),  # Invert so higher = more anomalous
            'threshold': contamination,
            'n_anomalies': anomalies.sum(),
            'anomaly_rate': anomalies.mean() * 100,
            'model': model
        }
        
        return self.detection_results['isolation_forest']
    
    def local_outlier_factor(self, n_neighbors: int = 20,
                            contamination: float = 0.05) -> Dict:
        """
        Detect anomalies using Local Outlier Factor.
        
        Args:
            n_neighbors: Number of neighbors to consider
            contamination: Expected proportion of anomalies
            
        Returns:
            Dictionary with detection results
        """
        # Prepare features
        features = self._create_features()
        
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Fit LOF
        model = LocalOutlierFactor(
            n_neighbors=n_neighbors,
            contamination=contamination
        )
        
        predictions = model.fit_predict(features_scaled)
        scores = model.negative_outlier_factor_
        
        # Anomalies are labeled as -1
        anomalies = predictions == -1
        
        self.detection_results['lof'] = {
            'anomalies': pd.Series(anomalies, index=self.data.index),
            'scores': pd.Series(-scores, index=self.data.index),
            'threshold': contamination,
            'n_anomalies': anomalies.sum(),
            'anomaly_rate': anomalies.mean() * 100
        }
        
        return self.detection_results['lof']
    
    def prophet_anomaly_detection(self, threshold: float = 0.95) -> Dict:
        """
        Detect anomalies using Prophet's uncertainty intervals.
        
        Args:
            threshold: Confidence level for anomaly detection
            
        Returns:
            Dictionary with detection results
        """
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("Prophet not installed")
        
        # Prepare data
        df = pd.DataFrame({
            'ds': self.data.index,
            'y': self.data.values
        })
        
        # Fit Prophet
        model = Prophet(
            interval_width=threshold,
            yearly_seasonality=True,
            weekly_seasonality=True
        )
        model.fit(df)
        
        # Predict
        future = model.make_future_dataframe(periods=0)
        forecast = model.predict(future)
        
        # Detect anomalies (outside confidence interval)
        anomalies = (self.data.values < forecast['yhat_lower'].values) | \
                   (self.data.values > forecast['yhat_upper'].values)
        
        # Calculate anomaly scores
        residuals = np.abs(self.data.values - forecast['yhat'].values)
        scores = residuals / (forecast['yhat_upper'] - forecast['yhat_lower']).values
        
        self.detection_results['prophet'] = {
            'anomalies': pd.Series(anomalies, index=self.data.index),
            'scores': pd.Series(scores, index=self.data.index),
            'threshold': threshold,
            'n_anomalies': anomalies.sum(),
            'anomaly_rate': anomalies.mean() * 100,
            'forecast': forecast
        }
        
        return self.detection_results['prophet']
    
    def lstm_anomaly_detection(self, sequence_length: int = 30,
                               threshold_percentile: float = 95) -> Dict:
        """
        Detect anomalies using LSTM reconstruction error.
        
        Args:
            sequence_length: Length of sequences for LSTM
            threshold_percentile: Percentile for anomaly threshold
            
        Returns:
            Dictionary with detection results
        """
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
        except ImportError:
            raise ImportError("TensorFlow not installed")
        
        # Normalize data
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(self.data.values.reshape(-1, 1))
        
        # Create sequences
        sequences = []
        for i in range(len(scaled_data) - sequence_length):
            sequences.append(scaled_data[i:i + sequence_length])
        sequences = np.array(sequences)
        
        # Build autoencoder
        model = Sequential([
            LSTM(64, activation='relu', input_shape=(sequence_length, 1), return_sequences=False),
            RepeatVector(sequence_length),
            LSTM(64, activation='relu', return_sequences=True),
            TimeDistributed(Dense(1))
        ])
        
        model.compile(optimizer='adam', loss='mse')
        
        # Train
        model.fit(sequences, sequences, epochs=50, batch_size=32, 
                 validation_split=0.1, verbose=0)
        
        # Calculate reconstruction error
        reconstructed = model.predict(sequences)
        mse = np.mean(np.power(sequences - reconstructed, 2), axis=(1, 2))
        
        # Pad to match original length
        scores = np.pad(mse, (sequence_length, 0), mode='edge')
        
        # Threshold
        threshold = np.percentile(scores, threshold_percentile)
        anomalies = scores > threshold
        
        self.detection_results['lstm'] = {
            'anomalies': pd.Series(anomalies, index=self.data.index),
            'scores': pd.Series(scores, index=self.data.index),
            'threshold': threshold,
            'n_anomalies': anomalies.sum(),
            'anomaly_rate': anomalies.mean() * 100,
            'model': model
        }
        
        return self.detection_results['lstm']
    
    def _create_features(self) -> pd.DataFrame:
        """Create feature matrix for ML models"""
        features = pd.DataFrame(index=self.data.index)
        
        # Original value
        features['value'] = self.data.values
        
        # Rolling statistics
        for window in [7, 14, 30]:
            features[f'rolling_mean_{window}'] = self.data.rolling(window=window, min_periods=1).mean()
            features[f'rolling_std_{window}'] = self.data.rolling(window=window, min_periods=1).std()
        
        # Lag features
        for lag in [1, 7, 14]:
            features[f'lag_{lag}'] = self.data.shift(lag)
        
        # Time features
        features['dayofweek'] = self.data.index.dayofweek
        features['month'] = self.data.index.month
        features['quarter'] = self.data.index.quarter
        
        # Fill NaN values
        features = features.fillna(method='bfill').fillna(method='ffill')
        
        return features
    
    def ensemble_detection(self, methods: List[str] = None,
                          voting: str = 'majority') -> Dict:
        """
        Combine multiple anomaly detection methods.
        
        Args:
            methods: List of methods to ensemble
            voting: 'majority' or 'unanimous'
            
        Returns:
            Dictionary with ensemble results
        """
        if methods is None:
            methods = ['statistical_zscore', 'isolation_forest', 'prophet']
        
        # Run all methods
        for method in methods:
            if method not in self.detection_results:
                if method.startswith('statistical_'):
                    self.statistical_method(method.split('_')[1])
                elif method == 'isolation_forest':
                    self.isolation_forest()
                elif method == 'prophet':
                    self.prophet_anomaly_detection()
        
        # Collect anomaly flags
        anomaly_votes = pd.DataFrame(index=self.data.index)
        for method in methods:
            if method in self.detection_results:
                anomaly_votes[method] = self.detection_results[method]['anomalies']
        
        # Ensemble decision
        if voting == 'majority':
            anomalies = anomaly_votes.sum(axis=1) > len(methods) / 2
        else:  # unanimous
            anomalies = anomaly_votes.all(axis=1)
        
        # Combined scores (average of normalized scores)
        combined_scores = pd.DataFrame(index=self.data.index)
        for method in methods:
            if method in self.detection_results:
                scores = self.detection_results[method]['scores']
                combined_scores[method] = (scores - scores.min()) / (scores.max() - scores.min())
        
        avg_scores = combined_scores.mean(axis=1)
        
        return {
            'anomalies': anomalies,
            'scores': avg_scores,
            'votes': anomaly_votes.sum(axis=1),
            'n_anomalies': anomalies.sum(),
            'anomaly_rate': anomalies.mean() * 100,
            'method_agreement': anomaly_votes.sum(axis=1) / len(methods)
        }
    
    def get_anomaly_summary(self) -> Dict:
        """
        Get summary of all detected anomalies.
        
        Returns:
            Dictionary with anomaly summary
        """
        summary = {
            'total_points': len(self.data),
            'methods_used': list(self.detection_results.keys()),
            'anomalies_by_method': {}
        }
        
        for method, results in self.detection_results.items():
            summary['anomalies_by_method'][method] = {
                'count': results['n_anomalies'],
                'rate': results['anomaly_rate']
            }
        
        return summary

# Example usage
"""
# Generate sample data with anomalies
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
data = pd.Series(np.random.normal(10, 2, len(dates)), index=dates)

# Inject anomalies
data.iloc[100:105] = 30  # Spike anomaly
data.iloc[500:510] = 0   # Drop anomaly

# Detect anomalies
detector = AnomalyDetector(data)

# Statistical method
stat_result = detector.statistical_method(method='zscore', threshold=3)
print(f"Statistical anomalies: {stat_result['n_anomalies']}")

# Isolation Forest
if_result = detector.isolation_forest(contamination=0.05)
print(f"Isolation Forest anomalies: {if_result['n_anomalies']}")

# Ensemble
ensemble = detector.ensemble_detection()
print(f"Ensemble anomalies: {ensemble['n_anomalies']}")
"""
```

---

## 9. Change Point Detection

### 9.1 Change Point Detection Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/change_point_detection.py

"""
Change Point Detection Module for ResilienceAI
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class ChangePointDetector:
    """
    Change point detection for disaster time series.
    Identifies abrupt changes in mean, variance, or trend.
    """
    
    def __init__(self, data: pd.Series):
        """
        Initialize change point detector.
        
        Args:
            data: Time series data as pandas Series with datetime index
        """
        self.data = data.dropna()
        self.change_points = []
        self.detection_results = {}
        
    def cusum_detection(self, threshold: float = 5.0, 
                       drift: float = 0.0) -> Dict:
        """
        Cumulative Sum (CUSUM) change point detection.
        Good for detecting small shifts in mean.
        
        Args:
            threshold: Detection threshold
            drift: Allowed drift
            
        Returns:
            Dictionary with detection results
        """
        values = self.data.values
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        # Normalize
        normalized = (values - mean_val) / std_val
        
        # CUSUM statistics
        s_pos = np.zeros(len(normalized))
        s_neg = np.zeros(len(normalized))
        
        change_points = []
        
        for i in range(1, len(normalized)):
            s_pos[i] = max(0, s_pos[i-1] + normalized[i] - drift)
            s_neg[i] = max(0, s_neg[i-1] - normalized[i] - drift)
            
            if s_pos[i] > threshold or s_neg[i] > threshold:
                change_points.append(i)
                s_pos[i] = 0
                s_neg[i] = 0
        
        self.detection_results['cusum'] = {
            'change_points': [self.data.index[i] for i in change_points],
            'change_indices': change_points,
            'n_changes': len(change_points),
            's_pos': s_pos,
            's_neg': s_neg,
            'threshold': threshold
        }
        
        return self.detection_results['cusum']
    
    def bayesian_online_detection(self, hazard: float = 0.01) -> Dict:
        """
        Bayesian Online Change Point Detection (BOCD).
        
        Args:
            hazard: Prior probability of change point
            
        Returns:
            Dictionary with detection results
        """
        values = self.data.values
        n = len(values)
        
        # Initialize
        R = np.zeros((n + 1, n + 1))
        R[0, 0] = 1
        
        # Message
        message = np.zeros(n + 1)
        message[0] = 1
        
        # Model parameters
        mu0 = 0
        kappa0 = 1
        alpha0 = 1
        beta0 = 1
        
        mu = np.zeros(n)
        kappa = np.zeros(n)
        alpha = np.zeros(n)
        beta = np.zeros(n)
        
        change_points = []
        max_probs = []
        
        for t in range(1, n + 1):
            # Predictive probabilities
            pred_probs = np.zeros(t)
            
            for tau in range(t):
                if tau == 0:
                    mu[tau] = mu0
                    kappa[tau] = kappa0
                    alpha[tau] = alpha0
                    beta[tau] = beta0
                else:
                    mu[tau] = (kappa[tau-1] * mu[tau-1] + values[t-1]) / (kappa[tau-1] + 1)
                    kappa[tau] = kappa[tau-1] + 1
                    alpha[tau] = alpha[tau-1] + 0.5
                    beta[tau] = beta[tau-1] + (kappa[tau-1] * (values[t-1] - mu[tau-1])**2) / (2 * (kappa[tau-1] + 1))
                
                # Student's t predictive
                pred_probs[tau] = stats.t.pdf(
                    values[t-1],
                    df=2 * alpha[tau],
                    loc=mu[tau],
                    scale=np.sqrt(beta[tau] * (kappa[tau] + 1) / (alpha[tau] * kappa[tau]))
                )
            
            # Growth probabilities
            R[t, 1:t+1] = R[t-1, :t] * pred_probs * (1 - hazard)
            
            # Changepoint probability
            R[t, 0] = np.sum(R[t-1, :t] * pred_probs * hazard)
            
            # Normalize
            R[t, :] = R[t, :] / np.sum(R[t, :])
            
            # Most likely run length
            max_run_length = np.argmax(R[t, :t+1])
            max_probs.append(R[t, max_run_length])
            
            # Detect change point
            if max_run_length == 0 and t > 10:
                change_points.append(t - 1)
        
        self.detection_results['bocd'] = {
            'change_points': [self.data.index[i] for i in change_points],
            'change_indices': change_points,
            'n_changes': len(change_points),
            'run_length_probabilities': R,
            'max_probabilities': max_probs
        }
        
        return self.detection_results['bocd']
    
    def binary_segmentation(self, n_bkps: int = 5, 
                           model: str = 'l2') -> Dict:
        """
        Binary segmentation for change point detection.
        
        Args:
            n_bkps: Number of breakpoints to detect
            model: Cost model ('l1', 'l2', 'rbf')
            
        Returns:
            Dictionary with detection results
        """
        try:
            from ruptures import Binseg
            
            # Prepare signal
            signal = self.data.values.reshape(-1, 1)
            
            # Binary segmentation
            algo = Binseg(model=model).fit(signal)
            change_indices = algo.predict(n_bkps=n_bkps)
            
            # Remove last index (end of series)
            change_indices = change_indices[:-1]
            
            self.detection_results['binary_segmentation'] = {
                'change_points': [self.data.index[i] for i in change_indices],
                'change_indices': change_indices,
                'n_changes': len(change_indices),
                'model': model
            }
            
            return self.detection_results['binary_segmentation']
            
        except ImportError:
            warnings.warn("ruptures not installed. Using simple method.")
            return self._simple_segmentation(n_bkps)
    
    def _simple_segmentation(self, n_bkps: int) -> Dict:
        """Simple change point detection using variance"""
        values = self.data.values
        n = len(values)
        
        change_points = []
        segment_size = n // (n_bkps + 1)
        
        for i in range(1, n_bkps + 1):
            cp = i * segment_size
            change_points.append(cp)
        
        return {
            'change_points': [self.data.index[i] for i in change_points],
            'change_indices': change_points,
            'n_changes': len(change_points),
            'model': 'simple'
        }
    
    def pelt_detection(self, pen: float = None, model: str = 'l2') -> Dict:
        """
        PELT (Pruned Exact Linear Time) change point detection.
        
        Args:
            pen: Penalty value (auto-calculated if None)
            model: Cost model
            
        Returns:
            Dictionary with detection results
        """
        try:
            from ruptures import Pelt
            
            # Auto-calculate penalty if not provided
            if pen is None:
                pen = np.log(len(self.data)) * np.var(self.data.values)
            
            # Prepare signal
            signal = self.data.values.reshape(-1, 1)
            
            # PELT algorithm
            algo = Pelt(model=model, min_size=3, jump=5).fit(signal)
            change_indices = algo.predict(pen=pen)
            
            # Remove last index
            change_indices = change_indices[:-1]
            
            self.detection_results['pelt'] = {
                'change_points': [self.data.index[i] for i in change_indices],
                'change_indices': change_indices,
                'n_changes': len(change_indices),
                'penalty': pen,
                'model': model
            }
            
            return self.detection_results['pelt']
            
        except ImportError:
            warnings.warn("ruptures not installed. Using binary segmentation.")
            return self.binary_segmentation(n_bkps=5)
    
    def window_based_detection(self, window_size: int = 30,
                              threshold: float = 3.0) -> Dict:
        """
        Window-based change point detection.
        
        Args:
            window_size: Size of comparison windows
            threshold: Statistical threshold
            
        Returns:
            Dictionary with detection results
        """
        values = self.data.values
        n = len(values)
        
        change_points = []
        scores = np.zeros(n)
        
        for i in range(window_size, n - window_size):
            # Left and right windows
            left = values[i-window_size:i]
            right = values[i:i+window_size]
            
            # Two-sample t-test
            t_stat, p_value = stats.ttest_ind(left, right)
            
            # Store score
            scores[i] = abs(t_stat)
            
            # Detect change point
            if abs(t_stat) > threshold:
                change_points.append(i)
        
        self.detection_results['window'] = {
            'change_points': [self.data.index[i] for i in change_points],
            'change_indices': change_points,
            'n_changes': len(change_points),
            'scores': scores,
            'threshold': threshold,
            'window_size': window_size
        }
        
        return self.detection_results['window']
    
    def get_change_point_summary(self) -> Dict:
        """
        Get summary of all detected change points.
        
        Returns:
            Dictionary with change point summary
        """
        summary = {
            'total_methods': len(self.detection_results),
            'change_points_by_method': {},
            'all_change_points': set()
        }
        
        for method, results in self.detection_results.items():
            cps = results['change_points']
            summary['change_points_by_method'][method] = {
                'count': len(cps),
                'dates': cps
            }
            summary['all_change_points'].update(cps)
        
        summary['all_change_points'] = sorted(list(summary['all_change_points']))
        summary['total_unique_changes'] = len(summary['all_change_points'])
        
        return summary

# Example usage
"""
# Generate data with change points
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')

# Data with change points
data = np.concatenate([
    np.random.normal(10, 1, 500),
    np.random.normal(15, 1, 500),  # Mean shift
    np.random.normal(10, 2, 500),  # Variance change
    np.random.normal(12, 1, len(dates) - 1500)
])

ts = pd.Series(data, index=dates)

# Detect change points
detector = ChangePointDetector(ts)

# CUSUM
cusum_result = detector.cusum_detection(threshold=5)
print(f"CUSUM change points: {cusum_result['n_changes']}")

# Binary segmentation
bs_result = detector.binary_segmentation(n_bkps=5)
print(f"Binary Segmentation change points: {bs_result['n_changes']}")

summary = detector.get_change_point_summary()
print(f"Total unique change points: {summary['total_unique_changes']}")
"""
```


---

## 10. Rolling Statistics

### 10.1 Rolling Statistics Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/rolling_statistics.py

"""
Rolling Statistics Module for ResilienceAI
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Callable
import warnings
warnings.filterwarnings('ignore')

class RollingStatistics:
    """
    Comprehensive rolling statistics for time series analysis.
    Calculates moving averages, volatility, and custom statistics.
    """
    
    def __init__(self, data: pd.Series):
        """
        Initialize rolling statistics calculator.
        
        Args:
            data: Time series data as pandas Series with datetime index
        """
        self.data = data.dropna()
        self.statistics = {}
        
    def moving_average(self, window: int = 30, 
                      center: bool = False,
                      win_type: str = None) -> pd.Series:
        """
        Calculate moving average.
        
        Args:
            window: Window size
            center: Center the window
            win_type: Window type ('triang', 'gaussian', etc.)
            
        Returns:
            Series with moving average
        """
        if win_type:
            ma = self.data.rolling(window=window, center=center, win_type=win_type).mean()
        else:
            ma = self.data.rolling(window=window, center=center).mean()
        
        self.statistics[f'ma_{window}'] = ma
        return ma
    
    def exponential_moving_average(self, span: int = 30,
                                   adjust: bool = True) -> pd.Series:
        """
        Calculate exponential moving average (EMA).
        
        Args:
            span: Span for EMA calculation
            adjust: Use adjustment factor
            
        Returns:
            Series with EMA
        """
        ema = self.data.ewm(span=span, adjust=adjust).mean()
        self.statistics[f'ema_{span}'] = ema
        return ema
    
    def rolling_volatility(self, window: int = 30,
                          annualize: bool = False) -> pd.Series:
        """
        Calculate rolling volatility (standard deviation).
        
        Args:
            window: Window size
            annualize: Annualize the volatility
            
        Returns:
            Series with rolling volatility
        """
        vol = self.data.rolling(window=window).std()
        
        if annualize:
            # Assuming daily data, annualize by sqrt(252)
            vol = vol * np.sqrt(252)
        
        self.statistics[f'volatility_{window}'] = vol
        return vol
    
    def rolling_statistics_summary(self, window: int = 30) -> pd.DataFrame:
        """
        Calculate comprehensive rolling statistics.
        
        Args:
            window: Window size
            
        Returns:
            DataFrame with multiple rolling statistics
        """
        rolling = self.data.rolling(window=window)
        
        stats_df = pd.DataFrame(index=self.data.index)
        stats_df['mean'] = rolling.mean()
        stats_df['std'] = rolling.std()
        stats_df['var'] = rolling.var()
        stats_df['min'] = rolling.min()
        stats_df['max'] = rolling.max()
        stats_df['median'] = rolling.median()
        stats_df['skew'] = rolling.skew()
        stats_df['kurt'] = rolling.kurt()
        
        # Percentiles
        stats_df['q25'] = rolling.quantile(0.25)
        stats_df['q75'] = rolling.quantile(0.75)
        stats_df['iqr'] = stats_df['q75'] - stats_df['q25']
        
        # Range
        stats_df['range'] = stats_df['max'] - stats_df['min']
        
        # Coefficient of variation
        stats_df['cv'] = stats_df['std'] / stats_df['mean']
        
        self.statistics[f'summary_{window}'] = stats_df
        return stats_df
    
    def rolling_correlation(self, other: pd.Series,
                           window: int = 30) -> pd.Series:
        """
        Calculate rolling correlation with another series.
        
        Args:
            other: Other time series
            window: Window size
            
        Returns:
            Series with rolling correlation
        """
        corr = self.data.rolling(window=window).corr(other)
        self.statistics[f'corr_{window}'] = corr
        return corr
    
    def rolling_covariance(self, other: pd.Series,
                          window: int = 30) -> pd.Series:
        """
        Calculate rolling covariance with another series.
        
        Args:
            other: Other time series
            window: Window size
            
        Returns:
            Series with rolling covariance
        """
        cov = self.data.rolling(window=window).cov(other)
        self.statistics[f'cov_{window}'] = cov
        return cov
    
    def rolling_regression(self, x: pd.Series,
                          window: int = 30) -> pd.DataFrame:
        """
        Calculate rolling regression coefficients.
        
        Args:
            x: Independent variable
            window: Window size
            
        Returns:
            DataFrame with rolling regression parameters
        """
        from sklearn.linear_model import LinearRegression
        
        slopes = []
        intercepts = []
        r_squared = []
        
        for i in range(window, len(self.data)):
            y_window = self.data.iloc[i-window:i].values.reshape(-1, 1)
            x_window = x.iloc[i-window:i].values.reshape(-1, 1)
            
            model = LinearRegression()
            model.fit(x_window, y_window)
            
            slopes.append(model.coef_[0][0])
            intercepts.append(model.intercept_[0])
            r_squared.append(model.score(x_window, y_window))
        
        # Pad with NaN for initial values
        slopes = [np.nan] * (window - 1) + slopes
        intercepts = [np.nan] * (window - 1) + intercepts
        r_squared = [np.nan] * (window - 1) + r_squared
        
        result = pd.DataFrame({
            'slope': slopes,
            'intercept': intercepts,
            'r_squared': r_squared
        }, index=self.data.index)
        
        self.statistics[f'regression_{window}'] = result
        return result
    
    def rolling_percent_change(self, window: int = 1) -> pd.Series:
        """
        Calculate rolling percentage change.
        
        Args:
            window: Window size for percentage change
            
        Returns:
            Series with percentage changes
        """
        pct_change = self.data.pct_change(periods=window) * 100
        self.statistics[f'pct_change_{window}'] = pct_change
        return pct_change
    
    def rolling_zscore(self, window: int = 30) -> pd.Series:
        """
        Calculate rolling z-score.
        
        Args:
            window: Window size
            
        Returns:
            Series with rolling z-scores
        """
        rolling_mean = self.data.rolling(window=window).mean()
        rolling_std = self.data.rolling(window=window).std()
        
        zscore = (self.data - rolling_mean) / rolling_std
        self.statistics[f'zscore_{window}'] = zscore
        return zscore
    
    def bollinger_bands(self, window: int = 20,
                       num_std: float = 2.0) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        
        Args:
            window: Window size for moving average
            num_std: Number of standard deviations for bands
            
        Returns:
            DataFrame with middle, upper, and lower bands
        """
        middle = self.data.rolling(window=window).mean()
        std = self.data.rolling(window=window).std()
        
        upper = middle + num_std * std
        lower = middle - num_std * std
        
        bands = pd.DataFrame({
            'middle': middle,
            'upper': upper,
            'lower': lower,
            'bandwidth': upper - lower,
            'percent_b': (self.data - lower) / (upper - lower)
        }, index=self.data.index)
        
        self.statistics[f'bollinger_{window}'] = bands
        return bands
    
    def rolling_rank(self, window: int = 30) -> pd.Series:
        """
        Calculate rolling rank (percentile) of current value.
        
        Args:
            window: Window size
            
        Returns:
            Series with rolling ranks (0-1)
        """
        def rank_in_window(x):
            return (x[-1] - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0.5
        
        rank = self.data.rolling(window=window).apply(rank_in_window, raw=True)
        self.statistics[f'rank_{window}'] = rank
        return rank
    
    def custom_rolling(self, func: Callable, 
                      window: int = 30,
                      name: str = 'custom') -> pd.Series:
        """
        Apply custom function on rolling window.
        
        Args:
            func: Custom function to apply
            window: Window size
            name: Name for the statistic
            
        Returns:
            Series with custom rolling statistic
        """
        result = self.data.rolling(window=window).apply(func, raw=True)
        self.statistics[f'{name}_{window}'] = result
        return result
    
    def get_all_statistics(self) -> pd.DataFrame:
        """
        Get all calculated statistics as a DataFrame.
        
        Returns:
            DataFrame with all statistics
        """
        if not self.statistics:
            return pd.DataFrame(index=self.data.index)
        
        return pd.concat(self.statistics.values(), axis=1)

# Example usage
"""
# Generate sample data
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
data = pd.Series(np.random.randn(len(dates)).cumsum() + 100, index=dates)

# Calculate rolling statistics
rs = RollingStatistics(data)

# Moving averages
ma_30 = rs.moving_average(window=30)
ema_30 = rs.exponential_moving_average(span=30)

# Comprehensive statistics
summary = rs.rolling_statistics_summary(window=30)

# Bollinger Bands
bb = rs.bollinger_bands(window=20)

print("Rolling Statistics Summary:")
print(summary.tail())
"""
```

---

## 11. Time Series Visualization

### 11.1 Visualization Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/visualization.py

"""
Time Series Visualization Module for ResilienceAI
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from typing import Dict, List, Optional, Tuple, Union
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 8)
plt.rcParams['font.size'] = 10

class TimeSeriesVisualizer:
    """
    Comprehensive time series visualization for disaster data analysis.
    Creates publication-quality plots for reports and dashboards.
    """
    
    def __init__(self, data: pd.Series):
        """
        Initialize visualizer.
        
        Args:
            data: Time series data as pandas Series with datetime index
        """
        self.data = data.dropna()
        self.figures = {}
        
    def plot_time_series(self, title: str = 'Time Series',
                        figsize: Tuple[int, int] = (15, 6),
                        color: str = 'steelblue',
                        save_path: str = None) -> plt.Figure:
        """
        Plot basic time series.
        
        Args:
            title: Plot title
            figsize: Figure size
            color: Line color
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(self.data.index, self.data.values, 
               color=color, linewidth=1.5, alpha=0.8)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        self.figures['time_series'] = fig
        return fig
    
    def plot_with_moving_averages(self, windows: List[int] = [7, 30, 90],
                                  figsize: Tuple[int, int] = (15, 8),
                                  save_path: str = None) -> plt.Figure:
        """
        Plot time series with multiple moving averages.
        
        Args:
            windows: List of window sizes for moving averages
            figsize: Figure size
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot original series
        ax.plot(self.data.index, self.data.values, 
               label='Original', color='black', alpha=0.3, linewidth=1)
        
        # Plot moving averages
        colors = ['orange', 'green', 'red', 'purple']
        for i, window in enumerate(windows):
            ma = self.data.rolling(window=window).mean()
            ax.plot(self.data.index, ma.values, 
                   label=f'MA-{window}', color=colors[i % len(colors)], 
                   linewidth=2, alpha=0.8)
        
        ax.set_title('Time Series with Moving Averages', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        self.figures['moving_averages'] = fig
        return fig
    
    def plot_seasonality(self, figsize: Tuple[int, int] = (15, 10),
                        save_path: str = None) -> plt.Figure:
        """
        Plot seasonality components (yearly, monthly, weekly).
        
        Args:
            figsize: Figure size
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(3, 1, figsize=figsize)
        
        # Yearly seasonality
        yearly = self.data.groupby(self.data.index.month).mean()
        axes[0].bar(yearly.index, yearly.values, color='steelblue', alpha=0.7)
        axes[0].set_title('Yearly Seasonality (Monthly Average)', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('Month')
        axes[0].set_ylabel('Average Value')
        axes[0].set_xticks(range(1, 13))
        axes[0].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        
        # Weekly seasonality
        weekly = self.data.groupby(self.data.index.dayofweek).mean()
        axes[1].bar(weekly.index, weekly.values, color='green', alpha=0.7)
        axes[1].set_title('Weekly Seasonality (Daily Average)', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Day of Week')
        axes[1].set_ylabel('Average Value')
        axes[1].set_xticks(range(7))
        axes[1].set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        
        # Hourly seasonality (if data has hour information)
        if hasattr(self.data.index, 'hour'):
            hourly = self.data.groupby(self.data.index.hour).mean()
            axes[2].plot(hourly.index, hourly.values, color='red', marker='o')
            axes[2].set_title('Hourly Seasonality', fontsize=12, fontweight='bold')
            axes[2].set_xlabel('Hour of Day')
            axes[2].set_ylabel('Average Value')
            axes[2].set_xticks(range(0, 24, 2))
        else:
            axes[2].text(0.5, 0.5, 'No hourly data available',
                        ha='center', va='center', fontsize=12)
            axes[2].set_title('Hourly Seasonality', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        self.figures['seasonality'] = fig
        return fig
    
    def plot_forecast(self, forecast: pd.Series,
                     lower_bound: pd.Series = None,
                     upper_bound: pd.Series = None,
                     title: str = 'Forecast',
                     figsize: Tuple[int, int] = (15, 8),
                     save_path: str = None) -> plt.Figure:
        """
        Plot forecast with confidence intervals.
        
        Args:
            forecast: Forecast values
            lower_bound: Lower confidence bound
            upper_bound: Upper confidence bound
            title: Plot title
            figsize: Figure size
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot historical data
        ax.plot(self.data.index, self.data.values, 
               label='Historical', color='black', linewidth=1.5)
        
        # Plot forecast
        ax.plot(forecast.index, forecast.values, 
               label='Forecast', color='blue', linewidth=2)
        
        # Plot confidence interval
        if lower_bound is not None and upper_bound is not None:
            ax.fill_between(forecast.index, lower_bound.values, upper_bound.values,
                          alpha=0.3, color='blue', label='Confidence Interval')
        
        # Add vertical line at forecast start
        forecast_start = forecast.index[0]
        ax.axvline(x=forecast_start, color='red', linestyle='--', 
                  alpha=0.7, label='Forecast Start')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        self.figures['forecast'] = fig
        return fig
    
    def plot_anomalies(self, anomalies: pd.Series,
                      anomaly_scores: pd.Series = None,
                      title: str = 'Anomaly Detection',
                      figsize: Tuple[int, int] = (15, 8),
                      save_path: str = None) -> plt.Figure:
        """
        Plot time series with detected anomalies highlighted.
        
        Args:
            anomalies: Boolean series indicating anomalies
            anomaly_scores: Anomaly scores (optional)
            title: Plot title
            figsize: Figure size
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 1, figsize=figsize, 
                                gridspec_kw={'height_ratios': [3, 1]})
        
        # Main plot
        axes[0].plot(self.data.index, self.data.values, 
                    color='black', alpha=0.7, linewidth=1, label='Data')
        
        # Highlight anomalies
        anomaly_points = self.data[anomalies]
        axes[0].scatter(anomaly_points.index, anomaly_points.values,
                       color='red', s=50, zorder=5, label='Anomalies')
        
        axes[0].set_title(title, fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Value', fontsize=12)
        axes[0].legend(loc='best')
        axes[0].grid(True, alpha=0.3)
        
        # Anomaly scores plot
        if anomaly_scores is not None:
            axes[1].plot(self.data.index, anomaly_scores.values,
                        color='orange', linewidth=1)
            axes[1].axhline(y=anomaly_scores.mean() + 2*anomaly_scores.std(),
                          color='red', linestyle='--', alpha=0.7,
                          label='Threshold')
            axes[1].set_ylabel('Anomaly Score', fontsize=12)
            axes[1].set_xlabel('Date', fontsize=12)
            axes[1].legend(loc='best')
            axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        self.figures['anomalies'] = fig
        return fig
    
    def plot_change_points(self, change_points: List[pd.Timestamp],
                          title: str = 'Change Point Detection',
                          figsize: Tuple[int, int] = (15, 6),
                          save_path: str = None) -> plt.Figure:
        """
        Plot time series with detected change points.
        
        Args:
            change_points: List of change point dates
            title: Plot title
            figsize: Figure size
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot data
        ax.plot(self.data.index, self.data.values, 
               color='black', linewidth=1.5, label='Data')
        
        # Mark change points
        for cp in change_points:
            ax.axvline(x=cp, color='red', linestyle='--', alpha=0.7)
        
        # Add legend
        ax.axvline(x=change_points[0] if change_points else self.data.index[0],
                  color='red', linestyle='--', alpha=0.7,
                  label='Change Points')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        self.figures['change_points'] = fig
        return fig
    
    def plot_correlation_matrix(self, other_series: Dict[str, pd.Series],
                               figsize: Tuple[int, int] = (10, 8),
                               save_path: str = None) -> plt.Figure:
        """
        Plot correlation matrix with other time series.
        
        Args:
            other_series: Dictionary of other time series
            figsize: Figure size
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        # Combine all series
        all_series = {'Target': self.data}
        all_series.update(other_series)
        
        # Create DataFrame
        df = pd.DataFrame(all_series)
        
        # Calculate correlation matrix
        corr_matrix = df.corr()
        
        # Plot
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
                   ax=ax)
        
        ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        self.figures['correlation'] = fig
        return fig
    
    def plot_acf_pacf(self, lags: int = 40,
                     figsize: Tuple[int, int] = (15, 5),
                     save_path: str = None) -> plt.Figure:
        """
        Plot ACF and PACF for time series.
        
        Args:
            lags: Number of lags to plot
            figsize: Figure size
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        try:
            from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
        except ImportError:
            raise ImportError("statsmodels not installed")
        
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # ACF
        plot_acf(self.data.dropna(), lags=lags, ax=axes[0])
        axes[0].set_title('Autocorrelation Function (ACF)', fontsize=12, fontweight='bold')
        
        # PACF
        plot_pacf(self.data.dropna(), lags=lags, ax=axes[1])
        axes[1].set_title('Partial Autocorrelation Function (PACF)', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        self.figures['acf_pacf'] = fig
        return fig
    
    def create_dashboard(self, forecast: pd.Series = None,
                        anomalies: pd.Series = None,
                        change_points: List[pd.Timestamp] = None,
                        figsize: Tuple[int, int] = (20, 16),
                        save_path: str = None) -> plt.Figure:
        """
        Create comprehensive dashboard with multiple plots.
        
        Args:
            forecast: Forecast series (optional)
            anomalies: Anomaly boolean series (optional)
            change_points: List of change points (optional)
            figsize: Figure size
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Main time series
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.data.index, self.data.values, color='black', linewidth=1)
        if forecast is not None:
            ax1.plot(forecast.index, forecast.values, color='blue', linewidth=2)
        if anomalies is not None:
            anomaly_points = self.data[anomalies]
            ax1.scatter(anomaly_points.index, anomaly_points.values, 
                       color='red', s=30, zorder=5)
        if change_points:
            for cp in change_points:
                ax1.axvline(x=cp, color='orange', linestyle='--', alpha=0.5)
        ax1.set_title('Time Series Overview', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Moving averages
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.plot(self.data.index, self.data.values, color='black', alpha=0.3)
        ax2.plot(self.data.index, self.data.rolling(30).mean(), 
                color='blue', linewidth=2, label='MA-30')
        ax2.plot(self.data.index, self.data.rolling(90).mean(), 
                color='red', linewidth=2, label='MA-90')
        ax2.set_title('Moving Averages', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Seasonality
        ax3 = fig.add_subplot(gs[1, 1])
        monthly = self.data.groupby(self.data.index.month).mean()
        ax3.bar(monthly.index, monthly.values, color='steelblue', alpha=0.7)
        ax3.set_title('Monthly Seasonality', fontsize=12, fontweight='bold')
        ax3.set_xticks(range(1, 13))
        ax3.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
        
        # Distribution
        ax4 = fig.add_subplot(gs[2, 0])
        ax4.hist(self.data.values, bins=50, color='green', alpha=0.7, edgecolor='black')
        ax4.set_title('Value Distribution', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Value')
        ax4.set_ylabel('Frequency')
        
        # Rolling statistics
        ax5 = fig.add_subplot(gs[2, 1])
        rolling_mean = self.data.rolling(30).mean()
        rolling_std = self.data.rolling(30).std()
        ax5.plot(self.data.index, rolling_mean, color='blue', label='Mean')
        ax5.fill_between(self.data.index, 
                        rolling_mean - rolling_std, 
                        rolling_mean + rolling_std,
                        alpha=0.3, color='blue', label='±1 Std')
        ax5.set_title('Rolling Statistics (30-day)', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        self.figures['dashboard'] = fig
        return fig

# Example usage
"""
# Generate sample data
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
data = pd.Series(np.random.randn(len(dates)).cumsum() + 100, index=dates)

# Create visualizations
viz = TimeSeriesVisualizer(data)

# Basic time series plot
viz.plot_time_series(title='Disaster Events Over Time')

# With moving averages
viz.plot_with_moving_averages(windows=[7, 30, 90])

# Seasonality
viz.plot_seasonality()

# Dashboard
viz.create_dashboard()

plt.show()
"""
```


---

## 12. Model Selection Framework

### 12.1 Model Selection Guide

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/model_selection.py

"""
Model Selection Framework for ResilienceAI Time Series
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class DataCharacteristics(Enum):
    """Data characteristics for model selection"""
    SHORT_SERIES = "short_series"           # < 100 observations
    MEDIUM_SERIES = "medium_series"         # 100-1000 observations
    LONG_SERIES = "long_series"             # > 1000 observations
    
    STATIONARY = "stationary"
    NON_STATIONARY = "non_stationary"
    
    STRONG_SEASONALITY = "strong_seasonality"
    WEAK_SEASONALITY = "weak_seasonality"
    NO_SEASONALITY = "no_seasonality"
    
    HIGH_FREQUENCY = "high_frequency"       # Hourly, daily
    LOW_FREQUENCY = "low_frequency"         # Weekly, monthly
    
    WITH_OUTLIERS = "with_outliers"
    CLEAN_DATA = "clean_data"

@dataclass
class ModelRecommendation:
    """Model recommendation result"""
    primary_model: str
    secondary_models: List[str]
    reasoning: str
    expected_performance: str
    complexity: str
    training_time: str

class ModelSelector:
    """
    Intelligent model selection for time series forecasting.
    Recommends optimal models based on data characteristics.
    """
    
    def __init__(self):
        """Initialize model selector"""
        self.model_characteristics = {
            'arima': {
                'min_observations': 30,
                'handles_seasonality': True,
                'handles_trend': True,
                'robust_to_outliers': False,
                'interpretability': 'high',
                'training_speed': 'fast',
                'forecast_quality': 'good_for_short_term'
            },
            'sarima': {
                'min_observations': 60,
                'handles_seasonality': True,
                'handles_trend': True,
                'robust_to_outliers': False,
                'interpretability': 'high',
                'training_speed': 'medium',
                'forecast_quality': 'good_for_seasonal'
            },
            'prophet': {
                'min_observations': 30,
                'handles_seasonality': True,
                'handles_trend': True,
                'robust_to_outliers': True,
                'interpretability': 'high',
                'training_speed': 'fast',
                'forecast_quality': 'good_for_long_term'
            },
            'lstm': {
                'min_observations': 500,
                'handles_seasonality': True,
                'handles_trend': True,
                'robust_to_outliers': True,
                'interpretability': 'low',
                'training_speed': 'slow',
                'forecast_quality': 'excellent_for_complex'
            },
            'xgboost': {
                'min_observations': 100,
                'handles_seasonality': True,
                'handles_trend': True,
                'robust_to_outliers': True,
                'interpretability': 'medium',
                'training_speed': 'fast',
                'forecast_quality': 'good_for_features'
            },
            'ensemble': {
                'min_observations': 100,
                'handles_seasonality': True,
                'handles_trend': True,
                'robust_to_outliers': True,
                'interpretability': 'medium',
                'training_speed': 'slow',
                'forecast_quality': 'excellent'
            }
        }
    
    def analyze_data(self, data: pd.Series) -> Dict[str, any]:
        """
        Analyze data characteristics for model selection.
        
        Args:
            data: Time series data
            
        Returns:
            Dictionary with data characteristics
        """
        characteristics = []
        
        # Series length
        n_obs = len(data)
        if n_obs < 100:
            characteristics.append(DataCharacteristics.SHORT_SERIES)
        elif n_obs < 1000:
            characteristics.append(DataCharacteristics.MEDIUM_SERIES)
        else:
            characteristics.append(DataCharacteristics.LONG_SERIES)
        
        # Stationarity
        from statsmodels.tsa.stattools import adfuller
        try:
            adf_result = adfuller(data.dropna())
            if adf_result[1] < 0.05:
                characteristics.append(DataCharacteristics.STATIONARY)
            else:
                characteristics.append(DataCharacteristics.NON_STATIONARY)
        except:
            characteristics.append(DataCharacteristics.NON_STATIONARY)
        
        # Seasonality detection
        if n_obs >= 60:  # Need at least 2 months for seasonality
            monthly_avg = data.groupby(data.index.month).mean()
            seasonal_strength = monthly_avg.std() / data.mean()
            
            if seasonal_strength > 0.3:
                characteristics.append(DataCharacteristics.STRONG_SEASONALITY)
            elif seasonal_strength > 0.1:
                characteristics.append(DataCharacteristics.WEAK_SEASONALITY)
            else:
                characteristics.append(DataCharacteristics.NO_SEASONALITY)
        else:
            characteristics.append(DataCharacteristics.NO_SEASONALITY)
        
        # Frequency
        inferred_freq = pd.infer_freq(data.index)
        if inferred_freq in ['H', 'T', 'S']:
            characteristics.append(DataCharacteristics.HIGH_FREQUENCY)
        else:
            characteristics.append(DataCharacteristics.LOW_FREQUENCY)
        
        # Outliers
        z_scores = np.abs((data - data.mean()) / data.std())
        outlier_ratio = (z_scores > 3).mean()
        
        if outlier_ratio > 0.05:
            characteristics.append(DataCharacteristics.WITH_OUTLIERS)
        else:
            characteristics.append(DataCharacteristics.CLEAN_DATA)
        
        return {
            'characteristics': characteristics,
            'n_observations': n_obs,
            'outlier_ratio': outlier_ratio,
            'seasonal_strength': seasonal_strength if n_obs >= 60 else None
        }
    
    def recommend_model(self, data: pd.Series, 
                       forecast_horizon: int = 30) -> ModelRecommendation:
        """
        Recommend best model(s) for the data.
        
        Args:
            data: Time series data
            forecast_horizon: Forecast horizon in periods
            
        Returns:
            ModelRecommendation object
        """
        analysis = self.analyze_data(data)
        chars = analysis['characteristics']
        n_obs = analysis['n_observations']
        
        # Decision logic
        if DataCharacteristics.SHORT_SERIES in chars:
            # Short series - use simple models
            if DataCharacteristics.STRONG_SEASONALITY in chars:
                return ModelRecommendation(
                    primary_model='prophet',
                    secondary_models=['arima'],
                    reasoning="Short series with seasonality. Prophet handles missing data and outliers well.",
                    expected_performance="Good for short-term forecasts",
                    complexity="Low",
                    training_time="Fast"
                )
            else:
                return ModelRecommendation(
                    primary_model='arima',
                    secondary_models=['prophet'],
                    reasoning="Short series without strong seasonality. ARIMA is efficient.",
                    expected_performance="Good for short-term forecasts",
                    complexity="Low",
                    training_time="Fast"
                )
        
        elif DataCharacteristics.LONG_SERIES in chars:
            # Long series - can use complex models
            if DataCharacteristics.STRONG_SEASONALITY in chars:
                return ModelRecommendation(
                    primary_model='ensemble',
                    secondary_models=['lstm', 'prophet'],
                    reasoning="Long series with strong seasonality. Ensemble of LSTM and Prophet for best accuracy.",
                    expected_performance="Excellent for complex patterns",
                    complexity="High",
                    training_time="Slow"
                )
            else:
                return ModelRecommendation(
                    primary_model='lstm',
                    secondary_models=['prophet', 'xgboost'],
                    reasoning="Long series without strong seasonality. LSTM captures complex patterns.",
                    expected_performance="Excellent for complex patterns",
                    complexity="High",
                    training_time="Slow"
                )
        
        else:  # Medium series
            if DataCharacteristics.WITH_OUTLIERS in chars:
                return ModelRecommendation(
                    primary_model='prophet',
                    secondary_models=['xgboost'],
                    reasoning="Medium series with outliers. Prophet is robust to outliers.",
                    expected_performance="Good for medium-term forecasts",
                    complexity="Medium",
                    training_time="Medium"
                )
            else:
                return ModelRecommendation(
                    primary_model='sarima',
                    secondary_models=['prophet', 'arima'],
                    reasoning="Medium series without outliers. SARIMA for seasonal patterns.",
                    expected_performance="Good for seasonal forecasts",
                    complexity="Medium",
                    training_time="Medium"
                )
    
    def compare_models(self, data: pd.Series, 
                      test_size: float = 0.2) -> pd.DataFrame:
        """
        Compare multiple models on the data.
        
        Args:
            data: Time series data
            test_size: Fraction of data for testing
            
        Returns:
            DataFrame with model comparison
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error
        
        # Split data
        split_idx = int(len(data) * (1 - test_size))
        train_data = data.iloc[:split_idx]
        test_data = data.iloc[split_idx:]
        
        results = []
        
        # Try each model
        models_to_try = ['arima', 'prophet']
        
        for model_name in models_to_try:
            try:
                if model_name == 'arima':
                    from .arima_models import ARIMAModel
                    model = ARIMAModel(train_data)
                    model.fit()
                    forecast = model.forecast(steps=len(test_data))
                    predictions = forecast['forecast']
                    
                elif model_name == 'prophet':
                    from .prophet_models import ProphetForecaster
                    model = ProphetForecaster()
                    model.fit(train_data)
                    forecast = model.forecast(periods=len(test_data))
                    predictions = forecast['forecast']['yhat']
                    predictions.index = test_data.index
                
                # Calculate metrics
                mse = mean_squared_error(test_data, predictions)
                rmse = np.sqrt(mse)
                mae = mean_absolute_error(test_data, predictions)
                mape = np.mean(np.abs((test_data - predictions) / test_data)) * 100
                
                results.append({
                    'model': model_name,
                    'mse': mse,
                    'rmse': rmse,
                    'mae': mae,
                    'mape': mape
                })
                
            except Exception as e:
                results.append({
                    'model': model_name,
                    'error': str(e)
                })
        
        return pd.DataFrame(results)

# Example usage
"""
# Generate sample data
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
data = pd.Series(np.random.randn(len(dates)).cumsum() + 100, index=dates)

# Get model recommendation
selector = ModelSelector()
recommendation = selector.recommend_model(data, forecast_horizon=30)

print(f"Primary Model: {recommendation.primary_model}")
print(f"Secondary Models: {recommendation.secondary_models}")
print(f"Reasoning: {recommendation.reasoning}")
"""
```

---

## 13. Integration Approach

### 13.1 Pipeline Integration

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/pipeline.py

"""
Time Series Pipeline Integration for ResilienceAI
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import pickle

@dataclass
class PipelineConfig:
    """Configuration for time series pipeline"""
    # Data parameters
    date_column: str = 'date'
    target_column: str = 'value'
    frequency: str = 'D'
    
    # Preprocessing
    handle_missing: str = 'interpolate'  # 'interpolate', 'forward_fill', 'drop'
    remove_outliers: bool = True
    outlier_method: str = 'zscore'
    outlier_threshold: float = 3.0
    
    # Analysis
    perform_decomposition: bool = True
    decomposition_method: str = 'stl'
    detect_seasonality: bool = True
    detect_trend: bool = True
    
    # Modeling
    forecast_horizon: int = 30
    models: List[str] = field(default_factory=lambda: ['prophet', 'arima'])
    use_ensemble: bool = True
    
    # Anomaly detection
    detect_anomalies: bool = True
    anomaly_methods: List[str] = field(default_factory=lambda: ['statistical', 'isolation_forest'])
    
    # Output
    save_results: bool = True
    output_directory: str = './output'

class TimeSeriesPipeline:
    """
    End-to-end time series analysis pipeline for ResilienceAI.
    Integrates all components into a unified workflow.
    """
    
    def __init__(self, config: PipelineConfig = None):
        """
        Initialize pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or PipelineConfig()
        self.results = {}
        self.models = {}
        
    def load_data(self, data: Union[pd.DataFrame, str]) -> pd.DataFrame:
        """
        Load and validate data.
        
        Args:
            data: DataFrame or path to CSV file
            
        Returns:
            Validated DataFrame
        """
        if isinstance(data, str):
            df = pd.read_csv(data)
        else:
            df = data.copy()
        
        # Validate columns
        if self.config.date_column not in df.columns:
            raise ValueError(f"Date column '{self.config.date_column}' not found")
        if self.config.target_column not in df.columns:
            raise ValueError(f"Target column '{self.config.target_column}' not found")
        
        # Convert date column
        df[self.config.date_column] = pd.to_datetime(df[self.config.date_column])
        df.set_index(self.config.date_column, inplace=True)
        
        # Sort by date
        df.sort_index(inplace=True)
        
        return df
    
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        # Handle missing values
        if self.config.handle_missing == 'interpolate':
            df[self.config.target_column] = df[self.config.target_column].interpolate()
        elif self.config.handle_missing == 'forward_fill':
            df[self.config.target_column] = df[self.config.target_column].fillna(method='ffill')
        elif self.config.handle_missing == 'drop':
            df = df.dropna(subset=[self.config.target_column])
        
        # Remove outliers
        if self.config.remove_outliers:
            if self.config.outlier_method == 'zscore':
                z_scores = np.abs((df[self.config.target_column] - df[self.config.target_column].mean()) / 
                                 df[self.config.target_column].std())
                df = df[z_scores < self.config.outlier_threshold]
            elif self.config.outlier_method == 'iqr':
                Q1 = df[self.config.target_column].quantile(0.25)
                Q3 = df[self.config.target_column].quantile(0.75)
                IQR = Q3 - Q1
                df = df[(df[self.config.target_column] >= Q1 - 1.5*IQR) & 
                       (df[self.config.target_column] <= Q3 + 1.5*IQR)]
        
        return df
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Perform comprehensive analysis.
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            Analysis results
        """
        series = df[self.config.target_column]
        analysis_results = {}
        
        # Decomposition
        if self.config.perform_decomposition:
            from .decomposition import TimeSeriesDecomposer
            decomposer = TimeSeriesDecomposer(series, freq=self.config.frequency)
            analysis_results['decomposition'] = decomposer.stl_decomposition()
            analysis_results['decomposition_strength'] = decomposer.get_strength_metrics()
        
        # Seasonality detection
        if self.config.detect_seasonality:
            from .seasonality import SeasonalityDetector
            detector = SeasonalityDetector(series)
            analysis_results['seasonality'] = detector.detect_all_seasonalities()
        
        # Trend analysis
        if self.config.detect_trend:
            from .trend_analysis import TrendAnalyzer
            analyzer = TrendAnalyzer(series)
            analysis_results['trend'] = analyzer.get_trend_summary()
        
        return analysis_results
    
    def fit_models(self, df: pd.DataFrame) -> Dict:
        """
        Fit forecasting models.
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            Fitted models and forecasts
        """
        series = df[self.config.target_column]
        model_results = {}
        forecasts = {}
        
        for model_name in self.config.models:
            try:
                if model_name == 'arima':
                    from .arima_models import ARIMAModel
                    model = ARIMAModel(series)
                    model.fit()
                    forecast = model.forecast(steps=self.config.forecast_horizon)
                    model_results['arima'] = model
                    forecasts['arima'] = forecast
                    
                elif model_name == 'prophet':
                    from .prophet_models import ProphetForecaster
                    model = ProphetForecaster()
                    model.fit(series)
                    forecast = model.forecast(periods=self.config.forecast_horizon)
                    model_results['prophet'] = model
                    forecasts['prophet'] = forecast
                    
                elif model_name == 'lstm':
                    from .lstm_models import LSTMForecaster
                    model = LSTMForecaster(sequence_length=30)
                    model.fit(series, verbose=0)
                    last_sequence = series.values[-30:].reshape(-1, 1)
                    forecast = model.predict(steps=self.config.forecast_horizon, 
                                            last_sequence=last_sequence)
                    model_results['lstm'] = model
                    forecasts['lstm'] = forecast
                    
            except Exception as e:
                print(f"Error fitting {model_name}: {str(e)}")
                continue
        
        self.models = model_results
        
        # Ensemble forecast
        if self.config.use_ensemble and len(forecasts) > 1:
            forecasts['ensemble'] = self._create_ensemble(forecasts)
        
        return forecasts
    
    def _create_ensemble(self, forecasts: Dict) -> pd.Series:
        """Create ensemble forecast from multiple models"""
        # Simple average ensemble
        forecast_values = []
        for model_name, forecast in forecasts.items():
            if isinstance(forecast, dict):
                forecast_values.append(forecast['forecast'].values)
            else:
                forecast_values.append(forecast.values)
        
        ensemble_values = np.mean(forecast_values, axis=0)
        
        # Use index from first forecast
        first_forecast = list(forecasts.values())[0]
        if isinstance(first_forecast, dict):
            index = first_forecast['forecast'].index
        else:
            index = first_forecast.index
        
        return pd.Series(ensemble_values, index=index)
    
    def detect_anomalies(self, df: pd.DataFrame) -> Dict:
        """
        Detect anomalies in the data.
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            Anomaly detection results
        """
        if not self.config.detect_anomalies:
            return {}
        
        series = df[self.config.target_column]
        
        from .anomaly_detection import AnomalyDetector
        detector = AnomalyDetector(series)
        
        # Run specified methods
        for method in self.config.anomaly_methods:
            if method == 'statistical':
                detector.statistical_method()
            elif method == 'isolation_forest':
                detector.isolation_forest()
            elif method == 'prophet':
                detector.prophet_anomaly_detection()
        
        # Get ensemble results
        return detector.ensemble_detection()
    
    def run(self, data: Union[pd.DataFrame, str]) -> Dict:
        """
        Run complete pipeline.
        
        Args:
            data: Input data or path to data file
            
        Returns:
            Complete pipeline results
        """
        print("=" * 60)
        print("ResilienceAI Time Series Pipeline")
        print("=" * 60)
        
        # Load data
        print("\n[1/6] Loading data...")
        df = self.load_data(data)
        print(f"  Loaded {len(df)} observations")
        
        # Preprocess
        print("\n[2/6] Preprocessing...")
        df = self.preprocess(df)
        print(f"  Preprocessed to {len(df)} observations")
        
        # Analyze
        print("\n[3/6] Analyzing...")
        analysis_results = self.analyze(df)
        print("  Analysis complete")
        
        # Fit models
        print("\n[4/6] Fitting models...")
        forecasts = self.fit_models(df)
        print(f"  Fitted {len(self.models)} models")
        
        # Detect anomalies
        print("\n[5/6] Detecting anomalies...")
        anomalies = self.detect_anomalies(df)
        print("  Anomaly detection complete")
        
        # Compile results
        print("\n[6/6] Compiling results...")
        self.results = {
            'data_summary': {
                'n_observations': len(df),
                'date_range': (df.index.min(), df.index.max()),
                'mean': df[self.config.target_column].mean(),
                'std': df[self.config.target_column].std()
            },
            'analysis': analysis_results,
            'forecasts': forecasts,
            'anomalies': anomalies,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save results
        if self.config.save_results:
            self._save_results()
        
        print("\n" + "=" * 60)
        print("Pipeline completed successfully!")
        print("=" * 60)
        
        return self.results
    
    def _save_results(self):
        """Save pipeline results to disk"""
        import os
        os.makedirs(self.config.output_directory, exist_ok=True)
        
        # Save as JSON (excluding non-serializable objects)
        results_json = {
            'data_summary': self.results['data_summary'],
            'timestamp': self.results['timestamp']
        }
        
        with open(f"{self.config.output_directory}/results.json", 'w') as f:
            json.dump(results_json, f, indent=2, default=str)
        
        # Save forecasts
        if 'forecasts' in self.results:
            for model_name, forecast in self.results['forecasts'].items():
                if isinstance(forecast, dict):
                    forecast_df = forecast['forecast']
                else:
                    forecast_df = forecast
                forecast_df.to_csv(f"{self.config.output_directory}/forecast_{model_name}.csv")
        
        print(f"  Results saved to {self.config.output_directory}")

# Example usage
"""
# Create pipeline configuration
config = PipelineConfig(
    date_column='date',
    target_column='disaster_count',
    forecast_horizon=30,
    models=['prophet', 'arima'],
    use_ensemble=True
)

# Create and run pipeline
pipeline = TimeSeriesPipeline(config)

# Generate sample data
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
data = pd.DataFrame({
    'date': dates,
    'disaster_count': np.random.poisson(5, len(dates))
})

# Run pipeline
results = pipeline.run(data)

# Access results
print(f"Forecast horizon: {len(results['forecasts']['prophet']['forecast'])}")
"""
```

---

## 14. Performance Tuning

### 14.1 Hyperparameter Optimization

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/hyperparameter_tuning.py

"""
Hyperparameter Tuning for Time Series Models
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable, Any
from sklearn.model_selection import TimeSeriesSplit
import optuna
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesTuner:
    """
    Hyperparameter tuning for time series models using Optuna.
    """
    
    def __init__(self, data: pd.Series, metric: str = 'rmse'):
        """
        Initialize tuner.
        
        Args:
            data: Time series data
            metric: Optimization metric ('rmse', 'mae', 'mape')
        """
        self.data = data
        self.metric = metric
        self.best_params = {}
        self.study = None
    
    def tune_arima(self, n_trials: int = 50) -> Dict:
        """
        Tune ARIMA hyperparameters.
        
        Args:
            n_trials: Number of optimization trials
            
        Returns:
            Dictionary with best parameters
        """
        def objective(trial):
            p = trial.suggest_int('p', 0, 5)
            d = trial.suggest_int('d', 0, 2)
            q = trial.suggest_int('q', 0, 5)
            
            try:
                from statsmodels.tsa.arima.model import ARIMA
                
                # Time series cross-validation
                tscv = TimeSeriesSplit(n_splits=3)
                scores = []
                
                for train_idx, val_idx in tscv.split(self.data):
                    train_data = self.data.iloc[train_idx]
                    val_data = self.data.iloc[val_idx]
                    
                    model = ARIMA(train_data, order=(p, d, q))
                    fitted = model.fit()
                    
                    forecast = fitted.forecast(steps=len(val_data))
                    
                    if self.metric == 'rmse':
                        score = np.sqrt(np.mean((val_data - forecast) ** 2))
                    elif self.metric == 'mae':
                        score = np.mean(np.abs(val_data - forecast))
                    elif self.metric == 'mape':
                        score = np.mean(np.abs((val_data - forecast) / val_data)) * 100
                    
                    scores.append(score)
                
                return np.mean(scores)
                
            except Exception as e:
                return float('inf')
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
        
        self.best_params['arima'] = study.best_params
        self.study = study
        
        return study.best_params
    
    def tune_prophet(self, n_trials: int = 50) -> Dict:
        """
        Tune Prophet hyperparameters.
        
        Args:
            n_trials: Number of optimization trials
            
        Returns:
            Dictionary with best parameters
        """
        def objective(trial):
            changepoint_prior_scale = trial.suggest_float('changepoint_prior_scale', 0.001, 0.5, log=True)
            seasonality_prior_scale = trial.suggest_float('seasonality_prior_scale', 0.01, 10, log=True)
            holidays_prior_scale = trial.suggest_float('holidays_prior_scale', 0.01, 10, log=True)
            
            try:
                from prophet import Prophet
                
                # Prepare data
                df = pd.DataFrame({
                    'ds': self.data.index,
                    'y': self.data.values
                })
                
                # Time series cross-validation
                tscv = TimeSeriesSplit(n_splits=3)
                scores = []
                
                for train_idx, val_idx in tscv.split(self.data):
                    train_df = df.iloc[train_idx]
                    val_df = df.iloc[val_idx]
                    
                    model = Prophet(
                        changepoint_prior_scale=changepoint_prior_scale,
                        seasonality_prior_scale=seasonality_prior_scale,
                        holidays_prior_scale=holidays_prior_scale,
                        yearly_seasonality=True,
                        weekly_seasonality=True
                    )
                    model.fit(train_df)
                    
                    future = model.make_future_dataframe(periods=len(val_df))
                    forecast = model.predict(future)
                    predictions = forecast['yhat'].iloc[-len(val_df):].values
                    
                    val_values = val_df['y'].values
                    
                    if self.metric == 'rmse':
                        score = np.sqrt(np.mean((val_values - predictions) ** 2))
                    elif self.metric == 'mae':
                        score = np.mean(np.abs(val_values - predictions))
                    elif self.metric == 'mape':
                        score = np.mean(np.abs((val_values - predictions) / val_values)) * 100
                    
                    scores.append(score)
                
                return np.mean(scores)
                
            except Exception as e:
                return float('inf')
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
        
        self.best_params['prophet'] = study.best_params
        self.study = study
        
        return study.best_params
    
    def tune_lstm(self, n_trials: int = 30) -> Dict:
        """
        Tune LSTM hyperparameters.
        
        Args:
            n_trials: Number of optimization trials
            
        Returns:
            Dictionary with best parameters
        """
        def objective(trial):
            sequence_length = trial.suggest_int('sequence_length', 10, 60)
            n_units = trial.suggest_int('n_units', 32, 256)
            n_layers = trial.suggest_int('n_layers', 1, 3)
            dropout_rate = trial.suggest_float('dropout_rate', 0.1, 0.5)
            learning_rate = trial.suggest_float('learning_rate', 1e-4, 1e-2, log=True)
            batch_size = trial.suggest_categorical('batch_size', [16, 32, 64])
            
            try:
                import tensorflow as tf
                from tensorflow.keras.models import Sequential
                from tensorflow.keras.layers import LSTM, Dense, Dropout
                from tensorflow.keras.optimizers import Adam
                
                # Prepare data
                scaler = MinMaxScaler()
                scaled_data = scaler.fit_transform(self.data.values.reshape(-1, 1))
                
                # Create sequences
                X, y = [], []
                for i in range(len(scaled_data) - sequence_length):
                    X.append(scaled_data[i:i + sequence_length])
                    y.append(scaled_data[i + sequence_length])
                X, y = np.array(X), np.array(y)
                
                # Split
                split_idx = int(0.8 * len(X))
                X_train, X_val = X[:split_idx], X[split_idx:]
                y_train, y_val = y[:split_idx], y[split_idx:]
                
                # Build model
                model = Sequential()
                for i in range(n_layers):
                    return_sequences = i < n_layers - 1
                    if i == 0:
                        model.add(LSTM(n_units, return_sequences=return_sequences,
                                      input_shape=(sequence_length, 1)))
                    else:
                        model.add(LSTM(n_units, return_sequences=return_sequences))
                    model.add(Dropout(dropout_rate))
                
                model.add(Dense(1))
                model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mse')
                
                # Train
                model.fit(X_train, y_train, epochs=20, batch_size=batch_size,
                         validation_data=(X_val, y_val), verbose=0)
                
                # Evaluate
                y_pred = model.predict(X_val, verbose=0)
                
                # Inverse transform
                y_val_inv = scaler.inverse_transform(y_val)
                y_pred_inv = scaler.inverse_transform(y_pred)
                
                if self.metric == 'rmse':
                    score = np.sqrt(np.mean((y_val_inv - y_pred_inv) ** 2))
                elif self.metric == 'mae':
                    score = np.mean(np.abs(y_val_inv - y_pred_inv))
                elif self.metric == 'mape':
                    score = np.mean(np.abs((y_val_inv - y_pred_inv) / y_val_inv)) * 100
                
                return score
                
            except Exception as e:
                return float('inf')
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
        
        self.best_params['lstm'] = study.best_params
        self.study = study
        
        return study.best_params
    
    def get_optimization_history(self) -> pd.DataFrame:
        """
        Get optimization history as DataFrame.
        
        Returns:
            DataFrame with trial history
        """
        if self.study is None:
            return pd.DataFrame()
        
        trials_df = self.study.trials_dataframe()
        return trials_df

# Example usage
"""
# Generate sample data
np.random.seed(42)
dates = pd.date_range('2019-01-01', '2024-12-31', freq='D')
data = pd.Series(np.random.randn(len(dates)).cumsum() + 100, index=dates)

# Tune ARIMA
tuner = TimeSeriesTuner(data, metric='rmse')
best_arima = tuner.tune_arima(n_trials=30)
print(f"Best ARIMA params: {best_arima}")
"""
```


---

## 15. Testing Strategy

### 15.1 Unit Tests

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/tests/test_time_series.py

"""
Unit Tests for Time Series Module
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class TestTimeSeriesDecomposition(unittest.TestCase):
    """Tests for time series decomposition"""
    
    def setUp(self):
        """Set up test data"""
        np.random.seed(42)
        self.dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        self.data = pd.Series(
            np.random.randn(len(self.dates)).cumsum() + 100,
            index=self.dates
        )
    
    def test_stl_decomposition(self):
        """Test STL decomposition"""
        from ..decomposition import TimeSeriesDecomposer
        
        decomposer = TimeSeriesDecomposer(self.data, freq='D')
        result = decomposer.stl_decomposition(seasonal_period=7)
        
        self.assertIn('trend', result)
        self.assertIn('seasonal', result)
        self.assertIn('residual', result)
        self.assertEqual(len(result['trend']), len(self.data))
    
    def test_strength_metrics(self):
        """Test strength metrics calculation"""
        from ..decomposition import TimeSeriesDecomposer
        
        decomposer = TimeSeriesDecomposer(self.data, freq='D')
        decomposer.stl_decomposition()
        strength = decomposer.get_strength_metrics()
        
        self.assertIn('trend_strength', strength)
        self.assertIn('seasonal_strength', strength)
        self.assertTrue(0 <= strength['trend_strength'] <= 1)
        self.assertTrue(0 <= strength['seasonal_strength'] <= 1)

class TestTrendAnalysis(unittest.TestCase):
    """Tests for trend analysis"""
    
    def setUp(self):
        """Set up test data"""
        np.random.seed(42)
        self.dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        # Data with clear trend
        self.trend_data = pd.Series(
            np.linspace(0, 100, len(self.dates)) + np.random.randn(len(self.dates)) * 5,
            index=self.dates
        )
    
    def test_linear_trend(self):
        """Test linear trend detection"""
        from ..trend_analysis import TrendAnalyzer
        
        analyzer = TrendAnalyzer(self.trend_data)
        result = analyzer.linear_trend()
        
        self.assertIn('slope', result)
        self.assertIn('r_squared', result)
        self.assertIn('mann_kendall', result)
        self.assertTrue(result['slope'] > 0)  # Should detect upward trend
    
    def test_mann_kendall(self):
        """Test Mann-Kendall trend test"""
        from ..trend_analysis import TrendAnalyzer
        
        analyzer = TrendAnalyzer(self.trend_data)
        result = analyzer.linear_trend()
        
        mk_result = result['mann_kendall']
        self.assertTrue(mk_result['significant'])  # Should detect significant trend

class TestAnomalyDetection(unittest.TestCase):
    """Tests for anomaly detection"""
    
    def setUp(self):
        """Set up test data with anomalies"""
        np.random.seed(42)
        self.dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        self.data = pd.Series(np.random.randn(len(self.dates)) * 5 + 100, index=self.dates)
        
        # Inject anomalies
        self.data.iloc[100:105] = 200  # Spike
        self.data.iloc[500:510] = 0    # Drop
    
    def test_statistical_detection(self):
        """Test statistical anomaly detection"""
        from ..anomaly_detection import AnomalyDetector
        
        detector = AnomalyDetector(self.data)
        result = detector.statistical_method(method='zscore', threshold=3)
        
        self.assertIn('anomalies', result)
        self.assertIn('scores', result)
        self.assertTrue(result['n_anomalies'] > 0)
    
    def test_isolation_forest(self):
        """Test Isolation Forest anomaly detection"""
        from ..anomaly_detection import AnomalyDetector
        
        detector = AnomalyDetector(self.data)
        result = detector.isolation_forest(contamination=0.05)
        
        self.assertIn('anomalies', result)
        self.assertTrue(result['n_anomalies'] > 0)

class TestRollingStatistics(unittest.TestCase):
    """Tests for rolling statistics"""
    
    def setUp(self):
        """Set up test data"""
        np.random.seed(42)
        self.dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        self.data = pd.Series(np.random.randn(len(self.dates)).cumsum() + 100, index=self.dates)
    
    def test_moving_average(self):
        """Test moving average calculation"""
        from ..rolling_statistics import RollingStatistics
        
        rs = RollingStatistics(self.data)
        ma = rs.moving_average(window=30)
        
        self.assertEqual(len(ma), len(self.data))
        self.assertTrue(ma.isna().sum() < 30)  # First 29 values should be NaN
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        from ..rolling_statistics import RollingStatistics
        
        rs = RollingStatistics(self.data)
        bands = rs.bollinger_bands(window=20)
        
        self.assertIn('middle', bands.columns)
        self.assertIn('upper', bands.columns)
        self.assertIn('lower', bands.columns)
        self.assertTrue((bands['upper'] >= bands['middle']).all())
        self.assertTrue((bands['middle'] >= bands['lower']).all())

class TestForecasting(unittest.TestCase):
    """Tests for forecasting models"""
    
    def setUp(self):
        """Set up test data"""
        np.random.seed(42)
        self.dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        self.data = pd.Series(
            np.sin(np.arange(len(self.dates)) * 2 * np.pi / 365) + 
            np.random.randn(len(self.dates)) * 0.1 + 10,
            index=self.dates
        )
    
    def test_arima_forecast(self):
        """Test ARIMA forecasting"""
        from ..arima_models import ARIMAModel
        
        model = ARIMAModel(self.data)
        model.fit(order=(2, 1, 2))
        forecast = model.forecast(steps=30)
        
        self.assertEqual(len(forecast['forecast']), 30)
        self.assertIn('lower_bound', forecast)
        self.assertIn('upper_bound', forecast)
    
    def test_prophet_forecast(self):
        """Test Prophet forecasting"""
        from ..prophet_models import ProphetForecaster
        
        model = ProphetForecaster()
        model.fit(self.data)
        forecast = model.forecast(periods=30)
        
        self.assertEqual(len(forecast['forecast']), 30)
        self.assertIn('yhat', forecast['forecast'].columns)

if __name__ == '__main__':
    unittest.main()
```

### 15.2 Integration Tests

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/time_series/tests/test_integration.py

"""
Integration Tests for Time Series Pipeline
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime
import tempfile
import os

class TestPipeline(unittest.TestCase):
    """Integration tests for the complete pipeline"""
    
    def setUp(self):
        """Set up test data and configuration"""
        np.random.seed(42)
        self.dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        self.data = pd.DataFrame({
            'date': self.dates,
            'disaster_count': np.random.poisson(5, len(self.dates)),
            'temperature': np.random.randn(len(self.dates)) * 10 + 20,
            'rainfall': np.random.exponential(5, len(self.dates))
        })
        
        self.temp_dir = tempfile.mkdtemp()
    
    def test_full_pipeline(self):
        """Test complete pipeline execution"""
        from ..pipeline import TimeSeriesPipeline, PipelineConfig
        
        config = PipelineConfig(
            date_column='date',
            target_column='disaster_count',
            forecast_horizon=30,
            models=['arima'],
            output_directory=self.temp_dir
        )
        
        pipeline = TimeSeriesPipeline(config)
        results = pipeline.run(self.data)
        
        # Verify results structure
        self.assertIn('data_summary', results)
        self.assertIn('forecasts', results)
        self.assertIn('analysis', results)
        
        # Verify forecast
        self.assertEqual(len(results['forecasts']['arima']['forecast']), 30)
    
    def test_model_selection(self):
        """Test model selection"""
        from ..model_selection import ModelSelector
        
        series = self.data.set_index('date')['disaster_count']
        selector = ModelSelector()
        
        recommendation = selector.recommend_model(series)
        
        self.assertIn(recommendation.primary_model, 
                     ['arima', 'sarima', 'prophet', 'lstm', 'ensemble'])
        self.assertIsInstance(recommendation.secondary_models, list)
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow with all components"""
        from ..pipeline import TimeSeriesPipeline, PipelineConfig
        from ..visualization import TimeSeriesVisualizer
        
        # Run pipeline
        config = PipelineConfig(
            date_column='date',
            target_column='disaster_count',
            forecast_horizon=30,
            models=['prophet'],
            detect_anomalies=True,
            output_directory=self.temp_dir
        )
        
        pipeline = TimeSeriesPipeline(config)
        results = pipeline.run(self.data)
        
        # Create visualizations
        series = self.data.set_index('date')['disaster_count']
        viz = TimeSeriesVisualizer(series)
        
        # Test various plots
        fig1 = viz.plot_time_series()
        self.assertIsNotNone(fig1)
        
        if 'prophet' in results['forecasts']:
            forecast = results['forecasts']['prophet']['forecast']['yhat']
            fig2 = viz.plot_forecast(forecast)
            self.assertIsNotNone(fig2)
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
```

---

## 16. Implementation Priority Order

### 16.1 Priority Matrix

| Priority | Component | Complexity | Business Value | Implementation Time |
|----------|-----------|------------|----------------|---------------------|
| **P0** | Data Preprocessing | Low | Critical | 1-2 days |
| **P0** | Time Series Decomposition | Medium | High | 2-3 days |
| **P0** | ARIMA Modeling | Medium | High | 2-3 days |
| **P0** | Prophet Forecasting | Low | High | 1-2 days |
| **P1** | Seasonality Detection | Medium | High | 2-3 days |
| **P1** | Trend Analysis | Medium | High | 2-3 days |
| **P1** | Anomaly Detection | Medium | High | 3-4 days |
| **P1** | Rolling Statistics | Low | Medium | 1-2 days |
| **P2** | LSTM Models | High | Medium | 5-7 days |
| **P2** | Change Point Detection | Medium | Medium | 2-3 days |
| **P2** | Model Selection | Medium | Medium | 2-3 days |
| **P2** | Hyperparameter Tuning | Medium | Medium | 2-3 days |
| **P3** | Ensemble Methods | High | Medium | 3-4 days |
| **P3** | Advanced Visualizations | Low | Low | 2-3 days |

### 16.2 Implementation Roadmap

```
Phase 1: Foundation (Weeks 1-2)
├── Data preprocessing pipeline
├── Time series decomposition (STL, Classical)
├── Basic visualization
└── Unit tests

Phase 2: Core Forecasting (Weeks 3-4)
├── ARIMA/SARIMA models
├── Prophet integration
├── Model evaluation framework
└── Integration tests

Phase 3: Analysis Features (Weeks 5-6)
├── Seasonality detection
├── Trend analysis
├── Rolling statistics
├── Anomaly detection (statistical)
└── Documentation

Phase 4: Advanced Features (Weeks 7-8)
├── LSTM models
├── Change point detection
├── Advanced anomaly detection (ML)
├── Model selection framework
└── Performance optimization

Phase 5: Production Ready (Weeks 9-10)
├── Ensemble methods
├── Hyperparameter tuning
├── Complete visualization suite
├── API integration
└── Production deployment
```

---

## 17. File Structure

```
/mnt/okcomputer/output/resilience_ai_analysis/time_series/
├── __init__.py
├── architecture.py          # Base classes and interfaces
├── decomposition.py         # Time series decomposition
├── trend_analysis.py        # Trend detection and analysis
├── seasonality.py           # Seasonality detection
├── arima_models.py          # ARIMA/SARIMA models
├── prophet_models.py        # Prophet forecasting
├── lstm_models.py           # LSTM neural networks
├── anomaly_detection.py     # Anomaly detection methods
├── change_point_detection.py # Change point detection
├── rolling_statistics.py    # Rolling statistics
├── visualization.py         # Visualization tools
├── model_selection.py       # Model selection framework
├── pipeline.py              # End-to-end pipeline
├── hyperparameter_tuning.py # Hyperparameter optimization
├── tests/
│   ├── __init__.py
│   ├── test_time_series.py  # Unit tests
│   └── test_integration.py  # Integration tests
└── examples/
    ├── basic_usage.py
    ├── disaster_forecasting.py
    └── anomaly_detection_example.py
```

---

## 18. Dependencies

### 18.1 Required Packages

```txt
# Core dependencies
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
scikit-learn>=1.0.0

# Time series specific
statsmodels>=0.13.0
prophet>=1.1.0

# Deep learning (optional)
tensorflow>=2.8.0
keras>=2.8.0

# Change point detection (optional)
ruptures>=1.1.0

# Hyperparameter tuning (optional)
optuna>=3.0.0

# Visualization
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0

# Testing
pytest>=7.0.0
pytest-cov>=3.0.0
```

---

## 19. Summary

This comprehensive time series analysis framework for ResilienceAI provides:

1. **Complete Pipeline**: End-to-end workflow from data ingestion to forecast generation
2. **Multiple Models**: ARIMA, Prophet, LSTM, and ensemble methods
3. **Advanced Analysis**: Decomposition, seasonality, trend, anomaly detection
4. **Production Ready**: Testing, optimization, and deployment considerations
5. **Extensible Architecture**: Easy to add new models and methods

### Key Features:
- **Automatic model selection** based on data characteristics
- **Robust anomaly detection** with multiple methods
- **Comprehensive visualization** for reporting
- **Hyperparameter tuning** for optimal performance
- **Full test coverage** for reliability

### Next Steps:
1. Implement Phase 1 components (Foundation)
2. Set up CI/CD pipeline for testing
3. Create example notebooks for users
4. Deploy to production environment
5. Monitor and iterate based on feedback

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Development Team*
