# IMPLEMENTATION STATUS — YTBER: UNIFIED AI VIDEO STUDIO

**Repository**: `thienduc-07/ytber`  
**Current Branch**: `feature/unified-ai-video-studio`  
**Status**: IN PROGRESS  
**Last Updated**: 2026-11-19 22:55:00+07:00  

---

## 1. Project Overview & Target Architecture
YTBER is a unified, publicly accessible, multi-user AI Video Production Studio operating on a zero-budget / free-tier-first model. It supports:
- **Short-form Video** (9:16 vertical, 15–180s: YouTube Shorts, TikTok, Reels)
- **Long-form Video** (16:9 horizontal, 5–60 min: Documentaries, Economics, Horror, Educational, Explainer with Chapter Planning, Segment Rendering, Assembly)
- **Genre Intelligence** (10 genres with specialized narrative, pacing, visual direction, voice direction, sound design)
- **Real Vietnamese Speech Synthesis** (Edge-TTS `vi-VN-NamMinhNeural` / `vi-VN-HoaiMyNeural` with word-boundary subtitle timestamps)
- **Real Media Discovery & Research** (Wikimedia Commons, Openverse with strict CC/PD licensing and attribution)
- **Fail-Closed Security & Multi-tenancy** (Strict JWT verification, user-isolated projects/quotas/storage)
- **High-Performance In-Browser & Backend Rendering** (WebCodecs + mp4-muxer fast-start containerization; segment-based assembly)

---

## 2. Phase Execution Matrix

| Phase | Description | Status | Evidence / Notes |
| :--- | :--- | :---: | :--- |
| **Phase 0** | Repository & Architecture Audit | **COMPLETE** | Full audit completed. Discovered in-memory store, JWT fail-open, mock audio URL, frontend-backend contract mismatch. |
| **Phase 1** | Critical Foundation (Security, DB, P0.1 Muxing) | **IN PROGRESS** | P0.1 MP4 muxing done (`mp4-muxer`). Now fixing fail-closed JWT & persistent DB storage (SQLite/Supabase). |
| **Phase 2** | Core Video Intelligence (10 Genres, Research, Assets) | **QUEUED** | Multi-genre schema, chaptering, Wikimedia/Openverse research engine. |
| **Phase 3** | Media Production (Edge-TTS, Sound Design, Timeline) | **QUEUED** | Real edge-tts Vietnamese voice provider + audio streaming endpoint + sound ducking. |
| **Phase 4** | Product Workflows (Shorts, Long-form, Horror) | **QUEUED** | Shorts & Long-form chapter pipeline, Horror tension escalation engine. |
| **Phase 5** | Public SaaS Foundation (Auth, Quotas, Rate Limiting) | **QUEUED** | User isolation, token bucket rate limiter, resource caps. |
| **Phase 6** | UX/UI & Frontend Integration | **QUEUED** | Connect ScriptStudio, Dashboard, Storyboard to real backend with auth tokens & aligned payloads. |
| **Phase 7** | Quality Assurance, Real Tests & Verification | **QUEUED** | Pytest 100% pass, frontend build pass, end-to-end video generation and inspection. |

---

## 3. Discovered Technical Debt & Action Items
1. **Security Vulnerability (`backend/core/security.py`)**:
   - *Problem*: `if jwt_secret and not jwt_secret.startswith("placeholder-"):` allowed completely skipping signature verification when secret is missing or placeholder.
   - *Action*: Implement strict fail-closed JWT verification using `PyJWT` or standard crypto with algorithm validation (`HS256`, `RS256`), rejecting unverified/expired tokens.
2. **Ephemeral In-Memory Persistence (`backend/routers/projects.py`)**:
   - *Problem*: `_PROJECTS_STORE` and `_EPISODES_STORE` in-memory dictionaries lose all data on backend restart.
   - *Action*: Implement SQLite / SQLAlchemy / Supabase persistence with ACID transactions, indexing, foreign keys, and user ownership isolation.
3. **Synthetic Audio & Placeholder TTS (`backend/providers/tts_engine.py`)**:
   - *Problem*: Returns dummy `/api/v1/tts/sample_audio.wav` without real audio synthesis.
   - *Action*: Implement `EdgeTTSVoiceProvider` generating real MP3 audio and word-level millisecond subtitle cues. Add static/streaming audio file serving.
4. **Frontend-Backend Contract Mismatch**:
   - *Problem*: Frontend `ScriptStudioPage.tsx` and `StoryboardEditor.tsx` send unauthenticated requests with mismatched keys (`pacing_preference` vs `target_duration_seconds`, `query` vs `q`).
   - *Action*: Align API request/response schemas and include `Authorization: Bearer <token>` in frontend API client.
5. **Genre Intelligence & Long-Form Pipeline**:
   - *Problem*: Current system only has a 1-level 60s Shorts prompt.
   - *Action*: Implement 10-genre intelligence system, chapter planning, and long-form 16:9 segment orchestration.
