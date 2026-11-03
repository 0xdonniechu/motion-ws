# Theming: preset mới = theme mới, chuyển động giữ nguyên

Quy tắc của chủ: **ngôn ngữ chuyển động cố định**, preset mới chỉ đổi màu, font và kiểu chữ; vibe giữ nhất quán. Bo góc thẻ/pill và độ đậm bóng là bố cục nên nằm ở `language.json`, không đổi theo theme.

## Làm preset mới
1. `cp themes/default.json themes/<tên>.json`, đổi `name` và các giá trị (xem bảng khoá).
2. Nếu dùng font mới: thêm `@font-face` (Fontsource woff2, subset latin + latin-ext + vietnamese, 700 và 800) vào `kit/fonts/fonts.css`, ghi giấy phép OFL cạnh file.
3. `node kit/build-tokens.mjs --theme <tên> --out kit/tokens.<tên>.js` (không `--out`: ghi đè `kit/tokens.js`, theme default).
4. Cho dự án HyperFrames trỏ `tokens.js` (symlink ở thư mục dự án) tới `kit/tokens.<tên>.js`; `index.html` là bản sao nguyên văn của composition gốc (không sửa riêng). Ví dụ: `jobs/20261103-corp-demo-dashboard/trial-night/`; `verify.sh` của job đó `cmp` hai `index.html`.
5. Render, rồi `compare_timing.py` (job corp-demo-dashboard) giữa hai theme: đợt chuyển động phải trùng khung. Thử tua: `JSDOM_DIR=… node demo/seek-test.mjs <index.html>` (xem đầu tệp).

## Khoá của một theme
| Khoá | Nội dung |
|---|---|
| `colors` | `surface` (thẻ), `accent_dark/primary/mid/light`, `ink`, `ink_secondary`, `yellow` (điểm nhấn nhỏ), `mark` (màu vệt tô của effect `mark`; tương phản >= 3.0 với `ink`, build-tokens kiểm) |
| `page` | `tint` (nền mặc định), `white` (nền thứ hai; ở theme tối là nền tối hơn/sáng hơn một bậc) |
| `iso` | ba mặt khối iso, sáng tới tối |
| `font` | `family`, `body_weight`, `accent_family` (font chữ nhấn nghiêng `~từ~`); trọng lượng tiêu đề nằm ở `type.roles.*.weight` |
| `type` | `roles.<vai>.{weight, scale}` (cỡ px = `language.type.sizes_px` x scale; chỉnh scale để bù độ rộng font), `line_height_em`, `letter_spacing_em`, `label_letter_spacing_em`, `case.{headline,label}` (`none` hoặc `uppercase`), `highlight.{style: color or marker, marker_alpha}`, `accent_italic.weight` (độ đậm chữ nhấn nghiêng; tỉ lệ cỡ 1.27 là language) |
| `shadow` | `rgb` (tông màu của bóng; alpha, blur, offset nằm ở language) |

`build-tokens.mjs` từ chối theme có khoá ngoài danh sách trên (kể cả `radii`, `shadow.alpha_scale`) hoặc thiếu khoá bắt buộc. `kit.js` và `kit.css` không chứa màu/font cứng, chỉ đọc biến `--k-*` sinh từ tokens.

## Không bao giờ đổi trong theme (đó là language: `language.json`)
Primitive chuyển động, ease, thời lượng, biên độ, quá đà, so le, chuyển cảnh (kiểu và thời lượng), nhịp (đứng yên, đợt), tỉ lệ bố cục (rộng thẻ/pill, bo góc, độ đậm bóng, lưới nền, vùng an toàn), cỡ chữ gốc theo vai, và từ vựng `catalog.json` (component, effect, transition). Muốn đổi những thứ này là đổi preset gốc, không phải làm theme: sửa `language.json` rồi `build-tokens.mjs --check-style` để đối chiếu `style.json`.
Hai bản render cùng composition ở hai theme phải có thời điểm chuyển động y hệt; chỉ màu, font, hình chữ khác.
