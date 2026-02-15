# ResilienceAI

**Disaster Vulnerability & Health Infrastructure Gap Assessment Agent**

MUIDSI Hackathon 2026 | Team Submission | "Agentic AI for Real-World Impact"

---

## Problem Statement

When disasters strike, vulnerable communities with sparse healthcare infrastructure suffer disproportionately. Emergency planners lack tools to quickly identify which areas face the greatest compound risk - combining disaster exposure, infrastructure gaps, and demographic vulnerability.

**ResilienceAI** solves this by fusing 7 federal data sources into a unified risk model that emergency planners can query through a natural language AI agent.

## Live Demo

```bash
# Launch the interactive dashboard
cd resilienceai
streamlit run app/dashboard.py --server.port 8503
```

Dashboard tabs:
1. **Overview** - Risk distribution, key metrics, top 20 highest-risk counties
2. **Risk Map** - Interactive Mapbox scatter map of 3,222 US counties colored by risk
3. **Infrastructure** - Facility distance analysis, infrastructure gap identification
4. **Model Performance** - Model comparison, confusion matrices, ROC curves, feature importance
5. **Agent Query** - Natural language interface for querying vulnerability data

## Architecture

```
resilienceai/
|-- config.py                  # Project configuration, API URLs, model params
|-- run_pipeline.py            # End-to-end pipeline orchestrator
|-- requirements.txt           # Python dependencies
|
|-- src/
|   |-- download_data.py       # Data acquisition from 5 APIs (HIFLD, FEMA, Census, CMS)
|   |-- feature_engineering.py # 27 engineered features (spatial, demographic, disaster)
|   |-- eda.py                 # 7 visualizations (distributions, maps, correlations)
|   |-- train_models.py        # 4 ML models with cross-validation and evaluation
|   |-- agent.py               # Archia agent config, MCP tools, query processing
|
|-- app/
|   |-- dashboard.py           # Streamlit dashboard (5 tabs, interactive maps)
|
|-- data/
|   |-- raw/                   # Downloaded CSVs from federal APIs
|   |-- processed/             # Engineered feature dataset (county_features.csv)
|   |-- cache/                 # API response cache (prevents re-downloads)
|
|-- models/                    # Trained model artifacts (.pkl) + agent config
|-- outputs/
|   |-- figures/               # EDA visualizations (PNG)
|   |-- reports/               # Summary statistics
```

## Data Sources

All data is real, from federal open data APIs. No synthetic data.

| Source | Records | API | What It Provides |
|--------|---------|-----|-----------------|
| **HIFLD Hospitals** | 7,496 | FEMA ArcGIS Hub | Hospital locations, type, status, beds |
| **HIFLD Fire Stations** | 52,051 | FEMA ArcGIS Hub | Fire station locations nationwide |
| **HIFLD EMS Stations** | 7,045 | FEMA ArcGIS Hub | Emergency medical service locations |
| **CMS Nursing Homes** | 14,713 | CMS Medicare API | Nursing home locations, bed counts, ratings |
| **FEMA Disasters** | 69,615 | OpenFEMA API | Historical disaster declarations by county since 1953 |
| **Census ACS** | 3,222 | Census Bureau API | County demographics: poverty, elderly, disability, uninsured |
| **Census Gazetteer** | 3,222 | Census Bureau | County centroid coordinates (lat/lon) |

**Total: 157,363 records from 7 sources**

## Feature Engineering (27 Features)

### Spatial Distance Features (8)
- Distance to nearest hospital, fire station, EMS station, nursing home (km)
- Count of each facility type within 50km radius
- Computed using scipy KD-tree for efficient nearest-neighbor search

### Infrastructure Density Features (4)
- Facilities per 10,000 population for each type within 50km

### Disaster History Features (7)
- Total disaster declarations per county
- Recent disasters (last 10 years)
- Breakdown by type: flood, severe storms, hurricane, fire, tornado

### Demographic Vulnerability Features (4)
- Elderly population percentage (65+)
- Poverty rate
- Disability rate
- Uninsured rate

### Composite Indices (4)
- **Vulnerability Index**: Normalized composite of elderly, poverty, disability, uninsured rates
- **Isolation Index**: Normalized average distance to all facility types
- **Risk Score**: Weighted composite (40% vulnerability + 30% isolation + 30% disaster exposure)
- **Risk Level**: Tercile classification (Low / Medium / High)

## Model Performance

| Model | Accuracy | F1 (macro) | CV F1 (5-fold) |
|-------|----------|-----------|----------------|
| **Logistic Regression** | **98.3%** | **0.983** | **0.979 +/- 0.009** |
| Gradient Boosting | 97.1% | 0.971 | 0.967 +/- 0.007 |
| Neural Network (MLP) | 94.9% | 0.949 | 0.950 +/- 0.013 |
| Random Forest | 94.4% | 0.944 | 0.933 +/- 0.003 |

- 3-class classification: Low / Medium / High risk
- Balanced classes: ~1,063 counties per class
- Train/test split: 80/20 with stratification
- Best model saved as `models/best_model.pkl`

## Agentic AI Component

ResilienceAI includes a natural language query interface powered by the Archia Cloud platform.

### Agent Capabilities
- **Query counties** by state, risk level, or minimum risk score
- **Get county details** with full vulnerability profile
- **Compare counties** side by side
- **Get statistics** for any feature across filtered subsets
- **Predict risk** for hypothetical community characteristics

### MCP Tool Integration
Agent config exported to `models/agent_config.json` with 5 defined tools:
- `query_counties` - Filter and sort county risk data
- `get_county_detail` - Detailed vulnerability profile
- `compare_counties` - Side-by-side comparison
- `get_statistics` - Feature summary statistics
- `predict_risk` - Risk prediction for new inputs

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Full Pipeline
```bash
python run_pipeline.py
```

This runs all 5 steps: download -> features -> eda -> train -> agent

### 3. Run Individual Steps
```bash
python run_pipeline.py --steps download        # Just download data
python run_pipeline.py --steps features eda    # Just feature eng + EDA
python run_pipeline.py --steps train           # Just model training
python run_pipeline.py --force                 # Force re-download all data
```

### 4. Launch Dashboard
```bash
streamlit run app/dashboard.py --server.port 8503
```

## Scoring Rubric Alignment

| Category | Weight | Coverage |
|----------|--------|----------|
| **Model Development** | 30% | 4 models, cross-validation, ROC-AUC, confusion matrices, feature importance |
| **Feature Engineering** | 20% | 27 features from 7 sources: spatial distances, density, vulnerability composites, disaster history |
| **EDA** | 10% | 7 static visualizations + interactive Plotly/Mapbox charts in dashboard |
| **Evaluation Metrics** | 10% | Accuracy, F1 (macro), precision/recall per class, 5-fold CV, ROC curves |
| **Novelty** | 10% | Multi-source federal data fusion, KD-tree spatial analysis, natural language agent |
| **Presentation** | 10% | 5-tab interactive dashboard with maps, agent queries, model explainability |
| **Problem + Social Good** | 10% | Disaster preparedness saves lives, actionable for FEMA/state agencies |

## Team

MUIDSI Hackathon 2026

## License

Academic use - MUIDSI Hackathon 2026 submission
