# Database Setup - Quick Reference Guide

## 🎯 Goal
Create SQLite database with realistic Nike-Yahoo campaign data (post-Clean Room workflow).

---

## 📋 Setup Steps

### Step 1: Navigate to Project
```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app
```

### Step 2: Delete Old Database (If Exists)
```bash
rm database/adcp_platform.db
```
**Why?** Prevents UNIQUE constraint errors from duplicate data.

### Step 3: Create & Populate Database
```bash
python3 database/seed_data.py
```

### Step 4: Verify Creation
```bash
ls -lh database/adcp_platform.db
```
Should show: **~144 KB file**

### Step 5: Inspect Data
```bash
python3 database/verify_data.py
```

---

## 🔍 SQL Verification

### Quick Check: Count All Records
```bash
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM tenants;"           # 1
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM principals;"        # 1
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM matched_audiences;" # 3
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM products;"          # 5
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM media_buys;"        # 2
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM creatives;"         # 3
sqlite3 database/adcp_platform.db "SELECT COUNT(*) FROM delivery_metrics;"  # 20
```

### Interactive SQL Session
```bash
sqlite3 database/adcp_platform.db
```

**Enable better formatting:**
```sql
.mode column
.headers on
```

**View matched audiences (Clean Room output):**
```sql
SELECT segment_name, overlap_count, engagement_score 
FROM matched_audiences 
ORDER BY overlap_count DESC;
```

**View products:**
```sql
SELECT product_id, name, product_type, 
       json_extract(pricing, '$.value') as cpm,
       matched_reach
FROM products 
ORDER BY matched_reach DESC;
```

**View active campaigns:**
```sql
SELECT media_buy_id, status, total_budget, spend,
       impressions_delivered, clicks,
       ROUND(clicks * 100.0 / impressions_delivered, 2) as ctr
FROM media_buys
WHERE status = 'active';
```

**View recent metrics:**
```sql
SELECT date, 
       SUM(impressions) as impressions,
       SUM(clicks) as clicks,
       ROUND(SUM(spend), 2) as spend
FROM delivery_metrics
GROUP BY date
ORDER BY date DESC
LIMIT 7;
```

**View authentication credentials:**
```sql
SELECT name, principal_id, auth_token, access_level
FROM principals;
```

**Exit:**
```sql
.quit
```

---

## 📊 What's in the Database

| Table | Records | Description |
|-------|---------|-------------|
| `tenants` | 1 | Yahoo Publisher |
| `principals` | 1 | Nike (token: `nike_token_12345`) |
| `matched_audiences` | 3 | Clean Room output (850K, 450K, 125K users) |
| `products` | 5 | Yahoo ad inventory (Display, Video, CTV, Native) |
| `media_buys` | 2 | 1 active campaign, 1 pending |
| `creatives` | 3 | Nike ad assets |
| `delivery_metrics` | 20 | 20 days of performance data |
| `audit_log` | 0 | Will be populated by MCP server |

---

## 🔑 Key Data Points

**Authentication:**
- Principal: `nike_advertiser`
- Token: `nike_token_12345`
- Access Level: `enterprise` (15% discount)

**Top Matched Audience:**
- Segment: Nike Running Enthusiasts × Yahoo Sports
- Overlap: 850,000 users
- Match Rate: 56.7%
- Engagement: 0.85

**Active Campaign:**
- Campaign: `nike_air_max_spring_q1`
- Budget: $50,000 | Spent: $24,500 (49%)
- Impressions: 8.5M | Clicks: 35.7K (0.42% CTR)
- Conversions: 1,428 (4% CVR)

---

## ⚠️ Common Issues

### Issue 1: "UNIQUE constraint failed"
```
sqlite3.IntegrityError: UNIQUE constraint failed: tenants.slug
```
**Cause:** Database already exists
**Fix:**
```bash
rm database/adcp_platform.db
python3 database/seed_data.py
```

### Issue 2: Database file not found
**Cause:** Running commands from wrong directory
**Fix:**
```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app
python3 database/seed_data.py
```

### Issue 3: "No module named 'sqlite3'"
**Cause:** SQLite not available (very rare)
**Fix:** SQLite comes with Python 3.10+. Check: `python3 --version`

---

## 💾 Database File Details

**Location:** `database/adcp_platform.db`
**Type:** SQLite 3
**Size:** ~144 KB
**Tables:** 8
**Engine:** SQLite (no server needed, file-based)

---

## 🧪 Test Queries for Development

### Get all products with matched audiences:
```sql
SELECT 
    p.product_id,
    p.name,
    p.matched_reach,
    json_extract(p.pricing, '$.value') as cpm
FROM products p
WHERE p.is_active = 1;
```

### Campaign performance summary:
```sql
SELECT 
    mb.media_buy_id,
    mb.total_budget,
    mb.spend,
    ROUND((mb.spend / mb.total_budget) * 100, 1) as pacing,
    mb.impressions_delivered,
    ROUND(mb.clicks * 100.0 / mb.impressions_delivered, 2) as ctr,
    ROUND(mb.conversions * 100.0 / mb.clicks, 2) as cvr
FROM media_buys mb
WHERE mb.status = 'active';
```

### Matched audience demographics:
```sql
SELECT 
    segment_id,
    segment_name,
    overlap_count,
    demographics
FROM matched_audiences
WHERE segment_id = 'nike_running_yahoo_sports';
```

---

## 📖 Full Documentation

For detailed information, see:
- **`BUILD_PHASE_1_DATABASE.md`** - Complete setup guide with all SQL examples
- **`database/schema.sql`** - Database schema definition
- **`database/seed_data.py`** - Data generation logic
- **`database/verify_data.py`** - Formatted data inspection

---

## ✅ Verification Checklist

- [ ] Database file created (~144 KB)
- [ ] 8 tables exist
- [ ] 1 Yahoo tenant
- [ ] 1 Nike principal with token
- [ ] 3 matched audiences (850K, 450K, 125K)
- [ ] 5 products (all with matched_reach > 0)
- [ ] 2 media buys (1 active)
- [ ] 3 creatives (all approved)
- [ ] 20 delivery metrics
- [ ] Can query with SQLite
- [ ] Verification script runs successfully

---

## ⏭️ Next Steps

Once database is verified:
1. ✅ Database ready
2. ➡️ Setup Yahoo MCP Server (Phase 2)
3. ⏳ Build Nike Streamlit Client (Phase 3)

See: **`PHASE_2_COMMANDS.md`** for MCP Server setup.

