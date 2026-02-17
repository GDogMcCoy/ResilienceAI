"""
ResilienceAI - Intervention Database Module
Comprehensive database of disaster preparedness interventions.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class InterventionCategory(Enum):
    """Intervention categories."""
    HEALTHCARE = "healthcare"
    EMERGENCY = "emergency"
    PREPAREDNESS = "preparedness"
    SOCIAL = "social"
    INFRASTRUCTURE = "infrastructure"
    TECHNOLOGY = "technology"
    EDUCATION = "education"


class RiskType(Enum):
    """Types of risks addressed."""
    FLOOD = "flood"
    HURRICANE = "hurricane"
    EARTHQUAKE = "earthquake"
    WILDFIRE = "wildfire"
    TORNADO = "tornado"
    PANDEMIC = "pandemic"
    CHEMICAL = "chemical"
    CYBER = "cyber"


@dataclass
class InterventionEffectiveness:
    """Effectiveness data for interventions."""
    base_effectiveness: float  # Base risk reduction (0-1)
    effectiveness_std: float   # Standard deviation
    risk_type_weights: Dict[RiskType, float] = field(default_factory=dict)

    def get_weighted_effectiveness(
        self,
        risk_profile: Dict[RiskType, float]
    ) -> float:
        """Calculate effectiveness for given risk profile."""
        weighted = sum(
            self.base_effectiveness * self.risk_type_weights.get(risk, 0) * level
            for risk, level in risk_profile.items()
        )
        return min(1.0, weighted)


@dataclass
class Intervention:
    """Disaster preparedness intervention definition."""

    id: str
    name: str
    description: str
    category: InterventionCategory

    # Cost parameters
    base_cost: float
    cost_components: Dict[str, float] = field(default_factory=dict)

    # Effectiveness
    effectiveness: InterventionEffectiveness = None

    # Implementation
    implementation_years: int = 1
    operational_lifetime: int = 20

    # Benefits
    lives_saved_per_year: float = 0.0
    dalys_averted_per_year: float = 0.0
    hospitalizations_prevented_per_year: float = 0.0
    economic_benefit_per_year: float = 0.0

    # Requirements
    prerequisites: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)

    # Metadata
    evidence_level: str = "medium"  # low, medium, high
    citations: List[str] = field(default_factory=list)


# Comprehensive intervention database
INTERVENTION_DATABASE = {
    # Healthcare Infrastructure
    "hospital_50bed": Intervention(
        id="hospital_50bed",
        name="Build New Hospital (50-bed)",
        description="Construction of a new 50-bed community hospital with emergency services",
        category=InterventionCategory.HEALTHCARE,
        base_cost=50_000_000,
        cost_components={
            "construction": 40_000_000,
            "equipment": 8_000_000,
            "land": 1_000_000,
            "permitting": 500_000,
            "annual_operating": 8_000_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.12,
            effectiveness_std=0.03,
            risk_type_weights={
                RiskType.PANDEMIC: 0.4,
                RiskType.FLOOD: 0.2,
                RiskType.HURRICANE: 0.2,
                RiskType.EARTHQUAKE: 0.2
            }
        ),
        implementation_years=5,
        operational_lifetime=30,
        lives_saved_per_year=5.0,
        dalys_averted_per_year=150.0,
        hospitalizations_prevented_per_year=500.0,
        economic_benefit_per_year=15_000_000,
        evidence_level="high"
    ),

    "hospital_expansion": Intervention(
        id="hospital_expansion",
        name="Expand Existing Hospital",
        description="Add 25 beds and expand emergency department capacity",
        category=InterventionCategory.HEALTHCARE,
        base_cost=25_000_000,
        cost_components={
            "construction": 20_000_000,
            "equipment": 4_000_000,
            "permitting": 300_000,
            "annual_operating": 4_000_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.08,
            effectiveness_std=0.02,
            risk_type_weights={
                RiskType.PANDEMIC: 0.4,
                RiskType.FLOOD: 0.2,
                RiskType.HURRICANE: 0.2,
                RiskType.EARTHQUAKE: 0.2
            }
        ),
        implementation_years=3,
        operational_lifetime=25,
        lives_saved_per_year=3.0,
        dalys_averted_per_year=90.0,
        hospitalizations_prevented_per_year=300.0,
        economic_benefit_per_year=8_000_000,
        evidence_level="high"
    ),

    "ems_station": Intervention(
        id="ems_station",
        name="Build EMS Station",
        description="New emergency medical services station with ambulance bay",
        category=InterventionCategory.EMERGENCY,
        base_cost=2_000_000,
        cost_components={
            "construction": 1_500_000,
            "equipment": 400_000,
            "land": 100_000,
            "annual_operating": 800_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.06,
            effectiveness_std=0.02,
            risk_type_weights={
                RiskType.FLOOD: 0.3,
                RiskType.HURRICANE: 0.3,
                RiskType.EARTHQUAKE: 0.2,
                RiskType.WILDFIRE: 0.2
            }
        ),
        implementation_years=1,
        operational_lifetime=25,
        lives_saved_per_year=2.0,
        dalys_averted_per_year=60.0,
        hospitalizations_prevented_per_year=150.0,
        economic_benefit_per_year=3_000_000,
        evidence_level="high"
    ),

    "fire_station": Intervention(
        id="fire_station",
        name="Build Fire Station",
        description="New fire station with equipment and training facilities",
        category=InterventionCategory.EMERGENCY,
        base_cost=3_000_000,
        cost_components={
            "construction": 2_500_000,
            "equipment": 400_000,
            "land": 100_000,
            "annual_operating": 1_200_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.05,
            effectiveness_std=0.015,
            risk_type_weights={
                RiskType.WILDFIRE: 0.4,
                RiskType.FLOOD: 0.2,
                RiskType.HURRICANE: 0.2,
                RiskType.EARTHQUAKE: 0.2
            }
        ),
        implementation_years=2,
        operational_lifetime=25,
        lives_saved_per_year=1.5,
        dalys_averted_per_year=45.0,
        hospitalizations_prevented_per_year=100.0,
        economic_benefit_per_year=4_000_000,
        evidence_level="high"
    ),

    "telehealth": Intervention(
        id="telehealth",
        name="Deploy Telehealth Infrastructure",
        description="Remote healthcare delivery system with telemedicine capabilities",
        category=InterventionCategory.TECHNOLOGY,
        base_cost=250_000,
        cost_components={
            "equipment": 200_000,
            "installation": 50_000,
            "annual_operating": 100_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.08,
            effectiveness_std=0.025,
            risk_type_weights={
                RiskType.PANDEMIC: 0.5,
                RiskType.FLOOD: 0.2,
                RiskType.HURRICANE: 0.2,
                RiskType.WILDFIRE: 0.1
            }
        ),
        implementation_years=1,
        operational_lifetime=10,
        lives_saved_per_year=1.0,
        dalys_averted_per_year=30.0,
        hospitalizations_prevented_per_year=80.0,
        economic_benefit_per_year=1_500_000,
        evidence_level="medium"
    ),

    "disaster_prep_program": Intervention(
        id="disaster_prep_program",
        name="Community Disaster Preparedness Program",
        description="Education, training, and resource distribution for disaster preparedness",
        category=InterventionCategory.PREPAREDNESS,
        base_cost=500_000,
        cost_components={
            "personnel": 300_000,
            "materials": 150_000,
            "training": 50_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.10,
            effectiveness_std=0.03,
            risk_type_weights={
                RiskType.FLOOD: 0.25,
                RiskType.HURRICANE: 0.25,
                RiskType.EARTHQUAKE: 0.25,
                RiskType.WILDFIRE: 0.25
            }
        ),
        implementation_years=1,
        operational_lifetime=5,
        lives_saved_per_year=2.0,
        dalys_averted_per_year=60.0,
        hospitalizations_prevented_per_year=100.0,
        economic_benefit_per_year=2_000_000,
        evidence_level="medium"
    ),

    "early_warning_system": Intervention(
        id="early_warning_system",
        name="Multi-Hazard Early Warning System",
        description="Integrated early warning system for multiple hazards",
        category=InterventionCategory.TECHNOLOGY,
        base_cost=5_000_000,
        cost_components={
            "equipment": 3_000_000,
            "installation": 1_000_000,
            "software": 500_000,
            "annual_operating": 500_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.15,
            effectiveness_std=0.04,
            risk_type_weights={
                RiskType.FLOOD: 0.3,
                RiskType.HURRICANE: 0.3,
                RiskType.TORNADO: 0.2,
                RiskType.WILDFIRE: 0.2
            }
        ),
        implementation_years=2,
        operational_lifetime=15,
        lives_saved_per_year=4.0,
        dalys_averted_per_year=120.0,
        hospitalizations_prevented_per_year=200.0,
        economic_benefit_per_year=8_000_000,
        evidence_level="high"
    ),

    "emergency_operations_center": Intervention(
        id="emergency_operations_center",
        name="Emergency Operations Center",
        description="Centralized facility for emergency coordination and response",
        category=InterventionCategory.INFRASTRUCTURE,
        base_cost=10_000_000,
        cost_components={
            "construction": 7_000_000,
            "equipment": 2_000_000,
            "technology": 500_000,
            "annual_operating": 1_500_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.12,
            effectiveness_std=0.03,
            risk_type_weights={
                RiskType.FLOOD: 0.25,
                RiskType.HURRICANE: 0.25,
                RiskType.EARTHQUAKE: 0.25,
                RiskType.WILDFIRE: 0.25
            }
        ),
        implementation_years=3,
        operational_lifetime=30,
        lives_saved_per_year=3.0,
        dalys_averted_per_year=90.0,
        hospitalizations_prevented_per_year=150.0,
        economic_benefit_per_year=6_000_000,
        evidence_level="medium"
    ),

    "shelter_upgrade": Intervention(
        id="shelter_upgrade",
        name="Emergency Shelter Upgrade",
        description="Upgrade existing shelters to meet disaster resilience standards",
        category=InterventionCategory.INFRASTRUCTURE,
        base_cost=1_500_000,
        cost_components={
            "construction": 1_200_000,
            "equipment": 200_000,
            "annual_operating": 100_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.07,
            effectiveness_std=0.02,
            risk_type_weights={
                RiskType.HURRICANE: 0.4,
                RiskType.FLOOD: 0.3,
                RiskType.TORNADO: 0.3
            }
        ),
        implementation_years=2,
        operational_lifetime=20,
        lives_saved_per_year=1.5,
        dalys_averted_per_year=45.0,
        hospitalizations_prevented_per_year=50.0,
        economic_benefit_per_year=1_500_000,
        evidence_level="medium"
    ),

    "mutual_aid_agreement": Intervention(
        id="mutual_aid_agreement",
        name="Regional Mutual Aid Agreement",
        description="Formal agreement for resource sharing between jurisdictions",
        category=InterventionCategory.PREPAREDNESS,
        base_cost=100_000,
        cost_components={
            "legal": 50_000,
            "coordination": 30_000,
            "training": 20_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.05,
            effectiveness_std=0.02,
            risk_type_weights={
                RiskType.FLOOD: 0.25,
                RiskType.HURRICANE: 0.25,
                RiskType.EARTHQUAKE: 0.25,
                RiskType.WILDFIRE: 0.25
            }
        ),
        implementation_years=1,
        operational_lifetime=10,
        lives_saved_per_year=1.0,
        dalys_averted_per_year=30.0,
        hospitalizations_prevented_per_year=50.0,
        economic_benefit_per_year=1_000_000,
        evidence_level="low"
    ),

    "poverty_reduction": Intervention(
        id="poverty_reduction",
        name="Economic Development / Poverty Reduction",
        description="Long-term economic development program to reduce vulnerability",
        category=InterventionCategory.SOCIAL,
        base_cost=10_000_000,
        cost_components={
            "programs": 8_000_000,
            "administration": 1_500_000,
            "evaluation": 500_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.15,
            effectiveness_std=0.05,
            risk_type_weights={
                RiskType.FLOOD: 0.2,
                RiskType.HURRICANE: 0.2,
                RiskType.EARTHQUAKE: 0.2,
                RiskType.WILDFIRE: 0.2,
                RiskType.PANDEMIC: 0.2
            }
        ),
        implementation_years=5,
        operational_lifetime=20,
        lives_saved_per_year=3.0,
        dalys_averted_per_year=200.0,
        hospitalizations_prevented_per_year=300.0,
        economic_benefit_per_year=15_000_000,
        evidence_level="medium"
    ),

    "critical_facility_hardening": Intervention(
        id="critical_facility_hardening",
        name="Critical Facility Hardening",
        description="Structural improvements to critical facilities",
        category=InterventionCategory.INFRASTRUCTURE,
        base_cost=8_000_000,
        cost_components={
            "construction": 6_000_000,
            "engineering": 1_500_000,
            "inspection": 500_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.18,
            effectiveness_std=0.04,
            risk_type_weights={
                RiskType.EARTHQUAKE: 0.4,
                RiskType.HURRICANE: 0.3,
                RiskType.FLOOD: 0.3
            }
        ),
        implementation_years=3,
        operational_lifetime=30,
        lives_saved_per_year=2.0,
        dalys_averted_per_year=60.0,
        hospitalizations_prevented_per_year=100.0,
        economic_benefit_per_year=5_000_000,
        evidence_level="high"
    ),

    "mobile_health_unit": Intervention(
        id="mobile_health_unit",
        name="Mobile Health Unit",
        description="Deploy mobile medical unit for emergency response",
        category=InterventionCategory.HEALTHCARE,
        base_cost=750_000,
        cost_components={
            "vehicle": 500_000,
            "equipment": 200_000,
            "annual_operating": 150_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.04,
            effectiveness_std=0.015,
            risk_type_weights={
                RiskType.FLOOD: 0.3,
                RiskType.HURRICANE: 0.3,
                RiskType.WILDFIRE: 0.2,
                RiskType.PANDEMIC: 0.2
            }
        ),
        implementation_years=1,
        operational_lifetime=10,
        lives_saved_per_year=1.0,
        dalys_averted_per_year=30.0,
        hospitalizations_prevented_per_year=80.0,
        economic_benefit_per_year=1_200_000,
        evidence_level="medium"
    ),

    "community_resilience_training": Intervention(
        id="community_resilience_training",
        name="Community Resilience Training Program",
        description="Train community members in disaster response and recovery",
        category=InterventionCategory.EDUCATION,
        base_cost=300_000,
        cost_components={
            "personnel": 200_000,
            "materials": 80_000,
            "facilities": 20_000
        },
        effectiveness=InterventionEffectiveness(
            base_effectiveness=0.06,
            effectiveness_std=0.02,
            risk_type_weights={
                RiskType.FLOOD: 0.25,
                RiskType.HURRICANE: 0.25,
                RiskType.EARTHQUAKE: 0.25,
                RiskType.WILDFIRE: 0.25
            }
        ),
        implementation_years=1,
        operational_lifetime=5,
        lives_saved_per_year=1.0,
        dalys_averted_per_year=30.0,
        hospitalizations_prevented_per_year=50.0,
        economic_benefit_per_year=800_000,
        evidence_level="low"
    )
}


def get_intervention(intervention_id: str) -> Optional[Intervention]:
    """Get intervention by ID."""
    return INTERVENTION_DATABASE.get(intervention_id)


def get_interventions_by_category(
    category: InterventionCategory
) -> List[Intervention]:
    """Get all interventions in a category."""
    return [
        inv for inv in INTERVENTION_DATABASE.values()
        if inv.category == category
    ]


def get_interventions_by_risk_type(
    risk_type: RiskType
) -> List[Intervention]:
    """Get interventions effective against a risk type."""
    return [
        inv for inv in INTERVENTION_DATABASE.values()
        if risk_type in inv.effectiveness.risk_type_weights
    ]


def get_all_interventions() -> List[Intervention]:
    """Get all interventions."""
    return list(INTERVENTION_DATABASE.values())


def search_interventions(
    category: Optional[InterventionCategory] = None,
    max_cost: Optional[float] = None,
    min_effectiveness: Optional[float] = None
) -> List[Intervention]:
    """Search interventions by criteria."""
    results = get_all_interventions()

    if category:
        results = [inv for inv in results if inv.category == category]

    if max_cost:
        results = [inv for inv in results if inv.base_cost <= max_cost]

    if min_effectiveness:
        results = [
            inv for inv in results
            if inv.effectiveness.base_effectiveness >= min_effectiveness
        ]

    return results


if __name__ == "__main__":
    # Example usage
    print("Available Interventions:")
    for inv in get_all_interventions():
        print(f"  {inv.name}: ${inv.base_cost:,.0f} "
              f"(Effectiveness: {inv.effectiveness.base_effectiveness:.1%})")

    print(f"\nTotal interventions: {len(INTERVENTION_DATABASE)}")
