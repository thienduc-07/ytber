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
    narration_text: str
    duration_seconds: float
    visual_method: str = Field(description="photo, stock, archival, map, svg, infographic, procedural, parallax, toon")
    visual_description: str
    suggested_asset_keywords: List[str] = Field(default_factory=list)
    camera_direction: Optional[str] = "slow push-in"
    transition: Optional[str] = "cut"
    sound_design: List[SoundDesignCue] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)

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
