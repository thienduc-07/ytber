import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.tests.test_director_router import get_auth_headers

def test_soundscape_presets_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/soundscape/presets")
    assert resp.status_code == 200
    presets = resp.json()
    assert len(presets) >= 8
    preset_ids = [p["id"] for p in presets]
    assert "horror_creepy" in preset_ids
    assert "crime_noir" in preset_ids
    assert "tropical_forest" in preset_ids

def test_soundscape_search_endpoint():
    client = TestClient(app)
    # Search for door creak
    r1 = client.get("/api/v1/soundscape/search?q=cửa")
    assert r1.status_code == 200
    results1 = r1.json()
    assert len(results1) >= 1
    assert any("cửa" in item["name"].lower() or "creak" in item["id"] for item in results1)

    # Search for whoosh
    r2 = client.get("/api/v1/soundscape/search?q=whoosh")
    assert r2.status_code == 200
    results2 = r2.json()
    assert len(results2) >= 1
    assert any("whoosh" in item["id"].lower() for item in results2)

def test_soundscape_detect_endpoint():
    client = TestClient(app)
    payload = {
        "scene_id": "test_sc_01",
        "scene_order": 1,
        "duration_sec": 3.0,
        "visual_description": "Căn nhà hoang cổ kính lúc nửa đêm có bóng ma lướt qua",
        "setting_name": "Nhà hoang",
        "character_action": "walk"
    }
    resp = client.post("/api/v1/soundscape/detect", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["primary_environment"] == "horror_creepy"
    assert data["music_theme"] == "horror_eerie_drone_piano"
    assert len(data["ambient_layers"]) >= 2
    assert len(data["action_sfx_events"]) >= 1

def test_tts_settings_and_voicestudio_status():
    client = TestClient(app)
    r1 = client.get("/api/v1/tts/settings")
    assert r1.status_code == 200
    settings = r1.json()
    assert "voicestudio_url" in settings
    assert "engine_mode" in settings

    r2 = client.get("/api/v1/tts/voicestudio/status")
    assert r2.status_code == 200
    vs = r2.json()
    assert "url" in vs
    assert "install_command" in vs
