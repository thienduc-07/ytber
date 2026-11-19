import base64
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
import jwt
from backend.core.config import settings

def _b64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def decode_and_verify_supabase_jwt(token: str, secret: Optional[str] = None) -> Dict[str, Any]:
    """
    Decodes and verifies a standard Supabase JWT token with strict FAIL-CLOSED security.
    Validates token structure, algorithm, signature, and expiration.
    Never bypasses verification for missing or placeholder secrets.
    """
    jwt_secret = secret or settings.SUPABASE_JWT_SECRET
    if not jwt_secret or jwt_secret.startswith("placeholder-"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Server JWT secret is not configured or placeholder. Signature verification cannot be performed.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # First verify unverified header to ensure allowed algorithms only
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg")
        if alg not in ("HS256", "RS256"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: Unsupported signing algorithm '{alg}'. Only HS256 and RS256 are permitted.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Strictly verify signature and expiration
        payload = jwt.decode(
            token,
            key=jwt_secret,
            algorithms=[alg],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["exp", "sub"]
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: JWT token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: JWT signature verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: Malformed or unparseable JWT token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """
    FastAPI dependency to authenticate requests and extract user_id (sub).
    Strictly enforces Bearer format and fail-closed validation.
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
