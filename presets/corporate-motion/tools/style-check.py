# So một clip đã render với DNA corporate-motion (style.json): nền tint/trắng, xanh nhấn, mực, nhịp (đợt chuyển động, đứng yên). Chỉ BÁO CÁO, không phải cổng:
# V = trong khoảng đo của 4 clip gốc, T = thấp hơn, C = cao hơn, N = không đo được (nền tối: hàng nền tint/trắng). Thoát 1 chỉ khi sai cỡ khung/fps/độ dài. Đo bằng hàm của jobs/20261028-230040/measure_style.py (không sửa file đó).
#   uvx --with numpy python -I -B style-check.py <clip.mp4> <cuts.json> [--tmp <thư mục>] [--json <tệp>]
import sys, os, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..", "..")
spec = importlib.util.spec_from_file_location("ms", os.path.join(ROOT, "jobs/20261028-230040/measure_style.py"))
ms = importlib.util.module_from_spec(spec); spec.loader.exec_module(ms)
pos = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] not in ("--tmp", "--json")]
opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
src, cuts = os.path.abspath(pos[0]), os.path.abspath(pos[1])
tmp = os.path.abspath(opt("--tmp", os.path.join(os.path.dirname(src), "tmp"))); os.makedirs(tmp, exist_ok=True)
style = json.load(open(os.path.join(HERE, "../style.json"))); lang = json.load(open(os.path.join(HERE, "../language.json")))
want_total = json.load(open(cuts))["TOTAL"]
q = ms._quiet; P = ms.probe(src); T = float(P["duration"])
bad = []
if (P["width"], P["height"]) != (lang["canvas"]["w"], lang["canvas"]["h"]): bad.append("cỡ khung %sx%s" % (P["width"], P["height"]))
if abs(P["fps"] - lang["canvas"]["fps"]) > 0.01: bad.append("fps %s" % P["fps"])
if abs(T - want_total) > 0.1: bad.append("dài %.2fs, kịch bản %.2fs" % (T, want_total))

try: pg = q(ms.page_background, src, T)
except (IndexError, ValueError):   # measure_style.page_background giả định nền SÁNG (điểm ảnh mép sáng > 190 hoặc trắng): theme tối không có điểm nào -> không đo được, báo N/A thay vì sập
    pg = None
allp = q(ms.types_palette, src, {"all": [[0.0, T]]}, 8)["all"]
ep = os.path.join(tmp, "energy-" + os.path.splitext(os.path.basename(src))[0] + ".json"); q(ms.energy, src, ep)   # tên riêng: không đè tmp/energy*.json của script đo khác
en = q(ms.energyprofile, ep, 1.0); ho = q(ms.global_holds, ep, 0.35, 0.5); bu = q(ms.motion_bursts, ep, 1.0); rh = q(ms.rhythm, cuts, ep)
modes = style["build_defaults"]["page_background"]["modes"]; rt = style["rhythm"]; cl = style["colors"]
rows = [  # (nhãn, đo được, khoảng [min, max] của 4 clip gốc)
    ("nền tint (tỉ lệ khung)", None if pg is None else pg["tint_frame_share"], modes["tint"]["frame_share_range"]),
    ("nền trắng (tỉ lệ khung)", None if pg is None else pg["white"]["frame_share"], modes["white"]["frame_share_range"]),
    # accent_share/ink_share dùng cùng giả định nền sáng của page_background (ms.types_palette phân biệt "mực" với nền sáng):
    # nền tối không sập nhưng ra số vô nghĩa (gần 1.0), nên N theo cùng điều kiện pg is None.
    ("điểm ảnh xanh nhấn", None if pg is None else allp["accent_share"], [cl["accent_pixel_share"]["min"], cl["accent_pixel_share"]["max"]]),
    ("điểm ảnh mực", None if pg is None else allp["ink_share"], [cl["ink_pixel_share"]["min"], cl["ink_pixel_share"]["max"]]),
    ("đợt chuyển động / phút", bu["per_min"], [rt["bursts_per_min"]["min"], rt["bursts_per_min"]["max"]]),
    ("độ dài đợt trung vị (s)", bu["len_median_s"], [rt["burst_len_median_s"]["min"], rt["burst_len_median_s"]["max"]]),
    ("khung đứng yên (E<0.1)", en["frac_frames_still(E<0.1)"], [rt["still_frame_share_E_lt_0.1"]["min"], rt["still_frame_share_E_lt_0.1"]["max"]]),
    ("giữ trung vị (s)", ho["median_s"], [rt["hold_median_s"]["min"], rt["hold_median_s"]["max"]]),
    ("phần clip ở trạng thái giữ", ho["share_of_clip"], [rt["hold_share_of_clip"]["min"], rt["hold_share_of_clip"]["max"]]),
    ("độ dài cảnh trung vị (s)", rh["len_median"], [rt["shot_len_p10"]["median"], rt["shot_len_p90"]["median"]]),   # p10-p90 của clip 1 (n=1)
]
out = {"src": src, "size": [P["width"], P["height"]], "fps": P["fps"], "duration_s": round(T, 2), "structural_problems": bad, "rows": []}
print("style-check %s  %sx%s %sfps %.1fs  (V trong khoảng 4 clip gốc, T thấp, C cao; báo cáo, không phải cổng)" % (os.path.basename(src), P["width"], P["height"], round(P["fps"]), T))
for lab, v, (lo, hi) in rows:
    if v is None: out["rows"].append({"token": lab, "value": None, "range": [lo, hi], "flag": "N"}); print("  %-28s %8s  [%.3f-%.3f]  N (không đo được: nền không sáng, đo DNA của preset giả định nền sáng)" % (lab, "n/a", lo, hi)); continue
    f = "V" if lo <= v <= hi else ("T" if v < lo else "C"); out["rows"].append({"token": lab, "value": v, "range": [lo, hi], "flag": f})
    print("  %-28s %8.3f  [%.3f-%.3f]  %s" % (lab, v, lo, hi, f))
nv = sum(r["flag"] == "V" for r in out["rows"]); nn = sum(r["flag"] == "N" for r in out["rows"]); out["in_range"] = "%d/%d" % (nv, len(rows) - nn); out["not_measurable"] = nn
print("  trong khoảng: %s%s" % (out["in_range"], ("  SAI CẤU TRÚC: " + "; ".join(bad)) if bad else ""))
if opt("--json"): json.dump(out, open(opt("--json"), "w"), ensure_ascii=False, indent=1)
sys.exit(1 if bad else 0)
