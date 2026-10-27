const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const { execFile } = require("node:child_process");
const { promisify } = require("node:util");
const ex = promisify(execFile);

const ROOT = __dirname;
const JOBS_DIR = path.join(ROOT, "jobs");
const RENDERS_DIR = path.join(ROOT, "renders");
const DB = path.join(JOBS_DIR, "jobs.json");
const STATUSES = ["todo", "processing", "done", "cancel"];
fs.mkdirSync(JOBS_DIR, { recursive: true });
fs.mkdirSync(RENDERS_DIR, { recursive: true });

function loadJobs() {
  try { return JSON.parse(fs.readFileSync(DB, "utf8")); }
  catch { return []; }
}
function saveJobs(jobs) { fs.writeFileSync(DB, JSON.stringify(jobs, null, 2)); }
function send(res, code, obj, type = "application/json") {
  res.writeHead(code, { "Content-Type": type });
  res.end(typeof obj === "string" ? obj : JSON.stringify(obj));
}
function body(req) {
  return new Promise((resolve) => {
    let s = "";
    req.on("data", (c) => (s += c));
    req.on("end", () => { try { resolve(JSON.parse(s || "{}")); } catch { resolve({}); } });
  });
}
function scaffold(job) {
  const dir = path.join(JOBS_DIR, job.id, "hyperframes");
  fs.mkdirSync(dir, { recursive: true });
  const dur = Math.min(60, Math.max(5, Math.round(job.duration || 8)));
  const html = `<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8">
<meta name="viewport" content="width=1280, height=720">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { margin: 0; width: 1280px; height: 720px; overflow: hidden; background: #141414; }
body { font-family: system-ui, sans-serif; }
#root { position: relative; width: 1280px; height: 720px; }
#scene { position: absolute; inset: 0; }
h1 { position: absolute; top: 300px; width: 1280px; text-align: center; color: #f2f2f2; font-size: 44px; }
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="${dur}" data-width="1280" data-height="720" data-fps="30">
<div id="scene" class="clip" data-start="0" data-duration="${dur}" data-track-index="1">
<h1>${job.title.replace(/</g, "&lt;")}</h1>
</div></div>
<script>
/* GSAP timeline: window.__timelines["main"] = gsap.timeline({ paused: true }); */
window.__timelines = window.__timelines || {};
</script>
</body></html>`;
  fs.writeFileSync(path.join(dir, "index.html"), html);
  fs.writeFileSync(path.join(dir, "hyperframes.json"),
    JSON.stringify({ paths: { blocks: "compositions", components: "compositions/components", assets: "assets" } }, null, 2));
  return "hyperframes";
}

const MIME = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".mp4": "video/mp4", ".jpg": "image/jpeg",
  ".png": "image/png", ".gif": "image/gif", ".webm": "video/webm", ".txt": "text/plain" };

function slug() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

async function buildAnalysis(jobDir, srcFile) {
  const framesDir = path.join(jobDir, "frames");
  fs.mkdirSync(framesDir, { recursive: true });
  const { stdout } = await ex("ffprobe", ["-v", "error", "-show_entries",
    "format=duration,size:stream=width,height", "-of", "json", srcFile]);
  const info = JSON.parse(stdout);
  const dur0 = parseFloat(info.format.duration || 0);
  const step = Math.max(1, Math.round((dur0 * 30) / 48));
  await ex("ffmpeg", ["-y", "-v", "error", "-i", srcFile,
    "-vf", `select='not(mod(n\\,${step}))',scale=320:-1`, "-vsync", "0",
    "-frames:v", "48", path.join(framesDir, "f_%03d.jpg")]);
  const frames = fs.readdirSync(framesDir).filter((f) => f.endsWith(".jpg")).slice(0, 16);
  const sheet = path.join(jobDir, "contact-sheet.jpg");
  await ex("ffmpeg", ["-y", "-v", "error", "-i", path.join(framesDir, "f_%03d.jpg"),
    "-vf", "scale=320:-1,tile=4x4", "-frames:v", "1", sheet]);
  const st = fs.statSync(srcFile);
  const vs = (info.streams || []).find((s) => s.width) || {};
  return { duration: parseFloat(info.format.duration || 0),
    size: parseInt(info.format.size || st.size, 10),
    width: vs.width || 0, height: vs.height || 0,
    frames: frames.length, sheet: "contact-sheet.jpg", src: path.basename(srcFile) };
}

async function runIngest(job) {
  const jobs = loadJobs();
  const set = (patch) => {
    const i = jobs.findIndex((j) => j.id === job.id);
    if (i >= 0) { jobs[i] = { ...jobs[i], ...patch }; saveJobs(jobs); }
  };
  try {
    const jobDir = path.join(JOBS_DIR, job.id);
    let src;
    if (job.file) {
      src = path.join(jobDir, "source" + path.extname(job.file));
      fs.copyFileSync(job.file, src);
    } else {
      await ex("uvx", ["yt-dlp", "--no-playlist", "-f", "mp4/best",
        "-o", path.join(jobDir, "source.%(ext)s"), job.url]);
      src = fs.readdirSync(jobDir).map((f) => path.join(jobDir, f))
        .find((f) => /source\.(mp4|webm|mkv|mov)$/.test(f));
      if (!src) throw new Error("download produced no video file");
    }
    const a = await buildAnalysis(jobDir, src);
    set({ status: "todo", ...a, note: "ingest xong, chờ phân tích" });
  } catch (e) { set({ status: "todo", note: "ingest lỗi: " + String(e.message || e).slice(0, 200) }); }
}

const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, "http://x");
  const p = u.pathname;
  try {
    if (p === "/api/jobs" && req.method === "GET") return send(res, 200, loadJobs());
    if (p === "/api/ingest" && req.method === "POST") {
      const b = await body(req);
      if (!b.url && !b.file) return send(res, 400, { error: "need url or file" });
      if (b.file && !fs.existsSync(b.file)) return send(res, 400, { error: "file not found" });
      const jobs = loadJobs();
      const job = { id: slug(), title: b.title || (b.url ? "video " + slug() : path.basename(b.file)),
        url: b.url || null, file: b.file || null, status: "processing",
        created: new Date().toISOString(), note: "đang tải + phân tích", output: null };
      fs.mkdirSync(path.join(JOBS_DIR, job.id), { recursive: true });
      jobs.unshift(job); saveJobs(jobs);
      runIngest(job);
      return send(res, 200, job);
    }
    const ma = p.match(/^\/api\/jobs\/([\w-]+)\/approve$/);
    if (ma && req.method === "POST") {
      const jobs = loadJobs();
      const i = jobs.findIndex((j) => j.id === ma[1]);
      if (i < 0) return send(res, 404, { error: "no job" });
      if (jobs[i].status !== "todo") return send(res, 400, { error: "chỉ duyệt job ở todo" });
      const hf = scaffold(jobs[i]);
      jobs[i] = { ...jobs[i], status: "processing", note: "đã duyệt, khung render ở jobs/" + ma[1] + "/" + hf };
      saveJobs(jobs);
      return send(res, 200, jobs[i]);
    }
    const m = p.match(/^\/api\/jobs\/([\w-]+)$/);
    if (m && req.method === "PATCH") {
      const b = await body(req);
      const jobs = loadJobs();
      const i = jobs.findIndex((j) => j.id === m[1]);
      if (i < 0) return send(res, 404, { error: "no job" });
      if (b.status && !STATUSES.includes(b.status)) return send(res, 400, { error: "bad status" });
      jobs[i] = { ...jobs[i], ...b };
      saveJobs(jobs);
      return send(res, 200, jobs[i]);
    }
    if (p === "/api/files" && req.method === "GET") {
      const entries = listDir(u.searchParams.get("dir") || ".");
      if (!entries) return send(res, 400, { error: "bad dir" });
      return send(res, 200, entries);
    }
    if (p.startsWith("/media/")) {
      const rel = decodeURIComponent(p.slice(7));
      const abs = path.resolve(ROOT, rel);
      const ok = abs.startsWith(ROOT + path.sep) && !rel.split("/").some((s) => s.startsWith("."));
      if (!ok || !fs.existsSync(abs) || fs.statSync(abs).isDirectory())
        return send(res, 404, "not found", "text/plain");
      res.writeHead(200, { "Content-Type": MIME[path.extname(abs)] || "application/octet-stream" });
      return fs.createReadStream(abs).pipe(res);
    }
    let f = path.join(ROOT, "public", p === "/" ? "index.html" : decodeURIComponent(p.slice(1)));
    f = path.resolve(f);
    if (!f.startsWith(path.join(ROOT, "public")) || !fs.existsSync(f) || fs.statSync(f).isDirectory())
      return send(res, 404, "not found", "text/plain");
    res.writeHead(200, { "Content-Type": MIME[path.extname(f)] || "application/octet-stream" });
    return fs.createReadStream(f).pipe(res);
  } catch (e) { send(res, 500, { error: String(e.message || e) }); }
});

const PORT = process.env.PORT || 8901;
server.listen(PORT, "127.0.0.1", () => console.log(`video-workspace on http://127.0.0.1:${PORT}`));

function listDir(rel) {
  const abs = path.normalize ? path.join(ROOT, rel) : path.join(ROOT, rel);
  const resolved = path.resolve(abs);
  if (!resolved.startsWith(ROOT)) return null;
  if (!fs.existsSync(resolved) || !fs.statSync(resolved).isDirectory()) return null;
  return fs.readdirSync(resolved, { withFileTypes: true }).map((e) => ({
    name: e.name, dir: e.isDirectory(),
    path: path.relative(ROOT, path.join(resolved, e.name)),
  })).sort((a, b) => (b.dir - a.dir) || a.name.localeCompare(b.name));
}
