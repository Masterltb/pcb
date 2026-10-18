# PROJECT.md: PCB điều khiển máy bán tô trái cây tự động (Rev A, production-ready)

## 1. Mục tiêu
Thiết kế PCB 2 lớp, chi phí thấp nhất, tự hàn (THT), điều khiển 2 cột xuất tô theo cơ chế FIFO.
Ưu tiên: dễ thay thế, dễ bảo trì, dễ chẩn đoán. Mọi thứ có thể hỏng đều phải rút cắm được, mọi rail đều đo được.
Kế hoạch: làm Rev A khoảng 5 tấm, chạy thử trên máy thật, ghi lỗi rồi mới ra Rev B.

## 2. Cơ chế hoạt động (mỗi cột)
- Mỗi cột có 2 cơ chế giữ chồng lên nhau: TRÊN và DƯỚI, luân phiên đóng/mở.
- Xuất tô: đóng TRÊN (giữ tô kế cuối) -> mở DƯỚI -> tô rơi, IR báo -> đóng DƯỚI -> mở TRÊN cho chồng tô tụt xuống DƯỚI.
- Trạng thái nghỉ (giả định, CẦN XÁC NHẬN): DƯỚI đóng giữ chồng tô, TRÊN mở.
- Không bao giờ để TRÊN và DƯỚI cùng mở. Mỗi cột chỉ có 1 servo chạy tại một thời điểm.
- Servo là loại 360 độ (continuous rotation): điều khiển theo thời gian, không có phản hồi vị trí. Phản hồi chính là cảm biến IR; limit switch là tùy chọn dự phòng chống lệch thời gian.

## 3. Kiến trúc
- **Mainboard** (100 x 100 mm tối đa): nguồn, ESP32, đầu nối.
- **2 board RX cảm biến IR nhỏ** (mỗi cột 1 tấm) đặt tại máng rơi tô: TSOP/VS1838B + lọc nguồn, nối về mainboard bằng cáp 3 dây.
- **2 LED IR phát** (mỗi cột 1 cái) đặt đối diện receiver, nối về mainboard bằng cáp 2 dây. Điện trở hạn dòng nằm trên mainboard.
- Mọi dây ngoài board đều qua đầu nối. Không hàn dây trực tiếp vào PCB.

```
12V (nguồn tổ ong) -> [cầu chì, đế thay được] -> [chống ngược cực] -> [TVS] -> rail 12V
 rail 12V -> Buck A (XL4015 module >=5A, 6.0V) -> [PTC] -> servo cột 1 (2 con)
 rail 12V -> Buck B (XL4015 module >=5A, 6.0V) -> [PTC] -> servo cột 2 (2 con)
 rail 12V -> Buck C (module nhỏ 5V) -> ESP32 DevKit (chân 5V) + IR TX
 ESP32 -> PWM 4 servo, 1 chân IR TX 38kHz, 2 chân đọc IR RX, 4 chân limit switch (tùy chọn)
GND chung toàn board.
```

## 4. Linh kiện chính
| Linh kiện | SL | Ghi chú |
|---|---|---|
| ESP32 DevKit 38 chân | 1 | Cắm qua header cái, KHÔNG hàn trực tiếp |
| MG996R quay liên tục 360° (người dùng xác nhận) | 4 | 4.8–6.6V, đỉnh ~2.5A/con khi kẹt; điều khiển theo thời gian, không có phản hồi vị trí. |
| XL4015 module >=5A | 2 | Cắm qua header, chỉnh 6.0V TRƯỚC khi nối servo. Thay LM2596 3A theo người dùng duyệt vì MG996R có dòng kẹt cao; footprint chỉ chốt theo module thực tế. |
| Buck 5V nhỏ cho logic (vd MP1584EN) | 1 | Tách khỏi nhánh servo để tránh reset ESP32 |
| TSOP38238 hoặc VS1838B | 2 | 38kHz, cấp 3.3V, trên board RX riêng |
| LED IR 940nm (TSAL6200 / IR333-A) | 2 | Mỗi LED có điện trở riêng, 5V |
| Transistor S8050 / 2N2222 | 1 | Đóng cắt LED IR |
| Nguồn tổ ong 12V 40A | 1 | Rất dư, bảo vệ bằng cầu chì trên board |

BOM cuối cùng phải có MPN và ít nhất 1 phương án thay thế cho từng món.

## 5. Bảng gán chân ESP32
| Chức năng | GPIO |
|---|---|
| Servo cột 1 TRÊN / DƯỚI | 16 / 17 |
| Servo cột 2 TRÊN / DƯỚI | 18 / 19 |
| IR TX 38kHz (1 chân, qua transistor, 2 LED) | 23 |
| IR RX cột 1 / cột 2 | 34 / 35 (chỉ input) |
| Limit switch 1–4 (tùy chọn, DNP) | 25, 26, 27, 32 |
| I2C dự phòng | 21 (SDA), 22 (SCL) |
| Dự phòng | 33 |

Tránh strapping pin: GPIO 0, 2, 12, 15. Không đổi bảng này khi chưa hỏi người dùng.

## 6. Đầu nối (mọi kết nối ngoài board)
| Kết nối | Loại | Ghi chú |
|---|---|---|
| Nguồn 12V vào | Terminal vít cắm rời (pluggable) | Tháo cả cụm khi bảo trì |
| Servo x4 (S1-TOP, S1-BOT, S2-TOP, S2-BOT) | Header 3 chân 2.54mm, theo đúng đầu servo gốc | Silkscreen ghi GND / V+ / SIG, chừa chỗ kẹp dây chống rung |
| IR RX x2 | JST-XH 3 chân có khóa chiều | VCC 3.3V, OUT, GND |
| IR TX LED x2 | JST-XH 2 chân có khóa chiều | |
| Limit switch x4 | JST-XH 2 chân, DNP | Kéo lên 10k + tụ 100nF, chỉ lắp khi cần |
| I2C dự phòng | Header 4 chân | |

## 7. Yêu cầu mạch
**Bảo vệ**
- Đầu vào 12V: cầu chì khoảng 5A (đế cầu chì để thay được), chống ngược cực, TVS. Agent đề xuất loại THT, người dùng duyệt.
- Mỗi rail servo: cầu chì tự phục hồi (PTC) chọn theo dòng stall ~2.5A/con (xác nhận theo datasheet), tụ điện phân 1000–2200µF (16V trở lên) sát chân cấp servo, kèm 100nF.
- Mỗi chân PWM servo: điện trở nối tiếp ~330Ω và **điện trở kéo xuống 10k** để servo không tự quay khi ESP32 đang khởi động.

**IR**
- LED IR: 5V, điện trở ~100–150Ω mỗi LED, base transistor ~1kΩ.
- Board RX: receiver cấp 3.3V, lọc 100Ω nối tiếp + tụ 4.7µF sát chân VCC. Ghi rõ pinout trên silkscreen vì hàng clone có thể khác.

**Chẩn đoán**
- LED báo nguồn (kèm điện trở) cho từng rail: 12V, 6V-A, 6V-B, 5V, 3.3V.
- Test point cho 12V, 6V-A, 6V-B, 5V, 3.3V và GND.
- Silkscreen có mã phiên bản và ngày (ví dụ `FV-CTRL Rev A`), nhãn rõ mọi đầu nối.
- Cổng USB của ESP32 phải nằm sát mép board, truy cập được để nạp firmware khi đã lắp.

## 8. Ràng buộc PCB và DFM
- 2 lớp, tối đa 100 x 100 mm, toàn bộ THT, 4 lỗ gá M3.
- Đường 12V và nhánh servo rộng khoảng 2mm trở lên, GND dùng copper pour. Trace/space tối thiểu tín hiệu khoảng 0.25mm, pad đủ lớn cho hàn tay.
- Buck servo đặt ở mép board, xa ESP32 và đường tín hiệu IR, chừa khoảng trống thoát nhiệt.
- Gom đầu nối theo cạnh: nguồn một cạnh, servo một cạnh, cảm biến một cạnh.

## 9. Hồ sơ cần xuất cùng board
- Gerber + drill, BOM (MPN + phương án thay thế), sơ đồ lắp ráp.
- Checklist bring-up lần đầu: đo từng rail (12V, 6V-A, 6V-B, 5V, 3.3V) khi chưa cắm ESP32 và servo, rồi mới lắp lần lượt.
- File gán chân firmware (`pins.h`) khớp mục 5.

## 10. Việc chưa chốt (cần người dùng đo/xác nhận)
- Kích thước và khoảng cách chân thật của 2 module XL4015 >=5A sẽ mua/dùng (đo bằng thước kẹp).
- Khoảng cách giữa 2 hàng header của ESP32 DevKit 38 chân đang dùng.
- Test IR với đúng loại tô (tô trong suốt có thể không chắn tia 940nm).
- Kích thước buck 5V nhỏ sẽ mua.
- MG996R đã xác nhận là bản quay liên tục 360°.

## 11. Ngoài phạm vi PCB nhưng bắt buộc trước khi vận hành
Phần điện lưới (AC) của nguồn tổ ong cần vỏ kín che đầu AC, cầu chì/cầu dao phía AC và nối đất vỏ. Nhờ người có chuyên môn điện kiểm tra trước khi đưa máy vào sử dụng.

## 12. Ngữ cảnh vận hành (CẦN NGƯỜI DÙNG ĐIỀN, agent không được tự đoán)
| Hạng mục | Giá trị |
|---|---|
| Nơi đặt máy (trong nhà / ngoài trời / có điều hòa) | TODO(user) |
| Ngăn chứa tô có làm lạnh/làm mát không (ảnh hưởng ngưng tụ hơi nước lên board) | TODO(user) |
| Nguy cơ nước, nước trái cây, bụi văng vào khu vực board; vị trí board trong máy | TODO(user) |
| Rung động khi vận hành | TODO(user) |
| Tô nhựa dùng một lần: đường kính miệng 17 cm, cao 6 cm, dung tích 850 ml; khối lượng khi đầy và chất liệu (trong suốt/mờ) | Đã xác nhận: miệng 17 cm, cao 6 cm, 850 ml; Chất liệu: Nhựa PET/PP trong suốt hoàn toàn (đặt cảm biến IR góc chiếu lệch hoặc đón gờ vành để khúc xạ/tán xạ cản tia 940nm) |
| Số tô tối đa mỗi cột, chiều cao chồng | TODO(user) |
| Thời gian mở/đóng mỗi cơ cấu giữ (ms) với servo 360 | TODO(user) |
| Chiều dài cáp servo, cáp IR (cm) | TODO(user) |
| Kích thước hộp chứa board, vị trí gá, hướng cổng USB | TODO(user) |
| Có thêm màn hình / nút / thanh toán / WiFi / cảm biến hết hàng / nhiệt độ không (ảnh hưởng GPIO dự phòng) | TODO(user) |
| Két nước tản nhiệt (ngoài phạm vi PCB Rev A): mục tiêu làm mát, nhiệt độ nước đặt, nhiệt độ môi trường, thể tích két, chiều dài ống, vị trí và nguồn làm lạnh | TODO(user) |
| Số board cần, ngân sách mỗi board, nhà sản xuất (Rev A khoảng 5 tấm) | TODO(user) |

## 13. Hành vi hệ thống (ĐỀ XUẤT, chờ người dùng duyệt)
Máy trạng thái mỗi cột:
`IDLE (TRÊN mở, DƯỚI đóng)` -> `CLOSE_TOP` -> `OPEN_BOT` -> `WAIT_IR (timeout T_ir)` -> `CLOSE_BOT` -> `OPEN_TOP` -> `IDLE`.
- Bất biến: không bao giờ để TRÊN và DƯỚI cùng mở; mỗi cột chỉ một servo chạy tại một thời điểm (firmware có interlock).
- IR timeout (tô không rơi, hết tô hoặc kẹt): đóng DƯỚI, KHÔNG mở TRÊN, báo lỗi `SOLD_OUT_OR_JAM`.
- Mất điện giữa chu trình: servo 360 điều khiển theo thời gian (Timed Rotation) kết hợp giám sát cảm biến rơi IR 38kHz (không cần thêm dây limit switch). Khi khởi động lại: thực hiện chu trình phục hồi đóng cả 2 cơ chế theo thời gian quy định để đưa về trạng thái an toàn trước khi vào IDLE.
- Giá trị timeout T_ir, thời gian mỗi bước: TODO(user).

## 14. Ghi chú IR (cần xác nhận bằng datasheet và test thực tế)
- Receiver 38kHz (họ TSOP/VS1838B) có thể triệt tín hiệu khi sóng mang phát liên tục. Firmware nên phát theo burst (bật/tắt khoảng 1ms) và coi là "chắn tia" khi KHÔNG thấy mức LOW ở OUT trong vài ms. Firmware test đã làm theo cách này.
- Điều này thay thế cách nói trước đó là phát 38kHz liên tục.

## 15. Bộ skill đi kèm
Bộ thiết kế: `fv-pcb-design` (điều phối), `fv-pcb-schematic`, `fv-pcb-layout`, `fv-pcb-release`.
Bộ kiểm thử: `fv-pcb-verify` (ERC/DRC + bảng chân + review), `fv-pcb-bringup`, `fv-pcb-functional-test`, `fv-pcb-debug`.
Nằm trong `.claude/skills/`.

## 16. Két nước tản nhiệt (ngoài phạm vi PCB Rev A)
- Rev A không có mạch, GPIO, đầu nối, nguồn cấp hoặc chức năng firmware cho két nước tản nhiệt.
- Két nước, bơm, bộ trao đổi nhiệt và bộ điều khiển nhiệt được thiết kế, cấp nguồn và kiểm thử như một phân hệ cơ khí/nhiệt độc lập.
- Khi bố trí máy, két, ống và khay hứng nước ngưng phải đặt tách PCB; PCB đặt cao hơn đáy máy và không nằm dưới điểm có thể rò hoặc nhỏ giọt.
- Khi cần tích hợp ở Rev sau, phải chốt mục tiêu nhiệt, điện áp/dòng của tải, loại tín hiệu trạng thái và phương án an toàn rồi mới thay đổi kiến trúc nguồn, GPIO hoặc schematic.
