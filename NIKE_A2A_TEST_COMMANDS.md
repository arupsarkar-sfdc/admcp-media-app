# Nike A2A Campaign Agent - Test Commands

## Deployed Agent Information

- **Agent Name**: Nike A2A Campaign Agent
- **Heroku App**: `nike-a2a-campaign-agent`
- **Base URL**: `https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com`
- **Agent Endpoint**: `/a2a/nike_campaign_agent`
- **Agent Card**: `/a2a/nike_campaign_agent/.well-known/agent.json`
- **Protocol**: A2A (JSON-RPC 2.0)
- **Role**: Campaign orchestrator that delegates to Yahoo Sales Agent

---

## Architecture

```
User → Nike Agent (Orchestrator) → Yahoo Agent (Advertising Platform) → Data Cloud/Snowflake
```

**Nike Agent**:
- No database credentials needed
- Acts as HTTP client to Yahoo agent
- Orchestrates campaign planning workflow

**Yahoo Agent**:
- Has Snowflake and Data Cloud credentials
- Performs actual data operations
- Returns advertising inventory and campaign data

---

## Test Commands

### 1. Health Check

```bash
curl https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "agent": "nike_campaign_agent",
  "yahoo_agent_connected": "https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent"
}
```

---

### 2. Get Agent Card (Discover Capabilities)

```bash
curl https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com/a2a/nike_campaign_agent/.well-known/agent.json
```

**Expected Response**:
```json
{
  "name": "nike_campaign_agent",
  "description": "Nike Campaign Planning Agent - Orchestrates advertising campaigns by delegating to Yahoo Sales Agent for inventory discovery and campaign creation.",
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["application/json"],
  "skills": [
    {
      "id": "plan_campaign",
      "name": "Plan Campaign",
      "description": "Plan an advertising campaign based on business objectives. Delegates to Yahoo Sales Agent for product discovery and campaign creation.",
      "tags": ["campaign", "planning", "orchestration"]
    },
    {
      "id": "test_connection",
      "name": "Test Connection",
      "description": "Test A2A connectivity with Yahoo Sales Agent using echo skill.",
      "tags": ["test", "connectivity"]
    }
  ],
  "url": "https://nike-a2a-campaign-agent.herokuapp.com/a2a/nike_campaign_agent",
  "capabilities": {},
  "version": "1.0.0"
}
```

---

### 3. Test Connection Skill

**Purpose**: Verify A2A connectivity between Nike and Yahoo agents

```bash
curl -X POST https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com/a2a/nike_campaign_agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "task/execute",
    "params": {
      "skill_id": "test_connection",
      "input": "Hello from Nike A2A Agent!"
    },
    "id": 1
  }'
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "test": "connection",
    "yahoo_response": {
      "status": "success",
      "message": "Echo from Yahoo A2A Agent: Hello from Nike A2A Agent!",
      "agent": "yahoo_sales_agent",
      "skill": "echo"
    },
    "message": "Successfully connected to Yahoo A2A Sales Agent!"
  },
  "id": 1
}
```

---

### 4. Plan Campaign Skill

**Purpose**: Test campaign planning orchestration (currently calls Yahoo echo, Phase 4 will add real discovery)

```bash
curl -X POST https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com/a2a/nike_campaign_agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "task/execute",
    "params": {
      "skill_id": "plan_campaign",
      "input": "Nike running shoes campaign for Q1 2025, budget $25,000"
    },
    "id": 2
  }'
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "skill": "plan_campaign",
    "note": "Phase 2: Basic connectivity test. Phase 4 will add Claude orchestration.",
    "yahoo_response": {
      "status": "success",
      "message": "Echo from Yahoo A2A Agent: Campaign planning request: Nike running shoes campaign for Q1 2025, budget $25,000",
      "agent": "yahoo_sales_agent",
      "skill": "echo"
    }
  },
  "id": 2
}
```

---

### 5. Test Invalid Skill (Error Handling)

```bash
curl -X POST https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com/a2a/nike_campaign_agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "task/execute",
    "params": {
      "skill_id": "nonexistent_skill",
      "input": "test"
    },
    "id": 3
  }'
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Skill not found: nonexistent_skill"
  },
  "id": 3
}
```

---

## Communication Flow

### Test Connection Flow
```
User → Nike Agent → Yahoo Agent (echo) → Yahoo Agent Response → Nike Agent Response → User
```

### Plan Campaign Flow (Current - Phase 2)
```
User → Nike Agent → Yahoo Agent (echo) → Yahoo Agent Response → Nike Agent Response → User
```

### Plan Campaign Flow (Future - Phase 4)
```
User → Nike Agent → Claude AI → Yahoo Agent (discover_products) → Data Cloud Query → 
Nike Agent → Yahoo Agent (create_campaign) → Snowflake Write → Nike Agent Response → User
```

---

## Environment Variables

Nike agent only needs:
- `YAHOO_AGENT_URL` (default: `https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent`)
- `YAHOO_AGENT_CARD_URL` (default: `https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json`)
- `PORT` (set by Heroku)

**No Snowflake or Data Cloud credentials needed** - Nike is just an orchestrator!

---

## Deployment

### Current Deployment
```bash
# Nike agent is deployed from nike-a2a branch
git checkout nike-a2a
git subtree push --prefix nike_a2a_agent heroku-nike-a2a main
```

### Check Logs
```bash
heroku logs --tail -a nike-a2a-campaign-agent
```

---

## Integration with A2A Demo App

The Nike agent is used in the A2A Communication Demo Streamlit app:
- **Demo URL**: `https://a2a-communication-demo-1e53a5e4c7d3.herokuapp.com`
- **Left Panel**: Nike Agent controls
- **Right Panel**: Yahoo Agent controls
- **Center**: Communication flow visualization

---

## Next Steps (Phase 4)

1. **Add Claude AI Integration**: Use Anthropic API for natural language understanding
2. **Update `plan_campaign` skill**: Call Yahoo's `discover_products` instead of `echo`
3. **Add campaign execution**: Call Yahoo's `create_campaign` to write to Snowflake
4. **Add status tracking**: Call Yahoo's `get_campaign_status` for delivery metrics

---

## Status

✅ **Phase 1**: Basic A2A connectivity - COMPLETE  
✅ **Phase 2**: Nike agent deployment - COMPLETE  
✅ **Phase 3**: Yahoo advertising skills - COMPLETE  
⏳ **Phase 4**: Claude orchestration - PENDING  

---

## Related Documentation

- [Yahoo A2A Test Commands](YAHOO_A2A_TEST_STATUS.md)
- [A2A Heroku Deployment Guide](A2A_HEROKU_DEPLOYMENT.md)
- [Complete System Documentation](COMPLETE_SYSTEM_DOCUMENTATION.md)
- [A2A Implementation Plan](A2A_IMPLEMENTATION_PLAN.md)

