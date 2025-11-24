"""
Yahoo A2A Sales Agent Server

This server wraps the Yahoo MCP server with A2A protocol support,
enabling agent-to-agent communication using Google's A2A SDK.

Architecture:
    Nike A2A Agent → Yahoo A2A Server → Yahoo MCP Tools → Data Cloud/Snowflake
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn

# A2A SDK imports
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

# Import existing MCP services
from services.datacloud_query_service import get_datacloud_query_service
from services.snowflake_write_service import get_snowflake_write_service

# Define MockPrincipal here (same as in server_http.py)
class MockPrincipal:
    """Mock principal for authentication (no database dependency)"""
    def __init__(self, principal_id: str, name: str, tenant_id: str, access_level: str):
        self.principal_id = principal_id
        self.name = name
        self.tenant_id = tenant_id
        self.access_level = access_level
        self.email = f"{name.lower()}@example.com"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Yahoo A2A Sales Agent",
    description="A2A wrapper for Yahoo Advertising Platform",
    version="1.0.0"
)

# Load agent card
AGENT_CARD_PATH = Path(__file__).parent / "yahoo-agent-card.json"
with open(AGENT_CARD_PATH, 'r') as f:
    AGENT_CARD_DATA = json.load(f)

# =============================================================================
# Helper Functions
# =============================================================================

def get_nike_principal() -> MockPrincipal:
    """Get Nike principal for authentication"""
    return MockPrincipal(
        principal_id="nike_principal_001",
        name="Nike",
        tenant_id="374df0f3-dab1-450d-871f-fbe9569d3042",  # Yahoo tenant
        access_level="premium"
    )

# =============================================================================
# A2A Skills Implementation
# =============================================================================

def skill_echo(task_input: str) -> Dict[str, Any]:
    """
    Echo skill - returns the input message.
    Used for testing A2A connectivity.
    
    Args:
        task_input: The message to echo
        
    Returns:
        Dict with echoed message
    """
    logger.info(f"🔊 Echo skill called with input: {task_input}")
    return {
        "status": "success",
        "message": f"Echo from Yahoo A2A Agent: {task_input}",
        "agent": "yahoo_sales_agent",
        "skill": "echo"
    }

async def skill_discover_products(task_input: str) -> Dict[str, Any]:
    """
    Discover advertising products from Yahoo inventory.
    
    **DATA SOURCE: Salesforce Data Cloud (virtualizing Snowflake)**
    
    Args:
        task_input: JSON string with campaign brief and optional budget_range
                   Example: {"brief": "Display ads for sports", "budget_range": [10000, 50000]}
        
    Returns:
        Dict with products list and metadata
    """
    logger.info(f"📦 discover_products skill called")
    
    try:
        # Parse input
        input_data = json.loads(task_input) if isinstance(task_input, str) else task_input
        brief = input_data.get("brief", task_input if isinstance(task_input, str) else "")
        budget_range = input_data.get("budget_range")
        
        logger.info(f"   Brief: {brief[:60]}...")
        logger.info(f"🌩️  Querying Data Cloud (Snowflake)...")
        
        # Get services
        principal = get_nike_principal()
        query_service = get_datacloud_query_service()
        
        # Query products from Data Cloud
        products_raw = await query_service.query_products(
            tenant_id=principal.tenant_id,
            is_active=True
        )
        
        logger.info(f"✅ Found {len(products_raw)} products from Data Cloud")
        
        # Apply budget filter if specified
        if budget_range and isinstance(budget_range, list) and len(budget_range) == 2:
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
            products.append({
                "product_id": p.get('product_id'),
                "name": p.get('name'),
                "description": p.get('description'),
                "product_type": p.get('product_type'),
                "pricing": {
                    "base_cpm": pricing.get('base_cpm', 0),
                    "original_value": pricing.get('base_cpm', 0),
                    "discount_percentage": 0,
                    "currency": pricing.get('currency', 'USD')
                },
                "minimum_budget": p.get('minimum_budget', 0),
                "estimated_reach": p.get('estimated_reach', 0),
                "estimated_impressions": p.get('estimated_impressions', 0),
                "formats": p.get('formats', []),
                "targeting": p.get('targeting', {}),
                "properties": p.get('properties', [])
            })
        
        return {
            "status": "success",
            "skill": "discover_products",
            "data": {
                "products": products[:10],  # Limit to 10 for A2A response
                "total_count": len(products),
                "brief": brief,
                "data_source": "Salesforce Data Cloud (Snowflake Zero Copy)"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in discover_products: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "skill": "discover_products",
            "error": str(e)
        }

async def skill_create_campaign(task_input: str) -> Dict[str, Any]:
    """
    Create a new advertising campaign.
    
    **DATA DESTINATION: Snowflake (Data Cloud reflects instantly via Zero Copy)**
    
    Args:
        task_input: JSON string with campaign details
                   Example: {"product_ids": ["prod_123"], "budget": 25000, ...}
        
    Returns:
        Dict with created campaign details
    """
    logger.info(f"🎯 create_campaign skill called")
    
    try:
        # Parse input
        input_data = json.loads(task_input) if isinstance(task_input, str) else task_input
        
        logger.info(f"🌩️  Writing to Snowflake...")
        
        # Get services
        principal = get_nike_principal()
        write_service = get_snowflake_write_service()
        
        # Create media buy in Snowflake
        media_buy_id = await write_service.insert_media_buy(
            tenant_id=principal.tenant_id,
            principal_id=principal.principal_id,
            product_ids=input_data.get("product_ids", []),
            total_budget=input_data.get("budget", 0),
            flight_start_date=input_data.get("start_date", "2025-01-01"),
            flight_end_date=input_data.get("end_date", "2025-03-31"),
            targeting=input_data.get("targeting", {}),
            packages=input_data.get("packages", [])
        )
        
        logger.info(f"✅ Created campaign: {media_buy_id}")
        
        return {
            "status": "success",
            "skill": "create_campaign",
            "data": {
                "campaign_id": media_buy_id,
                "message": "Campaign created successfully in Snowflake",
                "data_destination": "Snowflake (reflected in Data Cloud via Zero Copy)"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in create_campaign: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "skill": "create_campaign",
            "error": str(e)
        }

async def skill_get_campaign_status(task_input: str) -> Dict[str, Any]:
    """
    Get campaign delivery status and metrics.
    
    **DATA SOURCE: Salesforce Data Cloud (virtualizing Snowflake)**
    
    Args:
        task_input: Campaign ID or JSON with campaign_id
        
    Returns:
        Dict with campaign status and delivery metrics
    """
    logger.info(f"📊 get_campaign_status skill called")
    
    try:
        # Parse input
        if isinstance(task_input, str):
            try:
                input_data = json.loads(task_input)
                campaign_id = input_data.get("campaign_id", task_input)
            except:
                campaign_id = task_input
        else:
            campaign_id = task_input.get("campaign_id", "")
        
        logger.info(f"   Campaign ID: {campaign_id}")
        logger.info(f"🌩️  Querying Data Cloud...")
        
        # Get services
        query_service = get_datacloud_query_service()
        
        # Query campaign delivery data
        delivery_data = await query_service.query_media_buy_delivery(campaign_id)
        
        if not delivery_data:
            return {
                "status": "error",
                "skill": "get_campaign_status",
                "error": f"Campaign {campaign_id} not found"
            }
        
        logger.info(f"✅ Retrieved campaign status")
        
        return {
            "status": "success",
            "skill": "get_campaign_status",
            "data": {
                "campaign_id": campaign_id,
                "impressions_delivered": delivery_data.get("impressions_delivered", 0),
                "spend": delivery_data.get("spend", 0),
                "pacing": delivery_data.get("pacing", {}),
                "data_source": "Salesforce Data Cloud (Snowflake Zero Copy)"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in get_campaign_status: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "skill": "get_campaign_status",
            "error": str(e)
        }

# Skill registry
SKILLS = {
    "echo": skill_echo,
    "discover_products": skill_discover_products,
    "create_campaign": skill_create_campaign,
    "get_campaign_status": skill_get_campaign_status,
}

# =============================================================================
# A2A Protocol Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Yahoo A2A Sales Agent",
        "status": "active",
        "version": "1.0.0",
        "protocol": "A2A",
        "agent_card": "/a2a/yahoo_sales_agent/.well-known/agent.json"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "yahoo_sales_agent"}

@app.get("/a2a/yahoo_sales_agent/.well-known/agent.json")
async def get_agent_card():
    """
    Serve the agent card (A2A discovery endpoint).
    This allows other agents to discover Yahoo agent's capabilities.
    """
    logger.info("📋 Agent card requested")
    return JSONResponse(content=AGENT_CARD_DATA)

@app.post("/a2a/yahoo_sales_agent")
async def execute_task(request: Request):
    """
    Main A2A task execution endpoint.
    
    Receives A2A protocol messages and executes the requested skill.
    
    Expected JSON-RPC 2.0 format:
    {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": "echo",
            "input": "Hello World"
        },
        "id": 1
    }
    """
    try:
        # Parse request body
        body = await request.json()
        logger.info(f"📨 Received A2A request: {json.dumps(body, indent=2)}")
        
        # Extract JSON-RPC fields
        jsonrpc = body.get("jsonrpc", "2.0")
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        # Validate JSON-RPC version
        if jsonrpc != "2.0":
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32600,
                        "message": "Invalid JSON-RPC version"
                    },
                    "id": request_id
                }
            )
        
        # Handle different A2A methods
        if method == "task/execute":
            # Extract skill and input
            skill_id = params.get("skill_id")
            task_input = params.get("input", "")
            
            logger.info(f"🎯 Executing skill: {skill_id}")
            
            # Validate skill exists
            if skill_id not in SKILLS:
                return JSONResponse(
                    status_code=404,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": f"Skill not found: {skill_id}"
                        },
                        "id": request_id
                    }
                )
            
            # Execute skill
            skill_function = SKILLS[skill_id]
            result = skill_function(task_input)
            
            # Return success response
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                }
            )
        
        else:
            # Unsupported method
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": request_id
                }
            )
    
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error: Invalid JSON"
                },
                "id": None
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Error executing task: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": request_id if 'request_id' in locals() else None
            }
        )

# =============================================================================
# Server Startup
# =============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    
    print("\n" + "="*70)
    print("🚀 Yahoo A2A Sales Agent Server")
    print("="*70)
    print(f"📍 Server URL: http://localhost:{port}")
    print(f"📋 Agent Card: http://localhost:{port}/a2a/yahoo_sales_agent/.well-known/agent.json")
    print(f"🎯 Task Endpoint: http://localhost:{port}/a2a/yahoo_sales_agent")
    print(f"💡 Protocol: A2A (JSON-RPC 2.0)")
    print(f"🔧 Skills: {', '.join(SKILLS.keys())}")
    print("="*70 + "\n")
    
    uvicorn.run(
        "yahoo_a2a_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

