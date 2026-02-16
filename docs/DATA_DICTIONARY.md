# ResilienceAI - Data Dictionary

## Processed Dataset: `data/processed/county_features.csv`

3,222 US counties | 66 columns | All real federal data

---

### Identifiers

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `fips` | string | 5-digit FIPS county code | "29019" (Boone Co, MO) |
| `county_name` | string | County name with state | "Boone County, Missouri" |
| `latitude` | float | County centroid latitude | 38.99 |
| `longitude` | float | County centroid longitude | -92.31 |

### Demographics (Census ACS 2022)

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `total_population` | int | 50 - 9,936,690 | Total county population |
| `median_income` | int | varies* | Median household income ($) |
| `poverty_count` | int | 3 - 1,343,978 | Population below poverty line |
| `poverty_pct` | float | 1.6% - 65.6% | Poverty rate |
| `elderly_population` | int | 11 - 1,415,856 | Population age 65+ |
| `elderly_pct` | float | 2.9% - 57.9% | Elderly percentage |
| `disability_count` | int | 10 - 1,045,189 | Population with disability |
| `disability_pct` | float | 4.0% - 41.1% | Disability rate |
| `uninsured_count` | int | 0 - 997,287 | Uninsured population |
| `uninsured_pct` | float | 0.0% - 45.1% | Uninsured rate |

*Note: median_income uses Census sentinel value -666666666 for suppressed data (small counties). Filter or impute before analysis.

### Infrastructure Distance Features (HIFLD + CMS)

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `dist_nearest_hospitals_km` | float | 0.2 - 5,558 | Distance to nearest hospital (km) |
| `dist_nearest_fire_stations_km` | float | 0.04 - 5,558 | Distance to nearest fire station |
| `dist_nearest_ems_stations_km` | float | 0.2 - 27,433 | Distance to nearest EMS station |
| `dist_nearest_nursing_homes_km` | float | 0.2 - 5,769 | Distance to nearest nursing home |
| `dist_2nd_nearest_hospitals_km` | float | varies | Distance to 2nd nearest hospital (redundancy metric) |
| `dist_2nd_nearest_fire_stations_km` | float | varies | Distance to 2nd nearest fire station |
| `dist_2nd_nearest_ems_stations_km` | float | varies | Distance to 2nd nearest EMS station |
| `dist_2nd_nearest_nursing_homes_km` | float | varies | Distance to 2nd nearest nursing home |
| `count_hospitals_50km` | int | 0 - 165 | Hospitals within 50km radius |
| `count_fire_stations_50km` | int | 0 - 927 | Fire stations within 50km |
| `count_ems_stations_50km` | int | 0 - 248 | EMS stations within 50km |
| `count_nursing_homes_50km` | int | 0 - 381 | Nursing homes within 50km |

*Note: Large distances (>1,000km) indicate Alaska/Hawaii/territory counties.

### Infrastructure Density Features

| Column | Type | Description |
|--------|------|-------------|
| `density_hospitals_per10k` | float | Hospitals per 10,000 people within 50km |
| `density_fire_stations_per10k` | float | Fire stations per 10,000 people within 50km |
| `density_ems_stations_per10k` | float | EMS stations per 10,000 people within 50km |
| `density_nursing_homes_per10k` | float | Nursing homes per 10,000 people within 50km |

### Disaster History Features (FEMA)

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `disaster_count` | int | 0 - 172 | Total FEMA disaster declarations (since 1953) |
| `disaster_count_recent` | int | 0 - 150 | Disaster declarations since 2015 |
| `disaster_flood` | int | 0 - 25 | Flood disaster declarations |
| `disaster_severe_storms` | int | 0 | Severe storm declarations* |
| `disaster_hurricane` | int | 0 - 33 | Hurricane declarations |
| `disaster_fire` | int | 0 - 61 | Fire/wildfire declarations |
| `disaster_tornado` | int | 0 - 6 | Tornado declarations |

*Note: `disaster_severe_storms` is 0 because FEMA uses "Severe Storm(s)" which may not match the exact string filter. Check FEMA `incidentType` values for correction.

### Composite Indices (Engineered)

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `vulnerability_index` | float | 0.06 - 0.58 | Normalized composite of elderly, poverty, disability, uninsured rates (0=least, 1=most vulnerable) |
| `isolation_index` | float | 0.0 - 1.0 | Normalized average distance to all facility types (0=best access, 1=most isolated) |
| `risk_score` | float | 0.0 - 1.0 | Weighted composite: 40% vulnerability + 30% isolation + 30% disaster exposure, then min-max normalized |
| `risk_level` | string | Low/Med/High | Tercile classification of risk_score |

---

## Advanced Differentiator Features

These features enable the agentic AI to provide deeper insights, identify compound risks, and recommend targeted interventions.

### Compound Risk Clusters

Identify counties that are HIGH on 3+ risk dimensions simultaneously. Dimensions include: vulnerability, isolation, disaster exposure, and infrastructure deficit.

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `compound_risk_count` | int | 0 - 4 | Number of risk dimensions where county is in top quartile (high vulnerability, high isolation, high disaster count, low infrastructure density) |
| `compound_risk_flag` | bool/int | 0 or 1 | True if county has 3+ compound risk dimensions - indicates critical multi-factor vulnerability requiring immediate attention |

**Calculation Logic:**
- High vulnerability: `vulnerability_index >= 75th percentile`
- High isolation: `isolation_index >= 75th percentile`
- High disaster exposure: `disaster_count >= 75th percentile`
- Infrastructure deficit: `avg_density <= 25th percentile`

---

### Risk Contagion (Nearest-Neighbor Analysis)

For each county, computes the average risk_score of its 5 nearest geographic neighbors. If neighbors are all high-risk, overflow capacity is limited during disasters, creating a contagion effect.

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `neighbor_avg_risk` | float | 0.0 - 1.0 | Average risk_score of 5 nearest neighboring counties (geographic proximity) |
| `risk_contagion_delta` | float | -1.0 to 1.0 | Difference between neighbor average risk and own risk (positive = neighbors are higher risk, indicating potential resource strain) |

**Calculation Logic:**
- Uses cKDTree spatial index on county centroids (converted to radians)
- Queries K=5 nearest neighbors for each county (excluding self)
- `neighbor_avg_risk` = mean of neighbors' risk_score
- `risk_contagion_delta` = `neighbor_avg_risk - risk_score`

**Interpretation:**
- Positive delta: Surrounded by higher-risk counties (limited mutual aid capacity)
- Negative delta: Lower risk than neighbors (potential resource provider)
- Near zero: Risk level consistent with region

---

### Temporal Disaster Acceleration

Compares disaster frequency in recent decade (2015-2025) vs prior decade (2005-2014). Acceleration ratio > 1 indicates disasters are increasing.

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `disasters_2015_2025` | int | 0+ | Count of FEMA disaster declarations in recent decade (2015-2025) |
| `disasters_2005_2014` | int | 0+ | Count of FEMA disaster declarations in prior decade (2005-2014) |
| `disaster_acceleration` | float | 0+ | Ratio of recent to prior decade disasters (`disasters_2015_2025 / (disasters_2005_2014 + 1)`) |

**Calculation Logic:**
- Extracts year from `declarationDate` in FEMA data
- Groups by county FIPS for each decade
- Adds 1 to denominator to avoid division by zero
- Values > 1.0 indicate accelerating disaster frequency

**Interpretation:**
- `disaster_acceleration > 1.0`: Disasters are increasing (climate change impact, emerging risk)
- `disaster_acceleration < 1.0`: Disasters decreasing or stable
- `disaster_acceleration = 0`: No disasters in recent decade

---

### Infrastructure Redundancy Score

Measures how far the 2nd-nearest facility is. If very far, there's zero redundancy: one facility failure = complete loss of access.

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `redundancy_score` | float | 0.0 - 1.0 | Normalized average of inverted 2nd-nearest distances across all facility types (1.0 = high redundancy, 0.0 = no redundancy) |
| `zero_redundancy_flag` | bool/int | 0 or 1 | True if 2nd nearest hospital is >100km away - indicates critical single point of failure |

**Calculation Logic:**
- Uses `dist_2nd_nearest_*` columns for all 4 facility types
- Normalizes each distance (inverted: low distance = high redundancy)
- `redundancy_score` = mean of normalized inverted distances
- `zero_redundancy_flag` = 1 if `dist_2nd_nearest_hospitals_km > 100`

**Interpretation:**
- High redundancy_score: Multiple nearby facilities provide backup options
- zero_redundancy_flag = 1: Hospital deserts where nearest backup is >100km - critical vulnerability

---

### Population-Weighted Vulnerability

Weights vulnerability metrics by total population so the agent can prioritize interventions by total lives impacted, not just per-capita rates.

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `pop_weighted_vulnerability` | float | varies | Raw population-weighted vulnerability (`vulnerability_index * total_population`) |
| `pop_weighted_vulnerability_norm` | float | 0.0 - 1.0 | Min-max normalized pop_weighted_vulnerability for comparability |
| `pop_weighted_risk` | float | varies | Raw population-weighted risk (`risk_score * total_population`) |
| `pop_weighted_risk_norm` | float | 0.0 - 1.0 | Min-max normalized pop_weighted_risk for comparability |

**Calculation Logic:**
- `pop_weighted_vulnerability = vulnerability_index * total_population`
- `pop_weighted_risk = risk_score * total_population`
- Normalized variants use min-max scaling to 0-1 range

**Interpretation:**
- Prioritizes large metropolitan counties with moderate vulnerability over small counties with high per-capita rates
- Use for resource allocation decisions where total impact matters

---

### State-Level Rankings

Percentile rank within own state for key metrics. Enables agent to say "worst county in Texas" or "top 10% in Florida."

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `state_fips` | string | 2-digit | State FIPS code (first 2 digits of county FIPS) |
| `counties_in_state` | int | 1+ | Total number of counties in the same state |
| `risk_score_state_pctile` | float | 0.0 - 1.0 | Percentile rank of risk_score within state (1.0 = highest risk in state) |
| `vulnerability_index_state_pctile` | float | 0.0 - 1.0 | Percentile rank of vulnerability_index within state |
| `isolation_index_state_pctile` | float | 0.0 - 1.0 | Percentile rank of isolation_index within state |

**Calculation Logic:**
- Extracts `state_fips` from first 2 digits of county FIPS
- Uses pandas `groupby(state_fips).rank(pct=True)` for percentile calculation
- Counts counties per state for context

**Interpretation:**
- 0.90+ : Among worst 10% in the state
- 0.50 : Median for the state
- 0.10- : Among best 10% in the state

---

### Gap Analysis Matrix

For each county, estimates which single intervention would most reduce its risk score. Enables targeted resource allocation recommendations.

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `gap_hospital` | float | 0.0 - 1.0 | Normalized gap score for hospital access (higher = greater need) |
| `gap_ems` | float | 0.0 - 1.0 | Normalized gap score for EMS access |
| `gap_fire` | float | 0.0 - 1.0 | Normalized gap score for fire station access |
| `gap_poverty` | float | 0.0 - 1.0 | Normalized gap score for poverty reduction |
| `gap_disaster_prep` | float | 0.0 - 1.0 | Normalized gap score for disaster preparedness |
| `top_intervention` | string | category | Recommended intervention type: `add_hospital`, `add_ems`, `add_fire`, `add_poverty`, or `add_disaster_prep` |
| `top_intervention_score` | float | 0.0 - 1.0 | Score of the top intervention (higher = greater expected impact) |

**Calculation Logic:**
- Each gap is min-max normalized distance or rate for that dimension
- `gap_hospital`: Based on `dist_nearest_hospitals_km`
- `gap_ems`: Based on `dist_nearest_ems_stations_km`
- `gap_fire`: Based on `dist_nearest_fire_stations_km`
- `gap_poverty`: Based on `poverty_pct`
- `gap_disaster_prep`: Based on `disaster_count` (high count = need for prep)
- `top_intervention` = gap dimension with maximum value for each county
- `top_intervention_score` = value of that maximum gap

**Interpretation:**
- Use `top_intervention` to identify highest-impact intervention per county
- Counties with similar `top_intervention` can be grouped for program design
- `top_intervention_score` indicates urgency/potential impact

---

## Raw Data Files (`data/raw/`)

| File | Records | Source | Key Columns |
|------|---------|--------|-------------|
| `hifld_hospitals.csv` | 7,496 | FEMA ArcGIS Hub | NAME, STATE, COUNTY, latitude, longitude, TYPE, STATUS, BEDS |
| `hifld_fire_stations.csv` | 52,051 | FEMA ArcGIS Hub | NAME, latitude, longitude, FTYPE, FCODE |
| `hifld_ems_stations.csv` | 7,045 | FEMA ArcGIS Hub | NAME, latitude, longitude, FTYPE, FCODE |
| `hifld_nursing_homes.csv` | 14,713 | CMS Medicare API | NAME, STATE, COUNTY, latitude, longitude, BEDS |
| `fema_disasters.csv` | 69,615 | OpenFEMA API | fipsStateCode, fipsCountyCode, incidentType, declarationDate |
| `census_demographics.csv` | 3,222 | Census ACS API | fips, county_name, total_population, poverty_pct, elderly_pct, ... |
| `county_centroids.csv` | 3,222 | Census Gazetteer | fips, county_name, latitude, longitude |

## Model Artifacts (`models/`)

| File | Description |
|------|-------------|
| `best_model.pkl` | Best performing model (Logistic Regression, F1=0.983) |
| `model_random_forest.pkl` | Random Forest classifier |
| `model_gradient_boosting.pkl` | Gradient Boosting classifier |
| `model_logistic_regression.pkl` | Logistic Regression classifier |
| `model_neural_network.pkl` | MLP Neural Network classifier |
| `scaler.pkl` | StandardScaler fitted on training data |
| `label_encoder.pkl` | LabelEncoder for risk_level (High/Low/Medium) |
| `feature_names.pkl` | Ordered list of 27 feature column names |
| `agent_config.json` | Archia agent system prompt + MCP tool definitions |

---

## Feature Summary

| Category | Count | Columns |
|----------|-------|---------|
| Identifiers | 4 | fips, county_name, latitude, longitude |
| Demographics | 9 | total_population, median_income, poverty_count, poverty_pct, elderly_population, elderly_pct, disability_count, disability_pct, uninsured_count, uninsured_pct |
| Infrastructure Distance | 12 | dist_nearest_* (4), dist_2nd_nearest_* (4), count_*_50km (4) |
| Infrastructure Density | 4 | density_*_per10k (4) |
| Disaster History | 7 | disaster_count, disaster_count_recent, disaster_flood, disaster_severe_storms, disaster_hurricane, disaster_fire, disaster_tornado |
| Composite Indices | 4 | vulnerability_index, isolation_index, risk_score, risk_level |
| **Advanced Features** | **26** | See below |
| **Total** | **66** | |

### Advanced Features Breakdown (26)

| Category | Count | Columns |
|----------|-------|---------|
| Compound Risk Clusters | 2 | compound_risk_count, compound_risk_flag |
| Risk Contagion | 2 | neighbor_avg_risk, risk_contagion_delta |
| Temporal Disaster Acceleration | 3 | disaster_acceleration, disasters_2015_2025, disasters_2005_2014 |
| Infrastructure Redundancy | 2 | redundancy_score, zero_redundancy_flag |
| Population-Weighted Vulnerability | 4 | pop_weighted_vulnerability, pop_weighted_vulnerability_norm, pop_weighted_risk, pop_weighted_risk_norm |
| State-Level Rankings | 5 | state_fips, counties_in_state, risk_score_state_pctile, vulnerability_index_state_pctile, isolation_index_state_pctile |
| Gap Analysis Matrix | 7 | gap_hospital, gap_ems, gap_fire, gap_poverty, gap_disaster_prep, top_intervention, top_intervention_score |
| State Context | 1 | state_fips (also used for rankings) |

*Note: The infrastructure distance section already includes the 4 `dist_2nd_nearest_*` columns (8 total distance columns: 4 nearest + 4 2nd nearest).*
