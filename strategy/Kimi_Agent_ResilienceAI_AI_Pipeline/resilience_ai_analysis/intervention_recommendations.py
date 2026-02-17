"""
Intervention Recommendation System
Suggests interventions based on county profile, risk factors, and historical outcomes
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from datetime import datetime

from recommendation_architecture import BaseRecommender, Recommendation, RecommendationType


class InterventionCategory(Enum):
    """Intervention categories"""
    INFRASTRUCTURE = "infrastructure"
    EMERGENCY_PREPAREDNESS = "emergency_preparedness"
    COMMUNITY_ENGAGEMENT = "community_engagement"
    ECONOMIC_RESILIENCE = "economic_resilience"
    ENVIRONMENTAL = "environmental"
    HEALTHCARE = "healthcare"


@dataclass
class InterventionOutcome:
    """Historical outcome data for an intervention"""
    intervention_id: str
    county_id: str
    implementation_date: str
    outcome_score: float
    cost: float
    duration_days: int
    success: bool
    lessons_learned: List[str]


class InterventionRecommender(BaseRecommender):
    """Recommender for suggesting interventions"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.interventions: Optional[pd.DataFrame] = None
        self.outcomes: Optional[pd.DataFrame] = None
        self.county_profiles: Optional[pd.DataFrame] = None
        self.effectiveness_model = None
        self.risk_intervention_mapping: Dict[str, List[str]] = {}
    
    def fit(
        self,
        interventions: pd.DataFrame,
        outcomes: pd.DataFrame,
        county_profiles: pd.DataFrame
    ) -> None:
        """Train intervention recommender"""
        
        self.interventions = interventions.copy()
        self.outcomes = outcomes.copy()
        self.county_profiles = county_profiles.copy()
        
        # Build risk-intervention mapping
        self._build_risk_intervention_mapping()
        
        # Train effectiveness prediction model
        self._train_effectiveness_model()
        
        self.is_trained = True
    
    def _build_risk_intervention_mapping(self) -> None:
        """Build mapping from risk types to effective interventions"""
        
        # Merge outcomes with interventions
        merged = self.outcomes.merge(
            self.interventions,
            on='intervention_id',
            how='left'
        )
        
        # For each intervention, find which risks it addresses effectively
        for intervention_id in self.interventions['intervention_id'].unique():
            intervention_outcomes = merged[merged['intervention_id'] == intervention_id]
            
            if len(intervention_outcomes) > 0:
                avg_outcome = intervention_outcomes['outcome_score'].mean()
                
                if avg_outcome > 0.6:  # Threshold for effectiveness
                    target_risks = self.interventions[
                        self.interventions['intervention_id'] == intervention_id
                    ]['target_risks'].iloc[0]
                    
                    if isinstance(target_risks, list):
                        for risk in target_risks:
                            if risk not in self.risk_intervention_mapping:
                                self.risk_intervention_mapping[risk] = []
                            self.risk_intervention_mapping[risk].append(intervention_id)
    
    def _train_effectiveness_model(self) -> None:
        """Train model to predict intervention effectiveness"""
        
        # Prepare training data
        training_data = self._prepare_training_data()
        
        # Train gradient boosting model
        feature_cols = [c for c in training_data.columns 
                       if c not in ['outcome_score', 'county_id', 'intervention_id']]
        
        X = training_data[feature_cols].fillna(0)
        y = training_data['outcome_score']
        
        self.effectiveness_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.effectiveness_model.fit(X, y)
        
        self.feature_columns = feature_cols
    
    def _prepare_training_data(self) -> pd.DataFrame:
        """Prepare training data for effectiveness model"""
        
        # Merge outcomes with county profiles and intervention features
        data = self.outcomes.merge(
            self.county_profiles,
            on='county_id',
            how='left'
        ).merge(
            self.interventions,
            on='intervention_id',
            how='left'
        )
        
        # Feature engineering
        risk_cols = [c for c in data.columns if c.startswith('risk_')]
        for risk_col in risk_cols:
            data[f'{risk_col}_match'] = data.apply(
                lambda row: 1 if risk_col.replace('risk_', '') in 
                (row.get('target_risks', []) or []) else 0,
                axis=1
            )
        
        return data
    
    def recommend(
        self,
        query: Dict[str, Any],
        n_recommendations: int = 10
    ) -> Recommendation:
        """Generate intervention recommendations"""
        
        if not self.is_trained:
            raise RuntimeError("Model must be trained before generating recommendations")
        
        county_id = query.get('county_id')
        budget = query.get('budget')
        time_horizon = query.get('time_horizon')
        priority_risks = query.get('priority_risks', [])
        excluded_interventions = query.get('excluded_interventions', [])
        
        # Get county profile
        county_profile = self.county_profiles[
            self.county_profiles['county_id'] == county_id
        ]
        
        if len(county_profile) == 0:
            raise ValueError(f"Unknown county: {county_id}")
        
        county_profile = county_profile.iloc[0]
        
        # Score all interventions
        scored_interventions = self._score_interventions(
            county_profile,
            budget,
            time_horizon,
            priority_risks,
            excluded_interventions
        )
        
        # Sort and select top recommendations
        scored_interventions.sort(key=lambda x: x['score'], reverse=True)
        top_interventions = scored_interventions[:n_recommendations]
        
        # Build recommendation
        items = []
        scores = []
        
        for intervention in top_interventions:
            intervention_details = self._get_intervention_details(
                intervention['intervention_id']
            )
            intervention_details['predicted_effectiveness'] = intervention['score']
            intervention_details['match_reasons'] = intervention['match_reasons']
            
            items.append(intervention_details)
            scores.append(intervention['score'])
        
        return Recommendation(
            recommendation_id=f"interventions_{county_id}_{datetime.now().timestamp()}",
            type=RecommendationType.INTERVENTIONS,
            target_id=county_id,
            items=items,
            scores=scores,
            explanations=[],
            confidence=float(np.mean(scores)) if scores else 0,
            timestamp=datetime.now(),
            metadata={
                "priority_risks": priority_risks,
                "budget_constraint": budget,
                "time_horizon": time_horizon
            }
        )
    
    def _score_interventions(
        self,
        county_profile: pd.Series,
        budget: Optional[float],
        time_horizon: Optional[int],
        priority_risks: List[str],
        excluded_interventions: List[str]
    ) -> List[Dict[str, Any]]:
        """Score interventions for a county"""
        
        scored = []
        
        for _, intervention in self.interventions.iterrows():
            intervention_id = intervention['intervention_id']
            
            # Skip excluded interventions
            if intervention_id in excluded_interventions:
                continue
            
            # Check budget constraint
            if budget is not None:
                cost = intervention.get('cost', 0)
                if cost > budget:
                    continue
            
            # Check time horizon
            if time_horizon is not None:
                duration = intervention.get('duration', 0)
                if duration > time_horizon:
                    continue
            
            # Calculate score components
            match_reasons = []
            
            # 1. Predicted effectiveness
            effectiveness = self._predict_effectiveness(county_profile, intervention)
            
            # 2. Risk match score
            risk_score, risk_matches = self._calculate_risk_match(
                county_profile, intervention, priority_risks
            )
            match_reasons.extend(risk_matches)
            
            # 3. Historical success rate
            historical_score = self._get_historical_success(intervention_id)
            
            # 4. Cost-effectiveness
            cost_effectiveness = self._calculate_cost_effectiveness(
                intervention, effectiveness
            )
            
            # Combine scores
            combined_score = (
                0.4 * effectiveness +
                0.3 * risk_score +
                0.2 * historical_score +
                0.1 * cost_effectiveness
            )
            
            scored.append({
                'intervention_id': intervention_id,
                'score': combined_score,
                'effectiveness': effectiveness,
                'risk_score': risk_score,
                'historical_score': historical_score,
                'cost_effectiveness': cost_effectiveness,
                'match_reasons': match_reasons
            })
        
        return scored
    
    def _predict_effectiveness(
        self,
        county_profile: pd.Series,
        intervention: pd.Series
    ) -> float:
        """Predict intervention effectiveness for a county"""
        
        # Build feature vector
        features = []
        
        for col in self.feature_columns:
            if col in county_profile.index:
                features.append(county_profile[col])
            elif col in intervention.index:
                features.append(intervention[col])
            else:
                features.append(0)
        
        # Predict
        prediction = self.effectiveness_model.predict([features])[0]
        return float(np.clip(prediction, 0, 1))
    
    def _calculate_risk_match(
        self,
        county_profile: pd.Series,
        intervention: pd.Series,
        priority_risks: List[str]
    ) -> Tuple[float, List[str]]:
        """Calculate risk match score"""
        
        target_risks = intervention.get('target_risks', [])
        if not isinstance(target_risks, list):
            target_risks = []
        
        match_reasons = []
        matches = 0
        
        for risk in target_risks:
            risk_col = f'risk_{risk}'
            
            if risk_col in county_profile.index:
                risk_level = county_profile[risk_col]
                
                if risk in priority_risks:
                    matches += risk_level * 1.5
                    match_reasons.append(f"Addresses priority risk: {risk}")
                elif risk_level > 0.5:
                    matches += risk_level
                    match_reasons.append(f"Addresses significant risk: {risk}")
        
        score = min(matches / max(len(target_risks), 1), 1.0)
        return score, match_reasons
    
    def _get_historical_success(self, intervention_id: str) -> float:
        """Get historical success rate for an intervention"""
        
        intervention_outcomes = self.outcomes[
            self.outcomes['intervention_id'] == intervention_id
        ]
        
        if len(intervention_outcomes) == 0:
            return 0.5
        
        success_rate = intervention_outcomes['success'].mean()
        avg_outcome = intervention_outcomes['outcome_score'].mean()
        
        return (success_rate + avg_outcome) / 2
    
    def _calculate_cost_effectiveness(
        self,
        intervention: pd.Series,
        predicted_effectiveness: float
    ) -> float:
        """Calculate cost-effectiveness score"""
        
        cost = intervention.get('cost', 1)
        if cost == 0:
            cost = 1
        
        return predicted_effectiveness / np.log1p(cost)
    
    def _get_intervention_details(self, intervention_id: str) -> Dict[str, Any]:
        """Get detailed intervention information"""
        
        intervention = self.interventions[
            self.interventions['intervention_id'] == intervention_id
        ].iloc[0]
        
        return {
            'intervention_id': intervention_id,
            'name': intervention.get('name', ''),
            'category': intervention.get('category', ''),
            'description': intervention.get('description', ''),
            'cost': float(intervention.get('cost', 0)),
            'duration': int(intervention.get('duration', 0)),
            'target_risks': intervention.get('target_risks', []),
            'implementation_complexity': intervention.get('implementation_complexity', 'medium'),
            'required_resources': intervention.get('required_resources', {}),
            'success_rate': self._get_historical_success(intervention_id)
        }
    
    def explain(self, recommendation: Recommendation) -> List[str]:
        """Generate explanations for intervention recommendations"""
        
        explanations = []
        county_id = recommendation.target_id
        priority_risks = recommendation.metadata.get('priority_risks', [])
        
        explanations.append(
            f"These interventions were selected based on predicted effectiveness "
            f"for county {county_id}"
        )
        
        if priority_risks:
            explanations.append(
                f"Priority focus on: {', '.join(priority_risks)}"
            )
        
        for item in recommendation.items[:3]:
            name = item.get('name', item.get('intervention_id'))
            effectiveness = item.get('predicted_effectiveness', 0)
            match_reasons = item.get('match_reasons', [])
            
            explanations.append(
                f"{name}: Predicted effectiveness {effectiveness:.3f}"
            )
            
            if match_reasons:
                explanations.append(f"  - {match_reasons[0]}")
        
        return explanations
    
    def get_intervention_sequence(
        self,
        county_id: str,
        n_interventions: int = 5,
        budget: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get optimal sequence of interventions"""
        
        sequence = []
        remaining_budget = budget
        excluded = []
        
        for i in range(n_interventions):
            query = {
                'county_id': county_id,
                'budget': remaining_budget,
                'excluded_interventions': excluded
            }
            
            rec = self.recommend(query, n_recommendations=1)
            
            if not rec.items:
                break
            
            intervention = rec.items[0]
            sequence.append({
                'order': i + 1,
                **intervention
            })
            
            excluded.append(intervention['intervention_id'])
            
            if remaining_budget is not None:
                remaining_budget -= intervention.get('cost', 0)
                if remaining_budget <= 0:
                    break
        
        return sequence


# Example usage
if __name__ == "__main__":
    # Create sample data
    interventions = pd.DataFrame({
        'intervention_id': ['int_1', 'int_2', 'int_3', 'int_4'],
        'name': ['Flood Barrier', 'Early Warning System', 'Community Training', 'Economic Diversification'],
        'category': ['infrastructure', 'emergency_preparedness', 'community_engagement', 'economic_resilience'],
        'cost': [500000, 200000, 50000, 150000],
        'duration': [180, 90, 30, 120],
        'target_risks': [['flood'], ['flood', 'storm'], ['all'], ['economic']]
    })
    
    outcomes = pd.DataFrame({
        'intervention_id': ['int_1', 'int_1', 'int_2', 'int_3', 'int_4'],
        'county_id': ['county_1', 'county_2', 'county_1', 'county_2', 'county_1'],
        'outcome_score': [0.85, 0.80, 0.75, 0.90, 0.70],
        'success': [True, True, True, True, True]
    })
    
    county_profiles = pd.DataFrame({
        'county_id': ['county_1', 'county_2'],
        'population': [100000, 150000],
        'risk_flood': [0.8, 0.6],
        'risk_storm': [0.5, 0.4],
        'median_income': [50000, 60000]
    })
    
    # Initialize and train recommender
    config = {}
    recommender = InterventionRecommender(config)
    recommender.fit(interventions, outcomes, county_profiles)
    
    # Generate recommendations
    query = {
        'county_id': 'county_1',
        'budget': 400000,
        'priority_risks': ['flood']
    }
    
    recommendations = recommender.recommend(query, n_recommendations=3)
    
    print(f"Recommended interventions for county_1:")
    for item, score in zip(recommendations.items, recommendations.scores):
        print(f"  - {item['name']}: {score:.3f}")
        if item.get('match_reasons'):
            print(f"    Reason: {item['match_reasons'][0]}")
