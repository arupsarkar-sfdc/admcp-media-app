"""
Test script for Nike A2A Agent (Local)

Tests Nike agent's ability to communicate with Yahoo agent via A2A protocol.
"""

import json
import httpx
import asyncio

# Server configuration
NIKE_SERVER_URL = "http://localhost:8002"
NIKE_AGENT_CARD_URL = f"{NIKE_SERVER_URL}/a2a/nike_campaign_agent/.well-known/agent.json"
NIKE_TASK_ENDPOINT = f"{NIKE_SERVER_URL}/a2a/nike_campaign_agent"

async def test_health():
    """Test health endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Nike Agent Health Check")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{NIKE_SERVER_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✅ Nike agent health check passed")

async def test_agent_card():
    """Test Nike agent card endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Nike Agent Card Discovery")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(NIKE_AGENT_CARD_URL)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Agent Card:\n{json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data["name"] == "nike_campaign_agent"
        assert len(data["skills"]) > 0
        print(f"✅ Nike agent card retrieved: {data['name']}")
        print(f"   Skills available: {', '.join([s['id'] for s in data['skills']])}")

async def test_connection_skill():
    """Test Nike agent's test_connection skill (calls Yahoo echo)"""
    print("\n" + "="*70)
    print("TEST 3: Nike → Yahoo Connection Test")
    print("="*70)
    
    # Prepare A2A request (JSON-RPC 2.0)
    request_payload = {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": "test_connection",
            "input": "Hello from Nike test!"
        },
        "id": 1
    }
    
    print(f"Request to Nike:\n{json.dumps(request_payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            NIKE_TASK_ENDPOINT,
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response from Nike:\n{json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert data["result"]["status"] == "success"
        print("✅ Nike → Yahoo connection test successful")
        print(f"   Yahoo echoed: {data['result']['yahoo_response']['message']}")

async def test_plan_campaign_skill():
    """Test Nike agent's plan_campaign skill"""
    print("\n" + "="*70)
    print("TEST 4: Nike Campaign Planning (Phase 2 - Basic)")
    print("="*70)
    
    request_payload = {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": "plan_campaign",
            "input": "Nike Air Max campaign for Q1 2025, budget $50k, target US sports enthusiasts"
        },
        "id": 2
    }
    
    print(f"Request to Nike:\n{json.dumps(request_payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            NIKE_TASK_ENDPOINT,
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response from Nike:\n{json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        print("✅ Campaign planning skill executed")
        print(f"   Note: {data['result']['note']}")

async def test_invalid_skill():
    """Test invalid skill handling"""
    print("\n" + "="*70)
    print("TEST 5: Invalid Skill Handling")
    print("="*70)
    
    request_payload = {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": "nonexistent_skill",
            "input": "test"
        },
        "id": 3
    }
    
    print(f"Request:\n{json.dumps(request_payload, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            NIKE_TASK_ENDPOINT,
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
    print("🧪 Nike A2A Agent - Local Tests")
    print("="*70)
    print(f"Nike Server: {NIKE_SERVER_URL}")
    print(f"Yahoo Server: https://yahoo-a2a-agent-72829d23cce8.herokuapp.com")
    print("="*70)
    
    try:
        await test_health()
        await test_agent_card()
        await test_connection_skill()
        await test_plan_campaign_skill()
        await test_invalid_skill()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED - PHASE 2 COMPLETE!")
        print("="*70)
        print("\n🎉 Nike ↔ Yahoo A2A Communication Working!")
        print("\n💡 Next steps:")
        print("   1. Deploy Nike agent to Heroku")
        print("   2. Test deployed Nike → Yahoo communication")
        print("   3. Move to Phase 3: Add real Yahoo skills (discover_products, create_campaign)")
        print("   4. Move to Phase 4: Integrate Claude with Nike agent")
        print("="*70 + "\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ TEST FAILED: {str(e)}")
        print("="*70)
        print("\n💡 Troubleshooting:")
        print("   1. Make sure Yahoo A2A server is running on Heroku")
        print("   2. Make sure Nike A2A server is running: uv run python nike_agent.py")
        print("   3. Check logs for errors")
        print("="*70 + "\n")
        raise

if __name__ == "__main__":
    asyncio.run(run_all_tests())

