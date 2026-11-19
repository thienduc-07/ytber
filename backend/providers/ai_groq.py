import json
import httpx
from typing import Optional
from backend.core.config import settings
from backend.providers.ai_base import AIScriptProvider, ScriptAnalysisResult, ScenePlan
from backend.providers.ai_rule_based import RuleBasedScriptProvider

SYSTEM_PROMPT = """Bạn là Chuyên gia Biên kịch và Đạo diễn Hình ảnh AI hàng đầu cho video ngắn (YouTube Shorts, TikTok 9:16).
Nhiệm vụ của bạn là phân tích kịch bản tiếng Việt đầu vào, bẻ nhỏ thành các cảnh (scenes) từ 3.0 đến 6.0 giây, và chỉ định phương pháp hình ảnh phù hợp nhất (Adaptive Visual).

Các phương pháp hình ảnh được hỗ trợ:
- 'photo': Ảnh tư liệu tĩnh sắc nét với chuyển động Ken Burns pan/zoom.
- 'stock': Video tư liệu B-roll chất lượng cao.
- 'archival': Tài liệu lịch sử, báo cũ, ảnh cổ với tông màu sepia/duotone.
- 'map': Bản đồ địa lý vector trực quan hóa lộ trình, tọa độ.
- 'svg': Bản vẽ vector chuyển động giải thích cơ chế khoa học/vật lý.
- 'infographic': Đồ họa thông tin chuyển động, số liệu đếm, so sánh.
- 'procedural': Hiệu ứng đồ họa hạt Canvas2D, sóng xung kích, tia sét.
- 'parallax': Ảnh 2.5D tách lớp chiều sâu tiền cảnh/hậu cảnh.
- 'toon': Nhân vật hoạt hình 2D vẽ nét mực vector phong cách cartoon.

BẮT BUỘC trả về đúng định dạng JSON tuân thủ cấu trúc sau:
{
  "title": "Tiêu đề ngắn gọn hấp dẫn (dưới 8 chữ)",
  "hook_summary": "Tóm tắt câu mở đầu gây tò mò (1 câu)",
  "scenes": [
    {
      "scene_order": 1,
      "scene_type": "hook", // hook, setting, escalation, mechanism, twist
      "narration_text": "Câu thoại tiếng Việt cho cảnh này",
      "duration_seconds": 4.5, // từ 3.0 đến 6.0
      "visual_method": "parallax", // một trong 9 loại trên
      "visual_description": "Mô tả chi tiết góc quay, chuyển động và đối tượng",
      "suggested_asset_keywords": ["từ khóa 1 tiếng Anh/Việt để tìm ảnh", "từ khóa 2"]
    }
  ]
}
"""

class GroqScriptProvider(AIScriptProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.fallback = RuleBasedScriptProvider()

    async def analyze_script(
        self,
        script_text: str,
        target_duration: int = 60,
        visual_style: str = "adaptive"
    ) -> ScriptAnalysisResult:
        if not self.api_key or self.api_key.startswith("placeholder-"):
            # Fall back seamlessly to rule-based engine
            return await self.fallback.analyze_script(script_text, target_duration, visual_style)
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        user_prompt = f"Kịch bản đầu vào:\n\"\"\"\n{script_text}\n\"\"\"\nThời lượng mục tiêu: {target_duration} giây. Phong cách: {visual_style}."
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "max_tokens": 2048
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    return await self.fallback.analyze_script(script_text, target_duration, visual_style)
                
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                scenes = [
                    ScenePlan(
                        scene_order=s.get("scene_order", i + 1),
                        scene_type=s.get("scene_type", "narrative"),
                        narration_text=s.get("narration_text", ""),
                        duration_seconds=float(s.get("duration_seconds", 4.0)),
                        visual_method=s.get("visual_method", "photo"),
                        visual_description=s.get("visual_description", ""),
                        suggested_asset_keywords=s.get("suggested_asset_keywords", ["history"])
                    )
                    for i, s in enumerate(parsed.get("scenes", []))
                ]
                
                total_duration = sum(s.duration_seconds for s in scenes)
                
                return ScriptAnalysisResult(
                    title=parsed.get("title", "Video Shorts Tiếng Việt"),
                    estimated_syllables=len(script_text.split()),
                    estimated_duration_seconds=round(total_duration, 1),
                    hook_summary=parsed.get("hook_summary", ""),
                    scenes=scenes,
                    ai_provider_used="groq-llama-3.3"
                )
        except Exception:
            return await self.fallback.analyze_script(script_text, target_duration, visual_style)
