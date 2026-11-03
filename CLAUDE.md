# motion-ws: teardown clip motion → remake → preset phong cách dùng lại

## What it does
Phân rã clip motion graphic (TikTok, 9:16), dựng lại bằng HyperFrames + GSAP theo số đo từng khung, rồi rút thành preset phong cách để clip mới với nội dung khác vẫn giữ cùng vibe. Mục tiêu sau cùng là tính nhất quán phong cách, không phải sao chép. Không làm audio cho tới khi chủ yêu cầu. Lỗi tốn: mất job/render đã duyệt, hoặc preset sai làm lệch mọi clip sau.

## Verify
- Server: `node --check server.js`
- Mỗi scene đã đổi: `npx -y hyperframes@latest check` trong thư mục scene (0 errors)
- Job remake (sau render `.mov`): `bash jobs/<id>/compose.sh` rồi `uvx --with numpy python -I -B jobs/<id>/motion.py` (tỉ lệ ≥0.80, không cửa sổ 0.2s <0.50); ảnh nối `preview/joins/`; render lại 2 lần phải trùng framemd5
- Render nặng: `systemd-run --user --scope -p MemoryMax=16G npx -y hyperframes@latest render --format mov`
- Chỉ chủ làm được: chấm clip bằng mắt (`compare.mp4` qua Tailscale). Khi chủ đã chấm đạt, mỗi mục chỉ làm một lượt rồi báo, không ép mọi scene qua cổng.

## HARD: the main session does it directly, then hard-reviewer
- `server.js` ghi `jobs/jobs.json`; xoá job hoặc render
- Đổi `SPEC.md`, `joins.json` hay ngưỡng cổng của job đã duyệt

## MEDIUM: builder builds, reviewer reviews
- Dựng/sửa scene, preset, `shared/*.js` (kit), script đo `measure_*.py`, `compose.sh`/`motion.py`, `templates/`

## EASY: transcriber or builder, no review
- Tài liệu, chữ, đổi tên, sửa một dòng hiển nhiên

## Rules
- Mỗi preset = ngôn ngữ chuyển động cố định (`language.json`) + theme thay được (`themes/*.json`) + bộ từ vựng riêng (`kit/catalog.json`: component, effect, transition). Scene chỉ gọi tên trong catalog; thiếu thì thêm vào kit trước rồi mới dùng.
- Đo trước khi dựng (quỹ đạo 30fps); không bịa chuyển động để qua cổng. Không đổi ngưỡng cổng âm thầm.
- Không `Math.random`/rAF trong scene; mọi thứ là hàm của thời gian timeline.
- Render, `preview/`, `source.*` không commit (`.gitignore`).
- Git: tài khoản `0xdonniechu`, nhánh `0xdonniechu/<slug>`, mỗi mục một PR, không merge khi chưa được bảo.
- Tracker: Plane project `MWS`, viết tiếng Việt.

## Read when
- Teardown/remake clip mới: `docs/teardown-process.md` và `templates/teardown/README.md`
- Chọn preset: `presets/README.md`
- Kiến trúc server/job: `docs/architecture.md`

## Session state
- Work in progress lives in `HANDOFF.md` (gitignored). If it exists at session start, read it before anything else. Update it with `/handoff` before `/clear`; delete it once the goal is finished and recorded.
- Durable facts go in this file; tasks in the tracker. `HANDOFF.md` holds only where the current goal stands.
