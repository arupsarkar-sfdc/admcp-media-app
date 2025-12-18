# Yahoo Demo Script - December 2025

**Purpose**: Comprehensive demo showcasing AdCP + Slack CEM integration  
**Duration**: 20-30 minutes  
**Audience**: Yahoo stakeholders, agency partners

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        DEMO ARCHITECTURE                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │
│  │  AGENCY     │     │  YAHOO      │     │  YAHOO      │                │
│  │  SIDE       │     │  AdCP       │     │  INTERNAL   │                │
│  │             │     │  SERVER     │     │  (CEM)      │                │
│  │ Streamlit   │ ──▶ │ MCP Server  │ ──▶ │ Slack Bot   │                │
│  │ Campaign    │     │ (Heroku)    │     │ (Heroku)    │                │
│  │ Planner     │     │             │     │             │                │
│  └─────────────┘     └─────────────┘     └─────────────┘                │
│        │                   │                   │                         │
│        │                   ▼                   ▼                         │
│        │             ┌─────────────┐     ┌─────────────┐                │
│        │             │ Snowflake   │◀───▶│ Data Cloud  │                │
│        │             │ (Write)     │     │ (Read)      │                │
│        │             └─────────────┘     └─────────────┘                │
│        │                                                                 │
│        ▼                                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  DEMO FLOW                                                       │    │
│  │  1. Agency creates campaign (Streamlit)                          │    │
│  │  2. AdCP validates and writes to Snowflake                       │    │
│  │  3. Webhook notifies Slack CEM bot                               │    │
│  │  4. CEM reviews, approves/rejects in Slack                       │    │
│  │  5. Audit trail logged to Snowflake                              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Demo Objectives

| Objective | How We Show It |
|-----------|----------------|
| **Seamless Data Access** | Natural language → instant results |
| **AdCP Protocol Compliance** | MCP server with 9 AdCP tools |
| **Human-in-the-Loop** | CEM approval workflow in Slack |
| **AI-Powered Validation** | SQL checks + Claude summarization |
| **Enterprise Scale** | 100 CEMs, visibility rules, channels |
| **Audit Trail** | Every action logged to Snowflake |

---

## 📋 Pre-Demo Checklist

### **30 Minutes Before**

```bash
# 1. Verify MCP server
curl https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/.well-known/adagents.json

# 2. Verify Slack bot (check Heroku logs)
heroku logs --tail -a adcp-slack-app

# 3. Set environment
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/yahoo_mcp_server
export ANTHROPIC_API_KEY=your_key

# 4. Test Streamlit locally
uv run python -m streamlit run streamlit_app.py

# 5. Scale Heroku for Slack (if testing against Heroku)
heroku ps:scale web=1 -a adcp-slack-app
```

### **Verify Demo Data**

| Check | Command |
|-------|---------|
| Products exist | `SELECT * FROM products WHERE is_active = true` |
| Principals exist | `SELECT * FROM principals` |
| Audit log empty | `DELETE FROM cem_audit_log WHERE created_at < NOW()` |

---

## 🎬 Demo Flow

### **Part 1: Introduction (2 minutes)**

**What to Say:**
> "Today I'll demonstrate the complete advertising workflow — from agency campaign creation to Yahoo CEM approval. You'll see two interfaces working together: a Streamlit app for agencies and a Slack bot for internal approval workflows."

**Key Points:**
- AdCP protocol for standardized campaign management
- Slack integration for human-in-the-loop
- AI summarization for faster decisions
- Full audit trail in Snowflake

---

### **Part 2: Product Discovery (3 minutes)**

**Demo in Streamlit:**
```
Show me advertising options for Nike running shoes with a budget of $50,000
```

**What to Highlight:**
- Natural language understanding
- Product recommendations with pricing
- Enterprise discounts applied
- Audience overlap data

---

### **Part 3: Campaign Creation → CEM Workflow (10 minutes)**

This is the core demo. We show the complete flow from agency to CEM approval.

---

## ✅ HAPPY PATH DEMOS

### **Happy Path 1: Standard Campaign**

**Prompt (Streamlit or Slack):**
```
Create a Nike Spring Running Q1 2026 campaign with:
- Product: yahoo_sports_display_enthusiasts
- Budget: $50,000
- Flight dates: January 15, 2026 to March 15, 2026
- Pacing: even
```

**Expected Flow:**

| Step | What Happens | Where |
|------|--------------|-------|
| 1 | Campaign created | Snowflake |
| 2 | Webhook fired | Streamlit → Slack |
| 3 | Validation runs | 6 SQL checks pass |
| 4 | AI summarizes | Claude generates card |
| 5 | CEM sees approval card | Slack |
| 6 | CEM clicks Approve | Slack |
| 7 | Status → `active` | Snowflake |
| 8 | Audit logged | `cem_approved` |

**Expected Slack Card:**
```
┌──────────────────────────────────────────────────────────────┐
│ 📋 CEM REVIEW REQUIRED                                       │
├──────────────────────────────────────────────────────────────┤
│ Campaign: Nike Spring Running Q1 2026                        │
│ Budget: $50,000.00                                           │
│ Client: Nike Global                                          │
│ Flight: Jan 15, 2026 → Mar 15, 2026                          │
├──────────────────────────────────────────────────────────────┤
│ ✅ ALL VALIDATIONS PASSED (6/6)                              │
│                                                              │
│ 🤖 AI Recommendation: APPROVE                                │
│ Confidence: HIGH                                             │
│ Risk Level: LOW                                              │
│                                                              │
│ [✅ Approve] [❌ Reject] [📝 Request Changes]                │
└──────────────────────────────────────────────────────────────┘
```

**What to Say:**
> "Notice how the system automatically validates against our product catalog, budget limits, and principal authorization. The AI summarizes everything in plain English. One click to approve, and the audit trail is complete."

---

### **Happy Path 2: Sports Video Pre-roll**

```
Create a Nike Marathon Training campaign with:
- Product: yahoo_sports_video_preroll
- Budget: $125,000
- Flight dates: February 1, 2026 to April 30, 2026
- Pacing: front_loaded
```

**Why it passes:** Valid product, reasonable budget, future dates

---

### **Happy Path 3: Finance Premium Display**

```
Create a Nike Investor Relations Q2 campaign with:
- Product: yahoo_finance_display_premium
- Budget: $75,000
- Flight dates: April 1, 2026 to June 30, 2026
- Pacing: even
```

**Why it passes:** Different product vertical, still valid

---

### **Happy Path 4: CTV Video (High Budget)**

```
Create a Nike Olympics Summer 2026 campaign with:
- Product: yahoo_finance_ctv_video
- Budget: $500,000
- Flight dates: July 1, 2026 to August 15, 2026
- Pacing: back_loaded
```

**Why it passes:** High budget but within limits, valid product

---

### **Happy Path 5: Native Content**

```
Create a Nike Lifestyle Stories campaign with:
- Product: yahoo_sports_native
- Budget: $35,000
- Flight dates: March 1, 2026 to May 31, 2026
- Pacing: even
```

---

### **Happy Path 6: Natural Language (Unstructured)**

```
I need a $200K Nike Back to School campaign running August through September 2026 on Yahoo Sports Video
```

**What to Say:**
> "The AI understands natural language — no structured format required. It extracts product, budget, dates, and creates the campaign."

---

## ❌ SAD PATH DEMOS

### **Sad Path 1: Invalid Product (Meta Ads)**

```
Create a Nike Summer Running Q2 2026 campaign with:
- Product: yahoo_meta_ads_sports_display
- Budget: $50,000
- Flight dates: March 15, 2026 to June 14, 2026
- Pacing: even
```

**Why it fails:** `yahoo_meta_ads_sports_display` doesn't exist

**Expected Slack Card:**
```
┌──────────────────────────────────────────────────────────────┐
│ ⚠️ CEM REVIEW REQUIRED - VALIDATION ISSUES                   │
├──────────────────────────────────────────────────────────────┤
│ Campaign: Nike Summer Running Q2 2026                        │
│ Budget: $50,000.00                                           │
├──────────────────────────────────────────────────────────────┤
│ ❌ VALIDATION FAILED: products_exist                         │
│                                                              │
│ Invalid products: yahoo_meta_ads_sports_display              │
│                                                              │
│ 🤖 AI Recommendation: REJECT                                 │
│ Reason: Product not in Yahoo inventory                       │
│ Risk Level: HIGH                                             │
│                                                              │
│ [✅ Approve] [❌ Reject] [📝 Request Changes]                │
└──────────────────────────────────────────────────────────────┘
```

**What to Say:**
> "The system catches the error — this product doesn't exist in our catalog. The CEM sees exactly why it failed and can reject with one click."

---

### **Sad Path 2: Invalid Product (TikTok)**

```
Create a Nike Gen Z campaign with:
- Product: yahoo_tiktok_video
- Budget: $100,000
- Flight dates: May 1, 2026 to July 31, 2026
- Pacing: even
```

**Why it fails:** Yahoo doesn't sell TikTok inventory

---

### **Sad Path 3: Invalid Product (Competitor)**

```
Create a Nike Holiday campaign with:
- Product: google_youtube_masthead
- Budget: $250,000
- Flight dates: November 15, 2026 to December 31, 2026
- Pacing: back_loaded
```

**Why it fails:** This is a Google product, not Yahoo

---

### **Sad Path 4: Budget Too Low**

```
Create a Nike Test campaign with:
- Product: yahoo_sports_display_enthusiasts
- Budget: $500
- Flight dates: January 1, 2026 to January 31, 2026
- Pacing: even
```

**Why it fails:** Below $10,000 minimum

---

### **Sad Path 5: Budget Too High**

```
Create a Nike Global Domination campaign with:
- Product: yahoo_sports_video_preroll
- Budget: $50,000,000
- Flight dates: January 1, 2026 to December 31, 2026
- Pacing: even
```

**Why it fails:** Exceeds $10M maximum

---

### **Sad Path 6: Unauthorized Principal**

```
Create a Puma Running campaign with:
- Product: yahoo_sports_display_enthusiasts
- Budget: $75,000
- Flight dates: April 1, 2026 to June 30, 2026
- Pacing: even
```

**Why it fails:** Puma not in authorized principals list

---

### **Sad Path 7: Flight Dates in Past**

```
Create a Nike Retro campaign with:
- Product: yahoo_sports_native
- Budget: $50,000
- Flight dates: January 1, 2020 to March 31, 2020
- Pacing: even
```

**Why it fails:** Dates are in the past

---

### **Sad Path 8: End Date Before Start**

```
Create a Nike Confused campaign with:
- Product: yahoo_sports_display_enthusiasts
- Budget: $50,000
- Flight dates: December 31, 2026 to January 1, 2026
- Pacing: even
```

**Why it fails:** End date before start date

---

### **Sad Path 9: Multiple Failures**

```
Create a Nike Disaster campaign with:
- Product: yahoo_instagram_stories
- Budget: $999
- Flight dates: June 1, 2026 to June 30, 2026
- Pacing: even
```

**Why it fails:** Invalid product AND budget too low

---

## 🔍 REVIEW PATH DEMOS

### **Review 1: High Budget Needs Scrutiny**

```
Create a Nike Superbowl 2026 campaign with:
- Product: yahoo_sports_video_preroll
- Budget: $2,500,000
- Flight dates: February 1, 2026 to February 15, 2026
- Pacing: front_loaded
```

**Why it triggers REVIEW:**
- Very high budget ($2.5M)
- Very short flight (2 weeks)
- High daily spend rate (~$179K/day)

**AI Recommendation:** REVIEW (not approve or reject)

**What to Say:**
> "This passes all technical validations, but the AI flags unusual patterns — $2.5M for just 2 weeks. It recommends human review rather than auto-approving."

---

### **Review 2: Aggressive Pacing**

```
Create a Nike Flash Sale campaign with:
- Product: yahoo_sports_display_enthusiasts
- Budget: $500,000
- Flight dates: January 15, 2026 to January 22, 2026
- Pacing: front_loaded
```

**Why it triggers REVIEW:**
- 7-day flight with $500K = $71K/day spend
- Front-loaded pacing = even more aggressive start

---

## 📊 Reference Tables

### **Valid Products**

| Product ID | Type | Min Budget |
|------------|------|------------|
| `yahoo_sports_display_enthusiasts` | Display | $8,000 |
| `yahoo_sports_video_preroll` | Video | $15,000 |
| `yahoo_sports_native` | Native | $8,000 |
| `yahoo_finance_display_premium` | Display | $10,000 |
| `yahoo_finance_ctv_video` | CTV | $25,000 |

### **Valid Formats**

| Format ID | Type |
|-----------|------|
| `display_300x250` | Display |
| `display_728x90` | Display |
| `display_160x600` | Display |
| `display_320x50` | Mobile |
| `video_16x9_15s` | Video 15s |
| `video_16x9_30s` | Video 30s |
| `video_9x16_15s` | Vertical |
| `native_content_feed` | Native |
| `native_in_stream` | Native |

### **Valid Principals**

| Principal ID | Name |
|--------------|------|
| `nike_global` | Nike Global |
| `nike_na` | Nike North America |

### **Budget Limits**

| Limit | Value |
|-------|-------|
| Minimum | $10,000 |
| Maximum | $10,000,000 |

---

## 🎯 Quick Demo Commands

### **For Video Recording (Copy-Paste Ready)**

```
# Happy Path - Quick
Create a Nike Spring Running campaign with yahoo_sports_display_enthusiasts, $50K budget, Jan-Mar 2026

# Sad Path - Bad Product
Create a Nike Summer campaign with yahoo_tiktok_video, $100K budget, Jun-Aug 2026

# Sad Path - Unauthorized Client
Create a Puma Fall campaign with yahoo_sports_display_enthusiasts, $75K budget, Sep-Nov 2026

# Review Path - High Risk
Create a Nike Superbowl campaign with yahoo_sports_video_preroll, $2.5M budget, Feb 1-15 2026
```

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Slack not responding | Check `heroku logs --tail -a adcp-slack-app` |
| MCP server down | Check `heroku ps -a yahoo-mcp-server` |
| Validation always passes | Verify Snowflake connection in validators.py |
| Webhook not firing | Check `CEM_WEBHOOK_URL` in Streamlit env |
| Duplicate campaigns | Campaign IDs are timestamped, shouldn't conflict |

---

## 🎬 Closing Statement

**What to Say:**
> "You've seen the complete workflow — from agency campaign creation through CEM approval. The key innovations are:
> 
> 1. **AdCP Protocol** - Standardized, open protocol for advertising
> 2. **AI Validation** - SQL checks + Claude summarization
> 3. **Human-in-the-Loop** - CEM approval in Slack
> 4. **Full Audit Trail** - Every action logged to Snowflake
> 
> This is what agentic advertising looks like — intelligent, conversational, and compliant."

---

## 📝 Post-Demo Follow-Up

**Send to stakeholders:**
1. `YAHOO_VISION_MAPPING.md` — Vision alignment
2. `yahoo_mcp_server/slack/README.md` — Slack architecture
3. `yahoo_mcp_server/automation/README.md` — CEM workflow details
4. Demo recording (if recorded)

---

**Good luck with your demo! 🚀**
