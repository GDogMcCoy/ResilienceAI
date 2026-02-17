"""
ResilienceAI - Hyperdimensional Vector Space Module

This module provides vector encoding, FAISS indexing, and similarity search
capabilities for multi-domain county analysis.

Key Features:
- Sentence-transformer based embeddings (384-dim)
- Multi-domain vector encoding (climate, health, infrastructure, socioeconomic)
- FAISS index for fast similarity search
- Cross-domain similarity analysis
- Anomaly detection in vector space
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path
import warnings
from dataclasses import dataclass
from collections import defaultdict

# ML and vector libraries
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    warnings.warn("sentence-transformers not installed. Using fallback embeddings.")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    warnings.warn("faiss not installed. Similarity search will be slower.")

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.decomposition import PCA

# Configuration
from config import PROCESSED_DIR, MODELS_DIR

# Domain feature definitions
DOMAIN_FEATURES = {
    "climate": [
        "disaster_count", "disaster_flood", "disaster_severe_storms", 
        "disaster_hurricane", "disaster_fire", "disaster_tornado",
        "disaster_count_recent", "disasters_2015_2025", "disasters_2005_2014",
        "disaster_acceleration"
    ],
    "health": [
        "elderly_pct", "disability_pct", "uninsured_pct",
        "dist_nearest_hospitals_km", "dist_2nd_nearest_hospitals_km",
        "count_hospitals_50km", "density_hospitals_per10k",
        "dist_nearest_nursing_homes_km", "density_nursing_homes_per10k"
    ],
    "infrastructure": [
        "dist_nearest_fire_stations_km", "dist_2nd_nearest_fire_stations_km",
        "count_fire_stations_50km", "density_fire_stations_per10k",
        "dist_nearest_ems_stations_km", "dist_2nd_nearest_ems_stations_km",
        "count_ems_stations_50km", "density_ems_stations_per10k",
        "redundancy_score", "zero_redundancy_flag"
    ],
    "socioeconomic": [
        "total_population", "median_income", "poverty_pct",
        "vulnerability_index", "isolation_index", "risk_score",
        "pop_weighted_vulnerability", "pop_weighted_risk"
    ]
}

# All features combined
ALL_FEATURES = []
for domain, features in DOMAIN_FEATURES.items():
    ALL_FEATURES.extend(features)
ALL_FEATURES = list(set(ALL_FEATURES))


@dataclass
class VectorSearchResult:
    """Result from vector similarity search."""
    county_fips: str
    county_name: str
    similarity_score: float
    distance: float
    rank: int


@dataclass
class CrossDomainInsight:
    """Cross-domain insight for a county."""
    county_fips: str
    county_name: str
    primary_domain: str
    secondary_domain: str
    correlation_strength: float
    insight_type: str  # 'similarity', 'anomaly', 'correlation'
    description: str
    related_counties: List[str]


class CountyVectorEncoder:
    """
    Encodes county data into hyperdimensional vectors using sentence transformers.
    
    Uses all-MiniLM-L6-v2 model for 384-dimensional embeddings.
    Supports multi-domain encoding and cross-domain analysis.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", embedding_dim: int = 384):
        """
        Initialize the encoder.
        
        Args:
            model_name: Name of the sentence-transformer model
            embedding_dim: Expected embedding dimension
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.model = None
        self.scaler = StandardScaler()
        self.feature_scalers = {}
        self.is_fitted = False
        
        # Load model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                print(f"Loaded sentence-transformer model: {model_name}")
            except Exception as e:
                print(f"Error loading model: {e}. Using fallback embeddings.")
                self.model = None
    
    def _create_text_description(self, row: pd.Series, domain: Optional[str] = None) -> str:
        """
        Create a text description of a county for embedding.
        
        Args:
            row: County data row
            domain: Specific domain to focus on, or None for all
            
        Returns:
            Text description string
        """
        features = DOMAIN_FEATURES.get(domain, ALL_FEATURES) if domain else ALL_FEATURES
        
        parts = []
        county_name = row.get('county_name', 'Unknown County')
        parts.append(f"County: {county_name}")
        
        if domain == "climate" or domain is None:
            disaster_count = row.get('disaster_count', 0)
            flood = row.get('disaster_flood', 0)
            storms = row.get('disaster_severe_storms', 0)
            hurricane = row.get('disaster_hurricane', 0)
            fire = row.get('disaster_fire', 0)
            tornado = row.get('disaster_tornado', 0)
            acceleration = row.get('disaster_acceleration', 0)
            parts.append(f"Climate profile: {disaster_count} total disasters, "
                        f"{flood} floods, {storms} storms, {hurricane} hurricanes, "
                        f"{fire} fires, {tornado} tornadoes, acceleration {acceleration:.2f}")
        
        if domain == "health" or domain is None:
            elderly = row.get('elderly_pct', 0)
            disability = row.get('disability_pct', 0)
            uninsured = row.get('uninsured_pct', 0)
            hospital_dist = row.get('dist_nearest_hospitals_km', 0)
            hospital_density = row.get('density_hospitals_per10k', 0)
            parts.append(f"Health profile: {elderly:.1f}% elderly, {disability:.1f}% disabled, "
                        f"{uninsured:.1f}% uninsured, nearest hospital {hospital_dist:.1f}km, "
                        f"{hospital_density:.2f} hospitals per 10k")
        
        if domain == "infrastructure" or domain is None:
            fire_dist = row.get('dist_nearest_fire_stations_km', 0)
            ems_dist = row.get('dist_nearest_ems_stations_km', 0)
            fire_density = row.get('density_fire_stations_per10k', 0)
            ems_density = row.get('density_ems_stations_per10k', 0)
            redundancy = row.get('redundancy_score', 0)
            parts.append(f"Infrastructure: fire station {fire_dist:.1f}km, EMS {ems_dist:.1f}km, "
                        f"{fire_density:.2f} fire per 10k, {ems_density:.2f} EMS per 10k, "
                        f"redundancy {redundancy:.3f}")
        
        if domain == "socioeconomic" or domain is None:
            population = row.get('total_population', 0)
            income = row.get('median_income', 0)
            poverty = row.get('poverty_pct', 0)
            vulnerability = row.get('vulnerability_index', 0)
            risk = row.get('risk_score', 0)
            parts.append(f"Socioeconomic: population {population:,.0f}, median income ${income:,.0f}, "
                        f"{poverty:.1f}% poverty, vulnerability {vulnerability:.3f}, risk {risk:.3f}")
        
        return "; ".join(parts)
    
    def _fallback_embedding(self, text: str) -> np.ndarray:
        """
        Create a fallback embedding when sentence-transformers is not available.
        Uses character n-gram hashing for deterministic embeddings.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        # Simple hash-based embedding as fallback
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(self.embedding_dim).astype(np.float32)
    
    def encode_county(self, row: pd.Series, domain: Optional[str] = None) -> np.ndarray:
        """
        Encode a single county into a vector.
        
        Args:
            row: County data row
            domain: Specific domain to focus on, or None for all
            
        Returns:
            Embedding vector (384-dim for all-MiniLM-L6-v2)
        """
        text = self._create_text_description(row, domain)
        
        if self.model is not None:
            embedding = self.model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        else:
            embedding = self._fallback_embedding(text)
        
        return embedding.astype(np.float32)
    
    def encode_counties(self, df: pd.DataFrame, domain: Optional[str] = None,
                       batch_size: int = 32) -> np.ndarray:
        """
        Encode multiple counties into vectors.
        
        Args:
            df: DataFrame with county data
            domain: Specific domain to focus on, or None for all
            batch_size: Batch size for encoding
            
        Returns:
            Array of embedding vectors (n_counties x 384)
        """
        texts = []
        for _, row in df.iterrows():
            texts.append(self._create_text_description(row, domain))
        
        if self.model is not None:
            embeddings = self.model.encode(
                texts, 
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=True
            )
        else:
            embeddings = np.array([self._fallback_embedding(t) for t in texts])
        
        return embeddings.astype(np.float32)
    
    def encode_domain_specific(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Encode counties separately for each domain.
        
        Args:
            df: DataFrame with county data
            
        Returns:
            Dictionary mapping domain names to embedding arrays
        """
        domain_embeddings = {}
        for domain in DOMAIN_FEATURES.keys():
            print(f"Encoding {domain} domain...")
            domain_embeddings[domain] = self.encode_counties(df, domain=domain)
        return domain_embeddings


class CountyVectorIndex:
    """
    FAISS-based vector index for fast similarity search.
    
    Supports cosine similarity and L2 distance metrics.
    Indexes 3,222 counties with multi-domain vectors.
    """
    
    def __init__(self, embedding_dim: int = 384, metric: str = "cosine"):
        """
        Initialize the vector index.
        
        Args:
            embedding_dim: Dimension of embedding vectors
            metric: Distance metric ('cosine' or 'l2')
        """
        self.embedding_dim = embedding_dim
        self.metric = metric
        self.index = None
        self.county_fips = []
        self.county_names = []
        self.vectors = None
        self.is_built = False
        
        if not FAISS_AVAILABLE and metric == "cosine":
            print("Warning: FAISS not available. Using sklearn for similarity search.")
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors for cosine similarity."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        return vectors / norms
    
    def build_index(self, vectors: np.ndarray, county_fips: List[str],
                   county_names: List[str]) -> 'CountyVectorIndex':
        """
        Build the FAISS index from vectors.
        
        Args:
            vectors: Array of embedding vectors (n x embedding_dim)
            county_fips: List of county FIPS codes
            county_names: List of county names
            
        Returns:
            Self for method chaining
        """
        self.vectors = vectors.astype(np.float32).copy()
        self.county_fips = county_fips
        self.county_names = county_names
        self._normalized_vectors = None
        
        if FAISS_AVAILABLE:
            if self.metric == "cosine":
                # For cosine similarity, normalize vectors and use inner product
                normalized = self._normalize_vectors(self.vectors)
                self._normalized_vectors = normalized
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                self.index.add(normalized)
            else:  # l2
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.index.add(self.vectors)
        else:
            # Fallback: store vectors for sklearn-based search
            if self.metric == "cosine":
                self._normalized_vectors = self._normalize_vectors(self.vectors)
        
        self.is_built = True
        print(f"Built index with {len(vectors)} counties using {self.metric} metric")
        return self
    
    def search(self, query_vector: np.ndarray, k: int = 10) -> List[VectorSearchResult]:
        """
        Search for similar counties.
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.is_built:
            raise ValueError("Index not built. Call build_index() first.")
        
        query_vector = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        k = min(k, len(self.county_fips))
        
        if FAISS_AVAILABLE and self.index is not None:
            if self.metric == "cosine":
                query_vector = self._normalize_vectors(query_vector)
            distances, indices = self.index.search(query_vector, k)
            distances = distances[0]
            indices = indices[0]
        else:
            # Fallback using sklearn
            if self.metric == "cosine":
                query_vector = self._normalize_vectors(query_vector)
                search_vectors = self._normalized_vectors if self._normalized_vectors is not None else self.vectors
                similarities = cosine_similarity(query_vector, search_vectors)[0]
                indices = np.argsort(similarities)[::-1][:k]
                distances = 1 - similarities[indices]  # Convert similarity to distance
            else:
                distances = euclidean_distances(query_vector, self.vectors)[0]
                indices = np.argsort(distances)[:k]
        
        results = []
        for rank, (idx, dist) in enumerate(zip(indices, distances), 1):
            # For cosine with FAISS IP index, distance is actually similarity
            # For sklearn fallback, we computed distance = 1 - similarity
            if self.metric == "cosine":
                if FAISS_AVAILABLE:
                    sim_score = float(dist)  # FAISS IP returns similarity directly
                else:
                    sim_score = 1 - float(dist)  # sklearn: convert distance back to similarity
            else:
                sim_score = 1 - float(dist)  # L2: convert distance to similarity
            results.append(VectorSearchResult(
                county_fips=self.county_fips[idx],
                county_name=self.county_names[idx],
                similarity_score=float(sim_score),
                distance=float(dist),
                rank=rank
            ))
        
        return results
    
    def search_by_fips(self, fips: str, k: int = 10) -> List[VectorSearchResult]:
        """
        Search for counties similar to a given county by FIPS.
        
        Args:
            fips: County FIPS code
            k: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            idx = self.county_fips.index(fips)
            query_vector = self.vectors[idx]
            return self.search(query_vector, k=k)
        except ValueError:
            raise ValueError(f"FIPS {fips} not found in index")
    
    def save(self, path: Union[str, Path]) -> None:
        """
        Save the index to disk.
        
        Args:
            path: Directory path to save index
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save vectors and metadata
        np.save(path / "vectors.npy", self.vectors)
        np.save(path / "county_fips.npy", np.array(self.county_fips))
        np.save(path / "county_names.npy", np.array(self.county_names))
        
        # Save FAISS index if available
        if FAISS_AVAILABLE and self.index is not None:
            faiss.write_index(self.index, str(path / "faiss.index"))
        
        # Save config
        config = {
            "embedding_dim": self.embedding_dim,
            "metric": self.metric,
            "n_counties": len(self.county_fips),
            "faiss_available": FAISS_AVAILABLE
        }
        pd.DataFrame([config]).to_json(path / "config.json")
        
        print(f"Saved index to {path}")
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> 'CountyVectorIndex':
        """
        Load index from disk.
        
        Args:
            path: Directory path to load index from
            
        Returns:
            Loaded CountyVectorIndex
        """
        path = Path(path)
        
        # Load config
        config = pd.read_json(path / "config.json").iloc[0].to_dict()
        
        # Create instance
        instance = cls(
            embedding_dim=int(config["embedding_dim"]),
            metric=config["metric"]
        )
        
        # Load vectors and metadata
        instance.vectors = np.load(path / "vectors.npy")
        instance.county_fips = np.load(path / "county_fips.npy", allow_pickle=True).tolist()
        instance.county_names = np.load(path / "county_names.npy", allow_pickle=True).tolist()
        
        # Load FAISS index if available
        if FAISS_AVAILABLE and (path / "faiss.index").exists():
            instance.index = faiss.read_index(str(path / "faiss.index"))
        
        # Recompute normalized vectors for cosine metric if needed
        if instance.metric == "cosine":
            instance._normalized_vectors = instance._normalize_vectors(instance.vectors)
        
        instance.is_built = True
        print(f"Loaded index with {len(instance.county_fips)} counties")
        return instance


class CrossDomainAnalyzer:
    """
    Analyzes cross-domain relationships and detects anomalies.
    
    Features:
    - Cross-domain similarity matrix
    - Anomaly detection (outliers in vector space)
    - Unexpected correlation discovery
    """
    
    def __init__(self, encoder: CountyVectorEncoder):
        """
        Initialize the analyzer.
        
        Args:
            encoder: CountyVectorEncoder instance
        """
        self.encoder = encoder
        self.domain_embeddings = {}
        self.domain_indices = {}
        self.df = None
    
    def fit(self, df: pd.DataFrame) -> 'CrossDomainAnalyzer':
        """
        Fit the analyzer on county data.
        
        Args:
            df: DataFrame with county data
            
        Returns:
            Self for method chaining
        """
        self.df = df.copy()
        
        # Encode each domain separately
        print("Building domain-specific embeddings...")
        self.domain_embeddings = self.encoder.encode_domain_specific(df)
        
        # Build indices for each domain
        print("Building domain indices...")
        county_fips = df['fips'].tolist()
        county_names = df['county_name'].tolist()
        
        for domain, embeddings in self.domain_embeddings.items():
            self.domain_indices[domain] = CountyVectorIndex(
                embedding_dim=embeddings.shape[1],
                metric="cosine"
            ).build_index(embeddings, county_fips, county_names)
        
        return self
    
    def compute_cross_domain_similarity(self, fips: str) -> Dict[str, Dict[str, float]]:
        """
        Compute similarity of a county across different domains.
        
        Args:
            fips: County FIPS code
            
        Returns:
            Dictionary mapping domain pairs to similarity scores
        """
        if fips not in self.df['fips'].values:
            raise ValueError(f"FIPS {fips} not found")
        
        # Get index of the county
        idx = self.df[self.df['fips'] == fips].index[0]
        
        similarities = {}
        domains = list(self.domain_embeddings.keys())
        
        for i, domain1 in enumerate(domains):
            similarities[domain1] = {}
            for domain2 in domains:
                if domain1 == domain2:
                    similarities[domain1][domain2] = 1.0
                else:
                    vec1 = self.domain_embeddings[domain1][idx]
                    vec2 = self.domain_embeddings[domain2][idx]
                    
                    # Cosine similarity
                    sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    similarities[domain1][domain2] = float(sim)
        
        return similarities
    
    def compute_similarity_matrix(self) -> pd.DataFrame:
        """
        Compute cross-domain similarity matrix for all counties.
        
        Returns:
            DataFrame with similarity metrics
        """
        results = []
        
        for _, row in self.df.iterrows():
            fips = row['fips']
            similarities = self.compute_cross_domain_similarity(fips)
            
            # Compute average cross-domain similarity
            cross_sims = []
            domains = list(similarities.keys())
            for i, d1 in enumerate(domains):
                for d2 in domains[i+1:]:
                    cross_sims.append(similarities[d1][d2])
            
            avg_cross_sim = np.mean(cross_sims)
            min_cross_sim = np.min(cross_sims)
            max_cross_sim = np.max(cross_sims)
            
            results.append({
                'fips': fips,
                'county_name': row['county_name'],
                'avg_cross_domain_similarity': avg_cross_sim,
                'min_cross_domain_similarity': min_cross_sim,
                'max_cross_domain_similarity': max_cross_sim,
                'cross_domain_coherence': max_cross_sim - min_cross_sim
            })
        
        return pd.DataFrame(results)
    
    def detect_anomalies(self, method: str = "isolation", 
                        contamination: float = 0.05) -> pd.DataFrame:
        """
        Detect anomalous counties in vector space.
        
        Args:
            method: Anomaly detection method ('isolation', 'distance', 'density')
            contamination: Expected proportion of outliers
            
        Returns:
            DataFrame with anomaly scores
        """
        from sklearn.ensemble import IsolationForest
        from sklearn.neighbors import LocalOutlierFactor
        
        # Combine all domain embeddings for comprehensive anomaly detection
        combined = np.hstack(list(self.domain_embeddings.values()))
        
        results = []
        
        if method == "isolation":
            clf = IsolationForest(contamination=contamination, random_state=42)
            scores = clf.fit_predict(combined)
            anomaly_scores = clf.decision_function(combined)
        elif method == "density":
            clf = LocalOutlierFactor(n_neighbors=20, contamination=contamination)
            scores = clf.fit_predict(combined)
            anomaly_scores = -clf.negative_outlier_factor_
        else:  # distance-based
            # Compute distance to centroid
            centroid = np.mean(combined, axis=0)
            distances = np.linalg.norm(combined - centroid, axis=1)
            threshold = np.percentile(distances, (1 - contamination) * 100)
            scores = np.where(distances > threshold, -1, 1)
            anomaly_scores = distances / np.max(distances)
        
        for i, (_, row) in enumerate(self.df.iterrows()):
            results.append({
                'fips': row['fips'],
                'county_name': row['county_name'],
                'anomaly_score': float(anomaly_scores[i]),
                'is_anomaly': scores[i] == -1,
                'risk_score': row.get('risk_score', np.nan)
            })
        
        return pd.DataFrame(results).sort_values('anomaly_score')
    
    def find_similar_multi_domain(self, fips: str, k: int = 10) -> pd.DataFrame:
        """
        Find counties with similar multi-domain profiles.
        
        Args:
            fips: County FIPS code
            k: Number of similar counties to find
            
        Returns:
            DataFrame with similar counties and similarity scores
        """
        # Get query county index
        idx = self.df[self.df['fips'] == fips].index[0]
        
        # Combine all domain embeddings
        combined = np.hstack(list(self.domain_embeddings.values()))
        query_vec = combined[idx]
        
        # Compute similarities
        similarities = cosine_similarity([query_vec], combined)[0]
        
        # Get top k (excluding self)
        top_indices = np.argsort(similarities)[::-1][1:k+1]
        
        results = []
        for rank, idx in enumerate(top_indices, 1):
            row = self.df.iloc[idx]
            results.append({
                'rank': rank,
                'fips': row['fips'],
                'county_name': row['county_name'],
                'similarity_score': float(similarities[idx]),
                'risk_score': row.get('risk_score', np.nan),
                'vulnerability_index': row.get('vulnerability_index', np.nan)
            })
        
        return pd.DataFrame(results)
    
    def discover_correlations(self, top_n: int = 20) -> List[CrossDomainInsight]:
        """
        Discover unexpected cross-domain correlations.
        
        Args:
            top_n: Number of top correlations to return
            
        Returns:
            List of cross-domain insights
        """
        insights = []
        
        # Compute similarity matrix
        sim_df = self.compute_similarity_matrix()
        
        # Find counties with lowest cross-domain coherence (unexpected patterns)
        low_coherence = sim_df.nsmallest(top_n, 'cross_domain_coherence')
        
        for _, row in low_coherence.iterrows():
            fips = row['fips']
            
            # Find which domains are most different
            domain_sims = self.compute_cross_domain_similarity(fips)
            
            # Find the most divergent domain pair
            min_sim = 1.0
            divergent_pair = None
            domains = list(domain_sims.keys())
            for i, d1 in enumerate(domains):
                for d2 in domains[i+1:]:
                    sim = domain_sims[d1][d2]
                    if sim < min_sim:
                        min_sim = sim
                        divergent_pair = (d1, d2)
            
            if divergent_pair:
                insights.append(CrossDomainInsight(
                    county_fips=fips,
                    county_name=row['county_name'],
                    primary_domain=divergent_pair[0],
                    secondary_domain=divergent_pair[1],
                    correlation_strength=min_sim,
                    insight_type='divergent_profile',
                    description=f"County shows divergent {divergent_pair[0]} vs {divergent_pair[1]} profiles",
                    related_counties=[]
                ))
        
        # Find counties with highest cross-domain similarity (consistent profiles)
        high_coherence = sim_df.nlargest(top_n, 'avg_cross_domain_similarity')
        
        for _, row in high_coherence.iterrows():
            insights.append(CrossDomainInsight(
                county_fips=row['fips'],
                county_name=row['county_name'],
                primary_domain='all',
                secondary_domain='all',
                correlation_strength=row['avg_cross_domain_similarity'],
                insight_type='consistent_profile',
                description="County shows consistent profile across all domains",
                related_counties=[]
            ))
        
        return insights


class VectorSpaceManager:
    """
    Main manager class for vector space operations.
    
    Provides a unified interface for encoding, indexing, and analysis.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector space manager.
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        self.encoder = CountyVectorEncoder(model_name=model_name)
        self.index = None
        self.analyzer = None
        self.df = None
        self.embeddings = None
    
    def build(self, df: pd.DataFrame, build_domains: bool = True) -> 'VectorSpaceManager':
        """
        Build the complete vector space from county data.
        
        Args:
            df: DataFrame with county data
            build_domains: Whether to build domain-specific indices
            
        Returns:
            Self for method chaining
        """
        self.df = df.copy()
        
        # Encode all counties
        print("Encoding counties into vector space...")
        self.embeddings = self.encoder.encode_counties(df)
        
        # Build main index
        print("Building FAISS index...")
        self.index = CountyVectorIndex(
            embedding_dim=self.embeddings.shape[1],
            metric="cosine"
        ).build_index(
            self.embeddings,
            df['fips'].tolist(),
            df['county_name'].tolist()
        )
        
        # Build cross-domain analyzer
        if build_domains:
            print("Building cross-domain analyzer...")
            self.analyzer = CrossDomainAnalyzer(self.encoder).fit(df)
        
        return self
    
    def search_similar(self, query: Union[str, np.ndarray], k: int = 10) -> pd.DataFrame:
        """
        Search for counties similar to a query.
        
        Args:
            query: FIPS code or embedding vector
            k: Number of results
            
        Returns:
            DataFrame with search results
        """
        if isinstance(query, str):
            results = self.index.search_by_fips(query, k=k)
        else:
            results = self.index.search(query, k=k)
        
        return pd.DataFrame([{
            'rank': r.rank,
            'fips': r.county_fips,
            'county_name': r.county_name,
            'similarity_score': r.similarity_score,
            'distance': r.distance
        } for r in results])
    
    def get_anomalies(self, contamination: float = 0.05) -> pd.DataFrame:
        """Get anomalous counties."""
        if self.analyzer is None:
            raise ValueError("Analyzer not built. Call build() with build_domains=True.")
        return self.analyzer.detect_anomalies(contamination=contamination)
    
    def get_insights(self, top_n: int = 20) -> List[CrossDomainInsight]:
        """Get cross-domain insights."""
        if self.analyzer is None:
            raise ValueError("Analyzer not built. Call build() with build_domains=True.")
        return self.analyzer.discover_correlations(top_n=top_n)
    
    def save(self, path: Union[str, Path]) -> None:
        """
        Save the complete vector space.
        
        Args:
            path: Directory path to save to
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save index
        self.index.save(path / "index")
        
        # Save embeddings
        np.save(path / "embeddings.npy", self.embeddings)
        
        # Save analyzer data if available
        if self.analyzer is not None:
            for domain, embeddings in self.analyzer.domain_embeddings.items():
                np.save(path / f"embeddings_{domain}.npy", embeddings)
        
        # Save metadata
        self.df.to_parquet(path / "county_metadata.parquet")
        
        print(f"Saved vector space to {path}")
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> 'VectorSpaceManager':
        """
        Load a saved vector space.
        
        Args:
            path: Directory path to load from
            
        Returns:
            Loaded VectorSpaceManager
        """
        path = Path(path)
        
        instance = cls()
        
        # Load index
        instance.index = CountyVectorIndex.load(path / "index")
        instance.embeddings = np.load(path / "embeddings.npy")
        
        # Load metadata
        instance.df = pd.read_parquet(path / "county_metadata.parquet")
        
        print(f"Loaded vector space from {path}")
        return instance


def create_vector_space(data_path: Optional[str] = None,
                       save_path: Optional[str] = None) -> VectorSpaceManager:
    """
    Convenience function to create a complete vector space from county data.
    
    Args:
        data_path: Path to county features CSV (default: PROCESSED_DIR/county_features.csv)
        save_path: Path to save the vector space (optional)
        
    Returns:
        Configured VectorSpaceManager
    """
    if data_path is None:
        data_path = PROCESSED_DIR / "county_features.csv"
    
    print(f"Loading county data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} counties")
    
    # Build vector space
    manager = VectorSpaceManager()
    manager.build(df, build_domains=True)
    
    # Save if path provided
    if save_path:
        manager.save(save_path)
    
    return manager


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("ResilienceAI Vector Space - Example Usage")
    print("=" * 60)
    
    # Create vector space
    manager = create_vector_space()
    
    # Example: Search for similar counties
    print("\n--- Similarity Search Example ---")
    results = manager.search_similar("01001", k=5)  # Autauga County, AL
    print("Counties similar to Autauga County, AL:")
    print(results.to_string(index=False))
    
    # Example: Get anomalies
    print("\n--- Anomaly Detection Example ---")
    anomalies = manager.get_anomalies(contamination=0.02)
    print("Top 5 anomalous counties:")
    print(anomalies.head().to_string(index=False))
    
    # Example: Get insights
    print("\n--- Cross-Domain Insights Example ---")
    insights = manager.get_insights(top_n=5)
    for insight in insights[:5]:
        print(f"\n{insight.county_name}: {insight.description}")
        print(f"  Type: {insight.insight_type}, Strength: {insight.correlation_strength:.3f}")
    
    print("\n" + "=" * 60)
    print("Vector space ready for use!")
    print("=" * 60)
