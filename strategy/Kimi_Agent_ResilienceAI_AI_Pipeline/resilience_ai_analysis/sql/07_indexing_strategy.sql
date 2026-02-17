-- ============================================
-- RESILIENCEAI INDEXING STRATEGY
-- Comprehensive indexing for optimal query performance
-- ============================================

-- ============================================
-- 1. PRIMARY ACCESS PATTERNS
-- ============================================
-- A. Query by FIPS code (most common)
-- B. Query by state
-- C. Geospatial queries (within radius, intersection)
-- D. Time-range queries
-- E. Feature value range queries
-- F. Full-text search on county names

-- ============================================
-- 2. B-TREE INDEXES (Equality and Range Queries)
-- ============================================
-- For: Exact matches, range scans, sorting

-- County lookups
CREATE INDEX IF NOT EXISTS idx_counties_fips ON counties(fips_code);
CREATE INDEX IF NOT EXISTS idx_counties_state ON counties(state_abbrev);
CREATE INDEX IF NOT EXISTS idx_counties_state_fips ON counties(state_fips, county_fips);

-- Feature lookups
CREATE INDEX IF NOT EXISTS idx_feature_definitions_key ON feature_definitions(feature_key);
CREATE INDEX IF NOT EXISTS idx_feature_definitions_category ON feature_definitions(category_id);
CREATE INDEX IF NOT EXISTS idx_feature_definitions_active ON feature_definitions(is_active) WHERE is_active = TRUE;

-- County feature value lookups
CREATE INDEX IF NOT EXISTS idx_county_features_county ON county_features(county_id);
CREATE INDEX IF NOT EXISTS idx_county_features_feature ON county_features(feature_id);
CREATE INDEX IF NOT EXISTS idx_county_features_date ON county_features(effective_date);
CREATE INDEX IF NOT EXISTS idx_county_features_value ON county_features(numeric_value) WHERE numeric_value IS NOT NULL;

-- Alert lookups
CREATE INDEX IF NOT EXISTS idx_alert_events_county ON alert_events(county_id);
CREATE INDEX IF NOT EXISTS idx_alert_events_status ON alert_events(status);
CREATE INDEX IF NOT EXISTS idx_alert_events_triggered ON alert_events(triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_alert_events_type ON alert_events(alert_type);

-- Subscription lookups
CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_county ON alert_subscriptions(county_id);
CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_active ON alert_subscriptions(is_active) WHERE is_active = TRUE;

-- ============================================
-- 3. GIST INDEXES (Geospatial)
-- ============================================
-- For: Spatial relationships, nearest neighbor

CREATE INDEX IF NOT EXISTS idx_counties_centroid ON counties USING GIST(centroid);
CREATE INDEX IF NOT EXISTS idx_counties_boundary ON counties USING GIST(boundary);
CREATE INDEX IF NOT EXISTS idx_counties_bounding_box ON counties USING GIST(bounding_box);
CREATE INDEX IF NOT EXISTS idx_facilities_location ON facilities USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_facility_service_areas ON facility_service_areas USING GIST(service_area);
CREATE INDEX IF NOT EXISTS idx_alert_events_impact ON alert_events USING GIST(impact_area) WHERE impact_area IS NOT NULL;

-- ============================================
-- 4. GIN INDEXES (Full-text, JSONB, Arrays)
-- ============================================
-- For: Text search, JSON containment, array operations

-- Full-text search on county names
CREATE INDEX IF NOT EXISTS idx_counties_name_trgm ON counties USING GIN(county_name gin_trgm_ops);

-- JSONB indexes
CREATE INDEX IF NOT EXISTS idx_county_features_json ON county_features USING GIN(json_value);
CREATE INDEX IF NOT EXISTS idx_facilities_attributes ON facilities USING GIN(attributes);
CREATE INDEX IF NOT EXISTS idx_alert_events_source ON alert_events USING GIN(source_data);

-- Array indexes
CREATE INDEX IF NOT EXISTS idx_alert_events_affected ON alert_events USING GIN(affected_features);
CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_types ON alert_subscriptions USING GIN(alert_types);

-- ============================================
-- 5. BRIN INDEXES (Block Range - for large time-series)
-- ============================================
-- For: Time-series data where values correlate with insertion order

CREATE INDEX IF NOT EXISTS idx_county_metrics_history_brin ON county_metrics_history USING BRIN(time);
CREATE INDEX IF NOT EXISTS idx_realtime_events_brin ON realtime_events USING BRIN(time);
CREATE INDEX IF NOT EXISTS idx_predictions_brin ON predictions USING BRIN(time);

-- ============================================
-- 6. PARTIAL INDEXES (Filtered Subsets)
-- ============================================
-- For: Frequently queried subsets

-- Active alerts (most commonly queried)
CREATE INDEX IF NOT EXISTS idx_alert_events_active ON alert_events(county_id, triggered_at DESC) 
    WHERE status = 'active';

-- High severity alerts
CREATE INDEX IF NOT EXISTS idx_alert_events_high_severity ON alert_events(county_id, triggered_at DESC)
    WHERE severity IN ('high', 'critical');

-- Missouri counties (primary focus state)
CREATE INDEX IF NOT EXISTS idx_counties_mo ON counties(county_name) WHERE state_abbrev = 'MO';

-- Active facilities
CREATE INDEX IF NOT EXISTS idx_facilities_active ON facilities(facility_type) WHERE is_active = TRUE;

-- Unvalidated predictions
CREATE INDEX IF NOT EXISTS idx_predictions_unvalidated ON predictions(county_id, target_date)
    WHERE validated_at IS NULL;

-- Unprocessed real-time events
CREATE INDEX IF NOT EXISTS idx_realtime_events_unprocessed ON realtime_events(time)
    WHERE processed = FALSE;

-- ============================================
-- 7. COMPOSITE INDEXES (Multi-column)
-- ============================================
-- For: Queries with multiple WHERE conditions

-- County features by county, feature, and date
CREATE INDEX IF NOT EXISTS idx_county_features_county_feature_date 
    ON county_features(county_id, feature_id, effective_date DESC);

-- Predictions by county and model
CREATE INDEX IF NOT EXISTS idx_predictions_county_model 
    ON predictions(county_id, model_id, time DESC);

-- Alert deliveries by alert and status
CREATE INDEX IF NOT EXISTS idx_alert_deliveries_alert_status 
    ON alert_deliveries(alert_event_id, status);

-- County metrics by county, feature, and time
CREATE INDEX IF NOT EXISTS idx_county_metrics_history_lookup 
    ON county_metrics_history(county_id, feature_id, time DESC);

-- ============================================
-- 8. EXPRESSION INDEXES
-- ============================================
-- For: Queries on computed expressions

-- Lowercase county name for case-insensitive search
CREATE INDEX IF NOT EXISTS idx_counties_name_lower ON counties(LOWER(county_name));

-- Year-month extraction for time-series queries
CREATE INDEX IF NOT EXISTS idx_county_metrics_year_month 
    ON county_metrics_history(EXTRACT(YEAR FROM time), EXTRACT(MONTH FROM time));

-- ============================================
-- 9. INDEX MAINTENANCE FUNCTIONS
-- ============================================

-- Function to analyze all tables
CREATE OR REPLACE FUNCTION analyze_all_tables()
RETURNS void AS $$
BEGIN
    ANALYZE counties;
    ANALYZE county_features;
    ANALYZE feature_definitions;
    ANALYZE alert_events;
    ANALYZE alert_subscriptions;
    ANALYZE county_metrics_history;
    ANALYZE realtime_events;
    ANALYZE predictions;
END;
$$ LANGUAGE plpgsql;

-- Function to get index usage statistics
CREATE OR REPLACE FUNCTION get_index_usage_stats()
RETURNS TABLE (
    schemaname text,
    tablename text,
    indexname text,
    idx_scan bigint,
    idx_tup_read bigint,
    idx_tup_fetch bigint,
    table_rows bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.schemaname::text,
        s.relname::text as tablename,
        s.indexrelname::text as indexname,
        s.idx_scan,
        s.idx_tup_read,
        s.idx_tup_fetch,
        c.reltuples::bigint as table_rows
    FROM pg_stat_user_indexes s
    JOIN pg_class c ON s.relid = c.oid
    WHERE s.schemaname = 'public'
    ORDER BY s.idx_scan DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to identify unused indexes
CREATE OR REPLACE FUNCTION get_unused_indexes(
    min_table_rows integer DEFAULT 1000
)
RETURNS TABLE (
    schemaname text,
    tablename text,
    indexname text,
    idx_scan bigint,
    table_rows bigint,
    index_size text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.schemaname::text,
        s.relname::text as tablename,
        s.indexrelname::text as indexname,
        s.idx_scan,
        c.reltuples::bigint as table_rows,
        pg_size_pretty(pg_relation_size(s.indexrelid)) as index_size
    FROM pg_stat_user_indexes s
    JOIN pg_class c ON s.relid = c.oid
    WHERE s.schemaname = 'public'
      AND s.idx_scan = 0
      AND s.indexrelname NOT LIKE '%pkey%'
      AND s.indexrelname NOT LIKE '%unique%'
      AND c.reltuples > min_table_rows
    ORDER BY c.reltuples DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get index sizes
CREATE OR REPLACE FUNCTION get_index_sizes()
RETURNS TABLE (
    schemaname text,
    tablename text,
    indexname text,
    index_size text,
    table_size text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname::text,
        tablename::text,
        indexname::text,
        pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
        pg_size_pretty(pg_relation_size(relid)) as table_size
    FROM pg_indexes
    JOIN pg_class c ON pg_indexes.tablename = c.relname
    WHERE schemaname = 'public'
    ORDER BY pg_relation_size(indexrelid) DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 10. INDEX MONITORING VIEWS
-- ============================================

-- Index usage summary
CREATE OR REPLACE VIEW index_usage_summary AS
SELECT 
    s.relname as table_name,
    s.indexrelname as index_name,
    s.idx_scan as times_used,
    s.idx_tup_read as tuples_read,
    pg_size_pretty(pg_relation_size(s.indexrelid)) as index_size,
    CASE 
        WHEN s.idx_scan = 0 THEN 'UNUSED'
        WHEN s.idx_scan < 10 THEN 'RARELY USED'
        ELSE 'ACTIVE'
    END as usage_status
FROM pg_stat_user_indexes s
WHERE s.schemaname = 'public'
ORDER BY s.idx_scan DESC;

-- Missing index recommendations (based on sequential scans)
CREATE OR REPLACE VIEW missing_index_recommendations AS
SELECT 
    schemaname,
    relname as table_name,
    seq_scan,
    seq_tup_read,
    idx_scan,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    CASE 
        WHEN seq_scan > 0 AND idx_scan IS NULL THEN 'HIGH PRIORITY - No indexes used'
        WHEN seq_scan > idx_scan * 10 THEN 'MEDIUM PRIORITY - High seq_scan ratio'
        ELSE 'LOW PRIORITY'
    END as recommendation
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND relname NOT LIKE 'pg_%'
ORDER BY seq_scan DESC;

-- ============================================
-- 11. RUN INDEX ANALYSIS
-- ============================================

-- Analyze all tables
SELECT analyze_all_tables();

-- Show index usage summary
SELECT * FROM index_usage_summary LIMIT 20;
