"""
Collaborative Filtering for ResilienceAI
Implements user-based and item-based collaborative filtering
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict, Tuple, Optional
import torch
import torch.nn as nn
from dataclasses import dataclass
from datetime import datetime

from recommendation_architecture import BaseRecommender, Recommendation, RecommendationType


@dataclass
class InteractionMatrix:
    """User-item interaction data structure"""
    user_ids: List[str]
    item_ids: List[str]
    matrix: csr_matrix
    user_mapping: Dict[str, int]
    item_mapping: Dict[str, int]


class MatrixFactorization(nn.Module):
    """Neural Matrix Factorization for collaborative filtering"""
    
    def __init__(
        self,
        n_users: int,
        n_items: int,
        n_factors: int = 50,
        dropout: float = 0.2
    ):
        super().__init__()
        self.user_embeddings = nn.Embedding(n_users, n_factors)
        self.item_embeddings = nn.Embedding(n_items, n_factors)
        self.user_bias = nn.Embedding(n_users, 1)
        self.item_bias = nn.Embedding(n_items, 1)
        self.global_bias = nn.Parameter(torch.zeros(1))
        
        self.dropout = nn.Dropout(dropout)
        self.sigmoid = nn.Sigmoid()
        
        # Initialize weights
        nn.init.normal_(self.user_embeddings.weight, std=0.01)
        nn.init.normal_(self.item_embeddings.weight, std=0.01)
    
    def forward(self, user_ids: torch.Tensor, item_ids: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        user_emb = self.dropout(self.user_embeddings(user_ids))
        item_emb = self.dropout(self.item_embeddings(item_ids))
        
        # Dot product + biases
        interaction = (user_emb * item_emb).sum(dim=1, keepdim=True)
        interaction += self.user_bias(user_ids) + self.item_bias(item_ids) + self.global_bias
        
        return self.sigmoid(interaction)


class CollaborativeFilteringRecommender(BaseRecommender):
    """Collaborative filtering recommender for counties and interventions"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_type = config.get('model_type', 'svd')
        self.n_factors = config.get('n_factors', 50)
        self.n_neighbors = config.get('n_neighbors', 20)
        self.interaction_matrix: Optional[InteractionMatrix] = None
        self.model: Optional[nn.Module] = None
        self.similarity_matrix: Optional[np.ndarray] = None
    
    def build_interaction_matrix(
        self,
        interactions: pd.DataFrame,
        user_col: str = 'county_id',
        item_col: str = 'intervention_id',
        rating_col: str = 'outcome_score'
    ) -> InteractionMatrix:
        """Build user-item interaction matrix"""
        
        # Create mappings
        user_ids = interactions[user_col].unique()
        item_ids = interactions[item_col].unique()
        user_mapping = {uid: i for i, uid in enumerate(user_ids)}
        item_mapping = {iid: i for i, iid in enumerate(item_ids)}
        
        # Build sparse matrix
        row_indices = interactions[user_col].map(user_mapping)
        col_indices = interactions[item_col].map(item_mapping)
        ratings = interactions[rating_col].values
        
        matrix = csr_matrix(
            (ratings, (row_indices, col_indices)),
            shape=(len(user_ids), len(item_ids))
        )
        
        self.interaction_matrix = InteractionMatrix(
            user_ids=list(user_ids),
            item_ids=list(item_ids),
            matrix=matrix,
            user_mapping=user_mapping,
            item_mapping=item_mapping
        )
        
        return self.interaction_matrix
    
    def fit(self, data: pd.DataFrame) -> None:
        """Train collaborative filtering model"""
        
        # Build interaction matrix
        self.build_interaction_matrix(data)
        
        if self.model_type == 'svd':
            self._fit_svd()
        elif self.model_type == 'neural_mf':
            self._fit_neural_mf(data)
        elif self.model_type == 'item_based':
            self._fit_item_based()
        elif self.model_type == 'user_based':
            self._fit_user_based()
        
        self.is_trained = True
    
    def _fit_svd(self) -> None:
        """Fit SVD-based matrix factorization"""
        matrix = self.interaction_matrix.matrix.astype(float)
        
        # Normalize
        user_ratings_mean = np.mean(matrix, axis=1)
        matrix_demeaned = matrix - user_ratings_mean.reshape(-1, 1)
        
        # SVD
        U, sigma, Vt = svds(matrix_demeaned, k=self.n_factors)
        sigma = np.diag(sigma)
        
        # Store components
        self.user_factors = U
        self.item_factors = Vt.T
        self.sigma = sigma
        self.user_ratings_mean = user_ratings_mean
    
    def _fit_neural_mf(self, data: pd.DataFrame) -> None:
        """Fit neural matrix factorization"""
        n_users = len(self.interaction_matrix.user_ids)
        n_items = len(self.interaction_matrix.item_ids)
        
        self.model = MatrixFactorization(
            n_users=n_users,
            n_items=n_items,
            n_factors=self.n_factors
        )
        
        # Prepare training data
        user_indices = data['county_id'].map(self.interaction_matrix.user_mapping).values
        item_indices = data['intervention_id'].map(self.interaction_matrix.item_mapping).values
        ratings = data['outcome_score'].values
        
        # Training loop
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        
        for epoch in range(self.config.get('epochs', 100)):
            self.model.train()
            user_tensor = torch.LongTensor(user_indices)
            item_tensor = torch.LongTensor(item_indices)
            rating_tensor = torch.FloatTensor(ratings).unsqueeze(1)
            
            optimizer.zero_grad()
            predictions = self.model(user_tensor, item_tensor)
            loss = criterion(predictions, rating_tensor)
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 20 == 0:
                print(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")
    
    def _fit_item_based(self) -> None:
        """Fit item-based collaborative filtering"""
        # Compute item-item similarity
        item_matrix = self.interaction_matrix.matrix.T
        self.similarity_matrix = cosine_similarity(item_matrix)
        
        # Fit nearest neighbors
        self.nn_model = NearestNeighbors(
            n_neighbors=self.n_neighbors,
            metric='cosine'
        )
        self.nn_model.fit(item_matrix)
    
    def _fit_user_based(self) -> None:
        """Fit user-based collaborative filtering"""
        # Compute user-user similarity
        user_matrix = self.interaction_matrix.matrix
        self.similarity_matrix = cosine_similarity(user_matrix)
        
        # Fit nearest neighbors
        self.nn_model = NearestNeighbors(
            n_neighbors=self.n_neighbors,
            metric='cosine'
        )
        self.nn_model.fit(user_matrix)
    
    def recommend(
        self,
        query: Dict[str, Any],
        n_recommendations: int = 10
    ) -> Recommendation:
        """Generate collaborative filtering recommendations"""
        
        if not self.is_trained:
            raise RuntimeError("Model must be trained before generating recommendations")
        
        user_id = query.get('county_id')
        
        if self.model_type == 'svd':
            return self._recommend_svd(user_id, n_recommendations)
        elif self.model_type == 'neural_mf':
            return self._recommend_neural_mf(user_id, n_recommendations)
        elif self.model_type == 'item_based':
            return self._recommend_item_based(user_id, n_recommendations)
        elif self.model_type == 'user_based':
            return self._recommend_user_based(user_id, n_recommendations)
    
    def _recommend_svd(
        self,
        user_id: str,
        n_recommendations: int
    ) -> Recommendation:
        """Generate SVD-based recommendations"""
        user_idx = self.interaction_matrix.user_mapping.get(user_id)
        if user_idx is None:
            raise ValueError(f"Unknown user: {user_id}")
        
        # Predict ratings for all items
        user_vector = self.user_factors[user_idx:user_idx+1]
        predicted_ratings = user_vector @ self.sigma @ self.item_factors.T
        predicted_ratings = predicted_ratings.flatten() + self.user_ratings_mean[user_idx]
        
        # Get items already interacted with
        user_interactions = self.interaction_matrix.matrix[user_idx].toarray().flatten()
        interacted_items = np.where(user_interactions > 0)[0]
        
        # Mask interacted items
        predicted_ratings[interacted_items] = -np.inf
        
        # Get top recommendations
        top_indices = np.argsort(predicted_ratings)[::-1][:n_recommendations]
        top_scores = predicted_ratings[top_indices]
        
        # Map back to item IDs
        item_ids = [self.interaction_matrix.item_ids[i] for i in top_indices]
        
        return Recommendation(
            recommendation_id=f"cf_svd_{user_id}_{datetime.now().timestamp()}",
            type=RecommendationType.INTERVENTIONS,
            target_id=user_id,
            items=[{"intervention_id": iid, "predicted_score": float(score)} 
                   for iid, score in zip(item_ids, top_scores)],
            scores=top_scores.tolist(),
            explanations=[],
            confidence=float(np.mean(top_scores)),
            timestamp=datetime.now(),
            metadata={"method": "svd", "n_factors": self.n_factors}
        )
    
    def _recommend_neural_mf(
        self,
        user_id: str,
        n_recommendations: int
    ) -> Recommendation:
        """Generate neural MF recommendations"""
        user_idx = self.interaction_matrix.user_mapping.get(user_id)
        if user_idx is None:
            raise ValueError(f"Unknown user: {user_id}")
        
        self.model.eval()
        
        # Predict for all items
        user_tensor = torch.LongTensor([user_idx] * len(self.interaction_matrix.item_ids))
        item_tensor = torch.LongTensor(range(len(self.interaction_matrix.item_ids)))
        
        with torch.no_grad():
            predictions = self.model(user_tensor, item_tensor).numpy().flatten()
        
        # Get top recommendations
        top_indices = np.argsort(predictions)[::-1][:n_recommendations]
        top_scores = predictions[top_indices]
        
        item_ids = [self.interaction_matrix.item_ids[i] for i in top_indices]
        
        return Recommendation(
            recommendation_id=f"cf_nmf_{user_id}_{datetime.now().timestamp()}",
            type=RecommendationType.INTERVENTIONS,
            target_id=user_id,
            items=[{"intervention_id": iid, "predicted_score": float(score)} 
                   for iid, score in zip(item_ids, top_scores)],
            scores=top_scores.tolist(),
            explanations=[],
            confidence=float(np.mean(top_scores)),
            timestamp=datetime.now(),
            metadata={"method": "neural_mf", "n_factors": self.n_factors}
        )
    
    def _recommend_item_based(
        self,
        user_id: str,
        n_recommendations: int
    ) -> Recommendation:
        """Generate item-based recommendations"""
        # Implementation for item-based CF
        pass
    
    def _recommend_user_based(
        self,
        user_id: str,
        n_recommendations: int
    ) -> Recommendation:
        """Generate user-based recommendations"""
        # Implementation for user-based CF
        pass
    
    def explain(self, recommendation: Recommendation) -> List[str]:
        """Generate explanations for collaborative filtering recommendations"""
        explanations = []
        
        for item in recommendation.items:
            intervention_id = item.get('intervention_id')
            score = item.get('predicted_score', 0)
            
            if self.model_type in ['svd', 'neural_mf']:
                exp = f"This intervention has a predicted effectiveness score of {score:.3f} " \
                      f"based on similar counties' outcomes"
            elif self.model_type == 'item_based':
                exp = f"This intervention is similar to others that have worked well in comparable counties"
            elif self.model_type == 'user_based':
                exp = f"Counties similar to yours have successfully implemented this intervention"
            else:
                exp = f"Recommended based on collaborative filtering analysis"
            
            explanations.append(exp)
        
        return explanations


# Example usage
if __name__ == "__main__":
    # Create sample interaction data
    interactions = pd.DataFrame({
        'county_id': ['county_1', 'county_1', 'county_2', 'county_2', 'county_3', 'county_3'],
        'intervention_id': ['intervention_A', 'intervention_B', 'intervention_A', 
                           'intervention_C', 'intervention_B', 'intervention_D'],
        'outcome_score': [0.8, 0.6, 0.9, 0.7, 0.75, 0.85]
    })
    
    # Initialize and train recommender
    config = {
        'model_type': 'svd',
        'n_factors': 2
    }
    
    recommender = CollaborativeFilteringRecommender(config)
    recommender.fit(interactions)
    
    # Generate recommendations
    query = {'county_id': 'county_1', 'type': 'interventions'}
    recommendations = recommender.recommend(query, n_recommendations=3)
    
    print(f"Recommendations for county_1:")
    for item, score in zip(recommendations.items, recommendations.scores):
        print(f"  - {item['intervention_id']}: {score:.3f}")
