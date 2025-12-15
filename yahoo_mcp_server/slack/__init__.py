"""
Slack MCP Client Module

This module provides Slack integration for the Yahoo MCP Server,
enabling natural language advertising campaign management via Slack.

Components:
- bot: Slack Bolt app and event handlers
- agent: Claude AI + MCP tool calling (adapted from advertising_agent.py)
- formatters: Slack Block Kit formatting helpers
"""

from .agent import SlackAdvertisingAgent
from .bot import create_slack_app
from .formatters import (
    format_products_blocks,
    format_campaign_blocks,
    format_delivery_blocks,
    format_error_blocks,
    format_help_blocks
)

__all__ = [
    'SlackAdvertisingAgent',
    'create_slack_app',
    'format_products_blocks',
    'format_campaign_blocks',
    'format_delivery_blocks',
    'format_error_blocks',
    'format_help_blocks'
]

