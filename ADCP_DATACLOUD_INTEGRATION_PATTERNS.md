# Salesforce Data Cloud × AdCP Integration Patterns

## Color Legend

| Color | Role |
|-------|------|
| 🟦 | Salesforce Data Cloud / Clean Room |
| 🟩 | Advertiser / Orchestrator (e.g., Nike, agency, AI planning agent) |
| 🟥 | Media Seller / Decisioning (e.g., Yahoo, Hulu, DSP, RMN) |
| 🟧 | MCP / AdCP Orchestration & Agents |

---

## Pattern 1: Salesforce as Signal Provider to AdCP

Salesforce supplies **privacy-safe audience signals** and clean-room overlaps into an external AdCP ecosystem.

### 1.1 High-Level Architecture

```mermaid
flowchart TB
    subgraph BUYER ["🟩 ADVERTISER / ORCHESTRATOR"]
        PLAN["AI Planner<br/>MCP Client"]
    end

    subgraph ADCP_LAYER ["🟧 AdCP ORCHESTRATION"]
        ORCH["AdCP MCP<br/>Orchestrator"]
    end

    subgraph SFDC ["🟦 SALESFORCE DATA CLOUD ORG"]
        DC["Data Cloud<br/>Segments"]
        CR["Clean Room<br/>Federated Queries"]
        SF_SIG["MCP Signals Agent<br/>───────────────<br/>• discover_signals<br/>• compute_overlap<br/>• activate_segment"]
        
        DC --> CR
        CR --> SF_SIG
    end

    subgraph MEDIA ["🟥 MEDIA / DECISIONING"]
        SALES["Sales Agents<br/>Yahoo, RMN, DSP"]
        DSP["Decisioning<br/>Platform"]
        
        SALES --> DSP
    end

    PLAN -->|"1. NL brief & goals"| ORCH
    ORCH -->|"2. Signals tasks"| SF_SIG
    SF_SIG -->|"3. Segments & overlap<br/>(aggregated only)"| ORCH
    ORCH -->|"4. Media buy tasks"| SALES
    SALES -->|"5. Targeting handles<br/>cohort IDs, keys"| DSP
```

### 1.2 Sequence Diagram

```mermaid
sequenceDiagram
    box rgb(200, 230, 200) Advertiser
        participant P as 🟩 Planner<br/>(Nike MCP Client)
    end
    
    box rgb(255, 220, 180) Orchestration
        participant O as 🟧 AdCP<br/>Orchestrator
    end
    
    box rgb(200, 210, 240) Salesforce
        participant SA as 🟦 Signals Agent
        participant DC as 🟦 Data Cloud<br/>+ Clean Room
    end
    
    box rgb(255, 200, 200) Media
        participant S as 🟥 Media Sales<br/>Agent / DSP
    end

    rect rgb(240, 248, 255)
        Note over P,DC: Phase 1: Campaign Discovery
        P->>O: 1. "Find Nike runners in<br/>overlap with Hulu/Yahoo"
        O->>SA: 2. AdCP:discover_signals<br/>+ compute_overlap
        SA->>DC: 3. Run clean-room overlap<br/>on hashed IDs (no raw PII)
        DC-->>SA: 4. Aggregated overlap,<br/>cohort IDs
        SA-->>O: 5. Return AdCP signal objects<br/>(segment handles, overlap stats)
        O-->>P: 6. Options & recommendations
    end

    rect rgb(255, 248, 240)
        Note over P,S: Phase 2: Activation
        P->>O: 7. Choose segment + budget
        O->>S: 8. AdCP:media_buy<br/>with SFDC cohort IDs
        S-->>O: 9. Deal + campaign details
        O-->>P: 10. Confirmation +<br/>reporting links
    end
```

### 1.3 Key Points

- **Data stays in Salesforce**: Data Cloud + Clean Room remain **inside Salesforce**, enforcing no raw data movement and k‑anonymity.
- **Standards-based signals source**: An **MCP Signals Agent** fronting Salesforce exposes AdCP "signals" tasks; external AdCP orchestrators just see a standards-based signals source.
- **Privacy-first architecture**: Only aggregated overlap statistics and cohort IDs leave the clean room—never raw PII or user-level data.

---

## Pattern 2: Salesforce as AdCP Implementation

Salesforce hosts **AdCP agents (signals + sales)** and can become the **native protocol surface** for buyer and seller workflows.

### 2.1 High-Level Architecture

```mermaid
flowchart TB
    subgraph CLIENTS ["🟩 EXTERNAL & INTERNAL MCP CLIENTS"]
        NIKE["Planner / Agentforce Client<br/>─────────────────────<br/>Nike, Agency, Internal Teams"]
    end

    subgraph SFDC ["🟦 SALESFORCE CLOUD STACK — AdCP Native"]
        direction TB
        
        subgraph AGENTS ["🟧 MCP / AdCP AGENTS"]
            SF_SIG["Signals Agent<br/>───────────────<br/>AdCP Signals Protocol"]
            SF_SALES["Sales Agent<br/>───────────────<br/>AdCP Media Buy<br/>& Curation"]
        end

        subgraph DATACLOUD ["🟦 DATA CLOUD + CLEAN ROOM"]
            SEG["Segments & DMO<br/>───────────────<br/>Customer Data<br/>Engagement Data"]
            CR["Clean Room<br/>───────────────<br/>Federated Queries<br/>k-Anonymity"]
        end

        subgraph MEDIACLOUD ["🟦 MEDIA CLOUD / AD SALES"]
            INV["Inventory<br/>& Products"]
            DEAL["Deals, Orders<br/>& Campaigns"]
        end
    end

    subgraph DEST ["🟥 EXTERNAL DECISIONING"]
        DSP["Decisioning Platforms<br/>───────────────<br/>Retail Media • SSP • DSP"]
    end

    NIKE -->|"1. MCP calls tools"| SF_SIG
    NIKE -->|"2. MCP calls tools"| SF_SALES
    
    SF_SIG --> SEG
    SF_SIG --> CR
    
    SF_SALES --> INV
    SF_SALES --> DEAL
    DEAL -->|"Cohort IDs<br/>Line Items"| DSP
```

### 2.2 Sequence Diagram

```mermaid
sequenceDiagram
    box rgb(200, 230, 200) Client
        participant C as 🟩 Client<br/>(Nike / Planner)
    end
    
    box rgb(255, 220, 180) SFDC Agents
        participant SSA as 🟧 Signals Agent<br/>(MCP)
        participant SSALES as 🟧 Sales Agent<br/>(MCP)
    end
    
    box rgb(200, 210, 240) SFDC Backend
        participant DC as 🟦 Data Cloud<br/>+ Clean Room
        participant MC as 🟦 Media Cloud<br/>/ Ad Sales
    end
    
    box rgb(255, 200, 200) External
        participant DSP as 🟥 External<br/>DSP / RMN
    end

    rect rgb(230, 245, 255)
        Note over C,DC: Phase 1: Signals & Overlap Discovery
        C->>SSA: 1. AdCP:discover_signals<br/>("runners", "CTV viewers")
        SSA->>DC: 2. Query segments,<br/>run overlap in Clean Room
        DC-->>SSA: 3. Aggregated results<br/>+ cohort IDs
        SSA-->>C: 4. AdCP signal list<br/>(SFDC-native)
    end

    rect rgb(255, 245, 230)
        Note over C,MC: Phase 2: Plan & Create Buy
        C->>SSALES: 5. AdCP:media_buy<br/>(SF segments + SF inventory)
        SSALES->>MC: 6. Build proposal,<br/>deal, line items
        MC-->>SSALES: 7. Campaign IDs,<br/>pacing, flight dates
        SSALES-->>C: 8. Media buy confirmation<br/>+ tracking keys
    end

    rect rgb(255, 235, 235)
        Note over MC,DSP: Phase 3: Downstream Execution
        MC->>DSP: 9. Push cohort/segment IDs<br/>and line items
        DSP-->>MC: 10. Delivery &<br/>performance metrics
        MC-->>SSALES: 11. Aggregated reporting
        SSALES-->>C: 12. AdCP-standard<br/>analytics objects
    end
```

### 2.3 Key Points

- **Salesforce hosts MCP servers**: Salesforce **hosts the MCP servers** that implement AdCP tasks, so external agents just "talk AdCP to Salesforce."
- **Unified backend**: Data Cloud + Clean Room back all signals/overlap logic, while Media Cloud / Ad Sales back inventory and deal execution; both are exposed via AdCP Signals and Media Buy protocols.
- **End-to-end workflow**: Planning, audience creation, inventory selection, and activation all happen within Salesforce's AdCP-compatible surface.

---

## When to Choose Each Pattern

| Pattern | Use Case | Best For |
|---------|----------|----------|
| **Pattern 1 – Signal Provider** | Salesforce is the **data/identity and clean-room spine**, but orchestration and media buying are owned by external AdCP platforms (Yahoo, RMNs, DSPs) | Organizations with existing media buying infrastructure who want to leverage Salesforce's identity and data capabilities |
| **Pattern 2 – Full AdCP** | Salesforce is the **agentic media hub**: planning, audience, inventory, and activation all exposed via AdCP-compatible MCP servers (Agentforce + Data Cloud + Media Cloud) | Organizations wanting a unified, Salesforce-native advertising workflow with full protocol compliance |

---

## Summary Comparison

```mermaid
flowchart LR
    subgraph P1 ["PATTERN 1: Signal Provider"]
        direction TB
        A1["🟦 Salesforce<br/>Data Cloud"]
        B1["🟧 External<br/>AdCP Platform"]
        C1["🟥 Media<br/>Execution"]
        
        A1 -->|"Signals<br/>Only"| B1
        B1 --> C1
    end

    subgraph P2 ["PATTERN 2: Full AdCP Stack"]
        direction TB
        A2["🟩 External<br/>Clients"]
        B2["🟦 Salesforce<br/>AdCP Stack"]
        C2["🟥 Media<br/>Execution"]
        
        A2 -->|"AdCP<br/>Protocol"| B2
        B2 --> C2
    end

    P1 -..- CHOOSE1
    P2 -..- CHOOSE2

    CHOOSE1["✓ Choose when media buying<br/>is externally managed<br/>───────────────<br/>Data stays in SFDC<br/>External orchestration"]
    CHOOSE2["✓ Choose when SFDC is<br/>the agentic media hub<br/>───────────────<br/>Full stack in SFDC<br/>Native AdCP surface"]
```

---

## Data Flow Summary

```mermaid
flowchart LR
    subgraph INPUT ["📥 INPUT"]
        NL["Natural Language<br/>Campaign Brief"]
    end

    subgraph SIGNALS ["🟦 SIGNALS PHASE"]
        SIG1["discover_signals"]
        SIG2["compute_overlap"]
        SIG3["activate_segment"]
    end

    subgraph BUY ["🟧 MEDIA BUY PHASE"]
        BUY1["get_inventory"]
        BUY2["create_proposal"]
        BUY3["execute_buy"]
    end

    subgraph OUTPUT ["📤 OUTPUT"]
        OUT["Campaign Live<br/>+ Reporting"]
    end

    INPUT --> SIGNALS
    SIGNALS --> BUY
    BUY --> OUTPUT

    style INPUT fill:#e8f5e9
    style SIGNALS fill:#e3f2fd
    style BUY fill:#fff3e0
    style OUTPUT fill:#ffebee
```

---

## Glossary

| Term | Definition |
|------|------------|
| **AdCP** | Advertising Control Protocol – a standardized protocol for agentic advertising workflows |
| **MCP** | Model Context Protocol – enables AI agents to interact with external tools and data sources |
| **Clean Room** | Privacy-preserving environment for data collaboration without exposing raw user data |
| **k-Anonymity** | Privacy technique ensuring each record is indistinguishable from at least k-1 other records |
| **DMO** | Data Model Objects in Salesforce Data Cloud |
| **RMN** | Retail Media Network |
| **DSP** | Demand-Side Platform |
| **SSP** | Supply-Side Platform |
| **Cohort IDs** | Privacy-safe identifiers representing groups of users rather than individuals |
