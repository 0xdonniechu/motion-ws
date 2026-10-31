# Teardown — "PonyTail trong Claude Code" (hand-drawn whiteboard, 95s, 16:9)

Nguồn: https://vt.tiktok.com/ZSgpQmenV/ — tải 2026-10-28 qua yt-dlp, 1024x576, 95.6s.
Voice: nam Việt, 25 segments (audio.json; Whisper VI lẫn thuật ngữ —
"club" = Claude, "hút" = hook, "phi" = file, "AnDorayCatParty" = tên bộ
luật — đọc hình mới chuẩn). Không chép asset gốc vào repo.

## 1. Shots

| # | Mốc | Loại shot | Bố cục (layers) | Chuyển động | Sub/caption |
|---|-----|-----------|-----------------|-------------|-------------|
| 1 | 0–10 | Hook vấn đề | Tay cầm bút + giấy CLAUDE.md + robot bối rối (?) + caption "Đã dặn trong CLAUDE.md mà Claude..." + số ①② | Tay vẽ nét theo lời, caption thay | "sẵn hàm gì để dùng lại?" |
| 2 | 10–24 | Vì sao file dặn đứng yên | Giấy 2 dòng (cách làm ✓ / dự án có gì ?) + stack ngày 1→2→3 phình to + "lười tìm thì viết mới" | Stack mọc thêm mỗi ngày, dấu ? đỏ | "file dặn vẫn đứng yên" |
| 3 | 24–39 | Giá của chép tay | Giấy luật (nghĩ trước/đơn giản/đúng chỗ/kiểm tra) + giấy "hàm có sẵn" + tay chép + "tốn công, cũ dần" + chặt↔lỏng phải sửa file | Tay chép lặp, 2 đầu mũi tên chặt/lỏng | "tự chép... tốn công và cũ dần" |
| 4 | 39–64 | Giải pháp: hook 1 | Sơ đồ HOOK (mở/mở lại/xóa/tóm tắt) → robot LUẬT + bản đồ dự án (utils/: formatDate... ~2000 ký tự) + caption "nạp luật + bản đồ mới nhất" | Sơ đồ vẽ dần, mũi tên vào robot, list hàm hiện | "tự chạy đúng thời điểm" |
| 5 | 64–83 | Hook 2+3 + luật sống | LUẬT → 2 SUBAGENT + live phân mức (opt/giữ hết phiên) + "Ponytail không thay CLAUDE.md" | Nhánh subagent tỏa, badge mức | "mỗi phiên agent có cả luật lẫn bản đồ mới nhất" |
| 6 | 83–95 | Hẹn series + CTA | Tay chỉ + caption "Tập sau mổ từng luật, tập cuối cách cài" + "Bạn có hay phải dặn đi dặn lại Claude Code không?" | Dừng vẽ, zoom nhẹ caption | CTA comment |

Khung cố định: watermark header ("Góc nhìn AI... 28/10/2026") + số thứ tự
tròn góc trái + caption đen đáy. Tay + bút là neo xuyên suốt.

## 2. Transition

Hard-cut theo beat voice, mỗi cut = giấy mới + số thứ tự tăng (①②③...).
Trong shot: nét vẽ chạy theo lời (draw-in), tay di chuyển khớp nét vẽ,
caption đen thay câu. Không camera move, không frame đen.

## 3. Spatial map

Không continuous-canvas. Sân khấu giấy kem tĩnh; mỗi scene là 1 tờ giấy
mới vẽ tiếp câu chuyện. Tay vẽ là "camera" dẫn mắt — mắt đi theo đầu bút.

## 4. Design system trích ra

- Nền giấy kem #f2ede3, nét đen 3px, chữ viết tay đen + nhấn đỏ/xanh lam.
- Tay cầm bút Sharpie + robot xám + giấy kẻ là 3 nhân vật cố định.
- Caption đen chữ trắng đáy = sub chuẩn, không sub rời.
- Công thức series tái dùng: pain (dặn mà không nghe) → vì sao (file tĩnh,
  code động) → giá (chép tay) → cơ chế mới (hook + bản đồ) → luật sống
  (subagent, phân mức) → hẹn tập sau + CTA.
- Số thứ tự tròn + watermark ngày = cảm giác series nhiều tập.
- Nhịp: 4–6s/caption, 1 ý = 1 tờ giấy, 95s/6 tờ.

## 5. Câu hỏi mở

- Tay vẽ là quay thật hay motion graphics (ComfyUI lineart + whiteboard
  render)? Cần thử cả 2, so với whiteboard-animate trên 5090.
- Watermark "Góc nhìn AI của MRQ..." là chữ ký kênh — remake dùng header
  của mình.
- Sơ đồ hook/subagent vẽ SVG draw-in được hết bằng HyperFrames, nhưng nét
  vẽ tay nguệch ngoạc cần stroke wobble — preset nào giả lập?
