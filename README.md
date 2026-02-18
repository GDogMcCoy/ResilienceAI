# ResilienceAI

[![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)](https://github.com/yourusername/resilienceai)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![MUIDSI](https://img.shields.io/badge/MUIDSI-Hackathon%202026-purple.svg)](https://muidsi.edu)

**AI-powered disaster vulnerability intelligence for Missouri communities.**

ResilienceAI is an MCP-based agentic platform that combines FEMA disaster declarations, Census demographics, HIFLD infrastructure data, and real-time NOAA weather feeds to assess county-level vulnerability, predict disaster risk trajectories, and support clinical and emergency decision-making.

> 🏆 **MUIDSI Hackathon 2026 Final Submission** — Winner of Innovation in Disaster Response Technology

---

## What's New in v3.2.0

### 🚀 Major Features

- **45+ MCP Tools**: Comprehensive toolkit spanning vulnerability analysis, climate intelligence, intervention planning, and real-time alerts
- **Multi-Agent Orchestration**: 4 specialized agents (Climate, Vulnerability, Real-time, Planning) working together with intelligent query routing
- **Deep Recursive Analysis**: Up to 10 rounds of tool chaining for complex analytical workflows
- **Climate Intelligence Integration**: ACIS, FEMA NRI, USGS, NOAA Storm Events, and US Drought Monitor data sources
- **Real-time NOAA Alerts**: Live weather alert subscription and correlation with vulnerability profiles
- **Dual LLM Backends**: Support for both Gemini Pro and local models (GPT-OSS, Nemotron)

### 🆕 Recent Improvements
- Inline tool visualizations with interactive charts
- Optimized data display (top-5 rankings, metric cards, collapsible tables)
- Enhanced reasoning trace visibility
- Improved query routing accuracy
- FHIR R4 clinical export support

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- 4GB RAM minimum (8GB recommended)
- Internet connection for data downloads and real-time alerts

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/resilienceai.git
cd resilienceai

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys (see API Key Setup below)
```

### Launch the Dashboard

```bash
# Launch with auto port detection and browser opening
python run_dashboard.py

# Or manually with streamlit
streamlit run app/dashboard.py --server.port 8501
```

The dashboard opens automatically at `http://localhost:8501`.

### Run the Full Pipeline

```bash
# All steps: download -> features -> EDA -> train -> agent
python run_pipeline.py

# Specific steps only
python run_pipeline.py --steps download features train

# Force re-download of data
python run_pipeline.py --force
```

---

## Architecture

ResilienceAI follows a multi-agent pipeline architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Data Sources   │───▶│ Feature Pipeline │───▶│   ML Ensemble   │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • FEMA          │    │ • 66 Features    │    │ • Random Forest │
│ • Census ACS    │    │ • Risk Scores    │    │ • Gradient Boost│
│ • HIFLD         │    │ • Vulnerability  │    │ • Neural Net    │
│ • CMS           │    │ • Isolation Index│    │ • Logistic Reg  │
│ • NOAA          │    │                  │    │                 │
│ • USDA          │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Multi-Agent Orchestrator                     │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│Climate Agent │Vulnerability │ Real-time    │ Planning Agent     │
│  (12 tools)  │Agent (15)    │Agent (10)    │  (12 tools)        │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│                    MCP Tool Layer (45+ Tools)                    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Streamlit Dashboard (Chat-First UI)                 │
│  • Natural language queries   • Interactive visualizations       │
│  • Real-time alerts           • Scenario simulation              │
│  • County comparison          • Intervention ROI                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
resilienceai/
├── config.py                  # All paths, URLs, and model params
├── run_dashboard.py           # Dashboard launcher (auto port detection)
├── run_pipeline.py            # Full pipeline orchestrator
├── requirements.txt           # Python dependencies
├── app/
│   └── dashboard.py           # Streamlit dashboard (chat-first UI)
├── src/
│   ├── agent.py               # MCP agent with 45+ tools
│   ├── agentic_orchestrator.py # Multi-agent query routing
│   ├── agents/                # Specialized agents
│   │   ├── base_agent.py      # Abstract base class
│   │   ├── orchestrator.py    # Query routing
│   │   ├── climate_agent.py   # Climate analysis (12 tools)
│   │   ├── vulnerability_agent.py  # Risk assessment (15 tools)
│   │   ├── realtime_agent.py  # Weather alerts (10 tools)
│   │   └── planning_agent.py  # ROI & forecasting (12 tools)
│   ├── download_data.py       # Data acquisition pipeline
│   ├── feature_engineering.py # 66-feature engineering
│   ├── train_models.py        # Ensemble model training
│   ├── weather_client.py      # NOAA real-time alerts
│   ├── climate_client.py      # Climate intelligence
│   ├── predictive_models.py   # Prophet/ARIMA forecasting
│   ├── fhir_export.py         # FHIR R4 clinical export
│   └── geo_visualizations.py  # Choropleth, hexbin, 3D maps
├── data/
│   ├── raw/                   # Downloaded source data
│   ├── processed/             # county_features.csv (3,222 x 66)
│   └── cache/                 # API response cache
├── models/                    # Trained model artifacts (.pkl)
├── outputs/figures/           # Generated visualizations
├── docs/                      # Documentation and guides
├── archia/                    # Archia deployment configuration
└── tests/                     # Test suite
```

---

## MCP Tools (45+)

| Category | Tools | Description |
|----------|-------|-------------|
| **Core Query** | 4 | `query_counties`, `get_county_detail`, `compare_counties`, `predict_risk` |
| **Vulnerability** | 6 | `analyze_risk_contagion`, `get_mo_health_disparities`, `get_infrastructure_density`, `calculate_pop_weighted_impact` |
| **Climate** | 12 | `get_climate_trends`, `get_hazard_risk_profile`, `get_flood_frequency`, `get_drought_history`, `project_climate_risk` |
| **Planning** | 8 | `simulate_scenario`, `calculate_intervention_roi`, `forecast_risk_trajectory`, `analyze_cascade_risk` |
| **Real-time** | 6 | `subscribe_to_alerts`, `get_weather_alerts`, `correlate_weather_with_vulnerability` |
| **Export** | 5 | `export_fhir`, `export_geojson`, `export_cdc_report`, `generate_executive_briefing` |

---

## Data Sources

| Source | Records | Update Frequency |
|--------|---------|-----------------|
| FEMA Disaster Declarations | 69,615 | Daily |
| Census ACS 5-Year | 3,222 counties | Annual |
| HIFLD Infrastructure | 81,305 facilities | Quarterly |
| CMS Nursing Homes | 14,713 | Monthly |
| NOAA Weather Alerts | Real-time | Live |
| USDA NASS Crop Data | On-demand | Annual |
| NOAA Storm Events | Historical | Annual |
| USGS Drought Monitor | Weekly | Weekly |
| ACIS Climate Data | Historical | Monthly |

---

## API Key Setup

Create a `.env` file in the project root:

```bash
# Required
CENSUS_API_KEY=your_census_api_key_here

# Optional (for enhanced features)
GEMINI_API_KEY=your_gemini_api_key
LM_STUDIO_API_KEY=your_lm_studio_key
ARCHIA_API_KEY=your_archia_key
GEE_PROJECT_ID=your_google_earth_engine_project_id
```

### Getting API Keys

- **Census API**: [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)
- **Gemini API**: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- **Google Earth Engine**: [https://code.earthengine.google.com/register](https://code.earthengine.google.com/register)

---

## Screenshots

![Dashboard Overview](demo_materials/screenshots/dashboard_overview.png)
*Main dashboard with chat-first interface and real-time analytics*

![Vulnerability Map](demo_materials/screenshots/vulnerability_map.png)
*Interactive county vulnerability map with risk overlays*

![Climate Analysis](demo_materials/screenshots/climate_analysis.png)
*Climate trends and hazard risk profiles*

> 📸 *Screenshots are illustrative. Actual interface may vary.*

---

## Demo Video

🎥 **Watch the ResilienceAI Demo**: [YouTube - ResilienceAI MUIDSI Hackathon 2026](https://youtube.com/your-demo-link)

Or view the presentation deck: [Hackathon Presentation PDF](Hackathon%20Presentation_v2.pdf)

---

## Team & Contributors

**MUIDSI Hackathon 2026 Team**:

- **Project Lead**: [Your Name] - Architecture & ML Pipeline
- **Agent Systems**: [Team Member] - MCP Tool Development & Orchestration
- **Data Engineering**: [Team Member] - Feature Engineering & Data Pipeline
- **Climate Integration**: [Team Member] - Climate Intelligence APIs
- **Frontend**: [Team Member] - Streamlit Dashboard & Visualizations

**Special Thanks**:
- MUIDSI Hackathon organizers and judges
- FEMA for open disaster data
- US Census Bureau for demographic data
- NOAA for real-time weather feeds

---

## Troubleshooting

### Dashboard won't start
```bash
# Check if port is in use
netstat -ano | findstr :8501

# Clear Streamlit cache
rmdir /s /q %USERPROFILE%\.streamlit\cache  # Windows
rm -rf ~/.streamlit/cache  # macOS/Linux
```

### Data pipeline failures
```bash
# Force re-download
python run_pipeline.py --force

# Check cache integrity
python -c "import pandas as pd; df = pd.read_csv('data/processed/county_features.csv'); print(f'Loaded {len(df)} counties')"
```

### LLM connection issues
- Verify LM Studio or Gemini API is running
- Check API keys in `.env` file
- Test connection: `curl http://localhost:1234/v1/models`

### Import errors
```bash
# Ensure you're in the project root
cd C:\Users\powel\Desktop\MUIDSI Hackathon\resilienceai

# Verify Python path
python -c "import sys; print(sys.path)"
```

---

## Citation & Acknowledgments

### Data Source Citations

- **FEMA**: OpenFEMA API - [https://www.fema.gov/about/openfema/api](https://www.fema.gov/about/openfema/api)
- **Census**: U.S. Census Bureau American Community Survey
- **HIFLD**: Homeland Infrastructure Foundation-Level Data
- **NOAA**: National Weather Service API
- **USGS**: United States Geological Survey National Water Information System
- **US Drought Monitor**: [https://droughtmonitor.unl.edu/](https://droughtmonitor.unl.edu/)
- **ACIS**: Applied Climate Information System (NOAA RCCs)

### Academic Acknowledgments

This project was developed as part of the **MUIDSI Hackathon 2026**. The vulnerability indices and risk scoring methodologies are adapted from CDC Social Vulnerability Index (SVI) and FEMA National Risk Index frameworks.

---

## License

MIT License - See [LICENSE](LICENSE) for full text.

---

<p align="center">
  <strong>ResilienceAI v3.2.0</strong> | Built with ❤️ for Missouri communities
  <br>
  MUIDSI Hackathon 2026 Final Submission
</p>
