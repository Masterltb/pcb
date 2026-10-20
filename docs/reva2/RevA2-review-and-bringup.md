# FV-CTRL RevA2 — hồ sơ duyệt kỹ thuật, 2026-10-20

## Trạng thái và phạm vi
Mainboard mới 100 x 100 mm, hai lớp, linh kiện carrier THT; module cắm rời có linh kiện SMD bên trong. Giữ nguyên GPIO và hai rail 6V độc lập, hai XL4015 gá ngoài hộp theo người dùng duyệt. Không dùng file RevA cũ để đặt mainboard này. Hai vai dưới đây là hai góc đánh giá của cùng trợ lý, không phải chứng nhận từ hai kỹ sư độc lập.

**Kết luận: ứng viên prototype RevA2 đã qua kiểm tra điện tử CAD; chưa đủ bằng chứng để phê duyệt sản xuất hàng loạt. Chưa xuất Gerber.** Các board RX RevA hiện hữu được giữ nguyên; báo cáo DRC cũ sạch nhưng không được coi là đã hoàn tất qualification cho cả bộ máy. Chọn TSOP38238 theo datasheet, không thay VS1838B tùy ý.

## JaeBin — IC, nguồn và tín hiệu
- Đã sửa theo đúng DevKitC-32E: hai hàng 19 chân, cách 25.4 mm, GPIO16/17 dùng bản WROOM. Pololu D24V25F5 có thứ tự EN, VIN, GND, GND, OUT; EN để hở theo ứng dụng module. Anten có vùng tránh đồng và vùng thân module tránh linh kiện.
- Có cầu chì thay được, PMOS IRF4905 chống ngược cực, zener giới hạn VGS, TVS đầu 12V, hai PTC MF-R300 và hai tụ 2200uF/16V. TVS 12V không bảo vệ được lỗi buck đưa quá áp liên tục lên servo 6V. Cầu chì/PTC phải được phối hợp với đặc tính nguồn thực tế.
- Bốn PWM có 330 ohm nối tiếp và 10k kéo xuống; GPIO34/35 có 10k kéo lên ngoài và 1k nối tiếp cáp RX. Điện trở nối tiếp không thay thế kiểm thử ESD/EMC.
- Nguồn/servo đi dây tối thiểu 2mm, không chuyển lớp bằng via trên các nhánh này; GND phủ hai mặt. Không suy ra khả năng mang dòng hoặc nhiệt độ chỉ từ bề rộng. Cần xác nhận độ dày đồng, dòng thực và nhiệt độ môi trường.
- IR dùng burst 38kHz; khởi đầu thử 1ms bật / 1ms nghỉ với TSOP38238, điều chỉnh theo datasheet và đo thực tế. Không phát sóng mang liên tục. Tô PET/PP trong suốt có thể không chắn được tia.
- Servo 360 không có phản hồi vị trí. Interlock firmware và cảm biến rơi không chứng minh cơ cấu đã đóng. Limit DNP để lại đường nâng cấp; phải thử mất điện/khởi động lại và kẹt cơ cấu trước vận hành.
- Ước tính IRF4905 tại 5A, RDS(on)=20mOhm: P=0.5W ở điều kiện datasheet; điện trở tăng khi nóng, đây không phải kết quả nhiệt. Tụ 2200uF cấp riêng xung 2.5A trong 1ms sẽ sụt khoảng 1.14V theo I*dt/C, nên tụ không thay thế buck/dây đủ dòng.

## Jbungia — chế tạo, lắp ráp, bảo trì
- Carrier THT, module và dây rút cắm, cầu chì thay riêng, LED từng rail và test point đo nguồn. Bố trí hai hàng socket theo bản vẽ thay vì suy kích thước từ ảnh.
- DRC hiện tại: 0 vi phạm, 0 chân chưa nối, 0 lỗi parity schematic/PCB. Kiểm tra độc lập XML và pad thực PASS, gồm GPIO, cực LED, pin transistor/module, hai rail tách biệt và bề rộng nguồn.
- Đây chưa phải cam kết yield của xưởng. Phải yêu cầu xưởng xác nhận finished-hole tolerance, annular ring, solder mask và copper weight. Kiểm tra chân socket Samtec với lỗ nominal 1.0mm trước phát hành; nếu hãng yêu cầu lỗ lớn hơn phải cập nhật footprint và chạy lại DRC.
- Kiểm tra lắp 1:1 socket DevKit, buck 5V, tụ 12.5mm, PTC và terminal; kiểm tra vặn vít terminal, thay cầu chì và rút USB khi đã đóng hộp. Ảnh 3D thiếu model tùy biến không chứng minh đủ khoảng hở thực.
- Nhãn chức năng có thể nằm mặt sau để tránh pad; dùng thêm harness label và sơ đồ lắp, không chỉ nhìn vị trí chữ. In bản lắp trước hàn. Limit switch và linh kiện lọc liên quan ghi DNP trong BOM.
- Cần jig đo rail, kiểm tra thông mạch harness, kiểm tra phân cực và ảnh lắp chuẩn cho từng máy. Không thay linh kiện theo tên gọi chung khi pinout khác.

## Sản phẩm đã chọn và điều kiện mua
- MCU: [ESP32-DevKitC-32E / Mouser](https://www.mouser.com/en/ProductDetail/Espressif-Systems/ESP32-DevKitC-32E), [bản vẽ Espressif](https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf). Không mua clone 30 chân hoặc bản WROVER thay trực tiếp.
- Buck logic: [Pololu D24V25F5 #2850](https://www.pololu.com/product/2850), [bản vẽ](https://www.pololu.com/file/0J1414/d24v25fx-step-down-voltage-regulator.pdf). Đã chọn trong BOM RevA2; không thay MP1584 bằng footprint này.
- Buck servo x2: [XL4015 có screw terminal, heatsink và standoff](https://www.op-tronic.com/shop/dc-converters-step-down-converters-315/xl4015-dc-dc-step-down-module-with-voltmeter-5a-75w-151). Đây là ứng viên mua mẫu, không phải module đã được xác nhận 5A liên tục. Trang bán ghi 5A tối đa nhưng mô tả 4A liên tục / 4.5A ngắn hạn; phải thử với tải thực. Chưa chọn tọa độ gá hộp. Không chọn biến thể chỉ có pad hàn dây.
- BOM mainboard: `FV-CTRL_RevA2-bom.csv`, 80 reference, có nguồn và phương án thay thế. Các dòng candidate chưa là drop-in được phê duyệt. Phụ kiện ngoài BOM carrier: 2 XL4015, 1 DevKit, 4 servo, 2 RX, 2 LED TSAL6200, đầu cáp đối ứng, dây, hộp, nguồn và gá cách điện. Nguồn AC và nối đất phải do người có chuyên môn kiểm tra.

## Harness theo số chân, không theo màu dây
| Đầu nối main | Thứ tự chân |
|---|---|
| J1 | 1=12V vào, 2=GND |
| J2, J3 | 1=12V sau bảo vệ tới IN+ buck; 2=GND tới IN-; 3=OUT+ buck 6V về PCB; 4=GND OUT- |
| J5, J6 | 1=GND, 2=6V-A, 3=PWM cột 1 trên/dưới |
| J7, J8 | 1=GND, 2=6V-B, 3=PWM cột 2 trên/dưới |
| J9, J10 | 1=3.3V, 2=OUT receiver, 3=GND |
| J11, J12 | 1=anode LED IR, 2=cathode LED IR |
| JP1 | Ngắt nối 5V ngoài vào DevKit trước cắm USB |

Kiểm tra lại số pad trong KiCad trước làm cáp. Không nối hai OUT+ buck với nhau. Khuyến nghị khởi đầu dây servo/buck AWG18 mềm; tại 1m một chiều, vòng 2m đồng AWG18 khoảng 0.042 ohm, sụt khoảng 0.105V ở 2.5A, chưa tính tiếp xúc và PTC. Xác nhận dòng định mức đầu cắm servo và kích thước crimp; không ép dây lớn vào terminal không phù hợp. Cáp RX đi xa dây servo/buck, ghép OUT với GND và cố định chống kéo.

## Bring-up và tiêu chí nghiệm thu đề xuất
1. Chưa cấp nguồn: kiểm tra cực diode/tụ/Q1/Q2, ohm giữa mỗi rail với GND, không chập 6V-A/B. Đo thông mạch và cực từng harness khi cả hai đầu rời máy.
2. Rút DevKit, Pololu, servo và RX. Dùng nguồn bàn 12V giới hạn dòng để kiểm tra nhánh bảo vệ; thử ngược cực trên nguồn bàn hạn dòng, không dùng trực tiếp nguồn 40A.
3. Lắp Pololu, đo 5V; gắn từng XL4015, chỉnh bằng đồng hồ chính xác 6.00V khi chưa cắm servo. Đề xuất chấp nhận ban đầu 5V trong dung sai module, 6V tại tải 5.7–6.3V và không vượt giới hạn datasheet servo; đây là ngưỡng nghiệm thu cần xác nhận theo servo mua thực.
4. Cấp 12V với JP1 đóng, chỉ sau kiểm tra rail mới lắp DevKit và đo 3.3V. Khi nạp USB phải rút JP1 trước. Espressif yêu cầu các cách cấp nguồn loại trừ nhau; không cắm USB và 5V ngoài đồng thời.
5. Gắn RX, đo OUT HIGH/LOW và PWM TX bằng oscilloscope; kiểm tra nhiễu khi servo hoạt động, độ trễ phát hiện và đếm tô. Thử tô trong suốt ở các vị trí, ánh sáng và mức đầy thực tế.
6. Thử một servo rồi từng cột; chỉ một servo chạy mỗi cột. Ghi dòng cả servo đang chạy và servo giữ tải. Dùng tải điện tử để thử tải nặng an toàn, không cố giữ servo kẹt kéo dài.
7. Đo nhiệt trong hộp đóng ít nhất tới ổn định, ghi môi trường, dòng, điện áp đầu servo, nhiệt buck/Q1/PTC/terminal/tụ. Đạt khi từng linh kiện còn trong giới hạn hãng với margin được duyệt, không reset, không PTC trip nhầm và không có dấu hiệu nóng ở tiếp xúc. MF-R300 derating theo nhiệt; 3A hold không giữ nguyên khi hộp nóng.
8. Thử tải 4 tô x300g mỗi cột, tối thiểu 100 chu trình/cột cho prototype và ghi lỗi; 100 chu trình là screening ban đầu, chưa là chứng minh độ tin cậy sản xuất. Thử hết tô, tia bị che, mất RX, kẹt, reset, mất điện giữa từng bước; không được thả cả chồng tô.
9. Ghi kết quả theo số serial vào `rev-notes.md`; chỉ đóng từng mục khi có số đo/ảnh/log. Chưa có mẫu thật nên hiện toàn bộ phép thử vật lý là NOT RUN.

## Rủi ro phải duyệt trước Gerber
Đường nguồn 2mm cần đối chiếu copper weight và nhiệt; tụ bulk có thể chưa đủ cho xung thực; buck ngoài cần vị trí thoáng, dây ngắn và cách vùng anten/ESP32; USB phải tiếp cận được khi gá hộp và có quy trình JP1; lỗ socket cần đối chiếu dung sai; RX và tô trong suốt chưa kiểm chứng; servo 360 chưa chứng minh trạng thái cơ khí; môi trường nước/ngưng tụ và hộp chưa chốt. Không có phép thử ESD/EMC hay quá áp buck 6V. Các rủi ro này không được xóa bằng kết quả ERC/DRC.

AGENTS.md mục 9 yêu cầu liệt kê rủi ro để người dùng duyệt trước xuất Gerber. Hồ sơ này phục vụ duyệt prototype; chưa có phê duyệt Gerber hay sản xuất hàng loạt.

## Tái kiểm tra
Chạy `tools/build_rev_a2.py` bằng Python đi kèm KiCad 10, cần Java25 và Freerouting2.5 tại đường dẫn trong script; runtime tải về không nằm trong git. Script thay đổi file thiết kế và có thể làm thay đổi UUID; chỉ chạy khi chủ động rebuild. Để kiểm tra bản đã đóng băng, chạy ERC, xuất netlist XML, DRC với schematic parity, rồi `tools/verify_rev_a2.py --pcb`. Xem báo cáo `reports/RevA2-final-erc.rpt`, `RevA2-final-drc.rpt`, `RevA2-functional-gate.json`.
