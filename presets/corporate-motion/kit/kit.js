/* corporate-motion kit: thư viện từ vựng cho scene HyperFrames (1080x1920, 30fps). Một preset sở hữu từ vựng của nó; scene chỉ GỌI theo tên trong catalog.json:
     Kit.make(name, parent, props)    component  (dựng DOM, trả về handle {el, ...})
     Kit.fx(name, tl, target, props)  effect     (thêm tween vào timeline paused của scene; target = handle hoặc element)
     Kit.tx(name, tl, props)          transition (dissolve | wash | hard | bar-wipe | flash)
   Scene không tự vẽ gì ngoài các lời gọi này (cần thành phần mới thì thêm vào catalog.json + kit.js + demo trước).
   Nạp: fonts/fonts.css, kit.css, gsap, tokens.js (SINH bởi build-tokens.mjs từ language.json + themes/<tên>.json), kit.js.
   Quy tắc: mọi giá trị từ window.KIT_TOKENS (không màu/font cứng ở đây); không Math.random, rAF/setTimeout/Date, onUpdate;
   chữ gõ và số đếm là span bật/tắt bằng tl.set ở các khung cố định nên tua tới/lui đều ra cùng khung hình. `at` = giây trên timeline của scene. */
(function () {
  "use strict";
  const T = window.KIT_TOKENS;
  if (!T) throw new Error("kit: nạp tokens.js trước kit.js");
  if (!window.gsap) throw new Error("kit: nạp gsap trước kit.js");
  const FPS = T.canvas.fps, W = T.canvas.w, H = T.canvas.h;
  const snap = (t) => Math.round(t * FPS) / FPS;   // các bước rời rạc dính vào lưới khung
  const px = (n) => n + "px";

  // ---------------------------------------------------------------- biến CSS từ tokens (theme + language)
  const lum = (h) => parseInt(h.slice(1, 3), 16) * 0.299 + parseInt(h.slice(3, 5), 16) * 0.587 + parseInt(h.slice(5, 7), 16) * 0.114;
  const rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  function gridInk(kind) {   // nét lưới: màu nhấn chính, alpha sao cho tương phản với nền tint = contrast_lum đo được (không phụ thuộc nền sáng hay tối)
    const c = T.colors.accent_primary, a = Math.min(1, T.page.grid[kind].contrast_lum / Math.abs(lum(T.page.tint) - lum(c)));
    const [r, g, b] = rgb(c); return "rgba(" + r + "," + g + "," + b + "," + a.toFixed(3) + ")";
  }
  function applyVars(root) {
    const s = (root || document.documentElement).style, set = (k, v) => s.setProperty("--k-" + k, v);
    const C = T.colors, ty = T.type, role = (name, key) => { set(key + "-px", px(ty[name].px)); set(key + "-weight", ty[name].weight); };
    set("font", '"' + T.font.family + '", system-ui, sans-serif'); set("body-weight", T.font.body_weight);
    set("accent-font", '"' + T.font.accent_family + '", Georgia, serif'); set("ital-weight", ty.accent_italic.weight); set("ital-size", ty.accent_italic.size_ratio + "em");
    set("ink", C.ink); set("ink-secondary", C.ink_secondary); set("accent", C.accent_primary); set("accent-dark", C.accent_dark); set("accent-mid", C.accent_mid); set("accent-light", C.accent_light);
    set("surface", C.surface); set("yellow", C.yellow); set("tint", T.page.tint); set("white", T.page.white);
    role("headline", "headline"); role("caption", "caption"); role("subhead", "subhead"); role("list_item", "list"); role("pill_label", "pill-label"); role("display_number", "display"); role("percent_label", "percent");
    set("line-height", ty.line_height); set("letter-spacing", ty.letter_spacing_em + "em"); set("label-ls", ty.label_letter_spacing_em + "em");
    set("headline-case", ty.case.headline); set("label-case", ty.case.label);
    const [ar, ag, ab] = rgb(C.accent_primary);
    set("acc-bg", ty.highlight.style === "marker" ? "linear-gradient(transparent 58%, rgba(" + ar + "," + ag + "," + ab + "," + ty.highlight.marker_alpha + ") 58%)" : "none");
    set("out-w", ty.outline.stroke_em + "em");   // chữ rỗng `^từ^`: nét viền, em
    const [yr, yg, yb] = rgb(C.mark), st = ty.strike;
    set("mark-bg", "rgba(" + yr + "," + yg + "," + yb + "," + ty.mark.alpha + ")"); set("mark-top", (ty.mark.top * 100).toFixed(1) + "%"); set("mark-h", ((ty.mark.bottom - ty.mark.top) * 100).toFixed(1) + "%");   // vệt tô `{từ}`
    set("strk-h", st.thick_em + "em"); set("strk-over", (st.overshoot * 100) + "%"); set("strk-top", (st.baseline_em - st.cap_h_em * (1 - st.line_cy_over_cap_h) - st.thick_em / 2).toFixed(4) + "em");   // gạch `[từ]`
    set("card-radius", px(T.card.radius)); set("card-shadow", T.card.shadow);
    set("pill-radius", px(T.pill.radius)); set("pill-shadow", T.pill.shadow); set("pill-h", px(T.pill.height_px)); set("pill-pl", px(T.pill.padding.left)); set("pill-pr", px(T.pill.padding.right));
    set("line-pitch", px(T.page.grid.line.pitch_px)); set("dot-pitch", px(T.page.grid.dot.pitch_px)); set("grid-ink", gridInk("line"));
  }
  applyVars();

  // ---------------------------------------------------------------- ease: thời lượng GSAP từ "thời gian chạm 98%" của language.json
  const reachCache = {};
  function reachU(ease, level) {   // u nhỏ nhất (0..1) để ease(u) >= level lần đầu
    level = level || 0.98; const key = ease + "@" + level;
    if (reachCache[key] === undefined) {
      const f = gsap.parseEase(ease); let u = 1;
      for (let i = 1; i <= 4000; i++) { if (f(i / 4000) >= level) { u = i / 4000; break; } }
      reachCache[key] = u;
    }
    return reachCache[key];
  }
  const durFor = (ease, reach) => reach / reachU(ease);   // language đo thời gian chạm 98%, GSAP cần tổng thời lượng
  const node = (t) => (t && t.el) || t;   // handle hoặc element

  // ---------------------------------------------------------------- DOM helpers
  function el(tag, cls, parent, style) {
    const e = document.createElement(tag); if (cls) e.className = cls;
    if (style) Object.assign(e.style, style); if (parent) parent.appendChild(e); return e;
  }
  const place = (e, o) => { e.style.position = "absolute"; ["x:left", "y:top", "w:width", "h:height"].forEach((m) => { const [k, p] = m.split(":"); if (o[k] !== undefined) e.style[p] = px(o[k]); }); return e; };
  function parseRich(text) {   // "Dashboard *đẹp* lắm": từ giữa dấu * là từ khoá nhấn; "~từ~" = nhấn nghiêng có chân; "^từ^" = chữ rỗng viền (outline); "{cụm}" = vệt tô vàng (effect mark); "[cụm]" = gạch ngang (effect strike)
    const out = []; let acc = false, ital = false, outl = false, mark = false, strk = false;
    for (const ch of Array.from(String(text).normalize("NFC"))) {
      if (ch === "*") acc = !acc; else if (ch === "~") ital = !ital; else if (ch === "^") outl = !outl;
      else if (ch === "{") mark = true; else if (ch === "}") mark = false; else if (ch === "[") strk = true; else if (ch === "]") strk = false;
      else out.push({ ch, acc, ital, outl, mark, strk });
    }
    return out;
  }
  function fillRich(host, text, perChar) {   // span theo từ (nowrap) rồi theo ký tự (nếu perChar); trả mảng token {i, c, caret, space}
    host.textContent = ""; const chars = []; let word = null, accWrap = null, lastKey = null, runKey = "", box = host;
    parseRich(text).forEach((t, i) => {
      const rk = t.mark ? "mark" : t.strk ? "strk" : "";   // vệt/gạch bao cả cụm (kể cả dấu cách) nên có span riêng ngoài các span từ; lồng nhau thì vệt thắng
      if (rk !== runKey) {
        runKey = rk; word = null; accWrap = null; lastKey = null; box = host;
        if (rk) { const run = el("span", "k-" + rk, host); if (rk === "mark") el("i", "k-mark__bg", run); box = el("span", "k-" + rk + "__t", run); if (rk === "strk") el("i", "k-strk__line", run).setAttribute("data-layout-allow-occlusion", ""); }   // vạch gạch cố ý phủ chữ: báo cho layout check
      }
      if (t.ch === " " || t.ch === "\n") { word = null; accWrap = null; lastKey = null; box.appendChild(document.createTextNode(" ")); if (perChar) chars.push({ i, space: true }); return; }
      if (!word) { word = el("span", "k-w", box); lastKey = null; }
      const mode = t.ital ? 2 : t.acc ? 1 : 0, key = mode + (t.outl ? "o" : "");
      if (key !== lastKey) { accWrap = mode === 2 ? el("span", "k-ital", word) : mode === 1 ? el("span", "k-acc", word) : word; if (t.outl) accWrap = el("span", "k-out", accWrap); lastKey = key; }
      if (perChar) { const c = el("span", "k-ch", accWrap); c.textContent = t.ch; const caret = el("i", "k-caret", c); chars.push({ i, c, caret }); }
      else accWrap.appendChild(document.createTextNode(t.ch));
    });
    return chars;
  }

  const ICONS = {   // viewBox 24, nét, tô bằng currentColor
    check: "M5 12.5l4.5 4.5L19 7.5", question: "M9.2 9a3 3 0 1 1 4.6 2.5c-1 .7-1.8 1.2-1.8 2.5M12 17.6v.01", "arrow-right": "M4 12h15M13 6l6 6-6 6", "arrow-down": "M12 4v15M6 13l6 6 6-6",
    pin: "M12 21s-6-5.6-6-10a6 6 0 1 1 12 0c0 4.4-6 10-6 10zM12 11a2 2 0 1 0 0 .01", user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 20c0-4 3.6-6 8-6s8 2 8 6",
    quote: "M10 8H6v5h3c0 2-1 3-3 4M20 8h-4v5h3c0 2-1 3-3 4", chart: "M5 20V11M12 20V5M19 20v-9", chat: "M4 5h16v11H9l-5 4z", plus: "M12 5v14M5 12h14",
  };
  const svg = (inner, vb) => { const s = document.createElementNS("http://www.w3.org/2000/svg", "svg"); s.setAttribute("viewBox", vb || "0 0 24 24"); s.innerHTML = inner; return s; };

  // ================================================================ COMPONENTS (kind: component)
  const C = {};
  C.page = (parent, o) => { o = o || {}; const e = el("div", "k-page k-page--" + (o.mode || "tint") + (o.grid ? " k-page--grid-" + o.grid : ""), parent); if (o.grid === "dot") e.style.setProperty("--k-grid-ink", gridInk("dot")); return { el: e }; };
  C.card = (parent, o) => { o = o || {}; const e = el("div", "k-card" + (o.cls ? " " + o.cls : ""), parent); place(e, Object.assign({ w: T.card.width_px }, o)); return { el: e }; };
  C.text = (parent, o) => {   // role: headline | caption | subhead | list | label | display | percent; text rỗng = khung để effect typing/countUp điền
    const e = el("div", "k-text k-" + (o.role || "headline") + (o.accent ? " k-c-accent" : ""), parent); place(e, o);
    if (o.align) e.style.textAlign = o.align; if (o.minH) e.style.minHeight = px(o.minH); if (o.size) e.style.fontSize = px(o.size);
    if (o.text !== undefined) fillRich(e, o.text, false); return { el: e };
  };
  C.accentBar = (parent, o) => { const e = el("div", "k-accentbar", parent); place(e, Object.assign({ w: 150, h: 14 }, o)); return { el: e }; };
  C.icon = (parent, o) => {
    const e = el("div", "k-icon k-tone-" + (o.tone || "accent"), parent); place(e, Object.assign({ w: o.size || 48, h: o.size || 48 }, o));
    e.appendChild(svg('<path d="' + ICONS[o.name] + '"/>')); return { el: e };
  };
  C.avatar = (parent, o) => { const s = o.size || 96, e = el("div", "k-avatar", parent); place(e, Object.assign({ w: s, h: s }, o)); e.style.fontSize = px(Math.round(s * 0.38)); e.textContent = o.initials || ""; return { el: e }; };
  C.progressBar = (parent, o) => { const e = el("div", "k-track", parent); place(e, Object.assign({ h: 22 }, o)); const fill = el("div", "k-fill", e); return { el: e, fill }; };
  C.barChart = (parent, o) => {   // values: chiều cao tương đối so với max (mặc định giá trị lớn nhất); baseline = đường đáy
    const e = el("div", "k-bars" + (o.highlightLast === false ? " k-bars--flat" : ""), parent); place(e, o); const max = o.max || Math.max.apply(null, o.values), bars = [];
    o.values.forEach((v) => bars.push(el("i", "k-bar", e, { width: px(o.barW || 60), height: px(Math.round(v / max * o.h)) })));
    if (o.baseline !== false) el("div", "k-baseline", parent, { position: "absolute", left: px(o.x), top: px(o.y + o.h), width: px(o.w) });
    return { el: e, bars };
  };
  C.lineChart = (parent, o) => {
    const e = el("div", "k-linechart", parent); place(e, o); const max = o.max || Math.max.apply(null, o.values), n = o.values.length;
    const pts = o.values.map((v, i) => [Math.round(i / (n - 1) * o.w), Math.round(o.h - v / max * (o.h - 12) - 6)]), d = pts.map((p) => p.join(",")).join(" ");
    e.appendChild(svg('<polygon class="k-area" points="0,' + o.h + " " + d + " " + o.w + "," + o.h + '"/><polyline class="k-line" points="' + d + '"/>' + pts.map((p) => '<circle class="k-dot" cx="' + p[0] + '" cy="' + p[1] + '" r="7"/>').join(""), "0 0 " + o.w + " " + o.h));
    return { el: e };
  };
  C.donutChart = (parent, o) => {   // value 0..1; vòng chạy bằng effect ringFill
    const s = o.size || 300, r = 46, e = el("div", "k-donut", parent); place(e, Object.assign({ w: s, h: s }, o)); const len = 2 * Math.PI * r;
    e.appendChild(svg('<circle class="k-ring-bg" cx="60" cy="60" r="' + r + '"/><circle class="k-ring" cx="60" cy="60" r="' + r + '" stroke-dasharray="' + len.toFixed(2) + '" stroke-dashoffset="' + (len * (1 - (o.value === undefined ? 1 : o.value))).toFixed(2) + '" transform="rotate(-90 60 60)"/>', "0 0 120 120"));
    if (o.label !== undefined) { const l = el("div", "k-text k-percent k-donut__label", e); l.textContent = o.label; }
    return { el: e, ring: e.querySelector(".k-ring"), len };
  };
  C.skeleton = (parent, o) => { const e = el("div", "k-skeleton", parent); place(e, o); (o.rows || []).forEach((w, i) => el("div", "k-sk", e, { top: px(i * (o.gap || 35)), width: px(w) })); return { el: e }; };
  C.kpi = (parent, o) => {   // số lớn (host cho countUp) + nhãn bên phải
    const e = el("div", "k-kpi", parent); place(e, o); const num = el("div", "k-text k-percent k-c-accent", e), label = el("div", "k-text k-label", e);
    if (o.value !== undefined) num.textContent = o.value; label.textContent = o.label || ""; return { el: e, num, label };
  };
  C.button = (parent, o) => { const e = el("div", "k-button", parent); place(e, o); e.textContent = o.label || ""; return { el: e }; };
  C.pill = (parent, o) => {   // pill tiến trình "CÂU n/N" + dải chấm; dùng effect pillHop để chuyển bước
    const total = o.total || 3, step = o.step || 1, e = el("div", "k-pill", parent); place(e, Object.assign({ w: T.pill.width_px }, o));
    const badge = el("div", "k-pill__badge", e), nb = [], nl = [];
    for (let i = 1; i <= total; i++) { const s = el("span", i === step ? "is-on" : "", badge); s.textContent = i; nb.push(s); }
    const lab = el("span", "", e); lab.appendChild(document.createTextNode((o.label || "CÂU") + " "));
    const num = el("span", "k-pill__n", lab); for (let i = 1; i <= total; i++) { const s = el("span", i === step ? "is-on" : "", num); s.textContent = i; nl.push(s); }
    lab.appendChild(document.createTextNode("/" + total));
    const track = el("div", "k-pill__track", e, { width: px((total - 1) * DOT_PITCH + 22), marginLeft: "auto" });
    for (let i = 0; i < total; i++) el("span", "k-pill__dot", track, { left: px(i * DOT_PITCH + 4) });
    const marker = el("span", "k-pill__marker k-anim", track, { left: px((step - 1) * DOT_PITCH) });
    return { el: e, k: { total, step, nb, nl, marker } };
  };
  C.dashboardCard = (parent, o) => {   // thẻ dashboard mock: tiêu đề, KPI, thanh tiến độ, biểu đồ cột, dòng xương
    const card = C.card(parent, o), iw = o.w - 160, e = card.el;
    const title = C.text(e, { role: "label", text: o.title, x: 80, y: 54 });
    const kpi = C.kpi(e, { x: 80, y: 118, label: o.kpi.label });
    const progress = C.progressBar(e, { x: 80, y: 250, w: iw });
    const chart = C.barChart(e, { x: 80, y: 330, w: iw, h: 400, values: o.bars, max: 400, barW: 84 });
    const skel = C.skeleton(e, { x: 80, y: 775, rows: o.skeleton || [620, 440] });
    return { el: e, title, kpi, num: kpi.num, progress, fill: progress.fill, chart, bars: chart.bars, skel };
  };
  C.statCard = (parent, o) => {   // thẻ số lớn: nhãn góc, dẫn, SỐ (host), đơn vị, vạch nhấn, rồi thanh chạy hoặc biểu đồ cột
    const card = C.card(parent, o), e = card.el, w = o.w, r = {};
    if (o.tag) r.tag = C.text(e, { role: "label", text: o.tag, y: 14 }).el, r.tag.style.right = px(44), r.tag.style.left = "auto";
    r.lead = C.text(e, { role: "subhead", text: o.lead, y: 70, x: 0, w, align: "center" }).el;
    r.num = C.text(e, { role: "display", y: 126, x: 0, w, align: "center", accent: true, size: Math.round(T.type.display_number.px * (o.numberScale || 240 / 154)) }).el; r.num.style.lineHeight = "1";
    r.unit = C.text(e, { role: "headline", text: o.unit, y: 388, x: 0, w, align: "center" }).el;
    if (o.highlight !== false) r.bar = C.accentBar(e, { x: Math.round((w - 150) / 2), y: 482 }).el;
    if (o.progress) { const pw = o.progressW || 574; r.progress = C.progressBar(e, { x: Math.round((w - pw) / 2), y: 530, w: pw, h: 26 }); r.fill = r.progress.fill; }
    if (o.chart) {
      r.chart = C.barChart(e, { x: 80, y: o.chart.top || 540, w: w - 160, h: o.chart.h || 160, values: o.chart.values, barW: o.chart.barW || 40 }); r.bars = r.chart.bars;
      if (o.chart.caption) r.caption = C.text(e, { role: "label", text: o.chart.caption, x: 0, y: (o.chart.top || 540) + (o.chart.h || 160) + 16, w, align: "center" }).el;
    }
    return Object.assign({ el: e }, r);
  };
  C.quoteCard = (parent, o) => {   // thẻ câu chốt: dấu ngoặc kép, nhãn nguồn chung, dòng 1 (tĩnh), dòng 2 (khung gõ nếu không có text)
    const card = C.card(parent, o), e = card.el, iw = o.w - 160;
    const mark = el("div", "k-text k-quotemark k-c-accent", e); mark.textContent = "“";
    const tag = C.text(e, { role: "label", text: o.tag, x: 80, y: 250, w: iw }).el;
    const line1 = C.text(e, { role: "headline", text: o.line1, x: 80, y: 330, w: iw }).el;
    const line2 = C.text(e, { role: "headline", text: o.line2, x: 80, y: 520, w: iw, minH: 180 }).el;
    return { el: e, mark, tag, line1, line2 };
  };
  C.mapCard = (parent, o) => {   // bản đồ mock: đường phố + ghim (pins: [[fx, fy], ...] theo tỉ lệ thẻ)
    const card = C.card(parent, Object.assign({ cls: "k-mapcard" }, o)), e = card.el, roads = o.roads || [[0, 22, 100, 22], [0, 52, 100, 52], [0, 80, 100, 80], [20, 0, 20, 100], [55, 0, 55, 100], [82, 0, 82, 100], [0, 96, 100, 6]];
    e.appendChild(svg(roads.map((r) => '<line class="k-road" x1="' + r[0] + '" y1="' + r[1] + '" x2="' + r[2] + '" y2="' + r[3] + '"/>').join(""), "0 0 100 100"));
    e.lastChild.setAttribute("preserveAspectRatio", "none"); e.lastChild.setAttribute("class", "k-roads");
    const pins = (o.pins || []).map((p) => el("i", "k-bar k-pin", e, { left: px(Math.round(p[0] * o.w) - 15), top: px(Math.round(p[1] * o.h) - 46) }));
    return { el: e, pins };
  };
  C.iconCard = (parent, o) => { const card = C.card(parent, o), e = card.el; e.classList.add("k-rowcard");
    const icon = C.icon(e, { name: o.icon, size: o.iconSize || 84, tone: "accent" }).el; icon.style.position = "static"; icon.style.flex = "none";
    const text = C.text(e, { role: o.role || "list", text: o.text }).el; text.style.position = "static"; return { el: e, icon, text }; };
  C.listCard = (parent, o) => {   // hàng checklist: tick (popIn) + câu
    const card = C.card(parent, o), e = card.el; e.classList.add("k-rowcard");
    const tick = el("div", "k-tick", e); C.icon(tick, { name: o.icon || "check", size: 48, tone: "surface" }).el.style.position = "static";
    const text = C.text(e, { role: "list", text: o.text }).el; text.style.position = "static"; return { el: e, tick, text };
  };
  C.stepCard = (parent, o) => { const card = C.card(parent, o), e = card.el; e.classList.add("k-rowcard");
    const badge = el("div", "k-badge", e); badge.textContent = o.n; const text = C.text(e, { role: "list", text: o.text }).el; text.style.position = "static"; return { el: e, badge, text }; };
  C.connector = (parent, o) => {   // mũi tên dọc nối hai thẻ (x = tâm, y = đầu trên, h = chiều cao)
    const e = el("div", "k-connector", parent); place(e, { x: o.x - 18, y: o.y, w: 36, h: o.h }); el("i", "k-connector__line", e, { height: px(o.h - 30) });
    const a = C.icon(e, { name: "arrow-down", size: 36, tone: "accent" }).el; a.style.top = px(o.h - 36); a.style.left = "0"; return { el: e };
  };
  C.table = (parent, o) => {   // columns: ["Cột", ...]; rows: [["a","b"], ...]; highlight: chỉ số hàng nhấn
    const card = C.card(parent, Object.assign({ h: (o.rowH || 84) * (o.rows.length + 1) }, o)), e = card.el; e.classList.add("k-table"); const n = o.columns.length, rows = [];
    const row = (cells, cls) => { const r = el("div", "k-tr " + cls, e, { gridTemplateColumns: "repeat(" + n + ",1fr)", height: px(o.rowH || 84) }); cells.forEach((c) => { const d = el("div", "k-td", r); d.textContent = c; }); return r; };
    row(o.columns, "k-tr--head"); o.rows.forEach((r, i) => rows.push(row(r, i === o.highlight ? "k-tr--hl" : ""))); return { el: e, rows };
  };
  C.tabs = (parent, o) => {   // dải tab (pill chọn trượt): labels 2-4, active = tab đang chọn; con trỏ (cursor) nằm sẵn trong dải, hiện khi effect tabSwitch gọi
    const n = o.labels.length, tb = T.tabs, dw = tb.pitch_px * n, pitch = o.w ? o.w / n : tb.pitch_px, w = Math.round(pitch * n), active = o.active || 1, e = el("div", "k-tabs", parent);
    place(e, Object.assign({ w: dw, h: tb.strip_h_px }, o)); e.style.setProperty("--k-tab-pill-h", px(tb.pill_h_px)); e.style.setProperty("--k-tab-label-px", px(Math.round(T.type.pill_label.px * tb.label_scale_of_pill_label)));
    const inset = tb.pill_inset_px, pill = el("i", "k-tabs__pill", e, { left: px((active - 1) * pitch + inset), right: px(w - active * pitch + inset) }), labels = [];
    o.labels.forEach((t, i) => { const l = el("span", "k-tab", e, { left: px(i * pitch), width: px(pitch) }), off = el("b", "k-tab__off", l, { opacity: i + 1 === active ? 0 : 1 }), on = el("b", "k-tab__on", l, { opacity: i + 1 === active ? 1 : 0 }); off.textContent = t; on.textContent = t; labels.push({ off, on }); });
    const cursor = el("i", "k-cursor k-hold", e); cursor.appendChild(svg('<polygon points="2,2 2,39 12,30 19,46 26,43 19,29 33,29"/>', "0 0 " + tb.cursor.w_px + " " + tb.cursor.h_px));
    cursor.style.width = px(tb.cursor.w_px); cursor.style.height = px(tb.cursor.h_px);
    return { el: e, pill, cursor, labels, k: { n, pitch, w, inset, cur: active, pos: null } };
  };

  C.chatBox = (parent, o) => {   // messages: [{from: "user"|"bot", text}]
    const e = el("div", "k-chat", parent); place(e, o); const bubbles = (o.messages || []).map((m) => { const b = el("div", "k-bubble k-bubble--" + (m.from || "bot"), e); b.textContent = m.text; return b; });
    return { el: e, bubbles };
  };

  // ================================================================ EFFECTS (kind: effect)
  const F = {};
  F.fadeUp = (tl, t, o) => {   // ĐOÁN (language.guess): chữ/khối vào nhẹ
    o = o || {}; const e = node(t), g = T.guess.fade_up; e.classList.add("k-anim");
    tl.fromTo(e, { y: o.y === undefined ? g.y_px : o.y, opacity: 0 }, { y: 0, opacity: 1, duration: o.duration || g.duration_s, ease: o.ease || g.ease }, o.at || 0);
  };
  F.slideIn = (tl, t, o) => {   // card_slide_in
    o = o || {}; const e = node(t), m = T.motion.card_slide_in, at = o.at || 0, from = o.from || "bottom";
    const dist = o.dist === undefined ? Math.round(m.distance_frac * (m.distance_of === "H" ? H : W)) : o.dist;
    const prop = from === "bottom" || from === "top" ? "y" : "x", sign = from === "bottom" || from === "right" ? 1 : -1;
    e.classList.add("k-anim");
    tl.fromTo(e, { [prop]: sign * dist }, { [prop]: 0, duration: durFor(m.ease, o.reach || m.reach_s), ease: m.ease }, at);
    const fade = o.fade === undefined ? 0.1 : o.fade;
    if (fade > 0) tl.fromTo(e, { opacity: 0 }, { opacity: 1, duration: fade, ease: "none" }, at);
    else if (at > 0) { e.classList.add("k-hold"); tl.set(e, { opacity: 1 }, at); }   // ẩn mặc định bằng CSS (.k-hold), hiện ở `at`; không dùng tl.set ở thời điểm 0 (tua lùi về 0 đảo thứ tự các set)   // fade 0: hiện ngay ở `at`. Không dùng fromTo thời lượng 0: lúc dựng nó ghi giá trị ĐÍCH (opacity 1), nên thẻ hiện sớm ở lần chạy đầu và ẩn sau khi tua lùi
  };
  F.typing = (tl, t, o) => {   // typed_text: ký tự/giây từ language (trung vị 21.3); trả thời điểm gõ xong
    const host = node(t), cps = o.cps || T.motion.typed_text.chars_per_s, at = snap(o.at || 0), chars = fillRich(host, o.text, true), vis = chars.filter((c) => !c.space);
    host.classList.add("k-anim");
    vis.forEach((c, k) => {
      tl.set(c.c, { opacity: 1 }, snap(at + c.i / cps));
      if (o.caret !== false) { const nxt = vis[k + 1], off = nxt ? snap(at + nxt.i / cps) : snap(at + (c.i + 1) / cps + (o.caretHold === undefined ? 0.5 : o.caretHold)); tl.set(c.caret, { opacity: 1 }, snap(at + c.i / cps)); tl.set(c.caret, { opacity: 0 }, off); }
    });
    return snap(at + chars.length / cps);
  };
  const fmt = (n, o) => { const d = o.decimals || 0, s = Math.abs(n).toFixed(d), p = s.split("."), g = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, "."); return (o.prefix || "") + (n < 0 ? "-" : "") + g + (p[1] ? "," + p[1] : "") + (o.suffix || ""); };
  F.countUp = (tl, t, o) => {   // number_count_up: mỗi khung một span (giá trị = ease(u) tại khung đó); from > to cũng được
    const host = t.num || node(t), m = T.motion.number_count_up, ease = o.ease || m.ease, from = o.from || 0, at = snap(o.at || 0);
    const D = durFor(ease, o.reach || m.reach_s), f = gsap.parseEase(ease), n = Math.ceil(D * FPS);
    host.textContent = ""; host.classList.add("k-count", "k-count--" + (o.align || "left"));
    el("span", "k-count__ghost", host).textContent = fmt(Math.abs(o.to) >= Math.abs(from) ? o.to : from, o);
    const steps = []; let last = null;
    for (let i = 0; i <= n; i++) { const u = Math.min(1, i / (D * FPS)), v = from + (o.to - from) * f(u), s = fmt(o.decimals ? v : Math.round(v), o); if (s !== last) { steps.push({ t: snap(at + i / FPS), s }); last = s; } }
    let prev = null;
    steps.forEach((st, k) => { const sp = el("span", "k-count__v", host); sp.textContent = st.s; if (prev) tl.set(prev, { opacity: 0 }, st.t); if (k === 0) sp.classList.add("k-count__v--on"); else tl.set(sp, { opacity: 1 }, st.t); prev = sp; });   // giá trị đầu hiện sẵn bằng CSS
    return snap(at + D);
  };
  F.barFill = (tl, t, o) => {   // bar_fill; like: "count" -> cùng ease/thời gian với số đếm (đếm qua thanh chạy)
    o = o || {}; const e = t.fill || node(t), m = o.like === "count" ? T.motion.number_count_up : T.motion.bar_fill, ease = o.ease || m.ease; e.classList.add("k-anim");
    const D = durFor(ease, o.reach || m.reach_s); tl.fromTo(e, { scaleX: 0 }, { scaleX: o.to === undefined ? 1 : o.to, duration: D, ease }, o.at || 0); return (o.at || 0) + D;
  };
  F.chartPop = (tl, t, o) => {   // chart_pop: mọi cột chung ease/thời lượng/quá đà của cột 1; so le [0.167, 0.133]
    o = o || {}; const bars = Array.isArray(t) ? t : (t.bars || [node(t)]), m = T.motion.chart_pop, st = o.stagger || m.stagger_s, D = durFor(m.ease, o.reach || m.reach_s); let at = o.at || 0, end = at;
    bars.forEach((b, i) => { b.classList.add("k-anim"); tl.fromTo(b, { scaleY: 0 }, { scaleY: 1, duration: D, ease: m.ease }, at); end = at + D; at += Array.isArray(st) ? st[i % st.length] : st; });
    return end;
  };
  F.popIn = (tl, t, o) => {   // cùng ease/thời lượng/quá đà với chart_pop, nhưng phóng đều hai chiều từ tâm (dấu tick, ghim, huy hiệu)
    o = o || {}; const list = Array.isArray(t) ? t : [node(t)], m = T.motion.chart_pop, st = o.stagger || m.stagger_s, D = durFor(m.ease, o.reach || m.reach_s); let at = o.at || 0, end = at;
    list.forEach((b, i) => { b.classList.add("k-anim"); tl.fromTo(b, { scale: 0 }, { scale: 1, duration: D, ease: m.ease }, at); end = at + D; at += Array.isArray(st) ? st[i % st.length] : st; });
    return end;
  };
  F.ringFill = (tl, t, o) => {   // vòng donut chạy tới `to` (0..1), cùng bar_fill
    const h = t, m = T.motion.bar_fill, D = durFor(m.ease, o.reach || m.reach_s);
    tl.fromTo(h.ring, { strokeDashoffset: h.len }, { strokeDashoffset: h.len * (1 - o.to), duration: D, ease: m.ease }, o.at || 0); return (o.at || 0) + D;
  };
  F.pulse = (tl, t, o) => {   // button_pulse: phồng (power1.in) rồi bấm (expo.out)
    o = o || {}; const e = node(t), m = T.motion.button_pulse, rel = durFor(m.release_ease, m.release_s); let at = o.at || 0; e.classList.add("k-anim");
    for (let i = 0; i < (o.pulses || 1); i++) {
      // immediateRender:false: tween thứ hai trên cùng thuộc tính không được ghi trạng thái "từ" lúc dựng timeline (nút sẽ phồng 1.175 trước khi bấm)
      tl.fromTo(e, { scale: 1 }, { scale: m.scale, duration: durFor(m.ease, o.reach || m.reach_s), ease: m.ease, immediateRender: false }, at); at += durFor(m.ease, o.reach || m.reach_s);
      tl.fromTo(e, { scale: m.scale }, { scale: 1, duration: rel, ease: m.release_ease, immediateRender: false }, at); at += rel + (o.gap || 0.3);
    }
    return at;
  };
  const DOT_PITCH = 36;
  F.pillHop = (tl, t, o) => {   // pill_progress: chấm nhảy đúng 1 khung, pop 1.08, nhãn đổi số
    const k = t.k, m = T.motion.pill_progress, from = k.step, to = o.to === undefined ? from + 1 : o.to, at = snap(o.at || 0), base = k.base === undefined ? (k.base = from) : k.base;
    tl.set(k.marker, { x: (to - base) * DOT_PITCH }, at);
    tl.fromTo(k.marker, { scale: m.pop_scale }, { scale: 1, duration: Math.max(m.settle_s, 1 / FPS), ease: "none", immediateRender: false }, at);   // false: chấm chỉ pop 1.08 từ lúc nhảy, không phải từ đầu timeline
    tl.set(k.nb[from - 1], { opacity: 0 }, at); tl.set(k.nb[to - 1], { opacity: 1 }, at); tl.set(k.nl[from - 1], { opacity: 0 }, at); tl.set(k.nl[to - 1], { opacity: 1 }, at);
    k.step = to; return at;
  };
  F.tabSwitch = (tl, t, o) => {   // tab_switch + cursor_glide: con trỏ lướt tới tab đích (power2.inOut), tới nơi thì pill đổi tab: cạnh dẫn back.out chạy trước, cạnh theo sau power1.out chạy muộn
    const k = t.k, M = T.motion.tab_switch, G = T.motion.cursor_glide, tb = T.tabs, to = o.to, at = snap(o.at || 0), from = k.cur;
    let start = at;
    if (o.cursor !== false) {
      const tip = [Math.round((to - 1) * k.pitch + k.pitch / 2 + tb.cursor.tip_dx_frac_pitch * k.pitch), tb.cursor.tip_dy_px_from_strip_top], c = t.cursor, org = k.pos || [tip[0] + G.origin_offset_px[0], tip[1] + G.origin_offset_px[1]];
      const show = Math.max(at, 1 / FPS);   // không tl.set ở thời điểm 0 (tua lùi về 0 đảo thứ tự các set)
      c.classList.add("k-anim"); tl.set(c, { opacity: 1 }, show);
      tl.fromTo(c, { x: org[0], y: org[1] }, { x: tip[0], y: tip[1], duration: durFor(G.ease, G.reach_s), ease: G.ease, immediateRender: false }, show);
      k.pos = tip; start = snap(show + G.reach_s);
    }
    if (to !== from) {
      const R = k.w - (to * k.pitch - k.inset), L = (to - 1) * k.pitch + k.inset, R0 = k.w - (from * k.pitch - k.inset), L0 = (from - 1) * k.pitch + k.inset, right = to > from;
      const lead = right ? { prop: "right", a: R0, b: R } : { prop: "left", a: L0, b: L }, trail = right ? { prop: "left", a: L0, b: L } : { prop: "right", a: R0, b: R };
      const dl = M.lead_edge.dur_s, p = t.pill; p.classList.add("k-anim");
      tl.fromTo(p, { [lead.prop]: lead.a }, { [lead.prop]: lead.b, duration: dl, ease: M.lead_edge.ease, immediateRender: false }, start);
      tl.fromTo(p, { [trail.prop]: trail.a }, { [trail.prop]: trail.b, duration: durFor(M.trail_edge.ease, M.trail_edge.reach_s), ease: M.trail_edge.ease, immediateRender: false }, start);
      const sw = snap(start + dl * T.guess.tab_label_swap.at_frac_of_lead_dur);
      tl.set(t.labels[from - 1].on, { opacity: 0 }, sw); tl.set(t.labels[from - 1].off, { opacity: 1 }, sw); tl.set(t.labels[to - 1].on, { opacity: 1 }, sw); tl.set(t.labels[to - 1].off, { opacity: 0 }, sw);
      k.cur = to;
    }
    return snap(start + M.lead_edge.dur_s);
  };

  F.strike = (tl, t, o) => {   // strike: vạch gạch ngang (đầu tròn, màu nhấn) quét trái -> phải qua mọi cụm [..] trong chữ, rồi chữ ngả xám sau 1 khung
    const host = node(t), m = T.motion.strike, d = T.type.strike.dim, at = snap(o.at || 0), D = durFor(m.ease, m.reach_s);
    host.querySelectorAll(".k-strk").forEach((r) => {
      const line = r.querySelector(".k-strk__line"), txt = r.querySelector(".k-strk__t"); line.classList.add("k-anim");
      tl.fromTo(line, { scaleX: 0 }, { scaleX: 1, duration: D, ease: m.ease }, at);
      tl.fromTo(txt, { opacity: 1, filter: "grayscale(0)" }, { opacity: d.opacity, filter: "grayscale(" + d.grayscale + ")", duration: m.dim_delay_frames / FPS, ease: "none" }, at);   // đúng 1 khung: khung `at` còn nguyên màu, khung kế tiếp đã xám (không có khung giữa); fromTo (không tl.set) để style nội tuyến nhất quán khi tua
    });
    return snap(at + D);
  };
  F.mark = (tl, t, o) => {   // mark: vệt tô vàng quét trái -> phải sau mọi cụm {..} trong chữ
    const host = node(t), m = T.motion.mark, at = snap(o.at || 0), D = durFor(m.ease, m.reach_s);
    host.querySelectorAll(".k-mark__bg").forEach((b) => { b.classList.add("k-anim"); tl.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: D, ease: m.ease }, at); });
    return snap(at + D);
  };

  // ================================================================ TRANSITIONS (kind: transition)
  // `from`, `to`: hai cảnh (clip) chồng nhau trong [at, at+d]; `to` nằm trên `from`; data-start của `to` <= at, data-duration của `from` tới >= at+d.
  const X = {};
  const txPrep = (tl, o, kind) => {
    if (!o.from || !o.to || o.from.parentElement !== o.to.parentElement) throw new Error("kit: transition cần from/to là hai cảnh cùng cha");
    const cfg = T.transitions[kind]; const d = o.dur || cfg.duration_s; o.to.classList.add("k-anim"); if (kind === "hard" || kind === "wash" || kind === "flash-wipe") o.to.classList.add("k-hold");   // `to` ẩn (CSS) tới lúc vào; dissolve giấu bằng tween opacity, bar-wipe bằng clipPath
    return { at: snap(o.at), d, parent: o.parent || o.to.parentElement };
  };
  X.hard = (tl, o) => { const p = txPrep(tl, o, "hard"); tl.set(o.to, { opacity: 1 }, p.at); tl.set(o.from, { opacity: 0 }, snap(p.at + 1 / FPS)); return snap(p.at + 1 / FPS); };
  X.dissolve = (tl, o) => { const p = txPrep(tl, o, "dissolve"); tl.fromTo(o.to, { opacity: 0 }, { opacity: 1, duration: p.d, ease: "none" }, p.at); return p.at + p.d; };
  const overlay = (kind, tl, o, cfgKey) => {   // wash/flash: lớp phủ phủ kín tới giữa cửa sổ, đổi cảnh, rồi mở
    const p = txPrep(tl, o, cfgKey), half = p.d / 2, ov = el("div", "k-tx k-tx--" + kind, p.parent); ov.classList.add("k-anim");   // màu lớp phủ lấy từ theme qua CSS
    const mid = snap(p.at + half);   // hai nửa nối khít tại mốc đã dính khung: không chồng lấn trên cùng thuộc tính (chồng lấn làm tua tiến/lùi ra khác nhau)
    tl.fromTo(ov, { opacity: 0 }, { opacity: 1, duration: mid - p.at, ease: kind === "flash" ? "power1.in" : "none" }, p.at);
    tl.set(o.to, { opacity: 1 }, mid);
    tl.fromTo(ov, { opacity: 1 }, { opacity: 0, duration: p.at + p.d - mid, ease: kind === "flash" ? "power1.out" : "none", immediateRender: false }, mid);
    return p.at + p.d;
  };
  X.wash = (tl, o) => overlay("wash", tl, o, "wash");
  X.flash = (tl, o) => overlay("flash", tl, o, "flash-wipe");
  X["bar-wipe"] = (tl, o) => {   // dải xanh quét trái -> phải; cảnh `to` lộ ra sau mép trái của dải
    const p = txPrep(tl, o, "bar-wipe"), bw = o.barW || Math.round(W * 0.38), ov = el("div", "k-tx k-tx--bar k-anim", p.parent, { width: px(bw) }), lead = bw / (W + bw) * p.d;
    tl.fromTo(ov, { x: -bw }, { x: W, duration: p.d, ease: "none" }, p.at);
    tl.fromTo(o.to, { clipPath: "inset(0px " + W + "px 0px 0px)" }, { clipPath: "inset(0px 0px 0px 0px)", duration: p.d - lead, ease: "none" }, p.at + lead);
    return p.at + p.d;
  };

  // ================================================================ đăng ký + khớp catalog
  const REG = { component: C, effect: F, transition: X };
  if (T.catalog) {   // catalog.json là nguồn tên; lệch với cài đặt thì dừng
    for (const kind of Object.keys(REG)) {
      const want = (T.catalog[kind] || []).slice().sort().join(","), have = Object.keys(REG[kind]).sort().join(",");
      if (want !== have) throw new Error("kit: catalog.json lệch kit.js ở " + kind + ": catalog=[" + want + "] kit=[" + have + "]");
    }
  }
  const call = (kind, name) => { const f = REG[kind][name]; if (!f) throw new Error("kit: không có " + kind + " '" + name + "' trong catalog"); return f; };
  window.Kit = {
    tokens: T, FPS, W, H, snap,
    make: (name, parent, props) => call("component", name)(parent, props || {}),
    fx: (name, tl, target, props) => call("effect", name)(tl, target, props || {}),
    tx: (name, tl, props) => call("transition", name)(tl, props),
    scene: (id) => document.getElementById(id),   // vỏ cảnh (clip) viết tĩnh trong HTML: data-start/data-duration
  };
})();
