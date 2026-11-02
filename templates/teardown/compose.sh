#!/usr/bin/env bash
# Chồng N scene thành preview/remake.mp4 theo mốc gốc (cuts.json) + joins.json, rồi so sánh + SSIM + ảnh điểm nối.
# Mốc cắt đọc từ cuts.json: {"S":[0, ...mốc..., TOTAL], "TOTAL":<giây, mặc định S cuối>, "fps":30, "size":[W,H], "bg":"0xRRGGBB"}.
# Scene k (1..N, N = số phần tử S − 1) nằm ở [S[k-1]-pre, S[k]+post] trên timeline chung; scene sau đè scene trước.
# Mỗi scene dùng scenes/sNN.mov (có alpha) nếu có, không thì scenes/sNN.mp4 (đục).
# File render của scene phải dài đúng pre + D + post.
# Chạy: bash compose.sh   (từ bất kỳ đâu)
set -euo pipefail
cd "$(dirname "$0")"
command -v jq >/dev/null || { echo "LỖI: cần jq"; exit 1; }
[ -f source.mp4 ] || { echo "LỖI: thiếu source.mp4 (bước 0)"; exit 1; }
jq -e '.S | type == "array" and length >= 2' cuts.json >/dev/null || { echo "LỖI: cuts.json cần khoá \"S\" (mảng >= 2 mốc, bắt đầu 0)"; exit 1; }
mapfile -t S < <(jq -r '.S[]' cuts.json)
N=$(( ${#S[@]} - 1 ))
TOTAL=$(jq -r '(.TOTAL // (.S | last))' cuts.json)
FPS=$(jq -r '(.fps // 30)' cuts.json)
W=$(jq -r '(.size // [1080,1920])[0]' cuts.json); H=$(jq -r '(.size // [1080,1920])[1]' cuts.json)
BG=$(jq -r '(.bg // "0xefece6")' cuts.json)
mkdir -p preview
inputs=(-f lavfi -i "color=c=$BG:s=${W}x${H}:r=$FPS:d=$TOTAL")
fc=""; last="0:v"
for k in $(seq 1 "$N"); do
  n=$(printf s%02d "$k")
  pre=$(jq -r ".${n}.pre // 0" joins.json); post=$(jq -r ".${n}.post // 0" joins.json)
  f="scenes/$n.mov"
  if [ ! -f "$f" ]; then
    f="scenes/$n.mp4"
    [ -f "$f" ] || { echo "LỖI: thiếu scenes/$n.mov và scenes/$n.mp4 (render scene $n trước)"; exit 1; }
    awk "BEGIN{exit !($pre+$post > 0)}" && { echo "LỖI: $n có pre/post > 0 nhưng không có $n.mov (cần nền trong suốt)"; exit 1; }
  fi
  dur=$(awk "BEGIN{printf \"%.4f\", ${S[$k]}-${S[$((k-1))]}+$pre+$post}")
  off=$(awk "BEGIN{printf \"%.4f\", ${S[$((k-1))]}-$pre}")
  have=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  awk "BEGIN{exit !($have+0.034 < $dur)}" && { echo "LỖI: $f dài $have s, cần $dur s (pre $pre + D + post $post)"; exit 1; }
  awk "BEGIN{exit !($have > $dur+0.034)}" && echo "CẢNH BÁO: $f dài $have s, dư so với $dur s (pre $pre + D + post $post) — phần dư bị cắt"
  inputs+=(-i "$f")
  fc+="[$k:v]fps=$FPS,trim=duration=$dur,setpts=PTS-STARTPTS+$off/TB,format=yuva444p[v$k];"
  fc+="[$last][v$k]overlay=eof_action=pass:format=auto[o$k];"
  last="o$k"
done
fc+="[$last]trim=duration=$TOTAL,format=yuv420p[out]"
ffmpeg -v error -y "${inputs[@]}" -filter_complex "$fc" -map "[out]" -r "$FPS" -c:v libx264 -crf 18 preview/remake.mp4
ffmpeg -v error -y -i source.mp4 -i preview/remake.mp4 -filter_complex \
  "[0:v]fps=$FPS,scale=$((W/2)):$((H/2))[a];[1:v]scale=$((W/2)):$((H/2))[b];[a][b]hstack" -an -c:v libx264 -crf 22 preview/compare.mp4
: > preview/ssim.txt
for k in $(seq 1 "$N"); do
  a=${S[$((k-1))]}; d=$(awk "BEGIN{printf \"%.3f\", ${S[$k]}-$a}")
  v=$(ffmpeg -v info -ss "$a" -t "$d" -i source.mp4 -ss "$a" -t "$d" -i preview/remake.mp4 -filter_complex \
    "[0:v]fps=$FPS,scale=$((W/4)):$((H/4)),format=gray[x];[1:v]scale=$((W/4)):$((H/4)),format=gray[y];[x][y]ssim" -f null - 2>&1 \
    | grep -o 'All:[0-9.]*' | cut -d: -f2)
  printf "s%02d %s\n" "$k" "$v" >> preview/ssim.txt
done
# ảnh điểm nối: 6 ô trái→phải = gốc@cut−0.1, remake@cut−0.1, gốc@cut, remake@cut, gốc@cut+0.1, remake@cut+0.1
# (mỗi cặp gốc|remake là một khung của compare.mp4). N−1 điểm nối.
mkdir -p preview/joins
for j in $(seq 1 $((N - 1))); do
  t=${S[$j]}
  # đúng 1 khung mỗi mốc: số khung = round((cut+dt)*fps)
  sel=$(for dt in -0.1 0 0.1; do printf "+eq(n\\\\,%d)" "$(awk "BEGIN{printf \"%d\", ($t+$dt)*$FPS+0.5}")"; done); sel=${sel#+}
  ffmpeg -v error -y -i preview/compare.mp4 -vf "select='$sel',scale=$((W/2)):-1,tile=3x1" -frames:v 1 "preview/joins/J$(printf %02d $j).jpg"
done
echo "remake: $(ffprobe -v error -show_entries format=duration -of csv=p=0 preview/remake.mp4)s"; cat preview/ssim.txt | tr '\n' ' '; echo
