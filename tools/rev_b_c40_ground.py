"""One-time C40 repair on the pre-repair layout; not an idempotent generator."""
import math,re
import pcbnew as p
from rev_b_layout import FILE,ROOT,pt,xy,box,hits,segment,via
from rev_b_ground_graph import graph
from rev_b_route_connections import check

def main():
 original=FILE.read_bytes();b=p.LoadBoard(str(FILE));parent,names,root=graph(b)
 main=root(next(k for k,v in names.items() if v=='PAD J1'))
 qs={z.GetLayer():z.GetFilledPolysList(z.GetLayer()) for z in b.Zones() if not z.GetIsRuleArea()}
 obstacles=[box(f) for f in b.GetFootprints() if f.GetReference()!='C40']
 def inside(l,x,y):return any(root((l,i))==main and qs[l].Contains(pt(x,y),i) for i in range(qs[l].OutlineCount()))
 choices=[]
 for angle in [0,90,180,270]:
  ux,uy=math.cos(math.radians(angle)),-math.sin(math.radians(angle))
  hx,hy=(.95,.5) if angle%180==0 else (.5,.95)
  for ix in range(568,622):
   for iy in range(604,664):
    x,y=ix/4,iy/4
    if math.hypot(x-147.8,y-157.3)>6:continue
    if any(hits((x-hx,y-hy,x+hx,y+hy),o,.05) for o in obstacles):continue
    gx,gy=x+.48*ux,y+.48*uy
    if not inside(p.F_Cu,gx,gy):continue
    for vx,vy in [(gx+ux*1.05,gy+uy*1.05),(gx-uy*1.05,gy+ux*1.05),(gx+uy*1.05,gy-ux*1.05)]:
     if not all(inside(l,vx,vy) for l in qs):continue
     choices.append((math.hypot(x-147.8,y-157.3),x,y,angle,vx,vy))
 # Reviewed position used by the final native PCB; test this before a search.
 choices.append((-1,145,159,180,143.47,159))
 print('C40 candidates',len(choices),flush=True)
 def keep(m):
  text=m[0];coords=re.findall(r'\((?:start|end|at) ([\d.-]+) ([\d.-]+)',text)
  if '(net "GND")' in text and any(abs(float(x)-150.1)<.01 and abs(float(y)-156.8)<.01 for x,y in coords):return ''
  if '(net "VDD_SDIO")' in text and any(abs(float(x)-148.52)<.35 and abs(float(y)-156.8)<.35 for x,y in coords):return ''
  return text
 stripped=re.sub(r'\n\t\((?:segment|via)\b[\s\S]*?\n\t\)',keep,original.decode('utf-8'))
 for _,x,y,angle,vx,vy in sorted(choices):
  print('Try C40',x,y,angle,vx,vy,flush=True)
  FILE.write_text(stripped,encoding='utf-8');b=p.LoadBoard(str(FILE));f=next(f for f in b.GetFootprints() if f.GetReference()=='C40');f.SetPosition(pt(x,y));f.SetOrientationDegrees(angle)
  pad=next(a for a in f.Pads() if a.GetNetname()=='GND');segment(b,xy(pad.GetPosition()),(vx,vy),'GND',.2);via(b,vx,vy,'GND',.4,.2)
  b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b);report=check()
  if not any(v['severity']=='error' for v in report['violations']) and not any('[GND]' in u['items'][0]['description'] for u in report['unconnected_items']):
   print('C40 accepted',x,y,angle,'ground via',vx,vy,flush=True);return
  print('Rejected',[(v['description'],v['items']) for v in report['violations'] if v['severity']=='error'],flush=True)
  FILE.write_bytes(original);check()
 FILE.write_bytes(original);check();raise RuntimeError('No C40 candidate passed native DRC')

if __name__=='__main__':main()
