# So thời gian chuyển động giữa hai render (cùng composition, khác theme hoặc khác cách dựng). Mỗi khung i: E[i] = TB |khung i - khung i-1| và C[i] = số điểm ảnh đổi hơn 6 mức xám (xám 270x480); khung "chuyển động" = C > 50 điểm (loại nhiễu nén vài điểm ảnh).
#   uvx --with numpy python -I -B jobs/20261103-corp-demo-dashboard/compare_timing.py A.mp4 B.mp4
# In: số khung chuyển động mỗi bên, số khung lệch mặt nạ, các khung vào/ra từng đợt chuyển động (đợt = chuỗi khung chuyển động cách nhau <=3 khung) có trùng nhau không, Pearson r của C (chuẩn hoá) và độ trễ khớp tốt nhất. Độ lớn E khác nhau giữa theme là bình thường (nền tối, tương phản khác); nên so THỜI ĐIỂM, không so độ lớn.
import sys, subprocess, json
import numpy as np
a, b = sys.argv[1], sys.argv[2]
def series(src):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", "fps=30,scale=270:480,format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270).astype(np.int16); d = np.abs(F[1:] - F[:-1])
    return d.mean((1, 2)), (d > 6).sum((1, 2))
(Ea, Ca), (Eb, Cb) = series(a), series(b); n = min(len(Ea), len(Eb)); Ea, Eb, Ca, Cb = Ea[:n], Eb[:n], Ca[:n], Cb[:n]
Ma, Mb = Ca > 50, Cb > 50
na, nb = Ca / Ca.max(), Cb / Cb.max()
lags = {l: float(np.corrcoef(na[max(l, 0):n + min(l, 0)], nb[max(-l, 0):n - max(l, 0)])[0, 1]) for l in range(-6, 7)}
def bursts(M):
    out = []; i = 0
    while i < len(M):
        if M[i]:
            j = i
            while j + 1 < len(M) and M[j + 1:j + 5].any(): j += 1
            out.append((i + 1, j + 1)); i = j + 1
        else: i += 1
    return out
ba, bb = bursts(Ma), bursts(Mb)
res = {"frames": n + 1, "motion_frames_A": int(Ma.sum()), "motion_frames_B": int(Mb.sum()), "mask_mismatch_frames": int((Ma != Mb).sum()), "mismatch_at": [int(i + 1) for i in np.nonzero(Ma != Mb)[0]][:40],
       "bursts_A": len(ba), "bursts_B": len(bb), "burst_frames_A": ba, "burst_frames_B": bb, "bursts_equal": ba == bb, "burst_start_diff_frames": [abs(x[0] - y[0]) for x, y in zip(ba, bb)] if len(ba) == len(bb) else None,
       "burst_end_diff_frames": [abs(x[1] - y[1]) for x, y in zip(ba, bb)] if len(ba) == len(bb) else None,
       "pearson_r_C": round(float(np.corrcoef(na, nb)[0, 1]), 4), "best_lag_frames": max(lags, key=lags.get)}
print(json.dumps(res))
