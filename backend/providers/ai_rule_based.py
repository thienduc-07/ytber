import re
from typing import List
from backend.providers.ai_base import AIScriptProvider, ScriptAnalysisResult, ScenePlan

def count_vietnamese_syllables(text: str) -> int:
    clean = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
    words = clean.strip().split()
    return max(1, len(words))

class RuleBasedScriptProvider(AIScriptProvider):
    """
    Offline, deterministic, zero-API-key Vietnamese NLP Script Analyzer.
    Splits text into narrative documentary scenes, measures syllable pace,
    and intelligently assigns adaptive visual modalities.
    """
    
    def _determine_visual_method(self, text: str, scene_idx: int, total_scenes: int) -> tuple[str, str, List[str]]:
        t_lower = text.lower()
        
        # Opening scene priority: High-impact Parallax or Archival
        if scene_idx == 0:
            return (
                "parallax",
                "High-impact 2.5D portrait with dynamic camera push-in and dramatic focus",
                ["historical dramatic event", "documentary portrait"]
            )
        
        # Geographic / Location keywords
        if any(w in t_lower for w in ["tại", "ở", "thành phố", "đất nước", "quốc gia", "sông", "núi", "địa điểm", "manchester"]):
            return (
                "map",
                "Vector geographical visualization highlighting regional coordinates and movement",
                ["map topography historical route", "satellite geographic location"]
            )
            
        # Archival / Historical keywords
        if any(w in t_lower for w in ["năm", "thế kỷ", "lịch sử", "tư liệu", "quá khứ", "tài liệu", "1831"]):
            return (
                "archival",
                "Vintage archival photograph with warm sepia duotone grade and film grain",
                ["vintage historical archival document", "19th century archival photograph"]
            )
            
        # Scientific / Mechanism / Physics keywords
        if any(w in t_lower for w in ["nguyên lý", "khoa học", "cộng hưởng", "dao động", "tần số", "vật lý", "sóng"]):
            return (
                "svg",
                "Clean vector diagram sketching mechanical resonance frequency principles",
                ["physics resonance frequency diagram", "vector wave mechanics blueprint"]
            )
            
        # Numeric / Data / Comparison keywords
        if any(w in t_lower for w in ["số", "tỷ lệ", "phần trăm", "%", "lần", "triệu", "nghìn", "74", "30"]):
            return (
                "infographic",
                "Dynamic animated infographic counter illustrating statistical escalation",
                ["data comparison infographic", "statistics counter motion graphic"]
            )
            
        # Character / Action keywords
        if any(w in t_lower for w in ["lính", "người", "bước", "hành quân", "chạy", "nhảy", "quân đội"]):
            return (
                "toon",
                "Expressive 2D cartoon characters in dynamic motion with ink outlines",
                ["marching soldiers illustration", "historical figures cartoon vector"]
            )
            
        # Closing scene: Punchy Infographic or Stock outro
        if scene_idx == total_scenes - 1:
            return (
                "infographic",
                "Conclusion highlight card with lesson takeaway and callout framing",
                ["documentary conclusion", "quote highlight card"]
            )
            
        # Default fallback: Cinematic stock / photo
        return (
            "stock",
            "Color-graded cinematic contextual footage with Ken Burns smootherstep motion",
            ["cinematic documentary footage", "ambient contextual video"]
        )

    async def analyze_script(
        self,
        script_text: str,
        target_duration: int = 60,
        visual_style: str = "adaptive"
    ) -> ScriptAnalysisResult:
        # 1. Clean and split sentences (avoiding splitting on decimals like 7.09)
        raw_sentences = [s.strip() for s in re.split(r'(?<!\d)[.!?\n]+(?!\d)', script_text) if len(s.strip()) > 5]
        if not raw_sentences:
            raw_sentences = [script_text.strip() or "Nội dung video ngắn tiếng Việt."]

        total_syllables = sum(count_vietnamese_syllables(s) for s in raw_sentences)
        
        # 2. Standard Vietnamese short-form pace: 4.0 syllables per second
        target_syllables_per_sec = 4.0
        
        scenes: List[ScenePlan] = []
        current_frame = 0
        fps = 30
        
        # Distribute sentences across scenes
        for idx, sentence in enumerate(raw_sentences):
            s_count = count_vietnamese_syllables(sentence)
            duration = max(3.0, round(s_count / target_syllables_per_sec, 1))
            
            # Determine scene type
            if idx == 0:
                scene_type = "hook"
            elif idx == 1:
                scene_type = "setting"
            elif idx == len(raw_sentences) - 1:
                scene_type = "twist"
            elif "tại sao" in sentence.lower() or "nguyên nhân" in sentence.lower() or "bởi vì" in sentence.lower():
                scene_type = "mechanism"
            else:
                scene_type = "escalation"
                
            visual_method, visual_desc, keywords = self._determine_visual_method(sentence, idx, len(raw_sentences))
            
            scenes.append(ScenePlan(
                scene_order=idx + 1,
                scene_type=scene_type,
                narration_text=sentence,
                duration_seconds=duration,
                visual_method=visual_method,
                visual_description=visual_desc,
                suggested_asset_keywords=keywords
            ))
            
        total_calc_duration = sum(sc.duration_seconds for sc in scenes)
        
        # Extract title from first sentence
        first_clean = re.sub(r'[^\w\s]', '', raw_sentences[0])
        title_words = first_clean.split()[:7]
        title = " ".join(title_words).capitalize() if title_words else "Video Shorts Tiếng Việt"
        
        return ScriptAnalysisResult(
            title=title,
            estimated_syllables=total_syllables,
            estimated_duration_seconds=round(total_calc_duration, 1),
            hook_summary=raw_sentences[0][:100],
            scenes=scenes,
            ai_provider_used="rule-based-nlp-offline"
        )
