"""
User behavior profiles for realistic load simulation
"""

from dataclasses import dataclass
from typing import List, Dict
import random


@dataclass
class UserProfile:
    """User profile definition for load testing"""
    name: str
    weight: float  # Percentage of total users
    think_time_min: float  # Seconds
    think_time_max: float  # Seconds
    workflows: List[Dict]


# Define user profiles
USER_PROFILES = {
    "api_consumer": UserProfile(
        name="API Consumer",
        weight=0.50,  # 50% of users
        think_time_min=1.0,
        think_time_max=5.0,
        workflows=[
            {"endpoint": "/health", "method": "GET", "probability": 0.3},
            {"endpoint": "/api/v1/predict", "method": "POST", "probability": 0.6},
            {"endpoint": "/api/v1/explain", "method": "POST", "probability": 0.1},
        ]
    ),
    
    "batch_processor": UserProfile(
        name="Batch Processor",
        weight=0.25,  # 25% of users
        think_time_min=10.0,
        think_time_max=30.0,
        workflows=[
            {"endpoint": "/api/v1/batch-predict", "method": "POST", "probability": 0.8},
            {"endpoint": "/api/v1/models", "method": "GET", "probability": 0.2},
        ]
    ),
    
    "model_manager": UserProfile(
        name="Model Manager",
        weight=0.15,  # 15% of users
        think_time_min=5.0,
        think_time_max=15.0,
        workflows=[
            {"endpoint": "/api/v1/models", "method": "GET", "probability": 0.4},
            {"endpoint": "/api/v1/models/{id}", "method": "GET", "probability": 0.3},
            {"endpoint": "/api/v1/models/{id}/deploy", "method": "POST", "probability": 0.2},
            {"endpoint": "/api/v1/metrics", "method": "GET", "probability": 0.1},
        ]
    ),
    
    "streaming_client": UserProfile(
        name="Streaming Client",
        weight=0.10,  # 10% of users
        think_time_min=0.5,
        think_time_max=2.0,
        workflows=[
            {"endpoint": "/api/v1/stream/predict", "method": "WS", "probability": 0.9},
            {"endpoint": "/api/v1/feedback", "method": "POST", "probability": 0.1},
        ]
    ),
}


def get_random_user_profile() -> UserProfile:
    """Select a user profile based on weights"""
    profiles = list(USER_PROFILES.values())
    weights = [p.weight for p in profiles]
    return random.choices(profiles, weights=weights, k=1)[0]


def get_think_time(profile: UserProfile) -> float:
    """Generate random think time for a profile"""
    return random.uniform(profile.think_time_min, profile.think_time_max)


def select_workflow(profile: UserProfile) -> Dict:
    """Select a workflow based on probabilities"""
    workflows = profile.workflows
    probabilities = [w["probability"] for w in workflows]
    return random.choices(workflows, weights=probabilities, k=1)[0]
