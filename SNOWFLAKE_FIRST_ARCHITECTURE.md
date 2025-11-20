# Snowflake-First Architecture with Salesforce Data Cloud

**Strategy**: All AdCP data in Snowflake, virtualized to Salesforce Data Cloud via Zero Copy  
**Data Cloud Role**: Semantic layer with relationship definitions  
**MCP Server**: Single connection to Data Cloud API

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│         Nike MCP Server (FastMCP Cloud)                  │
│         Connects ONLY to Data Cloud                      │
└────────────────────┬─────────────────────────────────────┘
                     │ Salesforce Data Cloud API
                     │ (REST/GraphQL)
                     ▼
┌──────────────────────────────────────────────────────────┐
│      SALESFORCE DATA CLOUD                               │
│      Semantic Layer + Relationship Definitions           │
│                                                          │
│  ┌─────────────────────┐  ┌───────────────────────────┐ │
│  │ Native Salesforce   │  │ Zero Copy Virtual Tables  │ │
│  │                     │  │ (from Snowflake)          │ │
│  │ • Contact           │  │                           │ │
│  │ • Account           │  │ • tenants                 │ │
│  │ • Opportunity       │  │ • principals              │ │
│  │ • Campaign          │  │ • matched_audiences       │ │
│  │                     │  │ • products                │ │
│  │                     │  │ • media_buys              │ │
│  │                     │  │ • packages                │ │
│  │                     │  │ • package_formats         │ │
│  │                     │  │ • delivery_metrics        │ │
│  │                     │  │ • audit_log               │ │
│  └─────────────────────┘  └───────────────────────────┘ │
│           ↕                          ↕                   │
│  Relationships Defined:                                  │
│  1. matched_audiences.salesforce_contact_id = Contact.Id │
│     CARDINALITY: ONE_TO_ONE                              │
│  2. media_buys.salesforce_opportunity_id = Opportunity.Id│
│     CARDINALITY: MANY_TO_ONE                             │
│  3. tenants.salesforce_account_id = Account.Id           │
│     CARDINALITY: ONE_TO_ONE                              │
└──────────────────────────┼───────────────────────────────┘
                           │ Zero Copy (No Data Movement)
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    SNOWFLAKE                             │
│         SINGLE SOURCE OF TRUTH FOR ALL ADCP DATA         │
│                                                          │
│  Database: NIKE_YAHOO_ADCP                               │
│  Schema: PRODUCTION                                      │
│                                                          │
│  Tables:                                                 │
│  ├─ tenants (Yahoo publishers)                           │
│  ├─ principals (Nike advertisers)                        │
│  ├─ matched_audiences (Clean Room segments)              │
│  ├─ products (Inventory catalog)                         │
│  ├─ media_buys (Campaigns)                               │
│  ├─ packages (AdCP v2.3.0 packages)                      │
│  ├─ package_formats (Creative requirements)              │
│  ├─ delivery_metrics (Performance time-series)           │
│  └─ audit_log (Compliance trail)                         │
│                                                          │
│  Benefits:                                               │
│  • $23/TB/month storage (vs $250/GB in Salesforce!)     │
│  • Petabyte scale                                        │
│  • Time Travel (90 days)                                 │
│  • Full SQL power                                        │
└──────────────────────────────────────────────────────────┘
```

---

## Why This Architecture?

### **1. Cost Efficiency** 💰

| Component | Salesforce Data Cloud | Snowflake |
|-----------|----------------------|-----------|
| Storage | $250/GB/month | $23/TB/month (~10,000x cheaper!) |
| Compute | Included in license | $2/credit (pay per use) |
| **10 TB AdCP data** | **$2.5M/month** | **$230/month** |

### **2. Scalability** 📈
- Snowflake handles petabyte-scale data
- No Salesforce storage limits
- Elastic compute (scale up/down automatically)

### **3. Performance** ⚡
- Snowflake optimized for analytics
- Clustering keys for fast queries
- Zero Copy = no ETL lag
- Time Travel for historical queries

### **4. Salesforce Integration** 🔗
- Query Snowflake data AS IF it's in Salesforce
- Join with Contact, Account, Opportunity
- Einstein Analytics on Snowflake data
- Salesforce workflows triggered by Snowflake events

---

## Implementation Steps

### **Phase 1: Create Snowflake Database**

```sql
-- 1. Create database and schema
CREATE DATABASE NIKE_YAHOO_ADCP;
CREATE SCHEMA PRODUCTION;

USE DATABASE NIKE_YAHOO_ADCP;
USE SCHEMA PRODUCTION;

-- 2. Execute schema_v3_snowflake_first.sql
-- This creates all tables with Salesforce relationship columns

-- 3. Create service account for Data Cloud
CREATE ROLE data_cloud_reader;
GRANT USAGE ON DATABASE NIKE_YAHOO_ADCP TO ROLE data_cloud_reader;
GRANT USAGE ON SCHEMA PRODUCTION TO ROLE data_cloud_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA PRODUCTION TO ROLE data_cloud_reader;
GRANT SELECT ON FUTURE TABLES IN SCHEMA PRODUCTION TO ROLE data_cloud_reader;

CREATE USER salesforce_datacloud
  PASSWORD = 'secure_password'
  DEFAULT_ROLE = data_cloud_reader
  DEFAULT_WAREHOUSE = ADCP_QUERY_WH;

GRANT ROLE data_cloud_reader TO USER salesforce_datacloud;
```

---

### **Phase 2: Configure Data Cloud Zero Copy**

#### **Step 2.1: Add Snowflake Connection in Data Cloud**

```
Salesforce Setup
  → Data Cloud
  → Data Streams
  → External Connections
  → New External Connection

Connection Details:
  Name: Nike Yahoo AdCP Snowflake
  Type: Snowflake
  Account: nike_adcp.us-west-2.snowflakecomputing.com
  Database: NIKE_YAHOO_ADCP
  Schema: PRODUCTION
  Username: salesforce_datacloud
  Password: [secure_password]
  Warehouse: ADCP_QUERY_WH
  
Features:
  ✅ Enable Zero Copy
  ✅ Enable Data Virtualization
  ✅ Enable Einstein Analytics Access
```

#### **Step 2.2: Create Virtual Tables in Data Cloud**

```sql
-- In Salesforce Data Cloud SQL Editor

-- Virtualize all Snowflake tables
CREATE EXTERNAL TABLE snowflake_tenants
USING SNOWFLAKE CONNECTION nike_snowflake
FROM NIKE_YAHOO_ADCP.PRODUCTION.TENANTS;

CREATE EXTERNAL TABLE snowflake_principals
USING SNOWFLAKE CONNECTION nike_snowflake
FROM NIKE_YAHOO_ADCP.PRODUCTION.PRINCIPALS;

CREATE EXTERNAL TABLE snowflake_matched_audiences
USING SNOWFLAKE CONNECTION nike_snowflake
FROM NIKE_YAHOO_ADCP.PRODUCTION.MATCHED_AUDIENCES;

CREATE EXTERNAL TABLE snowflake_products
USING SNOWFLAKE CONNECTION nike_snowflake
FROM NIKE_YAHOO_ADCP.PRODUCTION.PRODUCTS;

CREATE EXTERNAL TABLE snowflake_media_buys
USING SNOWFLAKE CONNECTION nike_snowflake
FROM NIKE_YAHOO_ADCP.PRODUCTION.MEDIA_BUYS;

CREATE EXTERNAL TABLE snowflake_packages
USING SNOWFLAKE CONNECTION nike_snowflake
FROM NIKE_YAHOO_ADCP.PRODUCTION.PACKAGES;

CREATE EXTERNAL TABLE snowflake_package_formats
USING SNOWFLAKE CONNECTION nike_snowflake
FROM NIKE_YAHOO_ADCP.PRODUCTION.PACKAGE_FORMATS;

CREATE EXTERNAL TABLE snowflake_delivery_metrics
USING SNOWFLAKE CONNECTION nike_snowflake
FROM NIKE_YAHOO_ADCP.PRODUCTION.DELIVERY_METRICS;

CREATE EXTERNAL TABLE snowflake_audit_log
USING SNOWFLAKE CONNECTION nike_snowflake
FROM NIKE_YAHOO_ADCP.PRODUCTION.AUDIT_LOG;
```

---

### **Phase 3: Define Relationships in Data Cloud**

#### **Relationship 1: matched_audiences → Contact (1:1)**

```
Data Cloud → Data Model → Relationships → New Relationship

Name: MatchedAudience_to_Contact
Description: One-to-one relationship between Clean Room matched audience and Salesforce Contact

From Object: snowflake_matched_audiences
From Field: salesforce_contact_id

To Object: Contact
To Field: Id

Cardinality: ONE_TO_ONE
Relationship Label: Matched Audience
```

#### **Relationship 2: media_buys → Opportunity (Many:1)**

```
Name: MediaBuy_to_Opportunity
Description: Link AdCP campaigns to Salesforce Opportunities

From Object: snowflake_media_buys
From Field: salesforce_opportunity_id

To Object: Opportunity
To Field: Id

Cardinality: MANY_TO_ONE
Relationship Label: AdCP Campaigns
```

#### **Relationship 3: tenants → Account (1:1)**

```
Name: Tenant_to_Account
Description: Link Yahoo publishers to Salesforce Accounts

From Object: snowflake_tenants
From Field: salesforce_account_id

To Object: Account
To Field: Id

Cardinality: ONE_TO_ONE
Relationship Label: Publisher Account
```

#### **Relationship 4: principals → Contact (Many:1)**

```
Name: Principal_to_Contact
Description: Link advertisers to Salesforce Contacts

From Object: snowflake_principals
From Field: salesforce_contact_id

To Object: Contact
To Field: Id

Cardinality: MANY_TO_ONE
Relationship Label: Advertiser Principals
```

---

### **Phase 4: MCP Server Implementation**

#### **Unified Data Client**

```python
# yahoo_mcp_server/database/unified_data_client.py

from salesforce_data_cloud import DataCloudAPI
import os

class UnifiedDataClient:
    """
    Single connection point to Salesforce Data Cloud
    Queries both native Salesforce objects AND Snowflake tables via Zero Copy
    """
    
    def __init__(self):
        self.data_cloud = DataCloudAPI({
            "instance_url": os.getenv("SFDC_INSTANCE_URL"),
            "client_id": os.getenv("SFDC_CLIENT_ID"),
            "client_secret": os.getenv("SFDC_CLIENT_SECRET"),
            "username": os.getenv("SFDC_USERNAME"),
            "password": os.getenv("SFDC_PASSWORD")
        })
    
    # ================================================================
    # CREATE OPERATIONS (Write to Snowflake via Data Cloud)
    # ================================================================
    
    async def create_campaign(self, campaign_data: dict):
        """
        Create campaign in Snowflake via Data Cloud API
        Data Cloud writes to Snowflake automatically
        """
        return await self.data_cloud.insert(
            table="snowflake_media_buys",
            data=campaign_data
        )
    
    async def create_package(self, package_data: dict):
        """Create package in Snowflake via Data Cloud"""
        return await self.data_cloud.insert(
            table="snowflake_packages",
            data=package_data
        )
    
    async def create_package_format(self, format_data: dict):
        """Create package format in Snowflake via Data Cloud"""
        return await self.data_cloud.insert(
            table="snowflake_package_formats",
            data=format_data
        )
    
    # ================================================================
    # READ OPERATIONS (Query Snowflake via Data Cloud)
    # ================================================================
    
    async def get_campaign(self, media_buy_id: str):
        """Get campaign from Snowflake"""
        query = f"""
        SELECT * FROM snowflake_media_buys
        WHERE media_buy_id = '{media_buy_id}'
        """
        return await self.data_cloud.query(query)
    
    async def get_products(self, tenant_id: str, filters: dict = None):
        """Get products from Snowflake"""
        query = f"""
        SELECT * FROM snowflake_products
        WHERE tenant_id = '{tenant_id}'
          AND is_active = TRUE
        """
        return await self.data_cloud.query(query)
    
    # ================================================================
    # UNIFIED QUERIES (Join Snowflake + Salesforce)
    # ================================================================
    
    async def get_campaign_for_contact(self, contact_id: str):
        """
        Query campaigns for a Salesforce Contact
        Joins native Salesforce Contact with Snowflake tables via relationship
        """
        query = f"""
        SELECT 
            c.Id AS contact_id,
            c.Name AS contact_name,
            c.Email,
            ma.segment_name,
            ma.overlap_count,
            mb.campaign_name,
            mb.total_budget,
            mb.status,
            mb.flight_start_date,
            mb.flight_end_date
        FROM Contact c
        JOIN snowflake_matched_audiences ma 
          ON ma.salesforce_contact_id = c.Id
        JOIN snowflake_media_buys mb 
          ON mb.matched_audience_id = ma.id
        WHERE c.Id = '{contact_id}'
        ORDER BY mb.created_at DESC
        """
        return await self.data_cloud.query(query)
    
    async def get_campaign_performance_with_opportunity(
        self,
        opportunity_id: str
    ):
        """
        Get campaign performance linked to Salesforce Opportunity
        Joins Opportunity → media_buys → packages → delivery_metrics
        """
        query = f"""
        SELECT 
            opp.Id AS opportunity_id,
            opp.Name AS opportunity_name,
            opp.Amount AS opportunity_amount,
            opp.StageName,
            mb.campaign_name,
            mb.total_budget,
            p.package_id,
            p.budget AS package_budget,
            DATE_TRUNC('day', dm.date) AS date,
            SUM(dm.impressions) AS daily_impressions,
            SUM(dm.clicks) AS daily_clicks,
            SUM(dm.spend) AS daily_spend
        FROM Opportunity opp
        JOIN snowflake_media_buys mb 
          ON mb.salesforce_opportunity_id = opp.Id
        JOIN snowflake_packages p 
          ON p.media_buy_id = mb.id
        JOIN snowflake_delivery_metrics dm 
          ON dm.package_id = p.id
        WHERE opp.Id = '{opportunity_id}'
        GROUP BY opp.Id, opp.Name, opp.Amount, opp.StageName,
                 mb.campaign_name, mb.total_budget, p.package_id, 
                 p.budget, DATE_TRUNC('day', dm.date)
        ORDER BY date DESC
        """
        return await self.data_cloud.query(query)
    
    async def get_matched_audience_insights_by_account(
        self,
        account_id: str
    ):
        """
        Get matched audience insights for an Account
        Shows all Clean Room segments linked to this Account
        """
        query = f"""
        SELECT 
            acc.Id AS account_id,
            acc.Name AS account_name,
            ma.segment_id,
            ma.segment_name,
            ma.overlap_count,
            ma.engagement_score,
            ma.quality_score,
            COUNT(DISTINCT mb.id) AS total_campaigns,
            SUM(mb.total_budget) AS total_budget_spent
        FROM Account acc
        JOIN snowflake_matched_audiences ma 
          ON ma.salesforce_account_id = acc.Id
        LEFT JOIN snowflake_media_buys mb 
          ON mb.matched_audience_id = ma.id
        WHERE acc.Id = '{account_id}'
        GROUP BY acc.Id, acc.Name, ma.segment_id, ma.segment_name,
                 ma.overlap_count, ma.engagement_score, ma.quality_score
        """
        return await self.data_cloud.query(query)
```

---

### **Phase 5: Update MCP Server Tools**

```python
# yahoo_mcp_server/server_http.py

from database.unified_data_client import UnifiedDataClient

# Initialize unified client
data_client = UnifiedDataClient()

@mcp.tool()
async def create_media_buy(
    campaign_name: str,
    packages: list[dict],
    flight_start_date: str,
    flight_end_date: str,
    currency: str = "USD",
    salesforce_opportunity_id: str = None  # NEW: Link to Opportunity
) -> dict:
    """
    Create AdCP v2.3.0 campaign
    Writes to Snowflake via Data Cloud API
    """
    # Validate packages
    is_valid, error = AdCPValidator.validate_packages(packages)
    if not is_valid:
        return {"status": "error", "error": error}
    
    # Create campaign in Snowflake
    campaign_data = {
        "campaign_name": campaign_name,
        "total_budget": sum(pkg["budget"] for pkg in packages),
        "flight_start_date": flight_start_date,
        "flight_end_date": flight_end_date,
        "currency": currency,
        "salesforce_opportunity_id": salesforce_opportunity_id,
        "adcp_version": "2.3.0",
        "status": "pending"
    }
    
    campaign = await data_client.create_campaign(campaign_data)
    
    # Create packages in Snowflake
    for idx, pkg_data in enumerate(packages, 1):
        package = await data_client.create_package({
            "media_buy_id": campaign["id"],
            "package_id": f"pkg_{idx}",
            "product_id": pkg_data["product_id"],
            "budget": pkg_data["budget"],
            "pacing": pkg_data.get("pacing", "even"),
            "pricing_strategy": pkg_data.get("pricing_strategy", "cpm")
        })
        
        # Create package formats
        for fmt in pkg_data["format_ids"]:
            await data_client.create_package_format({
                "package_id": package["id"],
                "agent_url": fmt["agent_url"],
                "format_id": fmt["id"]
            })
    
    return {
        "status": "success",
        "media_buy_id": campaign["media_buy_id"],
        "campaign_name": campaign_name,
        "linked_to_opportunity": salesforce_opportunity_id is not None
    }

@mcp.tool()
async def get_campaign_for_contact(contact_id: str) -> dict:
    """
    Get all campaigns for a Salesforce Contact
    Uses 1:1 relationship via matched_audiences
    """
    return await data_client.get_campaign_for_contact(contact_id)
```

---

## Example Unified Queries

### **Query 1: Get Campaigns for Contact**

```sql
-- Find all AdCP campaigns for a specific Nike contact
SELECT 
    c.Name AS contact_name,
    c.Email,
    c.Phone,
    ma.segment_name AS audience_segment,
    ma.overlap_count AS matched_users,
    ma.engagement_score,
    mb.campaign_name,
    mb.total_budget,
    mb.status,
    mb.flight_start_date,
    mb.flight_end_date,
    SUM(dm.impressions) AS total_impressions,
    SUM(dm.clicks) AS total_clicks
FROM Contact c                               -- Native Salesforce
JOIN snowflake_matched_audiences ma          -- Snowflake (Zero Copy)
  ON ma.salesforce_contact_id = c.Id         -- 1:1 relationship
JOIN snowflake_media_buys mb                 -- Snowflake (Zero Copy)
  ON mb.matched_audience_id = ma.id
LEFT JOIN snowflake_delivery_metrics dm      -- Snowflake (Zero Copy)
  ON dm.media_buy_id = mb.id
WHERE c.Email = 'nike.marketer@nike.com'
GROUP BY c.Name, c.Email, c.Phone, ma.segment_name, 
         ma.overlap_count, ma.engagement_score, mb.campaign_name,
         mb.total_budget, mb.status, mb.flight_start_date, mb.flight_end_date;
```

### **Query 2: Package Performance by Opportunity**

```sql
-- Link AdCP package performance to Salesforce Opportunity
SELECT 
    opp.Name AS opportunity_name,
    opp.Amount AS opportunity_value,
    opp.StageName AS opportunity_stage,
    opp.CloseDate,
    mb.campaign_name,
    mb.total_budget AS campaign_budget,
    p.package_id,
    p.budget AS package_budget,
    p.pacing,
    COUNT(DISTINCT pf.format_id) AS format_count,
    SUM(dm.impressions) AS package_impressions,
    SUM(dm.clicks) AS package_clicks,
    SUM(dm.spend) AS package_spend,
    (SUM(dm.clicks)::FLOAT / NULLIF(SUM(dm.impressions), 0)) * 100 AS ctr_percentage
FROM Opportunity opp                         -- Native Salesforce
JOIN snowflake_media_buys mb                 -- Snowflake (Zero Copy)
  ON mb.salesforce_opportunity_id = opp.Id
JOIN snowflake_packages p                    -- Snowflake (Zero Copy)
  ON p.media_buy_id = mb.id
JOIN snowflake_package_formats pf            -- Snowflake (Zero Copy)
  ON pf.package_id = p.id
LEFT JOIN snowflake_delivery_metrics dm      -- Snowflake (Zero Copy)
  ON dm.package_id = p.id
WHERE opp.Id = '006xx000001RZjBAAW'
GROUP BY opp.Name, opp.Amount, opp.StageName, opp.CloseDate,
         mb.campaign_name, mb.total_budget, p.package_id, 
         p.budget, p.pacing
ORDER BY package_spend DESC;
```

### **Query 3: Account-Level Insights**

```sql
-- Get all matched audiences and campaigns for an Account
SELECT 
    acc.Name AS account_name,
    acc.Type AS account_type,
    acc.Industry,
    COUNT(DISTINCT ma.id) AS total_audiences,
    SUM(ma.overlap_count) AS total_matched_users,
    AVG(ma.engagement_score) AS avg_engagement_score,
    COUNT(DISTINCT mb.id) AS total_campaigns,
    SUM(mb.total_budget) AS total_budget_invested,
    SUM(dm.impressions) AS total_impressions,
    SUM(dm.clicks) AS total_clicks
FROM Account acc                             -- Native Salesforce
JOIN snowflake_matched_audiences ma          -- Snowflake (Zero Copy)
  ON ma.salesforce_account_id = acc.Id
LEFT JOIN snowflake_media_buys mb            -- Snowflake (Zero Copy)
  ON mb.matched_audience_id = ma.id
LEFT JOIN snowflake_delivery_metrics dm      -- Snowflake (Zero Copy)
  ON dm.media_buy_id = mb.id
WHERE acc.Id = '001xx000003DGb2AAG'
GROUP BY acc.Name, acc.Type, acc.Industry;
```

---

## Benefits Summary

| Feature | Traditional (Dual DB) | Snowflake-First + Zero Copy |
|---------|----------------------|---------------------------|
| **Storage Cost** | High (Data Cloud) | Low (Snowflake) |
| **Data Duplication** | Yes (ETL pipelines) | No (Zero Copy) |
| **Query Latency** | Low (native) | Low (Zero Copy ~100ms) |
| **Scalability** | Limited by SFDC | Petabyte-scale (Snowflake) |
| **Salesforce Integration** | Native | Via relationships |
| **MCP Server Complexity** | Dual connections | Single connection |
| **Einstein Analytics** | Yes | Yes (via Zero Copy) |
| **Cost (10 TB data)** | ~$2.5M/month | ~$2,200/month |

---

## Next Steps

1. ✅ **Schema designed** (`schema_v3_snowflake_first.sql`)
2. 🔄 **Create Snowflake database**
3. 🔄 **Configure Data Cloud Zero Copy connection**
4. 🔄 **Define relationships in Data Cloud**
5. 🔄 **Update MCP Server to use unified client**
6. 🔄 **Migrate data from SQLite to Snowflake**
7. 🔄 **Deploy to FastMCP Cloud**

---

**Ready to implement this architecture?** 🚀

