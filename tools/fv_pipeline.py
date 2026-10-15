"""Reproducible gate runner for the FV-CTRL manufacturing flow."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

STAGES = {
    "audit": [[PYTHON, "tools/generate_fv_schematic.py"], [PYTHON, "tools/validate_fv_design.py"], [PYTHON, "tools/audit_fv_project.py"]],
    "schematic": [[PYTHON, "tools/generate_fv_schematic.py"]],
    "erc": [["kicad-cli", "sch", "erc", "--severity-all", "--format", "report", "--output", "reports/erc.rpt", "hardware/FV-CTRL_RevA.kicad_sch"]],
}

stage = sys.argv[1] if len(sys.argv) > 1 else "audit"
if stage not in STAGES:
    raise SystemExit(f"Unsupported stage: {stage}. Supported: {', '.join(STAGES)}")
for cmd in STAGES[stage]:
    subprocess.run(cmd, cwd=ROOT, check=True)
