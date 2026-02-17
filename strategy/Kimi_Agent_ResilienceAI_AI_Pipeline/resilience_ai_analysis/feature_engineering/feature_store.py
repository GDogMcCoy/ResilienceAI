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
