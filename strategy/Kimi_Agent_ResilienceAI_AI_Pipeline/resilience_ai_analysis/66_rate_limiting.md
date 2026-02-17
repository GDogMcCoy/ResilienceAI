# ResilienceAI Rate Limiting Design

## Executive Summary

This document provides a comprehensive rate limiting architecture for ResilienceAI, designed to protect API resources, ensure fair usage, and maintain system stability under varying load conditions.

---

## 1. Rate Limiting Architecture Overview

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ResilienceAI Rate Limiting Layer                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Client     │───▶│  API Gateway │───▶│ Rate Limiter │                  │
│  │   Request    │    │   (Nginx/    │    │   Middleware │                  │
│  │              │    │    Envoy)    │    │              │                  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘                  │
│                       ┌──────────────────────────┼──────────────────┐      │
│                       ▼                          ▼                  ▼      │
│              ┌─────────────┐           ┌─────────────┐    ┌─────────────┐  │
│              │   Token     │           │   Window    │    │ Distributed │  │
│              │   Bucket    │           │   Counter   │    │   Counter   │  │
│              └──────┬──────┘           └──────┬──────┘    └──────┬──────┘  │
│                     │                         │                  │        │
│                     └─────────────────────────┴──────────────────┘        │
│                                               │                           │
│                                               ▼                           │
│                                    ┌─────────────────────┐                │
│                                    │    Redis Cluster    │                │
│                                    │  (Distributed Store)│                │
│                                    └─────────────────────┘                │
│                                               │                           │
│                                               ▼                           │
│                                    ┌─────────────────────┐                │
│                                    │   Application API   │                │
│                                    │    (FastAPI/Flask)  │                │
│                                    └─────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Rate Limiting Layers

| Layer | Purpose | Implementation |
|-------|---------|----------------|
| Edge/Gateway | First line of defense | Nginx/Envoy rate limiting |
| Application | Business logic limits | FastAPI middleware |
| Distributed | Cross-instance coordination | Redis Cluster |
| Endpoint-specific | Granular API control | Decorator-based |

### 1.3 Rate Limiting Strategies Matrix

| Strategy | Burst | Steady | Distributed | Accuracy |
|----------|-------|--------|-------------|----------|
| Token Bucket | Excellent | Good | Good | High |
| Fixed Window | Poor | Good | Excellent | Low |
| Sliding Window | Good | Excellent | Good | High |
| Leaky Bucket | Poor | Excellent | Moderate | High |
| Sliding Window Log | Good | Excellent | Moderate | Very High |

---

## 2. Token Bucket Algorithm Implementation

### 2.1 Core Token Bucket Class

```python
# File: /app/infrastructure/rate_limiting/token_bucket.py

import time
import threading
from typing import Optional, Dict
from dataclasses import dataclass
import asyncio
import redis.asyncio as redis


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    def __init__(self, retry_after: float, limit: int, remaining: int):
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


@dataclass
class TokenBucketConfig:
    """Configuration for token bucket"""
    capacity: int           # Maximum tokens in bucket
    refill_rate: float      # Tokens added per second
    initial_tokens: Optional[int] = None


class TokenBucket:
    """
    In-memory token bucket implementation.
    Features:
    - Thread-safe operations
    - Configurable capacity and refill rate
    - Supports burst handling
    """
    
    def __init__(self, config: TokenBucketConfig):
        self.capacity = config.capacity
        self.refill_rate = config.refill_rate
        self.tokens = config.initial_tokens or config.capacity
        self.last_refill = time.monotonic()
        self._lock = threading.RLock()
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time"""
        now = time.monotonic()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens from the bucket"""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Calculate wait time until enough tokens are available"""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                return 0.0
            tokens_needed = tokens - self.tokens
            return tokens_needed / self.refill_rate
    
    def peek(self) -> Dict[str, float]:
        """Get current bucket state without consuming"""
        with self._lock:
            self._refill()
            return {
                "tokens": self.tokens,
                "capacity": self.capacity,
                "available_percentage": (self.tokens / self.capacity) * 100
            }


class AsyncTokenBucket:
    """Async-compatible token bucket implementation"""
    
    def __init__(self, config: TokenBucketConfig):
        self.capacity = config.capacity
        self.refill_rate = config.refill_rate
        self.tokens = config.initial_tokens or config.capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    async def consume(self, tokens: int = 1) -> bool:
        async with self._lock:
            await self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
```

### 2.2 Distributed Token Bucket with Redis

```python
# File: /app/infrastructure/rate_limiting/redis_token_bucket.py

import redis.asyncio as redis
from typing import Optional, Dict
import time


class RedisTokenBucket:
    """
    Distributed token bucket using Redis.
    Uses Redis Lua scripts for atomic operations to ensure
    consistency across multiple application instances.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        key_prefix: str,
        capacity: int,
        refill_rate: float
    ):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.capacity = capacity
        self.refill_rate = refill_rate
        
        # Lua script for atomic token consumption
        self._consume_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now
        
        local elapsed = now - last_refill
        local tokens_to_add = elapsed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)
        
        local allowed = 0
        local remaining = tokens
        
        if tokens >= tokens_requested then
            tokens = tokens - tokens_requested
            allowed = 1
            remaining = tokens
        end
        
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) + 1)
        
        return {allowed, remaining, capacity}
        """
        self._consume_sha: Optional[str] = None
    
    async def _get_script_sha(self) -> str:
        if self._consume_sha is None:
            self._consume_sha = await self.redis.script_load(self._consume_script)
        return self._consume_sha
    
    async def consume(self, identifier: str, tokens: int = 1) -> Dict[str, any]:
        key = f"{self.key_prefix}:{identifier}"
        now = time.time()
        
        try:
            sha = await self._get_script_sha()
            result = await self.redis.evalsha(
                sha, 1, key, self.capacity, self.refill_rate, tokens, now
            )
        except redis.NoScriptError:
            result = await self.redis.eval(
                self._consume_script, 1, key, self.capacity, self.refill_rate, tokens, now
            )
        
        return {
            "allowed": bool(result[0]),
            "remaining": int(result[1]),
            "limit": int(result[2])
        }
    
    async def get_state(self, identifier: str) -> Dict[str, float]:
        key = f"{self.key_prefix}:{identifier}"
        bucket = await self.redis.hmget(key, 'tokens', 'last_refill')
        
        if bucket[0] is None:
            return {"tokens": self.capacity, "capacity": self.capacity, "available_percentage": 100.0}
        
        tokens = float(bucket[0])
        last_refill = float(bucket[1])
        now = time.time()
        elapsed = now - last_refill
        tokens = min(self.capacity, tokens + elapsed * self.refill_rate)
        
        return {
            "tokens": tokens,
            "capacity": self.capacity,
            "available_percentage": (tokens / self.capacity) * 100
        }
    
    async def reset(self, identifier: str) -> None:
        key = f"{self.key_prefix}:{identifier}"
        await self.redis.delete(key)
```

---

## 3. Fixed and Sliding Window Implementations

### 3.1 Fixed Window Counter

```python
# File: /app/infrastructure/rate_limiting/fixed_window.py

import time
import redis.asyncio as redis
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class FixedWindowConfig:
    """Configuration for fixed window rate limiting"""
    window_size: int    # Window size in seconds
    max_requests: int   # Maximum requests per window


class FixedWindowCounter:
    """
    Fixed window rate limiting implementation.
    Simple and efficient but can allow bursts at window boundaries.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        config: FixedWindowConfig,
        key_prefix: str = "fixed_window"
    ):
        self.redis = redis_client
        self.config = config
        self.key_prefix = key_prefix
        
        self._script = """
        local key = KEYS[1]
        local window = tonumber(ARGV[1])
        local limit = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        local current_window = math.floor(now / window)
        local window_key = key .. ":" .. current_window
        
        local current = redis.call('INCR', window_key)
        
        if current == 1 then
            redis.call('EXPIRE', window_key, window * 2)
        end
        
        local allowed = 0
        if current <= limit then
            allowed = 1
        end
        
        local remaining = math.max(0, limit - current)
        local reset_time = (current_window + 1) * window
        
        return {allowed, remaining, limit, reset_time}
        """
        self._script_sha: Optional[str] = None
    
    async def _get_script_sha(self) -> str:
        if self._script_sha is None:
            self._script_sha = await self.redis.script_load(self._script)
        return self._script_sha
    
    async def is_allowed(self, identifier: str) -> Dict[str, any]:
        key = f"{self.key_prefix}:{identifier}"
        now = time.time()
        
        try:
            sha = await self._get_script_sha()
            result = await self.redis.evalsha(
                sha, 1, key, self.config.window_size, self.config.max_requests, now
            )
        except redis.NoScriptError:
            result = await self.redis.eval(
                self._script, 1, key, self.config.window_size, self.config.max_requests, now
            )
        
        return {
            "allowed": bool(result[0]),
            "remaining": max(0, int(result[1])),
            "limit": int(result[2]),
            "reset_time": int(result[3])
        }
```

### 3.2 Sliding Window Counter

```python
# File: /app/infrastructure/rate_limiting/sliding_window.py

import time
import redis.asyncio as redis
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SlidingWindowConfig:
    """Configuration for sliding window rate limiting"""
    window_size: int    # Window size in seconds
    max_requests: int   # Maximum requests per window


class SlidingWindowCounter:
    """
    Sliding window rate limiting implementation.
    More accurate than fixed window but requires more Redis operations.
    Uses sorted sets for efficient time-based counting.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        config: SlidingWindowConfig,
        key_prefix: str = "sliding_window"
    ):
        self.redis = redis_client
        self.config = config
        self.key_prefix = key_prefix
        
        self._script = """
        local key = KEYS[1]
        local window = tonumber(ARGV[1])
        local limit = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local window_start = now - window
        
        redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
        local current = redis.call('ZCARD', key)
        
        local allowed = 0
        if current < limit then
            allowed = 1
            redis.call('ZADD', key, now, now .. ":" .. redis.call('INCR', key .. ":seq"))
            redis.call('EXPIRE', key, window)
        end
        
        local remaining = math.max(0, limit - current - allowed)
        local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
        local reset_time = now + window
        
        if #oldest >= 2 then
            reset_time = tonumber(oldest[2]) + window
        end
        
        return {allowed, remaining, limit, reset_time, current}
        """
        self._script_sha: Optional[str] = None
    
    async def _get_script_sha(self) -> str:
        if self._script_sha is None:
            self._script_sha = await self.redis.script_load(self._script)
        return self._script_sha
    
    async def is_allowed(self, identifier: str) -> Dict[str, any]:
        key = f"{self.key_prefix}:{identifier}"
        now = time.time()
        
        try:
            sha = await self._get_script_sha()
            result = await self.redis.evalsha(
                sha, 1, key, self.config.window_size, self.config.max_requests, now
            )
        except redis.NoScriptError:
            result = await self.redis.eval(
                self._script, 1, key, self.config.window_size, self.config.max_requests, now
            )
        
        return {
            "allowed": bool(result[0]),
            "remaining": max(0, int(result[1])),
            "limit": int(result[2]),
            "reset_time": int(result[3]),
            "current_count": int(result[4])
        }
```

---

## 4. Per-User and Per-Endpoint Rate Limiting

### 4.1 User-Based Rate Limiting

```python
# File: /app/infrastructure/rate_limiting/user_rate_limiter.py

import redis.asyncio as redis
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class UserTier(Enum):
    """User tiers with different rate limits"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    INTERNAL = "internal"


@dataclass
class UserRateLimitConfig:
    """Rate limit configuration for a user tier"""
    tier: UserTier
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_capacity: int
    concurrent_requests: int


# Default tier configurations
DEFAULT_TIER_CONFIGS: Dict[UserTier, UserRateLimitConfig] = {
    UserTier.FREE: UserRateLimitConfig(
        tier=UserTier.FREE,
        requests_per_minute=10,
        requests_per_hour=100,
        requests_per_day=1000,
        burst_capacity=5,
        concurrent_requests=2
    ),
    UserTier.BASIC: UserRateLimitConfig(
        tier=UserTier.BASIC,
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
        burst_capacity=20,
        concurrent_requests=5
    ),
    UserTier.PRO: UserRateLimitConfig(
        tier=UserTier.PRO,
        requests_per_minute=300,
        requests_per_hour=5000,
        requests_per_day=50000,
        burst_capacity=50,
        concurrent_requests=10
    ),
    UserTier.ENTERPRISE: UserRateLimitConfig(
        tier=UserTier.ENTERPRISE,
        requests_per_minute=1000,
        requests_per_hour=20000,
        requests_per_day=200000,
        burst_capacity=100,
        concurrent_requests=25
    ),
    UserTier.INTERNAL: UserRateLimitConfig(
        tier=UserTier.INTERNAL,
        requests_per_minute=10000,
        requests_per_hour=100000,
        requests_per_day=1000000,
        burst_capacity=500,
        concurrent_requests=100
    )
}
```

---

## 5. Rate Limit Headers Implementation

### 5.1 Standard Rate Limit Headers

```python
# File: /app/infrastructure/rate_limiting/headers.py

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class RateLimitHeaderFormat(Enum):
    """Rate limit header format standards"""
    IETF_DRAFT = "ietf_draft"
    X_RATE_LIMIT = "x_rate_limit"
    GITHUB = "github"


@dataclass
class RateLimitHeaders:
    """Standard rate limit headers"""
    limit: int
    remaining: int
    reset: int
    reset_after: Optional[int] = None
    policy: Optional[str] = None
    retry_after: Optional[int] = None
    
    def to_dict(self, format: RateLimitHeaderFormat = RateLimitHeaderFormat.IETF_DRAFT) -> Dict[str, str]:
        if format == RateLimitHeaderFormat.IETF_DRAFT:
            return self._to_ietf_headers()
        elif format == RateLimitHeaderFormat.X_RATE_LIMIT:
            return self._to_x_headers()
        elif format == RateLimitHeaderFormat.GITHUB:
            return self._to_github_headers()
        return {}
    
    def _to_ietf_headers(self) -> Dict[str, str]:
        headers = {
            "RateLimit-Limit": str(self.limit),
            "RateLimit-Remaining": str(self.remaining),
            "RateLimit-Reset": str(self.reset)
        }
        if self.policy:
            headers["RateLimit-Policy"] = self.policy
        if self.retry_after:
            headers["Retry-After"] = str(self.retry_after)
        return headers
    
    def _to_x_headers(self) -> Dict[str, str]:
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.remaining),
            "X-RateLimit-Reset": str(self.reset)
        }
        if self.reset_after:
            headers["X-RateLimit-Reset-After"] = str(self.reset_after)
        if self.retry_after:
            headers["Retry-After"] = str(self.retry_after)
        return headers
    
    def _to_github_headers(self) -> Dict[str, str]:
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.remaining),
            "X-RateLimit-Reset": str(self.reset),
            "X-RateLimit-Used": str(self.limit - self.remaining)
        }
        if self.policy:
            headers["X-RateLimit-Resource"] = self.policy
        if self.retry_after:
            headers["Retry-After"] = str(self.retry_after)
        return headers
```

---

## 6. Throttling Responses

### 6.1 Throttling Handler

```python
# File: /app/infrastructure/rate_limiting/throttling.py

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
import time


class ThrottleStrategy(Enum):
    """Throttling response strategies"""
    IMMEDIATE_REJECT = "immediate_reject"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    QUEUE = "queue"
    GRADUAL_DEGRADATION = "gradual_degradation"


@dataclass
class ThrottleConfig:
    """Configuration for throttling behavior"""
    strategy: ThrottleStrategy
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    queue_size: int = 100
    degradation_levels: int = 3


class ThrottlingHandler:
    """Advanced throttling response handler"""
    
    def __init__(self, config: ThrottleConfig):
        self.config = config
        self._backoff_tracker: Dict[str, Dict] = {}
        self._request_queue: Dict[str, list] = {}
    
    def calculate_backoff(self, identifier: str, attempt: int) -> float:
        if self.config.strategy == ThrottleStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        elif self.config.strategy == ThrottleStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * attempt
        else:
            delay = self.config.base_delay
        return min(delay, self.config.max_delay)
    
    def get_throttle_response(self, identifier: str, retry_after: int, limit_info: Dict[str, any]) -> Dict[str, any]:
        if self.config.strategy == ThrottleStrategy.IMMEDIATE_REJECT:
            return self._immediate_reject_response(retry_after, limit_info)
        elif self.config.strategy == ThrottleStrategy.EXPONENTIAL_BACKOFF:
            return self._backoff_response(identifier, retry_after, limit_info)
        elif self.config.strategy == ThrottleStrategy.LINEAR_BACKOFF:
            return self._backoff_response(identifier, retry_after, limit_info)
        elif self.config.strategy == ThrottleStrategy.QUEUE:
            return self._queue_response(identifier, limit_info)
        elif self.config.strategy == ThrottleStrategy.GRADUAL_DEGRADATION:
            return self._degradation_response(identifier, limit_info)
        return self._immediate_reject_response(retry_after, limit_info)
    
    def _immediate_reject_response(self, retry_after: int, limit_info: Dict[str, any]) -> Dict[str, any]:
        return {
            "status_code": 429,
            "headers": {
                "Content-Type": "application/json",
                "Retry-After": str(retry_after)
            },
            "body": {
                "error": "Too Many Requests",
                "message": "Rate limit exceeded. Please retry after the specified time.",
                "retry_after": retry_after,
                "limit": limit_info.get("limit"),
                "remaining": limit_info.get("remaining"),
                "reset_time": limit_info.get("reset_time"),
                "documentation_url": "https://docs.resilienceai.com/rate-limits"
            }
        }
```

---

## 7. Distributed Rate Limiting

### 7.1 Distributed Rate Limiter

```python
# File: /app/infrastructure/rate_limiting/distributed.py

import redis.asyncio as redis
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio
import hashlib
import time


@dataclass
class DistributedConfig:
    """Configuration for distributed rate limiting"""
    redis_nodes: List[str]
    sync_interval: float = 1.0
    consistency_level: str = "quorum"  # "one", "quorum", "all"
    partition_tolerance: bool = True


class ConsistentHashRing:
    """Consistent hashing for distributed rate limit partitioning"""
    
    def __init__(self, nodes: List[str], replicas: int = 150):
        self.nodes = nodes
        self.replicas = replicas
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        
        for node in nodes:
            self._add_node(node)
    
    def _add_node(self, node: str) -> None:
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)
        self.sorted_keys.sort()
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def get_node(self, key: str) -> str:
        if not self.ring:
            raise ValueError("No nodes in hash ring")
        hash_key = self._hash(key)
        for ring_key in self.sorted_keys:
            if ring_key >= hash_key:
                return self.ring[ring_key]
        return self.ring[self.sorted_keys[0]]
    
    def get_nodes(self, key: str, n: int = 3) -> List[str]:
        if not self.ring:
            raise ValueError("No nodes in hash ring")
        hash_key = self._hash(key)
        nodes = []
        seen = set()
        start_idx = 0
        for i, ring_key in enumerate(self.sorted_keys):
            if ring_key >= hash_key:
                start_idx = i
                break
        for i in range(len(self.sorted_keys)):
            idx = (start_idx + i) % len(self.sorted_keys)
            node = self.ring[self.sorted_keys[idx]]
            if node not in seen:
                seen.add(node)
                nodes.append(node)
                if len(nodes) >= n:
                    break
        return nodes
```

---

## 8. Rate Limit Monitoring

### 8.1 Monitoring and Metrics

```python
# File: /app/infrastructure/rate_limiting/monitoring.py

import redis.asyncio as redis
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import json
import time
from collections import defaultdict
import asyncio


@dataclass
class RateLimitMetrics:
    """Rate limit metrics data"""
    timestamp: float
    identifier: str
    endpoint: str
    allowed: bool
    limit: int
    remaining: int
    wait_time: float = 0.0
    region: str = "default"


class RateLimitMetricsCollector:
    """Collects and aggregates rate limit metrics"""
    
    def __init__(self, redis_client: redis.Redis, retention_hours: int = 24):
        self.redis = redis_client
        self.retention_hours = retention_hours
        self._buffer: List[RateLimitMetrics] = []
        self._buffer_lock = asyncio.Lock()
        self._flush_interval = 10
        self._running = False
    
    async def record(self, metrics: RateLimitMetrics) -> None:
        async with self._buffer_lock:
            self._buffer.append(metrics)
    
    async def start(self) -> None:
        self._running = True
        while self._running:
            await asyncio.sleep(self._flush_interval)
            await self._flush_buffer()
    
    async def stop(self) -> None:
        self._running = False
        await self._flush_buffer()
    
    async def _flush_buffer(self) -> None:
        async with self._buffer_lock:
            if not self._buffer:
                return
            metrics_batch = self._buffer[:]
            self._buffer = []
        
        pipeline = self.redis.pipeline()
        for metric in metrics_batch:
            key = f"metrics:rate_limit:{metric.endpoint}"
            score = metric.timestamp
            value = json.dumps({
                "identifier": metric.identifier,
                "allowed": metric.allowed,
                "limit": metric.limit,
                "remaining": metric.remaining,
                "wait_time": metric.wait_time,
                "region": metric.region
            })
            pipeline.zadd(key, {value: score})
            expiry = int(time.time()) + (self.retention_hours * 3600)
            pipeline.expireat(key, expiry)
        await pipeline.execute()
```

---

## 9. Whitelist and Blacklist System

### 9.1 Access Control Lists

```python
# File: /app/infrastructure/rate_limiting/access_control.py

import redis.asyncio as redis
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import ipaddress
import re
import time


class AccessDecision(Enum):
    """Access control decisions"""
    ALLOW = "allow"
    DENY = "deny"
    RATE_LIMIT = "rate_limit"
    CHALLENGE = "challenge"


@dataclass
class AccessRule:
    """Access control rule"""
    name: str
    decision: AccessDecision
    priority: int
    conditions: Dict[str, any]
    description: str = ""
    expires_at: Optional[float] = None


class IPRangeMatcher:
    """Match IP addresses against CIDR ranges"""
    
    def __init__(self):
        self._networks: List[ipaddress.IPv4Network] = []
        self._ipv6_networks: List[ipaddress.IPv6Network] = []
    
    def add_range(self, cidr: str) -> None:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if isinstance(network, ipaddress.IPv4Network):
                self._networks.append(network)
            else:
                self._ipv6_networks.append(network)
        except ValueError:
            pass
    
    def matches(self, ip: str) -> bool:
        try:
            addr = ipaddress.ip_address(ip)
            if isinstance(addr, ipaddress.IPv4Address):
                return any(addr in network for network in self._networks)
            else:
                return any(addr in network for network in self._ipv6_networks)
        except ValueError:
            return False


class AccessControlList:
    """Comprehensive access control list system"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self._ip_matcher = IPRangeMatcher()
        self._rules: List[AccessRule] = []
        self._cache: Dict[str, AccessDecision] = {}
        self._cache_ttl = 60
    
    async def add_whitelist_ip(self, ip_or_range: str, description: str = "", expires_at: Optional[float] = None) -> None:
        key = "acl:whitelist:ip"
        entry = {
            "range": ip_or_range,
            "description": description,
            "added_at": time.time(),
            "expires_at": expires_at
        }
        await self.redis.hset(key, ip_or_range, json.dumps(entry))
        self._ip_matcher.add_range(ip_or_range)
    
    async def add_blacklist_ip(self, ip_or_range: str, reason: str = "", expires_at: Optional[float] = None, metadata: Optional[Dict] = None) -> None:
        key = "acl:blacklist:ip"
        entry = {
            "range": ip_or_range,
            "reason": reason,
            "added_at": time.time(),
            "expires_at": expires_at,
            "metadata": metadata or {}
        }
        await self.redis.hset(key, ip_or_range, json.dumps(entry))
        await self.redis.setex(
            f"block:{ip_or_range}",
            int(expires_at - time.time()) if expires_at else 86400,
            json.dumps(entry)
        )
```

---

## 10. Configuration

### 10.1 Rate Limit Configuration File

```yaml
# File: /config/rate_limiting.yaml

# Global rate limiting settings
global:
  enabled: true
  default_algorithm: "token_bucket"
  header_format: "ietf_draft"

# User tier configurations
user_tiers:
  free:
    requests_per_minute: 10
    requests_per_hour: 100
    requests_per_day: 1000
    burst_capacity: 5
    concurrent_requests: 2
  basic:
    requests_per_minute: 60
    requests_per_hour: 1000
    requests_per_day: 10000
    burst_capacity: 20
    concurrent_requests: 5
  pro:
    requests_per_minute: 300
    requests_per_hour: 5000
    requests_per_day: 50000
    burst_capacity: 50
    concurrent_requests: 10
  enterprise:
    requests_per_minute: 1000
    requests_per_hour: 20000
    requests_per_day: 200000
    burst_capacity: 100
    concurrent_requests: 25
  internal:
    requests_per_minute: 10000
    requests_per_hour: 100000
    requests_per_day: 1000000
    burst_capacity: 500
    concurrent_requests: 100

# Endpoint-specific rate limits
endpoints:
  - path: "/api/v1/predict"
    method: "POST"
    requests_per_second: 2.0
    requests_per_minute: 30
    burst_size: 5
    algorithm: "token_bucket"
  - path: "/api/v1/batch"
    method: "POST"
    requests_per_second: 0.5
    requests_per_minute: 10
    burst_size: 2
    algorithm: "token_bucket"
  - path: "/api/v1/train"
    method: "POST"
    requests_per_second: 0.1
    requests_per_minute: 2
    burst_size: 1
    algorithm: "token_bucket"
  - path: "/api/v1/health"
    method: "GET"
    requests_per_second: 10.0
    requests_per_minute: 600
    burst_size: 20
    algorithm: "sliding_window"

# Distributed rate limiting
distributed:
  enabled: true
  redis_nodes:
    - "redis-node-1:6379"
    - "redis-node-2:6379"
    - "redis-node-3:6379"
  consistency_level: "quorum"
  sync_interval: 1.0

# Throttling configuration
throttling:
  strategy: "exponential_backoff"
  base_delay: 1.0
  max_delay: 60.0
  exponential_base: 2.0

# Monitoring configuration
monitoring:
  enabled: true
  retention_hours: 24
  flush_interval: 10
  alert_thresholds:
    deny_rate_warning: 20.0
    deny_rate_critical: 50.0
    near_limit_threshold: 5

# Access control lists
access_control:
  whitelist:
    ips:
      - "10.0.0.0/8"
      - "172.16.0.0/12"
      - "192.168.0.0/16"
    users:
      - "admin"
      - "service_account"
  blacklist:
    auto_block_duration: 3600
    max_failed_attempts: 5
```

---

## 11. Implementation Priority Order

### Phase 1: Core Rate Limiting (Week 1)
1. **Token Bucket Algorithm** - Priority: CRITICAL
2. **Fixed Window Counter** - Priority: HIGH
3. **User-Based Rate Limiting** - Priority: CRITICAL

### Phase 2: Advanced Features (Week 2)
4. **Sliding Window Counter** - Priority: HIGH
5. **Endpoint-Based Rate Limiting** - Priority: HIGH
6. **Rate Limit Headers** - Priority: MEDIUM

### Phase 3: Distributed & Monitoring (Week 3)
7. **Distributed Rate Limiting** - Priority: HIGH
8. **Throttling Responses** - Priority: MEDIUM
9. **Monitoring & Alerting** - Priority: MEDIUM

### Phase 4: Access Control & Polish (Week 4)
10. **Whitelist/Blacklist** - Priority: MEDIUM
11. **Testing & Documentation** - Priority: HIGH
12. **Performance Optimization** - Priority: MEDIUM

---

## 12. Summary

This comprehensive rate limiting design for ResilienceAI provides:

### Key Features
- **Multiple Algorithms**: Token bucket, fixed window, sliding window
- **Flexible Configuration**: Per-user, per-endpoint, tier-based limits
- **Distributed Support**: Redis-based coordination across instances
- **Rich Headers**: Standard-compliant rate limit headers
- **Smart Throttling**: Multiple throttling strategies
- **Access Control**: Whitelist/blacklist with pattern matching
- **Monitoring**: Real-time metrics and alerting

### Architecture Highlights
- Layered rate limiting (edge, application, distributed)
- Lua scripts for atomic Redis operations
- Consistent hashing for distributed deployments
- Circuit breaker pattern for resilience
- Comprehensive testing strategy

### Production Readiness
- Horizontal scaling support
- Graceful degradation
- Detailed monitoring
- Configurable strategies
- Performance optimized

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Engineering Team*
