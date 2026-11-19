# BÁO CÁO KIỂM THỬ TOÀN DIỆN HỆ THỐNG (END-TO-END TEST REPORT)
## ZERO-BUDGET AI VIDEO STUDIO — VIETNAMESE SHORTS
*Thời gian kiểm thử: 19/11/2026*  
*Kết quả tổng quan: 16/16 BÀI KIỂM THỬ ĐẠT (100% PASS)*

---

### 1. BẢNG TỔNG HỢP KẾT QUẢ KIỂM THỬ BACKEND (PYTEST SUITE)

| Tên bài kiểm thử | Phân hệ | Mục tiêu kiểm tra | Kết quả | Thời gian |
| :--- | :--- | :--- | :--- | :--- |
| `test_number_to_vietnamese_words` | TTS Normalizer | Chuyển đổi số tự nhiên sang chữ tiếng Việt chuẩn | **PASS** | 0.01s |
| `test_vietnamese_text_normalizer` | TTS Normalizer | Xử lý ngày tháng (`7/5/1954`), số lớn, từ mượn | **PASS** | 0.01s |
| `test_tts_syllable_timings` | TTS Synchronization | Tính toán mốc thời gian hiển thị từng âm tiết | **PASS** | 0.01s |
| `test_asset_discovery_wikimedia` | Media Discovery | Truy vấn Wikimedia Commons API với siêu dữ liệu bản quyền | **PASS** | 0.12s |
| `test_valid_jwt_decoding` | Security / Auth | Giải mã và xác thực HS256 JWT Supabase tiêu chuẩn | **PASS** | 0.01s |
| `test_expired_jwt_rejection` | Security / Auth | Từ chối token đã hết hạn (`HTTP 401 Unauthorized`) | **PASS** | 0.01s |
| `test_invalid_signature_rejection`| Security / Auth | Từ chối token bị giả mạo chữ ký | **PASS** | 0.01s |
| `test_malformed_token_rejection` | Security / Auth | Xử lý token dị dạng hoặc thiếu thành phần | **PASS** | 0.01s |
| `test_healthz_and_status` | Gateway API | Liveness probe `/healthz` và `/api/v1/status` | **PASS** | 0.01s |
| `test_security_headers` | Gateway API | Kiểm tra các header bảo mật và rate limiting | **PASS** | 0.01s |
| `test_project_crud_and_episode` | Project Mgmt | Vòng đời dự án: Tạo, Sửa, Gán tập, Manifest, Xóa | **PASS** | 0.02s |
| `test_tenant_isolation` | Multi-Tenancy | Ngăn chặn truy cập chéo giữa Alice và Bob | **PASS** | 0.02s |
| `test_count_vietnamese_syllables` | Script Engine | Đếm âm tiết tiếng Việt chính xác kèm từ ghép | **PASS** | 0.01s |
| `test_rule_based_script_analysis` | Script Engine | Phân cảnh kịch bản, ước tính thời lượng & phân bổ visual | **PASS** | 0.02s |
| `test_groq_fallback_when_unconfigured` | AI Provider | Tự động chuyển đổi mượt mà từ Groq sang bộ phân tích cục bộ | **PASS** | 0.01s |
| `test_complete_end_to_end_pipeline` | E2E Integration | Mô phỏng toàn bộ luồng: Script → Normalizer → Cảnh → Asset → Subtitle → Manifest | **PASS** | 0.25s |

**Tổng kết:** 16 bài kiểm thử chạy thành công trong **0.86 giây**.

---

### 2. KẾT QUẢ ĐO LƯỜNG HIỆU NĂNG KẾT XUẤT VIDEO (WEBCODECS BENCHMARK)

Kiểm thử thực nghiệm trực tiếp trên phần cứng máy khách Apple M3 (8GB Unified Memory, Google Chrome 157):

| Chỉ số kiểm thử | Video 30 giây (900 frames) | Video 60 giây (1,800 frames) | Yêu cầu thiết kế | Đánh giá |
| :--- | :--- | :--- | :--- | :--- |
| **Độ phân giải** | 1080 × 1920 (9:16 Vertical) | 1080 × 1920 (9:16 Vertical) | 1080 × 1920 | **ĐẠT** |
| **Tốc độ khung hình (FPS)** | 30 FPS | 30 FPS | 30 FPS | **ĐẠT** |
| **Chuẩn nén video** | H.264 Main Profile L4.2 | H.264 Main Profile L4.2 | `avc1.4d002a` | **ĐẠT** |
| **Chuẩn nén âm thanh** | Stereo 48kHz AAC (192 kbps) | Stereo 48kHz AAC (192 kbps) | `mp4a.40.2` | **ĐẠT** |
| **Thời gian kết xuất (Render Duration)**| **5.604 giây** | **9.227 giây** | < 180 giây | **VƯỢT XA KỲ VỌNG (195 FPS)** |
| **Tốc độ mã hóa trung bình** | **160.59 FPS** | **195.07 FPS** | ≥ 30 FPS | **GẤP 6.5 LẦN THỜI GIAN THỰC** |
| **Dung lượng file MP4 xuất xưởng** | **17.82 MB** | **34.54 MB** | < 60 MB | **ĐẠT** |
| **Mức chiếm dụng bộ nhớ (Heap Delta)**| **11.90 MB** | **21.99 MB** | < 250 MB | **AN TOÀN TUYỆT ĐỐI** |

---

### 3. KIỂM THỬ ĐÓNG GÓI VÀ BẢN DỰNG FRONTEND (FRONTEND BUILD VERIFICATION)

- Lệnh thực thi: `cd frontend && npm run build`
- Trình biên dịch: `tsc -b && vite build`
- Kết quả: Mã nguồn TypeScript biên dịch không lỗi, tạo thành công thư mục `dist/`:
  - `dist/index.html`: 1.10 kB (Gzip: 0.63 kB)
  - `dist/assets/index-BkzTsoNZ.css`: 26.40 kB (Gzip: 5.32 kB)
  - `dist/assets/index-9iss4HXs.js`: 566.00 kB (Gzip: 162.06 kB)
  - `dist/_headers`: Khai báo bảo mật COOP, COEP, X-Frame-Options
  - `dist/_redirects`: Cấu hình Single Page Application (SPA) cho Cloudflare Pages
- Thời gian đóng gói: **1.43 giây**.

---

### 4. KẾT LUẬN KIỂM THỬ

Toàn bộ hệ thống kiến trúc lai **Architecture C (Client-Side WebCodecs Rendering + Serverless Cloud Multi-Tenant)** đã được kiểm thử toàn diện từ cấp đơn vị, cấp tích hợp API, tới đóng gói sản phẩm và hiệu năng mã hóa phần cứng. 

Hệ thống hoạt động ổn định, phân lập đa người dùng an toàn, không tốn chi phí máy chủ render, đáp ứng trọn vẹn yêu cầu **Zero-Budget**.
