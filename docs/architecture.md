# Kiến trúc motion-ws — distill mọi video

Mục tiêu: dán URL bất kỳ vào, ra bản dựng lại được. Engine nào cũng cắm
được, tool/skill/MCP nạp theo shot. Sơ đồ trực quan:
`.archify/architecture-motion-ws-20261028-110720/motion-ws.html` (mở bằng browser).

## 5 tầng

1. **Ingest** (`server.js:runIngest`, `buildAnalysis`) — `uvx yt-dlp` tải video,
   ffprobe + ffmpeg tách frames + contact sheet, Whisper transcript.
   Mỗi job một folder `jobs/<id>/`: `source.mp4`, `frames/`, `contact-sheet.jpg`,
   `analysis/`, `rebuild/`, `preview/`.
2. **Understand** — teardown ra `analysis/shots.md` + spec sạch, không chép asset gốc.
3. **Plan (director)** — agent đọc spec, chẻ shot, chọn engine cho từng shot.
   Quy tắc hiện tại: chữ động → HyperFrames, vẽ procedural → animate skill,
   isometric → anatomy, ảnh→vẽ tay → whiteboard-animation-vi, asset → ComfyUI.
4. **Build (engine adapters)** — mỗi engine một adapter: nhận shot-spec, trả
   preview PNG rồi MP4. Thêm engine = thêm adapter + đăng ký capability,
   không sửa core. Nạp lazy theo shot, ghi vào manifest để tái tạo.
5. **Review** — contact card gốc-remake (`preview/compare.jpg`), check tự động
   (hyperframes check, animate review), gate duyệt → render final → đóng ticket.

## Gate bán tự động

`todo` (ingest xong) → **Duyệt** → `processing` (khung render trong job) →
`done` + output. Plane MWS mirror mọi chuyển đổi (`planeSync`).

## Trạng thái engine (2026-10-28)

Có: HyperFrames, animate skill, anatomy, ffmpeg + Whisper, whiteboard (đang cài).
Thiếu: ComfyUI, TTS voice-over, capability registry (hiện chọn tay).

## Quyết định đã chốt

Xem `intent/2026-10-27-video-workspace.md`.
