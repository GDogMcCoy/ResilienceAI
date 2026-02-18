# ResilienceAI: Free API Comparison Quick Reference

**Quick comparison of 15 recommended free APIs for ResilienceAI expansion**

---

## At-a-Glance Matrix

| # | API Name | Provider | Auth | Rate Limit | Granularity | Update Freq | Effort | Impact |
|---|----------|----------|------|------------|-------------|-------------|--------|--------|
| 1 | **EPA AirNow** | EPA | API Key | 500/hr | ZIP/LatLon | Hourly | Low | 🔥 High |
| 2 | **EPA AQS** | EPA | Email+Key | ~1/2min | Monitor/County | Hourly-Annual | Medium | 🔥 High |
| 3 | **NOAA NWPS** | NOAA | None | Fair use | River Gauge | 15-min | Medium | 🔥 High |
| 4 | **NASA SMAP** | NASA | Earthdata | Bulk access | 9km grid | 3-hourly | High | Medium |
| 5 | **CDC WONDER** | CDC | None | ~1/2min | National only | Monthly-Annual | Medium | Medium |
| 6 | **SAMHSA Locator** | SAMHSA | API Key | Not specified | Facility | Weekly | Medium | Low |
| 7 | **EPA EJSCREEN** | EPA | None | ArcGIS limits | Block Group | Annual | Medium | 🔥 High |
| 8 | **PowerOutage.us** | Private | API Key | 10-min refresh | County | Real-time | Medium | 🔥 High |
| 9 | **FCC Broadband** | FCC | User+Hash | Not specified | Address/Block | Semi-annual | Medium | Medium |
| 10 | **OpenCellID** | Unwired | API Key | 100/day | Cell Tower | Real-time | Low | Low |
| 11 | **USDA Food Atlas** | USDA | None | ArcGIS limits | Census Tract | Annual | Medium | 🔥 High |
| 12 | **HUD LAI** | HUD | None | ArcGIS limits | Block Group | Versioned | Low | Medium |
| 13 | **EPA Smart Location** | EPA | None | Download | Block Group | Versioned | Medium | Medium |
| 14 | **NWS Enhanced** | NOAA | User-Agent | Generous | 2.5km grid | Real-time | Low | 🔥 High |
| 15 | **USGS Earthquake** | USGS | None | 20K/query | Event-level | Real-time | Low | Medium |

---

## By Category

### 🌡️ Climate & Weather (4 APIs)

| API | Primary Use | Key Data | Free Tier |
|-----|-------------|----------|-----------|
| EPA AirNow | Real-time AQI | PM2.5, Ozone, Forecasts | ✅ Unlimited |
| EPA AQS | Historical air quality | Monitor data, trends | ✅ Unlimited |
| NOAA NWPS | River forecasts | Streamflow, flood stage | ✅ Unlimited |
| NASA SMAP | Soil moisture | Drought/flood potential | ✅ Earthdata login |

### 🏥 Public Health (3 APIs)

| API | Primary Use | Key Data | Limitations |
|-----|-------------|----------|-------------|
| CDC WONDER | Disease surveillance | Mortality, births, cancer | National only via API |
| SAMHSA Locator | Treatment facilities | Mental health/SUD locations | Access by request |
| EPA EJSCREEN | Environmental justice | 11 env + 6 demo indicators | Block group level |

### 🏗️ Infrastructure (3 APIs)

| API | Primary Use | Key Data | Coverage |
|-----|-------------|----------|----------|
| PowerOutage.us | Power outages | County-level outages | 96% US coverage |
| FCC Broadband | Internet access | Provider availability | National |
| OpenCellID | Cell towers | Tower locations, coverage | Global |

### 👥 Socioeconomic (3 APIs)

| API | Primary Use | Key Data | Granularity |
|-----|-------------|----------|-------------|
| USDA Food Atlas | Food access | Food desert indicators | Census Tract |
| HUD LAI | Housing affordability | Housing + transport costs | Block Group |
| EPA Smart Location | Built environment | Walkability, transit access | Block Group |

### ⚠️ Real-time Hazards (2 APIs)

| API | Primary Use | Key Data | Format |
|-----|-------------|----------|--------|
| NWS Enhanced | Severe weather | Alerts with GeoJSON polygons | GeoJSON |
| USGS Earthquake | Seismic activity | Real-time earthquakes | GeoJSON |

---

## Implementation Priority Matrix

```
Impact
  │
  │  🔥 Phase 1: Quick Wins
  │     ┌─────────────┐
High│     │ AirNow      │  NWS Enhanced
  │     │ NWPS        │  PowerOutage.us
  │     └─────────────┘
  │
  │  🔥 Phase 2: Core Features
  │     ┌─────────────┐
Med │     │ EJSCREEN    │  Food Atlas
  │     │ HUD LAI     │  Broadband
  │     └─────────────┘
  │
  │  🔥 Phase 3: Enhancement
  │     ┌─────────────┐
Low │     │ SMAP        │  CDC WONDER
  │     │ AQS Hist    │  Cell Towers
  │     └─────────────┘
  │
  └──────────────────────────
      Low    Medium    High
              Effort
```

---

## Required Credentials Summary

```bash
# Add these to your .env file

# EPA AirNow
AIRNOW_API_KEY=your_airnow_key_here

# EPA AQS
EPA_AQS_EMAIL=your_email@example.com
EPA_AQS_KEY=your_aqs_key_here

# PowerOutage.us (contact for access)
POWEROUTAGE_API_KEY=your_key_here

# FCC Broadband
FCC_BROADBAND_USER=your_email@example.com
FCC_BROADBAND_HASH=your_hash_here

# NASA Earthdata
NASA_EARTHDATA_USER=your_username
NASA_EARTHDATA_PASS=your_password

# SAMHSA (contact for access)
SAMHSA_API_KEY=your_key_here
```

---

## Quick Implementation Checklist

### Phase 1: Week 1-2
- [ ] Register for AirNow API key
- [ ] Implement `AirNowClient` class
- [ ] Add AQI features to vulnerability model
- [ ] Enhance NWS client with polygon alerts
- [ ] Add earthquake feed to dashboard

### Phase 2: Week 3-4
- [ ] Register for PowerOutage.us API
- [ ] Implement outage tracking client
- [ ] Add EJSCREEN data integration
- [ ] Integrate Food Access Atlas

### Phase 3: Week 5-6
- [ ] Set up NASA Earthdata access
- [ ] Implement SMAP soil moisture client
- [ ] Add HUD affordability indicators
- [ ] Integrate broadband availability

### Phase 4: Week 7-8
- [ ] Add EPA AQS historical client
- [ ] Implement CDC WONDER integration
- [ ] Add cell tower data layer
- [ ] Final testing and documentation

---

## Feature Coverage by API

| Feature | APIs |
|---------|------|
| **Air Quality** | AirNow, AQS, EJSCREEN |
| **Water/Hydrology** | NWPS, SMAP |
| **Weather Alerts** | NWS Enhanced |
| **Seismic** | USGS Earthquake |
| **Power Infrastructure** | PowerOutage.us |
| **Communications** | FCC Broadband, OpenCellID |
| **Food Security** | USDA Food Atlas |
| **Housing** | HUD LAI |
| **Transportation** | EPA Smart Location |
| **Health Surveillance** | CDC WONDER |
| **Behavioral Health** | SAMHSA Locator |
| **Environmental Justice** | EJSCREEN |

---

*Quick reference guide for ResilienceAI API integrations*
