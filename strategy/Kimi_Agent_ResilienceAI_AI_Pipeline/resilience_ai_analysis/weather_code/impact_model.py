"""
Weather Impact Modeling
Estimates population, infrastructure, and economic impacts from weather events
"""
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from enhanced_noaa_client import WeatherAlert, AlertSeverity

logger = logging.getLogger(__name__)


@dataclass
class ImpactEstimate:
    """Weather impact estimate"""
    alert_id: str
    event_type: str
    severity: str
    timestamp: datetime
    population_affected: Optional[int]
    critical_facilities_at_risk: List[Dict]
    infrastructure_risk_score: float
    economic_impact_usd: Optional[float]
    confidence_level: str
    assumptions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'event_type': self.event_type,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'population_affected': self.population_affected,
            'critical_facilities_at_risk': self.critical_facilities_at_risk,
            'infrastructure_risk_score': self.infrastructure_risk_score,
            'economic_impact_usd': self.economic_impact_usd,
            'confidence_level': self.confidence_level,
            'assumptions': self.assumptions
        }


class PopulationImpactModel:
    """Estimates population impact from weather events"""
    
    SEVERITY_MULTIPLIERS = {
        AlertSeverity.EXTREME: 0.9,
        AlertSeverity.SEVERE: 0.7,
        AlertSeverity.MODERATE: 0.4,
        AlertSeverity.MINOR: 0.1,
        AlertSeverity.UNKNOWN: 0.2
    }
    
    EVENT_TYPE_MULTIPLIERS = {
        'tornado': 0.8,
        'flash flood': 0.7,
        'hurricane': 0.9,
        'severe thunderstorm': 0.5,
        'flood': 0.6,
        'winter storm': 0.5,
        'fire': 0.6,
        'heat': 0.4,
        'wind': 0.3,
        'other': 0.3
    }
    
    def estimate_population_impact(
        self,
        alert: WeatherAlert,
        total_population: int,
        vulnerability_score: float,
        affected_area_pct: float = 0.5
    ) -> Dict[str, Any]:
        """Estimate population affected by weather alert"""
        severity_mult = self.SEVERITY_MULTIPLIERS.get(alert.severity, 0.2)
        
        event_type = alert.event.lower()
        event_mult = 0.3
        for event_key, mult in self.EVENT_TYPE_MULTIPLIERS.items():
            if event_key in event_type:
                event_mult = mult
                break
        
        affected_population = int(
            total_population * 
            affected_area_pct * 
            severity_mult * 
            event_mult * 
            vulnerability_score
        )
        
        evacuated_population = int(affected_population * 0.3)
        sheltered_population = int(affected_population * 0.2)
        
        return {
            'total_population': total_population,
            'affected_population': affected_population,
            'evacuated_population': evacuated_population,
            'sheltered_population': sheltered_population,
            'affected_area_pct': affected_area_pct,
            'severity_multiplier': severity_mult,
            'event_multiplier': event_mult,
            'vulnerability_score': vulnerability_score
        }


class InfrastructureImpactModel:
    """Estimates infrastructure impact from weather events"""
    
    CRITICAL_FACILITY_TYPES = [
        'hospital', 'school', 'power_plant', 'water_treatment',
        'emergency_services', 'communications', 'transportation'
    ]
    
    FACILITY_RISK_WEIGHTS = {
        'hospital': 1.0,
        'emergency_services': 0.9,
        'power_plant': 0.85,
        'water_treatment': 0.8,
        'communications': 0.75,
        'school': 0.6,
        'transportation': 0.5
    }
    
    def assess_infrastructure_risk(
        self,
        alert: WeatherAlert,
        critical_facilities: List[Dict],
        vulnerability_score: float
    ) -> Dict[str, Any]:
        """Assess risk to critical infrastructure"""
        at_risk_facilities = []
        total_risk_score = 0
        
        for facility in critical_facilities:
            facility_type = facility.get('type', 'other').lower()
            weight = self.FACILITY_RISK_WEIGHTS.get(facility_type, 0.3)
            
            risk_score = weight * self.SEVERITY_MULTIPLIERS.get(alert.severity, 0.2)
            
            if risk_score > 0.5:
                at_risk_facilities.append({
                    'name': facility.get('name', 'Unknown'),
                    'type': facility_type,
                    'risk_score': round(risk_score, 3),
                    'capacity': facility.get('capacity'),
                    'location': {
                        'lat': facility.get('latitude'),
                        'lon': facility.get('longitude')
                    }
                })
            
            total_risk_score += risk_score
        
        avg_risk_score = total_risk_score / len(critical_facilities) if critical_facilities else 0
        
        return {
            'total_facilities': len(critical_facilities),
            'at_risk_facilities': at_risk_facilities,
            'at_risk_count': len(at_risk_facilities),
            'average_risk_score': round(avg_risk_score, 3),
            'max_risk_score': round(max([f['risk_score'] for f in at_risk_facilities], default=0), 3),
            'vulnerability_score': vulnerability_score
        }
    
    @property
    def SEVERITY_MULTIPLIERS(self):
        return {
            AlertSeverity.EXTREME: 1.0,
            AlertSeverity.SEVERE: 0.8,
            AlertSeverity.MODERATE: 0.5,
            AlertSeverity.MINOR: 0.2,
            AlertSeverity.UNKNOWN: 0.2
        }


class EconomicImpactModel:
    """Estimates economic impact from weather events"""
    
    BASE_COSTS = {
        'tornado': 500_000_000,
        'flash flood': 100_000_000,
        'hurricane': 1_000_000_000,
        'severe thunderstorm': 50_000_000,
        'flood': 200_000_000,
        'winter storm': 75_000_000,
        'fire': 300_000_000,
        'heat': 25_000_000,
        'wind': 40_000_000,
        'other': 10_000_000
    }
    
    SEVERITY_MULTIPLIERS = {
        AlertSeverity.EXTREME: 2.0,
        AlertSeverity.SEVERE: 1.5,
        AlertSeverity.MODERATE: 1.0,
        AlertSeverity.MINOR: 0.5,
        AlertSeverity.UNKNOWN: 0.8
    }
    
    def estimate_economic_impact(
        self,
        alert: WeatherAlert,
        affected_population: int,
        vulnerability_score: float
    ) -> Dict[str, Any]:
        """Estimate economic impact of weather event"""
        event_type = alert.event.lower()
        base_cost = 10_000_000
        
        for event_key, cost in self.BASE_COSTS.items():
            if event_key in event_type:
                base_cost = cost
                break
        
        severity_mult = self.SEVERITY_MULTIPLIERS.get(alert.severity, 0.8)
        
        population_factor = min(affected_population / 100_000, 2.0)
        
        total_cost = base_cost * severity_mult * population_factor * vulnerability_score
        
        property_damage = total_cost * 0.6
        business_interruption = total_cost * 0.25
        emergency_response = total_cost * 0.1
        recovery_costs = total_cost * 0.05
        
        return {
            'total_estimated_cost': round(total_cost, 2),
            'property_damage': round(property_damage, 2),
            'business_interruption': round(business_interruption, 2),
            'emergency_response': round(emergency_response, 2),
            'recovery_costs': round(recovery_costs, 2),
            'base_cost': base_cost,
            'severity_multiplier': severity_mult,
            'population_factor': population_factor,
            'vulnerability_score': vulnerability_score,
            'confidence': 'medium'
        }


class WeatherImpactModel:
    """Main weather impact modeling class"""
    
    def __init__(
        self,
        population_model: Optional[PopulationImpactModel] = None,
        infrastructure_model: Optional[InfrastructureImpactModel] = None,
        economic_model: Optional[EconomicImpactModel] = None
    ):
        self.population_model = population_model or PopulationImpactModel()
        self.infrastructure_model = infrastructure_model or InfrastructureImpactModel()
        self.economic_model = economic_model or EconomicImpactModel()
    
    def calculate_impact(
        self,
        alert: WeatherAlert,
        county_data: Dict[str, Any]
    ) -> ImpactEstimate:
        """Calculate comprehensive impact estimate"""
        total_population = county_data.get('population', 0)
        vulnerability_score = county_data.get('vulnerability_score', 0.5)
        critical_facilities = county_data.get('critical_facilities', [])
        
        population_impact = self.population_model.estimate_population_impact(
            alert, total_population, vulnerability_score
        )
        
        infrastructure_impact = self.infrastructure_model.assess_infrastructure_risk(
            alert, critical_facilities, vulnerability_score
        )
        
        economic_impact = self.economic_model.estimate_economic_impact(
            alert, population_impact['affected_population'], vulnerability_score
        )
        
        assumptions = [
            f"Based on {alert.severity.value} severity level",
            f"County population: {total_population:,}",
            f"Vulnerability score: {vulnerability_score}",
            f"Affected area percentage: {population_impact['affected_area_pct'] * 100}%",
            "Assumes historical event patterns"
        ]
        
        return ImpactEstimate(
            alert_id=alert.id,
            event_type=alert.event,
            severity=alert.severity.value,
            timestamp=datetime.utcnow(),
            population_affected=population_impact['affected_population'],
            critical_facilities_at_risk=infrastructure_impact['at_risk_facilities'],
            infrastructure_risk_score=infrastructure_impact['average_risk_score'],
            economic_impact_usd=economic_impact['total_estimated_cost'],
            confidence_level='medium',
            assumptions=assumptions
        )
    
    def get_impact_summary(self, impact: ImpactEstimate) -> str:
        """Generate human-readable impact summary"""
        lines = [
            f"🌪️  Impact Estimate for {impact.event_type}",
            f"   Severity: {impact.severity}",
            f"   Population Affected: {impact.population_affected:,}" if impact.population_affected else "   Population Affected: Unknown",
            f"   Critical Facilities at Risk: {len(impact.critical_facilities_at_risk)}",
            f"   Infrastructure Risk Score: {impact.infrastructure_risk_score:.2f}",
            f"   Economic Impact: ${impact.economic_impact_usd:,.2f}" if impact.economic_impact_usd else "   Economic Impact: Unknown",
            f"   Confidence: {impact.confidence_level}"
        ]
        return '\n'.join(lines)
