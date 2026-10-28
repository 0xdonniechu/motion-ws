# Preset: pipeline-diagram

Sơ đồ quy trình 16:9: hộp + mũi tên trái→phải, code/browser/frames minh họa.
Đã verify bằng video-function-scene (check passed, 3 vòng fine-tune).

## Biến mỗi lần dùng

- `NODES`: mảng {khung (code/browser/stack/box/player), nhãn dưới}.
- Màu: nền #141414, viền vàng #e8c547, code xanh #7bc47f, chữ #f2f2f2.
- Nhịp: mỗi node 0.8–1.2s, vẽ nét (stroke-dashoffset) cho đồ thị.

## Template

Copy `video-function-scene/` làm điểm xuất phát (đã có 5 node chuẩn).
Bản rút gọn: `template/index.html` — 3 node mẫu, 8s, 1280x720.
