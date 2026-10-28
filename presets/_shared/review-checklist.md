# Review checklist (chạy tay trên contact sheet, tick đủ mới duyệt render)

## Global (mọi rebuild)

- [ ] `hyperframes check` pass, 0 error.
- [ ] Frame đầu có nội dung (không trống = thumbnail chết).
- [ ] Không frame đen giữa chừng, không chữ tràn khung.
- [ ] Mốc chuyển cảnh rơi đúng beat (lệch < 0.3s).
- [ ] Sub bám voice, không để trống quá 1s (nếu có voice).

## Theo preset

- list-vertical: đủ N item, số thứ tự đúng, caption 4 dòng đầy đủ.
- kinetic-type: từ khóa giữ 1.5–3s, không khung trống.
- pipeline-diagram: mũi tên nối đúng hộp, không nhãn đè (kinh nghiệm vòng 2).
- exploded-view: nhãn không đè lớp, đủ số lớp, sub đúng lớp đang hiện.
- continuous-canvas: biên 2 vùng liền kề khớp (không hở/lệch), chữ zoom sâu đọc được, camera không dừng lưng chừng > 0.5s.
