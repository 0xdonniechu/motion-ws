// Thử tua (seek) cho một composition HyperFrames dựng bằng kit: trạng thái ở thời điểm t phải GIỐNG HỆT dù tới t bằng cách nào
// (tua tiến, tua lùi, thứ tự xáo trộn, hay tua thẳng tới t lần đầu trên trang mới). Bắt lỗi kiểu fromTo lần hai ghi trạng thái "từ" lúc dựng timeline.
//   mkdir -p /tmp/jsdom-env && (cd /tmp/jsdom-env && npm i jsdom)       # một lần, ngoài repo
//   JSDOM_DIR=/tmp/jsdom-env node presets/corporate-motion/demo/seek-test.mjs <index.html> [bước_giây=0.2]
// Dấu vân = style nội tuyến của mọi phần tử trong #root. Thoát 1 nếu có thời điểm lệch.
// Thêm quy tắc TĨNH (bắt cả lỗi mà jsdom luôn cho kết quả nhất quán nhưng sai): (1) fromTo thứ hai trở đi trên cùng phần tử + thuộc tính phải immediateRender:false
// (không thì lúc dựng nó ghi trạng thái "từ" đè lên tween đứng trước: nút phồng 1.175 trước khi bấm); (2) fromTo thời lượng 0 không được immediateRender (lúc dựng nó ghi giá trị ĐÍCH); (3) tween scale từ giá trị gần 1 (pop, phồng; không phải vào cảnh từ 0) phải immediateRender:false (chấm pill ở 1.08 trước lần nhảy đầu).
import { createRequire } from "node:module";
import path from "node:path";
const require = createRequire(path.join(process.env.JSDOM_DIR || process.cwd(), "x.js"));
const { JSDOM } = require("jsdom");
const file = path.resolve(process.argv[2]), step = parseFloat(process.argv[3] || "0.2");

async function load() {
  const dom = await JSDOM.fromFile(file, { runScripts: "dangerously", resources: "usable", beforeParse(w) { w.__timelines = {}; } });
  await new Promise((r) => (dom.window.document.readyState === "complete" ? r() : dom.window.addEventListener("load", r)));
  const root = dom.window.document.getElementById("root"), tl = dom.window.__timelines[root.getAttribute("data-composition-id")];
  if (!tl) throw new Error("không thấy timeline đã đăng ký");
  return { dom, root, tl, dur: parseFloat(root.getAttribute("data-duration")) };
}
const IDENT = /^(rotate|scale|translate): none$|^transform: (none|translate\(0(px)?, ?0(px)?\)|scale\(1\))$/;   // phép biến đổi đơn vị = không biến đổi
const norm = (css) => css.split(";").map((x) => x.trim()).filter((x) => x && !IDENT.test(x)).sort().join("; ");   // thứ tự khai báo không phải trạng thái
const sig = (root) => { const w = root.ownerDocument.defaultView; return Array.from(root.querySelectorAll("*")).map((e) => norm(e.style.cssText.replace(/opacity:[^;]*;?/, "")) + " | opacity " + (parseFloat(w.getComputedStyle(e).opacity || "1") || 0)); };   // opacity theo giá trị tính ra: inline 0 và CSS mặc định 0 là cùng một trạng thái
const at = (ctx, t) => { ctx.tl.seek(t, false); return sig(ctx.root); };

const main = await load(); const times = [];
for (let t = 0; t <= main.dur + 1e-9; t += step) times.push(+t.toFixed(4));
times.push(+(main.dur - 1 / 30).toFixed(4));
const ref = {}, bad = [];
const ALIAS = { x: "translate", y: "translate", xPercent: "translate", yPercent: "translate", scaleX: "scale", scaleY: "scale" };
const groups = new Map();   // phần tử -> thuộc tính -> các tween
for (const tw of main.tl.getChildren(false, true, false)) {
  const sa = tw.vars && tw.vars.startAt; if (!sa || !tw.targets) continue;
  const imm = tw.vars.immediateRender !== false;
  for (const el of tw.targets()) for (const k of Object.keys(sa)) {
    const key = ALIAS[k] || k; if (!groups.has(el)) groups.set(el, {}); (groups.get(el)[key] = groups.get(el)[key] || []).push({ start: tw.startTime(), dur: tw.duration(), imm, k });
    if (imm && /^scale/.test(k) && sa[k] >= 0.5 && sa[k] <= 2 && tw.startTime() > 0) bad.push("tĩnh: tween " + k + " từ " + sa[k] + " (t=" + tw.startTime().toFixed(3) + ") immediateRender ghi trạng thái pop trước khi nó bắt đầu");
    if (imm && tw.duration() === 0) bad.push("tĩnh: fromTo thời lượng 0 (thuộc tính " + k + ", t=" + tw.startTime().toFixed(3) + ") immediateRender ghi giá trị đích lúc dựng");
  }
}
for (const [el, props] of groups) for (const [k, list] of Object.entries(props)) {
  list.sort((a, b) => a.start - b.start);
  list.slice(1).forEach((w) => { if (w.imm) bad.push("tĩnh: fromTo thứ hai trên '" + k + "' của <" + el.tagName.toLowerCase() + " class='" + el.className + "'> tại t=" + w.start.toFixed(3) + " thiếu immediateRender:false"); });
}
const check = (label, t, s) => {
  if (ref[t] === undefined) { ref[t] = s; return; }
  const i = s.findIndex((x, k) => x !== ref[t][k]);
  if (i >= 0) bad.push(label + " t=" + t + ": phần tử #" + i + " '" + s[i] + "' khác '" + ref[t][i] + "'");
};
times.forEach((t) => check("tiến", t, at(main, t)));
[...times].reverse().forEach((t) => check("lùi", t, at(main, t)));
let seed = 7; const shuffled = [...times].sort(() => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648) - 0.5);
shuffled.forEach((t) => check("xáo", t, at(main, t)));
const cold = times.filter((_, i) => i % Math.max(1, Math.floor(times.length / 12)) === 0);
for (const t of cold) { const c = await load(); check("lạnh", t, at(c, t)); c.dom.window.close(); }   // tua thẳng tới t, chưa qua thời điểm nào trước đó
console.log(path.basename(path.dirname(file)) + "/" + path.basename(file) + ": " + times.length + " thời điểm, " + (3 * times.length + cold.length) + " lần tua, " + (bad.length ? bad.length + " LỆCH" : "giống hệt"));
bad.slice(0, 8).forEach((b) => console.error("  " + b));
process.exit(bad.length ? 1 : 0);
