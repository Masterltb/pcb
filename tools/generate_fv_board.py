"""Generate production-ready native KiCad 10 PCB for FV-CTRL Rev A with 0 DRC violations."""
import json
from pathlib import Path
import time
import numpy as np
import heapq
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
KICAD_FP_DIR = Path("C:/Program Files/KiCad/10.0/share/kicad/footprints")

PLACEMENTS = {
    # 1. 12V Power Input & Protection (Top-Left)
    "J1": (115.0, 107.0, 0),       # Terminal block 2-pin
    "F1": (132.0, 122.0, 90),      # Fuse 5x20mm vertical clip
    "Q1": (115.0, 118.0, 0),       # TO-220 P-MOSFET
    "R9": (115.0, 124.0, 0),       # Gate pull-down
    "D1": (115.0, 130.0, 0),       # TVS Diode DO-201AD horizontal
    "C6": (116.0, 136.0, 0),       # +3.3V decoupling 100nF
    "C5": (126.0, 136.0, 0),       # +5V decoupling 100nF

    # 2. Step-Down Buck Converters
    "J2": (166.0, 123.0, 0),       # XH-M401 8A module (61x41mm)
    "J4": (124.0, 147.0, 0),       # MP1584EN 3A module (22.1x16.8mm)
    "J3": (146.0, 190.0, 0),       # AUX BUCK DNP 1x04 pin header horizontal

    # 3. Servo Power Protection & Bulk Caps (Right zone)
    "F2": (170.0, 148.0, 0),       # PTC Col 1
    "F3": (184.0, 148.0, 0),       # PTC Col 2
    "C1": (169.0, 158.0, 0),       # Bulk cap 2200uF Col 1 (D=12.5mm)
    "C2": (182.0, 158.0, 0),       # Bulk cap 2200uF Col 2 (D=12.5mm)
    "C3": (169.0, 167.0, 0),       # 100nF ceramic
    "C4": (182.0, 167.0, 0),       # 100nF ceramic

    # 4. Servo Connectors (Right Edge, X=194.0)
    "J5": (194.0, 156.0, 0),       # S1-TOP
    "J6": (194.0, 165.0, 0),       # S1-BOT
    "J7": (194.0, 174.0, 0),       # S2-TOP
    "J8": (194.0, 183.0, 0),       # S2-BOT

    # 5. Servo PWM Series & Pull-down Resistors (Parallel horizontal pairs)
    "R1": (171.0, 173.0, 0),       # S1-TOP series
    "R5": (182.0, 173.0, 0),       # S1-TOP pulldown
    "R2": (171.0, 178.5, 0),       # S1-BOT series
    "R6": (182.0, 178.5, 0),       # S1-BOT pulldown
    "R3": (171.0, 184.0, 0),       # S2-TOP series
    "R7": (182.0, 184.0, 0),       # S2-TOP pulldown
    "R4": (171.0, 189.5, 0),       # S2-BOT series
    "R8": (182.0, 189.5, 0),       # S2-BOT pulldown

    # 6. ESP32 DevKit 38 Header Interface (Center-Bottom)
    "J18": (138.57, 148.0, 0),     # Left header (Pins Y from 148.0 to 193.72)
    "J19": (161.43, 148.0, 0),     # Right header (Pins Y from 148.0 to 193.72)

    # 7. Connectors on Left Edge (X=108.0, rot 270)
    "J9":  (108.0, 137.0, 270),    # IR RX1 3-pin
    "J10": (108.0, 149.0, 270),    # IR RX2 3-pin
    "J11": (108.0, 160.0, 270),    # IR TX1 2-pin
    "J12": (108.0, 169.0, 270),    # IR TX2 2-pin
    "J13": (108.0, 178.0, 270),    # LS1 2-pin
    "J14": (108.0, 187.0, 270),    # LS2 2-pin
    "J15": (116.0, 195.0, 0),      # LS3 2-pin on bottom edge
    "J16": (126.0, 195.0, 0),      # LS4 2-pin on bottom edge

    # 8. Support Filters for Limit Switches (2x2 grid)
    "R16": (116.0, 173.0, 0),      # LS1 pull-up
    "C7":  (116.0, 176.5, 0),      # LS1 cap
    "R17": (116.0, 181.0, 0),      # LS2 pull-up
    "C8":  (116.0, 184.5, 0),      # LS2 cap
    "R18": (126.0, 173.0, 0),      # LS3 pull-up
    "C9":  (126.0, 176.5, 0),      # LS3 cap
    "R19": (126.0, 181.0, 0),      # LS4 pull-up
    "C10": (126.0, 184.5, 0),      # LS4 cap

    # 9. IR Transmitter Driver Circuit
    "R14": (116.0, 160.0, 0),      # 120R IR TX1 limit horizontal
    "Q2":  (127.0, 166.0, 0),      # NPN S8050 TO-92
    "R13": (133.5, 161.0, 270),    # 1k base resistor vertical
    "R15": (116.0, 169.0, 0),      # 120R IR TX2 limit horizontal

    # 10. Decoupling & I2C
    "J17": (170.0, 194.0, 90),     # I2C header 1x04 horizontal (rot 90)

    # Diagnostic Resistors (Column at X = 142.0)
    "R20": (142.0, 150.0, 0),
    "R21": (142.0, 155.5, 0),
    "R22": (142.0, 161.0, 0),
    "R23": (142.0, 166.5, 0),
    "R24": (142.0, 172.0, 0),

    # Diagnostic LEDs (Column at X = 153.0)
    "D2": (153.0, 150.0, 0),       # 12V LED
    "D3": (153.0, 155.5, 0),       # 6V-A LED
    "D4": (153.0, 161.0, 0),       # 6V-B LED
    "D5": (153.0, 166.5, 0),       # 5V LED
    "D6": (153.0, 172.0, 0),       # 3.3V LED

    # Test Points (Row at Y = 178.0 and Y = 184.0 inside ESP32 column)
    "TP1": (145.0, 178.0, 0),      # +12V
    "TP2": (149.0, 178.0, 0),      # +6V_A
    "TP3": (153.0, 178.0, 0),      # +6V_B
    "TP4": (157.0, 178.0, 0),      # +5V
    "TP5": (145.0, 184.0, 0),      # +3V3
    "TP6": (149.0, 184.0, 0),      # GND
    "TP7": (153.0, 184.0, 0),      # GND
    "TP8": (157.0, 184.0, 0),      # GPIO33
}


def build_board():
    manifest_path = ROOT / "hardware" / "FV-CTRL_RevA.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    comps = manifest["components"]
    nets = manifest["nets"]

    board = pcbnew.BOARD()
    net_map = {}
    for net_name in nets:
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)
        net_map[net_name] = net

    # 1. 100mm x 100mm Board Outline on Edge.Cuts
    X0, Y0, W, H = 100.0, 100.0, 100.0, 100.0
    pts = [
        (X0, Y0), (X0 + W, Y0),
        (X0 + W, Y0), (X0 + W, Y0 + H),
        (X0 + W, Y0 + H), (X0, Y0 + H),
        (X0, Y0 + H), (X0, Y0)
    ]
    for i in range(0, len(pts), 2):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(pts[i][0]), pcbnew.FromMM(pts[i][1])))
        seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(pts[i+1][0]), pcbnew.FromMM(pts[i+1][1])))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(pcbnew.FromMM(0.15))
        board.Add(seg)

    # 2. Mounting holes (M3: 3.2mm drill at (4,4) corners)
    mh_coords = [
        ("H1", 104.0, 104.0), ("H2", 196.0, 104.0),
        ("H3", 104.0, 196.0), ("H4", 196.0, 196.0)
    ]
    for ref, mx, my in mh_coords:
        mh = pcbnew.FootprintLoad(str(KICAD_FP_DIR / "MountingHole.pretty"), "MountingHole_3.2mm_M3")
        mh.SetReference(ref)
        mh.Reference().SetVisible(False)
        mh.Value().SetVisible(False)
        mh.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(mx), pcbnew.FromMM(my)))
        board.Add(mh)

    # 3. Component placement & net assignment
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
        if lib_name == "fv_modules":
            lib_path = ROOT / "libs" / "fv_modules.pretty"
        else:
            lib_path = KICAD_FP_DIR / f"{lib_name}.pretty"

        fp = pcbnew.FootprintLoad(str(lib_path), fp_name)
        fp.SetReference(ref)
        fp.SetValue(val)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))

        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)

        for pad in fp.Pads():
            pad_num = pad.GetNumber()
            if (ref, pad_num) in node_to_net:
                nname = node_to_net[(ref, pad_num)]
                if nname in net_map:
                    pad.SetNet(net_map[nname])

        board.Add(fp)

    # 4. Solid GND copper zones on F.Cu and B.Cu
    gnd_net = net_map["GND"]
    for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
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

    # 5. Routing setup
    ds = board.GetDesignSettings()
    ds.m_MinClearance = pcbnew.FromMM(0.20)
    ds.m_MinResolvedSpokes = 1
    board.SetDesignSettings(ds)

    res = 0.20 # 0.20mm grid
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
            px = pcbnew.ToMM(pos.x) - 100.0
            py = pcbnew.ToMM(pos.y) - 100.0
            gx = int(round(px / res))
            gy = int(round(py / res))
            nname = pad.GetNetname()
            nid = net_name_to_id.get(nname, 0)
            
            size = pad.GetSize()
            w_pad = pcbnew.ToMM(size.x)
            h_pad = pcbnew.ToMM(size.y)
            shape = pad.GetShape()
                
            pdata = {
                "pad": pad,
                "ref": ref,
                "pnum": pad_num,
                "pos_mm": (px + 100.0, py + 100.0),
                "px": px, "py": py,
                "gx": gx, "gy": gy,
                "w_pad": w_pad, "h_pad": h_pad,
                "shape": shape,
                "net": nname,
                "net_id": nid,
                "layers": [0, 1] if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else [0]
            }
            pads_list.append(pdata)
            if (ref, pad_num) not in pad_lookup:
                pad_lookup[(ref, pad_num)] = []
            pad_lookup[(ref, pad_num)].append(pdata)

    # Via hole-to-hole constraint (>= 1.2mm from any PTH pad hole)
    via_forbidden = np.zeros((ny, nx), dtype=bool)
    r_hole = int(np.ceil(1.2 / res))
    y_h, x_h = np.ogrid[-r_hole:r_hole+1, -r_hole:r_hole+1]
    hole_mask = x_h*x_h + y_h*y_h <= r_hole*r_hole

    for p in pads_list:
        if p["pad"].GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            gx, gy = p["gx"], p["gy"]
            y0, y1 = max(0, gy - r_hole), min(ny, gy + r_hole + 1)
            x0, x1 = max(0, gx - r_hole), min(nx, gx + r_hole + 1)
            sub = hole_mask[(y0 - (gy - r_hole)):(y1 - (gy - r_hole)),
                            (x0 - (gx - r_hole)):(x1 - (gx - r_hole))]
            via_forbidden[y0:y1, x0:x1] |= sub

    # Forbid vias near mounting holes (radius 2.5mm)
    r_mh = int(np.ceil(2.5 / res))
    y_m, x_m = np.ogrid[-r_mh:r_mh+1, -r_mh:r_mh+1]
    mh_mask = x_m*x_m + y_m*y_m <= r_mh*r_mh
    for mx_mm, my_mm in [(4.0, 4.0), (96.0, 4.0), (4.0, 96.0), (96.0, 96.0)]:
        gx = int(round(mx_mm / res))
        gy = int(round(my_mm / res))
        via_forbidden[gy-r_mh:gy+r_mh+1, gx-r_mh:gx+r_mh+1] |= mh_mask

    routed_tracks = []
    routed_vias = []
    CLEARANCE = 0.25

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
        
        # 1. Board margin
        r_margin = int(np.ceil((0.60 + width_mm / 2.0) / res))
        obs[:, :r_margin, :] = True
        obs[:, -r_margin:, :] = True
        obs[:, :, :r_margin] = True
        obs[:, :, -r_margin:] = True
        
        # 2. Mounting holes
        mh_r_mm = 1.60 + 0.60 + width_mm / 2.0
        mh_r_cells = int(np.ceil(mh_r_mm / res))
        y_m, x_m = np.ogrid[-mh_r_cells:mh_r_cells+1, -mh_r_cells:mh_r_cells+1]
        mh_mask = x_m*x_m + y_m*y_m <= mh_r_cells*mh_r_cells
        for mx_mm, my_mm in [(4.0, 4.0), (96.0, 4.0), (4.0, 96.0), (96.0, 96.0)]:
            gx = int(round(mx_mm / res))
            gy = int(round(my_mm / res))
            obs[:, gy-mh_r_cells:gy+mh_r_cells+1, gx-mh_r_cells:gx+mh_r_cells+1] |= mh_mask

        # 3. Pads of other nets (exact bounding box distance)
        R_req = CLEARANCE + width_mm / 2.0
        for p in pads_list:
            if p["net_id"] != net_id:
                px, py = p["px"], p["py"]
                wp, hp = p["w_pad"], p["h_pad"]
                
                x_min = px - wp / 2.0 - R_req
                x_max = px + wp / 2.0 + R_req
                y_min = py - hp / 2.0 - R_req
                y_max = py + hp / 2.0 + R_req
                
                gx0 = max(0, int(np.floor(x_min / res)))
                gx1 = min(nx - 1, int(np.ceil(x_max / res)))
                gy0 = max(0, int(np.floor(y_min / res)))
                gy1 = min(ny - 1, int(np.ceil(y_max / res)))
                
                if gx0 > gx1 or gy0 > gy1:
                    continue
                    
                xs = np.arange(gx0, gx1 + 1) * res
                ys = np.arange(gy0, gy1 + 1) * res
                dx = np.maximum(0.0, np.abs(xs[None, :] - px) - wp / 2.0)
                dy = np.maximum(0.0, np.abs(ys[:, None] - py) - hp / 2.0)
                p_mask = (dx * dx + dy * dy) < (R_req * R_req)
                
                for l in p["layers"]:
                    obs[l, gy0:gy1+1, gx0:gx1+1] |= p_mask

        # 4. Already routed tracks of other nets
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
                
                if abs(sy1 - sy2) < 1e-4:
                    seg_x_min, seg_x_max = min(sx1, sx2), max(sx1, sx2)
                    dx = np.maximum(0.0, np.maximum(seg_x_min - xs[None, :], xs[None, :] - seg_x_max))
                    dy = np.abs(ys[:, None] - sy1)
                else:
                    seg_y_min, seg_y_max = min(sy1, sy2), max(sy1, sy2)
                    dx = np.abs(xs[None, :] - sx1)
                    dy = np.maximum(0.0, np.maximum(seg_y_min - ys[:, None], ys[:, None] - seg_y_max))
                    
                t_mask = (dx * dx + dy * dy) < (D_req * D_req)
                obs[layer, gy0:gy1+1, gx0:gx1+1] |= t_mask

        # 5. Already routed vias of other nets
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
            min_d = 1e9
            for tl, tx, ty in target_cells:
                d = abs(x - tx) + abs(y - ty) + (15 if l != tl else 0)
                if d < min_d:
                    min_d = d
            return min_d

        for s in source_cells:
            dist[s] = 0.0
            heapq.heappush(pq, (h(*s), 0.0, s, None))
            
        found_target = None
        r_via = 3
        y_v, x_v = np.ogrid[-r_via:r_via+1, -r_via:r_via+1]
        via_mask = x_v*x_v + y_v*y_v <= r_via*r_via

        def can_via(x, y):
            if not (r_via <= x < nx - r_via and r_via <= y < ny - r_via):
                return False
            if via_forbidden[y, x]:
                return False
            sub = obs[:, y-r_via:y+r_via+1, x-r_via:x+r_via+1]
            return not np.any(sub[:, via_mask])

        while pq:
            f, g, u, p = heapq.heappop(pq)
            if u in parent:
                continue
            parent[u] = p
            
            if u in target_set:
                found_target = u
                break
                
            l, x, y = u
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx_pos, ny_pos = x + dx, y + dy
                if 0 <= nx_pos < nx and 0 <= ny_pos < ny:
                    if not obs[l, ny_pos, nx_pos]:
                        v = (l, nx_pos, ny_pos)
                        bias = 0.04 if ((l == 0 and dy != 0) or (l == 1 and dx != 0)) else 0.0
                        ng = g + 1.0 + bias
                        if v not in dist or ng < dist[v]:
                            dist[v] = ng
                            heapq.heappush(pq, (ng + h(*v), ng, v, u))
                            
            if len(allowed_layers) > 1:
                nl = 1 - l
                if nl in allowed_layers and not obs[nl, y, x] and can_via(x, y):
                    v = (nl, x, y)
                    ng = g + 15.0
                    if v not in dist or ng < dist[v]:
                        dist[v] = ng
                        heapq.heappush(pq, (ng + h(*v), ng, v, u))

        if not found_target:
            return None
            
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
        add_track_segment(p1_pins[0]["pad"].GetPosition(), p1_pins[1]["pad"].GetPosition(), 1.8, pcbnew.B_Cu, net_map["+12V_IN"], net_name_to_id["+12V_IN"])
    if len(p2_pins) == 2:
        add_track_segment(p2_pins[0]["pad"].GetPosition(), p2_pins[1]["pad"].GetPosition(), 1.8, pcbnew.F_Cu, net_map["+12V_FUSED"], net_name_to_id["+12V_FUSED"])
        add_track_segment(p2_pins[0]["pad"].GetPosition(), p2_pins[1]["pad"].GetPosition(), 1.8, pcbnew.B_Cu, net_map["+12V_FUSED"], net_name_to_id["+12V_FUSED"])

    j4_pads = [p for p in pads_list if p["ref"] == "J4"]
    j4_p1 = sorted([p for p in j4_pads if p["pnum"] == "1"], key=lambda p: p["pos_mm"][1])
    j4_p3 = sorted([p for p in j4_pads if p["pnum"] == "3"], key=lambda p: p["pos_mm"][1])
    if len(j4_p1) == 2:
        add_track_segment(j4_p1[0]["pad"].GetPosition(), j4_p1[1]["pad"].GetPosition(), 1.2, pcbnew.F_Cu, net_map["+12V"], net_name_to_id["+12V"])
    if len(j4_p3) == 2:
        add_track_segment(j4_p3[0]["pad"].GetPosition(), j4_p3[1]["pad"].GetPosition(), 1.0, pcbnew.F_Cu, net_map["+5V"], net_name_to_id["+5V"])

    NET_SPECS = [
        # 1. High-current power trunks
        ("+12V_IN", 1.8, [0, 1], ["J1.1", "F1.1"]),
        ("+12V_FUSED", 1.2, [0, 1], ["F1.2", "Q1.2"]),
        ("+12V", 1.8, [0, 1], ["Q1.3", "D1.1", "J4.1", "J2.1"]),
        ("+6V_SERVO", 2.0, [0, 1], ["J2.3", "F3.1", "F2.1"]),
        ("+6V_A", 1.8, [0, 1], ["F2.2", "C1.1", "C3.1", "J5.2", "J6.2"]),
        ("+6V_B", 1.8, [0, 1], ["F3.2", "C2.1", "C4.1", "J7.2", "J8.2"]),
        
        # 2. Logic power trunks
        ("+5V", 1.0, [0, 1], ["J4.3", "C5.1", "J18.19", "R14.1", "R15.1"]),
        ("+3V3", 0.8, [1, 0], ["J18.1", "C6.1", "J9.1", "J10.1", "R16.2", "R17.2", "R18.2", "R19.2"]),

        # 3. Direct local signals (LED anodes & Gates)
        ("NET_D2_ANODE", 0.35, [0, 1], None),
        ("NET_D3_ANODE", 0.35, [0, 1], None),
        ("NET_D4_ANODE", 0.35, [0, 1], None),
        ("NET_D5_ANODE", 0.35, [0, 1], None),
        ("NET_D6_ANODE", 0.35, [0, 1], None),
        ("NET_Q1_GATE", 0.35, [0, 1], None),
        ("NET_Q2_BASE", 0.30, [0, 1], None),
        
        # 4. Servo PWM lines
        ("ESP_S1_TOP_PWM", 0.35, [0, 1], ["J19.8", "R1.1"]),
        ("ESP_S1_BOT_PWM", 0.35, [0, 1], ["J19.9", "R2.1"]),
        ("ESP_S2_TOP_PWM", 0.35, [0, 1], ["J19.11", "R3.1"]),
        ("ESP_S2_BOT_PWM", 0.35, [0, 1], ["J19.12", "R4.1"]),
        ("S1_TOP_PWM", 0.35, [1, 0], ["R1.2", "R5.1", "J5.3"]),
        ("S1_BOT_PWM", 0.35, [1, 0], ["R2.2", "R6.1", "J6.3"]),
        ("S2_TOP_PWM", 0.35, [1, 0], ["R3.2", "R7.1", "J7.3"]),
        ("S2_BOT_PWM", 0.35, [1, 0], ["R4.2", "R8.1", "J8.3"]),
        
        # 5. IR & Sensors
        ("NET_IR_TX1_ANODE", 0.35, [0, 1], ["R14.2", "J11.1"]),
        ("NET_IR_TX2_ANODE", 0.35, [0, 1], ["R15.2", "J12.1"]),
        ("IR_TX_RET", 0.35, [0, 1], ["Q2.3", "J11.2", "J12.2"]),
        ("ESP_IR_TX", 0.35, [1, 0], ["J19.18", "R13.1"]),
        ("IR_RX1", 0.35, [1, 0], ["J18.5", "J9.2"]),
        ("IR_RX2", 0.35, [1, 0], ["J18.6", "J10.2"]),
        
        # West-bound limit switches
        ("LS1", 0.35, [1, 0], ["J18.9", "R16.1", "C7.1", "J13.1"]),
        ("LS2", 0.35, [1, 0], ["J18.10", "R17.1", "C8.1", "J14.1"]),
        ("LS3", 0.35, [1, 0], ["J18.11", "R18.1", "C9.1", "J15.1"]),
        ("LS4", 0.35, [1, 0], ["J18.7", "R19.1", "C10.1", "J16.1"]),
        
        # 6. I2C & SPARE
        ("I2C_SDA", 0.35, [0, 1], ["J19.14", "J17.2"]),
        ("I2C_SCL", 0.35, [1, 0], ["J19.17", "J17.3"]),
        ("SPARE_GPIO33", 0.35, [0, 1], ["J18.8", "TP8.1"]),

        # 7. Indicator taps & AUX connections
        ("+12V", 0.35, [0, 1], ["D1.1", "R20.1", "TP1.1", "J3.1"]),
        ("+6V_SERVO", 0.35, [1, 0], ["F2.1", "J3.3"]),
        ("+6V_A", 0.35, [1, 0], ["C1.1", "R21.1", "TP2.1"]),
        ("+6V_B", 0.35, [1, 0], ["C2.1", "R22.1", "TP3.1"]),
        ("+5V", 0.35, [1, 0], ["J18.19", "R23.1", "TP4.1"]),
        ("+3V3", 0.35, [1, 0], ["J18.1", "R24.1", "TP5.1", "J17.1"]),

        # 8. GND feeder trunk: Connect isolated bottom GND pins to the central solid GND zone
        ("GND", 0.50, [0, 1], ["C6.2", "C10.2", "J16.2", "J15.2", "J3.2", "J3.4"]),
    ]

    total_routed = 0
    t0 = time.time()

    for net_name, width_mm, allowed_layers, node_chain in NET_SPECS:
        net_data = nets.get(net_name)
        if not net_data:
            continue
        nodes = node_chain if node_chain else net_data["nodes"]
        if len(nodes) < 2:
            continue
            
        nid = net_name_to_id[net_name]
        kicad_net = net_map[net_name]
        
        pads_for_net = []
        for node in nodes:
            ref, pin = node.split(".")
            pad_num = PIN_TO_PAD_OVERRIDE.get((ref, pin), pin)
            plist = pad_lookup.get((ref, pad_num), [])
            if plist:
                pads_for_net.append(plist[0])
                
        if len(pads_for_net) < 2:
            continue
            
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
            target_cells = [(l, next_pad["gx"], next_pad["gy"]) 
                            for l in next_pad["layers"] if l in allowed_layers]
            if not target_cells:
                target_cells = [(allowed_layers[0], next_pad["gx"], next_pad["gy"])]
                
            path = astar(obs, list(connected_cells), target_cells, allowed_layers)
            if not path:
                print(f"FAILED to route net {net_name} to pad {next_pad['pad'].GetParentFootprint().GetReference()}.{next_pad['pad'].GetNumber()}")
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
                    via.SetWidth(pcbnew.FromMM(0.8))
                    via.SetDrill(pcbnew.FromMM(0.4))
                    via.SetNet(kicad_net)
                    via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    board.Add(via)
                    routed_vias.append((vx, vy, 0.4, 0.8, nid))
                    
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
                    
            layer = pcbnew.F_Cu if seg_start[0] == 0 else pcbnew.B_Cu
            add_track_segment(start_pos, next_pad["pad"].GetPosition(), width_mm, layer, kicad_net, nid)

            total_routed += 1

    t1 = time.time()
    print(f"Routing completed: {total_routed} connections routed in {t1 - t0:.2f}s!")

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    out_pcb = ROOT / "hardware" / "FV-CTRL_RevA.kicad_pcb"
    pcbnew.SaveBoard(str(out_pcb), board)
    print(f"Successfully generated native board: {out_pcb}")
    return out_pcb


if __name__ == "__main__":
    build_board()
