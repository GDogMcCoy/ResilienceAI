"""
ResilienceAI Weather Integration Module

This module provides comprehensive weather integration capabilities including:
- NOAA NWS API client with caching and rate limiting
- Severe weather alert processing pipeline
- Real-time weather feed management
- Weather impact modeling
- Weather visualization components
- Historical weather analysis
- Agent integration

Usage:
    from src.weather import EnhancedNOAAClient, AlertProcessor, WeatherAgent
    
    # Initialize client
    client = EnhancedNOAAClient(cache_dir='./cache', cache_ttl=300)
    
    # Get active alerts
    alerts = client.get_active_alerts(state='MO')
    
    # Correlate with vulnerability
    result = client.correlate_with_vulnerability(
        county_fips='29019',
        county_name='Boone',
        state='MO',
        vulnerability_score=0.7
    )
"""

from .enhanced_noaa_client import (
    EnhancedNOAAClient,
    WeatherAlert,
    WeatherForecast,
    WeatherStation,
    Observation,
    AlertSeverity,
    AlertUrgency,
    AlertCertainty,
    get_severity_color
)

from .alert_processor import (
    AlertProcessor,
    ProcessedAlert,
    AlertStatus,
    AlertCategory,
    CAPAlertParser,
    SeverityScorer
)

from .realtime_feed import (
    RealtimeFeedManager,
    WeatherFeed,
    NOAACAPFeed,
    USGSWaterServicesFeed,
    FeedStatus,
    FeedMetrics
)

from .impact_model import (
    WeatherImpactModel,
    PopulationImpactModel,
    InfrastructureImpactModel,
    EconomicImpactModel,
    ImpactEstimate
)

from .weather_viz import (
    WeatherAlertMap,
    WeatherAlertTimeline,
    WeatherDashboard,
    WeatherChartGenerator
)

from .weather_agent import (
    WeatherAgent,
    WeatherAgentIntegration
)

from .historical_weather import (
    NCEIClient,
    HistoricalAlertAnalyzer,
    WeatherPatternDetector,
    HistoricalWeatherReport
)

__version__ = "2.0.0"
__all__ = [
    # Core client
    'EnhancedNOAAClient',
    'WeatherAlert',
    'WeatherForecast',
    'WeatherStation',
    'Observation',
    'AlertSeverity',
    'AlertUrgency',
    'AlertCertainty',
    'get_severity_color',
    
    # Alert processing
    'AlertProcessor',
    'ProcessedAlert',
    'AlertStatus',
    'AlertCategory',
    'CAPAlertParser',
    'SeverityScorer',
    
    # Real-time feeds
    'RealtimeFeedManager',
    'WeatherFeed',
    'NOAACAPFeed',
    'USGSWaterServicesFeed',
    'FeedStatus',
    'FeedMetrics',
    
    # Impact modeling
    'WeatherImpactModel',
    'PopulationImpactModel',
    'InfrastructureImpactModel',
    'EconomicImpactModel',
    'ImpactEstimate',
    
    # Visualization
    'WeatherAlertMap',
    'WeatherAlertTimeline',
    'WeatherDashboard',
    'WeatherChartGenerator',
    
    # Agent integration
    'WeatherAgent',
    'WeatherAgentIntegration',
    
    # Historical analysis
    'NCEIClient',
    'HistoricalAlertAnalyzer',
    'WeatherPatternDetector',
    'HistoricalWeatherReport'
]
