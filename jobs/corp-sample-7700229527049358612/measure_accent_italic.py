"""Đo cỡ chữ nhấn nghiêng có chân (italic serif) so với chữ không chân đứng cạnh, ở các clip quét thêm 2026-11-03.
Cách đo: mỗi từ/dòng = một hộp (x0,y0,x1,y1, khung gốc); mực = điểm ảnh khác nền nhiều; dải x-height = các hàng có mật độ mực >= 60% hàng đậm nhất
(chữ thường không có nét lên/xuống chiếm dải này nhất). cỡ chữ = x-height / (sxHeight của font)/upm: Be Vietnam Pro 800 = 0.530 em, Newsreader italic = 0.426 em (852/2000, fontTools OS/2).
Chạy: uvx --with numpy --with pillow python -I -B measure_accent_italic.py <đường dẫn jobs>  (ffmpeg có sẵn)."""
import sys, os, json, subprocess, tempfile
import numpy as np
from PIL import Image
XH = {"sans": 0.530, "serif_italic": 0.426}
JOBS = sys.argv[1] if len(sys.argv) > 1 else ".."
# (clip, t, nhãn, hộp, loại)  hộp theo khung gốc của clip
CASES = [
  ("corp-sample-7699477231017446676", 98.0, "tra cứu", (170, 225, 280, 262), "sans"),
  ("corp-sample-7699477231017446676", 98.0, "biểu đồ", (286, 218, 402, 266), "serif_italic"),
  ("corp-sample-7699477231017446676", 102.0, "Từ điển", (195, 183, 380, 240), "sans"),
  ("corp-sample-7699477231017446676", 102.0, "hình ảnh.", (150, 236, 420, 296), "serif_italic"),
  ("corp-sample-7700229527049358612", 40.0, "trung vị", (170, 520, 330, 660), "serif_italic")   # "run" của "trung vị": chỉ chữ x-height,
]
def frame(clip, t):
    f = tempfile.mktemp(suffix=".png"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", os.path.join(JOBS, clip, "source.mp4"), "-frames:v", "1", f], check=True)
    im = np.asarray(Image.open(f).convert("RGB")).astype(int); os.remove(f); return im
W_BIG = lambda im: im.shape[1] > 1000   # khung 1080: nét dày hơn, ngưỡng thấp hơn
def xheight(im, box, frac=0.6):
    x0, y0, x1, y1 = box; c = im[y0:y1, x0:x1]; bg = np.median(c.reshape(-1, 3), 0); ink = (np.abs(c - bg).sum(2) > 150)
    dens = ink.sum(1); thr = frac * dens.max(); rows = np.nonzero(dens >= thr)[0]
    # dải liên tục dài nhất
    runs = np.split(rows, np.nonzero(np.diff(rows) > 1)[0] + 1); best = max(runs, key=len)
    return int(len(best)), int(best[0] + y0), int(best[-1] + y0)
out = []; cache = {}
for clip, t, label, box, kind in CASES:
    im = cache.setdefault((clip, t), frame(clip, t)); h, ya, yb = xheight(im, box, 0.3 if W_BIG(im) else 0.6); W = im.shape[1]
    size = h / XH[kind]
    out.append({"clip": clip, "t": t, "text": label, "kind": kind, "xheight_px": h, "rows": [ya, yb], "frame_w": W, "font_size_px": round(size, 1), "font_size_frac_W": round(size / W, 4)})
    print(json.dumps(out[-1], ensure_ascii=False))
pairs = []
for a, b in ((0, 1), (2, 3)):
    r = out[b]["font_size_px"] / out[a]["font_size_px"]; pairs.append(round(r, 3)); print("tỉ lệ cỡ italic/sans", out[a]["text"], "->", out[b]["text"], round(r, 3))
json.dump({"cases": out, "ratio_italic_over_sans": pairs, "ratio_mean": round(sum(pairs) / len(pairs), 3)}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "accent_italic.json"), "w"), ensure_ascii=False, indent=1)
