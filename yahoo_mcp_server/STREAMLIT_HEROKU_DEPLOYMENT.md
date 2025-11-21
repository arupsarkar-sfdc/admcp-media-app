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

### **Step 2: Set up the Procfile for Streamlit**

The current `Procfile` is for the MCP server. We need to use `Procfile.streamlit` for the Streamlit app.

**Option A: Deploy using git subtree (Recommended)**

This keeps your main repo clean and deploys only what's needed:

```bash
# From yahoo_mcp_server directory
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# Copy Procfile.streamlit to Procfile temporarily
cp Procfile.streamlit Procfile.streamlit.backup

# Add Streamlit Procfile
cp Procfile.streamlit Procfile

# Commit the change
git add Procfile
git commit -m "Add Streamlit Procfile for Heroku deployment"

# Add Heroku remote for Streamlit app
heroku git:remote -a adcp-campaign-planner

# Push to Heroku
git push heroku main
```

**Option B: Use git subtree (Alternative - cleaner separation)**

```bash
# From project root
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app

# Deploy yahoo_mcp_server subdirectory to Heroku
git subtree push --prefix yahoo_mcp_server heroku-streamlit main
```

But first, you need to:
1. Rename `Procfile.streamlit` to `Procfile` in the subdirectory
2. Add Heroku remote: `heroku git:remote -a adcp-campaign-planner -r heroku-streamlit`

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

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# Make sure Procfile.streamlit is copied to Procfile
cp Procfile.streamlit Procfile

# Commit changes
git add streamlit_app.py Procfile
git commit -m "Update Streamlit app"

# Push to Heroku
git push heroku main
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

