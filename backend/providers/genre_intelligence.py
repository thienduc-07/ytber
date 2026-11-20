from typing import Dict, Any, List
from pydantic import BaseModel, Field

class GenreProfile(BaseModel):
    genre_id: str
    display_name: str
    description: str
    syllables_per_second: float
    min_scene_sec: float
    max_scene_sec: float
    narrative_stages: List[str]
    preferred_visuals: List[str]
    sound_ambience: str
    camera_style: str
    transition_style: str

GENRE_REGISTRY: Dict[str, GenreProfile] = {
    "horror": GenreProfile(
        genre_id="horror",
        display_name="Kinh Dị / Bí Ẩn (Horror & Mystery)",
        description="Không khí u ám, leo thang căng thẳng, khoảng lặng nghẹt thở, cao trào rùng rợn.",
        syllables_per_second=3.4,
        min_scene_sec=1.8,
        max_scene_sec=5.0,
        narrative_stages=["eerie_hook", "mystery_setup", "gradual_dread", "chilling_revelation", "terror_climax", "haunting_outro"],
        preferred_visuals=["archival", "parallax", "procedural", "photo"],
        sound_ambience="low_frequency_suspense_drone_and_creaks",
        camera_style="creeping slow push-in with heavy vignette",
        transition_style="slow_fade_to_black"
    ),
    "historical_doc": GenreProfile(
        genre_id="historical_doc",
        display_name="Phim Tài Liệu Lịch Sử (Historical Documentary)",
        description="Biên niên sử hào hùng, tư liệu lưu trữ, bản đồ lộ trình quân sự và nhân chứng lịch sử.",
        syllables_per_second=3.8,
        min_scene_sec=1.8,
        max_scene_sec=5.5,
        narrative_stages=["historic_hook", "chronological_setup", "conflict_escalation", "historic_turning_point", "triumph_or_tragedy", "historic_legacy"],
        preferred_visuals=["archival", "map", "parallax", "photo", "stock"],
        sound_ambience="cinematic_orchestral_strings_and_drums",
        camera_style="dramatic Ken Burns pan across archival photos",
        transition_style="crossfade_with_film_grain"
    ),
    "economics": GenreProfile(
        genre_id="economics",
        display_name="Kinh Tế & Tài Chính (Economics & Finance)",
        description="Số liệu sắc bén, biểu đồ trực quan, so sánh tăng trưởng vĩ mô và bối cảnh thị trường.",
        syllables_per_second=4.2,
        min_scene_sec=3.0,
        max_scene_sec=5.5,
        narrative_stages=["data_hook", "market_context", "key_metric_breakdown", "comparative_analysis", "economic_impact", "future_outlook"],
        preferred_visuals=["infographic", "svg", "stock", "photo"],
        sound_ambience="clean_minimal_tech_rhythm",
        camera_style="dynamic smooth camera slide with data callouts",
        transition_style="sharp_whip_pan"
    ),
    "science": GenreProfile(
        genre_id="science",
        display_name="Khoa Học & Công Nghệ (Science & Technology)",
        description="Giải thích cơ chế vật lý, nguyên lý cơ học, sơ đồ vector và mô phỏng hạt vi mô.",
        syllables_per_second=3.9,
        min_scene_sec=3.5,
        max_scene_sec=6.0,
        narrative_stages=["curiosity_hook", "fundamental_principle", "micro_mechanism", "real_world_experiment", "scientific_breakthrough", "key_takeaway"],
        preferred_visuals=["svg", "procedural", "infographic", "stock"],
        sound_ambience="synthesizer_wave_mechanics_ambience",
        camera_style="micro-focus zoom into blueprints",
        transition_style="digital_grid_dissolve"
    ),
    "education": GenreProfile(
        genre_id="education",
        display_name="Giáo Dục & Kiến Thức (Education & Explainer)",
        description="Hệ thống bài học dễ hiểu, danh sách gạch đầu dòng, minh họa sinh động và tóm tắt cốt lõi.",
        syllables_per_second=3.7,
        min_scene_sec=3.5,
        max_scene_sec=6.0,
        narrative_stages=["concept_hook", "problem_definition", "step_by_step_explanation", "practical_example", "common_mistake", "summary_card"],
        preferred_visuals=["infographic", "toon", "svg", "photo"],
        sound_ambience="warm_acoustic_learning_background",
        camera_style="centered presentation framing",
        transition_style="slide_left"
    ),
    "news": GenreProfile(
        genre_id="news",
        display_name="Thời Sự & Phân Tích Tin Tức (News & Current Affairs)",
        description="Nhịp độ dồn dập, sự kiện nóng, định vị địa lý và dữ kiện xác thực tức thì.",
        syllables_per_second=4.4,
        min_scene_sec=2.5,
        max_scene_sec=5.0,
        narrative_stages=["breaking_hook", "event_timeline", "geographic_location", "key_stakeholder_response", "immediate_consequence", "next_developments"],
        preferred_visuals=["stock", "map", "infographic", "photo"],
        sound_ambience="urgent_broadcast_pulse",
        camera_style="fast documentary handheld camera snap",
        transition_style="quick_cut"
    ),
    "biography": GenreProfile(
        genre_id="biography",
        display_name="Tiểu Sử Danh Nhân & Lịch Sử Đời Người (Biography)",
        description="Chân dung nhân vật 2.5D, cuộc đời thăng trầm, dấu mốc sự nghiệp và di sản để lại.",
        syllables_per_second=3.6,
        min_scene_sec=3.5,
        max_scene_sec=6.0,
        narrative_stages=["legacy_hook", "humble_beginnings", "trials_and_struggles", "pivotal_breakthrough", "monumental_achievement", "eternal_legacy"],
        preferred_visuals=["parallax", "archival", "photo", "stock"],
        sound_ambience="emotional_reflective_piano_and_strings",
        camera_style="intimate slow camera push to portrait face",
        transition_style="gentle_dissolve"
    ),
    "business": GenreProfile(
        genre_id="business",
        display_name="Kinh Doanh & Khởi Nghiệp (Business & Entrepreneurship)",
        description="Chiến lược kinh doanh, bài học từ các tập đoàn lớn, tăng trưởng doanh thu và định vị.",
        syllables_per_second=4.1,
        min_scene_sec=3.0,
        max_scene_sec=5.5,
        narrative_stages=["billion_dollar_hook", "market_opportunity", "disruptive_strategy", "execution_hurdles", "scale_and_revenue", "business_lesson"],
        preferred_visuals=["stock", "infographic", "parallax", "photo"],
        sound_ambience="modern_confident_corporate_drive",
        camera_style="sleek corporate panning",
        transition_style="smooth_motion_blur_whip"
    ),
    "crime": GenreProfile(
        genre_id="crime",
        display_name="Phá Án & Điều Tra Tội Phạm (Crime & Investigation)",
        description="Hồ sơ vụ án, lời khai mâu thuẫn, bản đồ hiện trường và quá trình truy bắt kẻ thủ ác.",
        syllables_per_second=3.4,
        min_scene_sec=3.5,
        max_scene_sec=6.5,
        narrative_stages=["crime_scene_hook", "evidence_discovery", "suspect_profile", "investigation_twist", "confrontation_and_arrest", "court_justice"],
        preferred_visuals=["archival", "map", "parallax", "photo"],
        sound_ambience="tense_sub_bass_pulse_and_sirens",
        camera_style="noir low-angle with searchlight sweep",
        transition_style="shutter_flash_cut"
    ),
    "general": GenreProfile(
        genre_id="general",
        display_name="Kể Chuyện Đa Năng (General Storytelling)",
        description="Cấu trúc 3 hồi kinh điển, cân bằng giữa hình ảnh trực quan và giọng kể lôi cuốn.",
        syllables_per_second=4.0,
        min_scene_sec=3.0,
        max_scene_sec=6.0,
        narrative_stages=["hook", "exposition", "rising_action", "climax", "falling_action", "resolution"],
        preferred_visuals=["photo", "stock", "infographic", "procedural", "parallax"],
        sound_ambience="balanced_ambient_cinematic_soundtrack",
        camera_style="adaptive smooth Ken Burns",
        transition_style="crossfade"
    ),
}

def get_genre_profile(genre_id: str) -> GenreProfile:
    clean_id = (genre_id or "general").lower().replace("-", "_")
    return GENRE_REGISTRY.get(clean_id, GENRE_REGISTRY["general"])
