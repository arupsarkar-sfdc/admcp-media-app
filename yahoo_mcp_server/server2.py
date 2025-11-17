"""
Yahoo Sales Agent - MCP Server
Implements AdCP Media Buy Protocol v2.3.0
Following MCP Specification: https://modelcontextprotocol.io/specification/2025-06-18
Transport: HTTP with Server-Sent Events (SSE)
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import FastMCP
from fastmcp import FastMCP

# Import models and services
from models import get_session, Principal
from services.product_service import ProductService
from services.media_buy_service import MediaBuyService
from services.metrics_service import MetricsService

# Database path
DATABASE_PATH = os.getenv("DATABASE_PATH", "../database/adcp_platform.db")

# Initialize FastMCP server
mcp = FastMCP(
    name="yahoo-sales-agent",
    version="2.3.0"
)

logger.info("="*70)
logger.info("YAHOO SALES AGENT - MCP SERVER")
logger.info("MCP Protocol: Streamable HTTP (SSE)")
logger.info("="*70)
logger.info(f"Database: {DATABASE_PATH}")
logger.info(f"Port: {os.getenv('MCP_PORT', 8080)}")
logger.info(f"LLM: Gemini {'✓' if os.getenv('GEMINI_API_KEY') else '✗'} | OpenAI {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
logger.info("="*70)


def get_nike_principal():
    """
    Helper to get Nike principal from database
    Note: In production, this would come from authenticated request headers (x-adcp-auth)
    """
    session = get_session(DATABASE_PATH)
    try:
        principal = session.query(Principal).filter(
            Principal.principal_id == "nike_advertiser"
        ).first()
        
        if not principal:
            logger.error("Nike principal not found in database")
            raise ValueError("Nike principal not found. Run database/seed_data.py first.")
        
        return principal
    except Exception as e:
        logger.error(f"Error getting principal: {str(e)}")
        raise
    finally:
        session.close()


@mcp.tool()
async def get_products(
    brief: str,
    budget_range: Optional[list[int]] = None
) -> dict:
    """
    Discover advertising inventory using natural language brief.
    
    This tool searches Yahoo's advertising inventory across all properties
    and returns matching products with:
    - Pricing (CPM with principal-specific discounts)
    - Estimated reach and impressions
    - Matched audience data (from Clean Room)
    - Targeting capabilities
    - Creative format requirements
    
    Args:
        brief: Natural language description of campaign objectives
               Example: "Display ads for sports enthusiasts interested in running gear,
               targeting US users aged 25-45, budget $50,000"
        budget_range: Optional [min, max] budget in USD
    
    Returns:
        Dict with products list and total count
    """
    logger.info(f"📦 get_products called with brief: {brief[:60]}...")
    
    try:
        principal = get_nike_principal()
        
        session = get_session(DATABASE_PATH)
        try:
            service = ProductService(session)
            
            products = await service.discover_products(
                brief=brief,
                budget_range=budget_range,
                principal=principal,
                tenant_id=principal.tenant_id
            )
            
            logger.info(f"✅ Discovered {len(products)} products")
            
            return {
                "products": products,
                "total_count": len(products),
                "principal": {
                    "name": principal.name,
                    "access_level": principal.access_level
                }
            }
        finally:
            session.close()
    except Exception as e:
        logger.error(f"❌ Error in get_products: {str(e)}")
        raise


@mcp.tool()
async def create_media_buy(
    product_ids: list[str],
    total_budget: float,
    flight_start_date: str,
    flight_end_date: str,
    targeting: Optional[dict] = None,
    creative_ids: Optional[list[str]] = None
) -> dict:
    """
    Create a new advertising campaign (media buy).
    
    This tool:
    1. Validates product IDs and budget allocation
    2. Creates campaign in database
    3. Links to matched audience from Clean Room
    4. Returns media buy ID for tracking
    
    Args:
        product_ids: List of Yahoo product IDs to activate
        total_budget: Total campaign budget in USD
        flight_start_date: Campaign start date (YYYY-MM-DD)
        flight_end_date: Campaign end date (YYYY-MM-DD)
        targeting: Optional additional targeting parameters
        creative_ids: Optional list of creative IDs to assign
    
    Returns:
        Media buy response with ID, status, and next steps
    """
    logger.info(f"🚀 create_media_buy called for products: {product_ids}")
    
    try:
        principal = get_nike_principal()
        
        session = get_session(DATABASE_PATH)
        try:
            service = MediaBuyService(session)
            
            result = await service.create_media_buy(
                principal=principal,
                product_ids=product_ids,
                total_budget=total_budget,
                flight_start_date=flight_start_date,
                flight_end_date=flight_end_date,
                targeting=targeting,
                creative_ids=creative_ids
            )
            
            logger.info(f"✅ Created media buy: {result['media_buy_id']}")
            
            return result
        finally:
            session.close()
    except Exception as e:
        logger.error(f"❌ Error in create_media_buy: {str(e)}")
        raise


@mcp.tool()
async def get_media_buy(media_buy_id: str) -> dict:
    """
    Get campaign configuration details.
    
    Args:
        media_buy_id: Unique media buy identifier
    
    Returns:
        Media buy configuration with status and matched audience
    """
    logger.info(f"📋 get_media_buy called for {media_buy_id}")
    
    try:
        principal = get_nike_principal()
        
        session = get_session(DATABASE_PATH)
        try:
            service = MediaBuyService(session)
            return await service.get_media_buy(media_buy_id, principal)
        finally:
            session.close()
    except Exception as e:
        logger.error(f"❌ Error in get_media_buy: {str(e)}")
        raise


@mcp.tool()
async def get_media_buy_delivery(media_buy_id: str) -> dict:
    """
    Get real-time performance metrics for an active campaign.
    
    Returns:
    - Impressions delivered
    - Spend (cumulative)
    - Click-through rate (CTR)
    - Conversions
    - Conversion rate (CVR)
    - Delivery pacing (vs. budget/schedule)
    
    Metrics include matched audience data from Clean Room.
    
    Args:
        media_buy_id: Unique campaign identifier
    
    Returns:
        Delivery metrics with CTR, CVR, pacing, and matched audience info
    """
    logger.info(f"📊 get_media_buy_delivery called for {media_buy_id}")
    
    try:
        principal = get_nike_principal()
        
        session = get_session(DATABASE_PATH)
        try:
            service = MetricsService(session)
            result = await service.get_media_buy_delivery(media_buy_id, principal)
            
            logger.info(f"✅ Returned metrics: {result['delivery']['impressions']} impressions")
            
            return result
        finally:
            session.close()
    except Exception as e:
        logger.error(f"❌ Error in get_media_buy_delivery: {str(e)}")
        raise


@mcp.tool()
async def update_media_buy(
    media_buy_id: str,
    updates: dict
) -> dict:
    """
    Modify an active campaign configuration.
    
    Allows updates to:
    - Budget (increase/decrease)
    - Targeting parameters
    - Campaign status (active/paused)
    
    Args:
        media_buy_id: Campaign to update
        updates: Fields to modify (e.g., {"total_budget": 65000, "status": "active"})
    
    Returns:
        Updated campaign configuration
    """
    logger.info(f"⚙️ update_media_buy called for {media_buy_id}")
    
    try:
        principal = get_nike_principal()
        
        session = get_session(DATABASE_PATH)
        try:
            service = MediaBuyService(session)
            result = await service.update_media_buy(media_buy_id, updates, principal)
            
            logger.info(f"✅ Updated media buy: {media_buy_id}")
            
            return result
        finally:
            session.close()
    except Exception as e:
        logger.error(f"❌ Error in update_media_buy: {str(e)}")
        raise


@mcp.tool()
async def get_media_buy_report(
    media_buy_id: str,
    date_range: str = "last_7_days"
) -> dict:
    """
    Generate comprehensive analytics report.
    
    Includes:
    - Daily performance breakdown
    - Device/geo performance
    - Overall metrics with matched audience insights
    
    Args:
        media_buy_id: Campaign identifier
        date_range: Report time range ("last_7_days", "last_30_days", "lifetime")
    
    Returns:
        Detailed analytics report with breakdowns
    """
    logger.info(f"📈 get_media_buy_report called for {media_buy_id}")
    
    try:
        principal = get_nike_principal()
        
        session = get_session(DATABASE_PATH)
        try:
            service = MetricsService(session)
            result = await service.get_media_buy_report(media_buy_id, principal, date_range)
            
            logger.info(f"✅ Generated report for {media_buy_id}")
            
            return result
        finally:
            session.close()
    except Exception as e:
        logger.error(f"❌ Error in get_media_buy_report: {str(e)}")
        raise


if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", 8080))
    
    # logger.info(f"\n🚀 Starting Yahoo MCP Server (Streamable HTTP + SSE)")
    # logger.info(f"   Host: {host}")
    # logger.info(f"   Port: {port}")
    # logger.info(f"   SSE Endpoint: http://{host}:{port}/sse")
    # logger.info(f"\n📚 MCP Protocol Specification:")
    # logger.info(f"   https://modelcontextprotocol.io/specification/2025-06-18")
    # logger.info(f"\n🔌 Connect with MCP Client (see test_mcp_client.py)")
    # logger.info("")
    
    # Just pass "sse" as a string - FastMCP handles it internally
    # mcp.run(transport="sse", host=host, port=port)
    mcp.run(transport="stdio")