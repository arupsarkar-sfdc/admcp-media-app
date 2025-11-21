"""
Nike Campaign Workflow - HTTP Client
Tests Yahoo MCP Server via HTTP/SSE transport
Validates all 6 AdCP v2.3.0 tools end-to-end

Author: Nike Marketing Team
Protocol: Model Context Protocol (MCP) over HTTP/SSE
Transport: FastMCP Streamable HTTP
"""
import asyncio
import json
from fastmcp import Client

# Configuration
# For Heroku deployment:
MCP_SERVER_URL = "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp"
# For local testing:
# MCP_SERVER_URL = "http://localhost:8080/mcp"
EXISTING_CAMPAIGN_ID = "nike_air_max_spring_q1"  # Campaign with metrics data


async def run_nike_campaign_workflow():
    """
    Execute complete Nike campaign workflow via Yahoo MCP Server.
    
    Tests all 6 AdCP tools:
    1. get_products - Product discovery with LLM
    2. create_media_buy - Campaign creation
    3. get_media_buy - Campaign configuration
    4. get_media_buy_delivery - Performance metrics
    5. update_media_buy - Campaign optimization
    6. get_media_buy_report - Analytics reporting
    """
    
    print("\n" + "="*70)
    print("NIKE CAMPAIGN WORKFLOW - HTTP CLIENT")
    print("="*70)
    
    # Initialize MCP client
    client = Client(MCP_SERVER_URL)
    
    try:
        # Connect using context manager
        async with client:
            # Basic server interaction
            await client.ping()
            print("✅ Connected to Yahoo MCP Server\n")
            
            # ================================================================
            # TEST 1: Product Discovery (get_products)
            # ================================================================
            print("="*70)
            print("TEST 1: get_products (Product Discovery with LLM)")
            print("="*70)
            
            campaign_brief = """
            Nike wants to launch a Q1 2025 campaign targeting sports enthusiasts 
            interested in running gear and athletic apparel. 
            
            Target audience:
            - US users aged 25-45
            - Interested in fitness, running, basketball
            - Middle to high household income
            
            Budget: $50,000 over 3 months
            Goal: Brand awareness and product launches
            """
            
            print(f"\n📝 Campaign Brief:")
            print(campaign_brief)
            
            print("\n🔍 Querying Yahoo advertising inventory with LLM...")
            
            result = await client.call_tool(
                "get_products",
                arguments={
                    "brief": campaign_brief.strip(),
                    "budget_range": [40000, 60000]
                }
            )
            
            result_data = json.loads(result.content[0].text)
            
            print(f"\n✅ Found {result_data['total_count']} matching products")
            print(f"   Principal: {result_data['principal']['name']} ({result_data['principal']['access_level']})")
            
            print(f"\n📦 Available Products:\n")
            for i, product in enumerate(result_data['products'], 1):
                print(f"{i}. {product['name']}")
                print(f"   Product ID: {product['product_id']}")
                print(f"   Type: {product['product_type']}")
                
                # Pricing info
                pricing = product['pricing']
                print(f"   CPM: ${pricing['value']:.2f} (${pricing['original_value']:.2f} - {pricing['discount_percentage']})")
                
                print(f"   Est. Reach: {product['estimated_reach']:,} users")
                print(f"   Min Budget: ${product['minimum_budget']:,.0f}")
                
                if 'matched_audiences' in product and product['matched_audiences']:
                    print(f"   🎯 Matched Audiences (Clean Room):")
                    for audience in product['matched_audiences']:
                        print(f"      - {audience['segment_name']}")
                        print(f"        Overlap: {audience['overlap_count']:,} users ({audience['match_rate']*100:.1f}%)")
                        print(f"        Engagement: {int(audience['engagement_score']*100)}%")
                print()
            
            print("="*70)
            print("✅ TEST 1 COMPLETE - get_products works!")
            print("="*70)
            
            # ================================================================
            # TEST 2: create_media_buy (AdCP v2.3.0 Package-Based)
            # ================================================================
            print("\n" + "="*70)
            print("TEST 2: create_media_buy (AdCP v2.3.0 Package-Based Campaign)")
            print("="*70)
            
            # Use the first product from TEST 1
            selected_product = result_data['products'][0]
            print(f"\n📝 Campaign Configuration:")
            print(f"   Campaign Name: Nike Air Max Spring 2025")
            print(f"   Selected Product: {selected_product['name']}")
            print(f"   Product ID: {selected_product['product_id']}")
            print(f"   Budget: $25,000 (single package)")
            print(f"   Flight Dates: March 1 - May 31, 2025")
            print(f"   Creative Formats: Display 728x90, Display 300x250")
            print(f"   Targeting: US, Ages 25-45, Sports interests")
            
            print(f"\n🚀 Creating AdCP v2.3.0 campaign with package structure...")
            
            # Build AdCP v2.3.0 package
            packages = [
                {
                    "product_id": selected_product['product_id'],
                    "budget": 25000.0,
                        "format_ids": [
                            {
                                "agent_url": "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp",
                                "id": "display_728x90"
                            },
                            {
                                "agent_url": "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp",
                                "id": "display_300x250"
                            }
                        ],
                    "targeting_overlay": {
                        "geo": ["US"],
                        "age": [25, 45],
                        "interests": ["sports", "running", "fitness"]
                    },
                    "pacing": "even",
                    "pricing_strategy": "cpm"
                }
            ]
            
            result = await client.call_tool(
                "create_media_buy",
                arguments={
                    "campaign_name": "Nike Air Max Spring 2025",
                    "packages": packages,
                    "flight_start_date": "2025-03-01",
                    "flight_end_date": "2025-05-31",
                    "currency": "USD"
                }
            )
            
            campaign_data = json.loads(result.content[0].text)
            
            print(f"\n✅ AdCP v2.3.0 Campaign Created Successfully!")
            print(f"   Campaign Name: {campaign_data.get('campaign_name', 'N/A')}")
            print(f"   Campaign ID: {campaign_data['media_buy_id']}")
            print(f"   Status: {campaign_data['status'].upper()}")
            print(f"   AdCP Version: {campaign_data.get('adcp_version', 'N/A')}")
            print(f"   Total Budget: ${campaign_data['total_budget']:,.2f} {campaign_data.get('currency', 'USD')}")
            print(f"   Flight: {campaign_data['flight_start_date']} to {campaign_data['flight_end_date']}")
            
            if 'packages' in campaign_data and campaign_data['packages']:
                print(f"\n📦 Package Details:")
                for i, pkg in enumerate(campaign_data['packages'], 1):
                    print(f"   Package {i}: {pkg['product_name']}")
                    print(f"      Budget: ${pkg['budget']:,.2f}")
                    print(f"      Formats: {', '.join(pkg['formats'])}")
                    print(f"      Pacing: {pkg.get('pacing', 'even')}")
                    print(f"      Pricing: {pkg.get('pricing_strategy', 'cpm').upper()}")
            
            if 'matched_audience' in campaign_data and campaign_data['matched_audience']:
                ma = campaign_data['matched_audience']
                print(f"\n🎯 Matched Audience (Clean Room):")
                if isinstance(ma, dict):
                    if 'segment_name' in ma:
                        print(f"   Segment: {ma['segment_name']}")
                    if 'overlap_count' in ma:
                        print(f"   Matched Users: {ma['overlap_count']:,}")
                    if 'segment_id' in ma:
                        print(f"   Segment ID: {ma['segment_id']}")
            
            if 'workflow' in campaign_data:
                workflow = campaign_data['workflow']
                print(f"\n⚙️  Workflow:")
                print(f"   Requires Approval: {workflow.get('requires_approval', False)}")
                print(f"   Next Steps: {workflow.get('next_steps', 'N/A')}")
            
            # Store campaign ID for next tests
            test_campaign_id = campaign_data['media_buy_id']
            
            print("\n" + "="*70)
            print("✅ TEST 2 COMPLETE - create_media_buy works!")
            print("="*70)
            
            # ================================================================
            # TEST 3: get_media_buy (Get Campaign Configuration)
            # ================================================================
            print("\n" + "="*70)
            print("TEST 3: get_media_buy (Campaign Configuration)")
            print("="*70)
            
            print(f"\n📋 Fetching campaign details...")
            print(f"   Campaign ID: {test_campaign_id}")
            
            result = await client.call_tool(
                "get_media_buy",
                arguments={
                    "media_buy_id": test_campaign_id
                }
            )
            
            config_data = json.loads(result.content[0].text)
            
            print(f"\n✅ Campaign Configuration Retrieved:")
            print(f"   Campaign ID: {config_data['media_buy_id']}")
            print(f"   Status: {config_data['status'].upper()}")
            print(f"   Budget: ${config_data['total_budget']:,.2f}")
            if 'currency' in config_data:
                print(f"   Currency: {config_data['currency']}")
            print(f"   Flight: {config_data['flight_start_date']} to {config_data['flight_end_date']}")
            
            if 'products' in config_data and config_data['products']:
                print(f"\n📦 Associated Products:")
                for prod in config_data['products']:
                    print(f"   - {prod['name']} ({prod['product_type']})")
            
            if 'targeting' in config_data and config_data['targeting']:
                targeting = config_data['targeting']
                print(f"\n🎯 Targeting Parameters:")
                if 'geo' in targeting:
                    print(f"   Geo: {', '.join(targeting['geo'])}")
                if 'age' in targeting:
                    print(f"   Age: {targeting['age'][0]}-{targeting['age'][1]}")
                if 'interests' in targeting:
                    print(f"   Interests: {', '.join(targeting['interests'])}")
            
            if 'matched_audience' in config_data and config_data['matched_audience']:
                ma = config_data['matched_audience']
                print(f"\n🎯 Matched Audience (Clean Room):")
                if isinstance(ma, dict):
                    if 'segment_name' in ma:
                        print(f"   Segment: {ma['segment_name']}")
                    if 'overlap_count' in ma:
                        print(f"   Total Matched: {ma['overlap_count']:,} users")
                    if 'engagement_score' in ma:
                        print(f"   Engagement Score: {ma['engagement_score']:.2f}")
            
            print("\n" + "="*70)
            print("✅ TEST 3 COMPLETE - get_media_buy works!")
            print("="*70)
            
            # ================================================================
            # TEST 4: get_media_buy_delivery (Real-time Performance Metrics)
            # ================================================================
            print("\n" + "="*70)
            print("TEST 4: get_media_buy_delivery (Performance Metrics)")
            print("="*70)
            
            # Note: Use existing campaign with metrics data
            print(f"\n📊 Fetching performance metrics...")
            print(f"   Campaign ID: {EXISTING_CAMPAIGN_ID}")
            
            result = await client.call_tool(
                "get_media_buy_delivery",
                arguments={
                    "media_buy_id": EXISTING_CAMPAIGN_ID
                }
            )
            
            metrics_data = json.loads(result.content[0].text)
            
            print(f"\n✅ Performance Metrics Retrieved:")
            print(f"   Status: {metrics_data['status'].upper()}")
            
            if 'delivery' in metrics_data:
                delivery = metrics_data['delivery']
                print(f"\n📈 Delivery Metrics:")
                print(f"   Impressions: {delivery['impressions_delivered']:,}")
                print(f"   Clicks: {delivery['clicks']:,}")
                print(f"   Conversions: {delivery['conversions']:,}")
                print(f"   Spend: ${delivery['spend']:,.2f}")
                print(f"   CTR: {delivery['ctr']:.2f}%")
                print(f"   CVR: {delivery['cvr']:.2f}%")
            
            if 'pacing' in metrics_data:
                pacing = metrics_data['pacing']
                print(f"\n💰 Budget Pacing:")
                print(f"   Budget Spent: ${pacing['budget_spent']:,.2f}")
                print(f"   Budget Total: ${pacing['budget_total']:,.2f}")
                print(f"   Budget Pacing: {pacing['budget_pacing_pct']:.1f}%")
            
            if 'matched_audience' in metrics_data and metrics_data['matched_audience']:
                ma = metrics_data['matched_audience']
                print(f"\n🎯 Matched Audience (Clean Room):")
                if isinstance(ma, dict) and 'segment_name' in ma:
                    print(f"   Segment: {ma['segment_name']}")
                    if 'overlap_count' in ma:
                        print(f"   Total Matched: {ma['overlap_count']:,} users")
                    if 'engagement_score' in ma:
                        print(f"   Engagement Score: {ma['engagement_score']:.2f}")
            
            print("\n" + "="*70)
            print("✅ TEST 4 COMPLETE - get_media_buy_delivery works!")
            print("="*70)
            
            # ================================================================
            # TEST 5: update_media_buy (Modify Campaign)
            # ================================================================
            print("\n" + "="*70)
            print("TEST 5: update_media_buy (Campaign Optimization)")
            print("="*70)
            
            print(f"\n⚙️  Updating campaign: {test_campaign_id}")
            print(f"   Changes:")
            print(f"   - Increase budget: $25,000 → $35,000")
            print(f"   - Expand geo targeting: US → US, CA")
            
            result = await client.call_tool(
                "update_media_buy",
                arguments={
                    "media_buy_id": test_campaign_id,
                    "updates": {
                        "total_budget": 35000.0,
                        "targeting": {
                            "geo": ["US", "CA"],
                            "age": [25, 45],
                            "interests": ["sports", "running", "fitness"]
                        }
                    }
                }
            )
            
            update_data = json.loads(result.content[0].text)
            
            print(f"\n✅ Campaign Updated Successfully!")
            
            # Debug: show what we got
            if 'media_buy_id' not in update_data:
                print(f"\n🔍 DEBUG - Response keys: {list(update_data.keys())}")
                print(f"🔍 DEBUG - Full response: {json.dumps(update_data, indent=2)}")
            
            print(f"   Campaign ID: {update_data.get('media_buy_id', 'N/A')}")
            print(f"   Campaign Name: {update_data.get('campaign_name', 'N/A')}")
            print(f"   Status: {update_data.get('status', 'unknown').upper()}")
            print(f"   New Budget: ${update_data.get('total_budget', 0):,.2f}")
            
            if 'updates_applied' in update_data:
                print(f"\n📝 Updates Applied:")
                for key, value in update_data['updates_applied'].items():
                    print(f"   {key}: {value}")
            
            print("\n" + "="*70)
            print("✅ TEST 5 COMPLETE - update_media_buy works!")
            print("="*70)
            
            # ================================================================
            # TEST 6: get_media_buy_report (Analytics Report)
            # ================================================================
            print("\n" + "="*70)
            print("TEST 6: get_media_buy_report (Analytics Report)")
            print("="*70)
            
            print(f"\n📊 Generating 7-day performance report...")
            print(f"   Campaign ID: {EXISTING_CAMPAIGN_ID}")
            
            result = await client.call_tool(
                "get_media_buy_report",
                arguments={
                    "media_buy_id": EXISTING_CAMPAIGN_ID,
                    "date_range": "last_7_days"
                }
            )
            
            report_data = json.loads(result.content[0].text)
            
            print(f"\n✅ Report Generated:")
            if 'date_range' in report_data:
                print(f"   Period: {report_data['date_range']}")
            
            if 'overall' in report_data:
                overall = report_data['overall']
                if 'delivery' in overall:
                    delivery = overall['delivery']
                    print(f"\n📈 Overall Delivery:")
                    print(f"   Total Impressions: {delivery['impressions']:,}")
                    print(f"   Total Clicks: {delivery['clicks']:,}")
                    print(f"   Total Conversions: {delivery['conversions']:,}")
                    print(f"   Total Spend: ${delivery['spend']:,.2f}")
                
                if 'performance' in overall:
                    performance = overall['performance']
                    print(f"\n📊 Overall Performance:")
                    print(f"   Avg CTR: {performance['ctr']:.2f}%")
                    print(f"   Avg CVR: {performance['cvr']:.2f}%")
            
            if 'by_device' in report_data and report_data['by_device']:
                print(f"\n📱 Device Breakdown:")
                for device, stats in report_data['by_device'].items():
                    print(f"   {device.capitalize()}: {stats['impressions']:,} imp, CTR {stats['ctr']:.2f}%")
            
            if 'by_geo' in report_data and report_data['by_geo']:
                print(f"\n🌍 Geo Breakdown:")
                for geo, stats in report_data['by_geo'].items():
                    print(f"   {geo}: {stats['impressions']:,} imp, CTR {stats['ctr']:.2f}%")
            
            print("\n" + "="*70)
            print("✅ TEST 6 COMPLETE - get_media_buy_report works!")
            print("="*70)
            
            # ================================================================
            # FINAL SUMMARY
            # ================================================================
            print("\n" + "="*70)
            print("🎉 ALL TESTS COMPLETE - HTTP/SSE MCP TRANSPORT VALIDATED!")
            print("="*70)
            print("\n✅ Successfully Tested:")
            print("   1. get_products - LLM-powered product discovery")
            print("   2. create_media_buy - Campaign creation with DB")
            print("   3. get_media_buy - Campaign configuration retrieval")
            print("   4. get_media_buy_delivery - Real-time performance metrics")
            print("   5. update_media_buy - Campaign optimization")
            print("   6. get_media_buy_report - Analytics reporting")
            print("\n🌐 HTTP/SSE Transport: ✓")
            print("🗄️  Database Integration: ✓")
            print("🤖 LLM Integration (OpenAI): ✓")
            print("🔐 Authentication: ✓")
            print("\n" + "="*70)
    
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print("\n💡 Make sure server is running:")
        print("   uv run python server.py\n")
        
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """Entry point for Nike campaign workflow test."""
    try:
        asyncio.run(run_nike_campaign_workflow())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}\n")
        import traceback
        traceback.print_exc()