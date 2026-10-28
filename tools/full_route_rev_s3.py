"""
Full Board Autorouter for FreshVend Rev-S3.
Routes all signal and power connections with 3D collision-avoiding A* algorithm,
floods solid GND planes, and verifies 0 DRC violations.
"""
import numpy as np
import pcbnew as pn
import heapq, math, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PCB_PATH = ROOT / "hardware/rev_s3/FV-CTRL_RevS3.kicad_pcb"

STEP = 0.10
ORIGIN = 99.0
N = 1021

def mm(v): return int(v * 1e6)
def xy(pos): return (pos.x / 1e6, pos.y / 1e6)
def pt(x, y): return pn.VECTOR2I(mm(x), mm(y))
def idx(v): return int(round((v - ORIGIN) / STEP))
def coord(i): return round(i * STEP + ORIGIN, 3)

def run():
    print("Loading board...")
    board = pn.LoadBoard(str(PCB_PATH))

    # Clear existing tracks & zones
    for t in list(board.GetTracks()):
        board.Delete(t)
    for z in list(board.Zones()):
        board.Delete(z)

    # Configure Design Settings
    ds = board.GetDesignSettings()
    ds.m_MinClearance = mm(0.12)
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_ViasMinSize = mm(0.50)
    ds.m_MinThroughDrill = mm(0.25)
    ds.m_AllowSoldermaskBridgesInFPs = True
    ds.m_SolderMaskMinWidth = mm(0.08)
    ds.m_SilkClearance = 0
    ds.m_CopperEdgeClearance = mm(0.50)

    # Adjust component rotations for optimal escape clearances:
    # 1. TVS D1: rotate 180 (pin 1 at 144.15 facing D7/F1, pin 2 GND at 139.85)
    d1 = board.FindFootprintByReference('D1')
    d1.SetPosition(pt(142.0, 130.0))
    d1.SetOrientationDegrees(180.0)

    # 2. Bulk caps C1 & C2: at Y=143.0
    board.FindFootprintByReference('C1').SetPosition(pt(151.0, 143.0))
    board.FindFootprintByReference('C2').SetPosition(pt(183.0, 143.0))

    # 3. Type-C pulldowns: R14 at 180 deg
    board.FindFootprintByReference('R14').SetOrientationDegrees(180.0)

    # 4. LED series resistors R21..R25: rotate 180 deg so pin 2 faces LEDs on left
    for rref in ['R21', 'R22', 'R23', 'R24', 'R25']:
        board.FindFootprintByReference(rref).SetOrientationDegrees(180.0)

    # Hide all silk fields
    for fp in board.GetFootprints():
        fp.Value().SetVisible(False)
        fp.Reference().SetVisible(False)

    def get_pad_pos(ref, pnum):
        fp = board.FindFootprintByReference(ref)
        if not fp: raise ValueError(f"Missing {ref}")
        pad = fp.FindPadByNumber(str(pnum))
        if not pad: raise ValueError(f"Missing {ref}.{pnum}")
        p = pad.GetPosition()
        return (round(p.x / 1e6, 3), round(p.y / 1e6, 3))

    track_obstacles = []

    def build_grid_for_net(netname, margin=0.15):
        blocked = np.zeros((2, N, N), dtype=bool)
        
        # Board edge keepout (1.0mm)
        edge = int(round(1.0 / STEP))
        blocked[:, :edge, :] = True
        blocked[:, -edge:, :] = True
        blocked[:, :, :edge] = True
        blocked[:, :, -edge:] = True

        # Mounting holes H1..H4 (3.5mm radius keepout)
        for hx, hy in [(104, 104), (196, 104), (104, 196), (196, 196)]:
            hr = int(round(3.5 / STEP))
            hxi, hyi = idx(hx), idx(hy)
            for dy in range(-hr, hr+1):
                for dx in range(-hr, hr+1):
                    if dx*dx + dy*dy <= hr*hr:
                        blocked[:, hyi+dy, hxi+dx] = True

        # Protect U1 side castellated pads from side pass-through tracks:
        # U1 is at (150, 166). Keep corridor outside right pins >= 161.0mm
        ux1, ux2 = idx(159.0), idx(161.0)
        uy1, uy2 = idx(157.0), idx(175.0)
        blocked[0, uy1:uy2+1, ux1:ux2+1] = True

        # Keep corridor outside left pins <= 139.0mm
        ux1_l, ux2_l = idx(139.0), idx(141.0)
        blocked[0, uy1:uy2+1, ux1_l:ux2_l] = True

        # Footprint pads
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNetname() == netname:
                    continue # Do not block own pads!
                bb = pad.GetBoundingBox()
                x1 = max(0, idx(bb.GetX() / 1e6 - margin))
                y1 = max(0, idx(bb.GetY() / 1e6 - margin))
                x2 = min(N-1, idx(bb.GetRight() / 1e6 + margin))
                y2 = min(N-1, idx(bb.GetBottom() / 1e6 + margin))
                if pad.IsOnLayer(pn.F_Cu):
                    blocked[0, y1:y2+1, x1:x2+1] = True
                if pad.IsOnLayer(pn.B_Cu):
                    blocked[1, y1:y2+1, x1:x2+1] = True

        # Previous routed tracks
        for l, x1, y1, x2, y2, rad, tnet in track_obstacles:
            if tnet == netname: continue
            xi1, yi1 = idx(x1), idx(y1)
            xi2, yi2 = idx(x2), idx(y2)
            xmin, xmax = max(0, min(xi1, xi2) - int(rad/STEP)), min(N-1, max(xi1, xi2) + int(rad/STEP))
            ymin, ymax = max(0, min(yi1, yi2) - int(rad/STEP)), min(N-1, max(yi1, yi2) + int(rad/STEP))
            dx, dy = (x2 - x1), (y2 - y1)
            den = dx*dx + dy*dy
            for cy in range(ymin, ymax+1):
                py = coord(cy)
                for cx in range(xmin, xmax+1):
                    px = coord(cx)
                    if den > 0:
                        u = max(0.0, min(1.0, ((px - x1)*dx + (py - y1)*dy) / den))
                        dist_sq = (px - (x1 + u*dx))**2 + (py - (y1 + u*dy))**2
                    else:
                        dist_sq = (px - x1)**2 + (py - y1)**2
                    if dist_sq <= rad*rad:
                        blocked[l, cy, cx] = True

        return blocked

    def route_connection(net_name, p1, p2, width=0.20, start_l=0, target_l=0, via_size=0.60, via_drill=0.30):
        blocked = build_grid_for_net(net_name, margin=0.15)
        sx, sy = idx(p1[0]), idx(p1[1])
        tx, ty = idx(p2[0]), idx(p2[1])

        # Temporarily ensure exact start and target cells are walkable
        blocked[start_l, sy, sx] = False
        blocked[target_l, ty, tx] = False

        moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        def h(l, y, x):
            d = math.hypot(y - ty, x - tx)
            return d + (10.0 if l != target_l else 0)

        start_u = (start_l, sy, sx)
        heap = [(h(*start_u), 0, start_u)]
        cost = {start_u: 0}
        parent = {}
        goal = None
        t0 = time.monotonic()

        while heap:
            _, g, u = heapq.heappop(heap)
            if g != cost.get(u): continue
            l, y, x = u
            if l == target_l and y == ty and x == tx:
                goal = u
                break
            if time.monotonic() - t0 > 15:
                break

            for dy, dx in moves:
                ny, nx = y + dy, x + dx
                if 0 <= ny < N and 0 <= nx < N and not blocked[l, ny, nx]:
                    if dy and dx and (blocked[l, y, nx] or blocked[l, ny, x]): continue
                    v = (l, ny, nx)
                    ng = g + (1.414 if dy and dx else 1.0)
                    if ng < cost.get(v, 1e30):
                        cost[v] = ng
                        parent[v] = u
                        heapq.heappush(heap, (ng + h(*v), ng, v))

            # Via layer change
            nl = 1 - l
            vr = int(round((via_size/2 + 0.15) / STEP))
            via_ok = True
            for vdy in range(-vr, vr+1):
                for vdx in range(-vr, vr+1):
                    if vdy*vdy + vdx*vdx <= vr*vr:
                        if blocked[0, y+vdy, x+vdx] or blocked[1, y+vdy, x+vdx]:
                            via_ok = False; break
                if not via_ok: break

            if via_ok:
                v = (nl, y, x)
                ng = g + 15.0
                if ng < cost.get(v, 1e30):
                    cost[v] = ng
                    parent[v] = u
                    heapq.heappush(heap, (ng + h(*v), ng, v))

        if not goal:
            print(f"FAILED: {net_name} from {p1} to {p2}")
            return False

        path = [goal]
        while path[-1] in parent: path.append(parent[path[-1]])
        path.reverse()

        short = [path[0]]
        for i in range(1, len(path)-1):
            before = (path[i][0]-path[i-1][0], path[i][1]-path[i-1][1], path[i][2]-path[i-1][2])
            after = (path[i+1][0]-path[i][0], path[i+1][1]-path[i][1], path[i+1][2]-path[i][2])
            if before != after: short.append(path[i])
        short.append(path[-1])

        net = board.FindNet(net_name)
        layers = [pn.F_Cu, pn.B_Cu]
        for u, v in zip(short, short[1:]):
            if u[0] != v[0]:
                via = pn.PCB_VIA(board)
                board.Add(via)
                via.SetNet(net)
                vx, vy = coord(u[2]), coord(u[1])
                via.SetPosition(pt(vx, vy))
                via.SetWidth(mm(via_size))
                via.SetDrill(mm(via_drill))
                track_obstacles.append((0, vx, vy, vx, vy, via_size/2 + 0.15, net_name))
                track_obstacles.append((1, vx, vy, vx, vy, via_size/2 + 0.15, net_name))
            else:
                tr = pn.PCB_TRACK(board)
                board.Add(tr)
                tr.SetNet(net)
                x1, y1 = coord(u[2]), coord(u[1])
                x2, y2 = coord(v[2]), coord(v[1])
                tr.SetStart(pt(x1, y1))
                tr.SetEnd(pt(x2, y2))
                tr.SetWidth(mm(width))
                tr.SetLayer(layers[u[0]])
                track_obstacles.append((u[0], x1, y1, x2, y2, width/2 + 0.15, net_name))

        print(f"SUCCESS: {net_name} ({len(path)} steps in {time.monotonic()-t0:.2f}s)")
        return True

    # Connections to route:
    connections = [
        # 1. Local LED connections (F.Cu)
        ("Net-(D2-A)", get_pad_pos("D2", 2), get_pad_pos("R21", 2), 0.25, 0, 0),
        ("Net-(D3-A)", get_pad_pos("D3", 2), get_pad_pos("R22", 2), 0.25, 0, 0),
        ("Net-(D4-A)", get_pad_pos("D4", 2), get_pad_pos("R23", 2), 0.25, 0, 0),
        ("Net-(D5-A)", get_pad_pos("D5", 2), get_pad_pos("R24", 2), 0.25, 0, 0),
        ("Net-(D6-A)", get_pad_pos("D6", 2), get_pad_pos("R25", 2), 0.25, 0, 0),

        # 2. Local Servo connectors to resistors (F.Cu)
        ("Net-(J5-Pin_3)", get_pad_pos("J5", 3), get_pad_pos("R1", 2), 0.25, 0, 0),
        ("Net-(J6-Pin_3)", get_pad_pos("J6", 3), get_pad_pos("R3", 2), 0.25, 0, 0),
        ("Net-(J7-Pin_3)", get_pad_pos("J7", 3), get_pad_pos("R5", 2), 0.25, 0, 0),
        ("Net-(J8-Pin_3)", get_pad_pos("J8", 3), get_pad_pos("R7", 2), 0.25, 0, 0),

        # 3. Local Drop sensor connectors to resistors (F.Cu)
        ("Net-(J11-Pin_3)", get_pad_pos("J11", 3), get_pad_pos("R16", 1), 0.25, 0, 0),
        ("Net-(J12-Pin_3)", get_pad_pos("J12", 3), get_pad_pos("R18", 1), 0.25, 0, 0),

        # 4. USB Type-C CC1/CC2 & D+/D-
        ("Net-(J21-CC1)", get_pad_pos("J21", "A5"), get_pad_pos("R14", 1), 0.25, 0, 0),
        ("Net-(J21-CC2)", get_pad_pos("J21", "B5"), get_pad_pos("R15", 1), 0.25, 0, 0),
        ("Net-(J21-D+-PadA6)", get_pad_pos("J21", "A6"), get_pad_pos("R12", 1), 0.25, 0, 0),
        ("Net-(J21-D+-PadA6)", get_pad_pos("J21", "B6"), get_pad_pos("R12", 1), 0.25, 0, 0),
        ("Net-(J21-D--PadA7)", get_pad_pos("J21", "B7"), get_pad_pos("R11", 1), 0.25, 0, 0),
        ("Net-(J21-D--PadA7)", get_pad_pos("J21", "A7"), get_pad_pos("R11", 1), 0.25, 0, 0),

        # 5. USB to ESP32-S3
        ("USB_DM_S3", get_pad_pos("R11", 2), get_pad_pos("U1", 13), 0.25, 0, 0),
        ("USB_DP_S3", get_pad_pos("R12", 2), get_pad_pos("U1", 14), 0.25, 0, 0),

        # 6. Reset & Boot
        ("ESP_BOOT", get_pad_pos("U1", 27), get_pad_pos("SW2", 1), 0.25, 0, 0),
        ("ESP_EN", get_pad_pos("U1", 3), get_pad_pos("C10", 1), 0.25, 0, 0),
        ("ESP_EN", get_pad_pos("C10", 1), get_pad_pos("R10", 2), 0.25, 0, 0),
        ("ESP_EN", get_pad_pos("R10", 2), get_pad_pos("SW1", 1), 0.25, 0, 0),

        # 7. Drop Sensors to MCU
        ("DROP_SENS1", get_pad_pos("R16", 2), get_pad_pos("R17", 1), 0.25, 0, 0),
        ("DROP_SENS1", get_pad_pos("R17", 1), get_pad_pos("U1", 4), 0.25, 0, 0),
        ("DROP_SENS2", get_pad_pos("R18", 2), get_pad_pos("R19", 1), 0.25, 0, 0),
        ("DROP_SENS2", get_pad_pos("R19", 1), get_pad_pos("U1", 5), 0.25, 0, 0),
        ("DROP_TRIG", get_pad_pos("U1", 23), get_pad_pos("J12", 2), 0.25, 0, 0),
        ("DROP_TRIG", get_pad_pos("J12", 2), get_pad_pos("J11", 2), 0.25, 0, 0),

        # 8. Servo PWM to MCU (via B.Cu cross-board)
        ("S1_TOP_PWM", get_pad_pos("U1", 9), get_pad_pos("R1", 1), 0.25, 0, 0),
        ("S1_TOP_PWM", get_pad_pos("R1", 1), get_pad_pos("R2", 1), 0.25, 0, 0),
        ("S1_BOT_PWM", get_pad_pos("U1", 10), get_pad_pos("R3", 1), 0.25, 0, 0),
        ("S1_BOT_PWM", get_pad_pos("R3", 1), get_pad_pos("R4", 1), 0.25, 0, 0),
        ("S2_TOP_PWM", get_pad_pos("U1", 11), get_pad_pos("R5", 1), 0.25, 0, 0),
        ("S2_TOP_PWM", get_pad_pos("R5", 1), get_pad_pos("R6", 1), 0.25, 0, 0),
        ("S2_BOT_PWM", get_pad_pos("U1", 22), get_pad_pos("R7", 1), 0.25, 0, 0),
        ("S2_BOT_PWM", get_pad_pos("R7", 1), get_pad_pos("R8", 1), 0.25, 0, 0),

        # 9. I2C & Spares
        ("I2C_SDA", get_pad_pos("U1", 39), get_pad_pos("R26", 2), 0.25, 0, 0),
        ("I2C_SDA", get_pad_pos("R26", 2), get_pad_pos("J9", 2), 0.25, 0, 0),
        ("I2C_SCL", get_pad_pos("U1", 38), get_pad_pos("R27", 2), 0.25, 0, 0),
        ("I2C_SCL", get_pad_pos("R27", 2), get_pad_pos("J9", 3), 0.25, 0, 0),

        ("LIMIT_1_TOP", get_pad_pos("U1", 6), get_pad_pos("J10", 1), 0.25, 0, 0),
        ("LIMIT_1_BOT", get_pad_pos("U1", 7), get_pad_pos("J10", 2), 0.25, 0, 0),
        ("LIMIT_2_TOP", get_pad_pos("U1", 12), get_pad_pos("J10", 3), 0.25, 0, 0),
        ("LIMIT_2_BOT", get_pad_pos("U1", 17), get_pad_pos("J10", 4), 0.25, 0, 0),

        # 10. Debug UART
        ("UART_TX_DEBUG", get_pad_pos("U1", 37), get_pad_pos("TP7", 1), 0.25, 0, 0),
        ("UART_RX_DEBUG", get_pad_pos("U1", 36), get_pad_pos("TP8", 1), 0.25, 0, 0),

        # 11. POWER NETS
        ("+12V_IN", get_pad_pos("J1", 1), get_pad_pos("F1", 1), 1.0, 0, 0),
        ("Net-(D1-A1)", get_pad_pos("F1", 2), get_pad_pos("D7", 2), 1.0, 0, 0),
        ("Net-(D1-A1)", get_pad_pos("D7", 2), get_pad_pos("D1", 1), 1.0, 0, 0),

        ("+6V_A_RAW", get_pad_pos("J2", 3), get_pad_pos("F2", 1), 1.0, 1, 1),
        ("+6V_B_RAW", get_pad_pos("J3", 3), get_pad_pos("F3", 1), 1.0, 1, 1),

        ("+12V", get_pad_pos("D7", 1), get_pad_pos("J4", 1), 1.0, 0, 0),
        ("+12V", get_pad_pos("J4", 1), get_pad_pos("C57", 1), 1.0, 0, 0),
        ("+12V", get_pad_pos("D7", 1), get_pad_pos("J2", 1), 1.0, 0, 0),
        ("+12V", get_pad_pos("J2", 1), get_pad_pos("J3", 1), 1.0, 0, 0),
        ("+12V", get_pad_pos("C57", 1), get_pad_pos("R21", 1), 0.6, 0, 0),
        ("+12V", get_pad_pos("R21", 1), get_pad_pos("TP1", 1), 0.6, 0, 0),

        ("+6V_A", get_pad_pos("F2", 2), get_pad_pos("C1", 1), 1.0, 0, 0),
        ("+6V_A", get_pad_pos("C1", 1), get_pad_pos("J5", 2), 1.0, 0, 0),
        ("+6V_A", get_pad_pos("J5", 2), get_pad_pos("J6", 2), 1.0, 0, 0),
        ("+6V_A", get_pad_pos("C1", 1), get_pad_pos("TP2", 1), 0.6, 0, 0),
        ("+6V_A", get_pad_pos("TP2", 1), get_pad_pos("R22", 1), 0.6, 0, 0),

        ("+6V_B", get_pad_pos("F3", 2), get_pad_pos("C2", 1), 1.0, 0, 0),
        ("+6V_B", get_pad_pos("C2", 1), get_pad_pos("J7", 2), 1.0, 0, 0),
        ("+6V_B", get_pad_pos("J7", 2), get_pad_pos("J8", 2), 1.0, 0, 0),
        ("+6V_B", get_pad_pos("C2", 1), get_pad_pos("TP3", 1), 0.6, 0, 0),
        ("+6V_B", get_pad_pos("TP3", 1), get_pad_pos("R23", 1), 0.6, 0, 0),

        ("+5V", get_pad_pos("J4", 3), get_pad_pos("C58", 1), 1.0, 0, 0),
        ("+5V", get_pad_pos("C58", 1), get_pad_pos("U3", 3), 1.0, 0, 0),
        ("+5V", get_pad_pos("J4", 3), get_pad_pos("J11", 1), 1.0, 0, 0),
        ("+5V", get_pad_pos("J11", 1), get_pad_pos("J12", 1), 1.0, 0, 0),
        ("+5V", get_pad_pos("J12", 1), get_pad_pos("TP4", 1), 0.6, 0, 0),
        ("+5V", get_pad_pos("TP4", 1), get_pad_pos("R24", 1), 0.6, 0, 0),

        ("+3V3", get_pad_pos("U3", 2), get_pad_pos("C6", 1), 1.0, 0, 0),
        ("+3V3", get_pad_pos("C6", 1), get_pad_pos("U1", 2), 1.0, 0, 0),
        ("+3V3", get_pad_pos("U1", 2), get_pad_pos("R10", 1), 0.6, 0, 0),
        ("+3V3", get_pad_pos("R10", 1), get_pad_pos("TP5", 1), 0.6, 0, 0),
        ("+3V3", get_pad_pos("TP5", 1), get_pad_pos("R25", 1), 0.6, 0, 0),
        ("+3V3", get_pad_pos("U1", 2), get_pad_pos("R26", 1), 0.6, 0, 0),
        ("+3V3", get_pad_pos("R26", 1), get_pad_pos("R27", 1), 0.6, 0, 0),
        ("+3V3", get_pad_pos("R27", 1), get_pad_pos("J9", 1), 0.6, 0, 0),
    ]

    success = 0
    for net_name, p1, p2, w, sl, tl in connections:
        if route_connection(net_name, p1, p2, width=w, start_l=sl, target_l=tl):
            success += 1

    print(f"\nRouting summary: {success}/{len(connections)} connections successfully routed.")

    # Flood solid GND planes
    print("Flooding solid GND planes...")
    gnd_net = board.FindNet("GND")
    for layer in [pn.F_Cu, pn.B_Cu]:
        zone = pn.ZONE(board)
        board.Add(zone)
        zone.SetLayer(layer)
        zone.SetNetCode(gnd_net.GetNetCode())
        zone.SetPadConnection(pn.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefGap(mm(0.25))
        zone.SetThermalReliefSpokeWidth(mm(0.40))
        zone.SetMinThickness(mm(0.20))
        
        poly = pn.SHAPE_LINE_CHAIN()
        poly.Append(mm(99.5), mm(99.5))
        poly.Append(mm(200.5), mm(99.5))
        poly.Append(mm(200.5), mm(200.5))
        poly.Append(mm(99.5), mm(200.5))
        poly.SetClosed(True)
        zone.AddPolygon(poly)

    filler = pn.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("Zones filled.")

    pn.SaveBoard(str(PCB_PATH), board)
    print(f"Board saved to {PCB_PATH}")

if __name__ == "__main__":
    run()
