import os
import uuid
import time
import pytest
import jwt
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from backend.main import app
from backend.core.config import settings
from backend.core.database import AsyncSessionLocal, init_db_sync, engine
from backend.models.db_models import ProjectModel, EpisodeModel, ChapterModel, AudioFileModel
from backend.core.security import decode_and_verify_supabase_jwt

TEST_SECRET = "test_phase1_remediation_jwt_secret_32chars_long!!"

def create_jwt(payload: dict, secret: str = TEST_SECRET, algorithm: str = "HS256") -> str:
    return jwt.encode(payload, secret, algorithm=algorithm)

def get_auth_headers(user_id: str = "user_a", secret: str = TEST_SECRET) -> dict:
    now = int(time.time())
    token = create_jwt({
        "sub": user_id,
        "aud": "authenticated",
        "exp": now + 3600,
        "iat": now,
        "iss": "https://test.supabase.co/auth/v1"
    }, secret=secret)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", TEST_SECRET)
    monkeypatch.setattr(settings, "SUPABASE_JWT_AUDIENCE", "authenticated")
    monkeypatch.setattr(settings, "SUPABASE_JWT_ISSUER", "https://test.supabase.co/auth/v1")
    init_db_sync()

# ==============================================================================
# TASK B: SQLITE DATA INTEGRITY TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_sqlite_foreign_key_enforcement():
    """Verify SQLite foreign key enforcement strictly prevents orphan records."""
    async with AsyncSessionLocal() as session:
        # Check PRAGMA foreign_keys is 1
        res = await session.execute(text("PRAGMA foreign_keys;"))
        fk_status = res.scalar()
        assert fk_status == 1, "PRAGMA foreign_keys must be enabled (1)"

        # Attempt to insert an episode with non-existent project_id
        orphan_ep = EpisodeModel(
            id=str(uuid.uuid4()),
            project_id="non_existent_project_id_12345",
            user_id="test_user",
            title="Orphan Episode"
        )
        session.add(orphan_ep)
        with pytest.raises(IntegrityError):
            await session.commit()
        await session.rollback()

@pytest.mark.asyncio
async def test_sqlite_cascade_delete():
    """Verify deleting a Project automatically cascades and deletes child Episodes and Chapters."""
    async with AsyncSessionLocal() as session:
        proj_id = str(uuid.uuid4())
        ep_id = str(uuid.uuid4())
        ch_id = str(uuid.uuid4())

        proj = ProjectModel(id=proj_id, user_id="user_cascade", title="Cascade Project")
        ep = EpisodeModel(id=ep_id, project_id=proj_id, user_id="user_cascade", title="Cascade Episode")
        ch = ChapterModel(id=ch_id, episode_id=ep_id, user_id="user_cascade", chapter_order=1, title="Cascade Chapter")

        session.add_all([proj, ep, ch])
        await session.commit()

        # Delete Project
        await session.delete(proj)
        await session.commit()

        # Check Episode and Chapter are gone
        ep_check = await session.execute(select(EpisodeModel).where(EpisodeModel.id == ep_id))
        assert ep_check.scalar_one_or_none() is None, "Child episode must be cascade deleted"

        ch_check = await session.execute(select(ChapterModel).where(ChapterModel.id == ch_id))
        assert ch_check.scalar_one_or_none() is None, "Child chapter must be cascade deleted"

# ==============================================================================
# TASK C: JWT SECURITY TESTS
# ==============================================================================

def test_jwt_valid_token():
    client = TestClient(app)
    headers = get_auth_headers("user_valid")
    resp = client.get("/api/v1/projects", headers=headers)
    assert resp.status_code == 200

def test_jwt_expired_token():
    client = TestClient(app)
    now = int(time.time())
    token = create_jwt({
        "sub": "user_exp",
        "aud": "authenticated",
        "exp": now - 3600,
        "iss": "https://test.supabase.co/auth/v1"
    })
    resp = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert "expired" in resp.json()["detail"].lower()

def test_jwt_invalid_signature():
    client = TestClient(app)
    now = int(time.time())
    token = create_jwt({
        "sub": "user_bad_sig",
        "aud": "authenticated",
        "exp": now + 3600,
        "iss": "https://test.supabase.co/auth/v1"
    }, secret="wrong_signature_secret_32_chars_long!!")
    resp = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert "signature verification failed" in resp.json()["detail"].lower()

def test_jwt_invalid_audience():
    client = TestClient(app)
    now = int(time.time())
    token = create_jwt({
        "sub": "user_bad_aud",
        "aud": "wrong_audience_unauthorized",
        "exp": now + 3600,
        "iss": "https://test.supabase.co/auth/v1"
    })
    resp = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert "audience" in resp.json()["detail"].lower()

def test_jwt_invalid_issuer():
    client = TestClient(app)
    now = int(time.time())
    token = create_jwt({
        "sub": "user_bad_iss",
        "aud": "authenticated",
        "exp": now + 3600,
        "iss": "https://attacker.supabase.co/auth/v1"
    })
    resp = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert "issuer" in resp.json()["detail"].lower()

def test_jwt_algorithm_none_rejected():
    client = TestClient(app)
    now = int(time.time())
    # Hand-craft an alg: none token
    header = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0"
    payload = "eyJzdWIiOiJhdHRhY2tlciIsImF1ZCI6ImF1dGhlbnRpY2F0ZWQiLCJleHAiOjIwMDAwMDAwMDB9"
    token = f"{header}.{payload}."
    resp = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401

# ==============================================================================
# TASK D: SECURE AUDIO ENDPOINT TESTS
# ==============================================================================

def test_audio_endpoint_security_and_authorization(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "AUDIO_STORAGE_PATH", str(tmp_path))
    client = TestClient(app)

    # 1. Synthesize audio as User A
    headers_a = get_auth_headers("user_alpha")
    synth_resp = client.post("/api/v1/tts/synthesize", json={
        "text": "Xin chào đây là kiểm tra bảo mật âm thanh.",
        "voice": "vi-VN-NamMinhNeural"
    }, headers=headers_a)
    assert synth_resp.status_code == 200
    audio_data = synth_resp.json()
    filename = f"{audio_data['audio_id']}.mp3"

    # 2. User A downloads their own audio -> 200 OK
    get_a = client.get(f"/api/v1/tts/audio/{filename}", headers=headers_a)
    assert get_a.status_code == 200
    assert len(get_a.content) > 0

    # 3. User A downloads audio via ?token= query parameter -> 200 OK
    token_a = headers_a["Authorization"].split(" ")[1]
    get_a_token = client.get(f"/api/v1/tts/audio/{filename}?token={token_a}")
    assert get_a_token.status_code == 200
    assert len(get_a_token.content) > 0

    # 4. User B attempts to download User A's audio -> 403 Forbidden
    headers_b = get_auth_headers("user_bravo")
    get_b = client.get(f"/api/v1/tts/audio/{filename}", headers=headers_b)
    assert get_b.status_code == 403
    assert "access denied" in get_b.json()["detail"].lower()

    # 5. Unauthenticated download (no token) -> 401 Unauthorized
    get_anon = client.get(f"/api/v1/tts/audio/{filename}")
    assert get_anon.status_code == 401

    # 6. Path traversal attack attempt -> 400 Bad Request
    traversal_resp = client.get(f"/api/v1/tts/audio/../../etc/passwd", headers=headers_a)
    assert traversal_resp.status_code in (400, 404)

    # 7. Non-existent audio file -> 404 Not Found
    notfound_resp = client.get(f"/api/v1/tts/audio/{uuid.uuid4()}.mp3", headers=headers_a)
    assert notfound_resp.status_code == 404

# ==============================================================================
# TASK E: CORS TESTS
# ==============================================================================

def test_cors_cloudflare_pages_regex():
    client = TestClient(app)

    # 1. Valid Cloudflare Pages origin
    resp = client.get(
        "/api/v1/script/genres",
        headers={"Origin": "https://my-preview-app-123.pages.dev"}
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "https://my-preview-app-123.pages.dev"

    # 2. Another valid alphanumeric Pages origin
    resp2 = client.get(
        "/api/v1/script/genres",
        headers={"Origin": "https://zero-budget-studio.pages.dev"}
    )
    assert resp2.status_code == 200
    assert resp2.headers.get("access-control-allow-origin") == "https://zero-budget-studio.pages.dev"

    # 3. Disallowed origin (phishing or malicious)
    resp3 = client.get(
        "/api/v1/script/genres",
        headers={"Origin": "https://maliciouspages.dev"}
    )
    assert resp3.status_code == 200
    assert resp3.headers.get("access-control-allow-origin") is None

    # 4. Preflight OPTIONS request
    opt_resp = client.options(
        "/api/v1/projects",
        headers={
            "Origin": "https://my-studio.pages.dev",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
    )
    assert opt_resp.status_code == 200
    assert opt_resp.headers.get("access-control-allow-origin") == "https://my-studio.pages.dev"
    assert "POST" in opt_resp.headers.get("access-control-allow-methods", "")

# ==============================================================================
# TASK F: CHAPTER API TESTS (PUT & DELETE)
# ==============================================================================

def test_chapter_crud_api_and_tenant_isolation():
    client = TestClient(app)
    headers_a = get_auth_headers("user_alpha")
    headers_b = get_auth_headers("user_bravo")

    # 1. User A creates project and episode
    p_resp = client.post("/api/v1/projects", json={"title": "Project A", "video_type": "long-form"}, headers=headers_a)
    assert p_resp.status_code == 201
    p_id = p_resp.json()["id"]

    e_resp = client.post(f"/api/v1/projects/{p_id}/episodes", json={"title": "Episode 1"}, headers=headers_a)
    assert e_resp.status_code == 201
    e_id = e_resp.json()["id"]

    # 2. User A creates chapter
    ch_create = client.post(f"/api/v1/episodes/{e_id}/chapters", json={
        "title": "Chương 1: Mở Đầu",
        "chapter_order": 1,
        "summary": "Tóm tắt chương 1",
        "duration_seconds": 120.0
    }, headers=headers_a)
    assert ch_create.status_code == 201
    ch_id = ch_create.json()["id"]

    # 3. User A updates chapter (PUT)
    ch_update = client.put(f"/api/v1/episodes/{e_id}/chapters/{ch_id}", json={
        "title": "Chương 1: Mở Đầu Cải Tiến",
        "duration_seconds": 150.0
    }, headers=headers_a)
    assert ch_update.status_code == 200
    assert ch_update.json()["title"] == "Chương 1: Mở Đầu Cải Tiến"
    assert ch_update.json()["duration_seconds"] == 150.0

    # 4. User B attempts to update User A's chapter -> 404 Not Found (tenant isolated)
    b_update = client.put(f"/api/v1/episodes/{e_id}/chapters/{ch_id}", json={
        "title": "Hacked Title"
    }, headers=headers_b)
    assert b_update.status_code == 404

    # 5. User B attempts to delete User A's chapter -> 404 Not Found
    b_del = client.delete(f"/api/v1/episodes/{e_id}/chapters/{ch_id}", headers=headers_b)
    assert b_del.status_code == 404

    # 6. User A deletes chapter (DELETE) -> 204 No Content
    a_del = client.delete(f"/api/v1/episodes/{e_id}/chapters/{ch_id}", headers=headers_a)
    assert a_del.status_code == 204

    # 7. Check chapter is deleted
    list_ch = client.get(f"/api/v1/episodes/{e_id}/chapters", headers=headers_a)
    assert list_ch.status_code == 200
    assert len(list_ch.json()) == 0
