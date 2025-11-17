# Phase 2: Yahoo MCP Server - Commands to Run

## ✅ Files Created

All Python files and configurations have been created:

```
yahoo_mcp_server/
├── pyproject.toml            ✓ uv configuration
├── env.template              ✓ Environment variables template
├── README.md                 ✓ Documentation
├── server.py                 ✓ FastMCP entry point
├── models.py                 ✓ SQLAlchemy ORM models
├── services/
│   ├── __init__.py           ✓
│   ├── product_service.py    ✓ LLM-powered discovery
│   ├── media_buy_service.py  ✓ Campaign management
│   └── metrics_service.py    ✓ Performance aggregation
└── utils/
    ├── __init__.py           ✓
    ├── auth.py               ✓ Token authentication
    └── llm_client.py         ✓ Gemini/OpenAI wrapper
```

## 📋 Commands to Run Manually

### Step 1: Navigate to Server Directory

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server
```

### Step 2: Install Dependencies with uv

```bash
uv sync
```

This will install:
- fastmcp
- sqlalchemy
- google-generativeai
- openai
- python-dotenv

### Step 3: Create .env File

```bash
cp env.template .env
```

### Step 4: Edit .env File (IMPORTANT!)

Open `.env` in your editor and add your API keys:

```bash
# Option 1: Using nano
nano .env

# Option 2: Using vi
vi .env

# Option 3: Using VS Code
code .env
```

**Required Configuration**:
```bash
# Database (should work as-is)
DATABASE_PATH=../database/adcp_platform.db

# LLM API Keys - ADD YOUR KEYS HERE!
GEMINI_API_KEY=your_actual_gemini_key_here
OPENAI_API_KEY=your_actual_openai_key_here  # Optional

# Server Configuration (can leave as-is)
MCP_HOST=0.0.0.0
MCP_PORT=8080
LOG_LEVEL=INFO
```

**How to get API keys**:
- **Gemini**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys

### Step 5: Test Database Connection

```bash
uv run python -c "from models import get_session; session = get_session('../database/adcp_platform.db'); print('✓ Database connected'); session.close()"
```

Expected output: `✓ Database connected`

### Step 6: Run the MCP Server

```bash
uv run python server.py
```

**Expected output**:
```
======================================================================
YAHOO SALES AGENT - MCP SERVER
======================================================================
Database: ../database/adcp_platform.db
Port: 8080
LLM: Gemini ✓ | OpenAI ✓
======================================================================
✓ Gemini client initialized
✓ OpenAI client initialized

🚀 Starting Yahoo MCP Server on http://0.0.0.0:8080/
📚 Documentation: http://0.0.0.0:8080/docs

INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

**Keep this terminal open** - the server needs to stay running.

### Step 7: Test Server (Open New Terminal)

In a **new terminal window**, test the server:

```bash
# Test 1: List available tools
curl http://localhost:8080/tools/list

# Test 2: Discover products (requires authentication)
curl -X POST http://localhost:8080/tools/call \
  -H "x-adcp-auth: Bearer nike_token_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_products",
    "arguments": {
      "brief": "Display ads for sports enthusiasts interested in running",
      "budget_range": [10000, 100000]
    }
  }'

# Test 3: Get campaign delivery metrics
curl -X POST http://localhost:8080/tools/call \
  -H "x-adcp-auth: Bearer nike_token_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_media_buy_delivery",
    "arguments": {
      "media_buy_id": "nike_air_max_spring_q1"
    }
  }'
```

## ✅ Verification Checklist

After running the server, verify:

- [ ] Server starts without errors
- [ ] Port 8080 is accessible
- [ ] Gemini/OpenAI client initialized successfully
- [ ] Database connection works
- [ ] `/tools/list` returns 6 tools
- [ ] `get_products` returns Yahoo inventory
- [ ] `get_media_buy_delivery` returns campaign metrics

## 🔧 Troubleshooting

### Issue: "Module 'fastmcp' not found"
**Solution**: Run `uv sync` again

### Issue: "LLM client initialization failed"
**Solution**: 
1. Check `.env` file has valid API keys
2. Verify API keys work: https://makersuite.google.com/app/apikey

### Issue: "Database not found"
**Solution**: 
1. Verify Phase 1 completed: `ls -lh ../database/adcp_platform.db`
2. Check `DATABASE_PATH` in `.env` is correct

### Issue: "Port 8080 already in use"
**Solution**: 
1. Change port in `.env`: `MCP_PORT=8081`
2. Or kill existing process: `lsof -ti:8080 | xargs kill`

### Issue: "Authentication required"
**Solution**: Include header in curl:
```bash
-H "x-adcp-auth: Bearer nike_token_12345"
```

## 📊 What's Working Now

After Phase 2 completion:

✅ **Yahoo MCP Server Running**
- 6 AdCP tools exposed
- LLM-powered product discovery
- Real-time campaign metrics
- Matched audience integration
- Principal authentication

✅ **Database Integration**
- Connected to Phase 1 SQLite database
- 850K matched users from Clean Room
- 5 Yahoo products available
- 1 active campaign with 20 days metrics

## 🎯 Next: Phase 3

**Nike Streamlit Client** - Beautiful UI for campaign managers

Will provide:
- Product discovery interface
- Campaign creation wizard
- Performance dashboard with charts
- Real-time metrics visualization

---

**Ready when you are!** Let me know once the server is running successfully, and I'll build the Streamlit client.

