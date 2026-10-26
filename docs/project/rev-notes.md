# RevA2 physical qualification log

No physical boards tested as of 2026-10-20.

Record: serial, BOM/PCB revision, supply, harness lengths, ambient temperature, rail voltages and ripple, load currents, component temperatures, IR bowl tests, cycle count, injected fault and recovery result. Attach measurements and corrective actions.


## RevB — 2026-10-26: xuất Gerber mẫu

Theo yêu cầu trong chat, xuất Gerber/drill từ PCB RECOM RevB hiện hành (design commit `8282d76`), giữ nguyên schematic/PCB. Kiểm lại ERC/DRC/parity và verifier đều PASS; Gerber/drill đối chiếu 100 x 100 mm, 375 PTH (gồm 2 slot) và 4 NPTH. Xem `docs/revb/RevB-prototype-export-2026-10-26.md` và manifest trong `releases/revb/`.

Đây là xuất file để báo giá/chuẩn bị mẫu; chưa gửi xưởng hoặc đặt hàng. Chưa có thử mẫu thật, xác nhận DFM, RF/nhiệt hoặc nghiệm thu production. Ghi kết quả thử theo serial, firmware và tải khi có mẫu.
