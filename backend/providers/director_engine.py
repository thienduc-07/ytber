import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from backend.providers.ai_base import (
    AIScriptProvider,
    ScriptAnalysisResult,
    ScenePlan,
    ChapterPlan,
    ResearchEntity,
    CharacterProfile,
    EnvironmentSpec,
    CameraDirective,
    AnimationDirective,
    SoundDesignCue
)
from backend.providers.genre_intelligence import GENRE_REGISTRY, GenreProfile

class TopicSemanticAnalysis(BaseModel):
    main_subject: str
    topic_category: str
    context_era: str
    narrative_structure: str
    emotional_tone: str
    target_audience: str
    key_entities: List[str]
    suggested_music_theme: str
    suggested_palette: List[str]

class AIDirectorEngine:
    """
    Content-Independent Script Intelligence & Reusable AI Director.
    Analyzes any submitted script or topic, distinguishes narration from visual storytelling,
    establishes persistent character registries for visual consistency,
    and produces structured 17-attribute production specifications for 100% animated video generation.
    """

    # Domain Knowledge Patterns for Automated Semantic Understanding
    HISTORICAL_TRIGGERS = [
        "chiến dịch", "điện biên phủ", "1954", "lịch sử", "kháng chiến", "tướng", "quân đội",
        "hiệp định", "chiến thắng", "quân sự", "đờ cát", "de castries", "pháo binh", "việt minh",
        "thế chiến", "triều đại", "vua", "trận đánh", "cách mạng", "hào hùng", "dân tộc"
    ]
    ECONOMIC_TRIGGERS = [
        "lạm phát", "kinh tế", "gdp", "lãi suất", "ngân hàng", "thị trường", "tài chính",
        "đầu tư", "fdi", "giá dầu", "cung ứng", "tiền tệ", "chứng khoán", "tăng trưởng",
        "doanh nghiệp", "thương mại", "nguồn vốn", "xuất khẩu", "nhập khẩu", "suy thoái"
    ]
    TECH_TRIGGERS = [
        "trí tuệ nhân tạo", "ai", "máy tính", "thuật toán", "công nghệ", "robot", "phần mềm",
        "bán dẫn", "vi mạch", "dữ liệu", "internet", "tự động hóa", "neural", "kỹ thuật số",
        "mạng lưới", "điện toán", "hacker", "an ninh mạng", "mô hình ngôn ngữ"
    ]
    SCIENCE_TRIGGERS = [
        "hệ mặt trời", "vũ trụ", "hành tinh", "sao hỏa", "trái đất", "mặt trời", "vật lý",
        "nguyên tử", "lỗ đen", "thiên văn", "quang phổ", "khối lượng", "trọng lực", "sinh học",
        "hóa học", "tế bào", "khí quyển", "bức xạ", "không gian"
    ]
    SOCIAL_TRIGGERS = [
        "môi trường", "biến đổi khí hậu", "ô nhiễm", "xã hội", "đô thị hóa", "rác thải",
        "năng lượng xanh", "giao thông", "dân số", "giáo dục", "sức khỏe", "cộng đồng",
        "bền vững", "bảo tồn", "tài nguyên"
    ]

    def analyze_topic_semantics(self, text: str, user_genre: Optional[str] = None) -> TopicSemanticAnalysis:
        """
        Extracts deep semantic metadata independently of specific templates.
        Identifies topic category, era, emotion, audience, and narrative structure.
        """
        text_lower = text.lower()

        # Score category matches
        scores = {
            "historical_doc": sum(1 for k in self.HISTORICAL_TRIGGERS if k in text_lower),
            "economics": sum(1 for k in self.ECONOMIC_TRIGGERS if k in text_lower),
            "technology": sum(1 for k in self.TECH_TRIGGERS if k in text_lower),
            "science": sum(1 for k in self.SCIENCE_TRIGGERS if k in text_lower),
            "social": sum(1 for k in self.SOCIAL_TRIGGERS if k in text_lower)
        }

        # Determine dominant category
        best_cat = max(scores, key=scores.get) if any(scores.values()) else (user_genre or "general")
        if user_genre and user_genre in GENRE_REGISTRY and scores.get(user_genre, 0) > 0:
            best_cat = user_genre

        # Extract Subject from first sentence or title tokens
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if len(s.strip()) > 5]
        first_sentence = sentences[0] if sentences else text[:60]
        words = first_sentence.split()
        subject_phrase = " ".join(words[:6]) if len(words) >= 6 else first_sentence

        if best_cat == "historical_doc":
            era = "Chiến tranh Đông Dương / Thế kỷ 20" if any(w in text_lower for w in ["điện biên", "1954", "pháp", "kháng chiến"]) else "Bối cảnh Lịch sử Hào hùng"
            tone = "Hào hùng, trang trọng, kịch tính và tôn vinh lòng quả cảm"
            audience = "Khán giả đại chúng yêu thích lịch sử và phim tài liệu"
            structure = "Tập kết lực lượng -> Diễn biến chiến dịch -> Đột phá bước ngoặt -> Toàn thắng hào hùng"
            music_theme = "cinematic_orchestral_heroic_march"
            palette = ["#2B1E14", "#465F32", "#E2453C", "#FFE2A0", "#110E1A"]
        elif best_cat == "economics":
            era = "Thời kỳ Kinh tế Toàn cầu & Tái cấu trúc Tài chính 2024+"
            tone = "Sắc bén, logic, dữ liệu trực quan và phân tích chuyên sâu"
            audience = "Nhà đầu tư, sinh viên kinh tế và khán giả quan tâm tài chính"
            structure = "Cú sốc thị trường -> Phân tích chỉ số vĩ mô -> Cơ chế tác động -> Dự báo tương lai"
            music_theme = "minimal_tech_electronic_pulse"
            palette = ["#0F172A", "#1E3A8A", "#0D9488", "#F59E0B", "#F8FAFC"]
        elif best_cat == "technology":
            era = "Kỷ nguyên Trí tuệ Nhân tạo & Cách mạng Công nghiệp 4.0"
            tone = "Hiện đại, kỳ ảo, tốc độ cao và đột phá khoa học"
            audience = "Cộng đồng công nghệ, lập trình viên và người đam mê đổi mới sáng tạo"
            structure = "Vấn đề nan giải -> Đột phá thuật toán -> Mô phỏng hoạt động -> Ứng dụng thực tiễn"
            music_theme = "futuristic_synthwave_cyber_arpeggio"
            palette = ["#0A0F1D", "#0284C7", "#6366F1", "#10B981", "#EC4899"]
        elif best_cat == "science":
            era = "Kỷ nguyên Khám phá Không gian & Vật lý Vũ trụ"
            tone = "Huyền bí, kỳ vĩ, truyền cảm hứng khám phá chân lý tự nhiên"
            audience = "Học sinh, sinh viên và người say mê thiên văn khoa học"
            structure = "Hiện tượng kỳ thú -> Nguyên lý vật lý -> Mô phỏng không gian -> Ý nghĩa vũ trụ"
            music_theme = "ethereal_ambient_space_drone"
            palette = ["#030712", "#1E1B4B", "#4338CA", "#06B6D4", "#FDF4FF"]
        else:
            era = "Thời đại Đương đại & Đời sống Xã hội"
            tone = "Chân thực, nhân văn, kích thích tư duy cộng đồng"
            audience = "Khán giả trẻ và cộng đồng xã hội"
            structure = "Thực trạng xã hội -> Nguyên nhân cốt lõi -> Tác động đời sống -> Giải pháp hành động"
            music_theme = "warm_acoustic_documentary_strings"
            palette = ["#18181B", "#27272A", "#3F3F46", "#10B981", "#F4F4F5"]

        return TopicSemanticAnalysis(
            main_subject=subject_phrase,
            topic_category=best_cat,
            context_era=era,
            narrative_structure=structure,
            emotional_tone=tone,
            target_audience=audience,
            key_entities=words[:10],
            suggested_music_theme=music_theme,
            suggested_palette=palette
        )

    def build_character_registry(
        self,
        category: str,
        script_text: str
    ) -> Dict[str, CharacterProfile]:
        """
        Creates persistent animated character rigs for visual consistency.
        Characters retain their unique identity, costume, and palette across scenes.
        """
        registry: Dict[str, CharacterProfile] = {}
        text_lower = script_text.lower()

        if category == "historical_doc":
            # Vietnamese Soldier Rig
            soldier = CharacterProfile(
                character_id="char_soldier_01",
                name="Chiến sĩ Giải phóng Quân",
                role="protagonist",
                body_proportions="stylized_cartoon",
                costume_description="Áo trấn thủ xanh lục quân đội, mũ nan bọc lưới ngụy trang gắn sao vàng, quấn xà cạp vải, dây đai lưng da",
                color_scheme=["#36522D", "#EBB991", "#8A5C36", "#FFD700", "#DC281E"],
                facial_features="Gương mặt hoạt họa biểu cảm, mắt to cương nghị, nụ cười kiên cường, đôi mày rậm",
                distinguishing_props=["cờ Quyết chiến Quyết thắng", "dây thừng kéo pháo", "ba lô con cóc"]
            )
            registry[soldier.character_id] = soldier

            # Military Commander / Hero
            commander = CharacterProfile(
                character_id="char_commander_01",
                name="Chỉ huy Chiến dịch",
                role="supporting",
                body_proportions="stylized_cartoon",
                costume_description="Quân phục đại lễ màu xanh ô-liu phẳng phiu, mũ kê-pi chỉ huy, phù hiệu cấp tướng",
                color_scheme=["#2A4023", "#EBB991", "#5C4033", "#FFDF00", "#1E293B"],
                facial_features="Ánh mắt điềm tĩnh, nếp nhăn suy tư chiến lược, phong thái uy nghiêm nhân hậu",
                distinguishing_props=["bản đồ chiến sự", "ống nhòm quân sự"]
            )
            registry[commander.character_id] = commander

        elif category == "economics":
            economist = CharacterProfile(
                character_id="char_economist_01",
                name="Chuyên gia Kinh tế",
                role="presenter",
                body_proportions="stylized_cartoon",
                costume_description="Âu phục hiện đại màu xanh navy lịch lãm, cà vạt màu hổ phách, giày da bóng",
                color_scheme=["#1E293B", "#38BDF8", "#F59E0B", "#E2E8F0", "#0F172A"],
                facial_features="Kính cận gọng tròn thông minh, nụ cười tự tin, cử chỉ tay linh hoạt diễn giải số liệu",
                distinguishing_props=["máy tính bảng phân tích", "biểu đồ kỹ thuật số holo"]
            )
            registry[economist.character_id] = economist

        elif category == "technology":
            tech_avatar = CharacterProfile(
                character_id="char_engineer_01",
                name="Kỹ sư Trí tuệ Nhân tạo & Robot Trợ lý",
                role="protagonist",
                body_proportions="stylized_cartoon",
                costume_description="Áo hoodie phong cách techwear màu than chì có họa tiết mạch phát sáng neon, tai nghe kiểm âm",
                color_scheme=["#0F172A", "#06B6D4", "#A855F7", "#F8FAFC", "#10B981"],
                facial_features="Ánh mắt tò mò nhạy bén, biểu cảm ngạc nhiên trước phát kiến công nghệ mới",
                distinguishing_props=["giao diện tương tác không gian ba chiều", "chú robot mini trợ thủ"]
            )
            registry[tech_avatar.character_id] = tech_avatar

        elif category == "science":
            astronomer = CharacterProfile(
                character_id="char_scientist_01",
                name="Nhà Thiên văn Khám phá",
                role="protagonist",
                body_proportions="stylized_cartoon",
                costume_description="Áo phi hành thám hiểm hiện đại màu trắng bạc phối viền xanh lam thẫm, găng tay cơ học",
                color_scheme=["#F8FAFC", "#2563EB", "#7C3AED", "#06B6D4", "#030712"],
                facial_features="Mắt sáng ngời nhìn vào kính thiên văn, nụ cười say mê chân lý",
                distinguishing_props=["kính thiên văn quang học", "mô hình quỹ đạo hành tinh"]
            )
            registry[astronomer.character_id] = astronomer

        else:
            presenter = CharacterProfile(
                character_id="char_narrator_01",
                name="Người dẫn chuyện Thông thái",
                role="presenter",
                body_proportions="stylized_cartoon",
                costume_description="Trang phục áo khoác thường nhật trẻ trung năng động màu cam đất và quần jean",
                color_scheme=["#EA580C", "#3B82F6", "#F3F4F6", "#1F2937", "#10B981"],
                facial_features="Biểu cảm thân thiện gần gũi, đôi mắt biết nói thu hút người xem",
                distinguishing_props=["sổ tay ghi chép", "micro cổ áo"]
            )
            registry[presenter.character_id] = presenter

        return registry

    def direct_scene_production(
        self,
        scene_idx: int,
        total_scenes: int,
        sentence: str,
        semantics: TopicSemanticAnalysis,
        characters: Dict[str, CharacterProfile],
        genre_prof: GenreProfile
    ) -> ScenePlan:
        """
        AI Director Core: Synthesizes narration into visual storytelling,
        generating a structured 17-attribute production specification.
        Enforces 100% animated visual techniques (NO real-life photos).
        """
        # Determine narrative purpose based on position
        if scene_idx == 1:
            purpose = "hook_and_establishing_crisis"
            scene_type = "hook"
        elif scene_idx == total_scenes:
            purpose = "climax_resolution_and_legacy"
            scene_type = "resolution"
        elif scene_idx == total_scenes - 1:
            purpose = "turning_point_and_breakthrough"
            scene_type = "climax"
        else:
            purpose = f"narrative_development_stage_{scene_idx}"
            scene_type = "escalation"

        cat = semantics.topic_category
        first_char = list(characters.values())[0] if characters else None
        char_name = first_char.name if first_char else "Nhân vật hoạt họa"

        # Determine Environment, Camera, Animation & Sound based on semantic analysis
        if cat == "historical_doc":
            if scene_idx == 1:
                env = EnvironmentSpec(
                    setting_name="Thung lũng Điện Biên Phủ từ trên cao",
                    environment_type="mountain_battlefield",
                    time_of_day="sunset_golden",
                    weather_particles="smoke_embers",
                    primary_colors=semantics.suggested_palette
                )
                vis_desc = f"Toàn cảnh hoạt họa 2.5D: Thung lũng Điện Biên mờ sương, các cao điểm quân sự cách điệu, từng đoàn chiến sĩ hoạt hình hành quân trong hoàng hôn rực lửa."
                char_actions = ["march", "stand_vigilant"]
                props = ["ba lô con cóc", "ngọn đồi A1 cách điệu"]
                camera_angle = "high_angle_overview"
                camera_mov = "slow_push_in"
                anim_instr = AnimationDirective(character_action="march", object_action="particle_float", parallax_enabled=True, motion_intensity=0.85)
                lighting = "dramatic_golden_sunset_rim"
                vis_method = "toon"
                music_dir = "cinematic_heroic_drums_and_brass_intro"
                sfx_cues = [
                    SoundDesignCue(sfx_id="sfx_whoosh_01", sfx_type="whoosh", description="Âm thanh gió rít qua sườn đồi mở màn", start_time_offset_ms=0, volume=0.4),
                    SoundDesignCue(sfx_id="sfx_march_01", sfx_type="footsteps", description="Tiếng bước chân hành quân nhịp nhàng trên sỏi", start_time_offset_ms=500, volume=0.35)
                ]
            elif scene_idx == total_scenes:
                env = EnvironmentSpec(
                    setting_name="Nóc hầm De Castries toàn thắng",
                    environment_type="mountain_battlefield",
                    time_of_day="day",
                    weather_particles="clear",
                    primary_colors=["#DC281E", "#FFD700", "#36522D", "#87CEEB", "#FFFFFF"]
                )
                vis_desc = f"Chiến sĩ hoạt hình {char_name} phất cao lá cờ 'Quyết chiến Quyết thắng' đỏ thắm sao vàng trên nóc hầm chiến bại De Castries, ánh dương bừng sáng hào hùng."
                char_actions = ["cheer", "wave_flag"]
                props = ["lá cờ Quyết chiến Quyết thắng bay phần phật", "nóc hầm chỉ huy"]
                camera_angle = "low_angle_heroic"
                camera_mov = "tracking"
                anim_instr = AnimationDirective(character_action="cheer", object_action="flag_wave", parallax_enabled=True, motion_intensity=1.0)
                lighting = "bright_triumphant_daylight"
                vis_method = "toon"
                music_dir = "grand_orchestral_victory_anthem"
                sfx_cues = [
                    SoundDesignCue(sfx_id="sfx_flag_01", sfx_type="whoosh", description="Tiếng cờ bay phần phật trong gió", start_time_offset_ms=100, volume=0.5),
                    SoundDesignCue(sfx_id="sfx_cheer_01", sfx_type="cheer", description="Tiếng reo hò chiến thắng vang dội núi rừng", start_time_offset_ms=800, volume=0.45)
                ]
            else:
                env = EnvironmentSpec(
                    setting_name="Dốc núi hiểm trở kéo pháo",
                    environment_type="mountain_battlefield",
                    time_of_day="night_moonlight",
                    weather_particles="fog_mist",
                    primary_colors=["#111827", "#1F2937", "#374151", "#FFD700", "#DC281E"]
                )
                vis_desc = f"Hàng dài chiến sĩ hoạt họa gồng mình kéo khẩu đại pháo nặng hàng tấn qua đèo dốc đá cheo leo dưới ánh trăng, dây thừng căng siết thể hiện ý chí gang thép."
                char_actions = ["pull_cannon", "effort_stride"]
                props = ["khẩu đại pháo dã chiến", "dây thừng kéo pháo"]
                camera_angle = "eye_level"
                camera_mov = "pan_right"
                anim_instr = AnimationDirective(character_action="pull_cannon", object_action="cannon_fire", parallax_enabled=True, motion_intensity=0.9)
                lighting = "moody_contrast_moonlight"
                vis_method = "toon"
                music_dir = "heavy_tension_percussion_march"
                sfx_cues = [
                    SoundDesignCue(sfx_id="sfx_strain_01", sfx_type="impact", description="Tiếng bánh pháo nghiến trên đá và tiếng hò dô kéo pháo", start_time_offset_ms=200, volume=0.4)
                ]

        elif cat == "economics":
            if scene_idx == 1:
                env = EnvironmentSpec(
                    setting_name="Sàn giao dịch kinh tế toàn cầu",
                    environment_type="trading_floor",
                    time_of_day="day",
                    weather_particles="data_stream",
                    primary_colors=semantics.suggested_palette
                )
                vis_desc = f"Minh họa hoạt họa {char_name} đứng trước bức tường số liệu điện tử; biểu đồ đường giá dầu và lạm phát màu đỏ rực nhảy vọt tạo hiệu ứng cảnh báo."
                char_actions = ["point_gesture", "analyze_chart"]
                props = ["màn hình biểu đồ 3D", "chỉ số lạm phát nhấp nháy"]
                camera_angle = "eye_level"
                camera_mov = "slow_push_in"
                anim_instr = AnimationDirective(character_action="point_gesture", object_action="chart_grow", parallax_enabled=True, motion_intensity=0.8)
                lighting = "cool_futuristic_fluorescent"
                vis_method = "infographic"
                music_dir = "fast_paced_analytical_synth_pulse"
                sfx_cues = [
                    SoundDesignCue(sfx_id="sfx_impact_01", sfx_type="impact", description="Tiếng chuông mở sàn giao dịch tài chính", start_time_offset_ms=0, volume=0.4),
                    SoundDesignCue(sfx_id="sfx_chart_01", sfx_type="mechanical", description="Tiếng bíp bíp số liệu nhảy liên tục", start_time_offset_ms=400, volume=0.3)
                ]
            else:
                env = EnvironmentSpec(
                    setting_name="Trung tâm logistics cảng biển và chuỗi cung ứng thông minh",
                    environment_type="abstract_space",
                    time_of_day="sunset_golden",
                    weather_particles="clear",
                    primary_colors=["#0F172A", "#0284C7", "#10B981", "#F59E0B", "#F8FAFC"]
                )
                vis_desc = f"Mô hình đồ họa vector hoạt hình: Tàu container cách điệu di chuyển dọc luồng hàng hải, các container hàng hóa xếp tầng nhảy theo nhịp tăng trưởng GDP."
                char_actions = ["present_data"]
                props = ["tàu container hoạt hình", "cột tăng trưởng GDP vươn cao"]
                camera_angle = "high_angle_overview"
                camera_mov = "dynamic_zoom"
                anim_instr = AnimationDirective(character_action="present_data", object_action="chart_grow", parallax_enabled=True, motion_intensity=0.85)
                lighting = "clean_warm_amber_glow"
                vis_method = "infographic"
                music_dir = "inspirational_modern_corporate_tempo"
                sfx_cues = [
                    SoundDesignCue(sfx_id="sfx_whoosh_02", sfx_type="whoosh", description="Âm thanh vút bay của luồng hàng hải", start_time_offset_ms=100, volume=0.35),
                    SoundDesignCue(sfx_id="sfx_coin_01", sfx_type="coin", description="Tiếng keng kim loại của dòng vốn giải ngân", start_time_offset_ms=800, volume=0.3)
                ]

        elif cat == "technology":
            env = EnvironmentSpec(
                setting_name="Trung tâm nghiên cứu Trí tuệ Nhân tạo & Mạng nơ-ron",
                environment_type="interior_lab",
                time_of_day="night_moonlight",
                weather_particles="data_stream",
                primary_colors=semantics.suggested_palette
            )
            vis_desc = f"Nhân vật hoạt họa {char_name} thao tác trên không gian ba chiều: Các mạng nơ-ron phát sáng lấp lánh kết nối với chip bán dẫn và robot tự hành."
            char_actions = ["point_gesture", "interact_hologram"]
            props = ["mạng nơ-ron đa tầng phát sáng", "chip vi xử lý bán dẫn 3nm"]
            camera_angle = "eye_level"
            camera_mov = "slow_push_in"
            anim_instr = AnimationDirective(character_action="point_gesture", object_action="particle_float", parallax_enabled=True, motion_intensity=0.8)
            lighting = "cyber_neon_glow_cyan_and_violet"
            vis_method = "procedural"
            music_dir = "ambient_electronic_glitch_cyber_beat"
            sfx_cues = [
                SoundDesignCue(sfx_id="sfx_tech_01", sfx_type="mechanical", description="Tiếng xung điện tử truyền dữ liệu qua mạng nơ-ron", start_time_offset_ms=100, volume=0.35)
            ]

        elif cat == "science":
            env = EnvironmentSpec(
                setting_name="Không gian Vũ trụ & Quỹ đạo Hệ Mặt Trời",
                environment_type="abstract_space",
                time_of_day="night_moonlight",
                weather_particles="stars",
                primary_colors=semantics.suggested_palette
            )
            vis_desc = f"Mô phỏng đồ họa hoạt hình vũ trụ: Mặt Trời rực rỡ ở trung tâm với các hành tinh quay quanh theo quỹ đạo phát sáng, phi thuyền thám hiểm lướt qua màn hình."
            char_actions = ["stand_wonder", "observe_cosmos"]
            props = ["các hành tinh hoạt họa", "phi thuyền không gian"]
            camera_angle = "top_down_map"
            camera_mov = "tracking"
            anim_instr = AnimationDirective(character_action="stand", object_action="particle_float", parallax_enabled=True, motion_intensity=0.7)
            lighting = "deep_cosmic_starlight"
            vis_method = "procedural"
            music_dir = "deep_space_cosmic_orchestral_strings"
            sfx_cues = [
                SoundDesignCue(sfx_id="sfx_space_01", sfx_type="drone", description="Tiếng ngân vang trầm ấm của không gian vũ trụ", start_time_offset_ms=0, volume=0.4)
            ]

        else:
            env = EnvironmentSpec(
                setting_name="Không gian Đô thị Xanh Bền vững",
                environment_type="outdoor_nature",
                time_of_day="day",
                weather_particles="clear",
                primary_colors=semantics.suggested_palette
            )
            vis_desc = f"Nhân vật hoạt họa {char_name} đứng trước bức tranh thành phố sinh thái hiện đại: Tuabin gió quay đều, cây xanh trên mái nhà và dòng người tấp nập."
            char_actions = ["present_data", "walk"]
            props = ["tuabin gió hoạt hình", "tấm pin mặt trời cách điệu"]
            camera_angle = "eye_level"
            camera_mov = "slow_push_in"
            anim_instr = AnimationDirective(character_action="walk", object_action="particle_float", parallax_enabled=True, motion_intensity=0.75)
            lighting = "soft_natural_sunlight"
            vis_method = "toon"
            music_dir = "warm_acoustic_positive_storytelling"
            sfx_cues = [
                SoundDesignCue(sfx_id="sfx_wind_01", sfx_type="ambience", description="Tiếng gió thổi qua cánh đồng tuabin sinh thái", start_time_offset_ms=0, volume=0.3)
            ]

        # Calculate Duration from Vietnamese syllables
        # 1 Vietnamese syllable ~ 3.6 syllables per second
        words = sentence.split()
        syllable_count = len(words)
        rate = genre_prof.syllables_per_second if genre_prof else 3.8
        duration = max(genre_prof.min_scene_sec if genre_prof else 3.5, round(syllable_count / rate, 1))

        # Assign concrete animated search keywords (FOR VECTOR/ILLUSTRATION ONLY)
        kw_domain = f"{cat} animated vector illustration"
        keywords = [
            f"{cat} cartoon 2d illustration",
            f"{cat} animated infographic vector",
            f"{cat} stylized cartoon character vector clipart",
            f"{cat} flat design cartoon vector background"
        ]

        return ScenePlan(
            scene_id=f"sc_{scene_idx:02d}",
            scene_order=scene_idx,
            narrative_purpose=purpose,
            scene_type=scene_type,
            narration_text=sentence,
            narration=sentence,
            duration_seconds=duration,
            estimated_duration=duration,
            visual_method=vis_method,
            visual_description=vis_desc,
            environment=env,
            character_descriptions=[f"{c.name}: {c.costume_description}" for c in characters.values()],
            character_poses=char_actions,
            character_poses_actions=char_actions,
            props=props,
            camera_angle=camera_angle,
            camera_movement=camera_mov,
            camera_direction=camera_mov,
            animation_instructions=anim_instr,
            lighting=lighting,
            color_palette=semantics.suggested_palette,
            transition="crossfade" if scene_idx < total_scenes else "fade_to_black",
            transition_type="crossfade" if scene_idx < total_scenes else "fade_to_black",
            music_direction=music_dir,
            sound_design=sfx_cues,
            sound_effects=sfx_cues,
            subtitles_json=[],
            suggested_asset_keywords=keywords,
            search_keywords=keywords,
            preferred_media_type="image",
            preferred_aspect_ratio="9:16",
            source_references=[]
        )

    def analyze_and_direct(
        self,
        script_text: str,
        target_duration: int = 60,
        genre: Optional[str] = None,
        video_format: str = "short-form",
        visual_style: str = "2d_cartoon"
    ) -> ScriptAnalysisResult:
        """
        End-to-End Orchestrator:
        Takes any raw script text, analyzes semantics, establishes consistent character rigs,
        and directs each scene with full 17-attribute production specs.
        """
        clean_text = script_text.strip()
        if not clean_text:
            raise ValueError("Script text cannot be empty")

        # 1. Semantic Topic Understanding
        semantics = self.analyze_topic_semantics(clean_text, genre)
        matched_genre = semantics.topic_category
        genre_prof = GENRE_REGISTRY.get(matched_genre, GENRE_REGISTRY["education"])

        # 2. Consistent Character Registry
        characters = self.build_character_registry(matched_genre, clean_text)

        # 3. Sentence Splitting & Boundaries
        raw_sentences = [s.strip() for s in re.split(r'[.!?\n]+', clean_text) if len(s.strip()) > 8]
        if not raw_sentences:
            raw_sentences = [clean_text]

        # Combine very short sentences if needed to maintain optimal scene pacing
        scenes_text = []
        cur_buf = []
        for s in raw_sentences:
            cur_buf.append(s)
            combined = " ".join(cur_buf)
            if len(combined.split()) >= 12 or len(scenes_text) >= 5:
                scenes_text.append(combined)
                cur_buf = []
        if cur_buf:
            if scenes_text:
                scenes_text[-1] += " " + " ".join(cur_buf)
            else:
                scenes_text.append(" ".join(cur_buf))

        # Enforce minimum 3 scenes and maximum 8 scenes for shorts
        if len(scenes_text) < 3 and len(raw_sentences) >= 3:
            scenes_text = raw_sentences[:6]

        # 4. Direct Scenes
        scenes: List[ScenePlan] = []
        total_syllables = 0
        total_duration = 0.0

        for idx, s_text in enumerate(scenes_text, start=1):
            sc_plan = self.direct_scene_production(
                scene_idx=idx,
                total_scenes=len(scenes_text),
                sentence=s_text,
                semantics=semantics,
                characters=characters,
                genre_prof=genre_prof
            )
            scenes.append(sc_plan)
            total_syllables += len(s_text.split())
            total_duration += sc_plan.duration_seconds

        # 5. Extract Named Entities
        entities: List[ResearchEntity] = []
        for word in clean_text.split():
            if word and word[0].isupper() and len(word) > 2 and word not in ["Tuy", "Nhưng", "Trong", "Và", "Các", "Những", "Được"]:
                if not any(e.name == word for e in entities):
                    entities.append(ResearchEntity(
                        name=word,
                        entity_type="concept_or_location",
                        context=f"Thực thể được đề cập trong kịch bản {semantics.main_subject}",
                        search_query=f"{word} cartoon illustration"
                    ))
            if len(entities) >= 6:
                break

        title = semantics.main_subject
        aspect_ratio = "9:16" if video_format == "short-form" else "16:9"

        return ScriptAnalysisResult(
            title=title,
            genre=matched_genre,
            video_format=video_format,
            aspect_ratio=aspect_ratio,
            main_subject=semantics.main_subject,
            topic_category=semantics.topic_category,
            context_era=semantics.context_era,
            narrative_arc=semantics.narrative_structure,
            emotional_tone=semantics.emotional_tone,
            target_audience=semantics.target_audience,
            visual_style_preset=visual_style,
            character_registry=characters,
            estimated_syllables=total_syllables,
            estimated_duration_seconds=round(total_duration, 1),
            hook_summary=f"Cảnh mở màn thiết lập bối cảnh: {scenes[0].visual_description[:80]}...",
            scenes=scenes,
            chapters=[],
            entities=entities,
            ai_provider_used="AIDirectorEngine"
        )

    def generate_film_blueprint(
        self,
        script_text: str,
        genre: Optional[str] = None,
        video_format: str = "short-form",
        visual_style: str = "2d_cartoon"
    ) -> Dict[str, Any]:
        """
        Produces a rich, zero-touch Film Blueprint following dramatic storytelling principles:
        1. 5-part structure:
           - Hook (3-5s): Gripping narrative hook, high emotional stake, visual & audio burst.
           - Setup: World context, characters, thematic premise.
           - Conflict: Rising stakes, challenge, movement.
           - Climax: Peak tension, heroic/decisive moment, high sound intensity.
           - Resolution: Impact, conclusion, legacy & subscription call-to-action.
        2. Character Bible: Detailed character rig specs for visual and narrative consistency.
        3. Environment Bible: Specific physical settings, lighting, color palette, weather particles.
        4. Structured scene breakdown with visual search queries, visual method, camera movements, and audio cues.
        """
        analysis = self.analyze_and_direct(
            script_text=script_text,
            genre=genre,
            video_format=video_format,
            visual_style=visual_style
        )

        char_bible = {
            c_id: {
                "name": c.name,
                "role": c.role,
                "costume": c.costume_description,
                "facial_features": c.facial_features,
                "color_scheme": c.color_scheme,
                "props": c.distinguishing_props
            }
            for c_id, c in analysis.character_registry.items()
        }

        env_bible = {
            "primary_era": analysis.context_era,
            "narrative_arc": analysis.narrative_arc,
            "palette": analysis.scenes[0].color_palette if analysis.scenes else ["#1E293B", "#38BDF8"],
            "emotional_tone": analysis.emotional_tone,
            "target_audience": analysis.target_audience
        }

        dramatic_stages = ["hook", "setup", "conflict", "climax", "resolution"]
        total_sc = len(analysis.scenes)
        blueprint_scenes = []

        for idx, sc in enumerate(analysis.scenes):
            if total_sc <= 5:
                stage = dramatic_stages[idx] if idx < len(dramatic_stages) else "resolution"
            else:
                if idx == 0:
                    stage = "hook"
                elif idx == 1:
                    stage = "setup"
                elif idx == total_sc - 1:
                    stage = "resolution"
                elif idx == total_sc - 2:
                    stage = "climax"
                else:
                    stage = "conflict"

            subject_token = analysis.main_subject[:30]
            clean_sentence = re.sub(r'[^\w\s]', '', sc.narration_text)
            kw_tokens = [w for w in clean_sentence.split() if len(w) > 3][:4]
            visual_query = f"{subject_token} {' '.join(kw_tokens)}".strip()

            blueprint_scenes.append({
                "scene_order": sc.scene_order,
                "scene_id": sc.scene_id,
                "scene_type": stage,
                "narrative_stage": stage,
                "narration_text": sc.narration_text,
                "estimated_duration": sc.duration_seconds,
                "visual_query": visual_query,
                "visual_method": sc.visual_method,
                "visual_description": sc.visual_description,
                "camera_direction": sc.camera_movement,
                "transition": sc.transition,
                "environment_setting": sc.environment.setting_name if sc.environment else "studio",
                "ambient_profile": sc.environment.environment_type if sc.environment else "generic_ambient",
                "sfx_cues": [
                    {
                        "sfx_id": s.sfx_id,
                        "sfx_type": s.sfx_type,
                        "description": s.description,
                        "offset_ms": s.start_time_offset_ms,
                        "volume": s.volume
                    }
                    for s in (sc.sound_design or [])
                ],
                "suggested_asset_keywords": sc.suggested_asset_keywords
            })

        return {
            "title": analysis.title,
            "genre": analysis.genre,
            "video_format": analysis.video_format,
            "aspect_ratio": analysis.aspect_ratio,
            "estimated_duration_seconds": analysis.estimated_duration_seconds,
            "character_bible": char_bible,
            "environment_bible": env_bible,
            "dramatic_arc": analysis.narrative_arc,
            "scenes": blueprint_scenes
        }
