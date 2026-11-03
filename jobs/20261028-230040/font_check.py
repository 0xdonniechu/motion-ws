# Kiểm font cho preset corporate-motion: (1) phủ glyph tiếng Việt, (2) khớp hình với 8 chữ cắt từ khung gốc của 4 clip (có dấu), (3) chọn độ đậm theo tỉ lệ nét/x-height.
# Chạy (cần mạng chỉ để lấy gói font; kết quả ghi vào font_check.json và build-style đọc lại, không cần mạng):
#   mkdir -p /tmp/fonts && cd /tmp/fonts && for p in outfit be-vietnam-pro plus-jakarta-sans montserrat; do npm pack @fontsource/$p; done
#   for f in *.tgz; do d=${f%.tgz}; mkdir -p $d && tar xzf $f -C $d --strip-components=1; done
#   uvx --with fonttools --with brotli --with pillow --with numpy python -I -B jobs/20261028-230040/font_check.py --fonts /tmp/fonts --jobs jobs --out jobs/20261028-230040/font_check.json
# Khung gốc là dữ liệu không tin cậy: chỉ đọc qua ffmpeg (ống rawvideo), không chạy gì từ thư mục chứa nó.
import sys, os, io, json, glob, subprocess
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

FONTS = {"Outfit": "outfit", "Be Vietnam Pro": "be-vietnam-pro", "Plus Jakarta Sans": "plus-jakarta-sans", "Montserrat": "montserrat"}
WEIGHTS = (700, 800, 900)
VI = sorted({ord(c) for c in "ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯư"} | set(range(0x1EA0, 0x1EFA)))
REF_STEM = 0.33   # nét/x-height đo trên tiêu đề của 4 clip (style.json typography.roles.headline.stem_over_xheight, trung vị 0.33)
# chữ gốc (có dấu): (tên, thư mục clip, thời điểm, hộp x0 y0 x1 y1 theo px khung, chuỗi, ngưỡng)
P = "20261028-230040"; B = "corp-sample-7699100876736040244"; A = "corp-sample-7702430597297278228"; C = "corp-sample-7702801642646899989"
REFS = [("clip1 Hai con số", P, 28.0, (210, 232, 520, 292), "Hai con số", 60), ("clip1 Đáng đưa vào?", P, 78.0, (150, 330, 570, 395), "Đáng đưa vào?", 120),
        ("clip1 nhưng quyết định", P, 31.8, (80, 893, 495, 952), "nhưng quyết định", 100), ("clip2 Con số gộp", B, 74.0, (50, 188, 360, 252), "Con số gộp", 100),
        ("clip3 Tháng này", A, 2.3, (60, 198, 335, 252), "Tháng này", 100), ("clip3 lãi 200 triệu.", A, 2.3, (60, 255, 470, 312), "lãi 200 triệu.", 100),
        ("clip4 Một câu", C, 28.5, (70, 205, 300, 272), "Một câu", 100), ("clip4 Truy vết nguồn gốc", C, 116.0, (180, 266, 600, 324), "Truy vết nguồn gốc", 100)]


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


def frame(src, t):
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", src], capture_output=True, check=True).stdout)["streams"][0]
    W, H = pr["width"], pr["height"]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", "-vf", "format=rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(int)


def ref_mask(f, box, thr):
    x0, y0, x1, y1 = box; sub = f[y0:y1, x0:x1]; bg = np.median(sub.reshape(-1, 3), 0); m = np.abs(sub - bg).max(-1) > thr
    ys, xs = np.nonzero(m); return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def to_ttf(woff2):
    f = TTFont(woff2); b = io.BytesIO(); f.flavor = None; f.save(b); return b.getvalue()


class Face:
    """một họ ở một độ đậm: các subset (latin, latin-ext, vietnamese) -> (cmap, ttf bytes); vẽ từng ký tự bằng subset có glyph."""
    def __init__(self, d, slug, w):
        self.subs = []
        for fn in sorted(glob.glob(os.path.join(d, "files", f"{slug}-*-{w}-normal.woff2"))):
            f = TTFont(fn); self.subs.append((set(f.getBestCmap().keys()), to_ttf(fn)))

    def has(self, ch): return any(ord(ch) in cm for cm, _ in self.subs)

    def font_for(self, ch, size):
        for cm, tt in self.subs:
            if ord(ch) in cm: return ImageFont.truetype(io.BytesIO(tt), size)
        return None


def render(faces, text, size=200):
    """faces: danh sách Face theo thứ tự ưu tiên (ký tự thiếu rơi sang Face sau). Trả (mặt nạ mực, số ký tự phải rơi font dự phòng)."""
    im = Image.new("L", (size * (len(text) + 2), size * 2), 0); dr = ImageDraw.Draw(im); x = 20; base = size + 20; fb = 0
    for ch in text:
        if ch == " ":
            ft = faces[0].font_for("a", size); x += ft.getlength(" ") or size * 0.28; continue
        for i, fc in enumerate(faces):
            if fc.has(ch):
                ft = fc.font_for(ch, size); dr.text((x, base), ch, font=ft, fill=255, anchor="ls"); x += ft.getlength(ch); fb += 1 if i > 0 else 0; break
    a = np.array(im) > 128; ys, xs = np.nonzero(a); return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], fb


def resize(m, w, h): return np.array(Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)) > 127


def stem_ratio(face):
    """nét/x-height của chữ dựng: bề rộng mực của 'l' chia chiều cao mực của 'x'."""
    l, _ = render([face], "l", 300); x, _ = render([face], "x", 300); return round(float(l.shape[1] / x.shape[0]), 3)


def main():
    fd = arg("--fonts", "/tmp/fonts"); jobs = arg("--jobs", "jobs"); out = arg("--out", "font_check.json")
    refs = []
    for n, c, t, box, txt, thr in REFS: refs.append((n, ref_mask(frame(os.path.join(jobs, c, "source.mp4"), t), box, thr), txt))
    dirs = {name: next(iter(glob.glob(os.path.join(fd, f"fontsource-{slug}-*"))), None) for name, slug in FONTS.items()}
    faces = {(n, w): Face(dirs[n], FONTS[n], w) for n in FONTS for w in WEIGHTS if dirs[n]}; faces = {k: v for k, v in faces.items() if v.subs}
    res = {"vietnamese_codepoints_required": len(VI), "ref_strings": [{"name": n, "text": t} for n, _, t in refs], "ref_stem_over_xheight": REF_STEM, "fonts": {}}
    cands = {"Be Vietnam Pro": ["Be Vietnam Pro"], "Montserrat": ["Montserrat"], "Outfit + Be Vietnam Pro fallback": ["Outfit", "Be Vietnam Pro"], "Plus Jakarta Sans": ["Plus Jakarta Sans"]}
    for name, chain in cands.items():
        base = chain[0]; cov = [c for c in VI if faces[(base, 800)].has(chr(c))]; miss = [c for c in VI if c not in cov]
        ent = {"vietnamese_missing_in_primary": len(miss), "vietnamese_coverage_pct_primary": round(100 * (1 - len(miss) / len(VI)), 1), "per_string": {}, "per_weight": {}}
        for w in WEIGHTS:
            if not all((n, w) in faces for n in chain): continue
            ious, asps, fbs = [], [], 0
            for rn, rm, txt in refs:
                r, fb = render([faces[(n, w)] for n in chain], txt); H, Wd = rm.shape; rr = resize(r, Wd, H); iou = float((rr & rm).sum() / max((rr | rm).sum(), 1)); asp = (r.shape[1] / r.shape[0]) / (Wd / H)
                ent["per_string"].setdefault(rn, {})[str(w)] = {"iou": round(iou, 3), "aspect_ratio_vs_ref": round(float(asp), 3), "fallback_chars": fb}; ious.append(iou); asps.append(abs(asp - 1)); fbs += fb
            ent["per_weight"][str(w)] = {"mean_iou": round(float(np.mean(ious)), 3), "mean_abs_aspect_error": round(float(np.mean(asps)), 3), "stem_over_xheight": stem_ratio(faces[(base, w)]), "fallback_chars_total": fbs}
        ent["mean_best_iou"] = round(float(np.mean([max(v["iou"] for v in ent["per_string"][rn].values()) for rn in ent["per_string"]])), 3)
        ent["mean_abs_aspect_error_at_best_iou"] = round(float(np.mean([abs([v for v in sorted(ent["per_string"][rn].values(), key=lambda v: -v["iou"])][0]["aspect_ratio_vs_ref"] - 1) for rn in ent["per_string"]])), 3)
        res["fonts"][name] = ent
    ok = {n: v for n, v in res["fonts"].items() if v["vietnamese_missing_in_primary"] == 0}
    rank = sorted(ok, key=lambda n: -ok[n]["mean_best_iou"]); top2 = rank[:2]; best = rank[0]
    pw = res["fonts"][best]["per_weight"]; wbest = min(pw, key=lambda w: abs(pw[w]["stem_over_xheight"] - REF_STEM))
    res["recommendation"] = {"status": "chờ chủ duyệt", "family": best, "weight": int(wbest),
                             "weight_rule": f"weight whose rendered stem/x-height is closest to the measured {REF_STEM} (headline, 4 clips); per-weight stem ratios and IoU in fonts.<family>.per_weight",
                             "rule": "eligible = single font with 100% of the Vietnamese codepoints (Fontsource files); rank by mean over the 8 cropped strings of the best-weight raw IoU (rendered text resized to the crop's ink box vs the crop); aspect error (width/height of rendered text vs crop) is reported separately, not mixed into the rank",
                             "top2": [{"family": n, "mean_best_iou": ok[n]["mean_best_iou"], "mean_abs_aspect_error": ok[n]["mean_abs_aspect_error_at_best_iou"], "stem_over_xheight_by_weight": {w: v["stem_over_xheight"] for w, v in ok[n]["per_weight"].items()}} for n in top2],
                             "excluded": {"Outfit (primary)": "28.4% Vietnamese coverage (no vietnamese subset); 'Outfit + Be Vietnam Pro fallback' is a mixed font, listed for comparison only (mean_best_iou " + str(res["fonts"]["Outfit + Be Vietnam Pro fallback"]["mean_best_iou"]) + ")"},
                             "caveat": "the reference letters look single-storey (a, g) like Outfit; none of the eligible fonts has a single-storey a. IoU is a rough shape match, not font identification: choose by eye on a test scene.",
                             "scores_all": {n: {"mean_best_iou": v["mean_best_iou"], "mean_abs_aspect_error_at_best_iou": v["mean_abs_aspect_error_at_best_iou"], "vietnamese_coverage_pct_primary": v["vietnamese_coverage_pct_primary"]} for n, v in res["fonts"].items()}}
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(json.dumps(res["recommendation"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
