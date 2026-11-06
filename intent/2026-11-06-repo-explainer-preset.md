---
status: approved   # chủ duyệt 2026-11-06: trả lời câu mở + "cứ làm đi"
---

# Preset repo-explainer (thẻ GitHub + minh hoạ SVG phẳng)

Ticket: Plane MWS-9. Mẫu đầu: `jobs/repo-sample-7704833646468844807/` (`NOTES.md`, `beats.json`, `template_timing.json`).

**Problem** — Kênh @tongtaiai.com làm clip giải thích repo/công cụ AI bằng một vibe riêng: mỗi beat ~7s là một trang cố định (pill chủ đề + `n/14` + tiêu đề serif hai tông + phụ đề + MỘT thẻ + chân trang thương hiệu), thẻ chỉ có hai loại: trang GitHub (README, bảng, lệnh, panel repo, vệt tô vàng) và ảnh minh hoạ tình huống (ở clip gốc là ảnh đất sét 3D có nhân vật). Chủ xác nhận 2026-11-06 đây KHÔNG phải corporate-motion. Repo chưa có preset cho nó, và mới đo 1 clip (n=1) nên chưa tách được token nào là vibe, token nào là nội dung. Muốn clip mới về repo/công cụ khác vẫn giữ đúng vibe này.

**Outcome** — Xong khi cả ba đều đạt:
1. **Số đo n≥3**: thêm ≥2 clip cùng kênh, khác chủ đề, mỗi clip có `beats.json` + `template_timing.json`; `style.json` gộp các clip, mỗi token ghi CORE (≥3 clip) hay OPTIONAL và `disagree`. Đo thêm (hiện chỉ đọc bằng mắt): vệt tô vàng, cuộn trong thẻ GitHub, đường cong thẻ vào, chân trang/pill hồi lại, wipe tiêu đề ở nhiều beat (hiện n=1 beat).
2. **Preset** `presets/repo-explainer/`: `preset.md`, `language.json` (chuyển động cố định), `themes/default.json`, `layouts.json` (ô thẻ, lề, vị trí pill/số/chân trang), `kit/catalog.json` + `kit.js` + thẻ demo từng mục (component, effect, transition; mỗi mục có API và demo), dòng mới trong `presets/README.md` (bảng + luật matching). Hai loại thẻ:
   - **Thẻ GitHub**: HTML dựng từ văn bản công khai theo giao diện GitHub-like; không ảnh chụp, không logo.
   - **Thẻ cảnh minh hoạ**: SVG tự vẽ, hình khối phẳng, ghép từ một thư viện bộ phận (vật, ký hiệu, đồ thị, hình người phẳng tối giản nếu cần), CÓ chuyển động (xếp chồng, đổ, đếm, tràn, đo). Không thiếu cách diễn đạt: 6 tình huống minh hoạ của clip gốc (hoá đơn dồn lên, chồng trình duyệt đổ, quá tải, động cơ nặng không cần, đàn tác tử chạy mượt, câu hỏi kết) đều có công thức cảnh diễn đạt cùng ý (không chép hình), kiểm bằng bảng đối chiếu 6/6.
3. **Đoạn thử 3 beat** (chủ đề KHÁC Lightpanda, chỉ gọi tên trong catalog, gồm ≥1 thẻ GitHub và ≥1 thẻ cảnh minh hoạ ghép từ thư viện bộ phận): `hyperframes check` 0 errors; không có ảnh raster trong scene (kiểm bằng lệnh); render 2 lần trùng framemd5; thời điểm vào/ra beat đo bằng `measure_beat_*.py` trên đoạn render lệch ≤1 khung so với trung vị trong `style.json`; chủ chấm bằng mắt (`compare.mp4` qua Tailscale), việc chỉ chủ làm được.

**Constraints** — HyperFrames + GSAP, mỗi scene một timeline paused, không `Math.random`/rAF, mọi thứ là hàm của thời gian. Đo trước khi dựng, không bịa chuyển động, không đổi ngưỡng cổng âm thầm. Không chép asset gốc (ảnh, ảnh chụp README, logo) vào preset hay scene. Tiếng Việt; phông phải có subset Việt và qua `font_check`, **phông chờ chủ duyệt**. Không audio. **Không nhân vật đất sét, không ảnh AI sinh kiểu 3D, không mascot Q-version vẽ bằng code** (chủ quyết 2026-11-06; skill huashu-art-motion cũng xếp mascot vẽ code vào "AI slop"). **Rủi ro đã biết**: cảnh minh hoạ vẽ bằng code dễ ra vẻ rẻ tiền, nên plan đặt cổng thử một cảnh mẫu cho chủ duyệt vibe TRƯỚC khi dựng cả thư viện. Không dùng `presets/_shared/character-prompt.json` (style Spider-Verse). Render nặng dưới `systemd-run --user --scope -p MemoryMax=16G`. Độ khó: MEDIUM (kit, `measure_*.py`, scene, preset) nên builder làm, reviewer độc lập duyệt; không đụng `server.js`, `jobs/jobs.json`, `SPEC.md`/`joins.json` của job đã duyệt. Git: nhánh `0xdonniechu/<slug>`, mỗi mục một PR, không merge khi chưa được bảo. Không phải sản phẩm mới nên không có đường kiếm tiền; giá trị là tính nhất quán phong cách cho clip mới.

**Out of scope** — Dựng lại khung-từng-khung clip Lightpanda (không chạy cổng `motion.py` tỉ lệ ≥0.80). Audio (lời đọc, nhạc). Clip đầy đủ 14 beat và lệnh mỏng `/repo-explainer` (skill + `build-clip.mjs` + schema): intent riêng sau khi chủ duyệt đoạn thử. Ảnh đất sét, ảnh AI sinh, 3D: bỏ hẳn, không làm ô nhận ảnh. Sửa preset corporate-motion. Preset cho kênh hoặc phong cách khác.

**Quyết định đã chốt (2026-11-06)**
1. Minh hoạ: không đất sét/AI 3D, nhưng không được thiếu cách diễn đạt → thẻ cảnh minh hoạ SVG phẳng có chuyển động (Outcome 2).
2. Link ≥2 clip @tongtaiai.com khác chủ đề: chủ đồng ý, sẽ gửi.
3. Phông: tôi nêu ứng viên sau `font_check`, chủ duyệt (cổng trong plan).
4. Tên preset `repo-explainer`; thư mục mẫu đã đổi thành `repo-sample-7704833646468844807`.
5. Ticket: chủ cho phép tôi tự tạo → MWS-9.

**Open questions** — Không chặn plan: (a) link ≥2 clip chưa tới tay; Outcome 1 chỉ đóng được khi có; thiếu thì dừng ở n=1, `style.json` toàn OPTIONAL, không tuyên bố CORE. (b) Duyệt phông, ở cổng riêng trong plan.
