# AdCP Compliance Implementation Plan
## Nike-Yahoo MCP Server Refactoring

**Document Version:** 1.0  
**Date:** November 19, 2025  
**Author:** Nike-Yahoo Integration Team  
**Target Platform:** FastMCP Cloud → Salesforce Data Cloud

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Understanding AdCP Compliance](#understanding-adcp-compliance)
3. [Why AdCP Compliance Matters](#why-adcp-compliance-matters)
4. [Current State vs. AdCP-Compliant State](#current-state-vs-adcp-compliant-state)
5. [Technical Implementation Roadmap](#technical-implementation-roadmap)
6. [Phase 1: Agent Discovery Endpoints](#phase-1-agent-discovery-endpoints)
7. [Phase 2: Package-Based Media Buy](#phase-2-package-based-media-buy)
8. [Phase 3: Database Refactoring](#phase-3-database-refactoring)
9. [Phase 4: Testing & Validation](#phase-4-testing--validation)
10. [Phase 5: FastMCP Cloud Deployment](#phase-5-fastmcp-cloud-deployment)
11. [Phase 6: Salesforce Data Cloud Migration](#phase-6-salesforce-data-cloud-migration)

---

## Executive Summary

### Current State
- ✅ Fully functional Nike MCP Client ↔ Yahoo MCP Server
- ✅ HTTP/SSE transport working
- ✅ 6 custom tools (product discovery, campaign management, metrics)
- ✅ SQLite database with realistic data
- ✅ LLM integration (OpenAI/Gemini)

### Goal
Transform the Yahoo MCP Server into an **AdCP v2.3.0 compliant sales agent** that:
1. Can be discovered by any AdCP buyer agent (not just Nike)
2. Follows standardized AdCP media buy protocol
3. Supports package-based campaign structure
4. Exposes creative format specifications
5. Deploys to FastMCP Cloud for production readiness
6. Integrates with Salesforce Data Cloud for enterprise data management

### Success Criteria
- ✅ Pass AdCP schema validation
- ✅ Discoverable via `/.well-known/` endpoints
- ✅ Claude Desktop can discover and interact with Yahoo agent
- ✅ Package-based media buys work with multiple products
- ✅ Creative formats properly specified and validated
- ✅ Deployed to FastMCP Cloud with OAuth
- ✅ Connected to Salesforce Data Cloud

---

## Understanding AdCP Compliance

### What is AdCP?

**Ad Context Protocol (AdCP) v2.3.0** is an open standard that enables AI agents to autonomously discover, negotiate, and execute advertising media buys across different publishers.

**Key Principles:**
1. **Agent Discovery**: Standardized way for buyer agents to find seller agents
2. **Interoperability**: Any buyer can work with any seller using the protocol
3. **Package-Based Structure**: Media buys organized as discrete packages with specific formats
4. **Creative Format Specification**: Clear definition of required creative assets
5. **Namespace Isolation**: Prevents conflicts between different agents

### Core Components

#### 1. **Discovery Endpoints (/.well-known/)**

Two required JSON files that make your agent discoverable:

**A) `/.well-known/adagents.json`**
```json
{
  "$schema": "https://adcontextprotocol.org/schemas/v1/adagents.json",
  "authorized_agents": [
    {
      "url": "http://localhost:8080",
      "authorized_for": "Yahoo advertising inventory sales",
      "property_ids": ["yahoo_homepage", "yahoo_sports", "yahoo_finance"]
    }
  ],
  "properties": [...],
  "last_updated": "2025-11-19T00:00:00Z"
}
```

**B) `/.well-known/agent-card.json`**
```json
{
  "name": "Yahoo Sales Agent",
  "provider": {"name": "Yahoo", "url": "https://www.yahoo.com"},
  "url": "http://localhost:8080/mcp",
  "protocols": [{"name": "mcp", "version": "1.0"}],
  "authentication": {"schemes": ["Bearer"]},
  "skills": ["get_products", "create_media_buy", ...],
  "supported_formats": ["display_300x250", "video_30s"],
  "version": "1.0.0"
}
```

**Purpose:** Allows any AdCP buyer agent to:
- Discover that Yahoo has a sales agent
- Learn what properties are available (Sports, Finance, etc.)
- Understand authentication requirements
- See what capabilities/tools are available
- Know which creative formats are supported

#### 2. **Package-Based Media Buy Structure**

**Current (Non-Compliant):**
```python
create_media_buy(
    product_ids=["yahoo_sports_display"],  # ❌ Wrong
    total_budget=50000,                    # ❌ Wrong
    targeting={...}                        # ❌ Wrong
)
```

**AdCP-Compliant:**
```python
create_media_buy(
    buyer_ref="nike_q1_2025",              # ✅ Buyer reference
    packages=[                             # ✅ Package array
        {
            "buyer_ref": "nike_display_pkg",
            "product_id": "yahoo_sports_display",
            "budget": 30000,               # ✅ Per-package budget
            "pricing_option_id": "cpm-fixed-display",
            "pacing": "even",
            "format_ids": [                # ✅ REQUIRED
                {
                    "agent_url": "http://localhost:8080",
                    "id": "yahoo_display_300x250"
                }
            ],
            "targeting_overlay": {...}     # ✅ Renamed
        }
    ],
    flight_start_date="2025-01-01",
    flight_end_date="2025-03-31"
)
```

**Key Changes:**
- **No more `product_ids`** → Use `packages` array
- **No more `total_budget`** → Each package has its own budget
- **`format_ids` is REQUIRED** → Must specify creative formats
- **`targeting` → `targeting_overlay`** → Renamed per spec
- **Add `buyer_ref`** at both media buy and package level
- **Add `pricing_option_id`** to each package
- **Add `pacing`** strategy per package

#### 3. **Format ID Structure**

Every creative format MUST use structured `format_id`:

```json
{
  "format_id": {
    "agent_url": "http://localhost:8080",
    "id": "yahoo_display_300x250"
  }
}
```

**Components:**
- **`agent_url`**: URL of the agent that defines the format (your server)
- **`id`**: Unique format identifier in your namespace

**Namespace Pattern:** `{domain}:{format_id}`
- Example: `localhost:8080:yahoo_display_300x250`

**References:**
- [AdCP Format Specification](https://docs.adcontextprotocol.org/docs/creative/formats)
- [AdCP Standard Formats](https://adcontextprotocol.org/docs/media-buy/capability-discovery/implementing-standard-formats)

---

## Why AdCP Compliance Matters

### 1. **Universal Agent Interoperability**

**Without AdCP:**
- Only your custom Nike client can talk to Yahoo server
- Each new buyer requires custom integration
- No standardization across industry

**With AdCP:**
- **Claude Desktop** can discover and buy Yahoo inventory
- **Any AdCP buyer agent** (Google, Meta, agencies) can connect
- **AI assistants** can autonomously execute media buys
- **Programmatic platforms** can integrate easily

### 2. **Industry Standardization**

AdCP is becoming the **de facto standard** for AI-powered advertising:
- Backed by major industry players
- Open specification with growing ecosystem
- Future-proofs your implementation
- Reduces integration costs

### 3. **Yahoo's Strategic Advantage**

Being AdCP-compliant means:
- ✅ First to market with AI-native advertising platform
- ✅ Attracts innovative buyers using AI agents
- ✅ Reduces sales cycle (automated discovery)
- ✅ Competitive differentiation
- ✅ Ready for programmatic AI future

### 4. **Proof-of-Tech Success**

For Yahoo's proof-of-tech demonstration:
- ✅ Shows technical sophistication
- ✅ Demonstrates forward-thinking architecture
- ✅ Proves scalability and interoperability
- ✅ Validates investment in AI infrastructure

---

## Current State vs. AdCP-Compliant State

### Architecture Comparison

| Aspect | Current State | AdCP-Compliant State |
|--------|--------------|---------------------|
| **Discovery** | None (hardcoded client) | `/.well-known/adagents.json` + `agent-card.json` |
| **Media Buy Structure** | Product-based (`product_ids`, `total_budget`) | Package-based (array of packages with individual budgets) |
| **Creative Formats** | Optional `creative_ids` | **REQUIRED** `format_ids` with structured objects |
| **Targeting** | `targeting` dict | `targeting_overlay` dict |
| **Pricing** | Implicit in product | Explicit `pricing_option_id` per package |
| **Budget Pacing** | Not specified | Required `pacing` per package ("even", "asap", "front_loaded") |
| **Buyer Reference** | None | Required `buyer_ref` at media buy and package level |
| **Format Discovery** | No tool | New `list_creative_formats` tool |
| **Response Structure** | Simple `media_buy_id` | Includes `packages[]`, `creative_deadline` |

### Database Schema Changes Required

#### Current Tables (Simplified)
```sql
media_buys:
  - id
  - media_buy_id
  - product_ids (JSON array)        ← Change to packages
  - total_budget                    ← Remove
  - targeting (JSON)                ← Rename
  - creative_ids (JSON array)       ← Remove

products:
  - id
  - product_id
  - pricing (JSON)                  ← Add pricing_option_id
  - formats (JSON)                  ← Change to structured format_ids
```

#### AdCP-Compliant Schema
```sql
media_buys:
  - id
  - media_buy_id
  - buyer_ref                       ← NEW
  - packages (JSON array)           ← NEW (replaces product_ids)
  - creative_deadline               ← NEW
  - flight_start_date
  - flight_end_date

packages:                           ← NEW TABLE
  - id
  - media_buy_id (FK)
  - package_id
  - buyer_ref
  - product_id
  - budget                          ← Per-package
  - pricing_option_id               ← NEW
  - pacing                          ← NEW
  - format_ids (JSON)               ← NEW (structured)
  - targeting_overlay (JSON)        ← NEW
  - status

products:
  - id
  - product_id
  - pricing_options (JSON array)    ← NEW (list of pricing models)
  - supported_formats (JSON array)  ← NEW (structured format_ids)
```

---

## Technical Implementation Roadmap

### Overview

**Total Timeline:** 4-6 weeks  
**Phases:** 6 phases with clear milestones  
**Testing Strategy:** Iterative validation at each phase  
**Deployment Path:** Local → FastMCP Cloud → Salesforce Data Cloud

### Phase Dependencies

```
Phase 1: Discovery Endpoints
    ↓
Phase 2: Package-Based Media Buy
    ↓
Phase 3: Database Refactoring
    ↓
Phase 4: Testing & Validation
    ↓
Phase 5: FastMCP Cloud Deployment
    ↓
Phase 6: Salesforce Data Cloud Migration
```

---

## Phase 1: Agent Discovery Endpoints

**Duration:** 3-5 days  
**Goal:** Make Yahoo agent discoverable via standardized endpoints

### 1.1 Add FastAPI to Server

**Current Setup:**
- FastMCP handles MCP protocol at `/mcp`
- No standard HTTP endpoints

**Required Change:**
Add FastAPI alongside FastMCP for `/.well-known/` endpoints

**File:** `yahoo_mcp_server/server_http.py`

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
import uvicorn

# Initialize FastMCP (existing)
mcp = FastMCP(name="yahoo-sales-agent", version="2.3.0")

# Initialize FastAPI (NEW)
app = FastAPI(title="Yahoo Sales Agent - AdCP v2.3.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 1.2 Implement `/.well-known/adagents.json`

**Endpoint:** `GET /.well-known/adagents.json`

**Implementation:**

```python
@app.get("/.well-known/adagents.json")
async def adagents_discovery():
    """
    AdCP Agent Discovery Endpoint
    Declares Yahoo's authorization to sell inventory
    """
    return JSONResponse({
        "$schema": "https://adcontextprotocol.org/schemas/v1/adagents.json",
        "authorized_agents": [
            {
                "url": "http://localhost:8080",  # Will change for FastMCP Cloud
                "authorized_for": "Yahoo advertising inventory sales across Sports, Finance, and Entertainment properties",
                "property_ids": [
                    "yahoo_homepage",
                    "yahoo_sports",
                    "yahoo_finance",
                    "yahoo_entertainment"
                ]
            }
        ],
        "properties": [
            {
                "property_id": "yahoo_homepage",
                "property_type": "website",
                "name": "Yahoo Homepage",
                "identifiers": [
                    {"type": "domain", "value": "yahoo.com"}
                ],
                "tags": ["premium", "high-traffic", "brand-safe"]
            },
            {
                "property_id": "yahoo_sports",
                "property_type": "website",
                "name": "Yahoo Sports",
                "identifiers": [
                    {"type": "domain", "value": "sports.yahoo.com"}
                ],
                "tags": ["sports", "premium", "engaged-audience"]
            },
            {
                "property_id": "yahoo_finance",
                "property_type": "website",
                "name": "Yahoo Finance",
                "identifiers": [
                    {"type": "domain", "value": "finance.yahoo.com"}
                ],
                "tags": ["finance", "business", "affluent"]
            },
            {
                "property_id": "yahoo_entertainment",
                "property_type": "website",
                "name": "Yahoo Entertainment",
                "identifiers": [
                    {"type": "domain", "value": "entertainment.yahoo.com"}
                ],
                "tags": ["entertainment", "lifestyle", "trending"]
            }
        ],
        "last_updated": "2025-11-19T00:00:00Z"
    })
```

### 1.3 Implement `/.well-known/agent-card.json`

**Endpoint:** `GET /.well-known/agent-card.json`

**Implementation:**

```python
@app.get("/.well-known/agent-card.json")
async def agent_card():
    """
    AdCP Agent Card Endpoint
    Describes Yahoo agent capabilities and connection details
    """
    return JSONResponse({
        "name": "Yahoo Sales Agent",
        "description": "AI-powered sales agent for Yahoo advertising inventory across premium properties including Sports, Finance, and Entertainment",
        "provider": {
            "name": "Yahoo",
            "url": "https://www.yahoo.com",
            "contact_email": "adcp-support@yahoo.com"
        },
        "url": "http://localhost:8080/mcp",  # MCP endpoint
        "protocols": [
            {
                "name": "mcp",
                "version": "1.0",
                "endpoint": "http://localhost:8080/mcp",
                "transport": "streamable-http"
            }
        ],
        "authentication": {
            "schemes": ["Bearer"],
            "instructions": "Contact Yahoo Sales team to obtain API credentials. Enterprise customers receive dedicated tokens."
        },
        "capabilities": {
            "streaming": True,
            "webhooks": False,
            "batch_operations": False
        },
        "skills": [
            {
                "name": "get_products",
                "description": "Discover Yahoo advertising inventory using natural language. Supports LLM-powered product matching and returns matched audience data from Clean Room."
            },
            {
                "name": "create_media_buy",
                "description": "Create package-based advertising campaigns on Yahoo properties following AdCP v2.3.0 specification."
            },
            {
                "name": "get_media_buy",
                "description": "Retrieve campaign configuration and status."
            },
            {
                "name": "get_media_buy_delivery",
                "description": "Monitor real-time campaign performance metrics including CTR, CVR, pacing, and matched audience engagement."
            },
            {
                "name": "update_media_buy",
                "description": "Modify active campaign configuration including budget, targeting, and pacing."
            },
            {
                "name": "get_media_buy_report",
                "description": "Generate comprehensive analytics reports with device, geo, and creative breakdowns."
            },
            {
                "name": "list_creative_formats",
                "description": "Discover all creative formats supported by Yahoo inventory with detailed specifications."
            }
        ],
        "supported_formats": [
            "display_300x250",
            "display_728x90",
            "display_160x600",
            "video_30s",
            "video_15s",
            "native_responsive",
            "ctv_fullscreen"
        ],
        "version": "2.3.0",
        "adcp_version": "2.3.0",
        "last_updated": "2025-11-19T00:00:00Z"
    })
```

### 1.4 Mount FastAPI + FastMCP

**Challenge:** Run both FastAPI (for `/.well-known/`) and FastMCP (for `/mcp`) on same port

**Solution:** Use FastAPI's mount or sub-application pattern

```python
# Option 1: Mount MCP as sub-application
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP(name="yahoo-sales-agent")

# Add /.well-known/ endpoints to app (shown above)

# Mount MCP at /mcp
# Note: FastMCP provides .http_app attribute for this
app.mount("/mcp", mcp.http_app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 1.5 Testing Discovery Endpoints

**Test Commands:**

```bash
# Test adagents.json
curl http://localhost:8080/.well-known/adagents.json | jq

# Test agent-card.json
curl http://localhost:8080/.well-known/agent-card.json | jq

# Validate schema compliance
# (Use AdCP validator if available)
```

**Expected Responses:**
- ✅ 200 OK with valid JSON
- ✅ Correct schema structure
- ✅ All properties listed
- ✅ All skills documented

### 1.6 Deliverables - Phase 1

- [ ] `/.well-known/adagents.json` endpoint implemented
- [ ] `/.well-known/agent-card.json` endpoint implemented
- [ ] FastAPI + FastMCP mounted correctly
- [ ] Both endpoints return valid JSON
- [ ] Documentation updated with discovery endpoints
- [ ] Manual testing completed
- [ ] README updated with discovery examples

---

## Phase 2: Package-Based Media Buy

**Duration:** 5-7 days  
**Goal:** Refactor `create_media_buy` to AdCP v2.3.0 specification

### 2.1 New `create_media_buy` Signature

**File:** `yahoo_mcp_server/server_http.py`

**Current (Non-Compliant):**
```python
@mcp.tool()
async def create_media_buy(
    product_ids: list[str],
    total_budget: float,
    flight_start_date: str,
    flight_end_date: str,
    targeting: Optional[dict] = None,
    creative_ids: Optional[list[str]] = None
) -> dict:
    pass
```

**New (AdCP-Compliant):**
```python
@mcp.tool()
async def create_media_buy(
    buyer_ref: str,
    packages: list[dict],
    flight_start_date: str,
    flight_end_date: str
) -> dict:
    """
    Create advertising campaign following AdCP v2.3.0 specification.
    
    Args:
        buyer_ref: Buyer's reference identifier (e.g., "nike_q1_2025_campaign")
        packages: Array of package configurations. Each package must contain:
            - buyer_ref (str): Package-level reference (e.g., "nike_display_pkg_1")
            - product_id (str): Yahoo product identifier
            - budget (float): Budget allocated to THIS package
            - pricing_option_id (str): Pricing model (e.g., "cpm-fixed-display")
            - pacing (str): Budget pacing strategy ("even", "asap", "front_loaded")
            - format_ids (list[dict]): REQUIRED - Creative format specifications
                Each format_id contains:
                    - agent_url (str): Creative agent URL
                    - id (str): Format identifier
            - targeting_overlay (dict): Optional targeting parameters
                Common fields:
                    - geo_country_any_of: list[str]
                    - age_min: int
                    - age_max: int
                    - content_category_any_of: list[str]
                    - device_type_any_of: list[str]
        
        flight_start_date: ISO 8601 date (YYYY-MM-DD)
        flight_end_date: ISO 8601 date (YYYY-MM-DD)
    
    Returns:
        {
            "media_buy_id": str,
            "buyer_ref": str,
            "status": str,
            "total_budget": float,
            "creative_deadline": str (ISO 8601),
            "packages": [
                {
                    "package_id": str,
                    "buyer_ref": str,
                    "product_id": str,
                    "budget": float,
                    "status": str
                }
            ],
            "flight_start_date": str,
            "flight_end_date": str
        }
    
    Raises:
        ValueError: If required fields missing or invalid
    
    Example:
        {
            "buyer_ref": "nike_q1_2025",
            "packages": [
                {
                    "buyer_ref": "nike_sports_display",
                    "product_id": "yahoo_sports_display_enthusiasts",
                    "budget": 30000,
                    "pricing_option_id": "cpm-fixed-display",
                    "pacing": "even",
                    "format_ids": [
                        {
                            "agent_url": "http://localhost:8080",
                            "id": "yahoo_display_300x250"
                        }
                    ],
                    "targeting_overlay": {
                        "geo_country_any_of": ["US"],
                        "age_min": 25,
                        "age_max": 45
                    }
                }
            ],
            "flight_start_date": "2025-01-01",
            "flight_end_date": "2025-03-31"
        }
    """
    logger.info(f"🚀 create_media_buy (AdCP v2.3) - buyer_ref: {buyer_ref}")
    logger.info(f"   Packages: {len(packages)}")
    
    # Validation (see next section)
    validate_packages(packages)
    
    # Implementation (see next section)
    pass
```

### 2.2 Package Validation

**File:** `yahoo_mcp_server/validators/adcp_validator.py` (NEW)

```python
"""
AdCP v2.3.0 Validation Functions
Validates media buy requests against AdCP specification
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AdCPValidationError(Exception):
    """Raised when AdCP validation fails"""
    pass


def validate_packages(packages: List[Dict[str, Any]]) -> None:
    """
    Validate packages array against AdCP v2.3.0 specification.
    
    Required fields per package:
    - buyer_ref
    - product_id
    - budget
    - pricing_option_id
    - pacing
    - format_ids (CRITICAL - must be non-empty structured objects)
    
    Raises:
        AdCPValidationError: If validation fails
    """
    if not packages:
        raise AdCPValidationError("packages array cannot be empty")
    
    for idx, pkg in enumerate(packages):
        package_ref = f"Package {idx + 1}"
        
        # Required fields
        required_fields = [
            "buyer_ref",
            "product_id",
            "budget",
            "pricing_option_id",
            "pacing",
            "format_ids"
        ]
        
        for field in required_fields:
            if field not in pkg:
                raise AdCPValidationError(
                    f"{package_ref}: Missing required field '{field}'"
                )
        
        # Validate format_ids structure (CRITICAL)
        validate_format_ids(pkg["format_ids"], package_ref)
        
        # Validate budget
        if not isinstance(pkg["budget"], (int, float)) or pkg["budget"] <= 0:
            raise AdCPValidationError(
                f"{package_ref}: budget must be positive number"
            )
        
        # Validate pacing
        valid_pacing = ["even", "asap", "front_loaded"]
        if pkg["pacing"] not in valid_pacing:
            raise AdCPValidationError(
                f"{package_ref}: pacing must be one of {valid_pacing}"
            )
        
        logger.info(f"✅ {package_ref} validated: {pkg['buyer_ref']}")


def validate_format_ids(format_ids: List[Dict[str, str]], context: str) -> None:
    """
    Validate format_ids array - CRITICAL for AdCP v2.3.0.
    
    Each format_id must be a structured object with:
    - agent_url: string
    - id: string
    
    Args:
        format_ids: Array of format_id objects
        context: Context string for error messages
    
    Raises:
        AdCPValidationError: If validation fails
    """
    if not format_ids or len(format_ids) == 0:
        raise AdCPValidationError(
            f"{context}: format_ids is REQUIRED and cannot be empty (AdCP v2.3.0)"
        )
    
    for idx, fmt in enumerate(format_ids):
        if not isinstance(fmt, dict):
            raise AdCPValidationError(
                f"{context}: format_ids[{idx}] must be object with {{agent_url, id}}"
            )
        
        if "agent_url" not in fmt:
            raise AdCPValidationError(
                f"{context}: format_ids[{idx}] missing 'agent_url'"
            )
        
        if "id" not in fmt:
            raise AdCPValidationError(
                f"{context}: format_ids[{idx}] missing 'id'"
            )
        
        # Validate agent_url format (basic URL check)
        if not fmt["agent_url"].startswith(("http://", "https://")):
            raise AdCPValidationError(
                f"{context}: format_ids[{idx}].agent_url must be valid URL"
            )
        
        logger.debug(f"✅ Format validated: {fmt['agent_url']}:{fmt['id']}")
```

### 2.3 Deliverables - Phase 2

- [ ] `create_media_buy` refactored to package-based structure
- [ ] Package validation implemented
- [ ] `MediaBuyService.create_media_buy_adcp()` implemented
- [ ] `list_creative_formats` tool added
- [ ] AdCP validator module created
- [ ] Unit tests for validation logic
- [ ] Integration tests for package-based flow
- [ ] Documentation updated with examples

---

## Phase 3: Database Refactoring

**Duration:** 3-4 days  
**Goal:** Update database schema to support AdCP package structure

### 3.1 New Database Schema

**File:** `database/schema_adcp.sql` (NEW)

```sql
-- ============================================================================
-- AdCP v2.3.0 Compliant Schema
-- Supports package-based media buys with structured format_ids
-- ============================================================================

-- Tenants (unchanged)
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    adapter_type TEXT NOT NULL,
    adapter_config TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Principals (unchanged)
CREATE TABLE IF NOT EXISTS principals (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    principal_id TEXT UNIQUE NOT NULL,
    auth_token TEXT NOT NULL,
    access_level TEXT NOT NULL,
    metadata TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Products (MODIFIED - add pricing_options, structured formats)
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    product_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    product_type TEXT NOT NULL,
    properties TEXT,  -- JSON array of property domains
    
    -- CHANGED: pricing_options instead of single pricing
    pricing_options TEXT NOT NULL,  -- JSON array of pricing models
    
    -- CHANGED: structured format_ids
    supported_formats TEXT NOT NULL,  -- JSON array of format_id objects
    
    targeting TEXT,
    matched_audience_ids TEXT,
    minimum_budget REAL,
    estimated_reach INTEGER,
    matched_reach INTEGER,
    estimated_impressions INTEGER,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Media Buys (MODIFIED - add buyer_ref, packages, creative_deadline)
CREATE TABLE IF NOT EXISTS media_buys (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    media_buy_id TEXT UNIQUE NOT NULL,
    principal_id TEXT NOT NULL,
    
    -- NEW: AdCP fields
    buyer_ref TEXT NOT NULL,           -- Buyer's reference ID
    packages TEXT NOT NULL,            -- JSON array of package objects
    creative_deadline TEXT,            -- ISO 8601 timestamp
    
    -- Keep total_budget for reporting (calculated from packages)
    total_budget REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    
    flight_start_date TEXT NOT NULL,
    flight_end_date TEXT NOT NULL,
    status TEXT DEFAULT 'pending_creative',
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (principal_id) REFERENCES principals(id)
);

-- NEW: Packages table (normalized package data)
CREATE TABLE IF NOT EXISTS packages (
    id TEXT PRIMARY KEY,
    media_buy_id TEXT NOT NULL,  -- FK to media_buys
    package_id TEXT UNIQUE NOT NULL,
    buyer_ref TEXT NOT NULL,
    
    product_id TEXT NOT NULL,
    budget REAL NOT NULL,
    pricing_option_id TEXT NOT NULL,
    pacing TEXT NOT NULL,  -- "even", "asap", "front_loaded"
    
    format_ids TEXT NOT NULL,       -- JSON array of format_id objects
    targeting_overlay TEXT,         -- JSON targeting parameters
    
    status TEXT DEFAULT 'pending_creative',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (media_buy_id) REFERENCES media_buys(media_buy_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_media_buys_buyer_ref ON media_buys(buyer_ref);
CREATE INDEX IF NOT EXISTS idx_packages_media_buy ON packages(media_buy_id);
CREATE INDEX IF NOT EXISTS idx_packages_product ON packages(product_id);
```

### 3.2 Deliverables - Phase 3

- [ ] New AdCP schema created
- [ ] Migration script implemented and tested
- [ ] SQLAlchemy models updated
- [ ] Seed data updated with AdCP structure
- [ ] Database migrated successfully
- [ ] Data integrity verified
- [ ] Rollback procedure documented

---

## Phase 4: Testing & Validation

**Duration:** 3-4 days  
**Goal:** Comprehensive testing of AdCP compliance

### 4.1 Testing Strategy

1. **Unit Tests**: Validation logic, individual tools
2. **Integration Tests**: End-to-end package-based flow
3. **Client Tests**: HTTP client testing AdCP workflow
4. **Schema Validation**: Validate against AdCP schemas
5. **Manual Testing**: Discovery endpoints, Claude Desktop integration

### 4.2 Deliverables - Phase 4

- [ ] Unit tests passing (90%+ coverage)
- [ ] Integration tests passing
- [ ] Client workflow tests passing
- [ ] Manual testing checklist completed
- [ ] Schema validation successful
- [ ] Performance benchmarks captured
- [ ] Test documentation created

---

## Phase 5: FastMCP Cloud Deployment

**Duration:** 2-3 days  
**Goal:** Deploy AdCP-compliant server to FastMCP Cloud

### 5.1 Why FastMCP Cloud?

Based on https://fastmcp.cloud:

**Benefits:**
- ✅ **Zero Config MCP Servers**: No complex setup
- ✅ **Serverless at Scale**: Pay per use, no persistent costs
- ✅ **Built-in OAuth**: Security handled automatically
- ✅ **Git-Native CI/CD**: Push to deploy
- ✅ **MCP-Native Analytics**: Request/response tracking
- ✅ **ChatMCP Included**: Test tools in browser
- ✅ **Universal Client Support**: Works with Claude, Cursor, etc.

### 5.2 Deployment Steps

1. **Sign Up**: Create account at https://fastmcp.cloud
2. **Connect Repository**: Link GitHub repo
3. **Create Project**: Select `admcp-media-app` repository
4. **Configure Environment**: Add environment variables
5. **Enable OAuth**: Set up authentication
6. **Deploy**: Push to main branch
7. **Test**: Validate with ChatMCP and Claude Desktop
8. **Monitor**: Use built-in analytics dashboard

### 5.3 Deliverables - Phase 5

- [ ] FastMCP Cloud account created
- [ ] Project deployed successfully
- [ ] Environment variables configured
- [ ] OAuth enabled and tested
- [ ] Production URLs updated
- [ ] Claude Desktop integration working
- [ ] ChatMCP testing completed
- [ ] Analytics dashboard reviewed
- [ ] Deployment documentation created

---

## Phase 6: Salesforce Data Cloud Migration

**Duration:** 5-7 days  
**Goal:** Migrate database from SQLite to Salesforce Data Cloud

### 6.1 Why Salesforce Data Cloud?

**Benefits:**
- ✅ **Enterprise Data Platform**: Scalable, secure, compliant
- ✅ **Unified Customer Data**: Integrate with Salesforce ecosystem
- ✅ **AI-Ready**: Native Einstein AI integration
- ✅ **Real-Time**: Streaming data ingestion
- ✅ **Governance**: Data lineage, privacy controls
- ✅ **Analytics**: Built-in reporting and insights

### 6.2 Implementation Strategy

1. **Create Data Cloud Objects**: Map SQLite tables to Salesforce objects
2. **Implement Data Cloud Service**: API integration layer
3. **Update Services**: Replace SQLAlchemy with Data Cloud API calls
4. **Migrate Data**: Export SQLite, transform, bulk upload
5. **Test & Validate**: Ensure data integrity and performance
6. **Monitor**: Track usage and performance

### 6.3 Deliverables - Phase 6

- [ ] Data Cloud objects created
- [ ] DataCloudService implemented
- [ ] All services updated to use Data Cloud
- [ ] Data migration script created
- [ ] Migration executed successfully
- [ ] Data integrity verified
- [ ] Performance benchmarked
- [ ] Rollback plan documented
- [ ] Data Cloud documentation created

---

## Success Metrics

### Technical Validation

- [ ] `/.well-known/adagents.json` returns 200
- [ ] `/.well-known/agent-card.json` returns valid JSON
- [ ] `create_media_buy` accepts package structure
- [ ] `format_ids` validation enforced
- [ ] `list_creative_formats` returns structured formats
- [ ] All AdCP validation tests pass
- [ ] Claude Desktop can discover agent
- [ ] FastMCP Cloud deployment successful
- [ ] Data Cloud integration working

### Business Validation

- [ ] Nike can create campaigns via AdCP protocol
- [ ] Multiple packages in one media buy
- [ ] Creative requirements clearly specified
- [ ] Performance metrics tracked per package
- [ ] OAuth authentication working
- [ ] Ready for Yahoo proof-of-tech demo

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|-----------------|
| **Phase 1: Discovery** | 3-5 days | `/.well-known/` endpoints |
| **Phase 2: Package-Based** | 5-7 days | Refactored `create_media_buy` |
| **Phase 3: Database** | 3-4 days | AdCP schema migration |
| **Phase 4: Testing** | 3-4 days | Comprehensive validation |
| **Phase 5: FastMCP Cloud** | 2-3 days | Production deployment |
| **Phase 6: Data Cloud** | 5-7 days | Salesforce integration |
| **TOTAL** | **21-30 days** | **Fully AdCP-compliant production system** |

---

## References

- [Ad Context Protocol Documentation](https://docs.adcontextprotocol.org/docs/intro)
- [AdCP GitHub Repository](https://github.com/adcontextprotocol/adcp)
- [AdCP Sales Agent Example](https://github.com/adcontextprotocol/salesagent)
- [AdCP Creative Formats](https://docs.adcontextprotocol.org/docs/creative/formats)
- [FastMCP Cloud](https://fastmcp.cloud)

---

## Next Steps

1. **Review this plan** with Nike and Yahoo stakeholders
2. **Set up development environment** for Phase 1
3. **Schedule checkpoint meetings** after each phase
4. **Prepare FastMCP Cloud account**
5. **Coordinate with Salesforce Data Cloud team**

---

**Document Status:** ✅ Ready for Implementation  
**Last Updated:** November 19, 2025  
**Next Review:** Start of Phase 1

