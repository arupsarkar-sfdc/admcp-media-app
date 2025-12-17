#!/usr/bin/env python3
"""
Yahoo Ads Slack Bot - Entry Point

This is the main entry point for the Slack MCP client.
It can run in two modes:
1. Socket Mode (local development) - uses WebSocket connection
2. HTTP Mode (production/Heroku) - uses HTTP endpoints

Usage:
    # Local development (Socket Mode)
    python slack_app.py
    
    # Production (HTTP Mode via Heroku)
    Procfile: web: python slack_app.py

Environment Variables Required:
    SLACK_BOT_TOKEN     - Bot token (xoxb-...)
    SLACK_SIGNING_SECRET - Signing secret for request verification
    SLACK_APP_TOKEN     - App token for Socket Mode (xapp-...)
    ANTHROPIC_API_KEY   - Claude API key
    MCP_SERVER_URL      - Yahoo MCP Server URL (optional, has default)
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print("🎯 YAHOO ADS SLACK BOT")
    print("=" * 70)
    print()
    print("Slack MCP Client for Yahoo Advertising Platform")
    print("Powered by Claude AI + MCP Protocol")
    print()


def check_environment():
    """Check required environment variables"""
    required_vars = [
        ("SLACK_BOT_TOKEN", "Slack bot token (xoxb-...)"),
        ("ANTHROPIC_API_KEY", "Anthropic API key for Claude"),
    ]
    
    optional_vars = [
        ("SLACK_SIGNING_SECRET", "Slack signing secret (required for HTTP mode)"),
        ("SLACK_APP_TOKEN", "Slack app token (required for Socket Mode)"),
        ("MCP_SERVER_URL", "Yahoo MCP Server URL (has default)"),
    ]
    
    missing = []
    for var, desc in required_vars:
        if not os.getenv(var):
            missing.append(f"  - {var}: {desc}")
    
    if missing:
        print("❌ Missing required environment variables:")
        for m in missing:
            print(m)
        print()
        print("Set these in your .env file or environment.")
        sys.exit(1)
    
    print("✅ Required environment variables:")
    for var, _ in required_vars:
        value = os.getenv(var, "")
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"   {var}: {masked}")
    
    print()
    print("📋 Optional environment variables:")
    for var, desc in optional_vars:
        value = os.getenv(var, "")
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"   ✓ {var}: {masked}")
        else:
            print(f"   ○ {var}: (not set) - {desc}")
    print()


def determine_mode():
    """Determine whether to run in Socket Mode or HTTP Mode"""
    # Check for Socket Mode token FIRST - this takes priority
    app_token = os.getenv("SLACK_APP_TOKEN")
    
    # Check for Heroku's PORT environment variable
    port = os.getenv("PORT")
    
    # If we have an app token, ALWAYS use Socket Mode
    # Socket Mode is simpler and works everywhere (local + Heroku)
    if app_token:
        return "socket", int(port) if port else None
    elif port:
        # No app token but has PORT - use HTTP mode
        return "http", int(port)
    else:
        # Default to HTTP mode on port 3000
        return "http", 3000


async def run_http_mode(port: int):
    """Run in HTTP mode (for production/Heroku)"""
    from slack.bot import create_slack_app
    from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import JSONResponse
    import uvicorn
    
    # Create Slack app
    slack_app = create_slack_app()
    app_handler = AsyncSlackRequestHandler(slack_app)
    
    # Initialize the agent
    await slack_app._advertising_agent.initialize()
    
    async def handle_slack_events(request):
        """Handle Slack events via HTTP"""
        return await app_handler.handle(request)
    
    async def health_check(request):
        """Health check endpoint for Heroku"""
        return JSONResponse({
            "status": "healthy",
            "service": "yahoo-ads-slack-bot",
            "mcp_url": os.getenv("MCP_SERVER_URL", "default")
        })
    
    # Create Starlette app
    app = Starlette(
        routes=[
            Route("/slack/events", handle_slack_events, methods=["POST"]),
            Route("/health", health_check, methods=["GET"]),
            Route("/", health_check, methods=["GET"]),
        ]
    )
    
    print(f"🚀 Starting HTTP server on port {port}")
    print(f"   Slack events: POST /slack/events")
    print(f"   Health check: GET /health")
    print()
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_socket_mode(port: int = None):
    """Run in Socket Mode with optional health check server for Heroku"""
    from slack.bot import create_slack_app, run_socket_mode as start_socket_mode
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import JSONResponse
    from starlette.requests import Request
    import uvicorn
    import json
    
    # Create Slack app
    slack_app = create_slack_app()
    
    # Initialize the agent
    await slack_app._advertising_agent.initialize()
    
    print("🔌 Starting in Socket Mode (WebSocket connection)")
    
    # ================================================================
    # WEBHOOK ENDPOINT FOR STREAMLIT/AGENCY CAMPAIGN CREATION
    # ================================================================
    async def handle_campaign_webhook(request: Request):
        """
        Webhook endpoint for campaign creation notifications.
        
        Called by Streamlit/advertising_agent.py after successful create_media_buy.
        Triggers CEM workflow and posts approval card to configured channel.
        
        Expected payload:
        {
            "media_buy_id": "nike_spring_2026_xxxxx",
            "campaign_name": "Nike Spring Running Q1 2026",
            "total_budget": 50000,
            "principal_id": "nike_global",
            "flight_start_date": "2026-01-15",
            "flight_end_date": "2026-03-15",
            "created_by": "agency_user@example.com"
        }
        """
        try:
            # Parse request body
            body = await request.body()
            data = json.loads(body)
            
            media_buy_id = data.get("media_buy_id")
            if not media_buy_id:
                return JSONResponse(
                    {"error": "media_buy_id is required"},
                    status_code=400
                )
            
            logger.info(f"📨 Webhook received for campaign: {media_buy_id}")
            
            # Get CEM channel from environment
            cem_channel = os.getenv("CEM_CHANNEL_ID")
            if not cem_channel:
                logger.warning("CEM_CHANNEL_ID not set, using default")
                # Fallback: post to the app's DM or a default channel
                cem_channel = os.getenv("SLACK_DEFAULT_CHANNEL", "")
            
            # Import automation modules
            from automation import OrderValidator, AuditLogger, CEMAgent
            
            # Step 1: Validate order against master tables
            logger.info(f"🔍 Validating order: {media_buy_id}")
            validator = OrderValidator()
            validation_result = validator.validate_order(media_buy_id)
            order_details = validator.get_order_details(media_buy_id)
            
            if not order_details:
                return JSONResponse(
                    {"error": f"Order {media_buy_id} not found in database"},
                    status_code=404
                )
            
            logger.info(f"Validation result: {validation_result.summary}")
            
            # Step 2: Log validation to audit
            audit = AuditLogger()
            audit.log_validation(
                media_buy_id=media_buy_id,
                validation_result={
                    'all_passed': validation_result.all_passed,
                    'summary': validation_result.summary,
                    'checks': [
                        {'check_name': c.check_name, 'passed': c.passed, 'message': c.message}
                        for c in validation_result.checks
                    ]
                },
                principal_id=order_details.get('principal_id'),
                tenant_id='yahoo'
            )
            
            # Step 3: Generate AI summary for CEM
            logger.info("🤖 Generating CEM summary...")
            cem_agent = CEMAgent()
            cem_summary = cem_agent.generate_summary(
                order_details=order_details,
                validation_result={
                    'all_passed': validation_result.all_passed,
                    'summary': validation_result.summary,
                    'checks': [
                        {'check_name': c.check_name, 'passed': c.passed, 'message': c.message, 'details': c.details}
                        for c in validation_result.checks
                    ]
                }
            )
            
            # Step 4: Log approval request
            audit.log_approval_requested(
                media_buy_id=media_buy_id,
                order_details=order_details,
                validation_summary=cem_summary.order_summary,
                cem_channel=cem_channel or 'webhook'
            )
            
            # Step 5: Post approval card to Slack channel
            if cem_channel:
                from slack_sdk.web.async_client import AsyncWebClient
                
                client = AsyncWebClient(token=os.getenv("SLACK_BOT_TOKEN"))
                
                # Post the approval card
                await client.chat_postMessage(
                    channel=cem_channel,
                    blocks=cem_summary.to_slack_blocks(),
                    text=f"New order pending approval: {media_buy_id}"
                )
                
                logger.info(f"✅ Posted approval card to channel {cem_channel}")
            
            return JSONResponse({
                "success": True,
                "media_buy_id": media_buy_id,
                "validation_passed": validation_result.all_passed,
                "recommendation": cem_summary.recommendation.action,
                "message": f"CEM workflow initiated. Recommendation: {cem_summary.recommendation.action.upper()}"
            })
            
        except json.JSONDecodeError:
            return JSONResponse(
                {"error": "Invalid JSON payload"},
                status_code=400
            )
        except ImportError as e:
            logger.error(f"Automation module not found: {e}")
            return JSONResponse(
                {"error": "CEM workflow not available"},
                status_code=500
            )
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JSONResponse(
                {"error": str(e)},
                status_code=500
            )
    
    async def health_check(request):
        return JSONResponse({
            "status": "healthy",
            "mode": "socket",
            "service": "yahoo-ads-slack-bot",
            "webhook": "/webhook/campaign-created"
        })
    
    # ================================================================
    # END WEBHOOK
    # ================================================================
    
    if port:
        # Heroku requires binding to $PORT - run health server alongside Socket Mode
        print(f"   Running health check server on port {port} for Heroku")
        print(f"   Webhook endpoint: POST /webhook/campaign-created")
        
        webhook_app = Starlette(routes=[
            Route("/", health_check, methods=["GET"]),
            Route("/health", health_check, methods=["GET"]),
            Route("/webhook/campaign-created", handle_campaign_webhook, methods=["POST"]),
        ])
        
        # Run both health server and Socket Mode concurrently
        config = uvicorn.Config(webhook_app, host="0.0.0.0", port=port, log_level="warning")
        server = uvicorn.Server(config)
        
        # Start both tasks
        await asyncio.gather(
            server.serve(),
            start_socket_mode(slack_app)
        )
    else:
        print("   Local development mode")
        print()
        await start_socket_mode(slack_app)


async def main():
    """Main entry point"""
    print_banner()
    check_environment()
    
    mode, port = determine_mode()
    
    if mode == "http":
        await run_http_mode(port)
    else:
        # Pass port to Socket Mode so it can run health server for Heroku
        await run_socket_mode(port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Yahoo Ads Slack Bot...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

