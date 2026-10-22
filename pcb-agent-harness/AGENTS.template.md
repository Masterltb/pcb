# Quy tắc agent PCB

Đọc pcb-agent-harness/contract/project.json, requirements.csv, interfaces.csv, work-items.json và policy repository trước khi sửa.

1. Contract là nguồn sự thật. Dữ liệu thiếu hay mâu thuẫn phải ghi issue/risk, không tự suy diễn.
2. Chỉ một work item được in_progress.
3. Đổi interface, pin map, nguồn, package, outline hoặc rule xưởng phải cập nhật requirement, interface, risk và test liên quan.
4. Symbol, footprint, pin mapping và MPN cần datasheet hoặc nguồn đã kiểm. Không bịa pin/net/footprint để làm DRC sạch.
5. Generator, native source và build output tách nhau. Generator ghi build trước; promote sau gate PASS.
6. Sửa schematic: ERC, netlist và pin mapping. Sửa PCB: DRC, net hở, parity và review vùng thay đổi.
7. Evidence phải độc lập với generator: KiCad CLI, pcbnew, netlist parser, review thủ công hoặc phép đo.
8. ERC/DRC chỉ chứng minh rule đã cấu hình; không suy ra RF, EMC, nhiệt, tải hay cơ khí.
9. Không xuất fabrication package khi release gate fail hay evidence thiếu.
10. Work item hoàn thành phải có file đổi, command, report, giả định và risk còn mở.
