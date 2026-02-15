# ResilienceAI - Data Dictionary

## Processed Dataset: `data/processed/county_features.csv`

3,222 US counties | 37 columns | All real federal data

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
