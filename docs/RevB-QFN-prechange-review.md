# Review trước thay đổi: RevB ESP32 QFN + SMA

Trạng thái: yêu cầu và kiến trúc sơ bộ; chưa phải schematic/PCB đã kiểm tra hoặc gói sản xuất. Người dùng đã xác nhận IC ESP32 QFN rời, anten SMA ngoài và chuẩn bị theo JLCPCB. Hai vai là hai góc đánh giá của cùng trợ lý.

## JaeBin — IC / nguồn / SI / RF

1. Chọn hướng ESP32-D0WD-V3, QFN48 5x5mm, ECO V3; cần flash ngoài. Datasheet v5.3 liệt kê ESP32-D0WDQ6-V3 6x6mm là NRND. Không dùng U4WDH để tránh GPIO16/17 bị flash nội chiếm. Không PSRAM để giữ pin servo.
2. Duy trì nguồn 12V bảo vệ -> hai XL4015 6V độc lập và buck 5V logic. Bổ sung nguồn 3.3V cung cấp ít nhất 500mA theo Espressif, cộng headroom cảm biến/USB. Regulator phải kiểm tra nhiệt và dropout ở Vin thấp nhất, không lựa theo dòng in trên tên.
3. Mỗi chân nguồn phải có tụ local và đường hồi GND ngắn. VDD_SDIO cấp flash 3.3V; GPIO12 phải có trạng thái boot thích hợp, tránh chọn nhầm điện áp flash 1.8V. Kiểm tra GPIO0/2/5/12/15 khi reset.
4. Thạch anh 40MHz, độ chính xác theo hướng dẫn hãng; tụ tải lấy từ CL của part cụ thể và điện dung ký sinh, không sao chép giá trị từ module. CAP1/CAP2 của IC cần mạng RC theo datasheet, không được bỏ chỉ vì không có trên module pinout.
5. EN/CHIP_PU không để nổi; dự kiến RC 10k/1u theo hãng, kiểm tra timing thực tế và dự phòng supervisor khi nguồn lên/xuống bất thường. Nút BOOT và RESET cần tiếp cận được.
6. ESP32 cổ điển không có USB native: cần IC USB-UART rời hoặc đầu nạp UART phù hợp. Hướng giữ USB onboard bằng CP2102N; thiết kế nguồn và VBUS sense theo datasheet, không nối 5V trực tiếp vào VBUS sense. Manual BOOT/RESET luôn phải dùng được, kể cả auto-download lỗi.
7. RF đi tới SMA qua mạng matching sát LNA_IN. Anten ngoài vẫn cần matching chip và RF 50 ohm; không được nối LNA_IN thẳng SMA rồi tuyên bố đã khớp. Theo hướng dẫn hiện hành, linh kiện matching 0201; giá trị ban đầu và thông số cuối phải phân biệt, cần tuning/đo RF.
8. Hai lớp có thể dùng nhưng mặt dưới cần ground liên tục dưới MCU/RF/crystal. Không autoroute tín hiệu hoặc nguồn servo xuyên vùng reference này. Dây SMA/anten thực tế và vỏ hộp ảnh hưởng nghiệm thu cuối.

## Jbungia — DFM / DFA / sửa chữa

1. Bỏ socket J18/J19 và vùng thân DevKit; thay bằng IC QFN có exposed pad. Không giữ tuyên bố carrier toàn THT hoặc có thể chỉ hàn bằng mỏ.
2. JLCPCB công bố hỗ trợ QFN và 0201 ở dịch vụ phù hợp. Tuy nhiên cần kiểm tra từng part/BOM trong dịch vụ đặt thực, không suy ra mọi linh kiện đều được lắp hoặc có sẵn.
3. Footprint 5x5 không dùng lẫn 6x6. Kiểm tra pitch, kích thước pad, EP, mask, paste và dấu pin1 từ bản vẽ hãng. Via ground dưới EP phải xử lý tránh hút thiếc; chọn phương án tent/fill/cap theo DFM xưởng, không tự coi via mở là đạt.
4. Hướng dẫn Espressif yêu cầu ít nhất chín ground vias tại pad giữa. Bố trí phải đối chiếu đồng thời đường nguồn ở thiết kế hai lớp, paste window và khả năng khoan. Không copy pad EP kích thước khác package để dễ đi dây.
5. SMT mặt trên, lắp reflow trước; THT/terminal/tụ lớn sau. Cần fiducial, vùng kẹp gá và kiểm tra khả năng xử lý board 100x100; tooling/panel do xưởng xác nhận. Không tự tăng kích thước board sản phẩm để thêm rail gá.
6. QFN và 0201 khó sửa tại máy: thêm test point nguồn/EN/UART/BOOT dễ tiếp cận, điểm cô lập nguồn và tài liệu phân vùng lỗi; không đặt test stub trên đường RF hoặc đường crystal.
7. Giữ cầu chì thay được, terminal rút cắm, PTC, LED, test point và tùy chọn limit DNP. Chuẩn bị BOM SMT/MPN, BOM THT và placement với rotation được kiểm tra bằng preview xưởng.

## Bằng chứng / nguồn gốc thông số

- [ESP32 datasheet v5.3: mã IC, pinout, flash, package](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
- [Espressif schematic checklist: nguồn, reset, crystal, CAP, strapping, matching](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html)
- [Espressif layout: hai lớp, ground, EP vias và RF](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html)
- [CP2102N datasheet: nguồn, VBUS divider, USB và pinout](https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf)
- [JLCPCB PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
- [JLCPCB impedance calculator guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator)

## Những mục chưa được đóng

Chưa chọn MPN cuối cho regulator/crystal/SMA/ESD/flash; chưa có xác nhận stackup và bề rộng RF; chưa đo RF, nhiệt, ripple, nguồn reset hoặc khả năng xuất tô thật. Những thông số này phải được đối chiếu trong từng bước thực hiện, không đổi thành PASS từ kết quả RevA2. RevA2 ZIP đang có trên máy không phải gói ESP32 QFN.

## Trình tự thực hiện sau review

Chọn part và pin map thật -> schematic nhiều trang theo chức năng, chữ đọc được -> ERC và kiểm tra net độc lập -> placement chip/crystal/flash/RF thủ công -> đi dây nguồn/servo và tín hiệu -> DRC/parity -> BOM/placement/ảnh xưởng và checklist mẫu -> người dùng duyệt rủi ro trước Gerber. Mỗi thay đổi schematic/PCB phải kèm kiểm tra theo AGENTS.md; không tự xuất Gerber.

## Bổ sung review trước đi dây: giám sát nguồn

JaeBin: nguồn servo dùng chung nguồn gốc 12V, nên thêm supervisor reset độc lập thay vì chỉ dựa RC EN. Chọn TLV803EA29DBZR theo ví dụ TI: ngưỡng 2.93V, giữ reset khoảng 200ms, open-drain chia sẻ EN với nút RESET và auto-download, không tranh chấp ngõ ra push-pull. Cần đo brownout thực; không coi ngưỡng nominal là bảo vệ tuyệt đối flash hoặc mọi xung nhanh. Jbungia: SOT23-3 pin1 GND, pin2 RESET, pin3 VDD; không thay bằng các hậu tố R/V có pinout khác. Thêm 100nF sát nguồn supervisor và kiểm tra lại ERC/DRC.

Nguồn: https://www.ti.com/lit/ds/symlink/tlv803e.pdf (ví dụ TLV803EA29DBZR và bảng pinout).

## Review bổ sung: biên điện áp nguồn flash trước khi chốt BOM

JaeBin: ở chế độ 3,3 V, VDD_SDIO nhận nguồn từ miền RTC qua điện trở nội khoảng 6 Ω; Espressif yêu cầu miền RTC giữ trên 3,0 V khi cấp flash 3,3 V. Vì vậy chọn bản supervisor **TLV803EA30DBZR, ngưỡng 3,08 V**, thay lựa chọn EA29 trước đó. Với sai số ngưỡng ±2%, ngưỡng giảm áp thấp nhất tính toán là 3,018 V; vẫn cần đo đáp ứng xung, sụt áp nội và dòng flash thực tế. Đây không phải bảo đảm không mất dữ liệu khi rút điện giữa lúc ghi flash. Firmware phải dùng cơ chế lưu dữ liệu chịu mất điện.

Jbungia: EA30DBZR giữ pin 1 GND / 2 RESET / 3 VDD, cùng footprint SOT23, nên không đổi chân hoặc diện tích lắp. Không thay bằng R/V pinout. Đổi đồng bộ tên/value/MPN trong schematic, manifest, PCB và BOM; chạy lại ERC/DRC/parity. Biên giữa ngưỡng reset cao nhất và nguồn LDO thấp nhất phải được thử dưới tải Wi-Fi để loại trừ reset lặp.

Nguồn: [Espressif: VDD_SDIO và reset](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html), [TI: TLV803EA30DBZR](https://www.ti.com/product/TLV803E/part-details/TLV803EA30DBZR), [TI datasheet: mã 30 = 3,08 V và pinout](https://www.ti.com/lit/ds/symlink/tlv803e.pdf).

## Review RF trước sửa hình học và giá trị khởi đầu

JaeBin: đoạn sau cuộn cảm tới SMA cần đường rộng nhất quán, không kéo dài vài mm bằng đường 0,15 mm qua từng pad shunt. Dời trục đường chính xuống y=152,5 mm, rộng ứng viên 1,1 mm, nối C31 và diode ESD D8 bằng các nhánh ngắn khoảng 0,425 mm. Giữ ground liên tục bên dưới; bề rộng này chưa được xác nhận 50 Ω. D8 có điện dung điển hình 0,9 pF, do đó không cộng thêm nguyên 1,5 pF của mạch tham khảo rồi coi là tương đương: chọn **C31 0,5 pF khởi đầu**, GRM0335C1HR50BA01D, để tổng điện dung nominal của hai linh kiện khoảng 1,4 pF, chưa gồm ký sinh. Điện dung ESD phụ thuộc bias/tần số và sai số, nên phép cộng này chỉ dùng chọn điểm bắt đầu đo; không phải nghiệm thu matching hoặc thay cho VNA/đo phát thu.

Jbungia: không đổi footprint 0201; đường rộng tránh pad GND của C31/D8 nhờ nhánh shunt. Ground via gần tụ phải tent và tránh paste pad để giảm hút thiếc; vẫn cần xưởng duyệt. Chạy DRC sau đổi hình học, kiểm tra lại BOM và không đánh đồng giá trị ban đầu với giá trị RF đã tuning.

Nguồn: [Murata model list xác nhận dòng 0,5 pF C0G 0201 50 V](https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/static-model/component-list-s-mlcc-2506.ashx?cvid=20250805040438000000&la=ja-jp), [Nexperia PESD5V0X1BL](https://www.nexperia.com/product/PESD5V0X1BL), [Espressif RF layout](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html).

## Review fanout QFN trước khi đi lại vùng MCU

JaeBin: các nhánh nguồn đi vòng trước khi thoát các chân lân cận tạo ra vùng kín quanh pad QFN. Thay bằng fanout có thứ tự: đoạn đầu vuông góc hàng pad, sau đó mở rộng ra hàng via ngoài thân IC; giữ nguyên ground dưới MCU, RF và crystal. Đưa tụ 100 nF C23 sát miền VDDA pin 1 bằng footprint 0201, cùng MPN GRM033R71C104KE14D đã chọn cho C22. Dời bộ RC CAP1/CAP2, đường boot và các tụ/IC lân cận khi cần để bảo toàn lối thoát; không đổi GPIO/net. Di chuyển supervisor khỏi hàng via và kéo tụ của nó theo sát chân VDD. Nguồn flash và CPU có tụ cục bộ sau các via thoát chân.

Jbungia: via fanout 0,40/0,20 mm có annular ring 0,10 mm; giữ via ground EP 0,50/0,20 mm trong footprint hãng và các via khác theo thiết kế. Không dùng via-in-pad mở trên pad SMT. Yêu cầu này vẫn nằm trong chuẩn hai lớp 1 oz JLCPCB đang chuẩn bị; xưởng phải duyệt QFN/stencil/via EP. C23 0201 không đổi loại dịch vụ vì khối RF đã cần Standard PCBA. Kiểm tra courtyard, hole-to-hole, soldermask, clearance và parity sau bước fanout, rồi mới đi các kết nối còn lại.
