"""
Similar County Recommendation System
Finds counties with similar profiles for peer learning and benchmarking
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from recommendation_architecture import BaseRecommender, Recommendation, RecommendationType


class SimilarityDimension(Enum):
    """Dimensions for county similarity calculation"""
    DEMOGRAPHIC = "demographic"
    ECONOMIC = "economic"
    GEOGRAPHIC = "geographic"
    RISK = "risk"
    RESILIENCE = "resilience"
    INTERVENTION = "intervention"


@dataclass
class SimilarityConfig:
    """Configuration for similarity calculation"""
    dimensions: List[SimilarityDimension]
    weights: Dict[SimilarityDimension, float]
    normalization: str = "standard"


class SimilarCountyRecommender(BaseRecommender):
    """Recommender for finding similar counties"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.similarity_config = config.get('similarity_config', self._default_config())
        self.county_data: Optional[pd.DataFrame] = None
        self.county_embeddings: Optional[np.ndarray] = None
        self.county_ids: List[str] = []
        self.dimension_features: Dict[SimilarityDimension, List[str]] = {}
    
    def _default_config(self) -> SimilarityConfig:
        """Default similarity configuration"""
        return SimilarityConfig(
            dimensions=[
                SimilarityDimension.DEMOGRAPHIC,
                SimilarityDimension.ECONOMIC,
                SimilarityDimension.RISK
            ],
            weights={
                SimilarityDimension.DEMOGRAPHIC: 0.3,
                SimilarityDimension.ECONOMIC: 0.3,
                SimilarityDimension.RISK: 0.4
            }
        )
    
    def _define_dimension_features(self) -> None:
        """Define feature groups for each dimension"""
        
        self.dimension_features = {
            SimilarityDimension.DEMOGRAPHIC: [
                'population', 'population_density', 'median_age',
                'percent_urban', 'education_high_school', 'education_bachelors'
            ],
            SimilarityDimension.ECONOMIC: [
                'median_income', 'unemployment_rate', 'poverty_rate',
                'gdp_per_capita', 'industry_diversity_index'
            ],
            SimilarityDimension.GEOGRAPHIC: [
                'latitude', 'longitude', 'elevation',
                'climate_zone_encoded', 'coastal_distance'
            ],
            SimilarityDimension.RISK: [
                'risk_flood', 'risk_wildfire', 'risk_hurricane',
                'risk_earthquake', 'risk_drought', 'risk_storm'
            ],
            SimilarityDimension.RESILIENCE: [
                'resilience_score', 'infrastructure_quality',
                'emergency_preparedness', 'community_engagement'
            ],
            SimilarityDimension.INTERVENTION: [
                'historical_intervention_count', 'avg_intervention_success',
                'intervention_diversity'
            ]
        }
    
    def fit(self, county_data: pd.DataFrame) -> None:
        """Build county similarity model"""
        
        self.county_data = county_data.copy()
        self.county_ids = county_data['county_id'].tolist()
        
        self._define_dimension_features()
        
        # Build embeddings for each dimension
        self.dimension_embeddings = {}
        self.dimension_scalers = {}
        
        for dim in self.similarity_config.dimensions:
            features = self.dimension_features.get(dim, [])
            available_features = [f for f in features if f in county_data.columns]
            
            if available_features:
                # Extract and scale features
                dim_data = county_data[available_features].fillna(0)
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(dim_data)
                
                self.dimension_embeddings[dim] = scaled_data
                self.dimension_scalers[dim] = scaler
        
        # Build combined embedding
        self.county_embeddings = self._build_combined_embedding()
        
        self.is_trained = True
    
    def _build_combined_embedding(self) -> np.ndarray:
        """Build weighted combination of dimension embeddings"""
        
        combined_parts = []
        
        for dim in self.similarity_config.dimensions:
            if dim in self.dimension_embeddings:
                weight = self.similarity_config.weights.get(dim, 1.0)
                weighted_embedding = self.dimension_embeddings[dim] * weight
                combined_parts.append(weighted_embedding)
        
        if combined_parts:
            return np.hstack(combined_parts)
        else:
            return np.zeros((len(self.county_ids), 1))
    
    def recommend(
        self,
        query: Dict[str, Any],
        n_recommendations: int = 10
    ) -> Recommendation:
        """Find similar counties"""
        
        if not self.is_trained:
            raise RuntimeError("Model must be trained before generating recommendations")
        
        county_id = query.get('county_id')
        filters = query.get('filters', {})
        
        # Get query county index
        try:
            query_idx = self.county_ids.index(county_id)
        except ValueError:
            raise ValueError(f"Unknown county: {county_id}")
        
        # Compute similarity
        similarities = self._compute_similarity(query_idx, filters)
        
        # Get top similar counties (excluding self)
        similar_indices = np.argsort(similarities)[::-1]
        similar_indices = [i for i in similar_indices if i != query_idx][:n_recommendations]
        
        similar_counties = []
        scores = []
        
        for idx in similar_indices:
            county_info = self._get_county_details(idx)
            county_info['similarity_score'] = float(similarities[idx])
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
            metadata={
                "dimensions": [d.value for d in self.similarity_config.dimensions],
                "weights": {k.value: v for k, v in self.similarity_config.weights.items()}
            }
        )
    
    def _compute_similarity(
        self,
        query_idx: int,
        filters: Dict[str, Any]
    ) -> np.ndarray:
        """Compute similarity with optional filters"""
        
        query_embedding = self.county_embeddings[query_idx:query_idx+1]
        
        # Apply filters if specified
        if filters:
            mask = self._apply_filters(filters)
            filtered_embeddings = self.county_embeddings[mask]
            similarities = cosine_similarity(query_embedding, filtered_embeddings)[0]
            
            # Map back to original indices
            full_similarities = np.zeros(len(self.county_ids))
            full_similarities[mask] = similarities
            return full_similarities
        else:
            return cosine_similarity(query_embedding, self.county_embeddings)[0]
    
    def _apply_filters(self, filters: Dict[str, Any]) -> np.ndarray:
        """Apply filters to county data"""
        
        mask = np.ones(len(self.county_ids), dtype=bool)
        
        if 'min_population' in filters:
            mask &= self.county_data['population'] >= filters['min_population']
        
        if 'max_population' in filters:
            mask &= self.county_data['population'] <= filters['max_population']
        
        if 'states' in filters:
            mask &= self.county_data['state'].isin(filters['states'])
        
        if 'min_resilience_score' in filters:
            mask &= self.county_data['resilience_score'] >= filters['min_resilience_score']
        
        return mask
    
    def _get_county_details(self, idx: int) -> Dict[str, Any]:
        """Get detailed county information"""
        
        county_row = self.county_data.iloc[idx]
        
        return {
            'county_id': county_row['county_id'],
            'county_name': county_row.get('county_name', ''),
            'state': county_row.get('state', ''),
            'population': int(county_row.get('population', 0)),
            'resilience_score': float(county_row.get('resilience_score', 0)),
            'top_risks': self._get_top_risks(county_row),
            'key_demographics': self._get_key_demographics(county_row)
        }
    
    def _get_top_risks(self, county_row: pd.Series, n: int = 3) -> List[Dict[str, Any]]:
        """Get top risks for a county"""
        
        risk_cols = [c for c in county_row.index if c.startswith('risk_')]
        risks = [(c.replace('risk_', ''), county_row[c]) for c in risk_cols]
        risks.sort(key=lambda x: x[1], reverse=True)
        
        return [{'type': r[0], 'score': float(r[1])} for r in risks[:n]]
    
    def _get_key_demographics(self, county_row: pd.Series) -> Dict[str, Any]:
        """Get key demographic information"""
        
        return {
            'median_income': float(county_row.get('median_income', 0)),
            'unemployment_rate': float(county_row.get('unemployment_rate', 0)),
            'poverty_rate': float(county_row.get('poverty_rate', 0)),
            'median_age': float(county_row.get('median_age', 0))
        }
    
    def explain(self, recommendation: Recommendation) -> List[str]:
        """Generate explanations for similar county recommendations"""
        
        explanations = []
        target_id = recommendation.target_id
        dimensions = recommendation.metadata.get('dimensions', [])
        weights = recommendation.metadata.get('weights', {})
        
        explanations.append(
            f"These counties were selected based on similarity across "
            f"{len(dimensions)} dimensions: {', '.join(dimensions)}"
        )
        
        # Add dimension-specific explanations
        for dim, weight in weights.items():
            if weight > 0.3:
                explanations.append(
                    f"{dim.replace('_', ' ').title()} similarity has high influence (weight: {weight:.2f})"
                )
        
        return explanations
    
    def find_peer_groups(
        self,
        n_groups: int = 10,
        min_group_size: int = 5
    ) -> List[Dict[str, Any]]:
        """Find natural peer groups using clustering"""
        
        # Apply clustering
        kmeans = KMeans(n_clusters=n_groups, random_state=42, n_init=10)
        labels = kmeans.fit_predict(self.county_embeddings)
        
        # Build peer groups
        peer_groups = []
        for group_id in range(n_groups):
            group_mask = labels == group_id
            group_size = group_mask.sum()
            
            if group_size >= min_group_size:
                group_counties = [self.county_ids[i] for i in np.where(group_mask)[0]]
                
                # Compute group centroid
                centroid = self.county_embeddings[group_mask].mean(axis=0)
                
                # Find representative counties
                distances = np.linalg.norm(
                    self.county_embeddings[group_mask] - centroid,
                    axis=1
                )
                representative_idx = np.argmin(distances)
                representative = group_counties[representative_idx]
                
                peer_groups.append({
                    'group_id': group_id,
                    'size': int(group_size),
                    'counties': group_counties,
                    'representative': representative,
                    'characteristics': self._describe_group(group_mask)
                })
        
        return peer_groups
    
    def _describe_group(self, group_mask: np.ndarray) -> Dict[str, Any]:
        """Describe characteristics of a peer group"""
        
        group_data = self.county_data[group_mask]
        
        characteristics = {}
        
        if 'population' in group_data.columns:
            characteristics['avg_population'] = float(group_data['population'].mean())
        
        if 'resilience_score' in group_data.columns:
            characteristics['avg_resilience_score'] = float(group_data['resilience_score'].mean())
        
        # Common risks
        risk_cols = [c for c in group_data.columns if c.startswith('risk_')]
        if risk_cols:
            avg_risks = group_data[risk_cols].mean()
            top_risks = avg_risks.nlargest(3)
            characteristics['primary_risks'] = [
                {'type': c.replace('risk_', ''), 'avg_score': float(v)}
                for c, v in top_risks.items()
            ]
        
        return characteristics


# Example usage
if __name__ == "__main__":
    # Create sample county data
    county_data = pd.DataFrame({
        'county_id': ['county_1', 'county_2', 'county_3', 'county_4', 'county_5'],
        'county_name': ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon'],
        'state': ['CA', 'CA', 'TX', 'TX', 'FL'],
        'population': [100000, 150000, 200000, 80000, 120000],
        'median_income': [60000, 65000, 55000, 50000, 58000],
        'unemployment_rate': [0.05, 0.04, 0.06, 0.07, 0.055],
        'poverty_rate': [0.12, 0.10, 0.15, 0.18, 0.14],
        'resilience_score': [0.75, 0.80, 0.70, 0.65, 0.72],
        'risk_flood': [0.3, 0.2, 0.5, 0.4, 0.6],
        'risk_wildfire': [0.7, 0.6, 0.2, 0.3, 0.1],
        'risk_hurricane': [0.1, 0.1, 0.3, 0.2, 0.8]
    })
    
    # Initialize and train recommender
    config = {
        'similarity_config': SimilarityConfig(
            dimensions=[SimilarityDimension.DEMOGRAPHIC, SimilarityDimension.ECONOMIC, SimilarityDimension.RISK],
            weights={
                SimilarityDimension.DEMOGRAPHIC: 0.3,
                SimilarityDimension.ECONOMIC: 0.3,
                SimilarityDimension.RISK: 0.4
            }
        )
    }
    
    recommender = SimilarCountyRecommender(config)
    recommender.fit(county_data)
    
    # Find similar counties
    query = {'county_id': 'county_1'}
    recommendations = recommender.recommend(query, n_recommendations=3)
    
    print(f"Counties similar to county_1:")
    for item, score in zip(recommendations.items, recommendations.scores):
        print(f"  - {item['county_name']} ({item['county_id']}): {score:.3f}")
    
    # Find peer groups
    peer_groups = recommender.find_peer_groups(n_groups=3, min_group_size=2)
    print(f"\nFound {len(peer_groups)} peer groups")
    for group in peer_groups:
        print(f"  Group {group['group_id']}: {group['size']} counties, representative: {group['representative']}")
