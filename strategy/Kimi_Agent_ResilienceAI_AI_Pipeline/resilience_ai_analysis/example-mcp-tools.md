---
title: MCP Tools Reference
description: Complete reference for ResilienceAI's 45+ Model Context Protocol (MCP) tools
category: API Reference
version: 2.0.0
---

# MCP Tools Reference

## Overview

ResilienceAI provides **45+ Model Context Protocol (MCP) tools** for comprehensive disaster vulnerability assessment. These composable tools enable querying, analysis, prediction, and export functionality through a unified interface.

## Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| **Core Query** | 4 | Basic county queries and comparisons |
| **Advanced Analytics** | 8 | Risk analysis, gap analysis, equity assessment |
| **Export / Integration** | 5 | FHIR, GeoJSON, briefing generation |
| **Real-Time Systems** | 6 | Weather alerts, subscriptions, monitoring |
| **Agricultural Analysis** | 3 | Crop yield, agricultural vulnerability |
| **Predictive Modeling** | 5 | Forecasting, climate projections |
| **Network Analysis** | 4 | Cascade analysis, infrastructure networks |
| **Intervention Planning** | 4 | ROI calculation, scenario simulation |
| **Spatial Statistics** | 6 | Spatial autocorrelation, clustering |

## Core Query Tools

### query_counties

Query counties based on vulnerability criteria.

**Signature:**
```python
query_counties(
    state: Optional[str] = None,
    min_risk_score: Optional[float] = None,
    max_risk_score: Optional[float] = None,
    incident_types: Optional[List[str]] = None,
    limit: int = 100
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `state` | `str` | No | `None` | State name or abbreviation to filter by |
| `min_risk_score` | `float` | No | `None` | Minimum risk score (0-1) |
| `max_risk_score` | `float` | No | `None` | Maximum risk score (0-1) |
| `incident_types` | `List[str]` | No | `None` | Filter by disaster types experienced |
| `limit` | `int` | No | `100` | Maximum number of results |

**Returns:**

```json
{
  "status": "success",
  "count": 15,
  "counties": [
    {
      "fips": "29019",
      "name": "Boone County, Missouri",
      "state": "Missouri",
      "risk_score": 0.42,
      "vulnerability_index": 0.38,
      "population": 183,000
    }
  ],
  "query_params": {
    "state": "Missouri",
    "min_risk_score": 0.3
  }
}
```

**Example Usage:**

```python
# Query high-risk counties in Missouri
result = agent.query_counties(
    state="Missouri",
    min_risk_score=0.5,
    limit=10
)

# Query counties with flood history
result = agent.query_counties(
    incident_types=["Flood"],
    max_risk_score=0.7
)
```

---

### get_county_detail

Get detailed vulnerability information for a specific county.

**Signature:**
```python
get_county_detail(
    county_fips: str,
    include_features: bool = True,
    include_history: bool = True,
    include_infrastructure: bool = True
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `county_fips` | `str` | Yes | - | 5-digit FIPS county code |
| `include_features` | `bool` | No | `True` | Include all 66 features |
| `include_history` | `bool` | No | `True` | Include disaster history |
| `include_infrastructure` | `bool` | No | `True` | Include infrastructure data |

**Returns:**

```json
{
  "status": "success",
  "county": {
    "fips": "29019",
    "name": "Boone County, Missouri",
    "state": "Missouri",
    "population": 183000,
    "risk_score": 0.42,
    "risk_category": "Moderate",
    "features": {
      "demographics": {
        "poverty_pct": 14.2,
        "elderly_pct": 13.8,
        "disability_pct": 12.5,
        "uninsured_pct": 9.3
      },
      "infrastructure": {
        "dist_nearest_hospital_km": 8.5,
        "hospitals_per_10k": 0.8,
        "dist_nearest_fire_station_km": 4.2
      },
      "disaster_history": {
        "total_declarations": 12,
        "recent_declarations": 3,
        "primary_types": ["Flood", "Severe Storm"]
      }
    }
  }
}
```

---

### compare_counties

Compare multiple counties across vulnerability dimensions.

**Signature:**
```python
compare_counties(
    county_fips_list: List[str],
    metrics: Optional[List[str]] = None,
    normalize: bool = True
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `county_fips_list` | `List[str]` | Yes | - | List of 5-digit FIPS codes |
| `metrics` | `List[str]` | No | `None` | Specific metrics to compare |
| `normalize` | `bool` | No | `True` | Normalize values for comparison |

---

### predict_risk

Predict disaster risk for a county using ML models.

**Signature:**
```python
predict_risk(
    county_fips: str,
    disaster_type: Optional[str] = None,
    confidence_threshold: float = 0.7
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `county_fips` | `str` | Yes | - | 5-digit FIPS county code |
| `disaster_type` | `str` | No | `None` | Specific disaster type to predict |
| `confidence_threshold` | `float` | No | `0.7` | Minimum confidence for predictions |

**Returns:**

```json
{
  "status": "success",
  "county_fips": "29019",
  "predictions": {
    "flood": {
      "probability": 0.65,
      "confidence": 0.82,
      "risk_level": "High"
    },
    "severe_storm": {
      "probability": 0.45,
      "confidence": 0.75,
      "risk_level": "Moderate"
    }
  },
  "model_version": "2.0.0",
  "prediction_date": "2026-02-17"
}
```

---

## Advanced Analytics Tools

### analyze_cascade_risk

Analyze cascading disaster risks across county networks.

**Signature:**
```python
analyze_cascade_risk(
    seed_county_fips: str,
    disaster_type: str,
    cascade_depth: int = 2,
    include_infrastructure: bool = True
) -> Dict[str, Any]
```

**Example:**

```python
result = agent.analyze_cascade_risk(
    seed_county_fips="29019",
    disaster_type="Flood",
    cascade_depth=3
)
```

---

### calculate_intervention_roi

Calculate return on investment for vulnerability interventions.

**Signature:**
```python
calculate_intervention_roi(
    county_fips: str,
    intervention_type: str,
    investment_amount: float,
    time_horizon_years: int = 5
) -> Dict[str, Any]
```

**Intervention Types:**

| Type | Description |
|------|-------------|
| `add_hospital` | Add new hospital facility |
| `add_ems_station` | Add EMS station |
| `add_fire_station` | Add fire station |
| `reduce_poverty` | Poverty reduction program |
| `improve_infrastructure` | General infrastructure improvements |
| `early_warning_system` | Implement early warning systems |

**Returns:**

```json
{
  "status": "success",
  "intervention": "add_hospital",
  "investment": 50000000,
  "roi_analysis": {
    "lives_saved_estimate": 45,
    "economic_benefit": 125000000,
    "roi_ratio": 2.5,
    "payback_period_years": 3.2,
    "risk_reduction_pct": 18.5
  }
}
```

---

## Export Tools

### export_fhir

Export county vulnerability data as FHIR R4 bundle.

**Signature:**
```python
export_fhir(
    county_fips: str,
    bundle_type: str = "collection",
    include_history: bool = True
) -> Dict[str, Any]
```

**Example:**

```python
result = agent.export_fhir(
    county_fips="29019",
    bundle_type="collection"
)

# Save to file
with open("boone_county_fhir.json", "w") as f:
    json.dump(result["bundle"], f, indent=2)
```

---

### export_geojson

Export county data as GeoJSON for mapping tools.

**Signature:**
```python
export_geojson(
    county_fips_list: Optional[List[str]] = None,
    state: Optional[str] = None,
    include_features: List[str] = ["risk_score", "vulnerability_index"]
) -> Dict[str, Any]
```

---

## Real-Time Tools

### get_weather_alerts

Get current NOAA weather alerts for a county.

**Signature:**
```python
get_weather_alerts(
    county_fips: str,
    alert_types: Optional[List[str]] = None,
    active_only: bool = True
) -> Dict[str, Any]
```

**Returns:**

```json
{
  "status": "success",
  "county": "Boone County, Missouri",
  "alerts": [
    {
      "id": "NWS-KLZK-2026-02-17",
      "event": "Severe Thunderstorm Warning",
      "severity": "Severe",
      "urgency": "Immediate",
      "effective": "2026-02-17T14:30:00Z",
      "expires": "2026-02-17T16:00:00Z",
      "description": "Severe thunderstorms producing damaging winds...",
      "instruction": "Take shelter immediately..."
    }
  ],
  "alert_count": 1
}
```

---

### subscribe_to_alerts

Subscribe a county to real-time vulnerability alerts.

**Signature:**
```python
subscribe_to_alerts(
    county_fips: str,
    alert_threshold: float = 0.7,
    channels: List[str] = ["webhook"],
    webhook_url: Optional[str] = None
) -> Dict[str, Any]
```

---

## Predictive Modeling Tools

### forecast_risk_trajectory

Forecast risk trajectory using Prophet or ARIMA models.

**Signature:**
```python
forecast_risk_trajectory(
    county_fips: str,
    forecast_horizon_days: int = 90,
    model_type: str = "prophet",
    confidence_interval: float = 0.95
) -> Dict[str, Any]
```

**Returns:**

```json
{
  "status": "success",
  "county_fips": "29019",
  "forecast": {
    "model": "prophet",
    "horizon_days": 90,
    "predictions": [
      {
        "date": "2026-02-18",
        "risk_score": 0.43,
        "lower_bound": 0.38,
        "upper_bound": 0.48
      }
    ],
    "trend": "increasing",
    "trend_confidence": 0.85
  }
}
```

---

### project_climate_risk

Project future climate risk using IPCC scenarios.

**Signature:**
```python
project_climate_risk(
    county_fips: str,
    ssp_scenario: str = "SSP2-4.5",
    projection_year: int = 2050,
    hazard_types: Optional[List[str]] = None
) -> Dict[str, Any]
```

**SSP Scenarios:**

| Scenario | Description | Warming by 2100 |
|----------|-------------|-----------------|
| `SSP1-1.9` | Sustainability | ~1.5°C |
| `SSP1-2.6` | Sustainability | ~2.0°C |
| `SSP2-4.5` | Middle of the Road | ~2.7°C |
| `SSP3-7.0` | Regional Rivalry | ~3.6°C |
| `SSP5-8.5` | Fossil-fueled Development | ~4.4°C |

---

## Tool Response Format

All MCP tools return a standardized response format:

```json
{
  "status": "success|error",
  "data": { ... },
  "metadata": {
    "timestamp": "2026-02-17T10:30:00Z",
    "version": "2.0.0",
    "tool_name": "query_counties",
    "execution_time_ms": 145
  },
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `INVALID_FIPS` | Invalid FIPS code format | Use 5-digit FIPS code |
| `COUNTY_NOT_FOUND` | County not in database | Check FIPS code |
| `INVALID_PARAMETER` | Invalid parameter value | Check parameter constraints |
| `RATE_LIMITED` | API rate limit exceeded | Wait and retry |
| `DATA_UNAVAILABLE` | Requested data unavailable | Try alternative query |
| `MODEL_ERROR` | ML model prediction error | Check input data |

## Rate Limits

| Tool Category | Requests per Minute | Requests per Hour |
|---------------|---------------------|-------------------|
| Core Query | 60 | 1,000 |
| Analytics | 30 | 500 |
| Real-Time | 120 | 2,000 |
| Export | 10 | 100 |
| Predictive | 20 | 300 |

---

*For tool implementation details, see the [source code](https://github.com/GDogMcCoy/ResilienceAI/tree/main/src/agent.py)*
