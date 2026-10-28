"""
FreshVend Rev-S3 Incremental Autonomous Router.
Iterates over KiCad DRC unconnected items, shortest distance first.
Verifies each route with native KiCad DRC and rolls back if errors are introduced.
"""
from pathlib import Path
import sys, math, heapq, time, json, re, subprocess, collections
import numpy as np
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
PCB_PATH = ROOT / "hardware/rev_s3/FV-CTRL_RevS3.kicad_pcb"
DRC_JSON = ROOT / "reports/rev_s3/RevS3-routing-drc.json"
CHECKPOINT_PCB = ROOT / "scratch/RevS3-checkpoint.kicad_pcb"
KICAD_CLI = "C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"

STEP = 0.05
ORIGIN = 99.0
N = 2041
LAYERS = [p.F_Cu, p.B_Cu]

def pt(x, y): return p.VECTOR2I(int(x * 1e6), int(y * 1e6))
def xy(v): return (round(v.x / 1e6, 4), round(v.y / 1e6, 4))
def idx(v): return int(round((v - ORIGIN) / STEP))
def coord(i): return round(i * STEP + ORIGIN, 4)

def segment(b, a, c, net, width=0.20, layer=p.F_Cu):
    if a == c: return
    t = p.PCB_TRACK(b)
    t.SetStart(pt(*a))
    t.SetEnd(pt(*c))
    t.SetWidth(int(width * 1e6))
    t.SetLayer(layer)
    t.SetNet(b.FindNet(net))
    b.Add(t)

def via(b, x, y, net="GND", diam=0.50, drill=0.25):
    v = p.PCB_VIA(b)
    v.SetPosition(pt(x, y))
    v.SetWidth(int(diam * 1e6))
    v.SetDrill(int(drill * 1e6))
    v.SetViaType(p.VIATYPE_THROUGH)
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetNet(b.FindNet(net))
    b.Add(v)

def check_drc():
    cmd = [KICAD_CLI, "pcb", "drc", "--format", "json", "--output", str(DRC_JSON), str(PCB_PATH)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    with open(DRC_JSON, "r") as f:
        return json.load(f)

def route(net, start_key, end_key, width=0.20):
    b = p.LoadBoard(str(PCB_PATH))
    refs = {f.GetReference(): f for f in b.GetFootprints()}

    def endpoint(key):
        if key.startswith("="):
            parts = key[1:].split(",")
            return (float(parts[0]), float(parts[1])), [int(parts[2])]
        if key.startswith("@"):
            item = next((t for t in b.GetTracks() if t.m_Uuid.AsString() == key[1:]), None)
            if item:
                assert item.GetNetname() == net
                if item.GetClass() == "PCB_TRACK":
                    return xy(item.GetStart()), [LAYERS.index(item.GetLayer())]
                return xy(item.GetPosition()), [i for i, l in enumerate(LAYERS) if item.IsOnLayer(l)]
            for f in refs.values():
                for pad in f.Pads():
                    if pad.m_Uuid.AsString() == key[1:]:
                        assert pad.GetNetname() == net
                        return xy(pad.GetPosition()), [i for i, l in enumerate(LAYERS) if pad.IsOnLayer(l)]
        ref, pin = key.split(":")
        pad = next(a for a in refs[ref].Pads() if a.GetNumber() == pin)
        assert pad.GetNetname() == net
        return xy(pad.GetPosition()), [i for i, l in enumerate(LAYERS) if pad.IsOnLayer(l)]

    a, la = endpoint(start_key)
    c, lc = endpoint(end_key)

    blocked = np.zeros((2, N, N), dtype=bool)
    vb = np.zeros((N, N), dtype=bool)
    existing_switch = {}

    def limits(x1, y1, x2, y2):
        return (
            max(0, math.ceil((x1 - ORIGIN) / STEP)),
            max(0, math.ceil((y1 - ORIGIN) / STEP)),
            min(N - 1, math.floor((x2 - ORIGIN) / STEP)),
            min(N - 1, math.floor((y2 - ORIGIN) / STEP))
        )

    def rect(mask, bb, margin):
        x1, y1, x2, y2 = limits(bb[0] - margin, bb[1] - margin, bb[2] + margin, bb[3] + margin)
        if x2 >= x1 and y2 >= y1:
            mask[y1:y2+1, x1:x2+1] = True

    def capsule(mask, a, c, r):
        x1, y1, x2, y2 = limits(min(a[0], c[0]) - r, min(a[1], c[1]) - r, max(a[0], c[0]) + r, max(a[1], c[1]) + r)
        if x2 < x1 or y2 < y1: return
        ys, xs = np.mgrid[y1:y2+1, x1:x2+1]
        xs = xs * STEP + ORIGIN
        ys = ys * STEP + ORIGIN
        dx, dy = c[0] - a[0], c[1] - a[1]
        den = dx*dx + dy*dy
        if den > 1e-6:
            u = np.clip(((xs - a[0])*dx + (ys - a[1])*dy) / den, 0.0, 1.0)
            mask[y1:y2+1, x1:x2+1] |= (xs - a[0] - u*dx)**2 + (ys - a[1] - u*dy)**2 <= r*r
        else:
            mask[y1:y2+1, x1:x2+1] |= (xs - a[0])**2 + (ys - a[1])**2 <= r*r

    margin = width / 2.0 + 0.135

    # Footprint pads obstacles
    for f in b.GetFootprints():
        is_fine = f.GetReference() in ["U1", "J21"]
        for pad in f.Pads():
            q = pad.GetBoundingBox()
            bb = (q.GetX() / 1e6, q.GetY() / 1e6, q.GetRight() / 1e6, q.GetBottom() / 1e6)
            own = (pad.GetNetname() == net)
            if own and pad.IsOnLayer(p.F_Cu) and pad.IsOnLayer(p.B_Cu):
                xx, yy = xy(pad.GetPosition())
                existing_switch[(idx(yy), idx(xx))] = (xx, yy)
            if not own:
                pad_m = (width / 2.0 + 0.125) if is_fine else margin
                for i, l in enumerate(LAYERS):
                    if pad.IsOnLayer(l):
                        rect(blocked[i], bb, pad_m)
                rect(vb, bb, 0.42)
            elif pad.GetAttribute() == p.PAD_ATTRIB_SMD:
                rect(vb, bb, 0.30)
            else:
                rect(vb, bb, 0.15)

    # Tracks and vias obstacles
    for t in b.GetTracks():
        if t.GetNetname() == net:
            if t.GetClass() == "PCB_VIA":
                center = xy(t.GetPosition())
                capsule(vb, center, center, t.GetDrillValue() / 2e6 + 0.10 + 0.25)
                existing_switch[(idx(center[1]), idx(center[0]))] = center
            continue
        if t.GetClass() == "PCB_VIA":
            center = xy(t.GetPosition())
            r = t.GetWidth(p.F_Cu) / 2e6
            clearance_radius = max(r + 0.135, t.GetDrillValue() / 2e6 + 0.22) + width / 2.0
            for i in range(2):
                capsule(blocked[i], center, center, clearance_radius)
            capsule(vb, center, center, r + 0.42)
        else:
            aa, cc = xy(t.GetStart()), xy(t.GetEnd())
            r = t.GetWidth() / 2e6
            for i, l in enumerate(LAYERS):
                if t.IsOnLayer(l):
                    capsule(blocked[i], aa, cc, r + margin)
            capsule(vb, aa, cc, r + 0.42)

    # Edge keepout
    edge = math.ceil((0.8 + width / 2.0) / STEP)
    blocked[:, :edge, :] = True
    blocked[:, -edge:, :] = True
    blocked[:, :, :edge] = True
    blocked[:, :, -edge:] = True

    # Mounting holes H1..H4
    for hx, hy in [(104, 104), (196, 104), (104, 196), (196, 196)]:
        capsule(blocked[0], (hx, hy), (hx, hy), 3.5)
        capsule(blocked[1], (hx, hy), (hx, hy), 3.5)
        capsule(vb, (hx, hy), (hx, hy), 3.5)

    def component_anchors(key, original, layers):
        if key.startswith("="): return [(original, layers)]
        seed = None
        if key.startswith("@"):
            seed = next((t for t in b.GetTracks() if t.m_Uuid.AsString() == key[1:]), None)
            if not seed:
                for fp in refs.values():
                    for pad in fp.Pads():
                        if pad.m_Uuid.AsString() == key[1:]:
                            seed = pad; break
                    if seed: break
        else:
            ref, pin = key.split(":")
            seed = next((q for q in refs[ref].Pads() if q.GetNumber() == pin), None)
        if not seed: return [(original, layers)]
        conn = b.GetConnectivity()
        queue = [seed]
        seen = set()
        result = []
        while queue:
            item = queue.pop()
            uid = item.m_Uuid.AsString()
            if uid in seen: continue
            seen.add(uid)
            if item.GetNetname() != net or item.GetClass() not in ["PCB_TRACK", "PCB_VIA", "PAD"]: continue
            ls = [i for i, l in enumerate(LAYERS) if item.IsOnLayer(l)]
            if item.GetClass() == "PCB_TRACK":
                result.extend([(xy(item.GetStart()), ls), (xy(item.GetEnd()), ls)])
            else:
                result.append((xy(item.GetPosition()), ls))
            queue.extend(conn.GetConnectedItems(item))
        return result or [(original, layers)]

    anchors = {}
    def cells(points):
        result = set()
        for (xx, yy), ls in points:
            for layer in ls:
                u = (layer, idx(yy), idx(xx))
                result.add(u)
                anchors[u] = (xx, yy)
        return result

    sources = list(cells(component_anchors(start_key, a, la)))
    targets = cells(component_anchors(end_key, c, lc))
    for u in sources: blocked[u] = False
    for u in targets: blocked[u] = False

    if not sources or not targets:
        raise RuntimeError(f"Endpoints blocked for {net}")

    ty0 = min(u[1] for u in targets)
    ty1 = max(u[1] for u in targets)
    tx0 = min(u[2] for u in targets)
    tx1 = max(u[2] for u in targets)

    moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def h(u):
        return 1.4 * math.hypot(max(ty0 - u[1], 0, u[1] - ty1), max(tx0 - u[2], 0, u[2] - tx1))

    heap = [(h(u), 0, u) for u in sources]
    heapq.heapify(heap)
    cost = {u: 0 for u in sources}
    parent = {}
    goal = None
    t0 = time.monotonic()

    while heap:
        _, g, u = heapq.heappop(heap)
        if g != cost.get(u): continue
        if u in targets:
            goal = u
            break
        if time.monotonic() - t0 > 90.0: break
        l, y, x = u
        for dy, dx in moves:
            yy, xx = y + dy, x + dx
            if yy < 0 or yy >= N or xx < 0 or xx >= N or blocked[l, yy, xx]: continue
            if dy and dx and (blocked[l, y, xx] or blocked[l, yy, x]): continue
            v = (l, yy, xx)
            ng = g + (1.414 if dx and dy else 1.0)
            if ng < cost.get(v, 1e30):
                cost[v] = ng
                parent[v] = u
                heapq.heappush(heap, (ng + h(v), ng, v))

        # Via transition
        nl = 1 - l
        if ((y, x) in existing_switch or not vb[y, x]) and not blocked[nl, y, x]:
            v = (nl, y, x)
            ng = g + (0.1 if (y, x) in existing_switch else 20.0)
            if ng < cost.get(v, 1e30):
                cost[v] = ng
                parent[v] = u
                heapq.heappush(heap, (ng + h(v), ng, v))

    if goal is None:
        raise RuntimeError(f"No route found for {net}")

    path = [goal]
    while path[-1] in parent: path.append(parent[path[-1]])
    path.reverse()

    short = [path[0]]
    for i in range(1, len(path) - 1):
        before = tuple(path[i][j] - path[i-1][j] for j in range(3))
        after = tuple(path[i+1][j] - path[i][j] for j in range(3))
        if before != after: short.append(path[i])
    short.append(path[-1])

    def pos(u):
        return anchors.get(u, existing_switch.get((u[1], u[2]), (coord(u[2]), coord(u[1]))))

    for u, v in zip(short, short[1:]):
        if u[0] != v[0]:
            if (u[1], u[2]) not in existing_switch:
                via(b, *pos(u), net, diam=0.50, drill=0.25)
        else:
            segment(b, pos(u), pos(v), net, width, LAYERS[u[0]])

    b.BuildConnectivity()
    p.ZONE_FILLER(b).Fill(b.Zones())
    p.SaveBoard(str(PCB_PATH), b)

def main():
    failed = set()
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    count = 0

    while count < budget:
        report = check_drc()
        violations = report.get("violations", [])
        baseline_errs = sum(1 for v in violations if v.get("severity") == "error")
        if baseline_errs > 0:
            print(f"Aborting: {baseline_errs} hard DRC violations present. Fix before routing.", flush=True)
            break

        choices = []
        for item in report.get("unconnected_items", []):
            items = item.get("items", [])
            if len(items) != 2: continue
            first, second = items
            m = re.search(r"\[([^]]+)\]", first.get("description", ""))
            if not m: continue
            net = m.group(1)
            if net == "GND" or "Zone" in first.get("description", "") or "Zone" in second.get("description", ""):
                continue
            if net.startswith("unconnected-"):
                continue

            pair = (net, "@" + first["uuid"], "@" + second["uuid"])
            sig = (net, *sorted(pair[1:]))
            if sig in failed: continue

            dx = first["pos"]["x"] - second["pos"]["x"]
            dy = first["pos"]["y"] - second["pos"]["y"]
            dist = math.hypot(dx, dy)
            choices.append((dist, pair, first, second))

        if not choices:
            print(f"No more routable unconnected items! Total routed in this pass: {count}", flush=True)
            break

        dist, pair, first, second = min(choices, key=lambda x: x[0])
        net, k1, k2 = pair
        sig = (net, *sorted(pair[1:]))

        # Determine wire width
        is_u1 = "U1" in first["description"] or "U1" in second["description"]
        if is_u1:
            width = 0.18
        elif net in ["+12V", "+12V_IN", "+6V_A", "+6V_B", "+6V_A_RAW", "+6V_B_RAW"]:
            width = 0.50
        elif net in ["+5V", "+3V3"]:
            width = 0.35
        else:
            width = 0.20

        print(f"Attempting {net} (dist={dist:.2f}mm, width={width:.2f}mm): {first['description']} -> {second['description']}", flush=True)

        # Checkpoint before route
        before_bytes = PCB_PATH.read_bytes()

        try:
            route(net, k1, k2, width)
        except Exception as e:
            if width > 0.20:
                print(f"Retry {net} with narrower width 0.20mm due to: {e}", flush=True)
                try:
                    route(net, k1, k2, 0.20)
                except Exception as e2:
                    print(f"Failed {net}: {e2}", flush=True)
                    failed.add(sig)
                    continue
            else:
                print(f"Failed {net}: {e}", flush=True)
                failed.add(sig)
                continue

        # Verify DRC
        after_report = check_drc()
        after_errs = sum(1 for v in after_report.get("violations", []) if v.get("severity") == "error")

        if after_errs > baseline_errs:
            print(f"Rolled back: Route caused {after_errs - baseline_errs} new DRC error(s)", flush=True)
            PCB_PATH.write_bytes(before_bytes)
            failed.add(sig)
            continue

        count += 1
        rem = len(after_report.get("unconnected_items", []))
        print(f"VERIFIED route #{count}: {net} committed. Remaining opens: {rem}", flush=True)

    print(f"Batch routing ended. Completed {count} routes, {len(failed)} deferred.", flush=True)

if __name__ == "__main__":
    main()
