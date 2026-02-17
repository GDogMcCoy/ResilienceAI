"""
Enhanced USDA NASS Client for ResilienceAI Agricultural Intelligence Platform
"""
import requests
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class EnhancedCropData:
    """Enhanced agricultural data for a county with additional metrics"""
    county_fips: str
    county_name: str
    state: str
    year: int
    commodity: str
    acres_planted: Optional[int] = None
    acres_harvested: Optional[int] = None
    yield_per_acre: Optional[float] = None
    production: Optional[int] = None
    price_per_bushel: Optional[float] = None
    value_of_production: Optional[float] = None
    irrigation_acres: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'county_fips': self.county_fips,
            'county_name': self.county_name,
            'state': self.state,
            'year': self.year,
            'commodity': self.commodity,
            'acres_planted': self.acres_planted,
            'acres_harvested': self.acres_harvested,
            'yield_per_acre': self.yield_per_acre,
            'production': self.production,
            'price_per_bushel': self.price_per_bushel,
            'value_of_production': self.value_of_production,
            'irrigation_acres': self.irrigation_acres
        }


class EnhancedUSDANASSClient:
    """Enhanced client for USDA NASS Quick Stats API with caching"""
    
    BASE_URL = "https://quickstats.nass.usda.gov/api"
    
    MAJOR_CROPS = [
        'CORN', 'SOYBEANS', 'WHEAT', 'COTTON', 'RICE',
        'SORGHUM', 'BARLEY', 'OATS', 'PEANUTS', 'SUGARBEETS',
        'CANOLA', 'SUNFLOWER', 'FLAXSEED', 'SAFFLOWER'
    ]
    
    YIELD_UNITS = {
        'CORN': 'BU / ACRE', 'SOYBEANS': 'BU / ACRE',
        'WHEAT': 'BU / ACRE', 'COTTON': 'LB / ACRE',
        'RICE': 'LB / ACRE', 'SORGHUM': 'BU / ACRE',
        'BARLEY': 'BU / ACRE', 'OATS': 'BU / ACRE',
        'PEANUTS': 'LB / ACRE', 'SUGARBEETS': 'TONS / ACRE'
    }
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self._last_request_time = 0
        self._rate_limit_delay = 1.0
        self.cache_dir = cache_dir or Path("data/agriculture/raw/nass")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _rate_limit(self):
        """Implement rate limiting for NASS API"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, params: Dict) -> Dict:
        """Make API request with error handling and caching"""
        cache_key = json.dumps(params, sort_keys=True)
        cache_file = self.cache_dir / f"{hash(cache_key)}.json"
        
        if cache_file.exists():
            cache_age = time.time() - cache_file.stat().st_mtime
            if cache_age < 604800:  # 7 days
                return json.loads(cache_file.read_text())
        
        self._rate_limit()
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            response = self.session.get(f"{self.BASE_URL}/api_GET/", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            cache_file.write_text(json.dumps(data))
            return data
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {'error': str(e)}
    
    def get_crop_yield(self, state: str, county: Optional[str] = None,
                       commodity: str = 'CORN', year: Optional[int] = None,
                       start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[EnhancedCropData]:
        """Get crop yield data with time range support"""
        params = {
            'source_desc': 'SURVEY', 'sector_desc': 'CROPS',
            'group_desc': 'FIELD CROPS', 'commodity_desc': commodity,
            'statisticcat_desc': 'YIELD',
            'unit_desc': self.YIELD_UNITS.get(commodity, 'BU / ACRE'),
            'state_alpha': state, 'format': 'JSON'
        }
        if county:
            params['county_name'] = county.upper()
        if year:
            params['year'] = str(year)
        elif start_year and end_year:
            params['year__GE'] = str(start_year)
            params['year__LE'] = str(end_year)
        
        data = self._make_request(params)
        if 'error' in data:
            return []
        
        results = []
        for item in data.get('data', []):
            try:
                crop_data = EnhancedCropData(
                    county_fips=item.get('county_code', ''),
                    county_name=item.get('county_name', ''),
                    state=item.get('state_alpha', ''),
                    year=int(item.get('year', 0)),
                    commodity=item.get('commodity_desc', ''),
                    yield_per_acre=self._parse_value(item.get('Value'))
                )
                results.append(crop_data)
            except (ValueError, TypeError):
                continue
        return results
    
    def get_yield_trends(self, state: str, county: str, commodity: str = 'CORN', years: int = 10) -> Dict[str, Any]:
        """Analyze yield trends over time"""
        end_year = datetime.now().year
        start_year = end_year - years
        
        yields = self.get_crop_yield(state=state, county=county, commodity=commodity,
                                     start_year=start_year, end_year=end_year)
        
        if not yields:
            return {'error': 'No data available'}
        
        yield_values = [y.yield_per_acre for y in yields if y.yield_per_acre]
        years_data = [y.year for y in yields if y.yield_per_acre]
        
        if len(yield_values) < 2:
            return {'error': 'Insufficient data for trend analysis'}
        
        import numpy as np
        x, y = np.array(years_data), np.array(yield_values)
        slope, intercept = np.polyfit(x, y, 1)
        mean_yield, std_yield = np.mean(yield_values), np.std(yield_values)
        cv = std_yield / mean_yield if mean_yield > 0 else 0
        
        return {
            'commodity': commodity, 'county': county, 'state': state,
            'years_analyzed': len(yield_values),
            'trend_slope': round(slope, 4),
            'trend_direction': 'increasing' if slope > 0.5 else 'decreasing' if slope < -0.5 else 'stable',
            'mean_yield': round(mean_yield, 2), 'std_yield': round(std_yield, 2),
            'coefficient_variation': round(cv, 4),
            'min_yield': round(min(yield_values), 2),
            'max_yield': round(max(yield_values), 2)
        }
    
    def _parse_value(self, value: Any) -> Optional[float]:
        """Parse value string to float, handling special cases"""
        if value is None or value in ['(D)', '(Z)']:
            return None
        try:
            return float(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return None


USDANASSClient = EnhancedUSDANASSClient
