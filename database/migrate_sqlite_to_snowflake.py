"""
Migrate AdCP Data from SQLite to Snowflake
Creates tables and seeds data for Snowflake-First architecture

Usage:
    python migrate_sqlite_to_snowflake.py

Environment Variables Required:
    SNOWFLAKE_ACCOUNT=nike_adcp.us-west-2.snowflakecomputing.com
    SNOWFLAKE_USER=your_username
    SNOWFLAKE_PASSWORD=your_password
    SNOWFLAKE_DATABASE=NIKE_YAHOO_ADCP
    SNOWFLAKE_SCHEMA=PRODUCTION
    SNOWFLAKE_WAREHOUSE=ADCP_QUERY_WH
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment
load_dotenv()

try:
    import snowflake.connector
    from snowflake.connector import DictCursor
except ImportError:
    print("❌ Snowflake connector not installed")
    print("   Install with: pip install snowflake-connector-python")
    exit(1)


class SQLiteToSnowflakeMigration:
    """Migrate AdCP data from SQLite to Snowflake"""
    
    def __init__(self, sqlite_path: str = "adcp_platform.db"):
        self.sqlite_path = sqlite_path
        self.snowflake_conn = None
        self.sqlite_conn = None
        
    def connect_snowflake(self):
        """Connect to Snowflake"""
        print("\n🔌 Connecting to Snowflake...")
        
        connect_params = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE")
        }
        
        # Add role if specified
        if os.getenv("SNOWFLAKE_ROLE"):
            connect_params["role"] = os.getenv("SNOWFLAKE_ROLE")
        
        self.snowflake_conn = snowflake.connector.connect(**connect_params)
        
        print(f"✅ Connected to Snowflake: {os.getenv('SNOWFLAKE_DATABASE')}.{os.getenv('SNOWFLAKE_SCHEMA')}")
    
    def connect_sqlite(self):
        """Connect to SQLite"""
        print(f"\n🔌 Connecting to SQLite: {self.sqlite_path}")
        self.sqlite_conn = sqlite3.connect(self.sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        print("✅ Connected to SQLite")
    
    def create_snowflake_tables(self):
        """Create all tables in Snowflake"""
        print("\n📋 Creating Snowflake tables...")
        
        cursor = self.snowflake_conn.cursor()
        
        # Create tenants table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id STRING PRIMARY KEY,
            name STRING NOT NULL UNIQUE,
            slug STRING NOT NULL UNIQUE,
            adapter_type STRING NOT NULL,
            adapter_config VARIANT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            salesforce_account_id STRING,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        print("   ✓ Created 'tenants' table")
        
        # Create principals table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS principals (
            id STRING PRIMARY KEY,
            tenant_id STRING NOT NULL,
            name STRING NOT NULL,
            principal_id STRING NOT NULL,
            auth_token STRING NOT NULL,
            access_level STRING DEFAULT 'standard',
            metadata VARIANT,
            is_active BOOLEAN DEFAULT TRUE,
            salesforce_contact_id STRING,
            salesforce_account_id STRING,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        print("   ✓ Created 'principals' table")
        
        # Create matched_audiences table with contact_id
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS matched_audiences (
            id STRING PRIMARY KEY,
            segment_id STRING NOT NULL UNIQUE,
            segment_name STRING NOT NULL,
            tenant_id STRING NOT NULL,
            principal_id STRING NOT NULL,
            contact_id STRING,
            salesforce_contact_id STRING UNIQUE,
            salesforce_account_id STRING,
            overlap_count INTEGER NOT NULL,
            total_nike_segment INTEGER,
            total_yahoo_segment INTEGER,
            match_rate FLOAT,
            demographics VARIANT NOT NULL,
            engagement_score FLOAT,
            quality_score FLOAT,
            privacy_params VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            expires_at TIMESTAMP_NTZ
        )
        """)
        print("   ✓ Created 'matched_audiences' table (with contact_id column)")
        
        # Create products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id STRING PRIMARY KEY,
            tenant_id STRING NOT NULL,
            product_id STRING NOT NULL,
            name STRING NOT NULL,
            description STRING,
            product_type STRING,
            properties VARIANT NOT NULL,
            formats VARIANT NOT NULL,
            targeting VARIANT,
            matched_audience_ids VARIANT,
            pricing VARIANT NOT NULL,
            minimum_budget FLOAT,
            estimated_reach INTEGER,
            matched_reach INTEGER,
            estimated_impressions INTEGER,
            available_from TIMESTAMP_NTZ,
            available_to TIMESTAMP_NTZ,
            is_active BOOLEAN DEFAULT TRUE,
            principal_access VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        print("   ✓ Created 'products' table")
        
        # Create creatives table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS creatives (
            id STRING PRIMARY KEY,
            tenant_id STRING NOT NULL,
            creative_id STRING NOT NULL,
            principal_id STRING NOT NULL,
            name STRING NOT NULL,
            format STRING NOT NULL,
            file_url STRING NOT NULL,
            preview_url STRING,
            dimensions VARIANT,
            file_size_bytes INTEGER,
            duration_seconds INTEGER,
            approval_status STRING DEFAULT 'approved',
            approval_notes STRING,
            reviewed_by STRING,
            reviewed_at TIMESTAMP_NTZ,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        print("   ✓ Created 'creatives' table")
        
        # Create media_buys table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS media_buys (
            id STRING PRIMARY KEY,
            tenant_id STRING NOT NULL,
            media_buy_id STRING NOT NULL,
            principal_id STRING NOT NULL,
            product_ids VARIANT,
            campaign_name STRING,
            adcp_version STRING DEFAULT '2.3.0',
            salesforce_opportunity_id STRING,
            salesforce_campaign_id STRING,
            total_budget FLOAT NOT NULL,
            currency STRING DEFAULT 'USD',
            flight_start_date DATE NOT NULL,
            flight_end_date DATE NOT NULL,
            targeting VARIANT,
            matched_audience_id STRING,
            assigned_creatives VARIANT,
            status STRING DEFAULT 'pending',
            workflow_state VARIANT,
            impressions_delivered INTEGER DEFAULT 0,
            spend FLOAT DEFAULT 0.0,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            external_campaign_id STRING,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        print("   ✓ Created 'media_buys' table")
        
        # Create packages table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id STRING PRIMARY KEY,
            media_buy_id STRING NOT NULL,
            package_id STRING NOT NULL,
            product_id STRING NOT NULL,
            budget FLOAT NOT NULL,
            currency STRING DEFAULT 'USD',
            pacing STRING DEFAULT 'even',
            pricing_strategy STRING DEFAULT 'cpm',
            targeting_overlay VARIANT,
            impressions_delivered INTEGER DEFAULT 0,
            spend FLOAT DEFAULT 0.0,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        print("   ✓ Created 'packages' table")
        
        # Create package_formats table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS package_formats (
            id STRING PRIMARY KEY,
            package_id STRING NOT NULL,
            agent_url STRING NOT NULL,
            format_id STRING NOT NULL,
            format_name STRING,
            format_type STRING,
            assigned_creative_id STRING,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        print("   ✓ Created 'package_formats' table")
        
        # Create delivery_metrics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS delivery_metrics (
            id STRING PRIMARY KEY,
            media_buy_id STRING NOT NULL,
            package_id STRING,
            date DATE NOT NULL,
            hour INTEGER,
            impressions INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            spend FLOAT DEFAULT 0.0,
            product_id STRING,
            creative_id STRING,
            format_id STRING,
            geo STRING,
            device_type STRING,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        print("   ✓ Created 'delivery_metrics' table")
        
        # Create audit_log table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id STRING PRIMARY KEY,
            principal_id STRING,
            tenant_id STRING,
            operation STRING NOT NULL,
            tool_name STRING,
            request_params VARIANT,
            response_data VARIANT,
            status STRING,
            ip_address STRING,
            user_agent STRING,
            timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        print("   ✓ Created 'audit_log' table")
        
        cursor.close()
        print("\n✅ All tables created successfully")
    
    def migrate_table(self, table_name: str, transform_fn=None, truncate=False):
        """
        Migrate data from SQLite table to Snowflake
        
        Args:
            table_name: Name of the table
            transform_fn: Optional function to transform row data
            truncate: If True, truncate table before inserting
        """
        print(f"\n📦 Migrating '{table_name}'...")
        
        # Check if table already has data
        snowflake_cursor = self.snowflake_conn.cursor()
        snowflake_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        existing_count = snowflake_cursor.fetchone()[0]
        
        if existing_count > 0:
            if truncate:
                print(f"   🗑️  Truncating existing {existing_count} rows...")
                snowflake_cursor.execute(f"TRUNCATE TABLE {table_name}")
            else:
                print(f"   ⚠️  Table already has {existing_count} rows - skipping to avoid duplicates")
                print(f"      Run with truncate=True to replace data")
                snowflake_cursor.close()
                return
        
        # Read from SQLite
        sqlite_cursor = self.sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   ⚠️  No data in '{table_name}'")
            return
        
        # Get column names
        columns = [description[0] for description in sqlite_cursor.description]
        
        migrated_count = 0
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # Apply transformation if provided
            if transform_fn:
                row_dict = transform_fn(row_dict)
            
            # Convert column names to uppercase and prepare values
            upper_row_dict = {}
            for key, value in row_dict.items():
                upper_key = key.upper()
                
                # Convert values for Snowflake
                if value is None:
                    upper_row_dict[upper_key] = None
                elif isinstance(value, (dict, list)):
                    # Convert Python dict/list to JSON string
                    upper_row_dict[upper_key] = json.dumps(value)
                elif isinstance(value, bool):
                    # Convert Python bool to int for Snowflake BOOLEAN
                    upper_row_dict[upper_key] = 1 if value else 0
                else:
                    # Keep everything else as-is
                    upper_row_dict[upper_key] = value
            
            # Identify VARIANT columns that need PARSE_JSON()
            variant_columns = {'adapter_config', 'metadata', 'demographics', 'privacy_params',
                             'properties', 'formats', 'targeting', 'matched_audience_ids',
                             'pricing', 'principal_access', 'dimensions', 'workflow_state',
                             'targeting_overlay', 'request_params', 'response_data', 'product_ids',
                             'assigned_creatives'}
            
            # Build INSERT statement
            # Use SELECT with PARSE_JSON() for VARIANT columns (not VALUES clause)
            # Snowflake requires: INSERT INTO table SELECT PARSE_JSON(%s) for VARIANT
            cols = []
            select_exprs = []
            values = []
            
            for col, val in upper_row_dict.items():
                cols.append(col)
                values.append(val)
                
                # For VARIANT columns, use PARSE_JSON(%s) in SELECT
                if col.lower() in variant_columns and val is not None:
                    select_exprs.append('PARSE_JSON(%s)')
                else:
                    select_exprs.append('%s')
            
            insert_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) SELECT {', '.join(select_exprs)}"
            
            try:
                snowflake_cursor.execute(insert_sql, values)
                migrated_count += 1
            except Exception as e:
                # Log the error and continue
                print(f"   ⚠️  Error inserting row: {str(e)}")
                continue
        
        snowflake_cursor.close()
        print(f"   ✓ Migrated {migrated_count}/{len(rows)} rows")
    
    def add_contact_id_to_matched_audiences(self):
        """
        Ensure matched_audiences has contact_id column
        This will be populated later with CRM Contact IDs
        """
        print("\n📝 Adding contact_id column to matched_audiences...")
        
        cursor = self.snowflake_conn.cursor()
        
        # Check if column exists
        cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'MATCHED_AUDIENCES'
          AND COLUMN_NAME = 'CONTACT_ID'
        """)
        
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            print("   ✓ contact_id column already exists")
        else:
            cursor.execute("""
            ALTER TABLE matched_audiences 
            ADD COLUMN contact_id STRING
            """)
            print("   ✓ Added contact_id column (NULL, to be populated later)")
        
        cursor.close()
    
    def create_indexes(self):
        """Create clustering keys for performance"""
        print("\n🔍 Creating clustering keys...")
        
        cursor = self.snowflake_conn.cursor()
        
        cursor.execute("ALTER TABLE products CLUSTER BY (tenant_id, is_active)")
        print("   ✓ Clustered 'products' by tenant_id, is_active")
        
        cursor.execute("ALTER TABLE media_buys CLUSTER BY (tenant_id, status)")
        print("   ✓ Clustered 'media_buys' by tenant_id, status")
        
        cursor.execute("ALTER TABLE packages CLUSTER BY (media_buy_id)")
        print("   ✓ Clustered 'packages' by media_buy_id")
        
        cursor.execute("ALTER TABLE delivery_metrics CLUSTER BY (date, media_buy_id)")
        print("   ✓ Clustered 'delivery_metrics' by date, media_buy_id")
        
        cursor.close()
    
    def verify_migration(self):
        """Verify data was migrated successfully"""
        print("\n📊 Verifying migration...")
        
        cursor = self.snowflake_conn.cursor()
        
        tables = [
            "tenants",
            "principals",
            "matched_audiences",
            "products",
            "creatives",
            "media_buys",
            "packages",
            "package_formats",
            "delivery_metrics",
            "audit_log"
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table:25} {count:>6} rows")
        
        cursor.close()
    
    def run(self, truncate=False):
        """
        Run complete migration
        
        Args:
            truncate: If True, truncate existing data before migration
        """
        print("="*70)
        print("SQLite → Snowflake Migration")
        if truncate:
            print("MODE: TRUNCATE AND REPLACE")
        else:
            print("MODE: SKIP IF DATA EXISTS")
        print("="*70)
        
        try:
            # Connect to both databases
            self.connect_snowflake()
            self.connect_sqlite()
            
            # Create Snowflake tables
            self.create_snowflake_tables()
            
            # Ensure contact_id column exists
            self.add_contact_id_to_matched_audiences()
            
            # Migrate data
            print("\n" + "="*70)
            print("Migrating Data")
            print("="*70)
            
            self.migrate_table("tenants", truncate=truncate)
            self.migrate_table("principals", truncate=truncate)
            self.migrate_table("matched_audiences", truncate=truncate)
            self.migrate_table("products", truncate=truncate)
            self.migrate_table("creatives", truncate=truncate)
            self.migrate_table("media_buys", truncate=truncate)
            self.migrate_table("packages", truncate=truncate)
            self.migrate_table("package_formats", truncate=truncate)
            self.migrate_table("delivery_metrics", truncate=truncate)
            self.migrate_table("audit_log", truncate=truncate)
            
            # Create indexes
            self.create_indexes()
            
            # Verify migration
            self.verify_migration()
            
            # Commit
            self.snowflake_conn.commit()
            
            print("\n" + "="*70)
            print("✅ Migration completed successfully!")
            print("="*70)
            print("\n📝 Next Steps:")
            print("   1. Populate matched_audiences.contact_id with CRM Contact IDs")
            print("   2. Configure Data Cloud Zero Copy connection")
            print("   3. Define relationships in Data Cloud")
            print("   4. Update MCP Server to use Data Cloud API")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            if self.snowflake_conn:
                self.snowflake_conn.rollback()
            raise
        
        finally:
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.snowflake_conn:
                self.snowflake_conn.close()


if __name__ == "__main__":
    import sys
    
    # Check for required environment variables
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Set them in .env or export them:")
        print("   export SNOWFLAKE_ACCOUNT=your_account.us-west-2")
        print("   export SNOWFLAKE_USER=your_username")
        print("   export SNOWFLAKE_PASSWORD=your_password")
        sys.exit(1)
    
    # Check for truncate flag
    truncate = "--truncate" in sys.argv or "--force" in sys.argv
    
    # Run migration
    migration = SQLiteToSnowflakeMigration()
    migration.run(truncate=truncate)

