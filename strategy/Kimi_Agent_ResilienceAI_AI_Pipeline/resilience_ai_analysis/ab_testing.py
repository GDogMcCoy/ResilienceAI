"""
A/B Testing Framework for ResilienceAI
Manages experiments for recommendation algorithm evaluation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json


class ExperimentStatus(Enum):
    """Experiment status enum"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ExperimentVariant:
    """Experiment variant definition"""
    variant_id: str
    name: str
    config: Dict[str, Any]
    traffic_percentage: float
    recommender: Any = None


@dataclass
class Experiment:
    """A/B test experiment definition"""
    experiment_id: str
    name: str
    description: str
    hypothesis: str
    variants: List[ExperimentVariant]
    metrics: List[str]
    start_date: datetime
    end_date: Optional[datetime] = None
    status: ExperimentStatus = ExperimentStatus.DRAFT
    min_sample_size: int = 1000
    created_at: datetime = field(default_factory=datetime.now)


class ABTestFramework:
    """Framework for managing A/B tests"""
    
    def __init__(self, storage_backend: str = 'memory'):
        self.storage_backend = storage_backend
        self.experiments: Dict[str, Experiment] = {}
        self.assignments: Dict[str, str] = {}  # user_id -> variant_id
        self.events: List[Dict[str, Any]] = []
    
    def create_experiment(
        self,
        name: str,
        description: str,
        hypothesis: str,
        variants: List[ExperimentVariant],
        metrics: List[str],
        duration_days: int = 30,
        min_sample_size: int = 1000
    ) -> str:
        """Create a new A/B test experiment"""
        
        experiment_id = self._generate_id(name)
        
        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            hypothesis=hypothesis,
            variants=variants,
            metrics=metrics,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            min_sample_size=min_sample_size
        )
        
        self.experiments[experiment_id] = experiment
        
        return experiment_id
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start an experiment"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.RUNNING
        experiment.start_date = datetime.now()
        
        return True
    
    def pause_experiment(self, experiment_id: str) -> bool:
        """Pause an experiment"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        self.experiments[experiment_id].status = ExperimentStatus.PAUSED
        return True
    
    def complete_experiment(self, experiment_id: str) -> bool:
        """Complete an experiment"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        self.experiments[experiment_id].status = ExperimentStatus.COMPLETED
        return True
    
    def assign_variant(
        self,
        experiment_id: str,
        user_id: str
    ) -> str:
        """Assign a user to a variant"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment = self.experiments[experiment_id]
        
        # Check if user already assigned
        assignment_key = f"{experiment_id}:{user_id}"
        if assignment_key in self.assignments:
            return self.assignments[assignment_key]
        
        # Return control variant if experiment not running
        if experiment.status != ExperimentStatus.RUNNING:
            return experiment.variants[0].variant_id
        
        # Deterministic assignment based on hash
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Assign based on traffic percentages
        cumulative = 0
        for variant in experiment.variants:
            cumulative += variant.traffic_percentage
            if hash_value % 10000 < cumulative * 100:
                self.assignments[assignment_key] = variant.variant_id
                return variant.variant_id
        
        # Default to last variant
        return experiment.variants[-1].variant_id
    
    def get_recommender(
        self,
        experiment_id: str,
        user_id: str
    ) -> Any:
        """Get the recommender for a user's assigned variant"""
        
        variant_id = self.assign_variant(experiment_id, user_id)
        experiment = self.experiments[experiment_id]
        
        for variant in experiment.variants:
            if variant.variant_id == variant_id:
                return variant.recommender
        
        return None
    
    def track_event(
        self,
        experiment_id: str,
        user_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """Track an experiment event"""
        
        variant_id = self.assign_variant(experiment_id, user_id)
        
        event = {
            'timestamp': datetime.now(),
            'experiment_id': experiment_id,
            'variant_id': variant_id,
            'user_id': user_id,
            'event_type': event_type,
            'event_data': event_data
        }
        
        self.events.append(event)
    
    def get_results(
        self,
        experiment_id: str
    ) -> Dict[str, Any]:
        """Get experiment results"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment = self.experiments[experiment_id]
        
        # Filter events for this experiment
        experiment_events = [e for e in self.events 
                           if e['experiment_id'] == experiment_id]
        
        # Calculate metrics per variant
        variant_results = {}
        
        for variant in experiment.variants:
            variant_events = [e for e in experiment_events 
                            if e['variant_id'] == variant.variant_id]
            
            variant_results[variant.variant_id] = {
                'variant_name': variant.name,
                'sample_size': len(set(e['user_id'] for e in variant_events)),
                'metrics': self._calculate_metrics(variant_events, experiment.metrics)
            }
        
        # Perform statistical tests
        statistical_tests = self._perform_statistical_tests(variant_results)
        
        return {
            'experiment_id': experiment_id,
            'experiment_name': experiment.name,
            'hypothesis': experiment.hypothesis,
            'status': experiment.status.value,
            'start_date': experiment.start_date,
            'end_date': experiment.end_date,
            'variant_results': variant_results,
            'statistical_tests': statistical_tests,
            'recommendation': self._generate_recommendation(variant_results, statistical_tests)
        }
    
    def _calculate_metrics(
        self,
        events: List[Dict[str, Any]],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Calculate metrics from events"""
        
        results = {}
        
        # Group by user
        user_events = {}
        for event in events:
            user_id = event['user_id']
            if user_id not in user_events:
                user_events[user_id] = []
            user_events[user_id].append(event)
        
        # Calculate click-through rate
        if 'ctr' in metrics:
            clicks = sum(1 for e in events if e['event_type'] == 'click')
            impressions = sum(1 for e in events if e['event_type'] == 'impression')
            results['ctr'] = clicks / impressions if impressions > 0 else 0
        
        # Calculate conversion rate
        if 'conversion_rate' in metrics:
            conversions = sum(1 for e in events if e['event_type'] == 'conversion')
            unique_users = len(user_events)
            results['conversion_rate'] = conversions / unique_users if unique_users > 0 else 0
        
        # Calculate average engagement time
        if 'avg_engagement' in metrics:
            engagement_times = [e['event_data'].get('engagement_time', 0) 
                              for e in events if e['event_type'] == 'engagement']
            results['avg_engagement'] = np.mean(engagement_times) if engagement_times else 0
        
        # Calculate recommendation acceptance rate
        if 'acceptance_rate' in metrics:
            accepted = sum(1 for e in events if e['event_type'] == 'intervention_accepted')
            recommended = sum(1 for e in events if e['event_type'] == 'intervention_recommended')
            results['acceptance_rate'] = accepted / recommended if recommended > 0 else 0
        
        # Calculate outcome score
        if 'avg_outcome' in metrics:
            outcomes = [e['event_data'].get('outcome_score', 0) 
                       for e in events if 'outcome_score' in e['event_data']]
            results['avg_outcome'] = np.mean(outcomes) if outcomes else 0
        
        return results
    
    def _perform_statistical_tests(
        self,
        variant_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform statistical significance tests"""
        
        if len(variant_results) < 2:
            return {'error': 'Need at least 2 variants for comparison'}
        
        # Get control variant (first one)
        control_id = list(variant_results.keys())[0]
        control = variant_results[control_id]
        
        tests = {}
        
        for variant_id, variant in variant_results.items():
            if variant_id == control_id:
                continue
            
            tests[variant_id] = {}
            
            for metric in control['metrics'].keys():
                control_value = control['metrics'][metric]
                variant_value = variant['metrics'][metric]
                
                # Calculate lift
                lift = (variant_value - control_value) / control_value \
                       if control_value != 0 else 0
                
                # Simple significance test (would use proper statistical test in production)
                significant = abs(lift) > 0.05  # 5% threshold
                
                tests[variant_id][metric] = {
                    'control_value': control_value,
                    'variant_value': variant_value,
                    'lift': lift,
                    'significant': significant,
                    'p_value': 0.05  # Placeholder
                }
        
        return tests
    
    def _generate_recommendation(
        self,
        variant_results: Dict[str, Any],
        statistical_tests: Dict[str, Any]
    ) -> str:
        """Generate recommendation based on results"""
        
        # Find best performing variant
        best_variant = None
        best_score = -float('inf')
        
        for variant_id, tests in statistical_tests.items():
            if not tests:
                continue
            
            # Calculate average lift across metrics
            avg_lift = np.mean([t['lift'] for t in tests.values()])
            
            if avg_lift > best_score:
                best_score = avg_lift
                best_variant = variant_id
        
        if best_variant and best_score > 0:
            variant_name = variant_results[best_variant]['variant_name']
            return f"Recommend rolling out variant '{variant_name}' with {best_score:.1%} lift"
        else:
            return "No significant improvement detected; recommend keeping control"
    
    def _generate_id(self, name: str) -> str:
        """Generate unique experiment ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_part = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"exp_{timestamp}_{hash_part}"


class ExperimentTemplate:
    """Pre-defined experiment templates"""
    
    @staticmethod
    def create_recommender_comparison(
        framework: ABTestFramework,
        name: str,
        recommenders: Dict[str, Any],
        traffic_split: List[float] = None
    ) -> str:
        """Create experiment comparing different recommenders"""
        
        if traffic_split is None:
            traffic_split = [1.0 / len(recommenders)] * len(recommenders)
        
        variants = []
        for (rec_name, recommender), traffic in zip(recommenders.items(), traffic_split):
            variant = ExperimentVariant(
                variant_id=f"variant_{rec_name}",
                name=rec_name,
                config={'recommender_type': rec_name},
                traffic_percentage=traffic,
                recommender=recommender
            )
            variants.append(variant)
        
        return framework.create_experiment(
            name=name,
            description=f"Compare {len(recommenders)} recommendation algorithms",
            hypothesis="Different recommendation algorithms will yield different engagement rates",
            variants=variants,
            metrics=['ctr', 'conversion_rate', 'acceptance_rate', 'avg_outcome'],
            duration_days=30
        )
    
    @staticmethod
    def create_ranking_comparison(
        framework: ABTestFramework,
        name: str,
        ranking_methods: List[str]
    ) -> str:
        """Create experiment comparing ranking methods"""
        
        variants = []
        for method in ranking_methods:
            variant = ExperimentVariant(
                variant_id=f"variant_{method}",
                name=method,
                config={'ranking_method': method},
                traffic_percentage=1.0 / len(ranking_methods)
            )
            variants.append(variant)
        
        return framework.create_experiment(
            name=name,
            description=f"Compare {len(ranking_methods)} ranking methods",
            hypothesis="Different ranking methods will affect user engagement",
            variants=variants,
            metrics=['ctr', 'avg_engagement', 'conversion_rate'],
            duration_days=21
        )


# Example usage
if __name__ == "__main__":
    # Create A/B test framework
    framework = ABTestFramework()
    
    # Create experiment variants
    variants = [
        ExperimentVariant(
            variant_id="control",
            name="Control (SVD)",
            config={'model_type': 'svd'},
            traffic_percentage=0.5
        ),
        ExperimentVariant(
            variant_id="treatment",
            name="Treatment (Neural MF)",
            config={'model_type': 'neural_mf'},
            traffic_percentage=0.5
        )
    ]
    
    # Create experiment
    experiment_id = framework.create_experiment(
        name="Collaborative Filtering Comparison",
        description="Compare SVD vs Neural Matrix Factorization",
        hypothesis="Neural MF will have higher engagement than SVD",
        variants=variants,
        metrics=['ctr', 'acceptance_rate', 'avg_outcome'],
        duration_days=30
    )
    
    print(f"Created experiment: {experiment_id}")
    
    # Start experiment
    framework.start_experiment(experiment_id)
    
    # Simulate user assignments
    for i in range(10):
        user_id = f"user_{i}"
        variant = framework.assign_variant(experiment_id, user_id)
        print(f"User {user_id} assigned to {variant}")
    
    # Simulate events
    framework.track_event(experiment_id, "user_0", "impression", {})
    framework.track_event(experiment_id, "user_0", "click", {})
    framework.track_event(experiment_id, "user_1", "impression", {})
    
    # Get results
    results = framework.get_results(experiment_id)
    print(f"\nExperiment Results:")
    print(f"  Status: {results['status']}")
    print(f"  Recommendation: {results['recommendation']}")
