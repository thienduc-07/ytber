import os
import time
import pytest
import jwt
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.config import settings
from backend.core.database import init_db_sync

TEST_SECRET = "test_director_secret_min_32_characters_long!!"

def create_jwt(payload: dict, secret: str = TEST_SECRET, algorithm: str = "HS256") -> str:
    return jwt.encode(payload, secret, algorithm=algorithm)

def get_auth_headers(user_id: str = "director_test_user") -> dict:
    now = int(time.time())
    token = create_jwt({
        "sub": user_id,
        "aud": "authenticated",
        "exp": now + 3600,
        "iat": now,
        "iss": "https://test.supabase.co/auth/v1"
    }, secret=TEST_SECRET)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", TEST_SECRET)
    monkeypatch.setattr(settings, "SUPABASE_JWT_AUDIENCE", "authenticated")
    monkeypatch.setattr(settings, "SUPABASE_JWT_ISSUER", "https://test.supabase.co/auth/v1")
    monkeypatch.setattr(settings, "AUDIO_STORAGE_PATH", str(tmp_path / "audio"))
    monkeypatch.setattr(settings, "ASSET_STORAGE_PATH", str(tmp_path / "assets"))
    init_db_sync()

def test_director_blueprint_endpoint():
    client = TestClient(app)
    script = (
        "Bạn có biết rằng trận quyết chiến tại thung lũng Điện Biên Phủ năm 1954 đã thay đổi cục diện thế giới? "
        "Dưới sự chỉ huy kiệt xuất của Đại tướng Võ Nguyên Giáp, toàn quân ta đã vượt muôn vàn gian khó, kéo pháo qua núi. "
        "Chiều ngày 7 tháng 5 năm 1954, lá cờ Quyết chiến Quyết thắng tung bay trên nóc hầm De Castries, khẳng định mốc son rực rỡ."
    )
    resp = client.post("/api/v1/director/blueprint", json={
        "script_text": script,
        "genre": "historical_doc",
        "video_format": "short-form"
    })
    assert resp.status_code == 200
    data = resp.json()

    assert "character_bible" in data
    assert "environment_bible" in data
    assert "dramatic_arc" in data
    assert "scenes" in data
    assert len(data["scenes"]) >= 3

    # Check 5-part structure
    first_scene = data["scenes"][0]
    assert first_scene["scene_type"] == "hook"
    assert "visual_query" in first_scene
    assert "ambient_profile" in first_scene
    assert "sfx_cues" in first_scene

def test_zero_touch_generate_movie_endpoint():
    client = TestClient(app)
    headers = get_auth_headers("producer_alpha")

    script = (
        "Khám phá sự phát triển vũ bão của trí tuệ nhân tạo trong kỷ nguyên số. "
        "Các mô hình mạng nơ-ron học sâu đang mở ra bước ngoặt to lớn cho nhân loại. "
        "Hãy cùng đăng ký kênh để đồng hành cùng tương lai công nghệ đột phá!"
    )

    resp = client.post("/api/v1/director/generate-movie", json={
        "script_text": script,
        "genre": "technology",
        "video_format": "short-form",
        "voice": "vi-VN-NamMinhNeural"
    }, headers=headers)

    assert resp.status_code == 200
    manifest = resp.json()

    # Verify complete SceneManifest
    assert "episode_id" in manifest
    assert manifest["total_duration_sec"] > 0
    assert manifest["total_frames"] > 0
    assert manifest["aspect_ratio"] == "9:16"
    assert manifest["video_specs"]["fps"] == 30

    # 4-Bus Audio Specs
    assert "audio_specs" in manifest
    assert "buses" in manifest["audio_specs"]
    assert "Voiceover" in manifest["audio_specs"]["buses"]
    assert "ActionSFX" in manifest["audio_specs"]["buses"]

    # Verify each scene
    scenes = manifest["scenes"]
    assert len(scenes) >= 3
    for s in scenes:
        assert s["duration_seconds"] >= 3.0
        assert s["audio_url"] is not None
        assert "subtitles_json" in s
        assert "ambient_layers" in s
        assert "sound_design" in s
        assert s["start_frame"] < s["end_frame"]
