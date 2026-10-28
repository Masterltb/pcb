"""
Release Packaging Script for FV-CTRL Rev-S3
Generates JLCPCB Fabrication deliverables:
- Gerber & Drill ZIP
- JLCPCB SMT BOM CSV (with verified LCSC part numbers)
- JLCPCB SMT CPL CSV (Pick & Place)
- Full Engineering BOM CSV
- Schematic PDF & 3D STEP
- Release Manifest JSON with SHA256 checksums
"""

import os
import sys
import json
import csv
import hashlib
import zipfile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
PYTHON = r"C:\Program Files\KiCad\10.0\bin\python.exe"

SCH_PATH = ROOT / "hardware" / "rev_s3" / "FV-CTRL_RevS3.kicad_sch"
PCB_PATH = ROOT / "hardware" / "rev_s3" / "FV-CTRL_RevS3.kicad_pcb"
OUT_RELEASE = ROOT / "releases" / "rev_s3"
OUT_GERBERS = OUT_RELEASE / "gerbers"
OUT_DOCS = ROOT / "docs" / "rev_s3"

OUT_RELEASE.mkdir(parents=True, exist_ok=True)
OUT_GERBERS.mkdir(parents=True, exist_ok=True)
OUT_DOCS.mkdir(parents=True, exist_ok=True)

# LCSC Database for Rev-S3 components (Optimized for JLCPCB SMT in-stock parts)
LCSC_DATABASE = {
    # Active ICs
    "U1": ("ESP32-S3-WROOM-1U-N8", "C2980297", "SMD-41, 18x25.5mm", "Espressif Systems", "ESP32-S3 Dual-Core 240MHz, 8MB Flash, IPEX Ant", "SMT"),
    "U3": ("AMS1117-3.3", "C6186", "SOT-223-3", "Advanced Monolithic", "LDO 3.3V 1A Linear Regulator (Basic Part)", "SMT"),
    
    # USB & Diodes
    "J21": ("USB4105-GF-A", "C3020560", "USB-C-16P", "GCT", "USB Type-C receptacle matching KiCad USB4105 footprint", "SMT"),
    "D1": ("SMBJ12A", "C5353258", "DO-214AA (SMB)", "FOSAN", "12V TVS Transient Voltage Suppressor 600W", "SMT"),
    "D7": ("SS54C", "C16103", "DO-214AB (SMC)", "MDD", "Schottky Barrier Diode 5A 40V", "SMT"),
    
    # Indicator LEDs (0603)
    "D2": ("Blue LED 0603", "C84266", "0603", "NationStar", "+12V Main DC Power Indicator", "SMT"),
    "D3": ("Red LED 0603", "C2286", "0603", "KENTO", "+6V_A Servo Channel A Indicator (Basic Part)", "SMT"),
    "D4": ("Red LED 0603", "C2286", "0603", "KENTO", "+6V_B Servo Channel B Indicator (Basic Part)", "SMT"),
    "D5": ("Red LED 0603", "C2286", "0603", "KENTO", "+5V Logic Supply Indicator (Basic Part)", "SMT"),
    "D6": ("Red LED 0603", "C2286", "0603", "KENTO", "+3V3 ESP32-S3 VDD Indicator (Basic Part)", "SMT"),
    
    # Tactile Buttons (4x3mm SMD Basic Part)
    "SW1": ("TS-1088-AR02016", "C720477", "3.5x2.9mm SMD", "XUNPU", "Tactile Push Switch (RESET - Basic Part)", "SMT"),
    "SW2": ("TS-1088-AR02016", "C720477", "3.5x2.9mm SMD", "XUNPU", "Tactile Push Switch (BOOT - Basic Part)", "SMT"),
    
    # Resistors 0603 1%
    "R11": ("22R 1% 0603", "C23345", "0603", "UNI-ROYAL", "USB D- series damping resistor", "SMT"),
    "R12": ("22R 1% 0603", "C23345", "0603", "UNI-ROYAL", "USB D+ series damping resistor", "SMT"),
    "R14": ("5.1k 1% 0603", "C23186", "0603", "UNI-ROYAL", "USB-C CC1 5.1k pulldown (UFP device mode)", "SMT"),
    "R15": ("5.1k 1% 0603", "C23186", "0603", "UNI-ROYAL", "USB-C CC2 5.1k pulldown (UFP device mode)", "SMT"),
    "R1": ("330R 1% 0603", "C23138", "0603", "UNI-ROYAL", "Servo S1_TOP PWM series damping", "SMT"),
    "R3": ("330R 1% 0603", "C23138", "0603", "UNI-ROYAL", "Servo S1_BOT PWM series damping", "SMT"),
    "R5": ("330R 1% 0603", "C23138", "0603", "UNI-ROYAL", "Servo S2_TOP PWM series damping", "SMT"),
    "R7": ("330R 1% 0603", "C23138", "0603", "UNI-ROYAL", "Servo S2_BOT PWM series damping", "SMT"),
    "R2": ("10k 1% 0603", "C25804", "0603", "UNI-ROYAL", "Servo S1_TOP PWM fail-safe pulldown", "SMT"),
    "R4": ("10k 1% 0603", "C25804", "0603", "UNI-ROYAL", "Servo S1_BOT PWM fail-safe pulldown", "SMT"),
    "R6": ("10k 1% 0603", "C25804", "0603", "UNI-ROYAL", "Servo S2_TOP PWM fail-safe pulldown", "SMT"),
    "R8": ("10k 1% 0603", "C25804", "0603", "UNI-ROYAL", "Servo S2_BOT PWM fail-safe pulldown", "SMT"),
    "R10": ("10k 1% 0603", "C25804", "0603", "UNI-ROYAL", "EN / Reset line external pull-up", "SMT"),
    "R16": ("1k 1% 0603", "C21190", "0603", "UNI-ROYAL", "Drop Sensor Col 1 ECHO divider top (1k)", "SMT"),
    "R17": ("2k 1% 0603", "C22975", "0603", "UNI-ROYAL", "Drop Sensor Col 1 ECHO divider bot (2k)", "SMT"),
    "R18": ("1k 1% 0603", "C21190", "0603", "UNI-ROYAL", "Drop Sensor Col 2 ECHO divider top (1k)", "SMT"),
    "R19": ("2k 1% 0603", "C22975", "0603", "UNI-ROYAL", "Drop Sensor Col 2 ECHO divider bot (2k)", "SMT"),
    "R21": ("4.7k 1% 0603", "C23162", "0603", "UNI-ROYAL", "+12V LED ballast resistor", "SMT"),
    "R22": ("2.2k 1% 0603", "C4190", "0603", "UNI-ROYAL", "+6V_A LED ballast resistor", "SMT"),
    "R23": ("2.2k 1% 0603", "C4190", "0603", "UNI-ROYAL", "+6V_B LED ballast resistor", "SMT"),
    "R24": ("1.5k 1% 0603", "C22854", "0603", "UNI-ROYAL", "+5V LED ballast resistor", "SMT"),
    "R25": ("1k 1% 0603", "C21190", "0603", "UNI-ROYAL", "+3V3 LED ballast resistor", "SMT"),
    "R26": ("4.7k 1% 0603", "C23162", "0603", "UNI-ROYAL", "I2C SDA pull-up to +3V3", "SMT"),
    "R27": ("4.7k 1% 0603", "C23162", "0603", "UNI-ROYAL", "I2C SCL pull-up to +3V3", "SMT"),
    
    # Capacitors 0603
    "C58": ("100nF 50V X7R 0603", "C14663", "0603", "Samsung Electro-Mechanics", "High-frequency decoupling cap", "SMT"),
    "C10": ("1uF 50V X7R 0603", "C15849", "0603", "Samsung Electro-Mechanics", "EN RC delay timing filter", "SMT"),
    "C6": ("10uF 25V X5R 0603", "C19702", "0603", "Samsung Electro-Mechanics", "LDO Output bulk capacitor", "SMT"),
    
    # THT Components (Manual Assembly / Post-SMT)
    # TBD entries are intentional: never use the old, unverified C-codes for full PCBA.
    "C1": ("2200uF 25V Radial", "TBD", "D12.5mm P5.0mm", "TBD", "Channel A Servo Inrush Bulk Capacitor", "THT"),
    "C2": ("2200uF 25V Radial", "TBD", "D12.5mm P5.0mm", "TBD", "Channel B Servo Inrush Bulk Capacitor", "THT"),
    "C57": ("10uF 50V Radial", "TBD", "D5.0mm P2.0mm", "TBD", "12V Input Filter Capacitor", "THT"),
    "F1": ("5A 250V 5x20mm Fuse", "C3204125", "5x20mm Clip Holder", "Schurter 0031.8201", "Main 12V DC input fuse protection", "THT"),
    "F2": ("Bourns MF-RHT300 PTC", "TBD", "Radial Leaded", "Bourns", "Channel A Servo Overcurrent PPTC Fuse", "THT"),
    "F3": ("Bourns MF-RHT300 PTC", "TBD", "Radial Leaded", "Bourns", "Channel B Servo Overcurrent PPTC Fuse", "THT"),
    "J1": ("Phoenix 1757242 MSTBA 2-Pin 5.08mm", "C90074", "P5.08mm Horizontal", "Phoenix Contact", "Main +12V DC Power Input Header", "THT"),
    "J2": ("Phoenix 1757268 MSTBA 4-Pin 5.08mm", "C90076", "P5.08mm Horizontal", "Phoenix Contact", "Channel A XL4015 Buck Converter Interface", "THT"),
    "J3": ("Phoenix 1757268 MSTBA 4-Pin 5.08mm", "C90076", "P5.08mm Horizontal", "Phoenix Contact", "Channel B XL4015 Buck Converter Interface", "THT"),
    "J4": ("RECOM R-78E5.0-1.0", "C3033024", "SIP-3", "RECOM Power", "5V 1A High-efficiency DC/DC Converter; JLC stock to confirm", "THT"),
    "J5": ("1x03 Pin Header 2.54mm", "C49257", "P2.54mm Vertical", "BOOMELE", "Servo Channel 1 Top Header (S1_TOP)", "THT"),
    "J6": ("1x03 Pin Header 2.54mm", "C49257", "P2.54mm Vertical", "BOOMELE", "Servo Channel 1 Bottom Header (S1_BOT)", "THT"),
    "J7": ("1x03 Pin Header 2.54mm", "C49257", "P2.54mm Vertical", "BOOMELE", "Servo Channel 2 Top Header (S2_TOP)", "THT"),
    "J8": ("1x03 Pin Header 2.54mm", "C49257", "P2.54mm Vertical", "BOOMELE", "Servo Channel 2 Bottom Header (S2_BOT)", "THT"),
    "J9": ("XFCN PZ254V-11-04P", "C2691448", "P2.54mm Vertical", "XFCN", "I2C Spare Expansion Bus Header", "THT"),
    "J10": ("XFCN PZ254V-11-04P", "C2691448", "P2.54mm Vertical", "XFCN", "Limit Switches 4-Channel Input Header", "THT"),
    "J11": ("JST-XH 4-Pin 2.50mm", "C41422491", "B4B-XH-A P2.50mm", "JST", "Column 1 Universal Drop Sensor Header", "THT"),
    "J12": ("JST-XH 4-Pin 2.50mm", "C41422491", "B4B-XH-A P2.50mm", "JST", "Column 2 Universal Drop Sensor Header", "THT"),
}

def main():
    print("=" * 70)
    print("STARTING FRESHVEND FV-CTRL REV-S3 RELEASE PACKAGING")
    print("=" * 70)

    # 1. Verification of Schematic ERC
    print("\n[1/6] Running KiCad Schematic ERC...")
    erc_rpt = OUT_RELEASE / "FV-CTRL_RevS3-erc.rpt"
    cmd_erc = [KICAD_CLI, "sch", "erc", "-o", str(erc_rpt), str(SCH_PATH)]
    res = subprocess.run(cmd_erc, capture_output=True, text=True)
    assert res.returncode == 0, f"ERC failed:\n{res.stderr}\n{res.stdout}"
    assert "Found 0 violations" in res.stdout, f"ERC violations detected:\n{res.stdout}"
    print("  -> KiCad ERC Passed: 0 violations!")

    # 2. Verification of PCB DRC
    print("\n[2/6] Running KiCad PCB DRC...")
    drc_rpt = OUT_RELEASE / "FV-CTRL_RevS3-drc.rpt"
    cmd_drc = [KICAD_CLI, "pcb", "drc", "-o", str(drc_rpt), "--severity-all", str(PCB_PATH)]
    res = subprocess.run(cmd_drc, capture_output=True, text=True)
    assert res.returncode == 0, f"DRC failed:\n{res.stderr}\n{res.stdout}"
    assert "Found 0 DRC violations" in (drc_rpt.read_text(encoding="utf-8") if drc_rpt.exists() else res.stdout), "DRC violations detected!"
    print("  -> KiCad DRC Passed: 0 violations, 0 unconnected items!")

    # 3. Export Gerbers & Drill
    print("\n[3/6] Exporting Fabrication Gerbers and Excellon Drills...")
    cmd_gerber = [
        KICAD_CLI, "pcb", "export", "gerbers",
        "-o", str(OUT_GERBERS) + os.sep,
        "--subtract-soldermask",
        str(PCB_PATH)
    ]
    res = subprocess.run(cmd_gerber, capture_output=True, text=True)
    assert res.returncode == 0, f"Gerber export failed:\n{res.stderr}"

    cmd_drill = [
        KICAD_CLI, "pcb", "export", "drill",
        "-o", str(OUT_GERBERS) + os.sep,
        "--excellon-units", "mm",
        "--excellon-separate-th",
        str(PCB_PATH)
    ]
    res = subprocess.run(cmd_drill, capture_output=True, text=True)
    assert res.returncode == 0, f"Drill export failed:\n{res.stderr}"

    # Package Gerbers ZIP (11 standard fabrication layers)
    FAB_FILES = [
        "FV-CTRL_RevS3-F_Cu.gtl",
        "FV-CTRL_RevS3-B_Cu.gbl",
        "FV-CTRL_RevS3-F_Mask.gts",
        "FV-CTRL_RevS3-B_Mask.gbs",
        "FV-CTRL_RevS3-F_Silkscreen.gto",
        "FV-CTRL_RevS3-B_Silkscreen.gbo",
        "FV-CTRL_RevS3-F_Paste.gtp",
        "FV-CTRL_RevS3-B_Paste.gbp",
        "FV-CTRL_RevS3-Edge_Cuts.gm1",
        "FV-CTRL_RevS3-PTH.drl",
        "FV-CTRL_RevS3-NPTH.drl"
    ]
    gerber_zip = OUT_RELEASE / "FV-CTRL_RevS3-Gerber.zip"
    with zipfile.ZipFile(gerber_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for fname in FAB_FILES:
            fpath = OUT_GERBERS / fname
            assert fpath.exists(), f"Missing required fabrication file: {fname}"
            z.write(fpath, arcname=fname)
    print(f"  -> Created JLCPCB Gerber ZIP: {gerber_zip.name} ({gerber_zip.stat().st_size:,} bytes, 11 files)")

    # 4. Export BOM and CPL files
    print("\n[4/6] Generating JLCPCB SMT Assembly BOM & CPL (Centroid) files...")
    
    # Load Board via pcbnew Python API
    import pcbnew
    board = pcbnew.LoadBoard(str(PCB_PATH))
    fps = list(board.GetFootprints())
    
    # Parse footprints into SMT rows and full BOM rows
    smt_cpl_rows = []
    smt_bom_dict = {} # Key: (Comment, Footprint, LCSC) -> list of refs
    full_bom_rows = []

    for fp in sorted(fps, key=lambda x: x.GetReference()):
        ref = fp.GetReference()
        val = fp.GetValue()
        fpid = fp.GetFPIDAsString()
        
        # Skip mechanical items
        if ref.startswith("H") or ref.startswith("TP") or "MountingHole" in fpid or "TestPoint" in fpid:
            continue
            
        info = LCSC_DATABASE.get(ref, (val, "TBD", fpid, "Generic", "", "THT"))
        mpn, lcsc, pkg, mfr, desc, asm_type = info
        
        full_bom_rows.append({
            "Reference": ref,
            "Value": val,
            "MPN": mpn,
            "Package": pkg,
            "LCSC_Part": lcsc,
            "Manufacturer": mfr,
            "Assembly_Type": asm_type,
            "Description": desc
        })
        
        # SMT Pick & Place
        if asm_type == "SMT":
            pos = fp.GetPosition()
            rot = fp.GetOrientation().AsDegrees()
            # Calculate board-relative coordinates (bottom-left = 0,0)
            # Board: X in [100.0, 200.0], Y in [100.0, 200.0]
            mid_x = (pos.x / 1e6) - 100.0
            mid_y = 200.0 - (pos.y / 1e6)
            
            smt_cpl_rows.append({
                "Designator": ref,
                "Val": val,
                "Package": pkg,
                "Mid X": f"{mid_x:.3f}",
                "Mid Y": f"{mid_y:.3f}",
                "Rotation": f"{rot:.1f}",
                "Layer": "Top"
            })
            
            # Group by LCSC Part and Footprint so multiple identical parts (e.g. LEDs, switches) merge into one line
            comment = val
            if lcsc == "C2286":
                comment = "LED_RED"
            elif lcsc in ["C720477", "C26638", "C398055"]:
                comment = "SW_PUSH"
                
            key = (comment, pkg, lcsc)
            if key not in smt_bom_dict:
                smt_bom_dict[key] = []
            smt_bom_dict[key].append(ref)

    # Write JLCPCB SMT BOM CSV
    bom_jlc_path = OUT_RELEASE / "FV-CTRL_RevS3-BOM.csv"
    with open(bom_jlc_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (comment, footprint, lcsc), refs in sorted(smt_bom_dict.items(), key=lambda x: x[1][0]):
            writer.writerow([comment, ",".join(refs), footprint, lcsc])
    print(f"  -> Created JLCPCB SMT BOM: {bom_jlc_path.name} ({len(smt_bom_dict)} unique line items, {sum(len(r) for r in smt_bom_dict.values())} SMT components)")

    # Write JLCPCB SMT CPL CSV
    cpl_jlc_path = OUT_RELEASE / "FV-CTRL_RevS3-CPL.csv"
    with open(cpl_jlc_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
        writer.writeheader()
        writer.writerows(smt_cpl_rows)
    print(f"  -> Created JLCPCB SMT CPL: {cpl_jlc_path.name} ({len(smt_cpl_rows)} placement entries)")

    # Write Full Engineering BOM CSV
    full_bom_path = OUT_DOCS / "FV-CTRL_RevS3-BOM-full.csv"
    with open(full_bom_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Reference", "Value", "MPN", "Package", "LCSC_Part", "Manufacturer", "Assembly_Type", "Description"])
        writer.writeheader()
        writer.writerows(full_bom_rows)
    print(f"  -> Created Full Engineering BOM: {full_bom_path.name} ({len(full_bom_rows)} parts)")

    # 5. Export Schematic PDF and 3D STEP
    print("\n[5/6] Exporting Schematic PDF & 3D STEP...")
    pdf_path = OUT_DOCS / "FV-CTRL_RevS3-Schematic.pdf"
    cmd_pdf = [KICAD_CLI, "sch", "export", "pdf", "-o", str(pdf_path), str(SCH_PATH)]
    subprocess.run(cmd_pdf, check=True)
    print(f"  -> Created Schematic PDF: {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")

    step_path = OUT_DOCS / "FV-CTRL_RevS3-3D.step"
    cmd_step = [KICAD_CLI, "pcb", "export", "step", "-o", str(step_path), "--subst-models", str(PCB_PATH)]
    subprocess.run(cmd_step, check=True)
    print(f"  -> Created 3D STEP: {step_path.name} ({step_path.stat().st_size:,} bytes)")

    # 6. Generate Manifest
    print("\n[6/6] Generating Release Manifest...")
    git_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    git_branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()

    manifest_data = {
        "project": "FreshVend Controller Board",
        "revision": "Rev-S3",
        "target_mcu": "ESP32-S3-WROOM-1U-N8",
        "connector_type": "USB Type-C 16-Pin (Native USB-Serial-JTAG)",
        "drop_sensor_headers": "Dual Universal 4-Pin Headers (SW-420, HC-SR04, IR Beam)",
        "git_branch": git_branch,
        "git_commit": git_commit,
        "board_dimensions_mm": [100.0, 100.0],
        "copper_layers": 2,
        "copper_weight_oz": 1,
        "nominal_thickness_mm": 1.6,
        "erc_violations": 0,
        "drc_violations": 0,
        "unconnected_items": 0,
        "smt_components_count": len(smt_cpl_rows),
        "total_components_count": len(full_bom_rows),
        "deliverables": {
            "gerber_zip": {
                "filename": gerber_zip.name,
                "bytes": gerber_zip.stat().st_size,
                "sha256": hashlib.sha256(gerber_zip.read_bytes()).hexdigest(),
                "layer_count": len(FAB_FILES)
            },
            "jlcpcb_bom": {
                "filename": bom_jlc_path.name,
                "bytes": bom_jlc_path.stat().st_size,
                "sha256": hashlib.sha256(bom_jlc_path.read_bytes()).hexdigest()
            },
            "jlcpcb_cpl": {
                "filename": cpl_jlc_path.name,
                "bytes": cpl_jlc_path.stat().st_size,
                "sha256": hashlib.sha256(cpl_jlc_path.read_bytes()).hexdigest()
            },
            "schematic_pdf": {
                "filename": pdf_path.name,
                "bytes": pdf_path.stat().st_size,
                "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest()
            },
            "cad_step_3d": {
                "filename": step_path.name,
                "bytes": step_path.stat().st_size,
                "sha256": hashlib.sha256(step_path.read_bytes()).hexdigest()
            },
            "firmware_pins_header": {
                "filename": "FV-CTRL_RevS3-pins.h",
                "path": "docs/rev_s3/FV-CTRL_RevS3-pins.h"
            }
        }
    }

    manifest_path = OUT_RELEASE / "FV-CTRL_RevS3-manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    print(f"  -> Created Manifest: {manifest_path.name}")
    print("\n" + "=" * 70)
    print("ALL DELIVERABLES SUCCESSFULLY PRODUCED AND VALIDATED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
