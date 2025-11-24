# 🚀 Heroku Deployment Guide - Yahoo MCP Server

## 🎉 **DEPLOYMENT SUCCESSFUL!**

**Your Live Server:**
- **URL**: https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com
- **MCP Endpoint**: https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp
- **Discovery**: https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json
- **Status**: ✅ LIVE and RUNNING
- **Region**: US (us)
- **Owner**: arup.sarkar@salesforce.com

**View Apps in Heroku Dashboard:**
- **Dashboard**: https://dashboard.heroku.com/apps (once authenticated)
- View both **yahoo-mcp-server** (MCP Server) and **adcp-campaign-planner** (Streamlit Client)

---

## ✅ Prerequisites

You have:
- ✅ Heroku account with access
- ✅ Heroku CLI installed
- ✅ Cloud-native MCP server (no SQLite)
- ✅ All tests passing (6/6)
- ✅ **DEPLOYED TO HEROKU** ✨

---

## 📦 Files Created for Heroku

- ✅ **Procfile** - Tells Heroku how to run the app
- ✅ **requirements.txt** - Python dependencies
- ✅ **runtime.txt** - Python version (3.12.7)
- ✅ **.gitignore** - Files to exclude from Git
- ✅ **server_http.py** - Updated to use Heroku's PORT

---

## 🚀 Deployment Steps

### **STEP 1: Initialize Git Repository**

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Yahoo MCP Server for Heroku"
```

### **STEP 2: Login to Heroku**

```bash
# Login to Heroku
heroku login

# This will open a browser window for authentication
```

### **STEP 3: Create Heroku App**

```bash
# Create a new Heroku app
heroku create yahoo-mcp-server

# Or with a specific name:
# heroku create your-custom-name

# This will create:
# - A Heroku app: https://yahoo-mcp-server.herokuapp.com
# - A Git remote: heroku
```

### **STEP 4: Set Environment Variables**

```bash
# Snowflake Configuration (WRITES)
heroku config:set SNOWFLAKE_ACCOUNT=your_account.us-east-1 -a yahoo-mcp-server
heroku config:set SNOWFLAKE_USER=your_snowflake_user -a yahoo-mcp-server
heroku config:set SNOWFLAKE_PASSWORD=your_snowflake_password -a yahoo-mcp-server
heroku config:set SNOWFLAKE_DATABASE=ADCP_PLATFORM -a yahoo-mcp-server
heroku config:set SNOWFLAKE_SCHEMA=PUBLIC -a yahoo-mcp-server
heroku config:set SNOWFLAKE_WAREHOUSE=COMPUTE_WH -a yahoo-mcp-server
heroku config:set SNOWFLAKE_ROLE=ACCOUNTADMIN -a yahoo-mcp-server

# Data Cloud Configuration (READS)
heroku config:set DATACLOUD_TOKEN_URL=https://acme-dcunited-connector-app-58a61db33e61.herokuapp.com/get-token -a yahoo-mcp-server

# LLM Configuration
heroku config:set OPENAI_API_KEY=your_openai_key -a yahoo-mcp-server
heroku config:set GEMINI_API_KEY=your_gemini_key -a yahoo-mcp-server

# MCP Configuration
heroku config:set MCP_HOST=0.0.0.0 -a yahoo-mcp-server
heroku config:set MCP_BASE_URL=https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com -a yahoo-mcp-server
heroku config:set LOG_LEVEL=INFO -a yahoo-mcp-server

# Verify config
heroku config -a yahoo-mcp-server
```

**✅ YOUR ACTUAL HEROKU APP**: `yahoo-mcp-server`  
**✅ YOUR PUBLIC URL**: `https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com`

### **STEP 5: Deploy to Heroku**

```bash
# Push to Heroku (this triggers deployment)
git push heroku main

# Or if your branch is named 'master':
# git push heroku master

# This will:
# 1. Upload code to Heroku
# 2. Detect Python buildpack
# 3. Install dependencies from requirements.txt
# 4. Set Python version from runtime.txt
# 5. Start the app using Procfile
```

### **STEP 6: Scale the App**

```bash
# Ensure at least 1 dyno is running
heroku ps:scale web=1

# Check dyno status
heroku ps
```

### **STEP 7: View Logs**

```bash
# View real-time logs
heroku logs --tail

# View last 100 lines
heroku logs -n 100

# Filter by level
heroku logs --tail | grep ERROR
```

---

## ✅ Verify Deployment

### **1. Check App Status**

```bash
# Open app in browser
heroku open

# Should redirect to your MCP server
```

### **2. Test Discovery Endpoints**

```bash
# Get your app URL
heroku info -a yahoo-mcp-server

# Test agent discovery
curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json

# Test agent card
curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/agent-card.json
```

### **3. Test MCP Tools**

Your test client has been updated to:

```python
# nike_campaign_workflow_http_client.py (ALREADY UPDATED)
MCP_SERVER_URL = "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp"

# Run tests against Heroku deployment
uv run python nike_campaign_workflow_http_client.py
```

Expected results:
- ✅ TEST 1: get_products - PASS
- ✅ TEST 2: create_media_buy - PASS
- ✅ TEST 3: get_media_buy - PASS
- ✅ TEST 4: get_media_buy_delivery - PASS
- ✅ TEST 5: update_media_buy - PASS
- ✅ TEST 6: get_media_buy_report - PASS

---

## 🔧 Troubleshooting

### **Issue: Application Error (H10)**

**Cause**: App didn't start correctly

**Solution**:
```bash
# Check logs
heroku logs --tail

# Common issues:
# 1. Missing environment variables
# 2. Port binding issue (should use PORT env var)
# 3. Dependencies not installed
```

### **Issue: Connection Timeout to Snowflake**

**Cause**: Heroku dyno can't reach Snowflake

**Solution**:
```bash
# Verify Snowflake credentials
heroku config:get SNOWFLAKE_ACCOUNT
heroku config:get SNOWFLAKE_USER

# Check if Snowflake allows Heroku IPs
# Heroku uses dynamic IPs - ensure Snowflake network policy allows them
# Or use Snowflake's "Allow all IPs" for testing
```

### **Issue: 403 Forbidden from Data Cloud**

**Cause**: JWT token issue

**Solution**:
```bash
# Verify token URL is accessible from Heroku
heroku config:get DATACLOUD_TOKEN_URL

# Test token endpoint
heroku run bash
curl $DATACLOUD_TOKEN_URL
```

### **Issue: Crashes After Deployment**

```bash
# Restart the app
heroku restart

# Check recent logs
heroku logs --tail

# Check dyno status
heroku ps
```

---

## 📊 Monitoring

### **View Metrics**

```bash
# Open Heroku dashboard
heroku open --app yahoo-mcp-server

# Or visit: https://dashboard.heroku.com/apps/yahoo-mcp-server
```

Dashboard shows:
- Dyno hours used
- Request throughput
- Response time
- Memory usage

### **Set Up Alerts**

In Heroku Dashboard:
1. Go to your app
2. Settings → Webhooks
3. Add webhook for:
   - Dyno crashes
   - High memory usage
   - Build failures

---

## 🔄 Updates & Maintenance

### **Deploy Updates**

```bash
# Make changes to code
# Test locally first!

# Commit changes
git add .
git commit -m "Your update description"

# Deploy
git push heroku main

# Monitor deployment
heroku logs --tail
```

### **Rollback**

```bash
# View releases
heroku releases

# Rollback to previous version
heroku rollback

# Or specific version
heroku rollback v42
```

### **Scale Up/Down**

```bash
# Upgrade dyno type (for better performance)
heroku ps:scale web=1:standard-1x

# Scale to multiple dynos (for high availability)
heroku ps:scale web=2

# Scale down (to save costs)
heroku ps:scale web=1
```

---

## 💰 Cost Optimization

### **Free Tier**
- ✅ 550-1000 dyno hours/month (free)
- ✅ Sleeps after 30 min of inactivity
- ✅ Perfect for development/testing

### **Hobby Tier ($7/month)**
- ✅ No sleeping
- ✅ SSL certificate
- ✅ Better for production

### **Standard Tier ($25-50/month)**
- ✅ Better performance
- ✅ Horizontal scaling
- ✅ Advanced metrics

---

## 🔒 Security Best Practices

### **1. Use Heroku's Secret Management**

All sensitive data is in config vars (not in code):
```bash
heroku config
# Shows all environment variables
```

### **2. Enable SSL**

Free SSL is automatic on Heroku:
```bash
# Verify SSL
curl https://yahoo-mcp-server.herokuapp.com/.well-known/adagents.json
```

### **3. Rotate Credentials Regularly**

```bash
# Update Snowflake password
heroku config:set SNOWFLAKE_PASSWORD=new_password

# Restart to apply
heroku restart
```

### **4. Monitor Access Logs**

```bash
# Enable log drains (optional)
heroku drains:add syslog+tls://your-log-service.com

# Or use Heroku's built-in logs
heroku logs --tail
```

---

## 🧪 Testing Production Deployment

### **Test Script**

```python
#!/usr/bin/env python3
"""Test Heroku deployment"""

import asyncio
from fastmcp import Client

async def test_heroku_deployment():
    # Your Heroku app URL
    server_url = "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp"
    
    async with Client(server_url) as client:
        # Test 1: Get products
        print("🔍 Testing get_products...")
        result = await client.call_tool(
            "get_products",
            {
                "brief": "Nike campaign for sports enthusiasts"
            }
        )
        print(f"✅ Found {len(result)} products")
        
        # Test 2: List formats
        print("\n🎨 Testing list_creative_formats...")
        formats = await client.call_tool("list_creative_formats", {})
        print(f"✅ Found {formats['total_count']} formats")
        
        print("\n🎉 Heroku deployment working!")

if __name__ == "__main__":
    asyncio.run(test_heroku_deployment())
```

Run:
```bash
python test_heroku_deployment.py
```

---

## 📝 Environment Variables Reference

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `PORT` | Auto-set | `8080` | Heroku assigns this |
| `MCP_HOST` | Yes | `0.0.0.0` | Bind to all interfaces |
| `MCP_BASE_URL` | Yes | `https://your-app.herokuapp.com` | Public URL |
| `SNOWFLAKE_ACCOUNT` | Yes | `xy12345.us-east-1` | Snowflake account |
| `SNOWFLAKE_USER` | Yes | `your_user` | Snowflake username |
| `SNOWFLAKE_PASSWORD` | Yes | `***` | Snowflake password |
| `SNOWFLAKE_DATABASE` | Yes | `ADCP_PLATFORM` | Database name |
| `SNOWFLAKE_SCHEMA` | No | `PUBLIC` | Schema name |
| `SNOWFLAKE_WAREHOUSE` | Yes | `COMPUTE_WH` | Warehouse |
| `SNOWFLAKE_ROLE` | No | `ACCOUNTADMIN` | Role |
| `DATACLOUD_TOKEN_URL` | Yes | `https://...` | Token endpoint |
| `OPENAI_API_KEY` | No | `sk-...` | OpenAI key |
| `GEMINI_API_KEY` | No | `...` | Gemini key |
| `LOG_LEVEL` | No | `INFO` | Logging level |

---

## ✅ Post-Deployment Checklist

- [ ] App deployed successfully
- [ ] Environment variables configured
- [ ] Discovery endpoints working (`/.well-known/`)
- [ ] MCP tools responding correctly
- [ ] Snowflake write operations working
- [ ] Data Cloud read operations working
- [ ] All 6 tests passing
- [ ] Logs show no errors
- [ ] SSL working (https://)
- [ ] Update DNS/custom domain (optional)

---

## 🎯 Your Deployment Commands (Quick Reference)

```bash
# 1. Navigate to project
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# 2. Login to Heroku
heroku login

# 3. Create app
heroku create yahoo-mcp-server

# 4. Set all environment variables (see STEP 4 above)
heroku config:set KEY=VALUE

# 5. Deploy
git push heroku main

# 6. Scale
heroku ps:scale web=1

# 7. View logs
heroku logs --tail

# 8. Test
curl https://yahoo-mcp-server.herokuapp.com/.well-known/adagents.json
```

---

## 🎉 **DEPLOYMENT COMPLETE!**

**Your Yahoo MCP Server is LIVE at:**
- **Public URL**: https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com
- **MCP Endpoint**: https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp
- **Status**: ✅ Running
- **Region**: US

### **Quick Test Commands:**

```bash
# Test discovery
curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json

# Run full test suite
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server
uv run python nike_campaign_workflow_http_client.py

# View live logs
heroku logs --tail -a yahoo-mcp-server
```

🚀 **Your server is cloud-deployed and production-ready!**

