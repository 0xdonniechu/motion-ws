// Gộp LANGUAGE (../language.json: chuyển động, nhịp, tỉ lệ) với THEME (../themes/<tên>.json: màu, font, kiểu chữ, bo góc, tông bóng) thành tokens.js cho kit.
//   node build-tokens.mjs [--theme <tên>] [--out <tệp>]    ghi tokens.js (mặc định theme default, ra kit/tokens.js)
//   node build-tokens.mjs --check [--theme <tên>] [--out <tệp>]   thoát 1 nếu tệp đích lệch (cũ)
//   node build-tokens.mjs --check-style    so language.json với style.json (build_defaults) và báo chỗ lệch
//   node build-tokens.mjs --check-scenes <index.html>...  thoát 1 nếu scene truyền prop `internal` của catalog (ease, reach, dur) vào Kit.make/fx/tx
//   node build-tokens.mjs --check-catalog  catalog.json: đủ trường, và mỗi mục có thẻ demo trong ../demo/index.html (kit.js tự so tên catalog khi nạp)
// Theme chỉ được có màu, font, kiểu chữ và tông màu bóng (shadow.rgb); có khoá chuyển động, bố cục, bo góc, độ đậm bóng thì dừng (language không đổi theo theme).
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, "..");
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const J = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const lang = J(path.join(root, "language.json"));

if (process.argv.includes("--check-style")) {   // language.json phải khớp style.json (nguồn đo)
  const style = J(path.join(root, "style.json")), b = style.build_defaults, M = b.motion;
  const e = (k) => ({ ease: M[k].gsap_ease, reach_s: M[k].duration_s, settle_s: M[k].settle_s, overshoot: M[k].overshoot, distance_frac: M[k].distance_frac, distance_of: M[k].distance_of });
  const want = {
    "motion.card_slide_in": e("card_slide_in"), "motion.number_count_up": e("number_count_up.bar_driven"), "motion.bar_fill": e("bar_fill"),
    "motion.chart_pop": { ...e("chart_pop.bar1"), stagger_s: M["chart_pop.bar1"].stagger_s_clip1_only },
    "motion.pill_progress": { hop_frames: M.pill_progress.hop_frames, pop_scale: M.pill_progress.pop_scale, settle_s: M.pill_progress.settle_s },
    "motion.typed_text": { chars_per_s: style.motion.typed_text.chars_per_s.median, chars_per_s_range: [style.motion.typed_text.chars_per_s.min, style.motion.typed_text.chars_per_s.max] },
  };
  for (const [k, v] of Object.entries(b.transitions.kinds)) want["transitions." + k] = { duration_s: v.duration_s, share: v.share };
  const get = (o, p) => p.split(".").reduce((a, x) => (a === undefined ? a : a[x]), o);
  let bad = 0;
  for (const [k, v] of Object.entries(want)) {
    const got = get(lang, k); const gotSub = Object.fromEntries(Object.keys(v).map((x) => [x, got ? got[x] : undefined]));
    if (JSON.stringify(gotSub) !== JSON.stringify(v)) { bad++; console.error("lệch " + k + ": language=" + JSON.stringify(gotSub) + " style=" + JSON.stringify(v)); }
  }
  const sz = Object.fromEntries(Object.entries(b.type_scale.roles).map(([k, v]) => [k, v.font_size_px_1080x1920]));
  if (JSON.stringify(sz) !== JSON.stringify(lang.type.sizes_px)) { bad++; console.error("lệch type.sizes_px"); }
  console.log(bad ? bad + " chỗ lệch" : "language.json khớp style.json (build_defaults)"); process.exit(bad ? 1 : 0);
}

const catalog = J(path.join(here, "catalog.json"));
if (process.argv.includes("--check-catalog")) {
  const demo = fs.readFileSync(path.join(root, "demo", "index.html"), "utf8"); let bad = 0; const count = {};
  for (const e of catalog.entries) {
    count[e.kind] = (count[e.kind] || 0) + 1;
    for (const k of ["kind", "name", "purpose", "props", "suits", "example", "demo"]) if (e[k] === undefined) { bad++; console.error(e.name + " thiếu " + k); }
    if (!["component", "effect", "transition"].includes(e.kind)) { bad++; console.error(e.name + ": kind lạ " + e.kind); }
    if (!demo.includes('"' + e.name + '"')) { bad++; console.error(e.kind + " " + e.name + ": không có thẻ demo (chuỗi \"" + e.name + "\" trong demo/index.html)"); }
  }
  // props: so tập `o.<prop>` mà từng hàm trong kit.js đọc với khoá props của catalog (đủ và không thừa)
  const src = fs.readFileSync(path.join(here, "kit.js"), "utf8"), starts = [], re = /^\s*(C|F|X)(?:\.([A-Za-z]+)|\["([\w-]+)"\])\s*=/gm; let mm;
  while ((mm = re.exec(src))) starts.push({ kind: { C: "component", F: "effect", X: "transition" }[mm[1]], name: mm[2] || mm[3], at: mm.index });
  const regionEnd = src.indexOf("// ================================================================ đăng ký");
  const helper = (name) => { const i = src.indexOf("const " + name + " = "); if (i < 0) return ""; const j = src.indexOf("\n  };", i); return src.slice(i, Math.min(src.indexOf("\n", i) > j && j > 0 ? j : src.indexOf("\n", i), src.length)); };
  const fmtLine = (src.match(/const fmt = .*\n/) || [""])[0], txPrep = (src.match(/const txPrep = [\s\S]*?\n  };\n/) || [""])[0], overlay = (src.match(/const overlay = [\s\S]*?\n  };\n/) || [""])[0];
  for (const e of catalog.entries) {
    const i = starts.findIndex((x) => x.kind === e.kind && x.name === e.name);
    if (i < 0) { bad++; console.error(e.kind + " " + e.name + ": không có cài đặt trong kit.js"); continue; }
    const sect = src.indexOf("// ====", starts[i].at + 1), nextAt = i + 1 < starts.length ? starts[i + 1].at : regionEnd;
    const body = src.slice(starts[i].at, sect > 0 && sect < nextAt ? sect : nextAt).replace(fmtLine, "").replace(txPrep, "").replace(overlay, "");
    const used = new Set([...(body + (e.name === "countUp" ? fmtLine : "") + (e.kind === "transition" ? txPrep + (["wash", "flash"].includes(e.name) ? overlay : "") : "")).matchAll(/\bo\.([A-Za-z_]\w*)/g)].map((x) => x[1]));
    if (/place\(e,\s*(o\b|Object\.assign\([^)]*,\s*o\))/.test(body) || /C\.card\(parent,/.test(body)) for (const k of ["x", "y", "w", "h"]) used.add(k);
    if (/C\.card\(parent,/.test(body)) used.add("cls");
    const listed = new Set(Object.keys(e.props || {}));
    for (const k of used) if (!listed.has(k)) { bad++; console.error(e.kind + " " + e.name + ": kit.js đọc prop '" + k + "' nhưng catalog không liệt kê"); }
    for (const k of listed) if (!used.has(k)) { bad++; console.error(e.kind + " " + e.name + ": catalog liệt kê '" + k + "' nhưng kit.js không đọc"); }
  }
  console.log(JSON.stringify(count), "tổng", catalog.entries.length, bad ? bad + " lỗi" : "catalog đủ, props khớp kit.js, có demo"); process.exit(bad ? 1 : 0);
}

if (process.argv.includes("--check-scenes")) {   // scene chỉ được gọi theo catalog và không được ghi đè language
  const internal = new Set(); for (const e of catalog.entries) for (const [k, v] of Object.entries(e.props || {})) if (v.internal) internal.add(k);
  let bad = 0;
  for (const f of process.argv.slice(process.argv.indexOf("--check-scenes") + 1).filter((x) => !x.startsWith("--"))) {
    const src = fs.readFileSync(f, "utf8");
    for (const m of src.matchAll(/Kit\.(?:make|fx|tx)\(([^;\n]*)\)\s*;/g)) for (const k of internal) if (new RegExp("[{,]\\s*" + k + "\\s*:").test(m[1])) { bad++; console.error(path.basename(path.dirname(f)) + ": " + m[0].slice(0, 90) + " truyền '" + k + "' (ghi đè language, cấm trong scene)"); }
  }
  console.log(bad ? bad + " lỗi" : "scene không ghi đè language (" + [...internal].join(", ") + ")"); process.exit(bad ? 1 : 0);
}

const themeName = arg("--theme", "default");
const themePath = path.join(root, "themes", themeName + ".json");
if (!fs.existsSync(themePath)) { console.error("không có theme: " + themePath); process.exit(1); }
const theme = J(themePath);
const allowed = ["_doc", "name", "colors", "page", "iso", "font", "type", "shadow"];   // màu, font, kiểu chữ; shadow chỉ có tông màu (rgb)
if (theme.shadow) for (const k of Object.keys(theme.shadow)) if (k !== "rgb") { console.error("theme " + themeName + ": shadow." + k + " không được phép (độ đậm bóng thuộc language.json; theme chỉ đổi tông rgb)"); process.exit(1); }
for (const k of Object.keys(theme)) if (!allowed.includes(k)) { console.error("theme " + themeName + " có khoá không được phép: " + k + " (chỉ " + allowed.join(", ") + "; chuyển động/bố cục thuộc language.json)"); process.exit(1); }
const need = (v, what) => { if (v === undefined || v === null) { console.error("theme " + themeName + " thiếu " + what); process.exit(1); } return v; };
const C = need(theme.colors, "colors");
for (const k of ["surface", "accent_dark", "accent_primary", "accent_mid", "accent_light", "ink", "ink_secondary", "yellow", "mark"]) need(C[k], "colors." + k);
// chữ nằm trên vệt tô `mark` (kit.js) mà hyperframes check không thấy được (vệt là lớp định vị tuyệt đối): màu vệt so với màu chữ phải >= 3.0 (WCAG chữ lớn) ở MỌI theme, không thì dừng
const relLum = (h) => { const [r, g, b] = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
const contrast = (a, b) => { const [x, y] = [relLum(a), relLum(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };
for (const f of fs.readdirSync(path.join(root, "themes")).filter((x) => x.endsWith(".json"))) {
  const tc = J(path.join(root, "themes", f)).colors || {}, cr = contrast(need(tc.mark, "colors.mark (theme " + f + ")"), need(tc.ink, "colors.ink (theme " + f + ")"));
  if (cr < 3.0) { console.error("theme " + f + ": colors.mark " + tc.mark + " so với colors.ink " + tc.ink + " chỉ " + cr.toFixed(2) + ":1 (< 3.0): chữ trên vệt tô không đọc được; chỉnh colors.mark"); process.exit(1); }
}
// nét bút `penMark` và gợn `cursorClick` vẽ ĐÈ lên đích có nền riêng (nút, huy hiệu, tick, bong bóng, pill của tabs, khối iso...) mà hyperframes check không thấy. kit.js chọn màu nét theo nền thật dưới đích trong chuỗi
// [token ưu tiên] -> accent_primary -> accent_dark -> surface -> ink, lấy token đầu tiên có tương phản >= 3.0. Cổng chung (không theo từng đích): với MỌI màu nền mà theme có thể đặt dưới nét (mọi colors.*, page.tint, page.white, iso.*)
// phải có ít nhất một token trong chuỗi đạt >= 3.0, ở MỌI theme; không thì dừng
for (const f of fs.readdirSync(path.join(root, "themes")).filter((x) => x.endsWith(".json"))) {
  const tj = J(path.join(root, "themes", f)), tc = tj.colors || {}, fills = { "page.tint": need(tj.page && tj.page.tint, "page.tint (theme " + f + ")"), "page.white": need(tj.page.white, "page.white (theme " + f + ")") };
  for (const [k, v] of Object.entries(tc)) fills["colors." + k] = v;
  (tj.iso || []).forEach((v, i) => { fills["iso[" + i + "]"] = v; });
  const chain = ["accent_primary", "accent_dark", "surface", "ink"].map((k) => [k, need(tc[k], "colors." + k + " (theme " + f + ")")]);
  for (const [fn, fc] of Object.entries(fills)) {
    const best = chain.map(([k, c]) => [k, contrast(c, fc)]).sort((a, b) => b[1] - a[1])[0];
    if (best[1] < 3.0) { console.error("theme " + f + ": nền " + fn + " " + fc + ": không token nào trong [accent_primary, accent_dark, surface, ink] đạt tương phản >= 3.0 (tốt nhất " + best[0] + " " + best[1].toFixed(2) + ":1): nét bút/gợn đè lên nền này không đủ nổi; chỉnh màu"); process.exit(1); }
  }
}
need(theme.page && theme.page.tint, "page.tint"); need(theme.page.white, "page.white"); need(theme.font && theme.font.family, "font.family"); need(theme.font.body_weight, "font.body_weight");
need(theme.type && theme.type.roles, "type.roles"); need(theme.font.accent_family, "font.accent_family"); need(theme.type.accent_italic && theme.type.accent_italic.weight, "type.accent_italic.weight"); need(lang.type.accent_italic && lang.type.accent_italic.size_ratio, "language type.accent_italic.size_ratio"); need(theme.shadow && theme.shadow.rgb, "shadow.rgb");
const roleMap = { headline: "headline", subhead: "subhead", caption: "caption", list_item: "list_item", pill_label: "pill_label", display_number: "display_number", percent_label: "percent_label" };
const type = {};
for (const r of Object.keys(roleMap)) {
  const tr = need(theme.type.roles[r], "type.roles." + r);
  type[r] = { px: Math.round(lang.type.sizes_px[r] * need(tr.scale, "type.roles." + r + ".scale")), weight: need(tr.weight, "type.roles." + r + ".weight"), range_px: lang.type.size_range_px[r] };
}
const sh = (s, tint) => "0 " + s.y_px + "px " + s.blur_px + "px rgba(" + tint.rgb.join(",") + "," + s.alpha + ")";
const hl = need(theme.type.highlight, "type.highlight");

const tokens = {
  _generated: "kit/build-tokens.mjs: language.json + themes/" + themeName + ".json. Không sửa tay.",
  theme: themeName,
  canvas: lang.canvas,
  colors: { ...C },
  page: { tint: theme.page.tint, white: theme.page.white, tint_share: lang.page.tint_share, white_share: lang.page.white_share, grid: lang.page.grid },
  font: { family: theme.font.family, body_weight: theme.font.body_weight, accent_family: theme.font.accent_family },
  type: { ...type, line_height: need(theme.type.line_height_em, "type.line_height_em"), letter_spacing_em: need(theme.type.letter_spacing_em, "type.letter_spacing_em"), label_letter_spacing_em: need(theme.type.label_letter_spacing_em, "type.label_letter_spacing_em"), case: need(theme.type.case, "type.case"), highlight: hl, accent_italic: { size_ratio: lang.type.accent_italic.size_ratio, weight: theme.type.accent_italic.weight }, outline: { stroke_em: lang.type.outline.stroke_em }, strike: { thick_em: lang.type.strike.thick_em, line_cy_over_cap_h: lang.type.strike.line_cy_over_cap_h, cap_h_em: lang.type.outline.cap_h_em, baseline_em: lang.type.strike.baseline_from_box_top_em, overshoot: lang.type.strike.overshoot_each_side_over_text_w, dim: lang.type.strike.dim }, mark: { alpha: lang.type.mark.alpha, top: lang.type.mark.top_from_ink_top_over_ink_h, bottom: lang.type.mark.bottom_from_ink_top_over_ink_h } },
  card: { radius: lang.card.radius_px, shadow: sh(lang.card.shadow, theme.shadow), width_px: lang.card.width_px, padding: lang.card.padding },
  pill: { radius: lang.pill.radius_px, shadow: sh(lang.pill.shadow, theme.shadow), width_px: lang.pill.width_px, height_px: lang.pill.height_px, padding: lang.pill.padding },
  iso: theme.iso,
  safe: lang.safe, motion: lang.motion, transitions: lang.transitions, rhythm: lang.rhythm, guess: lang.guess, tabs: lang.tabs,
  catalog: Object.fromEntries(["component", "effect", "transition"].map((k) => [k, catalog.entries.filter((e) => e.kind === k).map((e) => e.name)])),
};
const outPath = path.resolve(arg("--out", path.join(here, "tokens.js")));
const body = "/* GENERATED — " + tokens._generated + " */\nwindow.KIT_TOKENS = " + JSON.stringify(tokens, null, 1) + ";\n";
if (process.argv.includes("--check")) {
  const cur = fs.existsSync(outPath) ? fs.readFileSync(outPath, "utf8") : "";
  if (cur !== body) { console.error(path.basename(outPath) + " lệch language.json/themes/" + themeName + ".json: chạy lại build-tokens.mjs"); process.exit(1); }
  console.log(path.basename(outPath) + " khớp (theme " + themeName + ", sha " + crypto.createHash("sha256").update(body).digest("hex").slice(0, 12) + ")");
} else { fs.writeFileSync(outPath, body); console.log("ghi", path.relative(process.cwd(), outPath), "(theme " + themeName + ")"); }
