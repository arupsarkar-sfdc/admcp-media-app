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
from datetime import datetime, timezone
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
            
            # Check if there's a pending CEM summary to post
            cem_summary = agent.get_pending_cem_summary()
            if cem_summary:
                # Post CEM approval request to the channel
                await say(
                    blocks=cem_summary.to_slack_blocks(),
                    text=f"Order {cem_summary.media_buy_id} pending CEM approval",
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
            
            # Check if there's a pending CEM summary to post
            cem_summary = agent.get_pending_cem_summary()
            if cem_summary:
                await say(
                    blocks=cem_summary.to_slack_blocks(),
                    text=f"Order {cem_summary.media_buy_id} pending CEM approval"
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
    
    # ================================================================
    # CEM APPROVAL WORKFLOW HANDLERS
    # Human-in-the-loop approval/rejection for Yahoo internal workflow
    # ================================================================
    
    @app.action(re.compile(r"cem_approve_.*"))
    async def handle_cem_approve(ack, action, say, body, client):
        """
        Handle CEM approval button click.
        
        This is Yahoo's INTERNAL workflow - not part of AdCP protocol.
        After approval:
        1. Update order status in Snowflake
        2. Log to audit_log
        3. (Future) Create Salesforce Opportunity
        """
        await ack()
        
        media_buy_id = action["value"]
        user_id = body["user"]["id"]
        user_name = body["user"].get("username", user_id)
        channel_id = body["channel"]["id"]
        message_ts = body.get("message", {}).get("ts")
        
        logger.info(f"CEM APPROVAL: {media_buy_id} by {user_name}")
        
        try:
            # Import automation modules
            from automation import AuditLogger
            
            # Log approval to audit
            audit = AuditLogger()
            audit.log_approved(
                media_buy_id=media_buy_id,
                approved_by=user_name,
                comments="Approved via Slack"
            )
            
            # Update order status in Snowflake
            try:
                from services.snowflake_write_service import SnowflakeWriteService
                sf_write = SnowflakeWriteService()
                # Update status to 'active'
                conn = sf_write._get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE media_buys 
                        SET status = 'active', updated_at = CURRENT_TIMESTAMP
                        WHERE media_buy_id = %s
                    """, (media_buy_id,))
                    conn.commit()
                    cursor.close()
                    logger.info(f"Updated media_buy status to 'active': {media_buy_id}")
            except Exception as e:
                logger.error(f"Failed to update status: {e}")
            
            # --------------------------------------------------------
            # FUTURE: Trigger Opportunity creation here after approval
            # agent = app._advertising_agent
            # opp_result = agent._create_opportunity_for_campaign(...)
            # --------------------------------------------------------
            
            # Update the original message to show approval
            approval_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ ORDER APPROVED",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Order ID:* `{media_buy_id}`\n*Approved by:* <@{user_id}>\n*Status:* Active"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Approved at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
                        }
                    ]
                }
            ]
            
            if message_ts:
                await client.chat_update(
                    channel=channel_id,
                    ts=message_ts,
                    blocks=approval_blocks,
                    text=f"Order {media_buy_id} approved"
                )
            else:
                await say(blocks=approval_blocks, text=f"Order {media_buy_id} approved")
                
        except ImportError as e:
            logger.error(f"Automation module not found: {e}")
            await say(text=f"⚠️ Could not process approval: automation module not available")
        except Exception as e:
            logger.error(f"Error processing approval: {e}")
            await say(text=f"⚠️ Error processing approval: {str(e)}")
    
    @app.action(re.compile(r"cem_reject_.*"))
    async def handle_cem_reject(ack, action, say, body, client):
        """
        Handle CEM rejection button click.
        
        Opens a modal to collect rejection reason.
        """
        await ack()
        
        media_buy_id = action["value"]
        user_id = body["user"]["id"]
        trigger_id = body["trigger_id"]
        
        logger.info(f"CEM REJECTION initiated: {media_buy_id} by {user_id}")
        
        # Open modal to collect rejection reason
        try:
            await client.views_open(
                trigger_id=trigger_id,
                view={
                    "type": "modal",
                    "callback_id": f"cem_reject_submit_{media_buy_id}",
                    "title": {"type": "plain_text", "text": "Reject Order"},
                    "submit": {"type": "plain_text", "text": "Reject"},
                    "close": {"type": "plain_text", "text": "Cancel"},
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Order ID:* `{media_buy_id}`\n\nPlease provide a reason for rejection:"
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "rejection_reason",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "reason_input",
                                "multiline": True,
                                "placeholder": {"type": "plain_text", "text": "Enter rejection reason..."}
                            },
                            "label": {"type": "plain_text", "text": "Rejection Reason"}
                        }
                    ],
                    "private_metadata": f"{body['channel']['id']}|{body.get('message', {}).get('ts', '')}"
                }
            )
        except Exception as e:
            logger.error(f"Failed to open reject modal: {e}")
            await say(text=f"⚠️ Could not open rejection form: {str(e)}")
    
    @app.view(re.compile(r"cem_reject_submit_.*"))
    async def handle_cem_reject_submit(ack, view, body, client):
        """Handle rejection modal submission"""
        await ack()
        
        # Extract media_buy_id from callback_id
        callback_id = view["callback_id"]
        media_buy_id = callback_id.replace("cem_reject_submit_", "")
        
        user_id = body["user"]["id"]
        user_name = body["user"].get("username", user_id)
        
        # Get rejection reason
        reason = view["state"]["values"]["rejection_reason"]["reason_input"]["value"]
        
        # Get original channel/message from private_metadata
        private_metadata = view.get("private_metadata", "").split("|")
        channel_id = private_metadata[0] if len(private_metadata) > 0 else None
        message_ts = private_metadata[1] if len(private_metadata) > 1 else None
        
        logger.info(f"CEM REJECTION: {media_buy_id} by {user_name} - {reason}")
        
        try:
            from automation import AuditLogger
            
            # Log rejection
            audit = AuditLogger()
            audit.log_rejected(
                media_buy_id=media_buy_id,
                rejected_by=user_name,
                reason=reason
            )
            
            # Update order status in Snowflake
            try:
                from services.snowflake_write_service import SnowflakeWriteService
                sf_write = SnowflakeWriteService()
                conn = sf_write._get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE media_buys 
                        SET status = 'rejected', updated_at = CURRENT_TIMESTAMP
                        WHERE media_buy_id = %s
                    """, (media_buy_id,))
                    conn.commit()
                    cursor.close()
            except Exception as e:
                logger.error(f"Failed to update status: {e}")
            
            # Post rejection message
            rejection_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ ORDER REJECTED",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Order ID:* `{media_buy_id}`\n*Rejected by:* <@{user_id}>\n*Reason:* {reason}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Rejected at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
                        }
                    ]
                }
            ]
            
            if channel_id and message_ts:
                await client.chat_update(
                    channel=channel_id,
                    ts=message_ts,
                    blocks=rejection_blocks,
                    text=f"Order {media_buy_id} rejected"
                )
            elif channel_id:
                await client.chat_postMessage(
                    channel=channel_id,
                    blocks=rejection_blocks,
                    text=f"Order {media_buy_id} rejected"
                )
                
        except Exception as e:
            logger.error(f"Error processing rejection: {e}")
    
    @app.action(re.compile(r"cem_review_.*"))
    async def handle_cem_review(ack, action, say, body, client):
        """
        Handle CEM review/changes request button click.
        
        Opens a modal to collect review comments.
        """
        await ack()
        
        media_buy_id = action["value"]
        user_id = body["user"]["id"]
        trigger_id = body["trigger_id"]
        
        logger.info(f"CEM REVIEW requested: {media_buy_id} by {user_id}")
        
        try:
            await client.views_open(
                trigger_id=trigger_id,
                view={
                    "type": "modal",
                    "callback_id": f"cem_review_submit_{media_buy_id}",
                    "title": {"type": "plain_text", "text": "Request Changes"},
                    "submit": {"type": "plain_text", "text": "Submit"},
                    "close": {"type": "plain_text", "text": "Cancel"},
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Order ID:* `{media_buy_id}`\n\nDescribe the changes needed:"
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "review_comments",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "comments_input",
                                "multiline": True,
                                "placeholder": {"type": "plain_text", "text": "What changes are needed?"}
                            },
                            "label": {"type": "plain_text", "text": "Changes Required"}
                        }
                    ],
                    "private_metadata": f"{body['channel']['id']}|{body.get('message', {}).get('ts', '')}"
                }
            )
        except Exception as e:
            logger.error(f"Failed to open review modal: {e}")
            await say(text=f"⚠️ Could not open review form: {str(e)}")
    
    @app.view(re.compile(r"cem_review_submit_.*"))
    async def handle_cem_review_submit(ack, view, body, client):
        """Handle review modal submission"""
        await ack()
        
        callback_id = view["callback_id"]
        media_buy_id = callback_id.replace("cem_review_submit_", "")
        
        user_id = body["user"]["id"]
        user_name = body["user"].get("username", user_id)
        
        comments = view["state"]["values"]["review_comments"]["comments_input"]["value"]
        
        private_metadata = view.get("private_metadata", "").split("|")
        channel_id = private_metadata[0] if len(private_metadata) > 0 else None
        message_ts = private_metadata[1] if len(private_metadata) > 1 else None
        
        logger.info(f"CEM REVIEW: {media_buy_id} by {user_name} - {comments}")
        
        try:
            from automation import AuditLogger
            
            audit = AuditLogger()
            audit.log_review_requested(
                media_buy_id=media_buy_id,
                requested_by=user_name,
                comments=comments
            )
            
            # Update order status to pending_changes
            try:
                from services.snowflake_write_service import SnowflakeWriteService
                sf_write = SnowflakeWriteService()
                conn = sf_write._get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE media_buys 
                        SET status = 'pending_changes', updated_at = CURRENT_TIMESTAMP
                        WHERE media_buy_id = %s
                    """, (media_buy_id,))
                    conn.commit()
                    cursor.close()
            except Exception as e:
                logger.error(f"Failed to update status: {e}")
            
            review_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 CHANGES REQUESTED",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Order ID:* `{media_buy_id}`\n*Requested by:* <@{user_id}>\n*Status:* Pending Changes"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Changes Needed:*\n{comments}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Review requested at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
                        }
                    ]
                }
            ]
            
            if channel_id and message_ts:
                await client.chat_update(
                    channel=channel_id,
                    ts=message_ts,
                    blocks=review_blocks,
                    text=f"Order {media_buy_id} - changes requested"
                )
            elif channel_id:
                await client.chat_postMessage(
                    channel=channel_id,
                    blocks=review_blocks,
                    text=f"Order {media_buy_id} - changes requested"
                )
                
        except Exception as e:
            logger.error(f"Error processing review request: {e}")
    
    # ================================================================
    # END CEM WORKFLOW HANDLERS
    # ================================================================
    
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


