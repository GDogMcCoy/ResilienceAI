"""
ResilienceAI Stakeholder Engagement
====================================
Stakeholder engagement framework for ethical AI.
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json


class StakeholderType(Enum):
    INTERNAL_TEAM = "internal_team"
    END_USERS = "end_users"
    AFFECTED_COMMUNITIES = "affected_communities"
    REGULATORS = "regulators"
    INDUSTRY_PEERS = "industry_peers"
    ACADEMIA = "academia"
    CIVIL_SOCIETY = "civil_society"


class EngagementMethod(Enum):
    SURVEY = "survey"
    INTERVIEW = "interview"
    FOCUS_GROUP = "focus_group"
    WORKSHOP = "workshop"
    PUBLIC_CONSULTATION = "public_consultation"
    ADVISORY_BOARD = "advisory_board"


@dataclass
class Stakeholder:
    id: str
    name: str
    type: StakeholderType
    contact_info: str
    influence_level: str
    interest_level: str
    concerns: List[str]
    engagement_history: List[Dict]


@dataclass
class EngagementActivity:
    id: str
    name: str
    method: EngagementMethod
    stakeholders: List[str]
    objectives: List[str]
    outcomes: List[str]
    feedback: List[str]
    date: str
    facilitator: str


class StakeholderEngagement:
    """Main stakeholder engagement class."""
    
    def __init__(self):
        self.stakeholders: Dict[str, Stakeholder] = {}
        self.activities: List[EngagementActivity] = []
    
    def register_stakeholder(self, stakeholder: Stakeholder):
        self.stakeholders[stakeholder.id] = stakeholder
    
    def plan_engagement(self, activity_name: str, method: EngagementMethod,
                        stakeholder_types: List[StakeholderType], objectives: List[str]) -> EngagementActivity:
        selected = [s.id for s in self.stakeholders.values() if s.type in stakeholder_types]
        return EngagementActivity(
            id=f"activity_{len(self.activities)+1}", name=activity_name, method=method,
            stakeholders=selected, objectives=objectives, outcomes=[], feedback=[],
            date=datetime.now().isoformat(), facilitator="TBD"
        )
    
    def conduct_engagement(self, activity: EngagementActivity, facilitator: str) -> EngagementActivity:
        activity.facilitator = facilitator
        self.activities.append(activity)
        for stakeholder_id in activity.stakeholders:
            if stakeholder_id in self.stakeholders:
                self.stakeholders[stakeholder_id].engagement_history.append({
                    "activity_id": activity.id, "date": activity.date, "method": activity.method.value
                })
        return activity
    
    def get_stakeholder_map(self) -> Dict:
        map_data = {"high_high": [], "high_low": [], "low_high": [], "low_low": []}
        for stakeholder in self.stakeholders.values():
            key = f"{stakeholder.influence_level[0]}_{stakeholder.interest_level[0]}"
            map_data[key].append({"id": stakeholder.id, "name": stakeholder.name})
        return map_data
    
    def generate_engagement_report(self) -> str:
        report = {
            "report_date": datetime.now().isoformat(),
            "stakeholder_summary": {"total": len(self.stakeholders)},
            "activities": len(self.activities)
        }
        return json.dumps(report, indent=2)


if __name__ == "__main__":
    engagement = StakeholderEngagement()
    
    stakeholders = [
        Stakeholder("s1", "Emergency Response Team", StakeholderType.END_USERS,
                   "emergency@resilienceai.org", "high", "high", ["Accuracy"], []),
        Stakeholder("s2", "Community Reps", StakeholderType.AFFECTED_COMMUNITIES,
                   "community@resilienceai.org", "medium", "high", ["Fairness"], [])
    ]
    
    for s in stakeholders:
        engagement.register_stakeholder(s)
    
    activity = engagement.plan_engagement("Fairness Workshop", EngagementMethod.WORKSHOP,
                                          [StakeholderType.END_USERS], ["Gather feedback"])
    print(f"Planned: {activity.name}")
    print(engagement.generate_engagement_report())
