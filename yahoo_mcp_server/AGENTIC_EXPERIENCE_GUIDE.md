# 🤖 Agentic Experience Guide

## What is an Agentic Experience?

Instead of manually calling API endpoints, users have **natural conversations** with an AI agent that:
- Understands intent from natural language
- Automatically calls the right tools
- Asks clarifying questions
- Provides context-aware responses
- Handles multi-step workflows

---

## 🚀 Quick Start - Local Python Agent

### **Step 1: Install Dependencies**

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server

# Install Anthropic (Claude)
uv pip install anthropic

# Your other dependencies are already installed
```

### **Step 2: Set API Key**

```bash
# Option A: Export in terminal
export ANTHROPIC_API_KEY=your_anthropic_api_key

# Option B: Add to .env file
echo "ANTHROPIC_API_KEY=your_key" >> .env
```

**Get Anthropic API Key:**
- Go to: https://console.anthropic.com/
- Sign up / Log in
- API Keys → Create Key
- Copy the key (starts with `sk-ant-...`)

### **Step 3: Run the Agent**

```bash
uv run python advertising_agent.py
```

---

## 💬 Example Conversations

### **Example 1: Discover Products**

```
You: Show me advertising options for Nike running shoes

🤖 Agent: Let me find suitable advertising options for Nike running shoes...

[Agent calls: get_products(brief="Nike running shoes")]

🤖 Agent: I found 5 excellent advertising options for Nike running shoes:

1. **Yahoo Sports - Display**
   - Pricing: $12.50 CPM (15% enterprise discount applied!)
   - Reach: 2,000,000 sports enthusiasts
   - Formats: Display, Video
   - Minimum Budget: $10,000

2. **Yahoo Finance - Display**
   - Pricing: $15.00 CPM
   - Reach: 1,500,000 professionals
   - Great for athletic apparel with purchasing power

Would you like more details about any of these options, or shall we 
create a campaign?
```

### **Example 2: Create Campaign**

```
You: Let's create a campaign with Yahoo Sports for $50,000

🤖 Agent: Great choice! Yahoo Sports is perfect for Nike running shoes.
Before I create the campaign, let me confirm a few details:

- Product: Yahoo Sports - Display
- Budget: $50,000
- Audience: 2M sports enthusiasts

What should we name this campaign, and what are your flight dates?

You: Call it "Nike Air Max Spring 2025", run it Q1 2025

🤖 Agent: Perfect! Let me check the available creative formats first...

[Agent calls: list_creative_formats()]

🤖 Agent: I can create ads in these formats:
- 728x90 (Leaderboard)
- 300x250 (Medium Rectangle)
- 160x600 (Skyscraper)

Which formats would you like? (You can choose multiple)

You: Leaderboard and rectangle

🤖 Agent: Excellent choices! Let me create your campaign now...

[Agent calls: create_media_buy(...)]

🤖 Agent: ✅ Campaign created successfully!

**Campaign Details:**
- Campaign ID: nike_air_max_spring_2025_20251120
- Name: Nike Air Max Spring 2025
- Budget: $50,000
- Product: Yahoo Sports - Display
- Formats: 728x90, 300x250
- Flight: January 1 - March 31, 2025
- Status: Pending

**Next Steps:**
1. Upload your creative assets
2. Review targeting settings
3. Activate when ready

Would you like me to show you the campaign details or make any changes?
```

### **Example 3: Check Performance**

```
You: How is my Nike campaign doing?

🤖 Agent: Let me check the performance of your Nike Air Max campaign...

[Agent calls: get_media_buy_delivery("nike_air_max_spring_2025_20251120")]

🤖 Agent: Here's how your Nike Air Max Spring 2025 campaign is performing:

**Delivery Metrics:**
- Impressions: 1,200,000 delivered
- Clicks: 10,200 (CTR: 0.85%)
- Conversions: 856 (CVR: 8.4%)
- Spend: $15,000 of $50,000

**Pacing Analysis:**
- You're 30% through the budget
- 25% through the flight period
- Slightly ahead of pace (good!)

Your CTR of 0.85% is above average for display campaigns. The campaign
is performing well! Would you like to see a detailed report or make any
adjustments?
```

### **Example 4: Optimize Campaign**

```
You: The performance looks good. Can we increase the budget to $75K?

🤖 Agent: Great idea! With that performance, increasing budget makes sense.
Let me update your campaign budget...

[Agent calls: update_media_buy(id="...", updates={"total_budget": 75000})]

🤖 Agent: ✅ Budget updated successfully!

**Updated Campaign:**
- New Budget: $75,000 (was $50,000)
- Current Spend: $15,000
- Remaining: $60,000

With the increased budget and current CTR of 0.85%, you can expect:
- Additional ~4.8M impressions
- ~40,800 more clicks
- ~3,400 more conversions

Pacing will continue at the current rate. I'll monitor performance and
let you know if any adjustments are needed!
```

---

## 🎭 What Makes It "Agentic"?

### **Traditional API (Not Agentic):**
```python
# User must know exact API calls
products = client.call_tool("get_products", {
    "brief": "Nike campaign",
    "budget_range": [10000, 50000]
})

# User must parse response
product_id = products['products'][0]['product_id']

# User must construct complex payload
campaign = client.call_tool("create_media_buy", {
    "campaign_name": "Nike Q1",
    "packages": [{
        "product_id": product_id,
        "budget": 50000,
        "format_ids": [
            {"agent_url": "...", "id": "display_728x90"}
        ],
        ...
    }],
    ...
})
```

### **Agentic Experience:**
```
User: "Create a $50K Nike campaign for Q1"

Agent: [Automatically]:
  1. Understands intent
  2. Discovers products
  3. Asks about formats
  4. Confirms details
  5. Creates campaign
  6. Explains results
```

**Key Differences:**
- ✅ Natural language (not API calls)
- ✅ Agent asks clarifying questions
- ✅ Multi-step workflows handled automatically
- ✅ Context maintained across turns
- ✅ Results explained in human terms

---

## 🛠️ Customization

### **Modify Agent Personality**

Edit the `system_prompt` in `advertising_agent.py`:

```python
system_prompt = """You are a helpful advertising campaign manager.

Personality: Professional, enthusiastic, data-driven

Guidelines:
1. Always confirm budgets before creating campaigns
2. Suggest optimizations proactively
3. Use data to support recommendations
4. Explain advertising terms simply

Example tone: "Your CTR of 0.85% is above the 0.65% industry average 
for display ads. Great creative!"
"""
```

### **Add Custom Commands**

```python
# In the main loop, add:
if user_input.lower() == 'summary':
    # Show conversation summary
    print("📊 Conversation Summary:")
    print(f"   Messages: {len(agent.conversation_history)}")
    # etc...
```

### **Multi-Agent System**

Create specialized agents:

```python
# Campaign Creation Agent
creation_agent = AdvertisingAgent(
    mcp_url=MCP_URL,
    system_prompt="You specialize in creating new campaigns..."
)

# Optimization Agent
optimization_agent = AdvertisingAgent(
    mcp_url=MCP_URL,
    system_prompt="You specialize in optimizing existing campaigns..."
)

# Route based on intent
if "create" in user_input:
    response = await creation_agent.chat(user_input)
elif "optimize" in user_input:
    response = await optimization_agent.chat(user_input)
```

---

## 🚀 Next Steps

### **1. Deploy Agent as Web Service**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
agent = AdvertisingAgent(mcp_url=MCP_URL)

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    response = await agent.chat(request.message)
    return {"response": response}
```

### **2. Add to Slack**

```python
from slack_bolt.async_app import AsyncApp

slack_app = AsyncApp(token=SLACK_TOKEN)
agent = AdvertisingAgent(mcp_url=MCP_URL)

@slack_app.message()
async def handle_message(message, say):
    response = await agent.chat(message['text'])
    await say(response)
```

### **3. Integrate with Salesforce**

Once Agentforce connects to your MCP server, it becomes the agent!
Users can chat with Einstein Agent, which uses your MCP tools.

---

## 📊 Monitoring Agent Behavior

### **Add Logging:**

```python
# In advertising_agent.py
import logging

logging.basicConfig(
    filename='agent.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Log every tool call
logging.info(f"User: {user_message}")
logging.info(f"Tool called: {tool_name}")
logging.info(f"Agent: {response}")
```

### **Track Metrics:**

```python
class AgentMetrics:
    def __init__(self):
        self.conversations = 0
        self.tool_calls = 0
        self.successful_campaigns = 0
    
    def log_tool_call(self, tool_name):
        self.tool_calls += 1
        if tool_name == "create_media_buy":
            self.successful_campaigns += 1
```

---

## 🎯 Use Cases

### **1. Sales Assistant**
"Help me find the best ad placement for this client's budget"

### **2. Campaign Manager**
"Show me all active campaigns and their performance"

### **3. Optimization Advisor**
"Which campaigns are under-performing and how can we fix them?"

### **4. Budget Planner**
"I have $500K for Q1. How should I allocate it across products?"

### **5. Creative Advisor**
"What formats perform best for sports apparel campaigns?"

---

## 🐛 Troubleshooting

### **"No AI API key found"**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### **"Failed to connect to MCP server"**
```bash
# Check if Heroku app is up
curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json
```

### **"Tool call failed"**
Check Heroku logs:
```bash
heroku logs --tail -a yahoo-mcp-server
```

---

## 📚 Resources

- **Anthropic Claude Docs**: https://docs.anthropic.com/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Your MCP Server**: https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com

---

**Ready to experience agentic AI?** Run `uv run python advertising_agent.py` and start chatting! 🚀

---

## 📝 Standalone Conversation Prompts

Copy these ready-to-use conversation flows to test your agent:

### **Prompt 1: Product Discovery for Nike**
```
Show me advertising options for Nike running shoes. I want to target sports enthusiasts aged 25-45 in the US with a budget of $50,000 for Q1 2025.
```

**Expected Agent Flow:**
1. Calls `get_products()` with the brief
2. Returns 3-5 matching products with pricing and reach
3. Asks if user wants details or to create a campaign

---

### **Prompt 2: Campaign Creation Flow**
```
I want to create a campaign for Nike Air Max shoes. Budget is $50,000, targeting US sports enthusiasts aged 25-45. Call it "Nike Air Max Spring 2025" and run it from January 1 to March 31, 2025. Use Yahoo Sports - Display product with leaderboard and medium rectangle formats.
```

**Expected Agent Flow:**
1. Calls `list_creative_formats()` to validate formats
2. Confirms all details with user
3. Calls `create_media_buy()` with full package structure
4. Returns campaign ID and success confirmation
5. Suggests next steps (upload creatives, review targeting)

---

### **Prompt 3: Multi-Turn Campaign Creation**
```
Turn 1: "I need help creating a Nike campaign"

Turn 2: "My budget is $50,000 and I want to target sports fans"

Turn 3: "Let's use Yahoo Sports - Display"

Turn 4: "Use the leaderboard and rectangle formats"

Turn 5: "Call it Nike Air Max Spring 2025, run it Q1 2025"

Turn 6: "Yes, create it"
```

**Expected Agent Flow:**
- Maintains context across all turns
- Asks clarifying questions at each step
- Summarizes details before final creation
- Confirms user intent before making changes

---

### **Prompt 4: Performance Check**
```
How is my Nike Air Max Spring 2025 campaign performing? Show me impressions, clicks, conversions, and pacing.
```

**Expected Agent Flow:**
1. Calls `get_media_buy_delivery()` with campaign ID
2. Presents metrics in readable format
3. Analyzes pacing (ahead/behind/on track)
4. Suggests optimizations if needed

---

### **Prompt 5: Campaign Optimization**
```
My Nike Air Max campaign (ID: nike_air_max_spring_2025_20251120_101430) is performing well with a CTR of 0.85%. Can we increase the budget from $50,000 to $75,000 to capitalize on this performance?
```

**Expected Agent Flow:**
1. Calls `get_media_buy_delivery()` to verify current performance
2. Confirms the budget increase with user
3. Calls `update_media_buy()` with new budget
4. Returns updated campaign details
5. Projects expected results with new budget

---

### **Prompt 6: Comprehensive Report Request**
```
Generate a 7-day performance report for campaign nike_air_max_spring_2025_20251120_101430. Include delivery metrics, top-performing formats, and recommendations.
```

**Expected Agent Flow:**
1. Calls `get_media_buy_report()` with 7-day timeframe
2. Presents report sections clearly:
   - Summary metrics
   - Format performance breakdown
   - Day-by-day trends
   - Recommendations
3. Asks if user wants to export or make changes

---

### **Prompt 7: Multi-Campaign Comparison**
```
I have three campaigns running for Nike. Can you compare their performance and tell me which one I should invest more budget in?

Campaign IDs:
- nike_air_max_spring_2025_20251120_101430
- nike_react_running_q1_2025
- nike_basketball_winter_2025
```

**Expected Agent Flow:**
1. Calls `get_media_buy_delivery()` for each campaign
2. Compares key metrics side-by-side:
   - CTR, CVR, CPC, ROAS
   - Pacing vs flight progress
   - Budget efficiency
3. Provides data-driven recommendation
4. Offers to update budgets if user agrees

---

### **Prompt 8: Budget Allocation Planning**
```
I'm Nike's media buyer and have $500,000 to spend in Q1 2025 targeting sports enthusiasts interested in running, basketball, and training gear. Help me plan how to allocate this budget across Yahoo's advertising products.
```

**Expected Agent Flow:**
1. Calls `get_products()` with each segment:
   - Running gear → Yahoo Sports
   - Basketball → Yahoo Sports + Entertainment
   - Training gear → Yahoo Fitness properties
2. Suggests allocation strategy:
   - 40% Yahoo Sports ($200K) - highest affinity
   - 30% Yahoo Finance ($150K) - affluent professionals
   - 20% Yahoo Mail ($100K) - broad reach
   - 10% Yahoo Entertainment ($50K) - lifestyle alignment
3. Asks if user wants to create campaigns with this allocation

---

### **Prompt 9: Format Performance Analysis**
```
Which creative formats perform best for Nike campaigns? Should I focus on display, video, or native ads?
```

**Expected Agent Flow:**
1. Calls `list_creative_formats()` to show available options
2. May call `get_media_buy_report()` for existing campaigns
3. Explains format strengths:
   - Display (728x90, 300x250): Best for awareness, lower CPM
   - Video (16:9): Higher engagement, better for storytelling
   - Native: Highest CTR, seamless integration
4. Recommends mix based on campaign goals

---

### **Prompt 10: Campaign Troubleshooting**
```
My campaign nike_air_max_spring_2025_20251120_101430 is under-pacing. We're 40% through the flight but only 25% through the budget. What should I do?
```

**Expected Agent Flow:**
1. Calls `get_media_buy_delivery()` to confirm status
2. Diagnoses potential issues:
   - Audience too narrow?
   - Bid too low?
   - Creative fatigue?
3. Suggests fixes:
   - Expand geo targeting
   - Increase daily budget cap
   - Refresh creative assets
4. Offers to make updates via `update_media_buy()`

---

### **Prompt 11: Creative Format Selection Help**
```
I'm new to digital advertising. What creative formats should I use for a Nike running shoe campaign? I don't know the technical sizes.
```

**Expected Agent Flow:**
1. Calls `list_creative_formats()`
2. Explains each format in simple terms:
   - "Leaderboard (728x90): Horizontal banner at top of page"
   - "Rectangle (300x250): Square ad in sidebar"
   - "Skyscraper (160x600): Tall vertical ad"
3. Recommends starter set: Leaderboard + Rectangle
4. Explains why: "These two cover 80% of ad placements"
5. Asks if user wants to proceed with these

---

### **Prompt 12: End-to-End Campaign Launch**
```
I need to launch a complete Nike campaign by end of day. Budget: $75,000. Target: US sports fans 18-54. Goal: 10 million impressions for new Air Max launch. Flight: Feb 1 - Mar 31, 2025. What do you recommend?
```

**Expected Agent Flow:**
1. **Discovery Phase:**
   - Calls `get_products()` to find best inventory
   - Recommends Yahoo Sports + Yahoo Finance mix

2. **Planning Phase:**
   - Calculates: $75K ÷ $12.50 CPM = 6M impressions (Yahoo Sports)
   - Suggests: Split budget 60/40 to hit 10M goal
   - Calls `list_creative_formats()` for format options

3. **Creation Phase:**
   - Confirms: "Create 2 campaigns totaling $75K?"
   - Calls `create_media_buy()` twice:
     - Campaign 1: Yahoo Sports ($45K)
     - Campaign 2: Yahoo Finance ($30K)

4. **Launch Phase:**
   - Returns both campaign IDs
   - Provides launch checklist:
     ✅ Campaigns created
     ⏳ Upload creatives
     ⏳ Review targeting
     ⏳ Activate campaigns

5. **Follow-up:**
   - "I'll check back tomorrow to see how they're performing"

---

### **Prompt 13: Conversational Troubleshooting**
```
Turn 1: "Something's wrong with my campaign"

Turn 2: "nike_air_max_spring_2025_20251120_101430"

Turn 3: "It's spending too fast"

Turn 4: "Yes, please slow it down to match the flight schedule"

Turn 5: "Actually, first show me the current pacing"
```

**Expected Agent Flow:**
- Patient, asks clarifying questions
- Doesn't assume intent
- Shows data before making changes
- Confirms every action

---

## 🎯 Testing Your Agent

Use these prompts to test:

1. **Intent Understanding**: Does it understand "Nike campaign" vs "show products"?
2. **Context Retention**: Does it remember campaign details across turns?
3. **Clarification**: Does it ask for missing info (budget, dates)?
4. **Confirmation**: Does it confirm before creating/updating?
5. **Error Handling**: How does it handle invalid campaign IDs?
6. **Multi-Tool**: Can it chain multiple tool calls?
7. **Explanation**: Does it explain results in plain language?

---

## 📋 Prompt Template for Custom Scenarios

```
**Scenario**: [What the user wants to achieve]

**User Prompt**: 
"[Natural language request]"

**Expected Agent Behavior**:
1. [First action/question]
2. [Tool calls needed]
3. [Response format]
4. [Follow-up suggestions]

**Success Criteria**:
- ✅ [Metric 1]
- ✅ [Metric 2]
- ✅ [User satisfaction indicator]
```

---

**Copy any prompt above and paste into your agent to test the agentic experience!** 🚀

