# Video Workspace — intent

**Problem** — Mỗi lần dựng lại 1 video tham chiếu phải làm tay: tải video, cắt frames, ghi chú, rồi mở HyperFrames riêng. Không có chỗ theo dõi job.

**Outcome** — Dán URL bất kỳ vào workspace: tự tải video, probe, tách frames, làm contact sheet, job hiện trên kanban. Tab Explorer duyệt file cây thư mục, xem trước mp4/ảnh. Render vẫn làm trong session riêng rồi gắn output vào job.

**Constraints** — Chạy local trên server Linux, xem từ Mac qua SSH forward. Không thêm dependency (Node thuần + ffmpeg + yt-dlp có sẵn). Không auth (1 user).

**Out of scope** — Tự động phân tích nội dung bằng AI, tự render HyperFrames từ job, voice-over trong app. Các bước đó làm trong session rồi gắn kết quả vào job.

**Quyết định** — Bán tự động (owner 2026-10-27): ingest + phân tích xong chờ duyệt. Nút Duyệt render tạo khung HyperFrames trong job, session dựng scene, gắn output rồi Xong.
**Quyết định** — Sync Plane MWS (owner 2026-10-27): ingest xong tự tạo ticket Todo, duyệt → In Progress, xong → Done, hủy → Cancelled. Ticket lưu ở job.plane. Không test framework trong repo (xác minh bằng probe sống vì cần secret + mạng thật).
