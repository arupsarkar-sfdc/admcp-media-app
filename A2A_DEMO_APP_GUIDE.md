# A2A Communication Demo - Streamlit App Guide

## Overview

**App Name**: A2A Communication Demo  
**Heroku App**: `a2a-communication-demo`  
**Live URL**: https://a2a-communication-demo-99c09c9b8b09.herokuapp.com/  
**Status**: ✅ DEPLOYED & OPERATIONAL

---

## Purpose

Real-time visualization of Agent-to-Agent (A2A) protocol communication between Nike Campaign Agent and Yahoo Sales Agent. Demonstrates bidirectional A2A communication with split-screen UI.

---

## Features

### 1. Split-Screen Interface

```
┌─────────────────────────────────────────────────────────┐
│              A2A Communication Demo                      │
├──────────────┬──────────────┬──────────────────────────┤
│   Nike       │     Flow     │        Yahoo             │
│   Agent      │  Visualization│        Agent            │
│  (Left)      │   (Center)   │       (Right)           │
├──────────────┼──────────────┼──────────────────────────┤
│ • Skills     │  User → Nike │  • Skills                │
│ • Input      │     ⬇️       │  • Input                 │
│ • Call       │  Nike → Yahoo│  • Call                  │
│   Button     │     ➡️       │    Button               │
│              │  Yahoo → Nike│                          │
│              │     ⬅️       │                          │
├──────────────┴──────────────┴──────────────────────────┤
│          Communication Log (Chronological)              │
│  • Timestamped entries                                  │
│  • Request/Response pairs                               │
│  • Nested Yahoo responses                               │
│  • Color-coded (blue=request, green=response)          │
└─────────────────────────────────────────────────────────┘
```

---

### 2. Nike Agent Panel (Left)

**Available Skills**:
- `test_connection` - Test A2A connectivity with Yahoo
- `plan_campaign` - Plan campaign (calls Yahoo agent)

**Input Options**:
- Text area for custom messages
- Skill selection dropdown
- "Call Nike Agent" button

**How It Works**:
- Nike agent receives your request
- Nike internally calls Yahoo agent
- Full Nike → Yahoo → Nike flow shown in log
- Nested Yahoo response displayed

---

### 3. Yahoo Agent Panel (Right)

**Available Skills**:
- `echo` - Simple echo test
- `discover_products` - Search advertising inventory (future)
- `create_campaign` - Create campaign (future)
- `get_campaign_status` - Get campaign metrics (future)

**Input Options**:
- Text area for custom messages
- Skill selection dropdown
- "Call Yahoo Agent" button

**How It Works**:
- Direct call to Yahoo agent
- Simple request → response flow
- No nested calls

---

### 4. Communication Flow (Center)

**Visualizes**:
- Current communication direction (arrows)
- Source and target agents
- Nested communication detection
- Real-time flow updates

**Flow Types**:
- **Simple**: User → Yahoo → User
- **Nested**: User → Nike → Yahoo → Nike → User

---

### 5. Communication Log (Bottom)

**Features**:
- ✅ Reverse chronological order (latest first)
- ✅ Expandable entries with timestamps
- ✅ Side-by-side request/response view
- ✅ Dark mode compatible styling
- ✅ JSON syntax highlighting
- ✅ Nested Yahoo response extraction
- ✅ Color coding:
  - 🔵 Blue boxes = Requests
  - 🟢 Green boxes = Successful responses
  - 🔴 Red boxes = Errors

---

## Testing the Demo App

### Test 1: Nike Agent - Test Connection

**Steps**:
1. Go to left panel (Nike Agent)
2. Select skill: `test_connection`
3. Input: `Hello from Nike!`
4. Click "🚀 Call Nike Agent"

**Expected Result**:
```json
{
  "status": "success",
  "test": "connection",
  "yahoo_response": {
    "status": "success",
    "message": "Echo from Yahoo A2A Agent: Hello from Nike!",
    "agent": "yahoo_sales_agent",
    "skill": "echo"
  },
  "message": "Successfully connected to Yahoo A2A Sales Agent!"
}
```

---

### Test 2: Nike Agent - Plan Campaign

**Steps**:
1. Go to left panel (Nike Agent)
2. Select skill: `plan_campaign`
3. Input: `Nike running shoes campaign for Q1 2025, budget $25,000`
4. Click "🚀 Call Nike Agent"

**Expected Result**:
```json
{
  "status": "success",
  "skill": "plan_campaign",
  "note": "Phase 2: Basic connectivity test. Phase 4 will add Claude orchestration.",
  "yahoo_response": {
    "status": "success",
    "message": "Echo from Yahoo A2A Agent: Campaign planning request: Nike running shoes campaign for Q1 2025, budget $25,000",
    "agent": "yahoo_sales_agent",
    "skill": "echo"
  }
}
```

---

### Test 3: Yahoo Agent - Echo

**Steps**:
1. Go to right panel (Yahoo Agent)
2. Select skill: `echo`
3. Input: `Hello from Yahoo!`
4. Click "🚀 Call Yahoo Agent"

**Expected Result**:
```json
{
  "status": "success",
  "message": "Echo from Yahoo A2A Agent: Hello from Yahoo!",
  "agent": "yahoo_sales_agent",
  "skill": "echo"
}
```

---

## Architecture

### Frontend (Streamlit)
- **File**: `nike_a2a_agent/a2a_demo_app.py`
- **Framework**: Streamlit 1.28+
- **Language**: Python 3.12
- **HTTP Client**: `httpx` (async)

### Agent Endpoints (Hardcoded)
```python
NIKE_AGENT_URL = "https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com/a2a/nike_campaign_agent"
YAHOO_AGENT_URL = "https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent"
```

### Communication Protocol
- **Protocol**: A2A (Agent-to-Agent)
- **Format**: JSON-RPC 2.0
- **Transport**: HTTPS POST
- **Headers**: `Content-Type: application/json`

### Request Format
```json
{
  "jsonrpc": "2.0",
  "method": "task/execute",
  "params": {
    "skill_id": "test_connection",
    "input": "Hello from Nike!"
  },
  "id": 1
}
```

### Response Format
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "message": "...",
    "data": {...}
  },
  "id": 1
}
```

---

## Deployment

### Current Branch
```bash
git branch
# * a2a-demo
```

### Deployment Commands
```bash
# From a2a-demo branch
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app

# Deploy to Heroku
git subtree push --prefix nike_a2a_agent heroku-a2a-demo main
```

### Procfile
```
web: streamlit run a2a_demo_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

### Dependencies
```
streamlit>=1.28.0
httpx>=0.24.0
python-dotenv>=1.0.0
```

---

## Environment Variables

**Heroku Config Vars**:
```bash
# Nike Agent URL
NIKE_AGENT_URL=https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com/a2a/nike_campaign_agent

# Yahoo Agent URL  
YAHOO_AGENT_URL=https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent

# Port (set by Heroku)
PORT=<dynamic>
```

**Note**: URLs are hardcoded in the app, so env vars are optional.

---

## Styling & UI

### Dark Mode Compatible
All message boxes have dark backgrounds with light text:
- **Request boxes**: Dark blue background (#1e3a5f)
- **Response boxes**: Dark green background (#1b4d3e)
- **Error boxes**: Dark red background (#4d1f1f)

### Custom CSS
```css
.agent-card {
  padding: 20px;
  border-radius: 10px;
}

.nike-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.yahoo-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.message-box {
  padding: 15px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 14px;
  font-weight: 500;
}
```

---

## Sidebar Features

### Configuration Display
- Nike Agent URL (read-only)
- Yahoo Agent URL (read-only)

### Communication Stats
- Total calls counter
- Updates in real-time

### Controls
- "🗑️ Clear Log" button
- Clears all communication history

### About Section
- Brief description of demo
- Protocol information
- Agent roles explanation

---

## Debugging Features

### Debug Logs (in app)
The app includes extensive debugging output:
- Request URL
- Request payload (formatted JSON)
- Response status code
- Response headers
- Response text (first 500 chars)

### Heroku Logs
```bash
# View real-time logs
heroku logs --tail -a a2a-communication-demo

# View last 500 lines
heroku logs -n 500 -a a2a-communication-demo
```

---

## Known Behaviors

### Session State
- Communication log persists during session
- Cleared on page refresh or manual clear
- Each request gets incremental ID

### Error Handling
- Invalid skill → Returns JSON-RPC error
- Network timeout → Shows error in UI
- Malformed JSON → Displays error message
- All errors logged to Heroku logs

### Performance
- Average response time: 1-3 seconds
- Includes network roundtrip to 2 Heroku apps
- No caching (fresh data every call)

---

## Future Enhancements (Phase 4)

### 1. Add Real Skills to Yahoo Panel
Currently only shows `echo`. Add:
- `discover_products`
- `create_campaign`
- `get_campaign_status`

### 2. Update Nike `plan_campaign`
Change from calling Yahoo `echo` to calling Yahoo `discover_products`

### 3. Add Campaign Workflow
Multi-step workflow in the demo:
1. Discover products
2. Select products
3. Create campaign
4. Check status

### 4. Add Data Visualization
- Product comparison charts
- Campaign budget breakdown
- Delivery metrics graphs

### 5. Add Export
- Export communication log as JSON
- Download campaign plan as PDF

---

## Troubleshooting

### Issue: "Connection Error"
**Cause**: Nike or Yahoo agent is down  
**Solution**: 
```bash
# Check Nike agent
curl https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com/health

# Check Yahoo agent
curl https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/health
```

### Issue: "Timeout Error"
**Cause**: Slow response from agents (>30s)  
**Solution**: Increase timeout in code:
```python
async with httpx.AsyncClient(timeout=60.0) as client:
```

### Issue: "Application Error"
**Cause**: Streamlit app crashed  
**Solution**: 
```bash
# Check logs
heroku logs --tail -a a2a-communication-demo

# Restart dyno
heroku restart -a a2a-communication-demo
```

### Issue: "Nested response not showing"
**Cause**: Response format changed  
**Solution**: Check if response has `yahoo_response` key:
```python
if "result" in log["response"] and "yahoo_response" in log["response"]["result"]:
    # Display nested response
```

---

## Validation Checklist

✅ **Deployment**
- [x] App deployed to Heroku
- [x] Procfile.streamlit configured
- [x] Dependencies installed
- [x] Environment variables set (optional)

✅ **Functionality**
- [x] Nike panel working
- [x] Yahoo panel working
- [x] Communication log updating
- [x] Flow visualization working
- [x] Clear log button working

✅ **UI/UX**
- [x] Split-screen layout
- [x] Dark mode styling
- [x] Expandable log entries
- [x] Color-coded messages
- [x] Help text under each panel

✅ **Integration**
- [x] Nike agent calls working
- [x] Yahoo agent calls working
- [x] Nested responses displayed
- [x] Error handling working

---

## Related Documentation

- [Nike A2A Test Commands](NIKE_A2A_TEST_COMMANDS.md)
- [Yahoo A2A Test Status](YAHOO_A2A_TEST_STATUS.md)
- [A2A Implementation Plan](A2A_IMPLEMENTATION_PLAN.md)
- [A2A Heroku Deployment](A2A_HEROKU_DEPLOYMENT.md)
- [Complete System Documentation](COMPLETE_SYSTEM_DOCUMENTATION.md)

---

## Quick Links

- **Live Demo**: https://a2a-communication-demo-99c09c9b8b09.herokuapp.com/
- **Nike Agent**: https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com
- **Yahoo Agent**: https://yahoo-a2a-agent-72829d23cce8.herokuapp.com
- **Source Code**: `nike_a2a_agent/a2a_demo_app.py`

---

## Status

✅ **DEPLOYED & OPERATIONAL**

- Heroku app running
- Both agent connections working
- UI fully functional
- Communication log working
- Ready for demonstration

---

**Last Updated**: 2025-11-24  
**Version**: 1.0.0  
**Maintained By**: Arup Sarkar

