"""
Slack Advertising Agent

Adapted from advertising_agent.py for Slack context.
Provides per-user conversation history and Slack-optimized responses.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Import MCP client
from fastmcp import Client

# Import Anthropic (Claude)
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

logger = logging.getLogger(__name__)


class ConversationStore:
    """
    Store conversation history per user/channel context.
    Uses in-memory storage (for production, consider Redis).
    """
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._store: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def get(self, context_key: str) -> List[Dict[str, Any]]:
        """Get conversation history for a context"""
        return self._store[context_key]
    
    def add(self, context_key: str, message: Dict[str, Any]):
        """Add a message to conversation history"""
        self._store[context_key].append(message)
        # Trim to max history
        if len(self._store[context_key]) > self.max_history:
            self._store[context_key] = self._store[context_key][-self.max_history:]
    
    def clear(self, context_key: str):
        """Clear conversation history for a context"""
        self._store[context_key] = []


class SlackAdvertisingAgent:
    """
    Slack-adapted advertising agent using Claude + MCP.
    
    Features:
    - Per-user/channel conversation context
    - Slack-optimized response formatting
    - Multi-turn conversations with tool calling
    - Reuses MCP tools from Yahoo MCP Server
    """
    
    SYSTEM_PROMPT = """You are Yahoo Ads Agent in Slack, helping users manage advertising campaigns.

You have access to Yahoo's advertising platform via MCP tools:
- get_products: Discover advertising inventory
- list_creative_formats: Get format specifications  
- create_media_buy: Create campaigns
- get_media_buy: Get campaign details
- get_media_buy_delivery: Get performance metrics
- update_media_buy: Modify campaigns
- get_media_buy_report: Get analytics

Guidelines for Slack responses:
1. Be CONCISE - Slack messages should be scannable
2. Use bullet points and formatting (*bold*, `code`)
3. Format monetary amounts nicely ($50,000 not 50000)
4. Keep responses under 3000 characters when possible
5. Suggest 1-2 next actions at the end

CRITICAL RULES FOR CAMPAIGN CREATION:
1. ALWAYS call list_creative_formats FIRST before creating any campaign
2. ONLY use format IDs that are returned by list_creative_formats
3. NEVER invent or guess format IDs
4. If create_media_buy fails, call list_creative_formats again

When users ask about advertising options, use get_products.
When creating campaigns, confirm budget and dates first.
Be helpful and enthusiastic!"""
    
    def __init__(
        self,
        mcp_url: str,
        anthropic_api_key: Optional[str] = None
    ):
        self.mcp_url = mcp_url
        self.conversations = ConversationStore()
        self.mcp_tools: List[Any] = []
        self.ai_tools: List[Dict] = []
        self._initialized = False
        
        # Initialize Anthropic client
        api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        if not HAS_ANTHROPIC:
            raise ValueError("anthropic package not installed")
        
        self.ai_client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"
        
        logger.info(f"SlackAdvertisingAgent initialized with MCP URL: {mcp_url}")
    
    async def initialize(self):
        """Connect to MCP server and discover available tools"""
        if self._initialized:
            return
        
        logger.info(f"Connecting to MCP Server: {self.mcp_url}")
        
        try:
            async with Client(self.mcp_url) as client:
                tools_result = await client.list_tools()
                
                if hasattr(tools_result, 'tools'):
                    self.mcp_tools = tools_result.tools
                else:
                    self.mcp_tools = tools_result
                
                logger.info(f"Discovered {len(self.mcp_tools)} MCP tools")
                self._prepare_tools_for_claude()
                self._initialized = True
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    def _prepare_tools_for_claude(self):
        """Convert MCP tool definitions to Claude's expected format"""
        self.ai_tools = []
        
        for tool in self.mcp_tools:
            tool_dict = tool if isinstance(tool, dict) else {
                'name': tool.name,
                'description': getattr(tool, 'description', ''),
                'input_schema': getattr(tool, 'inputSchema', {})
            }
            
            self.ai_tools.append({
                "name": tool_dict.get('name'),
                "description": tool_dict.get('description', ''),
                "input_schema": tool_dict.get('input_schema', tool_dict.get('inputSchema', {
                    "type": "object",
                    "properties": {},
                    "required": []
                }))
            })
    
    async def chat(
        self,
        user_id: str,
        channel_id: str,
        message: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message with conversation context.
        
        Args:
            user_id: Slack user ID
            channel_id: Slack channel ID
            message: User's message text
            thread_ts: Thread timestamp (for threaded conversations)
        
        Returns:
            Dict with:
                - text: Natural language response
                - blocks: Slack Block Kit blocks (optional)
                - tool_results: Raw tool results (for rich formatting)
        """
        # Ensure initialized
        if not self._initialized:
            await self.initialize()
        
        # Create context key (use thread if available for threaded conversations)
        context_key = f"{user_id}:{channel_id}:{thread_ts or 'main'}"
        
        # Add user message to history
        self.conversations.add(context_key, {
            "role": "user",
            "content": message
        })
        
        # Get conversation history
        history = self.conversations.get(context_key)
        
        try:
            # Get Claude response with tools
            response = await self._get_claude_response(history)
            
            # Add assistant response to history
            self.conversations.add(context_key, {
                "role": "assistant", 
                "content": response.get("text", "")
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "text": f"❌ Sorry, I encountered an error: {str(e)}",
                "blocks": None,
                "tool_results": None
            }
    
    async def _get_claude_response(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get response from Claude with MCP tool support"""
        
        response = self.ai_client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.SYSTEM_PROMPT,
            tools=self.ai_tools,
            messages=history
        )
        
        # Handle tool calls
        if response.stop_reason == "tool_use":
            return await self._handle_tool_calls(response, history)
        
        # Extract text response
        text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                text = block.text
        
        return {
            "text": text,
            "blocks": None,
            "tool_results": None
        }
    
    async def _handle_tool_calls(
        self,
        response,
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute MCP tool calls and continue conversation"""
        
        tool_results = []
        tool_result_messages = []
        
        # Add assistant's response with tool calls to a temp history
        temp_history = history.copy()
        temp_history.append({
            "role": "assistant",
            "content": response.content
        })
        
        async with Client(self.mcp_url) as mcp:
            for block in response.content:
                if hasattr(block, 'type') and block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id
                    
                    logger.info(f"Calling MCP tool: {tool_name}")
                    
                    try:
                        result = await mcp.call_tool(tool_name, tool_input)
                        
                        # Extract content
                        if hasattr(result, 'content'):
                            if isinstance(result.content, list) and len(result.content) > 0:
                                tool_result = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                            else:
                                tool_result = str(result.content)
                        else:
                            tool_result = str(result)
                        
                        tool_results.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "result": tool_result
                        })
                        
                        tool_result_messages.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": tool_result
                        })
                        
                    except Exception as e:
                        logger.error(f"Tool call failed: {e}")
                        tool_result_messages.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": f"Error: {str(e)}",
                            "is_error": True
                        })
        
        # Add tool results to temp history
        temp_history.append({
            "role": "user",
            "content": tool_result_messages
        })
        
        # Get final response from Claude
        final_response = self.ai_client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=self.SYSTEM_PROMPT,
            tools=self.ai_tools,
            messages=temp_history
        )
        
        # Check if more tool calls needed (recursive)
        if final_response.stop_reason == "tool_use":
            return await self._handle_tool_calls(final_response, temp_history)
        
        # Extract final text
        text = ""
        for block in final_response.content:
            if hasattr(block, 'text'):
                text = block.text
        
        return {
            "text": text,
            "blocks": None,
            "tool_results": tool_results
        }
    
    def clear_conversation(self, user_id: str, channel_id: str, thread_ts: Optional[str] = None):
        """Clear conversation history for a context"""
        context_key = f"{user_id}:{channel_id}:{thread_ts or 'main'}"
        self.conversations.clear(context_key)
        logger.info(f"Cleared conversation for {context_key}")

