"""Prepare a review-only mixed SMT/THT BOM and placement list; never export Gerbers."""

import ast
import csv
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "hardware/rev_s3/FV-CTRL_RevS3.kicad_pcb"
OUT = ROOT / "assembly/rev_s3/draft"
SOURCE = ROOT / "tools/package_rev_s3_release.py"


def load_parts():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "LCSC_DATABASE"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise RuntimeError("LCSC_DATABASE missing")


def main():
    parts = load_parts()
    board = pcbnew.LoadBoard(str(BOARD))
    bom = []
    cpl = []
    for fp in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
        ref = fp.GetReference()
        footprint = fp.GetFPIDAsString()
        if ref.startswith(("H", "TP")) or "MountingHole" in footprint or "TestPoint" in footprint:
            continue
        if ref not in parts:
            raise RuntimeError(f"No sourcing record for {ref}")
        mpn, lcsc, package, maker, description, assembly = parts[ref]
        value = fp.GetValue()
        bom.append([value, ref, footprint, lcsc, mpn, maker, assembly, description])
        position = fp.GetPosition()
        cpl.append([
            ref, value, footprint,
            f"{pcbnew.ToMM(position.x):.3f}",
            f"{pcbnew.ToMM(position.y):.3f}",
            f"{fp.GetOrientation().AsDegrees():.1f}",
            "Bottom" if fp.IsFlipped() else "Top", assembly,
        ])
    if len({row[1] for row in bom}) != len(bom):
        raise RuntimeError("Duplicate designators")
    if len(bom) != len(cpl):
        raise RuntimeError("BOM/CPL count mismatch")
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "RevS3-PCBA-BOM-DRAFT.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "MPN", "Manufacturer", "Assembly", "Description"])
        writer.writerows(bom)
    with (OUT / "RevS3-PCBA-CPL-DRAFT.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer", "Assembly"])
        writer.writerows(cpl)
    unresolved = [row[1] for row in bom if row[3] == "TBD"]
    print(f"Draft: {len(bom)} components, {sum(row[6] == 'SMT' for row in bom)} SMT, "
          f"{sum(row[6] == 'THT' for row in bom)} THT")
    print("Unresolved C-codes:", ", ".join(unresolved) or "none")
    print("Coordinates: native KiCad PCB mm; draft requires JLC placement preview")


if __name__ == "__main__":
    main()
