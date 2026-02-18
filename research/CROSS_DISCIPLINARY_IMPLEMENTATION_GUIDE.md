# Cross-Disciplinary Analysis Implementation Quick Reference

**Technical Vocabulary & Code Snippets for Claude Code Implementation**

---

## Methodology 1: CDC SVI Implementation

### Technical Vocabulary
- **Percentile Ranking**: `rank(pct=True)` - NOT min-max normalization
- **Thematic Aggregation**: Sum ranks within 4 themes, then rerank
- **Overall SVI**: Sum of theme rankings, percentile ranked
- **Ties**: Use `method='min'` for lower-is-better ranking

### Code Skeleton
```python
def calculate_cdc_svi(df):
    """CDC SVI uses percentile ranking, not min-max normalization."""
    
    # Theme 1: Socioeconomic
    theme1_vars = ['poverty_pct', 'unemployment_pct', 'no_highschool_pct', 'low_income_pct']
    for var in theme1_vars:
        df[f'{var}_rank'] = df[var].rank(pct=True, method='min')
    df['theme1_sum'] = df[[f'{v}_rank' for v in theme1_vars]].sum(axis=1)
    df['theme1_rank'] = df['theme1_sum'].rank(pct=True, method='min')
    
    # Repeat for themes 2-4...
    
    # Overall SVI
    df['svi_score'] = df[['theme1_rank', 'theme2_rank', 'theme3_rank', 'theme4_rank']].sum(axis=1)
    df['svi_percentile'] = df['svi_score'].rank(pct=True, method='min')
    
    return df
```

### Census Variables to Add
```python
ADDITIONAL_SVI_VARS = [
    "B23025_005E",  # Unemployed
    "B15003_002E",  # No high school diploma
    "B09001_001E",  # Population under 18
    "B11012_003E,B11012_014E",  # Single parent households
    "B03002_003E",  # White alone
    "C16002_004E,C16002_007E,C16002_010E,C16002_013E",  # Limited English
    "B25024_003E,B25024_004E",  # Multi-unit structures
    "B25024_010E",  # Mobile homes
    "B25014_005E,B25014_006E,B25014_007E",  # Crowding
    "B08201_002E",  # No vehicle
    "B26001_001E",  # Group quarters
]
```

---

## Methodology 2: FEMA NRI EAL Integration

### Technical Vocabulary
- **EAL**: Expected Annual Loss in dollars (highly right-skewed)
- **EALT**: Total EAL (property + population + agriculture)
- **Risk Rating**: Very Low/Low/Moderate/High/Very High
- **Log Transformation**: Use `np.log1p()` for EAL normalization

### Code Skeleton
```python
def calculate_eal_features(df, nri_df):
    """Integrate FEMA NRI Expected Annual Loss data."""
    
    # Join NRI data
    df = df.merge(nri_df[['STCOFIPS', 'EAL_VALT', 'EAL_RATNG']], 
                  left_on='fips', right_on='STCOFIPS', how='left')
    
    # Log transform due to extreme skew
    df['eal_log'] = np.log1p(df['EAL_VALT'].fillna(0))
    
    # EAL per capita
    df['eal_per_capita'] = df['EAL_VALT'] / df['total_population'].replace(0, np.nan)
    
    # Find dominant hazard
    hazard_cols = [f'{code}_EALT' for code in HAZARD_CODES.keys()]
    df['dominant_hazard'] = df[hazard_cols].idxmax(axis=1).str.replace('_EALT', '')
    
    # NRI composite risk
    df['nri_composite_risk'] = (
        np.log1p(df['EAL_VALT']) * df['svi_percentile'] / 
        (df.get('resilience_score', 0.5) + 0.1)
    )
    
    return df
```

### Hazard Codes Reference
```python
HAZARD_CODES = {
    "AVLN": "Avalanche", "CFLD": "Coastal Flooding", "CWAV": "Cold Wave",
    "DRGT": "Drought", "ERQK": "Earthquake", "HAIL": "Hail",
    "HWAV": "Heat Wave", "HRCN": "Hurricane", "ISTM": "Ice Storm",
    "LNDS": "Landslide", "LTNG": "Lightning", "RFLD": "Riverine Flooding",
    "SWND": "Strong Wind", "TRND": "Tornado", "TSUN": "Tsunami",
    "VLCN": "Volcanic Activity", "WFIR": "Wildfire", "WNTW": "Winter Weather"
}
```

---

## Methodology 3: Getis-Ord Gi* Hotspot Analysis

### Technical Vocabulary
- **Gi***: Getis-Ord statistic for local spatial clustering
- **Z-score**: Standardized Gi* value for significance testing
- **P-value**: < 0.05 = significant hotspot/coldspot
- **Distance Band**: Neighborhood radius (typically 50-100km for counties)

### Code Skeleton
```python
from esda import G_Local
from scipy.spatial.distance import cdist

def calculate_getis_ord_gi(df, variable='risk_score', distance_km=100):
    """Calculate Getis-Ord Gi* hotspot statistics."""
    
    coords = np.radians(df[['latitude', 'longitude']].values)
    y = df[variable].values
    
    # Haversine distance matrix
    R = 6371
    dist_matrix = R * np.arccos(np.clip(
        np.sin(coords[:, 0])[:, None] * np.sin(coords[:, 0]) +
        np.cos(coords[:, 0])[:, None] * np.cos(coords[:, 0]) * 
        np.cos(coords[:, 1][:, None] - coords[:, 1]), -1, 1))
    
    # Binary weights matrix
    w = (dist_matrix <= distance_km).astype(float)
    np.fill_diagonal(w, 0)
    
    # Calculate Gi* using esda
    gi = G_Local(y, w, star=True)
    
    df['gi_star'] = gi.Zs
    df['gi_pvalue'] = gi.p_sim
    
    # Classify hotspots
    df['hotspot_class'] = 'Not significant'
    df.loc[(df['gi_star'] >= 2.58) & (df['gi_pvalue'] < 0.01), 'hotspot_class'] = 'Hotspot (99%)'
    df.loc[(df['gi_star'] >= 1.96) & (df['gi_star'] < 2.58) & (df['gi_pvalue'] < 0.05), 'hotspot_class'] = 'Hotspot (95%)'
    df.loc[(df['gi_star'] <= -2.58) & (df['gi_pvalue'] < 0.01), 'hotspot_class'] = 'Coldspot (99%)'
    df.loc[(df['gi_star'] <= -1.96) & (df['gi_star'] > -2.58) & (df['gi_pvalue'] < 0.05), 'hotspot_class'] = 'Coldspot (95%)'
    
    return df
```

### Dependencies
```bash
pip install esda pointpats libpysal
```

---

## Methodology 4: Heat-Mortality ERF

### Technical Vocabulary
- **ERF**: Exposure-Response Function (relationship between exposure and outcome)
- **RR**: Relative Risk = exp(β × exposure)
- **T_ref**: Reference temperature (minimum mortality temperature, ~75-80°F)
- **AF**: Attributable Fraction = (RR - 1) / RR

### Code Skeleton
```python
def calculate_heat_mortality_risk(df, climate_df, beta=0.005, t_ref=80):
    """Calculate temperature-attributable mortality."""
    
    # Join climate data
    df = df.merge(climate_df[['fips', 'max_temp_f_summer']], on='fips', how='left')
    
    # Calculate relative risk for days above threshold
    temp_excess = np.maximum(0, df['max_temp_f_summer'] - t_ref)
    df['heat_rr'] = np.exp(beta * temp_excess)
    
    # Attributable fraction
    df['heat_af'] = (df['heat_rr'] - 1) / df['heat_rr']
    
    # Get baseline mortality (CDC WONDER or approximation)
    baseline_mortality = 850  # per 100,000 per year (US average)
    df['baseline_deaths'] = df['total_population'] * baseline_mortality / 100000
    
    # Attributable deaths
    df['heat_deaths_est'] = df['baseline_deaths'] * df['heat_af']
    
    # Vulnerability weighting
    df['heat_vulnerability'] = (
        df['elderly_pct'] * 3.5 +  # Age 65+ has 3.5× risk
        df['poverty_pct'] * 1.5 +   # Poverty multiplier
        (1 - df.get('ac_ownership_pct', 0.7)) * 2.0  # No AC multiplier
    ) / 7.0  # Normalize to 0-1
    
    df['heat_mortality_risk'] = df['heat_deaths_est'] * df['heat_vulnerability']
    
    return df
```

### CDC WONDER API Pattern
```python
def fetch_cdc_wonder_mortality(state_fips, county_fips):
    """Fetch age-adjusted death rates from CDC WONDER."""
    # CDC WONDER uses a form-based API - use direct download or scraping
    # Alternatively, use pre-downloaded county mortality rates
    url = "https://wonder.cdc.gov/controller/saved/D134/D278F067"
    # Implementation depends on CDC WONDER API access method
    pass
```

---

## Methodology 5: Joplin Economic Loss Model

### Technical Vocabulary
- **Direct Loss**: Immediate physical damage
- **Indirect Loss**: Business interruption, supply chain, downstream effects
- **Multiplier**: Indirect/Direct ratio (typically 1.5-3.0)
- **BCR**: Benefit-Cost Ratio

### Code Skeleton
```python
def calculate_joplin_economic_impact(df, bea_gdp_df):
    """Calculate indirect economic losses using Joplin multipliers."""
    
    # Sector multipliers from Joplin, MO study
    SECTOR_MULTIPLIERS = {
        'healthcare': 1.8,
        'manufacturing': 2.2,
        'retail': 1.6,
        'agriculture': 2.5,
        'services': 1.4,
        'government': 1.2
    }
    
    # Join GDP data
    df = df.merge(bea_gdp_df[['fips', 'gdp_2022', 'dominant_sector']], on='fips', how='left')
    
    # Get direct loss from FEMA NRI
    df['direct_loss'] = df['EAL_VALT'].fillna(0)
    
    # Apply sector-specific multiplier
    df['sector_multiplier'] = df['dominant_sector'].map(SECTOR_MULTIPLIERS).fillna(1.8)
    
    # Regional adjustment (rural areas have higher multipliers)
    df['regional_multiplier'] = np.where(
        df['total_population'] < 50000, 2.5,
        np.where(df['total_population'] < 200000, 2.0, 1.5)
    )
    
    # Calculate indirect loss
    df['indirect_loss'] = df['direct_loss'] * (df['sector_multiplier'] - 1) * df['regional_multiplier']
    
    # Business interruption (90 days for moderate events)
    df['daily_gdp'] = df['gdp_2022'] / 365
    df['bi_loss'] = df['daily_gdp'] * 90 * (df['disaster_count'] > 0).astype(float)
    
    df['total_economic_impact'] = df['direct_loss'] + df['indirect_loss'] + df['bi_loss']
    
    # Normalize to GDP
    df['economic_vulnerability'] = df['total_economic_impact'] / (df['gdp_2022'] + 1)
    
    return df
```

---

## Methodology 6: IRS Migration Flow Analysis

### Technical Vocabulary
- **Net Migration**: In-migration - Out-migration
- **Migration Rate**: Net migration / Base population
- **Brain Drain**: Net outflow of high-AGI households
- **Climate Migration**: Movement to lower-risk areas

### Code Skeleton
```python
def calculate_migration_risk_impact(df, migration_df):
    """Calculate population dynamics from IRS SOI migration data."""
    
    # Migration data structure
    # Columns: fips, inflow_returns, inflow_exemptions, inflow_agi,
    #          outflow_returns, outflow_exemptions, outflow_agi
    
    df = df.merge(migration_df, on='fips', how='left')
    
    # Net migration
    df['net_migration'] = df['inflow_exemptions'] - df['outflow_exemptions']
    df['net_migration_rate'] = df['net_migration'] / df['total_population']
    
    # Adjust for undercount (IRS misses ~15% of population)
    df['adjusted_net_migration'] = df['net_migration'] * 1.15
    
    # Brain drain (high-AGI households leaving)
    avg_agi_in = df['inflow_agi'] / df['inflow_returns'].replace(0, np.nan)
    avg_agi_out = df['outflow_agi'] / df['outflow_returns'].replace(0, np.nan)
    df['brain_drain_index'] = (avg_agi_out - avg_agi_in) / 1000  # in thousands
    
    # Climate migration indicator (migration to low-risk counties)
    risk_percentile = df['risk_score'].rank(pct=True)
    df['climate_migration_destination'] = (risk_percentile < 0.2) & (df['net_migration'] > 0)
    
    # Adjusted population for risk calculations
    df['migration_adjusted_population'] = df['total_population'] + df['adjusted_net_migration']
    
    # Project 5-year trend
    df['projected_2030_population'] = df['total_population'] + (df['adjusted_net_migration'] * 5)
    
    return df
```

### IRS SOI Data Download
```bash
# Download IRS migration data
wget https://www.irs.gov/pub/irs-soi/countyinflow2021.csv
wget https://www.irs.gov/pub/irs-soi/countyoutflow2021.csv
```

---

## Methodology 7: Infrastructure Interdependency

### Technical Vocabulary
- **Multi-Layer Network**: Separate layers for each infrastructure type
- **Cross-Layer Edges**: Dependencies between sectors
- **Cascade**: Propagation of failures across layers
- **Betweenness Centrality**: Bottleneck identification

### Code Skeleton
```python
def calculate_interdependency_risk(network, county_fips):
    """Calculate critical infrastructure interdependency risk."""
    
    # Interdependency weights (dependency strength)
    INTERDEPENDENCY = {
        ('power', 'water'): 0.9,      # Pumps need electricity
        ('power', 'communications'): 0.7,
        ('power', 'healthcare'): 0.95,  # Hospitals critical
        ('water', 'healthcare'): 0.8,
        ('communications', 'power'): 0.4,
        ('communications', 'water'): 0.3,
        ('communications', 'healthcare'): 0.85,
    }
    
    # Build multi-layer graph
    G = nx.Graph()
    
    # Add nodes for each sector
    for sector in ['power', 'water', 'communications', 'healthcare']:
        facilities = network.get_facilities(sector, county_fips)
        for i, fac in facilities.iterrows():
            G.add_node(f"{sector}_{i}", 
                      sector=sector,
                      capacity=fac.get('capacity', 100),
                      lon=fac['longitude'],
                      lat=fac['latitude'])
    
    # Add intra-layer edges (physical proximity)
    for sector in ['power', 'water', 'communications', 'healthcare']:
        sector_nodes = [n for n, d in G.nodes(data=True) if d['sector'] == sector]
        for i, n1 in enumerate(sector_nodes):
            for n2 in sector_nodes[i+1:]:
                dist = haversine_km(
                    G.nodes[n1]['lat'], G.nodes[n1]['lon'],
                    G.nodes[n2]['lat'], G.nodes[n2]['lon']
                )
                if dist < 50:  # km
                    G.add_edge(n1, n2, weight=dist, type='intra')
    
    # Add inter-layer edges (dependencies)
    for (s1, s2), weight in INTERDEPENDENCY.items():
        nodes_1 = [n for n, d in G.nodes(data=True) if d['sector'] == s1]
        nodes_2 = [n for n, d in G.nodes(data=True) if d['sector'] == s2]
        for n1 in nodes_1:
            for n2 in nodes_2:
                G.add_edge(n1, n2, weight=1/weight, type='inter', dependency=weight)
    
    # Calculate metrics
    betweenness = nx.betweenness_centrality(G, weight='weight')
    articulation = list(nx.articulation_points(G))
    
    # Find cross-sector bottlenecks
    cross_sector_betweenness = {}
    for node, cent in betweenness.items():
        if any(G.edges[e].get('type') == 'inter' for e in G.edges(node)):
            cross_sector_betweenness[node] = cent
    
    # Simulate cascade from worst-case failure
    critical_node = max(cross_sector_betweenness, key=cross_sector_betweenness.get)
    affected = simulate_cascade(G, critical_node)
    
    return {
        'interdependency_score': len(articulation) / G.number_of_nodes(),
        'cascade_affected_nodes': len(affected),
        'critical_cross_sector_nodes': list(cross_sector_betweenness.keys())[:5],
        'single_points_of_failure': articulation
    }
```

---

## Methodology 8: Mobile Home Vulnerability Multiplier

### Technical Vocabulary
- **Mobile Home Risk Ratio**: 15-20× for tornado, 4-10× for flood
- **Housing Vulnerability Multiplier**: Composite risk amplification
- **Foundation Type**: Anchored vs unanchored (critical for wind)

### Code Skeleton
```python
def calculate_mobile_home_vulnerability(df):
    """Calculate mobile home vulnerability multipliers."""
    
    # National average mobile home percentage
    NATIONAL_MH_PCT = 6.5
    
    # Risk ratios by hazard (from research)
    RISK_RATIOS = {
        'tornado': 15.0,
        'flood': 7.0,
        'hurricane': 4.0,
        'wind': 3.0,
        'fire': 1.5
    }
    
    # Calculate mobile home percentage
    df['mobile_home_pct'] = (df['mobile_home_units'] / df['total_housing_units']) * 100
    
    # Ratio to national average
    df['mobile_home_ratio'] = df['mobile_home_pct'] / NATIONAL_MH_PCT
    
    # Get dominant hazard from NRI
    dominant_hazard = df.get('dominant_hazard', 'flood')
    
    # Calculate hazard-specific multiplier
    base_ratio = RISK_RATIOS.get(dominant_hazard, 2.0)
    
    # Apply with diminishing returns
    df['housing_vulnerability_multiplier'] = 1 + (
        np.minimum(df['mobile_home_ratio'], 3.0) * (base_ratio / 20)
    )
    
    # Tornado-specific fatality risk
    if dominant_hazard == 'tornado':
        df['tornado_fatality_risk'] = (
            df['total_population'] * 
            df['mobile_home_pct'] / 100 * 
            0.001  # 0.1% fatality rate in direct hit
        )
    
    # Adjust overall risk score
    df['risk_score_adjusted'] = df['risk_score'] * df['housing_vulnerability_multiplier']
    
    return df
```

---

## Methodology 9: CEJST Cumulative Impact

### Technical Vocabulary
- **Burden Category**: Environmental or climate stressor
- **90th Percentile Threshold**: Indicator exceeds 90% of US
- **Disadvantaged Community**: >=2 burdens + socioeconomic criteria
- **Cumulative Impact**: Combined effect of multiple stressors

### Code Skeleton
```python
def calculate_cumulative_impact_score(df, ejscreen_df):
    """Calculate CEJST-style cumulative impact score."""
    
    # Merge EJSCREEN data
    df = df.merge(ejscreen_df, on='fips', how='left')
    
    # Define burden indicators with 90th percentile thresholds
    BURDENS = {
        'climate_burden': [
            ('flood_risk', 0.90),
            ('wildfire_risk', 0.90),
            ('extreme_heat_days', 0.90)
        ],
        'energy_burden': [
            ('energy_cost_burden', 0.90),
            ('pm25_exposure', 0.90)
        ],
        'transportation_burden': [
            ('diesel_pm_exposure', 0.90),
            ('traffic_proximity', 0.90)
        ],
        'housing_burden': [
            ('lead_paint_indicator', 0.90),
            ('historic_underinvestment', 0.90)
        ],
        'health_burden': [
            ('asthma_rate', 0.90),
            ('diabetes_rate', 0.90),
            ('heart_disease_rate', 0.90),
            ('low_life_expectancy', 0.90)
        ]
    }
    
    # Calculate 90th percentiles
    burden_count = 0
    for category, indicators in BURDENS.items():
        category_burden = 0
        for indicator, threshold_pct in indicators:
            if indicator in df.columns:
                threshold = df[indicator].quantile(threshold_pct)
                df[f'{indicator}_burden'] = (df[indicator] >= threshold).astype(int)
                category_burden += df[f'{indicator}_burden']
        
        # Category has burden if any indicator exceeds threshold
        df[f'{category}_flag'] = (category_burden > 0).astype(int)
        burden_count += df[f'{category}_flag']
    
    df['burden_category_count'] = burden_count
    
    # Socioeconomic criteria
    df['low_income_flag'] = (
        (df['poverty_pct'] > 20) | 
        (df['median_income'] < df['median_income'].quantile(0.20))
    ).astype(int)
    
    df['high_svi_flag'] = (df['svi_percentile'] > 0.75).astype(int)
    df['socioeconomic_flag'] = (df['low_income_flag'] | df['high_svi_flag']).astype(int)
    
    # CEJST disadvantaged classification
    df['cejst_disadvantaged'] = (
        (df['burden_category_count'] >= 2) & 
        df['socioeconomic_flag']
    ).astype(int)
    
    # Cumulative impact score
    df['cumulative_impact_score'] = (
        df['burden_category_count'] / 6 * 0.5 + 
        df['svi_percentile'] * 0.5
    )
    
    return df
```

---

## Methodology 10: Flood-Mental Health Impact

### Technical Vocabulary
- **PTSD Prevalence**: 15-30% at 6 months post-flood
- **Risk Factor Multipliers**: Displacement, income loss, prior trauma
- **Attributable Cases**: Population × prevalence × risk factors

### Code Skeleton
```python
def calculate_flood_mental_health_burden(df, fema_ia_df):
    """Calculate flood-attributable mental health burden."""
    
    # Prevalence rates by time since flood
    PREVALENCE = {
        'ptsd': {
            '6_months': 0.225,   # 15-30% range
            '1_year': 0.15,
            '2_years': 0.075
        },
        'depression': {
            '6_months': 0.30,
            '1_year': 0.225,
            '2_years': 0.125
        },
        'anxiety': {
            '6_months': 0.375,
            '1_year': 0.25
        }
    }
    
    # Risk factor multipliers
    RISK_FACTORS = {
        'displacement': 2.0,
        'income_loss': 1.8,
        'prior_trauma': 1.5,
        'social_isolation': 1.7,
        'repeat_flooding': 1.4
    }
    
    # Get affected population from FEMA Individual Assistance
    df = df.merge(fema_ia_df[['fips', 'ia_registrations', 'flood_events_5yr']], 
                  on='fips', how='left')
    
    affected_pop = df['ia_registrations'].fillna(0)
    
    # Calculate base prevalence (weighted by time since events)
    recent_events = df['flood_events_5yr'].fillna(0)
    
    # Assume average 2 years since most recent flood for calculation
    base_ptsd_rate = PREVALENCE['ptsd']['2_years']
    base_depression_rate = PREVALENCE['depression']['2_years']
    
    # Apply risk factors
    risk_multiplier = (
        1.0 +
        (df['poverty_pct'] / 100) * (RISK_FACTORS['income_loss'] - 1) +
        df['disability_pct'] / 100 * (RISK_FACTORS['prior_trauma'] - 1)
    )
    
    # Calculate attributable cases
    df['ptsd_cases_est'] = affected_pop * base_ptsd_rate * risk_multiplier
    df['depression_cases_est'] = affected_pop * base_depression_rate * risk_multiplier
    
    # Treatment cost estimate ($5,000 per case per year)
    TREATMENT_COST = 5000
    df['mh_treatment_cost_est'] = (
        (df['ptsd_cases_est'] + df['depression_cases_est']) * TREATMENT_COST
    )
    
    # Mental health burden index
    df['mental_health_burden_score'] = (
        (df['ptsd_cases_est'] + df['depression_cases_est']) / 
        df['total_population'].replace(0, np.nan)
    ).clip(0, 1)
    
    return df
```

---

## Methodology 11: 2SFCA Healthcare Accessibility

### Technical Vocabulary
- **2SFCA**: Two-Step Floating Catchment Area method
- **Supply**: Hospital beds, physicians, specialists
- **Demand**: Population within catchment
- **Distance Decay**: f(d) = exp(-β × d)

### Code Skeleton
```python
def calculate_2sfca_accessibility(df, facilities_df, beta=-0.03, max_dist=100):
    """Calculate healthcare accessibility using 2SFCA method."""
    
    coords = df[['latitude', 'longitude']].values
    fac_coords = facilities_df[['latitude', 'longitude']].values
    
    # Distance matrix (km)
    dist_matrix = cdist(np.radians(coords), np.radians(fac_coords)) * 6371
    
    # Distance decay weights
    weights = np.exp(beta * dist_matrix)
    weights[dist_matrix > max_dist] = 0
    
    # Step 1: Calculate provider-to-population ratio (R_j)
    # R_j = S_j / Σ_k P_k * f(d_kj)
    
    facility_supply = facilities_df['beds'].values  # or physicians, ICU beds
    population = df['total_population'].values
    
    # For each facility, calculate catchment population
    catchment_pop = np.zeros(len(facilities_df))
    for j in range(len(facilities_df)):
        for i in range(len(df)):
            catchment_pop[j] += population[i] * weights[i, j]
    
    # Provider-to-population ratio
    R = facility_supply / (catchment_pop + 1)  # Add 1 to avoid division by zero
    
    # Step 2: Calculate accessibility (A_i)
    # A_i = Σ_j R_j * f(d_ij)
    
    accessibility = np.zeros(len(df))
    for i in range(len(df)):
        for j in range(len(facilities_df)):
            accessibility[i] += R[j] * weights[i, j]
    
    df['healthcare_accessibility'] = accessibility
    
    # Normalize (higher = better access)
    df['healthcare_accessibility_norm'] = (
        (accessibility - accessibility.min()) / 
        (accessibility.max() - accessibility.min())
    )
    
    # Vulnerability-weighted accessibility (lower = worse access for vulnerable)
    df['vulnerability_weighted_access'] = (
        df['healthcare_accessibility_norm'] / 
        (df['svi_percentile'] + 0.1)
    )
    
    # Access gap (inverse)
    df['healthcare_access_gap'] = 1 - df['healthcare_accessibility_norm']
    
    return df
```

---

## Methodology 12: Compound Hazard Risk

### Technical Vocabulary
- **Compound Event**: Co-occurring hazards with multiplicative effect
- **Interaction Multiplier**: Risk amplification factor
- **Temporal Clustering**: Multiple events in short time window
- **Disaster Sequence**: Cascading failures from compound events

### Code Skeleton
```python
def calculate_compound_hazard_risk(df, disaster_history_df):
    """Calculate compound event risk with interaction multipliers."""
    
    # Compound hazard pairs with interaction multipliers
    COMPOUND_PAIRS = {
        ('drought', 'heat_wave'): {
            'multiplier': 2.5,
            'effect': 'wildfire_risk'
        },
        ('flood', 'power_outage'): {
            'multiplier': 3.0,
            'effect': 'health_impact'
        },
        ('hurricane', 'pandemic'): {
            'multiplier': 2.0,
            'effect': 'evacuation_difficulty'
        },
        ('extreme_cold', 'power_outage'): {
            'multiplier': 4.0,
            'effect': 'mortality'
        },
        ('wildfire', 'heat_wave'): {
            'multiplier': 1.5,
            'effect': 'respiratory_mortality'
        }
    }
    
    # Get hazard probabilities from NRI
    hazard_probs = {}
    for hazard in ['flood', 'drought', 'heat_wave', 'hurricane', 'wildfire']:
        hazard_probs[hazard] = df.get(f'{hazard}_annual_freq', 0.1)
    
    # Calculate compound risk for each pair
    compound_risks = []
    for (h1, h2), info in COMPOUND_PAIRS.items():
        if h1 in hazard_probs and h2 in hazard_probs:
            # P(compound) ≈ P(H1) * P(H2|H1) - simplified as P1 * P2 * correlation
            correlation = 0.3 if (h1 == 'drought' and h2 == 'heat_wave') else 0.1
            p_compound = hazard_probs[h1] * hazard_probs[h2] * correlation
            
            # Impact with multiplier
            max_impact = max(
                df.get(f'{h1}_risk_score', 0.5),
                df.get(f'{h2}_risk_score', 0.5)
            )
            impact = max_impact * info['multiplier']
            
            compound_risks.append(p_compound * impact)
    
    df['compound_hazard_risk'] = sum(compound_risks) if compound_risks else 0
    
    # Temporal clustering - disasters within 90 days
    df['disaster_sequences'] = count_disaster_sequences(disaster_history_df, window_days=90)
    df['sequence_risk_multiplier'] = 1 + (df['disaster_sequences'] * 0.2)
    
    # Adjust overall risk
    df['compound_adjusted_risk'] = df['risk_score'] * df['sequence_risk_multiplier']
    
    return df


def count_disaster_sequences(disaster_df, window_days=90):
    """Count sequences of disasters within time window."""
    disaster_df = disaster_df.sort_values('declarationDate')
    disaster_df['date'] = pd.to_datetime(disaster_df['declarationDate'])
    
    sequences = 0
    for fips in disaster_df['fips'].unique():
        county_disasters = disaster_df[disaster_df['fips'] == fips]
        if len(county_disasters) < 2:
            continue
        
        dates = county_disasters['date'].values
        for i in range(len(dates) - 1):
            if (dates[i+1] - dates[i]).days <= window_days:
                sequences += 1
    
    return sequences
```

---

## Common Utilities

### Haversine Distance
```python
def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))
```

### Percentile Ranking
```python
def percentile_rank(series):
    """Calculate percentile ranking (0-1, 1 = highest)."""
    return series.rank(pct=True, method='min')
```

### Mann-Kendall Trend Test
```python
from pymannkendall import original_test

def trend_direction(series):
    """Return trend direction using Mann-Kendall test."""
    result = original_test(series)
    if result.p < 0.05:
        return 'increasing' if result.z > 0 else 'decreasing'
    return 'stable'
```

---

## File Structure

```
src/
├── feature_engineering.py      # Add SVI, mobile home features
├── climate_client.py           # Extend NRI integration
├── spatial_stats.py            # Gi* hotspot analysis
├── health_impact.py            # Heat mortality, mental health (NEW)
├── health_access.py            # 2SFCA accessibility (NEW)
├── economic_impact.py          # Joplin model (NEW)
├── population_dynamics.py      # Migration analysis (NEW)
├── equity_analysis.py          # CEJST cumulative impact (NEW)
├── compound_risk.py            # Compound hazards (NEW)
└── network_analysis.py         # Extend with interdependency
```

---

## Dependencies

```
# Add to requirements.txt
esda>=2.4.0
pointpats>=2.2.0
libpysal>=4.7.0
pymannkendall>=1.4.3
```

---

*Implementation Guide for ResilienceAI Cross-Disciplinary Analysis*
