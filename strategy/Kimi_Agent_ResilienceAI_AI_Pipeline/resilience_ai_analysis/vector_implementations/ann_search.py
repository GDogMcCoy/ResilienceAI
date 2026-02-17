"""
Approximate Nearest Neighbor (ANN) Search Implementations

This module provides multiple ANN algorithms for fast similarity search:
- HNSW: Hierarchical Navigable Small World (best for high-dimensional data)
- IVF: Inverted File Index (good balance of speed and accuracy)
- PQ: Product Quantization (memory-efficient)
- OPQ: Optimized Product Quantization (improved PQ)

Author: Vector Embedding Specialist
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from enum import Enum
from dataclasses import dataclass
import warnings

# FAISS import with fallback
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    warnings.warn("FAISS not installed. ANN search will use sklearn fallback.")


class ANNAlgorithm(str, Enum):
    """Supported ANN algorithms."""
    HNSW = "hnsw"                    # Hierarchical Navigable Small World
    IVF = "ivf"                      # Inverted File Index
    PQ = "pq"                        # Product Quantization
    OPQ = "opq"                      # Optimized Product Quantization
    LSH = "lsh"                      # Locality Sensitive Hashing
    EXACT = "exact"                  # Exact search (brute force)


@dataclass
class ANNConfig:
    """Configuration for ANN index."""
    algorithm: ANNAlgorithm = ANNAlgorithm.HNSW
    
    # HNSW parameters
    m: int = 16                      # Connections per layer
    ef_construction: int = 200       # Construction-time search depth
    ef_search: int = 128             # Search-time depth
    
    # IVF parameters
    nlist: int = 100                 # Number of clusters
    nprobe: int = 10                 # Clusters to search
    
    # PQ/OPQ parameters
    nbits: int = 8                   # Bits per subvector
    
    # General parameters
    metric: str = "cosine"           # Distance metric
    use_gpu: bool = False            # Use GPU acceleration


class FAISSANNIndex:
    """
    FAISS-based ANN index implementations.
    
    This class provides a unified interface for multiple ANN algorithms,
    allowing users to choose the best algorithm for their use case.
    
    Algorithms:
    - HNSW: Best for high-dimensional data, very fast search
    - IVF: Good balance of speed and accuracy for large datasets
    - PQ: Memory-efficient, good for very large datasets
    - OPQ: Improved PQ with rotation optimization
    
    Example:
        >>> config = ANNConfig(algorithm=ANNAlgorithm.HNSW, m=32)
        >>> index = FAISSANNIndex(dimension=768, config=config)
        >>> index.build_index(vectors)
        >>> distances, indices = index.search(query_vector, k=10)
    """
    
    def __init__(self, dimension: int, config: Optional[ANNConfig] = None):
        """
        Initialize ANN index.
        
        Args:
            dimension: Dimension of embedding vectors
            config: ANN configuration
        """
        self.dimension = dimension
        self.config = config or ANNConfig()
        self.index = None
        self.vectors = None
        self.ids = None
        self._is_trained = False
        
        if not FAISS_AVAILABLE:
            print("Warning: FAISS not available. Using sklearn fallback.")
    
    def build_index(
        self,
        vectors: np.ndarray,
        ids: Optional[List[str]] = None
    ) -> 'FAISSANNIndex':
        """
        Build ANN index from vectors.
        
        Args:
            vectors: Array of embedding vectors (n x dimension)
            ids: Optional list of IDs for each vector
            
        Returns:
            Self for method chaining
        """
        self.vectors = vectors.astype(np.float32)
        self.ids = ids or [str(i) for i in range(len(vectors))]
        
        if FAISS_AVAILABLE:
            self.index = self._build_faiss_index()
        else:
            self.index = self._build_fallback_index()
        
        self._is_trained = True
        print(f"Built {self.config.algorithm.value} index with {len(vectors)} vectors")
        
        return self
    
    def _build_faiss_index(self) -> faiss.Index:
        """Build FAISS index based on algorithm."""
        # Normalize vectors for cosine similarity
        if self.config.metric == "cosine":
            vectors = self._normalize_vectors(self.vectors)
        else:
            vectors = self.vectors
        
        if self.config.algorithm == ANNAlgorithm.HNSW:
            return self._build_hnsw_index(vectors)
        elif self.config.algorithm == ANNAlgorithm.IVF:
            return self._build_ivf_index(vectors)
        elif self.config.algorithm == ANNAlgorithm.PQ:
            return self._build_pq_index(vectors)
        elif self.config.algorithm == ANNAlgorithm.OPQ:
            return self._build_opq_index(vectors)
        elif self.config.algorithm == ANNAlgorithm.EXACT:
            return self._build_exact_index(vectors)
        else:
            raise ValueError(f"Unknown algorithm: {self.config.algorithm}")
    
    def _build_hnsw_index(self, vectors: np.ndarray) -> faiss.Index:
        """
        Build HNSW (Hierarchical Navigable Small World) index.
        
        HNSW is a graph-based algorithm that provides excellent search performance
        for high-dimensional data. It's the recommended choice for most use cases.
        """
        # Create HNSW index
        if self.config.metric == "cosine":
            index = faiss.IndexHNSWFlat(self.dimension, self.config.m)
        else:
            index = faiss.IndexHNSWFlat(self.dimension, self.config.m)
        
        # Set HNSW parameters
        index.hnsw.efConstruction = self.config.ef_construction
        index.hnsw.efSearch = self.config.ef_search
        
        # Add vectors
        index.add(vectors)
        
        return index
    
    def _build_ivf_index(self, vectors: np.ndarray) -> faiss.Index:
        """
        Build IVF (Inverted File) index.
        
        IVF partitions the vector space into clusters and only searches
        the most relevant clusters. Good for large datasets.
        """
        # Create quantizer
        if self.config.metric == "cosine":
            quantizer = faiss.IndexFlatIP(self.dimension)
        else:
            quantizer = faiss.IndexFlatL2(self.dimension)
        
        # Create IVF index
        index = faiss.IndexIVFFlat(
            quantizer,
            self.dimension,
            self.config.nlist
        )
        
        # Train index
        print("Training IVF index...")
        index.train(vectors)
        
        # Add vectors
        index.add(vectors)
        
        # Set search parameters
        index.nprobe = self.config.nprobe
        
        return index
    
    def _build_pq_index(self, vectors: np.ndarray) -> faiss.Index:
        """
        Build PQ (Product Quantization) index.
        
        PQ compresses vectors by quantizing subvectors. It's very memory-efficient
        but may have lower accuracy than HNSW or IVF.
        """
        # Determine number of subquantizers
        m = self.dimension // 8  # 8 dimensions per subquantizer
        if m < 1:
            m = 1
        
        nbits = self.config.nbits
        
        # Create PQ index
        index = faiss.IndexPQ(self.dimension, m, nbits)
        
        # Train index
        print("Training PQ index...")
        index.train(vectors)
        
        # Add vectors
        index.add(vectors)
        
        return index
    
    def _build_opq_index(self, vectors: np.ndarray) -> faiss.Index:
        """
        Build OPQ (Optimized Product Quantization) index.
        
        OPQ improves upon PQ by applying a rotation matrix to the vectors
        before quantization, which can improve accuracy.
        """
        # Determine number of subquantizers
        m = self.dimension // 8
        if m < 1:
            m = 1
        
        nbits = self.config.nbits
        
        # Create OPQ matrix and PQ index
        opq = faiss.OPQMatrix(self.dimension, m)
        pq = faiss.IndexPQ(self.dimension, m, nbits)
        
        # Create pre-transform index
        index = faiss.IndexPreTransform(opq, pq)
        
        # Train index
        print("Training OPQ index...")
        index.train(vectors)
        
        # Add vectors
        index.add(vectors)
        
        return index
    
    def _build_exact_index(self, vectors: np.ndarray) -> faiss.Index:
        """Build exact search index (brute force)."""
        if self.config.metric == "cosine":
            index = faiss.IndexFlatIP(self.dimension)
        else:
            index = faiss.IndexFlatL2(self.dimension)
        
        index.add(vectors)
        return index
    
    def _build_fallback_index(self):
        """Build sklearn-based fallback index."""
        from sklearn.neighbors import NearestNeighbors
        
        metric = "cosine" if self.config.metric == "cosine" else "euclidean"
        index = NearestNeighbors(
            n_neighbors=10,
            metric=metric,
            algorithm='auto'
        )
        index.fit(self.vectors)
        
        return index
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors for cosine similarity."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        return vectors / norms
    
    def search(
        self,
        query: np.ndarray,
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for k nearest neighbors.
        
        Args:
            query: Query vector or array of vectors
            k: Number of nearest neighbors to return
            
        Returns:
            Tuple of (distances, indices)
            - distances: Array of distances/similarities
            - indices: Array of indices of nearest neighbors
        """
        if not self._is_trained:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Ensure query is 2D
        if query.ndim == 1:
            query = query.reshape(1, -1)
        
        query = query.astype(np.float32)
        
        # Normalize for cosine similarity
        if self.config.metric == "cosine":
            query = self._normalize_vectors(query)
        
        if FAISS_AVAILABLE:
            distances, indices = self.index.search(query, k)
        else:
            # Fallback to sklearn
            distances, indices = self.index.kneighbors(query, n_neighbors=k)
        
        return distances[0] if len(distances) == 1 else distances, \
               indices[0] if len(indices) == 1 else indices
    
    def batch_search(
        self,
        queries: np.ndarray,
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Batch search for multiple queries.
        
        Args:
            queries: Array of query vectors (n_queries x dimension)
            k: Number of nearest neighbors per query
            
        Returns:
            Tuple of (distances, indices)
            - distances: Array of shape (n_queries, k)
            - indices: Array of shape (n_queries, k)
        """
        return self.search(queries, k=k)
    
    def search_by_id(
        self,
        id: str,
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for neighbors of a vector by ID.
        
        Args:
            id: ID of the query vector
            k: Number of neighbors to return
            
        Returns:
            Tuple of (distances, indices)
        """
        if id not in self.ids:
            raise ValueError(f"ID {id} not found in index")
        
        idx = self.ids.index(id)
        query = self.vectors[idx]
        
        return self.search(query, k=k)
    
    def add_vectors(
        self,
        vectors: np.ndarray,
        ids: Optional[List[str]] = None
    ):
        """
        Add new vectors to the index.
        
        Note: Not all index types support incremental additions.
        
        Args:
            vectors: New vectors to add
            ids: IDs for new vectors
        """
        if not FAISS_AVAILABLE:
            raise NotImplementedError("Fallback index doesn't support incremental additions")
        
        vectors = vectors.astype(np.float32)
        
        if self.config.metric == "cosine":
            vectors = self._normalize_vectors(vectors)
        
        self.index.add(vectors)
        
        # Update tracking
        new_ids = ids or [str(len(self.ids) + i) for i in range(len(vectors))]
        self.ids.extend(new_ids)
        self.vectors = np.vstack([self.vectors, vectors])
    
    def remove_vectors(self, ids: List[str]):
        """
        Remove vectors from the index.
        
        Note: FAISS doesn't support direct removal. This requires rebuilding.
        
        Args:
            ids: IDs of vectors to remove
        """
        # FAISS doesn't support direct removal
        # We need to rebuild the index without the removed vectors
        indices_to_keep = [i for i, id in enumerate(self.ids) if id not in ids]
        
        self.vectors = self.vectors[indices_to_keep]
        self.ids = [self.ids[i] for i in indices_to_keep]
        
        # Rebuild index
        self.build_index(self.vectors, self.ids)
    
    def save(self, path: str):
        """
        Save index to disk.
        
        Args:
            path: File path to save index
        """
        if not FAISS_AVAILABLE:
            raise NotImplementedError("Cannot save fallback index")
        
        faiss.write_index(self.index, path)
        
        # Save IDs separately
        import json
        with open(path + '.ids', 'w') as f:
            json.dump(self.ids, f)
    
    def load(self, path: str) -> 'FAISSANNIndex':
        """
        Load index from disk.
        
        Args:
            path: File path to load index from
            
        Returns:
            Self for method chaining
        """
        if not FAISS_AVAILABLE:
            raise NotImplementedError("Cannot load fallback index")
        
        self.index = faiss.read_index(path)
        
        # Load IDs
        import json
        with open(path + '.ids', 'r') as f:
            self.ids = json.load(f)
        
        self._is_trained = True
        return self
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        stats = {
            'algorithm': self.config.algorithm.value,
            'metric': self.config.metric,
            'dimension': self.dimension,
            'n_vectors': len(self.ids) if self.ids else 0,
            'is_trained': self._is_trained
        }
        
        if FAISS_AVAILABLE and self.index is not None:
            # Add FAISS-specific stats
            if hasattr(self.index, 'ntotal'):
                stats['faiss_ntotal'] = self.index.ntotal
        
        return stats


class ANNIndexBuilder:
    """
    Builder class for creating ANN indices with different configurations.
    
    Example:
        >>> builder = ANNIndexBuilder(dimension=768)
        >>> index = (builder
        ...     .with_algorithm(ANNAlgorithm.HNSW)
        ...     .with_m(32)
        ...     .with_ef_construction(400)
        ...     .build(vectors))
    """
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.config = ANNConfig()
    
    def with_algorithm(self, algorithm: ANNAlgorithm) -> 'ANNIndexBuilder':
        """Set ANN algorithm."""
        self.config.algorithm = algorithm
        return self
    
    def with_m(self, m: int) -> 'ANNIndexBuilder':
        """Set HNSW M parameter."""
        self.config.m = m
        return self
    
    def with_ef_construction(self, ef: int) -> 'ANNIndexBuilder':
        """Set HNSW efConstruction parameter."""
        self.config.ef_construction = ef
        return self
    
    def with_ef_search(self, ef: int) -> 'ANNIndexBuilder':
        """Set HNSW efSearch parameter."""
        self.config.ef_search = ef
        return self
    
    def with_nlist(self, nlist: int) -> 'ANNIndexBuilder':
        """Set IVF nlist parameter."""
        self.config.nlist = nlist
        return self
    
    def with_nprobe(self, nprobe: int) -> 'ANNIndexBuilder':
        """Set IVF nprobe parameter."""
        self.config.nprobe = nprobe
        return self
    
    def with_metric(self, metric: str) -> 'ANNIndexBuilder':
        """Set distance metric."""
        self.config.metric = metric
        return self
    
    def build(
        self,
        vectors: np.ndarray,
        ids: Optional[List[str]] = None
    ) -> FAISSANNIndex:
        """Build the ANN index."""
        index = FAISSANNIndex(self.dimension, self.config)
        return index.build_index(vectors, ids)


# Convenience functions
def create_hnsw_index(
    vectors: np.ndarray,
    dimension: int,
    m: int = 16,
    ef_construction: int = 200,
    metric: str = "cosine",
    ids: Optional[List[str]] = None
) -> FAISSANNIndex:
    """
    Create HNSW index with specified parameters.
    
    Args:
        vectors: Vectors to index
        dimension: Vector dimension
        m: HNSW M parameter
        ef_construction: HNSW efConstruction parameter
        metric: Distance metric
        ids: Optional vector IDs
        
    Returns:
        Configured FAISSANNIndex
    """
    config = ANNConfig(
        algorithm=ANNAlgorithm.HNSW,
        m=m,
        ef_construction=ef_construction,
        metric=metric
    )
    
    index = FAISSANNIndex(dimension, config)
    return index.build_index(vectors, ids)


def create_ivf_index(
    vectors: np.ndarray,
    dimension: int,
    nlist: int = 100,
    nprobe: int = 10,
    metric: str = "cosine",
    ids: Optional[List[str]] = None
) -> FAISSANNIndex:
    """
    Create IVF index with specified parameters.
    
    Args:
        vectors: Vectors to index
        dimension: Vector dimension
        nlist: Number of clusters
        nprobe: Clusters to search
        metric: Distance metric
        ids: Optional vector IDs
        
    Returns:
        Configured FAISSANNIndex
    """
    config = ANNConfig(
        algorithm=ANNAlgorithm.IVF,
        nlist=nlist,
        nprobe=nprobe,
        metric=metric
    )
    
    index = FAISSANNIndex(dimension, config)
    return index.build_index(vectors, ids)


if __name__ == "__main__":
    # Example usage
    print("FAISSANNIndex - Example Usage")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    n_vectors = 1000
    dimension = 128
    
    vectors = np.random.randn(n_vectors, dimension).astype(np.float32)
    ids = [f"county_{i:04d}" for i in range(n_vectors)]
    
    print(f"\nSample data: {n_vectors} vectors of dimension {dimension}")
    
    # Build HNSW index
    print("\n--- HNSW Index ---")
    config = ANNConfig(algorithm=ANNAlgorithm.HNSW, m=16)
    index = FAISSANNIndex(dimension, config)
    index.build_index(vectors, ids)
    
    # Search
    query = vectors[0]
    distances, indices = index.search(query, k=5)
    
    print(f"Query ID: {ids[0]}")
    print(f"Top 5 neighbors:")
    for i, (dist, idx) in enumerate(zip(distances, indices)):
        print(f"  {i+1}. {ids[idx]} (distance: {dist:.4f})")
    
    # Get stats
    stats = index.get_stats()
    print(f"\nIndex stats: {stats}")
    
    print("\nFAISSANNIndex ready for use!")
