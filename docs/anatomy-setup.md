# Anatomy skill setup (wheresryan22/anatomy)

Skill vẽ minh họa isometric SVG chi tiết: vật thể nhiều chi tiết nhỏ,
khung card + tiêu đề + readout, tương tác được, xuất HTML độc lập.
Hợp cho cảnh "bản vẽ tách lớp" trong video explainer (kiểu phin cà phê).

## Cài (đã làm trên server 2026-10-27)

```bash
cd ~/tools && git clone https://github.com/wheresryan22/anatomy.git
```

Zero dependency, chỉ cần Node 20.10+ và Chrome/Chromium để check.
MIT license.

## Kiểm tra (đã chạy ok)

```bash
cd ~/tools/anatomy
node examples/dial-indicator/build.mjs   # ra dial-indicator.html độc lập
```

## Dùng

Đọc `~/tools/anatomy/SKILL.md`. Quy trình: đo size (Figure/Hero/Epic) →
viết concept + danh sách chi tiết trước → build bằng kit
(`kit/iso-kit.mjs`, `lathe.mjs`, `tube.mjs`) → audit hình học → xuất HTML.
SVG output đưa vào HyperFrames làm asset cảnh, hoặc tách lớp làm khung
whiteboard.
