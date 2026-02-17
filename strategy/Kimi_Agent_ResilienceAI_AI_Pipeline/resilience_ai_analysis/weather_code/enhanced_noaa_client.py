"""
Enhanced NOAA National Weather Service API Client
Provides comprehensive weather data integration with forecasting, radar, and impact modeling
"""
import requests
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """NOAA Alert Severity Levels"""
    EXTREME = "Extreme"
    SEVERE = "Severe"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


class AlertUrgency(Enum):
    """NOAA Alert Urgency Levels"""
    IMMEDIATE = "Immediate"
    EXPECTED = "Expected"
    FUTURE = "Future"
    PAST = "Past"
    UNKNOWN = "Unknown"


class AlertCertainty(Enum):
    """NOAA Alert Certainty Levels"""
    OBSERVED = "Observed"
    LIKELY = "Likely"
    POSSIBLE = "Possible"
    UNLIKELY = "Unlikely"
    UNKNOWN = "Unknown"


@dataclass
class WeatherAlert:
    """Enhanced NOAA weather alert with geospatial and impact data"""
    id: str
    event: str
    severity: AlertSeverity
    certainty: AlertCertainty
    urgency: AlertUrgency
    headline: str
    description: str
    instruction: str
    area_desc: str
    affected_counties: List[str]
    affected_fips: List[str]
    effective: datetime
    expires: datetime
    onset: Optional[datetime]
    ends: Optional[datetime]
    sender: str
    sender_email: Optional[str]
    polygon: Optional[List[Tuple[float, float]]]
    geocode: Dict[str, List[str]]
    parameters: Dict[str, Any]
    estimated_population_affected: Optional[int] = None
    critical_facilities_at_risk: List[str] = field(default_factory=list)
    infrastructure_risk_score: Optional[float] = None
    
    @classmethod
    def from_noaa_feature(cls, feature: Dict) -> 'WeatherAlert':
        props = feature.get('properties', {})
        geo = feature.get('geometry', {}) or {}
        
        def parse_dt(dt_str: Optional[str]) -> Optional[datetime]:
            if not dt_str:
                return None
            try:
                return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            except:
                return None
        
        polygon = None
        if geo.get('type') == 'Polygon':
            polygon = geo.get('coordinates', [[]])[0]
            polygon = [(coord[1], coord[0]) for coord in polygon]
        
        geocode = props.get('geocode', {})
        area_desc = props.get('areaDesc', '')
        affected_counties = [c.strip() for c in area_desc.split(';') if c.strip()]
        affected_fips = geocode.get('FIPS', [])
        
        return cls(
            id=feature.get('id', ''),
            event=props.get('event', 'Unknown'),
            severity=AlertSeverity(props.get('severity', 'Unknown')),
            certainty=AlertCertainty(props.get('certainty', 'Unknown')),
            urgency=AlertUrgency(props.get('urgency', 'Unknown')),
            headline=props.get('headline', ''),
            description=props.get('description', ''),
            instruction=props.get('instruction', ''),
            area_desc=area_desc,
            affected_counties=affected_counties,
            affected_fips=affected_fips,
            effective=parse_dt(props.get('effective')) or datetime.utcnow(),
            expires=parse_dt(props.get('expires')) or datetime.utcnow(),
            onset=parse_dt(props.get('onset')),
            ends=parse_dt(props.get('ends')),
            sender=props.get('senderName', ''),
            sender_email=props.get('senderEmail'),
            polygon=polygon,
            geocode=geocode,
            parameters=props.get('parameters', {})
        )
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'event': self.event,
            'severity': self.severity.value,
            'certainty': self.certainty.value,
            'urgency': self.urgency.value,
            'headline': self.headline,
            'description': self.description,
            'instruction': self.instruction,
            'area_desc': self.area_desc,
            'affected_counties': self.affected_counties,
            'affected_fips': self.affected_fips,
            'effective': self.effective.isoformat() if self.effective else None,
            'expires': self.expires.isoformat() if self.expires else None,
            'onset': self.onset.isoformat() if self.onset else None,
            'ends': self.ends.isoformat() if self.ends else None,
            'sender': self.sender,
            'polygon': self.polygon,
            'estimated_population_affected': self.estimated_population_affected,
            'critical_facilities_at_risk': self.critical_facilities_at_risk,
            'infrastructure_risk_score': self.infrastructure_risk_score
        }
    
    @property
    def is_active(self) -> bool:
        now = datetime.utcnow()
        return self.effective <= now <= self.expires


@dataclass
class WeatherForecast:
    """NWS Gridpoint forecast data"""
    grid_id: str
    grid_x: int
    grid_y: int
    forecast_office: str
    generated_at: datetime
    updated_at: datetime
    periods: List[Dict[str, Any]]
    elevation: Optional[float] = None
    
    @classmethod
    def from_nws_response(cls, data: Dict) -> 'WeatherForecast':
        props = data.get('properties', {})
        return cls(
            grid_id=props.get('gridId', ''),
            grid_x=props.get('gridX', 0),
            grid_y=props.get('gridY', 0),
            forecast_office=props.get('forecastOffice', ''),
            generated_at=datetime.fromisoformat(props.get('generatedAt', '').replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(props.get('updateTime', '').replace('Z', '+00:00')),
            periods=props.get('periods', []),
            elevation=props.get('elevation', {}).get('value')
        )


@dataclass
class WeatherStation:
    """NWS Weather Station metadata"""
    station_id: str
    name: str
    latitude: float
    longitude: float
    elevation: Optional[float]
    timezone: str
    county_fips: Optional[str]
    county_name: Optional[str]
    state: Optional[str]
    
    @classmethod
    def from_nws_response(cls, data: Dict) -> 'WeatherStation':
        props = data.get('properties', {})
        geo = data.get('geometry', {})
        coords = geo.get('coordinates', [0, 0]) if geo else [0, 0]
        
        return cls(
            station_id=props.get('stationIdentifier', ''),
            name=props.get('name', ''),
            latitude=coords[1] if len(coords) > 1 else 0,
            longitude=coords[0] if len(coords) > 0 else 0,
            elevation=props.get('elevation', {}).get('value'),
            timezone=props.get('timeZone', ''),
            county_fips=props.get('county', '').split('/')[-1] if props.get('county') else None,
            county_name=props.get('countyName'),
            state=props.get('state')
        )


@dataclass
class Observation:
    """Weather observation from a station"""
    station_id: str
    timestamp: datetime
    temperature: Optional[float]
    dewpoint: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[int]
    wind_gust: Optional[float]
    barometric_pressure: Optional[float]
    sea_level_pressure: Optional[float]
    visibility: Optional[float]
    relative_humidity: Optional[float]
    wind_chill: Optional[float]
    heat_index: Optional[float]
    precipitation_last_hour: Optional[float]
    conditions: List[str]
    raw_message: Optional[str]
    
    @classmethod
    def from_nws_response(cls, data: Dict) -> 'Observation':
        props = data.get('properties', {})
        
        def get_value(prop: str) -> Optional[float]:
            val = props.get(prop, {}).get('value')
            return float(val) if val is not None else None
        
        return cls(
            station_id=props.get('station', '').split('/')[-1],
            timestamp=datetime.fromisoformat(props.get('timestamp', '').replace('Z', '+00:00')),
            temperature=get_value('temperature'),
            dewpoint=get_value('dewpoint'),
            wind_speed=get_value('windSpeed'),
            wind_direction=int(get_value('windDirection')) if get_value('windDirection') else None,
            wind_gust=get_value('windGust'),
            barometric_pressure=get_value('barometricPressure'),
            sea_level_pressure=get_value('seaLevelPressure'),
            visibility=get_value('visibility'),
            relative_humidity=get_value('relativeHumidity'),
            wind_chill=get_value('windChill'),
            heat_index=get_value('heatIndex'),
            precipitation_last_hour=get_value('precipitationLastHour'),
            conditions=props.get('textDescription', '').split(', ') if props.get('textDescription') else [],
            raw_message=props.get('rawMessage')
        )


class EnhancedNOAAClient:
    """Enhanced NOAA National Weather Service API Client"""
    
    BASE_URL = "https://api.weather.gov"
    ALERTS_URL = "https://api.weather.gov/alerts"
    
    SEVERITY_WEIGHTS = {
        AlertSeverity.EXTREME: 1.0,
        AlertSeverity.SEVERE: 0.8,
        AlertSeverity.MODERATE: 0.5,
        AlertSeverity.MINOR: 0.2,
        AlertSeverity.UNKNOWN: 0.0
    }
    
    URGENCY_WEIGHTS = {
        AlertUrgency.IMMEDIATE: 1.0,
        AlertUrgency.EXPECTED: 0.7,
        AlertUrgency.FUTURE: 0.4,
        AlertUrgency.PAST: 0.1,
        AlertUrgency.UNKNOWN: 0.0
    }
    
    HIGH_IMPACT_EVENTS = {
        'Tornado Warning', 'Tornado Watch',
        'Severe Thunderstorm Warning', 'Severe Thunderstorm Watch',
        'Flash Flood Warning', 'Flash Flood Watch',
        'Flood Warning', 'Flood Watch',
        'Hurricane Warning', 'Hurricane Watch',
        'Winter Storm Warning', 'Winter Storm Watch',
        'Extreme Heat Warning', 'Excessive Heat Warning',
        'Red Flag Warning', 'Extreme Fire Danger',
        'High Wind Warning', 'High Wind Watch'
    }
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = 300,
        rate_limit_delay: float = 0.5,
        max_retries: int = 3,
        user_agent: str = 'ResilienceAI/2.0 (weather-integration)'
    ):
        self.cache_dir = cache_dir or Path('./weather_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = cache_ttl
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.user_agent = user_agent
        
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/geo+json'
        })
        
        self._last_request_time = 0
        self._cache_index: Dict[str, Dict] = {}
        self._load_cache_index()
    
    def _load_cache_index(self):
        index_file = self.cache_dir / 'cache_index.json'
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    self._cache_index = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache index: {e}")
                self._cache_index = {}
    
    def _save_cache_index(self):
        index_file = self.cache_dir / 'cache_index.json'
        try:
            with open(index_file, 'w') as f:
                json.dump(self._cache_index, f)
        except Exception as e:
            logger.warning(f"Failed to save cache index: {e}")
    
    def _get_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        if cache_key not in self._cache_index:
            return None
        
        cache_entry = self._cache_index[cache_key]
        cached_time = datetime.fromisoformat(cache_entry['timestamp'])
        
        if datetime.utcnow() - cached_time > timedelta(seconds=self.cache_ttl):
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read cache file: {e}")
            return None
    
    def _cache_response(self, cache_key: str, data: Dict):
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            self._cache_index[cache_key] = {
                'timestamp': datetime.utcnow().isoformat(),
                'file': str(cache_file)
            }
            self._save_cache_index()
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")
    
    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict:
        cache_key = self._get_cache_key(endpoint, params)
        
        if use_cache:
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
        
        self._rate_limit()
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = self._session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if use_cache:
                    self._cache_response(cache_key, data)
                
                return data
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                else:
                    return {'error': f'HTTP {response.status_code}: {str(e)}'}
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return {'error': f'Request failed: {str(e)}'}
                    
            except json.JSONDecodeError:
                return {'error': 'Invalid JSON response'}
        
        return {'error': 'Max retries exceeded'}
    
    def get_active_alerts(
        self,
        state: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
        event: Optional[str] = None,
        zone: Optional[str] = None,
        point: Optional[Tuple[float, float]] = None,
        limit: int = 500
    ) -> List[WeatherAlert]:
        endpoint = "/alerts/active"
        params = {'limit': limit}
        
        if state:
            params['area'] = state.upper()
        if severity:
            params['severity'] = severity.value
        if event:
            params['event'] = event
        if zone:
            params['zone'] = zone
        if point:
            params['point'] = f"{point[0]},{point[1]}"
        
        data = self._make_request(endpoint, params)
        
        if 'error' in data:
            logger.error(f"Error fetching alerts: {data['error']}")
            return []
        
        features = data.get('features', [])
        alerts = [WeatherAlert.from_noaa_feature(f) for f in features]
        alerts = [a for a in alerts if any(event in a.event for event in self.HIGH_IMPACT_EVENTS)]
        
        alerts.sort(key=lambda a: (
            self.SEVERITY_WEIGHTS.get(a.severity, 0),
            self.URGENCY_WEIGHTS.get(a.urgency, 0)
        ), reverse=True)
        
        return alerts
    
    def get_alerts_for_county(
        self,
        county_name: str,
        state: str
    ) -> List[WeatherAlert]:
        state_alerts = self.get_active_alerts(state=state)
        search_name = county_name.lower().replace(' county', '').replace(' parish', '').strip()
        
        county_alerts = []
        for alert in state_alerts:
            for affected in alert.affected_counties:
                if search_name in affected.lower():
                    county_alerts.append(alert)
                    break
        
        return county_alerts
    
    def get_point_forecast(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[WeatherForecast]:
        point_endpoint = f"/points/{latitude},{longitude}"
        point_data = self._make_request(point_endpoint)
        
        if 'error' in point_data:
            return None
        
        forecast_url = point_data.get('properties', {}).get('forecast')
        if not forecast_url:
            return None
        
        forecast_endpoint = forecast_url.replace(self.BASE_URL, '')
        forecast_data = self._make_request(forecast_endpoint)
        
        if 'error' in forecast_data:
            return None
        
        return WeatherForecast.from_nws_response(forecast_data)
    
    def get_nearest_station(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[WeatherStation]:
        point_endpoint = f"/points/{latitude},{longitude}"
        point_data = self._make_request(point_endpoint)
        
        if 'error' in point_data:
            return None
        
        station_url = point_data.get('properties', {}).get('observationStations')
        if not station_url:
            return None
        
        station_endpoint = station_url.replace(self.BASE_URL, '')
        stations_data = self._make_request(station_endpoint)
        
        if 'error' in stations_data or not stations_data.get('features'):
            return None
        
        return WeatherStation.from_nws_response(stations_data['features'][0])
    
    def get_latest_observation(self, station_id: str) -> Optional[Observation]:
        endpoint = f"/stations/{station_id}/observations/latest"
        data = self._make_request(endpoint, use_cache=False)
        
        if 'error' in data:
            return None
        
        return Observation.from_nws_response(data)
    
    def correlate_with_vulnerability(
        self,
        county_fips: str,
        county_name: str,
        state: str,
        vulnerability_score: float,
        population: Optional[int] = None,
        critical_facilities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        alerts = self.get_alerts_for_county(county_name, state)
        
        if not alerts:
            return {
                'county_fips': county_fips,
                'county_name': county_name,
                'state': state,
                'vulnerability_score': vulnerability_score,
                'active_alerts': 0,
                'alerts': [],
                'risk_assessment': {
                    'level': 'Low',
                    'composite_score': vulnerability_score,
                    'description': 'No active weather alerts'
                },
                'impact_estimate': None
            }
        
        max_severity_weight = max(self.SEVERITY_WEIGHTS.get(a.severity, 0.0) for a in alerts)
        max_urgency_weight = max(self.URGENCY_WEIGHTS.get(a.urgency, 0.0) for a in alerts)
        
        composite_risk = vulnerability_score * (0.4 + 0.35 * max_severity_weight + 0.25 * max_urgency_weight)
        
        if composite_risk >= 0.8:
            risk_level = 'Critical'
        elif composite_risk >= 0.6:
            risk_level = 'High'
        elif composite_risk >= 0.4:
            risk_level = 'Moderate'
        else:
            risk_level = 'Low'
        
        impact_estimate = self._estimate_impact(alerts, vulnerability_score, population, critical_facilities)
        
        return {
            'county_fips': county_fips,
            'county_name': county_name,
            'state': state,
            'vulnerability_score': vulnerability_score,
            'active_alerts': len(alerts),
            'alerts': [a.to_dict() for a in alerts],
            'composite_risk_score': round(composite_risk, 3),
            'risk_assessment': {
                'level': risk_level,
                'composite_score': round(composite_risk, 3),
                'description': f'{len(alerts)} active alerts elevate risk to {risk_level}'
            },
            'impact_estimate': impact_estimate,
            'recommended_actions': self._generate_recommendations(alerts, risk_level)
        }
    
    def _estimate_impact(
        self,
        alerts: List[WeatherAlert],
        vulnerability_score: float,
        population: Optional[int],
        critical_facilities: Optional[List[str]]
    ) -> Dict[str, Any]:
        affected_population = None
        if population:
            severity_factor = max(self.SEVERITY_WEIGHTS.get(a.severity, 0.0) for a in alerts)
            affected_population = int(population * vulnerability_score * severity_factor)
        
        at_risk_facilities = critical_facilities or []
        
        economic_impact = None
        if population:
            base_impact = population * 100
            severity_multiplier = max(self.SEVERITY_WEIGHTS.get(a.severity, 0.0) for a in alerts)
            economic_impact = base_impact * severity_multiplier * vulnerability_score
        
        return {
            'estimated_population_affected': affected_population,
            'critical_facilities_at_risk': at_risk_facilities,
            'estimated_economic_impact_usd': round(economic_impact, 2) if economic_impact else None,
            'confidence': 'medium'
        }
    
    def _generate_recommendations(
        self,
        alerts: List[WeatherAlert],
        risk_level: str
    ) -> List[str]:
        recommendations = []
        event_types = set(a.event for a in alerts)
        
        if 'Tornado Warning' in event_types:
            recommendations.extend([
                "Activate emergency operations center",
                "Issue immediate shelter-in-place orders",
                "Deploy search and rescue teams"
            ])
        
        if 'Flash Flood Warning' in event_types:
            recommendations.extend([
                "Evacuate flood-prone areas",
                "Close roads in affected zones",
                "Monitor water levels continuously"
            ])
        
        if risk_level in ['Critical', 'High']:
            recommendations.extend([
                "Declare state of emergency",
                "Coordinate with state emergency management",
                "Prepare mutual aid agreements"
            ])
        
        if not recommendations:
            recommendations.extend([
                "Monitor weather conditions",
                "Review emergency response plans"
            ])
        
        return recommendations
    
    def clear_cache(self):
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._cache_index = {}
        self._save_cache_index()
        logger.info("Cache cleared")


def get_severity_color(severity: AlertSeverity) -> str:
    colors = {
        AlertSeverity.EXTREME: '#7f0000',
        AlertSeverity.SEVERE: '#ff0000',
        AlertSeverity.MODERATE: '#ff9900',
        AlertSeverity.MINOR: '#ffff00',
        AlertSeverity.UNKNOWN: '#808080'
    }
    return colors.get(severity, '#808080')
