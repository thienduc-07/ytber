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
    
    result = await provider.analyze_script(script, target_duration=60)
    
    assert result.ai_provider_used == "rule-based-nlp-offline"
    assert len(result.scenes) >= 5
    assert result.scenes[0].scene_type == "hook"
    assert result.scenes[0].visual_method == "parallax"
    
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
    assert result.ai_provider_used == "rule-based-nlp-offline"
