"""
Unit tests for AISoundscapeDirector.
Verifies environmental acoustic soundscape generation, action-to-sound synchronization,
and ducking specifications across diverse scenarios.
"""

import pytest
from backend.providers.soundscape_engine import AISoundscapeDirector, SceneSoundscapeSpec


def test_tropical_forest_soundscape():
    """Verifies that tropical forest scene produces cicadas, birds, wind, and leaf footsteps."""
    spec = AISoundscapeDirector.generate_soundscape_for_scene(
        scene_id="scene_001",
        scene_order=1,
        duration_sec=6.0,
        visual_description="Nhân vật hoạt hình bước đi giữa rừng cây nhiệt đới rậm rạp, thảm lá xanh mướt",
        setting_name="Rừng rậm nhiệt đới",
        character_action="walk"
    )

    assert spec.primary_environment == "tropical_forest"
    assert spec.ducking_db == -17.0
    assert spec.voice_priority is True

    # Ambience layer checks
    amb_names = [a.name for a in spec.ambient_layers]
    assert any("ve sầu" in n.lower() or "côn trùng" in n.lower() for n in amb_names)
    assert any("chim rừng" in n.lower() for n in amb_names)
    assert any("gió" in n.lower() for n in amb_names)

    # Action-to-sound sync footsteps check (2.2Hz cadence, ~10-14 footsteps in 6s)
    footstep_events = [e for e in spec.action_sfx_events if e.action_type == "footsteps_leaves"]
    assert len(footstep_events) >= 10
    assert all(e.sync_trigger == "character_walk_step" for e in footstep_events)


def test_mountain_battlefield_soundscape():
    """Verifies battlefield scene produces wind, trench rumble, and artillery SFX."""
    spec = AISoundscapeDirector.generate_soundscape_for_scene(
        scene_id="scene_002",
        scene_order=2,
        duration_sec=5.0,
        visual_description="Chiến sĩ kéo pháo qua đèo cao dốc núi, chiến hào mịt mù",
        setting_name="Đèo Pha Đin Điện Biên",
        character_action="pull_cannon"
    )

    assert spec.primary_environment == "mountain_battlefield"
    assert any("pháo" in e.description.lower() for e in spec.action_sfx_events)


def test_financial_floor_soundscape():
    """Verifies economic/financial soundscape."""
    spec = AISoundscapeDirector.generate_soundscape_for_scene(
        scene_id="scene_003",
        scene_order=3,
        duration_sec=4.0,
        visual_description="Biểu đồ tài chính lạm phát và thị trường vàng tăng vọt",
        setting_name="Sàn giao dịch tài chính",
        character_action="present"
    )

    assert spec.primary_environment == "financial_floor"
    assert any("vàng" in e.description.lower() or "chuông" in e.description.lower() for e in spec.action_sfx_events)


def test_cyber_tech_lab_soundscape():
    """Verifies tech lab soundscape with server hum and data stream."""
    spec = AISoundscapeDirector.generate_soundscape_for_scene(
        scene_id="scene_004",
        scene_order=4,
        duration_sec=5.0,
        visual_description="Phòng thí nghiệm trí tuệ nhân tạo AI và mạng nơ-ron",
        setting_name="Trung tâm siêu máy tính",
        character_action="compute"
    )

    assert spec.primary_environment == "cyber_tech_lab"
    assert any("server" in a.name.lower() or "quạt" in a.name.lower() for a in spec.ambient_layers)


def test_manifest_soundscape_enrichment():
    """Verifies batch enrichment across an entire scene manifest."""
    manifest = {
        "title": "Hành trình xuyên rừng nhiệt đới",
        "scenes": [
            {
                "scene_id": "sc_1",
                "scene_order": 1,
                "duration_seconds": 4.5,
                "visual_description": "Khởi đầu chuyến thám hiểm rừng cây lá kim",
                "environment": {"setting_name": "Rừng cây"},
                "animation_instructions": {"character_action": "walk"}
            },
            {
                "scene_id": "sc_2",
                "scene_order": 2,
                "duration_seconds": 5.0,
                "visual_description": "Robot phân tích dữ liệu lượng tử",
                "environment": {"setting_name": "Phòng nghiên cứu máy tính"},
                "animation_instructions": {"character_action": "idle"}
            }
        ]
    }

    enriched = AISoundscapeDirector.enrich_manifest_soundscapes(manifest)
    scenes = enriched["scenes"]
    assert scenes[0]["music_direction"] == "tropical_forest"
    assert len(scenes[0]["sound_design"]) > 0
    assert scenes[1]["music_direction"] == "cyber_tech_lab"
