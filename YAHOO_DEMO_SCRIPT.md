# Yahoo Demo Script - November 25, 2025

**Purpose**: Structured demo flow showcasing Yahoo's vision alignment with implementation  
**Duration**: 15-20 minutes  
**Audience**: Yahoo stakeholders

---

## 🎯 Demo Objectives

1. ✅ Showcase **seamless data access** (natural language → instant results)
2. ✅ Demonstrate **proposal data** (pricing, targeting, formats, forecasts)
3. ✅ Highlight **matched audience integration** (Clean Room data)
4. ✅ Present **performance reporting** (real-time metrics, KPIs)
5. ✅ Illustrate **agentic experience** (conversational, intelligent)

---

## 📋 Pre-Demo Checklist

### **Technical Setup** (Do this 30 minutes before demo)

```bash
# 1. Verify MCP server is running
curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json

# 2. Set API key
export ANTHROPIC_API_KEY=your_key

# 3. Test agent connection
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server
uv run python advertising_agent.py
# Type: "test" or "hello" to verify connection

# 4. Have backup: Test with HTTP client
uv run python nike_campaign_workflow_http_client.py
```

### **Data Verification**

```bash
# Verify campaigns exist for performance demo
# Check Snowflake or use get_media_buy_delivery tool
```

### **Backup Plan**

- If agent fails: Use HTTP client (`nike_campaign_workflow_http_client.py`)
- If MCP server down: Show static screenshots + explain architecture
- If API key issues: Use pre-recorded video

---

## 🎬 Demo Flow (15-20 minutes)

### **Part 1: Introduction (2 minutes)**

**What to Say:**
> "Today I'll demonstrate how we've implemented Yahoo's vision for agency workflows. You'll see natural language conversations that power the entire campaign lifecycle - from planning to optimization to wrap-up."

**Key Points:**
- Natural language interface (no API knowledge needed)
- MCP protocol enables AI-native access
- Real-time data via Data Cloud Zero Copy

---

### **Part 2: Planning & Discovery (4 minutes)**

**Demo Prompt 1: Product Discovery**
```
Show me advertising options for Nike running shoes. I want to target sports enthusiasts aged 25-45 in the US with a budget of $50,000 for Q1 2025.
```

**What to Highlight:**
- ✅ **Seamless Access**: Natural language → instant product recommendations
- ✅ **Proposal Data**: Pricing (with enterprise discounts), targeting, formats, reach forecasts
- ✅ **Matched Audience**: Show audience overlap data (850K users, demographics)
- ✅ **LLM Intelligence**: Agent understands intent and filters appropriately

**Expected Agent Flow:**
1. Calls `get_products()` with extracted criteria
2. Returns 3-5 products with full proposal data
3. Shows matched audience demographics
4. Explains pricing and reach estimates

**What to Say:**
> "Notice how the agent understands the campaign brief, discovers relevant inventory, and presents complete proposal data - pricing, targeting, formats, and audience overlap - all from a simple natural language request. This is the seamless access Yahoo envisioned."

---

### **Part 3: Buying & Campaign Creation (5 minutes)**

**Demo Prompt 2: Campaign Creation**
```
I want to create a campaign for Nike Air Max shoes. Budget is $50,000, targeting US sports enthusiasts aged 25-45. Call it "Nike Air Max Spring 2025" and run it from January 1 to March 31, 2025. Use Yahoo Sports - Display product with leaderboard and medium rectangle formats.
```

**What to Highlight:**
- ✅ **Package-Based Structure**: AdCP v2.3.0 compliant
- ✅ **Creative Format Specifications**: Agent validates formats before creation
- ✅ **Automated Workflow**: Multi-step process handled automatically
- ✅ **Confirmation**: Agent confirms details before creating

**Expected Agent Flow:**
1. Calls `list_creative_formats()` to validate formats
2. Confirms all details
3. Calls `create_media_buy()` with full package structure
4. Returns campaign ID and success confirmation

**What to Say:**
> "The agent handles the entire campaign creation workflow - validating formats, confirming details, and creating the campaign in seconds. This demonstrates the proposal data vision: complete targeting, inventory, pricing, and creative specs all integrated."

**Alternative (if first prompt too complex):**
```
Turn 1: "I need help creating a Nike campaign"
Turn 2: "My budget is $50,000 and I want to target sports fans"
Turn 3: "Let's use Yahoo Sports - Display"
Turn 4: "Use the leaderboard and rectangle formats"
Turn 5: "Call it Nike Air Max Spring 2025, run it Q1 2025"
Turn 6: "Yes, create it"
```

**What to Say:**
> "Notice how the agent maintains context across multiple turns, asks clarifying questions, and only creates the campaign after confirmation. This is the agentic experience - intelligent, conversational, and safe."

---

### **Part 4: Optimization & Performance (4 minutes)**

**Demo Prompt 3: Performance Check**
```
How is my Nike Air Max Spring 2025 campaign performing? Show me impressions, clicks, conversions, and pacing.
```

**What to Highlight:**
- ✅ **Real-Time Metrics**: Instant access via Data Cloud Zero Copy
- ✅ **Performance Summary**: Budget/spend, KPIs (CTR, CVR, CPM, CPC, CPA)
- ✅ **Pacing Analysis**: Budget pacing vs. time pacing
- ✅ **Channel Breakdown**: Device/format performance

**Expected Agent Flow:**
1. Calls `get_media_buy_delivery()` with campaign ID
2. Presents metrics in readable format
3. Analyzes pacing (ahead/behind/on track)
4. Suggests optimizations if needed

**What to Say:**
> "Here we see real-time performance data - impressions, clicks, conversions, and pacing - all accessible instantly through natural language. This is the measurement and analytics vision: comprehensive performance tracking with actionable insights."

**Demo Prompt 4: Campaign Optimization**
```
The performance looks good. Can we increase the budget from $50,000 to $75,000 to capitalize on this performance?
```

**What to Highlight:**
- ✅ **Continuous Action**: Budget updates in real-time
- ✅ **Agent Intelligence**: Projects expected results with new budget
- ✅ **Safe Updates**: Confirms before making changes

**Expected Agent Flow:**
1. Confirms budget increase
2. Calls `update_media_buy()` with new budget
3. Projects expected results
4. Explains impact

**What to Say:**
> "The agent enables continuous optimization - budget adjustments, status changes, all through conversation. While we haven't implemented full automated recommendations yet, the foundation is here for dynamic budget reallocation across channels and creatives."

---

### **Part 5: Wrap-Up & Reporting (3 minutes)**

**Demo Prompt 5: Comprehensive Report**
```
Generate a 7-day performance report for campaign nike_air_max_spring_2025_20251120_101430. Include delivery metrics, top-performing formats, and recommendations.
```

**What to Highlight:**
- ✅ **Performance Summary**: Complete budget/spend overview, KPIs, channel breakdown
- ✅ **Daily Trends**: Day-by-day performance
- ✅ **Device Breakdown**: Performance by device type
- ✅ **Actionable Insights**: Recommendations based on data

**Expected Agent Flow:**
1. Calls `get_media_buy_report()` with 7-day timeframe
2. Presents report sections clearly
3. Provides recommendations
4. Offers next steps

**What to Say:**
> "This comprehensive report demonstrates the wrap-up vision: complete performance summaries with business outcomes, KPIs, and channel breakdowns. The agent can generate these reports instantly, replacing hours of manual work."

---

### **Part 6: Vision Alignment Summary (2 minutes)**

**What to Say:**
> "Let me summarize how this implementation aligns with Yahoo's vision:"

**Show Vision Mapping Table** (from `YAHOO_VISION_MAPPING.md`):

| Yahoo Vision | Status | Demo Shown |
|-------------|--------|------------|
| **Seamless Data Access** | ✅ | Natural language → instant results |
| **Proposal Data** | ✅ | Pricing, targeting, formats, forecasts |
| **Matched Audience** | ✅ | Clean Room audience overlap data |
| **Performance Summary** | ✅ | Complete KPIs, budget/spend, breakdowns |
| **Measurement & Analytics** | ⚠️ | Real-time metrics (BYOD/attribution coming) |
| **Continuous Optimization** | ⚠️ | Budget updates (automation coming) |

**What to Say:**
> "We've implemented 6 out of 10 vision items fully, with 4 partially implemented. The foundation is solid - seamless access, proposal data, matched audiences, and performance reporting all work today. The remaining features - automated recommendations, BYOD conversion data, and competitive insights - have clear technical paths forward."

---

## 🤖 Part 7: CEM Automation Workflow (5 minutes)

This section demonstrates Yahoo's **internal Campaign Escalation Manager (CEM) workflow** — the human-in-the-loop approval process that happens after AdCP creates a campaign.

> **Note:** This demo uses the **Slack App** (`adcp-slack-app`), not the Streamlit/CLI agent.

---

### **🟢 Happy Path: Validation Passes → CEM Approves**

**Demo Prompt (in Slack):**
```
Create a Nike Spring Running Q1 2026 campaign with:
- Product: yahoo_sports_display_enthusiasts
- Budget: $50,000
- Flight dates: January 15, 2026 to March 15, 2026
- Pacing: even
```

**What Happens:**

| Step | Action | Visual |
|------|--------|--------|
| 1️⃣ | Campaign created in Snowflake | ✅ Success message in Slack |
| 2️⃣ | CEM workflow triggered | 🔄 "Order submitted for CEM review" |
| 3️⃣ | SQL validation runs | ✅ All 6 checks pass |
| 4️⃣ | AI generates summary | 🤖 Claude analyzes order |
| 5️⃣ | Approval card posted | 📋 Card with buttons appears |
| 6️⃣ | CEM clicks **Approve** | ✅ Status → `active` |
| 7️⃣ | Audit logged | 📝 `cem_approved` in Snowflake |

**Expected Slack Card:**
```
🔔 New Order Pending CEM Approval
Order ID: nike_spring_running_q1_2026_xxxxx

📋 Order Summary
Nike (enterprise client) requesting $50,000 campaign...

✅ Validation Results
All 6 checks passed: product exists, budget within limits...

🤖 AI Recommendation
✅ APPROVE (Confidence: high)
🟢 Risk Level: low

[✅ Approve] [❌ Reject] [📝 Request Changes]
```

**What to Say:**
> "Notice how the system automatically validates the order against master tables — products, formats, budget limits, principal authorization. The AI then summarizes everything for the CEM in plain English, with a clear recommendation. The CEM can approve with one click, and the audit trail is automatically logged to Snowflake."

---

### **🔴 Sad Path: Validation Fails → CEM Rejects**

**Demo Prompt (in Slack):**
```
Create a Nike Summer Video campaign with:
- Product: yahoo_metaverse_ads
- Budget: $50,000
- Flight dates: January 15, 2026 to March 15, 2026
```

**What Happens:**

| Step | Action | Visual |
|------|--------|--------|
| 1️⃣ | Campaign created in Snowflake | ✅ Record created |
| 2️⃣ | CEM workflow triggered | 🔄 "Order submitted for CEM review" |
| 3️⃣ | SQL validation runs | ❌ `products_exist` fails |
| 4️⃣ | AI generates summary | 🤖 Claude identifies issue |
| 5️⃣ | Approval card posted | 📋 Card with REJECT recommendation |
| 6️⃣ | CEM clicks **Reject** | Modal opens for reason |
| 7️⃣ | CEM enters reason | "Product does not exist" |
| 8️⃣ | Rejection logged | 📝 `cem_rejected` in Snowflake |

**Expected Slack Card:**
```
🔔 New Order Pending CEM Approval
Order ID: nike_summer_video_xxxxx

📋 Order Summary
Nike requesting $50,000 campaign with invalid product...

❌ Validation Results
5/6 checks passed. FAILED: Product 'yahoo_metaverse_ads' 
does not exist in catalog.

⚠️ Risk Flags
• CRITICAL: Invalid product - does not exist in catalog
• Zero estimated impressions despite budget allocation

🤖 AI Recommendation
❌ REJECT (Confidence: high)
🔴 Risk Level: high

The order must be rejected because the specified product 
does not exist in Yahoo's product catalog...

[✅ Approve] [❌ Reject] [📝 Request Changes]
```

**What to Say:**
> "Here we see the system catching an error — the product doesn't exist in our catalog. The AI clearly explains why this should be rejected, and the CEM can reject with a documented reason. This ensures no invalid orders slip through, and every decision is audited."

---

### **🟡 Review Path: Passes Validation but Needs Scrutiny**

**Demo Prompt (in Slack):**
```
Create an Acme Partners Q1 Blitz campaign with:
- Product: yahoo_sports_display_enthusiasts
- Budget: $750,000
- Flight dates: January 2, 2026 to January 5, 2026
```

**What Happens:**
- All validations pass ✅
- AI flags risk: **High budget ($750K) for very short flight (3 days)**
- Recommendation: **REVIEW** (not approve or reject)
- CEM clicks **Request Changes** and provides feedback

**What to Say:**
> "This is where AI really shines. The order passes all technical validations, but the AI recognizes something unusual — $750K budget for just 3 days. Instead of auto-approving, it recommends human review. The CEM can request changes with specific feedback, creating a collaborative workflow."

---

### **CEM Workflow Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│  AdCP PROTOCOL (create_media_buy)                               │
│  ─────────────────────────────────────────────────────────────  │
│  Campaign created in Snowflake → Success                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼ HANDOFF
┌─────────────────────────────────────────────────────────────────┐
│  YAHOO INTERNAL CEM WORKFLOW                                    │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │ SQL         │ → │ AI          │ → │ Slack       │           │
│  │ Validation  │   │ Summary     │   │ Card        │           │
│  └─────────────┘   └─────────────┘   └──────┬──────┘           │
│                                             │                   │
│                    ┌────────────────────────┼────────────────┐  │
│                    │                        │                │  │
│                    ▼                        ▼                ▼  │
│             [✅ Approve]            [❌ Reject]      [📝 Review] │
│                    │                        │                │  │
│                    ▼                        ▼                ▼  │
│            status=active           status=rejected   status=    │
│            audit_log ✅            audit_log ✅     pending     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### **Valid Product IDs for Demo**

| Product ID | Type | Min Budget |
|------------|------|------------|
| `yahoo_sports_display_enthusiasts` | Display | $8,000 |
| `yahoo_sports_video_preroll` | Video | $15,000 |
| `yahoo_sports_native` | Native | $8,000 |
| `yahoo_finance_display_premium` | Display | $10,000 |
| `yahoo_finance_ctv_video` | CTV | $25,000 |

---

## 🎯 Key Talking Points

### **1. Seamless Access**
- "Natural language eliminates the need for API knowledge"
- "MCP protocol enables any AI to access Yahoo data"
- "Data Cloud Zero Copy provides instant, real-time access"

### **2. Proposal Data**
- "Complete proposals with pricing, targeting, formats, and forecasts"
- "Enterprise discounts automatically applied"
- "AdCP v2.3.0 compliant package structure"

### **3. Matched Audience**
- "Clean Room audience overlap integrated into every product"
- "Demographics, engagement scores, privacy-preserving"
- "850K matched users example shown in discovery"

### **4. Performance Reporting**
- "Real-time metrics via Data Cloud"
- "Complete KPIs: CTR, CVR, CPM, CPC, CPA"
- "Pacing analysis and device breakdowns"

### **5. Agentic Experience**
- "Conversational, intelligent, context-aware"
- "Multi-step workflows handled automatically"
- "Confirms before making changes"

---

## 🚨 Troubleshooting During Demo

### **If Agent Doesn't Respond:**
1. Check terminal for error messages
2. Verify MCP server is accessible: `curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json`
3. Try simpler prompt: "Show me advertising options for Nike"

### **If Tool Call Fails:**
1. Check Heroku logs: `heroku logs --tail -a yahoo-mcp-server`
2. Use backup: Show HTTP client example
3. Explain: "This is a demo environment, production would have better error handling"

### **If Format Validation Fails:**
1. Agent should call `list_creative_formats()` first
2. If it doesn't, manually show format list
3. Explain: "Agent learns from errors and improves"

### **If Campaign Creation Fails:**
1. Check if campaign ID already exists
2. Try different campaign name
3. Show the error handling: "Agent explains what went wrong"

---

## 📝 Backup Prompts (If Primary Ones Fail)

### **Simple Discovery:**
```
Show me advertising options for Nike
```

### **Simple Campaign:**
```
Create a $25,000 campaign for Nike running shoes using Yahoo Sports
```

### **Simple Performance:**
```
Show me campaign performance
```

---

## 🎬 Closing Statement

**What to Say:**
> "This demonstration shows how we've brought Yahoo's vision to life. The agentic experience makes advertising campaign management conversational and intelligent. The foundation is production-ready, and we have clear technical paths for the remaining features. 

> The key differentiator is the seamless access - natural language conversations that eliminate the complexity of traditional APIs. This is what makes Yahoo data accessible to more advertisers, exactly as envisioned.

> Questions?"

---

## 📊 Success Metrics

**Demo is successful if:**
- ✅ Agent responds to all prompts within 5 seconds
- ✅ Campaign creation completes successfully
- ✅ Performance data displays correctly
- ✅ Yahoo stakeholders understand the vision alignment
- ✅ Clear path forward for remaining features

---

## 🔄 Post-Demo Follow-Up

**Send after demo:**
1. `YAHOO_VISION_MAPPING.md` - Complete vision alignment
2. `TECHNOLOGY_BUSINESS_VISION.md` - Technical architecture
3. `AGENTIC_EXPERIENCE_GUIDE.md` - Full prompt library
4. Demo recording (if recorded)

---

**Good luck with your demo! 🚀**

