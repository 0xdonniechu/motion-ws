# Đo DNA phong cách (style teardown) của một clip motion-graphic dọc. Chỉ cần numpy + ffmpeg/ffprobe.
# Chạy từ bất kỳ đâu (nguồn không tin cậy: luôn `-I -B`, truyền đường dẫn bằng đối số; mặc định đọc source.mp4, cuts.json, tmp/ cạnh script):
#   uvx --with numpy python -I -B measure_style.py [--src source.mp4] [--cuts cuts.json] [--energy tmp/energy.json] <lệnh> ...
# Khung đọc 30fps qua ống rawvideo của ffmpeg; toạ độ in ra theo khung gốc W x H của nguồn (720x1280); đo bằng phân số H/W rồi nhân ra 1080x1920 (x1.5).
# Tái tạo toàn bộ số trong presets/corporate-motion/style.json (4 clip, mỗi clip có instances.json):
#   for c in jobs/20261028-230040 jobs/corp-sample-*; do uvx --with numpy python -I -B jobs/20261028-230040/measure_style.py --clip $c measure-clip; done
#   uvx --with numpy python -I -B jobs/20261028-230040/measure_style.py merge-style jobs/20261028-230040 jobs/corp-sample-* --out presets/corporate-motion/style.json
# Cắt cảnh (đã chạy, kết quả nằm trong cuts.json): energy -> candidates --thr 4 -> strips (duyệt bằng mắt) -> cuts --times ... --total 165.4
# Lệnh dùng lại cho clip khác (hộp = x0 y0 x1 y1 theo px khung gốc; mặt nạ = --rgb R,G,B,tol | --dark L | --light L | --sat S; --minrow N bỏ nhiễu):
#   info                               kích thước, fps, thời lượng
#   energy [--out]                     năng lượng |khung(t)-khung(t-1)| (xám 180x320) và tỉ lệ điểm đổi > 25, từng khung -> tmp/energy.json
#   candidates [--thr 4]               cụm năng lượng > thr (ứng viên cắt) + phân loại sơ bộ
#   cuts --times a,b,c [--total T]     chốt mốc cắt: bám vào đỉnh năng lượng gần nhất (±0.3s) -> cuts.json {"S","TOTAL","fps"}
#   strips t1,t2,.. --out x.jpg        dải khung -0.3..+0.5s bước 0.1s quanh từng mốc (duyệt kiểu chuyển cảnh)
#   grid t0 dur fps cols w --out x.jpg lưới khung để chọn hộp đo bằng mắt;  sheets [--fps 4]  contact sheet từng cảnh -> frames/shotNN.jpg
#   transitions                        phân loại từng điểm cắt: hard | wash | dissolve | bar-wipe | flash-wipe (luật in trong docstring) + đếm
#   palette t0 t1 [k] [--sat S] | palette-types [k] [--types types.json] | sample t x y [r]     màu chủ đạo + tỉ lệ diện tích (theo loại cảnh), màu một điểm
#   textrows t x0 y0 x1 y1 [thr]       số liệu chữ: dòng, x-height, nét, khe chữ, bước dòng, phân số H
#   scan t x|y idx a b [--thr]         đoạn khác nền dọc một đường (rộng nét, lề, mép thẻ);  corner t x0 y0 x1 y1 tl|tr|bl|br <mặt nạ>  bán kính góc;  shadow t x|y idx a len  bóng đổ
#   inkmap                             vùng an toàn/lề: phân bố mực theo dải dọc/ngang + hộp bao nội dung
#   series t0 t1 x0 y0 x1 y1 <mặt nạ> | onset ... --min A      diện tích, bbox, tâm từng khung của mặt nạ; khung đầu tiên có mặt nạ
#   ease t0 t1 x0 y0 x1 y1 <mặt nạ> --axis x|x1|y|y1|w|h|cx|cy|area [--pre t,giá trị]   chuẩn hoá 0..1, bắt đầu/reach/settle, quá đà, khớp ease (GSAP gần nhất + cubic-bezier)
#   typed t0 t1 x0 y0 x1 y1 <mặt nạ con trỏ>   ký tự/giây từ bước nhảy của con trỏ;  vscroll t0 t1 [--dir y|x]   dịch camera toàn cục từng khung
#   spread / changes / dwell t0 t1 box --thr / holds / bursts / energyprofile / rhythm    nhịp: bán kính node, khung đổi, thời gian chữ đứng yên, đợt chuyển động, hồ sơ năng lượng, độ dài cảnh + dừng cuối cảnh
#   build-style [--style out.json]     đo lại cả 4 clip (20261028-230040 + corp-sample-*) và gộp thành style.json (tái tạo toàn bộ)
#   measure-clip --clip DIR            đo cả clip theo DIR/instances.json -> DIR/tmp/measured.json;  merge-style DIR1 DIR2 .. --out style.json   gộp các clip: giá trị từng clip, trung vị, khoảng, n, CORE/OPTIONAL
#   cuts-rule [--out cuts_rule.json]   mốc cắt theo luật chung (E đỉnh >= 9 hoặc D đỉnh >= 0.15, cách >= 1s) để so sánh nhiều clip
import sys, os, json, subprocess, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30


def sh(cmd, **kw): return subprocess.run(cmd, capture_output=True, check=True, **kw).stdout


def probe(src):
    o = json.loads(sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,duration,codec_name,bit_rate", "-of", "json", src]))["streams"][0]
    n, d = o["r_frame_rate"].split("/"); o["fps"] = float(n) / float(d); return o


def read_frames(src, t0, dur, w=None, h=None, pix="rgb24", start_exact=True):
    """mảng (n,h,w,c) uint8 ở 30fps từ t0 dài dur. w,h None -> độ phân giải gốc."""
    p = probe(src); W, H = p["width"], p["height"]; w = w or W; h = h or H
    vf = f"fps={FPS}" + (f",scale={w}:{h}" if (w, h) != (W, H) else "") + f",format={pix}"
    raw = sh(["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", src, "-vf", vf, "-f", "rawvideo", "-"])
    c = 1 if pix == "gray" else 3
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, c)


def frame_at(src, t, **kw): return read_frames(src, t, 1.5 / FPS, **kw)[0]


def parse_opts(argv):
    pos, opt, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"): opt[a[2:]] = argv[i + 1]; i += 2
            else: opt[a[2:]] = True; i += 1
        else: pos.append(a); i += 1
    return pos, opt


def hexc(c): return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)


def load_cuts(path):
    c = json.load(open(path)); return c["S"], c.get("TOTAL", c["S"][-1])


# ---------------------------------------------------------------- energy / cuts
def energy(src, out):
    W, H = 180, 320
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    n = W * H; prev = None; E, D = [], []
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        g = np.frombuffer(b, np.uint8).reshape(H, W).astype(np.int16)
        if prev is not None:
            d = np.abs(g - prev); E.append(round(float(d.mean()), 3)); D.append(round(float((d > 25).mean()), 4))
        prev = g
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump({"E": E, "D": D}, open(out, "w"))
    E = np.array(E); print(f"{len(E)} khung; năng lượng TB {E.mean():.3f} trung vị {np.median(E):.3f} p95 {np.percentile(E, 95):.2f} p99 {np.percentile(E, 99):.2f} -> {out}")


def load_energy(path):
    d = json.load(open(path)); return np.array(d["E"]), np.array(d["D"])


def clusters(E, thr, gap=12):
    idx = np.nonzero(E > thr)[0]
    if not len(idx): return []
    cl, cur = [], [idx[0]]
    for i in idx[1:]:
        if i - cur[-1] <= gap: cur.append(i)
        else: cl.append(cur); cur = [i]
    cl.append(cur); return cl


def classify(E, D, c):
    """hard: đỉnh <= 2 khung và > 25% điểm ảnh đổi; wash: năng lượng cao nhưng < 8% điểm ảnh đổi (nền đổi sắc toàn cục);
    flash: một khung > 25% điểm đổi trong cụm dài; motion: còn lại."""
    pk = c[int(np.argmax(E[c]))]
    big = [i for i in c if D[i] > 0.25]
    if big and len(c) <= 3: return "hard"
    if D[pk] < 0.08 and len(c) <= 10: return "wash"
    if big: return "hard+motion"
    return "motion"


def candidates(epath, thr):
    E, D = load_energy(epath); rows = []
    for c in clusters(E, thr):
        pk = c[int(np.argmax(E[c]))]
        rows.append({"t0": round((c[0] + 1) / FPS, 3), "t1": round((c[-1] + 1) / FPS, 3), "pk": round((pk + 1) / FPS, 3), "E": round(float(E[pk]), 1), "D": round(float(D[pk]), 3), "n": len(c), "kind": classify(E, D, c)})
    for r in rows: print(f"pk={r['pk']:.3f} t0={r['t0']:.3f} t1={r['t1']:.3f} E={r['E']:.1f} D={r['D']:.2f} n={r['n']} {r['kind']}")
    return rows


def write_cuts(epath, times, total, out):
    E, D = load_energy(epath); S = [0.0]
    for t in times:
        i0 = max(int(round((t - 0.3) * FPS)) - 1, 0); i1 = min(int(round((t + 0.3) * FPS)), len(E))
        j = i0 + int(np.argmax(E[i0:i1])); s = round((j + 1) / FPS, 3)   # khung j+1 là khung đầu tiên khác khung trước
        S.append(s)
    S.append(round(total, 3))
    json.dump({"S": S, "TOTAL": round(total, 3), "fps": FPS}, open(out, "w"))
    print(len(S) - 1, "cảnh ->", out); print(S)


# ---------------------------------------------------------------- strips / sheets
def strips(src, times, out, w=96, back=0.3, fwd=0.5, step=0.1):
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True); rows = []
    n = int(round((back + fwd) / step)) + 1
    for k, t in enumerate(times):
        r = f"{out}.row{k:02d}.png"; t0 = max(t - back, 0)
        sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{back + fwd + 0.01:.3f}", "-i", src, "-vf", f"fps={1 / step},scale={w}:-1,tile={n}x1", "-frames:v", "1", r])
        rows.append(r)
    cmd = ["ffmpeg", "-v", "error", "-y"] + sum([["-i", r] for r in rows], []) + ["-filter_complex", f"vstack=inputs={len(rows)}", "-frames:v", "1", out]
    sh(cmd); [os.remove(r) for r in rows]; print(out, times)


def sheets(src, cuts, outdir, fps=4):
    S, T = load_cuts(cuts); os.makedirs(outdir, exist_ok=True)
    for k in range(len(S) - 1):
        a, d = S[k], S[k + 1] - S[k]; n = max(int(d * fps), 1); cols = min(n, 8); rows = math.ceil(n / cols)
        sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", src, "-vf", f"fps={fps},scale=135:-1,tile={cols}x{rows}", "-frames:v", "1", f"{outdir}/shot{k + 1:02d}.jpg"])
    print(len(S) - 1, "sheet ->", outdir)


def grid(src, t0, dur, fps, cols, w, out):
    """lưới khung: từ t0 dài dur ở `fps` khung/giây, `cols` cột, mỗi ô rộng w (để chọn hộp đo bằng mắt)."""
    n = max(int(round(dur * fps)), 1); rows = math.ceil(n / cols); os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", src, "-vf", f"fps={fps},scale={w}:-1,tile={cols}x{rows}", "-frames:v", "1", out]); print(out, f"{n} ô, ô đầu = {t0:.3f}s, bước {1 / fps:.3f}s")


# ---------------------------------------------------------------- palette
def _hsv_sat(px):
    mx = px.max(-1).astype(float); mn = px.min(-1).astype(float); return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)


def palette_of(px, k=8, merge=24, mask=None):
    """px (N,3) uint8 -> [(hex, share)] ; lượng tử hoá 16 mức/kênh rồi gộp tham lam các ô cách nhau < merge (RGB Euclid). share = tỉ lệ điểm ảnh (tổng các điểm đã chọn mask)."""
    px = px.reshape(-1, 3)
    if mask is not None: px = px[mask.reshape(-1)]
    n = len(px)
    if n == 0: return []
    key = (px[:, 0].astype(int) >> 4) * 256 + (px[:, 1].astype(int) >> 4) * 16 + (px[:, 2].astype(int) >> 4)
    cnt = np.bincount(key, minlength=4096); sums = np.zeros((4096, 3))
    for c in range(3): sums[:, c] = np.bincount(key, weights=px[:, c].astype(float), minlength=4096)
    order = [i for i in np.argsort(-cnt) if cnt[i] > 0]; out = []; used = np.zeros(4096, bool)
    mean = np.where(cnt[:, None] > 0, sums / np.maximum(cnt, 1)[:, None], 0)
    for i in order:
        if used[i]: continue
        near = [j for j in order if not used[j] and np.linalg.norm(mean[i] - mean[j]) < merge]
        for j in near: used[j] = True
        c = sum(cnt[j] for j in near); m = sum(sums[j] for j in near) / c
        out.append((hexc(m), c / n))
        if len(out) >= k: break
    return out


def sample_frames(src, t0, t1, fps=2, w=360, h=640):
    return read_frames(src, t0, max(t1 - t0, 1.0 / fps), w, h)[:: max(int(FPS / fps), 1)]


def palette(src, t0, t1, k=8, sat=None):
    F = sample_frames(src, t0, t1); px = F.reshape(-1, 3)
    mask = None if sat is None else (_hsv_sat(px) > sat)
    return palette_of(px, k, mask=mask)


def types_palette(src, types, k):
    """types: {tên: [[t0,t1],...]} -> palette tổng + palette điểm ảnh bão hoà (nhấn) + palette tối (chữ) cho từng loại cảnh."""
    res = {}
    for name, rngs in types.items():
        Fs = np.concatenate([sample_frames(src, a, b) for a, b in rngs]); px = Fs.reshape(-1, 3); lum = px.astype(float) @ [.299, .587, .114]
        sat = _hsv_sat(px) > 0.35; dark = lum < 90
        res[name] = {"seconds": round(sum(b - a for a, b in rngs), 2), "all": [[h, round(s, 4)] for h, s in palette_of(px, k)],
                     "accent_share": round(float(sat.mean()), 4), "accent": [[h, round(s, 4)] for h, s in palette_of(px, 5, mask=sat)],
                     "ink_share": round(float(dark.mean()), 4), "ink": [[h, round(s, 4)] for h, s in palette_of(px, 3, mask=dark)]}
    return res


def sample(src, t, x, y, r=3):
    f = frame_at(src, t); c = f[max(y - r, 0):y + r + 1, max(x - r, 0):x + r + 1].reshape(-1, 3); return hexc(np.median(c, 0))


# ---------------------------------------------------------------- masks / series / ease
def make_mask(img, o):
    """img (h,w,3) uint8 -> bool. o: rgb='R,G,B,tol' | dark=L | light=L (mọi kênh >= L) | sat=S (0-255) | bluish=1."""
    f = img.astype(int)
    if "rgb" in o:
        r, g, b, tol = [int(v) for v in o["rgb"].split(",")]; return (abs(f[..., 0] - r) <= tol) & (abs(f[..., 1] - g) <= tol) & (abs(f[..., 2] - b) <= tol)
    if "dark" in o: return (f @ [.299, .587, .114]) < float(o["dark"])
    if "light" in o: return f.min(-1) >= float(o["light"])
    if "sat" in o: return (f.max(-1) - f.min(-1)) >= float(o["sat"])
    sys.exit("cần --rgb | --dark | --light | --sat")


def bbox(m, minrow=3):
    """bbox bền với nhiễu: hàng/cột phải có >= minrow điểm."""
    rows = np.nonzero(m.sum(1) >= minrow)[0]; cols = np.nonzero(m.sum(0) >= minrow)[0]
    if not len(rows) or not len(cols): return None
    return int(cols[0]), int(rows[0]), int(cols[-1]), int(rows[-1])


def crop_box(a, box):
    x0, y0, x1, y1 = [int(v) for v in box]; return a[:, y0:y1, x0:x1], x0, y0


def series(src, t0, t1, box, o):
    """chuỗi từng khung 30fps của mặt nạ trong hộp: [(t, area, x0,y0,x1,y1) toạ độ khung gốc] (None nếu không có)."""
    F = read_frames(src, t0, t1 - t0); C, ox, oy = crop_box(F, box); rows = []
    for i in range(len(C)):
        m = make_mask(C[i], o); b = bbox(m, int(o.get("minrow", 3)))
        rows.append((t0 + i / FPS, int(m.sum()), None if b is None else (b[0] + ox, b[1] + oy, b[2] + ox, b[3] + oy)))
    return rows


def quantity(row, axis):
    t, area, b = row
    if axis == "area": return float(area)
    if b is None: return None
    x0, y0, x1, y1 = b
    return {"x": x0, "x1": x1, "y": y0, "y1": y1, "w": x1 - x0, "h": y1 - y0, "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2}[axis]


# bộ ease ứng viên (u: 0..1 -> 0..1)
def _back(s):
    return lambda u: 1 + (s + 1) * (u - 1) ** 3 + s * (u - 1) ** 2
EASES = {"none": lambda u: u}
for _n in (1, 2, 3, 4):
    _p = _n + 1
    EASES[f"power{_n}.out"] = (lambda p: lambda u: 1 - (1 - u) ** p)(_p)
    EASES[f"power{_n}.in"] = (lambda p: lambda u: u ** p)(_p)
    EASES[f"power{_n}.inOut"] = (lambda p: lambda u: 0.5 * (2 * u) ** p if u < .5 else 1 - 0.5 * (2 * (1 - u)) ** p)(_p)
EASES["sine.out"] = lambda u: math.sin(u * math.pi / 2)
EASES["sine.inOut"] = lambda u: -(math.cos(math.pi * u) - 1) / 2
EASES["expo.out"] = lambda u: 1 if u >= 1 else 1 - 2 ** (-10 * u)
EASES["circ.out"] = lambda u: math.sqrt(1 - (u - 1) ** 2)
def _elastic(per):
    s0 = per / (2 * math.pi) * (math.pi / 2)
    return lambda u: 0 if u <= 0 else (1 if u >= 1 else 2 ** (-10 * u) * math.sin((u - s0) * 2 * math.pi / per) + 1)
EASES["elastic.out(1,0.3)"] = _elastic(0.3); EASES["elastic.out(1,0.5)"] = _elastic(0.5)
for _s in (1.0, 1.4, 1.7, 2.5, 3.5):
    EASES[f"back.out({_s})"] = _back(_s)


def _bez(x1, y1, x2, y2):
    def f(u):
        lo, hi = 0.0, 1.0
        for _ in range(30):
            m = (lo + hi) / 2; x = 3 * (1 - m) ** 2 * m * x1 + 3 * (1 - m) * m * m * x2 + m ** 3
            if x < u: lo = m
            else: hi = m
        m = (lo + hi) / 2; return 3 * (1 - m) ** 2 * m * y1 + 3 * (1 - m) * m * m * y2 + m ** 3
    return f


def fit_ease(ts, ps):
    """ts: thời gian chuẩn hoá 0..1, ps: tiến độ 0..1 (có thể vượt). Trả (tên ease gần nhất, rmse, bezier tốt nhất (x1,y1,x2,y2), rmse bezier)."""
    ts = np.array(ts); ps = np.array(ps); best = ("none", 9e9)
    for n, f in EASES.items():
        e = float(np.sqrt(np.mean([(f(min(max(u, 0), 1)) - p) ** 2 for u, p in zip(ts, ps)])))
        if e < best[1]: best = (n, e)
    bb = (None, 9e9)
    for x1 in np.arange(0, 1.01, 0.1):
        for x2 in np.arange(0, 1.01, 0.1):
            for y1 in np.arange(-0.4, 1.41, 0.2):
                for y2 in np.arange(0.2, 1.61, 0.2):
                    f = _bez(x1, y1, x2, y2); e = float(np.sqrt(np.mean([(f(min(max(u, 0), 1)) - p) ** 2 for u, p in zip(ts, ps)])))
                    if e < bb[1]: bb = ((round(float(x1), 2), round(float(y1), 2), round(float(x2), 2), round(float(y2), 2)), e)
    return best[0], best[1], bb[0], bb[1]


def ease_report(rows, axis, eps=0.03, label=""):
    """chuẩn hoá đại lượng về 0..1 giữa giá trị đầu (ổn định) và cuối (ổn định); tìm khung bắt đầu, khung chạm 0.98 (reach), khung lắng hẳn trong ±2% (settle),
    quá đà (đỉnh p - 1), rồi khớp ease trên đoạn bắt đầu->lắng (hoặc ->reach nếu không quá đà)."""
    ts = np.array([r[0] for r in rows]); q = [quantity(r, axis) for r in rows]
    ok = [i for i, v in enumerate(q) if v is not None]
    if len(ok) < 4: print("quá ít khung có mặt nạ"); return None
    v = np.array([q[i] if q[i] is not None else np.nan for i in range(len(q))]); idx = np.array(ok)
    v0 = v[idx[0]]; v1 = v[idx[-1]]; span = v1 - v0
    if abs(span) < 1e-6: print("không đổi"); return None
    p = (v - v0) / span
    start = max(next(i for i in idx if abs(p[i]) > eps) - 1, idx[0])
    reach = next((i for i in idx if i >= start and p[i] >= 0.98), idx[-1])
    settle = next((i for i in reversed(idx) if abs(1 - p[i]) > 0.02), idx[-1]) + 1; settle = min(settle, idx[-1])
    over = float(np.nanmax(p[start:])) - 1.0
    stop = settle if over > 0.03 else max(reach, start + 3); stop = min(stop, idx[-1])
    seg = [i for i in idx if start <= i <= stop]; den = max(ts[stop] - ts[start], 1e-6)
    name, e, bz, eb = fit_ease([(ts[i] - ts[start]) / den for i in seg], [p[i] for i in seg])
    res = {"label": label, "axis": axis, "from": round(float(v0), 1), "to": round(float(v1), 1), "distance": round(float(span), 1),
           "t_start": round(float(ts[start]), 3), "reach_s": round(float(ts[reach] - ts[start]), 3), "settle_s": round(float(ts[settle] - ts[start]), 3), "frames_to_settle": int(round((ts[settle] - ts[start]) * FPS)),
           "overshoot": round(over, 3), "ease": name, "rmse": round(e, 3), "bezier": bz, "bezier_rmse": round(eb, 3)}
    print(json.dumps(res, ensure_ascii=False))
    print("p(t): " + " ".join(f"{p[i]:.2f}" for i in range(start, min(settle + 2, len(p))) if not np.isnan(p[i])))
    return res


def print_series(rows):
    for t, a, b in rows:
        print(f"t={t:.3f} area={a}" + ("" if b is None else f" x {b[0]}-{b[2]} y {b[1]}-{b[3]} w {b[2] - b[0]} h {b[3] - b[1]} c ({(b[0] + b[2]) / 2:.0f},{(b[1] + b[3]) / 2:.0f})"))


def spread(src, t0, t1, box, cx, cy, o):
    """phân bố bán kính (điểm ảnh của mặt nạ so với tâm cx,cy): trung vị và p90 từng khung -> node toả tròn."""
    F = read_frames(src, t0, t1 - t0); C, ox, oy = crop_box(F, box); rows = []
    for i in range(len(C)):
        m = make_mask(C[i], o); ys, xs = np.nonzero(m)
        if len(xs) < 20: rows.append((t0 + i / FPS, len(xs), None)); continue
        r = np.hypot(xs + ox - cx, ys + oy - cy); rows.append((t0 + i / FPS, int(len(xs)), (float(np.median(r)), float(np.percentile(r, 90)))))
    return rows


def changes(src, t0, t1, box, thr):
    """các khung có thay đổi trong hộp (|Δ| TB > thr): dùng cho đếm số nhảy (count-up), chữ gõ."""
    F = read_frames(src, t0, t1 - t0, pix="gray"); C, ox, oy = crop_box(F[..., 0] if F.ndim == 4 else F, box)
    ev = []
    for i in range(1, len(C)):
        d = float(np.abs(C[i].astype(int) - C[i - 1].astype(int)).mean())
        if d > thr: ev.append((t0 + i / FPS, d))
    return ev


def inkwidth(src, t0, t1, box, o):
    """chữ gõ: mép phải của mực (mặt nạ) trong hộp từng khung, mép trái cố định -> độ rộng chữ."""
    rows = series(src, t0, t1, box, o); return rows


def energyprofile(epath, win):
    E, D = load_energy(epath); n = int(round(win * FPS)); out = []
    for i in range(0, len(E) - n + 1, n): out.append(float(E[i:i + n].mean()))
    out = np.array(out)
    res = ({"window_s": win, "mean": round(float(E.mean()), 3), "median": round(float(np.median(E)), 3), "p25": round(float(np.percentile(E, 25)), 3), "p75": round(float(np.percentile(E, 75)), 3), "p95": round(float(np.percentile(E, 95)), 3),
                      "window_mean_p10": round(float(np.percentile(out, 10)), 3), "window_mean_p50": round(float(np.percentile(out, 50)), 3), "window_mean_p90": round(float(np.percentile(out, 90)), 3),
                      "frac_frames_still(E<0.1)": round(float((E < 0.1).mean()), 3), "frac_windows_E>2": round(float((out > 2).mean()), 3)})
    print(json.dumps(res)); return res


def rhythm(cutsp, epath, types_p=None):
    S, T = load_cuts(cutsp); L = np.diff(S); E, D = load_energy(epath)
    res = {"shots": len(L), "len_mean": round(float(L.mean()), 2), "len_median": round(float(np.median(L)), 2), "len_p10": round(float(np.percentile(L, 10)), 2), "len_p90": round(float(np.percentile(L, 90)), 2), "len_min": round(float(L.min()), 2), "len_max": round(float(L.max()), 2),
           "cuts_per_min": round(60 * (len(L) - 1) / T, 1)}
    print(json.dumps(res)); print("độ dài cảnh:", " ".join(f"{x:.1f}" for x in L))
    # histogram độ dài cảnh theo ô 2s
    h = np.histogram(L, bins=[0, 2, 4, 6, 8, 10, 12, 20])[0]; print("hist [0-2,2-4,4-6,6-8,8-10,10-12,12+]:", h.tolist())
    # năng lượng trung bình trong mỗi cảnh
    eh = []
    for k in range(len(L)):
        i0, i1 = int(S[k] * FPS), min(int(S[k + 1] * FPS), len(E)); seg = E[i0:max(i1 - 12, i0 + 1)]
        mv = np.nonzero(seg > 1.0)[0]; last = (mv.max() + 1) if len(mv) else 0; hold = (len(seg) - last) / FPS   # từ khung chuyển động cuối (E>1) tới 0.4s trước cắt: thời gian khung đứng yên cuối cảnh
        eh.append(hold); print(f"shot{k + 1:02d} {S[k]:.2f}-{S[k + 1]:.2f} len {L[k]:.2f} E_mean {E[i0:i1].mean():.2f} E_p90 {np.percentile(E[i0:i1], 90):.2f} end_hold {hold:.2f}s")
    eh = np.array(eh); res["end_hold_median_s"] = round(float(np.median(eh)), 2); res["end_hold_p90_s"] = round(float(np.percentile(eh, 90)), 2); res["end_hold_zero_share"] = round(float((eh < 0.1).mean()), 2)
    print(json.dumps({k: v for k, v in res.items() if k.startswith("end_hold")}))
    return res


def transitions(src, cutsp, epath):
    """đo từng điểm cắt rồi phân loại bằng luật đo được (xem số liệu từng dòng):
    flash-wipe: có khung phủ xanh (B-R>70, B>170) >= 60% diện tích · bar-wipe: có khung với hàng ngang (hoặc cột dọc) phủ xanh >= 60% bề rộng, tăng so với hai đầu cửa sổ
    hard: khung đỉnh chiếm >= 35% tổng E (E>2) của cửa sổ ±0.4s và D đỉnh >= 0.10 · wash: D đỉnh < 0.08 (đổi nền toàn cục, không có nét đổi hình) · dissolve: còn lại (>= 4 khung chuyển mềm)"""
    S, T = load_cuts(cutsp); E, D = load_energy(epath); rows = []
    for k in range(1, len(S) - 1):
        c = int(round(S[k] * FPS)) - 1; i0 = max(c - 12, 0); i1 = min(c + 13, len(E))
        seg = E[i0:i1]; hi = np.nonzero(seg > 2)[0]; n_hi = len(hi)
        F = read_frames(src, max(S[k] - 0.4, 0), 0.8, 144, 256).astype(int)
        blue = ((F[..., 2] - F[..., 0] > 70) & (F[..., 2] > 170))
        frac = blue.mean((1, 2)); rowcov = (blue.mean(2) > 0.6).mean(1); colcov = (blue.mean(1) > 0.6).mean(1)
        bar = max(float(rowcov.max() - max(rowcov[0], rowcov[-1])), float(colcov.max() - max(colcov[0], colcov[-1])))
        lum = F.mean((1, 2, 3)); dl = float(abs(lum[-1] - lum[0])); pkD = float(D[i0:i1].max()); pkE = float(seg.max())
        share = float(pkE / max(seg[seg > 2].sum(), 1e-6))
        if frac.max() >= 0.6: kind = "flash-wipe"
        elif bar >= 0.03: kind = "bar-wipe"
        elif share >= 0.35 and pkD >= 0.10: kind = "hard"
        elif pkD < 0.08: kind = "wash"
        else: kind = "dissolve"
        rows.append({"cut": k, "t": S[k], "frames_E>2": int(n_hi), "pkE": round(pkE, 1), "pkD": round(pkD, 2), "share": round(share, 2), "blue_max": round(float(frac.max()), 3), "bar_cover": round(bar, 3), "dLum": round(dl, 1), "kind": kind})
    for r in rows: print(json.dumps(r))
    cnt = {}
    for r in rows: cnt[r["kind"]] = cnt.get(r["kind"], 0) + 1
    print("đếm:", json.dumps(cnt)); return rows


# ---------------------------------------------------------------- typography
def ink_mask(img, thr=70):
    """điểm ảnh khác màu nền (trung vị của hộp) quá thr (khoảng cách kênh lớn nhất)."""
    f = img.astype(int); bg = np.median(f.reshape(-1, 3), 0); return np.abs(f - bg).max(-1) > thr


def runs(v):
    """các đoạn liên tiếp True của mảng bool 1-D -> [(bắt đầu, dài)]."""
    out = []; i = 0; n = len(v)
    while i < n:
        if v[i]:
            j = i
            while j < n and v[j]: j += 1
            out.append((i, j - i)); i = j
        else: i += 1
    return out


def textrows(src, t, box, thr=70, H=None):
    """chữ trong hộp -> từng dòng: hộp mực, x-height (dải hàng có mật độ >= 50% đỉnh), nét dày (trung vị đoạn mực ngang ở giữa x-height), khoảng cách chữ (khe giữa glyph trong dải x-height), bước dòng."""
    f = frame_at(src, t); p = probe(src); H = H or p["height"]; x0, y0, x1, y1 = [int(v) for v in box]
    m = ink_mask(f[y0:y1, x0:x1], thr); rs = m.sum(1); lines = runs(rs > 0); out = []
    for a, h in lines:
        if h < 4: continue
        sub = m[a:a + h]; prof = sub.sum(1); pk = prof.max(); band = np.nonzero(prof >= 0.5 * pk)[0]
        xt, xb = int(band.min()), int(band.max()); xh = xb - xt + 1
        cols = np.nonzero(sub.sum(0) > 0)[0]; mid = sub[(xt + xb) // 2]; rl = [l for _, l in runs(mid)]
        band_m = sub[xt:xb + 1]; colink = band_m.sum(0) > 0; gaps = [l for st, l in runs(~colink) if cols[0] < st < cols[-1]]
        out.append({"y0": int(a + y0), "y1": int(a + h - 1 + y0), "ink_h": int(h), "xt": int(xt + a + y0), "baseline": int(xb + a + y0), "xheight": xh,
                    "x0": int(cols[0] + x0), "x1": int(cols[-1] + x0), "width": int(cols[-1] - cols[0] + 1),
                    "stem_px": float(np.median(rl)) if rl else None, "gap_px": float(np.median(gaps)) if gaps else None, "n_gaps": len(gaps),
                    "xheight_frac_H": round(xh / H, 4), "ink_h_frac_H": round(h / H, 4)})
    for i in range(1, len(out)): out[i]["pitch_px"] = out[i]["baseline"] - out[i - 1]["baseline"]
    return out


# ---------------------------------------------------------------- layout: scan / corner / shadow
def scan(src, t, axis, idx, a, b, thr=40):
    """đường quét ngang (axis=x: hàng y=idx, cột a..b) hoặc dọc (axis=y: cột x=idx, hàng a..b): các đoạn khác màu nền (nền = trung vị đường) -> (vị trí đầu, dài, màu TB)."""
    f = frame_at(src, t); line = f[idx, a:b] if axis == "x" else f[a:b, idx]
    bg = np.median(line.astype(int), 0); m = np.abs(line.astype(int) - bg).max(-1) > thr; out = []
    for st, ln in runs(m): out.append((st + a, ln, hexc(line[st:st + ln].mean(0))))
    return out


def corner(src, t, box, corner_name, o):
    """bán kính góc của hình (mặt nạ trong hộp, góc tl|tr|bl|br của bbox mặt nạ): hàng/cột đầu tiên mà mép thẳng; bán kính = khoảng cách trung bình."""
    f = frame_at(src, t); x0, y0, x1, y1 = [int(v) for v in box]; m = make_mask(f[y0:y1, x0:x1], o)
    b = bbox(m, 3)
    if not b: return None
    bx0, by0, bx1, by1 = b
    if "r" in corner_name: m = m[:, ::-1]; bx0, bx1 = m.shape[1] - 1 - bx1, m.shape[1] - 1 - bx0
    if corner_name.startswith("b"): m = m[::-1]; by0, by1 = m.shape[0] - 1 - by1, m.shape[0] - 1 - by0
    rows = [np.nonzero(m[y])[0] for y in range(by0, min(by0 + 400, m.shape[0]))]
    ry = next((i for i, r in enumerate(rows) if len(r) and r.min() <= bx0 + 1), None)
    cols = [np.nonzero(m[:, x])[0] for x in range(bx0, min(bx0 + 400, m.shape[1]))]
    rx = next((i for i, c in enumerate(cols) if len(c) and c.min() <= by0 + 1), None)
    ys, xs = np.nonzero(m[by0:by0 + 400, bx0:bx0 + 400]); d = float(np.hypot(xs, ys).min()) if len(xs) else 0.0   # khoảng cách từ góc bbox tới điểm mặt nạ gần nhất = r(sqrt2-1)
    return {"bbox": [bx0 + x0, by0 + y0, bx1 + x0, by1 + y0], "r_from_rows": ry, "r_from_cols": rx, "r_diag": round(d / 0.4142, 1)}


def shadow(src, t, axis, idx, a, length, step=2):
    """bóng đổ: độ sáng TB (dải 12 px) theo khoảng cách từ mép (a) theo hướng +: axis=y quét xuống tại cột idx, axis=x quét sang phải tại hàng idx. In dL so với nền xa."""
    f = frame_at(src, t).astype(float); lum = f @ [.299, .587, .114]
    prof = []
    for d in range(0, length, step):
        if axis == "y": prof.append(lum[a + d, idx - 6:idx + 6].mean())
        else: prof.append(lum[idx - 6:idx + 6, a + d].mean())
    prof = np.array(prof); far = prof[-3:].mean(); dl = far - prof
    ext = next((i for i in range(len(dl) - 1, -1, -1) if dl[i] > 1.5), 0) * step
    return {"far_lum": round(float(far), 1), "max_darken": round(float(dl.max()), 1), "at_px": int(np.argmax(dl) * step), "extent_px_dL>1.5": int(ext), "profile": [round(float(x), 1) for x in dl[:: max(len(dl) // 12, 1)]]}


def typed(rows, min_step=8):
    """chữ gõ từ vị trí con trỏ (tâm x của mặt nạ con trỏ) theo khung: các bước nhảy -> số ký tự = tổng Δx / bề rộng ký tự (trung vị nửa dưới các bước dương, coi là 1 ký tự)."""
    xs = [(t, quantity((t, a, b), "cx")) for t, a, b in rows if b is not None and b[2] - b[0] <= 8]   # chỉ khung có con trỏ gọn (bỏ khung dính màu khác)
    xs = [(t, x) for t, x in xs if x is not None]
    steps = [(xs[i][0], xs[i][1] - xs[i - 1][1]) for i in range(1, len(xs)) if xs[i][1] - xs[i - 1][1] >= min_step]
    if not steps: print("không có bước"); return None
    d = sorted(v for _, v in steps); unit = float(np.median(d[:max(len(d) // 2, 1)]))
    total = xs[-1][1] - xs[0][1]; dur = xs[-1][0] - xs[0][0]; n = total / unit
    res = {"t_first": round(xs[0][0], 3), "t_last": round(xs[-1][0], 3), "dx_px": round(float(total), 1), "char_adv_px": round(unit, 1), "chars_est": round(float(n), 1), "steps": len(steps),
           "chars_per_s": round(float(n / dur), 1), "steps_per_s": round(len(steps) / dur, 1), "frames_per_char": round(dur * FPS / n, 2), "step_sizes_chars": [round(v / unit, 1) for _, v in steps]}
    print(json.dumps(res)); return res


def vscroll(src, t0, t1, rng=520, axis="y"):
    """camera tịnh tiến: dịch toàn cục giữa hai khung liền nhau (cực tiểu |Δ| của hồ sơ độ sáng trung bình theo hàng (axis=y) hoặc cột (axis=x), thử dịch -rng..rng; dương = nội dung đi xuống/sang phải).
    Trả [(t, dịch tích luỹ)] -> dùng với ease_report."""
    F = read_frames(src, t0, t1 - t0, 180, 320, "gray")[..., 0].astype(float); sc = 1280 / 320.0
    prof = F.mean(2 if axis == "y" else 1) if False else (F.mean(2) if axis == "y" else F.mean(1)); n = prof.shape[1]; R = int(rng / sc)
    rows = [(t0, 0, (0, 0, 0, 0))]; cum = 0.0; per = []
    for i in range(1, len(prof)):
        best, bs = 9e9, 0
        for sft in range(-R, R + 1):
            a = prof[i - 1, max(0, -sft):n - max(0, sft)]; b = prof[i, max(0, sft):n - max(0, -sft)]
            if len(a) < n // 2: continue
            e = float(np.abs(a - b).mean())
            if e < best: best, bs = e, sft
        cum += bs * sc; per.append(bs * sc); rows.append((t0 + i / FPS, 0, (cum, cum, cum, cum)))
    return rows, per


def holds(arr, thr, minlen):
    """các đoạn liên tiếp arr < thr dài >= minlen khung -> [(khung đầu, số khung)]."""
    return [(a, l) for a, l in runs(np.asarray(arr) < thr) if l >= minlen]


def dwell(src, t0, t1, box, thr=0.5, minlen=9):
    """chữ/đối tượng trong hộp đứng yên bao lâu: |Δ| TB giữa hai khung liền nhau trong hộp < thr, đoạn >= minlen khung (0.3s)."""
    F = read_frames(src, t0, t1 - t0, pix="gray"); C, ox, oy = crop_box(F[..., 0], box)
    d = [float(np.abs(C[i].astype(int) - C[i - 1].astype(int)).mean()) for i in range(1, len(C))]
    hs = holds(d, thr, minlen); res = [{"t": round(t0 + (a + 1) / FPS, 3), "dur_s": round(l / FPS, 2)} for a, l in hs]
    print(json.dumps(res)); return res


def global_holds(epath, thr, minlen_s):
    E, D = load_energy(epath); hs = holds(E, thr, int(minlen_s * FPS)); L = np.array([l / FPS for a, l in hs])
    res = {"thr_E": thr, "min_s": minlen_s, "n": len(hs), "total_s": round(float(L.sum()), 1), "share_of_clip": round(float(L.sum() / (len(E) / FPS)), 3), "median_s": round(float(np.median(L)), 2), "p90_s": round(float(np.percentile(L, 90)), 2), "max_s": round(float(L.max()), 2)}
    print(json.dumps(res)); return res


def motion_bursts(epath, thr=1.0, gap=6, minlen=3):
    """đợt chuyển động: các cụm khung E > thr (gộp khoảng hở <= gap khung) -> số đợt, độ dài, đỉnh."""
    E, D = load_energy(epath); cl = clusters(E, thr, gap); cl = [c for c in cl if len(c) >= minlen]; L = np.array([(c[-1] - c[0] + 1) / FPS for c in cl])
    res = {"thr_E": thr, "bursts": len(cl), "per_min": round(len(cl) / (len(E) / FPS / 60), 1), "len_median_s": round(float(np.median(L)), 2), "len_p90_s": round(float(np.percentile(L, 90)), 2), "peak_E_median": round(float(np.median([E[c].max() for c in cl])), 1)}
    print(json.dumps(res)); return res


def inkmap(src, fps=1, w=144, h=256):
    """vùng an toàn / lề: mặt nạ mực (tối < 140 hoặc bão hoà >= 80) từng khung -> phân bố theo dải dọc/ngang (20 dải) và phân vị hộp bao nội dung (phân số W,H)."""
    F = read_frames(src, 0, 1e4, w, h)[:: int(FPS / fps)].astype(int)
    lum = F @ [.299, .587, .114]; ink = (lum < 140) | ((F.max(-1) - F.min(-1)) >= 80)
    vy = ink.mean((0, 2)); hx = ink.mean((0, 1)); vb = [float(vy[i * h // 20:(i + 1) * h // 20].sum()) for i in range(20)]; hb = [float(hx[i * w // 20:(i + 1) * w // 20].sum()) for i in range(20)]
    sv = sum(vb); sh = sum(hb); bb = []
    for m in ink:
        r = np.nonzero(m.mean(1) > 0.01)[0]; c = np.nonzero(m.mean(0) > 0.01)[0]
        if len(r) and len(c): bb.append((c[0] / w, c[-1] / w, r[0] / h, r[-1] / h))
    bb = np.array(bb); pc = lambda i, q: round(float(np.percentile(bb[:, i], q)), 3)
    res = {"frames": int(len(ink)), "ink_share_by_vertical_20th": [round(v / sv, 3) for v in vb], "ink_share_by_horizontal_20th": [round(v / sh, 3) for v in hb],
           "bbox_left_p10_p50": [pc(0, 10), pc(0, 50)], "bbox_right_p50_p90": [pc(1, 50), pc(1, 90)], "bbox_top_p10_p50": [pc(2, 10), pc(2, 50)], "bbox_bottom_p50_p90": [pc(3, 50), pc(3, 90)],
           "ink_share_below_80pct_H": round(float(sum(vb[16:]) / sv), 3), "ink_share_above_10pct_H": round(float(sum(vb[:2]) / sv), 3)}
    print(json.dumps(res)); return res


# ---------------------------------------------------------------- bề mặt, nền trang, thẻ, lưới, khối iso
def page_background(src, T, fps=2, w=144, h=256):
    """nền trang có HAI chế độ: trắng và nền xanh nhạt (tint). Dải mép (trái/phải 4% bề rộng, trên 3%, dưới 5% chiều cao):
    khung là 'trắng' khi > 70% điểm ảnh mép là trắng bề mặt (mọi kênh >= 253), ngược lại là 'tint'. Trả: tỉ lệ khung mỗi chế độ (cả theo 10 phần thời gian),
    màu trắng (trung vị), màu tint (trung vị điểm ảnh mép KHÔNG trắng, lum > 190), dải độ sáng tint theo khung, điểm dừng dọc/ngang và chênh tâm-mép của tint."""
    F = sample_frames(src, 0, T, fps, w, h).astype(int); n = len(F)
    lum = F @ [.299, .587, .114]; white = F.min(-1) >= 253; page = (~white) & (lum > 190)
    edge = np.zeros((h, w), bool); edge[:, :int(w * .04) + 1] = True; edge[:, -int(w * .04) - 1:] = True; edge[:int(h * .03) + 1] = True; edge[-int(h * .05):] = True
    def med(m):
        px = F[m]; return None if len(px) < 30 else hexc(np.median(px, 0))
    ew = (white & edge[None]).sum((1, 2)) / edge.sum(); is_white = ew > 0.7
    dec = [round(float(is_white[int(n * i / 10):max(int(n * (i + 1) / 10), int(n * i / 10) + 1)].mean()), 3) for i in range(10)]
    allm = page & edge[None]; bg = med(allm); wc = med(white & edge[None] & is_white[:, None, None])
    per = [np.median(F[i][allm[i]], 0) for i in range(n) if allm[i].sum() > 30 and not is_white[i]]; pl = np.array([c @ [.299, .587, .114] for c in per])
    lo_i = int(np.argsort(pl)[int(len(pl) * .1)]); hi_i = int(np.argsort(pl)[int(len(pl) * .9)])
    tm = ~is_white   # các thống kê gradient chỉ lấy khung tint
    vstops = []
    for y0, y1 in ((0, 5), (25, 30), (50, 55), (75, 80), (95, 100)):
        m = np.zeros((h, w), bool); m[int(h * y0 / 100):int(h * y1 / 100) or 1, :int(w * .04) + 1] = True; m[int(h * y0 / 100):int(h * y1 / 100) or 1, -int(w * .04) - 1:] = True
        vstops.append([y0 / 100 + 0.025, med(page & m[None] & tm[:, None, None])])
    hstops = []
    for x0, x1 in ((0, 4), (48, 52), (96, 100)):
        m = np.zeros((h, w), bool); m[int(h * .95):, int(w * x0 / 100):max(int(w * x1 / 100), int(w * x0 / 100) + 1)] = True
        hstops.append([x0 / 100 + 0.02, med(page & m[None] & tm[:, None, None])])
    cm = np.zeros((h, w), bool); cm[int(h * .45):int(h * .55), int(w * .4):int(w * .6)] = True; centre = med(page & cm[None] & tm[:, None, None])
    L = lambda hx: None if hx is None else _lum(hx)
    vl = [L(v[1]) for v in vstops if v[1]]; hl = [L(v[1]) for v in hstops if v[1]]
    return {"bg": bg, "white": {"colour": wc, "frame_share": round(float(is_white.mean()), 3), "edge_pixel_share": round(float(ew.mean()), 3), "frame_share_by_decile": dec},
            "tint_frame_share": round(float(1 - is_white.mean()), 3), "tint_p10_p50_p90": [hexc(per[lo_i]), hexc(np.median(per, 0)), hexc(per[hi_i])], "tint_lum_p10_p90": [round(float(pl[lo_i]), 1), round(float(pl[hi_i]), 1)],
            "vertical_stops": vstops, "horizontal_stops_bottom_row": hstops, "centre": centre, "vertical_lum_delta_top_minus_bottom": round(vl[0] - vl[-1], 1) if len(vl) > 1 else None,
            "horizontal_lum_delta_left_minus_right": round(hl[0] - hl[-1], 1) if len(hl) > 1 else None, "centre_minus_edge_lum": None if not centre or not bg else round(L(centre) - L(bg), 1)}


def surface_color(src, T, fps=2, w=144, h=256):
    """bề mặt thẻ: điểm ảnh gần trắng (mọi kênh >= 250): trung vị màu và tỉ lệ điểm ảnh cả clip."""
    F = sample_frames(src, 0, T, fps, w, h).astype(int); m = F.min(-1) >= 250
    return {"color": hexc(np.median(F[m], 0)), "pixel_share": round(float(m.mean()), 3)}


def cardspec(src, t, box, thr=253, ink_thr=60):
    """thẻ/pill: hộp bao phần bề mặt trắng (mọi kênh >= thr) trong hộp tìm, rồi padding = khoảng từ mép thẻ tới hộp bao mực bên trong (tối < 150 hoặc bão hoà >= 70), tính theo phân số W/H; bóng 2 phía."""
    f = frame_at(src, t); H_, W_ = f.shape[:2]; x0, y0, x1, y1 = [int(v) for v in box]; sub = f[y0:y1, x0:x1].astype(int)
    m = sub.min(-1) >= thr; b = bbox(m, 12)
    if not b: return None
    bx0, by0, bx1, by1 = b; X0, Y0, X1, Y1 = bx0 + x0, by0 + y0, bx1 + x0, by1 + y0
    inner = f[Y0 + 5:Y1 - 4, X0 + 5:X1 - 4].astype(int); lum = inner @ [.299, .587, .114]; ink = (lum < 150) | ((inner.max(-1) - inner.min(-1)) >= 70)
    ib = bbox(ink, 2); pad = None
    if ib: pad = {"left": round((ib[0] + 5) / W_, 4), "right": round((X1 - X0 - 9 - ib[2] + 4) / W_, 4), "top": round((ib[1] + 5) / H_, 4), "bottom": round((Y1 - Y0 - 9 - ib[3] + 4) / H_, 4)}
    lm = f.astype(float) @ [.299, .587, .114]; cx = (X0 + X1) // 2; cy = (Y0 + Y1) // 2
    def side(vec, d0):   # vec: độ sáng dọc theo hướng ra ngoài tính từ mép
        far = float(np.mean(vec[-4:])); dl = far - np.asarray(vec); ext = next((i for i in range(len(dl) - 1, -1, -1) if dl[i] > 1.5), 0)
        return ext, float(dl[d0:].max()) if len(dl) > d0 else 0.0, int(d0 + np.argmax(dl[d0:]))
    ln = min(70, H_ - Y1 - 1); below = [lm[Y1 + 1 + d, cx - 6:cx + 7].mean() for d in range(ln)]
    up = min(70, Y0 - 1); above = [lm[Y0 - 1 - d, cx - 6:cx + 7].mean() for d in range(up)]
    eb, db, ab = side(below, 4); ea, da, aa = side(above, 4)
    col = f[Y1 + 1 + ab, cx - 6:cx + 7].mean(0); bgc = f[min(Y1 + 1 + ln - 1, H_ - 1), cx - 6:cx + 7].mean(0)
    a0 = np.array([21.0, 101.0, 192.0]); alpha = float(np.clip((bgc @ [.299, .587, .114] - col @ [.299, .587, .114]) / max(bgc @ [.299, .587, .114] - a0 @ [.299, .587, .114], 1), 0, 1))
    return {"bbox": [X0, Y0, X1, Y1], "width_frac_W": round((X1 - X0 + 1) / W_, 3), "height_frac_H": round((Y1 - Y0 + 1) / H_, 3), "center_x_frac_W": round(cx / W_, 3), "padding_frac_W": pad,
            "shadow": {"extent_below_frac_W": round(eb / W_, 4), "extent_above_frac_W": round(ea / W_, 4), "offset_y_frac_W": round((eb - ea) / 2 / W_, 4), "blur_frac_W": round((eb + ea) / 2 / W_, 4), "max_darken_lum": round(db, 1), "alpha_if_accent_dark_tint": round(alpha, 2)}}


def gridpitch(src, t, box):
    """nền lưới/chấm: chu kỳ (px) theo hai phương từ tự tương quan hồ sơ độ sáng trung bình của vùng nền trống, kèm độ tương phản (độ sáng)."""
    f = frame_at(src, t); x0, y0, x1, y1 = [int(v) for v in box]; lum = f[y0:y1, x0:x1].astype(float) @ [.299, .587, .114]; res = {}
    for nm, prof in (("x", lum.mean(0)), ("y", lum.mean(1))):
        p = prof - np.convolve(prof, np.ones(41) / 41, mode="same"); p = p[20:-20]; ac = np.correlate(p, p, "full")[len(p) - 1:]; ac = ac / max(ac[0], 1e-9)
        pk = [i for i in range(8, min(len(ac) - 1, 400)) if ac[i] > ac[i - 1] and ac[i] >= ac[i + 1] and ac[i] > 0.2]
        res[nm] = {"pitch_px": pk[0] if pk else None, "strength": round(float(ac[pk[0]]), 2) if pk else None, "contrast_lum": round(float(p.max() - p.min()), 1)}
    return res


def iso_palette(src, t, box, k=6):
    """khối iso: các cụm màu bão hoà trong hộp (mặt trên/trái/phải) + tỉ lệ -> sắp theo độ sáng."""
    f = frame_at(src, t); x0, y0, x1, y1 = [int(v) for v in box]; px = f[y0:y1, x0:x1].reshape(-1, 3)
    sat = (_hsv_sat(px) > 0.3) & ((px[:, 2].astype(int) - px[:, 0].astype(int)) > 40); cl = palette_of(px, k, mask=sat)   # chỉ cụm xanh (loại vàng/xám)
    return sorted([[h, round(sh, 3)] for h, sh in cl], key=lambda r: -_lum(r[0]))


# ---- measure-clip
# ---------------------------------------------------------------- measure-clip / merge-style: số đo từng clip theo instances.json, rồi gộp các clip thành style.json
import io, contextlib, re


def _quiet(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): r = fn(*a, **k)
    return r


def _lum(h): return float(int(h[1:3], 16) * .299 + int(h[3:5], 16) * .587 + int(h[5:7], 16) * .114)


def _frac(axis, v, W, H):
    if axis == "area": return None   # diện tích: không quy ra phân số một chiều
    return round(abs(v) / (W if axis in ("x", "x1", "w", "cx") else H), 4)


def _ease_inst(src, spec, W, H):
    o = dict(spec["mask"]); rows = series(src, spec["t0"], spec["t1"], spec["box"], o)
    if spec.get("pre"): rows = [(spec["pre"][0], 0, (spec["pre"][1],) * 4)] + rows[1:]
    r = _quiet(ease_report, rows, spec["axis"], label=spec.get("label", ""))
    if r is None: return None
    r["distance_frac"] = _frac(spec["axis"], r["distance"], W, H); r["frac_of"] = "area" if spec["axis"] == "area" else ("W" if spec["axis"] in ("x", "x1", "w", "cx") else "H")
    if spec.get("onset_min"):
        r["onset_t"] = round(next(t for t, a, b in series(src, spec["t0"] - 0.2, spec["t1"], spec["box"], o) if a >= spec["onset_min"]), 3)
    return r


def _hop_inst(src, spec):
    d = series(src, spec["t0"], spec["t1"], spec["box"], spec["mask"])
    cx = [(t, quantity((t, a, b), "cx"), quantity((t, a, b), "w")) for t, a, b in d if b]
    j = next(i for i in range(1, len(cx)) if abs(cx[i][1] - cx[i - 1][1]) > spec.get("min_hop", 20)); wfin = cx[-1][2]
    k = max([i for i in range(j, len(cx)) if cx[i][2] > wfin + 1.2] or [j])
    if min(c[2] for c in cx[j - 1:j + 2]) < 0.6 * wfin or wfin < 4: return None   # chấm quá mảnh/khung nhảy mất mặt nạ: không tin được
    return {"t_jump": round(cx[j][0], 3), "hop_px": round(abs(cx[j][1] - cx[j - 1][1]), 1), "hop_frames": 1, "dot_px": [cx[j][2], wfin], "pop_scale": round(cx[j][2] / wfin, 2), "settle_s": round(cx[min(k + 1, len(cx) - 1)][0] - cx[j][0], 3)}


def _nodes_inst(src, spec):
    hub = series(src, spec["hub_t"], spec["hub_t"] + 0.1, spec["hub_box"], spec["hub_mask"])[0][2]; hx, hy = (hub[0] + hub[2]) / 2, (hub[1] + hub[3]) / 2; nodes = {}
    for nm, box in spec["nodes"].items():
        rows = series(src, spec["t0"], spec["t1"], box, spec["mask"]); on_t = next(t for t, a, b in rows if a >= spec.get("onset_min", 250))
        fin = next(b for t, a, b in rows if t >= spec["t1"] - 0.2 and b); nodes[nm] = {"onset_t": round(on_t, 3), "center": [(fin[0] + fin[2]) // 2, (fin[1] + fin[3]) // 2]}
    ts = sorted(v["onset_t"] for v in nodes.values())
    return {"hub_center": [round(hx), round(hy)], "n": len(nodes), "arrival_span_s": round(ts[-1] - ts[0], 3), "mean_gap_s": round(float(np.mean(np.diff(ts))), 3), "nodes": nodes}


def _vscroll_inst(src, spec, H):
    out = {}
    for name, (a, b) in spec["phases"].items():
        d, per = vscroll(src, a, b); pk = int(max(abs(v) for v in per))
        out[name] = {"travel_frac_H": round(abs(d[-1][2][0]) / H, 3), "peak_px_per_frame": pk, "peak_frac_H_per_frame": round(pk / H, 3), "frames": len(per), "dy_per_frame": [round(v) for v in per[:12]]}
    return out


def measure_clip(cd):
    """đo một clip theo cd/instances.json (hộp/thời điểm tính theo px khung gốc của clip) -> dict số đo thô."""
    src = os.path.join(cd, "source.mp4"); ep = os.path.join(cd, "tmp/energy.json"); cutsp = os.path.join(cd, "cuts_rule.json"); inst = json.load(open(os.path.join(cd, "instances.json")))
    if not os.path.exists(ep): energy(src, ep)
    if not os.path.exists(cutsp): cuts_rule(ep, probe(src)["duration"], cutsp)
    P = probe(src); W, H = int(P["width"]), int(P["height"]); T = float(P["duration"]); out = {"id": inst["id"], "title": inst["title"], "url": inst["url"], "notes": inst.get("notes", {}), "content_motifs": inst.get("content_motifs", [])}
    out["source"] = {"codec": P["codec_name"], "size": [W, H], "fps": P["fps"], "duration_s": round(T, 2), "bit_rate": int(P["bit_rate"])}
    # ---- màu
    allp = types_palette(src, {"all": [[0.0, T]]}, 12)["all"]; acc = sorted(allp["accent"], key=lambda r: _lum(r[0])); ink = allp["ink"]
    pick = lambda lo, hi: max([r for r in acc if lo <= _lum(r[0]) < hi] or [[None, 0]], key=lambda r: r[1])[0]
    F = sample_frames(src, 0, T, 2).astype(int); ym = (abs(F[..., 0] - 252) <= 35) & (abs(F[..., 1] - 195) <= 35) & (abs(F[..., 2] - 55) <= 40)
    pg = page_background(src, T); sf = surface_color(src, T)
    out["colors"] = {"bg": pg["bg"], "surface": sf["color"], "surface_pixel_share": sf["pixel_share"], "page": pg, "accent_dark": next(r[0] for r in acc if _lum(r[0]) >= 45), "accent_primary": pick(90, 130), "accent_mid": pick(130, 160), "accent_light": acc[-1][0],
                     "ink": ink[0][0], "ink_secondary": ink[-1][0], "yellow": None if float(ym.mean()) < 0.0001 else hexc(np.median(F[ym], 0)), "yellow_pixel_share": round(float(ym.mean()), 5),
                     "accent_pixel_share": allp["accent_share"], "ink_pixel_share": allp["ink_share"], "accent_clusters": acc, "background_top": allp["all"][:6]}
    if os.path.exists(os.path.join(cd, "types.json")): out["colors"]["by_shot_type"] = types_palette(src, json.load(open(os.path.join(cd, "types.json"))), 6)
    out["colors"]["samples"] = {k: sample(src, *v) for k, v in inst.get("samples", {}).items()}
    # ---- chữ
    ty = {}
    for name, sp in inst["text"].items():
        rows = _quiet(textrows, src, sp["t"], sp["box"], sp.get("thr", 100)); r = max(rows, key=lambda x: x["ink_h"]); xh = r["xheight"]; digits = sp.get("digits", False)
        ty[name] = {"note": sp.get("note", ""), "t": sp["t"], "digits": digits, "xheight_frac_H": round(xh / H, 4), "ink_h_frac_H": round(r["ink_h"] / H, 4), "em_frac_H": round(xh / H / (0.70 if digits else 0.5), 4), "width_frac_W": round(r["width"] / W, 3),
                    "stem_over_xheight": None if r["stem_px"] is None else round(r["stem_px"] / xh, 2), "letter_gap_over_xheight": None if r["gap_px"] is None else round(r["gap_px"] / xh, 2),
                    "line_pitch_over_xheight": None if len(rows) < 2 or not sp.get("lines") else round(float(np.median([x.get("pitch_px", 0) / x["xheight"] for x in rows[1:]])), 2)}
    out["typography"] = ty
    # ---- bố cục
    lay = {"inkmap": _quiet(inkmap, src), "corner": {}, "shadow": {}, "stroke": {}}
    for sp in inst.get("corner", []):
        c = _quiet(corner, src, sp["t"], sp["box"], sp.get("corner", "tl"), sp["mask"]); lay["corner"][sp["name"]] = {"r_cols_frac_W": round(c["r_from_cols"] / W, 4), "r_diag_frac_W": round(c["r_diag"] / W, 4), "bbox": c["bbox"]}
    for sp in inst.get("shadow", []):
        s_ = _quiet(shadow, src, sp["t"], sp["axis"], sp["idx"], sp["a"], sp["len"]); lay["shadow"][sp["name"]] = {"extent_frac_W": round(s_["extent_px_dL>1.5"] / W, 4), "max_darken_lum": s_["max_darken"]}
    for sp in inst.get("stroke", []):
        sc_ = scan(src, sp["t"], sp["axis"], sp["idx"], sp["a"], sp["b"], sp.get("thr", 40))[:3]; lay["stroke"][sp["name"]] = {"px": [r[1] for r in sc_], "frac_W": [round(r[1] / W, 4) for r in sc_]}
    lay["cards"] = {sp["name"]: cardspec(src, sp["t"], sp["box"], sp.get("thr", 253)) for sp in inst.get("cards", [])}
    lay["grid"] = {}
    for sp in inst.get("grid", []):
        g_ = gridpitch(src, sp["t"], sp["box"])
        for ax in g_.values(): ax["pitch_frac_W"] = None if not ax["pitch_px"] else round(ax["pitch_px"] / W, 4)
        lay["grid"][sp["name"]] = g_
    lay["iso"] = {sp["name"]: iso_palette(src, sp["t"], sp["box"]) for sp in inst.get("iso", [])}
    out["layout"] = lay
    # ---- chuyển động: danh sách thể hiện {primitive, part, kind, ...}
    M = []
    for sp in inst["motion"]:
        k = sp["kind"]
        try:
            if k == "ease": r = _ease_inst(src, sp, W, H)
            elif k == "typed":
                r = _quiet(typed, series(src, sp["t0"], sp["t1"], sp["box"], sp["mask"]))
                if r is not None and sp.get("chars_eye"):   # số ký tự đọc bằng mắt ở hai khung (t, n): tốc độ = Δn / Δt (không phụ thuộc bề rộng ký tự)
                    (ta, na), (tb, nb) = sp["chars_eye"]; r["chars_eye"] = sp["chars_eye"]; r["chars_per_s"] = round((nb - na) / (tb - ta), 1); r["frames_per_char"] = round((tb - ta) * FPS / (nb - na), 2); r["method"] = "eye-read char counts at two frames"
            elif k == "hop": r = _hop_inst(src, sp)
            elif k == "nodes": r = _nodes_inst(src, sp)
            elif k == "vscroll": r = _vscroll_inst(src, sp, H)
            else: raise ValueError(k)
        except (StopIteration, ValueError, IndexError, TypeError) as e:
            r = None; print("  !! không đo được", sp.get("primitive"), sp.get("part", ""), type(e).__name__, file=sys.stderr)
        M.append({"primitive": sp["primitive"], "part": sp.get("part", ""), "kind": k, "t": sp.get("t0"), "note": sp.get("label", ""), "result": r})
    out["motion"] = M
    # ---- chuyển cảnh + nhịp (mốc cắt theo luật cuts_rule.json, cùng luật cho mọi clip)
    eyep = os.path.join(cd, "cuts.json"); use_eye = bool(inst.get("curated_cuts")) and os.path.exists(eyep); prim_cuts = eyep if use_eye else cutsp
    tr = _quiet(transitions, src, prim_cuts, ep); cnt = {}
    for r in tr: cnt.setdefault(r["kind"], []).append(r["t"])
    dur = {k: round(float(np.median([r["frames_E>2"] for r in tr if r["kind"] == k])) / FPS, 3) for k in cnt}
    out["transitions"] = {"cuts": len(tr), "counts": {k: len(v) for k, v in cnt.items()}, "times": cnt, "dur_s": dur, "rows": tr, "cut_source": "eye (cuts.json)" if use_eye else "rule (cuts_rule.json)"}
    if use_eye:
        eye = load_cuts(eyep)[0][1:-1]; rule = load_cuts(cutsp)[0][1:-1]; tp = sum(1 for r_ in rule if any(abs(r_ - e_) <= 0.35 for e_ in eye)); rc = sum(1 for e_ in eye if any(abs(r_ - e_) <= 0.35 for r_ in rule))
        out["cut_agreement"] = {"rule_cuts": len(rule), "eye_cuts": len(eye), "rule_matched": tp, "eye_matched": rc, "precision": f"{tp}/{len(rule)}", "recall": f"{rc}/{len(eye)}", "tolerance_s": 0.35,
                                "rule_only": [round(r_, 3) for r_ in rule if not any(abs(r_ - e_) <= 0.35 for e_ in eye)], "eye_only": [round(e_, 3) for e_ in eye if not any(abs(r_ - e_) <= 0.35 for r_ in rule)]}
    if inst.get("cut_spot_check"): out["cut_spot_check"] = inst["cut_spot_check"]
    rh = _quiet(rhythm, prim_cuts, ep); out["rhythm"] = dict(rh); out["rhythm"]["energy"] = _quiet(energyprofile, ep, 1.0); out["rhythm"]["holds"] = _quiet(global_holds, ep, 0.35, 0.5); out["rhythm"]["bursts"] = _quiet(motion_bursts, ep, 1.0)
    dw = {nm: _quiet(dwell, src, sp["t0"], sp["t1"], sp["box"], sp.get("thr", 0.3)) for nm, sp in inst.get("dwell", {}).items()}
    allh = [h["dur_s"] for v in dw.values() for h in v if h["dur_s"] >= 1.0]
    out["rhythm"]["text_dwell"] = {"per_text": dw, "holds_ge_1s": {"n": len(allh), "median_s": round(float(np.median(allh)), 2) if allh else None, "min_s": min(allh) if allh else None, "max_s": max(allh) if allh else None}}
    return out


def _med(v): return round(float(np.median(v)), 3)


def _stat(vals):
    v = [x for x in vals if x is not None]
    return {"values": [None if x is None else round(float(x), 4) for x in vals], "n": len(v), "median": _med(v) if v else None, "min": round(float(min(v)), 4) if v else None, "max": round(float(max(v)), 4) if v else None}


def _tier(n): return "CORE" if n >= 3 else "OPTIONAL"


def _stat_rel(vals, rel, ids):
    """như _stat nhưng trung vị/khoảng/n chỉ lấy các clip có mốc cắt tin được (rel); giá trị các clip còn lại vẫn in trong `values` kèm cờ unreliable."""
    st = _stat(vals); v = [x for x, r in zip(vals, rel) if r and x is not None]
    st.update({"n": len(v), "median": _med(v) if v else None, "min": round(float(min(v)), 4) if v else None, "max": round(float(max(v)), 4) if v else None, "unreliable_clips": [i for i, r in zip(ids, rel) if not r], "tier": _tier(len(v))}); return st


def _dis(st, ratio=2.0, name=""):
    """cờ không khớp: max/min > ratio giữa các clip (giá trị dương)."""
    v = [x for x in st["values"] if x is not None and x > 0]
    return [f"{name} varies {max(v) / min(v):.1f}x ({min(v)}-{max(v)})"] if len(v) > 1 and max(v) / min(v) > ratio else []


def _family(e): return re.sub(r"\(.*\)", "", e) if e else None   # giữ nguyên bậc và chiều: power1.inOut khác power2.out


def _hexmed(hs):
    a = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in hs]); d = max([float(np.linalg.norm(a[i] - a[j])) for i in range(len(a)) for j in range(len(a))] or [0.0])
    return hexc(np.median(a, 0)), round(d, 1)


def merge_style(ms):
    """gộp số đo thô của các clip -> style.json: mỗi token có giá trị từng clip, trung vị, khoảng, n và CORE (>=3 clip) / OPTIONAL (1-2 clip)."""
    ids = [m["id"] for m in ms]; N = len(ms)
    out = {"name": "corporate-motion", "version": 2, "clips": [{"id": m["id"], "title": m["title"], "url": m["url"], "source": m["source"]} for m in ms],
           "tiering": "CORE = token measured in >= 3 of the clips; OPTIONAL = 1-2 clips. min-max across clips; median over the clips that have it (n).", "units": "fractions of frame W/H (x1080 / x1920 for px), seconds at 30fps"}
    col = {}
    for k in ("bg", "surface", "accent_dark", "accent_primary", "accent_mid", "accent_light", "ink", "ink_secondary", "yellow"):
        hs = [m["colors"].get(k) if (k != "yellow" or m["colors"]["yellow_pixel_share"] >= 0.0001) else None for m in ms]; present = [h for h in hs if h]
        if not present: col[k] = {"values": hs, "n": 0, "tier": "OPTIONAL"}; continue
        med, spread = _hexmed(present); col[k] = {"values": hs, "median": med, "max_rgb_distance": spread, "n": len(present), "tier": _tier(len(present))}
    col["yellow"]["pixel_share_by_clip"] = [m["colors"]["yellow_pixel_share"] for m in ms]; col["surface"]["pixel_share_by_clip"] = [m["colors"]["surface_pixel_share"] for m in ms]
    pgs = [m["colors"]["page"] for m in ms]
    def stops(key):
        n_ = len(pgs[0][key]); r_ = []
        for i in range(n_):
            hx = [pg[key][i][1] for pg in pgs]; pres = [h for h in hx if h]
            r_.append({"at": pgs[0][key][i][0], "values": hx, "median": _hexmed(pres)[0] if pres else None})
        return r_
    wsh = [pg["white"]["frame_share"] for pg in pgs]; wd = [pg["white"]["frame_share_by_decile"] for pg in pgs]
    col["page_background"] = {"modes": {"tint": {"colour_median": _hexmed([pg["bg"] for pg in pgs])[0], "colour_by_clip": [pg["bg"] for pg in pgs], "frame_share": _stat([pg["tint_frame_share"] for pg in pgs]), "lum_p10": _stat([pg["tint_lum_p10_p90"][0] for pg in pgs]), "lum_p90": _stat([pg["tint_lum_p10_p90"][1] for pg in pgs]), "p10_colour_by_clip": [pg["tint_p10_p50_p90"][0] for pg in pgs], "p90_colour_by_clip": [pg["tint_p10_p50_p90"][2] for pg in pgs]},
                                       "white": {"colour_median": _hexmed([pg["white"]["colour"] for pg in pgs if pg["white"]["colour"]])[0], "colour_by_clip": [pg["white"]["colour"] for pg in pgs], "frame_share": _stat(wsh), "edge_pixel_share": _stat([pg["white"]["edge_pixel_share"] for pg in pgs]),
                                                 "frame_share_by_decile_median": [_med([d[i] for d in wd]) for i in range(10)], "frame_share_by_decile_by_clip": wd}},
                              "mode_rule": "frame = white page when > 70% of its edge pixels (left/right 4%, top 3%, bottom 5%) are card-white (min channel >= 253); otherwise tint. Both modes are normal: the page is NOT always tinted and NOT always white.",
                              "tint_gradient": {"vertical_stops": stops("vertical_stops"), "horizontal_stops_bottom_row": stops("horizontal_stops_bottom_row"), "centre_median": _hexmed([pg["centre"] for pg in pgs if pg["centre"]])[0],
                                                "vertical_lum_delta_top_minus_bottom": _stat([pg["vertical_lum_delta_top_minus_bottom"] for pg in pgs]), "horizontal_lum_delta_left_minus_right": _stat([pg["horizontal_lum_delta_left_minus_right"] for pg in pgs]),
                                                "centre_minus_edge_lum": _stat([pg["centre_minus_edge_lum"] for pg in pgs]),
                                                "note": "centre_minus_edge_lum is NEGATIVE (median -2.5): the centre patch is slightly DARKER than the edge median (cards' shadows and light-blue elements sit there), while the side-edge stops show the middle band ~2.5 lum lighter than the top/bottom. Direction is not consistent between clips, magnitude <= 8 lum: treat the tint as flat."},
                              "n": len(pgs), "tier": _tier(len(pgs))}
    col["accent_pixel_share"] = _stat([m["colors"]["accent_pixel_share"] for m in ms]); col["ink_pixel_share"] = _stat([m["colors"]["ink_pixel_share"] for m in ms])
    col["rule"] = "one blue hue in 4-5 tints on a near-white field, black ink + one grey; yellow is a rare single accent"
    out["colors"] = col
    roles = {}
    for m in ms:
        for r in m["typography"]: roles.setdefault(r, None)
    for r in list(roles):
        have = [m["typography"].get(r) for m in ms]; present = [h for h in have if h]
        g = lambda f: _stat([h[f] if h else None for h in have])
        roles[r] = {"em_frac_H": g("em_frac_H"), "xheight_frac_H": g("xheight_frac_H"), "stem_over_xheight": g("stem_over_xheight"), "letter_gap_over_xheight": g("letter_gap_over_xheight"), "line_pitch_over_xheight": g("line_pitch_over_xheight"),
                    "n": len(present), "tier": _tier(len(present)), "digits": present[0]["digits"]}
        roles[r]["em_px_1080x1920_median"] = round(roles[r]["em_frac_H"]["median"] * 1920)
        roles[r]["disagree"] = _dis(roles[r]["em_frac_H"], 2.0, "size") + _dis(roles[r]["stem_over_xheight"], 2.0, "stem/x-height") + _dis(roles[r]["letter_gap_over_xheight"], 2.0, "letter gap")
    out["typography"] = {"roles": roles, "assumption": "x-height = 0.5 em (lower-case text) or digit/cap height = 0.70 em (digits roles); +-10%",
                         "families": {"guess": "geometric heavy sans, single-storey o/g/a (Gilroy / Outfit look); not matched to a font file", "vietnamese_safe_substitutes_to_verify": ["Lexend", "Be Vietnam Pro", "Plus Jakarta Sans", "Inter"], "rule": "run the Vietnamese glyph check (docs/teardown-process.md step 2) before choosing"},
                         "weight_basis": "guess: stem/x-height ~0.35 = ExtraBold-Black class (800); small labels 700-800"}
    lay = {"safe_zone": {}, "corner_radius_frac_W": {}, "shadow_extent_frac_W": {}, "stroke_frac_W": {}}; ik = [m["layout"]["inkmap"] for m in ms]
    lay["safe_zone"] = {"bbox_left_median": _stat([i["bbox_left_p10_p50"][1] for i in ik]), "bbox_right_median": _stat([i["bbox_right_p50_p90"][0] for i in ik]), "bbox_top_median": _stat([i["bbox_top_p10_p50"][1] for i in ik]),
                        "bbox_bottom_median": _stat([i["bbox_bottom_p50_p90"][0] for i in ik]), "ink_share_below_80pct_H": _stat([i["ink_share_below_80pct_H"] for i in ik]), "ink_share_above_10pct_H": _stat([i["ink_share_above_10pct_H"] for i in ik]), "tier": "CORE", "n": N}
    for grp, key, tgt in (("corner", "r_diag_frac_W", "corner_radius_frac_W"), ("shadow", "extent_frac_W", "shadow_extent_frac_W"), ("stroke", "frac_W", "stroke_frac_W")):
        for nme in sorted({n for m in ms for n in m["layout"][grp]}):
            vals = []
            for m in ms:
                v = m["layout"][grp].get(nme); x = None if v is None else v[key]; vals.append(None if x is None else (x[0] if isinstance(x, list) and x else (None if isinstance(x, list) else x)))
            st = _stat(vals); st["tier"] = _tier(st["n"]); st["disagree"] = _dis(st, 2.0, nme); lay[tgt][nme] = st
    cards = {}
    for nme in sorted({n for m in ms for n in m["layout"].get("cards", {})}):
        cs = [m["layout"].get("cards", {}).get(nme) for m in ms]; cs = [c if c else None for c in cs]; g = lambda f: [None if c is None else f(c) for c in cs]
        ent = {"width_frac_W": _stat(g(lambda c: c["width_frac_W"])), "height_frac_H": _stat(g(lambda c: c["height_frac_H"])), "center_x_frac_W": _stat(g(lambda c: c["center_x_frac_W"])),
               "padding_left_frac_W": _stat(g(lambda c: c["padding_frac_W"]["left"] if c["padding_frac_W"] else None)), "padding_top_frac_H": _stat(g(lambda c: c["padding_frac_W"]["top"] if c["padding_frac_W"] else None)),
               "padding_right_frac_W": _stat(g(lambda c: c["padding_frac_W"]["right"] if c["padding_frac_W"] else None)), "padding_bottom_frac_H": _stat(g(lambda c: c["padding_frac_W"]["bottom"] if c["padding_frac_W"] else None)),
               "shadow_blur_frac_W": _stat(g(lambda c: c["shadow"]["blur_frac_W"])), "shadow_offset_y_frac_W": _stat(g(lambda c: c["shadow"]["offset_y_frac_W"])), "shadow_alpha": _stat(g(lambda c: c["shadow"]["alpha_if_accent_dark_tint"] if 0.05 <= c["shadow"]["alpha_if_accent_dark_tint"] <= 0.3 else None))}
        ent["n"] = ent["width_frac_W"]["n"]; ent["tier"] = _tier(ent["n"]); ent["disagree"] = _dis(ent["width_frac_W"], 1.6, "width") + _dis(ent["shadow_blur_frac_W"], 2.0, "shadow blur"); cards[nme] = ent
    lay["cards"] = cards
    gr = {}
    for nme in sorted({n for m in ms for n in m["layout"].get("grid", {})}):
        gs = [m["layout"].get("grid", {}).get(nme) for m in ms]; px = [None if g_ is None else g_["x"]["pitch_frac_W"] for g_ in gs]; py = [None if g_ is None else g_["y"]["pitch_frac_W"] for g_ in gs]
        ct = [None if g_ is None else g_["x"]["contrast_lum"] for g_ in gs]; ent = {"pitch_x_frac_W": _stat(px), "pitch_y_frac_W": _stat(py), "contrast_lum": _stat(ct)}; ent["n"] = ent["pitch_x_frac_W"]["n"]; ent["tier"] = _tier(ent["n"]); ent["disagree"] = _dis(ent["pitch_x_frac_W"], 1.6, "pitch"); gr[nme] = ent
    lay["grid"] = gr
    iso = {}
    for nme in sorted({n for m in ms for n in m["layout"].get("iso", {})}):
        pal = [m["layout"].get("iso", {}).get(nme) for m in ms]; have = [sorted(sorted(pl_, key=lambda r: -r[1])[:3], key=lambda r: -_lum(r[0])) for pl_ in pal if pl_ and len(pl_) >= 3]
        faces = [_hexmed([h[i][0] for h in have])[0] for i in range(3)] if have else None
        iso[nme] = {"faces_light_to_dark_median": faces, "by_clip": pal, "n": len(have), "tier": _tier(len(have)), "note": "3 most common saturated clusters in the block's box, sorted light to dark"}
    lay["iso"] = iso
    out["layout"] = lay
    prim = {}
    for ci, m in enumerate(ms):
        for it in m["motion"]: prim.setdefault(it["primitive"] + ("." + it["part"] if it["part"] else ""), {}).setdefault(ci, []).append(it)
    mo = {}
    for key, byc in prim.items():
        ok = {ci: [x for x in its if x["result"]] for ci, its in byc.items()}; ok = {ci: v for ci, v in ok.items() if v}
        if not ok: mo[key] = {"n": 0, "tier": "OPTIONAL", "note": "instance found but not measurable"}; continue
        kind = next(iter(ok.values()))[0]["kind"]; ent = {"kind": kind, "clips_with_instance": [ids[ci] for ci in ok], "n": len(ok), "tier": _tier(len(ok))}
        def per_clip(fn):
            res = []
            for ci in range(N):
                vs = [fn(x["result"]) for x in ok.get(ci, [])]; vs = [v for v in vs if v is not None]; res.append(_med(vs) if vs else None)
            return res
        if kind == "ease":
            for f in ("reach_s", "settle_s", "overshoot", "distance_frac"): ent[f] = _stat(per_clip(lambda r, f=f: r[f]))
            ent["ease_nearest_by_clip"] = [ok[ci][0]["result"]["ease"] if ci in ok else None for ci in range(N)]
            def _bz(r):   # giữ bezier chỉ khi khớp tốt (rmse <= 0.05) và hợp lý: không quá đà thì y1,y2 không vượt 1; quá đà thì cho phép
                if r["bezier_rmse"] > 0.05: return None
                if r["overshoot"] < 0.03 and (r["bezier"][1] > 1.0 or r["bezier"][3] > 1.05 or r["bezier"][1] < -0.1): return None
                return r["bezier"]
            ent["bezier_by_clip"] = [_bz(ok[ci][0]["result"]) if ci in ok else None for ci in range(N)]
            ent["bezier_note"] = "cubic-bezier kept only where fit rmse <= 0.05 and plausible (no overshoot in the data -> no y>1); otherwise null. Coarse grid fit, treat as a hint; the named GSAP ease is the working value."
            ent["frac_of"] = next(iter(ok.values()))[0]["result"]["frac_of"]; why = []
            fams = {_family(e) for e in ent["ease_nearest_by_clip"] if e}
            if len(fams) > 1: why.append("ease family differs: " + ", ".join(sorted(fams)))
            rs = [v for v in ent["reach_s"]["values"] if v]
            if len(rs) > 1 and max(rs) / max(min(rs), 1e-6) > 1.5 and max(rs) - min(rs) > 0.1: why.append(f"reach differs {min(rs)}-{max(rs)}s")
            ov = [v for v in ent["overshoot"]["values"] if v is not None]
            if len(ov) > 1 and max(ov) - min(ov) > 0.08: why.append(f"overshoot differs {min(ov)}-{max(ov)}")
            ent["disagree"] = why
        elif kind == "typed": ent["chars_per_s"] = _stat(per_clip(lambda r: r["chars_per_s"])); ent["frames_per_char"] = _stat(per_clip(lambda r: r["frames_per_char"]))
        elif kind == "hop":
            for f in ("hop_frames", "pop_scale", "settle_s"): ent[f] = _stat(per_clip(lambda r, f=f: r[f]))
            ss = [v for v in ent["settle_s"]["values"] if v is not None]; ent["disagree"] = [f"settle differs {min(ss)}-{max(ss)}s"] if len(ss) > 1 and max(ss) - min(ss) > 0.1 else []
        elif kind == "nodes": ent["mean_gap_s"] = _stat(per_clip(lambda r: r["mean_gap_s"])); ent["arrival_span_s"] = _stat(per_clip(lambda r: r["arrival_span_s"]))
        elif kind == "vscroll":
            for n in sorted({n for ci in ok for n in ok[ci][0]["result"]}):
                ent[n] = {"peak_frac_H_per_frame": _stat([ok[ci][0]["result"].get(n, {}).get("peak_frac_H_per_frame") if ci in ok else None for ci in range(N)])}
        if kind == "vscroll":
            pk = [v for n in ent if isinstance(ent[n], dict) and "peak_frac_H_per_frame" in ent[n] for v in ent[n]["peak_frac_H_per_frame"]["values"] if v]
            ent["disagree"] = ["peak speed differs %.3f-%.3f H/frame" % (min(pk), max(pk))] if len(pk) > 1 and max(pk) / min(pk) > 2 else []
        base = key.split(".")[0]; cn = {ids[ci]: ms[ci]["notes"][base] for ci in range(N) if base in ms[ci].get("notes", {})}
        if cn: ent["clip_notes"] = cn; ent.setdefault("disagree", []).append("see clip_notes (observed differences not captured by the numbers)")
        mo[key] = ent
    for ci in range(N):   # primitive chỉ có ghi chú, không đo được ở clip nào (vd gõ từng từ, cờ hiện 1 khung)
        for base, txt in ms[ci].get("notes", {}).items():
            if base.startswith("_"): continue
            if not any(k.split(".")[0] == base for k in mo): mo[base] = {"n": 0, "tier": "OPTIONAL", "clip_notes": {}, "note": "seen but not measurable"}
            if base in mo and "clip_notes" in mo[base] and ids[ci] not in mo[base]["clip_notes"]: mo[base]["clip_notes"][ids[ci]] = txt
    out["motion"] = mo
    cm = {}
    for ci in range(N):
        for mt in ms[ci].get("content_motifs", []): cm.setdefault(mt, []).append(ids[ci])
    out["observations_by_clip"] = {ids[ci]: {k: v for k, v in ms[ci].get("notes", {}).items() if k.startswith("_")} for ci in range(N) if any(k.startswith("_") for k in ms[ci].get("notes", {}))}
    out["content_not_style"] = {"rule": "motif seen in one clip only = content of that clip, not style (shared visual vocabulary is listed in preset.md)", "motifs": {k: v for k, v in cm.items()}}
    rel = [m["transitions"]["cut_source"].startswith("eye") for m in ms]; nrel = sum(rel)
    why = {}
    for m, r in zip(ms, rel):
        sc = m.get("cut_spot_check")
        why[m["id"]] = {"reliable": r, "reason": "eye-curated cuts (precision/recall of the rule on this clip: " + (m["cut_agreement"]["precision"] + " / " + m["cut_agreement"]["recall"] if m.get("cut_agreement") else "n/a") + ")" if r else
                        f"rule cuts; by-eye spot-check of 10 cuts: {sc['real_cuts']}/10 real (precision only: recall unknown, so missed soft changes cannot be bounded; the rule's recall on clip 1 was 25/30)" if sc else "rule cuts, not checked"}
    kinds = sorted({k for m in ms for k in m["transitions"]["counts"]}); tr = {"cuts": _stat_rel([m["transitions"]["cuts"] for m in ms], rel, ids), "kinds": {}}
    for k in kinds:
        sh_ = [m["transitions"]["counts"].get(k, 0) / m["transitions"]["cuts"] for m in ms]; rv = [x for x, r in zip(sh_, rel) if r]; present = sum(1 for x in rv if x > 0)
        tr["kinds"][k] = {"share_by_clip": [round(x, 3) for x in sh_], "median_share": _med(rv) if rv else None, "min": round(min(rv), 3) if rv else None, "max": round(max(rv), 3) if rv else None, "n": present, "tier": _tier(present),
                          "duration_s": _stat_rel([m["transitions"]["dur_s"].get(k) for m in ms], rel, ids), "seen_in_unreliable_clips": [i for i, x, r in zip(ids, sh_, rel) if (not r) and x > 0]}
    tr["approximate"] = True; tr["cut_source_by_clip"] = [m["transitions"]["cut_source"] for m in ms]; tr["cut_reliability"] = why; tr["reliable_clip_count"] = nrel
    ca = [m.get("cut_agreement") for m in ms if m.get("cut_agreement")]
    tr["cut_rule"] = ("UNRELIABLE for clips 2-4: their cuts come from the energy rule (E_peak>=9 or D_peak>=0.15, >=1s apart), which on clip 1 has precision " + (ca[0]["precision"] if ca else "n/a") + " and recall " + (ca[0]["recall"] if ca else "n/a") + " (tol 0.35s), and in a by-eye spot-check of 10 cuts per clip only 5/10, 6/10 and 8/10 were real (recall never checked). "
                      "Cut-dependent tokens (cuts, shot length, cuts/min, end hold, transition shares and durations) therefore use clip 1's eye cuts only (n=1); clips 2-4 are listed in `values` but excluded from median/min/max/n.")
    tr["cut_agreement_clip1"] = ca[0] if ca else None; tr["spot_check_by_clip"] = {m["id"]: m.get("cut_spot_check") for m in ms if m.get("cut_spot_check")}
    out["transitions"] = tr
    rh = {}
    for k in ("len_median", "len_p10", "len_p90", "cuts_per_min", "shots"): rh["shot_" + k] = _stat_rel([m["rhythm"][k] for m in ms], rel, ids)
    rh["energy_mean"] = _stat([m["rhythm"]["energy"]["mean"] for m in ms]); rh["energy_median"] = _stat([m["rhythm"]["energy"]["median"] for m in ms]); rh["energy_window_p90"] = _stat([m["rhythm"]["energy"]["window_mean_p90"] for m in ms])
    rh["still_frame_share_E_lt_0.1"] = _stat([m["rhythm"]["energy"]["frac_frames_still(E<0.1)"] for m in ms]); rh["bursts_per_min"] = _stat([m["rhythm"]["bursts"]["per_min"] for m in ms]); rh["burst_len_median_s"] = _stat([m["rhythm"]["bursts"]["len_median_s"] for m in ms])
    rh["hold_median_s"] = _stat([m["rhythm"]["holds"]["median_s"] for m in ms]); rh["hold_share_of_clip"] = _stat([m["rhythm"]["holds"]["share_of_clip"] for m in ms]); rh["end_hold_median_s"] = _stat_rel([m["rhythm"]["end_hold_median_s"] for m in ms], rel, ids)
    rh["text_dwell_median_s"] = _stat([m["rhythm"]["text_dwell"]["holds_ge_1s"]["median_s"] for m in ms]); rh["tier"] = "CORE"; rh["n"] = N
    rh["approximate"] = True; rh["approximate_note"] = "shot_*, end_hold_median_s: clip 1 only (eye cuts), clips 2-4 unreliable (see transitions.cut_rule). energy, still share, bursts, holds and text dwell do not depend on cuts and use all 4 clips"
    out["rhythm"] = rh
    out["build_defaults"] = _build_defaults(out, ms)
    out["beat_formula"] = ["wow demo / hook", "hanging number or question", "authority quote or setup", "metaphor", "checklist / steps", "costly detail", "lessons", "CTA", "loop back to the hook"]
    return _r(out)


def _canon_ease(ent):
    """một ease + thời lượng chuẩn cho primitive: ease = họ (power/back/circ...) mà nhiều clip dùng nhất; hoà thì theo clip Power BI (clip đầu); thời lượng/quá đà = trung vị trên các clip dùng họ đó."""
    names = ent["ease_nearest_by_clip"]; fam = [_family(n) for n in names]; cnt = {}
    for f in fam:
        if f: cnt[f] = cnt.get(f, 0) + 1
    top = max(cnt.values()); tied = [f for f, c in cnt.items() if c == top]; chosen = fam[0] if fam[0] in tied else sorted(tied)[0]
    idx = [i for i, f in enumerate(fam) if f == chosen]; rep = names[idx[0]] if names[0] and fam[0] == chosen else max({names[i] for i in idx}, key=lambda n: [names[i] for i in idx].count(n))
    def med_of(stat_): v = [stat_["values"][i] for i in idx if stat_["values"][i] is not None]; return _med(v) if v else None
    return {"gsap_ease": "none" if rep == "none" else rep, "consensus": top >= 2 and len(tied) == 1, "family_share": f"{top}/{sum(cnt.values())}", "tie_broken_by_power_bi_clip": len(tied) > 1, "duration_s": med_of(ent["reach_s"]), "settle_s": med_of(ent["settle_s"]), "overshoot": med_of(ent["overshoot"]),
            "distance_frac": med_of(ent["distance_frac"]) if ent["distance_frac"]["median"] is not None else None, "distance_of": ent["frac_of"], "clip_indexes_used": idx}


def _build_defaults(out, ms):
    """MỘT giá trị cho mỗi token, luật chọn nêu rõ ngay trong khối này; chỉ dùng số đã gộp ở trên (cộng quyết định có ghi chú)."""
    bd = {"rule": "one value per token. Colours/sizes/specs: median over the clips that have it. Eases: the ease family most CORE clips share, ties broken toward the Power BI clip (clip 1); duration/overshoot = median over the clips of that family. Anything not measured is labelled guess.",
          "status": "proposal derived from measurements; the font is pending owner approval (chờ chủ duyệt)"}
    c = out["colors"]; pgb = c["page_background"]
    bd["colors"] = {k: c[k]["median"] for k in ("surface", "accent_dark", "accent_primary", "accent_mid", "accent_light", "ink", "ink_secondary", "yellow")}
    bd["colors"]["surface_measured_median"] = c["surface"]["median"]; bd["colors"]["surface"] = "#ffffff" if min(int(c["surface"]["median"][i:i + 2], 16) for i in (1, 3, 5)) >= 0xfa else c["surface"]["median"]
    bd["colors"]["page_tint"] = c["bg"]["median"]; bd["colors"]["yellow_use"] = "single small accent (highlight bar, flag); absent in 1 of 4 clips"
    md = pgb["modes"]; ws_ = md["white"]["frame_share"]; ts_ = md["tint"]["frame_share"]; dec = md["white"]["frame_share_by_decile_median"]; wdec = [i for i, v in enumerate(dec) if v > 0.4]
    bd["page_background"] = {"modes": {"tint": {"colour": md["tint"]["colour_median"], "frame_share_median": ts_["median"], "frame_share_range": [ts_["min"], ts_["max"]], "lum_range_p10_p90": [md["tint"]["lum_p10"]["median"], md["tint"]["lum_p90"]["median"]]},
                                       "white": {"colour": "#ffffff", "measured_median": md["white"]["colour_median"], "frame_share_median": ws_["median"], "frame_share_range": [ws_["min"], ws_["max"]]}},
                             "when_to_use": f"two page modes, both normal. Tint ({md['tint']['colour_median']}) is the default: {round(100 * ts_['median'])}% of frames (range {round(100 * ts_['min'])}-{round(100 * ts_['max'])}%). White ({round(100 * ws_['median'])}% of frames, range {round(100 * ws_['min'])}-{round(100 * ws_['max'])}%) is used for "
                                            + ("the parts of the clip at " + ", ".join(f"{10 * i}-{10 * (i + 1)}%" for i in wdec) + " of the running time (median over clips)" if wdec else "no single part of the clip (white frames are spread through the clip: no decile has more than 40% white in the median)")
                                            + ". What triggers white inside a clip (title cards, quiet explainer scenes, end card) is NOT measured; pick per scene, and keep the surface cards `#ffffff` in both modes (on white they are separated by the shadow only).",
                             "white_share_by_decile_median": dec,
                             "tint_flat_css": md["tint"]["colour_median"], "tint_optional_vignette_stops": [[st["at"], st["median"]] for st in pgb["tint_gradient"]["vertical_stops"]],
                             "note": "the tint is practically flat (differences <= 8 lum). centre_minus_edge_lum median " + str(pgb["tint_gradient"]["centre_minus_edge_lum"]["median"]) + " = the centre patch is slightly DARKER than the edge median; the side-edge vertical stops show the middle band lighter than top/bottom, so the direction is inconsistent: use the flat colour. Scenes swing in tint between p10 and p90 (see tint lum range)."}
    fc = os.path.join(HERE, "font_check.json"); fw = int(json.load(open(fc))["recommendation"]["weight"]) if os.path.exists(fc) else 800
    ty = out["typography"]["roles"]; scale = {}
    for r, v in ty.items():
        if v["tier"] != "CORE": continue
        scale[r] = {"font_size_px_1080x1920": int(round(v["em_px_1080x1920_median"] / 2.0) * 2), "weight": fw if (v["stem_over_xheight"]["median"] or 0) * (0.70 if v["digits"] else 0.5) >= 0.15 else fw - 100, "range_px": [round(v["em_frac_H"]["min"] * 1920), round(v["em_frac_H"]["max"] * 1920)], "disagree": v["disagree"]}
    cap = ty["caption"]["line_pitch_over_xheight"]["median"]; bd["type_scale"] = {"roles": scale, "line_height_em": round(cap * 0.5, 2) if cap else 1.05, "letter_spacing": "0 (measured glyph gap/x-height 0.14-0.18)", "colour_pattern": "ink for plain words, accent_primary for the key word",
                                                                                   "note": "sizes are medians; display_number varies a lot between clips (see range_px) - pick per layout, the median is the default"}
    cd = out["layout"]["cards"]; cr = out["layout"]["corner_radius_frac_W"]; spec = {}
    for nm in ("main_card", "pill"):
        if nm not in cd or cd[nm]["n"] < 3: continue
        e = cd[nm]; r = cr.get(nm, {}).get("median"); bl = out["layout"]["shadow_extent_frac_W"][nm]["median"]; off = round(bl / 4, 4); al = e["shadow_alpha"]["median"]; W = 1080
        spec[nm] = {"width_frac_W": e["width_frac_W"]["median"], "width_px_1080": round(e["width_frac_W"]["median"] * W), "height_frac_H": e["height_frac_H"]["median"],
                    "padding_px_1080": {"left": round((e["padding_left_frac_W"]["median"] or 0) * W), "right": round((e["padding_right_frac_W"]["median"] or 0) * W), "top": round((e["padding_top_frac_H"]["median"] or 0) * 1920), "bottom": round((e["padding_bottom_frac_H"]["median"] or 0) * 1920)},
                    "radius_px_1080": None if r is None else round(r * W), "box_shadow": f"0 {round((off or 0) * W)}px {round((bl or 0) * W)}px rgba(21,101,192,{al})", "surface": bd["colors"]["surface"], "n": e["n"], "disagree": e["disagree"],
                    "note": "box-shadow: blur = measured extent below the card edge (layout.shadow_extent_frac_W); alpha = median darkening at 4px converted with an assumed accent_dark tint (guess); y offset = blur/4 is a GUESS (the above-edge extent could not be measured cleanly)"}
    bd["card_specs"] = spec
    gd = out["layout"]["grid"]; iso = out["layout"]["iso"]
    bd["background_pattern"] = {"default": "line_grid (clips 1, 4); dot_grid in clips 2, 3 - both very faint (contrast 2-24 lum), pattern family present in 4/4 clips", "patterns": {k: {"pitch_frac_W": v["pitch_x_frac_W"]["median"], "pitch_px_1080": None if v["pitch_x_frac_W"]["median"] is None else round(v["pitch_x_frac_W"]["median"] * 1080), "contrast_lum": v["contrast_lum"]["median"], "n": v["n"], "tier": v["tier"]} for k, v in gd.items()}}
    bd["iso_block"] = {k: {"faces_light_to_dark": v["faces_light_to_dark_median"], "n": v["n"], "tier": v["tier"]} for k, v in iso.items()}
    sz = out["layout"]["safe_zone"]; L, R, Tp, B = (sz[k]["median"] for k in ("bbox_left_median", "bbox_right_median", "bbox_top_median", "bbox_bottom_median"))
    bd["safe_zone"] = {"content_box_px_1080x1920": [round(L * 1080), round(Tp * 1920), round(R * 1080), round(B * 1920)], "content_box_frac": [L, Tp, R, B], "reserved_bottom_frac_H": round(1 - B, 3), "note": "median ink bounding box over 1fps frames; bottom ~26% of the frame is mostly empty (platform UI)"}
    eases = {}
    for k, v in out["motion"].items():
        if v.get("kind") == "ease" and v["tier"] == "CORE": eases[k] = _canon_ease(v)
    if "pill_progress" in out["motion"] and out["motion"]["pill_progress"]["tier"] == "CORE":
        pp = out["motion"]["pill_progress"]; eases["pill_progress"] = {"hop_frames": 1, "pop_scale": pp["pop_scale"]["median"], "settle_s": pp["settle_s"]["median"], "disagree": pp.get("disagree")}
    po = {}
    for it in ms[0]["motion"]:
        if it["primitive"] == "chart_pop" and it["result"] and it["result"].get("onset_t") is not None: po[it["part"]] = it["result"]["onset_t"]
    if "chart_pop.bar1" in eases and len(po) == 3: eases["chart_pop.bar1"]["stagger_s_clip1_only"] = [round(po["bar2"] - po["bar1"], 3), round(po["bar3"] - po["bar2"], 3)]; eases["chart_pop.bar1"]["use_for_all_bars"] = "bars 2-3 have too few clips (family 1/3); reuse bar1 ease, duration and overshoot for every bar"
    for k_, v_ in eases.items():
        if v_.get("consensus") is False: v_["note"] = "no two clips share an ease family: the value is the Power BI clip's (tie rule); treat as a free choice"
    bd["motion"] = eases; bd["motion_optional_not_defaulted"] = sorted(k for k, v in out["motion"].items() if v["tier"] != "CORE")
    relids = [i for i, r in zip([c_["id"] for c_ in out["clips"]], [out["transitions"]["cut_reliability"][c_["id"]]["reliable"] for c_ in out["clips"]]) if r]
    bd["transitions"] = {"source": "reliable (eye-cut) clips only: " + ", ".join(relids) + f" (n={len(relids)}); clips 2-4 excluded: rule cuts only 5/10, 6/10, 8/10 real in the spot-check and recall unknown", "n": len(relids),
                         "kinds": {k: {"share": v["median_share"], "duration_s": v["duration_s"]["median"], "seen_in_unreliable_clips": v["seen_in_unreliable_clips"]} for k, v in out["transitions"]["kinds"].items()}}
    rh = out["rhythm"]; bd["rhythm"] = {"cut_dependent_source": "clip 1 only (eye cuts), n=1", "shot_len_median_s": rh["shot_len_median"]["median"], "shot_len_p10_p90_s": [rh["shot_len_p10"]["median"], rh["shot_len_p90"]["median"]], "cuts_per_min": rh["shot_cuts_per_min"]["median"], "hold_median_s": rh["hold_median_s"]["median"], "burst_len_median_s": rh["burst_len_median_s"]["median"], "bursts_per_min": rh["bursts_per_min"]["median"], "approximate": True}
    fc = os.path.join(HERE, "font_check.json")
    if os.path.exists(fc): bd["font"] = json.load(open(fc))["recommendation"]
    od = os.path.join(HERE, "owner_decisions.json")   # quyết định của chủ đè lên đề xuất đo được
    if os.path.exists(od) and "font" in bd:
        d = json.load(open(od, encoding="utf-8")).get("font")
        if d: bd["font"].update({"family": d["family"], "weight": d["weight"], "status": f"chủ duyệt {d['date']}: {d['note']}"})
    return bd


def _r(x, n=3):
    if isinstance(x, float): return round(x, n)
    if isinstance(x, dict): return {k: _r(v, n) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [_r(v, n) for v in x]
    return x


def cuts_rule(epath, total, out, thr_e=9.0, thr_d=0.15, min_gap=1.0, floor=4.0):
    """mốc cắt theo luật (dùng chung cho mọi clip để so sánh được): ứng viên = cụm năng lượng > floor; giữ cụm có đỉnh E >= thr_e hoặc D >= thr_d;
    hai mốc cách < min_gap giây thì giữ mốc E lớn hơn. Ghi {"S","TOTAL","fps","rule"}."""
    E, D = load_energy(epath); keep = []
    for c in clusters(E, floor):
        pk = c[int(np.argmax(E[c]))]
        if E[pk] >= thr_e or D[pk] >= thr_d: keep.append(((pk + 1) / FPS, float(E[pk])))
    out_l = []
    for t, e in keep:
        if out_l and t - out_l[-1][0] < min_gap:
            if e > out_l[-1][1]: out_l[-1] = (t, e)
        else: out_l.append((t, e))
    S = [0.0] + [round(t, 3) for t, _ in out_l] + [round(total, 3)]
    json.dump({"S": S, "TOTAL": round(total, 3), "fps": FPS, "rule": f"E_peak>={thr_e} or D_peak>={thr_d}, min_gap {min_gap}s, floor {floor}"}, open(out, "w")); print(len(S) - 1, "cảnh ->", out)


# ---- main
def main():
    pos, o = parse_opts(sys.argv[1:])
    cd = os.path.abspath(o["clip"]) if "clip" in o else HERE   # --clip DIR: mọi tệp mặc định (source.mp4, cuts.json, tmp/, frames/) nằm trong DIR
    src = o.get("src", os.path.join(cd, "source.mp4")); cuts_p = o.get("cuts", os.path.join(cd, "cuts.json"))
    ep = o.get("energy", os.path.join(cd, "tmp/energy.json"))
    if not pos: print(__doc__ if __doc__ else open(__file__).read().split("import sys")[0]); return
    cmd, a = pos[0], pos[1:]
    if cmd == "info": print(json.dumps(probe(src)))
    elif cmd == "energy": energy(src, o.get("out", ep))
    elif cmd == "candidates": candidates(ep, float(o.get("thr", 4)))
    elif cmd == "cuts": write_cuts(ep, [float(x) for x in o["times"].split(",")], float(o.get("total", probe(src)["duration"])), o.get("out", cuts_p))
    elif cmd == "cuts-rule": cuts_rule(ep, float(o.get("total", probe(src)["duration"])), o.get("out", cuts_p), float(o.get("thr-e", 9)), float(o.get("thr-d", 0.15)), float(o.get("min-gap", 1.0)))
    elif cmd == "strips": strips(src, [float(x) for x in a[0].split(",")], o.get("out", os.path.join(cd, "frames/strips.jpg")))
    elif cmd == "grid": grid(src, float(a[0]), float(a[1]), float(a[2]), int(a[3]), int(a[4]), o.get("out", os.path.join(cd, "frames/grid.jpg")))
    elif cmd == "sheets": sheets(src, cuts_p, os.path.join(cd, "frames"), int(o.get("fps", 4)))
    elif cmd == "palette": print(json.dumps(palette(src, float(a[0]), float(a[1]), int(a[2]) if len(a) > 2 else 8, float(o["sat"]) if "sat" in o else None)))
    elif cmd == "palette-types": print(json.dumps(types_palette(src, json.load(open(o.get("types", os.path.join(cd, "types.json")))), int(a[0]) if a else 8), ensure_ascii=False, indent=1))
    elif cmd == "sample": print(sample(src, float(a[0]), int(a[1]), int(a[2]), int(a[3]) if len(a) > 3 else 3))
    elif cmd == "series": print_series(series(src, float(a[0]), float(a[1]), [float(v) for v in a[2:6]], o))
    elif cmd == "typed": typed(series(src, float(a[0]), float(a[1]), [float(v) for v in a[2:6]], o))
    elif cmd == "vscroll":
        rows, per = vscroll(src, float(a[0]), float(a[1]), axis=o.get("dir", "y"))
        print("dy/khung (px @720x1280): " + " ".join(f"{v:.0f}" for v in per)); print(f"tích luỹ {rows[-1][2][0]:.0f} px, tốc độ cực đại {max(abs(v) for v in per):.0f} px/khung = {max(abs(v) for v in per) * FPS:.0f} px/s")
        ease_report(rows, "y", label=o.get("label", ""))
    elif cmd == "dwell": dwell(src, float(a[0]), float(a[1]), [float(v) for v in a[2:6]], float(o.get("thr", 0.5)))
    elif cmd == "holds": global_holds(ep, float(o.get("thr", 0.35)), float(o.get("min", 0.5)))
    elif cmd == "bursts": motion_bursts(ep, float(o.get("thr", 1.0)))
    elif cmd == "inkmap": inkmap(src)
    elif cmd == "measure-clip":
        res = measure_clip(cd); outp = o.get("out", os.path.join(cd, "tmp/measured.json")); os.makedirs(os.path.dirname(outp) or ".", exist_ok=True); json.dump(res, open(outp, "w"), ensure_ascii=False, indent=1); print("ghi", outp)
    elif cmd == "build-style":   # build-style --style out.json [--jobs DIR]: đo lại mọi clip (20261028-230040 + corp-sample-*) rồi gộp -> style.json
        jd = os.path.abspath(o.get("jobs", os.path.join(HERE, ".."))); dirs = [os.path.join(jd, "20261028-230040")] + sorted(os.path.join(jd, d) for d in os.listdir(jd) if d.startswith("corp-sample-"))
        for d in dirs:
            r = measure_clip(d); os.makedirs(os.path.join(d, "tmp"), exist_ok=True); json.dump(r, open(os.path.join(d, "tmp/measured.json"), "w"), ensure_ascii=False, indent=1); print("đo", d)
        sp = o.get("style", os.path.join(HERE, "../../presets/corporate-motion/style.json")); os.makedirs(os.path.dirname(sp), exist_ok=True)
        json.dump(merge_style([json.load(open(os.path.join(d, "tmp/measured.json"))) for d in dirs]), open(sp, "w"), ensure_ascii=False, indent=1); print("ghi", sp)
    elif cmd == "merge-style":   # merge-style clipdir1 clipdir2 ... --out style.json   (mỗi clip cần tmp/measured.json từ measure-clip)
        ms = [json.load(open(os.path.join(os.path.abspath(d), "tmp/measured.json"))) for d in a]; os.makedirs(os.path.dirname(o["out"]) or ".", exist_ok=True)
        json.dump(merge_style(ms), open(o["out"], "w"), ensure_ascii=False, indent=1); print("ghi", o["out"])
    elif cmd == "onset":
        rows = series(src, float(a[0]), float(a[1]), [float(v) for v in a[2:6]], o); mn = int(o.get("min", 200))
        print(next((f"t={t:.3f} area={ar}" for t, ar, b in rows if ar >= mn), "không thấy"))
    elif cmd == "ease":
        rows = series(src, float(a[0]), float(a[1]), [float(v) for v in a[2:6]], o); ax = o.get("axis", "y")
        if "pre" in o:   # đại lượng ngoài khung ở khung đầu: "t,giá trị" ngoại suy, chỉ để chuẩn hoá điểm xuất phát (ghi rõ khi báo cáo)
            pt, pv = [float(v) for v in o["pre"].split(",")]; rows = [(pt, 0, (pv, pv, pv, pv))] + rows[1:] if ax in ("x", "y", "cx", "cy", "x1", "y1") else rows
        ease_report(rows, ax, label=o.get("label", ""))
    elif cmd == "spread":
        for t, n, r in spread(src, float(a[0]), float(a[1]), [float(v) for v in a[2:6]], float(a[6]), float(a[7]), o): print(f"t={t:.3f} n={n}" + ("" if r is None else f" r_median {r[0]:.1f} r_p90 {r[1]:.1f}"))
    elif cmd == "changes":
        for t, d in changes(src, float(a[0]), float(a[1]), [float(v) for v in a[2:6]], float(o.get("thr", 0.3))): print(f"t={t:.3f} d={d:.2f}")
    elif cmd == "textrows":
        for r in textrows(src, float(a[0]), [float(v) for v in a[1:5]], float(a[5]) if len(a) > 5 else 70): print(json.dumps(r))
    elif cmd == "scan":
        for st, ln, c in scan(src, float(a[0]), a[1], int(a[2]), int(a[3]), int(a[4]), float(o.get("thr", 40))): print(f"start {st} len {ln} colour {c}")
    elif cmd == "corner": print(json.dumps(corner(src, float(a[0]), [float(v) for v in a[1:5]], a[5], o)))
    elif cmd == "shadow": print(json.dumps(shadow(src, float(a[0]), a[1], int(a[2]), int(a[3]), int(a[4]))))
    elif cmd == "energyprofile": energyprofile(ep, float(o.get("win", 1.0)))
    elif cmd == "rhythm": rhythm(cuts_p, ep)
    elif cmd == "transitions": transitions(src, cuts_p, ep)
    else: sys.exit("lệnh không có: " + cmd)


if __name__ == "__main__":
    main()
