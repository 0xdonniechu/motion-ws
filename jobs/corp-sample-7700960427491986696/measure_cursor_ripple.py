"""Đo con trỏ độc lập + gợn sóng lúc bấm (quét 2026-11-04). Clip 7700960427491986696 (1080x1920), lần bấm vào ô "Tìm bộ dữ liệu..." ở ~44.2-45.0s.
Cách đo (30fps, ffmpeg tách khung): con trỏ = thành phần liên thông điểm tối (max RGB < 60) cỡ ~40x55 (góc trái-trên của hộp = đầu mũi tên; cùng quy ước kit: phần tử đặt tại điểm này);
lướt: p(n) = (x0 - x(n)) / (x0 - x_cuối) của đầu mũi tên, khớp ease/t0/D như measure_strike.py; bấm: tỉ lệ cao hộp con trỏ so với 55px (neo ở đầu mũi tên);
gợn: tâm cố định tại đầu mũi tên (-2,-2px); bán kính = đỉnh hồ sơ xuyên tâm của (B-R) so nền; độ đậm = biên độ đỉnh / biên độ khung đầu; độ dày = số px ở nửa biên độ.
Chạy: uvx --with numpy --with pillow --with scipy python -I -B measure_cursor_ripple.py <đường dẫn jobs>. Ghi cursor_ripple.json cạnh tệp này."""
import sys, os, json, subprocess, tempfile, glob
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
JOBS = sys.argv[1] if len(sys.argv) > 1 else ".."
CLIP = "corp-sample-7700960427491986696"; T0, DUR = 44.0, 1.6
EASES = {"linear": lambda u: u, "sine.inOut": lambda u: -(np.cos(np.pi * u) - 1) / 2, "power1.inOut": lambda u: np.where(u < .5, 2 * u * u, 1 - 2 * (1 - u) ** 2),
         "power2.inOut": lambda u: np.where(u < .5, 4 * u ** 3, 1 - 4 * (1 - u) ** 3), "power3.inOut": lambda u: np.where(u < .5, 8 * u ** 4, 1 - 8 * (1 - u) ** 4),
         "power4.inOut": lambda u: np.where(u < .5, 16 * u ** 5, 1 - 16 * (1 - u) ** 5), "expo.inOut": lambda u: np.where(u <= 0, 0, np.where(u >= 1, 1, np.where(u < .5, 2 ** (20 * u - 10) / 2, (2 - 2 ** (-20 * u + 10)) / 2))),
         "circ.inOut": lambda u: np.where(u < .5, (1 - np.sqrt(np.clip(1 - (2 * u) ** 2, 0, 1))) / 2, (np.sqrt(np.clip(1 - (-2 * u + 2) ** 2, 0, 1)) + 1) / 2),
         "sine.out": lambda u: np.sin(u * np.pi / 2), "power2.out": lambda u: 1 - (1 - u) ** 3, "power3.out": lambda u: 1 - (1 - u) ** 4, "expo.out": lambda u: np.where(u >= 1, 1, 1 - 2 ** (-10 * u))}
tmp = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(T0), "-t", str(DUR), "-i", os.path.join(JOBS, CLIP, "source.mp4"), "-vf", "fps=30", os.path.join(tmp, "f_%03d.png")], check=True)
fr = [np.asarray(Image.open(f).convert("RGB")).astype(float) for f in sorted(glob.glob(os.path.join(tmp, "f_*.png")))]
def cursor(a):
    sub = a[480:1000]; lab, n = ndi.label(sub.max(-1) < 60)
    for j, sl in enumerate(ndi.find_objects(lab)):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if 36 <= h <= 60 and 26 <= w <= 44: return sl[1].start, sl[0].start + 480, w, h
    return None
tr = [cursor(a) for a in fr]
def fit(p, lo, hi):
    best = None
    for name, f in EASES.items():
        for D in np.arange(2.0, 14.01, 0.25):
            for t0 in np.arange(lo - 3, hi + 1.01, 0.05):
                pred = np.clip(f(np.clip((np.arange(len(p)) - t0) / D, 0, 1)), 0, 1); r = float(np.sqrt(np.mean((pred - p) ** 2)))
                if best is None or r < best[0]: best = (r, name, float(D), float(t0))
    return best
# lướt tới ô tìm kiếm: đoạn từ lúc đứng yên cuối (x ~ 862) tới điểm bấm
xs = np.array([t[0] if t else np.nan for t in tr]); ys = np.array([t[1] if t else np.nan for t in tr])
end = int(next(i for i in range(len(xs)) if xs[i] < 526))   # khung đầu tiên con trỏ tới ô (x ~ 522; sau đó chỉ còn rung nhẹ)
x_end = xs[end]; start = max(i for i in range(end) if abs(xs[i] - xs[0]) < 1.5 and not np.isnan(xs[i]))
p = (xs[start:end + 1] - xs[start]) / (x_end - xs[start]); r, name, D, t0 = fit(p, 0, len(p))
glide = {"start_frame_in_window": int(start), "end_frame_in_window": int(end), "from_xy": [float(xs[start]), float(ys[start])], "to_xy": [float(x_end), float(ys[end])], "distance_px": round(float(np.hypot(xs[start] - x_end, ys[start] - ys[end])), 1),
         "progress_by_frame": [round(float(v), 3) for v in p], "best_fit": {"ease": name, "dur_frames": D, "dur_s": round(D / 30, 3), "t0_frames": round(t0, 2), "rmse": round(r, 4)}}
rank = []   # khớp TỰ DO (D, t0) riêng cho từng ease, để so công bằng giữa các họ (9 mẫu: kết quả chỉ chỉ hướng)
for n_, f_ in EASES.items():
    b_ = None
    for D_ in np.arange(2.0, 14.01, 0.25):
        for t0_ in np.arange(-3, len(p) + 0.01, 0.05):
            e_ = float(np.sqrt(np.mean((np.clip(f_(np.clip((np.arange(len(p)) - t0_) / D_, 0, 1)), 0, 1) - p) ** 2)))
            if b_ is None or e_ < b_[0]: b_ = (e_, D_, t0_)
    # khoảng 2% -> 98% của ease đó (khung) để so với khoảng đo được 0.015 -> 0.985
    u = np.linspace(0, 1, 4001); y = f_(u); span = float((u[np.argmax(y >= .98)] - u[np.argmax(y >= .02)]) * b_[1])
    rank.append({"ease": n_, "rmse": round(b_[0], 4), "dur_frames": b_[1], "dur_s": round(b_[1] / 30, 3), "t0_frames": round(b_[2], 2), "span_2_to_98_frames": round(span, 2)})
rank.sort(key=lambda r: r["rmse"]); glide["fit_ranking"] = rank
# bấm: co mũi tên neo ở đầu
sq = [round(t[3] / 55.0, 3) if t else None for t in tr[end - 1:end + 12]]
click_frame = end + next(i for i, t in enumerate(tr[end:]) if t and t[3] < 53)
glide["click_after_tween_start_s"] = round((click_frame - start - t0) / 30, 3)   # khung co đầu tiên - khung bắt đầu tween (khớp tự do của ease tốt nhất)
# gợn: tâm = đầu mũi tên - (2,2)
cx, cy = tr[end][0] - 2, tr[end][1] - 2
x0, y0, x1, y1 = cx - 140, cy - 90, cx + 140, cy + 110; yy, xx = np.mgrid[y0:y1, x0:x1]; rr = np.hypot(xx - cx, yy - cy)
ring = []
for i in range(end, min(end + 22, len(fr))):
    sub = fr[i][y0:y1, x0:x1]; br = sub[..., 2] - sub[..., 0]; ok = ~ndi.binary_dilation(sub.max(-1) < 110, iterations=5); base = float(np.median(br[ok & (rr > 70)]))
    prof = np.array([(br[ok & (rr >= R - .75) & (rr < R + .75)].mean() - base) if (ok & (rr >= R - .75) & (rr < R + .75)).sum() > 6 else 0 for R in np.arange(0, 70, 1.0)])
    k = int(prof.argmax()); ring.append({"frame": i, "R_px": float(k), "amp": round(float(prof[k]), 1), "fwhm_px": int((prof > prof[k] / 2).sum())})
first = next(i for i, g in enumerate(ring) if g["amp"] > 40)
live = [g for g in ring[first:] if g["amp"] > 5 and g["R_px"] < 60]; n0 = live[0]["frame"]
R = np.array([g["R_px"] for g in live]); A = np.array([g["amp"] for g in live]) / live[0]["amp"]; nn = np.arange(len(live))
slope, icpt = np.polyfit(nn, R, 1)
ALPHA = {"linear": lambda u: 1 - u, "power1.out": lambda u: (1 - u) ** 2, "power2.out": lambda u: (1 - u) ** 3, "power1.in": lambda u: 1 - u ** 2, "power2.in": lambda u: 1 - u ** 3, "sine.in": lambda u: np.cos(u * np.pi / 2), "sine.inOut": lambda u: (np.cos(np.pi * u) + 1) / 2}
afit = None
for nm, f in ALPHA.items():
    for D_ in np.arange(8, 16.01, 0.25):
        pred = f(np.clip(nn / D_, 0, 1)); e = float(np.sqrt(np.mean((pred - A) ** 2)))
        if afit is None or e < afit[0]: afit = (e, nm, float(D_))
sample = fr[n0][int(cy) - 80:int(cy) + 80, int(cx) - 80:int(cx) + 80]; brs = sample[..., 2] - sample[..., 0]; idx = np.unravel_index(np.argmax(brs), brs.shape); col = sample[idx].astype(int).tolist()
out = {"clip": CLIP, "t0_s": T0, "cursor_box_px": [40, 55], "glide": glide, "click": {"first_squish_frame_in_window": int(click_frame), "height_ratio_by_frame_from_end-1": sq, "min_scale": min(s for s in sq if s)},
       "ripple": {"centre_xy": [float(cx), float(cy)], "first_frame_in_window": int(n0), "frames_visible": len(live), "R_px_by_frame": R.tolist(), "R_slope_px_per_frame": round(float(slope), 2), "R_start_px": round(float(icpt), 1), "R_end_px": float(R[-1]),
                  "alpha_by_frame_rel_first": [round(float(v), 3) for v in A], "alpha_fit": {"ease_of_1-minus": afit[1], "dur_frames": afit[2], "rmse": round(afit[0], 3)}, "stroke_fwhm_px": int(np.median([g["fwhm_px"] for g in live])), "colour_rgb_first_frame": col, "amp_first_BminusR": live[0]["amp"]}}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cursor_ripple.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
