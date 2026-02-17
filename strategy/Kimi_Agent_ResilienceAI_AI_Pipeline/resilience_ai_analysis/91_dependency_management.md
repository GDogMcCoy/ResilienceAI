# ResilienceAI Dependency Management Strategy

## Executive Summary

This document provides a comprehensive dependency management strategy for ResilienceAI, covering requirements optimization, modern tooling migration, security scanning, license compliance, and automated updates. The strategy ensures reproducible builds, security compliance, and maintainable dependency workflows.

---

## Table of Contents

1. [Dependency Architecture](#1-dependency-architecture)
2. [Requirements Optimization](#2-requirements-optimization)
3. [Modern Tooling Migration](#3-modern-tooling-migration)
4. [Dependency Pinning Strategy](#4-dependency-pinning-strategy)
5. [Security Scanning](#5-security-scanning)
6. [License Compliance](#6-license-compliance)
7. [Dependency Updates](#7-dependency-updates)
8. [Virtual Environment Management](#8-virtual-environment-management)
9. [Container Dependencies](#9-container-dependencies)
10. [Development vs Production](#10-development-vs-production)
11. [Circular Dependency Detection](#11-circular-dependency-detection)
12. [Implementation Roadmap](#12-implementation-roadmap)

---

## 1. Dependency Architecture

### 1.1 Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESILIENCEAI DEPENDENCY ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   CORE DEPS  │    │   ML/AI DEPS │    │   INFRA DEPS │                   │
│  │ • fastapi    │    │ • torch      │    │ • docker     │                   │
│  │ • pydantic   │    │ • transformers│   │ • kubernetes │                   │
│  │ • sqlalchemy │    │ • numpy      │    │ • redis      │                   │
│  │ • httpx      │    │ • pandas     │    │ • celery     │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                   │                   │                           │
│         └───────────────────┼───────────────────┘                           │
│                             ▼                                               │
│              ┌──────────────────────────────┐                               │
│              │     DEPENDENCY RESOLVER      │                               │
│              │    (Poetry/Pipenv/pip)       │                               │
│              └──────────────────────────────┘                               │
│                             │                                               │
│         ┌───────────────────┼───────────────────┐                           │
│         ▼                   ▼                   ▼                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  LOCK FILE   │    │  SECURITY    │    │   LICENSE    │                   │
│  │ poetry.lock  │    │ safety/      │    │ pip-licenses │                   │
│  │ Pipfile.lock │    │ bandit/snyk  │    │ fossa        │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Dependency Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **Core** | Application framework | fastapi, pydantic, sqlalchemy |
| **ML/AI** | Machine learning | torch, transformers, numpy |
| **Data** | Data processing | pandas, pyarrow, polars |
| **Infrastructure** | Deployment & ops | docker, kubernetes, redis |
| **Security** | Authentication & crypto | cryptography, python-jose, bcrypt |
| **Monitoring** | Observability | prometheus-client, opentelemetry |
| **Testing** | Quality assurance | pytest, coverage, hypothesis |
| **Development** | Developer tools | black, ruff, mypy, pre-commit |

### 1.3 Dependency Hierarchy

```python
# File: /app/resilience_ai/dependencies/hierarchy.py
"""Dependency hierarchy management for ResilienceAI."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Set, List, Optional


class DependencyTier(Enum):
    """Dependency criticality tiers."""
    CRITICAL = auto()      # Core functionality, no alternatives
    HIGH = auto()          # Important features, limited alternatives
    MEDIUM = auto()        # Useful features, multiple alternatives
    LOW = auto()           # Nice-to-have, easily replaceable


class DependencyType(Enum):
    """Types of dependencies."""
    FRAMEWORK = auto()
    LIBRARY = auto()
    TOOL = auto()
    SERVICE = auto()


@dataclass
class Dependency:
    """Represents a project dependency."""
    name: str
    version_spec: str
    tier: DependencyTier
    dep_type: DependencyType
    alternatives: List[str]
    security_critical: bool = False
    license_check_required: bool = True
    
    def __hash__(self):
        return hash(self.name)


class DependencyHierarchy:
    """Manages dependency hierarchy and relationships."""
    
    # Critical dependencies - core to the application
    CRITICAL_DEPS: Set[Dependency] = {
        Dependency(
            name="fastapi",
            version_spec="^0.104.0",
            tier=DependencyTier.CRITICAL,
            dep_type=DependencyType.FRAMEWORK,
            alternatives=["flask", "django", "starlette"],
            security_critical=True
        ),
        Dependency(
            name="pydantic",
            version_spec="^2.5.0",
            tier=DependencyTier.CRITICAL,
            dep_type=DependencyType.LIBRARY,
            alternatives=["marshmallow", "attrs"],
            security_critical=True
        ),
        Dependency(
            name="sqlalchemy",
            version_spec="^2.0.0",
            tier=DependencyTier.CRITICAL,
            dep_type=DependencyType.LIBRARY,
            alternatives=["peewee", "tortoise-orm"],
            security_critical=False
        ),
    }
    
    # High-priority ML/AI dependencies
    HIGH_PRIORITY_ML_DEPS: Set[Dependency] = {
        Dependency(
            name="torch",
            version_spec="^2.1.0",
            tier=DependencyTier.HIGH,
            dep_type=DependencyType.LIBRARY,
            alternatives=["tensorflow", "jax"],
            security_critical=False
        ),
        Dependency(
            name="transformers",
            version_spec="^4.35.0",
            tier=DependencyTier.HIGH,
            dep_type=DependencyType.LIBRARY,
            alternatives=["sentence-transformers"],
            security_critical=False
        ),
    }
    
    @classmethod
    def get_all_dependencies(cls) -> Set[Dependency]:
        return cls.CRITICAL_DEPS | cls.HIGH_PRIORITY_ML_DEPS
    
    @classmethod
    def get_security_critical(cls) -> Set[Dependency]:
        return {d for d in cls.get_all_dependencies() if d.security_critical}
```

---

## 2. Requirements Optimization

### 2.1 Requirements File Structure

```
requirements/
├── base.txt              # Core dependencies (always needed)
├── production.txt        # Production-only dependencies
├── development.txt       # Development dependencies
├── testing.txt           # Testing dependencies
├── ml.txt               # Machine learning dependencies
├── monitoring.txt       # Monitoring and observability
├── constraints.txt      # Version constraints for all deps
└── generated/           # Auto-generated lock files
    ├── requirements-lock.txt
    └── requirements-dev-lock.txt
```

### 2.2 Base Requirements

```txt
# File: requirements/base.txt
# Core dependencies for ResilienceAI

# Web Framework
fastapi>=0.104.0,<0.105.0
uvicorn[standard]>=0.24.0,<0.25.0
python-multipart>=0.0.6,<0.1.0

# Data Validation
pydantic>=2.5.0,<2.6.0
pydantic-settings>=2.1.0,<2.2.0
email-validator>=2.1.0,<2.2.0

# Database
sqlalchemy>=2.0.0,<2.1.0
alembic>=1.12.0,<1.13.0
asyncpg>=0.29.0,<0.30.0

# HTTP Client
httpx>=0.25.0,<0.26.0
aiohttp>=3.9.0,<3.10.0

# Caching
redis>=5.0.0,<5.1.0
aioredis>=2.0.0,<2.1.0

# Task Queue
celery>=5.3.0,<5.4.0
flower>=2.0.0,<2.1.0

# Security
cryptography>=41.0.0,<42.0.0
python-jose[cryptography]>=3.3.0,<3.4.0
passlib[bcrypt]>=1.7.0,<1.8.0
python-dotenv>=1.0.0,<1.1.0

# Serialization
orjson>=3.9.0,<3.10.0
msgpack>=1.0.0,<1.1.0

# Utilities
python-dateutil>=2.8.0,<2.9.0
tenacity>=8.2.0,<8.3.0
structlog>=23.2.0,<23.3.0
```

### 2.3 Production Requirements

```txt
# File: requirements/production.txt
# Production-specific dependencies

-r base.txt

# WSGI/ASGI Server
gunicorn>=21.2.0,<21.3.0

# Performance
uvloop>=0.19.0,<0.20.0
httptools>=0.6.0,<0.7.0

# Monitoring & Observability
prometheus-client>=0.19.0,<0.20.0
opentelemetry-api>=1.21.0,<1.22.0
opentelemetry-sdk>=1.21.0,<1.22.0
sentry-sdk>=1.38.0,<1.39.0

# Health Checks
healthcheck>=1.3.0,<1.4.0

# Rate Limiting
slowapi>=0.1.0,<0.2.0
```

### 2.4 Development Requirements

```txt
# File: requirements/development.txt
# Development dependencies

-r base.txt
-r testing.txt

# Code Quality
black>=23.11.0,<23.12.0
isort>=5.12.0,<5.13.0
ruff>=0.1.6,<0.2.0
mypy>=1.7.0,<1.8.0

# Pre-commit
pre-commit>=3.5.0,<3.6.0

# Documentation
mkdocs>=1.5.0,<1.6.0
mkdocs-material>=9.4.0,<9.5.0

# Debugging
ipython>=8.18.0,<8.19.0
ipdb>=0.13.0,<0.14.0
py-spy>=0.3.0,<0.4.0
memray>=1.11.0,<1.12.0

# Development Server
watchdog>=3.0.0,<3.1.0
```

### 2.5 Testing Requirements

```txt
# File: requirements/testing.txt
# Testing dependencies

pytest>=7.4.0,<7.5.0
pytest-asyncio>=0.21.0,<0.22.0
pytest-cov>=4.1.0,<4.2.0
pytest-xdist>=3.5.0,<3.6.0
pytest-mock>=3.12.0,<3.13.0
pytest-timeout>=2.2.0,<2.3.0

# Test Data
factory-boy>=3.3.0,<3.4.0
faker>=20.1.0,<20.2.0
hypothesis>=6.91.0,<6.92.0

# HTTP Testing
httpx>=0.25.0,<0.26.0
respx>=0.20.0,<0.21.0
pytest-httpx>=0.27.0,<0.28.0

# Database Testing
pytest-postgresql>=5.0.0,<5.1.0
```

### 2.6 ML Requirements

```txt
# File: requirements/ml.txt
# Machine learning dependencies

-r base.txt

# Core ML
torch>=2.1.0,<2.2.0
torchvision>=0.16.0,<0.17.0
numpy>=1.24.0,<1.25.0

# Transformers
transformers>=4.35.0,<4.36.0
tokenizers>=0.15.0,<0.16.0
accelerate>=0.24.0,<0.25.0

# Data Processing
pandas>=2.1.0,<2.2.0
pyarrow>=14.0.0,<14.1.0
datasets>=2.14.0,<2.15.0

# Vector Stores
chromadb>=0.4.0,<0.5.0
faiss-cpu>=1.7.0,<1.8.0

# Embeddings
sentence-transformers>=2.2.0,<2.3.0
```

### 2.7 Version Constraints

```txt
# File: requirements/constraints.txt
# Global version constraints for all dependencies

cryptography<42.0.0
requests<3.0.0
urllib3<3.0.0
numpy<2.0.0
pyyaml<7.0.0
```

---

## 3. Modern Tooling Migration

### 3.1 Poetry Configuration

```toml
# File: pyproject.toml
[build-system]
requires = ["poetry-core>=1.8.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "resilience-ai"
version = "1.0.0"
description = "AI-powered resilience platform"
authors = ["ResilienceAI Team <team@resilience.ai>"]
readme = "README.md"
license = "MIT"

[tool.poetry.dependencies]
python = "^3.10"

# Core
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"

# Database
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
asyncpg = "^0.29.0"

# HTTP
httpx = "^0.25.0"
aiohttp = "^3.9.0"

# Caching & Queue
redis = "^5.0.0"
celery = {extras = ["redis"], version = "^5.3.0"}

# Security
cryptography = "^41.0.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.0"}

# ML/AI (optional)
torch = {version = "^2.1.0", optional = true}
transformers = {version = "^4.35.0", optional = true}
numpy = {version = "^1.24.0", optional = true}
pandas = {version = "^2.1.0", optional = true}

# Monitoring
prometheus-client = {version = "^0.19.0", optional = true}
sentry-sdk = {version = "^1.38.0", optional = true}

[tool.poetry.extras]
ml = ["torch", "transformers", "numpy", "pandas"]
monitoring = ["prometheus-client", "sentry-sdk"]
all = ["torch", "transformers", "numpy", "pandas", "prometheus-client", "sentry-sdk"]

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
black = "^23.11.0"
isort = "^5.12.0"
ruff = "^0.1.6"
mypy = "^1.7.0"
pre-commit = "^3.5.0"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5.0"
mkdocs-material = "^9.4.0"
```

### 3.2 Tool Comparison Matrix

| Feature | pip + requirements | Pipenv | Poetry | pdm |
|---------|-------------------|--------|--------|-----|
| **Lock File** | Manual | Pipfile.lock | poetry.lock | pdm.lock |
| **Resolution Speed** | Fast | Medium | Fast | Fast |
| **Virtual Env** | Manual | Auto | Auto | Auto |
| **Dependency Groups** | Limited | Yes | Yes | Yes |
| **PEP 517/518** | No | Partial | Yes | Yes |
| **License Check** | No | No | Plugin | Plugin |
| **Vulnerability Scan** | External | External | External | External |
| **Community** | Large | Medium | Large | Growing |
| **Recommended For** | Simple projects | Legacy | **ResilienceAI** | Modern |

---

## 4. Dependency Pinning Strategy

### 4.1 Pinning Levels

```python
# File: /app/resilience_ai/dependencies/pinning.py
"""Dependency pinning strategy for ResilienceAI."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional
import hashlib


class PinningLevel(Enum):
    """Levels of dependency pinning."""
    LOOSE = auto()      # No version constraints
    MINIMUM = auto()    # >= minimum version
    COMPATIBLE = auto() # ~= compatible release
    EXACT = auto()      # == exact version
    HASH = auto()       # == exact version + hash verification


class DependencyPinner:
    """Manages dependency pinning strategy."""
    
    STRATEGIES: Dict[str, PinningLevel] = {
        'production': PinningLevel.HASH,
        'staging': PinningLevel.EXACT,
        'development': PinningLevel.COMPATIBLE,
        'testing': PinningLevel.EXACT,
    }
    
    CRITICAL_PACKAGES: List[str] = [
        'cryptography', 'pydantic', 'sqlalchemy', 'fastapi', 'torch',
    ]
    
    def __init__(self, environment: str = 'production'):
        self.environment = environment
        self.pinning_level = self.STRATEGIES.get(environment, PinningLevel.EXACT)
    
    def should_pin_exactly(self, package_name: str) -> bool:
        if package_name.lower() in self.CRITICAL_PACKAGES:
            return True
        return self.pinning_level in (PinningLevel.EXACT, PinningLevel.HASH)
```

### 4.2 Pinning Policy Configuration

```yaml
# File: .dependency-pinning-policy.yaml
policy:
  name: "ResilienceAI Dependency Pinning Policy"
  version: "1.0.0"

environments:
  production:
    pinning_level: hash
    require_hashes: true
    allow_unsafe: false
    verify_ssl: true
    
  staging:
    pinning_level: exact
    require_hashes: false
    allow_unsafe: false
    verify_ssl: true
    
  development:
    pinning_level: compatible
    require_hashes: false
    allow_unsafe: true
    verify_ssl: true

critical_packages:
  - cryptography
  - pydantic
  - sqlalchemy
  - fastapi
  - torch
  - transformers
  - numpy
  - redis

version_constraints:
  python: ">=3.10,<3.13"
  numpy: "<2.0.0"
  cryptography: ">=41.0.0,<42.0.0"
```

---

## 5. Security Scanning

### 5.1 Security Scanning Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SECURITY SCANNING PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │   DEPENDENCY  │────▶│   SECURITY    │────▶│   VULNERABILITY│              │
│  │   SOURCES     │     │   SCANNING    │     │   DATABASE     │              │
│  │ • requirements│     │               │     │ • OSV          │              │
│  │ • poetry.lock │     │ • Safety      │     │ • NVD          │              │
│  │ • Pipfile.lock│     │ • Bandit      │     │ • Snyk         │              │
│  └──────────────┘     │ • pip-audit   │     └──────────────┘                │
│                       └──────────────┘              │                        │
│                              │                       │                        │
│                              ▼                       ▼                        │
│                       ┌──────────────┐     ┌──────────────┐                │
│                       │   SCAN        │────▶│   REPORT &   │                │
│                       │   RESULTS     │     │   REMEDIATION│                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Safety Configuration

```yaml
# File: .safety-policy.yml
security:
  # Ignore specific CVEs (with justification)
  ignore-cves:
    - CVE-2023-1234:
        reason: "Not applicable - feature not used"
        expires: "2024-06-01"
    
  # Severity threshold for failing builds
  fail-on-severity: high
  
  # Scan settings
  scan:
    requirements:
      - requirements/production.txt
      - requirements/base.txt
    
    lock-files:
      - poetry.lock
      - Pipfile.lock
    
    include-dev: false
    full-report: true

notifications:
  slack:
    webhook-url: ${SLACK_SECURITY_WEBHOOK}
    channel: "#security-alerts"
  
  email:
    recipients:
      - security@resilience.ai
    on-severity: high
```

### 5.3 CI/CD Security Integration

```yaml
# File: .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        scanner: [safety, pip-audit, bandit]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install safety pip-audit bandit
      
      - name: Run Safety Scan
        if: matrix.scanner == 'safety'
        run: |
          safety check --file requirements/production.txt --json --output safety-report.json
        continue-on-error: true
      
      - name: Run pip-audit
        if: matrix.scanner == 'pip-audit'
        run: |
          pip-audit --format=json --output=pip-audit-report.json requirements/production.txt
        continue-on-error: true
      
      - name: Run Bandit
        if: matrix.scanner == 'bandit'
        run: |
          bandit -r src/resilience_ai -f json -o bandit-report.json --skip B101,B601
        continue-on-error: true
      
      - name: Upload Security Reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports-${{ matrix.scanner }}
          path: '*-report.json'
```

---

## 6. License Compliance

### 6.1 License Policy

```yaml
# File: .license-policy.yaml
policy:
  name: "ResilienceAI License Policy"
  version: "1.0.0"

# Allowed licenses
allowed_licenses:
  - MIT
  - Apache-2.0
  - BSD-2-Clause
  - BSD-3-Clause
  - ISC
  - Python-2.0
  - PSF-2.0
  - LGPL-3.0
  - LGPL-2.1

# Restricted licenses (require review)
restricted_licenses:
  - GPL-2.0
  - GPL-3.0
  - AGPL-3.0
  - MPL-2.0
  - EPL-2.0

# Forbidden licenses
forbidden_licenses:
  - GPL-2.0-only
  - GPL-3.0-only
  - AGPL-1.0
  - AGPL-3.0-only
  - proprietary
  - unknown

# Scan settings
scan:
  include_dev: false
  include_transitive: true
  fail_on_forbidden: true
  warn_on_restricted: true

reporting:
  formats:
    - json
    - csv
    - html
  include_license_text: false
  group_by_license: true
```

---

## 7. Dependency Updates

### 7.1 Update Automation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEPENDENCY UPDATE AUTOMATION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │   SCHEDULED   │────▶│   OUTDATED    │────▶│   SECURITY    │              │
│  │   CHECK       │     │   CHECK       │     │   CHECK       │              │
│  │   (Weekly)    │     │   (pip/poetry)│     │   (Safety)    │              │
│  └──────────────┘     └──────────────┘     └──────────────┘                │
│                              │                       │                       │
│                              ▼                       ▼                       │
│                       ┌──────────────┐     ┌──────────────┐                │
│                       │   UPDATE     │◄────│   VULNERABLE │                │
│                       │   BRANCH     │     │   DEPS       │                │
│                       │ • Bump ver   │     │ • Priority   │                │
│                       │ • Run tests  │     │ • Emergency  │                │
│                       │ • Update lock│     │   fix        │                │
│                       └──────────────┘     └──────────────┘                │
│                              │                                              │
│                              ▼                                              │
│                       ┌──────────────┐     ┌──────────────┐                │
│                       │   CI TESTS   │────▶│   AUTO MERGE │                │
│                       │              │     │   (if pass)  │                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Dependabot Configuration

```yaml
# File: .github/dependabot.yml
version: 2

updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "America/New_York"
    open-pull-requests-limit: 10
    reviewers:
      - "resilience-ai/dependency-team"
    labels:
      - "dependencies"
      - "python"
    commit-message:
      prefix: "deps"
      include: "scope"
    versioning-strategy: "lockfile-only"
    
    # Group related updates
    groups:
      production-dependencies:
        dependency-type: "production"
        update-types:
          - "minor"
          - "patch"
      development-dependencies:
        dependency-type: "development"
        update-types:
          - "minor"
          - "patch"
    
    # Ignore certain dependencies
    ignore:
      - dependency-name: "numpy"
        versions: ["2.x"]
      - dependency-name: "torch"
        update-types: ["version-update:semver-major"]

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"

  # Docker dependencies
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"
```

---

## 8. Virtual Environment Management

### 8.1 Virtual Environment Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VIRTUAL ENVIRONMENT STRATEGY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        VIRTUAL ENVIRONMENT TYPES                      │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │   PROJECT    │  │   FEATURE    │  │   TESTING    │               │  │
│  │  │   DEFAULT    │  │   BRANCH     │  │   ISOLATED   │               │  │
│  │  │ .venv/       │  │ .venv-feat/  │  │ .venv-test/  │               │  │
│  │  │ Main dev     │  │ Feature work │  │ CI/testing   │               │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        ENVIRONMENT MANAGER                            │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │   poetry     │  │   conda      │  │   venv       │               │  │
│  │  │   (default)  │  │   (ML deps)  │  │   (fallback) │               │  │
│  │  │ • Fast       │  │ • GPU support│  │ • Standard   │               │  │
│  │  │ • Reliable   │  │ • Scientific │  │ • Universal  │               │  │
│  │  │ • Lock files │  │ • Binary pkgs│  │ • Built-in   │               │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Conda Environment for ML

```yaml
# File: environment.yml
# Conda environment for ML workloads

name: resilience-ai-ml
channels:
  - pytorch
  - nvidia
  - conda-forge
  - defaults

dependencies:
  # Python
  - python=3.11
  - pip
  
  # Core scientific
  - numpy=1.24
  - pandas=2.1
  - scipy=1.11
  - scikit-learn=1.3
  
  # PyTorch with CUDA
  - pytorch=2.1
  - torchvision=0.16
  - torchaudio=2.1
  - pytorch-cuda=12.1
  
  # Additional ML
  - transformers
  - accelerate
  - datasets
  - tokenizers
  
  # Jupyter
  - jupyter
  - ipykernel
  
  # Pip dependencies
  - pip:
    - fastapi>=0.104.0
    - uvicorn[standard]>=0.24.0
    - pydantic>=2.5.0
    - sqlalchemy>=2.0.0
    - celery>=5.3.0
    - redis>=5.0.0
    - chromadb>=0.4.0
    - sentence-transformers>=2.2.0
```

---

## 9. Container Dependencies

### 9.1 Multi-Stage Dockerfile

```dockerfile
# File: Dockerfile
# Multi-stage build for ResilienceAI

# =============================================================================
# STAGE 1: Builder
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python build tools
RUN pip install --no-cache-dir poetry==1.7.0

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry
RUN poetry config virtualenvs.create false \
    && poetry config installer.max-workers 10

# Install dependencies (without dev)
RUN poetry install --no-dev --no-interaction --no-ansi

# =============================================================================
# STAGE 2: Production
# =============================================================================
FROM python:3.11-slim as production

# Security: Run as non-root user
RUN groupadd -r resilience && useradd -r -g resilience resilience

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=resilience:resilience src/ ./src/
COPY --chown=resilience:resilience config/ ./config/

# Switch to non-root user
USER resilience

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "resilience_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# STAGE 3: Development
# =============================================================================
FROM builder as development

WORKDIR /app

# Install all dependencies (including dev)
RUN poetry install --no-interaction --no-ansi

# Install additional dev tools
RUN pip install --no-cache-dir ipython ipdb pytest-watch

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/
COPY config/ ./config/

# Expose port
EXPOSE 8000

# Run with auto-reload for development
CMD ["uvicorn", "resilience_ai.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# STAGE 4: ML Runtime
# =============================================================================
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime as ml

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements/ml.txt ./
RUN pip install --no-cache-dir -r ml.txt

# Copy application code
COPY src/ ./src/

# Run ML worker
CMD ["celery", "-A", "resilience_ai.ml.worker", "worker", "--loglevel=info"]
```

### 9.2 Docker Compose Configuration

```yaml
# File: docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://resilience:password@db:5432/resilience
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  api-dev:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src:ro
      - ./tests:/app/tests:ro
    environment:
      - DATABASE_URL=postgresql://resilience:password@db:5432/resilience
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=development
    depends_on:
      - db
      - redis
    profiles:
      - dev

  ml-worker:
    build:
      context: .
      dockerfile: Dockerfile
      target: ml
    environment:
      - DATABASE_URL=postgresql://resilience:password@db:5432/resilience
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    profiles:
      - ml

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=resilience
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=resilience
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 10. Development vs Production

### 10.1 Environment Separation Strategy

```python
# File: /app/resilience_ai/config/environments.py
"""Environment-specific configuration."""

from enum import Enum, auto
from typing import Dict, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = auto()
    TESTING = auto()
    STAGING = auto()
    PRODUCTION = auto()


class DependencyProfile(BaseSettings):
    """Dependency profile for an environment."""
    environment: Environment = Environment.DEVELOPMENT
    use_lock_file: bool = Field(default=False)
    allow_prerelease: bool = Field(default=False)
    install_dev_dependencies: bool = Field(default=False)
    require_hashes: bool = Field(default=False)
    verify_ssl: bool = Field(default=True)
    compile_bytecode: bool = Field(default=True)
    use_uvloop: bool = Field(default=False)
    enable_profiling: bool = Field(default=False)
    enable_debug_tools: bool = Field(default=False)


class DevelopmentProfile(DependencyProfile):
    environment: Environment = Environment.DEVELOPMENT
    use_lock_file: bool = False
    allow_prerelease: bool = True
    install_dev_dependencies: bool = True
    require_hashes: bool = False
    enable_profiling: bool = True
    enable_debug_tools: bool = True


class TestingProfile(DependencyProfile):
    environment: Environment = Environment.TESTING
    use_lock_file: bool = True
    allow_prerelease: bool = False
    install_dev_dependencies: bool = True
    require_hashes: bool = False
    enable_profiling: bool = True
    enable_debug_tools: bool = False


class StagingProfile(DependencyProfile):
    environment: Environment = Environment.STAGING
    use_lock_file: bool = True
    allow_prerelease: bool = False
    install_dev_dependencies: bool = False
    require_hashes: bool = True
    enable_profiling: bool = False
    enable_debug_tools: bool = False


class ProductionProfile(DependencyProfile):
    environment: Environment = Environment.PRODUCTION
    use_lock_file: bool = True
    allow_prerelease: bool = False
    install_dev_dependencies: bool = False
    require_hashes: bool = True
    use_uvloop: bool = True
    enable_profiling: bool = False
    enable_debug_tools: bool = False
```

---

## 11. Circular Dependency Detection

### 11.1 Circular Dependency Analyzer

```python
# File: /app/resilience_ai/dependencies/circular_deps.py
"""Circular dependency detection for ResilienceAI."""

import subprocess
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from pathlib import Path


@dataclass
class DependencyNode:
    """Represents a node in the dependency graph."""
    name: str
    version: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    
    def __hash__(self):
        return hash(self.name)


class DependencyGraph:
    """Represents the dependency graph."""
    
    def __init__(self):
        self.nodes: Dict[str, DependencyNode] = {}
    
    def add_node(self, name: str, version: str) -> DependencyNode:
        if name not in self.nodes:
            self.nodes[name] = DependencyNode(name=name, version=version)
        return self.nodes[name]
    
    def add_edge(self, from_pkg: str, to_pkg: str) -> None:
        if from_pkg in self.nodes and to_pkg in self.nodes:
            self.nodes[from_pkg].dependencies.add(to_pkg)
            self.nodes[to_pkg].dependents.add(from_pkg)
    
    def find_cycles(self) -> List[List[str]]:
        """Find all circular dependencies using DFS."""
        cycles = []
        visited = set()
        rec_stack = []
        rec_stack_set = set()
        
        def dfs(node_name: str) -> None:
            visited.add(node_name)
            rec_stack.append(node_name)
            rec_stack_set.add(node_name)
            
            node = self.nodes.get(node_name)
            if node:
                for dep in node.dependencies:
                    if dep not in visited:
                        dfs(dep)
                    elif dep in rec_stack_set:
                        cycle_start = rec_stack.index(dep)
                        cycle = rec_stack[cycle_start:] + [dep]
                        cycles.append(cycle)
            
            rec_stack.pop()
            rec_stack_set.remove(node_name)
        
        for node_name in self.nodes:
            if node_name not in visited:
                dfs(node_name)
        
        return cycles
```

---

## 12. Implementation Roadmap

### 12.1 Phase 1: Foundation (Weeks 1-2)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Audit current dependencies | High | 2 days | DevOps |
| Organize requirements files | High | 1 day | DevOps |
| Set up Poetry configuration | High | 2 days | DevOps |
| Create base lock files | High | 1 day | DevOps |
| Document current state | Medium | 1 day | Tech Lead |

### 12.2 Phase 2: Security (Weeks 3-4)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Implement Safety scanning | High | 2 days | Security |
| Set up pip-audit | High | 1 day | Security |
| Configure CI security checks | High | 2 days | DevOps |
| Create security policy | High | 1 day | Security |

### 12.3 Phase 3: Compliance (Weeks 5-6)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Implement license checking | High | 2 days | Legal/Dev |
| Create license policy | High | 1 day | Legal |
| Set up license scanning CI | Medium | 1 day | DevOps |

### 12.4 Phase 4: Automation (Weeks 7-8)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Set up Dependabot | High | 1 day | DevOps |
| Configure auto-updates | Medium | 2 days | DevOps |
| Create update scripts | Medium | 2 days | DevOps |

### 12.5 Phase 5: Advanced Features (Weeks 9-10)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Implement circular dep detection | Medium | 3 days | Dev |
| Create dependency graph visualization | Low | 2 days | Dev |
| Optimize container builds | Medium | 2 days | DevOps |

---

## Appendix A: Tool Selection Matrix

| Tool | Purpose | Recommended | Alternative |
|------|---------|-------------|-------------|
| **Poetry** | Dependency management | Primary | Pipenv |
| **pip-tools** | Requirements compilation | Secondary | Poetry export |
| **Safety** | Vulnerability scanning | Primary | Snyk |
| **pip-audit** | Vulnerability scanning | Secondary | Safety |
| **Bandit** | Code security scanning | Primary | Semgrep |
| **pip-licenses** | License scanning | Primary | FOSSA |
| **Dependabot** | Automated updates | Primary | Renovate |
| **pre-commit** | Git hooks | Primary | None |
| **Trivy** | Container scanning | Primary | Snyk |

## Appendix B: File Structure

```
resilience-ai/
├── requirements/
│   ├── base.txt
│   ├── production.txt
│   ├── development.txt
│   ├── testing.txt
│   ├── ml.txt
│   ├── monitoring.txt
│   ├── constraints.txt
│   └── generated/
│       ├── requirements-lock.txt
│       └── requirements-dev-lock.txt
├── pyproject.toml
├── poetry.lock
├── Pipfile
├── Pipfile.lock
├── environment.yml
├── .safety-policy.yml
├── .license-policy.yaml
├── .dependency-pinning-policy.yaml
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       ├── security-scan.yml
│       ├── license-check.yml
│       └── container-scan.yml
├── scripts/
│   ├── optimize_requirements.py
│   ├── migrate_to_poetry.py
│   ├── security_scan.py
│   ├── license_check.py
│   ├── check_updates.py
│   ├── venv_manager.py
│   └── generate_hashed_requirements.sh
└── src/resilience_ai/
    └── dependencies/
        ├── __init__.py
        ├── hierarchy.py
        ├── pinning.py
        ├── circular_deps.py
        └── import_cycles.py
```

## Appendix C: Quick Reference

### Poetry Commands
```bash
# Install dependencies
poetry install

# Add dependency
poetry add package-name

# Add dev dependency
poetry add --group dev package-name

# Update lock file
poetry lock

# Export requirements
poetry export -f requirements.txt --output requirements.txt

# Show outdated packages
poetry show --outdated

# Update all packages
poetry update
```

### Security Commands
```bash
# Run safety check
safety check -r requirements/production.txt

# Run pip-audit
pip-audit -r requirements/production.txt

# Run bandit
bandit -r src/resilience_ai

# Generate license report
pip-licenses --format=markdown --output-file=LICENSES.md
```

---

## Summary

This comprehensive dependency management strategy for ResilienceAI provides:

1. **Organized Requirements**: Clear separation of base, production, development, and ML dependencies
2. **Modern Tooling**: Poetry for primary dependency management with pip fallback
3. **Security First**: Automated vulnerability scanning with Safety, pip-audit, and Bandit
4. **License Compliance**: Automated license checking with policy enforcement
5. **Automated Updates**: Dependabot integration with auto-merge for patches
6. **Environment Management**: Flexible virtual environment management
7. **Container Optimization**: Multi-stage Docker builds for production efficiency
8. **Circular Dependency Detection**: Tools to identify and resolve dependency cycles

The implementation follows a phased approach, starting with foundational setup and progressing to advanced automation features.
