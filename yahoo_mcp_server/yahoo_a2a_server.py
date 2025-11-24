"""
Yahoo A2A Sales Agent Server

This server wraps the Yahoo MCP server with A2A protocol support,
enabling agent-to-agent communication using Google's A2A SDK.

Architecture:
    Nike A2A Agent → Yahoo A2A Server → Yahoo MCP Tools → Data Cloud/Snowflake
"""

import os
import json
import logging
from typing import Dict, Any
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn

# A2A SDK imports
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Yahoo A2A Sales Agent",
    description="A2A wrapper for Yahoo Advertising Platform",
    version="1.0.0"
)

# Load agent card
AGENT_CARD_PATH = Path(__file__).parent / "yahoo-agent-card.json"
with open(AGENT_CARD_PATH, 'r') as f:
    AGENT_CARD_DATA = json.load(f)

# =============================================================================
# A2A Skills Implementation
# =============================================================================

def skill_echo(task_input: str) -> Dict[str, Any]:
    """
    Echo skill - returns the input message.
    Used for testing A2A connectivity.
    
    Args:
        task_input: The message to echo
        
    Returns:
        Dict with echoed message
    """
    logger.info(f"🔊 Echo skill called with input: {task_input}")
    return {
        "status": "success",
        "message": f"Echo from Yahoo A2A Agent: {task_input}",
        "agent": "yahoo_sales_agent",
        "skill": "echo"
    }

# Skill registry
SKILLS = {
    "echo": skill_echo,
}

# =============================================================================
# A2A Protocol Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Yahoo A2A Sales Agent",
        "status": "active",
        "version": "1.0.0",
        "protocol": "A2A",
        "agent_card": "/a2a/yahoo_sales_agent/.well-known/agent.json"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "yahoo_sales_agent"}

@app.get("/a2a/yahoo_sales_agent/.well-known/agent.json")
async def get_agent_card():
    """
    Serve the agent card (A2A discovery endpoint).
    This allows other agents to discover Yahoo agent's capabilities.
    """
    logger.info("📋 Agent card requested")
    return JSONResponse(content=AGENT_CARD_DATA)

@app.post("/a2a/yahoo_sales_agent")
async def execute_task(request: Request):
    """
    Main A2A task execution endpoint.
    
    Receives A2A protocol messages and executes the requested skill.
    
    Expected JSON-RPC 2.0 format:
    {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": "echo",
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
            result = skill_function(task_input)
            
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
# Server Startup
# =============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    
    print("\n" + "="*70)
    print("🚀 Yahoo A2A Sales Agent Server")
    print("="*70)
    print(f"📍 Server URL: http://localhost:{port}")
    print(f"📋 Agent Card: http://localhost:{port}/a2a/yahoo_sales_agent/.well-known/agent.json")
    print(f"🎯 Task Endpoint: http://localhost:{port}/a2a/yahoo_sales_agent")
    print(f"💡 Protocol: A2A (JSON-RPC 2.0)")
    print(f"🔧 Skills: {', '.join(SKILLS.keys())}")
    print("="*70 + "\n")
    
    uvicorn.run(
        "yahoo_a2a_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

