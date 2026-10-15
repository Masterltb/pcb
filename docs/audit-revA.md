# FV-CTRL Rev A audit
- KiCad CLI: `10.0.7`
- Native schematic: present
- Native board: missing
- Legacy `.sch`: present (conceptual annotations only)
- Code netlist: present; 10 connectors, 11 signals.

## Gate status
- Electrical schematic: DRAFT READY — verified native KiCad 10 schematic (FV-CTRL_RevA.kicad_sch) with 0 ERC violations.
- Symbol/footprint validation: BLOCKED — module dimensions and MPNs are TBD.
- PCB/layout/routing/zones: BLOCKED — no native schematic netlist or enclosure/module dimensions.
- ERC/DRC/Gerber/drill/ZIP: BLOCKED — no native schematic or board.

## Electrical uncertainties
- Exact XL4015 module part number, pin spacing, hole/pad geometry and thermal rating.
- Exact 5V buck module, ESP32 DevKit header spacing, and mechanical enclosure.
- THT MPNs and datasheets for fuse, PTC, P-MOSFET, TVS, capacitors and connectors.
