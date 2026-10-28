# Công cụ theo phiên bản

Chạy từ thư mục gốc repository. Mở project bằng KiCad không cần chạy generator.

| Công việc | Script |
|---|---|
| Kiểm tra độc lập pin/net RevB | `verify_rev_b.py --pcb` |
| Kiểm tra bổ sung via với paste/mask RevB | `verify_rev_b_via_paste.py` |
| Kiểm tra RECOM/pin/pitch/budget/BOM | `verify_rev_b_supply.py` (KiCad Python; tùy chọn `--baseline <PCB cũ>`) |
| Cập nhật BOM RevB | `rev_b_procurement.py` |
| Đóng ZIP review RevB | `package_rev_b_review.py` |
| Kiểm tra RevA2 | `verify_rev_a2.py --pcb` |
| Tạo BOM/CPL nháp Rev-S3 cho review SMT+THT, không xuất Gerber | `prepare_rev_s3_pcba_draft.py` (KiCad Python) |

Các verifier dùng Python đi kèm KiCad để có `pcbnew`. Trước kiểm tra RevB, xuất netlist đúng dạng XML:

```powershell
kicad-cli sch export netlist --format kicadxml --output reports/revb/verified/RevB.net.xml hardware/revb/FV-CTRL_RevB.kicad_sch
kicad-cli sch erc --output reports/revb/verified/RevB-final-erc.rpt hardware/revb/FV-CTRL_RevB.kicad_sch
kicad-cli pcb drc --format json --schematic-parity --output reports/revb/verified/RevB-final-drc.json hardware/revb/FV-CTRL_RevB.kicad_pcb
```

`rev_b_design.py`, `rev_b_layout.py` và các script fanout/routing/repair là công cụ từng bước đã dùng để xây dựng thiết kế. Một số script có tính phá dựng lại và không idempotent: không chạy lại để xem mạch hoặc làm mới báo cáo. Nguồn chuẩn hiện tại là file KiCad đã kiểm tra trong `hardware/revb/`.

`rev_a2_*`, `build_rev_a2.py` thuộc RevA2. `generate_fv_*`, `generate_ir_*`, `fv_pipeline.py`, `package_handover.py` và các bài test generator thuộc RevA lịch sử. Các công cụ này có thể ghi đè nguồn tương ứng trong khu archive; không chạy vào các sửa đổi cục bộ chưa sao lưu. Không chạy quy trình xuất Gerber/handover khi chưa duyệt rủi ro.

`generate_freshvend_cad.py` làm việc với `cad/`. `update_report_docx.py` phục vụ báo cáo RevA lịch sử.
