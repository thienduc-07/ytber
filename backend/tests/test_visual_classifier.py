import pytest
from backend.providers.visual_classifier import AnimatedStyleValidator

def test_photographic_metadata_rejection():
    """
    Verifies that real photographs, press photos, stock photos, and camera shots
    are strictly rejected by the Animated Style Compliance layer.
    """
    # 1. Real news photo
    ok, reason, style = AnimatedStyleValidator.validate_metadata(
        title="Anand Sharma press photograph at ASEAN summit",
        description="Official photo taken with Canon EOS 5D Mark IV",
        source_url="https://example.com/photos/summit_press.jpg"
    )
    assert ok is False
    assert "photographic marker" in reason.lower()
    assert style == "photograph"

    # 2. Stock photography
    ok, reason, style = AnimatedStyleValidator.validate_metadata(
        title="Stock photo of modern container ship moored at terminal",
        description="High resolution stock photo for commercial use",
        source_url="https://example.com/stock-photos/ship.jpg"
    )
    assert ok is False
    assert "photographic marker" in reason.lower()

    # 3. Daguerreotype / vintage photograph
    ok, reason, style = AnimatedStyleValidator.validate_metadata(
        title="1854 daguerreotype photograph of general",
        description="Original daguerreotype from national archives",
        source_url="https://example.com/daguerreotype.jpg"
    )
    assert ok is False

def test_animated_illustration_metadata_acceptance():
    """
    Verifies that 2D cartoons, vector graphics, clipart, and stylized illustrations
    are accepted and categorized with appropriate visual styles.
    """
    # 1. 2D Cartoon character
    ok, reason, style = AnimatedStyleValidator.validate_metadata(
        title="Vietnamese soldier 2D cartoon character illustration",
        description="Stylized vector drawing with bold outlines",
        source_url="https://example.com/vector/soldier_cartoon.svg"
    )
    assert ok is True
    assert style == "2d_cartoon"

    # 2. Vector Infographic
    ok, reason, style = AnimatedStyleValidator.validate_metadata(
        title="Economic growth infographic vector diagram",
        description="Flat design animated bar chart and metrics icon",
        source_url="https://example.com/infographics/chart.png"
    )
    assert ok is True
    assert style == "infographic_vector"

    # 3. Stylized artwork
    ok, reason, style = AnimatedStyleValidator.validate_metadata(
        title="Stylized historical battle reconstruction artwork",
        description="Digital painting and illustrated map of Điện Biên Phủ",
        source_url="https://example.com/art/reconstruction.png"
    )
    assert ok is True
    assert style in ("stylized_illustration", "vector_illustration")

def test_semantic_relevance_validation():
    """
    Verifies Layer 1: Semantic Relevance Validation between scene description
    and candidate asset keywords.
    """
    scene_desc = "Đoàn chiến sĩ kéo pháo qua đèo dốc hiểm trở trong đêm"

    # High match
    ok, score, msg = AnimatedStyleValidator.validate_scene_relevance(
        scene_description=scene_desc,
        asset_title="Chiến sĩ kéo pháo hoạt hình",
        asset_keywords=["chiến sĩ", "kéo pháo", "đèo dốc", "hoạt họa"]
    )
    assert ok is True
    assert score > 0.3

    # Irrelevant asset
    ok_bad, score_bad, _ = AnimatedStyleValidator.validate_scene_relevance(
        scene_description=scene_desc,
        asset_title="Bãi biển nhiệt đới mùa hè",
        asset_keywords=["beach", "summer", "coconut", "resort"]
    )
    assert ok_bad is False
    assert score_bad < 0.2
