# PREMIUM 2.5D ANIMATED CONTENT PRODUCTION & COMMERCIALIZATION ARCHITECTURE
**Platform:** YTBER Unified AI Video Studio  
**Branch:** `feature/unified-ai-video-studio`  
**Status:** Production Operational  

---

## 1. System Overview

YTBER transforms Vietnamese scripts and topic ideas into broadcast-ready, commercially viable 2.5D animated videos with 100% vector-animated visuals, zero reliance on live-action footage, and complete zero-budget client-side WebCodecs MP4 rendering.

```
                    ┌──────────────────────────────────────────────┐
                    │               User Script / Topic            │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │              AI Research Engine              │
                    │   Verified Facts • Entities • Narrative Hook │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │             AI Director Engine               │
                    │      17 Production Attributes • 7 Layers     │
                    └──────────────────────┬───────────────────────┘
                                           │
                    ┌──────────────────────┴───────────────────────┐
                    ▼                                             ▼
┌──────────────────────────────────────┐       ┌─────────────────────────────────────┐
│       Edge-TTS & Audio Pipeline      │       │      2.5D Temporal Animation Engine │
│  • Edge-TTS Neural Voice (vi-VN)     │       │  • Layer 1: Atmosphere & Celestial  │
│  • Soundscape Director (Ambience)    │       │  • Layer 2: Multi-Plane Parallax    │
│  • Action-to-Sound Footsteps Sync    │       │  • Layer 3: Vector Characters & Prop│
│  • Dynamic Ducking (-17dB)           │       │  • Layer 4: Foreground Occlusion    │
│  • 48kHz Stereo AAC Encoding         │       │  • Layer 5: Dynamic Particle Field  │
└──────────────────┬───────────────────┘       │  • Layer 6: Volumetric Light Rays   │
                   │                           │  • Layer 7: Vignette & Color Grade  │
                   │                           └──────────────────┬──────────────────┘
                   ▼                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                    Client-Side In-Browser WebCodecs Renderer                       │
│              • Canvas 2D Frame Compositing • H.264 VideoEncoder (AVC1)             │
│              • AAC AudioEncoder (48kHz Stereo) • Fast MP4 Muxer (ISOBMFF)          │
└──────────────────────────────────────────┬─────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                       Automated Quality Control (AQC) Suite                        │
│            • ISOBMFF Valid Box Hierarchy (ftyp, moov, mdat)                        │
│            • Temporal Motion Delta (Delta >= 0.003, no slideshows)                 │
│            • 100% Animated Visual Policy (Vector/Palette Compliance >= 0.85)       │
│            • 3-Layer Audio + Mandatory Vietnamese Voiceover Verification           │
└────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Pillars

### Pillar I: AI Research & Fact Verification Engine
- **Module:** `backend/providers/research_engine.py` & `backend/routers/research.py`
- **Capabilities:**
  - Performs multi-perspective domain research prior to script generation across History, Economics, Technology, Astronomy, and Earth Sciences.
  - Generates `TopicResearchReport` with structured `verified_facts` (containing verified claims and reputable reference URLs), `key_entities` (costumes, props, and 2.5D visual directives), `storytelling_angles`, and audience retention narrative hooks.
  - Formulates commercial affiliate strategies with compliant disclosure notices.

### Pillar II: 7-Layer 2.5D Cinematic Animation Architecture
- **Module:** `frontend/src/services/animationEngine.ts`
- **Layers:**
  1. **Layer 1 (Atmosphere & Celestial Glow):** Dynamic sky gradient transitions (sunset, moonlight, dawn, cyber grid) with radial atmospheric halos.
  2. **Layer 2 (Multi-Plane Parallax Environment):** Distant mountain/canopy silhouettes ($0.2\times$ parallax), closer terrain ridges ($0.5\times$ parallax), and grounded action stage ($1.0\times$ parallax).
  3. **Layer 3 (Vector Characters & Tactical Visuals):**
     - Articulated character rigs with inverse kinematics walk cycles, strained pulling stances, cheering poses, and point gestures.
     - Dynamic elliptical contact shadows grounded under character feet.
     - Directional 3D rim lighting highlighting head and torso volumes.
     - Mouth-flap speech animation synchronized with voice activity.
     - Animated motion graphics: animated spline bar charts and pulsing network topologies.
     - Animated vector tactical maps with bezier route tracing and pulsing destination pins.
  4. **Layer 4 (Foreground Occlusion & Framing):** Hanging tropical liana vines, palm fronds, and foliage silhouettes moving at fast parallax ($1.35\times$) to create natural foreground depth.
  5. **Layer 5 (Environmental Particle Field):** Floating luminous fireflies, pollen spores, rising embers, or data streams.
  6. **Layer 6 (Volumetric Sunlight Shafts):** Screen-blended angled god rays streaming from celestial coordinates.
  7. **Layer 7 (Cinematic Vignette & Grading):** Subtle radial vignette framing the action zone.

### Pillar III: 3-Layer Audio Production & Dynamic Ducking
- **Module:** `backend/providers/soundscape_engine.py` & `frontend/src/services/soundDesignEngine.ts`
- **Bus Architecture:**
  - **Layer 1 (Voiceover Bus - 0dB Priority):** Decoded Edge-TTS Vietnamese neural speech (`vi-VN-NamMinhNeural` or `vi-VN-HoaiMyNeural`). Mandatory for production; videos fail if speech is absent or silent.
  - **Layer 2 (Environmental Soundscape Bus - Ambient):** Synthesized or preloaded high-fidelity environmental beds derived from scene semantics (tropical forest cicadas and canopy wind, mountain battlefield trench rumble, financial floor ambience, cyber server hum).
  - **Layer 3 (Action SFX Bus - Transients):** Action-synchronized sound effects. Walking cycle triggers footsteps on dry leaves/soil at $2.2\text{Hz}$ cadence; camera pans trigger whoosh risers; financial charts trigger coin chimes.
  - **BGM Bus & Dynamic Ducking:** Background music automatically attenuates by $-17\text{dB}$ with a smooth $80\text{ms}$ attack whenever voiceover is active, recovering with a $350\text{ms}$ release during pauses.

### Pillar IV: Commercial Content & Affiliate Engine
- **Module:** `frontend/src/services/webcodecsRenderer.ts`, `RemotionPlayer.tsx`, & `ScriptStudioPage.tsx`
- **Features:**
  - In-manifest affiliate campaign configuration: `product_name`, `affiliate_url`, `cta_style`, and `disclosure_text`.
  - Dynamic aspect ratio support: $9:16$ Portrait Shorts/Reels/TikTok and $16:9$ Landscape YouTube.
  - Non-intrusive animated CTA banner overlay with pulse dynamics and transparent disclosure notice.

### Pillar V: Automated Quality Control (AQC) Engine
- **Module:** `backend/services/quality_control.py`
- **Standards:**
  1. `validate_isobmff_mp4`: Verifies valid container boxes (`ftyp`, `moov`, `mdat`), H.264 video stream, and AAC 48kHz audio.
  2. `validate_temporal_motion`: Computes normalized frame delta across video intervals. Rejects static slideshows ($\Delta < 0.003$).
  3. `validate_animated_visual_policy`: Analyzes edge gradients and color palette clusters. Rejects photographic sensor grain ($\ge 85\%$ animated style compliance required).
  4. `validate_three_layer_audio`: Ensures dynamic range between speech and background beds.
  5. `validate_mandatory_voiceover`: Bandpasses speech frequencies ($250\text{Hz} - 2500\text{Hz}$) and checks envelope variance to guarantee human-like speech.
  6. `validate_environmental_soundscape`: Checks for ambient high/low frequency profiles matching expected environment.
