"""
USDA Agricultural Data Client for ResilienceAI
Provides crop yield, acreage, and agricultural vulnerability data
"""

import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class CropData:
    """Represents agricultural data for a county"""
    county_fips: str
    county_name: str
    state: str
    year: int
    commodity: str  # CORN, SOYBEANS, WHEAT, etc.
    acres_planted: Optional[int]
    acres_harvested: Optional[int]
    yield_per_acre: Optional[float]  # bushels per acre
    production: Optional[int]  # total bushels
    
    def to_dict(self) -> Dict:
        return {
            'county_fips': self.county_fips,
            'county_name': self.county_name,
            'state': self.state,
            'year': self.year,
            'commodity': self.commodity,
            'acres_planted': self.acres_planted,
            'acres_harvested': self.acres_harvested,
            'yield_per_acre': self.yield_per_acre,
            'production': self.production
        }


class USDANASSClient:
    """
    Client for USDA NASS Quick Stats API
    Free API for agricultural statistics
    """
    
    BASE_URL = "https://quickstats.nass.usda.gov/api"
    
    # Major crops to track
    MAJOR_CROPS = ['CORN', 'SOYBEANS', 'WHEAT', 'COTTON', 'RICE']
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self._last_request_time = 0
        self._rate_limit_delay = 1.0  # NASS recommends 1 second between requests
    
    def _rate_limit(self):
        """Simple rate limiting"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, params: Dict) -> Dict:
        """Make API request with error handling"""
        self._rate_limit()
        
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            response = self.session.get(f"{self.BASE_URL}/api_GET/", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'API request failed: {str(e)}'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}
    
    def get_crop_yield(self, state: str, county: str = None, 
                       commodity: str = 'CORN', year: int = None) -> List[CropData]:
        """
        Get crop yield data for a state or county
        
        Args:
            state: Two-letter state code
            county: County name (optional)
            commodity: Crop commodity code
            year: Specific year (default: most recent)
        """
        params = {
            'source_desc': 'SURVEY',
            'sector_desc': 'CROPS',
            'group_desc': 'FIELD CROPS',
            'commodity_desc': commodity,
            'statisticcat_desc': 'YIELD',
            'unit_desc': 'BU / ACRE',
            'state_alpha': state,
            'format': 'JSON'
        }
        
        if county:
            params['county_name'] = county.upper()
        
        if year:
            params['year'] = str(year)
        
        data = self._make_request(params)
        
        if 'error' in data:
            return []
        
        results = []
        for item in data.get('data', []):
            try:
                crop_data = CropData(
                    county_fips=item.get('county_code', ''),
                    county_name=item.get('county_name', ''),
                    state=item.get('state_alpha', ''),
                    year=int(item.get('year', 0)),
                    commodity=item.get('commodity_desc', ''),
                    acres_planted=None,
                    acres_harvested=None,
                    yield_per_acre=float(item.get('Value', 0)) if item.get('Value') else None,
                    production=None
                )
                results.append(crop_data)
            except (ValueError, TypeError):
                continue
        
        return results
    
    def get_acreage(self, state: str, county: str = None,
                    commodity: str = 'CORN', year: int = None) -> List[CropData]:
        """Get planted/harvested acreage data"""
        params = {
            'source_desc': 'SURVEY',
            'sector_desc': 'CROPS',
            'group_desc': 'FIELD CROPS',
            'commodity_desc': commodity,
            'statisticcat_desc': 'AREA HARVESTED',
            'unit_desc': 'ACRES',
            'state_alpha': state,
            'format': 'JSON'
        }
        
        if county:
            params['county_name'] = county.upper()
        if year:
            params['year'] = str(year)
        
        data = self._make_request(params)
        
        if 'error' in data:
            return []
        
        results = []
        for item in data.get('data', []):
            try:
                # Remove commas from acreage values
                value_str = item.get('Value', '0').replace(',', '')
                crop_data = CropData(
                    county_fips=item.get('county_code', ''),
                    county_name=item.get('county_name', ''),
                    state=item.get('state_alpha', ''),
                    year=int(item.get('year', 0)),
                    commodity=item.get('commodity_desc', ''),
                    acres_planted=None,
                    acres_harvested=int(float(value_str)) if value_str else None,
                    yield_per_acre=None,
                    production=None
                )
                results.append(crop_data)
            except (ValueError, TypeError):
                continue
        
        return results
    
    def get_state_crop_summary(self, state: str, year: int = None) -> Dict[str, Any]:
        """
        Get summary of all major crops for a state
        """
        summary = {
            'state': state,
            'year': year or 'latest',
            'crops': {}
        }
        
        for commodity in self.MAJOR_CROPS:
            # Get yield data
            yields = self.get_crop_yield(state, commodity=commodity, year=year)
            if yields:
                avg_yield = sum(y.yield_per_acre for y in yields if y.yield_per_acre) / len(yields)
                summary['crops'][commodity] = {
                    'counties_reporting': len(yields),
                    'average_yield_bu_per_acre': round(avg_yield, 2),
                    'top_county': max(yields, key=lambda x: x.yield_per_acre or 0).county_name if yields else None
                }
        
        return summary


class DroughtMonitorClient:
    """
    Client for US Drought Monitor data
    Weekly drought severity by county
    """
    
    DROUGHT_CATEGORIES = {
        'D0': 'Abnormally Dry',
        'D1': 'Moderate Drought',
        'D2': 'Severe Drought',
        'D3': 'Extreme Drought',
        'D4': 'Exceptional Drought'
    }
    
    def __init__(self):
        self.base_url = "https://usdmdataservices.unl.edu/api"
        self.session = requests.Session()
    
    def get_county_drought(self, county_fips: str, 
                          start_date: str = None,
                          end_date: str = None) -> List[Dict]:
        """
        Get drought data for a specific county
        
        Args:
            county_fips: 5-digit FIPS code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        params = {
            'CountyFIPS': county_fips,
            'Format': 'json'
        }
        
        if start_date:
            params['StartDate'] = start_date
        if end_date:
            params['EndDate'] = end_date
        
        try:
            response = self.session.get(
                f"{self.base_url}/CountyStatistics/GetCountyStatistics",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_current_drought(self, state: str = None) -> List[Dict]:
        """Get most recent drought data"""
        # This would need to be implemented based on actual USDM API
        # For now, return placeholder
        return []


class AgriculturalVulnerabilityScorer:
    """
    Calculate agricultural vulnerability scores
    Combines crop data, drought, and climate factors
    """
    
    def __init__(self, nass_client: USDANASSClient = None, 
                 drought_client: DroughtMonitorClient = None):
        self.nass = nass_client or USDANASSClient()
        self.drought = drought_client or DroughtMonitorClient()
    
    def calculate_crop_vulnerability(self, county_fips: str, 
                                     county_name: str,
                                     state: str) -> Dict[str, Any]:
        """
        Calculate agricultural vulnerability score for a county
        
        Returns vulnerability assessment combining:
        - Crop yield trends
        - Drought exposure
        - Crop diversity
        """
        # Get crop data
        corn_data = self.nass.get_crop_yield(state, county_name, 'CORN')
        soy_data = self.nass.get_crop_yield(state, county_name, 'SOYBEANS')
        wheat_data = self.nass.get_crop_yield(state, county_name, 'WHEAT')
        
        # Calculate yield stability (coefficient of variation)
        def calc_stability(data: List[CropData]) -> float:
            yields = [d.yield_per_acre for d in data if d.yield_per_acre]
            if len(yields) < 2:
                return 1.0  # High uncertainty
            mean_y = sum(yields) / len(yields)
            variance = sum((y - mean_y) ** 2 for y in yields) / len(yields)
            cv = (variance ** 0.5) / mean_y if mean_y > 0 else 1.0
            return min(cv, 1.0)  # Cap at 1.0
        
        corn_stability = calc_stability(corn_data)
        soy_stability = calc_stability(soy_data)
        wheat_stability = calc_stability(wheat_data)
        
        # Overall vulnerability (higher = more vulnerable)
        avg_stability = (corn_stability + soy_stability + wheat_stability) / 3
        vulnerability_score = avg_stability  # Higher CV = less stable = more vulnerable
        
        # Determine risk level
        if vulnerability_score >= 0.3:
            risk_level = 'High'
        elif vulnerability_score >= 0.2:
            risk_level = 'Moderate'
        else:
            risk_level = 'Low'
        
        return {
            'county_fips': county_fips,
            'county_name': county_name,
            'state': state,
            'vulnerability_score': round(vulnerability_score, 3),
            'risk_level': risk_level,
            'crop_stability': {
                'corn': round(corn_stability, 3),
                'soybeans': round(soy_stability, 3),
                'wheat': round(wheat_stability, 3)
            },
            'data_availability': {
                'corn_years': len(corn_data),
                'soy_years': len(soy_data),
                'wheat_years': len(wheat_data)
            }
        }
    
    def assess_food_security_risk(self, county_fips: str,
                                  county_name: str,
                                  state: str,
                                  population: int = None) -> Dict[str, Any]:
        """
        Assess food security risk based on agricultural capacity
        
        Combines:
        - Local crop production vs population
        - Import dependency risk
        - Drought vulnerability
        """
        # Get acreage data
        corn_acres = self.nass.get_acreage(state, county_name, 'CORN')
        soy_acres = self.nass.get_acreage(state, county_name, 'SOYBEANS')
        
        total_acres = sum(a.acres_harvested for a in corn_acres + soy_acres if a.acres_harvested)
        
        # Calculate food production capacity (simplified)
        # Assume 150 bushels/acre corn, 45 bushels/acre soybeans
        corn_production = sum(a.acres_harvested for a in corn_acres if a.acres_harvested) * 150
        soy_production = sum(a.acres_harvested for a in soy_acres if a.acres_harvested) * 45
        
        total_calories = corn_production * 30000 + soy_production * 50000  # rough calorie estimates
        
        # Food security score
        if population and population > 0:
            calories_per_capita = total_calories / population
            if calories_per_capita < 1000000:  # Less than 1M calories per person
                food_security_risk = 'High'
            elif calories_per_capita < 3000000:
                food_security_risk = 'Moderate'
            else:
                food_security_risk = 'Low'
        else:
            food_security_risk = 'Unknown'
            calories_per_capita = 0
        
        return {
            'county_fips': county_fips,
            'county_name': county_name,
            'state': state,
            'agricultural_acres': total_acres,
            'estimated_production': {
                'corn_bushels': corn_production,
                'soy_bushels': soy_production
            },
            'population': population,
            'calories_per_capita': int(calories_per_capita),
            'food_security_risk': food_security_risk,
            'import_dependency': 'High' if food_security_risk == 'High' else 'Moderate'
        }


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="USDA Agricultural Data CLI")
    parser.add_argument("--state", type=str, required=True, help="State code (e.g., MO)")
    parser.add_argument("--county", type=str, help="County name")
    parser.add_argument("--commodity", type=str, default="CORN", help="Crop commodity")
    parser.add_argument("--year", type=int, help="Year")
    parser.add_argument("--vulnerability", action="store_true", help="Calculate vulnerability")
    parser.add_argument("--food-security", action="store_true", help="Assess food security")
    parser.add_argument("--population", type=int, help="County population for food security")
    
    args = parser.parse_args()
    
    if args.vulnerability and args.county:
        scorer = AgriculturalVulnerabilityScorer()
        result = scorer.calculate_crop_vulnerability(
            county_fips="00000",  # Would need actual FIPS
            county_name=args.county,
            state=args.state
        )
        print(f"\n🌾 Agricultural Vulnerability for {args.county}, {args.state}")
        print(f"  Score: {result['vulnerability_score']}")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Crop Stability: {result['crop_stability']}")
    
    elif args.food_security and args.county:
        scorer = AgriculturalVulnerabilityScorer()
        result = scorer.assess_food_security_risk(
            county_fips="00000",
            county_name=args.county,
            state=args.state,
            population=args.population
        )
        print(f"\n🍞 Food Security Assessment for {args.county}, {args.state}")
        print(f"  Risk: {result['food_security_risk']}")
        print(f"  Agricultural Acres: {result['agricultural_acres']:,}")
        print(f"  Import Dependency: {result['import_dependency']}")
    
    else:
        # Default: show crop yields
        client = USDANASSClient()
        yields = client.get_crop_yield(args.state, args.county, args.commodity, args.year)
        print(f"\n🌽 {args.commodity} Yields for {args.county or args.state}")
        for y in yields[:10]:
            print(f"  {y.county_name} ({y.year}): {y.yield_per_acre} bu/acre")
