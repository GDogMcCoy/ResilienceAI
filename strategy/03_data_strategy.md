# ResilienceAI Data Strategy

## Executive Summary

This document outlines the comprehensive data strategy for the ResilienceAI platform, prioritizing data sources for the MUIDSI hackathon, integration approaches, preprocessing pipelines, and risk mitigation strategies. The strategy balances immediate hackathon deliverables with long-term scalability.

**Key Priorities:**
1. **Tier 1 (Critical)**: FEMA, Census ACS, HIFLD infrastructure - Already integrated, forms core foundation
2. **Tier 2 (High Value)**: NOAA/NWS weather, USGS geospatial, NEMSIS EMS - Real-time operational capabilities
3. **Tier 3 (Strategic)**: TAME-PAIN, ADNI, TCGA - Healthcare AI differentiation

---

## 1. Data Source Prioritization Matrix

### 1.1 Tier 1: Core Foundation (Implemented)

| Source | Data Type | Records | Update Frequency | Priority | Use Case |
|--------|-----------|---------|------------------|----------|----------|
| **FEMA Open** | Disaster declarations | 69,615 | Daily | CRITICAL | Historical disaster patterns, risk scoring |
| **Census ACS** | Demographics | 3,222 counties | Annual | CRITICAL | Vulnerability indices (poverty, elderly, disability) |
| **HIFLD** | Infrastructure locations | 81,305 facilities | Quarterly | CRITICAL | Distance calculations, access metrics |
| **CMS Medicare** | Nursing homes | 14,713 | Monthly | CRITICAL | Healthcare facility access |

**Status:** ✅ Fully integrated into `county_features.csv` (66 features)

### 1.2 Tier 2: Operational Intelligence (Hackathon Priority)

| Source | Data Type | API Status | Priority | Use Case |
|--------|-----------|------------|----------|----------|
| **NOAA NWS** | Weather alerts/forecasts | Free REST API | HIGH | Real-time threat correlation |
| **USGS** | Earthquakes, water data | Free REST API | HIGH | Natural hazard monitoring |
| **NEMSIS** | EMS/911 incidents | 2024 Public Dataset | HIGH | Emergency response analytics |
| **CDC WONDER** | Health statistics | Web interface | MEDIUM | Disease vulnerability |
| **USDA NASS** | Agricultural data | Free API | MEDIUM | Rural resilience metrics |

### 1.3 Tier 3: Healthcare AI Differentiation (Post-Hackathon)

| Source | Data Type | Access | Priority | Use Case |
|--------|-----------|--------|----------|----------|
| **TAME-PAIN** | Audio pain assessment | PhysioNet (credentialed) | MEDIUM | Pain assessment AI |
| **ADNI** | Alzheimer's imaging | Research application | MEDIUM | Cognitive vulnerability |
| **TCGA** | Cancer genomics | Open access | LOW | Health vulnerability modeling |
| **NACC** | Alzheimer's clinical | Research access | LOW | Longitudinal health decline |

---

## 2. Data Integration Architecture

### 2.1 Integration Patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESILIENCEAI DATA ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   FEMA API   │  │  Census API  │  │   HIFLD      │  │   NOAA NWS   │     │
│  │  (REST)      │  │  (REST)      │  │  (ArcGIS)    │  │  (REST)      │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │             │
│         └─────────────────┴─────────────────┴─────────────────┘             │
│                                    │                                        │
│                         ┌──────────▼──────────┐                            │
│                         │   ETL Pipeline      │                            │
│                         │  (src/data_loader)  │                            │
│                         └──────────┬──────────┘                            │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         │                          │                          │            │
│  ┌──────▼──────┐          ┌────────▼────────┐       ┌────────▼──────┐     │
│  │  Raw Data   │          │  Feature Eng.   │       │  Real-Time    │     │
│  │  (CSV/JSON) │          │  (66 features)  │       │  Cache        │     │
│  └──────┬──────┘          └────────┬────────┘       └────────┬──────┘     │
│         │                          │                          │            │
│         └──────────────────────────┼──────────────────────────┘            │
│                                    │                                        │
│                         ┌──────────▼──────────┐                            │
│                         │  county_features.csv │                            │
│                         │  (3,222 x 66)        │                            │
│                         └──────────┬──────────┘                            │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         │                          │                          │            │
│  ┌──────▼──────┐          ┌────────▼────────┐       ┌────────▼──────┐     │
│  │  MCP Tools  │          │  ML Models      │       │  Dashboard    │     │
│  │  (45 tools) │          │  (Prophet, etc) │       │  (Streamlit)  │     │
│  └─────────────┘          └─────────────────┘       └───────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Source-Specific Integration Plans

#### 2.2.1 NEMSIS (911/EMS Data)

**Dataset:** 2024 Public-Release Research Dataset

**Integration Approach:**
```python
# Data Structure
{
    "incident_id": "uuid",
    "timestamp": "ISO8601",
    "location": {"lat": float, "lon": float, "fips": string},
    "chief_complaint": "string",
    "vital_signs": {"pulse": int, "bp": string, "spo2": int},
    "patient_disposition": "string",
    "response_time_minutes": float,
    "scene_time_minutes": float,
    "transport_time_minutes": float
}
```

**Feature Engineering:**
- Average response times by county
- Call volume patterns (temporal)
- Chief complaint categorization (NLP)
- Outcome prediction features

**MCP Tools to Add:**
- `get_ems_response_metrics(fips)` - County-level EMS performance
- `predict_ems_demand(fips, time_horizon)` - Demand forecasting
- `analyze_emergency_patterns(fips)` - Pattern detection

**Risk Mitigation:**
- NEMSIS requires data use agreement
- PHI considerations (use public dataset only)
- Latency: Batch load, not real-time

#### 2.2.2 USGS Geospatial Data

**APIs:**
- Earthquake Catalog API (real-time)
- National Water Information System
- 3D Elevation Program

**Integration Approach:**
```python
# Real-time earthquake feed
GET https://earthquake.usgs.gov/fdsnws/event/1/query
    ?format=geojson
    &starttime={date}
    &minmagnitude=2.5
    &latitude={lat}&longitude={lon}&maxradiuskm=100
```

**Feature Engineering:**
- Seismic risk score by county
- Distance to nearest fault line
- Historical earthquake frequency
- Ground motion amplification factors

**MCP Tools to Add:**
- `get_seismic_risk(fips)` - Earthquake vulnerability
- `get_recent_earthquakes(fips, radius_km)` - Real-time feed
- `get_elevation_profile(fips)` - Flood risk correlation

#### 2.2.3 NOAA/NWS Weather Integration

**APIs:**
- Active Alerts API (real-time)
- Forecast API
- Historical Weather Data

**Integration Approach:**
```python
# Active alerts
GET https://api.weather.gov/alerts/active?area={state_code}

# County-specific forecast
GET https://api.weather.gov/points/{lat},{lon}
```

**Feature Engineering:**
- Active weather alert correlation
- Severe weather frequency by county
- Climate zone classification
- Temperature extremes (heat/cold vulnerability)

**MCP Tools to Add:**
- `get_active_weather_alerts(fips)` - Real-time alerts
- `correlate_weather_with_vulnerability(alert_id)` - Risk cross-reference
- `get_weather_forecast(fips, days=7)` - Planning support

#### 2.2.4 TAME-PAIN (Healthcare AI)

**Dataset:** PhysioNet credentialed access

**Integration Approach:**
- Audio feature extraction (MFCC, spectrograms)
- Pain level classification model
- Integration with elderly vulnerability index

**Feature Engineering:**
- Audio embeddings from pre-trained models
- Pain severity prediction
- Demographic correlation analysis

**MCP Tools to Add:**
- `analyze_pain_from_audio(audio_file)` - Pain assessment
- `correlate_pain_with_vulnerability(fips)` - Population analysis

**Risk Mitigation:**
- Requires PhysioNet credentialing (2-3 days)
- Audio data storage compliance
- Limited to non-commercial research

---

## 3. Data Preprocessing & Feature Engineering

### 3.1 Current Feature Pipeline (66 Features)

```
Raw Data → Cleaning → Feature Engineering → Normalization → Output
    │          │              │                  │            │
    ▼          ▼              ▼                  ▼            ▼
Hospitals  Missing    Distance calc       Min-max       county_
Census     value      Density calc        scaling       features
FEMA       handling   Composite           State         .csv
           Outlier    indices             percentiles
           removal    Gap analysis
```

### 3.2 Preprocessing Standards

| Step | Method | Parameters | Rationale |
|------|--------|------------|-----------|
| **Missing Values** | Median imputation | By feature type | Robust to outliers |
| **Outliers** | IQR method | 1.5 × IQR | Preserve extreme but remove errors |
| **Normalization** | Min-max scaling | 0-1 range | Interpretable risk scores |
| **Categorical** | One-hot encoding | - | ML model compatibility |
| **Temporal** | Year extraction | ISO8601 parse | Time-series analysis |

### 3.3 Feature Engineering Categories

#### 3.3.1 Infrastructure Features (Current)
```python
# Distance calculations (Haversine formula)
dist_nearest_hospital = min(haversine(county_center, facility) 
                            for facility in hospitals)

# Density metrics
density_hospitals = count_hospitals_50km / population_50km * 10000

# Redundancy scoring
redundancy_score = mean(1 / (1 + dist_2nd_nearest))
```

#### 3.3.2 Composite Risk Indices
```python
# Vulnerability Index (demographics)
vulnerability_index = weighted_mean([
    elderly_pct,
    poverty_pct, 
    disability_pct,
    uninsured_pct
], weights=[0.3, 0.3, 0.25, 0.15])

# Isolation Index (infrastructure)
isolation_index = mean(normalized_distances)

# Risk Score (composite)
risk_score = 0.4 * vulnerability + 0.3 * isolation + 0.3 * disaster_exposure
```

#### 3.3.3 Advanced Features (Implemented)
- **Compound Risk Flag**: Counties high on 3+ dimensions simultaneously
- **Risk Contagion Delta**: Neighbor risk vs. own risk
- **Disaster Acceleration**: Recent vs. prior decade frequency
- **Population-Weighted Risk**: Total impact prioritization
- **Gap Analysis**: Top intervention recommendation per county

### 3.4 New Feature Engineering (Planned)

#### Weather Correlation Features
```python
# Severe weather frequency
severe_weather_score = count_severe_alerts_last_5_years / 5

# Climate vulnerability
heat_vulnerability = elderly_pct * avg_summer_temp_anomaly
cold_vulnerability = poverty_pct * avg_winter_severity
```

#### EMS Integration Features
```python
# Response capacity
ems_capacity_score = count_ems_stations / population * 100000

# Historical performance
avg_response_time = mean(response_times_last_year)
response_reliability = std(response_times_last_year)
```

#### Geospatial Enhancement
```python
# Terrain risk
flood_risk = elevation_percentile * watershed_density
seismic_risk = proximity_to_fault * soil_liquefaction_index

# Network redundancy
network_centrality = graph_betweenness_centrality(county_node)
```

---

## 4. Data Quality & Availability Risks

### 4.1 Risk Assessment Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Census data suppression** | High | Medium | Use 5-year ACS estimates; impute suppressed values |
| **FEMA API rate limits** | Medium | High | Implement caching; batch requests |
| **NOAA API downtime** | Medium | Medium | Fallback to cached forecasts; degrade gracefully |
| **NEMSIS data lag** | High | Low | Use annual aggregates; note staleness |
| **TAME-PAIN access delay** | Medium | Medium | Mock audio pipeline; note credentialing requirement |
| **County boundary changes** | Low | High | Use vintage FIPS; validate annually |
| **Infrastructure data staleness** | High | Medium | Add data freshness indicators |

### 4.2 Data Quality Metrics

| Metric | Target | Monitoring |
|--------|--------|------------|
| **Completeness** | >95% | Per-feature null percentage |
| **Accuracy** | >98% | Cross-validation with ground truth |
| **Timeliness** | <30 days | Data freshness indicators |
| **Consistency** | 100% | Schema validation on load |
| **Uniqueness** | 100% | Duplicate detection |

### 4.3 Mitigation Strategies

#### 4.3.1 Handling Missing Data
```python
# Tiered imputation strategy
if feature_type == "demographic":
    # Use state median for small counties
    imputed_value = state_median
elif feature_type == "distance":
    # Use maximum observed (conservative)
    imputed_value = max_observed_distance
elif feature_type == "count":
    # Assume zero if not present
    imputed_value = 0
```

#### 4.3.2 API Resilience
```python
# Circuit breaker pattern
class APIClient:
    def __init__(self):
        self.failure_count = 0
        self.circuit_open = False
        self.last_failure = None
    
    def call(self, endpoint):
        if self.circuit_open:
            if time_since_last_failure > 60:
                self.circuit_open = False
            else:
                raise CircuitOpenError()
        
        try:
            response = requests.get(endpoint, timeout=5)
            self.failure_count = 0
            return response
        except Exception as e:
            self.failure_count += 1
            if self.failure_count > 3:
                self.circuit_open = True
                self.last_failure = time.now()
            raise
```

#### 4.3.3 Data Validation Pipeline
```python
# Schema validation
schema = {
    "fips": {"type": "string", "length": 5, "regex": r"^\d{5}$"},
    "latitude": {"type": "float", "min": 24.5, "max": 49.4},
    "longitude": {"type": "float", "min": -124.8, "max": -66.9},
    "risk_score": {"type": "float", "min": 0, "max": 1}
}

# Anomaly detection
def detect_anomalies(df):
    anomalies = []
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            z_scores = np.abs(stats.zscore(df[col]))
            outliers = df[z_scores > 3]
            if len(outliers) > 0:
                anomalies.append({"column": col, "count": len(outliers)})
    return anomalies
```

---

## 5. Implementation Roadmap

### 5.1 Hackathon Phase (48 Hours)

#### Hour 0-8: Foundation
- [ ] Implement NOAA NWS weather API client
- [ ] Add weather alert correlation features
- [ ] Cache layer for API responses

#### Hour 8-16: EMS Integration
- [ ] Download and process NEMSIS 2024 dataset
- [ ] Engineer EMS response metrics
- [ ] Add `get_ems_response_metrics()` MCP tool

#### Hour 16-24: Geospatial Enhancement
- [ ] USGS earthquake API integration
- [ ] Seismic risk feature engineering
- [ ] Add `get_seismic_risk()` MCP tool

#### Hour 24-32: Weather Intelligence
- [ ] Weather forecast integration
- [ ] Climate vulnerability scoring
- [ ] Add `correlate_weather_with_vulnerability()` tool

#### Hour 32-40: Advanced Analytics
- [ ] Time-series forecasting (Prophet)
- [ ] Disaster acceleration detection
- [ ] Predictive risk trajectories

#### Hour 40-48: Integration & Polish
- [ ] Dashboard integration
- [ ] Data quality indicators
- [ ] Documentation

### 5.2 Post-Hackathon Phase

#### Month 1: Healthcare AI
- [ ] TAME-PAIN credentialing application
- [ ] Audio preprocessing pipeline
- [ ] Pain assessment model integration

#### Month 2: Genomics Integration
- [ ] ADNI data access application
- [ ] Cognitive vulnerability features
- [ ] Multi-modal risk assessment

#### Month 3: Real-Time Streaming
- [ ] WebSocket implementation for live alerts
- [ ] Stream processing pipeline
- [ ] Alert subscription system

---

## 6. Data Governance & Compliance

### 6.1 Access Requirements

| Source | Credentialing | DUA Required | Timeline |
|--------|---------------|--------------|----------|
| FEMA Open | None | No | Immediate |
| Census ACS | API Key | No | Immediate |
| HIFLD | None | No | Immediate |
| NOAA NWS | None | No | Immediate |
| USGS | None | No | Immediate |
| NEMSIS | Registration | Yes | 1-2 weeks |
| TAME-PAIN | PhysioNet | Yes | 2-3 days |
| ADNI | Research app | Yes | 2-4 weeks |
| TCGA | dbGaP | Yes | 2-4 weeks |

### 6.2 Data Retention

| Data Type | Retention Period | Rationale |
|-----------|------------------|-----------|
| Raw API responses | 7 days | Debugging, caching |
| Processed features | Indefinite | Historical analysis |
| User queries | 90 days | Usage analytics |
| Alert logs | 1 year | Compliance, auditing |
| Audio data (TAME) | Per DUA | Research only |

### 6.3 Privacy Considerations

- **No PII in core dataset**: County-level aggregation only
- **NEMSIS**: Use public dataset; no individual records
- **TAME-PAIN**: De-identified audio; research use only
- **API logs**: Anonymize IP addresses

---

## 7. Success Metrics

### 7.1 Data Coverage
- [ ] 100% US county coverage (3,221 counties + DC)
- [ ] 50+ engineered features
- [ ] 5+ real-time data sources
- [ ] <5 minute data freshness for alerts

### 7.2 Quality Metrics
- [ ] <5% missing values in critical features
- [ ] 99.9% API uptime (with caching)
- [ ] <100ms query response time
- [ ] 100% data lineage tracking

### 7.3 Impact Metrics
- [ ] 45+ MCP tools operational
- [ ] 10+ predictive models deployed
- [ ] Real-time alert capability
- [ ] Multi-modal data integration

---

## 8. Appendix: Data Source Details

### 8.1 API Endpoints

```yaml
# FEMA Open
base_url: https://www.fema.gov/api/open
endpoints:
  - /v2/DisasterDeclarationsSummaries
  - /v1/FemaWebDisasterDeclarations

# Census ACS
base_url: https://api.census.gov/data/2022/acs/acs5
endpoints:
  - /?get=NAME,B01001_001E&for=county:*

# NOAA NWS
base_url: https://api.weather.gov
endpoints:
  - /alerts/active
  - /points/{lat},{lon}
  - /gridpoints/{office}/{gridX},{gridY}/forecast

# USGS Earthquakes
base_url: https://earthquake.usgs.gov/fdsnws/event/1
endpoints:
  - /query?format=geojson&starttime={date}
```

### 8.2 Feature Dictionary

See `docs/DATA_DICTIONARY.md` for complete feature documentation.

### 8.3 Model Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| Best Model | `models/best_model.pkl` | Logistic Regression (F1=0.983) |
| Scaler | `models/scaler.pkl` | StandardScaler fitted on training |
| Feature Names | `models/feature_names.pkl` | Ordered feature list |
| Agent Config | `models/agent_config.json` | MCP tool definitions |

---

## 9. Conclusion

The ResilienceAI data strategy prioritizes:

1. **Immediate Value**: Tier 1 sources provide comprehensive coverage today
2. **Operational Intelligence**: Tier 2 adds real-time capabilities for hackathon
3. **Long-term Differentiation**: Tier 3 enables healthcare AI post-hackathon

**Key Success Factors:**
- Robust caching for API resilience
- Comprehensive feature engineering pipeline
- Proactive data quality monitoring
- Clear governance for credentialed datasets

**Next Actions:**
1. Implement NOAA NWS integration (Hour 0-8)
2. Process NEMSIS 2024 dataset (Hour 8-16)
3. Add USGS seismic features (Hour 16-24)
4. Submit TAME-PAIN credentialing (parallel)

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: Data Strategy Specialist - ResilienceAI Council*
