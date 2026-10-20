"""
Clean Zero-DRC Board Generator for FV-CTRL Rev A.
Fast O(1) via clearance lookup and exact vectorized segment clearance.
"""
import sys
from pathlib import Path
import json
import time
import numpy as np
import heapq

ROOT = Path(r"F:\project\repo-github\pcb\pcb")
sys.path.insert(0, str(ROOT))
KICAD_FP_DIR = Path("C:/Program Files/KiCad/10.0/share/kicad/footprints")

import pcbnew
PLACEMENTS = {
    # 1. 12V Power Input & Protection (Top-Left)
    "J1": (115.0, 107.0, 0),       # Terminal block 2-pin
    "F1": (124.0, 114.0, 0),       # Fuse 5x20mm horizontal
    "Q1": (115.0, 124.0, 0),       # TO-220 P-MOSFET
    "R9": (115.0, 130.0, 0),       # Gate pull-down
    "D1": (115.0, 136.0, 0),       # TVS Diode DO-201AD horizontal

    # Local 12V Diagnostics
    "R20": (108.0, 125.0, 90),     # 12V LED limit resistor vertical at left edge
    "D2":  (108.0, 112.0, 270),    # 12V LED
    "TP1": (108.0, 131.0, 0),      # +12V Test Point

    # 2. Step-Down Buck Converters
    "J2": (166.0, 123.0, 0),       # XH-M401 8A module (61x41mm: X=135.5..196.5, Y=102.5..143.5)
    "J4": (124.0, 149.0, 0),       # MP1584EN 3A module (22.1x16.8mm)
    "C5": (131.0, 139.0, 0),       # +5V decoupling 100nF
    "C6": (116.0, 142.0, 0),       # +3.3V decoupling 100nF

    # Local 5V Diagnostics
    "R23": (124.0, 134.0, 0),      # 5V LED limit resistor
    "D5":  (119.0, 134.0, 0),      # 5V LED (clear of D1 TVS)
    "TP4": (136.0, 130.0, 0),      # +5V Test Point

    # 3. Servo Power Protection & Bulk Caps (Right zone)
    "F2": (172.0, 148.0, 0),       # PTC Col 1 (powers S1)
    "F3": (186.0, 148.0, 0),       # PTC Col 2 (powers S2)
    "C1": (172.0, 156.0, 0),       # Bulk cap 2200uF Col 1 (D=12.5mm)
    "C2": (186.0, 156.0, 0),       # Bulk cap 2200uF Col 2 (D=12.5mm)
    "C3": (172.0, 164.0, 0),       # 100nF ceramic
    "C4": (186.0, 164.0, 0),       # 100nF ceramic

    # Local 6V-A and 6V-B Diagnostics
    "R21": (154.0, 146.0, 0),      # 6V-A LED limit
    "D3":  (154.0, 152.0, 0),      # 6V-A LED
    "TP2": (154.0, 140.0, 0),      # +6V_A Test Point

    "R22": (164.0, 146.0, 0),      # 6V-B LED limit
    "D4":  (164.0, 152.0, 0),      # 6V-B LED
    "TP3": (164.0, 140.0, 0),      # +6V_B Test Point

    # 4. Servo Connectors (Ordered: S2_BOT, S2_TOP, S1_BOT, S1_TOP)
    "J8": (194.0, 168.0, 0),       # S2-BOT
    "J7": (194.0, 175.0, 0),       # S2-TOP
    "J6": (194.0, 182.0, 0),       # S1-BOT
    "J5": (194.0, 189.0, 0),       # S1-TOP

    # 5. Servo PWM Resistors (Aligned with U2 pins!)
    "R4": (171.0, 168.0, 0),       # S2-BOT series
    "R8": (181.0, 168.0, 0),       # S2-BOT pulldown
    "R3": (171.0, 175.0, 0),       # S2-TOP series
    "R7": (181.0, 175.0, 0),       # S2-TOP pulldown
    "R2": (171.0, 182.0, 0),       # S1-BOT series
    "R6": (181.0, 182.0, 0),       # S1-BOT pulldown
    "R1": (171.0, 189.0, 0),       # S1-TOP series
    "R5": (181.0, 189.0, 0),       # S1-TOP pulldown

    # 6. ESP32-WROOM-32 SMD MCU & 3.3V LDO Subsystem
    "U2": (150.0, 178.0, 0),       # ESP32-WROOM-32 SMD HandSolder
    "U3": (138.0, 148.0, 270),     # AMS1117-3.3 SOT-223 LDO
    "C11": (130.0, 145.0, 0),      # 10uF 16V LDO input filter
    "C12": (144.0, 148.0, 0),      # 22uF 16V LDO output filter
    "C13": (149.0, 148.0, 0),      # 100nF high-freq decoupling

    # Local 3.3V Diagnostics
    "R24": (146.0, 142.0, 0),      # 3.3V LED limit
    "D6":  (146.0, 146.0, 0),      # 3.3V LED
    "TP5": (146.0, 150.0, 0),      # +3V3 Test Point

    # Expansion Headers
    "J21": (130.0, 157.0, 0),      # SENSOR_ADC 1x04 (3V3, VP, VN, GND)
    "J22": (147.0, 156.0, 90),     # SENSOR_DIGITAL 1x08 (5V, 3V3, IO4, IO5, IO13, IO14, IO2, GND)

    # Reset & Boot Circuit
    "R10": (130.0, 168.0, 0),      # 10k EN pull-up
    "C14": (130.0, 172.0, 0),      # 100nF EN RC delay
    "R11": (166.0, 190.0, 0),      # 10k IO0 pull-up

    # Push buttons at accessible edge locations
    "SW1": (139.0, 190.0, 0),      # Reset button
    "SW2": (148.0, 190.0, 0),      # Boot button

    # Programming & I2C headers along bottom edge
    "J15": (114.0, 195.0, 0),      # LS3 2-pin
    "J16": (122.0, 195.0, 0),      # LS4 2-pin
    "J3":  (129.0, 195.0, 90),     # AUX BUCK DNP 1x04
    "J20": (158.0, 195.0, 90),     # PROG_UART0 1x06 (X=158..170.7, Y=195.0)
    "J17": (178.0, 195.0, 90),     # I2C OLED 1x04 (X=178..185.6, Y=195.0)

    # Test Points
    "TP8": (134.0, 180.0, 0),      # GPIO33 Test Point
    "TP6": (108.0, 195.0, 0),      # GND Test Point
    "TP7": (166.0, 150.0, 0),      # GND Test Point

    # 7. Left Edge Connectors (X=108.0, rot 270)
    "J9":  (108.0, 137.0, 270),    # IR RX1 3-pin
    "J10": (108.0, 149.0, 270),    # IR RX2 3-pin
    "J11": (108.0, 160.0, 270),    # IR TX1 2-pin
    "J12": (108.0, 169.0, 270),    # IR TX2 2-pin
    "J13": (108.0, 178.0, 270),    # LS1 2-pin
    "J14": (108.0, 187.0, 270),    # LS2 2-pin

    # 8. Limit Switch RC Filters (horizontal 2x2 grid)
    "R16": (115.0, 175.0, 0),      # LS1 pullup
    "C7":  (115.0, 179.0, 0),      # LS1 cap
    "R17": (115.0, 183.0, 0),      # LS2 pullup
    "C8":  (115.0, 187.0, 0),      # LS2 cap
    "R18": (125.0, 175.0, 0),      # LS3 pullup
    "C9":  (125.0, 179.0, 0),      # LS3 cap
    "R19": (125.0, 183.0, 0),      # LS4 pullup
    "C10": (125.0, 187.0, 0),      # LS4 cap

    # 9. IR Transmitter Driver Circuit
    "R14": (116.0, 160.0, 0),      # 120R IR TX1 limit horizontal
    "Q2":  (127.0, 166.0, 90),     # NPN S8050 TO-92 rotated 90 deg
    "R13": (127.0, 158.0, 90),     # 1k base resistor rot 90 deg
    "R15": (116.0, 169.0, 0),      # 120R IR TX2 limit horizontal
}

NET_SPECS_OPTIMAL = [
    # 1. Direct local signals (LED anodes & Gates) - Route first
    ("NET_D2_ANODE", 0.35, [0, 1], ["R20.2", "D2.1"]),
    ("NET_D3_ANODE", 0.35, [0, 1], ["R21.2", "D3.1"]),
    ("NET_D4_ANODE", 0.35, [0, 1], ["R22.2", "D4.1"]),
    ("NET_D5_ANODE", 0.35, [0, 1], ["R23.2", "D5.1"]),
    ("NET_D6_ANODE", 0.35, [0, 1], ["R24.2", "D6.1"]),
    ("NET_Q1_GATE", 0.35, [0, 1], None),
    ("NET_Q2_BASE", 0.30, [0, 1], ["R13.2", "Q2.2"]),
    ("NET_IR_TX1_ANODE", 0.35, [0, 1], ["R14.2", "J11.1"]),
    ("NET_IR_TX2_ANODE", 0.35, [0, 1], ["R15.2", "J12.1"]),
    ("IR_TX_RET", 0.35, [0, 1], ["Q2.3", "J11.2", "J12.2"]),

    # 2. West breakout signals (Direct horizontal fanout from U2 pins 6..12 to the West!)
    # Route these first to give them clean, unobstructed exit lanes!
    ("IR_RX1", 0.35, [0, 1], ["U2.6", "J9.2"]),
    ("IR_RX2", 0.35, [0, 1], ["U2.7", "J10.2"]),
    ("LS4", 0.35, [0, 1], ["U2.8", "R19.1", "C10.1", "J16.1"]),
    ("SPARE_GPIO33", 0.35, [0, 1], ["U2.9", "TP8.1"]),
    ("LS1", 0.35, [0, 1], ["U2.10", "R16.1", "C7.1", "J13.1"]),
    ("LS2", 0.35, [0, 1], ["U2.11", "R17.1", "C8.1", "J14.1"]),
    ("LS3", 0.35, [0, 1], ["U2.12", "R18.1", "C9.1", "J15.1"]),

    # 3. North Analog & Reset signals
    ("ESP_EN", 0.35, [0, 1], ["U2.3", "R10.2", "C14.1"]),
    ("ESP_EN", 0.35, [1, 0], ["C14.1", "SW1.1", "J20.6"]),
    ("ADC_VP", 0.35, [0, 1], ["U2.4", "J21.2"]),
    ("ADC_VN", 0.35, [0, 1], ["U2.5", "J21.3"]),

    # 4. Critical Servo PWM lines (Top Layer F.Cu priority!)
    ("ESP_S2_BOT_PWM", 0.35, [0, 1], ["U2.31", "R4.1"]),
    ("ESP_S2_TOP_PWM", 0.35, [0, 1], ["U2.30", "R3.1"]),
    ("ESP_S1_BOT_PWM", 0.35, [0, 1], ["U2.28", "R2.1"]),
    ("ESP_S1_TOP_PWM", 0.35, [0, 1], ["U2.27", "R1.1"]),
    ("S2_BOT_PWM", 0.35, [1, 0], ["R4.2", "R8.1", "J8.3"]),
    ("S2_TOP_PWM", 0.35, [1, 0], ["R3.2", "R7.1", "J7.3"]),
    ("S1_BOT_PWM", 0.35, [1, 0], ["R2.2", "R6.1", "J6.3"]),
    ("S1_TOP_PWM", 0.35, [1, 0], ["R1.2", "R5.1", "J5.3"]),

    # 5. Sensor & bus breakouts
    ("ESP_IO0", 0.35, [0, 1], ["U2.25", "SW2.1", "R11.2", "J20.5"]),
    ("EXP_IO4", 0.35, [0, 1], ["U2.26", "J22.3"]),
    ("EXP_IO5", 0.35, [0, 1], ["U2.29", "J22.4"]),
    ("EXP_IO13", 0.35, [1, 0], ["U2.16", "J22.5"]),
    ("EXP_IO14", 0.35, [0, 1], ["U2.13", "J22.6"]),
    ("EXP_IO2", 0.35, [0, 1], ["U2.24", "J22.7"]),
    ("ESP_IR_TX", 0.35, [0, 1], ["U2.37", "R13.1"]),

    # 6. South-bound bus signals
    ("I2C_SDA", 0.35, [0, 1], ["U2.33", "J17.2"]),
    ("ESP_RXD0", 0.35, [0, 1], ["U2.34", "J20.3"]),
    ("ESP_TXD0", 0.35, [0, 1], ["U2.35", "J20.2"]),
    ("I2C_SCL", 0.35, [0, 1], ["U2.36", "J17.3"]),

    # 7. High-current power trunks
    ("+12V_IN", 1.8, [0], ["J1.1", "F1.1"]),
    ("+12V_FUSED", 1.2, [0], ["F1.2", "Q1.2"]),
    ("+12V", 1.5, [0], ["Q1.3", "D1.1", "J2.1"]),
    ("+12V", 1.2, [0], ["D1.1", "J4.1"]),
    ("+6V_SERVO", 2.0, [0], ["J2.3", "F3.1", "F2.1"]),
    ("+6V_A", 1.8, [0], ["F2.2", "C1.1", "C3.1", "J6.2", "J5.2"]),
    ("+6V_B", 1.8, [0], ["F3.2", "C2.1", "C4.1", "J8.2", "J7.2"]),
    
    # 8. Logic power trunks
    ("+5V", 0.8, [0, 1], ["J4.3", "C5.1", "C11.1", "U3.3"]),
    ("+5V", 0.5, [0, 1], ["C5.1", "R14.1", "R15.1"]),
    ("+5V", 0.5, [0, 1], ["U3.3", "J22.1"]),
    ("+5V", 0.35, [0, 1], ["J4.3", "R23.1", "TP4.1"]),

    # 9. +3.3V Branches
    ("+3V3", 0.6, [0, 1], ["U3.2", "C12.1", "C13.1", "U2.2"]),
    ("+3V3", 0.4, [0, 1], ["U3.2", "C6.1", "J9.1", "J10.1"]),
    ("+3V3", 0.35, [0, 1], ["C6.1", "R16.2", "R17.2"]),
    ("+3V3", 0.35, [0, 1], ["C6.1", "R18.2", "R19.2"]),
    ("+3V3", 0.4, [0, 1], ["U3.2", "J22.2", "J21.1", "R10.1"]),
    ("+3V3", 0.4, [0, 1], ["J22.2", "J20.1", "J17.1", "R11.1"]),
    ("+3V3", 0.35, [0, 1], ["U3.2", "R24.1", "TP5.1"]),

    # 10. Indicator taps & AUX connections
    ("+12V", 0.35, [1, 0], ["D1.1", "R20.1", "TP1.1"]),
    ("+12V", 0.35, [1], ["D1.1", "J3.1"]),
    ("+6V_SERVO", 0.35, [1], ["F2.1", "J3.3"]),
    ("+6V_A", 0.35, [0, 1], ["C1.1", "R21.1", "TP2.1"]),
    ("+6V_B", 0.35, [0, 1], ["C2.1", "R22.1", "TP3.1"]),
]

def generate_clean_board():
    manifest_path = ROOT / "hardware/archive/reva" / "FV-CTRL_RevA.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    comps = manifest["components"]
    nets = manifest["nets"]

    board = pcbnew.BOARD()
    net_map = {}
    for net_name in nets:
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)
        net_map[net_name] = net

    # Edge cuts (100x100mm)
    X0, Y0, W, H = 100.0, 100.0, 100.0, 100.0
    pts = [(X0, Y0), (X0+W, Y0), (X0+W, Y0), (X0+W, Y0+H), (X0+W, Y0+H), (X0, Y0+H), (X0, Y0+H), (X0, Y0)]
    for i in range(0, len(pts), 2):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(pts[i][0]), pcbnew.FromMM(pts[i][1])))
        seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(pts[i+1][0]), pcbnew.FromMM(pts[i+1][1])))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(pcbnew.FromMM(0.15))
        board.Add(seg)

    # Mounting holes (3.2mm M3 at 4 corners)
    mh_coords = [("H1", 104.0, 104.0), ("H2", 196.0, 104.0), ("H3", 104.0, 196.0), ("H4", 196.0, 196.0)]
    for ref, mx, my in mh_coords:
        mh = pcbnew.FootprintLoad(str(KICAD_FP_DIR / "MountingHole.pretty"), "MountingHole_3.2mm_M3")
        mh.SetReference(ref)
        mh.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(mx), pcbnew.FromMM(my)))
        board.Add(mh)

    node_to_net = {}
    for net_name, net_data in nets.items():
        for node in net_data["nodes"]:
            ref, pin = node.split(".")
            node_to_net[(ref, pin)] = net_name

    PIN_TO_PAD_OVERRIDE = {
        ("Q1", "G"): "1", ("Q1", "D"): "2", ("Q1", "S"): "3",
        ("Q2", "E"): "1", ("Q2", "B"): "2", ("Q2", "C"): "3",
    }
    for (r, p), pad in PIN_TO_PAD_OVERRIDE.items():
        if (r, p) in node_to_net:
            node_to_net[(r, pad)] = node_to_net[(r, p)]

    for c in comps:
        ref = c["ref"]
        val = c["value"]
        lib_id = c["footprint"]
        x, y, rot = PLACEMENTS[ref]
        lib_name, fp_name = lib_id.split(":")
        lib_path = (ROOT / "libs" / "fv_modules.pretty") if lib_name == "fv_modules" else (KICAD_FP_DIR / f"{lib_name}.pretty")
        fp = pcbnew.FootprintLoad(str(lib_path), fp_name)
        fp.SetReference(ref)
        fp.SetValue(val)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        for pad in fp.Pads():
            pad_num = pad.GetNumber()
            if (ref, pad_num) in node_to_net:
                nname = node_to_net[(ref, pad_num)]
                if nname in net_map:
                    pad.SetNet(net_map[nname])
        board.Add(fp)

    # GND Zones (Top and Bottom)
    gnd_net = net_map["GND"]
    for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
        zone = pcbnew.ZONE(board)
        ls = pcbnew.LSET()
        ls.AddLayer(layer)
        zone.SetLayerSet(ls)
        zone.SetNetCode(gnd_net.GetNetCode())
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefGap(pcbnew.FromMM(0.5))
        zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.5))
        poly = zone.Outline()
        poly.NewOutline()
        poly.Append(pcbnew.FromMM(100.5), pcbnew.FromMM(100.5))
        poly.Append(pcbnew.FromMM(199.5), pcbnew.FromMM(100.5))
        poly.Append(pcbnew.FromMM(199.5), pcbnew.FromMM(199.5))
        poly.Append(pcbnew.FromMM(100.5), pcbnew.FromMM(199.5))
        board.Add(zone)

    res = 0.20
    nx = int(round(100.0 / res)) + 1
    ny = int(round(100.0 / res)) + 1

    net_name_to_id = {"GND": 1}
    for n in sorted(nets.keys()):
        if n != "GND":
            net_name_to_id[n] = len(net_name_to_id) + 1

    pads_list = []
    pad_lookup = {}
    for pad in board.GetPads():
        fp = pad.GetParentFootprint()
        if fp:
            ref = fp.GetReference()
            pad_num = pad.GetNumber()
            pos = pad.GetPosition()
            px_mm = pcbnew.ToMM(pos.x)
            py_mm = pcbnew.ToMM(pos.y)
            nname = pad.GetNetname()
            nid = net_name_to_id.get(nname, 0)
            sz = pad.GetSize()
            w_mm = pcbnew.ToMM(sz.x)
            h_mm = pcbnew.ToMM(sz.y)
            layers = [0, 1] if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else ([0] if pad.IsOnLayer(pcbnew.F_Cu) else [1])
            pdata = {
                "ref": ref, "pnum": pad_num, "pad": pad, "net_name": nname, "net_id": nid,
                "pos_mm": (px_mm, py_mm), "px": px_mm - 100.0, "py": py_mm - 100.0,
                "gx": int(round((px_mm - 100.0) / res)), "gy": int(round((py_mm - 100.0) / res)),
                "w_pad": w_mm, "h_pad": h_mm, "layers": layers
            }
            pads_list.append(pdata)
            if (ref, pad_num) not in pad_lookup:
                pad_lookup[(ref, pad_num)] = []
            pad_lookup[(ref, pad_num)].append(pdata)

    routed_tracks = []
    routed_vias = []
    CLEARANCE = 0.22
    VIA_DIAM = 0.65

    # Precompute base via obstacle grid
    base_via_obs = np.zeros((ny, nx), dtype=bool)
    v_margin = int(np.ceil(0.80 / res))
    base_via_obs[:v_margin, :] = True
    base_via_obs[-v_margin:, :] = True
    base_via_obs[:, :v_margin] = True
    base_via_obs[:, -v_margin:] = True

    # Keepout under ESP32 body & antenna
    kx0 = int(round((139.5 - 100.0) / res))
    kx1 = int(round((160.5 - 100.0) / res))
    ky0 = int(round((161.0 - 100.0) / res))
    ky1 = int(round((188.5 - 100.0) / res))
    base_via_obs[ky0:ky1+1, kx0:kx1+1] = True

    # Keepout around mounting holes
    for mx_mm, my_mm in [(4.0, 4.0), (96.0, 4.0), (4.0, 96.0), (96.0, 96.0)]:
        gx = int(round(mx_mm / res))
        gy = int(round(my_mm / res))
        r_mh_cells = int(np.ceil(2.2 / res))
        ym, xm = np.ogrid[-r_mh_cells:r_mh_cells+1, -r_mh_cells:r_mh_cells+1]
        base_via_obs[max(0, gy-r_mh_cells):min(ny, gy+r_mh_cells+1), max(0, gx-r_mh_cells):min(nx, gx+r_mh_cells+1)] |= (xm*xm + ym*ym <= r_mh_cells*r_mh_cells)

    # Vias cannot overlap any pad (or pad clearance)
    for p in pads_list:
        px, py = p["px"], p["py"]
        wp, hp = p["w_pad"], p["h_pad"]
        req_d = VIA_DIAM / 2.0 + CLEARANCE
        gx0 = max(0, int(np.floor((px - wp / 2.0 - req_d) / res)))
        gx1 = min(nx - 1, int(np.ceil((px + wp / 2.0 + req_d) / res)))
        gy0 = max(0, int(np.floor((py - hp / 2.0 - req_d) / res)))
        gy1 = min(ny - 1, int(np.ceil((py + hp / 2.0 + req_d) / res)))
        if gx0 <= gx1 and gy0 <= gy1:
            xs = np.arange(gx0, gx1 + 1) * res
            ys = np.arange(gy0, gy1 + 1) * res
            dx = np.maximum(0.0, np.abs(xs[None, :] - px) - wp / 2.0)
            dy = np.maximum(0.0, np.abs(ys[:, None] - py) - hp / 2.0)
            base_via_obs[gy0:gy1+1, gx0:gx1+1] |= ((dx*dx + dy*dy) < (req_d * req_d))

    def mark_via_placed(vx_mm, vy_mm):
        vx = vx_mm - 100.0
        vy = vy_mm - 100.0
        req_d = VIA_DIAM + CLEARANCE
        gx0 = max(0, int(np.floor((vx - req_d) / res)))
        gx1 = min(nx - 1, int(np.ceil((vx + req_d) / res)))
        gy0 = max(0, int(np.floor((vy - req_d) / res)))
        gy1 = min(ny - 1, int(np.ceil((vy + req_d) / res)))
        if gx0 <= gx1 and gy0 <= gy1:
            xs = np.arange(gx0, gx1 + 1) * res
            ys = np.arange(gy0, gy1 + 1) * res
            dx = xs[None, :] - vx
            dy = ys[:, None] - vy
            base_via_obs[gy0:gy1+1, gx0:gx1+1] |= ((dx*dx + dy*dy) < (req_d * req_d))

    def add_track_segment(start_vec, end_vec, width_mm, layer_id, kicad_net, nid):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(start_vec)
        t.SetEnd(end_vec)
        t.SetWidth(pcbnew.FromMM(width_mm))
        t.SetLayer(layer_id)
        t.SetNet(kicad_net)
        board.Add(t)
        x1, y1 = pcbnew.ToMM(start_vec.x), pcbnew.ToMM(start_vec.y)
        x2, y2 = pcbnew.ToMM(end_vec.x), pcbnew.ToMM(end_vec.y)
        routed_tracks.append((x1, y1, x2, y2, width_mm, 0 if layer_id == pcbnew.F_Cu else 1, nid))

    def build_obstacle_grid(net_id, width_mm):
        obs = np.zeros((2, ny, nx), dtype=bool)
        r_margin = int(np.ceil((0.60 + width_mm / 2.0) / res))
        obs[:, :r_margin, :] = True
        obs[:, -r_margin:, :] = True
        obs[:, :, :r_margin] = True
        obs[:, :, -r_margin:] = True
        
        # Mounting holes
        mh_r_mm = 1.60 + 0.60 + width_mm / 2.0
        mh_r_cells = int(np.ceil(mh_r_mm / res))
        y_m, x_m = np.ogrid[-mh_r_cells:mh_r_cells+1, -mh_r_cells:mh_r_cells+1]
        mh_mask = x_m*x_m + y_m*y_m <= mh_r_cells*mh_r_cells
        for mx_mm, my_mm in [(4.0, 4.0), (96.0, 4.0), (4.0, 96.0), (96.0, 96.0)]:
            gx = int(round(mx_mm / res))
            gy = int(round(my_mm / res))
            obs[:, gy-mh_r_cells:gy+mh_r_cells+1, gx-mh_r_cells:gx+mh_r_cells+1] |= mh_mask

        # Antenna keepout zone: X=[139.5..160.5], Y=[161.0..168.5]
        kx0 = int(round((139.5 - 100.0) / res))
        kx1 = int(round((160.5 - 100.0) / res))
        ky0 = int(round((161.0 - 100.0) / res))
        ky1 = int(round((168.5 - 100.0) / res))
        obs[:, ky0:ky1+1, kx0:kx1+1] = True

        # Pad obstacles
        R_req = CLEARANCE + width_mm / 2.0
        for p in pads_list:
            if p["net_id"] != net_id:
                px, py = p["px"], p["py"]
                wp, hp = p["w_pad"], p["h_pad"]
                gx0 = max(0, int(np.floor((px - wp / 2.0 - R_req) / res)))
                gx1 = min(nx - 1, int(np.ceil((px + wp / 2.0 + R_req) / res)))
                gy0 = max(0, int(np.floor((py - hp / 2.0 - R_req) / res)))
                gy1 = min(ny - 1, int(np.ceil((py + hp / 2.0 + R_req) / res)))
                if gx0 > gx1 or gy0 > gy1:
                    continue
                xs = np.arange(gx0, gx1 + 1) * res
                ys = np.arange(gy0, gy1 + 1) * res
                dx = np.maximum(0.0, np.abs(xs[None, :] - px) - wp / 2.0)
                dy = np.maximum(0.0, np.abs(ys[:, None] - py) - hp / 2.0)
                p_mask = (dx * dx + dy * dy) < (R_req * R_req)
                for l in p["layers"]:
                    obs[l, gy0:gy1+1, gx0:gx1+1] |= p_mask

        # Track obstacles (Exact point-to-segment distance for ALL angles)
        for (x1_mm, y1_mm, x2_mm, y2_mm, w_tr, layer, tr_nid) in routed_tracks:
            if tr_nid != net_id:
                D_req = w_tr / 2.0 + CLEARANCE + width_mm / 2.0
                min_x = min(x1_mm, x2_mm) - 100.0 - D_req
                max_x = max(x1_mm, x2_mm) - 100.0 + D_req
                min_y = min(y1_mm, y2_mm) - 100.0 - D_req
                max_y = max(y1_mm, y2_mm) - 100.0 + D_req
                gx0 = max(0, int(np.floor(min_x / res)))
                gx1 = min(nx - 1, int(np.ceil(max_x / res)))
                gy0 = max(0, int(np.floor(min_y / res)))
                gy1 = min(ny - 1, int(np.ceil(max_y / res)))
                if gx0 > gx1 or gy0 > gy1:
                    continue
                xs = np.arange(gx0, gx1 + 1) * res
                ys = np.arange(gy0, gy1 + 1) * res
                sx1, sy1 = x1_mm - 100.0, y1_mm - 100.0
                sx2, sy2 = x2_mm - 100.0, y2_mm - 100.0
                sdx = sx2 - sx1
                sdy = sy2 - sy1
                L2 = sdx*sdx + sdy*sdy
                if L2 < 1e-8:
                    t_mask = ((xs[None, :] - sx1)**2 + (ys[:, None] - sy1)**2) < (D_req * D_req)
                else:
                    t_proj = np.clip(((xs[None, :] - sx1)*sdx + (ys[:, None] - sy1)*sdy) / L2, 0.0, 1.0)
                    px_proj = sx1 + t_proj * sdx
                    py_proj = sy1 + t_proj * sdy
                    t_mask = ((xs[None, :] - px_proj)**2 + (ys[:, None] - py_proj)**2) < (D_req * D_req)
                obs[layer, gy0:gy1+1, gx0:gx1+1] |= t_mask

        # Via obstacles
        for (vx_mm, vy_mm, drill_mm, v_w_mm, v_nid) in routed_vias:
            if v_nid != net_id:
                D_req = v_w_mm / 2.0 + CLEARANCE + width_mm / 2.0
                vx, vy = vx_mm - 100.0, vy_mm - 100.0
                gx0 = max(0, int(np.floor((vx - D_req) / res)))
                gx1 = min(nx - 1, int(np.ceil((vx + D_req) / res)))
                gy0 = max(0, int(np.floor((vy - D_req) / res)))
                gy1 = min(ny - 1, int(np.ceil((vy + D_req) / res)))
                if gx0 > gx1 or gy0 > gy1:
                    continue
                xs = np.arange(gx0, gx1 + 1) * res
                ys = np.arange(gy0, gy1 + 1) * res
                dx = xs[None, :] - vx
                dy = ys[:, None] - vy
                v_mask = (dx * dx + dy * dy) < (D_req * D_req)
                obs[:, gy0:gy1+1, gx0:gx1+1] |= v_mask
        return obs

    def astar(obs, source_cells, target_cells, allowed_layers=(0, 1)):
        target_set = set(target_cells)
        pq = []
        parent = {}
        dist = {}
        def h(l, x, y):
            return min(abs(x - tx) + abs(y - ty) for tl, tx, ty in target_cells)

        for cell in source_cells:
            dist[cell] = 0.0
            parent[cell] = None
            heapq.heappush(pq, (h(*cell), 0.0, cell, None))

        found_target = None
        while pq:
            f, g, u, p_node = heapq.heappop(pq)
            if g > dist[u]: continue
            if u in target_set:
                found_target = u
                break
            l, x, y = u
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx_c, ny_c = x + dx, y + dy
                if 0 <= nx_c < nx and 0 <= ny_c < ny:
                    if not obs[l, ny_c, nx_c]:
                        v = (l, nx_c, ny_c)
                        turn_pen = 0.5 if (p_node and (nx_c - x, ny_c - y) != (x - p_node[1], y - p_node[2])) else 0.0
                        layer_pref = 0.0 if l == allowed_layers[0] else 0.2
                        ng = g + 1.0 + turn_pen + layer_pref
                        if v not in dist or ng < dist[v]:
                            dist[v] = ng
                            parent[v] = u
                            heapq.heappush(pq, (ng + h(*v), ng, v, u))

            if len(allowed_layers) > 1:
                nl = 1 - l
                if nl in allowed_layers and not obs[nl, y, x] and not base_via_obs[y, x]:
                    v = (nl, x, y)
                    ng = g + 15.0
                    if v not in dist or ng < dist[v]:
                        dist[v] = ng
                        parent[v] = u
                        heapq.heappush(pq, (ng + h(*v), ng, v, u))

        if not found_target: return None
        path = []
        curr = found_target
        while curr:
            path.append(curr)
            curr = parent[curr]
        path.reverse()
        return path

    # Pre-link multi-pin footprints (F1 and J4)
    f1_pads = [p for p in pads_list if p["ref"] == "F1"]
    p1_pins = sorted([p for p in f1_pads if p["pnum"] == "1"], key=lambda p: p["pos_mm"][1])
    p2_pins = sorted([p for p in f1_pads if p["pnum"] == "2"], key=lambda p: p["pos_mm"][1])
    if len(p1_pins) == 2:
        add_track_segment(p1_pins[0]["pad"].GetPosition(), p1_pins[1]["pad"].GetPosition(), 1.8, pcbnew.F_Cu, net_map["+12V_IN"], net_name_to_id["+12V_IN"])
    if len(p2_pins) == 2:
        add_track_segment(p2_pins[0]["pad"].GetPosition(), p2_pins[1]["pad"].GetPosition(), 1.2, pcbnew.F_Cu, net_map["+12V_FUSED"], net_name_to_id["+12V_FUSED"])

    j4_pads = [p for p in pads_list if p["ref"] == "J4"]
    j4_p1 = sorted([p for p in j4_pads if p["pnum"] == "1"], key=lambda p: p["pos_mm"][1])
    j4_p3 = sorted([p for p in j4_pads if p["pnum"] == "3"], key=lambda p: p["pos_mm"][1])
    if len(j4_p1) == 2:
        add_track_segment(j4_p1[0]["pad"].GetPosition(), j4_p1[1]["pad"].GetPosition(), 1.2, pcbnew.F_Cu, net_map["+12V"], net_name_to_id["+12V"])
    if len(j4_p3) == 2:
        add_track_segment(j4_p3[0]["pad"].GetPosition(), j4_p3[1]["pad"].GetPosition(), 1.0, pcbnew.F_Cu, net_map["+5V"], net_name_to_id["+5V"])

    total_routed = 0
    failed_routes = []
    t0 = time.time()

    for net_name, width_mm, allowed_layers, node_chain in NET_SPECS_OPTIMAL:
        net_data = nets.get(net_name)
        if not net_data: continue
        nodes = node_chain if node_chain else net_data["nodes"]
        if len(nodes) < 2: continue
        nid = net_name_to_id[net_name]
        kicad_net = net_map[net_name]
        
        pads_for_net = []
        for node in nodes:
            ref, pin = node.split(".")
            pad_num = PIN_TO_PAD_OVERRIDE.get((ref, pin), pin)
            plist = pad_lookup.get((ref, pad_num), [])
            if plist:
                pads_for_net.append(plist[0])
                
        if len(pads_for_net) < 2: continue
        obs = build_obstacle_grid(nid, width_mm)
        for p in pads_for_net:
            for l in p["layers"]:
                gx, gy = p["gx"], p["gy"]
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if 0 <= gx + dx < nx and 0 <= gy + dy < ny:
                            obs[l, gy + dy, gx + dx] = False
        
        connected_cells = set()
        first_pad = pads_for_net[0]
        fx, fy = first_pad["gx"], first_pad["gy"]
        for l in first_pad["layers"]:
            if l in allowed_layers and not obs[l, fy, fx]:
                connected_cells.add((l, fx, fy))
        if not connected_cells:
            connected_cells.add((allowed_layers[0], fx, fy))
            
        for next_pad in pads_for_net[1:]:
            target_cells = [(l, next_pad["gx"], next_pad["gy"]) for l in next_pad["layers"] if l in allowed_layers]
            if not target_cells:
                target_cells = [(allowed_layers[0], next_pad["gx"], next_pad["gy"])]
            path = astar(obs, list(connected_cells), target_cells, allowed_layers)
            if not path:
                fail_msg = f"{net_name} to {next_pad['pad'].GetParentFootprint().GetReference()}.{next_pad['pad'].GetNumber()}"
                failed_routes.append(fail_msg)
                continue
            for cell in path:
                connected_cells.add(cell)

            seg_start = path[0]
            curr_dir = None
            start_pos = pcbnew.VECTOR2I(pcbnew.FromMM(100.0 + seg_start[1]*res), pcbnew.FromMM(100.0 + seg_start[2]*res))
            for i in range(1, len(path)):
                prev = path[i-1]
                curr = path[i]
                if curr[0] != prev[0]:
                    if seg_start != prev:
                        x2 = 100.0 + prev[1]*res
                        y2 = 100.0 + prev[2]*res
                        layer = pcbnew.F_Cu if seg_start[0] == 0 else pcbnew.B_Cu
                        end_pos = pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2))
                        add_track_segment(start_pos, end_pos, width_mm, layer, kicad_net, nid)
                    via = pcbnew.PCB_VIA(board)
                    vx = 100.0 + prev[1]*res
                    vy = 100.0 + prev[2]*res
                    vpos = pcbnew.VECTOR2I(pcbnew.FromMM(vx), pcbnew.FromMM(vy))
                    via.SetPosition(vpos)
                    via.SetWidth(pcbnew.FromMM(VIA_DIAM))
                    via.SetDrill(pcbnew.FromMM(0.35))
                    via.SetNet(kicad_net)
                    via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    board.Add(via)
                    routed_vias.append((vx, vy, 0.35, VIA_DIAM, nid))
                    mark_via_placed(vx, vy)
                    seg_start = curr
                    start_pos = vpos
                    curr_dir = None
                    continue
                dir_step = (curr[1] - prev[1], curr[2] - prev[2])
                if curr_dir is None:
                    curr_dir = dir_step
                elif curr_dir != dir_step:
                    x2 = 100.0 + prev[1]*res
                    y2 = 100.0 + prev[2]*res
                    layer = pcbnew.F_Cu if seg_start[0] == 0 else pcbnew.B_Cu
                    end_pos = pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2))
                    add_track_segment(start_pos, end_pos, width_mm, layer, kicad_net, nid)
                    seg_start = prev
                    start_pos = end_pos
                    curr_dir = dir_step

            # Final connection from end of path to exact pad center with orthogonal segments
            layer = pcbnew.F_Cu if seg_start[0] == 0 else pcbnew.B_Cu
            pad_pos = next_pad["pad"].GetPosition()
            sx_mm = pcbnew.ToMM(start_pos.x)
            sy_mm = pcbnew.ToMM(start_pos.y)
            px_mm = pcbnew.ToMM(pad_pos.x)
            py_mm = pcbnew.ToMM(pad_pos.y)
            if abs(sx_mm - px_mm) > 0.05 and abs(sy_mm - py_mm) > 0.05:
                corner = pcbnew.VECTOR2I(pcbnew.FromMM(px_mm), pcbnew.FromMM(sy_mm))
                add_track_segment(start_pos, corner, width_mm, layer, kicad_net, nid)
                add_track_segment(corner, pad_pos, width_mm, layer, kicad_net, nid)
            else:
                add_track_segment(start_pos, pad_pos, width_mm, layer, kicad_net, nid)
            total_routed += 1

    t1 = time.time()
    print(f"Routing results: {total_routed} routed in {t1-t0:.2f}s, {len(failed_routes)} failed.", flush=True)
    for f in failed_routes:
        print(f"  FAILED: {f}", flush=True)

    # Link U3 pin 2 to U3 tab directly on F.Cu
    t_u3 = pcbnew.PCB_TRACK(board)
    t_u3.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(138.0), pcbnew.FromMM(144.85)))
    t_u3.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(138.0), pcbnew.FromMM(151.15)))
    t_u3.SetWidth(pcbnew.FromMM(0.6))
    t_u3.SetLayer(pcbnew.F_Cu)
    t_u3.SetNet(net_map['+3V3'])
    board.Add(t_u3)

    # Bridge SW1 and SW2 duplicate pins
    for sw_ref, sx, sy in [("SW1", 139.0, 190.0), ("SW2", 148.0, 190.0)]:
        t_sw1 = pcbnew.PCB_TRACK(board)
        t_sw1.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(sx), pcbnew.FromMM(sy)))
        t_sw1.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(sx + 6.5), pcbnew.FromMM(sy)))
        t_sw1.SetWidth(pcbnew.FromMM(0.35))
        t_sw1.SetLayer(pcbnew.F_Cu)
        t_sw1.SetNet(net_map["ESP_EN" if sw_ref == "SW1" else "ESP_IO0"])
        board.Add(t_sw1)
        t_sw2 = pcbnew.PCB_TRACK(board)
        t_sw2.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(sx), pcbnew.FromMM(sy + 4.5)))
        t_sw2.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(sx + 6.5), pcbnew.FromMM(sy + 4.5)))
        t_sw2.SetWidth(pcbnew.FromMM(0.5))
        t_sw2.SetLayer(pcbnew.B_Cu)
        t_sw2.SetNet(gnd_net)
        board.Add(t_sw2)

    # Connect U2.38 (GND) to U2.39 (belly pad) on F.Cu
    t_u2_gnd = pcbnew.PCB_TRACK(board)
    t_u2_gnd.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(159.0), pcbnew.FromMM(169.75)))
    t_u2_gnd.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(150.0), pcbnew.FromMM(169.75)))
    t_u2_gnd.SetWidth(pcbnew.FromMM(0.5))
    t_u2_gnd.SetLayer(pcbnew.F_Cu)
    t_u2_gnd.SetNet(gnd_net)
    board.Add(t_u2_gnd)

    t_u2_gnd2 = pcbnew.PCB_TRACK(board)
    t_u2_gnd2.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(150.0), pcbnew.FromMM(169.75)))
    t_u2_gnd2.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(150.0), pcbnew.FromMM(176.0)))
    t_u2_gnd2.SetWidth(pcbnew.FromMM(0.5))
    t_u2_gnd2.SetLayer(pcbnew.F_Cu)
    t_u2_gnd2.SetNet(gnd_net)
    board.Add(t_u2_gnd2)

    # Connect D4 cathode to GND
    t_d4_gnd = pcbnew.PCB_TRACK(board)
    t_d4_gnd.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(166.54), pcbnew.FromMM(152.0)))
    t_d4_gnd.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(166.54), pcbnew.FromMM(150.0)))
    t_d4_gnd.SetWidth(pcbnew.FromMM(0.5))
    t_d4_gnd.SetLayer(pcbnew.F_Cu)
    t_d4_gnd.SetNet(gnd_net)
    board.Add(t_d4_gnd)

    # Local GND escape tracks for THT caps and headers
    gnd_pad_links = [
        (135.0, 172.0, 137.0, 172.0),   # C14.2 -> via
        (136.0, 140.0, 136.0, 143.0),   # C5.2 -> via
        (165.62, 195.0, 165.62, 192.0), # J20.4 -> via
        (130.0, 179.0, 130.0, 187.0),   # C9.2 -> C10.2
    ]
    for x1, y1, x2, y2 in gnd_pad_links:
        t_link = pcbnew.PCB_TRACK(board)
        t_link.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        t_link.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        t_link.SetWidth(pcbnew.FromMM(0.4))
        t_link.SetLayer(pcbnew.B_Cu)
        t_link.SetNet(gnd_net)
        board.Add(t_link)

    # GND stitching vias to tie F.Cu GND plane to B.Cu GND plane
    stitching_coords = [
        (108.0, 108.0), (135.0, 108.0), (160.0, 108.0), (192.0, 108.0),
        (108.0, 145.0), (150.0, 142.0), (192.0, 142.0),
        (108.0, 172.0), (192.0, 162.0),
        (108.0, 192.0), (135.0, 192.0), (192.0, 192.0)
    ]
    for vx, vy in stitching_coords:
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(vx), pcbnew.FromMM(vy)))
        via.SetWidth(pcbnew.FromMM(0.80))
        via.SetDrill(pcbnew.FromMM(0.40))
        via.SetNet(gnd_net)
        via.SetViaType(pcbnew.VIATYPE_THROUGH)
        board.Add(via)

    board.BuildConnectivity()
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    out_pcb = ROOT / "hardware/archive/reva" / "FV-CTRL_RevA.kicad_pcb"
    pcbnew.SaveBoard(str(out_pcb), board)
    print("Saved clean board to:", str(out_pcb), flush=True)

if __name__ == "__main__":
    generate_clean_board()
