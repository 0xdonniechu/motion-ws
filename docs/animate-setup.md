# Animate engine setup (cth9191/animate)

Tool dựng cảnh procedural: canvas vẽ bằng code → headless Chromium → ffmpeg.
7 style: cut paper, crosshatch, riso, sketchbook, math, pixel, isometric.

## Cài (đã làm trên server 2026-10-27)

```bash
cd ~/tools && git clone https://github.com/cth9191/animate.git
cd animate/plugins/animate/skills/animate
npm i playwright --no-fund --no-audit
npx playwright install chromium
```

`package.json` + `package-lock.json` sinh ra trong clone là file setup local,
không commit vào repo upstream.

## Kiểm tra

```bash
node tools/gallery.mjs /tmp/gallery.png
```

Ra ảnh 8 ô style là engine chạy được.

## Dùng

Skill đọc tại `~/tools/animate/plugins/animate/skills/animate/SKILL.md`.
Luồng: intake → story check → look check → storyboard → build → review.
Piece nằm ở `pieces/<tên>/` trong project dùng nó.
