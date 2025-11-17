"""
Verify Database Data
Quick inspection of seeded data
"""
import sqlite3
import json

DB_PATH = "database/adcp_platform.db"

def inspect_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("DATABASE INSPECTION - NIKE-YAHOO ADCP PLATFORM")
    print("="*70 + "\n")
    
    # Matched Audiences
    print("📊 MATCHED AUDIENCES (Clean Room Output)")
    print("-"*70)
    cursor.execute("""
        SELECT segment_id, segment_name, overlap_count, match_rate, 
               engagement_score, demographics
        FROM matched_audiences
        ORDER BY overlap_count DESC
    """)
    
    for row in cursor.fetchall():
        demographics = json.loads(row[5])
        print(f"\n✓ {row[1]}")
        print(f"  Segment ID: {row[0]}")
        print(f"  Overlap: {row[2]:,} users")
        print(f"  Match Rate: {row[3]:.1%}")
        print(f"  Engagement: {row[4]:.2f}")
        print(f"  Age Distribution: {demographics['age_range']}")
        print(f"  Gender: Male {demographics['gender_split']['male']:.0%}, "
              f"Female {demographics['gender_split']['female']:.0%}")
    
    # Products
    print("\n\n" + "="*70)
    print("📦 PRODUCTS (Ad Inventory)")
    print("-"*70)
    cursor.execute("""
        SELECT product_id, name, product_type, pricing, estimated_reach, 
               matched_reach, matched_audience_ids
        FROM products
        ORDER BY matched_reach DESC
    """)
    
    for row in cursor.fetchall():
        pricing = json.loads(row[3])
        matched_audiences = json.loads(row[6])
        
        enterprise_price = pricing['value'] * (1 - pricing.get('enterprise_discount', 0))
        
        print(f"\n✓ {row[1]}")
        print(f"  Product ID: {row[0]}")
        print(f"  Type: {row[2].upper()}")
        print(f"  CPM: ${pricing['value']:.2f} (Enterprise: ${enterprise_price:.2f})")
        print(f"  Total Reach: {row[4]:,} | Matched Reach: {row[5]:,}")
        print(f"  Matched Audiences: {', '.join(matched_audiences)}")
    
    # Media Buys
    print("\n\n" + "="*70)
    print("🚀 MEDIA BUYS (Campaigns)")
    print("-"*70)
    cursor.execute("""
        SELECT mb.media_buy_id, mb.status, mb.total_budget, mb.spend,
               mb.impressions_delivered, mb.clicks, mb.conversions,
               mb.flight_start_date, mb.flight_end_date,
               ma.segment_name
        FROM media_buys mb
        LEFT JOIN matched_audiences ma ON mb.matched_audience_id = ma.id
        ORDER BY mb.created_at DESC
    """)
    
    for row in cursor.fetchall():
        print(f"\n✓ {row[0].upper()}")
        print(f"  Status: {row[1].upper()}")
        print(f"  Budget: ${row[2]:,.2f} | Spend: ${row[3]:,.2f} ({(row[3]/row[2]*100):.1f}%)")
        print(f"  Flight: {row[7]} to {row[8]}")
        print(f"  Matched Audience: {row[9]}")
        
        if row[4] > 0:
            ctr = (row[5] / row[4]) * 100
            cvr = (row[6] / row[5]) * 100 if row[5] > 0 else 0
            print(f"  Performance:")
            print(f"    Impressions: {row[4]:,}")
            print(f"    Clicks: {row[5]:,} (CTR: {ctr:.2f}%)")
            print(f"    Conversions: {row[6]:,} (CVR: {cvr:.2f}%)")
    
    # Delivery Metrics Summary
    print("\n\n" + "="*70)
    print("📈 DELIVERY METRICS (Last 7 Days)")
    print("-"*70)
    cursor.execute("""
        SELECT date, SUM(impressions), SUM(clicks), SUM(spend), SUM(conversions)
        FROM delivery_metrics
        GROUP BY date
        ORDER BY date DESC
        LIMIT 7
    """)
    
    print(f"\n{'Date':<12} {'Impressions':>12} {'Clicks':>8} {'Spend':>10} {'Conv':>6}")
    print("-"*70)
    for row in cursor.fetchall():
        ctr = (row[2] / row[1]) * 100 if row[1] > 0 else 0
        print(f"{row[0]:<12} {row[1]:>12,} {row[2]:>8,} ${row[3]:>9,.2f} {row[4]:>6,}")
    
    print("\n" + "="*70)
    print("✓ Database verification complete!")
    print("="*70 + "\n")
    
    conn.close()


if __name__ == "__main__":
    inspect_database()

