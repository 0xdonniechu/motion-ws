# Plan — preset 6 + shared system

## Files (theo thứ tự)

1. `presets/_shared/motion-vocab.md` — entrances, transitions catalog, camera moves, duration tokens.
2. `presets/_shared/teardown-template.md` — shots + transition + spatial map + câu hỏi.
3. `presets/_shared/review-checklist.md` — global + assertions riêng từng preset (tay).
4. `presets/continuous-canvas/preset.md` — khi dùng, biến, engine, nhịp.
5. `presets/continuous-canvas/template/{index.html,hyperframes.json,gsap.min.js}` — world 2400x1200, 3 vùng, camera pan/zoom, 12s, 1280x720 output.
6. `presets/README.md` — thêm preset 6 + luật matching.
7. `intent/2026-10-28-preset6-shared-system.md` — status → shipped khi xong.

## Risks

- Camera transform sai luật seek-safe (tween top/left thay vì x/scale) → bắt bằng `hyperframes check` + đọc lại keyframes skill trước khi viết template.
- Template viewport 1280x720 chứa world 2400x1200: text vùng zoom sâu vỡ floor → cỡ chữ tính theo zoom sâu nhất, check contrast báo.
- Label đè khi pan (kinh nghiệm vòng 2) → snapshot 3 vùng + 2 mốc camera, xem mắt.

## Proof

- `hyperframes check` pass cho template continuous-canvas (ghi output).
- Snapshot 4 mốc (3 vùng + 1 giữa camera move) mở xem: vùng rõ chữ, move mượt, không đen.
- `git log --oneline -3` có intent + plan + build commits, push main thành công.
- Review checklist chạy 1 lượt trên template mới, tick đủ mục.
