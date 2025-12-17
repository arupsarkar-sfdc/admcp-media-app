#!/usr/bin/env python3
"""
Yahoo Advertising Agent - Agentic Experience Demo

An AI agent that helps users create and manage advertising campaigns using
the Yahoo MCP Server via natural language conversation.

Usage:
    uv run python advertising_agent.py
"""

import os
import sys
import asyncio
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import MCP client
from fastmcp import Client

# Import httpx for webhook calls
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# Import Anthropic (Claude)
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("⚠️  Anthropic not installed. Install with: uv pip install anthropic")

# Import OpenAI (fallback)
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

load_dotenv()


class AdvertisingAgent:
    """
    An AI agent that uses the Yahoo MCP Server to help with advertising campaigns.
    
    Features:
    - Natural language conversation
    - Automatic tool calling via MCP
    - Context-aware responses
    - Multi-turn conversations
    """
    
    def __init__(
        self,
        mcp_url: str,
        use_anthropic: bool = True
    ):
        self.mcp_url = mcp_url
        self.use_anthropic = use_anthropic and HAS_ANTHROPIC
        self.conversation_history: List[Dict[str, Any]] = []
        self.mcp_tools = []
        
        # Initialize AI client
        if self.use_anthropic:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            self.ai_client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-sonnet-4-5-20250929"  # Latest stable Claude 3.5 Sonnet
            print("🤖 Using Claude (Anthropic)")
        elif HAS_OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            self.ai_client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4-turbo-preview"
            print("🤖 Using GPT-4 (OpenAI)")
        else:
            raise ValueError("No AI client available. Install anthropic or openai.")
        
        # CEM Webhook URL (for notifying internal team of new campaigns)
        self.cem_webhook_url = os.getenv("CEM_WEBHOOK_URL")
        if self.cem_webhook_url:
            print(f"📨 CEM Webhook: {self.cem_webhook_url[:50]}...")
    
    async def _notify_cem_webhook(self, campaign_data: Dict[str, Any]) -> bool:
        """
        Notify CEM team via webhook when a campaign is created.
        
        This triggers the internal Yahoo CEM approval workflow in Slack.
        
        Args:
            campaign_data: Campaign details including media_buy_id
            
        Returns:
            True if webhook succeeded, False otherwise
        """
        if not self.cem_webhook_url:
            print("   ℹ️  CEM_WEBHOOK_URL not set, skipping CEM notification")
            return False
        
        if not HAS_HTTPX:
            print("   ⚠️  httpx not installed, skipping CEM notification")
            return False
        
        try:
            print(f"\n📨 Notifying CEM team...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.cem_webhook_url,
                    json=campaign_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ CEM notified: {result.get('recommendation', 'pending').upper()}")
                    return True
                else:
                    print(f"   ⚠️  CEM webhook returned {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"   ⚠️  CEM webhook failed: {e}")
            return False
    
    async def initialize(self):
        """Connect to MCP server and discover available tools"""
        print(f"\n🔌 Connecting to MCP Server...")
        print(f"   URL: {self.mcp_url}")
        
        try:
            async with Client(self.mcp_url) as client:
                # Get server info
                # Get available tools
                tools_result = await client.list_tools()
                
                if hasattr(tools_result, 'tools'):
                    self.mcp_tools = tools_result.tools
                else:
                    self.mcp_tools = tools_result
                
                print(f"✅ Connected! Found {len(self.mcp_tools)} tools:")
                for tool in self.mcp_tools:
                    tool_name = tool.name if hasattr(tool, 'name') else tool.get('name', 'unknown')
                    print(f"   - {tool_name}")
                
                # Convert MCP tools to format expected by AI
                self._prepare_tools_for_ai()
                
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            raise
    
    def _prepare_tools_for_ai(self):
        """Convert MCP tool definitions to AI-compatible format"""
        if self.use_anthropic:
            # Claude expects tools in specific format
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
        else:
            # OpenAI format (similar but different structure)
            self.ai_tools = []
            for tool in self.mcp_tools:
                tool_dict = tool if isinstance(tool, dict) else {
                    'name': tool.name,
                    'description': getattr(tool, 'description', ''),
                    'parameters': getattr(tool, 'inputSchema', {})
                }
                
                self.ai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool_dict.get('name'),
                        "description": tool_dict.get('description', ''),
                        "parameters": tool_dict.get('input_schema', tool_dict.get('inputSchema', {}))
                    }
                })
    
    async def chat(self, user_message: str) -> str:
        """
        Have a conversation with the agent.
        
        Args:
            user_message: User's message in natural language
            
        Returns:
            Agent's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get response from AI with tools
        if self.use_anthropic:
            response = await self._chat_anthropic()
        else:
            response = await self._chat_openai()
        
        return response
    
    async def _chat_anthropic(self) -> str:
        """Handle conversation using Claude (Anthropic)"""
        
        # System prompt for the agent
        system_prompt = """You are a helpful advertising campaign manager for Yahoo Advertising.

You have access to tools that let you:
- Discover advertising inventory (products)
- List creative format options
- Create media buy campaigns
- Check campaign performance
- Update campaigns
- Generate reports

Guidelines:
1. Always be helpful and conversational
2. Before creating a campaign, confirm details with the user
3. Explain technical terms in simple language
4. Use tools proactively to help users
5. Format monetary amounts nicely (e.g., $50,000 not 50000)
6. Suggest next steps after completing actions

**CRITICAL RULES FOR CAMPAIGN CREATION:**
1. ALWAYS call list_creative_formats FIRST before creating any campaign
2. ONLY use format IDs that are returned by list_creative_formats
3. NEVER invent or guess format IDs (e.g., don't use "native_content_feed", "native_in_stream", "display_320x50" unless they appear in list_creative_formats)
4. Parse the list_creative_formats response and extract the exact "id" field from each format
5. If a format doesn't exist in list_creative_formats, DO NOT USE IT
6. If create_media_buy fails with "format not supported", call list_creative_formats again and use ONLY the IDs from that response

Valid format ID pattern examples (but ALWAYS verify with list_creative_formats):
- display_728x90
- display_300x250
- display_160x600
- video_16x9_15s
- video_16x9_30s
- native_article_sponsored

When users ask about advertising options, use get_products.
When creating campaigns, always confirm budget and dates first.
Be enthusiastic and supportive!"""
        
        try:
            response = self.ai_client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                tools=self.ai_tools,
                messages=self.conversation_history
            )
            
            # Handle tool calls
            if response.stop_reason == "tool_use":
                return await self._handle_tool_calls_anthropic(response)
            
            # Regular text response
            assistant_message = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    assistant_message = block.text
                elif isinstance(block, dict) and 'text' in block:
                    assistant_message = block['text']
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            return assistant_message
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def _handle_tool_calls_anthropic(self, response) -> str:
        """Handle tool calls from Claude"""
        
        # Add assistant's response with tool calls to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response.content
        })
        
        # Execute each tool call
        tool_results = []
        
        async with Client(self.mcp_url) as mcp:
            for block in response.content:
                if hasattr(block, 'type') and block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id
                    
                    print(f"\n🔧 Calling tool: {tool_name}")
                    print(f"   Input: {json.dumps(tool_input, indent=2)}")
                    
                    try:
                        # Call MCP tool
                        result = await mcp.call_tool(tool_name, tool_input)
                        
                        # Extract content
                        if hasattr(result, 'content'):
                            if isinstance(result.content, list) and len(result.content) > 0:
                                tool_result = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                            else:
                                tool_result = str(result.content)
                        else:
                            tool_result = str(result)
                        
                        print(f"✅ Tool result received")
                        
                        # ============================================================
                        # CEM WEBHOOK: Notify internal team when campaign is created
                        # ============================================================
                        if tool_name == "create_media_buy" and "error" not in tool_result.lower():
                            try:
                                # Parse the result to extract campaign data
                                result_data = json.loads(tool_result)
                                
                                # Build webhook payload
                                webhook_payload = {
                                    "media_buy_id": result_data.get("media_buy_id"),
                                    "campaign_name": result_data.get("campaign_name"),
                                    "total_budget": result_data.get("total_budget"),
                                    "flight_start_date": result_data.get("flight_start_date"),
                                    "flight_end_date": result_data.get("flight_end_date"),
                                    "created_by": "streamlit_agent",
                                    "source": "advertising_agent"
                                }
                                
                                # Call webhook (async)
                                await self._notify_cem_webhook(webhook_payload)
                                
                            except json.JSONDecodeError:
                                print("   ℹ️  Could not parse result for CEM notification")
                            except Exception as e:
                                print(f"   ⚠️  CEM notification error: {e}")
                        # ============================================================
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": tool_result
                        })
                        
                    except Exception as e:
                        print(f"❌ Tool call failed: {e}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": f"Error: {str(e)}",
                            "is_error": True
                        })
        
        # Add tool results to history
        self.conversation_history.append({
            "role": "user",
            "content": tool_results
        })
        
        # Get final response from Claude
        final_response = self.ai_client.messages.create(
            model=self.model,
            max_tokens=4096,
            system="You are a helpful advertising campaign manager for Yahoo Advertising.",
            tools=self.ai_tools,
            messages=self.conversation_history
        )
        
        # Check if more tool calls needed (recursive)
        if final_response.stop_reason == "tool_use":
            return await self._handle_tool_calls_anthropic(final_response)
        
        # Extract final text response
        assistant_message = ""
        for block in final_response.content:
            if hasattr(block, 'text'):
                assistant_message = block.text
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response.content
        })
        
        return assistant_message
    
    async def _chat_openai(self) -> str:
        """Handle conversation using GPT-4 (OpenAI)"""
        # TODO: Implement OpenAI version if needed
        return "OpenAI implementation coming soon. Use Anthropic (Claude) for now."
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🔄 Conversation reset")


async def main():
    """Main interactive loop"""
    
    # Configuration
    MCP_SERVER_URL = os.getenv(
        "MCP_SERVER_URL",
        "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp"
    )
    
    print("="*70)
    print("🎯 YAHOO ADVERTISING AGENT - Agentic Experience Demo")
    print("="*70)
    print()
    print("This AI agent helps you create and manage advertising campaigns")
    print("using natural language conversation.")
    print()
    
    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: No AI API key found!")
        print()
        print("Please set one of:")
        print("  export ANTHROPIC_API_KEY=your_key")
        print("  export OPENAI_API_KEY=your_key")
        print()
        print("Or add to your .env file")
        sys.exit(1)
    
    # Initialize agent
    try:
        agent = AdvertisingAgent(
            mcp_url=MCP_SERVER_URL,
            use_anthropic=True
        )
        
        await agent.initialize()
        
    except Exception as e:
        print(f"\n❌ Failed to initialize agent: {e}")
        sys.exit(1)
    
    print()
    print("="*70)
    print("💬 CONVERSATION MODE")
    print("="*70)
    print()
    print("Tips:")
    print("  • Ask about advertising options")
    print("  • Create campaigns naturally")
    print("  • Check campaign performance")
    print("  • Type 'reset' to start over")
    print("  • Type 'quit' or 'exit' to end")
    print()
    print("Example: 'Show me advertising options for Nike running shoes'")
    print()
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for using Yahoo Advertising Agent!")
                break
            
            if user_input.lower() == 'reset':
                agent.reset_conversation()
                continue
            
            # Get agent response
            print("\n🤖 Agent: ", end="", flush=True)
            response = await agent.chat(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print()


if __name__ == "__main__":
    asyncio.run(main())

