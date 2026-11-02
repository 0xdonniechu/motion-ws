#!/usr/bin/env bash
# Chồng 17 scene thành preview/remake.mp4 theo mốc gốc + joins.json, rồi so sánh + SSIM.
# Scene k (1..17) nằm ở [S[k-1]-pre, S[k]+post] trên timeline chung; scene sau đè scene trước.
# Mỗi scene dùng scenes/sNN.mov (có alpha) nếu có, không thì scenes/sNN.mp4 (đục).
# File render của scene phải dài đúng pre + D + post.
# Chạy: bash compose.sh   (từ bất kỳ đâu)
set -euo pipefail
cd "$(dirname "$0")"
S=(0 1.00 2.75 4.10 6.00 6.70 7.90 9.20 13.00 16.20 18.70 19.40 21.00 24.00 28.40 30.40 33.00 36.03)
TOTAL=36.03
mkdir -p preview
inputs=(-f lavfi -i "color=c=0xefece6:s=1080x1920:r=30:d=$TOTAL")
fc=""; last="0:v"
for k in $(seq 1 17); do
  n=$(printf s%02d "$k")
  pre=$(jq -r ".${n}.pre // 0" joins.json); post=$(jq -r ".${n}.post // 0" joins.json)
  f="scenes/$n.mov"
  if [ ! -f "$f" ]; then
    f="scenes/$n.mp4"
    awk "BEGIN{exit !($pre+$post > 0)}" && { echo "LỖI: $n có pre/post > 0 nhưng không có $n.mov (cần nền trong suốt)"; exit 1; }
  fi
  dur=$(awk "BEGIN{printf \"%.4f\", ${S[$k]}-${S[$((k-1))]}+$pre+$post}")
  off=$(awk "BEGIN{printf \"%.4f\", ${S[$((k-1))]}-$pre}")
  have=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  awk "BEGIN{exit !($have+0.034 < $dur)}" && { echo "LỖI: $f dài $have s, cần $dur s (pre $pre + D + post $post)"; exit 1; }
  awk "BEGIN{exit !($have > $dur+0.034)}" && echo "CẢNH BÁO: $f dài $have s, dư so với $dur s (pre $pre + D + post $post) — phần dư bị cắt"
  inputs+=(-i "$f")
  fc+="[$k:v]fps=30,trim=duration=$dur,setpts=PTS-STARTPTS+$off/TB,format=yuva444p[v$k];"
  fc+="[$last][v$k]overlay=eof_action=pass:format=auto[o$k];"
  last="o$k"
done
fc+="[$last]trim=duration=$TOTAL,format=yuv420p[out]"
ffmpeg -v error -y "${inputs[@]}" -filter_complex "$fc" -map "[out]" -r 30 -c:v libx264 -crf 18 preview/remake.mp4
ffmpeg -v error -y -i source.mp4 -i preview/remake.mp4 -filter_complex \
  "[0:v]fps=30,scale=540:960[a];[1:v]scale=540:960[b];[a][b]hstack" -an -c:v libx264 -crf 22 preview/compare.mp4
: > preview/ssim.txt
for k in $(seq 1 17); do
  a=${S[$((k-1))]}; d=$(awk "BEGIN{printf \"%.3f\", ${S[$k]}-$a}")
  v=$(ffmpeg -v info -ss "$a" -t "$d" -i source.mp4 -ss "$a" -t "$d" -i preview/remake.mp4 -filter_complex \
    "[0:v]fps=30,scale=270:480,format=gray[x];[1:v]scale=270:480,format=gray[y];[x][y]ssim" -f null - 2>&1 \
    | grep -o 'All:[0-9.]*' | cut -d: -f2)
  printf "s%02d %s\n" "$k" "$v" >> preview/ssim.txt
done
# ảnh điểm nối: 3 cặp (gốc trái | remake phải) tại cut-0.1 / cut / cut+0.1 cho 16 điểm nối
mkdir -p preview/joins
for j in $(seq 1 16); do
  t=${S[$j]}
  # đúng 1 khung mỗi mốc: số khung = round((cut+dt)*30)
  sel=$(for dt in -0.1 0 0.1; do printf "+eq(n\\\\,%d)" "$(awk "BEGIN{printf \"%d\", ($t+$dt)*30+0.5}")"; done); sel=${sel#+}
  ffmpeg -v error -y -i preview/compare.mp4 -vf "select='$sel',scale=540:-1,tile=3x1" -frames:v 1 "preview/joins/J$(printf %02d $j).jpg"
done
echo "remake: $(ffprobe -v error -show_entries format=duration -of csv=p=0 preview/remake.mp4)s"; cat preview/ssim.txt | tr '\n' ' '; echo
