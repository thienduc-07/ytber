import os
import re
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import get_current_user_id
from backend.models.db_models import AudioFileModel
from backend.providers.director_engine import AIDirectorEngine
from backend.providers.tts_engine import UnifiedTTSProvider
from backend.providers.asset_discovery import AssetDiscoveryService
from backend.providers.asset_downloader import AssetDownloaderService
from backend.providers.soundscape_engine import AISoundscapeDirector

router = APIRouter(prefix="/api/v1/director", tags=["AI Director & Zero-Touch Video Production"])

director_engine = AIDirectorEngine()
voice_provider = UnifiedTTSProvider(allow_offline_fallback=True)
asset_discovery = AssetDiscoveryService()
asset_downloader = AssetDownloaderService()

class FilmBlueprintRequest(BaseModel):
    script_text: str = Field(..., min_length=10, description="Văn bản kịch bản tiếng Việt")
    genre: str = Field(default="historical_doc", description="Thể loại video")
    video_format: str = Field(default="short-form", description="'short-form' (9:16) hoặc 'long-form' (16:9)")
    visual_style: str = Field(default="2d_cartoon", description="Phong cách hình ảnh")

class GenerateMovieRequest(BaseModel):
    script_text: str = Field(..., min_length=10, description="Văn bản kịch bản tiếng Việt đầu vào")
    genre: str = Field(default="historical_doc", description="Thể loại video")
    video_format: str = Field(default="short-form", description="'short-form' (9:16) hoặc 'long-form' (16:9)")
    voice: str = Field(default="vi-VN-NamMinhNeural", description="Giọng đọc tiếng Việt")
    rate: str = Field(default="+0%", description="Tốc độ đọc")
    pitch: str = Field(default="+0Hz", description="Cao độ")
    visual_style: str = Field(default="2d_cartoon", description="Phong cách hình ảnh 2.5D/Toon")

@router.post("/blueprint")
async def create_film_blueprint(req: FilmBlueprintRequest):
    """
    Sinh Bản Thiết Kế Điện Ảnh (Film Blueprint) tự động:
    - Cấu trúc kịch tính 5 phần (Hook 3-5s, Setup, Conflict, Climax, Resolution).
    - Character Bible: Thiết lập hồ sơ nhân vật hoạt họa đồng nhất.
    - Environment Bible: Thiết lập bối cảnh, ánh sáng, bảng màu.
    - Từng cảnh có chỉ đạo máy quay, từ khóa tìm tư liệu và hiệu ứng âm thanh SFX.
    """
    try:
        blueprint = director_engine.generate_film_blueprint(
            script_text=req.script_text,
            genre=req.genre,
            video_format=req.video_format,
            visual_style=req.visual_style
        )
        return blueprint
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lỗi tạo bản thiết kế điện ảnh: {str(e)}"
        )

@router.post("/generate-movie")
async def generate_movie_zero_touch(
    req: GenerateMovieRequest,
    authorization: Optional[str] = Header(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Quy trình sản xuất phim tự động 100% (Zero-Touch AI Studio):
    1. AI Director phân tích kịch bản và thiết lập Film Blueprint 5 phần.
    2. Tổng hợp giọng đọc tiếng Việt thật qua UnifiedTTSProvider (VoiceStudio / Edge-TTS).
    3. Tự động đồng bộ thời lượng cảnh theo độ dài tệp âm thanh thực tế (Duration Sync).
    4. Tự động tìm kiếm và tải tư liệu thực bản quyền mở (Wikimedia, Openverse, Pexels) kèm đầy đủ siêu dữ liệu nguồn gốc (Provenance).
    5. Thiết lập kiến trúc âm thanh 4 Bus (Voiceover, BGM ducked -17dB, Ambience môi trường đa lớp, Action SFX bước chân 2.2Hz & whoosh).
    6. Tính toán toàn bộ mốc khung hình (start_frame, end_frame, 30 FPS) và trả về SceneManifest hoàn chỉnh.
    """
    try:
        # 1. Generate Film Blueprint
        blueprint = director_engine.generate_film_blueprint(
            script_text=req.script_text,
            genre=req.genre,
            video_format=req.video_format,
            visual_style=req.visual_style
        )

        blueprint_scenes = blueprint.get("scenes", [])
        if not blueprint_scenes:
            raise ValueError("Không tạo được danh sách cảnh từ kịch bản")

        auth_token = authorization.split(" ")[1] if authorization and " " in authorization else "demo-guest-token"
        fps = 30
        is_long = req.video_format == "long-form"
        width = 1920 if is_long else 1080
        height = 1080 if is_long else 1920

        processed_scenes = []
        current_frame = 0

        # 2. Process each scene: TTS, Asset Discovery, and 4-Bus Soundscape
        for idx, bp_sc in enumerate(blueprint_scenes):
            narration = bp_sc.get("narration_text", "").strip()
            sc_order = bp_sc.get("scene_order", idx + 1)
            sc_id = bp_sc.get("scene_id", f"scene_{sc_order:02d}")

            # 2a. Voice Synthesis with Real Duration Measurement
            tts_res = await voice_provider.synthesize(
                text=narration,
                voice=req.voice,
                rate=req.rate,
                pitch=req.pitch
            )
            real_duration = max(3.0, round(tts_res.duration_seconds, 2))
            audio_filename = f"{tts_res.audio_id}.mp3"
            audio_url = f"/api/v1/tts/audio/{audio_filename}?token={auth_token}"

            # Register audio file in database for authenticated user
            stmt = select(AudioFileModel).where(
                AudioFileModel.filename == audio_filename,
                AudioFileModel.user_id == user_id
            )
            existing_audio = (await db.execute(stmt)).scalar_one_or_none()
            if not existing_audio:
                db_audio = AudioFileModel(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    filename=audio_filename,
                    duration_seconds=real_duration
                )
                db.add(db_audio)
                await db.commit()

            # 2b. Asset Discovery & Provenance Recording
            scene_assets = []
            visual_config: Dict[str, Any] = {}
            visual_method = bp_sc.get("visual_method", "toon")

            query = bp_sc.get("visual_query") or blueprint.get("title") or "Vietnam history"
            try:
                discovered = await asset_discovery.search(query=query, limit=3, media_type="image")
                if discovered:
                    top_asset = discovered[0]
                    # Secure download with provenance tracking
                    try:
                        downloaded = await asset_downloader.download_asset(
                            url=top_asset.download_url,
                            user_id=user_id
                        )
                        scene_assets.append({
                            "id": top_asset.asset_id,
                            "asset_type": "image",
                            "source_url": top_asset.source_url,
                            "download_url": top_asset.download_url,
                            "local_url": downloaded["local_url"],
                            "license_type": top_asset.license,
                            "author_name": top_asset.creator,
                            "attribution_text": top_asset.attribution_text,
                            "provider": top_asset.provider,
                            "semantic_relevance_score": 0.95,
                            "cache_path": downloaded["file_path"]
                        })
                        visual_config["imageUrl"] = downloaded["local_url"]
                        visual_method = "photo"
                    except Exception as dl_err:
                        # Fallback to procedural animated style if download fails
                        visual_method = "toon"
                        visual_config["procedural"] = True
                else:
                    visual_method = "toon"
                    visual_config["procedural"] = True
            except Exception:
                visual_method = "toon"
                visual_config["procedural"] = True

            # 2c. 4-Bus Soundscape Enrichment (Voiceover, BGM ducked, Ambience, SFX)
            soundscape_spec = AISoundscapeDirector.generate_soundscape_for_scene(
                scene_id=sc_id,
                scene_order=sc_order,
                duration_sec=real_duration,
                visual_description=bp_sc.get("visual_description", ""),
                setting_name=bp_sc.get("environment_setting", ""),
                character_action=bp_sc.get("sfx_cues", [{}])[0].get("sfx_type", "walk") if bp_sc.get("sfx_cues") else "walk"
            )

            # Combine soundscape SFX with blueprint cues
            combined_sfx = [
                {
                    "sfx_id": evt.event_id,
                    "sfx_type": evt.action_type,
                    "description": evt.description,
                    "start_time_offset_ms": evt.timestamp_offset_ms,
                    "volume": evt.volume,
                    "duck_narration": False
                }
                for evt in soundscape_spec.action_sfx_events
            ]

            # 2d. Frame bounds calculation
            frame_count = int(round(real_duration * fps))
            start_f = current_frame
            end_f = current_frame + frame_count
            current_frame = end_f

            processed_scenes.append({
                "scene_id": sc_id,
                "scene_order": sc_order,
                "scene_type": bp_sc.get("scene_type", "narrative"),
                "narrative_purpose": bp_sc.get("narrative_stage", "narrative"),
                "narration_text": narration,
                "duration_seconds": real_duration,
                "start_frame": start_f,
                "end_frame": end_f,
                "visual_method": visual_method,
                "visual_description": bp_sc.get("visual_description", ""),
                "visual_config": visual_config,
                "camera_direction": bp_sc.get("camera_direction", "slow_push_in"),
                "camera_movement": bp_sc.get("camera_direction", "slow_push_in"),
                "transition": bp_sc.get("transition", "crossfade"),
                "audio_url": audio_url,
                "subtitles_json": [w.model_dump() if hasattr(w, "model_dump") else w for w in tts_res.words],
                "assets": scene_assets,
                "music_direction": soundscape_spec.music_theme,
                "ambient_layers": [l.model_dump() if hasattr(l, "model_dump") else l for l in soundscape_spec.ambient_layers],
                "sound_design": combined_sfx,
                "sound_effects": combined_sfx
            })

        total_duration = sum(s["duration_seconds"] for s in processed_scenes)

        manifest = {
            "episode_id": f"movie_{uuid.uuid4().hex[:12]}",
            "title": blueprint.get("title", "Phim Hoạt Họa AI"),
            "genre": blueprint.get("genre", req.genre),
            "video_format": req.video_format,
            "aspect_ratio": "16:9" if is_long else "9:16",
            "total_duration_sec": round(total_duration, 2),
            "total_frames": current_frame,
            "dramatic_arc": blueprint.get("dramatic_arc", ""),
            "character_bible": blueprint.get("character_bible", {}),
            "environment_bible": blueprint.get("environment_bible", {}),
            "voice_config": {
                "voice": req.voice,
                "rate": req.rate,
                "pitch": req.pitch
            },
            "video_specs": {
                "width": width,
                "height": height,
                "fps": fps
            },
            "audio_specs": {
                "target_lufs": -14.0,
                "true_peak": -1.0,
                "ducking_attenuation_db": -17.0,
                "buses": ["Voiceover", "BackgroundMusic", "EnvironmentalAmbience", "ActionSFX"]
            },
            "scenes": processed_scenes,
            "chapters": []
        }

        return manifest

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi trong quy trình tạo phim tự động: {str(e)}"
        )
