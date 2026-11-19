# BACKEND REST API REFERENCE & CONTRACT SPECIFICATION
**Project:** Zero-Budget AI Video Studio (Vietnamese Shorts)  
**Document ID:** `docs/API_REFERENCE.md`  
**Base URL:** `https://api.yourdomain.com` or `http://localhost:8000`  
**Authentication:** Bearer Token (Supabase JWT via `Authorization: Bearer <token>`)  

---

## 1. Authentication & Security Headers

All protected endpoints require:
```http
Authorization: Bearer <supabase_jwt_token>
Content-Type: application/json
```
If the token is missing or invalid, the API returns:
```json
{
  "status": "error",
  "code": 401,
  "message": "Missing or invalid authorization token"
}
```

---

## 2. API Endpoints Specification

### 2.1 Health & System Status
#### `GET /api/v1/health`
* **Access:** Public
* **Response `200 OK`:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "providers": {
    "ai_engine": "groq-llama-3.3",
    "tts_engine": "piper-onnx-vivos",
    "asset_discovery": "wikimedia-openverse"
  }
}
```

---

### 2.2 AI Script Analysis & Structuring
#### `POST /api/v1/script/analyze`
* **Access:** Authenticated (Per-user rate limit: 2/day, max 1 in-flight)
* **Request Body:**
```json
{
  "script_text": "Ngày 12 tháng 04 năm 1831, 74 người lính bước đều qua cầu Broughton...",
  "target_duration_seconds": 60,
  "visual_style_preference": "adaptive"
}
```
* **Response `200 OK`:**
```json
{
  "status": "success",
  "title": "Bí Ẩn Cầu Broughton 1831",
  "estimated_syllables": 248,
  "estimated_duration_seconds": 58.5,
  "hook_summary": "74 người lính đánh sập cầu chỉ bằng cách bước đều",
  "scenes": [
    {
      "scene_order": 1,
      "scene_type": "hook",
      "narration_text": "74 người lính đã đánh sập một cây cầu sắt chỉ bằng cách... bước đều.",
      "duration_seconds": 5.0,
      "visual_method": "parallax",
      "visual_description": "Historical portrait of marching soldiers segmented against bridge backdrop",
      "suggested_asset_keywords": ["Broughton suspension bridge 1831", "British soldiers marching historical"]
    }
  ]
}
```

---

### 2.3 Vietnamese Voiceover Synthesis
#### `POST /api/v1/tts/synthesize`
* **Access:** Authenticated
* **Request Body:**
```json
{
  "text": "74 người lính đã đánh sập một cây cầu sắt chỉ bằng cách bước đều.",
  "voice": "vi-VN-NamMinhNeural",
  "rate": "+5%",
  "pitch": "+0Hz"
}
```
* **Response `200 OK`:**
```json
{
  "status": "success",
  "audio_url": "https://<supabase_storage>/voice/episode_123_scene_1.wav",
  "duration_seconds": 4.85,
  "words": [
    { "word": "74", "start_ms": 50, "end_ms": 420 },
    { "word": "người lính", "start_ms": 450, "end_ms": 950 },
    { "word": "đã", "start_ms": 980, "end_ms": 1180 }
  ]
}
```

---

### 2.4 Asset Discovery & License Verification
#### `GET /api/v1/assets/search?q={query}&type={image|video}&license={cc0|cc-by|all}`
* **Access:** Authenticated
* **Query Parameters:**
  * `q` (string, required): Search query (e.g., `Broughton suspension bridge`).
  * `type` (string, optional): `image` or `video` (default: `image`).
  * `license` (string, optional): `cc0`, `cc-by`, `pexels`, `all` (default: `all`).
* **Response `200 OK`:**
```json
{
  "status": "success",
  "query": "Broughton suspension bridge",
  "total_results": 12,
  "assets": [
    {
      "asset_id": "wm_839210",
      "title": "Broughton Suspension Bridge 1885 photograph",
      "media_type": "image",
      "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/.../640px-bridge.jpg",
      "full_url": "https://upload.wikimedia.org/wikipedia/commons/.../bridge.jpg",
      "source_provider": "wikimedia_commons",
      "source_page_url": "https://commons.wikimedia.org/wiki/File:Broughton_Bridge.jpg",
      "license_type": "Public Domain (CC0)",
      "author": "Archival Photo Bureau",
      "attribution_required": false
    }
  ]
}
```

---

### 2.5 Projects & Episodes Management
#### `GET /api/v1/projects`
* **Access:** Authenticated
* **Response `200 OK`:** Returns array of user projects filtered by `auth.uid() = user_id`.

#### `POST /api/v1/projects`
* **Access:** Authenticated
* **Request Body:**
```json
{
  "title": "Bí Ẩn Cầu Broughton",
  "description": "Shorts lịch sử về hiện tượng cộng hưởng cơ học"
}
```

#### `GET /api/v1/projects/{project_id}`
* **Access:** Authenticated (Owner only)
* **Response `200 OK`:** Returns project details, nested episodes, and scene manifests.

#### `DELETE /api/v1/projects/{project_id}`
* **Access:** Authenticated (Owner only)
* **Response `200 OK`:** Cascading delete of project, episodes, and assets.

---

### 2.6 Render Telemetry & Logging
#### `POST /api/v1/renders/log`
* **Access:** Authenticated
* **Request Body:**
```json
{
  "episode_id": "ep_123",
  "engine": "webcodecs-client",
  "client_browser": "Chrome 157 (macOS arm64)",
  "render_duration_sec": 9.23,
  "effective_fps": 195.1,
  "total_frames": 1800,
  "output_status": "completed"
}
```
* **Response `201 Created`:**
```json
{ "status": "logged", "job_id": "job_94821" }
```
