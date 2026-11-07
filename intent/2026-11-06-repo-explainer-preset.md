---
status: approved   # chủ duyệt 2026-11-06; thu hẹp phạm vi cùng ngày: chỉ teardown + lưu preset, chưa dựng
---

# Preset repo-explainer (thẻ GitHub + minh hoạ SVG phẳng): teardown và lưu preset

Ticket: Plane MWS-9. Mẫu đầu: `jobs/repo-sample-7704833646468844807/` (`NOTES.md`, `beats.json`, `template_timing.json`).

**Problem** — Kênh @tongtaiai.com làm clip giải thích repo/công cụ AI bằng một vibe riêng: mỗi beat ~7s là một trang cố định (pill chủ đề + `n/14` + tiêu đề serif hai tông + phụ đề + MỘT thẻ + chân trang thương hiệu), thẻ chỉ có hai loại: trang GitHub (README, bảng, lệnh, panel repo, vệt tô vàng) và ảnh minh hoạ tình huống (ở clip gốc là ảnh đất sét 3D có nhân vật). Chủ xác nhận 2026-11-06 đây KHÔNG phải corporate-motion. Repo chưa có preset cho nó, và mới đo 1 clip (n=1) nên chưa tách được token nào là vibe, token nào là nội dung. Cần lưu thành preset để clip mới về repo/công cụ khác giữ đúng vibe này.

**Outcome** — Xong khi cả hai đều đạt, theo thứ tự (lưu preset SAU khi đo xong):
1. **Số đo n≥3**: thêm ≥2 clip cùng kênh, khác chủ đề, mỗi clip một thư mục `jobs/repo-sample-<id>/` có `beats.json` + `template_timing.json`. Đo thêm những gì hiện chỉ đọc bằng mắt: vệt tô vàng, cuộn trong thẻ GitHub, đường cong thẻ vào, chân trang/pill hồi lại, wipe tiêu đề ở nhiều beat (hiện chỉ đo 1 beat).
2. **Preset lưu ở mức đặc tả** tại `presets/repo-explainer/`, không có mã dựng:
   - `style.json`: mỗi token có giá trị từng clip, trung vị, khoảng, `n`, `tier` (CORE khi ≥3 clip, OPTIONAL khi 1–2), `disagree`; khối `build_defaults` chọn MỘT giá trị cho mỗi token, cái không đo được ghi "đoán".
   - `language.json` (chuyển động cố định: ra/nghỉ/vào theo khung, wipe, ease, chân trang hồi lại), `themes/default.json` (màu, font, kiểu chữ), `layouts.json` (ô thẻ, lề, vị trí pill/số/chân trang).
   - `kit/catalog.json`: từ vựng dạng **mô tả** (component, effect, transition: tên, công dụng, prop, nguồn số đo), mỗi mục `status: "spec"`; không `kit.js`, không demo.
   - `preset.md`: khi dùng / không dùng, khung beat, giá trị dựng mặc định, token CORE/OPTIONAL, trạng thái. Có bảng đối chiếu **6/6 tình huống minh hoạ** của clip gốc (hoá đơn dồn lên, chồng trình duyệt đổ, quá tải, động cơ nặng không cần, đàn tác tử chạy mượt, câu hỏi kết) → cách diễn đạt bằng cảnh SVG phẳng có chuyển động, cùng ý, không chép hình. Đó là cách giữ "không thiếu cách diễn đạt" khi bỏ ảnh đất sét.
   - Dòng mới trong `presets/README.md` (bảng + luật matching).
   Kiểm: các JSON hợp lệ; mọi token có đủ giá trị theo số clip và `tier` đúng luật n; bảng 6/6 đủ; README có dòng mới; phông ghi rõ "chờ chủ duyệt" cho tới khi chủ duyệt.

**Constraints** — Đo trước, ghi đo/đọc bằng mắt/đoán riêng; không bịa số, không đổi ngưỡng âm thầm. Không chép asset gốc (ảnh, ảnh chụp README, logo) vào repo. Tiếng Việt; phông phải có subset Việt và qua `font_check`, **phông chờ chủ duyệt**. Không audio. **Không nhân vật đất sét, không ảnh AI sinh kiểu 3D, không mascot Q-version vẽ bằng code** (chủ quyết 2026-11-06; skill huashu-art-motion cũng xếp mascot vẽ code vào "AI slop"). Thẻ GitHub về sau dựng từ văn bản công khai theo giao diện GitHub-like, không ảnh chụp, không logo. Không dùng `presets/_shared/character-prompt.json` (style Spider-Verse). Lệnh đo nặng chạy dưới `systemd-run --user --scope -p MemoryMax=<N>G`. Độ khó: `measure_*.py` MEDIUM (builder làm, reviewer độc lập duyệt), tài liệu/JSON preset EASY; không đụng `server.js`, `jobs/jobs.json`, `SPEC.md`/`joins.json` của job đã duyệt. Git: nhánh `0xdonniechu/<slug>`, mỗi mục một PR, không merge khi chưa được bảo.

**Out of scope** — Mọi việc dựng, chủ chưa yêu cầu (2026-11-06): `kit.js`/`kit.css`, thư viện bộ phận SVG và công thức cảnh, thẻ demo, đoạn thử 3 beat, clip đầy đủ, lệnh mỏng `/repo-explainer`. Làm bằng intent riêng khi chủ bảo dựng. Dựng lại khung-từng-khung clip Lightpanda. Audio. Ảnh đất sét, ảnh AI sinh, 3D. Sửa preset corporate-motion. Preset cho kênh hoặc phong cách khác.

**Quyết định đã chốt (2026-11-06)**
1. Minh hoạ: không đất sét/AI 3D, nhưng không được thiếu cách diễn đạt → ghi thành cách diễn đạt SVG phẳng có chuyển động trong `preset.md` (bảng 6/6); dựng thật để sau.
2. Phạm vi: chỉ teardown + lưu preset; chưa dựng. Lưu preset khi đo xong (chủ chọn 2026-11-06).
3. Link ≥2 clip @tongtaiai.com khác chủ đề: chủ đồng ý, sẽ gửi.
4. Phông: tôi nêu ứng viên sau `font_check`, chủ duyệt.
5. Tên preset `repo-explainer`; thư mục mẫu đã đổi thành `repo-sample-7704833646468844807`.
6. Ticket: chủ cho phép tôi tự tạo → MWS-9.

**Open questions** — Không chặn plan: (a) link ≥2 clip chưa tới tay; thiếu thì Outcome 1 không đóng được, tôi dừng và hỏi chủ chứ không tự lưu preset với n=1. (b) Duyệt phông, ở cổng riêng trong plan.
