"""Khớp cạnh phải (cạnh dẫn) của pill tabs bằng back.out(s) có độ trễ và thời lượng tự do (lưới 0.1 khung / 1 khung / s 0.1). Đọc tmp/tabs_fit.json_tmp.raw.json do measure_tabs_cursor.py sinh."""
import json, math, sys
r = json.load(open(sys.argv[1])); pill = {round(t, 3): p for t, p in r["pill_series"]}; ts = sorted(pill)
back = lambda s: (lambda u: 1 + (s + 1) * (u - 1) ** 3 + s * (u - 1) ** 2)
out = {}
for name, (a, b, x0, x1, edge) in {"tab1_to_2_right": (14.30, 15.0, 408, 655, 1), "tab2_to_3_right": (15.70, 16.5, 655, 902, 1)}.items():
    pts = [(t, (pill[t][edge] - x0) / (x1 - x0)) for t in ts if a <= t <= b]; best = None
    for k in range(0, 200):
        t0 = a + k * 0.1 / 30
        for D in [d / 30 for d in range(2, 14)]:
            for s in [x / 10 for x in range(0, 40)]:
                f = back(s); e = math.sqrt(sum(((0 if t < t0 else f(min((t - t0) / D, 1))) - p) ** 2 for t, p in pts) / len(pts))
                if best is None or e < best[0]: best = (e, t0, D, s)
    out[name] = {"rmse": round(best[0], 3), "t0": round(best[1], 3), "dur_s": round(best[2], 3), "frames": round(best[2] * 30, 1), "s": best[3], "overshoot_measured": round(max(p for t, p in pts) - 1, 3)}
print(json.dumps(out, indent=1))
