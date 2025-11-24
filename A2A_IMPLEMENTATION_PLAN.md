# A2A Implementation Plan

## Overview

Build Yahoo A2A Sales Agent and Nike A2A Campaign Agent using Google's A2A SDK to enable bidirectional agent-to-agent communication over the existing MCP infrastructure.

---

## Architecture

```
Nike A2A Agent (Heroku: nike-a2a-campaign-agent)
    ↕️ A2A Protocol (JSON-RPC 2.0, bidirectional)
Yahoo A2A Agent (Heroku: yahoo-a2a-agent)
    ↓ Internal calls
Yahoo MCP Server (Heroku: yahoo-mcp-server, existing)
    ↓
Data Cloud → Snowflake
```

---

## Implementation Phases

### ✅ Phase 1: Setup and Hello World (Yahoo A2A Server)

**Goal**: Create a simple Yahoo A2A agent with an echo skill

**Tasks**:
1. ✅ Create implementation plan document
2. ⬜ Add `a2a-sdk` to yahoo_mcp_server requirements
3. ⬜ Create Yahoo agent card JSON
4. ⬜ Create Yahoo A2A server with echo skill
5. ⬜ Test locally with Python client
6. ⬜ Deploy to Heroku
7. ⬜ Test deployed endpoint with cURL

**Files to Create**:
- `yahoo_mcp_server/yahoo-agent-card.json`
- `yahoo_mcp_server/yahoo_a2a_server.py`
- `yahoo_mcp_server/Procfile.a2a`
- `yahoo_mcp_server/test_yahoo_a2a_local.py`

**Success Criteria**:
- Yahoo A2A server responds to echo task locally
- Yahoo A2A server deployed to Heroku
- Agent card accessible at `/.well-known/agent.json`

---

### ⬜ Phase 2: Nike A2A Agent (Hello World Client)

**Goal**: Create Nike A2A agent that calls Yahoo's echo skill

**Tasks**:
1. ⬜ Create nike_a2a_agent folder structure
2. ⬜ Create Nike agent card JSON
3. ⬜ Create Nike A2A agent with RemoteA2aAgent
4. ⬜ Test Nike → Yahoo communication locally
5. ⬜ Deploy Nike agent to Heroku
6. ⬜ Test Nike → Yahoo communication on Heroku

**Files to Create**:
- `nike_a2a_agent/nike-agent-card.json`
- `nike_a2a_agent/nike_agent.py`
- `nike_a2a_agent/Procfile`
- `nike_a2a_agent/requirements.txt`
- `nike_a2a_agent/.env.template`
- `nike_a2a_agent/test_nike_local.py`

**Success Criteria**:
- Nike agent successfully calls Yahoo echo skill locally
- Nike agent deployed to Heroku
- Nike → Yahoo communication works end-to-end

---

### ⬜ Phase 3: Yahoo Real Skills (MCP Integration)

**Goal**: Add real advertising skills to Yahoo A2A agent

**Tasks**:
1. ⬜ Add `discover_products` skill (wraps `get_products` MCP tool)
2. ⬜ Add `create_campaign` skill (wraps `create_media_buy` MCP tool)
3. ⬜ Add `get_campaign_status` skill (wraps `get_media_buy_delivery` MCP tool)
4. ⬜ Update Yahoo agent card with real skills
5. ⬜ Test each skill locally
6. ⬜ Deploy to Heroku
7. ⬜ Test with cURL and Python client

**Files to Update**:
- `yahoo_mcp_server/yahoo-agent-card.json`
- `yahoo_mcp_server/yahoo_a2a_server.py`

**Success Criteria**:
- All three skills work locally
- Skills return real data from Data Cloud/Snowflake
- Deployed Yahoo agent responds with real advertising data

---

### ⬜ Phase 4: Nike Orchestration (Claude Integration)

**Goal**: Add Claude-powered orchestration to Nike agent

**Tasks**:
1. ⬜ Integrate Anthropic Claude for NLU
2. ⬜ Add campaign planning logic
3. ⬜ Implement task delegation to Yahoo agent
4. ⬜ Add response processing and formatting
5. ⬜ Test complete workflow locally
6. ⬜ Deploy to Heroku
7. ⬜ Test end-to-end campaign creation

**Files to Update**:
- `nike_a2a_agent/nike_agent.py`

**Success Criteria**:
- Nike agent understands natural language queries
- Nike agent delegates to Yahoo agent appropriately
- Complete campaign workflow works end-to-end

---

### ⬜ Phase 5: Bidirectional Communication

**Goal**: Enable Nike agent to receive calls from other agents

**Tasks**:
1. ⬜ Add A2A server endpoints to Nike agent
2. ⬜ Implement Nike's exposed skills
3. ⬜ Test Nike as both client and server
4. ⬜ Deploy to Heroku
5. ⬜ Test bidirectional communication

**Files to Update**:
- `nike_a2a_agent/nike-agent-card.json`
- `nike_a2a_agent/nike_agent.py`

**Success Criteria**:
- Nike agent exposes A2A endpoints
- Other agents can call Nike's skills
- Nike can both call and be called

---

### ⬜ Phase 6: Streamlit UI (Optional)

**Goal**: Add web UI for Nike agent

**Tasks**:
1. ⬜ Create Streamlit app for Nike agent
2. ⬜ Add chat interface
3. ⬜ Add A2A communication visualization
4. ⬜ Deploy to Heroku
5. ⬜ Test UI

**Files to Create**:
- `nike_a2a_agent/streamlit_app.py`
- `nike_a2a_agent/Procfile.streamlit`

**Success Criteria**:
- Web UI allows natural language campaign planning
- UI shows A2A communication flow
- Deployed and accessible

---

## Deployment Strategy

### Heroku Apps

1. **yahoo-mcp-server** (existing)
   - Purpose: MCP server for Salesforce Agentforce
   - Branch: `main`
   - URL: `https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com`

2. **yahoo-a2a-agent** (new)
   - Purpose: A2A wrapper for Yahoo advertising platform
   - Branch: `yahoo-a2a`
   - URL: `https://yahoo-a2a-agent-xxxxx.herokuapp.com`

3. **nike-a2a-campaign-agent** (new)
   - Purpose: Campaign planning orchestrator
   - Branch: `nike-a2a`
   - URL: `https://nike-a2a-campaign-agent-xxxxx.herokuapp.com`

4. **adcp-campaign-planner** (existing)
   - Purpose: Streamlit UI for MCP
   - Branch: `mcp-client`
   - URL: `https://adcp-campaign-planner-xxxxx.herokuapp.com`

### Git Branch Strategy

```
main (MCP server)
├── yahoo-a2a (Yahoo A2A agent)
└── nike-a2a (Nike A2A agent)
    └── nike-a2a-ui (Nike Streamlit UI)
```

### Environment Variables

**Yahoo A2A Agent**:
```bash
# Data Cloud & Snowflake (reuse from MCP server)
DATA_CLOUD_INSTANCE_URL=...
DATA_CLOUD_USERNAME=...
DATA_CLOUD_PASSWORD=...
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_USER=...
SNOWFLAKE_PASSWORD=...
SNOWFLAKE_DATABASE=...
SNOWFLAKE_SCHEMA=...
SNOWFLAKE_WAREHOUSE=...

# A2A specific
YAHOO_AGENT_CARD_URL=https://yahoo-a2a-agent-xxxxx.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json
```

**Nike A2A Agent**:
```bash
ANTHROPIC_API_KEY=...
YAHOO_AGENT_CARD_URL=https://yahoo-a2a-agent-xxxxx.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json
NIKE_AGENT_URL=https://nike-a2a-campaign-agent-xxxxx.herokuapp.com/a2a/nike_campaign_agent
```

---

## Testing Strategy

### Local Testing

1. **Yahoo A2A Server**:
   ```bash
   cd yahoo_mcp_server
   uv run python yahoo_a2a_server.py
   # Server runs on http://localhost:8001
   ```

2. **Nike A2A Agent**:
   ```bash
   cd nike_a2a_agent
   uv run python nike_agent.py
   # Server runs on http://localhost:8002
   ```

3. **Test Communication**:
   ```bash
   cd nike_a2a_agent
   uv run python test_nike_local.py
   ```

### Heroku Testing

1. **Deploy Yahoo A2A**:
   ```bash
   git subtree push --prefix yahoo_mcp_server heroku-yahoo-a2a main
   ```

2. **Test Yahoo Endpoints**:
   ```bash
   curl https://yahoo-a2a-agent-xxxxx.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json
   ```

3. **Deploy Nike A2A**:
   ```bash
   git subtree push --prefix nike_a2a_agent heroku-nike-a2a main
   ```

4. **Test Nike → Yahoo**:
   ```bash
   curl -X POST https://nike-a2a-campaign-agent-xxxxx.herokuapp.com/test
   ```

---

## Folder Structure

```
admcp-media-app/
├── A2A_IMPLEMENTATION_PLAN.md (this file)
│
├── yahoo_mcp_server/
│   ├── server_http.py (existing MCP server)
│   ├── yahoo_a2a_server.py (new A2A wrapper)
│   ├── yahoo-agent-card.json (new)
│   ├── Procfile (existing, for MCP)
│   ├── Procfile.a2a (new, for A2A)
│   ├── requirements.txt (add a2a-sdk)
│   └── test_yahoo_a2a_local.py (new)
│
├── nike_a2a_agent/
│   ├── nike_agent.py (new)
│   ├── nike-agent-card.json (new)
│   ├── Procfile (new)
│   ├── requirements.txt (new)
│   ├── .env (new)
│   ├── .env.template (new)
│   ├── test_nike_local.py (new)
│   └── streamlit_app.py (optional, Phase 6)
│
└── database/ (existing)
```

---

## Success Metrics

1. ✅ Yahoo A2A agent deployed and accessible
2. ✅ Nike A2A agent deployed and accessible
3. ✅ Agent cards accessible via HTTP
4. ✅ Nike → Yahoo communication works
5. ✅ Yahoo → Nike responses work
6. ✅ Real advertising data flows through A2A
7. ✅ Complete campaign workflow via A2A
8. ✅ Bidirectional communication works
9. ✅ All tests pass locally and on Heroku
10. ✅ Documentation complete

---

## Current Status

**Phase**: 1 - Setup and Hello World
**Status**: In Progress
**Last Updated**: 2025-11-24

---

## Next Steps

1. Add `a2a-sdk` to yahoo_mcp_server requirements
2. Create Yahoo agent card JSON
3. Create Yahoo A2A server with echo skill
4. Test locally

---

## Notes

- Keep existing MCP server running (don't break Salesforce Agentforce integration)
- Use Google's `a2a-sdk==0.2.16` (same version as tutorial)
- Follow A2A protocol specification for agent cards and communication
- Test each phase thoroughly before moving to next phase
- Document all endpoints and testing procedures

