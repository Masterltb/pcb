import json
import shutil
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / "hardware/archive/reva"
DOCS = ROOT / "docs/archive/reva"
REPORTS = ROOT / "reports/archive/reva"

class CodeGenerationTests(unittest.TestCase):
    def test_pipeline_audit_and_generation(self):
        """Test full pipeline audit stage, verifying all artifacts are generated."""
        res = subprocess.run([sys.executable, "tools/fv_pipeline.py", "audit"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Pipeline audit failed:\n{res.stdout}\n{res.stderr}")

        self.assertTrue((DOCS / "audit-revA.md").exists(), "audit-revA.md must exist")
        self.assertTrue((DOCS / "requirements-and-blockers.md").exists(), "requirements-and-blockers.md must exist")
        self.assertTrue((HARDWARE / "FV-CTRL_RevA.kicad_sch").exists(), "FV-CTRL_RevA.kicad_sch must exist")
        self.assertTrue((HARDWARE / "FV-CTRL_RevA.manifest.json").exists(), "FV-CTRL_RevA.manifest.json must exist")
        self.assertTrue((HARDWARE / "FV-CTRL_RevA.net.json").exists(), "FV-CTRL_RevA.net.json must exist")
        self.assertTrue((HARDWARE / "FV-IR-RX_RevA.kicad_sch").exists(), "FV-IR-RX_RevA.kicad_sch must exist")
        self.assertTrue((HARDWARE / "FV-IR-RX_RevA.manifest.json").exists(), "FV-IR-RX_RevA.manifest.json must exist")
        self.assertTrue((DOCS / "FV-CTRL_RevA-bom-draft.md").exists(), "FV-CTRL_RevA-bom-draft.md must exist")

    def test_native_schematic_structure(self):
        """Test native KiCad 10 schematic content, symbols, and net definitions."""
        sch_path = HARDWARE / "FV-CTRL_RevA.kicad_sch"
        self.assertTrue(sch_path.exists())
        content = sch_path.read_text(encoding="utf-8")

        # Verify KiCad S-expression header
        self.assertIn("(kicad_sch", content)
        self.assertIn('(paper "A3")', content)
        self.assertIn("(lib_symbols", content)

        # Verify key functional blocks
        self.assertIn("1. POWER INPUT & 12V PROTECTION", content)
        self.assertIn("2. STEP-DOWN BUCK CONVERTERS", content)
        self.assertIn("3. SERVO POWER PROTECTION & CONNECTORS", content)
        self.assertIn("4. ESP32 DEVKIT 38 HEADER INTERFACE", content)
        self.assertIn("5. IR TRANSMITTER DRIVER CIRCUIT", content)
        self.assertIn("6. IR RECEIVER HEADERS", content)
        self.assertIn("7. LIMIT SWITCHES", content)
        self.assertIn("8. DIAGNOSTICS & RAIL DECOUPLING", content)

        # Verify required symbols
        required_symbols = [
            "J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9", "J10",
            "J11", "J12", "J13", "J14", "J15", "J16", "J17",
            "J18", "J19",
            "F1", "F2", "F3", "Q1", "Q2", "D1",
            "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R13", "R14", "R15",
            "C1", "C2", "C3", "C4", "C5", "C6",
            "TP1", "TP2", "TP3", "TP4", "TP5", "TP6", "TP7", "TP8"
        ]
        for ref in required_symbols:
            self.assertIn(f'(property "Reference" "{ref}"', content, f"Missing symbol reference: {ref}")

        # Verify required nets
        required_nets = [
            "+12V_IN", "+12V", "+6V_A", "+6V_B", "+5V", "+3V3",
            "S1_TOP_PWM", "S1_BOT_PWM", "S2_TOP_PWM", "S2_BOT_PWM",
            "IR_RX1", "IR_RX2", "LS1", "LS2", "LS3", "LS4",
            "I2C_SDA", "I2C_SCL"
        ]
        for net in required_nets:
            self.assertIn(f'(label "{net}"', content, f"Missing label for net: {net}")
        self.assertIn('(lib_id "power:GND")', content, "Missing power:GND power symbol in schematic")

    def test_manifest_integrity(self):
        """Verify machine-readable manifest completeness."""
        manifest_path = HARDWARE / "FV-CTRL_RevA.manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        components = {c["ref"]: c for c in manifest["components"]}
        nets = manifest["nets"]

        self.assertIn("F1", components)
        self.assertIn("Q1", components)
        self.assertIn("D1", components)
        self.assertIn("F2", components)
        self.assertIn("F3", components)
        self.assertIn("J18", components)
        self.assertIn("J19", components)

        for net in ["+12V_IN", "+12V", "+6V_A", "+6V_B", "+5V", "+3V3", "GND",
                    "S1_TOP_PWM", "S1_BOT_PWM", "S2_TOP_PWM", "S2_BOT_PWM", "IR_RX1", "IR_RX2"]:
            self.assertIn(net, nets)
            self.assertGreater(len(nets[net]["nodes"]), 1, f"Net {net} must connect at least 2 nodes")

    def test_kicad_erc_execution(self):
        """Run KiCad 10 CLI ERC on the generated native schematic and verify 0 violations."""
        if shutil.which("kicad-cli") is None:
            self.skipTest("kicad-cli not found in PATH")

        REPORTS.mkdir(exist_ok=True)
        erc_rpt = REPORTS / "erc.rpt"
        erc_json = REPORTS / "erc.json"

        cmd = [
            "kicad-cli", "sch", "erc",
            "--severity-all",
            "--format", "json",
            "--output", str(erc_json),
            str(HARDWARE / "FV-CTRL_RevA.kicad_sch")
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"kicad-cli sch erc returned {res.returncode}:\n{res.stdout}\n{res.stderr}")
        self.assertTrue(erc_json.exists())

        erc_data = json.loads(erc_json.read_text(encoding="utf-8"))
        violations = erc_data.get("violations", [])
        errors = [v for v in violations if v.get("severity") == "error"]
        self.assertEqual(len(errors), 0, f"ERC errors found: {errors}")

    def test_ir_rx_satellite_schematics(self):
        """Test satellite IR RX schematic structure, components, and ERC."""
        rx_path = HARDWARE / "FV-IR-RX_RevA.kicad_sch"
        self.assertTrue(rx_path.exists())
        content = rx_path.read_text(encoding="utf-8")

        # Verify key symbols
        self.assertIn('(property "Reference" "J1"', content)
        self.assertIn('(property "Reference" "R1"', content)
        self.assertIn('(property "Reference" "C1"', content)
        self.assertIn('(property "Reference" "U1"', content)

        # Verify nets
        self.assertIn('(label "+3V3_FILT"', content)
        self.assertIn('(label "IR_RX_OUT"', content)
        self.assertIn('(lib_id "power:GND")', content)

        # Verify manifest
        manifest_path = HARDWARE / "FV-IR-RX_RevA.manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        comp_refs = {c["ref"] for c in manifest["components"]}
        self.assertEqual(comp_refs, {"J1", "R1", "C1", "U1"})

        # Run ERC on satellite boards
        if shutil.which("kicad-cli") is not None:
            for sch in [HARDWARE / "FV-IR-RX_RevA.kicad_sch",
                        HARDWARE / "FV-IR-RX1_RevA.kicad_sch",
                        HARDWARE / "FV-IR-RX2_RevA.kicad_sch"]:
                out_rpt = REPORTS / f"erc_{sch.stem}.rpt"
                cmd = [
                    "kicad-cli", "sch", "erc",
                    "--severity-all",
                    "--format", "report",
                    "--output", str(out_rpt),
                    str(sch)
                ]
                res = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f"ERC failed on {sch.name}:\n{res.stdout}\n{res.stderr}")
                rpt_text = out_rpt.read_text(encoding="utf-8")
                self.assertIn("Errors 0  Warnings 0", rpt_text, f"ERC violations in {sch.name}:\n{rpt_text}")

    def test_native_pcb_generation_and_drc(self):
        """Verify native mainboard PCB generation and 0 DRC violations / 0 unconnected pads."""
        pcb_path = HARDWARE / "FV-CTRL_RevA.kicad_pcb"
        self.assertTrue(pcb_path.exists(), "FV-CTRL_RevA.kicad_pcb must exist")

        if shutil.which("kicad-cli") is not None:
            drc_rpt = REPORTS / "drc.rpt"
            cmd = [
                "kicad-cli", "pcb", "drc",
                "--severity-all",
                "--format", "report",
                "--output", str(drc_rpt),
                str(pcb_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"DRC failed on {pcb_path.name}:\n{res.stdout}\n{res.stderr}")
            rpt_text = drc_rpt.read_text(encoding="utf-8")
            self.assertIn("Found 0 DRC violations", rpt_text, f"DRC violations found:\n{rpt_text}")
            self.assertIn("Found 0 unconnected pads", rpt_text, f"Unconnected pads found:\n{rpt_text}")
            self.assertIn("Found 0 Footprint errors", rpt_text, f"Footprint errors found:\n{rpt_text}")

    def test_satellite_pcb_generation_and_drc(self):
        """Verify satellite IR RX board generation and 0 DRC violations."""
        for name in ["FV-IR-RX_RevA.kicad_pcb", "FV-IR-RX1_RevA.kicad_pcb", "FV-IR-RX2_RevA.kicad_pcb"]:
            pcb_path = HARDWARE / name
            self.assertTrue(pcb_path.exists(), f"{name} must exist")

            if shutil.which("kicad-cli") is not None:
                drc_rpt = REPORTS / f"drc_{pcb_path.stem}.rpt"
                cmd = [
                    "kicad-cli", "pcb", "drc",
                    "--severity-all",
                    "--format", "report",
                    "--output", str(drc_rpt),
                    str(pcb_path)
                ]
                res = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f"DRC failed on {name}:\n{res.stdout}\n{res.stderr}")
                rpt_text = drc_rpt.read_text(encoding="utf-8")
                self.assertIn("Found 0 DRC violations", rpt_text, f"DRC violations in {name}:\n{rpt_text}")
                self.assertIn("Found 0 unconnected pads", rpt_text, f"Unconnected pads in {name}:\n{rpt_text}")

    def test_gerber_export(self):
        """Verify Gerber and drill files exist and are populated."""
        gerber_dir = ROOT / "releases/archive/reva/gerbers" / "FV-CTRL_RevA"
        self.assertTrue(gerber_dir.exists(), "Gerbers directory must exist")
        gtl = gerber_dir / "FV-CTRL_RevA-F_Cu.gtl"
        gbl = gerber_dir / "FV-CTRL_RevA-B_Cu.gbl"
        drl = gerber_dir / "FV-CTRL_RevA.drl"
        self.assertTrue(gtl.exists() and gtl.stat().st_size > 0, "F_Cu Gerber must exist and be non-empty")
        self.assertTrue(gbl.exists() and gbl.stat().st_size > 0, "B_Cu Gerber must exist and be non-empty")
        self.assertTrue(drl.exists() and drl.stat().st_size > 0, "Drill file must exist and be non-empty")


if __name__ == "__main__":
    unittest.main()


