# ResilienceAI

**AI-powered disaster vulnerability intelligence for Missouri communities.**

ResilienceAI is an MCP-based agentic platform that combines FEMA disaster declarations, Census demographics, HIFLD infrastructure data, and real-time NOAA weather feeds to assess county-level vulnerability, predict disaster risk trajectories, and support clinical and emergency decision-making. Built for the MUIDSI Hackathon 2026.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
python run_dashboard.py
```

The dashboard opens automatically at `http://localhost:8501`.

## Architecture

ResilienceAI follows a pipeline architecture:

1. **Data Acquisition** - Downloads and caches data from FEMA, Census ACS, HIFLD, CMS, NOAA, and USDA
2. **Feature Engineering** - Generates 66 features including vulnerability indices, isolation scores, and disaster acceleration metrics
3. **ML Models** - Four-model ensemble (Logistic Regression, Random Forest, Gradient Boosting, Neural Network) with soft voting
4. **MCP Agent** - 45 composable tools for querying, analysis, prediction, and export
5. **Dashboard** - Streamlit UI with 16 tabs: maps, analytics, alerts, forecasting, and more

## Project Structure

```
resilienceai/
├── config.py                  # All paths, URLs, and model params
├── run_dashboard.py           # Dashboard launcher (auto port detection)
├── run_pipeline.py            # Full pipeline orchestrator
├── requirements.txt           # Python dependencies
├── app/
│   └── dashboard.py           # Streamlit dashboard (16 tabs)
├── src/
│   ├── agent.py               # MCP agent with 45 tools
│   ├── download_data.py       # Data acquisition pipeline
│   ├── feature_engineering.py # 66-feature engineering
│   ├── train_models.py        # Ensemble model training
│   ├── weather_client.py      # NOAA real-time alerts
│   ├── predictive_models.py   # Prophet/ARIMA forecasting
│   ├── fhir_export.py         # FHIR R4 clinical export
│   ├── geo_visualizations.py  # Choropleth, hexbin, 3D maps
│   └── pipeline/              # EDA and pipeline utilities
├── data/
│   ├── raw/                   # Downloaded source data
│   ├── processed/             # county_features.csv (3,222 x 66)
│   └── cache/                 # API response cache
├── models/                    # Trained model artifacts (.pkl)
├── outputs/figures/           # Generated visualizations
├── docs/                      # API reference, setup guide, data dictionary
├── archia/                    # Archia deployment configuration
├── strategy/                  # Strategic planning documents
├── research/                  # Hackathon research and analysis
├── demo_materials/            # Presentation assets
└── tests/                     # Test suite
```

## MCP Tools (45)

| Category | Tools | Examples |
|----------|-------|---------|
| Core Query | 4 | `query_counties`, `get_county_detail`, `compare_counties`, `predict_risk` |
| Advanced Analytics | 4 | `simulate_scenario`, `analyze_cascade_risk`, `calculate_intervention_roi` |
| Export / Integration | 3 | `export_fhir`, `export_geojson`, `analyze_spatial_autocorrelation` |
| Real-Time Systems | 3 | `subscribe_to_alerts`, `get_weather_alerts`, `correlate_weather_with_vulnerability` |
| Agricultural Analysis | 2 | `get_crop_yield`, `calculate_agricultural_vulnerability` |
| Predictive Modeling | 3 | `forecast_risk_trajectory`, `project_climate_risk`, `predict_disaster_probability` |

## Data Sources

| Source | Records | Update Frequency |
|--------|---------|-----------------|
| FEMA Disaster Declarations | 69,615 | Daily |
| Census ACS 5-Year | 3,222 counties | Annual |
| HIFLD Infrastructure | 81,305 facilities | Quarterly |
| CMS Nursing Homes | 14,713 | Monthly |
| NOAA Weather Alerts | Real-time | Live |
| USDA NASS Crop Data | On-demand | Annual |

## Run the Full Pipeline

```bash
# All steps: download -> features -> EDA -> train -> agent
python run_pipeline.py

# Specific steps only
python run_pipeline.py --steps download features train
```

## License

MIT
