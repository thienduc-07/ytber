import pytest
from backend.providers.ai_rule_based import RuleBasedScriptProvider, count_vietnamese_syllables
from backend.providers.ai_groq import GroqScriptProvider

def test_count_vietnamese_syllables():
    text = "74 người lính đã đánh sập một cây cầu sắt chỉ bằng cách bước đều."
    count = count_vietnamese_syllables(text)
    assert count == 15

    # Multi-clause with punctuation
    text2 = "Ngày 12 tháng 04 năm 1831, tại Manchester, điều kỳ lạ đã xảy ra!"
    assert count_vietnamese_syllables(text2) == 14

@pytest.mark.asyncio
async def test_rule_based_script_analysis():
    provider = RuleBasedScriptProvider()
    script = (
        "74 người lính đã đánh sập một cây cầu sắt chỉ bằng cách bước đều. "
        "Năm 1831, tại thành phố Manchester, cây cầu Broughton được xây dựng rất kiên cố. "
        "Khi đội quân đi qua, họ bước đều theo nhịp trống dõng dạc. "
        "Tần số bước chân trùng khớp với tần số dao động tự nhiên của cây cầu. "
        "Hiện tượng cộng hưởng cơ học đã xé toạc các chốt neo sắt trong tích tắc. "
        "Sau thảm họa, quân đội Anh ra lệnh: cấm bước đều khi qua cầu!"
    )
    
    result = await provider.analyze_script(script, target_duration=60, genre="historical_doc")
    
    assert "rule-based" in result.ai_provider_used
    assert len(result.scenes) >= 5
    assert len(result.entities) >= 1
    
    # Check that durations are reasonable
    for scene in result.scenes:
        assert 3.0 <= scene.duration_seconds <= 15.0
        assert len(scene.narration_text) > 0
        assert len(scene.suggested_asset_keywords) > 0

@pytest.mark.asyncio
async def test_groq_fallback_when_unconfigured():
    # Pass empty or invalid key to verify seamless fallback
    provider = GroqScriptProvider(api_key="")
    script = "Khoa học vũ trụ luôn ẩn chứa những bí mật bất ngờ. Trái đất quay quanh mặt trời."
    
    result = await provider.analyze_script(script, target_duration=30)
    assert result is not None
    assert len(result.scenes) >= 1
    assert "rule-based" in result.ai_provider_used

@pytest.mark.asyncio
async def test_horror_genre_specialization():
    provider = RuleBasedScriptProvider()
    horror_script = (
        "Căn nhà cổ bỏ hoang ở cuối làng luôn phát ra những tiếng thì thầm lúc nửa đêm. "
        "Người ta đồn rằng năm 1945, một gia đình đã biến mất không dấu vết tại đây. "
        "Càng tiến lại gần, không khí càng lạnh buốt đến thấu xương. "
        "Bất thình lình, cánh cửa gỗ tự động mở toang trong tiếng gió rít rùng rợn!"
    )
    res = await provider.analyze_script(horror_script, genre="horror")
    assert res.genre == "horror"
    assert res.aspect_ratio == "9:16"
    assert len(res.scenes) >= 3
    # Verify horror sound design cues (drone, impacts, silence)
    all_sfx = [cue.sfx_type for s in res.scenes for cue in s.sound_design]
    assert any(sfx in ["drone", "impact", "ambience", "silence"] for sfx in all_sfx)

@pytest.mark.asyncio
async def test_long_form_chapter_planning():
    provider = RuleBasedScriptProvider()
    long_script = (
        "Chương một mở ra toàn cảnh cuộc cách mạng công nghiệp thế kỷ mười chín. "
        "Các nhà máy mọc lên như nấm dọc theo các con sông lớn tại châu Âu. "
        "Giai cấp công nhân phải đối mặt với điều kiện lao động vô cùng khắc nghiệt. "
        "Những phát minh máy hơi nước đã thay đổi hoàn toàn năng suất sản xuất toàn cầu. "
        "Bước sang giai đoạn hai, thương mại quốc tế phát triển với tốc độ chóng mặt. "
        "Các cường quốc tranh giành thuộc địa và tài nguyên trên khắp các châu lục. "
        "Kết thúc thế kỷ, thế giới bước vào kỷ nguyên hiện đại với những bài học sâu sắc."
    )
    res = await provider.analyze_script(long_script, genre="historical_doc", video_format="long-form")
    assert res.video_format == "long-form"
    assert res.aspect_ratio == "16:9"
    assert len(res.chapters) >= 2
    for ch in res.chapters:
        assert ch.chapter_order >= 1
        assert ch.estimated_duration_seconds > 0
        assert len(ch.scenes) > 0
