# ResilienceAI Load Testing Framework

## Executive Summary

This document provides a comprehensive load testing framework for ResilienceAI, covering performance testing, scalability assessment, stress testing, and continuous monitoring. The framework is designed to ensure the system can handle production workloads while maintaining acceptable response times and reliability.

---

## Table of Contents

1. [Load Testing Architecture](#1-load-testing-architecture)
2. [Test Scenarios](#2-test-scenarios)
3. [Benchmarks & SLAs](#3-benchmarks--slas)
4. [Stress Testing](#4-stress-testing)
5. [Spike Testing](#5-spike-testing)
6. [Endurance Testing](#6-endurance-testing)
7. [Bottleneck Identification](#7-bottleneck-identification)
8. [Capacity Planning](#8-capacity-planning)
9. [Continuous Load Testing](#9-continuous-load-testing)
10. [Reporting & Analysis](#10-reporting--analysis)
11. [Implementation Priority](#11-implementation-priority)

---

## 1. Load Testing Architecture

### 1.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Load Testing Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Locust     │    │     k6       │    │   JMeter     │  Load Generators │
│  │   (Python)   │    │   (Go/JS)    │    │   (Java)     │                  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                   │                            │
│         └───────────────────┼───────────────────┘                            │
│                             │                                                │
│                    ┌────────┴────────┐                                       │
│                    │  Test Controller │                                       │
│                    │   (Orchestrator) │                                       │
│                    └────────┬────────┘                                       │
│                             │                                                │
│         ┌───────────────────┼───────────────────┐                            │
│         │                   │                   │                            │
│  ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐                       │
│  │   API GW    │    │  ML Service │    │  Analytics  │  Target Systems       │
│  │   (Nginx)   │    │  (FastAPI)  │    │  (Redis)    │                       │
│  └─────────────┘    └─────────────┘    └─────────────┘                       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                     Monitoring Stack                                 │     │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │     │
│  │  │Prometheus│  │ Grafana │  │  Jaeger │  │  ELK    │  │InfluxDB │   │     │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tool Selection Matrix

| Tool | Language | Best For | Complexity | Scalability | Integration |
|------|----------|----------|------------|-------------|-------------|
| **Locust** | Python | API testing, Python teams | Low | High (distributed) | Excellent |
| **k6** | JavaScript/Go | Modern APIs, CI/CD | Medium | Very High | Excellent |
| **JMeter** | Java | Complex scenarios, GUI | High | Medium | Good |
| **Artillery** | JavaScript | Quick tests, WebSocket | Low | Medium | Good |
| **Gatling** | Scala | High performance | Medium | Very High | Good |

### 1.3 Recommended Tool Stack

**Primary: Locust + k6**
- **Locust**: For Python-native integration and complex scenario modeling
- **k6**: For CI/CD integration and high-throughput testing
- **JMeter**: For legacy protocol support and GUI-based test design

---

## 2. Test Scenarios

### 2.1 API Endpoint Coverage Matrix

| Endpoint | Method | Priority | Base Load | Peak Load | Critical Path |
|----------|--------|----------|-----------|-----------|---------------|
| `/health` | GET | High | 100 RPS | 500 RPS | Yes |
| `/api/v1/predict` | POST | Critical | 50 RPS | 200 RPS | Yes |
| `/api/v1/batch-predict` | POST | High | 20 RPS | 100 RPS | Yes |
| `/api/v1/models` | GET | Medium | 30 RPS | 150 RPS | No |
| `/api/v1/models/{id}` | GET | Medium | 20 RPS | 100 RPS | No |
| `/api/v1/models/{id}/deploy` | POST | High | 5 RPS | 20 RPS | Yes |
| `/api/v1/explain` | POST | Medium | 10 RPS | 50 RPS | No |
| `/api/v1/metrics` | GET | Low | 10 RPS | 50 RPS | No |
| `/api/v1/feedback` | POST | Medium | 30 RPS | 150 RPS | No |
| `/api/v1/stream/predict` | WebSocket | High | 50 conn | 200 conn | Yes |

### 2.2 User Behavior Profiles

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/user_profiles.py

"""
User behavior profiles for realistic load simulation
"""

from dataclasses import dataclass
from typing import List, Dict
import random

@dataclass
class UserProfile:
    name: str
    weight: float  # Percentage of total users
    think_time_min: float  # Seconds
    think_time_max: float  # Seconds
    workflows: List[Dict]

# Define user profiles
USER_PROFILES = {
    "api_consumer": UserProfile(
        name="API Consumer",
        weight=0.50,  # 50% of users
        think_time_min=1.0,
        think_time_max=5.0,
        workflows=[
            {"endpoint": "/health", "method": "GET", "probability": 0.3},
            {"endpoint": "/api/v1/predict", "method": "POST", "probability": 0.6},
            {"endpoint": "/api/v1/explain", "method": "POST", "probability": 0.1},
        ]
    ),
    
    "batch_processor": UserProfile(
        name="Batch Processor",
        weight=0.25,  # 25% of users
        think_time_min=10.0,
        think_time_max=30.0,
        workflows=[
            {"endpoint": "/api/v1/batch-predict", "method": "POST", "probability": 0.8},
            {"endpoint": "/api/v1/models", "method": "GET", "probability": 0.2},
        ]
    ),
    
    "model_manager": UserProfile(
        name="Model Manager",
        weight=0.15,  # 15% of users
        think_time_min=5.0,
        think_time_max=15.0,
        workflows=[
            {"endpoint": "/api/v1/models", "method": "GET", "probability": 0.4},
            {"endpoint": "/api/v1/models/{id}", "method": "GET", "probability": 0.3},
            {"endpoint": "/api/v1/models/{id}/deploy", "method": "POST", "probability": 0.2},
            {"endpoint": "/api/v1/metrics", "method": "GET", "probability": 0.1},
        ]
    ),
    
    "streaming_client": UserProfile(
        name="Streaming Client",
        weight=0.10,  # 10% of users
        think_time_min=0.5,
        think_time_max=2.0,
        workflows=[
            {"endpoint": "/api/v1/stream/predict", "method": "WS", "probability": 0.9},
            {"endpoint": "/api/v1/feedback", "method": "POST", "probability": 0.1},
        ]
    ),
}

def get_random_user_profile() -> UserProfile:
    """Select a user profile based on weights"""
    profiles = list(USER_PROFILES.values())
    weights = [p.weight for p in profiles]
    return random.choices(profiles, weights=weights, k=1)[0]

def get_think_time(profile: UserProfile) -> float:
    """Generate random think time for a profile"""
    return random.uniform(profile.think_time_min, profile.think_time_max)
```

### 2.3 Test Data Generation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/test_data.py

"""
Test data generation for load testing
"""

import json
import random
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class TestDataGenerator:
    """Generate realistic test data for ML API testing"""
    
    @staticmethod
    def generate_prediction_request(model_type: str = "tabular") -> Dict[str, Any]:
        """Generate a prediction request payload"""
        
        if model_type == "tabular":
            return {
                "model_id": f"model_{random.randint(1, 10)}",
                "features": {
                    "feature_1": random.uniform(0, 100),
                    "feature_2": random.uniform(0, 100),
                    "feature_3": random.uniform(0, 100),
                    "feature_4": random.uniform(0, 100),
                    "feature_5": random.uniform(0, 100),
                    "category": random.choice(["A", "B", "C", "D"]),
                },
                "request_id": f"req_{random.randint(100000, 999999)}",
                "timestamp": random.randint(1609459200, 1704067200),
            }
        
        elif model_type == "image":
            return {
                "model_id": f"vision_model_{random.randint(1, 5)}",
                "image": "base64_encoded_image_data...",  # Simulated
                "preprocessing": {
                    "resize": [224, 224],
                    "normalize": True,
                },
                "request_id": f"req_{random.randint(100000, 999999)}",
            }
        
        elif model_type == "text":
            return {
                "model_id": f"nlp_model_{random.randint(1, 5)}",
                "text": random.choice([
                    "This is a sample text for classification",
                    "Another example of text input",
                    "Machine learning is fascinating",
                    "Load testing ensures reliability",
                ]),
                "task": random.choice(["classification", "sentiment", "ner"]),
                "request_id": f"req_{random.randint(100000, 999999)}",
            }
        
        elif model_type == "time_series":
            return {
                "model_id": f"ts_model_{random.randint(1, 5)}",
                "sequence": np.random.randn(100).tolist(),
                "window_size": 100,
                "forecast_horizon": random.randint(1, 30),
                "request_id": f"req_{random.randint(100000, 999999)}",
            }
    
    @staticmethod
    def generate_batch_request(batch_size: int = 100) -> Dict[str, Any]:
        """Generate a batch prediction request"""
        return {
            "model_id": f"model_{random.randint(1, 10)}",
            "batch_id": f"batch_{random.randint(1000, 9999)}",
            "requests": [
                TestDataGenerator.generate_prediction_request()
                for _ in range(batch_size)
            ],
            "priority": random.choice(["low", "normal", "high"]),
            "callback_url": f"https://callback.example.com/batch/{random.randint(1000, 9999)}",
        }
    
    @staticmethod
    def generate_explanation_request() -> Dict[str, Any]:
        """Generate an explanation request"""
        return {
            "model_id": f"model_{random.randint(1, 10)}",
            "prediction_id": f"pred_{random.randint(100000, 999999)}",
            "method": random.choice(["shap", "lime", "integrated_gradients"]),
            "features": TestDataGenerator.generate_prediction_request()["features"],
            "top_k": random.randint(3, 10),
        }
    
    @staticmethod
    def generate_feedback_request() -> Dict[str, Any]:
        """Generate a feedback request"""
        return {
            "prediction_id": f"pred_{random.randint(100000, 999999)}",
            "actual_value": random.uniform(0, 100),
            "feedback_type": random.choice(["correction", "validation", "rejection"]),
            "metadata": {
                "user_id": f"user_{random.randint(1, 1000)}",
                "timestamp": random.randint(1609459200, 1704067200),
                "confidence": random.uniform(0, 1),
            },
        }
```

---

## 3. Benchmarks & SLAs

### 3.1 Performance SLAs

| Metric | Target | Warning | Critical | Measurement |
|--------|--------|---------|----------|-------------|
| **Response Time (p50)** | < 100ms | 100-200ms | > 200ms | HTTP request duration |
| **Response Time (p95)** | < 500ms | 500-1000ms | > 1000ms | HTTP request duration |
| **Response Time (p99)** | < 1000ms | 1000-2000ms | > 2000ms | HTTP request duration |
| **Error Rate** | < 0.1% | 0.1-1% | > 1% | HTTP 5xx errors |
| **Throughput** | > 100 RPS | 50-100 RPS | < 50 RPS | Requests per second |
| **Availability** | > 99.9% | 99-99.9% | < 99% | Uptime percentage |
| **ML Inference Time** | < 50ms | 50-100ms | > 100ms | Model prediction time |
| **Batch Processing** | < 5s/100 items | 5-10s | > 10s | Batch completion time |

### 3.2 Scalability Benchmarks

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/benchmarks.py

"""
Performance benchmarks and SLA definitions
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum

class Severity(Enum):
    """Severity levels for benchmark violations"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Benchmark:
    """Performance benchmark definition"""
    name: str
    target: float
    warning_threshold: float
    critical_threshold: float
    unit: str
    description: str

# Define benchmarks
BENCHMARKS = {
    # Response Time Benchmarks
    "response_time_p50": Benchmark(
        name="Response Time (p50)",
        target=100,  # ms
        warning_threshold=200,
        critical_threshold=500,
        unit="ms",
        description="50th percentile response time"
    ),
    "response_time_p95": Benchmark(
        name="Response Time (p95)",
        target=500,  # ms
        warning_threshold=1000,
        critical_threshold=2000,
        unit="ms",
        description="95th percentile response time"
    ),
    "response_time_p99": Benchmark(
        name="Response Time (p99)",
        target=1000,  # ms
        warning_threshold=2000,
        critical_threshold=5000,
        unit="ms",
        description="99th percentile response time"
    ),
    
    # Throughput Benchmarks
    "throughput_predict": Benchmark(
        name="Prediction Throughput",
        target=100,  # RPS
        warning_threshold=50,
        critical_threshold=20,
        unit="RPS",
        description="Requests per second for prediction endpoint"
    ),
    "throughput_batch": Benchmark(
        name="Batch Throughput",
        target=20,  # batches/min
        warning_threshold=10,
        critical_threshold=5,
        unit="batches/min",
        description="Batch processing throughput"
    ),
    
    # Error Rate Benchmarks
    "error_rate": Benchmark(
        name="Error Rate",
        target=0.1,  # %
        warning_threshold=1.0,
        critical_threshold=5.0,
        unit="%",
        description="Percentage of failed requests"
    ),
    
    # ML-Specific Benchmarks
    "inference_time": Benchmark(
        name="ML Inference Time",
        target=50,  # ms
        warning_threshold=100,
        critical_threshold=200,
        unit="ms",
        description="Model inference time"
    ),
    "model_load_time": Benchmark(
        name="Model Load Time",
        target=5000,  # ms
        warning_threshold=10000,
        critical_threshold=30000,
        unit="ms",
        description="Time to load a model into memory"
    ),
    
    # Resource Benchmarks
    "cpu_usage": Benchmark(
        name="CPU Usage",
        target=70,  # %
        warning_threshold=80,
        critical_threshold=90,
        unit="%",
        description="CPU utilization"
    ),
    "memory_usage": Benchmark(
        name="Memory Usage",
        target=70,  # %
        warning_threshold=80,
        critical_threshold=90,
        unit="%",
        description="Memory utilization"
    ),
}

def check_benchmark(value: float, benchmark: Benchmark) -> tuple[Severity, str]:
    """
    Check if a value meets the benchmark
    
    Returns:
        Tuple of (severity, message)
    """
    if value > benchmark.critical_threshold:
        return (
            Severity.CRITICAL,
            f"CRITICAL: {benchmark.name} = {value}{benchmark.unit} "
            f"(threshold: {benchmark.critical_threshold}{benchmark.unit})"
        )
    elif value > benchmark.warning_threshold:
        return (
            Severity.WARNING,
            f"WARNING: {benchmark.name} = {value}{benchmark.unit} "
            f"(threshold: {benchmark.warning_threshold}{benchmark.unit})"
        )
    else:
        return (
            Severity.INFO,
            f"OK: {benchmark.name} = {value}{benchmark.unit} "
            f"(target: {benchmark.target}{benchmark.unit})"
        )
```

---

## 4. Stress Testing

### 4.1 Stress Test Scenarios

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/stress_tests.py

"""
Stress testing scenarios for ResilienceAI
"""

from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import json
import random
import time
from typing import Optional

class StressTestUser(HttpUser):
    """
    Stress test user that gradually increases load
    to find system breaking points
    """
    wait_time = between(0.1, 0.5)  # Aggressive timing
    
    def on_start(self):
        """Initialize user session"""
        self.model_ids = [f"model_{i}" for i in range(1, 11)]
        self.request_count = 0
    
    @task(50)
    def stress_predict_endpoint(self):
        """High-frequency prediction requests"""
        payload = {
            "model_id": random.choice(self.model_ids),
            "features": {
                f"feature_{i}": random.uniform(0, 100) 
                for i in range(50)  # Large feature set
            }
        }
        
        with self.client.post(
            "/api/v1/predict",
            json=payload,
            catch_response=True,
            timeout=30  # Extended timeout for stress
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:  # Rate limited
                response.failure("Rate limit exceeded")
            elif response.status_code >= 500:
                response.failure(f"Server error: {response.status_code}")
            else:
                response.success()
        
        self.request_count += 1
    
    @task(20)
    def stress_batch_endpoint(self):
        """Stress batch processing"""
        batch_size = random.randint(100, 1000)  # Large batches
        payload = {
            "model_id": random.choice(self.model_ids),
            "batch_id": f"stress_batch_{random.randint(1000, 9999)}",
            "requests": [
                {
                    "features": {
                        f"feature_{i}": random.uniform(0, 100)
                        for i in range(50)
                    }
                }
                for _ in range(batch_size)
            ]
        }
        
        with self.client.post(
            "/api/v1/batch-predict",
            json=payload,
            catch_response=True,
            timeout=120  # Extended for large batches
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 413:  # Payload too large
                response.failure("Batch size exceeded limit")
            elif response.status_code >= 500:
                response.failure(f"Server error: {response.status_code}")
            else:
                response.success()
    
    @task(20)
    def stress_concurrent_models(self):
        """Rapid model switching"""
        # Rapidly switch between different models
        for model_id in random.sample(self.model_ids, 5):
            payload = {
                "model_id": model_id,
                "features": {f"feature_{i}": random.uniform(0, 100) for i in range(10)}
            }
            
            with self.client.post(
                "/api/v1/predict",
                json=payload,
                catch_response=True,
                timeout=10
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Model {model_id} failed: {response.status_code}")
    
    @task(10)
    def stress_memory_pressure(self):
        """Create memory pressure with large payloads"""
        # Send requests with large feature sets
        payload = {
            "model_id": random.choice(self.model_ids),
            "features": {
                f"feature_{i}": [random.uniform(0, 100) for _ in range(100)]  # Nested arrays
                for i in range(100)
            }
        }
        
        with self.client.post(
            "/api/v1/predict",
            json=payload,
            catch_response=True,
            timeout=60
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 413:
                response.failure("Payload too large")
            else:
                response.success()


class GradualRampUpStressTest:
    """
    Configuration for gradual ramp-up stress testing
    """
    
    STAGES = [
        {"duration": "5m", "users": 100, "spawn_rate": 10},    # Baseline
        {"duration": "5m", "users": 250, "spawn_rate": 20},    # Light stress
        {"duration": "5m", "users": 500, "spawn_rate": 30},    # Medium stress
        {"duration": "5m", "users": 1000, "spawn_rate": 50},   # Heavy stress
        {"duration": "5m", "users": 2000, "spawn_rate": 100},  # Extreme stress
        {"duration": "10m", "users": 2000, "spawn_rate": 0},   # Sustained peak
        {"duration": "5m", "users": 0, "spawn_rate": 0},       # Recovery
    ]
    
    @classmethod
    def get_locust_command(cls, host: str) -> str:
        """Generate Locust command for stress test"""
        return f"""
locust -f stress_tests.py \
    --host={host} \
    --users=2000 \
    --spawn-rate=100 \
    --run-time=35m \
    --html=stress_test_report.html \
    --csv=stress_test_results
        """
```

### 4.2 Stress Test Metrics

| Stage | Duration | Users | Target RPS | Expected Behavior |
|-------|----------|-------|------------|-------------------|
| Baseline | 5 min | 100 | 200 RPS | Normal operation |
| Light Stress | 5 min | 250 | 500 RPS | Slight degradation |
| Medium Stress | 5 min | 500 | 1000 RPS | Noticeable slowdown |
| Heavy Stress | 5 min | 1000 | 2000 RPS | Performance limits |
| Extreme Stress | 5 min | 2000 | 4000 RPS | Breaking point |
| Sustained Peak | 10 min | 2000 | 4000 RPS | Stability test |
| Recovery | 5 min | 0 | 0 RPS | System recovery |

---

## 5. Spike Testing

### 5.1 Spike Test Scenarios

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/spike_tests.py

"""
Spike testing scenarios for ResilienceAI
"""

from locust import HttpUser, task, between
import json
import random

class SpikeTestUser(HttpUser):
    """
    User class for spike testing - rapid load changes
    """
    wait_time = between(0.01, 0.1)  # Very aggressive
    
    def on_start(self):
        self.model_ids = [f"model_{i}" for i in range(1, 11)]
    
    @task(100)
    def spike_prediction(self):
        """High-intensity prediction requests"""
        payload = {
            "model_id": random.choice(self.model_ids),
            "features": {
                f"feature_{i}": random.uniform(0, 100)
                for i in range(20)
            }
        }
        
        self.client.post(
            "/api/v1/predict",
            json=payload,
            timeout=5  # Short timeout for spike test
        )


# Spike Test Configuration
SPIKE_TEST_CONFIGS = {
    "sudden_spike": {
        "description": "Sudden traffic spike simulation",
        "pattern": [
            {"duration": "2m", "users": 50},    # Normal
            {"duration": "30s", "users": 1000},  # Sudden spike
            {"duration": "5m", "users": 1000},  # Sustained
            {"duration": "30s", "users": 50},   # Sudden drop
            {"duration": "3m", "users": 50},    # Recovery
        ]
    },
    
    "multiple_spikes": {
        "description": "Multiple consecutive spikes",
        "pattern": [
            {"duration": "2m", "users": 100},   # Normal
            {"duration": "1m", "users": 500},   # Spike 1
            {"duration": "2m", "users": 100},   # Recovery
            {"duration": "1m", "users": 800},   # Spike 2 (higher)
            {"duration": "2m", "users": 100},   # Recovery
            {"duration": "1m", "users": 1200},  # Spike 3 (extreme)
            {"duration": "5m", "users": 100},   # Final recovery
        ]
    },
    
    "flash_sale_simulation": {
        "description": "Flash sale / event simulation",
        "pattern": [
            {"duration": "1m", "users": 200},    # Pre-event
            {"duration": "10s", "users": 2000},  # Event start
            {"duration": "5m", "users": 2000},   # Peak event
            {"duration": "2m", "users": 500},    # Post-event
            {"duration": "3m", "users": 200},    # Normal
        ]
    },
    
    "viral_content": {
        "description": "Viral content / social media spike",
        "pattern": [
            {"duration": "3m", "users": 100},    # Baseline
            {"duration": "2m", "users": 300},    # Growing interest
            {"duration": "1m", "users": 800},    # Going viral
            {"duration": "5m", "users": 1500},   # Viral peak
            {"duration": "10m", "users": 600},   # Declining
            {"duration": "5m", "users": 200},    # New normal
        ]
    }
}


def generate_spike_test_plan(config_name: str) -> dict:
    """Generate a spike test plan"""
    config = SPIKE_TEST_CONFIGS.get(config_name)
    if not config:
        raise ValueError(f"Unknown spike test config: {config_name}")
    
    total_duration = sum(
        int(stage["duration"].rstrip("ms")) * 
        (60 if stage["duration"].endswith("m") else 1 if stage["duration"].endswith("s") else 1)
        for stage in config["pattern"]
    )
    
    max_users = max(stage["users"] for stage in config["pattern"])
    
    return {
        "name": config_name,
        "description": config["description"],
        "total_duration_seconds": total_duration,
        "max_concurrent_users": max_users,
        "stages": config["pattern"],
        "success_criteria": {
            "max_error_rate": 5.0,  # 5% error rate acceptable during spike
            "recovery_time_seconds": 60,  # Should recover within 60s
            "max_p99_response_time": 5000,  # 5s p99 during spike
        }
    }
```

### 5.2 k6 Spike Test Script

```javascript
// File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/spike_test_k6.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const requestsPerSecond = new Counter('requests_per_second');

// Spike test configuration
export const options = {
    stages: [
        { duration: '2m', target: 50 },    // Normal load
        { duration: '30s', target: 1000 }, // Sudden spike
        { duration: '5m', target: 1000 },  // Sustained spike
        { duration: '30s', target: 50 },   // Sudden drop
        { duration: '3m', target: 50 },    // Recovery
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'], // 95% under 2s
        http_req_failed: ['rate<0.05'],    // Error rate < 5%
        error_rate: ['rate<0.05'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
    const modelId = `model_${Math.floor(Math.random() * 10) + 1}`;
    
    const payload = JSON.stringify({
        model_id: modelId,
        features: {
            feature_1: Math.random() * 100,
            feature_2: Math.random() * 100,
            feature_3: Math.random() * 100,
            feature_4: Math.random() * 100,
            feature_5: Math.random() * 100,
        }
    });
    
    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
        timeout: '5s',
    };
    
    const response = http.post(`${BASE_URL}/api/v1/predict`, payload, params);
    
    // Record metrics
    responseTime.add(response.timings.duration);
    errorRate.add(response.status >= 400 ? 1 : 0);
    requestsPerSecond.add(1);
    
    // Assertions
    check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 5s': (r) => r.timings.duration < 5000,
        'has prediction': (r) => r.json('prediction') !== undefined,
    });
    
    sleep(0.1);
}

export function handleSummary(data) {
    return {
        'spike_test_summary.json': JSON.stringify(data, null, 2),
    };
}
```

---

## 6. Endurance Testing

### 6.1 Endurance Test Configuration

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/endurance_tests.py

"""
Endurance (soak) testing for ResilienceAI
"""

from locust import HttpUser, task, between
import json
import random
import time
from datetime import datetime

class EnduranceTestUser(HttpUser):
    """
    Endurance test user for long-running stability tests
    """
    wait_time = between(1, 5)  # Realistic think time
    
    def on_start(self):
        """Initialize user session with tracking"""
        self.model_ids = [f"model_{i}" for i in range(1, 11)]
        self.session_start = datetime.now()
        self.request_count = 0
        self.error_count = 0
    
    def on_stop(self):
        """Report session statistics"""
        duration = (datetime.now() - self.session_start).total_seconds()
        error_rate = (self.error_count / max(self.request_count, 1)) * 100
        print(f"Session completed: {self.request_count} requests, "
              f"{self.error_count} errors ({error_rate:.2f}%), "
              f"duration: {duration:.0f}s")
    
    @task(40)
    def endurance_predict(self):
        """Sustained prediction requests"""
        payload = {
            "model_id": random.choice(self.model_ids),
            "features": {
                f"feature_{i}": random.uniform(0, 100)
                for i in range(10)
            }
        }
        
        with self.client.post(
            "/api/v1/predict",
            json=payload,
            catch_response=True,
            timeout=30
        ) as response:
            self.request_count += 1
            if response.status_code == 200:
                response.success()
            else:
                self.error_count += 1
                response.failure(f"Status: {response.status_code}")
    
    @task(30)
    def endurance_health_check(self):
        """Regular health checks"""
        with self.client.get("/health", catch_response=True) as response:
            self.request_count += 1
            if response.status_code == 200:
                response.success()
            else:
                self.error_count += 1
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(20)
    def endurance_batch(self):
        """Periodic batch requests"""
        payload = {
            "model_id": random.choice(self.model_ids),
            "requests": [
                {"features": {f"feature_{i}": random.uniform(0, 100) for i in range(10)}}
                for _ in range(10)
            ]
        }
        
        with self.client.post(
            "/api/v1/batch-predict",
            json=payload,
            catch_response=True,
            timeout=60
        ) as response:
            self.request_count += 1
            if response.status_code == 200:
                response.success()
            else:
                self.error_count += 1
    
    @task(10)
    def endurance_model_list(self):
        """Model listing operations"""
        with self.client.get("/api/v1/models", catch_response=True) as response:
            self.request_count += 1
            if response.status_code == 200:
                response.success()
            else:
                self.error_count += 1


# Endurance Test Configurations
ENDURANCE_CONFIGS = {
    "8_hour_standard": {
        "duration": "8h",
        "users": 200,
        "description": "Standard 8-hour endurance test",
        "target_rps": 50,
        "check_intervals": ["1h", "4h", "8h"],
    },
    "24_hour_extended": {
        "duration": "24h",
        "users": 150,
        "description": "Extended 24-hour endurance test",
        "target_rps": 40,
        "check_intervals": ["4h", "8h", "12h", "16h", "20h", "24h"],
    },
    "72_hour_stress": {
        "duration": "72h",
        "users": 300,
        "description": "Weekend-long stress endurance test",
        "target_rps": 75,
        "check_intervals": ["8h", "24h", "48h", "72h"],
    },
    "memory_leak_detection": {
        "duration": "12h",
        "users": 500,
        "description": "High-load test for memory leak detection",
        "target_rps": 150,
        "check_intervals": ["1h", "3h", "6h", "9h", "12h"],
        "memory_threshold_mb": 2048,
    },
}


def get_endurance_test_command(config_name: str, host: str) -> str:
    """Generate Locust command for endurance test"""
    config = ENDURANCE_CONFIGS.get(config_name)
    if not config:
        raise ValueError(f"Unknown endurance config: {config_name}")
    
    return f"""
# Endurance Test: {config['description']}
# Duration: {config['duration']}
# Users: {config['users']}
# Target RPS: {config['target_rps']}

locust -f endurance_tests.py \\
    --host={host} \\
    --users={config['users']} \\
    --spawn-rate={config['users'] // 10} \\
    --run-time={config['duration']} \\
    --html=endurance_{config_name}_report.html \\
    --csv=endurance_{config_name}_results \\
    --logfile=endurance_{config_name}.log
    """
```

### 6.2 Endurance Monitoring Checklist

| Time | Memory Check | CPU Check | Error Rate | Response Time | Action |
|------|-------------|-----------|------------|---------------|--------|
| 1h | Baseline | Baseline | < 0.1% | Baseline | Monitor |
| 4h | Trend | Trend | < 0.1% | Stable | Analyze |
| 8h | Growth check | Sustained | < 0.5% | Stable | Review |
| 12h | Leak detection | Pattern | < 0.5% | Trend | Alert if growing |
| 24h | Full analysis | Full analysis | < 1% | Full analysis | Comprehensive review |
| 48h+ | Memory profile | Performance | < 1% | Degradation | Deep investigation |

---

## 7. Bottleneck Identification

### 7.1 Bottleneck Detection Framework

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/bottleneck_detection.py

"""
Bottleneck identification framework for ResilienceAI
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum
import time
import statistics

class BottleneckType(Enum):
    """Types of performance bottlenecks"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK = "network"
    DATABASE = "database"
    ML_INFERENCE = "ml_inference"
    MODEL_LOADING = "model_loading"
    QUEUE_BACKLOG = "queue_backlog"
    EXTERNAL_API = "external_api"
    UNKNOWN = "unknown"

@dataclass
class Bottleneck:
    """Detected bottleneck information"""
    type: BottleneckType
    severity: str  # low, medium, high, critical
    component: str
    metric: str
    value: float
    threshold: float
    timestamp: float
    recommendation: str

class BottleneckDetector:
    """
    Detects performance bottlenecks in the system
    """
    
    def __init__(self):
        self.metrics_history: Dict[str, List[float]] = {}
        self.bottlenecks: List[Bottleneck] = []
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_io_wait": 20.0,
            "network_latency_ms": 100.0,
            "db_query_time_ms": 500.0,
            "ml_inference_ms": 100.0,
            "model_load_time_ms": 5000.0,
            "queue_depth": 1000,
            "error_rate_percent": 5.0,
            "p99_response_ms": 2000.0,
        }
    
    def record_metric(self, name: str, value: float):
        """Record a metric for analysis"""
        if name not in self.metrics_history:
            self.metrics_history[name] = []
        self.metrics_history[name].append(value)
        
        # Keep only last 1000 values
        self.metrics_history[name] = self.metrics_history[name][-1000:]
    
    def detect_cpu_bottleneck(self) -> Optional[Bottleneck]:
        """Detect CPU bottlenecks"""
        cpu_values = self.metrics_history.get("cpu_percent", [])
        if len(cpu_values) < 10:
            return None
        
        avg_cpu = statistics.mean(cpu_values[-10:])
        if avg_cpu > self.thresholds["cpu_percent"]:
            return Bottleneck(
                type=BottleneckType.CPU,
                severity=self._get_severity(avg_cpu, self.thresholds["cpu_percent"]),
                component="application_server",
                metric="cpu_percent",
                value=avg_cpu,
                threshold=self.thresholds["cpu_percent"],
                timestamp=time.time(),
                recommendation="Scale horizontally or optimize CPU-intensive operations"
            )
        return None
    
    def detect_memory_bottleneck(self) -> Optional[Bottleneck]:
        """Detect memory bottlenecks"""
        memory_values = self.metrics_history.get("memory_percent", [])
        if len(memory_values) < 10:
            return None
        
        avg_memory = statistics.mean(memory_values[-10:])
        if avg_memory > self.thresholds["memory_percent"]:
            return Bottleneck(
                type=BottleneckType.MEMORY,
                severity=self._get_severity(avg_memory, self.thresholds["memory_percent"]),
                component="application_server",
                metric="memory_percent",
                value=avg_memory,
                threshold=self.thresholds["memory_percent"],
                timestamp=time.time(),
                recommendation="Check for memory leaks, increase memory, or optimize model loading"
            )
        return None
    
    def detect_ml_inference_bottleneck(self) -> Optional[Bottleneck]:
        """Detect ML inference bottlenecks"""
        inference_values = self.metrics_history.get("ml_inference_ms", [])
        if len(inference_values) < 10:
            return None
        
        p95_inference = sorted(inference_values)[int(len(inference_values) * 0.95)]
        if p95_inference > self.thresholds["ml_inference_ms"]:
            return Bottleneck(
                type=BottleneckType.ML_INFERENCE,
                severity=self._get_severity(p95_inference, self.thresholds["ml_inference_ms"]),
                component="ml_service",
                metric="ml_inference_ms",
                value=p95_inference,
                threshold=self.thresholds["ml_inference_ms"],
                timestamp=time.time(),
                recommendation="Consider model optimization, batching, or GPU acceleration"
            )
        return None
    
    def detect_queue_bottleneck(self) -> Optional[Bottleneck]:
        """Detect queue backlog bottlenecks"""
        queue_values = self.metrics_history.get("queue_depth", [])
        if len(queue_values) < 5:
            return None
        
        current_depth = queue_values[-1]
        if current_depth > self.thresholds["queue_depth"]:
            return Bottleneck(
                type=BottleneckType.QUEUE_BACKLOG,
                severity=self._get_severity(current_depth, self.thresholds["queue_depth"]),
                component="task_queue",
                metric="queue_depth",
                value=current_depth,
                threshold=self.thresholds["queue_depth"],
                timestamp=time.time(),
                recommendation="Increase worker count or optimize processing time"
            )
        return None
    
    def _get_severity(self, value: float, threshold: float) -> str:
        """Determine severity based on how much threshold is exceeded"""
        ratio = value / threshold
        if ratio > 2.0:
            return "critical"
        elif ratio > 1.5:
            return "high"
        elif ratio > 1.2:
            return "medium"
        else:
            return "low"
    
    def run_detection(self) -> List[Bottleneck]:
        """Run all bottleneck detection methods"""
        detectors: List[Callable[[], Optional[Bottleneck]]] = [
            self.detect_cpu_bottleneck,
            self.detect_memory_bottleneck,
            self.detect_ml_inference_bottleneck,
            self.detect_queue_bottleneck,
        ]
        
        new_bottlenecks = []
        for detector in detectors:
            bottleneck = detector()
            if bottleneck:
                new_bottlenecks.append(bottleneck)
                self.bottlenecks.append(bottleneck)
        
        return new_bottlenecks
    
    def get_bottleneck_report(self) -> Dict:
        """Generate a comprehensive bottleneck report"""
        return {
            "total_bottlenecks_detected": len(self.bottlenecks),
            "bottlenecks_by_type": self._group_by_type(),
            "critical_bottlenecks": [
                b for b in self.bottlenecks if b.severity == "critical"
            ],
            "recommendations": self._generate_recommendations(),
        }
    
    def _group_by_type(self) -> Dict[str, int]:
        """Group bottlenecks by type"""
        counts = {}
        for b in self.bottlenecks:
            counts[b.type.value] = counts.get(b.type.value, 0) + 1
        return counts
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations from detected bottlenecks"""
        recommendations = set()
        for b in self.bottlenecks:
            recommendations.add(b.recommendation)
        return list(recommendations)


# Bottleneck Test Scenarios
BOTTLENECK_TEST_SCENARIOS = {
    "cpu_intensive": {
        "description": "Test CPU-intensive model inference",
        "endpoint": "/api/v1/predict",
        "payload": {"model_type": "complex_nn", "features": "large_set"},
        "concurrent_users": 500,
        "duration": "10m",
        "expected_bottleneck": BottleneckType.CPU,
    },
    "memory_intensive": {
        "description": "Test memory-intensive operations",
        "endpoint": "/api/v1/models/{id}/deploy",
        "payload": {"preload": True, "cache_size": "large"},
        "concurrent_users": 100,
        "duration": "15m",
        "expected_bottleneck": BottleneckType.MEMORY,
    },
    "io_intensive": {
        "description": "Test I/O intensive batch processing",
        "endpoint": "/api/v1/batch-predict",
        "payload": {"batch_size": 10000, "output_format": "detailed"},
        "concurrent_users": 50,
        "duration": "10m",
        "expected_bottleneck": BottleneckType.DISK_IO,
    },
    "queue_buildup": {
        "description": "Test queue handling under load",
        "endpoint": "/api/v1/predict",
        "payload": {"async": True, "priority": "low"},
        "concurrent_users": 1000,
        "duration": "5m",
        "expected_bottleneck": BottleneckType.QUEUE_BACKLOG,
    },
}
```

---

## 8. Capacity Planning

### 8.1 Capacity Planning Model

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/capacity_planning.py

"""
Capacity planning framework for ResilienceAI
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math

@dataclass
class ResourceRequirements:
    """Resource requirements for a given load"""
    cpu_cores: float
    memory_gb: float
    gpu_count: int
    storage_gb: float
    network_mbps: float

@dataclass
class CapacityPlan:
    """Capacity planning result"""
    current_capacity: ResourceRequirements
    recommended_capacity: ResourceRequirements
    headroom_percent: float
    scaling_factor: float
    cost_estimate: Dict[str, float]
    recommendations: List[str]

class CapacityPlanner:
    """
    Capacity planning for ResilienceAI infrastructure
    """
    
    # Resource usage per unit of load
    BASELINE_RESOURCES = {
        "predict_request": {
            "cpu_ms": 50,      # CPU milliseconds per request
            "memory_mb": 10,   # Memory per concurrent request
            "gpu_ms": 0,       # GPU milliseconds (if applicable)
        },
        "batch_request": {
            "cpu_ms": 500,
            "memory_mb": 100,
            "gpu_ms": 0,
        },
        "model_load": {
            "cpu_ms": 10000,
            "memory_mb": 512,  # Per model
            "gpu_memory_mb": 1024,  # If using GPU
        },
    }
    
    # Overhead factors
    OVERHEAD_FACTOR = 1.3  # 30% overhead for system operations
    HEADROOM_FACTOR = 1.5  # 50% headroom for growth
    
    def __init__(self):
        self.current_metrics: Dict[str, float] = {}
        self.projected_growth: Dict[str, float] = {}
    
    def calculate_capacity(
        self,
        current_rps: float,
        target_rps: float,
        current_resources: ResourceRequirements,
        growth_rate_monthly: float = 0.1,  # 10% monthly growth
        planning_horizon_months: int = 6
    ) -> CapacityPlan:
        """
        Calculate required capacity for target load
        
        Args:
            current_rps: Current requests per second
            target_rps: Target requests per second
            current_resources: Current resource allocation
            growth_rate_monthly: Expected monthly growth rate
            planning_horizon_months: Planning time horizon
        
        Returns:
            CapacityPlan with recommendations
        """
        # Calculate scaling factor
        scaling_factor = target_rps / max(current_rps, 1)
        
        # Apply growth projection
        projected_growth = (1 + growth_rate_monthly) ** planning_horizon_months
        total_scaling = scaling_factor * projected_growth * self.HEADROOM_FACTOR
        
        # Calculate recommended resources
        recommended = ResourceRequirements(
            cpu_cores=current_resources.cpu_cores * total_scaling * self.OVERHEAD_FACTOR,
            memory_gb=current_resources.memory_gb * total_scaling * self.OVERHEAD_FACTOR,
            gpu_count=math.ceil(current_resources.gpu_count * scaling_factor),
            storage_gb=current_resources.storage_gb * math.sqrt(total_scaling),  # Sub-linear
            network_mbps=current_resources.network_mbps * scaling_factor * self.OVERHEAD_FACTOR,
        )
        
        # Generate cost estimate
        cost_estimate = self._estimate_cost(recommended)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            current_resources, recommended, scaling_factor
        )
        
        return CapacityPlan(
            current_capacity=current_resources,
            recommended_capacity=recommended,
            headroom_percent=(self.HEADROOM_FACTOR - 1) * 100,
            scaling_factor=total_scaling,
            cost_estimate=cost_estimate,
            recommendations=recommendations,
        )
    
    def _estimate_cost(self, resources: ResourceRequirements) -> Dict[str, float]:
        """Estimate monthly cost for resources"""
        # Simplified cost model (AWS-like pricing)
        costs = {
            "compute": resources.cpu_cores * 50,  # $50 per vCPU/month
            "memory": resources.memory_gb * 8,    # $8 per GB/month
            "gpu": resources.gpu_count * 2000,    # $2000 per GPU/month
            "storage": resources.storage_gb * 0.1,  # $0.10 per GB/month
            "network": resources.network_mbps * 10,  # $10 per Mbps/month
        }
        costs["total"] = sum(costs.values())
        return costs
    
    def _generate_recommendations(
        self,
        current: ResourceRequirements,
        recommended: ResourceRequirements,
        scaling_factor: float
    ) -> List[str]:
        """Generate capacity planning recommendations"""
        recommendations = []
        
        if scaling_factor > 3:
            recommendations.append(
                "Consider horizontal scaling with load balancer for better fault tolerance"
            )
        
        if recommended.cpu_cores > 32:
            recommendations.append(
                "Consider containerization with Kubernetes for better resource utilization"
            )
        
        if recommended.memory_gb > 128:
            recommendations.append(
                "Implement memory caching layer (Redis/Memcached) to reduce memory pressure"
            )
        
        if recommended.gpu_count > 2:
            recommendations.append(
                "Consider GPU cluster with job queue for efficient GPU utilization"
            )
        
        recommendations.append(
            f"Implement auto-scaling policies with target CPU: 70%, Memory: 80%"
        )
        
        recommendations.append(
            f"Set up monitoring alerts at 80% of recommended capacity"
        )
        
        return recommendations
    
    def analyze_peak_capacity(
        self,
        daily_peak_multiplier: float = 3.0,
        seasonal_peak_multiplier: float = 5.0,
        event_peak_multiplier: float = 10.0
    ) -> Dict[str, Dict]:
        """
        Analyze capacity for different peak scenarios
        
        Returns:
            Dictionary with capacity analysis for each scenario
        """
        scenarios = {
            "normal": {"multiplier": 1.0, "description": "Normal operations"},
            "daily_peak": {"multiplier": daily_peak_multiplier, "description": "Daily peak hours"},
            "seasonal_peak": {"multiplier": seasonal_peak_multiplier, "description": "Seasonal peak (holidays)"},
            "event_peak": {"multiplier": event_peak_multiplier, "description": "Special events/launches"},
        }
        
        results = {}
        for name, config in scenarios.items():
            results[name] = {
                "description": config["description"],
                "load_multiplier": config["multiplier"],
                "recommended_instances": math.ceil(config["multiplier"]),
                "scaling_strategy": self._get_scaling_strategy(config["multiplier"]),
            }
        
        return results
    
    def _get_scaling_strategy(self, multiplier: float) -> str:
        """Determine scaling strategy based on load multiplier"""
        if multiplier <= 1.5:
            return "vertical_scaling"
        elif multiplier <= 3.0:
            return "horizontal_scaling"
        elif multiplier <= 5.0:
            return "auto_scaling_with_warm_pool"
        else:
            return "event_driven_serverless"


# Capacity Planning Scenarios
CAPACITY_SCENARIOS = {
    "current_state": {
        "rps": 50,
        "resources": ResourceRequirements(
            cpu_cores=4,
            memory_gb=16,
            gpu_count=0,
            storage_gb=100,
            network_mbps=100,
        ),
    },
    "6_month_target": {
        "rps": 200,
        "growth_rate": 0.15,  # 15% monthly growth
        "horizon_months": 6,
    },
    "12_month_target": {
        "rps": 500,
        "growth_rate": 0.12,  # 12% monthly growth
        "horizon_months": 12,
    },
    "enterprise_scale": {
        "rps": 2000,
        "growth_rate": 0.10,  # 10% monthly growth
        "horizon_months": 12,
    },
}
```

---

## 9. Continuous Load Testing

### 9.1 CI/CD Integration

```yaml
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/.github/workflows/load-tests.yml

name: Continuous Load Testing

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    # Run nightly at 2 AM
    - cron: '0 2 * * *'
  workflow_dispatch:
    inputs:
      test_type:
        description: 'Type of load test'
        required: true
        default: 'smoke'
        type: choice
        options:
          - smoke
          - load
          - stress
          - spike
          - endurance

env:
  PYTHON_VERSION: '3.11'
  K6_VERSION: 'v0.48.0'

jobs:
  # Smoke Test - Quick validation
  smoke-test:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install locust prometheus-client
      
      - name: Start test server
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 30  # Wait for services
      
      - name: Run smoke test
        run: |
          locust -f load_testing/smoke_test.py \
            --host=http://localhost:8000 \
            --users=10 \
            --spawn-rate=5 \
            --run-time=2m \
            --headless \
            --only-summary
      
      - name: Upload results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: smoke-test-results
          path: |
            *.html
            *.csv

  # Load Test - Performance validation
  load-test:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    needs: smoke-test
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      
      - name: Start test environment
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 30
      
      - name: Run k6 load test
        run: |
          k6 run --out json=load_test_results.json \
            load_testing/k6_load_test.js
      
      - name: Check performance regression
        run: |
          python load_testing/check_regression.py load_test_results.json
      
      - name: Upload results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: load-test-results
          path: |
            *.json
            *.html

  # Stress Test - Weekly
  stress-test:
    runs-on: ubuntu-latest
    if: github.event.schedule == '0 2 * * 0'  # Weekly on Sunday
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install locust
      
      - name: Run stress test
        run: |
          locust -f load_testing/stress_tests.py \
            --host=${{ secrets.TEST_ENV_URL }} \
            --users=1000 \
            --spawn-rate=50 \
            --run-time=30m \
            --headless \
            --csv=stress_test
      
      - name: Analyze results
        run: |
          python load_testing/analyze_stress_test.py stress_test_stats.csv
      
      - name: Upload results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: stress-test-results
          path: |
            stress_test_*.csv
            stress_test_*.html

  # Performance Benchmark
  benchmark:
    runs-on: ubuntu-latest
    if: github.event_name == 'workflow_dispatch' && github.event.inputs.test_type == 'load'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up k6
        run: |
          sudo apt-get install k6
      
      - name: Run benchmark
        run: |
          k6 run --out influxdb=http://influxdb:8086/k6 \
            load_testing/benchmark_test.js
      
      - name: Generate report
        run: |
          python load_testing/generate_benchmark_report.py
      
      - name: Commit benchmark results
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add benchmarks/
          git commit -m "Update benchmark results [skip ci]"
          git push
```

### 9.2 Continuous Testing Dashboard

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/continuous_monitoring.py

"""
Continuous load testing monitoring and alerting
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import requests

@dataclass
class TestResult:
    """Load test result record"""
    test_id: str
    test_type: str
    timestamp: datetime
    duration_seconds: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float
    error_rate_percent: float
    status: str  # passed, failed, warning

class ContinuousLoadTester:
    """
    Continuous load testing with trend analysis
    """
    
    def __init__(self, api_base_url: str, prometheus_url: str):
        self.api_base_url = api_base_url
        self.prometheus_url = prometheus_url
        self.results_history: List[TestResult] = []
        self.baseline_metrics: Dict[str, float] = {}
    
    def run_continuous_test(
        self,
        interval_minutes: int = 60,
        test_duration_minutes: int = 5,
        users: int = 50
    ):
        """
        Run continuous load tests at specified intervals
        
        Args:
            interval_minutes: Time between tests
            test_duration_minutes: Duration of each test
            users: Number of concurrent users
        """
        while True:
            try:
                result = self._execute_test(test_duration_minutes, users)
                self.results_history.append(result)
                
                # Analyze trends
                self._analyze_trends()
                
                # Check for regressions
                if self._detect_regression(result):
                    self._alert_regression(result)
                
                # Save results
                self._save_results()
                
            except Exception as e:
                print(f"Test execution failed: {e}")
            
            # Wait for next interval
            time.sleep(interval_minutes * 60)
    
    def _execute_test(self, duration_minutes: int, users: int) -> TestResult:
        """Execute a single load test"""
        import subprocess
        
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Run locust test
        cmd = [
            "locust", "-f", "load_testing/locustfile.py",
            "--host", self.api_base_url,
            "--users", str(users),
            "--spawn-rate", str(users // 5),
            "--run-time", f"{duration_minutes}m",
            "--headless",
            "--json",
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results
        metrics = self._parse_locust_output(result.stdout)
        
        # Determine status
        status = self._determine_test_status(metrics)
        
        return TestResult(
            test_id=test_id,
            test_type="continuous",
            timestamp=datetime.now(),
            duration_seconds=duration_minutes * 60,
            total_requests=metrics.get("total_requests", 0),
            successful_requests=metrics.get("successful_requests", 0),
            failed_requests=metrics.get("failed_requests", 0),
            avg_response_time_ms=metrics.get("avg_response_time", 0),
            p95_response_time_ms=metrics.get("p95_response_time", 0),
            p99_response_time_ms=metrics.get("p99_response_time", 0),
            requests_per_second=metrics.get("rps", 0),
            error_rate_percent=metrics.get("error_rate", 0),
            status=status,
        )
    
    def _analyze_trends(self) -> Dict:
        """Analyze performance trends from history"""
        if len(self.results_history) < 7:  # Need at least a week of data
            return {}
        
        recent = self.results_history[-7:]
        
        trends = {
            "response_time_trend": self._calculate_trend(
                [r.avg_response_time_ms for r in recent]
            ),
            "error_rate_trend": self._calculate_trend(
                [r.error_rate_percent for r in recent]
            ),
            "throughput_trend": self._calculate_trend(
                [r.requests_per_second for r in recent]
            ),
        }
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression
        n = len(values)
        x_mean = sum(range(n)) / n
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1 * y_mean:
            return "increasing"
        elif slope < -0.1 * y_mean:
            return "decreasing"
        else:
            return "stable"
    
    def _detect_regression(self, result: TestResult) -> bool:
        """Detect performance regression"""
        if not self.baseline_metrics:
            return False
        
        # Check response time regression (> 20% increase)
        if result.avg_response_time_ms > self.baseline_metrics.get("avg_response_time", 0) * 1.2:
            return True
        
        # Check error rate regression (> 5x increase)
        if result.error_rate_percent > self.baseline_metrics.get("error_rate", 0.1) * 5:
            return True
        
        return False
    
    def _alert_regression(self, result: TestResult):
        """Send regression alert"""
        alert = {
            "type": "performance_regression",
            "test_id": result.test_id,
            "timestamp": result.timestamp.isoformat(),
            "metrics": {
                "avg_response_time_ms": result.avg_response_time_ms,
                "error_rate_percent": result.error_rate_percent,
                "baseline_avg_response_time_ms": self.baseline_metrics.get("avg_response_time"),
                "baseline_error_rate": self.baseline_metrics.get("error_rate"),
            },
        }
        
        # Send to alerting system
        print(f"ALERT: Performance regression detected! {json.dumps(alert, indent=2)}")
    
    def _determine_test_status(self, metrics: Dict) -> str:
        """Determine test status based on metrics"""
        error_rate = metrics.get("error_rate", 0)
        p95_time = metrics.get("p95_response_time", 0)
        
        if error_rate > 5.0 or p95_time > 5000:
            return "failed"
        elif error_rate > 1.0 or p95_time > 2000:
            return "warning"
        else:
            return "passed"
    
    def _save_results(self):
        """Save results to persistent storage"""
        results_data = [asdict(r) for r in self.results_history]
        with open("load_test_history.json", "w") as f:
            json.dump(results_data, f, indent=2, default=str)


# Prometheus metrics exporter
from prometheus_client import Counter, Histogram, Gauge, start_http_server

class LoadTestMetrics:
    """Prometheus metrics for load testing"""
    
    def __init__(self):
        # Counters
        self.requests_total = Counter(
            'loadtest_requests_total',
            'Total requests',
            ['endpoint', 'status']
        )
        
        # Histograms
        self.request_duration = Histogram(
            'loadtest_request_duration_seconds',
            'Request duration',
            ['endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Gauges
        self.active_users = Gauge(
            'loadtest_active_users',
            'Number of active users'
        )
        
        self.current_rps = Gauge(
            'loadtest_current_rps',
            'Current requests per second'
        )
    
    def record_request(self, endpoint: str, status: str, duration: float):
        """Record a request metric"""
        self.requests_total.labels(endpoint=endpoint, status=status).inc()
        self.request_duration.labels(endpoint=endpoint).observe(duration)
    
    def update_active_users(self, count: int):
        """Update active users gauge"""
        self.active_users.set(count)
    
    def update_rps(self, rps: float):
        """Update RPS gauge"""
        self.current_rps.set(rps)
```

---

## 10. Reporting & Analysis

### 10.1 Report Generation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/load_testing/report_generator.py

"""
Load test report generation for ResilienceAI
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np

@dataclass
class LoadTestReport:
    """Comprehensive load test report"""
    test_id: str
    test_type: str
    start_time: datetime
    end_time: datetime
    summary: Dict
    metrics: Dict
    charts: List[str]
    findings: List[str]
    recommendations: List[str]

class ReportGenerator:
    """
    Generate comprehensive load test reports
    """
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
    
    def generate_report(
        self,
        test_results: Dict,
        test_type: str = "load"
    ) -> LoadTestReport:
        """
        Generate a comprehensive load test report
        
        Args:
            test_results: Raw test results
            test_type: Type of test (load, stress, spike, endurance)
        
        Returns:
            LoadTestReport object
        """
        test_id = f"{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate summary
        summary = self._generate_summary(test_results)
        
        # Calculate metrics
        metrics = self._calculate_metrics(test_results)
        
        # Generate charts
        charts = self._generate_charts(test_results, test_id)
        
        # Identify findings
        findings = self._identify_findings(metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings, metrics)
        
        report = LoadTestReport(
            test_id=test_id,
            test_type=test_type,
            start_time=datetime.fromisoformat(test_results.get("start_time")),
            end_time=datetime.fromisoformat(test_results.get("end_time")),
            summary=summary,
            metrics=metrics,
            charts=charts,
            findings=findings,
            recommendations=recommendations,
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate test summary"""
        return {
            "total_requests": results.get("total_requests", 0),
            "successful_requests": results.get("successful_requests", 0),
            "failed_requests": results.get("failed_requests", 0),
            "success_rate": results.get("success_rate", 0),
            "total_duration_seconds": results.get("duration", 0),
            "peak_concurrent_users": results.get("peak_users", 0),
            "avg_requests_per_second": results.get("avg_rps", 0),
            "peak_requests_per_second": results.get("peak_rps", 0),
        }
    
    def _calculate_metrics(self, results: Dict) -> Dict:
        """Calculate detailed metrics"""
        response_times = results.get("response_times", [])
        
        if not response_times:
            return {}
        
        sorted_times = sorted(response_times)
        n = len(sorted_times)
        
        return {
            "response_time": {
                "min_ms": min(response_times),
                "max_ms": max(response_times),
                "mean_ms": np.mean(response_times),
                "median_ms": np.median(response_times),
                "std_ms": np.std(response_times),
                "p50_ms": sorted_times[int(n * 0.50)],
                "p90_ms": sorted_times[int(n * 0.90)],
                "p95_ms": sorted_times[int(n * 0.95)],
                "p99_ms": sorted_times[int(n * 0.99)],
            },
            "throughput": {
                "avg_rps": results.get("avg_rps", 0),
                "peak_rps": results.get("peak_rps", 0),
                "total_requests": results.get("total_requests", 0),
            },
            "errors": {
                "total_errors": results.get("failed_requests", 0),
                "error_rate": results.get("error_rate", 0),
                "error_breakdown": results.get("error_breakdown", {}),
            },
        }
    
    def _generate_charts(self, results: Dict, test_id: str) -> List[str]:
        """Generate visualization charts"""
        chart_files = []
        
        # Response time distribution
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Response time over time
        if "response_time_series" in results:
            ax = axes[0, 0]
            times = results["response_time_series"]
            ax.plot(times, label="Response Time")
            ax.axhline(y=np.percentile(times, 95), color='r', linestyle='--', label='p95')
            ax.set_xlabel('Request Number')
            ax.set_ylabel('Response Time (ms)')
            ax.set_title('Response Time Over Time')
            ax.legend()
        
        # RPS over time
        if "rps_series" in results:
            ax = axes[0, 1]
            ax.plot(results["rps_series"], label='RPS', color='green')
            ax.set_xlabel('Time')
            ax.set_ylabel('Requests per Second')
            ax.set_title('Throughput Over Time')
            ax.legend()
        
        # Response time histogram
        if "response_times" in results:
            ax = axes[1, 0]
            ax.hist(results["response_times"], bins=50, edgecolor='black')
            ax.set_xlabel('Response Time (ms)')
            ax.set_ylabel('Frequency')
            ax.set_title('Response Time Distribution')
        
        # Error rate over time
        if "error_rate_series" in results:
            ax = axes[1, 1]
            ax.plot(results["error_rate_series"], label='Error Rate', color='red')
            ax.set_xlabel('Time')
            ax.set_ylabel('Error Rate (%)')
            ax.set_title('Error Rate Over Time')
            ax.legend()
        
        plt.tight_layout()
        chart_file = f"{self.output_dir}/{test_id}_charts.png"
        plt.savefig(chart_file, dpi=150)
        plt.close()
        
        chart_files.append(chart_file)
        
        return chart_files
    
    def _identify_findings(self, metrics: Dict) -> List[str]:
        """Identify key findings from metrics"""
        findings = []
        
        rt = metrics.get("response_time", {})
        errors = metrics.get("errors", {})
        
        # Response time findings
        p95 = rt.get("p95_ms", 0)
        p99 = rt.get("p99_ms", 0)
        
        if p95 > 2000:
            findings.append(f"CRITICAL: p95 response time ({p95:.0f}ms) exceeds 2000ms threshold")
        elif p95 > 1000:
            findings.append(f"WARNING: p95 response time ({p95:.0f}ms) exceeds 1000ms target")
        
        if p99 > 5000:
            findings.append(f"CRITICAL: p99 response time ({p99:.0f}ms) exceeds 5000ms threshold")
        
        # Error rate findings
        error_rate = errors.get("error_rate", 0)
        if error_rate > 5.0:
            findings.append(f"CRITICAL: Error rate ({error_rate:.2f}%) exceeds 5% threshold")
        elif error_rate > 1.0:
            findings.append(f"WARNING: Error rate ({error_rate:.2f}%) exceeds 1% warning level")
        
        # Throughput findings
        avg_rps = metrics.get("throughput", {}).get("avg_rps", 0)
        if avg_rps < 50:
            findings.append(f"WARNING: Average throughput ({avg_rps:.1f} RPS) below target of 100 RPS")
        
        return findings
    
    def _generate_recommendations(self, findings: List[str], metrics: Dict) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        for finding in findings:
            if "response time" in finding.lower():
                recommendations.append(
                    "Consider implementing caching layer (Redis) to reduce response times"
                )
                recommendations.append(
                    "Optimize database queries and add appropriate indexes"
                )
                recommendations.append(
                    "Scale horizontally by adding more application servers"
                )
            
            if "error rate" in finding.lower():
                recommendations.append(
                    "Review application logs to identify root cause of errors"
                )
                recommendations.append(
                    "Implement circuit breaker pattern for external service calls"
                )
                recommendations.append(
                    "Increase connection pool sizes for database and external services"
                )
            
            if "throughput" in finding.lower():
                recommendations.append(
                    "Optimize ML model inference with batching or GPU acceleration"
                )
                recommendations.append(
                    "Implement async processing for non-critical operations"
                )
        
        # Add general recommendations
        recommendations.append(
            "Set up continuous monitoring with alerting for early detection"
        )
        recommendations.append(
            "Implement auto-scaling based on CPU and request queue depth"
        )
        
        return list(set(recommendations))  # Remove duplicates
    
    def _save_report(self, report: LoadTestReport):
        """Save report to file"""
        report_data = {
            "test_id": report.test_id,
            "test_type": report.test_type,
            "start_time": report.start_time.isoformat(),
            "end_time": report.end_time.isoformat(),
            "summary": report.summary,
            "metrics": report.metrics,
            "charts": report.charts,
            "findings": report.findings,
            "recommendations": report.recommendations,
        }
        
        report_file = f"{self.output_dir}/{report.test_id}_report.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        # Generate HTML report
        self._generate_html_report(report, report_file.replace(".json", ".html"))
    
    def _generate_html_report(self, report: LoadTestReport, output_file: str):
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Load Test Report - {report.test_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; }}
        .finding {{ background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }}
        .finding.critical {{ background: #f8d7da; border-left-color: #dc3545; }}
        .recommendation {{ background: #d1ecf1; padding: 10px; margin: 5px 0; border-left: 4px solid #17a2b8; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Load Test Report</h1>
    <p><strong>Test ID:</strong> {report.test_id}</p>
    <p><strong>Test Type:</strong> {report.test_type}</p>
    <p><strong>Duration:</strong> {report.start_time} to {report.end_time}</p>
    
    <h2>Summary</h2>
    <div class="summary">
        <div class="metric"><strong>Total Requests:</strong> {report.summary.get('total_requests', 0):,}</div>
        <div class="metric"><strong>Success Rate:</strong> {report.summary.get('success_rate', 0):.2f}%</div>
        <div class="metric"><strong>Average RPS:</strong> {report.summary.get('avg_requests_per_second', 0):.1f}</div>
        <div class="metric"><strong>Peak Concurrent Users:</strong> {report.summary.get('peak_concurrent_users', 0)}</div>
    </div>
    
    <h2>Key Findings</h2>
    {''.join(f'<div class="finding{" critical" if "CRITICAL" in f else ""}">{f}</div>' for f in report.findings)}
    
    <h2>Recommendations</h2>
    {''.join(f'<div class="recommendation">{r}</div>' for r in report.recommendations)}
    
    <h2>Charts</h2>
    {''.join(f'<img src="{c}" style="max-width:100%; margin: 20px 0;" />' for c in report.charts)}
</body>
</html>
        """
        
        with open(output_file, "w") as f:
            f.write(html)
```

---

## 11. Implementation Priority

### 11.1 Priority Matrix

| Component | Priority | Effort | Impact | Timeline |
|-----------|----------|--------|--------|----------|
| **Smoke Tests** | P0 | Low | High | Week 1 |
| **Load Test Scripts (Locust)** | P0 | Medium | High | Week 1-2 |
| **Basic Benchmarks** | P0 | Low | High | Week 2 |
| **CI/CD Integration** | P1 | Medium | High | Week 2-3 |
| **k6 Scripts** | P1 | Medium | Medium | Week 3 |
| **Stress Tests** | P1 | Medium | High | Week 3-4 |
| **Spike Tests** | P2 | Low | Medium | Week 4 |
| **Endurance Tests** | P2 | Medium | Medium | Week 4-5 |
| **Bottleneck Detection** | P2 | High | High | Week 5-6 |
| **Capacity Planning** | P3 | Medium | Medium | Week 6 |
| **Advanced Reporting** | P3 | Medium | Low | Week 7 |
| **Continuous Monitoring** | P3 | High | Medium | Week 7-8 |

### 11.2 Implementation Roadmap

```
Week 1-2: Foundation
├── Set up Locust framework
├── Create basic user scenarios
├── Implement smoke tests
├── Define performance benchmarks
└── Integrate with CI pipeline

Week 3-4: Core Testing
├── Develop k6 scripts
├── Implement stress tests
├── Create spike test scenarios
├── Set up test data generation
└── Build basic reporting

Week 5-6: Advanced Testing
├── Implement endurance tests
├── Build bottleneck detection
├── Create capacity planning model
├── Develop trend analysis
└── Set up alerting

Week 7-8: Optimization
├── Advanced reporting dashboard
├── Continuous monitoring
├── Performance optimization
├── Documentation
└── Team training
```

### 11.3 Quick Start Commands

```bash
# Install dependencies
pip install locust prometheus-client matplotlib

# Run smoke test
locust -f smoke_test.py --host=http://localhost:8000 --users=10 --run-time=2m --headless

# Run load test
locust -f load_test.py --host=http://localhost:8000 --users=100 --run-time=10m --html=report.html

# Run k6 test
k6 run --out json=results.json k6_load_test.js

# Run stress test
locust -f stress_tests.py --host=http://localhost:8000 --users=1000 --run-time=30m

# Run with distributed workers
locust -f load_test.py --master --expect-workers=4
locust -f load_test.py --worker --master-host=<master-ip>
```

---

## Appendix A: File Structure

```
/mnt/okcomputer/output/resilience_ai_analysis/load_testing/
├── README.md
├── requirements.txt
├── locustfile.py              # Main Locust test file
├── k6/
│   ├── load_test.js
│   ├── stress_test.js
│   ├── spike_test.js
│   └── smoke_test.js
├── scenarios/
│   ├── __init__.py
│   ├── user_profiles.py
│   ├── test_data.py
│   └── workflows.py
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py
│   ├── prometheus_exporter.py
│   └── alerting.py
├── analysis/
│   ├── __init__.py
│   ├── bottleneck_detection.py
│   ├── capacity_planning.py
│   └── trend_analysis.py
├── reporting/
│   ├── __init__.py
│   ├── report_generator.py
│   ├── html_templates/
│   └── charts.py
├── ci/
│   └── github-workflows/
│       └── load-tests.yml
├── config/
│   ├── benchmarks.yaml
│   ├── thresholds.yaml
│   └── test_scenarios.yaml
└── data/
    └── test_fixtures/
```

---

## Appendix B: Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOAD_TEST_HOST` | Target API host | `http://localhost:8000` |
| `LOAD_TEST_USERS` | Number of concurrent users | `100` |
| `LOAD_TEST_DURATION` | Test duration | `10m` |
| `LOAD_TEST_SPAWN_RATE` | User spawn rate | `10` |
| `PROMETHEUS_URL` | Prometheus endpoint | `http://localhost:9090` |
| `INFLUXDB_URL` | InfluxDB endpoint | `http://localhost:8086` |
| `SLACK_WEBHOOK` | Slack alert webhook | - |
| `ALERT_THRESHOLD_P95` | p95 alert threshold (ms) | `2000` |
| `ALERT_THRESHOLD_ERROR_RATE` | Error rate alert threshold (%) | `5` |

---

## Summary

This comprehensive load testing framework for ResilienceAI provides:

1. **Multi-tool approach** using Locust, k6, and JMeter
2. **Realistic test scenarios** based on user behavior profiles
3. **Clear performance benchmarks** with defined SLAs
4. **Stress and spike testing** for breaking point analysis
5. **Endurance testing** for stability validation
6. **Bottleneck detection** for performance optimization
7. **Capacity planning** for infrastructure scaling
8. **Continuous testing** integrated with CI/CD
9. **Comprehensive reporting** with actionable insights

The framework is designed to be incremental, allowing teams to start with basic smoke tests and progressively add more sophisticated testing capabilities.
