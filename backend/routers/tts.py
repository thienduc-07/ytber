import os
import re
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Header, Query, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import get_current_user_id, decode_and_verify_supabase_jwt
from backend.models.db_models import AudioFileModel
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
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Synthesizes real Vietnamese speech using Microsoft Edge Neural TTS.
    Returns the real audio download/stream URL, total duration, and exact
    word-level millisecond boundary cues for animated karaoke subtitle synchronization.
    Saves audio record with tenant ownership.
    """
    try:
        result = await voice_provider.synthesize(
            text=req.text,
            voice=req.voice,
            rate=req.rate,
            pitch=req.pitch
        )

        # Persist audio ownership in database
        filename = f"{result.audio_id}.mp3"
        audio_rec = AudioFileModel(
            id=result.audio_id,
            user_id=user_id,
            filename=filename,
            duration_seconds=result.duration_seconds
        )
        db.add(audio_rec)
        await db.commit()

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )

@router.get("/audio/{filename}")
async def get_audio_file(
    filename: str,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Serves synthesized genuine audio files for preview, video player, and WebCodecs muxing.
    Protected with Bearer token authentication or signed token query parameter.
    Enforces strict tenant isolation, path traversal prevention, and filesystem masking.
    """
    # 1. Path traversal and filename validation
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: Path traversal characters are not permitted"
        )
    if not re.match(r"^[a-zA-Z0-9_-]+\.(mp3|wav)$", filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: Filename format not allowed"
        )

    # 2. Extract and verify authentication token
    auth_token = None
    if authorization:
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            auth_token = parts[1]
    elif token:
        auth_token = token

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: Missing Bearer token or 'token' query parameter",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_and_verify_supabase_jwt(auth_token)
    current_user_id = str(payload.get("sub"))

    # 3. Check ownership in database
    stmt = select(AudioFileModel).where(AudioFileModel.filename == filename)
    res = await db.execute(stmt)
    audio_rec = res.scalar_one_or_none()
    if audio_rec and audio_rec.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not own this audio file"
        )

    # 4. Verify physical file existence securely within storage directory
    abs_storage = os.path.abspath(settings.AUDIO_STORAGE_PATH)
    filepath = os.path.abspath(os.path.join(abs_storage, filename))

    if not filepath.startswith(abs_storage) or not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tập tin âm thanh không tồn tại hoặc đã hết hạn lưu trữ"
        )

    return FileResponse(
        filepath,
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "private, max-age=86400",
        }
    )
