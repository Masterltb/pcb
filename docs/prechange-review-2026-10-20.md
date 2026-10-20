# Đánh giá trước sửa PCB - 2026-10-20

Trạng thái: KHÔNG DUYỆT SẢN XUẤT. Đây là hai góc nhìn review của cùng trợ lý, không phải chứng nhận độc lập hay kết quả thử nghiệm phần cứng.

## Phạm vi đã được người dùng xác nhận

- Hai XL4015 gá riêng trong hộp điện, nối mainboard bằng đầu nối cắm rời; không song song hai đầu ra. Mỗi bộ cấp một cột.
- Giữ GPIO theo PROJECT.md; DevKit tháo được, mainboard THT, hai lớp, tối đa 100 x 100 mm.
- Cáp dưới 1 m; khoảng bốn tô 300 g/cột; hộp điện ở ngoài khoang tô; chưa xác định điều kiện lạnh/ngưng tụ.
- Cho phép dùng bản vẽ sản phẩm làm căn cứ footprint; không còn bắt buộc chờ mẫu trước khi chuẩn bị thiết kế. Nghiệm thu hàng mua và thử lắp trước sản xuất vẫn cần.

## JaeBin - review điện trước sửa

Không duyệt bản hiện tại: DRC chạy lại có 737 vi phạm và 14 mục chưa nối; có short +5V/GND, +5V/+3V3. ERC 0 không xác minh độ đúng chức năng.

Các thay đổi được yêu cầu trước khi review lại:

1. Thay một buck chung bằng hai giao tiếp buck riêng: 12V/GND ra module, 6V/GND về board, PTC riêng mỗi rail. Không nối hai đầu ra 6V trước PTC.
2. Khôi phục DevKit 38 chân cắm socket; bỏ MCU SMD và LDO SMD trên carrier. GPIO16/17 yêu cầu phiên bản WROOM, không chọn WROVER.
3. Có cách ngắt cấp 5V carrier vào DevKit khi nạp USB; tài liệu hãng không cho cấp đồng thời các nguồn. Phải ghi thao tác bảo trì và kiểm tra backfeed.
4. Tính lại MOSFET chống ngược cực, clamp VGS, TVS và fuse phối hợp với nguồn tổ ong. TVS không bảo vệ quá áp duy trì hoặc bảo đảm rail servo không có overshoot.
5. Giữ 330R + 10k mỗi PWM, bulk 2200uF + 100nF mỗi rail. Dòng stall ~2.5A/con là giả thiết cần đo; tải cơ 1.2kg không xác định dòng điện.
6. Chốt receiver TSOP38238 và emitter TSAL6200; không coi VS1838B hoặc transistor khác pinout là thay thế tự động. IR dùng burst; thử tô trong suốt, crosstalk, mất dây.
7. Đo tải động, nhiệt, mất điện/reset, ESD cáp ngoài và hành vi cơ cấu trước vận hành. Không tuyên bố đạt IEC ESD hoặc EMC từ DRC.

## Jbungia - review DFM/DFA trước sửa

Không duyệt bản hiện tại: 12 lỗ U2 0.20mm dưới quy tắc khoan; 47 courtyard overlap; lỗ J12/via giao nhau; mask bridge; module SMD trái yêu cầu THT.

Các thay đổi được yêu cầu trước khi review lại:

1. Bỏ footprint đoán kích thước XL4015; dùng đầu nối có MPN và bản vẽ hãng. Module ngoài phải có gá chống rung, cách điện mặt dưới và đầu nối trên cả module, không hàn dây trực tiếp.
2. DevKitC V4: pitch chân 2.54mm, khoảng cách hàng 25.40mm theo bản vẽ hãng. 48.26mm là phần thân PCB; anten nhô thêm 6.04mm. Không nhầm tổng chiều dài với phần thân. USB và anten cần khoảng trống.
3. Chọn cặp terminal header/plug cùng hệ; kiểm tra lỗ hoàn thiện theo bản vẽ, không thay terminal cố định cho loại cắm rời.
4. Mọi linh kiện phải có vùng thân và chỗ dụng cụ hàn/tháo; test point THT thực; lỗ M3 chừa đầu vít/vòng đệm.
5. Kiểm tra routing nguồn cả đường đi và đường về, pad neck và thermal spokes; không suy ra dòng chịu đựng chỉ từ độ rộng trace.
6. Xuất từ đúng revision sau DRC và review rủi ro được người dùng duyệt. Không sử dụng gói handover cũ như hồ sơ đã nghiệm thu.

## Sản phẩm và căn cứ đã tra

| Khối | Sản phẩm / link mua | Căn cứ / giới hạn |
|---|---|---|
| Buck servo, x2 | [Hshop HS0742V XL4015](https://hshop.vn/mach-giamop-dc-xl4015-cu-hien-thi-5a-1) | Trang bán ghi 54 x 23 x 18mm, tối đa 5A, có heatsink. Đây không phải chứng minh 5A liên tục trong hộp. Gá ngoài, chưa vẽ tọa độ chân/lỗ module. Cần xác nhận module có terminal; nếu chỉ pad thì không đạt yêu cầu dây ngoài. |
| MCU | [Espressif ESP32-DevKitC-32E tại Mouser](https://www.mouser.com/en/ProductDetail/Espressif-Systems/ESP32-DevKitC-32E) | [Bản vẽ V4](https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf), [pinout và nguồn](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html). Mua đúng revision/pinout, không clone tùy ý. |
| Logic 5V, ứng viên có bản vẽ | [Pololu D24V25F5 #2850](https://www.pololu.com/product/2850) | [Bản vẽ](https://www.pololu.com/file/0J1414/d24v25fx-step-down-voltage-regulator.pdf). 17.8mm vuông, pitch2.54mm, có dung sai lỗ và STEP. Chi phí cao, chưa chốt là BOM sản xuất. |
| Logic 5V, ứng viên tiết kiệm | [RECOM R-78E5.0-1.0](https://backoffice.recom-power.com/en/products/switching-regulators/switching-regulators-sip/rec-p-R-78E5.0-1.0.html) | Module THT SIP3, cần đối chiếu datasheet đúng 1A trước chốt footprint; không dùng footprint bản 0.5A nếu kích thước khác. |
| Terminal buck | [Phoenix MSTBA 2,5/4-G-5,08 1757268](https://www.phoenixcontact.com/en-us/products/pcb-header-mstba-25-4-g-508-1757268) | Hãng ghi pitch5.08, lỗ1.4mm, pin1x1mm, plug tương thích1757035. Cần coding/nhãn tránh đổi nhầm harness. |

## Điều kiện đóng review

ERC/DRC sạch với thiết lập hợp lệ; netlist xuất thật từ schematic khớp PCB; BOM MPN và phương án thay thế có phân loại tương thích; bản vẽ lắp và harness; kết quả thử nghiệm thực. Các TODO về thời gian cơ cấu, nhiệt/môi trường và hộp không được đổi thành PASS khi chưa có dữ liệu.

Các skill fv-pcb-* được nhắc trong AGENTS.md không có trong checkout và thư mục skill đã tìm. Chưa thực hiện quy trình skill thiết kế bắt buộc; không đánh dấu hoàn tất review/release theo skill.

## Bổ sung trước lần sửa RX RevA2

Người dùng đã cho phép thay quy trình skill thiếu bằng thao tác KiCad trực tiếp, giữ review và ERC/DRC. JaeBin yêu cầu thêm kéo lên 10k ngoài cho GPIO34/35 (không có pull-up nội) và 1k nối tiếp mỗi OUT RX để hạn dòng; mức LOW ước tính khoảng 0.4V với receiver đang sink khoảng 0.3mA, cần đo xác nhận. Không coi 1k là chứng nhận ESD. Jbungia yêu cầu vẫn giữ THT, đặt thêm bốn điện trở với courtyard và nhãn rõ, kiểm tra DRC lại, không chồng lên vùng DevKit hoặc anten.
