"""
Nike A2A Campaign Agent

This agent orchestrates advertising campaigns by delegating to Yahoo Sales Agent
via the A2A protocol. It uses Anthropic Claude for natural language understanding
and task planning.

Architecture:
    User → Nike A2A Agent (Claude) → Yahoo A2A Agent → MCP Tools → Data Cloud/Snowflake
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import httpx
from dotenv import load_dotenv

# A2A SDK imports
from a2a.types import AgentCard, AgentSkill

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nike A2A Campaign Agent",
    description="Campaign planning orchestrator using A2A protocol",
    version="1.0.0"
)

# Configuration
YAHOO_AGENT_URL = os.getenv(
    "YAHOO_AGENT_URL",
    "https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent"
)
YAHOO_AGENT_CARD_URL = os.getenv(
    "YAHOO_AGENT_CARD_URL",
    "https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent/.well-known/agent.json"
)

# Load Nike agent card
AGENT_CARD_PATH = Path(__file__).parent / "nike-agent-card.json"
with open(AGENT_CARD_PATH, 'r') as f:
    AGENT_CARD_DATA = json.load(f)

# =============================================================================
# A2A Client - Call Remote Yahoo Agent
# =============================================================================

class YahooA2AClient:
    """Client for calling Yahoo A2A Sales Agent"""
    
    def __init__(self, agent_url: str, agent_card_url: str):
        self.agent_url = agent_url
        self.agent_card_url = agent_card_url
        self.agent_card: Optional[Dict[str, Any]] = None
        
    async def load_agent_card(self) -> Dict[str, Any]:
        """Load Yahoo agent's card to discover capabilities"""
        if self.agent_card:
            return self.agent_card
            
        logger.info(f"📋 Loading Yahoo agent card from: {self.agent_card_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.agent_card_url)
            response.raise_for_status()
            self.agent_card = response.json()
            
        logger.info(f"✅ Loaded Yahoo agent: {self.agent_card['name']}")
        logger.info(f"   Skills: {', '.join([s['id'] for s in self.agent_card['skills']])}")
        
        return self.agent_card
    
    async def execute_skill(
        self,
        skill_id: str,
        input_data: str,
        request_id: int = 1
    ) -> Dict[str, Any]:
        """
        Execute a skill on Yahoo agent via A2A protocol
        
        Args:
            skill_id: The skill to execute (e.g., "echo", "discover_products")
            input_data: Input for the skill
            request_id: JSON-RPC request ID
            
        Returns:
            Result from Yahoo agent
        """
        logger.info(f"🎯 Calling Yahoo agent skill: {skill_id}")
        
        # Prepare A2A request (JSON-RPC 2.0)
        request_payload = {
            "jsonrpc": "2.0",
            "method": "task/execute",
            "params": {
                "skill_id": skill_id,
                "input": input_data
            },
            "id": request_id
        }
        
        logger.info(f"📤 Request: {json.dumps(request_payload, indent=2)}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.agent_url,
                json=request_payload,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            result = response.json()
            
        logger.info(f"📥 Response: {json.dumps(result, indent=2)}")
        
        if "error" in result:
            raise Exception(f"Yahoo agent error: {result['error']['message']}")
        
        return result["result"]

# Initialize Yahoo client
yahoo_client = YahooA2AClient(YAHOO_AGENT_URL, YAHOO_AGENT_CARD_URL)

# =============================================================================
# Nike Agent Skills
# =============================================================================

async def skill_test_connection(input_data: str) -> Dict[str, Any]:
    """
    Test A2A connectivity with Yahoo agent using echo skill
    
    Args:
        input_data: Message to echo
        
    Returns:
        Echo response from Yahoo agent
    """
    logger.info(f"🧪 Testing connection to Yahoo agent")
    
    # Call Yahoo's echo skill
    result = await yahoo_client.execute_skill(
        skill_id="echo",
        input_data=input_data
    )
    
    return {
        "status": "success",
        "test": "connection",
        "yahoo_response": result,
        "message": "Successfully connected to Yahoo A2A Sales Agent!"
    }

async def skill_plan_campaign(input_data: str) -> Dict[str, Any]:
    """
    Plan a campaign (Phase 4 - will integrate Claude)
    
    For now, just echoes back via Yahoo agent
    
    Args:
        input_data: Campaign requirements
        
    Returns:
        Campaign plan
    """
    logger.info(f"📋 Planning campaign: {input_data}")
    
    # For Phase 2, just test connectivity
    # Phase 4 will add Claude orchestration
    result = await yahoo_client.execute_skill(
        skill_id="echo",
        input_data=f"Campaign planning request: {input_data}"
    )
    
    return {
        "status": "success",
        "skill": "plan_campaign",
        "note": "Phase 2: Basic connectivity test. Phase 4 will add Claude orchestration.",
        "yahoo_response": result
    }

# Skill registry
SKILLS = {
    "test_connection": skill_test_connection,
    "plan_campaign": skill_plan_campaign,
}

# =============================================================================
# A2A Protocol Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Nike A2A Campaign Agent",
        "status": "active",
        "version": "1.0.0",
        "protocol": "A2A",
        "agent_card": "/a2a/nike_campaign_agent/.well-known/agent.json",
        "yahoo_agent": YAHOO_AGENT_URL
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "nike_campaign_agent",
        "yahoo_agent_connected": YAHOO_AGENT_URL
    }

@app.get("/a2a/nike_campaign_agent/.well-known/agent.json")
async def get_agent_card():
    """
    Serve the agent card (A2A discovery endpoint).
    This allows other agents to discover Nike agent's capabilities.
    """
    logger.info("📋 Agent card requested")
    return JSONResponse(content=AGENT_CARD_DATA)

@app.post("/a2a/nike_campaign_agent")
async def execute_task(request: Request):
    """
    Main A2A task execution endpoint.
    
    Receives A2A protocol messages and executes the requested skill.
    
    Expected JSON-RPC 2.0 format:
    {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": "test_connection",
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
            result = await skill_function(task_input)
            
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
# Startup Event
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Load Yahoo agent card on startup"""
    try:
        await yahoo_client.load_agent_card()
    except Exception as e:
        logger.error(f"❌ Failed to load Yahoo agent card: {str(e)}")
        logger.warning("⚠️  Nike agent will start but Yahoo connectivity may fail")

# =============================================================================
# Server Startup
# =============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    
    print("\n" + "="*70)
    print("🚀 Nike A2A Campaign Agent Server")
    print("="*70)
    print(f"📍 Server URL: http://localhost:{port}")
    print(f"📋 Agent Card: http://localhost:{port}/a2a/nike_campaign_agent/.well-known/agent.json")
    print(f"🎯 Task Endpoint: http://localhost:{port}/a2a/nike_campaign_agent")
    print(f"💡 Protocol: A2A (JSON-RPC 2.0)")
    print(f"🔧 Skills: {', '.join(SKILLS.keys())}")
    print(f"🔗 Yahoo Agent: {YAHOO_AGENT_URL}")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

