import pytest
from backend.providers.tts_engine import VietnameseTextNormalizer, TTSService, number_to_vietnamese_words
from backend.providers.asset_discovery import AssetDiscoveryService

def test_number_to_vietnamese_words():
    assert number_to_vietnamese_words(0) == "không"
    assert number_to_vietnamese_words(7) == "bảy"
    assert number_to_vietnamese_words(10) == "mười"
    assert number_to_vietnamese_words(15) == "mười lăm"
    assert number_to_vietnamese_words(21) == "hai mươi mốt"
    assert number_to_vietnamese_words(74) == "bảy mươi tư"
    assert number_to_vietnamese_words(105) == "một trăm linh năm"
    assert number_to_vietnamese_words(1831) == "một nghìn tám trăm ba mươi mốt"

def test_vietnamese_text_normalizer():
    norm = VietnameseTextNormalizer()
    
    # 1. Number normalization
    raw1 = "74 người lính đã qua cầu năm 1831."
    n1 = norm.normalize(raw1)
    assert "bảy mươi tư người lính" in n1
    assert "một nghìn tám trăm ba mươi mốt" in n1
    
    # 2. Date normalization
    raw2 = "Ngày 12/04/1831 thảm họa xảy ra."
    n2 = norm.normalize(raw2)
    assert "ngày mười hai tháng tư năm một nghìn tám trăm ba mươi mốt" in n2.lower()
    
    # 3. Loan word normalization
    raw3 = "Hãy render video shorts với 30 fps."
    n3 = norm.normalize(raw3)
    assert "ren đơ" in n3
    assert "vi đê ô ngắn" in n3
    assert "khung hình trên giây" in n3

@pytest.mark.asyncio
async def test_tts_syllable_timings():
    service = TTSService()
    text = "74 người lính bước đều."
    result = await service.synthesize(text)
    
    assert result.duration_seconds >= 3.0
    assert len(result.words) > 0
    
    # Check monotonic timestamps
    last_end = 0
    for w in result.words:
        assert w.start_ms >= last_end
        assert w.end_ms > w.start_ms
        last_end = w.end_ms

@pytest.mark.asyncio
async def test_asset_discovery_wikimedia():
    service = AssetDiscoveryService()
    # Search Wikimedia Commons for public domain bridge
    assets = await service.search_wikimedia("Broughton bridge", limit=3)
    # Even if offline/mocked, verify return type
    assert isinstance(assets, list)
    if assets:
        assert assets[0].media_type == "image"
        assert len(assets[0].preview_url) > 0
        assert len(assets[0].license_type) > 0
        assert len(assets[0].attribution_text) > 0
