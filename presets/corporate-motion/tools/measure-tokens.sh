#!/usr/bin/env bash
# Đo token/chi phí của một lần chạy skill ở chế độ headless (không có chủ). Không đụng ~/.claude/hil (nhật ký thời gian chủ):
#   - `--setting-sources project,local`: KHÔNG nạp cài đặt/CLAUDE.md cấp user (nơi quy tắc ghi nhật ký chủ nằm), chỉ nạp .claude/ của repo;
#   - `--allowedTools` chỉ cho đọc presets/ và jobs/, ghi jobs/ (đường dẫn trong repo), chạy build-clip/make.sh, mkdir/date/ls; mọi thứ khác bị từ chối ở chế độ headless.
#   bash presets/corporate-motion/tools/measure-tokens.sh "/corporate-motion [--theme t] <chủ đề>" [tệp-json-ra]
# In: token vào/ra (không cache, ghi cache, đọc cache), chi phí, số lượt, và danh sách tệp mô hình đã đọc ngoài `--brief` + schema (lấy từ bản ghi phiên).
set -u
PROMPT="${1:-}"; [ -n "$PROMPT" ] || { echo 'dùng: measure-tokens.sh "/corporate-motion <chủ đề>" [tệp-json-ra]' >&2; exit 1; }
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"; OUTJ="${2:-/tmp/measure-tokens-$(date +%s).json}"
cd "$REPO" || exit 1
claude --help 2>&1 | grep -q -- '--setting-sources' || { echo "claude không có --setting-sources: dừng (không chạy khi chưa cô lập được cấp user)" >&2; exit 1; }
BASH_DEFAULT_TIMEOUT_MS=900000 BASH_MAX_TIMEOUT_MS=900000 claude -p "$PROMPT" --output-format json --setting-sources project,local --max-budget-usd 6 \
  --allowedTools "Read(presets/**)" "Read(jobs/**)" "Write(jobs/**)" "Edit(jobs/**)" "Bash(node presets/corporate-motion/tools/build-clip.mjs:*)" "Bash(bash presets/corporate-motion/tools/make.sh:*)" "Bash(mkdir:*)" "Bash(date:*)" "Bash(ls:*)" > "$OUTJ" 2> "$OUTJ.err"
echo "claude thoát $?; kết quả: $OUTJ"
python3 -I - "$OUTJ" "$REPO" <<'PY'
import json, sys, glob, os
d = json.load(open(sys.argv[1])); repo = sys.argv[2]; u = d.get("usage", {})
print("model: %s | lượt: %s | %.0fs | chi phí: $%.4f" % (", ".join(d.get("modelUsage", {})), d.get("num_turns"), d.get("duration_ms", 0) / 1000, d.get("total_cost_usd", 0)))
print("token: vào(không cache) %s | ghi cache %s | đọc cache %s | ra %s (suy luận %s)" % (u.get("input_tokens"), u.get("cache_creation_input_tokens"), u.get("cache_read_input_tokens"), u.get("output_tokens"), (u.get("output_tokens_details") or {}).get("thinking_tokens")))
print("từ chối quyền:", [x.get("tool_name") + ": " + json.dumps(x.get("tool_input"), ensure_ascii=False)[:70] for x in d.get("permission_denials", [])])
f = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % d.get("session_id")))
ok = ("script.schema.json", "build-clip.mjs --brief", "make.sh", "/script.json")
beyond = []
for line in open(f[0], encoding="utf8") if f else []:
    o = json.loads(line); c = (o.get("message") or {}).get("content")
    for b in c if isinstance(c, list) else []:
        if b.get("type") != "tool_use": continue
        i = b["input"]; t = b["name"]; s = i.get("file_path") or i.get("command") or ""
        if t == "Read" and not s.endswith(ok): beyond.append("Read " + s)
        elif t == "Bash" and not any(k in s for k in ok[:3]) and any(k in s for k in ("presets/", "jobs/", "catalog", "kit")) and not s.startswith(("mkdir", "date")): beyond.append("Bash " + s[:110])
print("đọc ngoài --brief + schema (%d):" % len(beyond)); [print("  -", x) for x in beyond]
PY
