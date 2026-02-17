"""
ResilienceAI Redis Caching Layer
Implements multi-tier caching strategy with Redis
"""

import json
import pickle
import hashlib
import logging
from typing import Any, Optional, Callable, List, Dict, Union
from functools import wraps
from datetime import datetime, timedelta
import redis
from redis.connection import ConnectionPool
from redis.exceptions import RedisError
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Cache TTL configurations (in seconds)
CACHE_TTL = {
    "county_features": 300,           # 5 minutes
    "county_list": 600,               # 10 minutes
    "county_detail": 600,             # 10 minutes
    "vector_search": 60,              # 1 minute
    "predictions": 180,               # 3 minutes
    "dashboard_data": 30,             # 30 seconds
    "aggregations": 120,              # 2 minutes
    "geospatial": 300,                # 5 minutes
    "alerts": 60,                     # 1 minute
    "feature_definitions": 3600,      # 1 hour
    "statistics": 600,                # 10 minutes
    "sessions": 3600,                 # 1 hour
    "rate_limits": 60,                # 1 minute
}

# Serialization format
SERIALIZATION_FORMAT = os.getenv("CACHE_SERIALIZATION", "pickle")  # 'pickle' or 'json'


class ResilienceCache:
    """
    Redis cache manager with tiered caching strategy.
    Supports pickle and JSON serialization.
    """
    
    def __init__(self, url: str = REDIS_URL, db: int = REDIS_DB):
        """
        Initialize Redis cache connection.
        
        Args:
            url: Redis connection URL
            db: Redis database number
        """
        self.pool = ConnectionPool.from_url(url, db=db)
        self.redis = redis.Redis(connection_pool=self.pool, decode_responses=False)
        self._check_connection()
    
    def _check_connection(self):
        """Verify Redis connection"""
        try:
            self.redis.ping()
            logger.info("Redis connection established")
        except RedisError as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value to bytes"""
        if SERIALIZATION_FORMAT == "json":
            return json.dumps(value, default=str).encode('utf-8')
        return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _deserialize(self, value: bytes) -> Any:
        """Deserialize bytes to value"""
        if value is None:
            return None
        if SERIALIZATION_FORMAT == "json":
            return json.loads(value.decode('utf-8'))
        return pickle.loads(value)
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_parts = [prefix]
        
        if args:
            key_parts.append(json.dumps(args, sort_keys=True, default=str))
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True, default=str))
        
        key_data = ":".join(key_parts)
        return f"{prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            return self._deserialize(value)
        except RedisError as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        try:
            serialized = self._serialize(value)
            self.redis.setex(key, ttl, serialized)
        except RedisError as e:
            logger.warning(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            self.redis.delete(key)
        except RedisError as e:
            logger.warning(f"Cache delete error: {e}")
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        try:
            for key in self.redis.scan_iter(match=pattern):
                self.redis.delete(key)
        except RedisError as e:
            logger.warning(f"Cache delete pattern error: {e}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return self.redis.exists(key) > 0
        except RedisError:
            return False
    
    def ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        try:
            return self.redis.ttl(key)
        except RedisError:
            return -2
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        try:
            return self.redis.incr(key, amount)
        except RedisError as e:
            logger.warning(f"Cache increment error: {e}")
            return 0
    
    def expire(self, key: str, ttl: int):
        """Set expiration on existing key"""
        try:
            self.redis.expire(key, ttl)
        except RedisError as e:
            logger.warning(f"Cache expire error: {e}")
    
    # ============================================
    # DECORATOR
    # ============================================
    
    def cached(self, prefix: str, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
        """
        Decorator for caching function results.
        
        Args:
            prefix: Cache key prefix
            ttl: Time-to-live in seconds (uses CACHE_TTL if not specified)
            key_func: Optional custom key generation function
            
        Usage:
            @cache.cached(prefix="county_features", ttl=300)
            def get_county_features(fips_code):
                # Expensive operation
                return result
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache_ttl = ttl or CACHE_TTL.get(prefix, 300)
                self.set(cache_key, result, cache_ttl)
                
                return result
            return wrapper
        return decorator
    
    def cache_evict(self, pattern: str):
        """
        Decorator to evict cache entries after function execution.
        
        Args:
            pattern: Pattern to match keys for eviction
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                self.delete_pattern(pattern)
                return result
            return wrapper
        return decorator
    
    # ============================================
    # COUNTY-SPECIFIC CACHE OPERATIONS
    # ============================================
    
    def cache_county_features(self, fips: str, features: Dict, ttl: int = None):
        """Cache county features"""
        key = f"county:features:{fips}"
        self.set(key, features, ttl or CACHE_TTL["county_features"])
    
    def get_cached_county_features(self, fips: str) -> Optional[Dict]:
        """Get cached county features"""
        return self.get(f"county:features:{fips}")
    
    def cache_county_detail(self, fips: str, data: Dict, ttl: int = None):
        """Cache county detail information"""
        key = f"county:detail:{fips}"
        self.set(key, data, ttl or CACHE_TTL["county_detail"])
    
    def get_cached_county_detail(self, fips: str) -> Optional[Dict]:
        """Get cached county detail"""
        return self.get(f"county:detail:{fips}")
    
    def cache_county_list(self, state: Optional[str], data: List[Dict], ttl: int = None):
        """Cache county list for a state"""
        key = f"county:list:{state or 'all'}"
        self.set(key, data, ttl or CACHE_TTL["county_list"])
    
    def get_cached_county_list(self, state: Optional[str] = None) -> Optional[List[Dict]]:
        """Get cached county list"""
        return self.get(f"county:list:{state or 'all'}")
    
    def invalidate_county(self, fips: str):
        """Invalidate all cache entries for a county"""
        self.delete_pattern(f"county:*:{fips}")
        logger.info(f"Invalidated cache for county: {fips}")
    
    def invalidate_state(self, state: str):
        """Invalidate all cache entries for a state"""
        self.delete_pattern(f"county:list:{state}")
        logger.info(f"Invalidated cache for state: {state}")
    
    # ============================================
    # FEATURE-SPECIFIC CACHE OPERATIONS
    # ============================================
    
    def cache_feature_definitions(self, data: List[Dict], ttl: int = None):
        """Cache feature definitions"""
        self.set("features:definitions", data, ttl or CACHE_TTL["feature_definitions"])
    
    def get_cached_feature_definitions(self) -> Optional[List[Dict]]:
        """Get cached feature definitions"""
        return self.get("features:definitions")
    
    def cache_feature_statistics(self, feature_key: str, stats: Dict, ttl: int = None):
        """Cache feature statistics"""
        key = f"feature:stats:{feature_key}"
        self.set(key, stats, ttl or CACHE_TTL["statistics"])
    
    def get_cached_feature_statistics(self, feature_key: str) -> Optional[Dict]:
        """Get cached feature statistics"""
        return self.get(f"feature:stats:{feature_key}")
    
    # ============================================
    # DASHBOARD CACHE OPERATIONS
    # ============================================
    
    def cache_dashboard_data(self, dashboard_type: str, params: Dict, data: Any, ttl: int = None):
        """Cache dashboard data"""
        key = f"dashboard:{dashboard_type}:{hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()}"
        self.set(key, data, ttl or CACHE_TTL["dashboard_data"])
    
    def get_cached_dashboard_data(self, dashboard_type: str, params: Dict) -> Optional[Any]:
        """Get cached dashboard data"""
        key = f"dashboard:{dashboard_type}:{hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()}"
        return self.get(key)
    
    def invalidate_dashboard(self, dashboard_type: Optional[str] = None):
        """Invalidate dashboard cache"""
        if dashboard_type:
            self.delete_pattern(f"dashboard:{dashboard_type}:*")
        else:
            self.delete_pattern("dashboard:*")
    
    # ============================================
    # VECTOR SEARCH CACHE
    # ============================================
    
    def cache_vector_search(self, query_vector_hash: str, results: List[Dict], ttl: int = None):
        """Cache vector search results"""
        key = f"vector:search:{query_vector_hash}"
        self.set(key, results, ttl or CACHE_TTL["vector_search"])
    
    def get_cached_vector_search(self, query_vector_hash: str) -> Optional[List[Dict]]:
        """Get cached vector search results"""
        return self.get(f"vector:search:{query_vector_hash}")
    
    # ============================================
    # PREDICTION CACHE
    # ============================================
    
    def cache_prediction(self, county_fips: str, prediction_type: str, data: Dict, ttl: int = None):
        """Cache prediction results"""
        key = f"prediction:{county_fips}:{prediction_type}"
        self.set(key, data, ttl or CACHE_TTL["predictions"])
    
    def get_cached_prediction(self, county_fips: str, prediction_type: str) -> Optional[Dict]:
        """Get cached prediction"""
        return self.get(f"prediction:{county_fips}:{prediction_type}")
    
    # ============================================
    # ALERT CACHE
    # ============================================
    
    def cache_alerts(self, fips: Optional[str], alerts: List[Dict], ttl: int = None):
        """Cache alerts for a county or all counties"""
        key = f"alerts:{fips or 'all'}"
        self.set(key, alerts, ttl or CACHE_TTL["alerts"])
    
    def get_cached_alerts(self, fips: Optional[str] = None) -> Optional[List[Dict]]:
        """Get cached alerts"""
        return self.get(f"alerts:{fips or 'all'}")
    
    def invalidate_alerts(self, fips: Optional[str] = None):
        """Invalidate alert cache"""
        if fips:
            self.delete(f"alerts:{fips}")
        else:
            self.delete_pattern("alerts:*")
    
    # ============================================
    # RATE LIMITING
    # ============================================
    
    def check_rate_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """
        Check if request is within rate limit using sliding window.
        
        Args:
            key: Rate limit key (e.g., "api:user:123")
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            True if within limit, False if exceeded
        """
        try:
            current = self.redis.get(key)
            if current is None:
                self.redis.setex(key, window, 1)
                return True
            
            count = int(current)
            if count >= limit:
                return False
            
            self.redis.incr(key)
            return True
        except RedisError as e:
            logger.warning(f"Rate limit check error: {e}")
            # Fail open if Redis is unavailable
            return True
    
    def get_rate_limit_remaining(self, key: str, limit: int) -> int:
        """Get remaining requests in rate limit window"""
        try:
            current = self.redis.get(key)
            if current is None:
                return limit
            return max(0, limit - int(current))
        except RedisError:
            return limit
    
    def reset_rate_limit(self, key: str):
        """Reset rate limit counter"""
        self.delete(key)
    
    # ============================================
    # PUB/SUB FOR REAL-TIME UPDATES
    # ============================================
    
    def publish(self, channel: str, message: Union[str, Dict]):
        """
        Publish message to channel.
        
        Args:
            channel: Channel name
            message: Message to publish (string or dict)
        """
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            self.redis.publish(channel, message)
        except RedisError as e:
            logger.warning(f"Publish error: {e}")
    
    def subscribe(self, channels: List[str], callback: Callable):
        """
        Subscribe to channels and call callback for each message.
        Note: This blocks, so run in a separate thread.
        
        Args:
            channels: List of channel names
            callback: Function to call with message data
        """
        try:
            pubsub = self.redis.pubsub()
            pubsub.subscribe(*channels)
            
            for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                    except json.JSONDecodeError:
                        data = message["data"].decode('utf-8')
                    callback(data)
        except RedisError as e:
            logger.error(f"Subscribe error: {e}")
    
    def publish_alert(self, alert_data: Dict):
        """Publish alert to subscribers"""
        self.publish("alerts:new", alert_data)
        
        # Also publish to county-specific channel
        if "county_fips" in alert_data:
            self.publish(f"alerts:county:{alert_data['county_fips']}", alert_data)
    
    def publish_county_update(self, county_fips: str, update_data: Dict):
        """Publish county data update"""
        self.publish(f"county:update:{county_fips}", update_data)
    
    # ============================================
    # CACHE STATISTICS
    # ============================================
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            info = self.redis.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "total_keys": self.redis.dbsize(),
                "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
            }
        except RedisError as e:
            logger.error(f"Stats error: {e}")
            return {"error": str(e)}
    
    def flush_all(self):
        """Clear all cache (use with caution!)"""
        try:
            self.redis.flushdb()
            logger.warning("Cache flushed")
        except RedisError as e:
            logger.error(f"Flush error: {e}")


# Global cache instance
cache = ResilienceCache()


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def get_cache() -> ResilienceCache:
    """Get global cache instance"""
    return cache


def cached(prefix: str, ttl: Optional[int] = None):
    """Shortcut for cache.cached decorator"""
    return cache.cached(prefix, ttl)


if __name__ == "__main__":
    # Test cache
    print("Testing Redis cache...")
    
    # Test basic operations
    cache.set("test:key", {"foo": "bar"}, ttl=60)
    result = cache.get("test:key")
    print(f"Get result: {result}")
    
    # Test county caching
    cache.cache_county_features("29095", {"population": 717204})
    features = cache.get_cached_county_features("29095")
    print(f"Cached features: {features}")
    
    # Test rate limiting
    allowed = cache.check_rate_limit("test:rate", limit=5, window=60)
    print(f"Rate limit allowed: {allowed}")
    
    # Get stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    # Cleanup
    cache.delete("test:key")
    print("Test completed")
