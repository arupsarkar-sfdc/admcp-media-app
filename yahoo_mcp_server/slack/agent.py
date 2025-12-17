"""
Slack Advertising Agent

Adapted from advertising_agent.py for Slack context.
Provides per-user conversation history and Slack-optimized responses.

Now includes Salesforce CRM integration:
- Automatically creates Opportunity when campaign is created
- Links campaign_id to Opportunity via Description field
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
from pathlib import Path
from datetime import date, timedelta

# Import MCP client
from fastmcp import Client

# Import Anthropic (Claude)
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Import Salesforce client
try:
    from simple_salesforce import Salesforce
    HAS_SALESFORCE = True
except ImportError:
    HAS_SALESFORCE = False

logger = logging.getLogger(__name__)


def get_salesforce_client() -> Optional[Salesforce]:
    """
    Initialize Salesforce client using JWT Bearer Flow.
    Returns None if not configured or connection fails.
    """
    if not HAS_SALESFORCE:
        logger.warning("simple-salesforce not installed, Salesforce integration disabled")
        return None
    
    # Check required env vars
    username = os.environ.get('SFDC_USER_NAME')
    consumer_key = os.environ.get('SFDC_CONSUMER_KEY')
    login_url = os.environ.get('SFDC_LOGIN_URL', 'https://login.salesforce.com')
    
    if not username or not consumer_key:
        logger.warning("SFDC credentials not configured, Salesforce integration disabled")
        return None
    
    # Get private key - prefer file, fallback to inline
    private_key = None
    key_file = os.environ.get('SFDC_PRIVATE_KEY_FILE')
    
    if key_file:
        key_path = Path(key_file)
        if not key_path.is_absolute():
            # Relative to yahoo_mcp_server folder
            key_path = Path(__file__).parent.parent / key_file
        
        if key_path.exists():
            private_key = key_path.read_text()
            logger.info(f"Loaded Salesforce private key from: {key_path}")
        else:
            logger.warning(f"Salesforce key file not found: {key_path}")
    else:
        private_key = os.environ.get('SFDC_PRIVATE_KEY')
        if private_key and '\\n' in private_key:
            private_key = private_key.replace('\\n', '\n')
    
    if not private_key:
        logger.warning("SFDC_PRIVATE_KEY not configured, Salesforce integration disabled")
        return None
    
    # Determine domain from login URL
    if 'test.salesforce.com' in login_url:
        domain = 'test'
    elif 'login.salesforce.com' in login_url:
        domain = 'login'
    else:
        domain = login_url.replace('https://', '').replace('http://', '').split('.')[0]
    
    try:
        sf = Salesforce(
            username=username,
            consumer_key=consumer_key,
            privatekey=private_key,
            domain=domain
        )
        logger.info(f"Salesforce connected: {sf.sf_instance}")
        return sf
    except Exception as e:
        logger.error(f"Failed to connect to Salesforce: {e}")
        return None


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

SALESFORCE CRM INTEGRATION:
When you successfully create a campaign, a Salesforce Opportunity is AUTOMATICALLY created and linked.
The Opportunity info will appear in the tool result - include it in your response to the user.
Always mention both the campaign AND the Opportunity when reporting success.

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
        
        # Initialize Salesforce client (optional - for CRM integration)
        self.sf_client = get_salesforce_client()
        if self.sf_client:
            logger.info("Salesforce CRM integration enabled")
        else:
            logger.info("Salesforce CRM integration disabled (not configured)")
        
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
                        
                        # ================================================================
                        # 🎯 POST-CAMPAIGN CREATION HOOK
                        # ================================================================
                        if tool_name == "create_media_buy" and "error" not in tool_result.lower():
                            
                            # --------------------------------------------------------
                            # COMMENTED OUT: CRM Opportunity Creation
                            # Keeping for later use - will be triggered after CEM approval
                            # --------------------------------------------------------
                            # opp_result = self._create_opportunity_for_campaign(tool_result, tool_input)
                            # if opp_result:
                            #     tool_results.append({
                            #         "tool": "salesforce_opportunity",
                            #         "input": {"campaign_id": tool_input.get("campaign_name", "")},
                            #         "result": opp_result
                            #     })
                            #     tool_result += f"\n\n✅ SALESFORCE OPPORTUNITY CREATED:\n- ID: {opp_result['opportunity_id']}\n- URL: {opp_result['opportunity_url']}"
                            # --------------------------------------------------------
                            
                            # 🔄 CEM ORCHESTRATION: Trigger Yahoo internal approval workflow
                            # This is INTERNAL to Yahoo - not part of AdCP protocol
                            cem_result = await self._trigger_cem_workflow(tool_result, tool_input)
                            if cem_result:
                                tool_result += f"\n\n📋 ORDER SUBMITTED FOR CEM REVIEW:\n{cem_result.get('message', 'Pending approval')}"
                        
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
    
    def _create_opportunity_for_campaign(
        self, 
        campaign_result: str, 
        tool_input: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Salesforce Opportunity linked to a campaign.
        
        Called automatically after successful create_media_buy.
        Uses Acme Partners as default account (PoC).
        
        Returns:
            Dict with opportunity_id and url, or None if failed
        """
        if not self.sf_client:
            logger.info("Salesforce not configured, skipping Opportunity creation")
            return None
        
        try:
            # Parse campaign result to extract details
            result_data = json.loads(campaign_result) if isinstance(campaign_result, str) else campaign_result
            
            # Extract campaign info
            campaign_id = result_data.get('campaign_id', 'unknown')
            campaign_name = result_data.get('campaign_name', tool_input.get('campaign_name', 'Campaign'))
            
            # Get budget from tool input or result
            budget = tool_input.get('budget', 0)
            if isinstance(budget, str):
                budget = float(budget.replace('$', '').replace(',', ''))
            
            # Find Acme Partners account (PoC hardcoded)
            account_query = self.sf_client.query(
                "SELECT Id, Name FROM Account WHERE Name LIKE '%Acme%' LIMIT 1"
            )
            
            if account_query['totalSize'] == 0:
                logger.warning("Acme account not found, creating Opportunity without Account link")
                account_id = None
            else:
                account_id = account_query['records'][0]['Id']
                logger.info(f"Found Account: {account_query['records'][0]['Name']}")
            
            # Create Opportunity
            close_date = (date.today() + timedelta(days=90)).isoformat()
            
            opp_data = {
                'Name': f"{campaign_name} - Yahoo Advertising",
                'StageName': 'Prospecting',
                'CloseDate': close_date,
                'Amount': budget,
                'Description': f"Auto-created from Slack MCP integration.\n\nCampaign ID: {campaign_id}\nCreated via AdCP workflow."
            }
            
            if account_id:
                opp_data['AccountId'] = account_id
            
            logger.info(f"Creating Opportunity: {opp_data['Name']}")
            result = self.sf_client.Opportunity.create(opp_data)
            
            if result.get('success'):
                opp_id = result['id']
                opp_url = f"https://{self.sf_client.sf_instance}/lightning/r/Opportunity/{opp_id}/view"
                
                logger.info(f"✅ Opportunity created: {opp_id}")
                
                return {
                    'opportunity_id': opp_id,
                    'opportunity_name': opp_data['Name'],
                    'opportunity_url': opp_url,
                    'amount': budget,
                    'stage': 'Prospecting',
                    'account': account_query['records'][0]['Name'] if account_id else None
                }
            else:
                logger.error(f"Failed to create Opportunity: {result}")
                return None
                
        except json.JSONDecodeError:
            logger.warning("Could not parse campaign result, skipping Opportunity")
            return None
        except Exception as e:
            logger.error(f"Error creating Opportunity: {e}")
            return None
    
    async def _trigger_cem_workflow(
        self,
        campaign_result: str,
        tool_input: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Trigger Yahoo's internal CEM approval workflow.
        
        This is Yahoo's internal process - NOT part of AdCP protocol.
        
        Steps:
        1. Parse media_buy_id from result
        2. Run SQL validation against master tables
        3. Log everything to audit_log
        4. Generate AI summary for CEM review
        5. Post to Slack for human approval (approve/reject/review)
        
        Args:
            campaign_result: JSON string result from create_media_buy
            tool_input: Original tool input parameters
            
        Returns:
            Dict with workflow status or None if failed
        """
        try:
            # Parse result to get media_buy_id
            result_data = json.loads(campaign_result)
            media_buy_id = result_data.get('media_buy_id')
            
            if not media_buy_id:
                logger.warning("No media_buy_id in result, skipping CEM workflow")
                return None
            
            logger.info(f"🔄 Starting CEM workflow for media_buy_id: {media_buy_id}")
            
            # Import automation modules
            from automation import OrderValidator, AuditLogger, CEMAgent
            
            # Step 1: Validate order against master tables
            validator = OrderValidator()
            validation_result = validator.validate_order(media_buy_id)
            
            logger.info(f"Validation result: {validation_result.summary}")
            
            # Get full order details
            order_details = validator.get_order_details(media_buy_id)
            
            if not order_details:
                logger.error(f"Could not retrieve order details for {media_buy_id}")
                return {"message": "⚠️ Validation failed - could not retrieve order"}
            
            # Step 2: Log validation to audit_log
            audit = AuditLogger()
            audit.log_validation(
                media_buy_id=media_buy_id,
                validation_result={
                    'all_passed': validation_result.all_passed,
                    'summary': validation_result.summary,
                    'checks': [
                        {
                            'check_name': c.check_name,
                            'passed': c.passed,
                            'message': c.message
                        }
                        for c in validation_result.checks
                    ]
                },
                principal_id=order_details.get('principal_id'),
                tenant_id='yahoo'  # Yahoo's tenant
            )
            
            # Step 3: Generate AI summary for CEM
            cem_agent = CEMAgent()
            cem_summary = cem_agent.generate_summary(
                order_details=order_details,
                validation_result={
                    'all_passed': validation_result.all_passed,
                    'summary': validation_result.summary,
                    'checks': [
                        {
                            'check_name': c.check_name,
                            'passed': c.passed,
                            'message': c.message,
                            'details': c.details
                        }
                        for c in validation_result.checks
                    ]
                }
            )
            
            # Step 4: Log approval request
            audit.log_approval_requested(
                media_buy_id=media_buy_id,
                order_details=order_details,
                validation_summary=cem_summary.order_summary,
                cem_channel='slack_cem'
            )
            
            # Step 5: Post to Slack for CEM approval
            # The blocks will be posted in the response
            # Store the summary for posting
            self._pending_cem_summary = cem_summary
            
            logger.info(f"✅ CEM workflow initiated for {media_buy_id}")
            logger.info(f"   Recommendation: {cem_summary.recommendation.action}")
            
            return {
                "message": f"Order submitted for CEM review. Recommendation: {cem_summary.recommendation.action.upper()}",
                "media_buy_id": media_buy_id,
                "validation_passed": validation_result.all_passed,
                "recommendation": cem_summary.recommendation.action,
                "risk_level": cem_summary.recommendation.risk_level
            }
            
        except json.JSONDecodeError:
            logger.warning("Could not parse campaign result for CEM workflow")
            return None
        except ImportError as e:
            logger.error(f"Could not import automation modules: {e}")
            return {"message": "⚠️ CEM workflow not available - automation module not found"}
        except Exception as e:
            logger.error(f"Error in CEM workflow: {e}")
            return {"message": f"⚠️ CEM workflow error: {str(e)}"}
    
    def get_pending_cem_summary(self):
        """Get pending CEM summary for posting to Slack"""
        summary = getattr(self, '_pending_cem_summary', None)
        if summary:
            self._pending_cem_summary = None  # Clear after retrieval
        return summary

