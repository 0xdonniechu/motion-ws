# motion-ws

Phân rã clip motion graphic (TikTok, 9:16), dựng lại bằng HyperFrames + GSAP theo số đo từng khung,
rồi rút thành **preset phong cách** để clip mới với nội dung khác vẫn giữ cùng vibe. Mục tiêu là
tính nhất quán phong cách, không phải sao chép từng clip. Xem đầy đủ luật làm việc ở [CLAUDE.md](CLAUDE.md).

## Cài trên máy mới (bắt buộc trước khi dùng `/corporate-motion` hay teardown)

```
git clone https://github.com/0xdonniechu/motion-ws.git
```

Cần có sẵn trên máy:

- **Node.js, ffmpeg, Python** (chạy qua `uv`/`uvx`, không cần cài gói riêng).
- **Mạng ra ngoài**: `npx -y hyperframes@latest` tải gói lúc chạy; `yt-dlp` (qua `uvx`) tải clip nguồn.
- **Danh tính git + GitHub**: `git config user.name/email` theo tài khoản `0xdonniechu`; `gh auth` đăng nhập
  đúng tài khoản đó nếu muốn mở PR.
- **Plane (tùy chọn)**: cần `PLANE_API_KEY` trong cấu hình MCP của máy đó để tự cập nhật ticket project `MWS`;
  không có vẫn làm việc bình thường, chỉ không ghi ticket được.
- **Chỉ trên Linux/systemd**: lệnh render nặng dùng
  `systemd-run --user --scope -p MemoryMax=16G npx -y hyperframes@latest render`
  để giới hạn RAM. Máy không có `systemd` (macOS, Windows) thì bỏ phần `systemd-run ...` hoặc thay
  bằng cách giới hạn RAM khác của hệ đó.

Mọi job, preset và kit nằm trong repo (trừ file render và `source.mp4`, bị `.gitignore` vì tái tạo được
bằng cách tải lại/render lại), nên clone xong là có đủ tiến độ, không mất gì khi đổi máy.

## Dùng ngay

- **Dựng clip mới theo phong cách đã có**: gõ `/corporate-motion [--theme <tên>] <nội dung>` trong Claude
  Code mở ở repo này (lệnh nằm ở `.claude/skills/corporate-motion/`, tự có khi mở repo). Xem
  [presets/corporate-motion/preset.md](presets/corporate-motion/preset.md).
- **Teardown một clip mới**: xem [docs/teardown-process.md](docs/teardown-process.md), bắt đầu bằng
  `cp -r templates/teardown jobs/<ngày>-<tên>`.
- **Chọn preset có sẵn**: xem [presets/README.md](presets/README.md).

## Kiến trúc

Xem [docs/architecture.md](docs/architecture.md).
