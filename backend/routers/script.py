from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from backend.core.security import get_current_user_id
from backend.providers.ai_groq import GroqScriptProvider
from backend.providers.ai_base import ScriptAnalysisResult
from backend.providers.genre_intelligence import GENRE_REGISTRY, GenreProfile

router = APIRouter(prefix="/api/v1/script", tags=["Script Analysis & Genre Intelligence"])

class ScriptAnalyzeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    script_text: str = Field(..., min_length=10, max_length=20000, description="Nội dung kịch bản tiếng Việt")
    target_duration_seconds: Optional[int] = Field(default=60, ge=15, le=3600, alias="target_duration_sec")
    genre: Optional[str] = Field(default="general", description="Thể loại: horror, historical_doc, economics, science, education, news, biography, business, crime, general")
    video_format: Optional[str] = Field(default="short-form", pattern="^(short-form|long-form)$")
    visual_style_preference: Optional[str] = Field(default="adaptive", alias="pacing_preference")

# Instantiate default provider (with automatic offline fallback)
script_provider = GroqScriptProvider()

@router.get("/genres", response_model=List[Dict[str, Any]])
async def list_supported_genres():
    """Lists all 10 specialized genres with pacing, narrative stages, and visual directions."""
    return [g.model_dump() if hasattr(g, "model_dump") else g.dict() for g in GENRE_REGISTRY.values()]

@router.post("/analyze", response_model=ScriptAnalysisResult)
async def analyze_script_endpoint(
    req: ScriptAnalyzeRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Analyzes a raw Vietnamese script with Genre Intelligence,
    breaks it into structured documentary scenes or long-form chapters,
    extracts research entities, and configures adaptive visuals and sound design.
    """
    try:
        result = await script_provider.analyze_script(
            script_text=req.script_text,
            target_duration=req.target_duration_seconds or 60,
            genre=req.genre or "general",
            video_format=req.video_format or "short-form",
            visual_style=req.visual_style_preference or "adaptive"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Script analysis failed: {str(e)}"
        )
