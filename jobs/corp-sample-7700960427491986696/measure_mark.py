"""Đo vệt tô nhấn vàng (highlight marker) chạy ngang sau chữ, ở quét cuối 2026-11-03: hai clip (7700960427491986696 "hỏi đúng câu.", 7702043938013629716 "nên làm gì?").
Cách đo: tách khung 30fps (quy về rộng 576), vệt = điểm ảnh vàng (R>235, G 180..225, B<120) trong hộp; tiến độ mỗi khung = (xmax-xmin+1)/chiều dài cuối; ngang cuối so với hộp mực chữ (điểm tối, tổng RGB<200)
cùng hộp; cao vệt / cao hộp mực chữ, đỉnh/đáy vệt tính từ đỉnh hộp mực. Khớp ease như measure_strike.py. Chạy: uvx --with numpy --with pillow python -I -B measure_mark.py <đường dẫn jobs>. Ghi mark.json cạnh tệp này."""
import sys, os, json, subprocess, tempfile, glob
import numpy as np
from PIL import Image
JOBS = sys.argv[1] if len(sys.argv) > 1 else ".."
# (nhãn, clip, t bắt đầu, độ dài s, hộp (x0,y0,x1,y1) ở khung rộng 576)
CASES = [("hỏi đúng câu.", "corp-sample-7700960427491986696", 149.6, 1.0, (100, 612, 440, 690)), ("nên làm gì?", "corp-sample-7702043938013629716", 140.0, 2.2, (190, 520, 440, 610))]
EASES = {"linear": lambda u: u, "sine.out": lambda u: np.sin(u * np.pi / 2), "power1.out": lambda u: 1 - (1 - u) ** 2, "power2.out": lambda u: 1 - (1 - u) ** 3,
         "power3.out": lambda u: 1 - (1 - u) ** 4, "expo.out": lambda u: np.where(u >= 1, 1, 1 - 2 ** (-10 * u)), "circ.out": lambda u: np.sqrt(1 - (1 - u) ** 2)}
def frames(clip, t, d):
    tmp = tempfile.mkdtemp(); subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-t", str(d), "-i", os.path.join(JOBS, clip, "source.mp4"), "-vf", "fps=30,scale=576:-1", os.path.join(tmp, "f_%03d.png")], check=True)
    return [np.asarray(Image.open(f).convert("RGB")).astype(int) for f in sorted(glob.glob(os.path.join(tmp, "f_*.png")))]
def fit(p):
    best = None
    for name, f in EASES.items():
        for D in np.arange(1.5, 14.01, 0.25):
            for t0 in np.arange(-2.0, 1.01, 0.05):
                pred = np.clip(f(np.clip((np.arange(len(p)) - t0) / D, 0, 1)), 0, 1); r = float(np.sqrt(np.mean((pred - p) ** 2)))
                if best is None or r < best[0]: best = (r, name, float(D), float(t0))
    return best
yel = lambda c: (c[..., 0] > 235) & (c[..., 1] > 180) & (c[..., 1] < 225) & (c[..., 2] < 120)
out = []
for label, clip, t, d, (x0, y0, x1, y1) in CASES:
    fr = frames(clip, t, d); ext = []
    for f in fr:
        m = yel(f[y0:y1, x0:x1]); ys, xs = np.nonzero(m); ext.append((int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())) if m.sum() > 30 else None)
    s = next(i for i, e in enumerate(ext) if e); fin = ext[-1]; length = fin[1] - fin[0] + 1
    p = np.array([0.0] + [((e[1] - e[0] + 1) / length) if e else 0 for e in ext[s:]]); r, name, D, t0 = fit(p[:14])
    last = fr[-1][y0:y1, x0:x1]; ink = last.sum(-1) < 200; ys, xs = np.nonzero(ink[:, fin[0]:fin[1] + 1]); it, ib = int(ys.min()), int(ys.max()); ih = ib - it + 1
    col = np.median(last[yel(last)], 0).astype(int)
    rec = {"clip": clip, "text": label, "frame_w": 576, "start_frame_in_window": s, "marker_len_px": length, "marker_h_px": fin[3] - fin[2] + 1, "ink_h_px": ih, "marker_h_over_ink_h": round((fin[3] - fin[2] + 1) / ih, 3),
           "marker_top_from_ink_top_over_ink_h": round((fin[2] - it) / ih, 3), "marker_bottom_from_ink_top_over_ink_h": round((fin[3] - it) / ih, 3),
           "ink_x_range": [int(xs.min()) + fin[0], int(xs.max()) + fin[0]], "marker_x_range": [fin[0] + x0, fin[1] + x0], "progress_by_frame": [round(float(v), 3) for v in p[:14]], "best_fit": {"ease": name, "dur_frames": D, "dur_s": round(D / 30, 3), "t0_frames": round(t0, 2), "rmse": round(r, 4)}, "colour_rgb": col.tolist()}
    out.append(rec); print(json.dumps(rec, ensure_ascii=False))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mark.json"), "w"), ensure_ascii=False, indent=1)
