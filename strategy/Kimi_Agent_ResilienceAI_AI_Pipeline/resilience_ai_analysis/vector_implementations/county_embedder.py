"""
Enhanced County Embedding Generator for ResilienceAI

This module provides advanced county embedding generation with multi-modal support,
multiple embedding models, and configurable fusion strategies.

Author: Vector Embedding Specialist
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
import warnings

# Optional imports with fallbacks
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    warnings.warn("sentence-transformers not installed. Using fallback embeddings.")


class EmbeddingModel(str, Enum):
    """Supported embedding models with their characteristics."""
    # Fast models (384-dim)
    MINILM_L6 = "all-MiniLM-L6-v2"
    MINILM_L12 = "all-MiniLM-L12-v2"
    E5_SMALL = "intfloat/e5-small-v2"
    GTE_SMALL = "thenlper/gte-small"
    BGE_SMALL = "BAAI/bge-small-en"
    
    # High quality models (768-dim)
    MPNET_BASE = "all-mpnet-base-v2"
    DISTILBERT = "distilbert-base-nli-stsb-mean-tokens"
    E5_BASE = "intfloat/e5-base-v2"
    GTE_BASE = "thenlper/gte-base"
    BGE_BASE = "BAAI/bge-base-en"
    INSTRUCTOR = "hkunlp/instructor-base"
    
    # Multilingual models
    MULTILINGUAL = "paraphrase-multilingual-MiniLM-L12-v2"
    E5_MULTILINGUAL = "intfloat/multilingual-e5-base"


class EmbeddingDomain(str, Enum):
    """Embedding domains for county data."""
    CLIMATE = "climate"
    HEALTH = "health"
    INFRASTRUCTURE = "infrastructure"
    SOCIOECONOMIC = "socioeconomic"
    AGRICULTURE = "agriculture"
    TRANSPORTATION = "transportation"
    COMMUNICATIONS = "communications"
    ENVIRONMENTAL = "environmental"
    ALL = "all"


@dataclass
class CountyEmbeddingConfig:
    """Configuration for county embedding generation."""
    model: EmbeddingModel = EmbeddingModel.MPNET_BASE
    embedding_dim: int = 768
    batch_size: int = 32
    normalize: bool = True
    include_metadata: bool = True
    cache_enabled: bool = True
    multi_modal: bool = True
    numeric_embedding_dim: int = 128
    geographic_embedding_dim: int = 64
    temporal_embedding_dim: int = 32
    device: str = "cpu"
    
    # Domain feature definitions
    domain_features: Dict[str, List[str]] = field(default_factory=lambda: {
        "climate": [
            "disaster_count", "disaster_flood", "disaster_severe_storms",
            "disaster_hurricane", "disaster_fire", "disaster_tornado",
            "disaster_drought", "disaster_winter_storm",
            "disaster_acceleration", "disaster_trend"
        ],
        "health": [
            "elderly_pct", "disability_pct", "uninsured_pct",
            "dist_nearest_hospitals_km", "density_hospitals_per10k",
            "dist_nearest_nursing_homes_km", "density_nursing_homes_per10k",
            "icu_beds_per_1000"
        ],
        "infrastructure": [
            "dist_nearest_fire_stations_km", "dist_nearest_ems_stations_km",
            "density_fire_stations_per10k", "density_ems_stations_per10k",
            "redundancy_score", "power_grid_resilience",
            "water_system_age", "bridge_condition_score"
        ],
        "socioeconomic": [
            "total_population", "median_income", "poverty_pct",
            "unemployment_rate", "education_index",
            "vulnerability_index", "risk_score"
        ],
        "agriculture": [
            "farmland_pct", "crop_diversity_index",
            "irrigation_coverage", "agricultural_drought_vulnerability"
        ]
    })


class CountyEmbedder:
    """
    Advanced county embedding generator with multi-modal support.
    
    Features:
    - Multiple embedding model support (MiniLM, MPNet, E5, GTE, BGE)
    - Multi-modal fusion (text + numeric + geographic + temporal)
    - Configurable embedding dimensions
    - Built-in caching support
    - Incremental embedding updates
    - Domain-specific encoding
    
    Example:
        >>> config = CountyEmbeddingConfig(model=EmbeddingModel.MPNET_BASE)
        >>> embedder = CountyEmbedder(config)
        >>> embedding = embedder.generate_text_embedding(county_data)
        >>> multi_modal = embedder.generate_multi_modal_embedding(county_data)
    """
    
    def __init__(self, config: Optional[CountyEmbeddingConfig] = None):
        """
        Initialize the county embedder.
        
        Args:
            config: Configuration object. Uses defaults if not provided.
        """
        self.config = config or CountyEmbeddingConfig()
        self.text_encoder = None
        self.numeric_encoder = None
        self.geo_encoder = None
        self.temporal_encoder = None
        self._is_initialized = False
        
        self._load_models()
        
    def _load_models(self):
        """Load embedding models based on configuration."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("Warning: sentence-transformers not available. Using fallback.")
            return
        
        try:
            # Load text encoder
            print(f"Loading embedding model: {self.config.model.value}")
            self.text_encoder = SentenceTransformer(
                self.config.model.value,
                device=self.config.device
            )
            self._is_initialized = True
        except Exception as e:
            print(f"Error loading model: {e}. Using fallback embeddings.")
            self.text_encoder = None
    
    def generate_text_embedding(
        self, 
        county_data: pd.Series,
        domain: EmbeddingDomain = EmbeddingDomain.ALL
    ) -> np.ndarray:
        """
        Generate text-based embedding from county description.
        
        Args:
            county_data: County data row (pandas Series)
            domain: Specific domain to focus on, or ALL for comprehensive
            
        Returns:
            Text embedding vector (numpy array)
            
        Raises:
            ValueError: If text encoder is not available
        """
        if self.text_encoder is None:
            return self._fallback_embedding(county_data)
        
        description = self._create_enhanced_description(county_data, domain)
        
        embedding = self.text_encoder.encode(
            description,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=self.config.normalize,
            batch_size=1
        )
        
        return embedding.astype(np.float32)
    
    def generate_numeric_embedding(self, county_data: pd.Series) -> np.ndarray:
        """
        Generate numeric feature embedding.
        
        Args:
            county_data: County data row
            
        Returns:
            Numeric embedding vector
        """
        numeric_features = self._extract_numeric_features(county_data)
        
        # Simple projection for now (can be replaced with neural network)
        np.random.seed(42)
        projection = np.random.randn(
            len(numeric_features),
            self.config.numeric_embedding_dim
        )
        
        embedding = np.dot(numeric_features, projection)
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        return embedding.astype(np.float32)
    
    def generate_geographic_embedding(self, county_data: pd.Series) -> np.ndarray:
        """
        Generate geographic embedding from coordinates.
        
        Args:
            county_data: County data row with lat/lon
            
        Returns:
            Geographic embedding vector
        """
        lat = county_data.get('latitude', county_data.get('centroid_lat', 0))
        lon = county_data.get('longitude', county_data.get('centroid_lon', 0))
        
        # Sinusoidal encoding (similar to positional encoding)
        position = np.array([lat, lon])
        div_term = np.exp(
            np.arange(0, self.config.geographic_embedding_dim // 2, 2) * 
            -(np.log(10000.0) / (self.config.geographic_embedding_dim // 2))
        )
        
        pe = np.zeros(self.config.geographic_embedding_dim)
        pe[0::4] = np.sin(position[0] * div_term[:len(pe[0::4])])
        pe[1::4] = np.cos(position[0] * div_term[:len(pe[1::4])])
        pe[2::4] = np.sin(position[1] * div_term[:len(pe[2::4])])
        pe[3::4] = np.cos(position[1] * div_term[:len(pe[3::4])])
        
        # Normalize
        pe = pe / (np.linalg.norm(pe) + 1e-8)
        
        return pe.astype(np.float32)
    
    def generate_temporal_embedding(self, county_data: pd.Series) -> np.ndarray:
        """
        Generate temporal embedding from time-series features.
        
        Args:
            county_data: County data row with temporal features
            
        Returns:
            Temporal embedding vector
        """
        temporal_features = self._extract_temporal_features(county_data)
        
        # Pad or truncate to output_dim
        features = np.array(temporal_features)
        if len(features) < self.config.temporal_embedding_dim:
            features = np.pad(
                features,
                (0, self.config.temporal_embedding_dim - len(features))
            )
        else:
            features = features[:self.config.temporal_embedding_dim]
        
        return features.astype(np.float32)
    
    def generate_multi_modal_embedding(
        self,
        county_data: pd.Series,
        domain: EmbeddingDomain = EmbeddingDomain.ALL,
        fusion_method: str = "concatenate"
    ) -> np.ndarray:
        """
        Generate multi-modal embedding combining all modalities.
        
        Args:
            county_data: County data row
            domain: Specific domain or ALL
            fusion_method: "concatenate", "weighted_sum", or "attention"
            
        Returns:
            Combined multi-modal embedding
        """
        # Generate individual embeddings
        text_emb = self.generate_text_embedding(county_data, domain)
        numeric_emb = self.generate_numeric_embedding(county_data)
        geo_emb = self.generate_geographic_embedding(county_data)
        temporal_emb = self.generate_temporal_embedding(county_data)
        
        # Fuse embeddings
        if fusion_method == "concatenate":
            combined = np.concatenate([
                text_emb,
                numeric_emb,
                geo_emb,
                temporal_emb
            ])
        elif fusion_method == "weighted_sum":
            combined = self._weighted_fusion(
                text_emb, numeric_emb, geo_emb, temporal_emb
            )
        elif fusion_method == "average":
            # Resize all to text embedding dimension
            target_dim = len(text_emb)
            combined = (
                text_emb +
                self._resize_vector(numeric_emb, target_dim) +
                self._resize_vector(geo_emb, target_dim) +
                self._resize_vector(temporal_emb, target_dim)
            ) / 4
        else:
            raise ValueError(f"Unknown fusion method: {fusion_method}")
        
        return combined.astype(np.float32)
    
    def encode_counties(
        self,
        df: pd.DataFrame,
        domain: EmbeddingDomain = EmbeddingDomain.ALL,
        batch_size: Optional[int] = None,
        use_multimodal: bool = False
    ) -> np.ndarray:
        """
        Encode multiple counties into vectors.
        
        Args:
            df: DataFrame with county data
            domain: Specific domain to focus on
            batch_size: Batch size for encoding
            use_multimodal: Whether to use multi-modal embeddings
            
        Returns:
            Array of embedding vectors (n_counties x embedding_dim)
        """
        batch_size = batch_size or self.config.batch_size
        embeddings = []
        
        print(f"Encoding {len(df)} counties...")
        
        for idx, row in df.iterrows():
            if use_multimodal:
                emb = self.generate_multi_modal_embedding(row, domain)
            else:
                emb = self.generate_text_embedding(row, domain)
            embeddings.append(emb)
            
            if (idx + 1) % 100 == 0:
                print(f"  Encoded {idx + 1}/{len(df)} counties...")
        
        return np.array(embeddings, dtype=np.float32)
    
    def encode_domain_specific(
        self,
        df: pd.DataFrame,
        batch_size: Optional[int] = None
    ) -> Dict[str, np.ndarray]:
        """
        Encode counties separately for each domain.
        
        Args:
            df: DataFrame with county data
            batch_size: Batch size for encoding
            
        Returns:
            Dictionary mapping domain names to embedding arrays
        """
        domain_embeddings = {}
        
        for domain in EmbeddingDomain:
            if domain == EmbeddingDomain.ALL:
                continue
            
            print(f"Encoding {domain.value} domain...")
            embeddings = self.encode_counties(
                df,
                domain=domain,
                batch_size=batch_size
            )
            domain_embeddings[domain.value] = embeddings
        
        return domain_embeddings
    
    def _create_enhanced_description(
        self,
        row: pd.Series,
        domain: EmbeddingDomain
    ) -> str:
        """Create enhanced text description for embedding."""
        parts = []
        county_name = row.get('county_name', 'Unknown County')
        state = row.get('state', row.get('state_name', 'Unknown State'))
        
        parts.append(f"County: {county_name}, State: {state}")
        
        # Domain-specific descriptions
        if domain in [EmbeddingDomain.CLIMATE, EmbeddingDomain.ALL]:
            parts.append(self._create_climate_description(row))
        
        if domain in [EmbeddingDomain.HEALTH, EmbeddingDomain.ALL]:
            parts.append(self._create_health_description(row))
        
        if domain in [EmbeddingDomain.INFRASTRUCTURE, EmbeddingDomain.ALL]:
            parts.append(self._create_infrastructure_description(row))
        
        if domain in [EmbeddingDomain.SOCIOECONOMIC, EmbeddingDomain.ALL]:
            parts.append(self._create_socioeconomic_description(row))
        
        if domain in [EmbeddingDomain.AGRICULTURE, EmbeddingDomain.ALL]:
            parts.append(self._create_agriculture_description(row))
        
        return "; ".join(parts)
    
    def _create_climate_description(self, row: pd.Series) -> str:
        """Create detailed climate profile description."""
        disaster_count = row.get('disaster_count', 0)
        flood = row.get('disaster_flood', 0)
        storms = row.get('disaster_severe_storms', 0)
        hurricane = row.get('disaster_hurricane', 0)
        fire = row.get('disaster_fire', 0)
        tornado = row.get('disaster_tornado', 0)
        drought = row.get('disaster_drought', 0)
        winter = row.get('disaster_winter_storm', 0)
        acceleration = row.get('disaster_acceleration', 0)
        
        return (
            f"Climate profile: {disaster_count} total disasters, "
            f"{flood} floods, {storms} severe storms, {hurricane} hurricanes, "
            f"{fire} wildfires, {tornado} tornadoes, {drought} droughts, "
            f"{winter} winter storms. Acceleration: {acceleration:.2f}"
        )
    
    def _create_health_description(self, row: pd.Series) -> str:
        """Create detailed health profile description."""
        elderly = row.get('elderly_pct', 0)
        disability = row.get('disability_pct', 0)
        uninsured = row.get('uninsured_pct', 0)
        hospital_dist = row.get('dist_nearest_hospitals_km', 0)
        hospital_density = row.get('density_hospitals_per10k', 0)
        
        return (
            f"Health profile: {elderly:.1f}% elderly, {disability:.1f}% disabled, "
            f"{uninsured:.1f}% uninsured. Healthcare access: nearest hospital "
            f"{hospital_dist:.1f}km away, {hospital_density:.2f} hospitals per 10k"
        )
    
    def _create_infrastructure_description(self, row: pd.Series) -> str:
        """Create detailed infrastructure profile description."""
        fire_dist = row.get('dist_nearest_fire_stations_km', 0)
        ems_dist = row.get('dist_nearest_ems_stations_km', 0)
        fire_density = row.get('density_fire_stations_per10k', 0)
        ems_density = row.get('density_ems_stations_per10k', 0)
        redundancy = row.get('redundancy_score', 0)
        
        return (
            f"Infrastructure: Fire station {fire_dist:.1f}km, EMS {ems_dist:.1f}km. "
            f"Densities: {fire_density:.2f} fire, {ems_density:.2f} EMS per 10k. "
            f"Redundancy score: {redundancy:.3f}"
        )
    
    def _create_socioeconomic_description(self, row: pd.Series) -> str:
        """Create detailed socioeconomic profile description."""
        population = row.get('total_population', 0)
        income = row.get('median_income', 0)
        poverty = row.get('poverty_pct', 0)
        vulnerability = row.get('vulnerability_index', 0)
        risk = row.get('risk_score', 0)
        
        return (
            f"Socioeconomic: Population {population:,.0f}, median income ${income:,.0f}, "
            f"{poverty:.1f}% poverty. Vulnerability: {vulnerability:.3f}, "
            f"Risk score: {risk:.3f}"
        )
    
    def _create_agriculture_description(self, row: pd.Series) -> str:
        """Create detailed agriculture profile description."""
        farmland_pct = row.get('farmland_pct', 0)
        crop_diversity = row.get('crop_diversity_index', 0)
        irrigation = row.get('irrigation_coverage', 0)
        
        return (
            f"Agriculture: {farmland_pct:.1f}% farmland, "
            f"crop diversity {crop_diversity:.2f}, "
            f"irrigation coverage {irrigation:.1f}%"
        )
    
    def _extract_numeric_features(self, row: pd.Series) -> np.ndarray:
        """Extract numeric features from county data."""
        features = []
        
        for domain, feature_list in self.config.domain_features.items():
            for feature in feature_list:
                value = row.get(feature, 0)
                # Handle missing values
                if pd.isna(value):
                    value = 0
                features.append(float(value))
        
        return np.array(features, dtype=np.float32)
    
    def _extract_temporal_features(self, row: pd.Series) -> List[float]:
        """Extract temporal features from county data."""
        return [
            row.get('trend_slope', 0),
            row.get('trend_acceleration', 0),
            row.get('seasonal_strength', 0),
            row.get('recent_change_1y', 0),
            row.get('recent_change_5y', 0),
            row.get('volatility', 0),
        ]
    
    def _weighted_fusion(
        self,
        text_emb: np.ndarray,
        numeric_emb: np.ndarray,
        geo_emb: np.ndarray,
        temporal_emb: np.ndarray
    ) -> np.ndarray:
        """Weighted fusion of embeddings."""
        # Default weights
        weights = {'text': 0.5, 'numeric': 0.25, 'geographic': 0.15, 'temporal': 0.1}
        
        target_dim = len(text_emb)
        
        combined = (
            weights['text'] * text_emb +
            weights['numeric'] * self._resize_vector(numeric_emb, target_dim) +
            weights['geographic'] * self._resize_vector(geo_emb, target_dim) +
            weights['temporal'] * self._resize_vector(temporal_emb, target_dim)
        )
        
        return combined
    
    def _resize_vector(self, vector: np.ndarray, target_dim: int) -> np.ndarray:
        """Resize vector to target dimension."""
        if len(vector) == target_dim:
            return vector
        
        # Simple linear interpolation
        indices = np.linspace(0, len(vector) - 1, target_dim)
        resized = np.interp(indices, np.arange(len(vector)), vector)
        
        return resized
    
    def _fallback_embedding(self, county_data: pd.Series) -> np.ndarray:
        """Create fallback embedding when model is not available."""
        # Use hash-based deterministic embedding
        text = str(county_data.to_dict())
        hash_val = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        
        np.random.seed(hash_val % (2**32))
        embedding = np.random.randn(self.config.embedding_dim)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.astype(np.float32)
    
    def get_embedding_dimension(self) -> int:
        """Get the output embedding dimension."""
        if self.config.multi_modal:
            return (
                self.config.embedding_dim +
                self.config.numeric_embedding_dim +
                self.config.geographic_embedding_dim +
                self.config.temporal_embedding_dim
            )
        return self.config.embedding_dim


# Convenience function
def create_county_embedder(
    model_name: str = "all-MiniLM-L6-v2",
    multi_modal: bool = False
) -> CountyEmbedder:
    """
    Create a county embedder with specified configuration.
    
    Args:
        model_name: Name of the embedding model
        multi_modal: Whether to enable multi-modal embeddings
        
    Returns:
        Configured CountyEmbedder instance
    """
    # Map string to enum
    model_map = {m.value: m for m in EmbeddingModel}
    model = model_map.get(model_name, EmbeddingModel.MINILM_L6)
    
    config = CountyEmbeddingConfig(
        model=model,
        multi_modal=multi_modal
    )
    
    return CountyEmbedder(config)


if __name__ == "__main__":
    # Example usage
    print("CountyEmbedder - Example Usage")
    print("=" * 50)
    
    # Create embedder
    config = CountyEmbeddingConfig(
        model=EmbeddingModel.MINILM_L6,
        multi_modal=False
    )
    embedder = CountyEmbedder(config)
    
    # Create sample county data
    sample_county = pd.Series({
        'county_name': 'Autauga County',
        'state': 'Alabama',
        'fips': '01001',
        'disaster_count': 15,
        'disaster_flood': 8,
        'disaster_tornado': 5,
        'elderly_pct': 14.2,
        'median_income': 55000,
        'vulnerability_index': 0.45,
        'risk_score': 0.62
    })
    
    # Generate embedding
    embedding = embedder.generate_text_embedding(sample_county)
    print(f"\nGenerated embedding shape: {embedding.shape}")
    print(f"Embedding norm: {np.linalg.norm(embedding):.4f}")
    
    # Generate multi-modal embedding
    multi_emb = embedder.generate_multi_modal_embedding(sample_county)
    print(f"\nMulti-modal embedding shape: {multi_emb.shape}")
    
    print("\nCountyEmbedder ready for use!")
