"""
Slack Bot - Event Handlers

Slack Bolt application with event handlers for:
- @mentions in channels
- Direct messages
- Slash commands
- Interactive components (buttons, modals)
"""

import os
import re
import logging
import asyncio
from typing import Optional

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from .agent import SlackAdvertisingAgent
from .formatters import (
    format_text_response,
    format_help_blocks,
    format_error_blocks
)

logger = logging.getLogger(__name__)


def create_slack_app(
    bot_token: Optional[str] = None,
    signing_secret: Optional[str] = None,
    mcp_url: Optional[str] = None
) -> AsyncApp:
    """
    Create and configure the Slack Bolt application.
    
    Args:
        bot_token: Slack bot token (xoxb-...)
        signing_secret: Slack signing secret
        mcp_url: Yahoo MCP Server URL
    
    Returns:
        Configured AsyncApp instance
    """
    # Get configuration from environment if not provided
    bot_token = bot_token or os.environ.get("SLACK_BOT_TOKEN")
    signing_secret = signing_secret or os.environ.get("SLACK_SIGNING_SECRET")
    mcp_url = mcp_url or os.environ.get(
        "MCP_SERVER_URL",
        "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp"
    )
    
    if not bot_token:
        raise ValueError("SLACK_BOT_TOKEN is required")
    
    # Create Slack app
    app = AsyncApp(
        token=bot_token,
        signing_secret=signing_secret
    )
    
    # Initialize the advertising agent
    agent = SlackAdvertisingAgent(mcp_url=mcp_url)
    
    # Store agent in app for access in handlers
    app._advertising_agent = agent
    
    # Register event handlers
    register_handlers(app)
    
    logger.info("Slack app created and configured")
    return app


def register_handlers(app: AsyncApp):
    """Register all event handlers on the app"""
    
    @app.event("app_mention")
    async def handle_app_mention(event, say, client):
        """
        Handle @YahooAdsBot mentions in channels.
        
        Example: "@YahooAdsBot show me Nike advertising options"
        """
        user_id = event["user"]
        channel_id = event["channel"]
        thread_ts = event.get("thread_ts", event["ts"])
        message = event["text"]
        
        # Remove bot mention from message
        # Pattern: <@U12345678> message
        message = re.sub(r'<@[A-Z0-9]+>\s*', '', message).strip()
        
        if not message:
            # Empty message after removing mention
            await say(
                blocks=format_help_blocks(),
                thread_ts=thread_ts
            )
            return
        
        # Check for special commands
        if message.lower() in ['help', '?']:
            await say(
                blocks=format_help_blocks(),
                thread_ts=thread_ts
            )
            return
        
        if message.lower() in ['clear', 'reset', 'start over']:
            agent = app._advertising_agent
            agent.clear_conversation(user_id, channel_id, thread_ts)
            await say(
                text="🔄 Conversation cleared! How can I help you?",
                thread_ts=thread_ts
            )
            return
        
        # Show typing indicator
        try:
            await client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="hourglass_flowing_sand"
            )
        except Exception:
            pass  # Ignore reaction errors
        
        try:
            # Get agent response
            agent = app._advertising_agent
            response = await agent.chat(
                user_id=user_id,
                channel_id=channel_id,
                message=message,
                thread_ts=thread_ts
            )
            
            # Send response
            if response.get("blocks"):
                await say(
                    blocks=response["blocks"],
                    text=response.get("text", ""),  # Fallback text
                    thread_ts=thread_ts
                )
            else:
                await say(
                    blocks=format_text_response(response.get("text", "I'm not sure how to respond.")),
                    text=response.get("text", ""),
                    thread_ts=thread_ts
                )
                
        except Exception as e:
            logger.error(f"Error handling mention: {e}")
            await say(
                blocks=format_error_blocks(
                    str(e),
                    "Try rephrasing your request or type 'help' for usage."
                ),
                thread_ts=thread_ts
            )
        
        finally:
            # Remove typing indicator
            try:
                await client.reactions_remove(
                    channel=channel_id,
                    timestamp=event["ts"],
                    name="hourglass_flowing_sand"
                )
            except Exception:
                pass
    
    @app.event("message")
    async def handle_direct_message(event, say, client):
        """
        Handle direct messages to the bot.
        
        DMs don't need @mentions - just send a message.
        """
        # Only handle DMs (im = instant message)
        if event.get("channel_type") != "im":
            return
        
        # Ignore bot's own messages
        if event.get("bot_id"):
            return
        
        # Ignore message updates/edits
        if event.get("subtype"):
            return
        
        user_id = event["user"]
        channel_id = event["channel"]
        message = event["text"]
        
        # Check for special commands
        if message.lower() in ['help', '?']:
            await say(blocks=format_help_blocks())
            return
        
        if message.lower() in ['clear', 'reset', 'start over']:
            agent = app._advertising_agent
            agent.clear_conversation(user_id, channel_id)
            await say(text="🔄 Conversation cleared! How can I help you?")
            return
        
        # Show typing indicator
        try:
            await client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="hourglass_flowing_sand"
            )
        except Exception:
            pass
        
        try:
            # Get agent response
            agent = app._advertising_agent
            response = await agent.chat(
                user_id=user_id,
                channel_id=channel_id,
                message=message
            )
            
            # Send response
            if response.get("blocks"):
                await say(
                    blocks=response["blocks"],
                    text=response.get("text", "")
                )
            else:
                await say(
                    blocks=format_text_response(response.get("text", "I'm not sure how to respond.")),
                    text=response.get("text", "")
                )
                
        except Exception as e:
            logger.error(f"Error handling DM: {e}")
            await say(
                blocks=format_error_blocks(
                    str(e),
                    "Try rephrasing your request or type 'help' for usage."
                )
            )
        
        finally:
            try:
                await client.reactions_remove(
                    channel=channel_id,
                    timestamp=event["ts"],
                    name="hourglass_flowing_sand"
                )
            except Exception:
                pass
    
    @app.command("/campaign")
    async def handle_campaign_command(ack, command, say, client):
        """
        Handle /campaign slash command.
        
        Usage:
            /campaign help
            /campaign status <campaign_id>
            /campaign list
        """
        await ack()
        
        user_id = command["user_id"]
        channel_id = command["channel_id"]
        args = command["text"].strip().split()
        action = args[0].lower() if args else "help"
        
        if action == "help":
            await say(blocks=format_help_blocks())
            return
        
        # For other actions, use the agent
        agent = app._advertising_agent
        
        if action == "status" and len(args) > 1:
            campaign_id = args[1]
            response = await agent.chat(
                user_id=user_id,
                channel_id=channel_id,
                message=f"Get delivery status for campaign {campaign_id}"
            )
        elif action == "list":
            response = await agent.chat(
                user_id=user_id,
                channel_id=channel_id,
                message="Show me available advertising products"
            )
        else:
            # Pass the full command to agent
            response = await agent.chat(
                user_id=user_id,
                channel_id=channel_id,
                message=f"Campaign command: {command['text']}"
            )
        
        if response.get("blocks"):
            await say(blocks=response["blocks"], text=response.get("text", ""))
        else:
            await say(text=response.get("text", "Command processed."))
    
    @app.action(re.compile(r"select_product_.*"))
    async def handle_product_selection(ack, action, say, body):
        """Handle product selection button clicks"""
        await ack()
        
        product_id = action["value"]
        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]
        
        agent = app._advertising_agent
        response = await agent.chat(
            user_id=user_id,
            channel_id=channel_id,
            message=f"I want to create a campaign with product {product_id}"
        )
        
        if response.get("blocks"):
            await say(blocks=response["blocks"], text=response.get("text", ""))
        else:
            await say(text=response.get("text", "Product selected."))
    
    # Log unhandled events for debugging
    @app.event("message")
    async def handle_message_default(event, logger):
        """Catch-all for unhandled message events"""
        logger.debug(f"Unhandled message event: {event.get('subtype', 'no subtype')}")


async def run_socket_mode(app: AsyncApp):
    """
    Run the app in Socket Mode (for development/local testing).
    
    Requires SLACK_APP_TOKEN environment variable.
    """
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        raise ValueError("SLACK_APP_TOKEN is required for Socket Mode")
    
    handler = AsyncSocketModeHandler(app, app_token)
    logger.info("Starting Slack app in Socket Mode...")
    await handler.start_async()

