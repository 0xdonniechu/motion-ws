# Template teardown → rebuild

Khung job để dựng lại một clip motion-graphic bằng HyperFrames + GSAP. Quy trình đầy đủ: `docs/teardown-process.md`.
Ví dụ đã làm xong: `jobs/20261102-full` (Plane MWS-7).

## Bắt đầu job mới

```bash
cp -r templates/teardown jobs/<ngày>-<tên>        # giữ nguyên symlink scenes/*/fonts, boil.js
cd jobs/<ngày>-<tên>
uvx yt-dlp --no-playlist -f "mp4/best" -o source.mp4 "<URL>"   # bước 0: source.mp4 (đã được .gitignore)
```

Rồi theo quy trình: tìm cắt (bước 1) → điền `cuts.json` → viết `SPEC.md` → đo chuyển động (bước 3) → dựng scene → render + `compose.sh` → cổng kiểm.

## Tệp

| Tệp | Việc |
|---|---|
| `cuts.json` | Mốc cắt: `{"S":[0, ...mốc..., TOTAL], "TOTAL":<giây>, "fps":30, "size":[W,H], "bg":"0xRRGGBB"}`. `S` bắt đầu bằng 0 và kết thúc bằng TOTAL; N cảnh = `len(S) − 1`. `TOTAL`, `fps`, `size`, `bg` có thể bỏ (mặc định S cuối, 30, 1080x1920, `0xefece6`). Mẫu chỉ có 1 cảnh (S = [0, 2.0]): thay bằng danh sách thật. |
| `joins.json` | `{"sNN": {"pre": x, "post": y}}` (giây); bỏ khoá = 0/0. Khoá `_doc` chỉ là ghi chú. |
| `SPEC.md` | Khung đặc tả: hệ thiết kế, bảng cảnh, chuyển động đã đo, bảng điểm nối J1..Jn, trạng thái cổng kiểm. |
| `compose.sh` | Chồng N scene → `preview/remake.mp4`, `compare.mp4`, `ssim.txt`, `joins/JNN.jpg` (6 ô: gốc@cut−0.1, remake@cut−0.1, gốc@cut, remake@cut, gốc@cut+0.1, remake@cut+0.1). Cần `jq`, `ffmpeg`. |
| `motion.py` | Cổng biên độ: tỉ lệ ≥ 0.80 cả cảnh, không cửa sổ 0.2s nào < 0.50. Chạy `uvx --with numpy python -I motion.py [sNN ...]`. |
| `shared/` | `fonts/` (`fonts.css` + woff2 chia theo unicode-range, có tiếng Việt), `gsap.min.js`, `boil.js` (rung nét xác định), `hyperframes.json`. |
| `scenes/s01/` | Scene mẫu tối thiểu: `index.html` + `fonts` và `boil.js` là symlink về `../../shared/`, `gsap.min.js` và `hyperframes.json` là bản chép (như job gốc). |

## Thêm scene

```bash
cp -r scenes/s01 scenes/s02          # chép cả symlink; sửa index.html, data-duration = pre + Dài + post
# thêm mốc vào cuts.json ("S"), pre/post vào joins.json
cd scenes/s02 && npx -y hyperframes@latest check .
systemd-run --user --scope -p MemoryMax=6G npx -y hyperframes@latest render --format mov -o ../s02.mov .
cd ../.. && bash compose.sh
```

Không để render nằm trong git: `scenes/*.mov`, `scenes/*.mp4`, `preview/`, `source.*` đã nằm trong `.gitignore`.
