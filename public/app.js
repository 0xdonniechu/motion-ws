const $ = (s) => document.querySelector(s);
const media = (p) => "/media/" + p;

async function api(url, opt) {
  const r = await fetch(url, opt);
  return r.json();
}

async function loadJobs() {
  const jobs = await api("/api/jobs");
  document.querySelectorAll(".col").forEach((col) => {
    const st = col.dataset.st;
    const box = col.querySelector(".cards");
    box.innerHTML = "";
    jobs.filter((j) => j.status === st).forEach((j) => box.appendChild(card(j)));
  });
}

function card(j) {
  const d = document.createElement("div");
  d.className = "card";
  const dur = j.duration ? Math.round(j.duration) + "s" : "";
  d.innerHTML = `
    ${j.sheet ? `<img src="${media("jobs/" + j.id + "/" + j.sheet)}">` : ""}
    <div class="t">${esc(j.title)}</div>
    <div class="m">${j.plane ? j.plane.num + " · " : ""}${j.id} · ${dur} ${j.frames ? "· " + j.frames + " frames" : ""}</div>
    <div class="m">${esc(j.note || "")}</div>
    <div class="row">
      ${j.status === "todo" ? `<button data-a="approve">Duyệt render</button>` : ""}
      ${j.status !== "done" && j.status !== "cancel" ? `<button data-a="done" class="ghost">Gắn output + Xong</button>` : ""}
      ${j.status !== "cancel" ? `<button data-a="cancel" class="ghost">Hủy</button>` : ""}
      ${j.status === "cancel" ? `<button data-a="todo" class="ghost">Mở lại</button>` : ""}
      ${j.src ? `<button data-a="play" class="ghost">Xem video</button>` : ""}
    </div>
    <div class="play"></div>`;
  d.querySelectorAll("button").forEach((b) => b.onclick = async () => {
    const a = b.dataset.a;
    if (a === "play") {
      const box = d.querySelector(".play");
      box.innerHTML = `<video controls src="${media("jobs/" + j.id + "/" + j.src)}"></video>`;
      return;
    }
    if (a === "approve") {
      await api("/api/jobs/" + j.id + "/approve", { method: "POST" });
      loadJobs();
      return;
    }
    if (a === "done") {
      const out = prompt("Đường dẫn file mp4 output (trong workspace):", "renders/" + j.id + ".mp4");
      if (out === null) return;
      await api("/api/jobs/" + j.id, { method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "done", output: out || null }) });
      loadJobs();
      return;
    }
    await api("/api/jobs/" + j.id, { method: "PATCH",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: a }) });
    loadJobs();
  });
  return d;
}
function esc(s) { return String(s ?? "").replace(/[&<>"]/g, (c) => `&#${c.charCodeAt(0)};`); }

$("#ingest").onsubmit = async (e) => {
  e.preventDefault();
  const url = $("#ingest-url").value.trim();
  if (!url) return;
  $("#ingest-url").value = "";
  await api("/api/ingest", { method: "POST",
    headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url }) });
  loadJobs();
  const t = setInterval(async () => {
    await loadJobs();
    const jobs = await api("/api/jobs");
    if (!jobs.some((j) => j.status === "processing" && j.url === url)) clearInterval(t);
  }, 5000);
};

$("#tab-board").onclick = () => switchTab("board");
$("#tab-explorer").onclick = () => switchTab("explorer");
function switchTab(t) {
  $("#tab-board").classList.toggle("active", t === "board");
  $("#tab-explorer").classList.toggle("active", t === "explorer");
  $("#view-board").hidden = t !== "board";
  $("#view-explorer").hidden = t !== "explorer";
  if (t === "explorer") loadTree(".", $("#tree"), 0);
}

async function loadTree(dir, el, depth) {
  const entries = await api("/api/files?dir=" + encodeURIComponent(dir));
  el.innerHTML = "";
  entries.forEach((e) => {
    if (e.name.startsWith(".") || e.name === "node_modules") return;
    const n = document.createElement("div");
    n.className = "tnode";
    const lbl = document.createElement("span");
    lbl.className = "lbl";
    lbl.textContent = (e.dir ? "📁 " : "📄 ") + e.name;
    n.appendChild(lbl);
    if (e.dir) {
      const kids = document.createElement("div");
      kids.className = "kids";
      lbl.onclick = () => {
        if (kids.innerHTML) { kids.innerHTML = ""; return; }
        if (depth < 4) loadTree(e.path, kids, depth + 1);
      };
      n.appendChild(kids);
    } else {
      lbl.onclick = () => preview(e.path);
    }
    el.appendChild(n);
  });
}

function preview(p) {
  const box = $("#preview");
  const ext = p.split(".").pop().toLowerCase();
  if (["mp4", "webm"].includes(ext))
    box.innerHTML = `<video controls src="${media(p)}"></video><p class="hint">${esc(p)}</p>`;
  else if (["jpg", "png", "gif"].includes(ext))
    box.innerHTML = `<img src="${media(p)}"><p class="hint">${esc(p)}</p>`;
  else
    box.innerHTML = `<p class="hint">${esc(p)} (không xem trước được)</p>`;
}

loadJobs();
