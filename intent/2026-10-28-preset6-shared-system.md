---
status: shipped
---

# Preset 6 continuous-canvas + shared system

**Problem** — Nhiều video là một bức tranh lớn, mỗi scene chỉ là cửa sổ camera
(prezi-style, infinite canvas). 5 preset hiện tại giả định shot độc lập nên
không distill được loại này. Thiếu vocab chuyển động/camera chung, teardown
thiếu cột transition + bản đồ không gian, review thiếu assertions theo preset.

**Outcome** — Xong khi: (1) preset `continuous-canvas` có preset.md + template
chạy được (HyperFrames check pass, snapshot 3 vùng + camera move); (2) vocab
chung `presets/_shared/motion-vocab.md` (entrances, transitions, camera, duration
tokens); (3) `presets/_shared/teardown-template.md` (shots + transition + spatial
map); (4) `presets/_shared/review-checklist.md` (checklist tay global + riêng
từng preset); (5) README cập nhật luật matching. Tiêu chí: check pass mọi
template mới/sửa, snapshot đối chiếu, commit + push main.

**Constraints** — Không thêm dependency. Template phải pass `hyperframes check`.
Tiếng Việt. Không đụng server.js (không đổi runtime), chỉ thêm presets/ + docs.

**Out of scope** — Assertions tự động trong pipeline. TTS/voice. ComfyUI.
Auto-classify preset (director vẫn gán tay).

**Open questions** — (trống = sẵn sàng duyệt)
