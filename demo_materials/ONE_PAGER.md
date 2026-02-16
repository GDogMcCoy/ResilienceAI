# ResilienceAI - One-Pager Summary
## MUIDSI Hackathon 2026 Submission

---

## PROJECT OVERVIEW

**ResilienceAI** is a production-ready Disaster Vulnerability & Health Infrastructure Gap Assessment Agent that transforms disaster preparedness from reactive to predictive through true agentic AI capabilities.

**The Problem:** Emergency managers spend hours analyzing siloed data from FEMA, Census, and health systems to answer simple questions like "Which counties are most vulnerable to flooding?" By the time they have answers, disasters have already struck.

**The Solution:** ResilienceAI unifies 157,363 records from 7 federal data sources into a single platform with natural language querying, predictive analytics, and direct health system integration via FHIR R4.

---

## KEY STATS

| Metric | Value |
|--------|-------|
| **Counties Analyzed** | 3,222 (100% US coverage) |
| **Facilities Mapped** | 157,363 |
| **MCP Tools** | 29 |
| **Engineered Features** | 66 per county |
| **Data Sources** | 7 federal agencies |
| **ML Model F1 Score** | 98.3% |
| **Query Response Time** | < 2 seconds |
| **Dashboard Tabs** | 12 interactive |
| **Export Formats** | FHIR R4, GeoJSON |

---

## UNIQUE SELLING POINTS

### 1. True Agentic AI (Not Keyword Matching)
ResilienceAI uses the Archia MCP runtime with 29 specialized tools. The agent reasons about query intent, selects appropriate analytical tools, and generates data-backed responses with citations.

**Example:** "Which Missouri counties are most vulnerable to flooding?"
- Parses: Missouri, flooding, vulnerability
- Selects: query_counties + disaster_flood filter
- Returns: Prioritized list with citations

### 2. FHIR R4 Health System Integration
The only disaster vulnerability tool with native EHR integration. Export vulnerability data as FHIR Bundles for direct import into Epic, Cerner, and other health systems.

**Use Case:** Hospital emergency departments can incorporate county-level disaster risk into clinical decision support.

### 3. 66 Engineered Features
Comprehensive vulnerability assessment with 37 core features + 29 advanced differentiators:
- Compound risk clusters
- Risk contagion analysis
- Disaster acceleration trends
- Zero redundancy detection
- Population-weighted prioritization
- Gap analysis for interventions

### 4. Spatial Statistics at Scale
Advanced geospatial analysis using:
- KD-tree spatial indexing (O(log n) queries)
- Moran's I for spatial autocorrelation
- Getis-Ord Gi* for hotspot detection

### 5. Production-Ready Architecture
- Kubernetes deployment manifests included
- Horizontal Pod Autoscaler (2-10 replicas)
- REST API for programmatic access
- Comprehensive documentation

---

## TECHNICAL HIGHLIGHTS

### Machine Learning
- **4 classifiers trained:** Random Forest, Gradient Boosting, Logistic Regression, Neural Network
- **Best model:** Logistic Regression with F1 = 0.983
- **Validation:** 5-fold cross-validation with statistical significance testing
- **Task:** 3-class risk classification (Low/Medium/High)

### Data Engineering
- **Unified dataset:** 7 federal sources fused into single county-level dataset
- **Spatial indexing:** KD-tree on 3,222 county centroids
- **Feature engineering:** 66 features including 7 advanced differentiator categories
- **Data quality:** 100% real data, no synthetic records

### Agent Architecture
- **MCP runtime:** Archia for tool orchestration
- **Tool inventory:** 29 tools (query, analysis, export, meta)
- **Reasoning:** Multi-step problem solving with context awareness
- **Self-improvement:** Response quality evaluation and optimization

### Integration Capabilities
- **FHIR R4:** Location, RiskAssessment, Observation resources
- **GeoJSON:** WGS84 compliant for GIS workflows
- **REST API:** 4 endpoints for programmatic access
- **Dashboard:** 12-tab Streamlit interface

---

## REAL-WORLD IMPACT

### For FEMA
- Pre-position resources before disasters strike
- Identify compound risk counties for priority response
- Optimize resource allocation across 3,222 counties

### For State Health Departments
- Identify hospital deserts (zero redundancy counties)
- Plan capacity expansion and mutual aid agreements
- Integrate vulnerability data into HPP capabilities

### For Emergency Managers
- Run scenario simulations for training exercises
- Get instant answers to complex vulnerability questions
- Export data for stakeholder presentations

### For Rural Hospitals
- Identify single points of failure in service area
- Plan patient transfer protocols
- Model surge capacity under disaster scenarios

---

## COMPETITIVE DIFFERENTIATION

| Capability | ResilienceAI | FEMA Tools | Commercial GIS |
|------------|--------------|------------|----------------|
| Natural Language Queries | ✅ | ❌ | ❌ |
| Agentic AI Reasoning | ✅ | ❌ | ❌ |
| FHIR EHR Integration | ✅ | ❌ | ❌ |
| 66 Engineered Features | ✅ | ❌ | ⚠️ |
| Compound Risk Detection | ✅ | ⚠️ | ⚠️ |
| Real-time Alerts | ✅ | ⚠️ | ⚠️ |
| Open Source | ✅ | ❌ | ❌ |
| Spatial Statistics | ✅ | ⚠️ | ✅ |

**Why ResilienceAI Wins:** Only tool combining true agentic AI, health system integration, comprehensive vulnerability features, and open-source accessibility.

---

## DATA SOURCES

All data from authoritative federal sources:

| Source | Records | Description |
|--------|---------|-------------|
| FEMA Open | 69,615 | Disaster declarations (1953-present) |
| Census ACS | 3,222 | County demographics (2022) |
| Census Gazetteer | 3,222 | County centroids |
| HIFLD Hospitals | 7,496 | Hospital locations, bed counts |
| HIFLD Fire Stations | 52,051 | Fire station locations |
| HIFLD EMS | 7,045 | EMS station locations |
| CMS Nursing Homes | 14,713 | Medicare-certified facilities |

**Total: 157,363 records from 7 sources**

---

## FEATURES

### Core Query Tools (10)
- query_counties, get_county_detail, compare_counties
- get_statistics, predict_risk, get_state_rankings
- prioritize_by_impact, get_real_time_alerts

### Advanced Analytics (7)
- find_compound_risk_counties, get_gap_analysis
- get_disaster_trends, find_zero_redundancy
- simulate_scenario, analyze_cascade_risk
- calculate_intervention_roi

### Agent Swarm Tools (4)
- export_fhir, export_geojson
- analyze_spatial_autocorrelation
- find_spatial_hotspots

### Alert System Tools (6)
- subscribe_to_alerts, unsubscribe_from_alerts
- list_alert_subscriptions, dispatch_alert
- get_active_alerts, acknowledge_alert

### Meta Tools (2)
- generate_executive_brief, self_improve

---

## DASHBOARD TABS

1. **Overview** — Key metrics, top 20 highest-risk counties
2. **Risk Map** — Interactive Mapbox scatter map
3. **Geographic Analysis** — 5 visualization modes
4. **Infrastructure** — Facility distance distributions
5. **Scenario Sim** — What-if disaster simulation
6. **Advanced Insights** — Compound risk, acceleration, redundancy
7. **Gap Analysis** — Intervention recommendations
8. **Alert Center** — Threshold-based monitoring
9. **Benchmarking** — County peer comparison
10. **Model Performance** — ML evaluation metrics
11. **Agent Query** — Natural language interface ← **NEW**
12. **Export** — FHIR/GeoJSON download

---

## QUICK START

```bash
# 1. Clone and setup
git clone https://github.com/GDogMcCoy/ResilienceAI.git
cd ResilienceAI
pip install -r requirements.txt

# 2. Run data pipeline
python run_pipeline.py

# 3. Start Archia server (Terminal 1)
archiad --config archia/archia.toml

# 4. Launch dashboard (Terminal 2)
streamlit run app/dashboard.py

# 5. Open http://localhost:8501
# 6. Click "Agent Query" tab
# 7. Ask: "Which Missouri counties are most vulnerable?"
```

---

## FUTURE ROADMAP

### Near Term (0-6 months)
- Real-time weather API integration (NOAA)
- Mobile alert dispatch system
- Agricultural vulnerability assessment
- Time-series forecasting

### Medium Term (6-12 months)
- Multi-county regional analysis
- Advanced network visualization
- Social media sentiment integration
- Mobile app (iOS/Android)

### Long Term (12+ months)
- International expansion
- Climate change projections
- AI-powered intervention recommendations
- Real-time digital twin

---

## CONTACT INFORMATION

**Project:** ResilienceAI  
**Event:** MUIDSI Hackathon 2026  
**Repository:** github.com/GDogMcCoy/ResilienceAI  

**Documentation:**
- Setup Guide: `docs/SETUP_GUIDE.md`
- Data Dictionary: `docs/DATA_DICTIONARY.md`
- API Reference: `docs/API_REFERENCE.md`

**Demo Materials:**
- Demo Script: `demo_materials/DEMO_SCRIPT.md`
- Video Script: `demo_materials/VIDEO_SCRIPT.md`
- Slide Deck: `demo_materials/SLIDE_DECK.md`
- Judge FAQ: `demo_materials/JUDGE_FAQ.md`

---

## TAGLINE

**ResilienceAI — Built for emergency planners. Powered by agentic AI.**

---

*One-Pager Version 1.0 — MUIDSI Hackathon 2026 Submission*
