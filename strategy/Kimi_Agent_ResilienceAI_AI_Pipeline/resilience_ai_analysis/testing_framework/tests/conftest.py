"""
ResilienceAI Test Configuration and Shared Fixtures

This module provides shared fixtures and configuration for all tests.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import json

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
    data_dir = project_root / "tests" / "fixtures" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture(scope="session")
def mock_responses_dir(project_root):
    """Return mock API responses directory."""
    responses_dir = project_root / "tests" / "fixtures" / "mock_api_responses"
    responses_dir.mkdir(parents=True, exist_ok=True)
    return responses_dir


@pytest.fixture(scope="session")
def temp_output_dir(project_root):
    """Return temporary output directory for tests."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# =============================================================================
# Data Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def sample_county_data():
    """Generate sample county data for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        'fips': [f'290{i:02d}' for i in range(1, 16)],
        'county_name': [f'County {chr(65+i)}, Missouri' for i in range(15)],
        'latitude': np.random.uniform(36, 40, 15),
        'longitude': np.random.uniform(-95, -89, 15),
        'population': np.random.randint(10000, 500000, 15),
        'uninsured_pct': np.random.uniform(5, 25, 15),
        'poverty_rate': np.random.uniform(8, 35, 15),
        'risk_level': np.random.choice(['Low', 'Medium', 'High'], 15),
        'healthcare_gap_score': np.random.uniform(0, 100, 15),
        'disaster_risk_score': np.random.uniform(0, 100, 15),
        'median_income': np.random.randint(30000, 100000, 15),
        'physician_per_1000': np.random.uniform(0.5, 4.0, 15),
        'hospital_distance_miles': np.random.uniform(5, 50, 15),
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
    
    np.random.seed(42)
    return pd.DataFrame({
        'fips': [f'29{i:03d}' for i in range(1, 116)],
        'county_name': [f"{c}, Missouri" for c in counties],
        'latitude': np.random.uniform(36, 40.5, 115),
        'longitude': np.random.uniform(-95.7, -89, 115),
        'population': np.random.randint(5000, 1000000, 115),
        'uninsured_pct': np.clip(np.random.normal(12, 5, 115), 3, 35),
        'poverty_rate': np.clip(np.random.normal(15, 7, 115), 5, 45),
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


@pytest.fixture(scope="function")
def large_dataset():
    """Generate large dataset for performance testing."""
    np.random.seed(42)
    n = 10000
    return pd.DataFrame({
        'fips': [f'29{i:05d}' for i in range(n)],
        'population': np.random.lognormal(10, 1.5, n).astype(int),
        'uninsured_pct': np.clip(np.random.normal(12, 5, n), 3, 35),
        'poverty_rate': np.clip(np.random.normal(15, 7, n), 5, 45),
        'flood_risk_score': np.random.uniform(0, 100, n),
        'tornado_risk_score': np.random.uniform(0, 100, n),
        'physician_per_1000': np.random.uniform(0.5, 4.0, n),
        'hospital_distance_miles': np.random.uniform(5, 50, n),
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
                    'senderName': 'NWS St. Louis',
                    'headline': 'Tornado Warning issued',
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[[-90.5, 38.6], [-90.5, 38.7], [-90.4, 38.7], [-90.5, 38.6]]]
                }
            },
            {
                'properties': {
                    'event': 'Severe Thunderstorm Warning',
                    'severity': 'Severe',
                    'areaDesc': 'Jackson County, Missouri',
                    'effective': '2024-01-01T14:00:00Z',
                    'expires': '2024-01-01T15:00:00Z',
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


@pytest.fixture(scope="function")
def mock_ollama_provider():
    """Mock Ollama LLM provider."""
    provider = Mock()
    provider.generate.return_value = Mock(
        content='{"action": "assess_vulnerability", "county": "St. Louis"}',
        model='mistral:7b',
        usage={'prompt_tokens': 10, 'completion_tokens': 15}
    )
    return provider


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture(scope="function", autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    original_env = {k: v for k, v in os.environ.items()}
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
        'LLM_TIMEOUT': 10,
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


# =============================================================================
# Helper Functions
# =============================================================================

def load_mock_response(filename: str, mock_responses_dir: Path) -> dict:
    """Load mock API response from JSON file."""
    filepath = mock_responses_dir / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}


def create_test_dataframe(rows: int = 10, cols: int = 5) -> pd.DataFrame:
    """Create a test DataFrame with random data."""
    np.random.seed(42)
    return pd.DataFrame(
        np.random.randn(rows, cols),
        columns=[f'col_{i}' for i in range(cols)]
    )
