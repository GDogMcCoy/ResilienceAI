# ResilienceAI - Setup Guide for Teammates

## Prerequisites

- Python 3.10+
- pip
- ~500MB free disk space (for data + models)

## Quick Start (5 minutes)

### 1. Clone/Copy the Project

Get the `resilienceai/` folder onto your machine.

### 2. Install Dependencies

```bash
cd resilienceai
pip install -r requirements.txt
```

### 3. Run the Full Pipeline

```bash
python run_pipeline.py
```

This downloads all data (cached after first run), engineers features, runs EDA, trains models, and exports agent config. Takes ~3-5 minutes on first run, ~1 minute on subsequent runs (data cached).

### 4. Launch the Dashboard

```bash
streamlit run app/dashboard.py --server.port 8503
```

Open http://localhost:8503 in your browser.

## Running Individual Steps

```bash
# Just download data (or use cache)
python run_pipeline.py --steps download

# Just feature engineering + EDA
python run_pipeline.py --steps features eda

# Just model training
python run_pipeline.py --steps train

# Force re-download everything
python run_pipeline.py --steps download --force
```

## Project Structure

```
resilienceai/
|-- config.py              <- Configuration (paths, URLs, model params)
|-- run_pipeline.py        <- Run everything with one command
|-- requirements.txt       <- pip install -r requirements.txt
|
|-- src/
|   |-- download_data.py   <- Downloads 7 data sources from federal APIs
|   |-- feature_engineering.py <- Builds 27 features from raw data
|   |-- eda.py             <- Generates 7 visualization PNGs
|   |-- train_models.py    <- Trains 4 ML models, saves metrics
|   |-- agent.py           <- Archia agent config + query tools
|
|-- app/
|   |-- dashboard.py       <- Streamlit dashboard (the demo)
|
|-- data/raw/              <- Downloaded CSVs (auto-populated)
|-- data/processed/        <- county_features.csv (3,222 x 37)
|-- data/cache/            <- API response cache (don't delete!)
|-- models/                <- Trained .pkl files + agent_config.json
|-- outputs/figures/       <- EDA visualizations (PNG)
|-- docs/                  <- This file + data dictionary
```

## Key Files to Know

| If you want to... | Edit this file |
|-------------------|---------------|
| Add new data sources | `config.py` (URLs) + `src/download_data.py` |
| Add new features | `src/feature_engineering.py` |
| Change model parameters | `src/train_models.py` (line ~100) |
| Modify dashboard layout | `app/dashboard.py` |
| Configure the AI agent | `src/agent.py` |
| Change risk score formula | `src/feature_engineering.py` (`compute_risk_score()`) |

## Troubleshooting

### "Port 8503 is not available"
Another Streamlit is running. Try `--server.port 8504` or kill the existing process.

### Data download fails
The pipeline caches all API responses in `data/cache/`. If a download fails midway, just re-run - it picks up where it left off. Use `--force` only if you need fresh data.

### Unicode errors on Windows
All print statements use ASCII characters. If you see encoding errors, check you haven't added unicode characters (arrows, emojis) to print statements.

## What Needs Work (for teammates)

### High Priority
1. **Archia Agent** - Deploy on console.archia.app, connect MCP tools to our SQLite database
2. **Video Script** - Write 10-min presentation covering problem, data, analysis, demo

### Medium Priority
3. **SHAP Analysis** - Add `shap.summary_plot()` to model training for feature explainability
4. **Dashboard Polish** - Add county search, improve Folium map with click popups
5. **Severe Storms Fix** - The FEMA `incidentType` for storms may not match our string filter

### Nice-to-Have
6. **Hyperparameter Tuning** - GridSearchCV or Optuna for XGBoost/RF
7. **Geospatial CV** - Spatial train/test split to avoid leakage
8. **Additional Data** - SAMHSA mental health facilities, flood zone maps
