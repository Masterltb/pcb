"""Dedicated router for the 7 remaining RevB MCU logic nets.
Creates clean perpendicular escapes outside the U1 keepout,
places DRC-compliant vias, and completes the connection to target pads on B.Cu.
"""
from pathlib import Path
import sys, math, heapq, time
import pcbnew as pn
import numpy as np

ROOT = Path(r"F:\project\pcb")
FILE = ROOT / "hardware/revb/FV-CTRL_RevB.kicad_pcb"

STEP = 0.05
ORIGIN = 100.0
N = 2001

def xy(pos): return (pn.ToMM(pos.x), pn.ToMM(pos.y))
def pt(x, y): return pn.VECTOR2I(pn.FromMM(x), pn.FromMM(y))
def idx(v): return round((v - ORIGIN) / STEP)

def add_track(b, netname, x1, y1, x2, y2, layer=pn.F_Cu, width=0.15):
    t = pn.PCB_TRACK(b)
    t.SetStart(pt(x1, y1))
    t.SetEnd(pt(x2, y2))
    t.SetWidth(pn.FromMM(width))
    t.SetLayer(layer)
    t.SetNet(b.FindNet(netname))
    b.Add(t)
    return t

def add_via(b, netname, x, y, diam=0.40, drill=0.20):
    v = pn.PCB_VIA(b)
    v.SetPosition(pt(x, y))
    v.SetWidth(pn.FromMM(diam))
    v.SetDrill(pn.FromMM(drill))
    v.SetViaType(pn.VIATYPE_THROUGH)
    v.SetLayerPair(pn.F_Cu, pn.B_Cu)
    v.SetNet(b.FindNet(netname))
    b.Add(v)
    return v

def limits(x1, y1, x2, y2):
    return max(0, math.ceil((x1 - ORIGIN) / STEP)), max(0, math.ceil((y1 - ORIGIN) / STEP)), min(N - 1, math.floor((x2 - ORIGIN) / STEP)), min(N - 1, math.floor((y2 - ORIGIN) / STEP))

def rect(mask, bb, margin):
    x1, y1, x2, y2 = limits(bb[0] - margin, bb[1] - margin, bb[2] + margin, bb[3] + margin)
    if x2 >= x1 and y2 >= y1: mask[y1:y2 + 1, x1:x2 + 1] = True

def capsule(mask, a, c, r):
    x1, y1, x2, y2 = limits(min(a[0], c[0]) - r, min(a[1], c[1]) - r, max(a[0], c[0]) + r, max(a[1], c[1]) + r)
    if x2 < x1 or y2 < y1: return
    ys, xs = np.mgrid[y1:y2 + 1, x1:x2 + 1]; xs = xs * STEP + ORIGIN; ys = ys * STEP + ORIGIN
    dx, dy = c[0] - a[0], c[1] - a[1]; den = dx * dx + dy * dy
    u = np.clip(((xs - a[0]) * dx + (ys - a[1]) * dy) / den, 0, 1) if den else 0
    mask[y1:y2 + 1, x1:x2 + 1] |= (xs - a[0] - u * dx) ** 2 + (ys - a[1] - u * dy) ** 2 <= r * r

def build_bcu_obstacle_grid(b, netname, width=0.20):
    blocked = np.zeros((N, N), dtype=bool)
    margin = width / 2 + 0.125 # 0.12mm native design clearance + 5um raster guard
    
    # Pads on B.Cu
    for f in b.GetFootprints():
        for pad in f.Pads():
            if pad.GetNetname() == netname: continue
            if pad.IsOnLayer(pn.B_Cu):
                q = pad.GetBoundingBox()
                bb = tuple(pn.ToMM(v) for v in [q.GetX(), q.GetY(), q.GetRight(), q.GetBottom()])
                rect(blocked, bb, margin)
                
    # Tracks and Vias
    for t in b.GetTracks():
        if t.GetNetname() == netname: continue
        if t.GetClass() == 'PCB_VIA':
            center = xy(t.GetPosition())
            r = pn.ToMM(t.GetWidth(pn.B_Cu)) / 2
            clearance_radius = max(r + 0.125, pn.ToMM(t.GetDrillValue()) / 2 + 0.245) + width / 2
            capsule(blocked, center, center, clearance_radius)
        elif t.GetLayer() == pn.B_Cu:
            aa, cc = xy(t.GetStart()), xy(t.GetEnd())
            r = pn.ToMM(t.GetWidth()) / 2
            capsule(blocked, aa, cc, r + margin)
            
    # Keepouts on B.Cu
    for z in b.Zones():
        if not z.GetIsRuleArea() or not z.GetDoNotAllowTracks() or not z.IsOnLayer(pn.B_Cu): continue
        outline = z.Outline().COutline(0)
        coords = [xy(outline.CPoint(i)) for i in range(outline.PointCount())]
        from PIL import Image, ImageDraw
        area = sum(coords[i][0] * coords[(i + 1) % len(coords)][1] - coords[(i + 1) % len(coords)][0] * coords[i][1] for i in range(len(coords)))
        normals = []
        for aa, cc in zip(coords, coords[1:] + coords[:1]):
            dx, dy = cc[0] - aa[0], cc[1] - aa[1]; length = math.hypot(dx, dy)
            normals.append((dy / length, -dx / length) if area > 0 else (-dy / length, dx / length))
        expanded = []; radius = width / 2 + 0.025
        for j, (xx, yy) in enumerate(coords):
            n1, n2 = normals[j - 1], normals[j]; den = 1 + n1[0] * n2[0] + n1[1] * n2[1]
            expanded.append((xx + radius * (n1[0] + n2[0]) / den, yy + radius * (n1[1] + n2[1]) / den))
        image = Image.new('L', (N, N)); ImageDraw.Draw(image).polygon([(idx(x), idx(y)) for x, y in expanded], fill=255)
        blocked |= np.asarray(image) > 0
        
    # Board edge margin (0.5 mm)
    edge = math.ceil((0.5 + width / 2) / STEP)
    blocked[:edge, :] = True; blocked[-edge:, :] = True
    blocked[:, :edge] = True; blocked[:, -edge:] = True
    
    return blocked

def route_bcu_astar(b, netname, start_xy, target_xy, width=0.20, blocked=None):
    if blocked is None:
        blocked = build_bcu_obstacle_grid(b, netname, width)
        
    sx, sy = idx(start_xy[0]), idx(start_xy[1])
    tx, ty = idx(target_xy[0]), idx(target_xy[1])
    
    # Ensure start and target are not blocked
    blocked[sy, sx] = False
    blocked[ty, tx] = False
    
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def h(y, x): return math.hypot(y - ty, x - tx)
    
    start_u = (sy, sx)
    heap = [(h(sy, sx), 0, start_u)]
    cost = {start_u: 0}
    parent = {}
    goal = None
    beg = time.monotonic()
    
    while heap:
        _, g, u = heapq.heappop(heap)
        if g != cost.get(u): continue
        if u == (ty, tx):
            goal = u
            break
        if time.monotonic() - beg > 30:
            break
            
        y, x = u
        for dy, dx in moves:
            yy, xx = y + dy, x + dx
            if yy < 0 or yy >= N or xx < 0 or xx >= N or blocked[yy, xx]: continue
            if dy and dx and (blocked[y, xx] or blocked[yy, x]): continue
            v = (yy, xx)
            ng = g + (math.sqrt(2) if dx and dy else 1)
            if ng < cost.get(v, 1e30):
                cost[v] = ng
                parent[v] = u
                heapq.heappush(heap, (ng + h(yy, xx), ng, v))
                
    if not goal:
        print(f"FAILED to find route for {netname} in {time.monotonic()-beg:.2f}s, explored {len(cost)} states")
        return False
        
    path = [goal]
    while path[-1] in parent:
        path.append(parent[path[-1]])
    path.reverse()
    
    # Simplify collinear segments
    points = [(path[0][1] * STEP + ORIGIN, path[0][0] * STEP + ORIGIN)]
    for i in range(1, len(path) - 1):
        dy1, dx1 = path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]
        dy2, dx2 = path[i+1][0] - path[i][0], path[i+1][1] - path[i][1]
        if (dy1, dx1) != (dy2, dx2):
            points.append((path[i][1] * STEP + ORIGIN, path[i][0] * STEP + ORIGIN))
    points.append((path[-1][1] * STEP + ORIGIN, path[-1][0] * STEP + ORIGIN))
    
    # Add segments to board
    for p1, p2 in zip(points, points[1:]):
        add_track(b, netname, p1[0], p1[1], p2[0], p2[1], layer=pn.B_Cu, width=width)
        
    print(f"SUCCESS: {netname} routed with {len(points)-1} segments, total length {round(cost[goal]*STEP, 2)} mm in {time.monotonic()-beg:.2f}s")
    return True
