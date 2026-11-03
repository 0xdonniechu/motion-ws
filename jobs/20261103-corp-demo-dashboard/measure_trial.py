# Đo đoạn thử corp-demo-dashboard theo DNA corporate-motion, bằng các hàm của jobs/20261028-230040/measure_style.py (không sửa file đó).
#   uvx --with numpy python -I -B jobs/20261103-corp-demo-dashboard/measure_trial.py [--src preview/trial-a.mp4]
#   thêm --full: đo clip đủ 41s (preview/full-a.mp4, cuts-full.json) kèm chữ gõ/đứng yên của beat 4-8; ghi tmp/full_measured.json
# Đọc: preview/trial-a.mp4 (hoặc --src), cuts.json (mốc cắt theo thiết kế). Ghi: tmp/energy*.json, tmp/*_measured.json (tmp/ không commit).
import sys, os, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ms", os.path.join(HERE, "../20261028-230040/measure_style.py"))
ms = importlib.util.module_from_spec(spec); spec.loader.exec_module(ms)
import numpy as np

FULL = "--full" in sys.argv
src = os.path.join(HERE, "preview/full-a.mp4" if FULL else "preview/trial-a.mp4")
if "--src" in sys.argv: src = os.path.abspath(sys.argv[sys.argv.index("--src") + 1])
cuts = os.path.join(HERE, "cuts-full.json" if FULL else "cuts.json"); ep = os.path.join(HERE, "tmp/energy_full.json" if FULL else "tmp/energy.json")
style = json.load(open(os.path.join(HERE, "../../presets/corporate-motion/style.json")))
P = ms.probe(src); T = float(P["duration"]); FPS = ms.FPS
out = {"src": os.path.relpath(src, HERE), "size": [P["width"], P["height"]], "fps": P["fps"], "duration_s": round(T, 3)}
q = ms._quiet

# ---- màu: nền tint/trắng, xanh nhấn, mực, bề mặt thẻ
pg = ms.page_background(src, T); sf = ms.surface_color(src, T); allp = ms.types_palette(src, {"all": [[0.0, T]]}, 8)["all"]
out["colors"] = {"tint_frame_share": pg["tint_frame_share"], "white_frame_share": pg["white"]["frame_share"], "tint_colour": pg["bg"], "white_colour": pg["white"]["colour"], "surface_pixel_share": sf["pixel_share"],
                 "accent_pixel_share": allp["accent_share"], "ink_pixel_share": allp["ink_share"], "accent_clusters": allp["accent"], "ink_clusters": allp["ink"]}

# ---- card_slide_in: mép trên thẻ trắng (mặt nạ như instances.json của clip 1: light 252, minrow 20), B1 từ khung 0 và B3 sau bar-wipe
def ease(t0, t1, box, mask, axis, label, pre=None, zero_start=False):
    rows = ms.series(src, t0, t1, box, mask)
    if zero_start:   # cột mọc từ 0: khung ngay trước khung đầu tiên có mặt nạ coi là cao 0 (khung đầu đã nảy giữa chừng thì chuẩn hoá sai)
        j = next(i for i, r in enumerate(rows) if r[2] is not None)
        if j > 0: rows[j - 1] = (rows[j - 1][0], 0, (0, 0, 0, 0))
    if pre: rows = [(pre[0], 0, (pre[1],) * 4)] + rows[1:]
    r = q(ms.ease_report, rows, axis, label=label)
    if r: r["distance_frac_of"] = ("W" if axis in ("x", "x1", "w", "cx") else "H"); r["distance_frac"] = round(abs(r["distance"]) / (1080 if axis in ("x", "x1", "w", "cx") else 1920), 3)
    return r
out["card_slide_in"] = {"B1": ease(0.0, 1.0, [0, 0, 1080, 1920], {"light": "252", "minrow": "20"}, "y", "B1 thẻ từ dưới lên"),
                        "B3": ease(8.2, 9.4, [0, 0, 1080, 1920], {"light": "252", "minrow": "20"}, "y", "B3 thẻ từ dưới lên")}
# ---- chart_pop: chiều cao cột 1..3 (mặt nạ xanh giữa #3e9cec), thẻ đã đứng yên khi cột nảy; tâm cột x = 170 + i*131.2
out["chart_pop"] = {}
for i in range(3):
    x0 = int(170 + i * 131.2) - 6
    out["chart_pop"]["bar%d" % (i + 1)] = ease(0.5, 2.2, [x0, 820, x0 + 96, 1285], {"rgb": "62,156,236,10", "minrow": "4"}, "h", "cột %d cao" % (i + 1), zero_start=True)
# ---- số đếm qua thanh chạy (B1, x1 của phần fill) và bar_fill riêng (B2)
out["number_count_up.bar_driven"] = ease(0.63, 1.9, [160, 785, 920, 818], {"rgb": "24,114,206,22", "minrow": "4"}, "x1", "B1 thanh chạy cùng số đếm", pre=(0.63, 170))   # pre: mép trái thanh = x1 lúc scaleX 0, như instances.json của clip 1
out["bar_fill"] = ease(4.7, 5.9, [250, 905, 830, 960], {"rgb": "24,114,206,22", "minrow": "4"}, "x1", "B2 bar_fill mặc định", pre=(4.7, 253))

# ---- chữ gõ: ký tự/giây = (số ký tự - 1) / (t ký tự cuối - t ký tự đầu); mực tối + xanh (lum < 150), tăng > 100 px² mỗi ký tự mới; con trỏ gắn liền nên không tăng thêm. Số ký tự đếm trong kịch bản (cả dấu cách).
def typed_speed(t0, t1, box, nchars, label):
    rows = ms.series(src, t0, t1, box, {"dark": "150", "minrow": "1"}); a = [r[1] for r in rows]; t = [r[0] for r in rows]
    first = next(i for i, v in enumerate(a) if v >= 10); last = max(i for i in range(first + 1, len(a)) if a[i] - a[i - 1] > 100)
    dur = t[last] - t[first]; return {"label": label, "t_first": round(t[first], 3), "t_last": round(t[last], 3), "chars": nchars, "chars_per_s": round((nchars - 1) / dur, 1), "frames_per_char": round(dur * FPS / (nchars - 1), 2)}
out["typed"] = [typed_speed(0.6, 2.6, [100, 290, 980, 480], 23, "B1 tiêu đề"), typed_speed(8.8, 10.6, [165, 985, 835, 1180], 23, "B3 câu chốt")]

# ---- nhịp: độ dài cảnh (mốc thiết kế), chuyển cảnh phân loại bằng luật của measure_style, năng lượng/đợt/đứng yên, chữ đứng yên
if not os.path.exists(ep): ms.energy(src, ep)
out["rhythm"] = q(ms.rhythm, cuts, ep); out["transitions"] = q(ms.transitions, src, cuts, ep)
out["energy"] = q(ms.energyprofile, ep, 1.0); out["holds"] = q(ms.global_holds, ep, 0.35, 0.5); out["bursts"] = q(ms.motion_bursts, ep, 1.0)
dw = {"B1 tiêu đề": q(ms.dwell, src, 0.6, 3.85, [100, 290, 980, 480], 0.3), "B2 câu hỏi": q(ms.dwell, src, 5.3, 7.8, [100, 1050, 980, 1230], 0.3), "B3 câu chốt": q(ms.dwell, src, 8.4, 11.8 if FULL else 12.0, [165, 790, 835, 1180], 0.3)}
if FULL:   # beat 4-8: chữ gõ (số ký tự = độ dài chuỗi bỏ dấu *) và thời gian đứng yên của khối chữ chính
    out["typed"] += [typed_speed(12.3, 14.1, [100, 290, 980, 480], 29, "B4 tiêu đề"), typed_speed(30.3, 32.5, [100, 290, 980, 560], 38, "B7 quy tắc")]
    dw.update({"B4 tiêu đề": q(ms.dwell, src, 14.0, 16.9, [100, 290, 980, 470], 0.3), "B5 ba câu hỏi": q(ms.dwell, src, 22.9, 24.8, [90, 520, 990, 1260], 0.3), "B6 câu kết": q(ms.dwell, src, 27.3, 29.8, [100, 1230, 980, 1400], 0.3),
               "B7 quy tắc": q(ms.dwell, src, 32.5, 34.8, [100, 290, 980, 560], 0.3), "B8 câu hỏi": q(ms.dwell, src, 36.8, 40.9, [100, 1040, 980, 1180], 0.3)})
hold = [h["dur_s"] for v in dw.values() for h in v if h["dur_s"] >= 1.0]
out["text_dwell"] = {"per_text": dw, "holds_ge_1s": {"n": len(hold), "median_s": round(float(np.median(hold)), 2) if hold else None}}

os.makedirs(os.path.join(HERE, "tmp"), exist_ok=True); json.dump(out, open(os.path.join(HERE, "tmp/full_measured.json" if FULL else "tmp/trial_measured.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
