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
