# Streamlit App - Heroku Deployment Guide

This guide shows you how to deploy the AdCP Campaign Planner Streamlit app to Heroku as a separate app from the MCP server.

---

## 🎯 **Prerequisites**

1. ✅ Heroku CLI installed and logged in
2. ✅ Git repository initialized
3. ✅ MCP Server already deployed to Heroku (`yahoo-mcp-server`)

---

## 🚀 **Deployment Steps**

### **Step 1: Create a new Heroku app for Streamlit**

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# Create new Heroku app
heroku create adcp-campaign-planner
```

This will create a new app and give you a URL like:
- `https://adcp-campaign-planner-xxxxx.herokuapp.com`

---

### **Step 2: Deploy using the deployment script (Recommended - Safest)**

**⚠️ IMPORTANT:** The `Procfile` in your repo is for the MCP server (`web: python server_http.py`). We'll use a deployment script that safely swaps it during deployment and restores it afterward.

```bash
# From yahoo_mcp_server directory
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# Make the deployment script executable
chmod +x deploy_streamlit.sh

# Run the deployment script
./deploy_streamlit.sh
```

This script will:
1. ✅ Backup your MCP server Procfile
2. ✅ Swap to Streamlit Procfile
3. ✅ Deploy to Heroku
4. ✅ Restore the MCP server Procfile
5. ✅ Keep your repo clean

---

### **Step 2 Alternative: Manual Deployment (If you prefer)**

If you want to do it manually:

```bash
# From yahoo_mcp_server directory
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# 1. Backup MCP Procfile
cp Procfile Procfile.mcp.backup

# 2. Swap to Streamlit Procfile
cp Procfile.streamlit Procfile

# 3. Commit (if needed)
git add Procfile streamlit_app.py requirements.txt
git commit -m "Deploy Streamlit app" || echo "No changes"

# 4. Add Heroku remote for Streamlit app
heroku git:remote -a adcp-campaign-planner

# 5. Deploy
git push heroku main

# 6. IMPORTANT: Restore MCP Procfile immediately!
cp Procfile.mcp.backup Procfile
git checkout -- Procfile  # Restore in git
rm Procfile.mcp.backup
```

**⚠️ Don't forget step 6!** Otherwise your next MCP server deployment will fail.

---

### **Step 2 Alternative: Deploy from `mcp-client` branch**

If you are working on the `mcp-client` branch, use this command to deploy to Heroku (which always builds from `main`):

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app

# Push yahoo_mcp_server subtree to Heroku's main branch
git subtree push --prefix yahoo_mcp_server heroku-streamlit main
```

---

### **Step 3: Set Environment Variables**

```bash
# Set config vars in Heroku
heroku config:set \
  ANTHROPIC_API_KEY=your_anthropic_key_here \
  MCP_SERVER_URL=https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp \
  -a adcp-campaign-planner
```

**Note:** You can get your `ANTHROPIC_API_KEY` from your local `.env` file.

---

### **Step 4: Verify Deployment**

```bash
# Check app status
heroku info -a adcp-campaign-planner

# View logs
heroku logs --tail -a adcp-campaign-planner

# Open app in browser
heroku open -a adcp-campaign-planner
```

---

## 🔄 **Updating the Streamlit App**

After making changes to `streamlit_app.py`:

**Option 1: Use the deployment script (Recommended)**
```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server
./deploy_streamlit.sh
```

**Option 2: Manual update**
```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# Backup MCP Procfile
cp Procfile Procfile.mcp.backup

# Swap to Streamlit Procfile
cp Procfile.streamlit Procfile

# Commit changes
git add streamlit_app.py Procfile requirements.txt
git commit -m "Update Streamlit app"

# Push to Heroku (Streamlit app)
heroku git:remote -a adcp-campaign-planner
git push heroku main

# IMPORTANT: Restore MCP Procfile!
cp Procfile.mcp.backup Procfile
git checkout -- Procfile
rm Procfile.mcp.backup
```

---

## 🏗️ **Architecture**

```
User Browser
    ↓
Streamlit App (Heroku: adcp-campaign-planner)
    ↓
advertising_agent.py (Python)
    ↓
FastMCP Client (HTTP)
    ↓
Yahoo MCP Server (Heroku: yahoo-mcp-server)
    ↓
Data Cloud → Snowflake
```

**Two separate Heroku apps:**
- `yahoo-mcp-server` - MCP Server (FastMCP)
- `adcp-campaign-planner` - Streamlit Web UI

---

## 🐛 **Troubleshooting**

### **"No web processes running"**

Check that `Procfile` exists and has the correct content:
```bash
heroku run cat Procfile -a adcp-campaign-planner
```

Should show:
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

### **"Module not found: streamlit"**

Make sure `requirements.txt` includes `streamlit>=1.28.0`:
```bash
heroku run pip list -a adcp-campaign-planner | grep streamlit
```

### **"Failed to connect to MCP server"**

Check that `MCP_SERVER_URL` is set correctly:
```bash
heroku config:get MCP_SERVER_URL -a adcp-campaign-planner
```

Should be: `https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp`

### **"ANTHROPIC_API_KEY not found"**

Set it in Heroku:
```bash
heroku config:set ANTHROPIC_API_KEY=your_key -a adcp-campaign-planner
```

---

## 📝 **Quick Reference**

**App URLs:**
- MCP Server: `https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com`
- Streamlit App: `https://adcp-campaign-planner-xxxxx.herokuapp.com`

**Heroku Commands:**
```bash
# View logs
heroku logs --tail -a adcp-campaign-planner

# Restart app
heroku restart -a adcp-campaign-planner

# Check config
heroku config -a adcp-campaign-planner

# Open app
heroku open -a adcp-campaign-planner
```

---

## ✅ **Deployment Checklist**

- [ ] Created Heroku app: `adcp-campaign-planner`
- [ ] Copied `Procfile.streamlit` to `Procfile`
- [ ] Set `ANTHROPIC_API_KEY` config var
- [ ] Set `MCP_SERVER_URL` config var
- [ ] Pushed code to Heroku
- [ ] Verified app is running: `heroku open -a adcp-campaign-planner`
- [ ] Tested chat functionality
- [ ] Verified MCP server connection

---

**Ready to deploy?** Follow the steps above! 🚀

