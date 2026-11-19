from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from backend.core.security import get_current_user_id
from backend.providers.tts_engine import TTSService, TTSResult

router = APIRouter(prefix="/api/v1/tts", tags=["Voice Studio"])
tts_service = TTSService()

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=2000, description="Văn bản lồng tiếng tiếng Việt")
    voice: str = Field(default="vi-VN-NamMinhNeural")
    rate: str = Field(default="+5%")
    pitch: str = Field(default="+0Hz")

@router.post("/synthesize", response_model=TTSResult)
async def synthesize_voice_endpoint(
    req: TTSRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Normalizes Vietnamese numbers/dates/loan-words, calculates speech duration,
    and returns word-level millisecond timestamps for animated subtitle synchronization.
    """
    return await tts_service.synthesize(text=req.text, voice=req.voice)
