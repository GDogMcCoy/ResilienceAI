# Contributing to ResilienceAI

## For Teammates

### Getting Started

1. Clone the repo
2. Run `pip install -r requirements.txt`
3. Run `python run_pipeline.py` (downloads data + trains models, ~5 min first time)
4. Run `streamlit run app/dashboard.py --server.port 8503`
5. Read `docs/DATA_DICTIONARY.md` for feature definitions

### Where to Contribute

| Area | File(s) | What's Needed |
|------|---------|---------------|
| Archia Agent | `src/agent.py`, `models/agent_config.json` | Deploy on console.archia.app, wire up MCP tools |
| Dashboard | `app/dashboard.py` | Geospatial overlays, county detail views, styling |
| SHAP Analysis | `src/train_models.py` | Add SHAP summary plots for model explainability |
| Video | -- | Script and record 10-min presentation |
| Data Quality | `src/feature_engineering.py` | Handle Census sentinel values, verify FEMA incident types |

### Code Conventions

- All print statements must use ASCII characters (no unicode arrows/emojis -- Windows cp1252 compatibility)
- New data sources go in `config.py` (URL) + `src/download_data.py` (download logic)
- New features go in `src/feature_engineering.py`
- Use `data/cache/` for API response caching to avoid re-downloads
- Test changes by running `python run_pipeline.py --steps features eda train`
