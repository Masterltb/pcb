# AGENTS.md — quy tắc làm việc với PCB FreshVend

Đọc phần quyết định mới nhất của `PROJECT.md` trước khi làm việc, rồi đọc mục liên quan đến task. Đây là nguồn sự thật về kiến trúc và GPIO; yêu cầu mới đã được người dùng duyệt ưu tiên hơn mô tả RevA lịch sử.

## Thiết kế hiện hành

- RevB: `hardware/revb/FV-CTRL_RevB.kicad_pro`; ESP32-D0WD-V3 QFN48 rời, flash ngoài, anten SMA. Không dùng DevKit/WROOM hoặc PSRAM chiếm GPIO16/17.
- PCB hai lớp, tối đa 100 × 100 mm. MCU/RF/USB dùng SMT/reflow tại xưởng; đầu nối và linh kiện công suất ưu tiên THT, có thể hàn tay. Yêu cầu THT-only/DevKit của RevA không áp dụng cho RevB.
- Hai XL4015 gá ngoài hộp điện qua đầu nối cắm rời, hai rail servo 6 V độc lập, GND chung; không nối song song đầu ra. Giữ buck 5 V logic và nguồn 3,3 V trên PCB. USB chỉ truyền dữ liệu, phải cấp nguồn chính khi nạp.
- RevA2: `hardware/reva2/`; RevA: `hardware/archive/reva/`. Chỉ sửa bản cũ khi task yêu cầu. Không trộn các thay đổi cục bộ chưa kiểm định vào commit RevB.
- Nguồn hiện tại đã được đi dây và kiểm tra trên file; chưa nghiệm thu production. Đọc `docs/revb/RevB-status.md` về tiến độ và các gate còn thiếu; không coi ERC/DRC sạch là đạt RF, nhiệt, DFM hoặc thử máy thật.

## Quy tắc thiết kế

1. Không đổi GPIO mục 5 của PROJECT.md hoặc kiến trúc nguồn khi chưa được người dùng duyệt.
2. Mọi kết nối ra ngoài qua đầu nối theo PROJECT.md; không thêm pad hàn dây trực tiếp.
3. Giá trị, pinout và footprint phải đối chiếu datasheet/bản vẽ hãng. Chưa chắc thì ghi “cần xác nhận”, không suy tọa độ từ ảnh.
4. Người dùng đã cho phép chọn sản phẩm cụ thể theo bản vẽ hãng trước khi mua mẫu. XL4015 gá ngoài nên không cần footprint cắm module lên mainboard; không yêu cầu lại số đo DevKit đã loại bỏ. Chỉ hỏi kích thước khi thiếu dữ liệu thực sự chặn bước đang làm; kiểm tra mẫu nhận được trước sản xuất.
5. Giữ cầu chì, PTC, chống ngược cực, TVS, điện trở kéo xuống PWM servo 10 kΩ, LED nguồn và test point. Giữ limit switch và linh kiện liên quan dạng DNP.
6. Trước thay đổi thiết kế, ghi review theo hai góc IC/SI/PI và DFM/DFA; không mô tả đó là chứng nhận độc lập. Chỉnh KiCad từng bước nhỏ, nêu rõ thay đổi.
7. Sau mỗi bước sửa schematic/PCB, chạy ERC/DRC và parity khi phù hợp; báo cáo lỗi trước bước tiếp. Không hạ rule hoặc bỏ bảo vệ để làm sạch kết quả. Xem lại thủ công nhánh 12 V/servo sau autoroute; giữ các đường RF/crystal đã review.
8. RF 50 Ω, matching/crystal, via/paste EP QFN, nhiệt LDO, xung hồi 6 V và điều kiện xưởng phải được xác nhận bằng dữ liệu phù hợp. File kiểm tra không thay thế đo mẫu hoặc DFM xưởng.
9. Trước khi xuất Gerber/drill, trình bày rủi ro layout cuối để người dùng duyệt: dòng lớn/đường hồi, tụ, buck ngoài, nhiệt, RF, QFN và truy cập USB. Không đặt hàng hoặc gửi dữ liệu cho xưởng nếu chưa được yêu cầu.
10. IR phát burst 38 kHz theo mục 14 PROJECT.md, không phát sóng mang liên tục. Với lỗi board thật, hỏi triệu chứng/số đo trước; kiểm tra 12 V → 6 V từng rail → 5 V → 3,3 V → PWM/IR/limit.

## Công cụ và vị trí file

Windows, KiCad 10 (`kicad-cli`); dùng Python đi kèm KiCad khi cần `pcbnew`. Freerouting cần đúng Java/runtime; kiểm tra đường dẫn sẵn có trước khi chạy.

- `libs/`: thư viện dùng chung; giữ đường dẫn tương đối trong bảng thư viện từng project.
- `docs/revb/`: review; `bom/`, `assembly/`, `schematic/`: đầu ra tương ứng.
- `reports/revb/verified/`: báo cáo hiện hành; `reports/revb/work/`: log/checkpoint/DSN/SES tạm, được Git bỏ qua.
- `releases/revb/`: ZIP review; `releases/archive/`: gói cũ, không dùng đặt RevB.
- Đọc `tools/README.md` trước khi chạy script. Không chạy lại generator/fanout/repair để chỉ mở mạch hoặc làm mới báo cáo: một số bước dựng lại nguồn và không idempotent.

```powershell
kicad-cli sch erc --output reports/revb/verified/RevB-final-erc.rpt hardware/revb/FV-CTRL_RevB.kicad_sch
kicad-cli pcb drc --format json --schematic-parity --output reports/revb/verified/RevB-final-drc.json hardware/revb/FV-CTRL_RevB.kicad_pcb
kicad-cli sch export netlist --format kicadxml --output reports/revb/verified/RevB.net.xml hardware/revb/FV-CTRL_RevB.kicad_sch
```

Dùng `tools/verify_rev_b.py --pcb` và `tools/verify_rev_b_via_paste.py` cho các thay đổi liên quan; `tools/package_rev_b_review.py` đóng ZIP sau khi các gate đạt. Chỉ xuất fabrication sau duyệt theo quy tắc 9. Ghi kết quả mẫu theo serial/firmware/tải vào `docs/project/rev-notes.md`.

## Tiết kiệm token, giữ chất lượng

- Đọc đúng phạm vi bằng `rg`, diff và đoạn liên quan; không đọc lại toàn repo hoặc tài liệu đã đọc nếu không có thay đổi liên quan.
- Gộp các thao tác đọc độc lập; giới hạn output. Với log dài, lấy số lỗi, đoạn lỗi và đường dẫn báo cáo, không in toàn bộ SVG/netlist/log.
- Chọn kiểm tra theo tác động: sửa mạch vẫn bắt buộc ERC/DRC; sửa đường dẫn kiểm tra khả năng mở/đóng gói; sửa văn bản thuần túy kiểm tra diff/liên kết. Không chạy lại kiểm tra đã đạt khi chưa có thay đổi liên quan.
- Tiếp tục các quyết định đã được duyệt; chỉ hỏi khi dữ liệu thiếu chặn việc hoặc cần đổi ràng buộc. TODO không liên quan không chặn task độc lập.
- Với công việc nhiều bước, lưu kế hoạch ngắn, trạng thái, commit và bằng chứng trong repo. Phân biệt “đã implement”, “đã kiểm tra trên file”, “đã thử phần cứng”; không đánh dấu hoàn tất khi còn gate bắt buộc.
- Cập nhật tiến độ ngắn khi có kết quả hoặc đổi hướng; kết thúc bằng thay đổi chính, kiểm tra, file/commit và việc còn chặn. Tránh lặp kế hoạch, báo cáo đầy đủ hoặc lịch sử chat.
- Dùng commit riêng cho thay đổi có ý nghĩa, tên Conventional Commits; nhánh dùng `feat/`, `fix/`, `docs/`, `chore/`, không dùng `codex/`. Không tạo commit rỗng hoặc đưa thay đổi ngoài phạm vi vào commit.

## Skill dự án

Nếu có `fv-pcb-design` và các skill `fv-pcb-*`, đọc và dùng theo phạm vi task. Bộ này trước đây không có sẵn; người dùng đã cho phép quy trình KiCad trực tiếp với review hai góc và đầy đủ kiểm tra. Nếu vẫn thiếu, tiếp tục theo ngoại lệ đã được duyệt, không hỏi lại chỉ vì thiếu skill. Không tuyên bố đã dùng skill không tồn tại.
