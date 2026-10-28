# Preset: list-vertical

Video list/countdown dọc 1080x1920: N item cùng 1 template (số + ảnh + caption).
Đã verify bằng job phin (4 shot, check passed).

## Biến mỗi lần dùng

- `ITEMS`: mảng {số, ảnh, tiêu đề, dòng phụ, sub}.
- `BG`: màu nền + lưới. `ACCENT`: màu chữ nhấn.
- Nhịp: 5s intro + 6–10s/item + 4s outro.

## Template

`template/index.html` — 2 item mẫu, 20s, 1080x1920.
Nhân item bằng cách copy khối clip, đổi `data-start` nối tiếp nhau.
