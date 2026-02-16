# ResilienceAI - Gemini CLI Context

This project, **ResilienceAI**, is an AI-powered platform for disaster vulnerability assessment across US counties. It combines machine learning, geospatial analysis, and natural language querying to provide actionable insights for emergency planners and policymakers.

## Project Overview

- **Purpose:** Analyze infrastructure gaps, demographic vulnerability, and historical disaster data to assess community risk.
- **Core Technologies:**
    - **Frontend:** Streamlit (16-tab dashboard with modern UI components).
    - **Backend:** Python (Pandas, NumPy, Scikit-learn).
    - **Agent Integration:** Archia MCP (Model Context Protocol) with 45 custom tools.
    - **Data Visualization:** Plotly, Folium (GeoJSON/Choropleth/Hexbin/3D).
    - **Forecasting:** Prophet/ARIMA for risk trajectory and climate scenario modeling.
- **Architecture:**
    - `app/dashboard.py`: Main Streamlit entry point.
    - `src/agent.py`: Implementation of MCP tools and `ResilienceAgent`.
    - `src/archia_client.py`: API client for Archia agent runtime.
    - `src/predictive_models.py`: Forecasting and climate modeling logic.
    - `data/processed/county_features.csv`: Primary dataset.
    - `models/`: Pre-trained ML models and scalers.

## Building and Running

### 1. Prerequisites
- Python 3.9+
- Pip

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
    1. Implementing the logic in `src/`.
    2. Defining the tool in `src/agent.py:get_mcp_tools()`.
    3. Implementing the tool's execution method in `ResilienceAgent`.
    4. Mapping the tool in `archia/mcp-servers.toml`.
- **Data Persistence:** Use `config.py` for directory paths (`DATA_DIR`, `MODELS_DIR`, etc.).
- **UI Components:** Use `src/modern_ui.py` for consistent styling across the dashboard.

## Key Files & Directories

- `🚀 run_dashboard.py`: Main launcher.
- `📊 app/`: Streamlit dashboard source.
- `🔧 src/`: Core business logic and agent tools.
- `⚙️ archia/`: Agent deployment and MCP configurations.
- `📁 data/`: Raw and processed county datasets.
- `🧠 models/`: Joblib-serialized ML models.
- `📖 docs/`: Detailed documentation for API, setup, and data.

## Deployment

Deploy to Archia using the provided script:
```bash
./deploy-to-archia.sh
```
Requires `ARCHIA_API_KEY` to be set in `.env.archia` or as an environment variable.
