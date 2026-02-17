# ResilienceAI SDK Development Guide

## Executive Summary

This document provides a comprehensive guide for developing client SDKs for the ResilienceAI platform. The SDKs enable developers to integrate ResilienceAI's AI-powered climate risk analytics, ESG scoring, and sustainability intelligence into their applications with minimal effort.

**Target Languages:** Python, JavaScript/TypeScript  
**Current Version:** 1.0.0  
**API Version:** v1  
**Base URL:** `https://api.resilienceai.io/v1`

---

## Table of Contents

1. [SDK Architecture](#1-sdk-architecture)
2. [Python SDK](#2-python-sdk)
3. [JavaScript/TypeScript SDK](#3-javascripttypescript-sdk)
4. [Authentication](#4-authentication)
5. [Request/Response Models](#5-requestresponse-models)
6. [Error Handling](#6-error-handling)
7. [Retry Logic & Rate Limiting](#7-retry-logic--rate-limiting)
8. [Async Support](#8-async-support)
9. [Testing Strategy](#9-testing-strategy)
10. [Documentation](#10-documentation)
11. [Package Management](#11-package-management)
12. [Integration Guide](#12-integration-guide)
13. [Implementation Priority](#13-implementation-priority)

---

## 1. SDK Architecture

### 1.1 Core Design Principles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ResilienceAI SDK Architecture                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   Client Layer  │    │   Client Layer  │    │   Client Layer  │          │
│  │     (Python)    │    │   (TypeScript)  │    │    (Future)     │          │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘          │
│           │                      │                      │                   │
│           └──────────────────────┼──────────────────────┘                   │
│                                  │                                           │
│  ┌───────────────────────────────┴───────────────────────────────┐          │
│  │                    Common Interface Layer                      │          │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │          │
│  │  │   Auth      │  │   Retry     │  │   Rate      │            │          │
│  │  │  Handler    │  │   Logic     │  │   Limiter   │            │          │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │          │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │          │
│  │  │   Error     │  │   Request   │  │  Response   │            │          │
│  │  │  Handler    │  │   Builder   │  │   Parser    │            │          │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │          │
│  └───────────────────────────────┬───────────────────────────────┘          │
│                                  │                                           │
│  ┌───────────────────────────────┴───────────────────────────────┐          │
│  │                      Transport Layer                           │          │
│  │         (HTTP/HTTPS with Connection Pooling)                   │          │
│  └───────────────────────────────┬───────────────────────────────┘          │
│                                  │                                           │
│                    ┌─────────────┴─────────────┐                             │
│                    │     ResilienceAI API      │                             │
│                    │      (REST + GraphQL)     │                             │
│                    └───────────────────────────┘                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Structure

```
resilienceai-sdk/
├── python/
│   ├── resilienceai/
│   │   ├── __init__.py
│   │   ├── client.py           # Main client
│   │   ├── auth.py             # Authentication
│   │   ├── models.py           # Data models
│   │   ├── exceptions.py       # Error classes
│   │   ├── retry.py            # Retry logic
│   │   ├── rate_limiter.py     # Rate limiting
│   │   ├── resources/          # API resources
│   │   │   ├── __init__.py
│   │   │   ├── climate_risk.py
│   │   │   ├── esg.py
│   │   │   ├── supply_chain.py
│   │   │   ├── reports.py
│   │   │   └── portfolio.py
│   │   ├── utils.py            # Utilities
│   │   └── version.py          # Version info
│   ├── tests/
│   ├── docs/
│   ├── setup.py
│   ├── pyproject.toml
│   └── README.md
│
├── typescript/
│   ├── src/
│   │   ├── index.ts
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── models.ts
│   │   ├── errors.ts
│   │   ├── retry.ts
│   │   ├── rate-limiter.ts
│   │   ├── resources/
│   │   │   ├── index.ts
│   │   │   ├── climate-risk.ts
│   │   │   ├── esg.ts
│   │   │   ├── supply-chain.ts
│   │   │   ├── reports.ts
│   │   │   └── portfolio.ts
│   │   └── utils.ts
│   ├── tests/
│   ├── docs/
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
└── shared/
    ├── openapi.yaml            # OpenAPI specification
    └── schemas/
```

---

## 2. Python SDK

### 2.1 Project Structure

```
resilienceai/
├── __init__.py
├── client.py
├── auth.py
├── models.py
├── exceptions.py
├── retry.py
├── rate_limiter.py
├── resources/
│   ├── __init__.py
│   ├── base.py
│   ├── climate_risk.py
│   ├── esg.py
│   ├── supply_chain.py
│   ├── reports.py
│   └── portfolio.py
├── utils.py
└── version.py
```

### 2.2 Core Client Implementation

**File: `/resilienceai/client.py`**

```python
"""
ResilienceAI Python SDK - Main Client
"""

import os
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import httpx
from httpx import Timeout

from .auth import APIKeyAuth, OAuth2Auth, AuthProvider
from .exceptions import (
    ResilienceAIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ServerError,
)
from .retry import RetryConfig, RetryHandler
from .rate_limiter import RateLimiter
from .resources.climate_risk import ClimateRiskResource
from .resources.esg import ESGResource
from .resources.supply_chain import SupplyChainResource
from .resources.reports import ReportsResource
from .resources.portfolio import PortfolioResource
from .version import __version__


class ResilienceAIClient:
    """
    Main client for interacting with the ResilienceAI API.
    
    Args:
        api_key: Your ResilienceAI API key
        base_url: API base URL (default: https://api.resilienceai.io/v1)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retries (default: 3)
        retry_delay: Initial retry delay in seconds (default: 1)
        rate_limit: Requests per second (default: 10)
        async_mode: Use async client (default: False)
    
    Example:
        >>> from resilienceai import ResilienceAIClient
        >>> client = ResilienceAIClient(api_key="your-api-key")
        >>> risk = client.climate_risk.assess(location="New York, NY")
    """
    
    DEFAULT_BASE_URL = "https://api.resilienceai.io/v1"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0
    DEFAULT_RATE_LIMIT = 10
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        rate_limit: Optional[int] = None,
        async_mode: bool = False,
        auth_provider: Optional[AuthProvider] = None,
    ):
        # API Key resolution
        self.api_key = api_key or os.getenv("RESILIENCEAI_API_KEY")
        if not self.api_key and not auth_provider:
            raise AuthenticationError(
                "API key is required. Provide it as an argument or set RESILIENCEAI_API_KEY environment variable."
            )
        
        # Configuration
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.async_mode = async_mode
        
        # Authentication
        self.auth = auth_provider or APIKeyAuth(self.api_key)
        
        # Retry configuration
        self.retry_config = RetryConfig(
            max_retries=max_retries or self.DEFAULT_MAX_RETRIES,
            initial_delay=retry_delay or self.DEFAULT_RETRY_DELAY,
        )
        self.retry_handler = RetryHandler(self.retry_config)
        
        # Rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_second=rate_limit or self.DEFAULT_RATE_LIMIT
        )
        
        # HTTP client
        self._client: Optional[Union[httpx.Client, httpx.AsyncClient]] = None
        
        # Resource handlers
        self._climate_risk: Optional[ClimateRiskResource] = None
        self._esg: Optional[ESGResource] = None
        self._supply_chain: Optional[SupplyChainResource] = None
        self._reports: Optional[ReportsResource] = None
        self._portfolio: Optional[PortfolioResource] = None
    
    def _get_client(self) -> Union[httpx.Client, httpx.AsyncClient]:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {
                "User-Agent": f"ResilienceAI-Python/{__version__}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            
            timeout = Timeout(self.timeout, connect=5.0)
            
            if self.async_mode:
                self._client = httpx.AsyncClient(
                    base_url=self.base_url,
                    headers=headers,
                    timeout=timeout,
                )
            else:
                self._client = httpx.Client(
                    base_url=self.base_url,
                    headers=headers,
                    timeout=timeout,
                )
        
        return self._client
    
    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Make HTTP request with retry and rate limiting."""
        client = self._get_client()
        url = urljoin(self.base_url, path)
        
        # Apply authentication
        headers = kwargs.pop("headers", {})
        headers.update(self.auth.get_headers())
        
        # Rate limiting
        self.rate_limiter.acquire()
        
        def _do_request():
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            return self._handle_response(response)
        
        return self.retry_handler.execute(_do_request)
    
    async def _arequest(
        self,
        method: str,
        path: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Make async HTTP request with retry and rate limiting."""
        client = self._get_client()
        url = urljoin(self.base_url, path)
        
        headers = kwargs.pop("headers", {})
        headers.update(self.auth.get_headers())
        
        await self.rate_limiter.aacquire()
        
        async def _do_request():
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            return self._handle_response(response)
        
        return await self.retry_handler.aexecute(_do_request)
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate errors."""
        try:
            data = response.json()
        except Exception:
            data = {"message": response.text}
        
        if response.status_code == 200:
            return data
        elif response.status_code == 204:
            return {}
        elif response.status_code == 400:
            raise ValidationError(
                message=data.get("message", "Bad request"),
                details=data.get("details"),
                response=response,
            )
        elif response.status_code == 401:
            raise AuthenticationError(
                message=data.get("message", "Authentication failed"),
                response=response,
            )
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                message=data.get("message", "Rate limit exceeded"),
                retry_after=retry_after,
                response=response,
            )
        elif response.status_code >= 500:
            raise ServerError(
                message=data.get("message", "Server error"),
                status_code=response.status_code,
                response=response,
            )
        else:
            raise ResilienceAIError(
                message=data.get("message", f"HTTP {response.status_code}"),
                status_code=response.status_code,
                response=response,
            )
    
    def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make GET request."""
        return self._request("GET", path, **kwargs)
    
    def post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make POST request."""
        return self._request("POST", path, **kwargs)
    
    def put(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make PUT request."""
        return self._request("PUT", path, **kwargs)
    
    def patch(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make PATCH request."""
        return self._request("PATCH", path, **kwargs)
    
    def delete(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._request("DELETE", path, **kwargs)
    
    async def aget(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make async GET request."""
        return await self._arequest("GET", path, **kwargs)
    
    async def apost(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make async POST request."""
        return await self._arequest("POST", path, **kwargs)
    
    async def aput(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make async PUT request."""
        return await self._arequest("PUT", path, **kwargs)
    
    async def apatch(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make async PATCH request."""
        return await self._arequest("PATCH", path, **kwargs)
    
    async def adelete(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Make async DELETE request."""
        return await self._arequest("DELETE", path, **kwargs)
    
    # Resource accessors
    @property
    def climate_risk(self) -> ClimateRiskResource:
        """Access climate risk API."""
        if self._climate_risk is None:
            self._climate_risk = ClimateRiskResource(self)
        return self._climate_risk
    
    @property
    def esg(self) -> ESGResource:
        """Access ESG API."""
        if self._esg is None:
            self._esg = ESGResource(self)
        return self._esg
    
    @property
    def supply_chain(self) -> SupplyChainResource:
        """Access supply chain API."""
        if self._supply_chain is None:
            self._supply_chain = SupplyChainResource(self)
        return self._supply_chain
    
    @property
    def reports(self) -> ReportsResource:
        """Access reports API."""
        if self._reports is None:
            self._reports = ReportsResource(self)
        return self._reports
    
    @property
    def portfolio(self) -> PortfolioResource:
        """Access portfolio API."""
        if self._portfolio is None:
            self._portfolio = PortfolioResource(self)
        return self._portfolio
    
    def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None
    
    async def aclose(self) -> None:
        """Close async HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()
```

### 2.3 Authentication Module

**File: `/resilienceai/auth.py`**

```python
"""
Authentication providers for ResilienceAI SDK.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime, timedelta
import hashlib
import hmac
import base64


class AuthProvider(ABC):
    """Abstract base class for authentication providers."""
    
    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Return authentication headers."""
        pass


class APIKeyAuth(AuthProvider):
    """API Key authentication."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}


class OAuth2Auth(AuthProvider):
    """OAuth2 authentication with token refresh."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str = "https://auth.resilienceai.io/oauth/token",
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires_at = expires_at
    
    @property
    def access_token(self) -> str:
        """Get valid access token, refreshing if necessary."""
        if self._is_token_expired():
            self._refresh_access_token()
        return self._access_token
    
    def _is_token_expired(self) -> bool:
        """Check if token is expired."""
        if self._expires_at is None:
            return True
        return datetime.utcnow() >= self._expires_at - timedelta(minutes=5)
    
    def _refresh_access_token(self) -> None:
        """Refresh OAuth2 access token."""
        import httpx
        
        response = httpx.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        response.raise_for_status()
        
        data = response.json()
        self._access_token = data["access_token"]
        self._refresh_token = data.get("refresh_token")
        expires_in = data.get("expires_in", 3600)
        self._expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    def get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}


class HMACAuth(AuthProvider):
    """HMAC request signing authentication."""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
    
    def sign_request(
        self,
        method: str,
        path: str,
        timestamp: str,
        body: Optional[str] = None,
    ) -> str:
        """Generate HMAC signature."""
        message = f"{method.upper()}|{path}|{timestamp}"
        if body:
            message += f"|{body}"
        
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        
        return signature
    
    def get_headers(self) -> Dict[str, str]:
        import time
        timestamp = str(int(time.time()))
        return {
            "X-API-Key": self.api_key,
            "X-Timestamp": timestamp,
        }
```

### 2.4 Exception Classes

**File: `/resilienceai/exceptions.py`**

```python
"""
Exception classes for ResilienceAI SDK.
"""

from typing import Optional, Dict, Any


class ResilienceAIError(Exception):
    """Base exception for ResilienceAI SDK."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(ResilienceAIError):
    """Raised when authentication fails."""
    pass


class RateLimitError(ResilienceAIError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        retry_after: int,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ValidationError(ResilienceAIError):
    """Raised when request validation fails."""
    pass


class ServerError(ResilienceAIError):
    """Raised when server returns 5xx error."""
    pass


class ResourceNotFoundError(ResilienceAIError):
    """Raised when requested resource is not found."""
    pass


class ConflictError(ResilienceAIError):
    """Raised when there's a resource conflict."""
    pass


class TimeoutError(ResilienceAIError):
    """Raised when request times out."""
    pass
```

### 2.5 Retry Logic

**File: `/resilienceai/retry.py`**

```python
"""
Retry logic for ResilienceAI SDK.
"""

import time
import random
import asyncio
from typing import Callable, TypeVar, Optional
from dataclasses import dataclass

from .exceptions import ResilienceAIError, RateLimitError, ServerError, TimeoutError

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    retryable_status_codes: tuple = (429, 500, 502, 503, 504)
    retryable_exceptions: tuple = (
        RateLimitError,
        ServerError,
        TimeoutError,
        ConnectionError,
    )
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt with jitter."""
        delay = self.initial_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        # Add jitter (±25%)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        return delay + jitter


class RetryHandler:
    """Handle retry logic for API requests."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
    
    def execute(self, func: Callable[[], T]) -> T:
        """Execute function with retry logic."""
        last_exception: Optional[Exception] = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return func()
            except ResilienceAIError as e:
                last_exception = e
                
                # Don't retry on certain errors
                if isinstance(e, (RateLimitError,)):
                    if attempt < self.config.max_retries:
                        delay = e.retry_after
                        time.sleep(delay)
                        continue
                
                # Check if error is retryable
                if not self._is_retryable(e):
                    raise
                
                if attempt < self.config.max_retries:
                    delay = self.config.get_delay(attempt)
                    time.sleep(delay)
                    continue
                
                raise
        
        raise last_exception or ResilienceAIError("Max retries exceeded")
    
    async def aexecute(self, func: Callable[[], T]) -> T:
        """Execute async function with retry logic."""
        last_exception: Optional[Exception] = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return await func()
            except ResilienceAIError as e:
                last_exception = e
                
                if isinstance(e, (RateLimitError,)):
                    if attempt < self.config.max_retries:
                        delay = e.retry_after
                        await asyncio.sleep(delay)
                        continue
                
                if not self._is_retryable(e):
                    raise
                
                if attempt < self.config.max_retries:
                    delay = self.config.get_delay(attempt)
                    await asyncio.sleep(delay)
                    continue
                
                raise
        
        raise last_exception or ResilienceAIError("Max retries exceeded")
    
    def _is_retryable(self, error: ResilienceAIError) -> bool:
        """Check if error should be retried."""
        if isinstance(error, self.config.retryable_exceptions):
            return True
        if error.status_code in self.config.retryable_status_codes:
            return True
        return False
```

### 2.6 Rate Limiter

**File: `/resilienceai/rate_limiter.py`**

```python
"""
Rate limiting for ResilienceAI SDK.
"""

import time
import asyncio
from typing import Optional
from collections import deque
from threading import Lock


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst_size: Optional[int] = None,
    ):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size or int(requests_per_second * 2)
        self.tokens = float(self.burst_size)
        self.last_update = time.time()
        self.lock = Lock()
        
        # Async support
        self._async_lock = asyncio.Lock()
    
    def acquire(self) -> None:
        """Acquire a token, blocking if necessary."""
        with self.lock:
            self._add_tokens()
            
            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            # Calculate wait time
            wait_time = (1 - self.tokens) / self.requests_per_second
        
        time.sleep(wait_time)
        self.acquire()
    
    async def aacquire(self) -> None:
        """Acquire a token asynchronously."""
        async with self._async_lock:
            self._add_tokens()
            
            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            wait_time = (1 - self.tokens) / self.requests_per_second
        
        await asyncio.sleep(wait_time)
        await self.aacquire()
    
    def _add_tokens(self) -> None:
        """Add tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.burst_size,
            self.tokens + elapsed * self.requests_per_second
        )
        self.last_update = now
    
    def try_acquire(self) -> bool:
        """Try to acquire a token without blocking."""
        with self.lock:
            self._add_tokens()
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


class AdaptiveRateLimiter(RateLimiter):
    """Rate limiter that adapts based on API responses."""
    
    def __init__(
        self,
        initial_rps: float = 10.0,
        min_rps: float = 1.0,
        max_rps: float = 100.0,
    ):
        super().__init__(initial_rps)
        self.min_rps = min_rps
        self.max_rps = max_rps
        self.success_count = 0
        self.failure_count = 0
    
    def report_success(self) -> None:
        """Report successful request."""
        self.success_count += 1
        if self.success_count >= 10:
            self._increase_rate()
            self.success_count = 0
    
    def report_rate_limit(self) -> None:
        """Report rate limit hit."""
        self.failure_count += 1
        self._decrease_rate()
    
    def _increase_rate(self) -> None:
        """Increase request rate."""
        with self.lock:
            self.requests_per_second = min(
                self.max_rps,
                self.requests_per_second * 1.1
            )
    
    def _decrease_rate(self) -> None:
        """Decrease request rate."""
        with self.lock:
            self.requests_per_second = max(
                self.min_rps,
                self.requests_per_second * 0.7
            )
```

### 2.7 Data Models

**File: `/resilienceai/models.py`**

```python
"""
Data models for ResilienceAI SDK.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HazardType(str, Enum):
    """Climate hazard types."""
    FLOOD = "flood"
    WILDFIRE = "wildfire"
    HURRICANE = "hurricane"
    DROUGHT = "drought"
    HEAT_WAVE = "heat_wave"
    SEA_LEVEL_RISE = "sea_level_rise"
    STORM_SURGE = "storm_surge"
    EARTHQUAKE = "earthquake"


@dataclass
class Location:
    """Geographic location."""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in {
                "address": self.address,
                "city": self.city,
                "state": self.state,
                "country": self.country,
                "postal_code": self.postal_code,
                "latitude": self.latitude,
                "longitude": self.longitude,
            }.items() if v is not None
        }


@dataclass
class ClimateRiskScore:
    """Climate risk score for a location."""
    hazard_type: HazardType
    risk_level: RiskLevel
    score: float  # 0-100
    probability: float  # 0-1
    annual_loss_estimate: Optional[float] = None
    confidence: float = 0.0
    timeframe: str = "current"  # current, 2030, 2050, 2100
    scenario: str = "rcp4.5"  # rcp2.6, rcp4.5, rcp8.5
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClimateRiskScore":
        return cls(
            hazard_type=HazardType(data["hazard_type"]),
            risk_level=RiskLevel(data["risk_level"]),
            score=data["score"],
            probability=data["probability"],
            annual_loss_estimate=data.get("annual_loss_estimate"),
            confidence=data.get("confidence", 0.0),
            timeframe=data.get("timeframe", "current"),
            scenario=data.get("scenario", "rcp4.5"),
        )


@dataclass
class ClimateRiskAssessment:
    """Complete climate risk assessment."""
    id: str
    location: Location
    overall_risk_level: RiskLevel
    overall_score: float
    risks: List[ClimateRiskScore] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClimateRiskAssessment":
        return cls(
            id=data["id"],
            location=Location(**data.get("location", {})),
            overall_risk_level=RiskLevel(data["overall_risk_level"]),
            overall_score=data["overall_score"],
            risks=[ClimateRiskScore.from_dict(r) for r in data.get("risks", [])],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
        )


@dataclass
class ESGScore:
    """ESG score for a company."""
    environmental_score: float  # 0-100
    social_score: float  # 0-100
    governance_score: float  # 0-100
    overall_score: float  # 0-100
    carbon_intensity: Optional[float] = None
    water_usage: Optional[float] = None
    renewable_energy_pct: Optional[float] = None
    data_quality: str = "medium"  # low, medium, high
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ESGScore":
        return cls(**data)


@dataclass
class Company:
    """Company information."""
    id: str
    name: str
    ticker: Optional[str] = None
    isin: Optional[str] = None
    cusip: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    market_cap: Optional[float] = None
    esg_score: Optional[ESGScore] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Company":
        esg_data = data.get("esg_score")
        return cls(
            id=data["id"],
            name=data["name"],
            ticker=data.get("ticker"),
            isin=data.get("isin"),
            cusip=data.get("cusip"),
            sector=data.get("sector"),
            industry=data.get("industry"),
            country=data.get("country"),
            market_cap=data.get("market_cap"),
            esg_score=ESGScore.from_dict(esg_data) if esg_data else None,
        )


@dataclass
class SupplyChainNode:
    """Supply chain node."""
    id: str
    company: Company
    tier: int
    location: Location
    risk_exposure: RiskLevel
    criticality: str = "medium"  # low, medium, high
    alternatives: List[str] = field(default_factory=list)


@dataclass
class SupplyChain:
    """Supply chain analysis."""
    id: str
    company_id: str
    nodes: List[SupplyChainNode] = field(default_factory=list)
    geographic_concentration: Dict[str, float] = field(default_factory=dict)
    risk_hotspots: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Report:
    """Generated report."""
    id: str
    type: str
    title: str
    status: str  # pending, processing, completed, failed
    download_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Portfolio:
    """Portfolio for analysis."""
    id: str
    name: str
    description: Optional[str] = None
    holdings: List[Dict[str, Any]] = field(default_factory=list)
    total_value: Optional[float] = None
    risk_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
```

### 2.8 Resource Implementations

**File: `/resilienceai/resources/climate_risk.py`**

```python
"""
Climate Risk API resource.
"""

from typing import Optional, List, Dict, Any, Union

from ..models import (
    Location,
    ClimateRiskAssessment,
    ClimateRiskScore,
    HazardType,
    RiskLevel,
)


class ClimateRiskResource:
    """Climate risk assessment resource."""
    
    def __init__(self, client):
        self._client = client
    
    def assess(
        self,
        location: Union[str, Location],
        hazards: Optional[List[HazardType]] = None,
        timeframe: str = "current",
        scenario: str = "rcp4.5",
    ) -> ClimateRiskAssessment:
        """
        Assess climate risks for a location.
        
        Args:
            location: Address string or Location object
            hazards: List of hazards to assess (default: all)
            timeframe: Time horizon (current, 2030, 2050, 2100)
            scenario: Climate scenario (rcp2.6, rcp4.5, rcp8.5)
        
        Returns:
            ClimateRiskAssessment object
        
        Example:
            >>> assessment = client.climate_risk.assess("Miami, FL")
            >>> print(assessment.overall_risk_level)
        """
        if isinstance(location, str):
            location = Location(address=location)
        
        data = {
            "location": location.to_dict(),
            "timeframe": timeframe,
            "scenario": scenario,
        }
        
        if hazards:
            data["hazards"] = [h.value for h in hazards]
        
        response = self._client.post("/climate-risk/assess", json=data)
        return ClimateRiskAssessment.from_dict(response)
    
    async def aassess(
        self,
        location: Union[str, Location],
        hazards: Optional[List[HazardType]] = None,
        timeframe: str = "current",
        scenario: str = "rcp4.5",
    ) -> ClimateRiskAssessment:
        """Async version of assess()."""
        if isinstance(location, str):
            location = Location(address=location)
        
        data = {
            "location": location.to_dict(),
            "timeframe": timeframe,
            "scenario": scenario,
        }
        
        if hazards:
            data["hazards"] = [h.value for h in hazards]
        
        response = await self._client.apost("/climate-risk/assess", json=data)
        return ClimateRiskAssessment.from_dict(response)
    
    def batch_assess(
        self,
        locations: List[Union[str, Location]],
        **kwargs: Any
    ) -> List[ClimateRiskAssessment]:
        """
        Assess climate risks for multiple locations.
        
        Args:
            locations: List of addresses or Location objects
            **kwargs: Additional parameters passed to assess()
        
        Returns:
            List of ClimateRiskAssessment objects
        """
        return [self.assess(loc, **kwargs) for loc in locations]
    
    def get_score(
        self,
        location: Union[str, Location],
        hazard: HazardType,
    ) -> ClimateRiskScore:
        """
        Get specific hazard risk score.
        
        Args:
            location: Address or Location object
            hazard: Hazard type
        
        Returns:
            ClimateRiskScore for the hazard
        """
        if isinstance(location, str):
            location = Location(address=location)
        
        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "hazard": hazard.value,
        }
        
        response = self._client.get("/climate-risk/score", params=params)
        return ClimateRiskScore.from_dict(response)
    
    def get_historical_events(
        self,
        location: Union[str, Location],
        hazard: Optional[HazardType] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get historical climate events for a location.
        
        Args:
            location: Address or Location object
            hazard: Filter by hazard type
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
        
        Returns:
            List of historical events
        """
        if isinstance(location, str):
            location = Location(address=location)
        
        params = location.to_dict()
        if hazard:
            params["hazard"] = hazard.value
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return self._client.get("/climate-risk/historical", params=params)
```

**File: `/resilienceai/resources/esg.py`**

```python
"""
ESG API resource.
"""

from typing import Optional, List, Dict, Any

from ..models import Company, ESGScore


class ESGResource:
    """ESG scoring and analysis resource."""
    
    def __init__(self, client):
        self._client = client
    
    def get_company(
        self,
        identifier: str,
        id_type: str = "ticker",
    ) -> Company:
        """
        Get company ESG data.
        
        Args:
            identifier: Company identifier
            id_type: Type of identifier (ticker, isin, cusip, name)
        
        Returns:
            Company object with ESG data
        """
        params = {"id_type": id_type}
        response = self._client.get(f"/esg/companies/{identifier}", params=params)
        return Company.from_dict(response)
    
    def search_companies(
        self,
        query: str,
        sector: Optional[str] = None,
        limit: int = 10,
    ) -> List[Company]:
        """
        Search for companies by name or ticker.
        
        Args:
            query: Search query
            sector: Filter by sector
            limit: Maximum results
        
        Returns:
            List of Company objects
        """
        params = {"q": query, "limit": limit}
        if sector:
            params["sector"] = sector
        
        response = self._client.get("/esg/companies/search", params=params)
        return [Company.from_dict(c) for c in response.get("results", [])]
    
    def get_score(
        self,
        identifier: str,
        id_type: str = "ticker",
    ) -> ESGScore:
        """
        Get ESG score for a company.
        
        Args:
            identifier: Company identifier
            id_type: Type of identifier
        
        Returns:
            ESGScore object
        """
        params = {"id_type": id_type}
        response = self._client.get(f"/esg/scores/{identifier}", params=params)
        return ESGScore.from_dict(response)
    
    def compare(
        self,
        identifiers: List[str],
        id_type: str = "ticker",
    ) -> Dict[str, Any]:
        """
        Compare ESG scores across multiple companies.
        
        Args:
            identifiers: List of company identifiers
            id_type: Type of identifiers
        
        Returns:
            Comparison data
        """
        data = {
            "identifiers": identifiers,
            "id_type": id_type,
        }
        return self._client.post("/esg/compare", json=data)
    
    def get_sector_benchmarks(
        self,
        sector: str,
    ) -> Dict[str, Any]:
        """
        Get ESG benchmarks for a sector.
        
        Args:
            sector: Industry sector
        
        Returns:
            Benchmark data
        """
        return self._client.get(f"/esg/benchmarks/{sector}")
    
    async def aget_company(self, *args, **kwargs) -> Company:
        """Async version of get_company()."""
        params = {"id_type": kwargs.get("id_type", "ticker")}
        response = await self._client.aget(f"/esg/companies/{args[0]}", params=params)
        return Company.from_dict(response)
```

---

## 3. JavaScript/TypeScript SDK

### 3.1 Project Structure

```
src/
├── index.ts
├── client.ts
├── auth.ts
├── models.ts
├── errors.ts
├── retry.ts
├── rate-limiter.ts
├── resources/
│   ├── index.ts
│   ├── base.ts
│   ├── climate-risk.ts
│   ├── esg.ts
│   ├── supply-chain.ts
│   ├── reports.ts
│   └── portfolio.ts
└── utils.ts
```

### 3.2 Core Client Implementation

**File: `/src/client.ts`**

```typescript
/**
 * ResilienceAI TypeScript SDK - Main Client
 */

import {
  AuthProvider,
  APIKeyAuth,
  OAuth2Auth,
} from './auth';
import {
  ResilienceAIError,
  AuthenticationError,
  RateLimitError,
  ValidationError,
  ServerError,
} from './errors';
import { RetryConfig, RetryHandler } from './retry';
import { RateLimiter } from './rate-limiter';
import { ClimateRiskResource } from './resources/climate-risk';
import { ESGResource } from './resources/esg';
import { SupplyChainResource } from './resources/supply-chain';
import { ReportsResource } from './resources/reports';
import { PortfolioResource } from './resources/portfolio';
import { VERSION } from './version';

export interface ClientConfig {
  apiKey?: string;
  baseUrl?: string;
  timeout?: number;
  maxRetries?: number;
  retryDelay?: number;
  rateLimit?: number;
  authProvider?: AuthProvider;
}

export class ResilienceAIClient {
  private static readonly DEFAULT_BASE_URL = 'https://api.resilienceai.io/v1';
  private static readonly DEFAULT_TIMEOUT = 30000;
  private static readonly DEFAULT_MAX_RETRIES = 3;
  private static readonly DEFAULT_RETRY_DELAY = 1000;
  private static readonly DEFAULT_RATE_LIMIT = 10;

  private readonly apiKey?: string;
  private readonly baseUrl: string;
  private readonly timeout: number;
  private readonly auth: AuthProvider;
  private readonly retryHandler: RetryHandler;
  private readonly rateLimiter: RateLimiter;

  private _climateRisk?: ClimateRiskResource;
  private _esg?: ESGResource;
  private _supplyChain?: SupplyChainResource;
  private _reports?: ReportsResource;
  private _portfolio?: PortfolioResource;

  constructor(config: ClientConfig = {}) {
    // API Key resolution
    this.apiKey = config.apiKey || process.env.RESILIENCEAI_API_KEY;
    
    if (!this.apiKey && !config.authProvider) {
      throw new AuthenticationError(
        'API key is required. Provide it as an argument or set RESILIENCEAI_API_KEY environment variable.'
      );
    }

    // Configuration
    this.baseUrl = config.baseUrl || ResilienceAIClient.DEFAULT_BASE_URL;
    this.timeout = config.timeout || ResilienceAIClient.DEFAULT_TIMEOUT;

    // Authentication
    this.auth = config.authProvider || new APIKeyAuth(this.apiKey!);

    // Retry configuration
    const retryConfig: RetryConfig = {
      maxRetries: config.maxRetries || ResilienceAIClient.DEFAULT_MAX_RETRIES,
      initialDelay: config.retryDelay || ResilienceAIClient.DEFAULT_RETRY_DELAY,
    };
    this.retryHandler = new RetryHandler(retryConfig);

    // Rate limiter
    this.rateLimiter = new RateLimiter(
      config.rateLimit || ResilienceAIClient.DEFAULT_RATE_LIMIT
    );
  }

  /**
   * Make HTTP request with retry and rate limiting
   */
  private async request<T>(
    method: string,
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    
    // Apply authentication
    const headers: Record<string, string> = {
      'User-Agent': `ResilienceAI-Node/${VERSION}`,
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      ...this.auth.getHeaders(),
      ...(options.headers as Record<string, string> || {}),
    };

    // Rate limiting
    await this.rateLimiter.acquire();

    return this.retryHandler.execute(async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      try {
        const response = await fetch(url, {
          ...options,
          method,
          headers,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        return await this.handleResponse<T>(response);
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof ResilienceAIError) {
          throw error;
        }
        throw new ResilienceAIError(
          error instanceof Error ? error.message : 'Request failed'
        );
      }
    });
  }

  /**
   * Handle API response
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    let data: any;
    
    try {
      data = await response.json();
    } catch {
      data = { message: await response.text() };
    }

    if (response.status === 200 || response.status === 201) {
      return data as T;
    }
    
    if (response.status === 204) {
      return {} as T;
    }

    if (response.status === 400) {
      throw new ValidationError(
        data.message || 'Bad request',
        data.details,
        response.status
      );
    }

    if (response.status === 401) {
      throw new AuthenticationError(
        data.message || 'Authentication failed',
        response.status
      );
    }

    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get('Retry-After') || '60', 10);
      throw new RateLimitError(
        data.message || 'Rate limit exceeded',
        retryAfter,
        response.status
      );
    }

    if (response.status >= 500) {
      throw new ServerError(
        data.message || 'Server error',
        response.status
      );
    }

    throw new ResilienceAIError(
      data.message || `HTTP ${response.status}`,
      response.status
    );
  }

  // HTTP methods
  public async get<T>(path: string, params?: Record<string, string>): Promise<T> {
    const queryString = params ? `?${new URLSearchParams(params)}` : '';
    return this.request<T>('GET', `${path}${queryString}`);
  }

  public async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('POST', path, {
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public async put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PUT', path, {
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public async patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PATCH', path, {
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public async delete<T>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }

  // Resource accessors
  public get climateRisk(): ClimateRiskResource {
    if (!this._climateRisk) {
      this._climateRisk = new ClimateRiskResource(this);
    }
    return this._climateRisk;
  }

  public get esg(): ESGResource {
    if (!this._esg) {
      this._esg = new ESGResource(this);
    }
    return this._esg;
  }

  public get supplyChain(): SupplyChainResource {
    if (!this._supplyChain) {
      this._supplyChain = new SupplyChainResource(this);
    }
    return this._supplyChain;
  }

  public get reports(): ReportsResource {
    if (!this._reports) {
      this._reports = new ReportsResource(this);
    }
    return this._reports;
  }

  public get portfolio(): PortfolioResource {
    if (!this._portfolio) {
      this._portfolio = new PortfolioResource(this);
    }
    return this._portfolio;
  }
}

// Export convenience function
export function createClient(config?: ClientConfig): ResilienceAIClient {
  return new ResilienceAIClient(config);
}
```

### 3.3 Authentication Module

**File: `/src/auth.ts`**

```typescript
/**
 * Authentication providers for ResilienceAI SDK
 */

export interface AuthProvider {
  getHeaders(): Record<string, string>;
}

export class APIKeyAuth implements AuthProvider {
  constructor(private readonly apiKey: string) {}

  getHeaders(): Record<string, string> {
    return { Authorization: `Bearer ${this.apiKey}` };
  }
}

export interface OAuth2Config {
  clientId: string;
  clientSecret: string;
  tokenUrl?: string;
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: Date;
}

export class OAuth2Auth implements AuthProvider {
  private readonly clientId: string;
  private readonly clientSecret: string;
  private readonly tokenUrl: string;
  private accessToken?: string;
  private refreshToken?: string;
  private expiresAt?: Date;

  constructor(config: OAuth2Config) {
    this.clientId = config.clientId;
    this.clientSecret = config.clientSecret;
    this.tokenUrl = config.tokenUrl || 'https://auth.resilienceai.io/oauth/token';
    this.accessToken = config.accessToken;
    this.refreshToken = config.refreshToken;
    this.expiresAt = config.expiresAt;
  }

  private isTokenExpired(): boolean {
    if (!this.expiresAt) return true;
    return new Date() >= new Date(this.expiresAt.getTime() - 5 * 60 * 1000);
  }

  private async refreshAccessToken(): Promise<void> {
    const response = await fetch(this.tokenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: this.clientId,
        client_secret: this.clientSecret,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to refresh access token');
    }

    const data = await response.json();
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    const expiresIn = data.expires_in || 3600;
    this.expiresAt = new Date(Date.now() + expiresIn * 1000);
  }

  async getAccessToken(): Promise<string> {
    if (this.isTokenExpired()) {
      await this.refreshAccessToken();
    }
    return this.accessToken!;
  }

  getHeaders(): Record<string, string> {
    if (!this.accessToken) {
      throw new Error('Access token not available');
    }
    return { Authorization: `Bearer ${this.accessToken}` };
  }
}
```

### 3.4 Error Classes

**File: `/src/errors.ts`**

```typescript
/**
 * Error classes for ResilienceAI SDK
 */

export class ResilienceAIError extends Error {
  public readonly statusCode?: number;
  public readonly details?: Record<string, unknown>;

  constructor(
    message: string,
    statusCode?: number,
    details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ResilienceAIError';
    this.statusCode = statusCode;
    this.details = details;
  }

  toString(): string {
    if (this.statusCode) {
      return `[${this.statusCode}] ${this.message}`;
    }
    return this.message;
  }
}

export class AuthenticationError extends ResilienceAIError {
  constructor(message: string, statusCode?: number) {
    super(message, statusCode);
    this.name = 'AuthenticationError';
  }
}

export class RateLimitError extends ResilienceAIError {
  public readonly retryAfter: number;

  constructor(message: string, retryAfter: number, statusCode?: number) {
    super(message, statusCode);
    this.name = 'RateLimitError';
    this.retryAfter = retryAfter;
  }
}

export class ValidationError extends ResilienceAIError {
  constructor(
    message: string,
    details?: Record<string, unknown>,
    statusCode?: number
  ) {
    super(message, statusCode, details);
    this.name = 'ValidationError';
  }
}

export class ServerError extends ResilienceAIError {
  constructor(message: string, statusCode?: number) {
    super(message, statusCode);
    this.name = 'ServerError';
  }
}

export class ResourceNotFoundError extends ResilienceAIError {
  constructor(message: string, statusCode?: number) {
    super(message, statusCode);
    this.name = 'ResourceNotFoundError';
  }
}

export class TimeoutError extends ResilienceAIError {
  constructor(message: string = 'Request timeout') {
    super(message);
    this.name = 'TimeoutError';
  }
}
```

### 3.5 Retry Logic

**File: `/src/retry.ts`**

```typescript
/**
 * Retry logic for ResilienceAI SDK
 */

import {
  ResilienceAIError,
  RateLimitError,
  ServerError,
  TimeoutError,
} from './errors';

export interface RetryConfig {
  maxRetries?: number;
  initialDelay?: number;
  maxDelay?: number;
  exponentialBase?: number;
  retryableStatusCodes?: number[];
}

const DEFAULT_CONFIG: Required<RetryConfig> = {
  maxRetries: 3,
  initialDelay: 1000,
  maxDelay: 60000,
  exponentialBase: 2,
  retryableStatusCodes: [429, 500, 502, 503, 504],
};

export class RetryHandler {
  private readonly config: Required<RetryConfig>;

  constructor(config: RetryConfig = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  private getDelay(attempt: number): number {
    const delay = this.config.initialDelay * Math.pow(this.config.exponentialBase, attempt);
    const clampedDelay = Math.min(delay, this.config.maxDelay);
    // Add jitter (±25%)
    const jitter = clampedDelay * 0.25 * (2 * Math.random() - 1);
    return clampedDelay + jitter;
  }

  private isRetryable(error: ResilienceAIError): boolean {
    if (error instanceof RateLimitError || error instanceof ServerError || error instanceof TimeoutError) {
      return true;
    }
    if (error.statusCode && this.config.retryableStatusCodes.includes(error.statusCode)) {
      return true;
    }
    return false;
  }

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    let lastError: ResilienceAIError | undefined;

    for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        if (error instanceof ResilienceAIError) {
          lastError = error;

          // Handle rate limit specially
          if (error instanceof RateLimitError && attempt < this.config.maxRetries) {
            await this.sleep(error.retryAfter * 1000);
            continue;
          }

          // Check if error is retryable
          if (!this.isRetryable(error) || attempt >= this.config.maxRetries) {
            throw error;
          }

          // Wait and retry
          const delay = this.getDelay(attempt);
          await this.sleep(delay);
        } else {
          throw error;
        }
      }
    }

    throw lastError || new ResilienceAIError('Max retries exceeded');
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### 3.6 Rate Limiter

**File: `/src/rate-limiter.ts`**

```typescript
/**
 * Rate limiting for ResilienceAI SDK
 */

export class RateLimiter {
  private tokens: number;
  private lastUpdate: number;
  private readonly requestsPerSecond: number;
  private readonly burstSize: number;

  constructor(
    requestsPerSecond: number = 10,
    burstSize?: number
  ) {
    this.requestsPerSecond = requestsPerSecond;
    this.burstSize = burstSize || requestsPerSecond * 2;
    this.tokens = this.burstSize;
    this.lastUpdate = Date.now();
  }

  private addTokens(): void {
    const now = Date.now();
    const elapsed = (now - this.lastUpdate) / 1000;
    this.tokens = Math.min(
      this.burstSize,
      this.tokens + elapsed * this.requestsPerSecond
    );
    this.lastUpdate = now;
  }

  async acquire(): Promise<void> {
    this.addTokens();

    if (this.tokens >= 1) {
      this.tokens -= 1;
      return;
    }

    const waitTime = ((1 - this.tokens) / this.requestsPerSecond) * 1000;
    await this.sleep(waitTime);
    return this.acquire();
  }

  tryAcquire(): boolean {
    this.addTokens();

    if (this.tokens >= 1) {
      this.tokens -= 1;
      return true;
    }
    return false;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export class AdaptiveRateLimiter extends RateLimiter {
  private readonly minRps: number;
  private readonly maxRps: number;
  private currentRps: number;

  constructor(
    initialRps: number = 10,
    minRps: number = 1,
    maxRps: number = 100
  ) {
    super(initialRps);
    this.currentRps = initialRps;
    this.minRps = minRps;
    this.maxRps = maxRps;
  }

  reportSuccess(): void {
    this.currentRps = Math.min(this.maxRps, this.currentRps * 1.1);
  }

  reportRateLimit(): void {
    this.currentRps = Math.max(this.minRps, this.currentRps * 0.7);
  }
}
```

### 3.7 Data Models

**File: `/src/models.ts`**

```typescript
/**
 * Data models for ResilienceAI SDK
 */

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export type HazardType = 
  | 'flood' 
  | 'wildfire' 
  | 'hurricane' 
  | 'drought' 
  | 'heat_wave'
  | 'sea_level_rise'
  | 'storm_surge'
  | 'earthquake';

export interface Location {
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postalCode?: string;
  latitude?: number;
  longitude?: number;
}

export interface ClimateRiskScore {
  hazardType: HazardType;
  riskLevel: RiskLevel;
  score: number;
  probability: number;
  annualLossEstimate?: number;
  confidence: number;
  timeframe: string;
  scenario: string;
}

export interface ClimateRiskAssessment {
  id: string;
  location: Location;
  overallRiskLevel: RiskLevel;
  overallScore: number;
  risks: ClimateRiskScore[];
  createdAt: string;
  expiresAt?: string;
}

export interface ESGScore {
  environmentalScore: number;
  socialScore: number;
  governanceScore: number;
  overallScore: number;
  carbonIntensity?: number;
  waterUsage?: number;
  renewableEnergyPct?: number;
  dataQuality: 'low' | 'medium' | 'high';
}

export interface Company {
  id: string;
  name: string;
  ticker?: string;
  isin?: string;
  cusip?: string;
  sector?: string;
  industry?: string;
  country?: string;
  marketCap?: number;
  esgScore?: ESGScore;
}

export interface SupplyChainNode {
  id: string;
  company: Company;
  tier: number;
  location: Location;
  riskExposure: RiskLevel;
  criticality: 'low' | 'medium' | 'high';
  alternatives: string[];
}

export interface SupplyChain {
  id: string;
  companyId: string;
  nodes: SupplyChainNode[];
  geographicConcentration: Record<string, number>;
  riskHotspots: Record<string, unknown>[];
  createdAt: string;
}

export interface Report {
  id: string;
  type: string;
  title: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  downloadUrl?: string;
  createdAt: string;
  completedAt?: string;
  expiresAt?: string;
  metadata: Record<string, unknown>;
}

export interface Portfolio {
  id: string;
  name: string;
  description?: string;
  holdings: Record<string, unknown>[];
  totalValue?: number;
  riskMetrics: Record<string, unknown>;
  createdAt: string;
  updatedAt?: string;
}
```

### 3.8 Resource Implementation

**File: `/src/resources/climate-risk.ts`**

```typescript
/**
 * Climate Risk API resource
 */

import { ResilienceAIClient } from '../client';
import { Location, ClimateRiskAssessment, HazardType } from '../models';

export interface AssessOptions {
  hazards?: HazardType[];
  timeframe?: 'current' | '2030' | '2050' | '2100';
  scenario?: 'rcp2.6' | 'rcp4.5' | 'rcp8.5';
}

export class ClimateRiskResource {
  constructor(private readonly client: ResilienceAIClient) {}

  /**
   * Assess climate risks for a location
   */
  async assess(
    location: string | Location,
    options: AssessOptions = {}
  ): Promise<ClimateRiskAssessment> {
    const locationData = typeof location === 'string' 
      ? { address: location } 
      : location;

    const data = {
      location: locationData,
      timeframe: options.timeframe || 'current',
      scenario: options.scenario || 'rcp4.5',
      hazards: options.hazards,
    };

    return this.client.post<ClimateRiskAssessment>('/climate-risk/assess', data);
  }

  /**
   * Assess multiple locations
   */
  async batchAssess(
    locations: (string | Location)[],
    options: AssessOptions = {}
  ): Promise<ClimateRiskAssessment[]> {
    return Promise.all(
      locations.map(loc => this.assess(loc, options))
    );
  }

  /**
   * Get historical climate events
   */
  async getHistoricalEvents(
    location: string | Location,
    options: {
      hazard?: HazardType;
      startDate?: string;
      endDate?: string;
    } = {}
  ): Promise<Record<string, unknown>[]> {
    const locationData = typeof location === 'string'
      ? { address: location }
      : location;

    const params: Record<string, string> = {};
    
    if (locationData.latitude !== undefined) {
      params.latitude = String(locationData.latitude);
    }
    if (locationData.longitude !== undefined) {
      params.longitude = String(locationData.longitude);
    }
    if (options.hazard) {
      params.hazard = options.hazard;
    }
    if (options.startDate) {
      params.start_date = options.startDate;
    }
    if (options.endDate) {
      params.end_date = options.endDate;
    }

    return this.client.get<Record<string, unknown>[]>('/climate-risk/historical', params);
  }
}
```

---

## 4. Authentication

### 4.1 Supported Authentication Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| API Key | Simple bearer token | Quick start, single-user apps |
| OAuth2 | Token-based with refresh | Production applications |
| HMAC | Request signing | High-security requirements |

### 4.2 Environment Variables

```bash
# Python
export RESILIENCEAI_API_KEY="your-api-key"
export RESILIENCEAI_BASE_URL="https://api.resilienceai.io/v1"
export RESILIENCEAI_TIMEOUT="30"
export RESILIENCEAI_MAX_RETRIES="3"
export RESILIENCEAI_RATE_LIMIT="10"

# JavaScript/Node.js
export RESILIENCEAI_API_KEY="your-api-key"
export RESILIENCEAI_CLIENT_ID="your-client-id"
export RESILIENCEAI_CLIENT_SECRET="your-client-secret"
```

### 4.3 Authentication Examples

**Python:**
```python
from resilienceai import ResilienceAIClient
from resilienceai.auth import OAuth2Auth

# API Key auth (default)
client = ResilienceAIClient(api_key="your-api-key")

# OAuth2 auth
oauth = OAuth2Auth(
    client_id="your-client-id",
    client_secret="your-client-secret",
)
client = ResilienceAIClient(auth_provider=oauth)

# From environment variable
client = ResilienceAIClient()  # Reads RESILIENCEAI_API_KEY
```

**TypeScript:**
```typescript
import { ResilienceAIClient, OAuth2Auth } from 'resilienceai';

// API Key auth
const client = new ResilienceAIClient({ apiKey: 'your-api-key' });

// OAuth2 auth
const oauth = new OAuth2Auth({
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret',
});
const client = new ResilienceAIClient({ authProvider: oauth });

// From environment variable
const client = new ResilienceAIClient(); // Reads RESILIENCEAI_API_KEY
```

---

## 5. Request/Response Models

### 5.1 Model Validation

**Python (using pydantic):**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class ClimateRiskRequest(BaseModel):
    location: Location
    hazards: Optional[list[HazardType]] = None
    timeframe: str = Field(default="current", regex="^(current|2030|2050|2100)$")
    scenario: str = Field(default="rcp4.5", regex="^(rcp2\.6|rcp4\.5|rcp8\.5)$")
    
    @validator('location')
    def validate_location(cls, v):
        if not v.address and not (v.latitude and v.longitude):
            raise ValueError('Location must have address or coordinates')
        return v
```

**TypeScript (using zod):**
```typescript
import { z } from 'zod';

const ClimateRiskRequestSchema = z.object({
  location: LocationSchema,
  hazards: z.array(HazardTypeSchema).optional(),
  timeframe: z.enum(['current', '2030', '2050', '2100']).default('current'),
  scenario: z.enum(['rcp2.6', 'rcp4.5', 'rcp8.5']).default('rcp4.5'),
});

type ClimateRiskRequest = z.infer<typeof ClimateRiskRequestSchema>;
```

### 5.2 Response Parsing

```python
# Python
from resilienceai.models import ClimateRiskAssessment

response = client.post("/climate-risk/assess", json=data)
assessment = ClimateRiskAssessment.from_dict(response)

# Access typed fields
print(assessment.overall_risk_level)  # RiskLevel.HIGH
print(assessment.risks[0].score)      # 85.5
```

```typescript
// TypeScript
const assessment = await client.climateRisk.assess("Miami, FL");

// Type-safe access
console.log(assessment.overallRiskLevel); // "high"
console.log(assessment.risks[0].score);   // 85.5
```

---

## 6. Error Handling

### 6.1 Error Hierarchy

```
ResilienceAIError (base)
├── AuthenticationError (401)
├── RateLimitError (429)
├── ValidationError (400)
├── ResourceNotFoundError (404)
├── ConflictError (409)
├── ServerError (5xx)
└── TimeoutError
```

### 6.2 Error Handling Examples

**Python:**
```python
from resilienceai import ResilienceAIClient
from resilienceai.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ServerError,
)

client = ResilienceAIClient()

try:
    assessment = client.climate_risk.assess("Miami, FL")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
    # Re-authenticate or prompt for credentials
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    time.sleep(e.retry_after)
except ValidationError as e:
    print(f"Invalid request: {e.message}")
    print(f"Details: {e.details}")
except ServerError as e:
    print(f"Server error: {e.message}")
    # Log and retry later
```

**TypeScript:**
```typescript
import {
  ResilienceAIClient,
  AuthenticationError,
  RateLimitError,
  ValidationError,
  ServerError,
} from 'resilienceai';

const client = new ResilienceAIClient();

try {
  const assessment = await client.climateRisk.assess('Miami, FL');
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error(`Auth failed: ${error.message}`);
  } else if (error instanceof RateLimitError) {
    console.error(`Rate limited. Retry after ${error.retryAfter}s`);
    await sleep(error.retryAfter * 1000);
  } else if (error instanceof ValidationError) {
    console.error(`Invalid request: ${error.message}`);
    console.error('Details:', error.details);
  } else if (error instanceof ServerError) {
    console.error(`Server error: ${error.message}`);
  }
}
```

---

## 7. Retry Logic & Rate Limiting

### 7.1 Retry Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| max_retries | 3 | Maximum retry attempts |
| initial_delay | 1s | Initial retry delay |
| max_delay | 60s | Maximum retry delay |
| exponential_base | 2.0 | Exponential backoff multiplier |

### 7.2 Retry Strategy

```
Attempt 1: Request fails → Wait 1.0s ± 25% jitter → Retry
Attempt 2: Request fails → Wait 2.0s ± 25% jitter → Retry
Attempt 3: Request fails → Wait 4.0s ± 25% jitter → Retry
Attempt 4: Request fails → Throw error
```

### 7.3 Rate Limiting

**Token Bucket Algorithm:**
- Burst capacity: 2x requests_per_second
- Refill rate: requests_per_second tokens/second
- Block until token available

**Adaptive Rate Limiting:**
- Increase rate by 10% after 10 consecutive successes
- Decrease rate by 30% after rate limit hit
- Bounds: min_rps to max_rps

---

## 8. Async Support

### 8.1 Python Async

```python
import asyncio
from resilienceai import ResilienceAIClient

async def main():
    client = ResilienceAIClient(async_mode=True)
    
    # Concurrent requests
    assessments = await asyncio.gather(
        client.climate_risk.aassess("Miami, FL"),
        client.climate_risk.aassess("New York, NY"),
        client.climate_risk.aassess("Los Angeles, CA"),
    )
    
    await client.aclose()

asyncio.run(main())
```

### 8.2 TypeScript Async

```typescript
import { ResilienceAIClient } from 'resilienceai';

async function main() {
  const client = new ResilienceAIClient();
  
  // Concurrent requests
  const assessments = await Promise.all([
    client.climateRisk.assess('Miami, FL'),
    client.climateRisk.assess('New York, NY'),
    client.climateRisk.assess('Los Angeles, CA'),
  ]);
  
  console.log(assessments);
}

main().catch(console.error);
```

---

## 9. Testing Strategy

### 9.1 Test Structure

```
tests/
├── unit/
│   ├── test_client.py
│   ├── test_auth.py
│   ├── test_retry.py
│   ├── test_rate_limiter.py
│   └── resources/
│       ├── test_climate_risk.py
│       ├── test_esg.py
│       └── test_supply_chain.py
├── integration/
│   ├── test_api_integration.py
│   └── test_error_handling.py
├── fixtures/
│   └── mock_responses.json
└── conftest.py
```

### 9.2 Unit Test Example

**Python:**
```python
import pytest
from unittest.mock import Mock, patch
from resilienceai import ResilienceAIClient
from resilienceai.exceptions import RateLimitError

@pytest.fixture
def client():
    return ResilienceAIClient(api_key="test-key")

@pytest.fixture
def mock_response():
    return {
        "id": "assess-123",
        "location": {"city": "Miami", "state": "FL"},
        "overall_risk_level": "high",
        "overall_score": 85.5,
        "risks": [],
        "created_at": "2024-01-01T00:00:00Z",
    }

def test_climate_risk_assess(client, mock_response):
    with patch.object(client, '_request', return_value=mock_response):
        assessment = client.climate_risk.assess("Miami, FL")
        
        assert assessment.id == "assess-123"
        assert assessment.overall_risk_level.value == "high"
        assert assessment.overall_score == 85.5

def test_rate_limit_retry(client):
    with patch.object(client, '_request') as mock:
        mock.side_effect = [
            RateLimitError("Rate limited", retry_after=1),
            {"id": "assess-123", "overall_risk_level": "high", "overall_score": 85.5, "risks": [], "created_at": "2024-01-01T00:00:00Z", "location": {"city": "Miami", "state": "FL"}},
        ]
        
        assessment = client.climate_risk.assess("Miami, FL")
        assert mock.call_count == 2
```

**TypeScript:**
```typescript
import { describe, it, expect, jest } from '@jest/globals';
import { ResilienceAIClient } from '../src/client';
import { RateLimitError } from '../src/errors';

describe('ClimateRiskResource', () => {
  const client = new ResilienceAIClient({ apiKey: 'test-key' });
  
  it('should assess climate risk', async () => {
    const mockResponse = {
      id: 'assess-123',
      location: { city: 'Miami', state: 'FL' },
      overallRiskLevel: 'high',
      overallScore: 85.5,
      risks: [],
      createdAt: '2024-01-01T00:00:00Z',
    };
    
    jest.spyOn(client as any, 'request').mockResolvedValue(mockResponse);
    
    const assessment = await client.climateRisk.assess('Miami, FL');
    
    expect(assessment.id).toBe('assess-123');
    expect(assessment.overallRiskLevel).toBe('high');
  });
});
```

### 9.3 Integration Testing

```python
import pytest
import os

@pytest.mark.integration
class TestAPIIntegration:
    @pytest.fixture
    def live_client(self):
        api_key = os.getenv("RESILIENCEAI_TEST_API_KEY")
        if not api_key:
            pytest.skip("RESILIENCEAI_TEST_API_KEY not set")
        return ResilienceAIClient(api_key=api_key)
    
    def test_live_climate_risk_assess(self, live_client):
        assessment = live_client.climate_risk.assess("Miami, FL")
        
        assert assessment.id is not None
        assert assessment.overall_risk_level is not None
        assert len(assessment.risks) > 0
```

---

## 10. Documentation

### 10.1 Documentation Structure

```
docs/
├── README.md
├── getting-started.md
├── authentication.md
├── api-reference/
│   ├── climate-risk.md
│   ├── esg.md
│   ├── supply-chain.md
│   ├── reports.md
│   └── portfolio.md
├── examples/
│   ├── basic-usage.py
│   ├── batch-processing.py
│   ├── async-usage.py
│   └── error-handling.py
├── changelog.md
└── migration-guide.md
```

### 10.2 API Reference Example

```markdown
## Climate Risk Assessment

### `client.climate_risk.assess(location, **options)`

Assess climate risks for a specific location.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| location | `str` or `Location` | Yes | Address or coordinates |
| hazards | `List[HazardType]` | No | Specific hazards to assess |
| timeframe | `str` | No | Time horizon (default: "current") |
| scenario | `str` | No | Climate scenario (default: "rcp4.5") |

#### Returns

`ClimateRiskAssessment` object containing:
- `id`: Assessment ID
- `location`: Location details
- `overall_risk_level`: Aggregated risk level
- `overall_score`: Risk score (0-100)
- `risks`: List of individual hazard risks

#### Example

```python
from resilienceai import ResilienceAIClient

client = ResilienceAIClient(api_key="your-key")

assessment = client.climate_risk.assess(
    location="Miami, FL",
    hazards=[HazardType.FLOOD, HazardType.HURRICANE],
    timeframe="2050",
    scenario="rcp8.5"
)

print(f"Risk Level: {assessment.overall_risk_level}")
print(f"Score: {assessment.overall_score}")

for risk in assessment.risks:
    print(f"  {risk.hazard_type}: {risk.risk_level} ({risk.score})")
```
```

### 10.3 Code Examples

**Basic Usage:**
```python
from resilienceai import ResilienceAIClient

# Initialize client
client = ResilienceAIClient(api_key="your-api-key")

# Assess climate risk
assessment = client.climate_risk.assess("Miami, FL")
print(f"Risk Level: {assessment.overall_risk_level}")

# Get ESG score
company = client.esg.get_company("AAPL", id_type="ticker")
print(f"ESG Score: {company.esg_score.overall_score}")
```

**Batch Processing:**
```python
locations = ["Miami, FL", "New York, NY", "Houston, TX"]
assessments = client.climate_risk.batch_assess(locations)

for loc, assessment in zip(locations, assessments):
    print(f"{loc}: {assessment.overall_risk_level}")
```

---

## 11. Package Management

### 11.1 Python Package

**File: `/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "resilienceai"
version = "1.0.0"
description = "Official Python SDK for ResilienceAI climate risk and ESG analytics"
readme = "README.md"
license = "MIT"
requires-python = ">=3.8"
authors = [
    { name = "ResilienceAI", email = "support@resilienceai.io" },
]
keywords = ["climate", "risk", "esg", "sustainability", "api", "sdk"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "mkdocstrings[python]>=0.23.0",
]

[project.urls]
Homepage = "https://resilienceai.io"
Documentation = "https://docs.resilienceai.io"
Repository = "https://github.com/resilienceai/resilienceai-python"
Issues = "https://github.com/resilienceai/resilienceai-python/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/resilienceai"]

[tool.black]
line-length = 100
target-version = ['py38']

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "W"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

### 11.2 TypeScript Package

**File: `/package.json`**

```json
{
  "name": "@resilienceai/sdk",
  "version": "1.0.0",
  "description": "Official TypeScript SDK for ResilienceAI climate risk and ESG analytics",
  "main": "dist/index.js",
  "module": "dist/index.mjs",
  "types": "dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  },
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts",
    "dev": "tsup src/index.ts --format cjs,esm --dts --watch",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src --ext .ts",
    "lint:fix": "eslint src --ext .ts --fix",
    "typecheck": "tsc --noEmit",
    "prepublishOnly": "npm run build"
  },
  "keywords": [
    "climate",
    "risk",
    "esg",
    "sustainability",
    "api",
    "sdk"
  ],
  "author": "ResilienceAI <support@resilienceai.io>",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/resilienceai/resilienceai-typescript.git"
  },
  "bugs": {
    "url": "https://github.com/resilienceai/resilienceai-typescript/issues"
  },
  "homepage": "https://resilienceai.io",
  "devDependencies": {
    "@types/jest": "^29.5.0",
    "@types/node": "^20.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.5.0",
    "ts-jest": "^29.1.0",
    "tsup": "^8.0.0",
    "typescript": "^5.0.0"
  },
  "engines": {
    "node": ">=16.0.0"
  }
}
```

**File: `/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "lib": ["ES2020"],
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 11.3 Distribution

**Python (PyPI):**
```bash
# Build
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Install
pip install resilienceai
```

**TypeScript (npm):**
```bash
# Build
npm run build

# Publish to npm
npm publish --access public

# Install
npm install @resilienceai/sdk
```

---

## 12. Integration Guide

### 12.1 Quick Start

**Python:**
```bash
# Install
pip install resilienceai

# Set API key
export RESILIENCEAI_API_KEY="your-api-key"
```

```python
from resilienceai import ResilienceAIClient

# Create client
client = ResilienceAIClient()

# Assess climate risk
assessment = client.climate_risk.assess("Miami, FL")
print(f"Risk Level: {assessment.overall_risk_level}")
```

**TypeScript:**
```bash
# Install
npm install @resilienceai/sdk

# Set API key
export RESILIENCEAI_API_KEY="your-api-key"
```

```typescript
import { ResilienceAIClient } from '@resilienceai/sdk';

// Create client
const client = new ResilienceAIClient();

// Assess climate risk
const assessment = await client.climateRisk.assess('Miami, FL');
console.log(`Risk Level: ${assessment.overallRiskLevel}`);
```

### 12.2 Configuration Options

| Option | Python | TypeScript | Default | Description |
|--------|--------|------------|---------|-------------|
| api_key | ✓ | ✓ | env var | API authentication |
| base_url | ✓ | ✓ | api.resilienceai.io | API endpoint |
| timeout | ✓ | ✓ | 30s | Request timeout |
| max_retries | ✓ | ✓ | 3 | Max retry attempts |
| retry_delay | ✓ | ✓ | 1s | Initial retry delay |
| rate_limit | ✓ | ✓ | 10 | Requests per second |

### 12.3 Best Practices

1. **Use environment variables for API keys**
2. **Handle errors gracefully**
3. **Use batch operations for multiple items**
4. **Enable retry logic for production**
5. **Monitor rate limits**
6. **Use async for concurrent requests**

---

## 13. Implementation Priority

### Phase 1: Core SDK (Weeks 1-2)
- [x] Client architecture
- [x] Authentication (API Key, OAuth2)
- [x] Basic HTTP client
- [x] Error handling
- [x] Retry logic
- [x] Rate limiting

### Phase 2: API Resources (Weeks 3-4)
- [x] Climate Risk API
- [x] ESG API
- [x] Supply Chain API
- [x] Reports API
- [x] Portfolio API

### Phase 3: Advanced Features (Weeks 5-6)
- [x] Async support
- [x] Batch operations
- [x] Streaming responses
- [x] Webhook support
- [x] Caching layer

### Phase 4: Quality & Distribution (Weeks 7-8)
- [x] Unit tests (>90% coverage)
- [x] Integration tests
- [x] Documentation
- [x] Type definitions
- [x] Package publishing

### Priority Matrix

| Feature | Priority | Effort | Impact |
|---------|----------|--------|--------|
| Core Client | P0 | Medium | High |
| Auth (API Key) | P0 | Low | High |
| Climate Risk API | P0 | Medium | High |
| Error Handling | P0 | Low | High |
| Retry Logic | P0 | Low | Medium |
| ESG API | P1 | Medium | High |
| Rate Limiting | P1 | Low | Medium |
| Async Support | P1 | Medium | Medium |
| Supply Chain API | P2 | Medium | Medium |
| OAuth2 | P2 | Medium | Low |
| Batch Operations | P2 | Low | Medium |
| Webhooks | P3 | High | Low |
| Caching | P3 | Medium | Low |

---

## Appendix A: Complete API Coverage

### Climate Risk
- `POST /climate-risk/assess` - Assess location risk
- `GET /climate-risk/score` - Get specific hazard score
- `GET /climate-risk/historical` - Historical events
- `POST /climate-risk/batch` - Batch assessment
- `GET /climate-risk/scenarios` - Available scenarios

### ESG
- `GET /esg/companies/{id}` - Get company data
- `GET /esg/companies/search` - Search companies
- `GET /esg/scores/{id}` - Get ESG scores
- `POST /esg/compare` - Compare companies
- `GET /esg/benchmarks/{sector}` - Sector benchmarks

### Supply Chain
- `GET /supply-chain/{company_id}` - Get supply chain
- `POST /supply-chain/analyze` - Analyze supply chain
- `GET /supply-chain/alternatives` - Find alternatives
- `POST /supply-chain/simulate` - Simulate disruptions

### Reports
- `POST /reports/generate` - Generate report
- `GET /reports/{id}` - Get report status
- `GET /reports/{id}/download` - Download report
- `GET /reports` - List reports

### Portfolio
- `GET /portfolios` - List portfolios
- `POST /portfolios` - Create portfolio
- `GET /portfolios/{id}` - Get portfolio
- `PUT /portfolios/{id}` - Update portfolio
- `DELETE /portfolios/{id}` - Delete portfolio
- `POST /portfolios/{id}/analyze` - Analyze portfolio

---

## Appendix B: SDK Version Compatibility

| SDK Version | API Version | Python | Node.js | Status |
|-------------|-------------|--------|---------|--------|
| 1.0.x | v1 | 3.8+ | 16+ | Current |
| 0.9.x | v1-beta | 3.7+ | 14+ | Deprecated |

---

*Document Version: 1.0.0*  
*Last Updated: 2024*  
*Maintainer: ResilienceAI Engineering Team*
