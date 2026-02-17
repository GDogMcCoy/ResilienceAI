-- ============================================
-- RESILIENCEAI TIMESCALEDB SCHEMA
-- Time-Series Data for Historical Metrics and Events
-- ============================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================
-- HISTORICAL COUNTY METRICS
-- ============================================

CREATE TABLE IF NOT EXISTS county_metrics_history (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    county_id UUID NOT NULL REFERENCES counties(id),
    feature_id UUID NOT NULL REFERENCES feature_definitions(id),
    
    -- Value
    value DECIMAL(20, 8) NOT NULL,
    value_type VARCHAR(20) DEFAULT 'measured' CHECK (value_type IN ('measured', 'interpolated', 'forecasted', 'imputed')),
    
    -- Data quality
    confidence DECIMAL(3, 2) DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    data_source VARCHAR(100),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Primary key includes time for uniqueness
    PRIMARY KEY (time, county_id, feature_id)
);

-- Convert to hypertable (partitioned by time)
SELECT create_hypertable('county_metrics_history', 'time', 
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- Enable compression on hypertable
ALTER TABLE county_metrics_history SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'county_id, feature_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- Add compression policy (compress chunks older than 7 days)
SELECT add_compression_policy('county_metrics_history', INTERVAL '7 days', if_not_exists => TRUE);

-- Add retention policy (keep raw data for 2 years)
SELECT add_retention_policy('county_metrics_history', INTERVAL '2 years', if_not_exists => TRUE);

-- Indexes for county metrics history
CREATE INDEX IF NOT EXISTS idx_county_metrics_history_county ON county_metrics_history(county_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_county_metrics_history_feature ON county_metrics_history(feature_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_county_metrics_history_source ON county_metrics_history(data_source, time DESC);

-- ============================================
-- CONTINUOUS AGGREGATES
-- ============================================

-- Daily aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS county_metrics_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS bucket,
    county_id,
    feature_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count,
    FIRST(value, time) as first_value,
    LAST(value, time) as last_value
FROM county_metrics_history
GROUP BY bucket, county_id, feature_id
WITH NO DATA;

-- Add refresh policy for daily aggregates
SELECT add_continuous_aggregate_policy('county_metrics_daily',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Monthly aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS county_metrics_monthly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 month', time) AS bucket,
    county_id,
    feature_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count,
    STDDEV(value) as stddev_value
FROM county_metrics_history
GROUP BY bucket, county_id, feature_id
WITH NO DATA;

-- Add refresh policy for monthly aggregates
SELECT add_continuous_aggregate_policy('county_metrics_monthly',
    start_offset => INTERVAL '1 year',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Yearly aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS county_metrics_yearly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 year', time) AS bucket,
    county_id,
    feature_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count
FROM county_metrics_history
GROUP BY bucket, county_id, feature_id
WITH NO DATA;

-- ============================================
-- REAL-TIME EVENTS
-- ============================================

CREATE TABLE IF NOT EXISTS realtime_events (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    event_id UUID DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,                   -- 'weather_alert', 'disaster_declaration', etc.
    source VARCHAR(50) NOT NULL,                       -- 'NOAA', 'FEMA', 'USGS'
    source_event_id VARCHAR(100),                      -- ID from source system
    
    -- Location
    county_id UUID REFERENCES counties(id),
    location GEOMETRY(POINT, 4326),
    
    -- Event data
    severity VARCHAR(20),
    title TEXT,
    description TEXT,
    raw_data JSONB DEFAULT '{}',
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processing_timestamp TIMESTAMP WITH TIME ZONE,
    processing_error TEXT,
    
    -- Alert generation
    alert_generated BOOLEAN DEFAULT FALSE,
    alert_event_id UUID REFERENCES alert_events(id)
);

-- Convert to hypertable
SELECT create_hypertable('realtime_events', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Retention: Keep events for 90 days
SELECT add_retention_policy('realtime_events', INTERVAL '90 days', if_not_exists => TRUE);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_realtime_events_type ON realtime_events(event_type, time DESC);
CREATE INDEX IF NOT EXISTS idx_realtime_events_county ON realtime_events(county_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_realtime_events_source ON realtime_events(source, time DESC);
CREATE INDEX IF NOT EXISTS idx_realtime_events_unprocessed ON realtime_events(processed, time) WHERE processed = FALSE;
CREATE INDEX IF NOT EXISTS idx_realtime_events_location ON realtime_events USING GIST(location);

-- ============================================
-- PREDICTIONS AND FORECASTS
-- ============================================

CREATE TABLE IF NOT EXISTS predictions (
    time TIMESTAMP WITH TIME ZONE NOT NULL,            -- When prediction was made
    county_id UUID NOT NULL REFERENCES counties(id),
    model_id VARCHAR(100) NOT NULL,                    -- Identifier for the model used
    
    -- Prediction details
    prediction_type VARCHAR(50),                       -- 'risk_score', 'disaster_probability', etc.
    target_date DATE,                                  -- What date is this prediction for?
    horizon_days INTEGER,                              -- How many days ahead?
    
    -- Values
    predicted_value DECIMAL(20, 8),
    confidence_lower DECIMAL(20, 8),                   -- Lower bound of confidence interval
    confidence_upper DECIMAL(20, 8),                   -- Upper bound
    confidence_level DECIMAL(3, 2) DEFAULT 0.95,       -- e.g., 0.95 for 95% CI
    
    -- Model metadata
    model_version VARCHAR(50),
    feature_importance JSONB DEFAULT '{}',             -- Which features contributed most
    
    -- Validation (filled in later when actual values known)
    actual_value DECIMAL(20, 8),
    prediction_error DECIMAL(20, 8),
    validated_at TIMESTAMP WITH TIME ZONE,
    
    PRIMARY KEY (time, county_id, model_id, prediction_type, target_date)
);

-- Convert to hypertable
SELECT create_hypertable('predictions', 'time',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

-- Retention: Keep predictions for 1 year
SELECT add_retention_policy('predictions', INTERVAL '1 year', if_not_exists => TRUE);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_predictions_county ON predictions(county_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_model ON predictions(model_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_target ON predictions(target_date);
CREATE INDEX IF NOT EXISTS idx_predictions_type ON predictions(prediction_type, time DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_unvalidated ON predictions(validated_at) WHERE validated_at IS NULL;

-- ============================================
-- MODEL PERFORMANCE TRACKING
-- ============================================

CREATE TABLE IF NOT EXISTS model_performance (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    
    -- Performance metrics
    prediction_type VARCHAR(50),
    horizon_days INTEGER,
    
    -- Error metrics
    mae DECIMAL(10, 6),                                -- Mean Absolute Error
    mse DECIMAL(10, 6),                                -- Mean Squared Error
    rmse DECIMAL(10, 6),                               -- Root Mean Squared Error
    mape DECIMAL(10, 6),                               -- Mean Absolute Percentage Error
    r2_score DECIMAL(5, 4),                            -- R-squared
    
    -- Sample information
    sample_count INTEGER,
    training_samples INTEGER,
    
    -- Additional metrics
    metrics JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('model_performance', 'time',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_model_performance_model ON model_performance(model_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_model_performance_type ON model_performance(prediction_type, time DESC);

-- ============================================
-- DATA INGESTION LOG
-- ============================================

CREATE TABLE IF NOT EXISTS data_ingestion_log (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(100) NOT NULL,                      -- Data source name
    ingestion_type VARCHAR(50),                        -- 'full', 'incremental', 'streaming'
    
    -- Status
    status VARCHAR(20) NOT NULL,                       -- 'started', 'completed', 'failed'
    
    -- Metrics
    records_processed INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    records_failed INTEGER,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Error information
    error_message TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('data_ingestion_log', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Retention: Keep logs for 30 days
SELECT add_retention_policy('data_ingestion_log', INTERVAL '30 days', if_not_exists => TRUE);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to insert metric with automatic time bucketing
CREATE OR REPLACE FUNCTION insert_county_metric(
    p_county_id UUID,
    p_feature_id UUID,
    p_value DECIMAL(20, 8),
    p_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    p_value_type VARCHAR(20) DEFAULT 'measured',
    p_confidence DECIMAL(3, 2) DEFAULT 1.0,
    p_data_source VARCHAR(100) DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO county_metrics_history (
        time, county_id, feature_id, value, value_type, confidence, data_source
    ) VALUES (
        p_timestamp, p_county_id, p_feature_id, p_value, p_value_type, p_confidence, p_data_source
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get time series for a county and feature
CREATE OR REPLACE FUNCTION get_county_time_series(
    p_county_fips VARCHAR(5),
    p_feature_key VARCHAR(100),
    p_start_time TIMESTAMP WITH TIME ZONE,
    p_end_time TIMESTAMP WITH TIME ZONE,
    p_aggregation VARCHAR(20) DEFAULT 'raw'           -- 'raw', 'hourly', 'daily', 'monthly'
)
RETURNS TABLE (
    timestamp TIMESTAMP WITH TIME ZONE,
    value DECIMAL(20, 8),
    sample_count BIGINT
) AS $$
DECLARE
    v_county_id UUID;
    v_feature_id UUID;
BEGIN
    -- Get IDs
    SELECT id INTO v_county_id FROM counties WHERE fips_code = p_county_fips;
    SELECT id INTO v_feature_id FROM feature_definitions WHERE feature_key = p_feature_key;
    
    IF v_county_id IS NULL OR v_feature_id IS NULL THEN
        RETURN;
    END IF;
    
    -- Return appropriate aggregation
    CASE p_aggregation
        WHEN 'daily' THEN
            RETURN QUERY
            SELECT 
                cmd.bucket as timestamp,
                cmd.avg_value as value,
                cmd.sample_count
            FROM county_metrics_daily cmd
            WHERE cmd.county_id = v_county_id
              AND cmd.feature_id = v_feature_id
              AND cmd.bucket BETWEEN p_start_time AND p_end_time
            ORDER BY cmd.bucket;
        WHEN 'monthly' THEN
            RETURN QUERY
            SELECT 
                cmm.bucket as timestamp,
                cmm.avg_value as value,
                cmm.sample_count
            FROM county_metrics_monthly cmm
            WHERE cmm.county_id = v_county_id
              AND cmm.feature_id = v_feature_id
              AND cmm.bucket BETWEEN p_start_time AND p_end_TIME
            ORDER BY cmm.bucket;
        ELSE
            RETURN QUERY
            SELECT 
                cmh.time as timestamp,
                cmh.value,
                1::BIGINT as sample_count
            FROM county_metrics_history cmh
            WHERE cmh.county_id = v_county_id
              AND cmh.feature_id = v_feature_id
              AND cmh.time BETWEEN p_start_time AND p_end_time
            ORDER BY cmh.time;
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- Function to validate predictions
CREATE OR REPLACE FUNCTION validate_predictions(
    p_model_id VARCHAR(100),
    p_as_of_date DATE DEFAULT CURRENT_DATE
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    UPDATE predictions p
    SET 
        actual_value = cmh.value,
        prediction_error = p.predicted_value - cmh.value,
        validated_at = NOW()
    FROM county_metrics_history cmh
    JOIN feature_definitions fd ON cmh.feature_id = fd.id
    WHERE p.county_id = cmh.county_id
      AND p.model_id = p_model_id
      AND p.target_date = p_as_of_date
      AND cmh.time = (
          SELECT MAX(time) 
          FROM county_metrics_history 
          WHERE county_id = p.county_id 
            AND time::date = p_as_of_date
      )
      AND fd.feature_key = p.prediction_type
      AND p.validated_at IS NULL;
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VIEWS
-- ============================================

-- Recent metrics view (last 24 hours)
CREATE OR REPLACE VIEW recent_metrics AS
SELECT 
    cmh.time,
    c.fips_code,
    c.county_name,
    fd.feature_key,
    fd.display_name,
    cmh.value,
    cmh.value_type,
    cmh.confidence
FROM county_metrics_history cmh
JOIN counties c ON cmh.county_id = c.id
JOIN feature_definitions fd ON cmh.feature_id = fd.id
WHERE cmh.time > NOW() - INTERVAL '24 hours'
ORDER BY cmh.time DESC;

-- Prediction accuracy view
CREATE OR REPLACE VIEW prediction_accuracy AS
SELECT 
    p.model_id,
    p.prediction_type,
    p.horizon_days,
    COUNT(*) as total_predictions,
    COUNT(*) FILTER (WHERE p.validated_at IS NOT NULL) as validated_count,
    AVG(ABS(p.prediction_error)) as mae,
    AVG(POWER(p.prediction_error, 2)) as mse,
    SQRT(AVG(POWER(p.prediction_error, 2))) as rmse,
    AVG(ABS(p.prediction_error) / NULLIF(p.actual_value, 0)) * 100 as mape
FROM predictions p
WHERE p.time > NOW() - INTERVAL '30 days'
GROUP BY p.model_id, p.prediction_type, p.horizon_days;

-- Data ingestion summary
CREATE OR REPLACE VIEW data_ingestion_summary AS
SELECT 
    source,
    DATE_TRUNC('day', time) as date,
    COUNT(*) as ingestion_count,
    SUM(records_processed) as total_records,
    SUM(records_inserted) as total_inserted,
    SUM(records_failed) as total_failed,
    AVG(duration_seconds) as avg_duration_seconds,
    COUNT(*) FILTER (WHERE status = 'failed') as failure_count
FROM data_ingestion_log
WHERE time > NOW() - INTERVAL '7 days'
GROUP BY source, DATE_TRUNC('day', time)
ORDER BY date DESC, source;
