# RevB — đối chiếu ảnh và review từng linh kiện

Ngày: 2026-10-24. Review trên file, không phải chứng nhận thử phần cứng.

## Xác minh phiên bản

- Ảnh người dùng khớp bố trí bản RevB trong docs/revb/assembly/RevB-top.png; không thể chứng minh byte/version file chỉ bằng ảnh.
- Local HEAD 150e0fe; origin/main 01e28c8 có thêm tài liệu harness, không đổi hardware/revb, libs hay docs/revb.
- PCB/schematic local không có diff; .kicad_pro chỉ đổi metadata tên RevA sang RevB, không đổi rule trong diff hiện tại.
- PCB SHA256: `2b557319850fd61a7cfeb96cccd99f01d77a2d1a713a5be5bb94b133a8a64160`.
- Chạy lại ERC: 0; DRC: 0; unconnected: 0; parity: 0; pin/net verifier PASS; via/paste heuristic PASS (không bao gồm nghiệm thu EP).
- 149 reference BOM đều có trên PCB, giá trị khớp; 12 DNP khớp BOM và cờ PCB. PCB có 152 footprints: 149 reference BOM và 3 dấu chuẩn máy FID1/FID2/FID3; fiducial là hình đồng phục vụ căn chỉnh SMT, không phải linh kiện cần mua.
- Bản render thiếu model U1, J20, J21, J4 và một số phần bảo vệ; không được kết luận linh kiện không cần lắp chỉ vì không thấy thân 3D. DNP vẫn có thể hiện trong render.

## Hai góc review

**IC/SI/PI:** chưa chốt nghiệm thu RF50Ω/matching/crystal, nhiệt LDO, flash brownout, xung hồi6V, ESD dây ngoài và tải servo. Header I²C chưa có pull-up chuyên dụng; phải có trên ngoại vi hoặc bổ sung trước khi dùng. Servo không có phản hồi vị trí cơ cấu; IR xác nhận tô rơi không chứng minh iris đã khóa.

**DFM/DFA:** cần duyệt EP QFN, via hút thiếc, stencil và khả năng sửa; xác nhận module 5V thực, connector/SMA/USB, cực và khoảng trống. Header servo không khóa cần xử lý chống tuột ở hệ thống. Không xác nhận yield hoặc sản xuất hàng loạt từ DRC.

## Danh mục đủ 149 reference

Mỗi dòng là một reference. MPN/giá trị lấy từ BOM hiện hành, net từ design JSON đã được verifier đối chiếu. FIT nghĩa là dự kiến lắp, không phải đã đạt nghiệm thu. Các MPN phụ không được tuyên bố đã tái kiểm toàn bộ datasheet trong lượt này.

| Ref | Giá trị / MPN | Lắp | Vai trò | Net chân | Kiểm tra / điểm còn mở |
|---|---|---|---|---|---|
| J1 | 12V INPUT / 1757242 + mating 1757019 | FIT | Đầu vào 12 V | 1=+12V_IN; 2=GND | Kiểm cực, dòng tiếp điểm, dây và lực giữ connector. |
| J2 | XL4015 A: 12/G/6/G / 1757268 + mating 1757035 | FIT | Đầu nối buck ngoài: 12 V/GND/6 V/GND | 1=+12V; 2=GND; 3=+6V_A_RAW; 4=GND | Hai đầu ra 6 V độc lập; kiểm thứ tự chân và chống cắm sai; đo sụt áp. |
| J3 | XL4015 B: 12/G/6/G / 1757268 + mating 1757035 | FIT | Đầu nối buck ngoài: 12 V/GND/6 V/GND | 1=+12V; 2=GND; 3=+6V_B_RAW; 4=GND | Hai đầu ra 6 V độc lập; kiểm thứ tự chân và chống cắm sai; đo sụt áp. |
| F1 | T5A - VERIFY I2T / SCHURTER 0001.2511 + 2x Littelfuse 01110001L | FIT | Cầu chì chậm 5 A đầu vào | 1=+12V_IN; 2=+12V_FUSED | Chưa chốt phối hợp I²t với nguồn, dây, TVS và dòng khởi động; không suy bảo vệ từ nhãn 5 A. |
| Q1 | IRF4905PBF / IRF4905PBF | FIT | MOSFET P chống ngược cực | G=Q1_GATE; D=+12V_FUSED; S=+12V | Đối chiếu G/D/S khi mua; thử ngược cực có giới hạn dòng; đo tổn hao/nhiệt. |
| R9 | 10k / CFR-25JR-52-10K | FIT | Kéo gate MOSFET | 1=Q1_GATE; 2=GND | Kiểm VGS và công suất trong mọi chế độ cấp nguồn. |
| D1 | 1.5KE15CA / Littelfuse 1.5KE15CA | FIT | TVS rail 12 V | 1=+12V; 2=GND | Không kẹp trực tiếp rail servo 6 V; cần kiểm điện áp kẹp, năng lượng và phối hợp cầu chì. |
| D7 | BZX55C12 / BZX55C12 | FIT | Zener bảo vệ gate-source Q1 | 1=+12V; 2=Q1_GATE | Kiểm cực và biên VGS của MOSFET. |
| F2 | MF-R300 / MF-R300 | FIT | PTC riêng từng rail servo | 1=+6V_A_RAW; 2=+6V_A | Dòng giữ/tác động phụ thuộc nhiệt; thử giữ tải, khởi động, kẹt và điện trở gây sụt áp. |
| F3 | MF-R300 / MF-R300 | FIT | PTC riêng từng rail servo | 1=+6V_B_RAW; 2=+6V_B | Dòng giữ/tác động phụ thuộc nhiệt; thử giữ tải, khởi động, kẹt và điện trở gây sụt áp. |
| C1 | 2200uF 16V / EEUFR1C222 | FIT | Tụ bulk 2200 µF cho servo | 1=+6V_A; 2=GND | Kiểm cực, ripple/ESR, kích thước thật; không thay được nguồn đủ dòng hoặc bảo vệ xung hồi. |
| C3 | 100nF / K104K15X7RF53H5 | FIT | Bypass cao tần rail servo | 1=+6V_A; 2=GND | Kiểm đường hồi ngắn; đo nhiễu khi servo đổi tải. |
| C2 | 2200uF 16V / EEUFR1C222 | FIT | Tụ bulk 2200 µF cho servo | 1=+6V_B; 2=GND | Kiểm cực, ripple/ESR, kích thước thật; không thay được nguồn đủ dòng hoặc bảo vệ xung hồi. |
| C4 | 100nF / K104K15X7RF53H5 | FIT | Bypass cao tần rail servo | 1=+6V_B; 2=GND | Kiểm đường hồi ngắn; đo nhiễu khi servo đổi tải. |
| J4 | 5V D24V25F5 / Pololu 2850 D24V25F5 + 1x05 female socket | FIT | Socket buck logic Pololu D24V25F5 | 2=+12V; 3=GND; 4=GND; 5=+5V | Ảnh không hiện module; phải lắp buck thật, xác nhận pinout/khoảng trống/khả năng tản nhiệt. |
| C5 | 10uF 50V / EEUFR1H100 | FIT | Tụ bulk rail 5 V | 1=+5V; 2=GND | Kiểm cực và sụt áp tải logic. |
| C6 | 100nF / K104K15X7RF53H5 | FIT | Bypass 3,3 V | 1=+3V3; 2=GND | Kết nối là 3,3 V dù vị trí gần khối nguồn vào; đọc net thay vì suy từ vị trí. |
| J5 | S1_TOP / M20-9990346 | FIT | Cổng servo GND/6 V/PWM | 1=GND; 2=+6V_A; 3=S1_TOP_PWM | Header không có khóa giữ; thử rung/rút dây và dòng tiếp điểm; kiểm thứ tự dây servo thật. |
| R1 | 330R / CFR-25JR-52-330R | FIT | Điện trở nối tiếp PWM | 1=ESP_S1_TOP_PWM; 2=S1_TOP_PWM | Giảm dòng xung/tác động đường dây; không phải cách ly hoặc bảo vệ ESD đầy đủ. |
| R5 | 10k / CFR-25JR-52-10K | FIT | Kéo xuống PWM 10 kΩ | 1=S1_TOP_PWM; 2=GND | Giữ mức thấp lúc MCU chưa điều khiển; vẫn thử servo lúc boot/reset/mất logic. |
| J6 | S1_BOT / M20-9990346 | FIT | Cổng servo GND/6 V/PWM | 1=GND; 2=+6V_A; 3=S1_BOT_PWM | Header không có khóa giữ; thử rung/rút dây và dòng tiếp điểm; kiểm thứ tự dây servo thật. |
| R2 | 330R / CFR-25JR-52-330R | FIT | Điện trở nối tiếp PWM | 1=ESP_S1_BOT_PWM; 2=S1_BOT_PWM | Giảm dòng xung/tác động đường dây; không phải cách ly hoặc bảo vệ ESD đầy đủ. |
| R6 | 10k / CFR-25JR-52-10K | FIT | Kéo xuống PWM 10 kΩ | 1=S1_BOT_PWM; 2=GND | Giữ mức thấp lúc MCU chưa điều khiển; vẫn thử servo lúc boot/reset/mất logic. |
| J7 | S2_TOP / M20-9990346 | FIT | Cổng servo GND/6 V/PWM | 1=GND; 2=+6V_B; 3=S2_TOP_PWM | Header không có khóa giữ; thử rung/rút dây và dòng tiếp điểm; kiểm thứ tự dây servo thật. |
| R3 | 330R / CFR-25JR-52-330R | FIT | Điện trở nối tiếp PWM | 1=ESP_S2_TOP_PWM; 2=S2_TOP_PWM | Giảm dòng xung/tác động đường dây; không phải cách ly hoặc bảo vệ ESD đầy đủ. |
| R7 | 10k / CFR-25JR-52-10K | FIT | Kéo xuống PWM 10 kΩ | 1=S2_TOP_PWM; 2=GND | Giữ mức thấp lúc MCU chưa điều khiển; vẫn thử servo lúc boot/reset/mất logic. |
| J8 | S2_BOT / M20-9990346 | FIT | Cổng servo GND/6 V/PWM | 1=GND; 2=+6V_B; 3=S2_BOT_PWM | Header không có khóa giữ; thử rung/rút dây và dòng tiếp điểm; kiểm thứ tự dây servo thật. |
| R4 | 330R / CFR-25JR-52-330R | FIT | Điện trở nối tiếp PWM | 1=ESP_S2_BOT_PWM; 2=S2_BOT_PWM | Giảm dòng xung/tác động đường dây; không phải cách ly hoặc bảo vệ ESD đầy đủ. |
| R8 | 10k / CFR-25JR-52-10K | FIT | Kéo xuống PWM 10 kΩ | 1=S2_BOT_PWM; 2=GND | Giữ mức thấp lúc MCU chưa điều khiển; vẫn thử servo lúc boot/reset/mất logic. |
| J9 | IR RX1 3V3/OUT/G / B3B-XH-A + XHP-3 + SXH-001T-P0.6 | FIT | Cổng receiver IR 3,3 V/OUT/GND | 1=+3V3; 2=IR_RX1_CABLE; 3=GND | Receiver nằm board ngoài; kiểm dây dưới 1 m, nguồn và nhiễu. |
| R26 | 10k / CFR-25JR-52-10K | FIT | Kéo lên tín hiệu IR RX 10 kΩ | 1=IR_RX1; 2=+3V3 | Kiểm mức logic và dạng sóng thực tế tại GPIO34/35. |
| R28 | 1k / CFR-25JR-52-1K | FIT | Điện trở nối tiếp IR RX 1 kΩ | 1=IR_RX1_CABLE; 2=IR_RX1 | Giới hạn dòng nhiễu; chưa chứng minh ESD/đấu nhầm hoặc cấp ngược qua GPIO được bảo vệ. |
| J10 | IR RX2 3V3/OUT/G / B3B-XH-A + XHP-3 + SXH-001T-P0.6 | FIT | Cổng receiver IR 3,3 V/OUT/GND | 1=+3V3; 2=IR_RX2_CABLE; 3=GND | Receiver nằm board ngoài; kiểm dây dưới 1 m, nguồn và nhiễu. |
| R27 | 10k / CFR-25JR-52-10K | FIT | Kéo lên tín hiệu IR RX 10 kΩ | 1=IR_RX2; 2=+3V3 | Kiểm mức logic và dạng sóng thực tế tại GPIO34/35. |
| R29 | 1k / CFR-25JR-52-1K | FIT | Điện trở nối tiếp IR RX 1 kΩ | 1=IR_RX2_CABLE; 2=IR_RX2 | Giới hạn dòng nhiễu; chưa chứng minh ESD/đấu nhầm hoặc cấp ngược qua GPIO được bảo vệ. |
| J11 | IR TX1 A/K / B2B-XH-A + XHP-2 + SXH-001T-P0.6 | FIT | Cổng LED IR phát A/K | 1=IR_TX1_A; 2=IR_TX_RET | LED nằm ngoài mainboard; kiểm cực và dòng xung. |
| R14 | 120R / CFR-25JR-52-120R | FIT | Hạn dòng từng LED IR 120 Ω | 1=+5V; 2=IR_TX1_A | Tính theo VF LED thật và VCE Q2; phát burst 38 kHz, thử tầm nhận. |
| J12 | IR TX2 A/K / B2B-XH-A + XHP-2 + SXH-001T-P0.6 | FIT | Cổng LED IR phát A/K | 1=IR_TX2_A; 2=IR_TX_RET | LED nằm ngoài mainboard; kiểm cực và dòng xung. |
| R15 | 120R / CFR-25JR-52-120R | FIT | Hạn dòng từng LED IR 120 Ω | 1=+5V; 2=IR_TX2_A | Tính theo VF LED thật và VCE Q2; phát burst 38 kHz, thử tầm nhận. |
| R13 | 330R / CFR-25JR-52-330R | FIT | Hạn dòng base Q2 | 1=ESP_IR_TX; 2=Q2_BASE | Kiểm dòng GPIO và Q2 bão hòa với hai nhánh LED. |
| R25 | 10k / CFR-25JR-52-10K | FIT | Kéo base Q2 xuống | 1=Q2_BASE; 2=GND | Tránh phát IR khi GPIO đang thả nổi. |
| Q2 | P2N2222AG / P2N2222AG | FIT | Transistor NPN đóng cắt LED IR | C=IR_TX_RET; B=Q2_BASE; E=GND | Kiểm đúng pinout P2N2222AG; không thay mọi 2N2222 cùng hình dạng mà bỏ kiểm chân. |
| J13 | LS1 DNP / B2B-XH-A + XHP-2 + SXH-001T-P0.6 | DNP | Cổng limit switch tùy chọn | 1=LS1; 2=GND | DNP: không lắp mặc định; ảnh 3D không quyết định population. |
| R16 | 10k / CFR-25JR-52-10K | DNP | Pull-up limit switch | 1=LS1; 2=+3V3 | DNP; nếu lắp kiểm debounce và hành vi đứt dây. |
| C7 | 100nF / K104K15X7RF53H5 | DNP | Tụ lọc limit switch | 1=LS1; 2=GND | DNP; với 10 kΩ và 100 nF, RC danh định 1 ms, không thay debounce firmware. |
| J14 | LS2 DNP / B2B-XH-A + XHP-2 + SXH-001T-P0.6 | DNP | Cổng limit switch tùy chọn | 1=LS2; 2=GND | DNP: không lắp mặc định; ảnh 3D không quyết định population. |
| R17 | 10k / CFR-25JR-52-10K | DNP | Pull-up limit switch | 1=LS2; 2=+3V3 | DNP; nếu lắp kiểm debounce và hành vi đứt dây. |
| C8 | 100nF / K104K15X7RF53H5 | DNP | Tụ lọc limit switch | 1=LS2; 2=GND | DNP; với 10 kΩ và 100 nF, RC danh định 1 ms, không thay debounce firmware. |
| J15 | LS3 DNP / B2B-XH-A + XHP-2 + SXH-001T-P0.6 | DNP | Cổng limit switch tùy chọn | 1=LS3; 2=GND | DNP: không lắp mặc định; ảnh 3D không quyết định population. |
| R18 | 10k / CFR-25JR-52-10K | DNP | Pull-up limit switch | 1=LS3; 2=+3V3 | DNP; nếu lắp kiểm debounce và hành vi đứt dây. |
| C9 | 100nF / K104K15X7RF53H5 | DNP | Tụ lọc limit switch | 1=LS3; 2=GND | DNP; với 10 kΩ và 100 nF, RC danh định 1 ms, không thay debounce firmware. |
| J16 | LS4 DNP / B2B-XH-A + XHP-2 + SXH-001T-P0.6 | DNP | Cổng limit switch tùy chọn | 1=LS4; 2=GND | DNP: không lắp mặc định; ảnh 3D không quyết định population. |
| R19 | 10k / CFR-25JR-52-10K | DNP | Pull-up limit switch | 1=LS4; 2=+3V3 | DNP; nếu lắp kiểm debounce và hành vi đứt dây. |
| C10 | 100nF / K104K15X7RF53H5 | DNP | Tụ lọc limit switch | 1=LS4; 2=GND | DNP; với 10 kΩ và 100 nF, RC danh định 1 ms, không thay debounce firmware. |
| J17 | I2C 3V3/SDA/SCL/G / M20-9990446 | FIT | Cổng mở rộng I²C 3,3 V | 1=+3V3; 2=I2C_SDA; 3=I2C_SCL; 4=GND | Không có pull-up SDA/SCL chuyên dụng trong BOM này; ngoại vi phải có hoặc cần thiết kế bổ sung khi sử dụng. |
| R20 | 5.6k / CFR-25JR-52-5K6 | FIT | Hạn dòng LED nguồn tương ứng 12/6A/6B/5/3,3 V | 1=+12V; 2=LED2_A | Kiểm dòng theo VF; LED sáng không chứng minh nguồn đủ tải. |
| D2 | +12V / WP710A10GD | FIT | LED báo nguồn tương ứng 12/6A/6B/5/3,3 V | 1=GND; 2=LED2_A | Model 3D đỏ không chứng minh màu thực của MPN; kiểm cực. |
| R21 | 2.2k / CFR-25JR-52-2K2 | FIT | Hạn dòng LED nguồn tương ứng 12/6A/6B/5/3,3 V | 1=+6V_A; 2=LED3_A | Kiểm dòng theo VF; LED sáng không chứng minh nguồn đủ tải. |
| D3 | +6V_A / WP710A10GD | FIT | LED báo nguồn tương ứng 12/6A/6B/5/3,3 V | 1=GND; 2=LED3_A | Model 3D đỏ không chứng minh màu thực của MPN; kiểm cực. |
| R22 | 2.2k / CFR-25JR-52-2K2 | FIT | Hạn dòng LED nguồn tương ứng 12/6A/6B/5/3,3 V | 1=+6V_B; 2=LED4_A | Kiểm dòng theo VF; LED sáng không chứng minh nguồn đủ tải. |
| D4 | +6V_B / WP710A10GD | FIT | LED báo nguồn tương ứng 12/6A/6B/5/3,3 V | 1=GND; 2=LED4_A | Model 3D đỏ không chứng minh màu thực của MPN; kiểm cực. |
| R23 | 1.5k / CFR-25JR-52-1K5 | FIT | Hạn dòng LED nguồn tương ứng 12/6A/6B/5/3,3 V | 1=+5V; 2=LED5_A | Kiểm dòng theo VF; LED sáng không chứng minh nguồn đủ tải. |
| D5 | +5V / WP710A10GD | FIT | LED báo nguồn tương ứng 12/6A/6B/5/3,3 V | 1=GND; 2=LED5_A | Model 3D đỏ không chứng minh màu thực của MPN; kiểm cực. |
| R24 | 1k / CFR-25JR-52-1K | FIT | Hạn dòng LED nguồn tương ứng 12/6A/6B/5/3,3 V | 1=+3V3; 2=LED6_A | Kiểm dòng theo VF; LED sáng không chứng minh nguồn đủ tải. |
| D6 | +3V3 / WP710A10GD | FIT | LED báo nguồn tương ứng 12/6A/6B/5/3,3 V | 1=GND; 2=LED6_A | Model 3D đỏ không chứng minh màu thực của MPN; kiểm cực. |
| TP1 | +12V / 5000 | FIT | Test point tương ứng 12/6A/6B/5/3,3 V | 1=+12V | Dùng đồng hồ và scope; không chỉ đo khi không tải. |
| TP2 | +6V_A / 5000 | FIT | Test point tương ứng 12/6A/6B/5/3,3 V | 1=+6V_A | Dùng đồng hồ và scope; không chỉ đo khi không tải. |
| TP3 | +6V_B / 5000 | FIT | Test point tương ứng 12/6A/6B/5/3,3 V | 1=+6V_B | Dùng đồng hồ và scope; không chỉ đo khi không tải. |
| TP4 | +5V / 5000 | FIT | Test point tương ứng 12/6A/6B/5/3,3 V | 1=+5V | Dùng đồng hồ và scope; không chỉ đo khi không tải. |
| TP5 | +3V3 / 5000 | FIT | Test point tương ứng 12/6A/6B/5/3,3 V | 1=+3V3 | Dùng đồng hồ và scope; không chỉ đo khi không tải. |
| TP6 | GND / 5001 | FIT | Test point GND | 1=GND | Kiểm điểm tham chiếu khi đo; ground spring gần IC cho xung nhanh. |
| TP7 | GND / 5001 | FIT | Test point GND | 1=GND | Kiểm điểm tham chiếu khi đo; ground spring gần IC cho xung nhanh. |
| TP8 | SPARE_GPIO33 / 5000 | FIT | Test point GPIO33 dự phòng | 1=SPARE_GPIO33 | Không đấu 5/6/12 V; chưa phải cổng tải công suất. |
| H1 | M3 MOUNT / M3 nylon spacer/screw set, enclosure dependent | FIT | Lỗ gá M3 |  | Kiểm spacer, vít và khoảng hở với hộp/đồng/linh kiện. |
| H2 | M3 MOUNT / M3 nylon spacer/screw set, enclosure dependent | FIT | Lỗ gá M3 |  | Kiểm spacer, vít và khoảng hở với hộp/đồng/linh kiện. |
| H3 | M3 MOUNT / M3 nylon spacer/screw set, enclosure dependent | FIT | Lỗ gá M3 |  | Kiểm spacer, vít và khoảng hở với hộp/đồng/linh kiện. |
| H4 | M3 MOUNT / M3 nylon spacer/screw set, enclosure dependent | FIT | Lỗ gá M3 |  | Kiểm spacer, vít và khoảng hở với hộp/đồng/linh kiện. |
| U1 | ESP32-D0WD-V3 / ESP32-D0WD-V3 | FIT | ESP32-D0WD-V3 QFN48 rời | 1=+3V3; 2=RF_CHIP; 3=+3V3_RF; 4=+3V3_RF; 9=ESP_EN; 10=IR_RX1; 11=IR_RX2; 12=LS4; 13=SPARE_GPIO33; 14=LS1; 15=LS2; 16=LS3; 18=STRAP_GPIO12; 19=+3V3; 21=STRAP_GPIO15; 22=STRAP_GPIO2; 23=ESP_BOOT; 25=ESP_S1_TOP_PWM; 26=VDD_SDIO; 27=ESP_S1_BOT_PWM; 28=SPI_HD; 29=SPI_WP; 30=SPI_CS; 31=SPI_CLK; 32=SPI_Q; 33=SPI_D; 34=STRAP_GPIO5; 35=ESP_S2_TOP_PWM; 36=ESP_IR_TX; 37=+3V3; 38=ESP_S2_BOT_PWM; 39=I2C_SCL; 40=UART_RX; 41=UART_TX_RAW; 42=I2C_SDA; 43=+3V3; 44=XTAL_N; 45=XTAL_P; 46=+3V3; 47=CAP2; 48=CAP1; 49=GND | Ảnh thiếu model thân IC; footprint có mặt. Kiểm EP/stencil/X-ray, boot, Wi-Fi và nhiệt; chưa nghiệm thu production. |
| U3 | LD1117V33 / LD1117V33 | FIT | LDO LD1117V33 từ 5 V xuống 3,3 V | 1=GND; 2=+3V3; 3=+5V | Tổn hao (5−3,3)×I; kiểm ổn định với tụ thực và nhiệt trong hộp. |
| U4 | W25Q32JVSSIQ / W25Q32JVSSIQ | FIT | Flash W25Q32JVSSIQ 4 MB | 1=FLASH_CS; 2=FLASH_Q; 3=FLASH_WP; 4=GND; 5=FLASH_D; 6=FLASH_CLK; 7=FLASH_HD; 8=VDD_SDIO | Nguồn VDD_SDIO: đo lúc đọc/ghi và brownout; thử QE/chế độ bus/tần số firmware. |
| R40 | 0R / RC0402JR-070RL | FIT | Điện trở nối tiếp bus flash 0 Ω | 1=SPI_CS; 2=FLASH_CS | Footprint chỉnh SI; 0 Ω chưa chứng minh ringing/timing đạt; kiểm clock và đọc/ghi. |
| R41 | 0R / RC0402JR-070RL | FIT | Điện trở nối tiếp bus flash 0 Ω | 1=SPI_CLK; 2=FLASH_CLK | Footprint chỉnh SI; 0 Ω chưa chứng minh ringing/timing đạt; kiểm clock và đọc/ghi. |
| R42 | 0R / RC0402JR-070RL | FIT | Điện trở nối tiếp bus flash 0 Ω | 1=SPI_Q; 2=FLASH_Q | Footprint chỉnh SI; 0 Ω chưa chứng minh ringing/timing đạt; kiểm clock và đọc/ghi. |
| R43 | 0R / RC0402JR-070RL | FIT | Điện trở nối tiếp bus flash 0 Ω | 1=SPI_D; 2=FLASH_D | Footprint chỉnh SI; 0 Ω chưa chứng minh ringing/timing đạt; kiểm clock và đọc/ghi. |
| R44 | 0R / RC0402JR-070RL | FIT | Điện trở nối tiếp bus flash 0 Ω | 1=SPI_WP; 2=FLASH_WP | Footprint chỉnh SI; 0 Ω chưa chứng minh ringing/timing đạt; kiểm clock và đọc/ghi. |
| R45 | 0R / RC0402JR-070RL | FIT | Điện trở nối tiếp bus flash 0 Ω | 1=SPI_HD; 2=FLASH_HD | Footprint chỉnh SI; 0 Ω chưa chứng minh ringing/timing đạt; kiểm clock và đọc/ghi. |
| R47 | 10k / RC0402FR-0710KL | FIT | Pull-up CS/WP/HD flash | 1=FLASH_CS; 2=VDD_SDIO | Kéo lên VDD_SDIO; kiểm trạng thái boot. |
| R48 | 10k / RC0402FR-0710KL | FIT | Pull-up CS/WP/HD flash | 1=FLASH_WP; 2=VDD_SDIO | Kéo lên VDD_SDIO; kiểm trạng thái boot. |
| R49 | 10k / RC0402FR-0710KL | FIT | Pull-up CS/WP/HD flash | 1=FLASH_HD; 2=VDD_SDIO | Kéo lên VDD_SDIO; kiểm trạng thái boot. |
| C40 | 1uF / GRM155R61A105KE15D | FIT | Decoupling nguồn flash VDD_SDIO | 1=VDD_SDIO; 2=GND | Đo sụt áp tại U4, chú ý đường cấp qua ESP32. |
| C41 | 100nF / GRM155R71C104KA88D | FIT | Decoupling nguồn flash VDD_SDIO | 1=VDD_SDIO; 2=GND | Đo sụt áp tại U4, chú ý đường cấp qua ESP32. |
| R30 | 10k / RC0402FR-0710KL | FIT | Pull-up EN | 1=ESP_EN; 2=+3V3 | Phối hợp C20 và supervisor; thử nguồn tăng chậm/mất nguồn ngắn. |
| R31 | 10k / RC0402FR-0710KL | FIT | Pull-up BOOT GPIO0 | 1=ESP_BOOT; 2=+3V3 | Nút BOOT/auto-download phải kéo thấp đúng thời điểm. |
| R34 | 10k / RC0402FR-0710KL | FIT | Pull-up GPIO5/GPIO15 | 1=STRAP_GPIO5; 2=+3V3 | Kiểm strap lúc reset; không để ngoại vi ép sai mức. |
| R35 | 10k / RC0402FR-0710KL | FIT | Pull-up GPIO5/GPIO15 | 1=STRAP_GPIO15; 2=+3V3 | Kiểm strap lúc reset; không để ngoại vi ép sai mức. |
| R32 | 10k / RC0402FR-0710KL | FIT | Pull-down GPIO2/GPIO12 | 1=STRAP_GPIO2; 2=GND | Strapping; GPIO12 thấp chọn nguồn flash 3,3 V theo cấu hình mặc định; kiểm eFuse. |
| R33 | 10k / RC0402FR-0710KL | FIT | Pull-down GPIO2/GPIO12 | 1=STRAP_GPIO12; 2=GND | Strapping; GPIO12 thấp chọn nguồn flash 3,3 V theo cấu hình mặc định; kiểm eFuse. |
| C20 | 1uF / GRM155R61A105KE15D | FIT | Tụ EN 1 µF | 1=ESP_EN; 2=GND | Phối hợp R30 và U5; kiểm auto-reset/nạp thực. |
| U5 | TLV803EA30DBZR / TLV803EA30DBZR | FIT | Supervisor TLV803EA30DBZR | 1=GND; 2=ESP_EN; 3=+3V3 | Ngưỡng danh định 3,08 V, delay 200 ms, open-drain; đúng biến thể pin1 GND; đo brownout flash. |
| C56 | 100nF / GRM155R71C104KA88D | FIT | Bypass supervisor | 1=+3V3; 2=GND | Đặt/đường hồi gần U5; kiểm nguồn nhiễu. |
| C11 | 10uF 50V / EEUFR1H100 | FIT | Tụ điện phân ngõ vào/ngõ ra LDO | 1=+5V; 2=GND | Kiểm cực, điện dung/ESR và ổn định; 50 V là rating tụ, không phải điện áp rail. |
| C12 | 10uF 50V / EEUFR1H100 | FIT | Tụ điện phân ngõ vào/ngõ ra LDO | 1=+3V3; 2=GND | Kiểm cực, điện dung/ESR và ổn định; 50 V là rating tụ, không phải điện áp rail. |
| C13 | 10uF / GRM188R60J106ME47D | FIT | Tụ bulk gốm 10 µF cho MCU/RF | 1=+3V3; 2=GND | Kiểm điện dung hiệu dụng dưới DC bias và đáp ứng tải. |
| C14 | 10uF / GRM188R60J106ME47D | FIT | Tụ bulk gốm 10 µF cho MCU/RF | 1=+3V3_RF; 2=GND | Kiểm điện dung hiệu dụng dưới DC bias và đáp ứng tải. |
| C15 | 10uF / GRM188R60J106ME47D | FIT | Tụ bulk gốm 10 µF cho MCU/RF | 1=+3V3_RF; 2=GND | Kiểm điện dung hiệu dụng dưới DC bias và đáp ứng tải. |
| C16 | 100nF / GRM155R71C104KA88D | FIT | Bypass nguồn ESP32 | 1=+3V3; 2=GND | Kiểm vòng dòng chân nguồn–tụ–GND; C23 loại 0201 khó sửa tay. |
| C17 | 100nF / GRM155R71C104KA88D | FIT | Bypass nguồn ESP32 | 1=+3V3; 2=GND | Kiểm vòng dòng chân nguồn–tụ–GND; C23 loại 0201 khó sửa tay. |
| C18 | 100nF / GRM155R71C104KA88D | FIT | Bypass nguồn ESP32 | 1=+3V3; 2=GND | Kiểm vòng dòng chân nguồn–tụ–GND; C23 loại 0201 khó sửa tay. |
| C19 | 100nF / GRM155R71C104KA88D | FIT | Bypass nguồn ESP32 | 1=+3V3; 2=GND | Kiểm vòng dòng chân nguồn–tụ–GND; C23 loại 0201 khó sửa tay. |
| C23 | 100nF / GRM033R71C104KE14D | FIT | Bypass nguồn ESP32 | 1=+3V3; 2=GND | Kiểm vòng dòng chân nguồn–tụ–GND; C23 loại 0201 khó sửa tay. |
| C21 | 1uF / GRM155R61A105KE15D | FIT | Bypass nhánh nguồn RF | 1=+3V3_RF; 2=GND | Đường hồi và vị trí quan trọng; C22 loại 0201. |
| C22 | 100nF / GRM033R71C104KE14D | FIT | Bypass nhánh nguồn RF | 1=+3V3_RF; 2=GND | Đường hồi và vị trí quan trọng; C22 loại 0201. |
| L2 | 2.0nH / LQP03TN2N0B02D | FIT | Cuộn cảm 2 nH nhánh cấp RF | 1=+3V3; 2=+3V3_RF | Không phải choke nguồn lớn; kiểm đặc tính cao tần, dòng và mạng LC thực. |
| Y1 | 40MHz CL10pF / ABM8-40.000MHZ-10-1-U-T | FIT | Thạch anh 40 MHz CL 10 pF | 1=XTAL_P_X; 2=GND; 3=XTAL_N; 4=GND | MPN chọn có dải −10…60 °C theo hồ sơ; xác nhận phù hợp hộp; đo tần số/khởi động. |
| R36 | 0R / RC0402JR-070RL | FIT | Điện trở nối tiếp clock 0 Ω | 1=XTAL_P; 2=XTAL_P_X | Footprint tuning; không đổi tùy tiện. |
| C24 | 16pF / GRM1555C1H160JA01D | FIT | Tụ tải crystal 16 pF | 1=XTAL_P_X; 2=GND | Giá trị ban đầu với giả định ký sinh; cần đo chỉnh, không coi là đã hiệu chuẩn. |
| C25 | 16pF / GRM1555C1H160JA01D | FIT | Tụ tải crystal 16 pF | 1=XTAL_N; 2=GND | Giá trị ban đầu với giả định ký sinh; cần đo chỉnh, không coi là đã hiệu chuẩn. |
| C26 | 10nF / GRM155R71C103KA01D | FIT | Mạng CAP1/CAP2 theo ESP32 | 1=CAP1; 2=GND | Không phải tụ lọc tùy ý; giữ đúng kết nối/giá trị và đối chiếu datasheet. |
| C27 | 3.3nF / GRM155R71H332KA01D | FIT | Mạng CAP1/CAP2 theo ESP32 | 1=CAP2; 2=CAP1 | Không phải tụ lọc tùy ý; giữ đúng kết nối/giá trị và đối chiếu datasheet. |
| R37 | 20k / RC0402FR-0720KL | FIT | Mạng CAP1/CAP2 theo ESP32 | 1=CAP2; 2=CAP1 | Không phải tụ lọc tùy ý; giữ đúng kết nối/giá trị và đối chiếu datasheet. |
| C30 | 1.5pF / GRM0335C1H1R5BA01D | FIT | Matching RF 1,5 pF / 2,7 nH / 0,5 pF | 1=RF_CHIP; 2=GND | Giá trị ban đầu; cần stackup, đường hồi và đo RF; C31 phải tính cả D8/ký sinh. |
| L1 | 2.7nH / LQP03TN2N7B02D | FIT | Matching RF 1,5 pF / 2,7 nH / 0,5 pF | 1=RF_CHIP; 2=RF_50 | Giá trị ban đầu; cần stackup, đường hồi và đo RF; C31 phải tính cả D8/ký sinh. |
| C31 | 0.5pF / GRM0335C1HR50BA01D | FIT | Matching RF 1,5 pF / 2,7 nH / 0,5 pF | 1=RF_50; 2=GND | Giá trị ban đầu; cần stackup, đường hồi và đo RF; C31 phải tính cả D8/ký sinh. |
| J20 | SMA 50ohm ANT / Amphenol 132134 | FIT | SMA anten ngoài | 1=RF_50; 2=GND | Ảnh chỉ có lỗ/pad do thiếu model; cần connector và anten đúng SMA, không nhầm RP-SMA; kiểm cơ khí. |
| D8 | PESD5V0X1BL / PESD5V0X1BL,315 | FIT | ESD cho đường RF | 1=RF_50; 2=GND | Điện dung ảnh hưởng matching; chưa thử ESD hệ thống. |
| U2 | CP2102N-A02-GQFN24 / CP2102N-A02-GQFN24 | FIT | CP2102N USB-UART | 2=GND; 3=USB_DP; 4=USB_DM; 5=+3V3; 6=+3V3; 7=+3V3; 8=USB_VBUS_SENSE; 9=USB_RESET; 19=USB_RTS; 20=UART_TX; 21=UART_RX; 23=USB_DTR; 25=GND | Self-powered 3,3 V; kiểm enumeration, UART và trạng thái USB khi main tắt; EP cần DFM. |
| J21 | USB MICRO DATA / Molex 105017-0001 | FIT | Micro-USB dữ liệu | 1=USB_VBUS; 2=USB_DM; 3=USB_DP; 5=GND; SH=GND | Ảnh thiếu model thân cổng; USB không cấp nguồn board; kiểm lực cơ khí và khả năng tiếp cận trong hộp. |
| R50 | 22.1k / RC0402FR-0722K1L | FIT | Chia áp USB VBUS sense | 1=USB_VBUS; 2=USB_VBUS_SENSE | 22,1 kΩ/47,5 kΩ: 5 V tạo khoảng 3,41 V; đối chiếu giới hạn và hot-plug/cấp nguồn từng phần. |
| R51 | 47.5k / RC0402FR-0747K5L | FIT | Chia áp USB VBUS sense | 1=USB_VBUS_SENSE; 2=GND | 22,1 kΩ/47,5 kΩ: 5 V tạo khoảng 3,41 V; đối chiếu giới hạn và hot-plug/cấp nguồn từng phần. |
| R52 | 1k / RC0402FR-071KL | FIT | Pull-up reset USB-UART 1 kΩ | 1=USB_RESET; 2=+3V3 | Kiểm mức reset của U2 trong mọi chế độ nguồn. |
| R53 | 499R / RC0402FR-07499RL | FIT | Điện trở nối tiếp TX ESP32 499 Ω | 1=UART_TX_RAW; 2=UART_TX | Kiểm cạnh/timing UART ở baud thực và với tải đo. |
| C50 | 4.7uF / GRM155R60J475ME87D | FIT | Tụ bulk/bypass CP2102N | 1=+3V3; 2=GND | Tụ 4,7 µF và 100 nF; kiểm hiệu dụng DC bias, đường hồi và nguồn khi cắm/rút USB. |
| C51 | 4.7uF / GRM155R60J475ME87D | FIT | Tụ bulk/bypass CP2102N | 1=+3V3; 2=GND | Tụ 4,7 µF và 100 nF; kiểm hiệu dụng DC bias, đường hồi và nguồn khi cắm/rút USB. |
| C52 | 4.7uF / GRM155R60J475ME87D | FIT | Tụ bulk/bypass CP2102N | 1=+3V3; 2=GND | Tụ 4,7 µF và 100 nF; kiểm hiệu dụng DC bias, đường hồi và nguồn khi cắm/rút USB. |
| C53 | 100nF / GRM155R71C104KA88D | FIT | Tụ bulk/bypass CP2102N | 1=+3V3; 2=GND | Tụ 4,7 µF và 100 nF; kiểm hiệu dụng DC bias, đường hồi và nguồn khi cắm/rút USB. |
| C54 | 100nF / GRM155R71C104KA88D | FIT | Tụ bulk/bypass CP2102N | 1=+3V3; 2=GND | Tụ 4,7 µF và 100 nF; kiểm hiệu dụng DC bias, đường hồi và nguồn khi cắm/rút USB. |
| C55 | 100nF / GRM155R71C104KA88D | FIT | Tụ bulk/bypass CP2102N | 1=+3V3; 2=GND | Tụ 4,7 µF và 100 nF; kiểm hiệu dụng DC bias, đường hồi và nguồn khi cắm/rút USB. |
| D9 | PESD5V0X1BL / PESD5V0X1BL,315 | FIT | ESD USB D+/D− | 1=USB_DP; 2=GND | Đặt gần cổng; kiểm USB signal integrity và ESD thực. |
| D10 | PESD5V0X1BL / PESD5V0X1BL,315 | FIT | ESD USB D+/D− | 1=USB_DM; 2=GND | Đặt gần cổng; kiểm USB signal integrity và ESD thực. |
| Q3 | MMBT3904 / MMBT3904LT1G | FIT | Transistor auto-download | 1=AUTO_EN_BASE; 2=USB_RTS; 3=ESP_EN | Kiểm bảng trạng thái DTR/RTS, reset và thao tác nạp; nút thủ công làm phương án phục hồi. |
| Q4 | MMBT3904 / MMBT3904LT1G | FIT | Transistor auto-download | 1=AUTO_BOOT_BASE; 2=USB_DTR; 3=ESP_BOOT | Kiểm bảng trạng thái DTR/RTS, reset và thao tác nạp; nút thủ công làm phương án phục hồi. |
| R54 | 10k / RC0402FR-0710KL | FIT | Hạn dòng base auto-download 10 kΩ | 1=USB_DTR; 2=AUTO_EN_BASE | Kiểm phối hợp với transistor và mức DTR/RTS. |
| R55 | 10k / RC0402FR-0710KL | FIT | Hạn dòng base auto-download 10 kΩ | 1=USB_RTS; 2=AUTO_BOOT_BASE | Kiểm phối hợp với transistor và mức DTR/RTS. |
| SW1 | RESET / Omron B3F-1000 | FIT | Nút RESET và BOOT | 1=ESP_EN; 2=GND | Kiểm thao tác và khoảng trống hộp; giữ BOOT/reset đúng trình tự khi phục hồi. |
| SW2 | BOOT / Omron B3F-1000 | FIT | Nút RESET và BOOT | 1=ESP_BOOT; 2=GND | Kiểm thao tác và khoảng trống hộp; giữ BOOT/reset đúng trình tự khi phục hồi. |
| TP9 | ESP_EN / Keystone 5000 | FIT | Test point EN/BOOT/UART TX/UART RX | 1=ESP_EN | Đối chiếu nhãn với net; log boot và đo timing reset/UART. |
| TP10 | ESP_BOOT / Keystone 5000 | FIT | Test point EN/BOOT/UART TX/UART RX | 1=ESP_BOOT | Đối chiếu nhãn với net; log boot và đo timing reset/UART. |
| TP11 | UART_TX / Keystone 5000 | FIT | Test point EN/BOOT/UART TX/UART RX | 1=UART_TX | Đối chiếu nhãn với net; log boot và đo timing reset/UART. |
| TP12 | UART_RX / Keystone 5000 | FIT | Test point EN/BOOT/UART TX/UART RX | 1=UART_RX | Đối chiếu nhãn với net; log boot và đo timing reset/UART. |

## Nguồn hãng đã đọc lại trong lượt review

- Espressif datasheet: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf
- Espressif schematic: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html
- Espressif layout: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html
- ST LD1117: https://www.st.com/resource/en/datasheet/ld1117.pdf
- Silicon Labs CP2102N: https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf
- TI TLV803E: https://www.ti.com/lit/ds/symlink/tlv803e.pdf

Các Source khác có trong docs/revb/bom/FV-CTRL_RevB-bom-review.csv; cần kiểm drawing/datasheet từng MPN và mẫu nhận được trước sản xuất. Không xuất Gerber hoặc thay đổi thiết kế trong lượt này.
