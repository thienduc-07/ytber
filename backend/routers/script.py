from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from backend.core.security import get_current_user_id
from backend.providers.ai_groq import GroqScriptProvider
from backend.providers.ai_base import ScriptAnalysisResult

router = APIRouter(prefix="/api/v1/script", tags=["Script Analysis"])

class ScriptAnalyzeRequest(BaseModel):
    script_text: str = Field(..., min_length=10, max_length=5000, description="Nội dung kịch bản tiếng Việt")
    target_duration_seconds: Optional[int] = Field(default=60, ge=15, le=120)
    visual_style_preference: Optional[str] = Field(default="adaptive")

# Instantiate default provider (with automatic offline fallback)
script_provider = GroqScriptProvider()

@router.post("/analyze", response_model=ScriptAnalysisResult)
async def analyze_script_endpoint(
    req: ScriptAnalyzeRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Analyzes a raw Vietnamese script, breaks it into documentary scenes,
    calculates target timings, and assigns adaptive visual methods.
    Multi-tenant authenticated endpoint.
    """
    try:
        result = await script_provider.analyze_script(
            script_text=req.script_text,
            target_duration=req.target_duration_seconds,
            visual_style=req.visual_style_preference
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Script analysis failed: {str(e)}"
        )
