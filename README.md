# Nike-Yahoo AdCP Media Platform

AI-powered advertising campaign platform built on **Model Context Protocol (MCP)** and **Ad Context Protocol (AdCP)**.

## 🎯 Overview

This project simulates a complete advertising workflow between **Nike** (advertiser) and **Yahoo** (publisher) after a Clean Room has matched their audiences. It demonstrates:

- **850K matched users** from Clean Room audience overlap
- **LLM-powered product discovery** using natural language
- **Real-time campaign performance** tracking
- **Privacy-preserving data collaboration** (post-Clean Room)
- **AdCP Media Buy Protocol** implementation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  Nike Streamlit Client (Phase 3)   │  ← Campaign Manager UI
│  - Product Discovery                │
│  - Campaign Creation                │
│  - Performance Dashboard            │
└──────────────┬──────────────────────┘
               │ MCP Protocol
               ▼
┌─────────────────────────────────────┐
│  Yahoo MCP Server (Phase 2)         │  ← FastMCP + LLM
│  - get_products()                   │
│  - create_media_buy()               │
│  - get_media_buy_delivery()         │
│  - update_media_buy()               │
└──────────────┬──────────────────────┘
               │ SQLAlchemy
               ▼
┌─────────────────────────────────────┐
│  SQLite Database (Phase 1)          │  ← Sample Data
│  - 850K matched users               │
│  - 5 Yahoo products                 │
│  - Active campaigns                 │
│  - 20 days metrics                  │
└─────────────────────────────────────┘
```

---

## 📦 Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ Complete | Database with realistic sample data |
| **Phase 2** | ✅ Files Created | Yahoo MCP Server (ready to run) |
| **Phase 3** | ⏳ Pending | Nike Streamlit Client UI |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- uv (Python package manager)
- SQLite (comes with Python)
- Gemini API key (or OpenAI)

### Phase 1: Database Setup

```bash
# Create database with sample data
rm database/adcp_platform.db  # If exists
python3 database/seed_data.py

# Verify
python3 database/verify_data.py
```

**See:** `DATABASE_SETUP_GUIDE.md` for SQL verification commands.

### Phase 2: Yahoo MCP Server

```bash
cd yahoo_mcp_server
uv sync
cp env.template .env
# Edit .env and add GEMINI_API_KEY
uv run python server.py
```

Server starts on: `http://localhost:8080/`

**See:** `PHASE_2_COMMANDS.md` for detailed setup.

### Phase 3: Nike Client (Coming Soon)

Streamlit web interface for campaign management.

---

## 📊 Sample Data

The database includes realistic data simulating a Nike-Yahoo campaign:

**Matched Audiences (Clean Room Output):**
- Nike Running Enthusiasts × Yahoo Sports: **850,000 users** (56.7% match rate)
- Nike Lifestyle × Yahoo Finance: **450,000 users** (56.3% match rate)
- Nike Athletes × Yahoo Sports Premium: **125,000 users** (62.5% match rate)

**Yahoo Products:**
- Yahoo Sports Display ($12.50 CPM → $10.62 enterprise)
- Yahoo Sports Video ($18.00 CPM)
- Yahoo Finance Display ($24.00 CPM)
- Yahoo Finance CTV ($35.00 CPM)
- Yahoo Sports Native ($16.00 CPM)

**Active Campaign:**
- Campaign: Nike Air Max Spring Q1
- Budget: $50,000 | Spent: $24,500 (49%)
- Impressions: 8.5M | Clicks: 35.7K (0.42% CTR)
- Conversions: 1,428 (4% CVR)

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **MCP Server** | FastMCP (Python) |
| **Database** | SQLite → PostgreSQL → Snowflake |
| **LLM** | Gemini 1.5 Pro (primary), OpenAI GPT-4 (fallback) |
| **Client** | Streamlit (Phase 3) |
| **ORM** | SQLAlchemy |
| **Package Manager** | uv |
| **Protocol** | AdCP v2.3.0, MCP |

---

## 📚 Documentation

### Setup Guides
- **`DATABASE_SETUP_GUIDE.md`** - Quick database setup with SQL commands
- **`BUILD_PHASE_1_DATABASE.md`** - Complete database setup guide
- **`PHASE_2_COMMANDS.md`** - Yahoo MCP Server setup
- **`GIT_SETUP_COMMANDS.md`** - Git initialization and best practices

### Project Documentation
- **`PROJECT_STATUS.md`** - Overall project status and roadmap
- **`README_Media_Workflow.md`** - Original specification (2,452 lines)
- **`BUILD_PHASE_2_MCP_SERVER.md`** - MCP Server build notes
- **`PHASE_2_COMPLETE.md`** - Phase 2 summary

### API Documentation
- **`yahoo_mcp_server/README.md`** - MCP Server API reference

---

## 🎯 Key Features

### LLM-Powered Product Discovery
Natural language campaign briefs automatically matched to relevant inventory:

```python
# Example request
brief = "Display ads for sports enthusiasts interested in running gear, 
         targeting US users aged 25-45, budget $50,000"

# Returns matched Yahoo products with audience overlap data
```

### Real-time Performance Tracking
```json
{
  "impressions": 8500000,
  "clicks": 35700,
  "ctr": 0.42,
  "conversions": 1428,
  "pacing": "on_track"
}
```

### Matched Audience Integration
Every product shows Clean Room audience overlap:
- Overlap count (850K users)
- Match rate (56.7%)
- Engagement score (0.85)
- Demographics (age, gender, income)
- Privacy parameters (k-anonymity, differential privacy)

---

## 🔐 Security & Privacy

### Authentication
- Bearer token authentication (`nike_token_12345` for testing)
- Principal-based access control
- Enterprise pricing tiers (15% discount)

### Privacy
- Clean Room output only (no PII)
- k-anonymity enforced (min 1000 users)
- Differential privacy (ε=0.1)
- Aggregated demographics only

### Git Security
- `.env` files excluded via `.gitignore`
- No API keys in committed code
- Test tokens clearly marked

---

## 🧪 Testing

### Test Database
```bash
# Count records
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM products;"

# View matched audiences
sqlite3 database/adcp_platform.db "SELECT segment_name, overlap_count FROM matched_audiences;"

# Check active campaigns
sqlite3 database/adcp_platform.db "SELECT media_buy_id, status FROM media_buys;"
```

### Test MCP Server
```bash
# List available tools
curl http://localhost:8080/tools/list

# Discover products
curl -X POST http://localhost:8080/tools/call \
  -H "x-adcp-auth: Bearer nike_token_12345" \
  -H "Content-Type: application/json" \
  -d '{"name":"get_products","arguments":{"brief":"running shoes display ads"}}'
```

---

## 📁 Project Structure

```
admcp-media-app/
├── database/                      # Phase 1: Sample data
│   ├── adcp_platform.db          # SQLite database (144 KB)
│   ├── schema.sql                # Database schema
│   ├── seed_data.py              # Data generator
│   └── verify_data.py            # Inspection tool
│
├── yahoo_mcp_server/             # Phase 2: MCP Server
│   ├── server.py                 # FastMCP entry point
│   ├── models.py                 # SQLAlchemy ORM
│   ├── services/                 # Business logic
│   │   ├── product_service.py    # LLM discovery
│   │   ├── media_buy_service.py  # Campaign mgmt
│   │   └── metrics_service.py    # Performance
│   ├── utils/                    # Utilities
│   │   ├── auth.py               # Authentication
│   │   └── llm_client.py         # Gemini/OpenAI
│   └── pyproject.toml            # uv config
│
├── nike_mcp_client/              # Phase 3: Streamlit UI (pending)
│
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
├── PROJECT_STATUS.md             # Project status
├── DATABASE_SETUP_GUIDE.md       # Quick setup guide
└── [other documentation]
```

---

## 🔄 Migration Path

### Current: SQLite (Local)
- File-based database
- Perfect for development
- 144 KB with sample data

### Next: PostgreSQL (Server)
- Production-ready
- Better concurrency
- JSON support

### Future: Snowflake/BigQuery (Warehouse)
- Analytics at scale
- Clean Room integration
- Data sharing capabilities

---

## 🤝 Contributing

This is a proof-of-concept for Nike-Yahoo advertising workflows.

### Development Workflow
1. Create feature branch: `git checkout -b feature-name`
2. Make changes
3. Test locally
4. Commit: `git commit -m "Add feature X"`
5. Push: `git push origin feature-name`

### Code Style
- Python: Follow PEP 8
- SQL: Uppercase keywords
- Commits: Descriptive messages

---

## 📖 References

- **AdCP Specification**: https://adcontextprotocol.org
- **Model Context Protocol**: https://modelcontextprotocol.io
- **FastMCP**: https://github.com/jlowin/fastmcp
- **Original Spec**: `README_Media_Workflow.md`

---

## 📝 License

Internal use only - Nike & Yahoo collaboration demo.

---

## 👥 Contact

For questions about this implementation:
- Phase 1 (Database): See `BUILD_PHASE_1_DATABASE.md`
- Phase 2 (MCP Server): See `yahoo_mcp_server/README.md`
- Git Setup: See `GIT_SETUP_COMMANDS.md`

---

**Version**: 1.0.0
**Last Updated**: November 17, 2025
**Status**: Phase 1 ✅ | Phase 2 ✅ Files Created | Phase 3 ⏳ Pending

