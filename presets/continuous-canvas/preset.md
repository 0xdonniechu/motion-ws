# Preset: continuous-canvas

Cả video là MỘT bức tranh lớn (world), mỗi scene là cửa sổ camera (vị trí +
zoom). Nối scene bằng camera move, không cắt. Prezi-style, infinite canvas,
"bức tranh lớn" gom hết vào đây.

## Biến mỗi lần dùng

- `WORLD`: kích thước tranh (mẫu 3840x2160 = 3 khung 1280x720 cạnh nhau, overview scale 0.3333 lấp kín không viền đen).
- `REGIONS`: mảng {tên, tâm x, nội dung}. Tối đa 3–4 vùng, vùng sau chồng vùng trước 1 vật tham chiếu.
- `ZOOMS`: 2 mức (tổng thể + chi tiết). Chữ nhỏ nhất ở zoom sâu vẫn đọc được.
- Nhịp: overview 2s → mỗi vùng 2–3s → move 1s → kết zoom-out (nếu có).

## Luật camera (từ motion-vocab)

Camera = `x/y/scale` trên world wrapper duy nhất, `transformOrigin` tính trước,
timeline paused. Cấm tween top/left/width/height. Vật tham chiếu chung giữa 2 vùng.

## Template

`template/` — world 3840x2160, 3 vùng (hook/diagram/payoff) + sợi chỉ
hành trình và chấm đỏ chạy suốt 12s, camera overview → A → B → C, 12s,
1280x720. Engine: HyperFrames. Đã verify: check pass, snapshot 1/4/7.5/10s.
