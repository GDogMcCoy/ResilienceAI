"""
NOAA National Weather Service API Client for ResilienceAI
Provides real-time weather alerts and forecasts
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class WeatherAlert:
    """Represents a NOAA weather alert"""
    id: str
    event: str
    severity: str
    certainty: str
    urgency: str
    headline: str
    description: str
    instruction: str
    area_desc: str
    affected_counties: List[str]
    effective: str
    expires: str
    sender: str
    
    @classmethod
    def from_noaa_feature(cls, feature: Dict) -> 'WeatherAlert':
        """Create WeatherAlert from NOAA API feature"""
        props = feature.get('properties', {})
        
        # Extract affected counties from area description
        area_desc = props.get('areaDesc', '')
        affected_counties = [c.strip() for c in area_desc.split(';') if c.strip()]
        
        return cls(
            id=feature.get('id', ''),
            event=props.get('event', 'Unknown'),
            severity=props.get('severity', 'Unknown'),
            certainty=props.get('certainty', 'Unknown'),
            urgency=props.get('urgency', 'Unknown'),
            headline=props.get('headline', ''),
            description=props.get('description', ''),
            instruction=props.get('instruction', ''),
            area_desc=area_desc,
            affected_counties=affected_counties,
            effective=props.get('effective', ''),
            expires=props.get('expires', ''),
            sender=props.get('senderName', '')
        )
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'event': self.event,
            'severity': self.severity,
            'certainty': self.certainty,
            'urgency': self.urgency,
            'headline': self.headline,
            'description': self.description,
            'instruction': self.instruction,
            'area_desc': self.area_desc,
            'affected_counties': self.affected_counties,
            'effective': self.effective,
            'expires': self.expires,
            'sender': self.sender
        }


class NOAAWeatherClient:
    """
    Client for NOAA National Weather Service API
    No API key required - free public access
    """
    
    BASE_URL = "https://api.weather.gov"
    
    # Severity mapping for risk correlation
    SEVERITY_WEIGHTS = {
        'Extreme': 1.0,
        'Severe': 0.8,
        'Moderate': 0.5,
        'Minor': 0.2,
        'Unknown': 0.0
    }
    
    # Event types we care about for vulnerability
    RELEVANT_EVENTS = [
        'Flood Warning', 'Flood Watch', 'Flash Flood Warning',
        'Severe Thunderstorm Warning', 'Severe Thunderstorm Watch',
        'Tornado Warning', 'Tornado Watch',
        'Winter Storm Warning', 'Winter Storm Watch',
        'Hurricane Warning', 'Hurricane Watch', 'Hurricane Local Statement',
        'Heat Advisory', 'Excessive Heat Warning', 'Excessive Heat Watch',
        'Drought', 'Extreme Fire Danger', 'Red Flag Warning',
        'High Wind Warning', 'High Wind Watch'
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResilienceAI/1.0 (hackathon@muidsi.edu)',
            'Accept': 'application/geo+json'
        })
        self._last_request_time = 0
        self._rate_limit_delay = 0.5  # Be nice to NOAA servers
    
    def _rate_limit(self):
        """Simple rate limiting"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'API request failed: {str(e)}'}
        except json.JSONDecodeError:
            return {'error': 'Invalid JSON response from API'}
    
    def get_active_alerts(self, state: str = None, 
                         severity: str = None,
                         event: str = None) -> List[WeatherAlert]:
        """
        Get active weather alerts
        
        Args:
            state: Two-letter state code (e.g., 'MO', 'CA')
            severity: Filter by severity ('Extreme', 'Severe', 'Moderate', 'Minor')
            event: Filter by event type
            
        Returns:
            List of WeatherAlert objects
        """
        endpoint = "/alerts/active"
        params = {}
        
        if state:
            params['area'] = state.upper()
        if severity:
            params['severity'] = severity
        if event:
            params['event'] = event
        
        data = self._make_request(endpoint, params)
        
        if 'error' in data:
            return []
        
        features = data.get('features', [])
        alerts = [WeatherAlert.from_noaa_feature(f) for f in features]
        
        # Filter to relevant events
        alerts = [a for a in alerts if any(relevant in a.event for relevant in self.RELEVANT_EVENTS)]
        
        return alerts
    
    def get_alerts_for_county(self, county_name: str, state: str) -> List[WeatherAlert]:
        """
        Get alerts affecting a specific county
        
        Args:
            county_name: County name (e.g., 'Boone')
            state: State abbreviation (e.g., 'MO')
            
        Returns:
            List of WeatherAlert objects affecting this county
        """
        # Get all alerts for the state
        state_alerts = self.get_active_alerts(state=state)
        
        # Filter to those mentioning this county
        county_alerts = []
        search_name = county_name.lower().replace(' county', '').replace(' parish', '')
        
        for alert in state_alerts:
            for affected in alert.affected_counties:
                if search_name in affected.lower():
                    county_alerts.append(alert)
                    break
        
        return county_alerts
    
    def correlate_with_vulnerability(self, county_fips: str, 
                                     county_name: str, 
                                     state: str,
                                     vulnerability_score: float) -> Dict:
        """
        Correlate weather alerts with county vulnerability
        
        Returns enhanced alert data with vulnerability context
        """
        alerts = self.get_alerts_for_county(county_name, state)
        
        if not alerts:
            return {
                'county_fips': county_fips,
                'county_name': county_name,
                'state': state,
                'vulnerability_score': vulnerability_score,
                'active_alerts': 0,
                'alerts': [],
                'risk_correlation': 'No active weather alerts'
            }
        
        # Calculate composite risk
        max_severity_weight = max(
            self.SEVERITY_WEIGHTS.get(a.severity, 0.0) for a in alerts
        )
        composite_risk = vulnerability_score * (0.5 + 0.5 * max_severity_weight)
        
        # Determine risk level
        if composite_risk >= 0.8:
            risk_level = 'Critical'
        elif composite_risk >= 0.6:
            risk_level = 'High'
        elif composite_risk >= 0.4:
            risk_level = 'Moderate'
        else:
            risk_level = 'Low'
        
        return {
            'county_fips': county_fips,
            'county_name': county_name,
            'state': state,
            'vulnerability_score': vulnerability_score,
            'active_alerts': len(alerts),
            'alerts': [a.to_dict() for a in alerts],
            'max_severity': max(a.severity for a in alerts),
            'composite_risk_score': round(composite_risk, 3),
            'risk_level': risk_level,
            'risk_correlation': f'{len(alerts)} active alerts elevate risk to {risk_level}'
        }
    
    def get_high_impact_alerts(self, min_severity: str = 'Severe') -> List[WeatherAlert]:
        """
        Get high-impact alerts across all states
        
        Args:
            min_severity: Minimum severity level to include
            
        Returns:
            List of high-severity alerts
        """
        severity_order = ['Minor', 'Moderate', 'Severe', 'Extreme']
        min_index = severity_order.index(min_severity) if min_severity in severity_order else 1
        
        all_alerts = self.get_active_alerts()
        
        high_impact = []
        for alert in all_alerts:
            if alert.severity in severity_order:
                if severity_order.index(alert.severity) >= min_index:
                    high_impact.append(alert)
        
        # Sort by severity
        high_impact.sort(
            key=lambda a: severity_order.index(a.severity) if a.severity in severity_order else -1,
            reverse=True
        )
        
        return high_impact
    
    def should_trigger_alert(self, county_fips: str, 
                            county_name: str, 
                            state: str,
                            vulnerability_threshold: float = 0.6) -> Dict:
        """
        Determine if weather conditions should trigger an alert
        
        Returns:
            Dict with trigger decision and alert details
        """
        alerts = self.get_alerts_for_county(county_name, state)
        
        if not alerts:
            return {
                'should_trigger': False,
                'reason': 'No active weather alerts'
            }
        
        # Check for severe/extreme alerts
        severe_alerts = [a for a in alerts if a.severity in ['Severe', 'Extreme']]
        
        if severe_alerts:
            return {
                'should_trigger': True,
                'reason': f'{len(severe_alerts)} severe/extreme weather alerts active',
                'triggering_alerts': [a.to_dict() for a in severe_alerts],
                'recommended_severity': 'high',
                'recommended_message': f'Severe weather: {severe_alerts[0].headline}'
            }
        
        # Check for moderate alerts in high-vulnerability counties
        moderate_alerts = [a for a in alerts if a.severity == 'Moderate']
        
        return {
            'should_trigger': len(moderate_alerts) > 0,
            'reason': f'{len(moderate_alerts)} moderate weather alerts active',
            'triggering_alerts': [a.to_dict() for a in moderate_alerts],
            'recommended_severity': 'medium',
            'recommended_message': f'Weather advisory: {moderate_alerts[0].headline if moderate_alerts else "None"}'
        }


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NOAA Weather Client CLI")
    parser.add_argument("--state", type=str, help="State code (e.g., MO)")
    parser.add_argument("--county", type=str, help="County name (e.g., Boone)")
    parser.add_argument("--severity", type=str, choices=['Extreme', 'Severe', 'Moderate', 'Minor'])
    parser.add_argument("--high-impact", action="store_true", help="Show high impact alerts only")
    parser.add_argument("--correlate", action="store_true", help="Correlate with vulnerability")
    parser.add_argument("--fips", type=str, help="County FIPS for correlation")
    parser.add_argument("--vuln-score", type=float, default=0.5, help="Vulnerability score for correlation")
    
    args = parser.parse_args()
    
    client = NOAAWeatherClient()
    
    if args.high_impact:
        alerts = client.get_high_impact_alerts()
        print(f"\n🚨 High Impact Alerts ({len(alerts)}):")
        for alert in alerts[:10]:
            print(f"  [{alert.severity}] {alert.event}: {alert.headline[:80]}...")
    
    elif args.correlate and args.fips and args.county and args.state:
        result = client.correlate_with_vulnerability(
            args.fips, args.county, args.state, args.vuln_score
        )
        print(f"\n🔗 Weather-Vulnerability Correlation for {args.county}, {args.state}")
        print(f"  Vulnerability Score: {result['vulnerability_score']}")
        print(f"  Active Alerts: {result['active_alerts']}")
        print(f"  Composite Risk: {result.get('composite_risk_score', 'N/A')}")
        print(f"  Risk Level: {result.get('risk_level', 'N/A')}")
        for alert in result.get('alerts', [])[:3]:
            print(f"    - [{alert['severity']}] {alert['event']}")
    
    elif args.county and args.state:
        alerts = client.get_alerts_for_county(args.county, args.state)
        print(f"\n🌦️ Active Alerts for {args.county}, {args.state} ({len(alerts)}):")
        for alert in alerts:
            print(f"  [{alert.severity}] {alert.event}")
            print(f"    {alert.headline}")
    
    elif args.state:
        alerts = client.get_active_alerts(state=args.state, severity=args.severity)
        print(f"\n🌦️ Active Alerts for {args.state} ({len(alerts)}):")
        for alert in alerts[:20]:
            print(f"  [{alert.severity}] {alert.event}: {alert.headline[:60]}...")
    
    else:
        # Show all high-impact alerts
        alerts = client.get_high_impact_alerts()
        print(f"\n🚨 Nationwide High Impact Alerts ({len(alerts)}):")
        for alert in alerts[:10]:
            print(f"  [{alert.severity}] {alert.event}: {alert.area_desc[:60]}...")
