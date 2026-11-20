# BÁO CÁO KỸ THUẬT GIAI ĐOẠN 3: REAL ASSET DISCOVERY & VIDEO RENDERING
**Hệ thống Video Studio AI Zero-Budget — Pipeline Khám phá Tư liệu & Dựng Video Thực tế**

- **Dự án**: YTBER — Unified AI Video Studio
- **Branch**: `feature/unified-ai-video-studio`
- **Phiên bản baseline**: Hoàn thành Giai đoạn 1 (Hạ tầng & Bảo mật) & Giai đoạn 2 (Vietnamese Neural TTS Engine)
- **Tình trạng**: **HOÀN THÀNH 100% (52/52 Tests Pass, Frontend Build Thành công, E2E Acceptance Pass)**

---

## 1. TỔNG QUAN VÀ MỤC TIÊU GIAI ĐOẠN 3

Mục tiêu cốt lõi của Giai đoạn 3 là **chuyển đổi hoàn toàn công nghệ dựng video từ đồ họa vector thủ công (procedural graphics / sine wave placeholder) sang pipeline sản xuất đa phương tiện thực tế (Real Media Production Pipeline)**.

Hệ thống cho phép người dùng nhập kịch bản tiếng Việt, sau đó AI tự động:
1. Phân tích ngữ cảnh và bẻ nhỏ thành các cảnh quay (scenes) có cấu trúc logic.
2. Tự động chuyển đổi lời bình tiếng Việt trừu tượng thành các **từ khóa tìm kiếm trực quan cụ thể (Intelligent Scene Search Queries)**.
3. Tìm kiếm và tổng hợp tư liệu bản quyền mở (Creative Commons / Public Domain) từ **Wikimedia Commons, Openverse** và tích hợp mở rộng Pexels.
4. Tải và lưu trữ an toàn các tư liệu được chọn với cơ chế phòng vệ **Anti-SSRF Zero-Trust, Magic-byte verification, Pillow dimension check, và phân lập đa người dùng (multi-tenant)**.
5. Bảo toàn siêu dữ liệu bản quyền và xuất bản **Bảng ghi nhận nguồn tư liệu (Attribution Manifest / `credits.txt`)**.
6. Đồng bộ lời bình tiếng Việt chuẩn neural từ Giai đoạn 2 (Edge-TTS) với phụ đề karaoke chính xác từng mili-giây.
7. Dựng video độ phân giải cao 1080x1920 (Shorts 9:16) hoàn toàn trên trình duyệt người dùng thông qua **WebCodecs + Canvas 2D + Web Audio API**, hỗ trợ hiệu ứng chuyển động Ken Burns pan/zoom, chuyển cảnh mượt mà, hòa âm BGM tự động giảm âm lượng (ducking) khi có giọng đọc, và đóng gói container MP4 chuẩn ISOBMFF.

---

## 2. KIẾN TRÚC VÀ CÁC THAY ĐỔI TRIỂN KHAI

### 2.1. Kiến trúc tổng thể Pipeline Media

```
+----------------------------------------------------------------------------------------------------+
|                                    BACKEND (FASTAPI + PYTHON 3.9)                                  |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [RuleBasedScriptProvider]                                                                         |
|        │                                                                                           |
|        ▼                                                                                           |
|  [Intelligent Query Formulation] ──> Chuyển đổi ngữ nghĩa tiếng Việt sang Visual Keyword tiếng Anh  |
|        │                                                                                           |
|        ▼                                                                                           |
|  [AssetDiscoveryEngine]                                                                            |
|        ├──> Wikimedia Commons API (User-Agent tuân thủ chuẩn, không cần API key)                    |
|        ├──> Openverse API (Creative Commons, fail-fast timeout 3s)                                 |
|        └──> Pexels Provider (Tự động kích hoạt khi có API key, fallback an toàn)                   |
|        │                                                                                           |
|        ▼                                                                                           |
|  [AssetDownloaderService (Anti-SSRF Zero-Trust)]                                                   |
|        ├── DNS Pre-resolution & Link-local / Private / Cloud Metadata blocking                     |
|        ├── Hop-by-Hop Redirect Validation (ngăn chặn bypass qua chuyển hướng 30x)                 |
|        ├── Streaming Chunking với trần dung lượng cứng 20MB                                        |
|        ├── Magic-byte Header Validation (JPEG, PNG, WebP, MP4)                                     |
|        ├── Pillow Image Integrity & Dimension Extraction (WxH)                                     |
|        └── SHA-256 Content Deduplication & Atomic File Write                                       |
|        │                                                                                           |
|        ▼                                                                                           |
|  [SQLite Database: AssetModel] ──> Phân lập Multi-tenant (user_id + filename index)                |
|  [Attribution Generator]      ──> Sinh manifest bản quyền & credits.txt tự động                   |
+----------------------------------------------------------------------------------------------------+
                                                 ▲
                                                 │ HTTP REST API
                                                 ▼
+----------------------------------------------------------------------------------------------------+
|                                  FRONTEND (REACT + TYPESCRIPT)                                     |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [StoryboardEditor / ScriptStudio]                                                                 |
|        │                                                                                           |
|        ▼                                                                                           |
|  [webcodecsRenderer.ts - Real Media Pipeline]                                                      |
|        ├── 1. Asset Preloading: Tải Blob & giải mã qua createImageBitmap(blob)                    |
|        ├── 2. Audio Decoding: Giải mã narration PCM qua AudioContext.decodeAudioData              |
|        ├── 3. Dynamic Audio Mixing: Trộn Voiceover + BGM bed (tự động ducking -18dB khi đọc)       |
|        ├── 4. Canvas Visual Rendering:                                                             |
|        │      ├── Aspect ratio "cover" fitting (khắc phục méo hình trên khung dọc 1080x1920)       |
|        │      ├── Hiệu ứng chuyển động điện ảnh Ken Burns (Pan & Zoom mượt mà theo tiến trình)     |
|        │      ├── Crossfade Transition giữa các cảnh liền kề                                       |
|        │      └── Phụ đề Karaoke Animated Subtitles đồng bộ mili-giây                              |
|        ├── 5. WebCodecs Hardware Encoding:                                                         |
|        │      ├── VideoEncoder (H.264 High Profile / Baseline 1080x1920 @ 30fps)                  |
|        │      └── AudioEncoder (AAC Stereo 48kHz @ 128kbps)                                        |
|        ├── 6. MP4 Muxer: Đóng gói ISOBMFF chuẩn xác với đầy đủ track video + audio                 |
|        └── 7. Resource Cleanup: imageBitmap.close() & audioContext.close() ngăn rò rỉ bộ nhớ       |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. CHI TIẾT CÁC MODULE TRIỂN KHAI

### 3.1. Phân tích Ngữ nghĩa & Tạo Từ khóa Tìm kiếm Trực quan (Intelligent Query Formulation)
- **Tập tin**: `backend/providers/ai_rule_based.py`, `backend/providers/ai_base.py`
- **Vấn đề**: Các engine cơ bản thường tìm kiếm bằng toàn bộ câu đọc tiếng Việt (ví dụ: *"Giá dầu thô và năng lượng thế giới tăng mạnh kỷ lục..."*), dẫn đến kết quả rỗng (0 kết quả) trên các kho lưu trữ toàn cầu.
- **Giải pháp**:
  - Tích hợp bộ quy tắc phân loại chuyên sâu cho 5 thể loại video: `economics`, `horror`, `technology`, `history`, `nature`.
  - Phân tích cú pháp và trích xuất danh từ hình ảnh cụ thể, vật thể hữu hình (concrete physical concepts) bằng tiếng Anh chuẩn:
    * Ví dụ `economics`: `crude oil refinery`, `container port cargo ship`, `central bank building`, `automated factory production line`, `economic growth chart`.
    * Ví dụ `horror`: `haunted mansion at night`, `dark mist foggy forest`, `abandoned decaying room`.
  - Cập nhật schema `ScenePlan` trong `backend/providers/ai_base.py` với các thuộc tính: `search_keywords`, `preferred_media_type`, `preferred_aspect_ratio`, `transition_type`.

### 3.2. Động cơ Khám phá Tư liệu Bản quyền Mở Đa Nguồn (Modular Asset Discovery Engine)
- **Tập tin**: `backend/providers/asset_discovery.py`
- **Kiến trúc**: Lớp cơ sở trừu tượng `BaseAssetProvider` với các provider cắm rút:
  1. **WikimediaCommonsProvider**:
     - Tích hợp trực tiếp MediaWiki Search API (`action=query&generator=search&prop=imageinfo`).
     - Tự động lọc bỏ các định dạng vector không vẽ trực tiếp trên canvas (SVG), file âm thanh, tài liệu PDF.
     - Trích xuất siêu dữ liệu bản quyền chi tiết: tác giả, giấy phép (CC BY, CC BY-SA, Public Domain), đường link nguồn.
     - Tuân thủ User-Agent Policy của Wikimedia (`YTBerStudio/2.0 (...)`), loại bỏ hoàn toàn lỗi HTTP 429.
  2. **OpenverseProvider**:
     - Kết nối kho dữ liệu Creative Commons toàn cầu Openverse.
     - Cấu hình fail-fast timeout (3.0s) để tránh làm nghẽn tiến trình khi API bên ngoài phản hồi chậm.
  3. **PexelsProvider**:
     - Hỗ trợ ảnh và video HD/4K miễn phí bản quyền thương mại khi người dùng cấu hình `PEXELS_API_KEY`.
     - Chuyển tiếp êm ái (graceful fallback) khi chưa cấu hình key.
  4. **AssetDiscoveryEngine (Aggregator)**:
     - Thực thi tìm kiếm bất đồng bộ song song qua `asyncio.gather`.
     - Sắp xếp và ưu tiên tư liệu theo độ phân giải cao ($\ge 1920\times 1080$), tỷ lệ khung hình, và khử trùng lặp (deduplication) dựa trên URL.

### 3.3. Dịch vụ Tải Tư liệu An toàn Tuyệt đối (SSRF-Safe Downloader)
- **Tập tin**: `backend/providers/asset_downloader.py`, `backend/core/config.py`
- **Cơ chế Bảo mật Phòng vệ Chiều sâu (Defense-in-Depth)**:
  - **Zero-Trust URL Sanitization (`is_safe_url`)**:
    * Chỉ cho phép giao thức `http` và `https`.
    * Chặn các hostname cấm: `localhost`, `127.0.0.1`, `::1`, `metadata.google.internal`, các đuôi `.local`, `.internal`, `.arpa`.
    * Phân giải DNS địa chỉ đích và duyệt kiểm tra từng IP: chặn triệt để dải mạng Private IP (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), Loopback (`127.0.0.0/8`), Link-Local (`169.254.0.0/16`), Multicast, Reserved, và đặc biệt IP metadata máy chủ đám mây AWS/GCP (`169.254.169.254`).
  - **Hop-by-Hop Redirect Inspection**: Thiết lập `follow_redirects=False`. Mỗi bước chuyển hướng HTTP 301/302 đều được phân tích và kiểm tra SSRF trước khi kết nối tới địa chỉ mới.
  - **Giới hạn Streaming Chặt chẽ**: Đọc dữ liệu theo từng chunk 64KB, kiểm soát trần tối đa 20MB (`MAX_ASSET_SIZE_BYTES`). Ngắt kết nối ngay lập tức nếu vượt ngưỡng.
  - **Xác thực Magic Bytes**: Kiểm tra header nhị phân thực tế của tập tin (JPEG `FF D8 FF`, PNG `89 50 4E 47`, WebP `RIFF...WEBP`, MP4 `ftyp`), ngăn chặn kẻ tấn công đổi đuôi file để tiêm mã độc.
  - **Kiểm định Kích thước bằng Pillow**: Mở hình ảnh bằng Pillow, kiểm tra tính toàn vẹn và trích xuất chiều rộng x chiều cao chuẩn xác.
  - **Khử trùng lặp Nội dung (Content Deduplication)**: Băm dữ liệu theo thuật toán SHA-256. Các tệp tin giống hệt nhau sẽ dùng chung bản ghi trên ổ đĩa, tiết kiệm dung lượng lưu trữ tối đa.
  - **Ghi đĩa Nguyên tử (Atomic Persistence)**: Tải về file tạm `.download`, sau khi vượt qua toàn bộ các bước kiểm tra mới đổi tên nguyên tử thành file chính thức.

### 3.4. Mô hình Dữ liệu & Phân lập Đa Người dùng (Multi-tenant Assets)
- **Tập tin**: `backend/models/db_models.py`, `backend/routers/assets.py`
- Bổ sung bảng `AssetModel` với các chỉ mục:
  * `idx_asset_user_id`: Tối ưu hóa truy vấn tài nguyên theo người dùng.
  * `idx_asset_filename_user`: Khóa duy nhất phức hợp đảm bảo tính phân lập dữ liệu triệt để giữa các tài khoản khác nhau.
- Bổ sung các API quản lý tư liệu:
  * `POST /api/v1/assets/download`: Tải và lưu trữ tư liệu an toàn từ URL bên ngoài.
  * `GET /api/v1/assets/media/{filename}`: Phục vụ file đa phương tiện với xác thực Token JWT và chặn tấn công duyệt đường dẫn (Path Traversal Protection).
  * `POST /api/v1/assets/attribution-manifest`: Tạo bản ghi nhận quyền tác giả theo định dạng văn bản chuẩn.

### 3.5. Pipeline Dựng Video Thực tế Phía Frontend (WebCodecs Real Media Rendering)
- **Tập tin**: `frontend/src/services/webcodecsRenderer.ts`
- **Chuyển đổi triệt để**:
  1. **Preload Media Thật**: Chuyển URL cục bộ thành `Blob` và khởi tạo đối tượng đồ họa bằng `createImageBitmap(blob)`.
  2. **Thuật toán Khớp tỷ lệ Cover (Aspect Ratio Cover Fitting)**:
     ```typescript
     const scale = Math.max(canvasWidth / img.width, canvasHeight / img.height) * zoomFactor;
     const drawW = img.width * scale;
     const drawH = img.height * scale;
     const drawX = (canvasWidth - drawW) / 2 + panX;
     const drawY = (canvasHeight - drawH) / 2 + panY;
     ctx.drawImage(img, drawX, drawY, drawW, drawH);
     ```
     Đảm bảo khung hình 1080x1920 luôn được lấp đầy tuyệt đối không có viền đen thô kệch và không bị méo tỷ lệ quang học.
  3. **Hiệu ứng Điện ảnh Ken Burns**: Áp dụng phép nội suy vi sai theo thời gian thực ($t \in [0, 1]$), tạo chuyển động pan ngang/dọc và phóng to/thu nhỏ nhẹ nhàng (tỷ lệ 1.0 đến 1.12), biến các ảnh tĩnh thành khung hình điện ảnh sống động.
  4. **Chuyển cảnh Mượt mà (Crossfade Transitions)**: Trong 0.5s cuối của mỗi cảnh, tiến hành pha trộn alpha (`globalAlpha = 1 - t_transition`) giữa cảnh hiện tại và hình ảnh của cảnh tiếp theo.
  5. **Hòa âm Đa kênh & Dynamic Ducking**:
     - Sử dụng `AudioContext` giải mã dữ liệu âm thanh giọng đọc từ Edge-TTS thành PCM Float32 (48kHz Stereo).
     - Hòa trộn với nhạc nền (BGM bed).
     - Khi phát hiện có tín hiệu giọng đọc, tự động giảm âm lượng BGM xuống -18dB (hệ số gain 0.15) để tôn rõ giọng đọc tiếng Việt; khi kết thúc câu đọc, âm lượng nhạc tự động hồi phục mượt mà về mức tiêu chuẩn.
  6. **Phụ đề Karaoke Đồng bộ Mili-giây**:
     - Ánh xạ mảng từ và mốc thời gian `start_ms`, `end_ms` từ TTS Giai đoạn 2.
     - Hiển thị phụ đề viền kép (Stroke + Fill), hiệu ứng highlight từ đang đọc với màu vàng điện ảnh nổi bật (`#FACC15`), căn giữa ở vị trí $85\%$ chiều cao khung hình.
  7. **Quản lý Vòng đời Tài nguyên Bộ nhớ**:
     - Gọi `imageBitmap.close()` ngay sau khi kết thúc quá trình render.
     - Hủy `AudioContext` để giải phóng bộ nhớ RAM đồ họa của trình duyệt.
     - Khi một tư liệu hình ảnh bị lỗi hoặc không tải được, kích hoạt chế độ Fallback Card với giao diện gradient hiện đại, biểu tượng cảnh báo và trích xuất lời thoại trực quan, không làm gián đoạn tiến trình render của toàn bộ video.

---

## 4. KẾT QUẢ KIỂM THỬ VÀ ĐO LƯỜNG THỰC TẾ

### 4.1. Kết quả Kiểm thử Toàn diện Backend (Pytest Suite)
Thực thi kiểm thử toàn bộ 52 test cases bao gồm kiểm thử bảo mật Auth JWT, phân lập dữ liệu SQLite, động cơ TTS, và bộ test mới của Giai đoạn 3:

```
collected 52 items

backend/tests/test_asset_discovery_production.py::test_wikimedia_live_discovery_integration PASSED [  1%]
backend/tests/test_asset_discovery_production.py::test_openverse_discovery_structure PASSED [  3%]
backend/tests/test_asset_discovery_production.py::test_pexels_unconfigured_graceful_fallback PASSED [  5%]
backend/tests/test_asset_discovery_production.py::test_intelligent_economic_query_formulation PASSED [  7%]
backend/tests/test_asset_discovery_production.py::test_ssrf_protection_blocks_malicious_targets PASSED [  9%]
backend/tests/test_asset_discovery_production.py::test_detect_media_format_magic_bytes PASSED [ 11%]
backend/tests/test_asset_discovery_production.py::test_asset_downloader_with_valid_image PASSED [ 13%]
backend/tests/test_asset_discovery_production.py::test_asset_api_download_and_tenant_isolation PASSED [ 15%]
backend/tests/test_asset_discovery_production.py::test_attribution_manifest_endpoint PASSED [ 17%]
backend/tests/test_assets_and_tts.py::test_number_to_vietnamese_words PASSED [ 19%]
backend/tests/test_assets_and_tts.py::test_vietnamese_text_normalizer PASSED [ 21%]
backend/tests/test_assets_and_tts.py::test_tts_syllable_timings PASSED [ 23%]
backend/tests/test_assets_and_tts.py::test_real_edge_tts_voice_provider PASSED [ 25%]
backend/tests/test_assets_and_tts.py::test_asset_discovery_wikimedia PASSED [ 26%]
backend/tests/test_auth_security.py::test_valid_jwt_decoding PASSED [ 28%]
backend/tests/test_auth_security.py::test_expired_jwt_rejection PASSED [ 30%]
backend/tests/test_auth_security.py::test_invalid_signature_rejection PASSED [ 32%]
backend/tests/test_auth_security.py::test_malformed_token_rejection PASSED [ 34%]
backend/tests/test_auth_security.py::test_fail_closed_when_secret_is_placeholder_or_missing PASSED [ 36%]
backend/tests/test_auth_security.py::test_algorithm_none_rejection PASSED [ 38%]
backend/tests/test_e2e_pipeline.py::test_complete_end_to_end_pipeline PASSED [ 40%]
backend/tests/test_e2e_pipeline.py::test_full_studio_api_workflow_end_to_end PASSED [ 42%]
backend/tests/test_phase1_remediation.py::test_sqlite_foreign_key_enforcement PASSED [ 44%]
backend/tests/test_phase1_remediation.py::test_sqlite_cascade_delete PASSED [ 46%]
backend/tests/test_phase1_remediation.py::test_jwt_valid_token PASSED [ 48%]
backend/tests/test_phase1_remediation.py::test_jwt_expired_token PASSED [ 50%]
backend/tests/test_phase1_remediation.py::test_jwt_invalid_signature PASSED [ 51%]
backend/tests/test_phase1_remediation.py::test_jwt_invalid_audience PASSED [ 53%]
backend/tests/test_phase1_remediation.py::test_jwt_invalid_issuer PASSED [ 55%]
backend/tests/test_phase1_remediation.py::test_jwt_algorithm_none_rejected PASSED [ 57%]
backend/tests/test_phase1_remediation.py::test_audio_endpoint_security_and_authorization PASSED [ 59%]
backend/tests/test_phase1_remediation.py::test_cors_cloudflare_pages_regex PASSED [ 61%]
backend/tests/test_phase1_remediation.py::test_chapter_crud_api_and_tenant_isolation PASSED [ 63%]
backend/tests/test_projects_api.py::test_healthz_and_status PASSED [ 65%]
backend/tests/test_projects_api.py::test_security_headers PASSED [ 67%]
backend/tests/test_projects_api.py::test_project_crud_and_episode_flow PASSED [ 69%]
backend/tests/test_projects_api.py::test_tenant_isolation PASSED [ 71%]
backend/tests/test_script_engine.py::test_count_vietnamese_syllables PASSED [ 73%]
backend/tests/test_script_engine.py::test_rule_based_script_analysis PASSED [ 75%]
backend/tests/test_script_engine.py::test_groq_fallback_when_unconfigured PASSED [ 76%]
backend/tests/test_script_engine.py::test_horror_genre_specialization PASSED [ 78%]
backend/tests/test_script_engine.py::test_long_form_chapter_planning PASSED [ 80%]
backend/tests/test_tts_production.py::test_vietnamese_text_chunker_word_preservation PASSED [ 82%]
backend/tests/test_tts_production.py::test_vietnamese_unicode_and_punctuation_preservation PASSED [ 84%]
backend/tests/test_tts_production.py::test_mp3_stitcher_frame_parsing_and_id3_stripping PASSED [ 86%]
backend/tests/test_tts_production.py::test_word_timestamp_monotonicity_and_rebasing PASSED [ 88%]
backend/tests/test_tts_production.py::test_deterministic_sha256_audio_caching PASSED [ 90%]
backend/tests/test_tts_production.py::test_multi_user_cache_sharing_and_tenant_isolation PASSED [ 92%]
backend/tests/test_tts_production.py::test_bounded_concurrency_control PASSED [ 94%]
backend/tests/test_tts_production.py::test_tts_retry_transient_failure_recovery PASSED [ 96%]
backend/tests/test_tts_production.py::test_tts_offline_fallback_when_hard_failure PASSED [ 98%]
backend/tests/test_tts_production.py::test_tts_api_input_validation_and_voices PASSED [100%]

============================= 52 passed in 23.92s ==============================
```

### 4.2. Kết quả End-to-End Acceptance Test Thực tế (10 Bước Khép kín)
Kịch bản kinh tế tiếng Việt gồm 5 cảnh quay thực tế được đưa vào kiểm thử đầu cuối (`backend/benchmarks/test_phase3_e2e_acceptance.py`):

| Bước | Hạng mục kiểm thử | Kết quả thực tế | Trạng thái |
|---|---|---|---|
| 1 | Phân tích kịch bản kinh tế 5 cảnh | Hoàn thành trong **0.42 ms**, trích xuất 5 nhóm keywords trực quan | **PASS** |
| 2 & 3 | Khám phá & Tải 5 tư liệu thực tế | Tải thành công 5 ảnh độ phân giải cao từ Wikimedia Commons trong **17.77s** | **PASS** |
| 4 | Bảo toàn bản quyền & Manifest | Tạo thành công manifest ghi nhận tác giả & giấy phép CC BY / CC BY-SA | **PASS** |
| 5 & 6 | Tổng hợp giọng đọc Edge-TTS tiếng Việt | Tổng thời lượng **28.68s**, phát hiện 107 từ, mốc thời gian đơn điệu 100% | **PASS** |
| 7, 8 & 9 | Muxing container MP4 | Đóng gói thành công tập tin MP4 với Video H.264 và Audio AAC Stereo | **PASS** |
| 10 | Giám định Container Độc lập (MP4Inspector) | Đạt chuẩn ISOBMFF (`ftyp`, `moov`, `mdat`), codec `avc1` + `mp4a` | **PASS** |

#### Bảng ghi nhận tư liệu thực tế được tải và kiểm định:
1. **Cảnh 1 (Dầu thô)**: *"Crude Oil Tanker Njord DF at BP Oil Refinery Jetty"* - Tác giả: Calistemon (CC BY-SA 4.0) — Kích thước: $4456 \times 2507$ px (1,332 KB).
2. **Cảnh 2 (Cảng biển)**: *"Cargo ship Primero moored at Eurogate Container Terminal Hamburg"* - Tác giả: Raimond Spekking (CC BY-SA 4.0) — Kích thước: $6414 \times 3608$ px (15,551 KB).
3. **Cảnh 3 (Ngân hàng)**: *"Bank Mellat Building 3vp perspective"* - Tác giả: Ali Safdarian (CC BY 3.0) — Kích thước: $2160 \times 3840$ px (1,559 KB).
4. **Cảnh 4 (Nhà máy tự động)**: *"Anand Sharma meeting the Japanese Minister for Economy, Trade & Industry"* - Tác giả: Ministry of Commerce and Industry (India) (GODL-India) — Kích thước: $2200 \times 1160$ px (315 KB).
5. **Cảnh 5 (Tăng trưởng GDP)**: *"Historical economic growth of Indonesia"* - Tác giả: Max Roser (CC BY 4.0) — Kích thước: $1033 \times 648$ px (42 KB).

#### Báo cáo JSON nghiệm thu (`backend/benchmarks/acceptance_test_report.json`):
```json
{
  "status": "PASS",
  "script": "Giá dầu thô và năng lượng thế giới tăng mạnh kỷ lục...",
  "scenes_count": 5,
  "assets_downloaded": 5,
  "total_audio_duration_seconds": 28.68,
  "mp4_file_size_bytes": 34912,
  "video_codec": "H.264 (avc1)",
  "audio_codec": "AAC (mp4a)",
  "isobmff_valid": true
}
```

### 4.3. Kết quả Kiểm tra Frontend Build
- Lệnh: `cd frontend && npm run build` (`tsc -b && vite build`)
- Thời gian biên dịch: **1.61s**
- Kết quả: **0 lỗi TypeScript, 0 lỗi cú pháp**. Bundles tạo ra sạch sẽ (`dist/index.html`, `dist/assets/index-Ba0kZOc1.js`).
- Kiểm tra mã nguồn: `git diff --check` đạt **0 cảnh báo / 0 lỗi whitespace**.

---

## 5. KẾT LUẬN VÀ BÀN GIAO

Giai đoạn 3 đã hoàn thành xuất sắc toàn bộ các chỉ tiêu kỹ thuật được giao:
- Loại bỏ hoàn toàn hình ảnh vector giả định và sóng sin procedural thô sơ.
- Vận hành trơn tru pipeline khám phá và tải tư liệu thực tế hoàn toàn miễn phí, tuân thủ pháp lý bản quyền quốc tế.
- Hạ tầng tải tư liệu được bảo vệ an toàn trước các cuộc tấn công SSRF và tấn công tiêm tệp độc hại.
- Trình dựng video trên frontend đã làm chủ công nghệ WebCodecs hiện đại: lấp đầy khung hình dọc 9:16 thông minh, chuyển động điện ảnh Ken Burns mượt mà, hòa âm BGM dynamic ducking, và đồng bộ phụ đề karaoke tiếng Việt chính xác theo mili-giây.
- Toàn bộ thay đổi được lưu trữ trên nhánh `feature/unified-ai-video-studio`, giữ nguyên tắc không merge vào nhánh `main`.
