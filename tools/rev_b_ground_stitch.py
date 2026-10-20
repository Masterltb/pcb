"""Bridge split ground pours using vias fully inside copper on both layers.

Keep a candidate only if native ERC/DRC passes and the ground open count falls.
"""
import math,json
import pcbnew as p
from rev_b_layout import FILE,ROOT,pt,xy,via
from rev_b_route_connections import check
from rev_b_ground_graph import graph

def opens(report):return sum('[GND]' in u['items'][0]['description'] for u in report['unconnected_items'])

def candidates(b):
 parent,names,root=graph(b)
 metal_roots={root(k) for k,v in names.items() if isinstance(k,str) and v.startswith(('PAD','PCB_TRACK','PCB_VIA'))}
 zones=[z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='GND']
 polys={z.GetLayer():z.GetFilledPolysList(z.GetLayer()) for z in zones}
 holes=[];pads=[]
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.GetAttribute()==p.PAD_ATTRIB_SMD:
    bb=a.GetBoundingBox();pads.append(tuple(p.ToMM(v) for v in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]))
   elif a.GetDrillSize().x:holes.append((*xy(a.GetPosition()),p.ToMM(max(a.GetDrillSize().x,a.GetDrillSize().y))/2))
 for t in b.GetTracks():
  if t.GetClass()=='PCB_VIA':holes.append((*xy(t.GetPosition()),p.ToMM(t.GetDrillValue())/2))
 circles=[(.18*math.cos(i*math.pi/4),.18*math.sin(i*math.pi/4)) for i in range(8)]+[(0,0)]
 choices=[]
 for layer,q in polys.items():
  for index in range(q.OutlineCount()):
   outline=q.COutline(index);area=abs(outline.Area()/1e12)
   if area>1000:continue
   if root((layer,index)) not in metal_roots:continue
   bb=outline.BBox();x0,y0=xy(bb.GetPosition());x1=x0+p.ToMM(bb.GetWidth());y1=y0+p.ToMM(bb.GetHeight())
   points={}
   for ix in range(math.ceil(x0*4),math.floor(x1*4)+1):
    for iy in range(math.ceil(y0*4),math.floor(y1*4)+1):
     x,y=ix/4,iy/4
     if not q.Contains(pt(x,y),index):continue
     if any(a-.25<x<c+.25 and d-.25<y<e+.25 for a,d,c,e in pads):continue
     if any(math.hypot(x-hx,y-hy)<r+.10+.27 for hx,hy,r in holes):continue
     if not all(all(poly.Contains(pt(x+dx,y+dy)) for dx,dy in circles) for poly in polys.values()):continue
     # Prefer a central point to improve the ground neck around the via.
     other=polys[p.B_Cu if layer==p.F_Cu else p.F_Cu]
     opposite=next(j for j in range(other.OutlineCount()) if other.Contains(pt(x,y),j))
     other_layer=p.B_Cu if layer==p.F_Cu else p.F_Cu
     if root((layer,index))==root((other_layer,opposite)) or root((other_layer,opposite)) not in metal_roots:continue
     points.setdefault(opposite,[]).append((math.hypot(x-(x0+x1)/2,y-(y0+y1)/2),x,y))
   if points:
    for group in points.values():
     _,x,y=min(group);choices.append((area,layer,index,x,y))
 return sorted(choices)

def main():
 (ROOT/'reports/revb/work/RevB-before-ground-stitches.kicad_pcb').write_bytes(FILE.read_bytes())
 baseline=check();assert not any(v['severity']=='error' for v in baseline['violations'])
 count=0
 for _,layer,index,x,y in candidates(p.LoadBoard(str(FILE))):
  if not opens(baseline):break
  before=FILE.read_bytes();b=p.LoadBoard(str(FILE));via(b,x,y,'GND',.4,.2)
  b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b)
  after=check()
  if any(v['severity']=='error' for v in after['violations']) or after['schematic_parity'] or opens(after)>=opens(baseline):
   print('Rejected stitch',x,y,'ground opens',opens(after),'errors',[v['type'] for v in after['violations'] if v['severity']=='error'],flush=True)
   FILE.write_bytes(before);check();continue
  baseline=after;count+=1;print('Ground stitch',x,y,'remaining ground opens',opens(after),flush=True)
 print('Accepted ground stitches',count,'remaining ground opens',opens(baseline))

if __name__=='__main__':main()
