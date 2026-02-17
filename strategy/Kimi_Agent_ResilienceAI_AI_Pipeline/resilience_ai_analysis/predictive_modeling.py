"""
Predictive Modeling for Digital Twin
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler


@dataclass
class PredictionResult:
    """Prediction result container"""
    prediction_id: str
    model_type: str
    target_variable: str
    prediction_value: float
    confidence_interval: Tuple[float, float]
    probability: Optional[float] = None
    feature_importance: Dict[str, float] = None
    horizon_days: int = 30


class FailurePredictionModel:
    """Asset failure prediction model"""
    
    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_importance = {}
    
    def prepare_features(self, asset: Dict, historical_data: List[Dict]) -> np.ndarray:
        """Extract features from asset data"""
        features = [
            asset.get("age_years", 0),
            asset.get("condition_index", 0.5),
            asset.get("criticality_score", 0.5),
            asset.get("maintenance_count", 0),
            asset.get("inspection_score", 0.5),
            1 if asset.get("asset_type") == "bridge" else 0,
            1 if asset.get("asset_type") == "road" else 0,
            1 if asset.get("asset_type") == "building" else 0,
        ]
        
        if historical_data:
            conditions = [h.get("condition", 0.5) for h in historical_data]
            features.extend([
                np.mean(conditions),
                np.std(conditions) if len(conditions) > 1 else 0,
                conditions[-1] - conditions[0] if len(conditions) > 1 else 0,
                len(historical_data)
            ])
        else:
            features.extend([0.5, 0, 0, 0])
        
        features.extend([
            asset.get("flood_exposure", 0),
            asset.get("seismic_risk", 0),
            asset.get("weather_exposure", 0)
        ])
        
        return np.array(features).reshape(1, -1)
    
    def train(self, training_data: List[Dict]):
        """Train the failure prediction model"""
        X, y = [], []
        for sample in training_data:
            features = self.prepare_features(sample["asset"], sample["history"])
            X.append(features[0])
            y.append(sample["failed"])
        
        X = np.array(X)
        y = np.array(y)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        feature_names = [
            "age", "condition", "criticality", "maintenance", "inspection",
            "is_bridge", "is_road", "is_building", "avg_condition", 
            "condition_std", "condition_trend", "history_length",
            "flood_exposure", "seismic_risk", "weather_exposure"
        ]
        self.feature_importance = dict(zip(feature_names, self.model.feature_importances_))
    
    def predict(self, asset: Dict, historical_data: List[Dict]) -> PredictionResult:
        """Predict failure probability"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        features = self.prepare_features(asset, historical_data)
        features_scaled = self.scaler.transform(features)
        prob = self.model.predict_proba(features_scaled)[0][1]
        
        return PredictionResult(
            prediction_id=f"pred_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            model_type="failure_prediction",
            target_variable="asset_failure",
            prediction_value=prob,
            confidence_interval=(max(0, prob - 0.1), min(1, prob + 0.1)),
            probability=prob,
            feature_importance=self.feature_importance
        )


class DegradationModel:
    """Asset degradation prediction model"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, time_series_data: List[Dict]):
        """Train degradation model on time series"""
        X, y = [], []
        for series in time_series_data:
            for i in range(len(series["conditions"]) - 1):
                X.append([
                    series["conditions"][i],
                    series["age"],
                    series["maintenance"],
                    series["usage"]
                ])
                y.append(series["conditions"][i + 1])
        
        X = np.array(X)
        y = np.array(y)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict_degradation(self, current_condition: float, age: float,
                           maintenance: float, usage: float,
                           horizon_years: int = 5) -> List[float]:
        """Predict condition over time horizon"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        conditions = [current_condition]
        for _ in range(horizon_years):
            features = np.array([[conditions[-1], age, maintenance, usage]])
            features_scaled = self.scaler.transform(features)
            next_condition = self.model.predict(features_scaled)[0]
            conditions.append(max(0, min(1, next_condition)))
            age += 1
        
        return conditions


class PredictiveAnalyticsEngine:
    """Main predictive analytics engine"""
    
    def __init__(self, county_twin: Any):
        self.county_twin = county_twin
        self.failure_model = FailurePredictionModel()
        self.degradation_model = DegradationModel()
        self.prediction_cache: Dict[str, PredictionResult] = {}
    
    def predict_asset_failures(self, horizon_days: int = 30) -> List[PredictionResult]:
        """Predict failures for all assets"""
        predictions = []
        for asset_id, asset in self.county_twin.assets.items():
            history = self._get_asset_history(asset_id)
            pred = self.failure_model.predict(asset, history)
            pred.horizon_days = horizon_days
            predictions.append(pred)
            self.prediction_cache[asset_id] = pred
        return predictions
    
    def predict_maintenance_needs(self) -> List[Dict]:
        """Predict maintenance needs"""
        predictions = self.predict_asset_failures(horizon_days=90)
        maintenance_needs = []
        for pred in predictions:
            if pred.probability > 0.5:
                maintenance_needs.append({
                    "asset_id": pred.prediction_id.split("_")[-1],
                    "failure_probability": pred.probability,
                    "recommended_action": "immediate_inspection" if pred.probability > 0.8 else "schedule_maintenance",
                    "priority": "critical" if pred.probability > 0.8 else "high" if pred.probability > 0.6 else "medium"
                })
        return sorted(maintenance_needs, key=lambda x: x["failure_probability"], reverse=True)
    
    def predict_lifecycle_costs(self, asset_id: str, planning_years: int = 20) -> Dict:
        """Predict lifecycle costs for asset"""
        asset = self.county_twin.assets.get(asset_id, {})
        current_condition = asset.get("condition_index", 0.5)
        age = asset.get("age_years", 0)
        
        conditions = self.degradation_model.predict_degradation(
            current_condition, age, 
            asset.get("maintenance_frequency", 1),
            asset.get("usage_intensity", 0.5),
            planning_years
        )
        
        maintenance_costs = []
        replacement_cost = asset.get("replacement_cost", 1000000)
        
        for year, condition in enumerate(conditions[1:], 1):
            if condition < 0.3:
                cost = replacement_cost * 0.2
            elif condition < 0.5:
                cost = replacement_cost * 0.1
            elif condition < 0.7:
                cost = replacement_cost * 0.05
            else:
                cost = replacement_cost * 0.02
            
            maintenance_costs.append({
                "year": year,
                "predicted_condition": condition,
                "maintenance_cost": cost
            })
        
        total_cost = sum(m["maintenance_cost"] for m in maintenance_costs)
        
        return {
            "asset_id": asset_id,
            "planning_years": planning_years,
            "total_maintenance_cost": total_cost,
            "annual_costs": maintenance_costs,
            "replacement_recommended": any(c < 0.2 for c in conditions),
            "optimal_replacement_year": next((i for i, c in enumerate(conditions) if c < 0.2), None)
        }
    
    def _get_asset_history(self, asset_id: str) -> List[Dict]:
        """Get historical data for asset"""
        return []
    
    def get_risk_ranking(self) -> List[Dict]:
        """Get assets ranked by risk"""
        predictions = self.predict_asset_failures()
        ranked = []
        for pred in predictions:
            ranked.append({
                "prediction_id": pred.prediction_id,
                "failure_probability": pred.probability,
                "confidence_low": pred.confidence_interval[0],
                "confidence_high": pred.confidence_interval[1]
            })
        return sorted(ranked, key=lambda x: x["failure_probability"], reverse=True)
