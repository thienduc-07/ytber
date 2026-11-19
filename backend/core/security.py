import base64
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
import jwt
from backend.core.config import settings

def _b64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def decode_and_verify_supabase_jwt(
    token: str,
    secret: Optional[str] = None,
    audience: Optional[str] = None,
    issuer: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Decodes and verifies a standard Supabase JWT token with strict FAIL-CLOSED security.
    Validates token structure, algorithm, signature, expiration, audience, and issuer.
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

        # Determine expected audience and issuer
        expected_aud = audience if audience is not None else settings.SUPABASE_JWT_AUDIENCE

        expected_iss = issuer
        if expected_iss is None:
            if settings.SUPABASE_JWT_ISSUER:
                expected_iss = settings.SUPABASE_JWT_ISSUER
            elif settings.SUPABASE_URL and not settings.SUPABASE_URL.startswith("https://placeholder-"):
                expected_iss = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"

        # Configure decode options
        decode_options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_aud": False,  # Custom validated below for audience/role compatibility
            "verify_iss": bool(expected_iss),
            "require": ["exp", "sub"]
        }
        if expected_iss:
            decode_options["require"].append("iss")

        # Strictly verify signature, expiration, and issuer
        payload = jwt.decode(
            token,
            key=jwt_secret,
            algorithms=[alg],
            issuer=expected_iss if expected_iss else None,
            options=decode_options
        )

        # Strictly verify audience (checking 'aud' claim, with fallback to 'role')
        if expected_aud:
            token_aud = payload.get("aud")
            token_role = payload.get("role")
            if token_aud is not None:
                if isinstance(token_aud, list):
                    if expected_aud not in token_aud:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed: JWT audience verification failed",
                            headers={"WWW-Authenticate": "Bearer"},
                        )
                elif token_aud != expected_aud:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication failed: JWT audience verification failed",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            elif token_role is not None:
                if token_role != expected_aud:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication failed: JWT audience verification failed",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication failed: Missing required JWT claim: Token is missing the 'aud' claim",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: JWT token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: JWT audience verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: JWT issuer verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: JWT signature verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.MissingRequiredClaimError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: Missing required JWT claim: {str(e)}",
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
