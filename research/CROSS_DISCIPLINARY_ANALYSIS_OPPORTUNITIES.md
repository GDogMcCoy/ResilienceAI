# Cross-Disciplinary Data Analysis Opportunities for ResilienceAI

**Research Report v1.0 | MUIDSI Hackathon 2026**

---

## Executive Summary

This report identifies 12 cross-disciplinary analysis methodologies that can enhance ResilienceAI's holistic risk assessment capabilities. Each methodology bridges climate science, public health, economics, and social vulnerability to provide more nuanced, actionable insights for disaster preparedness and response.

---

## Methodology 1: CDC SVI-Weighted Composite Vulnerability Index

### Concept Name
CDC/ATSDR Social Vulnerability Index Integration with Disaster Risk

### Current Gap
ResilienceAI's current vulnerability index uses simple min-max normalization of 4 demographic variables (elderly_pct, poverty_pct, disability_pct, uninsured_pct). It lacks the CDC SVI's sophisticated percentile-ranking methodology and 15-variable comprehensive framework across 4 themes.

### Implementation Approach

```python
# CDC SVI Methodology Implementation
def calculate_cdc_svi(df):
    """
    CDC SVI uses 15 census variables across 4 themes:
    
    Theme 1: Socioeconomic Status
    - Below poverty (B17001_002E/B17001_001E)
    - Unemployed (B23025_005E/B23025_003E)
    - Income (B19013_001E) - reverse scored
    - No high school diploma (B15003_002E/B15003_001E)
    
    Theme 2: Household Composition & Disability
    - Aged 65+ (B09020_001E/B01003_001E)
    - Aged 17 and younger (B09001_001E/B01003_001E)
    - Civilian with disability (B18101_001E/B01003_001E)
    - Single-parent households (B11012_003E+B11012_014E/B11012_001E)
    
    Theme 3: Minority Status & Language
    - Minority (non-white) (B03002_003E/B01003_001E) - reverse
    - Speaks English "less than well" (C16002_004E+C16002_007E+C16002_010E+C16002_013E/B16002_001E)
    
    Theme 4: Housing Type & Transportation
    - Multi-unit structures (B25024_003E+B25024_004E/B25024_001E)
    - Mobile homes (B25024_010E/B25024_001E)
    - Crowding (>1 person per room) (B25014_005E+B25014_006E+B25014_007E/B25014_001E)
    - No vehicle (B08201_002E/B08201_001E)
    - Group quarters (B26001_001E/B01003_001E)
    """
    
    # Step 1: Calculate percentiles for each variable (0-1 scale)
    # Step 2: Sum percentile ranks within each theme
    # Step 3: Calculate theme percentile ranking
    # Step 4: Sum all theme percentiles for overall SVI (0-1)
    # Step 5: Create percentile ranking (0-1 where 1 = most vulnerable)
    
    pass
```

1. **Percentile Ranking**: Rank each county for each variable (0 = lowest vulnerability, 1 = highest)
2. **Theme Aggregation**: Sum percentiles within each of 4 themes, then re-rank
3. **Overall SVI**: Sum all 4 theme rankings, percentile rank the result
4. **Disaster Risk Multiplier**: Multiply SVI × Expected Annual Loss for equity-weighted risk

### Required Data Sources
- **Census API**: Add 11 additional ACS variables beyond current 6
- **CDC SVI Database**: Download pre-calculated SVI (2022) for validation
- **API Endpoint**: `https://www.atsdr.cdc.gov/placeandhealth/svi/data_documentation_download.html`

### Expected Output
- `svi_score`: 0-1 overall vulnerability (1 = most vulnerable)
- `svi_theme_1` through `svi_theme_4`: Theme-specific scores
- `svi_percentile`: National percentile ranking
- `disaster_equity_index`: SVI × EAL (environmental justice weighted risk)

### Scientific Citations
- Flanagan et al. (2011). "A Social Vulnerability Index for Disaster Management." *International Journal of Environmental Research and Public Health*.
- ATSDR (2024). "CDC/ATSDR Social Vulnerability Index Documentation." Centers for Disease Control.

### Claude Code Instructions
```
Implement calculate_cdc_svi() in src/feature_engineering.py using percentile 
ranking (rank(pct=True)) not min-max normalization. Add to FEATURE_GROUPS['indices'].
Fetch additional Census variables: B23025_005E, B15003_002E, B09001_001E, 
B11012_003E, B03002_003E, C16002_004E, B25024_003E, B25024_010E, B25014_005E, 
B08201_002E, B26001_001E. Create SVI_THEME_COLUMNS constant.
```

---

## Methodology 2: FEMA NRI Expected Annual Loss Integration

### Concept Name
Expected Annual Loss (EAL) Hazard-Specific Risk Calculation

### Current Gap
ResilienceAI aggregates disaster counts but doesn't monetize risk using FEMA's EAL methodology, which calculates expected annual economic loss from 18 hazard types.

### Implementation Approach

```python
def calculate_eal_weighted_risk(df, nri_client):
    """
    EAL = Σ (Annual_Frequency × Consequence_Value) across all hazards
    
    FEMA NRI includes 18 hazards:
    - Meteorological: Avalanche, Cold Wave, Drought, Hail, Heat Wave, 
                      Hurricane, Ice Storm, Lightning, Strong Wind, 
                      Tornado, Winter Weather
    - Hydrological: Coastal Flooding, Riverine Flooding, Tsunami
    - Geological: Earthquake, Landslide, Volcanic Activity
    - Wildfire: Wildfire
    
    Risk Score = EAL_total × Social_Vulnerability / Community_Resilience
    """
    
    # For each county, fetch NRI data:
    # - {HAZARD}_EALT (Expected Annual Loss Total)
    # - {HAZARD}_RISKS (Risk Score)
    # - SOVI_SCORE (Social Vulnerability Index)
    # - RESL_SCORE (Community Resilience Score)
    
    # Calculate weighted composite
    # eal_weighted_risk = (EAL_total / 1e6) * (SOVI_SCORE / RESL_SCORE)
    
    pass
```

1. **Fetch NRI Data**: Integrate FEMANRIClient to get EAL for all 18 hazards
2. **Normalize EAL**: Log-transform due to high skewness (EAL ranges $0 - $500M+)
3. **Social Vulnerability Weighting**: Multiply EAL by SVI score
4. **Resilience Adjustment**: Divide by community resilience score
5. **Composite Risk Index**: Blend with existing risk_score

### Required Data Sources
- **FEMA NRI CSV**: ~50MB file with all 18 hazard EAL values
- **URL**: `https://www.fema.gov/about/reports-and-data/openfema/nri/v120/NRI_Table_Counties.zip`
- **Key Columns**: `STCOFIPS`, `EAL_VALT`, `EAL_RATNG`, `{HAZARD}_EALT`, `SOVI_SCORE`, `RESL_SCORE`

### Expected Output
- `eal_total`: Expected annual loss in dollars
- `eal_rating`: Very Low/Low/Moderate/High/Very High
- `dominant_hazard`: Hazard type with highest EAL contribution
- `eal_per_capita`: EAL normalized by population
- `nri_composite_risk`: SVI-adjusted, resilience-adjusted risk score

### Scientific Citations
- FEMA (2024). "National Risk Index Data Methodology and Hazards Overview." Federal Emergency Management Agency.
- National Risk Index Technical Documentation v1.20

### Claude Code Instructions
```
Extend FEMANRIClient.get_hazard_risk_profile() to return EAL-weighted metrics.
Add calculate_eal_features() in feature_engineering.py that joins NRI data.
Use log1p(EAL) for feature normalization due to extreme right skew.
Create dominant_hazard_classifier using argmax across 18 hazard columns.
```

---

## Methodology 3: Getis-Ord Gi* Hotspot Analysis with Time Slices

### Concept Name
Emerging Hot Spot Classification for Disaster Trend Analysis

### Current Gap
ResilienceAI has basic spatial autocorrelation (Moran's I) but lacks the Getis-Ord Gi* statistic for identifying statistically significant hot/cold spots and emerging trends.

### Implementation Approach

```python
def emerging_hotspot_analysis(df, date_col='declarationDate', 
                              value_col='disaster_count',
                              time_step='1Y', k_neighbors=8):
    """
    ArcGIS Emerging Hot Spot Classification Categories:
    
    Hot Spots:
    - New Hot Spot: Significant hotspot in final time step only
    - Consecutive Hot Spot: Significant hotspot in 90% of time steps
    - Intensifying Hot Spot: Significant hotspot, increasing intensity
    - Persistent Hot Spot: Significant hotspot in every time step
    - Diminishing Hot Spot: Significant hotspot, decreasing intensity
    - Sporadic Hot Spot: Significant hotspot in <90% of time steps
    - Historical Hot Spot: Significant hotspot in past, not recent
    
    Cold Spots: (mirror categories for low values)
    
    Additional:
    - Oscillating: Fluctuates between hot/cold
    - No Pattern: No significant trend
    """
    
    # Step 1: Create space-time cube (bin disasters by time/space)
    # Step 2: Calculate Gi* statistic for each location at each time
    # Step 3: Classify based on temporal trend and significance
    
    pass
```

1. **Space-Time Cube**: Aggregate disaster events into space-time bins
2. **Gi* Calculation**: For each county, calculate Getis-Ord Gi* at each time step
3. **Mann-Kendall Trend**: Test if Gi* is increasing/decreasing/stable over time
4. **Classification**: Assign to 1 of 17 emerging hotspot categories
5. **Risk Trajectory**: Use trend to project future risk

### Required Data Sources
- **Existing FEMA Data**: Use declarationDate for temporal analysis
- **Python Libraries**: `pointpats` (space-time cube), `esda` (Gi*)

### Expected Output
- `hotspot_category`: One of 17 emerging hotspot classifications
- `gi_star_current`: Current Gi* statistic value
- `gi_star_trend`: Increasing/decreasing/stable (Mann-Kendall)
- `hotspot_confidence`: 90%, 95%, or 99% confidence level
- `risk_trajectory`: Projected trend direction

### Scientific Citations
- Getis & Ord (1992). "The Analysis of Spatial Association by Use of Distance Statistics." *Geographical Analysis*.
- Esri (2024). "How Emerging Hot Spot Analysis Works." ArcGIS Pro Documentation.

### Claude Code Instructions
```
Add esda and pointpats to requirements.txt. Create EmergingHotspotAnalyzer 
class in src/spatial_stats.py. Implement space_time_cube() using STCube 
from pointpats. Use esda.G_Local for Gi* calculation. Add Mann-Kendall 
trend test from pymannkendall. Map classifications to string categories.
```

---

## Methodology 4: Heat-Mortality Exposure-Response Functions

### Concept Name
Temperature-Attributable Mortality Risk Modeling

### Current Gap
No health impact modeling currently exists. Heat waves are tracked as disasters but health outcomes aren't quantified.

### Implementation Approach

```python
def calculate_heat_mortality_risk(df, climate_data):
    """
    Calculate temperature-attributable mortality using exposure-response functions.
    
    Method: Distributed Lag Non-Linear Model (DLNM) simplified
    
    ERF Formula:
    RR(T) = exp(β × (T - T_ref)) for T > T_threshold
    
    Where:
    - T = daily maximum temperature (°F)
    - T_ref = minimum mortality temperature (~75-80°F)
    - T_threshold = heat threshold (~85°F)
    - β = 0.003 to 0.008 per °F (location-specific)
    
    Attributable Deaths = Baseline_Mortality × (RR - 1) / RR
    
    Vulnerability modifiers:
    - Age 65+: 3.5× baseline risk
    - Cardiovascular disease: 2.8× baseline risk  
    - Poverty: 1.5× baseline risk
    - No AC: 2.0× baseline risk
    """
    
    # Fetch CDC WONDER mortality data
    # Get county baseline mortality rates
    # Calculate cooling degree days above threshold
    # Apply ERF to estimate attributable deaths
    # Weight by SVI components
    
    pass
```

1. **Baseline Mortality**: Fetch CDC WONDER age-adjusted death rates by county
2. **Temperature Exposure**: ACIS climate data for heat degree days (>85°F)
3. **Relative Risk Model**: Apply ERF: RR = exp(0.005 × (Tmax - 80)) for T > 80°F
4. **Attributable Fraction**: AF = (RR - 1) / RR
5. **Vulnerability Weighting**: Multiply by SVI × elderly_pct

### Required Data Sources
- **CDC WONDER**: `https://wonder.cdc.gov/` - Age-adjusted mortality rates
- **ACIS Climate**: Already integrated, need heat degree days
- **Census**: AC ownership (B25040_002E), age distribution

### Expected Output
- `heat_mortality_rate`: Deaths per 100,000 per year attributable to heat
- `heat_vulnerability_score`: Composite 0-1 score
- `excess_heat_deaths_est`: Estimated annual heat deaths
- `extreme_heat_risk_days`: Days > 95°F annually

### Scientific Citations
- Anderson & Bell (2009). "Weather-Related Mortality: How Heat, Cold, and Heat Waves Affect Mortality in the United States." *Epidemiology*.
- Vicedo-Cabrera et al. (2021). "The burden of heat-related mortality attributable to recent human-induced climate change." *Nature Climate Change*.

### Claude Code Instructions
```
Create HealthImpactAnalyzer class in src/health_impact.py. Implement 
calculate_heat_mortality() using CDC WONDER API. Use simplified ERF: 
RR = exp(0.005 * max(0, tmax - 80)). Fetch AC ownership from Census 
B25040_002E. Add heat_vulnerability_index to FEATURE_GROUPS['indices'].
```

---

## Methodology 5: Joplin Model - Indirect Economic Loss Multipliers

### Concept Name
Disaster Economic Impact Multiplier Model

### Current Gap
Intervention ROI uses static costs but doesn't calculate indirect economic losses from business interruption, supply chain disruption, or property devaluation.

### Implementation Approach

```python
def calculate_joplin_economic_loss(county_fips, hazard_type, severity):
    """
    Joplin Model: Economic Loss = Direct Loss × (1 + Indirect Multiplier)
    
    Indirect Multipliers by Sector (from Joplin, MO tornado study):
    - Healthcare: 1.8× direct losses
    - Manufacturing: 2.2× direct losses  
    - Retail: 1.6× direct losses
    - Agriculture: 2.5× direct losses
    
    Regional Multipliers:
    - Metropolitan: 1.4× - 1.8×
    - Micropolitan: 1.8× - 2.2×
    - Rural: 2.2× - 3.0×
    
    Housing Price Impact:
    - 1-year post-disaster: -5% to -15%
    - 5-year recovery: -2% to -8%
    
    Migration Impact:
    - Population loss: 2-8% in severe disasters
    - Tax base erosion: proportional to population × income
    """
    
    # Fetch county economic profile from Bureau of Economic Analysis
    # Calculate direct losses from FEMA NRI EAL
    # Apply sector-specific multipliers
    # Estimate business interruption (90-day average for moderate events)
    # Calculate housing market impact
    # Project tax revenue loss
    
    pass
```

1. **Direct Losses**: Use FEMA NRI EAL as baseline
2. **Sector Composition**: Fetch BEA GDP by county for sector weights
3. **Apply Multipliers**: Weighted average of sector multipliers
4. **Business Interruption**: Add 90-day GDP interruption for moderate+ events
5. **Property Impact**: Housing price decline × total assessed value

### Required Data Sources
- **BEA Regional Data**: `https://apps.bea.gov/regional/downloadzip.htm` - GDP by county
- **Census QWI**: Quarterly workforce indicators for sector composition
- **FEMA NRI**: Direct EAL values

### Expected Output
- `direct_economic_loss`: From FEMA NRI EAL
- `indirect_economic_loss`: Multiplier × direct
- `total_economic_impact`: Direct + indirect
- `business_interruption_days`: Estimated downtime
- `tax_revenue_at_risk`: Property + sales tax loss estimate

### Scientific Citations
- Stokes & Sen (2022). "An optimization model to inform alternatives for resilient infrastructure investment." *Sustainable and Resilient Infrastructure*.
- Simmons et al. (2020). "The Economic Effects of Financial Relief Delays Following a Natural Disaster."

### Claude Code Instructions
```
Create EconomicImpactModeler in src/economic_impact.py. Add BEA API client 
for GDP data. Implement joplin_multiplier calculation using sector weights.
Add BUSINESS INTERRUPTION_DAYS constant by hazard severity. Create 
economic_vulnerability_index = (indirect_loss / county_gdp) × svi.
```

---

## Methodology 6: IRS SOI Migration Flow Analysis

### Concept Name
Population Dynamics Risk Adjustment via Tax Migration Data

### Current Gap
Population is treated as static, but disaster-prone areas experience out-migration that reduces vulnerability, while climate migrants increase vulnerability in receiving areas.

### Implementation Approach

```python
def analyze_migration_risk_impact(df, migration_data):
    """
    IRS SOI Migration Data Analysis
    
    Data Available:
    - In-migration: Number of returns, exemptions, adjusted gross income
    - Out-migration: Same metrics
    - Net migration: In - Out
    - Non-migrants: Population that stayed
    
    Risk Indicators:
    1. Brain drain: Out-migration of high-income earners (AGI > $100k)
    2. Vulnerability flight: Elderly out-migration post-disaster
    3. Climate migration pressure: In-migration to "climate havens"
    4. Tax base erosion: Net AGI loss / total county AGI
    
    Adjusted Population = Census Population + Net Migration × (1 + undercount_factor)
    
    Undercount factor: 1.15 (SOI misses ~15% of population)
    """
    
    # Fetch SOI migration data by county
    # Calculate net migration rates
    # Identify vulnerable subpopulations in flows
    # Adjust effective population for risk calculations
    # Estimate future population trajectory
    
    pass
```

1. **Fetch SOI Data**: IRS migration flows by county
2. **Net Migration Rate**: (In - Out) / Base Population
3. **Vulnerability Profile**: Age/income composition of migrants
4. **Population Projection**: Apply 5-year migration trend
5. **Risk Adjustment**: Dynamic population for exposure calculations

### Required Data Sources
- **IRS SOI Migration**: `https://www.irs.gov/statistics/soi-tax-stats-migration-data`
- **Format**: CSV files by year, county-to-county flows
- **Fields**: Returns, Exemptions, AGI in/out flows

### Expected Output
- `net_migration_rate`: Annual population change from migration
- `brain_drain_index`: Net loss of high-AGI households
- `migration_adjusted_population`: Census + migration adjustment
- `climate_migration_pressure`: In-migration to low-risk counties
- `projected_2030_population`: Trend projection

### Scientific Citations
- IRS Statistics of Income Division. "Migration Data Methodology." U.S. Treasury.
- Hauer (2017). "Migration induced by sea-level rise could reshape the US population landscape." *Nature Climate Change*.

### Claude Code Instructions
```
Create MigrationAnalyzer class in src/population_dynamics.py. Implement 
IRS SOI CSV parser for county-level flows. Add net_migration_rate calculation 
and population projection using linear trend. Add MIGRATION_COLUMNS to 
config.FEATURE_GROUPS['demographics']. Download historical SOI files 
for 2018-2022 to establish trends.
```

---

## Methodology 7: Critical Infrastructure Interdependency Score

### Concept Name
Cross-Sector Cascade Failure Risk Assessment

### Current Gap
Network analysis exists for single-sector facilities but doesn't model interdependencies between power, water, communications, and transportation.

### Implementation Approach

```python
def calculate_interdependency_risk(county_fips):
    """
    Critical Infrastructure Interdependency Model
    
    Sectors Modeled:
    - Energy: Power plants, substations, transmission lines (EIA 860/923)
    - Water: Treatment plants, pumping stations (EPA SDWIS)
    - Communications: Cell towers, data centers (FCC, self-reported)
    - Transportation: Highways, bridges, rail (DOT NHPN)
    - Healthcare: Hospitals (existing HIFLD)
    
    Interdependency Matrix:
    Power → Water (pumps need electricity)
    Power → Communications (towers need backup power)
    Water → Healthcare (hospitals need water)
    Communications → All (coordination dependency)
    
    Cascade Model:
    1. Initial failure in sector A
    2. Propagation time by dependency type (hours)
    3. Load redistribution to remaining nodes
    4. Secondary failures if load > capacity
    5. Calculate total affected population
    
    Interdependency Score = Σ (Dependency_Weight × Redundancy_Factor)
    """
    
    # Fetch infrastructure data for all sectors
    # Build multi-layer network graph
    # Calculate cross-sector betweenness centrality
    # Simulate cascade scenarios
    # Calculate population at risk from cascade
    
    pass
```

1. **Multi-Layer Network**: Extend existing NetworkX graph to multiple sectors
2. **Dependency Weights**: Power→Water=0.9, Power→Comm=0.7, Water→Health=0.8
3. **Redundancy Assessment**: Backup power, alternative water sources
4. **Cascade Simulation**: Breadth-first failure propagation
5. **Population Impact**: Service area × population for failed nodes

### Required Data Sources
- **EIA Form 860**: Power plant locations
- **EPA SDWIS**: Water treatment facilities
- **FCC ASR**: Antenna structure registry (cell towers)
- **DOT NHPN**: National highway planning network

### Expected Output
- `interdependency_score`: 0-1 composite score
- `single_points_of_failure`: Critical cross-sector nodes
- `cascade_affected_population`: People affected by worst-case cascade
- `redundancy_gaps`: Missing backup systems by sector
- `cross_sector_betweenness`: Bottleneck facilities

### Scientific Citations
- Lewis & Petit (2020). "Critical Infrastructure Interdependency Analysis." *UNDRR Technical Report*.
- Ouyang (2014). "Review on modeling and simulation of interdependent critical infrastructure systems." *Reliability Engineering & System Safety*.

### Claude Code Instructions
```
Extend InfrastructureNetwork in src/network_analysis.py to MultiLayerNetwork.
Add EIA, EPA, FCC data fetchers to src/download_data.py. Implement 
interdependency_matrix as adjacency matrix between sectors. Add 
calculate_cascade_impact() using BFS with load redistribution. Create 
INTERDEPENDENCY_WEIGHTS constant dictionary.
```

---

## Methodology 8: Mobile Home Vulnerability Multiplier

### Concept Name
Housing Type Risk Stratification (Manufactured Housing)

### Current Gap
All housing is treated equally, but mobile/manufactured homes have 15-20× higher tornado fatality rates and 4-10× higher flood damage rates.

### Implementation Approach

```python
def calculate_housing_vulnerability_multiplier(df):
    """
    Mobile/Manufactured Home Vulnerability Multiplier
    
    Research-Based Risk Ratios:
    
    Tornado Risk (Strader & Ashley 2018):
    - Mobile home fatality rate: 15-20× permanent housing
    - Risk varies by region (higher in Southeast)
    - Age of unit matters: pre-1976 = 2× vs post-1976
    
    Flood Risk (FEMA data):
    - Mobile home damage: 4-10× permanent housing
    - Foundation type critical: anchored vs unanchored
    - Elevation matters: <2ft above BFE = catastrophic
    
    Hurricane Risk:
    - Wind vulnerability: 3-5× permanent housing
    - Storm surge: Similar to flood risk
    
    Vulnerability Score Formula:
    mh_ratio = mobile_home_pct / national_avg_mobile_home_pct
    
    If mh_ratio > 1.5:
        tornado_multiplier = 1 + (mh_ratio × 0.15)
        flood_multiplier = 1 + (mh_ratio × 0.08)
    
    Composite Housing Vulnerability = weighted average by hazard probability
    """
    
    # Fetch mobile home percentage from Census B25024_010E
    # Calculate ratio to national average (6.5%)
    # Apply hazard-specific multipliers
    # Weight by county's dominant hazard type
    # Adjust existing risk_score
    
    pass
```

1. **Census Data**: B25024_010E (mobile homes) / B25024_001E (total housing)
2. **Risk Ratio Calculation**: County mobile home % / 6.5% (national avg)
3. **Hazard-Specific Multipliers**: Tornado (15×), Flood (7×), Hurricane (4×)
4. **Weighted Composite**: Blend based on FEMA NRI dominant hazard
5. **Risk Score Adjustment**: Multiply existing risk_score by vulnerability

### Required Data Sources
- **Census ACS**: B25024 (Units in Structure) for mobile home count
- **FEMA NRI**: Dominant hazard type by county
- **Research Data**: Strader & Ashley (2018) mobile home fatality rates

### Expected Output
- `mobile_home_pct`: % of housing that is mobile/manufactured
- `mobile_home_risk_ratio`: County vs national average
- `housing_vulnerability_multiplier`: Composite 1.0 - 3.0
- `tornado_fatality_risk`: Elevated risk score for tornado-prone areas

### Scientific Citations
- Strader & Ashley (2018). "Finescale Assessment of Mobile Home Tornado Vulnerability in the Central and Southeast United States." *Weather, Climate, and Society*.
- Simmons & Sutter (2012). "The 2011 Tornadoes and the Future of Tornado Research." *Bulletin of the American Meteorological Society*.

### Claude Code Instructions
```
Add B25024_010E to CENSUS_VARIABLES in config.py. Create 
calculate_housing_vulnerability() in feature_engineering.py. 
Define MOBILE_HOME_RISK_RATIOS = {'tornado': 15, 'flood': 7, 'hurricane': 4}. 
Calculate housing_vulnerability_multiplier as weighted average 
based on dominant_hazard. Add to risk_score calculation.
```

---

## Methodology 9: Cumulative Impact Assessment (CEJST Methodology)

### Concept Name
Environmental Justice Cumulative Impact Scoring

### Current Gap
No consideration of environmental burden accumulation - counties with multiple stressors (air pollution + poverty + flood risk) have compounding effects not captured by individual metrics.

### Implementation Approach

```python
def calculate_cumulative_impact_score(df):
    """
    Climate and Economic Justice Screening Tool (CEJST) Methodology
    
    Burden Categories (at least 1 indicator exceeded = burden):
    
    Climate Burden:
    - Flood risk (expected building loss rate > 90th percentile)
    - Wildfire risk (expected loss rate > 90th percentile)
    - Extreme heat (high temp days > 90th percentile)
    
    Energy Burden:
    - Energy cost burden > 90th percentile
    - PM2.5 exposure > 90th percentile
    
    Transportation Burden:
    - Diesel PM exposure > 90th percentile
    - Traffic proximity > 90th percentile
    
    Housing Burden:
    - Historic underinvestment (various housing indicators)
    - Lead paint (older housing stock)
    
    Health Burden:
    - Asthma (emergency visits > 90th percentile)
    - Diabetes (diagnosed rate > 90th percentile)
    - Heart disease
    - Life expectancy
    
    Socioeconomic Indicators (AND condition):
    - Low income (>65% below 200% federal poverty line)
    OR
    - High SVI
    
    Cumulative Impact = Σ(Burden_Categories) × Socioeconomic_Vulnerability
    
    Disadvantaged if: >= 2 burden categories AND socioeconomic indicator
    """
    
    # Fetch EJSCREEN data for environmental indicators
    # Calculate 90th percentile thresholds
    # Count burden categories exceeded
    # Check socioeconomic criteria
    # Classify as disadvantaged or not
    
    pass
```

1. **EJSCREEN Data**: EPA environmental justice screening data
2. **90th Percentile Thresholds**: Calculate for each burden indicator
3. **Burden Count**: Sum categories where county exceeds threshold
4. **Socioeconomic Check**: Poverty > 20% OR SVI > 0.75
5. **Cumulative Score**: Burden count × SVI for severity ranking

### Required Data Sources
- **EPA EJSCREEN**: `https://www.epa.gov/ejscreen` - Environmental indicators
- **CDC PLACES**: `https://www.cdc.gov/places` - Health outcomes
- **DOE LEAD**: Low-income energy affordability data

### Expected Output
- `burden_category_count`: 0-6 categories with elevated burdens
- `cumulative_impact_score`: Composite 0-1 score
- `cejst_disadvantaged`: Boolean (meets CEJST criteria)
- `environmental_burden_index`: Pollution + climate burden
- `health_vulnerability_index`: Disease prevalence composite

### Scientific Citations
- CEQ (2024). "Climate and Economic Justice Screening Tool: Methodology." Council on Environmental Quality.
- EPA (2024). "EJSCREEN Technical Documentation." Environmental Protection Agency.

### Claude Code Instructions
```
Create CumulativeImpactAnalyzer in src/equity_analysis.py. Add EJSCREEN 
API client. Define BURDEN_CATEGORIES dict with thresholds. Implement 
90th percentile calculation using numpy.percentile(). Add 
cejst_disadvantaged flag requiring >=2 burden categories AND 
(svi > 0.75 OR poverty_pct > 20). Add to FEATURE_GROUPS['indices'].
```

---

## Methodology 10: Flood-Mental Health Correlation Model

### Concept Name
Disaster-Attributable Mental Health Burden Quantification

### Current Gap
No mental health impact modeling exists despite flood PTSD rates of 15-30% and depression rates of 20-40% in affected populations.

### Implementation Approach

```python
def calculate_flood_mental_health_impact(df, fema_history):
    """
    Flood-Attributable Mental Health Burden Model
    
    Research-Based Prevalence Rates (post-flood):
    
    PTSD:
    - 6 months post-flood: 15-30%
    - 1 year post-flood: 10-20%
    - 2+ years post-flood: 5-10%
    
    Depression:
    - 6 months: 20-40%
    - 1 year: 15-30%
    - 2+ years: 10-15%
    
    Anxiety:
    - 6 months: 25-50%
    - 1 year: 20-30%
    
    Risk Factors (multipliers):
    - Displacement: 2.0× baseline
    - Income loss: 1.8× baseline
    - Prior trauma: 1.5× baseline
    - Social isolation: 1.7× baseline
    - Repeat flooding: 1.4× baseline
    
    Burden Calculation:
    For each flood event in past 5 years:
        affected_pop = flood_declaration_affected_population
        base_prevalence = research_rate_by_time_since
        adjusted_prevalence = base_prevalence × risk_factor_product
        cases = affected_pop × adjusted_prevalence
    
    Total MH burden = sum(cases across all events)
    """
    
    # Fetch FEMA IA (Individual Assistance) data for affected populations
    # Get flood event timeline
    # Apply research-based prevalence rates by time since event
    # Weight by risk factors (poverty, displacement)
    # Calculate treatment cost burden
    
    pass
```

1. **FEMA IA Data**: Individual Assistance registration counts by disaster
2. **Prevalence Rates**: Apply research-based PTSD/depression rates
3. **Time Decay**: Reduce rates as time since flood increases
4. **Risk Adjustment**: Multiply by SVI components (poverty, disability)
5. **Cost Estimation**: Cases × treatment cost (~$5,000/case/year)

### Required Data Sources
- **FEMA IA**: Individual Assistance data by disaster
- **NORS**: National Occupational Respiratory System (mental health services)
- **SAMHSA**: Treatment facility locator data

### Expected Output
- `ptsd_cases_est`: Estimated PTSD cases from recent floods
- `depression_cases_est`: Estimated depression cases
- `mental_health_burden_score`: Composite 0-1
- `unmet_mh_need_estimate`: Cases without access to treatment
- `mh_treatment_cost_estimate`: Annual cost in dollars

### Scientific Citations
- Stanke et al. (2012). "Health Effects of Drought: A Systematic Review of the Evidence." *PLOS Currents*.
- Munro et al. (2017). "Effect of evacuation and displacement on the association between flooding and mental health outcomes." *Lancet Planetary Health*.

### Claude Code Instructions
```
Create MentalHealthImpactAnalyzer in src/health_impact.py. Define 
MENTAL_HEALTH_PREVALENCE dict with rates by disorder and time. 
Implement calculate_flood_mental_health_burden() using FEMA 
disaster_history. Add risk_factor_multipliers for poverty, 
elderly_pct, disability_pct. Add mental_health_burden_index to 
FEATURE_GROUPS['indices'].
```

---

## Methodology 11: Spatial Interaction Model for Healthcare Access

### Concept Name
Distance-Decay Healthcare Accessibility Index

### Current Gap
Current system uses simple nearest-facility distance without considering capacity, specialty services, or the distance-decay of healthcare utilization.

### Implementation Approach

```python
def calculate_spatial_accessibility(df, facilities_df, beta=-0.03):
    """
    Two-Step Floating Catchment Area (2SFCA) Method
    
    Step 1: For each facility j:
        R_j = S_j / Σ_k (P_k × f(d_kj))
        Where:
        - S_j = supply (hospital beds, ICU capacity, specialists)
        - P_k = population in zone k
        - f(d_kj) = distance decay function
        - d_kj = distance from zone k to facility j
    
    Step 2: For each population zone i:
        A_i = Σ_j (R_j × f(d_ij))
        Where A_i = accessibility score for zone i
    
    Distance Decay Options:
    - Gaussian: f(d) = exp(-d²/σ²)
    - Gravity: f(d) = d^β where β = -0.03 to -0.05 per km
    - Kernel: f(d) = (1 - (d/dmax)²)² for d < dmax
    
    Vulnerability-Weighted Access:
    VWA_i = A_i × (1 / SVI_i)
    
    Lower VWA = higher healthcare access gap for vulnerable populations
    """
    
    # Get facility capacity data (CMS Hospital Cost Report)
    # Get specialty service availability
    # Calculate distance matrix between counties and facilities
    # Apply distance decay function
    # Calculate 2SFCA accessibility scores
    # Weight by population vulnerability
    
    pass
```

1. **Facility Capacity**: CMS Hospital Cost Report for bed counts
2. **Distance Matrix**: Haversine between counties and hospitals
3. **Gravity Model**: f(d) = exp(-0.03 × d_km)
4. **2SFCA Calculation**: Supply-to-demand ratio within catchment
5. **Vulnerability Weighting**: Divide by SVI to identify inequity

### Required Data Sources
- **CMS Hospital Cost Report**: Bed counts, ICU capacity
- **CMS POS**: Provider of Services file for specialty counts
- **AHA Annual Survey**: Hospital characteristics

### Expected Output
- `healthcare_accessibility_score`: 2SFCA accessibility index
- `icu_accessibility`: ICU-specific accessibility
- `specialty_accessibility_score`: Specialist physician access
- `vulnerability_weighted_access`: Adjusted for SVI
- `access_gap_index`: Inverse of accessibility for prioritization

### Scientific Citations
- Luo & Wang (2003). "Measures of Spatial Accessibility to Health Care in a GIS Environment." *International Journal of Geographical Information Science*.
- McGrail & Humphreys (2009). "Measuring spatial accessibility to primary care in rural areas." *Social Science & Medicine*.

### Claude Code Instructions
```
Implement TwoStepFCA class in src/health_access.py. Add 
CMS Hospital Cost Report data fetcher. Define gravity_decay(d, beta=-0.03) 
function. Calculate distance matrix using scipy.spatial.distance.cdist(). 
Add HEALTHCARE_SUPPLY_WEIGHTS for beds, ICU, specialists. Create 
healthcare_accessibility_gap = 1 / (accessibility_score + epsilon).
```

---

## Methodology 12: Compound Climate-Hazard Interaction Index

### Concept Name
Multi-Hazard Compounding and Cascade Risk Assessment

### Current Gap
Hazards are analyzed independently, but compound events (drought + heat, flood + power outage) have multiplicative rather than additive risk.

### Implementation Approach

```python
def calculate_compound_hazard_risk(df, climate_data):
    """
    Compound Event Risk Assessment
    
    Compound Hazard Pairs (with interaction multipliers):
    
    1. Drought + Heat Wave: 2.5× wildfire risk
       - Dried vegetation × high temperatures
       - Agricultural loss multiplier: 1.8×
    
    2. Flood + Power Outage: 3.0× health impact
       - Can't pump water, treat sewage
       - Hospital backup generator dependency
    
    3. Hurricane + Pandemic: 2.0× evacuation difficulty
       - Shelter capacity constraints
       - Social distancing complications
    
    4. Extreme Cold + Power Outage: 4.0× mortality
       - Texas 2021 Uri event pattern
       - Water pipe freeze cascade
    
    5. Wildfire Smoke + Heat: 1.5× respiratory mortality
       - PM2.5 + temperature synergistic effect
    
    Compound Risk Calculation:
    For each hazard pair (H1, H2):
        P_compound = P(H1) × P(H2|H1) × correlation_factor
        Impact_compound = max(Impact_H1, Impact_H2) × interaction_multiplier
        Risk_compound = P_compound × Impact_compound
    
    Total Compound Risk = Σ(all hazard pairs)
    
    Temporal Clustering:
    - Identify "disaster sequences" within 90-day windows
    - Recovery hasn't completed before next event
    - Psychological and infrastructure exhaustion
    """
    
    # Get hazard occurrence probabilities from NRI
    # Calculate conditional probabilities from historical co-occurrence
    # Apply interaction multipliers
    # Calculate compound risk scores
    # Identify high-risk compound combinations by county
    
    pass
```

1. **Hazard Correlation**: Calculate historical co-occurrence rates
2. **Conditional Probability**: P(H2|H1) from FEMA disaster history
3. **Interaction Multipliers**: Research-based amplification factors
4. **Compound Risk**: Multiply marginal risks by interaction terms
5. **Temporal Clustering**: Find disaster sequences in 90-day windows

### Required Data Sources
- **FEMA NRI**: Individual hazard annual frequency
- **FEMA Disasters**: Historical co-occurrence patterns
- **NOAA Storm Events**: Precise timing for compound identification

### Expected Output
- `compound_hazard_risk`: Aggregate compound risk score
- `top_compound_combo`: Highest-risk hazard pair
- `compound_event_probability`: Annual probability of compound event
- `cascade_vulnerability`: Risk amplification factor
- `disaster_sequence_risk`: Multiple events in short window

### Scientific Citations
- Zscheischler et al. (2018). "Future climate risk from compound events." *Nature Climate Change*.
- Raymond et al. (2020). "Understanding and managing connected extreme events." *Nature Climate Change*.

### Claude Code Instructions
```
Create CompoundHazardAnalyzer in src/compound_risk.py. Define 
COMPOUND_PAIRS dict with interaction_multipliers. Implement 
calculate_hazard_correlation_matrix() using FEMA disaster_history. 
Calculate conditional_probability using Bayes rule. Add 
compound_risk_multiplier to existing risk_score. Add temporal 
clustering using 90-day rolling windows on disaster dates.
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
| Methodology | File Changes | Priority |
|-------------|--------------|----------|
| CDC SVI Integration | `feature_engineering.py`, `config.py` | High |
| FEMA NRI EAL | `climate_client.py`, `config.py` | High |
| Mobile Home Multiplier | `feature_engineering.py`, `config.py` | High |

### Phase 2: Spatial Analysis (Weeks 3-4)
| Methodology | File Changes | Priority |
|-------------|--------------|----------|
| Getis-Ord Gi* Hotspots | `spatial_stats.py` (new) | Medium |
| CEJST Cumulative Impact | `equity_analysis.py` (new) | Medium |
| 2SFCA Healthcare Access | `health_access.py` (new) | Medium |

### Phase 3: Health & Population (Weeks 5-6)
| Methodology | File Changes | Priority |
|-------------|--------------|----------|
| Heat-Mortality ERF | `health_impact.py` (new) | High |
| Flood-Mental Health | `health_impact.py` | Medium |
| IRS Migration Flows | `population_dynamics.py` (new) | Medium |

### Phase 4: Economic & Infrastructure (Weeks 7-8)
| Methodology | File Changes | Priority |
|-------------|--------------|----------|
| Joplin Economic Model | `economic_impact.py` (new) | Medium |
| Infrastructure Interdependency | `network_analysis.py` | Low |
| Compound Hazards | `compound_risk.py` (new) | Low |

---

## Data Dependencies Summary

### New Census Variables Needed
```python
ADDITIONAL_CENSUS_VARS = [
    "B23025_005E",  # Unemployed
    "B15003_002E",  # No high school diploma
    "B09001_001E",  # Population under 18
    "B11012_003E",  # Single father households
    "B11012_014E",  # Single mother households
    "B03002_003E",  # White alone (for minority calc)
    "C16002_004E",  # Spanish, English less than very well
    "B25024_003E",  # 2-9 units in structure
    "B25024_004E",  # 10-19 units in structure
    "B25024_010E",  # Mobile homes
    "B25014_005E",  # 1-1.5 occupants per room
    "B08201_002E",  # No vehicle available
    "B26001_001E",  # Group quarters population
    "B25040_002E",  # No AC
]
```

### New External APIs
1. **CDC WONDER**: Mortality data (free, no key)
2. **EPA EJSCREEN**: Environmental justice data (free)
3. **IRS SOI**: Migration data (bulk CSV download)
4. **BEA Regional**: GDP by county (free API)
5. **CMS POS**: Provider services (bulk download)

---

## Expected Performance Impact

### Feature Count Increase
- Current: ~66 features
- After Phase 1: ~85 features (+19)
- After Phase 2: ~105 features (+20)
- After Phase 3: ~125 features (+20)
- After Phase 4: ~140 features (+15)

### Model Performance Expectations
- **Baseline Risk Prediction**: +8-12% AUC from SVI/EAL integration
- **Spatial Clustering**: Enables hotspot-focused interventions
- **Health Impacts**: New prediction target for mortality risk
- **Economic Loss**: Improved cost-benefit for interventions

### Computational Overhead
- SVI calculation: +2s per county (one-time)
- Spatial analysis: +30s for national dataset (one-time)
- Health models: +1s per query (real-time)
- Economic models: +0.5s per query (real-time)

---

## Scientific Validation

All methodologies should be validated against:
1. **CDC SVI**: Compare calculated SVI to official CDC values (r² > 0.95)
2. **FEMA NRI**: Compare EAL-weighted risk to NRI Risk Index (r² > 0.90)
3. **Spatial Stats**: Validate Gi* against ArcGIS output for same data
4. **Health Models**: Compare heat mortality to CDC heat death data
5. **Economic Models**: Validate against historical disaster cost estimates

---

## Conclusion

These 12 cross-disciplinary methodologies will transform ResilienceAI from a vulnerability assessment tool into a comprehensive disaster risk intelligence platform. By integrating climate science, public health, economics, and social vulnerability, the platform will provide:

1. **More accurate risk predictions** through compound hazard modeling
2. **Equity-focused interventions** through SVI and cumulative impact scoring
3. **Health-informed planning** through exposure-response functions
4. **Economic justification** through indirect loss multipliers
5. **Spatial targeting** through emerging hotspot analysis

The implementation roadmap prioritizes foundational indices (SVI, EAL) first, followed by spatial analysis, health impacts, and advanced economic/infrastructure models.

---

*Report compiled for ResilienceAI MUIDSI Hackathon 2026*
*Sources: CDC, FEMA, EPA, IRS, peer-reviewed literature*
