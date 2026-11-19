import pytest
from backend.providers.director_engine import AIDirectorEngine
from backend.providers.ai_rule_based import RuleBasedScriptProvider

@pytest.fixture
def director():
    return AIDirectorEngine()

@pytest.fixture
def script_provider():
    return RuleBasedScriptProvider()

def test_director_semantic_analysis_generalization(director):
    """
    Verifies that the AI Director independently analyzes semantic context,
    emotional tone, audience, and narrative structure across diverse topics.
    """
    # 1. Historical Topic
    hist_text = "Chiến thắng Điện Biên Phủ năm 1954 lừng lẫy năm châu chấn động địa cầu. Từng đoàn quân kéo pháo vượt qua đèo dốc hiểm trở."
    hist_sem = director.analyze_topic_semantics(hist_text)
    assert hist_sem.topic_category == "historical_doc"
    assert "Chiến tranh Đông Dương" in hist_sem.context_era or "Lịch sử" in hist_sem.context_era
    assert "Hào hùng" in hist_sem.emotional_tone

    # 2. Economic Topic
    econ_text = "Tỷ lệ lạm phát và lãi suất ngân hàng trung ương tiếp tục biến động mạnh tác động đến thị trường tài chính và tăng trưởng GDP."
    econ_sem = director.analyze_topic_semantics(econ_text)
    assert econ_sem.topic_category == "economics"
    assert "Kinh tế" in econ_sem.context_era
    assert "Sắc bén" in econ_sem.emotional_tone

    # 3. Technology Topic
    tech_text = "Mạng nơ-ron sâu và trí tuệ nhân tạo đột phá trong lĩnh vực chế tạo chip vi mạch bán dẫn và robot tự hành."
    tech_sem = director.analyze_topic_semantics(tech_text)
    assert tech_sem.topic_category == "technology"
    assert "Trí tuệ Nhân tạo" in tech_sem.context_era

    # 4. Science Topic
    sci_text = "Hệ mặt trời và các hành tinh quay quanh quỹ đạo dưới lực hấp dẫn kỳ vĩ của vũ trụ bao la."
    sci_sem = director.analyze_topic_semantics(sci_text)
    assert sci_sem.topic_category == "science"
    assert "Không gian" in sci_sem.context_era or "Vũ trụ" in sci_sem.context_era

def test_character_consistency_across_scenes(director):
    """
    Verifies that the character registry maintains consistent identity,
    costume, facial features, and color palette across the entire production.
    """
    hist_text = "Chiến sĩ kéo pháo qua dốc núi. Đại bác gầm vang. Lá cờ tung bay trên nóc hầm."
    characters = director.build_character_registry("historical_doc", hist_text)

    assert "char_soldier_01" in characters
    soldier = characters["char_soldier_01"]
    assert soldier.role == "protagonist"
    assert len(soldier.color_scheme) >= 4
    assert "mũ nan" in soldier.costume_description or "áo trấn thủ" in soldier.costume_description

    # Ensure palette contains military green (#36522D) and star gold (#FFD700)
    assert "#36522D" in soldier.color_scheme
    assert "#FFD700" in soldier.color_scheme

@pytest.mark.asyncio
async def test_17_attribute_production_specification(script_provider):
    """
    Verifies that the scene production plan generated for each scene contains
    the mandatory 17 attributes required by the AI Director specification.
    """
    script = (
        "Chiến thắng Điện Biên Phủ năm 1954 chấn động địa cầu. "
        "Bộ đội ta anh dũng kéo pháo qua đèo dốc hiểm trở trong đêm. "
        "Lá cờ Quyết chiến Quyết thắng tung bay kiêu hãnh trên nóc hầm De Castries."
    )

    result = await script_provider.analyze_script(
        script_text=script,
        genre="historical_doc",
        video_format="short-form"
    )

    assert len(result.scenes) >= 3
    assert result.character_registry is not None
    assert len(result.character_registry) > 0

    for idx, sc in enumerate(result.scenes):
        # 1. Scene ID
        assert sc.scene_id is not None and len(sc.scene_id) > 0
        # 2. Narrative purpose
        assert sc.narrative_purpose is not None and len(sc.narrative_purpose) > 0
        # 3. Narration
        assert sc.narration_text is not None and len(sc.narration_text) > 0
        # 4. Visual description
        assert sc.visual_description is not None and len(sc.visual_description) > 0
        # 5. Environment
        assert sc.environment is not None
        assert sc.environment.setting_name is not None
        assert sc.environment.environment_type is not None
        # 6. Character descriptions
        assert len(sc.character_descriptions) > 0
        # 7. Character poses & actions
        assert len(sc.character_poses) > 0
        # 8. Props
        assert len(sc.props) > 0
        # 9. Camera angle
        assert sc.camera_angle in ["eye_level", "low_angle_heroic", "high_angle_overview", "top_down_map"]
        # 10. Camera movement
        assert sc.camera_movement is not None
        # 11. Animation instructions
        assert sc.animation_instructions is not None
        assert sc.animation_instructions.character_action is not None
        # 12. Lighting
        assert sc.lighting is not None and len(sc.lighting) > 0
        # 13. Color palette
        assert len(sc.color_palette) >= 3
        # 14. Transition
        assert sc.transition is not None
        # 15. Scene duration
        assert sc.duration_seconds > 0
        # 16. Music direction
        assert sc.music_direction is not None and len(sc.music_direction) > 0
        # 17. Sound effects
        assert len(sc.sound_effects) > 0 or len(sc.sound_design) > 0

def test_strict_animated_policy_in_director(director):
    """
    Verifies that the director's visual descriptions and suggested keywords
    strictly enforce 100% animated visual formats (NO photographic requests).
    """
    script = "Khủng hoảng lạm phát toàn cầu năm 2024."
    res = director.analyze_and_direct(script)

    assert res.visual_style_preset == "2d_cartoon"
    for sc in res.scenes:
        # Visual description should mandate cartoon / vector / infographic / 2.5D
        assert any(term in sc.visual_description.lower() for term in ["hoạt họa", "hoạt hình", "đồ họa", "vector", "2.5d", "mô hình"])
        # Check that search keywords are tagged with illustration / vector / cartoon
        for kw in sc.search_keywords:
            assert any(tag in kw.lower() for tag in ["cartoon", "illustration", "vector", "clipart"])
            assert "photograph" not in kw.lower()
            assert "real photo" not in kw.lower()
