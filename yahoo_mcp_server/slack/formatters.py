"""
Slack Block Kit Formatters

Provides rich formatting for advertising data in Slack messages.
Uses Slack Block Kit for interactive, visually appealing messages.
"""

import json
from typing import List, Dict, Any, Optional


def format_products_blocks(products: List[Dict], title: Optional[str] = None) -> List[Dict]:
    """
    Format products as Slack Block Kit components.
    
    Args:
        products: List of product dictionaries from get_products
        title: Optional custom title
    
    Returns:
        List of Slack blocks
    """
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title or f"🎯 Found {len(products)} Yahoo Advertising Products",
                "emoji": True
            }
        },
        {"type": "divider"}
    ]
    
    # Show top 5 products
    for product in products[:5]:
        pricing = product.get("pricing", {})
        if isinstance(pricing, str):
            try:
                pricing = json.loads(pricing)
            except:
                pricing = {}
        
        price_value = pricing.get("value", 0)
        price_model = pricing.get("model", "CPM").upper()
        reach = product.get("estimated_reach", 0)
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{product.get('name', 'Unknown')}*\n"
                    f"Type: `{product.get('product_type', 'N/A')}` • "
                    f"{price_model}: *${price_value:,.2f}* • "
                    f"Reach: {reach:,}"
                )
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Select", "emoji": True},
                "value": product.get("product_id", "unknown"),
                "action_id": f"select_product_{product.get('product_id', 'unknown')}"
            }
        })
    
    if len(products) > 5:
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"_Showing 5 of {len(products)} products_"
            }]
        })
    
    # Add suggestions
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": "💡 *Next:* Tell me which product to use, or say 'create campaign with [product name]'"
        }]
    })
    
    return blocks


def format_campaign_blocks(campaign: Dict) -> List[Dict]:
    """
    Format campaign details as Slack blocks.
    
    Args:
        campaign: Campaign dictionary from get_media_buy or create_media_buy
    
    Returns:
        List of Slack blocks
    """
    status = campaign.get("status", "unknown")
    status_emoji = {
        "active": "🟢",
        "pending": "🟡", 
        "approved": "🟢",
        "paused": "⏸️",
        "completed": "✅",
        "error": "🔴"
    }.get(status, "⚪")
    
    campaign_name = campaign.get("campaign_name", campaign.get("media_buy_id", "Unknown"))
    total_budget = campaign.get("total_budget", 0)
    currency = campaign.get("currency", "USD")
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{status_emoji} Campaign: {campaign_name}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Status:*\n{status.title()}"},
                {"type": "mrkdwn", "text": f"*Budget:*\n${total_budget:,.2f} {currency}"},
                {"type": "mrkdwn", "text": f"*Start:*\n{campaign.get('flight_start_date', 'N/A')}"},
                {"type": "mrkdwn", "text": f"*End:*\n{campaign.get('flight_end_date', 'N/A')}"}
            ]
        }
    ]
    
    # Add packages if present
    packages = campaign.get("packages", [])
    if packages:
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📦 {len(packages)} Package(s):*"
            }
        })
        
        for pkg in packages[:3]:  # Show max 3 packages
            pkg_name = pkg.get("product_name", pkg.get("product_id", "Unknown"))
            pkg_budget = pkg.get("budget", 0)
            blocks.append({
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"• *{pkg_name}* — ${pkg_budget:,.2f}"
                }]
            })
    
    # Add campaign ID
    media_buy_id = campaign.get("media_buy_id")
    if media_buy_id:
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"📋 Campaign ID: `{media_buy_id}`"
            }]
        })
    
    return blocks


def format_delivery_blocks(delivery: Dict) -> List[Dict]:
    """
    Format delivery metrics as Slack blocks.
    
    Args:
        delivery: Delivery dictionary from get_media_buy_delivery
    
    Returns:
        List of Slack blocks
    """
    campaign_name = delivery.get("campaign_name", delivery.get("media_buy_id", "Unknown"))
    metrics = delivery.get("delivery", {})
    pacing = delivery.get("pacing", {})
    
    impressions = metrics.get("impressions_delivered", 0)
    clicks = metrics.get("clicks", 0)
    conversions = metrics.get("conversions", 0)
    spend = metrics.get("spend", 0)
    ctr = metrics.get("ctr", 0)
    cvr = metrics.get("cvr", 0)
    
    budget_total = pacing.get("budget_total", 0)
    budget_pacing = pacing.get("budget_pacing_pct", 0)
    
    # Determine pacing health
    pacing_emoji = "🟢" if 40 <= budget_pacing <= 60 else "🟡" if budget_pacing < 40 else "🔴"
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 Delivery: {campaign_name}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Impressions:*\n{impressions:,}"},
                {"type": "mrkdwn", "text": f"*Clicks:*\n{clicks:,}"},
                {"type": "mrkdwn", "text": f"*CTR:*\n{ctr:.2f}%"},
                {"type": "mrkdwn", "text": f"*Conversions:*\n{conversions:,}"}
            ]
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Spend:*\n${spend:,.2f}"},
                {"type": "mrkdwn", "text": f"*Budget:*\n${budget_total:,.2f}"},
                {"type": "mrkdwn", "text": f"*CVR:*\n{cvr:.2f}%"},
                {"type": "mrkdwn", "text": f"*Pacing:*\n{pacing_emoji} {budget_pacing:.1f}%"}
            ]
        }
    ]
    
    # Add pacing bar visualization
    pacing_bar = create_progress_bar(budget_pacing)
    blocks.append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": f"Budget Progress: {pacing_bar}"
        }]
    })
    
    return blocks


def format_error_blocks(error_message: str, hint: Optional[str] = None) -> List[Dict]:
    """
    Format error message as Slack blocks.
    
    Args:
        error_message: The error message
        hint: Optional hint for resolution
    
    Returns:
        List of Slack blocks
    """
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"❌ *Error:* {error_message}"
            }
        }
    ]
    
    if hint:
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"💡 *Hint:* {hint}"
            }]
        })
    
    return blocks


def format_help_blocks() -> List[Dict]:
    """
    Format help message as Slack blocks.
    
    Returns:
        List of Slack blocks with usage instructions
    """
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎯 Yahoo Ads Agent - Help",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "I can help you manage advertising campaigns on Yahoo. Here's what I can do:"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*📦 Discover Inventory*\n"
                    "• _\"Show me advertising options for Nike running shoes\"_\n"
                    "• _\"What products are available for a $50K budget?\"_"
                )
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*🚀 Create Campaigns*\n"
                    "• _\"Create a campaign with Yahoo Sports Video, $25K budget\"_\n"
                    "• _\"Set up a display campaign for Q1 2025\"_"
                )
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*📊 Track Performance*\n"
                    "• _\"How is campaign XYZ performing?\"_\n"
                    "• _\"Show me delivery metrics\"_"
                )
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*⚙️ Manage Campaigns*\n"
                    "• _\"Pause campaign XYZ\"_\n"
                    "• _\"Update budget to $30K\"_"
                )
            }
        },
        {"type": "divider"},
        {
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": "💬 Just @mention me with your request, or DM me directly!"
            }]
        }
    ]


def create_progress_bar(percentage: float, width: int = 10) -> str:
    """
    Create a text-based progress bar.
    
    Args:
        percentage: Progress percentage (0-100)
        width: Width of the bar in characters
    
    Returns:
        String representation of progress bar
    """
    filled = int(min(100, max(0, percentage)) / 100 * width)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] {percentage:.1f}%"


def format_text_response(text: str) -> List[Dict]:
    """
    Format a simple text response as Slack blocks.
    
    Args:
        text: The text message
    
    Returns:
        List of Slack blocks
    """
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    ]

