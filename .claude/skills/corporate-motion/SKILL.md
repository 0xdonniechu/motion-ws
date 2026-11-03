---
name: corporate-motion
description: Làm một clip motion graphic dọc 9:16 theo preset corporate-motion từ nội dung dán vào hoặc một chủ đề. Chỉ viết script.json (chữ + tên trong catalog); máy sinh, render và kiểm.
argument-hint: "[--theme tên] <nội dung dán vào hoặc chủ đề>"
disable-model-invocation: true
---

# /corporate-motion [--theme tên] <nội dung hoặc chủ đề>

Bạn chỉ viết NỘI DUNG và chọn TÊN trong catalog; `make.sh` làm mọi thứ còn lại (toạ độ, chuyển động, màu, render, kiểm). Đọc ĐÚNG hai thứ này và không gì khác (không grep/đọc catalog.json, kit.js, kit.css, preset.md, style.json, script.json của job khác; `--brief` đã có đủ ý nghĩa, đơn vị, khoảng giá trị, prop bắt buộc và ví dụ từng prop):
1. `node presets/corporate-motion/tools/build-clip.mjs --brief` (catalog.json + layouts.json + khung beat, rút gọn)
2. `presets/corporate-motion/script.schema.json` (dạng script.json, có ví dụ hai beat)

## Làm
1. Job: `jobs/<YYYYMMDD hôm nay>-corp-<slug-ascii-ngắn>/` (thư mục MỚI: nếu đã có, thêm -2, -3...). `--theme` nếu có thì chuyển nguyên cho make.sh.
2. Viết `<job>/script.json`:
   - tiếng Việt đủ dấu; chữ trên màn hình NGẮN (mỗi chuỗi <= 70 ký tự, thường <= 40); `*từ*` là từ nhấn, `~từ~` là từ nhấn nghiêng có chân (dùng ít, tối đa một cụm mỗi câu);
   - kịch bản NGUYÊN BẢN theo chủ đề, một sợi chỉ đếm được; theo khung beat: đúng thứ tự (đảo thứ tự là LỖI), được bỏ beat không hợp (chỉ cảnh báo), BẮT BUỘC kết ở `cta` (không thì lỗi);
   - số liệu bịa là số minh hoạ: ghi nhãn "Số minh hoạ" (prop `tag` của statCard) khi có;
   - không logo hãng thật, không ảnh chụp màn hình thật, không trích dẫn có tên người (quoteCard là câu chốt phổ quát, không tác giả);
   - chỉ dùng component/effect/transition trong `--brief` và prop công khai; không x/y/w/h/ease/reach/dur; mỗi slot một item; effect `at` là giây từ đầu beat (thẻ vào ~0.1s, số đếm/gõ chữ sau đó ~0.7s, chữ phụ sau ~1–2s, tăng dần); bỏ trống `duration` để máy tự tính.
3. Chạy: `bash presets/corporate-motion/tools/make.sh <job>/script.json [--theme tên]`. Lỗi script (thoát 1): sửa script.json đúng theo danh sách lỗi, chạy lại, tối đa 2 lần rồi báo.
4. Báo lại: đường dẫn mp4, báo cáo make.sh (check, seek-test, so DNA), và chỗ lệch nếu có. Không tự kể là đạt khi có dòng FAIL hoặc "not run".

## Dừng, không vẽ tạm
Nếu `make.sh` hoặc `build-clip.mjs` báo `thiếu mục X trong catalog` (thoát 2), hoặc ý cần một thứ không có trong `--brief`: DỪNG, báo tên mục và beat cần nó. Không thêm vào kit, không vẽ riêng trong scene, không đổi nội dung để lách. Thêm mục là việc của chủ (catalog.json + kit.js + demo/ trước).
