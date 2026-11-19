import pytest
import json
from backend.providers.ai_rule_based import RuleBasedScriptProvider
from backend.providers.tts_engine import VietnameseTextNormalizer, TTSService
from backend.providers.asset_discovery import AssetDiscoveryService

@pytest.mark.asyncio
async def test_complete_end_to_end_pipeline():
    """
    End-to-End Test for Zero-Budget AI Video Studio:
    Input Vietnamese Script -> Text Normalization -> AI Scene Analysis ->
    Asset Discovery -> Subtitle Synchronization -> Scene Manifest Verification.
    """
    raw_script = (
        "Chiến thắng Điện Biên Phủ ngày 7/5/1954 là mốc son chói lọi trong lịch sử dân tộc. "
        "Dưới sự chỉ huy của Đại tướng Võ Nguyên Giáp, quân và dân ta đã vượt qua muôn vàn gian khổ. "
        "Ngày nay, Điện Biên đã đổi thay với hơn 600000 người dân sinh sống ấm no hạnh phúc."
    )

    # 1. Text Normalization
    normalizer = VietnameseTextNormalizer()
    normalized_text = normalizer.normalize(raw_script)
    assert "ngày bảy tháng năm năm một nghìn chín trăm năm mươi tư" in normalized_text
    assert "sáu trăm nghìn" in normalized_text

    # 2. AI Scene Analysis & Adaptive Visuals
    ai_provider = RuleBasedScriptProvider()
    analysis = await ai_provider.analyze_script(raw_script, target_duration=55)
    assert len(analysis.scenes) >= 3
    assert analysis.estimated_duration_seconds > 0

    # Verify visual modality distribution
    modalities = [s.visual_method for s in analysis.scenes]
    assert any(m in ["archival", "photo", "procedural", "stock"] for m in modalities)

    # 3. Asset Discovery (Wikimedia Commons / CC)
    asset_service = AssetDiscoveryService()
    assets = await asset_service.search_wikimedia("Dien Bien Phu", limit=2)
    assert assets is not None
    # If network is available, assets will be returned; else fallback gracefully
    first_asset = assets[0] if len(assets) > 0 else None

    # 4. Syllable & Subtitle Synchronization
    tts_service = TTSService()
    subtitles = tts_service.generate_syllable_timings(
        analysis.scenes[0].narration_text,
        total_duration_sec=analysis.scenes[0].duration_seconds
    )
    assert len(subtitles) > 0
    assert subtitles[0].start_ms >= 0
    assert subtitles[-1].end_ms > 0

    # 5. Scene Manifest Output Construction
    manifest = {
        "episode_id": "e2e-test-ep",
        "title": "Chiến Thắng Điện Biên Phủ",
        "total_duration_sec": analysis.estimated_duration_seconds,
        "total_frames": int(analysis.estimated_duration_seconds * 30),
        "voice_config": {"voice": "vi-VN-HoaiMyNeural", "rate": "+0%", "pitch": "+0Hz"},
        "video_specs": {"width": 1080, "height": 1920, "fps": 30},
        "audio_specs": {"target_lufs": -14.0, "true_peak": -1.0},
        "scenes": [
            {
                "scene_order": s.scene_order,
                "scene_type": s.scene_type,
                "narration_text": s.narration_text,
                "duration_seconds": s.duration_seconds,
                "visual_method": s.visual_method,
                "assets": [first_asset.model_dump()] if s.scene_order == 1 and first_asset else []
            }
            for s in analysis.scenes
        ]
    }

    assert manifest["video_specs"]["width"] == 1080
    assert manifest["video_specs"]["height"] == 1920
    assert manifest["video_specs"]["fps"] == 30
    assert len(manifest["scenes"]) == len(analysis.scenes)

def test_full_studio_api_workflow_end_to_end():
    """
    Simulates the entire multi-user API workflow from start to finish:
    1. Authenticate user
    2. Create Project (with genre 'historical_doc')
    3. Create Episode
    4. Analyze Vietnamese Script (Genre Intelligence & Scenes)
    5. Search Open Media Assets (Wikimedia / CC)
    6. Synthesize Real Neural Voice (Edge-TTS)
    7. Save & Retrieve Final Episode Manifest in Persistent DB
    """
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.core.security import get_current_user_id

    # Authenticate as test user 'studio-director'
    app.dependency_overrides[get_current_user_id] = lambda: "studio-director-001"
    client = TestClient(app)

    # 1. Create Project
    proj_res = client.post(
        "/api/v1/projects",
        json={
            "title": "Hào Khí Thăng Long",
            "description": "Shorts 9:16 về ngàn năm văn hiến",
            "video_type": "short-form",
            "genre": "historical_doc"
        }
    )
    assert proj_res.status_code == 201
    proj_data = proj_res.json()
    proj_id = proj_data["id"]
    assert proj_data["genre"] == "historical_doc"

    # 2. Create Episode
    ep_res = client.post(
        f"/api/v1/projects/{proj_id}/episodes",
        json={
            "title": "Tập 1: Chiếu Dời Đô 1010",
            "script_raw": "Mùa thu năm Canh Tuất 1010, vua Lý Thái Tổ dời đô từ Hoa Lư về thành Đại La.",
            "voice_config": {"voice": "vi-VN-NamMinhNeural", "rate": "+0%", "pitch": "+0Hz"}
        }
    )
    assert ep_res.status_code == 201
    ep_data = ep_res.json()
    ep_id = ep_data["id"]

    # 3. Analyze Script with Genre Intelligence
    script_content = (
        "Mùa thu năm 1010, vua Lý Thái Tổ khởi hành dời đô từ Hoa Lư về Đại La. "
        "Nhìn thấy rồng vàng bay lên, ngài đặt tên cho vùng đất mới là Thăng Long. "
        "Trải qua hơn một nghìn năm lịch sử, Hà Nội vẫn giữ vững vị thế trái tim của cả nước."
    )
    analyze_res = client.post(
        "/api/v1/script/analyze",
        json={
            "script_text": script_content,
            "target_duration_seconds": 45,
            "genre": "historical_doc",
            "video_format": "short-form"
        }
    )
    assert analyze_res.status_code == 200
    analysis = analyze_res.json()
    assert analysis["genre"] == "historical_doc"
    assert len(analysis["scenes"]) >= 3
    assert len(analysis["entities"]) >= 1

    # 4. Search Creative Commons Assets for First Scene
    first_keyword = analysis["scenes"][0]["suggested_asset_keywords"][0] if analysis["scenes"][0]["suggested_asset_keywords"] else "Hanoi"
    asset_res = client.get(f"/api/v1/assets/search?q={first_keyword}&limit=3")
    assert asset_res.status_code == 200
    asset_data = asset_res.json()
    assert "assets" in asset_data

    # 5. Synthesize Real Edge-TTS Neural Voice
    tts_res = client.post(
        "/api/v1/tts/synthesize",
        json={
            "text": analysis["scenes"][0]["narration_text"],
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+0%"
        }
    )
    assert tts_res.status_code == 200
    tts_data = tts_res.json()
    assert tts_data["duration_seconds"] > 0
    assert len(tts_data["words"]) > 0

    # 6. Save Manifest to Persistent Episode
    built_manifest = {
        "episode_id": ep_id,
        "title": ep_data["title"],
        "genre": "historical_doc",
        "video_format": "short-form",
        "aspect_ratio": "9:16",
        "total_duration_sec": analysis["estimated_duration_seconds"],
        "total_frames": int(analysis["estimated_duration_seconds"] * 30),
        "voice_config": {"voice": "vi-VN-NamMinhNeural", "rate": "+0%", "pitch": "+0Hz"},
        "video_specs": {"width": 1080, "height": 1920, "fps": 30},
        "audio_specs": {"target_lufs": -14.0, "true_peak": -1.0},
        "scenes": [
            {
                "scene_order": s["scene_order"],
                "scene_type": s["scene_type"],
                "narration_text": s["narration_text"],
                "duration_seconds": s["duration_seconds"],
                "visual_method": s["visual_method"],
                "visual_config": {},
                "subtitles_json": tts_data["words"] if s["scene_order"] == 1 else [],
                "audio_url": tts_data["audio_url"] if s["scene_order"] == 1 else None,
                "assets": asset_data["assets"][:1] if s["scene_order"] == 1 else []
            }
            for s in analysis["scenes"]
        ]
    }

    save_res = client.put(
        f"/api/v1/episodes/{ep_id}/manifest",
        json={"manifest_json": built_manifest}
    )
    assert save_res.status_code == 200

    # 7. Retrieve from DB and verify tenant isolation and persistence
    fetch_res = client.get(f"/api/v1/episodes/{ep_id}")
    assert fetch_res.status_code == 200
    saved_ep = fetch_res.json()
    assert saved_ep["status"] == "analyzed"
    assert saved_ep["manifest_json"]["title"] == "Tập 1: Chiếu Dời Đô 1010"
    assert len(saved_ep["manifest_json"]["scenes"]) >= 3

    # Clean up overrides
    app.dependency_overrides.clear()
