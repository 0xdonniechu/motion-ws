"""Đo tabs (pill chọn trượt) và cursor (con trỏ chuột) ở clip 7700229527049358612 (TikTok @phantichdulieu.mda), 30fps, khung 1080x1920.
Chạy (cần scipy cho mẫu con trỏ): uvx --with numpy --with pillow --with scipy python -I -B jobs/corp-sample-7700229527049358612/measure_tabs_cursor.py <frames_dir> <t0> <out.json> analyse
Trước đó: ffmpeg -ss 13 -t 5 -i source.mp4 -vsync 0 -start_number 0 tmp/tabs/f_%03d.png (t0=13.0). Sau đó: python -I -B fit_back_edges.py tmp/tabs_fit.json_tmp.raw.json
frames_dir = các khung PNG f_000.png.. cắt bằng ffmpeg từ t0 (không vsync): t = t0 + i/30. Ease khớp bằng EASES/fit_ease của measure_style.py (cùng bộ ứng viên)."""
import sys, os, json, glob, importlib.util
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ms", os.path.join(HERE, "..", "20261028-230040", "measure_style.py")); ms = importlib.util.module_from_spec(spec); spec.loader.exec_module(ms)
FPS = 30
STRIP = (150, 625, 950, 712)      # x0,y0,x1,y1 vùng dải tab (khung 1080x1920)
CUR = (0, 640, 1080, 1500)      # vùng tìm con trỏ
TPL = (580, 685, 640, 750)        # khung mẫu con trỏ ở khung f_060 (t=15.0s)

def load(d):
    fs = sorted(glob.glob(os.path.join(d, "f_*.png")))
    return [np.asarray(Image.open(f).convert("RGB")).astype(int) for f in fs]

def pill_edges(im):
    x0, y0, x1, y1 = STRIP; c = im[y0:y1, x0:x1]
    m = (c[..., 2] > 150) & (c[..., 0] < 70) & (c[..., 1] < 140) & (c[..., 1] > 60)   # xanh đậm của pill
    cols = m.sum(0) > 30
    if cols.sum() < 20: return None
    xs = np.nonzero(cols)[0]; return int(xs[0] + x0), int(xs[-1] + x0)

def make_template(im, box):
    """mẫu con trỏ từ một khung sạch: viền đen (<70) + ruột trắng (lấp lỗ của viền) -> (outline, interior, tip_dx, tip_dy)."""
    from scipy import ndimage as nd
    x0, y0, x1, y1 = box; g = im[y0:y1, x0:x1].mean(2); dark = g < 70
    lab, n = nd.label(dark, structure=np.ones((3, 3))); sizes = nd.sum(dark, lab, range(1, n + 1)); k = 1 + int(np.argmax(sizes))
    ol = lab == k; filled = nd.binary_fill_holes(ol); inter = filled & ~ol & (g > 200)
    ys, xs = np.nonzero(ol); top = ys.min(); tip = int(xs[ys == top].mean())
    sub = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    return ol[sub].astype(float), inter[sub].astype(float), tip - xs.min(), 0

def cursor_tip(im, T):
    from scipy.signal import fftconvolve
    ol, it, dx, dy = T; x0, y0, x1, y1 = CUR; g = im[y0:y1, x0:x1].mean(2)
    D = (g < 70).astype(float); B = (g > 200).astype(float)
    sc = (fftconvolve(D, ol[::-1, ::-1], "valid") / ol.sum() + fftconvolve(B, it[::-1, ::-1], "valid") / max(it.sum(), 1)) / 2
    j = np.unravel_index(int(np.argmax(sc)), sc.shape)
    if sc[j] < 0.80: return None
    return int(j[1] + dx + x0), int(j[0] + dy + y0), round(float(sc[j]), 2)

def norm_fit(ts, vs, a, b, eps=0.03):
    """vs: đại lượng (x) theo khung trong [a,b]; chuẩn hoá 0..1, tìm khung bắt đầu/chạm 98%, khớp ease."""
    v = np.array(vs[a:b + 1], float); t = np.array(ts[a:b + 1]); span = v[-1] - v[0]; p = (v - v[0]) / span
    s = max(next(i for i, q in enumerate(p) if abs(q) > eps) - 1, 0); r = next((i for i, q in enumerate(p) if i >= s and q >= 0.98), len(p) - 1)
    seg = list(range(s, max(r, s + 3) + 1)); den = max(t[seg[-1]] - t[s], 1e-6)
    name, e, bz, eb = ms.fit_ease([(t[i] - t[s]) / den for i in seg], [p[i] for i in seg])
    return {"from_x": round(float(v[0]), 1), "to_x": round(float(v[-1]), 1), "t_start": round(float(t[s]), 3), "reach_s": round(float(t[r] - t[s]), 3), "frames_to_reach": r - s,
            "overshoot": round(float(p.max() - 1), 3), "ease": name, "rmse": round(e, 3), "p": [round(float(q), 2) for q in p[s:r + 3]]}

def main(d, t0, out):
    F = load(d); ts = [t0 + i / FPS for i in range(len(F))]
    T = make_template(F[60], TPL)
    pill = [pill_edges(f) for f in F]; cur = [cursor_tip(f, T) for f in F]
    res = {"t0": t0, "n_frames": len(F), "pill_series": [(round(ts[i], 3), pill[i]) for i in range(len(F)) if pill[i]], "cursor_series": [(round(ts[i], 3), cur[i]) for i in range(len(F)) if cur[i]]}
    json.dump(res, open(out + ".raw.json", "w"), ensure_ascii=False)
    print("pill frames", sum(1 for p in pill if p), "cursor frames", sum(1 for c in cur if c))
    return F, ts, pill, cur

if __name__ == "__main__" and len(sys.argv) <= 4:
    main(sys.argv[1], float(sys.argv[2]), sys.argv[3])

def analyse(d, t0, out):
    """chạy main rồi khớp ease: mỗi cạnh pill (trái/phải), con trỏ (tiến độ theo khoảng cách tới điểm dừng)."""
    F, ts, pill, cur = main(d, t0, out + "_tmp"); res = {"source": "7700229527049358612", "t0": t0, "fps": FPS}
    def seg(series, a, b): return series[a:b + 1]
    L = [p[0] if p else None for p in pill]; R = [p[1] if p else None for p in pill]
    def idx(t): return int(round((t - t0) * FPS))
    out_rows = {}
    for name, (ta, tb) in {"tab1_to_2": (14.30, 15.00), "tab2_to_3": (15.70, 16.50)}.items():
        a, b = idx(ta), idx(tb); r = {}
        for side, S in (("left", L), ("right", R)): r[side] = norm_fit(ts, [s if s is not None else np.nan for s in S], a, b)
        out_rows[name] = r
    res["pill"] = out_rows
    cx = [c for c in cur]
    def glide(ta, tb):
        a, b = idx(ta), idx(tb); pts = [(i, cur[i]) for i in range(a, b + 1) if cur[i]]
        end = pts[-1][1]; dist = [float(np.hypot(c[0] - end[0], c[1] - end[1])) for i, c in pts]
        v = [d for d in dist]; tt = [ts[i] for i, c in pts]; first = pts[0][1]
        return norm_fit(tt, [-x for x in v], 0, len(v) - 1) | {"from": first[:2], "to": end[:2], "dist_px": round(dist[0], 1), "t_first_seen": round(tt[0], 3), "frames_seen": len(pts)}
    res["cursor"] = {"approach": glide(13.60, 14.45), "tab2_to_3_glide": glide(15.30, 15.90)}
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False, indent=1))

if __name__ == "__main__" and len(sys.argv) > 4 and sys.argv[4] == "analyse":
    analyse(sys.argv[1], float(sys.argv[2]), sys.argv[3])
