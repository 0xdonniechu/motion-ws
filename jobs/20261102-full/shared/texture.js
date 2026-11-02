// texture.js — hạt và halftone vẽ bằng Canvas cho HyperFrames. Không Math.random, không rAF, không trạng thái tích luỹ:
// mọi khung là hàm thuần của (tham số, thời gian) nên seek tiến/lùi đều cho cùng một hình. Số đo lấy từ source.mp4 (xem SPEC.md, mục 3).
// Dùng: <script src="texture.js"> (symlink ../../shared/texture.js, như boil.js); gọi từ onUpdate của tween GSAP.
//
//   TX.hash(i, j, s)                  0..1 xác định
//   TX.dotField(cx, F)                trường hạt vuông gợn sóng (s02 -> s03), F = { T, reveal, conv, fade, ribFade, lines }
//   TX.rippleGrid(cx, t)              gợn sóng halftone cam toàn khung (s03, sau cụm thẻ)
//   TX.bars(cx, t)                    vệt dọc xám của s03 (vẽ sau rippleGrid trên cùng canvas)
//   TX.cellRing(cx, T, keys)          vòng tối halftone theo ô 46px (vignette s02); keys: [[giây, cy, rx, ry, [d tại TX.RK]], ...]
(function (g) {
  const TX = {};
  TX.hash = function (i, j, s) {
    let h = (i * 374761393 + j * 668265263 + (s || 0) * 2147483647) | 0;
    h = (h ^ (h >>> 13)) * 1274126177 | 0;
    return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
  };
  const hash = TX.hash, smooth = p => p * p * (3 - 2 * p), clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  // ---------- trường hạt (đo ở s02 f35–f45) ----------
  // Lưới 26 x 39 px, ô vuông 10–19 px, màu tối 80% / cam 13% / xanh 4.5% / xám 2.5%.
  // Dịch chuyển theo sóng phẳng (đo bằng bám hạt từng khung, 30fps):
  //   dy = 34 sin(0.0170 x + 0.0055 y + 8.74 T - 0.87)   (px, T = giây từ đầu s02)
  //   dx = 11.7 sin(0.0130 y + 8.74 T + 1.89) - 84 max(0, T - 1.17)   (trôi trái 2.8 px/khung)
  const PX = 26, PY = 39, C0 = -2, COLS = 46, ROWS = 53;
  const COL = ["#37322a", "#c45a33", "#536ff8", "#6f685e"];
  TX.GY = 967; TX.C0 = 0.55; // tâm dọc chữ GSAP; conv cuối s02 = conv đầu s03
  let TG = null;
  TX.buildTargets = function (fontOk) {
    if (TG) return TG;
    if (fontOk === false) return null;
    const oc = document.createElement("canvas"); oc.width = 1080; oc.height = 700;
    const o = oc.getContext("2d"), tk = Math.tan(9 * Math.PI / 180);
    o.fillStyle = "#000"; o.font = "400 410px Anton"; o.textAlign = "center"; o.textBaseline = "middle";
    o.setTransform(1, 0, tk, 1, 0, 0);
    o.fillText("GSAP", 540 - 350 * tk, 350);
    const d = o.getImageData(0, 0, 1080, 700).data;
    let x0 = 1e9, x1 = -1, y0 = 1e9, y1 = -1;
    for (let y = 0; y < 700; y += 2) for (let x = 0; x < 1080; x += 2) if (d[(y * 1080 + x) * 4 + 3] > 128) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
    const ox = 540 - (x0 + x1) / 2, oy = TX.GY - (y0 + y1) / 2, NT = 1400;
    let pts = [];
    for (let P = 14; P >= 4; P--) {
      pts = [];
      for (let y = y0; y <= y1; y += P) for (let x = x0; x <= x1; x += P) if (d[(y * 1080 + x) * 4 + 3] > 128) pts.push([x + ox, y + oy]);
      if (pts.length >= NT) break;
    }
    const idx = pts.map((_, k) => k).sort((a, b) => hash(a, 7, 0) - hash(b, 7, 0) || a - b);
    TG = idx.map(k => pts[k]);
    return TG;
  };

  TX.dotField = function (cx, F) {
    cx.clearRect(0, 0, 1080, 1920);
    const T = F.T, tg = TG;
    const half = F.reveal == null ? 99999 : F.reveal; // nửa cao dải hạt quanh y = 1200 (s02 f31–f35: mở dần từ giữa ra)
    const drift = -84 * Math.max(0, Math.min(T, 1.5) - 1.17); // đo trôi trái 2.8 px/khung ở f36–f46 (T 1.17–1.5); ngoài đó không có số đo nên giữ nguyên
    if (F.fade < 0.999 || F.ribFade < 0.999) {
      for (let j = 0; j < ROWS; j++) for (let i = 0; i < COLS; i++) {
        const n = j * COLS + i;
        const h = hash(i, j, 1), r = hash(i, j, 2), hs = hash(i, j, 3);
        if (hash(i, j, 4) < 0.04) continue; // lỗ thưa
        const bx = (i + C0) * PX + 6 * (hash(i, j, 5) - 0.5), by = (j - 1) * PY + 6 * (hash(i, j, 6) - 0.5);
        if (Math.abs(by - 1200) > half + 140 * h) continue;
        let x = bx + 11.7 * Math.sin(0.013 * by + 8.74 * T + 1.89) + drift;
        let y = by + 34 * Math.sin(0.0170 * bx + 0.0055 * by + 8.74 * T - 0.87);
        let s = Math.round(10 + 9 * hs), col = COL[r < 0.80 ? 0 : r < 0.93 ? 1 : r < 0.975 ? 2 : 3], a = 1;
        let toText = false;
        if (F.conv > 0 && tg) {
          const p = clamp((F.conv - 0.35 * h) / 0.65, 0, 1), e = smooth(p);
          if (i % 4 !== 2) { // 3/4 số cột lưới về chữ GSAP; cột i%4==2 ở lại thành cột chấm dọc (đo: khoảng cột 105px ≈ 4×26, hàng 39px)
            toText = true;
            const tp = tg[n % tg.length], ey = smooth(Math.min(1, p * 2));
            x += (tp[0] + 3 * Math.sin(n + T * 9) * (1 - e) - x) * e; y += (tp[1] + 3 * Math.cos(n * 1.7 + T * 9) * (1 - ey) - y) * ey;
            s += (6 - s) * e;
            if (e > 0.3) col = hash(n, 3, 9) < 0.82 ? "#c45a33" : "#37322a";
          }
        }
        a = toText ? 1 - F.fade : 1 - F.ribFade;
        if (!toText) a *= clamp((y - 120) / 380, 0, 1); // mờ dần về phía mép trên
        if (a <= 0.01) continue;
        cx.globalAlpha = a; cx.fillStyle = col;
        cx.fillRect(x - s / 2, y - s / 2, s, s);
      }
      cx.globalAlpha = 1;
    }
    if (F.lines > 0.01) { // sợi chấm ngang (s03 f6–f12): hàng chấm 11px bước 26px uốn quanh chữ
      cx.fillStyle = "#37322a";
      for (let k = 0; k < 14; k++) {
        const y0 = 160 + k * 120;
        for (let x = 0; x < 1080; x += 26) {
          const y = y0 + 52 * Math.sin(x * 0.007 + k * 0.55 + T * 6) + 28 * Math.sin(x * 0.019 - k * 0.8 - T * 4);
          if (hash(x / 26 | 0, k, 8) > F.lines) continue;
          cx.fillRect(x - 5, y - 5, 11, 11);
        }
      }
    }
  };

  // ---------- vòng tối halftone (vignette s02 f11–f22): ô 46px, bo 9, ô sáng #dbd5ce -> gần đen ----------
  // Mức tối trung bình ô d(x,y) = nội suy tuyến tính theo r = hypot((x-540)/rx, (y-cy)/ry) tại các mốc TX.RK (vòng elip có lõi rỗng, dày dần,
  // trượt xuống). Mỗi khung gốc một lần khớp riêng (bậc thang theo khung, không nội suy giữa các khung); khớp trên ô không bị thẻ/chữ che.
  // Trong vùng tối cả ô lẫn khe đều gần đen (đo: khe ≈ 16/255), nên cả hai tối theo cùng mức.
  TX.RK = [0, 0.4, 0.6, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 1.9, 3.0];
  TX.cellRing = function (cx, T, keys) {
    cx.clearRect(0, 0, 1080, 1920);
    let k = null;
    for (let q = 0; q < keys.length; q++) if (T >= keys[q][0] - 1e-6) k = keys[q];
    if (!k) return;
    const cy = k[1], rx = k[2], ry = k[3], v = k[4], RK = TX.RK;
    for (let j = 0; j < 42; j++) for (let i = 0; i < 24; i++) {
      const r = Math.hypot(((i + 0.5) * 46 - 540) / rx, ((j + 0.5) * 46 - cy) / ry);
      let d = v[v.length - 1];
      if (r < RK[RK.length - 1]) { let q = 1; while (RK[q] < r) q++; d = v[q - 1] + (v[q] - v[q - 1]) * (r - RK[q - 1]) / (RK[q] - RK[q - 1]); }
      const m = clamp(1.116 * d - 0.026, 0, 1); // d = 1 - L/232 trung bình ô+khe  ->  mức tối m của ô
      if (m < 0.02) continue;
      const c = (a, b) => Math.round(a + (b - a) * m);
      cx.fillStyle = `rgb(${c(240, 16)},${c(236, 14)},${c(230, 12)})`; cx.fillRect(i * 46, j * 46, 46, 46);
      cx.fillStyle = `rgb(${c(219, 20)},${c(213, 18)},${c(206, 15)})`;
      cx.beginPath(); cx.roundRect(i * 46 + 4, j * 46 + 5, 38, 36, 9); cx.fill();
    }
  };

  // ---------- gợn sóng halftone cam (s03 f34–f45): lưới ô vuông bo 78px, cỡ ô đổi theo bán kính, độ đậm tăng dần ----------
  // Đo từ ô cam của gốc (tâm (540,950), pha lưới x=24.7+78i, y=20.2+78j, màu lõi #c4430c; F = số khung file, t=(F−1)/30):
  //  - ô không dịch chuyển (|d| < 1px/khung), chỉ đổi cỡ (±4–8px/khung) và độ đậm;
  //  - độ đậm (r−b tại tâm ô hàng dưới, 12→180): f34 .20, f35 .36, f36 .52, f37 .67, f38 .78, f39 .88, f40 .97 (tăng đồng loạt theo mọi x);
  //  - mặt sóng (ô bắt đầu hiện) Rf ≈ 870 + 130·(F−34) px; gờ sóng (ô to nhất, nền 14px, +14px, σ≈170) ở 540 + 120·(F−34) px;
  //  - sóng thứ hai từ F=37 (đỉnh +34px ở F=40, bán kính 250→540 từ F=37→41).
  const RB_KEYS = [[36, 0, 250], [37, 15, 250], [38, 24, 270], [39, 31, 280], [40, 34, 380], [41, 30, 540], [42, 25, 700], [43, 20, 860], [46, 8, 1200]];
  const AL_KEYS = [[33, 0], [34, 0.2], [35, 0.36], [36, 0.52], [37, 0.67], [38, 0.78], [39, 0.88], [40, 0.97], [46, 1]];
  const lerpKeys = (K, F, i) => { if (F <= K[0][0]) return K[0][i]; for (let q = 1; q < K.length; q++) if (F <= K[q][0]) return K[q - 1][i] + (K[q][i] - K[q - 1][i]) * (F - K[q - 1][0]) / (K[q][0] - K[q - 1][0]); return K[K.length - 1][i]; };
  // lưới xám nhạt cùng pitch 78 trước khi cam tới (đo: tâm ô tối hơn khe 9.5/12.9/12.9/12.7/18/20/25/26 mức xám ở f26–f33, trung tính, không cam)
  const GR_KEYS = [[23, 0], [24, 0.45], [25, 0.4], [26, 0.24], [29, 0.32], [30, 0.45], [31, 0.5], [32, 0.63], [33, 0.65], [34, 0.65], [36, 0]];
  TX.rippleGrid = function (cx, t) {
    cx.clearRect(0, 0, 1080, 1920);
    const F = t * 30 + 0.3, al = lerpKeys(AL_KEYS, F, 1), gal = lerpKeys(GR_KEYS, F, 1);
    if (gal > 0.01) {
      cx.globalAlpha = gal; cx.fillStyle = "#cfc9bf";
      for (let j = -1; j < 26; j++) for (let i = -1; i < 15; i++) { cx.beginPath(); cx.roundRect(24.7 + 78 * i - 23, 20.2 + 78 * j - 23, 46, 46, 9); cx.fill(); }
      cx.globalAlpha = 1;
    } // +0.3 (không phải +1): cảnh bắt đầu ở khung 82.5, compose làm tròn nửa khung
    if (al <= 0 && F < 29.5 && gal <= 0.01) return;
    const Rf = 870 + 130 * (F - 34), RA = 540 + 120 * (F - 34), CX = 540, CY = 950;
    const A2 = F >= RB_KEYS[0][0] ? lerpKeys(RB_KEYS, F, 1) : 0, R2 = lerpKeys(RB_KEYS, F, 2);
    // vòng cam nhạt dày ~34px quanh cụm thẻ (gốc f30–f39, đỉnh phổ bán kính của điểm ảnh cam nhạt): hai vòng gần như đứng yên ở ~450 và ~510→550,
    // một vòng lan ra 270 → 370 → 470 → 650 → 810 → 930 → 1070 (f31–f37) rồi mờ
    const RINGS = [[[30, 450], [37, 450]], [[30, 510], [34, 510], [35, 550], [39, 540]], [[31, 270], [32, 370], [33, 470], [34, 650], [35, 810], [36, 930], [37, 1070]]];
    const RING_A = [[30, 0.25, 37, 38.5], [30, 0.25, 39, 40], [31, 0.25, 36.5, 37.5]];
    cx.strokeStyle = "#c4430c"; cx.lineWidth = 34;
    RINGS.forEach((K, n) => {
      const [a0, am, a1, a2] = RING_A[n]; if (F < a0 - 0.5 || F > a2) return;
      const rad = lerpKeys(K, F, 1), fade = F < a0 ? 0.5 : F <= a1 ? 1 : clamp(1 - (F - a1) / (a2 - a1), 0, 1);
      cx.globalAlpha = am * fade; cx.beginPath(); cx.arc(CX, CY - 70, rad, 0, Math.PI * 2); cx.stroke();
    });
    cx.fillStyle = "#c4430c";
    for (let j = -1; j < 26; j++) for (let i = -1; i < 15; i++) {
      const x = 24.7 + 78 * i, y = 20.2 + 78 * j, r = Math.hypot(x - CX, y - CY);
      let sz = 14 + 14 * Math.exp(-(((RA - r) / 170) ** 2)) + A2 * Math.exp(-(((r - R2) / 140) ** 2));
      const a = al * clamp((Rf - r) / 60, 0, 1);
      if (sz < 2 || a < 0.02) continue;
      cx.globalAlpha = a;
      cx.beginPath(); cx.roundRect(x - sz / 2, y - sz / 2, sz, sz, sz * 0.2); cx.fill();
    }
    cx.globalAlpha = 1;
  };

  // vệt dọc xám (s03 f19–f24, đo từ thành phần cao ≥250px, rộng 6–40px ở y>700): x, rộng, y trên, y dưới; xám #a7a39b đậm dần 0.15→0.96 trong f19→f23, hết ở f24;
  // thêm một vệt cam nhạt (741, rộng 36, y 700–1360) ở f23–f24
  const BARS = [[0, 9, 1292, 1920], [64, 36, 1366, 1920], [500, 28, 1303, 1897], [595, 30, 1302, 1780], [671, 13, 1426, 1920], [915, 12, 1368, 1889]];
  TX.bars = function (cx, t) {
    const F = t * 30 + 0.3, a = lerpKeys([[18.5, 0], [19, 0.15], [20, 0.38], [21, 0.62], [22, 0.8], [23, 0.96], [24, 0.35], [24.6, 0]], F, 1);
    if (a > 0.01) { cx.fillStyle = "#a7a39b"; cx.globalAlpha = a; BARS.forEach(b => cx.fillRect(b[0], b[2], b[1], b[3] - b[2])); }
    const o = lerpKeys([[22.5, 0], [23, 0.9], [24, 0.9], [24.6, 0]], F, 1);
    if (o > 0.01) { cx.fillStyle = "#e3b095"; cx.globalAlpha = o; cx.fillRect(741, 700, 36, 660); }
    cx.globalAlpha = 1;
  };

  // vòng bấm chuột s03 (f21–f24, đo bằng bỏ phiếu vòng tròn trên điểm ảnh cam): tâm (540,900), bán kính 46 (ước từ ảnh) → 201 → 531 → 903 px ở f21 → f24,
  // dày ~25px, màu đặc #c14212 (193,66,18), hết ở f25; ô vuông đen nghiêng ~20° (≈38px) ở tâm ở f21–f22.
  TX.clickRing = function (cx, t) {
    const F = t * 30 + 0.3;
    if (F < 20.7 || F > 24.6) return;
    const r = lerpKeys([[21, 46], [22, 201], [23, 531], [24, 903]], F, 1);
    cx.strokeStyle = "#c14212"; cx.lineWidth = 25; cx.globalAlpha = 1; cx.beginPath(); cx.arc(540, 900, r, 0, Math.PI * 2); cx.stroke();
    if (F < 22.6) { cx.save(); cx.translate(540, 900); cx.rotate(20 * Math.PI / 180); cx.fillStyle = "#14110f"; cx.fillRect(-19, -19, 38, 38); cx.restore(); }
  };
  g.TX = TX;
})(window);
