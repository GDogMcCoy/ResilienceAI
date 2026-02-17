"""
Weather Visualization Components
Creates visualizations for weather data and alerts
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from enhanced_noaa_client import WeatherAlert, AlertSeverity, get_severity_color

logger = logging.getLogger(__name__)


class WeatherAlertMap:
    """Generates map visualizations for weather alerts"""
    
    def __init__(self):
        self.map_style = "carto-positron"
    
    def create_alert_geojson(self, alerts: List[WeatherAlert]) -> Dict[str, Any]:
        """Create GeoJSON feature collection from alerts"""
        features = []
        
        for alert in alerts:
            if alert.polygon:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[lon, lat] for lat, lon in alert.polygon]]
                    },
                    "properties": {
                        "id": alert.id,
                        "event": alert.event,
                        "severity": alert.severity.value,
                        "urgency": alert.urgency.value,
                        "headline": alert.headline,
                        "effective": alert.effective.isoformat(),
                        "expires": alert.expires.isoformat(),
                        "color": get_severity_color(alert.severity),
                        "affected_counties": alert.affected_counties
                    }
                }
                features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def create_alert_map_config(
        self,
        alerts: List[WeatherAlert],
        center: Optional[tuple] = None,
        zoom: int = 6
    ) -> Dict[str, Any]:
        """Create map configuration for visualization"""
        geojson = self.create_alert_geojson(alerts)
        
        if not center and alerts:
            first_alert = alerts[0]
            if first_alert.polygon:
                center = (
                    sum(p[0] for p in first_alert.polygon) / len(first_alert.polygon),
                    sum(p[1] for p in first_alert.polygon) / len(first_alert.polygon)
                )
            else:
                center = (39.8283, -98.5795)  # US center
        elif not center:
            center = (39.8283, -98.5795)
        
        return {
            "type": "map",
            "config": {
                "center": {"lat": center[0], "lon": center[1]},
                "zoom": zoom,
                "style": self.map_style,
                "layers": [
                    {
                        "type": "geojson",
                        "data": geojson,
                        "style": {
                            "fillColor": ["get", "color"],
                            "fillOpacity": 0.5,
                            "strokeColor": ["get", "color"],
                            "strokeWidth": 2
                        },
                        "popup": {
                            "title": ["get", "event"],
                            "content": ["get", "headline"]
                        }
                    }
                ]
            }
        }


class WeatherAlertTimeline:
    """Generates timeline visualizations for weather alerts"""
    
    def create_timeline_data(self, alerts: List[WeatherAlert]) -> List[Dict[str, Any]]:
        """Create timeline data from alerts"""
        timeline_items = []
        
        for alert in alerts:
            item = {
                "id": alert.id,
                "start": alert.effective.isoformat(),
                "end": alert.expires.isoformat(),
                "content": f"{alert.severity.value}: {alert.event}",
                "group": alert.severity.value,
                "style": f"background-color: {get_severity_color(alert.severity)}; color: white;",
                "title": alert.headline,
                "data": {
                    "event": alert.event,
                    "description": alert.description[:100] + "..." if len(alert.description) > 100 else alert.description,
                    "affected_areas": alert.affected_counties
                }
            }
            timeline_items.append(item)
        
        return timeline_items
    
    def create_timeline_config(self, alerts: List[WeatherAlert]) -> Dict[str, Any]:
        """Create timeline configuration"""
        items = self.create_timeline_data(alerts)
        
        groups = list(set([alert.severity.value for alert in alerts]))
        groups.sort()
        
        return {
            "type": "timeline",
            "config": {
                "groups": [{"id": g, "content": g} for g in groups],
                "items": items,
                "options": {
                    "stack": True,
                    "start": min([a.effective for a in alerts]).isoformat() if alerts else None,
                    "end": max([a.expires for a in alerts]).isoformat() if alerts else None,
                    "zoomMin": 1000 * 60 * 60,  # 1 hour
                    "zoomMax": 1000 * 60 * 60 * 24 * 7  # 1 week
                }
            }
        }


class WeatherDashboard:
    """Generates weather dashboard data"""
    
    def __init__(self):
        self.alert_map = WeatherAlertMap()
        self.alert_timeline = WeatherAlertTimeline()
    
    def create_dashboard_data(
        self,
        alerts: List[WeatherAlert],
        county_name: Optional[str] = None,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create complete dashboard data"""
        severity_counts = self._count_by_severity(alerts)
        event_counts = self._count_by_event(alerts)
        
        active_alerts = [a for a in alerts if a.is_active]
        expiring_soon = [a for a in alerts if a.time_remaining < timedelta(hours=2)]
        
        return {
            "summary": {
                "total_alerts": len(alerts),
                "active_alerts": len(active_alerts),
                "expiring_soon": len(expiring_soon),
                "last_updated": datetime.utcnow().isoformat()
            },
            "severity_breakdown": severity_counts,
            "event_breakdown": event_counts,
            "alerts": [a.to_dict() for a in alerts[:20]],
            "map": self.alert_map.create_alert_map_config(alerts) if alerts else None,
            "timeline": self.alert_timeline.create_timeline_config(alerts) if alerts else None,
            "location": {
                "county": county_name,
                "state": state
            } if county_name and state else None
        }
    
    def _count_by_severity(self, alerts: List[WeatherAlert]) -> Dict[str, int]:
        """Count alerts by severity"""
        counts = {}
        for alert in alerts:
            severity = alert.severity.value
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _count_by_event(self, alerts: List[WeatherAlert]) -> Dict[str, int]:
        """Count alerts by event type"""
        counts = {}
        for alert in alerts:
            event = alert.event
            counts[event] = counts.get(event, 0) + 1
        return counts
    
    def create_alert_card(self, alert: WeatherAlert) -> Dict[str, Any]:
        """Create alert card data"""
        return {
            "id": alert.id,
            "title": alert.event,
            "severity": alert.severity.value,
            "severity_color": get_severity_color(alert.severity),
            "headline": alert.headline,
            "description": alert.description[:200] + "..." if len(alert.description) > 200 else alert.description,
            "instruction": alert.instruction[:200] + "..." if alert.instruction and len(alert.instruction) > 200 else alert.instruction,
            "effective": alert.effective.isoformat(),
            "expires": alert.expires.isoformat(),
            "time_remaining": str(alert.time_remaining),
            "affected_areas": alert.affected_counties[:5],
            "is_active": alert.is_active
        }


class WeatherChartGenerator:
    """Generates charts for weather data"""
    
    def create_severity_chart(self, alerts: List[WeatherAlert]) -> Dict[str, Any]:
        """Create severity distribution chart"""
        severity_order = ['Extreme', 'Severe', 'Moderate', 'Minor', 'Unknown']
        counts = {s: 0 for s in severity_order}
        
        for alert in alerts:
            severity = alert.severity.value
            if severity in counts:
                counts[severity] += 1
        
        return {
            "type": "bar",
            "data": {
                "labels": severity_order,
                "datasets": [{
                    "label": "Alert Count",
                    "data": [counts[s] for s in severity_order],
                    "backgroundColor": ['#7f0000', '#ff0000', '#ff9900', '#ffff00', '#808080']
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": "Alerts by Severity"
                },
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
    
    def create_event_type_chart(self, alerts: List[WeatherAlert], top_n: int = 10) -> Dict[str, Any]:
        """Create event type distribution chart"""
        event_counts = {}
        for alert in alerts:
            event = alert.event
            event_counts[event] = event_counts.get(event, 0) + 1
        
        sorted_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return {
            "type": "horizontalBar",
            "data": {
                "labels": [e[0] for e in sorted_events],
                "datasets": [{
                    "label": "Alert Count",
                    "data": [e[1] for e in sorted_events],
                    "backgroundColor": '#3b82f6'
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": f"Top {top_n} Event Types"
                },
                "scales": {
                    "x": {
                        "beginAtZero": True
                    }
                }
            }
        }
    
    def create_time_series_chart(self, alerts: List[WeatherAlert]) -> Dict[str, Any]:
        """Create time series of alert counts"""
        from collections import defaultdict
        
        hourly_counts = defaultdict(int)
        
        for alert in alerts:
            hour_key = alert.effective.strftime('%Y-%m-%d %H:00')
            hourly_counts[hour_key] += 1
        
        sorted_hours = sorted(hourly_counts.keys())
        
        return {
            "type": "line",
            "data": {
                "labels": sorted_hours,
                "datasets": [{
                    "label": "Alerts",
                    "data": [hourly_counts[h] for h in sorted_hours],
                    "borderColor": '#3b82f6',
                    "fill": False
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": "Alerts Over Time"
                },
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
