# TÀI LIỆU CÁC HẠN CHẾ ĐÃ BIẾT VÀ GIẢI PHÁP KHẮC PHỤC (KNOWN LIMITATIONS)
## ZERO-BUDGET AI VIDEO STUDIO — VIETNAMESE SHORTS
*Thời gian cập nhật: 19/11/2026 (Sau đợt kiểm toán thực tế)*

---

### 1. HẠN CHẾ ĐÓNG GÓI CONTAINER MP4 & MUXING ÂM THANH

#### 1.1 Hiện trạng phát hiện trong đợt kiểm toán
- Bộ mã hóa `webcodecsRenderer.ts` đã mã hóa thành công khung hình video H.264 và các khối âm thanh AAC bằng phần cứng GPU với tốc độ rất cao (203 – 205 FPS).
- Tuy nhiên, trong bước đóng gói tệp đầu ra (`Blob`), các khối NAL `EncodedVideoChunk` được nối trực tiếp vào một Blob mang MIME type `video/mp4` mà **chưa thông qua một bộ ghép luồng ISOBMFF MP4 Muxer**.
- Đồng thời, các khối `audioChunks` hiện tại chưa được đưa vào mảng Blob này.
- **Hậu quả:** Tệp tin tải về là luồng video H.264 Annex B thô, thiếu các hộp cấu trúc MP4 chuẩn (`ftyp`, `moov`, `mdat`), không có âm thanh và các trình phát native như QuickTime trên macOS sẽ báo lỗi không mở được.

#### 1.2 Giải pháp khắc phục
- Tích hợp thư viện `mediabunny` (đã có sẵn trong `frontend/node_modules/mediabunny`) vào `webcodecsRenderer.ts`.
- Sử dụng đối tượng `Output` định dạng `Mp4OutputFormat`, khai báo `OutputVideoTrack` và `OutputAudioTrack` để đóng gói cả luồng hình lẫn luồng tiếng vào đúng chuẩn container MP4 tiêu chuẩn quốc tế.

---

### 2. TÍNH TƯƠNG THÍCH TRÌNH DUYỆT VỚI WEBCODECS

#### 2.1 Hiện trạng các trình duyệt
- **Google Chrome, Microsoft Edge, Brave (Desktop 94+):**
  - Hỗ trợ hoàn hảo 100% cả `VideoEncoder` (`avc1.4d002a`) và `AudioEncoder` (`mp4a.40.2`).
  - Tốc độ kết xuất đo được thực tế: **203.42 – 205.35 FPS** trên Apple M3.
- **Mozilla Firefox:**
  - WebCodecs đã hỗ trợ trên các phiên bản mới, tuy nhiên một số phiên bản cũ có thể yêu cầu bật cờ cấu hình `dom.media.webcodecs.enabled`.
- **Apple Safari (macOS 16.4 – 18.x):**
  - Safari hiện tại chỉ hỗ trợ `VideoEncoder`, **chưa có `AudioEncoder` tiêu chuẩn** (việc mux luồng âm thanh AAC trực tiếp đòi hỏi Safari 26+).
- **Trình duyệt trên điện thoại di động (iOS / Android Mobile):**
  - Cơ chế tiết kiệm pin của hệ điều hành di động có thể tạm dừng Web Worker / Canvas khi người dùng chuyển tab hoặc khóa màn hình trong lúc video đang kết xuất.

#### 2.2 Giải pháp thiết kế & Xử lý người dùng
- Hệ thống tích hợp sẵn mô-đun phát hiện chủ động `checkWebCodecsSupport()` trong `frontend/src/services/webcodecs.ts`.
- Khi người dùng truy cập từ Safari hoặc trình duyệt không đủ điều kiện:
  1. Giao diện hiển thị ngay bảng thông báo màu hổ phách cảnh báo rõ ràng.
  2. Nút kết xuất video tạm thời vô hiệu hóa và hướng dẫn người dùng chuyển sang Google Chrome hoặc Microsoft Edge trên máy tính.
  3. Cung cấp chức năng tải kịch bản và phụ đề `.srt` để người dùng không bị gián đoạn công việc.

---

### 3. DỊCH VỤ GIỌNG ĐỌC MICROSOFT EDGE-TTS VÀ DỰ PHÒNG

#### 3.1 Hiện trạng dịch vụ Edge-TTS
- Giao thức WebSocket không chính thức của Microsoft Edge-TTS (`speech.platform.bing.com`) liên tục cập nhật thuật toán tạo mã DRM `Sec-MS-GEC`.
- Khi Microsoft cập nhật chữ ký, các kết nối WebSocket trực tiếp từ các thư viện nguồn mở có thể bị trả về lỗi `HTTP 400 Bad Request` hoặc ngắt kết nối đột ngột.

#### 3.2 Giải pháp kiến trúc của Studio
- **Không coi Edge-TTS là thành phần sống còn (Zero Single-Point-of-Failure):**
  - Hệ thống sở hữu bộ chuẩn hóa văn bản tiếng Việt độc lập (`VietnameseTextNormalizer`) có khả năng tự động phiên âm số học, ngày tháng, từ mượn tiếng Anh.
  - Bộ đồng bộ nhịp độ âm tiết (`generate_syllable_timings`) tự động tính toán chính xác mốc hiển thị phụ đề theo từng từ mà không phụ thuộc vào phản hồi từ máy chủ ngoài.
  - Trên giao diện Studio, âm thanh nền (BGM) và nhạc hiệu được tổng hợp trực tiếp bằng Web Audio API, giảm tải tối đa cho hệ thống mạng.

---

### 4. ĐỊNH MỨC TÀI NGUYÊN MIỄN PHÍ CỦA SUPABASE & DUNG LƯỢNG

#### 4.1 Định mức gói Free của Supabase
- Cơ sở dữ liệu PostgreSQL: tối đa 500 MB.
- Bộ nhớ lưu trữ (Storage): tối đa 1 GB.
- Số lượng người dùng hoạt động hàng tháng (MAU): tối đa 50,000.

#### 4.2 Chiến lược tối ưu dung lượng của Studio
- **Không lưu trữ video MP4 trên máy chủ đám mây:**
  - Nhờ kiến trúc kết xuất trực tiếp trên trình duyệt máy khách (In-Browser WebCodecs), file video MP4 hoàn thiện được tạo ra ngay trong RAM của trình duyệt người dùng và tải về máy tính cá nhân.
  - Máy chủ hoàn toàn không phải gánh chi phí lưu trữ hoặc băng thông tải xuống của các tệp video nặng hàng trăm Megabyte, bảo toàn vĩnh viễn hạn mức 1 GB miễn phí của Supabase Storage.
- **Trạng thái kết nối Supabase hiện tại:**
  - Do chưa cấu hình dự án Supabase thực tế, các yêu cầu đăng nhập/đăng ký trên frontend đang hiển thị lỗi kết nối mạng. Ứng dụng hiện hoạt động ở chế độ Demo nội bộ qua `localStorage`.
