# FreshVend — PCB điều khiển máy bán tô trái cây

**Thiết kế hiện hành: RevB, ESP32 QFN rời + anten SMA.** Hai buck servo 6 V độc lập được gá ngoài. Bản hiện tại đã qua kiểm tra phần mềm; chưa nghiệm thu sản xuất hàng loạt.

## Mở đúng file

- [Project KiCad 10 RevB](hardware/revb/FV-CTRL_RevB.kicad_pro)
- [Trạng thái, kết quả kiểm tra và rủi ro cần duyệt](docs/revb/RevB-status.md)
- [ZIP review giữ nguyên thư mục](releases/revb/FV-CTRL_RevB-review.zip)
- [BOM linh kiện](docs/revb/bom/FV-CTRL_RevB-bom-review.csv)
- [Checklist cấp nguồn và chạy mẫu](docs/revb/RevB-review-and-bringup.md)

Đọc [PROJECT.md](PROJECT.md) về yêu cầu và [AGENTS.md](AGENTS.md) trước khi sửa thiết kế. Không dùng các bản RevA/RevA2 để thay cho RevB.

## Cấu trúc

```text
hardware/
  revb/                 Project hiện hành: mainboard, 10 trang schematic, bảng thư viện
  reva2/                Bản cũ tham khảo: mainboard và IR RX
  archive/reva/         Nguồn RevA lịch sử, gồm các sửa đổi cục bộ chưa commit
libs/                   Thư viện dùng chung, giữ nguyên tên thư viện
cad/                    Cơ khí và mô phỏng FreeCAD

docs/
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
  revb/verified/        ERC/DRC, netlist và kết quả kiểm tra hiện hành
  revb/history/         Báo cáo trung gian đã lưu trong Git
  revb/work/            File chạy tạm/autoroute cục bộ, không đưa vào Git
  reva2/                Báo cáo RevA2
  archive/reva/         Báo cáo RevA lịch sử
  local/                Dữ liệu phân tích cục bộ, không đưa vào Git

releases/
  revb/                 ZIP review hiện hành và manifest SHA256
  archive/              ZIP/Gerber/handover các bản cũ; không dùng đặt RevB

tools/                  Công cụ; xem tools/README.md trước khi chạy
tests/                 Các bài kiểm tra generator RevA lịch sử
```

Các thư mục `hardware/<revision>` phải giữ quan hệ với `libs/`; không kéo riêng file project sang nơi khác. Gerber RevB chỉ được xuất sau khi người dùng duyệt rủi ro theo AGENTS.md. Bộ ZIP review không có Gerber/drill.

Xem [quy ước sắp xếp và kiểm tra](docs/repository-layout.md) để biết cách thêm file đúng chỗ.
