#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update report.docx to match current FreshVend engineering project:
- Dual-Tier Iris Aperture Escapement Dispensing Mechanism (replacing shaft-based)
- Actuators: 4x MG996R continuous-rotation servos
- Optical drop sensor: Active 38kHz modulated IR beam (TSOP38238 + 940nm LED)
- Custom PCBs: FV-CTRL_RevA (100x100mm THT) & FV-IR-RX_RevA daughterboards
- Power: 12V 40A PSU, dual XL4015 6V buck converters with PTC & 2200uF caps, MP1584EN 5V buck
- CAD: FreeCAD 1.1 3D parametric assembly & kinematics simulation (800 x 600 x 800 mm chassis)
"""

from pathlib import Path
import docx
from docx.shared import Pt, RGBColor

def update_report():
    doc = docx.Document(str(Path(__file__).resolve().parents[1] / "docs/archive/reva/report.docx"))
    print("Loaded report.docx successfully.")

    # -------------------------------------------------------------
    # 1. Update Pillar (2) in Section 3.1 Proposed Solutions (P[29])
    # -------------------------------------------------------------
    p29 = doc.paragraphs[29]
    p29.runs[0].text = "(2) Automated Dual-Tier Iris Aperture Dispensing Mechanism:"
    p29.runs[1].text = (
        " Integrates an automated dual-tier servo-driven iris aperture escapement mechanism per column "
        "(engineered specifically for standard plastic fruit bowls: 170 mm rim diameter, 60 mm height, 850 ml volume). "
        "Each vertical column features two stacked iris gates: Mechanism 1 (Lower Gate at Z=200mm) and "
        "Mechanism 2 (Upper Gate at Z=260mm), actuated by high-torque MG996R continuous-rotation servos. "
        "Dispensing executes on a strict FIFO cycle: upon payment confirmation, Mechanism 2 closes to firmly clamp the "
        "second bowl under its rim and support the upper stack; Mechanism 1 then opens to release the bottom-most bowl into "
        "a low-friction chute; an active 38kHz modulated infrared optical gate verifies positive bowl drop; Mechanism 1 closes "
        "back to 135 mm standby aperture; and Mechanism 2 opens to allow the upper stack to advance downward by one bowl height (60 mm) "
        "onto Mechanism 1. This prevents mechanical jamming and fruit deformation while ensuring 100% automated FIFO stock rotation."
    )
    print("Updated P[29] (Proposed Solutions - Pillar 2)")

    # -------------------------------------------------------------
    # 2. Update Flow 1 Steps 4 & 5 (P[60] & P[61])
    # -------------------------------------------------------------
    p60 = doc.paragraphs[60]
    p60.runs[0].text = "Step 4:"
    p60.runs[1].text = (
        " Upon payment confirmation, the ESP32 controller initiates the dual-tier iris dispensing cycle: "
        "Mechanism 2 (Upper Iris) rotates closed to clamp bowl #2 beneath its 170 mm rim flange, securing the upper stack; "
        "Mechanism 1 (Lower Iris) then rotates open to a 185 mm clear aperture, releasing bowl #1 to fall freely under gravity."
    )

    p61 = doc.paragraphs[61]
    p61.runs[0].text = "Step 5:"
    p61.runs[1].text = (
        " As bowl #1 falls, it interrupts an active 38kHz modulated optical gate (TSOP38238 receiver opposite 940nm LED), "
        "positively confirming the drop event. Mechanism 1 re-closes to standby (135 mm aperture); Mechanism 2 opens to 185 mm, "
        "allowing the upper stack to advance downward by 60 mm onto Mechanism 1 (preserving strict FIFO order). The bowl slides "
        "down the 22° chute into the front customer retrieval compartment."
    )
    print("Updated P[60] & P[61] (Main Flow 1: Steps 4 & 5)")

    # -------------------------------------------------------------
    # 3. Update Non-Functional Requirements: Jam rate & Frame size (P[98])
    # -------------------------------------------------------------
    p98 = doc.paragraphs[98]
    p98.runs[0].text = (
        "The automated dual-tier iris dispensing mechanism must maintain a failure/jam rate of less than 1% across all "
        "operational cycles, with a single-bowl drop cycle completed in under 3.5 seconds. "
        "The machine enclosure measures 800 mm (Width) x 600 mm (Depth) x 800 mm (Height), built from 3030 T-slot aluminum "
        "extrusions, housing 2 vertical dispensing columns (holding up to 30 bowls total), dual-tier iris modules, and electronics bay."
    )
    print("Updated P[98] (Non-Functional Requirements)")

    # -------------------------------------------------------------
    # 4. Update Section 3.5.2: IoT & Hardware Architecture (P[119]-P[121])
    # -------------------------------------------------------------
    p119 = doc.paragraphs[119]
    p119.runs[0].text = "IoT & Hardware Architecture:"

    p120 = doc.paragraphs[120]
    p120.runs[0].text = "Microcontroller & Actuators:"
    p120.runs[1].text = (
        " ESP32 DevKit V1 38-pin module (dual-core 240MHz, Wi-Fi & BLE), socketed via female headers on custom mainboard. "
        "Actuation is powered by 4x MG996R continuous-rotation (360°) metal-gear servos (2 servos per column: Upper & Lower Iris), "
        "delivering 11 kg·cm stall torque at 6.0V to drive the 3D-printed iris rotor rings via pushrod linkages."
    )

    p121 = doc.paragraphs[121]
    p121.runs[0].text = "Power, Sensors & Custom PCBs:"
    p121.runs[1].text = (
        " Powered by a 12V 40A (480W) industrial switching power supply. Features dual XL4015 DC-DC Buck modules (6.0V, >=5A each) "
        "dedicated to servo rails with resettable PTC fuses (~2.5A stall rating) and 2200µF bulk decoupling capacitors; and an MP1584EN "
        "Buck module (5.0V, 3A) for ESP32 logic isolation. Detection uses 2x active 38kHz modulated optical gates (TSOP38238 / VS1838B "
        "receivers paired with TSAL6200 940nm LEDs driven in burst mode via S8050 transistor) for ambient-light immune drop verification; "
        "DHT22 digital sensor for cold-chain monitoring; and 4x limit switches (DNP/optional). Electronics are fabricated on custom "
        "production-ready 2-layer KiCad PCBs: mainboard FV-CTRL_RevA (100x100mm THT, with 5A fuse, SS54 reverse polarity protection, "
        "SMAJ15A TVS diode, and 10k servo PWM pull-down resistors) and sensor daughterboards FV-IR-RX_RevA. 3D mechanical assemblies and "
        "kinematics simulations are designed in FreeCAD 1.1."
    )
    print("Updated P[119]-P[121] (Technology Stack - IoT & Hardware)")

    # -------------------------------------------------------------
    # 5. Update Section 3.5.3: Automated Hardware Controller (P[130])
    # -------------------------------------------------------------
    p130 = doc.paragraphs[130]
    p130.runs[0].text = "Automated Hardware & Mechanical Controller:"
    p130.runs[1].text = (
        " Complete hardware design and manufacturing package, including KiCad 10 production files (Gerber Rev A, drill, BOM with MPNs, "
        "schematics) for FV-CTRL_RevA mainboard and FV-IR-RX_RevA sensor daughterboards; ESP32 FreeRTOS firmware implementing dual-tier "
        "iris interlock state machines, 38kHz optical drop verification, and cold-chain telemetry; and full FreeCAD 3D CAD parametric assemblies "
        "(FreshVend_Machine_3D.FCStd, STEP, and STL files) for the 800x600x800mm chassis and iris escapement mechanisms."
    )
    print("Updated P[130] (Products - Automated Hardware Controller)")

    # -------------------------------------------------------------
    # 6. Update Task Package 2 (P[135] & P[144])
    # -------------------------------------------------------------
    p135 = doc.paragraphs[135]
    p135.runs[0].text = "Task Package 2:"
    p135.runs[1].text = (
        " IoT Hardware, Mechanical & Firmware Integration (FreeCAD 3D modeling, dual-tier iris mechanism fabrication, "
        "MG996R servo actuation calibration, FV-CTRL_RevA PCB bring-up, and ESP32 edge-to-cloud communication)."
    )

    p144 = doc.paragraphs[144]
    p144.runs[0].text = "Task Package 2: IoT Hardware, Mechanical & Firmware Integration"
    p144.runs[1].text = (
        " – Designing the 3D mechanical enclosure (800x600x800mm) and dual-tier iris aperture dispensing mechanism in FreeCAD; "
        "fabricating 3D-printed iris blades, rotor rings, and column guides; designing, fabricating, and assembling the FV-CTRL_RevA KiCad "
        "control PCB and FV-IR-RX_RevA optical sensor boards; calibrating MG996R continuous-rotation servos; and developing robust ESP32 "
        "firmware governing FIFO escapement sequencing, 38kHz optical drop verification, jam protection, and cloud telemetry."
    )
    print("Updated P[135] & P[144] (Task Package 2)")

    # -------------------------------------------------------------
    # 7. Update Section 4: Other Comments (P[156])
    # -------------------------------------------------------------
    p156 = doc.paragraphs[156]
    # Update runs in p156
    p156.text = (
        "This capstone project is a direct engineering extension and practical application of the team's research into "
        "\"Automated Retail Systems and IoT-Based Cold Chain Stability for Perishable Goods.\" "
        "The project prototype introduces a core mechanical innovation: replacing failure-prone spiral coils with a dual-tier "
        "servo-driven iris aperture escapement mechanism. Standard commercial vending coils deform or jam 170 mm wide disposable "
        "plastic fruit bowls; FreshVend's 6-blade iris aperture provides 360-degree radial support under the rim flange. "
        "Coordinated with active 38kHz optical drop verification and an isolated multi-rail power architecture (FV-CTRL_RevA PCB), "
        "the physical prototype delivers 100% automated First-In-First-Out (FIFO) stock rotation while preserving fruit integrity and "
        "cold-chain stability for unattended smart campus retail."
    )
    print("Updated P[156] (Section 4 Other Comments)")

    doc.save(str(Path(__file__).resolve().parents[1] / "docs/archive/reva/report.docx"))
    print("\nSUCCESS: Saved updated report.docx successfully!")

if __name__ == "__main__":
    update_report()
