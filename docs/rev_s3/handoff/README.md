# Bàn giao PCB FreshVend Rev-S3 — 2026-10-29

## Trạng thái

Rev-S3 dùng ESP32-S3-WROOM-1U-N8, anten IPEX, USB-C dữ liệu, nguồn chính 12 V, hai XL4015 gá ngoài tạo hai rail servo 6 V riêng. Board 100 × 100 mm, 2 lớp. Source hiện hành ở nhánh `fix/revs3-min-drill-0p3`; RevA/RevA2/RevB không thay đổi trong công việc này.

| Mức xác nhận | Kết quả |
|---|---|
| Đã implement | Lỗ tối thiểu 0,30 mm; sơ đồ và PCB đồng bộ hai cặp VBUS không sử dụng của USB-C; BOM/CPL nháp SMT+THT. |
| Đã kiểm tra trên file | ERC 0; DRC 0; 0 unconnected; 0 schematic parity issue. Gói Gerber 0,30 mm có 11 file fabrication. |
| Chưa kiểm tra trên phần cứng | Nạp USB, RF/Wi-Fi, sụt áp/nhiệt nguồn và dòng servo, hoạt động cảm biến, hành trình cơ khí. |
| Chưa được JLCPCB duyệt | Epoxy fill/cap đúng 12 lỗ dưới U1; J21 khớp footprint; danh sách linh kiện thiếu hàng và F2/F3. |

## Dùng đúng file

| Mục đích | File |
|---|---|
| Mở/sửa thiết kế | [Project KiCad 10](../../../hardware/rev_s3/FV-CTRL_RevS3.kicad_pro). Giữ cả thư mục `hardware/rev_s3/` cùng `libs/`. |
| Upload Gerber hiện hành | [ZIP Gerber 0,30 mm](../../../releases/rev_s3/prototype-0p3-2026-10-29/FV-CTRL_RevS3-prototype-0p3-2026-10-29-Gerber.zip). SHA-256 `91F55987D860309CA7DCE806E6B1584EC850970F528D6179789E509413190C19`. |
| Xem BOM match | [BOM JLCPCB nháp](../../../assembly/rev_s3/draft/RevS3-JLCPCB-BOM-MATCHING-DRAFT.csv), 30 nhóm/57 vị trí. |
| Xem vị trí lắp | [CPL JLCPCB nháp](../../../assembly/rev_s3/draft/RevS3-JLCPCB-CPL-MATCHING-DRAFT.csv), 57 vị trí. Tọa độ KiCad gốc phải được duyệt trong preview JLCPCB. |
| Đối chiếu từng linh kiện | [Engineering BOM nháp](../../../assembly/rev_s3/draft/RevS3-PCBA-BOM-DRAFT.csv), 39 SMT và 18 THT. |
| Đọc mạch | [PDF schematic hiện hành](../FV-CTRL_RevS3-Schematic.pdf), [pinout firmware](../FV-CTRL_RevS3-pins.h), [3D STEP tham khảo](../FV-CTRL_RevS3-3D.step). STEP thiếu model 3D U1/F2/F3; không dùng làm chứng cứ về khoảng hở các linh kiện này. |
| Kiểm tra file | [ERC](../../../reports/rev_s3/verified/RevS3-final-erc.rpt), [DRC/parity](../../../reports/rev_s3/verified/RevS3-final-drc.json), [netlist XML](../../../reports/rev_s3/verified/RevS3.net.xml). Netlist export có thông báo annotation warning dù ERC 0; đối chiếu pin/nets trên schematic nếu sửa tiếp. |

## Backup — không dùng cho đơn 0,30 mm

| Bản | File | SHA-256 / ghi chú |
|---|---|---|
| Trước review đường nguồn | [Snapshot đầy đủ](../../../backups/rev_s3_pre_power_review_2026-10-29.zip) | `36DBEB651D7F4C7E533F2F86E1BB0014A85768E222413EE6189FB7257F4A563E` |
| Gerber mẫu trước đổi lỗ | [ZIP Gerber 0,20/0,25 mm](../../../releases/rev_s3/prototype-2026-10-29/FV-CTRL_RevS3-prototype-2026-10-29-Gerber.zip) | `3660051F6D0FDA5299C6B26E66AF0AB633E37D2EB8D7596F096BA71DF0295948` |
| Release cũ hơn | `releases/rev_s3/FV-CTRL_RevS3-Gerber.zip` | Có trước các sửa đường nguồn; BOM/CPL cũ chỉ dành cho SMT. Không upload. |

## Hướng dẫn tiếp theo

1. Đọc [checklist đặt JLCPCB](JLCPCB-order.md) và [review rủi ro chi tiết](../RevS3-JLCPCB-order-readiness-2026-10-29.md).
2. Với mẫu lắp đủ linh kiện, giải quyết J4/J11/J12/J21 thiếu hàng, F2/F3 chưa match, cầu chì rời F1 và xác nhận DFM lỗ U1. Có thể chọn phương án để trống một số THT rồi hàn tại Việt Nam nếu danh sách lắp cuối ghi rõ; không vận hành thiếu bảo vệ.
3. Kiểm tra tất cả 57 vị trí, pin 1/cực tính, THT, tọa độ/rotation và production file của xưởng trước khi thanh toán.
4. Khi nhận mẫu, theo [checklist bring-up](bringup.md), ghi serial/firmware/tải/số đo vào [rev-notes](../../project/rev-notes.md).

Các review kỹ thuật nền: [nguồn và đường hồi](../RevS3-prechange-risk-review-2026-10-29.md), [đổi lỗ 0,30 mm](../RevS3-min-drill-0p3-prechange-review-2026-10-29.md), [USB VBUS](../RevS3-USB-VBUS-parity-review-2026-10-29.md), [phát hiện tô trong suốt](../RevS3-clear-bowl-drop-detection-review-2026-10-29.md).
