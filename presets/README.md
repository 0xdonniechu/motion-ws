# Preset visual — tái dùng theo concept

Mọi video đưa vào được phân vào 1 preset dưới đây rồi mới teardown chi tiết.
Preset = bố cục + nhịp + engine + biến cần thay. Không làm voice trong preset.
Dùng chung: `_shared/` (motion-vocab, teardown-template, review-checklist).

| Preset | Dùng khi video gốc là | Engine | Mẫu sống |
|---|---|---|---|
| [list-vertical](list-vertical/preset.md) | List/countdown dọc, thẻ + caption lặp lại | HyperFrames | job phin 182519 |
| [kinetic-type](kinetic-type/preset.md) | Chữ động lớn, nhịp nhanh | HyperFrames | — |
| [pipeline-diagram](pipeline-diagram/preset.md) | Sơ đồ khối mũi tên trái→phải | HyperFrames | video-function-scene |
| [exploded-view](exploded-view/preset.md) | Tách lớp vật thể + nhãn | HyperFrames + anatomy | job phin shot 3 |
| [continuous-canvas](continuous-canvas/preset.md) | Cả video là 1 bức tranh lớn, scene = cửa sổ camera | HyperFrames | template verify 2026-10-28 |
| [corporate-motion](corporate-motion/preset.md) | Dọc 9:16, 2–3 phút, giải thích kỹ năng/khoá học bằng thẻ UI phẳng trắng-xanh, số treo (80/20), ẩn dụ, checklist, bài học | HyperFrames + GSAP | 4 job (20261028-230040 + corp-sample-*): số đo + `style.json`, chưa có scene |

## Luật matching (director làm tay trước, tự động sau)

1. Dọc 9:16 + thẻ lặp → list-vertical.
2. Chữ chiếm >50% khung hình, đổi theo beat → kinetic-type.
3. Hộp + mũi tên giải thích quy trình → pipeline-diagram.
4. Một vật thể tách thành lớp có nhãn → exploded-view.
5. Nhiều scene là một phần của cả một bức tranh lớn → continuous-canvas.
6. Dọc 9:16 dài 2–3 phút, nền trắng-xanh phẳng, thẻ UI mockup + số treo + ẩn dụ + checklist (video bán kỹ năng/khoá học) → corporate-motion. Ưu tiên hơn luật 1 khi thẻ không lặp một khuôn.
7. Ảnh→vẽ tay từng nét → whiteboard (ngoài các preset này).
8. Không khớp gì → teardown tự do, tách preset mới nếu lặp lại lần 2.
