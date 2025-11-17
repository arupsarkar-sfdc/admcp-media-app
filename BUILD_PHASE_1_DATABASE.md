# Phase 1: Database Setup - Build Process

## Overview
Setting up SQLite database with realistic sample data simulating post-Clean Room workflow for Nike-Yahoo AdCP platform.

## Database Choice
- **Local Development**: SQLite (file-based, no server needed)
- **Migration Path**: PostgreSQL → Snowflake/BigQuery later
- **File Location**: `database/adcp_platform.db`

## Schema Design

### Core Tables

#### 1. **tenants** - Yahoo Publishers
Represents Yahoo's different properties (Sports, Finance, etc.)

#### 2. **principals** - Advertisers (Nike, etc.)
Authenticated entities with access levels and tokens

#### 3. **matched_audiences** - Clean Room Output
**KEY TABLE**: Stores pre-matched audience segments from Clean Room
- Represents Nike customers ∩ Yahoo users overlap
- Includes aggregated demographics (no PII)
- Used by product discovery for realistic reach estimates

#### 4. **products** - Ad Inventory
Yahoo's advertising products (Display, Video, Native)
- References matched_audiences for targeting
- Principal-specific pricing

#### 5. **media_buys** - Active Campaigns
Nike's campaigns with budget, dates, targeting

#### 6. **creatives** - Ad Assets
Nike's creative files (images, videos)

#### 7. **delivery_metrics** - Performance Data
Daily/hourly campaign performance metrics

#### 8. **audit_log** - Compliance Tracking
All MCP operations logged

## Realistic Sample Data

### Yahoo Properties
- **Yahoo Sports**: Sports enthusiasts, runners, fitness
- **Yahoo Finance**: Affluent, professionals, investors
- **Yahoo Entertainment**: General audience, lifestyle

### Nike Principal
- **principal_id**: `nike_advertiser`
- **Access Level**: `enterprise` (15% discount)
- **Auth Token**: `nike_token_12345` (static for POC)

### Matched Audiences (Clean Room Results)
Simulating 3 key segments:

1. **Nike Running Enthusiasts ∩ Yahoo Sports**
   - Overlap: 850,000 users
   - Demographics: Age 25-45, 60% male, HHI $75K+
   - Engagement: High (0.85 score)

2. **Nike Professional Athletes ∩ Yahoo Sports Premium**
   - Overlap: 125,000 users
   - Demographics: Age 18-35, 55% male, HHI $100K+
   - Engagement: Very High (0.92 score)

3. **Nike Lifestyle ∩ Yahoo Finance**
   - Overlap: 450,000 users
   - Demographics: Age 30-55, 50% male, HHI $85K+
   - Engagement: Medium (0.68 score)

### Products (5 Ad Products)

1. **Yahoo Sports - Display (Sports Enthusiasts)**
   - CPM: $12.50 (enterprise: $10.63)
   - Reach: 2.3M (850K matched)
   - Formats: 300x250, 728x90

2. **Yahoo Sports - Video Pre-roll**
   - CPM: $18.00 (enterprise: $15.30)
   - Reach: 1.2M (850K matched)
   - Format: 15s/30s video

3. **Yahoo Finance - Premium Display**
   - CPM: $24.00 (enterprise: $20.40)
   - Reach: 900K (450K matched)
   - Formats: 300x250, 970x250

4. **Yahoo Finance - CTV Video**
   - CPM: $35.00 (enterprise: $29.75)
   - Reach: 600K (450K matched)
   - Format: 15s/30s CTV

5. **Yahoo Sports - Native Ads**
   - CPM: $16.00 (enterprise: $13.60)
   - Reach: 1.8M (850K matched)
   - Format: Native

### Active Campaigns

1. **Nike Air Max Spring Q1**
   - Status: `active`
   - Budget: $50,000
   - Dates: Jan 15 - Apr 15, 2025
   - Products: Yahoo Sports Display
   - Performance: 8.5M impressions, $24,500 spend, 0.42% CTR

2. **Nike Running Gear Test**
   - Status: `pending`
   - Budget: $15,000
   - Dates: Feb 1 - Feb 28, 2025
   - Products: Yahoo Sports Video

### Creatives (Nike Assets)

1. **Nike Air Max 300x250** (Display - Medium Rectangle)
2. **Nike Running Leaderboard 728x90** (Display - Banner)
3. **Nike Just Do It 15s** (Video)

### Delivery Metrics (20 days of data)

For active campaign "Nike Air Max Spring Q1":
- Daily impressions: 300K-500K
- Daily spend: $1,000-$1,500
- CTR: 0.38%-0.48% (realistic variance)
- Conversions: 80-150 per day
- Peak performance on weekends

## Build Steps

### Prerequisites

Before starting, ensure you have:
- Python 3.10+ installed (`python3 --version`)
- SQLite (comes with Python, no separate install needed)

### Step 1: Navigate to Project Directory

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app
```

### Step 2: Verify Database Files Exist

```bash
ls -la database/
```

You should see:
- ✅ `schema.sql` - Database schema definition
- ✅ `seed_data.py` - Data generation script
- ✅ `verify_data.py` - Inspection tool

### Step 3: Delete Old Database (If Exists)

**Important**: If you've run this before, delete the old database first to avoid conflicts.

```bash
rm database/adcp_platform.db
```

**Why?** SQLite databases are files. Re-running the seed script on an existing database will cause UNIQUE constraint errors.

### Step 4: Create & Populate Database

```bash
python3 database/seed_data.py
```

**Expected Output:**
```
============================================================
SEEDING DATABASE - NIKE-YAHOO ADCP PLATFORM
============================================================

✓ Database initialized with schema

✓ Seeded tenant: Yahoo Publisher (ID: ...)
✓ Seeded principal: Nike (ID: ..., Token: nike_token_12345)
✓ Seeded 3 matched audiences (Clean Room output)
✓ Seeded 5 products
✓ Seeded 3 creatives
✓ Seeded 2 media buys (1 active, 1 pending)
✓ Seeded 20 delivery metrics (20 days)

============================================================
DATABASE SEEDING COMPLETE
============================================================
```

**Common Errors:**

❌ **Error**: `UNIQUE constraint failed: tenants.slug`
- **Cause**: Database already exists with data
- **Fix**: Run `rm database/adcp_platform.db` and try again

❌ **Error**: `No module named 'sqlite3'`
- **Cause**: SQLite not available (rare)
- **Fix**: SQLite comes with Python, ensure Python 3.10+ installed

### Step 5: Verify Database File Created

```bash
ls -lh database/adcp_platform.db
```

**Expected Output:**
```
-rw-r--r--  1 arup.sarkar  staff   144K Nov 17 10:19 database/adcp_platform.db
```

File size should be approximately **144 KB**.

### Step 6: Inspect Data with Verification Script

```bash
python3 database/verify_data.py
```

This provides a formatted view of:
- Matched audiences with overlap counts
- Products with pricing
- Active campaigns with performance metrics
- Recent delivery data

## SQL Verification Commands

### Method 1: Using SQLite Command Line

#### Open Database
```bash
sqlite3 database/adcp_platform.db
```

#### Basic SQL Commands

**List all tables:**
```sql
.tables
```

**Expected Output:**
```
audit_log          delivery_metrics   media_buys         products         
creatives          matched_audiences  principals         tenants
```

**Show table schema:**
```sql
.schema products
```

**Exit SQLite:**
```sql
.quit
```

---

### Method 2: Quick SQL Queries

#### Count Records in Each Table

```bash
# Open database and run query inline
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM tenants;"
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM principals;"
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM matched_audiences;"
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM products;"
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM media_buys;"
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM creatives;"
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM delivery_metrics;"
```

**Expected Output:**
```
1    # tenants
1    # principals
3    # matched_audiences
5    # products
2    # media_buys
3    # creatives
20   # delivery_metrics
```

---

### Method 3: Interactive SQL Session

Open database in interactive mode:
```bash
sqlite3 database/adcp_platform.db
```

Then run these queries:

#### 1. View Matched Audiences (Clean Room Output)

```sql
SELECT 
    segment_name,
    overlap_count,
    match_rate,
    engagement_score
FROM matched_audiences
ORDER BY overlap_count DESC;
```

**Expected Output:**
```
Nike Running Enthusiasts × Yahoo Sports|850000|0.567|0.85
Nike Lifestyle × Yahoo Finance Readers|450000|0.563|0.68
Nike Professional Athletes × Yahoo Sports Premium|125000|0.625|0.92
```

#### 2. View Products with Pricing

```sql
SELECT 
    product_id,
    name,
    product_type,
    json_extract(pricing, '$.value') as cpm,
    estimated_reach,
    matched_reach
FROM products
ORDER BY matched_reach DESC;
```

**Expected Output:**
```
yahoo_sports_display_enthusiasts|Yahoo Sports - Display (Sports Enthusiasts)|display|12.5|2300000|850000
yahoo_sports_video_preroll|Yahoo Sports - Video Pre-roll|video|18.0|1200000|850000
yahoo_sports_native|Yahoo Sports - Native Ads|native|16.0|1800000|850000
yahoo_finance_display_premium|Yahoo Finance - Premium Display|display|24.0|900000|450000
yahoo_finance_ctv_video|Yahoo Finance - CTV Video|ctv|35.0|600000|450000
```

#### 3. View Active Campaigns

```sql
SELECT 
    media_buy_id,
    status,
    total_budget,
    spend,
    impressions_delivered,
    clicks,
    ROUND(clicks * 100.0 / impressions_delivered, 2) as ctr_percent
FROM media_buys
ORDER BY created_at DESC;
```

**Expected Output:**
```
nike_running_gear_test|pending|15000.0|0.0|0|0|
nike_air_max_spring_q1|active|50000.0|24500.0|8500000|35700|0.42
```

#### 4. View Recent Delivery Metrics (Last 7 Days)

```sql
SELECT 
    date,
    SUM(impressions) as impressions,
    SUM(clicks) as clicks,
    ROUND(SUM(spend), 2) as spend,
    SUM(conversions) as conversions,
    ROUND(SUM(clicks) * 100.0 / SUM(impressions), 2) as ctr_percent
FROM delivery_metrics
GROUP BY date
ORDER BY date DESC
LIMIT 7;
```

#### 5. View Principal Authentication

```sql
SELECT 
    name,
    principal_id,
    auth_token,
    access_level
FROM principals;
```

**Expected Output:**
```
Nike|nike_advertiser|nike_token_12345|enterprise
```

#### 6. View Matched Audience Demographics (JSON)

```sql
SELECT 
    segment_name,
    demographics
FROM matched_audiences
WHERE segment_id = 'nike_running_yahoo_sports';
```

This shows the JSON demographics data from Clean Room.

#### 7. Performance Summary Query

```sql
SELECT 
    mb.media_buy_id,
    mb.total_budget,
    mb.spend,
    ROUND((mb.spend / mb.total_budget) * 100, 1) as budget_pacing_percent,
    mb.impressions_delivered,
    mb.clicks,
    mb.conversions,
    ROUND(mb.clicks * 100.0 / mb.impressions_delivered, 2) as ctr,
    ROUND(mb.conversions * 100.0 / mb.clicks, 2) as cvr
FROM media_buys mb
WHERE mb.status = 'active';
```

---

### Method 4: Export Data to CSV

Export any table to CSV for analysis:

```bash
# Export products
sqlite3 -header -csv database/adcp_platform.db "SELECT * FROM products;" > products.csv

# Export delivery metrics
sqlite3 -header -csv database/adcp_platform.db "SELECT * FROM delivery_metrics;" > metrics.csv

# Export matched audiences
sqlite3 -header -csv database/adcp_platform.db "SELECT * FROM matched_audiences;" > audiences.csv
```

---

### Method 5: Pretty Print with Python (Verification Script)

For formatted, human-readable output:

```bash
python3 database/verify_data.py
```

This shows a nicely formatted report with all key data.

---

## SQLite Tips & Tricks

### Enable Better Formatting

When in SQLite interactive mode, run these commands for better output:

```sql
.mode column          -- Columnar output
.headers on           -- Show column headers
.width 20 15 10       -- Set column widths
```

### Common SQLite Commands

| Command | Description |
|---------|-------------|
| `.tables` | List all tables |
| `.schema TABLE_NAME` | Show table structure |
| `.mode csv` | Switch to CSV output |
| `.mode column` | Switch to columnar output |
| `.headers on` | Show column headers |
| `.quit` or `.exit` | Exit SQLite |
| `.help` | Show all commands |

### Backup Database

```bash
# Create backup
cp database/adcp_platform.db database/adcp_platform_backup.db

# Or use SQLite backup
sqlite3 database/adcp_platform.db ".backup database/adcp_platform_backup.db"
```

---

## Verification Checklist

After running seed script, verify:

- [ ] Database file exists (`ls -lh database/adcp_platform.db`)
- [ ] File size is ~144 KB
- [ ] 8 tables created (`.tables`)
- [ ] 1 tenant (Yahoo)
- [ ] 1 principal (Nike with token)
- [ ] 3 matched audiences (850K, 450K, 125K users)
- [ ] 5 products (Display, Video, CTV, Native)
- [ ] 2 media buys (1 active, 1 pending)
- [ ] 3 creatives
- [ ] 20 delivery metrics records

## Database Summary

✅ **Successfully Created**:
- **Database File**: `database/adcp_platform.db` (144 KB)
- **Tenants**: 1 (Yahoo Publisher)
- **Principals**: 1 (Nike with token `nike_token_12345`)
- **Matched Audiences**: 3 segments (850K, 450K, 125K users)
- **Products**: 5 ad products (Display, Video, CTV, Native)
- **Media Buys**: 2 campaigns (1 active with 8.5M impressions, 1 pending)
- **Creatives**: 3 Nike assets
- **Delivery Metrics**: 20 days of performance data

### Key Highlights:

**Authentication**:
```
Principal ID: nike_advertiser
Auth Token: nike_token_12345
Access Level: Enterprise (15% discount)
```

**Top Matched Audience**:
- Nike Running Enthusiasts × Yahoo Sports
- 850,000 overlapping users
- 56.7% match rate
- 0.85 engagement score

**Active Campaign**:
- Nike Air Max Spring Q1
- Budget: $50,000 | Spend: $24,500 (49%)
- 8.5M impressions | 35.7K clicks (0.42% CTR)
- 1,428 conversions (4% CVR)

## Next Phase
**Phase 2: Yahoo MCP Server (FastMCP)**
- Implement AdCP tools (get_products, create_media_buy, etc.)
- LLM-powered product discovery with Gemini/OpenAI
- Real-time delivery metrics
- Principal authentication

---
**Build Status**: ✅ COMPLETED
**Duration**: ~5 minutes
**Database Path**: `database/adcp_platform.db`

