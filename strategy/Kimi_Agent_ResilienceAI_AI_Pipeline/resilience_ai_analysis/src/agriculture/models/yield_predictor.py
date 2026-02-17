"""
Crop Yield Prediction Model for ResilienceAI
Uses machine learning to predict crop yields based on weather, soil, and management data
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path
import joblib

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

logger = logging.getLogger(__name__)


@dataclass
class YieldPrediction:
    """Yield prediction result"""
    county_fips: str
    commodity: str
    predicted_yield: float
    prediction_interval: Tuple[float, float]
    confidence: float
    factors: Dict[str, float]
    model_version: str


class CropYieldPredictor:
    """Machine learning model for crop yield prediction"""
    
    def __init__(self, model_path: Optional[Path] = None):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.model_version = "1.0.0"
        self.model_path = model_path or Path("models/agriculture/yield_predictor.pkl")
        self.feature_importance = {}
    
    def prepare_features(self, yield_data: pd.DataFrame, weather_data: pd.DataFrame,
                         soil_data: pd.DataFrame, include_trends: bool = True) -> pd.DataFrame:
        """Prepare feature matrix for yield prediction"""
        features = pd.DataFrame()
        
        df = yield_data.merge(weather_data, on=['county_fips', 'year'], how='left')
        df = df.merge(soil_data, on='county_fips', how='left')
        
        # Weather features
        features['growing_degree_days'] = df.get('gdd', 0)
        features['precipitation_growing_season'] = df.get('growing_season_precip', 0)
        features['avg_temp_growing_season'] = df.get('avg_temp_growing', 0)
        features['drought_stress_index'] = df.get('drought_index', 0)
        features['spring_precipitation'] = df.get('spring_precip', 0)
        
        # Soil features
        features['soil_water_capacity'] = df.get('aws100', 0)
        features['soil_ph'] = df.get('ph1to1h2o', 7.0)
        features['soil_organic_matter'] = df.get('om', 0)
        
        # Historical yield features
        if include_trends:
            features['previous_year_yield'] = df.groupby('county_fips')['yield'].shift(1)
            features['previous_year_yield'] = features['previous_year_yield'].fillna(
                df.groupby('county_fips')['yield'].transform('mean')
            )
            features['three_year_avg_yield'] = df.groupby('county_fips')['yield'].transform(
                lambda x: x.rolling(3, min_periods=1).mean()
            )
        
        features['yield'] = df['yield']
        features['county_fips'] = df['county_fips']
        features['year'] = df['year']
        features['commodity'] = df['commodity']
        
        return features.fillna(features.median())
    
    def train(self, features: pd.DataFrame, model_type: str = 'gradient_boosting',
              cv_folds: int = 5) -> Dict[str, float]:
        """Train the yield prediction model"""
        feature_cols = [
            'growing_degree_days', 'precipitation_growing_season',
            'avg_temp_growing_season', 'drought_stress_index',
            'spring_precipitation', 'soil_water_capacity',
            'soil_ph', 'soil_organic_matter',
            'previous_year_yield', 'three_year_avg_yield'
        ]
        
        self.feature_names = [c for c in feature_cols if c in features.columns]
        X = features[self.feature_names]
        y = features['yield']
        
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = GradientBoostingRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42
        )
        
        tscv = TimeSeriesSplit(n_splits=cv_folds)
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=tscv, scoring='r2')
        
        self.model.fit(X_scaled, y)
        
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        y_pred = self.model.predict(X_scaled)
        
        return {
            'cv_r2_mean': float(np.mean(cv_scores)),
            'cv_r2_std': float(np.std(cv_scores)),
            'train_r2': r2_score(y, y_pred),
            'train_rmse': np.sqrt(mean_squared_error(y, y_pred)),
            'train_mae': mean_absolute_error(y, y_pred)
        }
    
    def predict(self, features: pd.DataFrame, return_interval: bool = True) -> List[YieldPrediction]:
        """Make yield predictions"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X = features[self.feature_names]
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        
        if return_interval and hasattr(self.model, 'estimators_'):
            all_predictions = np.array([tree.predict(X_scaled) for tree in self.model.estimators_])
            lower = np.percentile(all_predictions, 5, axis=0)
            upper = np.percentile(all_predictions, 95, axis=0)
        else:
            lower, upper = predictions * 0.85, predictions * 1.15
        
        results = []
        for i, pred in enumerate(predictions):
            interval_width = upper[i] - lower[i]
            confidence = max(0, 1 - (interval_width / pred)) if pred > 0 else 0
            
            factors = {feat: float(features[feat].iloc[i]) for feat in self.feature_names}
            
            results.append(YieldPrediction(
                county_fips=features['county_fips'].iloc[i],
                commodity=features['commodity'].iloc[i],
                predicted_yield=round(pred, 2),
                prediction_interval=(round(lower[i], 2), round(upper[i], 2)),
                confidence=round(confidence, 3),
                factors=factors,
                model_version=self.model_version
            ))
        
        return results
    
    def save(self, path: Optional[Path] = None):
        """Save model to disk"""
        save_path = path or self.model_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'version': self.model_version
        }, save_path)
        logger.info(f"Model saved to {save_path}")
    
    def load(self, path: Optional[Path] = None):
        """Load model from disk"""
        load_path = path or self.model_path
        if not load_path.exists():
            raise FileNotFoundError(f"Model file not found: {load_path}")
        
        data = joblib.load(load_path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.feature_importance = data['feature_importance']
        self.model_version = data['version']
        logger.info(f"Model loaded from {load_path}")
