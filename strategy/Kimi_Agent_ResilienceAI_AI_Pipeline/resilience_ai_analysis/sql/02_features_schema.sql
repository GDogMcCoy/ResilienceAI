-- ============================================
-- RESILIENCEAI FEATURES SCHEMA
-- Normalized Feature Definitions and Values
-- ============================================

-- ============================================
-- FEATURE CATEGORIES
-- ============================================

CREATE TABLE IF NOT EXISTS feature_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    domain VARCHAR(20) NOT NULL CHECK (domain IN ('climate', 'health', 'infrastructure', 'socioeconomic', 'agriculture', 'composite')),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default categories
INSERT INTO feature_categories (category_name, description, domain, display_order) VALUES
    ('Climate & Disasters', 'Climate vulnerability and disaster history metrics', 'climate', 1),
    ('Health Infrastructure', 'Healthcare facility access and health indicators', 'health', 2),
    ('Emergency Services', 'Fire, EMS, and emergency response infrastructure', 'infrastructure', 3),
    ('Socioeconomic', 'Economic and social vulnerability indicators', 'socioeconomic', 4),
    ('Agriculture', 'Agricultural vulnerability and farm metrics', 'agriculture', 5),
    ('Composite Risk', 'Combined risk scores and indices', 'composite', 6)
ON CONFLICT (category_name) DO NOTHING;

-- ============================================
-- FEATURE DEFINITIONS
-- ============================================

CREATE TABLE IF NOT EXISTS feature_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feature_key VARCHAR(100) UNIQUE NOT NULL,        -- Machine name (e.g., 'disaster_count')
    display_name VARCHAR(200) NOT NULL,               -- Human-readable name
    description TEXT,
    category_id INTEGER REFERENCES feature_categories(id),
    
    -- Data type and units
    data_type VARCHAR(20) NOT NULL CHECK (data_type IN ('integer', 'float', 'percentage', 'count', 'distance', 'currency', 'ratio')),
    unit VARCHAR(50),                                  -- e.g., 'km', '%', 'USD', 'count'
    precision_digits INTEGER DEFAULT 2,               -- Decimal places for display
    
    -- Value ranges for validation
    min_value DECIMAL(20, 8),
    max_value DECIMAL(20, 8),
    
    -- Source tracking
    data_source VARCHAR(100),                          -- e.g., 'FEMA', 'CDC', 'Census', 'HRSA'
    source_url TEXT,
    update_frequency VARCHAR(20),                      -- 'daily', 'weekly', 'monthly', 'yearly', 'on_demand'
    
    -- Metadata
    is_calculated BOOLEAN DEFAULT FALSE,              -- Derived from other features?
    calculation_formula TEXT,                          -- If calculated, store formula
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on feature_key for fast lookups
CREATE INDEX IF NOT EXISTS idx_feature_definitions_key ON feature_definitions(feature_key);
CREATE INDEX IF NOT EXISTS idx_feature_definitions_category ON feature_definitions(category_id);
CREATE INDEX IF NOT EXISTS idx_feature_definitions_domain ON feature_definitions(domain);

-- ============================================
-- COUNTY FEATURE VALUES (Current Snapshot)
-- ============================================

CREATE TABLE IF NOT EXISTS county_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    county_id UUID NOT NULL REFERENCES counties(id) ON DELETE CASCADE,
    feature_id UUID NOT NULL REFERENCES feature_definitions(id) ON DELETE CASCADE,
    
    -- Value storage (flexible for different types)
    numeric_value DECIMAL(20, 8),
    text_value TEXT,
    json_value JSONB,
    
    -- Data quality
    confidence_score DECIMAL(3, 2) DEFAULT 1.0,       -- 0.0 to 1.0
    data_quality_flags TEXT[],                        -- Array of quality issues
    
    -- Timestamps
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_county_feature_date UNIQUE (county_id, feature_id, effective_date),
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Indexes for county features
CREATE INDEX IF NOT EXISTS idx_county_features_county ON county_features(county_id);
CREATE INDEX IF NOT EXISTS idx_county_features_feature ON county_features(feature_id);
CREATE INDEX IF NOT EXISTS idx_county_features_date ON county_features(effective_date);
CREATE INDEX IF NOT EXISTS idx_county_features_value ON county_features(numeric_value) WHERE numeric_value IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_county_features_json ON county_features USING GIN(json_value);

-- Composite index for common query pattern
CREATE INDEX IF NOT EXISTS idx_county_features_county_feature ON county_features(county_id, feature_id, effective_date DESC);

-- ============================================
-- FEATURE DEFINITIONS - RESILIENCEAI 66 FEATURES
-- ============================================

-- Climate & Disasters Features
INSERT INTO feature_definitions (feature_key, display_name, description, category_id, data_type, unit, data_source) VALUES
    ('disaster_count', 'Total Disaster Count', 'Total number of disaster declarations', 1, 'count', 'count', 'FEMA'),
    ('disaster_flood', 'Flood Disasters', 'Number of flood-related disaster declarations', 1, 'count', 'count', 'FEMA'),
    ('disaster_severe_storms', 'Severe Storm Disasters', 'Number of severe storm disaster declarations', 1, 'count', 'count', 'FEMA'),
    ('disaster_hurricane', 'Hurricane Disasters', 'Number of hurricane-related disaster declarations', 1, 'count', 'count', 'FEMA'),
    ('disaster_fire', 'Fire Disasters', 'Number of fire-related disaster declarations', 1, 'count', 'count', 'FEMA'),
    ('disaster_tornado', 'Tornado Disasters', 'Number of tornado disaster declarations', 1, 'count', 'count', 'FEMA'),
    ('disaster_count_recent', 'Recent Disaster Count', 'Disaster count in last 5 years', 1, 'count', 'count', 'FEMA'),
    ('disasters_2015_2025', 'Disasters 2015-2025', 'Disaster count from 2015-2025', 1, 'count', 'count', 'FEMA'),
    ('disasters_2005_2014', 'Disasters 2005-2014', 'Disaster count from 2005-2014', 1, 'count', 'count', 'FEMA'),
    ('disaster_acceleration', 'Disaster Acceleration', 'Rate of increase in disaster frequency', 1, 'ratio', 'ratio', 'Calculated')
ON CONFLICT (feature_key) DO NOTHING;

-- Health Infrastructure Features
INSERT INTO feature_definitions (feature_key, display_name, description, category_id, data_type, unit, data_source) VALUES
    ('elderly_pct', 'Elderly Population %', 'Percentage of population aged 65+', 2, 'percentage', '%', 'Census'),
    ('disability_pct', 'Disability %', 'Percentage of population with disabilities', 2, 'percentage', '%', 'Census'),
    ('uninsured_pct', 'Uninsured %', 'Percentage of population without health insurance', 2, 'percentage', '%', 'Census'),
    ('dist_nearest_hospitals_km', 'Distance to Nearest Hospital', 'Distance to nearest hospital in km', 2, 'distance', 'km', 'HRSA'),
    ('dist_2nd_nearest_hospitals_km', 'Distance to 2nd Nearest Hospital', 'Distance to second nearest hospital', 2, 'distance', 'km', 'HRSA'),
    ('count_hospitals_50km', 'Hospitals within 50km', 'Count of hospitals within 50km radius', 2, 'count', 'count', 'HRSA'),
    ('density_hospitals_per10k', 'Hospital Density', 'Hospitals per 10,000 population', 2, 'ratio', 'per 10k', 'Calculated'),
    ('dist_nearest_nursing_homes_km', 'Distance to Nursing Home', 'Distance to nearest nursing home', 2, 'distance', 'km', 'CMS'),
    ('density_nursing_homes_per10k', 'Nursing Home Density', 'Nursing homes per 10,000 population', 2, 'ratio', 'per 10k', 'Calculated'),
    ('hospital_bed_count', 'Hospital Bed Count', 'Total hospital beds in county', 2, 'count', 'beds', 'HRSA')
ON CONFLICT (feature_key) DO NOTHING;

-- Emergency Services Features
INSERT INTO feature_definitions (feature_key, display_name, description, category_id, data_type, unit, data_source) VALUES
    ('dist_nearest_fire_stations_km', 'Distance to Fire Station', 'Distance to nearest fire station', 3, 'distance', 'km', 'HIFLD'),
    ('count_fire_stations_50km', 'Fire Stations within 50km', 'Count of fire stations within 50km', 3, 'count', 'count', 'HIFLD'),
    ('density_fire_stations_per10k', 'Fire Station Density', 'Fire stations per 10,000 population', 3, 'ratio', 'per 10k', 'Calculated'),
    ('dist_nearest_ems_km', 'Distance to EMS', 'Distance to nearest EMS station', 3, 'distance', 'km', 'HIFLD'),
    ('count_ems_50km', 'EMS Stations within 50km', 'Count of EMS stations within 50km', 3, 'count', 'count', 'HIFLD'),
    ('density_ems_per10k', 'EMS Density', 'EMS stations per 10,000 population', 3, 'ratio', 'per 10k', 'Calculated'),
    ('emergency_response_time', 'Avg Emergency Response Time', 'Average emergency response time', 3, 'distance', 'minutes', 'Calculated')
ON CONFLICT (feature_key) DO NOTHING;

-- Socioeconomic Features
INSERT INTO feature_definitions (feature_key, display_name, description, category_id, data_type, unit, data_source) VALUES
    ('median_household_income', 'Median Household Income', 'Median household income', 4, 'currency', 'USD', 'Census'),
    ('poverty_pct', 'Poverty Rate', 'Percentage below poverty line', 4, 'percentage', '%', 'Census'),
    ('unemployment_rate', 'Unemployment Rate', 'Unemployment percentage', 4, 'percentage', '%', 'BLS'),
    ('education_less_than_high_school', 'Less than High School %', 'Population without high school diploma', 4, 'percentage', '%', 'Census'),
    ('single_parent_households_pct', 'Single Parent Households %', 'Percentage of single-parent households', 4, 'percentage', '%', 'Census'),
    ('minority_population_pct', 'Minority Population %', 'Percentage of minority population', 4, 'percentage', '%', 'Census'),
    ('language_barrier_pct', 'Language Barrier %', 'Population with limited English proficiency', 4, 'percentage', '%', 'Census'),
    ('housing_units_mobile_homes_pct', 'Mobile Home %', 'Percentage of mobile home housing units', 4, 'percentage', '%', 'Census'),
    ('no_vehicle_households_pct', 'No Vehicle %', 'Percentage of households without vehicles', 4, 'percentage', '%', 'Census'),
    ('crowded_housing_pct', 'Crowded Housing %', 'Percentage in crowded housing', 4, 'percentage', '%', 'Census')
ON CONFLICT (feature_key) DO NOTHING;

-- Agriculture Features
INSERT INTO feature_definitions (feature_key, display_name, description, category_id, data_type, unit, data_source) VALUES
    ('farm_count', 'Farm Count', 'Number of farms in county', 5, 'count', 'count', 'USDA'),
    ('farm_acres', 'Total Farm Acres', 'Total agricultural acreage', 5, 'count', 'acres', 'USDA'),
    ('crop_diversity_index', 'Crop Diversity Index', 'Measure of crop diversity', 5, 'ratio', 'index', 'USDA'),
    ('irrigation_coverage_pct', 'Irrigation Coverage %', 'Percentage of farmland with irrigation', 5, 'percentage', '%', 'USDA'),
    ('agricultural_vulnerability_score', 'Agricultural Vulnerability', 'Composite agricultural vulnerability score', 5, 'ratio', 'score', 'Calculated')
ON CONFLICT (feature_key) DO NOTHING;

-- Composite Risk Features
INSERT INTO feature_definitions (feature_key, display_name, description, category_id, data_type, unit, data_source, is_calculated) VALUES
    ('svi_score', 'Social Vulnerability Index', 'CDC Social Vulnerability Index score', 6, 'ratio', 'score', 'CDC', true),
    ('resilience_score', 'Resilience Score', 'Overall county resilience score', 6, 'ratio', 'score', 'Calculated', true),
    ('climate_risk_score', 'Climate Risk Score', 'Composite climate risk score', 6, 'ratio', 'score', 'Calculated', true),
    ('health_risk_score', 'Health Risk Score', 'Composite health infrastructure risk score', 6, 'ratio', 'score', 'Calculated', true),
    ('infrastructure_risk_score', 'Infrastructure Risk Score', 'Composite infrastructure risk score', 6, 'ratio', 'score', 'Calculated', true),
    ('overall_risk_score', 'Overall Risk Score', 'Combined overall risk score', 6, 'ratio', 'score', 'Calculated', true),
    ('risk_percentile', 'Risk Percentile', 'National risk percentile ranking', 6, 'percentage', '%', 'Calculated', true)
ON CONFLICT (feature_key) DO NOTHING;

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to get all features for a county
CREATE OR REPLACE FUNCTION get_county_features(
    p_fips_code VARCHAR(5)
)
RETURNS TABLE (
    feature_key VARCHAR(100),
    display_name VARCHAR(200),
    category_name VARCHAR(50),
    numeric_value DECIMAL(20, 8),
    unit VARCHAR(50),
    confidence_score DECIMAL(3, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fd.feature_key,
        fd.display_name,
        fc.category_name,
        cf.numeric_value,
        fd.unit,
        cf.confidence_score
    FROM counties c
    JOIN county_features cf ON c.id = cf.county_id
    JOIN feature_definitions fd ON cf.feature_id = fd.id
    JOIN feature_categories fc ON fd.category_id = fc.id
    WHERE c.fips_code = p_fips_code
      AND cf.effective_date = CURRENT_DATE
    ORDER BY fc.display_order, fd.display_name;
END;
$$ LANGUAGE plpgsql;

-- Function to get feature value for a county
CREATE OR REPLACE FUNCTION get_feature_value(
    p_fips_code VARCHAR(5),
    p_feature_key VARCHAR(100)
)
RETURNS DECIMAL(20, 8) AS $$
DECLARE
    v_value DECIMAL(20, 8);
BEGIN
    SELECT cf.numeric_value INTO v_value
    FROM counties c
    JOIN county_features cf ON c.id = cf.county_id
    JOIN feature_definitions fd ON cf.feature_id = fd.id
    WHERE c.fips_code = p_fips_code
      AND fd.feature_key = p_feature_key
      AND cf.effective_date = CURRENT_DATE;
    
    RETURN v_value;
END;
$$ LANGUAGE plpgsql;

-- Function to compare counties by feature
CREATE OR REPLACE FUNCTION compare_counties_by_feature(
    p_feature_key VARCHAR(100),
    p_fips_codes VARCHAR(5)[]
)
RETURNS TABLE (
    fips_code VARCHAR(5),
    county_name VARCHAR(200),
    state_abbrev VARCHAR(2),
    feature_value DECIMAL(20, 8),
    national_percentile DECIMAL(5, 2)
) AS $$
BEGIN
    RETURN QUERY
    WITH feature_stats AS (
        SELECT 
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cf.numeric_value) as median_value,
            AVG(cf.numeric_value) as avg_value,
            STDDEV(cf.numeric_value) as stddev_value
        FROM county_features cf
        JOIN feature_definitions fd ON cf.feature_id = fd.id
        WHERE fd.feature_key = p_feature_key
          AND cf.effective_date = CURRENT_DATE
    ),
    county_values AS (
        SELECT 
            c.fips_code,
            c.county_name,
            c.state_abbrev,
            cf.numeric_value as feature_value,
            PERCENT_RANK() OVER (ORDER BY cf.numeric_value) * 100 as percentile
        FROM counties c
        JOIN county_features cf ON c.id = cf.county_id
        JOIN feature_definitions fd ON cf.feature_id = fd.id
        WHERE fd.feature_key = p_feature_key
          AND cf.effective_date = CURRENT_DATE
    )
    SELECT 
        cv.fips_code,
        cv.county_name,
        cv.state_abbrev,
        cv.feature_value,
        cv.percentile as national_percentile
    FROM county_values cv
    WHERE cv.fips_code = ANY(p_fips_codes)
    ORDER BY cv.feature_value DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VIEWS
-- ============================================

-- Feature summary view
CREATE OR REPLACE VIEW feature_summary AS
SELECT 
    fd.feature_key,
    fd.display_name,
    fc.category_name,
    fd.domain,
    fd.data_type,
    fd.unit,
    fd.data_source,
    fd.is_calculated,
    COUNT(cf.id) as county_count,
    AVG(cf.numeric_value) as avg_value,
    MIN(cf.numeric_value) as min_value,
    MAX(cf.numeric_value) as max_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cf.numeric_value) as median_value
FROM feature_definitions fd
JOIN feature_categories fc ON fd.category_id = fc.id
LEFT JOIN county_features cf ON fd.id = cf.feature_id
WHERE cf.effective_date = CURRENT_DATE OR cf.effective_date IS NULL
GROUP BY fd.id, fc.category_name;

-- County risk profile view
CREATE OR REPLACE VIEW county_risk_profile AS
SELECT 
    c.fips_code,
    c.county_name,
    c.state_abbrev,
    MAX(CASE WHEN fd.feature_key = 'overall_risk_score' THEN cf.numeric_value END) as overall_risk,
    MAX(CASE WHEN fd.feature_key = 'climate_risk_score' THEN cf.numeric_value END) as climate_risk,
    MAX(CASE WHEN fd.feature_key = 'health_risk_score' THEN cf.numeric_value END) as health_risk,
    MAX(CASE WHEN fd.feature_key = 'infrastructure_risk_score' THEN cf.numeric_value END) as infrastructure_risk,
    MAX(CASE WHEN fd.feature_key = 'svi_score' THEN cf.numeric_value END) as svi_score,
    MAX(CASE WHEN fd.feature_key = 'resilience_score' THEN cf.numeric_value END) as resilience_score
FROM counties c
LEFT JOIN county_features cf ON c.id = cf.county_id AND cf.effective_date = CURRENT_DATE
LEFT JOIN feature_definitions fd ON cf.feature_id = fd.id
GROUP BY c.id, c.fips_code, c.county_name, c.state_abbrev;
