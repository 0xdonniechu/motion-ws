// Sinh clip HyperFrames từ script.json của preset corporate-motion. LLM chỉ viết nội dung + chọn tên trong catalog; máy làm phần còn lại.
//   node build-clip.mjs <script.json> <outdir> [--theme <tên>]   kiểm script, rồi ghi outdir/{index.html,tokens.js,cuts.json,report.json} + symlink kit/gsap/hyperframes.json
//   node build-clip.mjs --brief                                  in bản rút gọn của catalog.json + layouts.json (chỉ những gì script được phép dùng)
// Kiểm trước khi ghi BẤT CỨ gì (có lỗi thì không vẽ): script.schema.json; tên component/effect/transition có trong kit/catalog.json
// (thiếu: "thiếu mục X trong catalog", thoát 2); prop công khai, đúng kiểu, không internal, không toạ độ (toạ độ thuộc layouts.json);
// item vào đúng slot (`for`); target effect nằm trong `returns`; mục hợp loại beat (`suits`).
// Thoát: 0 ok, 1 script sai, 2 thiếu mục trong catalog. Scene sinh ra chỉ là lời gọi Kit.make / Kit.fx / Kit.tx (không vẽ riêng).
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, "..");
const J = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const lang = J(path.join(root, "language.json")), catalog = J(path.join(root, "kit", "catalog.json")), layoutsDoc = J(path.join(root, "layouts.json")), schema = J(path.join(root, "script.schema.json"));
const LAYOUTS = layoutsDoc.layouts, BEATS = catalog.suits_values, FPS = lang.canvas.fps;
const OWNED = ["x", "y", "w", "h", "minH", "align"];
const NO_SCRIPT = ["cls"];                                     // lớp CSS tự do: không cho script dùng          // toạ độ/căn lề thuộc slot của layout
const MAX_TEXT = 70;                                           // chữ trên màn hình phải ngắn
const TX_CFG = { dissolve: "dissolve", wash: "wash", hard: "hard", "bar-wipe": "bar-wipe", flash: "flash-wipe" };   // tên catalog -> khoá language.transitions (như kit.js)
const byName = (n) => catalog.entries.find((e) => e.name === n);
const frames = (s) => Math.round(s * FPS);
const argv = process.argv.slice(2), opt = (k) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : undefined; };

// ---------------------------------------------------------------- --brief
function returnsKeys(e) { return [...String(e.returns || "").matchAll(/[A-Za-z][A-Za-z0-9]*/g)].map((m) => m[0]); }
if (argv.includes("--brief")) {
  const L = [];
  L.push("# corporate-motion: từ vựng cho script.json (rút từ kit/catalog.json + layouts.json; KHÔNG cần đọc kit.js)");
  L.push("Beat theo thứ tự (khung của preset): " + BEATS.join(" > ") + ". Clip kết ở cta. Loại beat = `type`.");
  L.push("\n## Layout (mỗi beat chọn một; item vào slot theo tên; [..] = component được phép)");
  for (const [n, l] of Object.entries(LAYOUTS)) L.push(`- ${n} (beat ${l.beat}): ${l.about}\n    ` + Object.entries(l.slots).map(([s, v]) => `${s}[${v.for.join(",")}]`).join("  "));
  const pub = (e) => Object.entries(e.props || {}).filter(([k, v]) => !v.internal && !v.system && !(e.kind === "component" && OWNED.includes(k)) && !NO_SCRIPT.includes(k) && !(e.kind === "effect" && k === "at"));
  const suits = (e) => (e.suits.length === BEATS.length ? "" : "  [chỉ beat " + e.suits.join(",") + "]");
  const fmtProp = ([k, v]) => {
    const rng = v.min !== undefined || v.max !== undefined ? ` ${v.min !== undefined ? v.min : ""}..${v.max !== undefined ? v.max : ""}` : "", len = v.maxLen ? ` <=${v.maxLen} ký tự` : "";
    const req = v.required === true ? "  BẮT BUỘC" : v.required ? "  BẮT BUỘC (trừ khi gõ bằng effect " + v.required.replace("unless:", "").replace("@", " target ") + ")" : "";
    const def = v.default !== undefined && v.default !== null && v.default !== "" ? "=" + JSON.stringify(v.default) : "";
    const ex = v.example !== undefined ? "  vd " + JSON.stringify(v.example) : "";
    return `    ${k}:${v.type}${def}${rng}${len}${req} — ${v.desc || ""}${ex}`;
  };
  const placeable = new Set(Object.values(LAYOUTS).flatMap((l) => Object.values(l.slots).flatMap((x) => x.for)));   // component không có slot nào nhận thì script chưa dùng được
  L.push("\n## Component (use) — mỗi prop: tên:kiểu=mặc định khoảng — ý nghĩa/đơn vị, vd; `-> target` = khoá effect có thể nhắm (ngoài `self`)");
  for (const e of catalog.entries.filter((x) => x.kind === "component" && placeable.has(x.name))) L.push(`- ${e.name}: ${e.purpose}${suits(e)}\n${pub(e).map(fmtProp).join("\n") || "    (không có prop)"}\n    -> ${returnsKeys(e).filter((k) => k !== "el").join(", ") || "(chỉ self)"}`);
  L.push("\n## Effect (use) — `at` (giây từ đầu beat), `target`, `props`");
  for (const e of catalog.entries.filter((x) => x.kind === "effect")) L.push(`- ${e.name}: ${e.purpose}${suits(e)}\n${pub(e).map(fmtProp).join("\n") || "    (không có prop)"}`);
  L.push("\n## Transition (transition.use, vào beat kế) — bỏ trống = dissolve");
  for (const e of catalog.entries.filter((x) => x.kind === "transition")) L.push(`- ${e.name}: ${e.purpose}${pub(e).length ? "\n" + pub(e).map(fmtProp).join("\n") : ""}`);
  L.push("\n## Luật: không truyền x,y,w,h,minH,align (layout lo); không truyền ease,reach,dur; chữ <= " + MAX_TEXT + " ký tự mỗi chuỗi; `*từ*` = từ nhấn, `~từ~` = từ nhấn nghiêng có chân (ít thôi, 1 cụm mỗi câu), `^từ^` = chữ rỗng viền, `{cụm}` = vệt tô vàng (kèm effect mark), `[cụm]` = gạch ngang (kèm effect strike); cụm {..} và [..] một dòng, ngắn. Thiếu mục trong catalog => dừng, báo, không vẽ.");
  console.log(L.join("\n")); process.exit(0);
}

// ---------------------------------------------------------------- kiểm theo script.schema.json (tập con JSON Schema đủ dùng)
const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
function check(s, v, p, errs) {
  if (s.const !== undefined) { if (v !== s.const) errs.push(`${p}: phải là ${JSON.stringify(s.const)}`); return; }
  if (s.oneOf) { if (!s.oneOf.some((x) => { const e = []; check(x, v, p, e); return !e.length; })) errs.push(`${p}: sai dạng (${s.oneOf.map((x) => x.const !== undefined ? JSON.stringify(x.const) : x.type).join(" hoặc ")})`); return; }
  if (s.enum) { if (!s.enum.some((x) => x === v)) errs.push(`${p}: phải là một trong ${s.enum.map((x) => JSON.stringify(x)).join(", ")}`); return; }
  const t = s.type;
  if (t) {
    const ok = t === "object" ? isObj(v) : t === "array" ? Array.isArray(v) : t === "string" ? typeof v === "string" : t === "number" ? typeof v === "number" && Number.isFinite(v) : true;
    if (!ok) { errs.push(`${p}: phải là ${t}`); return; }
  }
  if (typeof v === "string") {
    if (s.minLength !== undefined && v.length < s.minLength) errs.push(`${p}: rỗng`);
    if (s.maxLength !== undefined && v.length > s.maxLength) errs.push(`${p}: dài ${v.length} > ${s.maxLength} ký tự`);
    if (s.pattern && !new RegExp(s.pattern).test(v)) errs.push(`${p}: không khớp ${s.pattern}`);
  }
  if (typeof v === "number") {
    if (s.minimum !== undefined && v < s.minimum) errs.push(`${p}: ${v} < ${s.minimum}`);
    if (s.maximum !== undefined && v > s.maximum) errs.push(`${p}: ${v} > ${s.maximum}`);
  }
  if (Array.isArray(v)) {
    if (s.minItems !== undefined && v.length < s.minItems) errs.push(`${p}: cần >= ${s.minItems} phần tử`);
    if (s.maxItems !== undefined && v.length > s.maxItems) errs.push(`${p}: chỉ được <= ${s.maxItems} phần tử`);
    if (s.items) v.forEach((x, i) => check(s.items, x, `${p}[${i}]`, errs));
  }
  if (isObj(v)) {
    for (const k of s.required || []) if (!(k in v)) errs.push(`${p}: thiếu khoá "${k}"`);
    for (const [k, x] of Object.entries(v)) {
      if (s.properties && s.properties[k]) check(s.properties[k], x, `${p}.${k}`, errs);
      else if (s.additionalProperties === false) errs.push(`${p}: khoá lạ "${k}" (schema không có)`);
    }
  }
}

// kiểu prop trong catalog ("px", "s", "int", "a|b|null", "number[]", "[fx,fy][]", "{label}") -> giá trị có hợp không
const SCALAR = { px: (v) => typeof v === "number" && isFinite(v), s: (v) => typeof v === "number" && isFinite(v), number: (v) => typeof v === "number" && isFinite(v), int: Number.isInteger, string: (v) => typeof v === "string", bool: (v) => typeof v === "boolean", "0..1": (v) => typeof v === "number" && v >= 0 && v <= 1, element: () => false };
function matchesType(v, t) {
  t = t.trim();
  if (t.endsWith("[]")) return Array.isArray(v) && v.every((x) => matchesType(x, t.slice(0, -2)));
  if (t.startsWith("[")) return Array.isArray(v);                       // [fx,fy], [x1,y1,x2,y2]
  if (t.startsWith("{")) return isObj(v);
  if (t.includes("|")) return t.split("|").some((a) => matchesType(v, a));
  if (SCALAR[t]) return SCALAR[t](v);
  return t === "null" ? v === null : v === t;                           // giá trị chữ của enum
}
const strings = (v, out = []) => { if (typeof v === "string") out.push(v); else if (Array.isArray(v)) v.forEach((x) => strings(x, out)); else if (isObj(v)) for (const [k, x] of Object.entries(v)) if (k !== "cls") strings(x, out); return out; };

// ---------------------------------------------------------------- kiểm theo catalog + layouts
function validate(script, themeName) {
  const errs = [], warns = [], missing = [], calls = { make: 0, fx: 0, tx: 0 };
  check(schema, script, "script", errs);
  if (errs.length) return { errs, warns, missing, calls };           // sai dạng thì không đi tiếp
  const propsOf = (entry, props, where, owned, effs) => {
    props = props || {};
    for (const [k, v] of Object.entries(props)) {
      const spec = entry.props && entry.props[k];
      if (owned && OWNED.includes(k)) { errs.push(`${where}: prop "${k}" thuộc layout (toạ độ/căn lề), không truyền trong script`); continue; }
      if (NO_SCRIPT.includes(k)) { errs.push(`${where}: prop "${k}" không dùng trong script`); continue; }
      if (!spec) { errs.push(`${where}: "${entry.name}" không có prop công khai "${k}" (xem --brief)`); continue; }
      if (spec.internal) { errs.push(`${where}: prop "${k}" là nội bộ (ghi đè language), cấm truyền`); continue; }
      if (spec.system) { errs.push(`${where}: prop "${k}" do máy đặt (cảnh/thời điểm), cấm trong script`); continue; }
      if (!matchesType(v, spec.type)) { errs.push(`${where}: prop "${k}" phải là ${spec.type}, nhận ${JSON.stringify(v).slice(0, 40)}`); continue; }
      if (typeof v === "number") { if (spec.min !== undefined && v < spec.min) errs.push(`${where}: prop "${k}" = ${v} < ${spec.min}`); if (spec.max !== undefined && v > spec.max) errs.push(`${where}: prop "${k}" = ${v} > ${spec.max}`); }
      if (typeof v === "string" && spec.maxLen !== undefined && v.length > spec.maxLen) errs.push(`${where}: prop "${k}" dài ${v.length} > ${spec.maxLen} ký tự`);
      if (spec.schema) check(spec.schema, v, `${where}: prop "${k}"`, errs);
      for (const s of strings(v)) if (s.length > MAX_TEXT) errs.push(`${where}: prop "${k}" có chuỗi dài ${s.length} > ${MAX_TEXT} ký tự (chữ trên màn hình phải ngắn)`);
    }
    for (const [k, spec] of Object.entries(entry.props || {})) {   // prop bắt buộc (catalog: required)
      if (!spec.required || spec.internal || spec.system) continue;
      const has = k in props && !(typeof props[k] === "string" && props[k].trim() === "");
      if (spec.required === true) { if (!has) errs.push(`${where}: thiếu prop bắt buộc "${k}" (${entry.name})`); continue; }
      const m = /^unless:(\w+)@(\w+)$/.exec(spec.required);
      const typed = (effs || []).some((ef) => ef.use === m[1] && (ef.target || "self") === m[2] && typeof (ef.props && ef.props.text) === "string" && ef.props.text.trim() !== "");
      if (!has && !typed) errs.push(`${where}: thiếu "${k}": phải có prop "${k}" hoặc effect ${m[1]} (target ${m[2]}) kèm text, không thì ô trống`);
      if (has && typed) errs.push(`${where}: "${k}" vừa có chữ vừa có effect ${m[1]} chép đè: chọn một`);
    }
  };
  const lookup = (name, kind, where) => {
    const e = byName(name);
    if (!e) { missing.push(name); errs.push(`${where}: thiếu mục ${name} trong catalog (${kind})`); return null; }
    if (e.kind !== kind) { errs.push(`${where}: "${name}" là ${e.kind} trong catalog, không phải ${kind}`); return null; }
    return e;
  };
  let prevIdx = -1, allText = "";
  const types = script.beats.map((b) => b.type);
  script.beats.forEach((b, bi) => {
    const bw = `beat ${bi + 1}`;
    const ti = BEATS.indexOf(b.type);
    if (ti < 0) { errs.push(`${bw}: type "${b.type}" không có trong khung beat (${BEATS.join(", ")})`); return; }
    if (ti < prevIdx) errs.push(`${bw}: ${b.type} đứng sau ${types[bi - 1]}, ngược thứ tự khung beat (${BEATS.join(" > ")})`);
    prevIdx = Math.max(prevIdx, ti);
    const layoutName = b.layout || Object.keys(LAYOUTS).find((n) => LAYOUTS[n].beat === b.type);
    const layout = LAYOUTS[layoutName];
    if (!layout) { errs.push(`${bw}: không có layout cho beat ${b.type} (layouts.json)`); return; }
    if (layout.beat !== b.type) { errs.push(`${bw}: layout "${layoutName}" dành cho beat ${layout.beat}, không phải ${b.type}`); return; }
    if (b.page) { const pe = lookup("page", "component", bw); if (pe) propsOf(pe, b.page, bw + " page", false); }
    const used = new Set(); calls.make++;
    b.items.forEach((it, ii) => {
      const w = `${bw} item ${ii + 1}`;
      const ce = lookup(it.use, "component", w);
      calls.make++;
      const slot = layout.slots[it.slot];
      if (!slot) errs.push(`${w}: slot "${it.slot}" không có trong layout ${layoutName} (có: ${Object.keys(layout.slots).join(", ")})`);
      else if (used.has(it.slot)) errs.push(`${w}: slot "${it.slot}" đã có item khác`);
      else if (ce && !slot.for.includes(it.use)) errs.push(`${w}: slot "${it.slot}" chỉ nhận ${slot.for.join(", ")}, không nhận ${it.use}`);
      used.add(it.slot);
      if (ce) {
        if (!ce.suits.includes(b.type)) errs.push(`${w}: component ${it.use} không hợp beat ${b.type} (suits: ${ce.suits.join(", ")})`);
        propsOf(ce, it.props, w, true, it.effects);
        const pr = it.props || {};
        if (it.use === "statCard" && pr.chart && slot && slot.h !== undefined && slot.h < (pr.chart.top || 540) + (pr.chart.h || 160) + 70) errs.push(`${w}: chart (top ${pr.chart.top || 540} + h ${pr.chart.h || 160}) không vừa slot "${it.slot}" cao ${slot.h}: dùng layout stat-chart-line`);
        if (it.use === "table" && Array.isArray(pr.rows) && Array.isArray(pr.columns)) { if (pr.rows.some((r) => r.length !== pr.columns.length)) errs.push(`${w}: mỗi hàng của table phải có ${pr.columns.length} ô`); if (pr.highlight !== undefined && pr.highlight >= pr.rows.length) errs.push(`${w}: highlight ${pr.highlight} ngoài ${pr.rows.length} hàng`); }
        if (it.use === "tabs" && Array.isArray(pr.labels)) {
          if (pr.active !== undefined && pr.active > pr.labels.length) errs.push(`${w}: active ${pr.active} ngoài ${pr.labels.length} tab`);
          (it.effects || []).forEach((ef, ei) => { if (ef.use === "tabSwitch" && ef.props && ef.props.to !== undefined && ef.props.to > pr.labels.length) errs.push(`${w} effect ${ei + 1}: to ${ef.props.to} ngoài ${pr.labels.length} tab`); });
        }
        allText += " " + strings(it.props || {}).join(" ");
      }
      (it.effects || []).forEach((ef, ei) => {
        const we = `${w} effect ${ei + 1}`;
        const ee = lookup(ef.use, "effect", we); calls.fx++;
        if (!ee) return;
        if (!ee.suits.includes(b.type)) errs.push(`${we}: effect ${ef.use} không hợp beat ${b.type} (suits: ${ee.suits.join(", ")})`);
        if (ef.props && "at" in ef.props) errs.push(`${we}: dùng trường "at" của effect, không để trong props`);
        propsOf(ee, ef.props, we, false, []);
        allText += " " + strings(ef.props || {}).join(" ");
        if (ef.target && ef.target !== "self" && ce && !returnsKeys(ce).includes(ef.target)) errs.push(`${we}: target "${ef.target}" không có trong returns của ${it.use} (${returnsKeys(ce).join(", ")})`);
      });
      // vệt `{..}` / gạch `[..]` không có effect mark/strike thì hiện tĩnh từ khung 0; hai lần gọi cùng effect trên cùng chữ thì tween chồng nhau
      const effs = it.effects || [], mk = (re, use) => {
        const txt = strings(it.props || {}).concat(effs.filter((e) => e.use === "typing").flatMap((e) => strings(e.props || {})));
        const calls = effs.filter((e) => e.use === use), per = {}; calls.forEach((e) => { const t = e.target || "self"; per[t] = (per[t] || 0) + 1; });
        if (txt.some((t) => re.test(t)) && !calls.length) warns.push(`${w}: chữ có ${use === "mark" ? "{cụm}" : "[cụm]"} nhưng không có effect ${use}: sẽ hiện tĩnh từ khung 0`);
        for (const [t, n] of Object.entries(per)) if (n > 1) warns.push(`${w}: effect ${use} gọi ${n} lần trên cùng chữ (target ${t}): tween chồng nhau, gọi một lần thôi`);
      };
      mk(/\{[^}]+\}/, "mark"); mk(/\[[^\]]+\]/, "strike");
    });
    if (bi === script.beats.length - 1) { if (b.transition) errs.push(`${bw}: beat cuối không có transition`); }
    else { const tn = b.transition ? b.transition.use : "dissolve"; const te = lookup(tn, "transition", bw + " transition"); calls.tx++; if (te) propsOf(te, b.transition && b.transition.props, bw + " transition", false); }
  });
  if (script.beats[script.beats.length - 1].type !== "cta") errs.push(`beat cuối phải là cta, đang là ${script.beats[script.beats.length - 1].type}`);
  if (!missing.length && !errs.length) {
    if (script.beats[0].type !== BEATS[0]) warns.push(`bỏ beat đầu: clip mở bằng ${script.beats[0].type}, khung beat mở bằng ${BEATS[0]}`);
    
    if (allText.length > 120 && !/[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]/i.test(allText)) warns.push("chữ không có dấu tiếng Việt nào: kiểm lại (cần đủ dấu)");
  }
  if (!fs.existsSync(path.join(root, "themes", themeName + ".json"))) errs.push(`theme "${themeName}" không có trong themes/ (có: ${fs.readdirSync(path.join(root, "themes")).map((f) => f.replace(/\.json$/, "")).join(", ")})`);
  return { errs, warns, missing, calls };
}

// ---------------------------------------------------------------- dựng dòng thời gian (khung 30fps)
const typingSec = (it) => (it.effects || []).filter((e) => e.use === "typing").map((e) => e.at + String((e.props && e.props.text) || "").replace(/[*~^{}\[\]]/g, "").length / lang.motion.typed_text.chars_per_s);
function autoDuration(b) {   // nhịp từ language.json: độ dài cảnh trung vị, hoặc (lúc effect cuối + thời gian gõ + chữ đứng yên trung vị) nếu lớn hơn
  const ends = b.items.flatMap((it) => (it.effects || []).map((e) => e.at + (e.use === "typing" ? String((e.props && e.props.text) || "").replace(/[*~^{}\[\]]/g, "").length / lang.motion.typed_text.chars_per_s : 0)));
  return Math.max(lang.rhythm.shot_len_median_s, Math.max(0, ...ends) + lang.rhythm.text_dwell_median_s);
}
function timeline(script) {
  let t = 0; const rows = [];
  script.beats.forEach((b, i) => {
    const d = frames(b.duration === undefined || b.duration === "auto" ? autoDuration(b) : b.duration);
    const layout = b.layout || Object.keys(LAYOUTS).find((n) => LAYOUTS[n].beat === b.type);
    const txName = i < script.beats.length - 1 ? (b.transition ? b.transition.use : "dissolve") : null;
    rows.push({ i, b, start: t, dur: d, layout, txName, txFrames: txName ? Math.max(1, frames(lang.transitions[TX_CFG[txName]].duration_s)) : 0 });
    t += d;
  });
  rows.forEach((r, i) => { r.txAt = r.txName ? r.start + r.dur - Math.floor(r.txFrames / 2) : null; });   // chuyển cảnh nằm quanh mốc cắt (giống clip mẫu)
  rows.forEach((r, i) => { r.secStart = i === 0 ? 0 : rows[i - 1].txAt; r.secEnd = r.txName ? r.txAt + r.txFrames : t; });
  return { rows, total: t };
}

// ---------------------------------------------------------------- phát mã
const ident = /^[A-Za-z_$][\w$]*$/;
function js(v) {   // khoá không dấu ngoặc để build-tokens --check-scenes thấy được prop internal nếu lọt qua
  if (v === null) return "null";
  if (Array.isArray(v)) return "[" + v.map(js).join(", ") + "]";
  if (isObj(v)) { const e = Object.entries(v); return e.length ? "{ " + e.map(([k, x]) => (ident.test(k) ? k : JSON.stringify(k)) + ": " + js(x)).join(", ") + " }" : "{}"; }
  if (typeof v === "string") return JSON.stringify(v).replace(/</g, "\\u003c").replace(/[\u2028\u2029]/g, (c) => "\\u" + c.charCodeAt(0).toString(16));
  return String(v);
}
const sec = (f) => +(f / FPS).toFixed(4);
const geom = (slot) => Object.fromEntries(Object.entries(slot).filter(([k]) => k !== "for"));

function emit(script, tl) {
  const { rows, total } = tl, secs = [], code = [];
  for (const r of rows) {
    const id = "b" + (r.i + 1);
    secs.push(`  <section id="${id}" class="clip k-scene" data-start="${sec(r.secStart)}" data-duration="${sec(r.secEnd - r.secStart)}" data-track-index="${r.i + 1}"></section>`);
    const layout = LAYOUTS[r.layout], S = `S("${id}")`, vars = [];
    code.push(`// ---------- B${r.i + 1} (${sec(r.start)}-${sec(r.start + r.dur)}s): ${r.b.type} ----------`);
    code.push(`Kit.make("page", ${S}, ${js({ mode: "tint", ...(r.b.page || {}) })});`);
    r.b.items.forEach((it, ii) => { const v = `${id}i${ii}`; vars.push(v); code.push(`const ${v} = Kit.make(${js(it.use)}, ${S}, ${js({ ...(it.props || {}), ...geom(layout.slots[it.slot]) })});`); });
    if (r.i > 0) {
      const p = rows[r.i - 1], extra = Object.entries((p.b.transition && p.b.transition.props) || {}).map(([k, x]) => ", " + k + ": " + js(x)).join("");
      code.push(`Kit.tx(${js(p.txName)}, tl, { from: S("b${r.i}"), to: ${S}, at: f(${p.txAt})${extra} });`);
    }
    r.b.items.forEach((it, ii) => (it.effects || []).forEach((ef) => {
      const at = r.start + frames(ef.at), tgt = !ef.target || ef.target === "self" ? vars[ii] : `${vars[ii]}.${ef.target}`;
      code.push(`Kit.fx(${js(ef.use)}, tl, ${tgt}, { ${[`at: f(${at})`, ...Object.entries(ef.props || {}).map(([k, x]) => (ident.test(k) ? k : JSON.stringify(k)) + ": " + js(x))].join(", ")} });`);
    }));
    code.push("");
  }
  const title = String(script.title).replace(/--+/g, "-");
  return `<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=${lang.canvas.w}, height=${lang.canvas.h}">
<link rel="stylesheet" href="kit/fonts/fonts.css">
<link rel="stylesheet" href="kit/kit.css">
<script src="gsap.min.js"></script>
<script src="tokens.js"></script>
<script src="kit/kit.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: ${lang.canvas.w}px; height: ${lang.canvas.h}px; overflow: hidden; background: var(--k-tint); }
#root { position: relative; width: ${lang.canvas.w}px; height: ${lang.canvas.h}px; overflow: hidden; }
</style>
</head>
<body>
<!-- SINH TỰ ĐỘNG bởi presets/corporate-motion/tools/build-clip.mjs từ script.json ("${title}"); đừng sửa tay, sửa script rồi sinh lại. Scene chỉ là lời gọi catalog (Kit.make / Kit.fx / Kit.tx). -->
<div id="root" data-composition-id="main" data-start="0" data-duration="${sec(total)}" data-width="${lang.canvas.w}" data-height="${lang.canvas.h}" data-fps="${FPS}">
${secs.join("\n")}
</div>
<script>
const tl = gsap.timeline({ paused: true }), f = (n) => n / ${FPS}, S = Kit.scene;   // f: số khung -> giây

${code.join("\n")}
window.__timelines["main"] = tl;
</script>
</body>
</html>
`;
}

// ---------------------------------------------------------------- chính
const pos = argv.filter((a, i) => !a.startsWith("--") && argv[i - 1] !== "--theme");
if (pos.length !== 2) { console.error("dùng: node build-clip.mjs <script.json> <outdir> [--theme <tên>]   |   node build-clip.mjs --brief"); process.exit(1); }
const [scriptPath, outdir] = pos.map((p) => path.resolve(p));
let script;
try { script = J(scriptPath); } catch (e) { console.error("LỖI: không đọc được " + scriptPath + ": " + e.message); process.exit(1); }
const themeName = opt("--theme") || (isObj(script) && typeof script.theme === "string" ? script.theme : "default");
const v = validate(script, themeName);
if (v.errs.length) {
  console.error(`build-clip: ${v.errs.length} lỗi, KHÔNG ghi gì, KHÔNG vẽ:`); for (const e of v.errs) console.error("  - " + e);
  if (v.missing.length) console.error(`DỪNG: thiếu mục trong catalog (${[...new Set(v.missing)].join(", ")}). Thêm vào kit (catalog.json + kit.js + demo/) trước rồi mới dùng; không vẽ tạm trong scene.`);
  process.exit(v.missing.length ? 2 : 1);
}
const tl = timeline(script);
for (const r of tl.rows) {   // effect phải nằm trong beat
  for (const it of r.b.items) for (const ef of it.effects || []) if (frames(ef.at) >= r.dur) { console.error(`LỖI: beat ${r.i + 1} effect ${ef.use} at=${ef.at}s >= độ dài beat ${sec(r.dur)}s`); process.exit(1); }
}
const html = emit(script, tl);

const guard = path.join(outdir, "kit");
if (fs.existsSync(guard) && !fs.lstatSync(guard).isSymbolicLink()) { console.error("LỖI: " + guard + " là thư mục thật, không ghi đè"); process.exit(1); }
fs.mkdirSync(outdir, { recursive: true });
const link = (target, name) => { const p = path.join(outdir, name); try { fs.unlinkSync(p); } catch {} fs.symlinkSync(path.relative(outdir, target), p); };
link(path.join(root, "kit"), "kit"); link(path.join(root, "demo", "gsap.min.js"), "gsap.min.js"); link(path.join(root, "demo", "hyperframes.json"), "hyperframes.json");
fs.writeFileSync(path.join(outdir, "index.html"), html);
const cuts = { S: [...tl.rows.map((r) => sec(r.start)), sec(tl.total)], TOTAL: sec(tl.total), fps: FPS, note: "mốc cắt THEO THIẾT KẾ (giữa mỗi chuyển cảnh), sinh từ script.json" };
fs.writeFileSync(path.join(outdir, "cuts.json"), JSON.stringify(cuts));

// kiểm kiểu verify.sh
const checks = [], run = (label, args) => { const r = spawnSync("node", [path.join(root, "kit", "build-tokens.mjs"), ...args], { encoding: "utf8" }); checks.push({ label, ok: r.status === 0, out: (r.stdout + r.stderr).trim().split("\n").pop() }); return r.status === 0; };
run("tokens.js (theme " + themeName + ")", ["--theme", themeName, "--out", path.join(outdir, "tokens.js")]);
run("tokens.js cập nhật", ["--check", "--theme", themeName, "--out", path.join(outdir, "tokens.js")]);
run("catalog khớp kit.js", ["--check-catalog"]);
run("language khớp style.json", ["--check-style"]);
run("scene không ghi đè language", ["--check-scenes", path.join(outdir, "index.html")]);
const report = { title: script.title, theme: themeName, fps: FPS, frames: tl.total, duration_s: sec(tl.total), calls: v.calls, warnings: v.warns,
  beats: tl.rows.map((r) => ({ n: r.i + 1, type: r.b.type, layout: r.layout, start_s: sec(r.start), duration_s: sec(r.dur), section: [sec(r.secStart), sec(r.secEnd)], transition_out: r.txName, items: r.b.items.length, effects: r.b.items.reduce((a, it) => a + (it.effects || []).length, 0) })),
  checks };
fs.writeFileSync(path.join(outdir, "report.json"), JSON.stringify(report, null, 1));

console.log(`build-clip: "${script.title}"  theme=${themeName}  ${tl.rows.length} beat  ${sec(tl.total).toFixed(2)}s  ${tl.total} khung  -> ${path.relative(process.cwd(), outdir) || "."}`);
console.log(" #  giây            beat             layout              item eff  chuyển ra");
for (const b of report.beats) console.log(` ${String(b.n).padStart(1)}  ${(b.start_s.toFixed(1) + "-" + (b.start_s + b.duration_s).toFixed(1)).padEnd(14)}  ${b.type.padEnd(15)}  ${b.layout.padEnd(18)}  ${String(b.items).padStart(3)} ${String(b.effects).padStart(3)}  ${b.transition_out || "(kết)"}`);
console.log(`  lời gọi catalog: ${v.calls.make} make, ${v.calls.fx} fx, ${v.calls.tx} tx — đều có trong catalog`);
for (const w of v.warns) console.log("  cảnh báo: " + w);
for (const c of checks) console.log(`  [${c.ok ? "ok" : "LỖI"}] ${c.label}${c.ok ? "" : ": " + c.out}`);
process.exit(checks.every((c) => c.ok) ? 0 : 1);
