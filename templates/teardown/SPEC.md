# Remake spec — "<tên clip>" (<nguồn / tác giả>, <TOTAL>s, <W>x<H>, <fps>fps)

Gốc: `source.mp4` (cùng thư mục, KHÔNG commit, KHÔNG chép asset gốc vào scene).
Mốc cắt: `cuts.json` (`S`, `TOTAL`). Điểm nối: `joins.json`. Quy trình: `docs/teardown-process.md`.
Mẫu đã duyệt (đọc trước khi làm): `<đường dẫn đoạn thử đã được owner duyệt, điền sau bước 4>`.

## Hệ thiết kế chung (mọi cảnh)

Màu (hex, đo từ khung gốc, không đoán bằng mắt):

| Vai trò | Hex | Dùng cho |
|---|---|---|
| Nền sáng | `#xxxxxx` | |
| Nền tối | `#xxxxxx` | |
| Nhấn 1 | `#xxxxxx` | |
| Chữ chính | `#xxxxxx` | |

Font (chỉ dùng `../shared/fonts/`; font mới thêm vào `shared/fonts/fonts.css` theo unicode-range, xem mục Cạm bẫy trong quy trình):

| Vai trò | Font | Cỡ / đậm | Ghi chú |
|---|---|---|---|
| Chữ lớn | Anton | | |
| Phụ đề | Inter 500 | | từ nhấn: ISerif nghiêng |
| Nhãn / code | JBMono 500 | | |

Kiểm tra glyph tiếng Việt: dán `Ă ă Â â Ê ê Ô ô Ơ ơ Ư ư Đ đ ạ ả ấ ầ ẩ ẫ ậ ắ ằ ẳ ẵ ặ ẹ ẻ ẽ ế ề ể ễ ệ ỉ ị ọ ỏ ố ồ ổ ỗ ộ ớ ờ ở ỡ ợ ụ ủ ứ ừ ử ữ ự ỳ ỵ ỷ ỹ`
vào từng font ở từng cỡ dùng, chụp snapshot, xác nhận không rơi về font hệ thống và dấu không bị vẽ lệch. Kết quả: <ĐẠT / font nào lỗi>.

Quy ước khác: vị trí nhãn, vùng phụ đề, kiểu thẻ (viền, bóng, bo góc), hoạ tiết nền, thay thế nhân vật/ảnh người/logo (không chép asset gốc).

## Cảnh (mốc theo bản gốc; Dài = S[k] − S[k−1])

| # | Gốc | Dài | Nội dung | Phụ đề (từ nhấn trong *...*) |
|---|---|---|---|---|
| 01 | 0.00–<S1> | | | |

Cách xem gốc từng cảnh: `ffmpeg -ss <đầu> -t <dài> -i source.mp4 -vf "fps=5,scale=270:-1,tile=..." ...`

## Chuyển động đã đo (bước 3, TRƯỚC khi dựng)

Mỗi cảnh một mục: đối tượng nào chuyển động, quỹ đạo từng khung ở 30fps (vị trí, góc, tỉ lệ, độ mờ), đỉnh/điểm dừng/quá đà.
Chỉ ghi cái đã đo; chuyển động không đo được thì ghi "không đo" chứ không bịa.

| Cảnh | Đối tượng | Khung đầu–cuối | Quỹ đạo đo được | Cách đo (script / lệnh) |
|---|---|---|---|---|
| s01 | | | | |

## Điểm nối

Ghép bằng `compose.sh`: scene k nằm ở `[S[k-1]-pre, S[k]+post]`, scene sau ĐÈ scene trước.
`joins.json` khai báo `{"sNN": {"pre": x, "post": y}}`. File render phải dài đúng `pre + Dài + post`.

**Hợp đồng cho scene có pre hoặc post > 0** (hoặc cần trong suốt):
- Render `--format mov` → `scenes/sNN.mov` (ProRes 4444 alpha). Xoá `sNN.mp4` cũ của scene đó.
- `html, body, #root` nền `transparent`. Nền của scene là một lớp riêng (`#bg`) để che/lộ được.
- Nội dung cũ dịch đi `pre` giây: bọc timeline cũ vào timeline chính tại vị trí `pre` (`main.add(old, PRE)`), `data-duration` = pre + Dài + post.
- Trong `pre`: chỉ vẽ phần chuyển cảnh vào; phần còn lại trong suốt để scene trước lộ ra.
- Trong `post`: scene tiếp tục/thoát ra như bản gốc; scene sau sẽ đè lên.
- Khớp-khung (match-cut): khung cuối scene trước phải gần như trùng khung đầu scene sau. Kiểm tra bằng snapshot hai bên.

| J | Mốc | Kiểu (theo gốc) | Ai làm | pre (scene sau) / post (scene trước) |
|---|---|---|---|---|
| J1 | <S1> | | | 0/0 |

Kiểm tra mỗi điểm nối: `bash compose.sh` rồi xem `preview/joins/JNN.jpg`, 6 ô trái → phải:
gốc@cut−0.1, remake@cut−0.1, gốc@cut, remake@cut, gốc@cut+0.1, remake@cut+0.1.
Bản remake phải cùng KIỂU chuyển, cùng hướng, cùng nhịp. `joins.json` là nguồn đúng cho pre/post; cập nhật bảng này theo số đo thực.

## Cổng kiểm (bước 6) — trạng thái

| Cảnh | SSIM | Biên độ (motion.py: tỉ lệ / cửa sổ tệ nhất) | Ghi chú |
|---|---|---|---|
| s01 | | | |
