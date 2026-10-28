"""
Complete PCB Builder & Router for FreshVend Hardware Rev-S3.
Stage 1: Place footprints, assign netnames, create edge cuts & mounting holes -> Save.
Stage 2: LoadBoard -> Route power & signal tracks, add vias, flood GND copper zones -> Save.
"""
import pcbnew
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PCB = ROOT / "hardware/rev_s3/FV-CTRL_RevS3.kicad_pcb"
NET_XML = ROOT / "hardware/rev_s3/FV-CTRL_RevS3.net.xml"
KICAD_FP_DIR = Path("C:/Program Files/KiCad/10.0/share/kicad/footprints")
LOCAL_FP_DIR = ROOT / "libs"

def mm(val):
    return int(val * 1e6)

def add_track(board, net_name, x1, y1, x2, y2, width_mm, layer=pcbnew.F_Cu):
    net = board.FindNet(net_name)
    if not net:
        print(f"Warning: Net {net_name} not found!")
        return
    track = pcbnew.PCB_TRACK(board)
    board.Add(track)
    track.SetNet(net)
    track.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    track.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    track.SetWidth(mm(width_mm))
    track.SetLayer(layer)

def add_path(board, net_name, pts, width_mm, layer=pcbnew.F_Cu):
    for i in range(len(pts) - 1):
        add_track(board, net_name, pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], width_mm, layer)

def add_via(board, net_name, x, y, size_mm=0.60, drill_mm=0.30):
    net = board.FindNet(net_name)
    if not net:
        print(f"Warning: Net {net_name} not found for via!")
        return
    via = pcbnew.PCB_VIA(board)
    board.Add(via)
    via.SetNet(net)
    via.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    via.SetWidth(mm(size_mm))
    via.SetDrill(mm(drill_mm))

def stage1_placement():
    print("Stage 1: Placing footprints and setting up board...")
    board = pcbnew.BOARD()
    
    settings = board.GetDesignSettings()
    settings.m_TrackMinWidth = mm(0.25)
    settings.m_ViasMinSize = mm(0.60)
    settings.m_ViasMinDrill = mm(0.30)
    
    # 1. Edge.Cuts: 100mm x 100mm from (100, 100) to (200, 200)
    edge_pts = [
        (100.0, 100.0), (200.0, 100.0),
        (200.0, 200.0), (100.0, 200.0),
        (100.0, 100.0)
    ]
    for i in range(len(edge_pts) - 1):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(mm(edge_pts[i][0]), mm(edge_pts[i][1])))
        seg.SetEnd(pcbnew.VECTOR2I(mm(edge_pts[i+1][0]), mm(edge_pts[i+1][1])))
        seg.SetWidth(mm(0.15))
        seg.SetLayer(pcbnew.Edge_Cuts)
        board.Add(seg)
    
    # 2. Mounting Holes H1..H4 (M3)
    hole_fp_path = KICAD_FP_DIR / "MountingHole.pretty"
    holes = [("H1", 104.0, 104.0), ("H2", 196.0, 104.0), ("H3", 104.0, 196.0), ("H4", 196.0, 196.0)]
    for href, hx, hy in holes:
        hfp = pcbnew.FootprintLoad(str(hole_fp_path), "MountingHole_3.2mm_M3")
        hfp.SetReference(href)
        hfp.SetValue("MountingHole_3.2mm_M3")
        hfp.SetPosition(pcbnew.VECTOR2I(mm(hx), mm(hy)))
        board.Add(hfp)
    
    # 3. Parse Netlist
    tree = ET.parse(NET_XML)
    root = tree.getroot()
    
    pin_to_net = {}
    net_dict = {}
    code_idx = 1
    for net in root.find("nets").findall("net"):
        net_name = net.get("name")
        net_item = pcbnew.NETINFO_ITEM(board, net_name)
        net_item.SetNetCode(code_idx)
        net_dict[net_name] = net_item
        code_idx += 1
        for node in net.findall("node"):
            pin_to_net[(node.get("ref"), node.get("pin"))] = net_name
            
    # Optimized Placements (0 courtyard overlaps)
    placements = {
        # Power section (Top) - Golden RevB symmetric spacing (pitch 32mm)
        "J1":  (119.00, 112.00, 180.0), # 12V In KF2EDG 5.08mm
        "F1":  (123.00, 122.00, 0.0),   # Fuse 5x20mm horizontal (Y: 116.9..127.1)
        "D1":  (142.00, 130.00, 0.0),   # TVS SMBJ12A (safe from F1)
        "D7":  (142.00, 136.00, 0.0),   # Schottky SS54
        "J4":  (116.00, 142.00, 0.0),   # RECOM 5V 1A
        "C57": (108.00, 135.00, 0.0),   # 10uF 50V THT (safe from J4)
        "C58": (122.00, 148.00, 0.0),   # 100nF (safe from J4)
        "U3":  (130.00, 142.00, 0.0),   # LD1117S33 (safe from D7)
        "C6":  (138.00, 144.00, 0.0),   # 10uF 3.3V
        "J2":  (151.00, 112.00, 180.0), # Buck A Terminal
        "F2":  (151.00, 125.00, 0.0),   # PTC 2.5A
        "C1":  (151.00, 140.00, 0.0),   # 2200uF Bulk Cap A
        "J3":  (183.00, 112.00, 180.0), # Buck B Terminal
        "F3":  (183.00, 125.00, 0.0),   # PTC 2.5A
        "C2":  (183.00, 140.00, 0.0),   # 2200uF Bulk Cap B

        # MCU (Center)
        "U1":  (150.00, 166.00, 0.0),   # ESP32-S3-WROOM-1U

        # USB Type-C & Reset/Boot (Bottom-Center)
        "J21": (150.00, 196.50, 0.0),   # USB Type-C
        "R14": (145.00, 191.00, 0.0),   # CC1 5.1k
        "R15": (155.00, 191.00, 0.0),   # CC2 5.1k
        "R11": (147.00, 185.00, 90.0),  # D- 22R
        "R12": (153.00, 185.00, 90.0),  # D+ 22R
        "SW1": (136.00, 186.00, 0.0),   # RESET
        "R10": (133.00, 182.00, 0.0),   # 10k EN
        "C10": (138.00, 182.00, 0.0),   # 1uF EN
        "SW2": (161.00, 186.00, 0.0),   # BOOT

        # Servos (Right edge) - Golden 10mm pitch spacing
        "J5":  (194.00, 153.00, 0.0),   # S1_TOP
        "R1":  (186.00, 151.50, 0.0),   # 330R
        "R2":  (186.00, 154.50, 0.0),   # 10k
        "J6":  (194.00, 163.00, 0.0),   # S1_BOT
        "R3":  (186.00, 161.50, 0.0),   # 330R
        "R4":  (186.00, 164.50, 0.0),   # 10k
        "J7":  (194.00, 173.00, 0.0),   # S2_TOP
        "R5":  (186.00, 171.50, 0.0),   # 330R
        "R6":  (186.00, 174.50, 0.0),   # 10k
        "J8":  (194.00, 183.00, 0.0),   # S2_BOT
        "R7":  (186.00, 181.50, 0.0),   # 330R
        "R8":  (186.00, 184.50, 0.0),   # 10k

        # Universal Drop Sensors (Left edge)
        "J11": (107.00, 158.00, -90.0), # Col 1 Sensor
        "R16": (118.00, 156.50, 0.0),   # 1k
        "R17": (118.00, 159.50, 0.0),   # 2k
        "J12": (107.00, 175.00, -90.0), # Col 2 Sensor
        "R18": (118.00, 173.50, 0.0),   # 1k
        "R19": (118.00, 176.50, 0.0),   # 2k

        # Diagnostics & LEDs (Bottom-Left, safe from H3)
        "D2":  (112.00, 184.00, 0.0),   # LED 12V
        "R21": (117.00, 184.00, 0.0),   # 4.7k
        "D3":  (112.00, 186.50, 0.0),   # LED 6V_A
        "R22": (117.00, 186.50, 0.0),   # 2.2k
        "D4":  (112.00, 189.00, 0.0),   # LED 6V_B
        "R23": (117.00, 189.00, 0.0),   # 2.2k
        "D5":  (112.00, 191.50, 0.0),   # LED 5V
        "R24": (117.00, 191.50, 0.0),   # 1.5k
        "D6":  (112.00, 194.00, 0.0),   # LED 3V3
        "R25": (117.00, 194.00, 0.0),   # 1k

        # Test Points (2 columns)
        "TP1": (122.00, 184.00, 0.0),
        "TP2": (122.00, 187.00, 0.0),
        "TP3": (122.00, 190.00, 0.0),
        "TP4": (122.00, 193.00, 0.0),
        "TP5": (126.00, 184.00, 0.0),
        "TP6": (126.00, 187.00, 0.0),
        "TP7": (126.00, 190.00, 0.0),
        "TP8": (126.00, 193.00, 0.0),

        # Spares (Bottom-Right, safe from H4)
        "J9":  (167.00, 195.00, 90.0),  # I2C Spare (horizontal)
        "R26": (166.00, 188.00, 0.0),   # 4.7k SDA
        "R27": (170.00, 188.00, 0.0),   # 4.7k SCL
        "J10": (183.00, 195.00, 90.0),  # Limit switches spare (horizontal)
    }

    # Load and place all components
    for comp in root.find("components").findall("comp"):
        ref = comp.get("ref")
        fp_str = comp.find("footprint").text
        lib_name, fp_name = fp_str.split(":")
        lib_path = KICAD_FP_DIR / f"{lib_name}.pretty"
        if not lib_path.exists():
            lib_path = LOCAL_FP_DIR / f"{lib_name}.pretty"
        
        fp = pcbnew.FootprintLoad(str(lib_path), fp_name)
        fp.SetReference(ref)
        val = comp.find("value").text if comp.find("value") is not None else ""
        fp.SetValue(val)
        fp.Value().SetVisible(False)

        # Pad net mapping
        for pad in fp.Pads():
            pnum = pad.GetNumber()
            if (ref, pnum) in pin_to_net:
                nname = pin_to_net[(ref, pnum)]
                pad.SetNet(net_dict[nname])
            elif pnum == "" or pnum == "SH":
                pad.SetNet(net_dict["GND"])

        # Positioning
        if ref in placements:
            px, py, prot = placements[ref]
            fp.SetPosition(pcbnew.VECTOR2I(mm(px), mm(py)))
            fp.SetOrientationDegrees(prot)
            
        board.Add(fp)

    board.BuildListOfNets()
    pcbnew.SaveBoard(str(OUT_PCB), board)
    print(f"Stage 1 complete: Placed {len(board.GetFootprints())} footprints, saved to {OUT_PCB}")

def stage2_routing():
    print("Stage 2: Routing traces and filling GND planes...")
    board = pcbnew.LoadBoard(str(OUT_PCB))

    def pad_xy(ref, pnum):
        fp = board.FindFootprintByReference(ref)
        pad = fp.FindPadByNumber(str(pnum))
        p = pad.GetPosition()
        return p.x / 1e6, p.y / 1e6

    # 1. High-Current Power Paths
    add_path(board, "+12V_IN", [pad_xy("J1", 1), (119.0, 117.0), pad_xy("F1", 1)], 2.5)
    add_path(board, "Net-(D1-A1)", [pad_xy("F1", 2), (145.5, 126.0), pad_xy("D1", 1), pad_xy("D7", 2)], 2.5)
    add_path(board, "+6V_A_RAW", [pad_xy("J2", 3), (140.84, 118.0), pad_xy("F2", 1)], 2.0)
    add_path(board, "+6V_B_RAW", [pad_xy("J3", 3), (172.84, 118.0), pad_xy("F3", 1)], 2.0)

    # +12V Bus
    d7_1 = pad_xy("D7", 1)
    j4_1 = pad_xy("J4", 1)
    c57_1 = pad_xy("C57", 1)
    j2_1 = pad_xy("J2", 1)
    j3_1 = pad_xy("J3", 1)
    r21_1 = pad_xy("R21", 1)
    tp1_1 = pad_xy("TP1", 1)
    add_path(board, "+12V", [d7_1, (138.6, 134.0), j4_1, c57_1], 2.0)
    add_path(board, "+12V", [d7_1, (138.6, 118.0), (151.0, 118.0), j2_1], 2.0)
    add_path(board, "+12V", [(151.0, 118.0), (183.0, 118.0), j3_1], 2.0)
    add_path(board, "+12V", [c57_1, (108.0, 184.0), r21_1, tp1_1], 1.2)

    # +6V_A Bus
    f2_2 = pad_xy("F2", 2)
    c1_1 = pad_xy("C1", 1)
    j5_2 = pad_xy("J5", 2)
    j6_2 = pad_xy("J6", 2)
    r22_1 = pad_xy("R22", 1)
    tp2_1 = pad_xy("TP2", 1)
    add_path(board, "+6V_A", [f2_2, c1_1, (165.0, 140.0), (188.0, 155.54), j5_2], 2.0)
    add_path(board, "+6V_A", [j5_2, (194.0, 160.0), j6_2], 2.0)
    add_path(board, "+6V_A", [c1_1, (151.0, 148.0), (122.0, 148.0), (122.0, 187.0), tp2_1, r22_1], 1.2)

    # +6V_B Bus
    f3_2 = pad_xy("F3", 2)
    c2_1 = pad_xy("C2", 1)
    j7_2 = pad_xy("J7", 2)
    j8_2 = pad_xy("J8", 2)
    r23_1 = pad_xy("R23", 1)
    tp3_1 = pad_xy("TP3", 1)
    add_path(board, "+6V_B", [f3_2, c2_1, (190.0, 140.0), (190.0, 175.54), j7_2], 2.0)
    add_path(board, "+6V_B", [j7_2, (194.0, 180.0), j8_2], 2.0)
    add_path(board, "+6V_B", [c2_1, (183.0, 146.0), (130.0, 146.0), (130.0, 190.0), tp3_1, r23_1], 1.2)

    # +5V Bus
    j4_3 = pad_xy("J4", 3)
    c58_1 = pad_xy("C58", 1)
    u3_3 = pad_xy("U3", 3)
    j11_1 = pad_xy("J11", 1)
    j12_1 = pad_xy("J12", 1)
    r24_1 = pad_xy("R24", 1)
    tp4_1 = pad_xy("TP4", 1)
    add_path(board, "+5V", [j4_3, c58_1, u3_3], 1.5)
    add_path(board, "+5V", [j4_3, (116.0, 148.0), (107.0, 148.0), j11_1, j12_1, (107.0, 191.5), r24_1, tp4_1], 1.2)

    # +3V3 Bus
    u3_2 = pad_xy("U3", 2)
    c6_1 = pad_xy("C6", 1)
    u1_2 = pad_xy("U1", 2)
    r10_1 = pad_xy("R10", 1)
    j9_1 = pad_xy("J9", 1)
    r26_1 = pad_xy("R26", 1)
    r27_1 = pad_xy("R27", 1)
    r25_1 = pad_xy("R25", 1)
    tp5_1 = pad_xy("TP5", 1)
    add_path(board, "+3V3", [u3_2, c6_1, u1_2], 1.2)
    add_path(board, "+3V3", [u1_2, (136.0, 158.86), (136.0, 182.0), r10_1, (126.0, 184.0), tp5_1, (116.17, 194.0), r25_1], 0.8)
    add_path(board, "+3V3", [u1_2, (141.25, 154.0), (165.18, 154.0), (165.18, 188.0), r26_1, r27_1, j9_1], 0.8)

    # 2. USB Type-C signals
    add_path(board, "Net-(J21-CC1)", [pad_xy("J21", "A5"), pad_xy("R14", 1)], 0.25)
    add_path(board, "Net-(J21-CC2)", [pad_xy("J21", "B5"), pad_xy("R15", 1)], 0.25)
    add_path(board, "Net-(J21-D+-PadA6)", [pad_xy("J21", "A6"), pad_xy("J21", "B6"), pad_xy("R12", 1)], 0.25)
    add_path(board, "Net-(J21-D--PadA7)", [pad_xy("J21", "A7"), pad_xy("J21", "B7"), pad_xy("R11", 1)], 0.25)
    add_path(board, "USB_DP_S3", [pad_xy("R12", 2), (153.0, 178.0), (141.25, 174.1), pad_xy("U1", 14)], 0.25)
    add_path(board, "USB_DM_S3", [pad_xy("R11", 2), (147.0, 176.0), (141.25, 172.83), pad_xy("U1", 13)], 0.25)
    add_path(board, "USB_VBUS", [pad_xy("J21", "A4"), pad_xy("J21", "B4"), pad_xy("J21", "A9"), pad_xy("J21", "B9")], 0.5)

    # 3. Reset & Boot
    add_path(board, "ESP_EN", [pad_xy("U1", 3), (137.22, 160.13), pad_xy("C10", 1), pad_xy("R10", 2), pad_xy("SW1", 1)], 0.25)
    add_path(board, "ESP_BOOT", [pad_xy("U1", 27), pad_xy("SW2", 1)], 0.25)

    # 4. Servos
    add_path(board, "Net-(J5-Pin_3)", [pad_xy("J5", 3), pad_xy("R1", 2)], 0.25)
    add_path(board, "Net-(J6-Pin_3)", [pad_xy("J6", 3), pad_xy("R3", 2)], 0.25)
    add_path(board, "Net-(J7-Pin_3)", [pad_xy("J7", 3), pad_xy("R5", 2)], 0.25)
    add_path(board, "Net-(J8-Pin_3)", [pad_xy("J8", 3), pad_xy("R7", 2)], 0.25)

    add_path(board, "S1_TOP_PWM", [pad_xy("U1", 9), (141.25, 167.75), (145.0, 167.75)], 0.25, pcbnew.F_Cu)
    add_via(board, "S1_TOP_PWM", 145.0, 167.75)
    add_path(board, "S1_TOP_PWM", [(145.0, 167.75), (178.0, 167.75), (178.0, 151.5), (182.0, 151.5)], 0.25, pcbnew.B_Cu)
    add_via(board, "S1_TOP_PWM", 182.0, 151.5)
    add_path(board, "S1_TOP_PWM", [(182.0, 151.5), pad_xy("R1", 1), pad_xy("R2", 1)], 0.25, pcbnew.F_Cu)

    add_path(board, "S1_BOT_PWM", [pad_xy("U1", 10), (141.25, 169.02), (146.0, 169.02)], 0.25, pcbnew.F_Cu)
    add_via(board, "S1_BOT_PWM", 146.0, 169.02)
    add_path(board, "S1_BOT_PWM", [(146.0, 169.02), (177.0, 169.02), (177.0, 161.5), (182.0, 161.5)], 0.25, pcbnew.B_Cu)
    add_via(board, "S1_BOT_PWM", 182.0, 161.5)
    add_path(board, "S1_BOT_PWM", [(182.0, 161.5), pad_xy("R3", 1), pad_xy("R4", 1)], 0.25, pcbnew.F_Cu)

    add_path(board, "S2_TOP_PWM", [pad_xy("U1", 11), (141.25, 170.29), (147.0, 170.29)], 0.25, pcbnew.F_Cu)
    add_via(board, "S2_TOP_PWM", 147.0, 170.29)
    add_path(board, "S2_TOP_PWM", [(147.0, 170.29), (176.0, 170.29), (176.0, 171.5), (182.0, 171.5)], 0.25, pcbnew.B_Cu)
    add_via(board, "S2_TOP_PWM", 182.0, 171.5)
    add_path(board, "S2_TOP_PWM", [(182.0, 171.5), pad_xy("R5", 1), pad_xy("R6", 1)], 0.25, pcbnew.F_Cu)

    add_path(board, "S2_BOT_PWM", [pad_xy("U1", 22), (151.91, 175.35), (151.91, 181.5)], 0.25, pcbnew.F_Cu)
    add_via(board, "S2_BOT_PWM", 151.91, 181.5)
    add_path(board, "S2_BOT_PWM", [(151.91, 181.5), (182.0, 181.5)], 0.25, pcbnew.B_Cu)
    add_via(board, "S2_BOT_PWM", 182.0, 181.5)
    add_path(board, "S2_BOT_PWM", [(182.0, 181.5), pad_xy("R7", 1), pad_xy("R8", 1)], 0.25, pcbnew.F_Cu)

    # 5. Universal Drop Sensors
    add_path(board, "Net-(J11-Pin_3)", [pad_xy("J11", 3), pad_xy("R16", 1)], 0.25)
    add_path(board, "Net-(J12-Pin_3)", [pad_xy("J12", 3), pad_xy("R18", 1)], 0.25)
    add_path(board, "DROP_SENS1", [pad_xy("R16", 2), pad_xy("R17", 1), (124.0, 159.5), (124.0, 161.4), pad_xy("U1", 4)], 0.25)
    add_path(board, "DROP_SENS2", [pad_xy("R18", 2), pad_xy("R19", 1), (124.0, 176.5), (124.0, 162.67), pad_xy("U1", 5)], 0.25)
    
    add_path(board, "DROP_TRIG", [pad_xy("U1", 23), (153.18, 178.0)], 0.25, pcbnew.F_Cu)
    add_via(board, "DROP_TRIG", 153.18, 178.0)
    add_path(board, "DROP_TRIG", [(153.18, 178.0), (105.0, 178.0), pad_xy("J12", 2), (105.0, 160.5), pad_xy("J11", 2)], 0.25, pcbnew.B_Cu)

    # 6. I2C & Spares
    add_path(board, "I2C_SDA", [pad_xy("U1", 39), (160.0, 158.86), (160.0, 188.0), pad_xy("R26", 2), (169.54, 188.0), pad_xy("J9", 2)], 0.25)
    add_path(board, "I2C_SCL", [pad_xy("U1", 38), (161.0, 160.13), (161.0, 186.0), (170.82, 186.0), pad_xy("R27", 2), (172.08, 188.0), pad_xy("J9", 3)], 0.25)

    add_path(board, "LIMIT_1_TOP", [pad_xy("U1", 6), (139.0, 163.94)], 0.25, pcbnew.F_Cu)
    add_via(board, "LIMIT_1_TOP", 139.0, 163.94)
    add_path(board, "LIMIT_1_TOP", [(139.0, 163.94), (139.0, 170.0), (183.0, 170.0), pad_xy("J10", 1)], 0.25, pcbnew.B_Cu)

    add_path(board, "LIMIT_1_BOT", [pad_xy("U1", 7), (138.0, 165.21)], 0.25, pcbnew.F_Cu)
    add_via(board, "LIMIT_1_BOT", 138.0, 165.21)
    add_path(board, "LIMIT_1_BOT", [(138.0, 165.21), (138.0, 172.0), (185.54, 172.0), pad_xy("J10", 2)], 0.25, pcbnew.B_Cu)

    add_path(board, "LIMIT_2_TOP", [pad_xy("U1", 12), (137.0, 171.56)], 0.25, pcbnew.F_Cu)
    add_via(board, "LIMIT_2_TOP", 137.0, 171.56)
    add_path(board, "LIMIT_2_TOP", [(137.0, 171.56), (137.0, 174.0), (188.08, 174.0), pad_xy("J10", 3)], 0.25, pcbnew.B_Cu)

    add_path(board, "LIMIT_2_BOT", [pad_xy("U1", 17), (145.56, 175.35), (145.56, 179.0)], 0.25, pcbnew.F_Cu)
    add_via(board, "LIMIT_2_BOT", 145.56, 179.0)
    add_path(board, "LIMIT_2_BOT", [(145.56, 179.0), (190.62, 179.0), pad_xy("J10", 4)], 0.25, pcbnew.B_Cu)

    # 7. UART debug
    add_path(board, "UART_TX_DEBUG", [pad_xy("U1", 37), (158.75, 161.4), (163.0, 161.4)], 0.25, pcbnew.F_Cu)
    add_via(board, "UART_TX_DEBUG", 163.0, 161.4)
    add_path(board, "UART_TX_DEBUG", [(163.0, 161.4), (163.0, 165.0), (128.0, 165.0), (128.0, 190.0), pad_xy("TP7", 1)], 0.25, pcbnew.B_Cu)

    add_path(board, "UART_RX_DEBUG", [pad_xy("U1", 36), (158.75, 162.67), (164.0, 162.67)], 0.25, pcbnew.F_Cu)
    add_via(board, "UART_RX_DEBUG", 164.0, 162.67)
    add_path(board, "UART_RX_DEBUG", [(164.0, 162.67), (164.0, 166.0), (127.0, 166.0), (127.0, 193.0), pad_xy("TP8", 1)], 0.25, pcbnew.B_Cu)

    # 8. LEDs
    add_path(board, "Net-(D2-A)", [pad_xy("D2", 2), pad_xy("R21", 2)], 0.25)
    add_path(board, "Net-(D3-A)", [pad_xy("D3", 2), pad_xy("R22", 2)], 0.25)
    add_path(board, "Net-(D4-A)", [pad_xy("D4", 2), pad_xy("R23", 2)], 0.25)
    add_path(board, "Net-(D5-A)", [pad_xy("D5", 2), pad_xy("R24", 2)], 0.25)
    add_path(board, "Net-(D6-A)", [pad_xy("D6", 2), pad_xy("R25", 2)], 0.25)

    print(f"Routed {len(board.GetTracks())} tracks and vias.")

    # 9. Flood Solid GND Copper Zones on F.Cu and B.Cu
    print("Flooding solid GND planes...")
    gnd_net = board.FindNet("GND")
    for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
        zone = pcbnew.ZONE(board)
        board.Add(zone)
        zone.SetLayer(layer)
        zone.SetNetCode(gnd_net.GetNetCode())
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefGap(mm(0.25))
        zone.SetThermalReliefSpokeWidth(mm(0.40))
        zone.SetMinThickness(mm(0.20))
        
        poly = pcbnew.SHAPE_LINE_CHAIN()
        poly.Append(mm(99.5), mm(99.5))
        poly.Append(mm(200.5), mm(99.5))
        poly.Append(mm(200.5), mm(200.5))
        poly.Append(mm(99.5), mm(200.5))
        poly.SetClosed(True)
        zone.AddPolygon(poly)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("Zones filled.")

    pcbnew.SaveBoard(str(OUT_PCB), board)
    print(f"Stage 2 complete: Board successfully saved to {OUT_PCB}")

if __name__ == "__main__":
    stage1_placement()
    stage2_routing()
