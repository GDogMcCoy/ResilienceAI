# ResilienceAI - Presentation Deck
## Disaster Vulnerability & Health Infrastructure Gap Assessment Agent
### MUIDSI Hackathon 2026

---

## Slide 1: The Problem

**When disasters strike, damage is not distributed equally.**

- Communities with limited healthcare, aging populations, and high poverty bear disproportionate burden
- Emergency planners lack accessible, data-driven tools to identify **which specific communities** face the greatest compound risk **before** disaster hits
- No existing tool integrates infrastructure access + demographic vulnerability + disaster history into a single queryable platform

---

## Slide 2: Our Solution - ResilienceAI

An **agentic AI platform** that fuses 7 federal data sources into a unified machine learning pipeline:

1. **66 engineered features** including 29 advanced differentiator analytics
2. **4 ML models** trained and evaluated (best F1 = 0.983)
3. **19 MCP-compatible tools** for natural language queries
4. **11-tab interactive dashboard** with 3D visualization, scenario simulation, and real-time alerts

**Live Demo:** https://resiliencea-he3ymacsegj4rb6bldxq4t.streamlit.app/

---

## Slide 3: Data - 100% Real Federal Sources

| Source | Records | Agency |
|--------|---------|--------|
| Hospitals | 7,496 | FEMA/HIFLD |
| Fire Stations | 52,051 | FEMA/HIFLD |
| EMS Stations | 7,045 | FEMA/HIFLD |
| Nursing Homes | 14,713 | CMS Medicare |
| Disaster Declarations | 69,615 | FEMA OpenData |
| Census Demographics | 3,222 | US Census ACS |
| County Centroids | 3,222 | Census Gazetteer |

**Total: 157,363 records | 3,222 US counties | Zero synthetic data**

---

## Slide 4: Feature Engineering & Model Results

### 66 Features Across 12 Categories
- Spatial infrastructure access (KD-tree distances)
- Infrastructure density & redundancy
- Disaster history & temporal acceleration
- Demographic vulnerability composites
- Compound risk clusters, gap analysis, risk contagion

### Model Performance

| Model | F1 (macro) | CV F1 |
|-------|-----------|-------|
| **Logistic Regression** | **0.983** | **0.979** |
| Gradient Boosting | 0.971 | 0.967 |
| Neural Network | 0.949 | 0.950 |
| Random Forest | 0.944 | 0.933 |

---

## Slide 5: Agentic AI - 19 MCP Tools

Natural language queries for emergency planners:

- *"Which Missouri counties are most vulnerable to flooding?"*
- *"Where are disasters accelerating fastest?"*
- *"Which counties have zero hospital redundancy?"*
- *"Simulate a Category 5 hurricane hitting Miami-Dade"*
- *"What's the ROI of building a hospital in rural Kansas?"*
- *"Generate an executive briefing for Jackson County"*

**Advanced capabilities:** Scenario simulation, cascade risk analysis, intervention ROI, equity analysis, peer benchmarking, real-time alerts, self-improvement loop

---

## Slide 6: Interactive Dashboard - 11 Tabs

1. **Overview** - Key metrics & risk distribution
2. **Risk Map** - Interactive Mapbox scatter
3. **Geographic Analysis** - 5 viz modes incl. 3D risk landscape
4. **Infrastructure** - Facility distance analysis & gaps
5. **Scenario Sim** - What-if disaster modeling (10 preset types)
6. **Advanced Insights** - Compound risk, acceleration, redundancy, contagion
7. **Gap Analysis** - Intervention recommendations by county
8. **Alert Center** - Threshold-based monitoring
9. **Benchmarking** - Peer comparison with radar charts
10. **Model Performance** - Full evaluation suite
11. **Agent Query** - Natural language interface

---

## Slide 7: Impact & Social Good

- **Actionable for emergency planners**: Identifies specific counties needing specific interventions
- **Equity-focused**: Surfaces disparities in disaster vulnerability by demographics
- **Proactive, not reactive**: Compound risk detection before disaster strikes
- **177 counties** flagged with 3+ simultaneous risk dimensions
- **74 counties** with zero hospital redundancy (single point of failure)
- **1,305 counties** with accelerating disaster frequency

**Built on 100% real federal open data. Fully reproducible with one command.**

---

## Technical Stack

Python | pandas | scikit-learn | XGBoost | Plotly | Folium | Streamlit | NetworkX | ReportLab | python-pptx

**Deployed on Streamlit Cloud | Agent config ready for Archia Cloud import**
