# ResilienceAI Vector Embedding Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the current vector embedding capabilities in ResilienceAI and proposes extensive enhancements for a production-ready vector similarity search platform. The analysis covers county embedding generation, vector database integration, semantic search, multi-modal embeddings, and approximate nearest neighbor (ANN) search implementations.

---

## 1. Current State Analysis

### 1.1 Existing Vector Capabilities

The current `src/vector_space.py` implementation provides:

| Feature | Current Implementation | Status |
|---------|----------------------|--------|
| Embedding Model | sentence-transformers (all-MiniLM-L6-v2) | ✅ Implemented |
| Vector Dimension | 384-dim | ✅ Implemented |
| Similarity Search | FAISS IndexFlatIP/IndexFlatL2 | ✅ Implemented |
| Multi-domain Encoding | climate, health, infrastructure, socioeconomic | ✅ Implemented |
| Cross-domain Analysis | Similarity matrix computation | ✅ Implemented |
| Anomaly Detection | Isolation Forest, LOF, distance-based | ✅ Implemented |
| Index Persistence | NumPy + FAISS native format | ✅ Implemented |
| Fallback Embeddings | Hash-based deterministic | ✅ Implemented |

### 1.2 Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CountyVectorEncoder                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Text Description Generator (Domain-specific)           │   │
│  │  - Climate: disaster counts, types, acceleration        │   │
│  │  - Health: elderly%, disability%, uninsured%            │   │
│  │  - Infrastructure: distances, densities, redundancy     │   │
│  │  - Socioeconomic: population, income, poverty           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SentenceTransformer (all-MiniLM-L6-v2, 384-dim)        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CountyVectorIndex                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FAISS Index (IndexFlatIP for cosine, IndexFlatL2)      │   │
│  │  - Exact search (brute force)                           │   │
│  │  - O(n) complexity per query                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CrossDomainAnalyzer                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Cross-domain similarity matrix                       │   │
│  │  - Anomaly detection (Isolation Forest, LOF)            │   │
│  │  - Correlation discovery                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Current Limitations

| Limitation | Impact | Severity |
|------------|--------|----------|
| Exact search only (no ANN) | Slow queries at scale | High |
| No vector database integration | Limited scalability | High |
| Single embedding model | No model selection flexibility | Medium |
| No embedding caching | Redundant computations | Medium |
| No semantic query understanding | Limited search expressiveness | High |
| No visualization tools | Difficult to interpret embeddings | Medium |
| No multi-modal support | Cannot combine text + numeric + geospatial | High |
| No incremental updates | Full reindexing required | Medium |
| No embedding versioning | Reproducibility issues | Low |

---

## 2. Proposed Vector Embedding Platform

### 2.1 Enhanced Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VECTOR EMBEDDING PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EMBEDDING GENERATION LAYER                        │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │  Text Emb    │ │  Numeric Emb │ │  Geo Emb     │ │  Time Emb  │  │   │
│  │  │  (BERT-based)│ │  (Tabular NN)│ │  (GeoHash)   │ │  (Temporal)│  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │   │
│  │                              ↓                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │   │
│  │  │              MULTI-MODAL FUSION (Concatenate/Attention)         │  │   │
│  │  └─────────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EMBEDDING CACHE LAYER                             │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │  Redis Cache │ │  Disk Cache  │ │  Memcached   │ │  LRU Cache │  │   │
│  │  │  (Hot data)  │ │  (Cold data) │ │  (Session)   │ │  (Local)   │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 VECTOR DATABASE LAYER (Multi-Provider)               │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │   Pinecone   │ │   Weaviate   │ │    Qdrant    │ │   FAISS    │  │   │
│  │  │  (Managed)   │ │  (Graph+Vec) │ │  (Open Src)  │ │  (Local)   │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SIMILARITY SEARCH LAYER                           │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │  Exact KNN   │ │  HNSW (ANN)  │ │  IVF (ANN)   │ │  PQ (ANN)  │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    QUERY UNDERSTANDING LAYER                         │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │  NL Query    │ │  Intent      │ │  Entity      │ │  Query     │  │   │
│  │  │  Parser      │ │  Classifier  │ │  Extraction  │ │  Expansion │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    VISUALIZATION LAYER                               │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │   t-SNE      │ │    UMAP      │ │  PCA Scatter │ │  Heatmaps  │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. County Embedding Generation

### 3.1 Enhanced County Embedding Pipeline

```python
# File: src/vector/embeddings/county_embedder.py

from typing import Dict, List, Optional, Union, Any
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import hashlib
import json

class EmbeddingModel(str, Enum):
    """Supported embedding models."""
    MINILM_L6 = "all-MiniLM-L6-v2"           # 384-dim, fast
    MINILM_L12 = "all-MiniLM-L12-v2"         # 384-dim, more accurate
    MPNET_BASE = "all-mpnet-base-v2"         # 768-dim, best quality
    DISTILBERT = "distilbert-base-nli"       # 768-dim, balanced
    E5_SMALL = "intfloat/e5-small-v2"        # 384-dim, optimized for search
    E5_BASE = "intfloat/e5-base-v2"          # 768-dim, high quality
    GTE_SMALL = "thenlper/gte-small"         # 384-dim, general text
    GTE_BASE = "thenlper/gte-base"           # 768-dim, general text
    BGE_SMALL = "BAAI/bge-small-en"          # 384-dim, bilingual
    BGE_BASE = "BAAI/bge-base-en"            # 768-dim, bilingual
    INSTRUCTOR = "hkunlp/instructor-base"    # 768-dim, instruction-tuned
    MULTILINGUAL = "paraphrase-multilingual-MiniLM-L12-v2"  # 384-dim, multi-lang

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

class CountyEmbedder:
    """
    Advanced county embedding generator with multi-modal support.
    
    Features:
    - Multiple embedding model support
    - Multi-modal fusion (text + numeric + geographic + temporal)
    - Configurable embedding dimensions
    - Built-in caching
    - Incremental embedding updates
    """
    
    def __init__(self, config: Optional[CountyEmbeddingConfig] = None):
        self.config = config or CountyEmbeddingConfig()
        self.text_encoder = None
        self.numeric_encoder = None
        self.geo_encoder = None
        self.temporal_encoder = None
        self._load_models()
        
    def _load_models(self):
        """Load embedding models based on configuration."""
        from sentence_transformers import SentenceTransformer
        
        # Load text encoder
        self.text_encoder = SentenceTransformer(self.config.model.value)
        
        # Initialize numeric encoder (tabular neural network)
        self.numeric_encoder = TabularEncoder(
            input_dim=50,  # Number of numeric features
            output_dim=self.config.numeric_embedding_dim
        )
        
        # Initialize geographic encoder (geohash + coordinate embedding)
        self.geo_encoder = GeographicEncoder(
            output_dim=self.config.geographic_embedding_dim
        )
        
        # Initialize temporal encoder (time-series features)
        self.temporal_encoder = TemporalEncoder(
            output_dim=self.config.temporal_embedding_dim
        )
    
    def generate_text_embedding(
        self, 
        county_data: pd.Series,
        domain: EmbeddingDomain = EmbeddingDomain.ALL
    ) -> np.ndarray:
        """
        Generate text-based embedding from county description.
        
        Args:
            county_data: County data row
            domain: Specific domain or ALL for comprehensive
            
        Returns:
            Text embedding vector
        """
        description = self._create_enhanced_description(county_data, domain)
        embedding = self.text_encoder.encode(
            description,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=self.config.normalize
        )
        return embedding.astype(np.float32)
    
    def generate_numeric_embedding(self, county_data: pd.Series) -> np.ndarray:
        """
        Generate numeric feature embedding using tabular NN.
        
        Args:
            county_data: County data row
            
        Returns:
            Numeric embedding vector
        """
        numeric_features = self._extract_numeric_features(county_data)
        return self.numeric_encoder.encode(numeric_features)
    
    def generate_geographic_embedding(self, county_data: pd.Series) -> np.ndarray:
        """
        Generate geographic embedding from coordinates.
        
        Args:
            county_data: County data row with lat/lon
            
        Returns:
            Geographic embedding vector
        """
        lat = county_data.get('latitude', county_data.get('centroid_lat'))
        lon = county_data.get('longitude', county_data.get('centroid_lon'))
        return self.geo_encoder.encode(lat, lon)
    
    def generate_temporal_embedding(self, county_data: pd.Series) -> np.ndarray:
        """
        Generate temporal embedding from time-series features.
        
        Args:
            county_data: County data row with temporal features
            
        Returns:
            Temporal embedding vector
        """
        temporal_features = self._extract_temporal_features(county_data)
        return self.temporal_encoder.encode(temporal_features)
    
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
            # Learned weights for each modality
            weights = self._get_modality_weights(domain)
            combined = (
                weights['text'] * text_emb +
                weights['numeric'] * np.resize(numeric_emb, text_emb.shape) +
                weights['geographic'] * np.resize(geo_emb, text_emb.shape) +
                weights['temporal'] * np.resize(temporal_emb, text_emb.shape)
            )
        elif fusion_method == "attention":
            combined = self._attention_fusion(
                text_emb, numeric_emb, geo_emb, temporal_emb
            )
        else:
            raise ValueError(f"Unknown fusion method: {fusion_method}")
        
        return combined.astype(np.float32)
    
    def _create_enhanced_description(
        self,
        row: pd.Series,
        domain: EmbeddingDomain
    ) -> str:
        """Create enhanced text description for embedding."""
        parts = []
        county_name = row.get('county_name', 'Unknown County')
        state = row.get('state', 'Unknown State')
        
        parts.append(f"County: {county_name}, State: {state}")
        
        # Domain-specific descriptions with enhanced detail
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
        trend = row.get('disaster_trend', 'stable')
        
        return (
            f"Climate profile: {disaster_count} total disasters, "
            f"{flood} floods, {storms} severe storms, {hurricane} hurricanes, "
            f"{fire} wildfires, {tornado} tornadoes, {drought} droughts, "
            f"{winter} winter storms. Trend: {trend} with acceleration {acceleration:.2f}"
        )
    
    def _create_health_description(self, row: pd.Series) -> str:
        """Create detailed health profile description."""
        elderly = row.get('elderly_pct', 0)
        disability = row.get('disability_pct', 0)
        uninsured = row.get('uninsured_pct', 0)
        hospital_dist = row.get('dist_nearest_hospitals_km', 0)
        hospital_density = row.get('density_hospitals_per10k', 0)
        nursing_dist = row.get('dist_nearest_nursing_homes_km', 0)
        nursing_density = row.get('density_nursing_homes_per10k', 0)
        icu_beds = row.get('icu_beds_per_1000', 0)
        
        return (
            f"Health profile: {elderly:.1f}% elderly, {disability:.1f}% disabled, "
            f"{uninsured:.1f}% uninsured. Healthcare access: nearest hospital "
            f"{hospital_dist:.1f}km away, {hospital_density:.2f} hospitals per 10k, "
            f"{icu_beds:.2f} ICU beds per 1000. Nursing homes: {nursing_dist:.1f}km, "
            f"{nursing_density:.2f} per 10k"
        )
    
    def _create_infrastructure_description(self, row: pd.Series) -> str:
        """Create detailed infrastructure profile description."""
        fire_dist = row.get('dist_nearest_fire_stations_km', 0)
        ems_dist = row.get('dist_nearest_ems_stations_km', 0)
        fire_density = row.get('density_fire_stations_per10k', 0)
        ems_density = row.get('density_ems_stations_per10k', 0)
        redundancy = row.get('redundancy_score', 0)
        power_grid = row.get('power_grid_resilience', 'unknown')
        water_system = row.get('water_system_age', 0)
        bridge_condition = row.get('bridge_condition_score', 0)
        
        return (
            f"Infrastructure: Fire station {fire_dist:.1f}km, EMS {ems_dist:.1f}km. "
            f"Densities: {fire_density:.2f} fire, {ems_density:.2f} EMS per 10k. "
            f"Redundancy score: {redundancy:.3f}. Power grid: {power_grid}. "
            f"Water system age: {water_system:.0f} years. "
            f"Bridge condition: {bridge_condition:.1f}/100"
        )
    
    def _create_socioeconomic_description(self, row: pd.Series) -> str:
        """Create detailed socioeconomic profile description."""
        population = row.get('total_population', 0)
        income = row.get('median_income', 0)
        poverty = row.get('poverty_pct', 0)
        unemployment = row.get('unemployment_rate', 0)
        education = row.get('education_index', 0)
        vulnerability = row.get('vulnerability_index', 0)
        risk = row.get('risk_score', 0)
        
        return (
            f"Socioeconomic: Population {population:,.0f}, median income ${income:,.0f}, "
            f"{poverty:.1f}% poverty, {unemployment:.1f}% unemployment. "
            f"Education index: {education:.3f}. Vulnerability: {vulnerability:.3f}, "
            f"Risk score: {risk:.3f}"
        )
    
    def _create_agriculture_description(self, row: pd.Series) -> str:
        """Create detailed agriculture profile description."""
        farmland_pct = row.get('farmland_pct', 0)
        crop_diversity = row.get('crop_diversity_index', 0)
        irrigation = row.get('irrigation_coverage', 0)
        drought_vulnerability = row.get('agricultural_drought_vulnerability', 0)
        
        return (
            f"Agriculture: {farmland_pct:.1f}% farmland, crop diversity {crop_diversity:.2f}, "
            f"irrigation coverage {irrigation:.1f}%, "
            f"drought vulnerability {drought_vulnerability:.3f}"
        )
```

### 3.2 Tabular Numeric Encoder

```python
# File: src/vector/embeddings/numeric_encoder.py

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any

class TabularEncoder(nn.Module):
    """
    Neural network encoder for tabular numeric features.
    Uses a feed-forward network with batch normalization.
    """
    
    def __init__(
        self,
        input_dim: int = 50,
        output_dim: int = 128,
        hidden_dims: List[int] = [256, 128],
        dropout: float = 0.2
    ):
        super().__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, output_dim))
        self.encoder = nn.Sequential(*layers)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)
    
    def encode(self, features: np.ndarray) -> np.ndarray:
        """Encode numeric features to embedding vector."""
        with torch.no_grad():
            x = torch.FloatTensor(features).unsqueeze(0)
            embedding = self.forward(x)
            return embedding.numpy().flatten()

class GeographicEncoder:
    """
    Geographic coordinate encoder using geohash and sinusoidal encoding.
    """
    
    def __init__(self, output_dim: int = 64, precision: int = 6):
        self.output_dim = output_dim
        self.precision = precision
        
    def encode(self, lat: float, lon: float) -> np.ndarray:
        """
        Encode geographic coordinates to embedding.
        
        Uses:
        1. Geohash for spatial binning
        2. Sinusoidal encoding for continuous coordinates
        3. Distance to major landmarks
        """
        import pygeohash as pgh
        
        # Geohash encoding
        geohash = pgh.encode(lat, lon, precision=self.precision)
        geohash_int = int.from_bytes(geohash.encode(), 'little') % 10000
        
        # Sinusoidal encoding (similar to positional encoding in Transformers)
        position = np.array([lat, lon])
        div_term = np.exp(
            np.arange(0, self.output_dim // 2, 2) * 
            -(np.log(10000.0) / (self.output_dim // 2))
        )
        
        pe = np.zeros(self.output_dim)
        pe[0::4] = np.sin(position[0] * div_term)
        pe[1::4] = np.cos(position[0] * div_term)
        pe[2::4] = np.sin(position[1] * div_term)
        pe[3::4] = np.cos(position[1] * div_term)
        
        # Normalize
        pe = pe / np.linalg.norm(pe)
        
        return pe.astype(np.float32)

class TemporalEncoder:
    """
    Temporal feature encoder for time-series data.
    """
    
    def __init__(self, output_dim: int = 32):
        self.output_dim = output_dim
        
    def encode(self, temporal_features: Dict[str, float]) -> np.ndarray:
        """
        Encode temporal features to embedding.
        
        Features:
        - Trend direction and magnitude
        - Seasonality patterns
        - Recent change indicators
        """
        features = np.array([
            temporal_features.get('trend_slope', 0),
            temporal_features.get('trend_acceleration', 0),
            temporal_features.get('seasonal_strength', 0),
            temporal_features.get('recent_change_1y', 0),
            temporal_features.get('recent_change_5y', 0),
            temporal_features.get('volatility', 0),
        ])
        
        # Pad or truncate to output_dim
        if len(features) < self.output_dim:
            features = np.pad(features, (0, self.output_dim - len(features)))
        else:
            features = features[:self.output_dim]
        
        return features.astype(np.float32)
```

---

## 4. Vector Database Integration

### 4.1 Unified Vector Database Interface

```python
# File: src/vector/databases/base.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import numpy as np
from enum import Enum

class VectorDBProvider(str, Enum):
    """Supported vector database providers."""
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    FAISS = "faiss"
    CHROMA = "chroma"
    MILVUS = "milvus"

@dataclass
class VectorRecord:
    """Single vector record for database storage."""
    id: str
    vector: np.ndarray
    metadata: Dict[str, Any]
    
@dataclass
class SearchResult:
    """Result from vector similarity search."""
    id: str
    score: float
    metadata: Dict[str, Any]
    
@dataclass
class VectorDBConfig:
    """Configuration for vector database connection."""
    provider: VectorDBProvider
    api_key: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    index_name: str = "county_vectors"
    dimension: int = 768
    metric: str = "cosine"  # cosine, euclidean, dotproduct
    
class BaseVectorDB(ABC):
    """Abstract base class for vector database implementations."""
    
    def __init__(self, config: VectorDBConfig):
        self.config = config
        self.client = None
        
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to vector database."""
        pass
    
    @abstractmethod
    def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine",
        **kwargs
    ) -> bool:
        """Create a new vector index."""
        pass
    
    @abstractmethod
    def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None
    ) -> bool:
        """Insert or update vectors in the database."""
        pass
    
    @abstractmethod
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: Optional[str] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> bool:
        """Delete vectors by ID."""
        pass
    
    @abstractmethod
    def fetch(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> List[VectorRecord]:
        """Fetch vectors by ID."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        pass
```

### 4.2 Pinecone Integration

```python
# File: src/vector/databases/pinecone_db.py

from typing import Dict, List, Optional, Any
import numpy as np
from pinecone import Pinecone, ServerlessSpec
from .base import BaseVectorDB, VectorDBConfig, VectorRecord, SearchResult

class PineconeVectorDB(BaseVectorDB):
    """
    Pinecone vector database implementation.
    
    Features:
    - Managed vector database service
    - Automatic scaling
    - Metadata filtering
    - Hybrid search (dense + sparse)
    """
    
    def __init__(self, config: VectorDBConfig):
        super().__init__(config)
        self.index = None
        
    def connect(self) -> bool:
        """Connect to Pinecone."""
        try:
            self.client = Pinecone(api_key=self.config.api_key)
            self.index = self.client.Index(self.config.index_name)
            return True
        except Exception as e:
            print(f"Failed to connect to Pinecone: {e}")
            return False
    
    def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1",
        **kwargs
    ) -> bool:
        """Create a Pinecone index."""
        try:
            # Check if index exists
            if index_name in self.client.list_indexes().names():
                print(f"Index {index_name} already exists")
                return True
            
            # Create index
            self.client.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud=cloud, region=region)
            )
            self.index = self.client.Index(index_name)
            return True
        except Exception as e:
            print(f"Failed to create index: {e}")
            return False
    
    def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None
    ) -> bool:
        """Upsert vectors to Pinecone."""
        try:
            vectors = []
            for record in records:
                vectors.append({
                    'id': record.id,
                    'values': record.vector.tolist(),
                    'metadata': record.metadata
                })
            
            self.index.upsert(vectors=vectors, namespace=namespace)
            return True
        except Exception as e:
            print(f"Failed to upsert vectors: {e}")
            return False
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: Optional[str] = None
    ) -> List[SearchResult]:
        """Search Pinecone for similar vectors."""
        try:
            results = self.index.query(
                vector=query_vector.tolist(),
                top_k=top_k,
                filter=filter_dict,
                namespace=namespace,
                include_metadata=True
            )
            
            return [
                SearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata
                )
                for match in results.matches
            ]
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> bool:
        """Delete vectors from Pinecone."""
        try:
            self.index.delete(ids=ids, namespace=namespace)
            return True
        except Exception as e:
            print(f"Delete failed: {e}")
            return False
    
    def fetch(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> List[VectorRecord]:
        """Fetch vectors from Pinecone."""
        try:
            results = self.index.fetch(ids=ids, namespace=namespace)
            
            records = []
            for id, vector_data in results.vectors.items():
                records.append(VectorRecord(
                    id=id,
                    vector=np.array(vector_data.values),
                    metadata=vector_data.metadata
                ))
            return records
        except Exception as e:
            print(f"Fetch failed: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics."""
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness
            }
        except Exception as e:
            print(f"Failed to get stats: {e}")
            return {}
```

### 4.3 Weaviate Integration

```python
# File: src/vector/databases/weaviate_db.py

import weaviate
from weaviate.classes import Config as WeaviateConfig
from weaviate.classes.query import Filter
from typing import Dict, List, Optional, Any
import numpy as np
from .base import BaseVectorDB, VectorDBConfig, VectorRecord, SearchResult

class WeaviateVectorDB(BaseVectorDB):
    """
    Weaviate vector database implementation.
    
    Features:
    - GraphQL interface
    - Vector + BM25 hybrid search
    - Built-in vectorization modules
    - Schema-based data organization
    """
    
    def __init__(self, config: VectorDBConfig):
        super().__init__(config)
        
    def connect(self) -> bool:
        """Connect to Weaviate."""
        try:
            self.client = weaviate.connect_to_wcs(
                cluster_url=self.config.host,
                auth_credentials=weaviate.auth.AuthApiKey(self.config.api_key)
            )
            return True
        except Exception as e:
            print(f"Failed to connect to Weaviate: {e}")
            return False
    
    def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine",
        properties: Optional[List[Dict]] = None,
        **kwargs
    ) -> bool:
        """Create a Weaviate collection (class)."""
        try:
            # Define schema
            class_schema = {
                "class": index_name,
                "vectorizer": "none",  # We provide vectors
                "vectorIndexConfig": {
                    "distance": metric,
                    "ef": 256,
                    "efConstruction": 128,
                    "maxConnections": 64
                },
                "properties": properties or [
                    {"name": "county_name", "dataType": ["text"]},
                    {"name": "state", "dataType": ["text"]},
                    {"name": "fips", "dataType": ["text"]},
                    {"name": "risk_score", "dataType": ["number"]},
                    {"name": "vulnerability_index", "dataType": ["number"]},
                ]
            }
            
            self.client.collections.create_from_dict(class_schema)
            return True
        except Exception as e:
            print(f"Failed to create collection: {e}")
            return False
    
    def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None
    ) -> bool:
        """Upsert vectors to Weaviate."""
        try:
            collection = self.client.collections.get(self.config.index_name)
            
            with collection.batch.dynamic() as batch:
                for record in records:
                    batch.add_object(
                        properties=record.metadata,
                        vector=record.vector.tolist(),
                        uuid=record.id
                    )
            
            return True
        except Exception as e:
            print(f"Failed to upsert vectors: {e}")
            return False
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: Optional[str] = None
    ) -> List[SearchResult]:
        """Search Weaviate for similar vectors."""
        try:
            collection = self.client.collections.get(self.config.index_name)
            
            # Build filter if provided
            weaviate_filter = None
            if filter_dict:
                filters = []
                for key, value in filter_dict.items():
                    filters.append(Filter.by_property(key).equal(value))
                weaviate_filter = Filter.all_of(filters)
            
            results = collection.query.near_vector(
                near_vector=query_vector.tolist(),
                limit=top_k,
                filters=weaviate_filter,
                return_metadata=["distance"]
            )
            
            return [
                SearchResult(
                    id=obj.uuid,
                    score=1 - obj.metadata.distance,  # Convert distance to similarity
                    metadata=obj.properties
                )
                for obj in results.objects
            ]
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def hybrid_search(
        self,
        query_text: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        alpha: float = 0.5
    ) -> List[SearchResult]:
        """
        Hybrid search combining vector and BM25.
        
        Args:
            query_text: Text query for BM25
            query_vector: Vector for similarity search
            top_k: Number of results
            alpha: Weight for vector search (1-alpha for BM25)
        """
        try:
            collection = self.client.collections.get(self.config.index_name)
            
            results = collection.query.hybrid(
                query=query_text,
                vector=query_vector.tolist(),
                alpha=alpha,
                limit=top_k
            )
            
            return [
                SearchResult(
                    id=obj.uuid,
                    score=obj.metadata.score,
                    metadata=obj.properties
                )
                for obj in results.objects
            ]
        except Exception as e:
            print(f"Hybrid search failed: {e}")
            return []
```

### 4.4 Qdrant Integration

```python
# File: src/vector/databases/qdrant_db.py

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter as QdrantFilter,
    FieldCondition, MatchValue
)
from typing import Dict, List, Optional, Any
import numpy as np
from .base import BaseVectorDB, VectorDBConfig, VectorRecord, SearchResult

class QdrantVectorDB(BaseVectorDB):
    """
    Qdrant vector database implementation.
    
    Features:
    - Open-source with managed cloud option
    - Payload-based filtering
    - HNSW indexing
    - Built-in recommendation API
    """
    
    def __init__(self, config: VectorDBConfig):
        super().__init__(config)
        
    def connect(self) -> bool:
        """Connect to Qdrant."""
        try:
            if self.config.host:
                self.client = QdrantClient(
                    host=self.config.host,
                    port=self.config.port or 6333,
                    api_key=self.config.api_key
                )
            else:
                # Local mode
                self.client = QdrantClient(path="./qdrant_storage")
            return True
        except Exception as e:
            print(f"Failed to connect to Qdrant: {e}")
            return False
    
    def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine",
        **kwargs
    ) -> bool:
        """Create a Qdrant collection."""
        try:
            # Map metric to Qdrant Distance
            metric_map = {
                "cosine": Distance.COSINE,
                "euclidean": Distance.EUCLID,
                "dotproduct": Distance.DOT
            }
            
            self.client.create_collection(
                collection_name=index_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=metric_map.get(metric, Distance.COSINE),
                    hnsw_config={
                        "m": 16,
                        "ef_construct": 100,
                        "full_scan_threshold": 10000
                    }
                )
            )
            return True
        except Exception as e:
            print(f"Failed to create collection: {e}")
            return False
    
    def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None
    ) -> bool:
        """Upsert vectors to Qdrant."""
        try:
            points = [
                PointStruct(
                    id=record.id,
                    vector=record.vector.tolist(),
                    payload=record.metadata
                )
                for record in records
            ]
            
            self.client.upsert(
                collection_name=self.config.index_name,
                points=points
            )
            return True
        except Exception as e:
            print(f"Failed to upsert vectors: {e}")
            return False
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: Optional[str] = None
    ) -> List[SearchResult]:
        """Search Qdrant for similar vectors."""
        try:
            # Build filter
            search_filter = None
            if filter_dict:
                conditions = [
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                    for key, value in filter_dict.items()
                ]
                search_filter = QdrantFilter(must=conditions)
            
            results = self.client.search(
                collection_name=self.config.index_name,
                query_vector=query_vector.tolist(),
                limit=top_k,
                query_filter=search_filter,
                with_payload=True
            )
            
            return [
                SearchResult(
                    id=str(result.id),
                    score=result.score,
                    metadata=result.payload
                )
                for result in results
            ]
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def recommend(
        self,
        positive_ids: List[str],
        negative_ids: Optional[List[str]] = None,
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        Recommend similar counties based on positive/negative examples.
        
        Args:
            positive_ids: IDs of counties to use as positive examples
            negative_ids: IDs of counties to use as negative examples
            top_k: Number of recommendations
        """
        try:
            results = self.client.recommend(
                collection_name=self.config.index_name,
                positive=positive_ids,
                negative=negative_ids or [],
                limit=top_k,
                with_payload=True
            )
            
            return [
                SearchResult(
                    id=str(result.id),
                    score=result.score,
                    metadata=result.payload
                )
                for result in results
            ]
        except Exception as e:
            print(f"Recommendation failed: {e}")
            return []
```

---

## 5. Similarity Search Architecture

### 5.1 Approximate Nearest Neighbor (ANN) Implementations

```python
# File: src/vector/search/ann_search.py

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from enum import Enum
from dataclasses import dataclass
import faiss

class ANNAlgorithm(str, Enum):
    """Supported ANN algorithms."""
    HNSW = "hnsw"                    # Hierarchical Navigable Small World
    IVF = "ivf"                      # Inverted File Index
    PQ = "pq"                        # Product Quantization
    OPQ = "opq"                      # Optimized Product Quantization
    LSH = "lsh"                      # Locality Sensitive Hashing
    SCANN = "scann"                  # Scalable Nearest Neighbors (Google)

@dataclass
class ANNConfig:
    """Configuration for ANN index."""
    algorithm: ANNAlgorithm = ANNAlgorithm.HNSW
    nlist: int = 100                 # Number of clusters for IVF
    nprobe: int = 10                 # Number of clusters to search
    m: int = 16                      # HNSW connections per layer
    ef_construction: int = 200       # HNSW construction parameter
    ef_search: int = 128             # HNSW search parameter
    nbits: int = 8                   # Bits per subvector for PQ
    
class FAISSANNIndex:
    """
    FAISS-based ANN index implementations.
    
    Supports multiple ANN algorithms for different use cases:
    - HNSW: Best for high-dimensional data, fast search
    - IVF: Good balance of speed and accuracy
    - PQ: Best for memory-constrained scenarios
    """
    
    def __init__(self, dimension: int, config: ANNConfig):
        self.dimension = dimension
        self.config = config
        self.index = None
        self.vectors = None
        self.ids = None
        
    def build_index(
        self,
        vectors: np.ndarray,
        ids: Optional[List[str]] = None
    ) -> 'FAISSANNIndex':
        """Build ANN index from vectors."""
        self.vectors = vectors.astype(np.float32)
        self.ids = ids or [str(i) for i in range(len(vectors))]
        
        if self.config.algorithm == ANNAlgorithm.HNSW:
            self.index = self._build_hnsw_index()
        elif self.config.algorithm == ANNAlgorithm.IVF:
            self.index = self._build_ivf_index()
        elif self.config.algorithm == ANNAlgorithm.PQ:
            self.index = self._build_pq_index()
        elif self.config.algorithm == ANNAlgorithm.OPQ:
            self.index = self._build_opq_index()
        else:
            raise ValueError(f"Unknown algorithm: {self.config.algorithm}")
        
        return self
    
    def _build_hnsw_index(self) -> faiss.Index:
        """Build HNSW index."""
        # HNSW is best for high-dimensional data
        index = faiss.IndexHNSWFlat(self.dimension, self.config.m)
        index.hnsw.efConstruction = self.config.ef_construction
        index.hnsw.efSearch = self.config.ef_search
        index.add(self.vectors)
        return index
    
    def _build_ivf_index(self) -> faiss.Index:
        """Build IVF (Inverted File) index."""
        # IVF is good for large datasets
        quantizer = faiss.IndexFlatIP(self.dimension)
        index = faiss.IndexIVFFlat(
            quantizer,
            self.dimension,
            self.config.nlist
        )
        index.train(self.vectors)
        index.add(self.vectors)
        index.nprobe = self.config.nprobe
        return index
    
    def _build_pq_index(self) -> faiss.Index:
        """Build Product Quantization index."""
        # PQ is memory-efficient
        m = self.dimension // 8  # Number of subquantizers
        nbits = self.config.nbits
        
        index = faiss.IndexPQ(self.dimension, m, nbits)
        index.train(self.vectors)
        index.add(self.vectors)
        return index
    
    def _build_opq_index(self) -> faiss.Index:
        """Build Optimized Product Quantization index."""
        # OPQ improves PQ with rotation
        m = self.dimension // 8
        nbits = self.config.nbits
        
        opq = faiss.OPQMatrix(self.dimension, m)
        pq = faiss.IndexPQ(self.dimension, m, nbits)
        index = faiss.IndexPreTransform(opq, pq)
        index.train(self.vectors)
        index.add(self.vectors)
        return index
    
    def search(
        self,
        query: np.ndarray,
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for k nearest neighbors.
        
        Returns:
            distances, indices
        """
        query = query.reshape(1, -1).astype(np.float32)
        distances, indices = self.index.search(query, k)
        return distances[0], indices[0]
    
    def batch_search(
        self,
        queries: np.ndarray,
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Batch search for multiple queries."""
        queries = queries.astype(np.float32)
        return self.index.search(queries, k)
    
    def save(self, path: str):
        """Save index to disk."""
        faiss.write_index(self.index, path)
        
    def load(self, path: str):
        """Load index from disk."""
        self.index = faiss.read_index(path)
```

### 5.2 Similar County Identification

```python
# File: src/vector/search/similarity_engine.py

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum

class SimilarityMetric(str, Enum):
    """Supported similarity metrics."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"
    PEARSON = "pearson"
    JACCARD = "jaccard"

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

class SimilarityEngine:
    """
    Advanced similarity search engine for counties.
    
    Features:
    - Multi-metric similarity computation
    - Domain-specific similarity weighting
    - Explainable similarity results
    - Temporal similarity (trend comparison)
    """
    
    def __init__(
        self,
        vector_db: Any,
        county_metadata: pd.DataFrame
    ):
        self.vector_db = vector_db
        self.metadata = county_metadata
        self.domain_weights = {
            'climate': 0.25,
            'health': 0.25,
            'infrastructure': 0.25,
            'socioeconomic': 0.25
        }
        
    def find_similar_counties(
        self,
        query_fips: str,
        k: int = 10,
        metric: SimilarityMetric = SimilarityMetric.COSINE,
        domain_weights: Optional[Dict[str, float]] = None,
        filter_criteria: Optional[Dict] = None
    ) -> List[SimilarCountyResult]:
        """
        Find counties similar to the query county.
        
        Args:
            query_fips: FIPS code of query county
            k: Number of similar counties to return
            metric: Similarity metric to use
            domain_weights: Custom weights for each domain
            filter_criteria: Additional filters (e.g., same state)
            
        Returns:
            List of similar counties with scores
        """
        # Get query county vector
        query_vector = self._get_county_vector(query_fips)
        
        # Apply domain weights if provided
        weights = domain_weights or self.domain_weights
        query_vector = self._apply_domain_weights(query_vector, weights)
        
        # Search vector database
        results = self.vector_db.search(
            query_vector=query_vector,
            top_k=k + 1,  # +1 to exclude self
            filter_dict=filter_criteria
        )
        
        # Format results
        similar_counties = []
        rank = 1
        for result in results:
            if result.id == query_fips:
                continue
            
            county_data = self.metadata[self.metadata['fips'] == result.id].iloc[0]
            
            # Compute domain-specific similarities
            domain_scores = self._compute_domain_similarities(
                query_fips, result.id
            )
            
            # Generate explanation
            explanation = self._generate_similarity_explanation(
                query_fips, result.id, domain_scores
            )
            
            similar_counties.append(SimilarCountyResult(
                county_fips=result.id,
                county_name=county_data['county_name'],
                state=county_data.get('state', 'Unknown'),
                similarity_score=result.score,
                rank=rank,
                domain_scores=domain_scores,
                explanation=explanation
            ))
            
            rank += 1
            if rank > k:
                break
        
        return similar_counties
    
    def find_similar_by_profile(
        self,
        profile: Dict[str, Any],
        k: int = 10
    ) -> List[SimilarCountyResult]:
        """
        Find counties matching a hypothetical profile.
        
        Args:
            profile: Dictionary of desired characteristics
            k: Number of results
            
        Returns:
            List of matching counties
        """
        # Convert profile to vector
        profile_vector = self._profile_to_vector(profile)
        
        # Search
        results = self.vector_db.search(
            query_vector=profile_vector,
            top_k=k
        )
        
        return self._format_results(results)
    
    def compute_similarity_matrix(
        self,
        fips_list: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Compute pairwise similarity matrix for counties.
        
        Args:
            fips_list: List of FIPS codes (None for all)
            
        Returns:
            Similarity matrix DataFrame
        """
        if fips_list is None:
            fips_list = self.metadata['fips'].tolist()
        
        n = len(fips_list)
        matrix = np.zeros((n, n))
        
        for i, fips1 in enumerate(fips_list):
            vec1 = self._get_county_vector(fips1)
            for j, fips2 in enumerate(fips_list):
                if i <= j:
                    vec2 = self._get_county_vector(fips2)
                    sim = self._compute_similarity(vec1, vec2)
                    matrix[i, j] = sim
                    matrix[j, i] = sim
        
        return pd.DataFrame(
            matrix,
            index=fips_list,
            columns=fips_list
        )
    
    def _compute_similarity(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray,
        metric: SimilarityMetric = SimilarityMetric.COSINE
    ) -> float:
        """Compute similarity between two vectors."""
        if metric == SimilarityMetric.COSINE:
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        elif metric == SimilarityMetric.EUCLIDEAN:
            return 1 / (1 + np.linalg.norm(vec1 - vec2))
        elif metric == SimilarityMetric.MANHATTAN:
            return 1 / (1 + np.sum(np.abs(vec1 - vec2)))
        elif metric == SimilarityMetric.DOT_PRODUCT:
            return np.dot(vec1, vec2)
        elif metric == SimilarityMetric.PEARSON:
            return np.corrcoef(vec1, vec2)[0, 1]
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
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
            parts.append(
                f"Highly similar in: {', '.join(top_domains)}"
            )
        
        # Identify differences
        bottom_domains = [d for d, s in sorted_domains[-2:] if s < 0.5]
        if bottom_domains:
            parts.append(
                f"Different in: {', '.join(bottom_domains)}"
            )
        
        return "; ".join(parts) if parts else "Moderately similar across all domains"
```

---

## 6. Semantic Query Understanding

### 6.1 Natural Language Query Parser

```python
# File: src/vector/query/query_parser.py

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class QueryIntent(str, Enum):
    """Types of query intents."""
    FIND_SIMILAR = "find_similar"
    COMPARE = "compare"
    RANK = "rank"
    FILTER = "filter"
    ANALYZE = "analyze"
    TREND = "trend"

class QueryEntity(str, Enum):
    """Types of entities in queries."""
    COUNTY = "county"
    STATE = "state"
    REGION = "region"
    DISASTER_TYPE = "disaster_type"
    RISK_LEVEL = "risk_level"
    POPULATION = "population"
    INCOME = "income"

@dataclass
class ParsedQuery:
    """Parsed natural language query."""
    original_query: str
    intent: QueryIntent
    entities: Dict[str, Any]
    filters: Dict[str, Any]
    sort_by: Optional[str]
    limit: int
    confidence: float

class NLQueryParser:
    """
    Natural language query parser for county searches.
    
    Converts natural language queries to structured search parameters.
    """
    
    def __init__(self):
        self.intent_patterns = {
            QueryIntent.FIND_SIMILAR: [
                r"similar to (?P<county>.+?)(?: county)?",
                r"like (?P<county>.+?)(?: county)?",
                r"counties similar to (?P<county>.+)",
                r"comparable to (?P<county>.+)"
            ],
            QueryIntent.COMPARE: [
                r"compare (?P<county1>.+?) and (?P<county2>.+)",
                r"difference between (?P<county1>.+?) and (?P<county2>.+)",
                r"how does (?P<county1>.+?) compare to (?P<county2>.+)"
            ],
            QueryIntent.RANK: [
                r"(?:top|highest|most) (?P<n>\d+)?\s*(?P<metric>.+)",
                r"rank by (?P<metric>.+)",
                r"(?:lowest|least) (?P<metric>.+)"
            ],
            QueryIntent.FILTER: [
                r"counties (?:with|having) (?P<criteria>.+)",
                r"where (?P<criteria>.+)",
                r"(?P<state>.+?) counties"
            ],
            QueryIntent.ANALYZE: [
                r"analyze (?P<county>.+)",
                r"tell me about (?P<county>.+)",
                r"what do you know about (?P<county>.+)"
            ]
        }
        
        self.disaster_types = [
            "flood", "hurricane", "tornado", "fire", "wildfire",
            "storm", "earthquake", "drought", "winter storm"
        ]
        
        self.risk_levels = ["low", "medium", "high", "very high", "extreme"]
        
    def parse(self, query: str) -> ParsedQuery:
        """
        Parse natural language query.
        
        Args:
            query: Natural language query string
            
        Returns:
            ParsedQuery with structured information
        """
        query_lower = query.lower()
        
        # Detect intent
        intent, entities, confidence = self._detect_intent(query_lower)
        
        # Extract filters
        filters = self._extract_filters(query_lower)
        
        # Extract sort criteria
        sort_by = self._extract_sort_criteria(query_lower)
        
        # Extract limit
        limit = self._extract_limit(query_lower)
        
        return ParsedQuery(
            original_query=query,
            intent=intent,
            entities=entities,
            filters=filters,
            sort_by=sort_by,
            limit=limit,
            confidence=confidence
        )
    
    def _detect_intent(self, query: str) -> Tuple[QueryIntent, Dict, float]:
        """Detect query intent and extract entities."""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    return intent, match.groupdict(), 0.9
        
        # Default to FIND_SIMILAR if no pattern matches
        return QueryIntent.FIND_SIMILAR, {}, 0.5
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filter criteria from query."""
        filters = {}
        
        # Extract disaster type
        for disaster in self.disaster_types:
            if disaster in query:
                filters['disaster_type'] = disaster
                break
        
        # Extract risk level
        for risk in self.risk_levels:
            if risk in query:
                filters['risk_level'] = risk
                break
        
        # Extract population criteria
        pop_match = re.search(
            r"population\s*(?P<op>>|<|>=|<=|=)\s*(?P<value>\d+)",
            query
        )
        if pop_match:
            filters['population'] = {
                'op': pop_match.group('op'),
                'value': int(pop_match.group('value'))
            }
        
        # Extract income criteria
        income_match = re.search(
            r"(?:income|median income)\s*(?P<op>>|<|>=|<=|=)\s*\$?(?P<value>\d+)",
            query
        )
        if income_match:
            filters['income'] = {
                'op': income_match.group('op'),
                'value': int(income_match.group('value'))
            }
        
        return filters
    
    def _extract_sort_criteria(self, query: str) -> Optional[str]:
        """Extract sort criteria from query."""
        sort_patterns = [
            r"(?:sort|order) by (?P<criteria>.+)",
            r"ranked by (?P<criteria>.+)"
        ]
        
        for pattern in sort_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group('criteria').strip()
        
        return None
    
    def _extract_limit(self, query: str) -> int:
        """Extract result limit from query."""
        # Look for "top N" or "N counties"
        patterns = [
            r"top\s+(\d+)",
            r"(\d+)\s+(?:counties|results)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))
        
        return 10  # Default limit
```

### 6.2 Query Embedding and Semantic Search

```python
# File: src/vector/query/semantic_search.py

from typing import Dict, List, Optional, Any
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticSearchEngine:
    """
    Semantic search engine using query embeddings.
    
    Converts natural language queries to vector embeddings
    and performs semantic similarity search.
    """
    
    def __init__(
        self,
        vector_db: Any,
        query_model: str = "intfloat/e5-base-v2"
    ):
        self.vector_db = vector_db
        self.query_encoder = SentenceTransformer(query_model)
        
    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using natural language query.
        
        Args:
            query: Natural language query
            top_k: Number of results
            filter_dict: Additional filters
            
        Returns:
            List of search results with relevance scores
        """
        # Encode query
        query_embedding = self.query_encoder.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # Search vector database
        results = self.vector_db.search(
            query_vector=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        return results
    
    def hybrid_search(
        self,
        query: str,
        keywords: Optional[List[str]] = None,
        top_k: int = 10,
        alpha: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining semantic and keyword search.
        
        Args:
            query: Natural language query
            keywords: Additional keywords for filtering
            top_k: Number of results
            alpha: Weight for semantic search (1-alpha for keyword)
            
        Returns:
            Combined search results
        """
        # Semantic search
        semantic_results = self.semantic_search(query, top_k=top_k * 2)
        
        # Keyword filtering if provided
        if keywords:
            keyword_results = self._keyword_search(keywords, top_k=top_k * 2)
            
            # Combine results
            combined = self._combine_results(
                semantic_results,
                keyword_results,
                alpha=alpha,
                top_k=top_k
            )
            return combined
        
        return semantic_results[:top_k]
    
    def query_expansion(
        self,
        query: str,
        expansion_method: str = "synonyms"
    ) -> List[str]:
        """
        Expand query with related terms.
        
        Args:
            query: Original query
            expansion_method: Method for expansion
            
        Returns:
            List of expanded queries
        """
        expanded = [query]
        
        if expansion_method == "synonyms":
            # Add synonym variations
            synonym_map = {
                "flood": ["flooding", "inundation"],
                "hurricane": ["tropical storm", "cyclone"],
                "fire": ["wildfire", "blaze"],
                "high risk": ["vulnerable", "dangerous"],
                "poor": ["low income", "impoverished"]
            }
            
            for term, synonyms in synonym_map.items():
                if term in query.lower():
                    for synonym in synonyms:
                        expanded.append(query.replace(term, synonym))
        
        elif expansion_method == "llm":
            # Use LLM for query expansion
            expanded.extend(self._llm_query_expansion(query))
        
        return expanded[:5]  # Limit expansions
    
    def _llm_query_expansion(self, query: str) -> List[str]:
        """Use LLM to generate query expansions."""
        # This would integrate with the LLM interface
        prompt = f"""
        Generate 3 alternative ways to express this query about counties:
        Query: "{query}"
        
        Alternatives:
        1.
        2.
        3.
        """
        
        # Placeholder for LLM integration
        return []
```

---

## 7. Embedding Visualization

### 7.1 t-SNE and UMAP Visualization

```python
# File: src/vector/visualization/embedding_viz.py

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.manifold import TSNE
import umap

class EmbeddingVisualizer:
    """
    Visualization tools for embedding analysis.
    
    Provides interactive visualizations using Plotly:
    - t-SNE projections
    - UMAP projections
    - PCA scatter plots
    - Similarity heatmaps
    """
    
    def __init__(self, embeddings: np.ndarray, metadata: pd.DataFrame):
        self.embeddings = embeddings
        self.metadata = metadata
        self.projections = {}
        
    def compute_tsne(
        self,
        n_components: int = 2,
        perplexity: float = 30.0,
        learning_rate: float = 200.0,
        n_iter: int = 1000,
        random_state: int = 42
    ) -> np.ndarray:
        """
        Compute t-SNE projection.
        
        Args:
            n_components: 2 or 3 for visualization
            perplexity: Perplexity parameter (typically 5-50)
            learning_rate: Learning rate for optimization
            n_iter: Number of iterations
            
        Returns:
            Projected coordinates
        """
        print(f"Computing t-SNE (perplexity={perplexity})...")
        tsne = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            learning_rate=learning_rate,
            n_iter=n_iter,
            random_state=random_state,
            n_jobs=-1
        )
        projection = tsne.fit_transform(self.embeddings)
        self.projections['tsne'] = projection
        return projection
    
    def compute_umap(
        self,
        n_components: int = 2,
        n_neighbors: int = 15,
        min_dist: float = 0.1,
        metric: str = "cosine",
        random_state: int = 42
    ) -> np.ndarray:
        """
        Compute UMAP projection.
        
        Args:
            n_components: 2 or 3 for visualization
            n_neighbors: Number of neighbors for local structure
            min_dist: Minimum distance between points
            metric: Distance metric
            
        Returns:
            Projected coordinates
        """
        print(f"Computing UMAP (n_neighbors={n_neighbors})...")
        reducer = umap.UMAP(
            n_components=n_components,
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            metric=metric,
            random_state=random_state
        )
        projection = reducer.fit_transform(self.embeddings)
        self.projections['umap'] = projection
        return projection
    
    def plot_2d_scatter(
        self,
        projection_type: str = "umap",
        color_by: str = "risk_score",
        size_by: Optional[str] = None,
        hover_data: Optional[List[str]] = None,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create interactive 2D scatter plot.
        
        Args:
            projection_type: "tsne", "umap", or "pca"
            color_by: Column to use for color
            size_by: Column to use for point size
            hover_data: Additional columns for hover tooltip
            title: Plot title
            
        Returns:
            Plotly figure
        """
        if projection_type not in self.projections:
            if projection_type == "tsne":
                self.compute_tsne()
            elif projection_type == "umap":
                self.compute_umap()
            else:
                raise ValueError(f"Unknown projection: {projection_type}")
        
        projection = self.projections[projection_type]
        
        # Prepare data
        plot_df = pd.DataFrame({
            'x': projection[:, 0],
            'y': projection[:, 1],
            'county_name': self.metadata['county_name'],
            'fips': self.metadata['fips']
        })
        
        # Add color column
        if color_by in self.metadata.columns:
            plot_df['color'] = self.metadata[color_by]
        
        # Add size column
        if size_by and size_by in self.metadata.columns:
            plot_df['size'] = self.metadata[size_by]
        
        # Add hover data
        hover_cols = ['county_name', 'fips']
        if hover_data:
            for col in hover_data:
                if col in self.metadata.columns:
                    plot_df[col] = self.metadata[col]
                    hover_cols.append(col)
        
        # Create figure
        fig = px.scatter(
            plot_df,
            x='x',
            y='y',
            color='color' if 'color' in plot_df.columns else None,
            size='size' if 'size' in plot_df.columns else None,
            hover_data=hover_cols,
            title=title or f"County Embeddings ({projection_type.upper()})",
            labels={'color': color_by}
        )
        
        fig.update_layout(
            width=900,
            height=700,
            template='plotly_white'
        )
        
        return fig
    
    def plot_similarity_heatmap(
        self,
        county_fips: List[str],
        metric: str = "cosine",
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create similarity heatmap for selected counties.
        
        Args:
            county_fips: List of FIPS codes to include
            metric: Similarity metric
            title: Plot title
            
        Returns:
            Plotly figure
        """
        # Get embeddings for selected counties
        indices = [
            self.metadata[self.metadata['fips'] == fips].index[0]
            for fips in county_fips
        ]
        selected_embeddings = self.embeddings[indices]
        
        # Compute similarity matrix
        from sklearn.metrics.pairwise import cosine_similarity
        sim_matrix = cosine_similarity(selected_embeddings)
        
        # Get county names
        county_names = [
            self.metadata[self.metadata['fips'] == fips]['county_name'].iloc[0]
            for fips in county_fips
        ]
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=sim_matrix,
            x=county_names,
            y=county_names,
            colorscale='RdYlBu',
            zmid=0.5,
            text=np.round(sim_matrix, 2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title=title or "County Similarity Matrix",
            width=800,
            height=800,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def plot_domain_comparison(
        self,
        fips: str,
        domain_embeddings: Dict[str, np.ndarray]
    ) -> go.Figure:
        """
        Visualize county profile across different domains.
        
        Args:
            fips: County FIPS code
            domain_embeddings: Dictionary of domain-specific embeddings
            
        Returns:
            Plotly figure
        """
        # Get county index
        idx = self.metadata[self.metadata['fips'] == fips].index[0]
        county_name = self.metadata[self.metadata['fips'] == fips]['county_name'].iloc[0]
        
        # Create radar chart
        domains = list(domain_embeddings.keys())
        
        # Compute similarity to average for each domain
        values = []
        for domain, embeddings in domain_embeddings.items():
            county_emb = embeddings[idx]
            avg_emb = np.mean(embeddings, axis=0)
            sim = np.dot(county_emb, avg_emb) / (
                np.linalg.norm(county_emb) * np.linalg.norm(avg_emb)
            )
            values.append(sim)
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=domains + [domains[0]],
            fill='toself',
            name=county_name
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title=f"Domain Profile: {county_name}",
            showlegend=True
        )
        
        return fig
```

---

## 8. Embedding Caching Strategy

### 8.1 Multi-Tier Caching System

```python
# File: src/vector/cache/embedding_cache.py

from typing import Dict, List, Optional, Any, Union
import hashlib
import json
import pickle
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import redis
from functools import lru_cache
import diskcache as dc

@dataclass
class CacheConfig:
    """Configuration for embedding cache."""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    disk_cache_path: str = "./cache/embeddings"
    memory_cache_size: int = 1000
    ttl_seconds: int = 86400  # 24 hours
    compression: bool = True

class EmbeddingCache:
    """
    Multi-tier caching system for embeddings.
    
    Tiers:
    1. In-memory LRU cache (fastest, smallest)
    2. Redis cache (distributed, medium speed)
    3. Disk cache (persistent, slowest)
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=False
            )
            self.redis_available = self.redis_client.ping()
        except:
            self.redis_available = False
            print("Redis not available, using disk cache only")
        
        # Initialize disk cache
        self.disk_cache = dc.Cache(self.config.disk_cache_path)
        
        # Memory cache will be handled by @lru_cache decorator
        
    def _generate_key(
        self,
        county_data: Dict[str, Any],
        model_name: str,
        domain: str
    ) -> str:
        """Generate cache key from county data and model."""
        # Create deterministic key
        key_data = {
            'fips': county_data.get('fips'),
            'model': model_name,
            'domain': domain,
            'version': '1.0'  # Cache version for invalidation
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get(
        self,
        county_data: Dict[str, Any],
        model_name: str,
        domain: str = "all"
    ) -> Optional[np.ndarray]:
        """
        Retrieve embedding from cache.
        
        Args:
            county_data: County data dictionary
            model_name: Name of embedding model
            domain: Embedding domain
            
        Returns:
            Cached embedding or None
        """
        key = self._generate_key(county_data, model_name, domain)
        
        # Try memory cache first (via lru_cache on compute method)
        
        # Try Redis
        if self.redis_available:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    embedding = pickle.loads(cached)
                    return embedding
            except Exception as e:
                print(f"Redis get error: {e}")
        
        # Try disk cache
        try:
            cached = self.disk_cache.get(key)
            if cached is not None:
                # Promote to Redis if available
                if self.redis_available:
                    self._set_redis(key, cached)
                return cached
        except Exception as e:
            print(f"Disk cache get error: {e}")
        
        return None
    
    def set(
        self,
        county_data: Dict[str, Any],
        model_name: str,
        domain: str,
        embedding: np.ndarray
    ) -> bool:
        """
        Store embedding in cache.
        
        Args:
            county_data: County data dictionary
            model_name: Name of embedding model
            domain: Embedding domain
            embedding: Embedding vector
            
        Returns:
            True if successful
        """
        key = self._generate_key(county_data, model_name, domain)
        
        # Store in Redis
        if self.redis_available:
            self._set_redis(key, embedding)
        
        # Store in disk cache
        try:
            self.disk_cache.set(key, embedding)
            return True
        except Exception as e:
            print(f"Disk cache set error: {e}")
            return False
    
    def _set_redis(self, key: str, embedding: np.ndarray):
        """Store in Redis with TTL."""
        try:
            serialized = pickle.dumps(embedding)
            self.redis_client.setex(
                key,
                self.config.ttl_seconds,
                serialized
            )
        except Exception as e:
            print(f"Redis set error: {e}")
    
    def invalidate(
        self,
        fips: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Invalidate cache entries.
        
        Args:
            fips: Invalidate specific county (None for all)
            model_name: Invalidate specific model (None for all)
        """
        # This would require maintaining an index of keys
        # For now, clear all caches
        if fips is None and model_name is None:
            if self.redis_available:
                self.redis_client.flushdb()
            self.disk_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'redis_available': self.redis_available,
            'disk_size': len(self.disk_cache)
        }
        
        if self.redis_available:
            info = self.redis_client.info()
            stats['redis_keys'] = self.redis_client.dbsize()
            stats['redis_memory'] = info.get('used_memory_human', 'N/A')
        
        return stats
```

---

## 9. Folder Structure and File Paths

### 9.1 Proposed Directory Structure

```
resilience_ai/
├── src/
│   ├── vector/                          # NEW: Vector embedding module
│   │   ├── __init__.py
│   │   ├── embeddings/                  # Embedding generation
│   │   │   ├── __init__.py
│   │   │   ├── county_embedder.py       # Main county embedder
│   │   │   ├── numeric_encoder.py       # Tabular NN encoder
│   │   │   ├── text_encoder.py          # Text embedding wrapper
│   │   │   └── multimodal_fusion.py     # Multi-modal fusion
│   │   ├── databases/                   # Vector database integrations
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # Abstract base class
│   │   │   ├── pinecone_db.py           # Pinecone integration
│   │   │   ├── weaviate_db.py           # Weaviate integration
│   │   │   ├── qdrant_db.py             # Qdrant integration
│   │   │   ├── faiss_db.py              # FAISS wrapper
│   │   │   └── database_factory.py      # Factory for DB creation
│   │   ├── search/                      # Similarity search
│   │   │   ├── __init__.py
│   │   │   ├── ann_search.py            # ANN implementations
│   │   │   ├── similarity_engine.py     # Similarity computation
│   │   │   └── search_factory.py        # Search strategy factory
│   │   ├── query/                       # Query understanding
│   │   │   ├── __init__.py
│   │   │   ├── query_parser.py          # NL query parser
│   │   │   ├── semantic_search.py       # Semantic search engine
│   │   │   └── query_expansion.py       # Query expansion
│   │   ├── cache/                       # Embedding caching
│   │   │   ├── __init__.py
│   │   │   ├── embedding_cache.py       # Multi-tier cache
│   │   │   └── cache_strategies.py      # Caching strategies
│   │   ├── visualization/               # Visualization tools
│   │   │   ├── __init__.py
│   │   │   ├── embedding_viz.py         # t-SNE, UMAP plots
│   │   │   └── interactive_viz.py       # Interactive dashboards
│   │   ├── models/                      # Embedding model management
│   │   │   ├── __init__.py
│   │   │   ├── model_registry.py        # Model versioning
│   │   │   └── model_loader.py          # Model loading utilities
│   │   ├── utils/                       # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── vector_utils.py          # Vector operations
│   │   │   └── validation.py            # Input validation
│   │   └── config.py                    # Vector module configuration
│   ├── vector_space.py                  # EXISTING: Current implementation
│   └── ...
├── tests/
│   ├── vector/                          # Vector module tests
│   │   ├── test_embeddings.py
│   │   ├── test_databases.py
│   │   ├── test_search.py
│   │   ├── test_cache.py
│   │   └── test_visualization.py
│   └── ...
├── models/
│   └── vector/                          # Saved vector models
│       ├── text_encoders/
│       ├── numeric_encoders/
│       └── fusion_models/
├── data/
│   └── cache/                           # Disk cache directory
│       └── embeddings/
└── docs/
    └── vector/                            # Documentation
        ├── embedding_guide.md
        ├── database_setup.md
        └── api_reference.md
```

---

## 10. Integration Points with Existing Code

### 10.1 Integration with Current vector_space.py

```python
# File: src/vector/compat/legacy_adapter.py

"""
Adapter to integrate new vector platform with existing vector_space.py.

This allows gradual migration without breaking existing code.
"""

from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
from pathlib import Path

# Import existing classes
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from vector_space import (
    CountyVectorEncoder as LegacyEncoder,
    CountyVectorIndex as LegacyIndex,
    CrossDomainAnalyzer as LegacyAnalyzer,
    VectorSpaceManager as LegacyManager
)

# Import new classes
from ..embeddings.county_embedder import CountyEmbedder, CountyEmbeddingConfig
from ..databases.pinecone_db import PineconeVectorDB, VectorDBConfig
from ..search.similarity_engine import SimilarityEngine

class VectorSpaceAdapter:
    """
    Adapter that wraps new vector platform with legacy interface.
    
    Allows existing code to use new features without modification.
    """
    
    def __init__(
        self,
        use_new_platform: bool = True,
        config: Optional[Dict] = None
    ):
        self.use_new_platform = use_new_platform
        self.config = config or {}
        
        if use_new_platform:
            self._init_new_platform()
        else:
            self._init_legacy_platform()
    
    def _init_new_platform(self):
        """Initialize new vector platform."""
        # Create new embedder with enhanced features
        embedder_config = CountyEmbeddingConfig(
            model=self.config.get('model', 'all-MiniLM-L6-v2'),
            embedding_dim=self.config.get('embedding_dim', 384),
            multi_modal=self.config.get('multi_modal', True),
            cache_enabled=self.config.get('cache_enabled', True)
        )
        self.embedder = CountyEmbedder(embedder_config)
        
        # Initialize vector database if configured
        db_config = self.config.get('vector_db')
        if db_config:
            self.vector_db = self._create_vector_db(db_config)
        else:
            self.vector_db = None
        
        self.similarity_engine = None
        
    def _init_legacy_platform(self):
        """Initialize legacy vector space."""
        self.encoder = LegacyEncoder(
            model_name=self.config.get('model', 'all-MiniLM-L6-v2')
        )
        self.index = None
        self.analyzer = None
    
    def build(self, df: pd.DataFrame, build_domains: bool = True):
        """Build vector space (compatible with legacy interface)."""
        if self.use_new_platform:
            # Use new platform
            self.embeddings = self.embedder.encode_counties(df)
            
            if self.vector_db:
                # Store in vector database
                records = self._create_vector_records(df, self.embeddings)
                self.vector_db.upsert(records)
            
            # Initialize similarity engine
            self.similarity_engine = SimilarityEngine(
                vector_db=self.vector_db,
                county_metadata=df
            )
        else:
            # Use legacy platform
            self.encoder = LegacyEncoder()
            self.embeddings = self.encoder.encode_counties(df)
            
            from vector_space import CountyVectorIndex
            self.index = CountyVectorIndex().build_index(
                self.embeddings,
                df['fips'].tolist(),
                df['county_name'].tolist()
            )
            
            if build_domains:
                from vector_space import CrossDomainAnalyzer
                self.analyzer = CrossDomainAnalyzer(self.encoder).fit(df)
        
        return self
    
    def search_similar(
        self,
        query: Union[str, np.ndarray],
        k: int = 10
    ) -> pd.DataFrame:
        """Search for similar counties (compatible with legacy interface)."""
        if self.use_new_platform and self.similarity_engine:
            results = self.similarity_engine.find_similar_counties(
                query_fips=query if isinstance(query, str) else None,
                k=k
            )
            return pd.DataFrame([{
                'fips': r.county_fips,
                'county_name': r.county_name,
                'similarity_score': r.similarity_score,
                'rank': r.rank
            } for r in results])
        else:
            # Legacy search
            if isinstance(query, str):
                results = self.index.search_by_fips(query, k=k)
            else:
                results = self.index.search(query, k=k)
            
            return pd.DataFrame([{
                'fips': r.county_fips,
                'county_name': r.county_name,
                'similarity_score': r.similarity_score,
                'rank': r.rank
            } for r in results])
    
    def get_anomalies(self, contamination: float = 0.05) -> pd.DataFrame:
        """Get anomalous counties (compatible with legacy interface)."""
        if self.use_new_platform:
            # New anomaly detection
            from sklearn.ensemble import IsolationForest
            clf = IsolationForest(contamination=contamination)
            scores = clf.fit_predict(self.embeddings)
            
            # Format results
            results = []
            for i, score in enumerate(scores):
                if score == -1:
                    results.append({
                        'fips': self.metadata.iloc[i]['fips'],
                        'county_name': self.metadata.iloc[i]['county_name'],
                        'anomaly_score': clf.decision_function(
                            self.embeddings[i:i+1]
                        )[0]
                    })
            
            return pd.DataFrame(results)
        else:
            # Legacy anomaly detection
            return self.analyzer.detect_anomalies(contamination=contamination)
```

---

## 11. Implementation Priority Order

### 11.1 Phase 1: Foundation (Weeks 1-2)

| Priority | Task | Files | Impact |
|----------|------|-------|--------|
| 1 | Enhanced County Embedder | `src/vector/embeddings/county_embedder.py` | High |
| 2 | ANN Index (HNSW) | `src/vector/search/ann_search.py` | High |
| 3 | Embedding Cache | `src/vector/cache/embedding_cache.py` | Medium |
| 4 | Legacy Adapter | `src/vector/compat/legacy_adapter.py` | High |

### 11.2 Phase 2: Database Integration (Weeks 3-4)

| Priority | Task | Files | Impact |
|----------|------|-------|--------|
| 1 | Pinecone Integration | `src/vector/databases/pinecone_db.py` | High |
| 2 | Qdrant Integration | `src/vector/databases/qdrant_db.py` | High |
| 3 | Database Factory | `src/vector/databases/database_factory.py` | Medium |
| 4 | Similarity Engine | `src/vector/search/similarity_engine.py` | High |

### 11.3 Phase 3: Query Understanding (Weeks 5-6)

| Priority | Task | Files | Impact |
|----------|------|-------|--------|
| 1 | NL Query Parser | `src/vector/query/query_parser.py` | High |
| 2 | Semantic Search | `src/vector/query/semantic_search.py` | High |
| 3 | Query Expansion | `src/vector/query/query_expansion.py` | Medium |

### 11.4 Phase 4: Visualization (Weeks 7-8)

| Priority | Task | Files | Impact |
|----------|------|-------|--------|
| 1 | t-SNE/UMAP Viz | `src/vector/visualization/embedding_viz.py` | Medium |
| 2 | Interactive Dashboard | `src/vector/visualization/interactive_viz.py` | Medium |
| 3 | Similarity Heatmaps | Part of embedding_viz.py | Low |

### 11.5 Phase 5: Advanced Features (Weeks 9-10)

| Priority | Task | Files | Impact |
|----------|------|-------|--------|
| 1 | Multi-modal Embeddings | `src/vector/embeddings/multimodal_fusion.py` | High |
| 2 | Weaviate Integration | `src/vector/databases/weaviate_db.py` | Medium |
| 3 | Model Registry | `src/vector/models/model_registry.py` | Low |

---

## 12. Dependencies and Requirements

### 12.1 Updated requirements.txt

```txt
# Vector space and embeddings
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4
umap-learn>=0.5.4

# Vector databases
pinecone-client>=3.0.0
qdrant-client>=1.7.0
weaviate-client>=4.0.0

# Caching
redis>=5.0.0
diskcache>=5.6.0

# Visualization
plotly>=5.15.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Geographic encoding
pygeohash>=1.2.0

# Neural networks for tabular encoding
torch>=2.0.0
pytorch-tabnet>=4.1.0

# Approximate nearest neighbors
hnswlib>=0.8.0
annoy>=1.17.0

# Additional utilities
tqdm>=4.65.0
joblib>=1.3.0
```

---

## 13. Configuration Schema

### 13.1 Vector Module Configuration

```yaml
# config/vector_config.yaml

vector_embedding:
  # Embedding model settings
  model:
    name: "all-MiniLM-L6-v2"
    dimension: 384
    batch_size: 32
    normalize: true
  
  # Multi-modal settings
  multi_modal:
    enabled: true
    numeric_dim: 128
    geographic_dim: 64
    temporal_dim: 32
    fusion_method: "concatenate"
  
  # Caching settings
  cache:
    enabled: true
    memory_size: 1000
    redis:
      host: "localhost"
      port: 6379
      ttl: 86400
    disk:
      path: "./data/cache/embeddings"
  
  # Vector database settings
  vector_db:
    provider: "pinecone"  # pinecone, qdrant, weaviate, faiss
    index_name: "county_vectors"
    dimension: 768
    metric: "cosine"
    
    # Provider-specific settings
    pinecone:
      cloud: "aws"
      region: "us-east-1"
    
    qdrant:
      host: "localhost"
      port: 6333
    
    weaviate:
      host: "https://your-cluster.weaviate.network"
  
  # ANN search settings
  ann:
    algorithm: "hnsw"  # hnsw, ivf, pq, opq
    hnsw:
      m: 16
      ef_construction: 200
      ef_search: 128
    ivf:
      nlist: 100
      nprobe: 10
  
  # Similarity search settings
  similarity:
    default_metric: "cosine"
    domain_weights:
      climate: 0.25
      health: 0.25
      infrastructure: 0.25
      socioeconomic: 0.25
  
  # Query understanding settings
  query:
    expansion_enabled: true
    expansion_method: "synonyms"
    semantic_search_enabled: true
    query_model: "intfloat/e5-base-v2"
  
  # Visualization settings
  visualization:
    default_projection: "umap"
    tsne_perplexity: 30
    umap_neighbors: 15
    umap_min_dist: 0.1
```

---

## 14. Summary

This comprehensive vector embedding enhancement plan for ResilienceAI provides:

1. **Enhanced County Embeddings**: Multi-modal fusion combining text, numeric, geographic, and temporal features
2. **Vector Database Integration**: Support for Pinecone, Weaviate, Qdrant with unified interface
3. **ANN Search**: HNSW, IVF, and PQ implementations for fast approximate search
4. **Semantic Query Understanding**: Natural language query parsing and semantic search
5. **Embedding Visualization**: t-SNE, UMAP, and interactive Plotly visualizations
6. **Multi-tier Caching**: In-memory, Redis, and disk caching for performance
7. **Gradual Migration**: Legacy adapter for backward compatibility

The implementation follows a phased approach, starting with foundational enhancements and progressively adding advanced features. The modular architecture allows for flexible deployment and future extensibility.

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Author: Vector Embedding Specialist*
