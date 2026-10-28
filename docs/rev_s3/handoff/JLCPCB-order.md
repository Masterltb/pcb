# Checklist đặt 5 PCB/PCBA Rev-S3 tại JLCPCB

## Upload và cấu hình PCB

1. Tải [ZIP Gerber 0,30 mm](../../../releases/rev_s3/prototype-0p3-2026-10-29/FV-CTRL_RevS3-prototype-0p3-2026-10-29-Gerber.zip). Không dùng hai ZIP backup trong [bảng phiên bản](README.md#backup--không-dùng-cho-đơn-030-mm).
2. Xác nhận FR-4, 2 lớp, 100 × 100 mm, 5 PCB, 1 thiết kế, 1,6 mm, đồng 1 oz. Chọn lỗ tối thiểu `0.3 mm/(0.4/0.45 mm)`, electrical test và `Confirm Production file = Yes`.
3. PCB có 12 lỗ 0,30 mm **trong pad tản nhiệt U1**. Yêu cầu JLCPCB xác nhận epoxy-fill/cap đúng 12 lỗ này, không lấp lỗ chân THT. Chỉ chọn option Via Covering không đủ để chứng minh họ đã nhận diện đúng lỗ; kiểm tra production file trước khi trả tiền.

## Cấu hình PCBA

- `Economic`, lắp mặt trên, 5 PCBA, tooling holes do JLCPCB thêm; bật xác nhận parts placement. Kiểm tra lỗ tooling mới không cắt đường hoặc cản gá M3.
- Tải [BOM](../../../assembly/rev_s3/draft/RevS3-JLCPCB-BOM-MATCHING-DRAFT.csv) và [CPL](../../../assembly/rev_s3/draft/RevS3-JLCPCB-CPL-MATCHING-DRAFT.csv) nháp riêng rẽ; giữ JLCPCB preview để so đủ 57 vị trí.
- Mục `Extended` và giá linh kiện không đồng nghĩa lỗi hoặc phí hàn tay. `Shortfall` là thiếu tồn kho ở quote; không tự chọn part chỉ vì cùng giá trị điện.

## Các dòng đang chặn đơn đầy đủ

| Vị trí | Cần cho 5 PCB | Tình trạng tại quote người dùng gửi | Hành động |
|---|---:|---|---|
| J4 — RECOM R-78E5.0-1.0/C3033024 | 5 | 5 shortfall | Pre-order/global source/consign đúng RECOM; không thay EVISUN cùng tên khi chưa duyệt pinout, điện, cơ. |
| J11/J12 — JST B4B-XH-A/C41422491 | 10 | 10 shortfall | Tìm nguồn đúng MPN/biến thể cơ khí. |
| J21 — GCT USB4105-GF-A/C3020560 | 5 | 5 shortfall; mô tả JLCPCB ghi 12P | Xác nhận part thực tế đúng bản vẽ GCT và footprint 16 pad. Là SMT, cần xưởng SMT nếu JLCPCB không lắp. |
| F2/F3 — Bourns MF-RHT300 | 10 | Unmatched, mã `TBD` | Tìm nguồn/consign đúng loại. BOM ghi `PTC 2.5A`, còn datasheet MF-RHT300 có Ihold 3 A tại 23 °C; duyệt theo dòng/tải thực trước khi thay. |
| F1 — đế cầu chì | 5 đế + 5 cầu chì rời | BOM mới có đế, chưa có công đoạn lắp cartridge | Chốt loại cầu chì 5 × 20 mm 5 A và hỏi JLCPCB có cắm cầu chì vào đế sau hàn không. |

Nếu chọn hàn F2/F3 tại Việt Nam, đánh dấu hai vị trí **không lắp tại JLCPCB**, mua đủ **10 PTC cho 5 PCB**, rồi nhờ xưởng hàn xuyên lỗ và kiểm tra mối hàn. J4 và J11/J12 cũng là THT, có thể xử lý tương tự nếu nguồn hàng phù hợp. J21 là SMT và cần tay nghề/thiết bị SMT. Không nối tắt F2/F3 hoặc vận hành rail servo khi chưa lắp bảo vệ.

## Trước khi thanh toán

- Đối chiếu tất cả linh kiện được chọn, MPN, footprint, pin 1/cực tính C1/C2/C57, D1–D7, chiều J1–J12/J21 và U1 trong preview.
- Xem danh sách vị trí không lắp; bất kỳ vị trí nào để trống phải được ghi rõ và có kế hoạch hàn sau.
- Nhận xác nhận JLCPCB về 12 lỗ U1, mối hàn module, lỗ tooling, J21 và khả năng lắp THT. Lưu quote/ảnh production file theo số đơn.
- Sau khi nhận mẫu mới đo nguồn/nhiệt/USB/RF và thử servo. ERC/DRC 0 không thay thế bước đó.
