# Đo chi tiết còn thiếu của s01, s13, s16, s17 (mục 6 / details). Chạy từ thư mục job, sau compose.sh:
#   uvx --with numpy --with pillow --with scipy python -I -B measure_details.py <lệnh> ...
# Khung gốc 30fps (khung file f01 = đầu cảnh; t cảnh = (f−1)/30), tách bằng:
#   ffmpeg -v error -ss 33.0 -t 3.03 -i source.mp4 -vf fps=30 frames/s17/f%02d.png     (s01: -ss 0 -t 1.15 ; s13: -ss 21 -t 3.3 ; s16: -ss 30.4 -t 2.8)
# Lệnh:
#   energy sNN            năng lượng |khung(t)−khung(t−1)| từng khung, gốc | remake | tỉ lệ (270x480 -> 180x320 xám như motion.py)
#   where sNN f0 f1       năng lượng từng ô lưới 6x8 (cột x hàng) trong khoảng khung f0..f1 (1-based), gốc | remake | hụt: chỉ ra vùng thiếu chuyển động
#   arms frames/s17 [out.json]   s17: tay nhân vật gốc. Mỗi khung và mỗi bên: cổ tay W (băng xám cổ tay áo), bàn tay F (trọng tâm vùng da ngoài đầu quanh W),
#                         khuỷu E (giải hai đoạn S→E→W với độ dài cố định, chọn nghiệm xa đầu), góc vai/khuỷu/bàn tay (độ); đầu H (trọng tâm vùng da lớn nhất).
#                         Kiểm: độ phủ ống tay (điểm ảnh áo tối nằm ngoài thân trong bán kính 34 px quanh S–E–W)
#   armtab tmp/arms.json   s17: bảng từng khung cho scene (đầu lệch so với tư thế nghỉ; mỗi tay [Ex,Ey,Wx,Wy,Fx,Fy] hoặc 0 = tay buông/khuất): in ra dạng JS
#   box DIR a b x0 y0 x1 y1 R G B tol   hộp bao + diện tích của màu (R,G,B ±tol) trong vùng, từng khung a..b của thư mục khung (gốc: frames/sNN, remake: frames/sNN_r)
#   cover DIR a b          phủ tối (điểm ảnh < 60 sáng) của 5 mảnh 200x200 (góc TL, TR, giữa, BL, BR) từng khung a..b: đo nhịp chấm halftone đen của chuyển cảnh J16 (s17 f1–f14)
#   nem DIR a b [ref]      s13 (cần thêm --with opencv-python-headless): bám thẻ NÉM (chữ NÉM + 2 thanh xám, mẫu cắt từ khung gốc f73 ở (296..484, 428..552)) bằng matchTemplate chuẩn hoá,
#                         quét xoay −45..45° (bước 6) × tỉ lệ 0.7–1.3, vùng y 330–700: in NCC, tỉ lệ, góc (cv2: dương = ngược chiều kim đồng hồ; CSS rotate = −góc), tâm mẫu. DIR = frames/s13 (gốc) hoặc frames/s13_r (remake)
#   ring13 DIR a b         s13 f81–f90: vòng đỏ quanh logo Motion (tâm ~ (890,685)): bán kính trung vị và số điểm ảnh đỏ theo khung
#   throw DIR a b          s13: thẻ trắng "throw" (thành phần trắng lớn nhất, vùng x 0–520, y 1040–1560): lệch (dx, dy) so với lúc nghỉ (mép trái 35 / phải 304, đáy 1324) từng khung; dx lấy từ mép trái (hoặc mép phải nếu mép trái chạm 0), dy từ đáy
#   cells sNN f0 f1        s16: năng lượng trung bình của từng ô trong lưới 3×3 (x 28–362/372–706/716–1050, y 596–932/948–1284/1298–1632 trên 1080x1920) khoảng khung f0..f1: gốc | remake | tỉ lệ; kèm tổng thiếu (gốc − remake) tính trên cả cảnh
#   rows DIR a b           s16 ô (1,3): thành phần trắng lớn (hàng Tasks, mở 2 px, diện tích ≥ 2200) trong ô: x0, x1, y0, y1, lớp màu biểu tượng, diện tích; hàng chạm nhau gộp thành một thành phần (cao ~104 = 2 hàng, bước hàng ≈ 52 px) nên chưa tách được danh tính hàng
#   rg17 DIR a b           s17 f35–f46: ô dấu tích đỏ (vùng x 800–1075, y 880–1200: diện tích, hộp bao) và vòng đỏ khớp đường tròn (Kåsa, lặp loại ngoại lai; vùng x 200–860, y 880–1200): tâm, bán kính, số điểm ảnh
#   ry17 DIR a b           s17 f36–f44: các mảnh đỏ rời (tia) quanh tâm vòng (451,1010), bán kính 40–260: góc, bán kính trong–ngoài, điểm ảnh
#   rays DIR a b           s13 f82–f92: các mảnh đỏ rời (tia) quanh logo Motion (893,689), bán kính 70–185: góc trung bình, bán kính trong–ngoài, điểm ảnh
#   orb DIR a b            s16: hệ số zoom + dịch giữa hai khung liền nhau (ORB + similarity RANSAC) của từng ô trong lưới 3×3, khung a..b−1 (DIR = frames/s16; cần opencv-python-headless)
#   cellpop DIR a b        s16: viền trái/phải/trên/dưới của ô (2,1) (hàng y=1116, cột x=195) và các viền của ô giữa (2,2) trên hàng y=1116 từng khung a..b, dùng đo cỡ ô lúc phình (rộng nghỉ 329 px)
#   poster frames/s01     s01: khung 0–2 (poster) đứng yên? chênh khung 2→3 (cắt); vùng tối/cam của poster
#   letters frames/s01 a b  s01: hộp bao mặt nạ chữ tối (CHUYỂN) và cam (ĐỘNG) từng khung a..b
import sys, os, json, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
S = [0, 1.00, 2.75, 4.10, 6.00, 6.70, 7.90, 9.20, 13.00, 16.20, 18.70, 19.40, 21.00, 24.00, 28.40, 30.40, 33.00, 36.03]
W, H = 180, 320


def gray(path, a, d, w=W, h=H):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(d), "-i", path, "-vf", f"fps=30,scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.int16)


def scene_range(name):
    k = int(name[1:]); return S[k - 1], S[k] - S[k - 1]


def pair(name):
    a, d = scene_range(name)
    o = gray(os.path.join(HERE, "source.mp4"), a, d); r = gray(os.path.join(HERE, "preview/remake.mp4"), a, d)
    m = min(len(o), len(r)); return o[:m], r[:m]


def energy(name):
    o, r = pair(name); a, _ = scene_range(name)
    eo = np.abs(np.diff(o, axis=0)).mean(axis=(1, 2)); er = np.abs(np.diff(r, axis=0)).mean(axis=(1, 2))
    for i in range(len(eo)):
        print(f"f{i + 1:3d} t={a + i / 30:6.3f} o={eo[i]:6.2f} r={er[i]:6.2f} {er[i] / max(eo[i], 1e-6):5.2f}")
    print(f"tổng gốc {eo.mean():.2f} remake {er.mean():.2f} tỉ lệ {er.mean() / eo.mean():.2f}")


def where(name, f0, f1):
    o, r = pair(name)
    do = np.abs(np.diff(o, axis=0))[f0 - 1:f1]; dr = np.abs(np.diff(r, axis=0))[f0 - 1:f1]
    gx, gy = 6, 8; cw, ch = W // gx, H // gy
    print(f"{name} f{f0}..f{f1}: ô lưới {gx}x{gy} (mỗi ô {1080 // gx}x{1920 // gy} px); năng lượng trung bình gốc | remake")
    for j in range(gy):
        row = []
        for i in range(gx):
            eo = do[:, j * ch:(j + 1) * ch, i * cw:(i + 1) * cw].mean(); er = dr[:, j * ch:(j + 1) * ch, i * cw:(i + 1) * cw].mean()
            row.append(f"{eo:5.1f}|{er:5.1f}")
        print(f"y{j * 1920 // gy:4d}  " + "  ".join(row))
    tot = do.mean() * W * H; print(f"tổng gốc {do.mean():.2f} remake {dr.mean():.2f}")


# ---------------- s17: tay nhân vật ----------------
Y0 = 1050
SH = {"L": (632, 1795), "R": (930, 1795)}           # vai (đo từ chỗ ống tay rời thân, f28/f60/f91)
L1, L2 = 140, 70                                     # đoạn trên (vai→khuỷu), đoạn dưới (khuỷu→cổ tay); đo từ khuỷu ngoài của ống tay


def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(int)


def detect(img):
    """đầu H, cổ tay W{L,R}, bàn tay F{L,R} của một khung (toạ độ 1080x1920). None nếu không thấy."""
    im = img[Y0:]; R, G, B = im[..., 0], im[..., 1], im[..., 2]
    skin = (R > 215) & (R < 252) & (G > 190) & (G < 228) & (B > 165) & (B < 210) & (R - B > 25) & (R - B < 60)
    cuff = (abs(R - G) < 12) & (R > 55) & (R < 125) & (B - R >= 3) & (B - R <= 34)
    lab, n = ndi.label(skin)
    if n == 0: return None
    sizes = ndi.sum(skin, lab, range(1, n + 1)); h = int(np.argmax(sizes)) + 1
    if sizes[h - 1] < 30000: return None                       # đầu chưa hiện đủ (halftone / chuyển cảnh)
    hy, hx = ndi.center_of_mass(lab == h)
    out = {"H": (hx, hy + Y0), "W": {}, "F": {}}
    cl, cn = ndi.label(ndi.binary_closing(cuff, iterations=2)); cs = ndi.sum(cuff, cl, range(1, cn + 1))
    for i, s in enumerate(cs):
        if s < 100: continue
        y, x = ndi.center_of_mass(cl == i + 1)
        if abs(x - hx) < 120 and y > hy + 120: continue        # cổ áo/dây mũ cùng màu xám
        if y + Y0 > 1900 and (x < 20 or x > 1060): continue
        side = "L" if x < hx else "R"
        if side in out["W"]: continue
        out["W"][side] = (x, y + Y0)
    hands = [(x, y + Y0, s) for i, s in enumerate(sizes) if i + 1 != h and s >= 400
             for y, x in [ndi.center_of_mass(lab == i + 1)]]
    for side, (wx, wy) in out["W"].items():
        near = [p for p in hands if np.hypot(p[0] - wx, p[1] - wy) < 170 and (p[0] < hx) == (side == "L")]
        if near:
            ws = np.array([p[2] for p in near], float); out["F"][side] = (float(np.dot([p[0] for p in near], ws) / ws.sum()), float(np.dot([p[1] for p in near], ws) / ws.sum()))
    return out


def ik(side, w):
    """S cố định → khuỷu E sao cho |SE|=L1, |EW|=L2; chọn nghiệm xa đầu (ra ngoài). W ngoài tầm với thì kẹp về tầm."""
    s = np.array(SH[side], float); w = np.array(w, float); d = w - s; dist = np.hypot(*d)
    dist = min(max(dist, abs(L1 - L2) + 1), L1 + L2 - 1)
    a = (L1 ** 2 - L2 ** 2 + dist ** 2) / (2 * dist); hgt = np.sqrt(max(L1 ** 2 - a ** 2, 0))
    u = d / max(np.hypot(*d), 1e-6); p = s + u * a; n = np.array([-u[1], u[0]])
    c1, c2 = p + n * hgt, p - n * hgt
    out = (lambda e: e[0]) if side == "L" else (lambda e: -e[0])
    return c1 if out(c1) < out(c2) else c2


def ang(v): return float(np.degrees(np.arctan2(v[1], v[0])))


def arms(src, out=None):
    rows = []
    for f in range(1, 92):
        p = os.path.join(src, f"f{f:02d}.png")
        if not os.path.exists(p): continue
        d = detect(load(p)); rows.append((f, d))
    res = {}
    for f, d in rows:
        if d is None: print(f"f{f:02d} -"); continue
        rec = {"head": [round(d["H"][0], 1), round(d["H"][1], 1)]}
        line = f"f{f:02d} head ({d['H'][0]:.0f},{d['H'][1]:.0f})"
        for side in "LR":
            if side not in d["W"]: line += f" | {side} -"; continue
            wv = d["W"][side]; e = ik(side, wv); s = np.array(SH[side], float)
            a1 = ang(e - s); a2 = ang(np.array(wv) - e); fv = d["F"].get(side)
            a3 = ang(np.array(fv) - np.array(wv)) if fv else None
            rec[side] = {"W": [round(wv[0], 1), round(wv[1], 1)], "E": [round(float(e[0]), 1), round(float(e[1]), 1)],
                         "F": [round(fv[0], 1), round(fv[1], 1)] if fv else None, "a1": round(a1, 1), "a2": round(a2 - a1, 1), "a3": None if a3 is None else round(a3, 1)}
            line += f" | {side} W({wv[0]:.0f},{wv[1]:.0f}) E({e[0]:.0f},{e[1]:.0f}) vai {a1:6.1f}° khuỷu {((a2 - a1 + 180) % 360) - 180:6.1f}° tay " + ("-" if a3 is None else f"{a3:6.1f}°")
        res[f] = rec; print(line)
    if out: json.dump(res, open(out, "w"), indent=0); print("ghi", out)


REST = (766.0, 1574.0)                              # đầu ở tư thế nghỉ (f28–f37, f67–f91 gần như đứng yên)
SWING = {"L": ((485, 1781), (410, 1750)), "R": ((1068, 1744), (1068, 1744))}   # tay vung ngang (f22, f41, f62): W đo ở f62; F từ vùng da ở mép trái (f22/f41/f62 ~ (404–439, 1726–1784))
SWING_FRAMES = {"L": (22, 41, 62), "R": (41, 62)}  # khung có tay vung mà băng cổ tay bị nhoè/khuất nên chưa tự dò được (xem ảnh f22, f41)


def armtab(path):
    """bảng từng khung: pose rời rạc (gốc là hoạt hình đổi hình, không có khung chuyển) -> in mảng JS."""
    d = json.load(open(path)); head, A = [], {"L": [], "R": []}
    for f in range(1, 92):
        r = d.get(str(f))
        h = r["head"] if r else None
        head.append([0, 0] if h is None else [round(h[0] - REST[0]), round(h[1] - REST[1])])
        for side in "LR":
            e = None
            if r and side in r:
                q = r[side]; w = np.array(q["W"]); fv = np.array(q["F"]) if q["F"] else w + 130 * np.array([np.cos(np.radians(q["a3"] if q["a3"] is not None else -90)), np.sin(np.radians(q["a3"] if q["a3"] is not None else -90))])
                e = [q["E"][0], q["E"][1], w[0], w[1], fv[0], fv[1]]
            elif f in SWING_FRAMES[side]:
                w = np.array(SWING[side][0], float); fv = np.array(SWING[side][1], float); el = ik(side, w); e = [el[0], el[1], w[0], w[1], fv[0], fv[1]]
            A[side].append(0 if e is None or f < 12 else [round(float(v)) for v in e])
    print("const AVH =", json.dumps(head, separators=(",", ":")) + ";")
    for side in "LR": print(f"const ARM_{side} =", json.dumps(A[side], separators=(",", ":")) + ";")


def box(src, a, b, x0, y0, x1, y1, r, g, bl, tol):
    for i in range(a, b + 1):
        p = os.path.join(src, f"f{i:02d}.png")
        if not os.path.exists(p): continue
        im = load(p)[y0:y1, x0:x1]; m = (abs(im[..., 0] - r) <= tol) & (abs(im[..., 1] - g) <= tol) & (abs(im[..., 2] - bl) <= tol)
        ys, xs = np.nonzero(m)
        print(f"f{i:02d} diện tích {int(m.sum()):7d}" + (f" hộp x {xs.min() + x0}..{xs.max() + x0} y {ys.min() + y0}..{ys.max() + y0}" if len(xs) > 50 else ""))


def cover(src, a, b):
    P = [(0, 0), (880, 0), (440, 860), (0, 1720), (880, 1720)]
    for i in range(a, b + 1):
        im = load(os.path.join(src, f"f{i:02d}.png")); g = im.max(2)
        print(f"f{i:02d} " + " ".join(f"{(g[y:y + 200, x:x + 200] < 60).mean():5.2f}" for x, y in P))


def nem(src, a, b):
    import cv2
    def img(d, f): return cv2.imread(os.path.join(d, f"f{f:02d}.png"), cv2.IMREAD_GRAYSCALE)
    t0 = img(os.path.join(HERE, "frames/s13"), 73)[428:552, 296:484].astype(np.float32)

    def rot(t, ang, sc):
        h, w = t.shape; M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, sc)
        nw, nh = int(w * sc * 1.5) + 20, int(h * sc * 1.5) + 20; M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
        return cv2.warpAffine(t, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    for f in range(a, b + 1):
        G = img(src, f)[330:700].astype(np.float32); best = (-1,)
        for sc in (0.7, 0.85, 1.0, 1.15, 1.3):
            for ang in range(-45, 46, 6):
                t = rot(t0, ang, sc); h, w = t.shape; c = t[int(h * .2):int(h * .8), int(w * .2):int(w * .8)]
                if c.shape[0] >= G.shape[0] or c.shape[1] >= G.shape[1]: continue
                mx = cv2.minMaxLoc(cv2.matchTemplate(G, c, cv2.TM_CCOEFF_NORMED))
                if mx[1] > best[0]: best = (mx[1], sc, ang, mx[3][0] + c.shape[1] / 2, mx[3][1] + c.shape[0] / 2 + 330)
        print(f"f{f} ncc {best[0]:.2f} scale {best[1]} rot {best[2]} tâm ({best[3]:.0f},{best[4]:.0f})")


def ring13(src, a, b, cx=890, cy=685):
    """vòng đỏ quanh logo: bán kính đỉnh của biểu đồ bán kính (ô 3 px) = vòng mảnh; phần đỏ ngoài vòng +12 px = tia"""
    for f in range(a, b + 1):
        im = load(os.path.join(src, f"f{f:02d}.png")); R, G, B = im[..., 0], im[..., 1], im[..., 2]
        red = (R > 150) & (G < 120) & (B < 100) & (R - G > 70)
        ys, xs = np.nonzero(red[cy - 220:cy + 220, cx - 220:cx + 220]); xs = xs + cx - 220; ys = ys + cy - 220
        d = np.hypot(xs - cx, ys - cy); d = d[d > 55]
        if len(d) < 50: print(f"f{f} -"); continue
        h, e = np.histogram(d, bins=np.arange(50, 224, 3)); k = int(np.argmax(h)); r = (e[k] + e[k + 1]) / 2
        print(f"f{f} đỏ {len(d):5d} vòng r={r:5.1f} (đỉnh {int(h[k])} điểm ảnh) tia ngoài vòng {int((d > r + 12).sum())} điểm ảnh, xa nhất {d.max():5.1f}")


def throw(src, a, b):
    out = []
    for f in range(a, b + 1):
        g = load(os.path.join(src, f"f{f:02d}.png"))[1040:1560, 0:520]
        wh = ndi.binary_opening(g.min(2) > 235, iterations=3); lab, n = ndi.label(wh); best = None
        for i in range(1, n + 1):
            m = lab == i; ar = int(m.sum())
            if ar > 15000 and (best is None or ar > best[0]):
                ys, xs = np.nonzero(m); best = (ar, xs.min(), xs.max(), ys.max() + 1040)
        if best is None: out.append(None); print(f"f{f} -"); continue
        _, x0, x1, y1 = best
        dx = (x0 - 35) if x0 >= 3 else (x1 - 304); dy = y1 - 1324
        out.append([int(dx), int(dy)]); print(f"f{f} xmin {x0} xmax {x1} đáy {y1} -> dx {dx} dy {dy}")
    print("const THROW0 =", a, "; const THROWD =", json.dumps(out, separators=(",", ":")) + ";")


CELLX = [(28, 362), (372, 706), (716, 1050)]; CELLY = [(596, 932), (948, 1284), (1298, 1632)]


def cells(name, f0, f1):
    o, r = pair(name); do = np.abs(np.diff(o, axis=0)); dr = np.abs(np.diff(r, axis=0)); k = W / 1080.0
    print(f"{name} f{f0}..f{f1}: ô (hàng, cột)  gốc | remake | tỉ lệ | thiếu (gốc−remake) × diện tích ô / diện tích khung")
    for j, (ya, yb) in enumerate(CELLY):
        row = []
        for i, (xa, xb) in enumerate(CELLX):
            sl = (slice(f0 - 1, f1), slice(int(ya * k), int(yb * k)), slice(int(xa * k), int(xb * k)))
            eo = do[sl].mean(); er = dr[sl].mean(); row.append(f"{eo:5.1f}|{er:5.1f}|{er / max(eo, 1e-6):4.2f}|{(eo - er) * (xb - xa) * (yb - ya) / 1080 / 1920:5.2f}")
        print(f"hàng {j + 1}  " + "   ".join(row))


def rows(src, a, b):
    def cls(rgb):
        r, g, bb = rgb
        if r > 150 and g < 110 and bb < 80: return "cam"
        if bb > 150 and r < 110: return "xanh"
        if r > 100 and bb > 180 and g < 110: return "tim"
        if g > 110 and r < 80 and bb < 120: return "luc"
        if r > 190 and g > 130 and bb < 80: return "vang"
        return "?"
    for f in range(a, b + 1):
        im = load(os.path.join(src, f"f{f:02d}.png"))[601:927, 721:1045]
        lab, n = ndi.label(ndi.binary_opening(im.min(2) > 236, iterations=2)); out = []
        for i in range(1, n + 1):
            m = lab == i; ar = int(m.sum())
            if ar < 2200: continue
            ys, xs = np.nonzero(m); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
            if y0 < 80 or (x1 - x0) < 110: continue
            out.append((int(x0), int(x1), int(y0), int(y1), cls(im[int((y0 + y1) / 2), min(323, x0 + 24)]), ar))
        out.sort(key=lambda t: t[2]); print(f"f{f}", out)


def rg17(src, a, b):
    for f in range(a, b + 1):
        im = load(os.path.join(src, f"f{f:02d}.png")); R, G, B = im[..., 0], im[..., 1], im[..., 2]
        red = (R > 150) & (G < 120) & (B < 100) & (R - G > 70)
        c = red[880:1200, 800:1075]; ys, xs = np.nonzero(c)
        chk = (int(c.sum()), (int(xs.min() + 800), int(xs.max() + 800), int(ys.min() + 880), int(ys.max() + 880))) if len(xs) > 30 else (int(c.sum()), None)
        m = red[880:1200, 200:860]; ys, xs = np.nonzero(m); xs = xs + 200; ys = ys + 880; ring = None
        if len(xs) > 80:
            ok = np.ones(len(xs), bool)
            for _ in range(6):
                A = np.c_[2 * xs[ok], 2 * ys[ok], np.ones(ok.sum())]; bb = xs[ok] ** 2 + ys[ok] ** 2
                sol = np.linalg.lstsq(A, bb, rcond=None)[0]; cx, cy = sol[0], sol[1]; r = np.sqrt(sol[2] + cx * cx + cy * cy)
                dd = np.abs(np.hypot(xs - cx, ys - cy) - r); ok = dd < max(4, np.percentile(dd, 60))
            ring = (round(float(cx)), round(float(cy)), round(float(r)), int(ok.sum()), int(len(xs)))
        print(f"f{f} chk {chk} ring(cx,cy,r,inl,tổng) {ring}")


def _rays(src, a, b, cx, cy, r0, r1, region=None):
    for f in range(a, b + 1):
        im = load(os.path.join(src, f"f{f:02d}.png")); R, G, B = im[..., 0], im[..., 1], im[..., 2]
        red = (R > 150) & (G < 130) & (B < 110) & (R - G > 60)
        yy, xx = np.mgrid[0:1920, 0:1080]; d = np.hypot(xx - cx, yy - cy); m = red & (d > r0) & (d < r1)
        if region: m &= (yy > region[0]) & (yy < region[1]) & (xx < region[2])
        lab, n = ndi.label(ndi.binary_dilation(m, iterations=2 if region else 1)); out = []
        for i in range(1, n + 1):
            mm = (lab == i) & m; ar = int(mm.sum())
            if ar < (20 if region else 25): continue
            ys, xs = np.nonzero(mm); r = np.hypot(xs - cx, ys - cy)
            out.append((round(float(np.degrees(np.arctan2((ys - cy).mean(), (xs - cx).mean())))), int(r.min()), int(r.max()), ar))
        out.sort(); print(f, len(out), out[:22])


def ry17(src, a, b): _rays(src, a, b, 451, 1010, 40, 260, region=(800, 1230, 880))
def rays(src, a, b): _rays(src, a, b, 893, 689, 70, 185)


def orb(src, a, b):
    import cv2
    detector = cv2.ORB_create(1500, fastThreshold=5); bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    XS = [33, 377, 721]; YS = [601, 953, 1303]
    def rd(f): return cv2.imread(os.path.join(src, f"f{f:02d}.png"), cv2.IMREAD_GRAYSCALE)
    def tr(f, x, y):
        ka, da = detector.detectAndCompute(rd(f)[y:y + 326, x:x + 324], None); kb, db = detector.detectAndCompute(rd(f + 1)[y:y + 326, x:x + 324], None)
        if da is None or db is None or len(ka) < 8 or len(kb) < 8: return None
        m = bf.match(da, db)
        if len(m) < 8: return None
        pa = np.float32([ka[i.queryIdx].pt for i in m]); pb = np.float32([kb[i.trainIdx].pt for i in m])
        M, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=3)
        if M is None or inl.sum() < 12: return None
        return round(float(np.hypot(M[0, 0], M[1, 0])), 3), round(float(M[0, 2])), round(float(M[1, 2]))
    for j in range(3):
        for i in range(3): print(f"ô ({j + 1},{i + 1}) (zoom, dx, dy) f{a}→f{b}:", [tr(f, XS[i], YS[j]) for f in range(a, b)])


def cellpop(src, a, b):
    def runs(v, thr=70):
        m = v < thr; out = []; i = 0
        while i < len(m):
            if m[i]:
                j = i
                while j < len(m) and m[j]: j += 1
                out.append((i, j)); i = j
            else: i += 1
        return [(x, y) for x, y in out if 4 <= y - x <= 12]
    for f in range(a, b + 1):
        im = np.asarray(Image.open(os.path.join(src, f"f{f:02d}.png")).convert("L")).astype(int)
        r = runs(im[1116, :420]); c = runs(im[900:1330, 195])
        L = [(x + y) / 2 for x, y in r if x < 130]; Rr = [(x + y) / 2 for x, y in r if x >= 250]
        T = [(x + y) / 2 + 900 for x, y in c if x < 120]; B = [(x + y) / 2 + 900 for x, y in c if x >= 300]
        mid = [(x + y) / 2 for x, y in runs(im[1116, 340:760])]   # viền ô giữa (2,2): trái ≈ 375.5, phải ≈ 704.5 lúc nghỉ (cộng 340)
        print(f, "trái", L[:2], "phải", Rr[:2], "trên", T[:2], "dưới", B[:2], "| ô giữa viền", [m + 340 for m in mid][:6])


# ---------------- s01: poster + chữ ----------------
def poster(src):
    f = [load(os.path.join(src, f"f{i:02d}.png")).astype(np.int16) for i in range(1, 8)]
    for i in range(6): print(f"f{i + 1:02d}→f{i + 2:02d}: |Δ| trung bình {np.abs(f[i + 1] - f[i]).mean():6.2f}")
    # poster: cỡ chữ GSAP/MOTION ... đo hộp bao vùng tối của khung poster (f01)
    g = f[0]; dark = (g.max(2) < 70)
    ys, xs = np.nonzero(dark); print("poster f01 vùng tối: x", xs.min(), xs.max(), "y", ys.min(), ys.max(), "diện tích", int(dark.sum()))
    org = (g[..., 0] > 150) & (g[..., 1] < 110) & (g[..., 2] < 80); ys, xs = np.nonzero(org); print("poster f01 vùng cam: x", xs.min(), xs.max(), "y", ys.min(), ys.max(), "diện tích", int(org.sum()))


def letters(src, a, b):
    for i in range(a, b + 1):
        g = load(os.path.join(src, f"f{i:02d}.png"))[300:1050]; r, gg, bb = g[..., 0], g[..., 1], g[..., 2]
        dark = (r < 80) & (gg < 80) & (bb < 80); org = (r > 150) & (gg < 110) & (bb < 80) & (r - bb > 90)
        def box(m):
            ys, xs = np.nonzero(m)
            return (int(xs.min()), int(ys.min() + 300), int(xs.max()), int(ys.max() + 300), int(m.sum())) if len(xs) > 200 else None
        print(f"f{i:02d} tối {box(dark)} cam {box(org)}")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "energy": energy(sys.argv[2])
    elif c == "where": where(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "arms": arms(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif c == "box": box(sys.argv[2], *map(int, sys.argv[3:11]), *map(int, sys.argv[11:15]))
    elif c == "cover": cover(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "nem": nem(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "ring13": ring13(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "throw": throw(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "cells": cells(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "rows": rows(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "rg17": rg17(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "ry17": ry17(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "rays": rays(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "orb": orb(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "cellpop": cellpop(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == "armtab": armtab(sys.argv[2])
    elif c == "poster": poster(sys.argv[2])
    elif c == "letters": letters(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    else: sys.exit("lệnh?")
