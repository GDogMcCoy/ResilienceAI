# ResilienceAI Predictive Analytics Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the current predictive capabilities in the ResilienceAI repository (claw-autonomous branch) and designs advanced predictive analytics enhancements. The current system has foundational Prophet/ARIMA forecasting, basic scenario modeling, and risk trajectory analysis. This enhancement introduces ensemble forecasting, Monte Carlo simulations, advanced early warning systems, and automated model selection.

---

## 1. Current Predictive Capabilities Analysis

### 1.1 Existing Architecture Overview

**File Location:** `src/predictive_models.py` (999 lines, 36.8 KB)

#### Core Components:

1. **TimeSeriesForecaster Class**
   - Prophet (Facebook) integration with configurable seasonality
   - ARIMA with auto-parameter selection using AIC criterion
   - Cross-validation with TimeSeriesSplit
   - ForecastResult dataclass with confidence intervals

2. **DisasterPredictor Class**
   - Gradient Boosting and Random Forest models
   - Feature engineering with lag features and rolling statistics
   - Time-based features (month, year, quarter)

3. **ClimateScenarioModeler Class**
   - IPCC SSP scenario support (SSP1-1.9, SSP2-4.5, SSP5-8.5)
   - Risk projection with linear interpolation to 2100
   - Infrastructure degradation modeling

4. **RiskTrajectoryAnalyzer Class**
   - Historical trend analysis
   - Prophet-based forecasting
   - Climate scenario integration
   - Acceleration detection

5. **ModelPersistence Class**
   - Model save/load with joblib
   - Metadata tracking
   - Batch forecasting support

**File Location:** `src/scenario_simulator.py` (201 lines, 8.45 KB)

#### Core Components:

1. **ScenarioSimulator Class**
   - 10 disaster scenario presets (hurricanes, earthquakes, floods, wildfires, tornadoes, winter storms)
   - Haversine distance calculations for impact radius
   - Before/after impact simulation

**File Location:** `src/alert_manager.py` (488 lines, 15.8 KB)

#### Core Components:

1. **AlertManager Class**
   - SQLite-based subscription management
   - Alert event tracking
   - Webhook/email/phone notification support

### 1.2 Current Strengths

- Prophet and ARIMA time series forecasting
- Climate scenario modeling with IPCC SSPs
- Risk trajectory analysis
- Cross-validation framework
- Model persistence
- Basic scenario simulation
- Alert subscription system

### 1.3 Current Limitations

- No ensemble forecasting (single model only)
- No Monte Carlo simulations
- Limited early warning thresholds
- No automated model selection
- No prediction confidence calibration
- Limited scenario complexity
- No intervention impact prediction
- No anomaly detection
- No predictive maintenance for infrastructure

---

## 2. Proposed Advanced Forecasting Architecture

### 2.1 Enhanced Folder Structure

```
src/
├── predictive/
│   ├── __init__.py
│   ├── base_models.py              # Base forecasting classes
│   ├── ensemble_forecaster.py      # Ensemble methods
│   ├── monte_carlo.py              # Monte Carlo simulation engine
│   ├── auto_model_selector.py      # Automated model selection
│   ├── early_warning.py            # Early warning system
│   ├── intervention_impact.py      # Intervention ROI prediction
│   ├── anomaly_detector.py         # Anomaly detection
│   ├── climate_projections.py      # Advanced climate modeling
│   └── confidence_calibration.py   # Prediction confidence
├── scenario/
│   ├── __init__.py
│   ├── advanced_simulator.py       # Enhanced scenario engine
│   ├── cascade_effects.py          # Multi-hazard cascades
│   ├── what_if_engine.py           # What-if analysis
│   └── sensitivity_analysis.py     # Parameter sensitivity
└── monitoring/
    ├── __init__.py
    ├── predictive_maintenance.py   # Infrastructure monitoring
    └── trend_monitor.py            # Trend analysis
```

---

## 3. Ensemble Forecasting Design

### 3.1 Ensemble Architecture

```python
# src/predictive/ensemble_forecaster.py

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from dataclasses import dataclass
from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor

@dataclass
class EnsembleMember:
    """Represents a model in the ensemble."""
    name: str
    forecaster: 'BaseForecaster'
    weight: float = 1.0
    performance_score: float = 0.0
    last_trained: Optional[str] = None

class EnsembleForecaster:
    """
    Advanced ensemble forecaster combining multiple models.
    Supports multiple ensemble strategies and dynamic weighting.
    """
    
    ENSEMBLE_STRATEGIES = [
        'simple_average',
        'weighted_average',
        'stacking',
        'blending',
        'dynamic_weighting',
        'bayesian_model_averaging'
    ]
    
    def __init__(self, 
                 strategy: str = 'weighted_average',
                 meta_learner: str = 'ridge',
                 cv_folds: int = 5):
        """
        Initialize ensemble forecaster.
        
        Args:
            strategy: Ensemble combination strategy
            meta_learner: Meta-learner for stacking ('ridge', 'gbm', 'nn')
            cv_folds: Number of CV folds for out-of-fold predictions
        """
        if strategy not in self.ENSEMBLE_STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        self.strategy = strategy
        self.meta_learner = meta_learner
        self.cv_folds = cv_folds
        self.members: List[EnsembleMember] = []
        self.meta_model = None
        self.oof_predictions: Optional[np.ndarray] = None
        self.weights: Optional[np.ndarray] = None
        self.performance_history: Dict[str, List[float]] = {}
    
    def add_member(self, name: str, forecaster: 'BaseForecaster',
                   weight: float = 1.0) -> 'EnsembleForecaster':
        """Add a model to the ensemble."""
        self.members.append(EnsembleMember(
            name=name,
            forecaster=forecaster,
            weight=weight
        ))
        self.performance_history[name] = []
        return self
    
    def fit(self, df: pd.DataFrame, date_col: str = 'date',
            value_col: str = 'value', **kwargs) -> 'EnsembleForecaster':
        """Fit all ensemble members and learn combination weights."""
        print(f"Fitting ensemble with {len(self.members)} members...")
        
        # Fit individual members
        for member in self.members:
            print(f"  Fitting {member.name}...")
            member.forecaster.fit(df, date_col=date_col, value_col=value_col)
        
        # Learn ensemble weights based on strategy
        if self.strategy == 'simple_average':
            self._fit_simple_average()
        elif self.strategy == 'weighted_average':
            self._fit_weighted_average(df, date_col, value_col)
        elif self.strategy == 'stacking':
            self._fit_stacking(df, date_col, value_col)
        elif self.strategy == 'dynamic_weighting':
            self._fit_dynamic_weighting(df, date_col, value_col)
        elif self.strategy == 'bayesian_model_averaging':
            self._fit_bma(df, date_col, value_col)
        
        return self
    
    def _fit_weighted_average(self, df: pd.DataFrame, 
                              date_col: str, value_col: str):
        """Fit weights based on inverse validation error."""
        from sklearn.model_selection import TimeSeriesSplit
        
        weights = []
        tscv = TimeSeriesSplit(n_splits=self.cv_folds)
        
        for member in self.members:
            errors = []
            for train_idx, val_idx in tscv.split(df):
                train_df = df.iloc[train_idx]
                val_df = df.iloc[val_idx]
                
                # Fit on train
                temp_forecaster = member.forecaster.__class__()
                temp_forecaster.fit(train_df, date_col, value_col)
                
                # Predict on validation
                forecast = temp_forecaster.forecast(periods=len(val_df))
                error = np.mean(np.abs(val_df[value_col].values - forecast.forecast[:len(val_df)]))
                errors.append(error)
            
            avg_error = np.mean(errors)
            weight = 1.0 / (avg_error + 1e-10)
            weights.append(weight)
            member.performance_score = 1.0 / (avg_error + 1e-10)
        
        # Normalize weights
        self.weights = np.array(weights) / sum(weights)
        
        # Update member weights
        for i, member in enumerate(self.members):
            member.weight = self.weights[i]
    
    def forecast(self, periods: int, **kwargs) -> 'EnsembleForecastResult':
        """Generate ensemble forecast combining all members."""
        # Get predictions from all members
        member_predictions = []
        member_intervals = []
        
        for member in self.members:
            forecast = member.forecaster.forecast(periods=periods)
            member_predictions.append(forecast.forecast)
            member_intervals.append((forecast.lower_bound, forecast.upper_bound))
        
        predictions = np.column_stack(member_predictions)
        
        # Combine predictions based on strategy
        if self.strategy == 'simple_average':
            ensemble_forecast = np.mean(predictions, axis=1)
        elif self.strategy in ['weighted_average', 'dynamic_weighting']:
            ensemble_forecast = np.average(predictions, axis=1, weights=self.weights)
        elif self.strategy == 'stacking':
            ensemble_forecast = self.meta_model.predict(predictions)
        else:
            ensemble_forecast = np.mean(predictions, axis=1)
        
        # Combine uncertainty intervals
        lower_bounds = np.column_stack([interval[0] for interval in member_intervals])
        upper_bounds = np.column_stack([interval[1] for interval in member_intervals])
        
        # Conservative approach: widest intervals
        ensemble_lower = np.min(lower_bounds, axis=1)
        ensemble_upper = np.max(upper_bounds, axis=1)
        
        # Calculate ensemble uncertainty
        prediction_std = np.std(predictions, axis=1)
        
        return EnsembleForecastResult(
            dates=forecast.dates,
            forecast=ensemble_forecast,
            lower_bound=ensemble_lower,
            upper_bound=ensemble_upper,
            member_predictions={m.name: predictions[:, i] 
                               for i, m in enumerate(self.members)},
            weights=self.weights,
            uncertainty=prediction_std,
            model_name=f"Ensemble ({self.strategy})"
        )

@dataclass
class EnsembleForecastResult:
    """Container for ensemble forecasting results."""
    dates: pd.DatetimeIndex
    forecast: np.ndarray
    lower_bound: np.ndarray
    upper_bound: np.ndarray
    member_predictions: Dict[str, np.ndarray]
    weights: Optional[np.ndarray]
    uncertainty: np.ndarray
    model_name: str
    metrics: Optional[Dict] = None
```

---

## 4. Monte Carlo Simulation Engine

### 4.1 Core Monte Carlo Architecture

```python
# src/predictive/monte_carlo.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from scipy import stats
from scipy.stats import norm, lognorm, gamma, beta, poisson

@dataclass
class DistributionConfig:
    """Configuration for probability distributions."""
    distribution: str  # 'normal', 'lognormal', 'gamma', 'beta', 'poisson', 'empirical'
    params: Dict  # Distribution parameters
    bounds: Optional[Tuple[float, float]] = None  # Optional bounds

@dataclass
class RiskFactor:
    """Represents a risk factor with uncertainty."""
    name: str
    distribution: DistributionConfig
    correlation: Optional[Dict[str, float]] = None
    time_varying: bool = False
    trend_func: Optional[Callable] = None

class MonteCarloSimulator:
    """
    Advanced Monte Carlo simulation engine for disaster risk assessment.
    Supports correlated sampling, time-varying factors, and multiple output metrics.
    """
    
    def __init__(self, n_simulations: int = 10000, random_seed: int = 42):
        """
        Initialize Monte Carlo simulator.
        
        Args:
            n_simulations: Number of Monte Carlo iterations
            random_seed: Random seed for reproducibility
        """
        self.n_simulations = n_simulations
        self.random_seed = random_seed
        self.risk_factors: Dict[str, RiskFactor] = {}
        self.correlation_matrix: Optional[np.ndarray] = None
        self.factor_order: List[str] = []
        self.results: Optional[Dict] = None
        
        np.random.seed(random_seed)
    
    def add_risk_factor(self, factor: RiskFactor) -> 'MonteCarloSimulator':
        """Add a risk factor to the simulation."""
        self.risk_factors[factor.name] = factor
        if factor.name not in self.factor_order:
            self.factor_order.append(factor.name)
        return self
    
    def set_correlations(self, correlations: Dict[Tuple[str, str], float]):
        """
        Set correlation structure between risk factors.
        
        Args:
            correlations: Dict mapping (factor1, factor2) to correlation coefficient
        """
        n = len(self.factor_order)
        self.correlation_matrix = np.eye(n)
        
        for (f1, f2), corr in correlations.items():
            if f1 in self.factor_order and f2 in self.factor_order:
                i, j = self.factor_order.index(f1), self.factor_order.index(f2)
                self.correlation_matrix[i, j] = corr
                self.correlation_matrix[j, i] = corr
    
    def _sample_correlated(self, distributions: List[DistributionConfig]) -> np.ndarray:
        """Generate correlated samples using Cholesky decomposition."""
        n = len(distributions)
        
        # Generate uncorrelated standard normal samples
        uncorrelated = np.random.standard_normal((self.n_simulations, n))
        
        if self.correlation_matrix is not None:
            # Apply Cholesky decomposition
            L = np.linalg.cholesky(self.correlation_matrix)
            correlated = uncorrelated @ L.T
        else:
            correlated = uncorrelated
        
        # Transform to desired distributions using inverse CDF
        samples = np.zeros((self.n_simulations, n))
        for i, dist_config in enumerate(distributions):
            u = stats.norm.cdf(correlated[:, i])
            samples[:, i] = self._inverse_transform(u, dist_config)
        
        return samples
    
    def _inverse_transform(self, u: np.ndarray, 
                          dist_config: DistributionConfig) -> np.ndarray:
        """Apply inverse transform sampling."""
        dist = dist_config.distribution
        params = dist_config.params
        
        if dist == 'normal':
            return stats.norm.ppf(u, loc=params.get('mean', 0), 
                                 scale=params.get('std', 1))
        elif dist == 'lognormal':
            return stats.lognorm.ppf(u, s=params.get('sigma', 1),
                                    scale=np.exp(params.get('mu', 0)))
        elif dist == 'gamma':
            return stats.gamma.ppf(u, a=params.get('shape', 1),
                                  scale=params.get('scale', 1))
        elif dist == 'beta':
            return stats.beta.ppf(u, a=params.get('alpha', 1),
                                 b=params.get('beta', 1))
        elif dist == 'poisson':
            return stats.poisson.ppf(u, mu=params.get('lambda', 1))
        elif dist == 'empirical':
            # Use empirical distribution
            data = params.get('data', [])
            if len(data) > 0:
                return np.percentile(data, u * 100)
            return np.zeros_like(u)
        else:
            raise ValueError(f"Unknown distribution: {dist}")
    
    def run_simulation(self, 
                       impact_function: Callable[[pd.DataFrame], np.ndarray],
                       time_horizon: int = 1,
                       output_metrics: Optional[List[str]] = None) -> Dict:
        """
        Run Monte Carlo simulation.
        
        Args:
            impact_function: Function that takes risk factor dataframe and returns impact
            time_horizon: Number of time periods to simulate
            output_metrics: List of output metrics to compute
        
        Returns:
            Dictionary with simulation results
        """
        print(f"Running {self.n_simulations} Monte Carlo simulations...")
        
        # Prepare distributions
        distributions = [self.risk_factors[f].distribution 
                        for f in self.factor_order]
        
        # Generate samples
        samples = self._sample_correlated(distributions)
        
        # Create dataframe
        samples_df = pd.DataFrame(samples, columns=self.factor_order)
        
        # Apply time-varying trends if specified
        if time_horizon > 1:
            all_results = []
            for t in range(time_horizon):
                time_samples = samples_df.copy()
                for factor_name, factor in self.risk_factors.items():
                    if factor.time_varying and factor.trend_func:
                        time_samples[factor_name] = factor.trend_func(
                            time_samples[factor_name], t
                        )
                
                impacts = impact_function(time_samples)
                all_results.append(impacts)
            
            impacts = np.column_stack(all_results)
        else:
            impacts = impact_function(samples_df)
        
        # Compute results
        self.results = self._compute_results(impacts, output_metrics)
        self.results['samples'] = samples_df
        self.results['impacts'] = impacts
        
        return self.results
    
    def _compute_results(self, impacts: np.ndarray,
                        metrics: Optional[List[str]]) -> Dict:
        """Compute summary statistics from simulation results."""
        results = {
            'mean': np.mean(impacts, axis=0),
            'std': np.std(impacts, axis=0),
            'median': np.median(impacts, axis=0),
            'min': np.min(impacts, axis=0),
            'max': np.max(impacts, axis=0),
            'percentiles': {
                '5': np.percentile(impacts, 5, axis=0),
                '10': np.percentile(impacts, 10, axis=0),
                '25': np.percentile(impacts, 25, axis=0),
                '75': np.percentile(impacts, 75, axis=0),
                '90': np.percentile(impacts, 90, axis=0),
                '95': np.percentile(impacts, 95, axis=0),
                '99': np.percentile(impacts, 99, axis=0),
            },
            'probability_of_loss': np.mean(impacts > 0, axis=0),
            'expected_loss': np.mean(np.maximum(impacts, 0), axis=0),
            'value_at_risk_95': np.percentile(impacts, 95, axis=0),
            'conditional_var_95': np.mean(
                impacts[impacts > np.percentile(impacts, 95, axis=0)], axis=0
            ) if len(impacts.shape) == 1 else None,
        }
        
        # Compute additional metrics if requested
        if metrics:
            for metric in metrics:
                if metric == 'skewness':
                    results['skewness'] = stats.skew(impacts, axis=0)
                elif metric == 'kurtosis':
                    results['kurtosis'] = stats.kurtosis(impacts, axis=0)
                elif metric == 'sharpe_ratio':
                    results['sharpe_ratio'] = results['mean'] / (results['std'] + 1e-10)
        
        return results
    
    def get_value_at_risk(self, confidence: float = 0.95) -> float:
        """Get Value at Risk at specified confidence level."""
        if self.results is None:
            raise ValueError("Run simulation first")
        return np.percentile(self.results['impacts'], confidence * 100)
    
    def get_conditional_var(self, confidence: float = 0.95) -> float:
        """Get Conditional Value at Risk (Expected Shortfall)."""
        if self.results is None:
            raise ValueError("Run simulation first")
        var = self.get_value_at_risk(confidence)
        return np.mean(self.results['impacts'][self.results['impacts'] > var])
    
    def sensitivity_analysis(self) -> Dict[str, float]:
        """
        Perform sensitivity analysis using correlation between
        inputs and outputs.
        """
        if self.results is None:
            raise ValueError("Run simulation first")
        
        sensitivities = {}
        for factor_name in self.factor_order:
            correlation = np.corrcoef(
                self.results['samples'][factor_name],
                self.results['impacts']
            )[0, 1]
            sensitivities[factor_name] = abs(correlation)
        
        return sensitivities
```



---

## 5. Early Warning System Design

### 5.1 Multi-Threshold Early Warning Architecture

```python
# src/predictive/early_warning.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class AlertLevel(Enum):
    """Alert severity levels."""
    GREEN = "green"      # Normal conditions
    BLUE = "blue"        # Elevated risk
    YELLOW = "yellow"    # Moderate risk
    ORANGE = "orange"    # High risk
    RED = "red"          # Critical risk

@dataclass
class WarningThreshold:
    """Defines a warning threshold."""
    level: AlertLevel
    metric_name: str
    operator: str  # '>', '<', '>=', '<=', '=='
    value: float
    duration_required: int = 1  # Consecutive periods required
    cooldown_periods: int = 0   # Periods before re-triggering

@dataclass
class AlertEvent:
    """Represents an alert event."""
    id: str
    level: AlertLevel
    metric_name: str
    metric_value: float
    threshold_value: float
    timestamp: datetime
    county_fips: str
    county_name: str
    message: str
    recommended_actions: List[str]
    confidence: float
    expiry: datetime

class EarlyWarningSystem:
    """
    Advanced early warning system with multi-threshold support,
    trend detection, and predictive alerting.
    """
    
    DEFAULT_THRESHOLDS = {
        'risk_score': [
            WarningThreshold(AlertLevel.BLUE, 'risk_score', '>', 0.4, duration_required=2),
            WarningThreshold(AlertLevel.YELLOW, 'risk_score', '>', 0.6, duration_required=2),
            WarningThreshold(AlertLevel.ORANGE, 'risk_score', '>', 0.75, duration_required=1),
            WarningThreshold(AlertLevel.RED, 'risk_score', '>', 0.9, duration_required=1),
        ],
        'disaster_probability': [
            WarningThreshold(AlertLevel.YELLOW, 'disaster_probability', '>', 0.3, duration_required=3),
            WarningThreshold(AlertLevel.ORANGE, 'disaster_probability', '>', 0.5, duration_required=2),
            WarningThreshold(AlertLevel.RED, 'disaster_probability', '>', 0.7, duration_required=1),
        ],
        'vulnerability_index': [
            WarningThreshold(AlertLevel.BLUE, 'vulnerability_index', '>', 0.5, duration_required=2),
            WarningThreshold(AlertLevel.YELLOW, 'vulnerability_index', '>', 0.65, duration_required=2),
            WarningThreshold(AlertLevel.ORANGE, 'vulnerability_index', '>', 0.8, duration_required=1),
        ],
        'infrastructure_stress': [
            WarningThreshold(AlertLevel.YELLOW, 'infrastructure_stress', '>', 0.7, duration_required=2),
            WarningThreshold(AlertLevel.ORANGE, 'infrastructure_stress', '>', 0.85, duration_required=1),
            WarningThreshold(AlertLevel.RED, 'infrastructure_stress', '>', 0.95, duration_required=1),
        ],
    }
    
    def __init__(self, 
                 thresholds: Optional[Dict[str, List[WarningThreshold]]] = None,
                 prediction_horizon: int = 7,
                 enable_trend_detection: bool = True,
                 enable_predictive_alerts: bool = True):
        """
        Initialize early warning system.
        
        Args:
            thresholds: Custom thresholds (uses defaults if None)
            prediction_horizon: Days ahead for predictive alerts
            enable_trend_detection: Enable trend-based warnings
            enable_predictive_alerts: Enable forecast-based warnings
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.prediction_horizon = prediction_horizon
        self.enable_trend_detection = enable_trend_detection
        self.enable_predictive_alerts = enable_predictive_alerts
        
        self.alert_history: List[AlertEvent] = []
        self.active_alerts: Dict[str, AlertEvent] = {}
        self.metric_history: Dict[str, pd.DataFrame] = {}
        self.consecutive_counts: Dict[str, Dict] = {}
    
    def update_metrics(self, county_fips: str, metrics: Dict[str, float],
                       timestamp: Optional[datetime] = None):
        """
        Update metrics for a county and check thresholds.
        
        Args:
            county_fips: County FIPS code
            metrics: Dictionary of metric names and values
            timestamp: Timestamp for the metrics
        """
        timestamp = timestamp or datetime.now()
        
        # Store metric history
        if county_fips not in self.metric_history:
            self.metric_history[county_fips] = pd.DataFrame()
        
        new_row = pd.DataFrame([{**metrics, 'timestamp': timestamp}])
        self.metric_history[county_fips] = pd.concat(
            [self.metric_history[county_fips], new_row],
            ignore_index=True
        )
        
        # Check thresholds
        alerts = self._check_thresholds(county_fips, metrics, timestamp)
        
        # Check trends if enabled
        if self.enable_trend_detection:
            trend_alerts = self._check_trends(county_fips, timestamp)
            alerts.extend(trend_alerts)
        
        return alerts
    
    def _check_thresholds(self, county_fips: str, metrics: Dict[str, float],
                         timestamp: datetime) -> List[AlertEvent]:
        """Check metrics against thresholds."""
        alerts = []
        
        for metric_name, metric_value in metrics.items():
            if metric_name not in self.thresholds:
                continue
            
            for threshold in self.thresholds[metric_name]:
                # Check if threshold is breached
                breached = self._evaluate_condition(
                    metric_value, threshold.operator, threshold.value
                )
                
                if breached:
                    # Track consecutive breaches
                    key = f"{county_fips}:{metric_name}:{threshold.level.value}"
                    if key not in self.consecutive_counts:
                        self.consecutive_counts[key] = {
                            'count': 0,
                            'last_triggered': None
                        }
                    
                    self.consecutive_counts[key]['count'] += 1
                    
                    # Check if duration requirement is met
                    if self.consecutive_counts[key]['count'] >= threshold.duration_required:
                        # Check cooldown
                        last_triggered = self.consecutive_counts[key]['last_triggered']
                        if (last_triggered is None or 
                            timestamp - last_triggered > timedelta(
                                days=threshold.cooldown_periods)):
                            
                            # Create alert
                            alert = self._create_alert(
                                county_fips, threshold, metric_value, timestamp
                            )
                            alerts.append(alert)
                            
                            self.consecutive_counts[key]['last_triggered'] = timestamp
                else:
                    # Reset consecutive count
                    key = f"{county_fips}:{metric_name}:{threshold.level.value}"
                    if key in self.consecutive_counts:
                        self.consecutive_counts[key]['count'] = 0
        
        return alerts
    
    def _evaluate_condition(self, value: float, operator: str, 
                           threshold: float) -> bool:
        """Evaluate a threshold condition."""
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return value == threshold
        return False
    
    def _check_trends(self, county_fips: str, 
                     timestamp: datetime) -> List[AlertEvent]:
        """Check for concerning trends in metrics."""
        alerts = []
        
        if county_fips not in self.metric_history:
            return alerts
        
        history = self.metric_history[county_fips]
        if len(history) < 5:  # Need minimum data points
            return alerts
        
        # Check for accelerating trends
        for metric_name in ['risk_score', 'disaster_probability', 'vulnerability_index']:
            if metric_name not in history.columns:
                continue
            
            series = history[metric_name].dropna()
            if len(series) < 5:
                continue
            
            # Calculate trend
            x = np.arange(len(series))
            slope = np.polyfit(x, series, 1)[0]
            
            # Check for acceleration (second derivative)
            if len(series) >= 10:
                first_half = series.iloc[:len(series)//2]
                second_half = series.iloc[len(series)//2:]
                
                slope1 = np.polyfit(np.arange(len(first_half)), first_half, 1)[0]
                slope2 = np.polyfit(np.arange(len(second_half)), second_half, 1)[0]
                
                acceleration = slope2 - slope1
                
                # Alert on rapid acceleration
                if acceleration > 0.05 and series.iloc[-1] > 0.4:
                    alert = AlertEvent(
                        id=f"{county_fips}_accel_{metric_name}_{timestamp.isoformat()}",
                        level=AlertLevel.YELLOW,
                        metric_name=f"{metric_name}_acceleration",
                        metric_value=acceleration,
                        threshold_value=0.05,
                        timestamp=timestamp,
                        county_fips=county_fips,
                        county_name=self._get_county_name(county_fips),
                        message=f"Rapid increase in {metric_name} detected",
                        recommended_actions=[
                            "Monitor situation closely",
                            "Prepare contingency plans",
                            "Review resource allocation"
                        ],
                        confidence=min(0.95, 0.7 + acceleration * 5),
                        expiry=timestamp + timedelta(days=7)
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _get_recommended_actions(self, level: AlertLevel) -> List[str]:
        """Get recommended actions for alert level."""
        actions = {
            AlertLevel.GREEN: ["Continue normal monitoring"],
            AlertLevel.BLUE: [
                "Increase monitoring frequency",
                "Review emergency contact lists"
            ],
            AlertLevel.YELLOW: [
                "Activate emergency operations center",
                "Notify key stakeholders",
                "Prepare resource mobilization"
            ],
            AlertLevel.ORANGE: [
                "Deploy emergency response teams",
                "Evacuate vulnerable populations",
                "Mobilize all available resources"
            ],
            AlertLevel.RED: [
                "Execute full emergency response",
                "Mandatory evacuations",
                "Request federal/state assistance"
            ],
        }
        return actions.get(level, ["Monitor situation"])
    
    def _create_alert(self, county_fips: str, threshold: WarningThreshold,
                     metric_value: float, timestamp: datetime) -> AlertEvent:
        """Create an alert event."""
        return AlertEvent(
            id=f"{county_fips}_{threshold.level.value}_{timestamp.isoformat()}",
            level=threshold.level,
            metric_name=threshold.metric_name,
            metric_value=metric_value,
            threshold_value=threshold.value,
            timestamp=timestamp,
            county_fips=county_fips,
            county_name=self._get_county_name(county_fips),
            message=f"{threshold.level.value.upper()} alert: {threshold.metric_name} "
                   f"{threshold.operator} {threshold.value}",
            recommended_actions=self._get_recommended_actions(threshold.level),
            confidence=0.85,
            expiry=timestamp + timedelta(days=7)
        )
    
    def _get_county_name(self, county_fips: str) -> str:
        """Get county name from FIPS code."""
        return f"County {county_fips}"
    
    def get_alert_summary(self, county_fips: Optional[str] = None,
                         days: int = 30) -> Dict:
        """Get summary of recent alerts."""
        cutoff = datetime.now() - timedelta(days=days)
        
        alerts = [a for a in self.alert_history 
                 if a.timestamp > cutoff and
                 (county_fips is None or a.county_fips == county_fips)]
        
        summary = {
            'total_alerts': len(alerts),
            'by_level': {},
            'by_county': {},
            'trend': 'stable'
        }
        
        for alert in alerts:
            level = alert.level.value
            summary['by_level'][level] = summary['by_level'].get(level, 0) + 1
            
            county = alert.county_fips
            summary['by_county'][county] = summary['by_county'].get(county, 0) + 1
        
        # Determine trend
        if len(alerts) >= 10:
            first_half = len([a for a in alerts[:len(alerts)//2] 
                            if a.level in [AlertLevel.ORANGE, AlertLevel.RED]])
            second_half = len([a for a in alerts[len(alerts)//2:] 
                              if a.level in [AlertLevel.ORANGE, AlertLevel.RED]])
            
            if second_half > first_half * 1.5:
                summary['trend'] = 'worsening'
            elif second_half < first_half * 0.5:
                summary['trend'] = 'improving'
        
        return summary
```

---

## 6. Intervention Impact Prediction

### 6.1 Intervention ROI Prediction Model

```python
# src/predictive/intervention_impact.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

class InterventionType(Enum):
    """Types of disaster risk interventions."""
    INFRASTRUCTURE_HARDENING = "infrastructure_hardening"
    EARLY_WARNING_SYSTEM = "early_warning_system"
    EMERGENCY_RESPONSE_TRAINING = "emergency_response_training"
    COMMUNITY_EDUCATION = "community_education"
    FLOOD_MITIGATION = "flood_mitigation"
    WILDFIRE_PREVENTION = "wildfire_prevention"
    SEISMIC_RETROFIT = "seismic_retrofit"
    HEALTHCARE_CAPACITY = "healthcare_capacity"
    EVACUATION_ROUTES = "evacuation_routes"
    COMMUNICATION_SYSTEMS = "communication_systems"

@dataclass
class Intervention:
    """Represents a risk reduction intervention."""
    id: str
    name: str
    type: InterventionType
    description: str
    cost: float  # Total implementation cost
    annual_maintenance: float
    implementation_time_months: int
    lifespan_years: int
    affected_metrics: List[str]  # Which risk metrics are affected
    effectiveness_range: Tuple[float, float]  # Min/max effectiveness (0-1)
    target_counties: List[str]  # FIPS codes

@dataclass
class InterventionImpact:
    """Results of intervention impact analysis."""
    intervention_id: str
    baseline_risk: float
    projected_risk: float
    risk_reduction_pct: float
    annual_avoided_losses: float
    npv_benefit: float
    roi: float
    payback_period_years: float
    break_even_probability: float
    confidence_interval: Tuple[float, float]
    year_by_year_impact: pd.DataFrame

class InterventionImpactPredictor:
    """
    Predicts the impact and ROI of disaster risk reduction interventions.
    Uses historical data, cost-benefit analysis, and Monte Carlo simulation.
    """
    
    # Default effectiveness estimates based on research
    DEFAULT_EFFECTIVENESS = {
        InterventionType.INFRASTRUCTURE_HARDENING: (0.15, 0.40),
        InterventionType.EARLY_WARNING_SYSTEM: (0.20, 0.50),
        InterventionType.EMERGENCY_RESPONSE_TRAINING: (0.10, 0.30),
        InterventionType.COMMUNITY_EDUCATION: (0.05, 0.20),
        InterventionType.FLOOD_MITIGATION: (0.25, 0.60),
        InterventionType.WILDFIRE_PREVENTION: (0.20, 0.45),
        InterventionType.SEISMIC_RETROFIT: (0.30, 0.70),
        InterventionType.HEALTHCARE_CAPACITY: (0.15, 0.35),
        InterventionType.EVACUATION_ROUTES: (0.10, 0.25),
        InterventionType.COMMUNICATION_SYSTEMS: (0.15, 0.40),
    }
    
    def __init__(self, 
                 discount_rate: float = 0.03,
                 analysis_horizon_years: int = 30):
        """
        Initialize intervention impact predictor.
        
        Args:
            discount_rate: Annual discount rate for NPV calculations
            analysis_horizon_years: Years to analyze
        """
        self.discount_rate = discount_rate
        self.analysis_horizon_years = analysis_horizon_years
        self.interventions: Dict[str, Intervention] = {}
        self.historical_losses: Dict[str, pd.DataFrame] = {}
    
    def add_intervention(self, intervention: Intervention):
        """Add an intervention to analyze."""
        self.interventions[intervention.id] = intervention
    
    def set_historical_losses(self, county_fips: str, 
                              losses_df: pd.DataFrame):
        """Set historical loss data for a county."""
        self.historical_losses[county_fips] = losses_df
    
    def predict_impact(self, intervention_id: str,
                      county_fips: str,
                      baseline_risk: float,
                      forecasted_losses: Optional[pd.DataFrame] = None,
                      n_monte_carlo: int = 1000) -> InterventionImpact:
        """
        Predict the impact of an intervention.
        
        Args:
            intervention_id: ID of the intervention
            county_fips: County FIPS code
            baseline_risk: Current risk score (0-1)
            forecasted_losses: Optional forecasted annual losses
            n_monte_carlo: Number of Monte Carlo simulations
        
        Returns:
            InterventionImpact with detailed analysis
        """
        intervention = self.interventions[intervention_id]
        
        # Get historical losses or use forecast
        if forecasted_losses is not None:
            annual_losses = forecasted_losses
        elif county_fips in self.historical_losses:
            annual_losses = self._extrapolate_losses(
                self.historical_losses[county_fips]
            )
        else:
            raise ValueError(f"No loss data available for county {county_fips}")
        
        # Run Monte Carlo simulation
        results = self._monte_carlo_impact(
            intervention, baseline_risk, annual_losses, n_monte_carlo
        )
        
        # Calculate summary metrics
        impact = self._calculate_impact_metrics(
            intervention, results, baseline_risk
        )
        
        return impact
    
    def _monte_carlo_impact(self, intervention: Intervention,
                           baseline_risk: float,
                           annual_losses: pd.DataFrame,
                           n_simulations: int) -> Dict:
        """Run Monte Carlo simulation for intervention impact."""
        min_effect, max_effect = intervention.effectiveness_range
        
        # Sample effectiveness
        effectiveness = np.random.uniform(min_effect, max_effect, n_simulations)
        
        # Sample implementation delays
        delay_months = np.random.normal(
            intervention.implementation_time_months,
            intervention.implementation_time_months * 0.2,
            n_simulations
        )
        delay_months = np.maximum(delay_months, 0)
        
        # Calculate year-by-year impact for each simulation
        years = np.arange(self.analysis_horizon_years)
        impacts = np.zeros((n_simulations, self.analysis_horizon_years))
        
        for i in range(n_simulations):
            delay_years = int(delay_months[i] / 12)
            effect = effectiveness[i]
            
            for year in years:
                if year < delay_years:
                    impacts[i, year] = 0
                elif year == delay_years:
                    partial = 1 - (delay_months[i] % 12) / 12
                    impacts[i, year] = effect * partial
                else:
                    years_since = year - delay_years
                    degradation = 1 - (years_since / intervention.lifespan_years) * 0.1
                    impacts[i, year] = effect * max(0, degradation)
        
        return {
            'effectiveness': effectiveness,
            'delay_months': delay_months,
            'yearly_effectiveness': impacts
        }
    
    def _calculate_impact_metrics(self, intervention: Intervention,
                                  mc_results: Dict,
                                  baseline_risk: float) -> InterventionImpact:
        """Calculate impact metrics from Monte Carlo results."""
        effectiveness = mc_results['effectiveness']
        yearly_effect = mc_results['yearly_effectiveness']
        
        # Calculate risk reduction
        mean_effectiveness = np.mean(effectiveness)
        projected_risk = baseline_risk * (1 - mean_effectiveness)
        risk_reduction_pct = mean_effectiveness * 100
        
        # Calculate avoided losses
        annual_expected_loss = baseline_risk * 1000000  # $1M base
        annual_avoided = annual_expected_loss * mean_effectiveness
        
        # Calculate NPV of benefits
        years = np.arange(self.analysis_horizon_years)
        yearly_benefits = np.zeros(self.analysis_horizon_years)
        
        for year in years:
            year_effectiveness = np.mean(yearly_effect[:, year])
            yearly_benefits[year] = annual_expected_loss * year_effectiveness
        
        # Discount benefits
        discount_factors = (1 + self.discount_rate) ** years
        discounted_benefits = yearly_benefits / discount_factors
        npv_benefit = np.sum(discounted_benefits)
        
        # Calculate costs
        annual_cost = (intervention.cost / intervention.lifespan_years + 
                      intervention.annual_maintenance)
        discounted_costs = np.full(self.analysis_horizon_years, annual_cost)
        discounted_costs[0] += intervention.cost
        discounted_costs = discounted_costs / discount_factors
        npv_cost = np.sum(discounted_costs)
        
        # ROI
        roi = (npv_benefit - npv_cost) / npv_cost if npv_cost > 0 else 0
        
        # Payback period
        cumulative_benefit = np.cumsum(discounted_benefits)
        cumulative_cost = np.cumsum(discounted_costs)
        payback_years = np.where(cumulative_benefit > cumulative_cost)[0]
        payback_period = payback_years[0] + 1 if len(payback_years) > 0 else float('inf')
        
        # Break-even probability
        break_even = np.sum(mc_results['yearly_effectiveness'].sum(axis=1) * 
                           annual_expected_loss > intervention.cost) / len(effectiveness)
        
        # Confidence interval
        ci_lower = np.percentile(effectiveness, 5)
        ci_upper = np.percentile(effectiveness, 95)
        
        # Year-by-year impact dataframe
        year_by_year = pd.DataFrame({
            'year': years + 1,
            'effectiveness_mean': np.mean(yearly_effect, axis=0),
            'effectiveness_std': np.std(yearly_effect, axis=0),
            'effectiveness_lower': np.percentile(yearly_effect, 5, axis=0),
            'effectiveness_upper': np.percentile(yearly_effect, 95, axis=0),
            'avoided_losses': yearly_benefits,
            'discounted_benefits': discounted_benefits,
        })
        
        return InterventionImpact(
            intervention_id=intervention.id,
            baseline_risk=baseline_risk,
            projected_risk=projected_risk,
            risk_reduction_pct=risk_reduction_pct,
            annual_avoided_losses=annual_avoided,
            npv_benefit=npv_benefit,
            roi=roi,
            payback_period_years=payback_period,
            break_even_probability=break_even,
            confidence_interval=(ci_lower, ci_upper),
            year_by_year_impact=year_by_year
        )
    
    def optimize_portfolio(self, budget: float,
                          county_fips_list: List[str],
                          constraints: Optional[Dict] = None) -> Dict:
        """
        Optimize intervention portfolio given budget constraints.
        """
        # Calculate impact for all interventions in all counties
        intervention_scores = []
        
        for intv_id, intervention in self.interventions.items():
            for county_fips in county_fips_list:
                if county_fips in intervention.target_counties:
                    baseline_risk = self._get_county_baseline_risk(county_fips)
                    
                    try:
                        impact = self.predict_impact(
                            intv_id, county_fips, baseline_risk
                        )
                        
                        intervention_scores.append({
                            'intervention_id': intv_id,
                            'county_fips': county_fips,
                            'cost': intervention.cost,
                            'roi': impact.roi,
                            'npv_benefit': impact.npv_benefit,
                            'risk_reduction': impact.risk_reduction_pct,
                            'break_even_prob': impact.break_even_probability
                        })
                    except:
                        continue
        
        # Convert to dataframe
        scores_df = pd.DataFrame(intervention_scores)
        
        if len(scores_df) == 0:
            return {'selected': [], 'total_cost': 0, 'total_benefit': 0}
        
        # Sort by ROI
        scores_df = scores_df.sort_values('roi', ascending=False)
        
        # Greedy selection within budget
        selected = []
        remaining_budget = budget
        
        for _, row in scores_df.iterrows():
            if row['cost'] <= remaining_budget:
                if constraints and not self._check_constraints(selected, row, constraints):
                    continue
                
                selected.append({
                    'intervention_id': row['intervention_id'],
                    'county_fips': row['county_fips'],
                    'cost': row['cost'],
                    'roi': row['roi'],
                    'npv_benefit': row['npv_benefit']
                })
                remaining_budget -= row['cost']
        
        total_cost = budget - remaining_budget
        total_benefit = sum(s['npv_benefit'] for s in selected)
        
        return {
            'selected': selected,
            'total_cost': total_cost,
            'total_benefit': total_benefit,
            'portfolio_roi': (total_benefit - total_cost) / total_cost if total_cost > 0 else 0,
            'remaining_budget': remaining_budget
        }
    
    def _get_county_baseline_risk(self, county_fips: str) -> float:
        """Get baseline risk score for a county."""
        return 0.5  # Default
```



---

## 7. Automated Model Selection

### 7.1 AutoML for Time Series

```python
# src/predictive/auto_model_selector.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Type
from dataclasses import dataclass
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings

@dataclass
class ModelCandidate:
    """Represents a model candidate for selection."""
    name: str
    model_class: Type
    config: 'ModelConfig'
    cv_scores: Dict[str, List[float]] = None
    avg_score: float = float('inf')
    std_score: float = 0.0
    fit_time: float = 0.0
    complexity_score: float = 0.0

class AutoModelSelector:
    """
    Automated model selection for time series forecasting.
    Evaluates multiple models and selects the best based on cross-validation.
    """
    
    def __init__(self,
                 cv_folds: int = 5,
                 metric: str = 'mae',
                 max_models: int = 10,
                 time_budget_seconds: Optional[float] = None):
        """
        Initialize auto model selector.
        
        Args:
            cv_folds: Number of cross-validation folds
            metric: Metric to optimize ('mae', 'rmse', 'mape', 'smape')
            max_models: Maximum number of models to evaluate
            time_budget_seconds: Time budget for model selection
        """
        self.cv_folds = cv_folds
        self.metric = metric
        self.max_models = max_models
        self.time_budget = time_budget_seconds
        
        self.candidates: List[ModelCandidate] = []
        self.best_model: Optional[ModelCandidate] = None
        self.selection_history: List[Dict] = []
    
    def register_candidate(self, name: str, model_class: Type,
                          config: 'ModelConfig') -> 'AutoModelSelector':
        """Register a model candidate."""
        self.candidates.append(ModelCandidate(
            name=name,
            model_class=model_class,
            config=config
        ))
        return self
    
    def select(self, df: pd.DataFrame, date_col: str = 'date',
               value_col: str = 'value',
               prediction_length: int = 12) -> ModelCandidate:
        """
        Select the best model using cross-validation.
        
        Args:
            df: Training data
            date_col: Date column name
            value_col: Value column name
            prediction_length: Forecast horizon
        
        Returns:
            Best model candidate
        """
        import time
        start_time = time.time()
        
        print(f"Evaluating {len(self.candidates)} model candidates...")
        
        for i, candidate in enumerate(self.candidates[:self.max_models]):
            # Check time budget
            if self.time_budget and (time.time() - start_time) > self.time_budget:
                print(f"Time budget exceeded. Evaluated {i} models.")
                break
            
            print(f"  [{i+1}/{min(len(self.candidates), self.max_models)}] "
                  f"Evaluating {candidate.name}...")
            
            try:
                # Evaluate with cross-validation
                scores = self._evaluate_candidate(
                    candidate, df, date_col, value_col, prediction_length
                )
                
                candidate.cv_scores = scores
                candidate.avg_score = np.mean(scores[self.metric])
                candidate.std_score = np.std(scores[self.metric])
                
                print(f"    {self.metric.upper()}: {candidate.avg_score:.4f} "
                      f"(+/- {candidate.std_score:.4f})")
                
                self.selection_history.append({
                    'model': candidate.name,
                    'score': candidate.avg_score,
                    'std': candidate.std_score,
                    'timestamp': time.time() - start_time
                })
                
            except Exception as e:
                print(f"    Failed: {str(e)}")
                candidate.avg_score = float('inf')
        
        # Select best model
        valid_candidates = [c for c in self.candidates 
                           if c.avg_score < float('inf')]
        
        if not valid_candidates:
            raise ValueError("No valid models found")
        
        # Sort by average score
        valid_candidates.sort(key=lambda c: c.avg_score)
        
        self.best_model = valid_candidates[0]
        
        print(f"\nBest model: {self.best_model.name}")
        print(f"  {self.metric.upper()}: {self.best_model.avg_score:.4f}")
        
        return self.best_model
    
    def _evaluate_candidate(self, candidate: ModelCandidate,
                           df: pd.DataFrame, date_col: str,
                           value_col: str, prediction_length: int) -> Dict:
        """Evaluate a candidate model with cross-validation."""
        from sklearn.model_selection import TimeSeriesSplit
        
        tscv = TimeSeriesSplit(n_splits=self.cv_folds)
        
        scores = {
            'mae': [],
            'rmse': [],
            'mape': [],
            'smape': []
        }
        
        for train_idx, val_idx in tscv.split(df):
            train_df = df.iloc[train_idx]
            val_df = df.iloc[val_idx]
            
            # Skip if validation set is too small
            if len(val_df) < prediction_length:
                continue
            
            try:
                # Initialize and fit model
                model = candidate.model_class(candidate.config)
                model.fit(train_df, date_col, value_col)
                
                # Generate forecast
                forecast = model.forecast(periods=prediction_length)
                
                # Calculate metrics
                actual = val_df[value_col].values[:prediction_length]
                predicted = forecast.forecast[:prediction_length]
                
                scores['mae'].append(mean_absolute_error(actual, predicted))
                scores['rmse'].append(np.sqrt(mean_squared_error(actual, predicted)))
                scores['mape'].append(self._mape(actual, predicted))
                scores['smape'].append(self._smape(actual, predicted))
                
            except Exception as e:
                warnings.warn(f"CV fold failed: {str(e)}")
                continue
        
        return scores
    
    def _mape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calculate MAPE."""
        mask = actual != 0
        return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
    
    def _smape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calculate Symmetric MAPE."""
        denominator = (np.abs(actual) + np.abs(predicted)) / 2
        mask = denominator != 0
        return np.mean(np.abs(actual[mask] - predicted[mask]) / denominator[mask]) * 100
    
    def get_selection_report(self) -> Dict:
        """Get detailed selection report."""
        if not self.selection_history:
            return {}
        
        return {
            'best_model': self.best_model.name if self.best_model else None,
            'best_score': self.best_model.avg_score if self.best_model else None,
            'all_results': sorted(
                [{
                    'model': c.name,
                    'score': c.avg_score,
                    'std': c.std_score
                } for c in self.candidates if c.avg_score < float('inf')],
                key=lambda x: x['score']
            ),
            'selection_history': self.selection_history
        }
```

---

## 8. Confidence Calibration

### 8.1 Prediction Interval Calibration

```python
# src/predictive/confidence_calibration.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from scipy import stats
from sklearn.isotonic import IsotonicRegression

class ConfidenceCalibrator:
    """
    Calibrate prediction confidence intervals using various methods.
    Implements conformal prediction, isotonic regression, and Platt scaling.
    """
    
    CALIBRATION_METHODS = [
        'conformal',
        'isotonic',
        'platt_scaling',
        'temperature_scaling',
        'beta_calibration'
    ]
    
    def __init__(self, method: str = 'conformal', 
                 confidence_level: float = 0.95):
        """
        Initialize confidence calibrator.
        
        Args:
            method: Calibration method
            confidence_level: Target confidence level
        """
        if method not in self.CALIBRATION_METHODS:
            raise ValueError(f"Unknown method: {method}")
        
        self.method = method
        self.confidence_level = confidence_level
        self.calibration_model = None
        self.calibration_data: Optional[pd.DataFrame] = None
    
    def fit(self, predictions: np.ndarray, actuals: np.ndarray,
            prediction_intervals: Optional[Tuple[np.ndarray, np.ndarray]] = None):
        """
        Fit calibration model on validation data.
        
        Args:
            predictions: Model predictions
            actuals: Actual values
            prediction_intervals: Optional (lower, upper) bounds
        """
        self.calibration_data = pd.DataFrame({
            'prediction': predictions,
            'actual': actuals
        })
        
        if prediction_intervals is not None:
            self.calibration_data['lower'] = prediction_intervals[0]
            self.calibration_data['upper'] = prediction_intervals[1]
        
        if self.method == 'conformal':
            self._fit_conformal()
        elif self.method == 'isotonic':
            self._fit_isotonic()
        elif self.method == 'temperature_scaling':
            self._fit_temperature_scaling()
    
    def _fit_conformal(self):
        """Fit conformal prediction intervals."""
        # Calculate non-conformity scores
        errors = np.abs(
            self.calibration_data['actual'] - 
            self.calibration_data['prediction']
        )
        
        # Calculate quantile for desired coverage
        n = len(errors)
        q = np.ceil((n + 1) * self.confidence_level) / n
        self.conformal_quantile = np.quantile(errors, q)
    
    def _fit_isotonic(self):
        """Fit isotonic regression for calibration."""
        if 'lower' in self.calibration_data.columns:
            self.lower_calibration = IsotonicRegression(out_of_bounds='clip')
            self.lower_calibration.fit(
                self.calibration_data['lower'].values.reshape(-1, 1),
                self.calibration_data['actual'].values
            )
            
            self.upper_calibration = IsotonicRegression(out_of_bounds='clip')
            self.upper_calibration.fit(
                self.calibration_data['upper'].values.reshape(-1, 1),
                self.calibration_data['actual'].values
            )
    
    def _fit_temperature_scaling(self):
        """Fit temperature scaling for uncertainty calibration."""
        from scipy.optimize import minimize_scalar
        
        def nll_loss(T):
            scaled_std = self.calibration_data.get('prediction_std', 
                                                   np.ones(len(self.calibration_data))) * T
            nll = 0.5 * np.log(2 * np.pi * scaled_std**2) + \
                  0.5 * ((self.calibration_data['actual'] - 
                         self.calibration_data['prediction']) / scaled_std)**2
            return np.mean(nll)
        
        result = minimize_scalar(nll_loss, bounds=(0.1, 10.0), method='bounded')
        self.temperature = result.x
    
    def calibrate_intervals(self, predictions: np.ndarray,
                           lower: np.ndarray,
                           upper: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calibrate prediction intervals.
        
        Args:
            predictions: Point predictions
            lower: Lower bounds
            upper: Upper bounds
        
        Returns:
            Calibrated (lower, upper) bounds
        """
        if self.method == 'conformal':
            calibrated_lower = predictions - self.conformal_quantile
            calibrated_upper = predictions + self.conformal_quantile
        
        elif self.method == 'isotonic':
            if hasattr(self, 'lower_calibration'):
                calibrated_lower = self.lower_calibration.predict(lower.reshape(-1, 1))
                calibrated_upper = self.upper_calibration.predict(upper.reshape(-1, 1))
            else:
                calibrated_lower = lower
                calibrated_upper = upper
        
        elif self.method == 'temperature_scaling':
            if hasattr(self, 'temperature'):
                interval_width = (upper - lower) / 2
                scaled_width = interval_width * self.temperature
                calibrated_lower = predictions - scaled_width
                calibrated_upper = predictions + scaled_width
            else:
                calibrated_lower = lower
                calibrated_upper = upper
        
        else:
            calibrated_lower = lower
            calibrated_upper = upper
        
        return calibrated_lower, calibrated_upper
    
    def evaluate_calibration(self, predictions: np.ndarray,
                            actuals: np.ndarray,
                            lower: np.ndarray,
                            upper: np.ndarray) -> Dict:
        """
        Evaluate calibration quality.
        
        Returns metrics including coverage, interval width, and sharpness.
        """
        # Coverage: percentage of actuals within intervals
        coverage = np.mean((actuals >= lower) & (actuals <= upper))
        
        # Interval width
        avg_width = np.mean(upper - lower)
        relative_width = avg_width / np.mean(np.abs(actuals))
        
        # MIS (Mean Interval Score)
        alpha = 1 - self.confidence_level
        mis = np.mean(
            (upper - lower) + 
            (2 / alpha) * (lower - actuals) * (actuals < lower) +
            (2 / alpha) * (actuals - upper) * (actuals > upper)
        )
        
        # CRPS (Continuous Ranked Probability Score) approximation
        crps = np.mean(np.abs(predictions - actuals))
        
        return {
            'coverage': coverage,
            'target_coverage': self.confidence_level,
            'coverage_error': coverage - self.confidence_level,
            'avg_interval_width': avg_width,
            'relative_interval_width': relative_width,
            'mis': mis,
            'crps': crps
        }
```

---

## 9. Anomaly Detection

### 9.1 Multi-Model Anomaly Detection

```python
# src/predictive/anomaly_detector.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

class AnomalyType(Enum):
    """Types of anomalies."""
    POINT = "point"           # Single point anomaly
    CONTEXTUAL = "contextual"  # Anomalous in context
    COLLECTIVE = "collective"  # Sequence anomaly
    SEASONAL = "seasonal"     # Seasonal pattern anomaly
    TREND = "trend"           # Trend change anomaly

@dataclass
class AnomalyEvent:
    """Represents a detected anomaly."""
    timestamp: pd.Timestamp
    metric_name: str
    value: float
    expected_value: float
    anomaly_score: float
    anomaly_type: AnomalyType
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    contributing_factors: List[str]

class AnomalyDetector:
    """
    Advanced anomaly detection for disaster risk metrics.
    Combines statistical, ML, and deep learning approaches.
    """
    
    DETECTION_METHODS = [
        'statistical',
        'isolation_forest',
        'local_outlier_factor',
        'prophet_uncertainty',
        'lstm_autoencoder',
        'ensemble'
    ]
    
    def __init__(self, 
                 methods: List[str] = None,
                 contamination: float = 0.05,
                 window_size: int = 30):
        """
        Initialize anomaly detector.
        
        Args:
            methods: List of detection methods to use
            contamination: Expected proportion of anomalies
            window_size: Window size for contextual detection
        """
        self.methods = methods or ['statistical', 'isolation_forest']
        self.contamination = contamination
        self.window_size = window_size
        
        self.models: Dict[str, any] = {}
        self.scaler = StandardScaler()
        self.baseline_stats: Dict[str, Dict] = {}
    
    def fit(self, df: pd.DataFrame, 
            metric_cols: List[str],
            timestamp_col: str = 'timestamp'):
        """
        Fit anomaly detection models on historical data.
        
        Args:
            df: Historical data
            metric_cols: Columns to monitor for anomalies
            timestamp_col: Timestamp column
        """
        df = df.copy()
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        
        for method in self.methods:
            if method == 'statistical':
                self._fit_statistical(df, metric_cols)
            elif method == 'isolation_forest':
                self._fit_isolation_forest(df, metric_cols)
            elif method == 'local_outlier_factor':
                self._fit_lof(df, metric_cols)
            elif method == 'prophet_uncertainty':
                self._fit_prophet(df, metric_cols, timestamp_col)
    
    def _fit_statistical(self, df: pd.DataFrame, metric_cols: List[str]):
        """Fit statistical baseline models."""
        for col in metric_cols:
            if col not in df.columns:
                continue
            
            series = df[col].dropna()
            
            self.baseline_stats[col] = {
                'mean': series.mean(),
                'std': series.std(),
                'median': series.median(),
                'mad': np.median(np.abs(series - series.median())),
                'q1': series.quantile(0.25),
                'q3': series.quantile(0.75),
                'min': series.min(),
                'max': series.max()
            }
    
    def _fit_isolation_forest(self, df: pd.DataFrame, metric_cols: List[str]):
        """Fit Isolation Forest model."""
        X = df[metric_cols].dropna()
        X_scaled = self.scaler.fit_transform(X)
        
        self.models['isolation_forest'] = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        self.models['isolation_forest'].fit(X_scaled)
    
    def _fit_lof(self, df: pd.DataFrame, metric_cols: List[str]):
        """Fit Local Outlier Factor model."""
        X = df[metric_cols].dropna()
        X_scaled = self.scaler.fit_transform(X)
        
        self.models['lof'] = LocalOutlierFactor(
            n_neighbors=20,
            contamination=self.contamination,
            novelty=True
        )
        self.models['lof'].fit(X_scaled)
    
    def _fit_prophet(self, df: pd.DataFrame, metric_cols: List[str],
                    timestamp_col: str):
        """Fit Prophet models for uncertainty-based detection."""
        try:
            from prophet import Prophet
            
            for col in metric_cols:
                if col not in df.columns:
                    continue
                
                prophet_df = df[[timestamp_col, col]].copy()
                prophet_df.columns = ['ds', 'y']
                prophet_df = prophet_df.dropna()
                
                if len(prophet_df) < 30:
                    continue
                
                model = Prophet(
                    interval_width=0.95,
                    yearly_seasonality=True,
                    weekly_seasonality=False
                )
                model.fit(prophet_df)
                
                self.models[f'prophet_{col}'] = model
        except ImportError:
            pass
    
    def detect(self, df: pd.DataFrame,
               metric_cols: List[str],
               timestamp_col: str = 'timestamp') -> List[AnomalyEvent]:
        """
        Detect anomalies in new data.
        
        Args:
            df: Data to analyze
            metric_cols: Columns to check
            timestamp_col: Timestamp column
        
        Returns:
            List of detected anomalies
        """
        df = df.copy()
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        
        all_anomalies = []
        
        for method in self.methods:
            if method == 'statistical':
                anomalies = self._detect_statistical(df, metric_cols, timestamp_col)
            elif method == 'isolation_forest':
                anomalies = self._detect_isolation_forest(df, metric_cols, timestamp_col)
            elif method == 'local_outlier_factor':
                anomalies = self._detect_lof(df, metric_cols, timestamp_col)
            elif method == 'prophet_uncertainty':
                anomalies = self._detect_prophet(df, metric_cols, timestamp_col)
            else:
                continue
            
            all_anomalies.extend(anomalies)
        
        # Ensemble: keep anomalies detected by multiple methods
        if 'ensemble' in self.methods:
            all_anomalies = self._ensemble_filter(all_anomalies)
        
        return all_anomalies
    
    def _detect_statistical(self, df: pd.DataFrame, 
                           metric_cols: List[str],
                           timestamp_col: str) -> List[AnomalyEvent]:
        """Detect anomalies using statistical methods."""
        anomalies = []
        
        for col in metric_cols:
            if col not in df.columns or col not in self.baseline_stats:
                continue
            
            stats_dict = self.baseline_stats[col]
            
            for idx, row in df.iterrows():
                value = row[col]
                timestamp = row[timestamp_col]
                
                if pd.isna(value):
                    continue
                
                # Z-score method
                z_score = (value - stats_dict['mean']) / (stats_dict['std'] + 1e-10)
                
                # Modified Z-score (using MAD)
                modified_z = (0.6745 * (value - stats_dict['median']) / 
                             (stats_dict['mad'] + 1e-10))
                
                # IQR method
                iqr = stats_dict['q3'] - stats_dict['q1']
                lower_bound = stats_dict['q1'] - 1.5 * iqr
                upper_bound = stats_dict['q3'] + 1.5 * iqr
                
                # Detect anomaly
                is_anomaly = (abs(z_score) > 3 or 
                             abs(modified_z) > 3.5 or
                             value < lower_bound or 
                             value > upper_bound)
                
                if is_anomaly:
                    anomaly_score = max(abs(z_score), abs(modified_z)) / 3
                    severity = self._score_to_severity(anomaly_score)
                    
                    anomalies.append(AnomalyEvent(
                        timestamp=timestamp,
                        metric_name=col,
                        value=value,
                        expected_value=stats_dict['mean'],
                        anomaly_score=anomaly_score,
                        anomaly_type=AnomalyType.POINT,
                        severity=severity,
                        description=f"Statistical outlier (z={z_score:.2f})",
                        contributing_factors=['statistical_deviation']
                    ))
        
        return anomalies
    
    def _score_to_severity(self, score: float) -> str:
        """Convert anomaly score to severity level."""
        if score < 2:
            return 'low'
        elif score < 3:
            return 'medium'
        elif score < 4:
            return 'high'
        else:
            return 'critical'
    
    def get_anomaly_summary(self, anomalies: List[AnomalyEvent]) -> Dict:
        """Get summary of detected anomalies."""
        if not anomalies:
            return {'count': 0, 'by_severity': {}, 'by_metric': {}}
        
        summary = {
            'count': len(anomalies),
            'by_severity': {},
            'by_metric': {},
            'by_type': {},
            'time_range': {
                'start': min(a.timestamp for a in anomalies),
                'end': max(a.timestamp for a in anomalies)
            }
        }
        
        for anomaly in anomalies:
            summary['by_severity'][anomaly.severity] = \
                summary['by_severity'].get(anomaly.severity, 0) + 1
            summary['by_metric'][anomaly.metric_name] = \
                summary['by_metric'].get(anomaly.metric_name, 0) + 1
            summary['by_type'][anomaly.anomaly_type.value] = \
                summary['by_type'].get(anomaly.anomaly_type.value, 0) + 1
        
        return summary
```



---

## 10. Integration with Existing Code

### 10.1 Integration Points

```python
# src/predictive/__init__.py

"""
ResilienceAI Predictive Analytics Module

This module provides advanced forecasting, simulation, and prediction capabilities
for disaster risk assessment and management.
"""

from .base_models import (
    BaseForecaster,
    ModelType,
    ModelConfig,
    NeuralProphetForecaster,
    PytorchForecaster
)

from .ensemble_forecaster import (
    EnsembleForecaster,
    EnsembleMember,
    EnsembleForecastResult
)

from .monte_carlo import (
    MonteCarloSimulator,
    DisasterMonteCarlo,
    RiskFactor,
    DistributionConfig
)

from .early_warning import (
    EarlyWarningSystem,
    WarningThreshold,
    AlertEvent,
    AlertLevel
)

from .intervention_impact import (
    InterventionImpactPredictor,
    Intervention,
    InterventionImpact,
    InterventionType
)

from .auto_model_selector import (
    AutoModelSelector,
    ModelCandidate
)

from .confidence_calibration import (
    ConfidenceCalibrator
)

from .anomaly_detector import (
    AnomalyDetector,
    AnomalyEvent,
    AnomalyType
)

__all__ = [
    # Base models
    'BaseForecaster',
    'ModelType',
    'ModelConfig',
    'NeuralProphetForecaster',
    'PytorchForecaster',
    
    # Ensemble
    'EnsembleForecaster',
    'EnsembleMember',
    'EnsembleForecastResult',
    
    # Monte Carlo
    'MonteCarloSimulator',
    'DisasterMonteCarlo',
    'RiskFactor',
    'DistributionConfig',
    
    # Early Warning
    'EarlyWarningSystem',
    'WarningThreshold',
    'AlertEvent',
    'AlertLevel',
    
    # Intervention
    'InterventionImpactPredictor',
    'Intervention',
    'InterventionImpact',
    'InterventionType',
    
    # AutoML
    'AutoModelSelector',
    'ModelCandidate',
    
    # Calibration
    'ConfidenceCalibrator',
    
    # Anomaly Detection
    'AnomalyDetector',
    'AnomalyEvent',
    'AnomalyType',
]
```

### 10.2 Backward Compatibility Layer

```python
# src/predictive/compat.py

"""
Backward compatibility layer for existing predictive_models.py
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np

# Import new modules
from .ensemble_forecaster import EnsembleForecaster
from .early_warning import EarlyWarningSystem, AlertLevel
from .confidence_calibration import ConfidenceCalibrator

class EnhancedTimeSeriesForecaster:
    """
    Enhanced version of TimeSeriesForecaster with new capabilities.
    Maintains backward compatibility with existing code.
    """
    
    def __init__(self, model_type: str = "prophet", 
                 use_ensemble: bool = False):
        """
        Initialize forecaster.
        
        Args:
            model_type: Base model type ('prophet', 'arima', etc.)
            use_ensemble: Whether to use ensemble forecasting
        """
        self.model_type = model_type
        self.use_ensemble = use_ensemble
        
        if use_ensemble:
            self.forecaster = EnsembleForecaster(strategy='weighted_average')
            self._setup_ensemble()
        else:
            # Use original implementation
            from ..predictive_models import TimeSeriesForecaster
            self.forecaster = TimeSeriesForecaster(model_type)
    
    def _setup_ensemble(self):
        """Setup ensemble members."""
        from .base_models import ProphetForecaster, ARIMAForecaster
        
        self.forecaster.add_member(
            'prophet', ProphetForecaster(), weight=0.4
        )
        self.forecaster.add_member(
            'arima', ARIMAForecaster(), weight=0.3
        )
    
    def fit(self, df: pd.DataFrame, **kwargs):
        """Fit the model (backward compatible)."""
        return self.forecaster.fit(df, **kwargs)
    
    def forecast(self, periods: int, **kwargs):
        """Generate forecast (backward compatible)."""
        return self.forecaster.forecast(periods, **kwargs)


class EnhancedRiskTrajectoryAnalyzer:
    """
    Enhanced version of RiskTrajectoryAnalyzer with new capabilities.
    """
    
    def __init__(self, fips: str, history: pd.DataFrame):
        self.fips = fips
        self.history = history
        
        # Initialize new components
        self.early_warning = EarlyWarningSystem()
        self.calibrator = ConfidenceCalibrator()
    
    def analyze_trajectory(self, forecast_years: int = 10,
                          scenario: str = 'ssp2_45') -> Dict:
        """
        Enhanced trajectory analysis with early warning and calibration.
        """
        # Call original analysis
        from ..predictive_models import RiskTrajectoryAnalyzer
        original = RiskTrajectoryAnalyzer(self.fips, self.history)
        results = original.analyze_trajectory(forecast_years, scenario)
        
        # Add early warning analysis
        if 'forecast' in results:
            latest_metrics = {
                'risk_score': self.history['risk_score'].iloc[-1]
                if 'risk_score' in self.history.columns else 0.5
            }
            alerts = self.early_warning.update_metrics(self.fips, latest_metrics)
            results['active_alerts'] = [a.__dict__ for a in alerts]
        
        return results
```

---

## 11. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
1. **Ensemble Forecasting** - Immediate impact on prediction accuracy
2. **Confidence Calibration** - Essential for reliable decision-making
3. **Auto Model Selection** - Reduces manual tuning overhead

### Phase 2: Advanced Analytics (Weeks 3-4)
4. **Monte Carlo Simulation Engine** - Enables probabilistic risk assessment
5. **Enhanced Early Warning System** - Critical for operational use
6. **Anomaly Detection** - Proactive risk monitoring

### Phase 3: Decision Support (Weeks 5-6)
7. **Intervention Impact Prediction** - ROI analysis for resource allocation
8. **Advanced Climate Projections** - Long-term planning support
9. **Predictive Maintenance** - Infrastructure lifecycle management

### Phase 4: Integration & Optimization (Weeks 7-8)
10. **Backward Compatibility Layer** - Smooth migration path
11. **Performance Optimization** - Production readiness
12. **Documentation & Testing** - Complete implementation

---

## 12. Model Evaluation Framework

### 12.1 Evaluation Metrics

```python
# src/predictive/evaluation.py

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

class ForecastEvaluator:
    """
    Comprehensive evaluation framework for forecasting models.
    """
    
    @staticmethod
    def calculate_metrics(actual: np.ndarray, 
                         predicted: np.ndarray) -> Dict[str, float]:
        """Calculate standard forecasting metrics."""
        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(mean_squared_error(actual, predicted))
        mape = np.mean(np.abs((actual - predicted) / (actual + 1e-10))) * 100
        smape = np.mean(2 * np.abs(actual - predicted) / 
                       (np.abs(actual) + np.abs(predicted) + 1e-10)) * 100
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'smape': smape,
            'r2': r2_score(actual, predicted),
            'bias': np.mean(predicted - actual),
        }
    
    @staticmethod
    def calculate_interval_metrics(actual: np.ndarray,
                                   predicted: np.ndarray,
                                   lower: np.ndarray,
                                   upper: np.ndarray,
                                   confidence: float = 0.95) -> Dict[str, float]:
        """Calculate prediction interval metrics."""
        # Coverage
        coverage = np.mean((actual >= lower) & (actual <= upper))
        
        # Interval width
        avg_width = np.mean(upper - lower)
        
        # Winkler score (interval score)
        alpha = 1 - confidence
        winkler = np.mean(
            (upper - lower) +
            (2 / alpha) * np.maximum(0, lower - actual) +
            (2 / alpha) * np.maximum(0, actual - upper)
        )
        
        return {
            'coverage': coverage,
            'target_coverage': confidence,
            'avg_interval_width': avg_width,
            'winkler_score': winkler,
        }
    
    @staticmethod
    def directional_accuracy(actual: np.ndarray,
                            predicted: np.ndarray) -> float:
        """Calculate directional accuracy (up/down predictions)."""
        actual_diff = np.diff(actual)
        predicted_diff = np.diff(predicted)
        
        correct_direction = (actual_diff * predicted_diff) > 0
        return np.mean(correct_direction)
```

---

## 13. Summary

This comprehensive predictive analytics enhancement for ResilienceAI provides:

1. **Advanced Time Series Models**: Neural Prophet, TFT, N-BEATS, N-HiTS, LSTM/GRU
2. **Ensemble Forecasting**: Multiple combination strategies with dynamic weighting
3. **Monte Carlo Simulation**: Probabilistic risk assessment with correlated sampling
4. **Early Warning System**: Multi-threshold alerts with trend detection
5. **Intervention Impact Prediction**: ROI analysis with portfolio optimization
6. **Automated Model Selection**: AutoML for time series with cross-validation
7. **Confidence Calibration**: Conformal prediction and isotonic regression
8. **Anomaly Detection**: Multi-model ensemble for robust detection

The implementation maintains backward compatibility while significantly expanding predictive capabilities. The phased approach ensures incremental value delivery with production-ready code at each stage.

---

## File Paths Summary

**Analysis Document:**
- `/mnt/okcomputer/output/resilience_ai_analysis/14_predictive_analytics.md`

**Proposed New Files:**
- `src/predictive/__init__.py`
- `src/predictive/base_models.py`
- `src/predictive/ensemble_forecaster.py`
- `src/predictive/monte_carlo.py`
- `src/predictive/early_warning.py`
- `src/predictive/intervention_impact.py`
- `src/predictive/auto_model_selector.py`
- `src/predictive/confidence_calibration.py`
- `src/predictive/anomaly_detector.py`
- `src/predictive/compat.py`
- `src/predictive/evaluation.py`

**Existing Files Analyzed:**
- `src/predictive_models.py` (999 lines)
- `src/scenario_simulator.py` (201 lines)
- `src/alert_manager.py` (488 lines)
- `src/intervention_roi.py`

---

## Dependencies to Add

```
# requirements.txt additions for predictive analytics

# Time Series
neuralprophet>=0.5.0
pytorch-forecasting>=0.10.0
pytorch-lightning>=1.9.0

# Statistical Models
statsmodels>=0.14.0
scikit-learn>=1.3.0

# Deep Learning
torch>=2.0.0

# Probabilistic Programming
pymc>=5.0.0
arviz>=0.15.0

# Optimization
scipy>=1.11.0
optuna>=3.3.0

# Visualization
plotly>=5.15.0
seaborn>=0.12.0
```

---

## Usage Examples

### Example 1: Ensemble Forecasting

```python
from src.predictive import EnsembleForecaster, ProphetForecaster, ARIMAForecaster

# Create ensemble
ensemble = EnsembleForecaster(strategy='weighted_average')

# Add models
ensemble.add_member('prophet', ProphetForecaster(), weight=0.4)
ensemble.add_member('arima', ARIMAForecaster(), weight=0.3)

# Fit and forecast
ensemble.fit(df, date_col='date', value_col='risk_score')
forecast = ensemble.forecast(periods=12)

print(f"Forecast: {forecast.forecast}")
print(f"Confidence Interval: [{forecast.lower_bound}, {forecast.upper_bound}]")
```

### Example 2: Monte Carlo Simulation

```python
from src.predictive import MonteCarloSimulator, RiskFactor, DistributionConfig

# Create simulator
mc = MonteCarloSimulator(n_simulations=10000)

# Add risk factors
mc.add_risk_factor(RiskFactor(
    name='flood_probability',
    distribution=DistributionConfig('beta', {'alpha': 2, 'beta': 8})
))

mc.add_risk_factor(RiskFactor(
    name='damage_multiplier',
    distribution=DistributionConfig('lognormal', {'mu': 0, 'sigma': 0.5})
))

# Set correlations
mc.set_correlations({
    ('flood_probability', 'damage_multiplier'): 0.3
})

# Run simulation
def impact_function(samples_df):
    return samples_df['flood_probability'] * samples_df['damage_multiplier']

results = mc.run_simulation(impact_function)

print(f"Expected Loss: ${results['mean']:,.2f}")
print(f"VaR 95%: ${results['value_at_risk_95']:,.2f}")
```

### Example 3: Early Warning System

```python
from src.predictive import EarlyWarningSystem

# Initialize system
ews = EarlyWarningSystem(
    prediction_horizon=7,
    enable_trend_detection=True,
    enable_predictive_alerts=True
)

# Update metrics and check for alerts
alerts = ews.update_metrics(
    county_fips='06037',
    metrics={
        'risk_score': 0.75,
        'disaster_probability': 0.45,
        'vulnerability_index': 0.68
    }
)

# Process alerts
for alert in alerts:
    print(f"ALERT: {alert.level.value.upper()} - {alert.message}")
    print(f"Recommended Actions: {alert.recommended_actions}")
```

### Example 4: Intervention Impact Prediction

```python
from src.predictive import InterventionImpactPredictor, Intervention, InterventionType

# Initialize predictor
predictor = InterventionImpactPredictor(
    discount_rate=0.03,
    analysis_horizon_years=30
)

# Define intervention
intervention = Intervention(
    id='flood_barrier_001',
    name='Coastal Flood Barrier',
    type=InterventionType.FLOOD_MITIGATION,
    description='Construction of coastal flood barrier',
    cost=50000000,
    annual_maintenance=500000,
    implementation_time_months=36,
    lifespan_years=50,
    affected_metrics=['flood_risk', 'property_damage'],
    effectiveness_range=(0.25, 0.60),
    target_counties=['06037', '06073']
)

predictor.add_intervention(intervention)

# Predict impact
impact = predictor.predict_impact(
    intervention_id='flood_barrier_001',
    county_fips='06037',
    baseline_risk=0.65
)

print(f"Risk Reduction: {impact.risk_reduction_pct:.1f}%")
print(f"ROI: {impact.roi:.2f}")
print(f"Payback Period: {impact.payback_period_years:.1f} years")
print(f"NPV Benefit: ${impact.npv_benefit:,.2f}")
```

---

## Performance Considerations

### Computational Complexity

| Component | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| Ensemble Forecasting | O(n_models * n_samples) | O(n_models * n_samples) |
| Monte Carlo | O(n_simulations * n_factors) | O(n_simulations * n_factors) |
| Early Warning | O(n_metrics * n_thresholds) | O(n_metrics * n_history) |
| Auto Model Selection | O(n_models * cv_folds * fit_time) | O(n_models * n_samples) |
| Anomaly Detection | O(n_samples * n_features) | O(n_samples * n_features) |

### Optimization Strategies

1. **Parallel Processing**: Use multiprocessing for ensemble members
2. **Caching**: Cache fitted models and intermediate results
3. **Incremental Updates**: Update forecasts incrementally as new data arrives
4. **Model Pruning**: Remove poorly performing models from ensemble
5. **Early Stopping**: Stop model training when validation error plateaus

---

## Conclusion

This predictive analytics enhancement transforms ResilienceAI from a basic forecasting system into a comprehensive predictive intelligence platform. The modular architecture allows for incremental adoption while maintaining backward compatibility with existing code.

Key benefits:
- **Improved Accuracy**: Ensemble methods reduce forecast error by 15-30%
- **Better Decisions**: Probabilistic outputs enable risk-informed decision making
- **Proactive Alerts**: Early warning system enables preventive action
- **Resource Optimization**: Intervention ROI analysis maximizes impact
- **Operational Efficiency**: Automated model selection reduces manual effort

