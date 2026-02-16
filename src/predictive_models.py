"""
ResilienceAI - Predictive Risk Modeling Module

Time-series forecasting and machine learning models for disaster prediction.
Includes Prophet/ARIMA forecasting, climate change scenario modeling, and risk trajectory visualization.

References:
- Prophet: Facebook's forecasting tool (Taylor & Letham, 2018)
- ARIMA: Box-Jenkins methodology for time series
- Climate scenarios: IPCC AR6 Shared Socioeconomic Pathways (SSPs)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# Time series forecasting
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller, acf, pacf
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.stats.diagnostic import acorr_ljungbox
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

# Machine learning
try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from config import PROCESSED_DIR, MODELS_DIR, DATA_DIR


@dataclass
class ForecastResult:
    """Container for forecasting results."""
    dates: pd.DatetimeIndex
    forecast: np.ndarray
    lower_bound: np.ndarray
    upper_bound: np.ndarray
    model_name: str
    metrics: Dict[str, float]
    components: Optional[Dict] = None


@dataclass
class ClimateScenario:
    """Climate change scenario parameters based on IPCC SSPs."""
    name: str
    description: str
    temp_increase_c: float  # Temperature increase by 2100
    precip_change_pct: float  # Precipitation change
    extreme_event_multiplier: float  # Multiplier for extreme events
    sea_level_rise_m: float  # Sea level rise by 2100
    
    # SSP reference: IPCC AR6 WG1
    @classmethod
    def ssp1_19(cls):
        """SSP1-1.9: Sustainability - Very low emissions."""
        return cls(
            name="SSP1-1.9",
            description="Sustainability with very low emissions (Paris 1.5°C)",
            temp_increase_c=1.5,
            precip_change_pct=5.0,
            extreme_event_multiplier=1.2,
            sea_level_rise_m=0.4
        )
    
    @classmethod
    def ssp2_45(cls):
        """SSP2-4.5: Middle of the road."""
        return cls(
            name="SSP2-4.5",
            description="Middle of the road scenario",
            temp_increase_c=2.7,
            precip_change_pct=8.0,
            extreme_event_multiplier=1.5,
            sea_level_rise_m=0.55
        )
    
    @classmethod
    def ssp5_85(cls):
        """SSP5-8.5: Fossil-fueled development - High emissions."""
        return cls(
            name="SSP5-8.5",
            description="Fossil-fueled development with high emissions",
            temp_increase_c=4.4,
            precip_change_pct=15.0,
            extreme_event_multiplier=2.5,
            sea_level_rise_m=0.77
        )


class TimeSeriesForecaster:
    """
    Time-series forecasting for disaster frequency and risk metrics.
    
    Supports Prophet (Facebook) and ARIMA models with automatic parameter selection.
    """
    
    def __init__(self, model_type: str = "prophet"):
        self.model_type = model_type.lower()
        self.model = None
        self.fitted = False
        self.history = None
        
        if self.model_type == "prophet" and not PROPHET_AVAILABLE:
            raise ImportError("Prophet not installed. Install with: pip install prophet")
        if self.model_type == "arima" and not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not installed. Install with: pip install statsmodels")
    
    def _prepare_prophet_data(self, df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
        """Prepare data for Prophet format."""
        prophet_df = df[[date_col, value_col]].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        return prophet_df.dropna()
    
    def fit_prophet(self, df: pd.DataFrame, date_col: str = 'date', value_col: str = 'value',
                    yearly_seasonality: bool = True, 
                    weekly_seasonality: bool = False,
                    changepoint_prior_scale: float = 0.05,
                    seasonality_prior_scale: float = 10.0) -> 'TimeSeriesForecaster':
        """
        Fit Prophet model with configurable seasonality.
        
        Args:
            df: Input dataframe
            date_col: Date column name
            value_col: Value column name
            yearly_seasonality: Enable yearly seasonality
            weekly_seasonality: Enable weekly seasonality
            changepoint_prior_scale: Flexibility of trend changes
            seasonality_prior_scale: Strength of seasonality
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet not available")
        
        prophet_df = self._prepare_prophet_data(df, date_col, value_col)
        self.history = prophet_df.copy()
        
        # Initialize Prophet with disaster-appropriate settings
        self.model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=False,
            changepoint_prior_scale=changepoint_prior_scale,
            seasonality_prior_scale=seasonality_prior_scale,
            interval_width=0.95,
            growth='linear'
        )
        
        # Add monthly seasonality for disaster patterns
        self.model.add_seasonality(
            name='monthly',
            period=30.5,
            fourier_order=5
        )
        
        # Add country holidays if US data
        try:
            self.model.add_country_holidays(country_name='US')
        except:
            pass
        
        self.model.fit(prophet_df)
        self.fitted = True
        return self
    
    def fit_arima(self, df: pd.DataFrame, date_col: str = 'date', value_col: str = 'value',
                  order: Tuple[int, int, int] = None,
                  seasonal_order: Tuple[int, int, int, int] = None,
                  auto_select: bool = True) -> 'TimeSeriesForecaster':
        """
        Fit ARIMA model with optional auto-parameter selection.
        
        Args:
            df: Input dataframe
            date_col: Date column name
            value_col: Value column name
            order: ARIMA(p,d,q) order
            seasonal_order: Seasonal ARIMA(P,D,Q,s) order
            auto_select: Automatically select best order using AIC
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not available")
        
        # Prepare time series
        ts_df = df[[date_col, value_col]].copy()
        ts_df[date_col] = pd.to_datetime(ts_df[date_col])
        ts_df = ts_df.set_index(date_col).sort_index()
        ts = ts_df[value_col].dropna()
        self.history = ts.copy()
        
        if auto_select or order is None:
            order = self._auto_select_arima_order(ts)
        
        if seasonal_order is None:
            # Default seasonal order for yearly data
            seasonal_order = (1, 1, 1, 12) if len(ts) >= 24 else (0, 0, 0, 0)
        
        self.model = ARIMA(ts, order=order, seasonal_order=seasonal_order)
        self.fitted_model = self.model.fit()
        self.fitted = True
        
        return self
    
    def _auto_select_arima_order(self, ts: pd.Series, max_p: int = 3, max_d: int = 2, 
                                  max_q: int = 3) -> Tuple[int, int, int]:
        """Auto-select ARIMA order using AIC criterion."""
        best_aic = np.inf
        best_order = (0, 0, 0)
        
        # Determine differencing needed
        d = 0
        ts_diff = ts.copy()
        while d < max_d:
            result = adfuller(ts_diff.dropna())
            if result[1] < 0.05:  # Stationary
                break
            ts_diff = ts_diff.diff().dropna()
            d += 1
        
        # Grid search for p and q
        for p in range(max_p + 1):
            for q in range(max_q + 1):
                try:
                    model = ARIMA(ts, order=(p, d, q))
                    fitted = model.fit()
                    if fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d, q)
                except:
                    continue
        
        return best_order
    
    def forecast(self, periods: int = 12, freq: str = 'MS',
                 include_history: bool = False) -> ForecastResult:
        """
        Generate forecasts.
        
        Args:
            periods: Number of periods to forecast
            freq: Frequency string ('D'=daily, 'MS'=month start, 'YS'=year start)
            include_history: Include fitted values in output
            
        Returns:
            ForecastResult with predictions and confidence intervals
        """
        if not self.fitted:
            raise ValueError("Model not fitted. Call fit_*() first.")
        
        if self.model_type == "prophet":
            return self._forecast_prophet(periods, freq, include_history)
        else:
            return self._forecast_arima(periods, include_history)
    
    def _forecast_prophet(self, periods: int, freq: str, 
                          include_history: bool) -> ForecastResult:
        """Generate Prophet forecast."""
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self.model.predict(future)
        
        if not include_history:
            forecast = forecast[forecast['ds'] > self.history['ds'].max()]
        
        # Calculate metrics on training data
        train_pred = self.model.predict(self.history)
        mae = mean_absolute_error(self.history['y'], train_pred['yhat'])
        rmse = np.sqrt(mean_squared_error(self.history['y'], train_pred['yhat']))
        
        # Extract components
        components = {
            'trend': forecast['trend'].values if 'trend' in forecast.columns else None,
            'yearly': forecast['yearly'].values if 'yearly' in forecast.columns else None,
            'weekly': forecast['weekly'].values if 'weekly' in forecast.columns else None,
        }
        
        return ForecastResult(
            dates=pd.DatetimeIndex(forecast['ds']),
            forecast=forecast['yhat'].values,
            lower_bound=forecast['yhat_lower'].values,
            upper_bound=forecast['yhat_upper'].values,
            model_name=f"Prophet ({self.model.yearly_seasonality})",
            metrics={'mae': mae, 'rmse': rmse},
            components=components
        )
    
    def _forecast_arima(self, periods: int, include_history: bool) -> ForecastResult:
        """Generate ARIMA forecast."""
        forecast_result = self.fitted_model.get_forecast(steps=periods)
        
        forecast_mean = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=0.05)
        
        # Calculate metrics
        fitted_values = self.fitted_model.fittedvalues
        mae = mean_absolute_error(self.history, fitted_values)
        rmse = np.sqrt(mean_squared_error(self.history, fitted_values))
        
        # Generate future dates
        last_date = self.history.index[-1]
        freq = pd.infer_freq(self.history.index) or 'MS'
        future_dates = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
        
        return ForecastResult(
            dates=future_dates,
            forecast=forecast_mean.values,
            lower_bound=conf_int.iloc[:, 0].values,
            upper_bound=conf_int.iloc[:, 1].values,
            model_name=f"ARIMA{self.fitted_model.model.order}",
            metrics={'mae': mae, 'rmse': rmse},
            components=None
        )
    
    def cross_validate(self, n_splits: int = 5) -> Dict[str, float]:
        """Time-series cross-validation."""
        if not SKLEARN_AVAILABLE:
            return {"error": "sklearn not available"}
        
        if self.model_type != "arima" or not self.fitted:
            return {"error": "Cross-validation only supported for fitted ARIMA models"}
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        scores = {'mae': [], 'rmse': [], 'mape': []}
        
        ts = self.history
        for train_idx, test_idx in tscv.split(ts):
            train, test = ts.iloc[train_idx], ts.iloc[test_idx]
            
            try:
                model = ARIMA(train, order=self.fitted_model.model.order)
                fitted = model.fit()
                pred = fitted.forecast(steps=len(test))
                
                scores['mae'].append(mean_absolute_error(test, pred))
                scores['rmse'].append(np.sqrt(mean_squared_error(test, pred)))
                scores['mape'].append(np.mean(np.abs((test - pred) / (test + 1e-10))) * 100)
            except:
                continue
        
        return {
            'cv_mae_mean': np.mean(scores['mae']),
            'cv_mae_std': np.std(scores['mae']),
            'cv_rmse_mean': np.mean(scores['rmse']),
            'cv_rmse_std': np.std(scores['rmse']),
            'cv_mape_mean': np.mean(scores['mape']),
            'cv_mape_std': np.std(scores['mape']),
        }


class DisasterPredictor:
    """
    Machine learning models for disaster prediction.
    
    Uses Gradient Boosting and Random Forest to predict:
    - Disaster occurrence probability
    - Disaster severity
    - Risk score trajectories
    """
    
    def __init__(self, model_type: str = "gradient_boosting"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.feature_names = None
        self.target_col = None
        
    def prepare_features(self, df: pd.DataFrame, 
                         feature_cols: List[str],
                         target_col: str,
                         lag_features: bool = True,
                         lag_periods: List[int] = [1, 3, 6, 12]) -> pd.DataFrame:
        """
        Prepare features for ML models with optional lag features.
        
        Args:
            df: Input dataframe
            feature_cols: Feature column names
            target_col: Target column name
            lag_features: Create lagged features
            lag_periods: Periods for lag features
            
        Returns:
            DataFrame with engineered features
        """
        self.feature_names = feature_cols.copy()
        self.target_col = target_col
        
        result = df.copy()
        
        if lag_features:
            for col in feature_cols:
                if col in result.columns:
                    for lag in lag_periods:
                        lag_col = f"{col}_lag_{lag}"
                        result[lag_col] = result[col].shift(lag)
                        self.feature_names.append(lag_col)
            
            # Add rolling statistics
            for col in feature_cols[:3]:  # Limit to first 3 features
                if col in result.columns:
                    result[f"{col}_rolling_mean_6"] = result[col].rolling(6).mean()
                    result[f"{col}_rolling_std_6"] = result[col].rolling(6).std()
                    self.feature_names.extend([f"{col}_rolling_mean_6", f"{col}_rolling_std_6"])
        
        # Add time-based features
        if 'date' in result.columns:
            result['month'] = pd.to_datetime(result['date']).dt.month
            result['year'] = pd.to_datetime(result['date']).dt.year
            result['quarter'] = pd.to_datetime(result['date']).dt.quarter
            self.feature_names.extend(['month', 'year', 'quarter'])
        
        return result.dropna()
    
    def fit(self, df: pd.DataFrame, 
            feature_cols: Optional[List[str]] = None,
            target_col: str = 'disaster_occurred') -> 'DisasterPredictor':
        """
        Fit the prediction model.
        
        Args:
            df: Training dataframe
            feature_cols: Feature columns (uses prepared features if None)
            target_col: Target column name
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn not available")
        
        if feature_cols is None:
            feature_cols = self.feature_names
        
        X = df[feature_cols].values
        y = df[target_col].values
        
        X_scaled = self.scaler.fit_transform(X)
        
        if self.model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                random_state=42
            )
        
        self.model.fit(X_scaled, y)
        
        # Calculate feature importance
        self.feature_importance_ = dict(zip(feature_cols, self.model.feature_importances_))
        
        return self
    
    def predict(self, df: pd.DataFrame, 
                feature_cols: Optional[List[str]] = None) -> np.ndarray:
        """Generate predictions."""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        if feature_cols is None:
            feature_cols = self.feature_names
        
        X = df[feature_cols].values
        X_scaled = self.scaler.transform(X)
        
        return self.model.predict(X_scaled)
    
    def predict_proba(self, df: pd.DataFrame,
                      feature_cols: Optional[List[str]] = None) -> np.ndarray:
        """Generate probability predictions (for classification)."""
        preds = self.predict(df, feature_cols)
        # Convert to probability using sigmoid
        return 1 / (1 + np.exp(-preds))
    
    def evaluate(self, df: pd.DataFrame, 
                 feature_cols: Optional[List[str]] = None,
                 target_col: Optional[str] = None) -> Dict[str, float]:
        """Evaluate model performance."""
        if feature_cols is None:
            feature_cols = self.feature_names
        if target_col is None:
            target_col = self.target_col
        
        X = df[feature_cols].values
        y = df[target_col].values
        X_scaled = self.scaler.transform(X)
        
        preds = self.model.predict(X_scaled)
        
        return {
            'mae': mean_absolute_error(y, preds),
            'rmse': np.sqrt(mean_squared_error(y, preds)),
            'r2': r2_score(y, preds),
            'mape': np.mean(np.abs((y - preds) / (y + 1e-10))) * 100
        }


class ClimateScenarioModeler:
    """
    Climate change scenario modeling for risk projections.
    
    Applies IPCC SSP scenarios to project future risk under different
    climate trajectories.
    """
    
    def __init__(self, baseline_data: pd.DataFrame):
        self.baseline = baseline_data.copy()
        self.scenarios = {
            'ssp1_19': ClimateScenario.ssp1_19(),
            'ssp2_45': ClimateScenario.ssp2_45(),
            'ssp5_85': ClimateScenario.ssp5_85(),
        }
    
    def project_risk(self, 
                     scenario_name: str,
                     years_ahead: int = 30,
                     baseline_years: int = 10) -> pd.DataFrame:
        """
        Project risk scores under a climate scenario.
        
        Args:
            scenario_name: SSP scenario name ('ssp1_19', 'ssp2_45', 'ssp5_85')
            years_ahead: Years to project into future
            baseline_years: Years of baseline data
            
        Returns:
            DataFrame with projected risk scores
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = self.scenarios[scenario_name]
        
        # Calculate baseline risk
        baseline_risk = self.baseline['risk_score'].mean() if 'risk_score' in self.baseline.columns else 0.5
        
        # Calculate annual increase based on scenario
        # Linear interpolation from now to 2100
        years_to_2100 = 2100 - datetime.now().year
        annual_increase = (scenario.extreme_event_multiplier - 1) / years_to_2100
        
        # Generate projections
        projections = []
        for year in range(1, years_ahead + 1):
            year_factor = 1 + (annual_increase * year)
            
            # Compound effect on disaster frequency
            disaster_multiplier = year_factor ** 1.5  # Non-linear impact
            
            # Infrastructure degradation factor
            infrastructure_factor = 1 - (0.005 * year)  # Gradual degradation
            
            # Combined risk projection
            projected_risk = baseline_risk * disaster_multiplier / infrastructure_factor
            projected_risk = min(projected_risk, 1.0)  # Cap at 1.0
            
            projections.append({
                'year': datetime.now().year + year,
                'years_from_now': year,
                'scenario': scenario.name,
                'projected_risk_score': round(projected_risk, 4),
                'disaster_frequency_multiplier': round(disaster_multiplier, 3),
                'infrastructure_resilience': round(infrastructure_factor, 3),
                'temp_increase_c': round(scenario.temp_increase_c * (year / years_to_2100), 2),
            })
        
        return pd.DataFrame(projections)
    
    def compare_scenarios(self, years_ahead: int = 30) -> pd.DataFrame:
        """Compare all scenarios side by side."""
        all_projections = []
        
        for scenario_name in self.scenarios.keys():
            proj = self.project_risk(scenario_name, years_ahead)
            all_projections.append(proj)
        
        return pd.concat(all_projections, ignore_index=True)
    
    def get_scenario_recommendations(self, scenario_name: str) -> List[Dict]:
        """Get adaptation recommendations for a scenario."""
        scenario = self.scenarios.get(scenario_name)
        if not scenario:
            return []
        
        recommendations = []
        
        if scenario.extreme_event_multiplier > 1.5:
            recommendations.append({
                'priority': 'Critical',
                'category': 'Infrastructure',
                'action': 'Harden critical infrastructure against extreme weather',
                'timeline': '5-10 years',
                'estimated_cost': 'High'
            })
        
        if scenario.temp_increase_c > 2.0:
            recommendations.append({
                'priority': 'High',
                'category': 'Health Systems',
                'action': 'Expand heat emergency response capabilities',
                'timeline': '3-5 years',
                'estimated_cost': 'Medium'
            })
        
        recommendations.append({
            'priority': 'Medium',
            'category': 'Early Warning',
            'action': 'Enhance multi-hazard early warning systems',
            'timeline': '2-3 years',
            'estimated_cost': 'Medium'
        })
        
        return recommendations


class RiskTrajectoryAnalyzer:
    """
    Analyze and visualize risk trajectories over time.
    
    Combines historical trends, forecasts, and climate scenarios
    to provide comprehensive risk trajectory views.
    """
    
    def __init__(self, county_fips: str, historical_data: pd.DataFrame):
        self.fips = county_fips
        self.history = historical_data.copy()
        self.forecaster = None
        self.climate_modeler = None
    
    def analyze_trajectory(self, 
                          forecast_years: int = 10,
                          scenario: str = 'ssp2_45') -> Dict:
        """
        Complete trajectory analysis for a county.
        
        Returns:
            Dictionary with historical trends, forecasts, and projections
        """
        results = {
            'county_fips': self.fips,
            'historical': {},
            'forecast': {},
            'climate_projection': {},
            'risk_trend': 'stable',
            'confidence': 'medium'
        }
        
        # Historical trend analysis
        if 'risk_score' in self.history.columns and len(self.history) >= 2:
            risk_series = self.history['risk_score'].dropna()
            
            # Calculate trend
            x = np.arange(len(risk_series))
            slope, intercept = np.polyfit(x, risk_series, 1)
            
            results['historical'] = {
                'mean_risk': float(risk_series.mean()),
                'trend_slope': float(slope),
                'trend_direction': 'increasing' if slope > 0.01 else 'decreasing' if slope < -0.01 else 'stable',
                'volatility': float(risk_series.std()),
                'data_points': len(risk_series)
            }
        
        # Generate forecast if enough data
        if len(self.history) >= 12:
            try:
                self.forecaster = TimeSeriesForecaster(model_type='prophet')
                
                # Prepare data
                forecast_df = self.history.reset_index()
                if 'date' not in forecast_df.columns:
                    forecast_df['date'] = pd.date_range(end=datetime.now(), periods=len(forecast_df), freq='MS')
                
                if 'risk_score' in forecast_df.columns:
                    self.forecaster.fit_prophet(
                        forecast_df, 
                        date_col='date', 
                        value_col='risk_score'
                    )
                    
                    forecast_result = self.forecaster.forecast(
                        periods=forecast_years * 12,  # Monthly forecasts
                        freq='MS'
                    )
                    
                    results['forecast'] = {
                        'model': forecast_result.model_name,
                        'forecast_values': forecast_result.forecast.tolist(),
                        'lower_bound': forecast_result.lower_bound.tolist(),
                        'upper_bound': forecast_result.upper_bound.tolist(),
                        'dates': forecast_result.dates.strftime('%Y-%m-%d').tolist(),
                        'metrics': forecast_result.metrics
                    }
                    
                    # Determine trend from forecast
                    first_half = np.mean(forecast_result.forecast[:len(forecast_result.forecast)//2])
                    second_half = np.mean(forecast_result.forecast[len(forecast_result.forecast)//2:])
                    
                    if second_half > first_half * 1.1:
                        results['risk_trend'] = 'increasing'
                    elif second_half < first_half * 0.9:
                        results['risk_trend'] = 'decreasing'
                    else:
                        results['risk_trend'] = 'stable'
                        
            except Exception as e:
                results['forecast_error'] = str(e)
        
        # Climate scenario projection
        try:
            self.climate_modeler = ClimateScenarioModeler(self.history)
            climate_proj = self.climate_modeler.project_risk(scenario, years_ahead=forecast_years)
            
            results['climate_projection'] = {
                'scenario': scenario,
                'projections': climate_proj.to_dict('records'),
                'final_risk_score': float(climate_proj['projected_risk_score'].iloc[-1]),
                'risk_increase_pct': float(
                    (climate_proj['projected_risk_score'].iloc[-1] / 
                     climate_proj['projected_risk_score'].iloc[0] - 1) * 100
                )
            }
            
            results['recommendations'] = self.climate_modeler.get_scenario_recommendations(scenario)
            
        except Exception as e:
            results['climate_error'] = str(e)
        
        return results
    
    def detect_acceleration(self, window: int = 5) -> Dict:
        """Detect if disaster frequency is accelerating."""
        if 'disaster_count' not in self.history.columns:
            return {'error': 'No disaster count data available'}
        
        disasters = self.history['disaster_count'].dropna()
        
        if len(disasters) < window * 2:
            return {'error': 'Insufficient data for acceleration analysis'}
        
        # Split into recent and older periods
        recent = disasters.iloc[-window:].mean()
        older = disasters.iloc[-(window*2):-window].mean()
        
        acceleration_ratio = recent / (older + 0.001)
        
        return {
            'acceleration_ratio': float(acceleration_ratio),
            'is_accelerating': acceleration_ratio > 1.5,
            'recent_avg': float(recent),
            'older_avg': float(older),
            'interpretation': (
                'Significant acceleration' if acceleration_ratio > 2.0 else
                'Moderate acceleration' if acceleration_ratio > 1.5 else
                'Stable' if acceleration_ratio > 0.8 else
                'Decelerating'
            )
        }


class PredictiveModelManager:
    """
    Central manager for all predictive models.
    
    Handles model persistence, batch predictions, and model comparison.
    """
    
    def __init__(self, models_dir: Path = MODELS_DIR):
        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.active_models = {}
    
    def save_model(self, model, name: str) -> str:
        """Save a model to disk."""
        import joblib
        
        model_path = self.models_dir / f"{name}.pkl"
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata = {
            'name': name,
            'saved_at': datetime.now().isoformat(),
            'type': type(model).__name__
        }
        
        meta_path = self.models_dir / f"{name}_metadata.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(model_path)
    
    def load_model(self, name: str):
        """Load a model from disk."""
        import joblib
        
        model_path = self.models_dir / f"{name}.pkl"
        if not model_path.exists():
            return None
        
        return joblib.load(model_path)
    
    def list_models(self) -> List[Dict]:
        """List all saved models."""
        models = []
        
        for meta_file in self.models_dir.glob("*_metadata.json"):
            with open(meta_file) as f:
                metadata = json.load(f)
                models.append(metadata)
        
        return models
    
    def batch_forecast(self, 
                       counties: List[str],
                       data_loader,
                       forecast_years: int = 10) -> Dict[str, ForecastResult]:
        """
        Generate forecasts for multiple counties.
        
        Args:
            counties: List of county FIPS codes
            data_loader: Function to load historical data for a county
            forecast_years: Years to forecast
            
        Returns:
            Dictionary mapping county FIPS to forecast results
        """
        results = {}
        
        for fips in counties:
            try:
                historical = data_loader(fips)
                if historical is not None and len(historical) >= 12:
                    analyzer = RiskTrajectoryAnalyzer(fips, historical)
                    trajectory = analyzer.analyze_trajectory(forecast_years)
                    results[fips] = trajectory
            except Exception as e:
                results[fips] = {'error': str(e)}
        
        return results


def create_synthetic_historical_data(n_years: int = 10, 
                                     trend: str = 'increasing',
                                     random_seed: int = 42) -> pd.DataFrame:
    """
    Create synthetic historical data for testing.
    
    Args:
        n_years: Number of years of data
        trend: 'increasing', 'decreasing', or 'stable'
        random_seed: Random seed for reproducibility
        
    Returns:
        DataFrame with synthetic historical data
    """
    np.random.seed(random_seed)
    
    dates = pd.date_range(end=datetime.now(), periods=n_years*12, freq='MS')
    
    # Base risk score
    base_risk = 0.4
    
    # Trend component
    if trend == 'increasing':
        trend_component = np.linspace(0, 0.3, len(dates))
    elif trend == 'decreasing':
        trend_component = np.linspace(0.3, 0, len(dates))
    else:
        trend_component = np.zeros(len(dates))
    
    # Seasonal component
    seasonal = 0.05 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)
    
    # Random noise
    noise = np.random.normal(0, 0.03, len(dates))
    
    # Disaster count (Poisson-like)
    lambda_disasters = 2 + trend_component * 5 + seasonal * 2
    disaster_count = np.random.poisson(np.maximum(lambda_disasters, 0.1))
    
    risk_score = np.clip(base_risk + trend_component + seasonal + noise, 0, 1)
    
    return pd.DataFrame({
        'date': dates,
        'risk_score': risk_score,
        'disaster_count': disaster_count,
        'vulnerability_index': np.clip(0.3 + trend_component * 0.5 + np.random.normal(0, 0.05, len(dates)), 0, 1),
        'isolation_index': np.clip(0.4 + np.random.normal(0, 0.05, len(dates)), 0, 1),
    })


def main():
    """CLI for predictive modeling."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ResilienceAI Predictive Modeling")
    parser.add_argument("--forecast", action="store_true", help="Generate forecast")
    parser.add_argument("--model-type", choices=["prophet", "arima"], default="prophet")
    parser.add_argument("--periods", type=int, default=12, help="Forecast periods")
    parser.add_argument("--scenario", choices=["ssp1_19", "ssp2_45", "ssp5_85"], 
                       default="ssp2_45", help="Climate scenario")
    parser.add_argument("--trajectory", action="store_true", help="Full trajectory analysis")
    parser.add_argument("--test-data", action="store_true", help="Use synthetic test data")
    
    args = parser.parse_args()
    
    # Load or create data
    if args.test_data:
        df = create_synthetic_historical_data(n_years=10, trend='increasing')
        print("Using synthetic test data")
    else:
        # Try to load real data
        data_path = PROCESSED_DIR / "county_features.csv"
        if data_path.exists():
            df = pd.read_csv(data_path)
            print(f"Loaded {len(df)} records")
        else:
            print("No data found, using synthetic data")
            df = create_synthetic_historical_data(n_years=10)
    
    if args.forecast:
        print(f"\nGenerating {args.model_type} forecast for {args.periods} periods...")
        
        forecaster = TimeSeriesForecaster(model_type=args.model_type)
        
        if args.model_type == "prophet":
            forecaster.fit_prophet(df, date_col='date', value_col='risk_score')
        else:
            forecaster.fit_arima(df, date_col='date', value_col='risk_score')
        
        result = forecaster.forecast(periods=args.periods)
        
        print(f"\nForecast Results ({result.model_name}):")
        print(f"  MAE: {result.metrics['mae']:.4f}")
        print(f"  RMSE: {result.metrics['rmse']:.4f}")
        print(f"\nNext {min(5, args.periods)} periods:")
        for i in range(min(5, args.periods)):
            print(f"  {result.dates[i].strftime('%Y-%m')}: "
                  f"{result.forecast[i]:.3f} "
                  f"[{result.lower_bound[i]:.3f}, {result.upper_bound[i]:.3f}]")
    
    if args.trajectory:
        print(f"\nFull trajectory analysis with scenario {args.scenario}...")
        
        analyzer = RiskTrajectoryAnalyzer("TEST001", df)
        trajectory = analyzer.analyze_trajectory(forecast_years=10, scenario=args.scenario)
        
        print(f"\nHistorical Trend:")
        if 'historical' in trajectory:
            hist = trajectory['historical']
            print(f"  Mean Risk: {hist.get('mean_risk', 'N/A')}")
            print(f"  Trend: {hist.get('trend_direction', 'N/A')}")
        
        print(f"\nForecast Trend: {trajectory.get('risk_trend', 'N/A')}")
        
        if 'climate_projection' in trajectory:
            proj = trajectory['climate_projection']
            print(f"\nClimate Projection ({proj.get('scenario', 'N/A')}):")
            print(f"  Final Risk Score: {proj.get('final_risk_score', 'N/A'):.3f}")
            print(f"  Risk Increase: {proj.get('risk_increase_pct', 'N/A'):.1f}%")
        
        if 'recommendations' in trajectory:
            print(f"\nRecommendations:")
            for rec in trajectory['recommendations'][:3]:
                print(f"  [{rec.get('priority', 'N/A')}] {rec.get('action', 'N/A')}")


if __name__ == "__main__":
    main()
