# Kế hoạch Nâng cấp Phần cứng: Chuyển đổi sang ESP32-S3-WROOM-1U

**Ngày lập kế hoạch:** 2026-10-28  
**Trạng thái:** DRAFT / CHỜ DUYỆT TRƯỚC KHI THI CÔNG  
**Mục tiêu:** Tiết kiệm chi phí triệt để (giảm 60–70% chi phí PCBA), loại bỏ linh kiện chân siêu nhỏ (QFN 0.35mm, 0402, 0201), tối ưu hóa khả năng tự hàn và gia công tại các xưởng SMT giá rẻ trong nước và quốc tế.

---

## 1. Phân tích Thay đổi Phần cứng (BOM & Schematic Delta)

### 1.1. Các linh kiện được LOẠI BỎ HOÀN TOÀN (Cắt giảm chi phí & diện tích)
| Linh kiện cũ | Mã / Footprint cũ | Lý do loại bỏ khi dùng ESP32-S3-WROOM-1U |
|---|---|---|
| **U1** (MCU ESP32) | ESP32-D0WD-V3 (QFN48 5x5mm, pitch 0.35mm) | Thay bằng module tích hợp ESP32-S3-WROOM-1U (pitch 1.27mm). |
| **U4** (Flash SPI) | Winbond W25Q32JVSSIQ (SOIC-8) | Module S3 đã tích hợp sẵn Flash 8MB hoặc 16MB bên trong vỏ nhôm. |
| **X1, C24, C25** (Thạch anh) | Crystal 40MHz 10ppm + 2x tụ tải 16pF | Module S3 đã tích hợp sẵn thạch anh dao động chính xác cao. |
| **R40 – R45** (Điện trở SPI) | 6x điện trở 0R/33R damping Flash SPI | Đường SPI Flash nằm trọn vẹn trong module, không cần trở ngoài. |
| **U2** (USB-UART Bridge) | CP2102N (QFN24/28) | **ESP32-S3 tích hợp sẵn USB Native (USB-Serial-JTAG)** tại GPIO19/20. |
| **Q3, Q4 & trở phân áp** | S8050 / MMBTH10 auto-reset circuit | Mạch USB Native tự động reset/nạp firmware, không cần mạch transistor ngoài. |
| **C30, L1, C31** (RF Matching) | Mạng lọc pi-matching 1.5pF / 2.7nH / 0.5pF (0201) | Mạch RF đã chuẩn hóa bên trong module, đạt chứng chỉ FCC/CE. |
| **J10** (Cọc SMA hàn bo) | Đầu nối SMA cái hàn góc trực tiếp trên bo mạch | **ESP32-S3-WROOM-1U có sẵn cổng IPEX (U.FL)** trên lưng; dùng cáp pigtail IPEX sang SMA bắt ra vỏ hộp máy bán hàng (thuận tiện cơ khí hơn nhiều). |

### 1.2. Các khối GIỮ NGUYÊN 100% (Bảo toàn độ tin cậy công nghiệp)
- **Khối nguồn 5V Logic:** Module **RECOM R-78E5.0-1.0** (THT 3 chân) + C57 (10µF) + C58 (100nF).
- **Khối nguồn 3.3V:** LDO **LD1117S33** + tụ lọc đầu vào/ra.
- **Khối bảo vệ đầu vào 12V:** Cầu chì F1 5A, Diode Schottky chống ngược cực, Diode TVS kẹp xung áp.
- **Khối động cơ Servo 6V:** 
  - 2 đầu nối J2, J3 nối ra 2 module Buck XL4015 gá ngoài hộp điện (rail +6V_A và +6V_B riêng biệt).
  - 2 cầu chì tự phục hồi PTC MF-R300 (2.5A).
  - 2 tụ hóa lớn 2200µF/25V chống sụt áp tức thời.
  - 4 cổng servo J5–J8 kèm điện trở hạn dòng 330Ω và điện trở kéo xuống an toàn 10kΩ.
- **Khối cảm biến quang IR:**
  - 2 cổng phát IR (J13, J14) qua transistor S8050 phát xung 38kHz.
  - 2 cổng nhận IR RX (J11, J12) kết nối cáp 3 dây tới mắt nhận TSOP38238/VS1838B.
- **Khối chẩn đoán:** 5 LED báo nguồn (12V, 6V-A, 6V-B, 5V, 3.3V) và các Test Point.

---

## 2. Đề xuất Bảng Phân bổ Chân GPIO Mới (Pinout Mapping)

Do **ESP32-S3 sử dụng chân GPIO19 làm USB D- và GPIO20 làm USB D+**, ta cần điều chỉnh nhẹ chân Servo 2 Bottom (vốn nằm ở GPIO19 trên RevB cũ) sang chân khác:

| Chức năng phần cứng | Chân cũ (ESP32 D0WD) | **Chân đề xuất mới (ESP32-S3)** | Ghi chú kỹ thuật |
|---|:---:|:---:|---|
| **USB Data Minus (D-)** | *(Nối qua CP2102N)* | **GPIO19** | Chân phần cứng USB OTG / Serial-JTAG của S3 |
| **USB Data Plus (D+)** | *(Nối qua CP2102N)* | **GPIO20** | Chân phần cứng USB OTG / Serial-JTAG của S3 |
| **Servo 1 - TOP (Iris Trên Cột 1)** | GPIO16 | **GPIO16** | Giữ nguyên (LEDC PWM 50Hz) |
| **Servo 1 - BOTTOM (Iris Dưới Cột 1)** | GPIO17 | **GPIO17** | Giữ nguyên (LEDC PWM 50Hz) |
| **Servo 2 - TOP (Iris Trên Cột 2)** | GPIO18 | **GPIO18** | Giữ nguyên (LEDC PWM 50Hz) |
| **Servo 2 - BOTTOM (Iris Dưới Cột 2)** | *GPIO19* | **GPIO14** *(Đổi chân)* | **Đổi sang GPIO14** để nhường GPIO19 cho cổng USB |
| **IR TX 38kHz (Phát xung)** | GPIO23 | **GPIO21** *(Đổi chân)* | Điều chế xung vuông 38kHz burst qua LEDC/RMT |
| **IR RX Cột 1 (Mắt nhận rơi tô 1)** | GPIO34 | **GPIO4** *(Đổi chân)* | Chân ngắt đọc tín hiệu TSOP38238 |
| **IR RX Cột 2 (Mắt nhận rơi tô 2)** | GPIO35 | **GPIO5** *(Đổi chân)* | Chân ngắt đọc tín hiệu TSOP38238 |
| **Limit Switch 1..4 (DNP - Dự phòng)** | GPIO25, 26, 27, 32 | **GPIO6, 7, 8, 9** | Đầu vào kéo lên 10kΩ + tụ 100nF |
| **I2C SDA / SCL (Dự phòng mở rộng)**| GPIO21, 22 | **GPIO1, GPIO2** | Giao tiếp cảm biến / màn hình nếu cần |
| **Chân Nút bấm Reset (CHIP_PU / EN)**| EN | **CHIP_PU (EN)** | Có nút nhấn SW1 + tụ 1µF chống rung |
| **Chân Nút bấm Boot (BOOT)** | GPIO0 | **GPIO0** | Có nút nhấn SW2 để ép vào ROM Bootloader nếu cần |

---

## 3. Ràng buộc Thiết kế PCB & DFM (Dễ hàn, Chi phí thấp nhất)

1. **Số lớp & Kích thước:** Giữ nguyên PCB 2 lớp, kích thước tối đa 100 × 100 mm.
2. **Quy chuẩn đi dây (Track/Clearance):**
   - Không còn chân 0.35mm, toàn bộ chân module là **1.27 mm**.
   - Bề rộng đường tín hiệu: **$\ge 0.25\text{ mm}$ (10 mil)**.
   - Khoảng cách cách điện (Clearance): **$\ge 0.20\text{ mm}$ (8 mil)**.
   - Đường nguồn 12V và 6V servo: **$\ge 2.0\text{ mm}$** (chịu dòng 5A, không dùng via).
   - Lỗ via: Khoan lỗ $\ge 0.3\text{ mm}$, vành pad $\ge 0.6\text{ mm}$ (chuẩn rẻ nhất của mọi xưởng).
3. **Footprint Linh kiện thụ động:**
   - Toàn bộ điện trở, tụ điện gốm chuyển sang kích thước **0603 (1608 Metric)** hoặc **0805 (2012 Metric)** $\rightarrow$ Dễ dàng hàn tay hoặc kiểm tra bằng mắt thường.
4. **Lớp mạ bề mặt (Surface Finish):**
   - Do chân module 1.27mm to và phẳng, bạn có thể chọn **HASL (có chì)** hoặc **LeadFree HASL (không chì)** giá rẻ nhất tại JLCPCB (khoảng $2 USD cho 5 bo mạch), không bắt buộc phải tốn tiền mạ vàng ENIG.

---

## 4. Chiến lược Sao lưu & Quản trị Rủi ro (Backup & Safe Rollback)

Để tuyệt đối **không làm hỏng hoặc mất mát các tài liệu / Gerber đã verified của bản RevB 0402**:

1. **Tạo nhánh Git mới riêng biệt:**
   - Nhánh mới: `feat/esp32-s3-wroom-upgrade`.
   - Giữ nguyên các nhánh cũ `fix/revb-recom-logic-supply` và gói phát hành [`releases/revb/FV-CTRL_RevB-Gerber-2026-10-26.zip`](file:///f:/project/repo-github/pcb/pcb/releases/revb/FV-CTRL_RevB-Gerber-2026-10-26.zip) làm phương án dự phòng gốc (Golden Fallback).
2. **Tách riêng thư mục phần cứng:**
   - Thiết kế mới sẽ được đặt tại thư mục riêng: `hardware/rev_s3/` (hoặc `hardware/revc/`), hoàn toàn không ghi đè vào thư mục `hardware/revb/`.
3. **Tương thích Firmware:**
   - Logic điều khiển cốt lõi trong [`simulation/revb/controller.h`](file:///f:/project/repo-github/pcb/pcb/simulation/revb/controller.h) (State Machine, Journaling chống mất điện, Debounce) được **giữ nguyên 100% không đổi 1 dòng code**.
   - Chỉ cập nhật file định nghĩa chân pin: [`FV-CTRL_RevB-pins.h`](file:///f:/project/repo-github/pcb/pcb/docs/revb/FV-CTRL_RevB-pins.h) sang file chân mới `FV-CTRL_RevS3-pins.h` khớp với Bảng mục 2.

---

## 5. Lộ trình Thực hiện (Execution Phases & Gates)

- **Gate 1 (Review Kiến trúc):** Người dùng duyệt Bảng phân bổ chân GPIO mục 2 và cấu hình module ESP32-S3-WROOM-1U.
- **Gate 2 (Backup & Khởi tạo):** Tạo nhánh git `feat/esp32-s3-wroom-upgrade`, tạo thư mục `hardware/rev_s3/`, import footprint module KiCad chuẩn.
- **Gate 3 (Hoàn thiện Schematic):** Vẽ sơ đồ nguyên lý mới, thay thế khối MCU/USB/Flash, kết nối cổng USB Native, chạy ERC 0 lỗi.
- **Gate 4 (Layout PCB 2 lớp):** Bố trí linh kiện 0603 chân to, đi dây tín hiệu $\ge 0.25\text{ mm}$, đổ mass GND nguyên vẹn, chạy DRC 0 lỗi, 0 hở mạch.
- **Gate 5 (Kiểm chứng & Xuất File):** Xuất trọn bộ Gerber, BOM linh kiện chân to giá rẻ, CPL và hướng dẫn đặt hàng tiết kiệm chi phí.
