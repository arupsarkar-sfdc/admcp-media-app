"""Test using stdio transport"""
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_stdio():
    """Test with stdio transport"""
    print("Testing Yahoo MCP Server via stdio...")
    
    # Start server as subprocess
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "server2.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f"\nAvailable tools: {[t.name for t in tools.tools]}")
            
            # Call get_products
            result = await session.call_tool(
                "get_products",
                arguments={
                    "brief": "Display ads for sports enthusiasts",
                    "budget_range": [10000, 100000]
                }
            )
            print(f"\nResult: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(test_stdio())