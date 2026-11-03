// Hình morph dùng chung cho s06 và s15 (mục 5 / morph). Gốc dùng MỘT đoạn morph (tròn -> sao -> blob -> vuông -> chữ G, cùng bóng ma)
// ở cả hai cảnh: dãy chiều cao hình theo khung của s15 f24..f57 trùng s06 f5..f38 (lệch 19 khung, kể cả nhịp rung 5%/khung); xem SPEC "Morph (mục 5)".
// Mọi thứ là HÀM THUẦN của thời gian đoạn morph tc (giây, tc = (f - 1)/30 với f là khung của s06): không trạng thái tích luỹ, seek an toàn.
//   Morph.ROWS   bảng [khung, tâm bbox x, tâm bbox y, rộng, cao] của hình cam (mặt nạ, đo bằng measure_morph.py table), tọa độ s06 (tâm 540)
//   Morph.frame(tc, dx, TR, f) -> mảng điểm của hình: trạng thái morph tại tc theo lịch TR, co giãn về bbox đo ở khung f của s06, dời dx
//   Morph.ghost(f)          -> khoảng cách (px, gần mép nhất trước) từ mép trên hình tới từng bóng ma ở khung f của s06 (đo `ghost`/`gstack` ở cột x 330 và 750): bóng ma là bản của hình hiện tại dịch lên đúng khoảng đó
//   Morph.ghostW(j, n)      -> [giãn ngang, dời ngang px] của bóng ma thứ j trong chồng n nét
//   Morph.d(pts)            -> chuỗi path SVG
(function () {
  const N = 220, STROKE = 9, rad = d => (d * Math.PI) / 180;
  function resample(poly, n) {
    const m = poly.length, cum = [0];
    for (let i = 0; i < m; i++) { const a = poly[i], b = poly[(i + 1) % m]; cum.push(cum[i] + Math.hypot(b[0] - a[0], b[1] - a[1])); }
    const L = cum[m], out = []; let k = 0;
    for (let i = 0; i < n; i++) {
      const d = (i * L) / n; while (cum[k + 1] < d) k++;
      const a = poly[k], b = poly[(k + 1) % m], f = (d - cum[k]) / (cum[k + 1] - cum[k] || 1);
      out.push([a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f]);
    }
    return out;
  }
  const circle = []; for (let i = 0; i < 360; i++) { const a = rad(i - 90); circle.push([385 * Math.cos(a), 385 * Math.sin(a)]); }
  // sao 5 cánh: R 460, r 213, dịch xuống 41 (khớp IoU 0.93 vào mặt nạ gốc, measure_morph.py gfit 11 12; bản cũ r 215 R 450 cho diện tích +34%)
  const star = []; for (let i = 0; i < 10; i++) {
    const a = rad(i * 36 - 90), r = i % 2 ? 213 : 460;
    star.push([r * Math.cos(a) + (i % 3) * 4, r * Math.sin(a) + 41 + ((i * 7) % 5) * 3]);
  }
  const blob = []; for (let i = 0; i < 360; i++) {
    const a = rad(i - 90), r = 375 * (1 + 0.075 * Math.sin(2 * a + 0.8) + 0.05 * Math.sin(3 * a + 2.1));
    blob.push([r * Math.cos(a) * 1.02, r * Math.sin(a) * 0.98]);
  }
  const sq = []; for (let i = 0; i < 360; i++) {
    const a = rad(i - 90), c = Math.cos(a), s = Math.sin(a), n = 5;
    const r = 395 / Math.pow(Math.pow(Math.abs(c), n) + Math.pow(Math.abs(s), n), 1 / n);
    const x = r * c, y = r * s, t = rad(-2.5);
    sq.push([x * Math.cos(t) - y * Math.sin(t), x * Math.sin(t) + y * Math.cos(t)]);
  }
  // chữ G nghiêng đậm (đường viền kín). Tham số khớp IoU 0.865 vào mặt nạ gốc s06 f33-f34 (gfit 33 34): ngoài (a,b), trong (ai,bi), bậc (xb, yb, góc th), đầu mút te, nghiêng sh.
  // Bản cũ a 330 b 430 ai 175 bi 280 (vòng mảnh, diện tích -17%).
  const G = []; { const a = 390.8, b = 404.5, ai = 164.1, bi = 223.7, th = 29.15, xb = 5.3, yb = -18.6, te = -28.5, sh = 0.209;
    for (let p = -90; p <= te; p += 2) G.push([a * Math.cos(rad(p)), b * Math.sin(rad(p))]);
    for (let p = te; p >= -336; p -= 3) G.push([ai * Math.cos(rad(p)), bi * Math.sin(rad(p))]);
    const iy = bi * Math.sin(rad(th));
    G.push([ai * Math.cos(rad(th)), iy], [xb, iy], [xb, yb], [a * 0.985, yb]);
    for (let p = -2; p <= 268; p += 3) G.push([a * Math.cos(rad(p)), b * Math.sin(rad(p))]);
    for (let i = 0; i < G.length; i++) G[i] = [G[i][0] - sh * G[i][1], G[i][1]];
  }
  const SP = [circle, star, blob, sq, G].map(p => resample(p, N));

  // bbox từng khung đo trên gốc (mặt nạ cam đã bỏ nét viền 9px): [khung, tâm x, tâm y, rộng, cao]; f4 = chấm 227px, f5 = tròn 763
  const ROWS = [[4,540,960,227,227],[5,540,960,763,763],[6,538,974,873,847],[7,540,960,807,805],[8,540,960,785,787],[9,556,956,755,783],[10,542,930,755,723],[11,538,926,745,703],[12,538,925,745,702],[13,540,926,783,729],[14,540,926,796,744],[15,540,924,759,719],[16,540,924,747,705],[17,539,926,746,703],[18,537,924,750,707],[19,526,926,761,723],[20,528,950,768,751],[21,530,953,775,762],[22,530,954,776,763],[23,529,954,824,805],[24,529,954,822,805],[25,532,954,811,795],[26,538,958,777,775],[27,540,960,751,751],[28,540,960,747,747],[29,540,960,768,768],[30,542,960,806,803],[31,566,947,833,766],[32,554,1162,469,491],[33,426,964,643,805],[34,426,962,643,805],[35,419,970,676,831],[36,418,972,684,835],[37,424,964,655,815],[38,428,962,653,805]];

  function mix(a, b, f) { return a.map((p, i) => [p[0] + (b[i][0] - p[0]) * f, p[1] + (b[i][1] - p[1]) * f]); }
  // lịch morph TR = [[t0, dài, tên ease]]: trạng thái liên tục s = k + ease(u) của đoạn k đang chạy
  function state(tc, TR) {
    let s = 0;
    for (let k = 0; k < TR.length; k++) {
      const u = Math.min(1, Math.max(0, (tc - TR[k][0]) / TR[k][1]));
      if (u > 0) s = k + gsap.parseEase(TR[k][2])(u);
    }
    const i = Math.min(SP.length - 2, Math.floor(s)); return mix(SP[i], SP[i + 1], s - i);
  }
  function row(f) {
    return ROWS[Math.min(ROWS.length - 1, Math.max(0, f - ROWS[0][0]))];
  }
  function frame(tc, dx, TR, f) {
    const p = state(tc, TR), r = row(f); let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    for (const q of p) { if (q[0] < x0) x0 = q[0]; if (q[0] > x1) x1 = q[0]; if (q[1] < y0) y0 = q[1]; if (q[1] > y1) y1 = q[1]; }
    const sx = (r[3] + STROKE) / (x1 - x0), sy = (r[4] + STROKE) / (y1 - y0), bx = (x0 + x1) / 2, by = (y0 + y1) / 2;
    return p.map(q => [r[1] + dx + (q[0] - bx) * sx, r[2] + (q[1] - by) * sy]);
  }
  // Bóng ma đo trên gốc (s06; s15 trùng với lệch 19 khung): khoảng cách từ mép trên hình tới nét ma, trung vị hai cột x 330 và 750 (measure_morph.py ghost, gstack).
  // Ở khoảng sao (f15–f18) là chồng 5 nét CÁCH ĐỀU 50 px (±3) và ĐỨNG YÊN so với mép hình; dựng dần f11–f15, sụp ở f19–f20, sau đó còn 1 nét cách 38–66 px (blob, vuông, G).
  const GH = {6:[48],7:[51],8:[72],9:[66,145],10:[73,160],11:[64,214],12:[53,112,257],13:[46,95,155],14:[43,93,142,200],15:[50,99,148,198,255],16:[52,101,150,199,249],17:[52,101,150,199,248],18:[48,96,145,193,243],19:[48,96,145,189],20:[53],21:[42,62],22:[44,70],23:[45,66],24:[45],25:[47],26:[44],27:[64],28:[66],29:[57],30:[42],31:[64],32:[],33:[64],34:[38,75],35:[45],36:[43,86],37:[43,86],38:[43,86]};
  // bảng đo từ MẶT NẠ cam (mép trong của viền 9px); remake đo cùng cách cho khoảng cách lớn hơn đúng 5 px (đo lại f15–f18 ở x 330: 256/206/157/108 so với 251/200/151/102), nên trừ 5.
  function ghost(f) { return (GH[Math.min(38, f)] || []).map(v => Math.max(1, v - 5)); }
  // Bóng ma của sao (chồng >= 3 nét) còn LOE NGANG: ở hàng y 1100 (s06 f16) khoảng cách nét ma tới mép trái là 19/51/82/114/146 px (cách nhau 32) còn bên phải 15/27/38/51/63 (cách nhau 12, như dịch dọc thuần);
  // ở hàng y 700 bóng ma ngoài cùng trải x 38..986 so với 160..920 của remake chỉ dịch dọc. Mô hình: nét thứ j (0 = gần nhất) giãn ngang 5% mỗi bước quanh tâm và dời trái 5.6 px mỗi bước
  // (ngoài cùng: x1.25, -28 px) — khớp hai hàng trong ±20 px; các hình sau (1-2 nét) chưa đo nên không giãn.
  function ghostW(j, n) { return n >= 3 ? [1 + 0.05 * (j + 1), -5.6 * (j + 1)] : [1, 0]; }
  function d(pts) { return "M" + pts.map(p => p[0].toFixed(1) + " " + p[1].toFixed(1)).join("L") + "Z"; }
  window.Morph = { ROWS, frame, ghost, ghostW, d, N };
})();
