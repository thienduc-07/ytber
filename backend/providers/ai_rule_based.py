import re
import math
from typing import List, Tuple
from backend.providers.ai_base import (
    AIScriptProvider, ScriptAnalysisResult, ScenePlan, ChapterPlan,
    ResearchEntity, SoundDesignCue
)
from backend.providers.genre_intelligence import get_genre_profile, GenreProfile

def count_vietnamese_syllables(text: str) -> int:
    clean = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
    words = clean.strip().split()
    return max(1, len(words))

class RuleBasedScriptProvider(AIScriptProvider):
    """
    Offline, deterministic Vietnamese NLP Script & Genre Intelligence Engine.
    Supports 10 genres, short-form (9:16) & long-form (16:9), research entity extraction,
    and adaptive sound design without any external API keys or subscription costs.
    """

    def _extract_research_entities(self, text: str) -> List[ResearchEntity]:
        entities: List[ResearchEntity] = []
        seen = set()

        # 1. Historical Years
        year_matches = re.findall(r'\b(1[0-9]{3}|20[0-2][0-9])\b', text)
        for y in set(year_matches):
            if y not in seen:
                seen.add(y)
                entities.append(ResearchEntity(
                    name=f"Năm {y}",
                    entity_type="date",
                    context=f"Mốc thời gian lịch sử trong kịch bản: năm {y}",
                    search_query=f"history {y} archival"
                ))

        # 2. Key Vietnamese Locations & Historical Figures
        LOCATION_PATTERNS = [
            "Điện Biên Phủ", "Điện Biên", "Hà Nội", "Hồ Gươm", "Tây Bắc", "Sài Gòn",
            "Đà Nẵng", "Huế", "Việt Nam", "Manchester", "Broughton"
        ]
        for loc in LOCATION_PATTERNS:
            if loc.lower() in text.lower() and loc not in seen:
                seen.add(loc)
                entities.append(ResearchEntity(
                    name=loc,
                    entity_type="location",
                    context=f"Địa danh quan trọng xuất hiện trong nội dung: {loc}",
                    search_query=f"{loc} geography archival photography"
                ))

        FIGURE_PATTERNS = [
            "Võ Nguyên Giáp", "Hồ Chí Minh", "De Castries", "Trần Hưng Đạo", "Quang Trung"
        ]
        for fig in FIGURE_PATTERNS:
            if fig.lower() in text.lower() and fig not in seen:
                seen.add(fig)
                entities.append(ResearchEntity(
                    name=fig,
                    entity_type="person",
                    context=f"Nhân vật lịch sử / trọng tâm: {fig}",
                    search_query=f"{fig} historical portrait photograph"
                ))

        return entities

    def _determine_visual_method(
        self,
        text: str,
        scene_idx: int,
        total_scenes: int,
        profile: GenreProfile
    ) -> Tuple[str, str, List[str]]:
        t_lower = text.lower()

        # Genre-specific overrides
        if profile.genre_id == "horror":
            if scene_idx == 0:
                return (
                    "archival",
                    "U ám ma mị với tông màu phim cũ, ánh sáng leo lét và bóng tối sâu thẳm",
                    ["creepy eerie vintage abandoned house", "dark mysterious woods archival"]
                )
            if any(w in t_lower for w in ["tiếng", "bóng", "ma", "chết", "máu", "rùng rợn", "kỳ lạ", "biến mất"]):
                return (
                    "parallax",
                    "Hiệu ứng 2.5D đẩy chậm vào góc tối, tạo cảm giác bị rình rập trong bóng đêm",
                    ["dark horror silhouette ominous shadow", "scary abandoned hallway creepy"]
                )
            return (
                "procedural",
                "Hiệu ứng sương mù ma quái, nhiễu tĩnh điện hạt nhiễu âm thanh CRT",
                ["dark atmospheric mist fog", "ominous static dark texture"]
            )

        if profile.genre_id == "economics":
            # Specific industrial facilities, oil/energy, and physical assets
            if any(w in t_lower for w in ["dầu", "giá dầu", "xăng dầu", "năng lượng", "opec", "crude oil", "khai thác"]):
                return (
                    "photo",
                    "Cơ sở lọc hóa dầu công nghiệp quy mô lớn với các bồn chứa và giàn khoan ngoài khơi",
                    ["crude oil refinery", "oil barrels petroleum", "oil trading market", "petroleum production facility"]
                )
            if any(w in t_lower for w in ["cảng", "container", "vận tải", "chuỗi cung ứng", "logistics", "xuất khẩu", "nhập khẩu"]):
                return (
                    "photo",
                    "Cảng biển container quốc tế với cần cẩu xếp dỡ và tàu hàng siêu tải trọng",
                    ["container port cargo ship", "logistics freight shipping", "global supply chain terminal"]
                )
            if any(w in t_lower for w in ["ngân hàng", "lãi suất", "tiền tệ", "lạm phát", "fed", "ngân hàng trung ương"]):
                return (
                    "photo",
                    "Tòa nhà ngân hàng trung ương và sàn giao dịch tài chính với biểu đồ điện tử",
                    ["central bank building", "stock exchange trading floor", "financial banking treasury"]
                )
            if any(w in t_lower for w in ["nhà máy", "sản xuất", "chế tạo", "công nghiệp", "dây chuyền"]):
                return (
                    "photo",
                    "Dây chuyền sản xuất tự động hóa trong nhà máy công nghiệp hiện đại",
                    ["automated factory production line", "modern manufacturing facility", "industrial robot assembly"]
                )
            if any(w in t_lower for w in ["tỷ lệ", "phần trăm", "%", "tỷ usd", "doanh thu", "tăng trưởng", "gdp", "chỉ số"]):
                return (
                    "infographic",
                    "Biểu đồ số liệu động với bộ đếm tăng trưởng sắc nét, màu sắc tương phản cao",
                    ["economic growth chart", "financial stock market graph", "macroeconomic data analysis"]
                )
            if any(w in t_lower for w in ["fdi", "doanh nghiệp", "thị trường", "tập đoàn", "đầu tư"]):
                return (
                    "stock",
                    "Trung tâm tài chính hiện đại với các tòa nhà văn phòng và giới doanh nhân",
                    ["financial district skyscraper", "modern corporate business district"]
                )

        # Opening scene priority
        if scene_idx == 0:
            preferred = profile.preferred_visuals[0] if profile.preferred_visuals else "parallax"
            return (
                preferred,
                f"Cảnh mở màn ấn tượng phong cách {profile.display_name} với góc máy cận cảnh",
                ["historical dramatic event", "high impact cinematic scene"]
            )

        # Geographic / Location keywords
        if any(w in t_lower for w in ["tại", "ở", "thành phố", "đất nước", "quốc gia", "sông", "núi", "địa điểm", "tây bắc", "điện biên"]):
            return (
                "map",
                "Bản đồ vector định vị địa lý trực quan hóa lộ trình và địa hình thực địa",
                ["topographic route map terrain", "satellite geographic vector overview"]
            )

        # Archival / Historical keywords
        if any(w in t_lower for w in ["năm", "thế kỷ", "lịch sử", "tư liệu", "quá khứ", "tài liệu", "1954", "1831"]):
            return (
                "archival",
                "Ảnh tư liệu lịch sử đen trắng hoặc sepia với hạt nhiễu phim điện ảnh",
                ["vintage historical archival document", "1954 historical photograph archival"]
            )

        # Scientific / Mechanism / Physics keywords
        if any(w in t_lower for w in ["nguyên lý", "khoa học", "cộng hưởng", "dao động", "tần số", "vật lý", "sóng"]):
            return (
                "svg",
                "Bản vẽ vector cơ học hiển thị cơ chế dao động và sóng cộng hưởng",
                ["physics resonance frequency blueprint", "vector mechanical diagram"]
            )

        # Numeric / Data / Comparison keywords
        if any(w in t_lower for w in ["số", "tỷ lệ", "phần trăm", "%", "lần", "triệu", "nghìn", "kỷ lục"]):
            return (
                "infographic",
                "Đồ họa thông tin chuyển động hiển thị thông số so sánh quy mô",
                ["infographic comparison metrics", "statistics dynamic motion counter"]
            )

        # Closing scene
        if scene_idx == total_scenes - 1:
            return (
                "infographic",
                "Thẻ kết luận làm nổi bật thông điệp sâu sắc và lời kêu gọi hành động",
                ["documentary conclusion card", "inspirational takeaway highlight"]
            )

        # Default fallback from profile preferred visuals
        default_vis = profile.preferred_visuals[1] if len(profile.preferred_visuals) > 1 else "stock"
        return (
            default_vis,
            f"Thước phim bối cảnh điện ảnh sắc nét ({profile.display_name}) với chuyển động Ken Burns",
            ["cinematic documentary footage", "ambient context video"]
        )

    def _generate_sound_cues(self, scene_type: str, profile: GenreProfile) -> List[SoundDesignCue]:
        cues: List[SoundDesignCue] = []
        if profile.genre_id == "horror":
            if "hook" in scene_type or "climax" in scene_type:
                cues.append(SoundDesignCue(sfx_type="drone", description="Âm hưởng siêu trầm 35Hz kích thích cảm giác bất an", volume=0.35))
                cues.append(SoundDesignCue(sfx_type="impact", description="Tiếng va đập kim loại rùng rợn khi hé lộ chi tiết bí ẩn", volume=0.4))
            elif "mystery" in scene_type or "dread" in scene_type:
                cues.append(SoundDesignCue(sfx_type="ambience", description="Tiếng gió rít qua khe cửa và tiếng bước chân gỗ kẽo kẹt", volume=0.25))
            else:
                cues.append(SoundDesignCue(sfx_type="silence", description="Khoảng lặng nghẹt thở trước khi rơi vào cao trào", volume=0.0))
        elif profile.genre_id == "economics":
            cues.append(SoundDesignCue(sfx_type="whoosh", description="Âm thanh vút nhẹ hiện số liệu infographic", volume=0.2))
            cues.append(SoundDesignCue(sfx_type="ambience", description="Nhịp điệu điện tử tinh tế giữ độ rõ nét cho giọng đọc", volume=0.2))
        elif profile.genre_id == "historical_doc":
            cues.append(SoundDesignCue(sfx_type="ambience", description="Dàn nhạc giao hưởng trầm hùng với tiếng trống trận hào tráng", volume=0.25))
            if "climax" in scene_type or "triumph" in scene_type:
                cues.append(SoundDesignCue(sfx_type="impact", description="Tiếng chuông ngân vang đánh dấu chiến thắng lịch sử", volume=0.35))
        else:
            cues.append(SoundDesignCue(sfx_type="ambience", description="Nhạc nền ambient điện ảnh cân bằng", volume=0.25))
        return cues

    async def analyze_script(
        self,
        script_text: str,
        target_duration: int = 60,
        genre: str = "general",
        video_format: str = "short-form",
        visual_style: str = "adaptive"
    ) -> ScriptAnalysisResult:
        profile = get_genre_profile(genre)

        # 1. Clean and split sentences
        raw_sentences = [
            s.strip() for s in re.split(r'(?<!\d)[.!?\n]+(?!\d)', script_text)
            if len(s.strip()) > 5
        ]
        if not raw_sentences:
            raw_sentences = [script_text.strip() or "Nội dung video thuyết minh tiếng Việt chất lượng cao."]

        total_syllables = sum(count_vietnamese_syllables(s) for s in raw_sentences)
        syllables_per_sec = profile.syllables_per_second

        scenes: List[ScenePlan] = []
        stages = profile.narrative_stages

        # Distribute sentences across narrative stages
        for idx, sentence in enumerate(raw_sentences):
            s_count = count_vietnamese_syllables(sentence)
            calc_dur = max(profile.min_scene_sec, min(profile.max_scene_sec, round(s_count / syllables_per_sec, 1)))

            stage_idx = min(idx, len(stages) - 1)
            scene_type = stages[stage_idx]

            visual_method, visual_desc, keywords = self._determine_visual_method(
                sentence, idx, len(raw_sentences), profile
            )

            sound_cues = self._generate_sound_cues(scene_type, profile)

            scenes.append(ScenePlan(
                scene_id=f"scene_{idx+1:03d}",
                scene_order=idx + 1,
                chapter_order=(idx // 4) + 1 if video_format == "long-form" else 1,
                scene_type=scene_type,
                narration_text=sentence,
                duration_seconds=calc_dur,
                visual_method=visual_method,
                visual_description=visual_desc,
                suggested_asset_keywords=keywords,
                search_keywords=keywords,
                preferred_media_type="image",
                preferred_aspect_ratio="16:9" if video_format == "long-form" else "9:16",
                camera_direction=profile.camera_style,
                transition=profile.transition_style,
                transition_type=profile.transition_style,
                sound_design=sound_cues,
                source_references=[f"Nguồn tư liệu kiểm chứng cảnh {idx+1}"]
            ))

        total_calc_duration = sum(sc.duration_seconds for sc in scenes)

        # Extract title from first sentence
        first_clean = re.sub(r'[^\w\s]', '', raw_sentences[0])
        title_words = first_clean.split()[:7]
        title = " ".join(title_words).capitalize() if title_words else f"Video {profile.display_name}"

        # Extract Research Entities
        entities = self._extract_research_entities(script_text)

        # Long-form chapter orchestration
        chapters: List[ChapterPlan] = []
        aspect_ratio = "16:9" if video_format == "long-form" else "9:16"

        if video_format == "long-form":
            scenes_per_chapter = max(2, math.ceil(len(scenes) / 3))
            chapter_chunks = [scenes[i:i + scenes_per_chapter] for i in range(0, len(scenes), scenes_per_chapter)]

            for c_idx, chunk in enumerate(chapter_chunks):
                ch_dur = sum(s.duration_seconds for s in chunk)
                chapters.append(ChapterPlan(
                    chapter_order=c_idx + 1,
                    title=f"Chương {c_idx + 1}: {chunk[0].narration_text[:40]}...",
                    summary=f"Phát triển cốt truyện chương {c_idx + 1} với {len(chunk)} phân cảnh.",
                    estimated_duration_seconds=round(ch_dur, 1),
                    scene_count=len(chunk),
                    scenes=chunk
                ))
        else:
            chapters.append(ChapterPlan(
                chapter_order=1,
                title=title,
                summary=raw_sentences[0][:120],
                estimated_duration_seconds=round(total_calc_duration, 1),
                scene_count=len(scenes),
                scenes=scenes
            ))

        return ScriptAnalysisResult(
            title=title,
            genre=profile.genre_id,
            video_format=video_format,
            aspect_ratio=aspect_ratio,
            estimated_syllables=total_syllables,
            estimated_duration_seconds=round(total_calc_duration, 1),
            hook_summary=raw_sentences[0][:120],
            scenes=scenes,
            chapters=chapters,
            entities=entities,
            ai_provider_used="rule-based-genre-intelligence"
        )
