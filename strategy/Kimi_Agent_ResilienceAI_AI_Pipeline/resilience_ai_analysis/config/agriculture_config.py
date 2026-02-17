"""
Agricultural Data Sources Configuration for ResilienceAI
"""

# Data source configurations
AGRICULTURAL_DATA_SOURCES = {
    "usda_nass": {
        "url": "https://quickstats.nass.usda.gov/api",
        "api_key_env": "USDA_NASS_API_KEY",
        "cache_hours": 168,
        "rate_limit": 1.0,
        "description": "USDA National Agricultural Statistics Service"
    },
    "nrcs_soil": {
        "url": "https://sdmdataaccess.nrcs.usda.gov",
        "cache_hours": 720,
        "description": "NRCS Soil Survey Geographic Database"
    },
    "drought_monitor": {
        "url": "https://usdmdataservices.unl.edu/api",
        "cache_hours": 24,
        "description": "US Drought Monitor"
    },
    "noaa_acis": {
        "url": "https://data.rcc-acis.org/",
        "cache_hours": 24,
        "description": "NOAA Applied Climate Information System"
    },
    "nasa_power": {
        "url": "https://power.larc.nasa.gov/api/temporal",
        "cache_hours": 24,
        "description": "NASA Prediction of Worldwide Energy Resources"
    },
    "commodity_prices": {
        "url": "https://www.quandl.com/api/v3",
        "api_key_env": "QUANDL_API_KEY",
        "cache_hours": 4,
        "description": "Commodity price data"
    }
}

# Crop configuration
CROP_CONFIG = {
    "major_crops": [
        "CORN", "SOYBEANS", "WHEAT", "COTTON", "RICE",
        "SORGHUM", "BARLEY", "OATS", "PEANUTS", "SUGARBEETS"
    ],
    "specialty_crops": [
        "APPLES", "GRAPES", "ORANGES", "POTATOES", "TOMATOES"
    ],
    "yield_units": {
        "CORN": "BU / ACRE",
        "SOYBEANS": "BU / ACRE",
        "WHEAT": "BU / ACRE",
        "COTTON": "LB / ACRE",
        "RICE": "LB / ACRE"
    },
    "planting_windows": {
        "CORN": {"early": "04-15", "late": "05-15", "optimal": "04-25"},
        "SOYBEANS": {"early": "04-20", "late": "06-10", "optimal": "05-05"},
        "WHEAT": {"early": "09-15", "late": "10-30", "optimal": "10-01"}
    }
}

# Agricultural feature groups for ML
AGRICULTURAL_FEATURES = {
    "yield_prediction": [
        "avg_temperature_growing_season",
        "total_precipitation_growing_season",
        "growing_degree_days",
        "soil_ph",
        "soil_organic_matter",
        "soil_water_capacity",
        "drought_index",
        "previous_year_yield",
        "trend_yield"
    ],
    "vulnerability_assessment": [
        "yield_coefficient_variation",
        "drought_frequency",
        "crop_diversity_index",
        "irrigation_coverage",
        "soil_quality_score",
        "climate_risk_score"
    ],
    "economic_analysis": [
        "farm_income_per_acre",
        "production_costs",
        "net_returns",
        "price_volatility"
    ]
}

# Drought impact thresholds by crop
DROUGHT_IMPACT_THRESHOLDS = {
    'CORN': {
        'D0': {'yield_reduction': 0, 'irrigation_increase': 10},
        'D1': {'yield_reduction': 10, 'irrigation_increase': 25},
        'D2': {'yield_reduction': 25, 'irrigation_increase': 50},
        'D3': {'yield_reduction': 45, 'irrigation_increase': 75},
        'D4': {'yield_reduction': 70, 'irrigation_increase': 100}
    },
    'SOYBEANS': {
        'D0': {'yield_reduction': 0, 'irrigation_increase': 10},
        'D1': {'yield_reduction': 8, 'irrigation_increase': 20},
        'D2': {'yield_reduction': 20, 'irrigation_increase': 45},
        'D3': {'yield_reduction': 40, 'irrigation_increase': 70},
        'D4': {'yield_reduction': 65, 'irrigation_increase': 100}
    },
    'WHEAT': {
        'D0': {'yield_reduction': 0, 'irrigation_increase': 5},
        'D1': {'yield_reduction': 5, 'irrigation_increase': 15},
        'D2': {'yield_reduction': 15, 'irrigation_increase': 35},
        'D3': {'yield_reduction': 35, 'irrigation_increase': 60},
        'D4': {'yield_reduction': 60, 'irrigation_increase': 100}
    }
}

# Commodity price units
COMMODITY_PRICE_UNITS = {
    'CORN': '$ / BU',
    'SOYBEANS': '$ / BU',
    'WHEAT': '$ / BU',
    'COTTON': '$ / LB',
    'RICE': '$ / CWT'
}
