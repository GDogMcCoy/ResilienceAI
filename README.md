# ResilienceAI

### Disaster Vulnerability & Health Infrastructure Gap Assessment Agent

> **MUIDSI Hackathon 2026** | Theme: *Agentic AI for Real-World Impact*
>
> **Live Demo:** [resiliencea-he3ymacsegj4rb6bldxq4t.streamlit.app](https://resiliencea-he3ymacsegj4rb6bldxq4t.streamlit.app/)

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

1. **Engineers 66 features** including 7 advanced differentiator analytics for agentic AI insight exploration
2. **Trains and evaluates 4 classification models** to predict county-level disaster risk (Low / Medium / High)
3. **Deploys an agentic AI interface** with 19 MCP-compatible tools where emergency planners ask questions in natural language and receive data-backed answers with interactive maps

**Example queries the agent handles:**
- *"Which Missouri counties are most vulnerable to flooding?"*
- *"Where are disasters accelerating fastest in the Southeast?"*
- *"Which counties have zero hospital redundancy?"*
- *"What single intervention would most reduce risk in Jackson County?"*
- *"Show me compound risk hotspots -- counties high on 3+ dimensions"*

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

We engineered **66 features** across 3,222 US counties, organized into 12 categories:

### Core Features (37)

**Spatial Infrastructure Access (12 features)**: KD-tree nearest-neighbor search (`scipy.spatial.cKDTree`) for distance to nearest *and 2nd-nearest* hospital, fire station, EMS station, and nursing home, plus facility counts within 50km.

**Infrastructure Density (4 features)**: Facilities per 10,000 population within 50km for each facility type.

**Disaster History (7 features)**: Total declarations (all time), recent (2015+), and breakdown by type (flood, hurricane, fire, tornado, severe storms) from FEMA data.

**Demographic Vulnerability (4 features)**: Elderly %, poverty %, disability %, uninsured % from Census ACS.

**Composite Indices (4 features)**: Vulnerability Index, Isolation Index, Risk Score (weighted 40/30/30), Risk Level (tercile classification).

### Advanced Differentiator Features (29)

These features are specifically designed to serve rich, actionable insights to the agentic AI layer:

| # | Feature Category | Key Columns | What It Enables |
|---|-----------------|-------------|-----------------|
| 1 | **Compound Risk Clusters** | `compound_risk_count`, `compound_risk_flag` | Identifies counties high on 3+ risk dimensions simultaneously (177 counties flagged) |
| 2 | **Nearest-Neighbor Risk Contagion** | `neighbor_avg_risk`, `risk_contagion_delta` | Detects overflow risk -- when surrounding counties are also high-risk, capacity is limited |
| 3 | **Temporal Disaster Acceleration** | `disaster_acceleration`, `disasters_2015_2025`, `disasters_2005_2014` | Compares recent vs prior decade frequency (1,305 counties accelerating) |
| 4 | **Infrastructure Redundancy** | `redundancy_score`, `zero_redundancy_flag` | Distance to 2nd-nearest facility; flags single-point-of-failure counties (74 with zero hospital redundancy) |
| 5 | **Population-Weighted Vulnerability** | `pop_weighted_risk`, `pop_weighted_vulnerability` | Weights insights by lives impacted for intervention prioritization |
| 6 | **State-Level Rankings** | `risk_score_state_pctile`, `vulnerability_index_state_pctile` | Percentile rank within own state for contextual comparison |
| 7 | **Gap Analysis Matrix** | `gap_hospital`, `gap_ems`, `gap_fire`, `gap_poverty`, `gap_disaster_prep`, `top_intervention` | Identifies which single intervention most reduces each county's risk |

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
- A **system prompt** establishing the agent as a disaster vulnerability advisor with knowledge of all 66 features
- **19 MCP-compatible tools** for structured data access, advanced analytics, scenario simulation, and reporting
- **Temperature 0.3** for factual, consistent responses

### MCP Tool Definitions

| Tool | Purpose |
|------|---------|
| `query_counties` | Filter and sort counties by state, risk level, or score |
| `get_county_detail` | Full vulnerability profile for a specific county |
| `compare_counties` | Side-by-side comparison of multiple counties |
| `get_statistics` | Summary statistics for any feature |
| `predict_risk` | Predict risk for hypothetical community characteristics |
| `find_compound_risk_counties` | Find hotspot counties high on 3+ risk dimensions |
| `get_gap_analysis` | Identify which single intervention most reduces risk per county |
| `get_disaster_trends` | Find counties with accelerating disaster frequency |
| `find_zero_redundancy` | Locate single-point-of-failure communities |
| `get_state_rankings` | Rank counties within a state by risk percentile |
| `prioritize_by_impact` | Rank by population-weighted risk for maximum-impact interventions |
| `simulate_scenario` | What-if disaster simulation with 10 preset types |
| `analyze_cascade_risk` | Infrastructure network cascade/dependency analysis |
| `calculate_intervention_roi` | Cost-effectiveness analysis for proposed interventions |
| `generate_executive_brief` | PDF/PPTX/text executive briefing generation |
| `get_equity_analysis` | Disparity ratios across poverty/elderly/disability/uninsured |
| `benchmark_county` | Peer comparison with Z-scores and percentiles |
| `get_real_time_alerts` | Threshold-based monitoring with severity levels |
| `self_improve` | Autonomous capability enhancement meta-tool |

Agent configuration is exported to `models/agent_config.json` for direct import into Archia.

### Demo Mode

The Streamlit dashboard includes a keyword-based query processor (Tab 11: "Agent Query") that demonstrates the agent's intended functionality including advanced feature queries (compound risk, gap analysis, disaster acceleration, redundancy, equity, benchmarking).

---

## Interactive Dashboard

The Streamlit dashboard (`app/dashboard.py`) provides **11 interactive tabs**:

| Tab | Contents |
|-----|----------|
| **Overview** | Key metrics, risk distribution charts, top 20 highest-risk counties |
| **Risk Map** | Interactive Plotly Mapbox scatter map colored by risk score |
| **Geographic Analysis** | 5 visualization modes: density heatmap, scatter map, 3D risk landscape, state choropleth, regional hexbins |
| **Infrastructure** | Facility distance distributions, infrastructure gap identification, vulnerability vs. isolation scatter |
| **Scenario Sim** | What-if disaster simulation with 10 preset types and before/after comparison |
| **Advanced Insights** | Compound risk hotspot map, disaster acceleration trends, infrastructure redundancy analysis, neighbor risk contagion scatter |
| **Gap Analysis** | Intervention recommendation map, gap score breakdown by dimension, state-level county rankings with percentiles |
| **Alert Center** | Threshold-based risk monitoring with critical/warning severity alerts |
| **Benchmarking** | County peer comparison with radar charts, Z-scores, and percentiles |
| **Model Performance** | Model comparison, confusion matrices, ROC curves, feature importance |
| **Agent Query** | Natural language query interface supporting 15+ query patterns |

### Sidebar Filters
- State multi-select
- Risk level filter (Low / Medium / High)
- Population range slider
- Reset Filters button

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
|   |-- feature_engineering.py   # 66 features: 37 core + 29 advanced differentiator analytics
|   |-- eda.py                   # 7 static visualizations (matplotlib/seaborn)
|   |-- train_models.py          # 4 ML models with cross-validation and full evaluation suite
|   |-- agent.py                 # Archia agent: system prompt, 19 MCP tools, advanced query methods
|   |-- scenario_simulator.py    # What-if disaster simulation engine with 10 preset types
|   |-- network_analysis.py      # Infrastructure dependency and cascade risk modeling
|   |-- intervention_roi.py      # Cost-effectiveness analysis for proposed interventions
|   |-- briefing_generator.py    # Executive briefing generation (PDF/PPTX/text)
|   |-- self_improve.py          # Self-recursive improvement and capability enhancement
|   |-- visualization_3d.py      # Geographic visualizations: heatmaps, scatter, 3D landscape, choropleth
|
|-- app/
|   |-- dashboard.py             # Streamlit dashboard with 11 interactive tabs
|
|-- data/
|   |-- raw/                     # Downloaded CSVs from federal APIs (gitignored, regenerated by pipeline)
|   |-- processed/               # county_features.csv: 3,222 x 66 (gitignored, regenerated)
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
|   |-- DATA_DICTIONARY.md       # Column-level documentation for all 66 features
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
2. **Feature Engineering** - Computes 66 features for 3,222 counties (~15 sec)
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
| **Feature Engineering** | 20% | 66 features from 7 sources: KD-tree spatial distances, infrastructure density/redundancy, FEMA disaster history + acceleration trends, Census vulnerability composites, compound risk clusters, gap analysis matrix, risk contagion, population-weighted impact, state rankings |
| **EDA** | 10% | 7 static visualizations + 11-tab interactive Plotly/Mapbox dashboard with 3D risk landscape, scenario simulation, and advanced insight overlays |
| **Evaluation Metrics** | 10% | Accuracy, F1 (macro), precision/recall per class, 5-fold CV with standard deviation, micro-average ROC curves |
| **Novelty** | 10% | Multi-agency federal data fusion, 7 advanced differentiator features (compound risk, contagion, acceleration, redundancy, gap analysis), 19 MCP tools for agentic AI, what-if scenario simulation, executive briefing generation |
| **Presentation** | 10% | 11-tab interactive Streamlit dashboard: Mapbox risk maps, 3D risk landscape, scenario simulation, compound risk overlays, gap analysis maps, alert center, benchmarking, peer comparison radar charts |
| **Problem + Social Good** | 10% | Disaster preparedness for vulnerable communities, actionable gap analysis for FEMA/state emergency management, 100% real federal data |

---

## Team

**MUIDSI Hackathon 2026**

---

## License

Academic use -- MUIDSI Hackathon 2026 submission.
