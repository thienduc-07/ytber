import pytest
import hmac
import hashlib
import base64
import json
import time
from fastapi import HTTPException
from backend.core.security import decode_and_verify_supabase_jwt, _b64url_decode

def create_test_jwt(payload: dict, secret: str = "test-secret-key-32-characters-long!!") -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig_input = f"{h_b64}.{p_b64}".encode()
    sig = hmac.new(secret.encode(), sig_input, hashlib.sha256).digest()
    s_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{h_b64}.{p_b64}.{s_b64}"

def test_valid_jwt_decoding():
    secret = "my-test-super-secret-key-32-chars!!"
    payload = {"sub": "user-12345", "role": "authenticated", "exp": int(time.time()) + 3600}
    token = create_test_jwt(payload, secret)
    
    decoded = decode_and_verify_supabase_jwt(token, secret=secret)
    assert decoded["sub"] == "user-12345"
    assert decoded["role"] == "authenticated"

def test_expired_jwt_rejection():
    secret = "my-test-super-secret-key-32-chars!!"
    payload = {"sub": "user-expired", "exp": int(time.time()) - 100}
    token = create_test_jwt(payload, secret)
    
    with pytest.raises(HTTPException) as exc:
        decode_and_verify_supabase_jwt(token, secret=secret)
    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail.lower()

def test_invalid_signature_rejection():
    secret_real = "real-secret-key-must-be-32-chars-long!"
    secret_fake = "fake-secret-key-must-be-32-chars-long!"
    payload = {"sub": "user-hacker", "exp": int(time.time()) + 3600}
    token = create_test_jwt(payload, secret_fake)
    
    with pytest.raises(HTTPException) as exc:
        decode_and_verify_supabase_jwt(token, secret=secret_real)
    assert exc.value.status_code == 401
    assert "verification failed" in exc.value.detail.lower()

def test_malformed_token_rejection():
    with pytest.raises(HTTPException) as exc:
        decode_and_verify_supabase_jwt("not.a.valid.jwt.token")
    assert exc.value.status_code == 401
