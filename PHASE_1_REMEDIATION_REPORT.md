# BÁO CÁO KHẮC PHỤC HẠ TẦNG VÀ BẢO MẬT: PHASE 1 REMEDIATION REPORT
**Dự án:** YTBER — Unified AI Video Studio  
**Repository:** `thienduc-07/ytber`  
**Nhánh Git:** `feature/unified-ai-video-studio`  
**Audit Baseline:** `76bc55b8b400c92488d767362c63b45393c79a41`  
**Thời điểm thực hiện:** 2026-11-20  
**Trạng thái kiểm tra:** **PHASE 1 PASSED (100% Tiêu chí nghiệm thu hoàn thành)**  

---

## 1. CÁC LỖI BAN ĐẦU ĐÃ ĐƯỢC XÁC ĐỊNH (INITIAL ISSUES)

Dựa trên kết quả từ Production Audit, 6 lỗi hạ tầng và bảo mật cốt lõi cần giải quyết ngay:
1. **[P0] Thiếu phụ thuộc nền tảng trong `requirements.txt`:** `SQLAlchemy>=2.0.0` và `greenlet>=3.0.0` được import trong toàn bộ code database của backend nhưng không có trong `requirements.txt`, làm Docker build và môi trường sạch bị crash khi khởi động.
2. **[P0] Docker build thất bại / thiếu `.dockerignore`:** Không có `.dockerignore` khiến toàn bộ thư mục `.venv` (hàng trăm MB) bị gửi vào build context, gây tràn I/O và lỗi giải nén.
3. **[P1] SQLite không bật kiểm tra khóa ngoại (Foreign Keys Disabled):** SQLite mặc định tắt `foreign_keys`, dẫn đến việc có thể chèn các Episode/Chapter mồ côi không gắn với Project hợp lệ, làm hỏng tính toàn vẹn dữ liệu.
4. **[P1] JWT thiếu xác thực Audience (`aud`) và Issuer (`iss`):** PyJWT chỉ kiểm tra signature và expiration mà không xác thực audience (`authenticated`) và issuer, có thể bị lợi dụng bởi token phát hành từ dự án Supabase khác hoặc token `anon`.
5. **[P1] Endpoint audio stream không có phân quyền (`/api/v1/tts/audio/{filename}`):** Bất kỳ ai biết tên file đều có thể tải audio mà không cần token xác thực; thiếu cơ chế ngăn chặn Path Traversal (`../`).
6. **[P1] Cấu hình CORS dùng sai cú pháp wildcard:** `https://*.pages.dev` đặt trong `allow_origins` không có tác dụng trong Starlette, khiến frontend trên Cloudflare Pages bị chặn CORS.
7. **[P1] Thiếu API cập nhật và xóa Chapter:** Chưa có `PUT` và `DELETE` cho từng chương trong một tập phim.

---

## 2. NGUYÊN NHÂN GỐC RỄ (ROOT CAUSE ANALYSIS)

* **Dependencies:** Trong quá trình nâng cấp từ in-memory dictionary lên SQLite DB, `SQLAlchemy` và `greenlet` được cài đặt cục bộ qua pip nhưng chưa được ghi lại vào `backend/requirements.txt`.
* **SQLite FK:** Trong SQLite, kết nối pool của SQLAlchemy mặc định không tự động gửi lệnh `PRAGMA foreign_keys = ON;`. Cần có một connection listener event `@event.listens_for(engine.sync_engine, "connect")`.
* **JWT:** Cấu hình `jwt.decode` chưa kích hoạt cờ `verify_aud` và `verify_iss`, đồng thời chưa có cấu hình dự phòng cho `role` của Supabase token.
* **Audio Security:** Endpoint `/api/v1/tts/audio/{filename}` ban đầu được thiết kế phục vụ thẻ `<audio>` tĩnh mà không lưu quyền sở hữu người dùng trong cơ sở dữ liệu.
* **CORS Wildcard:** Starlette `CORSMiddleware` phân biệt giữa so khớp chuỗi tuyệt đối (`allow_origins`) và so khớp biểu thức chính quy (`allow_origin_regex`). Ký tự `*` trong `allow_origins` chỉ hoạt động khi đứng một mình (`["*"]`), không hỗ trợ tiền tố/hậu tố.

---

## 3. NHỮNG TỆP ĐÃ CHỈNH SỬA VÀ THÊM MỚI (MODIFIED & ADDED FILES)

| Tệp tin | Loại thay đổi | Mô tả kỹ thuật |
| :--- | :---: | :--- |
| `backend/requirements.txt` | Sửa đổi | Bổ sung `sqlalchemy>=2.0.0` và `greenlet>=3.0.0`. |
| `.dockerignore` | Thêm mới | Loại bỏ `.venv`, `node_modules`, `data/`, `__pycache__`, `tmp/` khỏi Docker build context. |
| `backend/core/config.py` | Sửa đổi | Thêm `SUPABASE_JWT_AUDIENCE` và `SUPABASE_JWT_ISSUER`. |
| `backend/core/database.py` | Sửa đổi | Đăng ký event `PRAGMA foreign_keys = ON;` cho cả async engine và sync engine. Xử lý chuẩn hóa URL kết nối cho cả SQLite và PostgreSQL. |
| `backend/models/db_models.py` | Sửa đổi | Thêm model `AudioFileModel` để lưu trữ quyền sở hữu tệp âm thanh theo `user_id`. |
| `backend/core/security.py` | Sửa đổi | Bổ sung xác thực Audience và Issuer trong `decode_and_verify_supabase_jwt`, kiểm tra token claims, hỗ trợ fallback `role`. |
| `backend/routers/tts.py` | Sửa đổi | Lưu metadata quyền sở hữu khi tổng hợp giọng nói. Bổ sung xác thực Bearer / query token `token=...`, kiểm tra quyền sở hữu, ngăn chặn Path Traversal và che giấu đường dẫn filesystem. |
| `backend/providers/tts_engine.py` | Sửa đổi | Chuyển `storage_dir` thành dynamic property đọc từ `settings.AUDIO_STORAGE_PATH`. |
| `backend/main.py` | Sửa đổi | Cấu hình `allow_origin_regex=r"^https://[a-zA-Z0-9-]+\.pages\.dev$"` cho Cloudflare Pages. |
| `backend/routers/projects.py` | Sửa đổi | Thêm `ChapterUpdateRequest`, triển khai endpoint `PUT` và `DELETE` cho Chapter có kiểm tra quyền sở hữu. |
| `backend/tests/test_phase1_remediation.py` | Thêm mới | Bộ kiểm thử tích hợp 11 kịch bản kiểm tra toàn diện cho các thành phần vừa khắc phục. |

---

## 4. GIẢI PHÁP KỸ THUẬT CHI TIẾT (TECHNICAL IMPLEMENTATION)

### 4.1. SQLite Foreign Key Enforcement
Đăng ký lắng nghe sự kiện kết nối của SQLAlchemy engine:
```python
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```
Bảo đảm mọi kết nối lấy ra từ pool đều được kích hoạt `PRAGMA foreign_keys = 1`.

### 4.2. JWT Security & Audience / Issuer Validation
Tự động xác thực `aud` (`authenticated`) và `iss` (nếu cấu hình):
```python
# Xác thực chữ ký, hạn dùng, issuer qua PyJWT
payload = jwt.decode(
    token,
    key=jwt_secret,
    algorithms=[alg],
    issuer=expected_iss if expected_iss else None,
    options=decode_options
)
# Xác thực audience nghiêm ngặt (hỗ trợ aud claim và fallback role claim)
if expected_aud:
    token_aud = payload.get("aud")
    token_role = payload.get("role")
    ...
```

### 4.3. Phân quyền và Bảo mật Tệp Âm thanh (Audio Authorization)
* Khi gọi `POST /api/v1/tts/synthesize`, lưu bản ghi vào bảng `audio_files` với `user_id` của người tạo.
* Khi gọi `GET /api/v1/tts/audio/{filename}`:
  1. Chặn Path Traversal: `if ".." in filename or "/" in filename or "\\" in filename: raise 400`
  2. Định dạng filename hợp lệ: `re.match(r"^[a-zA-Z0-9_-]+\.(mp3|wav)$", filename)`
  3. Xác thực Bearer Token (qua header `Authorization` hoặc query param `?token=...` cho thẻ HTML5 audio).
  4. Truy vấn database kiểm tra quyền sở hữu: nếu `audio_rec.user_id != current_user_id` ➔ trả về `HTTP 403 Forbidden`.
  5. Đảm bảo đường dẫn tệp tuyệt đối nằm trong thư mục `AUDIO_STORAGE_PATH`.

### 4.4. Cấu hình CORS Regex
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://zero-budget-video-studio.pages.dev"
    ],
    allow_origin_regex=r"^https://[a-zA-Z0-9-]+\.pages\.dev$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
)
```

---

## 5. KẾT QUẢ KIỂM THỬ THỰC TẾ (TEST RESULTS)

### 5.1. Bộ Kiểm Thử Khắc Phục Mới (`test_phase1_remediation.py`)
11/11 tests hoàn thành thành công 100%:
```
backend/tests/test_phase1_remediation.py::test_sqlite_foreign_key_enforcement PASSED [  9%]
backend/tests/test_phase1_remediation.py::test_sqlite_cascade_delete PASSED         [ 18%]
backend/tests/test_phase1_remediation.py::test_jwt_valid_token PASSED               [ 27%]
backend/tests/test_phase1_remediation.py::test_jwt_expired_token PASSED             [ 36%]
backend/tests/test_phase1_remediation.py::test_jwt_invalid_signature PASSED         [ 45%]
backend/tests/test_phase1_remediation.py::test_jwt_invalid_audience PASSED          [ 54%]
backend/tests/test_phase1_remediation.py::test_jwt_invalid_issuer PASSED            [ 63%]
backend/tests/test_phase1_remediation.py::test_jwt_algorithm_none_rejected PASSED   [ 72%]
backend/tests/test_phase1_remediation.py::test_audio_endpoint_security_and_authorization PASSED [ 81%]
backend/tests/test_phase1_remediation.py::test_cors_cloudflare_pages_regex PASSED   [ 90%]
backend/tests/test_phase1_remediation.py::test_chapter_crud_api_and_tenant_isolation PASSED [100%]
```

### 5.2. Toàn Bộ Test Suite Backend (Regression Tests)
**33/33 tests** chạy tự động và vượt qua thành công:
```
============================= test session starts ==============================
collected 33 items

backend/tests/test_assets_and_tts.py::test_number_to_vietnamese_words PASSED   [  3%]
backend/tests/test_assets_and_tts.py::test_vietnamese_text_normalizer PASSED   [  6%]
backend/tests/test_assets_and_tts.py::test_tts_syllable_timings PASSED         [  9%]
backend/tests/test_assets_and_tts.py::test_real_edge_tts_voice_provider PASSED [ 12%]
backend/tests/test_assets_and_tts.py::test_asset_discovery_wikimedia PASSED   [ 15%]
backend/tests/test_auth_security.py::test_valid_jwt_decoding PASSED            [ 18%]
backend/tests/test_auth_security.py::test_expired_jwt_rejection PASSED         [ 21%]
backend/tests/test_auth_security.py::test_invalid_signature_rejection PASSED   [ 24%]
backend/tests/test_auth_security.py::test_malformed_token_rejection PASSED     [ 27%]
backend/tests/test_auth_security.py::test_fail_closed_when_secret_is_placeholder_or_missing PASSED [ 30%]
backend/tests/test_auth_security.py::test_algorithm_none_rejection PASSED       [ 33%]
backend/tests/test_e2e_pipeline.py::test_complete_end_to_end_pipeline PASSED   [ 36%]
backend/tests/test_e2e_pipeline.py::test_full_studio_api_workflow_end_to_end PASSED [ 39%]
backend/tests/test_phase1_remediation.py::test_sqlite_foreign_key_enforcement PASSED [ 42%]
backend/tests/test_phase1_remediation.py::test_sqlite_cascade_delete PASSED   [ 45%]
backend/tests/test_phase1_remediation.py::test_jwt_valid_token PASSED          [ 48%]
backend/tests/test_phase1_remediation.py::test_jwt_expired_token PASSED        [ 51%]
backend/tests/test_phase1_remediation.py::test_jwt_invalid_signature PASSED   [ 54%]
backend/tests/test_phase1_remediation.py::test_jwt_invalid_audience PASSED    [ 57%]
backend/tests/test_phase1_remediation.py::test_jwt_invalid_issuer PASSED      [ 60%]
backend/tests/test_phase1_remediation.py::test_jwt_algorithm_none_rejected PASSED [ 63%]
backend/tests/test_phase1_remediation.py::test_audio_endpoint_security_and_authorization PASSED [ 66%]
backend/tests/test_phase1_remediation.py::test_cors_cloudflare_pages_regex PASSED [ 69%]
backend/tests/test_phase1_remediation.py::test_chapter_crud_api_and_tenant_isolation PASSED [ 72%]
backend/tests/test_projects_api.py::test_healthz_and_status PASSED             [ 75%]
backend/tests/test_projects_api.py::test_security_headers PASSED               [ 78%]
backend/tests/test_projects_api.py::test_project_crud_and_episode_flow PASSED [ 81%]
backend/tests/test_projects_api.py::test_tenant_isolation PASSED               [ 84%]
backend/tests/test_script_engine.py::test_count_vietnamese_syllables PASSED    [ 87%]
backend/tests/test_script_engine.py::test_rule_based_script_analysis PASSED   [ 90%]
backend/tests/test_script_engine.py::test_groq_fallback_when_unconfigured PASSED [ 93%]
backend/tests/test_script_engine.py::test_horror_genre_specialization PASSED   [ 96%]
backend/tests/test_script_engine.py::test_long_form_chapter_planning PASSED   [100%]

======================= 33 passed, 30 warnings in 3.45s ========================
```

---

## 6. KẾT QUẢ DOCKER BUILD VÀ RUNTIME RUN CHECK

### 6.1. Docker Build Thành Công
Lệnh build: `docker build -t ytber-backend:latest -f backend/Dockerfile .`
```
[+] Building 14.9s (10/10) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [1/5] FROM docker.io/library/python:3.11-slim
 => [2/5] WORKDIR /app
 => [3/5] COPY backend/requirements.txt /app/requirements.txt
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt
 => [5/5] COPY backend /app/backend
 => exporting to image
 => naming to docker.io/library/ytber-backend:latest
```

### 6.2. Docker Container Khởi Động & Health Check
Lệnh khởi động: `docker run -d --name ytber-backend-test -p 8008:8000 ytber-backend:latest`
Log container:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
Kiểm tra endpoint `/healthz` trên container:
```bash
curl -i http://127.0.0.1:8008/healthz
```
Kết quả phản hồi:
```http
HTTP/1.1 200 OK
date: Thu, 19 Nov 2026 18:12:24 GMT
server: uvicorn
content-type: application/json
x-content-type-options: nosniff
x-frame-options: DENY
x-ratelimit-limit: 60
x-ratelimit-remaining: 59

{"status":"healthy","service":"zero-budget-ai-video-studio-api","timestamp":1795111944.469229,"architecture":"Architecture C (Hybrid WebCodecs)","rendering_location":"in-browser-client-side","cost_per_render":"$0.00"}
```

---

## 7. CÁC VẤN ĐỀ VÀ RỦI RO CÒN LẠI (REMAINING RISKS & NEXT STEPS)

Các vấn đề hạ tầng và bảo mật của Phase 1 đã được giải quyết triệt để. Các vấn đề thuộc Phase 2 và Phase 3 tiếp theo bao gồm:
1. **[Phase 2 Next] Trộn giọng đọc thực tế vào WebCodecs Video:** Cần nạp file audio PCM và đưa vào `AudioEncoder` thay cho procedural synth tone.
2. **[Phase 2 Next] Tải ảnh tư liệu thật lên Canvas:** Cần tích hợp `ctx.drawImage` với hình ảnh từ Wikimedia/Openverse.
3. **[Phase 3 Next] Chia nhỏ văn bản kịch bản cho Edge-TTS:** Cần phân đoạn câu (<250 ký tự) và điều tiết concurrency semaphore để ngăn lỗi websocket `NoAudioReceived`.
4. **[Phase 3 Next] Ghép nối phân đoạn Long-Form:** Cần cơ chế ghép nối file MP4 các chương thành video hoàn chỉnh 15–60 phút.

---

## 8. THÔNG TIN GIT & KẾT LUẬN

* **Branch:** `feature/unified-ai-video-studio`
* **Commit Message:** `fix(phase-1): remediate infrastructure and security`
* **Kiểm tra Secret:** Đã xác minh không có credentials trong git diff.
* **Working tree:** Sạch sẽ (`working tree clean`).
* **Đẩy lên Remote:** `origin/feature/unified-ai-video-studio`.
* **KẾT LUẬN:** **PHASE 1 ĐÃ HOÀN THÀNH VÀ ĐẠT TẤT CẢ TIÊU CHÍ NGHIỆM THU (PASSED).**
