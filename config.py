"""
ResilienceAI Configuration
Version: 3.2.0 (MUIDSI Hackathon 2026 Final)
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"

# Ensure directories exist
for dir_path in [DATA_DIR, RAW_DIR, PROCESSED_DIR, CACHE_DIR, MODELS_DIR, REPORTS_DIR, FIGURES_DIR]:
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

# HIFLD ArcGIS endpoints
HIFLD_URLS = {
    "hospitals": "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Hospitals_1/FeatureServer/0/query",
    "fire_stations": "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Fire_Stations/FeatureServer/0/query",
    "ems_stations": "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/EMS_Stations/FeatureServer/0/query",
}
CMS_NURSING_HOME_URL = "https://data.cms.gov/provider-data/sites/default/files/resources/6c77e8398f0e0bba2ded0a4e590a2b46/NH_ProviderInfo.csv"

# Census API
CENSUS_BASE_URL = "https://api.census.gov/data/2022/acs/acs5"
CENSUS_VARIABLES = "B01003_001E,B19013_001E,B17001_002E,B09020_001E,B18101_001E,B27010_001E"
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")

# Geographic scope
FOCUS_STATES = ["29"]  # Missouri FIPS
COL_FIPS = "fips"

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

# Convenience aliases from MODEL_CONFIG
RANDOM_STATE = MODEL_CONFIG["random_state"]
TEST_SIZE = MODEL_CONFIG["test_size"]
CV_FOLDS = MODEL_CONFIG["cv_folds"]

# Agent configuration
AGENT_CONFIG = {
    "default_model": "claude-sonnet-4-5-20250929",
    "temperature": 0.3,
    "max_tokens": 4096,
    "archia_server_url": "http://localhost:8080"
}

# Climate data sources
CLIMATE_SOURCES = {
    "acis": {"url": "https://data.rcc-acis.org/", "cache_hours": 168},
    "fema_nri": {"url": "https://hazards.fema.gov/nri/data", "cache_hours": 720},
    "usgs_nwis": {"url": "https://waterservices.usgs.gov/nwis/", "cache_hours": 24},
    "swdi": {"url": "https://www.ncei.noaa.gov/access/services/search/v1/data", "cache_hours": 168},
    "drought_monitor": {"url": "https://usdmdataservices.unl.edu/api", "cache_hours": 24},
    "gee": {"url": "https://earthengine.googleapis.com", "cache_hours": 720,
            "datasets": ["MODIS/061/MOD11A2", "MODIS/061/MOD13Q1", "GRIDMET/DROUGHT",
                         "NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG", "JRC/GSW1_4/GlobalSurfaceWater",
                         "MODIS/061/MCD64A1"]},
}

# Google Earth Engine
GEE_PROJECT_ID = os.environ.get("GEE_PROJECT_ID", "")
GEE_CACHE_DIR = DATA_DIR / "gee_cache"
GEE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

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
