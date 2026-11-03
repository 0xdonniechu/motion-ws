"""Đo dấu X vẽ tay (gạch chéo) đè lên thẻ "KHO" ở clip 7700960427491986696 (1080x1920), ~41.7s (quét 2026-11-04).
Cách đo (30fps): nét = điểm cùng màu nhấn (#1872ce, dung sai 55) trong hộp quanh thẻ, trừ biểu tượng hộp và chữ (đếm ở khung cuối làm mẫu số); độ dày nét = số điểm nhấn liên tiếp theo phương thẳng đứng chia cos(góc);
cao chữ in "KHO" = hộp mực điểm tối ở khung cuối. Chạy: uvx --with numpy --with pillow python -I -B measure_cross.py <đường dẫn jobs>. Ghi cross.json cạnh tệp này."""
import sys, os, json, subprocess, tempfile, glob
import numpy as np
from PIL import Image
JOBS = sys.argv[1] if len(sys.argv) > 1 else ".."
CLIP = "corp-sample-7700960427491986696"; T0, DUR = 41.5, 0.8
ACC = np.array([24, 114, 206]); isacc = lambda a: (np.abs(a - ACC).max(-1) < 55)
tmp = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(T0), "-t", str(DUR), "-i", os.path.join(JOBS, CLIP, "source.mp4"), "-vf", "fps=30", os.path.join(tmp, "f_%03d.png")], check=True)
A = [np.asarray(Image.open(f).convert("RGB")).astype(int) for f in sorted(glob.glob(os.path.join(tmp, "f_*.png")))]
x0, y0, x1, y1 = 100, 720, 700, 1060
cnt = [int(isacc(a[y0:y1, x0:x1]).sum()) for a in A]
last = A[-1]; m = isacc(last[y0:y1, x0:x1]); ys, xs = np.nonzero(m)
first = next(i for i, c in enumerate(cnt) if c > cnt[0] * 1.5 + 200)
# độ dày: tại cột cách trái nét chéo (xs.min()+60) đếm run dọc, chia cos(45)=0.707 -> bề dày vuông góc
runs = []
for cx in range(xs.min() + 40, xs.min() + 110, 7):
    col = m[:, cx]; n = 0; best = 0
    for v in col:
        n = n + 1 if v else 0; best = max(best, n) if n else best
    runs.append(best)
thick = float(np.median(runs)) * 0.707
ink = (last[y0:y1, x0:x1].max(-1) < 60); iy, ix = np.nonzero(ink); H = int(iy.max() - iy.min() + 1)
ys_all, xs_all = ys + y0, xs + x0
out = {"clip": CLIP, "t0_s": T0, "frame_w": 1080, "accent_px_by_frame": cnt, "first_visible_frame": int(first), "full_frame": int(next(i for i, c in enumerate(cnt) if c >= cnt[-1] * 0.97)),
       "draw_frames": int(next(i for i, c in enumerate(cnt) if c >= cnt[-1] * 0.97)) - int(first) + 1, "stroke_px": round(thick, 1), "stroke_over_W": round(thick / 1080, 4), "cap_h_KHO_px": H, "stroke_over_cap_h": round(thick / H, 3),
       "x_bbox_px": [int(xs_all.min()), int(ys_all.min()), int(xs_all.max()), int(ys_all.max())], "colour_rgb": np.median(last[y0:y1, x0:x1][m], 0).astype(int).tolist(), "note": "ước lượng thô (chỉ 1 thể hiện; hộp bao gồm cả khung nét đứt cùng màu nhấn nên x_bbox dư)"}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cross.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
