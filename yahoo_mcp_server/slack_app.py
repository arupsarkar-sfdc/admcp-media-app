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


async def run_socket_mode():
    """Run in Socket Mode (for local development)"""
    from slack.bot import create_slack_app, run_socket_mode
    
    # Create Slack app
    slack_app = create_slack_app()
    
    # Initialize the agent
    await slack_app._advertising_agent.initialize()
    
    print("🔌 Starting in Socket Mode (WebSocket connection)")
    print("   This mode is for local development")
    print()
    
    await run_socket_mode(slack_app)


async def main():
    """Main entry point"""
    print_banner()
    check_environment()
    
    mode, port = determine_mode()
    
    if mode == "http":
        await run_http_mode(port)
    else:
        await run_socket_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Yahoo Ads Slack Bot...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

