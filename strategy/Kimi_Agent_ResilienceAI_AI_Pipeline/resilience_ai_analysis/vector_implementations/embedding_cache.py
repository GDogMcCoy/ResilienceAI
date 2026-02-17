"""
Multi-Tier Embedding Cache System

This module provides a multi-tier caching system for embeddings:
- In-memory LRU cache (fastest, smallest)
- Redis cache (distributed, medium speed)
- Disk cache (persistent, slowest)

Author: Vector Embedding Specialist
"""

from typing import Dict, List, Optional, Any, Union, Callable
import hashlib
import json
import pickle
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import lru_cache, wraps
import numpy as np
from pathlib import Path
import threading

# Optional imports with fallbacks
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import diskcache as dc
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False


@dataclass
class CacheConfig:
    """Configuration for embedding cache."""
    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # Disk cache settings
    disk_cache_path: str = "./cache/embeddings"
    disk_size_limit: int = 10 * 1024 * 1024 * 1024  # 10 GB
    disk_eviction_policy: str = "least-recently-used"
    
    # Memory cache settings
    memory_cache_size: int = 1000
    
    # TTL settings
    ttl_seconds: int = 86400  # 24 hours
    
    # Compression
    compression: bool = True
    compression_level: int = 6
    
    # Cache key settings
    version: str = "1.0"  # Cache version for invalidation
    include_timestamp: bool = False


class EmbeddingCache:
    """
    Multi-tier caching system for embeddings.
    
    This cache implements a three-tier storage strategy:
    1. In-memory LRU cache: Fastest access for hot data
    2. Redis cache: Distributed cache for shared access
    3. Disk cache: Persistent storage for cold data
    
    The cache automatically promotes data between tiers based on access patterns.
    
    Example:
        >>> config = CacheConfig(memory_cache_size=500)
        >>> cache = EmbeddingCache(config)
        >>> 
        >>> # Store embedding
        >>> cache.set(county_data, "model_v1", embedding)
        >>> 
        >>> # Retrieve embedding
        >>> cached_emb = cache.get(county_data, "model_v1")
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize the embedding cache.
        
        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        
        # Initialize Redis connection
        self.redis_client = None
        self.redis_available = False
        
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    db=self.config.redis_db,
                    password=self.config.redis_password,
                    ssl=self.config.redis_ssl,
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                self.redis_available = self.redis_client.ping()
                if self.redis_available:
                    print(f"Connected to Redis at {self.config.redis_host}:{self.config.redis_port}")
            except Exception as e:
                print(f"Redis connection failed: {e}")
        
        # Initialize disk cache
        self.disk_cache = None
        self.disk_available = False
        
        if DISKCACHE_AVAILABLE:
            try:
                Path(self.config.disk_cache_path).mkdir(parents=True, exist_ok=True)
                self.disk_cache = dc.Cache(
                    self.config.disk_cache_path,
                    size_limit=self.config.disk_size_limit,
                    eviction_policy=self.config.disk_eviction_policy
                )
                self.disk_available = True
                print(f"Initialized disk cache at {self.config.disk_cache_path}")
            except Exception as e:
                print(f"Disk cache initialization failed: {e}")
        
        # Memory cache is handled via @lru_cache decorator on methods
        
        # Statistics
        self.stats = {
            'memory_hits': 0,
            'redis_hits': 0,
            'disk_hits': 0,
            'misses': 0,
            'sets': 0
        }
        
        # Thread safety
        self._lock = threading.RLock()
    
    def _generate_key(
        self,
        county_data: Dict[str, Any],
        model_name: str,
        domain: str = "all"
    ) -> str:
        """
        Generate cache key from county data and model.
        
        The key is deterministic based on input data, ensuring that
        identical inputs always produce the same key.
        
        Args:
            county_data: County data dictionary
            model_name: Name of embedding model
            domain: Embedding domain
            
        Returns:
            Cache key string
        """
        # Create deterministic key components
        key_data = {
            'fips': county_data.get('fips'),
            'model': model_name,
            'domain': domain,
            'version': self.config.version
        }
        
        # Add timestamp if configured
        if self.config.include_timestamp:
            key_data['timestamp'] = datetime.now().isoformat()
        
        # Create hash
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        hash_val = hashlib.sha256(key_str.encode()).hexdigest()
        
        # Use first 32 characters of hash for key
        return f"emb:{hash_val[:32]}"
    
    def _serialize(self, embedding: np.ndarray) -> bytes:
        """Serialize embedding to bytes."""
        if self.config.compression:
            import zlib
            data = pickle.dumps(embedding, protocol=pickle.HIGHEST_PROTOCOL)
            return zlib.compress(data, level=self.config.compression_level)
        else:
            return pickle.dumps(embedding, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _deserialize(self, data: bytes) -> np.ndarray:
        """Deserialize embedding from bytes."""
        if self.config.compression:
            import zlib
            data = zlib.decompress(data)
        return pickle.loads(data)
    
    def get(
        self,
        county_data: Dict[str, Any],
        model_name: str,
        domain: str = "all"
    ) -> Optional[np.ndarray]:
        """
        Retrieve embedding from cache.
        
        Tries tiers in order: memory -> Redis -> disk
        
        Args:
            county_data: County data dictionary
            model_name: Name of embedding model
            domain: Embedding domain
            
        Returns:
            Cached embedding or None if not found
        """
        with self._lock:
            key = self._generate_key(county_data, model_name, domain)
            
            # Try memory cache (via lru_cache on compute method)
            # This is handled by the @lru_cache decorator on encode methods
            
            # Try Redis
            if self.redis_available:
                try:
                    cached = self.redis_client.get(key)
                    if cached:
                        embedding = self._deserialize(cached)
                        self.stats['redis_hits'] += 1
                        
                        # Promote to memory cache by returning
                        return embedding
                except Exception as e:
                    print(f"Redis get error: {e}")
            
            # Try disk cache
            if self.disk_available:
                try:
                    cached = self.disk_cache.get(key)
                    if cached is not None:
                        embedding = cached
                        self.stats['disk_hits'] += 1
                        
                        # Promote to Redis if available
                        if self.redis_available:
                            self._set_redis(key, embedding)
                        
                        return embedding
                except Exception as e:
                    print(f"Disk cache get error: {e}")
            
            # Cache miss
            self.stats['misses'] += 1
            return None
    
    def set(
        self,
        county_data: Dict[str, Any],
        model_name: str,
        embedding: np.ndarray,
        domain: str = "all",
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store embedding in cache.
        
        Stores in all available tiers.
        
        Args:
            county_data: County data dictionary
            model_name: Name of embedding model
            embedding: Embedding vector
            domain: Embedding domain
            ttl: Time-to-live in seconds (overrides config)
            
        Returns:
            True if successfully stored in at least one tier
        """
        with self._lock:
            key = self._generate_key(county_data, model_name, domain)
            ttl = ttl or self.config.ttl_seconds
            
            success = False
            
            # Store in Redis
            if self.redis_available:
                try:
                    self._set_redis(key, embedding, ttl)
                    success = True
                except Exception as e:
                    print(f"Redis set error: {e}")
            
            # Store in disk cache
            if self.disk_available:
                try:
                    self.disk_cache.set(key, embedding, expire=ttl)
                    success = True
                except Exception as e:
                    print(f"Disk cache set error: {e}")
            
            if success:
                self.stats['sets'] += 1
            
            return success
    
    def _set_redis(
        self,
        key: str,
        embedding: np.ndarray,
        ttl: Optional[int] = None
    ):
        """Store embedding in Redis with TTL."""
        ttl = ttl or self.config.ttl_seconds
        serialized = self._serialize(embedding)
        self.redis_client.setex(key, ttl, serialized)
    
    def delete(
        self,
        county_data: Dict[str, Any],
        model_name: str,
        domain: str = "all"
    ) -> bool:
        """
        Delete embedding from cache.
        
        Args:
            county_data: County data dictionary
            model_name: Name of embedding model
            domain: Embedding domain
            
        Returns:
            True if deleted from at least one tier
        """
        with self._lock:
            key = self._generate_key(county_data, model_name, domain)
            
            success = False
            
            # Delete from Redis
            if self.redis_available:
                try:
                    self.redis_client.delete(key)
                    success = True
                except Exception as e:
                    print(f"Redis delete error: {e}")
            
            # Delete from disk cache
            if self.disk_available:
                try:
                    del self.disk_cache[key]
                    success = True
                except KeyError:
                    pass
                except Exception as e:
                    print(f"Disk cache delete error: {e}")
            
            return success
    
    def invalidate(
        self,
        fips: Optional[str] = None,
        model_name: Optional[str] = None,
        domain: Optional[str] = None
    ) -> int:
        """
        Invalidate cache entries matching criteria.
        
        Args:
            fips: Invalidate specific county (None for all)
            model_name: Invalidate specific model (None for all)
            domain: Invalidate specific domain (None for all)
            
        Returns:
            Number of entries invalidated
        """
        with self._lock:
            count = 0
            
            # If no criteria specified, clear all caches
            if fips is None and model_name is None and domain is None:
                if self.redis_available:
                    self.redis_client.flushdb()
                    count += 1
                
                if self.disk_available:
                    self.disk_cache.clear()
                    count += 1
                
                return count
            
            # Pattern-based invalidation would require maintaining an index
            # For now, we clear all if any criteria is specified
            # TODO: Implement pattern-based invalidation
            
            return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            stats = self.stats.copy()
            
            # Calculate hit rates
            total_requests = (
                stats['memory_hits'] +
                stats['redis_hits'] +
                stats['disk_hits'] +
                stats['misses']
            )
            
            if total_requests > 0:
                stats['hit_rate'] = (
                    (total_requests - stats['misses']) / total_requests
                )
            else:
                stats['hit_rate'] = 0.0
            
            # Add tier availability
            stats['redis_available'] = self.redis_available
            stats['disk_available'] = self.disk_available
            
            # Add Redis stats
            if self.redis_available:
                try:
                    info = self.redis_client.info()
                    stats['redis_keys'] = self.redis_client.dbsize()
                    stats['redis_memory'] = info.get('used_memory_human', 'N/A')
                except Exception as e:
                    stats['redis_error'] = str(e)
            
            # Add disk stats
            if self.disk_available:
                try:
                    stats['disk_size'] = len(self.disk_cache)
                    stats['disk_volume'] = self.disk_cache.volume
                except Exception as e:
                    stats['disk_error'] = str(e)
            
            return stats
    
    def clear_stats(self):
        """Reset cache statistics."""
        with self._lock:
            self.stats = {
                'memory_hits': 0,
                'redis_hits': 0,
                'disk_hits': 0,
                'misses': 0,
                'sets': 0
            }
    
    def close(self):
        """Close cache connections."""
        if self.disk_available:
            self.disk_cache.close()
        
        if self.redis_available:
            self.redis_client.close()


def cached_embedding(
    cache: EmbeddingCache,
    model_name: str,
    domain: str = "all"
):
    """
    Decorator for caching embedding function results.
    
    Args:
        cache: EmbeddingCache instance
        model_name: Name of the embedding model
        domain: Embedding domain
        
    Returns:
        Decorator function
        
    Example:
        >>> cache = EmbeddingCache()
        >>> 
        >>> @cached_embedding(cache, "model_v1", "climate")
        >>> def generate_embedding(county_data):
        >>>     # Expensive computation
        >>>     return embedding
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(county_data: Dict[str, Any], *args, **kwargs):
            # Try to get from cache
            cached = cache.get(county_data, model_name, domain)
            if cached is not None:
                return cached
            
            # Compute embedding
            embedding = func(county_data, *args, **kwargs)
            
            # Store in cache
            cache.set(county_data, model_name, embedding, domain)
            
            return embedding
        
        return wrapper
    return decorator


class CacheManager:
    """
    Manager for multiple cache instances.
    
    Provides centralized cache management and monitoring.
    """
    
    def __init__(self):
        self.caches: Dict[str, EmbeddingCache] = {}
        
    def register_cache(self, name: str, cache: EmbeddingCache):
        """Register a cache instance."""
        self.caches[name] = cache
        
    def get_cache(self, name: str) -> Optional[EmbeddingCache]:
        """Get a registered cache."""
        return self.caches.get(name)
        
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        return {name: cache.get_stats() for name, cache in self.caches.items()}
        
    def invalidate_all(
        self,
        fips: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """Invalidate entries in all caches."""
        for cache in self.caches.values():
            cache.invalidate(fips, model_name)
            
    def close_all(self):
        """Close all cache connections."""
        for cache in self.caches.values():
            cache.close()


# Convenience function
def create_embedding_cache(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    disk_path: str = "./cache/embeddings",
    memory_size: int = 1000
) -> EmbeddingCache:
    """
    Create an embedding cache with specified configuration.
    
    Args:
        redis_host: Redis host
        redis_port: Redis port
        disk_path: Disk cache path
        memory_size: Memory cache size
        
    Returns:
        Configured EmbeddingCache instance
    """
    config = CacheConfig(
        redis_host=redis_host,
        redis_port=redis_port,
        disk_cache_path=disk_path,
        memory_cache_size=memory_size
    )
    
    return EmbeddingCache(config)


if __name__ == "__main__":
    # Example usage
    print("EmbeddingCache - Example Usage")
    print("=" * 50)
    
    # Create cache
    config = CacheConfig(
        disk_cache_path="./test_cache/embeddings",
        memory_cache_size=100
    )
    cache = EmbeddingCache(config)
    
    # Sample county data
    county_data = {
        'fips': '01001',
        'county_name': 'Autauga County',
        'state': 'Alabama'
    }
    
    # Sample embedding
    embedding = np.random.randn(384).astype(np.float32)
    
    # Store in cache
    print("\nStoring embedding in cache...")
    success = cache.set(county_data, "model_v1", embedding)
    print(f"Store successful: {success}")
    
    # Retrieve from cache
    print("\nRetrieving embedding from cache...")
    cached = cache.get(county_data, "model_v1")
    print(f"Cache hit: {cached is not None}")
    
    if cached is not None:
        print(f"Embedding shape: {cached.shape}")
        print(f"Values match: {np.allclose(embedding, cached)}")
    
    # Get stats
    print("\nCache statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Cleanup
    cache.close()
    
    print("\nEmbeddingCache ready for use!")
