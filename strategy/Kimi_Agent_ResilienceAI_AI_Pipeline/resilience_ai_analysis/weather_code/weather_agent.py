"""
Weather Agent Integration
Integrates weather data with ResilienceAI agent orchestrator
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from enhanced_noaa_client import EnhancedNOAAClient, WeatherAlert, AlertSeverity
from alert_processor import AlertProcessor, ProcessedAlert
from impact_model import WeatherImpactModel

logger = logging.getLogger(__name__)


class WeatherAgent:
    """Weather agent for ResilienceAI agent orchestrator"""
    
    def __init__(
        self,
        noaa_client: Optional[EnhancedNOAAClient] = None,
        alert_processor: Optional[AlertProcessor] = None,
        impact_model: Optional[WeatherImpactModel] = None
    ):
        self.noaa_client = noaa_client or EnhancedNOAAClient()
        self.alert_processor = alert_processor or AlertProcessor()
        self.impact_model = impact_model or WeatherImpactModel()
        self.name = "WeatherAgent"
        self.description = "Monitors weather conditions and provides alerts and impact assessments"
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "monitor_weather_alerts",
            "assess_weather_impact",
            "provide_forecast_data",
            "correlate_weather_vulnerability",
            "generate_weather_recommendations"
        ]
    
    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weather agent action"""
        actions = {
            'get_active_alerts': self._get_active_alerts,
            'get_county_alerts': self._get_county_alerts,
            'assess_impact': self._assess_impact,
            'get_forecast': self._get_forecast,
            'correlate_vulnerability': self._correlate_vulnerability,
            'should_trigger_alert': self._should_trigger_alert
        }
        
        if action in actions:
            return actions[action](params)
        else:
            return {'error': f'Unknown action: {action}'}
    
    def _get_active_alerts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get active weather alerts"""
        state = params.get('state')
        severity = params.get('severity')
        
        if severity:
            severity = AlertSeverity(severity)
        
        alerts = self.noaa_client.get_active_alerts(
            state=state,
            severity=severity,
            limit=params.get('limit', 100)
        )
        
        return {
            'action': 'get_active_alerts',
            'count': len(alerts),
            'alerts': [a.to_dict() for a in alerts],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_county_alerts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get alerts for specific county"""
        county_name = params.get('county_name')
        state = params.get('state')
        
        if not county_name or not state:
            return {'error': 'county_name and state are required'}
        
        alerts = self.noaa_client.get_alerts_for_county(county_name, state)
        
        return {
            'action': 'get_county_alerts',
            'county': county_name,
            'state': state,
            'count': len(alerts),
            'alerts': [a.to_dict() for a in alerts],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _assess_impact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assess weather impact for county"""
        county_data = params.get('county_data', {})
        alert_data = params.get('alert')
        
        if not alert_data:
            return {'error': 'alert data is required'}
        
        alert = WeatherAlert(**alert_data)
        impact = self.impact_model.calculate_impact(alert, county_data)
        
        return {
            'action': 'assess_impact',
            'impact': impact.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather forecast for location"""
        lat = params.get('latitude')
        lon = params.get('longitude')
        
        if lat is None or lon is None:
            return {'error': 'latitude and longitude are required'}
        
        forecast = self.noaa_client.get_point_forecast(lat, lon)
        
        if forecast:
            return {
                'action': 'get_forecast',
                'forecast': {
                    'grid_id': forecast.grid_id,
                    'grid_x': forecast.grid_x,
                    'grid_y': forecast.grid_y,
                    'office': forecast.forecast_office,
                    'periods': forecast.periods[:5]
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {'error': 'Failed to get forecast'}
    
    def _correlate_vulnerability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate weather with vulnerability"""
        county_fips = params.get('county_fips')
        county_name = params.get('county_name')
        state = params.get('state')
        vulnerability_score = params.get('vulnerability_score', 0.5)
        population = params.get('population')
        
        if not county_name or not state:
            return {'error': 'county_name and state are required'}
        
        result = self.noaa_client.correlate_with_vulnerability(
            county_fips=county_fips or '',
            county_name=county_name,
            state=state,
            vulnerability_score=vulnerability_score,
            population=population
        )
        
        return {
            'action': 'correlate_vulnerability',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _should_trigger_alert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if weather should trigger alert"""
        county_fips = params.get('county_fips')
        county_name = params.get('county_name')
        state = params.get('state')
        vulnerability_threshold = params.get('vulnerability_threshold', 0.6)
        
        if not county_name or not state:
            return {'error': 'county_name and state are required'}
        
        result = self.noaa_client.should_trigger_alert(
            county_fips=county_fips or '',
            county_name=county_name,
            state=state,
            vulnerability_threshold=vulnerability_threshold
        )
        
        return {
            'action': 'should_trigger_alert',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def generate_weather_summary(self, county_name: str, state: str) -> str:
        """Generate natural language weather summary"""
        alerts = self.noaa_client.get_alerts_for_county(county_name, state)
        
        if not alerts:
            return f"No active weather alerts for {county_name}, {state}."
        
        lines = [f"🌦️ Weather Summary for {county_name}, {state}", ""]
        
        for alert in alerts[:5]:
            lines.extend([
                f"⚠️  {alert.severity.value}: {alert.event}",
                f"   {alert.headline}",
                f"   Effective: {alert.effective.strftime('%Y-%m-%d %H:%M UTC')}",
                f"   Expires: {alert.expires.strftime('%Y-%m-%d %H:%M UTC')}",
                ""
            ])
        
        return '\n'.join(lines)
    
    def to_agent_config(self) -> Dict[str, Any]:
        """Convert to agent orchestrator configuration"""
        return {
            'name': self.name,
            'description': self.description,
            'capabilities': self.get_capabilities(),
            'config': {
                'cache_ttl': 300,
                'rate_limit_delay': 0.5,
                'max_retries': 3
            }
        }


class WeatherAgentIntegration:
    """Integration layer for WeatherAgent with ResilienceAI"""
    
    def __init__(self, weather_agent: Optional[WeatherAgent] = None):
        self.weather_agent = weather_agent or WeatherAgent()
    
    def register_with_orchestrator(self, orchestrator) -> bool:
        """Register weather agent with agent orchestrator"""
        try:
            agent_config = self.weather_agent.to_agent_config()
            orchestrator.register_agent(self.weather_agent.name, agent_config)
            logger.info(f"WeatherAgent registered with orchestrator")
            return True
        except Exception as e:
            logger.error(f"Failed to register WeatherAgent: {e}")
            return False
    
    def get_weather_context(self, county_fips: str, county_name: str, state: str) -> Dict[str, Any]:
        """Get weather context for agent context building"""
        alerts = self.weather_agent.noaa_client.get_alerts_for_county(county_name, state)
        
        return {
            'weather': {
                'active_alerts': len(alerts),
                'max_severity': max([a.severity.value for a in alerts], default='None'),
                'alert_types': list(set([a.event for a in alerts])),
                'has_severe_weather': any(a.severity in [AlertSeverity.SEVERE, AlertSeverity.EXTREME] for a in alerts)
            }
        }
