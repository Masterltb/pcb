# CLAUDE.md: quy tắc cho agent thiết kế PCB

Đọc `PROJECT.md` trước khi làm bất cứ việc gì. Đó là nguồn sự thật về mạch, bảng chân và ràng buộc.

## Môi trường
- Windows, KiCad 10 (`kicad-cli`), Python 3.11, Freerouting 2.5.0 (cần Java 25) tại `F:\programs\freerouting`.
- Project hiện hành nằm trong `hardware/revb/`; RevA2 ở `hardware/reva2/`, RevA lịch sử ở `hardware/archive/reva/`. Footprint tự tạo nằm trong `libs/`. Tài liệu xuất ra nằm trong `docs/`.
- Repo dùng git. Mỗi thay đổi thiết kế có ý nghĩa là một commit riêng.

## Quy tắc bắt buộc
1. Không đổi bảng gán chân ESP32 hoặc kiến trúc nguồn khi chưa hỏi người dùng.
2. Board 2 lớp, tối đa 100 x 100 mm, chỉ linh kiện THT, tự hàn.
3. Mọi kết nối ra ngoài board đều qua đầu nối theo mục 6 của PROJECT.md. Không có pad hàn dây trực tiếp.
4. Mọi giá trị linh kiện phải đối chiếu datasheet. Không chắc thì ghi "cần xác nhận", không tự bịa.
5. Footprint của ESP32 DevKit và XL4015 module phải dựa trên số đo thật của người dùng (mục 10 của PROJECT.md). Chưa có số đo thì dừng và hỏi.
6. Phần bảo vệ (cầu chì, PTC, chống ngược cực, TVS, điện trở kéo xuống 10k cho PWM servo) và chẩn đoán (LED nguồn, test point) là bắt buộc, không được bỏ để tiết kiệm chỗ.
7. Mạch limit switch là tùy chọn: vẽ footprint và điện trở/tụ, đánh dấu DNP.
8. Sau mỗi lần sửa schematic/PCB, chạy ERC/DRC và báo cáo lỗi trước khi làm bước tiếp.
9. Trước khi xuất Gerber, liệt kê điểm rủi ro cho người dùng duyệt (đường dòng lớn, vị trí tụ, khoảng cách buck với ESP32, truy cập cổng USB).
10. Sửa file KiCad theo từng thay đổi nhỏ, nói rõ đã đổi gì.

## Lệnh thường dùng
```
kicad-cli sch erc --output reports/revb/verified/RevB-final-erc.rpt hardware/revb/<ten>.kicad_sch
kicad-cli pcb drc --output reports/revb/verified/RevB-final-drc.rpt hardware/revb/<ten>.kicad_pcb
kicad-cli pcb export gerbers --output releases/revb/fabrication/ hardware/revb/<ten>.kicad_pcb
kicad-cli pcb export drill --output releases/revb/fabrication/ hardware/revb/<ten>.kicad_pcb
```
Autoroute: xuất DSN từ PCB Editor, chạy Freerouting, nhập lại SES. Luôn xem lại đi dây nhánh 12V và servo bằng tay.

## Quy trình
1. Schematic (mainboard, rồi board RX) -> ERC sạch.
2. Gán footprint, đặt linh kiện theo ràng buộc mục 8 của PROJECT.md.
3. Đi dây nhánh nguồn/servo trước, tín hiệu sau.
4. DRC sạch -> người dùng duyệt -> xuất Gerber, BOM (MPN + phương án thay thế), checklist bring-up vào `docs/`.
5. Rev A khoảng 5 tấm; ghi lỗi từ máy thật vào `docs/project/rev-notes.md` để làm Rev B.

## Debug
- Khi người dùng báo lỗi trên board thật, hỏi triệu chứng và số đo (điện áp tại test point, LED nguồn nào tắt) trước khi đề xuất sửa.
- Thứ tự kiểm tra: 12V, 6V từng rail, 5V logic, 3.3V, rồi PWM servo, TX/RX IR, limit switch.

## Skill của dự án (trong `.claude/skills/`)
- Thiết kế: bắt đầu bằng `fv-pcb-design`; nó điều phối `fv-pcb-schematic` -> `fv-pcb-layout` -> `fv-pcb-release`.
- Kiểm thử: `fv-pcb-verify` (trước khi sản xuất), `fv-pcb-bringup` (cấp nguồn lần đầu), `fv-pcb-functional-test` (servo, IR, chu trình thật), `fv-pcb-debug` (khi có lỗi).
- Nếu PROJECT.md còn `TODO(user)` chặn bước hiện tại (mục 10, 12, 13), dừng và hỏi người dùng.
- Phần IR: xem mục 14 của PROJECT.md (phát burst, không phát liên tục).
