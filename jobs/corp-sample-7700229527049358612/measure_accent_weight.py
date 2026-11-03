"""Độ đậm của chữ nhấn nghiêng: độ dài chạy ngang trung vị của mực ở dải x-height / x-height, đo ở khung gốc rồi so với Newsreader italic dựng ở wght 300..700 (fontTools instancer + Pillow) cùng x-height.
Chạy: uvx --with numpy --with pillow --with fonttools --with brotli python -I -B measure_accent_weight.py <jobs> <fonts_dir>"""
import sys, os, io, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
JOBS, FONTS = sys.argv[1], sys.argv[2]
def runs_med(ink, rows):
    L = []
    for r in rows:
        x = ink[r].astype(int); d = np.diff(np.concatenate([[0], x, [0]])); s = np.nonzero(d == 1)[0]; e = np.nonzero(d == -1)[0]; L += list(e - s)
    return float(np.median(L))
def source(clip, t, box, y0, y1):
    f = tempfile.mktemp(suffix=".png"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", os.path.join(JOBS, clip, "source.mp4"), "-frames:v", "1", f], check=True)
    im = np.asarray(Image.open(f).convert("RGB")).astype(int); os.remove(f); x0, _, x1, _ = box; c = im[y0:y1 + 1, x0:x1]; bg = np.median(c.reshape(-1, 3), 0)
    ink = np.abs(c - bg).sum(2) > 200; mid = [(y1 - y0) // 2 - 3, (y1 - y0) // 2, (y1 - y0) // 2 + 3]
    return runs_med(ink, mid) / (y1 - y0 + 1)
cases = {"trung vị (xh 70)": source("corp-sample-7700229527049358612", 40.0, (170, 520, 330, 660), 567, 636)}
print("đo gốc: độ dài chạy / x-height =", {k: round(v, 3) for k, v in cases.items()})
base = TTFont(os.path.join(FONTS, "newsreader-latin-wght-italic.woff2"))
for w in (300, 400, 500, 600, 700):
    f = instancer.instantiateVariableFont(TTFont(os.path.join(FONTS, "newsreader-latin-wght-italic.woff2")), {"wght": w}); bio = io.BytesIO(); f.save(bio); bio.seek(0)
    size = 70 / 0.426; ft = ImageFont.truetype(bio, int(round(size))); im = Image.new("L", (900, 400), 255); d = ImageDraw.Draw(im); d.text((20, 40), "run", font=ft, fill=0)
    a = np.asarray(im) < 128; ys = np.nonzero(a.sum(1) > 0.5 * a.sum(1).max())[0]; y0, y1 = ys.min(), ys.max()
    mid = [(y0 + y1) // 2 - 3, (y0 + y1) // 2, (y0 + y1) // 2 + 3]
    print("wght", w, "x-height dải", y1 - y0 + 1, "chạy/x-height", round(runs_med(a, mid) / (y1 - y0 + 1), 3))
