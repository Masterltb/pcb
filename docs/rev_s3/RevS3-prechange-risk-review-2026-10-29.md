# Rev-S3 — review trước khi sửa nguồn và parity (2026-10-29)

## Phạm vi và bản dự phòng

- Nguồn thiết kế: `hardware/rev_s3/`. Không sửa RevA, RevA2 hoặc RevB.
- Snapshot trước thay đổi: `backups/rev_s3_pre_power_review_2026-10-29.zip` (bao gồm hardware, docs và release Rev-S3 hiện có). Git HEAD lúc tạo: `da9bebe`.
- Các đầu ra `releases/rev_s3/` hiện có chỉ là gói cũ; chưa phát hành lại sau review.

## Góc IC / SI / PI

- ESP32-S3-WROOM-1U thay cho ESP32 rời của RevB; cần soát pinout, reset/boot, 3,3 V và khoảng trống anten/cáp IPEX theo tài liệu hãng và mẫu thực.
- PCB 1 oz có các đường +12V, +6V_A và +6V_B chủ yếu 0,5 mm; +6V_A có nhánh 0,2 mm dài khoảng 56 mm đi tới TP2/LED/C1. Mỗi rail servo có thể chịu dòng đỉnh khoảng 2,5 A theo PROJECT.md. Chưa có phân tích nhiệt, sụt áp, dòng qua via hoặc chỗ thắt cổ đồng. Không được coi DRC sạch là xác nhận dòng tải.
- GND có một zone F.Cu và một zone B.Cu (đã kiểm lại LayerSet, thay cho nhận định ban đầu sai). Zone B.Cu có một polygon liên tục sau khi thêm đường cấp 6 V A; zone F.Cu có ba polygon. Cần kiểm tra chỗ thắt cổ đồng và đo sụt áp đường hồi từ J5–J8 về buck tương ứng, đặc biệt nhiễu áp đất đối với MCU/USB.
- USB D− 0,18 mm, D+ 0,20 mm, chiều dài hình học lần lượt khoảng 14,0 và 17,8 mm; cần kiểm tra cặp tín hiệu, trở kháng/return path và ESD. VBUS của J21 để hở có chủ đích theo design manual nhưng schematic và PCB còn lệch parity.

## Góc DFM / DFA

- ERC 0 lỗi/0 cảnh báo; DRC 0 violations/0 unconnected, nhưng schematic parity có 81 cảnh báo: 73 footprint ID không khớp tên thư viện, 4 net conflict VBUS J21 và 4 lỗ gá chỉ có ở PCB.
- Đường tín hiệu nhỏ nhất 0,15 mm; các linh kiện thụ động SMT trong BOM là 0603. Cần xưởng xác nhận năng lực lắp module ESP32-S3-WROOM-1U, USB-C 16 chân, lỗ gá, connector THT, copper 1 oz và khoảng cách antenna/cáp.
- BOM ghi U3 `LD1117S33` nhưng MPN `AMS1117-3.3`; cần đối chiếu đúng nhà sản xuất, pinout, tụ ổn định và nhiệt trước mua.
- Gói Gerber/BOM hiện có hash khớp manifest tại thời điểm review, nhưng manifest chỉ ghi 0 ERC/DRC, không ghi 81 cảnh báo parity. Không dùng gói này đặt hàng.

## Các gate để hoàn tất

Thử nghiệm trên bản PCB tạm (không chép vào nguồn thiết kế): tăng 1.463 đoạn đường nguồn 0,5 lên 1,0 mm làm DRC phát sinh 831 mục, trong đó 499 clearance và 71 shorting. Bản thử này không thể dùng để sản xuất; phải bố trí lại đường đồng và khoảng trống theo từng cụm, không tăng bề rộng hàng loạt. DRC trên bản tạm không nằm cùng đường project nên một phần cảnh báo rule mặc định cần phân loại lại; kết luận chắc chắn là cách đổi hàng loạt không đạt.

### Ước lượng điện trở đường servo (PCB hiện tại)

Từ graph track/via của file PCB, nhánh `+6V_B` F3.2 → J7.2 dài khoảng 56,2 mm và F3.2 → J8.2 khoảng 67,3 mm, đều rộng 0,5 mm. Với đồng 1 oz (~35 µm), điện trở suất Cu 1,724×10⁻⁸ Ω·m ở 20 °C và bỏ qua điện trở via, điện trở đường lần lượt khoảng 0,055/0,066 Ω. Ở 2,5 A đỉnh, sụt áp riêng đường dương khoảng 0,14/0,17 V; tổn hao tức thời khoảng 0,35/0,41 W. Đây là ước lượng đường hình học, chưa gồm đường hồi, PTC, connector, buck, nhiệt độ và điện trở tiếp xúc. Cần đo trên mẫu.

Một thử nghiệm thứ hai trong `reports/rev_s3/work/trial/` chỉ tăng 487 đoạn `+6V_B` từ 0,5 lên 0,8 mm. Với rule project, DRC phát sinh 509 mục (499 clearance, 8 shorting, 2 solder-mask bridge). Vì vậy không thể sửa bằng thay bề rộng tự động ngay trên route cũ; phải dời/reroute những đoạn chịu tải và kiểm tra khoảng trống từng khu vực. Thử nghiệm tăng hàng loạt không được áp dụng vào nguồn thiết kế.

### Thay đổi đã áp dụng: đường cấp bổ sung 6 V B

- Ngày 2026-10-29: thêm đường `+6V_B` rộng 1,2 mm trên F.Cu từ F3.2 đi sát mép phải (x ≈ 198 mm) tới J7.2 và J8.2. Đường 0,5 mm cũ vẫn nối song song; không đổi footprint, schematic hoặc rail A.
- Đường ngắn nhất theo graph từ F3.2 tới J7.2/J8.2 hiện có điện trở lý tưởng khoảng 0,026/0,030 Ω, tương ứng sụt áp đỉnh 2,5 A khoảng 0,065/0,075 V. Đây là ước lượng chỉ cho đồng dương 1 oz tại 20 °C, bỏ qua via/tiếp xúc/nhiệt và nhánh song song.
- Sau khi đổ lại zone, ERC 0 lỗi/0 cảnh báo; DRC 0 violation/0 unconnected; parity còn 81 mục như trước. Đường GND của J7/J8 vẫn về zone F.Cu; chưa có kiểm chứng sụt áp/nhiệt đường hồi trên mẫu. Vì vậy chỉ đánh dấu đường dương 6 V B đã cải thiện trên file, chưa nghiệm thu toàn rail hoặc production.

### Thay đổi đã áp dụng: đường cấp bổ sung 6 V A

- Ngày 2026-10-29: thêm đường `+6V_A` rộng 1,2 mm trên B.Cu từ F2.2 qua vùng giữa board tới J5.2 và J6.2. Đường 0,5 mm cũ vẫn nối song song; không đổi rail B hoặc footprint.
- Chiều dài hình học đường mới khoảng 65/75 mm tới J5/J6. Với đồng 1 oz tại 20 °C, điện trở lý tưởng khoảng 0,027/0,031 Ω; ở đỉnh 2,5 A tương ứng khoảng 0,067/0,077 V trên đường dương. Không tính đường cũ song song, pad, PTC, đầu nối và đường hồi.
- ERC 0 lỗi/0 cảnh báo; DRC 0 violation/0 unconnected; parity còn 81 mục. GND B.Cu vẫn là một polygon liên tục sau đổ lại đồng. Đây là kiểm tra trên file, chưa phải thử tải/nhiệt.

### Thay đổi đã áp dụng: liên kết 12 V giữa hai buck

- Thêm đường `+12V` rộng 1,2 mm trên B.Cu từ J2.1 tới J3.1, dài 44 mm, song song với đường 0,5 mm cũ. Điện trở đường mới lý tưởng khoảng 0,018 Ω tại 20 °C (chưa tính nhánh song song).
- ERC 0 lỗi/0 cảnh báo; DRC 0 violation/0 unconnected; parity vẫn 81 mục. Zone GND B.Cu vẫn là một polygon liên tục sau đổ lại đồng.
- Đoạn `+12V` D7.1 → J2.1 ban đầu rộng 0,5 mm dài khoảng 29,7 mm, điện trở hình học khoảng 0,029 Ω. Đoạn này mang tổng dòng vào hai buck. Với hai đầu ra 6 V × 2,5 A đỉnh, hiệu suất buck giả định 85%, dòng vào 12 V xấp xỉ 2,94 A chưa gồm logic; cần dùng số đo thật để chốt. Phép thử thêm đường trực tiếp qua vùng D7/F1/F2 gây 7 lỗi DRC, nên không áp dụng.

### Thay đổi đã áp dụng: bypass 12 V từ D7 tới J2 và giảm parity

- Thêm đường `+12V` rộng 1,5 mm trên B.Cu đi vòng phía trên J2, nối D7.1 qua hai via xuyên lỗ 1,0/0,5 mm rồi về J2.1. Đường 0,5 mm cũ được giữ song song. Đường mới dài khoảng 62 mm, điện trở đồng lý tưởng khoảng 0,020 Ω tại 20 °C (chưa tính via và nhánh song song). Ở 3 A, sụt áp riêng đường mới khoảng 0,061 V và tổn hao tức thời khoảng 0,18 W; cần đo nhiệt/áp trên mẫu.
- Bổ sung thư viện định danh cho 65 footprint trên PCB; đánh dấu H1–H4 là footprint chỉ thuộc board; đặt TP1–TP8 ngoài BOM trên schematic để khớp thuộc tính PCB. Các thay đổi này không đổi hình học đồng hoặc net. Parity giảm từ 81 xuống 4 mục.
- Bốn mục còn lại là pad VBUS chồng nhau ở USB-C J21: schematic đánh dấu không kết nối riêng từng chân, còn hai cặp pad vật lý chồng lên nhau phải cùng net trên PCB. Thử xoá net tại pad làm DRC phát sinh lỗi clearance; giữ cấu hình hiện tại, cần kiểm tra thủ công footprint USB-C và ghi ngoại lệ khi phát hành.
- Sau thay đổi: ERC 0 lỗi/0 cảnh báo; DRC 0 violation/0 unconnected; zone GND B.Cu vẫn một polygon liên tục. Chưa thử tải, nhiệt hoặc DFM xưởng; chưa phát hành Gerber mới.

1. Xác định dòng liên tục/đỉnh của mỗi rail bằng thông số servo và phép đo; lập budget sụt áp/nhiệt cho 12 V, 6 V, GND, via, fuse/PTC và connector.
2. Sửa layout nguồn/return theo budget; giữ hai rail 6 V độc lập. Sau mỗi sửa, chạy ERC/DRC/parity và xem lại thủ công.
3. Giải quyết hoặc ghi ngoại lệ có chủ đích cho từng nhóm parity; kiểm tra footprint/cực tính theo bản vẽ hãng.
4. Review USB, anten, nguồn 3,3 V và DFM với xưởng; trình bày rủi ro layout cuối cho người dùng duyệt trước khi xuất fabrication mới.
5. Thử mẫu có tải, ghi số đo/serial/firmware rồi mới nghiệm thu production.
