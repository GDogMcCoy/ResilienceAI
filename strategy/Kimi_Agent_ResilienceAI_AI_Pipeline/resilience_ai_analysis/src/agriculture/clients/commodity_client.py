"""
Commodity Price Client for ResilienceAI
Provides commodity price data and correlation analysis
"""
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Commodity price data point"""
    commodity: str
    date: datetime
    price: float
    unit: str
    market: str


@dataclass
class PriceCorrelation:
    """Price correlation analysis result"""
    commodity1: str
    commodity2: str
    correlation: float
    p_value: float
    time_period: str
    significance: str


class CommodityPriceClient:
    """Client for commodity price data"""
    
    NASS_PRICES = {
        'CORN': {'statisticcat_desc': 'PRICE RECEIVED', 'unit_desc': '$ / BU'},
        'SOYBEANS': {'statisticcat_desc': 'PRICE RECEIVED', 'unit_desc': '$ / BU'},
        'WHEAT': {'statisticcat_desc': 'PRICE RECEIVED', 'unit_desc': '$ / BU'},
        'COTTON': {'statisticcat_desc': 'PRICE RECEIVED', 'unit_desc': '$ / LB'},
        'RICE': {'statisticcat_desc': 'PRICE RECEIVED', 'unit_desc': '$ / CWT'}
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.usda_base_url = "https://quickstats.nass.usda.gov/api"
        self.session = requests.Session()
    
    def get_historical_prices(self, commodity: str, start_date: datetime,
                              end_date: datetime, state: Optional[str] = None) -> List[PriceData]:
        """Get historical commodity prices from USDA NASS"""
        params = {
            'source_desc': 'SURVEY', 'sector_desc': 'CROPS',
            'group_desc': 'FIELD CROPS', 'commodity_desc': commodity,
            'statisticcat_desc': 'PRICE RECEIVED',
            'unit_desc': self.NASS_PRICES.get(commodity, {}).get('unit_desc', '$ / BU'),
            'format': 'JSON'
        }
        if state:
            params['state_alpha'] = state
        
        try:
            response = self.session.get(f"{self.usda_base_url}/api_GET/", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('data', []):
                try:
                    year = int(item.get('year', 0))
                    if start_date.year <= year <= end_date.year:
                        results.append(PriceData(
                            commodity=item.get('commodity_desc', ''),
                            date=datetime(year, 1, 1),
                            price=float(item.get('Value', 0)),
                            unit=item.get('unit_desc', ''),
                            market=item.get('reference_period_desc', 'ANNUAL')
                        ))
                except (ValueError, TypeError):
                    continue
            return results
        except Exception as e:
            logger.error(f"Error fetching price data: {e}")
            return []
    
    def calculate_price_correlation(self, commodity1: str, commodity2: str,
                                    years: int = 10) -> PriceCorrelation:
        """Calculate price correlation between two commodities"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        prices1 = self.get_historical_prices(commodity1, start_date, end_date)
        prices2 = self.get_historical_prices(commodity2, start_date, end_date)
        
        if not prices1 or not prices2:
            return PriceCorrelation(commodity1, commodity2, 0, 1, f"{years} years", 'No Data')
        
        df1 = pd.DataFrame([(p.date.year, p.price) for p in prices1], columns=['year', 'price1'])
        df2 = pd.DataFrame([(p.date.year, p.price) for p in prices2], columns=['year', 'price2'])
        df = df1.merge(df2, on='year', how='inner')
        
        if len(df) < 3:
            return PriceCorrelation(commodity1, commodity2, 0, 1, f"{years} years", 'Insufficient Data')
        
        from scipy.stats import pearsonr
        corr, p_value = pearsonr(df['price1'], df['price2'])
        
        if p_value < 0.01: significance = 'Highly Significant'
        elif p_value < 0.05: significance = 'Significant'
        elif p_value < 0.1: significance = 'Marginally Significant'
        else: significance = 'Not Significant'
        
        return PriceCorrelation(
            commodity1, commodity2, round(corr, 4), round(p_value, 4),
            f"{years} years", significance
        )
    
    def analyze_price_volatility(self, commodity: str, years: int = 10) -> Dict[str, Any]:
        """Analyze price volatility for a commodity"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        prices = self.get_historical_prices(commodity, start_date, end_date)
        if not prices:
            return {'error': 'No price data available'}
        
        price_values = [p.price for p in prices]
        mean_price = np.mean(price_values)
        std_price = np.std(price_values)
        cv = std_price / mean_price if mean_price > 0 else 0
        
        returns = [(price_values[i] - price_values[i-1]) / price_values[i-1]
                   for i in range(1, len(price_values))]
        
        return {
            'commodity': commodity,
            'years_analyzed': len(price_values),
            'mean_price': round(mean_price, 2),
            'std_price': round(std_price, 2),
            'coefficient_variation': round(cv, 4),
            'min_price': round(min(price_values), 2),
            'max_price': round(max(price_values), 2),
            'price_range_pct': round((max(price_values) - min(price_values)) / mean_price * 100, 2),
            'avg_annual_return': round(np.mean(returns) * 100, 2) if returns else 0,
            'return_volatility': round(np.std(returns) * 100, 2) if returns else 0,
            'volatility_category': 'High' if cv > 0.3 else 'Moderate' if cv > 0.15 else 'Low'
        }
