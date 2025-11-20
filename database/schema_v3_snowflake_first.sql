-- =====================================================================
-- Nike-Yahoo AdCP Platform - Snowflake-First Schema v3.0
-- Architecture: All data in Snowflake, virtualized to Salesforce Data Cloud
-- Data Cloud provides: Relationship definitions + query interface
-- =====================================================================

-- =====================================================================
-- CORE ENTITIES (All in Snowflake, virtualized to Data Cloud)
-- =====================================================================

-- Tenants: Yahoo Publishers (Yahoo Sports, Yahoo Finance, etc.)
CREATE OR REPLACE TABLE tenants (
    id STRING PRIMARY KEY,
    name STRING NOT NULL UNIQUE,
    slug STRING NOT NULL UNIQUE,
    adapter_type STRING NOT NULL,  -- 'yahoo_dsp', 'mock'
    adapter_config VARIANT NOT NULL,  -- JSON object
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Salesforce Integration
    salesforce_account_id STRING,  -- Links to Account.Id in Salesforce
    
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Principals: Authenticated entities (Nike, other advertisers)
CREATE OR REPLACE TABLE principals (
    id STRING PRIMARY KEY,
    tenant_id STRING NOT NULL,
    name STRING NOT NULL,
    principal_id STRING NOT NULL,  -- 'nike_advertiser'
    auth_token STRING NOT NULL,
    access_level STRING DEFAULT 'standard',
    metadata VARIANT,  -- JSON object
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Salesforce Integration
    salesforce_contact_id STRING,  -- Links to Contact.Id in Salesforce
    salesforce_account_id STRING,  -- Links to Account.Id in Salesforce
    
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    UNIQUE (tenant_id, principal_id)
);

-- Matched Audiences: Clean Room output (pre-matched segments)
-- KEY TABLE: Represents Nike customers ∩ Yahoo users overlap
-- 1:1 RELATIONSHIP with Salesforce Contact
CREATE OR REPLACE TABLE matched_audiences (
    id STRING PRIMARY KEY,
    segment_id STRING NOT NULL UNIQUE,  -- 'nike_running_yahoo_sports'
    segment_name STRING NOT NULL,
    tenant_id STRING NOT NULL,
    principal_id STRING NOT NULL,
    
    -- Salesforce Integration: 1:1 with Contact
    salesforce_contact_id STRING UNIQUE,  -- 1:1 with Contact.Id
    salesforce_account_id STRING,         -- Many:1 with Account.Id
    
    -- Overlap Metrics (from Clean Room)
    overlap_count INTEGER NOT NULL,
    total_nike_segment INTEGER,
    total_yahoo_segment INTEGER,
    match_rate FLOAT,
    
    -- Aggregated Demographics (no PII, k-anonymity applied)
    demographics VARIANT NOT NULL,  -- JSON
    
    -- Engagement Scores
    engagement_score FLOAT,
    quality_score FLOAT,
    
    -- Privacy Parameters
    privacy_params VARIANT,  -- JSON
    
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    expires_at TIMESTAMP_NTZ,
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (principal_id) REFERENCES principals(id)
);

-- Products: Advertising inventory packages
CREATE OR REPLACE TABLE products (
    id STRING PRIMARY KEY,
    tenant_id STRING NOT NULL,
    product_id STRING NOT NULL,
    name STRING NOT NULL,
    description STRING,
    product_type STRING,  -- 'display', 'video', 'native', 'ctv'
    
    -- Inventory Details
    properties VARIANT NOT NULL,  -- JSON array
    formats VARIANT NOT NULL,  -- JSON array
    targeting VARIANT,  -- JSON object
    
    -- Matched Audience Reference (Clean Room linkage)
    matched_audience_ids VARIANT,  -- JSON array
    
    -- Pricing
    pricing VARIANT NOT NULL,  -- JSON object
    minimum_budget FLOAT,
    
    -- Reach Estimates
    estimated_reach INTEGER,
    matched_reach INTEGER,
    estimated_impressions INTEGER,
    
    -- Availability
    available_from TIMESTAMP_NTZ,
    available_to TIMESTAMP_NTZ,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Access Control
    principal_access VARIANT,  -- JSON object
    
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    UNIQUE (tenant_id, product_id)
);

-- Creatives: Ad assets
CREATE OR REPLACE TABLE creatives (
    id STRING PRIMARY KEY,
    tenant_id STRING NOT NULL,
    creative_id STRING NOT NULL,
    principal_id STRING NOT NULL,
    
    -- Creative Details
    name STRING NOT NULL,
    format STRING NOT NULL,  -- 'display_300x250', 'video_15s', 'native'
    file_url STRING NOT NULL,
    preview_url STRING,
    
    -- Specifications
    dimensions VARIANT,  -- JSON object
    file_size_bytes INTEGER,
    duration_seconds INTEGER,
    
    -- Approval Workflow
    approval_status STRING DEFAULT 'approved',
    approval_notes STRING,
    reviewed_by STRING,
    reviewed_at TIMESTAMP_NTZ,
    
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (principal_id) REFERENCES principals(id),
    UNIQUE (tenant_id, creative_id)
);

-- =====================================================================
-- AdCP v2.3.0 PACKAGE-BASED CAMPAIGN STRUCTURE
-- =====================================================================

-- Media Buys: Active advertising campaigns
CREATE OR REPLACE TABLE media_buys (
    id STRING PRIMARY KEY,
    tenant_id STRING NOT NULL,
    media_buy_id STRING NOT NULL,
    principal_id STRING NOT NULL,
    
    -- Campaign Metadata (AdCP v2.3.0)
    campaign_name STRING NOT NULL,
    adcp_version STRING DEFAULT '2.3.0',
    
    -- Salesforce Integration
    salesforce_opportunity_id STRING,  -- Links to Opportunity.Id
    salesforce_campaign_id STRING,     -- Links to Campaign.Id (Standard object)
    
    -- Budget & Currency
    total_budget FLOAT NOT NULL,
    currency STRING DEFAULT 'USD',
    
    -- Flight Schedule
    flight_start_date DATE NOT NULL,
    flight_end_date DATE NOT NULL,
    
    -- Matched Audience (Campaign-level)
    matched_audience_id STRING,
    
    -- Status & Workflow
    status STRING DEFAULT 'pending',  -- 'pending', 'approved', 'active', 'paused', 'completed'
    workflow_state VARIANT,  -- JSON object
    
    -- Performance Metrics (cached aggregates from delivery_metrics)
    impressions_delivered INTEGER DEFAULT 0,
    spend FLOAT DEFAULT 0.0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    
    -- External References
    external_campaign_id STRING,  -- Yahoo DSP campaign ID
    
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (principal_id) REFERENCES principals(id),
    FOREIGN KEY (matched_audience_id) REFERENCES matched_audiences(id),
    UNIQUE (tenant_id, media_buy_id)
);

-- Packages: AdCP v2.3.0 Core Entity
CREATE OR REPLACE TABLE packages (
    id STRING PRIMARY KEY,
    media_buy_id STRING NOT NULL,
    package_id STRING NOT NULL,  -- 'pkg_1', 'pkg_2', etc.
    
    -- Product Reference
    product_id STRING NOT NULL,
    
    -- Budget Allocation
    budget FLOAT NOT NULL,
    currency STRING DEFAULT 'USD',
    
    -- Pacing & Pricing
    pacing STRING DEFAULT 'even',  -- 'even', 'asap', 'frontloaded'
    pricing_strategy STRING DEFAULT 'cpm',  -- 'cpm', 'cpc', 'cpa', 'cpv'
    
    -- Targeting Overlay (package-specific targeting)
    targeting_overlay VARIANT,  -- JSON object
    
    -- Performance Metrics (cached from delivery_metrics)
    impressions_delivered INTEGER DEFAULT 0,
    spend FLOAT DEFAULT 0.0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (media_buy_id) REFERENCES media_buys(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE (media_buy_id, package_id)
);

-- Package Formats: AdCP v2.3.0 Creative Format Association
CREATE OR REPLACE TABLE package_formats (
    id STRING PRIMARY KEY,
    package_id STRING NOT NULL,
    
    -- AdCP v2.3.0 format_id structure
    agent_url STRING NOT NULL,
    format_id STRING NOT NULL,
    
    -- Format Metadata (denormalized for performance)
    format_name STRING,
    format_type STRING,  -- 'display', 'video', 'native'
    
    -- Creative Assignment (optional)
    assigned_creative_id STRING,
    
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_creative_id) REFERENCES creatives(id),
    UNIQUE (package_id, agent_url, format_id)
);

-- =====================================================================
-- ANALYTICS & TIME-SERIES DATA
-- =====================================================================

-- Delivery Metrics: Campaign performance data (time-series)
CREATE OR REPLACE TABLE delivery_metrics (
    id STRING PRIMARY KEY,
    media_buy_id STRING NOT NULL,
    package_id STRING,  -- Package-level tracking
    
    -- Time Dimension
    date DATE NOT NULL,
    hour INTEGER,  -- 0-23 for hourly granularity (NULL for daily)
    
    -- Metrics
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    spend FLOAT DEFAULT 0.0,
    
    -- Dimensions
    product_id STRING,
    creative_id STRING,
    format_id STRING,  -- Format-level tracking
    geo STRING,
    device_type STRING,
    
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (media_buy_id) REFERENCES media_buys(id),
    FOREIGN KEY (package_id) REFERENCES packages(id),
    UNIQUE (media_buy_id, package_id, date, hour, product_id, creative_id, format_id, geo, device_type)
);

-- Audit Log: Immutable record of all operations
CREATE OR REPLACE TABLE audit_log (
    id STRING PRIMARY KEY,
    
    -- Request Context
    principal_id STRING,
    tenant_id STRING,
    
    -- Operation
    operation STRING NOT NULL,
    tool_name STRING,
    
    -- Request/Response
    request_params VARIANT,  -- JSON object
    response_data VARIANT,  -- JSON object
    status STRING,
    
    -- Metadata
    ip_address STRING,
    user_agent STRING,
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (principal_id) REFERENCES principals(id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- =====================================================================
-- INDEXES (Snowflake clustering keys for performance)
-- =====================================================================

-- Transactional tables
ALTER TABLE products CLUSTER BY (tenant_id, is_active);
ALTER TABLE media_buys CLUSTER BY (tenant_id, status, flight_start_date);
ALTER TABLE packages CLUSTER BY (media_buy_id);
ALTER TABLE matched_audiences CLUSTER BY (principal_id, tenant_id);

-- Analytics tables (time-series optimized)
ALTER TABLE delivery_metrics CLUSTER BY (date, media_buy_id);
ALTER TABLE audit_log CLUSTER BY (timestamp, principal_id);

-- =====================================================================
-- SALESFORCE DATA CLOUD RELATIONSHIP DEFINITIONS
-- (Defined in Data Cloud UI, documented here for reference)
-- =====================================================================

/*
In Salesforce Data Cloud, define these relationships:

1. matched_audiences → Contact (1:1)
   FROM: snowflake_matched_audiences.salesforce_contact_id
   TO:   Contact.Id
   CARDINALITY: ONE_TO_ONE
   
2. principals → Contact (Many:1)
   FROM: snowflake_principals.salesforce_contact_id
   TO:   Contact.Id
   CARDINALITY: MANY_TO_ONE

3. tenants → Account (1:1)
   FROM: snowflake_tenants.salesforce_account_id
   TO:   Account.Id
   CARDINALITY: ONE_TO_ONE

4. media_buys → Opportunity (Many:1)
   FROM: snowflake_media_buys.salesforce_opportunity_id
   TO:   Opportunity.Id
   CARDINALITY: MANY_TO_ONE

5. media_buys → Campaign (Many:1)
   FROM: snowflake_media_buys.salesforce_campaign_id
   TO:   Campaign.Id
   CARDINALITY: MANY_TO_ONE
*/

-- =====================================================================
-- EXAMPLE UNIFIED QUERIES (via Data Cloud)
-- =====================================================================

/*
-- Query 1: Get all campaigns for a Contact
SELECT 
    c.Name AS contact_name,
    c.Email,
    ma.segment_name,
    ma.overlap_count,
    mb.campaign_name,
    mb.total_budget,
    mb.status
FROM Contact c                              -- Native Salesforce
JOIN snowflake_matched_audiences ma         -- Snowflake via Zero Copy
  ON ma.salesforce_contact_id = c.Id        -- 1:1 relationship
JOIN snowflake_media_buys mb                -- Snowflake via Zero Copy
  ON mb.matched_audience_id = ma.id
WHERE c.Id = '003xx000004TmiOAAS';

-- Query 2: Get package performance for an Opportunity
SELECT 
    opp.Name AS opportunity_name,
    opp.Amount AS opportunity_amount,
    mb.campaign_name,
    p.package_id,
    p.budget,
    SUM(dm.impressions) AS total_impressions,
    SUM(dm.clicks) AS total_clicks,
    SUM(dm.spend) AS total_spend
FROM Opportunity opp                        -- Native Salesforce
JOIN snowflake_media_buys mb               -- Snowflake via Zero Copy
  ON mb.salesforce_opportunity_id = opp.Id
JOIN snowflake_packages p                   -- Snowflake via Zero Copy
  ON p.media_buy_id = mb.id
JOIN snowflake_delivery_metrics dm          -- Snowflake via Zero Copy
  ON dm.package_id = p.id
WHERE opp.Id = '006xx000001RZjBAAW'
GROUP BY opp.Name, opp.Amount, mb.campaign_name, 
         p.package_id, p.budget;

-- Query 3: Get matched audience insights for an Account
SELECT 
    acc.Name AS account_name,
    COUNT(DISTINCT ma.id) AS total_audiences,
    SUM(ma.overlap_count) AS total_matched_users,
    AVG(ma.engagement_score) AS avg_engagement,
    COUNT(DISTINCT mb.id) AS total_campaigns
FROM Account acc                            -- Native Salesforce
JOIN snowflake_matched_audiences ma         -- Snowflake via Zero Copy
  ON ma.salesforce_account_id = acc.Id
LEFT JOIN snowflake_media_buys mb           -- Snowflake via Zero Copy
  ON mb.matched_audience_id = ma.id
WHERE acc.Id = '001xx000003DGb2AAG'
GROUP BY acc.Name;
*/

-- =====================================================================
-- COMMENTS & DOCUMENTATION
-- =====================================================================

COMMENT ON TABLE tenants IS 'Yahoo publisher configuration with Salesforce Account linkage';
COMMENT ON TABLE principals IS 'Advertiser authentication with Salesforce Contact linkage';
COMMENT ON TABLE matched_audiences IS 'Clean Room matched segments (1:1 with Salesforce Contact)';
COMMENT ON TABLE media_buys IS 'AdCP v2.3.0 campaigns with Salesforce Opportunity linkage';
COMMENT ON TABLE packages IS 'Package-based budget and targeting structure';
COMMENT ON TABLE package_formats IS 'Creative format requirements per package';
COMMENT ON TABLE delivery_metrics IS 'Time-series performance metrics';

COMMENT ON COLUMN matched_audiences.salesforce_contact_id IS '1:1 relationship with Contact.Id in Salesforce';
COMMENT ON COLUMN media_buys.salesforce_opportunity_id IS 'Links campaign to Opportunity in Salesforce';
COMMENT ON COLUMN tenants.salesforce_account_id IS 'Links Yahoo publisher to Account in Salesforce';

