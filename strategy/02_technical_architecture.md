# ResilienceAI Technical Architecture

## Executive Summary

This document outlines the technical architecture for ResilienceAI, a disaster vulnerability assessment platform built for the Archia MCP runtime. The architecture supports 45+ MCP tools, real-time data integration, predictive modeling, and multi-modal AI interactions for emergency planners and public health officials.

**Key Architectural Decisions:**
- **MCP (Model Context Protocol) Runtime**: Archia platform for agent orchestration
- **Python-First Stack**: Streamlit for rapid UI, FastAPI for API layer
- **Modular Agent Design**: Plugin-based tool system for extensibility
- **Multi-Source Data Integration**: FEMA, Census, HIFLD, NOAA, USDA

---

## 1. Technical Stack Recommendations

### 1.1 Core Platform: Archia MCP Runtime

**Rationale**: The Archia platform provides native MCP (Model Context Protocol) support, which is essential for the agentic AI architecture of ResilienceAI.

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent Runtime** | Archia MCP Server | Orchestrates 45+ tools, handles LLM interactions |
| **LLM Provider** | Anthropic Claude 3.5 Sonnet | Natural language understanding, tool selection |
| **API Gateway** | Archia Cloud (api.archia.app) | Production hosting, rate limiting, auth |
| **Local Development** | Archia Daemon (archiad) | Local testing and development |

**Archia Configuration** (`archia/archia.toml`):
```toml
[agent]
name = "ResilienceAI"
version = "1.0.0"

[agent.model]
provider = "anthropic"
model = "claude-sonnet-4-5-20250929"
temperature = 0.3
max_tokens = 4096
```

### 1.2 Backend Stack

| Layer | Technology | Version | Justification |
|-------|------------|---------|---------------|
| **Language** | Python | 3.10+ | ML/AI ecosystem, team expertise |
| **Data Processing** | Pandas, NumPy, SciPy | Latest | Tabular data manipulation |
| **ML/AI** | scikit-learn, Prophet | Latest | Classification, forecasting |
| **Geospatial** | GeoPandas, Shapely | 0.14+ | Spatial analysis, GeoJSON |
| **HTTP Client** | Requests | 2.31+ | External API integration |
| **Serialization** | Joblib, PyYAML | Latest | Model persistence, config |

### 1.3 Frontend Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Dashboard Framework** | Streamlit | Rapid prototyping, data apps |
| **UI Components** | streamlit-antd-components | Modern UI elements |
| **Visualizations** | Plotly | Interactive charts, maps |
| **Animations** | streamlit-lottie | Loading states, polish |

**Why Streamlit over React/Vue:**
- Hackathon-proven rapid development (hours vs days)
- Native Python integration with data science stack
- Built-in caching and state management
- Single-file component architecture

### 1.4 Data Storage

| Data Type | Storage | Format |
|-----------|---------|--------|
| **Processed Features** | Local/Cloud Filesystem | CSV (county_features.csv) |
| **Raw Data** | Local Filesystem | CSV, GeoJSON |
| **Model Artifacts** | Local Filesystem | Pickle (.pkl) |
| **FHIR Exports** | Generated on-demand | JSON (FHIR R4) |
| **GeoJSON Exports** | Generated on-demand | GeoJSON |
| **Alert Subscriptions** | In-memory/SQLite | JSON/SQL |

**Note**: Current architecture uses file-based storage for simplicity. For production scale, migrate to:
- **PostgreSQL + PostGIS** for relational + spatial data
- **Redis** for alert subscription caching
- **S3/Cloud Storage** for model artifacts

---

## 2. AI/ML Architecture for Disaster Resilience

### 2.1 Model Architecture

**Risk Classification Pipeline**:

```
Raw Data → Feature Engineering → Model Ensemble → Risk Score → Risk Level
```

| Model | Purpose | Performance |
|-------|---------|-------------|
| **Logistic Regression** | Baseline, interpretability | F1=0.983 |
| **Random Forest** | Feature importance, non-linear | F1=0.978 |
| **Gradient Boosting** | Best accuracy, handles imbalance | F1=0.981 |
| **Neural Network (MLP)** | Complex patterns | F1=0.975 |

**Ensemble Strategy**: Soft voting (probability averaging) across all models

### 2.2 Feature Engineering Pipeline

**66 Engineered Features** across 7 categories:

```
┌─────────────────────────────────────────────────────────────┐
│                    FEATURE HIERARCHY                        │
├─────────────────────────────────────────────────────────────┤
│ 1. Demographics (9)      → Census ACS 2022                  │
│ 2. Infrastructure (12)   → HIFLD + CMS facilities           │
│ 3. Disaster History (7)  → FEMA declarations                │
│ 4. Composite Indices (4) → vulnerability, isolation, risk   │
│ 5. Compound Risk (2)     → multi-dimensional clustering     │
│ 6. Temporal (3)          → disaster acceleration            │
│ 7. Intervention Gaps (6) → gap analysis matrix              │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Predictive Modeling Components

| Component | Algorithm | Use Case |
|-----------|-----------|----------|
| **Time-Series Forecasting** | Prophet, ARIMA | Risk trajectory prediction |
| **Climate Projection** | IPCC SSP Scenarios | Long-term risk modeling |
| **Disaster Probability** | Gradient Boosting | Event likelihood |
| **Spatial Autocorrelation** | Moran's I, Getis-Ord Gi* | Hotspot detection |

### 2.4 Agent Tool Architecture (45 MCP Tools)

**Tool Categories**:

```
Core Query Tools (10)
├── query_counties
├── get_county_detail
├── compare_counties
├── get_statistics
├── predict_risk
├── find_compound_risk_counties
├── get_gap_analysis
├── get_disaster_trends
├── find_zero_redundancy
└── get_state_rankings

Advanced Analytics (7)
├── simulate_scenario
├── analyze_cascade_risk
├── calculate_intervention_roi
├── generate_executive_brief
├── get_equity_analysis
├── benchmark_county
└── prioritize_by_impact

Export & Integration (4)
├── export_fhir
├── export_geojson
├── analyze_spatial_autocorrelation
└── find_spatial_hotspots

Real-Time Systems (10)
├── subscribe_to_alerts
├── unsubscribe_from_alerts
├── list_alert_subscriptions
├── dispatch_alert
├── get_active_alerts
├── acknowledge_alert
├── get_weather_alerts
├── correlate_weather_with_vulnerability
├── get_high_impact_weather
└── should_trigger_weather_alert

Agricultural Analysis (4)
├── get_crop_yield
├── calculate_agricultural_vulnerability
├── assess_food_security_risk
└── get_state_crop_summary

Predictive Modeling (7)
├── forecast_risk_trajectory
├── analyze_risk_trajectory
├── project_climate_risk
├── detect_disaster_acceleration
├── predict_disaster_probability
├── batch_forecast_counties
└── get_climate_adaptation_recommendations

Meta & Utility (3)
├── get_real_time_alerts
├── self_improve
└── get_mo_health_disparities
```

---

## 3. Data Domain Integration Patterns

### 3.1 Geospatial Data Integration

**Sources**:
- **Census Gazetteer**: County centroids, boundaries
- **HIFLD (FEMA)**: Hospital, fire station, EMS locations
- **FEMA ArcGIS Hub**: Facility coordinates

**Integration Pattern**:
```python
# Spatial join using cKDTree for efficiency
from scipy.spatial import cKDTree

# Build spatial index
tree = cKDTree(county_coords_rad)

# Query nearest facilities
distances, indices = tree.query(facility_coords, k=2)
```

**Key Metrics**:
- Distance to nearest/2nd-nearest facility
- Facility density per 10k population
- Spatial autocorrelation (Moran's I)

### 3.2 Healthcare Data Integration

**Sources**:
- **CMS Medicare**: Nursing home locations, bed counts
- **HIFLD**: Hospital locations, emergency services
- **Census ACS**: Uninsured rates, disability rates

**Integration Pattern**:
```python
# FHIR R4 Export for EHR integration
from fhir.resources.bundle import Bundle
from fhir.resources.location import Location
from fhir.resources.riskassessment import RiskAssessment
```

**Key Metrics**:
- Healthcare facility accessibility
- Uninsured population percentage
- Medical resource redundancy

### 3.3 911/Emergency Data Integration

**Sources**:
- **FEMA Open API**: Disaster declarations (1953-present)
- **NOAA NWS API**: Real-time weather alerts
- **USGS**: Seismic activity (planned)

**Integration Pattern**:
```python
# Real-time weather alert correlation
class NOAAWeatherClient:
    def correlate_with_vulnerability(self, county_fips, 
                                     vulnerability_score):
        alerts = self.get_alerts_for_county(county_fips)
        enhanced_risk = vulnerability_score * alert_severity
        return enhanced_risk_assessment
```

**Key Metrics**:
- Historical disaster frequency by type
- Real-time weather alert correlation
- Disaster acceleration trends

### 3.4 Agricultural Data Integration

**Sources**:
- **USDA NASS API**: Crop yields, production data
- **Custom vulnerability models**: Food security risk

**Key Metrics**:
- Crop yield stability
- Agricultural diversity index
- Food import dependency

---

## 4. Critical Technical Decisions

### 4.1 Decision: MCP over Traditional REST API

**Context**: Need to expose 45+ analytical capabilities to LLM

**Options Considered**:
| Approach | Pros | Cons |
|----------|------|------|
| REST API | Familiar, well-documented | LLM struggles with endpoint selection |
| GraphQL | Flexible queries | Complex to implement, overkill |
| **MCP (Selected)** | Native LLM integration, tool discovery | Newer standard, learning curve |

**Decision**: Use Archia MCP runtime for native LLM tool orchestration

### 4.2 Decision: Streamlit over React/Vue

**Context**: Need rapid dashboard development for hackathon

**Options Considered**:
| Approach | Pros | Cons |
|----------|------|------|
| React + FastAPI | Production-ready, flexible | Longer development time |
| **Streamlit (Selected)** | Python-native, rapid prototyping | Less customizable UI |
| Gradio | Simple ML demos | Limited for complex dashboards |

**Decision**: Streamlit for MVP, React migration path for production

### 4.3 Decision: File-Based over Database Storage

**Context**: 3,222 counties, 66 features = ~2MB dataset

**Options Considered**:
| Approach | Pros | Cons |
|----------|------|------|
| PostgreSQL + PostGIS | Scalable, ACID | Overhead for small dataset |
| **CSV + Parquet (Selected)** | Simple, zero config | No concurrent writes |
| SQLite | Lightweight SQL | Limited geospatial support |

**Decision**: File-based for MVP, PostgreSQL migration for multi-user scale

### 4.4 Decision: Claude over GPT-4

**Context**: Need reliable tool selection and reasoning

**Options Considered**:
| Model | Pros | Cons |
|-------|------|------|
| GPT-4o | Fast, cost-effective | Less reliable tool calling |
| **Claude 3.5 Sonnet (Selected)** | Excellent reasoning, tool use | Slightly higher latency |
| Llama 3 (local) | Privacy, no API costs | Requires GPU, less capable |

**Decision**: Claude 3.5 Sonnet for production, local fallback option

### 4.5 Decision: Prophet + ARIMA over Deep Learning

**Context**: Time-series forecasting for 3,222 counties with limited historical data

**Options Considered**:
| Approach | Pros | Cons |
|----------|------|------|
| LSTM/Transformer | State-of-art accuracy | Requires large training data |
| **Prophet + ARIMA (Selected)** | Interpretable, works with small data | Less accurate for complex patterns |
| XGBoost | Fast, feature importance | No native time-series support |

**Decision**: Classical methods for interpretability, DL upgrade path for v2

---

## 5. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│  Streamlit Dashboard        Web/Mobile         External Systems     │
│  ├─ Agent Query Tab         (Future)           ├─ EHR (FHIR)        │
│  ├─ Risk Maps               ├─ React App       ├─ GIS Workflows     │
│  ├─ Predictive Analytics    └─ PWA             └─ FEMA Systems      │
│  └─ Real-Time Alerts                                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ARCHIA MCP RUNTIME                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Agent      │  │   Tool       │  │   LLM        │              │
│  │   Router     │──│   Registry   │──│   Interface  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│         │                 │                 │                       │
│         ▼                 ▼                 ▼                       │
│  ┌─────────────────────────────────────────────────────┐           │
│  │              45+ MCP Tools                          │           │
│  │  ├─ Core Query      ├─ Real-Time Alerts            │           │
│  │  ├─ Analytics       ├─ Weather Integration         │           │
│  │  ├─ Predictive      ├─ Agriculture                 │           │
│  │  └─ Export          └─ Meta Tools                  │           │
│  └─────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI ENGINE                              │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Resilience  │  │  Predictive  │  │   Spatial    │              │
│  │  Agent       │  │  Models      │  │   Stats      │              │
│  │  (agent.py)  │  │  (prophet)   │  │  (morans_i)  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Weather    │  │    Alert     │  │    FHIR      │              │
│  │   Client     │  │   Manager    │  │   Export     │              │
│  │  (NOAA)      │  │              │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Processed  │  │     Raw      │  │    Models    │              │
│  │   Features   │  │    Data      │  │   (pickle)   │              │
│  │   (CSV)      │  │   (CSV)      │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   EXTERNAL DATA SOURCES                             │
├─────────────────────────────────────────────────────────────────────┤
│  FEMA        Census       NOAA        HIFLD        USDA            │
│  ├─ Disasters ├─ ACS      ├─ Weather  ├─ Hospitals  ├─ Crop Yields │
│  └─ Declar.  └─ Demog.   └─ Alerts   ├─ Fire/EMS   └─ NASS        │
│                                       └─ Nursing Homes              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Completed)
- [x] Core data pipeline (FEMA, Census, HIFLD)
- [x] Feature engineering (66 features)
- [x] Risk classification models
- [x] Basic MCP tools (10)
- [x] Streamlit dashboard

### Phase 2: Advanced Analytics (Completed)
- [x] Scenario simulation
- [x] Network cascade analysis
- [x] Intervention ROI calculator
- [x] FHIR/GeoJSON export
- [x] Spatial statistics

### Phase 3: Real-Time Systems (Completed)
- [x] Alert subscription system
- [x] NOAA weather integration
- [x] Weather-vulnerability correlation
- [x] Alert dispatch system

### Phase 4: Predictive Modeling (Completed)
- [x] Prophet/ARIMA forecasting
- [x] Climate scenario modeling (IPCC SSPs)
- [x] Disaster probability prediction
- [x] Batch forecasting

### Phase 5: Production Hardening (Next)
- [ ] PostgreSQL + PostGIS migration
- [ ] Redis caching layer
- [ ] Kubernetes deployment
- [ ] Monitoring (Prometheus/Grafana)
- [ ] API rate limiting
- [ ] Authentication/Authorization

### Phase 6: Scale & Extend (Future)
- [ ] Real-time streaming (Kafka/Kinesis)
- [ ] Deep learning forecasting (LSTM)
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] International expansion

---

## 7. Deployment Architecture

### 7.1 Local Development

```bash
# Start Archia daemon
archiad --config archia/archia.toml

# Start Streamlit dashboard
streamlit run app/dashboard.py
```

### 7.2 Production Deployment (Archia Cloud)

```bash
# Deploy to Archia Cloud
./deploy-to-archia.sh

# Configuration
export ARCHIA_API_KEY="ask_wbkaHYsVv6yiaBMBko3VU_YZ9Bonga3nThObPyKJwwA="
curl -X POST https://api.archia.app/v1/agents/deploy \
  -H "Authorization: Bearer $ARCHIA_API_KEY" \
  -d @archia/archia.toml
```

### 7.3 Kubernetes Deployment

```yaml
# archia/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resilienceai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: resilienceai
  template:
    spec:
      containers:
      - name: agent
        image: resilienceai:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

---

## 8. Security Considerations

| Layer | Measures |
|-------|----------|
| **API** | API key authentication, rate limiting (100 req/min) |
| **Data** | No PII stored, aggregated county-level only |
| **Transport** | HTTPS only for external APIs |
| **Model** | Input validation on all tool parameters |
| **Export** | FHIR bundles conform to HIPAA Safe Harbor |

---

## 9. Performance Benchmarks

| Metric | Target | Current |
|--------|--------|---------|
| Query Response | <2s | ~500ms |
| Model Inference | <100ms | ~50ms |
| Dashboard Load | <3s | ~2s |
| Forecast Generation | <5s | ~3s |
| Concurrent Users | 100 | 10 (local) |

---

## 10. Conclusion

The ResilienceAI architecture prioritizes:

1. **Rapid Development**: Python + Streamlit + MCP for fast iteration
2. **AI-Native Design**: MCP tools designed for LLM consumption
3. **Modularity**: Plugin-based tool system for easy extension
4. **Data Integration**: Multi-source fusion (geospatial, health, 911, agriculture)
5. **Production Path**: Clear migration path from file-based to database storage

**Critical Success Factors**:
- Maintain MCP tool quality (descriptions, parameters, error handling)
- Monitor LLM tool selection accuracy
- Plan PostgreSQL migration before 10k+ user scale
- Implement caching for external API calls (NOAA, USDA)

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: Technical Architecture Specialist - ResilienceAI Council*
