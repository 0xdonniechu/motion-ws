# Motion vocab chung (dùng cho mọi preset)

## Entrances (vào khung)

| Tên | Dùng khi | Token |
|---|---|---|
| `pop` | Số, badge, CTA cần nhấn | scale 0.7→1, 0.5–0.7s, `back.out(1.5)` |
| `slide-fade` | Thẻ, caption, layer | x -30→0 + opacity, 0.5s, `power2.out` |
| `draw-in` | Nét vẽ, wave, mũi tên | stroke-dashoffset 100→0, 0.8–1.1s, `power1.inOut` |
| `rise` | Tiêu đề lớn | y 60–80→0 + opacity, 0.6–0.7s, `power3.out` |
| `fade` | Sub, nhãn phụ | opacity, 0.4–0.6s |

## Transitions (nối shot)

| Tên | Dùng khi | Token |
|---|---|---|
| `hard-cut` | Mặc định TikTok dọc, countdown, list | 0s, 2 clip nối nhau |
| `fade` | Đổi chủ đề nhẹ, outro | overlap + autoAlpha 0.3–0.5s, cấm tween visibility của clip |
| `slide-push` | Sang item kế tiếp (list) | wrapper x ±1280, 0.4s, `power2.inOut` |

Luật: chuyển cảnh rơi đúng beat/word (lệch > 0.3s là fail). Không frame đen chết.

## Camera (preset continuous-canvas)

| Tên | Dùng khi | Token |
|---|---|---|
| `map-overview` | Mở đầu: thấy cả bản đồ | scale vừa khít world, 1.5–2s giữ |
| `pan` | Sang vùng kế bên | x/y trên world wrapper, 0.8–1.2s, `power2.inOut` |
| `zoom-in` | Vào chi tiết | scale + x/y cùng lúc, giữ vật tham chiếu chung |
| `zoom-out` | Kết: thấy bức tranh lớn | ngược zoom-in |

Luật seek-safe: camera = `x/y/scale` trên **wrapper** (không đụng clip),
`transformOrigin` tính trước, tọa độ tuyệt đối, timeline paused duy nhất.
Vật tham chiếu chung giữa 2 vùng để mắt không lạc. Zoom sâu nhất chữ vẫn đọc được.
