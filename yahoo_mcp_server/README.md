# Yahoo MCP Server - AdCP Sales Agent

FastMCP server exposing Yahoo advertising inventory via AdCP Media Buy Protocol.

## Features

- **LLM-Powered Product Discovery**: Natural language campaign brief → matched products
- **Matched Audience Integration**: Products linked to Clean Room audience overlaps
- **Real-time Performance Metrics**: Campaign delivery, CTR, CVR, pacing
- **Principal Authentication**: Bearer token auth with access level discounts
- **Campaign Management**: Create, update, monitor media buys

## AdCP Tools

| Tool | Description |
|------|-------------|
| `get_products` | Discover inventory using natural language brief |
| `create_media_buy` | Create new campaign |
| `get_media_buy` | Get campaign configuration |
| `get_media_buy_delivery` | Real-time performance metrics |
| `update_media_buy` | Modify active campaign |
| `get_media_buy_report` | Generate analytics report |

## Quick Start

### 1. Install Dependencies

```bash
cd yahoo_mcp_server
uv sync
```

### 2. Configure Environment

```bash
cp env.template .env
# Edit .env and add your API keys:
# - GEMINI_API_KEY (required)
# - OPENAI_API_KEY (optional fallback)
```

### 3. Run Server

```bash
uv run python server.py
```

Server starts on: `http://localhost:8080/`

## Authentication

Include bearer token in requests:

```bash
x-adcp-auth: Bearer nike_token_12345
```

**Test Credentials**:
- Principal: `nike_advertiser`
- Token: `nike_token_12345`
- Access Level: `enterprise` (15% discount)

## Example Requests

### List Available Tools

```bash
curl http://localhost:8080/tools/list
```

### Discover Products

```bash
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
```

### Get Campaign Delivery

```bash
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

## Architecture

```
server.py                     # FastMCP entry point
├── models.py                 # SQLAlchemy ORM models
├── services/
│   ├── product_service.py    # LLM-powered discovery
│   ├── media_buy_service.py  # Campaign lifecycle
│   └── metrics_service.py    # Performance aggregation
└── utils/
    ├── auth.py               # Token authentication
    └── llm_client.py         # Gemini/OpenAI wrapper
```

## Database

Connects to: `../database/adcp_platform.db` (SQLite from Phase 1)

**Tables Used**:
- `principals` - Authentication
- `products` - Ad inventory
- `matched_audiences` - Clean Room output
- `media_buys` - Campaigns
- `delivery_metrics` - Performance data

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_PATH` | Yes | Path to SQLite database |
| `GEMINI_API_KEY` | Yes* | Google Gemini API key |
| `OPENAI_API_KEY` | No | OpenAI API key (fallback) |
| `MCP_HOST` | No | Server host (default: 0.0.0.0) |
| `MCP_PORT` | No | Server port (default: 8080) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

*At least one LLM API key required

## Next Steps

After server is running:
- **Phase 3**: Build Nike Streamlit Client to interact with this server
- **Testing**: Use curl or Postman to test endpoints
- **Migration**: Move database to PostgreSQL/Snowflake

## Troubleshooting

**Issue**: "LLM client initialization failed"
- **Fix**: Add `GEMINI_API_KEY` or `OPENAI_API_KEY` to `.env`

**Issue**: "Authentication required"
- **Fix**: Include `x-adcp-auth: Bearer nike_token_12345` header

**Issue**: "Database not found"
- **Fix**: Run Phase 1 database setup first: `python database/seed_data.py`

