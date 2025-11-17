"""
Seed Database with Realistic Sample Data
Nike-Yahoo AdCP Platform - Post-Clean Room Workflow
"""
import sqlite3
import json
import uuid
from datetime import datetime, timedelta
import random

# Database file path
DB_PATH = "database/adcp_platform.db"
SCHEMA_PATH = "database/schema.sql"


def generate_id():
    """Generate UUID for primary keys"""
    return str(uuid.uuid4())


def init_database():
    """Initialize database with schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read and execute schema
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    conn.commit()
    return conn


def seed_tenants(conn):
    """Seed Yahoo tenant"""
    cursor = conn.cursor()
    
    tenant_id = generate_id()
    
    cursor.execute("""
        INSERT INTO tenants (id, name, slug, adapter_type, adapter_config, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        tenant_id,
        'Yahoo Publisher',
        'yahoo',
        'mock',  # Mock adapter for POC
        json.dumps({
            "api_endpoint": "https://api.yahoo.com/dsp/v1",
            "properties": ["yahoo.com/sports", "yahoo.com/finance", "yahoo.com/entertainment"]
        }),
        1
    ))
    
    conn.commit()
    print(f"✓ Seeded tenant: Yahoo Publisher (ID: {tenant_id})")
    return tenant_id


def seed_principals(conn, tenant_id):
    """Seed Nike principal"""
    cursor = conn.cursor()
    
    principal_id = generate_id()
    
    cursor.execute("""
        INSERT INTO principals (id, tenant_id, name, principal_id, auth_token, access_level, metadata, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        principal_id,
        tenant_id,
        'Nike',
        'nike_advertiser',
        'nike_token_12345',  # Static token for POC
        'enterprise',
        json.dumps({
            "industry": "athletic_apparel",
            "budget_tier": "enterprise",
            "account_manager": "sarah.johnson@yahoo.com"
        }),
        1
    ))
    
    conn.commit()
    print(f"✓ Seeded principal: Nike (ID: {principal_id}, Token: nike_token_12345)")
    return principal_id


def seed_matched_audiences(conn, tenant_id, principal_id):
    """Seed matched audiences (Clean Room output)"""
    cursor = conn.cursor()
    
    audiences = [
        {
            "id": generate_id(),
            "segment_id": "nike_running_yahoo_sports",
            "segment_name": "Nike Running Enthusiasts × Yahoo Sports",
            "overlap_count": 850000,
            "total_nike_segment": 1500000,
            "total_yahoo_segment": 2300000,
            "match_rate": 0.567,
            "demographics": {
                "age_range": {"25-34": 0.35, "35-44": 0.40, "45-54": 0.25},
                "gender_split": {"male": 0.60, "female": 0.38, "other": 0.02},
                "household_income": {"50k-75k": 0.25, "75k-100k": 0.35, "100k+": 0.40},
                "geo_distribution": {"US": 0.70, "CA": 0.15, "UK": 0.10, "other": 0.05}
            },
            "engagement_score": 0.85,
            "quality_score": 0.92,
            "privacy_params": {"k_anonymity": 1000, "epsilon": 0.1, "noise_added": True}
        },
        {
            "id": generate_id(),
            "segment_id": "nike_athletes_yahoo_sports_premium",
            "segment_name": "Nike Professional Athletes × Yahoo Sports Premium",
            "overlap_count": 125000,
            "total_nike_segment": 200000,
            "total_yahoo_segment": 400000,
            "match_rate": 0.625,
            "demographics": {
                "age_range": {"18-24": 0.30, "25-34": 0.45, "35-44": 0.25},
                "gender_split": {"male": 0.55, "female": 0.43, "other": 0.02},
                "household_income": {"75k-100k": 0.30, "100k+": 0.70},
                "geo_distribution": {"US": 0.75, "CA": 0.12, "UK": 0.08, "other": 0.05}
            },
            "engagement_score": 0.92,
            "quality_score": 0.95,
            "privacy_params": {"k_anonymity": 1000, "epsilon": 0.1, "noise_added": True}
        },
        {
            "id": generate_id(),
            "segment_id": "nike_lifestyle_yahoo_finance",
            "segment_name": "Nike Lifestyle × Yahoo Finance Readers",
            "overlap_count": 450000,
            "total_nike_segment": 800000,
            "total_yahoo_segment": 900000,
            "match_rate": 0.563,
            "demographics": {
                "age_range": {"30-39": 0.35, "40-49": 0.35, "50-59": 0.30},
                "gender_split": {"male": 0.50, "female": 0.48, "other": 0.02},
                "household_income": {"75k-100k": 0.35, "100k+": 0.65},
                "geo_distribution": {"US": 0.80, "CA": 0.10, "UK": 0.06, "other": 0.04}
            },
            "engagement_score": 0.68,
            "quality_score": 0.78,
            "privacy_params": {"k_anonymity": 1000, "epsilon": 0.1, "noise_added": True}
        }
    ]
    
    audience_ids = {}
    
    for aud in audiences:
        expires_at = (datetime.now() + timedelta(days=90)).isoformat()
        
        cursor.execute("""
            INSERT INTO matched_audiences 
            (id, segment_id, segment_name, tenant_id, principal_id, overlap_count, 
             total_nike_segment, total_yahoo_segment, match_rate, demographics, 
             engagement_score, quality_score, privacy_params, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            aud["id"],
            aud["segment_id"],
            aud["segment_name"],
            tenant_id,
            principal_id,
            aud["overlap_count"],
            aud["total_nike_segment"],
            aud["total_yahoo_segment"],
            aud["match_rate"],
            json.dumps(aud["demographics"]),
            aud["engagement_score"],
            aud["quality_score"],
            json.dumps(aud["privacy_params"]),
            expires_at
        ))
        
        audience_ids[aud["segment_id"]] = aud["id"]
    
    conn.commit()
    print(f"✓ Seeded {len(audiences)} matched audiences (Clean Room output)")
    return audience_ids


def seed_products(conn, tenant_id, audience_ids):
    """Seed Yahoo ad products"""
    cursor = conn.cursor()
    
    products = [
        {
            "id": generate_id(),
            "product_id": "yahoo_sports_display_enthusiasts",
            "name": "Yahoo Sports - Display (Sports Enthusiasts)",
            "description": "Premium display inventory on Yahoo Sports targeting engaged sports fans. High-value audience with proven purchase intent for athletic apparel and footwear.",
            "product_type": "display",
            "properties": ["yahoo.com/sports"],
            "formats": [
                {
                    "format": "display_300x250",
                    "name": "Medium Rectangle",
                    "dimensions": {"width": 300, "height": 250},
                    "file_types": ["jpg", "png", "gif", "html5"],
                    "max_file_size_kb": 150
                },
                {
                    "format": "display_728x90",
                    "name": "Leaderboard",
                    "dimensions": {"width": 728, "height": 90},
                    "file_types": ["jpg", "png", "gif", "html5"],
                    "max_file_size_kb": 150
                }
            ],
            "targeting": {
                "geo": ["US", "CA", "UK"],
                "age": [25, 54],
                "interests": ["sports", "fitness", "running", "basketball"],
                "devices": ["desktop", "mobile", "tablet"]
            },
            "matched_audience_ids": ["nike_running_yahoo_sports"],
            "pricing": {
                "type": "cpm",
                "value": 12.50,
                "currency": "USD",
                "enterprise_discount": 0.15
            },
            "minimum_budget": 5000,
            "estimated_reach": 2300000,
            "matched_reach": 850000,
            "estimated_impressions": 15000000
        },
        {
            "id": generate_id(),
            "product_id": "yahoo_sports_video_preroll",
            "name": "Yahoo Sports - Video Pre-roll",
            "description": "High-engagement video inventory on Yahoo Sports. Perfect for brand storytelling and product launches.",
            "product_type": "video",
            "properties": ["yahoo.com/sports"],
            "formats": [
                {
                    "format": "video_15s",
                    "name": "15-second Pre-roll",
                    "duration_seconds": 15,
                    "file_types": ["mp4", "mov"],
                    "max_file_size_mb": 50,
                    "resolution": "1920x1080"
                },
                {
                    "format": "video_30s",
                    "name": "30-second Pre-roll",
                    "duration_seconds": 30,
                    "file_types": ["mp4", "mov"],
                    "max_file_size_mb": 100,
                    "resolution": "1920x1080"
                }
            ],
            "targeting": {
                "geo": ["US", "CA"],
                "age": [18, 54],
                "interests": ["sports", "fitness", "running"],
                "devices": ["desktop", "mobile", "tablet"]
            },
            "matched_audience_ids": ["nike_running_yahoo_sports", "nike_athletes_yahoo_sports_premium"],
            "pricing": {
                "type": "cpm",
                "value": 18.00,
                "currency": "USD",
                "enterprise_discount": 0.15
            },
            "minimum_budget": 10000,
            "estimated_reach": 1200000,
            "matched_reach": 850000,
            "estimated_impressions": 8000000
        },
        {
            "id": generate_id(),
            "product_id": "yahoo_finance_display_premium",
            "name": "Yahoo Finance - Premium Display",
            "description": "Affluent, financially-engaged audience. Ideal for premium lifestyle and professional athletic products.",
            "product_type": "display",
            "properties": ["yahoo.com/finance"],
            "formats": [
                {
                    "format": "display_300x250",
                    "name": "Medium Rectangle",
                    "dimensions": {"width": 300, "height": 250},
                    "file_types": ["jpg", "png", "html5"],
                    "max_file_size_kb": 150
                },
                {
                    "format": "display_970x250",
                    "name": "Billboard",
                    "dimensions": {"width": 970, "height": 250},
                    "file_types": ["jpg", "png", "html5"],
                    "max_file_size_kb": 200
                }
            ],
            "targeting": {
                "geo": ["US"],
                "age": [30, 65],
                "household_income": ["75000+"],
                "interests": ["finance", "investing", "lifestyle"],
                "devices": ["desktop", "mobile"]
            },
            "matched_audience_ids": ["nike_lifestyle_yahoo_finance"],
            "pricing": {
                "type": "cpm",
                "value": 24.00,
                "currency": "USD",
                "enterprise_discount": 0.15
            },
            "minimum_budget": 15000,
            "estimated_reach": 900000,
            "matched_reach": 450000,
            "estimated_impressions": 6000000
        },
        {
            "id": generate_id(),
            "product_id": "yahoo_finance_ctv_video",
            "name": "Yahoo Finance - CTV Video",
            "description": "Connected TV video inventory on Yahoo Finance. Premium, brand-safe environment reaching affluent viewers.",
            "product_type": "ctv",
            "properties": ["yahoo.com/finance"],
            "formats": [
                {
                    "format": "video_15s",
                    "name": "15-second CTV",
                    "duration_seconds": 15,
                    "file_types": ["mp4"],
                    "max_file_size_mb": 50,
                    "resolution": "1920x1080"
                },
                {
                    "format": "video_30s",
                    "name": "30-second CTV",
                    "duration_seconds": 30,
                    "file_types": ["mp4"],
                    "max_file_size_mb": 100,
                    "resolution": "1920x1080"
                }
            ],
            "targeting": {
                "geo": ["US"],
                "age": [30, 65],
                "household_income": ["100000+"],
                "devices": ["ctv", "smart_tv"]
            },
            "matched_audience_ids": ["nike_lifestyle_yahoo_finance"],
            "pricing": {
                "type": "cpm",
                "value": 35.00,
                "currency": "USD",
                "enterprise_discount": 0.15
            },
            "minimum_budget": 25000,
            "estimated_reach": 600000,
            "matched_reach": 450000,
            "estimated_impressions": 4000000
        },
        {
            "id": generate_id(),
            "product_id": "yahoo_sports_native",
            "name": "Yahoo Sports - Native Ads",
            "description": "Native advertising units seamlessly integrated into Yahoo Sports content. High engagement and CTR.",
            "product_type": "native",
            "properties": ["yahoo.com/sports"],
            "formats": [
                {
                    "format": "native_standard",
                    "name": "Standard Native",
                    "dimensions": {"width": 1200, "height": 627},
                    "file_types": ["jpg", "png"],
                    "max_file_size_kb": 200,
                    "text_requirements": {
                        "headline_max_chars": 90,
                        "body_max_chars": 200
                    }
                }
            ],
            "targeting": {
                "geo": ["US", "CA", "UK"],
                "age": [18, 54],
                "interests": ["sports", "fitness", "lifestyle"],
                "devices": ["mobile", "tablet", "desktop"]
            },
            "matched_audience_ids": ["nike_running_yahoo_sports", "nike_athletes_yahoo_sports_premium"],
            "pricing": {
                "type": "cpm",
                "value": 16.00,
                "currency": "USD",
                "enterprise_discount": 0.15
            },
            "minimum_budget": 8000,
            "estimated_reach": 1800000,
            "matched_reach": 850000,
            "estimated_impressions": 12000000
        }
    ]
    
    product_map = {}
    
    for prod in products:
        cursor.execute("""
            INSERT INTO products 
            (id, tenant_id, product_id, name, description, product_type, properties, 
             formats, targeting, matched_audience_ids, pricing, minimum_budget, 
             estimated_reach, matched_reach, estimated_impressions, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prod["id"],
            tenant_id,
            prod["product_id"],
            prod["name"],
            prod["description"],
            prod["product_type"],
            json.dumps(prod["properties"]),
            json.dumps(prod["formats"]),
            json.dumps(prod["targeting"]),
            json.dumps(prod["matched_audience_ids"]),
            json.dumps(prod["pricing"]),
            prod["minimum_budget"],
            prod["estimated_reach"],
            prod["matched_reach"],
            prod["estimated_impressions"],
            1
        ))
        
        product_map[prod["product_id"]] = prod["id"]
    
    conn.commit()
    print(f"✓ Seeded {len(products)} products")
    return product_map


def seed_creatives(conn, tenant_id, principal_id):
    """Seed Nike creatives"""
    cursor = conn.cursor()
    
    creatives = [
        {
            "id": generate_id(),
            "creative_id": "nike_air_max_300x250",
            "name": "Nike Air Max - Medium Rectangle",
            "format": "display_300x250",
            "file_url": "https://cdn.nike.com/creatives/air_max_300x250.jpg",
            "preview_url": "https://cdn.nike.com/creatives/air_max_300x250_preview.jpg",
            "dimensions": {"width": 300, "height": 250},
            "file_size_bytes": 125000
        },
        {
            "id": generate_id(),
            "creative_id": "nike_running_728x90",
            "name": "Nike Running - Leaderboard",
            "format": "display_728x90",
            "file_url": "https://cdn.nike.com/creatives/running_728x90.jpg",
            "preview_url": "https://cdn.nike.com/creatives/running_728x90_preview.jpg",
            "dimensions": {"width": 728, "height": 90},
            "file_size_bytes": 95000
        },
        {
            "id": generate_id(),
            "creative_id": "nike_just_do_it_15s",
            "name": "Nike Just Do It - 15s Video",
            "format": "video_15s",
            "file_url": "https://cdn.nike.com/creatives/just_do_it_15s.mp4",
            "preview_url": "https://cdn.nike.com/creatives/just_do_it_15s_thumbnail.jpg",
            "dimensions": {"width": 1920, "height": 1080},
            "file_size_bytes": 45000000,
            "duration_seconds": 15
        }
    ]
    
    creative_map = {}
    
    for creative in creatives:
        cursor.execute("""
            INSERT INTO creatives
            (id, tenant_id, creative_id, principal_id, name, format, file_url, 
             preview_url, dimensions, file_size_bytes, duration_seconds, approval_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            creative["id"],
            tenant_id,
            creative["creative_id"],
            principal_id,
            creative["name"],
            creative["format"],
            creative["file_url"],
            creative["preview_url"],
            json.dumps(creative["dimensions"]),
            creative["file_size_bytes"],
            creative.get("duration_seconds"),
            "approved"
        ))
        
        creative_map[creative["creative_id"]] = creative["id"]
    
    conn.commit()
    print(f"✓ Seeded {len(creatives)} creatives")
    return creative_map


def seed_media_buys(conn, tenant_id, principal_id, product_map, creative_map, audience_ids):
    """Seed media buys (campaigns)"""
    cursor = conn.cursor()
    
    # Active campaign
    mb1_id = generate_id()
    mb1_media_buy_id = "nike_air_max_spring_q1"
    
    cursor.execute("""
        INSERT INTO media_buys
        (id, tenant_id, media_buy_id, principal_id, product_ids, total_budget, currency,
         flight_start_date, flight_end_date, targeting, matched_audience_id, 
         assigned_creatives, status, impressions_delivered, spend, clicks, conversions,
         external_campaign_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        mb1_id,
        tenant_id,
        mb1_media_buy_id,
        principal_id,
        json.dumps([product_map["yahoo_sports_display_enthusiasts"]]),
        50000.00,
        "USD",
        "2025-01-15",
        "2025-04-15",
        json.dumps({
            "geo": ["US", "CA"],
            "age": [25, 45],
            "interests": ["sports", "running"]
        }),
        audience_ids["nike_running_yahoo_sports"],
        json.dumps([
            {
                "creative_id": creative_map["nike_air_max_300x250"],
                "product_id": product_map["yahoo_sports_display_enthusiasts"]
            }
        ]),
        "active",
        8500000,
        24500.00,
        35700,
        1428,
        "yahoo_dsp_campaign_12345"
    ))
    
    # Pending campaign
    mb2_id = generate_id()
    mb2_media_buy_id = "nike_running_gear_test"
    
    cursor.execute("""
        INSERT INTO media_buys
        (id, tenant_id, media_buy_id, principal_id, product_ids, total_budget, currency,
         flight_start_date, flight_end_date, targeting, matched_audience_id, 
         assigned_creatives, status, impressions_delivered, spend, clicks, conversions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        mb2_id,
        tenant_id,
        mb2_media_buy_id,
        principal_id,
        json.dumps([product_map["yahoo_sports_video_preroll"]]),
        15000.00,
        "USD",
        "2025-02-01",
        "2025-02-28",
        json.dumps({
            "geo": ["US"],
            "age": [18, 45],
            "interests": ["running", "fitness"]
        }),
        audience_ids["nike_running_yahoo_sports"],
        json.dumps([
            {
                "creative_id": creative_map["nike_just_do_it_15s"],
                "product_id": product_map["yahoo_sports_video_preroll"]
            }
        ]),
        "pending",
        0,
        0.00,
        0,
        0
    ))
    
    conn.commit()
    print(f"✓ Seeded 2 media buys (1 active, 1 pending)")
    return {mb1_media_buy_id: mb1_id, mb2_media_buy_id: mb2_id}


def seed_delivery_metrics(conn, media_buy_map):
    """Seed delivery metrics for active campaign (20 days of data)"""
    cursor = conn.cursor()
    
    mb_id = media_buy_map["nike_air_max_spring_q1"]
    start_date = datetime(2025, 1, 15)
    
    metrics = []
    
    for day in range(20):
        current_date = start_date + timedelta(days=day)
        
        # Weekend boost (Sat=5, Sun=6)
        is_weekend = current_date.weekday() in [5, 6]
        base_impressions = random.randint(380000, 450000)
        if is_weekend:
            base_impressions = int(base_impressions * 1.3)
        
        # CPM = $12.50, enterprise discount = 15% -> $10.625
        cpm = 10.625
        spend = (base_impressions / 1000) * cpm
        
        # CTR between 0.38% - 0.48%
        ctr = random.uniform(0.0038, 0.0048)
        clicks = int(base_impressions * ctr)
        
        # Conversion rate ~4% of clicks
        conversions = int(clicks * 0.04)
        
        metrics.append({
            "id": generate_id(),
            "media_buy_id": mb_id,
            "date": current_date.strftime("%Y-%m-%d"),
            "impressions": base_impressions,
            "clicks": clicks,
            "conversions": conversions,
            "spend": round(spend, 2),
            "product_id": "yahoo_sports_display_enthusiasts",
            "creative_id": "nike_air_max_300x250",
            "geo": "US",
            "device_type": random.choice(["desktop", "mobile", "tablet"])
        })
    
    for metric in metrics:
        cursor.execute("""
            INSERT INTO delivery_metrics
            (id, media_buy_id, date, impressions, clicks, conversions, spend,
             product_id, creative_id, geo, device_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric["id"],
            metric["media_buy_id"],
            metric["date"],
            metric["impressions"],
            metric["clicks"],
            metric["conversions"],
            metric["spend"],
            metric["product_id"],
            metric["creative_id"],
            metric["geo"],
            metric["device_type"]
        ))
    
    conn.commit()
    print(f"✓ Seeded {len(metrics)} delivery metrics (20 days)")


def print_summary(conn):
    """Print database summary"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("DATABASE SEEDING COMPLETE")
    print("="*60)
    
    tables = [
        "tenants", "principals", "matched_audiences", "products", 
        "creatives", "media_buys", "delivery_metrics"
    ]
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:25} {count:>5} records")
    
    print("\n" + "-"*60)
    print("AUTHENTICATION")
    print("-"*60)
    print("  Principal: nike_advertiser")
    print("  Token: nike_token_12345")
    print("\n" + "-"*60)
    print("MATCHED AUDIENCES (Clean Room Output)")
    print("-"*60)
    
    cursor.execute("""
        SELECT segment_name, overlap_count, engagement_score 
        FROM matched_audiences
        ORDER BY overlap_count DESC
    """)
    
    for row in cursor.fetchall():
        print(f"  • {row[0]}")
        print(f"    Overlap: {row[1]:,} users | Engagement: {row[2]:.2f}")
    
    print("\n" + "-"*60)
    print("READY FOR MCP SERVER & CLIENT")
    print("-"*60)
    print(f"  Database: {DB_PATH}")
    print("  Next: Build Yahoo MCP Server (Phase 2)")
    print("="*60 + "\n")


def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("SEEDING DATABASE - NIKE-YAHOO ADCP PLATFORM")
    print("="*60 + "\n")
    
    # Initialize
    conn = init_database()
    print("✓ Database initialized with schema\n")
    
    # Seed data
    tenant_id = seed_tenants(conn)
    principal_id = seed_principals(conn, tenant_id)
    audience_ids = seed_matched_audiences(conn, tenant_id, principal_id)
    product_map = seed_products(conn, tenant_id, audience_ids)
    creative_map = seed_creatives(conn, tenant_id, principal_id)
    media_buy_map = seed_media_buys(conn, tenant_id, principal_id, product_map, creative_map, audience_ids)
    seed_delivery_metrics(conn, media_buy_map)
    
    # Summary
    print_summary(conn)
    
    conn.close()


if __name__ == "__main__":
    main()

