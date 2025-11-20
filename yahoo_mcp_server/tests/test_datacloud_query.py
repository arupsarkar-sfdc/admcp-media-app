"""
Test Salesforce Data Cloud Query Service
Execute SQL queries against Snowflake data via Data Cloud
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.datacloud_query_service import DataCloudQueryService


async def test_query_service():
    """Test Data Cloud Query Service with real Snowflake data"""
    
    print("="*70)
    print("Testing Salesforce Data Cloud Query Service")
    print("="*70)
    
    # Initialize service
    query_service = DataCloudQueryService()
    
    # Test 1: Simple count query
    print("\n1️⃣ Test: Count all products")
    print("-" * 70)
    
    sql = "SELECT COUNT(*) as total_products FROM products__dlm"
    
    try:
        result = await query_service.execute_query(sql)
        print(f"   ✅ Query executed successfully")
        print(f"   Rows returned: {result['row_count']}")
        print(f"   Data: {result['rows']}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return
    
    # Test 2: Fetch products with details
    print("\n2️⃣ Test: Fetch active products")
    print("-" * 70)
    
    try:
        products = await query_service.query_products(is_active=True)
        print(f"   ✅ Found {len(products)} active products")
        
        for i, product in enumerate(products[:3], 1):
            print(f"\n   Product {i}:")
            print(f"      ID: {product.get('id')}")
            print(f"      Name: {product.get('name')}")
            print(f"      Product ID: {product.get('product_id')}")
            print(f"      Type: {product.get('product_type')}")
            print(f"      Min Budget: ${product.get('minimum_budget', 0):,.2f}")
            print(f"      Reach: {product.get('estimated_reach', 0):,}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Query media buys
    print("\n3️⃣ Test: Fetch media buys")
    print("-" * 70)
    
    media_buys = []
    try:
        media_buys = await query_service.query_media_buys()
        print(f"   ✅ Found {len(media_buys)} media buys")
        
        for i, buy in enumerate(media_buys[:3], 1):
            print(f"\n   Media Buy {i}:")
            print(f"      ID: {buy.get('media_buy_id')}")
            print(f"      Campaign: {buy.get('campaign_name')}")
            print(f"      Budget: ${buy.get('total_budget', 0):,.2f}")
            print(f"      Status: {buy.get('status')}")
            print(f"      Flight: {buy.get('flight_start_date')} to {buy.get('flight_end_date')}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: Query packages for a media buy
    print("\n4️⃣ Test: Fetch packages for first media buy")
    print("-" * 70)
    
    packages = []
    if media_buys:
        try:
            media_buy_id = media_buys[0].get('media_buy_id')
            packages = await query_service.query_packages_by_media_buy(media_buy_id)
            print(f"   ✅ Found {len(packages)} packages for media buy {media_buy_id}")
            
            for i, pkg in enumerate(packages, 1):
                print(f"\n   Package {i}:")
                print(f"      Package ID: {pkg.get('package_id')}")
                print(f"      Product ID: {pkg.get('product_id')}")
                print(f"      Budget: ${pkg.get('budget', 0):,.2f}")
                print(f"      Pacing: {pkg.get('pacing')}")
                print(f"      Pricing: {pkg.get('pricing_strategy')}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Test 5: Custom SQL query with JOIN
    print("\n5️⃣ Test: Join media_buys with packages")
    print("-" * 70)
    
    sql = """
    SELECT 
        mb.campaign_name__c as campaign_name,
        mb.total_budget__c as total_budget,
        mb.status__c as status,
        COUNT(p.id__c) as package_count,
        SUM(p.budget__c) as total_package_budget
    FROM media_buys__dlm mb
    LEFT JOIN packages__dlm p ON mb.media_buy_id__c = p.media_buy_id__c
    GROUP BY mb.campaign_name__c, mb.total_budget__c, mb.status__c
    ORDER BY mb.campaign_name__c
    """
    
    try:
        result = await query_service.execute_query(sql)
        print(f"   ✅ Query executed: {result['row_count']} rows")
        
        for row in result['rows']:
            print(f"\n   Campaign: {row.get('campaign_name')}")
            print(f"      Budget: ${row.get('total_budget', 0):,.2f}")
            print(f"      Packages: {row.get('package_count')}")
            print(f"      Package Budget: ${row.get('total_package_budget', 0):,.2f}")
            print(f"      Status: {row.get('status')}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 6: Query matched audiences
    print("\n6️⃣ Test: Fetch matched audiences")
    print("-" * 70)
    
    try:
        audiences = await query_service.query_matched_audiences()
        print(f"   ✅ Found {len(audiences)} matched audiences")
        
        for i, aud in enumerate(audiences[:2], 1):
            print(f"\n   Audience {i}:")
            print(f"      Segment ID: {aud.get('segment_id')}")
            print(f"      Name: {aud.get('segment_name')}")
            print(f"      Overlap: {aud.get('overlap_count', 0):,}")
            print(f"      Match Rate: {aud.get('match_rate', 0):.2%}")
            print(f"      Contact ID: {aud.get('contact_id')}")
            print(f"      SFDC Account: {aud.get('salesforce_account_id')}")
            print(f"      SFDC Contact: {aud.get('salesforce_contact_id')}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 7: Query delivery metrics
    print("\n7️⃣ Test: Fetch delivery metrics")
    print("-" * 70)
    
    try:
        metrics = await query_service.query_delivery_metrics()
        print(f"   ✅ Found {len(metrics)} delivery metric records")
        
        for i, metric in enumerate(metrics[:3], 1):
            print(f"\n   Metric {i}:")
            print(f"      Date: {metric.get('date')} Hour: {metric.get('hour')}")
            print(f"      Media Buy ID: {metric.get('media_buy_id')}")
            print(f"      Impressions: {metric.get('impressions', 0):,}")
            print(f"      Clicks: {metric.get('clicks', 0):,}")
            print(f"      Spend: ${metric.get('spend', 0):,.2f}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 8: Query package formats
    print("\n8️⃣ Test: Fetch package formats")
    print("-" * 70)
    
    if packages:
        try:
            package_id = packages[0].get('package_id')
            formats = await query_service.query_package_formats_by_package(package_id)
            print(f"   ✅ Found {len(formats)} formats for package {package_id}")
            
            for i, fmt in enumerate(formats, 1):
                print(f"\n   Format {i}:")
                print(f"      Format ID: {fmt.get('format_id')}")
                print(f"      Agent URL: {fmt.get('agent_url')}")
                print(f"      Format Name: {fmt.get('format_name')}")
                print(f"      Format Type: {fmt.get('format_type')}")
                print(f"      Assigned Creative: {fmt.get('assigned_creative_id')}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "="*70)
    print("✅ Data Cloud Query Service Test Complete!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_query_service())

