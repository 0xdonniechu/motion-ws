# Năng lượng chuyển động: trung bình |khung(t) - khung(t-1)| (xám, 180x320, 30fps) theo từng cảnh, gốc vs remake.
# Chạy (từ thư mục job, sau compose.sh):  uvx --with numpy python -I motion.py [sNN ...]
# Cổng mục "biên độ": tỉ lệ cả cảnh >= 0.80 và không cửa sổ 0.2s nào < 0.50 khi gốc có chuyển động (năng lượng > 2).
import numpy as np, subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
W, H = 180, 320
S = [0, 1.00, 2.75, 4.10, 6.00, 6.70, 7.90, 9.20, 13.00, 16.20, 18.70, 19.40, 21.00, 24.00, 28.40, 30.40, 33.00, 36.03]

def energy(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-t", "36.03", "-vf", f"fps=30,scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
    return np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))

o = energy(os.path.join(here, "source.mp4")); r = energy(os.path.join(here, "preview/remake.mp4"))
m = min(len(o), len(r)); o, r = o[:m], r[:m]
want = set(sys.argv[1:])
bad = 0
for k in range(17):
    name = f"s{k+1:02d}"
    if want and name not in want: continue
    a, b = int(S[k] * 30), int(S[k + 1] * 30)
    eo, er = o[a:b].mean(), r[a:b].mean(); ratio = er / max(eo, 1e-6)
    wins = []
    for s in range(a, b - 6, 3):
        go, gr = o[s:s + 6].mean(), r[s:s + 6].mean()
        if go > 2: wins.append((gr / go, s / 30))
    wins.sort()
    ok = ratio >= 0.80 and (not wins or wins[0][0] >= 0.50)
    bad += not ok
    print(f"{name} gốc {eo:5.2f} remake {er:5.2f} tỉ lệ {ratio:4.2f} {'ĐẠT' if ok else 'CHƯA'}  hụt nhất: "
          + ", ".join(f"{t:.1f}s({x:.2f})" for x, t in wins[:3]))
sys.exit(1 if bad else 0)
