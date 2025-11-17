# Phase 2: Yahoo MCP Server - Build Process

## Overview
Building Python FastMCP server with uv for dependency management. Server exposes AdCP tools for Nike to discover products, create campaigns, and monitor performance.

## Technology Stack
- **Package Manager**: uv (fast Python package installer)
- **Framework**: FastMCP (MCP server framework)
- **Database**: SQLite (from Phase 1)
- **LLM**: Gemini (primary), OpenAI (fallback)
- **Transport**: HTTP/SSE on port 8080
- **ORM**: SQLAlchemy

## Project Structure

```
yahoo_mcp_server/
├── pyproject.toml            # uv project configuration
├── uv.lock                   # Dependency lockfile (auto-generated)
├── .env.example              # Environment variables template
├── .env                      # Your actual API keys (gitignored)
├── server.py                 # FastMCP entry point
├── models.py                 # SQLAlchemy models
├── services/
│   ├── __init__.py
│   ├── product_service.py    # LLM-powered product discovery
│   ├── media_buy_service.py  # Campaign lifecycle management
│   └── metrics_service.py    # Performance aggregation
└── utils/
    ├── __init__.py
    ├── auth.py               # Token authentication
    └── llm_client.py         # Gemini/OpenAI wrapper
```

## Features

### AdCP Tools (MCP Endpoints)

1. **get_products(brief, budget_range)**
   - Natural language product discovery
   - Uses Gemini/OpenAI to parse campaign brief
   - Matches against products with audience overlap data
   - Applies enterprise pricing discount
   - Returns top 5-10 relevant products

2. **create_media_buy(...)**
   - Creates new campaign in database
   - Validates budget against product minimums
   - Links to matched audience
   - Assigns creatives
   - Returns media_buy_id

3. **get_media_buy_delivery(media_buy_id)**
   - Aggregates performance metrics from delivery_metrics table
   - Calculates CTR, CVR, pacing
   - Returns real-time performance data

4. **update_media_buy(media_buy_id, updates)**
   - Updates campaign budget, targeting, or status
   - Validates changes
   - Logs updates in audit_log

5. **get_media_buy_report(media_buy_id)**
   - Generates comprehensive analytics report
   - Day-by-day breakdown
   - Device/geo performance

### Authentication
- Bearer token validation (`nike_token_12345`)
- Principal-based access control
- Automatic enterprise discount application

### LLM Integration
- **Primary**: Gemini 1.5 Pro (via `google-generativeai`)
- **Fallback**: OpenAI GPT-4 (if Gemini fails)
- **Use Cases**:
  - Parse campaign briefs
  - Extract targeting criteria
  - Rank products by relevance

## Build Steps

### Step 1: Create Project Directory
```bash
mkdir yahoo_mcp_server
cd yahoo_mcp_server
```

### Step 2: Initialize uv Project
```bash
uv init --no-readme
```

### Step 3: Add Dependencies via uv
```bash
uv add fastmcp sqlalchemy google-generativeai openai python-dotenv
```

### Step 4: Create .env File
```bash
cp .env.example .env
# Add your API keys to .env
```

### Step 5: Implement Server Files
- Create all Python files (server.py, models.py, services/, utils/)

### Step 6: Run Server
```bash
uv run python server.py
```

Server will start on: `http://localhost:8080/mcp/`

### Step 7: Test Authentication
```bash
curl -X POST http://localhost:8080/mcp/ \
  -H "x-adcp-auth: Bearer nike_token_12345" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

## Environment Variables

Required in `.env`:
```bash
# Database
DATABASE_PATH=../database/adcp_platform.db

# LLM APIs (at least one required)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional fallback

# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8080
LOG_LEVEL=INFO
```

## Testing Flow

Once server is running:

1. **List Available Tools**
   ```bash
   curl -H "x-adcp-auth: Bearer nike_token_12345" \
        http://localhost:8080/mcp/tools/list
   ```

2. **Discover Products**
   ```bash
   curl -X POST http://localhost:8080/mcp/tools/call \
     -H "x-adcp-auth: Bearer nike_token_12345" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "get_products",
       "arguments": {
         "brief": "Display ads for sports enthusiasts interested in running",
         "budget_range": [10000, 100000]
       }
     }'
   ```

3. **Get Campaign Delivery**
   ```bash
   curl -X POST http://localhost:8080/mcp/tools/call \
     -H "x-adcp-auth: Bearer nike_token_12345" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "get_media_buy_delivery",
       "arguments": {
         "media_buy_id": "nike_air_max_spring_q1"
       }
     }'
   ```

## Next Phase
After MCP Server: **Phase 3 - Nike Streamlit Client**

---
**Build Status**: Ready to implement
**Estimated Time**: 30-40 minutes
**Dependencies**: Phase 1 database, Gemini/OpenAI API key

