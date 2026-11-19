import hmac
import hashlib
import base64
import json
import time
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
from backend.core.config import settings

def _b64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def decode_and_verify_supabase_jwt(token: str, secret: Optional[str] = None) -> Dict[str, Any]:
    """
    Decodes and verifies a standard Supabase HS256 JWT token.
    Uses Python standard library (hmac, hashlib, base64, json) for 100% zero-dependency execution.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT token format (expected 3 parts)")
        
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature if secret is provided and not default placeholder
        jwt_secret = secret or settings.SUPABASE_JWT_SECRET
        if jwt_secret and not jwt_secret.startswith("placeholder-"):
            signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
            expected_sig = hmac.new(
                jwt_secret.encode("utf-8"),
                signing_input,
                hashlib.sha256
            ).digest()
            actual_sig = _b64url_decode(signature_b64)
            if not hmac.compare_digest(expected_sig, actual_sig):
                raise ValueError("JWT signature verification failed")
        
        # Decode payload
        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
        
        # Check expiration
        exp = payload.get("exp")
        if exp and exp < time.time():
            raise ValueError("JWT token has expired")
            
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """
    FastAPI dependency to authenticate requests and extract user_id (sub).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    payload = decode_and_verify_supabase_jwt(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT token payload missing 'sub' subject claim",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return str(user_id)
