# Contract-driven PCB workflow

State machine:

intake -> architecture -> schematic -> part-validation -> layout -> verification -> release-review -> prototype -> production

Không bỏ state. Khi source, connector, IC, package, outline hoặc rule xưởng thay đổi, quay lại state bị ảnh hưởng.

## Harness principles

- Contract before generation: đọc requirement, interface, constraint và risk trước tool.
- WIP equals one: chỉ một work item đang làm.
- Independent evidence: generator không thể là verifier duy nhất.
- Bidirectional traceability: requirement có design artifact, method và evidence; feature không truy ra requirement phải review để loại.
- Change impact: đổi interface thì kiểm requirement, connector, firmware mapping, test và document liên quan.
- Promotion: build output chỉ thành source sau gate PASS và review diff.

| Role | Câu hỏi chính |
|---|---|
| Architect | Requirement, interface và power tree có nhất quán? |
| Schematic engineer | Pin, cực tính, protection và net có đúng datasheet? |
| Layout engineer | Placement, return path, current loop, clearance và cơ khí có đúng? |
| Verification reviewer | Evidence độc lập có đủ không? |
| DFM reviewer | Xưởng có thể làm và lắp feature này không? |
| Bring-up engineer | Đo gì, theo thứ tự nào, ngưỡng pass là gì? |
