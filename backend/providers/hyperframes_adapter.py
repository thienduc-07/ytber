"""
HyperFrames Composition Adapter & Code-First Motion Graphics Engine.

Translates SceneManifest into an authoritative HyperFrames project:
1. Deterministic HTML/SVG/GSAP visual scene compositions.
2. 7 distinct motion graphics grammars:
   - AnimatedTacticalMap (SVG routes, radar, battle pins, coordinates).
   - HistoricalTimelineSequence (Milestone nodes, expanding cards, chronological spine).
   - AnimatedDataChartAndCounter (Animated ticking numbers, SVG bar charts, gauges).
   - ArchivalBlueprintAndDocument (Drafting grid, stamps, crosshairs, typewriter titles).
   - MultiLayerParallaxEnvironment (Foreground, midground, background parallax, particles).
   - KineticEditorialStatement (Punchy typography, color-blocked keywords, camera zoom).
   - VectorCharacterAction (Stylized vector commander/narrator with gesturing rigs).
3. Kinetic Pop Subtitles (@RicksClips3000 standard: word-by-word bouncing highlight in #FACC15).
4. Synchronized Multi-Track Audio:
   - Voiceover audio clips per scene.
   - Thematic background music bed (BGM, ducked at 0.14 volume).
   - Action sound effects (SFX) aligned with animation triggers.
5. HyperFrames project configuration (hyperframes.json, package.json, assets).
"""

import os
import re
import json
import shutil
import subprocess
from typing import Dict, Any, List, Optional
from backend.core.config import settings
from backend.providers.tts_engine import UnifiedTTSProvider, WordTiming, validate_audio_file
from backend.providers.character_rig_2d import CharacterRig2D
from backend.providers.environment_builder_2d import EnvironmentBuilder2D
from backend.providers.soundscape_engine import AISoundscapeDirector


class HyperFramesAdapter:
    """Authoritative adapter compiling SceneManifest into a deterministic HyperFrames project."""

    def __init__(self, base_render_dir: str = "./data/renders"):
        self.base_render_dir = base_render_dir
        os.makedirs(self.base_render_dir, exist_ok=True)

    def prepare_job_workspace(self, job_id: str) -> str:
        """Creates an isolated render workspace for the job."""
        job_dir = os.path.abspath(os.path.join(self.base_render_dir, job_id))
        os.makedirs(job_dir, exist_ok=True)
        os.makedirs(os.path.join(job_dir, "assets", "audio"), exist_ok=True)
        os.makedirs(os.path.join(job_dir, "compositions"), exist_ok=True)
        return job_dir

    def synthesize_acoustic_asset(self, filepath: str, audio_type: str, duration_sec: float = 5.0):
        """
        Synthesizes real acoustic MP3 audio for BGM and SFX using high-fidelity multi-harmonic waveforms.
        Guarantees pristine non-silent audio files without external network dependencies.
        """
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            return

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "lavfi"]
        if audio_type == "bgm_heroic":
            # Rich cinematic brass/strings progression (C minor chord progression with bass pulse)
            expr = (
                "0.35*sin(2*PI*65.41*t) + 0.25*sin(2*PI*130.81*t) + 0.20*sin(2*PI*155.56*t) + "
                "0.15*sin(2*PI*196.00*t) + 0.10*sin(2*PI*261.63*t)"
            )
            cmd.extend(["-i", f"aevalsrc={expr}:d={duration_sec}"])
        elif audio_type == "bgm_horror":
            # Eerie sub-bass drone with dissonant tritone minor second (55Hz + 77.78Hz tritone)
            expr = (
                "0.40*sin(2*PI*55.00*t) + 0.25*sin(2*PI*77.78*t) + 0.15*sin(2*PI*116.54*t) + "
                "0.10*sin(2*PI*440*t)*sin(2*PI*0.5*t)"
            )
            cmd.extend(["-i", f"aevalsrc={expr}:d={duration_sec}"])
        elif audio_type == "bgm_tech":
            # Rhythmic electronic pulse arpeggio
            expr = (
                "0.30*sin(2*PI*110*t)*(0.5+0.5*sin(2*PI*4*t)) + 0.20*sin(2*PI*220*t) + "
                "0.15*sin(2*PI*330*t)"
            )
            cmd.extend(["-i", f"aevalsrc={expr}:d={duration_sec}"])
        elif audio_type == "sfx_whoosh":
            # Fast frequency drop whoosh
            expr = "0.5*sin(2*PI*(900 - 700*t)*t)*exp(-4*t)"
            cmd.extend(["-i", f"aevalsrc={expr}:d=0.8"])
        elif audio_type == "sfx_impact":
            # Sub-bass heavy impact with fast decay
            expr = "0.8*sin(2*PI*75*t)*exp(-6*t) + 0.3*sin(2*PI*150*t)*exp(-8*t)"
            cmd.extend(["-i", f"aevalsrc={expr}:d=1.2"])
        elif audio_type == "sfx_click":
            # Short subtle typewriter or pop click
            expr = "0.6*sin(2*PI*1400*t)*exp(-25*t)"
            cmd.extend(["-i", f"aevalsrc={expr}:d=0.2"])
        else:
            # General subtle cinematic bed
            expr = "0.3*sin(2*PI*110*t) + 0.2*sin(2*PI*220*t)"
            cmd.extend(["-i", f"aevalsrc={expr}:d={duration_sec}"])

        cmd.extend(["-c:a", "libmp3lame", "-b:a", "192k", filepath])
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    def select_visual_grammar(self, scene: Dict[str, Any], scene_idx: int, total_scenes: int, genre: str) -> str:
        """Selects the best code-first visual grammar for the narrative beat."""
        text = (scene.get("narration_text") or "").lower()
        vis_method = (scene.get("visual_method") or "").lower()
        cat = (genre or "").lower()

        # 1. Direct explicit grammar override if specified
        if vis_method in ("anatomy", "anatomical", "anatomical_system_breakdown"):
            return "anatomical_system_breakdown"
        if vis_method in ("schematic", "scientific", "scientific_technical_schematic"):
            return "scientific_technical_schematic"
        if vis_method in ("presenter", "doctor", "narrator", "narrator_expert_explainer"):
            return "narrator_expert_explainer"
        if vis_method in ("horror", "gothic_horror"):
            if any(w in text for w in ["hành lang", "bước chân", "dấu chân", "chạy", "đuổi"]):
                return "horror_dark_corridor"
            elif any(w in text for w in ["bóng", "người đàn bà", "áo trắng", "sau lưng", "gương", "quỷ", "twist", "mẹ"]):
                return "horror_shadow_encounter"
            elif any(w in text for w in ["hét", "sốc", "kinh hoàng", "giật mình", "bầm tím", "chết lặng"]):
                return "horror_shock_recoil"
            else:
                return "horror_bedroom_flashlight"

        # 2. Anatomical, Internal Organs, Biological, Health & Medical explainer
        is_anatomy = any(g in cat for g in ["medical", "biology", "health", "science_explainer"]) or any(
            w in text for w in [
                "nội tạng", "tim", "phổi", "gan", "thận", "não", "mạch máu", "cơ quan", "tế bào",
                "y học", "sức khỏe", "bác sĩ", "sinh học", "huyết áp", "nhịp đập", "cơ thể",
                "giải phẫu", "van tim", "oxy", "tuần hoàn", "co bóp", "hệ tiêu hóa", "bệnh lý"
            ]
        )
        if is_anatomy:
            anatomy_grammars = ["anatomical_system_breakdown", "scientific_technical_schematic", "narrator_expert_explainer"]
            return anatomy_grammars[(scene_idx - 1) % len(anatomy_grammars)]

        # 3. Scientific, Engineering, Mechanical & Deep-Tech explainer
        is_science_tech = any(g in cat for g in ["tech", "engineering", "space"]) or any(
            w in text for w in [
                "nguyên lý", "cơ chế", "cấu tạo", "hoạt động", "hệ thống", "kỹ thuật", "sơ đồ",
                "máy móc", "động cơ", "vũ trụ", "hành tinh", "vi mạch", "thuật toán", "công nghệ",
                "vật lý", "hóa học", "nguyên tử", "laser", "radar", "áp suất", "tần số"
            ]
        )
        if is_science_tech:
            tech_grammars = ["scientific_technical_schematic", "anatomical_system_breakdown", "data_counter_chart"]
            return tech_grammars[(scene_idx - 1) % len(tech_grammars)]

        # 4. Horror & Creepy Urban Legend (Articulated 2D Character Rig & Illustrated Environment)
        is_horror = "horror" in cat or any(w in text for w in ["ma", "kinh dị", "quỷ", "bóng đè", "rùng rợn", "ngôi nhà hoang", "nghĩa địa", "tiếng gõ", "nửa đêm", "ác mộng"])
        if is_horror:
            horror_grammars = ["horror_bedroom_flashlight", "horror_dark_corridor", "horror_shadow_encounter", "horror_shock_recoil"]
            return horror_grammars[(scene_idx - 1) % len(horror_grammars)]

        # 5. Historical Narrative (Articulated Military Rigs, Dien Bien Phu Basin, Command Bunker, Victory Flag)
        is_history = "historical" in cat or any(w in text for w in ["điện biên", "1954", "pháo", "kéo pháo", "tướng", "chỉ huy", "chiến thắng", "kháng chiến", "đờ cát", "de castries", "quân đội", "hào hùng", "bạch đằng", "lê lợi", "gươm thần"])
        if is_history:
            history_grammars = ["history_mountain_artillery", "history_command_bunker", "tactical_map", "history_victory_flag"]
            return history_grammars[(scene_idx - 1) % len(history_grammars)]

        # 6. Specific content triggers
        if any(w in text for w in ["bản đồ", "thung lũng", "địa cầu", "tây bắc", "núi", "đèo", "lòng chảo", "chiến dịch", "vị trí", "địa điểm", "hướng tiến"]):
            return "tactical_map"
        elif any(w in text for w in ["năm", "tháng", "ngày", "lịch sử", "thời gian", "giai đoạn", "bắt đầu", "kết thúc", "cột mốc"]):
            return "historical_timeline"
        elif any(w in text for w in ["quân", "lực lượng", "tấn", "triệu", "nghìn", "phần trăm", "%", "con số", "thống kê", "chi phí", "thiệt hại"]):
            return "data_counter_chart"
        elif any(w in text for w in ["chỉ huy", "đại tướng", "quyết định", "mật lệnh", "kế hoạch", "hồ sơ", "tài liệu", "hầm"]):
            return "archival_blueprint"
        elif any(w in text for w in ["chiến đấu", "gian khổ", "đêm", "rừng", "chiến sĩ", "hành quân", "khói lửa"]):
            return "parallax_environment"
        elif scene_idx == 1 or scene_idx == total_scenes:
            return "kinetic_statement"
        else:
            grammars = ["tactical_map", "historical_timeline", "data_counter_chart", "archival_blueprint", "parallax_environment", "kinetic_statement"]
            return grammars[scene_idx % len(grammars)]

    def resolve_scene_voiceover_path(self, scene: Dict[str, Any], s_order: int) -> str:
        """
        Resolves genuine narration audio file with traversal protection and strict ordering:
        1. scene.get("audio_file_path")
        2. os.path.join(settings.AUDIO_STORAGE_PATH, clean_filename)
        3. os.path.abspath(os.path.join("./data/audio", clean_filename))
        4. scene.get("audio_url") local file path if absolute or relative
        """
        import urllib.parse

        audio_file_path = scene.get("audio_file_path")
        audio_url = scene.get("audio_url") or ""
        audio_id = scene.get("audio_id") or ""
        audio_filename = scene.get("audio_filename") or ""

        clean_filename = ""
        if audio_filename:
            clean_filename = os.path.basename(audio_filename.strip())
        elif audio_url:
            url_clean = urllib.parse.unquote(audio_url.split("?")[0].strip())
            if "/api/v1/tts/audio/" in url_clean:
                clean_filename = os.path.basename(url_clean.split("/api/v1/tts/audio/")[-1])
            else:
                clean_filename = os.path.basename(url_clean)
        elif audio_id:
            clean_filename = audio_id if audio_id.endswith(".mp3") else f"{audio_id}.mp3"
            clean_filename = os.path.basename(clean_filename.strip())

        candidates = []
        # Candidate 1: Explicit audio_file_path from TTS Result
        if audio_file_path and isinstance(audio_file_path, str):
            candidates.append(os.path.abspath(audio_file_path))

        # Candidate 2: Configured audio storage paths across possible working dirs
        storage_root = getattr(settings, "AUDIO_STORAGE_PATH", "./data/audio")
        storage_dirs = [
            os.path.abspath(storage_root),
            os.path.abspath("./data/audio"),
            os.path.abspath(os.path.join(os.getcwd(), "data/audio")),
            os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "data", "audio"))
        ]

        if clean_filename:
            safe_filename = "".join(c for c in clean_filename if c.isalnum() or c in (".", "_", "-"))
            if safe_filename:
                for s_dir in storage_dirs:
                    candidates.append(os.path.join(s_dir, safe_filename))
                    if not safe_filename.endswith(".mp3"):
                        candidates.append(os.path.join(s_dir, f"{safe_filename}.mp3"))

        # Candidate 3: audio_url path if on local filesystem
        if audio_url:
            url_clean = urllib.parse.unquote(audio_url.split("?")[0].strip())
            if os.path.isabs(url_clean) and not url_clean.startswith("http"):
                candidates.append(os.path.abspath(url_clean))
            elif "/api/v1/tts/audio/" in url_clean:
                fname = url_clean.split("/api/v1/tts/audio/")[-1].strip()
                safe_fname = "".join(c for c in fname if c.isalnum() or c in (".", "_", "-"))
                if safe_fname:
                    for s_dir in storage_dirs:
                        candidates.append(os.path.join(s_dir, safe_fname))
                        if not safe_fname.endswith(".mp3"):
                            candidates.append(os.path.join(s_dir, f"{safe_fname}.mp3"))

        for p in candidates:
            if p and os.path.exists(p) and os.path.getsize(p) > 200:
                is_valid, _ = validate_audio_file(p)
                if is_valid:
                    return p

        searched = ", ".join(candidates) if candidates else "No candidates generated"
        raise RuntimeError(
            f"Missing or corrupted narration voiceover for scene {s_order}: '{clean_filename}'. "
            f"Searched paths: [{searched}]. "
            "Production pipeline strictly prohibits substituting fake audio or silence for voiceover."
        )

    def preflight_validate_all_audio(self, scenes: List[Dict[str, Any]]):
        """Preflight validates that all scenes possess valid non-silent voiceover audio before generating project."""
        for idx, scene in enumerate(scenes):
            s_order = idx + 1
            self.resolve_scene_voiceover_path(scene, s_order)

    def generate_html_composition(self, manifest: Dict[str, Any], job_dir: str) -> str:
        """
        Generates index.html adhering 100% to the HyperFrames composition contract:
        - Exact resolution (1080x1920) and FPS (30).
        - .clip elements with data-start and data-duration in seconds.
        - Audio elements on separate tracks (Voiceover, BGM, SFX).
        - GSAP master timeline bound to window.__timelines['main'].
        - Kinetic Pop Subtitles word-by-word bouncing highlight.
        """
        scenes = manifest.get("scenes", [])
        fps = manifest.get("video_specs", {}).get("fps", 30)
        total_duration = max(5.0, manifest.get("total_duration_sec", 10.0))
        genre = manifest.get("genre", "historical_doc")

        # Preflight validation: verify all scene audio exists and is valid before rendering
        self.preflight_validate_all_audio(scenes)

        # Dynamic Aspect Ratio & Resolution Handling (Shorts 9:16 vs Long-form 16:9)
        video_format = manifest.get("video_format") or manifest.get("format") or manifest.get("video_specs", {}).get("format") or "short-form"
        aspect_ratio = manifest.get("aspect_ratio") or manifest.get("video_specs", {}).get("aspect_ratio") or ("9:16" if video_format == "short-form" else "16:9")
        is_long = video_format == "long-form" or aspect_ratio == "16:9"
        width = 1920 if is_long else 1080
        height = 1080 if is_long else 1920
        sub_pad_bottom = 110 if is_long else 240

        # Prepare BGM and SFX audio files
        bgm_type = "bgm_horror" if "horror" in genre else ("bgm_tech" if "tech" in genre else "bgm_heroic")
        bgm_path = os.path.join(job_dir, "assets", "audio", "bgm.mp3")
        self.synthesize_acoustic_asset(bgm_path, bgm_type, duration_sec=total_duration + 5.0)

        sfx_whoosh_path = os.path.join(job_dir, "assets", "audio", "sfx_whoosh.mp3")
        self.synthesize_acoustic_asset(sfx_whoosh_path, "sfx_whoosh", duration_sec=1.0)

        sfx_impact_path = os.path.join(job_dir, "assets", "audio", "sfx_impact.mp3")
        self.synthesize_acoustic_asset(sfx_impact_path, "sfx_impact", duration_sec=1.5)

        sfx_click_path = os.path.join(job_dir, "assets", "audio", "sfx_click.mp3")
        self.synthesize_acoustic_asset(sfx_click_path, "sfx_click", duration_sec=0.5)

        # Audio elements markup - 4 distinct production buses
        audio_elements = []
        # Bus 2: Background music bed (ducked at 0.14 volume = -17dB)
        audio_elements.append(
            f'<audio id="bgm_track" class="clip" src="assets/audio/bgm.mp3" data-start="0.0" data-duration="{round(total_duration, 2)}" data-volume="0.14" data-track-index="1"></audio>'
        )

        scenes_markup = []
        gsap_tweens = []

        current_time = 0.0

        for idx, scene in enumerate(scenes):
            s_order = idx + 1
            duration = max(2.0, round(float(scene.get("duration_seconds", 3.0)), 2))
            start_time = round(current_time, 2)
            end_time = round(start_time + duration, 2)
            narration = scene.get("narration_text", "")
            grammar = self.select_visual_grammar(scene, s_order, len(scenes), genre)

            # Bus 1: Copy Genuine Voiceover Audio (Never fake tones)
            voice_rel_path = f"assets/audio/voice_{idx}.mp3"
            voice_dest_path = os.path.join(job_dir, voice_rel_path)

            source_audio_path = self.resolve_scene_voiceover_path(scene, s_order)
            shutil.copy2(source_audio_path, voice_dest_path)

            # Bus 1: Voiceover tag
            audio_elements.append(
                f'<audio id="voice_{idx}" class="clip" src="{voice_rel_path}" data-start="{start_time}" data-duration="{duration}" data-volume="1.0" data-track-index="2"></audio>'
            )

            # Bus 3: Environmental Ambience
            amb_list = scene.get("ambient_layers") or manifest.get("ambient_layers") or []
            if amb_list:
                top_amb = amb_list[0]
                amb_id = top_amb.get("layer_id") or "amb_room_tone"
                clean_amb_id = "".join(c for c in amb_id if c.isalnum() or c in ("_", "-"))
                amb_file = f"assets/audio/{clean_amb_id}.mp3"
                amb_dest = os.path.join(job_dir, amb_file)
                if not os.path.exists(amb_dest):
                    AISoundscapeDirector.synthesize_sfx_file(clean_amb_id, amb_dest)
                amb_vol = top_amb.get("volume", 0.25)
                audio_elements.append(
                    f'<audio id="amb_{idx}" class="clip" src="{amb_file}" data-start="{start_time}" data-duration="{duration}" data-volume="{amb_vol}" data-track-index="4"></audio>'
                )

            # Bus 4: Action SFX Cue per scene
            sfx_list = scene.get("sfx_cues") or scene.get("sound_design") or []
            if sfx_list:
                top_sfx = sfx_list[0]
                sfx_id = top_sfx.get("sfx_id") or "sfx_whoosh"
                clean_sfx_id = "".join(c for c in sfx_id if c.isalnum() or c in ("_", "-"))
                sfx_file = f"assets/audio/{clean_sfx_id}.mp3"
                sfx_dest = os.path.join(job_dir, sfx_file)
                if not os.path.exists(sfx_dest):
                    AISoundscapeDirector.synthesize_sfx_file(clean_sfx_id, sfx_dest)
                sfx_vol = top_sfx.get("volume", 0.45)
                sfx_offset = min(1.0, round(float(top_sfx.get("start_time_offset_ms", 0)) / 1000.0, 2))
                sfx_time = round(start_time + sfx_offset, 2)
                audio_elements.append(
                    f'<audio id="sfx_{idx}" class="clip" src="{sfx_file}" data-start="{sfx_time}" data-duration="1.8" data-volume="{sfx_vol}" data-track-index="3"></audio>'
                )
            else:
                audio_elements.append(
                    f'<audio id="sfx_whoosh_{idx}" class="clip" src="assets/audio/sfx_whoosh.mp3" data-start="{start_time}" data-duration="0.8" data-volume="0.35" data-track-index="3"></audio>'
                )

            # Generate Visual Scene HTML & GSAP Tweens based on Grammar
            scene_html, scene_tweens = self._render_grammar_scene(idx, s_order, start_time, duration, grammar, narration, scene)
            scenes_markup.append(scene_html)
            gsap_tweens.extend(scene_tweens)

            # Generate Kinetic Pop Subtitles
            sub_html, sub_tweens = self._render_kinetic_pop_subtitles(idx, start_time, duration, narration, scene.get("subtitles_json", []))
            scenes_markup.append(sub_html)
            gsap_tweens.extend(sub_tweens)

            current_time += duration

        total_duration = max(total_duration, current_time)

        # Assemble Full index.html
        index_html = f"""<!doctype html>
<html lang="vi" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{manifest.get("title", "AI Video Studio Video")}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,700;0,800;0,900;1,900&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {{
        --ground: #07090E;
        --surface: #0E131F;
        --card: #151D30;
        --accent: #FACC15;
        --accent-red: #EF4444;
        --accent-blue: #38BDF8;
        --ink: #FFFFFF;
        --ink-dim: #94A3B8;
        --font-primary: 'Montserrat', sans-serif;
        --font-mono: 'Space Grotesk', monospace;
      }}
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html, body {{
        width: {width}px;
        height: {height}px;
        overflow: hidden;
        background: var(--ground);
        font-family: var(--font-primary);
        color: var(--ink);
        -webkit-font-smoothing: antialiased;
      }}
      #root {{
        width: {width}px;
        height: {height}px;
        position: relative;
        overflow: hidden;
        background: radial-gradient(circle at 50% 40%, #161F36 0%, #07090E 80%);
      }}
      
      /* Global Cinematic Vignette & Noise Texture Overlay */
      .cinematic-vignette {{
        position: absolute;
        inset: 0;
        pointer-events: none;
        box-shadow: inset 0 0 160px rgba(0, 0, 0, 0.85);
        z-index: 20;
      }}
      
      /* Scene Containers */
      .scene-viewport {{
        position: absolute;
        inset: 0;
        width: {width}px;
        height: {height}px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
      }}

      /* CapCut / TikTok Kinetic Subtitles with "Khung Cam" Sliding/Bouncing Highlight Pill */
      .subtitles-container {{
        position: absolute !important;
        inset: 0 !important;
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-end !important;
        padding-bottom: {sub_pad_bottom}px !important; /* Dynamic lower third safe zone: 240px for Shorts 9:16, 110px for Long-form 16:9 */
        z-index: 95;
        pointer-events: none;
        text-align: center;
        padding-left: 35px;
        padding-right: 35px;
      }}
      @media (min-aspect-ratio: 1/1) {{
        .subtitles-container {{
          padding-bottom: 110px !important; /* Lower third safe zone for 16:9 Long-form */
        }}
      }}
      .sub-phrase-card {{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 10px 22px;
        max-width: 1000px;
        will-change: transform, opacity;
      }}
      .sub-word-box {{
        display: inline-block;
        will-change: transform;
      }}
      .sub-word-text {{
        font-family: var(--font-primary), 'Montserrat', 'Impact', sans-serif;
        font-size: 64px;
        font-weight: 900;
        text-transform: uppercase;
        color: #FFFFFF;
        letter-spacing: -0.01em;
        -webkit-text-stroke: 8px #000000;
        paint-order: stroke fill;
        text-shadow: 0 4px 18px rgba(0,0,0,0.95);
        line-height: 1.1;
        display: inline-block;
        will-change: transform, color, text-shadow;
      }}
      @media (min-aspect-ratio: 1/1) {{
        .sub-word-text {{
          font-size: 46px;
          -webkit-text-stroke: 6px #000000;
        }}
      }}

      /* Anatomical & Scientific HUD Styles */
      .hud-leader-line {{
        stroke: #38BDF8;
        stroke-width: 2.5;
        stroke-dasharray: 6 4;
        fill: none;
      }}
      .hud-callout-card {{
        background: rgba(15, 23, 42, 0.88);
        border: 2px solid #38BDF8;
        border-radius: 14px;
        padding: 10px 18px;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.35);
        backdrop-filter: blur(8px);
      }}
      .hud-callout-title {{
        font-family: var(--font-mono);
        font-size: 16px;
        font-weight: 900;
        color: #38BDF8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}
      .hud-callout-val {{
        font-family: var(--font-primary);
        font-size: 24px;
        font-weight: 900;
        color: #F8FAFC;
        margin-top: 2px;
      }}
      .laser-scan-bar {{
        position: absolute;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, transparent, #38BDF8, #FACC15, #38BDF8, transparent);
        box-shadow: 0 0 20px #38BDF8, 0 0 40px #38BDF8;
        z-index: 30;
      }}

      /* Vector Map Styles */
      .tactical-grid {{
        position: absolute;
        inset: 40px;
        border: 2px solid rgba(56, 189, 248, 0.2);
        border-radius: 24px;
        background-image: 
          linear-gradient(to right, rgba(56, 189, 248, 0.05) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(56, 189, 248, 0.05) 1px, transparent 1px);
        background-size: 60px 60px;
      }}
      .hud-header {{
        position: absolute;
        top: 80px;
        left: 80px;
        right: 80px;
        display: flex;
        justify-content: space-between;
        font-family: var(--font-mono);
        font-size: 22px;
        color: var(--accent-blue);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        border-bottom: 2px solid rgba(56, 189, 248, 0.3);
        padding-bottom: 16px;
      }}
      .hud-title {{
        position: absolute;
        top: 150px;
        left: 80px;
        font-size: 42px;
        font-weight: 900;
        text-transform: uppercase;
        color: #FFFFFF;
        letter-spacing: -0.02em;
      }}

      /* Data Counters & Charts */
      .stat-counter-box {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: -120px;
      }}
      .stat-number {{
        font-size: 130px;
        font-weight: 900;
        font-family: var(--font-primary);
        color: var(--accent);
        text-shadow: 0 0 40px rgba(250, 204, 21, 0.6);
        line-height: 1;
        letter-spacing: -0.04em;
      }}
      .stat-label {{
        font-size: 32px;
        font-weight: 800;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 10px;
      }}

      /* Archival Blueprint Stamp */
      .archival-stamp {{
        border: 8px solid var(--accent-red);
        color: var(--accent-red);
        font-size: 64px;
        font-weight: 900;
        padding: 16px 48px;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        border-radius: 12px;
        transform: rotate(-12deg);
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.4);
      }}

      /* Timeline Milestone Nodes */
      .timeline-spine {{
        position: absolute;
        left: 140px;
        top: 250px;
        bottom: 250px;
        width: 8px;
        background: linear-gradient(to bottom, var(--accent-blue), var(--accent));
        border-radius: 4px;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
      }}
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="{round(total_duration, 2)}"
      data-width="{width}"
      data-height="{height}"
      data-fps="{fps}"
    >
      <div class="cinematic-vignette"></div>

      <!-- Synchronized Audio Tracks -->
      {''.join(audio_elements)}

      <!-- Visual Animated Scenes -->
      {''.join(scenes_markup)}
    </div>

    <script>
      const tl = gsap.timeline({{ paused: true }});

      // Master Tween Sequences
      {chr(10).join(gsap_tweens)}

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>"""

        index_path = os.path.join(job_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_html)

        # Write hyperframes.json
        hf_config = {
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {
                "blocks": "compositions",
                "components": "compositions/components",
                "assets": "assets"
            },
            "media": {
                "autoProxy": True
            }
        }
        with open(os.path.join(job_dir, "hyperframes.json"), "w", encoding="utf-8") as f:
            json.dump(hf_config, f, indent=2)

        # Write package.json
        pkg_json = {
            "name": f"render-job-{os.path.basename(job_dir)}",
            "private": True,
            "type": "module",
            "scripts": {
                "render": "npx -y hyperframes@0.9.72 render"
            }
        }
        with open(os.path.join(job_dir, "package.json"), "w", encoding="utf-8") as f:
            json.dump(pkg_json, f, indent=2)

        return index_path

    def _render_grammar_scene(
        self,
        scene_idx: int,
        order: int,
        start_time: float,
        duration: float,
        grammar: str,
        narration: str,
        scene: Dict[str, Any]
    ) -> (str, List[str]):
        """Generates HTML and GSAP tweens for a specific motion graphics grammar."""
        prefix = f"s{scene_idx}"
        tweens: List[str] = []

        if grammar == "horror_bedroom_flashlight":
            env = EnvironmentBuilder2D.render_environment("old_wooden_bedroom", f"{prefix}_env")
            char = CharacterRig2D.render_character_svg(f"{prefix}_char", archetype="horror_investigator", pose="frightened_creep", expression="terrified", x=420, y=1250, scale=1.0)
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
          {env["svg"]}
          {char["svg"]}
        </svg>
      </div>"""
            adapted = [t.replace("tl.", f"{prefix}_tl.") for t in env["tweens"] + char["tweens"]]
            tweens.append(f"""
      const {prefix}_tl = gsap.timeline();
      {chr(10).join(adapted)}
      {prefix}_tl.to("#{prefix}_view", {{ scale: 1.05, duration: {duration}, ease: "none" }}, 0.0);
      tl.add({prefix}_tl, {start_time});
""")

        elif grammar == "horror_dark_corridor":
            env = EnvironmentBuilder2D.render_environment("dark_corridor", f"{prefix}_env")
            char = CharacterRig2D.render_character_svg(f"{prefix}_char", archetype="horror_investigator", pose="shock_recoil", expression="shocked", x=540, y=1300, scale=1.0)
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
          {env["svg"]}
          {char["svg"]}
        </svg>
      </div>"""
            adapted = [t.replace("tl.", f"{prefix}_tl.") for t in env["tweens"] + char["tweens"]]
            tweens.append(f"""
      const {prefix}_tl = gsap.timeline();
      {chr(10).join(adapted)}
      {prefix}_tl.to("#{prefix}_view", {{ x: "+=6", y: "+=4", yoyo: true, repeat: 15, duration: 0.1, ease: "sine.inOut" }}, 0.0);
      tl.add({prefix}_tl, {start_time});
""")

        elif grammar == "horror_shadow_encounter":
            env = EnvironmentBuilder2D.render_environment("old_wooden_bedroom", f"{prefix}_env")
            char_inv = CharacterRig2D.render_character_svg(f"{prefix}_inv", archetype="horror_investigator", pose="frightened_creep", expression="terrified", x=260, y=1350, scale=0.88)
            char_shadow = CharacterRig2D.render_character_svg(f"{prefix}_shadow", archetype="shadow_entity", pose="observant_stand", expression="eerie", x=720, y=1050, scale=1.2)
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
          {env["svg"]}
          {char_shadow["svg"]}
          {char_inv["svg"]}
        </svg>
      </div>"""
            adapted = [t.replace("tl.", f"{prefix}_tl.") for t in env["tweens"] + char_shadow["tweens"] + char_inv["tweens"]]
            tweens.append(f"""
      const {prefix}_tl = gsap.timeline();
      {chr(10).join(adapted)}
      {prefix}_tl.to("#{prefix}_shadow_root", {{ scale: 1.15, transformOrigin: "bottom center", duration: {duration}, ease: "power1.inOut" }}, 0.0);
      tl.add({prefix}_tl, {start_time});
""")

        elif grammar == "horror_shock_recoil":
            env = EnvironmentBuilder2D.render_environment("dark_corridor", f"{prefix}_env")
            char = CharacterRig2D.render_character_svg(f"{prefix}_char", archetype="horror_investigator", pose="shock_recoil", expression="shocked", x=540, y=1180, scale=1.35)
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
          {env["svg"]}
          {char["svg"]}
        </svg>
      </div>"""
            adapted = [t.replace("tl.", f"{prefix}_tl.") for t in env["tweens"] + char["tweens"]]
            tweens.append(f"""
      const {prefix}_tl = gsap.timeline();
      {chr(10).join(adapted)}
      {prefix}_tl.fromTo("#{prefix}_char_root", {{ scale: 0.9 }}, {{ scale: 1.45, duration: 0.35, ease: "back.out(2)" }}, 0.1);
      tl.add({prefix}_tl, {start_time});
""")

        elif grammar == "history_mountain_artillery":
            env = EnvironmentBuilder2D.render_environment("mountain_battlefield", f"{prefix}_env")
            char = CharacterRig2D.render_character_svg(f"{prefix}_char", archetype="artillery_soldier", pose="pulling_rope", expression="determined", x=480, y=1200, scale=1.0)
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
          {env["svg"]}
          {char["svg"]}
        </svg>
      </div>"""
            adapted = [t.replace("tl.", f"{prefix}_tl.") for t in env["tweens"] + char["tweens"]]
            tweens.append(f"""
      const {prefix}_tl = gsap.timeline();
      {chr(10).join(adapted)}
      {prefix}_tl.to("#{prefix}_char_root", {{ x: "+=35", duration: {duration}, ease: "none" }}, 0.0);
      tl.add({prefix}_tl, {start_time});
""")

        elif grammar == "history_command_bunker":
            env = EnvironmentBuilder2D.render_environment("command_bunker", f"{prefix}_env")
            char = CharacterRig2D.render_character_svg(f"{prefix}_char", archetype="military_commander", pose="commanding_point", expression="determined", x=380, y=1220, scale=1.0)
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
          {env["svg"]}
          {char["svg"]}
        </svg>
      </div>"""
            adapted = [t.replace("tl.", f"{prefix}_tl.") for t in env["tweens"] + char["tweens"]]
            tweens.append(f"""
      const {prefix}_tl = gsap.timeline();
      {chr(10).join(adapted)}
      {prefix}_tl.to("#{prefix}_char_root", {{ scale: 1.05, duration: {duration}, ease: "power1.out" }}, 0.0);
      tl.add({prefix}_tl, {start_time});
""")

        elif grammar == "history_victory_flag":
            env = EnvironmentBuilder2D.render_environment("victory_roof", f"{prefix}_env")
            char = CharacterRig2D.render_character_svg(f"{prefix}_char", archetype="military_commander", pose="commanding_point", expression="determined", x=320, y=1300, scale=0.92)
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
          {env["svg"]}
          {char["svg"]}
        </svg>
      </div>"""
            adapted = [t.replace("tl.", f"{prefix}_tl.") for t in env["tweens"] + char["tweens"]]
            tweens.append(f"""
      const {prefix}_tl = gsap.timeline();
      {chr(10).join(adapted)}
      {prefix}_tl.fromTo("#{prefix}_view", {{ scale: 0.98, y: 30 }}, {{ scale: 1.04, y: -20, duration: {duration}, ease: "power2.out" }}, 0.0);
      tl.add({prefix}_tl, {start_time});
""")

        elif grammar == "tactical_map":
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <div class="tactical-grid">
          <div class="hud-header" data-layout-ignore="true">
            <span>CHIẾN DỊCH QUÂN SỰ</span>
            <span>21°23'N 103°01'E</span>
            <span>TỌA ĐỘ BẮC BỘ</span>
          </div>
          <div class="hud-title" data-layout-ignore="true">SƠ ĐỒ CỨ ĐIỂM CHIẾN LƯỢC</div>
          
          <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1000 1840">
            <!-- Contour circles -->
            <ellipse cx="500" cy="900" rx="420" ry="320" fill="none" stroke="rgba(56, 189, 248, 0.15)" stroke-width="3" stroke-dasharray="10 8"/>
            <ellipse cx="500" cy="900" rx="300" ry="220" fill="none" stroke="rgba(56, 189, 248, 0.25)" stroke-width="4" stroke-dasharray="12 6"/>
            <ellipse cx="500" cy="900" rx="180" ry="130" fill="rgba(239, 68, 68, 0.1)" stroke="#EF4444" stroke-width="4"/>

            <!-- Attack Route Path 1 (West) -->
            <path id="{prefix}_route_w" d="M 120 1450 Q 300 1200 480 940" fill="none" stroke="#FACC15" stroke-width="12" stroke-linecap="round" stroke-dasharray="800" stroke-dashoffset="800"/>
            
            <!-- Attack Route Path 2 (East) -->
            <path id="{prefix}_route_e" d="M 880 1400 Q 720 1150 520 940" fill="none" stroke="#FACC15" stroke-width="12" stroke-linecap="round" stroke-dasharray="800" stroke-dashoffset="800"/>

            <!-- Central Stronghold Marker -->
            <g id="{prefix}_marker" transform="translate(500, 900)">
              <circle r="40" fill="#EF4444" opacity="0.4"/>
              <circle r="20" fill="#EF4444"/>
              <circle r="6" fill="#FFFFFF"/>
            </g>
          </svg>
        </div>
      </div>"""
            tweens.append(f"""
      tl.fromTo("#{prefix}_route_w", {{ strokeDashoffset: 800 }}, {{ strokeDashoffset: 0, duration: {min(2.5, duration * 0.7)}, ease: "power2.inOut" }}, {start_time + 0.1});
      tl.fromTo("#{prefix}_route_e", {{ strokeDashoffset: 800 }}, {{ strokeDashoffset: 0, duration: {min(2.5, duration * 0.7)}, ease: "power2.inOut" }}, {start_time + 0.2});
      tl.fromTo("#{prefix}_marker", {{ scale: 0, transformOrigin: "center center" }}, {{ scale: 1.4, duration: 0.6, ease: "back.out(2)" }}, {start_time + 1.2});
      tl.fromTo("#{prefix}_view", {{ scale: 1 }}, {{ scale: 1.08, duration: {duration}, ease: "none" }}, {start_time});
""")

        elif grammar == "data_counter_chart":
            # Extract number if present or highlight
            digits = re.findall(r'\d+', narration)
            num_val = digits[0] if digits else "100%"
            label = "LỰC LƯỢNG QUYẾT ĐỊNH" if "quân" in narration else "KỲ TÍCH LỊCH SỬ"

            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <div class="stat-counter-box">
          <div id="{prefix}_num" class="stat-number">{num_val}</div>
          <div id="{prefix}_lbl" class="stat-label">{label}</div>
          
          <!-- Animated SVG Bar Visualizer -->
          <svg width="600" height="120" style="margin-top: 50px;" viewBox="0 0 600 120">
            <rect x="0" y="40" width="600" height="40" rx="20" fill="#1E293B"/>
            <rect id="{prefix}_bar" x="0" y="40" width="600" height="40" rx="20" fill="url(#grad_{prefix})"/>
            <defs>
              <linearGradient id="grad_{prefix}" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#38BDF8"/>
                <stop offset="100%" stop-color="#FACC15"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>"""
            tweens.append(f"""
      tl.fromTo("#{prefix}_num", {{ scale: 0.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.7, ease: "back.out(2.5)" }}, {start_time + 0.1});
      tl.fromTo("#{prefix}_lbl", {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }}, {start_time + 0.3});
      tl.fromTo("#{prefix}_bar", {{ width: 0 }}, {{ width: 600, duration: {min(2.0, duration * 0.65)}, ease: "power2.out" }}, {start_time + 0.2});
""")

        elif grammar == "historical_timeline":
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <div class="timeline-spine" id="{prefix}_spine"></div>
        
        <div style="position: absolute; left: 190px; top: 400px; max-width: 780px;">
          <div style="display: flex; align-items: center; gap: 20px;">
            <div id="{prefix}_dot" style="width: 32px; height: 32px; border-radius: 50%; background: #FACC15; box-shadow: 0 0 25px #FACC15;"></div>
            <span style="font-family: var(--font-mono); font-size: 28px; color: var(--accent); font-weight: 700; text-transform: uppercase;">MỐC SON LỊCH SỬ</span>
          </div>
          <h2 id="{prefix}_text" style="font-size: 46px; font-weight: 900; margin-top: 24px; text-transform: uppercase; line-height: 1.25; color: #FFFFFF;">
            {narration[:80]}...
          </h2>
        </div>
      </div>"""
            tweens.append(f"""
      tl.fromTo("#{prefix}_spine", {{ scaleY: 0, transformOrigin: "top center" }}, {{ scaleY: 1, duration: 0.9, ease: "power2.out" }}, {start_time + 0.1});
      tl.fromTo("#{prefix}_dot", {{ scale: 0 }}, {{ scale: 1.3, duration: 0.5, ease: "back.out(3)" }}, {start_time + 0.3});
      tl.fromTo("#{prefix}_text", {{ opacity: 0, x: 40 }}, {{ opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }}, {start_time + 0.4});
""")

        elif grammar == "archival_blueprint":
            stamp_text = "TOÀN THẮNG" if "thắng" in narration else "MỆNH LỆNH"
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <!-- Blueprint Grid & Crosshair -->
        <div style="position: absolute; inset: 60px; border: 4px solid rgba(255,255,255,0.2); border-radius: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
          <div style="font-family: var(--font-mono); font-size: 24px; color: var(--ink-dim); letter-spacing: 0.2em; margin-bottom: 30px;" data-layout-ignore="true">
            HỒ SƠ TÁC CHIẾN TỐI MẬT
          </div>
          <div id="{prefix}_stamp" class="archival-stamp" data-layout-allow-overlap="true" data-layout-ignore="true">{stamp_text}</div>
          <div style="width: 80%; height: 2px; background: rgba(255,255,255,0.2); margin: 40px 0;"></div>
          <div style="font-family: var(--font-mono); font-size: 26px; color: #38BDF8; letter-spacing: 0.05em; text-align: center;" data-layout-ignore="true">
            HẦM CHỈ HUY TẬP ĐOÀN CỨ ĐIỂM
          </div>
        </div>
      </div>"""
            tweens.append(f"""
      tl.fromTo("#{prefix}_stamp", {{ scale: 2.8, opacity: 0, rotation: -25 }}, {{ scale: 1, opacity: 1, rotation: -12, duration: 0.45, ease: "bounce.out" }}, {start_time + 0.2});
      tl.fromTo("#{prefix}_view", {{ scale: 1 }}, {{ scale: 1.05, duration: {duration}, ease: "none" }}, {start_time});
""")

        elif grammar == "parallax_environment":
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <!-- Background Layer: Distant mountains -->
        <svg id="{prefix}_bg" style="position: absolute; bottom: 0; width: 120%; left: -10%;" viewBox="0 0 1200 800">
          <polygon points="0,800 200,450 500,600 800,400 1200,800" fill="#0F172A"/>
          <polygon points="150,800 380,480 650,650 950,420 1200,800" fill="#1E293B" opacity="0.7"/>
        </svg>

        <!-- Midground Layer: Barbed wire & artillery -->
        <svg id="{prefix}_mg" style="position: absolute; bottom: 0; width: 110%; left: -5%;" viewBox="0 0 1100 400">
          <rect x="0" y="250" width="1100" height="150" fill="#090D16"/>
          <!-- Cannon silhouette -->
          <polygon points="400,280 480,220 540,240 450,300" fill="#FACC15" opacity="0.3"/>
          <circle cx="430" cy="300" r="30" fill="#334155"/>
        </svg>

        <!-- Foreground Atmosphere: Fire Sparks -->
        <div id="{prefix}_spark1" style="position: absolute; width: 8px; height: 8px; background: #EF4444; border-radius: 50%; box-shadow: 0 0 12px #EF4444;"></div>
        <div id="{prefix}_spark2" style="position: absolute; width: 12px; height: 12px; background: #FACC15; border-radius: 50%; box-shadow: 0 0 16px #FACC15;"></div>
      </div>"""
            tweens.append(f"""
      tl.fromTo("#{prefix}_bg", {{ x: -30 }}, {{ x: 30, duration: {duration}, ease: "none" }}, {start_time});
      tl.fromTo("#{prefix}_mg", {{ x: 40 }}, {{ x: -40, duration: {duration}, ease: "none" }}, {start_time});
      tl.fromTo("#{prefix}_spark1", {{ x: 300, y: 1400, opacity: 0 }}, {{ x: 380, y: 900, opacity: 1, duration: {min(2.5, duration)}, ease: "power1.out" }}, {start_time + 0.1});
      tl.fromTo("#{prefix}_spark2", {{ x: 650, y: 1500, opacity: 0 }}, {{ x: 600, y: 850, opacity: 1, duration: {min(3.0, duration)}, ease: "power1.out" }}, {start_time + 0.2});
""")

        elif grammar == "anatomical_system_breakdown":
            # Medical / Biological / Anatomical Organ Explainer with Pulsing Heart, ECG Waveform & Telemetry HUD
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <!-- Laser Scan Sweep Line -->
        <div id="{prefix}_laser" class="laser-scan-bar" style="top: 15%;"></div>

        <!-- Master Camera Rig (Push-in & Pan) -->
        <div id="{prefix}_camera_rig" style="position: absolute; inset: 0; width: 100%; height: 100%;">
          <!-- Background Blueprint Grid -->
          <div style="position: absolute; inset: 20px; border: 1.5px solid rgba(56, 189, 248, 0.2); border-radius: 20px; background-image: radial-gradient(circle, rgba(56, 189, 248, 0.08) 1.5px, transparent 1.5px); background-size: 35px 35px;"></div>

          <!-- Anatomical SVG Centerpiece: Human Heart & Circulatory Engine -->
          <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
            <!-- Defs for organ glow filters & gradients -->
            <defs>
              <linearGradient id="{prefix}_aorta_grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#EF4444"/>
                <stop offset="100%" stop-color="#991B1B"/>
              </linearGradient>
              <linearGradient id="{prefix}_pulmonary_grad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#0284C7"/>
                <stop offset="100%" stop-color="#0369A1"/>
              </linearGradient>
              <radialGradient id="{prefix}_heart_tissue" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#DC2626"/>
                <stop offset="70%" stop-color="#991B1B"/>
                <stop offset="100%" stop-color="#450A0A"/>
              </radialGradient>
              <filter id="{prefix}_glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="8" result="blur"/>
                <feMerge>
                  <feMergeNode in="blur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>

            <!-- Pulsing Organ Core -->
            <g id="{prefix}_heart_core" transform="translate(540, 840)">
              <!-- Vascular Aorta Arch -->
              <path d="M -20 -150 C -40 -260 80 -270 90 -160 C 95 -110 50 -80 30 -60" fill="none" stroke="url(#{prefix}_aorta_grad)" stroke-width="48" stroke-linecap="round"/>
              <!-- Three Aortic Arteries -->
              <line x1="-10" y1="-220" x2="-25" y2="-280" stroke="#EF4444" stroke-width="14" stroke-linecap="round"/>
              <line x1="25" y1="-235" x2="25" y2="-295" stroke="#EF4444" stroke-width="14" stroke-linecap="round"/>
              <line x1="60" y1="-220" x2="75" y2="-280" stroke="#EF4444" stroke-width="14" stroke-linecap="round"/>

              <!-- Pulmonary Artery (Blue/Cyan deoxygenated path) -->
              <path d="M -70 -120 C -110 -150 -120 -80 -60 -40" fill="none" stroke="url(#{prefix}_pulmonary_grad)" stroke-width="36" stroke-linecap="round"/>

              <!-- Main Muscle Ventricle Body -->
              <path d="M 0 -80 C -180 -120 -240 80 -60 220 C -20 250 20 250 60 220 C 240 80 180 -120 0 -80 Z" fill="url(#{prefix}_heart_tissue)" filter="url(#{prefix}_glow)"/>
              
              <!-- Ventricle Muscular Sulcus / Coronary Artery Branch -->
              <path id="{prefix}_coronary" d="M -15 -60 Q 20 30 -10 120 Q -25 170 5 210" fill="none" stroke="#FACC15" stroke-width="5" stroke-linecap="round"/>
              <path d="M 5 20 Q 40 45 65 75" fill="none" stroke="#FACC15" stroke-width="3.5" stroke-linecap="round"/>

              <!-- Internal Cross-Section Valve Chamber Highlight -->
              <ellipse id="{prefix}_valve" cx="35" cy="50" rx="35" ry="45" fill="none" stroke="#38BDF8" stroke-width="3.5" stroke-dasharray="6 4"/>
              <circle cx="35" cy="50" r="10" fill="#38BDF8" opacity="0.6"/>

              <!-- Glowing Vascular Blood Flow Pulse Particles -->
              <circle id="{prefix}_pulse1" cx="-10" cy="-220" r="6" fill="#FEE2E2" filter="url(#{prefix}_glow)"/>
              <circle id="{prefix}_pulse2" cx="35" cy="50" r="7" fill="#FACC15" filter="url(#{prefix}_glow)"/>
            </g>

            <!-- Anatomical Leader Lines & Telemetry Callouts -->
            <!-- Callout 1: Động Mạch Chủ (Aorta) -->
            <line class="hud-leader-line" x1="610" y1="620" x2="800" y2="520"/>
            <circle cx="610" cy="620" r="5" fill="#38BDF8"/>
            <foreignObject x="760" y="470" width="280" height="110">
              <div class="hud-callout-card">
                <div class="hud-callout-title">ĐỘNG MẠCH CHỦ (AORTA)</div>
                <div class="hud-callout-val">ÁP LỰC: 120 mmHg</div>
              </div>
            </foreignObject>

            <!-- Callout 2: Tâm Thất & Buồng Bơm (Ventricle) -->
            <line class="hud-leader-line" x1="575" y1="890" x2="800" y2="980"/>
            <circle cx="575" cy="890" r="5" fill="#38BDF8"/>
            <foreignObject x="760" y="930" width="280" height="110">
              <div class="hud-callout-card">
                <div class="hud-callout-title">TÂM THẤT TRÁI</div>
                <div class="hud-callout-val">CÔNG SUẤT: 5.2 L/P</div>
              </div>
            </foreignObject>

            <!-- Callout 3: Tần Số Sinh Học / Heart Rate Metric -->
            <foreignObject x="50" y="470" width="300" height="130">
              <div class="hud-callout-card" style="border-color: #22C55E;">
                <div class="hud-callout-title" style="color: #22C55E;">NHỊP TIM SINH HỌC</div>
                <div class="hud-callout-val" style="color: #22C55E; font-size: 32px;">72 BPM</div>
                <div style="font-family: var(--font-mono); font-size: 13px; color: #94A3B8; margin-top: 4px;">CHU KỲ: 0.83 GIÂY</div>
              </div>
            </foreignObject>

            <!-- Live Animated Electrocardiogram (ECG) Waveform -->
            <g id="{prefix}_ecg" transform="translate(140, 1340)">
              <rect x="0" y="0" width="800" height="140" rx="16" fill="rgba(15, 23, 42, 0.9)" stroke="rgba(34, 197, 94, 0.4)" stroke-width="2"/>
              <!-- ECG Grid -->
              <line x1="0" y1="70" x2="800" y2="70" stroke="rgba(34, 197, 94, 0.15)" stroke-width="1"/>
              <!-- Real ECG Wave (P-Q-R-S-T) -->
              <polyline id="{prefix}_ecg_wave" points="
                0,70 140,70 160,65 175,70 190,70 200,85 215,20 230,105 240,70 260,70 280,55 310,70 
                420,70 440,65 455,70 470,70 480,85 495,20 510,105 520,70 540,70 560,55 590,70 700,70 800,70
              " fill="none" stroke="#22C55E" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#{prefix}_glow)"/>
              <text x="30" y="40" font-family="var(--font-mono)" font-size="16" fill="#22C55E" font-weight="bold">ECG TELEMETRY [LEAD II]</text>
            </g>
          </svg>
        </div>
      </div>"""
            tweens.append(f"""
      // 1. Rhythmic Heartbeat Pulsation Cycle (72 BPM)
      tl.to("#{prefix}_heart_core", {{ scale: 1.09, duration: 0.16, ease: "power2.out", yoyo: true, repeat: {max(8, int(duration * 2.4))}, transformOrigin: "center center" }}, {start_time});
      tl.to("#{prefix}_pulse1, #{prefix}_pulse2", {{ scale: 1.5, opacity: 0.4, duration: 0.16, yoyo: true, repeat: {max(8, int(duration * 2.4))} }}, {start_time});

      // 2. Dynamic Camera Choreography: Push-in Macro Zoom & Pan
      tl.fromTo("#{prefix}_camera_rig", 
        {{ scale: 1.0, x: 0, y: 0 }}, 
        {{ scale: 1.35, x: -70, y: -90, duration: {duration}, ease: "power1.inOut" }}, 
        {start_time}
      );

      // 3. Laser Scanline Sweep across Organ
      tl.fromTo("#{prefix}_laser", {{ top: "15%", opacity: 0 }}, {{ top: "85%", opacity: 0.9, duration: {min(4.0, duration)}, ease: "none" }}, {start_time + 0.3});

      // 4. Live ECG Waveform Sweep
      tl.fromTo("#{prefix}_ecg_wave", {{ strokeDasharray: 900, strokeDashoffset: 900 }}, {{ strokeDashoffset: 0, duration: {duration}, ease: "none" }}, {start_time});
""")

        elif grammar == "scientific_technical_schematic":
            # Multi-topic Engineering & Science Blueprint Schematic with Radar Scanner & Metrics
            words = narration.split()
            concept_title = " ".join(words[:4]).upper() if len(words) >= 4 else "CƠ CHẾ KHOA HỌC"
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <!-- Blueprint Grid -->
        <div style="position: absolute; inset: 30px; border: 2px solid rgba(56, 189, 248, 0.25); border-radius: 20px; background-image: linear-gradient(rgba(56, 189, 248, 0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, 0.08) 1px, transparent 1px); background-size: 40px 40px;"></div>

        <!-- Camera Rig for Dynamic Pan -->
        <div id="{prefix}_schematic_cam" style="position: absolute; inset: 0; width: 100%; height: 100%;">
          <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
            <!-- Center Rotating Radar / Synapse Core -->
            <g id="{prefix}_radar_core" transform="translate(540, 800)">
              <circle cx="0" cy="0" r="220" fill="none" stroke="#38BDF8" stroke-width="2" stroke-dasharray="10 5" opacity="0.6"/>
              <circle cx="0" cy="0" r="150" fill="none" stroke="#38BDF8" stroke-width="3" opacity="0.8"/>
              <circle cx="0" cy="0" r="80" fill="rgba(56, 189, 248, 0.15)" stroke="#38BDF8" stroke-width="2.5"/>
              <!-- Crosshair Axes -->
              <line x1="-260" y1="0" x2="260" y2="0" stroke="#38BDF8" stroke-width="1.5" opacity="0.5"/>
              <line x1="0" y1="-260" x2="0" y2="260" stroke="#38BDF8" stroke-width="1.5" opacity="0.5"/>
              <!-- Rotating Sweep Line -->
              <line id="{prefix}_sweep" x1="0" y1="0" x2="160" y2="-160" stroke="#FACC15" stroke-width="4" stroke-linecap="round"/>
            </g>

            <!-- Header Badge -->
            <foreignObject x="80" y="240" width="920" height="150">
              <div style="text-align: center;">
                <span style="font-family: var(--font-mono); font-size: 18px; color: #38BDF8; letter-spacing: 0.15em; font-weight: 800;">SƠ ĐỒ NGUYÊN LÝ CHUYÊN SÂU</span>
                <h2 style="font-family: var(--font-primary); font-size: 46px; color: #FFFFFF; font-weight: 900; margin-top: 6px; letter-spacing: -0.02em;">{concept_title}</h2>
              </div>
            </foreignObject>

            <!-- Metric Cards -->
            <foreignObject x="80" y="1120" width="430" height="140">
              <div class="hud-callout-card">
                <div class="hud-callout-title">HIỆU SUẤT VẬN HÀNH</div>
                <div class="hud-callout-val" style="color: #38BDF8; font-size: 32px;">98.4%</div>
                <div style="font-family: var(--font-mono); font-size: 13px; color: #94A3B8;">TỐI ƯU HÓA HOÀN HẢO</div>
              </div>
            </foreignObject>
            <foreignObject x="570" y="1120" width="430" height="140">
              <div class="hud-callout-card" style="border-color: #FACC15;">
                <div class="hud-callout-title" style="color: #FACC15;">TẦN SỐ ĐIỀU BIÊN</div>
                <div class="hud-callout-val" style="color: #FACC15; font-size: 32px;">4.85 GHz</div>
                <div style="font-family: var(--font-mono); font-size: 13px; color: #94A3B8;">BĂNG THÔNG MỞ RỘNG</div>
              </div>
            </foreignObject>
          </svg>
        </div>
      </div>"""
            tweens.append(f"""
      // Rotating Radar Sweep Line
      tl.to("#{prefix}_sweep", {{ rotation: 360, transformOrigin: "0px 0px", duration: 3.0, repeat: -1, ease: "none" }}, {start_time});
      // Camera Pan & Gentle Zoom
      tl.fromTo("#{prefix}_schematic_cam", 
        {{ scale: 1.0, x: 40 }}, 
        {{ scale: 1.15, x: -40, duration: {duration}, ease: "power1.inOut" }}, 
        {start_time}
      );
""")

        elif grammar == "narrator_expert_explainer":
            # Human Presenter / Medical Doctor with Lip-Sync Talking Mouth Flap & Head Tilt
            char = CharacterRig2D.render_character_svg(
                f"{prefix}_doctor",
                archetype="expert_presenter",
                pose="explaining_pointer",
                expression="confident_explaining",
                x=360,
                y=1220,
                scale=1.05,
                duration=duration
            )
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <!-- Modern Clinical / High-Tech Studio Backdrop -->
        <div style="position: absolute; inset: 0; background: radial-gradient(circle at 65% 40%, #0F172A 0%, #020617 100%);"></div>
        <div style="position: absolute; right: 60px; top: 280px; width: 440px; height: 500px; border: 2px solid rgba(56, 189, 248, 0.3); border-radius: 20px; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(10px); padding: 24px;">
          <div style="font-family: var(--font-mono); font-size: 15px; color: #38BDF8; font-weight: 800; letter-spacing: 0.1em; border-bottom: 1px solid rgba(56, 189, 248, 0.2); pb: 8px;">
            HỒ SƠ PHÂN TÍCH CHUYÊN GIA
          </div>
          <div style="margin-top: 18px; font-family: var(--font-primary); font-size: 26px; font-weight: 800; color: #FFFFFF; line-height: 1.3;">
            Giải thích chi tiết cơ chế hoạt động
          </div>
          <div style="margin-top: 24px; display: flex; flex-direction: column; gap: 12px;">
            <div style="background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38BDF8; padding: 8px 12px; font-size: 14px; color: #E2E8F0; font-family: var(--font-mono);">
              Mức độ tin cậy: 99.8%
            </div>
            <div style="background: rgba(34, 197, 94, 0.1); border-left: 3px solid #22C55E; padding: 8px 12px; font-size: 14px; color: #E2E8F0; font-family: var(--font-mono);">
              Trạng thái: Đang trình bày
            </div>
          </div>
        </div>

        <!-- Vector Articulated Presenter -->
        <svg style="position: absolute; inset: 0; width: 100%; height: 100%;" viewBox="0 0 1080 1920">
          {char["svg"]}
        </svg>
      </div>"""
            adapted = [t.replace("tl.", f"{prefix}_tl.") for t in char["tweens"]]
            tweens.append(f"""
      const {prefix}_tl = gsap.timeline();
      {chr(10).join(adapted)}
      {prefix}_tl.fromTo("#{prefix}_view", {{ scale: 0.98 }}, {{ scale: 1.04, duration: {duration}, ease: "none" }}, 0.0);
      tl.add({prefix}_tl, {start_time});
""")

        else: # kinetic_statement
            words = narration.split()
            headline = " ".join(words[:5]) if len(words) >= 5 else narration
            html = f"""
      <div id="{prefix}_view" class="clip scene-viewport" data-start="{start_time}" data-duration="{duration}" data-track-index="0">
        <div style="padding: 0 60px; text-align: center; margin-top: -80px;">
          <div style="font-family: var(--font-mono); font-size: 26px; color: var(--accent); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 20px;">
            CHIẾN CÔNG VANG DỘI
          </div>
          <h1 id="{prefix}_head" style="font-size: 68px; font-weight: 900; line-height: 1.15; text-transform: uppercase; color: #FFFFFF; letter-spacing: -0.03em;">
            {headline}
          </h1>
        </div>
      </div>"""
            tweens.append(f"""
      tl.fromTo("#{prefix}_head", {{ scale: 0.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.6, ease: "power3.out" }}, {start_time + 0.1});
      tl.fromTo("#{prefix}_view", {{ scale: 1 }}, {{ scale: 1.06, duration: {duration}, ease: "none" }}, {start_time});
""")

        return html, tweens

    def _render_kinetic_pop_subtitles(
        self,
        scene_idx: int,
        start_time: float,
        duration: float,
        narration: str,
        subtitles_json: List[Dict[str, Any]]
    ) -> (str, List[str]):
        """
        Renders CapCut / TikTok / Instagram Reels standard kinetic subtitles:
        1. Phrase chunking (2-4 words per card, default 3 words) so only the current phrase is on screen.
        2. Dynamic "Khung Cam" (Vibrant Orange/Gold glowing pill badge) leaping under/behind the active word.
        3. Word-by-word bouncing highlight (scale 1.25, high-contrast glow, #FF6B00 / #FACC15).
        4. Automatic alignment with real TTS millisecond word boundaries.
        """
        words = narration.split()
        if not words:
            return "", []

        total_words = len(words)
        effective_dur = max(0.8, duration - 0.25)

        # Proportional syllable weights to prevent subtitle rushing or lagging
        weights = []
        for idx, w in enumerate(words):
            clean_len = max(1, len(re.sub(r'[^\w]', '', w)))
            wt = 0.70 + (clean_len * 0.12)
            if w.endswith(('.', '!', '?', ':', ';')):
                wt += 0.45
            elif w.endswith(','):
                wt += 0.25
            weights.append(wt)
        total_weight = sum(weights) or 1.0

        # Build list of word timings
        word_items = []
        running_time = start_time + 0.10

        for w_idx, w in enumerate(words):
            clean_text = re.sub(r'[^\w\s-]', '', w) or w
            if subtitles_json and len(subtitles_json) >= total_words:
                w_start_ms = subtitles_json[w_idx].get("start_ms", 0)
                w_end_ms = subtitles_json[w_idx].get("end_ms", 0)
                w_time = start_time + round(w_start_ms / 1000.0, 3)
                w_dur = max(0.12, round((w_end_ms - w_start_ms) / 1000.0, 3))
            else:
                w_dur = max(0.12, round((weights[w_idx] / total_weight) * effective_dur, 3))
                w_time = round(running_time, 3)
                running_time += w_dur

            word_items.append({
                "index": w_idx,
                "text": clean_text,
                "time": w_time,
                "duration": w_dur,
                "end_time": round(w_time + w_dur, 3),
                "id": f"w_{scene_idx}_{w_idx}",
            })

        # Chunk words into groups of 3 (or 2-4) words per card so subtitle doesn't dump whole paragraph on screen
        CHUNK_SIZE = 3
        chunks = []
        for i in range(0, len(word_items), CHUNK_SIZE):
            chunk_slice = word_items[i:i + CHUNK_SIZE]
            chunks.append(chunk_slice)

        chunk_html_parts = []
        tweens = []

        for c_idx, chunk in enumerate(chunks):
            chunk_id = f"sub_chunk_{scene_idx}_{c_idx}"
            c_start = chunk[0]["time"]
            c_end = chunk[-1]["end_time"]
            c_dur = max(0.3, round(c_end - c_start, 3))

            word_elements = []
            for w in chunk:
                # Clean text-only word without any box/borders wrapping it
                word_elements.append(f"""
                  <span id="{w['id']}" class="sub-word-text">{w['text']}</span>
                """)

            chunk_html_parts.append(f"""
              <div id="{chunk_id}" class="sub-phrase-card" style="opacity: 0; display: none;">
                {''.join(word_elements)}
              </div>
            """)

            # Animate phrase chunk card entry and exit
            tweens.append(f"""
      // Chunk {scene_idx}_{c_idx} appearance
      tl.set("#{chunk_id}", {{ display: "flex", opacity: 0, scale: 0.90, y: 15 }}, {c_start - 0.04});
      tl.to("#{chunk_id}", {{ opacity: 1, scale: 1.0, y: 0, duration: 0.14, ease: "back.out(2)" }}, {c_start});
      tl.to("#{chunk_id}", {{ opacity: 0, scale: 0.95, y: -10, duration: 0.1, ease: "power1.in" }}, {c_end});
      tl.set("#{chunk_id}", {{ display: "none" }}, {c_end + 0.11});
""")

            # Word-by-word bouncing highlight on the word text itself (no bounding boxes)
            for w in chunk:
                tweens.append(f"""
      tl.to("#{w['id']}", {{
        scale: 1.25,
        color: "#FF5722",
        textShadow: "0 0 32px rgba(255, 87, 34, 0.95), 0 0 12px #FF9800, 0 4px 14px rgba(0,0,0,0.9)",
        duration: 0.08,
        ease: "back.out(2.2)"
      }}, {w['time']});
      tl.to("#{w['id']}", {{
        scale: 1.0,
        color: "#FFFFFF",
        textShadow: "0 4px 18px rgba(0,0,0,0.95)",
        duration: 0.12,
        ease: "power2.inOut"
      }}, {w['end_time']});
""")

        html = f"""
      <div id="subs_{scene_idx}" class="clip subtitles-container" data-layout-ignore="true" data-layout-allow-safe-zone="true" data-layout-allow-overlap="true" data-start="{start_time}" data-duration="{duration}" data-track-index="4">
        {''.join(chunk_html_parts)}
      </div>"""

        return html, tweens
