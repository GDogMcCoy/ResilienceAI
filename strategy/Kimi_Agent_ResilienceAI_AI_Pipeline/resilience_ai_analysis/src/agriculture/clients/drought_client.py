"""
Enhanced US Drought Monitor Client
Provides comprehensive drought impact assessment for agriculture
"""
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class DroughtImpact:
    """Agricultural drought impact assessment"""
    county_fips: str
    assessment_date: datetime
    drought_severity: str
    crop_impact_risk: str
    pasture_impact_risk: str
    livestock_impact_risk: str
    irrigation_demand_increase: Optional[float] = None
    yield_reduction_estimate: Optional[float] = None


class EnhancedDroughtMonitorClient:
    """Enhanced client for US Drought Monitor data"""
    
    BASE_URL = "https://usdmdataservices.unl.edu/api"
    
    DROUGHT_CATEGORIES = {
        'None': {'level': 0, 'description': 'No Drought'},
        'D0': {'level': 1, 'description': 'Abnormally Dry'},
        'D1': {'level': 2, 'description': 'Moderate Drought'},
        'D2': {'level': 3, 'description': 'Severe Drought'},
        'D3': {'level': 4, 'description': 'Extreme Drought'},
        'D4': {'level': 5, 'description': 'Exceptional Drought'}
    }
    
    CROP_IMPACT_THRESHOLDS = {
        'CORN': {
            'D0': {'yield_reduction': 0, 'irrigation_increase': 10},
            'D1': {'yield_reduction': 10, 'irrigation_increase': 25},
            'D2': {'yield_reduction': 25, 'irrigation_increase': 50},
            'D3': {'yield_reduction': 45, 'irrigation_increase': 75},
            'D4': {'yield_reduction': 70, 'irrigation_increase': 100}
        },
        'SOYBEANS': {
            'D0': {'yield_reduction': 0, 'irrigation_increase': 10},
            'D1': {'yield_reduction': 8, 'irrigation_increase': 20},
            'D2': {'yield_reduction': 20, 'irrigation_increase': 45},
            'D3': {'yield_reduction': 40, 'irrigation_increase': 70},
            'D4': {'yield_reduction': 65, 'irrigation_increase': 100}
        },
        'WHEAT': {
            'D0': {'yield_reduction': 0, 'irrigation_increase': 5},
            'D1': {'yield_reduction': 5, 'irrigation_increase': 15},
            'D2': {'yield_reduction': 15, 'irrigation_increase': 35},
            'D3': {'yield_reduction': 35, 'irrigation_increase': 60},
            'D4': {'yield_reduction': 60, 'irrigation_increase': 100}
        }
    }
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_county_drought_history(self, county_fips: str, 
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None) -> List[Dict]:
        """Get drought history for a county"""
        params = {'CountyFIPS': county_fips, 'Format': 'json'}
        if start_date:
            params['StartDate'] = start_date
        if end_date:
            params['EndDate'] = end_date
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/CountyStatistics/GetCountyStatistics",
                params=params, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching drought data: {e}")
            return []
    
    def assess_drought_impact(self, county_fips: str, commodity: str,
                              current_drought_level: Optional[str] = None) -> DroughtImpact:
        """Assess agricultural drought impact for a specific crop"""
        if not current_drought_level:
            recent_data = self.get_county_drought_history(
                county_fips,
                start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            )
            current_drought_level = recent_data[-1].get('DroughtLevel', 'None') if recent_data else 'None'
        
        thresholds = self.CROP_IMPACT_THRESHOLDS.get(commodity, self.CROP_IMPACT_THRESHOLDS['CORN'])
        impact = thresholds.get(current_drought_level, thresholds['D0'])
        
        yield_reduction = impact['yield_reduction']
        if yield_reduction >= 50: crop_risk = 'Severe'
        elif yield_reduction >= 25: crop_risk = 'High'
        elif yield_reduction >= 10: crop_risk = 'Moderate'
        else: crop_risk = 'Low'
        
        return DroughtImpact(
            county_fips=county_fips,
            assessment_date=datetime.now(),
            drought_severity=self.DROUGHT_CATEGORIES.get(current_drought_level, {}).get('description', 'No Drought'),
            crop_impact_risk=crop_risk,
            pasture_impact_risk=crop_risk,
            livestock_impact_risk='High' if crop_risk in ['High', 'Severe'] else crop_risk,
            irrigation_demand_increase=impact['irrigation_increase'],
            yield_reduction_estimate=yield_reduction
        )
    
    def calculate_drought_frequency(self, county_fips: str, years: int = 10, min_level: str = 'D1') -> Dict[str, Any]:
        """Calculate drought frequency for a county"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        drought_data = self.get_county_drought_history(
            county_fips,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if not drought_data:
            return {'error': 'No drought data available'}
        
        min_level_num = self.DROUGHT_CATEGORIES[min_level]['level']
        drought_weeks = sum(
            1 for d in drought_data
            if self.DROUGHT_CATEGORIES.get(d.get('DroughtLevel'), {}).get('level', 0) >= min_level_num
        )
        
        total_weeks = len(drought_data)
        drought_frequency = drought_weeks / total_weeks if total_weeks > 0 else 0
        
        return {
            'county_fips': county_fips,
            'years_analyzed': years,
            'drought_weeks': drought_weeks,
            'drought_frequency': round(drought_frequency, 4),
            'drought_frequency_pct': round(drought_frequency * 100, 2)
        }
