from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SoundDesignCue(BaseModel):
    sfx_type: str = Field(description="ambience, drone, impact, whoosh, footsteps, static, riser, silence")
    description: str
    volume: float = Field(default=0.3, ge=0.0, le=1.0)
    duck_narration: bool = Field(default=True)

class ResearchEntity(BaseModel):
    name: str
    entity_type: str = Field(description="person, location, event, organization, date, concept")
    context: str
    search_query: str

class ScenePlan(BaseModel):
    scene_id: Optional[str] = None
    scene_order: int
    chapter_order: Optional[int] = 1
    scene_type: str = Field(description="hook, setting, escalation, mechanism, climax, twist, resolution, cta")
    narration_text: str = ""
    narration: Optional[str] = None
    duration_seconds: float = 4.0
    estimated_duration: Optional[float] = None
    visual_method: str = Field(default="photo", description="photo, stock, archival, map, svg, infographic, procedural, parallax, toon")
    visual_description: str = ""
    suggested_asset_keywords: List[str] = Field(default_factory=list)
    search_keywords: List[str] = Field(default_factory=list)
    preferred_media_type: str = Field(default="image", description="image or video")
    preferred_aspect_ratio: str = Field(default="9:16", description="9:16 or 16:9")
    camera_direction: Optional[str] = "slow push-in"
    transition: Optional[str] = "cut"
    transition_type: Optional[str] = "cut"
    sound_design: List[SoundDesignCue] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        # Synchronize alias fields
        if "narration" in data and not data.get("narration_text"):
            data["narration_text"] = data["narration"]
        elif "narration_text" in data and not data.get("narration"):
            data["narration"] = data["narration_text"]

        if "duration_seconds" in data and not data.get("estimated_duration"):
            data["estimated_duration"] = data["duration_seconds"]
        elif "estimated_duration" in data and not data.get("duration_seconds"):
            data["duration_seconds"] = data["estimated_duration"]

        if "search_keywords" in data and not data.get("suggested_asset_keywords"):
            data["suggested_asset_keywords"] = data["search_keywords"]
        elif "suggested_asset_keywords" in data and not data.get("search_keywords"):
            data["search_keywords"] = data["suggested_asset_keywords"]

        if "transition" in data and not data.get("transition_type"):
            data["transition_type"] = data["transition"]
        elif "transition_type" in data and not data.get("transition"):
            data["transition"] = data["transition_type"]

        super().__init__(**data)

class ChapterPlan(BaseModel):
    chapter_order: int
    title: str
    summary: str
    estimated_duration_seconds: float
    scene_count: int
    scenes: List[ScenePlan] = Field(default_factory=list)

class ScriptAnalysisResult(BaseModel):
    title: str
    genre: str = Field(default="general")
    video_format: str = Field(default="short-form", description="short-form (9:16) or long-form (16:9)")
    aspect_ratio: str = Field(default="9:16")
    estimated_syllables: int
    estimated_duration_seconds: float
    hook_summary: str
    scenes: List[ScenePlan]
    chapters: List[ChapterPlan] = Field(default_factory=list)
    entities: List[ResearchEntity] = Field(default_factory=list)
    ai_provider_used: str

class AIScriptProvider(ABC):
    @abstractmethod
    async def analyze_script(
        self,
        script_text: str,
        target_duration: int = 60,
        genre: str = "general",
        video_format: str = "short-form",
        visual_style: str = "adaptive"
    ) -> ScriptAnalysisResult:
        """
        Analyzes a raw Vietnamese script with Genre Intelligence,
        extracts entities and research needs, plans scenes/chapters,
        calculates pacing, sound design, and adaptive visual methods.
        """
        pass
