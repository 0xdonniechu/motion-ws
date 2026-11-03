# Đo hình morph của s06 và s15 (mục 5 / morph). Chạy từ thư mục job; khung 30fps của gốc và của remake tách sẵn:
#   ffmpeg -v error -ss 6.7  -t 1.3 -i source.mp4 -vf fps=30 frames/s06/f%02d.png     (s15: -ss 28.4 -t 2.2 -> frames/s15)
#   ffmpeg -v error -ss 6.7  -t 1.3 -i preview/remake.mp4 -vf fps=30 tmp/rf/s06/f%02d.png    (cùng cách cho tmp/rf/s15)
#   uvx --with numpy --with pillow --with scipy python -I -B measure_morph.py <lệnh> ...
# Lệnh (src = thư mục khung: frames/s06, tmp/rf/s06, ...; khung file f01 = đầu cảnh, t cảnh = (f-1)/30):
#   energy sNN n         năng lượng |khung(t)-khung(t-1)| (xám 270x480) tách theo lớp: vùng cam / vùng nét tối / còn lại (tia, nền); gốc | remake
#   shape src x0 x1 f0 f1  hình cam lớn nhất (mở 9px bỏ nét mảnh): diện tích, bbox, tâm, rộng/cao theo từng khung, trong cột x0..x1
#   ghost src x f0 f1    cắt dọc theo cột x: các nét mảnh (bóng ma) phía trên mép hình cam: y, màu (D tối / O cam), độ dày
#   table src x0 x1 f0 f1 [u]  bảng JS [khung, tâm bbox x, y, rộng, cao] của hình cam theo khung (đưa thẳng vào scene); u = hợp mọi mảnh (s15)
#   chord src x0 x1 y f0 f1  hàng ngang y của hình cam: mép trái/phải (chỗ hình bị cắt bởi nửa trái 534px, đo cx từ dây cung ngắn ở đỉnh)
#   regions sNN n        năng lượng khung-khung theo 6 vùng (trái/phải x 3 dải dọc: 0-640, 640-1280, 1280-1920), gốc/remake: tìm chỗ remake thiếu chuyển động
#   box src x0 y0 x1 y1 f0 f1  điểm ảnh TỐI (tổng RGB < 200) trong khung chữ nhật: số điểm, bbox, tâm theo khung (đo ô logo GSAP / Motion: lúc hiện, cỡ)
#   logo src x0 y0 x1 y1 f0 f1  ô logo: thành phần tối (tổng RGB < 130, mở 21px) lớn nhất trong khung chữ nhật: số điểm, bbox, tâm, rộng/cao, độ tối trung bình của lõi theo khung
#   band src x0 y0 x1 y1 f0 f1  khối đen #141414 (tổng RGB < 90, mở 15px) lớn nhất trong khung: diện tích, bbox, tâm theo khung (thẻ "layout" tối nở ra ở cột phải s15)
#   grow src y f0 f1  bóng ma theo HÀNG ngang y (s06): khoảng cách từ mép trái / phải của hình cam tới các nét ma ở phía ngoài, D tối / O cam
#   rows src f0 f1 [Wn]  hàng bảng Tasks s15 (thẻ trắng trong cột phải, y 700-1500): với mỗi thành phần trắng lớn (mở 9px): x0, y0, rộng x cao nhìn thấy, cờ cắt (L = chạm mép trái cột, R = chạm mép phải 542) và mép trái THẬT suy ra khi hàng rộng Wn (mặc định 470): cắt trái -> phải - Wn, cắt phải -> x0, còn lại x0; hàng chạm nhau hợp thành một thành phần (cờ M, rộng > Wn)
#   reveal src x0 y0 x1 y1 fbefore fend f0 f1  tiến độ hiện của một vật (logo, chip) trong khung chữ nhật: 1 - |khung f - khung fend| / |khung fbefore - khung fend| (trung bình điểm ảnh), và bbox vùng khác khung fbefore (> 40 mức xám) theo từng khung
#   blur src x0 y0 x1 y1 fref f0 f1  độ nét vùng chữ (phương sai Laplace chuẩn hoá theo khung fref) và độ phủ điểm tối (< 300 tổng RGB): đo nhoè + mờ của chữ "layout"
#   gstack src x0 x1 f0 f1 [u]  bóng ma: ở mỗi khung quét 5 cột (tỉ lệ 0.3-0.7 bề rộng hình) phía trên mép hình cam và 2 hàng (tâm, +-150) hai bên: vị trí các nét mảnh (khoảng cách tới mép hình, bỏ viền thân <= 20px), lấy trung vị theo cột; D = nét tối, O = nét cam
#   iou sNN f0 f1 x0 x1  IoU của mặt nạ cam (mở 9px) giữa gốc và remake theo khung, kèm chênh diện tích và chênh tâm
#   gfit f0 f1           khớp chữ G (đa giác tham số, nghiêng) và sao (bán kính trong) vào mặt nạ cam gốc của s06 (IoU sau khi co giãn về bbox của gốc, nét 9px tính vào): in tham số tốt nhất
#   boil src x0 x1 f0 f1 chu vi hình cam theo hướng (36 hướng): độ lệch bán kính giữa hai khung liền nhau (rung nét vẽ tay), trung bình/lớn nhất
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(int)
def orange(img): return (img[..., 0] > 150) & (img[..., 0] - img[..., 2] > 100) & (img[..., 1] < 110)
def dark(img): return img.sum(2) < 230
UNION = False   # s15: hộp lời nhắc cắt hình cam thành nhiều mảnh -> lấy hợp mọi mảnh >= 4000 điểm trong y 480..1480 (lệnh thêm 'u' ở cuối)
def fill(img, x0=0, x1=1080, k=9):
    m = orange(img)[:, x0:x1]; m = ndi.binary_opening(m, np.ones((k, k)))
    lab, n = ndi.label(m)
    if not n: return m
    s = ndi.sum(m, lab, range(1, n + 1))
    if UNION:
        keep = [i + 1 for i, v in enumerate(s) if v >= 4000]; m2 = np.isin(lab, keep); m2[:480] = 0; m2[1480:] = 0; return m2
    return lab == (1 + int(np.argmax(s)))
def stats(m, x0=0):
    if not m.any(): return None
    ys, xs = np.nonzero(m); return dict(a=int(m.sum()), x0=int(xs.min()) + x0, x1=int(xs.max()) + x0, y0=int(ys.min()), y1=int(ys.max()), cx=float(xs.mean()) + x0, cy=float(ys.mean()))

def energy(sc, n):
    def gray(a): return a @ np.array([.299, .587, .114])
    def rs(p): return np.asarray(Image.open(p).convert("RGB").resize((270, 480), Image.BILINEAR)).astype(float)
    print("f  t | gốc: tổng vùng-cam nét-tối còn-lại | remake: cùng cột")
    for i in range(2, n):
        out = []
        for d in ("frames", "tmp/rf"):
            a, b = rs(f"{d}/{sc}/f{i-1:02d}.png"), rs(f"{d}/{sc}/f{i:02d}.png"); df = np.abs(gray(a) - gray(b))
            def cls(x): return ((x[..., 0] > 150) & (x[..., 1] < 120) & (x[..., 2] < 80), x.sum(2) < 260)
            oa, da = cls(a); ob, db = cls(b); om = oa | ob; dm = (da | db) & ~om; rest = ~(om | dm)
            out.append((df.mean(), (df * om).sum() / df.size, (df * dm).sum() / df.size, (df * rest).sum() / df.size))
        print(f"{i:2d} {(i-1)/30:.2f} | " + " ".join("%5.2f" % x for x in out[0]) + " | " + " ".join("%5.2f" % x for x in out[1]))

def shape(src, x0, x1, f0, f1):
    for f in range(f0, f1 + 1):
        s = stats(fill(load(f"{src}/f{f:02d}.png"), x0, x1), x0)
        print(f"f{f:02d} t{(f-1)/30:.2f} " + ("-" if not s else f"area {s['a']:7d} x {s['x0']}-{s['x1']} y {s['y0']}-{s['y1']} w {s['x1']-s['x0']} h {s['y1']-s['y0']} tâm ({s['cx']:.0f},{s['cy']:.0f})"))

def ghost(src, x, f0, f1):
    for f in range(f0, f1 + 1):
        img = load(f"{src}/f{f:02d}.png"); col = img[:, x - 2:x + 3].mean(1)
        fm = fill(img)[:, x]; ys = np.nonzero(fm)[0]; top = int(ys.min()) if len(ys) else 1500
        lines = []; y = 440
        while y < top - 4:
            c = col[y]; lum = c.sum()
            if lum < 420 and not (c[0] > 150 and c[2] > 150):
                y1 = y
                while y1 < top - 4 and col[y1].sum() < 420: y1 += 1
                cc = col[(y + y1) // 2]; lines.append(("O" if cc[0] - cc[2] > 80 else "D", y, y1 - y)); y = y1
            y += 1
        print(f"f{f:02d} đỉnh {top}  " + " ".join(f"{k}{top-y0}({w})" for k, y0, w in lines))

def table(src, x0, x1, f0, f1):
    rows = []
    for f in range(f0, f1 + 1):
        s = stats(fill(load(f"{src}/f{f:02d}.png"), x0, x1), x0)
        if s: rows.append(f"[{f},{(s['x0']+s['x1'])/2:.0f},{(s['y0']+s['y1'])/2:.0f},{s['x1']-s['x0']},{s['y1']-s['y0']}]")
    print(",".join(rows))

def chord(src, x0, x1, y, f0, f1):
    for f in range(f0, f1 + 1):
        r = fill(load(f"{src}/f{f:02d}.png"), x0, x1)[y]; xs = np.nonzero(r)[0]
        print(f"f{f:02d} " + ("-" if not len(xs) else f"y{y}: x {xs.min()+x0}-{xs.max()+x0} dây {xs.max()-xs.min()} tâm {(xs.max()+xs.min())/2+x0:.0f}"))

def regions(sc, n):
    def g(p): return np.asarray(Image.open(p).convert("L").resize((270, 480))).astype(float)
    print("f  t   | trái trên | trái giữa | trái dưới | phải trên | phải giữa | phải dưới  (gốc/remake)")
    for i in range(2, n):
        d = [np.abs(g(f"{dd}/{sc}/f{i:02d}.png") - g(f"{dd}/{sc}/f{i-1:02d}.png")) for dd in ("frames", "tmp/rf")]
        def blk(a): return [a[y0:y1, x0:x1].mean() for x0, x1 in ((0, 133), (135, 270)) for y0, y1 in ((0, 160), (160, 320), (320, 480))]
        o, r = blk(d[0]), blk(d[1]); L = [o[0], o[1], o[2], o[3], o[4], o[5]]
        print(f"{i:2d} {(i-1)/30:.2f} | " + " | ".join(f"{L[k]:4.1f}/{r[k]:4.1f}" for k in (0, 1, 2, 3, 4, 5)))

def box(src, x0, y0, x1, y1, f0, f1):
    for f in range(f0, f1 + 1):
        a = load(f"{src}/f{f:02d}.png")[y0:y1, x0:x1]; m = a.sum(2) < 200
        if m.sum() < 30: print(f"f{f:02d} t{(f-1)/30:.2f} -"); continue
        ys, xs = np.nonzero(m); print(f"f{f:02d} t{(f-1)/30:.2f} n {int(m.sum()):6d} x {xs.min()+x0}-{xs.max()+x0} y {ys.min()+y0}-{ys.max()+y0} w {xs.max()-xs.min()} h {ys.max()-ys.min()} tâm ({xs.mean()+x0:.0f},{ys.mean()+y0:.0f})")

def logo(src, x0, y0, x1, y1, f0, f1):
    for f in range(f0, f1 + 1):
        a = load(f"{src}/f{f:02d}.png")[y0:y1, x0:x1]; m = ndi.binary_opening(a.sum(2) < 130, np.ones((21, 21)))
        lab, n = ndi.label(m)
        if not n: print(f"f{f:02d} t{(f-1)/30:.2f} -  (tối nhất {int(a.sum(2).min())})"); continue
        k = 1 + int(np.argmax(ndi.sum(m, lab, range(1, n + 1)))); ys, xs = np.nonzero(lab == k)
        print(f"f{f:02d} t{(f-1)/30:.2f} n {len(ys):6d} x {xs.min()+x0}-{xs.max()+x0} y {ys.min()+y0}-{ys.max()+y0} w {xs.max()-xs.min()} h {ys.max()-ys.min()} tâm ({xs.mean()+x0:.0f},{ys.mean()+y0:.0f}) tối nhất {int(a.sum(2).min())}")

def band(src, x0, y0, x1, y1, f0, f1):
    for f in range(f0, f1 + 1):
        a = load(f"{src}/f{f:02d}.png")[y0:y1, x0:x1]; m = ndi.binary_opening(a.sum(2) < 90, np.ones((15, 15))); lab, n = ndi.label(m)
        if not n: print(f"f{f:02d} t{(f-1)/30:.2f} -"); continue
        k = 1 + int(np.argmax(ndi.sum(m, lab, range(1, n + 1)))); ys, xs = np.nonzero(lab == k)
        print(f"f{f:02d} t{(f-1)/30:.2f} n {len(ys):6d} x {xs.min()+x0}-{xs.max()+x0} y {ys.min()+y0}-{ys.max()+y0} w {xs.max()-xs.min()} h {ys.max()-ys.min()}")

def grow(src, y, f0, f1):
    for f in range(f0, f1 + 1):
        img = load(f"{src}/f{f:02d}.png"); m = fill(img); xs = np.nonzero(m[y])[0]
        if not len(xs): print(f"f{f:02d} y{y}: không có hình"); continue
        l, r = int(xs.min()), int(xs.max()); row = img[y]
        left = [(l - x, c) for x, _, c in _runs(row[:l - 12][::-1], 0) for x in [int(x)]]
        right = [(x, c) for x, _, c in _runs(row[r + 12:], 0) for x in [int(x)]]
        print(f"f{f:02d} y{y}: mép trái {l} phải {r} | trái: " + " ".join(f"{c}{d+12}" for d, c in left[:6]) + " | phải: " + " ".join(f"{c}{d+12}" for d, c in right[:6]))

def rows(src, f0, f1, Wn=470):
    for f in range(f0, f1 + 1):
        a = load(f"{src}/f{f:02d}.png")[700:1500, 538:1080]; m = ndi.binary_opening(a.min(2) > 235, np.ones((9, 9))); lab, n = ndi.label(m); out = []
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            if (lab[sl] == i).sum() < 5000: continue
            x0, x1 = sl[1].start, sl[1].stop; y0 = sl[0].start + 700; w = x1 - x0; h = sl[0].stop - sl[0].start
            if w > Wn + 20: flag, L = "M", x0
            elif x0 <= 12: flag, L = "L", x1 - Wn
            elif x1 >= 530: flag, L = "R", x0
            else: flag, L = "-", x0
            if h < 100 or h > 135: flag += "?"   # không phải một hàng nguyên (bị hộp lời nhắc/thẻ che hoặc là thẻ khác)
            out.append(f"{flag}[x {x0}-{x1} y {y0} h {h} L {L}]")
        print(f"f{f:02d} " + " ".join(out))

def reveal(src, x0, y0, x1, y1, fb, fe, f0, f1):
    def g(f): return load(f"{src}/f{f:02d}.png")[y0:y1, x0:x1].astype(float)
    B, E = g(fb), g(fe); d0 = np.abs(B - E).mean()
    for f in range(f0, f1 + 1):
        A = g(f); p = 1 - np.abs(A - E).mean() / max(d0, 1e-6); m = np.abs(A - B).max(2) > 40
        ys, xs = np.nonzero(m)
        print(f"f{f:02d} t{(f-1)/30:.2f} tiến độ {p:5.2f} " + (f"bbox x {xs.min()+x0}-{xs.max()+x0} y {ys.min()+y0}-{ys.max()+y0} ({xs.max()-xs.min()}x{ys.max()-ys.min()})" if len(xs) > 200 else "(không đổi)"))

def blur(src, x0, y0, x1, y1, fr, f0, f1):
    def lap(f):
        a = load(f"{src}/f{f:02d}.png")[y0:y1, x0:x1].mean(2); L = a[1:-1, 1:-1] * 4 - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]
        return L.var(), (a < 100).mean()
    v0 = lap(fr)[0]
    for f in range(f0, f1 + 1):
        v, d = lap(f); print(f"f{f:02d} t{(f-1)/30:.2f} độ nét {v/v0:5.2f} độ phủ tối {d*100:5.1f}%")

def _runs(line, lim, ymin=0):
    # các đoạn nét mảnh (tối hoặc cam) dọc theo mảng điểm RGB `line` (từ xa tới gần mép hình); trả [(vị trí giữa, độ dày, màu)]
    out = []; i = 0; n = len(line)
    while i < n:
        c = line[i]
        if i >= ymin and c.sum() < 420 and not (c[0] > 150 and c[2] > 150):
            j = i
            while j < n and line[j].sum() < 420: j += 1
            m = line[(i + j) // 2]; out.append(((i + j) / 2, j - i, "O" if m[0] - m[2] > 80 else "D")); i = j
        i += 1
    return out
def gstack(src, x0, x1, f0, f1):
    for f in range(f0, f1 + 1):
        img = load(f"{src}/f{f:02d}.png"); m = fill(img, x0, x1); s = stats(m, x0)
        if not s: print(f"f{f:02d} -"); continue
        res = []; w = s["x1"] - s["x0"]
        for fr in (0.3, 0.4, 0.5, 0.6, 0.7):
            x = int(s["x0"] + fr * w); ys = np.nonzero(m[:, x - x0])[0]
            if not len(ys): continue
            top = int(ys.min()); col = img[:, x - 2:x + 3].mean(1)[:top - 20]
            res.append([(top - y, th, c) for y, th, c in _runs(col, 0) if top - y > 20 and y >= 440 and th <= 12])
        k = min(map(len, res)) if res else 0
        txt = " ".join(f"{np.median([r[::-1][j][0] for r in res]):.0f}{res[0][::-1][j][2]}" for j in range(k)) if k else "(không nét)"
        print(f"f{f:02d} số nét theo cột {[len(r) for r in res]} -> trung vị từ gần mép: {txt}")

def iou(sc, f0, f1, x0, x1):
    print("f  t  IoU  diện tích gốc/remake  chênh tâm (dx,dy)")
    for f in range(f0, f1 + 1):
        a = fill(load(f"frames/{sc}/f{f:02d}.png"), x0, x1); b = fill(load(f"tmp/rf/{sc}/f{f:02d}.png"), x0, x1)
        sa, sb = stats(a, x0), stats(b, x0)
        u = (a | b).sum(); i = (a & b).sum() / u if u else 1.0
        print(f"{f:02d} {(f-1)/30:.2f} {i:.2f}  {sa['a'] if sa else 0:7d}/{sb['a'] if sb else 0:7d}  " + (f"({sb['cx']-sa['cx']:+.0f},{sb['cy']-sa['cy']:+.0f})" if sa and sb else ""))

def boil(src, x0, x1, f0, f1):
    ang = np.linspace(0, 2 * np.pi, 36, endpoint=False); prev = None
    for f in range(f0, f1 + 1):
        m = fill(load(f"{src}/f{f:02d}.png"), x0, x1); s = stats(m, 0)
        if not s: prev = None; continue
        cx, cy = s["cx"], s["cy"]; r = []
        for a in ang:
            rr = np.arange(0, 1200); xx = (cx + rr * np.cos(a)).astype(int); yy = (cy + rr * np.sin(a)).astype(int)
            ok = (xx >= 0) & (xx < m.shape[1]) & (yy >= 0) & (yy < m.shape[0]); v = m[yy[ok], xx[ok]]; r.append(rr[ok][v].max() if v.any() else 0)
        r = np.array(r, float)
        print(f"f{f:02d} " + (f"rung {np.abs(r - prev).mean():5.1f} lớn nhất {np.abs(r - prev).max():5.0f}  bán kính TB {r.mean():5.0f}" if prev is not None else "-")); prev = r

def rad(d): return d * np.pi / 180
def g_poly(q):
    a, b, ai, bi, th, xb, yb, te, sh = q                   # ngoài (a,b), trong (ai,bi), góc bậc thang th, x bậc xb, y mép trên bậc yb, góc đầu mút te, độ nghiêng sh
    G = []
    for p in np.arange(-90, te + 1e-6, 2): G.append([a * np.cos(rad(p)), b * np.sin(rad(p))])
    for p in np.arange(te, -336 - 1e-6, -3): G.append([ai * np.cos(rad(p)), bi * np.sin(rad(p))])
    iy = bi * np.sin(rad(th)); G += [[ai * np.cos(rad(th)), iy], [xb, iy], [xb, yb], [a * 0.985, yb]]
    for p in np.arange(-2, 268 + 1e-6, 3): G.append([a * np.cos(rad(p)), b * np.sin(rad(p))])
    return np.array([[x - sh * y, y] for x, y in G])
def star_poly(R, r, dy):
    return np.array([[(R if i % 2 == 0 else r) * np.cos(rad(i * 36 - 90)) + (i % 3) * 4, (R if i % 2 == 0 else r) * np.sin(rad(i * 36 - 90)) + dy + ((i * 7) % 5) * 3] for i in range(10)])
def to_bbox(P, m):                                         # co giãn bất đẳng hướng đa giác về bbox của mặt nạ m
    ys, xs = np.nonzero(m); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    mn, mx = P.min(0), P.max(0); return (P - mn) / (mx - mn) * [x1 - x0, y1 - y0] + [x0, y0]
def raster(P, shp):
    from PIL import ImageDraw
    im = Image.new("L", (shp[1], shp[0]), 0); ImageDraw.Draw(im).polygon([tuple(p) for p in P], fill=1); return np.asarray(im).astype(bool)
def gfit(f0, f1):
    from scipy.optimize import minimize
    tg = [ndi.binary_dilation(fill(load(f"frames/s06/f{f:02d}.png")), iterations=5) for f in range(f0, f1 + 1)]
    def loss(q, which):
        try: P = g_poly(q) if which == "G" else star_poly(*q)
        except Exception: return 1
        v = 0
        for m in tg:
            r = raster(to_bbox(P, m), m.shape); v += 1 - (r & m).sum() / (r | m).sum()
        return v / len(tg)
    which = "G" if f0 >= 30 else "star"
    x0 = [405.5, 372.7, 167, 206.6, 30, -40, -11.6, -27, 0.224] if which == "G" else [450, 215, 40]   # G: khởi đầu từ lần khớp 1 (xb 20 -> -40 để thoát cực trị)
    print(which, "IoU trước", 1 - loss(x0, which))
    best = minimize(loss, x0, args=(which,), method="Nelder-Mead", options=dict(maxiter=500 if which == "G" else 200, xatol=.5, fatol=1e-4))
    print("IoU sau", 1 - best.fun, "tham số", np.round(best.x, 3).tolist())

if __name__ == "__main__":
    c, a = sys.argv[1], sys.argv[2:]
    if a and a[-1] == "u": UNION = True; a = a[:-1]
    {"energy": lambda: energy(a[0], int(a[1])), "shape": lambda: shape(a[0], *map(int, a[1:5])), "ghost": lambda: ghost(a[0], *map(int, a[1:4])),
     "table": lambda: table(a[0], *map(int, a[1:5])), "chord": lambda: chord(a[0], *map(int, a[1:7])), "gfit": lambda: gfit(*map(int, a[:2])), "reveal": lambda: reveal(a[0], *map(int, a[1:9])), "blur": lambda: blur(a[0], *map(int, a[1:8])), "rows": lambda: rows(a[0], int(a[1]), int(a[2]), *(int(x) for x in a[3:4])), "grow": lambda: grow(a[0], *map(int, a[1:4])), "band": lambda: band(a[0], *map(int, a[1:7])), "logo": lambda: logo(a[0], *map(int, a[1:7])), "box": lambda: box(a[0], *map(int, a[1:7])), "regions": lambda: regions(a[0], int(a[1])), "gstack": lambda: gstack(a[0], *map(int, a[1:5])), "iou": lambda: iou(a[0], *map(int, a[1:5])), "boil": lambda: boil(a[0], *map(int, a[1:5]))}[c]()
