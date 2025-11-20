# SQLite to Snowflake Migration Guide

**Purpose**: Migrate AdCP data from local SQLite to Snowflake for production deployment

---

## Prerequisites

### 1. Snowflake Account Setup

```sql
-- In Snowflake Web UI or SnowSQL

-- Create database
CREATE DATABASE NIKE_YAHOO_ADCP;

-- Create schema
CREATE SCHEMA PRODUCTION;

-- Create warehouse for queries
CREATE WAREHOUSE ADCP_QUERY_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 2;

-- Create service user for migration
CREATE USER migration_user
    PASSWORD = 'secure_password_here'
    DEFAULT_WAREHOUSE = ADCP_QUERY_WH
    DEFAULT_NAMESPACE = NIKE_YAHOO_ADCP.PRODUCTION;

-- Grant permissions
GRANT USAGE ON WAREHOUSE ADCP_QUERY_WH TO USER migration_user;
GRANT ALL ON DATABASE NIKE_YAHOO_ADCP TO USER migration_user;
GRANT ALL ON SCHEMA NIKE_YAHOO_ADCP.PRODUCTION TO USER migration_user;
```

### 2. Install Python Dependencies

```bash
cd database
pip install snowflake-connector-python python-dotenv
```

### 3. Configure Environment Variables

```bash
# Copy template
cp snowflake.env.template .env

# Edit .env with your Snowflake credentials
nano .env
```

**Required Variables**:
```
SNOWFLAKE_ACCOUNT=nike_adcp.us-west-2.aws
SNOWFLAKE_USER=migration_user
SNOWFLAKE_PASSWORD=secure_password_here
SNOWFLAKE_DATABASE=NIKE_YAHOO_ADCP
SNOWFLAKE_SCHEMA=PRODUCTION
SNOWFLAKE_WAREHOUSE=ADCP_QUERY_WH
```

---

## Migration Steps

### Step 1: Verify SQLite Data

```bash
# Check SQLite database has data
sqlite3 adcp_platform.db "SELECT COUNT(*) FROM tenants;"
sqlite3 adcp_platform.db "SELECT COUNT(*) FROM products;"
sqlite3 adcp_platform.db "SELECT COUNT(*) FROM media_buys;"
```

### Step 2: Run Migration Script

```bash
cd database
python migrate_sqlite_to_snowflake.py
```

**Expected Output**:
```
======================================================================
SQLite → Snowflake Migration
======================================================================

🔌 Connecting to Snowflake...
✅ Connected to Snowflake: NIKE_YAHOO_ADCP.PRODUCTION

🔌 Connecting to SQLite: adcp_platform.db
✅ Connected to SQLite

📋 Creating Snowflake tables...
   ✓ Created 'tenants' table
   ✓ Created 'principals' table
   ✓ Created 'matched_audiences' table (with contact_id column)
   ✓ Created 'products' table
   ✓ Created 'creatives' table
   ✓ Created 'media_buys' table
   ✓ Created 'packages' table
   ✓ Created 'package_formats' table
   ✓ Created 'delivery_metrics' table
   ✓ Created 'audit_log' table

✅ All tables created successfully

📝 Adding contact_id column to matched_audiences...
   ✓ contact_id column already exists

======================================================================
Migrating Data
======================================================================

📦 Migrating 'tenants'...
   ✓ Migrated 3/3 rows

📦 Migrating 'principals'...
   ✓ Migrated 1/1 rows

📦 Migrating 'matched_audiences'...
   ✓ Migrated 5/5 rows

📦 Migrating 'products'...
   ✓ Migrated 15/15 rows

📦 Migrating 'creatives'...
   ✓ Migrated 0/0 rows

📦 Migrating 'media_buys'...
   ✓ Migrated 16/16 rows

📦 Migrating 'packages'...
   ✓ Migrated 1/1 rows

📦 Migrating 'package_formats'...
   ✓ Migrated 2/2 rows

📦 Migrating 'delivery_metrics'...
   ✓ Migrated 42/42 rows

📦 Migrating 'audit_log'...
   ✓ Migrated 0/0 rows

🔍 Creating clustering keys...
   ✓ Clustered 'products' by tenant_id, is_active
   ✓ Clustered 'media_buys' by tenant_id, status
   ✓ Clustered 'packages' by media_buy_id
   ✓ Clustered 'delivery_metrics' by date, media_buy_id

📊 Verifying migration...
   tenants                          3 rows
   principals                       1 rows
   matched_audiences                5 rows
   products                        15 rows
   creatives                        0 rows
   media_buys                      16 rows
   packages                         1 rows
   package_formats                  2 rows
   delivery_metrics                42 rows
   audit_log                        0 rows

======================================================================
✅ Migration completed successfully!
======================================================================

📝 Next Steps:
   1. Populate matched_audiences.contact_id with CRM Contact IDs
   2. Configure Data Cloud Zero Copy connection
   3. Define relationships in Data Cloud
   4. Update MCP Server to use Data Cloud API
```

### Step 3: Verify Data in Snowflake

```sql
-- Connect to Snowflake and verify

USE DATABASE NIKE_YAHOO_ADCP;
USE SCHEMA PRODUCTION;

-- Check row counts
SELECT 'tenants' AS table_name, COUNT(*) AS row_count FROM tenants
UNION ALL
SELECT 'principals', COUNT(*) FROM principals
UNION ALL
SELECT 'matched_audiences', COUNT(*) FROM matched_audiences
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'media_buys', COUNT(*) FROM media_buys
UNION ALL
SELECT 'packages', COUNT(*) FROM packages
UNION ALL
SELECT 'package_formats', COUNT(*) FROM package_formats
UNION ALL
SELECT 'delivery_metrics', COUNT(*) FROM delivery_metrics;

-- View sample data
SELECT * FROM media_buys LIMIT 5;
SELECT * FROM packages LIMIT 5;
SELECT * FROM matched_audiences LIMIT 5;

-- Verify contact_id column exists (NULL for now)
SELECT id, segment_name, contact_id 
FROM matched_audiences 
LIMIT 5;
```

---

## Populating contact_id (Later)

The `contact_id` column in `matched_audiences` is **NULL** after migration. You'll populate it later when you have CRM Contact IDs:

```sql
-- Example: Update contact_id with CRM Contact IDs
UPDATE matched_audiences
SET contact_id = '003xx000004TmiOAAS'
WHERE segment_id = 'nike_running_yahoo_sports';

-- Or bulk update from a mapping table
UPDATE matched_audiences ma
SET contact_id = m.crm_contact_id
FROM contact_id_mapping m
WHERE ma.segment_id = m.segment_id;
```

---

## Rollback (If Needed)

If migration fails or you need to start over:

```sql
-- In Snowflake
USE DATABASE NIKE_YAHOO_ADCP;
USE SCHEMA PRODUCTION;

-- Drop all tables
DROP TABLE IF EXISTS package_formats;
DROP TABLE IF EXISTS packages;
DROP TABLE IF EXISTS delivery_metrics;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS media_buys;
DROP TABLE IF EXISTS creatives;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS matched_audiences;
DROP TABLE IF EXISTS principals;
DROP TABLE IF EXISTS tenants;

-- Then re-run migration script
```

---

## Troubleshooting

### Error: "Connection refused"
- Check Snowflake account name format: `account.region.cloud_provider`
- Verify firewall/VPN isn't blocking Snowflake

### Error: "Authentication failed"
- Double-check username and password in `.env`
- Ensure user has correct permissions

### Error: "Database does not exist"
- Create database in Snowflake first (see Prerequisites)

### Error: "Warehouse does not exist"
- Create warehouse in Snowflake first (see Prerequisites)

### Data Mismatch
- Compare row counts: SQLite vs Snowflake
- Check for errors in migration output
- Verify JSON fields parsed correctly

---

## Cost Estimation

**Snowflake Costs** (approximate):

| Resource | Size | Monthly Cost |
|----------|------|--------------|
| Storage (10 GB) | 10 GB | $0.23 |
| X-Small Warehouse | 1 credit/hour | $2/hour |
| **Estimated Total** | 10 hours/month | **~$20/month** |

**Note**: Auto-suspend after 5 minutes of inactivity keeps costs low!

---

## Next Steps After Migration

1. ✅ **Verify data in Snowflake**
2. 🔄 **Populate `contact_id` in `matched_audiences`**
3. 🔄 **Configure Salesforce Data Cloud Zero Copy**
4. 🔄 **Define relationships in Data Cloud**
5. 🔄 **Update MCP Server to use Data Cloud API**
6. 🔄 **Deploy MCP Server to FastMCP Cloud**

---

## Support

For issues or questions:
- Check Snowflake logs in web UI
- Review migration script output
- Verify environment variables
- Contact Snowflake support for account/permission issues

