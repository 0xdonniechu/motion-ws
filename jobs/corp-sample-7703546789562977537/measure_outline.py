"""Đo chữ rỗng viền mảnh (outline) ở quét cuối 2026-11-03: nét viền / chiều cao chữ, màu viền, ở hai clip (7703546789562977537 "15%", 7700593599045520641 chữ "N" của "CÔNG CỤ").
Cách đo: một khung tĩnh; hộp mực = điểm ảnh khác nền; chiều cao chữ = hộp mực của chữ không dấu (chữ số, hoặc chữ N); nét viền = trung vị độ dài đoạn mực liên tục trên các hàng ngang
nửa dưới chiều cao chữ, bỏ đoạn dài > 2.5x trung vị đoạn ngắn nhất (nét chéo / thân chữ cắt xiên) và cả theo chiều dọc ở các cột; màu viền = màu đậm nhất ở lõi nét.
Chạy: uvx --with numpy --with pillow python -I -B measure_outline.py <đường dẫn jobs>. Ghi outline.json cạnh tệp này."""
import sys, os, json, subprocess, tempfile
import numpy as np
from PIL import Image
JOBS = sys.argv[1] if len(sys.argv) > 1 else ".."
# (nhãn, clip, t, hộp chữ không dấu (x0,y0,x1,y1) khung 576x1024, màu nền)
CASES = [("15%", "corp-sample-7703546789562977537", 85.5, (160, 636, 370, 736)), ("N", "corp-sample-7700593599045520641", 157.75, (222, 440, 285, 520))]
def frame(clip, t):
    f = tempfile.mktemp(suffix=".png"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", os.path.join(JOBS, clip, "source.mp4"), "-frames:v", "1", f], check=True)
    im = np.asarray(Image.open(f).convert("RGB")).astype(int); os.remove(f); return im
def runs(v):
    r = []; n = 0
    for x in v:
        if x: n += 1
        elif n: r.append(n); n = 0
    if n: r.append(n)
    return r
out = []
for label, clip, t, (x0, y0, x1, y1) in CASES:
    im = frame(clip, t); c = im[y0:y1, x0:x1]; bg = np.median(c.reshape(-1, 3), 0); d = np.abs(c - bg).sum(2); ink = d > 90
    ys, xs = np.nonzero(ink); h = int(ys.max() - ys.min() + 1); w = int(xs.max() - xs.min() + 1); ya, yb = int(ys.min()), int(ys.max())
    hr = [r for y in range(ya + h // 2, yb - 2) for r in runs(ink[y]) if r <= 12]   # đoạn ngang ngắn (nét thẳng đứng bị cắt ngang)
    vr = [r for x in range(xs.min(), xs.max() + 1) for r in runs(ink[ya + 2:yb - 1, x]) if r <= 12]
    stroke_h = float(np.median(hr)) if hr else None; stroke_v = float(np.median(vr)) if vr else None
    core = c[ink & (d > np.percentile(d[ink], 90))]; col = np.median(core, 0).astype(int)
    rec = {"clip": clip, "text": label, "frame_w": im.shape[1], "cap_h_px": h, "text_w_px": w, "stroke_horiz_scan_px": stroke_h, "stroke_vert_scan_px": stroke_v,
           "stroke_over_cap_h_mean": round((stroke_h + stroke_v) / 2 / h, 4), "stroke_colour_rgb": col.tolist(), "bg_rgb": bg.astype(int).tolist(), "fill_inside": "rỗng (nền thấy qua)"}
    out.append(rec); print(json.dumps(rec, ensure_ascii=False))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outline.json"), "w"), ensure_ascii=False, indent=1)
