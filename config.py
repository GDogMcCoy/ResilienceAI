"""ResilienceAI - Project Configuration"""
import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Ensure directories exist
for d in [RAW_DIR, PROCESSED_DIR, CACHE_DIR, MODELS_DIR, FIGURES_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Data Source URLs ───────────────────────────────────────────────────
# HIFLD facility data via FEMA ArcGIS Hub (verified working Feb 2026)
HIFLD_ARCGIS_BASE = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services"
HIFLD_URLS = {
    # Hospitals from HIFLD official dataset
    "hospitals": f"{HIFLD_ARCGIS_BASE}/Hospitals/FeatureServer/0/query",
    # Fire & EMS from FEMA Structures_Medical_Emergency_Response_v1
    # Layer 1 = EMS stations, Layer 2 = Fire stations
    "ems_stations": f"{HIFLD_ARCGIS_BASE}/Structures_Medical_Emergency_Response_v1/FeatureServer/1/query",
    "fire_stations": f"{HIFLD_ARCGIS_BASE}/Structures_Medical_Emergency_Response_v1/FeatureServer/2/query",
}

# CMS Medicare nursing home data (has lat/lon, reliable API)
CMS_NURSING_HOME_URL = "https://data.cms.gov/provider-data/api/1/datastore/query/4pq5-n9py/0"

# FEMA Disaster Declarations (OpenFEMA API)
FEMA_DECLARATIONS_URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$top=10000&$format=json"

# Census ACS 5-Year (2022) - Key demographic variables by county
# Variables: total pop, median income, poverty count, 65+ pop, disability, uninsured
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")
CENSUS_BASE_URL = "https://api.census.gov/data/2022/acs/acs5"
CENSUS_VARIABLES = [
    "B01003_001E",  # Total population
    "B19013_001E",  # Median household income
    "B17001_002E",  # Population below poverty
    "B01001_020E",  # Male 65-66
    "B01001_021E",  # Male 67-69
    "B01001_022E",  # Male 70-74
    "B01001_023E",  # Male 75-79
    "B01001_024E",  # Male 80-84
    "B01001_025E",  # Male 85+
    "B01001_044E",  # Female 65-66
    "B01001_045E",  # Female 67-69
    "B01001_046E",  # Female 70-74
    "B01001_047E",  # Female 75-79
    "B01001_048E",  # Female 80-84
    "B01001_049E",  # Female 85+
    "B18101_001E",  # Total disability universe
    "B18101_004E",  # Male under 5 with disability
    "B18101_007E",  # Male 5-17 with disability
    "B18101_010E",  # Male 18-34 with disability
    "B18101_013E",  # Male 35-64 with disability
    "B18101_016E",  # Male 65-74 with disability
    "B18101_019E",  # Male 75+ with disability
    "B18101_023E",  # Female under 5 with disability
    "B18101_026E",  # Female 5-17 with disability
    "B18101_029E",  # Female 18-34 with disability
    "B18101_032E",  # Female 35-64 with disability
    "B18101_035E",  # Female 65-74 with disability
    "B18101_038E",  # Female 75+ with disability
    "B27010_001E",  # Health insurance universe
    "B27010_017E",  # Uninsured under 19
    "B27010_033E",  # Uninsured 19-34
    "B27010_050E",  # Uninsured 35-64
    "B27010_066E",  # Uninsured 65+
]

# ── Focus Area ─────────────────────────────────────────────────────────
# We can focus on specific states for faster processing or do nationwide
FOCUS_STATES = None  # None = nationwide, or e.g. ["MO", "IL", "KS", "AR"]

# ── Model Configuration ───────────────────────────────────────────────
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Target variable bins for classification
RISK_BINS = {
    "Low": (0, 0.33),
    "Medium": (0.33, 0.66),
    "High": (0.66, 1.0),
}

# ── Column Names ───────────────────────────────────────────────────────
COL_FIPS = "fips"
COL_STATE = "state"
COL_COUNTY = "county"
COL_LAT = "latitude"
COL_LON = "longitude"
COL_POPULATION = "total_population"
COL_RISK_SCORE = "risk_score"
COL_RISK_LEVEL = "risk_level"
