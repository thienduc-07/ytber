# PHASE 3 — REAL ASSET DISCOVERY & VIDEO RENDERING ARCHITECTURE
**Project:** YTBER — Unified AI Video Studio  
**Author:** Principal Software Architect & Video Infrastructure Engineer  
**Branch:** `feature/unified-ai-video-studio`  
**Status:** ARCHITECTURE APPROVED — IMPLEMENTATION IN PROGRESS  
**Date:** 2026-11-20

---

## 1. System Architecture Overview

Phase 3 transforms YTBER from a vector-based schematic renderer into a full-scale, real-world media production pipeline. The system automates the complete creative cycle:
1. **Script Analysis:** Structured decomposition of Vietnamese narrative into narrative stages and scenes.
2. **Intelligent Scene Query Formulation:** Automatic translation of scene context into concrete visual search queries (prioritizing actual facilities, locations, charts, and archival photography over generic stock).
3. **Multi-Source Permissive Asset Discovery:** Aggregated discovery across Wikimedia Commons, Openverse, and optional Pexels without paid API requirements.
4. **Hardened Asset Download & Storage:** SSRF-safe streaming download, magic-byte MIME validation, image dimension extraction, SHA-256 content deduplication, and multi-tenant access control.
5. **Licensing & Attribution Manifest:** Automated preservation of creators, license types, source URLs, and generation of attribution slides and downloadable `credits.txt`.
6. **In-Browser WebCodecs Real Media Rendering:** Real-time canvas rendering of decoded image assets (`createImageBitmap`), Ken Burns pan & zoom, transitions, and fallback graphics.
7. **Production Voiceover & Subtitle Integration:** Dual-track audio mixing (Edge-TTS narration + dynamic BGM bed with auto-ducking) encoded into AAC, synchronized with Phase 2 millisecond-exact karaoke subtitles.
8. **MP4 Containerization:** Standards-compliant MP4 muxing using `mp4-muxer` (fastStart in-memory, AVC/H.264 + AAC).

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USER BROWSER / STUDIO UI                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 1. Submit Vietnamese Script
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    BACKEND FASTAPI / SCRIPT ROUTER                     │
│  - AIScriptProvider / RuleBasedScriptProvider / GroqScriptProvider     │
│  - Vietnamese NLP Syllable Pacing & Scene Planning                     │
│  - Intelligent Visual Keyword Formulation (Concrete visual concepts)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 2. Structured Scene Plans
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       ASSET DISCOVERY ENGINE                           │
│  - WikimediaCommonsProvider (Public Domain / CC-BY / CC-BY-SA)         │
│  - OpenverseProvider (Creative Commons Permissive Aggregator)          │
│  - PexelsProvider (Optional free API key configuration)                │
│  - Relevance, Resolution, and License Filter                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 3. Discovered Permissive Assets
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    SECURE ASSET DOWNLOAD & STORAGE                     │
│  - Anti-SSRF Resolver & Private IP / Loopback Blocking                │
│  - Stream Pipeline with Max Size Limiting (20MB Image / 50MB Video)    │
│  - Magic-Byte Header Sniffing & Dimension Verification (Pillow)        │
│  - Content SHA-256 Deduplication & Multi-Tenant Database Association   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 4. Stitched Audio & Downloaded Assets
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 CLIENT-SIDE WEBCODECS MEDIA RENDERER                   │
│  - Bounded Asset Preloading (Async Image Fetch & createImageBitmap)    │
│  - Canvas 2D Engine: Cover/Contain Fit, Smooth Ken Burns Motion        │
│  - Crossfade & Cut Scene Transitions                                   │
│  - Audio Mixer: Decoded Narration PCM + BGM with Auto-Ducking          │
│  - Karaoke Animated Subtitles (Synced with Phase 2 Word Timestamps)    │
│  - Hardware-Accelerated VideoEncoder (H.264) + AudioEncoder (AAC)      │
│  - MP4 Muxer Containerization (mp4-muxer)                              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 5. Valid 1080x1920 MP4 Download
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       COMPLETED HIGH-QUALITY VIDEO                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Existing vs. Upgraded Components

| Component | Prototype Status (Phase 2) | Upgraded Production Status (Phase 3) |
| :--- | :--- | :--- |
| **Asset Discovery** | Hardcoded Wikimedia + Openverse queries with no provider interface and no fallback. | **Modular Provider Architecture** (`AssetProvider` interface), concurrency handling, rate-limit resilience, deduplication, and optional Pexels support. |
| **Search Querying** | Generic labels (`"historical photography"`, `"documentary footage"`). | **Intelligent Domain-Specific Query Formulation:** Translates abstract narrative concepts into physical facilities, objects, locations, and data visualizations. |
| **Asset Storage** | Pure URLs returned to client; client fetches directly (CORS failures, broken links). | **Secure Asset Downloader Service:** Backend validates, downloads, deduplicates via SHA256, stores on disk, and serves via authenticated local proxy. |
| **SSRF Defense** | None (client requested URLs directly). | **Multi-layer SSRF Shield:** IP resolution check, loopback/private subnet blocking (`10/8`, `172.16/12`, `192.168/16`, `127/8`, `169.254/16`), hop-by-hop redirect verification. |
| **Licensing Compliance** | Partial text display in UI; no formal attribution tracking. | **Attribution Manifest System:** Tracks creator, license type, license URL, source page, generates downloadable `credits.txt` and closing credits sequence. |
| **Visual Rendering** | Abstract vector procedural graphics (circles, grids, gradients). | **Real Media Canvas Pipeline:** Decodes real images with `createImageBitmap`, applies aspect ratio fitting (`cover`/`contain`), smooth Ken Burns pan/zoom, and crossfades. |
| **Audio Rendering** | Procedural sine-wave beep bed. | **Real Audio Mixing:** Loads actual Phase 2 Edge-TTS audio, decodes PCM, mixes with background music with auto-ducking, encodes stereo AAC at 48kHz. |
| **Subtitles** | Linear approximation `Math.floor(t * words.length)`. | **Karaoke Sync:** Uses millisecond-exact word timings from Phase 2, word highlighting, Vietnamese Unicode line wrapping. |
| **Video Decoding** | Unsupported. | **Browser Video Support & Capability Detection:** Inspects video decode capability, trims scene segments, falls back gracefully to poster frame. |

---

## 3. Modular Asset Discovery Architecture

### 3.1 Standardized Asset Data Contract
Every asset returned by the discovery layer adheres to a strict contract:
```json
{
  "asset_id": "wm_123456",
  "provider": "wikimedia_commons",
  "source_url": "https://commons.wikimedia.org/wiki/File:Ha_Noi_1954.jpg",
  "download_url": "https://upload.wikimedia.org/wikipedia/commons/.../Ha_Noi_1954.jpg",
  "title": "Ha Noi tiep quan 1954",
  "description": "Historical photograph of military parade in Hanoi, 1954",
  "creator": "Nguyen Van A",
  "license": "CC-BY-SA 4.0",
  "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
  "width": 1920,
  "height": 1080,
  "media_type": "image",
  "attribution_required": true
}
```

### 3.2 Provider Registry
- **`WikimediaCommonsProvider`:**
  - Endpoint: `https://commons.wikimedia.org/w/api.php`
  - Generator search: `action=query&generator=search&gsrnamespace=6`
  - Properties extracted: `url|extmetadata|dimensions|mime`
  - Filters: JPEG, PNG, WebP, MP4, WebM; excludes SVGs for direct video rendering unless rasterized.
- **`OpenverseProvider`:**
  - Endpoint: `https://api.openverse.org/v1/images/`
  - Permissive licenses: `all-cc` (`pdm`, `cc0`, `by`, `by-sa`)
  - Metadata parsing: Creator, license URL, foreign landing URL.
- **`PexelsProvider` (Optional):**
  - Endpoint: `https://api.pexels.com/v1/search`
  - Requires `PEXELS_API_KEY` in environment. If omitted, engine runs 100% free without errors.

---

## 4. Intelligent Scene Search Formulation

The system maps script sentences to concrete visual search queries, prioritizing physical entities over abstract words:

### 4.1 Economics & Financial Narratives
- *"Giá dầu thế giới tăng mạnh"* $\to$ `crude oil refinery`, `oil barrels`, `petroleum trading`, `oil tanker ship`
- *"Lạm phát và tăng trưởng GDP"* $\to$ `financial stock market chart`, `central bank building`, `container cargo port`, `factory production line`
- *"Thị trường bất động sản đóng băng"* $\to$ `modern commercial skyscraper`, `urban construction site`, `housing development aerial`

### 4.2 Historical & Archival Narratives
- *"Chiến thắng Điện Biên Phủ năm 1954"* $\to$ `Dien Bien Phu 1954 archival photograph`, `Vo Nguyen Giap historic portrait`, `artillery transport Vietnam history`
- *"Hà Nội tiếp quản thủ đô"* $\to$ `Hanoi historic flag 1954`, `Thang Long historic city gate`, `Hoan Kiem lake archival vintage`

---

## 5. Secure Asset Downloader & Storage Pipeline

### 5.1 Anti-SSRF Defense Specification
1. **URL Scheme Check:** Only `http` and `https` allowed; file, gopher, ftp, ldap rejected.
2. **DNS & IP Pinning:**
   - Resolves target host to IP addresses.
   - Verifies all resolved IPs against IANA reserved subnets:
     - `127.0.0.0/8` (Loopback)
     - `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (Private Intranet)
     - `169.254.0.0/16` (Link-local / AWS instance metadata `169.254.169.254`)
     - `0.0.0.0/8` (Local host)
     - `::1` (IPv6 Loopback)
3. **Redirect Protection:** Disables automatic redirect following in HTTP client; manually checks each target location header against the SSRF validator.

### 5.2 Content Validation & Deduplication
- **Stream Limiting:** Aborts if downloaded bytes exceed `MAX_ASSET_SIZE_BYTES` (20MB for images).
- **Magic-Byte Sniffing:**
  - JPEG: `\xFF\xD8\xFF`
  - PNG: `\x89PNG\r\n\x1a\n`
  - WebP: `RIFF....WEBP`
  - MP4: `....ftyp`
- **Integrity & Dimension Check:** Pillow `Image.open()` validates image headers and extracts true width/height without executing untrusted decoders.
- **SHA-256 Storage:** File saved to `data/assets/{sha256}.{ext}`. Duplicate downloads of the same image instantly resolve to the cached file.
- **Database Index:** `AssetModel` records file metadata, provider, license, and owner tenant.

---

## 6. Real-Media WebCodecs Canvas Rendering Pipeline

### 6.1 Image Preloading & Decoding
```typescript
// Bounded preloading with concurrency limit
const imageBitmaps = await Promise.all(
  assets.map(async (asset) => {
    const res = await fetch(asset.local_url || asset.source_url);
    const blob = await res.blob();
    return await createImageBitmap(blob);
  })
);
```

### 6.2 Aspect Ratio Fitting (`cover` vs `contain`)
For a target canvas of $W \times H$ (e.g. $1080 \times 1920$ for 9:16 Shorts):
```typescript
function drawImageCover(ctx, img, targetW, targetH, zoom, panX, panY) {
  const imgAspect = img.width / img.height;
  const targetAspect = targetW / targetH;
  let sW, sH, sX, sY;

  if (imgAspect > targetAspect) {
    sH = img.height;
    sW = sH * targetAspect;
    sX = (img.width - sW) / 2 + panX;
    sY = (img.height - sH) / 2 + panY;
  } else {
    sW = img.width;
    sH = sW / targetAspect;
    sX = (img.width - sW) / 2 + panX;
    sY = (img.height - sH) / 2 + panY;
  }
  ctx.drawImage(img, sX, sY, sW, sH, 0, 0, targetW, targetH);
}
```

### 6.3 Ken Burns Camera Dynamics
- Smooth zoom: $scale(t) = 1.0 + t \times 0.12$ ($0 \le t \le 1$).
- Smooth pan: $x(t) = \Delta x \times t$, $y(t) = \Delta y \times t$.
- Scene crossfade: Linear opacity interpolation between scene $N$ and scene $N+1$ over a 15-frame window.

### 6.4 Audio Stem Mixing & AAC Encoding
1. Fetch narration MP3 from `/api/v1/tts/audio/{filename}`.
2. Decode to raw Float32Array PCM samples via Web Audio `AudioContext.decodeAudioData`.
3. Synthesize/Mix background ambience with dynamic ducking (volume $0.10$ during voiceover, $0.25$ during pauses).
4. Feed 48,000Hz stereo `AudioData` chunks into WebCodecs `AudioEncoder` (`mp4a.40.2`).
5. Multiplex synchronously into the final MP4 with video frames.

---

## 7. Verification & Acceptance Criteria

1. **Asset Discovery:** Search queries return verified assets with complete metadata from Wikimedia and Openverse.
2. **Download & Security:** External media downloads are validated, checked for SSRF, deduplicated by SHA256, and served safely.
3. **Licensing Manifest:** Attribution manifest is generated with valid creator and license information.
4. **Real Canvas Rendering:** Images are loaded, decoded with `createImageBitmap`, rendered with Ken Burns motion, and properly disposed.
5. **Real Audio & Subtitles:** Edge-TTS speech is mixed into AAC; karaoke subtitles animate based on millisecond cues.
6. **End-to-End MP4 Export:** The system generates a valid 1080x1920 MP4 file with real visuals and real narration for a multi-scene Vietnamese script.
