# Preset: exploded-view

Tách lớp vật thể: các lớp xếp dọc + leader line + nhãn, hiện dần từng lớp.
Đã verify bằng shot phin (5 lớp, check passed).

## Biến mỗi lần dùng

- `LAYERS`: mảng {hình SVG, nhãn} từ trên xuống dưới.
- Nền sáng + lưới mờ. Nhãn mono 30px, line xám.
- Figure phức tạp thì vẽ bằng skill anatomy, xuất SVG rồi nhúng vào template.

## Template

`template/index.html` — 3 lớp mẫu (nắp/thân/đế) + nhãn, 8s, 1080x1920.
