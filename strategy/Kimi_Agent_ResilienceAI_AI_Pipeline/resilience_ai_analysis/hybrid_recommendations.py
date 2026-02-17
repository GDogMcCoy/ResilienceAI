"""
Hybrid Recommendation System for ResilienceAI
Combines multiple recommendation approaches with learned weights
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import torch
import torch.nn as nn
from datetime import datetime

from recommendation_architecture import BaseRecommender, Recommendation, RecommendationType


class HybridRecommender(BaseRecommender):
    """Hybrid recommender combining multiple approaches"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.recommenders: Dict[str, BaseRecommender] = {}
        self.weights: Dict[str, float] = {}
        self.combination_method = config.get('combination_method', 'weighted')
        self.reranker = None
    
    def add_recommender(
        self,
        name: str,
        recommender: BaseRecommender,
        weight: float = 1.0
    ) -> None:
        """Add a recommender component"""
        self.recommenders[name] = recommender
        self.weights[name] = weight
    
    def fit(self, data: Any) -> None:
        """Train hybrid model"""
        
        # Train all component recommenders
        for name, recommender in self.recommenders.items():
            print(f"Training {name} recommender...")
            recommender.fit(data)
        
        # Learn optimal weights if using learned combination
        if self.combination_method == 'learned':
            self._learn_weights(data)
        
        self.is_trained = True
    
    def _learn_weights(self, validation_data: pd.DataFrame) -> None:
        """Learn optimal weights using validation data"""
        
        # Generate predictions from each recommender
        predictions = defaultdict(list)
        actuals = []
        
        for _, row in validation_data.iterrows():
            query = {'county_id': row['county_id'], 'type': 'interventions'}
            actuals.append(row['outcome_score'])
            
            for name, recommender in self.recommenders.items():
                try:
                    rec = recommender.recommend(query, n_recommendations=1)
                    pred_score = rec.scores[0] if rec.scores else 0.5
                    predictions[name].append(pred_score)
                except:
                    predictions[name].append(0.5)
        
        # Optimize weights to minimize MSE
        from scipy.optimize import minimize
        
        def objective(weights):
            combined = np.zeros(len(actuals))
            for i, (name, preds) in enumerate(predictions.items()):
                combined += weights[i] * np.array(preds)
            mse = np.mean((np.array(actuals) - combined) ** 2)
            return mse
        
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = [(0, 1) for _ in self.recommenders]
        
        result = minimize(
            objective,
            x0=[1/len(self.recommenders)] * len(self.recommenders),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        # Update weights
        for i, name in enumerate(self.recommenders.keys()):
            self.weights[name] = result.x[i]
        
        print(f"Learned weights: {self.weights}")
    
    def recommend(
        self,
        query: Dict[str, Any],
        n_recommendations: int = 10
    ) -> Recommendation:
        """Generate hybrid recommendations"""
        
        if not self.is_trained:
            raise RuntimeError("Model must be trained before generating recommendations")
        
        # Get recommendations from all components
        all_recommendations = {}
        for name, recommender in self.recommenders.items():
            try:
                rec = recommender.recommend(query, n_recommendations=n_recommendations * 2)
                all_recommendations[name] = rec
            except Exception as e:
                print(f"Warning: {name} recommender failed: {e}")
        
        # Combine recommendations
        if self.combination_method == 'weighted':
            return self._weighted_combine(all_recommendations, query, n_recommendations)
        elif self.combination_method == 'switching':
            return self._switching_combine(all_recommendations, query, n_recommendations)
        elif self.combination_method == 'cascade':
            return self._cascade_combine(all_recommendations, query, n_recommendations)
        else:
            return self._weighted_combine(all_recommendations, query, n_recommendations)
    
    def _weighted_combine(
        self,
        all_recommendations: Dict[str, Recommendation],
        query: Dict[str, Any],
        n_recommendations: int
    ) -> Recommendation:
        """Combine recommendations using weighted scores"""
        
        # Aggregate scores for each item
        item_scores = defaultdict(lambda: {'score': 0, 'count': 0, 'sources': []})
        
        for source, rec in all_recommendations.items():
            weight = self.weights.get(source, 1.0)
            
            for item, score in zip(rec.items, rec.scores):
                item_id = item.get('intervention_id') or item.get('county_id') or item.get('item_id')
                item_scores[item_id]['score'] += weight * score
                item_scores[item_id]['count'] += 1
                item_scores[item_id]['sources'].append(source)
        
        # Normalize by count and weight sum
        total_weight = sum(self.weights.values())
        for item_id in item_scores:
            item_scores[item_id]['score'] /= total_weight
        
        # Sort by combined score
        sorted_items = sorted(
            item_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:n_recommendations]
        
        # Build recommendation
        items = []
        scores = []
        for item_id, data in sorted_items:
            items.append({
                'item_id': item_id,
                'combined_score': data['score'],
                'sources': data['sources']
            })
            scores.append(data['score'])
        
        return Recommendation(
            recommendation_id=f"hybrid_{query.get('county_id')}_{datetime.now().timestamp()}",
            type=RecommendationType.HYBRID,
            target_id=query.get('county_id'),
            items=items,
            scores=scores,
            explanations=[],
            confidence=float(np.mean(scores)) if scores else 0,
            timestamp=datetime.now(),
            metadata={
                "method": "weighted_hybrid",
                "weights": self.weights,
                "sources": list(all_recommendations.keys())
            }
        )
    
    def _switching_combine(
        self,
        all_recommendations: Dict[str, Recommendation],
        query: Dict[str, Any],
        n_recommendations: int
    ) -> Recommendation:
        """Switch between recommenders based on context"""
        
        # Determine which recommender to use based on query context
        county_id = query.get('county_id')
        
        # Simple heuristic: use collaborative filtering if we have history,
        # otherwise use content-based
        if 'cf' in all_recommendations:
            selected = all_recommendations['cf']
        elif 'cb' in all_recommendations:
            selected = all_recommendations['cb']
        else:
            selected = list(all_recommendations.values())[0]
        
        # Truncate to requested number
        selected.items = selected.items[:n_recommendations]
        selected.scores = selected.scores[:n_recommendations]
        
        return selected
    
    def _cascade_combine(
        self,
        all_recommendations: Dict[str, Recommendation],
        query: Dict[str, Any],
        n_recommendations: int
    ) -> Recommendation:
        """Cascade recommenders: use one to filter, another to rank"""
        
        # Use content-based for candidate generation
        cb_rec = all_recommendations.get('cb')
        if cb_rec:
            candidates = {item.get('item_id', item.get('county_id')): item 
                         for item in cb_rec.items}
        else:
            candidates = {}
        
        # Use collaborative filtering for ranking
        cf_rec = all_recommendations.get('cf')
        if cf_rec:
            for item, score in zip(cf_rec.items, cf_rec.scores):
                item_id = item.get('item_id', item.get('county_id'))
                if item_id in candidates:
                    candidates[item_id]['cf_score'] = score
        
        # Sort by combined criteria
        sorted_items = sorted(
            candidates.items(),
            key=lambda x: (x[1].get('cf_score', 0) + x[1].get('match_score', 0)) / 2,
            reverse=True
        )[:n_recommendations]
        
        items = [{'item_id': k, **v} for k, v in sorted_items]
        scores = [item.get('cf_score', 0) for item in items]
        
        return Recommendation(
            recommendation_id=f"hybrid_cascade_{query.get('county_id')}_{datetime.now().timestamp()}",
            type=RecommendationType.HYBRID,
            target_id=query.get('county_id'),
            items=items,
            scores=scores,
            explanations=[],
            confidence=float(np.mean(scores)) if scores else 0,
            timestamp=datetime.now(),
            metadata={"method": "cascade_hybrid"}
        )
    
    def explain(self, recommendation: Recommendation) -> List[str]:
        """Generate explanations for hybrid recommendations"""
        
        explanations = []
        sources = recommendation.metadata.get('sources', [])
        
        explanations.append(
            f"This recommendation combines insights from {len(sources)} approaches: "
            f"{', '.join(sources)}"
        )
        
        for item in recommendation.items[:3]:
            item_sources = item.get('sources', [])
            score = item.get('combined_score', 0)
            explanations.append(
                f"Item {item.get('item_id')} has combined score {score:.3f} "
                f"based on {len(item_sources)} recommendation sources"
            )
        
        return explanations


class NeuralHybridModel(nn.Module):
    """Neural network for learning hybrid recommendation combinations"""
    
    def __init__(
        self,
        n_recommenders: int,
        hidden_dim: int = 64,
        dropout: float = 0.2
    ):
        super().__init__()
        
        self.fc1 = nn.Linear(n_recommenders, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, 1)
        
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.sigmoid(self.fc3(x))
        return x


# Example usage
if __name__ == "__main__":
    from collaborative_filtering import CollaborativeFilteringRecommender
    
    # Create sample data
    interactions = pd.DataFrame({
        'county_id': ['c1', 'c1', 'c2', 'c2', 'c3', 'c3'],
        'intervention_id': ['i1', 'i2', 'i1', 'i3', 'i2', 'i4'],
        'outcome_score': [0.8, 0.6, 0.9, 0.7, 0.75, 0.85]
    })
    
    # Create hybrid recommender
    hybrid = HybridRecommender({'combination_method': 'weighted'})
    
    # Add collaborative filtering recommender
    cf_config = {'model_type': 'svd', 'n_factors': 2}
    cf_recommender = CollaborativeFilteringRecommender(cf_config)
    
    hybrid.add_recommender('cf', cf_recommender, weight=0.6)
    
    # Train hybrid model
    hybrid.fit(interactions)
    
    # Generate recommendations
    query = {'county_id': 'c1'}
    recommendations = hybrid.recommend(query, n_recommendations=3)
    
    print(f"Hybrid Recommendations for c1:")
    for item, score in zip(recommendations.items, recommendations.scores):
        print(f"  - {item['item_id']}: {score:.3f}")
        print(f"    Sources: {item.get('sources', [])}")
