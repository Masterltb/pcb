# FV-CTRL Rev A Project Audit

- KiCad CLI Version: `10.0.7`
- Mainboard Schematic (`FV-CTRL_RevA.kicad_sch`): PRESENT
- Satellite IR RX Schematic (`FV-IR-RX_RevA.kicad_sch`): PRESENT
- Mainboard PCB (`FV-CTRL_RevA.kicad_pcb`): PRESENT
- Satellite IR RX PCB (`FV-IR-RX_RevA.kicad_pcb`): PRESENT
- Total Components Placed: 69 / 69
- Total Nets Routed: 37 nets

## Gate Status

- **Electrical Schematic:** PASS — 0 ERC errors, 0 warnings across mainboard and satellite boards.
- **Symbol & Footprint Validation:** PASS — Verified real footprints for XH-M401 (XL4016 8A), MP1584EN (Mini 3A), ESP32 DevKit 38, fuseholder clips, TVS, MOSFET, PTCs, JST/terminal connectors.
- **PCB Layout & Routing:** PASS — 100mm × 100mm 2-layer all-THT hand-solderable board, solid dual-layer GND planes with thermal relief, orthogonal high-current/logic routing.
- **KiCad DRC Verification:** PASS — 0 DRC violations, 0 unconnected pads, 0 footprint errors.
- **Production Artifacts:** PASS — Gerbers, Excellon drill files, and BOM generated.

## Hardware Specifications Selected

- **Servo Buck:** XH-M401 (XL4016E1 8A 200W PWM Buck Converter), 5.08mm KF301 screw terminals, set to 6.0V.
- **Logic Buck:** MP1584EN (Mini 3A 0.8-20V Buck Converter), dual 2.54mm pin headers, set to 5.0V.
- **Microcontroller Interface:** ESP32 DevKit 38 (38 pins, 0.9" / 22.86mm row pitch, USB facing bottom edge).
- **Dual Column Servos:** S1-TOP, S1-BOT, S2-TOP, S2-BOT with individual PTC fuses (F2, F3) and 2200µF bulk decoupling.
- **IR Sensor Subsystem:** 2x satellite boards with TSOP38238/VS1838B receivers, 100Ω + 4.7µF local RC filter.
