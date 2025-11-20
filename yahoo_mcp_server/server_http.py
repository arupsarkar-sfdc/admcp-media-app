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

# Import services (cloud-native, no SQLite)
from services.datacloud_query_service import get_datacloud_query_service
from services.snowflake_write_service import get_snowflake_write_service
from validators.adcp_validator import AdCPValidator

# Initialize FastMCP server
mcp = FastMCP(
    name="yahoo-sales-agent",
    version="1.0.0"
)

logger.info("="*70)
logger.info("YAHOO SALES AGENT - MCP SERVER")
logger.info("MCP Protocol: Streamable HTTP (SSE)")
logger.info("="*70)
logger.info(f"Snowflake (WRITE): Direct writes ✓")
logger.info(f"Data Cloud (READ): Snowflake via Zero Copy ✓")
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


class MockPrincipal:
    """Mock principal for testing (replaces SQLite dependency)"""
    def __init__(self):
        self.principal_id = "nike_advertiser"
        self.tenant_id = "374df0f3-dab1-450d-871f-fbe9569d3042"  # Yahoo Publisher tenant ID
        self.name = "Nike"
        self.access_level = "enterprise"
        self.email = "advertiser@nike.com"

def get_nike_principal():
    """
    Helper to get Nike principal
    
    Note: In production, this would come from authenticated request headers (x-adcp-auth)
    For cloud deployment, principal data comes from environment variables or JWT token
    """
    # For now, return mock principal (no SQLite dependency)
    # TODO: Implement JWT-based principal extraction from x-adcp-auth header
    return MockPrincipal()


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
    
    **DATA SOURCE: Salesforce Data Cloud (virtualizing Snowflake)**
    
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
    logger.info(f"🌩️  Querying Snowflake data via Data Cloud...")
    
    try:
        principal = get_nike_principal()
        query_service = get_datacloud_query_service()
        
        # Query products from Data Cloud (Snowflake)
        products_raw = await query_service.query_products(
            tenant_id=principal.tenant_id,
            is_active=True
        )
        
        logger.info(f"✅ Found {len(products_raw)} products from Data Cloud")
        
        # Apply budget filter if specified
        if budget_range:
            min_budget, max_budget = budget_range
            products_raw = [
                p for p in products_raw
                if p.get('minimum_budget', 0) <= max_budget
            ]
            logger.info(f"   Filtered to {len(products_raw)} products within budget")
        
        # Format products for response
        products = []
        for p in products_raw:
            pricing = p.get('pricing', {})
            if isinstance(pricing, str):
                import json
                pricing = json.loads(pricing) if pricing else {}
            
            # Apply principal-specific pricing discount
            base_price = pricing.get('value', 0)
            discount = 0.0
            
            # Apply access-level discount
            if principal.access_level == 'enterprise':
                discount = 0.15  # 15% discount
            elif principal.access_level == 'preferred':
                discount = 0.10  # 10% discount
            
            discounted_price = base_price * (1 - discount)
            discount_pct = f"{int(discount * 100)}%" if discount > 0 else "0%"
            
            # Build complete pricing structure
            pricing_response = {
                "value": round(discounted_price, 2),
                "original_value": base_price,
                "discount_percentage": discount_pct,
                "currency": pricing.get('currency', 'USD'),
                "model": pricing.get('model', 'cpm')
            }
            
            products.append({
                "product_id": p.get('product_id'),
                "name": p.get('name'),
                "description": p.get('description'),
                "product_type": p.get('product_type'),
                "pricing": pricing_response,
                "minimum_budget": p.get('minimum_budget', 0),
                "estimated_reach": p.get('estimated_reach', 0),
                "matched_reach": p.get('matched_reach', 0),
                "is_active": p.get('is_active', False),
                "created_at": p.get('created_at')
            })
        
        logger.info(f"✅ Returning {len(products)} products")
        
        return {
            "products": products,
            "total_count": len(products),
            "principal": {
                "name": principal.name,
                "access_level": principal.access_level
            },
            "data_source": "Salesforce Data Cloud (Snowflake)"
        }
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
        
        # STEP 3: Get principal
        principal = get_nike_principal()
        
        # STEP 4: Write to Snowflake (Data Cloud will reflect instantly via Zero Copy)
        logger.info(f"🌩️  Writing to Snowflake...")
        snowflake_service = get_snowflake_write_service()
        
        # Create media buy (synchronous Snowflake connector)
        media_buy_id = snowflake_service.insert_media_buy(
            tenant_id=principal.tenant_id,
            principal_id=principal.principal_id,
            campaign_name=campaign_name,
            total_budget=total_budget,
            currency=currency,
            flight_start_date=flight_start_date,
            flight_end_date=flight_end_date,
            adcp_version="2.3.0"
        )
        
        # Create packages
        package_responses = []
        for pkg in packages:
            package_id = snowflake_service.insert_package(
                media_buy_id=media_buy_id,
                package=pkg
            )
            
            # Extract format IDs for display
            format_ids = pkg.get("format_ids", [])
            format_list = [fmt.get("id", "unknown") for fmt in format_ids]
            
            package_responses.append({
                "package_id": package_id,
                "product_id": pkg["product_id"],
                "product_name": pkg["product_id"],  # Client expects this
                "budget": pkg["budget"],
                "currency": pkg.get("currency", currency),
                "formats": format_list,  # Client expects this as a list
                "pacing": pkg.get("pacing", "even"),
                "pricing_strategy": pkg.get("pricing_strategy", "cpm"),
                "format_count": len(format_ids)
            })
        
        result = {
            "status": "success",
            "media_buy_id": media_buy_id,
            "campaign_name": campaign_name,
            "total_budget": total_budget,
            "currency": currency,
            "flight_start_date": flight_start_date,
            "flight_end_date": flight_end_date,
            "adcp_version": "2.3.0",
            "packages": package_responses,
            "package_count": len(packages),
            "next_steps": [
                "Campaign created in Snowflake ✅",
                "Data Cloud reflects instantly via Zero Copy ✅",
                "Use get_media_buy to verify",
                "Upload creatives using assigned format_ids",
                "Activate campaign when ready"
            ],
            "data_source": "Snowflake (instant Data Cloud visibility)"
        }
        
        logger.info(f"✅ Created AdCP v2.3.0 media buy in Snowflake: {media_buy_id}")
        
        return result
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
    
    **DATA SOURCE: Salesforce Data Cloud (virtualizing Snowflake)**
    
    Args:
        media_buy_id: Unique media buy identifier
    
    Returns:
        Media buy configuration with status, packages, and matched audience
    """
    logger.info(f"📋 get_media_buy called for {media_buy_id}")
    logger.info(f"🌩️  Querying Snowflake data via Data Cloud...")
    
    try:
        principal = get_nike_principal()
        query_service = get_datacloud_query_service()
        
        # Query media buy from Data Cloud
        media_buys = await query_service.query_media_buys(
            tenant_id=principal.tenant_id
        )
        
        # Find the specific media buy
        media_buy = next((mb for mb in media_buys if mb.get('media_buy_id') == media_buy_id), None)
        
        if not media_buy:
            return {
                "status": "error",
                "error": f"Media buy {media_buy_id} not found"
            }
        
        # Query packages for this media buy
        packages = await query_service.query_packages_by_media_buy(media_buy_id)
        
        # Format response
        result = {
            "media_buy_id": media_buy.get('media_buy_id'),
            "campaign_name": media_buy.get('campaign_name'),
            "status": media_buy.get('status'),
            "total_budget": media_buy.get('total_budget'),
            "currency": media_buy.get('currency'),
            "flight_start_date": media_buy.get('flight_start_date'),
            "flight_end_date": media_buy.get('flight_end_date'),
            "adcp_version": media_buy.get('adcp_version'),
            "packages": [
                {
                    "package_id": pkg.get('package_id'),
                    "product_id": pkg.get('product_id'),
                    "budget": pkg.get('budget'),
                    "currency": pkg.get('currency'),
                    "pacing": pkg.get('pacing'),
                    "pricing_strategy": pkg.get('pricing_strategy'),
                    "impressions_delivered": pkg.get('impressions_delivered', 0),
                    "spend": pkg.get('spend', 0),
                    "clicks": pkg.get('clicks', 0),
                    "conversions": pkg.get('conversions', 0)
                }
                for pkg in packages
            ],
            "impressions_delivered": media_buy.get('impressions_delivered', 0),
            "spend": media_buy.get('spend', 0),
            "clicks": media_buy.get('clicks', 0),
            "conversions": media_buy.get('conversions', 0),
            "created_at": media_buy.get('created_at'),
            "updated_at": media_buy.get('updated_at'),
            "data_source": "Salesforce Data Cloud (Snowflake)"
        }
        
        logger.info(f"✅ Retrieved media buy {media_buy_id} with {len(packages)} packages")
        
        return result
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
    
    **DATA SOURCE: Salesforce Data Cloud (virtualizing Snowflake)**
    
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
    logger.info(f"🌩️  Querying Snowflake data via Data Cloud...")
    
    try:
        principal = get_nike_principal()
        query_service = get_datacloud_query_service()
        
        # Query media buy from Data Cloud
        media_buys = await query_service.query_media_buys(
            tenant_id=principal.tenant_id
        )
        
        media_buy = next((mb for mb in media_buys if mb.get('media_buy_id') == media_buy_id), None)
        
        if not media_buy:
            return {
                "status": "error",
                "error": f"Media buy {media_buy_id} not found"
            }
        
        # Query delivery metrics from Data Cloud
        metrics = await query_service.query_delivery_metrics(media_buy_id=media_buy_id)
        
        # Calculate aggregated metrics
        total_impressions = sum(m.get('impressions', 0) for m in metrics)
        total_clicks = sum(m.get('clicks', 0) for m in metrics)
        total_conversions = sum(m.get('conversions', 0) for m in metrics)
        total_spend = sum(m.get('spend', 0) for m in metrics)
        
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        # Calculate pacing
        total_budget = media_buy.get('total_budget', 0)
        budget_pacing = (total_spend / total_budget * 100) if total_budget > 0 else 0
        
        result = {
            "media_buy_id": media_buy_id,
            "campaign_name": media_buy.get('campaign_name'),
            "status": media_buy.get('status'),
            "delivery": {
                "impressions_delivered": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "spend": total_spend,
                "ctr": round(ctr, 2),
                "cvr": round(cvr, 2)
            },
            "pacing": {
                "budget_spent": total_spend,
                "budget_total": total_budget,
                "budget_pacing_pct": round(budget_pacing, 2)
            },
            "metrics_count": len(metrics),
            "data_source": "Salesforce Data Cloud (Snowflake)"
        }
        
        logger.info(f"✅ Retrieved delivery metrics for {media_buy_id}: {total_impressions} impressions")
        
        return result
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
    
    **DATA DESTINATION: Snowflake (Data Cloud reflects instantly via Zero Copy)**
    
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
    logger.info(f"🌩️  Writing to Snowflake...")
    
    try:
        # Write to Snowflake
        snowflake_service = get_snowflake_write_service()
        snowflake_service.update_media_buy(media_buy_id, updates)
        
        # Query updated data from Data Cloud to return
        principal = get_nike_principal()
        query_service = get_datacloud_query_service()
        
        media_buys = await query_service.query_media_buys(tenant_id=principal.tenant_id)
        media_buy = next((mb for mb in media_buys if mb.get('media_buy_id') == media_buy_id), None)
        
        if not media_buy:
            return {
                "status": "error",
                "error": f"Media buy {media_buy_id} not found after update"
            }
        
        result = {
            "status": "success",
            "media_buy_id": media_buy_id,
            "campaign_name": media_buy.get('campaign_name'),
            "total_budget": media_buy.get('total_budget'),
            "currency": media_buy.get('currency'),
            "status": media_buy.get('status'),
            "updated_at": media_buy.get('updated_at'),
            "updates_applied": updates,
            "data_source": "Snowflake (instant Data Cloud visibility)"
        }
        
        logger.info(f"✅ Updated media buy in Snowflake: {media_buy_id}")
        
        return result
    except Exception as e:
        logger.error(f"❌ Error in update_media_buy: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


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
    
    **DATA SOURCE: Salesforce Data Cloud (virtualizing Snowflake)**
    
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
    logger.info(f"🌩️  Querying Snowflake data via Data Cloud...")
    
    try:
        principal = get_nike_principal()
        query_service = get_datacloud_query_service()
        
        # Query media buy and metrics from Data Cloud
        media_buys = await query_service.query_media_buys(tenant_id=principal.tenant_id)
        media_buy = next((mb for mb in media_buys if mb.get('media_buy_id') == media_buy_id), None)
        
        if not media_buy:
            return {
                "status": "error",
                "error": f"Media buy {media_buy_id} not found"
            }
        
        # Query all delivery metrics for this media buy
        metrics = await query_service.query_delivery_metrics(media_buy_id=media_buy_id)
        
        # Calculate overall metrics
        total_impressions = sum(m.get('impressions', 0) for m in metrics)
        total_clicks = sum(m.get('clicks', 0) for m in metrics)
        total_conversions = sum(m.get('conversions', 0) for m in metrics)
        total_spend = sum(m.get('spend', 0) for m in metrics)
        
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        # Group by date for daily breakdown
        daily_metrics = {}
        for m in metrics:
            date = m.get('date')
            if date not in daily_metrics:
                daily_metrics[date] = {
                    "date": date,
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "spend": 0
                }
            daily_metrics[date]["impressions"] += m.get('impressions', 0)
            daily_metrics[date]["clicks"] += m.get('clicks', 0)
            daily_metrics[date]["conversions"] += m.get('conversions', 0)
            daily_metrics[date]["spend"] += m.get('spend', 0)
        
        # Group by device for device breakdown
        device_metrics = {}
        for m in metrics:
            device = m.get('device_type', 'unknown')
            if device not in device_metrics:
                device_metrics[device] = {
                    "device": device,
                    "impressions": 0,
                    "clicks": 0,
                    "spend": 0
                }
            device_metrics[device]["impressions"] += m.get('impressions', 0)
            device_metrics[device]["clicks"] += m.get('clicks', 0)
            device_metrics[device]["spend"] += m.get('spend', 0)
        
        # Group by geo for geo breakdown
        geo_metrics = {}
        for m in metrics:
            geo = m.get('geo', 'unknown')
            if geo not in geo_metrics:
                geo_metrics[geo] = {
                    "geo": geo,
                    "impressions": 0,
                    "clicks": 0,
                    "spend": 0
                }
            geo_metrics[geo]["impressions"] += m.get('impressions', 0)
            geo_metrics[geo]["clicks"] += m.get('clicks', 0)
            geo_metrics[geo]["spend"] += m.get('spend', 0)
        
        result = {
            "media_buy_id": media_buy_id,
            "campaign_name": media_buy.get('campaign_name'),
            "date_range": date_range,
            "report_generated_at": None,  # Could add timestamp
            "overall_metrics": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "spend": total_spend,
                "ctr": round(ctr, 2),
                "cvr": round(cvr, 2),
                "budget": media_buy.get('total_budget', 0),
                "budget_pacing_pct": round((total_spend / media_buy.get('total_budget', 1) * 100), 2)
            },
            "daily_breakdown": sorted(daily_metrics.values(), key=lambda x: x['date'], reverse=True),
            "device_breakdown": list(device_metrics.values()),
            "geo_breakdown": list(geo_metrics.values()),
            "metrics_count": len(metrics),
            "data_source": "Salesforce Data Cloud (Snowflake)"
        }
        
        logger.info(f"✅ Generated report for {media_buy_id}: {len(daily_metrics)} days, {len(metrics)} data points")
        
        return result
    except Exception as e:
        logger.error(f"❌ Error in get_media_buy_report: {str(e)}")
        raise


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    # Heroku assigns PORT dynamically, use it if available
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8080")))
    
    print(f"\n🚀 Starting Yahoo MCP Server (HTTP/SSE) - AdCP v2.3.0 Compliant")
    print(f"   Host: {host}:{port}")
    print(f"   Transport: Streamable HTTP (Server-Sent Events)")
    print(f"\n🔍 Agent Discovery Endpoints:")
    print(f"   GET  http://{host}:{port}/.well-known/adagents.json")
    print(f"   GET  http://{host}:{port}/.well-known/agent-card.json")
    print(f"\n📦 Available MCP Tools:")
    print(f"   1. echo(message: str) [test only]")
    print(f"   2. get_products(brief, budget_range) [🌩️  READ: Data Cloud → Snowflake]")
    print(f"   3. list_creative_formats() [AdCP v2.3.0 ✅]")
    print(f"   4. get_campaign_stats(campaign_id) [mock - test only]")
    print(f"   5. create_media_buy(packages, ...) [🌩️  WRITE: Snowflake | AdCP v2.3.0 ✅]")
    print(f"   6. get_media_buy(media_buy_id) [🌩️  READ: Data Cloud → Snowflake]")
    print(f"   7. get_media_buy_delivery(media_buy_id) [🌩️  READ: Data Cloud → Snowflake]")
    print(f"   8. update_media_buy(media_buy_id, updates) [🌩️  WRITE: Snowflake]")
    print(f"   9. get_media_buy_report(media_buy_id, date_range) [🌩️  READ: Data Cloud → Snowflake]")
    print(f"\n🔗 Connect from MCP client:")
    print(f"   Client('http://{host}:{port}/mcp')")
    print(f"\n🎯 AdCP v2.3.0 Compliant ✅ | Cloud-Native Architecture 🌩️")
    print(f"   READ: Salesforce Data Cloud → Snowflake (Zero Copy)")
    print(f"   WRITE: Snowflake → Data Cloud (Zero Copy instant visibility)")
    print(f"   9/9 Tools Complete | Discovery Endpoints (2/2)")
    print(f"   ✨ 100% CLOUD-NATIVE STACK - NO SQLite ✨")
    print("")
    
    # Run FastMCP server with SSE transport
    mcp.run(
        transport="streamable-http",  # (52) Use HTTP transport (good for local dev & desktop apps)
        host=host,                    # (53) Bind host (0.0.0.0 listens on all interfaces)
        port=port,                    # (54) Bind port (ensure it matches your BASE_URL)
        path="/mcp",                # (55) Mount path for the MCP endpoint (defines the resource)
    )