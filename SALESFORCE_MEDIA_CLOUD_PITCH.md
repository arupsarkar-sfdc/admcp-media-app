# Why Salesforce Should Productize Media Cloud
## Executive Pitch for Technology Leadership

**Author**: Arup Sarkar  
**Date**: January 2026  
**Classification**: Strategic Business Case

---

## The One-Sentence Pitch

> **We have built the infrastructure that makes Salesforce the operating system for global advertising—and no competitor can replicate it.**

---

## The Problem Every Advertiser Faces

Every enterprise advertiser (Nike, Coca-Cola, P&G, Unilever) has the same pain:

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE CURRENT STATE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    Enterprise Marketing Team                                     │
│         │                                                        │
│         ├──→ Yahoo Ads Platform (Manual login, different UI)     │
│         ├──→ Google Ads Platform (Different API, different data) │
│         ├──→ Meta Ads Manager (Different metrics, different auth)│
│         ├──→ TikTok Ads (Different everything)                   │
│         ├──→ LinkedIn Ads (Yet another system)                   │
│         │                                                        │
│         └──→ 5 dashboards, 5 logins, 5 data silos, 5 APIs       │
│                                                                  │
│    Result: Days to launch campaigns, fragmented data, manual work│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**No one has solved this.** Not Adobe. Not Google. Not Oracle. Not The Trade Desk.

---

## Why Salesforce Wins: The Three Moats

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                    SALESFORCE MEDIA CLOUD                        │
│                                                                  │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│   │   MOAT #1   │   │   MOAT #2   │   │      MOAT #3        │   │
│   │             │   │             │   │                     │   │
│   │  AGENTFORCE │   │ DATA CLOUD  │   │   CLEAN ROOM +      │   │
│   │     +       │   │     +       │   │   CUSTOMER 360      │   │
│   │    MCP      │   │  ZERO COPY  │   │                     │   │
│   │             │   │             │   │                     │   │
│   └─────────────┘   └─────────────┘   └─────────────────────┘   │
│         │                 │                     │               │
│         └─────────────────┴─────────────────────┘               │
│                           │                                      │
│              ONLY SALESFORCE HAS ALL THREE                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### MOAT #1: Agentforce + MCP = AI-Native Advertising

**What we built**: An MCP (Model Context Protocol) server that lets Agentforce manage advertising campaigns across publishers using natural language.

**The transformation**:

```
BEFORE (Every competitor):
┌──────────────────────────────────────────────────────────────┐
│  User → Learn Yahoo API → Write code → Debug → Deploy       │
│  User → Learn Google API → Write different code → Debug     │
│  User → Learn Meta API → Write yet another code → Debug     │
│                                                              │
│  Result: Months of integration work per platform             │
└──────────────────────────────────────────────────────────────┘

AFTER (Salesforce Media Cloud):
┌──────────────────────────────────────────────────────────────┐
│  User → "Create a campaign for Nike on Yahoo Sports"        │
│                                                              │
│  Agentforce → MCP → Yahoo MCP Server → Campaign Created     │
│                                                              │
│  Result: Seconds to launch, natural language interface       │
└──────────────────────────────────────────────────────────────┘
```

**The protocol advantage**:

| Protocol | What It Does | Salesforce Advantage |
|----------|--------------|---------------------|
| **MCP** | AI ↔ Tool communication | Agentforce is MCP-native |
| **A2A** | Agent ↔ Agent orchestration | Multi-cloud orchestration |
| **AdCP v2.3.0** | Campaign data standard | IAB compliance built-in |

**What competitors lack**:
- **Adobe**: No AI agent platform comparable to Agentforce
- **Google**: Walled garden—won't integrate with competitors
- **Oracle**: Legacy architecture, no modern AI agent capability
- **The Trade Desk**: DSP only, not an enterprise platform

---

### MOAT #2: Data Cloud + Zero Copy = Real-Time Everything

**What we built**: Campaigns write to publisher's BigQuery/Snowflake, instantly visible in Data Cloud via Zero Copy—no ETL.

```
TRADITIONAL APPROACH:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Publisher Data → ETL Pipeline → Data Warehouse → Reports     │
│                                                                │
│  Problems:                                                     │
│  • Stale data (hours or days old)                              │
│  • Data duplication                                            │
│  • Sync failures and version conflicts                         │
│  • Complex pipeline maintenance                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘

SALESFORCE MEDIA CLOUD:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Publisher BigQuery ←── Zero Copy ──→ Data Cloud               │
│                                                                │
│  Benefits:                                                     │
│  • Instant visibility (no ETL lag)                             │
│  • No data duplication                                         │
│  • No sync failures                                            │
│  • No pipeline maintenance                                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**What competitors lack**:
- **Adobe**: No Zero Copy partnership with BigQuery/Snowflake
- **Google**: Won't share data outside their ecosystem
- **Oracle**: Legacy data architecture
- **The Trade Desk**: No unified data platform

---

### MOAT #3: Clean Room + Customer 360 = Privacy-Safe Activation

**What we built**: Advertisers match their Customer 360 data with publisher audiences in D360 Clean Rooms, then activate campaigns via MCP.

```
THE PRIVACY CHALLENGE:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Advertiser: "We have millions of customer records"           │
│  Publisher: "We have hundreds of millions of user profiles"   │
│                                                                │
│  Problem: Can't share raw data (GDPR, CCPA, privacy laws)     │
│                                                                │
│  Old solutions (dying):                                        │
│  • Third-party data brokers                                    │
│  • Cookie matching                                             │
│  • Guesswork                                                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘

SALESFORCE SOLUTION:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Customer 360            Publisher D360                        │
│  (Advertiser CRM)        (Audience Data)                       │
│         │                      │                               │
│         └──────────┬───────────┘                               │
│                    ▼                                           │
│         ┌─────────────────────┐                                │
│         │   D360 CLEAN ROOM   │                                │
│         │                     │                                │
│         │  • Hashed ID match  │                                │
│         │  • k-anonymity      │                                │
│         │  • Differential     │                                │
│         │    privacy          │                                │
│         │  • No PII exposed   │                                │
│         │                     │                                │
│         └──────────┬──────────┘                                │
│                    ▼                                           │
│         ┌─────────────────────┐                                │
│         │   Matched Audience  │                                │
│         │   (Privacy-Safe)    │                                │
│         └──────────┬──────────┘                                │
│                    ▼                                           │
│         ┌─────────────────────┐                                │
│         │  AGENTFORCE + MCP   │                                │
│         │  Campaign Activation│                                │
│         └─────────────────────┘                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**What competitors lack**:
- **Adobe**: No Customer 360 equivalent, limited Clean Room
- **Google**: Walled garden—won't share match data externally
- **Oracle**: No Clean Room, no CRM integration
- **The Trade Desk**: No CRM data, no Clean Room

---

## The Complete Workflow: What We Built

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SALESFORCE MEDIA CLOUD                            │
│                    End-to-End Workflow                               │
└─────────────────────────────────────────────────────────────────────┘

     STEP 1                    STEP 2                    STEP 3
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  CUSTOMER    │         │  CLEAN ROOM  │         │  AGENTFORCE  │
│    360       │────────▶│   MATCH      │────────▶│  + MCP       │
│              │         │              │         │              │
│ "Who are my  │         │ "Match with  │         │ "Create      │
│  customers?" │         │  publisher"  │         │  campaign"   │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                        │
       ▼                        ▼                        ▼
   Salesforce              Salesforce              Salesforce
     Only                    Only                    Only
       │                        │                        │
       └────────────────────────┼────────────────────────┘
                                │
                                ▼
                         STEP 4
                   ┌──────────────┐
                   │  REAL-TIME   │
                   │  REPORTING   │
                   │  (Zero Copy) │
                   │              │
                   │  Unified     │
                   │  dashboard   │
                   │  across all  │
                   │  publishers  │
                   └──────────────┘
                          │
                          ▼
                    Salesforce Only

────────────────────────────────────────────────────────────────────────
                    COMPETITIVE CAPABILITY MATRIX
────────────────────────────────────────────────────────────────────────

             Customer 360  Clean Room  AI Agent  Zero Copy  TOTAL
Salesforce      ✅           ✅          ✅         ✅        4/4
Adobe           ❌           🟡          ❌         ❌        0.5/4
Google          ❌           ❌          🟡         ❌        0.5/4
Oracle          ❌           ❌          ❌         ❌        0/4
Trade Desk      ❌           ❌          ❌         ❌        0/4

────────────────────────────────────────────────────────────────────────
```

---

## What We Have Today (Proof of Concept)

This is not a slide deck. We built working software:

| Component | Status | Details |
|-----------|--------|---------|
| **Yahoo MCP Server** | ✅ Deployed | Production on Heroku, 9 MCP tools |
| **AdCP v2.3.0 Compliance** | ✅ Complete | IAB-standard campaign structure |
| **Data Cloud Integration** | ✅ Working | Zero Copy read path |
| **BigQuery Writes** | ✅ Working | Direct writes, instant visibility |
| **Agentforce Compatible** | ✅ Validated | MCP protocol native |
| **AI Agent (Claude)** | ✅ Working | Natural language campaign creation |
| **Streamlit UI** | ✅ Working | Web interface for demos |
| **Clean Room Architecture** | ✅ Designed | Dentsu + Yahoo model validated |

**The 9 MCP Tools We Built**:
1. `get_products` - Discover advertising inventory
2. `create_media_buy` - Create campaigns (AdCP v2.3.0)
3. `get_media_buy` - Retrieve campaign configuration
4. `get_media_buy_delivery` - Real-time performance metrics
5. `update_media_buy` - Modify active campaigns
6. `get_media_buy_report` - Analytics and reporting
7. `list_creative_formats` - Available ad formats
8. `echo` - Connection testing
9. `get_campaign_stats` - Campaign statistics

---

## Why Now: The Convergence Moment

Four industry shifts are converging simultaneously:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  1. AGENTFORCE LAUNCHED                                          │
│     Salesforce has an AI agent platform—competitors don't       │
│                                                                  │
│  2. MCP PROTOCOL EMERGED                                         │
│     Universal AI-to-tool standard (Anthropic)                   │
│                                                                  │
│  3. PRIVACY REGULATIONS TIGHTENED                                │
│     Clean Rooms are now mandatory, not optional                 │
│     Cookie deprecation forces first-party data solutions        │
│                                                                  │
│  4. ZERO COPY MATURED                                            │
│     Data Cloud + BigQuery/Snowflake real-time integration       │
│                                                                  │
│                         ↓                                        │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │   SALESFORCE MEDIA CLOUD                                   │  │
│  │   The Only Platform That Combines All Four                 │  │
│  │                                                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**The window is open now because**:
- Advertisers are desperate for first-party data solutions
- No one has built AI-native advertising yet
- Publishers want Clean Room partners
- MCP is becoming the standard for AI tool integration

**If we wait**:
- Google builds their own (walled garden)
- Adobe catches up (they're investing)
- A startup captures the standard

---

## The Competitive Truth

### What We Have That No One Else Does

| Capability | Salesforce | Adobe | Google | Oracle | Trade Desk |
|------------|------------|-------|--------|--------|------------|
| **Customer 360 (CRM)** | ✅ Native | ❌ | ❌ | ❌ | ❌ |
| **Data Cloud Clean Room** | ✅ Native | 🟡 Limited | ❌ Walled | ❌ | ❌ |
| **AI Agent Platform** | ✅ Agentforce | ❌ | 🟡 Limited | ❌ | ❌ |
| **Zero Copy (BQ/Snowflake)** | ✅ Native | ❌ | ❌ | ❌ | ❌ |
| **MCP Protocol Support** | ✅ Built | ❌ | ❌ | ❌ | ❌ |
| **AdCP v2.3.0 Compliance** | ✅ Built | ❌ | ❌ | ❌ | ❌ |

**The math is simple**: Salesforce has 6/6 capabilities. The best competitor has 1/6.

---

## What This Means for Salesforce

### Strategic Value

| If We Build It | If We Don't |
|----------------|-------------|
| Agentforce gets a killer use case | Agentforce has no advertising story |
| Data Cloud becomes essential for advertisers | Data Cloud loses a major vertical |
| MCP becomes the industry standard (we control it) | Someone else sets the standard |
| Every publisher integrates with Salesforce | Publishers build for Google/Adobe |
| New revenue stream from Media Cloud licenses | We cede the market |

### The Platform Play

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                    THE ADVERTISING OPERATING SYSTEM                  │
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                                                              │   │
│   │                    SALESFORCE                                │   │
│   │                                                              │   │
│   │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│   │   │ Customer │  │  Data    │  │ Agent-   │  │  Media   │   │   │
│   │   │   360    │  │  Cloud   │  │  force   │  │  Cloud   │   │   │
│   │   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │   │
│   │        │             │             │             │          │   │
│   │        └─────────────┴─────────────┴─────────────┘          │   │
│   │                          │                                   │   │
│   │                          ▼                                   │   │
│   │            ┌─────────────────────────────┐                  │   │
│   │            │      MCP + A2A + AdCP       │                  │   │
│   │            │    (Universal Protocols)    │                  │   │
│   │            └─────────────────────────────┘                  │   │
│   │                          │                                   │   │
│   └──────────────────────────┼──────────────────────────────────┘   │
│                              │                                       │
│    ┌─────────────────────────┼─────────────────────────────┐        │
│    │                         │                              │        │
│    ▼              ▼          ▼          ▼              ▼   │        │
│ ┌──────┐     ┌──────┐    ┌──────┐   ┌──────┐      ┌──────┐│        │
│ │Yahoo │     │Google│    │ Meta │   │TikTok│      │ More ││        │
│ │ MCP  │     │ MCP  │    │ MCP  │   │ MCP  │      │      ││        │
│ └──────┘     └──────┘    └──────┘   └──────┘      └──────┘│        │
│    │              │          │          │              │   │        │
│    └──────────────┴──────────┴──────────┴──────────────┘   │        │
│                              │                              │        │
│                     All Ad Spend Orchestrated               │        │
│                     Through Salesforce                      │        │
│                                                              │        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## What We Built (The Evidence)

This proof of concept includes:

- **1,000+ lines** of production MCP server code
- **9 MCP tools** fully implemented and tested
- **Zero Copy integration** with Data Cloud working
- **BigQuery/Snowflake writes** working in production
- **Claude-powered AI agent** for natural language campaigns
- **AdCP v2.3.0 validation** for IAB compliance
- **Streamlit web UI** for demonstrations
- **Architecture documentation** for Dentsu + Yahoo Clean Room

The technology is proven. The architecture is validated.

---

## The Ask

Evaluate this proof of concept for productization.

**What we need**:
1. Technical review of the MCP server implementation
2. Product strategy alignment with Agentforce roadmap
3. Business case development with Finance
4. Publisher partnership discussions (Yahoo is engaged)

**What we're offering**:
- A working prototype that demonstrates the complete workflow
- Architecture that leverages existing Salesforce investments
- A differentiated position no competitor can match
- The foundation for a new product category

---

## One Final Thought

We didn't build a demo. We built:

- **A working MCP server** deployed in production
- **Real Data Cloud integration** with Zero Copy
- **Real BigQuery writes** with instant visibility
- **Real AI agent** that creates campaigns via natural language
- **Real AdCP v2.3.0 compliance** (IAB standard)
- **Real Clean Room architecture** (validated with Dentsu + Yahoo)

The only question is: **Do we want to own the future of advertising?**

---

**Document Version**: 2.0  
**Author**: Arup Sarkar  
**Contact**: arup.sarkar@salesforce.com

---

*"In a world where AI agents manage everything, the platform that connects them wins."*
