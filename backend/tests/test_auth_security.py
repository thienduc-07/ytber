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
        decode_and_verify_supabase_jwt("not.a.valid.jwt.token", secret="valid-secret-key-32-chars-long!!")
    assert exc.value.status_code == 401

def test_fail_closed_when_secret_is_placeholder_or_missing():
    payload = {"sub": "user-test", "exp": int(time.time()) + 3600}
    token = create_test_jwt(payload, "any-secret")
    
    # Passing placeholder secret must fail closed with 401
    with pytest.raises(HTTPException) as exc:
        decode_and_verify_supabase_jwt(token, secret="placeholder-secret")
    assert exc.value.status_code == 401
    assert "cannot be performed" in exc.value.detail or "unconfigured" in exc.value.detail

def test_algorithm_none_rejection():
    # Attack vector: "alg": "none"
    header = {"alg": "none", "typ": "JWT"}
    payload = {"sub": "attacker", "exp": int(time.time()) + 3600}
    h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    none_token = f"{h_b64}.{p_b64}."
    
    with pytest.raises(HTTPException) as exc:
        decode_and_verify_supabase_jwt(none_token, secret="valid-secret-key-32-chars-long!!")
    assert exc.value.status_code == 401
    assert "algorithm" in exc.value.detail.lower()
