-- ============================================
-- RESILIENCEAI ALERT MANAGEMENT SCHEMA
-- Real-time Alert Subscriptions and Events
-- ============================================

-- ============================================
-- ENUM TYPES
-- ============================================

DO $$ BEGIN
    CREATE TYPE alert_severity AS ENUM ('info', 'low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE alert_status AS ENUM ('active', 'acknowledged', 'resolved', 'dismissed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE alert_type AS ENUM (
        'weather_warning', 
        'disaster_declaration', 
        'risk_threshold', 
        'infrastructure_failure', 
        'health_emergency', 
        'agricultural_threat',
        'climate_anomaly',
        'prediction_update'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- ALERT SUBSCRIPTIONS
-- ============================================

CREATE TABLE IF NOT EXISTS alert_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    county_id UUID NOT NULL REFERENCES counties(id) ON DELETE CASCADE,
    
    -- Subscription configuration
    subscription_name VARCHAR(200),
    alert_types alert_type[] NOT NULL DEFAULT ARRAY['risk_threshold']::alert_type[],
    severity_threshold alert_severity DEFAULT 'medium',
    risk_threshold DECIMAL(5, 4),                     -- Trigger when risk score exceeds this value
    
    -- Feature-specific thresholds
    feature_thresholds JSONB DEFAULT '{}',            -- {"feature_key": threshold_value}
    
    -- Notification channels
    email VARCHAR(255),
    phone VARCHAR(20),
    webhook_url TEXT,
    slack_channel VARCHAR(100),
    discord_webhook TEXT,
    
    -- Delivery preferences
    digest_mode BOOLEAN DEFAULT FALSE,                -- Send digest instead of immediate
    digest_frequency VARCHAR(20) DEFAULT 'daily',     -- 'immediate', 'hourly', 'daily', 'weekly'
    quiet_hours_start TIME,                           -- Don't send alerts during quiet hours
    quiet_hours_end TIME,
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),                          -- User or system identifier
    description TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_triggered TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    last_digest_sent TIMESTAMP WITH TIME ZONE
);

-- Indexes for alert subscriptions
CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_county ON alert_subscriptions(county_id);
CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_active ON alert_subscriptions(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_email ON alert_subscriptions(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_types ON alert_subscriptions USING GIN(alert_types);

-- ============================================
-- ALERT EVENTS
-- ============================================

CREATE TABLE IF NOT EXISTS alert_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID REFERENCES alert_subscriptions(id) ON DELETE SET NULL,
    county_id UUID NOT NULL REFERENCES counties(id) ON DELETE CASCADE,
    
    -- Alert details
    alert_type alert_type NOT NULL,
    severity alert_severity NOT NULL,
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    
    -- Associated data
    risk_score DECIMAL(5, 4),
    affected_features UUID[],                         -- Related feature IDs
    source_data JSONB DEFAULT '{}',                   -- Original triggering data
    
    -- External references
    external_id VARCHAR(100),                         -- ID from external system (NOAA, FEMA)
    external_url TEXT,                                -- Link to external resource
    
    -- Status tracking
    status alert_status DEFAULT 'active',
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_notes TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    
    -- Geospatial impact (if applicable)
    impact_area GEOMETRY(POLYGON, 4326),
    affected_population INTEGER,
    
    -- Timestamps
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,              -- Auto-expire old alerts
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for alert events
CREATE INDEX IF NOT EXISTS idx_alert_events_county ON alert_events(county_id);
CREATE INDEX IF NOT EXISTS idx_alert_events_status ON alert_events(status);
CREATE INDEX IF NOT EXISTS idx_alert_events_triggered ON alert_events(triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_alert_events_expires ON alert_events(expires_at);
CREATE INDEX IF NOT EXISTS idx_alert_events_type ON alert_events(alert_type);
CREATE INDEX IF NOT EXISTS idx_alert_events_severity ON alert_events(severity);
CREATE INDEX IF NOT EXISTS idx_alert_events_external ON alert_events(external_id) WHERE external_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_alert_events_impact ON alert_events USING GIST(impact_area) WHERE impact_area IS NOT NULL;

-- Partial index for active alerts (most queried)
CREATE INDEX IF NOT EXISTS idx_alert_events_active ON alert_events(county_id, triggered_at DESC) 
    WHERE status = 'active';

-- ============================================
-- ALERT DELIVERY LOG
-- ============================================

CREATE TABLE IF NOT EXISTS alert_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_event_id UUID NOT NULL REFERENCES alert_events(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES alert_subscriptions(id) ON DELETE SET NULL,
    
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('email', 'sms', 'webhook', 'slack', 'discord', 'push', 'in_app')),
    recipient TEXT NOT NULL,
    
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'bounced', 'suppressed')),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Content
    message_subject TEXT,
    message_body TEXT,
    
    -- Timestamps
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for alert deliveries
CREATE INDEX IF NOT EXISTS idx_alert_deliveries_alert ON alert_deliveries(alert_event_id);
CREATE INDEX IF NOT EXISTS idx_alert_deliveries_status ON alert_deliveries(status);
CREATE INDEX IF NOT EXISTS idx_alert_deliveries_pending ON alert_deliveries(created_at) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_alert_deliveries_channel ON alert_deliveries(channel);

-- ============================================
-- ALERT DIGEST QUEUE
-- ============================================

CREATE TABLE IF NOT EXISTS alert_digest_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID NOT NULL REFERENCES alert_subscriptions(id) ON DELETE CASCADE,
    alert_event_id UUID NOT NULL REFERENCES alert_events(id) ON DELETE CASCADE,
    
    -- Digest processing
    is_included BOOLEAN DEFAULT FALSE,
    included_in_digest UUID,                          -- Reference to sent digest
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_digest_queue_subscription ON alert_digest_queue(subscription_id);
CREATE INDEX IF NOT EXISTS idx_digest_queue_included ON alert_digest_queue(is_included) WHERE is_included = FALSE;

-- ============================================
-- ALERT TEMPLATES
-- ============================================

CREATE TABLE IF NOT EXISTS alert_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(100) UNIQUE NOT NULL,
    alert_type alert_type NOT NULL,
    
    -- Template content
    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    sms_template TEXT,
    
    -- Variables used in template
    required_variables TEXT[] DEFAULT '{}',
    
    -- Channel availability
    available_channels VARCHAR(20)[] DEFAULT ARRAY['email', 'in_app']::VARCHAR(20)[],
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default templates
INSERT INTO alert_templates (template_name, alert_type, subject_template, body_template, sms_template) VALUES
    ('risk_threshold_exceeded', 'risk_threshold', 
     'Risk Alert: {{county_name}} Risk Score Exceeded Threshold',
     'The risk score for {{county_name}}, {{state_abbrev}} has exceeded your configured threshold.\n\nCurrent Risk Score: {{risk_score}}\nThreshold: {{threshold}}\n\nView details: {{dashboard_url}}',
     'Risk Alert: {{county_name}} risk score {{risk_score}} exceeded threshold {{threshold}}'),
    
    ('weather_warning', 'weather_warning',
     'Weather Alert: {{alert_title}} for {{county_name}}',
     'A weather alert has been issued for {{county_name}}, {{state_abbrev}}.\n\nAlert: {{alert_title}}\nSeverity: {{severity}}\n\n{{message}}\n\nView details: {{dashboard_url}}',
     'Weather Alert: {{alert_title}} for {{county_name}}. {{message}}'),
    
    ('disaster_declaration', 'disaster_declaration',
     'Disaster Declared: {{disaster_type}} in {{county_name}}',
     'A disaster has been declared for {{county_name}}, {{state_abbrev}}.\n\nDisaster Type: {{disaster_type}}\nDeclaration Date: {{declaration_date}}\n\nView details: {{dashboard_url}}',
     'Disaster declared: {{disaster_type}} in {{county_name}}')
ON CONFLICT (template_name) DO NOTHING;

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to create alert subscription
CREATE OR REPLACE FUNCTION create_alert_subscription(
    p_county_fips VARCHAR(5),
    p_email VARCHAR(255),
    p_alert_types alert_type[],
    p_severity_threshold alert_severity DEFAULT 'medium',
    p_risk_threshold DECIMAL(5, 4) DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_county_id UUID;
    v_subscription_id UUID;
BEGIN
    -- Get county ID
    SELECT id INTO v_county_id FROM counties WHERE fips_code = p_county_fips;
    
    IF v_county_id IS NULL THEN
        RAISE EXCEPTION 'County not found: %', p_county_fips;
    END IF;
    
    -- Create subscription
    INSERT INTO alert_subscriptions (
        county_id, email, alert_types, severity_threshold, risk_threshold
    ) VALUES (
        v_county_id, p_email, p_alert_types, p_severity_threshold, p_risk_threshold
    ) RETURNING id INTO v_subscription_id;
    
    RETURN v_subscription_id;
END;
$$ LANGUAGE plpgsql;

-- Function to trigger alert
CREATE OR REPLACE FUNCTION trigger_alert(
    p_county_fips VARCHAR(5),
    p_alert_type alert_type,
    p_severity alert_severity,
    p_title VARCHAR(500),
    p_message TEXT,
    p_risk_score DECIMAL(5, 4) DEFAULT NULL,
    p_source_data JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    v_county_id UUID;
    v_alert_id UUID;
    v_subscription RECORD;
BEGIN
    -- Get county ID
    SELECT id INTO v_county_id FROM counties WHERE fips_code = p_county_fips;
    
    IF v_county_id IS NULL THEN
        RAISE EXCEPTION 'County not found: %', p_county_fips;
    END IF;
    
    -- Create alert event
    INSERT INTO alert_events (
        county_id, alert_type, severity, title, message, 
        risk_score, source_data, expires_at
    ) VALUES (
        v_county_id, p_alert_type, p_severity, p_title, p_message,
        p_risk_score, p_source_data, NOW() + INTERVAL '7 days'
    ) RETURNING id INTO v_alert_id;
    
    -- Find matching subscriptions
    FOR v_subscription IN
        SELECT s.*
        FROM alert_subscriptions s
        WHERE s.county_id = v_county_id
          AND s.is_active = TRUE
          AND p_alert_type = ANY(s.alert_types)
          AND p_severity >= s.severity_threshold
          AND (s.risk_threshold IS NULL OR p_risk_score >= s.risk_threshold)
    LOOP
        -- Queue delivery for each channel
        IF v_subscription.email IS NOT NULL THEN
            INSERT INTO alert_deliveries (alert_event_id, subscription_id, channel, recipient)
            VALUES (v_alert_id, v_subscription.id, 'email', v_subscription.email);
        END IF;
        
        IF v_subscription.webhook_url IS NOT NULL THEN
            INSERT INTO alert_deliveries (alert_event_id, subscription_id, channel, recipient)
            VALUES (v_alert_id, v_subscription.id, 'webhook', v_subscription.webhook_url);
        END IF;
        
        -- Update subscription trigger count
        UPDATE alert_subscriptions 
        SET trigger_count = trigger_count + 1, last_triggered = NOW()
        WHERE id = v_subscription.id;
    END LOOP;
    
    RETURN v_alert_id;
END;
$$ LANGUAGE plpgsql;

-- Function to acknowledge alert
CREATE OR REPLACE FUNCTION acknowledge_alert(
    p_alert_id UUID,
    p_acknowledged_by VARCHAR(100),
    p_notes TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE alert_events
    SET status = 'acknowledged',
        acknowledged_by = p_acknowledged_by,
        acknowledged_at = NOW(),
        acknowledged_notes = p_notes
    WHERE id = p_alert_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get active alerts for county
CREATE OR REPLACE FUNCTION get_active_alerts(
    p_county_fips VARCHAR(5),
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    alert_id UUID,
    alert_type alert_type,
    severity alert_severity,
    title VARCHAR(500),
    message TEXT,
    risk_score DECIMAL(5, 4),
    triggered_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ae.id as alert_id,
        ae.alert_type,
        ae.severity,
        ae.title,
        ae.message,
        ae.risk_score,
        ae.triggered_at,
        ae.expires_at
    FROM alert_events ae
    JOIN counties c ON ae.county_id = c.id
    WHERE c.fips_code = p_county_fips
      AND ae.status = 'active'
      AND (ae.expires_at IS NULL OR ae.expires_at > NOW())
    ORDER BY ae.triggered_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired alerts
CREATE OR REPLACE FUNCTION cleanup_expired_alerts()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    UPDATE alert_events
    SET status = 'resolved',
        resolution_notes = 'Auto-resolved: Expired',
        resolved_at = NOW()
    WHERE status = 'active'
      AND expires_at < NOW();
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VIEWS
-- ============================================

-- Active alerts summary
CREATE OR REPLACE VIEW active_alerts_summary AS
SELECT 
    ae.id,
    ae.alert_type,
    ae.severity,
    ae.title,
    c.fips_code,
    c.county_name,
    c.state_abbrev,
    ae.risk_score,
    ae.triggered_at,
    ae.expires_at,
    EXTRACT(EPOCH FROM (NOW() - ae.triggered_at))/3600 as hours_since_triggered
FROM alert_events ae
JOIN counties c ON ae.county_id = c.id
WHERE ae.status = 'active'
  AND (ae.expires_at IS NULL OR ae.expires_at > NOW())
ORDER BY ae.severity DESC, ae.triggered_at DESC;

-- Alert statistics by county
CREATE OR REPLACE VIEW county_alert_stats AS
SELECT 
    c.fips_code,
    c.county_name,
    c.state_abbrev,
    COUNT(*) FILTER (WHERE ae.status = 'active') as active_alerts,
    COUNT(*) FILTER (WHERE ae.triggered_at > NOW() - INTERVAL '7 days') as alerts_last_7_days,
    COUNT(*) FILTER (WHERE ae.triggered_at > NOW() - INTERVAL '30 days') as alerts_last_30_days,
    MAX(ae.triggered_at) as last_alert_at,
    COUNT(DISTINCT s.id) as subscription_count
FROM counties c
LEFT JOIN alert_events ae ON c.id = ae.county_id
LEFT JOIN alert_subscriptions s ON c.id = s.county_id AND s.is_active = TRUE
GROUP BY c.id, c.fips_code, c.county_name, c.state_abbrev;

-- Delivery statistics
CREATE OR REPLACE VIEW delivery_stats AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    channel,
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (sent_at - created_at))) as avg_send_time_seconds
FROM alert_deliveries
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at), channel, status
ORDER BY date DESC, channel;
