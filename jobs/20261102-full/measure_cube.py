# Đo hộp 3D của s08 / s09 (mục 4 / cubes): khớp tư thế hộp (tịnh tiến + xoay) và camera phối cảnh theo từng khung 30fps.
# Chạy từ thư mục job, sau khi tách khung 30fps của gốc:
#   ffmpeg -v error -ss 9.2 -t 4.4 -i source.mp4 -vf fps=30 frames/s08/f%03d.png      (f001 = đầu cảnh; t cảnh = (f-1)/30; s08 có post 0.6s nên lấy 4.4s)
#   uvx --with numpy --with opencv-python-headless --with scipy python -I measure_cube.py <lệnh> ...
# Lệnh (thứ tự đã dùng cho s08; mọi lệnh in số, không sửa scene):
#   cam    frames/s08                    khớp chung trên 9 khung (f36..f108): cạnh hộp hy,hz (hx=300), khoảng cách camera P; tâm phối cảnh cố định (540,960); ghi cube_cam.json
#   track  frames/s08 out.json           bám tư thế (x,y,z,rx,ry,rz) f30..f132 từ f60 (tiến, rồi lùi); mất mát hằng-màu từng mặt; ry bám liên tục nên giữ đúng thứ tự mặt SCROLL->SCRUB->GSAP->PIN
#   back   frames/s08 out.json 29 16     bám lùi f29..f16 (giai đoạn ráp, nắp còn hở)
#   tail   / tail2 frames/s08 out.json 113 128   bám đoạn hộp bay lên + phóng to (13.1-13.6s): ROI cả khung; tail2 dùng IoU riêng từng mặt cam (mặt đáy xám không bị phạt)
#   overlay frames/s08 out.json f1 f2 .. ghi tmp/cube_overlay.jpg: khung gốc + hình chiếu hộp (xanh: mặt bên, tím: nắp/đáy) để kiểm bằng mắt
#   shade  frames/s08 out.json           màu phẳng từng mặt theo pháp tuyến camera: hồi quy ánh sáng cho sai số chuẩn 16 mức, còn màu theo MẶT thì cố định tuyệt đối (xem SPEC mục 4)
#   jit    frames/s08 9                  nhiễu xoay ô halftone của #cover ở đầu s08 (±A theo khung)
#   shadow frames/s08 20 117 4           bbox lõi tối của bóng elip theo khung
#   tail3  frames/s08 out.json 115 131   bám lại f115..f131 bằng IoU mặt trước/mặt bên + cạnh đáy mặt trước (loss_front); sau đó chỉnh y theo cạnh đáy đo được:
#   closeloop frames/s08 frames/r08 out.json 112 131   sau khi dựng: so cạnh đáy/trái/phải của mặt trước giữa gốc và remake (cùng hàm đo) rồi dời (x,y,z) cho khớp; lặp tới khi chênh <= ~10 px
#   ybottom frames/s08 out.json 112 114 | 115 116 interp | 129 131 hold   (mất mát null = chỉnh theo số đo: f112-f114 giữ tư thế chỉ giải y; f115-f116 tự khớp thất bại nên nội suy giữa f114 và f117 rồi giải y; f129-f131 giữ tư thế f128 rồi giải y)
#   Thứ tự đã chạy cho cube_track_s08.json: cam, track (f60 tiến/lùi), back 29 16, tail2 113 128, tail3 115 131, ybottom 112 114, ybottom 115 116 interp, ybottom 129 131 hold. f132 không có số đo (hộp rời khung): `export` ngoại suy.
#   export out.json                      in bảng CP (t, x, y, z, rx, ry, rz; làm trơn 3 điểm) dán vào scene
# Mô hình (đúng với CSS):  p_cam = T + Rz(rz)·Rx(rx)·Ry(ry)·p;  màn hình = (ox,oy) + (p_cam.x, p_cam.y)·P/(P − p_cam.z);  y xuống, z về phía người xem.
import sys, os, json, numpy as np, cv2
from scipy.optimize import minimize

W, H, D = 540, 960, 2      # khung đo ở nửa độ phân giải
CAM = dict(P=1400.0, ox=540.0, oy=960.0, hx=300.0, hy=250.0, hz=240.0)   # ghi đè bằng kết quả `cam` (xem SPEC mục 4)
if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cube_cam.json")):
    CAM.update(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cube_cam.json"))))

# mặt: tên, pháp tuyến (trong hệ hộp), 4 đỉnh theo chỉ số (±1,±1,±1) nhân nửa cạnh
FACES = {"F": ((0, 0, 1)), "B": ((0, 0, -1)), "R": ((1, 0, 0)), "L": ((-1, 0, 0)), "T": ((0, -1, 0)), "U": ((0, 1, 0))}
def face_quads():
    q = {}
    for n, nv in FACES.items():
        nv = np.array(nv); a = np.argmax(np.abs(nv)); u, v = [i for i in range(3) if i != a]
        pts = []
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = np.zeros(3); p[a] = nv[a]; p[u] = su; p[v] = sv; pts.append(p)
        q[n] = np.array(pts)
    return q
QUADS = face_quads()

def rot(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]); Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]); Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Rx @ Ry

def project(q, cam=CAM):
    """q = [x,y,z,rx,ry,rz (độ)] -> {mặt: (4 đỉnh màn hình nửa độ phân giải, pháp tuyến camera)} chỉ mặt quay về camera"""
    R = rot(*np.radians(q[3:6])); T = np.array(q[:3]); h = np.array([cam["hx"], cam["hy"], cam["hz"]])
    out = {}
    for n, quad in QUADS.items():
        pc = (quad * h) @ R.T + T; s = cam["P"] / (cam["P"] - pc[:, 2])
        sc = np.c_[cam["ox"] + pc[:, 0] * s, cam["oy"] + pc[:, 1] * s] / D
        nc = R @ np.array(FACES[n]); cen = pc.mean(0)
        if np.dot(nc, np.array([0, 0, cam["P"]]) - cen) > 0: out[n] = (sc, nc)
    return out

def load(src, f):
    im = cv2.imread(f"{src}/f{f:03d}.png"); return cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)[:, :, ::-1].astype(np.int16)

def classes(img, f):
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    org = (r > 70) & (r < 215) & (g > 0.16 * r) & (g < 0.44 * r) & (b < (0.10 * r + 2 if f < 112 else 0.13 * r + 3))
    wht = img.min(2) >= 245
    drk = img.max(2) < 62
    drk &= cv2.dilate((org | wht).astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool)   # viền/băng keo sát mặt cam/trắng (không tính bóng, chấm, chữ lớn)
    roi = np.zeros((H, W), bool); roi[300:780] = True
    if f >= 112: roi[:] = True            # hộp phóng to bay lên khỏi khung (post của s08): lấy cả khung
    if 60 <= f < 112:                     # nhãn lớp (pill) che hộp từ ~2s
        for c in (298, 400, 499, 598, 700): roi[c - 28:c + 28, :130] = False
    return org & roi, wht & roi, drk & roi, roi, r.astype(np.float32)

def loss(q, cls, cam=CAM, detail=False):
    """Mất mát hằng-màu: mỗi mặt nhìn thấy phải phủ vùng cam MỘT sắc (|r - trung vị| < 14) hoặc, với mặt nắp/đáy, vùng trắng; vùng cam ngoài hình chiếu bị phạt."""
    org, wht, drk, roi, R = cls
    fs = project(q, cam)
    if not fs: return 1e3
    A = B = C = 0.0; union = np.zeros((H, W), np.uint8)
    for n, (sc, nc) in fs.items():
        p = np.round(sc * 16).astype(np.int32)
        m = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(m, p, 1, shift=4); m = m.astype(bool) & roi
        union |= m.astype(np.uint8)
        if not m.any(): continue
        if n == "U":               # đáy: xám (đáy hộp, hộp phóng to trong post), chỉ cấm cam
            B += (m & org).sum()
        elif n == "T":
            B += (m & org).sum() + 0.5 * (m & ~(wht | drk)).sum()
        else:
            pix = m & org
            if pix.sum() < 0.3 * m.sum(): B += (m & ~(org | wht | drk)).sum() + 0.3 * (m & ~org).sum(); continue
            med = np.median(R[pix]); ok = org & (np.abs(R - med) < 14)
            B += (m & ~ok & ~wht & ~drk).sum() + 0.3 * (m & wht).sum()
    un = union.astype(bool)
    A = (org & ~un).sum(); C = (wht & ~un).sum()
    v = (A + B + C) / 60000.0
    return (v, A, B, C) if detail else v

def loss_tail(q, cls, cam=CAM):
    """Khung 113+: hộp bay lên/phóng to, bị phủ xám, mặt đáy xám. Khớp IoU riêng từng mặt cam (mặt sáng = mặt trước, mặt tối = mặt bên) với hai mặt cam quan sát được (tách bằng Otsu trên r)."""
    org, wht, drk, roi, R = cls[:5]; of, os_ = cls[5], cls[6]
    fs = project(q, cam)
    if not fs: return 3.0
    tot = 0.0
    for obs, pick in ((of, lambda n, nc: nc[2]), (os_, lambda n, nc: -abs(nc[2]))):
        best = 1.0
        for n, (sc, nc) in fs.items():
            if n in "TU": continue
            m = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(m, np.round(sc * 16).astype(np.int32), 1, shift=4); m = m.astype(bool)
            u = (m | obs).sum(); i = (m & obs).sum(); best = min(best, 1 - i / max(u, 1))
        tot += best
    return tot

def classes_tail(img, f):
    org, wht, drk, roi, R = classes(img, f)
    r = R[org]
    if r.size < 50: return org, wht, drk, roi, R, org, org
    t = cv2.threshold(r.astype(np.uint8).reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0]
    return org, wht, drk, roi, R, org & (R > t), org & (R <= t)

def front_masks(src, f):
    """mặt trước (cam sáng) và mặt bên (cam tối) của hộp từ ảnh gốc, ở nửa độ phân giải; ignore = vùng tối (terminal, bóng, chữ); bottom = hàng thấp nhất (độ phân giải đầy đủ) của mặt trước"""
    im = cv2.imread(f"{src}/f{f:03d}.png")[:, :, ::-1].astype(int); r, g, b = im[..., 0], im[..., 1], im[..., 2]
    org = (r > 60) & (r < 215) & (g > 0.17 * r) & (g < 0.46 * r) & (b < 0.16 * r + 3); org[1380:] = False
    if org.sum() < 3000: return None
    t = cv2.threshold(r[org].astype(np.uint8).reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0]
    out = {}
    for nm, m in (("F", org & (r > t)), ("R", org & (r <= t))):
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8)); n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        if n < 2: return None
        i = 1 + np.argmax(st[1:, 4]); out[nm] = (lab == i)
        if nm == "F": out["bottom"] = int(st[i, 1] + st[i, 3])
    ign = cv2.dilate((im.max(2) < 62).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
    rs = lambda m: cv2.resize(m.astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST).astype(bool)
    return dict(F=rs(out["F"]), R=rs(out["R"]), ign=rs(ign), bottom=out["bottom"])

def loss_front(q, tg, cam=CAM):
    fs = project(q, cam); tot = 0.0
    for n in "FR":
        if n not in fs: tot += 1.0; continue
        m = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(m, np.round(fs[n][0] * 16).astype(np.int32), 1, shift=4)
        m = cv2.erode(m, np.ones((5, 5), np.uint8)).astype(bool); ok = ~tg["ign"]
        a = m & ok; b = tg[n] & ok; tot += 1 - (a & b).sum() / max((a | b).sum(), 1)
        if n == "F":
            rows = np.where(m.any(1))[0]; tot += min(abs((rows.max() * D if len(rows) else 0) - tg["bottom"]) / 60.0, 3.0)
    return tot

def fit_frame(cls, q0, cam=CAM, step=(25, 25, 40, 3, 3, 3), iters=700, lossf=None):
    if lossf is not None: loss_ = lossf
    else: loss_ = loss
    return _fit(cls, q0, cam, step, iters, loss_)

def _fit(cls, q0, cam, step, iters, loss):
    x0 = np.array(q0, float); sim = np.vstack([x0] + [x0 + np.eye(6)[i] * step[i] for i in range(6)])
    r = minimize(lambda q: loss(q, cls, cam), x0, method="Nelder-Mead", options=dict(initial_simplex=sim, maxiter=iters, xatol=0.05, fatol=1e-5))
    r2 = minimize(lambda q: loss(q, cls, cam), r.x, method="Nelder-Mead", options=dict(initial_simplex=np.vstack([r.x] + [r.x + np.eye(6)[i] * step[i] * 0.3 for i in range(6)]), maxiter=iters, xatol=0.02, fatol=1e-6))
    return r2.x, r2.fun

def init_pose(cls, cam=CAM, iters=250, rys=range(-30, 31, 10)):
    best = None
    for ry in rys:
        for rx in (-35, -20, -5):
            q, v = fit_frame(cls, [0, 0, 0, rx, ry, 0], cam, iters=iters)
            if best is None or v < best[1]: best = (q, v)
    return best

def _cam_job(a):
    f, q, cam, src = a
    cls = classes(load(src, f), f); q, v = fit_frame(cls, q, cam, iters=250); return f, q, v

def camfit(src, outp="cube_cam.json"):
    from multiprocessing import Pool
    KF = [36, 44, 52, 60, 68, 76, 84, 96, 108]
    pool = Pool(9); qs = {}
    cam = dict(CAM)
    qs[60] = init_pose(classes(load(src, 60), 60), cam, 200)[0]; print("khởi đầu 60", np.round(qs[60], 1), flush=True)
    for f in KF:                       # bám tiến/lùi từ f60 để giữ đúng mặt (SCROLL phía trước)
        if f == 60: continue
        step = 1 if f > 60 else -1
        q = qs[60]
        for g in range(60 + step, f + step, step):
            q, v = fit_frame(classes(load(src, g), g), q, cam, iters=200)
        qs[f] = q; print("khởi đầu", f, np.round(q, 1), round(v, 3), flush=True)
    def total(g):
        c = dict(cam, P=g[0], hy=g[1], hz=g[2])
        out = pool.map(_cam_job, [(f, qs[f], c, src) for f in KF])
        for f, q, v in out: qs[f] = q
        t = sum(v for _, _, v in out); print(np.round(g, 1), round(t / len(KF), 4), flush=True); return t
    g0 = np.array([cam["P"], cam["hy"], cam["hz"]])
    st = np.array([500, 40, 40])
    r = minimize(total, g0, method="Nelder-Mead", options=dict(initial_simplex=np.vstack([g0] + [g0 + np.eye(3)[i] * st[i] for i in range(3)]), maxiter=60, xatol=1, fatol=1e-4))
    g = r.x; res = dict(P=g[0], hy=g[1], hz=g[2], ox=cam['ox'], oy=cam['oy'], hx=300.0, err=r.fun / len(KF))
    json.dump(res, open(outp, "w"), indent=1); print(res)

def track_seq(src, frames, q0, cam=CAM):
    """bám tuần tự: mỗi khung thử nhiều điểm khởi đầu (giữ nguyên, ngoại suy theo vận tốc xoay, lệch ry ±8/±16/±30) rồi lấy mất mát thấp nhất"""
    out = {}; q = np.array(q0, float); vel = np.zeros(6)
    for f in frames:
        cls = classes(load(src, f), f); cands = []
        for k in (0, 1, 0.5):
            for dy in (0, 8, -8, 16, -16, 30, -30):
                c = q + vel * k; c = c.copy(); c[4] += dy; cands.append(c)
        sc = sorted(((loss(c, cls, cam), i) for i, c in enumerate(cands)))[:4]
        best = None
        for _, i in sc:
            qq, v = fit_frame(cls, cands[i], cam, iters=300)
            if best is None or v < best[1]: best = (qq, v)
        vel = best[0] - q; q = best[0]; out[f] = (q.tolist(), float(best[1]))
        print(f, np.round(q, 1), round(best[1], 3), flush=True)
    return out

def track(src, outp):
    cls = classes(load(src, 60), 60); q0, v0 = init_pose(cls, CAM, 300)
    res = {60: (q0.tolist(), v0)}
    res.update(track_seq(src, range(61, 133), q0, CAM))
    res.update(track_seq(src, range(59, 29, -1), q0, CAM))
    json.dump({str(k): v for k, v in sorted(res.items())}, open(outp, "w"))

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "cam":
        camfit(sys.argv[2])
    elif cmd == "tail":      # tail frames/s08 track08.json f0 f1: bám lại f0..f1 (đoạn hộp phóng to bay lên) từ tư thế f0-1 trong track08.json, ghi đè vào cùng file
        js = json.load(open(sys.argv[3])); f0, f1 = int(sys.argv[4]), int(sys.argv[5])
        out = track_seq(sys.argv[2], range(f0, f1 + 1), js[str(f0 - 1)][0], CAM)
        for k, v in out.items(): js[str(k)] = v
        json.dump(js, open(sys.argv[3], "w"))
    elif cmd == "back":      # back frames/s08 track08.json f1 f0: bám lùi f1..f0 (giảm dần) từ tư thế f1+1 (giai đoạn ráp hộp, thân hộp còn nắp hở)
        js = json.load(open(sys.argv[3])); f1, f0 = int(sys.argv[4]), int(sys.argv[5])
        out = track_seq(sys.argv[2], range(f1, f0 - 1, -1), js[str(f1 + 1)][0], CAM)
        for k, v in out.items(): js[str(k)] = v
        json.dump(js, open(sys.argv[3], "w"))
    elif cmd == "closeloop":  # closeloop frames/s08 frames/r08 out.json f0 f1: vòng kín đo-trên-ảnh-dựng: so [đáy, x0, x1] của mặt trước (hàm front_masks) giữa ảnh GỐC và ảnh REMAKE rồi chỉnh (x,y,z,rx) để mô hình dịch đúng phần chênh; x0 bỏ khi bị cắt ở mép (<6 px); rx giữ nguyên (phạt nặng); với f>=117 chỉ còn đáy và x1 nên (x,z) có phạt nhẹ
        from scipy.optimize import least_squares
        js = json.load(open(sys.argv[4])); f0, f1 = int(sys.argv[5]), int(sys.argv[6])
        def extv(q):
            P = project(q, CAM)["F"][0] * D; return np.array([P[:, 1].max(), P[:, 0].min(), P[:, 0].max(), P[:, 1].min()])
        def meas(src, f):
            tg = front_masks(src, f); cols = np.where(tg["F"].any(0))[0]; rows = np.where(tg["F"].any(1))[0]; return np.array([tg["bottom"], cols.min() * D, cols.max() * D, rows.min() * D], float)
        for f in range(f0, f1 + 1):
            q = np.array(js[str(f)][0]); mo = meas(sys.argv[2], f); mr = meas(sys.argv[3], f); dm = mo - mr
            w = np.array([1.0, 0.0 if min(mo[1], mr[1]) < 6 else 1.0, 1.0, 0.0]); base = extv(q)   # đỉnh KHÔNG dùng: chữ marquee lớn che phần trên mặt trước ở gốc và ở remake khác nhau
            def res(v):
                qq = q.copy(); qq[[0, 1, 2, 3]] += v
                return np.r_[w * (extv(qq) - base - dm), 0.15 * v[0] if f >= 117 else 0, 0.05 * v[2] if f >= 117 else 0, 3.0 * v[3]]
            r = least_squares(res, np.zeros(4)); q[[0, 1, 2, 3]] += r.x; js[str(f)] = (q.tolist(), None)
            print(f, "chênh [đáy,x0,x1,đỉnh] gốc-remake", np.round(dm, 0), "-> dịch (x,y,z,rx)", np.round(r.x, 1))
        json.dump(js, open(sys.argv[4], "w"))
    elif cmd == "ybottom":   # ybottom frames/s08 out.json f0 f1 [interp|hold]: giữ x,z,rx,ry,rz, giải y sao cho cạnh đáy mặt trước của mô hình = cạnh đáy đo trên ảnh (mất mát ghi null = chỉnh tay theo số đo); interp: x,z,rx,ry,rz nội suy giữa f0-1 và f1+1; hold: lấy của f-1
        js = json.load(open(sys.argv[3])); f0, f1 = int(sys.argv[4]), int(sys.argv[5]); mode = sys.argv[6] if len(sys.argv) > 6 else ""
        def mb(q):
            fs = project(q, CAM); m = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(m, np.round(fs["F"][0] * 16).astype(np.int32), 1, shift=4)
            rows = np.where(cv2.erode(m, np.ones((5, 5), np.uint8)).any(1))[0]; return rows.max() * D if len(rows) else -10 ** 4
        for f in range(f0, f1 + 1):
            tg = front_masks(sys.argv[2], f)
            if mode == "interp": a, b = np.array(js[str(f0 - 1)][0]), np.array(js[str(f1 + 1)][0]); q = a + (b - a) * (f - f0 + 1) / (f1 - f0 + 2)
            elif mode == "hold": q = np.array(js[str(f - 1)][0])
            else: q = np.array(js[str(f)][0])
            lo, hi = -1500.0, 500.0
            for _ in range(40):
                mid = (lo + hi) / 2; qq = q.copy(); qq[1] = mid
                if mb(qq) > tg["bottom"]: hi = mid
                else: lo = mid
            q[1] = (lo + hi) / 2; js[str(f)] = (q.tolist(), None); print(f, np.round(q, 1), "đáy mô hình", mb(q), "đo", tg["bottom"])
        json.dump(js, open(sys.argv[3], "w"))
    elif cmd == "tail3":     # tail3 frames/s08 out.json f0 f1: bám lại f0..f1 bằng IoU của MẶT TRƯỚC (cam sáng) và MẶT BÊN (cam tối) + sai lệch cạnh đáy mặt trước (đo trên ảnh, cùng hàm `front_masks`), bỏ vùng tối (terminal, bóng, chữ); ry giữ gần giá trị trước
        js = json.load(open(sys.argv[3])); f0, f1 = int(sys.argv[4]), int(sys.argv[5]); q = np.array(js[str(f0 - 1)][0]); vel = np.zeros(6)
        for f in range(f0, f1 + 1):
            tg = front_masks(sys.argv[2], f)
            if tg is None: print(f, "không còn hộp"); break
            cands = []
            for k in (0, 1):
                for dz in (0, 150, -150, 300):
                    for dy in (0, 100, -100, 200):
                        c = q + vel * k; c = c.copy(); c[2] += dz; c[1] += dy; cands.append(c)
            sc = sorted(((loss_front(c, tg), i) for i, c in enumerate(cands)))[:4]; best = None
            for _, i in sc:
                qq, v = _fit(None, cands[i], CAM, (30, 30, 60, 4, 2, 3), 500, lambda qq, _c, _cam, tg=tg: loss_front(qq, tg))
                if best is None or v < best[1]: best = (qq, v)
            vel = best[0] - q; q = best[0]; js[str(f)] = (q.tolist(), float(best[1])); print(f, np.round(q, 1), round(best[1], 3), "đáy đo", tg["bottom"], flush=True)
        json.dump(js, open(sys.argv[3], "w"))
    elif cmd == "tail2":     # tail2 frames/s08 track08.json f0 f1: như `tail` nhưng dùng IoU từng mặt (loss_tail)
        js = json.load(open(sys.argv[3])); f0, f1 = int(sys.argv[4]), int(sys.argv[5]); q = np.array(js[str(f0 - 1)][0]); vel = np.zeros(6)
        for f in range(f0, f1 + 1):
            cls = classes_tail(load(sys.argv[2], f), f); cands = []
            for k in (0, 1):
                for dz in (0, 100, -100, 200, 300):
                    for dy in (0, 60, -60, 120, -120):
                        for drx in (0, 8, -8):
                            c = q + vel * k; c = c.copy(); c[2] += dz; c[1] += dy; c[3] += drx; cands.append(c)
            sc = sorted(((loss_tail(c, cls), i) for i, c in enumerate(cands)))[:5]; best = None
            for _, i in sc:
                qq, v = fit_frame(cls, cands[i], CAM, step=(30, 30, 60, 4, 3, 3), iters=400, lossf=loss_tail)
                if best is None or v < best[1]: best = (qq, v)
            vel = best[0] - q; q = best[0]; js[str(f)] = (q.tolist(), float(best[1])); print(f, np.round(q, 1), round(best[1], 3), flush=True)
        json.dump(js, open(sys.argv[3], "w"))
    elif cmd == "track":
        track(sys.argv[2], sys.argv[3])
    elif cmd == "overlay":   # overlay frames/s08 out.json f1 f2 ... -> tmp/cube_overlay.jpg (lưới khớp chồng lên khung gốc)
        src, js = sys.argv[2], json.load(open(sys.argv[3])); tiles = []
        for f in map(int, sys.argv[4:]):
            im = load(src, f)[:, :, ::-1].astype(np.uint8).copy()
            for n, (sc, nc) in project(js[str(f)][0]).items():
                cv2.polylines(im, [np.round(sc).astype(np.int32)], True, (0, 255, 0) if n not in "TU" else (255, 0, 255), 2)
            tiles.append(im)
        cv2.imwrite("tmp/cube_overlay.jpg", np.hstack(tiles))
    elif cmd == "shade":     # shade frames/s08 track08.json: màu phẳng từng mặt cam theo pháp tuyến camera (n_x, n_y, n_z) -> hồi quy tuyến tính r = a + b·n_x + c·n_y + d·n_z
        src, js = sys.argv[2], json.load(open(sys.argv[3])); X = []; Y = []
        for f in range(30, 113):
            q = js[str(f)][0]; img = load(src, f); org = classes(img, f)[0]
            for n, (sc, nc) in project(q).items():
                if n in "TU": continue
                m = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(m, np.round(sc * 16).astype(np.int32), 1, shift=4)
                m = cv2.erode(m, np.ones((9, 9), np.uint8)).astype(bool) & org
                if m.sum() < 400: continue
                X.append([1, *nc]); Y.append(np.median(img[m], axis=0))
        X = np.array(X); Y = np.array(Y); print("mẫu", len(X))
        for c, nm in enumerate("rgb"):
            co, *_ = np.linalg.lstsq(X, Y[:, c], rcond=None); res = Y[:, c] - X @ co
            print(nm, "a,nx,ny,nz =", np.round(co, 2), "sai số chuẩn", round(res.std(), 2), "min/max", Y[:, c].min(), Y[:, c].max())
        # r theo nz đơn lẻ
        co, *_ = np.linalg.lstsq(X[:, [0, 3]], Y[:, 0], rcond=None); print("r = a + d·nz:", np.round(co, 2), "sai số", round((Y[:, 0] - X[:, [0, 3]] @ co).std(), 2))
        co, *_ = np.linalg.lstsq(np.c_[np.ones(len(Y)), Y[:, 0]], Y[:, 1], rcond=None); print("g theo r:", np.round(co, 3)); co, *_ = np.linalg.lstsq(np.c_[np.ones(len(Y)), Y[:, 0]], Y[:, 2], rcond=None); print("b theo r:", np.round(co, 3))
    elif cmd == "export":    # export track.json -> in bảng tư thế làm trơn (t, x, y, z, rx, ry, rz) dạng JS cho scene; f18..f132, trơn 3 điểm trừ f26-f30 (đợt phình), f113+ (bay lên: giữ nguyên số đo) và ry
        js = json.load(open(sys.argv[2])); fr = sorted(int(k) for k in js if int(k) >= 18)
        Q = {f: np.array(js[str(f)][0]) for f in fr}
        for f in range(max(fr) + 1, 133): Q[f] = Q[f - 1] + np.array([0, Q[f - 1][1] - Q[f - 2][1], 0, 0, 0, 0])      # hộp ra khỏi khung: ngoại suy theo bước y của 2 khung cuối
        fr = sorted(Q); S = {}
        for f in fr:
            if f in (fr[0], fr[-1]) or 26 <= f <= 30 or f >= 113: S[f] = Q[f].copy(); continue
            S[f] = 0.25 * Q[f - 1] + 0.5 * Q[f] + 0.25 * Q[f + 1]; S[f][4] = Q[f][4]
        rows = [[round((f - 1) / 30, 4)] + [round(float(v), 1) for v in S[f]] for f in fr]
        print("const CP = " + json.dumps(rows, separators=(",", ":")) + ";")
    elif cmd == "jit":       # jit frames/s08 [f_cuối]: nhiễu xoay ô halftone của #cover ở đầu s08 (f1..f9): độ tập trung hướng cạnh R của 4θ -> biên độ xoay đều ±A, R = sin(4A)/(4A) (cách đo của measure_texture.py jit, vùng y 500-1700)
        from scipy import ndimage as ndi
        def solve(R):
            lo, hi = 0.0, np.pi / 4
            for _ in range(40):
                m = (lo + hi) / 2
                if np.sin(4 * m) / (4 * m) > R: lo = m
                else: hi = m
            return np.degrees((lo + hi) / 2)
        for f in range(1, (int(sys.argv[3]) if len(sys.argv) > 3 else 9) + 1):
            lum = cv2.imread(f"{sys.argv[2]}/f{f:03d}.png").astype(float).mean(2)[500:1700]
            sm = ndi.gaussian_filter(lum, 1.0); gx = ndi.sobel(sm, axis=1); gy = ndi.sobel(sm, axis=0); mag = np.hypot(gx, gy); m = mag > 120
            th = np.arctan2(gy[m], gx[m]); w = mag[m]; R = abs((w * np.exp(4j * th)).sum() / w.sum())
            print(f"f{f}: R {R:.2f} -> ±{solve(min(R, 0.999)):.0f}°")
    elif cmd == "shadow":    # shadow frames/s08 f0 f1 step -> bbox lõi tối (max<50) của bóng elip dưới hộp, theo khung (hàng có >=200 điểm tối trong x 150-950 và y 1280-1460)
        src = sys.argv[2]
        for f in range(int(sys.argv[3]), int(sys.argv[4]) + 1, int(sys.argv[5])):
            im = cv2.imread(f"{src}/f{f:03d}.png")[:, :, ::-1].astype(int); dk = im[1280:1460, 150:950].max(2) < 50
            rows = [y for y in range(dk.shape[0]) if dk[y].sum() >= 200]
            if not rows: print(f, "-"); continue
            # chỉ lấy dải liên tục thấp nhất
            xs = np.where(dk[rows].any(0))[0]; print(f, "y", rows[0] + 1280, rows[-1] + 1280, "x", xs.min() + 150, xs.max() + 150, "dài", len(rows))
