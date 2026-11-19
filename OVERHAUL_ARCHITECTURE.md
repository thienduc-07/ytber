# KIẾN TRÚC TOÀN DIỆN VÀ LỘ TRÌNH TRIỂN KHAI: AI ANIMATION & VIDEO STUDIO
**Global Product Overhaul — Automated AI Animation & Sound Production Platform**

- **Dự án**: YTBER — Unified AI Video Studio
- **Branch**: `feature/unified-ai-video-studio`
- **Mục tiêu**: Nâng cấp toàn diện sản phẩm từ dựng video cắt ghép sang **Studio Hoạt hình & Sản xuất Video AI Tự động hóa Hoàn toàn (100% Animated Visuals, 3-Layer Sound Design, Temporal Animation, Content-Independent Intelligence)**.
- **Nguyên tắc cốt lõi**:
  1. **Chính sách Hình ảnh 100% Hoạt hình (Strict Animated Visual Policy)**: Tuyệt đối không sử dụng hình ảnh thực tế, ảnh chụp stock, video tài liệu live-action.
  2. **Hoạt họa Thực tế (Actual Temporal Animation)**: Cấm video dạng slideshow tĩnh gắn hiệu ứng zoom đơn thuần. Mọi cảnh quay đều phải có chuyển động vật thể, nhân vật, môi trường hoặc motion graphics theo thời gian.
  3. **Thiết kế Âm thanh 3 Lớp (Complete 3-Layer Sound Design)**: Voiceover AI tiếng Việt + Nhạc nền (BGM) theo chủ đề + Hiệu ứng âm thanh ngữ cảnh (SFX) với dynamic ducking.
  4. **AI Director & Character Consistency**: Đạo diễn AI sinh kịch bản sản xuất 17 trường thuộc tính; duy trì nhận diện ngoại hình nhân vật nhất quán xuyên suốt các cảnh.
  5. **Độc lập Chủ đề (Content-Independent Intelligence)**: Xử lý mượt mà mọi kịch bản (Lịch sử, Kinh tế, Công nghệ, Khoa học, Xã hội).

---

## 1. KẾT QUẢ AUDIT HỆ THỐNG HIỆN TẠI

### 1.1. Thành phần Đang hoạt động & Có thể Tái sử dụng
- **Vietnamese Neural Voiceover Engine (Phase 2)**:
  - Tích hợp `Edge-TTS` với các giọng đọc tiếng Việt chuẩn (`vi-VN-NamMinhNeural`, `vi-VN-HoaiMyNeural`).
  - Bộ băm nhỏ văn bản thông minh (`tts_chunker.py`) bảo toàn dấu câu và ngữ nghĩa.
  - Ghép nối audio MP3 (`mp3_stitcher.py`) chuẩn frame MPEG, rebase mốc thời gian mili-giây đơn điệu.
  - Cache âm thanh SHA-256 an toàn và kiểm soát đồng thời (bounded concurrency).
  - Tái sử dụng 100% làm **Layer 1: Voiceover**.
- **Hạ tầng Cơ sở Dữ liệu & Bảo mật (Phase 1)**:
  - SQLite SQLAlchemy models (`ProjectModel`, `EpisodeModel`, `ChapterModel`, `JobModel`, `AssetModel`).
  - Khóa ngoại và cascade delete thực thi chặt chẽ.
  - JWT xác thực fail-closed, phân lập dữ liệu đa người dùng (multi-tenant isolation).
  - Rate limiting middleware bảo vệ hệ thống.
- **Đóng gói Video Phần cứng (Hardware WebCodecs + MP4 Muxer)**:
  - `webcodecsRenderer.ts` đã làm chủ luồng mã hóa video phần cứng `VideoEncoder` (H.264) và `AudioEncoder` (AAC 48kHz Stereo).
  - Đóng gói container chuẩn ISOBMFF (`ftyp`, `moov`, `mdat`) bằng `mp4-muxer`, xuất video hợp lệ xem được trên mọi nền tảng di động và web.

### 1.2. Hạn chế, Thiếu sót & Thành phần Giả định (Mocked/Incomplete)
1. **Vi phạm Chính sách Hình ảnh Hoạt hình (Phase 3 Asset Discovery)**:
   - Module `asset_discovery.py` hiện đang tìm kiếm và tải ảnh chụp thực tế (photographs) từ Wikimedia Commons (ảnh chụp nhà máy dầu, tàu chở hàng, tòa nhà ngân hàng, chân dung người thật).
   - Điều này xung đột với yêu cầu sản phẩm: **100% Animated Visuals — 0% Real-life Visuals**.
2. **Thiếu Hoạt họa Thực tế (Temporal Animation Deficit)**:
   - `webcodecsRenderer.ts` hiện tại chỉ vẽ ảnh tĩnh và scale nhẹ (Ken Burns effect). Đây thực chất là một slideshow ảnh tĩnh, không có chuyển động nhân vật, không có chuyển động vật thể, không có hạt môi trường.
3. **Thiếu Hệ thống Thiết kế Âm thanh 3 Lớp (Sound Design Gap)**:
   - Hiện tại chỉ có giọng đọc TTS và một sóng sin đơn giản mô phỏng BGM bed. Chưa có hệ thống phát sinh hiệu ứng âm thanh ngữ cảnh (SFX: whoosh, impact, footsteps, ambient drone, mechanical clicks) và chưa có bộ phối khí BGM chuẩn theo thể loại.
4. **Thiếu AI Director & Character Consistency**:
   - `ai_rule_based.py` chỉ phân đoạn câu văn đơn giản và sinh từ khóa ảnh chụp. Chưa có đạo diễn AI thiết lập môi trường, cử chỉ nhân vật, góc máy, hướng dẫn diễn hoạt và bảng màu đồng bộ. Nhân vật chưa có hồ sơ tạo hình nhất quán.
5. **Chưa có Automated Quality Control (AQC)**:
   - Chưa có bộ kiểm định tự động đo lường độ biến thiên khung hình (motion delta), kiểm định tuân thủ phong cách hoạt hình (style compliance) và phát hiện ảnh chụp bị lọt vào video.

---

## 2. KIẾN TRÚC MỤC TIÊU (TARGET ARCHITECTURE)

```
+----------------------------------------------------------------------------------------------------+
|                                    BACKEND CORE (FASTAPI / PYTHON 3.9)                             |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [Global Script Intelligence Engine]                                                               |
|        │ Nhận diện: Subject, Topic, Historical/Modern Context, Narrative Arc, Emotion, Entities   |
|        ▼                                                                                           |
|  [AI Director & Character Consistency Engine]                                                      |
|        ├── Character Registry: Tạo hình nhân vật nhất quán (Tên, Trang phục, Dáng người, Bảng màu)  |
|        └── 17-Attribute Scene Specification:                                                       |
|              (Narrative Purpose, Environment, Character Actions, Props, Camera Angle/Motion,      |
|               Animation Directives, Lighting, Color Palette, Transitions, Music, SFX cues)         |
|        │                                                                                           |
|        ▼                                                                                           |
|  [Animated Style Compliance & Asset Classifier]                                                    |
|        ├── Strict Filter: Chỉ cho phép SVG, Vector Illustration, Cartoon Clipart, Procedural Assets|
|        └── Anti-Photographic Gatekeeper: Chặn 100% ảnh chụp người, sự kiện, stock photo           |
|        │                                                                                           |
|        ▼                                                                                           |
|  [Automated Quality Control (AQC) Engine]                                                          |
|        ├── Semantic Relevance Verifier                                                             |
|        ├── Style Compliance Verifier (100% Animated)                                               |
|        └── Motion Delta & Timeline Verifier                                                        |
+----------------------------------------------------------------------------------------------------+
                                                 ▲
                                                 │ Unified Production Manifest JSON
                                                 ▼
+----------------------------------------------------------------------------------------------------+
|                              FRONTEND PRODUCTION PIPELINE (WEBCODECS / CANVAS)                     |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [Unified Timeline Engine]                                                                         |
|        │ Đồng bộ khung hình (VideoFrames), Âm thanh (AudioFrames), Phụ đề, SFX, BGM Ducking        |
|        │                                                                                           |
|        ├──> [Temporal Animation Engine (Canvas 2D / Vector Rigs)]                                  |
|        │      ├── Stylized Character Rig: Đi bộ/hành quân, chỉ tay, kéo vật nặng, reo hò, nháy mắt |
|        │      ├── Dynamic Object Animation: Đại bác giật nổ, cờ bay, xe chạy, tiền rơi, biểu đồ vẽ |
|        │      ├── Multi-Plane Parallax: Nền trời (0.2x), Dãy núi (0.5x), Nhân vật (1.0x), Cận cảnh |
|        │      ├── Environmental Particle System: Khói lửa, bụi bay, tia lửa, mây trôi, ánh sao    |
|        │      ├── Animated Motion Graphics: Cột tăng trưởng vươn cao, biểu đồ sóng, radar quét     |
|        │      └── Animated Vector Maps: Zoom bản đồ địa hình, đường hành quân vẽ động, pin định vị |
|        │                                                                                           |
|        └──> [Complete 3-Layer Sound Design Engine]                                                 |
|               ├── Layer 1: Voiceover (Edge-TTS AudioBuffer giải mã PCM 48kHz)                      |
|               ├── Layer 2: Synthesized BGM Engine (Phối khí nhạc nền điện ảnh theo thể loại/cảm xúc)|
|               ├── Layer 3: Contextual SFX Synthesizer (Whoosh, Impact, Ambience, Footsteps, Beeps) |
|               └── Dynamic Ducking: BGM & SFX tự động giảm -18dB khi giọng đọc cất lên              |
|        │                                                                                           |
|        ▼                                                                                           |
|  [Hardware WebCodecs Video & Audio Encoders] ──> [MP4 Muxer (ISOBMFF)] ──> Final Animated MP4 Video |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. THIẾT KẾ CHI TIẾT CÁC PHÂN HỆ

### 3.1. Phân hệ 1: Global Script Intelligence & AI Director
- **Tập tin**: `backend/providers/director_engine.py` (Mới), mở rộng `backend/providers/ai_base.py`.
- **Nhiệm vụ**:
  - Không hardcode chủ đề. Phân tích ngữ nghĩa độc lập nội dung:
    * Chủ thể chính (`main_subject`), thể loại (`topic_category`), bối cảnh lịch sử/đương đại (`context_era`), nhịp độ kể chuyện (`pacing_tempo`).
    * Trích xuất các thực thể nhân vật (`CharacterProfile`): xác định tên, trang phục văn hóa/lịch sử/nghề nghiệp, màu sắc chủ đạo, tỷ lệ đầu/thân phong cách hoạt hình (chibi 1:2.5 hoặc hoạt họa kinh điển 1:4).
  - Sinh đặc tả sản xuất 17 trường cho từng cảnh quay (`SceneProductionPlan`):
    1. `scene_id`: Mã cảnh duy nhất.
    2. `narrative_purpose`: Mục đích tự sự (thiết lập bối cảnh, leo thang căng thẳng, đột phá công nghệ, cao trào chiến thắng, bài học đúc kết).
    3. `narration_text`: Lời đọc tiếng Việt.
    4. `visual_description`: Mô tả hình ảnh hoạt họa chi tiết.
    5. `environment`: Bối cảnh (rừng núi sương mù, thung lũng chiến trường, sàn giao dịch công nghệ, phòng thí nghiệm, vũ trụ không gian).
    6. `character_descriptions`: Danh sách nhân vật xuất hiện và nhận diện thị giác.
    7. `character_poses_actions`: Hành động cụ thể của từng nhân vật (`march`, `pull_heavy_load`, `present_data`, `celebrate`, `stand_vigilant`).
    8. `props`: Đạo cụ hoạt họa xuất hiện (pháo kéo, cờ lệnh, ống nhòm, máy tính, bảng biểu đồ, phi thuyền).
    9. `camera_angle`: Góc quay (`wide_establishing`, `medium_character`, `low_angle_heroic`, `top_down_map`).
    10. `camera_movement`: Chuyển động máy quay (`pan_right`, `smootherstep_push_in`, `tilt_up`, `whip_pan`, `track_character`).
    11. `animation_instructions`: Chỉ dẫn diễn hoạt chi tiết cho engine đồ họa.
    12. `lighting`: Ánh sáng (`golden_hour_rim`, `dramatic_chiaroscuro`, `clean_high_key`, `eerie_moonlight`).
    13. `color_palette`: Bảng màu đồ họa gồm 5 mã hex đồng bộ.
    14. `transition`: Kiểu chuyển cảnh (`crossfade`, `whip_pan`, `zoom_punch`, `iris_wipe`, `cut`).
    15. `scene_duration`: Thời lượng cảnh (tính chuẩn xác theo số âm tiết tiếng Việt và nhịp độ).
    16. `music_direction`: Chỉ dẫn âm nhạc (tempo, mood, chord progression, orchestration style).
    17. `sound_effects`: Danh sách các điểm rơi âm thanh SFX (`SoundEffectCue`).

### 3.2. Phân hệ 2: Strict Animated Visual Policy & Asset Classifier
- **Tập tin**: `backend/providers/visual_classifier.py` (Mới), nâng cấp `backend/providers/asset_discovery.py`.
- **Quy tắc Kiểm duyệt 2 Lớp (Dual-Layer Validation)**:
  - **Lớp 1: Semantic Relevance**: Đối chiếu từ khóa đồ họa với ngữ cảnh cảnh quay.
  - **Lớp 2: Animated Style Compliance (Gatekeeper)**:
    * Kiểm tra định dạng: Chỉ chấp nhận vector SVG, bản vẽ minh họa hoạt họa 2D, tranh vẽ minh họa lịch sử cách điệu.
    * Thuật toán phát hiện ảnh thực tế: Phân tích tần số màu và phân bố cạnh (edge distribution). Nếu phát hiện ảnh chụp người thật, ảnh tin tức hoặc video live-action $\rightarrow$ **LẬP TỨC TỪ CHỐI VÀ CHUYỂN HƯỚNG SANG PROCEDURAL ANIMATION ENGINE**.
    * Từ chối tuyệt đối việc để màn hình trống hoặc hộp chữ nhật đen.

### 3.3. Phân hệ 3: Temporal Animation Engine (Frontend Canvas 2D)
- **Tập tin**: `frontend/src/services/animationEngine.ts` (Mới), tích hợp sâu vào `frontend/src/services/webcodecsRenderer.ts`.
- **Cấu trúc Diễn hoạt Thực tế**:
  1. **Stylized Character Rigging**:
     - Vẽ nhân vật hoạt họa hoàn chỉnh bằng mã lệnh Canvas vector:
       * Khuôn mặt: Mắt biểu cảm (chớp mắt, nhíu mày), miệng chuyển động đóng mở theo âm thanh đọc (`mouth flap` khớp với word timestamps).
       * Cơ thể: Trang phục chi tiết (bộ quân phục bộ đội mũ nan, áo sơ mi nhà kinh tế, áo blouse nhà khoa học, trang phục thám hiểm).
       * Chân tay: Chuyển động bước chân (walking cycle), tay vung nhịp nhàng, kéo dây thừng dốc núi, giơ cờ lệnh.
  2. **Multi-Plane Parallax Depth System**:
     - Chia khung hình thành 3–4 lớp không gian di chuyển với vận tốc khác nhau ($v_{bg} < v_{mid} < v_{char} < v_{fg}$), tạo chiều sâu không gian quang học 3 chiều ấn tượng mà không cần GPU 3D nặng nề.
  3. **Environmental Particle Systems**:
     - Lớp hiệu ứng hạt môi trường chuyển động liên tục:
       * Khói sương mù bay lững lờ trên dãy núi thung lũng.
       * Hạt lửa tàn tro và bụi đất chiến trường.
       * Tia sáng mặt trời xuyên kẽ lá (god rays).
       * Lưới tọa độ số học và các khối dữ liệu bay lơ lửng cho chủ đề công nghệ/kinh tế.
  4. **Animated Motion Graphics & Vector Maps**:
     - Cột tăng trưởng GDP / lạm phát mọc lên từ đáy màn hình với số liệu đếm nhảy động (`animated counter`).
     - Bản đồ địa hình với đường nét đứt biểu diễn lộ trình hành quân/vận tải uốn lượn theo thời gian thực và biểu tượng định vị nhấp nháy phát sóng xung kích.

### 3.4. Phân hệ 4: Complete 3-Layer Sound Design Engine
- **Tập tin**: `frontend/src/services/soundDesignEngine.ts` (Mới), kết hợp `backend/providers/tts_engine.py`.
- **Thiết kế 3 Lớp Âm thanh**:
  - **Layer 1: Voiceover (Giọng đọc)**:
    * Giữ nguyên và khai thác tối đa engine Edge-TTS từ Phase 2.
    * Giải mã PCM 48kHz Stereo thông qua Web Audio API `AudioContext.decodeAudioData`.
  - **Layer 2: Background Music (Nhạc nền)**:
    * Hệ thống bộ tổng hợp hợp âm đa âm sắc (synthesized chord progression engine):
      - Lịch sử / Hùng tráng: Hợp âm rền vang, nhịp trống dồn dập (martial march cadence), âm hưởng kèn đồng hùng vĩ.
      - Kinh tế / Công nghệ: Nhịp pulse điện tử hiện đại, pad ấm áp, arpeggio dồn dập kích thích tư duy.
      - Kinh dị / Bí ẩn: Dải âm trầm drone tần số thấp (low drone), tiếng piano lẻ loi vang vọng, chuỗi âm bất hòa.
  - **Layer 3: Contextual Sound Effects (Hiệu ứng Âm thanh SFX)**:
    * Máy phát âm thanh ngữ cảnh tổng hợp:
      - `whoosh`: Âm thanh gió quét khi chuyển cảnh nhanh hoặc lia máy.
      - `impact`: Âm trầm va đập khi dữ liệu, nhân vật hoặc biến cố xuất hiện.
      - `ambient`: Tiếng gió đêm, tiếng côn trùng rừng sâu, tiếng máy móc nhà xưởng rì rầm.
      - `mechanical`: Tiếng click bánh răng, tiếng gõ phím số liệu, tiếng chuông giao dịch.
      - `footsteps`: Tiếng bước chân hành quân nhịp nhàng trên nền đất sỏi.
  - **Dynamic Audio Ducking & Mastering**:
    * Tính toán đường bao âm lượng (gain envelope). Tự động hạ âm lượng BGM xuống $-18\text{ dB}$ (hệ số 0.12–0.15) ngay khi giọng đọc phát ra, và nâng âm lượng mượt mà (fade in 300ms) khi giọng đọc tạm nghỉ.

### 3.5. Phân hệ 5: Automated Quality Control (AQC) Engine
- **Tập tin**: `backend/services/quality_control.py` (Mới).
- **Bộ Tiêu chuẩn Nghiệm thu Tự động (AQC Invariants)**:
  1. `assert_100_percent_animated`: Quét mẫu ngẫu nhiên các khung hình đã kết xuất, kiểm tra xem có tệp ảnh chụp hoặc khung hình live-action bị tiêm vào không.
  2. `assert_temporal_motion`: Tính toán độ biến thiên sai phân giữa các khung hình liên tiếp ($\Delta_{\text{frames}} > \epsilon$). Nếu toàn bộ cảnh có pixel tĩnh giống nhau (slideshow) $\rightarrow$ **ĐÁNH RỚT KIỂM ĐỊNH**.
  3. `assert_three_layer_audio`: Kiểm tra phổ tần số âm thanh, bắt buộc phải có đầy đủ track giọng đọc, nền nhạc BGM và hiệu ứng âm thanh SFX.
  4. `assert_character_consistency`: Kiểm tra sự xuất hiện nhất quán của các nhân vật chủ chốt trong các cảnh quay được chỉ định.
  5. `assert_isobmff_mp4`: Kiểm tra cấu trúc container MP4 với đầy đủ track H.264 video và AAC stereo audio.

---

## 4. LỘ TRÌNH THỰC HIỆN TỪNG MILESTONE (ROADMAP)

| Milestone | Tên Phân hệ | Nhiệm vụ Cốt lõi | Tiêu chí Hoàn thành & Nghiệm thu |
|---|---|---|---|
| **M1** | **Audit & Target Architecture** | Lập tài liệu kiểm toán, phân tích lỗi phiên bản cũ, thiết kế kiến trúc toàn diện 100% hoạt hình. | Tài liệu `OVERHAUL_ARCHITECTURE.md` hoàn chỉnh, cam kết giữ nguyên branch. |
| **M2** | **AI Director & Script Intelligence** | Nâng cấp `director_engine.py` sinh kịch bản sản xuất 17 thuộc tính, quản lý nhân vật nhất quán (`CharacterRegistry`). | Kịch bản bất kỳ được phân tích thành các cảnh có môi trường, hành động, góc máy và bảng màu cụ thể. Test cases pass. |
| **M3** | **Strict Animated Asset System** | Chuyển đổi `asset_discovery.py`, bổ sung `visual_classifier.py` chặn 100% ảnh chụp thực tế, chỉ chấp nhận vector/hoạt hình. | Kiểm thử với ảnh chụp bị từ chối; chỉ duyệt asset hoạt họa hợp lệ. |
| **M4** | **Temporal Animation Engine** | Triển khai `animationEngine.ts`: rig nhân vật hoạt họa chuyển động, đa mặt phẳng parallax, hiệu ứng hạt khói bụi, bản đồ động, đồ thị chuyển động. | Video render có chuyển động cơ thể, môi trường di chuyển theo thời gian thực, không còn là slideshow tĩnh. |
| **M5** | **Complete Sound Design Engine** | Triển khai `soundDesignEngine.ts`: tổng hợp nhạc nền BGM theo thể loại + bộ phát SFX (whoosh, impact, ambience, steps) + dynamic ducking. | Kết xuất âm thanh 3 lớp rõ nét, tiếng nhạc tự động lùi xuống khi có giọng đọc, âm thanh SFX xuất hiện đúng cảnh. |
| **M6** | **Unified Production Integration & UX** | Tích hợp toàn diện vào `webcodecsRenderer.ts`, gỡ bỏ debug labels thừa, nâng cấp giao diện `ScriptStudioPage.tsx` và `RemotionPlayer.tsx`. | Giao diện cho phép chọn phong cách hoạt họa, tạo video trơn tru từ đầu đến cuối trên trình duyệt. |
| **M7** | **Automated Quality Control (AQC)** | Xây dựng `quality_control.py` kiểm định tự động: 100% animated, motion delta > 0, 3-layer audio, MP4 decoding. | Bộ test AQC tự động chạy và đánh giá video đạt chuẩn trước khi xuất xưởng. |
| **M8** | **Generalized Verification & Deliverables** | Thực thi kiểm thử nghiệm thu trên 5 chủ đề độc lập (Điện Biên Phủ, Lạm phát, Trí tuệ nhân tạo, Hệ Mặt Trời, Biến đổi khí hậu). Xuất video kiểm định thực tế. | Báo cáo `OVERHAUL_FINAL_REPORT.md`, tất cả 5 chủ đề đều render thành công video hoạt họa có âm thanh hoàn chỉnh. Commit & push sạch sẽ. |

---

## 5. CAM KẾT KỸ THUẬT VÀ PHẠM VI BẢO TOÀN

- **Bảo toàn Nhánh**: Duy trì tuyệt đối nhánh `feature/unified-ai-video-studio`. Tuyệt đối không checkout sang `main`, không merge vào `main`.
- **Bảo toàn Hạ tầng Đang hoạt động**: Không xóa bỏ các thành phần đã được kiểm thử kỹ càng từ Phase 1 và Phase 2 (JWT auth, SQLite models, Edge-TTS chunker/stitcher, WebCodecs MP4 Muxer).
- **Ràng buộc Zero-Budget**: Toàn bộ hệ thống chạy trên nền tảng miễn phí (Edge-TTS, HTML5 Canvas 2D Vector Rigs, WebCodecs, Web Audio API, Wikimedia SVG / Public Domain Cliparts), không phụ thuộc vào API trả phí đắt đỏ.
- **Tiêu chuẩn Hoạt hình Thực chất**: Loại bỏ vĩnh viễn hình ảnh chụp thực tế và slideshow giả hoạt hình; cung cấp video hoạt họa sống động, chuyên nghiệp cho người dùng cuối.
