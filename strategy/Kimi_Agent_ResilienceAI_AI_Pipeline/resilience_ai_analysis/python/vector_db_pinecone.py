"""
ResilienceAI Pinecone Vector Database Integration
Manages county embeddings for similarity search and clustering.
"""

import os
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
INDEX_NAME = os.getenv("PINECONE_INDEX", "resilienceai-counties")
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "384"))  # Default: all-MiniLM-L6-v2

# Domain-specific namespace configuration
NAMESPACES = {
    "climate": "Climate vulnerability embeddings",
    "health": "Health infrastructure embeddings",
    "infrastructure": "Infrastructure resilience embeddings",
    "socioeconomic": "Socioeconomic vulnerability embeddings",
    "agriculture": "Agricultural vulnerability embeddings",
    "comprehensive": "All-domain combined embeddings",
}


@dataclass
class CountyVector:
    """Represents a county's vector embedding with metadata"""
    id: str                          # county_fips (5-digit)
    values: List[float]              # Embedding vector
    metadata: Dict[str, Any]         # Associated metadata
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "values": self.values,
            "metadata": self.metadata
        }


@dataclass
class SimilarityResult:
    """Result from similarity search"""
    id: str                          # County FIPS
    score: float                     # Similarity score
    metadata: Dict[str, Any]         # County metadata
    
    def to_dict(self) -> Dict:
        return {
            "fips_code": self.id,
            "similarity_score": self.score,
            **self.metadata
        }


class PineconeVectorStore:
    """
    Vector database operations for county embeddings using Pinecone.
    Supports multi-namespace organization by domain.
    """
    
    def __init__(self, index_name: str = INDEX_NAME, dimension: int = VECTOR_DIMENSION):
        """
        Initialize Pinecone vector store.
        
        Args:
            index_name: Name of the Pinecone index
            dimension: Vector dimension size
        """
        self.index_name = index_name
        self.dimension = dimension
        self._pc = None
        self._index = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Pinecone connection"""
        try:
            from pinecone import Pinecone, ServerlessSpec
            
            if not PINECONE_API_KEY:
                raise ValueError("PINECONE_API_KEY environment variable not set")
            
            self._pc = Pinecone(api_key=PINECONE_API_KEY)
            self._index = self._get_or_create_index()
            logger.info(f"Pinecone initialized: index={self.index_name}, dim={self.dimension}")
            
        except ImportError:
            logger.error("pinecone-client not installed. Run: pip install pinecone-client")
            raise
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {e}")
            raise
    
    def _get_or_create_index(self):
        """Get existing index or create new one"""
        from pinecone import ServerlessSpec
        
        if self.index_name not in self._pc.list_indexes().names():
            logger.info(f"Creating new Pinecone index: {self.index_name}")
            self._pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=PINECONE_ENVIRONMENT
                )
            )
        
        return self._pc.Index(self.index_name)
    
    # ============================================
    # UPSERT OPERATIONS
    # ============================================
    
    def upsert_county(self, county: CountyVector, namespace: str = ""):
        """
        Upsert a single county vector.
        
        Args:
            county: CountyVector to upsert
            namespace: Optional namespace for domain separation
        """
        self.upsert_counties([county], namespace)
    
    def upsert_counties(self, counties: List[CountyVector], namespace: str = ""):
        """
        Upsert multiple county vectors in batches.
        
        Args:
            counties: List of CountyVector objects
            namespace: Optional namespace for domain separation
        """
        if not counties:
            return
        
        # Prepare vectors for upsert
        vectors = [
            {
                "id": c.id,
                "values": c.values,
                "metadata": c.metadata
            }
            for c in counties
        ]
        
        # Upsert in batches of 100 (Pinecone limit)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                self._index.upsert(vectors=batch, namespace=namespace)
                logger.debug(f"Upserted {len(batch)} vectors to namespace '{namespace}'")
            except Exception as e:
                logger.error(f"Upsert failed for batch {i//batch_size}: {e}")
                raise
        
        logger.info(f"Upserted {len(counties)} vectors to namespace '{namespace}'")
    
    def upsert_from_dataframe(
        self, 
        df, 
        fips_column: str = "fips",
        vector_columns: List[str] = None,
        metadata_columns: List[str] = None,
        namespace: str = ""
    ):
        """
        Upsert counties from a pandas DataFrame.
        
        Args:
            df: Pandas DataFrame
            fips_column: Column name for FIPS code
            vector_columns: Columns to use for vector (None = all numeric)
            metadata_columns: Columns to include as metadata
            namespace: Optional namespace
        """
        import pandas as pd
        
        if vector_columns is None:
            # Use all numeric columns except fips
            vector_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            if fips_column in vector_columns:
                vector_columns.remove(fips_column)
        
        if metadata_columns is None:
            metadata_columns = ['county_name', 'state', 'population']
        
        counties = []
        for _, row in df.iterrows():
            # Extract vector values
            vector_values = []
            for col in vector_columns:
                val = row.get(col, 0)
                if pd.isna(val):
                    val = 0
                vector_values.append(float(val))
            
            # Pad or truncate to match dimension
            if len(vector_values) < self.dimension:
                vector_values.extend([0.0] * (self.dimension - len(vector_values)))
            vector_values = vector_values[:self.dimension]
            
            # Build metadata
            metadata = {}
            for col in metadata_columns:
                if col in row:
                    val = row[col]
                    if pd.isna(val):
                        val = None
                    metadata[col] = val
            
            counties.append(CountyVector(
                id=str(row[fips_column]).zfill(5),
                values=vector_values,
                metadata=metadata
            ))
        
        self.upsert_counties(counties, namespace)
    
    # ============================================
    # SEARCH OPERATIONS
    # ============================================
    
    def search_similar(
        self, 
        query_vector: List[float], 
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: str = ""
    ) -> List[SimilarityResult]:
        """
        Search for similar counties by vector.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Metadata filter (e.g., {"state": "MO"})
            namespace: Namespace to search
            
        Returns:
            List of SimilarityResult objects
        """
        try:
            results = self._index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict,
                namespace=namespace
            )
            
            return [
                SimilarityResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata or {}
                )
                for match in results.matches
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_by_county_fips(
        self, 
        county_fips: str, 
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: str = ""
    ) -> List[SimilarityResult]:
        """
        Find counties similar to a given county.
        
        Args:
            county_fips: Reference county FIPS code
            top_k: Number of results to return
            filter_dict: Metadata filter
            namespace: Namespace to search
            
        Returns:
            List of SimilarityResult objects (excluding the reference county)
        """
        # Fetch the vector for the reference county
        result = self._index.fetch(ids=[county_fips], namespace=namespace)
        
        if county_fips not in result.vectors:
            logger.warning(f"County {county_fips} not found in namespace '{namespace}'")
            return []
        
        vector = result.vectors[county_fips].values
        results = self.search_similar(vector, top_k=top_k + 1, filter_dict=filter_dict, namespace=namespace)
        
        # Remove the reference county from results
        return [r for r in results if r.id != county_fips][:top_k]
    
    def search_by_text(
        self,
        text: str,
        text_encoder: Callable[[str], List[float]],
        top_k: int = 10,
        filter_dict: Optional[Dict] = None,
        namespace: str = ""
    ) -> List[SimilarityResult]:
        """
        Search using text query (requires text encoder).
        
        Args:
            text: Text query
            text_encoder: Function that converts text to embedding vector
            top_k: Number of results
            filter_dict: Metadata filter
            namespace: Namespace to search
            
        Returns:
            List of SimilarityResult objects
        """
        vector = text_encoder(text)
        return self.search_similar(vector, top_k, filter_dict, namespace)
    
    def find_anomalies(
        self,
        county_fips: str,
        threshold: float = 0.3,
        namespace: str = ""
    ) -> List[SimilarityResult]:
        """
        Find counties that are anomalies (dissimilar) to a reference county.
        
        Args:
            county_fips: Reference county FIPS
            threshold: Similarity threshold (lower = more dissimilar)
            namespace: Namespace to search
            
        Returns:
            List of most dissimilar counties
        """
        # Get all counties (or a large sample)
        all_results = self.search_by_county_fips(county_fips, top_k=1000, namespace=namespace)
        
        # Filter for low similarity scores
        anomalies = [r for r in all_results if r.score < threshold]
        
        # Sort by similarity (ascending - most dissimilar first)
        return sorted(anomalies, key=lambda x: x.score)
    
    # ============================================
    # FETCH OPERATIONS
    # ============================================
    
    def get_county_vector(
        self, 
        county_fips: str, 
        namespace: str = ""
    ) -> Optional[CountyVector]:
        """
        Get a county's vector by FIPS code.
        
        Args:
            county_fips: County FIPS code
            namespace: Namespace
            
        Returns:
            CountyVector or None if not found
        """
        result = self._index.fetch(ids=[county_fips], namespace=namespace)
        
        if county_fips not in result.vectors:
            return None
        
        vector_data = result.vectors[county_fips]
        return CountyVector(
            id=county_fips,
            values=vector_data.values,
            metadata=vector_data.metadata or {}
        )
    
    def get_multiple_counties(
        self, 
        county_fips_list: List[str], 
        namespace: str = ""
    ) -> List[CountyVector]:
        """
        Get multiple county vectors.
        
        Args:
            county_fips_list: List of FIPS codes
            namespace: Namespace
            
        Returns:
            List of CountyVector objects
        """
        result = self._index.fetch(ids=county_fips_list, namespace=namespace)
        
        counties = []
        for fips, vector_data in result.vectors.items():
            counties.append(CountyVector(
                id=fips,
                values=vector_data.values,
                metadata=vector_data.metadata or {}
            ))
        
        return counties
    
    # ============================================
    # DELETE OPERATIONS
    # ============================================
    
    def delete_county(self, county_fips: str, namespace: str = ""):
        """Delete a county's vector"""
        self._index.delete(ids=[county_fips], namespace=namespace)
        logger.info(f"Deleted county {county_fips} from namespace '{namespace}'")
    
    def delete_counties(self, county_fips_list: List[str], namespace: str = ""):
        """Delete multiple counties"""
        self._index.delete(ids=county_fips_list, namespace=namespace)
        logger.info(f"Deleted {len(county_fips_list)} counties from namespace '{namespace}'")
    
    def delete_all_in_namespace(self, namespace: str = ""):
        """Delete all vectors in a namespace"""
        self._index.delete(delete_all=True, namespace=namespace)
        logger.warning(f"Deleted all vectors in namespace '{namespace}'")
    
    # ============================================
    # STATISTICS AND INFO
    # ============================================
    
    def get_namespace_stats(self, namespace: str = "") -> Dict:
        """Get statistics for a namespace"""
        stats = self._index.describe_index_stats()
        
        # Get namespace-specific stats if available
        ns_stats = stats.namespaces.get(namespace, {})
        
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "namespace_vectors": ns_stats.get('vector_count', 0) if ns_stats else 0
        }
    
    def get_all_namespaces(self) -> List[str]:
        """Get list of all namespaces"""
        stats = self._index.describe_index_stats()
        return list(stats.namespaces.keys())
    
    def get_index_stats(self) -> Dict:
        """Get overall index statistics"""
        return self._index.describe_index_stats().to_dict()
    
    # ============================================
    # DOMAIN-SPECIFIC OPERATIONS
    # ============================================
    
    def upsert_domain_vectors(
        self, 
        domain: str, 
        counties: List[CountyVector]
    ):
        """
        Upsert vectors to a domain-specific namespace.
        
        Args:
            domain: Domain name (climate, health, infrastructure, etc.)
            counties: List of CountyVector objects
        """
        if domain not in NAMESPACES:
            raise ValueError(f"Unknown domain: {domain}. Valid: {list(NAMESPACES.keys())}")
        
        self.upsert_counties(counties, namespace=domain)
    
    def search_domain(
        self, 
        domain: str,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[SimilarityResult]:
        """
        Search within a specific domain namespace.
        
        Args:
            domain: Domain name
            query_vector: Query embedding
            top_k: Number of results
            filter_dict: Metadata filter
            
        Returns:
            List of SimilarityResult objects
        """
        return self.search_similar(
            query_vector, 
            top_k=top_k, 
            filter_dict=filter_dict, 
            namespace=domain
        )
    
    def cross_domain_search(
        self,
        query_vector: List[float],
        domains: List[str],
        top_k_per_domain: int = 5
    ) -> Dict[str, List[SimilarityResult]]:
        """
        Search across multiple domains.
        
        Args:
            query_vector: Query embedding
            domains: List of domain names to search
            top_k_per_domain: Results per domain
            
        Returns:
            Dict mapping domain to results
        """
        results = {}
        for domain in domains:
            results[domain] = self.search_domain(
                domain, 
                query_vector, 
                top_k=top_k_per_domain
            )
        return results


# ============================================
# HELPER FUNCTIONS
# ============================================

def create_vector_from_features(
    features: Dict[str, float],
    feature_order: List[str],
    dimension: int = VECTOR_DIMENSION
) -> List[float]:
    """
    Create a vector from feature dictionary.
    
    Args:
        features: Dictionary of feature_key -> value
        feature_order: Order of features for vector
        dimension: Target vector dimension
        
    Returns:
        Vector as list of floats
    """
    vector = []
    for key in feature_order:
        val = features.get(key, 0.0)
        if np.isnan(val):
            val = 0.0
        vector.append(float(val))
    
    # Pad or truncate
    if len(vector) < dimension:
        vector.extend([0.0] * (dimension - len(vector)))
    return vector[:dimension]


def normalize_vector(vector: List[float]) -> List[float]:
    """L2 normalize a vector"""
    arr = np.array(vector)
    norm = np.linalg.norm(arr)
    if norm == 0:
        return vector
    return (arr / norm).tolist()


# Global vector store instance
_vector_store = None

def get_vector_store() -> PineconeVectorStore:
    """Get or create global vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = PineconeVectorStore()
    return _vector_store


if __name__ == "__main__":
    # Test vector store
    print("Testing Pinecone vector store...")
    
    store = PineconeVectorStore()
    
    # Test upsert
    test_counties = [
        CountyVector(
            id="29095",
            values=[0.1] * 384,
            metadata={"county_name": "Jackson County", "state": "MO"}
        ),
        CountyVector(
            id="29189",
            values=[0.2] * 384,
            metadata={"county_name": "St. Louis County", "state": "MO"}
        )
    ]
    
    store.upsert_counties(test_counties, namespace="test")
    
    # Test search
    results = store.search_similar([0.15] * 384, top_k=5, namespace="test")
    print(f"Search results: {results}")
    
    # Test stats
    stats = store.get_namespace_stats("test")
    print(f"Namespace stats: {stats}")
    
    # Cleanup
    store.delete_all_in_namespace("test")
    print("Test completed")
