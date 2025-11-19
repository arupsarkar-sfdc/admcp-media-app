"""
Yahoo MCP Server - AdCP v2.3.0 Compliant
FastMCP implementation with Agent Discovery endpoints
Following: https://gofastmcp.com/deployment/http
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.responses import JSONResponse

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import models and services (for real tools)
from models import get_session, Principal
from services.product_service import ProductService
from services.media_buy_service import MediaBuyService
from services.metrics_service import MetricsService
from validators.adcp_validator import AdCPValidator

# Database path
DATABASE_PATH = os.getenv("DATABASE_PATH", "../database/adcp_platform.db")

# Initialize FastMCP server
mcp = FastMCP(
    name="yahoo-sales-agent",
    version="1.0.0"
)

logger.info("="*70)
logger.info("YAHOO SALES AGENT - MCP SERVER")
logger.info("MCP Protocol: Streamable HTTP (SSE)")
logger.info("="*70)
logger.info(f"Database: {DATABASE_PATH}")
logger.info(f"Port: {os.getenv('MCP_PORT', 8080)}")
logger.info(f"LLM: Gemini {'✓' if os.getenv('GEMINI_API_KEY') else '✗'} | OpenAI {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
logger.info("="*70)


# ============================================================================
# AGENT DISCOVERY ENDPOINTS (AdCP v2.3.0)
# ============================================================================

@mcp.custom_route("/.well-known/adagents.json", methods=["GET"])
async def adagents_discovery(request):
    """
    Agent Discovery Manifest (AdCP v2.3.0)
    Returns list of available advertising agents and their capabilities
    """
    base_url = os.getenv("MCP_BASE_URL", f"http://localhost:{os.getenv('MCP_PORT', 8080)}")
    
    return JSONResponse({
        "agents": [
            {
                "agent_url": f"{base_url}/mcp",
                "name": "yahoo-sales-agent",
                "version": "1.0.0",
                "description": "Yahoo Advertising Platform - AdCP v2.3.0 Compliant Sales Agent",
                "capabilities": [
                    "product_discovery",
                    "media_buy_creation",
                    "creative_formats",
                    "delivery_metrics",
                    "campaign_reporting"
                ],
                "protocols": ["mcp/1.0"],
                "supported_adcp_version": "2.3.0",
                "creative_formats_endpoint": f"{base_url}/mcp/list_creative_formats"
            }
        ]
    })


@mcp.custom_route("/.well-known/agent-card.json", methods=["GET"])
async def agent_card(request):
    """
    Agent Business Card (AdCP v2.3.0)
    Returns organizational and contact information
    """
    return JSONResponse({
        "organization": "Yahoo Advertising",
        "agent_name": "yahoo-sales-agent",
        "contact_email": "adcp-support@yahooinc.com",
        "website": "https://advertising.yahoo.com",
        "documentation": "https://advertising.yahoo.com/adcp/docs",
        "terms_of_service": "https://advertising.yahoo.com/terms",
        "privacy_policy": "https://advertising.yahoo.com/privacy",
        "adcp_version": "2.3.0",
        "mcp_version": "1.0",
        "supported_transports": ["http", "sse"],
        "rate_limits": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000
        },
        "availability": {
            "status": "operational",
            "uptime_sla": "99.9%"
        }
    })


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


# ============================================================================
# TOOL 1: Simple Echo (Test Tool)
# ============================================================================

@mcp.tool()
async def echo(message: str) -> dict:
    """
    Simple echo tool for testing
    
    Args:
        message: Message to echo back
    
    Returns:
        Dict with echoed message
    """
    print(f"📢 echo called with: {message}")
    return {
        "echo": message,
        "status": "success"
    }


# ============================================================================
# TOOL 2: Get Products (REAL - with LLM + Database)
# ============================================================================

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


# ============================================================================
# TOOL 3: List Creative Formats (AdCP v2.3.0)
# ============================================================================

@mcp.tool()
async def list_creative_formats() -> dict:
    """
    List available creative formats for campaign creation.
    
    Returns specifications for display, video, and native ad formats
    including dimensions, file types, size limits, and technical requirements.
    
    This tool is essential for AdCP v2.3.0 compliance - it provides the
    format_ids that buyers must reference when creating media buys.
    
    Returns:
        Dict with formats array containing format specifications
    """
    logger.info("🎨 list_creative_formats called")
    
    base_url = os.getenv("MCP_BASE_URL", f"http://localhost:{os.getenv('MCP_PORT', 8080)}")
    
    return {
        "agent_url": f"{base_url}/mcp",
        "formats": [
            # Display Formats
            {
                "id": "display_300x250",
                "name": "Display - Medium Rectangle",
                "type": "display",
                "dimensions": {"width": 300, "height": 250},
                "file_types": ["jpg", "png", "gif"],
                "max_file_size_kb": 150,
                "aspect_ratio": "6:5"
            },
            {
                "id": "display_728x90",
                "name": "Display - Leaderboard",
                "type": "display",
                "dimensions": {"width": 728, "height": 90},
                "file_types": ["jpg", "png", "gif"],
                "max_file_size_kb": 150,
                "aspect_ratio": "8.09:1"
            },
            {
                "id": "display_160x600",
                "name": "Display - Wide Skyscraper",
                "type": "display",
                "dimensions": {"width": 160, "height": 600},
                "file_types": ["jpg", "png", "gif"],
                "max_file_size_kb": 150,
                "aspect_ratio": "4:15"
            },
            {
                "id": "display_320x50",
                "name": "Display - Mobile Banner",
                "type": "display",
                "dimensions": {"width": 320, "height": 50},
                "file_types": ["jpg", "png", "gif"],
                "max_file_size_kb": 50,
                "aspect_ratio": "32:5"
            },
            # Video Formats
            {
                "id": "video_16x9_15s",
                "name": "Video - Widescreen 15s",
                "type": "video",
                "aspect_ratio": "16:9",
                "duration_seconds": 15,
                "min_duration_seconds": 6,
                "max_duration_seconds": 15,
                "file_types": ["mp4", "mov"],
                "max_file_size_mb": 100,
                "codec": "H.264",
                "audio_codec": "AAC"
            },
            {
                "id": "video_16x9_30s",
                "name": "Video - Widescreen 30s",
                "type": "video",
                "aspect_ratio": "16:9",
                "duration_seconds": 30,
                "min_duration_seconds": 15,
                "max_duration_seconds": 30,
                "file_types": ["mp4", "mov"],
                "max_file_size_mb": 200,
                "codec": "H.264",
                "audio_codec": "AAC"
            },
            {
                "id": "video_9x16_15s",
                "name": "Video - Vertical 15s",
                "type": "video",
                "aspect_ratio": "9:16",
                "duration_seconds": 15,
                "min_duration_seconds": 6,
                "max_duration_seconds": 15,
                "file_types": ["mp4", "mov"],
                "max_file_size_mb": 100,
                "codec": "H.264",
                "audio_codec": "AAC"
            },
            # Native Formats
            {
                "id": "native_content_feed",
                "name": "Native - Content Feed",
                "type": "native",
                "components": {
                    "title": {"max_length": 25, "required": True},
                    "description": {"max_length": 90, "required": True},
                    "image": {
                        "dimensions": {"width": 1200, "height": 628},
                        "file_types": ["jpg", "png"],
                        "max_file_size_kb": 300,
                        "required": True
                    },
                    "cta_text": {"max_length": 15, "required": False},
                    "brand_name": {"max_length": 25, "required": True}
                }
            },
            {
                "id": "native_in_stream",
                "name": "Native - In-Stream",
                "type": "native",
                "components": {
                    "title": {"max_length": 40, "required": True},
                    "description": {"max_length": 140, "required": True},
                    "thumbnail": {
                        "dimensions": {"width": 600, "height": 600},
                        "file_types": ["jpg", "png"],
                        "max_file_size_kb": 200,
                        "required": True
                    },
                    "brand_logo": {
                        "dimensions": {"width": 200, "height": 200},
                        "file_types": ["png"],
                        "max_file_size_kb": 50,
                        "required": True
                    }
                }
            }
        ],
        "total_count": 9,
        "supported_adcp_version": "2.3.0"
    }


# ============================================================================
# TOOL 4: Get Campaign Stats (Mock - Test Only)
# ============================================================================

@mcp.tool()
async def get_campaign_stats(campaign_id: str) -> dict:
    """
    Get campaign statistics
    
    Args:
        campaign_id: Campaign identifier
    
    Returns:
        Mock campaign stats
    """
    print(f"📊 get_campaign_stats called for: {campaign_id}")
    
    # Return mock data
    return {
        "campaign_id": campaign_id,
        "status": "active",
        "impressions": 1500000,
        "clicks": 4500,
        "ctr": 0.003,
        "spend": 18750.00
    }


# ============================================================================
# TOOL 4: Create Media Buy (REAL - AdCP v2.3.0 Package-Based)
# ============================================================================

@mcp.tool()
async def create_media_buy(
    campaign_name: str,
    packages: list[dict],
    flight_start_date: str,
    flight_end_date: str,
    currency: str = "USD"
) -> dict:
    """
    Create a new advertising campaign (media buy) using AdCP v2.3.0 package structure.
    
    **AdCP v2.3.0 Package Structure**:
    Each package must contain:
    - product_id (str, required): Yahoo product ID from get_products
    - budget (float, required): Per-package budget allocation
    - format_ids (list[dict], required): Creative formats as [{"agent_url": "...", "id": "..."}]
    - targeting_overlay (dict, optional): Package-specific targeting
    - pacing (str, optional): "even", "asap", or "frontloaded"
    - pricing_strategy (str, optional): "cpm", "cpc", "cpa", or "cpv"
    
    **Example**:
    ```python
    packages = [
        {
            "product_id": "yahoo_homepage_premium_desktop",
            "budget": 30000,
            "format_ids": [
                {"agent_url": "http://localhost:8080/mcp", "id": "display_728x90"},
                {"agent_url": "http://localhost:8080/mcp", "id": "display_300x250"}
            ],
            "targeting_overlay": {"device": ["desktop"]},
            "pacing": "even"
        },
        {
            "product_id": "yahoo_mail_native_mobile",
            "budget": 20000,
            "format_ids": [
                {"agent_url": "http://localhost:8080/mcp", "id": "native_feed"}
            ],
            "targeting_overlay": {"device": ["mobile"]},
            "pacing": "frontloaded"
        }
    ]
    ```
    
    **Workflow**:
    1. Call `list_creative_formats` to discover supported format_ids
    2. Call `get_products` to discover available products
    3. Build packages with required format_ids
    4. Call this tool to create the campaign
    
    Args:
        campaign_name: Human-readable campaign name
        packages: List of AdCP v2.3.0 package dictionaries
        flight_start_date: Campaign start date (YYYY-MM-DD)
        flight_end_date: Campaign end date (YYYY-MM-DD)
        currency: Currency code (default: USD)
    
    Returns:
        Media buy response with ID, status, package details, and next steps
    """
    logger.info(f"🚀 create_media_buy called: {campaign_name} with {len(packages)} package(s)")
    
    try:
        # STEP 1: Validate AdCP v2.3.0 package structure
        is_valid, error_msg = AdCPValidator.validate_packages(packages)
        if not is_valid:
            logger.error(f"❌ AdCP validation failed: {error_msg}")
            return {
                "status": "error",
                "error": f"AdCP v2.3.0 validation failed: {error_msg}",
                "hint": "Call list_creative_formats to discover valid format_ids"
            }
        
        # STEP 2: Calculate total budget
        total_budget = AdCPValidator.calculate_total_budget(packages)
        logger.info(f"📊 Total budget: ${total_budget:,.2f} across {len(packages)} package(s)")
        
        # STEP 3: Extract product_ids for service layer (backward compatibility)
        product_ids = [pkg["product_id"] for pkg in packages]
        
        # STEP 4: Get principal and create media buy
        principal = get_nike_principal()
        
        session = get_session(DATABASE_PATH)
        try:
            service = MediaBuyService(session)
            
            result = await service.create_media_buy_v2(
                principal=principal,
                campaign_name=campaign_name,
                packages=packages,
                total_budget=total_budget,
                flight_start_date=flight_start_date,
                flight_end_date=flight_end_date,
                currency=currency
            )
            
            logger.info(f"✅ Created AdCP v2.3.0 media buy: {result['media_buy_id']}")
            
            return result
        finally:
            session.close()
    except Exception as e:
        logger.error(f"❌ Error in create_media_buy: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# TOOL 5: Get Media Buy (REAL - with Database)
# ============================================================================

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


# ============================================================================
# TOOL 6: Get Media Buy Delivery (REAL - with Database)
# ============================================================================

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


# ============================================================================
# TOOL 7: Update Media Buy (REAL - with Database)
# ============================================================================

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


# ============================================================================
# TOOL 8: Get Media Buy Report (REAL - with Database)
# ============================================================================

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


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", 8080))
    
    print(f"\n🚀 Starting Yahoo MCP Server (HTTP/SSE) - AdCP v2.3.0 Compliant")
    print(f"   Host: {host}:{port}")
    print(f"   Transport: Streamable HTTP (Server-Sent Events)")
    print(f"\n🔍 Agent Discovery Endpoints:")
    print(f"   GET  http://{host}:{port}/.well-known/adagents.json")
    print(f"   GET  http://{host}:{port}/.well-known/agent-card.json")
    print(f"\n📦 Available MCP Tools:")
    print(f"   1. echo(message: str) [mock - test only]")
    print(f"   2. get_products(brief, budget_range) [REAL - LLM + DB]")
    print(f"   3. list_creative_formats() [REAL - AdCP v2.3.0 ✅]")
    print(f"   4. get_campaign_stats(campaign_id) [mock - test only]")
    print(f"   5. create_media_buy(packages, ...) [REAL - AdCP v2.3.0 Package-Based ✅]")
    print(f"   6. get_media_buy(media_buy_id) [REAL - DB]")
    print(f"   7. get_media_buy_delivery(media_buy_id) [REAL - DB]")
    print(f"   8. update_media_buy(media_buy_id, updates) [REAL - DB]")
    print(f"   9. get_media_buy_report(media_buy_id, date_range) [REAL - DB]")
    print(f"\n🔗 Connect from MCP client:")
    print(f"   Client('http://{host}:{port}/mcp')")
    print(f"\n🎯 AdCP v2.3.0 Compliant ✅ | 8/8 Tools Complete | Discovery Endpoints (2/2)")
    print("")
    
    # Run FastMCP server with SSE transport
    mcp.run(
        transport="streamable-http",  # (52) Use HTTP transport (good for local dev & desktop apps)
        host=host,                    # (53) Bind host (0.0.0.0 listens on all interfaces)
        port=port,                    # (54) Bind port (ensure it matches your BASE_URL)
        path="/mcp",                # (55) Mount path for the MCP endpoint (defines the resource)
    )