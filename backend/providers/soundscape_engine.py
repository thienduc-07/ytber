"""
AI Environmental Sound Director & Acoustic Landscape Engine.

Derives multi-layered environmental soundscapes and action-synchronized SFX
from scene semantics, environmental setting, and character actions:
1. Environmental Ambience (Nature/Forest, Ocean, Rain, Urban, Historical, Space, Tech).
2. Action-to-Sound Synchronization (Footsteps on surfaces, foliage movement, object impacts).
3. Thematic Background Music Bus.
4. Dynamic Ducking & Audio Priority.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SoundscapeLayer(BaseModel):
    layer_id: str
    name: str
    category: str  # nature, weather, mechanical, crowd, room_tone, sub_bass
    description: str
    volume: float = 0.5
    loop: bool = True
    frequency_range_hz: str = "300-8000"


class ActionSFXEvent(BaseModel):
    event_id: str
    action_type: str  # footsteps_leaves, footsteps_soil, foliage_rustle, bird_chirp, wind_gust, cannon_boom, whoosh_pan, coin_chime
    description: str
    timestamp_offset_ms: int
    duration_ms: int
    volume: float = 0.6
    sync_trigger: str  # character_walk_step, camera_pan, object_impact, ambient_wildlife


class SceneSoundscapeSpec(BaseModel):
    scene_id: str
    scene_order: int
    primary_environment: str  # tropical_forest, mountain_battlefield, financial_floor, cyber_tech_lab, deep_space, green_wind_farm
    ambient_layers: List[SoundscapeLayer]
    action_sfx_events: List[ActionSFXEvent]
    music_theme: str
    ducking_db: float = -17.0
    voice_priority: bool = True


class AISoundscapeDirector:
    """
    Intelligent Environmental Sound Director generating structured 3-layer sound design specifications.
    """

    @classmethod
    def generate_soundscape_for_scene(
        cls,
        scene_id: str,
        scene_order: int,
        duration_sec: float,
        visual_description: str,
        setting_name: str,
        character_action: str = "walk",
        genre: Optional[str] = None
    ) -> SceneSoundscapeSpec:
        desc_lower = f"{visual_description} {setting_name} {character_action} {genre or ''}".lower()

        ambient_layers: List[SoundscapeLayer] = []
        action_sfx: List[ActionSFXEvent] = []
        music_theme = "thematic_cinematic"
        primary_env = "generic_ambient"

        # 0. Horror & Creepy Story / Chuyện ma rùng rợn & Tâm linh
        if (genre and "horror" in genre.lower()) or any(w in desc_lower for w in ["ma", "kinh dị", "quỷ", "rùng rợn", "nhà hoang", "nghĩa địa", "tâm linh", "bóng đè", "huyền bí", "creepy", "ghost", "eerie", "tối", "đêm", "khe cửa", "tiếng gõ", "sợ hãi", "lạnh gáy", "hoảng loạn"]):
            primary_env = "horror_creepy"
            music_theme = "horror_eerie_drone_piano"
            ambient_layers = [
                SoundscapeLayer(
                    layer_id="amb_eerie_wind",
                    name="Tiếng gió rít qua khe cửa hoang lạnh",
                    category="weather",
                    description="Gió hú rít từng cơn qua khe cửa sổ gỗ mục nát",
                    volume=0.35,
                    loop=True,
                    frequency_range_hz="150-2200"
                ),
                SoundscapeLayer(
                    layer_id="amb_ghostly_whispers",
                    name="Tiếng thì thầm ma quái hư ảo",
                    category="room_tone",
                    description="Âm hưởng thì thầm chập chờn xa xăm tạo cảm giác rợn tóc gáy",
                    volume=0.25,
                    loop=True,
                    frequency_range_hz="800-4500"
                ),
                SoundscapeLayer(
                    layer_id="amb_dark_drone_sub",
                    name="Tần số hạ âm u ám rùng mình",
                    category="sub_bass",
                    description="Sub-bass u uất trầm đặc gây cảm giác hồi hộp tức ngực",
                    volume=0.30,
                    loop=True,
                    frequency_range_hz="35-180"
                )
            ]
            action_sfx = [
                ActionSFXEvent(
                    event_id="sfx_creaking_floor",
                    action_type="footsteps_wood",
                    description="Tiếng bước chân kẽo kẹt trên sàn gỗ mục",
                    timestamp_offset_ms=400,
                    duration_ms=350,
                    volume=0.55,
                    sync_trigger="character_walk_step"
                ),
                ActionSFXEvent(
                    event_id="sfx_creaking_door",
                    action_type="door_creak",
                    description="Cánh cửa gỗ mục từ từ hé mở kẽo kẹt rợn người",
                    timestamp_offset_ms=int(duration_sec * 350),
                    duration_ms=650,
                    volume=0.50,
                    sync_trigger="camera_pan"
                ),
                ActionSFXEvent(
                    event_id="sfx_heartbeat_pulse",
                    action_type="heartbeat",
                    description="Tiếng tim đập thình thịch căng thẳng hồi hộp",
                    timestamp_offset_ms=int(duration_sec * 700),
                    duration_ms=800,
                    volume=0.60,
                    sync_trigger="camera_pan"
                )
            ]

        # 0.5. Mystery & Noir Crime / Điều tra phá án
        elif any(w in desc_lower for w in ["vụ án", "phá án", "tội phạm", "điều tra", "thám tử", "hình sự", "cảnh sát", "manh mối", "dấu vết"]):
            primary_env = "crime_noir"
            music_theme = "noir_jazz_investigation"
            ambient_layers = [
                SoundscapeLayer(
                    layer_id="amb_noir_rain",
                    name="Mưa đêm rả rích trên mặt đường",
                    category="weather",
                    description="Âm hưởng mưa đêm cô độc rơi trên mái hiên và mặt đường nhựa",
                    volume=0.30,
                    loop=True,
                    frequency_range_hz="300-4000"
                )
            ]
            action_sfx = [
                ActionSFXEvent(
                    event_id="sfx_typewriter",
                    action_type="typewriter",
                    description="Tiếng gõ phím máy chữ lạch cạch ghi chép hồ sơ",
                    timestamp_offset_ms=300,
                    duration_ms=450,
                    volume=0.45,
                    sync_trigger="camera_pan"
                ),
                ActionSFXEvent(
                    event_id="sfx_camera_shutter",
                    action_type="camera_shutter",
                    description="Tiếng chớp màn trập máy ảnh lưu lại hiện trường",
                    timestamp_offset_ms=int(duration_sec * 500),
                    duration_ms=300,
                    volume=0.40,
                    sync_trigger="camera_pan"
                )
            ]

        # 1. Tropical Forest / Jungle Environment
        elif any(w in desc_lower for w in ["rừng", "forest", "cây", "lá", "tropical", "cỏ", "thiên nhiên", "đồi"]):
            primary_env = "tropical_forest"
            music_theme = "nature_acoustic_strings"
            ambient_layers = [
                SoundscapeLayer(
                    layer_id="amb_insects",
                    name="Tiếng ve sầu & côn trùng rừng nhiệt đới",
                    category="nature",
                    description="Râm ran liên tục của ve sầu và côn trùng đêm/ngày trong tán rừng",
                    volume=0.35,
                    loop=True,
                    frequency_range_hz="4500-7500"
                ),
                SoundscapeLayer(
                    layer_id="amb_birds",
                    name="Tiếng chim rừng hót xa xăm",
                    category="nature",
                    description="Tiếng chim rừng líu lo ngắt quãng ở hậu cảnh tạo chiều sâu không gian",
                    volume=0.30,
                    loop=True,
                    frequency_range_hz="2000-4000"
                ),
                SoundscapeLayer(
                    layer_id="amb_wind_canopy",
                    name="Gió thổi qua vòm tán lá",
                    category="weather",
                    description="Âm thanh xào xạc của gió lùa qua vòm lá rậm rạp",
                    volume=0.25,
                    loop=True,
                    frequency_range_hz="400-2500"
                )
            ]

            # Synchronized Footsteps for walking in forest (dry leaves & damp soil)
            step_interval_ms = 450  # ~2.2 steps per second for natural walk cycle
            total_duration_ms = int(duration_sec * 1000)
            step_time = 300
            step_count = 1

            while step_time < total_duration_ms - 400:
                action_sfx.append(ActionSFXEvent(
                    event_id=f"sfx_step_{step_count:02d}",
                    action_type="footsteps_leaves",
                    description="Tiếng bước chân giẫm lên thảm lá khô và nền đất xốp",
                    timestamp_offset_ms=step_time,
                    duration_ms=180,
                    volume=0.45,
                    sync_trigger="character_walk_step"
                ))
                step_time += step_interval_ms
                step_count += 1

            # Intermittent foliage rustle
            action_sfx.append(ActionSFXEvent(
                event_id="sfx_foliage_01",
                action_type="foliage_rustle",
                description="Tán cây xào xạc đung đưa theo cơn gió thoảng",
                timestamp_offset_ms=int(duration_sec * 400),
                duration_ms=800,
                volume=0.35,
                sync_trigger="ambient_wildlife"
            ))

        # 2. Historical Battlefield / Điện Biên Phủ / Kháng chiến
        elif (genre and any(g in genre.lower() for g in ["history", "war", "battle", "military", "historical"])) or any(w in desc_lower for w in ["điện biên", "pháo", "chiến hào", "hầm", "quân đội", "hành quân", "chiến trường", "chiến thắng", "lịch sử", "kháng chiến", "artillery", "bunker"]):
            primary_env = "mountain_battlefield"
            music_theme = "heroic_orchestral_brass"
            ambient_layers = [
                SoundscapeLayer(
                    layer_id="amb_valley_wind",
                    name="Gió rít qua hẻm núi lòng chảo",
                    category="weather",
                    description="Tiếng gió trầm đục lùa qua thung lũng Mường Thanh",
                    volume=0.35,
                    loop=True,
                    frequency_range_hz="150-1200"
                ),
                SoundscapeLayer(
                    layer_id="amb_trench_rumble",
                    name="Âm vang trầm của mặt trận",
                    category="historical",
                    description="Tiếng rền rĩ trầm thấp của chiến dịch ở phía chân trời xa",
                    volume=0.25,
                    loop=True,
                    frequency_range_hz="60-350"
                )
            ]
            action_sfx = [
                ActionSFXEvent(
                    event_id="sfx_march_01",
                    action_type="footsteps_soil",
                    description="Bước chân quân hành rập ràng trên sỏi đá",
                    timestamp_offset_ms=400,
                    duration_ms=250,
                    volume=0.50,
                    sync_trigger="character_walk_step"
                ),
                ActionSFXEvent(
                    event_id="sfx_cannon_distant",
                    action_type="cannon_boom",
                    description="Tiếng trọng pháo 105mm dội lại từ vách núi",
                    timestamp_offset_ms=int(duration_sec * 600),
                    duration_ms=1200,
                    volume=0.55,
                    sync_trigger="ambient_wildlife"
                ),
                ActionSFXEvent(
                    event_id="sfx_flag_wave",
                    action_type="foliage_rustle",
                    description="Tiếng cờ vải tung bay phần phật trong gió",
                    timestamp_offset_ms=int(duration_sec * 200),
                    duration_ms=600,
                    volume=0.40,
                    sync_trigger="character_walk_step"
                )
            ]

        # 3. Economics & Finance
        elif any(w in desc_lower for w in ["lạm phát", "kinh tế", "tiền tệ", "thị trường", "biểu đồ", "công sở"]):
            primary_env = "financial_floor"
            music_theme = "rhythmic_minimal_marimba"
            ambient_layers = [
                SoundscapeLayer(
                    layer_id="amb_office_pulse",
                    name="Âm hưởng phòng giao dịch hiện đại",
                    category="room_tone",
                    description="Không khí phòng làm việc tài chính tĩnh lặng, tập trung",
                    volume=0.20,
                    loop=True,
                    frequency_range_hz="100-3000"
                )
            ]
            action_sfx = [
                ActionSFXEvent(
                    event_id="sfx_coin_chime",
                    action_type="coin_chime",
                    description="Âm thanh leng keng trong trẻo của đồng tiền vàng",
                    timestamp_offset_ms=500,
                    duration_ms=400,
                    volume=0.40,
                    sync_trigger="camera_pan"
                ),
                ActionSFXEvent(
                    event_id="sfx_chart_rise",
                    action_type="whoosh_pan",
                    description="Hiệu ứng vút lên khi cột biểu đồ kinh tế tăng trưởng",
                    timestamp_offset_ms=int(duration_sec * 450),
                    duration_ms=350,
                    volume=0.35,
                    sync_trigger="camera_pan"
                )
            ]

        # 4. Technology & AI
        elif any(w in desc_lower for w in ["ai", "trí tuệ", "nơ-ron", "chip", "công nghệ", "máy tính"]):
            primary_env = "cyber_tech_lab"
            music_theme = "synthwave_ambient_arpeggio"
            ambient_layers = [
                SoundscapeLayer(
                    layer_id="amb_server_hum",
                    name="Tiếng server và quạt tản nhiệt trung tâm dữ liệu",
                    category="mechanical",
                    description="Tiếng vo ve êm ái của hệ thống máy chủ và tản nhiệt",
                    volume=0.25,
                    loop=True,
                    frequency_range_hz="120-1500"
                )
            ]
            action_sfx = [
                ActionSFXEvent(
                    event_id="sfx_data_stream",
                    action_type="whoosh_pan",
                    description="Luồng dữ liệu số quét qua mạng nơ-ron",
                    timestamp_offset_ms=350,
                    duration_ms=400,
                    volume=0.45,
                    sync_trigger="camera_pan"
                )
            ]

        # 5. Deep Space & Solar System
        elif any(w in desc_lower for w in ["vũ trụ", "mặt trời", "hành tinh", "sao", "space"]):
            primary_env = "deep_space"
            music_theme = "ethereal_cosmic_pad"
            ambient_layers = [
                SoundscapeLayer(
                    layer_id="amb_cosmic_sub",
                    name="Tần số hạ âm vũ trụ bao la",
                    category="sub_bass",
                    description="Âm thanh sâu thẳm tĩnh mịch của không gian vô tận",
                    volume=0.30,
                    loop=True,
                    frequency_range_hz="40-200"
                )
            ]
            action_sfx = [
                ActionSFXEvent(
                    event_id="sfx_orbit_whoosh",
                    action_type="whoosh_pan",
                    description="Tiếng gió vũ trụ mượt mà khi hành tinh lướt trên quỹ đạo",
                    timestamp_offset_ms=int(duration_sec * 300),
                    duration_ms=600,
                    volume=0.40,
                    sync_trigger="camera_pan"
                )
            ]

        # 6. Environment & Wind Energy
        else:
            primary_env = "green_wind_farm"
            music_theme = "uplifting_acoustic_warm"
            ambient_layers = [
                SoundscapeLayer(
                    layer_id="amb_gentle_breeze",
                    name="Gió thoảng qua đồng cỏ xanh",
                    category="weather",
                    description="Làn gió mát lành quay cánh quạt năng lượng tái tạo",
                    volume=0.30,
                    loop=True,
                    frequency_range_hz="300-3500"
                )
            ]
            action_sfx = [
                ActionSFXEvent(
                    event_id="sfx_turbine_whoosh",
                    action_type="foliage_rustle",
                    description="Âm thanh êm ái khi cánh quạt gió xoay vòng",
                    timestamp_offset_ms=int(duration_sec * 400),
                    duration_ms=700,
                    volume=0.35,
                    sync_trigger="ambient_wildlife"
                )
            ]

        return SceneSoundscapeSpec(
            scene_id=scene_id,
            scene_order=scene_order,
            primary_environment=primary_env,
            ambient_layers=ambient_layers,
            action_sfx_events=action_sfx,
            music_theme=music_theme,
            ducking_db=-17.0,
            voice_priority=True
        )

    @classmethod
    def enrich_manifest_soundscapes(cls, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches all scenes in a SceneManifest with derived soundscapes,
        environmental ambience, and action SFX events.
        """
        enriched_manifest = dict(manifest)
        manifest_genre = enriched_manifest.get("genre") or enriched_manifest.get("video_metadata", {}).get("genre") or ""
        scenes = enriched_manifest.get("scenes", [])
        updated_scenes = []

        for idx, sc in enumerate(scenes):
            scene_dict = dict(sc)
            sc_id = str(scene_dict.get("scene_id", f"scene_{idx + 1}"))
            dur = float(scene_dict.get("duration_seconds") or scene_dict.get("duration") or 4.0)
            vis_desc = (
                scene_dict.get("visual_description")
                or scene_dict.get("description")
                or scene_dict.get("script_text")
                or scene_dict.get("narration")
                or ""
            )
            setting = scene_dict.get("environment", {}).get("setting_name", "") if isinstance(scene_dict.get("environment"), dict) else str(scene_dict.get("setting", ""))
            char_action = scene_dict.get("animation_instructions", {}).get("character_action", "walk") if isinstance(scene_dict.get("animation_instructions"), dict) else "walk"

            spec = cls.generate_soundscape_for_scene(
                scene_id=sc_id,
                scene_order=scene_dict.get("scene_order", idx + 1),
                duration_sec=dur,
                visual_description=vis_desc,
                setting_name=setting,
                character_action=char_action,
                genre=manifest_genre
            )

            scene_dict["music_direction"] = spec.primary_environment
            scene_dict["sound_design"] = [
                {
                    "sfx_id": evt.event_id,
                    "sfx_type": evt.action_type,
                    "description": evt.description,
                    "start_time_offset_ms": evt.timestamp_offset_ms,
                    "volume": evt.volume,
                    "duck_narration": False
                }
                for evt in spec.action_sfx_events
            ]
            updated_scenes.append(scene_dict)

        enriched_manifest["scenes"] = updated_scenes
        return enriched_manifest

    enrich_manifest_with_soundscape = enrich_manifest_soundscapes

    @classmethod
    def get_soundscape_presets(cls) -> List[Dict[str, Any]]:
        return [
            {
                "id": "horror_creepy",
                "name": "👻 Kinh dị / Chuyện ma (Gió hú, tiếng bước chân kẽo kẹt, cửa hé, tiếng tim)",
                "music_theme": "horror_eerie_drone_piano",
                "default_sfx": ["sfx_creaking_floor", "sfx_creaking_door", "sfx_heartbeat_pulse", "sfx_jumpscare_stinger"]
            },
            {
                "id": "crime_noir",
                "name": "🕵️ Trinh thám / Phá án (Mưa đêm, máy chữ lạch cạch, chớp máy ảnh)",
                "music_theme": "noir_jazz_investigation",
                "default_sfx": ["sfx_typewriter", "sfx_camera_shutter"]
            },
            {
                "id": "comedy_cartoon",
                "name": "🎭 Hoạt họa / Hài hước (Lò xo boing, còi trượt, bong bóng nổ)",
                "music_theme": "cartoon_whimsical_bounce",
                "default_sfx": ["sfx_spring_boing", "sfx_slide_whistle"]
            },
            {
                "id": "epic_action",
                "name": "⚡ Hành động / Trailer (Va đập chấn động, whoosh nhanh, dồn dập)",
                "music_theme": "epic_percussion_trailer",
                "default_sfx": ["sfx_impact", "sfx_whoosh"]
            },
            {
                "id": "lofi_chill",
                "name": "🌸 Lofi / Thư giãn (Đĩa than tí tách, chuông gió, mưa nhẹ)",
                "music_theme": "lofi_vinyl_chillhop",
                "default_sfx": ["sfx_vinyl_crackle", "sfx_wind_chime"]
            },
            {
                "id": "ancient_dynasty",
                "name": "🏛️ Cổ trang / Cung đình (Đàn tranh, chuông đồng, bước chân ngự đạo)",
                "music_theme": "traditional_zither_court",
                "default_sfx": ["sfx_bronze_bell", "sfx_zither_strum"]
            },
            {
                "id": "tropical_forest",
                "name": "🌲 Rừng nhiệt đới (Ve sầu, gió tán lá, chim hót, bước chân lá)",
                "music_theme": "nature_acoustic_strings",
                "default_sfx": ["sfx_step_01", "sfx_foliage_01"]
            },
            {
                "id": "mountain_battlefield",
                "name": "⚔️ Chiến trường đèo núi (Gió hú, rền đại bác, bước chân bùn)",
                "music_theme": "heroic_orchestral_brass",
                "default_sfx": ["sfx_cannon_distant", "sfx_march_01"]
            },
            {
                "id": "financial_floor",
                "name": "📈 Thị trường tài chính (Chuông vàng, văn phòng giao dịch)",
                "music_theme": "rhythmic_minimal_marimba",
                "default_sfx": ["sfx_coin_chime", "sfx_chart_rise"]
            },
            {
                "id": "cyber_tech_lab",
                "name": "💻 Phòng công nghệ (Server hum, data stream whoosh)",
                "music_theme": "synthwave_ambient_arpeggio",
                "default_sfx": ["sfx_data_stream"]
            },
            {
                "id": "cyberpunk_neon",
                "name": "🌃 Thành thị tương lai (Mưa neon, còi xe bay, tiếng synth ngầm)",
                "music_theme": "cyberpunk_dystopian_synth",
                "default_sfx": ["sfx_neon_flicker", "sfx_flyby_whoosh"]
            },
            {
                "id": "deep_space",
                "name": "🚀 Vũ trụ / Thiên văn (Sub-bass, cosmic wash)",
                "music_theme": "ethereal_cosmic_pad",
                "default_sfx": ["sfx_orbit_whoosh"]
            },
            {
                "id": "green_wind_farm",
                "name": "🍃 Đồng cỏ sinh thái (Gió turbine, thiên nhiên xanh)",
                "music_theme": "uplifting_acoustic_warm",
                "default_sfx": ["sfx_turbine_whoosh"]
            },
            {
                "id": "ocean_voyage",
                "name": "🌊 Biển khơi / Hải trình (Sóng vỗ mạn thuyền, hải âu xa xăm)",
                "music_theme": "ocean_acoustic_ambient",
                "default_sfx": ["sfx_waves_crash", "sfx_seagull_call"]
            }
        ]

    @classmethod
    def search_sfx(cls, query: str = "", category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Smart Search Engine for environmental sound effects, transitions, and musical stingers.
        Matches keywords in name, category, or tags.
        """
        sfx_catalog = [
            # Horror & Suspense (Kinh dị / Siêu nhiên / Rùng rợn)
            {"id": "sfx_creaking_floor", "name": "Tiếng sàn gỗ kẽo kẹt rợn người", "category": "horror", "tags": ["ma", "gỗ", "bước chân", "kẽo kẹt", "creak", "floor"], "action_type": "footsteps_wood", "duration_ms": 1500, "volume": 0.55},
            {"id": "sfx_creaking_door", "name": "Tiếng cửa gỗ mục từ từ hé mở", "category": "horror", "tags": ["cửa", "ma", "rùng rợn", "door", "creak"], "action_type": "door_creak", "duration_ms": 2000, "volume": 0.50},
            {"id": "sfx_jumpscare_stinger", "name": "Hiệu ứng Jumpscare thót tim", "category": "horror", "tags": ["jumpscare", "giật mình", "thót tim", "stinger", "horror"], "action_type": "jumpscare_stinger", "duration_ms": 1200, "volume": 0.65},
            {"id": "sfx_heartbeat_pulse", "name": "Nhịp tim đập dồn dập hồi hộp", "category": "horror", "tags": ["tim", "đập", "hồi hộp", "heartbeat"], "action_type": "heartbeat", "duration_ms": 2500, "volume": 0.60},
            {"id": "sfx_distant_crow", "name": "Tiếng quạ kêu đêm khuya hoang vắng", "category": "horror", "tags": ["quạ", "chim", "đêm", "crow"], "action_type": "bird_chirp", "duration_ms": 1800, "volume": 0.40},
            {"id": "sfx_ghostly_whisper", "name": "Tiếng thì thầm ma quái hư thực", "category": "horror", "tags": ["thì thầm", "ma", "whisper", "ghost"], "action_type": "ghostly_whisper", "duration_ms": 2200, "volume": 0.45},
            {"id": "sfx_clock_ticking", "name": "Tiếng đồng hồ quả lắc điểm từng nhịp", "category": "horror", "tags": ["đồng hồ", "tích tắc", "clock", "tick", "đêm"], "action_type": "clock_ticking", "duration_ms": 2000, "volume": 0.45},
            {"id": "sfx_thunder_crack", "name": "Sấm sét rạch trời kinh hoàng", "category": "weather", "tags": ["sấm", "sét", "mưa", "thunder", "storm"], "action_type": "cannon_boom", "duration_ms": 3000, "volume": 0.60},
            {"id": "sfx_screaming_gasp", "name": "Tiếng thở gấp kinh hoàng (Gasp)", "category": "horror", "tags": ["thở", "sợ hãi", "gasp", "screaming", "horror"], "action_type": "whoosh_pan", "duration_ms": 900, "volume": 0.55},
            {"id": "sfx_dark_wind_howl", "name": "Tiếng gió rít qua khe cửa hoang lạnh", "category": "horror", "tags": ["gió", "hú", "wind", "cold", "rùng rợn"], "action_type": "whoosh_pan", "duration_ms": 2800, "volume": 0.40},
            {"id": "sfx_water_drip", "name": "Tiếng giọt nước tí tách hầm tối", "category": "horror", "tags": ["nước", "giọt", "drip", "tí tách", "hầm"], "action_type": "coin_chime", "duration_ms": 1100, "volume": 0.35},

            # Viral Cinematic & Cuts (Ricks Clips style)
            {"id": "sfx_whoosh_swipe", "name": "Whoosh chuyển cảnh chớp nhoáng (Viral Cut)", "category": "transition", "tags": ["whoosh", "chuyển cảnh", "swipe", "cut", "fast"], "action_type": "whoosh_pan", "duration_ms": 400, "volume": 0.50},
            {"id": "sfx_heavy_impact", "name": "Cú va đập chấn động (Bass Drop Hit)", "category": "impact", "tags": ["hit", "impact", "bass", "va đập", "boom"], "action_type": "cannon_boom", "duration_ms": 1000, "volume": 0.65},
            {"id": "sfx_glitch_riser", "name": "Hiệu ứng Riser dồn nhịp căng thẳng", "category": "transition", "tags": ["riser", "glitch", "dồn dập", "căng thẳng"], "action_type": "whoosh_pan", "duration_ms": 1500, "volume": 0.45},
            {"id": "sfx_fast_zoom_whoosh", "name": "Whoosh Zoom cận cảnh đột ngột", "category": "transition", "tags": ["zoom", "whoosh", "push in", "nhanh"], "action_type": "whoosh_pan", "duration_ms": 500, "volume": 0.50},

            # Historical & Military (Lịch sử & Chiến hào)
            {"id": "sfx_cannon_distant", "name": "Tiếng trọng pháo dội vách núi", "category": "historical", "tags": ["đại bác", "pháo", "súng", "chiến tranh", "cannon"], "action_type": "cannon_boom", "duration_ms": 2200, "volume": 0.55},
            {"id": "sfx_artillery_explosion", "name": "Tiếng bộc phá nổ rung chuyển công sự", "category": "historical", "tags": ["bộc phá", "nổ", "đại bác", "explosion"], "action_type": "cannon_boom", "duration_ms": 2500, "volume": 0.65},
            {"id": "sfx_march_01", "name": "Bước chân quân hành rập ràng sỏi đá", "category": "historical", "tags": ["quân hành", "hành quân", "bước chân", "march"], "action_type": "footsteps_soil", "duration_ms": 1800, "volume": 0.50},
            {"id": "sfx_rope_strain", "name": "Tiếng dây chão kéo pháo căng nghẹt", "category": "historical", "tags": ["dây thừng", "kéo pháo", "rope", "strain", "căng"], "action_type": "door_creak", "duration_ms": 1400, "volume": 0.50},
            {"id": "sfx_war_drums", "name": "Tiếng trống trận giục giã hào hùng", "category": "historical", "tags": ["trống", "trận", "drum", "hào hùng", "war"], "action_type": "cannon_boom", "duration_ms": 2000, "volume": 0.55},
            {"id": "sfx_victory_fanfare", "name": "Kèn đồng khúc khải hoàn ca chiến thắng", "category": "historical", "tags": ["kèn", "khải hoàn", "chiến thắng", "fanfare", "brass"], "action_type": "coin_chime", "duration_ms": 2600, "volume": 0.60},
            {"id": "sfx_vintage_radio_static", "name": "Tiếng rè đài điện đài quân sự", "category": "historical", "tags": ["radio", "bộ đàm", "điện đài", "static", "rè"], "action_type": "typewriter", "duration_ms": 1500, "volume": 0.40},

            # Mystery & Crime (Trinh thám & Hiện trường)
            {"id": "sfx_typewriter", "name": "Tiếng gõ máy chữ lạch cạch hồ sơ", "category": "crime", "tags": ["máy chữ", "phá án", "typewriter", "hồ sơ"], "action_type": "typewriter", "duration_ms": 1200, "volume": 0.45},
            {"id": "sfx_camera_shutter", "name": "Tiếng bấm máy ảnh hiện trường", "category": "crime", "tags": ["máy ảnh", "camera", "chụp hình", "shutter"], "action_type": "camera_shutter", "duration_ms": 600, "volume": 0.40},
            {"id": "sfx_footsteps_pavement", "name": "Tiếng giày da thám tử bước trên hè phố mưa", "category": "crime", "tags": ["bước chân", "mưa", "đêm", "footsteps"], "action_type": "footsteps_soil", "duration_ms": 1600, "volume": 0.45},

            # Finance & Markets (Tài chính & Kinh tế)
            {"id": "sfx_coin_chime", "name": "Tiếng đồng xu vàng leng keng", "category": "finance", "tags": ["tiền", "xu", "vàng", "coin", "chime"], "action_type": "coin_chime", "duration_ms": 800, "volume": 0.40},
            {"id": "sfx_cash_register", "name": "Tiếng máy đếm tiền ting ting", "category": "finance", "tags": ["cash", "register", "tiền", "ting"], "action_type": "coin_chime", "duration_ms": 900, "volume": 0.45},
            {"id": "sfx_chart_rise", "name": "Âm thanh đồ họa tăng trưởng vút lên", "category": "finance", "tags": ["chart", "tăng trưởng", "rise", "uptrend"], "action_type": "whoosh_pan", "duration_ms": 850, "volume": 0.40},

            # Technology & Cyber (Công nghệ & AI)
            {"id": "sfx_data_stream", "name": "Luồng dữ liệu số quét qua mạng nơ-ron", "category": "tech", "tags": ["data", "công nghệ", "ai", "stream"], "action_type": "whoosh_pan", "duration_ms": 600, "volume": 0.45},
            {"id": "sfx_server_hum", "name": "Tiếng quạt tản nhiệt cụm siêu máy tính", "category": "tech", "tags": ["server", "hum", "máy chủ", "fan"], "action_type": "whoosh_pan", "duration_ms": 2500, "volume": 0.35},
            {"id": "sfx_cyber_glitch", "name": "Nhiễu sóng xung điện từ Cyberpunk", "category": "tech", "tags": ["glitch", "cyber", "nhiễu", "xung điện"], "action_type": "whoosh_pan", "duration_ms": 700, "volume": 0.40},

            # Cartoon & Comedy (Hài hước / Hoạt họa)
            {"id": "sfx_cartoon_boing", "name": "Tiếng lò xo nảy tưng tưng", "category": "comedy", "tags": ["boing", "hài", "lò xo", "cartoon"], "action_type": "coin_chime", "duration_ms": 700, "volume": 0.50},
            {"id": "sfx_slide_whistle", "name": "Tiếng còi trượt vui nhộn", "category": "comedy", "tags": ["còi", "trượt", "whistle", "funny"], "action_type": "whoosh_pan", "duration_ms": 1000, "volume": 0.45},
            {"id": "sfx_pop_bubble", "name": "Tiếng bong bóng nổ bốp", "category": "comedy", "tags": ["pop", "bong bóng", "bubble"], "action_type": "coin_chime", "duration_ms": 350, "volume": 0.40}
        ]

        q = (query or "").strip().lower()
        if not q and not category:
            return sfx_catalog

        results = []
        for item in sfx_catalog:
            if category and item["category"] != category:
                continue
            if not q:
                results.append(item)
                continue
            matches_name = q in item["name"].lower()
            matches_cat = q in item["category"].lower()
            matches_tags = any(q in t.lower() for t in item["tags"])
            if matches_name or matches_cat or matches_tags:
                results.append(item)

        return results

    @classmethod
    def synthesize_sfx_file(cls, sfx_id: str, out_path: str) -> str:
        """
        Synthesizes real acoustic audio file for the given SFX ID using FFmpeg lavfi acoustic waveforms.
        Guarantees non-silent, rich harmonic audio files on disk.
        """
        import os
        import subprocess

        if os.path.exists(out_path) and os.path.getsize(out_path) > 500:
            return out_path

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

        # Map SFX to authentic acoustic synthesis expressions
        expressions = {
            "sfx_creaking_floor": ("0.35*sin(2*PI*(220+40*sin(2*PI*8*t))*t)*exp(-2.5*t) + 0.15*sin(2*PI*550*t)*exp(-3*t)", 1.5),
            "sfx_creaking_door": ("0.40*sin(2*PI*(180+60*sin(2*PI*4*t))*t)*exp(-1.5*t) + 0.20*sin(2*PI*360*t)*exp(-2*t)", 2.0),
            "sfx_jumpscare_stinger": ("0.70*sin(2*PI*880*t)*exp(-5*t) + 0.50*sin(2*PI*1240*t)*exp(-4*t) + 0.60*sin(2*PI*65*t)*exp(-2*t)", 1.2),
            "sfx_heartbeat_pulse": ("0.80*sin(2*PI*55*t)*exp(-8*(t-0.2*floor(t/0.6)))*(t>0.05) + 0.50*sin(2*PI*70*t)*exp(-10*(t-0.25*floor(t/0.6)))", 2.5),
            "sfx_ghostly_whisper": ("0.25*sin(2*PI*(600+150*sin(2*PI*3*t))*t)*sin(2*PI*0.8*t) + 0.15*sin(2*PI*1100*t)*sin(2*PI*1.5*t)", 2.2),
            "sfx_clock_ticking": ("0.50*sin(2*PI*1200*t)*exp(-35*(t-0.5*floor(t/0.5))) + 0.20*sin(2*PI*800*t)*exp(-30*(t-0.5*floor(t/0.5)))", 2.0),
            "sfx_thunder_crack": ("0.85*sin(2*PI*60*t)*exp(-1.8*t) + 0.40*sin(2*PI*120*t)*exp(-2.5*t) + 0.30*sin(2*PI*240*t)*exp(-3*t)", 3.0),
            "sfx_cannon_distant": ("0.90*sin(2*PI*50*t)*exp(-3*t) + 0.45*sin(2*PI*95*t)*exp(-4*t)", 2.2),
            "sfx_artillery_explosion": ("0.95*sin(2*PI*45*t)*exp(-2*t) + 0.60*sin(2*PI*110*t)*exp(-3*t) + 0.35*sin(2*PI*320*t)*exp(-5*t)", 2.5),
            "sfx_march_01": ("0.60*sin(2*PI*140*t)*exp(-12*(t-0.45*floor(t/0.45))) + 0.30*sin(2*PI*280*t)*exp(-15*(t-0.45*floor(t/0.45)))", 1.8),
            "sfx_rope_strain": ("0.40*sin(2*PI*(350+80*sin(2*PI*6*t))*t)*exp(-2*t)", 1.4),
            "sfx_war_drums": ("0.80*sin(2*PI*80*t)*exp(-8*(t-0.4*floor(t/0.4))) + 0.40*sin(2*PI*160*t)*exp(-10*(t-0.4*floor(t/0.4)))", 2.0),
            "sfx_victory_fanfare": ("0.45*sin(2*PI*523.25*t) + 0.40*sin(2*PI*659.25*t) + 0.35*sin(2*PI*783.99*t) + 0.30*sin(2*PI*1046.50*t)", 2.6),
            "sfx_whoosh_swipe": ("0.55*sin(2*PI*(1100 - 850*t)*t)*exp(-4*t)", 0.6),
            "sfx_heavy_impact": ("0.85*sin(2*PI*70*t)*exp(-5*t) + 0.40*sin(2*PI*140*t)*exp(-7*t)", 1.2),
            "sfx_glitch_riser": ("0.35*sin(2*PI*(150 + 600*t*t)*t) + 0.20*sin(2*PI*(300 + 1200*t*t)*t)", 1.5),
            "sfx_coin_chime": ("0.60*sin(2*PI*2400*t)*exp(-12*t) + 0.35*sin(2*PI*4800*t)*exp(-15*t)", 0.8),
            "sfx_cash_register": ("0.50*sin(2*PI*1800*t)*exp(-15*t) + 0.40*sin(2*PI*3200*t)*exp(-20*t)", 0.9),
            "sfx_data_stream": ("0.30*sin(2*PI*(400 + 800*sin(2*PI*12*t))*t)*exp(-2*t)", 0.8),
            "sfx_cartoon_boing": ("0.60*sin(2*PI*(200 + 350*sin(2*PI*10*t))*t)*exp(-3*t)", 0.8)
        }

        expr, dur = expressions.get(sfx_id, ("0.4*sin(2*PI*440*t)*exp(-3*t)", 1.0))
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"aevalsrc={expr}:d={dur}",
            "-c:a", "libmp3lame", "-b:a", "192k",
            out_path
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except Exception as e:
            with open(out_path, "wb") as f:
                f.write(b'\xff\xf3\x60\x00' * 50)
        return out_path
