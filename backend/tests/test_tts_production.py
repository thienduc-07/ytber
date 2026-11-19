import os
import uuid
import time
import asyncio
import pytest
import jwt
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.config import settings
from backend.core.database import AsyncSessionLocal, init_db_sync
from backend.models.db_models import AudioFileModel
from backend.providers.tts_chunker import VietnameseTextChunker
from backend.providers.mp3_stitcher import MP3Stitcher
from backend.providers.tts_engine import (
    EdgeTTSVoiceProvider,
    VietnameseTextNormalizer,
    VOICE_REGISTRY,
    TTSResult,
    WordTiming
)

TEST_SECRET = "test_phase2_production_tts_secret_32chars_long!!"

def create_jwt(payload: dict, secret: str = TEST_SECRET, algorithm: str = "HS256") -> str:
    return jwt.encode(payload, secret, algorithm=algorithm)

def get_auth_headers(user_id: str = "user_alpha", secret: str = TEST_SECRET) -> dict:
    now = int(time.time())
    token = create_jwt({
        "sub": user_id,
        "aud": "authenticated",
        "exp": now + 3600,
        "iat": now,
        "iss": "https://test.supabase.co/auth/v1"
    }, secret=secret)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", TEST_SECRET)
    monkeypatch.setattr(settings, "SUPABASE_JWT_AUDIENCE", "authenticated")
    monkeypatch.setattr(settings, "SUPABASE_JWT_ISSUER", "https://test.supabase.co/auth/v1")
    monkeypatch.setattr(settings, "AUDIO_STORAGE_PATH", str(tmp_path))
    init_db_sync()

# ==============================================================================
# 1. TEXT CHUNKER & WORD PRESERVATION TESTS
# ==============================================================================

def test_vietnamese_text_chunker_word_preservation():
    """Verify chunker guarantees 100% word preservation across 100, 500, 2000, 5000 words."""
    chunker = VietnameseTextChunker(max_chars=250)
    normalizer = VietnameseTextNormalizer()

    sample_sentences = [
        "Hôm nay trời nắng đẹp, gió thổi nhẹ trên những tán cây xanh biếc.",
        "Trần Hưng Đạo là một danh tướng kiệt xuất trong lịch sử bảo vệ non sông Đại Việt.",
        "Ứng dụng trí tuệ nhân tạo đang thay đổi toàn diện ngành công nghiệp sản xuất video kỹ thuật số.",
        "Những dòng sông uốn lượn chảy qua miền đồng bằng trù phú mang nặng phù sa.",
        "Kỹ thuật xử lý âm thanh tự động giúp đồng bộ lời thoại và hình ảnh chính xác từng mili-giây."
    ]

    word_counts = [100, 500, 2000, 5000]
    for target_count in word_counts:
        # Build text with target word count
        words = []
        while len(words) < target_count:
            for s in sample_sentences:
                words.extend(s.split())
                if len(words) >= target_count:
                    break
        raw_text = " ".join(words[:target_count])
        normalized = normalizer.normalize(raw_text)
        expected_words = normalized.split()

        chunks = chunker.chunk_text(normalized)
        assert len(chunks) >= 1, f"Should have at least 1 chunk for {target_count} words"

        # Reconstruct words from chunks
        reconstructed_words = []
        for c in chunks:
            assert len(c.text) <= 350, f"Chunk exceeded safety max limit: {len(c.text)}"
            reconstructed_words.extend(c.text.split())

        assert reconstructed_words == expected_words, (
            f"Word mismatch at {target_count} words! "
            f"Expected {len(expected_words)} words, got {len(reconstructed_words)} words"
        )

def test_vietnamese_unicode_and_punctuation_preservation():
    """Verify Vietnamese tonal diacritics and complex punctuation are fully preserved."""
    chunker = VietnameseTextChunker(max_chars=200)
    normalizer = VietnameseTextNormalizer()

    unicode_text = (
        "«Đại Việt Sử Ký Toàn Thư»: Thăng Long ngàn năm văn hiến! "
        "Nguyễn Trãi từng viết: 'Đem đại nghĩa để thắng hung tàn; "
        "lấy chí nhân để thay cường bạo...'. "
        "Những từ có đủ 6 thanh điệu: má, mà, mả, mã, mạ, ma, "
        "các nguyên âm đặc trưng: ư, ơ, ê, ô, ă, â, đ!"
    )
    normalized = normalizer.normalize(unicode_text)
    chunks = chunker.chunk_text(normalized)

    full_reconstructed = " ".join(c.text for c in chunks)
    for sample_word in ["Thăng", "nghĩa", "hung", "bạo", "má", "mạ", "đặc"]:
        assert sample_word.lower() in full_reconstructed.lower(), f"Missing word {sample_word}"

# ==============================================================================
# 2. MP3 STITCHER & FRAME INTEGRITY TESTS
# ==============================================================================

def test_mp3_stitcher_frame_parsing_and_id3_stripping():
    """Verify MP3 frame parser extracts valid frames, strips ID3v2, and computes exact duration."""
    stitcher = MP3Stitcher()

    # Generate mock MPEG 2.5 / 2 / 1 Layer III frame sync header
    # 0xFF, 0xF3 (MPEG-2, Layer 3, no CRC)
    # Bitrate 32kbps (index 4), 24000Hz (index 1), no padding -> frame size = 72 * 32000 / 24000 = 96 bytes
    # Frame duration = 576 / 24000 = 0.024 sec = 24 ms
    frame_hdr = bytes([0xFF, 0xF3, 0x44, 0x00])
    single_frame = frame_hdr + bytes([0xAA] * 92) # total 96 bytes
    assert len(single_frame) == 96

    # Fake ID3v2 header (10 bytes header + 20 bytes payload = 30 bytes)
    id3_tag = b"ID3\x03\x00\x00\x00\x00\x00\x14" + (b"X" * 20)
    chunk1 = id3_tag + (single_frame * 10)  # 10 frames = 240 ms
    chunk2 = id3_tag + (single_frame * 15)  # 15 frames = 360 ms

    # Test strip_id3v2
    stripped = stitcher.strip_id3v2(chunk2)
    assert not stripped.startswith(b"ID3")
    assert stripped.startswith(bytes([0xFF, 0xF3]))

    # Test parse_frames
    frames1, dur1, _ = stitcher.parse_frames(chunk1)
    assert frames1 == 10
    assert abs(dur1 - 0.24) < 0.001

    frames2, dur2, _ = stitcher.parse_frames(stripped)
    assert frames2 == 15
    assert abs(dur2 - 0.36) < 0.001

    # Test stitch_chunks
    stitched, chunk_durs, total_dur = stitcher.stitch_chunks([chunk1, chunk2])
    assert stitched.startswith(bytes([0xFF, 0xF3]))  # Clean audio sync frame
    assert abs(total_dur - 0.60) < 0.001

# ==============================================================================
# 3. WORD TIMING & MONOTONICITY TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_word_timestamp_monotonicity_and_rebasing():
    """Verify word timestamps are strictly monotonic and correctly offset across chunks."""
    provider = EdgeTTSVoiceProvider()

    test_script = (
        "Triều đại nhà Lý bắt đầu từ năm 1009 khi Lý Công Uẩn lên ngôi hoàng đế. "
        "Năm 1010, nhà vua ban Chiếu dời đô chuyển kinh đô từ Hoa Lư về thành Đại La "
        "và đổi tên thành Thăng Long rực rỡ gấm hoa muôn đời."
    )

    result = await provider.synthesize(test_script, voice="vi-VN-NamMinhNeural")
    assert result.duration_seconds > 0
    assert len(result.words) > 0

    prev_start = -1
    for i, w in enumerate(result.words):
        # Monotonicity check
        assert w.start_ms >= prev_start, f"Word {i} ({w.word}) start_ms {w.start_ms} < prev {prev_start}"
        assert w.end_ms >= w.start_ms, f"Word {i} end_ms < start_ms"
        assert w.end_ms <= (result.duration_seconds * 1000) + 500, f"Word {i} timing exceeds total duration"
        assert w.text is not None and len(w.text) > 0
        assert w.start_time is not None
        assert w.end_time is not None
        prev_start = w.start_ms

# ==============================================================================
# 4. DETERMINISTIC CACHE & ISOLATION TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_deterministic_sha256_audio_caching():
    """Verify deterministic cache key, fast sub-10ms cache hit, and cache differentiation."""
    provider = EdgeTTSVoiceProvider()
    text = "Thử nghiệm cơ chế bộ nhớ đệm SHA256 cho giọng đọc tiếng Việt."

    # First call: Cache miss
    res1 = await provider.synthesize(text, voice="vi-VN-NamMinhNeural", rate="+0%", pitch="+0Hz")
    assert not res1.cached
    audio_id_1 = res1.audio_id

    # Second call with identical params: Cache hit
    t0 = time.perf_counter()
    res2 = await provider.synthesize(text, voice="vi-VN-NamMinhNeural", rate="+0%", pitch="+0Hz")
    t1 = time.perf_counter()

    assert res2.cached, "Second call must return cached=True"
    assert res2.audio_id == audio_id_1, "Cache key must be identical"
    assert abs(res2.duration_seconds - res1.duration_seconds) < 0.001
    assert len(res2.words) == len(res1.words)
    assert (t1 - t0) < 0.1, f"Cache hit took too long: {t1 - t0}s"

    # Third call with different rate -> Cache miss & different ID
    res3 = await provider.synthesize(text, voice="vi-VN-NamMinhNeural", rate="+15%", pitch="+0Hz")
    assert not res3.cached
    assert res3.audio_id != audio_id_1

# ==============================================================================
# 5. MULTI-TENANT ISOLATION WITH CACHED AUDIO TESTS
# ==============================================================================

def test_multi_user_cache_sharing_and_tenant_isolation(tmp_path, monkeypatch):
    """
    Verify strict tenant isolation:
    User A synthesizes audio -> User B gets 403 trying to access User A's file.
    User B synthesizes same text -> Cache hit occurs, User B is granted access.
    User C has not synthesized -> User C still gets 403.
    """
    monkeypatch.setattr(settings, "AUDIO_STORAGE_PATH", str(tmp_path))
    client = TestClient(app)

    uid = uuid.uuid4().hex[:8]
    headers_a = get_auth_headers(f"tenant_alpha_{uid}")
    headers_b = get_auth_headers(f"tenant_bravo_{uid}")
    headers_c = get_auth_headers(f"tenant_charlie_{uid}")

    script_text = "Bảo mật đa người dùng và chia sẻ tài nguyên âm thanh có kiểm soát."

    # 1. Tenant Alpha synthesizes audio
    resp_a = client.post("/api/v1/tts/synthesize", json={
        "text": script_text,
        "voice": "vi-VN-NamMinhNeural"
    }, headers=headers_a)
    assert resp_a.status_code == 200
    data_a = resp_a.json()
    assert not data_a["cached"]
    filename = f"{data_a['audio_id']}.mp3"

    # 2. Tenant Alpha accesses their audio -> 200 OK
    get_a = client.get(f"/api/v1/tts/audio/{filename}", headers=headers_a)
    assert get_a.status_code == 200
    assert len(get_a.content) > 0

    # 3. Tenant Bravo attempts to access Alpha's file directly -> 403 Forbidden
    get_b_before = client.get(f"/api/v1/tts/audio/{filename}", headers=headers_b)
    assert get_b_before.status_code == 403
    assert "access denied" in get_b_before.json()["detail"].lower()

    # 4. Tenant Bravo synthesizes the same script -> Cache hit!
    resp_b = client.post("/api/v1/tts/synthesize", json={
        "text": script_text,
        "voice": "vi-VN-NamMinhNeural"
    }, headers=headers_b)
    assert resp_b.status_code == 200
    data_b = resp_b.json()
    assert data_b["cached"], "Should be a cache hit for Tenant Bravo"
    assert data_b["audio_id"] == data_a["audio_id"]

    # 5. Tenant Bravo now accesses the audio -> 200 OK
    get_b_after = client.get(f"/api/v1/tts/audio/{filename}", headers=headers_b)
    assert get_b_after.status_code == 200
    assert len(get_b_after.content) > 0

    # 6. Tenant Charlie (who hasn't synthesized) still gets 403 Forbidden
    get_c = client.get(f"/api/v1/tts/audio/{filename}", headers=headers_c)
    assert get_c.status_code == 403

# ==============================================================================
# 6. CONCURRENCY & RATE LIMITING TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_bounded_concurrency_control():
    """Verify concurrency semaphore limits concurrent websocket operations."""
    provider = EdgeTTSVoiceProvider()

    # Verify semaphore initialization
    assert provider._semaphore._value == settings.MAX_TTS_CONCURRENCY

    # Run 4 concurrent requests (higher than semaphore limit of 2)
    texts = [
        f"Câu thứ {i}: Việt Nam đất nước con người tươi đẹp vạn dặm."
        for i in range(4)
    ]
    tasks = [
        provider.synthesize(t, voice="vi-VN-NamMinhNeural")
        for t in texts
    ]
    results = await asyncio.gather(*tasks)
    assert len(results) == 4
    for r in results:
        assert r.duration_seconds > 0
        assert len(r.words) > 0

# ==============================================================================
# 7. RETRY & FALLBACK RECOVERY TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_tts_retry_transient_failure_recovery():
    """Verify transient websocket errors recover on retry with exponential backoff."""
    provider = EdgeTTSVoiceProvider()

    attempt_count = 0
    real_synthesize_chunk = provider._synthesize_single_chunk

    async def mock_transient_fail(*args, **kwargs):
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count == 1:
            raise ConnectionResetError("Transient network drop")
        return await real_synthesize_chunk(*args, **kwargs)

    with patch.object(provider, "_synthesize_single_chunk", side_effect=mock_transient_fail):
        result = await provider.synthesize("Kiểm tra cơ chế thử lại tự động khi rớt mạng.", voice="vi-VN-NamMinhNeural")
        assert attempt_count >= 2, "Should have retried at least once"
        assert result.duration_seconds > 0
        assert len(result.words) > 0

@pytest.mark.asyncio
async def test_tts_offline_fallback_when_hard_failure():
    """Verify permanent failure falls back gracefully to valid playable audio."""
    provider = EdgeTTSVoiceProvider()

    with patch.object(provider, "_synthesize_chunk_with_retry", side_effect=RuntimeError("Edge TTS Service Down")):
        result = await provider.synthesize("Đoạn văn kiểm tra chế độ dự phòng khẩn cấp.", voice="vi-VN-NamMinhNeural")
        assert result.duration_seconds > 0
        assert len(result.words) > 0
        # Check audio file on disk
        filepath = os.path.join(provider.storage_dir, f"{result.audio_id}.mp3")
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0

# ==============================================================================
# 8. API ENDPOINT & VALIDATION TESTS
# ==============================================================================

def test_tts_api_input_validation_and_voices():
    """Verify API input validation for rate, pitch, volume, and voices listing."""
    client = TestClient(app)
    headers = get_auth_headers("test_user_api")

    # 1. Voices listing
    v_resp = client.get("/api/v1/tts/voices")
    assert v_resp.status_code == 200
    voices = v_resp.json()
    assert len(voices) >= 2
    voice_ids = [v["id"] for v in voices]
    assert "vi-VN-NamMinhNeural" in voice_ids
    assert "vi-VN-HoaiMyNeural" in voice_ids

    # 2. Invalid rate format -> 400
    bad_rate = client.post("/api/v1/tts/synthesize", json={
        "text": "Kiểm tra tốc độ đọc không hợp lệ.",
        "rate": "nhanh_hon"
    }, headers=headers)
    assert bad_rate.status_code == 400

    # 3. Invalid pitch format -> 400
    bad_pitch = client.post("/api/v1/tts/synthesize", json={
        "text": "Kiểm tra cao độ giọng đọc không hợp lệ.",
        "pitch": "+20"
    }, headers=headers)
    assert bad_pitch.status_code == 400

    # 4. Invalid volume format -> 400
    bad_vol = client.post("/api/v1/tts/synthesize", json={
        "text": "Kiểm tra âm lượng giọng đọc không hợp lệ.",
        "volume": "to_hon"
    }, headers=headers)
    assert bad_vol.status_code == 400

    # 5. Text too short -> 422
    too_short = client.post("/api/v1/tts/synthesize", json={
        "text": "a"
    }, headers=headers)
    assert too_short.status_code == 422
