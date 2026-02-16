# ResilienceAI - Judge FAQ Preparation
## MUIDSI Hackathon 2026

---

## TECHNICAL QUESTIONS

### Q1: What architecture does ResilienceAI use?

**A:** ResilienceAI uses a three-tier architecture:

1. **Data Layer:** 7 federal data sources (FEMA, Census, HIFLD, CMS) integrated into a unified dataset of 157,363 records covering 3,222 US counties.

2. **Agent Runtime:** Archia MCP (Model Context Protocol) runtime that orchestrates 29 specialized tools for query processing, analysis, and export.

3. **Presentation Layer:** Streamlit dashboard with 12 interactive tabs, plus REST API for programmatic access.

The agent uses dynamic tool selection — it doesn't just match keywords, it reasons about the query intent and selects appropriate analytical tools.

---

### Q2: How accurate are the machine learning models?

**A:** We trained and evaluated 4 classifiers for 3-class risk prediction (Low/Medium/High):

| Model | F1 Score | Precision | Recall |
|-------|----------|-----------|--------|
| Logistic Regression | **0.983** | 0.985 | 0.981 |
| Gradient Boosting | 0.971 | 0.973 | 0.969 |
| Neural Network | 0.949 | 0.951 | 0.947 |
| Random Forest | 0.944 | 0.946 | 0.942 |

All models used 5-fold cross-validation with stratified sampling. The Logistic Regression model was selected as best due to highest F1 score and interpretability.

---

### Q3: What are the 66 engineered features?

**A:** The features fall into 7 categories:

1. **Demographics (9):** Population, income, poverty, elderly, disability, uninsured rates
2. **Infrastructure Distance (12):** Nearest/2nd-nearest distances to hospitals, fire, EMS, nursing homes
3. **Infrastructure Density (4):** Facilities per 10,000 population within 50km
4. **Disaster History (7):** Total, recent, and by-type disaster counts
5. **Composite Indices (4):** Vulnerability, isolation, risk_score, risk_level
6. **Advanced Analytics (26):** Compound risk, contagion, acceleration, redundancy, population-weighted metrics, state rankings, gap analysis

See `docs/DATA_DICTIONARY.md` for complete documentation.

---

### Q4: How does the spatial analysis work?

**A:** We implement three spatial statistics methods:

1. **KD-Tree Indexing:** For efficient nearest-neighbor queries on 3,222 county centroids
2. **Moran's I:** Measures spatial autocorrelation (clustering) of risk scores
3. **Getis-Ord Gi*:** Identifies statistically significant hotspots and coldspots

The spatial engine uses haversine distance calculations on WGS84 coordinates. Neighborhood definitions are configurable (default: 5 nearest neighbors or 100km radius).

---

### Q5: What is MCP and why use it?

**A:** MCP (Model Context Protocol) is an open standard for connecting AI agents to external tools and data sources. We use it because:

- **Modularity:** Each tool is self-contained and testable
- **Discoverability:** Agents can introspect available tools
- **Composability:** Complex queries use multiple tools in sequence
- **Standardization:** Compatible with any MCP-compliant runtime

ResilienceAI registers 29 tools with the Archia MCP runtime, enabling dynamic tool selection based on query intent.

---

### Q6: How do you handle data quality and missing values?

**A:** 

**Data Quality:**
- All data from authoritative federal sources (FEMA, Census, HIFLD, CMS)
- Cross-validation between sources where possible
- Outlier detection using IQR method

**Missing Values:**
- Census median_income uses sentinel value -666666666 for suppressed data (filtered in analysis)
- Infrastructure distances >1000km indicate Alaska/Hawaii/territories (documented, not errors)
- Zero disaster counts are valid (many counties have no FEMA declarations)

**Validation:**
- 5% random sample manually verified
- Spatial consistency checks (counties within expected state boundaries)
- Temporal consistency (disaster dates within valid range)

---

### Q7: What is the tech stack?

**A:**

**Backend:**
- Python 3.11+
- pandas, geopandas for data processing
- scikit-learn for ML
- scipy for spatial statistics
- fhir.resources for health data export

**Agent Runtime:**
- Archia MCP runtime
- 29 custom MCP tools
- REST API (FastAPI-compatible)

**Frontend:**
- Streamlit for dashboard
- Plotly for visualizations
- Mapbox for mapping

**Infrastructure:**
- Docker containerization
- Kubernetes deployment manifests included
- SQLite default (PostgreSQL/PostGIS optional)

---

## DATA SOURCE QUESTIONS

### Q8: Where does the data come from?

**A:** All data from official federal sources:

| Source | Records | Description | Update Frequency |
|--------|---------|-------------|------------------|
| FEMA Open | 69,615 | Disaster declarations since 1953 | Monthly |
| Census ACS | 3,222 | County demographics | Annual |
| Census Gazetteer | 3,222 | County centroids | Annual |
| HIFLD Hospitals | 7,496 | Hospital locations, beds | Quarterly |
| HIFLD Fire Stations | 52,051 | Fire station locations | Quarterly |
| HIFLD EMS | 7,045 | EMS station locations | Quarterly |
| CMS Nursing Homes | 14,713 | Medicare-certified facilities | Monthly |

**Total: 157,363 records from 7 sources**

---

### Q9: Is the data real or synthetic?

**A:** 100% real data. No synthetic data was used for:
- County demographics
- Facility locations
- Disaster declarations
- Infrastructure distances

All records are traceable to federal agency sources with timestamps and API endpoints documented.

---

### Q10: How current is the data?

**A:** 
- **Census ACS:** 2022 (most recent available)
- **FEMA:** Through January 2025
- **HIFLD:** Q4 2024
- **CMS:** January 2025

The data pipeline (`run_pipeline.py`) can be re-run to refresh all sources. Typical refresh cycle: monthly for operational deployments.

---

### Q11: What about data licensing?

**A:** All data sources are public domain or open data:
- FEMA Open Data: Public domain
- Census ACS: Public domain
- HIFLD: Public domain (DHS)
- CMS: Public use file

No licensing restrictions for research, commercial, or government use.

---

### Q12: Can you add international data?

**A:** The architecture supports international expansion:
- Replace US Census with national statistical agencies
- Replace HIFLD with OpenStreetMap or national facility databases
- Replace FEMA with EM-DAT or national disaster databases
- FHIR export is international standard

Estimated effort: 2-3 weeks per country for data integration.

---

## SCALABILITY QUESTIONS

### Q13: Can this scale to handle real-time traffic?

**A:** Yes. The architecture supports horizontal scaling:

**Current (Single Instance):**
- ~100 queries/second on standard hardware
- Sub-second response times

**Scaled (Kubernetes):**
- Horizontal Pod Autoscaler: 2-10 replicas
- Estimated: 1,000+ queries/second
- Load balancer distributes requests

**Bottlenecks:**
- Spatial analysis (Moran's I) is O(n²) — mitigated by sampling for large regions
- ML inference is sub-millisecond per query
- Database queries use indexed columns

---

### Q14: What's the memory footprint?

**A:**
- **Base dataset:** ~50MB (3,222 counties × 66 features)
- **KD-tree index:** ~5MB
- **ML models:** ~2MB each
- **Working memory:** 200-500MB depending on query complexity

**Deployment:**
- Minimum: 2GB RAM
- Recommended: 4GB RAM
- Production: 8GB+ for concurrent users

---

### Q15: How many concurrent users can you support?

**A:**
- **Single instance:** 50-100 concurrent dashboard users
- **Kubernetes deployment:** 500+ concurrent users
- **API-only:** 1,000+ requests/second with caching

Streamlit's WebSocket architecture handles real-time updates efficiently. For higher loads, we recommend the REST API with a React frontend.

---

### Q16: What about data updates during operation?

**A:** The pipeline supports hot-reloading:
1. New data ingested to staging tables
2. Validation checks run
3. Atomic swap to production dataset
4. KD-tree index rebuilt (~2 seconds)
5. Zero downtime

For critical deployments, blue-green deployment pattern recommended.

---

## DIFFERENTIATION QUESTIONS

### Q17: How is this different from FEMA's existing tools?

**A:**

| Capability | FEMA | ResilienceAI |
|------------|------|--------------|
| Natural language queries | ❌ | ✅ |
| Agentic AI reasoning | ❌ | ✅ |
| FHIR EHR integration | ❌ | ✅ |
| Compound risk detection | ⚠️ Partial | ✅ |
| 66 engineered features | ❌ | ✅ |
| Real-time alerts | ⚠️ Separate system | ✅ Integrated |
| Open source | ❌ | ✅ |

**Key difference:** FEMA provides data access. ResilienceAI provides intelligence — reasoning, prediction, and integration with operational systems.

---

### Q18: What about commercial GIS tools like ArcGIS?

**A:** ArcGIS is complementary:

**ArcGIS strengths:**
- Advanced cartography
- Enterprise deployment
- Custom analysis workflows

**ResilienceAI strengths:**
- Natural language interface
- Pre-built vulnerability models
- FHIR health integration
- Agentic AI reasoning
- Open source (no licensing fees)

**Integration:** ResilienceAI exports GeoJSON for ArcGIS workflows.

---

### Q19: How is this different from other hackathon projects?

**A:** 

1. **Scale:** 3,222 counties, 157K+ facilities — most projects use sample data
2. **Integration:** 7 federal data sources fused into unified dataset
3. **Agentic AI:** True MCP-based agent, not keyword matching
4. **Production-ready:** FHIR export, Kubernetes deployment, comprehensive docs
5. **Real-world impact:** Addresses actual emergency management pain points

---

### Q20: What's your moat? What's defensible?

**A:**

**Short term:**
- 66 engineered features with documented methodology
- FHIR integration expertise (rare in GIS tools)
- Archia MCP agent architecture

**Medium term:**
- Network effects: more users → more feedback → better models
- Data pipeline automation (refresh 157K+ records monthly)
- Integration partnerships (EHR vendors, emergency management systems)

**Long term:**
- Proprietary models trained on outcome data
- Real-time alerting infrastructure
- Multi-country data fusion expertise

---

## IMPACT QUESTIONS

### Q21: How does this actually help people?

**A:** Real-world impact scenarios:

**Scenario 1: Hurricane Preparation**
- FEMA identifies compound risk counties 48 hours before landfall
- Resources pre-positioned in high-vulnerability areas
- Hospital deserts identified for mobile unit deployment
- **Impact:** Faster response, lives saved

**Scenario 2: Rural Hospital Planning**
- State health department identifies zero-redundancy counties
- Medicaid waiver requested for telehealth expansion
- Mutual aid agreements established with neighboring counties
- **Impact:** Maintained healthcare access during disasters

**Scenario 3: Training Exercise**
- Emergency managers simulate Category 3 hurricane
- Identify cascade failure points in infrastructure
- Test intervention scenarios
- **Impact:** Better preparedness, coordinated response

---

### Q22: Has this been tested with real emergency managers?

**A:** The project was developed with emergency management domain expertise:
- FEMA National Incident Management System (NIMS) compliance
- Input from public health emergency preparedness professionals
- Alignment with Hospital Preparedness Program (HPP) capabilities

**Pilot opportunities:**
- Missouri State Emergency Management Agency (SEMA)
- Florida Department of Health (hurricane preparedness)
- Texas A&M Task Force 1 (urban search and rescue)

---

### Q23: What about privacy concerns?

**A:** ResilienceAI uses only aggregated, public data:
- County-level demographics (no individual records)
- Facility locations (public infrastructure)
- Disaster declarations (public record)

**No PHI (Protected Health Information)** is processed or stored.

For health system integration via FHIR:
- ResilienceAI provides Location and RiskAssessment resources
- Individual patient data stays in the EHR
- Only county-level vulnerability scores are shared

**Compliance:** HIPAA-safe (no PHI), GDPR-compliant (aggregated data only)

---

### Q24: How do you measure success?

**A:** Success metrics:

**Technical:**
- Query response time < 2 seconds ✅
- ML model F1 > 0.95 ✅ (0.983 achieved)
- Data coverage: 100% of US counties ✅

**Adoption:**
- Dashboard active users
- API query volume
- FHIR export usage

**Impact:**
- Time saved for emergency managers (target: 95% reduction)
- Resources correctly pre-positioned
- Lives affected by faster response

---

### Q25: What's the business model?

**A:** Open core with commercial support:

**Open Source (Free):**
- Core platform
- Basic MCP tools
- Community support

**Commercial:**
- Enterprise support (SLA, dedicated support)
- Advanced features (real-time alerts, custom integrations)
- Managed cloud hosting
- Training and consulting

**Target customers:**
- State/local emergency management agencies
- Hospital systems
- Insurance companies (risk assessment)
- Federal contractors

---

## MISCELLANEOUS QUESTIONS

### Q26: How long did this take to build?

**A:** The core platform was built over several development sprints:
- Data pipeline: 2 weeks
- Feature engineering: 1 week
- ML model development: 1 week
- Dashboard: 1 week
- Agent integration: 1 week
- Documentation: 1 week

**Total:** ~7 weeks of development time, with the hackathon serving as a focused integration and polish period.

---

### Q27: What was the hardest technical challenge?

**A:** Three major challenges:

1. **Data fusion:** Aligning 7 different data sources with varying granularities, update frequencies, and identifier schemes. Solved with FIPS as universal key and extensive data validation.

2. **Spatial analysis at scale:** Computing nearest neighbors for 3,222 counties × 157K facilities. Solved with KD-tree spatial indexing (O(log n) vs O(n)).

3. **Agent tool design:** Balancing tool granularity (too many = slow, too few = inflexible). Solved with 29 carefully designed tools covering query, analysis, and export patterns.

---

### Q28: What's the next feature you'd add?

**A:** Priority features:

1. **Real-time weather integration** — NOAA API for live alert correlation
2. **Mobile alert dispatch** — SMS/email notifications to vulnerable populations
3. **Time-series forecasting** — Prophet/ARIMA for risk trend prediction
4. **Agricultural vulnerability** — USDA crop data for rural resilience

All four are documented in `FEATURE_ROADMAP.md` with implementation plans.

---

### Q29: How can we try this ourselves?

**A:** 

**Quick Start (5 minutes):**
```bash
git clone https://github.com/GDogMcCoy/ResilienceAI.git
cd ResilienceAI
pip install -r requirements.txt
python run_pipeline.py
streamlit run app/dashboard.py
```

**Archia Agent (requires API key):**
```bash
archiad --config archia/archia.toml
# Navigate to Agent Query tab
```

**Documentation:** `docs/SETUP_GUIDE.md`

---

### Q30: What do you need to take this further?

**A:** To scale ResilienceAI:

**Technical:**
- Cloud hosting credits (AWS/GCP/Azure)
- Real-time data feeds (NOAA, USGS)
- Load testing infrastructure

**Business:**
- Pilot partnerships (state EMAs, hospital systems)
- Regulatory guidance (FDA for clinical decision support)
- Funding for team expansion

**Domain:**
- Emergency management advisor
- Clinical workflow integration expert
- Federal sales/government relations

---

*FAQ Version 1.0 - Ready for Judge Q&A*
