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
        character_action: str = "walk"
    ) -> SceneSoundscapeSpec:
        desc_lower = (visual_description + " " + setting_name + " " + character_action).lower()

        ambient_layers: List[SoundscapeLayer] = []
        action_sfx: List[ActionSFXEvent] = []
        music_theme = "thematic_cinematic"
        primary_env = "generic_ambient"

        # 1. Tropical Forest / Jungle Environment
        if any(w in desc_lower for w in ["rừng", "forest", "cây", "lá", "tropical", "cỏ", "thiên nhiên", "đồi"]):
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

        # 2. Historical Battlefield / Điện Biên Phủ
        elif any(w in desc_lower for w in ["điện biên", "pháo", "chiến hào", "hầm", "quân đội", "hành quân", "chiến trường"]):
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
        scenes = enriched_manifest.get("scenes", [])
        updated_scenes = []

        for idx, sc in enumerate(scenes):
            scene_dict = dict(sc)
            sc_id = scene_dict.get("scene_id", f"scene_{idx + 1}")
            dur = float(scene_dict.get("duration_seconds", 4.0))
            vis_desc = scene_dict.get("visual_description", "")
            setting = scene_dict.get("environment", {}).get("setting_name", "") if isinstance(scene_dict.get("environment"), dict) else ""
            char_action = scene_dict.get("animation_instructions", {}).get("character_action", "walk") if isinstance(scene_dict.get("animation_instructions"), dict) else "walk"

            spec = cls.generate_soundscape_for_scene(
                scene_id=sc_id,
                scene_order=scene_dict.get("scene_order", idx + 1),
                duration_sec=dur,
                visual_description=vis_desc,
                setting_name=setting,
                character_action=char_action
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
