from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CharacterProfile(BaseModel):
    character_id: str
    name: str
    role: str = "protagonist"  # protagonist, antagonist, supporting, presenter
    body_proportions: str = "stylized_cartoon"  # stylized_cartoon, chibi, infographic_figure
    costume_description: str = ""
    color_scheme: List[str] = Field(default_factory=lambda: ["#36522D", "#EBB991", "#8A5C36", "#FFD700", "#DC281E"])
    facial_features: str = "expressive animated eyes with dynamic eyebrows and mouth"
    distinguishing_props: List[str] = Field(default_factory=list)

class EnvironmentSpec(BaseModel):
    setting_name: str = "historical_outdoor"
    environment_type: str = "mountain_battlefield"  # outdoor_nature, mountain_battlefield, interior_lab, trading_floor, abstract_space
    time_of_day: str = "sunset_golden"  # day, sunset_golden, night_moonlight, dawn
    weather_particles: str = "smoke_embers"  # clear, fog_mist, smoke_embers, dust_wind, data_stream, stars
    primary_colors: List[str] = Field(default_factory=lambda: ["#2B1E14", "#465F32", "#E2453C", "#FFE2A0", "#110E1A"])

class CameraDirective(BaseModel):
    angle: str = "eye_level"  # eye_level, low_angle_heroic, high_angle_overview, top_down_map
    movement: str = "slow_push_in"  # slow_push_in, pan_right, tilt_up, tracking, dynamic_zoom, static_hold
    zoom_ratio: float = 1.12

class AnimationDirective(BaseModel):
    character_action: str = "march"  # march, pull_cannon, point_gesture, cheer, stand, analyze_chart
    object_action: str = "particle_float"  # cannon_fire, flag_wave, car_move, chart_grow, map_trace, particle_float
    parallax_enabled: bool = True
    motion_intensity: float = 0.8

class SoundDesignCue(BaseModel):
    sfx_id: Optional[str] = None
    sfx_type: str = Field(description="ambience, drone, impact, whoosh, footsteps, static, riser, silence, cannon, cheer, coin, click")
    description: str
    start_time_offset_ms: int = 0
    volume: float = Field(default=0.3, ge=0.0, le=1.0)
    duck_narration: bool = Field(default=True)

class ResearchEntity(BaseModel):
    name: str
    entity_type: str = Field(description="person, location, event, organization, date, concept")
    context: str
    search_query: str

class ScenePlan(BaseModel):
    # 17-Attribute Production Specification for AI Director
    scene_id: Optional[str] = None
    scene_order: int
    chapter_order: Optional[int] = 1
    narrative_purpose: str = "setting_and_context"
    scene_type: str = Field(default="hook", description="hook, setting, escalation, mechanism, climax, twist, resolution, cta")
    narration_text: str = ""
    narration: Optional[str] = None
    duration_seconds: float = 4.0
    estimated_duration: Optional[float] = None
    visual_method: str = Field(default="toon", description="toon, procedural, svg, infographic, map, parallax, archival")
    visual_description: str = ""
    environment: Optional[EnvironmentSpec] = None
    character_descriptions: List[str] = Field(default_factory=list)
    character_poses: List[str] = Field(default_factory=list)
    character_poses_actions: Optional[List[str]] = None
    props: List[str] = Field(default_factory=list)
    camera_angle: str = "eye_level"
    camera_movement: str = "slow_push_in"
    camera_direction: Optional[str] = "slow push-in"
    animation_instructions: Optional[AnimationDirective] = None
    lighting: str = "cinematic_golden_hour"
    color_palette: List[str] = Field(default_factory=lambda: ["#1e293b", "#334155", "#e2e8f0", "#facc15", "#ef4444"])
    transition: Optional[str] = "crossfade"
    transition_type: Optional[str] = "crossfade"
    music_direction: str = "cinematic_orchestral_heroic"
    sound_design: List[SoundDesignCue] = Field(default_factory=list)
    sound_effects: Optional[List[SoundDesignCue]] = None
    subtitles_json: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_asset_keywords: List[str] = Field(default_factory=list)
    search_keywords: List[str] = Field(default_factory=list)
    preferred_media_type: str = Field(default="image", description="image or video")
    preferred_aspect_ratio: str = Field(default="9:16", description="9:16 or 16:9")
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

        if "character_poses_actions" in data and not data.get("character_poses"):
            data["character_poses"] = data["character_poses_actions"]
        elif "character_poses" in data and not data.get("character_poses_actions"):
            data["character_poses_actions"] = data["character_poses"]

        if "sound_effects" in data and not data.get("sound_design"):
            data["sound_design"] = data["sound_effects"]
        elif "sound_design" in data and not data.get("sound_effects"):
            data["sound_effects"] = data["sound_design"]

        if not data.get("scene_id") and "scene_order" in data:
            data["scene_id"] = f"sc_{data['scene_order']:02d}"

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
    main_subject: str = ""
    topic_category: str = "general"
    context_era: str = "contemporary"
    narrative_arc: str = "chronological_escalation"
    emotional_tone: str = "informative_and_engaging"
    target_audience: str = "general_public"
    visual_style_preset: str = "2d_cartoon"
    character_registry: Dict[str, CharacterProfile] = Field(default_factory=dict)
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
        visual_style: str = "2d_cartoon"
    ) -> ScriptAnalysisResult:
        """
        Analyzes a raw script with Global Script Intelligence and AI Director,
        extracts entities and persistent character profiles, plans 17-attribute scene
        specifications, coordinates sound design, and strictly enforces animated visual direction.
        """
        pass
