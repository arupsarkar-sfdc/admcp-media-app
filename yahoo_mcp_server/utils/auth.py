"""
Authentication Utilities
Principal authentication via bearer token
"""
from typing import Optional
from sqlalchemy.orm import Session
from models import Principal


def authenticate_principal(session: Session, token: str) -> Optional[Principal]:
    """
    Authenticate principal by token
    
    Args:
        session: Database session
        token: Bearer token from x-adcp-auth header
    
    Returns:
        Principal object if valid, None otherwise
    """
    principal = session.query(Principal).filter(
        Principal.auth_token == token,
        Principal.is_active == 1
    ).first()
    
    return principal


def validate_request_headers(headers: dict) -> Optional[str]:
    """
    Extract and validate authentication token from headers
    
    Args:
        headers: Request headers dict
    
    Returns:
        Token string if valid, None otherwise
    """
    auth_header = headers.get("x-adcp-auth", "")
    
    if not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "").strip()
    return token if token else None

