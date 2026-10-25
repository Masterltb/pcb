# SIM-001 — mô phỏng chức năng RevB

Ngày bắt đầu: 2026-10-25. Nhánh: feat/revb-wokwi-simulation.

Phạm vi: firmware mô phỏng ESP32/PWM/IR/limit, trạng thái hai cột,
server local thử nhận lệnh/kết quả. Không sửa nguồn KiCad hoặc đổi GPIO.

Kế hoạch và gate:
- [x] Đọc PROJECT/AGENTS, đối chiếu GPIO và giới hạn Wokwi.
- [x] Dựng project Wokwi, firmware và server mẫu.
- [x] Compile ESP32 và kiểm thử state machine/protocol/inventory.
- [x] Viết hướng dẫn, kịch bản và bằng chứng; commit riêng theo phạm vi.
- [ ] Chạy engine Wokwi thực: cần runtime/license/token hợp lệ; chưa có token CLI trong môi trường.

Acceptance: boot khóa chuyển động; arm có xác nhận; mỗi cột chỉ một motor chạy;
không chủ động mở hai tầng cùng lúc; cần IR clear→blocked→clear mới thành công;
timeout không báo thành công; ID trùng không chạy lại; lưu ID trước chuyển động;
khởi động lại không tự tiếp tục lệnh dang dở; mất mạng không giữ motor chạy vô hạn.

Review IC/SI/PI: mức PWM và mô phỏng GPIO không xác nhận nguồn/RF; IR nhập logic
sau receiver, không mô phỏng sóng/quang/AGC. Thời gian servo chỉ là giả định.
Review DFM/DFA: không sửa PCB; model DevKit trong Wokwi chỉ là đại diện CPU,
không thay BOM chip QFN hoặc chứng minh footprint/lắp ráp/cơ khí.

## Kết quả kiểm tra

- Implement: `a13667b` (firmware/diagram), `3383063` (server/test).
- Build ESP32 PASS; 18 kịch bản C++ native và 9 kiểm thử Python PASS.
- Đối chiếu Git object: schematic/PCB RevB không đổi; không cần chạy lại ERC/DRC cho task firmware này.
- Bằng chứng: `reports/revb/verified/RevB-simulation-check.json`; log local `reports/revb/work/sim-check.log`.
- Engine Wokwi, NVS qua reset thực trong engine và luồng ESP32 mô phỏng ↔ server: CHƯA CHẠY.
- Không đánh dấu gate Wokwi/hardware là hoàn tất. Các kiểm thử host không thay thế chạy engine hoặc thử máy thật.
