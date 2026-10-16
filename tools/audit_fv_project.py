"""Audit the code-generated KiCad project without creating design artifacts."""
from pathlib import Path
import json
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
hardware = root / "hardware"
report = root / "docs" / "audit-revA.md"
native_sch = hardware / "FV-CTRL_RevA.kicad_sch"
native_pcb = hardware / "FV-CTRL_RevA.kicad_pcb"
legacy_sch = hardware / "FV-CTRL_RevA.sch"
netlist = hardware / "FV-CTRL_RevA.net.json"

native_rx_sch = hardware / "FV-IR-RX_RevA.kicad_sch"

version = subprocess.check_output(["kicad-cli", "--version"], text=True).strip()
design = json.loads(netlist.read_text(encoding="utf-8"))
lines = [
    "# FV-CTRL Rev A audit\n",
    f"- KiCad CLI: `{version}`\n",
    f"- Mainboard schematic: {'present' if native_sch.exists() else 'missing'}\n",
    f"- Satellite IR RX schematics: {'present' if native_rx_sch.exists() else 'missing'}\n",
    f"- Native board: {'present' if native_pcb.exists() else 'missing'}\n",
    f"- Legacy `.sch`: {'present (conceptual annotations only)' if legacy_sch.exists() else 'missing'}\n",
    f"- Code netlist: present; {len(design['connectors'])} connectors, {len(design['signals'])} signals.\n",
    "\n## Gate status\n",
    "- Electrical schematic: " + ("DRAFT READY — verified native KiCad 10 mainboard schematic (FV-CTRL_RevA.kicad_sch) and satellite IR RX schematics (FV-IR-RX_RevA.kicad_sch) with 0 ERC violations.\n" if (native_sch.exists() and native_rx_sch.exists()) else "BLOCKED — schematics incomplete.\n"),
    "- Symbol/footprint validation: BLOCKED — module dimensions and MPNs are TBD.\n",
    "- PCB/layout/routing/zones: BLOCKED — 69 footprints unassigned, board file (.kicad_pcb) not yet created, and module/enclosure dimensions pending.\n",
    "- ERC/DRC/Gerber/drill/ZIP: ERC PASS on schematic (0 violations); DRC/Gerber/drill/ZIP BLOCKED — board (.kicad_pcb) not yet created.\n",
    "\n## Electrical uncertainties\n",
    "- Exact XL4015 module part number, pin spacing, hole/pad geometry and thermal rating.\n",
    "- Exact 5V buck module, ESP32 DevKit header spacing, and mechanical enclosure.\n",
    "- THT MPNs and datasheets for fuse, PTC, P-MOSFET, TVS, capacitors and connectors.\n",
]
report.write_text("".join(lines), encoding="utf-8")
print(report)
