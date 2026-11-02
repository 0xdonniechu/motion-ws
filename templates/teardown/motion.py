# Năng lượng chuyển động: trung bình |khung(t) - khung(t-1)| (xám, 180x320, theo fps của cuts.json) theo từng cảnh, gốc vs remake.
# Mốc cảnh đọc từ cuts.json ("S", "TOTAL", "fps") — cùng nguồn với compose.sh.
# Chạy (từ thư mục job, sau compose.sh):  uvx --with numpy python -I motion.py [sNN ...]
# Cổng mục "biên độ": tỉ lệ cả cảnh >= 0.80 và không cửa sổ 0.2s nào < 0.50 khi gốc có chuyển động (năng lượng > 2).
import json, numpy as np, subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
W, H = 180, 320
with open(os.path.join(here, "cuts.json"), encoding="utf-8") as f:
    cuts = json.load(f)
S = cuts.get("S")
if not isinstance(S, list) or len(S) < 2: sys.exit("LỖI: cuts.json thiếu \"S\" (mảng ≥ 2 mốc)")
TOTAL = cuts.get("TOTAL") or S[-1]
FPS = cuts.get("fps") or 30
WIN = max(2, round(0.2 * FPS)); STEP = max(1, WIN // 2)  # cửa sổ 0.2s ở mọi fps
N = len(S) - 1

def energy(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-t", str(TOTAL), "-vf", f"fps={FPS},scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
    return np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))

o = energy(os.path.join(here, "source.mp4")); r = energy(os.path.join(here, "preview/remake.mp4"))
m = min(len(o), len(r)); o, r = o[:m], r[:m]
want = set(sys.argv[1:])
bad = 0
for k in range(N):
    name = f"s{k+1:02d}"
    if want and name not in want: continue
    a, b = int(S[k] * FPS), int(S[k + 1] * FPS)
    eo, er = o[a:b].mean(), r[a:b].mean(); ratio = er / max(eo, 1e-6)
    wins = []
    for s in range(a, b - WIN, STEP):
        go, gr = o[s:s + WIN].mean(), r[s:s + WIN].mean()
        if go > 2: wins.append((gr / go, s / FPS))
    wins.sort()
    ok = ratio >= 0.80 and (not wins or wins[0][0] >= 0.50)
    bad += not ok
    print(f"{name} gốc {eo:5.2f} remake {er:5.2f} tỉ lệ {ratio:4.2f} {'ĐẠT' if ok else 'CHƯA'}  hụt nhất: "
          + ", ".join(f"{t:.1f}s({x:.2f})" for x, t in wins[:3]))
sys.exit(1 if bad else 0)
