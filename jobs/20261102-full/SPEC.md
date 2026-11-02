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
