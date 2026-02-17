"""
ResilienceAI Unified API Gateway
Provides centralized routing, caching, rate limiting, and circuit breaking

File: src/api/gateway.py
"""
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
import hashlib
import json
from functools import wraps
import aiohttp
from aiohttp import ClientTimeout, ClientError

# Optional Redis support
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Optional Prometheus support
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Optional structured logging
try:
    import structlog
    logger = structlog.get_logger()
    STRUCTLOG_AVAILABLE = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    STRUCTLOG_AVAILABLE = False


# Metrics (only if Prometheus available)
if PROMETHEUS_AVAILABLE:
    API_REQUESTS = Counter('api_requests_total', 'Total API requests', ['service', 'endpoint'])
    API_LATENCY = Histogram('api_request_duration_seconds', 'API request latency', ['service'])
    API_ERRORS = Counter('api_errors_total', 'Total API errors', ['service', 'error_type'])
    CIRCUIT_STATE = Gauge('circuit_breaker_state', 'Circuit breaker state', ['service'])


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern"""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    success_threshold: int = 2


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_second: float = 10.0
    burst_size: int = 20
    key_prefix: str = "ratelimit"


@dataclass
class CacheConfig:
    """Configuration for caching"""
    ttl_seconds: int = 300
    max_size: int = 10000
    key_prefix: str = "apicache"


class CircuitBreaker:
    """
    Circuit Breaker Pattern Implementation
    Prevents cascading failures by stopping requests to failing services
    
    Usage:
        cb = CircuitBreaker("noaa")
        result = await cb.call(fetch_weather_data, params)
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.half_open_calls = 0
        self._lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.info(f"Circuit {self.name} entering HALF_OPEN state")
                else:
                    raise CircuitBreakerOpen(f"Circuit {self.name} is OPEN")
            
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpen(f"Circuit {self.name} half-open limit reached")
                self.half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _on_success(self):
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info(f"Circuit {self.name} CLOSED - service recovered")
            else:
                self.failure_count = max(0, self.failure_count - 1)
    
    async def _on_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit {self.name} OPEN - recovery failed")
            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit {self.name} OPEN - failure threshold reached")
        
        if PROMETHEUS_AVAILABLE:
            CIRCUIT_STATE.labels(service=self.name).set(
                0 if self.state == CircuitState.CLOSED else 1
            )
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state


class RateLimiter:
    """
    Token Bucket Rate Limiter
    Supports distributed rate limiting with Redis
    """
    
    def __init__(self, redis_client=None, config: RateLimitConfig = None):
        self.redis = redis_client
        self.config = config or RateLimitConfig()
        self._local_buckets: Dict[str, Dict] = {}
        
    async def acquire(self, key: str) -> bool:
        """Acquire rate limit token"""
        if self.redis and REDIS_AVAILABLE:
            return await self._distributed_acquire(key)
        return self._local_acquire(key)
    
    def _local_acquire(self, key: str) -> bool:
        """Local token bucket implementation"""
        now = time.time()
        bucket = self._local_buckets.get(key, {
            'tokens': self.config.burst_size,
            'last_update': now
        })
        
        # Add tokens based on time elapsed
        elapsed = now - bucket['last_update']
        tokens_to_add = elapsed * self.config.requests_per_second
        bucket['tokens'] = min(self.config.burst_size, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = now
        
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            self._local_buckets[key] = bucket
            return True
        
        self._local_buckets[key] = bucket
        return False
    
    async def _distributed_acquire(self, key: str) -> bool:
        """Redis-based distributed rate limiting"""
        lua_script = """
        local key = KEYS[1]
        local rate = tonumber(ARGV[1])
        local burst = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
        local tokens = tonumber(bucket[1]) or burst
        local last_update = tonumber(bucket[2]) or now
        
        local elapsed = now - last_update
        tokens = math.min(burst, tokens + elapsed * rate)
        
        if tokens >= 1 then
            tokens = tokens - 1
            redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
            redis.call('EXPIRE', key, 60)
            return 1
        else
            redis.call('HSET', key, 'tokens', tokens)
            return 0
        end
        """
        
        result = await self.redis.eval(
            lua_script, 1, 
            f"{self.config.key_prefix}:{key}",
            self.config.requests_per_second,
            self.config.burst_size,
            time.time()
        )
        return bool(result)


class APIGateway:
    """
    Unified API Gateway for ResilienceAI
    Provides centralized API management with caching, rate limiting, and circuit breaking
    
    Usage:
        async with APIGateway() as gateway:
            result = await gateway.request(
                service="noaa",
                method="GET",
                url="https://api.weather.gov/alerts",
                cache_ttl=60
            )
    """
    
    def __init__(self, redis_url: str = None):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiter: Optional[RateLimiter] = None
        self.redis = None
        self.cache: Dict[str, Any] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
        if redis_url and REDIS_AVAILABLE:
            self.redis = aioredis.from_url(redis_url)
            self.rate_limiter = RateLimiter(self.redis)
        else:
            self.rate_limiter = RateLimiter()
    
    async def __aenter__(self):
        timeout = ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.redis:
            await self.redis.close()
    
    def get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker(service)
        return self.circuit_breakers[service]
    
    def _generate_cache_key(self, service: str, endpoint: str, params: Dict) -> str:
        """Generate cache key from request parameters"""
        key_data = f"{service}:{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    async def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached response"""
        if self.redis:
            cached = await self.redis.get(f"cache:{cache_key}")
            if cached:
                return json.loads(cached)
        return self.cache.get(cache_key)
    
    async def _set_cached(self, cache_key: str, data: Any, ttl: int = 300):
        """Cache response"""
        serialized = json.dumps(data, default=str)
        if self.redis:
            await self.redis.setex(f"cache:{cache_key}", ttl, serialized)
        else:
            self.cache[cache_key] = data
    
    async def request(
        self,
        service: str,
        method: str,
        url: str,
        params: Dict = None,
        headers: Dict = None,
        json_data: Dict = None,
        cache_ttl: int = None,
        rate_limit_key: str = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Make API request through gateway with all protections
        
        Args:
            service: Service name for circuit breaker
            method: HTTP method
            url: Request URL
            params: Query parameters
            headers: Request headers
            json_data: JSON body
            cache_ttl: Cache TTL in seconds (None = no cache)
            rate_limit_key: Key for rate limiting
            timeout: Request timeout
            
        Returns:
            Dict with 'data' and 'cached' keys
        """
        # Check rate limit
        if rate_limit_key:
            if not await self.rate_limiter.acquire(rate_limit_key):
                raise RateLimitExceeded(f"Rate limit exceeded for {rate_limit_key}")
        
        # Check cache
        cache_key = None
        if cache_ttl:
            cache_key = self._generate_cache_key(service, url, params or {})
            cached = await self._get_cached(cache_key)
            if cached:
                logger.debug(f"Cache hit for {service}")
                return {"data": cached, "cached": True}
        
        # Execute through circuit breaker
        circuit = self.get_circuit_breaker(service)
        
        start_time = time.time()
        try:
            if PROMETHEUS_AVAILABLE:
                with API_LATENCY.labels(service=service).time():
                    result = await circuit.call(
                        self._make_request,
                        method, url, params, headers, json_data, timeout
                    )
            else:
                result = await circuit.call(
                    self._make_request,
                    method, url, params, headers, json_data, timeout
                )
            
            if PROMETHEUS_AVAILABLE:
                API_REQUESTS.labels(service=service, endpoint=url).inc()
            
            # Cache successful response
            if cache_key and cache_ttl:
                await self._set_cached(cache_key, result, cache_ttl)
            
            return {"data": result, "cached": False}
            
        except Exception as e:
            if PROMETHEUS_AVAILABLE:
                API_ERRORS.labels(service=service, error_type=type(e).__name__).inc()
            raise
    
    async def _make_request(
        self,
        method: str,
        url: str,
        params: Dict = None,
        headers: Dict = None,
        json_data: Dict = None,
        timeout: int = 30
    ) -> Any:
        """Execute HTTP request"""
        async with self.session.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json=json_data,
            timeout=ClientTimeout(total=timeout)
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    def get_health(self) -> Dict[str, Any]:
        """Get gateway health status"""
        return {
            "circuit_breakers": {
                name: cb.state.value
                for name, cb in self.circuit_breakers.items()
            },
            "cache_size": len(self.cache),
            "redis_connected": self.redis is not None
        }


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open"""
    pass


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    pass


# Convenience functions for common operations
async def fetch_with_retry(
    url: str,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    **kwargs
) -> Dict:
    """
    Fetch URL with exponential backoff retry
    
    Args:
        url: URL to fetch
        max_retries: Maximum retry attempts
        backoff_factor: Backoff multiplier
        **kwargs: Additional aiohttp request kwargs
    """
    async with aiohttp.ClientSession() as session:
        for attempt in range(max_retries):
            try:
                async with session.get(url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = backoff_factor * (2 ** attempt)
                logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)


async def batch_requests(
    urls: List[str],
    max_concurrent: int = 10,
    **kwargs
) -> List[Dict]:
    """
    Execute multiple requests with concurrency limiting
    
    Args:
        urls: List of URLs to fetch
        max_concurrent: Maximum concurrent requests
        **kwargs: Additional request kwargs
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_one(url):
        async with semaphore:
            return await fetch_with_retry(url, **kwargs)
    
    tasks = [fetch_one(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [
        result if not isinstance(result, Exception) else {"error": str(result)}
        for result in results
    ]


if __name__ == "__main__":
    # Example usage
    async def test_gateway():
        async with APIGateway() as gateway:
            # Test NOAA API
            result = await gateway.request(
                service="noaa",
                method="GET",
                url="https://api.weather.gov/alerts/active",
                params={"area": "MO"},
                cache_ttl=60,
                rate_limit_key="noaa"
            )
            print(f"Alerts cached: {result['cached']}")
            print(f"Number of alerts: {len(result['data'].get('features', []))}")
            
            # Check health
            print(f"Gateway health: {gateway.get_health()}")
    
    asyncio.run(test_gateway())
