"""Static checks for the code-defined FV-CTRL Rev A schematic."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "hardware/archive/reva" / "FV-CTRL_RevA.net.json").read_text(encoding="utf-8"))
signals = data["signals"]
errors = []
required = {"S1_TOP_PWM", "S1_BOT_PWM", "S2_TOP_PWM", "S2_BOT_PWM", "IR_TX", "IR_RX1", "IR_RX2"}
missing = required - signals.keys()
if missing:
    errors.append("missing signals: " + ", ".join(sorted(missing)))
for name, gpio in signals.items():
    number = int(gpio.removeprefix("GPIO"))
    if number in {0, 2, 12, 15}:
        errors.append(f"{name} uses strapping GPIO{number}")
    if number in range(34, 40) and name not in {"IR_RX1", "IR_RX2"}:
        errors.append(f"{name} uses input-only GPIO{number} as output")
part_text = " ".join(p["ref"] for p in data["parts"])
for ref in ("F1", "Q1", "D1", "F2", "F3", "R1-R4", "R5-R8", "C1,C2", "Q2"):
    if ref not in part_text:
        errors.append(f"required protection part missing: {ref}")
print("PASS" if not errors else "FAIL")
for error in errors:
    print("-", error)
sys.exit(bool(errors))
