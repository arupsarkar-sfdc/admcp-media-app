# AdCP Campaign Planner - Streamlit Web UI

Simple, fast web interface for the Yahoo MCP Server advertising agent.

---

## 🚀 **Quick Start (Local)**

### **1. Make sure dependencies are installed**
```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server
uv pip install streamlit
```

### **2. Make sure .env is configured**
```bash
# Should already have:
ANTHROPIC_API_KEY=sk-ant-...
MCP_SERVER_URL=https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp
```

### **3. Run Streamlit app**
```bash
streamlit run streamlit_app.py
```

### **4. Open browser**
```
http://localhost:8501
```

---

## ✨ **Features**

- ✅ **Chat Interface** - Natural language conversation
- ✅ **Example Prompts** - Quick start templates in sidebar
- ✅ **MCP Integration** - Connects to your Heroku MCP server
- ✅ **Real Tool Calls** - Actually executes tools (you'll see Heroku logs!)
- ✅ **Session Management** - Maintains conversation context
- ✅ **Clear History** - Reset conversation anytime
- ✅ **Status Display** - Shows connection status and configuration

---

## 🧪 **Test Prompts**

Try these in the chat:

1. **Product Discovery:**
   ```
   Show me advertising options for Nike running shoes with $50K budget
   ```

2. **List Formats:**
   ```
   What creative formats are available?
   ```

3. **Create Campaign:**
   ```
   Create a campaign for Nike with $30K for Q1 2025
   ```

4. **Check Performance:**
   ```
   How is campaign nike_air_max_2025 performing?
   ```

---

## 🔍 **Debugging**

### **View Logs**

**Streamlit logs** (in terminal):
```bash
# You'll see:
# 🔧 Calling tool: get_products
# ✅ Tool result received
```

**MCP Server logs** (Heroku):
```bash
heroku logs --tail -a yahoo-mcp-server

# You'll see the actual tool execution!
```

### **Connection Issues**

If you see "Failed to connect to MCP server":
1. Check MCP_SERVER_URL is correct
2. Verify Heroku server is running:
   ```bash
   curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json
   ```

### **API Key Issues**

If you see "ANTHROPIC_API_KEY not found":
1. Check `.env` file has the key
2. Restart Streamlit: `Ctrl+C` then `streamlit run streamlit_app.py`

---

## 🌐 **Deploy to Streamlit Cloud (FREE)**

### **Option 1: Streamlit Community Cloud**

1. **Push to GitHub** (if not already)
   ```bash
   git add yahoo_mcp_server/streamlit_app.py
   git add yahoo_mcp_server/.streamlit/
   git commit -m "Add Streamlit web UI"
   git push
   ```

2. **Go to** [share.streamlit.io](https://share.streamlit.io)

3. **Connect your GitHub repo**

4. **Set main file path:** `yahoo_mcp_server/streamlit_app.py`

5. **Add secrets** (in Streamlit Cloud dashboard):
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   MCP_SERVER_URL = "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp"
   ```

6. **Deploy!** - Gets a URL like `https://your-app.streamlit.app`

---

## 🚀 **Deploy to Heroku (Alternative)**

### **Create separate Heroku app for Streamlit**

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app

# Create Procfile for Streamlit
echo "web: streamlit run streamlit_app.py --server.port=\$PORT --server.address=0.0.0.0" > yahoo_mcp_server/Procfile.streamlit

# Create Heroku app
heroku create adcp-campaign-planner-streamlit

# Set config
heroku config:set \
  ANTHROPIC_API_KEY=your_key \
  MCP_SERVER_URL=https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp \
  -a adcp-campaign-planner-streamlit

# Deploy (note: different Procfile)
# Need to rename Procfile.streamlit to Procfile before deploying
```

---

## 📊 **Architecture**

```
User Browser
    ↓
Streamlit App (Python)
    ↓
advertising_agent.py (existing code!)
    ↓
FastMCP Client
    ↓
Yahoo MCP Server (Heroku)
    ↓
Data Cloud → Snowflake
```

**Key advantage:** Reuses your existing Python code! No protocol conversion needed.

---

## 🎨 **Customization**

### **Change Theme**

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B35"  # Orange
backgroundColor = "#F7F7F7"
```

### **Add Custom Logo**

In `streamlit_app.py`, add:
```python
st.image("logo.png", width=200)
```

### **Add More Sidebar Features**

In `streamlit_app.py`, add to sidebar:
```python
with st.sidebar:
    st.header("📊 Quick Stats")
    st.metric("Active Campaigns", "12")
    st.metric("Total Spend", "$245K")
```

---

## 🆚 **Streamlit vs Next.js**

| Feature | Streamlit | Next.js |
|---------|-----------|---------|
| **Build Time** | 20 mins | 2+ hours |
| **Code Reuse** | ✅ 100% | ❌ 0% (TypeScript rewrite) |
| **Works Now** | ✅ Yes | ❌ Protocol issues |
| **Deployment** | Free (Streamlit Cloud) | Heroku/Vercel |
| **UI Polish** | Good (functional) | Excellent (custom) |
| **Debugging** | Easy (Python logs) | Complex (TypeScript + HTTP) |

**Verdict:** Streamlit for **internal tools**, Next.js for **client-facing apps**.

---

## 🐛 **Troubleshooting**

### **"Module not found: streamlit"**
```bash
uv pip install streamlit
```

### **"Port 8501 already in use"**
```bash
lsof -ti:8501 | xargs kill -9
streamlit run streamlit_app.py
```

### **Chat not responding**
- Check terminal for errors
- Check Heroku logs for MCP server
- Verify ANTHROPIC_API_KEY is set

---

**Ready to test?** Just run: `streamlit run streamlit_app.py` 🚀



