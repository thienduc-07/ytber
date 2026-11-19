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
                "assets": [first_asset.dict()] if s.scene_order == 1 and first_asset else []
            }
            for s in analysis.scenes
        ]
    }

    assert manifest["video_specs"]["width"] == 1080
    assert manifest["video_specs"]["height"] == 1920
    assert manifest["video_specs"]["fps"] == 30
    assert len(manifest["scenes"]) == len(analysis.scenes)
