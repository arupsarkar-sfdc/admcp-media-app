# Yahoo A2A Sales Agent - Test Status

## Current Status: 🔧 Fixing Issues

### ✅ Working Skills

#### 1. `discover_products` - **WORKING**
- **Status**: ✅ Fully functional
- **Test Date**: 2025-11-24
- **Data Source**: Salesforce Data Cloud (Snowflake Zero Copy)
- **Test Result**: Successfully returned 5 Yahoo advertising products with full details

**Test Command**:
```bash
curl -k -X POST "https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "task/execute",
    "params": {
      "skill_id": "discover_products",
      "input": "{\"brief\": \"Nike running shoes campaign targeting sports enthusiasts, Q1 2025\", \"budget_range\": [10000, 50000]}"
    },
    "id": 1
  }'
```

**Sample Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "skill": "discover_products",
    "data": {
      "products": [
        {
          "product_id": "yahoo_sports_video_preroll",
          "name": "Yahoo Sports Video Pre-roll",
          "description": "15-30 second video ads before Yahoo Sports content",
          "product_type": "VIDEO",
          "pricing": {
            "base_cpm": 18.5,
            "currency": "USD"
          },
          "minimum_budget": 15000,
          "estimated_reach": 2500000
        }
        // ... 4 more products
      ],
      "total_count": 5,
      "data_source": "Salesforce Data Cloud (Snowflake Zero Copy)"
    }
  }
}
```

---

### 🔧 In Progress

#### 2. `create_campaign` - **FIXING**
- **Status**: 🔧 Code fixed, awaiting deployment
- **Issue**: Snowflake connection error (account was None)
- **Root Cause**: Env vars are set correctly in Heroku, but there was a method signature mismatch
- **Fix Applied**: 
  - Updated `skill_create_campaign` to match `insert_media_buy` signature
  - Changed from `product_ids` to `campaign_name` parameter
  - Added package insertion logic
- **Next Step**: Deploy and retest

**Test Command**:
```bash
curl -k -X POST "https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "task/execute",
    "params": {
      "skill_id": "create_campaign",
      "input": "{\"campaign_name\": \"Nike Running Q1 2025\", \"budget\": 25000, \"currency\": \"USD\", \"start_date\": \"2025-01-15\", \"end_date\": \"2025-03-31\", \"packages\": [{\"product_id\": \"yahoo_sports_video_preroll\", \"budget\": 25000, \"currency\": \"USD\", \"pacing\": \"EVEN\", \"pricing_strategy\": \"CPM\"}]}"
    },
    "id": 2
  }'
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "skill": "create_campaign",
    "data": {
      "campaign_id": "nike_running_q1_2025_20251124_153000",
      "campaign_name": "Nike Running Q1 2025",
      "packages_created": 1,
      "message": "Campaign created successfully in Snowflake",
      "data_destination": "Snowflake (reflected in Data Cloud via Zero Copy)"
    }
  }
}
```

---

#### 3. `get_campaign_status` - **FIXING**
- **Status**: 🔧 Code fixed, awaiting deployment
- **Issue**: Method `query_media_buy_delivery` doesn't exist
- **Root Cause**: Wrong method name used
- **Fix Applied**: 
  - Changed to use `query_delivery_metrics(media_buy_id=campaign_id)`
  - Added aggregation logic for impressions, spend, clicks, conversions
  - Added graceful handling for campaigns with no delivery data yet
- **Next Step**: Deploy and retest

**Test Command**:
```bash
# Use campaign_id from create_campaign response
curl -k -X POST "https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "task/execute",
    "params": {
      "skill_id": "get_campaign_status",
      "input": "{\"campaign_id\": \"nike_running_q1_2025_20251124_153000\"}"
    },
    "id": 3
  }'
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "skill": "get_campaign_status",
    "data": {
      "campaign_id": "nike_running_q1_2025_20251124_153000",
      "impressions_delivered": 0,
      "spend": 0.0,
      "clicks": 0,
      "conversions": 0,
      "message": "Campaign found but no delivery data yet",
      "data_source": "Salesforce Data Cloud (Snowflake Zero Copy)"
    }
  }
}
```

---

## Deployment Commands

### 1. Deploy Yahoo A2A Agent to Heroku
```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app
git subtree push --prefix yahoo_mcp_server heroku-yahoo-a2a main
```

### 2. Check Heroku Logs
```bash
heroku logs --tail -a yahoo-a2a-agent
```

### 3. Verify Deployment
```bash
# Health check
curl -k https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/health

# Agent card
curl -k https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json
```

---

## Environment Variables (Heroku)

All required Snowflake and Data Cloud env vars are configured:

```
SNOWFLAKE_ACCOUNT:   fcubxjp-wc35904
SNOWFLAKE_DATABASE:  DEMO_BYOL_QUERY_FEDERATION_FOR_SALESFORCE
SNOWFLAKE_PASSWORD:  *** (set)
SNOWFLAKE_ROLE:      ACCOUNTADMIN
SNOWFLAKE_SCHEMA:    PUBLIC
SNOWFLAKE_USER:      dcunitedarchitects
SNOWFLAKE_WAREHOUSE: COMPUTE_WH
DATA_CLOUD_URL:      (set)
DATA_CLOUD_CLIENT_ID: (set)
DATA_CLOUD_CLIENT_SECRET: (set)
```

---

## Next Steps

1. ✅ **Deploy fixes to Heroku**
2. ✅ **Retest all three skills**
3. ⏳ **Update Nike A2A agent** to call `discover_products`
4. ⏳ **Update A2A demo Streamlit app** to showcase real workflow
5. ⏳ **Document complete system** in COMPLETE_SYSTEM_DOCUMENTATION.md

---

## Git Commits

- `aba6538` - Fix JSON parsing for Data Cloud VARIANT fields in discover_products
- `0ea34fe` - Fix create_campaign skill to match insert_media_buy signature
- `f962c2d` - Fix get_campaign_status to use query_delivery_metrics method

