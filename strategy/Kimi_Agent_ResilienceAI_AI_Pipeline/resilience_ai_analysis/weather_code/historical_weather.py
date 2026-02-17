"""
Historical Weather Analysis
Analyzes historical weather data for trend detection and pattern analysis
"""
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

import requests

from enhanced_noaa_client import WeatherAlert, AlertSeverity

logger = logging.getLogger(__name__)


class NCEIClient:
    """NOAA National Centers for Environmental Information (NCEI) API Client"""
    
    BASE_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResilienceAI/2.0 (historical-weather)',
            'Accept': 'application/json'
        })
    
    def get_historical_weather(
        self,
        station_id: str,
        start_date: datetime,
        end_date: datetime,
        dataset: str = "daily-summaries"
    ) -> List[Dict[str, Any]]:
        """Get historical weather data for a station"""
        params = {
            'stations': station_id,
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'format': 'json',
            'dataset': dataset
        }
        
        if self.api_token:
            params['token'] = self.api_token
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching historical data: {e}")
            return []
    
    def get_stations(
        self,
        state: Optional[str] = None,
        county: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get weather stations"""
        url = "https://www.ncei.noaa.gov/access/services/search/v1/data"
        params = {
            'dataset': 'daily-summaries',
            'limit': limit
        }
        
        if state:
            params['location'] = f'FIPS:{state}'
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            logger.error(f"Error fetching stations: {e}")
            return []


class HistoricalAlertAnalyzer:
    """Analyzes historical weather alerts"""
    
    def __init__(self):
        self.alert_history: List[Dict[str, Any]] = []
    
    def add_alerts(self, alerts: List[WeatherAlert]):
        """Add alerts to history"""
        for alert in alerts:
            self.alert_history.append({
                'id': alert.id,
                'event': alert.event,
                'severity': alert.severity.value,
                'effective': alert.effective.isoformat(),
                'expires': alert.expires.isoformat(),
                'affected_counties': alert.affected_counties
            })
    
    def get_severity_trends(self) -> Dict[str, Any]:
        """Analyze severity trends over time"""
        monthly_severity = defaultdict(lambda: defaultdict(int))
        
        for alert in self.alert_history:
            month = alert['effective'][:7]  # YYYY-MM
            severity = alert['severity']
            monthly_severity[month][severity] += 1
        
        return {
            'monthly_breakdown': dict(monthly_severity),
            'trend_direction': self._calculate_trend(monthly_severity)
        }
    
    def get_event_frequency(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get most frequent event types"""
        event_counts = defaultdict(int)
        
        for alert in self.alert_history:
            event_counts[alert['event']] += 1
        
        return sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def get_seasonal_patterns(self) -> Dict[str, Dict[str, int]]:
        """Analyze seasonal patterns"""
        seasonal_counts = defaultdict(lambda: defaultdict(int))
        
        for alert in self.alert_history:
            month = int(alert['effective'][5:7])  # MM
            season = self._get_season(month)
            event = alert['event']
            seasonal_counts[season][event] += 1
        
        return dict(seasonal_counts)
    
    def _get_season(self, month: int) -> str:
        """Get season from month number"""
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    def _calculate_trend(self, monthly_data: Dict) -> str:
        """Calculate trend direction from monthly data"""
        if len(monthly_data) < 3:
            return 'insufficient_data'
        
        months = sorted(monthly_data.keys())
        recent = sum(sum(monthly_data[m].values()) for m in months[-3:])
        older = sum(sum(monthly_data[m].values()) for m in months[:3])
        
        if recent > older * 1.2:
            return 'increasing'
        elif recent < older * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_alert_duration_stats(self) -> Dict[str, Any]:
        """Get statistics on alert durations"""
        durations = []
        
        for alert in self.alert_history:
            try:
                effective = datetime.fromisoformat(alert['effective'])
                expires = datetime.fromisoformat(alert['expires'])
                duration = (expires - effective).total_seconds() / 3600  # hours
                durations.append(duration)
            except:
                continue
        
        if not durations:
            return {}
        
        return {
            'average_duration_hours': sum(durations) / len(durations),
            'min_duration_hours': min(durations),
            'max_duration_hours': max(durations),
            'median_duration_hours': sorted(durations)[len(durations) // 2]
        }


class WeatherPatternDetector:
    """Detects patterns in weather data"""
    
    def __init__(self):
        self.patterns: List[Dict[str, Any]] = []
    
    def detect_severe_weather_clusters(
        self,
        alerts: List[WeatherAlert],
        time_window_hours: int = 24,
        min_alerts: int = 3
    ) -> List[Dict[str, Any]]:
        """Detect clusters of severe weather alerts"""
        clusters = []
        
        sorted_alerts = sorted(alerts, key=lambda a: a.effective)
        
        for i, alert in enumerate(sorted_alerts):
            cluster = [alert]
            window_end = alert.effective + timedelta(hours=time_window_hours)
            
            for other in sorted_alerts[i+1:]:
                if other.effective <= window_end:
                    cluster.append(other)
                else:
                    break
            
            if len(cluster) >= min_alerts:
                clusters.append({
                    'start_time': cluster[0].effective.isoformat(),
                    'end_time': cluster[-1].effective.isoformat(),
                    'alert_count': len(cluster),
                    'events': list(set(a.event for a in cluster)),
                    'max_severity': max(a.severity.value for a in cluster),
                    'affected_areas': list(set(
                        county for a in cluster for county in a.affected_counties
                    ))
                })
        
        return clusters
    
    def detect_recurring_events(
        self,
        alerts: List[WeatherAlert],
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """Detect recurring weather events"""
        event_dates = defaultdict(list)
        
        for alert in alerts:
            event_dates[alert.event].append(alert.effective)
        
        recurring = []
        for event, dates in event_dates.items():
            if len(dates) >= min_occurrences:
                dates.sort()
                intervals = [
                    (dates[i+1] - dates[i]).days
                    for i in range(len(dates) - 1)
                ]
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    recurring.append({
                        'event': event,
                        'occurrences': len(dates),
                        'first_occurrence': dates[0].isoformat(),
                        'last_occurrence': dates[-1].isoformat(),
                        'average_interval_days': avg_interval,
                        'regularity': 'regular' if self._is_regular(intervals) else 'irregular'
                    })
        
        return recurring
    
    def _is_regular(self, intervals: List[int], threshold: float = 0.3) -> bool:
        """Check if intervals are regular"""
        if len(intervals) < 2:
            return False
        
        avg = sum(intervals) / len(intervals)
        variance = sum((i - avg) ** 2 for i in intervals) / len(intervals)
        std_dev = variance ** 0.5
        
        return (std_dev / avg) < threshold
    
    def predict_next_occurrence(
        self,
        event_type: str,
        alerts: List[WeatherAlert]
    ) -> Optional[Dict[str, Any]]:
        """Predict next occurrence of an event type"""
        event_alerts = [a for a in alerts if event_type in a.event]
        
        if len(event_alerts) < 3:
            return None
        
        dates = sorted([a.effective for a in event_alerts])
        intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]
        
        avg_interval = sum(intervals) / len(intervals)
        last_occurrence = dates[-1]
        predicted_next = last_occurrence + timedelta(days=int(avg_interval))
        
        return {
            'event_type': event_type,
            'last_occurrence': last_occurrence.isoformat(),
            'predicted_next': predicted_next.isoformat(),
            'confidence': 'low' if len(intervals) < 5 else 'medium',
            'average_interval_days': avg_interval
        }


class HistoricalWeatherReport:
    """Generates historical weather reports"""
    
    def __init__(
        self,
        ncei_client: Optional[NCEIClient] = None,
        alert_analyzer: Optional[HistoricalAlertAnalyzer] = None
    ):
        self.ncei_client = ncei_client or NCEIClient()
        self.alert_analyzer = alert_analyzer or HistoricalAlertAnalyzer()
        self.pattern_detector = WeatherPatternDetector()
    
    def generate_report(
        self,
        county_name: str,
        state: str,
        days: int = 365
    ) -> Dict[str, Any]:
        """Generate comprehensive historical weather report"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        report = {
            'location': {
                'county': county_name,
                'state': state
            },
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'alert_summary': self.alert_analyzer.get_severity_trends(),
            'event_frequency': self.alert_analyzer.get_event_frequency(),
            'seasonal_patterns': self.alert_analyzer.get_seasonal_patterns(),
            'duration_stats': self.alert_analyzer.get_alert_duration_stats(),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return report
    
    def generate_risk_assessment(
        self,
        county_name: str,
        state: str
    ) -> Dict[str, Any]:
        """Generate risk assessment based on historical data"""
        event_freq = self.alert_analyzer.get_event_frequency()
        seasonal = self.alert_analyzer.get_seasonal_patterns()
        
        high_risk_events = [e for e in event_freq if e[1] > 10]
        current_season = self.pattern_detector._get_season(datetime.utcnow().month)
        seasonal_risk = seasonal.get(current_season, {})
        
        return {
            'location': {
                'county': county_name,
                'state': state
            },
            'current_season': current_season,
            'high_risk_events': high_risk_events,
            'seasonal_risk': dict(seasonal_risk),
            'overall_risk_level': self._calculate_risk_level(high_risk_events, seasonal_risk),
            'recommendations': self._generate_recommendations(high_risk_events, current_season)
        }
    
    def _calculate_risk_level(
        self,
        high_risk_events: List[Tuple[str, int]],
        seasonal_risk: Dict[str, int]
    ) -> str:
        """Calculate overall risk level"""
        risk_score = len(high_risk_events) * 10 + sum(seasonal_risk.values())
        
        if risk_score > 100:
            return 'High'
        elif risk_score > 50:
            return 'Moderate'
        else:
            return 'Low'
    
    def _generate_recommendations(
        self,
        high_risk_events: List[Tuple[str, int]],
        current_season: str
    ) -> List[str]:
        """Generate preparedness recommendations"""
        recommendations = []
        
        for event, count in high_risk_events[:3]:
            recommendations.append(f"Review and update {event} response plans")
        
        if current_season in ['Winter', 'Spring']:
            recommendations.append("Ensure winter storm supplies are stocked")
        
        if current_season in ['Summer', 'Fall']:
            recommendations.append("Monitor for severe thunderstorm and tornado activity")
        
        recommendations.append("Conduct emergency response drills")
        recommendations.append("Review evacuation routes and shelter locations")
        
        return recommendations
