# 🚀 Yahoo MCP Server - Deployment Information

## 📡 **LIVE PRODUCTION SERVER**

### **Heroku Deployment**

| Property | Value |
|----------|-------|
| **Public URL** | https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com |
| **MCP Endpoint** | https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp |
| **App Name** | yahoo-mcp-server |
| **Region** | US (us) |
| **Owner** | arup.sarkar@salesforce.com |
| **Status** | ✅ LIVE |
| **Stack** | heroku-24 |
| **Slug Size** | 95 MB |

---

## 🔗 **API Endpoints**

### **AdCP v2.3.0 Discovery Endpoints**

```bash
# Agent Discovery Manifest
GET https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json

# Agent Business Card
GET https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/agent-card.json
```

### **MCP Protocol Endpoint**

```bash
# MCP Server (HTTP/SSE Transport)
POST https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp
```

---

## 🛠️ **Management Commands**

### **View Logs**
```bash
heroku logs --tail -a yahoo-mcp-server
```

### **Restart Server**
```bash
heroku restart -a yahoo-mcp-server
```

### **Check Status**
```bash
heroku ps -a yahoo-mcp-server
```

### **View Config**
```bash
heroku config -a yahoo-mcp-server
```

### **Scale Dynos**
```bash
# Scale up (more performance)
heroku ps:scale web=2 -a yahoo-mcp-server

# Scale down (save costs)
heroku ps:scale web=1 -a yahoo-mcp-server
```

---

## 🧪 **Testing**

### **Test Discovery Endpoints**

```bash
# Test agent discovery
curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json

# Expected: JSON with agent manifest

# Test agent card
curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/agent-card.json

# Expected: JSON with business card info
```

### **Run Full Test Suite**

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# Client is already configured for Heroku URL
uv run python nike_campaign_workflow_http_client.py

# Expected: 6/6 tests passing
```

### **Test with MCP Client**

```python
from fastmcp import Client
import asyncio

async def test_heroku():
    async with Client("https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp") as client:
        # Test get_products
        result = await client.call_tool(
            "get_products",
            {"brief": "Nike campaign for sports enthusiasts"}
        )
        print(f"✅ Found {len(result.get('products', []))} products")

asyncio.run(test_heroku())
```

---

## 📊 **Architecture**

### **Data Flow**

```
┌─────────────┐
│   Client    │
│  (Buyer)    │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────┐
│   Heroku (Yahoo MCP Server)     │
│  https://yahoo-mcp-server-...   │
│                                 │
│  ┌─────────────────────────┐   │
│  │  FastMCP HTTP/SSE       │   │
│  │  - get_products         │   │
│  │  - create_media_buy     │   │
│  │  - update_media_buy     │   │
│  │  - get_media_buy        │   │
│  │  - etc (9 tools)        │   │
│  └────┬────────────────┬───┘   │
└───────┼────────────────┼───────┘
        │                │
        │ WRITE          │ READ
        ▼                ▼
   ┌─────────────┐  ┌──────────────────┐
   │  Snowflake  │  │ Salesforce Data  │
   │  (Direct)   │  │ Cloud (Zero Copy)│
   └─────────────┘  └──────────────────┘
         │                    │
         └────────────────────┘
              Same Data
```

### **Key Features**

- ✅ **AdCP v2.3.0 Compliant** - Full package-based media buy structure
- ✅ **HTTP/SSE Transport** - FastMCP streamable-http
- ✅ **Cloud-Native** - No SQLite, 100% cloud data sources
- ✅ **Snowflake Writes** - Direct write operations with PARSE_JSON
- ✅ **Data Cloud Reads** - Zero Copy virtualization from Snowflake
- ✅ **LLM-Powered** - OpenAI + Gemini for product discovery
- ✅ **Multi-Tenant** - UUID-based tenant isolation
- ✅ **Discoverable** - Standard `.well-known` endpoints

---

## 🔐 **Environment Variables**

All sensitive configuration is stored in Heroku config vars (not in code):

```bash
# View all config vars
heroku config -a yahoo-mcp-server

# Set/update a config var
heroku config:set KEY=VALUE -a yahoo-mcp-server

# Delete a config var
heroku config:unset KEY -a yahoo-mcp-server
```

**Required Config Vars:**
- `SNOWFLAKE_*` (8 vars) - Snowflake connection
- `DATACLOUD_TOKEN_URL` - JWT token endpoint
- `MCP_BASE_URL` - Public URL
- `OPENAI_API_KEY` / `GEMINI_API_KEY` - LLM APIs

---

## 📈 **Monitoring**

### **Heroku Dashboard**

https://dashboard.heroku.com/apps/yahoo-mcp-server

Provides:
- Dyno metrics (CPU, memory)
- Request throughput
- Response times
- Error rates

### **Log Analysis**

```bash
# View errors only
heroku logs -a yahoo-mcp-server | grep ERROR

# View last 100 lines
heroku logs -n 100 -a yahoo-mcp-server

# Follow logs in real-time
heroku logs --tail -a yahoo-mcp-server
```

---

## 🔄 **Deployment Updates**

### **Deploy New Version**

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app

# Make changes to code
# Commit changes
git add .
git commit -m "Update description"

# Deploy to Heroku
git subtree push --prefix yahoo_mcp_server heroku main

# Monitor deployment
heroku logs --tail -a yahoo-mcp-server
```

### **Rollback to Previous Version**

```bash
# View releases
heroku releases -a yahoo-mcp-server

# Rollback to previous
heroku rollback -a yahoo-mcp-server

# Or specific version
heroku rollback v42 -a yahoo-mcp-server
```

---

## 🎯 **Integration Examples**

### **Connect from Claude Desktop (MCP Client)**

Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "yahoo-sales-agent": {
      "url": "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp",
      "transport": "http"
    }
  }
}
```

### **Connect from Python**

```python
from fastmcp import Client

async def use_yahoo_agent():
    async with Client("https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp") as client:
        # Discover products
        products = await client.call_tool(
            "get_products",
            {"brief": "Campaign targeting sports enthusiasts"}
        )
        
        # Create media buy
        campaign = await client.call_tool(
            "create_media_buy",
            {
                "campaign_name": "Q1 2025 Campaign",
                "packages": [...],
                "flight_start_date": "2025-01-01",
                "flight_end_date": "2025-03-31"
            }
        )
```

### **Connect from cURL**

```bash
# Initialize MCP session
curl -X POST https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "params": {...}, "id": 1}'
```

---

## 💰 **Cost Estimates**

### **Current Setup**
- **Dyno Type**: Eco ($5/month) or Free (with sleep)
- **Estimated Monthly Cost**: $0-5
- **Includes**:
  - 1000 dyno hours (free tier) or always-on (paid)
  - Automatic SSL
  - Metrics dashboard
  - Log storage (1500 lines)

### **Scale-Up Options**
- **Basic ($7/month)**: No sleep, better uptime
- **Standard-1X ($25/month)**: 2X performance
- **Standard-2X ($50/month)**: 4X performance
- **Performance-M ($250/month)**: Enterprise-grade

---

## ✅ **Production Readiness Checklist**

- [x] Deployed to Heroku
- [x] Environment variables configured
- [x] Discovery endpoints working
- [x] MCP tools responding
- [x] Snowflake writes working
- [x] Data Cloud reads working
- [x] SSL enabled (HTTPS)
- [x] Logs accessible
- [ ] Custom domain (optional)
- [ ] JWT authentication (TODO)
- [ ] Rate limiting (TODO)
- [ ] Horizontal scaling (TODO)

---

## 📚 **Additional Resources**

- **Full Deployment Guide**: See `HEROKU_DEPLOYMENT.md`
- **AdCP Specification**: `ADCP_COMPLIANCE_IMPLEMENTATION_PLAN.md`
- **Data Cloud Integration**: `DATA_CLOUD_INTEGRATION_COMPLETE.md`
- **Snowflake Architecture**: `SNOWFLAKE_FIRST_ARCHITECTURE.md`

---

## 🆘 **Support**

### **Issues?**

1. Check logs: `heroku logs --tail -a yahoo-mcp-server`
2. Verify config: `heroku config -a yahoo-mcp-server`
3. Restart: `heroku restart -a yahoo-mcp-server`
4. Check status: `heroku ps -a yahoo-mcp-server`

### **Common Issues**

**"Application Error" (H10)**
- Check logs for startup errors
- Verify all config vars are set
- Ensure PORT binding is correct (using `os.getenv("PORT")`)

**"Connection Timeout"**
- Snowflake credentials correct?
- Snowflake network policy allows Heroku IPs?
- Data Cloud token URL accessible?

**"503 Service Unavailable"**
- Dyno sleeping (free tier)?
- Scale up: `heroku ps:scale web=1`

---

**Last Updated**: November 20, 2025  
**Deployment Date**: November 20, 2025  
**Status**: ✅ PRODUCTION

