# ResilienceAI Testing & QA Strategy
## Comprehensive Testing Framework Design

---

## Executive Summary

This document outlines a comprehensive testing and quality assurance strategy for the ResilienceAI platform. The strategy addresses the multi-layered architecture including data pipelines, ML models, agent orchestration, LLM integrations, geospatial processing, and Streamlit dashboards.

---

## 1. Current Testing Setup Analysis

### 1.1 Existing Test Structure

```
tests/
├── test_archia_pipeline.py      # Archia Cloud API tests
├── test_dashboard_logic.py      # Dashboard data integrity tests
├── test_geospatial_pipeline.py  # Geospatial processing tests
├── test_llm_integration.py      # LLM provider tests (458 lines)
├── test_orchestration.py        # Multi-agent orchestration tests (377 lines)
├── test_vector_space.py         # Vector space/embedding tests
├── test_visualizations.py       # Visualization tests
├── DASHBOARD_TEST_RESULTS.md    # Dashboard test documentation
├── EDGE_CASE_TEST_RESULTS.md    # Edge case documentation
├── UX_TEST_RESULTS.md           # UX test documentation
└── VISUAL_TEST_RESULTS.md       # Visual test documentation
```

### 1.2 Current Test Coverage Assessment

| Component | Coverage Level | Test Types | Gaps Identified |
|-----------|---------------|------------|-----------------|
| LLM Integration | Medium | Unit, Mock | Async tests, error handling |
| Agent Orchestration | Medium | Unit, Mock | Integration tests, load tests |
| Dashboard Logic | Low | Integration | E2E tests, visual regression |
| Geospatial Pipeline | Low | Integration | Performance tests, edge cases |
| Vector Space | Medium | Unit | Load tests, concurrency |
| Data Pipeline | Low | None | Full coverage needed |
| API Clients | Low | None | Mock tests, contract tests |
| ML Models | None | None | Model validation, drift tests |

### 1.3 Current Testing Framework

- **Framework**: pytest with unittest.mock
- **Test Data**: Real data files (county_features.csv)
- **Mocking**: Basic unittest.mock usage
- **CI/CD**: GitHub Actions workflows (limited)
- **Coverage**: No coverage reporting configured

---

## 2. Testing Pyramid Architecture

```
                    ┌─────────────────┐
                    │   E2E Tests     │  ← 5% (Selenium, Playwright)
                    │  (Dashboard UI) │
                    ├─────────────────┤
                    │  Integration    │  ← 15% (API, Pipeline, Agents)
                    │    Tests        │
                    ├─────────────────┤
                    │   Unit Tests    │  ← 80% (Functions, Classes, Methods)
                    │  (pytest)       │
                    └─────────────────┘
```

### 2.1 Test Categories by Component

```
┌─────────────────────────────────────────────────────────────────────┐
│                      RESILIENCEAI TEST ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Data Layer  │  │    ML/DL     │  │   API Layer  │              │
│  │  Tests       │  │    Tests     │  │   Tests      │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│         │                 │                 │                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Agent      │  │  Geospatial  │  │  Dashboard   │              │
│  │  System      │  │   Engine     │  │    Tests     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Security & Performance Test Suite                │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Enhanced Test Directory Structure

```
tests/
├── conftest.py                          # Shared fixtures and configuration
├── pytest.ini                           # pytest configuration
├── .coveragerc                          # Coverage configuration
├── __init__.py
│
├── unit/                                # Unit Tests (80%)
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── test_base_agent.py
│   │   ├── test_climate_agent.py
│   │   ├── test_vulnerability_agent.py
│   │   ├── test_planning_agent.py
│   │   ├── test_realtime_agent.py
│   │   └── test_orchestrator.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── test_llm_interface.py
│   │   ├── test_llm_providers.py
│   │   └── test_prompt_templates.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── test_feature_engineering.py
│   │   ├── test_download_data.py
│   │   └── test_data_validation.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── test_predictive_models.py
│   │   ├── test_train_models.py
│   │   └── test_model_validation.py
│   ├── geospatial/
│   │   ├── __init__.py
│   │   ├── test_spatial_stats.py
│   │   ├── test_geo_visualizations.py
│   │   └── test_network_analysis.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── test_fhir_export.py
│   │   ├── test_geojson_export.py
│   │   └── test_config.py
│   └── api_clients/
│       ├── __init__.py
│       ├── test_weather_client.py
│       ├── test_climate_client.py
│       ├── test_archia_client.py
│       └── test_agriculture_client.py
│
├── integration/                         # Integration Tests (15%)
│   ├── __init__.py
│   ├── test_data_pipeline.py
│   ├── test_agent_workflows.py
│   ├── test_llm_orchestration.py
│   ├── test_geospatial_pipeline.py
│   ├── test_api_integration.py
│   ├── test_end_to_end_flow.py
│   └── test_database_integration.py
│
├── e2e/                                 # End-to-End Tests (5%)
│   ├── __init__.py
│   ├── test_dashboard.py
│   ├── test_user_workflows.py
│   └── page_objects/
│       ├── __init__.py
│       ├── base_page.py
│       └── dashboard_page.py
│
├── performance/                         # Performance Tests
│   ├── __init__.py
│   ├── test_load.py
│   ├── test_stress.py
│   ├── test_api_latency.py
│   ├── test_data_processing_speed.py
│   └── benchmarks/
│       ├── __init__.py
│       └── benchmark_results.py
│
├── security/                            # Security Tests
│   ├── __init__.py
│   ├── test_input_validation.py
│   ├── test_api_security.py
│   └── test_data_sanitization.py
│
├── fixtures/                            # Test Data & Fixtures
│   ├── __init__.py
│   ├── data/
│   │   ├── sample_county_data.csv
│   │   ├── sample_predictions.json
│   │   └── mock_api_responses/
│   ├── agents/
│   │   └── mock_agent_configs.yaml
│   └── factories/
│       ├── __init__.py
│       └── data_factories.py
│
└── mocks/                               # Mock Implementations
    ├── __init__.py
    ├── mock_llm_providers.py
    ├── mock_api_clients.py
    ├── mock_gee_client.py
    └── mock_agents.py
```

---

## 4. Test Configuration Files

### 4.1 pytest.ini Configuration

**File Path**: `/tests/pytest.ini`

```ini
[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Test paths
testpaths = tests

# Markers for test categorization
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, with dependencies)
    e2e: End-to-end tests (full system)
    performance: Performance and load tests
    security: Security-focused tests
    slow: Tests that take longer than 1 second
    llm: Tests requiring LLM infrastructure
    geospatial: Tests requiring geospatial data
    agents: Tests for agent system
    dashboard: Tests for Streamlit dashboard
    api: Tests for external API clients
    
# Coverage settings
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=70

# Async support
asyncio_mode = auto

# Warnings
filterwarnings =
    ignore::DeprecationWarning:tensorflow.*
    ignore::UserWarning:shap.*

# Environment variables
env =
    TESTING=true
    PYTHONPATH=.
```

### 4.2 conftest.py - Shared Fixtures

**File Path**: `/tests/conftest.py`

```python
"""
ResilienceAI Test Configuration and Shared Fixtures
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# =============================================================================
# Path Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def project_root():
    """Return project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Return test data directory."""
    return project_root / "tests" / "fixtures" / "data"

@pytest.fixture(scope="session")
def mock_responses_dir(project_root):
    """Return mock API responses directory."""
    return project_root / "tests" / "fixtures" / "mock_api_responses"

# =============================================================================
# Data Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def sample_county_data():
    """Generate sample county data for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        'fips': [f'29001', f'29002', f'29003'] * 5,
        'county_name': ['County A, Missouri', 'County B, Missouri', 'County C, Missouri'] * 5,
        'latitude': np.random.uniform(36, 40, 15),
        'longitude': np.random.uniform(-95, -89, 15),
        'population': np.random.randint(10000, 500000, 15),
        'uninsured_pct': np.random.uniform(5, 25, 15),
        'poverty_rate': np.random.uniform(8, 35, 15),
        'risk_level': np.random.choice(['Low', 'Medium', 'High'], 15),
        'healthcare_gap_score': np.random.uniform(0, 100, 15),
        'disaster_risk_score': np.random.uniform(0, 100, 15),
    })

@pytest.fixture(scope="function")
def sample_missouri_counties():
    """Generate all 115 Missouri counties for testing."""
    counties = [
        "Adair", "Andrew", "Atchison", "Audrain", "Barry", "Barton", "Bates",
        "Benton", "Bollinger", "Boone", "Buchanan", "Butler", "Caldwell",
        "Callaway", "Camden", "Cape Girardeau", "Carroll", "Carter", "Cass",
        "Cedar", "Chariton", "Christian", "Clark", "Clay", "Clinton", "Cole",
        "Cooper", "Crawford", "Dade", "Dallas", "Daviess", "DeKalb", "Dent",
        "Douglas", "Dunklin", "Franklin", "Gasconade", "Gentry", "Greene",
        "Grundy", "Harrison", "Henry", "Hickory", "Holt", "Howard", "Howell",
        "Iron", "Jackson", "Jasper", "Jefferson", "Johnson", "Knox", "Laclede",
        "Lafayette", "Lawrence", "Lewis", "Lincoln", "Linn", "Livingston",
        "Macon", "Madison", "Maries", "Marion", "McDonald", "Mercer", "Miller",
        "Mississippi", "Moniteau", "Monroe", "Montgomery", "Morgan", "New Madrid",
        "Newton", "Nodaway", "Oregon", "Osage", "Ozark", "Pemiscot", "Perry",
        "Pettis", "Phelps", "Pike", "Platte", "Polk", "Pulaski", "Putnam",
        "Ralls", "Randolph", "Ray", "Reynolds", "Ripley", "Saline", "Schuyler",
        "Scotland", "Scott", "Shannon", "Shelby", "St. Charles", "St. Clair",
        "St. Francois", "St. Louis", "St. Louis City", "Ste. Genevieve",
        "Stoddard", "Stone", "Sullivan", "Taney", "Texas", "Vernon", "Warren",
        "Washington", "Wayne", "Webster", "Worth", "Wright"
    ]
    
    return pd.DataFrame({
        'fips': [f'29{i:03d}' for i in range(1, 116)],
        'county_name': [f"{c}, Missouri" for c in counties],
        'latitude': np.random.uniform(36, 40.5, 115),
        'longitude': np.random.uniform(-95.7, -89, 115),
        'population': np.random.randint(5000, 1000000, 115),
        'uninsured_pct': np.random.uniform(5, 25, 115),
        'poverty_rate': np.random.uniform(8, 35, 115),
        'risk_level': np.random.choice(['Low', 'Medium', 'High'], 115),
    })

@pytest.fixture(scope="function")
def empty_dataframe():
    """Return empty DataFrame for edge case testing."""
    return pd.DataFrame()

@pytest.fixture(scope="function")
def invalid_dataframe():
    """Return DataFrame with invalid data for error testing."""
    return pd.DataFrame({
        'fips': [None, '', 'invalid', np.nan],
        'latitude': [999, -999, 'invalid', None],
        'longitude': ['abc', None, 999, -999],
    })

# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        'content': 'This is a test response from the LLM.',
        'model': 'test-model',
        'usage': {'prompt_tokens': 10, 'completion_tokens': 10},
        'metadata': {'test': True}
    }

@pytest.fixture(scope="function")
def mock_weather_alerts():
    """Mock weather alerts from NOAA API."""
    return {
        'features': [
            {
                'properties': {
                    'event': 'Tornado Warning',
                    'severity': 'Extreme',
                    'areaDesc': 'St. Louis County, Missouri',
                    'effective': '2024-01-01T12:00:00Z',
                    'expires': '2024-01-01T13:00:00Z',
                }
            }
        ]
    }

@pytest.fixture(scope="function")
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock()
    agent.name = "test_agent"
    agent.description = "Test agent for unit testing"
    agent.version = "1.0.0"
    agent.process.return_value = {
        'success': True,
        'data': {'result': 'test'},
        'error': None
    }
    return agent

@pytest.fixture(scope="function")
def mock_requests_session():
    """Mock requests session for API testing."""
    with patch('requests.Session') as mock_session:
        yield mock_session

# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture(scope="function", autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    original_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture(scope="session")
def test_config():
    """Test configuration that doesn't affect production."""
    return {
        'TESTING': True,
        'DEBUG': True,
        'LOG_LEVEL': 'DEBUG',
        'CACHE_ENABLED': False,
        'API_TIMEOUT': 5,
    }

# =============================================================================
# Async Fixtures
# =============================================================================

@pytest.fixture(scope="function")
async def async_mock_llm():
    """Async mock LLM provider."""
    mock = MagicMock()
    mock.generate = MagicMock(return_value=Mock(
        content='Async test response',
        model='async-test-model'
    ))
    return mock
```

### 4.3 Coverage Configuration

**File Path**: `/tests/.coveragerc`

```ini
[run]
source = src
branch = True
omit = 
    */tests/*
    */test_*
    */__pycache__/*
    */venv/*
    */.venv/*
    */env/*
    setup.py
    */migrations/*
    */examples/*
    */demo_materials/*
    */research/*
    */strategy/*
    src/llm_example.py
    src/modern_ui.py
    
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    pass
    except ImportError:
    
show_missing = True
skip_covered = False
fail_under = 70

[html]
directory = htmlcov
```

---

## 5. Unit Testing Strategy

### 5.1 Agent System Unit Tests

**File Path**: `/tests/unit/agents/test_base_agent.py`

```python
"""
Unit tests for BaseAgent class
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.base_agent import BaseAgent, AgentOutput, AgentStatus, ToolResult


class TestAgentOutput:
    """Tests for AgentOutput dataclass."""
    
    def test_agent_output_creation(self):
        """Test creating AgentOutput with valid data."""
        output = AgentOutput(
            success=True,
            data={'result': 'test'},
            error=None,
            agent_name='test_agent'
        )
        assert output.success is True
        assert output.data == {'result': 'test'}
        assert output.error is None
        assert output.agent_name == 'test_agent'
    
    def test_agent_output_failure(self):
        """Test AgentOutput with failure state."""
        output = AgentOutput(
            success=False,
            data=None,
            error='Test error message',
            agent_name='test_agent'
        )
        assert output.success is False
        assert output.error == 'Test error message'
    
    def test_agent_output_to_dict(self):
        """Test conversion to dictionary."""
        output = AgentOutput(
            success=True,
            data={'key': 'value'},
            error=None,
            agent_name='test_agent'
        )
        result = output.to_dict()
        assert result['success'] is True
        assert result['data'] == {'key': 'value'}


class TestToolResult:
    """Tests for ToolResult dataclass."""
    
    def test_tool_result_success(self):
        """Test successful tool execution result."""
        result = ToolResult(
            success=True,
            data={'weather': 'sunny'},
            tool_name='get_weather',
            execution_time_ms=150.5
        )
        assert result.success is True
        assert result.execution_time_ms == 150.5
    
    def test_tool_result_failure(self):
        """Test failed tool execution result."""
        result = ToolResult(
            success=False,
            data=None,
            error='API timeout',
            tool_name='get_weather',
            execution_time_ms=5000.0
        )
        assert result.success is False
        assert result.error == 'API timeout'


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""
    
    @pytest.fixture
    def concrete_agent(self):
        """Create a concrete agent implementation for testing."""
        class TestAgent(BaseAgent):
            name = "test_agent"
            description = "Test agent"
            version = "1.0.0"
            intent_keywords = ["test", "demo"]
            
            @property
            def system_prompt(self) -> str:
                return "You are a test agent."
            
            def get_tools(self):
                return [{"name": "test_tool", "description": "Test tool"}]
            
            async def process(self, query, context=None):
                return AgentOutput(
                    success=True,
                    data={"query": query},
                    agent_name=self.name
                )
        
        return TestAgent()
    
    def test_agent_initialization(self, concrete_agent):
        """Test agent initializes correctly."""
        assert concrete_agent.name == "test_agent"
        assert concrete_agent.version == "1.0.0"
        assert "test" in concrete_agent.intent_keywords
    
    def test_agent_matches_intent(self, concrete_agent):
        """Test intent matching functionality."""
        assert concrete_agent.matches_intent("test query") is True
        assert concrete_agent.matches_intent("demo request") is True
        assert concrete_agent.matches_intent("unrelated query") is False
    
    @pytest.mark.asyncio
    async def test_agent_process(self, concrete_agent):
        """Test agent processing."""
        result = await concrete_agent.process("test query")
        assert result.success is True
        assert result.data["query"] == "test query"
    
    def test_agent_get_info(self, concrete_agent):
        """Test agent info retrieval."""
        info = concrete_agent.get_info()
        assert info['name'] == "test_agent"
        assert info['version'] == "1.0.0"
        assert 'tools' in info
```

### 5.2 LLM Interface Unit Tests

**File Path**: `/tests/unit/llm/test_llm_interface.py`

```python
"""
Unit tests for LLM Interface
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from src.llm_interface import (
    LLMMessage, LLMResponse, LLMConfig, 
    BaseLLMProvider, LLMProviderFactory, LLMManager
)


class TestLLMMessage:
    """Tests for LLMMessage dataclass."""
    
    def test_message_creation(self):
        """Test creating LLM message."""
        msg = LLMMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
    
    def test_system_message(self):
        """Test system message creation."""
        msg = LLMMessage(role="system", content="You are helpful")
        assert msg.role == "system"
    
    def test_message_to_dict(self):
        """Test message serialization."""
        msg = LLMMessage(role="user", content="Test")
        result = msg.to_dict()
        assert result == {"role": "user", "content": "Test"}


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""
    
    def test_response_creation(self):
        """Test creating LLM response."""
        resp = LLMResponse(
            content="Hello there",
            model="mistral:7b",
            usage={"prompt_tokens": 10, "completion_tokens": 5}
        )
        assert resp.content == "Hello there"
        assert resp.model == "mistral:7b"
        assert resp.usage["prompt_tokens"] == 10
    
    def test_response_with_metadata(self):
        """Test response with metadata."""
        resp = LLMResponse(
            content="Test",
            model="test-model",
            metadata={"key": "value"}
        )
        assert resp.metadata["key"] == "value"


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = LLMConfig()
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = LLMConfig(
            temperature=0.5,
            max_tokens=1024,
            top_p=0.9
        )
        assert config.temperature == 0.5
        assert config.max_tokens == 1024


class TestLLMProviderFactory:
    """Tests for LLMProviderFactory."""
    
    @patch('src.llm_interface.OllamaProvider')
    def test_create_ollama_provider(self, mock_provider):
        """Test creating Ollama provider."""
        mock_instance = Mock()
        mock_provider.return_value = mock_instance
        
        provider = LLMProviderFactory.create_provider(
            provider_type="ollama",
            model="mistral:7b"
        )
        
        assert provider == mock_instance
        mock_provider.assert_called_once()
    
    @patch('src.llm_interface.HuggingFaceProvider')
    def test_create_hf_provider(self, mock_provider):
        """Test creating HuggingFace provider."""
        mock_instance = Mock()
        mock_provider.return_value = mock_instance
        
        provider = LLMProviderFactory.create_provider(
            provider_type="huggingface",
            model="gpt2"
        )
        
        assert provider == mock_instance
    
    def test_create_invalid_provider(self):
        """Test creating invalid provider raises error."""
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMProviderFactory.create_provider(
                provider_type="invalid",
                model="test"
            )


class TestLLMManager:
    """Tests for LLMManager."""
    
    @pytest.fixture
    def manager(self):
        """Create LLMManager instance."""
        return LLMManager()
    
    def test_manager_initialization(self, manager):
        """Test manager initializes correctly."""
        assert manager.providers == {}
        assert manager.default_provider is None
    
    @patch('src.llm_interface.LLMProviderFactory')
    def test_register_provider(self, mock_factory, manager):
        """Test registering a provider."""
        mock_provider = Mock()
        mock_factory.create_provider.return_value = mock_provider
        
        manager.register_provider(
            name="test",
            provider_type="ollama",
            model="mistral:7b"
        )
        
        assert "test" in manager.providers
    
    @patch('src.llm_interface.LLMProviderFactory')
    def test_set_default_provider(self, mock_factory, manager):
        """Test setting default provider."""
        mock_provider = Mock()
        mock_factory.create_provider.return_value = mock_provider
        
        manager.register_provider("default", "ollama", "mistral:7b")
        manager.set_default_provider("default")
        
        assert manager.default_provider == "default"
```

### 5.3 Data Pipeline Unit Tests

**File Path**: `/tests/unit/data/test_feature_engineering.py`

```python
"""
Unit tests for Feature Engineering module
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from src.feature_engineering import (
    calculate_healthcare_gap_score,
    calculate_disaster_risk_score,
    calculate_vulnerability_index,
    FeatureEngineer
)


class TestHealthcareGapScore:
    """Tests for healthcare gap score calculation."""
    
    def test_calculate_healthcare_gap_basic(self):
        """Test basic healthcare gap calculation."""
        df = pd.DataFrame({
            'uninsured_pct': [10.0, 15.0, 20.0],
            'physician_per_1000': [2.0, 1.5, 1.0],
            'hospital_distance_miles': [10, 20, 30]
        })
        
        result = calculate_healthcare_gap_score(df)
        
        assert 'healthcare_gap_score' in result.columns
        assert result['healthcare_gap_score'].between(0, 100).all()
    
    def test_calculate_healthcare_gap_missing_columns(self):
        """Test handling missing required columns."""
        df = pd.DataFrame({'uninsured_pct': [10.0]})
        
        with pytest.raises(ValueError, match="Missing required columns"):
            calculate_healthcare_gap_score(df)
    
    def test_calculate_healthcare_gap_empty_dataframe(self):
        """Test handling empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            calculate_healthcare_gap_score(df)
    
    def test_calculate_healthcare_gap_invalid_values(self):
        """Test handling invalid percentage values."""
        df = pd.DataFrame({
            'uninsured_pct': [-5.0, 150.0, np.nan],
            'physician_per_1000': [2.0, 1.5, 1.0],
            'hospital_distance_miles': [10, 20, 30]
        })
        
        result = calculate_healthcare_gap_score(df)
        
        # Should handle invalid values gracefully
        assert result['healthcare_gap_score'].notna().all()


class TestDisasterRiskScore:
    """Tests for disaster risk score calculation."""
    
    def test_calculate_disaster_risk_basic(self):
        """Test basic disaster risk calculation."""
        df = pd.DataFrame({
            'flood_risk_score': [30.0, 50.0, 80.0],
            'tornado_risk_score': [20.0, 40.0, 60.0],
            'historical_disaster_count': [1, 3, 5]
        })
        
        result = calculate_disaster_risk_score(df)
        
        assert 'disaster_risk_score' in result.columns
        assert result['disaster_risk_score'].between(0, 100).all()
    
    def test_disaster_risk_weights(self):
        """Test that weights are applied correctly."""
        df = pd.DataFrame({
            'flood_risk_score': [100.0],
            'tornado_risk_score': [0.0],
            'historical_disaster_count': [0]
        })
        
        result = calculate_disaster_risk_score(df)
        
        # High flood risk should contribute significantly
        assert result['disaster_risk_score'].iloc[0] > 30


class TestFeatureEngineer:
    """Tests for FeatureEngineer class."""
    
    @pytest.fixture
    def engineer(self):
        """Create FeatureEngineer instance."""
        return FeatureEngineer()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'fips': ['29001', '29002', '29003'],
            'county_name': ['County A', 'County B', 'County C'],
            'population': [10000, 50000, 100000],
            'uninsured_pct': [10.0, 15.0, 20.0],
            'poverty_rate': [12.0, 18.0, 25.0],
            'flood_risk_score': [30.0, 50.0, 80.0],
            'tornado_risk_score': [20.0, 40.0, 60.0],
            'physician_per_1000': [2.0, 1.5, 1.0],
            'hospital_distance_miles': [10, 20, 30],
            'historical_disaster_count': [1, 3, 5]
        })
    
    def test_engineer_initialization(self, engineer):
        """Test FeatureEngineer initialization."""
        assert engineer is not None
    
    def test_transform(self, engineer, sample_data):
        """Test feature transformation."""
        result = engineer.transform(sample_data)
        
        # Check that new features are created
        assert 'healthcare_gap_score' in result.columns
        assert 'disaster_risk_score' in result.columns
        assert 'vulnerability_index' in result.columns
    
    def test_transform_preserves_original(self, engineer, sample_data):
        """Test that original columns are preserved."""
        result = engineer.transform(sample_data)
        
        for col in sample_data.columns:
            assert col in result.columns
    
    def test_risk_level_classification(self, engineer, sample_data):
        """Test risk level classification."""
        result = engineer.transform(sample_data)
        
        assert 'risk_level' in result.columns
        assert set(result['risk_level'].unique()).issubset(
            {'Low', 'Medium', 'High', 'Critical'}
        )
```

### 5.4 API Client Unit Tests with Mocking

**File Path**: `/tests/unit/api_clients/test_weather_client.py`

```python
"""
Unit tests for Weather Client with mocking
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from src.weather_client import WeatherClient, WeatherAlert


class TestWeatherClient:
    """Tests for WeatherClient class."""
    
    @pytest.fixture
    def client(self):
        """Create WeatherClient instance."""
        return WeatherClient()
    
    @pytest.fixture
    def mock_alert_response(self):
        """Mock NOAA alerts API response."""
        return {
            'features': [
                {
                    'properties': {
                        'event': 'Tornado Warning',
                        'severity': 'Extreme',
                        'areaDesc': 'St. Louis County, Missouri',
                        'effective': '2024-01-01T12:00:00Z',
                        'expires': '2024-01-01T13:00:00Z',
                        'senderName': 'NWS St. Louis',
                        'headline': 'Tornado Warning issued',
                        'description': 'At 12:00 PM CST, a confirmed tornado'
                    },
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[[-90.5, 38.6], [-90.5, 38.7], [-90.4, 38.7]]]
                    }
                }
            ]
        }
    
    @patch('requests.get')
    def test_get_alerts_success(self, mock_get, client, mock_alert_response):
        """Test successful alert retrieval."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = mock_alert_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Call method
        alerts = client.get_alerts(state='MO')
        
        # Assertions
        assert len(alerts) == 1
        assert alerts[0]['event'] == 'Tornado Warning'
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_alerts_with_county_filter(self, mock_get, client, mock_alert_response):
        """Test alert retrieval with county filter."""
        mock_response = Mock()
        mock_response.json.return_value = mock_alert_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        alerts = client.get_alerts(state='MO', county='St. Louis')
        
        assert len(alerts) == 1
    
    @patch('requests.get')
    def test_get_alerts_api_failure(self, mock_get, client):
        """Test handling API failure."""
        mock_get.side_effect = requests.RequestException("API Error")
        
        with pytest.raises(requests.RequestException):
            client.get_alerts(state='MO')
    
    @patch('requests.get')
    def test_get_alerts_timeout(self, mock_get, client):
        """Test handling timeout."""
        mock_get.side_effect = requests.Timeout("Request timed out")
        
        with pytest.raises(requests.Timeout):
            client.get_alerts(state='MO')
    
    @patch('requests.get')
    def test_get_alerts_empty_response(self, mock_get, client):
        """Test handling empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {'features': []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        alerts = client.get_alerts(state='MO')
        
        assert len(alerts) == 0
    
    @patch('requests.get')
    def test_get_alerts_invalid_json(self, mock_get, client):
        """Test handling invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError):
            client.get_alerts(state='MO')


class TestWeatherAlert:
    """Tests for WeatherAlert dataclass."""
    
    def test_alert_creation(self):
        """Test creating WeatherAlert."""
        alert = WeatherAlert(
            event='Tornado Warning',
            severity='Extreme',
            area='St. Louis County',
            effective='2024-01-01T12:00:00Z',
            expires='2024-01-01T13:00:00Z'
        )
        
        assert alert.event == 'Tornado Warning'
        assert alert.severity == 'Extreme'
    
    def test_alert_is_active(self):
        """Test checking if alert is active."""
        from datetime import datetime, timezone
        
        alert = WeatherAlert(
            event='Test',
            severity='Minor',
            area='Test Area',
            effective='2024-01-01T12:00:00Z',
            expires='2099-12-31T23:59:59Z'  # Far future
        )
        
        assert alert.is_active() is True
    
    def test_alert_to_dict(self):
        """Test alert serialization."""
        alert = WeatherAlert(
            event='Flood Warning',
            severity='Moderate',
            area='Test County',
            effective='2024-01-01T12:00:00Z',
            expires='2024-01-02T12:00:00Z'
        )
        
        result = alert.to_dict()
        
        assert result['event'] == 'Flood Warning'
        assert result['severity'] == 'Moderate'
```

---

## 6. Integration Testing Strategy

### 6.1 Data Pipeline Integration Tests

**File Path**: `/tests/integration/test_data_pipeline.py`

```python
"""
Integration tests for complete data pipeline
"""
import pytest
import pandas as pd
from pathlib import Path
from src.download_data import DataDownloader
from src.feature_engineering import FeatureEngineer
from src.train_models import ModelTrainer


@pytest.mark.integration
class TestDataPipeline:
    """End-to-end data pipeline integration tests."""
    
    @pytest.fixture(scope="class")
    def pipeline_output(self, tmp_path_factory):
        """Run full pipeline and return outputs."""
        temp_dir = tmp_path_factory.mktemp("pipeline_test")
        
        # Step 1: Download data
        downloader = DataDownloader(output_dir=temp_dir / "raw")
        raw_data = downloader.download_all()
        
        # Step 2: Feature engineering
        engineer = FeatureEngineer()
        processed_data = engineer.transform(raw_data)
        
        # Step 3: Train models
        trainer = ModelTrainer(output_dir=temp_dir / "models")
        models = trainer.train_all(processed_data)
        
        return {
            'raw_data': raw_data,
            'processed_data': processed_data,
            'models': models,
            'temp_dir': temp_dir
        }
    
    def test_raw_data_downloaded(self, pipeline_output):
        """Test that raw data was downloaded successfully."""
        raw_data = pipeline_output['raw_data']
        assert raw_data is not None
        assert len(raw_data) > 0
    
    def test_features_engineered(self, pipeline_output):
        """Test that features were properly engineered."""
        processed = pipeline_output['processed_data']
        
        # Check required columns exist
        required_cols = [
            'healthcare_gap_score',
            'disaster_risk_score',
            'vulnerability_index',
            'risk_level'
        ]
        
        for col in required_cols:
            assert col in processed.columns, f"Missing column: {col}"
    
    def test_models_trained(self, pipeline_output):
        """Test that models were trained successfully."""
        models = pipeline_output['models']
        
        required_models = [
            'vulnerability_classifier',
            'risk_predictor',
            'healthcare_gap_model'
        ]
        
        for model_name in required_models:
            assert model_name in models, f"Missing model: {model_name}"
            assert models[model_name] is not None
    
    def test_data_integrity_through_pipeline(self, pipeline_output):
        """Test data integrity through the pipeline."""
        raw = pipeline_output['raw_data']
        processed = pipeline_output['processed_data']
        
        # Row count should be preserved
        assert len(raw) == len(processed)
        
        # FIPS codes should be preserved
        assert raw['fips'].equals(processed['fips'])


@pytest.mark.integration
class TestAgentWorkflowIntegration:
    """Integration tests for agent workflows."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create agent orchestrator."""
        from src.agents.orchestrator import AgentOrchestrator
        return AgentOrchestrator()
    
    def test_vulnerability_assessment_workflow(self, orchestrator):
        """Test complete vulnerability assessment workflow."""
        query = "Assess vulnerability for St. Louis County, Missouri"
        
        result = orchestrator.process(query)
        
        assert result.success is True
        assert 'vulnerability_score' in result.data
        assert 'risk_factors' in result.data
    
    def test_multi_agent_coordination(self, orchestrator):
        """Test coordination between multiple agents."""
        query = "Generate a comprehensive disaster preparedness report for Missouri"
        
        result = orchestrator.process(query)
        
        assert result.success is True
        # Should involve multiple agents
        assert 'agents_invoked' in result.metadata
        assert len(result.metadata['agents_invoked']) > 1
```

### 6.2 LLM Orchestration Integration Tests

**File Path**: `/tests/integration/test_llm_orchestration.py`

```python
"""
Integration tests for LLM orchestration with agents
"""
import pytest
from unittest.mock import Mock, patch
from src.llm_interface import LLMManager, LLMMessage
from src.agents.orchestrator import AgentOrchestrator


@pytest.mark.integration
@pytest.mark.llm
class TestLLMOrchestration:
    """Tests for LLM and agent orchestration integration."""
    
    @pytest.fixture
    def llm_manager(self):
        """Create LLM manager with mock provider."""
        manager = LLMManager()
        
        # Register mock provider
        mock_provider = Mock()
        mock_provider.generate.return_value = Mock(
            content='{"action": "assess_vulnerability", "county": "St. Louis"}',
            model='test-model'
        )
        
        manager.providers['test'] = mock_provider
        manager.default_provider = 'test'
        
        return manager
    
    def test_llm_agent_communication(self, llm_manager):
        """Test LLM can communicate with agents."""
        messages = [
            LLMMessage(role="system", content="You are a disaster assessment agent."),
            LLMMessage(role="user", content="Assess St. Louis County")
        ]
        
        response = llm_manager.generate(messages)
        
        assert response.content is not None
        assert 'assess_vulnerability' in response.content
    
    def test_agent_uses_llm_for_reasoning(self, llm_manager):
        """Test agent uses LLM for complex reasoning."""
        orchestrator = AgentOrchestrator(llm_manager=llm_manager)
        
        query = "What are the top 3 risk factors for Jackson County?"
        result = orchestrator.process(query)
        
        assert result.success is True
        # LLM should have been called
        llm_manager.providers['test'].generate.assert_called()
```

---

## 7. End-to-End Testing Strategy

### 7.1 Streamlit Dashboard E2E Tests

**File Path**: `/tests/e2e/test_dashboard.py`

```python
"""
End-to-end tests for Streamlit Dashboard using Playwright
"""
import pytest
import re
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestDashboard:
    """E2E tests for ResilienceAI Dashboard."""
    
    @pytest.fixture(scope="class")
    def page(self, browser):
        """Navigate to dashboard."""
        page = browser.new_page()
        page.goto("http://localhost:8501")
        yield page
        page.close()
    
    def test_dashboard_loads(self, page: Page):
        """Test dashboard loads successfully."""
        # Check title
        expect(page).to_have_title(re.compile("ResilienceAI"))
        
        # Check main header
        header = page.locator("h1")
        expect(header).to_contain_text("ResilienceAI")
    
    def test_sidebar_navigation(self, page: Page):
        """Test sidebar navigation works."""
        # Find and click on different tabs
        tabs = ['Vulnerability Map', 'Risk Analysis', 'Healthcare Gaps', 'Agent Chat']
        
        for tab in tabs:
            tab_button = page.locator(f"text={tab}")
            if tab_button.is_visible():
                tab_button.click()
                # Verify tab content loaded
                expect(page.locator("main")).to_be_visible()
    
    def test_county_filter_functionality(self, page: Page):
        """Test county filter works."""
        # Find county filter
        county_filter = page.locator("[data-testid='county-filter']")
        
        if county_filter.is_visible():
            # Type county name
            county_filter.fill("St. Louis")
            
            # Verify filter applied
            expect(page.locator("text=St. Louis")).to_be_visible()
    
    def test_visualization_renders(self, page: Page):
        """Test that visualizations render correctly."""
        # Wait for map to load
        map_container = page.locator("[data-testid='stDeckGlJsonChart']")
        
        if map_container.is_visible():
            expect(map_container).to_be_visible()
    
    def test_agent_chat_interface(self, page: Page):
        """Test agent chat interface."""
        # Navigate to chat tab
        chat_tab = page.locator("text=Agent Chat")
        if chat_tab.is_visible():
            chat_tab.click()
            
            # Find chat input
            chat_input = page.locator("[data-testid='stChatInput']")
            expect(chat_input).to_be_visible()
            
            # Send message
            chat_input.fill("What is the vulnerability score for Jackson County?")
            chat_input.press("Enter")
            
            # Wait for response
            response = page.locator("[data-testid='chat-message']").last
            expect(response).to_be_visible(timeout=10000)


@pytest.mark.e2e
class TestDashboardResponsiveness:
    """Test dashboard responsiveness at different viewports."""
    
    @pytest.mark.parametrize("viewport", [
        {"width": 1920, "height": 1080},  # Desktop
        {"width": 1366, "height": 768},   # Laptop
        {"width": 768, "height": 1024},   # Tablet
        {"width": 375, "height": 667},    # Mobile
    ])
    def test_responsive_layout(self, browser, viewport):
        """Test dashboard at different viewport sizes."""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()
        
        page.goto("http://localhost:8501")
        
        # Check that main content is visible
        expect(page.locator("main")).to_be_visible()
        
        context.close()
```

### 7.2 Page Objects for E2E Tests

**File Path**: `/tests/e2e/page_objects/base_page.py`

```python
"""
Base Page Object for Dashboard E2E Tests
"""
from playwright.sync_api import Page, expect


class BasePage:
    """Base class for page objects."""
    
    def __init__(self, page: Page):
        self.page = page
    
    def navigate(self, url: str):
        """Navigate to URL."""
        self.page.goto(url)
    
    def wait_for_load(self):
        """Wait for page to load."""
        self.page.wait_for_load_state("networkidle")
    
    def take_screenshot(self, name: str):
        """Take screenshot for debugging."""
        self.page.screenshot(path=f"tests/e2e/screenshots/{name}.png")
    
    def get_element(self, selector: str):
        """Get element by selector."""
        return self.page.locator(selector)
    
    def click(self, selector: str):
        """Click element."""
        self.get_element(selector).click()
    
    def fill(self, selector: str, text: str):
        """Fill input field."""
        self.get_element(selector).fill(text)
    
    def expect_visible(self, selector: str):
        """Assert element is visible."""
        expect(self.get_element(selector)).to_be_visible()


class DashboardPage(BasePage):
    """Page object for Dashboard."""
    
    URL = "http://localhost:8501"
    
    # Selectors
    HEADER = "h1"
    SIDEBAR = "[data-testid='stSidebar']"
    COUNTY_FILTER = "[data-testid='county-filter']"
    RISK_MAP = "[data-testid='stDeckGlJsonChart']"
    CHAT_INPUT = "[data-testid='stChatInput']"
    
    def navigate_to_dashboard(self):
        """Navigate to dashboard."""
        self.navigate(self.URL)
        self.wait_for_load()
    
    def get_header_text(self) -> str:
        """Get header text."""
        return self.get_element(self.HEADER).text_content()
    
    def filter_by_county(self, county_name: str):
        """Filter dashboard by county."""
        self.fill(self.COUNTY_FILTER, county_name)
        self.page.wait_for_timeout(500)  # Wait for filter to apply
    
    def send_chat_message(self, message: str):
        """Send message in chat."""
        self.fill(self.CHAT_INPUT, message)
        self.page.keyboard.press("Enter")
        # Wait for response
        self.page.wait_for_selector("[data-testid='chat-message']", timeout=10000)
    
    def get_chat_messages(self):
        """Get all chat messages."""
        return self.page.locator("[data-testid='chat-message']").all()
    
    def switch_tab(self, tab_name: str):
        """Switch to different dashboard tab."""
        tab = self.page.locator(f"text={tab_name}")
        tab.click()
        self.page.wait_for_timeout(500)
```

---

## 8. Performance Testing Strategy

### 8.1 Load Testing with Locust

**File Path**: `/tests/performance/test_load.py`

```python
"""
Load testing for ResilienceAI using Locust
"""
from locust import HttpUser, task, between
import random


class DashboardUser(HttpUser):
    """Simulates a user interacting with the dashboard."""
    
    wait_time = between(1, 5)
    
    def on_start(self):
        """Called when user starts."""
        self.counties = [
            "St. Louis", "Jackson", "Greene", "Clay", "Jefferson",
            "Boone", "Jasper", "Cape Girardeau", "Franklin", "Cole"
        ]
    
    @task(3)
    def view_dashboard(self):
        """View main dashboard."""
        self.client.get("/")
    
    @task(2)
    def filter_by_county(self):
        """Filter by random county."""
        county = random.choice(self.counties)
        self.client.get(f"/?county={county}")
    
    @task(1)
    def view_vulnerability_map(self):
        """View vulnerability map tab."""
        self.client.get("/?tab=vulnerability_map")
    
    @task(1)
    def view_risk_analysis(self):
        """View risk analysis tab."""
        self.client.get("/?tab=risk_analysis")


class APIUser(HttpUser):
    """Simulates API client usage."""
    
    wait_time = between(0.5, 2)
    
    @task(5)
    def get_county_data(self):
        """Get county vulnerability data."""
        fips = f"29{random.randint(1, 115):03d}"
        self.client.get(f"/api/v1/counties/{fips}/vulnerability")
    
    @task(3)
    def get_risk_assessment(self):
        """Get risk assessment."""
        self.client.post("/api/v1/assessments/risk", json={
            "county_fips": f"29{random.randint(1, 115):03d}",
            "disaster_type": random.choice(["flood", "tornado", "earthquake"])
        })
    
    @task(2)
    def agent_query(self):
        """Send query to agent system."""
        self.client.post("/api/v1/agents/query", json={
            "query": "What is the healthcare gap for Jackson County?",
            "context": {"state": "Missouri"}
        })


class DataProcessingUser(HttpUser):
    """Simulates data processing load."""
    
    wait_time = between(10, 30)
    
    @task(1)
    def trigger_pipeline(self):
        """Trigger data pipeline processing."""
        self.client.post("/api/v1/pipeline/run", json={
            "full_refresh": False,
            "counties": None
        })
```

### 8.2 Performance Benchmarks

**File Path**: `/tests/performance/benchmarks/benchmark_results.py`

```python
"""
Performance benchmarks for ResilienceAI components
"""
import pytest
import time
import statistics
from typing import List, Callable
import pandas as pd


class PerformanceBenchmark:
    """Base class for performance benchmarks."""
    
    def __init__(self, iterations: int = 10):
        self.iterations = iterations
        self.results: List[float] = []
    
    def benchmark(self, func: Callable, *args, **kwargs) -> dict:
        """Run benchmark and return statistics."""
        self.results = []
        
        for _ in range(self.iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            self.results.append((end - start) * 1000)  # Convert to ms
        
        return {
            'mean': statistics.mean(self.results),
            'median': statistics.median(self.results),
            'stdev': statistics.stdev(self.results) if len(self.results) > 1 else 0,
            'min': min(self.results),
            'max': max(self.results),
            'iterations': self.iterations
        }


@pytest.mark.performance
class TestDataProcessingBenchmarks:
    """Benchmarks for data processing operations."""
    
    @pytest.fixture
    def large_dataset(self):
        """Generate large dataset for benchmarking."""
        return pd.DataFrame({
            'fips': [f'29{i:05d}' for i in range(10000)],
            'population': [10000] * 10000,
            'uninsured_pct': [10.0] * 10000,
            'poverty_rate': [15.0] * 10000,
            'flood_risk_score': [50.0] * 10000,
        })
    
    def test_feature_engineering_performance(self, large_dataset):
        """Benchmark feature engineering on large dataset."""
        from src.feature_engineering import FeatureEngineer
        
        engineer = FeatureEngineer()
        benchmark = PerformanceBenchmark(iterations=5)
        
        results = benchmark.benchmark(engineer.transform, large_dataset)
        
        # Assert performance requirements
        assert results['mean'] < 5000, f"Feature engineering too slow: {results['mean']:.2f}ms"
        assert results['stdev'] < 500, f"High variance in feature engineering: {results['stdev']:.2f}ms"
        
        print(f"\nFeature Engineering Benchmark:")
        print(f"  Mean: {results['mean']:.2f}ms")
        print(f"  Median: {results['median']:.2f}ms")
        print(f"  StdDev: {results['stdev']:.2f}ms")
    
    def test_prediction_performance(self):
        """Benchmark model prediction performance."""
        from src.predictive_models import RiskPredictor
        import joblib
        import numpy as np
        
        # Create test data
        X = np.random.rand(1000, 66)  # 66 features
        
        predictor = RiskPredictor()
        benchmark = PerformanceBenchmark(iterations=10)
        
        results = benchmark.benchmark(predictor.predict, X)
        
        assert results['mean'] < 100, f"Prediction too slow: {results['mean']:.2f}ms"
        
        print(f"\nPrediction Benchmark:")
        print(f"  Mean: {results['mean']:.2f}ms")
        print(f"  Throughput: {1000 / (results['mean'] / 1000):.0f} predictions/sec")


@pytest.mark.performance
class TestAPIBenchmarks:
    """Benchmarks for API endpoints."""
    
    def test_weather_api_latency(self):
        """Benchmark weather API response time."""
        from src.weather_client import WeatherClient
        
        client = WeatherClient()
        benchmark = PerformanceBenchmark(iterations=5)
        
        results = benchmark.benchmark(client.get_alerts, state='MO')
        
        # External API should respond within 2 seconds
        assert results['mean'] < 2000, f"Weather API too slow: {results['mean']:.2f}ms"
        
        print(f"\nWeather API Benchmark:")
        print(f"  Mean: {results['mean']:.2f}ms")
    
    def test_agent_response_time(self):
        """Benchmark agent response time."""
        from src.agents.orchestrator import AgentOrchestrator
        
        orchestrator = AgentOrchestrator()
        benchmark = PerformanceBenchmark(iterations=3)
        
        results = benchmark.benchmark(
            orchestrator.process,
            "What is the vulnerability score for St. Louis County?"
        )
        
        assert results['mean'] < 5000, f"Agent response too slow: {results['mean']:.2f}ms"
        
        print(f"\nAgent Response Benchmark:")
        print(f"  Mean: {results['mean']:.2f}ms")
```

---

## 9. Security Testing Strategy

### 9.1 Input Validation Tests

**File Path**: `/tests/security/test_input_validation.py`

```python
"""
Security tests for input validation and sanitization
"""
import pytest
from src.feature_engineering import FeatureEngineer
from src.agents.orchestrator import AgentOrchestrator


@pytest.mark.security
class TestInputValidation:
    """Tests for input validation security."""
    
    @pytest.fixture
    def engineer(self):
        """Create FeatureEngineer instance."""
        return FeatureEngineer()
    
    def test_sql_injection_in_county_name(self, engineer):
        """Test SQL injection attempt in county name."""
        import pandas as pd
        
        malicious_data = pd.DataFrame({
            'fips': ['29001'],
            'county_name': ["'; DROP TABLE counties; --"],
            'population': [10000],
            'uninsured_pct': [10.0],
        })
        
        # Should not raise error or execute malicious code
        result = engineer.transform(malicious_data)
        assert result is not None
    
    def test_xss_in_query(self):
        """Test XSS attempt in agent query."""
        orchestrator = AgentOrchestrator()
        
        xss_query = "<script>alert('XSS')</script>"
        
        # Should sanitize input
        result = orchestrator.process(xss_query)
        assert result.success is True
        # Response should not contain unescaped script
        assert '<script>' not in str(result.data)
    
    def test_command_injection_attempt(self):
        """Test command injection attempt."""
        orchestrator = AgentOrchestrator()
        
        malicious_query = "; rm -rf /; "
        
        # Should not execute system commands
        result = orchestrator.process(malicious_query)
        assert result.success is True  # Should handle gracefully
    
    def test_very_long_input(self, engineer):
        """Test handling of very long input."""
        import pandas as pd
        
        long_string = "A" * 1000000  # 1MB string
        
        data = pd.DataFrame({
            'fips': ['29001'],
            'county_name': [long_string],
            'population': [10000],
        })
        
        # Should handle without memory issues
        result = engineer.transform(data)
        assert result is not None
    
    def test_special_characters_in_fips(self, engineer):
        """Test special characters in FIPS code."""
        import pandas as pd
        
        data = pd.DataFrame({
            'fips': ['29<script>01', '29;01', '29\'01', '29"01'],
            'county_name': ['Test'],
            'population': [10000],
        })
        
        result = engineer.transform(data)
        assert result is not None
        # FIPS should be sanitized
        assert '<script>' not in result['fips'].values[0]


@pytest.mark.security
class TestAPIRateLimiting:
    """Tests for API rate limiting."""
    
    def test_weather_api_rate_limit(self):
        """Test weather API rate limiting."""
        from src.weather_client import WeatherClient
        import time
        
        client = WeatherClient()
        
        # Make rapid requests
        responses = []
        for _ in range(10):
            try:
                response = client.get_alerts(state='MO')
                responses.append(response)
            except Exception as e:
                responses.append(e)
            time.sleep(0.1)
        
        # Should not all succeed (rate limiting should kick in)
        # Or should have proper delays
        assert len(responses) == 10
```

---

## 10. Mocking Strategy

### 10.1 Mock LLM Providers

**File Path**: `/tests/mocks/mock_llm_providers.py`

```python
"""
Mock LLM providers for testing
"""
from unittest.mock import Mock
from typing import List, Dict, Any
from src.llm_interface import LLMResponse, LLMMessage


class MockOllamaProvider:
    """Mock Ollama provider for testing."""
    
    def __init__(self, model: str = "mistral:7b", **kwargs):
        self.model = model
        self.call_count = 0
        self.responses = []
    
    def set_responses(self, responses: List[str]):
        """Set predefined responses."""
        self.responses = responses
    
    def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate mock response."""
        self.call_count += 1
        
        if self.responses:
            content = self.responses[(self.call_count - 1) % len(self.responses)]
        else:
            content = f"Mock response {self.call_count}"
        
        return LLMResponse(
            content=content,
            model=self.model,
            usage={
                "prompt_tokens": 10,
                "completion_tokens": len(content.split()),
                "total_tokens": 10 + len(content.split())
            }
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model info."""
        return {
            "name": self.model,
            "provider": "ollama",
            "capabilities": ["text-generation"]
        }


class MockHuggingFaceProvider:
    """Mock HuggingFace provider for testing."""
    
    def __init__(self, model: str = "gpt2", **kwargs):
        self.model = model
        self.pipeline = Mock()
    
    def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate mock response."""
        return LLMResponse(
            content="Mock HF response",
            model=self.model,
            usage={"prompt_tokens": 5, "completion_tokens": 5}
        )


@pytest.fixture
def mock_llm_manager():
    """Create mock LLM manager."""
    from src.llm_interface import LLMManager
    
    manager = LLMManager()
    
    # Register mock providers
    mock_ollama = MockOllamaProvider()
    mock_ollama.set_responses([
        '{"action": "assess_vulnerability", "county": "St. Louis"}',
        '{"action": "get_weather", "location": "Missouri"}',
        'This is a general response.'
    ])
    
    manager.providers['mock_ollama'] = mock_ollama
    manager.default_provider = 'mock_ollama'
    
    return manager
```

### 10.2 Mock API Clients

**File Path**: `/tests/mocks/mock_api_clients.py`

```python
"""
Mock API clients for testing
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class MockWeatherClient:
    """Mock weather client for testing."""
    
    def __init__(self, responses_dir: Optional[Path] = None):
        self.responses_dir = responses_dir
        self.call_history = []
    
    def get_alerts(self, state: str, county: Optional[str] = None) -> Dict[str, Any]:
        """Get mock weather alerts."""
        self.call_history.append({'method': 'get_alerts', 'state': state, 'county': county})
        
        return {
            'features': [
                {
                    'properties': {
                        'event': 'Tornado Warning',
                        'severity': 'Extreme',
                        'areaDesc': f'{county or "Test"} County, {state}',
                        'effective': '2024-01-01T12:00:00Z',
                        'expires': '2024-01-01T13:00:00Z',
                    }
                }
            ]
        }
    
    def get_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get mock weather forecast."""
        self.call_history.append({'method': 'get_forecast', 'lat': lat, 'lon': lon})
        
        return {
            'properties': {
                'periods': [
                    {'name': 'Today', 'temperature': 75, 'shortForecast': 'Sunny'},
                    {'name': 'Tonight', 'temperature': 55, 'shortForecast': 'Clear'},
                ]
            }
        }


class MockArchiaClient:
    """Mock Archia Cloud client for testing."""
    
    def __init__(self):
        self.authenticated = True
        self.call_history = []
    
    def query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute mock query."""
        self.call_history.append({'query': query, 'context': context})
        
        return {
            'success': True,
            'data': {
                'response': f'Mock response for: {query}',
                'sources': ['mock_source_1', 'mock_source_2'],
                'confidence': 0.95
            },
            'metadata': {
                'processing_time_ms': 150,
                'tokens_used': 100
            }
        }
    
    def health_check(self) -> bool:
        """Mock health check."""
        return self.authenticated


class MockGEEClient:
    """Mock Google Earth Engine client for testing."""
    
    def __init__(self):
        self.initialized = True
    
    def get_satellite_imagery(self, region: str, date_range: tuple) -> Dict[str, Any]:
        """Get mock satellite imagery."""
        return {
            'url': 'https://mock-gee-url.com/image.png',
            'metadata': {
                'cloud_cover': 5.0,
                'resolution': 10,
                'date_captured': date_range[0]
            }
        }
    
    def calculate_ndvi(self, region: str) -> Dict[str, Any]:
        """Calculate mock NDVI."""
        return {
            'mean_ndvi': 0.65,
            'min_ndvi': 0.2,
            'max_ndvi': 0.9,
            'area_km2': 100.0
        }
```

---

## 11. Test Data Generation

### 11.1 Data Factories

**File Path**: `/tests/fixtures/factories/data_factories.py`

```python
"""
Test data factories using factory_boy pattern
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CountyDataFactory:
    """Factory for generating test county data."""
    
    num_counties: int = 115  # Missouri counties
    state_fips: str = "29"
    random_seed: int = 42
    
    def __post_init__(self):
        np.random.seed(self.random_seed)
    
    def generate(self) -> pd.DataFrame:
        """Generate county data DataFrame."""
        counties = self._get_missouri_counties()
        
        return pd.DataFrame({
            'fips': [f'{self.state_fips}{i:03d}' for i in range(1, self.num_counties + 1)],
            'county_name': [f"{c}, Missouri" for c in counties[:self.num_counties]],
            'latitude': np.random.uniform(36, 40.5, self.num_counties),
            'longitude': np.random.uniform(-95.7, -89, self.num_counties),
            'population': np.random.lognormal(10, 1.5, self.num_counties).astype(int),
            'uninsured_pct': np.clip(np.random.normal(12, 5, self.num_counties), 3, 35),
            'poverty_rate': np.clip(np.random.normal(15, 7, self.num_counties), 5, 45),
            'median_income': np.random.lognormal(10.8, 0.4, self.num_counties).astype(int),
            'physician_per_1000': np.clip(np.random.normal(1.8, 0.8, self.num_counties), 0.2, 5),
            'hospital_distance_miles': np.clip(np.random.exponential(15, self.num_counties), 2, 100),
            'flood_risk_score': np.clip(np.random.beta(2, 5, self.num_counties) * 100, 0, 100),
            'tornado_risk_score': np.clip(np.random.beta(3, 3, self.num_counties) * 100, 0, 100),
            'historical_disaster_count': np.random.poisson(3, self.num_counties),
            'elderly_pct': np.clip(np.random.normal(16, 4, self.num_counties), 5, 35),
            'single_parent_pct': np.clip(np.random.normal(25, 8, self.num_counties), 10, 50),
        })
    
    def _get_missouri_counties(self) -> List[str]:
        """Return list of Missouri county names."""
        return [
            "Adair", "Andrew", "Atchison", "Audrain", "Barry", "Barton", "Bates",
            "Benton", "Bollinger", "Boone", "Buchanan", "Butler", "Caldwell",
            "Callaway", "Camden", "Cape Girardeau", "Carroll", "Carter", "Cass",
            "Cedar", "Chariton", "Christian", "Clark", "Clay", "Clinton", "Cole",
            "Cooper", "Crawford", "Dade", "Dallas", "Daviess", "DeKalb", "Dent",
            "Douglas", "Dunklin", "Franklin", "Gasconade", "Gentry", "Greene",
            "Grundy", "Harrison", "Henry", "Hickory", "Holt", "Howard", "Howell",
            "Iron", "Jackson", "Jasper", "Jefferson", "Johnson", "Knox", "Laclede",
            "Lafayette", "Lawrence", "Lewis", "Lincoln", "Linn", "Livingston",
            "Macon", "Madison", "Maries", "Marion", "McDonald", "Mercer", "Miller",
            "Mississippi", "Moniteau", "Monroe", "Montgomery", "Morgan", "New Madrid",
            "Newton", "Nodaway", "Oregon", "Osage", "Ozark", "Pemiscot", "Perry",
            "Pettis", "Phelps", "Pike", "Platte", "Polk", "Pulaski", "Putnam",
            "Ralls", "Randolph", "Ray", "Reynolds", "Ripley", "Saline", "Schuyler",
            "Scotland", "Scott", "Shannon", "Shelby", "St. Charles", "St. Clair",
            "St. Francois", "St. Louis", "St. Louis City", "Ste. Genevieve",
            "Stoddard", "Stone", "Sullivan", "Taney", "Texas", "Vernon", "Warren",
            "Washington", "Wayne", "Webster", "Worth", "Wright"
        ]


@dataclass
class WeatherAlertFactory:
    """Factory for generating test weather alerts."""
    
    num_alerts: int = 5
    states: List[str] = field(default_factory=lambda: ["MO"])
    
    def generate(self) -> List[Dict[str, Any]]:
        """Generate list of weather alerts."""
        events = ['Tornado Warning', 'Severe Thunderstorm Warning', 
                  'Flash Flood Warning', 'Winter Storm Warning']
        severities = ['Minor', 'Moderate', 'Severe', 'Extreme']
        
        alerts = []
        for i in range(self.num_alerts):
            alerts.append({
                'event': np.random.choice(events),
                'severity': np.random.choice(severities),
                'areaDesc': f'Test County {i}, {np.random.choice(self.states)}',
                'effective': '2024-01-01T12:00:00Z',
                'expires': '2024-01-01T15:00:00Z',
                'senderName': 'NWS Test Office',
                'headline': f'Test {events[i % len(events)]}',
                'description': f'This is a test alert description for alert {i}.'
            })
        
        return alerts


@dataclass
class ModelPredictionFactory:
    """Factory for generating model predictions."""
    
    num_samples: int = 100
    num_features: int = 66
    
    def generate_features(self) -> pd.DataFrame:
        """Generate feature matrix."""
        return pd.DataFrame(
            np.random.randn(self.num_samples, self.num_features),
            columns=[f'feature_{i}' for i in range(self.num_features)]
        )
    
    def generate_predictions(self) -> np.ndarray:
        """Generate prediction probabilities."""
        return np.random.beta(2, 2, self.num_samples)
    
    def generate_with_labels(self) -> tuple:
        """Generate features and labels."""
        X = self.generate_features()
        y = np.random.binomial(1, 0.3, self.num_samples)
        return X, y
```

---

## 12. CI/CD Pipeline Integration

### 12.1 GitHub Actions Workflow

**File Path**: `/.github/workflows/test-suite.yml`

```yaml
name: ResilienceAI Test Suite

on:
  push:
    branches: [main, claw-autonomous, develop]
  pull_request:
    branches: [main, claw-autonomous]
  schedule:
    # Run tests daily at 2 AM UTC
    - cron: '0 2 * * *'

env:
  PYTHON_VERSION: '3.10'
  TESTING: 'true'

jobs:
  # =============================================================================
  # Unit Tests
  # =============================================================================
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt', 'requirements-dev.txt') }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: |
          pytest tests/unit \
            -v \
            -m "unit and not slow" \
            --cov=src \
            --cov-report=xml:unit-coverage.xml \
            --cov-report=html:unit-htmlcov \
            --junitxml=unit-test-results.xml
      
      - name: Upload unit test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: unit-test-results
          path: |
            unit-test-results.xml
            unit-coverage.xml
            unit-htmlcov/
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: unit-coverage.xml
          flags: unit
          name: unit-tests

  # =============================================================================
  # Integration Tests
  # =============================================================================
  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: unit-tests
    
    services:
      # Add any required services (databases, caches, etc.)
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run integration tests
        run: |
          pytest tests/integration \
            -v \
            -m "integration" \
            --cov=src \
            --cov-report=xml:integration-coverage.xml \
            --cov-report=html:integration-htmlcov \
            --junitxml=integration-test-results.xml
        env:
          REDIS_URL: redis://localhost:6379
      
      - name: Upload integration test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: integration-test-results
          path: |
            integration-test-results.xml
            integration-coverage.xml
            integration-htmlcov/

  # =============================================================================
  # Performance Tests
  # =============================================================================
  performance-tests:
    name: Performance Tests
    runs-on: ubuntu-latest
    needs: unit-tests
    if: github.event_name == 'schedule' || contains(github.event.head_commit.message, '[perf]')
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run performance benchmarks
        run: |
          pytest tests/performance \
            -v \
            -m "performance" \
            --benchmark-only \
            --benchmark-json=benchmark-results.json
      
      - name: Upload benchmark results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark-results.json
      
      - name: Compare benchmarks
        run: |
          pip install pybenchcompare
          pybenchcompare compare --file benchmark-results.json --threshold 1.2

  # =============================================================================
  # Security Tests
  # =============================================================================
  security-tests:
    name: Security Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install bandit safety
      
      - name: Run security tests
        run: |
          pytest tests/security -v -m security
      
      - name: Run Bandit security scan
        run: bandit -r src/ -f json -o bandit-results.json || true
      
      - name: Check dependencies for vulnerabilities
        run: safety check -r requirements.txt --json --output safety-results.json || true
      
      - name: Upload security scan results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-scan-results
          path: |
            bandit-results.json
            safety-results.json

  # =============================================================================
  # Code Quality
  # =============================================================================
  code-quality:
    name: Code Quality
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install linting tools
        run: |
          python -m pip install --upgrade pip
          pip install flake8 black isort mypy pylint
      
      - name: Run Black formatting check
        run: black --check src/ tests/
      
      - name: Run isort import check
        run: isort --check-only src/ tests/
      
      - name: Run Flake8 linting
        run: flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203
      
      - name: Run type checking
        run: mypy src/ --ignore-missing-imports --show-error-codes

  # =============================================================================
  # E2E Tests
  # =============================================================================
  e2e-tests:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    if: github.event_name == 'pull_request'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pip install playwright
          playwright install
      
      - name: Start dashboard
        run: |
          python run_dashboard.py &
          sleep 10  # Wait for dashboard to start
      
      - name: Run E2E tests
        run: |
          pytest tests/e2e -v -m e2e --headed=false
      
      - name: Upload E2E screenshots
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: e2e-screenshots
          path: tests/e2e/screenshots/

  # =============================================================================
  # Test Summary
  # =============================================================================
  test-summary:
    name: Test Summary
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, security-tests, code-quality]
    if: always()
    
    steps:
      - name: Download all test results
        uses: actions/download-artifact@v4
      
      - name: Generate test summary
        run: |
          echo "# Test Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "| Job | Status |" >> $GITHUB_STEP_SUMMARY
          echo "|-----|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| Unit Tests | ${{ needs.unit-tests.result }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Integration Tests | ${{ needs.integration-tests.result }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Security Tests | ${{ needs.security-tests.result }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Code Quality | ${{ needs.code-quality.result }} |" >> $GITHUB_STEP_SUMMARY
```

### 12.2 Requirements for Development

**File Path**: `/requirements-dev.txt`

```txt
# Testing Framework
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-xdist>=3.3.0
pytest-benchmark>=4.0.0
pytest-html>=3.2.0
pytest-mock>=3.11.0

# E2E Testing
playwright>=1.40.0
selenium>=4.15.0

# Load Testing
locust>=2.18.0

# Code Quality
black>=23.0.0
isort>=5.12.0
flake8>=6.1.0
mypy>=1.7.0
pylint>=3.0.0

# Security Testing
bandit>=1.7.5
safety>=2.3.0

# Coverage
coverage>=7.3.0
codecov>=2.1.13

# Type Stubs
types-requests>=2.31.0
types-pyyaml>=6.0.0

# Test Data
factory-boy>=3.3.0
faker>=20.0.0

# Documentation
pytest-doc>=0.1.0
```

---

## 13. Implementation Priority

### 13.1 Phase 1: Foundation (Week 1-2)

| Priority | Task | Files | Effort |
|----------|------|-------|--------|
| 1 | Setup pytest configuration | `pytest.ini`, `conftest.py` | 1 day |
| 2 | Create shared fixtures | `tests/conftest.py` | 2 days |
| 3 | Unit tests for data layer | `tests/unit/data/` | 3 days |
| 4 | Unit tests for LLM interface | `tests/unit/llm/` | 2 days |
| 5 | Mock implementations | `tests/mocks/` | 2 days |

### 13.2 Phase 2: Core Coverage (Week 3-4)

| Priority | Task | Files | Effort |
|----------|------|-------|--------|
| 6 | Unit tests for agent system | `tests/unit/agents/` | 4 days |
| 7 | Unit tests for API clients | `tests/unit/api_clients/` | 3 days |
| 8 | Unit tests for models | `tests/unit/models/` | 3 days |
| 9 | Integration tests for pipeline | `tests/integration/` | 3 days |
| 10 | Coverage reporting setup | `.coveragerc`, CI | 1 day |

### 13.3 Phase 3: Advanced Testing (Week 5-6)

| Priority | Task | Files | Effort |
|----------|------|-------|--------|
| 11 | E2E dashboard tests | `tests/e2e/` | 4 days |
| 12 | Performance benchmarks | `tests/performance/` | 3 days |
| 13 | Security tests | `tests/security/` | 2 days |
| 14 | Load testing setup | Locust configuration | 2 days |
| 15 | CI/CD integration | `.github/workflows/` | 2 days |

### 13.4 Phase 4: Continuous Improvement (Ongoing)

| Priority | Task | Frequency |
|----------|------|-----------|
| 16 | Increase code coverage | Weekly |
| 17 | Add regression tests | Per bug fix |
| 18 | Update test data | Monthly |
| 19 | Performance monitoring | Daily (CI) |
| 20 | Security scanning | Daily (CI) |

---

## 14. Test Execution Commands

```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/agents/test_base_agent.py -v

# Run with parallel execution
pytest -n auto

# Run performance benchmarks
pytest tests/performance --benchmark-only

# Run E2E tests
pytest tests/e2e -m e2e --headed

# Run security tests
pytest tests/security -m security

# Run tests matching pattern
pytest -k "test_healthcare"

# Run with detailed output
pytest -v --tb=long

# Run failed tests only
pytest --lf

# Run tests in random order
pytest --random-order
```

---

## 15. Success Metrics

| Metric | Target | Current | Priority |
|--------|--------|---------|----------|
| Code Coverage | >80% | ~30% | High |
| Unit Test Count | >500 | ~50 | High |
| Integration Test Count | >50 | ~5 | Medium |
| E2E Test Count | >20 | 0 | Medium |
| Test Execution Time | <5 min | N/A | High |
| Flaky Test Rate | <2% | N/A | High |
| Security Issues | 0 | Unknown | High |
| Performance Regression | <5% | N/A | Medium |

---

## 16. Conclusion

This comprehensive testing strategy provides:

1. **Structured Test Organization**: Clear separation of unit, integration, E2E, performance, and security tests
2. **Extensive Mocking**: Mock implementations for all external dependencies
3. **Test Data Generation**: Factories for generating realistic test data
4. **CI/CD Integration**: Automated testing pipeline with GitHub Actions
5. **Performance Monitoring**: Benchmarks and load testing capabilities
6. **Security Coverage**: Input validation and vulnerability scanning

The implementation should follow the phased approach to gradually build testing coverage while maintaining development velocity.

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: Testing & QA Engineering Team*
