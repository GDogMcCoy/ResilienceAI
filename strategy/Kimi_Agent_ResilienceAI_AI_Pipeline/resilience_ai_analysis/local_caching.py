"""
Local Caching Strategy for ResilienceAI Edge
============================================
Multi-tier caching for optimal performance and offline capability.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import threading


class CacheTier(Enum):
    """Cache tier levels"""
    MEMORY = "memory"
    LOCAL_SSD = "ssd"
    LOCAL_HDD = "hdd"
    EXTERNAL = "external"


class EvictionPolicy(Enum):
    """Cache eviction policies"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"
    SIZE = "size"


@dataclass
class CacheEntry:
    """Cache entry metadata"""
    key: str
    value: Any
    size_bytes: int
    created_at: datetime
    accessed_at: datetime
    access_count: int
    ttl_seconds: Optional[int]
    tier: CacheTier


class MultiTierCache:
    """Multi-tier caching system for edge deployment"""
    
    def __init__(
        self,
        memory_limit_mb: float = 512,
        ssd_limit_gb: float = 10,
        hdd_limit_gb: float = 100,
        eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    ):
        self.memory_limit = memory_limit_mb * 1024 * 1024
        self.ssd_limit = ssd_limit_gb * 1024 * 1024 * 1024
        self.hdd_limit = hdd_limit_gb * 1024 * 1024 * 1024
        
        self.eviction_policy = eviction_policy
        
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.ssd_cache: Dict[str, CacheEntry] = {}
        self.hdd_cache: Dict[str, CacheEntry] = {}
        
        self.tier_usage = {
            CacheTier.MEMORY: 0,
            CacheTier.LOCAL_SSD: 0,
            CacheTier.LOCAL_HDD: 0
        }
        
        self.lock = threading.RLock()
        
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "writes": 0
        }
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            for tier, cache in [
                (CacheTier.MEMORY, self.memory_cache),
                (CacheTier.LOCAL_SSD, self.ssd_cache),
                (CacheTier.LOCAL_HDD, self.hdd_cache)
            ]:
                if key in cache:
                    entry = cache[key]
                    
                    if entry.ttl_seconds:
                        age = (datetime.utcnow() - entry.created_at).total_seconds()
                        if age > entry.ttl_seconds:
                            del cache[key]
                            self.tier_usage[tier] -= entry.size_bytes
                            self.stats["misses"] += 1
                            return None
                            
                    entry.accessed_at = datetime.utcnow()
                    entry.access_count += 1
                    
                    if tier != CacheTier.MEMORY and entry.access_count > 5:
                        self._promote_entry(entry)
                        
                    self.stats["hits"] += 1
                    return entry.value
                    
            self.stats["misses"] += 1
            return None
            
    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None, preferred_tier: CacheTier = CacheTier.MEMORY):
        """Put value into cache"""
        with self.lock:
            size = self._estimate_size(value)
            tier = self._select_tier(size, preferred_tier)
            
            entry = CacheEntry(
                key=key,
                value=value,
                size_bytes=size,
                created_at=datetime.utcnow(),
                accessed_at=datetime.utcnow(),
                access_count=0,
                ttl_seconds=ttl_seconds,
                tier=tier
            )
            
            cache = self._get_cache_for_tier(tier)
            
            if self.tier_usage[tier] + size > self._get_limit_for_tier(tier):
                self._evict_entries(tier, size)
                
            cache[key] = entry
            self.tier_usage[tier] += size
            self.stats["writes"] += 1
            
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        try:
            return len(json.dumps(value).encode('utf-8'))
        except:
            return 1024
            
    def _select_tier(self, size: int, preferred: CacheTier) -> CacheTier:
        """Select appropriate cache tier"""
        if preferred == CacheTier.MEMORY and size < self.memory_limit * 0.1:
            return CacheTier.MEMORY
        elif preferred == CacheTier.LOCAL_SSD and size < self.ssd_limit * 0.1:
            return CacheTier.LOCAL_SSD
            
        if size < 1024 * 1024:
            return CacheTier.MEMORY
        elif size < 100 * 1024 * 1024:
            return CacheTier.LOCAL_SSD
        else:
            return CacheTier.LOCAL_HDD
            
    def _get_cache_for_tier(self, tier: CacheTier) -> Dict:
        """Get cache dictionary for tier"""
        if tier == CacheTier.MEMORY:
            return self.memory_cache
        elif tier == CacheTier.LOCAL_SSD:
            return self.ssd_cache
        else:
            return self.hdd_cache
            
    def _get_limit_for_tier(self, tier: CacheTier) -> int:
        """Get size limit for tier"""
        if tier == CacheTier.MEMORY:
            return self.memory_limit
        elif tier == CacheTier.LOCAL_SSD:
            return self.ssd_limit
        else:
            return self.hdd_limit
            
    def _evict_entries(self, tier: CacheTier, required_space: int):
        """Evict entries to make space"""
        cache = self._get_cache_for_tier(tier)
        freed_space = 0
        entries_to_evict = self._select_entries_to_evict(cache, tier)
        
        for key in entries_to_evict:
            if freed_space >= required_space:
                break
            entry = cache[key]
            freed_space += entry.size_bytes
            del cache[key]
            self.tier_usage[tier] -= entry.size_bytes
            self.stats["evictions"] += 1
            
    def _select_entries_to_evict(self, cache: Dict, tier: CacheTier) -> List[str]:
        """Select entries to evict based on policy"""
        entries = list(cache.values())
        
        if self.eviction_policy == EvictionPolicy.LRU:
            entries.sort(key=lambda e: e.accessed_at)
        elif self.eviction_policy == EvictionPolicy.LFU:
            entries.sort(key=lambda e: e.access_count)
        elif self.eviction_policy == EvictionPolicy.FIFO:
            entries.sort(key=lambda e: e.created_at)
        elif self.eviction_policy == EvictionPolicy.TTL:
            entries.sort(key=lambda e: e.ttl_seconds or float('inf'))
        elif self.eviction_policy == EvictionPolicy.SIZE:
            entries.sort(key=lambda e: e.size_bytes, reverse=True)
            
        return [e.key for e in entries]
        
    def _promote_entry(self, entry: CacheEntry):
        """Promote entry to faster tier"""
        pass
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "evictions": self.stats["evictions"],
            "writes": self.stats["writes"],
            "tier_usage": {
                tier.value: {
                    "used_bytes": usage,
                    "used_percent": usage / self._get_limit_for_tier(tier) * 100
                }
                for tier, usage in self.tier_usage.items()
            }
        }
        
    def prefetch(self, keys: List[str], loader: Callable[[str], Any]):
        """Prefetch data into cache"""
        for key in keys:
            if self.get(key) is None:
                value = loader(key)
                if value is not None:
                    self.put(key, value)
