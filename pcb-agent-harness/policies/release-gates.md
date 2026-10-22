# PCB release gates

Mỗi gate là pass, fail hoặc not-applicable và có evidence path. Not-applicable cần lý do.

## G0 Intake và interface
- Requirement có ID, nguồn, priority và verification method.
- Interface có origin, destination, connector/mate, pinout, voltage/current hoặc impedance, protection và method.
- Cơ khí, môi trường, nguồn, safety, manufacturing constraint được ghi.
- Critical unknown không bị thay bằng giả định.

## G1 Schematic
- Symbol, pin mapping, MPN và footprint có nguồn xác minh.
- ERC không có error/warning chưa xử lý.
- Firmware pin map, straps, reset, boot, sequencing và DNP được kiểm nếu áp dụng.
- External I/O có connector và nhãn rõ.

## G2 Layout
- Outline kín; mounting và keepout hợp vỏ/cáp.
- Placement theo power/interface flow; decoupling, crystal, RF, switching loop theo datasheet.
- DRC 0 error; unconnected 0; schematic-PCB parity 0.
- Power, high current, high-speed/RF, analog và return path có review riêng.
- Không overlap footprint, silk over pad hoặc connector không truy cập được.

## G3 DFM/DFA và release candidate
- Stackup, copper, drill, via, mask/paste và assembly capability có xác nhận xưởng hoặc risk mở.
- BOM có MPN và điều kiện thay thế; CPL đã preview pin 1, rotation, side.
- Gerber, drill, BOM và CPL cùng revision, đã preview.
- Release ZIP có manifest hash, ERC/DRC report và open-risk list.

## G4 Prototype và production
- Bring-up có power sequence, current limit và test point.
- Requirement critical/high có dữ liệu điều kiện, thiết bị, revision, serial và kết quả.
- Risk tải, nhiệt, RF/EMC, ESD, cơ khí, firmware interface và reliability đã đóng hoặc chấp thuận.
- production_allowed chỉ bật sau prototype review.
