# FV-CTRL RevB — hồ sơ review trước chế tạo mẫu

Ngày kiểm tra: 2026-10-25. Nguồn5V: RECOM R-78E5.0-1.0; nhánh `fix/revb-recom-logic-supply`. Commit thiết kế và SHA256 xem manifest ZIP hiện hành.

**Kết luận: bản KiCad đã đi dây và vượt qua kiểm tra phần mềm; chưa nghiệm thu production.** Hồ sơ này dùng để duyệt rủi ro và trao đổi DFM/báo giá. Gerber/drill mẫu đã xuất ngày 2026-10-26 theo yêu cầu trong chat, giữ nguyên thiết kế. Chưa đặt hàng và chưa gửi dữ liệu cho xưởng.

Cập nhật xuất mẫu: [hồ sơ và kết quả kiểm tra](RevB-prototype-export-2026-10-26.md). ERC/DRC/parity, verifier và hình học Gerber/drill đã kiểm lại; ZIP Gerber và gói handoff có ngày nằm trong `releases/revb/`. Việc xuất file không phải nghiệm thu RF/nhiệt/phần cứng hoặc duyệt DFM của xưởng.

## Cập nhật nguồn5V

J4 hiện là RECOM R-78E5.0-1.0, ba chân1VIN/2GND/3VOUT, THT trực tiếp;
không dùng Pololu/socket cũ. Thêm C57 10µF đầu12V và C58 100nF0402 đầu5V.
Giữ Phoenix, hai XL4015 và GPIO. Budget tính0,887A, chưa đo; mẫu phải thử
inrush/soft-start/hotplug/ripple/thermal, mục tiêu ambient0…50°C gầnmodule.
Xem `RevB-RECOM-prechange-review.md` và `reports/revb/verified/RevB-RECOM-check.json`.
Model3D J4 cùng envelope của họR-78E, không phải xác nhận mẫu nhận được.

## Kết quả trên file hiện tại

| Kiểm tra | Kết quả |
|---|---|
| ERC KiCad 10 | 0 lỗi/cảnh báo |
| DRC theo rule của project | 0 lỗi/cảnh báo |
| Kết nối hở | 0 |
| Đối chiếu schematic–PCB | 0 sai khác |
| Kiểm tra độc lập chân/net/kiến trúc | PASS |
| Lỗ via thông thường với mask/paste SMT | PASS, khoảng cách hình học tối thiểu 0,05 mm; EP review riêng |
| BOM và tọa độ SMT | Khớp63 reference SMT, tổng151 reference BOM |
| PCB | 100 × 100 mm, hai lớp, 1,6 mm danh định, chuẩn bị đồng 1 oz |

Giữ IC ESP32-D0WD-V3 rời, anten SMA, bảng GPIO và hai XL4015 servo 6 V độc lập gá ngoài. Không nối song song đầu ra buck. USB chỉ truyền dữ liệu; phải cấp nguồn chính khi nạp. Limit switch mặc định DNP.

## Hai góc đánh giá

**JaeBin — IC/SI/PI:** pin/net, strapping, reset supervisor, flash, mạng CAP1/CAP2, cấp nguồn và RF đã được kiểm tra trên thiết kế. Các đường 12 V và 6 V có chiều rộng tối thiểu 2 mm, không dùng via trên các net này. Ground của C22, C40 và nhóm supervisor đã nối về phần còn lại của board. Điều kiện để nghiệm thu còn gồm RF/crystal, sụt áp và ripple khi Wi-Fi/servo hoạt động, nhiệt LDO, xung hồi trên rail 6 V, thử flash và chu trình máy thật.

**Jbungia — DFM/DFA:** fanout 0,40/0,20 mm, annular ring danh định 0,10 mm; chữ silk tối thiểu 1 mm, nét 0,15 mm, khoảng cách silk 0,15 mm. Mask expansion ứng viên 0,025 mm và web tối thiểu 0,10 mm. Không có via mở trong pad SMT thông thường. Hai IC có tổng 25 lỗ nhiệt EP cần xưởng duyệt fill/cap/stencil. Yêu cầu QFN pitch 0,35 mm và 0201 cần JLCPCB Standard PCBA theo năng lực đã tham chiếu. Chưa có DFM/yield thực tế hoặc xác nhận tồn kho.

Hai phần trên là hai góc review trong công việc thiết kế này, không phải chứng nhận độc lập của xưởng hoặc phòng thử nghiệm.

## Những điểm cần duyệt trước Gerber

1. **Nguồn và tải:** giữ hai buck 6 V riêng; thử dòng khởi động/giữ/kẹt, PTC, cầu chì, connector, sụt áp dây dưới 1 m và xung hồi 6 V. TVS đầu vào 12 V không bảo vệ trực tiếp đầu ra 6 V. Nhiệt LD1117 cần đo trong hộp điện.
2. **RF và crystal:** matching 1,5 pF / 2,7 nH / 0,5 pF, tụ tải crystal 16 pF và đường RF rộng 1,1 mm là điểm bắt đầu đo chỉnh. PCB hai lớp chuẩn bị theo JLCPCB chưa có bảo đảm controlled impedance 50 Ω. Cần chốt stackup, anten/dây/vỏ và phương án đo; không tự coi DRC sạch là RF đạt.
3. **Lắp ráp QFN:** xưởng xác nhận pad EP, 25 lỗ trong `FV-CTRL_RevB-EP-vias.csv`, fill/cap, tenting và cửa sổ stencil. Chỉ xử lý fill/cap các lỗ EP được liệt kê, không fill lỗ chân THT. Stencil 0,10 mm là ứng viên để xưởng duyệt.
4. **Linh kiện:** BOM có MPN và thông tin thay thế có điều kiện; chưa xác nhận giá, tồn kho, MOQ hoặc chấp thuận mọi phương án thay thế. Crystal đã chọn có dải -10…60 °C; cần xác nhận phù hợp nhiệt độ hộp thực tế. Không thay ESP32 bằng module hoặc biến thể chiếm GPIO16/17.
5. **Cơ khí và bảo trì:** kiểm tra kích thước thật đầu nối, fuse holder, buck logic, SMA và khoảng trống USB/BOOT/RESET khi lắp vào hộp; kiểm tra cực dây trước cấp nguồn. Một số nhãn RX/TX, chân nguồn và limit DNP nằm mặt dưới: xem cả hai bản vẽ lắp ráp.

Mục 9 của `AGENTS.md` yêu cầu duyệt rủi ro trước khi xuất Gerber. Đồng ý xuất Gerber cho mẫu không đồng nghĩa nghiệm thu sản xuất hàng loạt. Sau đó nên làm khoảng 5 mẫu, chạy checklist bring-up và lưu kết quả trước khi chốt sản xuất.

## Cách mở và đọc hồ sơ

- Giải nén nguyên cấu trúc; mở `hardware/revb/FV-CTRL_RevB.kicad_pro` bằng KiCad 10. Mở schematic từ file gốc để giữ quan hệ 9 trang chức năng và trang chỉ mục.
- `libs/` là thư viện cục bộ; không di chuyển tách khỏi `hardware/`. Cần thư viện chuẩn KiCad 10 để sửa/gán footprint.
- `RevB-front-assembly.svg` và `RevB-back-assembly.svg` là bản vẽ vector, phóng to để đọc. Mặt dưới đã được mirror để nhìn trực tiếp từ mặt dưới.
- `FV-CTRL_RevB-SMT-position-review.csv` dùng mm, gốc phụ tại góc trái dưới PCB (tọa độ thiết kế 100,200 mm), Y dương hướng lên. Góc quay là quy ước KiCad; xưởng phải kiểm tra pin 1/rotation trên preview lắp ráp trước khi duyệt CPL.
- Bản đồ EP dùng tọa độ thiết kế tuyệt đối và ghi rõ trong tiêu đề CSV; không nhầm với gốc phụ của file SMT.
- Ảnh 3D chỉ minh họa: bộ thư viện cài đặt hiện thiếu model STEP đúng của ESP32 QFN 5 × 5 mm và một số đầu nối. Vị trí U1 hiện có thể nhìn thấy pad thay vì thân chip. Không dùng ảnh này để duyệt chiều cao/cơ khí; dùng footprint, datasheet và mẫu thật.
- Chưa kiểm chứng import RevB trong EasyEDA. File KiCad và báo cáo KiCad là nguồn kiểm tra của bản này.

Chi tiết phép thử: `RevB-review-and-bringup.md`. Báo cáo gốc: `reports/revb/verified/RevB-final-erc.rpt`, `reports/revb/verified/RevB-final-drc.rpt` và `reports/revb/verified/RevB-functional-gate.json`.
