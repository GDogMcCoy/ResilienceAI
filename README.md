# ResilienceAI

### Disaster Vulnerability & Health Infrastructure Gap Assessment Agent

> **MUIDSI Hackathon 2026** | Theme: *Agentic AI for Real-World Impact*

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Our Solution](#our-solution)
- [Data Sources](#data-sources)
- [Feature Engineering](#feature-engineering)
- [Exploratory Data Analysis](#exploratory-data-analysis)
- [Model Development & Evaluation](#model-development--evaluation)
- [Agentic AI Component](#agentic-ai-component)
- [Interactive Dashboard](#interactive-dashboard)
- [Project Architecture](#project-architecture)
- [Reproducibility](#reproducibility)
- [Scoring Rubric Alignment](#scoring-rubric-alignment)
- [Team](#team)

---

## Problem Statement

When natural disasters strike, the damage is not distributed equally. Communities with limited healthcare infrastructure, aging populations, high poverty rates, and histories of repeated disasters bear a disproportionate burden. Yet emergency planners lack accessible, data-driven tools to identify **which specific communities** face the greatest compound risk before disaster hits.

**The gap**: No existing tool integrates infrastructure access, demographic vulnerability, and disaster history into a single queryable platform that a non-technical emergency planner can use.

## Our Solution

**ResilienceAI** fuses **7 federal open data sources** (157,363 total records) into a unified machine learning pipeline that:

1. **Engineers 27 features** capturing spatial infrastructure access, demographic vulnerability, and disaster exposure for every US county
2. **Trains and evaluates 4 classification models** to predict county-level disaster risk (Low / Medium / High)
3. **Deploys an agentic AI interface** where emergency planners ask questions in natural language and receive data-backed answers with interactive maps

**Example queries the agent handles:**
- *"Which Missouri counties are most vulnerable to flooding?"*
- *"Compare hospital access in rural vs. urban counties in the Southeast"*
- *"What areas have high elderly populations AND no EMS station within 50km?"*

---

## Data Sources

All data is **real, publicly available federal open data**. No synthetic or simulated data was used at any point.

| # | Source | Records | Description | Access Link |
|---|--------|---------|-------------|-------------|
| 1 | **HIFLD Hospitals** | 7,496 | Hospital locations, type, status, bed count | [FEMA ArcGIS Hub - Hospitals](https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Hospitals/FeatureServer/0) |
| 2 | **HIFLD Fire Stations** | 52,051 | Fire station locations nationwide | [FEMA ArcGIS Hub - Fire/EMS Layer 2](https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Structures_Medical_Emergency_Response_v1/FeatureServer/2) |
| 3 | **HIFLD EMS Stations** | 7,045 | Emergency medical service locations | [FEMA ArcGIS Hub - Fire/EMS Layer 1](https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Structures_Medical_Emergency_Response_v1/FeatureServer/1) |
| 4 | **CMS Nursing Homes** | 14,713 | Medicare-certified nursing home locations, bed counts, ratings | [CMS Provider Data API](https://data.cms.gov/provider-data/api/1/datastore/query/4pq5-n9py/0) |
| 5 | **FEMA Disaster Declarations** | 69,615 | Every federal disaster declaration since 1953, by county | [OpenFEMA API](https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries) |
| 6 | **Census ACS 5-Year (2022)** | 3,222 | County-level demographics: population, income, poverty, elderly, disability, uninsured rates | [Census Bureau API](https://api.census.gov/data/2022/acs/acs5) |
| 7 | **Census Gazetteer (2024)** | 3,222 | County centroid coordinates (latitude/longitude) | [Census Gazetteer Files](https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/) |

**Total: 157,363 records from 7 federal sources**

### Data Provenance

| Source Agency | Datasets Used | Data Format |
|---------------|---------------|-------------|
| FEMA | Hospitals, Fire Stations, EMS Stations, Disaster Declarations | ArcGIS REST API (JSON), OpenFEMA API (JSON) |
| CMS (Medicare) | Nursing Homes | REST API (JSON) |
| U.S. Census Bureau | Demographics (ACS), County Centroids (Gazetteer) | REST API (JSON), Tab-delimited text |

All data is downloaded programmatically via `src/download_data.py` with local caching. See [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) for verified endpoint URLs and pagination details.

---

## Feature Engineering

We engineered **27 predictive features** across 3,222 US counties, organized into 5 categories:

### Spatial Infrastructure Access (8 features)
| Feature | Method |
|---------|--------|
| Distance to nearest hospital (km) | KD-tree nearest-neighbor search on facility coordinates |
| Distance to nearest fire station (km) | KD-tree nearest-neighbor search |
| Distance to nearest EMS station (km) | KD-tree nearest-neighbor search |
| Distance to nearest nursing home (km) | KD-tree nearest-neighbor search |
| Hospital count within 50km | KD-tree ball query (radius = 50km) |
| Fire station count within 50km | KD-tree ball query |
| EMS station count within 50km | KD-tree ball query |
| Nursing home count within 50km | KD-tree ball query |

*Implementation: `scipy.spatial.cKDTree` with coordinates converted to radians for spherical distance approximation.*

### Infrastructure Density (4 features)
| Feature | Formula |
|---------|---------|
| Hospital density per 10k population | (count within 50km / population) * 10,000 |
| Fire station density per 10k | Same formula |
| EMS density per 10k | Same formula |
| Nursing home density per 10k | Same formula |

### Disaster History (7 features)
| Feature | Source |
|---------|--------|
| Total disaster declarations (all time) | FEMA, grouped by county FIPS |
| Recent disaster declarations (2015-present) | FEMA, filtered by declaration date |
| Flood disaster count | FEMA, filtered by `incidentType` |
| Hurricane disaster count | FEMA, filtered by `incidentType` |
| Fire/wildfire disaster count | FEMA, filtered by `incidentType` |
| Tornado disaster count | FEMA, filtered by `incidentType` |
| Severe storm count | FEMA, filtered by `incidentType` |

### Demographic Vulnerability (4 features)
| Feature | Source | National Range |
|---------|--------|---------------|
| Elderly population % (age 65+) | Census ACS | 2.9% - 57.9% |
| Poverty rate % | Census ACS | 1.6% - 65.6% |
| Disability rate % | Census ACS | 4.0% - 41.1% |
| Uninsured rate % | Census ACS | 0.0% - 45.1% |

### Composite Indices (4 features)
| Feature | Construction |
|---------|-------------|
| **Vulnerability Index** | Min-max normalized average of elderly %, poverty %, disability %, uninsured % |
| **Isolation Index** | Min-max normalized average of distances to all 4 facility types |
| **Risk Score** | Weighted composite: 40% vulnerability + 30% isolation + 30% disaster exposure, then min-max normalized to [0, 1] |
| **Risk Level** | Tercile classification of risk score: Low / Medium / High |

Full column-level documentation: [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md)

---

## Exploratory Data Analysis

EDA is implemented in `src/eda.py` and generates the following visualizations (saved to `outputs/figures/`):

| Visualization | What It Shows |
|---------------|---------------|
| `risk_distribution.png` | Histogram of risk scores + bar chart of risk level counts |
| `vulnerability_components.png` | Distribution of elderly %, poverty %, disability %, uninsured % across all counties |
| `facility_distances.png` | Distribution of distance-to-nearest for each facility type |
| `correlation_heatmap.png` | Pairwise Pearson correlation of all 27 numeric features |
| `disaster_frequency.png` | Disaster count distribution + top 20 most disaster-affected counties |
| `geographic_risk_map.png` | Continental US scatter plot of counties colored by risk score |
| `summary_statistics.csv` | Descriptive statistics for all features |

### Key Findings from EDA

- **Coverage**: 3,222 counties covering 334.4 million total US population
- **Disaster exposure**: Maximum 172 disaster declarations for a single county; only 12 counties with zero declarations
- **Mean risk score**: 0.261 (skewed toward lower risk, reflecting that most counties have some infrastructure access)
- **Infrastructure gaps**: Counties in Alaska, Hawaii, and rural Great Plains show the highest isolation indices

The Streamlit dashboard provides additional **interactive** EDA via Plotly and Mapbox visualizations.

---

## Model Development & Evaluation

### Task Definition

**3-class classification**: Predict county disaster risk level (Low / Medium / High) from 27 engineered features.

- **Samples**: 3,222 counties
- **Classes**: Low (1,063) | Medium (1,096) | High (1,063) -- balanced via tercile binning
- **Split**: 80% train (2,577) / 20% test (645), stratified
- **Validation**: 5-fold stratified cross-validation on training set

### Models Trained

| Model | Configuration |
|-------|--------------|
| **Random Forest** | 200 trees, max_depth=15, min_samples_split=5 |
| **Gradient Boosting** | 200 estimators, max_depth=5, learning_rate=0.1 |
| **Logistic Regression** | max_iter=1000, default regularization |
| **Neural Network (MLP)** | 3 hidden layers (128, 64, 32), early stopping |

*Feature scaling: StandardScaler applied for Logistic Regression and Neural Network. Tree-based models use raw features.*

### Results

| Model | Test Accuracy | Test F1 (macro) | CV F1 Mean | CV F1 Std |
|-------|:------------:|:---------------:|:----------:|:---------:|
| **Logistic Regression** | **98.3%** | **0.983** | **0.979** | **0.009** |
| Gradient Boosting | 97.1% | 0.971 | 0.967 | 0.007 |
| Neural Network | 94.9% | 0.949 | 0.950 | 0.013 |
| Random Forest | 94.4% | 0.944 | 0.933 | 0.003 |

**Best model**: Logistic Regression (F1=0.983, CV=0.979)

### Evaluation Artifacts

Generated in `outputs/figures/`:

| File | Description |
|------|-------------|
| `model_comparison.png` | Bar chart comparing accuracy + F1 across all models |
| `confusion_matrices.png` | Side-by-side confusion matrices for all 4 models |
| `roc_curves.png` | Micro-average ROC curves with AUC scores |
| `feature_importance_random_forest.png` | Top 20 features by Gini importance |
| `feature_importance_gradient_boosting.png` | Top 20 features by Gradient Boosting importance |
| `model_results_summary.csv` | Tabular results for all models |

All trained models are serialized to `models/` as `.pkl` files via joblib.

---

## Agentic AI Component

ResilienceAI includes a natural language query interface designed for deployment on the [Archia Cloud platform](https://console.archia.app).

### Agent Design

The agent is configured with:
- A **system prompt** establishing the agent's role as a disaster vulnerability advisor
- **5 MCP-compatible tools** for structured data access
- **Temperature 0.3** for factual, consistent responses

### MCP Tool Definitions

| Tool | Purpose | Parameters |
|------|---------|------------|
| `query_counties` | Filter and sort counties by state, risk level, or score | state, risk_level, min_risk_score, sort_by, max_results |
| `get_county_detail` | Full vulnerability profile for a specific county | county_name or fips |
| `compare_counties` | Side-by-side comparison of multiple counties | county_names[] |
| `get_statistics` | Summary statistics for any feature | feature, state, risk_level |
| `predict_risk` | Predict risk for hypothetical community characteristics | population, income, elderly_pct, etc. |

Agent configuration is exported to `models/agent_config.json` for direct import into Archia.

### Demo Mode

The Streamlit dashboard includes a keyword-based query processor (Tab 5: "Agent Query") that demonstrates the agent's intended functionality with state detection, risk filtering, disaster type filtering, and county comparison.

---

## Interactive Dashboard

The Streamlit dashboard (`app/dashboard.py`) provides 5 interactive tabs:

| Tab | Contents |
|-----|----------|
| **Overview** | Key metrics (county count, avg risk, high-risk count, total disasters), risk distribution charts, top 20 highest-risk counties table |
| **Risk Map** | Interactive Plotly Mapbox scatter map of all US counties colored by risk score, with hover tooltips |
| **Infrastructure** | Facility distance distributions, infrastructure gap identification (counties >50km from nearest facility), vulnerability vs. isolation scatter plot |
| **Model Performance** | All evaluation visualizations: model comparison, confusion matrices, ROC curves, feature importance |
| **Agent Query** | Natural language query interface with example prompts and formatted results |

### Sidebar Filters
- State multi-select
- Risk level filter (Low / Medium / High)
- Population range slider

---

## Project Architecture

```
resilienceai/
|
|-- config.py                    # Central configuration: paths, API URLs, model hyperparameters
|-- run_pipeline.py              # End-to-end pipeline orchestrator (download -> features -> eda -> train -> agent)
|-- requirements.txt             # Python dependencies
|
|-- src/
|   |-- download_data.py         # Data acquisition from 5 APIs with caching and pagination
|   |-- feature_engineering.py   # 27 engineered features using KD-tree spatial analysis
|   |-- eda.py                   # 7 static visualizations (matplotlib/seaborn)
|   |-- train_models.py          # 4 ML models with cross-validation and full evaluation suite
|   |-- agent.py                 # Archia agent system prompt, MCP tool definitions, query processor
|
|-- app/
|   |-- dashboard.py             # Streamlit dashboard with 5 interactive tabs
|
|-- data/
|   |-- raw/                     # Downloaded CSVs from federal APIs (gitignored, regenerated by pipeline)
|   |-- processed/               # county_features.csv: 3,222 x 37 (gitignored, regenerated)
|   |-- cache/                   # API response cache for fast re-runs (gitignored)
|
|-- models/
|   |-- best_model.pkl           # Best classifier (gitignored, regenerated)
|   |-- agent_config.json        # Archia agent configuration (committed)
|
|-- outputs/
|   |-- figures/                 # EDA + model evaluation PNGs (gitignored, regenerated)
|
|-- docs/
|   |-- DATA_DICTIONARY.md       # Column-level documentation for all 37 features
|   |-- SETUP_GUIDE.md           # Teammate onboarding instructions
|   |-- API_REFERENCE.md         # Verified API endpoints, pagination details, troubleshooting
```

---

## Reproducibility

### Prerequisites
- Python 3.10+
- Internet connection (for initial data download)

### Full Pipeline (One Command)

```bash
pip install -r requirements.txt
python run_pipeline.py
```

This executes all 5 stages:
1. **Download** - Fetches all 7 data sources from federal APIs (~3 min, cached after first run)
2. **Feature Engineering** - Computes 27 features for 3,222 counties (~10 sec)
3. **EDA** - Generates 7 visualizations (~5 sec)
4. **Model Training** - Trains 4 classifiers with cross-validation (~60 sec)
5. **Agent Config** - Exports Archia-compatible agent configuration (~1 sec)

### Individual Steps

```bash
python run_pipeline.py --steps download          # Data acquisition only
python run_pipeline.py --steps features eda      # Feature engineering + EDA only
python run_pipeline.py --steps train             # Model training only
python run_pipeline.py --steps download --force  # Force re-download (bypass cache)
```

### Launch Dashboard

```bash
streamlit run app/dashboard.py --server.port 8503
```

Open [http://localhost:8503](http://localhost:8503) in your browser.

---

## Scoring Rubric Alignment

| Category | Weight | What We Deliver |
|----------|:------:|-----------------|
| **Model Development** | 30% | 4 classifiers (RF, GBM, LR, MLP), 5-fold stratified CV, ROC-AUC, confusion matrices, feature importance, best F1=0.983 |
| **Feature Engineering** | 20% | 27 features from 7 sources: KD-tree spatial distances, infrastructure density, FEMA disaster history, Census vulnerability composites, normalized risk indices |
| **EDA** | 10% | 7 static visualizations + interactive Plotly/Mapbox dashboard with filters |
| **Evaluation Metrics** | 10% | Accuracy, F1 (macro), precision/recall per class, 5-fold CV with standard deviation, micro-average ROC curves |
| **Novelty** | 10% | Multi-agency federal data fusion, KD-tree geospatial feature engineering, natural language agent with MCP tools |
| **Presentation** | 10% | 5-tab interactive Streamlit dashboard, Mapbox risk visualization, agent query demo |
| **Problem + Social Good** | 10% | Disaster preparedness for vulnerable communities, actionable for FEMA/state emergency management, real federal data |

---

## Team

**MUIDSI Hackathon 2026**

---

## License

Academic use -- MUIDSI Hackathon 2026 submission.
