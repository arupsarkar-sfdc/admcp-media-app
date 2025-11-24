"""
Test script for Yahoo A2A Server (Local)

Tests the Yahoo A2A agent's echo skill locally before deployment.
"""

import json
import httpx
import asyncio

# Server configuration
SERVER_URL = "http://localhost:8001"
AGENT_CARD_URL = f"{SERVER_URL}/a2a/yahoo_sales_agent/.well-known/agent.json"
TASK_ENDPOINT = f"{SERVER_URL}/a2a/yahoo_sales_agent"

async def test_health():
    """Test health endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✅ Health check passed")

async def test_agent_card():
    """Test agent card endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Agent Card Discovery")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(AGENT_CARD_URL)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Agent Card:\n{json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data["name"] == "yahoo_sales_agent"
        assert len(data["skills"]) > 0
        print(f"✅ Agent card retrieved: {data['name']}")
        print(f"   Skills available: {', '.join([s['id'] for s in data['skills']])}")

async def test_echo_skill():
    """Test echo skill"""
    print("\n" + "="*70)
    print("TEST 3: Echo Skill Execution")
    print("="*70)
    
    # Prepare A2A request (JSON-RPC 2.0)
    request_payload = {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": "echo",
            "input": "Hello from Nike A2A Agent!"
        },
        "id": 1
    }
    
    print(f"Request:\n{json.dumps(request_payload, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TASK_ENDPOINT,
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert data["result"]["status"] == "success"
        print("✅ Echo skill executed successfully")
        print(f"   Message: {data['result']['message']}")

async def test_invalid_skill():
    """Test invalid skill handling"""
    print("\n" + "="*70)
    print("TEST 4: Invalid Skill Handling")
    print("="*70)
    
    request_payload = {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": "nonexistent_skill",
            "input": "test"
        },
        "id": 2
    }
    
    print(f"Request:\n{json.dumps(request_payload, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TASK_ENDPOINT,
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        assert response.status_code == 404
        assert "error" in data
        print("✅ Invalid skill handled correctly")

async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 Yahoo A2A Server - Local Tests")
    print("="*70)
    print(f"Server: {SERVER_URL}")
    print("="*70)
    
    try:
        await test_health()
        await test_agent_card()
        await test_echo_skill()
        await test_invalid_skill()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\n💡 Next steps:")
        print("   1. Deploy to Heroku")
        print("   2. Test deployed endpoint with cURL")
        print("   3. Move to Phase 2: Nike A2A Agent")
        print("="*70 + "\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ TEST FAILED: {str(e)}")
        print("="*70)
        raise

if __name__ == "__main__":
    asyncio.run(run_all_tests())

