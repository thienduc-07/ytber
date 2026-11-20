import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx

from backend.providers.tts_engine import (
    validate_audio_file,
    VoiceStudioProvider,
    UnifiedTTSProvider,
    TTSGenerationError,
    TTSResult,
    WordTiming
)

def test_validate_audio_file_size_and_silence():
    # 1. Too small (< 512 bytes)
    too_small = b"\xff\xf3\x60\x00" + (b"\x55" * 100)
    is_valid, msg = validate_audio_file(too_small, min_bytes=512)
    assert not is_valid
    assert "too small" in msg.lower()

    # 2. Silent dummy repeating mock pattern (> 512 bytes but low entropy)
    silent_mock = (b"\xff\xf3\x60\x00" + (b"\x55" * 140)) * 10  # 1440 bytes, only 4 unique bytes
    is_valid, msg = validate_audio_file(silent_mock, min_bytes=512)
    assert not is_valid
    assert "silent/synthetic mock" in msg.lower()

    # 3. Invalid header
    invalid_header = bytes([i % 256 for i in range(1000)])
    is_valid, msg = validate_audio_file(invalid_header, min_bytes=512)
    assert not is_valid
    assert "invalid audio format" in msg.lower()

    # 4. Valid MP3 audio frame with rich entropy
    valid_frame = b"\xff\xf3\x60\x00" + bytes([(i * 17 + (i % 7) * 31) & 0xFF for i in range(140)])
    valid_audio = valid_frame * 15  # 2160 bytes
    is_valid, msg = validate_audio_file(valid_audio, min_bytes=512)
    assert is_valid, f"Expected valid audio, got: {msg}"

@pytest.mark.asyncio
async def test_voicestudio_provider_success(tmp_path):
    provider = VoiceStudioProvider(storage_dir=str(tmp_path))
    test_text = "Chiến thắng Điện Biên Phủ lừng lẫy năm châu chấn động địa cầu."

    valid_frame = b"\xff\xf3\x60\x00" + bytes([(i * 17 + (i % 7) * 31) & 0xFF for i in range(140)])
    mock_mp3_data = valid_frame * 30  # ~4320 bytes

    # Mock VoiceStudio HTTP API
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.content = mock_mp3_data

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get, \
         patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock) as mock_post:
        
        mock_get.return_value = MagicMock(status_code=200)
        mock_post.return_value = mock_response

        assert await provider.is_available() is True
        result = await provider.synthesize(test_text, voice="vi-VN-NamMinhNeural")

        assert result.provider == "voicestudio"
        assert result.duration_seconds > 0
        assert len(result.words) > 0
        audio_file = os.path.join(str(tmp_path), f"{result.audio_id}.mp3")
        assert os.path.exists(audio_file)
        assert os.path.getsize(audio_file) >= 512

@pytest.mark.asyncio
async def test_unified_tts_provider_failover_to_edge(tmp_path):
    provider = UnifiedTTSProvider(storage_dir=str(tmp_path), allow_offline_fallback=False)
    test_text = "Thử nghiệm cơ chế dự phòng tự động chuyển từ VoiceStudio sang Edge TTS."

    # Simulate VoiceStudio server down
    with patch.object(provider.voicestudio, "is_available", new_callable=AsyncMock, return_value=False):
        result = await provider.synthesize(test_text, voice="vi-VN-NamMinhNeural")
        # Should gracefully fall back to EdgeTTS
        assert "edge-tts" in result.provider.lower()
        assert result.duration_seconds > 0
        assert len(result.words) > 0

@pytest.mark.asyncio
async def test_unified_tts_provider_raises_when_both_fail(tmp_path):
    provider = UnifiedTTSProvider(storage_dir=str(tmp_path), allow_offline_fallback=False)
    test_text = "Kiểm tra cơ chế nghiêm ngặt không mock silent audio khi cả hai đều lỗi."

    with patch.object(provider.voicestudio, "is_available", new_callable=AsyncMock, return_value=False), \
         patch.object(provider.edge_tts, "synthesize", side_effect=RuntimeError("EdgeTTS connection failure")):
        
        with pytest.raises(TTSGenerationError) as exc_info:
            await provider.synthesize(test_text)
        
        err_msg = str(exc_info.value)
        assert "VoiceStudio" in err_msg
        assert "Edge-TTS" in err_msg
