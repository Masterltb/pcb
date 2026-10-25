# FV-CTRL RevB — hồ sơ kỹ thuật, chưa phát hành sản xuất

RevB dùng ESP32-D0WD-V3 QFN48 rời, flash W25Q32JV 4 MB, thạch anh 40 MHz và anten ngoài SMA. Không dùng DevKit hoặc ESP32-WROOM. RevA2 là thiết kế cũ, không phải bản thay thế tương đương.

## Hai góc review

**JaeBin — IC, nguồn, SI/RF.** Giữ nguyên GPIO và hai buck servo 6 V độc lập. Bổ sung LD1117V33, tụ nguồn từng miền, mạng CAP1/CAP2, điện trở strapping, supervisor TLV803EA30 và USB-UART CP2102N. GPIO12 kéo xuống để tránh chọn nguồn flash 1,8 V. CP2102N tự cấp từ 3,3 V; VBUS USB chỉ được cảm nhận qua chia áp 22,1 kΩ/47,5 kΩ. Phải cấp nguồn chính khi nạp, USB không cấp nguồn cho board.

Kiểm tra phần mềm về pin/net không chứng minh các đường nguồn đủ trở kháng thấp, độ chính xác thạch anh, nhiệt hoặc RF. Các tụ tải 16 pF và matching RF 1,5 pF / 2,7 nH / 0,5 pF (cộng điện dung ESD) là giá trị khởi đầu để đo chỉnh. Không tự thay matching bằng giá trị từ module khác. Không gắn đầu dò oscilloscope thông thường vào chân crystal rồi coi tần số đó là phép nghiệm thu.

**Jbungia — DFM, lắp ráp, bảo trì.** QFN pitch 0,35 mm và RF 0201 cần lắp SMT/reflow, chuẩn bị theo Standard PCBA. Đầu nối, cầu chì, PTC, tụ lớn và test point THT được lắp sau. Không coi bản này là thiết kế chỉ hàn bằng mỏ. Phải duyệt paste và xử lý via dưới exposed pad với xưởng; kiểm tra X-ray QFN nếu dịch vụ hỗ trợ, đồng thời xác nhận cách tính phí. Kiểm tra chiều pin 1, cực tụ/diode, hướng USB và connector bằng preview lắp ráp trước khi đặt.

## Điều kiện đặt PCB dự kiến

- Hai lớp, 100 × 100 mm, FR4 1,6 mm, đồng 1 oz. Không tự chọn 2 oz: khả năng line/space khác và chưa được rà lại cho QFN.
- Quy tắc hiện tại: clearance đồng 0,12 mm, chiều rộng tối thiểu tuyệt đối 0,10 mm cho thoát chân. Các nhánh 12 V/6 V giữ ít nhất 2 mm. Chiều rộng tối thiểu không phải chiều rộng dùng cho toàn bộ đường nguồn.
- Mặt dưới giữ ground dưới MCU/RF/crystal. Không được phá vùng này để router đạt đủ kết nối.
- JLCPCB công bố dịch vụ trở kháng có kiểm soát cho PCB từ bốn lớp; cấu hình hai lớp hiện tại **không có bảo đảm trở kháng 50 Ω của xưởng**. Bề rộng RF hiện tại chỉ là ứng viên; cần đo/tuning với stackup và anten/vỏ thật.
- Via EP, annular ring, soldermask, stencil, vị trí linh kiện và khả năng mua đúng MPN cần được xưởng kiểm tra. Không suy ra PASS từ ERC/DRC.
- BOM review liệt kê nguồn và phương án thay thế có điều kiện. Mã LCSC là ứng viên, chưa xác nhận tồn kho, MOQ, đơn giá hoặc thời gian giao. Chưa gửi đơn đặt hàng hay hồ sơ riêng tới xưởng.

Nguồn: [JLCPCB PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities), [Espressif layout](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html), [CP2102N](https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf).

## Trình tự cấp nguồn mẫu

1. Chưa nối servo. Soi kính và kiểm tra chạm chập các rail với GND khi chưa cấp điện; xác nhận cực connector và diode. Không dùng một giá trị điện trở duy nhất làm tiêu chuẩn PASS cho mọi rail có IC.
2. Chỉnh từng XL4015 ngoài board về 6,0 V bằng tải thử; không nối song song hai đầu ra. Xác nhận buck logic 5 V trước khi nối board. Dùng nguồn giới hạn dòng thích hợp, theo dõi dòng và nhiệt; không lấy nguồn 12 V/40 A làm giới hạn bảo vệ mẫu.
3. Đo tại test point theo thứ tự: 12 V → 6 V-A → 6 V-B → 5 V → 3,3 V. Đo trực tiếp cả hai phía connector để phát hiện sụt áp dây. Dừng khi sai áp hoặc dòng/nhiệt bất thường.
4. Đo EN khi nguồn lên/chập chờn; kiểm tra supervisor giữ reset, BOOT và strapping ở đúng mức khi nhả reset. Kiểm tra nguồn VDD_SDIO khoảng 3,3 V trước khi đọc/ghi flash. Giữ log reset/brownout.
5. Cấp nguồn chính rồi nối USB; kiểm tra cổng serial, nạp bằng BOOT/RESET thủ công, sau đó thử auto-download. Kiểm tra không cấp ngược từ USB khi tắt nguồn chính.
6. Chạy firmware test Wi-Fi và tải CPU, đo 3,3 V tại IC bằng ground spring ngắn, theo dõi ripple/sụt áp và nhiệt ổn áp trong hộp điện. Ngưỡng nghiệm thu phải dựa trên datasheet trong toàn dải hoạt động, không chỉ điện áp DC trung bình.
7. Đo RF/crystal với phương pháp và thiết bị phù hợp. Anten, dây SMA, vỏ hộp và matching đều phải giữ đúng cấu hình đã thử. Không tuyên bố RF/EMC đạt khi chỉ kết nối Wi-Fi được trên bàn.
8. Nối một servo rồi từng cột. Kiểm tra PWM khi boot/reset; xác nhận không tự quay ngoài ý muốn. Thử tải thật, khởi động đồng thời hai cột và tình huống kẹt có giới hạn thời gian; theo dõi áp, dòng, nhiệt PTC/connector/đường đồng và khả năng phục hồi. Không giữ servo kẹt kéo dài.
9. IR phát burst 38 kHz, không sóng mang liên tục. Thử có/không tô, ánh sáng môi trường, dây dưới 1 m và nhiễu khi servo hoạt động. Limit switch mặc định DNP; nếu lắp phải test debounce, đứt dây và trạng thái lỗi.
10. Chạy chu trình FIFO với bốn tô khoảng 300 g mỗi cột; kiểm tra cơ cấu giữ thân tô, tô méo/kẹt, mất điện giữa chu trình và cơ chế ngăn hai cửa cùng mở. Chưa có thử nghiệm này thì chưa nghiệm thu sản phẩm.

Ghi kết quả theo số serial mẫu, điện áp nguồn, tải, nhiệt độ và phiên bản firmware trong `docs/project/rev-notes.md`. Hiện chưa có dữ liệu đo trên mẫu thật.

## DFM của fanout QFN

Via thoát chân QFN là 0,40/0,20 mm, annular ring danh định 0,10 mm. `FV-CTRL_RevB-EP-vias.csv` liệt kê 25 lỗ nhiệt dưới U1/U2 theo tọa độ PCB; chỉ các lỗ EP này cần xưởng đánh giá fill/cap. Không fill lỗ chân linh kiện THT. Tenting mặt dưới chưa chứng minh yield của QFN; cần xưởng duyệt quy trình và kiểm tra mối hàn EP trên mẫu.

Giữ PCB hai lớp 1 oz; QFN pitch 0,35 mm và 0201 cần Standard PCBA theo năng lực đang tham chiếu. Stencil 0,10 mm là ứng viên để xưởng duyệt aperture 0201 và cửa sổ paste EP, chưa phải thông số đã nghiệm thu. Không đổi sang đồng 2 oz khi chưa kiểm tra lại rule.

Tab LD1117V33 nối 3,3 V. Tab linh kiện công suất phải đối chiếu pinout BOM trước khi gắn heatsink hoặc hộp kim loại; không mặc định tab là GND.

## Giới hạn cần đo trước nghiệm thu

TVS hiện tại bảo vệ đầu vào 12 V; nó không kẹp trực tiếp hai đầu ra servo 6 V. Cần đo xung trên từng rail khi servo giảm tốc, đảo chiều và khi cơ cấu bị kẹt. Không coi XL4015 là tải hấp thụ năng lượng tái sinh. Nếu xung vượt giới hạn servo hoặc buck, phải bổ sung giải pháp kẹp/hấp thụ được tính từ năng lượng đo thực tế và review lại trước sản xuất. Một diode flyback ngoài đầu cấp servo không thay thế được việc này vì motor và H-bridge nằm trong servo.

Hai PTC MF-R300 và cầu chì T5A là lựa chọn cần xác nhận bằng tải/nhiệt thực tế, gồm servo đang giữ tải trong khi servo còn lại chạy. Dòng hold của PTC giảm khi nhiệt độ tăng. Cáp dưới 1 m vẫn cần đo sụt áp ở đầu servo, kiểm tra đầu nối và tình huống hai cột hoạt động.

Bus flash có đường đổi lớp và chiều dài khác nhau; ERC/DRC chỉ xác nhận kết nối/khoảng cách. Kiểm tra khởi động, đọc/ghi flash ở cấu hình tần số sử dụng, dưới tải Wi-Fi và toàn dải nguồn/nhiệt. Điện trở nối tiếp 0 Ω là giá trị khởi đầu; chỉ đổi để chỉnh SI sau khi đo và đối chiếu hướng dẫn hãng.

## Điểm phải duyệt trước Gerber

Đường dòng lớn và sụt áp; vị trí tụ/đường hồi nguồn; nhiệt LD1117 và linh kiện công suất; khoảng cách và dây nối tới hai buck ngoài; truy cập USB/BOOT/RESET; ground reference và giới hạn RF hai lớp; via/paste QFN; BOM và điều kiện xưởng. Theo AGENTS.md, chỉ xuất Gerber sau khi người dùng duyệt hồ sơ rủi ro của layout cuối.

## Bring-up RECOM — 2026-10-25

J4 chỉ lắp R-78E5.0-1.0 đúng1VIN/2GND/3VOUT; bỏ Pololu/socket cũ.
C57 đúng cực; C58 là100nF0402. Scope Vin khi bật/tắt/cắm nóng và xác nhận
soft-start nguồn12V. Tăng tải5V từng bước tới0,9A để kiểm chứng budget có điều
kiện; đồng thời đo3V3/LDO khiWi-Fi/IR chạy. Định mứcLDO không chứng minh nhiệt đạt.
Đo ripple/transient tạiJ4 và IC; thử trong hộp ở nhiệt độ dự kiến. Mốc60°C trên
derating không phải nhiệt độ vận hành đã duyệt. Tổngtụ bảo thủ kể cả20% là
94,576µF <220µF; vẫn thử inrush/khởi động thực. Không thêm tải ngoài chưa tính.
RF/crystal/6V/front12V và footprint cũ ngoàiJ4 đã đối chiếu baseline không đổi;
điều này không thay thế đoRF/EMC/nhiệt hoặc thử máy.
