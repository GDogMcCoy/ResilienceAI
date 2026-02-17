"""
Integration module for Agricultural Intelligence Platform with ResilienceAI
"""
from typing import Dict, List, Optional, Any
import pandas as pd
import logging

from src.agriculture.clients.nass_client import EnhancedUSDANASSClient
from src.agriculture.clients.soil_client import NRCSSoilClient
from src.agriculture.clients.drought_client import EnhancedDroughtMonitorClient
from src.agriculture.models.yield_predictor import CropYieldPredictor
from src.agriculture.models.vulnerability_model import AgriculturalVulnerabilityModel
from src.agriculture.indices.vulnerability_index import AgriculturalVulnerabilityIndex
from src.agriculture.analysis.planting_optimizer import PlantingOptimizer

logger = logging.getLogger(__name__)


class AgriculturalIntelligenceIntegration:
    """Integrates agricultural intelligence with ResilienceAI core systems"""
    
    def __init__(self):
        self.nass_client = EnhancedUSDANASSClient()
        self.soil_client = NRCSSoilClient()
        self.drought_client = EnhancedDroughtMonitorClient()
        self.yield_predictor = CropYieldPredictor()
        self.vulnerability_model = AgriculturalVulnerabilityModel()
        self.vulnerability_index = AgriculturalVulnerabilityIndex()
        self.planting_optimizer = PlantingOptimizer()
    
    def enrich_county_data(self, county_fips: str, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich county data with agricultural intelligence"""
        state = county_fips[:2]
        
        # Get agricultural vulnerability
        vulnerability = self.vulnerability_index.calculate_index(
            yield_data=base_data.get('yield_data', pd.DataFrame()),
            drought_data=base_data.get('drought_data', pd.DataFrame()),
            soil_data=base_data.get('soil_data', pd.DataFrame()),
            climate_data=base_data.get('climate_data', pd.DataFrame()),
            economic_data=base_data.get('economic_data', pd.DataFrame()),
            county_fips=county_fips
        )
        
        # Get yield predictions
        yield_predictions = []
        for commodity in ['CORN', 'SOYBEANS', 'WHEAT']:
            try:
                pred = self.yield_predictor.predict(base_data.get('yield_features', pd.DataFrame()))
                yield_predictions.extend(pred)
            except Exception as e:
                logger.warning(f"Could not predict {commodity} yield: {e}")
        
        # Get drought impact
        drought_impact = self.drought_client.assess_drought_impact(
            county_fips=county_fips, commodity='CORN'
        )
        
        # Enrich base data
        enriched = base_data.copy()
        enriched['agricultural_vulnerability'] = {
            'score': vulnerability.overall_score,
            'category': vulnerability.risk_category,
            'components': vulnerability.component_scores
        }
        enriched['yield_predictions'] = [
            {'commodity': p.commodity, 'predicted_yield': p.predicted_yield, 'confidence': p.confidence}
            for p in yield_predictions
        ]
        enriched['drought_impact'] = {
            'severity': drought_impact.drought_severity,
            'crop_risk': drought_impact.crop_impact_risk,
            'yield_reduction': drought_impact.yield_reduction_estimate
        }
        
        return enriched
    
    def generate_agricultural_dashboard_data(self, state: str, counties: List[str]) -> Dict[str, Any]:
        """Generate data for agricultural dashboard"""
        dashboard_data = {'state': state, 'counties': [], 'state_summary': {}}
        vulnerability_scores = []
        
        for county in counties:
            try:
                yield_trends = self.nass_client.get_yield_trends(
                    state=state, county=county, commodity='CORN', years=10
                )
                drought_freq = self.drought_client.calculate_drought_frequency(
                    county_fips=county, years=10
                )
                
                county_data = {
                    'county_fips': county,
                    'yield_trend': yield_trends.get('trend_direction', 'Unknown'),
                    'yield_volatility': yield_trends.get('coefficient_variation', 0),
                    'drought_frequency': drought_freq.get('drought_frequency_pct', 0),
                    'vulnerability_score': 0
                }
                
                dashboard_data['counties'].append(county_data)
                vulnerability_scores.append(county_data['vulnerability_score'])
                
            except Exception as e:
                logger.error(f"Error processing county {county}: {e}")
        
        if vulnerability_scores:
            dashboard_data['state_summary'] = {
                'avg_vulnerability': sum(vulnerability_scores) / len(vulnerability_scores),
                'counties_high_risk': sum(1 for v in vulnerability_scores if v > 70),
                'counties_moderate_risk': sum(1 for v in vulnerability_scores if 50 <= v < 70),
                'counties_low_risk': sum(1 for v in vulnerability_scores if v < 50)
            }
        
        return dashboard_data
    
    def get_agricultural_alerts(self, state: str, alert_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate agricultural alerts"""
        alert_types = alert_types or ['drought', 'yield', 'planting']
        alerts = []
        
        if 'drought' in alert_types:
            pass  # Implementation would query drought monitor
        
        if 'yield' in alert_types:
            pass  # Implementation would compare predictions to historical
        
        if 'planting' in alert_types:
            pass  # Implementation would check current date vs optimal planting
        
        return alerts
