"""
Seasonal Planting Recommendation Engine
Provides optimized planting recommendations based on climate, soil, and market conditions
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PlantingRecommendation:
    """Planting recommendation for a specific crop and location"""
    county_fips: str
    commodity: str
    recommended_planting_date: str
    planting_window: Tuple[str, str]
    confidence: float
    factors: Dict[str, Any]
    risk_assessment: Dict[str, str]
    expected_yield_range: Tuple[float, float]


class PlantingOptimizer:
    """Optimizes planting decisions based on multiple factors"""
    
    PLANTING_WINDOWS = {
        'CORN': {
            'Corn Belt': {'early': '04-20', 'optimal': '05-05', 'late': '05-20'},
            'Southern': {'early': '03-15', 'optimal': '03-25', 'late': '04-15'},
            'Northern': {'early': '05-01', 'optimal': '05-15', 'late': '05-25'}
        },
        'SOYBEANS': {
            'Corn Belt': {'early': '04-25', 'optimal': '05-10', 'late': '06-10'},
            'Southern': {'early': '04-01', 'optimal': '04-15', 'late': '05-15'},
            'Northern': {'early': '05-05', 'optimal': '05-20', 'late': '06-05'}
        },
        'WHEAT': {
            'Winter': {'early': '09-15', 'optimal': '10-01', 'late': '10-20'},
            'Spring': {'early': '03-20', 'optimal': '04-01', 'late': '04-20'}
        }
    }
    
    GDD_REQUIREMENTS = {'CORN': 100, 'SOYBEANS': 90, 'WHEAT': 80}
    
    def __init__(self):
        self.recommendation_cache = {}
    
    def get_planting_recommendation(self, county_fips: str, commodity: str,
                                    weather_forecast: pd.DataFrame,
                                    soil_data: Dict[str, Any],
                                    current_date: datetime = None) -> PlantingRecommendation:
        """Generate planting recommendation for a county and crop"""
        current_date = current_date or datetime.now()
        
        region = self._determine_region(county_fips)
        base_window = self.PLANTING_WINDOWS.get(commodity, {}).get(region, {})
        
        if not base_window:
            return PlantingRecommendation(
                county_fips=county_fips, commodity=commodity,
                recommended_planting_date='Unknown',
                planting_window=('Unknown', 'Unknown'),
                confidence=0, factors={}, risk_assessment={'overall': 'Unknown'},
                expected_yield_range=(0, 0)
            )
        
        weather_factors = self._analyze_weather(weather_forecast, commodity)
        soil_factors = self._analyze_soil(soil_data)
        
        adjusted_date = self._adjust_planting_date(base_window['optimal'], weather_factors, soil_factors)
        confidence = self._calculate_confidence(weather_factors, soil_factors)
        risk_assessment = self._assess_risks(weather_factors, soil_factors, commodity)
        yield_range = self._estimate_yield_range(commodity, weather_factors, soil_factors)
        
        return PlantingRecommendation(
            county_fips=county_fips, commodity=commodity,
            recommended_planting_date=adjusted_date,
            planting_window=(base_window['early'], base_window['late']),
            confidence=round(confidence, 3),
            factors={'weather': weather_factors, 'soil': soil_factors},
            risk_assessment=risk_assessment,
            expected_yield_range=yield_range
        )
    
    def _determine_region(self, county_fips: str) -> str:
        """Determine agricultural region from county FIPS"""
        state_fips = county_fips[:2]
        if state_fips in ['17', '18', '19', '26', '27', '29', '31', '39', '55']:
            return 'Corn Belt'
        elif state_fips in ['01', '05', '12', '13', '22', '28', '45', '47', '48']:
            return 'Southern'
        elif state_fips in ['27', '38', '46']:
            return 'Northern'
        return 'Corn Belt'
    
    def _analyze_weather(self, weather_forecast: pd.DataFrame, commodity: str) -> Dict[str, Any]:
        """Analyze weather conditions for planting"""
        factors = {}
        factors['soil_temp_4in'] = weather_forecast.get('soil_temp_4in', [50])[0]
        factors['soil_temp_suitable'] = factors['soil_temp_4in'] >= 50
        
        precip_forecast = weather_forecast.get('precipitation', [0])
        factors['precip_7day'] = sum(precip_forecast[:7])
        factors['dry_period_expected'] = factors['precip_7day'] < 1.0
        
        gdd_forecast = weather_forecast.get('gdd', [0])
        factors['gdd_7day'] = sum(gdd_forecast[:7])
        factors['gdd_sufficient'] = factors['gdd_7day'] >= self.GDD_REQUIREMENTS.get(commodity, 100)
        
        min_temps = weather_forecast.get('min_temp', [50])
        factors['frost_risk'] = any(t < 32 for t in min_temps[:14])
        
        return factors
    
    def _analyze_soil(self, soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze soil conditions for planting"""
        factors = {}
        factors['water_storage'] = soil_data.get('aws100', 0)
        factors['adequate_moisture'] = factors['water_storage'] >= 15
        factors['drainage_class'] = soil_data.get('drainage_class', 'Moderate')
        factors['well_drained'] = factors['drainage_class'] in ['Well', 'Moderately Well']
        factors['soil_temp'] = soil_data.get('soil_temp', 50)
        return factors
    
    def _adjust_planting_date(self, base_date: str, weather_factors: Dict[str, Any],
                              soil_factors: Dict[str, Any]) -> str:
        """Adjust planting date based on conditions"""
        base = datetime.strptime(base_date, '%m-%d')
        
        if not weather_factors['soil_temp_suitable']:
            base += timedelta(days=7)
        if not weather_factors['dry_period_expected']:
            base += timedelta(days=3)
        if weather_factors['frost_risk']:
            base += timedelta(days=7)
        
        return base.strftime('%m-%d')
    
    def _calculate_confidence(self, weather_factors: Dict[str, Any],
                              soil_factors: Dict[str, Any]) -> float:
        """Calculate confidence in recommendation"""
        score = 0
        if weather_factors['soil_temp_suitable']: score += 0.3
        if weather_factors['dry_period_expected']: score += 0.2
        if not weather_factors['frost_risk']: score += 0.2
        if soil_factors['adequate_moisture']: score += 0.2
        if soil_factors['well_drained']: score += 0.1
        return score
    
    def _assess_risks(self, weather_factors: Dict[str, Any], soil_factors: Dict[str, Any],
                      commodity: str) -> Dict[str, str]:
        """Assess planting risks"""
        risks = {}
        risks['frost'] = 'High' if weather_factors['frost_risk'] else 'Low'
        risks['wet_conditions'] = 'Moderate' if not weather_factors['dry_period_expected'] else 'Low'
        risks['poor_drainage'] = 'Moderate' if not soil_factors['well_drained'] else 'Low'
        
        high_risks = sum(1 for r in risks.values() if r == 'High')
        mod_risks = sum(1 for r in risks.values() if r == 'Moderate')
        
        if high_risks > 0: risks['overall'] = 'High'
        elif mod_risks > 1: risks['overall'] = 'Moderate'
        else: risks['overall'] = 'Low'
        
        return risks
    
    def _estimate_yield_range(self, commodity: str, weather_factors: Dict[str, Any],
                              soil_factors: Dict[str, Any]) -> Tuple[float, float]:
        """Estimate expected yield range"""
        base_yields = {'CORN': (150, 180), 'SOYBEANS': (45, 55), 'WHEAT': (60, 75)}
        low, high = base_yields.get(commodity, (0, 0))
        
        if not weather_factors['soil_temp_suitable']:
            low *= 0.9
            high *= 0.95
        if weather_factors['frost_risk']:
            low *= 0.85
            high *= 0.90
        if not soil_factors['adequate_moisture']:
            low *= 0.90
            high *= 0.95
        
        return (round(low, 1), round(high, 1))
