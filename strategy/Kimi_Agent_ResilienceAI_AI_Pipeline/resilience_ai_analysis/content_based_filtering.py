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
from datetime import datetime

from recommendation_architecture import BaseRecommender, Recommendation, RecommendationType


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
    
    def _process_intervention_features(self, interventions: pd.DataFrame) -> np.ndarray:
        """Process intervention features into embeddings"""
        
        # Numerical features
        numerical_cols = ['cost', 'duration', 'effectiveness_score', 'success_rate']
        
        # Categorical features
        categorical_cols = ['category', 'target_risk_type', 'implementation_complexity']
        
        # Build preprocessor
        numerical_features = [c for c in numerical_cols if c in interventions.columns]
        categorical_features = [c for c in categorical_cols if c in interventions.columns]
        
        transformers = []
        
        if numerical_features:
            transformers.append(('num', StandardScaler(), numerical_features))
        
        if categorical_features:
            transformers.append(('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features))
        
        preprocessor = ColumnTransformer(transformers, remainder='drop')
        
        # Fit and transform
        features = preprocessor.fit_transform(interventions)
        
        return features
    
    def recommend(
        self,
        query: Dict[str, Any],
        n_recommendations: int = 10
    ) -> Recommendation:
        """Generate content-based recommendations"""
        
        if not self.is_trained:
            raise RuntimeError("Model must be trained before generating recommendations")
        
        rec_type = query.get('type', 'interventions')
        
        if rec_type == 'similar_counties':
            return self._recommend_similar_counties(query, n_recommendations)
        elif rec_type == 'interventions':
            return self._recommend_interventions(query, n_recommendations)
        else:
            raise ValueError(f"Unknown recommendation type: {rec_type}")
    
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
    
    def _recommend_interventions(
        self,
        query: Dict[str, Any],
        n_recommendations: int
    ) -> Recommendation:
        """Recommend interventions based on county profile"""
        
        county_id = query.get('county_id')
        county_idx = self.county_ids.index(county_id)
        
        # Get county features
        county_features = self.county_features[county_idx:county_idx+1]
        
        # Project county features to intervention space
        # For simplicity, we'll use a learned projection
        if not hasattr(self, 'projection_matrix'):
            # Initialize with random projection (in practice, learn from data)
            self.projection_matrix = np.random.randn(
                self.county_features.shape[1],
                self.intervention_features.shape[1]
            )
        
        projected_county = county_features @ self.projection_matrix
        
        # Compute similarity with all interventions
        similarities = cosine_similarity(projected_county, self.intervention_features)[0]
        
        # Get top interventions
        top_indices = np.argsort(similarities)[::-1][:n_recommendations]
        top_scores = similarities[top_indices]
        
        top_interventions = [self.intervention_ids[i] for i in top_indices]
        
        return Recommendation(
            recommendation_id=f"cb_interventions_{county_id}_{datetime.now().timestamp()}",
            type=RecommendationType.INTERVENTIONS,
            target_id=county_id,
            items=[{"intervention_id": iid, "match_score": float(score)} 
                   for iid, score in zip(top_interventions, top_scores)],
            scores=top_scores.tolist(),
            explanations=[],
            confidence=float(np.mean(top_scores)),
            timestamp=datetime.now(),
            metadata={"method": "content_based", "feature_type": self.feature_type}
        )
    
    def explain(self, recommendation: Recommendation) -> List[str]:
        """Generate explanations for content-based recommendations"""
        
        explanations = []
        target_id = recommendation.target_id
        
        if recommendation.type == RecommendationType.SIMILAR_COUNTIES:
            explanations.append(
                f"These counties have similar demographic profiles, risk factors, "
                f"and socioeconomic characteristics to {target_id}"
            )
        elif recommendation.type == RecommendationType.INTERVENTIONS:
            explanations.append(
                f"These interventions are well-suited for counties with similar "
                f"profiles to {target_id} based on their characteristics"
            )
        
        # Add feature-specific explanations
        for item in recommendation.items[:3]:
            if 'similarity_score' in item:
                score = item['similarity_score']
                explanations.append(
                    f"Match score: {score:.3f} based on shared characteristics"
                )
        
        return explanations


class TFIDFRecommender:
    """TF-IDF based recommender for text-based matching"""
    
    def __init__(
        self,
        max_features: int = 1000,
        ngram_range: tuple = (1, 2),
        min_df: int = 2
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.vectorizer = None
        self.tfidf_matrix = None
        self.item_ids = []
    
    def fit(self, documents: List[str], item_ids: List[str]) -> None:
        """Fit TF-IDF vectorizer"""
        
        self.item_ids = item_ids
        
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            stop_words='english'
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)
    
    def recommend(
        self,
        query: str,
        n_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """Recommend items based on text query"""
        
        # Transform query
        query_vector = self.vectorizer.transform([query])
        
        # Compute similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # Get top matches
        top_indices = np.argsort(similarities)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_indices:
            recommendations.append({
                'item_id': self.item_ids[idx],
                'score': float(similarities[idx])
            })
        
        return recommendations


# Example usage
if __name__ == "__main__":
    # Create sample county data
    counties = pd.DataFrame({
        'county_id': ['c1', 'c2', 'c3'],
        'population': [100000, 150000, 80000],
        'median_income': [50000, 60000, 45000],
        'unemployment_rate': [0.05, 0.04, 0.06],
        'state': ['CA', 'CA', 'TX'],
        'risk_flood': [0.3, 0.2, 0.5],
        'risk_wildfire': [0.7, 0.6, 0.2]
    })
    
    interventions = pd.DataFrame({
        'intervention_id': ['i1', 'i2', 'i3'],
        'cost': [100000, 150000, 80000],
        'duration': [180, 90, 30],
        'effectiveness_score': [0.8, 0.7, 0.6],
        'category': ['infrastructure', 'emergency', 'community'],
        'success_rate': [0.75, 0.80, 0.70]
    })
    
    # Initialize and train recommender
    config = {'feature_type': 'tabular'}
    recommender = ContentBasedRecommender(config)
    recommender.fit(counties, interventions)
    
    # Find similar counties
    query = {'county_id': 'c1', 'type': 'similar_counties'}
    recommendations = recommender.recommend(query, n_recommendations=2)
    
    print(f"Counties similar to c1:")
    for item, score in zip(recommendations.items, recommendations.scores):
        print(f"  - {item['county_id']}: {score:.3f}")
    
    # Recommend interventions
    query = {'county_id': 'c1', 'type': 'interventions'}
    recommendations = recommender.recommend(query, n_recommendations=2)
    
    print(f"\nInterventions for c1:")
    for item, score in zip(recommendations.items, recommendations.scores):
        print(f"  - {item['intervention_id']}: {score:.3f}")
