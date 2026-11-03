# Kịch bản: "Vì sao dashboard đẹp mà không ai quyết gì"

Clip chứng minh preset `corporate-motion` mang được vibe sang nội dung MỚI. 9:16, 1080x1920, 30fps, **41.0s**, không âm thanh, không giọng đọc: chữ trên màn hình mang thông điệp (tiếng Việt đủ dấu).
Kịch bản tự viết, theo khung beat của preset (`style.json` → `beat_formula`). Chủ đề gần nhất với một clip của kênh là `jobs/corp-sample-7702801642646899989` ("Dashboard 2 tuần không ai mở", một trong 4 clip nguồn của preset); lời văn, ẩn dụ (bản đồ), số và thứ tự beat ở đây là nguyên bản, không chép hay diễn đạt lại clip đó. Chỉ mockup UI tự vẽ trong kit, không logo hãng, không ảnh chụp màn hình thật.
Mọi con số là **số minh hoạ** (beat 2 và 6 có nhãn "Số minh hoạ"). Cỡ chữ, nhịp gõ (21.3 ký tự/s) và thời gian đứng yên của tiêu đề lấy từ `language.json`.
Scene viết thuần lời gọi từ vựng `kit/catalog.json` (`Kit.make`, `Kit.fx`, `Kit.tx`): không vẽ riêng trong scene.

| # | Giây | Beat | Chữ trên màn hình | Component (catalog) | Chuyển ra |
|---|------|------|-------------------|---------------------|-----------|
| 1 | 0–4.0 | wow demo | gõ: "Dashboard *đẹp* như phim." | `dashboardCard` (KPI 87% đếm theo thanh chạy, 6 cột nảy), `text` | wash |
| 2 | 4.0–8.0 | số treo | "Dashboard họp tuần có **47** biểu đồ." / "Mấy cái *đổi được* một quyết định?" | `statCard` (số, vạch vàng, thanh chạy), `text` | bar-wipe |
| 3 | 8.0–12.0 | câu chốt phổ quát | "Ai làm dữ liệu lâu cũng nhận ra:" / "Không cần thêm biểu đồ." / gõ "Họ cần một *câu trả lời*." | `quoteCard` | dissolve |
| 4 | 12–17 | ẩn dụ | gõ "Bản đồ *chi tiết* đến từng ngõ," / "mà không ghi *điểm đến*." | `mapCard` (9 ghim nảy), `iconCard` (dấu hỏi "điểm đến?"), `text` | hard |
| 5 | 17–25 | checklist | pill "CÂU 1/3" → "2/3" → "3/3"; "Quyết định nào cần *chốt*?", "*Ai* là người chốt?", "Con số nào *đổi được* hành động?" | `pill` + `pillHop`, 3× `listCard` + `popIn` tick | dissolve |
| 6 | 25–30 | chi tiết đắt | "Mỗi quý, làm báo cáo mất **72** giờ." / "mà không ai dùng để *quyết*." | `statCard` với `chart` (12 cột tuần, 6 giờ/tuần), `text` | flash |
| 7 | 30–35 | bài học | gõ "Chốt *quyết định* trước. Vẽ biểu đồ sau." / Quyết định → Câu hỏi → Biểu đồ | 3× `stepCard`, 2× `connector` | dissolve |
| 8 | 35–41 | CTA, quay về số treo | "Trong 47 biểu đồ, giữ lại **1** con số." / "Bạn sẽ giữ *con số* nào?" / nút "Lưu lại" | `statCard` (số đếm 47 → 1), `button` + `pulse` | kết (giữ 2s) |

Nền: tint ở 1, 3, 4, 6, 7; trắng ở 2, 5, 8. Vàng chỉ là vạch nhỏ ở beat 2, 6, 8.

## Đã dựng

- `trial/` beat 1–3 (12.0s) và `full/` cả 8 beat (41.0s, 1230 khung): `index.html` chỉ gồm vỏ cảnh (`clip`) và lời gọi catalog; `kit` và `tokens.js` là symlink tới `presets/corporate-motion/kit/`. Beat 1–3 của `full/` giữ nguyên thời gian của `trial/` (321 khung đầu trùng byte với `trial-r1.mp4`; khung sau lệch do bộ mã hoá nhìn trước cảnh mới).
- `trial-night/`: `index.html` là bản sao nguyên văn của `trial/index.html` (`verify.sh` chạy `cmp`); chỉ `tokens.js` trỏ tới theme `night` (nền navy, nhấn xanh ngọc, Montserrat, từ khoá có vạch nền, nhãn viết hoa; bo góc và bóng theo language). Render `preview/trial-night.mp4`.
- Render: `systemd-run --user --scope -p MemoryMax=16G npx -y hyperframes@latest render . -o ../preview/<tên>.mp4 --fps 30 --workers 1 --no-browser-gpu`. `--workers 1` vì nhiều worker làm khung tĩnh nhấp nháy tuần hoàn 6 khung (snapshot cùng thời điểm giống hệt); hai lần render nhiều worker vẫn trùng nhau nhưng sai mọi số đo "đứng yên".
  Hai lần render `full-a`/`full-b`: 1230 khung, framemd5 trùng từng khung. Tương tự `trial-r1`/`trial-r2` (360 khung).
- `hyperframes check`: 0 lỗi, 0 cảnh báo lint trên `trial/` và `full/`; cảnh báo còn lại chỉ là `line_unread` cho số đếm/chữ gõ (mỗi khung một span). `presets/corporate-motion/demo/` (39 thẻ) cũng 0 lỗi.
- Kiểm nhanh không render: `JSDOM_DIR=/tmp/jsdom-env bash jobs/20261103-corp-demo-dashboard/verify.sh` (token, catalog gồm props, theme, `cmp` trial-night, thử tua `demo/seek-test.mjs` cho demo, trial, full: tua tiến, lùi, xáo, lạnh cho cùng trạng thái; cộng quy tắc tĩnh cho fromTo).
- Đo: `uvx --with numpy python -I -B jobs/20261103-corp-demo-dashboard/measure_trial.py [--full]` (dùng hàm của `jobs/20261028-230040/measure_style.py`, không sửa). Mốc cắt `cuts.json`/`cuts-full.json` là THEO THIẾT KẾ.

### Cùng thời gian chuyển động giữa các theme và cách dựng (`compare_timing.py`, đoạn thử 360 khung)

| So sánh | khung chuyển động (>50 điểm ảnh đổi >6 mức) | lệch mặt nạ | đợt chuyển động | r của số điểm ảnh đổi | trễ |
|---|---|---|---|---|---|
| `trial-a` (dựng cũ, vẽ trong scene) vs `trial-r1` (chỉ gọi catalog, kit đã sửa) | 160 / 160 | 0 | 5 / 5, đầu/cuối trùng | 0.999 | 0 |
| `trial-r1` (default) vs `trial-night` | 160 / 163 | 3 (khung 168–170) | 5 / 5, đầu/cuối của từng đợt trùng khung | 0.967 | 0 |

Chênh 3 khung (168–170) là do ngưỡng độ tương phản (chữ vào nhẹ trên nền tối vượt ngưỡng 50 điểm ảnh sớm hơn một khung); cùng một timeline GSAP nên thời điểm không thể khác. Độ lớn năng lượng khác giữa theme là bình thường.

## So với `build_defaults` (clip đủ 41.0s, `tmp/full_measured.json`)

"Khoảng" = min–max các clip gốc trong `style.json`. Đạt: V = trong khoảng, T = thấp hơn, C = cao hơn.

| Token | Mặc định | Khoảng | Clip đủ | Đạt |
|---|---|---|---|---|
| nền tint / trắng (tỉ lệ khung) | 77.8% / 22.1% | 53.6–92.5% / 7.5–46.4% | 57.3% / 42.7% | V / V |
| điểm ảnh xanh nhấn | (đo 4 clip) | 4.6–5.0% | 3.81% | T |
| điểm ảnh mực | (đo 4 clip) | 1.1–1.6% | 1.30% | V |
| card_slide_in chạm 98% | 0.475s `power2.out` | 0.27–0.50s | 0.50s (B1), 0.47s (B3); khớp gần nhất `power1.out` | V (tên ease lệch 1 khung) |
| card_slide_in quãng | 0.327 H | 0.22–0.41 H | 0.327 H (B1) | V |
| chart_pop chạm / lắng / quá đà | 0.117s / 0.433s / 0.181, `back.out(2.5)` | 0.10–0.20s / 0.27–0.63s / 0–0.33 | 0.133s / 0.40s / 0.181–0.186; khớp `back.out(2.5)` | V |
| number_count_up (qua thanh) | 0.767s `sine.out` | 0.77–2.33s | 0.80s `sine.out` | V |
| bar_fill | 0.683s `power1.inOut` | 0.30–1.4s | 0.633s; khớp `sine.inOut` | V (tên ease lệch) |
| typed_text (4 đoạn) | 21.3 ký tự/s | 20.4–22.2 | 21.3, 21.3, 21.5, 21.3 | V |
| chữ đứng yên (đoạn ≥1s, trung vị, 8 khối) | 2.01s | 1.67–5.25s | 2.07s (nhỏ nhất 1.73s) | V |
| độ dài cảnh trung vị | 4.77s | p10–p90 2.43–8.17s | 5.0s (p10 4.0, p90 6.6; 8 cảnh) | V |
| cắt/phút | 10.9 | — | 10.2 | — |
| chuyển cảnh: luật phân loại vs thiết kế | wash 0.233s, bar-wipe/dissolve/flash 0.333s, hard 1 khung | — | bar-wipe, hard, flash đúng (3/3); wash→"dissolve"; 3 dissolve→"wash" (nền cùng màu nên ít điểm ảnh đổi) | một phần |
| đợt chuyển động / phút | 29.95 | 21.6–34.8 | 19.0 | T |
| độ dài đợt (trung vị) | 0.355s | 0.33–0.42s | 0.73s | C |
| khung đứng yên (E<0.1) | 31.6% | 28.9–42.8% | 59.0% | C |
| phần clip ở trạng thái giữ | 37% | 32.7–52% | 63.0% | C |
| giữ trung vị | 0.83s | 0.77–0.90s | 1.80s | C |

## Chỗ hổng (không chỉnh số để qua cổng; nhịp theo lệnh chủ giữ nguyên)

- Nhịp: ít đợt chuyển động hơn, dài hơn, xen khoảng đứng yên dài hơn khoảng đo; một phần vì clip gốc là video nén nên không bao giờ đứng yên tuyệt đối (render sạch của ta đứng yên hẳn). Chủ đã duyệt nhịp đoạn thử ("cơ bản là ổn"), beat 4–8 giữ cùng nhịp.
- Xanh nhấn 3.81% thấp hơn khoảng 4.6–5.0% (nhiều thẻ trắng và nền trắng ở beat 2, 5, 8).
- Luật phân loại chuyển cảnh của `measure_style.py` không phân biệt wash với dissolve khi hai cảnh cùng màu nền; kit chưa kiểm chứng wash đúng nghĩa preset (nền đổi sắc toàn cục, nội dung đổi sau).
- Không đo được riêng: slide-in ở beat 5 (thẻ trắng trên nền trắng), chart_pop của ghim bản đồ và cột beat 6, số đếm 47 → 1.
- `hyperframes check` vẫn báo `line_unread` (số đếm/chữ gõ là các span chớp theo khung).
