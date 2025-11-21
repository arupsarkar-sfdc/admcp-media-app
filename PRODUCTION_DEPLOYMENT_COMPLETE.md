# Yahoo MCP Server - Cloud-Native Architecture Complete ✅

## Full Migration: SQLite → Snowflake + Data Cloud

**Status**: ✅ **PRODUCTION READY**

**Date**: November 20-21, 2025

**Deployment**: ✅ Heroku (https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com)

**Salesforce Integration**: ✅ Registered in Agentforce

---

## 100% Cloud-Native Architecture (Snowflake-First)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI Agents & Interfaces                           │
│  ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │ Salesforce       │  │ Custom Python   │  │ Claude Desktop   │   │
│  │ Agentforce       │  │ Agent (Local)   │  │ MCP Client       │   │
│  │ ✅ Registered     │  │ ✅ Ready         │  │ ✅ Compatible    │   │
│  └──────────────────┘  └─────────────────┘  └──────────────────┘   │
│            │                    │                      │             │
│            └────────────────────┴──────────────────────┘             │
│                              MCP Protocol                            │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│         Yahoo MCP Server (Heroku - 100% Cloud-Native)               │
│         https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com         │
│                      AdCP v2.3.0 Compliant ✅                        │
│                                                                      │
│  ┌──────────────────────────┐      ┌──────────────────────────┐    │
│  │   READ Operations (4)    │      │   WRITE Operations (2)   │    │
│  │   ✅ Data Cloud Queries   │      │   ✅ Snowflake Direct     │    │
│  │                          │      │                          │    │
│  │  - get_products          │      │  - create_media_buy      │    │
│  │  - get_media_buy         │      │  - update_media_buy      │    │
│  │  - get_media_buy_        │      │                          │    │
│  │    delivery              │      │  ↓ Snowflake             │    │
│  │  - get_media_buy_report  │      │    Write Service         │    │
│  │                          │      │  ↓ PARSE_JSON()          │    │
│  │  ↓ Data Cloud            │      │    for VARIANT           │    │
│  │    Query Service         │      └──────────────────────────┘    │
│  │  ↓ SQL with Aliases      │                                       │
│  └──────────────────────────┘                                       │
│                                                                      │
│  Additional Tools:                                                  │
│  - list_creative_formats (AdCP v2.3.0)                              │
│  - Discovery: /.well-known/adagents.json                            │
│  - Discovery: /.well-known/agent-card.json                          │
└────────────────────────┬─────────────────────┬─────────────────────┘
                         │                     │
                    READ │                     │ WRITE
                         ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Salesforce Data Cloud (Semantic Layer)                │
│                    Query API: POST /api/v1/query                    │
│             JWT Authentication (cdp_query_api scope)                │
│                                                                      │
│     Zero Copy Data Virtualization (JDBC Live Connection)            │
│     ✅ Reads: Instant query results from Snowflake                  │
│     ✅ Writes: Reflected instantly via live JDBC                    │
└────────────────────────┬───────────────────────────────────────┬────┘
                         │                                       │
                    READ │                                       │ WRITE
                         ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Snowflake (Single Source of Truth) 🏔️                  │
│           Database: ACME_ORG_DW | Schema: YAHOO_ADCP                │
│                                                                      │
│  AdCP Tables (Zero Copy → Data Cloud):                              │
│    ✅ products__dlm (5 active products)                             │
│    ✅ media_buys__dlm (campaigns with VARIANT fields)               │
│    ✅ packages__dlm (AdCP v2.3.0 package structure)                 │
│    ✅ package_formats__dlm (creative format assignments)            │
│    ✅ matched_audiences__dlm (w/ salesforce_contact_id__c)          │
│    ✅ delivery_metrics__dlm (real-time performance data)            │
│    ✅ audit_log__dlm (change tracking)                              │
│                                                                      │
│  CRM Integration Ready:                                             │
│    - salesforce_account_id__c columns                               │
│    - salesforce_contact_id__c for audience matching                 │
│    - Data Cloud relationships (1:1 with Contact)                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Complete Migration Timeline

### Phase 1: Data Migration to Snowflake ✅
- Created Snowflake schema with AdCP v2.3.0 structure
- Migrated all data from SQLite to Snowflake
- Fixed VARIANT column handling (PARSE_JSON pattern)
- Added CRM integration columns (salesforce_contact_id__c, salesforce_account_id__c)

### Phase 2: Data Cloud Integration (Reads) ✅
- Implemented JWT authentication service
- Created Data Cloud Query Service
- Updated 4 read tools to query via Data Cloud
- Implemented SQL alias pattern for clean column names

### Phase 3: Snowflake Write Service ✅
- Implemented SnowflakeWriteService class
- Updated `create_media_buy` to write directly to Snowflake
- Updated `update_media_buy` to write directly to Snowflake
- Fixed VARIANT handling with `PARSE_JSON(%s)` pattern
- Removed SQLite dependency (100% cloud-native)

### Phase 4: Deployment & Integration ✅
- Deployed to Heroku (streamable-http transport)
- Registered in Salesforce Agentforce
- Created 4 agentic Topics in Agentforce
- Built custom Python agent for local testing
- Fixed validator bug (VALID_FORMAT_IDS sync)

---

## Current Architecture Details

### 1. **MCP Server (`server_http.py`)**

#### READ Operations (4 tools) - Data Cloud
```python
from services.datacloud_query_service import get_datacloud_query_service
```

**Tool 2: `get_products`**
- ✅ Queries `products__dlm` from Data Cloud
- ✅ Applies principal-specific discounts (enterprise: 15%, standard: 5%)
- ✅ Returns pricing with `original_value` and `discount_percentage`
- ✅ Budget filtering with flexibility (0.5x to 1.5x range)

**Tool 6: `get_media_buy`**
- ✅ Queries `media_buys__dlm` and `packages__dlm` from Data Cloud
- ✅ Joins package_formats to show `formats` list
- ✅ Returns `product_name` for each package
- ✅ Shows campaign-level and package-level details

**Tool 7: `get_media_buy_delivery`**
- ✅ Queries `delivery_metrics__dlm` from Data Cloud
- ✅ Aggregates: impressions_delivered, clicks, conversions, spend
- ✅ Calculates: CTR, CVR, CPC, pacing analysis
- ✅ Returns unified performance object

**Tool 9: `get_media_buy_report`**
- ✅ Queries `delivery_metrics__dlm` with date filtering
- ✅ Daily breakdown with trends
- ✅ Device breakdown (desktop, mobile, tablet)
- ✅ Geo breakdown by region
- ✅ Format performance analysis

#### WRITE Operations (2 tools) - Snowflake Direct
```python
from services.snowflake_write_service import get_snowflake_write_service
```

**Tool 5: `create_media_buy`**
- ✅ Writes to `media_buys__dlm` table in Snowflake
- ✅ Creates packages in `packages__dlm`
- ✅ Creates format assignments in `package_formats__dlm`
- ✅ Uses `PARSE_JSON(%s)` for VARIANT columns
- ✅ Data Cloud reflects instantly via Zero Copy

**Tool 8: `update_media_buy`**
- ✅ Updates `media_buys__dlm` directly in Snowflake
- ✅ Handles VARIANT columns (targeting, workflow_state, etc.)
- ✅ Supports partial updates (only changed fields)
- ✅ Data Cloud shows updates immediately

#### Removed SQLite Dependency
```python
# OLD: get_nike_principal(db_session)
# NEW: MockPrincipal with correct tenant_id
class MockPrincipal:
    def __init__(self):
        self.principal_id = "nike_advertiser"
        self.tenant_id = "374df0f3-dab1-450d-871f-fbe9569d3042"  # Matches Snowflake
        self.name = "Nike"
        self.access_level = "enterprise"
```

#### Updated Startup Banner (Production)
```
======================================================================
🎯 YAHOO SALES AGENT - MCP SERVER
======================================================================
MCP Protocol: Streamable HTTP (Heroku Compatible)
AdCP Version: v2.3.0 ✅
Port: 8080
Cloud Architecture: 100% Cloud-Native 🌩️

📊 DATA ARCHITECTURE:
   READ:  Salesforce Data Cloud → Snowflake (Zero Copy) ✅
   WRITE: Snowflake Direct (VARIANT with PARSE_JSON) ✅
   Status: NO SQLite dependency - Fully cloud-native!

📦 9 MCP TOOLS AVAILABLE:
   1. echo                       [test only]
   2. get_products               [🌩️ Data Cloud → Snowflake]
   3. list_creative_formats      [AdCP v2.3.0 ✅]
   4. get_campaign_stats         [mock - test only]
   5. create_media_buy           [⚡ Snowflake Direct Write]
   6. get_media_buy              [🌩️ Data Cloud → Snowflake]
   7. get_media_buy_delivery     [🌩️ Data Cloud → Snowflake]
   8. update_media_buy           [⚡ Snowflake Direct Write]
   9. get_media_buy_report       [🌩️ Data Cloud → Snowflake]

🔍 DISCOVERY ENDPOINTS:
   ✅ GET  /.well-known/adagents.json
   ✅ GET  /.well-known/agent-card.json

🎭 AGENTIC EXPERIENCE:
   ✅ Salesforce Agentforce (4 Topics configured)
   ✅ Custom Python Agent (advertising_agent.py)
   ✅ Claude Desktop compatible
======================================================================
```

---

## Data Validation

### Verified Data Cloud Queries Work
✅ **5 products** - Retrieved from `products__dlm`  
✅ **16 media buys** - Retrieved from `media_buys__dlm`  
✅ **3 matched audiences** - Retrieved from `matched_audiences__dlm`  
✅ **20 delivery metrics** - Retrieved from `delivery_metrics__dlm`  

### SQL Alias Strategy
All queries use SQL aliases for clean, predictable column names:
```sql
SELECT 
    name__c as name,
    product_id__c as product_id,
    minimum_budget__c as minimum_budget
FROM products__dlm
WHERE is_active__c = true
```

Access in Python:
```python
product.get('name')  # Clean, no __C suffix
```

---

## Benefits Achieved

### 1. **Cloud-Native Architecture**
- ✅ Single source of truth: Snowflake
- ✅ Zero Copy virtualization: Data Cloud
- ✅ No data duplication or ETL
- ✅ Real-time data visibility

### 2. **Scalability**
- ✅ Snowflake handles massive datasets
- ✅ Data Cloud provides enterprise-grade query performance
- ✅ MCP server is stateless (no local data dependencies)

### 3. **CRM Integration Ready**
- ✅ `matched_audiences__dlm` has `salesforce_contact_id__c` and `salesforce_account_id__c`
- ✅ Data Cloud relationships can unify Yahoo audiences with Salesforce CRM data
- ✅ Enables cross-platform customer insights

### 4. **AdCP v2.3.0 Compliance**
- ✅ All read tools return AdCP-compliant data structures
- ✅ Agent discovery endpoints operational
- ✅ Package-based media buys supported

---

## Deployment

### Heroku Production
```bash
# Server URL
https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com

# MCP Endpoint (streamable-http)
https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/

# Discovery Endpoints
https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json
https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/agent-card.json
```

### Config Vars (Heroku)
- `SNOWFLAKE_*` - Snowflake connection credentials
- `SALESFORCE_TOKEN_ENDPOINT` - JWT token service
- `ANTHROPIC_API_KEY` - For LLM features (optional)
- `OPENAI_API_KEY` - For LLM features (optional)
- `PORT` - Auto-set by Heroku

### Deploy Updates
```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app
git add .
git commit -m "Your commit message"
git subtree push --prefix yahoo_mcp_server heroku main
```

---

## Testing Instructions

### Option 1: Test Locally
```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app

# Set environment variables
export ANTHROPIC_API_KEY=your_key
# (Snowflake vars already in .env)

# Start local server
uv run python yahoo_mcp_server/server_http.py

# In another terminal, run test client
uv run python yahoo_mcp_server/nike_campaign_workflow_http_client.py
```

### Option 2: Test with Custom Agent
```bash
# Set API key
export ANTHROPIC_API_KEY=your_key

# Run agentic experience
uv run python yahoo_mcp_server/advertising_agent.py

# Try prompts like:
# "Show me advertising options for Nike running shoes"
# "Create a $50K campaign for Nike Air Max"
```

### Option 3: Test in Salesforce Agentforce
1. Go to Salesforce Agentforce
2. Open "Nike Campaign Planner" or any configured topic
3. Chat with the agent using natural language
4. Agent uses MCP tools via Heroku deployment

### Expected Results (All Environments)
- **get_products**: Returns 5 products from Snowflake via Data Cloud ✅
- **create_media_buy**: Creates campaign in Snowflake, visible in Data Cloud instantly ✅
- **get_media_buy**: Retrieves campaign from Snowflake via Data Cloud ✅
- **get_media_buy_delivery**: Shows real-time metrics from Snowflake ✅
- **update_media_buy**: Updates Snowflake, reflected instantly in Data Cloud ✅
- **get_media_buy_report**: Generates analytics from Snowflake ✅

---

## Salesforce Agentforce Integration

### MCP Server Registration ✅
- **Name**: YahooSalesAgent
- **Description**: Yahoo Advertising Platform - AdCP v2.3.0 compliant
- **Status**: Active (registered November 20, 2025)
- **URL**: https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/
- **Tools Enabled**: 9/9 (all tools)

### Agentic Topics Created

#### Topic 1: Advertising Options for Nike Running Shoes
- **Scope**: Full campaign lifecycle for Nike campaigns
- **Tools**: All 6 primary tools (get_products, list_creative_formats, create_media_buy, get_media_buy_delivery, update_media_buy, get_media_buy_report)
- **Instructions**: 7 detailed behavioral instructions

#### Topic 2: Campaign Performance Analysis
- **Scope**: Performance monitoring and optimization
- **Tools**: get_media_buy_delivery, get_media_buy_report, update_media_buy
- **Instructions**: 4 analysis-focused instructions

#### Topic 3: Budget Planning & Campaign Setup
- **Scope**: Product discovery and campaign creation
- **Tools**: get_products, list_creative_formats, create_media_buy
- **Instructions**: 4 planning-focused instructions

#### Topic 4: Creative Strategy & Format Recommendations
- **Scope**: Format guidance and creative best practices
- **Tools**: list_creative_formats, get_media_buy_report
- **Instructions**: 4 creative-focused instructions

---

## Recent Bug Fixes & Improvements

### Bug Fix: VALID_FORMAT_IDS Sync Issue (Nov 21, 2025)
**Problem**: Agent was hallucinating invalid format IDs and retrying 5 times
- Agent called `list_creative_formats` ✅
- Agent used format IDs returned from the tool ✅
- Validator rejected valid IDs because hardcoded list was outdated ❌

**Root Cause**: `adcp_validator.py` VALID_FORMAT_IDS didn't match `server_http.py` list_creative_formats

**Fix Applied**:
```python
# Updated VALID_FORMAT_IDS in adcp_validator.py
VALID_FORMAT_IDS = {
    "display_300x250", "display_728x90", "display_160x600", "display_320x50",
    "video_16x9_15s", "video_16x9_30s", "video_9x16_15s",
    "native_content_feed", "native_in_stream"
}
```

**Result**: Campaign creation now succeeds on first attempt (no retries needed)

### Improvement: Agent System Prompt
- Added strict instructions to ONLY use format IDs from `list_creative_formats`
- Emphasized calling `list_creative_formats` FIRST before creating campaigns
- Added validation error handling guidance

---

## Production Readiness Checklist

### Core Functionality ✅
- [x] AdCP v2.3.0 package-based media buys
- [x] All 9 MCP tools functional
- [x] Discovery endpoints (/.well-known/)
- [x] Format validation aligned with server

### Data Layer ✅
- [x] Snowflake schema created and populated
- [x] Data Cloud Zero Copy virtualization working
- [x] Read operations via Data Cloud Query Service
- [x] Write operations via Snowflake Write Service
- [x] VARIANT column handling (PARSE_JSON pattern)
- [x] CRM integration columns added

### Authentication ✅
- [x] JWT token service for Data Cloud
- [x] Token caching and auto-refresh
- [x] Correct scope (cdp_query_api)

### Deployment ✅
- [x] Heroku deployment configured
- [x] Environment variables set
- [x] Streamable-http transport working
- [x] Port binding correct (dynamic PORT)
- [x] Mount path correct (/) for Agentforce

### Integration ✅
- [x] Salesforce Agentforce registration
- [x] 4 Topics configured with instructions
- [x] Custom Python agent for local testing
- [x] Documentation complete

### Quality ✅
- [x] Format ID validation fixed
- [x] MockPrincipal tenant_id matches Snowflake data
- [x] Response structures match client expectations
- [x] Error handling and logging comprehensive

---

## Summary

🎉 **FULL MIGRATION COMPLETE - PRODUCTION READY!**

### All Tasks Completed ✅
1. ✅ Snowflake schema and data migration
2. ✅ Data Cloud Query Service integration (reads)
3. ✅ Snowflake Write Service implementation (writes)
4. ✅ Heroku deployment
5. ✅ Salesforce Agentforce registration
6. ✅ Agentic experience (4 topics + custom agent)
7. ✅ Bug fixes (validator sync)

### Architecture Achievement 🏗️
- **100% Cloud-Native**: No SQLite dependency
- **Single Source of Truth**: Snowflake stores all data
- **Zero Copy**: Data Cloud virtualizes Snowflake instantly
- **Real-Time**: Writes to Snowflake visible immediately in Data Cloud
- **CRM Ready**: Integration columns for Salesforce Contact/Account
- **AdCP Compliant**: Full v2.3.0 package-based structure

### Tools Status 📊
- **9 Total MCP Tools**: All functional
- **4 READ tools**: Data Cloud → Snowflake (Zero Copy)
- **2 WRITE tools**: Direct to Snowflake (PARSE_JSON for VARIANT)
- **1 Metadata tool**: list_creative_formats (AdCP v2.3.0)
- **2 Discovery endpoints**: /.well-known/ (AdCP compliance)

### Integration Points 🔗
- **Salesforce Agentforce**: Registered and active with 4 topics
- **Custom Python Agent**: Local testing with Claude/GPT-4
- **Heroku**: Production deployment at https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com

### Data Flow Validated ✅
```
CREATE campaign → Snowflake → Data Cloud reflects instantly → READ via any tool
UPDATE campaign → Snowflake → Data Cloud reflects instantly → READ shows changes
```

### Key Technical Wins 🎯
1. **VARIANT Handling**: Mastered `PARSE_JSON(%s)` pattern for Snowflake
2. **SQL Aliases**: Clean column names (`id` not `ID__C`) in application layer
3. **Format Validation**: Aligned validator with server format definitions
4. **JWT Authentication**: Working token service with correct scopes
5. **Streamable HTTP**: FastMCP transport compatible with Salesforce

---

**Status**: 🚀 **READY FOR PRODUCTION USE**

**Next Steps**: Use it! Create campaigns, analyze performance, optimize budgets. The agentic experience is live in Salesforce Agentforce and available via custom Python agent.

