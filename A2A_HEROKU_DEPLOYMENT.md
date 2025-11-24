# A2A Agents - Heroku Deployment Guide

Complete deployment guide for Yahoo A2A Sales Agent and Nike A2A Campaign Agent on Heroku.

---

## 🏗️ Architecture Overview

```
Nike A2A Campaign Agent (Heroku)
    ↕️ A2A Protocol (JSON-RPC 2.0, bidirectional)
Yahoo A2A Sales Agent (Heroku)
    ↓ Internal calls
Yahoo MCP Server (Heroku, existing)
    ↓
Data Cloud → Snowflake
```

---

## 📦 Heroku Apps

### App 1: Yahoo MCP Server (Existing)
- **App Name**: `yahoo-mcp-server`
- **Purpose**: MCP server for Salesforce Agentforce
- **URL**: `https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com`
- **Branch**: `main`
- **Status**: ✅ Already deployed

### App 2: Yahoo A2A Sales Agent (New)
- **App Name**: `yahoo-a2a-agent`
- **Purpose**: A2A wrapper for Yahoo advertising platform
- **URL**: `https://yahoo-a2a-agent-72829d23cce8.herokuapp.com`
- **Branch**: `main` (deployed from `yahoo_mcp_server` folder)
- **Status**: 🚀 Deploying in this guide

### App 3: Nike A2A Campaign Agent (Future)
- **App Name**: `nike-a2a-campaign-agent`
- **Purpose**: Campaign planning orchestrator
- **URL**: TBD
- **Branch**: `main` (deployed from `nike_a2a_agent` folder)
- **Status**: ⏳ Phase 2

### App 4: Streamlit UI (Existing)
- **App Name**: `adcp-campaign-planner`
- **Purpose**: Web UI for MCP server
- **URL**: `https://adcp-campaign-planner-xxxxx.herokuapp.com`
- **Branch**: `mcp-client`
- **Status**: ✅ Already deployed

---

## ⚠️ CRITICAL: Procfile Management

**THE SAME `yahoo_mcp_server/Procfile` IS USED FOR 3 DIFFERENT HEROKU APPS!**

This is the **most critical** part of deployment. You MUST swap the Procfile for each deployment.

### Procfile Mapping

| Heroku App | Source Folder | Procfile to Use | Command |
|------------|---------------|-----------------|---------|
| `yahoo-mcp-server` | `yahoo_mcp_server/` | `Procfile` (original) | `web: python server_http.py` |
| `yahoo-a2a-agent` | `yahoo_mcp_server/` | `Procfile.a2a` | `web: python yahoo_a2a_server.py` |
| `adcp-campaign-planner` | `yahoo_mcp_server/` | `Procfile.streamlit` | `web: streamlit run streamlit_app.py...` |
| `nike-a2a-campaign-agent` | `nike_a2a_agent/` | `Procfile` | `web: python nike_agent.py` |

### The Problem

All 3 apps (`yahoo-mcp-server`, `yahoo-a2a-agent`, `adcp-campaign-planner`) deploy from the **SAME folder** (`yahoo_mcp_server/`) but run **DIFFERENT applications**:

1. **yahoo-mcp-server** runs `server_http.py` (MCP server)
2. **yahoo-a2a-agent** runs `yahoo_a2a_server.py` (A2A server)
3. **adcp-campaign-planner** runs `streamlit_app.py` (Streamlit UI)

### The Solution

**ALWAYS follow this workflow:**

1. **Backup** the current Procfile
2. **Swap** to the correct Procfile for the app you're deploying
3. **Commit** the Procfile change
4. **Deploy** to Heroku
5. **IMMEDIATELY restore** the original Procfile
6. **Verify** you restored it correctly

### Deployment Workflow

```bash
# STEP 1: Backup current Procfile
cp yahoo_mcp_server/Procfile yahoo_mcp_server/Procfile.backup

# STEP 2: Swap to target Procfile
# For yahoo-a2a-agent:
cp yahoo_mcp_server/Procfile.a2a yahoo_mcp_server/Procfile

# For adcp-campaign-planner:
# cp yahoo_mcp_server/Procfile.streamlit yahoo_mcp_server/Procfile

# For yahoo-mcp-server (original):
# cp yahoo_mcp_server/Procfile.backup yahoo_mcp_server/Procfile

# STEP 3: Commit
git add yahoo_mcp_server/Procfile
git commit -m "Deploy [APP_NAME]"

# STEP 4: Deploy
git subtree push --prefix yahoo_mcp_server [HEROKU_REMOTE] main

# STEP 5: IMMEDIATELY restore original Procfile
cp yahoo_mcp_server/Procfile.backup yahoo_mcp_server/Procfile
git checkout -- yahoo_mcp_server/Procfile
rm yahoo_mcp_server/Procfile.backup

# STEP 6: Verify
cat yahoo_mcp_server/Procfile
# Should show: web: python server_http.py
```

### What Happens If You Forget to Restore?

❌ **Disaster scenarios:**

1. You deploy `yahoo-a2a-agent` with `Procfile.a2a`
2. You forget to restore the original Procfile
3. You later deploy `yahoo-mcp-server` (thinking you're deploying MCP server)
4. **Result**: MCP server now runs `yahoo_a2a_server.py` instead of `server_http.py`
5. **Impact**: Salesforce Agentforce breaks, Streamlit UI breaks, everything breaks!

### Safety Checks

**Before deploying, ALWAYS check:**

```bash
# Check current Procfile
cat yahoo_mcp_server/Procfile

# Check which app you're deploying to
git remote -v | grep heroku

# Verify the command matches the app
# yahoo-mcp-server → server_http.py
# yahoo-a2a-agent → yahoo_a2a_server.py
# adcp-campaign-planner → streamlit_app.py
```

**After deploying, ALWAYS verify:**

```bash
# Check Procfile was restored
cat yahoo_mcp_server/Procfile
# MUST show: web: python server_http.py

# If not, restore immediately:
git checkout -- yahoo_mcp_server/Procfile
```

### Git Branch Strategy

**CRITICAL: Each Heroku app has its own dedicated Git branch for clean separation!**

| Branch | Purpose | Source Folder | Deploys To | Procfile |
|--------|---------|---------------|------------|----------|
| `main` | MCP Server | `yahoo_mcp_server/` | `yahoo-mcp-server` | `web: python server_http.py` |
| `mcp-client` | Streamlit UI | `yahoo_mcp_server/` | `adcp-campaign-planner` | `web: streamlit run streamlit_app.py...` |
| `yahoo-a2a` | Yahoo A2A Agent | `yahoo_mcp_server/` | `yahoo-a2a-agent` | `web: python yahoo_a2a_server.py` |
| `nike-a2a` | Nike A2A Agent | `nike_a2a_agent/` | `nike-a2a-campaign-agent` | `web: python nike_agent.py` |

**Why separate branches?**
1. **No Procfile conflicts** - Each branch has the correct Procfile for its app
2. **Clean deployments** - No need to swap/restore Procfiles
3. **Safe** - Deploying one app never breaks another
4. **Clear history** - Each branch shows its app's deployment history

**Deployment commands:**

```bash
# MCP Server (from main branch)
git checkout main
git push heroku main

# Streamlit UI (from mcp-client branch)
git checkout mcp-client
git subtree push --prefix yahoo_mcp_server heroku-streamlit main

# Yahoo A2A Agent (from yahoo-a2a branch)
git checkout yahoo-a2a
git subtree push --prefix yahoo_mcp_server heroku-yahoo-a2a main

# Nike A2A Agent (from nike-a2a branch)
git checkout nike-a2a
git subtree push --prefix nike_a2a_agent heroku-nike-a2a main
```

---

## 🚀 Yahoo A2A Agent Deployment

### Prerequisites

1. ✅ Heroku CLI installed and logged in
2. ✅ Git repository initialized
3. ✅ Local testing passed
4. ✅ Yahoo MCP Server already deployed

### Step 1: Create Heroku App

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app

# Create new Heroku app
heroku create yahoo-a2a-agent
```

**Output**:
```
Creating ⬢ yahoo-a2a-agent... done
https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/ | https://git.heroku.com/yahoo-a2a-agent.git
```

---

### Step 2: Add Heroku Remote

```bash
# Add Heroku remote with custom name
heroku git:remote -a yahoo-a2a-agent -r heroku-yahoo-a2a
```

**Verify remotes**:
```bash
git remote -v
```

**Expected output**:
```
heroku              https://git.heroku.com/yahoo-mcp-server.git (fetch)
heroku              https://git.heroku.com/yahoo-mcp-server.git (push)
heroku-streamlit    https://git.heroku.com/adcp-campaign-planner.git (fetch)
heroku-streamlit    https://git.heroku.com/adcp-campaign-planner.git (push)
heroku-yahoo-a2a    https://git.heroku.com/yahoo-a2a-agent.git (fetch)
heroku-yahoo-a2a    https://git.heroku.com/yahoo-a2a-agent.git (push)
origin              https://github.com/arupsarkar-sfdc/admcp-media-app.git (fetch)
origin              https://github.com/arupsarkar-sfdc/admcp-media-app.git (push)
```

---

### Step 3: Prepare Deployment Files

**Important**: The Yahoo A2A agent needs a different `Procfile` than the MCP server.

#### Option A: Use Deployment Script (Recommended)

Create a deployment script:

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# Create deployment script
cat > deploy_a2a.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Deploying Yahoo A2A Agent to Heroku..."

# Backup current Procfile
cp Procfile Procfile.mcp.backup
echo "✅ Backed up MCP Procfile"

# Swap to A2A Procfile
cp Procfile.a2a Procfile
echo "✅ Swapped to A2A Procfile"

# Commit changes
git add Procfile
git commit -m "Deploy Yahoo A2A Agent" || echo "No changes to commit"

# Deploy to Heroku
cd ..
git subtree push --prefix yahoo_mcp_server heroku-yahoo-a2a main
echo "✅ Deployed to Heroku"

# Restore MCP Procfile
cd yahoo_mcp_server
cp Procfile.mcp.backup Procfile
git checkout -- Procfile
rm Procfile.mcp.backup
echo "✅ Restored MCP Procfile"

echo "🎉 Deployment complete!"
EOF

# Make executable
chmod +x deploy_a2a.sh

# Run deployment
./deploy_a2a.sh
```

#### Option B: Manual Deployment

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# 1. Backup MCP Procfile
cp Procfile Procfile.mcp.backup

# 2. Swap to A2A Procfile
cp Procfile.a2a Procfile

# 3. Commit
git add Procfile
git commit -m "Deploy Yahoo A2A Agent"

# 4. Deploy from repo root
cd ..
git subtree push --prefix yahoo_mcp_server heroku-yahoo-a2a main

# 5. IMPORTANT: Restore MCP Procfile immediately!
cd yahoo_mcp_server
cp Procfile.mcp.backup Procfile
git checkout -- Procfile
rm Procfile.mcp.backup
```

**⚠️ Critical**: Always restore the MCP Procfile after deployment to avoid breaking the MCP server on next deploy.

---

### Step 4: Set Environment Variables

The Yahoo A2A agent needs access to Data Cloud and Snowflake (same as MCP server).

```bash
# Set config vars
heroku config:set \
  DATA_CLOUD_INSTANCE_URL=your_data_cloud_url \
  DATA_CLOUD_USERNAME=your_username \
  DATA_CLOUD_PASSWORD=your_password \
  SNOWFLAKE_ACCOUNT=your_account \
  SNOWFLAKE_USER=your_user \
  SNOWFLAKE_PASSWORD=your_password \
  SNOWFLAKE_DATABASE=ADCP_MEDIA_PLATFORM \
  SNOWFLAKE_SCHEMA=YAHOO_DSP \
  SNOWFLAKE_WAREHOUSE=your_warehouse \
  YAHOO_AGENT_CARD_URL=https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json \
  -a yahoo-a2a-agent
```

**Note**: You can copy these values from your existing MCP server:

```bash
# View MCP server config
heroku config -a yahoo-mcp-server

# Copy specific values
heroku config:get DATA_CLOUD_INSTANCE_URL -a yahoo-mcp-server
```

---

### Step 5: Verify Deployment

```bash
# Check app status
heroku info -a yahoo-a2a-agent

# View logs
heroku logs --tail -a yahoo-a2a-agent

# Open app in browser
heroku open -a yahoo-a2a-agent
```

---

### Step 6: Test Deployed Endpoints

#### Test 1: Health Check

```bash
curl https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "agent": "yahoo_sales_agent"
}
```

#### Test 2: Agent Card Discovery

```bash
curl https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json
```

**Expected response**:
```json
{
  "name": "yahoo_sales_agent",
  "description": "Yahoo Advertising Platform Agent - AdCP v2.3.0 compliant...",
  "skills": [
    {
      "id": "echo",
      "name": "Echo",
      "description": "Simple echo test skill..."
    }
  ],
  "url": "https://yahoo-a2a-agent.herokuapp.com/a2a/yahoo_sales_agent"
}
```

#### Test 3: Echo Skill Execution

```bash
curl -X POST https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "task/execute",
    "params": {
      "skill_id": "echo",
      "input": "Hello from cURL!"
    },
    "id": 1
  }'
```

**Expected response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "message": "Echo from Yahoo A2A Agent: Hello from cURL!",
    "agent": "yahoo_sales_agent",
    "skill": "echo"
  },
  "id": 1
}
```

---

## 🚀 Nike A2A Agent Deployment

### Prerequisites

1. ✅ Yahoo A2A agent deployed and tested
2. ✅ Nike agent files created in `nike_a2a_agent/` folder
3. ✅ Local testing passed (optional)

### Step 1: Create Nike A2A Branch

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app

# Switch to main branch
git checkout main

# Create nike-a2a branch
git checkout -b nike-a2a

# Add Nike agent files
git add nike_a2a_agent/
git commit -m "Nike A2A agent - initial commit"
```

---

### Step 2: Create Heroku App

```bash
# Create new Heroku app
heroku create nike-a2a-campaign-agent

# Add Heroku remote
heroku git:remote -a nike-a2a-campaign-agent -r heroku-nike-a2a
```

**Output**:
```
Creating ⬢ nike-a2a-campaign-agent... done
https://nike-a2a-campaign-agent-xxxxx.herokuapp.com/ | https://git.heroku.com/nike-a2a-campaign-agent.git
```

---

### Step 3: Deploy to Heroku

```bash
# Deploy from nike-a2a branch
git subtree push --prefix nike_a2a_agent heroku-nike-a2a main
```

**Note**: Nike agent has its own folder (`nike_a2a_agent/`) separate from Yahoo's folder (`yahoo_mcp_server/`), so no Procfile conflicts!

---

### Step 4: Set Environment Variables

```bash
# Set config vars
heroku config:set \
  ANTHROPIC_API_KEY=your_anthropic_key \
  YAHOO_AGENT_URL=https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent \
  YAHOO_AGENT_CARD_URL=https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json \
  NIKE_AGENT_URL=https://nike-a2a-campaign-agent-xxxxx.herokuapp.com/a2a/nike_campaign_agent \
  -a nike-a2a-campaign-agent
```

---

### Step 5: Verify Deployment

```bash
# Check app status
heroku info -a nike-a2a-campaign-agent

# View logs
heroku logs --tail -a nike-a2a-campaign-agent

# Open app in browser
heroku open -a nike-a2a-campaign-agent
```

---

### Step 6: Test Nike Agent Endpoints

#### Test 1: Health Check

```bash
curl https://nike-a2a-campaign-agent-xxxxx.herokuapp.com/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "agent": "nike_campaign_agent",
  "yahoo_agent_connected": "https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent"
}
```

#### Test 2: Nike Agent Card

```bash
curl https://nike-a2a-campaign-agent-xxxxx.herokuapp.com/a2a/nike_campaign_agent/.well-known/agent.json
```

**Expected response**:
```json
{
  "name": "nike_campaign_agent",
  "description": "Nike Campaign Planning Agent...",
  "skills": [
    {
      "id": "plan_campaign",
      "name": "Plan Campaign",
      ...
    },
    {
      "id": "test_connection",
      "name": "Test Connection",
      ...
    }
  ]
}
```

#### Test 3: Nike → Yahoo Connection Test

```bash
curl -X POST https://nike-a2a-campaign-agent-xxxxx.herokuapp.com/a2a/nike_campaign_agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "task/execute",
    "params": {
      "skill_id": "test_connection",
      "input": "Hello from Nike to Yahoo!"
    },
    "id": 1
  }'
```

**Expected response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "test": "connection",
    "yahoo_response": {
      "status": "success",
      "message": "Echo from Yahoo A2A Agent: Hello from Nike to Yahoo!",
      "agent": "yahoo_sales_agent",
      "skill": "echo"
    },
    "message": "Successfully connected to Yahoo A2A Sales Agent!"
  },
  "id": 1
}
```

**✅ If this works, Nike ↔ Yahoo A2A communication is fully operational!**

---

### Step 7: Switch Back to Main Branch

```bash
# Switch back to main (keeps nike-a2a branch clean)
git checkout main
```

---

## 🔄 Updating Nike A2A Agent

After making changes to Nike agent:

```bash
# Switch to nike-a2a branch
git checkout nike-a2a

# Make your changes to nike_a2a_agent/ files
# ...

# Commit changes
git add nike_a2a_agent/
git commit -m "Update Nike A2A agent"

# Deploy
git subtree push --prefix nike_a2a_agent heroku-nike-a2a main

# Switch back to main
git checkout main
```

---

## 🔄 Updating Yahoo A2A Agent

After making changes to `yahoo_a2a_server.py` or other files:

### Using Deployment Script

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server
./deploy_a2a.sh
```

### Manual Update

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# 1. Commit your changes
git add yahoo_a2a_server.py yahoo-agent-card.json
git commit -m "Update Yahoo A2A agent"

# 2. Backup and swap Procfile
cp Procfile Procfile.mcp.backup
cp Procfile.a2a Procfile
git add Procfile
git commit -m "Deploy A2A agent"

# 3. Deploy
cd ..
git subtree push --prefix yahoo_mcp_server heroku-yahoo-a2a main

# 4. Restore Procfile
cd yahoo_mcp_server
cp Procfile.mcp.backup Procfile
git checkout -- Procfile
rm Procfile.mcp.backup
```

---

## 🐛 Troubleshooting

### Issue 1: "fatal: 'heroku-yahoo-a2a' does not appear to be a git repository"

**Solution**: Add the Heroku remote:
```bash
heroku git:remote -a yahoo-a2a-agent -r heroku-yahoo-a2a
```

### Issue 2: "No web processes running"

**Check Procfile**:
```bash
heroku run cat Procfile -a yahoo-a2a-agent
```

Should show:
```
web: python yahoo_a2a_server.py
```

If it shows `web: python server_http.py`, you deployed with the wrong Procfile.

**Fix**:
```bash
cd yahoo_mcp_server
cp Procfile.a2a Procfile
git add Procfile
git commit -m "Fix Procfile for A2A"
cd ..
git subtree push --prefix yahoo_mcp_server heroku-yahoo-a2a main
```

### Issue 3: "Module not found: a2a"

**Check requirements.txt**:
```bash
heroku run pip list -a yahoo-a2a-agent | grep a2a
```

Should show `a2a-sdk 0.2.16`.

If not, ensure `requirements.txt` includes `a2a-sdk==0.2.16` and redeploy.

### Issue 4: "Application Error"

**View logs**:
```bash
heroku logs --tail -a yahoo-a2a-agent
```

Common causes:
- Missing environment variables
- Python syntax errors
- Missing dependencies

### Issue 5: 404 on Agent Card URL

**Check URL format**:
```
✅ Correct: /a2a/yahoo_sales_agent/.well-known/agent.json
❌ Wrong:   /yahoo_sales_agent/.well-known/agent.json
❌ Wrong:   /a2a/.well-known/agent.json
```

---

## 📊 Monitoring

### View Real-Time Logs

```bash
heroku logs --tail -a yahoo-a2a-agent
```

### Check Dyno Status

```bash
heroku ps -a yahoo-a2a-agent
```

### Restart App

```bash
heroku restart -a yahoo-a2a-agent
```

### Scale Dynos

```bash
# Scale up
heroku ps:scale web=1 -a yahoo-a2a-agent

# Scale down (stop)
heroku ps:scale web=0 -a yahoo-a2a-agent
```

---

## 🔗 Important URLs

### Yahoo A2A Agent
- **App Dashboard**: https://dashboard.heroku.com/apps/yahoo-a2a-agent
- **Root**: https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/
- **Health**: https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/health
- **Agent Card**: https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json
- **Task Endpoint**: https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent

### Yahoo MCP Server (Existing)
- **App Dashboard**: https://dashboard.heroku.com/apps/yahoo-mcp-server
- **Root**: https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/
- **MCP Endpoint**: https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp

### Streamlit UI (Existing)
- **App Dashboard**: https://dashboard.heroku.com/apps/adcp-campaign-planner
- **Root**: https://adcp-campaign-planner-xxxxx.herokuapp.com/

---

## 📝 Configuration Summary

### Procfile Mapping

| App | Procfile | Command |
|-----|----------|---------|
| yahoo-mcp-server | `Procfile` | `web: python server_http.py` |
| yahoo-a2a-agent | `Procfile.a2a` → `Procfile` | `web: python yahoo_a2a_server.py` |
| adcp-campaign-planner | `Procfile.streamlit` → `Procfile` | `web: streamlit run streamlit_app.py...` |

### Git Remotes

```bash
git remote -v
```

| Remote | App | URL |
|--------|-----|-----|
| heroku | yahoo-mcp-server | https://git.heroku.com/yahoo-mcp-server.git |
| heroku-yahoo-a2a | yahoo-a2a-agent | https://git.heroku.com/yahoo-a2a-agent.git |
| heroku-streamlit | adcp-campaign-planner | https://git.heroku.com/adcp-campaign-planner.git |
| origin | GitHub | https://github.com/arupsarkar-sfdc/admcp-media-app.git |

### Deployment Commands

| App | Command |
|-----|---------|
| yahoo-mcp-server | `git push heroku main` |
| yahoo-a2a-agent | `git subtree push --prefix yahoo_mcp_server heroku-yahoo-a2a main` |
| adcp-campaign-planner | `git subtree push --prefix yahoo_mcp_server heroku-streamlit main` |

---

## ✅ Deployment Checklist

### Yahoo A2A Agent

- [ ] Created Heroku app: `yahoo-a2a-agent`
- [ ] Added Heroku remote: `heroku-yahoo-a2a`
- [ ] Created `Procfile.a2a`
- [ ] Added `a2a-sdk==0.2.16` to `requirements.txt`
- [ ] Set all environment variables
- [ ] Deployed using `git subtree push`
- [ ] Verified health endpoint
- [ ] Verified agent card endpoint
- [ ] Tested echo skill with cURL
- [ ] Restored MCP Procfile after deployment
- [ ] Documented all URLs

---

## 🚀 Next Steps

After Yahoo A2A Agent is deployed and tested:

1. **Phase 2**: Build Nike A2A Campaign Agent
2. **Phase 3**: Add real skills to Yahoo A2A (discover_products, create_campaign, etc.)
3. **Phase 4**: Integrate Claude with Nike agent
4. **Phase 5**: Enable bidirectional communication
5. **Phase 6**: Add Streamlit UI for Nike agent

---

## 📚 Related Documentation

- [A2A Implementation Plan](A2A_IMPLEMENTATION_PLAN.md)
- [Yahoo MCP Server Deployment](yahoo_mcp_server/HEROKU_DEPLOYMENT.md)
- [Streamlit Deployment](yahoo_mcp_server/STREAMLIT_HEROKU_DEPLOYMENT.md)
- [Agentic Experience Guide](yahoo_mcp_server/AGENTIC_EXPERIENCE_GUIDE.md)

---

**Last Updated**: 2025-11-24
**Status**: Yahoo A2A Agent - Deployed ✅

