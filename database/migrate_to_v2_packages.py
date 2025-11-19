"""
Migration Script: Extract AdCP v2.3.0 Packages from JSON to Normalized Tables
Migrates from schema v1 (JSON packages) to schema v2 (relational packages)

Usage:
    cd database
    python migrate_to_v2_packages.py
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any


def migrate_database(db_path: str = "adcp_platform.db"):
    """
    Migrate database from v1 (JSON packages) to v2 (normalized packages).
    
    Steps:
    1. Create new tables (packages, package_formats)
    2. Extract packages from media_buys.targeting JSON
    3. Insert into normalized tables
    4. Update media_buys table structure
    5. Verify data integrity
    """
    print("="*70)
    print("AdCP Platform - Database Migration v1 → v2")
    print("="*70)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # STEP 1: Create new tables
        print("\n📋 Step 1: Creating new tables...")
        create_new_tables(cursor)
        
        # STEP 2: Add new columns to media_buys
        print("\n📋 Step 2: Updating media_buys table...")
        add_media_buys_columns(cursor)
        
        # STEP 3: Migrate existing data
        print("\n📋 Step 3: Migrating AdCP v2.3.0 campaigns...")
        migrate_campaigns(cursor)
        
        # STEP 4: Verify migration
        print("\n📋 Step 4: Verifying data integrity...")
        verify_migration(cursor)
        
        # Commit transaction
        conn.commit()
        
        print("\n" + "="*70)
        print("✅ Migration completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()


def create_new_tables(cursor):
    """Create packages and package_formats tables"""
    # Packages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id TEXT PRIMARY KEY,
            media_buy_id TEXT NOT NULL,
            package_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            budget REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            pacing TEXT DEFAULT 'even',
            pricing_strategy TEXT DEFAULT 'cpm',
            targeting_overlay TEXT,
            impressions_delivered INTEGER DEFAULT 0,
            spend REAL DEFAULT 0.00,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (media_buy_id) REFERENCES media_buys(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id),
            UNIQUE(media_buy_id, package_id)
        )
    """)
    print("   ✓ Created 'packages' table")
    
    # Package formats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS package_formats (
            id TEXT PRIMARY KEY,
            package_id TEXT NOT NULL,
            agent_url TEXT NOT NULL,
            format_id TEXT NOT NULL,
            format_name TEXT,
            format_type TEXT,
            assigned_creative_id TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_creative_id) REFERENCES creatives(id),
            UNIQUE(package_id, agent_url, format_id)
        )
    """)
    print("   ✓ Created 'package_formats' table")
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_packages_media_buy ON packages(media_buy_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_packages_product ON packages(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_package_formats_package ON package_formats(package_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_package_formats_format ON package_formats(format_id)")
    print("   ✓ Created indexes")


def add_media_buys_columns(cursor):
    """Add new columns to media_buys table for AdCP v2.3.0"""
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(media_buys)")
    columns = {row['name'] for row in cursor.fetchall()}
    
    # Add campaign_name if not exists
    if 'campaign_name' not in columns:
        cursor.execute("""
            ALTER TABLE media_buys 
            ADD COLUMN campaign_name TEXT DEFAULT 'Untitled Campaign'
        """)
        print("   ✓ Added 'campaign_name' column")
    
    # Add adcp_version if not exists
    if 'adcp_version' not in columns:
        cursor.execute("""
            ALTER TABLE media_buys 
            ADD COLUMN adcp_version TEXT DEFAULT '2.3.0'
        """)
        print("   ✓ Added 'adcp_version' column")


def migrate_campaigns(cursor):
    """Extract packages from JSON and insert into normalized tables"""
    # Get all media buys with AdCP v2.3.0 packages in JSON
    cursor.execute("""
        SELECT id, media_buy_id, targeting, workflow_state, total_budget
        FROM media_buys
        WHERE targeting IS NOT NULL
    """)
    
    campaigns = cursor.fetchall()
    migrated_count = 0
    skipped_count = 0
    
    for campaign in campaigns:
        try:
            targeting = json.loads(campaign['targeting']) if campaign['targeting'] else {}
            workflow_state = json.loads(campaign['workflow_state']) if campaign['workflow_state'] else {}
            
            # Check if this is an AdCP v2.3.0 campaign
            if 'adcp_version' not in targeting or 'packages' not in targeting:
                skipped_count += 1
                continue
            
            # Extract campaign name from workflow_state
            campaign_name = workflow_state.get('campaign_name', 'Migrated Campaign')
            
            # Update media_buy with campaign name
            cursor.execute("""
                UPDATE media_buys
                SET campaign_name = ?,
                    adcp_version = ?
                WHERE id = ?
            """, (campaign_name, '2.3.0', campaign['id']))
            
            # Extract and migrate packages
            packages = targeting['packages']
            for idx, pkg_data in enumerate(packages, 1):
                migrate_package(cursor, campaign, pkg_data, idx)
            
            migrated_count += 1
            print(f"   ✓ Migrated campaign: {campaign['media_buy_id']} ({len(packages)} package(s))")
            
        except Exception as e:
            print(f"   ⚠️  Skipped campaign {campaign['media_buy_id']}: {str(e)}")
            skipped_count += 1
    
    print(f"\n   Summary: {migrated_count} campaigns migrated, {skipped_count} skipped")


def migrate_package(cursor, campaign: sqlite3.Row, pkg_data: Dict[str, Any], pkg_idx: int):
    """Migrate a single package from JSON to normalized structure"""
    package_id = f"pkg_{pkg_idx}"
    package_uuid = str(uuid.uuid4())
    
    # Get product internal ID from product_id
    cursor.execute("""
        SELECT id FROM products WHERE product_id = ?
    """, (pkg_data['product_id'],))
    product = cursor.fetchone()
    
    if not product:
        raise ValueError(f"Product not found: {pkg_data['product_id']}")
    
    # Insert package
    cursor.execute("""
        INSERT INTO packages (
            id, media_buy_id, package_id, product_id, budget, currency,
            pacing, pricing_strategy, targeting_overlay, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        package_uuid,
        campaign['id'],
        package_id,
        product['id'],
        pkg_data['budget'],
        'USD',
        pkg_data.get('pacing', 'even'),
        pkg_data.get('pricing_strategy', 'cpm'),
        json.dumps(pkg_data.get('targeting_overlay', {})),
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    # Insert package formats
    format_ids = pkg_data.get('format_ids', [])
    for fmt in format_ids:
        cursor.execute("""
            INSERT INTO package_formats (
                id, package_id, agent_url, format_id, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            package_uuid,
            fmt['agent_url'],
            fmt['id'],
            datetime.now().isoformat()
        ))


def verify_migration(cursor):
    """Verify data integrity after migration"""
    # Count media buys
    cursor.execute("SELECT COUNT(*) as count FROM media_buys")
    media_buy_count = cursor.fetchone()['count']
    print(f"   ✓ Media buys: {media_buy_count}")
    
    # Count packages
    cursor.execute("SELECT COUNT(*) as count FROM packages")
    package_count = cursor.fetchone()['count']
    print(f"   ✓ Packages: {package_count}")
    
    # Count package formats
    cursor.execute("SELECT COUNT(*) as count FROM package_formats")
    format_count = cursor.fetchone()['count']
    print(f"   ✓ Package formats: {format_count}")
    
    # Verify referential integrity
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM packages p
        LEFT JOIN media_buys mb ON p.media_buy_id = mb.id
        WHERE mb.id IS NULL
    """)
    orphaned_packages = cursor.fetchone()['count']
    
    if orphaned_packages > 0:
        raise ValueError(f"Found {orphaned_packages} orphaned packages!")
    
    print(f"   ✓ Referential integrity verified")
    
    # Show sample data
    cursor.execute("""
        SELECT 
            mb.campaign_name,
            mb.media_buy_id,
            COUNT(p.id) as package_count,
            SUM(p.budget) as total_budget
        FROM media_buys mb
        LEFT JOIN packages p ON mb.id = p.media_buy_id
        WHERE mb.adcp_version = '2.3.0'
        GROUP BY mb.id
        LIMIT 3
    """)
    
    print("\n   📊 Sample migrated campaigns:")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            pkg_count = row['package_count'] or 0
            total_budget = row['total_budget'] or 0.0
            print(f"      • {row['campaign_name']}")
            print(f"        ID: {row['media_buy_id']}")
            print(f"        Packages: {pkg_count}, Budget: ${total_budget:,.2f}")
    else:
        print("      (No AdCP v2.3.0 campaigns found)")


def rollback_migration(db_path: str = "adcp_platform.db"):
    """
    Rollback migration: Drop new tables and columns
    WARNING: This will delete all package data!
    """
    print("⚠️  WARNING: Rolling back migration will DELETE all package data!")
    confirm = input("Type 'ROLLBACK' to confirm: ")
    
    if confirm != 'ROLLBACK':
        print("Rollback cancelled.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DROP TABLE IF EXISTS package_formats")
        cursor.execute("DROP TABLE IF EXISTS packages")
        print("✓ Dropped new tables")
        
        # Note: SQLite doesn't support DROP COLUMN, so we'd need to recreate the table
        # For now, we'll just leave the new columns
        
        conn.commit()
        print("✅ Rollback completed")
    except Exception as e:
        print(f"❌ Rollback failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        migrate_database()

