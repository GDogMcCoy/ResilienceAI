# ResilienceAI Recommendation System Design

## Executive Summary

This document provides a comprehensive design for the ResilienceAI recommendation system, covering collaborative filtering, content-based filtering, hybrid approaches, and domain-specific recommendations for county resilience planning, intervention suggestions, and resource allocation optimization.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Collaborative Filtering](#2-collaborative-filtering)
3. [Content-Based Filtering](#3-content-based-filtering)
4. [Hybrid Recommendations](#4-hybrid-recommendations)
5. [Similar County Recommendations](#5-similar-county-recommendations)
6. [Intervention Recommendations](#6-intervention-recommendations)
7. [Resource Allocation Optimization](#7-resource-allocation-optimization)
8. [Ranking Algorithms](#8-ranking-algorithms)
9. [A/B Testing Framework](#9-ab-testing-framework)
10. [Feedback Loops](#10-feedback-loops)
11. [Recommendation Explanations](#11-recommendation-explanations)
12. [Implementation Roadmap](#12-implementation-roadmap)

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESILIENCEAI RECOMMENDATION ENGINE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Data       │  │   Feature    │  │  Candidate   │  │   Ranking    │     │
│  │   Ingestion  │→ │   Engineering│→ │  Generation  │→ │   & Scoring  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                 │                 │             │
│         ↓                 ↓                 ↓                 ↓             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RECOMMENDATION PIPELINE                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │ Collaborative│  │ Content-Based│  │   Hybrid    │  │   Context   │ │   │
│  │  │  Filtering  │  │  Filtering  │  │   Model     │  │   Aware     │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    POST-PROCESSING LAYER                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │  Diversity  │  │   Fairness  │  │  Explanation│  │    A/B      │ │   │
│  │  │   Boosting  │  │   Constraints│  │  Generation │  │   Testing   │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    OUTPUT LAYER                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   Similar   │  │ Intervention│  │   Resource  │  │   Feedback  │ │   │
│  │  │   Counties  │  │ Suggestions │  │ Allocation  │  │   Capture   │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Overview

| Component | Purpose | Technology Stack |
|-----------|---------|------------------|
| Data Ingestion | Collect county data, interventions, outcomes | Apache Kafka, PostgreSQL |
| Feature Engineering | Create embeddings and feature vectors | Python, Scikit-learn, PyTorch |
| Candidate Generation | Generate recommendation candidates | FAISS, Annoy, ScaNN |
| Ranking & Scoring | Score and rank candidates | TensorFlow Ranking, XGBoost |
| Post-Processing | Apply business rules and constraints | Python, Custom Rules Engine |
| Output Layer | Deliver recommendations via API | FastAPI, Redis Cache |

### 1.3 Data Flow Architecture

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/recommendation_architecture.py

"""
ResilienceAI Recommendation System Architecture
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime

class RecommendationType(Enum):
    SIMILAR_COUNTIES = "similar_counties"
    INTERVENTIONS = "interventions"
    RESOURCES = "resources"
    HYBRID = "hybrid"

@dataclass
class CountyProfile:
    """County demographic and resilience profile"""
    county_id: str
    state: str
    population: int
    demographics: Dict[str, float]
    risk_factors: Dict[str, float]
    resilience_score: float
    historical_interventions: List[str]
    outcomes: Dict[str, float]
    embedding: Optional[np.ndarray] = None

@dataclass
class Intervention:
    """Intervention definition and metadata"""
    intervention_id: str
    name: str
    category: str
    target_risks: List[str]
    cost_range: Tuple[float, float]
    effectiveness_score: float
    implementation_time: int  # days
    required_resources: Dict[str, Any]
    success_rate: float
    embedding: Optional[np.ndarray] = None

@dataclass
class Recommendation:
    """Recommendation output structure"""
    recommendation_id: str
    type: RecommendationType
    target_id: str
    items: List[Dict[str, Any]]
    scores: List[float]
    explanations: List[str]
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]

class BaseRecommender(ABC):
    """Abstract base class for all recommenders"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_trained = False
    
    @abstractmethod
    def fit(self, data: Any) -> None:
        """Train the recommender model"""
        pass
    
    @abstractmethod
    def recommend(self, query: Any, n_recommendations: int = 10) -> Recommendation:
        """Generate recommendations"""
        pass
    
    @abstractmethod
    def explain(self, recommendation: Recommendation) -> List[str]:
        """Generate explanations for recommendations"""
        pass

class RecommendationPipeline:
    """Main recommendation pipeline orchestrator"""
    
    def __init__(self):
        self.recommenders: Dict[str, BaseRecommender] = {}
        self.post_processors: List[Any] = []
        self.cache = {}
    
    def register_recommender(self, name: str, recommender: BaseRecommender):
        """Register a recommender component"""
        self.recommenders[name] = recommender
    
    def register_post_processor(self, processor: Any):
        """Register a post-processing component"""
        self.post_processors.append(processor)
    
    def generate_recommendations(
        self,
        query: Any,
        rec_type: RecommendationType,
        n_recommendations: int = 10,
        use_cache: bool = True
    ) -> Recommendation:
        """Execute full recommendation pipeline"""
        
        # Check cache
        cache_key = f"{rec_type.value}_{hash(str(query))}"
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Select appropriate recommender
        recommender = self.recommenders.get(rec_type.value)
        if not recommender:
            raise ValueError(f"No recommender registered for type: {rec_type}")
        
        # Generate base recommendations
        recommendation = recommender.recommend(query, n_recommendations)
        
        # Apply post-processing
        for processor in self.post_processors:
            recommendation = processor.process(recommendation)
        
        # Generate explanations
        recommendation.explanations = recommender.explain(recommendation)
        
        # Cache result
        if use_cache:
            self.cache[cache_key] = recommendation
        
        return recommendation
```

---

## 2. Collaborative Filtering

### 2.1 User-Item Collaborative Filtering

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/collaborative_filtering.py

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
        self.model_type = config.get('model_type', 'matrix_factorization')
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
        
        if self.model_type == 'matrix_factorization':
            self._fit_matrix_factorization()
        elif self.model_type == 'svd':
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
        
        # Training loop (simplified)
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
        rec_type = query.get('type', 'interventions')
        
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
            
            explanations.append(exp)
        
        return explanations
```

### 2.2 Implicit Feedback Collaborative Filtering

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/implicit_cf.py

"""
Implicit Feedback Collaborative Filtering
For cases where explicit ratings are not available
"""

import numpy as np
from scipy.sparse import csr_matrix
from typing import Dict, List, Optional
import implicit

class ImplicitCollaborativeFiltering:
    """Implicit feedback collaborative filtering using ALS"""
    
    def __init__(
        self,
        factors: int = 50,
        regularization: float = 0.01,
        iterations: int = 30,
        use_gpu: bool = False
    ):
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.use_gpu = use_gpu
        self.model = None
        self.item_factors = None
        self.user_factors = None
    
    def fit(self, interaction_matrix: csr_matrix) -> None:
        """Train implicit ALS model"""
        
        # Initialize model
        self.model = implicit.als.AlternatingLeastSquares(
            factors=self.factors,
            regularization=self.regularization,
            iterations=self.iterations,
            use_gpu=self.use_gpu
        )
        
        # Fit model
        self.model.fit(interaction_matrix)
        
        # Store factors
        self.user_factors = self.model.user_factors
        self.item_factors = self.model.item_factors
    
    def recommend(
        self,
        user_id: int,
        interaction_matrix: csr_matrix,
        n_recommendations: int = 10,
        filter_already_liked: bool = True
    ) -> List[tuple]:
        """Generate recommendations for a user"""
        
        recommendations = self.model.recommend(
            userid=user_id,
            user_items=interaction_matrix,
            N=n_recommendations,
            filter_already_liked_items=filter_already_liked,
            recalculate_user=True
        )
        
        return recommendations
```

---

## 3. Content-Based Filtering

### 3.1 County Profile-Based Recommendations

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/content_based_filtering.py

"""
Content-Based Filtering for ResilienceAI
Implements TF-IDF, word embeddings, and attribute-based matching
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModel

class ContentBasedRecommender(BaseRecommender):
    """Content-based recommender using county and intervention features"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.feature_type = config.get('feature_type', 'tabular')
        self.similarity_metric = config.get('similarity_metric', 'cosine')
        self.use_text_embeddings = config.get('use_text_embeddings', False)
        
        self.county_features: Optional[np.ndarray] = None
        self.intervention_features: Optional[np.ndarray] = None
        self.county_ids: List[str] = []
        self.intervention_ids: List[str] = []
        self.preprocessor = None
        self.text_model = None
        self.text_tokenizer = None
    
    def fit(
        self,
        counties: pd.DataFrame,
        interventions: pd.DataFrame
    ) -> None:
        """Train content-based model"""
        
        self.county_ids = counties['county_id'].tolist()
        self.intervention_ids = interventions['intervention_id'].tolist()
        
        # Process county features
        self.county_features = self._process_county_features(counties)
        
        # Process intervention features
        self.intervention_features = self._process_intervention_features(interventions)
        
        self.is_trained = True
    
    def _process_county_features(self, counties: pd.DataFrame) -> np.ndarray:
        """Process county features into embeddings"""
        
        # Numerical features
        numerical_cols = [
            'population', 'median_income', 'unemployment_rate',
            'poverty_rate', 'education_level', 'health_index'
        ]
        
        # Categorical features
        categorical_cols = ['state', 'urban_rural', 'climate_zone']
        
        # Risk factor features
        risk_cols = [col for col in counties.columns if col.startswith('risk_')]
        
        # Build preprocessor
        numerical_features = [c for c in numerical_cols if c in counties.columns]
        categorical_features = [c for c in categorical_cols if c in counties.columns]
        risk_features = [c for c in risk_cols if c in counties.columns]
        
        transformers = []
        
        if numerical_features:
            transformers.append(('num', StandardScaler(), numerical_features))
        
        if categorical_features:
            transformers.append(('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features))
        
        if risk_features:
            transformers.append(('risk', StandardScaler(), risk_features))
        
        self.preprocessor = ColumnTransformer(transformers, remainder='drop')
        
        # Fit and transform
        features = self.preprocessor.fit_transform(counties)
        
        return features
    
    def _recommend_similar_counties(
        self,
        query: Dict[str, Any],
        n_recommendations: int
    ) -> Recommendation:
        """Find similar counties based on profile"""
        
        county_id = query.get('county_id')
        county_idx = self.county_ids.index(county_id)
        
        # Get county features
        county_features = self.county_features[county_idx:county_idx+1]
        
        # Compute similarity with all counties
        similarities = cosine_similarity(county_features, self.county_features)[0]
        
        # Get top similar counties (excluding self)
        similar_indices = np.argsort(similarities)[::-1][1:n_recommendations+1]
        similar_scores = similarities[similar_indices]
        
        similar_counties = [self.county_ids[i] for i in similar_indices]
        
        return Recommendation(
            recommendation_id=f"cb_counties_{county_id}_{datetime.now().timestamp()}",
            type=RecommendationType.SIMILAR_COUNTIES,
            target_id=county_id,
            items=[{"county_id": cid, "similarity_score": float(score)} 
                   for cid, score in zip(similar_counties, similar_scores)],
            scores=similar_scores.tolist(),
            explanations=[],
            confidence=float(np.mean(similar_scores)),
            timestamp=datetime.now(),
            metadata={"method": "content_based", "feature_type": self.feature_type}
        )
```

---

## 4. Hybrid Recommendations

### 4.1 Weighted Hybrid Approach

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/hybrid_recommendations.py

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
                item_id = item.get('intervention_id') or item.get('county_id')
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
```

---

## 5. Similar County Recommendations

### 5.1 Multi-Dimensional Similarity

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/similar_counties.py

"""
Similar County Recommendation System
Finds counties with similar profiles for peer learning and benchmarking
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class SimilarityDimension(Enum):
    DEMOGRAPHIC = "demographic"
    ECONOMIC = "economic"
    GEOGRAPHIC = "geographic"
    RISK = "risk"
    RESILIENCE = "resilience"
    INTERVENTION = "intervention"

class SimilarCountyRecommender(BaseRecommender):
    """Recommender for finding similar counties"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.county_data: Optional[pd.DataFrame] = None
        self.county_embeddings: Optional[np.ndarray] = None
        self.county_ids: List[str] = []
    
    def fit(self, county_data: pd.DataFrame) -> None:
        """Build county similarity model"""
        
        self.county_data = county_data.copy()
        self.county_ids = county_data['county_id'].tolist()
        
        # Build combined embedding
        self.county_embeddings = self._build_combined_embedding(county_data)
        
        self.is_trained = True
    
    def _build_combined_embedding(self, county_data: pd.DataFrame) -> np.ndarray:
        """Build weighted combination of dimension embeddings"""
        
        # Feature groups
        demographic_cols = ['population', 'median_age', 'percent_urban']
        economic_cols = ['median_income', 'unemployment_rate', 'poverty_rate']
        risk_cols = [c for c in county_data.columns if c.startswith('risk_')]
        
        # Scale features
        scaler = StandardScaler()
        
        features = []
        for cols in [demographic_cols, economic_cols, risk_cols]:
            available = [c for c in cols if c in county_data.columns]
            if available:
                scaled = scaler.fit_transform(county_data[available].fillna(0))
                features.append(scaled)
        
        return np.hstack(features) if features else np.zeros((len(county_data), 1))
    
    def recommend(
        self,
        query: Dict[str, Any],
        n_recommendations: int = 10
    ) -> Recommendation:
        """Find similar counties"""
        
        county_id = query.get('county_id')
        
        # Get query county index
        query_idx = self.county_ids.index(county_id)
        
        # Compute similarity
        query_embedding = self.county_embeddings[query_idx:query_idx+1]
        similarities = cosine_similarity(query_embedding, self.county_embeddings)[0]
        
        # Get top similar counties (excluding self)
        similar_indices = np.argsort(similarities)[::-1]
        similar_indices = [i for i in similar_indices if i != query_idx][:n_recommendations]
        
        similar_counties = []
        scores = []
        
        for idx in similar_indices:
            county_info = {
                'county_id': self.county_ids[idx],
                'similarity_score': float(similarities[idx])
            }
            similar_counties.append(county_info)
            scores.append(float(similarities[idx]))
        
        return Recommendation(
            recommendation_id=f"similar_counties_{county_id}_{datetime.now().timestamp()}",
            type=RecommendationType.SIMILAR_COUNTIES,
            target_id=county_id,
            items=similar_counties,
            scores=scores,
            explanations=[],
            confidence=float(np.mean(scores)) if scores else 0,
            timestamp=datetime.now(),
            metadata={"method": "multi_dimensional_similarity"}
        )
```

---

## 6. Intervention Recommendations

### 6.1 Context-Aware Intervention Suggesting

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/intervention_recommendations.py

"""
Intervention Recommendation System
Suggests interventions based on county profile, risk factors, and historical outcomes
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sklearn.ensemble import GradientBoostingRegressor

class InterventionRecommender(BaseRecommender):
    """Recommender for suggesting interventions"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.interventions: Optional[pd.DataFrame] = None
        self.outcomes: Optional[pd.DataFrame] = None
        self.county_profiles: Optional[pd.DataFrame] = None
        self.effectiveness_model = None
    
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
        
        # Train effectiveness prediction model
        self._train_effectiveness_model()
        
        self.is_trained = True
    
    def _train_effectiveness_model(self) -> None:
        """Train model to predict intervention effectiveness"""
        
        # Merge data
        data = self.outcomes.merge(
            self.county_profiles, on='county_id', how='left'
        ).merge(
            self.interventions, on='intervention_id', how='left'
        )
        
        # Feature columns
        feature_cols = [c for c in data.columns 
                       if c not in ['outcome_score', 'county_id', 'intervention_id']]
        
        X = data[feature_cols].fillna(0)
        y = data['outcome_score']
        
        self.effectiveness_model = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, random_state=42
        )
        self.effectiveness_model.fit(X, y)
        self.feature_columns = feature_cols
    
    def recommend(
        self,
        query: Dict[str, Any],
        n_recommendations: int = 10
    ) -> Recommendation:
        """Generate intervention recommendations"""
        
        county_id = query.get('county_id')
        budget = query.get('budget')
        priority_risks = query.get('priority_risks', [])
        
        # Get county profile
        county_profile = self.county_profiles[
            self.county_profiles['county_id'] == county_id
        ].iloc[0]
        
        # Score all interventions
        scored_interventions = []
        
        for _, intervention in self.interventions.iterrows():
            intervention_id = intervention['intervention_id']
            
            # Check budget constraint
            if budget is not None and intervention.get('cost', 0) > budget:
                continue
            
            # Predict effectiveness
            features = self._extract_features(county_profile, intervention)
            effectiveness = self.effectiveness_model.predict([features])[0]
            
            scored_interventions.append({
                'intervention_id': intervention_id,
                'score': effectiveness,
                'name': intervention.get('name', '')
            })
        
        # Sort and select top
        scored_interventions.sort(key=lambda x: x['score'], reverse=True)
        top_interventions = scored_interventions[:n_recommendations]
        
        return Recommendation(
            recommendation_id=f"interventions_{county_id}_{datetime.now().timestamp()}",
            type=RecommendationType.INTERVENTIONS,
            target_id=county_id,
            items=top_interventions,
            scores=[i['score'] for i in top_interventions],
            explanations=[],
            confidence=float(np.mean([i['score'] for i in top_interventions])),
            timestamp=datetime.now(),
            metadata={"priority_risks": priority_risks}
        )
    
    def _extract_features(
        self,
        county_profile: pd.Series,
        intervention: pd.Series
    ) -> List[float]:
        """Extract features for prediction"""
        
        features = []
        
        for col in self.feature_columns:
            if col in county_profile.index:
                features.append(county_profile[col])
            elif col in intervention.index:
                features.append(intervention[col])
            else:
                features.append(0)
        
        return features
```

---

## 7. Resource Allocation Optimization

### 7.1 Multi-Objective Optimization

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/resource_allocation.py

"""
Resource Allocation Optimization for ResilienceAI
Optimizes distribution of resources across counties and interventions
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class AllocationResult:
    """Resource allocation result"""
    county_allocations: Dict[str, Dict[str, float]]
    intervention_allocations: Dict[str, Dict[str, float]]
    total_cost: float
    expected_impact: float
    coverage: float
    equity_score: float

class ResourceAllocationOptimizer:
    """Optimizer for resource allocation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.county_data: Optional[pd.DataFrame] = None
        self.intervention_data: Optional[pd.DataFrame] = None
        self.effectiveness_matrix: Optional[np.ndarray] = None
    
    def fit(
        self,
        county_data: pd.DataFrame,
        intervention_data: pd.DataFrame,
        effectiveness_matrix: np.ndarray
    ) -> None:
        """Initialize optimizer"""
        
        self.county_data = county_data.copy()
        self.intervention_data = intervention_data.copy()
        self.effectiveness_matrix = effectiveness_matrix
        
        self.n_counties = len(county_data)
        self.n_interventions = len(intervention_data)
    
    def optimize(
        self,
        total_budget: float,
        equity_weight: float = 0.3
    ) -> AllocationResult:
        """Optimize resource allocation using greedy approach"""
        
        n_counties = self.n_counties
        n_interventions = self.n_interventions
        
        allocation_matrix = np.zeros((n_counties, n_interventions))
        remaining_budget = total_budget
        
        costs = self.intervention_data['cost'].values
        
        # Calculate cost-effectiveness
        cost_effectiveness = self.effectiveness_matrix / (costs + 1)
        
        # Greedy allocation
        flat_indices = np.argsort(cost_effectiveness.flatten())[::-1]
        
        for flat_idx in flat_indices:
            county_idx = flat_idx // n_interventions
            intervention_idx = flat_idx % n_interventions
            
            cost = costs[intervention_idx]
            
            if cost <= remaining_budget:
                allocation_matrix[county_idx, intervention_idx] += cost
                remaining_budget -= cost
        
        return self._build_allocation_result(allocation_matrix, costs)
    
    def _build_allocation_result(
        self,
        allocation_matrix: np.ndarray,
        costs: np.ndarray
    ) -> AllocationResult:
        """Build allocation result from matrix"""
        
        county_ids = self.county_data['county_id'].values
        intervention_ids = self.intervention_data['intervention_id'].values
        
        county_allocations = {}
        for i, county_id in enumerate(county_ids):
            county_allocations[county_id] = {
                'total': float(np.sum(allocation_matrix[i, :])),
                'by_intervention': {
                    intervention_ids[j]: float(allocation_matrix[i, j])
                    for j in range(len(intervention_ids))
                    if allocation_matrix[i, j] > 0
                }
            }
        
        total_cost = float(np.sum(allocation_matrix * costs))
        expected_impact = float(np.sum(allocation_matrix * self.effectiveness_matrix))
        
        counties_with_allocation = np.sum(np.sum(allocation_matrix, axis=1) > 0)
        coverage = counties_with_allocation / len(county_ids)
        
        return AllocationResult(
            county_allocations=county_allocations,
            intervention_allocations={},
            total_cost=total_cost,
            expected_impact=expected_impact,
            coverage=coverage,
            equity_score=0.5  # Placeholder
        )
```

---

## 8. Ranking Algorithms

### 8.1 Learning-to-Rank Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/ranking_algorithms.py

"""
Ranking Algorithms for ResilienceAI
Implements various learning-to-rank approaches
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

class ListwiseRanker(nn.Module):
    """Neural listwise ranking model"""
    
    def __init__(
        self,
        n_features: int,
        hidden_dims: List[int] = [128, 64, 32],
        dropout: float = 0.2
    ):
        super().__init__()
        
        layers = []
        prev_dim = n_features
        
        for dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, dim),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev_dim = dim
        
        layers.append(nn.Linear(prev_dim, 1))
        self.network = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class LearningToRank:
    """Learning-to-rank implementation"""
    
    def __init__(
        self,
        method: str = 'listnet',
        learning_rate: float = 0.001,
        epochs: int = 100
    ):
        self.method = method
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.model = None
        self.feature_columns = []
    
    def fit(
        self,
        training_data: pd.DataFrame,
        query_col: str = 'county_id',
        label_col: str = 'relevance',
        feature_cols: Optional[List[str]] = None
    ) -> None:
        """Train ranking model"""
        
        if feature_cols is None:
            feature_cols = [c for c in training_data.columns 
                          if c not in [query_col, label_col, 'item_id']]
        
        self.feature_columns = feature_cols
        
        if self.method == 'listnet':
            self._fit_listnet(training_data, query_col, label_col)
    
    def _fit_listnet(
        self,
        data: pd.DataFrame,
        query_col: str,
        label_col: str
    ) -> None:
        """Fit ListNet ranking model"""
        
        n_features = len(self.feature_columns)
        self.model = ListwiseRanker(n_features)
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        queries = data[query_col].unique()
        
        for epoch in range(self.epochs):
            total_loss = 0
            
            for query in queries:
                query_data = data[data[query_col] == query]
                
                if len(query_data) < 2:
                    continue
                
                X = torch.FloatTensor(query_data[self.feature_columns].values)
                y = torch.FloatTensor(query_data[label_col].values)
                
                scores = self.model(X).squeeze()
                
                # ListNet loss
                score_probs = F.softmax(scores, dim=0)
                label_probs = F.softmax(y, dim=0)
                
                loss = -torch.sum(label_probs * torch.log(score_probs + 1e-10))
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}, Loss: {total_loss:.4f}")
    
    def rank(
        self,
        items: pd.DataFrame,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank items"""
        
        X = items[self.feature_columns].values
        
        self.model.eval()
        with torch.no_grad():
            scores = self.model(torch.FloatTensor(X)).squeeze().numpy()
        
        ranked_indices = np.argsort(scores)[::-1][:n_results]
        
        results = []
        for idx in ranked_indices:
            item = items.iloc[idx].to_dict()
            item['rank_score'] = float(scores[idx])
            results.append(item)
        
        return results
```

---

## 9. A/B Testing Framework

### 9.1 Experiment Management

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/ab_testing.py

"""
A/B Testing Framework for ResilienceAI
Manages experiments for recommendation algorithm evaluation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib

class ExperimentStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

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

class ABTestFramework:
    """Framework for managing A/B tests"""
    
    def __init__(self, storage_backend: str = 'memory'):
        self.storage_backend = storage_backend
        self.experiments: Dict[str, Experiment] = {}
        self.assignments: Dict[str, str] = {}
        self.events: List[Dict[str, Any]] = []
    
    def create_experiment(
        self,
        name: str,
        description: str,
        hypothesis: str,
        variants: List[ExperimentVariant],
        metrics: List[str],
        duration_days: int = 30
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
            end_date=datetime.now() + timedelta(days=duration_days)
        )
        
        self.experiments[experiment_id] = experiment
        return experiment_id
    
    def assign_variant(
        self,
        experiment_id: str,
        user_id: str
    ) -> str:
        """Assign a user to a variant"""
        
        experiment = self.experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.RUNNING:
            return experiment.variants[0].variant_id
        
        # Deterministic assignment
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        cumulative = 0
        for variant in experiment.variants:
            cumulative += variant.traffic_percentage
            if hash_value % 10000 < cumulative * 100:
                return variant.variant_id
        
        return experiment.variants[-1].variant_id
    
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
    
    def get_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get experiment results"""
        
        experiment = self.experiments[experiment_id]
        experiment_events = [e for e in self.events 
                           if e['experiment_id'] == experiment_id]
        
        variant_results = {}
        
        for variant in experiment.variants:
            variant_events = [e for e in experiment_events 
                            if e['variant_id'] == variant.variant_id]
            
            variant_results[variant.variant_id] = {
                'variant_name': variant.name,
                'sample_size': len(set(e['user_id'] for e in variant_events)),
                'metrics': self._calculate_metrics(variant_events, experiment.metrics)
            }
        
        return {
            'experiment_id': experiment_id,
            'experiment_name': experiment.name,
            'variant_results': variant_results
        }
    
    def _calculate_metrics(
        self,
        events: List[Dict[str, Any]],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Calculate metrics from events"""
        
        results = {}
        
        if 'ctr' in metrics:
            clicks = sum(1 for e in events if e['event_type'] == 'click')
            impressions = sum(1 for e in events if e['event_type'] == 'impression')
            results['ctr'] = clicks / impressions if impressions > 0 else 0
        
        if 'conversion_rate' in metrics:
            conversions = sum(1 for e in events if e['event_type'] == 'conversion')
            unique_users = len(set(e['user_id'] for e in events))
            results['conversion_rate'] = conversions / unique_users if unique_users > 0 else 0
        
        return results
    
    def _generate_id(self, name: str) -> str:
        """Generate unique experiment ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_part = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"exp_{timestamp}_{hash_part}"
```

---

## 10. Feedback Loops

### 10.1 Real-Time Feedback Integration

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/feedback_loops.py

"""
Feedback Loops for ResilienceAI
Implements real-time feedback collection and model updates
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import threading

@dataclass
class FeedbackEvent:
    """User feedback event"""
    event_id: str
    user_id: str
    recommendation_id: str
    event_type: str
    timestamp: datetime
    context: Dict[str, Any]
    value: Optional[float] = None

class FeedbackCollector:
    """Collects and processes user feedback"""
    
    def __init__(
        self,
        max_buffer_size: int = 10000,
        flush_interval_seconds: int = 60
    ):
        self.max_buffer_size = max_buffer_size
        self.flush_interval = flush_interval_seconds
        
        self.feedback_buffer: deque = deque(maxlen=max_buffer_size)
        self.processed_feedback: List[FeedbackEvent] = []
        self.handlers: Dict[str, List[Callable]] = {}
        self.lock = threading.Lock()
    
    def collect(
        self,
        user_id: str,
        recommendation_id: str,
        event_type: str,
        context: Dict[str, Any],
        value: Optional[float] = None
    ) -> None:
        """Collect a feedback event"""
        
        event = FeedbackEvent(
            event_id=self._generate_event_id(),
            user_id=user_id,
            recommendation_id=recommendation_id,
            event_type=event_type,
            timestamp=datetime.now(),
            context=context,
            value=value
        )
        
        with self.lock:
            self.feedback_buffer.append(event)
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"evt_{timestamp}"
    
    def get_feedback_summary(
        self,
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get summary of feedback"""
        
        filtered = self.processed_feedback
        
        if since:
            filtered = [e for e in filtered if e.timestamp >= since]
        
        summary = {
            'total_events': len(filtered),
            'events_by_type': {},
            'average_value': None
        }
        
        for event in filtered:
            if event.event_type not in summary['events_by_type']:
                summary['events_by_type'][event.event_type] = 0
            summary['events_by_type'][event.event_type] += 1
        
        values = [e.value for e in filtered if e.value is not None]
        if values:
            summary['average_value'] = np.mean(values)
        
        return summary
```

---

## 11. Recommendation Explanations

### 11.1 Explanation Generation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/explanation_generation.py

"""
Recommendation Explanation Generation for ResilienceAI
Generates human-readable explanations for recommendations
"""

from typing import List, Dict, Any, Optional
import numpy as np

class ExplanationGenerator:
    """Generates explanations for recommendations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.explanation_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load explanation templates"""
        
        return {
            'similar_counties': [
                "{county_name} shares {similarity_percentage:.0%} similarity with your county based on {dimensions}",
                "These counties have similar {primary_characteristics} profiles",
                "Peer counties with comparable {key_metrics}"
            ],
            'interventions': [
                "This intervention has a predicted effectiveness of {effectiveness:.0%} for your county",
                "Similar counties achieved {avg_outcome:.0%} success with this intervention",
                "Addresses your priority risk: {primary_risk}"
            ],
            'collaborative_filtering': [
                "Counties similar to yours rated this {rating:.1f}/5.0",
                "Based on outcomes from {n_similar} comparable counties",
                "{success_rate:.0%} of similar counties reported positive outcomes"
            ],
            'content_based': [
                "Matches your county's {matching_features}",
                "Aligned with your {demographic_match} characteristics",
                "Suitable for counties with {risk_profile} risk profile"
            ]
        }
    
    def generate_explanation(
        self,
        recommendation_type: str,
        item: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate explanation for a recommendation"""
        
        templates = self.explanation_templates.get(recommendation_type, [])
        
        if not templates:
            return "Recommended based on analysis of your county profile"
        
        # Select template based on available data
        template = templates[0]
        
        # Fill in template
        try:
            explanation = template.format(**{**item, **context})
        except KeyError:
            explanation = template
        
        return explanation
    
    def generate_counterfactual_explanation(
        self,
        recommended_item: Dict[str, Any],
        alternative_item: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate counterfactual explanation"""
        
        score_diff = recommended_item.get('score', 0) - alternative_item.get('score', 0)
        
        explanation = (
            f"This intervention was chosen over {alternative_item.get('name', 'alternatives')} "
            f"because it has a {score_diff:.0%} higher predicted effectiveness "
            f"for counties with your profile."
        )
        
        return explanation
    
    def generate_feature_importance_explanation(
        self,
        item: Dict[str, Any],
        feature_importance: Dict[str, float]
    ) -> str:
        """Generate explanation based on feature importance"""
        
        # Sort features by importance
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        top_features = [f.replace('_', ' ') for f, _ in sorted_features]
        
        explanation = (
            f"Key factors in this recommendation: {', '.join(top_features)}"
        )
        
        return explanation
```

---

## 12. Implementation Roadmap

### 12.1 Priority Order

| Phase | Component | Priority | Timeline | Dependencies |
|-------|-----------|----------|----------|--------------|
| 1 | Content-Based Filtering | High | Week 1-2 | Data pipeline |
| 1 | Similar County Recommender | High | Week 2-3 | Content-based |
| 2 | Collaborative Filtering | High | Week 3-4 | Interaction data |
| 2 | Intervention Recommender | High | Week 4-5 | CF + CB |
| 3 | Hybrid Recommender | Medium | Week 5-6 | CF + CB |
| 3 | Ranking Algorithms | Medium | Week 6-7 | Hybrid model |
| 4 | Resource Allocation | Medium | Week 7-8 | All recommenders |
| 4 | A/B Testing Framework | Medium | Week 8-9 | All components |
| 5 | Feedback Loops | Low | Week 9-10 | A/B framework |
| 5 | Explanation Generation | Low | Week 10-11 | All recommenders |

### 12.2 Integration Architecture

```
API Layer (FastAPI)
    |
    v
Recommendation Service
    |-- Similar County Endpoint
    |-- Intervention Endpoint
    |-- Resource Allocation Endpoint
    |
    v
Model Layer
    |-- Content-Based Model
    |-- Collaborative Filtering Model
    |-- Hybrid Model
    |-- Ranking Model
    |
    v
Data Layer
    |-- County Profiles
    |-- Intervention Database
    |-- Interaction History
    |-- Outcomes Data
```

### 12.3 Key Performance Indicators

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recommendation Acceptance Rate | >60% | User feedback |
| Click-Through Rate | >15% | Event tracking |
| Outcome Improvement | >20% | Before/after comparison |
| Latency (p99) | <200ms | API monitoring |
| Coverage | >95% | Counties with recommendations |
| Diversity | >0.7 | Intra-list similarity |

---

## Summary

This comprehensive recommendation system design for ResilienceAI includes:

1. **Multiple recommendation approaches**: Collaborative filtering, content-based filtering, and hybrid methods
2. **Domain-specific recommenders**: Similar counties, interventions, and resource allocation
3. **Advanced ranking**: Learning-to-rank algorithms with diversity reranking
4. **Experimentation**: A/B testing framework for continuous improvement
5. **Feedback integration**: Real-time feedback collection and model updates
6. **Explainability**: Human-readable explanations for all recommendations

The implementation follows a phased approach, starting with foundational components and building toward advanced features.

---

## Generated Files

All implementation code is available in the following files:

- `/mnt/okcomputer/output/resilience_ai_analysis/recommendation_architecture.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/collaborative_filtering.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/implicit_cf.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/content_based_filtering.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/hybrid_recommendations.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/similar_counties.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/intervention_recommendations.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/resource_allocation.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/ranking_algorithms.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/ab_testing.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/feedback_loops.py`
- `/mnt/okcomputer/output/resilience_ai_analysis/explanation_generation.py`
