"""
Vector Database Factory and Implementations

This module provides a unified interface for multiple vector databases:
- Pinecone (managed cloud service)
- Weaviate (graph + vector database)
- Qdrant (open-source with managed option)
- FAISS (local, in-memory)

Author: Vector Embedding Specialist
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from pathlib import Path
import json


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
    provider: VectorDBProvider = VectorDBProvider.FAISS
    api_key: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    index_name: str = "county_vectors"
    dimension: int = 768
    metric: str = "cosine"  # cosine, euclidean, dotproduct
    
    # Provider-specific settings
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    
    qdrant_grpc_port: int = 6334
    
    faiss_index_path: Optional[str] = None


class BaseVectorDB(ABC):
    """
    Abstract base class for vector database implementations.
    
    All vector database implementations should inherit from this class
    and implement the abstract methods.
    """
    
    def __init__(self, config: VectorDBConfig):
        """
        Initialize the vector database.
        
        Args:
            config: Vector database configuration
        """
        self.config = config
        self.client = None
        self._is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to vector database."""
        pass
    
    @abstractmethod
    def create_index(
        self,
        index_name: Optional[str] = None,
        dimension: Optional[int] = None,
        metric: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Create a new vector index.
        
        Args:
            index_name: Name of the index
            dimension: Vector dimension
            metric: Distance metric
            **kwargs: Provider-specific parameters
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None
    ) -> bool:
        """
        Insert or update vectors in the database.
        
        Args:
            records: List of vector records
            namespace: Optional namespace/collection
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            namespace: Optional namespace/collection
            
        Returns:
            List of search results
        """
        pass
    
    @abstractmethod
    def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> bool:
        """
        Delete vectors by ID.
        
        Args:
            ids: List of vector IDs to delete
            namespace: Optional namespace/collection
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def fetch(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> List[VectorRecord]:
        """
        Fetch vectors by ID.
        
        Args:
            ids: List of vector IDs to fetch
            namespace: Optional namespace/collection
            
        Returns:
            List of vector records
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        pass
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._is_connected


class VectorDBFactory:
    """
    Factory class for creating vector database instances.
    
    Example:
        >>> config = VectorDBConfig(provider=VectorDBProvider.PINECONE)
        >>> db = VectorDBFactory.create(config)
        >>> db.connect()
    """
    
    @staticmethod
    def create(config: VectorDBConfig) -> BaseVectorDB:
        """
        Create a vector database instance based on configuration.
        
        Args:
            config: Vector database configuration
            
        Returns:
            Vector database instance
        """
        if config.provider == VectorDBProvider.PINECONE:
            from .pinecone_db import PineconeVectorDB
            return PineconeVectorDB(config)
        
        elif config.provider == VectorDBProvider.WEAVIATE:
            from .weaviate_db import WeaviateVectorDB
            return WeaviateVectorDB(config)
        
        elif config.provider == VectorDBProvider.QDRANT:
            from .qdrant_db import QdrantVectorDB
            return QdrantVectorDB(config)
        
        elif config.provider == VectorDBProvider.FAISS:
            from .faiss_db import FAISSVectorDB
            return FAISSVectorDB(config)
        
        else:
            raise ValueError(f"Unknown provider: {config.provider}")
    
    @staticmethod
    def create_from_env() -> BaseVectorDB:
        """
        Create vector database from environment variables.
        
        Environment variables:
        - VECTOR_DB_PROVIDER: Provider name
        - VECTOR_DB_API_KEY: API key
        - VECTOR_DB_HOST: Host URL
        - VECTOR_DB_INDEX: Index name
        
        Returns:
            Vector database instance
        """
        import os
        
        provider = os.getenv('VECTOR_DB_PROVIDER', 'faiss')
        api_key = os.getenv('VECTOR_DB_API_KEY')
        host = os.getenv('VECTOR_DB_HOST')
        index_name = os.getenv('VECTOR_DB_INDEX', 'county_vectors')
        
        provider_map = {
            'pinecone': VectorDBProvider.PINECONE,
            'weaviate': VectorDBProvider.WEAVIATE,
            'qdrant': VectorDBProvider.QDRANT,
            'faiss': VectorDBProvider.FAISS
        }
        
        config = VectorDBConfig(
            provider=provider_map.get(provider, VectorDBProvider.FAISS),
            api_key=api_key,
            host=host,
            index_name=index_name
        )
        
        return VectorDBFactory.create(config)


class FAISSVectorDB(BaseVectorDB):
    """
    FAISS-based local vector database.
    
    This is a simple wrapper around FAISS for local storage.
    """
    
    def __init__(self, config: VectorDBConfig):
        super().__init__(config)
        self.index = None
        self.records = {}
        
    def connect(self) -> bool:
        """Connect to FAISS (no-op for local)."""
        self._is_connected = True
        return True
    
    def create_index(
        self,
        index_name: Optional[str] = None,
        dimension: Optional[int] = None,
        metric: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Create FAISS index."""
        from .ann_search import FAISSANNIndex, ANNConfig, ANNAlgorithm
        
        dimension = dimension or self.config.dimension
        metric = metric or self.config.metric
        
        ann_config = ANNConfig(
            algorithm=ANNAlgorithm.EXACT,
            metric=metric
        )
        
        self.index = FAISSANNIndex(dimension, ann_config)
        return True
    
    def upsert(
        self,
        records: List[VectorRecord],
        namespace: Optional[str] = None
    ) -> bool:
        """Upsert vectors to FAISS."""
        if self.index is None:
            if len(records) > 0:
                dimension = len(records[0].vector)
                self.create_index(dimension=dimension)
        
        vectors = np.array([r.vector for r in records])
        ids = [r.id for r in records]
        
        # Store metadata
        for record in records:
            self.records[record.id] = record.metadata
        
        # Build or update index
        if not self.index._is_trained:
            self.index.build_index(vectors, ids)
        else:
            self.index.add_vectors(vectors, ids)
        
        return True
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: Optional[str] = None
    ) -> List[SearchResult]:
        """Search FAISS index."""
        if self.index is None:
            return []
        
        distances, indices = self.index.search(query_vector, k=top_k)
        
        results = []
        for dist, idx in zip(distances, indices):
            id = self.index.ids[idx]
            
            # Apply filter if specified
            if filter_dict:
                metadata = self.records.get(id, {})
                if not all(metadata.get(k) == v for k, v in filter_dict.items()):
                    continue
            
            results.append(SearchResult(
                id=id,
                score=float(dist),
                metadata=self.records.get(id, {})
            ))
        
        return results
    
    def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> bool:
        """Delete vectors from FAISS."""
        if self.index is None:
            return False
        
        self.index.remove_vectors(ids)
        
        for id in ids:
            if id in self.records:
                del self.records[id]
        
        return True
    
    def fetch(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> List[VectorRecord]:
        """Fetch vectors from FAISS."""
        results = []
        
        for id in ids:
            if id in self.index.ids:
                idx = self.index.ids.index(id)
                vector = self.index.vectors[idx]
                metadata = self.records.get(id, {})
                
                results.append(VectorRecord(
                    id=id,
                    vector=vector,
                    metadata=metadata
                ))
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get FAISS index statistics."""
        if self.index is None:
            return {'status': 'not_initialized'}
        
        return {
            'provider': 'faiss',
            'n_vectors': len(self.index.ids),
            'dimension': self.index.dimension,
            'is_trained': self.index._is_trained
        }
    
    def save(self, path: str):
        """Save FAISS index to disk."""
        if self.index:
            self.index.save(path)
            
            # Save metadata
            with open(path + '.meta', 'w') as f:
                json.dump(self.records, f)
    
    def load(self, path: str):
        """Load FAISS index from disk."""
        from .ann_search import FAISSANNIndex, ANNConfig
        
        self.index = FAISSANNIndex(self.config.dimension, ANNConfig())
        self.index.load(path)
        
        # Load metadata
        with open(path + '.meta', 'r') as f:
            self.records = json.load(f)


# Convenience functions
def create_pinecone_db(
    api_key: str,
    index_name: str = "county_vectors",
    dimension: int = 768,
    metric: str = "cosine"
) -> BaseVectorDB:
    """
    Create a Pinecone vector database.
    
    Args:
        api_key: Pinecone API key
        index_name: Index name
        dimension: Vector dimension
        metric: Distance metric
        
    Returns:
        Configured PineconeVectorDB
    """
    config = VectorDBConfig(
        provider=VectorDBProvider.PINECONE,
        api_key=api_key,
        index_name=index_name,
        dimension=dimension,
        metric=metric
    )
    
    return VectorDBFactory.create(config)


def create_qdrant_db(
    host: str = "localhost",
    port: int = 6333,
    index_name: str = "county_vectors",
    dimension: int = 768,
    metric: str = "cosine"
) -> BaseVectorDB:
    """
    Create a Qdrant vector database.
    
    Args:
        host: Qdrant host
        port: Qdrant port
        index_name: Collection name
        dimension: Vector dimension
        metric: Distance metric
        
    Returns:
        Configured QdrantVectorDB
    """
    config = VectorDBConfig(
        provider=VectorDBProvider.QDRANT,
        host=host,
        port=port,
        index_name=index_name,
        dimension=dimension,
        metric=metric
    )
    
    return VectorDBFactory.create(config)


def create_faiss_db(
    index_path: Optional[str] = None,
    dimension: int = 768,
    metric: str = "cosine"
) -> BaseVectorDB:
    """
    Create a FAISS vector database.
    
    Args:
        index_path: Path to save/load index
        dimension: Vector dimension
        metric: Distance metric
        
    Returns:
        Configured FAISSVectorDB
    """
    config = VectorDBConfig(
        provider=VectorDBProvider.FAISS,
        index_name="faiss_index",
        dimension=dimension,
        metric=metric,
        faiss_index_path=index_path
    )
    
    return VectorDBFactory.create(config)


if __name__ == "__main__":
    # Example usage
    print("VectorDBFactory - Example Usage")
    print("=" * 50)
    
    # Create FAISS database
    config = VectorDBConfig(
        provider=VectorDBProvider.FAISS,
        dimension=128,
        metric="cosine"
    )
    
    db = VectorDBFactory.create(config)
    db.connect()
    print(f"\nCreated {config.provider.value} database")
    
    # Create sample records
    np.random.seed(42)
    n_records = 100
    
    records = [
        VectorRecord(
            id=f"county_{i:04d}",
            vector=np.random.randn(128).astype(np.float32),
            metadata={
                'county_name': f"County {i}",
                'state': np.random.choice(['AL', 'CA', 'NY']),
                'risk_score': float(np.random.rand())
            }
        )
        for i in range(n_records)
    ]
    
    print(f"\nUpserting {n_records} records...")
    db.upsert(records)
    
    # Search
    print("\nSearching...")
    query = np.random.randn(128).astype(np.float32)
    results = db.search(query, top_k=5)
    
    print(f"\nTop 5 results:")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r.id} (score: {r.score:.4f})")
    
    # Get stats
    stats = db.get_stats()
    print(f"\nDatabase stats: {stats}")
    
    print("\nVectorDBFactory ready for use!")
