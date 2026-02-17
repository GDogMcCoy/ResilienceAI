# ResilienceAI Code Quality Framework

## Executive Summary

This document provides a comprehensive code quality framework for ResilienceAI, encompassing linting, type checking, static analysis, pre-commit hooks, code coverage, review automation, complexity analysis, documentation coverage, security scanning, and CI/CD integration.

---

## 1. Code Quality Architecture

### 1.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESILIENCEAI CODE QUALITY STACK                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   LINTING   │  │   TYPE      │  │   STATIC    │  │   SECURITY  │        │
│  │   LAYER     │  │   CHECKING  │  │   ANALYSIS  │  │   SCANNING  │        │
│  │             │  │             │  │             │  │             │        │
│  │ • Black     │  │ • mypy      │  │ • Bandit    │  │ • Bandit    │        │
│  │ • isort     │  │ • pydantic  │  │ • Pylint    │  │ • Safety    │        │
│  │ • Flake8    │  │ • beartype  │  │ • SonarQube │  │ • Semgrep   │        │
│  │ • Pylint    │  │             │  │ • Radon     │  │ • CodeQL    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│         └────────────────┴────────────────┴────────────────┘               │
│                                    │                                        │
│                         ┌──────────┴──────────┐                            │
│                         │   PRE-COMMIT HOOKS  │                            │
│                         │                     │                            │
│                         │ • Local validation  │                            │
│                         │ • Fast feedback     │                            │
│                         │ • Developer guard   │                            │
│                         └──────────┬──────────┘                            │
│                                    │                                        │
│  ┌─────────────────────────────────┴─────────────────────────────────┐     │
│  │                         CI/CD PIPELINE                            │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │     │
│  │  │   Test   │  │ Coverage │  │  Sonar   │  │ Security │          │     │
│  │  │   Run    │  │  Report  │  │  Scan    │  │  Audit   │          │     │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                    │                                        │
│                         ┌──────────┴──────────┐                            │
│                         │  CODE REVIEW BOT    │                            │
│                         │  (GitHub Actions)   │                            │
│                         └─────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Quality Gates

| Gate | Purpose | Tools | Threshold |
|------|---------|-------|-----------|
| **Gate 1: Format** | Code style consistency | Black, isort | 100% compliance |
| **Gate 2: Lint** | Code quality checks | Flake8, Pylint | Zero errors |
| **Gate 3: Type** | Type safety | mypy | 100% coverage |
| **Gate 4: Security** | Vulnerability detection | Bandit, Safety | Zero high/critical |
| **Gate 5: Test** | Test coverage | pytest, coverage | >80% coverage |
| **Gate 6: Complexity** | Maintainability | Radon, xenon | Cyclomatic <10 |
| **Gate 7: Documentation** | Doc coverage | pydocstyle, interrogate | >90% coverage |

---

## 2. Linting Configuration

### 2.1 Black Configuration

**File:** `pyproject.toml`

```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
  | migrations
  | node_modules
  | __pycache__
  | \.pytest_cache
  | htmlcov
  | \.coverage
  | \.scannerwork
)/
'''
skip-string-normalization = false
skip-magic-trailing-comma = false
preview = true
unstable = false
```

### 2.2 isort Configuration

**File:** `pyproject.toml`

```toml
[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_gitignore = true
skip = [
    ".git", "__pycache__", ".venv", "venv", "build", "dist",
    ".tox", ".eggs", "*.egg-info", "node_modules", "migrations",
]
known_first_party = ["resilience_ai", "resilience_core", "resilience_api"]
known_third_party = [
    "fastapi", "pydantic", "sqlalchemy", "alembic", "celery",
    "redis", "httpx", "pytest", "numpy", "pandas",
]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
import_heading_future = "Future Imports"
import_heading_stdlib = "Standard Library"
import_heading_thirdparty = "Third Party"
import_heading_firstparty = "ResilienceAI"
import_heading_localfolder = "Local"
```

### 2.3 Flake8 Configuration

**File:** `.flake8`

```ini
[flake8]
max-line-length = 88
extend-ignore = 
    E203, E501, W503, W504, E402, E731, B008, B905, SIM105
exclude =
    .git, __pycache__, .venv, venv, build, dist, .tox, .eggs,
    *.egg-info, node_modules, migrations, alembic/versions,
    docs, htmlcov, .coverage, .scannerwork, *_pb2.py, *_pb2_grpc.py
per-file-ignores =
    __init__.py:F401,F403
    tests/*:S101,S311,S105,S106
    conftest.py:F401,F811
    */migrations/*:E501
max-complexity = 10
max-cognitive-complexity = 15
select = 
    E, W, F, C, B, B9, S, I, N, D, DOC, SIM, C4, UP, PT, C90, RUF
enable-extensions = G, FS003
```

### 2.4 Pylint Configuration

**File:** `.pylintrc`

```ini
[MASTER]
init-hook='import sys; sys.path.append(".")'
ignore=migrations,alembic,__pycache__,.git,.venv,venv,build,dist,node_modules,tests,conftest.py
persistent=yes
load-plugins=
    pylint.extensions.check_elif,pylint.extensions.bad_builtin,
    pylint.extensions.docstyle,pylint.extensions.typing
jobs=4
extension-pkg-allow-list=pydantic,numpy,pandas,sqlalchemy

[MESSAGES CONTROL]
disable=
    C0103,C0114,C0115,C0116,C0301,R0903,R0913,R0914,R0915,R0902,R0904,
    R0917,W0718,W0719,W1203,R0801,R0401,E0611,E1101,C0415,W0108

[REPORTS]
output-format=colorized
reports=yes
score=yes

[BASIC]
good-names=i,j,k,ex,Run,_,id,pk,db,fn,logger,app,router,config,settings,T,K,V
bad-names=foo,bar,baz,toto,tutu,tata

[FORMAT]
max-line-length=88
max-module-lines=1000
indent-string='    '
expected-line-ending-format=LF

[MISCELLANEOUS]
notes=FIXME,XXX,TODO,HACK,BUG,OPTIMIZE,REVIEW

[SIMILARITIES]
min-similarity-lines=4
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=yes
```

---

## 3. Type Checking Configuration

### 3.1 mypy Configuration

**File:** `pyproject.toml`

```toml
[tool.mypy]
python_version = "3.11"
platform = "linux"
show_column_numbers = true
show_error_codes = true
show_error_context = true
ignore_missing_imports = true
follow_imports = "normal"
namespace_packages = true
explicit_package_bases = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
warn_unreachable = true
strict_equality = true
strict_concatenate = true
check_untyped_defs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
disallow_untyped_calls = true
disallow_untyped_decorators = false
disallow_subclassing_any = false
disallow_any_generics = false
no_implicit_optional = true
no_implicit_reexport = true
strict_optional = true
strict = true
plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]
exclude = ["migrations", "alembic", "tests", "conftest.py", "docs", "build", "dist"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false

[[tool.mypy.overrides]]
module = "migrations.*"
ignore_errors = true

[[tool.mypy.overrides]]
module = ["celery.*", "redis.*", "boto3.*", "botocore.*", "httpx.*"]
ignore_missing_imports = true

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
warn_untyped_fields = true
```

### 3.2 Type Checking Example

**File:** `resilience_core/domain/models/incident.py`

```python
"""Incident domain model with strict type checking."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from .organization import Organization
    from .user import User


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident status states."""
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    POST_MORTEM = "post_mortem"
    CLOSED = "closed"


class Incident(BaseModel):
    """Core incident domain model with full type safety."""

    model_config = ConfigDict(
        frozen=False, validate_assignment=True, extra="forbid", str_strip_whitespace=True
    )

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=5000)
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.DETECTED
    organization_id: UUID
    created_by: UUID
    assigned_to: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate incident title."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    def acknowledge(self, user_id: UUID) -> Self:
        """Acknowledge the incident."""
        if self.status in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED):
            raise ValueError("Cannot acknowledge resolved or closed incident")
        self.status = IncidentStatus.ACKNOWLEDGED
        self.assigned_to = user_id
        self.updated_at = datetime.utcnow()
        return self

    def resolve(self, resolution_notes: Optional[str] = None) -> Self:
        """Resolve the incident."""
        self.status = IncidentStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if resolution_notes:
            self.metadata["resolution_notes"] = resolution_notes
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert incident to dictionary."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Incident:
        """Create incident from dictionary."""
        return cls.model_validate(data)
```

---

## 4. Static Analysis Configuration

### 4.1 Bandit Security Scanner

**File:** `.bandit.yaml`

```yaml
# Bandit security scanner configuration
skips: []
tests:
  - B101, B102, B103, B104, B105, B106, B107, B108, B110, B112
  - B201, B301, B302, B303, B304, B305, B306, B307, B308, B310
  - B311, B312, B313, B314, B315, B316, B317, B318, B319, B320
  - B321, B323, B324, B325, B401, B402, B403, B404, B405, B406
  - B407, B408, B409, B410, B411, B412, B413, B501, B502, B503
  - B504, B505, B506, B507, B601, B602, B603, B604, B605, B606
  - B607, B608, B609, B610, B611, B701, B702, B703

exclude_dirs:
  - tests, conftest.py, migrations, alembic, docs, build, dist
  - node_modules, .venv, venv, __pycache__, .git, .tox, .eggs

severity: LOW
confidence: LOW
extensions: [.py]
recursive: true
aggregate: vuln
format: json
output_file: bandit-report.json
quiet: false
verbose: true
ignore_nosec: false
```

### 4.2 SonarQube Configuration

**File:** `sonar-project.properties`

```properties
# SonarQube Configuration for ResilienceAI
sonar.projectKey=resilience-ai
sonar.projectName=ResilienceAI
sonar.projectVersion=1.0.0
sonar.organization=resilience-ai-org

sonar.sources=resilience_core,resilience_api,resilience_ml,resilience_worker
sonar.tests=tests
sonar.inclusions=**/*.py
sonar.exclusions=**/migrations/**,**/alembic/**,**/tests/**,**/conftest.py

sonar.python.version=3.11
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=pytest-report.xml
sonar.python.pylint.reportPath=pylint-report.txt
sonar.python.bandit.reportPaths=bandit-report.json

sonar.sourceEncoding=UTF-8
sonar.scm.provider=git
sonar.qualitygate.wait=true

sonar.cpd.exclusions=**/migrations/**,**/tests/**,**/alembic/**
sonar.coverage.exclusions=**/tests/**,**/migrations/**,**/alembic/**
sonar.technicalDebt.developmentCost=30
```

### 4.3 Radon Complexity Analysis

**File:** `.radon.yaml`

```yaml
# Radon complexity analysis configuration
cc:
  min: A
  max: F
  show_complexity: true
  average: false
  total_average: false
  order: SCORE

mi:
  min: A
  max: C
  multi: true
  show: true

raw:
  functions: true
  classes: true
  methods: true
  comments: true
  docstrings: true
  imports: true
  lines: true
  sloc: true
  loc: true
  blanks: true

hal:
  functions: true
  classes: true
  methods: true

exclude:
  - "**/migrations/**"
  - "**/alembic/**"
  - "**/tests/**"
  - "**/conftest.py"

format: json
output: radon-report.json
verbose: true
```

---

## 5. Pre-commit Hooks Configuration

### 5.1 Pre-commit Configuration

**File:** `.pre-commit-config.yaml`

```yaml
# Pre-commit hooks configuration for ResilienceAI
default_language_version:
  python: python3.11

default_stages:
  - pre-commit
  - pre-push

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: detect-aws-credentials
        args: [--allow-missing-credentials]
      - id: detect-private-key
      - id: mixed-line-ending
        args: [--fix=lf]
      - id: no-commit-to-branch
        args: [--branch, main, --branch, master]

  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        additional_dependencies:
          - flake8-bugbear>=24.1.17
          - flake8-comprehensions>=3.14.0
          - flake8-docstrings>=1.7.0
          - flake8-simplify>=0.21.0
          - flake8-bandit>=4.1.1

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic>=2.5.0
          - types-python-dateutil
          - types-pytz
          - types-redis

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.7
    hooks:
      - id: bandit
        args: [-c, .bandit.yaml, -f, json, -o, bandit-report.json]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: [--baseline, .secrets.baseline]

fail_fast: false
```

### 5.2 Pre-commit Installation Script

**File:** `scripts/install-hooks.sh`

```bash
#!/bin/bash
set -e

echo "Installing pre-commit hooks..."

if ! command -v pre-commit &> /dev/null; then
    echo "pre-commit not found. Installing..."
    pip install pre-commit
fi

pre-commit install
pre-commit install --hook-type pre-push
pre-commit install --hook-type commit-msg

echo "Installing additional dependencies..."
pip install black isort flake8 mypy bandit pydocstyle pyupgrade vulture xenon

echo "Pre-commit hooks installed successfully!"
echo "To run all hooks manually: pre-commit run --all-files"
echo "To update hooks: pre-commit autoupdate"
```

---

## 6. Code Coverage Configuration

### 6.1 Coverage.py Configuration

**File:** `pyproject.toml`

```toml
[tool.coverage.run]
source = ["resilience_core", "resilience_api", "resilience_ml", "resilience_worker"]
branch = true
parallel = true
data_file = ".coverage"
omit = [
    "*/tests/*", "*/test_*", "*/conftest.py", "*/migrations/*", "*/alembic/*",
    "*/__pycache__/*", "*/.venv/*", "*/venv/*", "*/build/*", "*/dist/*",
    "*/node_modules/*", "*/docs/*", "*/htmlcov/*", "*/.tox/*", "*/.eggs/*",
    "*/*.egg-info/*", "*/setup.py", "*/manage.py", "*/wsgi.py", "*/asgi.py",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
skip_empty = true
sort = "cover"
exclude_lines = [
    "pragma: no cover",
    "def __repr__", "def __str__",
    "raise AssertionError", "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:", "if typing.TYPE_CHECKING:",
    "@(abc\\.)?abstractmethod", "@(abc\\.)?abstractproperty",
    "@overload", "@typing.overload",
    "pass", "\\.\\.\\.",
    "raise ImportError", "except ImportError:",
    "return NotImplemented", "def __post_init__",
    "# noqa", "# type: ignore", "# pragma: no cover",
]
fail_under = 80

[tool.coverage.html]
directory = "htmlcov"
title = "ResilienceAI Coverage Report"
show_contexts = true

[tool.coverage.xml]
output = "coverage.xml"

[tool.coverage.json]
output = "coverage.json"
show_contexts = true
```

### 6.2 pytest Configuration

**File:** `pyproject.toml`

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers", "--strict-config", "--verbose", "--tb=short",
    "--cov=resilience_core", "--cov=resilience_api", "--cov=resilience_ml", "--cov=resilience_worker",
    "--cov-branch", "--cov-report=term-missing", "--cov-report=html:htmlcov",
    "--cov-report=xml:coverage.xml", "--cov-report=json:coverage.json",
    "--cov-fail-under=80", "--no-cov-on-fail", "-ra",
]
markers = [
    "unit: Unit tests", "integration: Integration tests", "e2e: End-to-end tests",
    "slow: Slow tests", "fast: Fast tests", "api: API tests",
    "db: Database tests", "redis: Redis tests", "celery: Celery tests",
    "ml: Machine learning tests", "security: Security tests",
    "performance: Performance tests", "smoke: Smoke tests",
]
filterwarnings = ["error", "ignore::DeprecationWarning", "ignore::UserWarning"]
env = ["TESTING=true", "ENVIRONMENT=test"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

---

## 7. Code Review Automation

### 7.1 GitHub Actions - Code Quality Workflow

**File:** `.github/workflows/code-quality.yml`

```yaml
name: Code Quality

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: |
          pip install black isort flake8 pylint mypy bandit
          black --check --diff .
          isort --check-only --diff .
          flake8 --format=github .
          pylint --output-format=github resilience_core resilience_api

  type-check:
    name: Type Checking
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: |
          pip install mypy pydantic sqlalchemy types-python-dateutil types-pytz
          mypy --show-error-codes --pretty .

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: |
          pip install bandit safety
          bandit -r . -f json -o bandit-report.json || true
          safety check --full-report || true
      - uses: actions/upload-artifact@v4
        with:
          name: bandit-report
          path: bandit-report.json

  test:
    name: Tests & Coverage
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
        run: pytest --cov-report=xml --cov-report=html
      - uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/

  sonarqube:
    name: SonarQube Analysis
    runs-on: ubuntu-latest
    needs: [lint, type-check, test]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: sonarqube-quality-gate-action@master
        with:
          scanMetadataReportFile: .scannerwork/report-task.txt
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

---

## 8. Complexity Analysis

### 8.1 Complexity Monitoring Script

**File:** `scripts/complexity-monitor.py`

```python
#!/usr/bin/env python3
"""Monitor code complexity and generate reports."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ComplexityMetrics:
    """Code complexity metrics."""
    file_path: str
    cyclomatic_complexity: int = 0
    maintainability_index: float = 0.0
    lines_of_code: int = 0
    functions: list[dict[str, Any]] = field(default_factory=list)

    @property
    def complexity_rank(self) -> str:
        if self.cyclomatic_complexity <= 5: return "A"
        if self.cyclomatic_complexity <= 10: return "B"
        if self.cyclomatic_complexity <= 20: return "C"
        if self.cyclomatic_complexity <= 30: return "D"
        if self.cyclomatic_complexity <= 40: return "E"
        return "F"


class ComplexityAnalyzer:
    THRESHOLDS = {
        "cyclomatic_complexity": 10,
        "maintainability_index": 20,
        "function_complexity": 10,
    }

    def __init__(self, project_path: Path = Path(".")) -> None:
        self.project_path = project_path
        self.metrics: list[ComplexityMetrics] = []

    def run_radon_cc(self) -> dict[str, Any]:
        result = subprocess.run(
            ["radon", "cc", str(self.project_path), "-j", "-a"],
            capture_output=True, text=True,
        )
        return json.loads(result.stdout) if result.stdout else {}

    def run_radon_mi(self) -> dict[str, Any]:
        result = subprocess.run(
            ["radon", "mi", str(self.project_path), "-j"],
            capture_output=True, text=True,
        )
        return json.loads(result.stdout) if result.stdout else {}

    def analyze(self) -> None:
        cc_data = self.run_radon_cc()
        mi_data = self.run_radon_mi()
        all_files = set(cc_data.keys()) | set(mi_data.keys())

        for file_path in all_files:
            metrics = ComplexityMetrics(file_path=file_path)
            if file_path in cc_data and cc_data[file_path]:
                metrics.cyclomatic_complexity = max(
                    b.get("complexity", 0) for b in cc_data[file_path]
                )
            if file_path in mi_data:
                metrics.maintainability_index = mi_data[file_path].get("mi", 0)
            self.metrics.append(metrics)

    def generate_report(self) -> dict[str, Any]:
        total_cc = sum(m.cyclomatic_complexity for m in self.metrics)
        avg_cc = total_cc / len(self.metrics) if self.metrics else 0
        avg_mi = sum(m.maintainability_index for m in self.metrics) / len(self.metrics)

        rank_distribution: dict[str, int] = {}
        for m in self.metrics:
            rank = m.complexity_rank
            rank_distribution[rank] = rank_distribution.get(rank, 0) + 1

        complex_files = [m for m in self.metrics if m.cyclomatic_complexity > 10]

        return {
            "summary": {
                "total_files": len(self.metrics),
                "average_cyclomatic_complexity": round(avg_cc, 2),
                "average_maintainability_index": round(avg_mi, 2),
                "complex_files_count": len(complex_files),
                "rank_distribution": rank_distribution,
            },
            "thresholds": self.THRESHOLDS,
            "complex_files": [
                {"path": m.file_path, "cyclomatic_complexity": m.cyclomatic_complexity}
                for m in sorted(complex_files, key=lambda x: x.cyclomatic_complexity, reverse=True)
            ],
        }

    def save_report(self, output_path: Path = Path("complexity-report.json")) -> None:
        report = self.generate_report()
        output_path.write_text(json.dumps(report, indent=2))
        print(f"Complexity report saved to {output_path}")

    def print_summary(self) -> None:
        report = self.generate_report()
        summary = report["summary"]
        print("\n" + "=" * 60)
        print("COMPLEXITY ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total Files: {summary['total_files']}")
        print(f"Avg Cyclomatic Complexity: {summary['average_cyclomatic_complexity']}")
        print(f"Complex Files: {summary['complex_files_count']}")
        if summary["complex_files_count"] > 0:
            print("\n⚠️  Complex files detected! Consider refactoring.")
            sys.exit(1)
        else:
            print("\n✅ All files within complexity thresholds.")


def main() -> None:
    analyzer = ComplexityAnalyzer()
    analyzer.analyze()
    analyzer.save_report()
    analyzer.print_summary()


if __name__ == "__main__":
    main()
```

---

## 9. Documentation Coverage

### 9.1 pydocstyle Configuration

**File:** `pyproject.toml`

```toml
[tool.pydocstyle]
convention = "google"
add_select = [
    "D212", "D213", "D404", "D405", "D406", "D407", "D408",
    "D409", "D410", "D411", "D412", "D413", "D414", "D416", "D417",
]
add_ignore = [
    "D100", "D101", "D102", "D103", "D104", "D105", "D106", "D107",
    "D203", "D212", "D402", "D415",
]
match = "(?!test_)(?!conftest).*\\.py"
match_dir = "[^migrations|^alembic|^tests|^docs|^build|^dist|^node_modules].*"
```

### 9.2 Interrogate Configuration

**File:** `pyproject.toml`

```toml
[tool.interrogate]
ignore-init-method = true
ignore-init-module = true
ignore-magic = false
ignore-semiprivate = false
ignore-private = false
ignore-property-decorators = false
ignore-module = false
ignore-nested-functions = false
ignore-nested-classes = true
ignore-setters = false
fail-under = 90
exclude = [
    "tests", "conftest.py", "migrations", "alembic", "docs",
    "build", "dist", "node_modules", "__pycache__", ".venv", "venv",
]
ignore-regex = ["^test_", "^__", "^_.*", "^get_", "^set_"]
verbose = 2
quiet = false
color = true
omit-covered-files = false
generate-badge = "docs/assets/doc-coverage-badge.svg"
badge-format = "svg"
```

---

## 10. Security Scanning

### 10.1 Safety Configuration

**File:** `.safety-policy.yml`

```yaml
# Safety security policy configuration
security:
  ignore-cvss-severity-below: 0
  ignore-vulnerabilities: {}
  continue-on-vulnerability-error: False

report:
  format: json
  output: safety-report.json
  full-report: True

system:
  target: requirements.txt
  json: True
  cache: 3600
  ignore-unpinned-requirements: False
```

### 10.2 Semgrep Configuration

**File:** `.semgrep.yaml`

```yaml
# Semgrep configuration for ResilienceAI
rules:
  - import:
      - p/python
      - p/python-flask
      - p/python-sqlalchemy
      - p/fastapi
      - p/celery
      - p/owasp-top-ten
      - p/cwe-top-25
      - p/security-audit
      - p/secrets

  - id: resilience-ai-no-raw-sql
    pattern-either:
      - pattern: text($SQL, ...)
      - pattern: execute($SQL, ...)
      - pattern: raw($SQL, ...)
    message: "Avoid using raw SQL queries. Use ORM methods instead."
    languages: [python]
    severity: WARNING
    metadata:
      category: security
      cwe: "CWE-89: SQL Injection"

  - id: resilience-ai-no-hardcoded-secrets
    pattern-regex: (?i)(password|secret|api_key|token)\s*=\s*["'][^"']{8,}["']
    message: "Potential hardcoded secret detected."
    languages: [python]
    severity: ERROR
    metadata:
      category: security
      cwe: "CWE-798: Use of Hard-coded Credentials"

  - id: resilience-ai-no-debug-mode
    pattern: debug=True
    message: "Debug mode should not be enabled in production."
    languages: [python]
    severity: WARNING
    metadata:
      category: security
      cwe: "CWE-489: Active Debug Code"

scan:
  include: ["**/*.py"]
  exclude: ["**/tests/**", "**/migrations/**", "**/alembic/**"]
  output:
    format: json
    file: semgrep-report.json
  error-on-findings: true
  severity-threshold: WARNING
```

---

## 11. CI/CD Integration

### 11.1 Main CI Pipeline

**File:** `.github/workflows/ci.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop, "release/*"]
    tags: ["v*"]
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: "3.11"
  POETRY_VERSION: "1.7.1"
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - uses: snok/install-poetry@v1
        with:
          version: ${{ env.POETRY_VERSION }}
      - run: poetry install --no-interaction --only dev
      - run: poetry run black --check --diff .
      - run: poetry run isort --check-only --diff .
      - run: poetry run flake8 .

  type-check:
    name: Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - uses: snok/install-poetry@v1
        with:
          version: ${{ env.POETRY_VERSION }}
      - run: poetry install --no-interaction
      - run: poetry run mypy --show-error-codes --pretty .

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - uses: snok/install-poetry@v1
        with:
          version: ${{ env.POETRY_VERSION }}
      - run: poetry install --no-interaction
      - run: poetry run bandit -r . -f json -o bandit-report.json || true
      - run: poetry run safety check --full-report
      - uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/python
            p/owasp-top-ten
            p/cwe-top-25
            p/security-audit
            p/secrets

  test:
    name: Tests
    runs-on: ubuntu-latest
    needs: [lint, type-check]
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - uses: snok/install-poetry@v1
        with:
          version: ${{ env.POETRY_VERSION }}
      - run: poetry install --no-interaction --with dev
      - env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
          TESTING: "true"
        run: |
          poetry run pytest \
            --cov=resilience_core --cov=resilience_api \
            --cov-report=xml --cov-report=html \
            --cov-fail-under=80 -v
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests

  sonarqube:
    name: SonarQube
    runs-on: ubuntu-latest
    needs: [test, security]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
      - uses: sonarsource/sonarqube-quality-gate-action@master
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  build:
    name: Build & Push
    runs-on: ubuntu-latest
    needs: [test, security, sonarqube]
    if: github.event_name != 'pull_request'
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
```

---

## 12. Makefile for Local Development

**File:** `Makefile`

```makefile
.PHONY: help install install-dev lint format type-check test coverage security complexity docs clean ci all

help:
	@echo "ResilienceAI Code Quality Commands"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

format:
	@echo "Formatting code..."
	black .
	isort .

format-check:
	@echo "Checking code formatting..."
	black --check --diff .
	isort --check-only --diff .

lint:
	@echo "Running linters..."
	flake8 .
	pylint resilience_core resilience_api resilience_ml resilience_worker

type-check:
	@echo "Running type checks..."
	mypy --show-error-codes --pretty .

test:
	@echo "Running tests..."
	pytest -v

test-coverage:
	pytest -v --cov=resilience_core --cov=resilience_api --cov=resilience_ml --cov=resilience_worker \
		--cov-report=html --cov-report=term-missing

security:
	@echo "Running security scans..."
	bandit -r . -f json -o bandit-report.json || true
	safety check --full-report

complexity:
	@echo "Running complexity analysis..."
	radon cc . -a -nc
	xenon --max-absolute B --max-modules B --max-average A .
	docs:
	@echo "Building documentation..."
	mkdocs build

pre-commit:
	pre-commit run --all-files

pre-commit-update:
	pre-commit autoupdate

ci:
	@echo "Running all CI checks..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	$(MAKE) test-coverage

clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache .mypy_cache __pycache__ .coverage htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

all:
	$(MAKE) ci
```

---

## 13. Implementation Priority Order

### Phase 1: Foundation (Week 1-2)
1. **Set up Black and isort** - Immediate code formatting
2. **Configure Flake8** - Basic linting rules
3. **Install pre-commit hooks** - Enforce at commit time
4. **Set up pytest** - Test framework with coverage

### Phase 2: Type Safety (Week 2-3)
1. **Configure mypy** - Type checking with strict mode
2. **Add type annotations** - Gradual typing adoption
3. **Set up Pydantic** - Runtime type validation

### Phase 3: Security (Week 3-4)
1. **Configure Bandit** - Security scanning
2. **Set up Safety** - Dependency vulnerability scanning
3. **Configure Semgrep** - Advanced security rules
4. **Implement secrets detection**

### Phase 4: Static Analysis (Week 4-5)
1. **Configure Pylint** - Advanced linting
2. **Set up SonarQube** - Comprehensive analysis
3. **Configure Radon** - Complexity monitoring
4. **Set up documentation coverage**

### Phase 5: Automation (Week 5-6)
1. **Configure GitHub Actions** - CI/CD pipeline
2. **Set up code review bot** - Automated PR reviews
3. **Configure coverage reporting** - Codecov integration
4. **Set up quality gates**

### Phase 6: Optimization (Week 6+)
1. **Fine-tune thresholds** - Based on project metrics
2. **Add custom rules** - Project-specific requirements
3. **Optimize CI performance** - Parallel jobs, caching
4. **Monitor and adjust** - Continuous improvement

---

## 14. Summary

This comprehensive code quality framework provides:

| Category | Tools | Purpose |
|----------|-------|---------|
| **Linting** | Black, isort, Flake8, Pylint | Code style and quality |
| **Type Checking** | mypy, Pydantic | Type safety |
| **Static Analysis** | Bandit, SonarQube, Radon | Deep code analysis |
| **Pre-commit** | pre-commit hooks | Early issue detection |
| **Coverage** | pytest-cov, Codecov | Test coverage tracking |
| **Review Bot** | GitHub Actions, custom scripts | Automated PR reviews |
| **Complexity** | Radon, Xenon | Maintainability metrics |
| **Documentation** | pydocstyle, interrogate | Doc coverage |
| **Security** | Bandit, Safety, Semgrep | Vulnerability scanning |
| **CI/CD** | GitHub Actions | Automated pipelines |

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Engineering Team*
