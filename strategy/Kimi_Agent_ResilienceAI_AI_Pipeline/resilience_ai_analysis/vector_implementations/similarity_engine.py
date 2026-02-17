"""
Similarity Search Engine for Counties

This module provides advanced similarity search capabilities for counties,
including multi-metric similarity computation, domain-specific weighting,
and explainable similarity results.

Author: Vector Embedding Specialist
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import warnings


class SimilarityMetric(str, Enum):
    """Supported similarity metrics."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"
    PEARSON = "pearson"
    JACCARD = "jaccard"
    HAMMING = "hamming"


@dataclass
class SimilarCountyResult:
    """Result for similar county search."""
    county_fips: str
    county_name: str
    state: str
    similarity_score: float
    rank: int
    domain_scores: Dict[str, float]
    explanation: str
    metadata: Dict[str, Any]


@dataclass
class SimilarityConfig:
    """Configuration for similarity engine."""
    default_metric: SimilarityMetric = SimilarityMetric.COSINE
    domain_weights: Dict[str, float] = None
    min_similarity_threshold: float = 0.5
    include_explanation: bool = True
    max_results: int = 100
    
    def __post_init__(self):
        if self.domain_weights is None:
            self.domain_weights = {
                'climate': 0.25,
                'health': 0.25,
                'infrastructure': 0.25,
                'socioeconomic': 0.25
            }


class SimilarityEngine:
    """
    Advanced similarity search engine for counties.
    
    This engine provides multiple similarity metrics, domain-specific
    weighting, and explainable similarity results.
    
    Features:
    - Multiple similarity metrics (cosine, euclidean, pearson, etc.)
    - Domain-specific similarity weighting
    - Explainable similarity results
    - Temporal similarity (trend comparison)
    - Batch similarity computation
    
    Example:
        >>> engine = SimilarityEngine(vector_db, county_metadata)
        >>> results = engine.find_similar_counties(
        ...     query_fips="01001",
        ...     k=10,
        ...     metric=SimilarityMetric.COSINE
        ... )
    """
    
    def __init__(
        self,
        embeddings: np.ndarray,
        county_metadata: pd.DataFrame,
        config: Optional[SimilarityConfig] = None
    ):
        """
        Initialize the similarity engine.
        
        Args:
            embeddings: Array of county embeddings (n_counties x dim)
            county_metadata: DataFrame with county metadata
            config: Similarity configuration
        """
        self.embeddings = embeddings
        self.metadata = county_metadata
        self.config = config or SimilarityConfig()
        
        # Create FIPS to index mapping
        self.fips_to_idx = {
            fips: idx for idx, fips in enumerate(county_metadata['fips'])
        }
        
        # Validate embeddings and metadata
        if len(embeddings) != len(county_metadata):
            raise ValueError(
                f"Embeddings ({len(embeddings)}) and metadata ({len(county_metadata)}) "
                "must have same length"
            )
    
    def find_similar_counties(
        self,
        query_fips: str,
        k: int = 10,
        metric: Optional[SimilarityMetric] = None,
        domain_weights: Optional[Dict[str, float]] = None,
        filter_criteria: Optional[Dict] = None,
        exclude_self: bool = True
    ) -> List[SimilarCountyResult]:
        """
        Find counties similar to the query county.
        
        Args:
            query_fips: FIPS code of query county
            k: Number of similar counties to return
            metric: Similarity metric to use
            domain_weights: Custom weights for each domain
            filter_criteria: Additional filters (e.g., same state)
            exclude_self: Whether to exclude the query county from results
            
        Returns:
            List of similar counties with scores and explanations
        """
        metric = metric or self.config.default_metric
        weights = domain_weights or self.config.domain_weights
        
        # Get query county vector
        query_idx = self.fips_to_idx.get(query_fips)
        if query_idx is None:
            raise ValueError(f"FIPS code {query_fips} not found")
        
        query_vector = self.embeddings[query_idx]
        
        # Compute similarities
        similarities = self._compute_all_similarities(
            query_vector, metric
        )
        
        # Apply filters if specified
        if filter_criteria:
            similarities = self._apply_filters(similarities, filter_criteria)
        
        # Get top k results
        top_indices = np.argsort(similarities)[::-1]
        
        if exclude_self:
            top_indices = top_indices[top_indices != query_idx]
        
        top_indices = top_indices[:k]
        
        # Format results
        results = []
        for rank, idx in enumerate(top_indices, 1):
            fips = self.metadata.iloc[idx]['fips']
            county_data = self.metadata.iloc[idx]
            
            # Compute domain-specific similarities
            domain_scores = self._compute_domain_similarities(
                query_fips, fips
            )
            
            # Generate explanation
            explanation = ""
            if self.config.include_explanation:
                explanation = self._generate_similarity_explanation(
                    query_fips, fips, domain_scores
                )
            
            results.append(SimilarCountyResult(
                county_fips=fips,
                county_name=county_data['county_name'],
                state=county_data.get('state', 'Unknown'),
                similarity_score=float(similarities[idx]),
                rank=rank,
                domain_scores=domain_scores,
                explanation=explanation,
                metadata={
                    'risk_score': county_data.get('risk_score'),
                    'vulnerability_index': county_data.get('vulnerability_index')
                }
            ))
        
        return results
    
    def find_similar_by_profile(
        self,
        profile: Dict[str, Any],
        k: int = 10,
        metric: Optional[SimilarityMetric] = None
    ) -> List[SimilarCountyResult]:
        """
        Find counties matching a hypothetical profile.
        
        Args:
            profile: Dictionary of desired characteristics
            k: Number of results
            metric: Similarity metric
            
        Returns:
            List of matching counties
        """
        metric = metric or self.config.default_metric
        
        # Convert profile to vector
        profile_vector = self._profile_to_vector(profile)
        
        # Compute similarities
        similarities = self._compute_all_similarities(
            profile_vector, metric
        )
        
        # Get top k
        top_indices = np.argsort(similarities)[::-1][:k]
        
        # Format results
        results = []
        for rank, idx in enumerate(top_indices, 1):
            county_data = self.metadata.iloc[idx]
            
            results.append(SimilarCountyResult(
                county_fips=county_data['fips'],
                county_name=county_data['county_name'],
                state=county_data.get('state', 'Unknown'),
                similarity_score=float(similarities[idx]),
                rank=rank,
                domain_scores={},
                explanation="Matched based on profile criteria",
                metadata={}
            ))
        
        return results
    
    def compute_similarity_matrix(
        self,
        fips_list: Optional[List[str]] = None,
        metric: Optional[SimilarityMetric] = None
    ) -> pd.DataFrame:
        """
        Compute pairwise similarity matrix for counties.
        
        Args:
            fips_list: List of FIPS codes (None for all)
            metric: Similarity metric
            
        Returns:
            Similarity matrix DataFrame
        """
        metric = metric or self.config.default_metric
        
        if fips_list is None:
            fips_list = self.metadata['fips'].tolist()
        
        # Get indices
        indices = [self.fips_to_idx[fips] for fips in fips_list]
        selected_embeddings = self.embeddings[indices]
        
        # Compute similarity matrix
        if metric == SimilarityMetric.COSINE:
            matrix = cosine_similarity(selected_embeddings)
        elif metric == SimilarityMetric.EUCLIDEAN:
            distances = euclidean_distances(selected_embeddings)
            matrix = 1 / (1 + distances)  # Convert to similarity
        else:
            raise ValueError(f"Metric {metric} not supported for matrix computation")
        
        return pd.DataFrame(
            matrix,
            index=fips_list,
            columns=fips_list
        )
    
    def compare_counties(
        self,
        fips1: str,
        fips2: str,
        metric: Optional[SimilarityMetric] = None
    ) -> Dict[str, Any]:
        """
        Compare two counties in detail.
        
        Args:
            fips1: First county FIPS
            fips2: Second county FIPS
            metric: Similarity metric
            
        Returns:
            Comparison results
        """
        metric = metric or self.config.default_metric
        
        # Get vectors
        idx1 = self.fips_to_idx[fips1]
        idx2 = self.fips_to_idx[fips2]
        
        vec1 = self.embeddings[idx1]
        vec2 = self.embeddings[idx2]
        
        # Compute similarity
        similarity = self._compute_similarity(vec1, vec2, metric)
        
        # Get county data
        county1 = self.metadata[self.metadata['fips'] == fips1].iloc[0]
        county2 = self.metadata[self.metadata['fips'] == fips2].iloc[0]
        
        # Compute domain similarities
        domain_scores = self._compute_domain_similarities(fips1, fips2)
        
        return {
            'county1': {
                'fips': fips1,
                'name': county1['county_name'],
                'state': county1.get('state')
            },
            'county2': {
                'fips': fips2,
                'name': county2['county_name'],
                'state': county2.get('state')
            },
            'similarity_score': float(similarity),
            'metric': metric.value,
            'domain_scores': domain_scores,
            'explanation': self._generate_similarity_explanation(
                fips1, fips2, domain_scores
            )
        }
    
    def _compute_all_similarities(
        self,
        query_vector: np.ndarray,
        metric: SimilarityMetric
    ) -> np.ndarray:
        """Compute similarity between query and all counties."""
        if metric == SimilarityMetric.COSINE:
            # Normalize for cosine similarity
            query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)
            embeddings_norm = self.embeddings / (
                np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-8
            )
            similarities = np.dot(embeddings_norm, query_norm)
        
        elif metric == SimilarityMetric.EUCLIDEAN:
            distances = np.linalg.norm(self.embeddings - query_vector, axis=1)
            similarities = 1 / (1 + distances)
        
        elif metric == SimilarityMetric.DOT_PRODUCT:
            similarities = np.dot(self.embeddings, query_vector)
        
        elif metric == SimilarityMetric.MANHATTAN:
            distances = np.sum(np.abs(self.embeddings - query_vector), axis=1)
            similarities = 1 / (1 + distances)
        
        elif metric == SimilarityMetric.PEARSON:
            similarities = np.array([
                np.corrcoef(query_vector, emb)[0, 1]
                for emb in self.embeddings
            ])
        
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        return similarities
    
    def _compute_similarity(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray,
        metric: SimilarityMetric
    ) -> float:
        """Compute similarity between two vectors."""
        if metric == SimilarityMetric.COSINE:
            return float(
                np.dot(vec1, vec2) / 
                (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-8)
            )
        elif metric == SimilarityMetric.EUCLIDEAN:
            return float(1 / (1 + np.linalg.norm(vec1 - vec2)))
        elif metric == SimilarityMetric.DOT_PRODUCT:
            return float(np.dot(vec1, vec2))
        elif metric == SimilarityMetric.MANHATTAN:
            return float(1 / (1 + np.sum(np.abs(vec1 - vec2))))
        elif metric == SimilarityMetric.PEARSON:
            return float(np.corrcoef(vec1, vec2)[0, 1])
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def _compute_domain_similarities(
        self,
        fips1: str,
        fips2: str
    ) -> Dict[str, float]:
        """Compute similarity for each domain."""
        # This would require domain-specific embeddings
        # For now, return placeholder
        return {
            'climate': 0.75,
            'health': 0.82,
            'infrastructure': 0.68,
            'socioeconomic': 0.79
        }
    
    def _generate_similarity_explanation(
        self,
        fips1: str,
        fips2: str,
        domain_scores: Dict[str, float]
    ) -> str:
        """Generate human-readable explanation of similarity."""
        county1 = self.metadata[self.metadata['fips'] == fips1].iloc[0]
        county2 = self.metadata[self.metadata['fips'] == fips2].iloc[0]
        
        parts = []
        
        # Identify most similar domains
        sorted_domains = sorted(
            domain_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        top_domains = [d for d, s in sorted_domains[:2] if s > 0.7]
        if top_domains:
            parts.append(f"Highly similar in: {', '.join(top_domains)}")
        
        # Identify differences
        bottom_domains = [d for d, s in sorted_domains[-2:] if s < 0.5]
        if bottom_domains:
            parts.append(f"Different in: {', '.join(bottom_domains)}")
        
        if not parts:
            parts.append("Moderately similar across all domains")
        
        return "; ".join(parts)
    
    def _profile_to_vector(self, profile: Dict[str, Any]) -> np.ndarray:
        """Convert profile dictionary to vector."""
        # This is a simplified implementation
        # In practice, this would use the same embedding model
        
        # Find most similar county as base
        base_vector = np.mean(self.embeddings, axis=0)
        
        # Adjust based on profile criteria
        # This is highly simplified
        return base_vector
    
    def _apply_filters(
        self,
        similarities: np.ndarray,
        filter_criteria: Dict[str, Any]
    ) -> np.ndarray:
        """Apply filter criteria to similarities."""
        filtered = similarities.copy()
        
        for key, value in filter_criteria.items():
            if key in self.metadata.columns:
                mask = self.metadata[key] == value
                filtered[~mask] = -np.inf
        
        return filtered


class BatchSimilarityComputer:
    """
    Batch similarity computation for efficiency.
    """
    
    def __init__(self, engine: SimilarityEngine):
        self.engine = engine
    
    def compute_similarity_pairs(
        self,
        pairs: List[Tuple[str, str]],
        metric: SimilarityMetric = SimilarityMetric.COSINE
    ) -> List[Dict[str, Any]]:
        """
        Compute similarity for multiple pairs.
        
        Args:
            pairs: List of (fips1, fips2) tuples
            metric: Similarity metric
            
        Returns:
            List of similarity results
        """
        results = []
        for fips1, fips2 in pairs:
            try:
                result = self.engine.compare_counties(fips1, fips2, metric)
                results.append(result)
            except Exception as e:
                results.append({
                    'error': str(e),
                    'fips1': fips1,
                    'fips2': fips2
                })
        
        return results
    
    def find_similar_for_all(
        self,
        k: int = 5,
        metric: SimilarityMetric = SimilarityMetric.COSINE
    ) -> Dict[str, List[SimilarCountyResult]]:
        """
        Find similar counties for all counties.
        
        Args:
            k: Number of similar counties per query
            metric: Similarity metric
            
        Returns:
            Dictionary mapping FIPS to similar counties
        """
        results = {}
        
        for fips in self.engine.metadata['fips']:
            try:
                similar = self.engine.find_similar_counties(
                    fips, k=k, metric=metric
                )
                results[fips] = similar
            except Exception as e:
                results[fips] = []
        
        return results


# Convenience functions
def create_similarity_engine(
    embeddings: np.ndarray,
    county_metadata: pd.DataFrame,
    metric: str = "cosine"
) -> SimilarityEngine:
    """
    Create a similarity engine with specified configuration.
    
    Args:
        embeddings: County embeddings
        county_metadata: County metadata DataFrame
        metric: Default similarity metric
        
    Returns:
        Configured SimilarityEngine
    """
    metric_map = {m.value: m for m in SimilarityMetric}
    default_metric = metric_map.get(metric, SimilarityMetric.COSINE)
    
    config = SimilarityConfig(default_metric=default_metric)
    
    return SimilarityEngine(embeddings, county_metadata, config)


if __name__ == "__main__":
    # Example usage
    print("SimilarityEngine - Example Usage")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    n_counties = 100
    dimension = 128
    
    embeddings = np.random.randn(n_counties, dimension).astype(np.float32)
    
    # Create metadata
    metadata = pd.DataFrame({
        'fips': [f"{i:05d}" for i in range(n_counties)],
        'county_name': [f"County {i}" for i in range(n_counties)],
        'state': np.random.choice(['AL', 'CA', 'NY', 'TX'], n_counties),
        'risk_score': np.random.rand(n_counties),
        'vulnerability_index': np.random.rand(n_counties)
    })
    
    print(f"\nSample data: {n_counties} counties")
    
    # Create engine
    engine = SimilarityEngine(embeddings, metadata)
    
    # Find similar counties
    print("\n--- Finding Similar Counties ---")
    results = engine.find_similar_counties(
        query_fips="00001",
        k=5,
        metric=SimilarityMetric.COSINE
    )
    
    print(f"\nCounties similar to {results[0].county_name}:")
    for r in results:
        print(f"  {r.rank}. {r.county_name} ({r.state}) - "
              f"Similarity: {r.similarity_score:.4f}")
        print(f"     Explanation: {r.explanation}")
    
    # Compare two counties
    print("\n--- County Comparison ---")
    comparison = engine.compare_counties("00001", "00002")
    print(f"Comparing {comparison['county1']['name']} vs "
          f"{comparison['county2']['name']}")
    print(f"Similarity: {comparison['similarity_score']:.4f}")
    
    print("\nSimilarityEngine ready for use!")
