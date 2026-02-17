# ResilienceAI - Gemini CLI Context

This project, **ResilienceAI**, is an AI-powered platform for disaster vulnerability assessment across all 3,222 US counties. It combines machine learning, geospatial analysis, and natural language querying to provide actionable insights for emergency planners, public health officials, and policymakers.

## Project Overview

- **Purpose:** Analyze infrastructure gaps, demographic vulnerability, and historical disaster data to assess community risk and prioritize interventions.
- **Core Technologies:**
    - **Frontend:** Streamlit (5-tab "Hero Dashboard" with Esoteric Noir UI).
    - **Backend:** Python (Pandas, NumPy, Scikit-learn, Joblib).
    - **Agent Integration:** Archia MCP (Model Context Protocol) with **45+ custom tools**.
    - **Data Visualization:** Plotly, Mapbox (3D Hexbin/Choropleth), PyDeck.
    - **Interoperability:** FHIR R4 (Health Systems), GeoJSON (GIS), Webhooks (Alerts).
- **Architecture:**
    - `app/dashboard.py`: Main Streamlit entry point (Streamlined Focus Edition).
    - `src/agent.py`: Implementation of `ResilienceAgent` and 45+ MCP tool definitions.
    - `src/archia_client.py`: API client for Archia agent runtime.
    - `src/fhir_export.py`: FHIR R4 export for health system EHR integration.
    - `src/geojson_export.py`: GeoJSON export for GIS professional workflows.
    - `src/spatial_stats.py`: Moran's I and Getis-Ord Gi* spatial autocorrelation analysis.
    - `src/alert_manager.py`: Multi-channel real-time alert system (Webhook, SMS, Email).
    - `src/predictive_models.py`: Forecasting and climate scenario modeling logic.
    - `data/processed/county_features.csv`: Primary dataset (66 features per county).
    - `models/`: Pre-trained ML models (Gradient Boosting, Random Forest, etc.).

## Key Capabilities

- **Agentic Intelligence:** Natural language interface powered by Archia MCP, capable of multi-step reasoning, tool execution, and self-improvement.
- **Health System Integration:** Direct export of vulnerability data as FHIR Resources (Location, RiskAssessment, Observation).
- **Advanced Spatial Stats:** Identification of statistically significant hotspots and coldspots using global and local spatial autocorrelation.
- **Real-Time Alerting:** Subscribe to counties and receive automated notifications when risk thresholds are exceeded or disasters are dispatched.
- **Sector Analysis:** Specialized analysis for Healthcare disparities (Missouri focus) and Agricultural vulnerability.

## Building and Running

### 1. Prerequisites
- Python 3.9+
- Pip
- (Optional) Archia API Key for production intelligence.

### 2. Setup
```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Dashboard
The easiest way to start the application:
```bash
python run_dashboard.py
```
This script auto-detects a free port (8501-8510) and opens your browser.

Manual start:
```bash
streamlit run app/dashboard.py
```

### 4. Diagnostics
If you encounter connection or environment issues, run:
```bash
python diagnose.py
```

## Development Conventions

- **Coding Style:** Standard Python PEP 8.
- **Modularity:** New capabilities should be added as modules in `src/` and integrated into `ResilienceAgent` in `src/agent.py`.
- **MCP Tools:** Adding a new analytical capability involves:
    1. Implementing the logic in a new or existing `src/` module.
    2. Defining the tool in `src/agent.py:get_mcp_tools()`.
    3. Implementing the tool's execution method in `ResilienceAgent` class.
    4. Mapping the tool in `archia/mcp-servers.toml` for remote execution.
- **UI Components:** Use `src/modern_ui.py` and `sac` (streamlit-antd-components) for consistent styling.

## Key Files & Directories

- `🚀 run_dashboard.py`: Main launcher.
- `📊 app/`: Streamlit dashboard source.
- `🔧 src/`: Core business logic, data clients, and agent tools.
- `⚙️ archia/`: Agent deployment and MCP configurations.
- `📁 data/`: Raw, processed, and cached datasets.
- `🧠 models/`: Joblib-serialized ML models and scalers.
- `📖 docs/`: Detailed documentation including `DATA_DICTIONARY.md` and `SETUP_GUIDE.md`.

## Deployment

Deploy to Archia using the provided script:
```bash
./deploy-to-archia.sh
```
Requires `ARCHIA_API_KEY` to be set in `.env.archia` or as an environment variable.
