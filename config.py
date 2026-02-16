"""
ResilienceAI Configuration
"""
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for dir_path in [DATA_DIR, RAW_DIR, PROCESSED_DIR, MODELS_DIR, REPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Data source URLs and configurations
DATA_SOURCES = {
    "fema_disasters": {
        "url": "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries",
        "description": "FEMA Disaster Declarations Database"
    },
    "hrsa_facilities": {
        "url": "https://data.hrsa.gov/tools/data-reporting/program-data",
        "description": "HRSA Health Facility Data"
    },
    "cdc_svi": {
        "url": "https://www.atsdr.cdc.gov/placeandhealth/svi/data_documentation_download.html",
        "description": "CDC Social Vulnerability Index"
    },
    "census_acs": {
        "url": "https://www.census.gov/programs-surveys/acs/data.html",
        "description": "American Community Survey"
    }
}

# Model configuration
MODEL_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "cv_folds": 5,
    "risk_thresholds": {
        "low": 0.33,
        "medium": 0.67,
        "high": 1.0
    }
}

# Agent configuration
AGENT_CONFIG = {
    "default_model": "claude-sonnet-4-5-20250929",
    "temperature": 0.3,
    "max_tokens": 4096,
    "archia_server_url": "http://localhost:8080"
}

# Feature groups for analysis
FEATURE_GROUPS = {
    "demographics": [
        "total_population",
        "median_income",
        "poverty_pct",
        "elderly_pct",
        "disability_pct",
        "uninsured_pct"
    ],
    "infrastructure": [
        "dist_nearest_hospitals_km",
        "dist_2nd_nearest_hospitals_km",
        "dist_nearest_fire_stations_km",
        "dist_nearest_ems_km",
        "hospitals_per_10k",
        "fire_stations_per_10k"
    ],
    "disaster_history": [
        "disaster_count",
        "disasters_2015_2025",
        "disasters_2005_2014",
        "disaster_acceleration",
        "flood_count",
        "hurricane_count",
        "fire_count",
        "tornado_count"
    ],
    "indices": [
        "vulnerability_index",
        "isolation_index",
        "risk_score",
        "compound_risk_count"
    ]
}
