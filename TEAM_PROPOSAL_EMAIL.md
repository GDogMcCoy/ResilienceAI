# Team Proposal Email - ResilienceAI

**Subject:** Hackathon Project Proposal: "ResilienceAI" - Disaster Vulnerability & Health Infrastructure Gap Agent

---

Hi team,

I've been working on scoping out our project for the MUIDSI Hackathon and wanted to propose a direction before we get too deep into the weekend. I've already built a working prototype so we can hit the ground running.

## The Idea: ResilienceAI

**Problem:** When disasters strike, vulnerable communities with limited healthcare infrastructure suffer disproportionately. Emergency planners currently lack tools to quickly identify which areas face the greatest compound risk - combining disaster exposure, infrastructure gaps, and demographic vulnerability.

**Our Solution:** An AI-powered agent that lets emergency planners query community vulnerability data in natural language and receive automated risk assessments with interactive maps.

Example queries:
- "Show me the most vulnerable communities in Missouri for flooding"
- "Which counties have the worst hospital access during tornadoes?"
- "What areas have high elderly populations AND low shelter coverage?"

## Why This Wins (Mapped to Scoring Rubric)

| Category (Weight) | Our Strength |
|---|---|
| **Model Development (30%)** | 4 trained models: Random Forest, Gradient Boosting, Logistic Regression (F1=0.983), Neural Net. Cross-validation, SHAP explainability. |
| **Feature Engineering (20%)** | 27 engineered features: distance-to-nearest facilities, infrastructure density, vulnerability composites, disaster history, spatial isolation |
| **EDA (10%)** | Interactive maps, correlation heatmaps, distribution analysis, geographic visualizations - all generated |
| **Eval Metrics (10%)** | ROC-AUC, F1, precision-recall, confusion matrices, 5-fold CV |
| **Novelty (10%)** | Combines 5 real federal data sources (HIFLD, FEMA, Census, CMS) into a single agent-queryable platform |
| **Presentation (10%)** | Interactive Streamlit dashboard + natural language agent = compelling 10-min video |
| **Problem + Social Good (10%)** | Disaster preparedness literally saves lives. Marketable to FEMA and state emergency agencies. |

## Data Sources (All Real, All Downloaded)

| Source | Records | What It Provides |
|--------|---------|-----------------|
| HIFLD/FEMA (hospitals) | 7,496 | Hospital locations with coordinates |
| HIFLD/FEMA (fire stations) | 52,051 | Fire station coverage nationwide |
| HIFLD/FEMA (EMS stations) | 7,045 | Emergency medical service locations |
| CMS Medicare (nursing homes) | 14,713 | Nursing home locations + bed counts |
| FEMA OpenFEMA (disasters) | 69,615 | Historical disaster declarations by county |
| Census ACS (demographics) | 3,222 | County-level poverty, elderly, disability, uninsured rates |
| Census Gazetteer (centroids) | 3,222 | County geographic coordinates |

All from approved data sources - no synthetic data, no registration barriers.

## What's Already Done (Day 1 - Completed)

I have a **fully working prototype** with:
- All 7 data sources downloaded and cached (153K+ records)
- 27 engineered features across all 3,222 US counties
- 4 trained ML models (best: Logistic Regression, F1=0.983)
- 7 EDA visualizations (risk maps, correlations, distributions)
- 5-tab Streamlit dashboard running with interactive Mapbox maps
- Agent query interface (demo mode)

**Live demo:** http://localhost:8503 (running on my machine - happy to screenshare or deploy)

## What's Left for the Team (Day 2-3)

Here's where teammates can plug in:

1. **Archia agent setup** - Deploy the agent on console.archia.app with MCP database tools (HIGH)
2. **Dashboard polish** - Improve map interactivity, county detail views, styling (MEDIUM)
3. **SHAP explainability** - Add feature importance explanations per prediction (MEDIUM)
4. **Presentation** - Script and record 10-min video, create slides (CRITICAL)
5. **Additional features** - Hyperparameter tuning, geospatial train/test split (NICE-TO-HAVE)

## Timeline

- **Saturday (Done):** Data acquisition, feature engineering, EDA, model training, dashboard v1
- **Sunday:** Archia agent deployment, dashboard polish, team onboarding
- **Monday:** Final polish, script + record 10-min video, submit by 11:59 PM

## Next Steps

If you're on board (or have modifications), let me know and I can:
- Share the codebase via GitHub
- Screenshare the live dashboard
- Jump on a call to walk through the framework

If anyone has a competing idea they feel strongly about, let's discuss ASAP - we need to commit to a direction today.

Best,
Garren

---

*Tech Stack: Python (pandas, scikit-learn, xgboost, geopandas, folium, plotly), Streamlit, Archia Cloud, SQLite*
*Data: HIFLD, FEMA, Census ACS, CMS Medicare - all federal open data*
