"""
Severe Weather Alert Processing Pipeline
Handles ingestion, processing, and dispatch of weather alerts
"""
import asyncio
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

from enhanced_noaa_client import EnhancedNOAAClient, WeatherAlert, AlertSeverity

logger = logging.getLogger(__name__)


class AlertStatus(Enum):
    """Alert processing status"""
    RECEIVED = "received"
    PARSING = "parsing"
    VALIDATING = "validating"
    ENRICHING = "enriching"
    CORRELATING = "correlating"
    PROCESSED = "processed"
    DISPATCHED = "dispatched"
    ERROR = "error"


class AlertCategory(Enum):
    """Categorized alert types"""
    TORNADO = "tornado"
    SEVERE_THUNDERSTORM = "severe_thunderstorm"
    FLOOD = "flood"
    FLASH_FLOOD = "flash_flood"
    WINTER_STORM = "winter_storm"
    HURRICANE = "hurricane"
    HEAT = "heat"
    FIRE = "fire"
    WIND = "wind"
    OTHER = "other"


@dataclass
class ProcessedAlert:
    """Fully processed weather alert with all enrichments"""
    original_alert: WeatherAlert
    status: AlertStatus
    received_at: datetime
    processed_at: Optional[datetime] = None
    processing_duration_ms: Optional[float] = None
    category: Optional[AlertCategory] = None
    affected_population: Optional[int] = None
    affected_area_sq_km: Optional[float] = None
    intersecting_counties: List[Dict] = field(default_factory=list)
    critical_facilities_at_risk: List[Dict] = field(default_factory=list)
    infrastructure_risk_score: Optional[float] = None
    vulnerability_context: Optional[Dict] = None
    historical_similar_events: List[Dict] = field(default_factory=list)
    composite_risk_score: Optional[float] = None
    recommended_actions: List[str] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)
    escalation_level: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.original_alert.id,
            'event': self.original_alert.event,
            'severity': self.original_alert.severity.value,
            'status': self.status.value,
            'received_at': self.received_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processing_duration_ms': self.processing_duration_ms,
            'category': self.category.value if self.category else None,
            'affected_population': self.affected_population,
            'affected_area_sq_km': self.affected_area_sq_km,
            'intersecting_counties': self.intersecting_counties,
            'critical_facilities_at_risk': self.critical_facilities_at_risk,
            'infrastructure_risk_score': self.infrastructure_risk_score,
            'composite_risk_score': self.composite_risk_score,
            'recommended_actions': self.recommended_actions,
            'notification_channels': self.notification_channels,
            'escalation_level': self.escalation_level,
            'error_message': self.error_message
        }


class CAPAlertParser:
    """Parser for Common Alerting Protocol (CAP) XML messages"""
    
    CAP_NS = '{urn:oasis:names:tc:emergency:cap:1.2}'
    
    EVENT_CATEGORIES = {
        'tornado': AlertCategory.TORNADO,
        'severe thunderstorm': AlertCategory.SEVERE_THUNDERSTORM,
        'flash flood': AlertCategory.FLASH_FLOOD,
        'flood': AlertCategory.FLOOD,
        'winter storm': AlertCategory.WINTER_STORM,
        'blizzard': AlertCategory.WINTER_STORM,
        'ice storm': AlertCategory.WINTER_STORM,
        'hurricane': AlertCategory.HURRICANE,
        'tropical storm': AlertCategory.HURRICANE,
        'heat': AlertCategory.HEAT,
        'excessive heat': AlertCategory.HEAT,
        'fire': AlertCategory.FIRE,
        'red flag': AlertCategory.FIRE,
        'wind': AlertCategory.WIND,
        'high wind': AlertCategory.WIND,
    }
    
    @classmethod
    def parse_cap_xml(cls, xml_content: str) -> Optional[Dict[str, Any]]:
        try:
            root = ET.fromstring(xml_content)
            ns = cls.CAP_NS if root.tag.startswith(cls.CAP_NS) else ''
            
            alert_data = {
                'identifier': cls._get_text(root, f'{ns}identifier'),
                'sender': cls._get_text(root, f'{ns}sender'),
                'sent': cls._get_text(root, f'{ns}sent'),
                'status': cls._get_text(root, f'{ns}status'),
                'msg_type': cls._get_text(root, f'{ns}msgType'),
                'scope': cls._get_text(root, f'{ns}scope'),
                'info': []
            }
            
            for info in root.findall(f'{ns}info'):
                info_data = cls._parse_info_block(info, ns)
                alert_data['info'].append(info_data)
            
            return alert_data
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse CAP XML: {e}")
            return None
    
    @classmethod
    def _parse_info_block(cls, info: ET.Element, ns: str) -> Dict[str, Any]:
        info_data = {
            'language': cls._get_text(info, f'{ns}language'),
            'category': cls._get_text(info, f'{ns}category'),
            'event': cls._get_text(info, f'{ns}event'),
            'urgency': cls._get_text(info, f'{ns}urgency'),
            'severity': cls._get_text(info, f'{ns}severity'),
            'certainty': cls._get_text(info, f'{ns}certainty'),
            'effective': cls._get_text(info, f'{ns}effective'),
            'onset': cls._get_text(info, f'{ns}onset'),
            'expires': cls._get_text(info, f'{ns}expires'),
            'sender_name': cls._get_text(info, f'{ns}senderName'),
            'headline': cls._get_text(info, f'{ns}headline'),
            'description': cls._get_text(info, f'{ns}description'),
            'instruction': cls._get_text(info, f'{ns}instruction'),
            'web': cls._get_text(info, f'{ns}web'),
            'contact': cls._get_text(info, f'{ns}contact'),
            'areas': [],
            'polygons': []
        }
        
        for area in info.findall(f'{ns}area'):
            area_data = cls._parse_area_block(area, ns)
            info_data['areas'].append(area_data)
        
        for polygon in info.findall(f'{ns}polygon'):
            if polygon.text:
                coords = cls._parse_polygon_text(polygon.text)
                if coords:
                    info_data['polygons'].append(coords)
        
        return info_data
    
    @classmethod
    def _parse_area_block(cls, area: ET.Element, ns: str) -> Dict[str, Any]:
        area_data = {
            'description': cls._get_text(area, f'{ns}areaDesc'),
            'polygons': [],
            'geocodes': {}
        }
        
        for polygon in area.findall(f'{ns}polygon'):
            if polygon.text:
                coords = cls._parse_polygon_text(polygon.text)
                if coords:
                    area_data['polygons'].append(coords)
        
        for geocode in area.findall(f'{ns}geocode'):
            value_name = cls._get_text(geocode, f'{ns}valueName')
            value = cls._get_text(geocode, f'{ns}value')
            if value_name and value:
                area_data['geocodes'][value_name] = value
        
        return area_data
    
    @classmethod
    def _parse_polygon_text(cls, text: str) -> Optional[List[tuple]]:
        try:
            coords = []
            for point in text.strip().split(' '):
                parts = point.split(',')
                if len(parts) == 2:
                    lat, lon = float(parts[0]), float(parts[1])
                    coords.append((lat, lon))
            return coords
        except ValueError:
            return None
    
    @classmethod
    def _get_text(cls, element: ET.Element, path: str) -> Optional[str]:
        elem = element.find(path)
        return elem.text if elem is not None else None
    
    @classmethod
    def categorize_event(cls, event: str) -> AlertCategory:
        event_lower = event.lower()
        for pattern, category in cls.EVENT_CATEGORIES.items():
            if pattern in event_lower:
                return category
        return AlertCategory.OTHER


class SeverityScorer:
    """Calculates severity scores for weather alerts"""
    
    SEVERITY_WEIGHTS = {
        AlertSeverity.EXTREME: 1.0,
        AlertSeverity.SEVERE: 0.8,
        AlertSeverity.MODERATE: 0.5,
        AlertSeverity.MINOR: 0.2,
        AlertSeverity.UNKNOWN: 0.0
    }
    
    URGENCY_WEIGHTS = {
        'Immediate': 1.0,
        'Expected': 0.7,
        'Future': 0.4,
        'Past': 0.1,
        'Unknown': 0.0
    }
    
    CERTAINTY_WEIGHTS = {
        'Observed': 1.0,
        'Likely': 0.8,
        'Possible': 0.5,
        'Unlikely': 0.2,
        'Unknown': 0.0
    }
    
    CATEGORY_MULTIPLIERS = {
        AlertCategory.TORNADO: 1.5,
        AlertCategory.FLASH_FLOOD: 1.4,
        AlertCategory.HURRICANE: 1.3,
        AlertCategory.SEVERE_THUNDERSTORM: 1.2,
        AlertCategory.FLOOD: 1.1,
        AlertCategory.WINTER_STORM: 1.1,
        AlertCategory.FIRE: 1.2,
        AlertCategory.HEAT: 1.0,
        AlertCategory.WIND: 1.0,
        AlertCategory.OTHER: 1.0
    }
    
    def calculate_severity_score(self, alert: WeatherAlert, category: AlertCategory) -> float:
        severity_score = self.SEVERITY_WEIGHTS.get(alert.severity, 0.0)
        urgency_score = self.URGENCY_WEIGHTS.get(alert.urgency.value, 0.0)
        certainty_score = self.CERTAINTY_WEIGHTS.get(alert.certainty.value, 0.0)
        category_mult = self.CATEGORY_MULTIPLIERS.get(category, 1.0)
        
        composite = (0.4 * severity_score + 0.3 * urgency_score + 0.3 * certainty_score) * category_mult
        return min(composite, 1.0)
    
    def calculate_impact_score(
        self,
        alert: WeatherAlert,
        geocoding_results: Dict[str, Any],
        vulnerability_context: Optional[Dict] = None
    ) -> float:
        impact_factors = []
        
        population = geocoding_results.get('population_estimate')
        if population:
            pop_factor = min(population / 1_000_000, 1.0)
            impact_factors.append(pop_factor)
        
        facilities = geocoding_results.get('critical_facilities', [])
        if facilities:
            facility_factor = min(len(facilities) / 50, 1.0)
            impact_factors.append(facility_factor)
        
        if vulnerability_context:
            vuln_score = vulnerability_context.get('vulnerability_score', 0.5)
            impact_factors.append(vuln_score)
        
        if impact_factors:
            return sum(impact_factors) / len(impact_factors)
        
        return 0.5


class AlertProcessor:
    """Main alert processing pipeline"""
    
    def __init__(
        self,
        noaa_client: Optional[EnhancedNOAAClient] = None,
        scorer: Optional[SeverityScorer] = None,
        output_handlers: Optional[List[Callable]] = None
    ):
        self.noaa_client = noaa_client or EnhancedNOAAClient()
        self.scorer = scorer or SeverityScorer()
        self.output_handlers = output_handlers or []
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._processed_alerts: Dict[str, ProcessedAlert] = {}
        self._is_running = False
    
    async def start(self):
        self._is_running = True
        logger.info("Alert processor started")
        
        while self._is_running:
            try:
                alert = await asyncio.wait_for(self._processing_queue.get(), timeout=1.0)
                await self._process_alert(alert)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
    
    def stop(self):
        self._is_running = False
        logger.info("Alert processor stopped")
    
    async def ingest_alert(self, alert: WeatherAlert):
        await self._processing_queue.put(alert)
        logger.info(f"Alert {alert.id} ingested for processing")
    
    async def ingest_cap_xml(self, xml_content: str):
        parsed = CAPAlertParser.parse_cap_xml(xml_content)
        if parsed:
            for info in parsed.get('info', []):
                alert = self._cap_to_weather_alert(parsed, info)
                await self.ingest_alert(alert)
    
    def _cap_to_weather_alert(self, parsed: Dict, info: Dict) -> WeatherAlert:
        return WeatherAlert(
            id=parsed.get('identifier', ''),
            event=info.get('event', 'Unknown'),
            severity=AlertSeverity(info.get('severity', 'Unknown')),
            certainty=info.get('certainty', 'Unknown'),
            urgency=info.get('urgency', 'Unknown'),
            headline=info.get('headline', ''),
            description=info.get('description', ''),
            instruction=info.get('instruction', ''),
            area_desc='; '.join(a.get('description', '') for a in info.get('areas', [])),
            affected_counties=[a.get('description', '') for a in info.get('areas', [])],
            affected_fips=[],
            effective=datetime.fromisoformat(info.get('effective', '').replace('Z', '+00:00')),
            expires=datetime.fromisoformat(info.get('expires', '').replace('Z', '+00:00')),
            onset=datetime.fromisoformat(info.get('onset', '').replace('Z', '+00:00')) if info.get('onset') else None,
            ends=datetime.fromisoformat(info.get('ends', '').replace('Z', '+00:00')) if info.get('ends') else None,
            sender=parsed.get('sender', ''),
            sender_email=None,
            polygon=info.get('polygons', [None])[0] if info.get('polygons') else None,
            geocode={},
            parameters={}
        )
    
    async def _process_alert(self, alert: WeatherAlert):
        received_at = datetime.utcnow()
        
        processed = ProcessedAlert(
            original_alert=alert,
            status=AlertStatus.RECEIVED,
            received_at=received_at
        )
        
        try:
            processed.status = AlertStatus.PARSING
            processed.category = CAPAlertParser.categorize_event(alert.event)
            
            processed.status = AlertStatus.ENRICHING
            
            severity_score = self.scorer.calculate_severity_score(alert, processed.category)
            impact_score = 0.5
            
            processed.composite_risk_score = (severity_score * 0.6 + impact_score * 0.4)
            
            processed.recommended_actions = self._generate_recommendations(processed)
            processed.notification_channels = self._determine_channels(processed)
            processed.escalation_level = self._determine_escalation(processed)
            
            processed.status = AlertStatus.PROCESSED
            processed.processed_at = datetime.utcnow()
            processed.processing_duration_ms = (processed.processed_at - received_at).total_seconds() * 1000
            
            self._processed_alerts[alert.id] = processed
            await self._dispatch_alert(processed)
            
        except Exception as e:
            logger.error(f"Error processing alert {alert.id}: {e}")
            processed.status = AlertStatus.ERROR
            processed.error_message = str(e)
            processed.retry_count += 1
    
    def _generate_recommendations(self, processed: ProcessedAlert) -> List[str]:
        recommendations = []
        alert = processed.original_alert
        
        if processed.category == AlertCategory.TORNADO:
            recommendations.extend([
                "Activate Emergency Operations Center immediately",
                "Issue shelter-in-place orders for affected areas",
                "Deploy search and rescue teams to standby",
                "Open designated tornado shelters"
            ])
        
        elif processed.category == AlertCategory.FLASH_FLOOD:
            recommendations.extend([
                "Evacuate flood-prone areas immediately",
                "Close roads in affected zones",
                "Monitor stream gauges continuously",
                "Alert downstream communities"
            ])
        
        elif processed.category == AlertCategory.SEVERE_THUNDERSTORM:
            recommendations.extend([
                "Issue severe weather warnings",
                "Prepare for power outages",
                "Secure outdoor equipment",
                "Monitor for tornado development"
            ])
        
        if alert.severity == AlertSeverity.EXTREME:
            recommendations.extend([
                "Declare state of emergency",
                "Request mutual aid agreements",
                "Coordinate with state emergency management"
            ])
        
        if processed.affected_population:
            if processed.affected_population > 100000:
                recommendations.append("Activate mass care facilities")
            if processed.affected_population > 500000:
                recommendations.append("Request federal assistance standby")
        
        return recommendations
    
    def _determine_channels(self, processed: ProcessedAlert) -> List[str]:
        channels = ['dashboard', 'api']
        alert = processed.original_alert
        
        if alert.severity in [AlertSeverity.SEVERE, AlertSeverity.EXTREME]:
            channels.extend(['sms', 'push', 'email'])
        
        if alert.severity == AlertSeverity.EXTREME:
            channels.extend(['siren', 'radio', 'tv'])
        
        if processed.affected_population:
            if processed.affected_population > 10000:
                channels.append('social_media')
            if processed.affected_population > 100000:
                channels.append('emergency_broadcast')
        
        return list(set(channels))
    
    def _determine_escalation(self, processed: ProcessedAlert) -> str:
        alert = processed.original_alert
        
        if alert.severity == AlertSeverity.EXTREME:
            return 'level_1_critical'
        elif alert.severity == AlertSeverity.SEVERE:
            return 'level_2_high'
        elif alert.severity == AlertSeverity.MODERATE:
            return 'level_3_moderate'
        else:
            return 'level_4_low'
    
    async def _dispatch_alert(self, processed: ProcessedAlert):
        processed.status = AlertStatus.DISPATCHED
        
        for handler in self.output_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(processed)
                else:
                    handler(processed)
            except Exception as e:
                logger.error(f"Output handler error: {e}")
    
    def get_processed_alert(self, alert_id: str) -> Optional[ProcessedAlert]:
        return self._processed_alerts.get(alert_id)
    
    def get_active_processed_alerts(
        self,
        min_severity: Optional[AlertSeverity] = None
    ) -> List[ProcessedAlert]:
        alerts = [a for a in self._processed_alerts.values() if a.original_alert.is_active]
        
        if min_severity:
            alerts = [a for a in alerts if a.original_alert.severity.value >= min_severity.value]
        
        alerts.sort(key=lambda a: a.composite_risk_score or 0, reverse=True)
        return alerts
