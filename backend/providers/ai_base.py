from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ScenePlan(BaseModel):
    scene_order: int
    scene_type: str = Field(description="hook, setting, escalation, mechanism, climax, twist")
    narration_text: str
    duration_seconds: float
    visual_method: str = Field(description="photo, stock, archival, map, svg, infographic, procedural, parallax, toon")
    visual_description: str
    suggested_asset_keywords: List[str]

class ScriptAnalysisResult(BaseModel):
    title: str
    estimated_syllables: int
    estimated_duration_seconds: float
    hook_summary: str
    scenes: List[ScenePlan]
    ai_provider_used: str

class AIScriptProvider(ABC):
    @abstractmethod
    async def analyze_script(
        self,
        script_text: str,
        target_duration: int = 60,
        visual_style: str = "adaptive"
    ) -> ScriptAnalysisResult:
        """
        Analyzes a raw Vietnamese script, breaks it into structured scenes,
        estimates durations based on Vietnamese speech pacing, and assigns visual methods.
        """
        pass
