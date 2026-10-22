# PCB Agent Harness

Bộ khung đa dự án cho agent vẽ PCB theo nguyên tắc harness engineering: contract rõ ràng, kiểm soát interface, truy vết requirement, WIP bằng một và evidence độc lập.

FreshVend chỉ là dự án tham chiếu. Không copy GPIO, nguồn, footprint hoặc giới hạn dòng nếu contract dự án mới không yêu cầu.

## Cấu trúc

- AGENTS.template.md: quy tắc làm việc cho agent.
- contract/project.json: toolchain, nguồn file và lệnh verification.
- contract/requirements.csv: requirement đến thiết kế, test và evidence.
- contract/interfaces.csv: interface control document.
- contract/work-items.json: WIP một công việc.
- contract/risk-register.csv: risk mở và evidence đóng risk.
- policies/release-gates.md: gate cho schematic, layout, release và prototype.
- scripts: khởi tạo, kiểm contract, chạy verification.
- docs/agent-workflow.md: state machine và role review.

## Cách dùng

1. Copy folder này vào dự án mới với tên pcb-agent-harness.
2. Copy AGENTS.template.md thành AGENTS.md, hoặc tích hợp nó vào policy hiện có.
3. Điền contract trước khi tạo schematic.
4. Chạy python pcb-agent-harness/scripts/validate_contract.py --root .
5. Chỉ tạo Gerber sau G3; chỉ bật production sau G4.

Generator luôn ghi build directory trước. Native KiCad source chỉ được promote sau gate PASS. ERC và DRC sạch không chứng minh RF, nhiệt, EMC, cơ khí hay production quality.
