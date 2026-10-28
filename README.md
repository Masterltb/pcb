# FreshVend — PCB điều khiển máy bán tô trái cây

**Rev-S3 là bản mẫu đang phát triển trên nhánh `fix/revs3-min-drill-0p3`.** Dùng ESP32-S3-WROOM-1U-N8, anten IPEX, USB-C dữ liệu và hai buck servo 6 V gá ngoài. RevB ở dưới là bản lịch sử; chưa bản nào được nghiệm thu sản xuất hàng loạt.

## Bàn giao Rev-S3

- [Bắt đầu tại đây: trạng thái, sơ đồ thư mục, bản hiện hành và backup](docs/rev_s3/handoff/README.md)
- [Project KiCad 10 Rev-S3](hardware/rev_s3/FV-CTRL_RevS3.kicad_pro)
- [Gerber 0,30 mm hiện hành cho 5 mẫu](releases/rev_s3/prototype-0p3-2026-10-29/FV-CTRL_RevS3-prototype-0p3-2026-10-29-Gerber.zip)
- [BOM nháp để kiểm tra linh kiện JLCPCB](assembly/rev_s3/draft/RevS3-JLCPCB-BOM-MATCHING-DRAFT.csv) và [CPL nháp](assembly/rev_s3/draft/RevS3-JLCPCB-CPL-MATCHING-DRAFT.csv)
- [ERC/DRC/parity hiện hành](reports/rev_s3/verified/RevS3-final-drc.json) và [rủi ro đặt hàng](docs/rev_s3/RevS3-JLCPCB-order-readiness-2026-10-29.md)

Các vị trí J4, J11/J12, J21 đang thiếu hàng ở báo giá JLCPCB; F2/F3 chưa có mã linh kiện. Gói Gerber dùng để kiểm tra/đặt mẫu PCB, chưa phải chứng nhận PCBA hoàn chỉnh.

## Bản RevB lưu để tham khảo

- [Project KiCad 10 RevB](hardware/revb/FV-CTRL_RevB.kicad_pro)
- [Trạng thái, kết quả kiểm tra và rủi ro cần duyệt](docs/revb/RevB-status.md)
- [ZIP review giữ nguyên thư mục](releases/revb/FV-CTRL_RevB-review.zip)
- [Gerber + drill mẫu RevB, 2026-10-26](releases/revb/FV-CTRL_RevB-Gerber-2026-10-26.zip)
- [Gói gửi xưởng báo giá/mẫu: Gerber, BOM, CPL và DFM](releases/revb/FV-CTRL_RevB-Prototype-Handoff-2026-10-26.zip)
- [Ghi chú lần xuất Gerber và giới hạn nghiệm thu](docs/revb/RevB-prototype-export-2026-10-26.md)
- [BOM linh kiện](docs/revb/bom/FV-CTRL_RevB-bom-review.csv)
- [Checklist cấp nguồn và chạy mẫu](docs/revb/RevB-review-and-bringup.md)
- [Mô phỏng Wokwi: ESP32, servo, IR và server local](simulation/revb/README.md)

Đọc [PROJECT.md](PROJECT.md) về yêu cầu và [AGENTS.md](AGENTS.md) trước khi sửa thiết kế. Không dùng các bản RevA/RevA2 để thay cho RevB.

## Cấu trúc

```text
hardware/
  rev_s3/               Project Rev-S3 đang phát triển; schematic, PCB và bảng thư viện
  revb/                 Project RevB lịch sử: mainboard, schematic và bảng thư viện
  reva2/                Bản cũ tham khảo: mainboard và IR RX
  archive/reva/         Nguồn RevA lịch sử, gồm các sửa đổi cục bộ chưa commit
libs/                   Thư viện dùng chung, giữ nguyên tên thư viện
cad/                    Cơ khí và mô phỏng FreeCAD
simulation/revb/        Mô phỏng chức năng Wokwi; không phải firmware production

docs/
  rev_s3/handoff/       Điểm vào bàn giao, đặt hàng và bring-up bản mẫu
  rev_s3/               Review, PDF schematic, STEP, pinout Rev-S3
  revb/
    bom/                BOM tổng, BOM SMT báo giá, linh kiện THT
    assembly/           Hình lắp ráp, ảnh 3D minh họa, tọa độ SMT, bản đồ via EP
    schematic/          Schematic xuất SVG/PNG để đọc
    RevB-status.md      Bắt đầu review tại đây
  reva2/                Tài liệu bản cũ
  archive/reva/         Tài liệu RevA lịch sử
  references/           Datasheet và hình tham khảo
  project/              Yêu cầu chung và ghi chú thử nghiệm
  mechanical/           Báo cáo cơ khí

reports/
  rev_s3/verified/      ERC, DRC/parity và netlist hiện hành
  rev_s3/work/          Log/checkpoint thử nghiệm cục bộ; không đưa vào Git
  revb/verified/        ERC/DRC, netlist và kết quả kiểm tra hiện hành
  revb/history/         Báo cáo trung gian đã lưu trong Git
  revb/work/            File chạy tạm/autoroute cục bộ, không đưa vào Git
  reva2/                Báo cáo RevA2
  archive/reva/         Báo cáo RevA lịch sử
  local/                Dữ liệu phân tích cục bộ, không đưa vào Git

releases/
  rev_s3/               Gerber hiện hành và các ZIP backup có ngày
  revb/                 ZIP review, Gerber/handoff mẫu có ngày và manifest SHA256
  archive/              ZIP/Gerber/handover các bản cũ; không dùng đặt RevB

tools/                  Công cụ; xem tools/README.md trước khi chạy
tests/                 Các bài kiểm tra generator RevA lịch sử
```

Các thư mục `hardware/<revision>` phải giữ quan hệ với `libs/`; không kéo riêng file project sang nơi khác. Trước khi đặt Rev-S3, đọc [bàn giao Rev-S3](docs/rev_s3/handoff/README.md) để phân biệt gói hiện hành với backup. Chưa có nghiệm thu phần cứng hoặc chấp thuận DFM của xưởng.

Xem [quy ước sắp xếp và kiểm tra](docs/repository-layout.md) để biết cách thêm file đúng chỗ.
