-- ============================================
-- RESILIENCEAI COUNTIES SCHEMA
-- PostgreSQL + PostGIS Geospatial Core
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS btree_gist;   -- For GiST indexes
CREATE EXTENSION IF NOT EXISTS uuid-ossp;    -- For UUID generation

-- ============================================
-- COUNTIES TABLE (Geospatial Core)
-- ============================================

CREATE TABLE IF NOT EXISTS counties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fips_code VARCHAR(5) UNIQUE NOT NULL,           -- 5-digit FIPS (State + County)
    state_fips VARCHAR(2) NOT NULL,                  -- 2-digit State FIPS
    county_fips VARCHAR(3) NOT NULL,                 -- 3-digit County FIPS
    state_name VARCHAR(100) NOT NULL,
    state_abbrev VARCHAR(2) NOT NULL,
    county_name VARCHAR(200) NOT NULL,
    
    -- Geospatial data
    centroid GEOMETRY(POINT, 4326) NOT NULL,         -- County centroid
    boundary GEOMETRY(MULTIPOLYGON, 4326),           -- County boundary
    bounding_box GEOMETRY(POLYGON, 4326),            -- For quick intersection tests
    
    -- Derived metrics (cached for performance)
    area_sq_km DECIMAL(12, 4),
    population INTEGER,
    population_density DECIMAL(10, 4),
    
    -- Metadata
    data_quality_score DECIMAL(3, 2) DEFAULT 1.0,    -- 0.0 to 1.0
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_fips CHECK (LENGTH(fips_code) = 5),
    CONSTRAINT valid_state_abbrev CHECK (LENGTH(state_abbrev) = 2)
);

-- ============================================
-- GEOSPATIAL INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_counties_centroid ON counties USING GIST(centroid);
CREATE INDEX IF NOT EXISTS idx_counties_boundary ON counties USING GIST(boundary);
CREATE INDEX IF NOT EXISTS idx_counties_bounding_box ON counties USING GIST(bounding_box);

-- ============================================
-- STANDARD INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_counties_fips ON counties(fips_code);
CREATE INDEX IF NOT EXISTS idx_counties_state ON counties(state_abbrev);
CREATE INDEX IF NOT EXISTS idx_counties_state_fips ON counties(state_fips);
CREATE INDEX IF NOT EXISTS idx_counties_name_trgm ON counties USING GIN(county_name gin_trgm_ops);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_counties_state_population ON counties(state_abbrev, population DESC);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to find counties within radius
CREATE OR REPLACE FUNCTION find_counties_within_radius(
    center_lon FLOAT,
    center_lat FLOAT,
    radius_km FLOAT
)
RETURNS TABLE (
    id UUID,
    fips_code VARCHAR(5),
    county_name VARCHAR(200),
    state_abbrev VARCHAR(2),
    distance_km FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.fips_code,
        c.county_name,
        c.state_abbrev,
        ST_Distance(
            c.centroid::geography,
            ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography
        ) / 1000 as distance_km
    FROM counties c
    WHERE ST_DWithin(
        c.centroid::geography,
        ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography,
        radius_km * 1000
    )
    ORDER BY distance_km;
END;
$$ LANGUAGE plpgsql;

-- Function to find counties intersecting with polygon
CREATE OR REPLACE FUNCTION find_counties_in_polygon(
    polygon_wkt TEXT
)
RETURNS TABLE (
    id UUID,
    fips_code VARCHAR(5),
    county_name VARCHAR(200),
    state_abbrev VARCHAR(2),
    intersection_area FLOAT
) AS $$
DECLARE
    search_geom GEOMETRY;
BEGIN
    search_geom := ST_GeomFromText(polygon_wkt, 4326);
    
    RETURN QUERY
    SELECT 
        c.id,
        c.fips_code,
        c.county_name,
        c.state_abbrev,
        ST_Area(ST_Intersection(c.boundary, search_geom)::geography) as intersection_area
    FROM counties c
    WHERE ST_Intersects(c.boundary, search_geom)
    ORDER BY intersection_area DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to find nearest counties
CREATE OR REPLACE FUNCTION find_nearest_counties(
    center_lon FLOAT,
    center_lat FLOAT,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    fips_code VARCHAR(5),
    county_name VARCHAR(200),
    state_abbrev VARCHAR(2),
    distance_km FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.fips_code,
        c.county_name,
        c.state_abbrev,
        ST_Distance(
            c.centroid::geography,
            ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography
        ) / 1000 as distance_km
    FROM counties c
    ORDER BY c.centroid <-> ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VIEWS
-- ============================================

-- County summary view with key metrics
CREATE OR REPLACE VIEW county_summary AS
SELECT 
    c.id,
    c.fips_code,
    c.county_name,
    c.state_abbrev,
    c.state_name,
    c.population,
    c.population_density,
    c.area_sq_km,
    ST_X(c.centroid) as longitude,
    ST_Y(c.centroid) as latitude,
    c.data_quality_score,
    c.last_updated
FROM counties c;

-- State summary view
CREATE OR REPLACE VIEW state_summary AS
SELECT 
    c.state_abbrev,
    c.state_name,
    COUNT(*) as county_count,
    SUM(c.population) as total_population,
    AVG(c.population_density) as avg_density,
    AVG(c.data_quality_score) as avg_data_quality
FROM counties c
GROUP BY c.state_abbrev, c.state_name
ORDER BY total_population DESC;

-- ============================================
-- SAMPLE DATA INSERTION (for testing)
-- ============================================

-- Insert sample Missouri counties (for testing)
INSERT INTO counties (
    fips_code, state_fips, county_fips, state_name, state_abbrev, 
    county_name, centroid, population
) VALUES 
    ('29001', '29', '001', 'Missouri', 'MO', 'Adair County', 
     ST_SetSRID(ST_MakePoint(-92.6038, 40.1906), 4326), 25316),
    ('29003', '29', '003', 'Missouri', 'MO', 'Andrew County', 
     ST_SetSRID(ST_MakePoint(-94.8029, 39.9844), 4326), 18215),
    ('29095', '29', '095', 'Missouri', 'MO', 'Jackson County', 
     ST_SetSRID(ST_MakePoint(-94.3426, 39.0164), 4326), 717204),
    ('29189', '29', '189', 'Missouri', 'MO', 'St. Louis County', 
     ST_SetSRID(ST_MakePoint(-90.4434, 38.6406), 4326), 1004125)
ON CONFLICT (fips_code) DO NOTHING;
