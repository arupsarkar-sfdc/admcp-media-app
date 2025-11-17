-- =====================================================================
-- Nike-Yahoo AdCP Platform - SQLite Schema
-- Post-Clean Room workflow database
-- =====================================================================

-- =====================================================================
-- CORE ENTITIES
-- =====================================================================

-- Tenants: Yahoo Publishers (Yahoo Sports, Yahoo Finance, etc.)
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    adapter_type TEXT NOT NULL,  -- 'yahoo_dsp', 'mock'
    adapter_config TEXT NOT NULL,  -- JSON string
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Principals: Authenticated entities (Nike, other advertisers)
CREATE TABLE IF NOT EXISTS principals (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    principal_id TEXT NOT NULL,  -- 'nike_advertiser'
    auth_token TEXT NOT NULL,  -- Static token for POC
    access_level TEXT DEFAULT 'standard',  -- 'standard', 'premium', 'enterprise'
    metadata TEXT,  -- JSON string
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    UNIQUE(tenant_id, principal_id)
);

-- Matched Audiences: Clean Room output (pre-matched segments)
-- KEY TABLE: Represents Nike customers ∩ Yahoo users overlap
CREATE TABLE IF NOT EXISTS matched_audiences (
    id TEXT PRIMARY KEY,
    segment_id TEXT NOT NULL UNIQUE,  -- 'nike_running_yahoo_sports'
    segment_name TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    principal_id TEXT NOT NULL,
    
    -- Overlap Metrics (from Clean Room)
    overlap_count INTEGER NOT NULL,  -- 850000
    total_nike_segment INTEGER,  -- Nike's total segment size
    total_yahoo_segment INTEGER,  -- Yahoo's total segment size
    match_rate REAL,  -- overlap_count / total_nike_segment
    
    -- Aggregated Demographics (no PII, k-anonymity applied)
    demographics TEXT NOT NULL,  -- JSON: {age_range, gender_split, hhi, geo}
    
    -- Engagement Scores
    engagement_score REAL,  -- 0.0 - 1.0
    quality_score REAL,  -- 0.0 - 1.0
    
    -- Privacy Parameters
    privacy_params TEXT,  -- JSON: {k_anonymity: 1000, epsilon: 0.1}
    
    -- Metadata
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT,  -- Data retention (90 days)
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (principal_id) REFERENCES principals(id)
);

-- Products: Advertising inventory packages
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    product_id TEXT NOT NULL,  -- 'yahoo_sports_display_enthusiasts'
    name TEXT NOT NULL,
    description TEXT,
    product_type TEXT,  -- 'display', 'video', 'native', 'ctv'
    
    -- Inventory Details
    properties TEXT NOT NULL,  -- JSON: ['yahoo.com/sports']
    formats TEXT NOT NULL,  -- JSON: Creative format specs
    targeting TEXT,  -- JSON: Available targeting options
    
    -- Matched Audience Reference (Clean Room linkage)
    matched_audience_ids TEXT,  -- JSON: ['nike_running_yahoo_sports']
    
    -- Pricing
    pricing TEXT NOT NULL,  -- JSON: {type: 'cpm', value: 12.50, currency: 'USD'}
    minimum_budget REAL,
    
    -- Reach Estimates
    estimated_reach INTEGER,  -- Total Yahoo reach
    matched_reach INTEGER,  -- Matched audience reach (from Clean Room)
    estimated_impressions INTEGER,
    
    -- Availability
    available_from TEXT,
    available_to TEXT,
    is_active INTEGER DEFAULT 1,
    
    -- Access Control
    principal_access TEXT,  -- JSON: Principal-specific pricing/access
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    UNIQUE(tenant_id, product_id)
);

-- Media Buys: Active advertising campaigns
CREATE TABLE IF NOT EXISTS media_buys (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    media_buy_id TEXT NOT NULL,  -- 'nike_sports_q1_2025'
    principal_id TEXT NOT NULL,
    
    -- Campaign Configuration
    product_ids TEXT NOT NULL,  -- JSON: ['yahoo_sports_display']
    total_budget REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    
    -- Flight Schedule
    flight_start_date TEXT NOT NULL,
    flight_end_date TEXT NOT NULL,
    
    -- Targeting (includes matched audience)
    targeting TEXT,  -- JSON: {matched_audience_id, geo, age, interests}
    matched_audience_id TEXT,  -- Link to matched_audiences table
    
    -- Creative Assignment
    assigned_creatives TEXT,  -- JSON: [{creative_id, product_id}]
    
    -- Status & Workflow
    status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'active', 'paused', 'completed'
    workflow_state TEXT,  -- JSON: Human-in-the-loop approval tracking
    
    -- Performance Metrics (cached from delivery)
    impressions_delivered INTEGER DEFAULT 0,
    spend REAL DEFAULT 0.00,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    
    -- External References
    external_campaign_id TEXT,  -- Yahoo DSP campaign ID
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (principal_id) REFERENCES principals(id),
    FOREIGN KEY (matched_audience_id) REFERENCES matched_audiences(id),
    UNIQUE(tenant_id, media_buy_id)
);

-- Creatives: Ad assets
CREATE TABLE IF NOT EXISTS creatives (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    creative_id TEXT NOT NULL,
    principal_id TEXT NOT NULL,
    
    -- Creative Details
    name TEXT NOT NULL,
    format TEXT NOT NULL,  -- 'display_300x250', 'video_15s', 'native'
    file_url TEXT NOT NULL,
    preview_url TEXT,
    
    -- Specifications
    dimensions TEXT,  -- JSON: {width: 300, height: 250}
    file_size_bytes INTEGER,
    duration_seconds INTEGER,  -- For video/audio
    
    -- Approval Workflow
    approval_status TEXT DEFAULT 'approved',  -- 'pending', 'approved', 'rejected'
    approval_notes TEXT,
    reviewed_by TEXT,
    reviewed_at TEXT,
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (principal_id) REFERENCES principals(id),
    UNIQUE(tenant_id, creative_id)
);

-- =====================================================================
-- PERFORMANCE & ANALYTICS
-- =====================================================================

-- Delivery Metrics: Campaign performance data
CREATE TABLE IF NOT EXISTS delivery_metrics (
    id TEXT PRIMARY KEY,
    media_buy_id TEXT NOT NULL,
    
    -- Time Dimension
    date TEXT NOT NULL,  -- YYYY-MM-DD
    hour INTEGER,  -- 0-23 for hourly granularity (NULL for daily)
    
    -- Metrics
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    spend REAL DEFAULT 0.00,
    
    -- Dimensions
    product_id TEXT,
    creative_id TEXT,
    geo TEXT,
    device_type TEXT,
    
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (media_buy_id) REFERENCES media_buys(id),
    UNIQUE(media_buy_id, date, hour, product_id, creative_id)
);

-- =====================================================================
-- AUDIT & COMPLIANCE
-- =====================================================================

-- Audit Log: Immutable record of all operations
CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    
    -- Request Context
    principal_id TEXT,
    tenant_id TEXT,
    
    -- Operation
    operation TEXT NOT NULL,  -- 'get_products', 'create_media_buy', etc.
    tool_name TEXT,  -- MCP tool name
    
    -- Request/Response
    request_params TEXT,  -- JSON
    response_data TEXT,  -- JSON
    status TEXT,  -- 'success', 'error', 'unauthorized'
    
    -- Metadata
    ip_address TEXT,
    user_agent TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (principal_id) REFERENCES principals(id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- =====================================================================
-- INDEXES
-- =====================================================================

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_products_tenant_active ON products(tenant_id, is_active);
CREATE INDEX IF NOT EXISTS idx_media_buys_tenant_status ON media_buys(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_media_buys_flight_dates ON media_buys(flight_start_date, flight_end_date);
CREATE INDEX IF NOT EXISTS idx_delivery_metrics_media_buy ON delivery_metrics(media_buy_id, date);
CREATE INDEX IF NOT EXISTS idx_audit_log_principal ON audit_log(principal_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_matched_audiences_principal ON matched_audiences(principal_id, tenant_id);

