# ResilienceAI: Free API Database Expansions Research

**Research Date:** February 17, 2026  
**Researcher:** AI Research Agent  
**Project:** ResilienceAI - MUIDSI Hackathon 2026

---

## Executive Summary

This document presents a curated list of **15 high-value, free-tier APIs** that can significantly expand ResilienceAI's data sources beyond current FEMA, Census, NOAA, and USGS integrations. Each API has been evaluated against strict criteria: free tier available, US county/ZIP granularity, programmatic REST access, reasonable rate limits (>100 requests/day), and documented endpoints.

---

## Table of Contents

1. [Climate & Weather APIs (4)](#1-climate--weather-apis)
2. [Public Health Data APIs (3)](#2-public-health-data-apis)
3. [Infrastructure & Utilities APIs (3)](#3-infrastructure--utilities-apis)
4. [Socioeconomic Enhancement APIs (3)](#4-socioeconomic-enhancement-apis)
5. [Real-time Hazard APIs (2)](#5-real-time-hazard-apis)
6. [Implementation Roadmap](#6-implementation-roadmap)

---

## 1. Climate & Weather APIs

### 1.1 EPA AirNow API

| Attribute | Details |
|-----------|---------|
| **API Name** | EPA AirNow API |
| **Provider** | U.S. Environmental Protection Agency (EPA) |
| **Endpoint URL** | `https://www.airnowapi.org/aq/` |
| **Documentation** | https://docs.airnowapi.org/ |
| **Authentication** | API Key (free registration at airnowapi.org) |
| **Rate Limits** | 500 requests/hour per API key |
| **Data Granularity** | ZIP code, Lat/Lon, Reporting Area |
| **Update Frequency** | Hourly observations, Daily forecasts |
| **Data Retention** | Real-time + 48 hours forecast |

**Integration Value for ResilienceAI:**
- Real-time Air Quality Index (AQI) for PM2.5, PM10, Ozone
- Wildfire smoke impact assessment
- Health vulnerability overlay for disaster response
- Forecast data for 3-6 days ahead

**Key Endpoints:**
- `/observation/latLong/?format=text/csv` - Current observations by lat/lon
- `/forecast/zipCode/?format=text/csv` - Forecasts by ZIP code
- `/forecast/latLong/?format=application/json` - Forecasts by coordinates

**Implementation Files:**
- Add to: `src/climate_client.py` or new `src/air_quality_client.py`
- Configuration: Add `AIRNOW_API_KEY` to `config.py`
- Feature engineering: Air quality features in `src/feature_engineering.py`

**Claude Code Instructions:**
```python
# Create AirNow client class
class AirNowClient:
    BASE_URL = "https://www.airnowapi.org/aq"
    
    def get_current_aqi(self, lat: float, lon: float) -> Dict:
        """Fetch current AQI for location."""
        
    def get_forecast_by_zip(self, zip_code: str) -> List[Dict]:
        """Get AQI forecast for ZIP code."""
```

---

### 1.2 EPA AQS API (Air Quality System)

| Attribute | Details |
|-----------|---------|
| **API Name** | EPA Air Quality System (AQS) API v2 |
| **Provider** | U.S. Environmental Protection Agency |
| **Endpoint URL** | `https://aqs.epa.gov/data/api/` |
| **Documentation** | https://aqs.epa.gov/aqsweb/documents/data_api.html |
| **Authentication** | Email + API Key (free registration) |
| **Rate Limits** | No explicit limit; 1 query per 2 minutes recommended for bulk |
| **Data Granularity** | Monitor-level, County, State, CBSA, Lat/Lon bounding box |
| **Update Frequency** | Hourly to Annual summaries |
| **Data Retention** | Historical data from 1980s to present |

**Integration Value for ResilienceAI:**
- Historical air quality data for vulnerability modeling
- Monitor-level granularity for precise health impact assessment
- Long-term exposure tracking for chronic disease correlation
- Quarterly and annual summaries for trend analysis

**Key Endpoints:**
- `/sampleData/byCounty` - Raw sample data by county
- `/dailyData/byState` - Daily summaries by state
- `/annualData/byCounty` - Annual summaries for trend analysis
- `/monitors/byCounty` - Monitor metadata and locations

**Implementation Files:**
- Add to: `src/climate_client.py`
- Feature engineering: Historical pollution exposure features
- New file: `src/air_quality_historical.py`

---

### 1.3 NOAA NWPS API (National Water Prediction Service)

| Attribute | Details |
|-----------|---------|
| **API Name** | NOAA National Water Prediction Service API |
| **Provider** | National Weather Service / NOAA |
| **Endpoint URL** | `https://api.water.noaa.gov/nwps/v1/` |
| **Documentation** | https://water.noaa.gov/about/api |
| **Authentication** | None required |
| **Rate Limits** | No explicit limits (fair use) |
| **Data Granularity** | River gauge locations (lat/lon), County-based aggregation |
| **Update Frequency** | 15-minute observations, hourly forecasts |
| **Data Retention** | Real-time + 10-day forecasts |

**Integration Value for ResilienceAI:**
- River stage and flow forecasts beyond current NWIS
- National Water Model output integration
- Flood inundation mapping support
- Hydrologic ensemble forecast (HEFS) data

**Key Endpoints:**
- `/gages` - List all river gages
- `/gages/{gageId}/observations` - Current and recent observations
- `/gages/{gageId}/forecast` - Official NWS streamflow forecasts
- `/gages/{gageId}/nwm/forecast` - National Water Model forecasts

**Implementation Files:**
- Extend: `src/climate_client.py` (add to existing hydrology methods)
- Dashboard: New flood forecast visualization tab

---

### 1.4 NASA SMAP L4 Soil Moisture (via Earth Engine / direct)

| Attribute | Details |
|-----------|---------|
| **API Name** | NASA SMAP Level-4 Soil Moisture |
| **Provider** | NASA GMAO / NSIDC |
| **Endpoint URL** | `https://gmao.gsfc.nasa.gov/gmao-products/smap-l4/` |
| **Access Methods** | NASA Earthdata, Google Earth Engine, OPeNDAP |
| **Documentation** | https://nsidc.org/data/spl4smgp |
| **Authentication** | NASA Earthdata Login (free) |
| **Rate Limits** | No API limits; bulk data access |
| **Data Granularity** | 9km grid, global coverage |
| **Update Frequency** | 3-hourly analysis updates |
| **Data Retention** | 2015-present (9+ years) |

**Integration Value for ResilienceAI:**
- Root zone soil moisture (0-100cm) for drought assessment
- Surface soil moisture for flood potential estimation
- Agricultural drought impact modeling
- Wildfire risk assessment (dry soil conditions)

**Key Variables:**
- `sm_surface` - Surface soil moisture (0-5cm)
- `sm_rootzone` - Root zone soil moisture (0-100cm)
- `sm_profile` - Full profile soil moisture
- `land_evapotranspiration_flux` - ET for water balance

**Implementation Files:**
- Add to: `src/climate_client.py` or `src/geospatial/earth_engine_client.py`
- Requires: Google Earth Engine Python API or direct HDF5 processing

---

## 2. Public Health Data APIs

### 2.1 CDC WONDER API

| Attribute | Details |
|-----------|---------|
| **API Name** | CDC WONDER API for Data Query Web Service |
| **Provider** | Centers for Disease Control and Prevention |
| **Endpoint URL** | `https://wonder.cdc.gov/controller/datarequest/{database}` |
| **Documentation** | https://wonder.cdc.gov/wonder/help/wonder-api.html |
| **Authentication** | None required |
| **Rate Limits** | 1 query per 2 minutes recommended |
| **Data Granularity** | National (API restricted from county-level for vital stats) |
| **Update Frequency** | Annual for most datasets, Monthly for provisional mortality |
| **Data Retention** | 1968-present (varies by dataset) |

**Integration Value for ResilienceAI:**
- Disease surveillance data (National level)
- Mortality statistics by cause
- Birth and natality statistics
- Cancer incidence and mortality
- Emergency department visit patterns

**Available Databases:**
- D76: Detailed Mortality (1999-2023)
- D27: Natality (Births)
- D14: Cancer Statistics
- D122: Provisional Mortality

**Implementation Files:**
- New file: `src/health_clients/cdc_wonder_client.py`
- Note: Geographic restrictions apply - national data only via API

**Important Limitation:** 
> "Only national data are available for query by the API. Queries for mortality and births statistics from the National Vital Statistics System cannot limit or group results by any location field, such as Region, Division, State or County."

---

### 2.2 SAMHSA FindTreatment.gov API

| Attribute | Details |
|-----------|---------|
| **API Name** | SAMHSA FindTreatment.gov Facility Locator API |
| **Provider** | Substance Abuse and Mental Health Services Administration |
| **Endpoint URL** | `https://findtreatment.gov/api/` (internal API) |
| **Documentation** | https://findtreatment.gov/assets/FindTreatment-Developer-Guide.pdf |
| **Authentication** | API Key required (contact SAMHSA) |
| **Rate Limits** | Not publicly specified |
| **Data Granularity** | Facility-level (can aggregate to county) |
| **Update Frequency** | Weekly updates |
| **Data Retention** | Current facilities only |

**Integration Value for ResilienceAI:**
- Mental health and substance abuse treatment facility locations
- Post-disaster behavioral health resource mapping
- Vulnerability indicator (areas with limited treatment access)
- Emergency response planning for behavioral health crises

**Alternative Access:**
- Data.gov Dataset: https://catalog.data.gov/dataset/substance-abuse-treatment-facilities-locator
- Direct download of facility data available

**Implementation Files:**
- New file: `src/health_clients/samhsa_client.py`
- Integration: Add to vulnerability assessment features

---

### 2.3 EPA EJSCREEN API

| Attribute | Details |
|-----------|---------|
| **API Name** | EPA EJSCREEN (Environmental Justice Screening and Mapping) |
| **Provider** | U.S. Environmental Protection Agency |
| **Endpoint URL** | `https://geopub.epa.gov/arcgis/rest/services/ejscreen/` |
| **Documentation** | https://www.epa.gov/ejscreen |
| **Authentication** | None required for REST services |
| **Rate Limits** | Standard ArcGIS Server limits |
| **Data Granularity** | Census Block Group, Census Tract |
| **Update Frequency** | Annual (updated with new ACS data) |
| **Data Retention** | 2015-present |

**Integration Value for ResilienceAI:**
- Environmental justice vulnerability indicators
- 11 environmental indicators (PM2.5, ozone, traffic proximity, etc.)
- 6 demographic indicators (low income, minority population, etc.)
- EJ Index combining environmental and demographic factors

**Key Services:**
- `/ejscreen_mapserver/MapServer` - Map service
- `/ejscreen_geo/` - Geoprocessing service
- Data download: https://gaftp.epa.gov/EJScreen/

**Key Variables:**
- `PM25` - Particulate Matter 2.5
- `OZONE` - Ozone concentration
- `DSLPM` - Diesel particulate matter
- `CANCER` - Cancer risk from inhalation
- `RESP` - Respiratory hazard index
- `PTRAF` - Traffic proximity
- `PNPL` - Superfund proximity

**Implementation Files:**
- New file: `src/environmental_clients/ejscreen_client.py`
- Feature engineering: Add EJ indices to vulnerability model

---

## 3. Infrastructure & Utilities APIs

### 3.1 PowerOutage.us API

| Attribute | Details |
|-----------|---------|
| **API Name** | PowerOutage.us Live Outage REST API |
| **Provider** | PowerOutage.us (private aggregator) |
| **Endpoint URL** | `https://poweroutage.us/api/` (requires enterprise access) |
| **Documentation** | https://poweroutage.us/use-our-data |
| **Authentication** | API Key required |
| **Rate Limits** | 10-minute refresh cycles |
| **Data Granularity** | County-level, Utility-level, State-level |
| **Update Frequency** | Every 10 minutes |
| **Data Retention** | 8+ years historical (since 2017) |

**Integration Value for ResilienceAI:**
- Real-time power outage tracking at county level
- Historical outage data for infrastructure vulnerability modeling
- Storm impact assessment
- Critical facility backup power need estimation

**Coverage:**
- USA: 154M+ customers tracked (96% coverage)
- 978+ utilities monitored

**Access Note:**
> Free tier available for limited use. Enterprise access required for full API. Contact info@poweroutage.us for access.

**Implementation Files:**
- New file: `src/infrastructure_clients/power_outage_client.py`
- Dashboard: Real-time outage map overlay

---

### 3.2 FCC National Broadband Map API

| Attribute | Details |
|-----------|---------|
| **API Name** | FCC Broadband Data Collection (BDC) Public Data API |
| **Provider** | Federal Communications Commission |
| **Endpoint URL** | `https://broadbandmap.fcc.gov/api/public/map/` |
| **Documentation** | https://www.fcc.gov/sites/default/files/bdc-public-data-api-spec.pdf |
| **Authentication** | Username + Hash Value (free registration) |
| **Rate Limits** | Not specified |
| **Data Granularity** | Location (address), Block, County, State |
| **Update Frequency** | Semi-annual (twice per year) |
| **Data Retention** | 2022-present (newer BDC data) |

**Integration Value for ResilienceAI:**
- Broadband availability for telehealth access assessment
- Digital divide indicators for vulnerability modeling
- Infrastructure resilience (communication redundancy)
- Remote work capability during disasters

**Key Endpoints:**
- `/listAsOfDates` - Available data versions
- `/broadband/providers` - Providers by location
- `/broadband/technologies` - Technology availability

**Implementation Files:**
- New file: `src/infrastructure_clients/fcc_broadband_client.py`
- Feature engineering: Digital access vulnerability indicators

---

### 3.3 OpenCellID / Mozilla Location Service (MLS)

| Attribute | Details |
|-----------|---------|
| **API Name** | OpenCellID API / Mozilla Location Service |
| **Provider** | Unwired Labs / Mozilla |
| **Endpoint URL** | `https://opencellid.org/api/` |
| **Documentation** | https://opencellid.org/ |
| **Authentication** | API Key (free tier available) |
| **Rate Limits** | Free: 100 requests/day; Paid tiers available |
| **Data Granularity** | Cell tower locations (lat/lon), can aggregate to county |
| **Update Frequency** | Continuous (crowdsourced) |
| **Data Retention** | Historical coverage since 2008 |

**Integration Value for ResilienceAI:**
- Cellular infrastructure density mapping
- Communication resilience assessment
- Population displacement tracking (anonymized cell tower activity)
- Emergency communication capability estimation

**Key Endpoints:**
- `/cell/get` - Get cell tower information
- `/cell/getInArea` - Get cells in geographic area
- `/measure/add` - Contribute measurements (optional)

**Implementation Files:**
- New file: `src/infrastructure_clients/cell_tower_client.py`
- Note: Consider as secondary data source due to rate limits

---

## 4. Socioeconomic Enhancement APIs

### 4.1 USDA Food Access Research Atlas API

| Attribute | Details |
|-----------|---------|
| **API Name** | USDA Food Access Research Atlas (FARA) |
| **Provider** | USDA Economic Research Service |
| **Endpoint URL** | `https://www.ers.usda.gov/data-products/food-access-research-atlas/` |
| **GIS Services** | https://gis.ers.usda.gov/arcgis/rest/services/
| **Documentation** | https://www.ers.usda.gov/data-products/food-access-research-atlas/documentation/ |
| **Authentication** | None required |
| **Rate Limits** | Standard ArcGIS Server limits |
| **Data Granularity** | Census Tract |
| **Update Frequency** | Annual (2019 data most recent) |
| **Data Retention** | 2010, 2015, 2019 versions |

**Integration Value for ResilienceAI:**
- Food desert identification
- Food insecurity vulnerability assessment
- Post-disaster food access disruption modeling
- SNAP-authorized retailer locations

**Key Variables:**
- `LILATracts_1And10` - Low income & low access (>1 mile from supermarket)
- `LILATracts_1And20` - Low income & low access (>20 miles for rural)
- `food_taxcredit` - Food tax credit areas
- `lapop1_10` - Population count low access

**Implementation Files:**
- New file: `src/socioeconomic_clients/usda_food_access_client.py`
- Feature engineering: Food security vulnerability indicators

---

### 4.2 HUD Location Affordability Index

| Attribute | Details |
|-----------|---------|
| **API Name** | HUD Location Affordability Index (LAI) |
| **Provider** | U.S. Department of Housing and Urban Development |
| **Endpoint URL** | https://hudgis-hud.opendata.arcgis.com/datasets/c1c32742599a42c9a45c95be50ed2ab6_12/about |
| **Documentation** | https://www.hudexchange.info/programs/location-affordability-index/ |
| **Authentication** | None required |
| **Rate Limits** | ArcGIS Online limits |
| **Data Granularity** | Census Block Group |
| **Update Frequency** | Version 3.0 (2012-2016 ACS data) |
| **Data Retention** | Historical versions available |

**Integration Value for ResilienceAI:**
- Housing cost burden indicators
- Transportation cost vulnerability
- Combined housing + transportation affordability
- Economic resilience assessment

**Key Variables:**
- `h_am_own` - Annual housing cost (owner)
- `h_am_rent` - Annual housing cost (renter)
- `t_am_own` - Annual transportation cost (owner)
- `t_am_rent` - Annual transportation cost (renter)
- `ht_am_own` - Combined housing + transport cost

**Implementation Files:**
- New file: `src/socioeconomic_clients/hud_affordability_client.py`
- Feature engineering: Economic vulnerability indicators

---

### 4.3 EPA Smart Location Database

| Attribute | Details |
|-----------|---------|
| **API Name** | EPA Smart Location Database (SLD) |
| **Provider** | U.S. Environmental Protection Agency |
| **Endpoint URL** | https://www.epa.gov/smartgrowth/smart-location-mapping |
| **Documentation** | https://www.epa.gov/system/files/documents/2023-10/epa_sld_3.0_technicaldocumentationuserguide_may2021_0.pdf |
| **Authentication** | None required |
| **Rate Limits** | Download-based (no API limits) |
| **Data Granularity** | Census Block Group (90+ attributes) |
| **Update Frequency** | Version 3.0 (2021 release) |
| **Data Retention** | 2013-2021 |

**Integration Value for ResilienceAI:**
- Walkability scores for evacuation feasibility
- Transit access for carless population vulnerability
- Employment accessibility for economic resilience
- Street network design for emergency access

**Key Variables:**
- `D3B` - Street intersection density
- `D4a` - Transit frequency (where available)
- `D2a_EpHHm` - Employment + housing mix
- `D5ar` - Jobs within 45-minute transit commute
- `D5br` - Jobs within 45-minute auto commute

**Related Dataset:**
- National Walkability Index derived from SLD

**Implementation Files:**
- New file: `src/socioeconomic_clients/epa_smart_location_client.py`
- Feature engineering: Built environment vulnerability indicators

---

## 5. Real-time Hazard APIs

### 5.1 NWS Weather API (Enhanced Usage)

| Attribute | Details |
|-----------|---------|
| **API Name** | National Weather Service API |
| **Provider** | NOAA / National Weather Service |
| **Endpoint URL** | `https://api.weather.gov/` |
| **Documentation** | https://www.weather.gov/documentation/services-web-api |
| **Authentication** | User-Agent header required (no API key) |
| **Rate Limits** | Generous; retry after 5 seconds if exceeded |
| **Data Granularity** | 2.5km grid, County, Zone |
| **Update Frequency** | Hourly forecasts, Real-time alerts |
| **Data Retention** | 7-day forecasts, 7-day alert archive |

**Integration Value for ResilienceAI:**
- Severe weather alerts with GeoJSON polygons
- High-resolution gridded forecasts (2.5km)
- 7-day hourly forecasts
- Storm-based polygon warnings (tornado, severe thunderstorm)

**Key Endpoints:**
- `/alerts/active` - All active alerts
- `/alerts/active?area={state}` - Alerts by state
- `/points/{lat},{lon}` - Grid forecast for location
- `/gridpoints/{office}/{gridX},{gridY}/forecast` - Detailed forecast

**Implementation Files:**
- Extend: `src/weather_client.py` (already exists, enhance with polygon alerts)
- Dashboard: Add storm polygon visualization

**Claude Code Instructions:**
```python
# Enhance existing weather client with polygon support
def get_alerts_with_geometry(self, state: str) -> List[Dict]:
    """Fetch active alerts with GeoJSON polygons."""
    url = f"{self.base_url}/alerts/active?area={state}"
    headers = {"Accept": "application/geo+json"}
    # Parse and return alerts with geometry
```

---

### 5.2 USGS Earthquake GeoJSON Feed

| Attribute | Details |
|-----------|---------|
| **API Name** | USGS Earthquake Catalog API / GeoJSON Feeds |
| **Provider** | U.S. Geological Survey |
| **Endpoint URL** | `https://earthquake.usgs.gov/fdsnws/event/1/` (API)  
`https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/` (Feeds) |
| **Documentation** | https://earthquake.usgs.gov/fdsnws/event/1/ |
| **Authentication** | None required |
| **Rate Limits** | No explicit limits for feeds; 20,000 limit for API queries |
| **Data Granularity** | Event-level (lat/lon depth), aggregate by county |
| **Update Frequency** | Real-time (minute delay typical) |
| **Data Retention** | Real-time feeds + historical API (historical data available) |

**Integration Value for ResilienceAI:**
- Real-time earthquake notifications
- Seismic hazard assessment
- ShakeMap integration for impact estimation
- Historical seismicity for risk modeling

**Feed Types:**
- `significant_month.geojson` - Significant earthquakes
- `all_day.geojson` - All earthquakes past day
- `all_week.geojson` - All earthquakes past week

**API Parameters:**
- `format=geojson` - GeoJSON output
- `minmagnitude` - Minimum magnitude filter
- `latitude`/`longitude`/`maxradiuskm` - Location-based search

**Implementation Files:**
- Extend: `src/climate_client.py` or new `src/hazard_clients/earthquake_client.py`
- Dashboard: Real-time earthquake map

---

## 6. Implementation Roadmap

### Phase 1: High-Impact, Easy Integration (Months 1-2)

| Priority | API | Effort | Impact |
|----------|-----|--------|--------|
| 1 | EPA AirNow API | Low | High - Air quality for health vulnerability |
| 2 | NWS Weather API (enhanced) | Low | High - Severe weather polygons |
| 3 | USGS Earthquake Feed | Low | Medium - Real-time seismic hazard |
| 4 | NOAA NWPS | Medium | High - Flood forecasting enhancement |

### Phase 2: Socioeconomic Vulnerability (Months 2-3)

| Priority | API | Effort | Impact |
|----------|-----|--------|--------|
| 5 | EPA EJSCREEN | Medium | High - Environmental justice indicators |
| 6 | USDA Food Access Atlas | Medium | High - Food security vulnerability |
| 7 | EPA Smart Location Database | Medium | Medium - Walkability/transit access |
| 8 | HUD Location Affordability | Low | Medium - Housing burden indicators |

### Phase 3: Infrastructure & Health (Months 3-4)

| Priority | API | Effort | Impact |
|----------|-----|--------|--------|
| 9 | PowerOutage.us | Medium | High - Real-time utility status |
| 10 | FCC Broadband Map | Medium | Medium - Digital divide assessment |
| 11 | CDC WONDER | Medium | Medium - Disease surveillance |
| 12 | NASA SMAP | High | Medium - Soil moisture for drought |

### Phase 4: Specialized Data (Months 4-5)

| Priority | API | Effort | Impact |
|----------|-----|--------|--------|
| 13 | EPA AQS Historical | Medium | Low - Historical air quality trends |
| 14 | SAMHSA Treatment Locator | Medium | Low - Behavioral health resources |
| 15 | OpenCellID | Low | Low - Cell tower infrastructure |

---

## Configuration Updates Required

Add to `config.py`:

```python
# New API Configurations
API_KEYS = {
    'CENSUS_API_KEY': os.getenv('CENSUS_API_KEY'),
    'AIRNOW_API_KEY': os.getenv('AIRNOW_API_KEY'),
    'EPA_AQS_EMAIL': os.getenv('EPA_AQS_EMAIL'),
    'EPA_AQS_KEY': os.getenv('EPA_AQS_KEY'),
    'POWEROUTAGE_API_KEY': os.getenv('POWEROUTAGE_API_KEY'),
    'FCC_BROADBAND_USER': os.getenv('FCC_BROADBAND_USER'),
    'FCC_BROADBAND_HASH': os.getenv('FCC_BROADBAND_HASH'),
}

# New Data Source URLs
DATA_SOURCES.update({
    'airnow': 'https://www.airnowapi.org/aq',
    'epa_aqs': 'https://aqs.epa.gov/data/api',
    'noaa_nwps': 'https://api.water.noaa.gov/nwps/v1',
    'nws_api': 'https://api.weather.gov',
    'usgs_earthquake': 'https://earthquake.usgs.gov/fdsnws/event/1',
    'usgs_geojson_feed': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary',
    'ejscreen': 'https://geopub.epa.gov/arcgis/rest/services/ejscreen',
    'usda_fara': 'https://www.ers.usda.gov/data-products/food-access-research-atlas',
    'hud_lai': 'https://hudgis-hud.opendata.arcgis.com/datasets/c1c32742599a42c9a45c95be50ed2ab6_12',
    'epa_sld': 'https://edg.epa.gov/EPADataCommons/public/OA/WalkabilityIndex.zip',
})
```

---

## API Credentials Summary

| API | Credential Type | How to Obtain | Cost |
|-----|-----------------|---------------|------|
| EPA AirNow | API Key | https://www.airnowapi.org/login | Free |
| EPA AQS | Email + Key | https://aqs.epa.gov/aqsweb/documents/data_api.html | Free |
| PowerOutage.us | API Key | Contact info@poweroutage.us | Free tier available |
| FCC Broadband | User + Hash | https://broadbandmap.fcc.gov/account | Free |
| NASA Earthdata | Login | https://urs.earthdata.nasa.gov/ | Free |
| All Others | None | N/A | Free |

---

## Conclusion

This research identifies 15 high-value APIs that can significantly enhance ResilienceAI's capabilities across climate monitoring, public health assessment, infrastructure tracking, socioeconomic vulnerability analysis, and real-time hazard detection. The recommended implementation roadmap prioritizes APIs based on integration effort and potential impact, with Phase 1 APIs offering immediate high-value enhancements with minimal development effort.

---

*Document generated for ResilienceAI - MUIDSI Hackathon 2026*
*Research completed: February 17, 2026*
