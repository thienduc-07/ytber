"""
Soundscape and Environmental Sound Design Router.
Provides API endpoints for soundscape presets, smart SFX search,
and dynamic scene acoustic detection.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field

from backend.providers.soundscape_engine import AISoundscapeDirector, SceneSoundscapeSpec

router = APIRouter(prefix="/api/v1/soundscape", tags=["AI Soundscape & SFX Design"])


class DetectSoundscapeRequest(BaseModel):
    scene_id: str = Field(default="scene_01")
    scene_order: int = Field(default=1)
    duration_sec: float = Field(default=3.5, ge=0.5, le=300.0)
    visual_description: str = Field(..., description="Mô tả hình ảnh hoặc hành động của cảnh")
    setting_name: str = Field(default="", description="Tên bối cảnh (ví dụ: Nhà hoang, Rừng cổ, Hiện trường)")
    character_action: str = Field(default="walk", description="Hành động nhân vật")


@router.get("/presets", response_model=List[Dict[str, Any]])
async def get_soundscape_presets():
    """
    Returns rich soundscape presets including:
    👻 Kinh dị / Chuyện ma (Horror), 🕵️ Phá án / Trinh thám (Crime Noir),
    🌲 Rừng nhiệt đới, ⚔️ Chiến trường đèo núi, 📈 Tài chính,
    💻 Công nghệ, 🚀 Vũ trụ, 🍃 Đồng cỏ sinh thái.
    """
    return AISoundscapeDirector.get_soundscape_presets()


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_sound_effects(
    q: Optional[str] = Query(default="", description="Từ khóa tìm kiếm hiệu ứng (ví dụ: ma, cửa, bước chân, sấm sét, whoosh, tim, tiền)"),
    category: Optional[str] = Query(default=None, description="Lọc theo thể loại: horror, transition, crime, historical, weather, comedy")
):
    """
    Real-time Smart Sound Effect Search.
    Allows searching and filtering action SFX, whooshes, impacts, and ambient stingers.
    """
    return AISoundscapeDirector.search_sfx(query=q or "", category=category)


@router.post("/detect", response_model=SceneSoundscapeSpec)
async def detect_scene_soundscape(req: DetectSoundscapeRequest):
    """
    Automatically detects and derives a 3-layer soundscape specification
    (BGM theme, environmental ambience, and action SFX events) from scene semantics.
    """
    try:
        spec = AISoundscapeDirector.generate_soundscape_for_scene(
            scene_id=req.scene_id,
            scene_order=req.scene_order,
            duration_sec=req.duration_sec,
            visual_description=req.visual_description,
            setting_name=req.setting_name,
            character_action=req.character_action
        )
        return spec
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi phân tích âm thanh cảnh: {str(e)}"
        )


@router.get("/audio/{sfx_id}")
async def get_sfx_audio_preview(sfx_id: str):
    """
    Returns audio preview stream for the specified sound effect.
    Synthesizes acoustic audio file on the fly if not yet cached.
    """
    import os
    from fastapi.responses import FileResponse
    from backend.core.config import settings

    storage_dir = getattr(settings, "AUDIO_STORAGE_PATH", "./data/audio")
    sfx_dir = os.path.join(storage_dir, "sfx")
    os.makedirs(sfx_dir, exist_ok=True)

    clean_id = "".join(c for c in sfx_id if c.isalnum() or c in ("_", "-"))
    file_path = os.path.join(sfx_dir, f"{clean_id}.mp3")

    if not os.path.exists(file_path):
        AISoundscapeDirector.synthesize_sfx_file(clean_id, file_path)

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=f"{clean_id}.mp3"
    )


class AutoEnrichRequest(BaseModel):
    manifest: Dict[str, Any]


@router.post("/auto-enrich")
async def auto_enrich_manifest_sound(req: AutoEnrichRequest):
    """
    Scans every scene in the manifest, automatically determines narrative mood and action beats,
    and assigns optimal environmental soundscapes, action SFX cues, and thematic background music.
    """
    manifest = req.manifest
    scenes = manifest.get("scenes", [])
    if not scenes:
        return manifest

    enriched = AISoundscapeDirector.enrich_manifest_soundscapes(manifest)
    return enriched
