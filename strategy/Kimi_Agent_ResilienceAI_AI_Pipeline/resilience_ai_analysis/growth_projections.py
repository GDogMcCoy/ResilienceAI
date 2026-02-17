"""
Growth Projection and Capacity Planning
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class GrowthModel(Enum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGISTIC = "logistic"


@dataclass
class GrowthProjection:
    """Growth projection for a service"""
    service_name: str
    metric_name: str
    projection_date: datetime
    
    # Historical data
    historical_values: List[float]
    historical_dates: List[datetime]
    
    # Projections by time horizon
    projections_1m: float
    projections_3m: float
    projections_6m: float
    projections_12m: float
    
    # Confidence intervals
    confidence_lower_12m: float
    confidence_upper_12m: float
    
    # Growth rate
    monthly_growth_rate: float
    annual_growth_rate: float
    
    # Model used
    model: GrowthModel
    model_accuracy: float


class GrowthProjector:
    """Project future growth based on historical trends"""
    
    def __init__(self):
        self.growth_models = {
            GrowthModel.LINEAR: self._linear_growth,
            GrowthModel.EXPONENTIAL: self._exponential_growth,
            GrowthModel.LOGISTIC: self._logistic_growth,
        }
        self.projection_history: List[GrowthProjection] = []
    
    def project_growth(
        self,
        service_name: str,
        metric_name: str,
        historical_data: List[float],
        historical_dates: List[datetime],
        model: GrowthModel = GrowthModel.EXPONENTIAL
    ) -> GrowthProjection:
        """Project growth for a service metric"""
        
        if len(historical_data) < 3:
            raise ValueError("Need at least 3 data points for projection")
        
        # Fit growth model
        growth_fn = self.growth_models.get(model, self._exponential_growth)
        params, accuracy = self._fit_model(historical_data, model)
        
        # Calculate growth rates
        monthly_growth = self._calculate_monthly_growth_rate(historical_data)
        annual_growth = (1 + monthly_growth) ** 12 - 1
        
        # Project forward
        last_value = historical_data[-1]
        
        # Projections at different horizons
        projection_1m = growth_fn(last_value, params, 1)
        projection_3m = growth_fn(last_value, params, 3)
        projection_6m = growth_fn(last_value, params, 6)
        projection_12m = growth_fn(last_value, params, 12)
        
        # Calculate confidence intervals
        std_error = np.std(historical_data) * 0.5
        confidence_lower = projection_12m - 1.96 * std_error
        confidence_upper = projection_12m + 1.96 * std_error
        
        projection = GrowthProjection(
            service_name=service_name,
            metric_name=metric_name,
            projection_date=datetime.now(),
            historical_values=historical_data,
            historical_dates=historical_dates,
            projections_1m=max(0, projection_1m),
            projections_3m=max(0, projection_3m),
            projections_6m=max(0, projection_6m),
            projections_12m=max(0, projection_12m),
            confidence_lower_12m=max(0, confidence_lower),
            confidence_upper_12m=confidence_upper,
            monthly_growth_rate=monthly_growth,
            annual_growth_rate=annual_growth,
            model=model,
            model_accuracy=accuracy
        )
        
        self.projection_history.append(projection)
        return projection
    
    def _fit_model(self, data: List[float], model: GrowthModel) -> Tuple[Dict, float]:
        """Fit growth model to data"""
        
        if model == GrowthModel.LINEAR:
            x = np.arange(len(data))
            slope, intercept = np.polyfit(x, data, 1)
            params = {'slope': slope, 'intercept': intercept}
            
        elif model == GrowthModel.EXPONENTIAL:
            log_data = np.log(np.array(data) + 1)
            x = np.arange(len(data))
            b, log_a = np.polyfit(x, log_data, 1)
            params = {'a': np.exp(log_a), 'b': b}
            
        elif model == GrowthModel.LOGISTIC:
            params = {'K': max(data) * 2, 'r': 0.1, 't0': len(data) / 2}
        else:
            params = {}
        
        # Calculate accuracy (R²)
        accuracy = self._calculate_r_squared(data, model, params)
        
        return params, accuracy
    
    def _linear_growth(self, last_value: float, params: Dict, months: int) -> float:
        """Linear growth projection"""
        return last_value + params['slope'] * months
    
    def _exponential_growth(self, last_value: float, params: Dict, months: int) -> float:
        """Exponential growth projection"""
        return params['a'] * np.exp(params['b'] * months)
    
    def _logistic_growth(self, last_value: float, params: Dict, months: int) -> float:
        """Logistic growth projection"""
        K = params['K']
        r = params['r']
        t0 = params['t0']
        t = months
        return K / (1 + np.exp(-r * (t - t0)))
    
    def _calculate_r_squared(self, data: List[float], model: GrowthModel, params: Dict) -> float:
        """Calculate R² for model fit"""
        y_mean = np.mean(data)
        ss_tot = sum((y - y_mean) ** 2 for y in data)
        
        if model == GrowthModel.LINEAR:
            predictions = [params['slope'] * x + params['intercept'] for x in range(len(data))]
        elif model == GrowthModel.EXPONENTIAL:
            predictions = [params['a'] * np.exp(params['b'] * x) for x in range(len(data))]
        else:
            predictions = data
        
        ss_res = sum((y - p) ** 2 for y, p in zip(data, predictions))
        
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    def _calculate_monthly_growth_rate(self, data: List[float]) -> float:
        """Calculate average monthly growth rate"""
        if len(data) < 2:
            return 0
        
        growth_rates = []
        for i in range(1, len(data)):
            if data[i-1] > 0:
                growth = (data[i] - data[i-1]) / data[i-1]
                growth_rates.append(growth)
        
        return np.mean(growth_rates) if growth_rates else 0
    
    def generate_capacity_plan_from_growth(
        self,
        service_name: str,
        projection: GrowthProjection,
        capacity_per_unit: float,
        headroom_percent: float = 30
    ) -> Dict:
        """Generate capacity plan based on growth projection"""
        
        headroom_factor = 1 + (headroom_percent / 100)
        current_capacity = projection.historical_values[-1] / capacity_per_unit
        
        plan = {
            'service_name': service_name,
            'current_capacity_units': current_capacity,
            'projections': {
                '1_month': {
                    'projected_load': projection.projections_1m,
                    'required_capacity': projection.projections_1m * headroom_factor / capacity_per_unit,
                    'additional_units_needed': max(0, projection.projections_1m * headroom_factor / capacity_per_unit - current_capacity)
                },
                '3_months': {
                    'projected_load': projection.projections_3m,
                    'required_capacity': projection.projections_3m * headroom_factor / capacity_per_unit,
                    'additional_units_needed': max(0, projection.projections_3m * headroom_factor / capacity_per_unit - current_capacity)
                },
                '6_months': {
                    'projected_load': projection.projections_6m,
                    'required_capacity': projection.projections_6m * headroom_factor / capacity_per_unit,
                    'additional_units_needed': max(0, projection.projections_6m * headroom_factor / capacity_per_unit - current_capacity)
                },
                '12_months': {
                    'projected_load': projection.projections_12m,
                    'required_capacity': projection.projections_12m * headroom_factor / capacity_per_unit,
                    'additional_units_needed': max(0, projection.projections_12m * headroom_factor / capacity_per_unit - current_capacity),
                    'confidence_range': {
                        'lower': projection.confidence_lower_12m * headroom_factor / capacity_per_unit,
                        'upper': projection.confidence_upper_12m * headroom_factor / capacity_per_unit
                    }
                }
            },
            'growth_rates': {
                'monthly': projection.monthly_growth_rate * 100,
                'annual': projection.annual_growth_rate * 100
            }
        }
        
        return plan
