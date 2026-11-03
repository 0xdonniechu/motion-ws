"""Đo nét bút vẽ tay (khoanh tròn + dấu tick) ở clip 7702043938013629716 (576x1024), 117.3-118.9s (quét 2026-11-04): bút khoanh biểu tượng cột ở thẻ "Kênh A chậm lại" rồi gạch dấu tick.
Cách đo (30fps): nét = điểm cùng màu nhấn (#1872ce, dung sai 55). Khoanh: tâm/bán kính từ khung cuối (dựng tay, 114,455, rx 50, ry 47; vòng vẽ tay lệch +-4px), tiến độ = số bin góc (72 bin, 5 độ)
liên tục tính từ bin bắt đầu theo chiều quét (chỉ lấy các khung bút đã chạm vòng, bỏ khung kính lúp xanh đi ngang và khung bút che); độ dày = số điểm nhấn liên tiếp theo pháp tuyến ở nhiều góc trên khung cuối;
cao chữ in K của "Kênh A" = hộp mực điểm tối ở khung cuối. Tick: số điểm nhấn trong hộp dưới vòng, trừ phần vòng (nền = số ở khung 28) chia (cuối - nền).
Chạy: uvx --with numpy --with pillow python -I -B measure_pen.py <đường dẫn jobs>. Ghi pen.json cạnh tệp này. CHỈ 1 clip có bút vẽ dần; ở clip 7700960427491986696 dấu X chéo và clip 7701337835403726101 vạch chéo hiện đủ trong 1 khung (xem preset.md)."""
import sys, os, json, subprocess, tempfile, glob
import numpy as np
from PIL import Image
JOBS = sys.argv[1] if len(sys.argv) > 1 else ".."
CLIP = "corp-sample-7702043938013629716"; T0, DUR = 117.3, 1.6
ACC = np.array([24, 114, 206]); isacc = lambda a: (np.abs(a - ACC).max(-1) < 55)
tmp = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(T0), "-t", str(DUR), "-i", os.path.join(JOBS, CLIP, "source.mp4"), "-vf", "fps=30", os.path.join(tmp, "f_%03d.png")], check=True)
A = [np.asarray(Image.open(f).convert("RGB")).astype(int) for f in sorted(glob.glob(os.path.join(tmp, "f_*.png")))]
last = A[-1]; cx, cy, rx, ry = 114.0, 455.0, 50.0, 47.0; NB = 72; th = np.linspace(0, 2 * np.pi, NB, endpoint=False)
def cov(a):
    m = isacc(a); out = np.zeros(NB, bool)
    for k, t in enumerate(th):
        for d in np.arange(-8, 9, 1.0):
            if m[int(round(cy + (ry + d) * np.sin(t))), int(round(cx + (rx + d) * np.cos(t)))]: out[k] = True; break
    return out
# độ dày nét ở khung cuối: bề dày theo pháp tuyến tại các góc xa chữ (trái 160-200 độ, trên 250-290)
thick = []
for ang in list(range(160, 201, 10)) + list(range(250, 291, 10)):
    t = np.deg2rad(ang); best = 0
    for d0 in np.arange(-8, 9, 1.0):
        n = 0; d = d0
        while d < 12 and isacc(last)[int(round(cy + (ry + d) * np.sin(t))), int(round(cx + (rx + d) * np.cos(t)))]: n += 1; d += 1
        best = max(best, n)
    thick.append(best)
K = last[420:452, 168:200]; ink = K.max(-1) < 60; ys, xs = np.nonzero(ink); cap_h = int(ys.max() - ys.min() + 1)
cols = np.array([last[int(round(cy + ry * np.sin(t))), int(round(cx + rx * np.cos(t)))] for t in th[::6]]); ring_col = np.median(cols[isacc(cols)], 0).astype(int).tolist()
runs = []
for i, a in enumerate(A[16:30], 16):
    c = cov(a); start = 47; n = 0
    while n < NB and c[(start + n) % NB]: n += 1
    runs.append(n)
EASES = {"linear": lambda u: u, "sine.inOut": lambda u: -(np.cos(np.pi * u) - 1) / 2, "power1.inOut": lambda u: np.where(u < .5, 2 * u * u, 1 - 2 * (1 - u) ** 2), "power2.inOut": lambda u: np.where(u < .5, 4 * u ** 3, 1 - 4 * (1 - u) ** 3),
         "power2.in": lambda u: u ** 3, "power1.in": lambda u: u ** 2, "power2.out": lambda u: 1 - (1 - u) ** 3, "power1.out": lambda u: 1 - (1 - u) ** 2, "sine.out": lambda u: np.sin(u * np.pi / 2)}
def fit(p, idx):
    best = None
    for name, f in EASES.items():
        for D in np.arange(2.0, 14.01, 0.25):
            for t0 in np.arange(idx.min() - 4, idx.max() + 1.01, 0.1):
                pred = np.clip(f(np.clip((idx - t0) / D, 0, 1)), 0, 1); r = float(np.sqrt(np.mean((pred - p) ** 2)))
                if best is None or r < best[0]: best = (r, name, float(D), float(t0))
    return best
ci = np.arange(16, 30); crun = np.array(runs, float)
use = np.array([i in (17, 18, 19, 20, 21, 22, 24, 25, 29) for i in ci])   # khung bút chạm vòng liên tục; 23 có cung giả của thân bút, 26-28 đã kín (cộng thêm 1.0)
cp = np.where(ci >= 24, 1.0, crun / NB); cidx = ci[use]; cpv = cp[use]; cr, cn, cD, ct0 = fit(cpv, cidx.astype(float))
def tickcount(a): return int(isacc(a[497:545, 118:182]).sum())
tc = np.array([tickcount(A[i]) for i in range(28, 40)], float); base = tc[0]; final = tc[-1]; tp = (tc - base) / (final - base); tidx = np.arange(28, 40).astype(float); sel = (tp >= -0.05)
tr, tn, tD, tt0 = fit(np.clip(tp, 0, 1), tidx)
out = {"clip": CLIP, "t0_s": T0, "frame_w": 576, "circle": {"centre_xy": [cx, cy], "rx_ry_px": [rx, ry], "stroke_px": float(np.median(thick)), "stroke_px_samples": thick, "stroke_over_W": round(float(np.median(thick)) / 576, 4), "cap_h_of_K_px": cap_h, "stroke_over_cap_h": round(float(np.median(thick)) / cap_h, 3),
                    "stroke_over_diameter": round(float(np.median(thick)) / (rx + ry), 3), "leading_edge_bins_by_frame": dict(zip([int(x) for x in ci], [int(x) for x in runs])), "start_frame_in_window": 17,
                    "frames_to_close": 8, "dur_s": round(8 / 30, 3), "progress_used": dict(zip([int(x) for x in cidx], [round(float(x), 3) for x in cpv])), "best_fit": {"ease": cn, "dur_frames": cD, "dur_s": round(cD / 30, 3), "t0_frames": round(ct0, 2), "rmse": round(cr, 3)}, "colour_rgb": ring_col, "wobble_px": 4},
       "tick": {"count_by_frame": dict(zip([int(x) for x in tidx], [int(x) for x in tc])), "progress": [round(float(x), 3) for x in tp], "best_fit": {"ease": tn, "dur_frames": tD, "dur_s": round(tD / 30, 3), "t0_frames": round(tt0, 2), "rmse": round(tr, 3)}, "start_frame_in_window": 28, "end_frame_in_window": 35}}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pen.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
