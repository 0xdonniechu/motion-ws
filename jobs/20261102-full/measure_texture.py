# Đo kết cấu của s02, s03, s07 (mục 3 / textures). Chạy từ thư mục job, sau khi tách khung 30fps của từng cảnh:
#   ffmpeg -v error -ss 1.0  -t 1.75 -i source.mp4 -vf fps=30 frames/s02/f%02d.png     (s03: -ss 2.75 -t 1.35; s07: -ss 7.9 -t 1.3)
#   uvx --with numpy --with pillow --with scipy python -I measure_texture.py <lệnh> ...
# Lệnh:
#   wave  frames/s02 38 44   số hạt, cỡ, màu lõi; biên độ + pha sóng dy (kx 0.0170, ky 0.0055) và dx (ky 0.0130) bám theo từng hạt
#   ring  frames/s02         vòng tối halftone s02 f11–f24: cột trái (độ tối 0–9 theo hàng ô 46px) và khớp elip + hồ sơ bán kính theo từng khung
#   disc  frames/s07         s07: mép đĩa đen (trên/dưới/trái/phải), độ lệch chuẩn góc xoay ô theo khoảng cách tới mép đĩa, mép trên khối đen (mặt quét)
#   cluster frames/s03 24 41   s03: dịch chuyển dọc (NCC) của cột thẻ trái (x<230) và phải (x>860) giữa hai khung liền nhau; hàng trên/giữa-dưới
#   cols  frames/s03         s03 f13–f21: khoảng cột hạt (tự tương quan x), khoảng hàng; vệt dọc xám (thành phần cao ≥250px); lưới xám 78px (tâm ô − khe)
#   robot frames/s02 22 36   s02: cạnh ô trắng robot theo khung (tâm 804,1317); thẻ trên lệch (NCC) vùng x 20–420,y 470–760
#   fly   frames/s03 26 23   s03: bám 13 thẻ từ khung tham chiếu (26) ngược về f23 bằng matchTemplate (cần thêm opencv-python-headless): NCC, tâm, co, xoay; kèm cạnh logo và vòng bấm chuột (bỏ phiếu vòng tròn)
#   brk   frames/s02 tmp/rf2/s02   s02: độ phủ tối của tấm code và vùng thẻ f25–f38 (gốc | remake); phần đỏ trong ô robot
#   jit   frames/s07         s07 f1–f20: độ tập trung hướng cạnh R của 4θ -> biên độ xoay đều ±A (R = sin(4A)/(4A))
#   ripple frames/s03        s03: cỡ ô cam theo bán kính (tâm 540,950), độ đậm (r−b) tại tâm ô lưới 78px hàng y=1736, đỉnh phổ bán kính điểm ảnh cam nhạt
import sys, os, collections, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
BG = np.array([239, 236, 230]); Y0, Y1 = 1450, 1900  # dải dưới, không có thẻ/tem

def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(int)
def comps(img):
    reg = img[Y0:Y1]; lab, _ = ndi.label(np.abs(reg - BG).sum(2) > 60); out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        m = lab[sl] == i
        if m.sum() < 40: continue
        w = sl[1].stop - sl[1].start
        if w >= 26: continue
        cy, cx = ndi.center_of_mass(m); out.append((cx + sl[1].start, cy + sl[0].start + Y0, w))
    return np.array(out)
def klass(img, x, y):
    r, g, b = img[int(round(y)), int(round(x))]
    return "blue" if b > r + 60 else "orange" if (r > g + 70 and r > 150) else "dark" if r < 110 else "other"
def pairs(src, i):
    p, c = comps(load(f"{src}/f{i:02d}.png")), comps(load(f"{src}/f{i+1:02d}.png"))
    D = cdist(p[:, :2], c[:, :2]); r, cc = linear_sum_assignment(D); ok = D[r, cc] < 20
    return p[r[ok]], c[cc[ok], :2] - p[r[ok], :2]

def wave(src, a, b):
    img = load(f"{src}/f{a:02d}.png"); c = comps(img)
    k = collections.Counter(klass(img, x, y) for x, y, _ in c)
    print(f"f{a}: {len(c)} hạt trong dải y {Y0}-{Y1}, cỡ trung vị {np.median(c[:, 2]):.0f}px (10-90%: {np.percentile(c[:, 2], 10):.0f}-{np.percentile(c[:, 2], 90):.0f}), màu {dict(k)}")
    for i in range(a, b):
        p, d = pairs(src, i); x, y = p[:, 0], p[:, 1]; o = [f"f{i}"]
        for nm, v, (kx, ky) in (("dy", d[:, 1], (0.0170, 0.0055)), ("dx", d[:, 0], (0.0, 0.0130))):
            ph = kx * x + ky * y; A = np.c_[np.sin(ph), np.cos(ph)]; v = v - v.mean(); co, *_ = np.linalg.lstsq(A, v, rcond=None)
            o.append(f"{nm} amp {np.hypot(*co):.1f}px/khung pha {np.degrees(np.arctan2(co[1], co[0])):.0f}deg R2 {1 - ((v - A @ co) ** 2).sum() / (v ** 2).sum():.2f}")
        print("  ".join(o), f"trôi {d.mean(0).round(1)}")

def ring(src):
    from scipy.optimize import least_squares
    C = 46; NY, NX = 1920 // C, 1080 // C
    def cellmap(path):
        L = np.asarray(Image.open(path).convert("L")).astype(float); return L[:NY * C, :NX * C].reshape(NY, C, NX, C).mean((1, 3))
    yy, xx = np.mgrid[0:NY, 0:NX]; X = (xx + .5) * C; Y = (yy + .5) * C
    mask = (X < 40) | (X > 1040) | (Y > 1480) | ((Y < 500) & (X > 700))   # ô không bị thẻ/chữ che
    W = np.where(X < 40, 4.0, np.where(X > 1040, 1.0, 1.5))                  # cột trái là phép đo chuẩn
    RK = np.array([0, .4, .6, .75, .9, 1, 1.1, 1.25, 1.5, 1.9, 3.0])
    for f in range(11, 25):
        d = np.clip(1 - cellmap(f"{src}/f{f:02d}.png") / 232, 0, 1)         # độ tối trung bình ô+khe
        def model(p): return np.interp(np.hypot((X - 540) / p[1], (Y - p[0]) / p[2]), RK, p[3:])
        best = None
        for cy0 in (500, 800, 1000, 1300, 1600, 2000):
            for rx0 in (350, 600, 900, 1300):
                for k in (0.8, 1.2, 2.0):
                    p0 = np.r_[cy0, rx0, rx0 * k, np.full(len(RK), .5)]; lb = np.r_[200, 150, 150, np.zeros(len(RK))]; ub = np.r_[2400, 3000, 4500, np.full(len(RK), .95)]
                    try: r_ = least_squares(lambda p: ((model(p) - d) * W)[mask], np.clip(p0, lb + 1e-6, ub - 1e-6), bounds=(lb, ub), max_nfev=60)
                    except Exception: continue
                    if best is None or r_.cost < best.cost: best = r_
        p = best.x; m = model(p)
        print(f"f{f}: cy {p[0]:.0f} rx {p[1]:.0f} ry {p[2]:.0f} knots {np.round(p[3:], 2).tolist()}  RMS(mặt nạ) {np.sqrt(((m - d)[mask] ** 2).mean()):.3f}")
        print("   cột trái gốc:", "".join(str(min(9, int(v * 10))) for v in d[:, 0]), "\n   cột trái khớp:", "".join(str(min(9, int(v * 10))) for v in m[:, 0]))

def disc(src):
    P = 36
    RAD = {17: 28, 18: 126, 19: 210, 20: 305, 21: 423, 22: 490, 23: 525, 24: 561, 25: 606, 26: 646}
    for f in range(17, 31):
        L = np.asarray(Image.open(f"{src}/f{f:02d}.png").convert("L")).astype(float)
        col = np.convolve(L[:, 510:570].mean(1), np.ones(36) / 36, mode="same"); row = np.convolve(L[930:990, :].mean(0), np.ones(36) / 36, mode="same")
        def seg(k, c):
            if k[c] >= 100: return None
            a = c
            while a > 0 and k[a] < 100: a -= 1
            b = c
            while b < len(k) - 1 and k[b] < 100: b += 1
            return a, b
        print(f"f{f}: mép đĩa đen dọc x=540 (trên,dưới) {seg(col, 960)}  ngang y=960 (trái,phải) {seg(row, 540)}")
    print("độ lệch chuẩn góc xoay ô (độ) / cạnh ô (px) theo khoảng cách d = r − bán kính đĩa, ô 36px:")
    def rot_of(fg):
        ys, xs = np.where(fg)
        if len(xs) < 60: return None, None
        cx, cy = xs.mean(), ys.mean(); pad = np.pad(fg, 1); edge = fg & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        ey, ex = np.where(edge); th = np.arctan2(ey - cy, ex - cx); rr = np.hypot(ey - cy, ex - cx)
        ang = (np.degrees(np.angle((rr * np.exp(4j * th)).sum())) / 4) % 90
        return ((ang - 45) + 45) % 90 - 45, np.sqrt(len(xs))
    for f, rad in RAD.items():
        lum = np.asarray(Image.open(f"{src}/f{f:02d}.png").convert("RGB")).astype(float).mean(2); rows = {b: [] for b in range(5)}
        for j in range(10, 50):
            for i in range(30):
                x0, y0 = i * 36, j * 36
                if y0 + 36 > 1920 or x0 + 36 > 1080: continue
                d = np.hypot(x0 + 18 - 540, y0 + 18 - 960) - rad
                b = 0 if -120 <= d < -60 else 1 if -60 <= d < 0 else 2 if 0 <= d < 60 else 3 if 60 <= d < 120 else 4 if 120 <= d < 240 else None
                if b is None: continue
                r_, a_ = rot_of(lum[y0:y0 + 36, x0:x0 + 36] < 160)
                if r_ is not None: rows[b].append((r_, a_))
        print(f"f{f}:", ["n/a" if len(v) < 5 else "%.0f/%.0f" % (np.std([q[0] for q in v]), np.mean([q[1] for q in v])) for v in rows.values()], "(d: -120..-60, -60..0, 0..60, 60..120, 120..240)")
    print("mặt quét: hàng đầu tiên (từ y=560) có độ sáng làm mượt 72px < 110 suốt 120px, theo x = 100,300,540,780,980")
    for f in range(26, 36):
        L = np.asarray(Image.open(f"{src}/f{f:02d}.png").convert("L")).astype(float); out = []
        for x in (100, 300, 540, 780, 980):
            k = np.convolve(L[:, x - 30:x + 30].mean(1), np.ones(72) / 72, mode="same")
            out.append(next((y for y in range(560, 1800) if k[y] < 110 and (k[y:y + 120] < 110).all()), -1))
        print(f"f{f}:", out)

def ripple(src):
    from scipy import ndimage as ndi
    def orange(path):
        im = np.asarray(Image.open(path).convert("RGB")).astype(int); r, g, b = im[..., 0], im[..., 1], im[..., 2]
        m = ndi.binary_opening((r > 170) & (r - g > 60) & (g - b > 10) & (r - b > 90), iterations=1); lab, _ = ndi.label(m); out = []
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            mm = lab[sl] == i; h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
            if mm.sum() < 60 or w > 70 or h > 70 or abs(w - h) > 8: continue
            cy, cx = ndi.center_of_mass(mm); out.append((cx + sl[1].start, cy + sl[0].start, (w + h) / 2))
        return out
    print("cỡ ô cam theo bán kính (cột 60px từ 0), tâm (540,950)")
    for f in range(31, 42):
        c = orange(f"{src}/f{f:02d}.png")
        if len(c) < 5: continue
        P = np.array([(q[0], q[1]) for q in c]); w = np.array([q[2] for q in c]); r = np.hypot(P[:, 0] - 540, P[:, 1] - 950)
        print(f, len(c), "".join("%3d" % round(w[(r >= a) & (r < a + 60)].mean()) if ((r >= a) & (r < a + 60)).sum() >= 2 else "  ." for a in range(0, 1200, 60)))
    print("độ đậm (r−b) tại tâm ô lưới 78px (x=24.7+78i, y=1736):")
    for f in range(30, 42):
        im = np.asarray(Image.open(f"{src}/f{f:02d}.png").convert("RGB")).astype(int)
        v = [int(im[1736, int(24.7 + 78 * i), 0] - im[1736, int(24.7 + 78 * i), 2]) for i in range(14)]; print(f, "tb %.0f" % np.mean(v), v)
    yy, xx = np.mgrid[0:1920, 0:1080]; R = np.hypot(xx - 540, yy - 950).astype(int)
    print("đỉnh phổ bán kính của điểm ảnh cam nhạt (vòng dày):")
    for f in range(30, 41):
        im = np.asarray(Image.open(f"{src}/f{f:02d}.png").convert("RGB")).astype(int); r, g, b = im[..., 0], im[..., 1], im[..., 2]
        m = (r > 205) & ((r - b) > 45) & ((r - b) < 115) & (g > 130) & (g < 205)
        hb = np.bincount(R[m], minlength=1400)[:1300].astype(float).reshape(-1, 20).sum(1)
        print(f, [(i * 20 + 10, int(hb[i])) for i in range(1, len(hb) - 1) if hb[i] > hb[i - 1] and hb[i] >= hb[i + 1] and hb[i] > 1200][:8])

def _g(src, f): return np.asarray(Image.open(f"{src}/f{f:02d}.png").convert("L")).astype(float)

def _vshift(a, b, maxs=260):
    h = a.shape[0]; best = (0, -1)
    for sft in range(-maxs, maxs + 1):
        A, B = (a[:h - sft], b[sft:]) if sft >= 0 else (a[-sft:], b[:h + sft])
        if A.size < 3000: continue
        A = A - A.mean(); B = B - B.mean(); c = (A * B).sum() / (np.sqrt((A * A).sum() * (B * B).sum()) + 1e-9)
        if c > best[1]: best = (sft, c)
    return best

def cluster(src, a, b):
    for name, (x0, x1, y0, y1) in {"cột trái x0-230 y480-1180": (0, 230, 480, 1180), "cột phải x860-1080 y380-1180": (860, 1080, 380, 1180)}.items():
        out = []
        for f in range(a, b):
            sft, c = _vshift(_g(src, f)[y0:y1, x0:x1], _g(src, f + 1)[y0:y1, x0:x1]); out.append(f"{f}→{f+1}: {sft:+d} ({c:.2f})")
        print(name, "| ".join(out))

def cols(src):
    from scipy import ndimage as ndi
    for f in (13, 15, 17, 19, 21):
        img = load(f"{src}/f{f:02d}.png"); reg = img[1300:1900]; lab, _ = ndi.label(np.abs(reg - BG).sum(2) > 60); pts = []
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            m = lab[sl] == i; w = sl[1].stop - sl[1].start
            if 30 < m.sum() and w < 30: cy, cx = ndi.center_of_mass(m); pts.append((cx + sl[1].start, cy + sl[0].start + 1300))
        P = np.array(pts); h = np.bincount(np.clip(P[:, 0].astype(int), 0, 1079), minlength=1080).astype(float); h = np.convolve(h, np.ones(9) / 9, mode="same"); h -= h.mean()
        ac = np.array([(h[:-k] * h[k:]).sum() if k else (h * h).sum() for k in range(200)]) / (h * h).sum()
        pk = [k for k in range(20, 199) if ac[k] > ac[k - 1] and ac[k] >= ac[k + 1] and ac[k] > 0.15]
        dys = [q[1] - p[1] for p in pts for q in pts if abs(p[0] - q[0]) < 14 and 15 < q[1] - p[1] < 80]
        print(f"f{f}: {len(P)} hạt, khoảng cột (đỉnh tự tương quan x) {pk[:3]}px, khoảng hàng trung vị {np.median(dys):.0f}px")
    print("vệt dọc: thành phần cao >=250px, rộng 6-40px, y>700 (x0,x1,y0,y1,RGB)")
    from scipy import ndimage as ndi
    for f in range(17, 26):
        im = load(f"{src}/f{f:02d}.png"); L = im.mean(2); ch = im.max(2) - im.min(2)
        m = ((L > 110) & (L < 232) & (ch < 40)) | ((im[..., 0] - im[..., 2] > 25) & (L > 150) & (L < 235) & (im[..., 0] > 190)); m[:700] = False
        m = ndi.binary_opening(m, structure=np.ones((9, 3))); lab, _ = ndi.label(m); out = []
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            h_ = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
            if h_ >= 250 and 6 <= w <= 40: out.append((sl[1].start, sl[1].stop, sl[0].start, sl[0].stop, tuple(int(v) for v in im[sl][lab[sl] == i].mean(0))))
        print(f"f{f}:", sorted(out)[:8])
    print("lưới xám 78px: tâm ô − khe (độ sáng) ở các hàng y>1560")
    for f in range(20, 36):
        im = load(f"{src}/f{f:02d}.png").astype(float); cs, gs = [], []
        for j in range(20, 25):
            for i in range(14):
                x = int(24.7 + 78 * i); y = int(20.2 + 78 * j)
                if 1560 <= y <= 1900: cs.append(im[y - 3:y + 4, x - 3:x + 4].mean()); gs.append(im[min(1915, y + 39) - 3:min(1915, y + 39) + 4, min(1075, x + 39) - 3:min(1075, x + 39) + 4].mean())
        print(f"f{f}: {np.mean(gs) - np.mean(cs):.1f}", end="  ")
    print()

def robot(src, a, b):
    from scipy import ndimage as ndi
    for f in range(a, b):
        im = load(f"{src}/f{f:02d}.png")[1150:1520, 650:960]; w = im.min(2) >= 247; lab, n = ndi.label(ndi.binary_opening(w, iterations=2)); bb = None
        if n:
            sz = ndi.sum(w, lab, range(1, n + 1)); k = int(np.argmax(sz)) + 1; ys, xs = np.where(lab == k)
            if sz.max() > 800: bb = (int(xs.min()) + 650, int(xs.max()) + 650, int(ys.min()) + 1150, int(ys.max()) + 1150)
        print(f"f{f}: ô trắng robot bbox {bb}")
    print("thẻ trên: dịch (dx,dy) NCC vùng x20-420 y470-760 (cạnh 2px, tìm ±40)")
    box = (20, 470, 420, 760)
    for f in range(18, 30):
        A = _g(src, f)[470:760, 20:420][::2, ::2]; B = _g(src, f + 1)[470:760, 20:420][::2, ::2]; best = (0, 0, -1)
        for dy in range(-20, 21):
            for dx in range(-20, 21):
                h_, w_ = A.shape; ya0, ya1 = max(0, -dy), min(h_, h_ - dy); xa0, xa1 = max(0, -dx), min(w_, w_ - dx)
                P_ = A[ya0:ya1, xa0:xa1]; Q_ = B[ya0 + dy:ya1 + dy, xa0 + dx:xa1 + dx]
                if P_.size < 5000: continue
                P_ = P_ - P_.mean(); Q_ = Q_ - Q_.mean(); c = (P_ * Q_).sum() / (np.sqrt((P_ * P_).sum() * (Q_ * Q_).sum()) + 1e-9)
                if c > best[2]: best = (dx * 2, dy * 2, c)
        print(f"{f}→{f+1}: ({best[0]:+d},{best[1]:+d}) NCC {best[2]:.2f}", end="  ")
    print()

def jit(src):
    from scipy import ndimage as ndi
    def solve(R):
        lo, hi = 0.0, np.pi / 4
        for _ in range(40):
            m = (lo + hi) / 2; v = np.sin(4 * m) / (4 * m)
            if v > R: lo = m
            else: hi = m
        return np.degrees((lo + hi) / 2)
    for f in range(1, 21):
        lum = np.asarray(Image.open(f"{src}/f{f:02d}.png").convert("RGB")).astype(float).mean(2)[500:1700]
        sm = ndi.gaussian_filter(lum, 1.0); gx = ndi.sobel(sm, axis=1); gy = ndi.sobel(sm, axis=0); mag = np.hypot(gx, gy); m = mag > 120
        th = np.arctan2(gy[m], gx[m]); w = mag[m]; R = abs((w * np.exp(4j * th)).sum() / w.sum())
        print(f"f{f}: R {R:.2f} -> ±{solve(min(R, 0.999)):.0f}°")

def fly(src, ref, last):
    import cv2, re
    html = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes/s03/index.html")).read()
    tiles = re.findall(r'<div class="t \w" id="(t\d+)" style="left:(\d+)px;top:(\d+)px(?:;width:(\d+)px;height:(\d+)px)?', html)
    gray = lambda f: cv2.imread(f"{src}/f{f:02d}.png", cv2.IMREAD_GRAYSCALE)
    R = gray(ref)
    for tid, l, t, w, h in tiles:
        l, t = int(l), int(t); w = int(w) if w else 240; h = int(h) if h else 200; tpl = R[t:t + h, l:l + w]; out = []
        for f in range(last, ref):
            im = gray(f); best = (-1, 0, 0, 1, 0)
            for sc in (0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3):
                for rot in range(-40, 41, 8):
                    tp = cv2.warpAffine(tpl, cv2.getRotationMatrix2D((w / 2, h / 2), rot, sc), (w, h), borderValue=int(tpl.mean()))
                    cx_, cy_ = l + w / 2, t + h / 2; x0 = int(max(0, cx_ - w / 2 - 170)); y0 = int(max(0, cy_ - h / 2 - 170))
                    r = cv2.matchTemplate(im[y0:int(min(1920, cy_ + h / 2 + 170)), x0:int(min(1080, cx_ + w / 2 + 170))], tp, cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(r)
                    if mx > best[0]: best = (mx, loc[0] + x0 + w / 2, loc[1] + y0 + h / 2, sc, rot)
            out.append((f, round(best[0], 2), round(best[1] - (l + w / 2)), round(best[2] - (t + h / 2)), best[3], best[4]))
        print(tid, "(khung, NCC, dx, dy, co, xoay):", out)
    from scipy import ndimage as ndi
    print("logo (thành phần gần đen lớn nhất x200-880,y480-1200):")
    for f in range(last, ref + 4):
        L = _g(src, f); reg = ndi.binary_opening(L[480:1200, 200:880] < 45, iterations=4); lab, n = ndi.label(reg)
        if n:
            k = int(np.argmax(ndi.sum(reg, lab, range(1, n + 1)))) + 1; ys, xs = np.where(lab == k); print(f"f{f}: bbox x {xs.min() + 200}-{xs.max() + 200} y {ys.min() + 480}-{ys.max() + 480}")
    yy, xx = np.mgrid[0:1920, 0:1080]
    print("vòng bấm chuột: tâm (x,y) và bán kính tốt nhất (bỏ phiếu vòng tròn trên điểm ảnh cam r>170,g<125,b<90):")
    for f in range(20, 29):
        im = load(f"{src}/f{f:02d}.png"); m = (im[..., 0] > 170) & (im[..., 1] < 125) & (im[..., 2] < 90); ys, xs = np.where(m)
        if len(xs) > 60000: sel = np.random.RandomState(1).choice(len(xs), 60000, replace=False); ys, xs = ys[sel], xs[sel]
        best = (0, 0, 0, 0)
        for cx in range(300, 781, 40):
            for cy in range(500, 1501, 40):
                h_ = np.bincount((np.hypot(xs - cx, ys - cy) // 6).astype(int), minlength=200)[10:200]; k = int(np.argmax(h_))
                if h_[k] > best[0]: best = (int(h_[k]), cx, cy, (k + 10) * 6 + 3)
        print(f"f{f}: phiếu {best[0]} tâm ({best[1]},{best[2]}) bán kính {best[3]}")

def brk(src, rmk):
    for s_ in (src, rmk):
        print(s_)
        for f in range(25, 39):
            L = _g(s_, f); p = L[800:1000, 100:900]; c = L[480:700, 200:900]
            im = load(f"{s_}/f{f:02d}.png")[1150:1520, 650:960]; red = (im[..., 0] > 185) & (im[..., 1] < 120) & (im[..., 2] < 90)
            yy, xx = np.mgrid[0:370, 0:310]; inside = (abs(xx - 154) < 86) & (abs(yy - 167) < 86)
            print(f"f{f}: tấm code sáng TB {p.mean():.0f} tối {(p < 60).mean():.2f} | thẻ sáng TB {c.mean():.0f} tối {(c < 60).mean():.2f} | đỏ robot tổng {red.mean():.3f} trong ô {red[inside].mean():.3f}")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "wave": wave(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == "ring": ring(sys.argv[2])
    elif cmd == "disc": disc(sys.argv[2])
    elif cmd == "ripple": ripple(sys.argv[2])
    elif cmd == "cluster": cluster(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == "cols": cols(sys.argv[2])
    elif cmd == "robot": robot(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == "jit": jit(sys.argv[2])
    elif cmd == "fly": fly(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == "brk": brk(sys.argv[2], sys.argv[3])
    else: print(__doc__ if __doc__ else "dùng: wave|ring|disc|ripple <thư mục khung> ...")
