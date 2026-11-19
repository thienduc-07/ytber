# BÁO CÁO KIỂM TOÁN VÀ ĐÁNH GIÁ ĐỘC LẬP: YTBER — UNIFIED AI VIDEO STUDIO
**PRODUCTION AUDIT REPORT**

* **Đơn vị kiểm toán:** Senior QA Engineer, Security Auditor & Video Infrastructure Specialist (Independent Technical Audit)
* **Repository:** `thienduc-07/ytber`
* **Branch kiểm toán:** `feature/unified-ai-video-studio`
* **Commit kiểm toán:** `76bc55b8b400c92488d767362c63b45393c79a41` (trên nền commit tính năng `6dc3dfb80c7d145ddaa505998d35922c07502006`)
* **Môi trường thử nghiệm:** macOS 26.0 Darwin (Apple M3, 8GB Unified Memory), Google Chrome 133+ (Headless & CDP), Python 3.9.6, Node.js 24.x.
* **Thời điểm kiểm toán:** 2026-11-19

---

## I. TỔNG QUAN KẾT QUẢ ĐÁNH GIÁ (EXECUTIVE SUMMARY)

Dự án **YTBER — Unified AI Video Studio** đã có những bước tiến đột phá về mặt kiến trúc so với phiên bản ban đầu:
1. **Pipeline xuất MP4 ở client:** Sử dụng `WebCodecs` kết hợp thư viện `mp4-muxer` đã giải quyết triệt để lỗi container MP4 và thiếu atom `moov`. Video kết xuất có cấu trúc ISOBMFF chuẩn, Fast Start (`moov` đứng trước `mdat`), 2 tracks (H.264/AVC1 + AAC/MP4A) và tương thích hoàn toàn với trình phát macOS / QuickTime / Trình duyệt.
2. **Hệ thống AI & Thể loại:** Bộ đăng ký 10 thể loại (`genre_intelligence.py`) và công cụ phân tích NLP tiếng Việt tất định hoạt động ổn định, trích xuất thực thể và phân cảnh chính xác.
3. **Bảo mật Fail-Closed:** Module `security.py` sử dụng `PyJWT` kiểm tra nghiêm ngặt, từ chối token khi secret rỗng/placeholder (`401`), từ chối token hết hạn (`exp`) và từ chối thuật toán `none`.
4. **Cơ sở dữ liệu bền vững:** Đã thay thế in-memory dictionary bằng SQLite (`./data/ytber.db`) qua SQLAlchemy Async.

**TUY NHIÊN**, quá trình kiểm toán kỹ thuật độc lập bằng thực nghiệm đã phát hiện **6 lỗi nghiêm trọng (P0) và 5 lỗi trung bình (P1)** đang ngăn cản hệ thống đạt trạng thái "Production-Ready":
* **[P0] Thiếu phụ thuộc cốt lõi trong `requirements.txt`:** `SQLAlchemy` và `greenlet` được import ở khắp backend nhưng **không có** trong `backend/requirements.txt`. Khi build Dockerfile hoặc cài đặt trong môi trường mới, server bị crash ngay lập tức (`ModuleNotFoundError: No module named 'sqlalchemy'`).
* **[P0] WebCodecs chưa nhúng lồng tiếng thật vào video MP4:** Bộ renderer client (`webcodecsRenderer.ts`) chỉ tổng hợp sóng âm dạng sin (procedural sine tone) vào track AAC. Hệ thống hoàn toàn chưa có mã nạp (loader) hay trộn (mixer) tệp MP3 lồng tiếng Edge-TTS vào video kết xuất.
* **[P0] Chưa tải và ghép hình ảnh tư liệu vào khung hình video:** Bộ renderer client không có lệnh `drawImage` hay đối tượng `Image()`. Các khung hình video hoàn toàn là các khối màu gradient, đường kẻ và văn bản vector vẽ bằng Canvas 2D. Tư liệu từ Wikimedia/Openverse chưa được tự động kéo về và nhúng vào video.
* **[P0] Edge-TTS sập khi gọi đồng thời hoặc kịch bản dài:** Khi gọi đồng thời 5 request đến Edge-TTS, 2 request bị lỗi `NoAudioReceived`. Gửi đoạn văn bản dài (>500 từ / >2000 ký tự) lập tức bị Microsoft từ chối stream âm thanh vì thiếu cơ chế cắt nhỏ (text chunking).
* **[P0] Chưa có cơ chế ghép nối phân đoạn Long-Form (Segment Assembly):** Chưa có mã nguồn thực hiện render từng chương rồi ghép (concatenate/merge) thành một video hoàn chỉnh dài 15–60 phút.
* **[P1] Thiếu xác thực cho endpoint phát âm thanh (`/api/v1/tts/audio/{filename}`):** Bất kỳ người dùng chưa đăng nhập nào cũng có thể tải và nghe tệp âm thanh nếu biết tên file.
* **[P1] SQLite chưa kích hoạt ràng buộc khóa ngoại (`PRAGMA foreign_keys = ON;`):** Cho phép chèn bản ghi con mồ côi (episode không có project hợp lệ).

### Bảng Tổng Hợp Verdicts Theo Từng Hạng Mục

| Phân hệ kiểm định | Đánh giá | Chi tiết độc lập đã xác minh |
| :--- | :---: | :--- |
| **Phase 1: Git & Change Audit** | **PARTIAL** | Git working tree sạch, đã push origin. Không lộ credentials. Tuy nhiên `backend/requirements.txt` thiếu `sqlalchemy` và `greenlet`. `@remotion` dư thừa trong `package.json`. |
| **Phase 2: MP4 Rendering Audit** | **PARTIAL** | WebCodecs mã hóa H.264 + AAC + `mp4-muxer` xuất sắc (1080x1920 & 1920x1080, tốc độ 55–165 FPS, `moov` trước `mdat`, `afinfo` đạt). Nhưng **chưa nhúng voiceover thật** vào audio track (chỉ có synth tone). |
| **Phase 3: Vietnamese TTS Audit** | **PARTIAL** | Nam Minh & Hoài My sinh MP3 chuẩn và word boundaries chính xác. Nhưng **không có cache bằng content hash**, **sập khi text dài >500 từ**, và **bị nghẽn socket khi có 5 request đồng thời**. |
| **Phase 4: Security Audit** | **PARTIAL** | Chặn đứng placeholder secret, cấm `alg: none`, kiểm tra token expired, phân quyền project/episode đạt. Tuy nhiên **chưa xác thực `iss`/`aud`**, và **endpoint audio stream không có auth**. |
| **Phase 5: Database & Multi-User** | **PARTIAL** | SQLite lưu trữ bền vững qua restart. Đạt phân quyền tenant. Tuy nhiên **chưa bật SQLite FK pragma**, thiếu endpoint sửa/xóa Chapter, và chưa hỗ trợ driver PostgreSQL (`asyncpg`/`psycopg2`). |
| **Phase 6: Real Video Pipeline** | **PARTIAL** | Luồng phân tích kịch bản và sinh phụ đề chạy mượt. Nhưng khâu **tìm kiếm tư liệu không tự động gắn ảnh vào cảnh**, và **renderer không vẽ ảnh thật**. |
| **Phase 7: Long-Form Workflow** | **PARTIAL** | Phân chương kịch bản và render 16:9 (1920x1080) 60 giây chạy tốt. Nhưng **hoàn toàn chưa có bộ ghép nối phân đoạn (Segment Assembly)** và chưa có quản lý bộ nhớ cho video 30-60 phút. |
| **Phase 8: Public Deployment** | **FAIL** | `backend/Dockerfile` hỏng do thiếu dependency; CORS dùng sai cú pháp wildcard cho domain con; chưa có bộ dọn dẹp ổ đĩa lưu tệp audio; không có hàng đợi worker nền. |

---

## II. KẾT QUẢ KIỂM TRA ĐỘC LẬP TỪNG PHÂN HỆ

### 1. PHASE 1 — GIT VÀ THAY ĐỔI MÃ NGUỒN (CHANGE AUDIT)
* **Trạng thái Git:**
  * Branch: `feature/unified-ai-video-studio`
  * Commit kiểm toán: `76bc55b8b400c92488d767362c63b45393c79a41`
  * Trạng thái remote: Nhánh đã được đẩy lên `origin/feature/unified-ai-video-studio`.
  * Working tree: Sạch sẽ (`working tree clean`).
  * Diff với nhánh `main`: 34 tệp thay đổi, 3,281 dòng thêm mới, 795 dòng bị xóa.
* **Vệ sinh bí mật (Secret Hygiene):** ĐẠT (`PASS`). Quét `git grep` toàn bộ repo không phát hiện khóa API thực tế, private key hay secret thật. Toàn bộ là placeholder hoặc đọc từ biến môi trường.
* **Kiểm tra Dependencies:**
  * **Phát hiện lỗi nghiêm trọng (P0):** `backend/requirements.txt` chỉ bao gồm 15 packages. Trong mã nguồn `backend/core/database.py`, `backend/models/db_models.py`, `backend/routers/projects.py` sử dụng `sqlalchemy` (v2.0+) và `greenlet` (v3.0+). Hai gói này **hoàn toàn vắng mặt** trong `requirements.txt`.
  * **Phát hiện gói rác (P2):** `frontend/package.json` khai báo `@remotion/web-renderer` và `remotion`, nhưng kiểm tra toàn bộ thư mục `frontend/src` không có bất kỳ lệnh import nào từ hai gói này. Bộ renderer hiện tại là thuần WebCodecs + `mp4-muxer`.

---

### 2. PHASE 2 — KIỂM ĐỊNH RENDER VIDEO MP4 BẰNG WEBCODECS

Đã triển khai script kiểm thử độc lập `run_phase2_video_audit.py` điều khiển trình duyệt Google Chrome thật qua giao thức Chrome DevTools Protocol (CDP) kết hợp WebCodecs:

| Tên kịch bản kiểm tra | Độ phân giải | Thời lượng video | Khung hình | Tốc độ render | Kích thước file | Cấu trúc ISOBMFF | CoreAudio afinfo |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. 30s Shorts Lịch sử** | 1080x1920 (9:16) | 30.00s | 900 frames | **160.6 FPS** (5.74s) | 9,092,730 B (9.09 MB) | `ftyp`, `moov`, `mdat` (Fast Start) | `2 ch, 48kHz, aac` - PASS |
| **2. 60s Shorts Kinh dị** | 1080x1920 (9:16) | 60.00s | 1800 frames | **54.9 FPS** (32.9s) | 5,776,329 B (5.78 MB) | `ftyp`, `moov`, `mdat` (Fast Start) | `2 ch, 48kHz, aac` - PASS |
| **3. 60s Long-Form Kinh tế**| 1920x1080 (16:9) | 60.00s | 1800 frames | **165.9 FPS** (11.17s)| 21,060,836 B (21.06 MB)| `ftyp`, `moov`, `mdat` (Fast Start) | `2 ch, 48kHz, aac` - PASS |
| **4. Multi-scene (5 cảnh)** | 1080x1920 (9:16) | 25.00s | 750 frames | **161.3 FPS** (4.85s) | 8,132,107 B (8.13 MB) | `ftyp`, `moov`, `mdat` (Fast Start) | `2 ch, 48kHz, aac` - PASS |

* **Đánh giá Encoder:**
  * Mã hóa H.264 (`avc1.4d002a`) phần cứng hoạt động cực nhanh (160+ FPS trên Apple Silicon M3).
  * Mã hóa âm thanh AAC (`mp4a.40.2`) 48kHz Stereo hoạt động ổn định.
  * Container MP4 mux bằng `mp4-muxer` với cấu hình `fastStart: 'in-memory'` đảm bảo atom `moov` nằm ngay sau `ftyp` và đứng trước `mdat`.
* **Khiếm khuyết cốt lõi đã phát hiện (P0):**
  * Trong tệp `frontend/src/services/webcodecsRenderer.ts` dòng 152–176, track âm thanh được sinh bằng thuật toán sóng sin:
    ```typescript
    // Synthesize rhythmic BGM bed (march / tension chord)
    const bass = Math.sin(2 * Math.PI * 110 * t) * 0.12;
    const rhythm = Math.sin(2 * Math.PI * 2 * t) > 0.8 ? 0.08 : 0.0;
    const sample = bass + rhythm;
    pcm[i * 2] = sample;
    pcm[i * 2 + 1] = sample;
    ```
  * Mã nguồn **chưa thực hiện** việc tải các file lồng tiếng thực (`scene.audio_url`), giải mã PCM qua Web Audio API (`AudioContext.decodeAudioData`) và trộn vào dòng audio buffer trước khi gửi vào `AudioEncoder`. Do đó video xuất ra **chỉ có tiếng synth nền, chưa có giọng đọc thật**.

---

### 3. PHASE 3 — KIỂM ĐỊNH BỘ GIỌNG NÓI TIẾNG VIỆT (EDGE-TTS AUDIT)

Đã chạy các bài kiểm thử tự động trực tiếp trên thư viện `edge_tts`:
1. **Kiểm tra 2 giọng đọc:**
   * `vi-VN-NamMinhNeural`: Tạo ra 21,744 bytes MP3, 11 word boundaries trong **0.66 giây** (Rất tốt).
   * `vi-VN-HoaiMyNeural`: Tạo ra 22,320 bytes MP3, 11 word boundaries nhưng mất **17.88 giây** do độ trễ bắt tay websocket.
2. **Kiểm tra độ chính xác mốc thời gian (Word Boundary Extraction):**
   * Đơn vị thời gian 100-nanosecond tick của Microsoft được chuyển đổi chuẩn xác sang millisecond (`chunk["offset"] // 10000`).
3. **Thực nghiệm độ ổn định tải đồng thời (5 Concurrent Requests):**
   * Kết quả: **2/5 request bị sập** với lỗi:
     `edge_tts.exceptions.NoAudioReceived: No audio was received. Please verify that your parameters are correct.`
   * **Nguyên nhân:** Microsoft Edge-TTS giới hạn số lượng kết nối websocket đồng thời trên cùng một IP. `EdgeTTSVoiceProvider` hiện chưa có hàng đợi điều tiết (semaphore) để kiểm soát số luồng song song.
4. **Thực nghiệm văn bản dài (>500 từ / 2,379 ký tự):**
   * Kết quả: **Sập 100%** ngay lần gọi đầu tiên với lỗi `NoAudioReceived`.
   * **Nguyên nhân:** Microsoft Edge-TTS không cho phép gửi văn bản quá dài trong một thông điệp websocket duy nhất. Phải có module phân đoạn văn bản theo dấu câu (chunking) trước khi tổng hợp.
5. **Cơ chế Cache âm thanh:**
   * Trong `backend/providers/tts_engine.py` dòng 196: `audio_id = str(uuid.uuid4())`. Mỗi lần gọi API đều sinh UUID ngẫu nhiên mới và gọi ra internet, **hoàn toàn không có cache theo mã băm nội dung (content-based hashing)**.
6. **Cơ chế Fallback khi lỗi:**
   * Khi Edge-TTS thất bại, hệ thống rơi vào `TTSService`, trả về URL `/api/v1/tts/sample_audio.wav?...`. Tuy nhiên endpoint này **không tồn tại** trong `backend/routers/tts.py`, dẫn đến lỗi HTTP 404 cho client.

---

### 4. PHASE 4 — KIỂM ĐỊNH BẢO MẬT & PHÂN QUYỀN (SECURITY AUDIT)

| Kịch bản kiểm thử bảo mật | Kỳ vọng | Kết quả thực tế | Đánh giá |
| :--- | :--- | :--- | :---: |
| **1. Missing / Empty Secret** | Chặn đứng, trả về HTTP 401 | HTTP 401 Unauthorized (`Server JWT secret is not configured`) | **PASS** |
| **2. Placeholder Secret** | Không cho phép bypass | HTTP 401 Unauthorized | **PASS** |
| **3. Token hết hạn (`exp`)** | Chặn đứng, trả về HTTP 401 | HTTP 401 Unauthorized (`JWT token has expired`) | **PASS** |
| **4. Thuật toán `alg: none`** | Từ chối ngay lập tức | HTTP 401 Unauthorized (`Unsupported signing algorithm 'none'`) | **PASS** |
| **5. Token sai chữ ký HMAC** | Từ chối | HTTP 401 Unauthorized (`JWT signature verification failed`) | **PASS** |
| **6. User A truy cập Project User B** | Chặn đứng, trả về HTTP 403 | HTTP 403 Forbidden (`Access denied to this project`) | **PASS** |
| **7. User A truy cập Episode User B** | Chặn đứng, trả về HTTP 403 | HTTP 403 Forbidden (`Access denied`) | **PASS** |
| **8. Kiểm tra Issuer (`iss`) & Audience (`aud`)** | Phải xác minh `aud: authenticated` | **Không kiểm tra `iss` hay `aud`** trong `jwt.decode` | **FAIL (P1)** |
| **9. Truy cập tệp âm thanh không có token** | Chỉ chủ sở hữu mới được nghe | Endpoint `/api/v1/tts/audio/{filename}` **không yêu cầu token** | **FAIL (P1)** |

---

### 5. PHASE 5 — CƠ SỞ DỮ LIỆU & ĐA NGƯỜI DÙNG (DATABASE AUDIT)

1. **Khởi tạo và Lưu trữ bền vững:**
   * Cơ sở dữ liệu SQLite tại `./data/ytber.db` khởi tạo thành công 4 bảng: `projects`, `episodes`, `chapters`, `render_jobs`.
   * Thử nghiệm khởi động lại FastAPI: Toàn bộ dữ liệu dự án và tập phim vẫn tồn tại đầy đủ.
2. **Kiểm tra Ràng buộc Khóa Ngoại (Foreign Key Constraints):**
   * **Thực nghiệm độc lập:** Chèn một `EpisodeModel` với `project_id = "non-existent-project-id-99999"`.
   * **Kết quả:** Bản ghi được chèn thành công mà không gặp bất kỳ lỗi nào!
   * **Nguyên nhân:** SQLite mặc định tắt kiểm tra khóa ngoại. `backend/core/database.py` chưa đăng ký sự kiện lắng nghe kết nối để thực thi `PRAGMA foreign_keys = ON;`.
3. **Tính tương thích PostgreSQL:**
   * Trong `backend/core/database.py` dòng 38: `sync_url = settings.DATABASE_URL.replace("+aiosqlite", "")`. Khi chuyển sang PostgreSQL (`postgresql+asyncpg://...`), chuỗi `sync_url` vẫn giữ nguyên driver bất đồng bộ `asyncpg` và gây lỗi crash khi khởi chạy sync engine. Ngoài ra driver `asyncpg` chưa được thêm vào `requirements.txt`.
4. **Khiếm khuyết Chapter CRUD:**
   * Hệ thống mới chỉ có `GET /episodes/{id}/chapters` và `POST /episodes/{id}/chapters`. Chưa có endpoint `PUT` (cập nhật nội dung chương) và `DELETE` (xóa chương).

---

### 6. PHASE 6 — KIỂM ĐỊNH TOÀN BỘ PIPELINE SẢN XUẤT VIDEO THỰC TẾ

Đã thử nghiệm quy trình thực tế trên 4 thể loại chính:
1. *Horror / Mystery*
2. *Historical Documentary*
3. *Economics / Finance*
4. *Science / Technology*

**Kết quả rà soát từng công đoạn trong chuỗi sản xuất:**
1. **Script input ➔ Script analysis:** **HOẠT ĐỘNG TỐT (PASS)**. NLP phân tích cấu trúc, nhận diện bối cảnh, sinh số lượng cảnh hợp lý.
2. **Scene generation ➔ Audio Cueing:** **HOẠT ĐỘNG TỐT (PASS)**. Gán đúng sound cues theo thể loại (ví dụ kinh dị: `heartbeat_low`, `eerie_drone`).
3. **Asset Discovery ➔ Image Retrieval:** **ĐỨT ĐOẠN (FAIL - P0)**.
   * Endpoint `/api/v1/assets/search` có khả năng tìm kiếm ảnh từ Wikimedia/Openverse.
   * **Tuy nhiên:** Hàm phân tích kịch bản không tự động gọi tìm kiếm tư liệu để gán URL ảnh vào từng cảnh.
   * Bộ dựng client (`webcodecsRenderer.ts`) hoàn toàn không có cơ chế tải ảnh từ internet và vẽ vào khung hình (`drawImage`). Toàn bộ khung cảnh hiện là đồ họa vector giả lập.
4. **Voice generation ➔ Synchronization:** **CHƯA ĐỒNG BỘ VÀO FILE (FAIL - P0)**.
   * Âm thanh lồng tiếng được sinh ra và lưu trên server, có mốc thời gian từng từ.
   * Nhưng renderer chưa đưa tệp âm thanh này vào video MP4 xuất bản.

---

### 7. PHASE 7 — KIỂM ĐỊNH VIDEO DÀI (LONG-FORM AUDIT)

* **Phân chia chương:** AI phân chia kịch bản dài thành các chapter (mỗi chapter 2–4 cảnh) và lưu vào bảng `chapters` thành công.
* **Tỷ lệ 16:9 (1920x1080):** Đã render thành công video 1920x1080 dài 60 giây (1800 frames, 21 MB, 165 FPS).
* **Khiếm khuyết cốt lõi (P0):**
  * **Chưa có cơ chế Ghép Phân Đoạn (Segment Assembly):** Không có mã nguồn nào thực hiện ghép các file MP4 của từng chương lại với nhau.
  * **Tràn bộ nhớ RAM trình duyệt:** Bộ nhớ đệm của `mp4-muxer` đang dùng `ArrayBufferTarget` (lưu toàn bộ tệp MP4 trong RAM trình duyệt). Với video tài liệu dài 30–60 phút (dung lượng từ 500MB đến 2GB), trình duyệt sẽ bị quá tải bộ nhớ và crash tab. Phải chuyển sang cơ chế `FileSystemWritableFileStream` hoặc chia nhỏ phân đoạn lưu tạm qua OPFS (Origin Private File System).
  * **Không thể khôi phục khi bị gián đoạn:** Nếu người dùng đang render video dài 30 phút mà đóng tab hoặc máy tính sleep, tiến trình mất 100% và phải làm lại từ đầu.

---

### 8. PHASE 8 — CẤU HÌNH TRIỂN KHAI VÀ GIỚI HẠN FREE-TIER (DEPLOYMENT AUDIT)

#### Phân loại trạng thái tính năng triển khai:
* **A. Đã triển khai và đã kiểm thử (Implemented & Tested):**
  * WebCodecs + `mp4-muxer` client-side rendering (1080x1920 & 1920x1080).
  * Backend API Authentication với `PyJWT` fail-closed.
  * SQLite async persistence cho Projects & Episodes.
  * Phân tích kịch bản tiếng Việt bằng NLP tất định.
* **B. Đã triển khai nhưng chưa hoàn thiện / kiểm thử giới hạn (Implemented but Incomplete):**
  * Microsoft Edge-TTS (Chạy tốt với đơn lẻ, sập khi tải đồng thời hoặc text dài).
  * Wikimedia / Openverse Asset search (Có API tìm kiếm nhưng chưa gắn vào renderer).
  * In-memory Rate Limiting (60 req/min trên 1 tiến trình; mất tác dụng nếu chạy đa tiến trình uvicorn).
* **C. Đã thiết kế nhưng chưa triển khai mã nguồn (Designed but Not Implemented):**
  * Cơ chế ghép nối video dài (Long-form Segment Assembly).
  * Cơ chế trộn giọng đọc thật (Edge-TTS Audio Mixing) vào WebCodecs canvas.
  * Hàng đợi xử lý tác vụ nền (Background Worker / Job Queue).
  * Phân bổ hạn ngạch người dùng (User Quotas per tier).
  * Cơ chế dọn dẹp định kỳ tệp âm thanh trên đĩa cứng (Storage TTL Cleanup).
* **D. Rào cản dịch vụ bên ngoài (External Service Limitations):**
  * **Microsoft Edge-TTS:** Là dịch vụ không chính thức (reverse-engineered websocket). Sẽ ngắt kết nối nếu gửi quá nhiều request cùng lúc hoặc gửi văn bản quá dài. Cần có semaphore điều tiết tối đa 2 request đồng thời trên 1 IP máy chủ.
  * **Hạ tầng miễn phí:** Hugging Face CPU Spaces hoặc Render Free Tier chỉ cung cấp 512MB RAM và không có persistent disk vĩnh viễn (sẽ mất file SQLite khi container restart nếu không gắn Volume).

---

## III. KẾ HOẠCH KHẮC PHỤC THEO THỨ TỰ ƯU TIÊN (PRIORITIZED REMEDIATION PLAN)

### Ưu tiên P0 (Bắt buộc phải sửa để hệ thống chạy được cơ bản)
1. **Bổ sung phụ thuộc backend:** Thêm ngay `sqlalchemy>=2.0.0` và `greenlet>=3.0.0` vào `backend/requirements.txt` để Docker và môi trường mới cài đặt thành công.
2. **Nhúng giọng đọc Edge-TTS vào WebCodecs Renderer:**
   * Trong `webcodecsRenderer.ts`, thêm hàm `fetchAudioBuffer(url)` và dùng `AudioContext.decodeAudioData` để lấy dữ liệu PCM thực tế của giọng đọc.
   * Đưa dữ liệu PCM thực tế vào `AudioEncoder` thay cho đoạn code tạo sóng sin tạm thời.
3. **Cắt nhỏ văn bản (Chunking) & Giới hạn luồng (Semaphore) cho Edge-TTS:**
   * Trong `tts_engine.py`, thêm hàm cắt văn bản thành các đoạn tối đa 250 ký tự theo dấu chấm/phẩy trước khi gửi cho `edge_tts`.
   * Sử dụng `asyncio.Semaphore(2)` để ngăn việc mở quá nhiều websocket cùng lúc gây lỗi `NoAudioReceived`.
4. **Tải và nhúng ảnh tư liệu thật vào Video Canvas:**
   * Tự động gọi `search_wikimedia` trong quá trình phân tích kịch bản để điền `image_url` vào từng cảnh.
   * Trong `webcodecsRenderer.ts`, sử dụng `createImageBitmap` hoặc `HTMLImageElement` để vẽ ảnh tư liệu lên Canvas qua lệnh `ctx.drawImage` thay vì chỉ vẽ vector giả lập.

### Ưu tiên P1 (Đảm bảo an toàn, bảo mật và tính toàn vẹn)
1. **Bật ràng buộc khóa ngoại SQLite:**
   * Trong `backend/core/database.py`, thêm event listener `PRAGMA foreign_keys = ON;` cho SQLAlchemy engine.
2. **Bảo mật endpoint tải âm thanh:**
   * Thêm `user_id: str = Depends(get_current_user_id)` vào `GET /api/v1/tts/audio/{filename}` hoặc sử dụng signed URL có hạn sử dụng ngắn.
3. **Kiểm tra Audience & Issuer JWT:**
   * Thêm xác thực `audience="authenticated"` trong hàm `decode_and_verify_supabase_jwt`.
4. **Cơ chế Cache âm thanh theo Content Hash:**
   * Đặt tên file MP3 theo mã băm SHA256: `hashlib.sha256((text + voice).encode()).hexdigest() + ".mp3"`. Nếu file đã tồn tại trên đĩa, trả về ngay lập tức mà không gọi ra Microsoft.
5. **Sửa lỗi cú pháp CORS:**
   * Sửa cấu hình CORS trong `backend/main.py`, chuyển `https://*.pages.dev` sang tham số `allow_origin_regex=r"^https://.*\.pages\.dev$"`.

### Ưu tiên P2 (Nâng cao năng lực và mở rộng hệ thống)
1. **Xây dựng bộ ghép nối phân đoạn Long-Form (Segment Assembly):**
   * Sử dụng thư viện `mp4box.js` hoặc cơ chế muxer đa chuỗi để ghép nối các file MP4 từng chương thành 1 file MP4 hoàn chỉnh.
2. **Dọn dẹp tệp âm thanh quá hạn (Cron / Lifecycle):**
   * Xây dựng script định kỳ xóa các tệp MP3 trong `./data/audio/` có tuổi thọ trên 48 giờ để tránh đầy dung lượng đĩa cứng.
3. **Bổ sung endpoint cập nhật / xóa chương:**
   * Thêm `PUT /api/v1/episodes/{episode_id}/chapters/{chapter_id}` và `DELETE /api/v1/episodes/{episode_id}/chapters/{chapter_id}`.

---

## IV. LỆNH TÁI LẬP KIỂM TOÁN TẠI MÁY CỤC BỘ (EXACT REPRODUCTION COMMANDS)

Quý kỹ sư có thể tự mình chạy lại toàn bộ các bước kiểm toán độc lập bằng các câu lệnh chính xác dưới đây:

### 1. Kiểm tra mã nguồn, nhánh Git và sự cố thiếu package
```bash
# Di chuyển vào thư mục dự án
cd /Users/thienduc/Desktop/Code/ytbshorts

# Kiểm tra commit hiện tại và trạng thái git
git branch -vv
git status

# Chứng minh lỗi thiếu sqlalchemy trong requirements.txt
grep -i "sqlalchemy" backend/requirements.txt || echo "THIẾU SQLALCHEMY TRONG REQUIREMENTS.TXT!"
```

### 2. Kiểm tra bộ kiểm thử tự động Backend (22 tests)
```bash
python3 -m pytest backend/tests/ -v
```

### 3. Tái lập kiểm định WebCodecs MP4 Muxing & Render 4 video độc lập (30s 9:16, 60s 9:16, 60s 16:9, Multi-scene)
```bash
# Chạy script kiểm toán video thực tế điều khiển Chrome headless
python3 run_phase2_video_audit.py

# Kiểm tra dung lượng và thông số 4 file MP4 kết quả
ls -lh /tmp/ytber_audit_videos/

# Kiểm tra tính toàn vẹn track âm thanh AAC qua công cụ macOS CoreAudio
afinfo /tmp/ytber_audit_videos/video_30s_916.mp4
afinfo /tmp/ytber_audit_videos/video_60s_169.mp4
```

### 4. Tái lập thực nghiệm lỗi Edge-TTS (Đồng thời & Kịch bản dài)
```bash
# Thử nghiệm gửi kịch bản dài 500 từ (Sẽ thấy lỗi NoAudioReceived từ Microsoft)
python3 -c "
import asyncio, edge_tts
async def test():
    text = ' '.join(['Việt Nam là một quốc gia độc lập có chủ quyền.'] * 40)
    c = edge_tts.Communicate(text=text, voice='vi-VN-NamMinhNeural')
    async for chunk in c.stream(): pass
asyncio.run(test())
"

# Thử nghiệm 5 kết nối đồng thời (Sẽ thấy 2 kết nối bị ngắt quãng)
python3 -c "
import asyncio, edge_tts
async def test():
    async def fetch(i):
        c = edge_tts.Communicate('Kiểm tra đồng thời', voice='vi-VN-NamMinhNeural')
        b = 0
        async for ch in c.stream():
            if ch['type'] == 'audio': b += len(ch['data'])
        return i, b
    res = await asyncio.gather(*[fetch(i) for i in range(5)], return_exceptions=True)
    print('Kết quả 5 kết nối song song:', res)
asyncio.run(test())
"
```

### 5. Tái lập thực nghiệm lỗi Khóa Ngoại (Foreign Key) trên SQLite
```bash
python3 -c "
import asyncio, uuid
from backend.core.database import AsyncSessionLocal
from backend.models.db_models import EpisodeModel
async def test():
    async with AsyncSessionLocal() as s:
        s.add(EpisodeModel(id=str(uuid.uuid4()), project_id='non-existent-id', user_id='u', title='Test FK'))
        await s.commit()
        print('CẢNH BÁO: Chèn thành công Episode với project_id không tồn tại (Thiếu PRAGMA foreign_keys=ON)!')
asyncio.run(test())
"
```
