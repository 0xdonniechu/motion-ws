// boil.js — "boil" (nhảy nét kiểu vẽ tay) xác định cho HyperFrames. Không dùng Math.random; mọi giá trị là hàm thuần của thời gian
// (hash có seed) nên seek-safe. Đặt vào CSS `translate` / `rotate` (thuộc tính riêng của trình duyệt) để KHÔNG đè lên transform của GSAP.
// Mỗi phần tử chỉ nên có một lời gọi boil (hai lời gọi trên cùng phần tử sẽ ghi đè nhau).
//
// boil(tl, targets, opts)
//   tl       timeline GSAP chính của scene
//   targets  selector | phần tử | mảng phần tử
//   opts.start, opts.end   khoảng thời gian (giây, theo đồng hồ của tl); ngoài khoảng: offset = 0
//   opts.mode  "step" (mặc định): mỗi `step` giây nhảy sang offset mới ngẫu nhiên theo hash, biên độ ±amp (x), ±ampY (y, mặc định = amp), ±rot (độ)
//              "saw": răng cưa đo từ gốc — trôi theo hướng dir (−1 = lên) với lũy thừa `power` trong mỗi chu kỳ rồi giật về 0.
//                     chu kỳ đều: `period`; hoặc liệt kê `cycles: [[t0, dài, biên độ], ...]` (biên độ px theo trục y, hoặc x nếu axis:"x")
//   opts.seed  hạt giống (mỗi phần tử lệch thêm chỉ số của nó; `sync:true` để mọi phần tử cùng một giá trị)
(function (g) {
  function hash(i, j, s) {
    let h = (i * 374761393 + j * 668265263 + s * 2147483647) | 0;
    h = (h ^ (h >>> 13)) * 1274126177 | 0;
    return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
  }
  function offset(o, t, idx) {
    if (t < o.start || t >= o.end) return [0, 0, 0];
    const rel = t - o.start, who = o.sync ? 0 : idx;
    if (o.mode === "saw") {
      let t0, len, amp;
      if (o.cycles) {
        const c = o.cycles.find(c => t >= c[0] && t < c[0] + c[1]);
        if (!c) return [0, 0, 0];
        t0 = c[0]; len = c[1]; amp = c[2];
      } else {
        const k = Math.floor(rel / o.period); t0 = o.start + k * o.period; len = o.period;
        amp = o.amp * (1 + (hash(k, who, o.seed) - 0.5) * (o.ampVar || 0));
      }
      const u = Math.min(1, Math.max(0, (t - t0) / len)), d = o.dir * amp * Math.pow(u, o.power);
      return o.axis === "x" ? [d, 0, 0] : [0, d, 0];
    }
    const k = Math.floor(rel / o.step + 1e-9);
    const ax = o.axis === "y" ? 0 : 1, ay = o.axis === "x" ? 0 : 1;
    return [ax * (hash(k, who, o.seed) - 0.5) * 2 * o.amp, ay * (hash(k, who, o.seed + 101) - 0.5) * 2 * (o.ampY == null ? o.amp : o.ampY),
      o.rot ? (hash(k, who, o.seed + 202) - 0.5) * 2 * o.rot : 0];
  }
  g.boil = function (tl, targets, opts) {
    const o = Object.assign({ mode: "step", amp: 6, ampY: null, step: 0.1, start: 0, end: 1, seed: 1, rot: 0, axis: "xy", period: 0.18, power: 2.2, dir: -1, sync: false }, opts || {});
    const list = typeof targets === "string" ? [...document.querySelectorAll(targets)] : (targets && targets.length != null && !targets.nodeType ? [...targets] : [targets]);
    const clock = { t: o.start };
    function apply() {
      list.forEach((el, i) => {
        const [x, y, r] = offset(o, clock.t, i);
        el.style.translate = (x || y) ? `${x.toFixed(2)}px ${y.toFixed(2)}px` : "";
        el.style.rotate = r ? `${r.toFixed(2)}deg` : "";
      });
    }
    tl.fromTo(clock, { t: o.start }, { t: o.end, duration: Math.max(0.001, o.end - o.start), ease: "none", onUpdate: apply, immediateRender: false }, o.start);
    return clock;
  };
})(window);
