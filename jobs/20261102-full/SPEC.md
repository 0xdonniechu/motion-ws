# Remake spec — "GSAP và Motion" (ghuypham.dev, 36.03s, 1080x1920, 30fps)

Gốc: `source.mp4` (cùng thư mục, KHÔNG commit, KHÔNG chép asset gốc vào scene).
Mẫu đã duyệt (đọc trước khi làm): `../20261102-spring-seg/rebuild/index.html` —
cấu trúc HyperFrames, font-face, ease lò xo, cách che chữ dưới thanh.

## Hệ thiết kế chung (mọi cảnh)
- Nền giấy kem `#efece6`; cảnh tối `#1b1714`/`#141414`. Cam đỏ `#c9451c`, xanh `#2f5bea`,
  vàng `#e0a312`, tím `#7a3cf0`, xanh lá `#1d8a52`, xanh GSAP `#0ae448`.
- Nhãn `AI Tips` JBMono 26px tại (130,128) — có ở mọi cảnh, kể cả cảnh tối (màu nhạt).
- Phụ đề: Inter 500 78px, left 130 top 248 width 900, hiện từng từ theo nhịp đọc;
  từ nhấn = Instrument Serif nghiêng 96px màu cam đỏ (`em`).
- Chữ lớn: Anton, tô gradient xám đậm→nhạt hoặc đặc; thẻ: viền đen 7px, bóng đổ cứng 10/12px đen, bo 30px.
- Hoạ tiết nền: lưới chấm (halftone), chấm cam, giao diện mờ nghiêng phối cảnh.
- Font chỉ dùng `../shared/fonts/` (Anton, Inter, Instrument Serif italic, JetBrains Mono).
  Nhân vật hoạt hình/ảnh người: thay bằng vòng tròn avatar đơn giản (khối màu + chữ "GH").
  Logo Motion: ô đen bo góc có 3 vạch xiên trắng + chấm (tự vẽ SVG). Logo GSAP: ô chữ "GSAP" Anton.

## Cảnh (mốc theo bản gốc; duration của scene = cột Dài)

| # | Gốc | Dài | Nội dung | Phụ đề (từ nhấn trong *...*) |
|---|---|---|---|---|
| 01 | 0.00–1.00 | 1.00 | Chữ "CHUYỂN / ĐỘNG" Anton cực lớn (cam đỏ, bóng đen) bay vào từng mảnh rồi rung; 3 sọc cam ngang dưới; 0.75s vòng halftone cam bùng ra quanh chữ | Toàn bộ chuyển động bạn đang / là |
| 02 | 1.00–2.75 | 1.75 | Chồng thẻ code đen xếp nghiêng (gsap.timeline() / .to(chars, { stagger: 0.02 }) / SplitText.create...), chữ gõ dần; tem "CODE THẬT" Anton cam nghiêng; vignette tối; từ 2.0 code tan thành trường hạt chấm gợn sóng | là code thật, do Claude Code viết bằng *hai* thư viện: |
| 03 | 2.75–4.10 | 1.35 | Hạt hội tụ thành chữ "GSAP" trong thẻ đen → chữ xanh GSAP đặc; 3.4s cụm thẻ tính năng (spring, stagger, exit, drag, useAnimate, useSpring) bung ra quanh logo Motion; ô logo GSAP + Motion + avatar góc dưới | *GSAP* và *Motion.* |
| 04 | 4.10–6.00 | 1.90 | Chữ "gsap.timeline()" mono cam; đường cong xoắn ốc đen, chuỗi ô vuông màu chạy dọc đường (như rắn); thước thời gian dưới với vạch play đỏ chạy; chữ "timeline" mờ lớn phía sau | *GSAP* mạnh nhất ở những chuỗi chuyển động dài; |
| 05 | 6.00–6.70 | 0.70 | Chữ "SplitText" ký tự bay tán loạn rồi ráp lại; "TỪNG KÝ TỰ" cam; chip đen `type: chars` | chữ tách từng *ký* tự, |
| 06 | 6.70–7.90 | 1.20 | Hình cam đỏ viền đen morph: tròn → sao → blob → vuông → chữ G, để lại viền ma mảnh; tia mảnh toả nền; chip đen `morphSVG: "#circle"` đổi text theo hình | *hình* này biến thành *hình* khác, |
| 07 | 7.90–9.20 | 1.30 | Quả cầu chấm cam → lưới halftone full màn cam gợn sóng; vòng tròn đen lan ra rồi thành vòng sáng; hết cảnh: lưới đen-cam | cả nghìn ô gợn sóng cùng một lúc. |
| 08 | 9.20–13.0 | 3.80 | Khối hộp 3D cam (mặt SCROLL / PIN / SCRUB / GSAP) xoay theo bộ đếm `scrollY` tăng dần (góc phải dưới); marquee chữ lớn "CUỘN · SCROLL" và "NHIỀU LỚP · KHÁC TỐC ĐỘ" chạy ngang; nhãn lớp far 0.2× / mid 0.5× / near 1× / product pin / fore 2.4×; chấm tròn mờ màu bay parallax; bóng elip dưới hộp | *Cuộn* tới đâu, cảnh dựng tới đó. / Nhiều lớp chạy khác tốc độ, / sản phẩm xoay theo từng nhịp *cuộn.* |
| 09 | 13.0–16.2 | 3.20 | Nền tối lưới ô vuông; cửa sổ terminal "Claude Code" gõ `/plugin marketplace add greensock/gsap-skills` rồi `/plugin install gsap-skills@gsap-skills`, badge số đỏ ①②; số % lớn trái đếm 18→78; tam giác play cam bay; chip "greensock/gsap-skills" + ô GSAP; cuối cảnh lùi xa, mặt hộp cam phía sau | Để Claude viết *đúng* như vậy, / cài skill *chính chủ* của GSAP: / *hai* lệnh plugin. |
| 10 | 16.2–18.7 | 2.50 | Vòng tròn mở ra nền sáng: "GIAO DIỆN" Anton gradient; tab All/Design/Code (pill đen chạy); lưới 2 cột thẻ dashboard (thanh màu) tự sắp xếp lại theo tab (FLIP); chữ lớn đổi "layout"; giao diện mờ nghiêng nền; viền chấm cam | *Motion* mạnh ở giao diện: / thẻ tự sắp xếp lại, |
| 11 | 18.7–19.40 | 0.70 | Thẻ đen "Tasks" với badge số cam (6→9→6→8), các hàng chip (layout, exit, stagger, initial, animate, useSpring, layoutId, popLayout) chèn/xoá; chữ lớn "THÊM BỚT" | danh sách thêm bớt mượt, |
| 12 | 19.40–21.0 | 1.60 | Cảnh spring — lấy từ mẫu đã duyệt, cắt còn 1.6s (đoạn 0.4–2.0 của mẫu, tức bỏ 0.4s đầu) | mọi thứ nảy như *lò* xo thật. |
| 13 | 21.0–24.0 | 3.00 | Trên: bảng thẻ màu chữ to "KÉO" "NÉM" "THẢ" "TRƯỢT" "NẢY" bị kéo-ném bởi con trỏ; nhãn `Draggable + Inertia`. Dưới: panel đen `drag · dragElastic` với thẻ throw/inertia/drag/elastic/bounce bị con trỏ kéo, trượt quán tính | *Kéo,* ném, buông tay, / mọi thứ vẫn trượt tiếp tự nhiên. |
| 14 | 24.0–28.4 | 4.40 | Lớp phủ xám trên cảnh 13; terminal `$ npx motion-ai` gõ; tag cam "/motion" bật ra; chip trắng "MCP · mcp.motion.dev" có đường nối tới icon; thẻ dưới tiếp tục xáo | Còn *Motion,* chạy lệnh trên màn *hình.* / nó thêm skill */motion* và kết nối / *MCP* tra cứu docs cho Claude Code. |
| 15 | 28.4–30.4 | 2.00 | Các panel dọc trượt ngang (mảnh các cảnh trước: GIAO DIỆN, SplitText, layout); ô prompt trắng gõ "Tiêu đề bay vào từng chữ, thẻ này như lò xo"; sao cam lớn morph thành G; chip `morphSVG` | Rồi chỉ cần tả bằng *lời.* |
| 16 | 30.4–33.0 | 2.60 | Lưới 3×3 thẻ ôn lại (thu nhỏ các cảnh: hạt, tròn cam, Tasks, hộp SCROLL, halftone, spring chips, KÉO/NÉM, logo Motion, drag) — mỗi ô tự động nhẹ; pill cam "Đọc SKILL.md trước khi cài"; cuối: 2 ô logo GSAP + Motion nổi + dấu "?" cam + avatar | Claude viết *đúng* cách của từng thư viện. / *Đọc* kỹ skill trước khi cài. / Bạn thích cái nào hơn? |
| 17 | 33.0–36.03 | 3.03 | Chuyển halftone đen quét; "LƯU" Anton đen + bookmark cam; "&" serif nghiêng cam; nút đen "FOLLOW" → con trỏ bấm → "FOLLOWING ✓"; pill "@ghuypham.dev"; 3 icon nhỏ; avatar góc phải dưới (thay nhân vật) | (không phụ đề) |

Cách xem gốc từng cảnh: `ffmpeg -ss <đầu> -t <dài> -i source.mp4 -vf "fps=5,scale=270:-1,tile=..." ...`
— xem khung trước khi dựng, khớp vị trí/kích thước bằng mắt ở 1080x1920.

## Điểm nối (mục 2, duyệt 2026-11-02)

Ghép bằng `compose.sh`: scene k nằm ở `[S[k-1]-pre, S[k]+post]`, scene sau ĐÈ scene trước.
`joins.json` khai báo `{"sNN": {"pre": x, "post": y}}`. File render phải dài đúng `pre + Dài + post`.

**Hợp đồng cho scene có pre hoặc post > 0** (hoặc cần trong suốt):
- Render `--format mov` → `scenes/sNN.mov` (ProRes 4444 alpha). Xoá `sNN.mp4` cũ của scene đó.
- `html, body, #root` nền `transparent`. Nền giấy/tối của scene là một lớp riêng (`#bg`) để che/lộ được.
- Nội dung cũ dịch đi `pre` giây: bọc timeline cũ vào timeline chính tại vị trí `pre`
  (`main.add(old, PRE)`), `data-duration` = pre + Dài + post.
- Trong `pre`: chỉ vẽ phần chuyển cảnh vào (hình mở/quét/chữ bay); phần còn lại trong suốt để scene trước lộ ra.
- Trong `post`: scene tiếp tục/thoát ra như bản gốc (mờ dần, bay đi); scene sau sẽ đè lên.
- Khớp-khung (match-cut): khung cuối scene trước phải gần như trùng khung đầu scene sau
  (cùng vị trí, kích thước, màu). Kiểm tra bằng snapshot hai bên.

| J | Mốc | Kiểu (theo gốc) | Ai làm | pre (scene sau) / post (scene trước) |
|---|---|---|---|---|
| J1 | 1.00 | Vòng halftone cam lan ra phủ kín cam đặc tại 1.00; scene 02 mở từ cam đặc mờ dần (0.15s) ra thẻ code | s01 post: chữ nhoè + cam phủ (khung 27–32); s02 trong suốt, mờ dần vào, thẻ code rõ ở khung 35 | 0/0.15 (đo theo gốc) |
| J2 | 2.75 | Trường hạt của s02 hội tụ thành chữ GSAP | s03 bắt đầu bằng đúng trường hạt cuối s02 (chép bộ sinh hạt của s02) rồi hội tụ | khớp-khung, 0/0 |
| J3 | 4.10 | s04 trượt lên từ dưới có nhoè dọc, đè lên s03 | s04 pre; s03 post (đứng yên/tiếp tục) | 0.15/0.15 |
| J4 | 6.00 | Chữ SplitText bay vào đè lên s04 đang mờ dần (rắn màu còn chạy) | s05 pre (trong suốt trừ chữ); s04 post mờ dần về 0 | 0.30/0.30 |
| J5 | 6.70 | Chữ SplitText giãn ra + mờ; hình tròn cam nở ra | s06 pre (chỉ hình tròn + nền mở dần); s05 post chữ giãn + mờ | 0.15/0.15 |
| J6 | 7.90 | Chữ G tan thành mây chấm cam | s06 kết thúc ở G bắt đầu tan; s07 khung đầu là mây chấm đúng vị trí/kích thước G | khớp-khung, 0/0 |
| J7 | 9.20 | Lưới halftone cam bị quét chéo, cảnh hộp SCROLL lộ ra sau mép chéo | s08 pre (mặt nạ chéo mở dần); s07 post giữ lưới | 0.25/0.25 |
| J8 | 13.00 | Hộp phóng to bay lên khỏi mép trên; cảnh terminal tối trồi lên từ dưới | s08 post (hộp scale + bay lên, rời khung ~13.57 như đo); s09 pre (nền tối trượt lên từ dưới, trong suốt phía trên) | 0.35/0.60 (đo theo gốc) |
| J9 | 16.20 | s09 lùi xa + xám; chấm cam ở giữa nở thành vòng tròn mở ra cảnh 10 (viền cam) | s10 (mặt nạ tròn từ chấm, viền cam, trong suốt); s09 post lùi + xám tới khi vòng tròn phủ kín (gốc 16.20–16.45) | 0/0.25 (đo theo gốc) |
| J10 | 18.70 | Khớp: tiêu đề + thẻ Tasks đã có từ ~18.3 trong s10 | s10 kết thúc đúng bố cục khung đầu s11 (tiêu đề "THÊM BỚT", thẻ Tasks cùng vị trí) | khớp-khung, 0/0 |
| J11 | 19.40 | Thẻ Tasks ngả ra sau rơi xuống; chữ "spring" mọc + thẻ bounce rơi đè lên | s12 pre (trong suốt trừ thanh/chữ/thẻ; nền kem mở dần); s11 post thẻ Tasks ngả + rơi | 0.30/0.30 |
| J12 | 21.00 | Bảng KÉO/NÉM trượt từ trái, panel tối trượt từ phải, đè lên spring | s13 pre; s12 post giữ spring | 0.15/0.15 |
| J13 | 24.00 | s13 tối dần (gốc: 23.433, trong 2 khung) thành lớp phủ xám; s14 tiếp tục trên đúng bố cục đó | s13 tự tối trong thời lượng; s14 khung đầu trùng khung cuối s13 | khớp-khung, 0/0 |
| J14 | 28.40 | Gốc: lớp phủ s14 mờ đi 28.33–28.47 rồi cắt sang nền kem tại 28.5 (không có dải trượt) | s14 post tự mờ; s15 trong suốt tới t=0.1 | 0/0.10 (đo theo gốc) |
| J15 | 30.40 | G của s15 tan thành hạt cam; lưới 3×3 thu từ lớn về chỗ | s15 post: G tan hạt + panel mờ; s16 ô giữa bật tại 30.40, các ô khác 30.467 | 0/0.15 (đo theo gốc) |
| J16 | 33.00 | Chấm halftone đen lan phủ kín rồi co lại lộ nền kem + "LƯU" | s17 chấm đen quét chéo từ góc trên trái, đen kín ~33.13, co lại lộ LƯU; s16 post giữ | 0/0.20 (đo theo gốc) |

Kiểm tra mỗi điểm nối: `bash compose.sh` rồi xem `preview/joins/JNN.jpg`
(3 cặp gốc|remake tại mốc −0.1 / 0 / +0.1 s). Bản remake phải cùng KIỂU chuyển, cùng hướng, cùng nhịp.

`joins.json` là nguồn đúng cho pre/post; bảng trên đã cập nhật theo số đo thực (2026-11-02).

## Textures (mục 3: s02, s03, s07)

Đo từ khung 30fps của `source.mp4` (khung file f01 = đầu cảnh; thời gian cảnh t = (f−1)/30). Script đo lặp lại được: `measure_texture.py`
(`wave`, `ring`, `disc`, `ripple`). Mã dựng: `shared/texture.js` (symlink vào s02, s03, s07 như `boil.js`): hàm thuần của (tham số, thời gian),
hash có seed, không `Math.random`, không rAF. Chỉ dựng cái đo được; chỗ nào chưa có số đo thì ghi ở "Còn thiếu".

### Số đo và cách dựng

**s02: trường hạt (f31–f53), vùng y 1450–1900 không có thẻ.** Ô VUÔNG đặc cỡ 10–19px (trung vị 14), ~460 hạt / 1080×450 px², lưới 26×39 px lệch ±3px;
màu lõi tối `#37322a` 80%, cam `#c45a33` 13%, xanh `#536ff8` 4.5%, xám 2.5%. Dịch chuyển bám từng hạt (≈400 hạt khớp/khung, R² 0.8–0.9; trung vị 8 px/khung):
`dy = 34 sin(0.0170 x + 0.0055 y + 8.74 T − 0.87)`, `dx = 11.7 sin(0.0130 y + 8.74 T + 1.89)` (T = giây từ đầu s02) và trôi trái 2.8 px/khung CHỈ đo ở f36–f46 (T 1.17–1.5), mã
dừng trôi ở T=1.5. Hạt hiện từ giữa (y≈1200) mở ra cả khung trong f31–f35; ô nền biến mất cùng lúc; mép trên mờ (y 120→500).
Cuối s02 hạt kéo về dải y≈967 (13–17 px/khung); s03: 55% hạt thành chữ GSAP, phần còn lại thành sợi; gốc có khung lặp (s03 f1=f2, f16=f17=f18): không dựng lại.

**s02: vòng tối halftone (f11–f22).** Là chính lưới ô 46px (ô 38×36, bo 9, `#dbd5ce`) tối dần tới gần đen, kể cả khe (khe ≈ 16/255 trong vùng tối).
Mỗi khung một lần khớp riêng: elip (cy, rx, ry) + hồ sơ độ tối theo bán kính tại 11 mốc (`TX.RK`), khớp trên ô không bị thẻ/chữ che, trọng số lớn nhất cho cột ô trái.
Kiểm: độ sáng dải trái x 0–30 (gốc → remake), y 736–828: f12–f23 = 223,120,26,22,63,143,197,223,… → 220,124,40,20,27,129,176,208,… (cùng nhịp, lệch ≤ ~40 mức xám ở khung chuyển).
(Bản trước đặt khoá thời gian lệch 1 khung: đã sửa thành t = (f−1)/30.) Lưới ô nền chỉ hiện từ y≈220→700 trở xuống.

**s02: thẻ xoè (f6–f12).** Mép trên chồng thẻ ở x=540 đo được 730, 689, 660, 619, 584, 508 px (f6→f11; thẻ trồi lên từ sau tấm code, 29–76 px/khung) và độ dốc mép đổi 4.7° → 6.2° → 4.9° → 3.2° → −1.1° → −4.6°;
mép dưới của thẻ phía dưới ở x=660: 1181 → 1317 (f6→f10, thẻ tụt xuống sau tấm code). Dựng: hai nhóm `#upG`/`#dnG` có khoá dịch (và góc, nhóm trên) từng khung từ các số đo này
(`FAN` trong s02), so với tư thế cuối. Mép trên remake sau khi dựng: 731, 690, 661, 621, 586, 510 (khớp ±5px ở x=300–660). Thẻ trôi cuối cảnh trở lại ±14px/±1.5° như bản gốc của job (bản ±36/±3.5° không có số đo đã bỏ).
Thẻ vỡ sớm 0.1s (0.9s thay vì 1.0s) vì năng lượng khung gốc tăng ở f28–f30.

**s02: robot và thẻ trên sau khi xoè.** Ô trắng robot (tâm 804,1317) hiện ở f23 nhỏ ~85px xoay ~−18° (khung cắt), cạnh 140, 157, 167, 173 px ở f25–f28 (đo bbox thành phần trắng); vòng nan đường kính ~198, 279, 319, 346, 352 px ở f24–f28 (đo trên ảnh cắt, mờ ở f29–f31):
dựng bằng khoá từng khung (`RB`, `RRK` trong s02), thay cho tween bắt đầu 0.62s (hiện sớm ở f19). Thẻ trên còn lệch tiếp f18→f24 theo NCC vùng x 20–420, y 470–760 (NCC ≥ 0.79): (+24,−20), (+16,−8), (+12,−4), (0,−4), (−12,−4), (−4,0) px, sau đó đứng; dựng thành khoá x,y của `#upG`.
Các dịch f12–f17 có NCC 0.4–0.7 (bị vòng tối che) nên không dựng.
Vỡ thẻ code (đo độ phủ điểm ảnh tối < 60 của tấm code, vùng x 100–900, y 800–1000): gốc 0.87 tới f29, 0.86 (f30), 0.70 (f31), 0.22 (f32), 0.14 (f33) ⇒ độ mờ tấm code 1, 0.99, 0.80, 0.25, 0.15, 0 ở f29–f34; vùng thẻ: 0.39 → 0.30 → 0.11 → 0.10 ⇒ 0.77, 0.28, 0.26, 0.15, 0 ở f30–f34.
Bản trước dùng power1.in từ 0.9s nên tấm code đã còn 0.2 ở f31 (gốc 0.8); nay dựng bằng khoá từng khung (`BRK`), bỏ co 1.05/1.06 không có số đo.
Robot: tỉ lệ điểm ảnh đỏ trong hộp x 650–960, y 1150–1520 gốc 0.069, 0.070, 0.086, 0.104, 0.100, 0.105, 0.106, 0.100, 0.069 (f22–f30), remake 0.038, 0.048, 0.070, 0.093, 0.100, 0.106, 0.106, 0.101, 0.059 — khớp trong ±0.01 ở f25–f29 (ngưỡng đỏ: R>185, G<120, B<90 của lệnh `brk` trong measure_texture.py; với ngưỡng R−B>80 gốc 0.137–0.165, remake 0.087–0.123, nên kết luận phụ thuộc ngưỡng); trong ô trắng
gốc 0.033 → 0.145 (f22 → f29, đạt đỉnh f29) so với remake 0 → 0.174 (đỉnh f28): remake đỏ HƠN gốc ~20%, không thiếu 30% như số liệu của người duyệt (khác cách đo; chưa tìm được vùng cho ra 0.15 → 0.22). Đường kính vòng nan và góc xoay 30° chỉ có ước lượng bằng mắt (xem Còn thiếu).

**s03: thời điểm (tương quan chéo năng lượng vùng giữa theo độ lệch khung).** Thẻ GSAP: gốc bùng ở khung 9–11, remake sớm ~1.5–2 khung ⇒ `SH = 0.067`. Cụm thẻ: theo yêu cầu `SC = 0` (gốc hiện cụm ở abs 104; remake hiện trong ±2 khung: đỉnh năng lượng vùng giữa ở idx 19–20 so với gốc idx 21–23).
Chuột bấm, logo nhỏ không có số đo nên không dời. Ô nền xám 46px không có ở s03 (gốc: kem trơn) nên tắt.

**s03: cụm thẻ hiện (f22–f26) và vòng bấm chuột.** Bám mẫu từng thẻ từ f26 ngược về f25/f24 (matchTemplate, thử co 0.6–1.3, xoay ±40°; chỉ giữ NCC ≥ 0.5): ở f25 phần lớn thẻ lệch ≤ ~25px khỏi chỗ cuối, ở f24 lệch 40–85px
(`exit` từ −86 → −40 → −17 px theo y ở f23 → f25; `useSpring` −77 → −2; thẻ `stagger` đầu hàng −55 → +14 rồi vào chỗ); f23 không bám được (NCC < 0.5) nên giữ tư thế f24. Khoá dịch từng thẻ nằm trong `TP` (s03). Xoay/co từng thẻ chưa đo đủ tin cậy nên không dựng, trừ thẻ logo:
cạnh 257 → 413 → ~496 px ở f23 → f25 (co 0.52, 0.83, 1.0), xoay ước ~−12° → −2°.
Vòng bấm chuột (bỏ phiếu vòng tròn trên điểm ảnh cam): tâm (540,900), bán kính 201 (f22) → 531 (f23) → 903 (f24), dày ~25px, màu ĐẶC `#c14212` (193,66,18) — không nhạt như yêu cầu của người duyệt (đo màu thực của gốc); hết ở f25; ô vuông đen nghiêng ở tâm ở f21–f22.
Thẻ vào đầu cột (cột trái: thẻ xanh, rồi `useAnimate` cam; phải trên: `drag` mờ) thay cho thẻ cũ quay vòng; đầu cụm mờ dần ở y 380–480.
Bỏ nhún ±8px sau khi vào chỗ vì không có số đo. Gốc KHÔNG đứng yên: ở abs 108–112 các khối gốc 10–43 so với remake 0.4–5 (thẻ logo còn xoay thẳng và dịch, thẻ quanh còn chạy, logo tô từ xám sang trắng); NCC chỉ 0.03–0.18 vì nội dung đổi, không phải vì đứng yên. Chưa dựng — xem khoảng hụt.

**s03: cột thẻ trượt dọc (f32–f41).** NCC dải cột giữa hai khung liền nhau (NCC 0.5–0.78): cột trái (x<230) trượt xuống +76, +115, +109, +84, +58, +19, +5, +8 px/khung ở f32→f40 (tổng ~474, cực đại 115 ở f33→34);
cột phải (x>860): −34, +87, +26, +68, +38, −3, +67, +38 px/khung ở f33→f41; hàng trên (y 380–600) và vùng giữa-dưới (x 260–560, y 1150–1480) không dịch chuyển (|d| ≤ 3). Dựng: tịnh tiến dọc (CSS `translate`, không đè GSAP) cột trái `t0,t4,t6,t8,t11` và cột phải `t3,t5,t7,t12`
theo khoá trên; thẻ trôi khỏi đáy cụm thì ra ngoài khung, thẻ mới vào từ đầu cột như đã nêu ở trên.

**s03: cột hạt dọc và vệt dọc (f13–f23).** Tự tương quan x của hạt dưới thẻ GSAP: khoảng cột 104–105px (= 4×26), khoảng hàng 39px ⇒ sau khi hạt kéo về chữ, chỉ còn 1 cột lưới trên 4 (i%4==2) và giữ nguyên sóng dy/dx ⇒ cột chấm dọc; 3/4 số cột về chữ GSAP (bản trước giữ 45% hạt ở mọi cột nên thành hàng ngang).
Vệt dọc xám đo từ thành phần cao ≥250px, rộng 6–40px: x = 0 (w9), 64 (w36), 500 (w28), 595 (w30), 671 (w13), 915 (w12), y từ ~1300–1430 tới 1780–1920, màu `#a7a39b`, đậm dần 0.15 → 0.96 ở f19 → f23, hết ở f24; thêm vệt cam nhạt x=741 (w36, y 700–1360) ở f23–f24 (thay cho 6 vệt đặt tay).
Lưới xám 78px (cùng pitch với gợn sóng) có từ f24: tâm ô tối hơn khe 27/22 (f24–25), 9.5, 12.9, 12.9, 12.7 (f26–29), 18, 20, 25, 26 (f30–33), trung tính (không cam) ⇒ vẽ ô xám 46px bo 9 `#cfc9bf`, độ đậm 0.24 → 0.65 rồi mờ khi cam tới (f36).

**s03: gợn sóng halftone cam (f31–f41).** Lưới ô vuông bo 78px (pha x=24.7+78i, y=20.2+78j), màu lõi `#c4430c`; ô KHÔNG dịch chuyển (|d| < 1px/khung), chỉ đổi cỡ (±4–8px/khung) và độ đậm.
Độ đậm (r−b tại tâm ô, 12→180) tăng đồng loạt theo mọi x: f34 .20, f35 .36, f36 .52, f37 .67, f38 .78, f39 .88, f40 .97. Cỡ ô theo bán kính từ tâm (540,950): nền 14px, gờ sóng +14px (σ≈170) ở 540 + 120·(F−34) px,
mặt sóng (ô bắt đầu hiện) ở 870 + 130·(F−34) px, sóng thứ hai từ f37 (đỉnh +34px ở f40, bán kính 250 → 540 từ f37 → f41). Thêm các vòng cam nhạt dày ~34px (đỉnh phổ bán kính của điểm ảnh cam nhạt): hai vòng gần đứng yên ở ~450 và 510→550,
một vòng lan 270 → 370 → 470 → 650 → 810 → 930 → 1070 (f31–f37). Thay cho lưới 54px trượt từ đáy lên của bản trước (không có số đo). Độ đậm ở hàng dưới khớp gốc trong ±15 (r−b: gốc 45,72,100,125,135 → remake 54,83,107,133,150 ở f34–f38); độ đậm các vòng dày (alpha 0.25) chưa đối chiếu lại sau khi hạ.

**s07: lưới halftone.** Lưới 36×36 px, ô vuông bo ~7px, cạnh ô ~34px (khe 2–3px). Đám chấm f1–f16: ô xoay ngẫu nhiên mỗi khung. Ô đứng riêng không có (chồng lấn), nên đo độ tập trung hướng cạnh R của 4θ (R = sin(4A)/(4A) cho xoay đều ±A) trên vùng y 500–1700: f1–f2 ±35°, f3–f4 ±28°, f5 ±31°, f6–f12 ±39–44° (R 0.03–0.14), f13 ±35°, f14 ±33°, f15 ±31°, f16 ±30° (f13–f16 lẫn cạnh của vòng nên là cận trên).
Đo bằng góc đỉnh ô (f17–f26): ô BÊN TRONG đĩa đen thẳng hàng (độ lệch chuẩn 0–1°), ô BÊN NGOÀI mép đĩa lệch chuẩn 22–29° (≈ ±43° đều) ở f17–f22 rồi 7–8° ở f24–f26 ⇒ nhiễu xoay chỉ áp cho ô ngoài đĩa: ±43° tới 0.7s, giảm tới ±12° ở 0.767s, hết ở 0.9s.
(Nhiễu dịch ±4px và co ±8% ở bản trước không có số đo: đã bỏ.)
Đĩa đen đo từ mép trên/dưới/trái/phải ở x=540 / y=960: bán kính f17–f26 = 28, 126, 210, 305, 423, 490, 525, 561, 606, 646 px, tâm dọc trôi xuống 962 (f20) → 1011 (f22) → 1107 (f24) → 1196 (f26) → ~1300 (f28),
mép trên đứng ở y≈550; đĩa phủ kín ở f27–f28 (bản trước đen kín ở f24–f25). Remake sau sửa: mép dưới 1493, 1578, 1670, 1760, 1848 (gốc 1494, 1580, 1668, 1763, 1843).
Mặt quét làm sáng (mép trên khối đen): bắt đầu ở mép trái f28, chạy xuống 150 px/khung (≈4500 px/s), trễ dần sang phải (x=980 bắt đầu ở f31 ⇒ mép nghiêng −0.5 px/px); ô sau mặt quét xoay ~38° (hình thoi);
lưới đen-cam xuất hiện theo thời gian toàn cục, quét từ trên xuống trong ~2 khung (gốc f34 → f36). Cung trắng 9.1s (f37–f39): dải dày ~76px, đoạn trái nằm ngang rồi dốc −0.35, tụt 152 px/khung (y trái 1628 → 1780 → ~1930), dài ra sang phải (đầu phải x≈870 → 1050).

### Kết quả cổng (trước → sau)

| Cảnh | SSIM | Tỉ lệ biên độ | Cửa sổ 0.2s kém nhất |
|---|---|---|---|
| s02 | 0.273 → 0.315 | 0.55 → 0.90 ĐẠT | 0.04 → 0.59 ĐẠT |
| s03 | 0.273 → 0.343 | 0.46 → 0.70 CHƯA | 0.32 → 0.32 (3.6s; CHƯA) |
| s07 | 0.343 → 0.401 | 0.53 → 0.92 ĐẠT | 0.37 → 0.61 ĐẠT |

s02 và s07 đạt cổng. Các cảnh khác: file `.mov` không đổi (md5), `joins.json` không đổi.

### Còn thiếu (đã đo)

- **s03 (tỉ lệ 0.70; cửa sổ yếu nhất 0.32 ở abs 109–114 = f27–f32, cửa sổ 3.5s 0.49 ở f23–f27):** f27–f32: remake đứng yên trong khi cụm gốc còn lắng — thẻ logo xoay thẳng và dịch, thẻ quanh chạy, logo tô xám→trắng (chưa đo, chưa dựng). f23–f27: gốc dàn năng lượng ~50 ở ba khung abs 104–106 (49.8 / 49.8 / 48.0); remake 26.6 / 59.1 / 28.2 (một khung bùng rồi tụt) và vùng dưới (y>1500) gốc 52 / 44 / 27 so với 20 / 12 / 4.
  Nguyên nhân chưa dựng được: (1) bám thẻ f23 thất bại (NCC < 0.5) nên không có quỹ đạo từng thẻ trong 3 khung bay vào, chỉ có độ lệch ở f24/f25; không đo được xoay ±15° của từng thẻ; (2) ô xám 78px hiện ở f23 đồng loạt, (3) nhiều vòng dày đồng tâm quanh logo.
  Sau f27 gốc còn dao động nhẹ ở cột trái/phải (21–33/khung ở f27–f30) mà remake đứng yên.
- **s03 SSIM** thấp hơn lần trước (0.351 → 0.343) sau khi thẻ hiện theo số đo: vị trí/xoay từng thẻ vẫn lệch so với gốc.
- **s02:** đường kính vòng nan robot (198 / 279 / 319 / 346 / 352 px ở f24–f28) và góc xoay ~30° chỉ là ước lượng bằng mắt trên ảnh cắt; phép đo số bị thẻ che nên chưa có số. Màu đỏ robot đo được không thiếu (xem trên).
- **s07:** mép mặt quét gốc cong (nửa trái phẳng hơn), remake là đường thẳng; khe giữa các ô ở khung đen kín remake 1–2px, gốc 3px.

## Hộp 3D (mục 4: s08, s09)

Đo từ khung 30fps của `source.mp4` (khung file f01 = đầu cảnh; t cảnh = (f−1)/30; s08 lấy 4.4s để có cả post, f115 của s08 = f01 của s09). Script đo lặp lại được: `measure_cube.py` (lệnh `cam`, `track`, `back`, `tail`, `tail2`, `overlay`, `shade`, `shadow`, `export`; đầu file ghi cách chạy).
Mô hình: hộp lập phương + camera phối cảnh khớp thẳng với CSS (`translate3d · rotateZ · rotateX · rotateY` trên phần tử `preserve-3d`, `perspective` ở cha). Mỗi khung khớp 6 tham số (x, y, z, rx, ry, rz) bằng mất mát "hằng màu":
mỗi mặt nhìn thấy phải phủ vùng cam MỘT sắc, nắp phủ vùng trắng, vùng cam ngoài hình chiếu bị phạt; kiểm bằng `overlay` (hình chiếu chồng khung gốc). Kết quả từng khung: `cube_track_s08.json` (cam: `cube_cam.json`).

### Số đo và cách dựng

**Camera và hình hộp.** Khớp chung trên 9 khung (f36…f108): `P = 1621` px (khoảng cách camera; = CSS `perspective`), cạnh hộp 600 × 605 × 593 (hy/hx = 1.008, hz/hx = 0.988 ⇒ lập phương 600, sai ≤1%).
Tâm phối cảnh cố định (540, 960): để tự do thì trôi tới oy 580–630 và lẫn với `y`/nghiêng X. Bản cũ dùng `perspective: 2100px` và hộp 600×500×480 (không phải lập phương) ⇒ sai dáng và phối cảnh ⇒ SSIM thấp.
Hộp đứng ở z ≈ −350 (tỉ lệ ảnh 0.82), x ≈ 0, y ≈ +5 so với (540, 960), KHÔNG chạm đất (lơ lửng trên bóng).

**Tư thế theo thời gian** (độ; ry bám liên tục nên đúng thứ tự mặt SCROLL → SCRUB → GSAP → PIN → SCROLL, kiểm bằng mắt ở f72 SCRUB, f78 GSAP, f87 PIN):
- f30–f52: đứng yên ở SCROLL: rx −21.6, ry −29.7 → −27 (PIN lộ bên phải), rz −10.8 → −10.
- f53–f87: quay ry −23 → +270 (SCRUB f72 ≈ 99, GSAP f78 ≈ 183, PIN f87 ≈ 270), đỉnh vận tốc 23°/khung (f76–f77), rx −24.7 (f60) → +8.4 (f75) → −8 (f90), rz +21 (f69–f72) → −8 (f87).
- f88–f105: ry 289 → 332 (SCROLL, giảm tốc: +17, +13, +9, +4 độ mỗi 3 khung), rx −8.4, rz −3.7; f105–f112 đứng yên (332–334).
- Bản cũ: đứng yên tới 2.0s rồi quay đều ry 15° → 346° (`ease: none`) với nghiêng X cố định −20 — thiếu cú ngoặt đầu, không có đổi rx +8, rz ±21.

**Màu mặt (PHẲNG, không có ánh sáng).** Mỗi mặt một màu hằng: SCROLL `#c23f0c` (194,63,12), PIN `#882c07` (136,44,7), GSAP `#97340d` (151,52,13), SCRUB `#71280a` (113,40,10) — 63/61/13/15 mẫu, 0 mẫu khác màu. Mặt PIN vẫn 136 khi quay thẳng ra trước (n_z = 0.85) ⇒ không phải Lambert (hồi quy tuyến tính theo pháp tuyến cho sai số chuẩn 18.2 mức, Lambert phi tuyến ~16).
Nắp trắng `#ffffff` kèm băng keo `#2d2a25` rộng 17.7% bề sâu nắp, cách mép xa 39.6% (đo f60 qua ánh xạ đồng phẳng); đáy xám `#a19e9c` (mặt đáy chỉ thấy lúc ráp và lúc hộp bay lên).
Viền đen `#211b12` dày 6 px ở tỉ lệ 0.82 ⇒ 7 px CSS (như bản cũ). Chữ trắng trên mặt: Anton, nghiêng −6° như bản cũ, chưa đo lại cỡ.

**Cú phình 10.067–10.10s (f27–f28).** z (tư thế khớp): f26 −364, f27 −186, f28 −213, f29 −308, f30 −334 ⇒ tỉ lệ ảnh so với f30: 0.985, **1.082**, 1.066, 1.013, 1.0 (đỉnh +8% so với f30, +10% so với f26, ở f27; hồi trong 2 khung). Bản làm lại có sẵn trong bảng tư thế (không làm riêng).

**Bóng, vòng quỹ đạo, thanh trượt, tay cầm và bộ đếm.** Bóng elip ĐỨNG YÊN (không bám hộp): lõi tối x 245–830, y 1320–1377 (kể cả mờ y 1307–1383) từ f24 tới f116 ⇒ `left 240, top 1311, rộng 600, cao 72, blur 8` (bản cũ 520×80 ở y 1300–1380). Từ f117 (13.067s) trôi lên: mép trên bóng (s09 f1, f3, f4, f13, f14, f15, f17, f19, f20, f21, f22) = 1308, 1284, 1229, 646, 579, 513, 378, 245, 178, 112, 45 (thẳng ~−66.8 px/khung = −2005 px/s) ⇒ dy = −23 (f3), −78 (f4), −661 (f13), −1262 (f22), ra khỏi khung ở f23 (13.73s). Khớp mẫu từng khung (cột x 1000–1080, s09 f3–f23) cho thanh trượt đỏ/tay cầm: −53, −57, −61, −64, −66 px/khung rồi đều −66.7 (cùng bảng với bóng) và bộ đếm chữ "scrollY 3270" (đứng ở 3270 từ f117; 3138, 3178, 3222 ở f114–f116) cũng thế. s08 hết ở 13.6s (joins.json cố định) nên s09 vẽ tiếp cùng một phần tử (`#grd`: bóng + vòng + thanh/tay cầm/bộ đếm) từ 13.6s tới 13.8s, cùng bảng dy (liên tục ở 13.6s: −1037 px). Sau khi dời bảng +0.0125s (lần đầu bóng cao hơn gốc ~25 px), mép trên bóng remake: 1317 (f1), 1289 (f3), 645 (f13), 578, 512, 245 (f19), 179, 112, 45 (f22) so với gốc 1308, 1284, 646, 579, 513, 245, 178, 112, 45 — khớp ≤1 px từ f13, +5/+9 px ở f1/f3 (đang đứng/bắt đầu). Đỉnh năng lượng 1/3 khung trên (gốc 26, 24, 21, 20, 17, 21, 20, 15 ở 13.53–13.77s; remake 15, 30, 12, 13, 13, 19, 18, 13) không còn "≈1".
**Tay cầm thanh trượt**: tâm vòng đen gốc (x 1028–1064) = 834 (f50), 1128 (f80), 1324 (f100), 1442 (f112), 1464 (f114), 9.84 px/khung; bản cũ chạy xuống 1545 (lệch 73–91 px): sửa thành tâm y = 834 + 295.2·(t − 1.633) Reviewer đo lại trên remake: lệch ≤ 8 px ở f40, f60, f80, f100, f112, f115; lúc bay lên (f117–f121) chạy trước gốc 30–46 px vì dùng chung bảng `GD` với bóng và quỹ đạo (khoảng hụt).

**Bay lên + phóng to (post, f113–f131; 13.1–13.57s).** Chuẩn so sánh là CẠNH ĐÁY MẶT TRƯỚC (hàng thấp nhất của vùng cam sáng liên thông lớn nhất, ảnh 1080×1920, hàm `front_masks`) đo trên ảnh gốc VÀ ảnh remake bằng cùng một hàm. Gốc (f112 → f131): 1292, 1273, 1244, 1192, 1100, 972, 916, 858, 796, 730, 696, 630, 562, 496, 430, 362, 296, 230, 162, 96 — nhanh dần 25, 29, 52, 92, 128 px/khung rồi ĐỀU ~66 px/khung (≈1990 px/s) từ 13.1s, hộp rời khung lúc ~13.57s.
Lần khớp IoU đầu (`tail2`) trông khớp bằng mắt nhưng cạnh đáy lệch 120–270 px (remake cao hơn gốc, gần đứng yên ở 13.1–13.17s, rời khung sớm ở 13.45s): nhận xét "hình chiếu khớp bằng mắt" ở bản trước là SAI, đã bỏ. Bản này: `tail3` (IoU mặt trước/mặt bên + sai lệch cạnh đáy), rồi `ybottom` (f112–f114 giữ tư thế chỉ giải y; f115–f116 nội suy giữa f114 và f117 rồi giải y; f129–f131 giữ tư thế f128 rồi giải y), rồi `closeloop` (so [đáy, trái, phải] của mặt trước giữa gốc và remake đã dựng rồi dời x, y, z; hai vòng dựng–đo).
Kết quả đo lại trên remake (đáy, px): f112–f131 = 1288, 1279, 1254, 1184, 1082, 960, 906, 844, 768, 710, 696, 631, 562, 492, 428, 362, 298, 230, 160, 90 so với gốc ở trên: lệch ≤12 px ở 15 trong 20 khung (remake − gốc); lớn nhất f120 −28, f121 −20, f116 −18, f119 −14, f118 −10; mép phải mặt trước lệch ≤20 px từ f113 (f108–f110: remake rộng hơn gốc ~30–46 px — tư thế f≤112 chưa chỉnh, xem Còn thiếu). Dấu "mất mát null" trong `cube_track_s08.json` = f112–f116 và f129–f131 chỉnh theo số đo ảnh, không phải mất mát tự khớp; f132 không có số đo (hộp rời khung), `export` ngoại suy theo bước y của hai khung cuối.
Độ rộng/diện tích vùng cam KHÔNG so được (chữ marquee lớn che phần trên mặt trước ở gốc và ở remake khác nhau): dùng đáy/trái/phải, không dùng đỉnh.
Chuyển động này thay cho `scale 1.8 / 1.6 + y −1100` của bản cũ.

**Chữ SCRUB lớn (s08) mờ đi.** Độ đục α (trung vị kênh G của điểm ảnh cam so với nền kem/đỏ #c9451c) ở gốc: 1.0 tới f109, 0.93, 0.71, 0.58, 0.47 (f110–f113), mờ nốt tới 0 ở f117 (f114–f116 nội suy tuyến tính theo bóng mờ thấy được). Bản cũ để 0.55 rồi BẬT LẠI ở f117–f119 (hai tween chồng lên nhau): sửa bằng một bảng độ đục.

**Xám phủ hộp lúc post (s09, `#shade`)**: độ sáng nền ở 3 điểm sạch (20,200), (1060,200), (1060,1000) = 237, 239, 213, 188, 162, 149, 138, 134, 129, 128 (s09 f1–f10) ⇒ GIẢM ĐỀU, không chớp; α = (239−v)/221 = 0, 0.11, 0.24, 0.33, 0.41, 0.46, 0.48, 0.50. Kiểm trên remake dựng ra (cùng 3 điểm): 224, 232, 213, 186, 165, 147 so với gốc 237, 239, 213, 188, 162, 149 ở f1–f6 (lệch ≤3 từ f3); mốc α được dời +0.025s so với dãy gốc vì lần dựng đầu chạy sớm ~1 khung (đo ảnh). (Lần đo đầu một điểm ở góc phải-dưới cho dãy 145, 183, 165… "chớp": sai, điểm đó bị vật khác che.)
**Cửa sổ terminal (s09, `#term`)**: rộng (vùng `#141210`, px) f3–f12 của s09 = 598, 688, 756, 805, 854, 870, 877 (đỉnh f9), 877, 870, 860 ⇒ tỉ lệ so với bản cũ (833 px): 0.72 → 0.83 → 0.91 → 0.97 → 1.02 → 1.045 → 1.05 (f9–f10) → 1.0 trước 0.5s (bản cũ: mờ vào ở 0.94 → 1).
**Nền tối quét lên (s09, `#dark`)**: mép trên đo MỘT cách cho cả đoạn (cột x 15–95, độ sáng trung bình 15 hàng < 105, quét từ đáy lên; s09 f3–f31): đi lên ĐỀU, y = 2128.9 − 66.83·f (f = số khung s09; sai số lớn nhất 14 px) = 2062 − 2005·t: 1920 lúc 0.071s, tới đỉnh lúc 1.029s (gốc: 1914, 1861, 1797, … 1462 (f10), 1261 (f13), 1128 (f15), 929 (f18), 661 (f22), 323 (f27), 56 (f31)). Bản cũ: 4 đoạn đặt tay (một số theo power1.out) rồi dừng ở 480 lúc 0.6–0.75s: sớm tới 0.05s ở 0.3–0.5s, sớm hơn nữa ở 0.6s. Dựng một tween tuyến tính dời +0.019s (38 px) vì cùng hàm đo trên remake lệch −38 px so với phương trình; đo lại remake: 1920, 1867, 1798, 1731, 1663, 1595, 1528, 1461 (f3–f10), 1128 (f15), 928 (f18), 327 (f27) — khớp gốc ≤7 px.

**Ráp hộp (f1–f17).** Chỉ khớp được thân hộp từ f18 (fit mất mát 0.46–0.7 vì nắp còn hở); trước đó 6 tấm bay rời. Giữ cách dựng cũ (6 tấm bay vào từ xa, `back.out`, đến lúc 0.57s = f18), tăng biên độ bay (×2.6 vị trí, ×9 góc, +700 px độ sâu) để năng lượng chuyển động đạt cổng, tấm đáy (xám) tới trễ ở 0.85s (thấy dải xám dưới mặt trước ở f19–f26 của gốc), nắp bản lề khép 0.73–0.83s (như cũ, bản lề dời theo hộp 600). Lưới halftone của `#cover` (đầu s08) xoay ngẫu nhiên mỗi khung với biên độ ±A đo ở s08 f1–f10 (`measure_cube.py jit`, cùng cách đo `jit` của s07): 34, 39, 41, 38, 41, 36, 34, 31, 30, 32° (f8–f10 lẫn cạnh của tấm bay vào nên là cận trên).
**Mã dựng**: `scenes/s08/index.html`: `CP` (bảng t, x, y, z, rx, ry, rz mỗi khung f18–f132, làm trơn 3 điểm trừ f26–f30 và f113+), `cubePose(t)` nội suy tuyến tính, `setCube()` gán `transform` CSS — một tween `TP.t` 0 → 4.4s (`ease: none`) nên là hàm thuần của thời gian, seek an toàn (render hai lần cho cùng md5 từng khung).

### Kết quả cổng (trước → sau)

| Cảnh | SSIM | Tỉ lệ biên độ | Cửa sổ 0.2s kém nhất |
|---|---|---|---|
| s08 | 0.307 → 0.373 | 0.85 → 0.868 ĐẠT | 0.50 (9.3s) → 0.504 (9.3s) |
| s09 | 0.443 → 0.478 | 0.82 → 0.826 ĐẠT | 0.53 (15.3s) → 0.531 (15.3s) |

Các cảnh khác: file `.mov` không đổi (md5), `joins.json` không đổi; ảnh J07–J09 cùng kiểu chuyển/hướng/nhịp với gốc; `hyperframes check` s08 và s09: 0 lỗi, 0 cảnh báo. (SSIM s10–s14 lệch ở chữ số thứ 5 giữa các lần ghép vì x264 của `remake.mp4`, file `.mov` các cảnh đó không đổi.)
Lịch sử: bản sửa vòng 1 để s09 ở 0.7985 (CHƯA); cổng đạt lại khi sửa theo số đo (nền tối đi lên đều ~2000 px/s thay vì dừng ở 480, hộp và bóng/vòng/thanh trượt bay lên đúng nhịp ~66 px/khung đến 13.8s), không thêm chuyển động nào không có ở gốc.

### Còn thiếu (đã đo)

- **Ráp hộp f1–f17**: chưa đo từng tấm (6 tấm tư thế riêng, nắp hở, tấm đáy); biên độ và thời điểm tới chỉ đặt theo năng lượng chuyển động và dáng ở f11–f17. Tư thế thân hộp f18–f25 chỉ khớp tạm (mất mát 0.46–0.7).
- **Bay lên f113–f131**: tư thế tự khớp (IoU) không đủ tin (mất mát 0.23–0.33 ở f117–f128, bị chữ khổng lồ và terminal che); cạnh đáy mặt trước đã được chỉnh bằng vòng kín nên khớp ≤12 px ở 15/20 khung, lệch lớn nhất f120 −28, f121 −20, f116 −18 px; chưa khớp độ rộng/diện tích mặt trước (bị chữ che) và tư thế f108–f112 (mép phải mặt trước remake rộng hơn gốc 30–46 px ở f108–f110). Màu mặt đáy xám khi bị phủ xám chưa đo riêng.
- **Cửa sổ terminal ở f3 của s09** hơi nghiêng phối cảnh (gốc), bản làm lại chỉ co giãn đều.
- **s09 cuối cảnh**: thẻ PIN cam / SCRUB đen là thẻ phẳng (không phải khối 3D), giữ nguyên; năng lượng 15.3–15.8s của s09 vẫn hụt (gốc 8–9, remake 4–5: bộ đếm px, nhịp con trỏ) — ngoài mục này.
- **s08**: nhãn lớp (far/mid/near/…) mất sớm hơn ở gốc; chữ SCRUB lớn mờ dần tới f117 (gốc còn chữ mờ ở f114–f116); bộ đếm scrollY f108–f114 cao hơn gốc 52–60 và lùi một bước ở f115 (3191 → 3178); lớp xám s09 nhạt dần về 0.40 lúc 0.6s trong khi gốc giữ 0.50; khung lệch nhất của cạnh đáy hộp là f120, 32 px; nền kem của remake sáng hơn gốc; cửa sổ 0.2s 9.3s (0.50) nằm sát ngưỡng vì lưới halftone s07 (mục 2/3), không phải hộp.
- Cỡ và nghiêng chữ trên mặt hộp chưa đo lại.

## Morph (mục 5: s06, s15)

Đo từ khung 30fps của `source.mp4` (s06: `-ss 6.7 -t 1.3`, s15: `-ss 28.4 -t 2.2`; file f01 = đầu cảnh; kiểm: khung 855 của `compare.mp4` = f04 của s15, 856 = f05) và của `preview/remake.mp4` cùng cách. Script đo lặp lại được: `measure_morph.py` (lệnh `energy`, `regions`, `shape`, `table`, `chord`, `ghost`, `gstack`, `grow`, `band`, `rows`, `reveal`, `blur`, `box`, `logo`, `boil`, `iou`, `gfit`; đầu file ghi cách chạy).
Mô tả nhiệm vụ gọi s06 là "tường chữ SplitText" và s15 là "chữ G nghiêng + viền ma"; thực tế cả hai cảnh đều là hình cam morph (tròn → sao → blob → vuông → chữ G) với viền ma; tường chữ SplitText chỉ nằm ở f1–f3 của s06 (xem Còn thiếu).

### Số đo và cách dựng

**Trước khi sửa.** s06: tỉ lệ 0.77 (gốc 12.38, remake 9.49), cửa sổ kém nhất 6.9s (0.68), SSIM 0.674. s15: 0.70 (gốc 16.67, remake 11.66), 30.1s (0.16), 30.0s (0.26), 29.8s (0.27), SSIM 0.469.
`energy` (|khung(t) − khung(t−1)| xám 270x480, tách theo lớp: vùng cam / nét tối / còn lại) cho thấy thiếu hụt nằm ở hình cam và nét tối (viền hình + bóng ma), không ở tia nền.

**Hình đứng yên trong bản cũ, rung từng khung ở gốc.** `shape` (mặt nạ cam, mở 9px bỏ nét mảnh): ở gốc rộng/cao đổi mỗi khung vài px quanh vị trí giữ (s06 sao f11–f18, rộng×cao: 745×703, 745×702, 783×729, 796×744, 759×719, 747×705, 746×703, 750×707: một nhịp phình ở f13–f15, +3–6%, còn lại ±1%; vuông f26–f30 cao 775, 751, 747, 768, 803 px), bán kính biên đổi tới 95 px giữa hai khung lúc đổi hình (`boil`). Bản cũ: diện tích cam giữ nguyên tới 7 chữ số trong mọi khoảng yên (f10–f18, f26–f29, f33–f36).
**Một đoạn morph dùng ở cả hai cảnh.** Chiều cao hình theo khung của s15 f24…f57 trùng s06 f5…f38 (lệch đúng 19 khung): tròn 763/845/805/785/781 so với 763/847/805/787/783, sao 716…707 so với 723…707, vuông f42–f50 802…766 so với f23–f31 805…766, G f52–f57 809…806 so với f33–f38 805. Tâm hình ở s15 là x 267 (giữa cột trái 534px) = tâm s06 540 − 273 (`chord` hàng y 620: tâm 266–276), cột trái cắt hình ở mép nên chỉ đo được chiều cao (dùng `table … u`: hợp mọi mảnh vì hộp lời nhắc cắt hình). Mốc chuyển đổi hình: s15 f28→f29 (tròn → sao), f37→f39 (sao → blob), f41→f42 (blob → vuông), f50→f52 (vuông → G).
**Dáng hình.** `gfit` (đa giác tham số co giãn về bbox gốc, IoU, nét 9px tính vào): chữ G f33–f34 khớp 0.865 (bản cũ 0.747): vòng ngoài 391×404, trong 164×224, bậc x 5 y −19 góc 29°, đầu mút −28.5°, nghiêng 0.209 (bản cũ a 330 b 430 ai 175 bi 280: vòng mảnh, diện tích −17%); sao f11–f12 khớp 0.93 với R 460, r 213, dịch xuống 41 (bản cũ R 450 r 215: diện tích +34%).
**Bóng ma** (`ghost` ở cột x 330 và 750, `gstack` quét 5 cột theo bề rộng hình; khoảng cách từ mép trên mặt nạ cam tới nét ma): khi hình là sao (s06 f15–f18, s15 f34–f37 cho cùng số) là chồng 5 nét xen kẽ đen/cam CÁCH ĐỀU 50 px và ĐỨNG YÊN so với mép hình: 261/199/149/100/50, 251/200/151/102/52, 250/200/151/102/52, 248/198/149/100/51 (±3 px giữa các khung, cột 330 và 750 chênh ≤ 4 px ⇒ chỉ dịch dọc, không dịch ngang). Chồng dựng dần f11 → f15 (1, 2, 3, 4, 5 nét: 64/214, 53/112/257, 46/95/155, 43/93/142/200), sụp ở f19–f20 (48/96/145/189 rồi 53), từ blob/vuông/G chỉ còn 1 nét cách 38–66 px (f21–f31: 42–66; f33–f36: 38–86). Nét dày 5–9 px.
Dựng: bảng khoảng cách theo khung `GH` trong `shared/morph.js` (`Morph.ghost(f)`, s15 tra cùng bảng với f − 19); mỗi bóng là bản của hình HIỆN TẠI (cùng bbox từng khung) dịch lên đúng khoảng đó, nét 5px đen/cam xen kẽ từ nét gần nhất (đen). Trừ 5 px vì remake đo từ mặt nạ cho khoảng lớn hơn 5 px (đo lại f15–f18 x 330: 256/206/157/108 → sau trừ 251/201/152/103/54 so với gốc 251/200/151/102/52). Bản trước dựng bóng ma 20/54/95/150/250 px sang trái 3–20 px, mỗi bóng là hình ở 2/3/5/7/9 khung TRƯỚC: độ trễ đó chọn theo `energy` (chính chỉ số của cổng) nên đã BỎ.
**Bóng ma loe ngang** (`grow` quét theo HÀNG, s06 f16–f17): ở hàng y 1100 khoảng cách từ mép trái hình tới nét ma là 19/51/82/114/146 px (cách nhau 32) còn bên phải 15/27/38/51/63 (cách nhau 12 — đúng như dịch dọc thuần: remake chỉ dịch dọc cho 5/17/29 bên trái và 16/27/39 bên phải); ở hàng y 700 và 800 phần trải ngoài cùng của gốc là x 38–986 và 116–946 so với 160–920 và 162–920 của remake chỉ dịch dọc (bbox ma toàn cảnh x 0–1033). Mô hình: nét thứ j (0 = gần nhất) của chồng sao giãn ngang 5%·(j+1) quanh tâm hình và dời trái 5.6 px·(j+1) (ngoài cùng ×1.25, −28 px; `Morph.ghostW`), chỉ cho chồng ≥ 3 nét; các hình sau (1–2 nét) chưa đo ngang nên không giãn. Kết quả đo lại trên remake: hàng y 1100 trái 19/50/80 px (cách nhau ~31, 3 nét đầu thấy được), phải 21/38/56 (gốc 15/27/38: cách nhau 17 so với 12); hàng y 700 trải x 86–959 (trước 160–920, gốc 38–986), y 800 x 138–933 (gốc 116–946); bbox ma toàn cảnh x 36–986 (gốc 0–1033). Hai nét thừa ở cột 330 (~81 và ~30 px) đã hết.
Chưa khớp: nét ma ngoài cùng bên trái chưa tới x 0 như gốc (36 so với 0, 38 so với 86 ở hàng 700), bên phải khoảng cách cách nhau 17 px thay vì 12; năng lượng f16–f18 của s06 vẫn cao hơn gốc (tổng 6.3/3.1/4.1 so với 4.2/1.9/2.5) nhưng phần vượt nằm chủ yếu ở lớp "còn lại" (tia nền, chip, phụ đề: 3.81/1.76/2.11 so với 2.49/1.51/0.59), không phải ở bóng ma (lớp nét tối 1.91/1.00/1.38 so với 1.52/0.14/1.27, vùng cam 0.60/0.32/0.61 so với 0.23/0.20/0.60); tia nền của s06 (bảng RAYU, chip) không thuộc mục này.
**Quạt tia ở s15**: gốc có quạt tia nền như s06 ở cột trái (tâm 267, 1000), nhảy theo cùng bảng RAYU; bản cũ không có. Thêm theo bảng đã đo của s06 (không đo lại biên độ).
**Chấm cam của s15** (`#ldots` bản cũ đặt ở CỘT TRÁI, 46px): đo mặt nạ cam vùng x 0–534, y 1600–1900 f12–f49 của gốc = 0% mọi khung nên bỏ; chấm có thật nhưng ở CỘT PHẢI (`#rdots`): lưới 60 px (tự tương quan: chu kỳ 60 ở cả x và y), tâm x địa phương 59 mod 60 và y tuyệt đối 33 mod 60 (gấp mặt nạ cam f24–f27), nằm dưới thẻ và thẻ đen; độ phủ cam vùng x 540–1080, y 1520–1900: 0.3, 1.6, 4.1, 6.3, 7.8, 8.7, 9.2 % ở f20–f26, rồi 8.7, 7.5, 3.5, 0.6 % ở f27–f30, bật lại 0.5, 1.2, 1.8, 1.2, 0.6, 0.1 % ở f31–f36. Dựng: chấm bán kính 13 px, độ đục theo bảng `RD` (độ phủ chuẩn hoá theo đỉnh f26). Bán kính suy từ độ phủ các mảng không bị thẻ che (~17–20%): chưa đo từng chấm.
**Cột phải s15, vào cảnh và thẻ đen.** (1) Nội dung vào ở khung f5 (28.533s = tl 4/30; `tl.set` trước đặt 0.1334 nên vào muộn một khung: năng lượng f5 gốc 12.5, remake 0.0 → 18.6 sau khi sửa ở 4/30 − 1e-4; J14: khung 855 gốc = f04 trống, 856 = f05 có dải cột phải; remake khớp từng khung). (2) Thẻ đen "layout" KHÔNG trượt từ phải mà nở ra từ mép trái cột phải (x 538): thành phần đen lớn nhất (`band`): f23 rộng 81, f24 225, f25 381, f26 516, f27 541 (tới mép), cao dưới 1255 → 1307 → 1361 → 1409 → 1447 → 1474 → 1489 → 1498 → 1503 (f23–f31), mép trên 1102, 1028, 1022 rồi 771, 719, 686, 665, 651, 644, 642 (f23–f32); bản cũ trượt cả cột B từ phải ở f26–f36 (diện tích đen trễ 3–4 khung). Dựng: `clip-path` của `#band` theo bảng `BC` (hàm thuần của khung). (3) Chữ "layout" lớn đứng yên tới f30 rồi nhoè + mờ trong 3 khung, không trượt -140 px như bản cũ: `blur` (vùng x 560–1070, y 400–640; độ nét chuẩn hoá theo f26 | độ phủ tối) f28–f34 = 1.09, 1.11, 1.07, 0.91, 0.34, 0.12, 0.10 | 24.7, 24.7, 24.5, 16.1, 2.4, 0.0, 0.0 % ⇒ dựng bước: mờ 66% + nhoè 1px ở f31, 10% + nhoè 5px ở f32, hết ở f33 (bản trước mờ tuyến tính tới 40% trong f31–f34). (4) THÊM BỚT: gốc hiện từng chữ trồi lên từ đáy mặt nạ ở f35–f39 (độ phủ điểm tối vùng x 560–1070, y 400–640: 0 ở f33–f34 rồi 2, 5, 12, 13, 17 % ở f35–f39), mỗi chữ trễ 1 khung; bản cũ trượt vào cùng thẻ từ f26 (độ phủ 44–45% từ f31 khi gốc còn 0–2%, sớm khoảng 9 khung). (5) Logo GSAP và Motion, chip `gsap.timeline()`: ƯỚC LƯỢNG đọc bằng mắt từng khung (không phải số đo tự động): f52 (1.70s) mờ ~35% nhỏ ~55% (80 px), f53 65%/79%, f54 90%/92%, f55 đủ (GSAP 146 px tâm (205, 1242), Motion 160 px tâm (876, 1241)), chip hiện từ f53; sai số cỡ ±10 px, ±10% độ đục; bản cũ hiện ở f58, 134 px, lệch tâm. Đối chiếu bằng `reveal` (|khung f − khung f57| / |khung f50 − khung f57| trong khung ô logo; âm ở f52–f53 vì logo mờ xám khác nền cam hơn cả logo đủ): GSAP −0.05, −0.24, 0.25, 0.69, 0.90, 1.00 và Motion −0.01, −0.22, 0.28, 0.73, 0.93, 1.00 ở f52–f57, chip 0.05, 0.05, 0.17, 0.36, 0.55, 0.72, 1.00 ở f52–f58: bắt đầu đổi ở f51–f52 như đã dựng nhưng chỉ ổn định ở f57 (độ sáng/cỡ còn đổi sau f55), nghĩa là bảng dựng (đủ ở f55) sớm hơn đường cong này khoảng 1–2 khung; chưa chỉnh lại. (6) Hàng bảng Tasks (`rows`: thành phần trắng trong cột phải, cờ cắt trái/phải của mép cột 542 px): hàng gốc có chiều rộng CỐ ĐỊNH ~470 px (bản dựng CSS 300 × 1.55) và chỉ TRƯỢT NGANG, bị mép cột cắt; "chiều rộng 418 → 134 → 270" ở lần đo trước chỉ là phần nhìn thấy — bản trước co hàng lại nên icon đè chữ ("an✓at", "in✓ia", f29–f58). Mép trái thật L = x1 − 470 khi bị cắt trái ("ate ✓", "utId ◯"), L = x0 khi bị cắt phải; riêng `exit` x0 = 405 là chỗ hộp lời nhắc che, nhãn "exit" bắt đầu ở x 487 = L + 115 ⇒ L 372. Theo dõi sáu hàng + `layoutId` (bảng `TRK` trong `scenes/s15/index.html`, mỗi khung [L, y, tỉ lệ]): `animate` L −43 → −327 khi bay lên 1200 → 1087 (f26–f30), −190 (f37), rung −280, −371 (f39–f40), −312 (f43), −207 (f45–); `initial` từ (360, 1019) f27 tới (211, 957) f30 rồi sang phải 285 (f38–f50), hết ở f51; `exit` 892 → 819 (f27–f32), 821 tới f50, vắng f51–f52, 875 → 817 (f53–f58); `useSpring` từ mép phải 373 (f38) → 188 → 92 → 70 (phóng 1.10 ở f40–f41) → 155 (f43) → 268, 303, 321, 322 (f45–f48) → 272 (f54); `stagger` (chỉ thấy đáy dưới hộp lời nhắc, y 951) L −237 … −270 … −202; `layoutId` (hàng mới, icon cam) vào từ phải 240 (f48), 33 (f49), rồi trượt trái −129, −217, −260, −266 (f50–f53); `layout` hiện ở f58 (398, 817); `popLayout` chưa thấy ở gốc tới f58 nên ẩn. Nội suy tuyến tính ở khung hai hàng chạm nhau (thành phần hợp) hoặc bị logo/hộp che: `animate` f41–f42, f44; `exit` f28–f29, f54; `useSpring` f42, f44. Bỏ các chuyển động bản cũ không có ở gốc (bảy hàng bật cùng lúc từ f31, rw1 trượt ra và rw3 tụt 120 px ở 1.5s, rw0 nhún). (7) Hộp lời nhắc trắng 255 tới f57 rồi mờ từ f58 (251, 247, 225, 188, 112 ở f58–f62; đo độ sáng vùng x 250–700, y 945–1000); bản cũ mờ từ 1.8s (f55) nên đã dời về 1.9s.
**Độ lệch nửa khung của s06.** Cảnh có pre 0.15s = 4.5 khung nên `.mov` lấy mẫu dòng thời gian ở nửa khung; khung ghép f hiện tl = (f − 0.5)/30 (đo: f04 hiện hình của f05 khi tra theo khung tròn, IoU 0.00). Bảng bbox tra theo f = round(tl·30 + 0.5); lịch morph TR (đã chỉnh theo đỉnh năng lượng ở mục 3) tra theo tl liên tục. s15 không có pre nên f = round(tl·30) + 1 − 19.
**Mã dựng**: `shared/morph.js` (symlink `scenes/s06/morph.js`, `scenes/s15/morph.js`): `Morph.ROWS` (35 hàng `[khung, tâm bbox x, y, rộng, cao]` của s06 f4–f38), `Morph.frame(tc, dx, TR, f)` (trạng thái morph tại tc co giãn về bbox +9px nét), `Morph.ghost`, `Morph.ghostW`, `Morph.d`. Mỗi cảnh một tween `DRV.t` (`ease: none`) gọi `drawMorph()` (s15 còn gọi `applyBand`, `drawRows`, độ đục `#rdots`) — hàm thuần của thời gian, seek an toàn: render hai lần cho cùng md5 TỪNG KHUNG ĐÃ GIẢI MÃ (`ffmpeg -threads 1 -f framemd5`; md5 cả file `.mov` không dùng để so vì có thẻ `hyperframes_version`); không `Math.random`.

### Kết quả cổng (trước → sau)

| Cảnh | SSIM | Tỉ lệ biên độ | Cửa sổ 0.2s kém nhất |
|---|---|---|---|
| s06 | 0.674 → 0.701 | 0.77 → 0.84 ĐẠT | 0.68 (6.9s) → 0.61 (6.9s) |
| s15 | 0.469 → 0.542 | 0.70 → 0.81 ĐẠT | 0.16 (30.1s) → 0.57 (28.8s) |

IoU mặt nạ cam gốc/remake (`iou`): s06 f4–f31 0.81–0.99 (f9 0.81, f19 0.85, f20 0.86 là khung đang đổi hình), f32 0.65, f33–f36 0.83–0.85; s15 f24–f50 0.78–0.97, f51 0.49, f52–f57 0.70–0.82.
s15 đạt cổng (tỉ lệ 0.81 ≥ 0.80, cửa sổ 0.2s kém nhất 0.57 ≥ 0.50) nhưng với biên mỏng: cột phải f38–f58 vùng giữa (`regions`) trung bình gốc 13.1, remake 10.9 (21 khung); các vòng trước bản s15 từng ở 0.82 (bóng ma trễ, chuyển động tự bịa), rồi 0.79 và 0.77 khi bỏ chuyển động không có ở gốc; vòng này dựng lại hàng bảng theo số đo (trượt ngang có cắt) nên lên 0.81, SSIM 0.514 → 0.542. Kết quả không chỉnh theo chỉ số năng lượng: mọi giá trị trong `TRK`, `BC`, `RD` là số đo hoặc ước lượng đã ghi.
Các cảnh khác: 15 file `.mov` còn lại không đổi (md5 cả file, trước/sau), `joins.json` không đổi; `hyperframes check` s06 và s15: 0 lỗi; cảnh báo không vượt bản HEAD (s06 lint 6 + craft 11 như HEAD; s15 lint 5 + craft 5, HEAD 5 + 1 + 11). Ảnh J05/J06/J14/J15: kiểu chuyển và hướng như trước; J14 khung vào cột phải f5 khớp gốc; J15: gốc còn G đang tan thành hạt ở cut−0.1s (30.3s), remake đã ẩn hình; chữ THÊM BỚT của remake lớn hơn/lệch phải so với "HÊM BÓ" của gốc (vị trí ngang chưa đo).

### Còn thiếu (đã đo)

- **Tường chữ SplitText ở f1–f3 của s06**: gốc là tường từ mờ (FROM / CHARS / WORDS / KÝ TỰ) nhảy từng khung (năng lượng f2 16.8 so với 10.4); phần này do s05 post vẽ (không thuộc mục này, md5 s05 phải giữ) và khác kiểu chữ của gốc. Năng lượng f2–f3 của remake vẫn thấp hơn.
- **Cột trái s15 f6–f23 (SplitText, dải tối `type: chars`, tường từ)**: gốc là mảnh s05 phóng to (~1.4×) dịch ngang, tường từ nhảy và nhoè từng khung (năng lượng trái-giữa 9–14 so với 3–7 ở 28.70–29.03s); remake là chữ nhỏ hơn, tường tĩnh, chip khác chỗ. Chưa đo và chưa dựng.
- **Cột phải s15**: thẻ A ở f22–f28 gốc rải rác lộn xộn (xáo trộn giữa chừng, nhoè), remake vẫn lưới 2×5 rồi hoán vị; thẻ đen gốc có viền cam; hàng bảng: `exit` f48–f58 (h 108 → 51 + 74 → 128: bị chia/che), hàng `whileDrag`/`layout`/`popLayout` sau f55, ô tròn rỗng ◯ của `useSpring` ở f40–f44 (remake luôn ✓), chữ THÊM BỚT vị trí ngang; hàng ở f54–f58 bị logo/chip che nên giữ vị trí cuối; thẻ biểu đồ nhoè bay chéo và thẻ mờ lớn trôi ở đáy cột phải (f30–f40, năng lượng 2–3.6 ở 29.40–29.60s, remake 0) chưa đo/dựng.
- **Bóng ma**: số nét, khoảng cách 50 px và độ đứng yên đã đo (xem trên) nhưng bóng ma được dựng là bản dịch dọc (và loe ngang ở chồng sao) của hình hiện tại; gốc đổi hình thất thường (chữ ký nguệch ngoạc ở f33–f36, hình vuông ma lớn ở f33, bóng ma của hình cũ khi đổi hình) chưa mô phỏng; 2 nét thừa ở cột 330; dịch ngang chưa đo riêng (chỉ suy từ cột 330/750 chênh ≤ 4 px); khung f6–f10 (tròn → sao) lấy từ vài cột nên chỉ gần đúng.
- **Khung đang đổi hình** (s06 f9, f32; s15 f51): bbox đo được nhưng dáng hình giữa chừng chỉ là nội suy đa giác (IoU 0.49–0.65 ở f32/f51).
- **G gốc vs G đa giác**: IoU 0.865 (đầu mút trên và bậc chưa khớp chi tiết).
- **J06**: ở 7.90–7.93s remake hiện chữ G thẳng đứng của halftone s07 như MỘT khối đặc và các hạt chỉ bắt đầu từ 7.967s; gốc giữ G đặc nghiêng của s06 tới 7.933s (s06 f37–f38 IoU 0.39–0.40 vì mặt nạ cam của remake là G của s07). Phần này thuộc s07/`joins.json` (J6 khớp-khung 0/0), không sửa ở mục này.
- **s15 f58–f59 (1.90–1.93s)**: gốc đã loãng thành hạt hình chữ G; remake ẩn hình ở 1.90s và đám hạt (elip, mục 2/3) bật ở 1.93s (J15 ở cut−0.1s: gốc còn G đang tan, remake chỉ còn logo); chưa đo lại ảnh hưởng lên cửa sổ 30.1s với dựng mới.
- **Độ trễ nửa khung** của s06 do `pre` 0.15s lẻ khung: bù trong scene; nếu đổi `pre` thì phải xem lại `f = round(tl·30 + 0.5)`.
