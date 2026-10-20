"""Reproducible gate runner for the FV-CTRL manufacturing flow."""
from pathlib import Path
import subprocess
import sys
import shutil

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

# Check for KiCad's embedded Python with pcbnew module
KICAD_PYTHON = Path("C:/Program Files/KiCad/10.0/bin/python.exe")
BOARD_PYTHON = str(KICAD_PYTHON) if KICAD_PYTHON.exists() else PYTHON

STAGES = {
    "schematic": [
        [PYTHON, "tools/generate_fv_schematic.py"],
        [PYTHON, "tools/generate_ir_rx_schematic.py"]
    ],
    "board": [
        [BOARD_PYTHON, "tools/generate_fv_board.py"],
        [BOARD_PYTHON, "tools/generate_ir_rx_board.py"]
    ],
    "erc": [
        ["kicad-cli", "sch", "erc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/erc.rpt", "hardware/archive/reva/FV-CTRL_RevA.kicad_sch"],
        ["kicad-cli", "sch", "erc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/erc_FV-IR-RX_RevA.rpt", "hardware/archive/reva/FV-IR-RX_RevA.kicad_sch"],
        ["kicad-cli", "sch", "erc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/erc_FV-IR-RX1_RevA.rpt", "hardware/archive/reva/FV-IR-RX1_RevA.kicad_sch"],
        ["kicad-cli", "sch", "erc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/erc_FV-IR-RX2_RevA.rpt", "hardware/archive/reva/FV-IR-RX2_RevA.kicad_sch"]
    ],
    "drc": [
        ["kicad-cli", "pcb", "drc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/drc.rpt", "hardware/archive/reva/FV-CTRL_RevA.kicad_pcb"],
        ["kicad-cli", "pcb", "drc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/drc_FV-IR-RX_RevA.rpt", "hardware/archive/reva/FV-IR-RX_RevA.kicad_pcb"],
        ["kicad-cli", "pcb", "drc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/drc_FV-IR-RX1_RevA.rpt", "hardware/archive/reva/FV-IR-RX1_RevA.kicad_pcb"],
        ["kicad-cli", "pcb", "drc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/drc_FV-IR-RX2_RevA.rpt", "hardware/archive/reva/FV-IR-RX2_RevA.kicad_pcb"]
    ],
    "gerber": [
        ["kicad-cli", "pcb", "export", "gerbers", "-o", "releases/archive/reva/gerbers/FV-CTRL_RevA", "hardware/archive/reva/FV-CTRL_RevA.kicad_pcb"],
        ["kicad-cli", "pcb", "export", "drill", "-o", "releases/archive/reva/gerbers/FV-CTRL_RevA", "hardware/archive/reva/FV-CTRL_RevA.kicad_pcb"],
        ["kicad-cli", "pcb", "export", "gerbers", "-o", "releases/archive/reva/gerbers/FV-IR-RX_RevA", "hardware/archive/reva/FV-IR-RX_RevA.kicad_pcb"],
        ["kicad-cli", "pcb", "export", "drill", "-o", "releases/archive/reva/gerbers/FV-IR-RX_RevA", "hardware/archive/reva/FV-IR-RX_RevA.kicad_pcb"]
    ],
    "audit": [
        [PYTHON, "tools/generate_fv_schematic.py"],
        [PYTHON, "tools/generate_ir_rx_schematic.py"],
        [BOARD_PYTHON, "tools/generate_fv_board.py"],
        [BOARD_PYTHON, "tools/generate_ir_rx_board.py"],
        [PYTHON, "tools/validate_fv_design.py"],
        [PYTHON, "tools/audit_fv_project.py"]
    ],
    "all": [
        [PYTHON, "tools/generate_fv_schematic.py"],
        [PYTHON, "tools/generate_ir_rx_schematic.py"],
        [BOARD_PYTHON, "tools/generate_fv_board.py"],
        [BOARD_PYTHON, "tools/generate_ir_rx_board.py"],
        ["kicad-cli", "sch", "erc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/erc.rpt", "hardware/archive/reva/FV-CTRL_RevA.kicad_sch"],
        ["kicad-cli", "sch", "erc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/erc_FV-IR-RX_RevA.rpt", "hardware/archive/reva/FV-IR-RX_RevA.kicad_sch"],
        ["kicad-cli", "pcb", "drc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/drc.rpt", "hardware/archive/reva/FV-CTRL_RevA.kicad_pcb"],
        ["kicad-cli", "pcb", "drc", "--severity-all", "--format", "report", "--output", "reports/archive/reva/drc_FV-IR-RX_RevA.rpt", "hardware/archive/reva/FV-IR-RX_RevA.kicad_pcb"],
        ["kicad-cli", "pcb", "export", "gerbers", "-o", "releases/archive/reva/gerbers/FV-CTRL_RevA", "hardware/archive/reva/FV-CTRL_RevA.kicad_pcb"],
        ["kicad-cli", "pcb", "export", "drill", "-o", "releases/archive/reva/gerbers/FV-CTRL_RevA", "hardware/archive/reva/FV-CTRL_RevA.kicad_pcb"],
        [PYTHON, "tools/validate_fv_design.py"],
        [PYTHON, "tools/audit_fv_project.py"]
    ]
}

stage = sys.argv[1] if len(sys.argv) > 1 else "audit"
if stage not in STAGES:
    raise SystemExit(f"Unsupported stage: {stage}. Supported: {', '.join(STAGES)}")
for cmd in STAGES[stage]:
    subprocess.run(cmd, cwd=ROOT, check=True)
