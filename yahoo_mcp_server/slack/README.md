# Slack MCP Client for Yahoo Advertising

## The Problem We're Solving

Media buyers spend too much time switching between tools.

Picture this: You're a campaign manager at Nike. You need to launch a Q1 campaign for running shoes. Today, that means logging into Yahoo's ad platform, searching inventory, exporting to a spreadsheet, cross-referencing with your CRM data, emailing your Yahoo rep, waiting for a proposal, going back and forth on targeting, and finally—maybe a week later—your campaign goes live.

That workflow is broken. Not because the people are slow, but because the tools don't talk to each other.

**What if you could just ask?**

> "Hey, show me Yahoo's sports video inventory for Nike runners. Budget is $50K for Q1."

And get an answer. Right there in Slack. Where your team already works.

That's what this does.

---

## What This Is

A Slack bot that connects your team directly to Yahoo's advertising platform using:

- **Claude AI** for natural language understanding
- **MCP (Model Context Protocol)** for standardized tool calling
- **Salesforce Data Cloud** for real-time campaign data
- **Snowflake** as the source of truth

No new logins. No context switching. Just ask questions in Slack and get answers.

---

## How It Works

When someone sends a message to the bot, here's what happens behind the scenes:

```mermaid
flowchart TB
    subgraph SLACK ["💬 SLACK"]
        USER["User sends message"]
        RESPONSE["User sees response"]
    end

    subgraph BOT ["🤖 SLACK BOT (Heroku)"]
        BOLT["Slack Bolt\nEvent Handler"]
        AGENT["Claude AI Agent\nNatural Language → Tool Calls"]
        MCP_CLIENT["MCP Client\nTool Execution"]
    end

    subgraph YAHOO ["🎯 YAHOO MCP SERVER (Heroku)"]
        MCP_SERVER["MCP Server\n9 AdCP Tools"]
    end

    subgraph DATA ["💾 DATA LAYER"]
        DC["Salesforce\nData Cloud\n─────────\nREAD Path\nQuery API"]
        SF["Snowflake\n─────────\nWRITE Path\nDirect Insert"]
    end

    USER --> BOLT
    BOLT --> AGENT
    AGENT --> MCP_CLIENT
    MCP_CLIENT --> MCP_SERVER
    
    MCP_SERVER -->|"Query"| DC
    MCP_SERVER -->|"Insert/Update"| SF
    DC <-->|"Zero Copy"| SF
    
    SF --> MCP_SERVER
    DC --> MCP_SERVER
    MCP_SERVER --> MCP_CLIENT
    MCP_CLIENT --> AGENT
    AGENT --> BOLT
    BOLT --> RESPONSE

    style SLACK fill:#4A154B,stroke:#611f69,color:#fff
    style BOT fill:#1264A3,stroke:#0b4f8a,color:#fff
    style YAHOO fill:#7B68EE,stroke:#5a4fcf,color:#fff
    style DATA fill:#2E8B57,stroke:#1e6b47,color:#fff
```

---

## Request/Response Flow

Here's the complete journey of a single request:

```mermaid
sequenceDiagram
    box rgba(74,21,75,0.8) Slack Workspace
        participant U as 👤 User
        participant S as 💬 Slack
    end
    
    box rgba(18,100,163,0.8) Slack Bot
        participant B as 🔌 Bolt Handler
        participant A as 🧠 Claude Agent
        participant M as 📡 MCP Client
    end
    
    box rgba(123,104,238,0.8) Yahoo Platform
        participant Y as 🎯 MCP Server
    end
    
    box rgba(46,139,87,0.8) Data Layer
        participant DC as ☁️ Data Cloud
        participant SF as ❄️ Snowflake
    end

    Note over U,SF: Example: "Show me Nike advertising options"
    
    U->>S: @adcp-slack-app show me<br/>Nike advertising options
    S->>B: Slack Event (app_mention)
    
    rect rgba(18,100,163,0.3)
        Note over B,M: Bot Processing
        B->>A: Extract message text
        A->>A: Build conversation context
        A->>M: Tool call: get_products<br/>brief="Nike advertising"
    end
    
    rect rgba(123,104,238,0.3)
        Note over M,Y: MCP Protocol
        M->>Y: JSON-RPC 2.0 Request<br/>method: tools/call
        Y->>Y: Validate principal<br/>Apply enterprise pricing
    end
    
    rect rgba(46,139,87,0.3)
        Note over Y,SF: Data Access (READ)
        Y->>DC: SQL Query via Query API
        DC->>SF: Zero Copy Read
        SF-->>DC: Product catalog (5 rows)
        DC-->>Y: Query results
    end
    
    Y-->>M: Tool result (products JSON)
    M-->>A: Products data
    A->>A: Format natural language response
    A-->>B: "Found 5 Yahoo products..."
    B-->>S: Slack Blocks (rich formatting)
    S-->>U: Message with product cards
    
    Note over U,SF: Total time: 2-4 seconds
```

---

## Write Path (Campaign Creation)

When a user creates a campaign, the flow is slightly different:

```mermaid
sequenceDiagram
    box rgba(74,21,75,0.8) Slack
        participant U as 👤 User
    end
    
    box rgba(18,100,163,0.8) Bot
        participant A as 🧠 Agent
    end
    
    box rgba(123,104,238,0.8) Yahoo
        participant Y as 🎯 MCP Server
    end
    
    box rgba(46,139,87,0.8) Data
        participant SF as ❄️ Snowflake
        participant DC as ☁️ Data Cloud
    end

    U->>A: Create campaign with<br/>Yahoo Sports Video, $25K
    
    A->>Y: list_creative_formats
    Y-->>A: Format specs
    
    A->>Y: create_media_buy<br/>packages, dates, budget
    
    rect rgba(255,165,0,0.2)
        Note over Y,DC: WRITE Path
        Y->>SF: INSERT media_buys
        Y->>SF: INSERT packages
        SF->>SF: Commit transaction
        SF-->>DC: Zero Copy Sync<br/>(instant visibility)
    end
    
    Y-->>A: Campaign ID + confirmation
    A-->>U: ✅ Campaign created!<br/>ID: nike_running_q1_2025
    
    Note over SF,DC: Data Cloud sees new campaign<br/>immediately via Zero Copy
```

---

## Architecture Components

### Slack Bot Layer

| Component | Purpose |
|-----------|---------|
| **Slack Bolt** | Handles Slack events (mentions, DMs, commands) |
| **Claude Agent** | Converts natural language to tool calls |
| **MCP Client** | Executes tools against Yahoo MCP Server |

### Yahoo MCP Server

| Tool | Operation | Data Path |
|------|-----------|-----------|
| `get_products` | Discover inventory | READ → Data Cloud |
| `list_creative_formats` | Get format specs | Static response |
| `create_media_buy` | Create campaign | WRITE → Snowflake |
| `get_media_buy` | Get campaign details | READ → Data Cloud |
| `get_media_buy_delivery` | Performance metrics | READ → Data Cloud |
| `update_media_buy` | Modify campaign | WRITE → Snowflake |
| `get_media_buy_report` | Analytics report | READ → Data Cloud |

### Data Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     SNOWFLAKE                                │
│              (Single Source of Truth)                        │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌───────────────┐  │
│  │products │  │media_   │  │packages  │  │delivery_      │  │
│  │         │  │buys     │  │          │  │metrics        │  │
│  └─────────┘  └─────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Zero Copy
                            │ (No ETL, instant sync)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 SALESFORCE DATA CLOUD                        │
│              (Query Interface + Semantics)                   │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌───────────────┐  │
│  │products_│  │media_   │  │packages_ │  │delivery_      │  │
│  │_dlm     │  │buys_dlm │  │_dlm      │  │metrics_dlm    │  │
│  └─────────┘  └─────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Why This Matters

| Before | After |
|--------|-------|
| 5+ systems to launch a campaign | 1 Slack message |
| 2-3 days from brief to live | 30 seconds |
| Manual data reconciliation | Automatic via Zero Copy |
| Copy-paste errors | Validated tool calls |
| Scattered conversations | Threaded, searchable history |

---

## Getting Started

### Prerequisites

1. Slack workspace with admin access
2. Slack App configured with:
   - Socket Mode enabled
   - Bot scopes: `app_mentions:read`, `chat:write`, `im:history`, `im:read`, `im:write`
   - Event subscriptions: `app_mention`, `message.im`
3. Anthropic API key (for Claude)

### Environment Variables

```bash
SLACK_BOT_TOKEN=xoxb-...      # OAuth & Permissions page
SLACK_APP_TOKEN=xapp-...      # Socket Mode token
SLACK_SIGNING_SECRET=...      # Basic Information page
ANTHROPIC_API_KEY=sk-ant-...  # Claude API
MCP_SERVER_URL=https://...    # Yahoo MCP Server (optional, has default)
```

### Run Locally

```bash
cd yahoo_mcp_server
uv sync
uv run python slack_app.py
```

### Test in Slack

DM the bot or @mention it:
- `help` — Show available commands
- `Show me advertising options for Nike` — Discover products
- `Create a campaign with Yahoo Sports Video, $25K` — Create campaign
- `How is campaign XYZ performing?` — Get metrics

---

## Files

```
slack/
├── __init__.py       # Package exports
├── agent.py          # Claude + MCP integration
├── bot.py            # Slack Bolt handlers
├── formatters.py     # Block Kit formatting
└── README.md         # This file

slack_app.py          # Entry point (HTTP + Socket Mode)
```

---

## Learn More

- [MCP Protocol](https://modelcontextprotocol.io)
- [AdCP Specification](https://adcontextprotocol.org)
- [Slack Bolt for Python](https://slack.dev/bolt-python)
- [Salesforce Data Cloud](https://www.salesforce.com/data-cloud/)

