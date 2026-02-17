# Maximum-Resolution Climatological Trend Analysis for ResilienceAI

## Executive Summary

This analysis identifies the highest-resolution climatological trend analysis achievable using exclusively open-source data. The finest achievable spatial resolution is **30 meters** for temperature (Landsat thermal) and **800 meters** for gridded climate normals (PRISM). The deepest temporal records extend **130 years** (PRISM monthly data from 1895-present). The "wow" insight emerges from constructing a **Compound Climate Vulnerability Index (CCVI)** at 1km resolution that fuses 130 years of climate trends with real-time infrastructure and socioeconomic vulnerability layers—revealing previously invisible "risk archipelagos" where multiple hazards converge on vulnerable populations.

---

## 1. Highest-Resolution Climate Data Available

### 1.1 Precipitation Data

| Dataset | Spatial Resolution | Temporal Resolution | Coverage | Historical Depth | Source |
|---------|-------------------|---------------------|----------|------------------|--------|
| **PRISM** | 800m (4km available) | Daily, Monthly, Annual | Conterminous US | 1895-present (130 years) | Oregon State |
| **Daymet** | 1km | Daily | North America, Hawaii, Puerto Rico | 1980-present (45 years) | ORNL DAAC |
| **CHIRPS** | 0.05° (~5km) | Daily, Pentad, Monthly | 50°S-50°N global | 1981-present (44 years) | UCSB Climate Hazards Center |
| **NOAA NClimGrid** | ~5km | Daily, Monthly | Conterminous US | 1950-present (75 years) | NOAA NCEI |
| **PERSIANN-CDR** | 0.25° (~25km) | Daily | Quasi-global | 1982-present (43 years) | NOAA |

**Best for High-Resolution Analysis:**
- **PRISM (800m)** - Gold standard for US climatological analysis with 130-year record
- **Daymet (1km)** - Best for daily-scale processes and North America coverage
- **CHIRPS (5km)** - Best for global precipitation trend analysis

### 1.2 Temperature Data

| Dataset | Spatial Resolution | Temporal Resolution | Coverage | Historical Depth | Source |
|---------|-------------------|---------------------|----------|------------------|--------|
| **Landsat LST** | 30m | 16-day revisit | Global | 1984-present (41 years) | USGS/NASA |
| **MODIS LST** | 1km | Daily (day/night) | Global | 2000-present (25 years) | NASA LP DAAC |
| **PRISM** | 800m | Daily, Monthly, Annual | Conterminous US | 1895-present (130 years) | Oregon State |
| **Daymet** | 1km | Daily | North America | 1980-present (45 years) | ORNL DAAC |
| **ERA5** | 0.25° (~31km) | Hourly | Global | 1940-present (85 years) | ECMWF |
| **WorldClim** | 1km (30 arc-sec) | Monthly | Global | 1970-2000 baseline + future | WorldClim.org |

**Best for High-Resolution Analysis:**
- **Landsat LST (30m)** - Unmatched spatial resolution for urban heat island and microclimate analysis
- **PRISM (800m)** - Longest historical record for climatological trends
- **MODIS LST (1km)** - Best temporal resolution for daily temperature extremes

### 1.3 Emerging Ultra-High Resolution Sources

| Dataset | Resolution | Application | Status |
|---------|------------|-------------|--------|
| **ECOSTRESS** | 30-60m | Land surface temperature, evapotranspiration | 2018-present |
| **Sentinel-3 SLSTR** | 1km | Sea and land surface temperature | Operational |
| **GOES-R LST** | 2km | Continental US, 5-min updates | Operational |
| **ASTER GDEM** | 30m | Topographic correction for climate | Static |
| **SRTM** | 30m (1 arc-sec) | Elevation for lapse rate corrections | Static |

---

## 2. Composite Climatological Risk Construction

### 2.1 Risk Framework

```
Composite Climate Risk = f(Hazard × Exposure × Vulnerability)
```

### 2.2 Component Layers

#### A. Precipitation Trends (Flood & Drought)

**Indicators:**
1. **Extreme Precipitation Index (EPI)**
   - 95th percentile daily precipitation trend
   - Mann-Kendall trend significance
   - Theil-Sen slope magnitude

2. **Standardized Precipitation Index (SPI)**
   - Multiple timescales: 1, 3, 6, 12, 24 months
   - Drought frequency and duration trends
   - Derived from PRISM/Daymet at native resolution

3. **Standardized Precipitation Evapotranspiration Index (SPEI)**
   - Incorporates temperature-driven evaporative demand
   - Better for climate change context
   - High-resolution implementations available (5km, 1km)

4. **Consecutive Dry Days (CDD)**
   - Maximum dry spell duration trend
   - Agricultural drought relevance

**Data Fusion Approach:**
```python
# Conceptual workflow
PRISM (800m) + Daymet (1km) → Harmonized to 1km → 
Trend Analysis (Mann-Kendall) → Flood/Drought Risk Surfaces
```

#### B. Temperature Trends (Heat & Cold)

**Indicators:**
1. **Heat Wave Magnitude Index (HWMI)**
   - Frequency, duration, intensity trends
   - Derived from daily maximum temperature

2. **Cooling Degree Days (CDD) / Heating Degree Days (HDD)**
   - Energy demand implications
   - Threshold-based accumulation

3. **Land Surface Temperature Trends**
   - Landsat 30m for urban heat island analysis
   - MODIS 1km for regional trends
   - Urban-rural differential analysis

4. **Cold Snap Intensity**
   - Minimum temperature extremes
   - Growing season length trends

#### C. Infrastructure Vulnerability

**HIFLD (Homeland Infrastructure Foundation-Level Data):**

| Layer | Type | Resolution | Attributes |
|-------|------|------------|------------|
| Electric Transmission Lines | Vector | Line geometry | Voltage, owner, status |
| Power Plants | Point | Exact location | Capacity, fuel type, age |
| Substations | Point | Exact location | Voltage, transformer count |
| Hospitals | Point | Address-level | Bed count, trauma level |
| Emergency Services | Point | Address-level | Type, response time |
| Transportation | Vector | Road/rail network | Class, traffic volume |
| Water Treatment | Point | Facility location | Capacity, source type |

**Vulnerability Scoring:**
```python
Infrastructure_Vulnerability = Σ(Asset_Value × Criticality × Age_Factor × Redundancy)
```

**Grid Vulnerability Specifics:**
- Transformer aging curves
- Vegetation encroachment risk
- Flood zone intersection analysis
- Heat derating factors for transmission lines

#### D. Socioeconomic Factors

**CDC Social Vulnerability Index (SVI):**

| Theme | Variables | Data Source |
|-------|-----------|-------------|
| Socioeconomic Status | Poverty, unemployment, income, education | ACS 5-year estimates |
| Household Composition | Age 65+, age 17-, disability, single-parent | ACS 5-year estimates |
| Minority Status | Race/ethnicity, limited English | ACS 5-year estimates |
| Housing/Transportation | Multi-unit structures, mobile homes, crowding, no vehicle | ACS 5-year estimates |

**Resolution:** Census tract (optimal), county (available)

**Additional Socioeconomic Layers:**
1. **CDC Environmental Justice Index (EJI)**
2. **FEMA National Risk Index**
3. **USDA Food Access Research Atlas**
4. **HUD Location Affordability Index**

---

## 3. Trend Analysis Methodologies

### 3.1 Mann-Kendall Trend Test

**Purpose:** Non-parametric test for monotonic trends in time series

**Advantages:**
- No assumption of normality
- Robust to outliers
- Suitable for censored data
- Works with missing values

**Implementation:**
```python
import pymannkendall as mk

# For gridded data
result = mk.original_test(time_series, alpha=0.05)
# Returns: trend (increasing/decreasing/no trend), 
#          p-value, Kendall's tau, slope
```

**Variants:**
- **Original Mann-Kendall:** Standard test
- **Seasonal MK:** Accounts for seasonal cycles
- **Hamed-Rao Modified MK:** Accounts for autocorrelation
- **Multivariate MK:** Multiple stations/variables
- **Regional MK:** Regional trend assessment

### 3.2 Theil-Sen Slope Estimator

**Purpose:** Robust non-parametric slope estimation

**Advantages:**
- Median of all pairwise slopes
- Insensitive to outliers
- ~90% efficiency vs OLS for normal data
- Better for skewed distributions

**Implementation:**
```python
from scipy import stats

slope, intercept, lo, hi = stats.theilslopes(y, x, 0.95)
```

**Interpretation:**
- Slope magnitude indicates rate of change
- Confidence intervals indicate uncertainty
- Combined with MK p-value for significance

### 3.3 Change Point Detection

**Methods:**

| Method | Best For | Sensitivity |
|--------|----------|-------------|
| **Pettitt Test** | Single change point | Middle of series |
| **Standard Normal Homogeneity Test (SNHT)** | Single/multiple | Beginning/end |
| **Buishand Range Test** | Single change point | Middle of series |
| **Binary Segmentation** | Multiple change points | Iterative detection |
| **PELT (Pruned Exact Linear Time)** | Multiple change points | Computationally efficient |

**Implementation:**
```python
import pyhomogeneity as hg

# Pettitt test
result = hg.pettitt_test(time_series, alpha=0.05)

# Buishand test
result = hg.buishand_range_test(time_series, alpha=0.05)
```

**Applications:**
- Detecting climate regime shifts
- Instrument change detection
- Urbanization impact assessment
- Policy intervention evaluation

### 3.4 Advanced Trend Techniques

**1. Ensemble Trend Analysis:**
- Multiple datasets (PRISM + Daymet + CHIRPS)
- Consensus mapping
- Uncertainty quantification

**2. Spatially Varying Trends:**
- Geographically Weighted Regression (GWR)
- Local trend surfaces
- Spatial autocorrelation consideration

**3. Extreme Value Analysis:**
- Generalized Extreme Value (GEV) distribution
- Peak Over Threshold (POT) methods
- Return period estimation

---

## 4. Downscaling Techniques

### 4.1 Statistical Downscaling

#### Bias Correction Spatial Disaggregation (BCSD)

**Process:**
1. Bias correction of GCM output against observations
2. Spatial disaggregation using high-res climatology
3. Preserves spatial patterns from observations

**Resolution:** Typically 1km from 25-100km GCMs

**Strengths:** Computationally efficient, preserves observed spatial variability

#### Localized Constructed Analogs (LOCA)

**Process:**
1. Find historical analog days matching GCM patterns
2. Construct weighted combination of analogs
3. Apply to high-resolution historical data

**Resolution:** 6km (native), can be further downscaled

**Strengths:** Better extreme event representation, physical consistency

**Availability:** LOCA2 (CMIP6) for US, 1950-2100

### 4.2 Dynamical Downscaling

**Regional Climate Models (RCMs):**
- WRF (Weather Research and Forecasting)
- RegCM
- CCLM

**Resolution:** 3-50km typical

**Strengths:** Physical process representation, internal consistency

**Limitations:** Computational expense, boundary condition dependency

### 4.3 Machine Learning Downscaling

**Deep Learning Approaches:**

| Method | Architecture | Resolution Gain | Status |
|--------|--------------|-----------------|--------|
| **Super-Resolution CNN** | ResNet, U-Net | 10-25x | Research |
| **Generative Adversarial Networks (GAN)** | SRGAN, ESRGAN | 4-16x | Emerging |
| **Transformers** | Vision Transformers | Variable | Cutting-edge |
| **Physics-Informed Neural Networks** | PINNs | Variable | Research |

**Open Source Implementations:**
- `climate-learn`: PyTorch-based climate ML
- `climdex`: Climate indices calculation
- Google Earth Engine: Built-in downscaling tools

### 4.4 Downscaling Workflow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  ERA5/CMIP6     │     │  Statistical     │     │  High-Res       │
│  (25-100km)     │────▶│  Downscaling     │────▶│  (1-5km)        │
│                 │     │  (BCSD/LOCA)     │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  ML Super-Res    │
                        │  (Optional)      │
                        └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  30m-1km Final   │
                        │  Resolution      │
                        └──────────────────┘
```

---

## 5. Data Fusion Approaches

### 5.1 Resolution Harmonization

**Common Target Resolution: 1km**

| Source Data | Native Resolution | Harmonization Method |
|-------------|-------------------|---------------------|
| PRISM | 800m | Resampling (bilinear) |
| Daymet | 1km | Native |
| CHIRPS | 5km | Downscaling (bilinear + lapse rate) |
| Landsat LST | 30m | Aggregation (mean) or selective extraction |
| SVI | Census tract | Dasymetric mapping to 1km grid |
| HIFLD | Vector | Rasterization with attribute preservation |

### 5.2 Data Fusion Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CLIMATE DATA FUSION PIPELINE                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  PRISM       │  │  Daymet      │  │  CHIRPS      │              │
│  │  (800m)      │  │  (1km)       │  │  (5km)       │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│         └────────┬────────┴────────┬────────┘                       │
│                  ▼                 ▼                                │
│         ┌──────────────────────────────────┐                        │
│         │  ENSEMBLE PRECIPITATION (1km)    │                        │
│         │  - Weighted average              │                        │
│         │  - Uncertainty quantification    │                        │
│         └──────────────┬───────────────────┘                        │
│                        ▼                                            │
│  ┌──────────────┐  ┌──────────────────────┐  ┌──────────────┐      │
│  │  Landsat LST │  │  MODIS LST           │  │  PRISM Temp  │      │
│  │  (30m)       │  │  (1km)               │  │  (800m)      │      │
│  └──────┬───────┘  └──────────┬───────────┘  └──────┬───────┘      │
│         │                     │                     │               │
│         └────────────┬────────┴────────┬────────────┘               │
│                      ▼                 ▼                            │
│         ┌──────────────────────────────────┐                        │
│         │  ENSEMBLE TEMPERATURE (1km)      │                        │
│         │  - Urban heat island correction  │                        │
│         │  - Topographic adjustment        │                        │
│         └──────────────┬───────────────────┘                        │
│                        ▼                                            │
│         ┌──────────────────────────────────┐                        │
│         │  TREND ANALYSIS LAYER            │                        │
│         │  - Mann-Kendall significance     │                        │
│         │  - Theil-Sen slopes              │                        │
│         │  - Change point detection        │                        │
│         └──────────────┬───────────────────┘                        │
│                        ▼                                            │
│  ┌──────────────┐  ┌──────────────────────┐  ┌──────────────┐      │
│  │  HIFLD       │  │  SVI                 │  │  ACS/Census  │      │
│  │  Infrastructure│  │  (Census Tract)      │  │  Socioeconomic│     │
│  └──────┬───────┘  └──────────┬───────────┘  └──────┬───────┘      │
│         │                     │                     │               │
│         └────────────┬────────┴────────┬────────────┘               │
│                      ▼                 ▼                            │
│         ┌──────────────────────────────────┐                        │
│         │  VULNERABILITY LAYER (1km)       │                        │
│         │  - Dasymetric mapping            │                        │
│         │  - Infrastructure density        │                        │
│         │  - Population-weighted SVI       │                        │
│         └──────────────┬───────────────────┘                        │
│                        ▼                                            │
│         ┌──────────────────────────────────┐                        │
│         │  COMPOSITE RISK INDEX            │                        │
│         │  - Multi-hazard combination      │                        │
│         │  - Exposure-weighted vulnerability│                       │
│         │  - Temporal trend integration    │                        │
│         └──────────────────────────────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.3 Uncertainty Quantification

**Sources of Uncertainty:**
1. Measurement uncertainty (instrument precision)
2. Spatial representativeness
3. Temporal sampling
4. Model structural uncertainty
5. Downscaling artifacts

**Propagation Methods:**
- Ensemble spread analysis
- Monte Carlo simulation
- Bayesian hierarchical models
- Fuzzy logic approaches

---

## 6. Achievable Specifications

### 6.1 Spatial Resolution

| Component | Finest Achievable | Practical Target | Method |
|-----------|------------------|------------------|--------|
| Temperature trends | **30m** | 1km | Landsat LST aggregation |
| Precipitation trends | **800m** | 1km | PRISM/Daymet fusion |
| Drought indices | **1km** | 1km | SPEI from downscaled data |
| Infrastructure | **Vector** | 1km | Rasterization |
| Socioeconomic | **Census tract** | 1km | Dasymetric mapping |
| **Composite Index** | **1km** | 1km | Harmonized grid |

### 6.2 Temporal Depth

| Component | Maximum Available | Recommended Analysis | Notes |
|-----------|------------------|---------------------|-------|
| Temperature | 130 years (PRISM) | 50-70 years | Reliable instrument era |
| Precipitation | 130 years (PRISM) | 50-70 years | US only |
| Global precipitation | 44 years (CHIRPS) | 40 years | Satellite era |
| Land surface temp | 41 years (Landsat) | 20-30 years | Sparse temporal coverage |
| Infrastructure | Current snapshot | Current + projected | Limited historical data |
| Socioeconomic | 15 years (ACS) | 10 years | Intercensal estimates |

### 6.3 Temporal Resolution

| Analysis Type | Optimal Resolution | Data Sources |
|--------------|-------------------|--------------|
| Climate trends | Monthly/Annual | PRISM, Daymet |
| Extreme events | Daily | Daymet, CHIRPS |
| Heat waves | Daily | Daymet, MODIS |
| Drought monitoring | Weekly/Monthly | SPI/SPEI |
| Real-time monitoring | Daily | CHIRPS, MODIS |

---

## 7. Novel Composite Indices

### 7.1 Compound Climate Vulnerability Index (CCVI)

**Formula:**
```
CCVI = (Hazard_Trend × Exposure × SVI) / Adaptive_Capacity
```

**Components:**
1. **Multi-Hazard Trend Score** (0-1)
   - Flood trend (precipitation extremes)
   - Drought trend (SPI/SPEI)
   - Heat trend (LST/HWMI)
   - Cold trend (extreme minimum)

2. **Critical Infrastructure Exposure** (0-1)
   - Power grid density × vulnerability
   - Healthcare facility proximity
   - Transportation network criticality

3. **Social Vulnerability** (0-1)
   - CDC SVI themes
   - Age-adjusted vulnerability
   - Economic resilience factors

4. **Adaptive Capacity** (0-1)
   - Emergency response capacity
   - Economic resources
   - Institutional preparedness

### 7.2 Climate Resilience Gap Index (CRGI)

**Purpose:** Identify where climate trends outpace adaptive capacity

```
CRGI = Climate_Trend_Rate / Adaptive_Capacity_Growth_Rate
```

**Interpretation:**
- CRGI > 2: Critical resilience gap
- CRGI 1-2: Moderate gap
- CRGI < 1: Adequate resilience

### 7.3 Infrastructure Climate Stress Index (ICSI)

**Components:**
1. Thermal stress on power grid
2. Flood risk to substations
3. Wind/ice loading trends
4. Vegetation encroachment risk
5. Aging infrastructure exposure

### 7.4 Novel Insights Possible

**1. Risk Archipelago Mapping**
- Identify disconnected high-risk areas
- Prioritize resource allocation
- Network vulnerability analysis

**2. Trend Convergence Zones**
- Where multiple hazards intensify simultaneously
- Compound event probability mapping
- Cascading failure risk assessment

**3. Climate Gentrification Predictor**
- Where climate improvements may drive displacement
- Environmental justice implications
- Policy intervention targeting

**4. Infrastructure Investment Optimization**
- ROI analysis for climate adaptation
- Risk-reduction per dollar invested
- Priority ranking algorithms

---

## 8. The "Wow" Insight

### 8.1 Discovery Potential

**The Hidden Pattern:**
By fusing 130 years of climate trends at 800m resolution with real-time infrastructure and socioeconomic data, ResilienceAI can reveal **"climate risk archipelagos"**—clusters of census tracts where:

1. **Multiple hazards are accelerating simultaneously** (compound risk)
2. **Critical infrastructure is aging and exposed** (cascading failure potential)
3. **Populations are least able to adapt** (vulnerability concentration)
4. **No existing index captures the convergence** (analysis gap)

### 8.2 Specific Wow Insights

**1. The 30-Meter Urban Heat Divide**
Using Landsat LST at 30m resolution, identify individual neighborhoods where:
- Surface temperatures vary by 15-20°F within 1km
- Low-income housing correlates with highest heat exposure
- Tree canopy gaps align with vulnerable populations

**2. The 130-Year Precipitation Regime Shift**
Using PRISM data back to 1895, identify:
- Locations where "100-year" storms now occur every 20 years
- Previously safe areas now in flood zones
- Infrastructure designed for historical climate now inadequate

**3. The Infrastructure-Climate Mismatch**
Overlay HIFLD power grid data with climate trends to find:
- Substations in accelerating flood zones
- Transmission corridors with increasing heat derating
- Critical facilities with no redundancy in high-risk areas

**4. The Vulnerability-Time Bomb**
Combine SVI with climate projections to identify:
- Communities where aging populations meet intensifying heat
- Areas where poverty prevents adaptation to accelerating change
- Locations where multiple vulnerabilities compound

### 8.3 Competitive Differentiation

**What Doesn't Exist Elsewhere:**

| Capability | Existing Solutions | ResilienceAI Potential |
|------------|-------------------|----------------------|
| Resolution | 5-10km typical | **800m-1km operational, 30m for specific analyses** |
| Temporal depth | 30-50 years | **130 years for US, 40+ years global** |
| Integration | Single hazard focus | **Multi-hazard compound risk** |
| Infrastructure | Limited or proprietary | **Full HIFLD integration** |
| Socioeconomic | County-level | **Census tract with dasymetric refinement** |
| Trend analysis | Simple linear trends | **Mann-Kendall + change point detection** |
| Future projections | Generic scenarios | **Location-specific, downscaled CMIP6** |

---

## 9. Implementation Recommendations

### 9.1 Data Stack

**Core Climate Data:**
- PRISM (primary US analysis)
- Daymet (daily processes)
- CHIRPS (global coverage)
- Landsat LST (urban heat analysis)

**Infrastructure Data:**
- HIFLD Open (primary)
- OpenStreetMap (supplementary)
- EIA Form 860 (power plants)

**Socioeconomic Data:**
- CDC SVI (primary)
- US Census ACS (detailed demographics)
- HUD datasets (housing vulnerability)

### 9.2 Processing Infrastructure

**Recommended Stack:**
- **Storage:** Cloud-optimized GeoTIFFs (COG)
- **Processing:** Google Earth Engine + local Python
- **Database:** PostGIS for vector, Zarr for gridded
- **API:** FastAPI for data services
- **Visualization:** Leaflet/Mapbox with custom layers

### 9.3 Analysis Pipeline

```
1. Data Ingestion → Cloud-optimized formats
2. Quality Control → Homogeneity testing
3. Trend Analysis → Mann-Kendall + Theil-Sen
4. Change Detection → Pettitt/Buishand tests
5. Downscaling → BCSD/LOCA + ML enhancement
6. Fusion → Harmonized 1km grid
7. Index Construction → CCVI calculation
8. Validation → Cross-validation with events
9. Delivery → API + visualization
```

---

## 10. Conclusion

The maximum-resolution climatological trend analysis achievable with open-source data for ResilienceAI is:

- **Spatial:** 800m operational (PRISM), 30m for targeted thermal analysis (Landsat)
- **Temporal:** 130 years for US climate (1895-present), 40+ years globally
- **Composite:** Novel CCVI at 1km integrating climate, infrastructure, and socioeconomic factors
- **Methodological:** State-of-the-art non-parametric trend detection with uncertainty quantification

The "wow" insight emerges from the **convergence analysis**—revealing locations where accelerating climate hazards, aging infrastructure, and vulnerable populations intersect in ways no existing index captures. This creates actionable intelligence for:
- **Emergency managers:** Prioritizing limited resources
- **Infrastructure operators:** Targeting hardening investments
- **Policymakers:** Designing equitable adaptation strategies
- **Researchers:** Understanding compound climate risks

The technical foundation exists. The data is available. The methodology is proven. The differentiation is clear.

---

## Appendix A: Data Source URLs

| Dataset | URL | Access |
|---------|-----|--------|
| PRISM | https://prism.oregonstate.edu/ | Free, FTP/HTTP |
| Daymet | https://daymet.ornl.gov/ | Free, NASA Earthdata |
| CHIRPS | https://www.chc.ucsb.edu/data/chirps | Free, HTTP |
| Landsat | https://earthexplorer.usgs.gov/ | Free, USGS |
| MODIS | https://lpdaac.usgs.gov/ | Free, NASA |
| HIFLD | https://hifld-geoplatform.opendata.arcgis.com/ | Free, Open Data |
| CDC SVI | https://svi.cdc.gov/ | Free, Download |
| Census ACS | https://www.census.gov/programs-surveys/acs/ | Free, API/Download |
| ERA5 | https://cds.climate.copernicus.eu/ | Free, CDS |
| WorldClim | https://www.worldclim.org/ | Free, Download |

## Appendix B: Python Libraries

```python
# Climate data processing
import xarray        # NetCDF/gridded data
import rasterio      # Raster I/O
import rioxarray     # Raster xarray extension

# Trend analysis
import pymannkendall      # Mann-Kendall tests
import pyhomogeneity      # Change point detection
from scipy import stats   # Theil-Sen slope

# Geospatial
import geopandas     # Vector data
import xarray-spatial  # Raster analysis

# Downscaling
import climate-learn  # ML downscaling
import scikit-downscale  # Statistical downscaling

# Visualization
import matplotlib
import holoviews
import geoviews
```

---

*Document Version: 1.0*
*Date: 2026-02-17*
*Analysis for ResilienceAI Strategic Planning*
