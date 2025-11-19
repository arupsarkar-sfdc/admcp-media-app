-- =====================================================================
-- Nike-Yahoo AdCP Platform - Cloud-Native Schema v2.0
-- Target: Salesforce Data Cloud (transactional) + Snowflake (analytics)
-- AdCP v2.3.0 Compliant with Package-Based Structure
-- =====================================================================

-- =====================================================================
-- SALESFORCE DATA CLOUD TABLES (Transactional)
-- =====================================================================

-- ---------------------------------------------------------------------
-- CORE ENTITIES (No changes from v1)
-- ---------------------------------------------------------------------

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

-- ---------------------------------------------------------------------
-- NEW: AdCP v2.3.0 PACKAGE-BASED STRUCTURE
-- ---------------------------------------------------------------------

-- Media Buys: Active advertising campaigns (REFACTORED for AdCP v2.3.0)
CREATE TABLE IF NOT EXISTS media_buys (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    media_buy_id TEXT NOT NULL,  -- 'nike_air_max_spring_2025_20251119'
    principal_id TEXT NOT NULL,
    
    -- Campaign Metadata
    campaign_name TEXT NOT NULL,  -- NEW: Human-readable name
    adcp_version TEXT DEFAULT '2.3.0',  -- NEW: Track AdCP version
    
    -- Budget & Currency
    total_budget REAL NOT NULL,  -- Sum of all package budgets
    currency TEXT DEFAULT 'USD',
    
    -- Flight Schedule
    flight_start_date TEXT NOT NULL,
    flight_end_date TEXT NOT NULL,
    
    -- Matched Audience (Campaign-level)
    matched_audience_id TEXT,  -- Link to matched_audiences table
    
    -- Status & Workflow
    status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'active', 'paused', 'completed'
    workflow_state TEXT,  -- JSON: Human-in-the-loop approval tracking
    
    -- Performance Metrics (cached aggregates from Snowflake)
    impressions_delivered INTEGER DEFAULT 0,
    spend REAL DEFAULT 0.00,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    
    -- External References
    external_campaign_id TEXT,  -- Yahoo DSP campaign ID
    
    -- Metadata
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (principal_id) REFERENCES principals(id),
    FOREIGN KEY (matched_audience_id) REFERENCES matched_audiences(id),
    UNIQUE(tenant_id, media_buy_id)
);

-- NEW: Packages (AdCP v2.3.0 Core Entity)
-- Each media buy contains 1+ packages, each with its own product, budget, and formats
CREATE TABLE IF NOT EXISTS packages (
    id TEXT PRIMARY KEY,
    media_buy_id TEXT NOT NULL,  -- Parent campaign
    package_id TEXT NOT NULL,  -- 'pkg_1', 'pkg_2', etc.
    
    -- Product Reference
    product_id TEXT NOT NULL,  -- Link to products table
    
    -- Budget Allocation
    budget REAL NOT NULL,  -- Per-package budget
    currency TEXT DEFAULT 'USD',
    
    -- Pacing & Pricing
    pacing TEXT DEFAULT 'even',  -- 'even', 'asap', 'frontloaded'
    pricing_strategy TEXT DEFAULT 'cpm',  -- 'cpm', 'cpc', 'cpa', 'cpv'
    
    -- Targeting Overlay (package-specific targeting)
    targeting_overlay TEXT,  -- JSON: {geo: ['US'], device: ['mobile']}
    
    -- Performance Metrics (cached from Snowflake)
    impressions_delivered INTEGER DEFAULT 0,
    spend REAL DEFAULT 0.00,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (media_buy_id) REFERENCES media_buys(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE(media_buy_id, package_id)
);

-- NEW: Package Formats (AdCP v2.3.0 Creative Format Association)
-- Junction table linking packages to required creative formats
CREATE TABLE IF NOT EXISTS package_formats (
    id TEXT PRIMARY KEY,
    package_id TEXT NOT NULL,  -- Link to packages table
    
    -- AdCP v2.3.0 format_id structure
    agent_url TEXT NOT NULL,  -- 'http://localhost:8080/mcp'
    format_id TEXT NOT NULL,  -- 'display_728x90', 'video_preroll_640x480', etc.
    
    -- Format Metadata (denormalized for performance)
    format_name TEXT,  -- 'Display - Leaderboard (728x90)'
    format_type TEXT,  -- 'display', 'video', 'native'
    
    -- Creative Assignment (optional - links to actual creative)
    assigned_creative_id TEXT,  -- Link to creatives table
    
    -- Metadata
    created_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_creative_id) REFERENCES creatives(id),
    UNIQUE(package_id, agent_url, format_id)
);

-- =====================================================================
-- SNOWFLAKE TABLES (Analytics & Time-Series Data)
-- =====================================================================

-- Delivery Metrics: Campaign performance data (ENHANCED for package-level tracking)
-- NOTE: This will be replicated to Snowflake for analytics
CREATE TABLE IF NOT EXISTS delivery_metrics (
    id TEXT PRIMARY KEY,
    media_buy_id TEXT NOT NULL,
    package_id TEXT,  -- NEW: Track metrics at package level
    
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
    format_id TEXT,  -- NEW: Track performance by format
    geo TEXT,
    device_type TEXT,
    
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (media_buy_id) REFERENCES media_buys(id),
    FOREIGN KEY (package_id) REFERENCES packages(id),
    UNIQUE(media_buy_id, package_id, date, hour, product_id, creative_id, format_id)
);

-- Audit Log: Immutable record of all operations
-- NOTE: This will be replicated to Snowflake for compliance reporting
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
-- INDEXES (Optimized for Salesforce Data Cloud & Snowflake)
-- =====================================================================

-- Salesforce Data Cloud Indexes (Transactional Queries)
CREATE INDEX IF NOT EXISTS idx_products_tenant_active ON products(tenant_id, is_active);
CREATE INDEX IF NOT EXISTS idx_media_buys_tenant_status ON media_buys(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_media_buys_flight_dates ON media_buys(flight_start_date, flight_end_date);
CREATE INDEX IF NOT EXISTS idx_matched_audiences_principal ON matched_audiences(principal_id, tenant_id);

-- NEW: Package Indexes
CREATE INDEX IF NOT EXISTS idx_packages_media_buy ON packages(media_buy_id);
CREATE INDEX IF NOT EXISTS idx_packages_product ON packages(product_id);
CREATE INDEX IF NOT EXISTS idx_package_formats_package ON package_formats(package_id);
CREATE INDEX IF NOT EXISTS idx_package_formats_format ON package_formats(format_id);

-- Snowflake Indexes (Analytics Queries)
CREATE INDEX IF NOT EXISTS idx_delivery_metrics_media_buy ON delivery_metrics(media_buy_id, date);
CREATE INDEX IF NOT EXISTS idx_delivery_metrics_package ON delivery_metrics(package_id, date);  -- NEW
CREATE INDEX IF NOT EXISTS idx_delivery_metrics_format ON delivery_metrics(format_id, date);  -- NEW
CREATE INDEX IF NOT EXISTS idx_audit_log_principal ON audit_log(principal_id, timestamp);

-- =====================================================================
-- MIGRATION NOTES
-- =====================================================================
-- 
-- PHASE 1: SQLite (Current State)
-- - All data in single SQLite database
-- - Packages stored as JSON in media_buys.targeting field
-- 
-- PHASE 2: SQLite with Normalized Packages (This Schema)
-- - Extract packages from JSON to dedicated tables
-- - Add package_formats junction table
-- - Maintain backward compatibility
-- 
-- PHASE 3: Salesforce Data Cloud Migration
-- - Migrate transactional tables to Data Cloud
-- - Use Data Cloud's native Salesforce Object references
-- - Leverage Einstein for audience insights
-- 
-- PHASE 4: Snowflake Migration
-- - Stream delivery_metrics to Snowflake
-- - Stream audit_log to Snowflake
-- - Use Snowflake for BI dashboards and ML models
-- 
-- PHASE 5: Hybrid Architecture
-- - Salesforce Data Cloud: Campaign management, product catalog
-- - Snowflake: Analytics, reporting, ML training data
-- - Real-time sync via Salesforce Data Streams
-- 
-- =====================================================================

