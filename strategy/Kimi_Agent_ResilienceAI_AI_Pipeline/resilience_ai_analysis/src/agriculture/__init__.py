"""
ResilienceAI Agricultural Intelligence Platform

This module provides comprehensive agricultural analysis capabilities including:
- USDA NASS data integration
- Soil quality assessment
- Drought impact analysis
- Crop yield prediction
- Agricultural vulnerability assessment
- Seasonal planting recommendations
- Commodity price analysis
"""

from src.agriculture.clients.nass_client import EnhancedUSDANASSClient
from src.agriculture.clients.soil_client import NRCSSoilClient
from src.agriculture.clients.drought_client import EnhancedDroughtMonitorClient
from src.agriculture.clients.commodity_client import CommodityPriceClient
from src.agriculture.models.yield_predictor import CropYieldPredictor
from src.agriculture.models.vulnerability_model import AgriculturalVulnerabilityModel
from src.agriculture.indices.vulnerability_index import AgriculturalVulnerabilityIndex
from src.agriculture.analysis.planting_optimizer import PlantingOptimizer
from src.agriculture.integration import AgriculturalIntelligenceIntegration

__version__ = "1.0.0"

__all__ = [
    'EnhancedUSDANASSClient',
    'NRCSSoilClient',
    'EnhancedDroughtMonitorClient',
    'CommodityPriceClient',
    'CropYieldPredictor',
    'AgriculturalVulnerabilityModel',
    'AgriculturalVulnerabilityIndex',
    'PlantingOptimizer',
    'AgriculturalIntelligenceIntegration'
]
