# ResilienceAI Feature Engineering Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the current feature engineering implementation in ResilienceAI (66 features) and proposes advanced enhancements including automated feature generation, feature store implementation, dimensionality reduction, and temporal/geospatial feature engineering.

**Current State:** 66 features in `src/feature_engineering.py`  
**Target State:** 150+ features with automated pipelines and feature store  
**Priority:** High - Critical for model performance and agent insights

---

## 1. Current Feature Engineering Analysis

### 1.1 Existing Feature Categories (66 Features)

#### Base Features (37 features)
| Category | Features | Description |
|----------|----------|-------------|
| **Demographics** | 8 | elderly_pct, poverty_pct, disability_pct, uninsured_pct, total_population, median_income, etc. |
| **Facility Distances** | 12 | dist_nearest_hospitals_km, dist_2nd_nearest_hospitals_km, etc. |
| **Facility Counts** | 8 | count_hospitals_50km, count_ems_stations_50km, etc. |
| **Disaster History** | 6 | disaster_count, disaster_flood, disaster_severe_storm, disaster_hurricane, disaster_fire, disaster_tornado |
| **Geographic** | 3 | latitude, longitude, fips |

#### Advanced Differentiator Features (29 features)
| Feature | Formula | Purpose |
|---------|---------|---------|
| `vulnerability_index` | mean(elderly_pct, poverty_pct, disability_pct, uninsured_pct) | Composite vulnerability score |
| `isolation_index` | mean(normalized distances) | Spatial isolation metric |
| `risk_score` | 0.4*vulnerability + 0.3*isolation + 0.3*disaster_norm | Target variable |
| `compound_risk_count` | count(dimensions ≥ 75th percentile) | Multi-dimensional risk |
| `compound_risk_flag` | compound_risk_count ≥ 3 | High-risk county flag |
| `neighbor_avg_risk` | mean(risk_score of K=5 neighbors) | Risk contagion effect |
| `risk_contagion_delta` | neighbor_avg_risk - risk_score | Contagion differential |
| `disaster_acceleration` | disasters_2015_2025 / (disasters_2005_2014 + 1) | Temporal trend |
| `redundancy_score` | 1 - mean(normalized 2nd-nearest distances) | Infrastructure redundancy |
| `zero_redundancy_flag` | dist_2nd_nearest_hospital > 100km | Critical redundancy gap |
| `pop_weighted_vulnerability` | vulnerability_index * total_population | Population impact |
| `pop_weighted_risk` | risk_score * total_population | Population-weighted risk |
| `risk_score_state_pctile` | rank(risk_score) within state | State-relative ranking |
| `top_intervention` | argmax(gap scores) | Recommended intervention |
| `top_intervention_score` | max(gap scores) | Intervention priority |

### 1.2 Current Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FEATURE ENGINEERING PIPELINE                  │
├─────────────────────────────────────────────────────────────────┤
│  Raw Data → Distance Calc → Disaster Features → Vulnerability   │
│     ↓           ↓                    ↓              ↓           │
│  Census    HIFLD Facilities      FEMA Data    Demographics      │
│     ↓           ↓                    ↓              ↓           │
│     └───────────┴────────────────────┴──────────────┘           │
│                         ↓                                        │
│              ┌─────────────────────┐                            │
│              │  Advanced Features  │                            │
│              │  - Compound Risk    │                            │
│              │  - Risk Contagion   │                            │
│              │  - Acceleration     │                            │
│              │  - Redundancy       │                            │
│              │  - Population Wt    │                            │
│              │  - State Rankings   │                            │
│              │  - Gap Analysis     │                            │
│              └─────────────────────┘                            │
│                         ↓                                        │
│              county_features.csv (66 features)                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Current Limitations

1. **No Automated Feature Generation** - Manual feature creation only
2. **No Feature Selection** - All 66 features used regardless of importance
3. **No Dimensionality Reduction** - Missing PCA/t-SNE for visualization
4. **No Feature Store** - No versioning, lineage, or sharing
5. **Limited Temporal Features** - Only disaster acceleration
6. **No Interaction Features** - Missing feature cross-products
7. **No Polynomial Features** - Linear relationships only
8. **No Feature Importance Analysis** - Can't identify key drivers
9. **Static Feature Engineering** - No adaptive/recursive features
10. **Limited Geospatial Features** - Basic distance metrics only

---

## 2. Proposed Feature Engineering Enhancements

### 2.1 Enhancement Overview

| Enhancement | Priority | Complexity | Impact |
|-------------|----------|------------|--------|
| Automated Feature Generation | High | Medium | High |
| Feature Importance Analysis | High | Low | High |
| Feature Store Implementation | High | High | High |
| Dimensionality Reduction | Medium | Medium | Medium |
| Temporal Feature Engineering | High | Medium | High |
| Geospatial Features | High | Medium | High |
| Interaction Features | Medium | Low | Medium |
| Polynomial Features | Low | Low | Low |
| Feature Selection Algorithms | High | Medium | High |
| Feature Versioning | Medium | High | Medium |

### 2.2 Target Feature Count by Category

```
Current:  66 features
Target:  150+ features

Breakdown:
├── Base Features:           37 →  37 (stable)
├── Advanced Features:       29 →  45 (+16 new)
├── Temporal Features:        0 →  25 (new)
├── Geospatial Features:      0 →  20 (new)
├── Interaction Features:     0 →  15 (new)
├── Polynomial Features:      0 →  10 (new)
└── Derived Metrics:          0 →  10 (new)
```

---

## 3. Automated Feature Pipeline Architecture

### 3.1 Proposed Pipeline Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATED FEATURE ENGINEERING PIPELINE                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Raw Data    │  │   Feature    │  │   Feature    │  │   Feature   │ │
│  │   Ingestion  │→ │  Generators  │→ │   Store      │→ │   Registry  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
│         │                 │                 │                │          │
│         ↓                 ↓                 ↓                ↓          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Data        │  │  Automated   │  │  Feature     │  │  Version    │ │
│  │  Validation  │  │  Feature     │  │  Lineage     │  │  Control    │ │
│  │              │  │  Engineering │  │  Tracking    │  │             │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
│         │                 │                 │                │          │
│         └─────────────────┴─────────────────┴────────────────┘          │
│                              ↓                                          │
│                    ┌───────────────────┐                                │
│                    │  Feature Selector │                                │
│                    │  - Importance     │                                │
│                    │  - Correlation    │                                │
│                    │  - Redundancy     │                                │
│                    └───────────────────┘                                │
│                              ↓                                          │
│                    ┌───────────────────┐                                │
│                    │  Dimensionality   │                                │
│                    │  Reduction        │                                │
│                    │  (PCA, t-SNE)     │                                │
│                    └───────────────────┘                                │
│                              ↓                                          │
│                    ┌───────────────────┐                                │
│                    │  Model Training   │                                │
│                    │  & Inference      │                                │
│                    └───────────────────┘                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 File Structure

```
src/
├── feature_engineering/
│   ├── __init__.py
│   ├── base_features.py              # Current 37 base features
│   ├── advanced_features.py          # Current 29 advanced features
│   ├── temporal_features.py          # NEW: Time-based features
│   ├── geospatial_features.py        # NEW: Spatial features
│   ├── interaction_features.py       # NEW: Feature interactions
│   ├── polynomial_features.py        # NEW: Polynomial expansions
│   ├── automated_generator.py        # NEW: Auto-feature generation
│   ├── feature_selector.py           # NEW: Feature selection algorithms
│   └── feature_utils.py              # NEW: Shared utilities
├── feature_store/
│   ├── __init__.py
│   ├── store.py                      # NEW: Feature store core
│   ├── registry.py                   # NEW: Feature registry
│   ├── lineage.py                    # NEW: Feature lineage tracking
│   ├── versioning.py                 # NEW: Feature versioning
│   └── metadata.py                   # NEW: Feature metadata
└── dimensionality/
    ├── __init__.py
    ├── pca_reduction.py              # NEW: PCA implementation
    ├── tsne_visualization.py         # NEW: t-SNE for visualization
    └── feature_importance.py         # NEW: Importance analysis
```

---

## 4. New Feature Categories with Mathematical Formulas

### 4.1 Temporal Feature Engineering (25 features)

#### 4.1.1 Time-Series Features

```python
# Disaster Frequency Trends
feature: disaster_trend_slope
formula: slope from linear regression on disaster counts by year
        β = Σ((x_i - x̄)(y_i - ȳ)) / Σ((x_i - x̄)²)

feature: disaster_trend_acceleration  
formula: second derivative of trend (change in slope)
        α = (β_recent - β_historical) / Δt

feature: disaster_seasonality_strength
formula: 1 - (residual_variance / total_variance)
        S = 1 - (σ²_resid / σ²_total)

# Recency-Weighted Features
feature: disaster_recency_score
formula: Σ(disaster_i * exp(-λ * (current_year - year_i)))
        where λ = 0.1 (decay factor)

feature: weighted_disaster_count_5yr
formula: Σ(disaster_count_year * w_year)
        where w_year = [0.5, 0.7, 0.85, 0.95, 1.0] for years t-4 to t

# Cyclical Features
feature: disaster_season_peak
formula: month with max(disaster_count) grouped by incidentType

feature: disaster_interarrival_mean
formula: mean(time between consecutive disasters)
        μ_inter = Σ(t_i+1 - t_i) / (n-1)

feature: disaster_interarrival_std
formula: std(time between consecutive disasters)
        σ_inter = sqrt(Σ((t_i+1 - t_i - μ_inter)²) / (n-1))
```

#### 4.1.2 Temporal Risk Trajectory

```python
feature: risk_velocity
formula: (risk_score_current - risk_score_5yr_ago) / 5

feature: risk_acceleration
formula: (risk_velocity_current - risk_velocity_past) / Δt

feature: risk_volatility
formula: std(risk_score over 10-year window)

feature: risk_trend_direction
formula: sign of correlation coefficient between year and risk_score
        direction = sign(ρ(year, risk_score))
```

### 4.2 Geospatial Feature Engineering (20 features)

#### 4.2.1 Spatial Clustering Features

```python
# Moran's I for spatial autocorrelation
feature: risk_morans_i
formula: I = (n / W) * ΣΣ w_ij (x_i - x̄)(x_j - x̄) / Σ(x_i - x̄)²
        where W = ΣΣ w_ij, w_ij = inverse distance weight

feature: vulnerability_local_moran
formula: Local Moran's I for each county
        I_i = (x_i - x̄) * Σ w_ij (x_j - x̄)

# Getis-Ord Gi* Hotspot Analysis
feature: risk_hotspot_gi_star
formula: G_i* = Σ w_ij x_j / Σ x_j
        standardized: Z(G_i*) = (G_i* - E[G_i*]) / sqrt(Var(G_i*))

feature: vulnerability_coldspot_flag
formula: 1 if Z(G_i*) < -1.96 and x_i > x̄, else 0

feature: risk_hotspot_flag
formula: 1 if Z(G_i*) > 1.96 and x_i > x̄, else 0
```

#### 4.2.2 Network Distance Features

```python
# Graph-based connectivity
feature: network_connectivity_index
formula: degree centrality in facility network
        C_D(v) = deg(v) / (n - 1)

feature: facility_network_efficiency
formula: average inverse shortest path length
        E = (1 / (n * (n-1))) * ΣΣ (1 / d_ij)

# Accessibility metrics
feature: healthcare_accessibility_score
formula: Σ (facility_capacity_j / distance_ij^β)
        where β = 2 (gravity model exponent)

feature: emergency_response_time_estimate
formula: distance_nearest_ems / avg_ambulance_speed
        response_time = dist_km / 60 km/h * 60 min
```

#### 4.2.3 Terrain and Environmental Features

```python
feature: flood_risk_index
formula: elevation_weighted * proximity_to_water * historical_flood_rate
        FRI = (1 / elevation_m) * (1 / dist_water_km) * flood_history

feature: wildfire_risk_index
formula: vegetation_density * drought_index * historical_fire_rate
        WRI = NDVI * Palmer_index * fire_history

feature: tornado_risk_index
formula: historical_tornado_density * flat_terrain_factor
        TRI = (tornado_count / area_km2) * (1 / elevation_variance)
```

### 4.3 Interaction Features (15 features)

```python
# Vulnerability × Infrastructure interactions
feature: vulnerable_isolated_interaction
formula: vulnerability_index * isolation_index

feature: poverty_distance_interaction
formula: poverty_pct * dist_nearest_hospital_km

feature: elderly_access_interaction
formula: elderly_pct * (1 / count_hospitals_50km)

# Disaster × Demographic interactions
feature: disaster_vulnerable_interaction
formula: disaster_count * vulnerability_index

feature: flood_poverty_interaction
formula: disaster_flood * poverty_pct

feature: storm_elderly_interaction
formula: disaster_severe_storm * elderly_pct

# Multi-way interactions
feature: compound_risk_interaction
formula: vulnerability_index * isolation_index * disaster_count

feature: infrastructure_deficit_interaction
formula: (1 / density_hospitals_per10k) * (1 / density_ems_per10k)
```

### 4.4 Polynomial Features (10 features)

```python
# Quadratic terms for non-linear relationships
feature: vulnerability_squared
formula: vulnerability_index²

feature: isolation_squared
formula: isolation_index²

feature: disaster_count_squared
formula: disaster_count²

feature: poverty_squared
formula: poverty_pct²

# Cubic terms for complex relationships
feature: vulnerability_cubed
formula: vulnerability_index³

# Ratio features
feature: vulnerability_to_isolation_ratio
formula: vulnerability_index / (isolation_index + ε)

feature: disaster_to_infrastructure_ratio
formula: disaster_count / (count_hospitals_50km + 1)
```

### 4.5 Derived Composite Metrics (10 features)

```python
# Healthcare System Strain Index
feature: healthcare_strain_index
formula: (vulnerable_population / hospital_beds) * disaster_frequency
        HSI = ((elderly + disabled) / beds) * disaster_count

# Emergency Preparedness Gap
feature: preparedness_gap_index
formula: disaster_exposure - (infrastructure_density + resources)
        PGI = disaster_count - (hospital_density + ems_density)

# Social Vulnerability Amplification
feature: sv_amplification_factor
formula: Π(1 + normalized_vulnerability_component)
        SVA = (1 + elderly_norm) * (1 + poverty_norm) * (1 + disability_norm)

# Infrastructure Criticality Score
feature: infrastructure_criticality
formula: population_served / (facility_count * redundancy_score)
        IC = total_population / (count_hospitals_50km * redundancy_score)

# Climate Vulnerability Index
feature: climate_vulnerability_index
formula: Σ(disaster_type_count * climate_change_factor_type)
        CVI = Σ(d_i * ccf_i) for i in [flood, storm, fire, tornado]
```

---

## 5. Feature Store Implementation

### 5.1 Feature Store Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FEATURE STORE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     FEATURE REGISTRY                             │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │   │
│  │  │ Feature     │ │ Feature     │ │ Feature     │ │ Feature   │ │   │
│  │  │ Metadata    │ │ Schema      │ │ Statistics  │ │ Lineage   │ │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     STORAGE LAYERS                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │   │
│  │  │  Online      │  │  Offline     │  │  Metadata            │  │   │
│  │  │  Store       │  │  Store       │  │  Store               │  │   │
│  │  │  (Redis)     │  │  (Parquet)   │  │  (SQLite/PostgreSQL) │  │   │
│  │  │              │  │              │  │                      │  │   │
│  │  │ Low latency  │  │ Batch        │  │ Feature definitions  │  │   │
│  │  │ Features     │  │ training     │  │ Version history      │  │   │
│  │  │              │  │ data         │  │ Statistics           │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     API LAYER                                    │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │   │
│  │  │ get_features│ │ log_feature │ │ get_feature │ │ search_   │ │   │
│  │  │ (online)    │ │ _usage      │ │ _history    │ │ features  │ │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Feature Store Implementation Code

```python
# src/feature_store/store.py
"""
ResilienceAI Feature Store
Centralized storage and management of ML features.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path
import json
import hashlib
import pandas as pd
import numpy as np
from enum import Enum

class FeatureType(Enum):
    """Feature data types."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    GEOSPATIAL = "geospatial"

class FeatureStoreType(Enum):
    """Feature store storage types."""
    ONLINE = "online"      # Low-latency serving
    OFFLINE = "offline"    # Batch training data

@dataclass
class FeatureMetadata:
    """Metadata for a feature."""
    name: str
    description: str
    feature_type: FeatureType
    source: str
    created_at: datetime
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    statistics: Dict[str, float] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "feature_type": self.feature_type.value,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "version": self.version,
            "tags": self.tags,
            "statistics": self.statistics,
            "dependencies": self.dependencies
        }

@dataclass
class FeatureLineage:
    """Lineage tracking for feature provenance."""
    feature_name: str
    source_data: List[str]
    transformation: str
    dependencies: List[str]
    created_by: str
    created_at: datetime
    
    def compute_hash(self) -> str:
        """Compute unique hash for this lineage."""
        content = f"{self.feature_name}:{self.transformation}:{self.created_at}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

class FeatureStore:
    """
    Centralized feature store for ResilienceAI.
    
    Supports:
    - Online feature serving (low latency)
    - Offline batch retrieval (training data)
    - Feature versioning and lineage
    - Feature discovery and search
    """
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.online_path = self.base_path / "online"
        self.offline_path = self.base_path / "offline"
        self.metadata_path = self.base_path / "metadata"
        
        # Create directories
        for path in [self.online_path, self.offline_path, self.metadata_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # In-memory caches
        self._metadata_cache: Dict[str, FeatureMetadata] = {}
        self._lineage_cache: Dict[str, FeatureLineage] = {}
        
        # Load existing metadata
        self._load_metadata()
    
    def register_feature(
        self,
        name: str,
        description: str,
        feature_type: FeatureType,
        source: str,
        data: pd.DataFrame,
        store_type: FeatureStoreType = FeatureStoreType.OFFLINE,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        version: str = "1.0.0"
    ) -> str:
        """
        Register a new feature in the store.
        
        Args:
            name: Feature name
            description: Human-readable description
            feature_type: Type of feature data
            source: Source data/system
            data: Feature data (DataFrame with 'fips' and feature column)
            store_type: Online or offline storage
            tags: Optional tags for categorization
            dependencies: Other features this depends on
            version: Feature version
            
        Returns:
            Feature ID (hash)
        """
        # Compute statistics
        feature_col = data[name] if name in data.columns else data.iloc[:, -1]
        statistics = self._compute_statistics(feature_col, feature_type)
        
        # Create metadata
        metadata = FeatureMetadata(
            name=name,
            description=description,
            feature_type=feature_type,
            source=source,
            created_at=datetime.now(),
            version=version,
            tags=tags or [],
            statistics=statistics,
            dependencies=dependencies or []
        )
        
        # Create lineage
        lineage = FeatureLineage(
            feature_name=name,
            source_data=[source],
            transformation=f"register_feature:{name}",
            dependencies=dependencies or [],
            created_by="feature_store",
            created_at=datetime.now()
        )
        
        feature_id = lineage.compute_hash()
        
        # Store data
        if store_type == FeatureStoreType.ONLINE:
            self._store_online(name, data, feature_id)
        else:
            self._store_offline(name, data, feature_id)
        
        # Store metadata and lineage
        self._metadata_cache[name] = metadata
        self._lineage_cache[name] = lineage
        self._save_metadata(name, metadata)
        self._save_lineage(name, lineage)
        
        return feature_id
    
    def get_feature(
        self,
        name: str,
        fips_list: Optional[List[str]] = None,
        as_of: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Retrieve feature data.
        
        Args:
            name: Feature name
            fips_list: Optional list of FIPS codes to filter
            as_of: Optional timestamp for historical data
            
        Returns:
            DataFrame with 'fips' and feature column
        """
        # Try online store first (faster)
        online_path = self.online_path / f"{name}.parquet"
        if online_path.exists():
            df = pd.read_parquet(online_path)
        else:
            # Fall back to offline store
            offline_path = self.offline_path / f"{name}.parquet"
            if not offline_path.exists():
                raise ValueError(f"Feature '{name}' not found in store")
            df = pd.read_parquet(offline_path)
        
        # Filter by FIPS if specified
        if fips_list:
            df = df[df['fips'].isin(fips_list)]
        
        return df
    
    def get_feature_set(
        self,
        feature_names: List[str],
        fips_list: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Retrieve multiple features joined together.
        
        Args:
            feature_names: List of feature names to retrieve
            fips_list: Optional list of FIPS codes
            
        Returns:
            DataFrame with all requested features
        """
        if not feature_names:
            return pd.DataFrame()
        
        # Start with first feature
        result = self.get_feature(feature_names[0], fips_list)
        
        # Join remaining features
        for name in feature_names[1:]:
            feature_df = self.get_feature(name, fips_list)
            result = result.merge(feature_df, on='fips', how='outer')
        
        return result
    
    def search_features(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        feature_type: Optional[FeatureType] = None,
        source: Optional[str] = None
    ) -> List[FeatureMetadata]:
        """
        Search for features matching criteria.
        
        Args:
            query: Text search in name/description
            tags: Filter by tags
            feature_type: Filter by type
            source: Filter by source
            
        Returns:
            List of matching feature metadata
        """
        results = []
        
        for metadata in self._metadata_cache.values():
            # Apply filters
            if query and query.lower() not in metadata.name.lower():
                if metadata.description and query.lower() not in metadata.description.lower():
                    continue
            
            if tags and not any(tag in metadata.tags for tag in tags):
                continue
            
            if feature_type and metadata.feature_type != feature_type:
                continue
            
            if source and metadata.source != source:
                continue
            
            results.append(metadata)
        
        return results
    
    def get_feature_lineage(self, name: str) -> Optional[FeatureLineage]:
        """Get lineage information for a feature."""
        return self._lineage_cache.get(name)
    
    def get_feature_statistics(self, name: str) -> Dict[str, float]:
        """Get computed statistics for a feature."""
        metadata = self._metadata_cache.get(name)
        return metadata.statistics if metadata else {}
    
    def _compute_statistics(
        self,
        data: pd.Series,
        feature_type: FeatureType
    ) -> Dict[str, float]:
        """Compute feature statistics."""
        stats = {}
        
        if feature_type == FeatureType.NUMERIC:
            stats['mean'] = float(data.mean())
            stats['std'] = float(data.std())
            stats['min'] = float(data.min())
            stats['max'] = float(data.max())
            stats['median'] = float(data.median())
            stats['null_count'] = int(data.isnull().sum())
        elif feature_type == FeatureType.CATEGORICAL:
            stats['unique_count'] = int(data.nunique())
            stats['mode'] = str(data.mode().iloc[0]) if len(data.mode()) > 0 else None
            stats['null_count'] = int(data.isnull().sum())
        
        return stats
    
    def _store_online(self, name: str, data: pd.DataFrame, feature_id: str):
        """Store feature in online store (optimized for serving)."""
        path = self.online_path / f"{name}.parquet"
        # Keep only necessary columns
        cols_to_keep = ['fips', name] if name in data.columns else ['fips', data.columns[-1]]
        data[cols_to_keep].to_parquet(path, index=False)
    
    def _store_offline(self, name: str, data: pd.DataFrame, feature_id: str):
        """Store feature in offline store (for training)."""
        path = self.offline_path / f"{name}.parquet"
        data.to_parquet(path, index=False)
    
    def _save_metadata(self, name: str, metadata: FeatureMetadata):
        """Save feature metadata to disk."""
        path = self.metadata_path / f"{name}_metadata.json"
        with open(path, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
    
    def _save_lineage(self, name: str, lineage: FeatureLineage):
        """Save feature lineage to disk."""
        path = self.metadata_path / f"{name}_lineage.json"
        with open(path, 'w') as f:
            json.dump({
                "feature_name": lineage.feature_name,
                "source_data": lineage.source_data,
                "transformation": lineage.transformation,
                "dependencies": lineage.dependencies,
                "created_by": lineage.created_by,
                "created_at": lineage.created_at.isoformat(),
                "hash": lineage.compute_hash()
            }, f, indent=2)
    
    def _load_metadata(self):
        """Load existing metadata from disk."""
        if not self.metadata_path.exists():
            return
        
        for path in self.metadata_path.glob("*_metadata.json"):
            with open(path, 'r') as f:
                data = json.load(f)
                metadata = FeatureMetadata(
                    name=data['name'],
                    description=data['description'],
                    feature_type=FeatureType(data['feature_type']),
                    source=data['source'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    version=data['version'],
                    tags=data.get('tags', []),
                    statistics=data.get('statistics', {}),
                    dependencies=data.get('dependencies', [])
                )
                self._metadata_cache[metadata.name] = metadata


# Singleton instance
_feature_store: Optional[FeatureStore] = None

def get_feature_store(base_path: Optional[Path] = None) -> FeatureStore:
    """Get or create singleton feature store instance."""
    global _feature_store
    if _feature_store is None:
        if base_path is None:
            from config import DATA_DIR
            base_path = DATA_DIR / "feature_store"
        _feature_store = FeatureStore(base_path)
    return _feature_store
```

---

## 6. Feature Importance Analysis

### 6.1 Implementation Code

```python
# src/dimensionality/feature_importance.py
"""
Feature Importance Analysis for ResilienceAI
Multiple methods for identifying key predictive features.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
import warnings

class FeatureImportanceAnalyzer:
    """
    Comprehensive feature importance analysis using multiple methods.
    
    Methods:
    - Tree-based importance (Gini/MDI)
    - Permutation importance
    - SHAP values (if available)
    - Correlation-based importance
    - Mutual information
    """
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.importance_results: Dict[str, pd.DataFrame] = {}
    
    def analyze(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        methods: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Run comprehensive feature importance analysis.
        
        Args:
            X: Feature matrix
            y: Target variable
            methods: List of methods to use (default: all)
            
        Returns:
            Dictionary of importance results by method
        """
        if methods is None:
            methods = ['tree', 'permutation', 'correlation', 'mutual_info']
        
        results = {}
        
        if 'tree' in methods:
            results['tree_importance'] = self._tree_importance(X, y)
        
        if 'permutation' in methods:
            results['permutation_importance'] = self._permutation_importance(X, y)
        
        if 'correlation' in methods:
            results['correlation_importance'] = self._correlation_importance(X, y)
        
        if 'mutual_info' in methods:
            results['mutual_information'] = self._mutual_information(X, y)
        
        self.importance_results = results
        return results
    
    def _tree_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> pd.DataFrame:
        """Compute tree-based feature importance using Random Forest."""
        # Train Random Forest
        rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=self.random_state,
            n_jobs=-1
        )
        rf.fit(X, y)
        
        # Get importance
        importance = rf.feature_importances_
        
        # Also train Gradient Boosting for comparison
        gb = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=self.random_state
        )
        gb.fit(X, y)
        
        # Combine results
        results = pd.DataFrame({
            'feature': X.columns,
            'rf_importance': importance,
            'gb_importance': gb.feature_importances_,
            'mean_importance': (importance + gb.feature_importances_) / 2
        })
        
        return results.sort_values('mean_importance', ascending=False)
    
    def _permutation_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_repeats: int = 10
    ) -> pd.DataFrame:
        """Compute permutation importance."""
        # Train a model
        rf = RandomForestRegressor(
            n_estimators=50,
            random_state=self.random_state,
            n_jobs=-1
        )
        rf.fit(X, y)
        
        # Compute permutation importance
        perm_importance = permutation_importance(
            rf, X, y,
            n_repeats=n_repeats,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        results = pd.DataFrame({
            'feature': X.columns,
            'importance_mean': perm_importance.importances_mean,
            'importance_std': perm_importance.importances_std
        })
        
        return results.sort_values('importance_mean', ascending=False)
    
    def _correlation_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> pd.DataFrame:
        """Compute correlation-based importance."""
        correlations = []
        
        for col in X.columns:
            corr = np.abs(X[col].corr(y))
            correlations.append(corr)
        
        results = pd.DataFrame({
            'feature': X.columns,
            'abs_correlation': correlations
        })
        
        return results.sort_values('abs_correlation', ascending=False)
    
    def _mutual_information(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> pd.DataFrame:
        """Compute mutual information scores."""
        from sklearn.feature_selection import mutual_info_regression
        
        # Handle missing values
        X_clean = X.fillna(X.median())
        
        # Compute mutual information
        mi_scores = mutual_info_regression(
            X_clean, y,
            random_state=self.random_state
        )
        
        results = pd.DataFrame({
            'feature': X.columns,
            'mutual_info': mi_scores
        })
        
        return results.sort_values('mutual_info', ascending=False)
    
    def get_consensus_ranking(
        self,
        top_n: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get consensus ranking across all methods.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with consensus rankings
        """
        if not self.importance_results:
            raise ValueError("No importance results available. Run analyze() first.")
        
        # Normalize each method's scores to 0-1
        normalized_scores = {}
        
        for method, df in self.importance_results.items():
            score_col = [c for c in df.columns if 'importance' in c or 'correlation' in c or 'info' in c][0]
            scores = df[score_col].values
            
            if scores.max() > scores.min():
                normalized = (scores - scores.min()) / (scores.max() - scores.min())
            else:
                normalized = np.ones_like(scores)
            
            for i, feature in enumerate(df['feature']):
                if feature not in normalized_scores:
                    normalized_scores[feature] = []
                normalized_scores[feature].append(normalized[i])
        
        # Compute consensus score (mean of normalized scores)
        consensus = []
        for feature, scores in normalized_scores.items():
            consensus.append({
                'feature': feature,
                'consensus_score': np.mean(scores),
                'score_std': np.std(scores),
                'methods_count': len(scores)
            })
        
        results = pd.DataFrame(consensus).sort_values(
            'consensus_score', ascending=False
        )
        
        if top_n:
            results = results.head(top_n)
        
        return results
    
    def select_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        method: str = 'consensus',
        threshold: float = 0.01,
        top_n: Optional[int] = None
    ) -> List[str]:
        """
        Select important features based on analysis.
        
        Args:
            X: Feature matrix
            y: Target variable
            method: Selection method ('consensus', 'tree', 'permutation')
            threshold: Minimum importance threshold
            top_n: Maximum number of features to select
            
        Returns:
            List of selected feature names
        """
        # Run analysis if not already done
        if not self.importance_results:
            self.analyze(X, y)
        
        # Get importance scores
        if method == 'consensus':
            ranking = self.get_consensus_ranking()
            scores = ranking.set_index('feature')['consensus_score']
        elif method in self.importance_results:
            df = self.importance_results[method]
            score_col = [c for c in df.columns if 'importance' in c or 'correlation' in c][0]
            scores = df.set_index('feature')[score_col]
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Apply threshold
        selected = scores[scores >= threshold].index.tolist()
        
        # Apply top_n limit
        if top_n and len(selected) > top_n:
            selected = selected[:top_n]
        
        return selected


def analyze_feature_importance(
    df: pd.DataFrame,
    target_col: str = 'risk_score',
    exclude_cols: Optional[List[str]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Convenience function for quick feature importance analysis.
    
    Args:
        df: DataFrame with features and target
        target_col: Name of target column
        exclude_cols: Columns to exclude from analysis
        
    Returns:
        Dictionary of importance results
    """
    exclude_cols = exclude_cols or ['fips', 'county_name', 'state', 'risk_level']
    exclude_cols.append(target_col)
    
    # Prepare features
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    X = df[feature_cols].select_dtypes(include=[np.number]).fillna(0)
    y = df[target_col]
    
    # Run analysis
    analyzer = FeatureImportanceAnalyzer()
    results = analyzer.analyze(X, y)
    
    # Print summary
    print("=" * 60)
    print("Feature Importance Analysis Summary")
    print("=" * 60)
    
    consensus = analyzer.get_consensus_ranking(top_n=10)
    print("\nTop 10 Features (Consensus Ranking):")
    print(consensus.to_string(index=False))
    
    return results
```

---

## 7. Dimensionality Reduction Implementation

### 7.1 PCA Implementation

```python
# src/dimensionality/pca_reduction.py
"""
PCA Dimensionality Reduction for ResilienceAI
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import joblib

class PCAReducer:
    """
    PCA-based dimensionality reduction with feature store integration.
    """
    
    def __init__(self, n_components: Optional[int] = None, variance_threshold: float = 0.95):
        """
        Initialize PCA reducer.
        
        Args:
            n_components: Number of components (None for auto-selection)
            variance_threshold: Minimum cumulative variance to retain
        """
        self.n_components = n_components
        self.variance_threshold = variance_threshold
        self.pca: Optional[PCA] = None
        self.scaler = StandardScaler()
        self.feature_names: Optional[List[str]] = None
    
    def fit(self, X: pd.DataFrame) -> 'PCAReducer':
        """
        Fit PCA on training data.
        
        Args:
            X: Feature matrix (numeric only)
            
        Returns:
            Self for method chaining
        """
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Standardize
        X_scaled = self.scaler.fit_transform(X)
        
        # Determine number of components
        if self.n_components is None:
            # Fit full PCA first to determine components
            pca_full = PCA()
            pca_full.fit(X_scaled)
            
            # Find number of components for variance threshold
            cumsum = np.cumsum(pca_full.explained_variance_ratio_)
            self.n_components = np.argmax(cumsum >= self.variance_threshold) + 1
            print(f"Auto-selected {self.n_components} components for {self.variance_threshold:.0%} variance")
        
        # Fit final PCA
        self.pca = PCA(n_components=self.n_components)
        self.pca.fit(X_scaled)
        
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data using fitted PCA.
        
        Args:
            X: Feature matrix
            
        Returns:
            Transformed data with principal components
        """
        if self.pca is None:
            raise ValueError("PCA not fitted. Call fit() first.")
        
        # Ensure same columns
        if self.feature_names:
            X = X[self.feature_names]
        
        # Standardize and transform
        X_scaled = self.scaler.transform(X)
        X_pca = self.pca.transform(X_scaled)
        
        # Create DataFrame
        columns = [f'PC{i+1}' for i in range(self.n_components)]
        return pd.DataFrame(X_pca, columns=columns, index=X.index)
    
    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform in one step."""
        return self.fit(X).transform(X)
    
    def get_explained_variance(self) -> pd.DataFrame:
        """Get explained variance by component."""
        if self.pca is None:
            raise ValueError("PCA not fitted.")
        
        return pd.DataFrame({
            'component': [f'PC{i+1}' for i in range(self.n_components)],
            'explained_variance_ratio': self.pca.explained_variance_ratio_,
            'cumulative_variance_ratio': np.cumsum(self.pca.explained_variance_ratio_)
        })
    
    def get_feature_loadings(self, n_components: Optional[int] = None) -> pd.DataFrame:
        """
        Get feature loadings (contributions) for each component.
        
        Args:
            n_components: Number of components to include
            
        Returns:
            DataFrame with feature loadings
        """
        if self.pca is None:
            raise ValueError("PCA not fitted.")
        
        n = n_components or self.n_components
        
        loadings = pd.DataFrame(
            self.pca.components_[:n].T,
            columns=[f'PC{i+1}' for i in range(n)],
            index=self.feature_names
        )
        
        return loadings
    
    def get_top_features_per_component(
        self,
        component: int = 0,
        n_features: int = 10
    ) -> pd.DataFrame:
        """
        Get top contributing features for a component.
        
        Args:
            component: Component index (0-based)
            n_features: Number of top features to return
            
        Returns:
            DataFrame with top features and their loadings
        """
        loadings = self.get_feature_loadings(n_components=component + 1)
        pc_col = f'PC{component + 1}'
        
        top = loadings[pc_col].abs().sort_values(ascending=False).head(n_features)
        
        return pd.DataFrame({
            'feature': top.index,
            'loading': loadings.loc[top.index, pc_col],
            'abs_loading': top.values
        })
    
    def inverse_transform(self, X_pca: pd.DataFrame) -> pd.DataFrame:
        """Transform PCA components back to original feature space."""
        if self.pca is None:
            raise ValueError("PCA not fitted.")
        
        X_recovered = self.pca.inverse_transform(X_pca)
        X_unscaled = self.scaler.inverse_transform(X_recovered)
        
        return pd.DataFrame(X_unscaled, columns=self.feature_names, index=X_pca.index)
    
    def save(self, path: str):
        """Save fitted PCA to disk."""
        joblib.dump({
            'pca': self.pca,
            'scaler': self.scaler,
            'n_components': self.n_components,
            'variance_threshold': self.variance_threshold,
            'feature_names': self.feature_names
        }, path)
    
    def load(self, path: str) -> 'PCAReducer':
        """Load fitted PCA from disk."""
        data = joblib.load(path)
        self.pca = data['pca']
        self.scaler = data['scaler']
        self.n_components = data['n_components']
        self.variance_threshold = data['variance_threshold']
        self.feature_names = data['feature_names']
        return self


def apply_pca_to_counties(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    n_components: Optional[int] = None,
    variance_threshold: float = 0.95
) -> Tuple[pd.DataFrame, PCAReducer]:
    """
    Apply PCA to county features.
    
    Args:
        df: County features DataFrame
        feature_cols: Columns to use (default: all numeric)
        n_components: Number of components
        variance_threshold: Minimum variance to retain
        
    Returns:
        Tuple of (transformed DataFrame, fitted reducer)
    """
    # Select features
    if feature_cols is None:
        exclude = ['fips', 'county_name', 'state', 'risk_level', 'latitude', 'longitude']
        feature_cols = [c for c in df.columns 
                       if c not in exclude and df[c].dtype in ['float64', 'int64']]
    
    X = df[feature_cols].fillna(0)
    
    # Fit PCA
    reducer = PCAReducer(n_components=n_components, variance_threshold=variance_threshold)
    X_pca = reducer.fit_transform(X)
    
    # Add FIPS back
    X_pca['fips'] = df['fips'].values
    
    # Print summary
    print("\nPCA Summary:")
    print(f"  Original dimensions: {len(feature_cols)}")
    print(f"  Reduced dimensions: {reducer.n_components}")
    print(f"  Variance retained: {reducer.get_explained_variance()['cumulative_variance_ratio'].iloc[-1]:.2%}")
    
    print("\nTop Features by Component:")
    for i in range(min(3, reducer.n_components)):
        top = reducer.get_top_features_per_component(i, n_features=5)
        print(f"\n  PC{i+1} (explains {reducer.pca.explained_variance_ratio_[i]:.1%} variance):")
        for _, row in top.iterrows():
            print(f"    - {row['feature']}: {row['loading']:.3f}")
    
    return X_pca, reducer
```

### 7.2 t-SNE Visualization

```python
# src/dimensionality/tsne_visualization.py
"""
t-SNE Visualization for ResilienceAI Feature Exploration
"""

import numpy as np
import pandas as pd
from typing import Optional, List, Tuple
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

class TSNEVisualizer:
    """
    t-SNE visualization for high-dimensional feature exploration.
    """
    
    def __init__(
        self,
        n_components: int = 2,
        perplexity: float = 30.0,
        learning_rate: float = 200.0,
        n_iter: int = 1000,
        random_state: int = 42
    ):
        """
        Initialize t-SNE visualizer.
        
        Args:
            n_components: Output dimensions (2 or 3)
            perplexity: t-SNE perplexity parameter
            learning_rate: Learning rate for optimization
            n_iter: Number of iterations
            random_state: Random seed
        """
        self.n_components = n_components
        self.perplexity = perplexity
        self.learning_rate = learning_rate
        self.n_iter = n_iter
        self.random_state = random_state
        
        self.tsne: Optional[TSNE] = None
        self.scaler = StandardScaler()
    
    def fit_transform(
        self,
        X: pd.DataFrame,
        sample_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fit t-SNE and transform data.
        
        Args:
            X: Feature matrix
            sample_size: Optional sample size for large datasets
            
        Returns:
            DataFrame with t-SNE coordinates
        """
        # Sample if needed
        if sample_size and len(X) > sample_size:
            X = X.sample(n=sample_size, random_state=self.random_state)
            print(f"Sampled {sample_size} points for t-SNE")
        
        # Standardize
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit t-SNE
        self.tsne = TSNE(
            n_components=self.n_components,
            perplexity=self.perplexity,
            learning_rate=self.learning_rate,
            n_iter=self.n_iter,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        X_tsne = self.tsne.fit_transform(X_scaled)
        
        # Create DataFrame
        if self.n_components == 2:
            columns = ['tsne_x', 'tsne_y']
        else:
            columns = ['tsne_x', 'tsne_y', 'tsne_z']
        
        return pd.DataFrame(X_tsne, columns=columns, index=X.index)
    
    def create_visualization_data(
        self,
        df: pd.DataFrame,
        feature_cols: Optional[List[str]] = None,
        color_by: str = 'risk_score',
        sample_size: Optional[int] = 1000
    ) -> pd.DataFrame:
        """
        Create data for t-SNE visualization.
        
        Args:
            df: County features DataFrame
            feature_cols: Features to use for t-SNE
            color_by: Column to use for coloring
            sample_size: Sample size for large datasets
            
        Returns:
            DataFrame with t-SNE coordinates and metadata
        """
        # Select features
        if feature_cols is None:
            exclude = ['fips', 'county_name', 'state', 'risk_level']
            feature_cols = [c for c in df.columns 
                           if c not in exclude and df[c].dtype in ['float64', 'int64']]
        
        X = df[feature_cols].fillna(0)
        
        # Fit t-SNE
        tsne_df = self.fit_transform(X, sample_size=sample_size)
        
        # Add metadata
        tsne_df['fips'] = df.loc[tsne_df.index, 'fips'].values
        tsne_df['county_name'] = df.loc[tsne_df.index, 'county_name'].values
        
        if color_by in df.columns:
            tsne_df[color_by] = df.loc[tsne_df.index, color_by].values
        
        return tsne_df


def create_risk_clusters_visualization(
    df: pd.DataFrame,
    sample_size: int = 500
) -> pd.DataFrame:
    """
    Create t-SNE visualization colored by risk level.
    
    Args:
        df: County features DataFrame
        sample_size: Number of counties to sample
        
    Returns:
        DataFrame with t-SNE coordinates
    """
    visualizer = TSNEVisualizer(n_components=2, perplexity=30, random_state=42)
    
    return visualizer.create_visualization_data(
        df,
        color_by='risk_score',
        sample_size=sample_size
    )
```

---

## 8. Temporal Feature Engineering Implementation

```python
# src/feature_engineering/temporal_features.py
"""
Temporal Feature Engineering for ResilienceAI
Time-based features for disaster prediction and trend analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from scipy import stats
from sklearn.linear_model import LinearRegression

class TemporalFeatureEngineer:
    """
    Generate temporal features from time-series disaster data.
    """
    
    def __init__(self, reference_year: int = 2025):
        self.reference_year = reference_year
    
    def compute_all_temporal_features(
        self,
        fema_df: pd.DataFrame,
        county_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Compute all temporal features for counties.
        
        Args:
            fema_df: FEMA disaster declarations DataFrame
            county_df: County features DataFrame
            
        Returns:
            County DataFrame with temporal features added
        """
        df = county_df.copy()
        
        # Prepare FEMA data
        fema = self._prepare_fema_data(fema_df)
        
        # Compute features
        print("Computing temporal features...")
        
        # Trend features
        df = self._compute_trend_features(df, fema)
        
        # Recency features
        df = self._compute_recency_features(df, fema)
        
        # Seasonality features
        df = self._compute_seasonality_features(df, fema)
        
        # Interarrival features
        df = self._compute_interarrival_features(df, fema)
        
        # Acceleration features
        df = self._compute_acceleration_features(df, fema)
        
        print(f"  Added {len([c for c in df.columns if 'temp_' in c or 'trend_' in c or 'accel_' in c])} temporal features")
        
        return df
    
    def _prepare_fema_data(self, fema_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare FEMA data for temporal analysis."""
        fema = fema_df.copy()
        
        # Create FIPS if not exists
        if 'fips' not in fema.columns:
            fema['fips'] = (
                fema['fipsStateCode'].astype(str).str.zfill(2) +
                fema['fipsCountyCode'].astype(str).str.zfill(3)
            )
        
        # Parse dates
        fema['declarationDate'] = pd.to_datetime(fema['declarationDate'], errors='coerce')
        fema['year'] = fema['declarationDate'].dt.year
        fema['month'] = fema['declarationDate'].dt.month
        
        return fema
    
    def _compute_trend_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute disaster trend features."""
        
        def compute_trend(county_fips: str) -> Tuple[float, float]:
            """Compute trend slope and R² for a county."""
            county_disasters = fema[fema['fips'] == county_fips]
            
            if len(county_disasters) < 3:
                return 0.0, 0.0
            
            # Group by year
            yearly = county_disasters.groupby('year').size().reset_index(name='count')
            
            # Linear regression
            X = yearly['year'].values.reshape(-1, 1)
            y = yearly['count'].values
            
            model = LinearRegression().fit(X, y)
            slope = model.coef_[0]
            r2 = model.score(X, y)
            
            return slope, r2
        
        # Compute for each county
        trends = []
        for fips in df['fips']:
            slope, r2 = compute_trend(fips)
            trends.append({'fips': fips, 'trend_slope': slope, 'trend_r2': r2})
        
        trends_df = pd.DataFrame(trends)
        df = df.merge(trends_df, on='fips', how='left')
        
        return df
    
    def _compute_recency_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute recency-weighted disaster features."""
        
        # Years to consider
        recent_years = [self.reference_year - i for i in range(5)]
        
        # Compute recency-weighted count
        def compute_recency_score(county_fips: str) -> float:
            county_disasters = fema[fema['fips'] == county_fips]
            
            score = 0.0
            for i, year in enumerate(reversed(recent_years)):
                weight = 0.5 + (i * 0.125)  # [0.5, 0.625, 0.75, 0.875, 1.0]
                count = len(county_disasters[county_disasters['year'] == year])
                score += count * weight
            
            return score
        
        df['recency_weighted_disasters'] = df['fips'].apply(compute_recency_score)
        
        # Years since last disaster
        def years_since_last(county_fips: str) -> int:
            county_disasters = fema[fema['fips'] == county_fips]
            if len(county_disasters) == 0:
                return 999
            last_year = county_disasters['year'].max()
            return self.reference_year - last_year
        
        df['years_since_last_disaster'] = df['fips'].apply(years_since_last)
        
        return df
    
    def _compute_seasonality_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute disaster seasonality features."""
        
        # Peak disaster month
        def get_peak_month(county_fips: str) -> int:
            county_disasters = fema[fema['fips'] == county_fips]
            if len(county_disasters) < 3:
                return 0
            
            monthly = county_disasters.groupby('month').size()
            return monthly.idxmax() if len(monthly) > 0 else 0
        
        df['disaster_peak_month'] = df['fips'].apply(get_peak_month)
        
        # Seasonality strength (coefficient of variation)
        def get_seasonality_strength(county_fips: str) -> float:
            county_disasters = fema[fema['fips'] == county_fips]
            if len(county_disasters) < 12:
                return 0.0
            
            monthly = county_disasters.groupby('month').size()
            if monthly.mean() > 0:
                return monthly.std() / monthly.mean()
            return 0.0
        
        df['disaster_seasonality_cv'] = df['fips'].apply(get_seasonality_strength)
        
        return df
    
    def _compute_interarrival_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute interarrival time features."""
        
        def compute_interarrival_stats(county_fips: str) -> Tuple[float, float]:
            county_disasters = fema[fema['fips'] == county_fips]
            if len(county_disasters) < 2:
                return 999.0, 0.0
            
            # Sort by date
            dates = county_disasters['declarationDate'].sort_values()
            
            # Compute interarrival times in days
            interarrival = (dates.diff().dt.days).dropna()
            
            return interarrival.mean(), interarrival.std()
        
        interarrival_data = []
        for fips in df['fips']:
            mean_ia, std_ia = compute_interarrival_stats(fips)
            interarrival_data.append({
                'fips': fips,
                'interarrival_mean_days': mean_ia,
                'interarrival_std_days': std_ia
            })
        
        interarrival_df = pd.DataFrame(interarrival_data)
        df = df.merge(interarrival_df, on='fips', how='left')
        
        return df
    
    def _compute_acceleration_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute disaster acceleration features."""
        
        # Compare recent 5 years vs previous 5 years
        recent_period = (fema['year'] >= self.reference_year - 4) & (fema['year'] <= self.reference_year)
        prior_period = (fema['year'] >= self.reference_year - 9) & (fema['year'] <= self.reference_year - 5)
        
        recent_counts = fema[recent_period].groupby('fips').size().reset_index(name='disasters_recent_5yr')
        prior_counts = fema[prior_period].groupby('fips').size().reset_index(name='disasters_prior_5yr')
        
        df = df.merge(recent_counts, on='fips', how='left')
        df = df.merge(prior_counts, on='fips', how='left')
        
        df['disasters_recent_5yr'] = df['disasters_recent_5yr'].fillna(0)
        df['disasters_prior_5yr'] = df['disasters_prior_5yr'].fillna(0)
        
        # Acceleration ratio
        df['disaster_5yr_acceleration'] = df['disasters_recent_5yr'] / (df['disasters_prior_5yr'] + 1)
        
        return df


def add_temporal_features(
    county_df: pd.DataFrame,
    fema_df: pd.DataFrame,
    reference_year: int = 2025
) -> pd.DataFrame:
    """
    Convenience function to add all temporal features.
    
    Args:
        county_df: County features DataFrame
        fema_df: FEMA disaster data
        reference_year: Reference year for recency calculations
        
    Returns:
        DataFrame with temporal features added
    """
    engineer = TemporalFeatureEngineer(reference_year=reference_year)
    return engineer.compute_all_temporal_features(fema_df, county_df)
```

---

## 9. Integration Points with Existing Code

### 9.1 Modified Pipeline Integration

```python
# src/feature_engineering/__init__.py
"""
ResilienceAI Feature Engineering Package
"""

from .base_features import compute_base_features
from .advanced_features import compute_advanced_features
from .temporal_features import add_temporal_features
from .geospatial_features import add_geospatial_features
from .interaction_features import add_interaction_features
from .automated_generator import AutoFeatureGenerator
from .feature_selector import FeatureSelector

__all__ = [
    'compute_base_features',
    'compute_advanced_features',
    'add_temporal_features',
    'add_geospatial_features',
    'add_interaction_features',
    'AutoFeatureGenerator',
    'FeatureSelector'
]
```

### 9.2 Enhanced Main Pipeline

```python
# src/feature_engineering/enhanced_pipeline.py
"""
Enhanced Feature Engineering Pipeline
Integrates all new feature engineering capabilities.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List

from config import RAW_DIR, PROCESSED_DIR
from feature_store.store import get_feature_store
from .base_features import compute_base_features
from .advanced_features import compute_advanced_features
from .temporal_features import add_temporal_features
from .geospatial_features import add_geospatial_features
from .interaction_features import add_interaction_features
from .polynomial_features import add_polynomial_features
from .automated_generator import AutoFeatureGenerator
from .feature_selector import FeatureSelector
from dimensionality.feature_importance import FeatureImportanceAnalyzer
from dimensionality.pca_reduction import apply_pca_to_counties

class EnhancedFeaturePipeline:
    """
    Enhanced feature engineering pipeline with automation and feature store.
    """
    
    def __init__(
        self,
        use_feature_store: bool = True,
        auto_generate: bool = True,
        apply_selection: bool = True,
        target_feature_count: int = 100
    ):
        self.use_feature_store = use_feature_store
        self.auto_generate = auto_generate
        self.apply_selection = apply_selection
        self.target_feature_count = target_feature_count
        
        self.feature_store = get_feature_store() if use_feature_store else None
        self.auto_generator = AutoFeatureGenerator() if auto_generate else None
        self.selector = FeatureSelector() if apply_selection else None
        self.importance_analyzer = FeatureImportanceAnalyzer()
    
    def run(
        self,
        save_intermediate: bool = True,
        apply_pca: bool = False,
        pca_variance: float = 0.95
    ) -> pd.DataFrame:
        """
        Run the enhanced feature engineering pipeline.
        
        Args:
            save_intermediate: Save intermediate results
            apply_pca: Apply PCA dimensionality reduction
            pca_variance: Variance threshold for PCA
            
        Returns:
            DataFrame with engineered features
        """
        print("=" * 70)
        print("ResilienceAI - Enhanced Feature Engineering Pipeline")
        print("=" * 70)
        
        # Load raw data
        print("\n[1/8] Loading raw data...")
        census = pd.read_csv(RAW_DIR / "census_demographics.csv", dtype={"fips": str})
        centroids = pd.read_csv(RAW_DIR / "county_centroids.csv", dtype={"fips": str})
        fema = pd.read_csv(RAW_DIR / "fema_disasters.csv")
        
        # Merge base data
        df = census.merge(centroids[["fips", "latitude", "longitude"]], on="fips", how="left")
        df = df.dropna(subset=["latitude", "longitude"])
        print(f"  Base counties: {len(df)}")
        
        # Compute base features
        print("\n[2/8] Computing base features...")
        df = compute_base_features(df)
        print(f"  Features after base: {len(df.columns)}")
        
        # Compute advanced features
        print("\n[3/8] Computing advanced features...")
        df = compute_advanced_features(df, fema)
        print(f"  Features after advanced: {len(df.columns)}")
        
        # Add temporal features
        print("\n[4/8] Adding temporal features...")
        df = add_temporal_features(df, fema)
        print(f"  Features after temporal: {len(df.columns)}")
        
        # Add geospatial features
        print("\n[5/8] Adding geospatial features...")
        df = add_geospatial_features(df)
        print(f"  Features after geospatial: {len(df.columns)}")
        
        # Add interaction features
        print("\n[6/8] Adding interaction features...")
        df = add_interaction_features(df)
        print(f"  Features after interactions: {len(df.columns)}")
        
        # Auto-generate features
        if self.auto_generate:
            print("\n[7/8] Auto-generating features...")
            df = self.auto_generator.generate(df)
            print(f"  Features after auto-generation: {len(df.columns)}")
        
        # Feature importance analysis
        print("\n[8/8] Analyzing feature importance...")
        if 'risk_score' in df.columns:
            importance_results = self.importance_analyzer.analyze(
                df.select_dtypes(include=['float64', 'int64']).fillna(0),
                df['risk_score']
            )
            
            consensus = self.importance_analyzer.get_consensus_ranking(top_n=15)
            print("\n  Top 15 Most Important Features:")
            for i, row in consensus.iterrows():
                print(f"    {i+1:2d}. {row['feature'][:40]:<40} {row['consensus_score']:.4f}")
        
        # Feature selection
        if self.apply_selection and len(df.columns) > self.target_feature_count:
            print(f"\n[9/8] Selecting top {self.target_feature_count} features...")
            selected = self.selector.select_features(
                df,
                target_col='risk_score',
                n_features=self.target_feature_count
            )
            
            # Keep essential columns
            essential = ['fips', 'county_name', 'state', 'latitude', 'longitude', 'risk_score', 'risk_level']
            selected = list(set(selected + essential))
            
            df = df[selected]
            print(f"  Features after selection: {len(df.columns)}")
        
        # Store features in feature store
        if self.feature_store:
            print("\n[10/8] Registering features in feature store...")
            for col in df.columns:
                if col not in ['fips', 'county_name', 'state']:
                    self.feature_store.register_feature(
                        name=col,
                        description=f"Engineered feature: {col}",
                        feature_type=self._infer_feature_type(df[col]),
                        source="enhanced_pipeline",
                        data=df[['fips', col]]
                    )
            print(f"  Registered {len(df.columns) - 3} features")
        
        # Apply PCA if requested
        if apply_pca:
            print("\n[11/8] Applying PCA dimensionality reduction...")
            pca_df, reducer = apply_pca_to_counties(df, variance_threshold=pca_variance)
            
            # Save PCA model
            reducer.save(PROCESSED_DIR / "pca_reducer.joblib")
            
            # Merge PCA components back
            df = df.merge(pca_df[['fips'] + [c for c in pca_df.columns if c.startswith('PC')]], on='fips')
        
        # Save final output
        output_path = PROCESSED_DIR / "county_features_enhanced.csv"
        df.to_csv(output_path, index=False)
        
        print("\n" + "=" * 70)
        print("Enhanced Feature Engineering Complete!")
        print(f"  Counties: {len(df)}")
        print(f"  Features: {len(df.columns)}")
        print(f"  Output: {output_path}")
        print("=" * 70)
        
        return df
    
    def _infer_feature_type(self, series: pd.Series) -> 'FeatureType':
        """Infer feature type from data."""
        from feature_store.store import FeatureType
        
        if series.dtype == 'bool':
            return FeatureType.BOOLEAN
        elif series.dtype in ['int64', 'float64']:
            return FeatureType.NUMERIC
        elif series.dtype == 'datetime64[ns]':
            return FeatureType.DATETIME
        else:
            return FeatureType.CATEGORICAL


def run_enhanced_pipeline(**kwargs) -> pd.DataFrame:
    """Convenience function to run enhanced pipeline."""
    pipeline = EnhancedFeaturePipeline()
    return pipeline.run(**kwargs)
```

---

## 10. Implementation Priority Order

### Phase 1: Foundation (Week 1-2) - HIGH PRIORITY

| Task | Effort | Impact | Files |
|------|--------|--------|-------|
| Feature Store Core | 3 days | High | `src/feature_store/store.py`, `registry.py` |
| Feature Importance Analysis | 2 days | High | `src/dimensionality/feature_importance.py` |
| Temporal Features | 2 days | High | `src/feature_engineering/temporal_features.py` |
| Geospatial Features | 2 days | High | `src/feature_engineering/geospatial_features.py` |

### Phase 2: Enhancement (Week 3-4) - MEDIUM PRIORITY

| Task | Effort | Impact | Files |
|------|--------|--------|-------|
| Interaction Features | 1 day | Medium | `src/feature_engineering/interaction_features.py` |
| Polynomial Features | 1 day | Low | `src/feature_engineering/polynomial_features.py` |
| PCA Reduction | 2 days | Medium | `src/dimensionality/pca_reduction.py` |
| t-SNE Visualization | 1 day | Medium | `src/dimensionality/tsne_visualization.py` |

### Phase 3: Automation (Week 5-6) - MEDIUM PRIORITY

| Task | Effort | Impact | Files |
|------|--------|--------|-------|
| Auto Feature Generator | 3 days | High | `src/feature_engineering/automated_generator.py` |
| Feature Selector | 2 days | High | `src/feature_engineering/feature_selector.py` |
| Feature Lineage Tracking | 2 days | Medium | `src/feature_store/lineage.py` |
| Feature Versioning | 2 days | Medium | `src/feature_store/versioning.py` |

### Phase 4: Integration (Week 7-8) - LOW PRIORITY

| Task | Effort | Impact | Files |
|------|--------|--------|-------|
| Enhanced Pipeline Integration | 2 days | High | `src/feature_engineering/enhanced_pipeline.py` |
| Feature Store API | 2 days | Medium | `src/feature_store/api.py` |
| Monitoring & Alerting | 2 days | Low | `src/feature_store/monitoring.py` |
| Documentation & Tests | 2 days | Medium | Tests, docs |

---

## 11. Summary

### Current State: 66 Features
- 37 base features (demographics, distances, counts)
- 29 advanced features (indices, clusters, rankings)

### Target State: 150+ Features
- 37 base features (stable)
- 45 advanced features (+16 new)
- 25 temporal features (new)
- 20 geospatial features (new)
- 15 interaction features (new)
- 10 polynomial features (new)
- 10 derived composite metrics (new)

### Key Deliverables

1. **Feature Store** - Centralized storage with versioning and lineage
2. **Automated Pipeline** - Self-improving feature generation
3. **Feature Selection** - Data-driven feature importance analysis
4. **Dimensionality Reduction** - PCA and t-SNE for visualization
5. **Temporal Features** - Time-series trend and acceleration analysis
6. **Geospatial Features** - Spatial clustering and network analysis

### Expected Impact

- **Model Performance**: 15-25% improvement in risk prediction accuracy
- **Feature Discovery**: Automated identification of predictive patterns
- **Maintainability**: Centralized feature management with versioning
- **Interpretability**: Feature importance and lineage tracking
- **Scalability**: Efficient feature serving for real-time predictions

---

*Document generated for ResilienceAI Feature Engineering Enhancement*  
*Target: claw-autonomous branch*  
*Analysis Date: 2026*
