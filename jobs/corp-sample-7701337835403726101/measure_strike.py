"""Đo vạch gạch ngang chữ (strike) ở quét cuối 2026-11-03. Cách đo: tách khung 30fps quanh lúc vạch hiện (ffmpeg), vạch = điểm ảnh cùng màu nhấn (#1872ce, dung sai 30)
trên hàng giữa vạch; chiều dài vạch mỗi khung = đoạn liên tục từ mép trái vạch; dày = số hàng nhấn ở cột sát mép trái vạch (vượt ra ngoài chữ); chữ = hộp mực khung TRƯỚC lúc gạch;
màu chữ sau = trung vị điểm mực ngoài vạch. Khớp ease: tiến độ p(n) = ease((n - t0)/D), duyệt t0 (khung) và D (khung) cho từng họ ease, rmse nhỏ nhất.
Chạy: uvx --with numpy --with pillow python -I -B measure_strike.py <đường dẫn jobs>  (ffmpeg có sẵn). Ghi strike.json cạnh tệp này."""
import sys, os, json, subprocess, tempfile, glob
import numpy as np
from PIL import Image
JOBS = sys.argv[1] if len(sys.argv) > 1 else ".."
ACC = np.array([24, 114, 206])
# (nhãn, clip, t bắt đầu, độ dài s, hộp tìm (x0,y0,x1,y1), chỉ số khung trước lúc gạch)
CASES = [("101", "corp-sample-7701337835403726101", 34.0, 2.0, (150, 450, 450, 585), 39),
         ("CÁI SAI.", "corp-sample-7701337835403726101", 37.6, 0.8, (30, 250, 430, 340), 12)]
EASES = {"linear": lambda u: u, "sine.out": lambda u: np.sin(u * np.pi / 2), "power1.out": lambda u: 1 - (1 - u) ** 2, "power2.out": lambda u: 1 - (1 - u) ** 3,
         "power3.out": lambda u: 1 - (1 - u) ** 4, "power4.out": lambda u: 1 - (1 - u) ** 5, "expo.out": lambda u: np.where(u >= 1, 1, 1 - 2 ** (-10 * u)), "circ.out": lambda u: np.sqrt(1 - (1 - u) ** 2)}
def frames(clip, t, d):
    tmp = tempfile.mkdtemp(); subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-t", str(d), "-i", os.path.join(JOBS, clip, "source.mp4"), "-vf", "fps=30", os.path.join(tmp, "f_%03d.png")], check=True)
    fs = sorted(glob.glob(os.path.join(tmp, "f_*.png"))); return [np.asarray(Image.open(f).convert("RGB")).astype(int) for f in fs]
isacc = lambda c: (np.abs(c - ACC).max(-1) < 30)
def fit(p):
    best = None
    for name, f in EASES.items():
        for D in np.arange(1.5, 14.01, 0.25):
            for t0 in np.arange(-2.0, 1.01, 0.05):
                pred = np.clip(f(np.clip((np.arange(len(p)) - t0) / D, 0, 1)), 0, 1); r = float(np.sqrt(np.mean((pred - p) ** 2)))
                if best is None or r < best[0]: best = (r, name, float(D), float(t0))
    return best
out = []
for label, clip, t, d, (x0, y0, x1, y1), pre in CASES:
    fr = frames(clip, t, d); H, W = fr[0].shape[:2]
    c = fr[pre][y0:y1, x0:x1]; bg = np.median(c.reshape(-1, 3), 0); ink = np.abs(c - bg).sum(2) > 200; ys, xs = np.nonzero(ink)
    gx0, gx1, gy0, gy1 = xs.min() + x0, xs.max() + x0, ys.min() + y0, ys.max() + y0   # hộp mực chữ trước lúc gạch
    last = fr[-1]; band = isacc(last[y0:y1, x0:x1]); rows = band.sum(1); ly = int(rows.argmax()) + y0   # hàng giữa vạch
    cols = np.nonzero(band[ly - y0])[0]; lx0 = int(cols.min()) + x0
    thick = int(band[:, lx0 - x0 + 2].sum())
    lens = []
    for f in fr:
        row = isacc(f[ly, lx0:x1]); n = 0
        while n < len(row) and row[n]: n += 1
        lens.append(n)
    final = lens[-1]; s = next(i for i, v in enumerate(lens) if v > 0); p = np.array(lens[s - 1:], float) / final; r, name, D, t0 = fit(p)
    rowsink = last[y0:y1, x0:x1]; textmask = (np.abs(rowsink - bg).sum(2) > 200) & ~isacc(rowsink); col = np.median(rowsink[textmask], 0).astype(int)
    rec = {"clip": clip, "text": label, "start_frame_in_window": s, "frame_w": W, "cap_h_px": int(gy1 - gy0 + 1), "text_w_px": int(gx1 - gx0 + 1), "line_len_px": final, "line_len_over_text_w": round(final / (gx1 - gx0 + 1), 3),
           "overshoot_left_px": int(gx0 - lx0), "overshoot_right_px": int(lx0 + final - 1 - gx1), "thick_px": thick, "thick_over_cap_h": round(thick / (gy1 - gy0 + 1), 3), "line_cy_from_cap_top_over_cap_h": round((ly - gy0) / (gy1 - gy0 + 1), 3),
           "progress_by_frame": [round(float(v), 3) for v in p], "best_fit": {"ease": name, "dur_frames": D, "dur_s": round(D / 30, 3), "t0_frames": round(t0, 2), "rmse": round(r, 4)}, "text_colour_after_rgb": col.tolist(), "line_colour_rgb": last[ly, lx0 + final // 2].tolist()}
    out.append(rec); print(json.dumps(rec, ensure_ascii=False))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "strike.json"), "w"), ensure_ascii=False, indent=1)
