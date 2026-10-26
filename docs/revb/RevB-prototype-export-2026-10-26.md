# FV-CTRL RevB — Gerber cho báo giá và chế tạo mẫu, 2026-10-26

Yêu cầu trong chat: xuất Gerber để gửi bên thứ ba báo giá và làm mẫu thử.
Đã xuất từ layout hiện hành, không sửa schematic, PCB, GPIO hoặc kiến trúc nguồn.
Đây là hồ sơ mẫu kỹ thuật có các điều kiện DFM bên dưới; chưa đặt hàng, gửi xưởng,
được xưởng duyệt hoặc nghiệm thu sản xuất hàng loạt.

## File bàn giao

- `FV-CTRL_RevB-Gerber-2026-10-26.zip`: 9 lớp Gerber X2 và 2 file khoan Excellon, ở gốc ZIP.
- `FV-CTRL_RevB-Prototype-Handoff-2026-10-26.zip`: ZIP Gerber trên, BOM, CPL,
  DNP, bản vẽ lắp, bản đồ EP, ảnh xem từ Gerber và báo cáo kiểm tra.
- `FV-CTRL_RevB-Prototype-2026-10-26-manifest.json`: SHA256 các gói và nguồn thiết kế.

ZIP Gerber gồm F/B copper, F/B soldermask, F/B silkscreen, Edge.Cuts, F/B paste,
PTH.drl và NPTH.drl. B.Paste trống là chủ ý: linh kiện SMT ở mặt trên.
Dùng ZIP Gerber để upload báo giá PCB; gửi thêm cả gói Handoff cho kỹ sư DFM/PCBA.
Không dùng Gerber RevA trong archive để chế tạo RevB.

## Thông số chế tạo và tọa độ

- PCB 2 lớp, đường bao tâm nét 100 x 100 mm; FR4 1,6 mm, đồng 1 oz.
- Không tự đổi thành 2 oz; fanout QFN đã được kiểm theo cấu hình 1 oz.
- Gerber X2, metric, absolute, định dạng tọa độ 4.6. Excellon metric, decimal,
  absolute, tách PTH/NPTH; hai slot dùng lệnh G85. Không mirror dữ liệu gửi xưởng.
- 375 vị trí khoan/slot mạ xuyên (bao gồm 2 slot) và 4 lỗ không mạ 3,2 mm.
- KiCad gbrjob tự ghi 100,05 mm do tính cả bề rộng nét outline 0,05 mm;
  file job chỉ lưu trong bằng chứng, không đưa vào ZIP upload. Kích thước chế tạo
  xác định theo tâm bốn đoạn Edge.Cuts, đã kiểm là 100 x 100 mm.
- CPL dùng mm, gốc phụ góc trái dưới (100,200 mm trong thiết kế), Y hướng lên,
  góc theo KiCad. Gerber/drill và bản đồ EP dùng tọa độ tuyệt đối. Xưởng cần
  đặt gốc phù hợp và kiểm pin 1/rotation trên preview lắp ráp, không cộng trực tiếp
  tọa độ CPL vào bản đồ EP.
- Số lượng, màu mask/silk, surface finish, phạm vi hàn THT, panel/tooling và
  phương pháp kiểm tra cần ghi trong báo giá; chưa có đơn đặt hàng được chốt.

## Review IC/SI/PI và DFM/DFA của layout giữ nguyên

Hai góc review nội bộ dựa trên hồ sơ RevB đã có, không phải chứng nhận độc lập.

1. Nguồn/tải: hai XL4015 gá ngoài cấp hai rail 6 V độc lập, GND chung; không
   nối song song đầu ra. Giữ cầu chì, chống ngược, TVS, PTC và tụ nguồn.
   Đường 12 V/6 V tối thiểu 2 mm đã qua verifier. Dòng khởi động/kẹt, đường hồi,
   vị trí tụ với dây thực, xung hồi 6 V và sụt áp đầu nối vẫn cần đo trên mẫu.
2. Nguồn logic: J4 là RECOM R-78E5.0-1.0 cố định 5 V/1 A, ba chân 1 VIN/2 GND/3 VOUT;
   C57 10 uF và C58 100 nF. Budget 0,887193 A là tính toán, chưa đo.
   Nhiệt LD1117, RECOM, ripple/inrush/soft-start/hotplug cần thử với Wi-Fi/IR và hộp thật.
3. RF/crystal: giữ matching, crystal và ground hiện tại. RF 50 ohm là mục tiêu,
   chưa có xác nhận trở kháng hai lớp hoặc đo tuning với anten/dây/vỏ thật.
4. QFN/SMT: ESP32 QFN pitch 0,35 mm, linh kiện RF 0201, via fanout 0,40/0,20 mm.
   Xưởng xác nhận khả năng lắp, soldermask/paste/stencil và 25 lỗ EP trong
   `assembly/FV-CTRL_RevB-EP-vias.csv`. Fill/cap hoặc quy trình thay thế phải được
   thống nhất cho đúng 25 lỗ EP; không fill lỗ THT hoặc mọi via 0,2 mm.
   Stencil 0,10 mm là ứng viên, cần xưởng duyệt; đề nghị báo giá kiểm tra QFN/X-ray.
5. Cơ khí/USB: kiểm khoảng trống đầu nối, SMA, tụ, RECOM, BOOT/RESET và cổng USB
   khi lắp hộp. USB chỉ truyền dữ liệu; phải cấp nguồn chính 12 V khi nạp.
6. BOM: 151 reference tổng, 63 reference SMT. MPN/mã LCSC có mục chưa xác nhận
   tồn kho/MOQ/giá hoặc phương án thay thế; phải đối chiếu với nhà lắp ráp.
   Limit switch và linh kiện liên quan mặc định DNP. Hai XL4015 là phần gá ngoài.

## Bằng chứng kiểm tra lần xuất

- KiCad CLI 10.0.7; header Gerber báo build 10.0.7-rc2.
- ERC: 0; DRC: 0; unconnected: 0; schematic parity: 0.
- Chạy severity-all/exit-code-violations; giữ nguyên các rule bị tắt sẵn trong
  project, không nới rule. JSON ERC/DRC đính kèm liệt kê ignored_checks.
- Verifier pin/net/PCB, nguồn RECOM và via/paste đều PASS; header GPIO khớp bảng cố định.
- Kiểm độc lập 9 file Gerber đọc được; outline kín, 2 lớp đồng, 100 x 100 mm.
- Đối chiếu từng vị trí, đường kính và chiều dài slot với KiCad: 375 PTH + 4 NPTH;
  sai số làm tròn xuất Excellon lớn nhất 0,0005 mm.
- Xem ảnh mặt trên/mặt dưới dựng từ chính Gerber bằng Gerbonara + resvg;
  kiểm đường bao, lỗ, lớp đồng, mask, silk, QFN và vùng USB. Không có runtime
  điều khiển GUI GerbView trong phiên; không ghi nhận đã xem bằng KiCad GerbView.
- Gerbonara 1.5.0 không đọc G85 trực tiếp: chỉ biểu diễn hai slot thành đoạn hình
  học khi dựng ảnh; không sửa file khoan gửi xưởng. Cảnh báo G90 sau header là
  cách xuất native của KiCad, được ghi lại trong báo cáo; tọa độ tuyệt đối đã kiểm.
- Kiểm checksum toàn bộ nguồn staged với checkout; không thay đổi thiết kế.
- Chưa có mẫu thật hoặc test chức năng trên máy. Không dùng firmware Wokwi làm
  firmware nghiệm thu. Nếu thuê xưởng test chức năng, cần chốt firmware, fixture,
  tải, ngưỡng đạt và phiếu kết quả riêng.

## Quy trình xuất đã dùng

Chạy trong bản sao giữ nguyên quan hệ hardware/libs dưới reports/revb/work/gerber-2026-10-26.
Không chạy generator/fanout/repair. Báo cáo cũ và gói review cũ được giữ làm mốc lịch sử.

```powershell
kicad-cli sch erc --format json --severity-all --exit-code-violations --output reports/revb/verified/RevB-export-erc.json hardware/revb/FV-CTRL_RevB.kicad_sch
kicad-cli pcb drc --format json --schematic-parity --severity-all --exit-code-violations --output reports/revb/verified/RevB-export-drc.json hardware/revb/FV-CTRL_RevB.kicad_pcb
kicad-cli sch export netlist --format kicadxml --output reports/revb/verified/RevB.net.xml hardware/revb/FV-CTRL_RevB.kicad_sch
# Sau đó chạy verify_rev_b.py --pcb, verify_rev_b_via_paste.py, verify_rev_b_supply.py bằng Python KiCad.
kicad-cli pcb export gerbers --output fabrication/ --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts,F.Paste,B.Paste --subtract-soldermask --disable-aperture-macros hardware/revb/FV-CTRL_RevB.kicad_pcb
kicad-cli pcb export drill --output fabrication/ --format excellon --drill-origin absolute --excellon-zeros-format decimal --excellon-oval-format alternate --excellon-units mm --excellon-separate-th --generate-map --map-format svg --generate-report --report-path reports/revb/verified/RevB-drill-report.txt hardware/revb/FV-CTRL_RevB.kicad_pcb
```
