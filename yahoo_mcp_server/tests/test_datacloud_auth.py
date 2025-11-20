"""
Test Salesforce Data Cloud Authentication Service
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.datacloud_auth_service import DataCloudAuthService


async def test_auth_service():
    """Test Data Cloud authentication flow"""
    
    print("="*70)
    print("Testing Salesforce Data Cloud Authentication Service")
    print("="*70)
    
    # Initialize service
    auth_service = DataCloudAuthService()
    
    print("\n1️⃣ Initial token status:")
    print(f"   {auth_service.get_token_info()}")
    
    print("\n2️⃣ Fetching JWT token...")
    try:
        token = await auth_service.get_access_token()
        print(f"   ✅ Token retrieved: {token[:50]}...")
        print(f"   Instance URL: {auth_service.get_instance_url()}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return
    
    print("\n3️⃣ Token status after fetch:")
    info = auth_service.get_token_info()
    print(f"   Status: {info['status']}")
    print(f"   Valid: {info['valid']}")
    print(f"   Expires in: {info['expires_in_seconds']} seconds ({info['expires_in_seconds'] // 3600}h)")
    print(f"   Expires at: {info['expires_at']}")
    
    print("\n4️⃣ Getting auth headers:")
    headers = await auth_service.get_auth_headers()
    print(f"   Authorization: Bearer {headers['Authorization'][7:57]}...")
    print(f"   Content-Type: {headers['Content-Type']}")
    
    print("\n5️⃣ Testing token reuse (should use cached token):")
    token2 = await auth_service.get_access_token()
    print(f"   ✅ Same token reused: {token == token2}")
    
    print("\n6️⃣ Invalidating token cache:")
    await auth_service.invalidate_token()
    print(f"   Status: {auth_service.get_token_info()['status']}")
    
    print("\n7️⃣ Fetching new token after invalidation:")
    token3 = await auth_service.get_access_token()
    print(f"   ✅ New token retrieved: {token3[:50]}...")
    print(f"   Different from previous: {token != token3}")
    
    print("\n" + "="*70)
    print("✅ Authentication Service Test Complete!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_auth_service())

