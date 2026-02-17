# ResilienceAI Testing Framework

Comprehensive testing framework for the ResilienceAI platform including unit tests, integration tests, end-to-end tests, performance benchmarks, and security tests.

## Quick Start

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install Playwright browsers (for E2E tests)
playwright install

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini              # pytest configuration
├── .coveragerc             # Coverage configuration
├── unit/                   # Unit tests (80%)
│   ├── agents/            # Agent system tests
│   ├── data/              # Data pipeline tests
│   ├── llm/               # LLM interface tests
│   ├── api_clients/       # API client tests
│   └── models/            # ML model tests
├── integration/           # Integration tests (15%)
├── e2e/                   # End-to-end tests (5%)
├── performance/           # Performance benchmarks
├── security/              # Security tests
├── fixtures/              # Test data and fixtures
│   ├── data/             # Sample data files
│   └── factories/        # Data generation factories
└── mocks/                 # Mock implementations
```

## Running Tests

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit -v

# Run specific module
pytest tests/unit/data -v

# Run with coverage
pytest tests/unit --cov=src --cov-report=html
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration -v -m integration

# Run with real dependencies
pytest tests/integration -v --no-mock
```

### End-to-End Tests

```bash
# Start dashboard first
python run_dashboard.py &

# Run E2E tests
pytest tests/e2e -v -m e2e

# Run with visible browser
pytest tests/e2e -v --headed

# Run specific test
pytest tests/e2e/test_dashboard.py::TestDashboard::test_dashboard_loads -v
```

### Performance Tests

```bash
# Run benchmarks
pytest tests/performance -v --benchmark-only

# Save benchmark results
pytest tests/performance --benchmark-json=benchmark-results.json
```

### Security Tests

```bash
# Run security tests
pytest tests/security -v -m security

# Run Bandit scan
bandit -r src/ -f json -o bandit-results.json

# Check dependencies
safety check -r requirements.txt
```

## Test Markers

| Marker | Description |
|--------|-------------|
| `unit` | Fast, isolated unit tests |
| `integration` | Tests with dependencies |
| `e2e` | End-to-end browser tests |
| `performance` | Performance benchmarks |
| `security` | Security-focused tests |
| `slow` | Tests taking >1 second |
| `llm` | Tests requiring LLM |

## Fixtures

### Data Fixtures

```python
# Sample county data
@pytest.fixture
def sample_county_data():
    return pd.DataFrame({...})

# All Missouri counties
@pytest.fixture
def sample_missouri_counties():
    return pd.DataFrame({...})

# Large dataset for performance testing
@pytest.fixture
def large_dataset():
    return pd.DataFrame({...})
```

### Mock Fixtures

```python
# Mock LLM provider
@pytest.fixture
def mock_llm_manager():
    return MockLLMManager()

# Mock weather alerts
@pytest.fixture
def mock_weather_alerts():
    return {...}
```

## Writing Tests

### Unit Test Example

```python
import pytest
from src.feature_engineering import FeatureEngineer

@pytest.mark.unit
class TestFeatureEngineer:
    def test_transform(self, sample_county_data):
        engineer = FeatureEngineer()
        result = engineer.transform(sample_county_data)
        
        assert 'healthcare_gap_score' in result.columns
        assert result['healthcare_gap_score'].between(0, 100).all()
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
class TestDataPipeline:
    def test_full_pipeline(self):
        # Test complete data flow
        raw_data = download_data()
        processed = engineer.transform(raw_data)
        models = train_models(processed)
        
        assert len(models) > 0
```

### E2E Test Example

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
class TestDashboard:
    def test_dashboard_loads(self, page: Page):
        page.goto("http://localhost:8501")
        expect(page).to_have_title(/ResilienceAI/)
```

## CI/CD Integration

Tests run automatically on:
- Push to main/claw-autonomous branches
- Pull requests
- Daily at 2 AM UTC

See `.github/workflows/test-suite.yml` for configuration.

## Coverage

Current coverage targets:
- Overall: >70%
- Unit tests: >80%
- Integration tests: >60%

View coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Tests failing due to missing data

```bash
# Generate test fixtures
python tests/fixtures/factories/data_factories.py
```

### E2E tests failing

```bash
# Ensure dashboard is running
python run_dashboard.py &

# Install Playwright browsers
playwright install
```

### Import errors

```bash
# Ensure src is in Python path
export PYTHONPATH=.
```

## Contributing

1. Write tests for new features
2. Follow existing test patterns
3. Use appropriate markers
4. Update fixtures as needed
5. Ensure CI passes

## License

Same as ResilienceAI project
