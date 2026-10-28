# Rev-S3 — review trước khi đổi lỗ tối thiểu sang 0,30 mm

Mục tiêu: cho phép chọn cấu hình khoan 0,30 mm thông thường của JLCPCB cho 5 PCB mẫu. Giữ ZIP Gerber 0,20/0,25 mm ở commit `e1b9153` làm bản sao lưu; chỉ thay đổi file PCB Rev-S3 và xuất ZIP mới với tên riêng.

## IC/SI/PI

- Tăng 62 via tín hiệu/nguồn từ lỗ 0,25 mm lên 0,30 mm, giữ đường kính đồng 0,50 mm. Vành đồng danh định còn 0,10 mm mỗi phía, cần DRC kiểm tra clearance và annular ring; việc tăng lỗ không cải thiện dòng tải của đường nguồn/đường hồi.
- Tăng 12 lỗ xuyên trong pad tản nhiệt U1 từ 0,20 mm lên 0,30 mm, giữ pad đồng 0,60 mm; vành đồng danh định còn 0,15 mm. Lỗ lớn hơn có thể tăng nguy cơ hút thiếc khi reflow; vẫn cần JLCPCB xác nhận epoxy-fill/cap chính xác 12 lỗ này.
- Không đổi net, chiều rộng track, vị trí linh kiện, nguồn, GPIO, RF/USB hoặc đường anten. ERC/DRC/parity phải được kiểm tra lại trên file sau sửa.

## DFM/DFA

- JLCPCB nêu kích thước via tối thiểu 0,30/0,40–0,45 mm là lựa chọn thông thường trên biểu mẫu, nhưng Gerber cũ có lỗ nhỏ hơn. Chỉ được chọn mức này khi **mọi lỗ xuyên của PCB mới tối thiểu 0,30 mm**; kiểm tra file drill sau xuất.
- 12 lỗ U1 nằm trong pad SMT, không phải via rời. Cấu hình “Via Covering” có thể không tự xử lý đúng các lỗ này. Phải ghi chú riêng cho JLCPCB, chọn xác nhận production file và không thanh toán trước khi DFM xác nhận lỗ U1 được fill/cap mà các lỗ THT khác vẫn mở.
- Kết quả trên file không chứng minh chất lượng mối hàn U1 hoặc nhiệt/điện dưới tải. Kiểm tra điện và cơ sau khi nhận mẫu.

## Kết quả triển khai trên file

- Tăng đúng 62 via 0,25 → 0,30 mm và 12 lỗ pad U1 0,20 → 0,30 mm. Giữ 2 via nguồn 0,50 mm và mọi lỗ THT còn lại. Drill PTH xuất ra chỉ còn kích thước tối thiểu 0,30 mm.
- Dời cục bộ ba via `+6V_B`, `+12V`, `I2C_SDA` và chia lại một đoạn B.Cu `+6V_B` để giữ khoảng cách lỗ–track; refill zone. Không đổi các linh kiện, GPIO hoặc nhánh nguồn khác.
- Lưu footprint U1 đã chỉnh vào `libs/fv_rev_s3.pretty/ESP32-S3-WROOM-1U_0p3.kicad_mod`; đồng bộ thư viện project, schematic và PCB để DRC không báo mismatch.
- `reports/rev_s3/work/RevS3-min-drill-0p3-final-erc.rpt`: ERC 0 violation. `reports/rev_s3/work/RevS3-min-drill-0p3-final-drc.json`: DRC 0 violation, 0 unconnected, còn 4 cảnh báo parity J21 VBUS như bản trước.
- ZIP Gerber/drill có 11 file fabrication tại `releases/rev_s3/prototype-0p3-2026-10-29/`; các file 0,20/0,25 mm cũ vẫn giữ làm backup. Chưa tải lên JLCPCB hoặc đặt hàng.
