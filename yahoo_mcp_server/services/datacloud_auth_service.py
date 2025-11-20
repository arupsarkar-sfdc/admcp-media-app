"""
Salesforce Data Cloud Authentication Service
Manages JWT token retrieval and caching for Data Cloud API access
"""
import os
import time
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class DataCloudAuthService:
    """Handle authentication with Salesforce Data Cloud"""
    
    def __init__(self, token_url: Optional[str] = None):
        """
        Initialize the auth service
        
        Args:
            token_url: Override token endpoint (defaults to env var or Heroku connector)
        """
        self.token_url = token_url or os.getenv(
            "DATACLOUD_TOKEN_URL",
            "https://acme-dcunited-connector-app-58a61db33e61.herokuapp.com/get-token"
        )
        
        # Token cache
        self._access_token: Optional[str] = None
        self._instance_url: Optional[str] = None
        self._expires_at: Optional[float] = None
        self._refresh_buffer = 300  # Refresh 5 minutes before expiration
    
    def _is_token_valid(self) -> bool:
        """Check if cached token is still valid"""
        if not self._access_token or not self._expires_at:
            return False
        
        # Check if token expires soon (within refresh buffer)
        return time.time() < (self._expires_at - self._refresh_buffer)
    
    async def _fetch_new_token(self) -> Dict[str, Any]:
        """
        Fetch a new JWT token from the token service
        
        Returns:
            Token response data
            
        Raises:
            httpx.HTTPError: If token fetch fails
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.token_url)
            response.raise_for_status()
            
            data = response.json()
            token_data = data.get("token", {})
            
            if not token_data.get("access_token"):
                raise ValueError("Invalid token response: missing access_token")
            
            # Log full token response for debugging
            print("\n" + "="*70)
            print("📋 FULL TOKEN RESPONSE:")
            print("="*70)
            import json
            print(json.dumps(token_data, indent=2))
            print("="*70 + "\n")
            
            return token_data
    
    async def get_access_token(self) -> str:
        """
        Get a valid access token (fetches new if expired)
        
        Returns:
            Valid JWT access token
            
        Raises:
            Exception: If token fetch fails
        """
        if self._is_token_valid():
            return self._access_token
        
        # Fetch new token
        token_data = await self._fetch_new_token()
        
        self._access_token = token_data["access_token"]
        self._instance_url = token_data.get("instance_url")
        
        # Calculate expiration time
        expires_in = token_data.get("expires_in", 28800)  # Default 8 hours
        self._expires_at = time.time() + expires_in
        
        print(f"✅ Data Cloud token refreshed (expires in {expires_in // 3600}h)")
        
        return self._access_token
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for Data Cloud API requests
        
        Returns:
            Dictionary with Authorization header
        """
        token = await self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_instance_url(self) -> Optional[str]:
        """
        Get the Data Cloud instance URL
        
        Returns:
            Instance URL or None if not yet fetched
        """
        return self._instance_url
    
    async def invalidate_token(self):
        """Force token refresh on next request"""
        self._access_token = None
        self._expires_at = None
        print("🔄 Data Cloud token cache invalidated")
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Get current token status information
        
        Returns:
            Dictionary with token status
        """
        if not self._access_token:
            return {
                "status": "no_token",
                "valid": False
            }
        
        time_remaining = self._expires_at - time.time() if self._expires_at else 0
        
        return {
            "status": "valid" if self._is_token_valid() else "expired",
            "valid": self._is_token_valid(),
            "expires_in_seconds": max(0, int(time_remaining)),
            "expires_at": datetime.fromtimestamp(self._expires_at).isoformat() if self._expires_at else None,
            "instance_url": self._instance_url
        }


# Global singleton instance
_auth_service: Optional[DataCloudAuthService] = None


def get_datacloud_auth_service() -> DataCloudAuthService:
    """
    Get the global Data Cloud auth service instance
    
    Returns:
        Singleton DataCloudAuthService instance
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = DataCloudAuthService()
    return _auth_service

