# ResilienceAI - Agent Development Guide

This document provides essential information for AI coding agents working on the ResilienceAI project.

## Project Overview

**ResilienceAI** is an MCP-based agentic platform that combines FEMA disaster declarations, Census demographics, HIFLD infrastructure data, and real-time NOAA weather feeds to assess county-level vulnerability, predict disaster risk trajectories, and support clinical and emergency decision-making.

Built for the MUIDSI Hackathon 2026, the platform features a multi-agent orchestration system with 45+ MCP tools and a Streamlit dashboard with 16+ tabs.

## Technology Stack

| Category | Technologies |
|----------|--------------|
| **Language** | Python 3.10+ |
| **ML/Data** | scikit-learn, pandas, numpy, scipy, shap |
| **Geospatial** | geopandas, shapely, earthengine-api |
| **Visualization** | plotly, matplotlib, seaborn, streamlit |
| **LLM Integration** | Archia Cloud API, LM Studio, Gemini API |
| **Data Export** | fhir.resources (FHIR R4 clinical export) |
| **Vector Search** | sentence-transformers, faiss-cpu, umap-learn |

## Project Structure

```
resilienceai/
├── config.py                  # Central configuration: paths, URLs, model params
├── run_dashboard.py           # Dashboard launcher with auto port detection
├── run_pipeline.py            # Full pipeline orchestrator
├── requirements.txt           # Python dependencies
├── .env.archia               # Archia cloud credentials
├── .streamlit/config.toml    # Streamlit theme configuration
│
├── app/
│   └── dashboard.py          # Streamlit dashboard (16+ tabs)
│
├── src/                      # Main source code
│   ├── agent.py              # Main MCP agent with 45 tools
│   ├── agentic_orchestrator.py  # Agent query orchestration
│   ├── download_data.py      # Data acquisition from FEMA, Census, HIFLD
│   ├── feature_engineering.py   # 66-feature engineering pipeline
│   ├── train_models.py       # Ensemble model training (RF, GB, NN, LR)
│   ├── weather_client.py     # NOAA real-time alerts
│   ├── climate_client.py     # Climate intelligence (ACIS, NRI, USGS)
│   ├── predictive_models.py  # Prophet/ARIMA forecasting
│   ├── fhir_export.py        # FHIR R4 clinical export
│   ├── geo_visualizations.py # Choropleth, hexbin, 3D maps
│   ├── scenario_simulator.py # Disaster scenario modeling
│   ├── intervention_roi.py   # Cost-effectiveness analysis
│   ├── briefing_generator.py # Executive brief generation
│   ├── alert_manager.py      # Real-time alert system
│   ├── archia_client.py      # Archia cloud integration
│   ├── agents/               # Specialized agents
│   │   ├── base_agent.py     # Abstract base class for all agents
│   │   ├── orchestrator.py   # Multi-agent query routing
│   │   ├── climate_agent.py  # Climate analysis specialist
│   │   ├── vulnerability_agent.py  # Vulnerability assessment
│   │   ├── realtime_agent.py # Real-time alerts specialist
│   │   ├── planning_agent.py # ROI and forecasting
│   │   └── langgraph_flow.py # LangGraph state machine
│   ├── geospatial/           # Geospatial processing
│   └── llm_providers/        # LLM provider integrations
│
├── data/                     # Data storage
│   ├── raw/                  # Downloaded source data
│   ├── processed/            # county_features.csv (3,222 x 66)
│   └── cache/                # API response cache
│
├── models/                   # Trained model artifacts (.pkl)
├── outputs/figures/          # Generated visualizations
├── docs/                     # Documentation and reports
├── archia/                   # Archia deployment configuration
├── tests/                    # Test suite
└── examples/                 # Usage examples
```

## Build and Run Commands

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### Dashboard Launch
```bash
# Launch the dashboard (auto-detects port, opens browser)
python run_dashboard.py

# Or manually with streamlit
streamlit run app/dashboard.py --server.port 8501
```

### Data Pipeline
```bash
# Run full pipeline: download -> features -> EDA -> train -> agent
python run_pipeline.py

# Run specific steps only
python run_pipeline.py --steps download features train

# Force re-download of data
python run_pipeline.py --force
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_orchestration.py -v
```

## Code Style Guidelines

### Python Style
- Follow **PEP 8** guidelines
- Use **type hints** for function signatures
- Document public APIs with docstrings (Google style)
- Keep functions focused and small (single responsibility)

### Module Patterns
```python
"""
ResilienceAI - Module Description
One-line summary of purpose.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports grouped: stdlib, third-party, local
import pandas as pd
from config import PROCESSED_DIR, MODELS_DIR
```

### Configuration Management
- **ALL** paths, URLs, and parameters are in `config.py`
- Use `Path` objects from pathlib for file paths
- Environment variables for secrets (CENSUS_API_KEY, ARCHIA_API_KEY, etc.)
- Never hardcode paths or URLs in individual modules

### Agent Development
- All specialized agents inherit from `BaseAgent`
- Implement required abstract methods: `system_prompt`, `get_tools()`, `execute_tool()`
- Register tool handlers in `_register_tool_handlers()`
- Use `intent_keywords` for query routing

## Testing Instructions

### Test Structure
- `tests/test_orchestration.py` - Multi-agent routing and orchestration
- `tests/test_dashboard_logic.py` - Dashboard component tests
- `tests/test_archia_pipeline.py` - Archia cloud integration
- `tests/test_geospatial_pipeline.py` - Geospatial processing
- `tests/test_llm_integration.py` - LLM provider tests
- `tests/test_vector_space.py` - Vector search functionality
- `tests/test_visualizations.py` - Visualization components

### Writing Tests
```python
import unittest
from unittest.mock import Mock, patch
from src.agents.base_agent import BaseAgent, AgentOutput

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        # Setup test fixtures
        pass
    
    def test_specific_behavior(self):
        # Test implementation
        pass
```

### Running Tests
```bash
# With coverage
pytest --cov=src --cov-report=html

# With debugger on failure
pytest --pdb
```

## Key Architecture Patterns

### 1. Multi-Agent Orchestration
The system uses 4 specialized agents coordinated by `AgentOrchestrator`:
- **ClimateAgent**: Climate trends, hazard profiles, drought monitoring
- **VulnerabilityAgent**: County risk, infrastructure, demographics
- **RealtimeAgent**: Weather alerts, subscriptions, emergency dispatch
- **PlanningAgent**: Intervention ROI, forecasting, agriculture

### 2. MCP Tool System
Tools are defined as JSON schemas and registered with handlers:
```python
def get_tools(self) -> List[Dict[str, Any]]:
    return [{
        "name": "tool_name",
        "description": "What it does",
        "parameters": {"type": "object", "properties": {...}}
    }]

def execute_tool(self, tool_name: str, params: Dict) -> Dict:
    if tool_name in self._tool_handlers:
        return self._tool_handlers[tool_name](**params)
```

### 3. Data Pipeline Flow
```
Raw Data -> Feature Engineering -> Model Training -> Agent Configuration
     ↑              ↓                      ↓              ↓
   Cache      county_features.csv    Models (.pkl)   agent_config.json
```

### 4. Configuration Pattern
All configurations centralized in `config.py`:
- `DATA_SOURCES` - API endpoints for FEMA, Census, etc.
- `FEATURE_GROUPS` - Feature categorization (demographics, infrastructure, etc.)
- `MODEL_CONFIG` - Training parameters (test_size, random_state, cv_folds)
- `AGENT_CONFIG` - LLM parameters (temperature, max_tokens)
- `CLIMATE_SOURCES` - Climate data endpoints with cache TTL

## Environment Variables

Create `.env` file in project root:
```bash
# Required
CENSUS_API_KEY=your_census_api_key_here

# Optional
GEE_PROJECT_ID=your_google_earth_engine_project_id
GEMINI_API_KEY=your_gemini_api_key
LM_STUDIO_API_KEY=your_lm_studio_key
ARCHIA_API_KEY=your_archia_key
ARCHIA_ENDPOINT=https://api.archia.app/v1
```

## Security Considerations

### API Keys
- **NEVER** commit API keys to git
- Use environment variables or `.env` files
- `.env.archia` contains Archia credentials - do not commit

### Data Handling
- No PII in processed datasets (county-level aggregates only)
- FHIR export follows clinical data standards
- Cache files may contain sensitive API responses

### Dependencies
- `requirements.txt` pins minimum versions, not exact
- Review security advisories for geospatial packages
- Google Earth Engine requires authentication setup

## Common Development Tasks

### Adding a New MCP Tool
1. Define tool schema in agent's `get_tools()` method
2. Register handler in `_register_tool_handlers()`
3. Implement handler method
4. Add test in appropriate test file
5. Update tool count in documentation

### Adding a New Agent
1. Create file in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement abstract methods
4. Register in `AgentOrchestrator.__init__()`
5. Add routing keywords to intent classification

### Adding Data Sources
1. Add URL/configuration to `config.py` `DATA_SOURCES` or `CLIMATE_SOURCES`
2. Implement download logic in `src/download_data.py`
3. Add feature engineering in `src/feature_engineering.py` if needed
4. Update data dictionary documentation

### Dashboard Modifications
- Main dashboard: `app/dashboard.py`
- Theme config: `.streamlit/config.toml`
- Add new tabs by creating functions and calling them in main layout
- Session state keys defined in `init_session_state()`

## Troubleshooting

### Import Errors
- Ensure `sys.path.insert(0, ...)` is at module top
- Check virtual environment is activated
- Verify `config.py` is importable from module location

### Data Pipeline Failures
- Check cache files in `data/cache/` for corruption
- Use `--force` flag to re-download
- Verify API keys are set correctly

### Dashboard Issues
- Port conflict: Script auto-detects ports 8501-8510
- Clear Streamlit cache: `rm -rf ~/.streamlit/cache`
- Check browser console for JavaScript errors

## External Dependencies

### Data Sources
| Source | Records | Frequency |
|--------|---------|-----------|
| FEMA Disaster Declarations | 69,615 | Daily |
| Census ACS 5-Year | 3,222 counties | Annual |
| HIFLD Infrastructure | 81,305 facilities | Quarterly |
| CMS Nursing Homes | 14,713 | Monthly |
| NOAA Weather Alerts | Real-time | Live |

### APIs and Services
- **Archia Cloud**: Agent orchestration platform (`https://api.archia.app/v1`)
- **Google Earth Engine**: Satellite data processing
- **US Census API**: Demographic data (`api.census.gov`)
- **FEMA Open API**: Disaster declarations
- **NOAA**: Real-time weather alerts

## Documentation References

- `docs/SETUP_GUIDE.md` - Complete setup instructions
- `docs/API_REFERENCE.md` - API documentation
- `docs/DATA_DICTIONARY.md` - Feature descriptions
- `docs/PREDICTIVE_MODELING.md` - Model documentation
- `README.md` - Project overview

## License

MIT License - See project root for full license text.

---

*This document is maintained for AI coding agents. For human contributors, see `docs/CONTRIBUTING.md`.*
