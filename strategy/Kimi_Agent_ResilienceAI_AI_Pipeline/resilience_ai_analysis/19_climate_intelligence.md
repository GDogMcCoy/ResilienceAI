# ResilienceAI Climate Intelligence Enhancement

## Executive Summary

This document provides a comprehensive analysis of the current climate capabilities in ResilienceAI and proposes a multi-phase enhancement strategy to build a world-class climate intelligence platform. The current system integrates 5 climate data sources (RCC-ACIS, FEMA NRI, USGS NWIS, NOAA SWDI/SPC, US Drought Monitor) with basic trend analysis and forecasting capabilities.

---

## Current State Analysis

### Existing Climate Infrastructure

#### 1. Climate Data Client (`src/climate_client.py`)
**Current Capabilities:**
- **RCC-ACIS Integration**: Historical temperature/precipitation data (4km grid, county-level)
- **FEMA NRI**: 18-hazard risk profiles for all US counties
- **USGS NWIS**: Streamflow gauges and flood frequency analysis
- **NOAA SWDI/SPC**: Severe weather event tracking (tornadoes, hail, wind)
- **US Drought Monitor**: Weekly drought classification (D0-D4)

**Key Classes:**
```python
class ClimateIntelligenceClient:
    """Unified facade for all 5 climate data sources"""
    def __init__(self):
        self.acis = ACISClient()
        self.nri = FEMANRIClient()
        self.usgs = USGSFloodClient()
        self.severe = SevereWeatherClient()
        self.drought = DroughtMonitorClient()
```

#### 2. Weather Client (`src/weather_client.py`)
**Current Capabilities:**
- Real-time NOAA weather alerts
- County-level alert filtering
- Severity-based risk correlation
- Vulnerability-weighted composite risk scoring

#### 3. Predictive Models (`src/predictive_models.py`)
**Current Capabilities:**
- Prophet/ARIMA time-series forecasting
- Climate scenario modeling (IPCC SSPs)
- Gradient Boosting/Random Forest disaster prediction
- Risk trajectory analysis

---

## Proposed Climate Intelligence Platform

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI CLIMATE INTELLIGENCE PLATFORM                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   DATA       │  │   ANALYSIS   │  │   MODELING   │  │  VISUALIZE   │    │
│  │   LAYER      │  │   LAYER      │  │   LAYER      │  │   LAYER      │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐    │
│  │ NOAA APIs    │  │ Trend Engine │  │ ML Models    │  │ Dashboard    │    │
│  │ NCEI/ACIS    │  │ Anomaly Det. │  │ Forecasting  │  │ Maps         │    │
│  │ USGS NWIS    │  │ Correlation  │  │ Scenarios    │  │ Reports      │    │
│  │ FEMA NRI     │  │ Clustering   │  │ Ensembles    │  │ Alerts       │    │
│  │ NASA GEE     │  │ Index Calc.  │  │ Downscaling  │  │ API          │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Enhanced NOAA Integration

### 1.1 NCEI Climate Data Online (CDO) Integration

**File:** `src/climate/noaa_cdo_client.py`

```python
"""NOAA NCEI Climate Data Online Client"""
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class StationMetadata:
    """NOAA weather station metadata"""
    station_id: str
    name: str
    state: str
    latitude: float
    longitude: float
    elevation: float
    data_coverage: float

class NCEIClient:
    """NOAA NCEI Climate Data Online API Client"""
    BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"
    
    DATASETS = {
        "daily": "GHCND",           # Global Historical Climatology Network-Daily
        "summary": "GSOM",
        "normals": "NORMAL_DLY",    # Daily Normals (1991-2020)
    }
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.environ.get("NOAA_CDO_TOKEN", "")
        self.session = requests.Session()
        self.session.headers.update({
            "token": self.api_token,
            "Accept": "application/json"
        })
    
    def find_stations(self, state: str = None, bbox: Tuple = None, 
                      limit: int = 1000) -> List[StationMetadata]:
        """Find weather stations by location criteria"""
        params = {"datasetid": "GHCND", "limit": min(limit, 1000)}
        if state:
            params["locationid"] = f"FIPS:{state}"
        if bbox:
            params["extent"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        
        resp = self._make_request("/stations", params)
        return [StationMetadata(**r) for r in resp.get("results", [])]
    
    def get_daily_data(self, station_id: str, start_date: str, 
                       end_date: str) -> pd.DataFrame:
        """Retrieve daily observations for a station"""
        params = {
            "datasetid": "GHCND",
            "stationid": station_id,
            "startdate": start_date,
            "enddate": end_date,
            "units": "standard"
        }
        resp = self._make_request("/data", params)
        df = pd.DataFrame(resp.get("results", []))
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.pivot(index="date", columns="datatype", values="value")
        return df
```

### 1.2 NOAA Radar and Satellite Integration

**File:** `src/climate/noaa_radar_client.py`

```python
"""NOAA Radar and Satellite Data Client"""
import boto3
from botocore.config import Config
import numpy as np
from datetime import datetime
import xarray as xr

class NOAARadarClient:
    """NOAA NEXRAD and MRMS Data Access"""
    
    BUCKETS = {
        "nexrad_l2": "noaa-nexrad-level2",
        "mrms": "noaa-mrms-pds"
    }
    
    MRMS_PRODUCTS = {
        "reflectivity": "MergedReflectivityQC",
        "precip_rate": "PrecipRate",
        "severe_prob": "SevereProbability",
        "rotation": "RotationTrack",
        "hail": "HailSwath"
    }
    
    def __init__(self):
        self.s3 = boto3.client('s3', config=Config(signature_version=botocore.UNSIGNED))
    
    def get_latest_radar_scan(self, radar_site: str) -> xr.Dataset:
        """Get latest NEXRAD Level 2 scan for a radar site"""
        prefix = f"{radar_site}/{datetime.utcnow():%Y/%m/%d}/"
        response = self.s3.list_objects_v2(Bucket=self.BUCKETS["nexrad_l2"], 
                                           Prefix=prefix, MaxKeys=10)
        if not response.get("Contents"):
            raise ValueError(f"No radar data found for {radar_site}")
        latest = sorted(response["Contents"], key=lambda x: x["LastModified"])[-1]
        obj = self.s3.get_object(Bucket=self.BUCKETS["nexrad_l2"], Key=latest["Key"])
        return self._parse_nexrad_l2(obj["Body"].read())
    
    def get_severe_weather_detected(self, bbox: Tuple, time_window: int = 60) -> List[Dict]:
        """Detect severe weather features using MRMS"""
        features = []
        rotation = self.get_mrms_product("rotation")
        hail = self.get_mrms_product("hail")
        # Extract features within bbox
        return features
```

---

## Phase 2: Climate Risk Projection Models

### 2.1 Climate Change Impact Modeler

**File:** `src/climate/climate_impact_modeler.py`

```python
"""Climate Change Impact Modeler for ResilienceAI"""
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import xarray as xr

class ClimateScenario(Enum):
    """IPCC AR6 Shared Socioeconomic Pathways"""
    SSP1_19 = "ssp1_1.9"  # Very low emissions
    SSP2_45 = "ssp2_4.5"  # Intermediate
    SSP5_85 = "ssp5_8.5"  # Very high emissions

@dataclass
class ClimateProjection:
    scenario: str
    year: int
    latitude: float
    longitude: float
    mean_temp_c: float
    temp_anomaly_c: float
    heat_wave_days: int
    drought_risk_index: float
    flood_risk_index: float

class CMIP6Downscaler:
    """Downscale CMIP6 climate projections to local scales"""
    MODELS = ["ACCESS-CM2", "BCC-CSM2-MR", "CanESM5", "GFDL-ESM4", 
              "IPSL-CM6A-LR", "MIROC6"]
    
    def load_cmip6_ensemble(self, variable: str, scenario: ClimateScenario,
                           bbox: Tuple) -> xr.Dataset:
        """Load CMIP6 multi-model ensemble for a region"""
        datasets = []
        for model in self.MODELS:
            try:
                ds = self._load_model_data(model, variable, scenario)
                ds = ds.sel(lon=slice(bbox[0], bbox[2]), lat=slice(bbox[1], bbox[3]))
                ds["model"] = model
                datasets.append(ds)
            except Exception as e:
                print(f"Could not load {model}: {e}")
        return xr.concat(datasets, dim="model")
    
    def project_county_climate(self, county_fips: str, scenario: ClimateScenario,
                               years: List[int] = None) -> List[ClimateProjection]:
        """Generate county-level climate projections"""
        if years is None:
            years = list(range(2025, 2101, 5))
        # Implementation details...
        return projections

class ClimateRiskProjector:
    """Project future disaster risk under climate change scenarios"""
    
    def __init__(self, impact_modeler: CMIP6Downscaler):
        self.impact_modeler = impact_modeler
        self.risk_functions = {
            "flood": self._flood_risk_function,
            "drought": self._drought_risk_function,
            "heat": self._heat_risk_function
        }
    
    def project_disaster_risk(self, county_fips: str, disaster_type: str,
                              scenario: ClimateScenario, projection_years: int = 30) -> pd.DataFrame:
        """Project disaster risk trajectory for a county"""
        years = list(range(2025, 2025 + projection_years + 1))
        climate_proj = self.impact_modeler.project_county_climate(county_fips, scenario, years)
        current_vuln = self._get_current_vulnerability(county_fips)
        risk_func = self.risk_functions.get(disaster_type)
        
        projections = []
        for proj in climate_proj:
            baseline_risk = risk_func(proj, current_vuln, baseline=True)
            projected_risk = risk_func(proj, current_vuln, baseline=False)
            projections.append({
                "year": proj.year,
                "baseline_risk": baseline_risk,
                "projected_risk": projected_risk,
                "risk_ratio": projected_risk / baseline_risk if baseline_risk > 0 else 1
            })
        return pd.DataFrame(projections)
```

---

## Phase 3: Extreme Weather Analysis

### 3.1 Extreme Event Detection and Analysis

**File:** `src/climate/extreme_event_analyzer.py`

```python
"""Extreme Weather Event Analysis Module"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ExtremeEvent:
    event_id: str
    event_type: str
    start_date: datetime
    end_date: datetime
    peak_intensity: float
    severity_score: float
    return_period: float

class ExtremeEventDetector:
    """Detect extreme weather events from historical data"""
    
    EVENT_DEFINITIONS = {
        "heat_wave": {"variable": "tmax", "threshold_percentile": 95, "min_duration_days": 3},
        "cold_wave": {"variable": "tmin", "threshold_percentile": 5, "min_duration_days": 3},
        "heavy_precipitation": {"variable": "prcp", "threshold_percentile": 95, "min_duration_days": 1},
        "drought": {"variable": "spi", "threshold_value": -1.5, "min_duration_days": 30}
    }
    
    def __init__(self, baseline_period: Tuple[str, str] = ("1991", "2020")):
        self.baseline_period = baseline_period
        self.baseline_stats = {}
    
    def fit_baseline(self, data: pd.DataFrame, variable: str):
        """Calculate baseline statistics for extreme event detection"""
        baseline_data = data[self.baseline_period[0]:self.baseline_period[1]]
        baseline_data["month"] = baseline_data.index.month
        self.baseline_stats[variable] = {
            "monthly_mean": baseline_data.groupby("month")[variable].mean(),
            "monthly_95th": baseline_data.groupby("month")[variable].quantile(0.95),
            "annual_max": baseline_data.groupby(baseline_data.index.year)[variable].max()
        }
    
    def detect_events(self, data: pd.DataFrame, event_type: str) -> List[ExtremeEvent]:
        """Detect extreme events in a time series"""
        definition = self.EVENT_DEFINITIONS.get(event_type)
        variable = definition["variable"]
        # Implementation details...
        return events
    
    def calculate_return_period(self, event: ExtremeEvent, variable: str) -> float:
        """Calculate return period using extreme value theory"""
        from scipy.stats import genextreme
        annual_extremes = self.baseline_stats[variable]["annual_max"]
        shape, loc, scale = genextreme.fit(annual_extremes)
        exceedance_prob = 1 - genextreme.cdf(event.peak_intensity, shape, loc, scale)
        return 1 / exceedance_prob if exceedance_prob > 0 else np.inf
```

---

## Phase 4: Drought Index Calculation

### 4.1 Multi-Index Drought Monitor

**File:** `src/climate/drought_index_calculator.py`

```python
"""Drought Index Calculator - Multiple drought indices"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DroughtIndex:
    index_name: str
    value: float
    date: datetime
    severity: str
    severity_description: str

class DroughtIndexCalculator:
    """Calculate multiple drought indices from climate data"""
    
    def __init__(self, calibration_period: Tuple[str, str] = ("1991", "2020")):
        self.calibration_period = calibration_period
    
    def calculate_spi(self, precipitation: pd.Series, timescale: int = 3) -> pd.Series:
        """Calculate Standardized Precipitation Index (SPI)"""
        precip_accum = precipitation.rolling(window=timescale, min_periods=timescale).sum()
        spi_values = pd.Series(index=precipitation.index, dtype=float)
        
        for month in range(1, 13):
            month_mask = precip_accum.index.month == month
            month_data = precip_accum[month_mask].dropna()
            if len(month_data) < 10:
                continue
            alpha, loc, beta = stats.gamma.fit(month_data[month_data > 0], floc=0)
            p_zero = (month_data == 0).sum() / len(month_data)
            
            for idx in month_data.index:
                x = month_data[idx]
                cdf = p_zero if x == 0 else p_zero + (1 - p_zero) * stats.gamma.cdf(x, alpha, loc=loc, scale=beta)
                spi_values[idx] = stats.norm.ppf(cdf)
        return spi_values
    
    def calculate_spei(self, precipitation: pd.Series, temperature: pd.Series,
                       latitude: float, timescale: int = 3) -> pd.Series:
        """Calculate Standardized Precipitation Evapotranspiration Index (SPEI)"""
        pet = self._thornthwaite_pet(temperature, latitude)
        water_balance = precipitation - pet
        if timescale > 1:
            water_balance = water_balance.rolling(window=timescale, min_periods=timescale).sum()
        # Fit log-logistic distribution and calculate SPEI
        return spei_values
    
    def create_drought_monitor(self, county_fips: str, start_date: str, 
                               end_date: str) -> pd.DataFrame:
        """Create comprehensive drought monitor for a county"""
        climate_data = self._load_county_climate(county_fips, start_date, end_date)
        spi_3 = self.calculate_spi(climate_data["prcp"], timescale=3)
        spi_12 = self.calculate_spi(climate_data["prcp"], timescale=12)
        
        monitor = pd.DataFrame({
            "date": climate_data.index,
            "spi_3": spi_3.values,
            "spi_12": spi_12.values
        })
        monitor["composite"] = monitor[["spi_3", "spi_12"]].mean(axis=1)
        monitor["usdm_category"] = monitor["composite"].apply(self._spi_to_usdm)
        return monitor
    
    def _spi_to_usdm(self, spi: float) -> str:
        """Convert SPI value to USDM category"""
        if spi >= 0: return "None"
        elif spi >= -0.5: return "D0"
        elif spi >= -1.0: return "D1"
        elif spi >= -1.5: return "D2"
        elif spi >= -2.0: return "D3"
        else: return "D4"
```

---

## Phase 5: Flood Risk Assessment

### 5.1 Comprehensive Flood Risk Modeler

**File:** `src/climate/flood_risk_modeler.py`

```python
"""Flood Risk Assessment Module"""
import numpy as np
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FloodRiskAssessment:
    county_fips: str
    assessment_date: datetime
    riverine_risk_score: float
    flash_flood_risk_score: float
    coastal_risk_score: float
    overall_flood_risk: float
    contributing_factors: Dict[str, float]

class FloodRiskModeler:
    """Comprehensive flood risk assessment combining multiple data sources"""
    
    def __init__(self):
        self.usgs_client = USGSFloodClient()
        self.nwm_client = NationalWaterModelClient()
    
    def assess_riverine_flood_risk(self, county_fips: str, forecast_days: int = 7) -> Dict:
        """Assess riverine flood risk using gauge data and forecasts"""
        gauges = self.usgs_client.get_sites_in_county(county_fips)
        if not gauges:
            return {"error": "No streamflow gauges in county", "risk_score": 0.5}
        
        risk_assessments = []
        for gauge in gauges:
            current = self.usgs_client.get_current_flow(gauge["site_id"])
            peaks = self.usgs_client.get_peak_flows(gauge["site_id"])
            stage_ratio = current["stage"] / gauge.get("flood_stage", 999) if current.get("stage") else 0.5
            return_period = self._calculate_return_period(current["discharge"], peaks) if peaks else 100
            risk_score = self._calculate_riverine_risk(stage_ratio, return_period)
            risk_assessments.append({"gauge_id": gauge["site_id"], "risk_score": risk_score})
        
        return {
            "county_fips": county_fips,
            "max_risk_score": max(r["risk_score"] for r in risk_assessments),
            "weighted_risk_score": np.mean([r["risk_score"] for r in risk_assessments])
        }
    
    def assess_flash_flood_risk(self, county_fips: str) -> Dict:
        """Assess flash flood risk using rainfall-runoff relationships"""
        catchments = self._get_catchments_in_county(county_fips)
        ffg = self._get_flash_flood_guidance(county_fips)
        # Calculate rainfall-runoff ratios and risk scores
        return {"county_fips": county_fips, "max_risk_score": 0.0}
    
    def create_comprehensive_assessment(self, county_fips: str) -> FloodRiskAssessment:
        """Create comprehensive flood risk assessment combining all flood types"""
        riverine = self.assess_riverine_flood_risk(county_fips)
        flash = self.assess_flash_flood_risk(county_fips)
        coastal = self.assess_coastal_flood_risk(county_fips)
        
        overall_risk = max([riverine.get("weighted_risk_score", 0),
                           flash.get("max_risk_score", 0),
                           coastal.get("risk_score", 0)])
        
        return FloodRiskAssessment(
            county_fips=county_fips,
            assessment_date=datetime.now(),
            riverine_risk_score=riverine.get("weighted_risk_score", 0),
            flash_flood_risk_score=flash.get("max_risk_score", 0),
            coastal_risk_score=coastal.get("risk_score", 0),
            overall_flood_risk=overall_risk,
            contributing_factors={"impervious_surface": 0.3, "floodplain_occupancy": 0.2}
        )
```

---

## Phase 6: Hurricane Tracking and Prediction

### 6.1 Hurricane Intelligence System

**File:** `src/climate/hurricane_tracker.py`

```python
"""Hurricane Tracking and Impact Prediction System"""
import numpy as np
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import requests

@dataclass
class HurricaneTrack:
    timestamp: datetime
    latitude: float
    longitude: float
    max_wind_kts: int
    storm_category: int
    wind_radii: Dict[str, int]

class HurricaneTracker:
    """Hurricane tracking and forecast integration"""
    
    NHC_ATCF_URL = "https://ftp.nhc.noaa.gov/atcf/index/"
    SAFFIR_SIMPSON = {
        0: (0, 33), 1: (34, 63), 2: (64, 82), 3: (83, 95),
        4: (96, 112), 5: (113, 999)
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "ResilienceAI/2.0"})
    
    def get_active_storms(self) -> List[Dict]:
        """Get list of currently active tropical cyclones"""
        url = "https://www.nhc.noaa.gov/CurrentStorms.json"
        resp = self.session.get(url, timeout=30)
        data = resp.json()
        return [{
            "storm_id": s.get("id"), "storm_name": s.get("name"),
            "max_wind": s.get("maxWind"), "classification": s.get("classification")
        } for s in data.get("activeStorms", [])]
    
    def get_storm_track(self, storm_id: str) -> List[HurricaneTrack]:
        """Get best track (historical positions) for a storm"""
        url = f"{self.NHC_ATCF_URL}/b{storm_id.lower()}.dat"
        resp = self.session.get(url, timeout=30)
        # Parse ATCF format
        return tracks
    
    def predict_county_impact(self, storm_id: str, county_fips: str) -> Dict:
        """Predict hurricane impact on a specific county"""
        county = self._get_county_info(county_fips)
        ensemble = self.get_ensemble_forecast(storm_id)
        
        impacts = []
        for track_point in ensemble.get("official", []):
            distance_nm = self._haversine_distance(county["lat"], county["lon"],
                                                   track_point.latitude, track_point.longitude)
            wind_at_county = self._calculate_wind_at_distance(track_point.max_wind_kts, 
                                                              distance_nm, track_point.wind_radii)
            impacts.append({"distance_nm": distance_nm, "wind_speed_kts": wind_at_county})
        
        wind_speeds = [i["wind_speed_kts"] for i in impacts]
        return {
            "county_fips": county_fips,
            "max_sustained_wind_kts": max(wind_speeds) if wind_speeds else 0,
            "probability_tropical_storm_force": np.mean([1 if w >= 34 else 0 for w in wind_speeds]),
            "probability_hurricane_force": np.mean([1 if w >= 64 else 0 for w in wind_speeds])
        }
```

---

## Phase 7: Seasonal Forecasting

### 7.1 Seasonal Climate Forecast System

**File:** `src/climate/seasonal_forecaster.py`

```python
"""Seasonal Climate Forecasting System"""
import numpy as np
import pandas as pd
from typing import Dict
from dataclasses import dataclass
from datetime import datetime
import requests

@dataclass
class SeasonalForecast:
    region: str
    forecast_season: str
    forecast_year: int
    temp_forecast: str
    temp_probability: Dict[str, float]
    precip_forecast: str
    precip_probability: Dict[str, float]
    confidence: str

class SeasonalForecaster:
    """Seasonal climate forecasting using multiple sources"""
    
    CPC_OUTLOOK_URL = "https://www.cpc.ncep.noaa.gov/products/predictions/"
    SEASONS = {"DJF": (12, 1, 2), "MAM": (3, 4, 5), "JJA": (6, 7, 8), "SON": (9, 10, 11)}
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_enso_forecast(self) -> Dict:
        """Get ENSO forecast from CPC/IRI"""
        nino34 = self._get_nino34_anomaly()
        if nino34 > 0.5:
            enso_state = "El Nino"
        elif nino34 < -0.5:
            enso_state = "La Nina"
        else:
            enso_state = "Neutral"
        return {"current_state": enso_state, "nino34_anomaly_c": nino34}
    
    def create_county_forecast(self, county_fips: str, target_season: str,
                               target_year: int) -> SeasonalForecast:
        """Create seasonal forecast for a specific county"""
        county = self._get_county_info(county_fips)
        enso = self.get_enso_forecast()
        
        # Apply local ENSO relationships
        temp_prob = {"above_normal": 0.33, "near_normal": 0.34, "below_normal": 0.33}
        precip_prob = {"above_normal": 0.33, "near_normal": 0.34, "below_normal": 0.33}
        
        return SeasonalForecast(
            region=county_fips,
            forecast_season=target_season,
            forecast_year=target_year,
            temp_forecast="Near Normal",
            temp_probability=temp_prob,
            precip_forecast="Near Normal",
            precip_probability=precip_prob,
            confidence="Medium"
        )
```

---

## Phase 8: Climate Data Visualization

### 8.1 Climate Visualization Suite

**File:** `src/visualizations/climate_visualizations.py`

```python
"""Climate Data Visualization Suite for ResilienceAI"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List

class ClimateVisualizer:
    """Comprehensive climate data visualization suite"""
    
    def __init__(self, theme: str = "plotly_white"):
        self.theme = theme
        self.color_schemes = {
            "temperature": ["#2166ac", "#4393c3", "#92c5de", "#f7f7f7", "#fddbc7", "#f4a582", "#d6604d", "#b2182b"],
            "drought": ["#1a9641", "#a6d96a", "#ffffbf", "#fdae61", "#d7191c", "#8B0000", "#4B0000"]
        }
    
    def create_climate_trends_chart(self, climate_data: pd.DataFrame, 
                                    variables: List[str] = ["tmax", "tmin", "prcp"]) -> go.Figure:
        """Create interactive climate trends chart"""
        fig = make_subplots(rows=len(variables), cols=1, 
                           subplot_titles=[f"{v.upper()} Trends" for v in variables])
        
        for i, var in enumerate(variables, 1):
            if var not in climate_data.columns:
                continue
            fig.add_trace(go.Scatter(x=climate_data.index, y=climate_data[var],
                                      mode='lines', name=var.upper()), row=i, col=1)
            # Add trend line
            trend = self._calculate_trend(climate_data[var])
            fig.add_trace(go.Scatter(x=climate_data.index, y=trend,
                                      mode='lines', name=f'{var.upper()} Trend',
                                      line=dict(dash='dash')), row=i, col=1)
        
        fig.update_layout(height=300 * len(variables), title_text="Climate Trends Analysis",
                         template=self.theme)
        return fig
    
    def create_drought_monitor_heatmap(self, drought_data: pd.DataFrame) -> go.Figure:
        """Create drought monitor heatmap showing drought severity over time"""
        heatmap_data = drought_data.pivot(index="county_fips", columns="date", values="spi_3")
        colorscale = [[0, "#4B0000"], [0.17, "#8B0000"], [0.33, "#d7191c"],
                      [0.5, "#fdae61"], [0.67, "#ffffbf"], [0.83, "#a6d96a"], [1, "#1a9641"]]
        
        fig = go.Figure(data=go.Heatmap(z=heatmap_data.values, x=heatmap_data.columns,
                                        y=heatmap_data.index, colorscale=colorscale,
                                        zmid=0, zmin=-3, zmax=3))
        fig.update_layout(title="Drought Monitor - SPI-3 Heatmap", template=self.theme)
        return fig
    
    def create_climate_projection_chart(self, projections: pd.DataFrame) -> go.Figure:
        """Create climate projection chart with multiple scenarios"""
        fig = go.Figure()
        scenario_colors = {"ssp1_19": "#2ca02c", "ssp2_45": "#ff7f0e", "ssp5_85": "#d62728"}
        
        for scenario in projections["scenario"].unique():
            scenario_data = projections[projections["scenario"] == scenario]
            color = scenario_colors.get(scenario, "#1f77b4")
            fig.add_trace(go.Scatter(x=scenario_data["year"], y=scenario_data["projected_value"],
                                      mode='lines', name=scenario.upper(), line=dict(color=color)))
        
        fig.update_layout(title="Climate Projections by Scenario", template=self.theme)
        return fig
    
    def _calculate_trend(self, series: pd.Series) -> pd.Series:
        """Calculate linear trend for a time series"""
        x = np.arange(len(series))
        mask = ~np.isnan(series.values)
        if mask.sum() < 2:
            return pd.Series(index=series.index, dtype=float)
        slope, intercept = np.polyfit(x[mask], series.values[mask], 1)
        return pd.Series(slope * x + intercept, index=series.index)
```

---

## Implementation Priority Order

### Phase 1 (Months 1-2): Foundation
1. **Enhanced NOAA Integration** - NCEI CDO client for historical station data
2. **Climate Data Pipeline** - Standardized data ingestion

### Phase 2 (Months 3-4): Analysis
3. **Extreme Event Detection** - Statistical threshold detection
4. **Drought Index Suite** - SPI, SPEI, PDSI implementations

### Phase 3 (Months 5-6): Modeling
5. **Climate Risk Projections** - CMIP6 downscaling
6. **Flood Risk Assessment** - Multi-source flood modeling

### Phase 4 (Months 7-8): Advanced Features
7. **Hurricane Tracking** - NHC integration
8. **Seasonal Forecasting** - CPC outlook integration

### Phase 5 (Months 9-10): Visualization
9. **Climate Visualization Suite** - Interactive dashboards

---

## Integration Points with Existing Code

### 1. Climate Client Integration
```python
# In src/climate_client.py
from src.climate.noaa_cdo_client import NCEIClient
from src.climate.drought_index_calculator import DroughtIndexCalculator
from src.climate.extreme_event_analyzer import ExtremeEventDetector

class ClimateIntelligenceClient:
    def __init__(self):
        self.acis = ACISClient()
        self.nri = FEMANRIClient()
        self.ncei = NCEIClient()
        self.drought_calc = DroughtIndexCalculator()
        self.extreme_detector = ExtremeEventDetector()
```

### 2. Predictive Models Integration
```python
# In src/predictive_models.py
from src.climate.climate_impact_modeler import CMIP6Downscaler
from src.climate.flood_risk_modeler import FloodRiskModeler

class ClimateScenarioModeler:
    def __init__(self, baseline_data: pd.DataFrame):
        self.baseline = baseline_data.copy()
        self.downscaler = CMIP6Downscaler()
        self.flood_modeler = FloodRiskModeler()
```

---

## Data Source Summary

| Source | Data Type | Update Frequency | Access Method |
|--------|-----------|------------------|---------------|
| NOAA NCEI CDO | Historical weather | Daily | REST API |
| NOAA NEXRAD | Radar data | Real-time | AWS S3 |
| NOAA MRMS | Multi-sensor | Real-time | AWS S3 |
| NOAA CPC | Seasonal outlooks | Monthly | HTTP/FTP |
| USGS NWIS | Streamflow | 15-min | REST API |
| FEMA NFHL | Flood maps | Annual | REST API |
| NHC ATCF | Hurricane tracks | 6-hour | FTP/HTTP |
| CMIP6 | Climate projections | Static | ESGF/HTTP |
| US Drought Monitor | Drought status | Weekly | REST API |
| IRI/NMME | Seasonal ensemble | Monthly | HTTP |

---

## File Structure

```
src/
├── climate/
│   ├── __init__.py
│   ├── noaa_cdo_client.py          # NCEI historical data
│   ├── noaa_radar_client.py        # NEXRAD/MRMS data
│   ├── climate_impact_modeler.py   # CMIP6 projections
│   ├── extreme_event_analyzer.py   # Extreme event detection
│   ├── drought_index_calculator.py # Drought indices
│   ├── flood_risk_modeler.py       # Flood assessment
│   ├── hurricane_tracker.py        # Hurricane tracking
│   ├── seasonal_forecaster.py      # Seasonal forecasts
│   └── utils.py                    # Climate utilities
├── visualizations/
│   ├── __init__.py
│   └── climate_visualizations.py   # Climate viz suite
└── [existing files...]
```

---

## Conclusion

This comprehensive climate intelligence enhancement will transform ResilienceAI into a world-class climate risk assessment platform. The phased implementation approach ensures incremental value delivery while building toward a complete climate intelligence system.

Key benefits:
- **Improved Data Quality**: Direct NOAA/NCEI integration
- **Enhanced Analysis**: Multi-index drought monitoring, extreme event detection
- **Future Planning**: Climate change projections and scenario modeling
- **Better Communication**: Rich visualizations and dashboards
- **Operational Value**: Real-time flood/hurricane tracking, seasonal forecasts

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: Climate Intelligence Engineering Team*
