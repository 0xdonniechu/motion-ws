# Preset: corporate-motion

Phong cách "corporate motion graphics" dọc 9:16, 2–3 phút của kênh @phantichdulieu.mda (MDA): nền trang hai chế độ (xanh rất nhạt hoặc trắng), thẻ UI trắng bo góc có bóng xanh nhạt,
chữ đậm hình học (đen + một từ nhấn xanh), pill tiến trình làm neo, số khổng lồ, khối iso xanh. Dùng để clip mới với nội dung khác vẫn mang cùng vibe; KHÔNG dựng lại khung-từng-khung.
Số đo máy đọc nằm ở `style.json`: mỗi token có giá trị từng clip, trung vị, khoảng, n, CORE/OPTIONAL và `disagree`. Khối `build_defaults` trong đó chọn MỘT giá trị cho mỗi token (đủ để dựng scene); phần "Giá trị dựng mặc định" bên dưới là bản đọc cho người của khối đó.

Trạng thái: có số đo 4 clip, token và giá trị dựng mặc định. Có kit `kit/` (từ vựng `catalog.json`: 24 component, 10 effect, 5 transition; scene chỉ gọi theo tên), tách `language.json` (chuyển động, cố định) và `themes/<tên>.json` (màu, font, kiểu chữ), xem `THEMING.md`; clip mẫu đủ 8 beat ở `jobs/20261103-corp-demo-dashboard/full/`. Font: CHỜ CHỦ DUYỆT.

## Bốn clip (cột trong mọi mảng `values` của style.json theo đúng thứ tự này)

| # | Job | Clip | Dài | Nguồn | Mốc cắt |
|---|-----|------|-----|-------|---------|
| 1 | `jobs/20261028-230040` | Power BI skill và 20% quyết định | 165.4s | 720x1280 HEVC | duyệt bằng mắt (30 mốc) |
| 2 | `jobs/corp-sample-7699100876736040244` | OEE | 167s | 576x1024 H.264 | luật năng lượng (18 mốc, không đáng tin) |
| 3 | `jobs/corp-sample-7702430597297278228` | Lãi 200 triệu mà hết tiền | 168s | 576x1024 H.264 | luật năng lượng (21 mốc, không đáng tin) |
| 4 | `jobs/corp-sample-7702801642646899989` | Dashboard 2 tuần không ai mở | 176s | 720x1280 HEVC | luật năng lượng (32 mốc, không đáng tin: độ phủ chưa biết) |

CORE = đo được ở ≥3/4 clip; OPTIONAL = 1–2 clip.

### Mốc cắt: clip 2–4 KHÔNG ĐÁNG TIN, token phụ thuộc mốc cắt chỉ lấy từ clip 1 (n=1)

Clip 1 dùng bộ mốc duyệt bằng mắt. Clip 2–4 dùng luật năng lượng (`cuts_rule.json`: đỉnh E ≥ 9 hoặc D ≥ 0.15, cách ≥ 1s).
Đối chiếu luật với mắt trên clip 1 (sai số 0.35s): độ chính xác 25/33, độ phủ 25/30. Luật thêm 8 mốc là chuyển động trong cảnh (2.667 là camera zoom, 23.8, 39.5, 43.1, 47.5, 97.0, 99.067, 101.7) và bỏ sót 5 đổi cảnh mềm (37.867, 65.3, 86.067, 131.2, 162.0).
Soi mắt 10 mốc luật dàn đều theo thời gian ở mỗi clip mẫu: thật 5/10 (clip 2), 6/10 (clip 3), 8/10 (clip 4). Phép soi này chỉ đo độ chính xác, KHÔNG đo độ phủ (không biết luật bỏ sót bao nhiêu đổi cảnh mềm; trên clip 1 độ phủ là 25/30). Vì vậy cả clip 2, 3 và clip 4 (8/10 nhưng thiếu độ phủ) bị coi là `unreliable`: số mốc, độ dài cảnh, cắt/phút, thời gian đứng yên cuối cảnh và tỉ lệ/thời lượng từng kiểu chuyển cảnh được liệt kê trong `values` nhưng KHÔNG vào trung vị/khoảng/n và KHÔNG vào `build_defaults`; mặc định lấy từ clip 1 (n=1, tier OPTIONAL). Các token không phụ thuộc mốc cắt (năng lượng, đợt chuyển động, khoảng đứng yên, chữ đứng yên) vẫn dùng cả 4 clip.

## Dùng khi

- Video giải thích một kỹ năng, công cụ hoặc khoá học cho người đi làm (dữ liệu, AI, Power BI, vận hành…), 120–180s, có giọng đọc, kết bằng thẻ thương hiệu.
- Có một luận điểm đếm được ("80/20", "4 câu hỏi", "6 tầng", "3 bước") làm sợi chỉ xuyên suốt.
- Cần mockup UI tự vẽ, không logo hãng/ảnh chụp màn hình thật.

Không dùng khi: chữ chiếm > 50% khung (kinetic-type), thẻ lặp một khuôn (list-vertical), sơ đồ hộp-mũi tên (pipeline-diagram).

## Khung beat (quan sát bằng mắt ở cả 4 clip, không đo)

wow demo / câu hỏi gây sốc → số hoặc câu hỏi treo → quote hoặc bối cảnh → ẩn dụ → checklist / các bước (pill "CÂU n/4", "BƯỚC n/3", "TẦNG n/6") → chi tiết đắt → bài học hoặc công cụ AI → CTA → thẻ MDA, và quay về số/câu treo đầu clip.
Beat của clip 1: demo 0–21.6s, số treo 21.6–37.9s, quote+ẩn dụ tảng băng 40.6–65.3s, checklist 65.3–93.8s, chi tiết đắt 93.8–113.2s, bài học 113.2–131.2s, quảng bá 131.2–141.2s, CTA 141.2–165.4s.

## Giá trị dựng mặc định (`style.json` → `build_defaults`)

Luật chọn: màu/cỡ/thông số = trung vị trên các clip có đo; ease = họ ease nhiều clip CORE dùng chung nhất, hoà thì theo clip Power BI (clip 1), thời lượng/quá đà = trung vị trên các clip cùng họ đó. Cái gì không đo được ghi "đoán".

**Màu (px ở 1080x1920 khi nói về kích thước)**
- Nền trang có HAI chế độ, cả hai bình thường: **tint `#eef7fc`** (xanh rất nhạt, phẳng; lệch ≤9 mức RGB giữa clip) và **trắng `#ffffff`** (đo `#fdfdfd`). Khung tính là "trắng" khi >70% điểm ảnh ở mép (trái/phải 4%, trên 3%, dưới 5%) là trắng bề mặt. Tỉ lệ khung trắng theo clip [1,2,3,4]: 14%, 7.5%, 46%, 30% (trung vị 22%, khoảng 8–46%); tint là mặc định, 78% khung (54–92%). Trắng không gom về một đoạn nhất định của clip (trung vị theo thập phân vị chỉ cao ở 50–70%, nhiễu giữa các clip); điều gì khiến cảnh dùng nền trắng KHÔNG đo được: chọn theo từng cảnh. Thẻ luôn `#ffffff`; trên nền trắng thẻ chỉ tách bằng bóng.
- Tint gần như phẳng (chênh ≤8 lum; p10 `#d2e9fb`–`#e1f0fb`, p90 `#fafdfd`–`#fcfcfc` giữa các cảnh). `centre_minus_edge_lum` trung vị −2.7 nghĩa là mảng giữa tối hơn mép chút (bóng thẻ và phần tử xanh nhạt nằm ở giữa), còn các điểm dừng dọc ở mép bên lại cho dải giữa sáng hơn trên/dưới ~2.5 lum: hướng không nhất quán nên dùng màu phẳng.
- Xanh đậm `#1664ba`, xanh chính `#1872ce`, xanh giữa `#3e9cec`, xanh nhạt `#8ec8f6`; chữ `#010102`, chữ phụ `#383a3b`. Xanh 4.6–5.0% điểm ảnh, mực 1.1–1.6%.
- Vàng `#fcc435` chỉ có ở 3/4 clip (clip 3 không có), một điểm nhấn nhỏ (vạch nhấn chữ, cờ).

**Thang chữ** (cỡ = trung vị 4 clip; khoảng min–max trong ngoặc; line-height 1.03 em; letter-spacing 0)
tiêu đề 84px/800 (60–106), phụ đề 56px/700 (36–87), caption 80px/800 (64–125), mục danh sách 50px/800 (37–66), nhãn pill 40px/800 (32–43), số khổng lồ 154px/800 (118–302), nhãn phần trăm 90px/800 (56–115).
Quy ước màu chữ: chữ thường đen, từ khoá xanh chính.

**Thẻ và pill** (`box-shadow` = blur đo + alpha từ độ tối ở 4px quy theo tông xanh đậm giả định; offset y = blur/4 là ĐOÁN)
- Thẻ chính: rộng 731px (0.68 W; 0.31–0.85 W giữa clip), bo góc 24px, `0 13px 53px rgba(21,101,192,0.18)`, padding nội dung 113/82/29/75 (trái/phải/trên/dưới; phụ thuộc nội dung).
- Pill: rộng 470px, cao ~83px, bo góc 41px (viên thuốc), `0 10px 40px rgba(21,101,192,0.19)`, padding 12/24/19/17.

**Nền hoạ tiết và khối iso**: lưới ô vuông chu kỳ 180px (clip 1, 4) hoặc lưới chấm chu kỳ 46px (clip 2, 3), rất mờ (tương phản 2–24 lum); họ hoạ tiết có ở 4/4 clip nhưng từng kiểu chỉ 2 clip. Khối iso xanh (3 clip: 1, 2, 4): ba mặt `#aad5fa` / `#90c7f3` / `#1b74d0` (sáng→tối).

**Vùng an toàn**: hộp nội dung (px 1080x1920) trái 143, trên 290, phải 874, dưới 1415; 26% đáy khung dành cho UI nền tảng.

**Chuyển động mặc định** (thời lượng = chạm 98%)

| Primitive | Ease | Thời lượng | Khác |
|---|---|---|---|
| card_slide_in | `power2.out` (hoà 2–2 với circ.out; theo clip 1) | 0.48s | quãng 0.33 H |
| number_count_up | `sine.out` (KHÔNG đồng thuận: sine, tuyến tính, power2.out; giá trị của clip 1, tự do chọn) | 0.77s | qua thanh chạy |
| bar_fill | `power1.inOut` (2/4: clip 2, 3; sine.out và power2.out mỗi cái 1) | 0.68s | quãng ~0.49 W |
| chart_pop (mọi cột) | `back.out(2.5)` (hoà 2–2 với power2.out; theo clip 1) | chạm 0.12s, lắng 0.43s | quá đà 0.18; so le 0.17s/0.13s (chỉ clip 1) |
| pill_progress | chấm nhảy 1 khung | pop 1.08x, lắng 0.03s | nhãn số xáo 1–2 khung |

Họ ease được so theo tên đầy đủ (bậc và chiều): `power1.inOut` khác `power2.out`.

Chuyển cảnh và nhịp phụ thuộc mốc cắt: chỉ từ clip 1 (mốc duyệt bằng mắt, n=1): dissolve 33% số mốc (0.33s), wash nền 23% (0.23s), cắt cứng 20% (1 khung), wipe dải xanh 17% (0.33s), flash xanh 7% (0.33s); cảnh trung vị 4.8s (p10 2.4s, p90 8.2s), 10.9 cắt/phút. Các kiểu chuyển cảnh đều cũng thấy ở clip 2–4 nhưng tỉ lệ ở đó không đáng tin. Không phụ thuộc mốc cắt (4 clip): đợt chuyển động 0.36s xen khoảng đứng yên 0.83s, ~30 đợt/phút.

**Font: Be Vietnam Pro 800** (chủ duyệt 2026-11-03, ghi trong `jobs/20261028-230040/owner_decisions.json`). Theo luật xếp hạng IoU, Montserrat 800 đứng đầu, Be Vietnam Pro thứ hai; chủ chọn Be Vietnam Pro vì độ rộng chữ chỉ lệch 5% (Montserrat 15%), xuống dòng giống gốc. Bằng chứng (`jobs/20261028-230040/font_check.py` → `font_check.json`, gói Fontsource; 8 chữ có dấu cắt từ 4 clip: "Hai con số", "Đáng đưa vào?", "nhưng quyết định", "Con số gộp", "Tháng này", "lãi 200 triệu.", "Một câu", "Truy vết nguồn gốc"; dựng ở 700/800/900):

| Font | Phủ tiếng Việt (134 ký tự) | IoU thô TB (trọng lượng tốt nhất mỗi chuỗi) | Sai tỉ lệ rộng/cao TB (riêng) | Nét/x-height 700 / 800 / 900 |
|---|---|---|---|---|
| Montserrat | 100% | 0.634 | 0.146 | 0.286 / 0.350 / 0.415 |
| Be Vietnam Pro | 100% | 0.581 | 0.052 | 0.289 / 0.321 / 0.358 |
| Outfit + Be Vietnam Pro dự phòng (font ghép, chỉ so sánh) | Outfit 28.4% | 0.536 | 0.058 | — |
| Plus Jakarta Sans | 100% | 0.534 | 0.062 | — |

Luật: chỉ xét font đơn phủ đủ 100%; xếp theo IoU thô (chữ dựng co về đúng hộp mực của chữ gốc); sai tỉ lệ báo riêng, không trộn vào điểm. Độ đậm = trọng lượng có nét/x-height dựng gần nhất giá trị đo 0.33 (tiêu đề, 4 clip): 800 ở cả hai font, khớp thang chữ (800; nhãn nhẹ hơn 700). Montserrat đứng đầu về IoU nhưng chữ rộng hơn gốc 15% so với 5% của Be Vietnam Pro: hai ứng viên sát nhau, chủ cần duyệt bằng mắt trên một đoạn thử. Chữ gốc có "a", "g" một tầng như Outfit nhưng Outfit không phủ tiếng Việt, và không font đủ điều kiện nào có "a" một tầng; IoU là so hình thô, không phải nhận diện font.

## Token CORE (4 clip; trung vị, khoảng min–max)

- Màu: xem trên (mọi token màu 4/4, vàng 3/4).
- Chữ (cỡ = x-height/0.5 hoặc cao chữ số/0.7, ±10%); nét/x-height 0.12–0.37 (≈ ExtraBold–Black); khe chữ/x-height 0.14–0.18 trên tiêu đề.
  **Không khớp giữa clip** (`disagree` trong style.json): số khổng lồ lệch 2.6× (0.061–0.157 H: clip 1 rất lớn 302px, clip 4 118px), phụ đề 2.4×, nhãn phần trăm 2.1×, nét/x-height của caption 3.0× (0.12–0.36), nhãn pill 2.3×, khe chữ tiêu đề 2.4× và số khổng lồ 5×.
- Bố cục: hộp bao nội dung trung vị x 0.13–0.81 W, y 0.15–0.74 H. Bo góc (W): pill 0.038, thẻ chính 0.022 (lệch 3.1×: 0.014–0.044), thẻ hàng 0.026 (2.6×), khung xanh cta_frame 0.024 (4.3×; clip 4 góc vuông). Nét khung cta_frame 0.0035–0.028 W (lệch 7.9×). Bóng tản (W): pill 0.037, thẻ chính 0.049 (0.025–0.059).
- Chuyển cảnh: KHÔNG có token CORE đáng tin (chỉ clip 1 có mốc duyệt bằng mắt, n=1); xem mục mốc cắt. Tỉ lệ ở clip 2–4 (không đáng tin) trong `values`: dissolve 56–57%, cắt cứng 5–33%, wash 11–19%.
- Nhịp: ~30 đợt chuyển động/phút (22–35) dài ~0.36s xen khoảng đứng yên trung vị 0.83s (0.77–0.90), 37% thời gian clip đứng yên (33–52%), chữ tiêu đề đứng yên trung vị 2.0s (1.7–5.3). Độ dài cảnh và cắt/phút: chỉ clip 1 (4.8s; 10.9/phút), clip 2–4 không đáng tin.
- Primitive CORE: card_slide_in, number_count_up (3/4), bar_fill, chart_pop (cột 1: 4/4; cột 2, 3: 3/4), pill_progress (3/4).

## Token OPTIONAL

typed_text (2/4), camera_dive (2/4), flash-wipe (clip 1, 3), headline_question, flag_plant, node_radial, chat_autoscroll, chart_bar_fall, icon_pole (mỗi cái 1 clip), button (tách thành 3 hành vi, mỗi hành vi 1 clip), lưới ô vuông và lưới chấm (mỗi kiểu 2 clip). Dùng khi nội dung cần, không bắt buộc cho vibe.

## Primitive: số đo và chỗ các clip KHÔNG khớp

Mỗi ô là trung vị (min–max) trên các clip đo được; "ease" là tên GSAP gần nhất theo từng clip [1,2,3,4]. Bezier chỉ giữ khi khớp tốt (rmse ≤ 0.05) và hợp lý; bezier vô lý (vd. y>1 khi dữ liệu không quá đà) đã bỏ khỏi style.json (`bezier_by_clip` = null).

| Primitive | n | Chạm 98% | Quá đà | Ease [1,2,3,4] | Không khớp |
|---|---|---|---|---|---|
| card_slide_in | 4 | 0.375s (0.27–0.50) | 0 | power2.out, power2.out, circ.out, circ.out | hoà 2–2 power2.out vs circ.out; 0.27–0.5s; quãng 0.22–0.41 H |
| number_count_up | 3 | 1.4s (0.77–2.33) | 0 | sine/ramp, linear, —, power2.out | ba đường cong khác nhau: clip 1 chậm rồi nhanh qua thanh, clip 2 tuyến tính 2.3s qua diện tích, clip 4 power2.out 1.4s |
| bar_fill | 4 | 0.68s (0.30–1.4) | 0 | sine.out, power1.inOut, power1.inOut, power2.out | ba họ ease (sine.out / power1.inOut / power2.out); thời lượng 0.3–1.4s |
| chart_pop (cột 1/2/3) | 4/3/3 | 0.2/0.13/0.10s | 0.08/0.17/0.18 (khoảng 0–0.33) | back.out(2.5), power2.out, power2.out, back.out(2.5) | HAI KIỂU: clip 1, 4 nảy 16–33% (back/elastic, lắng 0.27–0.63s); clip 2, 3 lên mượt không quá đà. Clip 2: cột 2–3 là cột RƠI (chart_bar_fall) |
| pill_progress | 3 | nhảy 1 khung | pop 1.08x (1.07–1.17) | — | lắng 0.03s (clip 2, 4) vs 0.2s (clip 1); clip 3 chấm quá mảnh, không đo |
| typed_text | 2 | — | — | — | đếm khung chính xác (chỉ số khung từ 0, t = n/30s). Clip 1: ký tự đầu "M" ở khung 49, ký tự thứ 21 (dấu phẩy, "Mở báo cáo doanh thu,") ở khung 76: 20 ký tự trong 0.9s = 22.2 ký tự/s. Clip 2: ký tự đầu ở khung 177, ký tự thứ 20 ("Máy chạy hết rồi mà,") ở khung 205: 19 ký tự trong 0.93s = 20.4 ký tự/s. Số ký tự đọc bằng mắt tại các khung đó (ghi trong `instances.json`). Clip 3: chữ hiện từng TỪ, không đo; clip 4: không đo được |
| button_swell_pre_click (clip 1) | 1 | 1.4s | 0 | power1.in | phồng 1.0→1.175 rồi bấm |
| button_pop (clip 2) | 1 | 0.6s | 0 | tuyến tính | pop rồi thả |
| button_click_swell (clip 4) | 1 | 0.07s | 0 | expo.out | phồng khi bấm, 2 khung |
| camera_dive | 2 | — | — | — | tốc độ đỉnh khác 16× (0.016–0.254 H/khung) |
| flag_plant | 1 | cột 0.2s, cờ 0.17s (quá đà 6%) | — | power2.out, back.out(1) | clip 3: cờ hiện đúng 1 khung |

Nút từng gộp ba hành vi không liên quan thành một primitive; nay tách thành ba primitive OPTIONAL, mỗi cái một clip.
Tóm lại: tên primitive và vị trí dùng chung giữa 4 clip, nhưng đường cong ease không thống nhất. Khi dựng, dùng bộ mặc định ở trên, coi min–max là vùng cho phép và kiểm lại từng scene bằng `motion.py`.

## Nên

- Một họ màu xanh 4–5 sắc; nền trang tint `#eef7fc` là mặc định, trắng cho khoảng 1/5 số khung (8–46% tuỳ clip); thẻ luôn trắng; vàng chỉ một điểm nhấn nhỏ.
- Tiêu đề 2 màu: từ thường đen, từ khoá xanh, cùng độ đậm.
- Vào cảnh bằng `power2.out` hoặc `circ.out`; pop có quá đà bằng `back.out(~2.5)` khi cần "nảy" (clip 1, 4).
- Pill tiến trình đứng yên, chỉ chấm nhảy 1 khung rồi lắng.
- Đổi ý lớn bằng dissolve/wash 0.2–0.4s; dành cắt cứng và wipe dải xanh cho nhịp "đập".
- Mockup UI tự vẽ; mọi thứ là hàm của thời gian timeline (không `Math.random`).

## Không nên

- Không chép logo hãng/ảnh chụp màn hình thật (Microsoft Build, Power BI là mockup trong gốc).
- Không bóng đổ cứng/đen, không gradient rực, không thêm tông ngoài họ xanh + vàng.
- Không coi ease/độ nảy/cỡ số khổng lồ là cố định: 4 clip không thống nhất (bảng trên).
- Không ép "typed text" từng ký tự cho mọi clip: gốc có cả gõ từng ký tự lẫn hiện từng từ.

## Nội dung riêng từng clip (KHÔNG phải style)

Mỗi mục chỉ xuất hiện ở một clip (danh sách đầy đủ ở `style.json` → `content_not_style`):
- Clip 1: tảng băng (phần nổi/chìm), cặp số 80/20, hộp Skill + mockup Microsoft Build, cờ "dấu mốc", mindmap 6 nút Agentic AI Analytics.
- Clip 2 (OEE): ẩn dụ xô nước rò, nhà máy iso, lưới ô vuông đơn vị (60.000/72.000), khung chat "Còn AI?", cột rơi 100%→85%→72.3%.
- Clip 3 (Lãi): đường + xe + đồng hồ xăng, thẻ "BẢNG ĐIỂM" hạng A, bình nước/ống dòng tiền, số 200 triệu / 1,2 tỷ.
- Clip 4 (Dashboard): mockup điện thoại, ngôi nhà nứt, cầu thang/chồng 6 tầng iso, ếch "nhảy cóc", khối lego dấu hỏi.
Từ vựng hình ảnh chung quan sát ở ≥3 clip (xem tổng quan, không đo): pill tiến trình đánh số, tiêu đề 2 màu, khối iso xanh, khung góc vuông + lưới nền, thẻ MDA kết video.

## Bằng chứng và tái tạo

Mỗi clip có `instances.json` (thể hiện đo từng primitive/chữ/góc/bóng/thẻ/lưới/khối iso, số ký tự gõ đọc bằng mắt, kết quả soi mốc cắt), `cuts_rule.json`, `tmp/measured.json` (số đo thô, gitignored). Clip 1 còn `cuts.json` (mốc duyệt bằng mắt). Mã đo chung: `jobs/20261028-230040/measure_style.py`; so font: `jobs/20261028-230040/font_check.py` (8 chữ có dấu; kết quả `font_check.json`, `build-style` chỉ đọc lại, không cần mạng).
Tái tạo y hệt `style.json` (đã chạy hai lần, so byte): `uvx --with numpy python -I -B jobs/20261028-230040/measure_style.py build-style --style presets/corporate-motion/style.json`.
Khung xem tay (gitignored, tạo lại bằng `grid`/`strips`/`sheets`): `jobs/*/frames/`.

## Chỗ hổng và phỏng đoán

- Font: so hình thô, hai ứng viên đầu sát nhau (Montserrat IoU cao hơn nhưng rộng hơn gốc), chưa có "a" một tầng; CHỜ CHỦ DUYỆT. Độ đậm suy từ nét/em; cỡ chữ từ x-height/0.5 hoặc cao chữ số/0.7 (±10%).
- Mốc cắt clip 2–4 theo luật, không đáng tin (độ chính xác soi mắt 5–8/10, độ phủ chưa biết): token phụ thuộc mốc cắt chỉ từ clip 1 (n=1). Kiểu chuyển cảnh phân loại bằng luật đo được, chưa duyệt từng điểm.
- `box-shadow`: blur và alpha suy từ số đo, offset y và tông xanh là ĐOÁN. Padding thẻ phụ thuộc nội dung (thẻ minh hoạ chạm mép) nên khoảng rộng; chiều rộng thẻ chính lệch 2.8× giữa clip.
- Lưới nền: chu kỳ đo trên một khung mỗi clip, rất mờ; khối iso: màu ba cụm xanh nhiều nhất trong hộp tay chọn.
- Clip 2, 3 chỉ có bản 576x1024 (clip 1, 4: 720x1280): nét mảnh sai số lớn hơn, phân số W/H đã chuẩn hoá. Một số vai chữ/bo góc đo trên phần tử khác nhau giữa clip nên khoảng min–max rộng.
- Mỗi primitive mỗi clip thường chỉ một thể hiện; đường cong ease khớp trên 3–30 mẫu 30fps. Số đếm đo gián tiếp qua thanh/diện tích. Camera dive chỉ đo tịnh tiến dọc.
- Chưa phân tích âm thanh (CLAUDE.md: không làm audio cho tới khi chủ yêu cầu).
