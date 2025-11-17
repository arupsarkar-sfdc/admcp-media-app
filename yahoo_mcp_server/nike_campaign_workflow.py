"""
Nike Campaign Manager - Complete Workflow
Tests the full campaign lifecycle with Yahoo MCP Server via stdio transport

Workflow (from README_Media_Workflow.md):
1. Product Discovery - Find Yahoo inventory matching campaign brief
2. Campaign Creation - Create media buy for selected products
3. Performance Monitoring - Check real-time delivery metrics
4. Analytics Report - Generate comprehensive campaign report
5. Campaign Optimization - Update campaign parameters

Transport: stdio (spawns server2.py as subprocess)
"""
"""
Nike Campaign Workflow - MCP Client (FIXED)
Demonstrates full campaign lifecycle using Yahoo Sales Agent
Proper async context management
"""
import asyncio
import json
import sys
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# Logging Setup - Dual output to terminal AND log file
# ============================================================
class DualLogger:
    """Write to both terminal and log file"""
    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log = open(log_file, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()  # Ensure immediate write
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()


# Create log file with timestamp
log_filename = f"nike_campaign_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
dual_logger = DualLogger(log_filename)
sys.stdout = dual_logger
sys.stderr = dual_logger

print(f"📝 Logging to: {log_filename}")
print("="*70)


async def run_nike_campaign_workflow():
    """
    Complete Nike → Yahoo advertising workflow
    Following AdCP Media Buy Protocol v2.3.0
    """
    
    print("\n" + "="*70)
    print("NIKE-YAHOO ADVERTISING CAMPAIGN")
    print("AdCP Media Buy Protocol v2.3.0")
    print("Transport: MCP over stdio")
    print("="*70)
    
    print("\n" + "👟"*35)
    print("NIKE CAMPAIGN MANAGER")
    print("Full Workflow with Yahoo Sales Agent (MCP Server)")
    print("👟"*35)
    
    # Configure Yahoo MCP Server
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "server2.py"],
        env=None
    )
    
    # Use proper nested context managers
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # ============================================================
            # Initialize Connection
            # ============================================================
            print("\n" + "="*70)
            print("🔌 NIKE → Connecting to Yahoo Sales Agent")
            print("="*70)
            
            await session.initialize()
            print("✅ Connected to Yahoo Sales Agent (MCP Server)")
            
            # List available tools
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print(f"📦 Available tools: {tool_names}\n")
            
            # ============================================================
            # STEP 1: Product Discovery
            # ============================================================
            print("="*70)
            print("📦 STEP 1: Product Discovery with Natural Language")
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
            
            print(f"Campaign Brief:")
            print(f"{campaign_brief.strip()}\n")
            
            print("🔍 Querying Yahoo advertising inventory...")
            
            result = await session.call_tool(
                "get_products",
                arguments={
                    "brief": campaign_brief.strip(),
                    "budget_range": [10000, 100000]
                }
            )
            
            # Parse response
            products_response = json.loads(result.content[0].text)
            products = products_response['products']
            
            print(f"\n✅ Found {products_response['total_count']} matching products")
            print(f"   Principal: {products_response['principal']['name']} ({products_response['principal']['access_level']})\n")
            
            # Display product details
            print("📦 Available Products:\n")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product['name']}")
                print(f"   Product ID: {product['product_id']}")
                print(f"   Type: {product['product_type'].upper()}")
                print(f"   CPM: ${product['pricing']['value']:.2f} (${product['pricing']['original_value']:.2f} - {product['pricing']['discount_percentage']} discount)")
                print(f"   Est. Reach: {product['estimated_reach']:,} users")
                print(f"   Min Budget: ${product['minimum_budget']:,.0f}")
                
                # Show matched audience from Clean Room
                if product.get('matched_audiences'):
                    print(f"   🎯 Matched Audiences (Clean Room):")
                    for ma in product['matched_audiences']:
                        print(f"      - {ma['segment_name']}")
                        print(f"        Overlap: {ma['overlap_count']:,} users ({ma['match_rate']:.1%})")
                        print(f"        Engagement: {ma['engagement_score']:.0%}")
                
                print()
            
            # ============================================================
            # STEP 2: Check Existing Campaign Performance
            # ============================================================
            print("="*70)
            print("📊 STEP 2: Monitor Existing Campaign Performance")
            print("="*70)
            
            existing_campaign_id = "nike_air_max_spring_q1"
            print(f"Campaign ID: {existing_campaign_id}\n")
            
            print("🔍 Fetching real-time metrics...")
            
            result = await session.call_tool(
                "get_media_buy_delivery",
                arguments={
                    "media_buy_id": existing_campaign_id
                }
            )
            
            metrics_response = json.loads(result.content[0].text)
            delivery = metrics_response['delivery']
            performance = metrics_response['performance']
            
            print(f"\n✅ Campaign Performance:")
            print(f"   Status: {metrics_response['status'].upper()}")
            print(f"   Impressions: {delivery['impressions']:,}")
            print(f"   Clicks: {delivery['clicks']:,}")
            print(f"   Conversions: {delivery['conversions']:,}")
            print(f"   Spend: ${delivery['spend']:,.2f}")
            print(f"   CTR: {performance['ctr']:.2f}%")
            print(f"   CVR: {performance['cvr']:.2f}%")
            print(f"   CPC: ${performance['cpc']:.2f}")
            print(f"   CPA: ${performance['cpa']:.2f}")
            
            # Show pacing info
            if 'pacing' in metrics_response:
                pacing = metrics_response['pacing']
                print(f"\n📈 Budget Pacing:")
                print(f"   Health: {pacing['health'].upper()}")
                print(f"   Budget: {pacing['budget_pacing']:.1f}%")
                print(f"   Time: {pacing['time_pacing']:.1f}%")
                print(f"   Days: {pacing['days_elapsed']}/{pacing['days_total']}")
            
            # Show matched audience from Clean Room
            if 'matched_audience' in metrics_response and metrics_response['matched_audience']:
                ma = metrics_response['matched_audience']
                print(f"\n🎯 Matched Audience (Privacy-Safe via Clean Room):")
                print(f"   Segment: {ma['segment_name']}")
                print(f"   Total Matched: {ma['overlap_count']:,} users")
                print(f"   Engagement Score: {ma['engagement_score']:.2f}")
                print(f"   Privacy: k-anonymity (k≥1000), differential privacy (ε=0.1)")
            
            # ============================================================
            # STEP 3: Campaign Configuration Details
            # ============================================================
            print("\n" + "="*70)
            print("📋 STEP 3: Campaign Configuration")
            print("="*70)
            
            result = await session.call_tool(
                "get_media_buy",
                arguments={
                    "media_buy_id": existing_campaign_id
                }
            )
            
            campaign_data = json.loads(result.content[0].text)
            
            print(f"\n✅ Campaign Details:")
            print(f"   Campaign ID: {campaign_data['media_buy_id']}")
            print(f"   Budget: ${campaign_data['total_budget']:,.2f}")
            print(f"   Flight: {campaign_data['flight_start_date']} to {campaign_data['flight_end_date']}")
            print(f"   Status: {campaign_data['status'].upper()}")
            
            if 'products' in campaign_data:
                print(f"\n📦 Products:")
                for product in campaign_data['products']:
                    print(f"   - {product['name']}")
            
            if 'targeting' in campaign_data and campaign_data['targeting']:
                print(f"\n🎯 Targeting:")
                targeting = campaign_data['targeting']
                if 'geo' in targeting:
                    print(f"   Geo: {', '.join(targeting['geo'])}")
                if 'age' in targeting:
                    print(f"   Age: {targeting['age'][0]}-{targeting['age'][1]}")
                if 'interests' in targeting:
                    print(f"   Interests: {', '.join(targeting['interests'])}")
            
            # ============================================================
            # STEP 4: Campaign Optimization (Optional)
            # ============================================================
            print("\n" + "="*70)
            print("⚙️  STEP 4: Campaign Optimization")
            print("="*70)
            
            print("\nAnalyzing performance...")
            
            # Check if optimization is needed
            if performance['ctr'] < 0.3:  # CTR below 0.3%
                print("⚠️  CTR below target (0.30%)")
                print("💡 Recommendation: Increase mobile budget allocation")
                
                optimize = input("\nApply optimization? (y/n): ").lower() == 'y'
                
                if optimize:
                    print("\n🔧 Applying optimization...")
                    print("   - Shifting 30% of budget to mobile")
                    print("   - Expanding geo targeting to CA, UK")
                    
                    result = await session.call_tool(
                        "update_media_buy",
                        arguments={
                            "media_buy_id": existing_campaign_id,
                            "updates": {
                                "targeting": {
                                    "geo": ["US", "CA", "UK"],
                                    "device_allocation": {
                                        "mobile": 0.70,
                                        "desktop": 0.30
                                    }
                                }
                            }
                        }
                    )
                    
                    update_response = json.loads(result.content[0].text)
                    print(f"\n✅ Campaign updated!")
                    print(f"   Changes effective immediately")
                    print(f"   Monitor for 48h before re-evaluating")
            else:
                print("✅ Campaign performing within target parameters")
            
            # ============================================================
            # STEP 5: Create New Campaign (Optional)
            # ============================================================
            print("\n" + "="*70)
            print("🚀 STEP 5: Create New Campaign")
            print("="*70)
            
            create_new = input("\nCreate a new test campaign? (y/n): ").lower() == 'y'
            
            if create_new:
                print("\n📝 New Campaign Configuration:")
                print("   Product: Yahoo Sports - Display (Sports Enthusiasts)")
                print("   Budget: $50,000")
                print("   Flight: March 1 - May 31, 2025")
                print("   Target: US users aged 25-45, sports interests")
                
                print("\n🚀 Creating campaign...")
                
                result = await session.call_tool(
                    "create_media_buy",
                    arguments={
                        "product_ids": ["yahoo_sports_display_enthusiasts"],
                        "total_budget": 50000.0,
                        "flight_start_date": "2025-03-01",
                        "flight_end_date": "2025-05-31",
                        "targeting": {
                            "geo": ["US"],
                            "age": [25, 45],
                            "interests": ["sports", "running", "fitness"]
                        }
                    }
                )
                
                new_campaign = json.loads(result.content[0].text)
                
                print(f"\n✅ Campaign Created Successfully!")
                print(f"   Campaign ID: {new_campaign['media_buy_id']}")
                print(f"   Status: {new_campaign['status'].upper()}")
                print(f"   Budget: ${new_campaign['total_budget']:,.2f}")
                print(f"   Flight: {new_campaign['flight_start_date']} to {new_campaign['flight_end_date']}")
                
                if new_campaign.get('status') == 'pending_approval':
                    print(f"\n📋 Next Steps:")
                    print(f"   1. Yahoo sales team will review (Est. 2-4 hours)")
                    print(f"   2. Upload creative assets")
                    print(f"   3. Campaign will go live on approval")
            else:
                print("\n⏭️  Skipping new campaign creation")
            
            # ============================================================
            # STEP 6: Generate Analytics Report
            # ============================================================
            print("\n" + "="*70)
            print("📈 STEP 6: Analytics Report")
            print("="*70)
            
            print(f"\n📊 Generating 7-day performance report...")
            
            result = await session.call_tool(
                "get_media_buy_report",
                arguments={
                    "media_buy_id": existing_campaign_id,
                    "date_range": "last_7_days"
                }
            )
            
            report = json.loads(result.content[0].text)
            overall = report['overall']
            delivery = overall['delivery']
            performance = overall['performance']
            
            print(f"\n✅ Report Generated:")
            print(f"   Period: {report['report_date_range']['start']} to {report['report_date_range']['end']}")
            print(f"   Total Impressions: {delivery['impressions']:,}")
            print(f"   Total Clicks: {delivery['clicks']:,}")
            print(f"   Total Conversions: {delivery['conversions']:,}")
            print(f"   Total Spend: ${delivery['spend']:,.2f}")
            print(f"   Avg CTR: {performance['ctr']:.2f}%")
            print(f"   Avg CVR: {performance['cvr']:.2f}%")
            
            if 'daily_breakdown' in report and report['daily_breakdown']:
                print(f"\n📅 Daily Performance (Last 3 Days):")
                for day in report['daily_breakdown'][-3:]:  # Show last 3 days
                    print(f"   {day['date']}: {day['impressions']:,} imp, {day['clicks']:,} clicks, CTR {day['ctr']:.2f}%")
            
            if 'device_breakdown' in report and report['device_breakdown']:
                print(f"\n📱 Device Breakdown:")
                for device in report['device_breakdown']:
                    print(f"   {device['device_type']}: {device['impressions']:,} imp, CTR {device['ctr']:.2f}%")
            
            # ============================================================
            # Workflow Complete
            # ============================================================
            print("\n" + "="*70)
            print("✅ NIKE CAMPAIGN WORKFLOW COMPLETE")
            print("="*70)
            
            print("\n📊 Summary:")
            print(f"   - Discovered {products_response['total_count']} advertising products")
            print(f"   - Monitored 1 active campaign")
            print(f"   - Generated performance report")
            if create_new:
                print(f"   - Created 1 new campaign")
            
            print(f"\n🎯 Key Insights:")
            if metrics_response.get('matched_audience'):
                print(f"   - Matched Audience: {metrics_response['matched_audience']['overlap_count']:,} users")
            print(f"   - Campaign CTR: {performance['ctr']:.2f}%")
            print(f"   - Budget Pacing: {metrics_response['pacing']['health'].upper()}")
            
            print(f"\n💡 Next Steps:")
            print(f"   1. Monitor campaign performance daily")
            print(f"   2. Optimize based on CTR/CVR trends")
            print(f"   3. Upload creative assets for new campaigns")
            print(f"   4. Review Clean Room analytics for attribution")
            
            print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(run_nike_campaign_workflow())
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        print("Campaign data preserved in database\n")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close log file
        print(f"\n📝 Log saved to: {log_filename}")
        dual_logger.close()
        sys.stdout = dual_logger.terminal
        sys.stderr = dual_logger.terminal