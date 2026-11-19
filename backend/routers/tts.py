import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.core.security import get_current_user_id
from backend.providers.tts_engine import EdgeTTSVoiceProvider, TTSResult

router = APIRouter(prefix="/api/v1/tts", tags=["Voice Studio & Speech Synthesis"])
voice_provider = EdgeTTSVoiceProvider()

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=5000, description="Văn bản lồng tiếng tiếng Việt")
    voice: str = Field(default="vi-VN-NamMinhNeural", description="vi-VN-NamMinhNeural hoặc vi-VN-HoaiMyNeural")
    rate: str = Field(default="+0%", description="Tốc độ đọc (ví dụ: -10%, +0%, +15%)")
    pitch: str = Field(default="+0Hz", description="Cao độ giọng đọc")

@router.get("/voices", response_model=List[Dict[str, Any]])
async def get_available_voices():
    """Returns list of supported high-quality neural Vietnamese voices."""
    return voice_provider.get_supported_voices()

@router.post("/synthesize", response_model=TTSResult)
async def synthesize_voice_endpoint(
    req: TTSRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Synthesizes real Vietnamese speech using Microsoft Edge Neural TTS.
    Returns the real audio download/stream URL, total duration, and exact
    word-level millisecond boundary cues for animated karaoke subtitle synchronization.
    """
    try:
        result = await voice_provider.synthesize(
            text=req.text,
            voice=req.voice,
            rate=req.rate,
            pitch=req.pitch
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )

@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serves synthesized genuine audio files for preview, video player, and WebCodecs muxing."""
    # Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(settings.AUDIO_STORAGE_PATH, safe_filename)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tập tin âm thanh không tồn tại hoặc đã hết hạn lưu trữ"
        )

    return FileResponse(
        filepath,
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=86400",
        }
    )
