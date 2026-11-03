#!/usr/bin/env bash
# Một lệnh từ script.json tới mp4 + báo cáo: sinh clip, render, hyperframes check, thử tua (seek), so DNA phong cách.
#   bash presets/corporate-motion/tools/make.sh <script.json> [--theme <tên>]
# Ghi cạnh script: clip/ (dự án HyperFrames sinh ra), preview/<job>[-theme].mp4, tmp/ (log, đo). Render nặng chạy dưới giới hạn 16G, --workers 1
# (nhiều worker làm khung tĩnh nhấp nháy). Render ra tệp tạm rồi mới `mv` đè mp4 cũ khi thành công (render lỗi không mất mp4 cũ).
# DỪNG ở bước lỗi đầu tiên (sinh, render, check, thử tua; thử tua "not run" cũng là lỗi). So DNA: sai cấu trúc (cỡ khung, fps, độ dài) là lỗi;
# lệch khoảng chỉ báo cáo. Thoát 0 khi mọi bước qua; 2 nếu thiếu mục trong catalog (không vẽ); 1 cho lỗi khác.
set -u
SCRIPT="" THEME=""
while [ $# -gt 0 ]; do
  case "$1" in
    --theme) [ $# -ge 2 ] && [ -n "$2" ] && [ "${2#-}" = "$2" ] || { echo "--theme cần một tên theme (vd --theme night)" >&2; exit 1; }; THEME="$2"; shift 2;;
    -*) echo "tham số lạ: $1" >&2; exit 1;;
    *) [ -z "$SCRIPT" ] || { echo "chỉ một script.json" >&2; exit 1; }; SCRIPT="$1"; shift;;
  esac
done
[ -f "$SCRIPT" ] || { echo "dùng: make.sh <script.json> [--theme <tên>]" >&2; exit 1; }
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; P="$(dirname "$HERE")"; SCRIPT="$(cd "$(dirname "$SCRIPT")" && pwd)/$(basename "$SCRIPT")"
JOB="$(dirname "$SCRIPT")"; OUT="$JOB/clip"; PREV="$JOB/preview"; TMP="$JOB/tmp"; mkdir -p "$PREV" "$TMP"
NAME="$(basename "$JOB")${THEME:+-$THEME}"; MP4="$PREV/$NAME.mp4"; MP4_NEW="$PREV/$NAME.tmp.mp4"
BUILD=(node "$HERE/build-clip.mjs" "$SCRIPT" "$OUT"); [ -n "$THEME" ] && BUILD+=(--theme "$THEME")
LINES=(); ok() { LINES+=("  $1: PASS${2:+ ($2)}"); }
finish() {   # $1 = mã thoát, $2 = bước dừng (rỗng nếu xong)
  echo; echo "================ make.sh: $(basename "$JOB")${THEME:+  theme=$THEME} ================"
  [ -f "$TMP/generate.log" ] && sed -n '1,10p' "$TMP/generate.log" && grep -E '^\s+(cảnh báo)' "$TMP/generate.log"
  printf '%s\n' "${LINES[@]}"
  if [ -n "$2" ]; then echo "  DỪNG ở bước: $2 (log trong $TMP/)"; fi
  if [ -z "$2" ]; then echo "  mp4: $MP4  ($(du -h "$MP4" | cut -f1))"; else echo "  mp4: không cập nhật"; fi
  exit "$1"
}

# 1. sinh (kiểm schema + catalog trước khi ghi)
"${BUILD[@]}" > "$TMP/generate.log" 2>&1; G=$?
if [ $G -ne 0 ]; then cat "$TMP/generate.log"; [ $G -eq 2 ] && echo "DỪNG: thiếu mục trong catalog, báo chủ, không vẽ tạm."; exit $G; fi
ok "sinh clip" "schema, catalog, tokens, scene không ghi đè language"

# 2. render (nặng: giới hạn bộ nhớ, một worker); ra tệp tạm, thành công mới đè mp4 cũ
rm -f "$MP4_NEW"
( cd "$OUT" && systemd-run --user --scope --quiet -p MemoryMax=16G npx -y hyperframes@latest render . -o "$MP4_NEW" --fps 30 --workers 1 --no-browser-gpu ) > "$TMP/render.log" 2>&1; R=$?
if [ $R -ne 0 ] || [ ! -s "$MP4_NEW" ]; then rm -f "$MP4_NEW"; tail -15 "$TMP/render.log"; LINES+=("  render: FAIL"); finish 1 render; fi
mv -f "$MP4_NEW" "$MP4"; ok render

# 3. hyperframes check
( cd "$OUT" && npx -y hyperframes@latest check ) > "$TMP/check.log" 2>&1; C=$?
CERR=$(grep -oE '[0-9]+ error\(s\)' "$TMP/check.log" | awk '{s+=$1} END{print s+0}'); CWARN=$(grep -oE '[0-9]+ warning\(s\)' "$TMP/check.log" | awk '{s+=$1} END{print s+0}')
if [ $C -ne 0 ] || [ "$CERR" -gt 0 ]; then grep -E '✗|error' "$TMP/check.log" | head -8; LINES+=("  hyperframes check: FAIL ($CERR lỗi)"); finish 1 "hyperframes check"; fi
ok "hyperframes check" "$CERR lỗi, $CWARN cảnh báo"

# 4. thử tua (jsdom cài một lần ngoài repo)
JD="${JSDOM_DIR:-/tmp/jsdom-env}"
if [ ! -d "$JD/node_modules/jsdom" ]; then LINES+=("  thử tua (seek): not run: thiếu jsdom ($JD; cài: mkdir -p /tmp/jsdom-env && cd /tmp/jsdom-env && npm i jsdom)"); finish 1 "thử tua (không chạy được)"; fi
JSDOM_DIR="$JD" node "$P/demo/seek-test.mjs" "$OUT/index.html" 0.4 > "$TMP/seek.log" 2>&1; K=$?
if [ $K -ne 0 ]; then tail -8 "$TMP/seek.log"; LINES+=("  thử tua (seek): FAIL"); finish 1 "thử tua"; fi
ok "thử tua (seek)" "$(tail -1 "$TMP/seek.log")"

# 5. so DNA: sai cấu trúc là lỗi; lệch khoảng chỉ báo cáo
uvx --with numpy python -I -B "$HERE/style-check.py" "$MP4" "$OUT/cuts.json" --tmp "$TMP" --json "$TMP/style-check.json" > "$TMP/style.log" 2>&1; S=$?
LINES+=("  so DNA: $(grep -oE 'trong khoảng: [0-9]+/[0-9]+' "$TMP/style.log" || echo '?') (xem $TMP/style.log)")
while IFS= read -r l; do LINES+=("      lệch: $l"); done < <(grep -E '\s(T|C)$' "$TMP/style.log")
if [ $S -ne 0 ]; then LINES+=("  so DNA cấu trúc: FAIL — $(grep -oE 'SAI CẤU TRÚC.*' "$TMP/style.log" || tail -2 "$TMP/style.log")"); finish 1 "so DNA (sai cấu trúc)"; fi
finish 0 ""
