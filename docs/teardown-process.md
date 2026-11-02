# Quy trình teardown → rebuild một clip motion-graphic

Quy trình chuẩn để dựng lại (remake) một clip motion-graphic dọc 1080x1920, 30fps bằng HyperFrames + GSAP,
khớp bản gốc về cảnh, điểm nối và biên độ chuyển động. Rút từ job `jobs/20261102-full`
(clip "GSAP và Motion", 36.03s, 17 cảnh, 16 điểm nối; ticket Plane MWS-7) — đây là ví dụ làm xong để đối chiếu.

Khung job sẵn: `templates/teardown/` (`cp -r templates/teardown jobs/<ngày>-<tên>`, xem `templates/teardown/README.md`).

Nguyên tắc chung:
- Đo trước, dựng sau. Mọi con số (mốc cắt, quỹ đạo, màu) lấy từ khung gốc, không đoán bằng mắt.
- Không chép asset gốc (ảnh, nhân vật, logo) vào scene; thay bằng hình tự vẽ.
- Mỗi bước có một kết quả cụ thể và một chỗ ghi (file) để bước sau đọc.

## Bước 0 — Lấy nguồn

```bash
mkdir -p jobs/<ngày>-<tên> && cd jobs/<ngày>-<tên>
uvx yt-dlp --no-playlist -f "mp4/best" -o source.mp4 "<URL>"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames,duration -of default=nw=1 source.mp4
```

Lưu thành `jobs/<ngày>-<tên>/source.mp4` (đã nằm trong `.gitignore`, không commit). Ghi vào `SPEC.md`: kích thước, fps, thời lượng.
Nếu fps gốc không phải 30 thì quyết định một lần (giữ fps gốc hoặc ép 30) và ghi vào `cuts.json` (`fps`).

## Bước 1 — Tìm điểm cắt

1. Ứng viên bằng `scdet`:

   ```bash
   ffmpeg -hide_banner -i source.mp4 -vf "scdet=threshold=5:sc_pass=1" -an -f null - 2>&1 \
     | grep -o 'lavfi.scd.score: [0-9.]*, lavfi.scd.time: [0-9.]*'
   ```

   Ngưỡng cao (10) bỏ sót nhiều cắt của clip motion; hạ ngưỡng (3–5) rồi lọc bằng mắt. `scdet` chỉ cho ứng viên.
2. Khung dày quanh mỗi ứng viên (±0.2s, từng khung 30fps) để lấy thời điểm chính xác tới khung:

   ```bash
   mkdir -p frames
   ffmpeg -v error -ss <cut-0.2> -t 0.4 -i source.mp4 -vf "fps=30" frames/cut<NN>_%02d.png
   ```
3. Contact sheet cả clip và từng cảnh để xem bằng mắt:

   ```bash
   ffmpeg -v error -i source.mp4 -vf "fps=5,scale=270:-1,tile=8x5" -frames:v 1 contact-sheet.jpg
   ffmpeg -v error -ss <đầu> -t <dài> -i source.mp4 -vf "fps=10,scale=270:-1,tile=6x4" -frames:v 1 frames/sheet<NN>.jpg
   ```
4. Kết quả: danh sách **S** = các mốc đầu cảnh, bắt đầu bằng 0 và kết thúc bằng TOTAL. Một "cảnh" là một khối hình ảnh liền mạch,
   có thể gộp nhiều cắt nhỏ (job mẫu: 26 cắt phát hiện được, 17 cảnh). Ghi vào `cuts.json`:

   ```json
   {"S": [0, 1.00, 2.75, 4.10], "TOTAL": 4.10, "fps": 30, "size": [1080, 1920]}
   ```

   `compose.sh` và `motion.py` đọc S, TOTAL, fps từ file này; số cảnh N = `len(S) − 1`. Không viết cứng mốc ở chỗ khác.
   (`jobs/20261102-full/cuts.json` là đầu ra phát hiện cắt kiểu cũ — `cuts_frames`, `cuts_sec`, `grid` — không có khoá `S`; job đó giữ S viết cứng trong script.)

## Bước 2 — SPEC.md

Chép `templates/teardown/SPEC.md` và điền:

- **Hệ thiết kế**: màu (hex đo từ khung), font (chỉ từ `shared/fonts/`), cỡ chữ, phụ đề, thẻ/viền/bóng, hoạ tiết nền, thay thế nhân vật/logo.
  **Kiểm glyph tiếng Việt** ngay ở bước này: render thử chuỗi đủ dấu (`Ă Â Ê Ô Ơ Ư Đ ạ ả ấ ầ ẩ ẫ ậ …`) ở từng font và cỡ định dùng; font nào rơi về font hệ thống thì đổi font hoặc nạp đủ subset (xem Cạm bẫy).
- **Bảng cảnh**: số, mốc gốc, dài, nội dung, phụ đề.
- **Bảng điểm nối J1..Jn** (n = N − 1): mỗi điểm một dòng — kiểu chuyển theo gốc, ai làm (scene nào có `pre`, scene nào có `post`),
  giá trị `pre`/`post`; hoặc "khớp-khung" (match-cut, 0/0). Giá trị `pre`/`post` đo theo gốc, ghi vào `joins.json`.
  Scene k nằm ở `[S[k-1]−pre, S[k]+post]` trên timeline chung, scene sau đè scene trước.

Duyệt SPEC với owner trước khi dựng.

## Bước 3 — ĐO chuyển động trước khi dựng

Với mỗi cảnh có chuyển động, đo quỹ đạo từng khung ở 30fps bằng numpy (thêm `opencv-python-headless` nếu cần matchTemplate / ECC):

```bash
ffmpeg -v error -ss <đầu> -t <dài> -i source.mp4 -vf "fps=30,scale=540:-1,format=rgb24" -f rawvideo - | \
  uvx --with numpy python -I measure.py        # script đo của bạn (ví dụ: mặt nạ màu → bbox / tâm / góc theo từng khung)
```

Đo cái gì: vị trí, tỉ lệ, góc, độ mờ của từng đối tượng chính theo khung; đỉnh, điểm dừng, quá đà (overshoot), khung bắt đầu và kết thúc;
rung nét kiểu vẽ tay (boil) đo riêng (biên độ, bước, hướng). Ghi bảng quỹ đạo vào mục "Chuyển động đã đo" của SPEC; khi dựng, đưa mảng khung thẳng vào timeline
(`tl.to(..., { duration: 1/30, ease: "none" }, (f-1)/30)`), xem `jobs/20261102-full/scenes/s01/index.html`.

**Bài học (job mẫu)**: lần đầu dựng bằng cách "tạo dáng" từ vài khung thưa (đầu, giữa, cuối), chuyển động ra **quá nhỏ** so với gốc,
và phải làm lại chuyển động sau khi đo từng khung (commit "Remake motion amplitude: measured trajectories"). Đừng bỏ bước đo, đừng đo từ khung thưa.

## Bước 4 — Scene HyperFrames độc lập

Mỗi cảnh là một project HyperFrames riêng: `scenes/sNN/index.html` (+ `gsap.min.js`, `hyperframes.json`, symlink `fonts` → `../../shared/fonts`, symlink `boil.js` → `../../shared/boil.js`).

- **Một** timeline GSAP, `paused: true`, đăng ký `window.__timelines["main"] = tl`. Không `Math.random`, không `setTimeout`; mọi thứ là hàm thuần của thời gian để seek an toàn.
  Rung nét dùng `boil(tl, targets, opts)` của `shared/boil.js` (xác định, đặt vào CSS `translate`/`rotate` để không đè transform của GSAP), chỉ cho phần tử đã đo là rung.
- `html, body, #root` nền `transparent`; nền của scene là lớp `#bg` riêng. `data-duration` = pre + dài + post.
- Chữ tiếng Việt viết thẳng bằng ký tự có dấu; font phải có subset Việt (xem Cạm bẫy).
- Kiểm: `npx -y hyperframes@latest check <thư mục scene>` (lint, runtime, layout, contrast) và `... snapshot` để xem khung.

**Làm một đoạn thử trước** (một cảnh hoặc 2–3 cảnh liền, ví dụ `jobs/20261102-spring-seg/rebuild/`) và đưa owner duyệt giao diện, font, nhịp trước khi dựng hết.
Chỉ khi đoạn thử được duyệt mới dựng các cảnh còn lại; đường dẫn mẫu đã duyệt ghi ở đầu SPEC.

## Bước 5 — Render từng scene thành .mov alpha, rồi ghép

```bash
cd scenes/sNN
systemd-run --user --scope -p MemoryMax=6G npx -y hyperframes@latest render --format mov -o ../sNN.mov .
cd ../.. && bash compose.sh
```

- `--format mov` là ProRes 4444 có alpha, bắt buộc cho scene có `pre`/`post` > 0. Scene đục, không có pre/post, có thể là `sNN.mp4`.
- File render dài đúng `pre + dài + post`; `compose.sh` báo LỖI nếu thiếu, CẢNH BÁO nếu dư.
- `compose.sh` chồng N scene lên nền `bg`, ra `preview/remake.mp4`, `preview/compare.mp4` (gốc trái | remake phải), `preview/ssim.txt`, `preview/joins/JNN.jpg`.
- Render `-o` ra ngoài thư mục scene (`../sNN.mov`) để không có `renders/` trong git; `scenes/*.mov`, `scenes/*.mp4`, `preview/` đã nằm trong `.gitignore`.

## Bước 6 — Cổng kiểm

1. **SSIM từng cảnh** (`preview/ssim.txt`, xám 270x480): để theo dõi; cảnh nào thấp bất thường thì mở `compare.mp4` đúng đoạn đó.
2. **Ảnh điểm nối** `preview/joins/JNN.jpg`, mỗi điểm nối một ảnh gồm **6 ô, trái → phải**:
   1. gốc @ cut−0.1s
   2. remake @ cut−0.1s
   3. gốc @ cut
   4. remake @ cut
   5. gốc @ cut+0.1s
   6. remake @ cut+0.1s

   (Mỗi cặp ô 1-2, 3-4, 5-6 là một khung của `compare.mp4`: gốc bên trái, remake bên phải.) Remake phải cùng **kiểu** chuyển, cùng hướng, cùng nhịp với gốc ở cả ba thời điểm.
3. **Biên độ** `uvx --with numpy python -I motion.py [sNN ...]`: năng lượng chuyển động trung bình |khung(t) − khung(t−1)| gốc so với remake.
   Đạt khi **tỉ lệ cả cảnh ≥ 0.80** và **không cửa sổ 0.2s nào < 0.50** (chỉ xét cửa sổ gốc có chuyển động, năng lượng > 2). Mã thoát 1 nếu còn cảnh CHƯA đạt.

Ghi kết quả vào bảng "Cổng kiểm" của SPEC. Cảnh chưa đạt mà có lý do đã đo (ví dụ gốc dùng hiệu ứng mà remake chưa có) thì ghi rõ lý do, không âm thầm bỏ qua.

## Bước 7 — builder → reviewer, mỗi PR một mục

Sửa lại theo từng mục riêng, mỗi mục một PR: builder làm, reviewer độc lập duyệt (đưa task + diff, không đưa tóm tắt của builder); FAIL thì builder sửa theo danh sách đánh số, tối đa 2 vòng rồi hỏi owner. Thứ tự:

1. **Font** — subset tiếng Việt, đúng font từng vai trò, không rơi font hệ thống.
2. **Điểm nối** — `joins.json`, `pre`/`post`, ảnh J01..Jn khớp gốc.
3. **Biên độ** — đo lại quỹ đạo, `motion.py` đạt, boil.
4. **Textures** — hạt, halftone, nhiễu giấy, bóng, độ mờ chuyển động (dùng thêm skill `wtt-code-animation-studio`, `huashu-art-motion`).

Chỉ session chính commit, push, mở PR; builder chỉ sửa working tree.

## Bảng công cụ

| Công cụ | Dùng để | Lệnh / ghi chú |
|---|---|---|
| `uvx yt-dlp` | tải nguồn (bước 0) | `uvx yt-dlp --no-playlist -f "mp4/best" -o source.mp4 <URL>` |
| `ffprobe` | kích thước, fps, thời lượng, độ dài file render | |
| `ffmpeg` | `scdet`, khung dày, contact sheet, ghép, SSIM | trong `compose.sh` |
| `jq` | đọc `cuts.json`, `joins.json` | `compose.sh` |
| `numpy` (qua `uvx --with numpy python -I`) | đo quỹ đạo (bước 3), `motion.py` | thêm `opencv-python-headless` khi cần matchTemplate/ECC |
| `npx -y hyperframes@latest` | `check`, `snapshot`, `render --format mov` | dưới `systemd-run` |
| GSAP (`shared/gsap.min.js`) | timeline | một timeline paused mỗi scene |
| `shared/boil.js` | rung nét xác định | `boil(tl, targets, opts)` |
| `systemd-run --user --scope -p MemoryMax=<N>G` | giới hạn RAM cho lệnh nặng | xem Cạm bẫy |
| `git` | một mục một PR | chỉ session chính commit/push |

## Skill

Cần dùng:

| Skill | Lý do |
|---|---|
| `hyperframes` | điểm vào bắt buộc cho mọi việc video/HyperFrames |
| `hyperframes-core` | hợp đồng composition: `data-*`, `class="clip"`, track, quy tắc render xác định |
| `hyperframes-animation` | quy tắc chuyển động, timeline GSAP seek-safe, chuyển cảnh |
| `hyperframes-cli` | `check`, `snapshot`, `render`, chẩn đoán lỗi build/render |
| `hyperframes-keyframes` | keyframe 2D/3D, zoom, đường dẫn, mặt nạ, SVG morph |
| `gsap-skills` | cách viết GSAP đúng chuẩn (plugin skill chính chủ GSAP) |
| `wtt-code-animation-studio` | chỉ ở mục Textures: giấy, halftone, hạt, nét vẽ |
| `huashu-art-motion` | chỉ ở mục Textures: công thức chuyển động/phong cách để đối chiếu |

Không cần cho thể loại này:

| Skill | Lý do |
|---|---|
| `lemo-opuscar` | làm phim ngắn theo phong cách thư viện riêng; ở đây phong cách đã có sẵn ở clip gốc |
| `dashi-animationstyle` | dựng từ lời dẫn có giọng đọc; clip này không có giọng đọc |
| `video-shotcraft` | video sản phẩm dựng bằng Remotion, khác framework |
| `xilo-opus-video` | quy trình đề xuất 3 hướng rồi dựng; ở đây hướng đã cố định bởi clip gốc |
| `hyperframes-audio`, `media-use` | chưa có âm thanh; dùng khi bắt đầu thêm tiếng |
| `mg-styles-15` | chỉ là tài liệu tham khảo phong cách, không phải bước trong quy trình |

## Cạm bẫy

- **Font tiếng Việt**: dùng bản Fontsource chia theo `unicode-range` (`latin`, `latin-ext`, `vietnamese`) cho từng font và khai đủ ba `@font-face` (xem `shared/fonts/fonts.css`).
  Thiếu subset `vietnamese` thì dấu (ạ ả ấ ầ ẩ ẫ ậ ơ ư đ …) rơi về font hệ thống mà nhìn thoáng không thấy. KHÔNG vẽ dấu bằng CSS (pseudo-element, định vị chồng): lệch theo font, hỏng khi đổi cỡ.
  Font không có glyph Việt thì đổi font, không vá.
- **Lệnh nặng chạy dưới giới hạn RAM**: `systemd-run --user --scope -p MemoryMax=<N>G <lệnh>` cho render và dựng hàng loạt (mỗi worker Chrome ~256 MB). Vượt ngưỡng thì chỉ lệnh đó bị giết; không có nó, systemd-oomd có thể giết cả terminal host cùng mọi session.
- **Không bao giờ `pkill -f` với mẫu khớp chính shell của mình**: dòng lệnh của shell chứa mẫu đó nên `pkill -f "<mẫu>"` tự giết shell. Tìm PID chính xác (`pgrep -af`), loại PID của shell, rồi `kill <pid>`; hoặc dùng `pkill -x <tên tiến trình>`. Sau khi dừng agent, kiểm tra tiến trình con còn sót.
- **File render và `preview/` không vào git**: `source.*`, `frames/`, `scenes/*.mov`, `scenes/*.mp4`, `preview/`, `tmp/`, `.hyperframes/` đã có trong `.gitignore` (cả `jobs/*` và `templates/*`). Render bằng `-o ../sNN.mov`; kiểm `git status` trước khi commit.
- **Độ dài file render**: sai một chút so với `pre + dài + post` là `compose.sh` báo lỗi hoặc cắt mất phần đuôi (post). Đặt `data-duration` đúng ngay từ đầu.
- **Seek-safe**: `Math.random`, `setTimeout`, trạng thái tích luỹ làm render khác preview. Dùng hàm thuần của thời gian (`boil.js`).

## Ví dụ làm xong: jobs/20261102-full (Plane MWS-7)

| Thành phần | Chỗ xem |
|---|---|
| Đặc tả: hệ thiết kế, 17 cảnh, 16 điểm nối | `jobs/20261102-full/SPEC.md` |
| 17 scene độc lập | `jobs/20261102-full/scenes/s01..s17/index.html` |
| Điểm nối pre/post | `jobs/20261102-full/joins.json` |
| Ghép, SSIM, ảnh điểm nối | `jobs/20261102-full/compose.sh` |
| Cổng biên độ | `jobs/20261102-full/motion.py` |
| Font, GSAP, boil | `jobs/20261102-full/shared/` |
| Đoạn thử đã duyệt | `jobs/20261102-spring-seg/rebuild/` |

Job này có S viết cứng trong `compose.sh`/`motion.py` (17 cảnh); template `templates/teardown/` đã chuyển sang đọc `cuts.json` và lặp theo số cảnh.
