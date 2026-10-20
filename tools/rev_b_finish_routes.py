"""Conservative grid routing of an explicitly requested RevB connection.

This is a geometry aid, not sign-off. Refill and run KiCad ERC/DRC after
every invocation. Never changes pinout, placement, or existing copper.
"""
from pathlib import Path
import sys,math,heapq,time
import numpy as np
import pcbnew as p
from rev_b_layout import FILE,pt,xy,segment,via

STEP=.05; ORIGIN=100.; N=2001
LAYERS=[p.F_Cu,p.B_Cu]

def route(net,start,end,width=.12):
 b=p.LoadBoard(str(FILE)); refs={f.GetReference():f for f in b.GetFootprints()}
 def endpoint(key):
  if key.startswith('='):
   x,y,layer=key[1:].split(',');return (float(x),float(y)),[int(layer)]
  if key.startswith('@'):
   item=next((t for t in b.GetTracks() if t.m_Uuid.AsString()==key[1:]),None)
   assert item and item.GetNetname()==net
   if item.GetClass()=='PCB_TRACK':return xy(item.GetStart()),[LAYERS.index(item.GetLayer())]
   return xy(item.GetPosition()),[i for i,l in enumerate(LAYERS) if item.IsOnLayer(l)]
  ref,pin=key.split(':'); a=next(a for a in refs[ref].Pads() if a.GetNumber()==pin)
  assert a.GetNetname()==net,(key,a.GetNetname(),net)
  return xy(a.GetPosition()),[i for i,l in enumerate(LAYERS) if a.IsOnLayer(l)]
 a,la=endpoint(start);c,lc=endpoint(end)
 blocked=np.zeros((2,N,N),dtype=bool); vb=np.zeros((N,N),dtype=bool)
 def idx(v):return round((v-ORIGIN)/STEP)
 existing_switch={}
 def limits(x1,y1,x2,y2):
  return max(0,math.ceil((x1-ORIGIN)/STEP)),max(0,math.ceil((y1-ORIGIN)/STEP)),min(N-1,math.floor((x2-ORIGIN)/STEP)),min(N-1,math.floor((y2-ORIGIN)/STEP))
 def rect(mask,bb,margin):
  x1,y1,x2,y2=limits(bb[0]-margin,bb[1]-margin,bb[2]+margin,bb[3]+margin)
  if x2>=x1 and y2>=y1:mask[y1:y2+1,x1:x2+1]=True
 def capsule(mask,a,c,r):
  x1,y1,x2,y2=limits(min(a[0],c[0])-r,min(a[1],c[1])-r,max(a[0],c[0])+r,max(a[1],c[1])+r)
  if x2<x1 or y2<y1:return
  ys,xs=np.mgrid[y1:y2+1,x1:x2+1];xs=xs*STEP+ORIGIN;ys=ys*STEP+ORIGIN
  dx,dy=c[0]-a[0],c[1]-a[1];den=dx*dx+dy*dy
  u=np.clip(((xs-a[0])*dx+(ys-a[1])*dy)/den,0,1) if den else 0
  mask[y1:y2+1,x1:x2+1]|=(xs-a[0]-u*dx)**2+(ys-a[1]-u*dy)**2<=r*r
 # 0.12mm design clearance plus a 5um raster guard. Native DRC still decides.
 margin=width/2+.125
 for f in b.GetFootprints():
  for pad in f.Pads():
   q=pad.GetBoundingBox();bb=tuple(p.ToMM(v) for v in [q.GetX(),q.GetY(),q.GetRight(),q.GetBottom()])
   own=pad.GetNetname()==net
   if own and pad.IsOnLayer(p.F_Cu) and pad.IsOnLayer(p.B_Cu):
    xx,yy=xy(pad.GetPosition());existing_switch[idx(yy),idx(xx)]=(xx,yy)
   if not own:
    for i,l in enumerate(LAYERS):
     if pad.IsOnLayer(l):rect(blocked[i],bb,margin)
    rect(vb,bb,.345)
   elif pad.GetAttribute()==p.PAD_ATTRIB_SMD:
    # No unqualified via-in-pad on a reflow pad.
    rect(vb,bb,.25)
   else:
    # An existing PTH already changes layers. Never drill another via in it.
    rect(vb,bb,.12)
 for t in b.GetTracks():
  if t.GetNetname()==net:
   if t.GetClass()=='PCB_VIA':
    center=xy(t.GetPosition());capsule(vb,center,center,p.ToMM(t.GetDrillValue())/2+.10+.265)
    existing_switch[idx(center[1]),idx(center[0])]=center
   continue
  if t.GetClass()=='PCB_VIA':
   center=xy(t.GetPosition());r=p.ToMM(t.GetWidth(p.F_Cu))/2
   clearance_radius=max(r+.125,p.ToMM(t.GetDrillValue())/2+.245)+width/2
   for i in range(2):capsule(blocked[i],center,center,clearance_radius)
   capsule(vb,center,center,r+.345)
  else:
   aa,cc=xy(t.GetStart()),xy(t.GetEnd());r=p.ToMM(t.GetWidth())/2
   for i,l in enumerate(LAYERS):
    if t.IsOnLayer(l):capsule(blocked[i],aa,cc,r+margin)
   capsule(vb,aa,cc,r+.345)
 # Reference-plane track keepouts remain authoritative on the bottom layer.
 for z in b.Zones():
  if not z.GetIsRuleArea() or not z.GetDoNotAllowTracks():continue
  outline=z.Outline().COutline(0);coords=[xy(outline.CPoint(i)) for i in range(outline.PointCount())]
  from PIL import Image,ImageDraw
  # Offset convex keepout edges in their normal direction. A square image
  # dilation over-blocks diagonal clock corridors by sqrt(2).
  area=sum(coords[i][0]*coords[(i+1)%len(coords)][1]-coords[(i+1)%len(coords)][0]*coords[i][1] for i in range(len(coords)))
  normals=[]
  for aa,cc in zip(coords,coords[1:]+coords[:1]):
   dx,dy=cc[0]-aa[0],cc[1]-aa[1];length=math.hypot(dx,dy)
   normals.append((dy/length,-dx/length) if area>0 else (-dy/length,dx/length))
  expanded=[];radius=width/2+.025
  for j,(xx,yy) in enumerate(coords):
   n1,n2=normals[j-1],normals[j];den=1+n1[0]*n2[0]+n1[1]*n2[1]
   expanded.append((xx+radius*(n1[0]+n2[0])/den,yy+radius*(n1[1]+n2[1])/den))
  image=Image.new('L',(N,N));ImageDraw.Draw(image).polygon([(idx(x),idx(y)) for x,y in expanded],fill=255)
  for i,l in enumerate(LAYERS):
   if z.IsOnLayer(l):blocked[i]|=np.asarray(image)>0
 edge=math.ceil((.5+width/2)/STEP)
 blocked[:,:edge,:]=True;blocked[:,-edge:,:]=True;blocked[:,:,:edge]=True;blocked[:,:,-edge:]=True
 def component_anchors(key,original,layers):
  if key.startswith('='):return [(original,layers)]
  if key.startswith('@'):seed=next(t for t in b.GetTracks() if t.m_Uuid.AsString()==key[1:])
  else:
   ref,pin=key.split(':');seed=next(q for q in refs[ref].Pads() if q.GetNumber()==pin)
  conn=b.GetConnectivity();queue=[seed];seen=set();result=[]
  while queue:
   item=queue.pop();uid=item.m_Uuid.AsString()
   if uid in seen:continue
   seen.add(uid)
   if item.GetNetname()!=net or item.GetClass() not in ['PCB_TRACK','PCB_VIA','PAD']:continue
   ls=[i for i,l in enumerate(LAYERS) if item.IsOnLayer(l)]
   if item.GetClass()=='PCB_TRACK':result.extend([(xy(item.GetStart()),ls),(xy(item.GetEnd()),ls)])
   else:result.append((xy(item.GetPosition()),ls))
   queue.extend(conn.GetConnectedItems(item))
  return result or [(original,layers)]
 anchors={}
 def cells(points):
  result=set()
  for (xx,yy),ls in points:
   for layer in ls:
    u=(layer,idx(yy),idx(xx))
    if not blocked[u]:result.add(u);anchors[u]=(xx,yy)
  return result
 sources=cells(component_anchors(start,a,la));targets=cells(component_anchors(end,c,lc))
 sources=[u for u in sources if not blocked[u]];targets={u for u in targets if not blocked[u]}
 if not sources or not targets:raise RuntimeError('Endpoint blocked '+str((sources,targets)))
 ty0=min(u[1] for u in targets);ty1=max(u[1] for u in targets);tx0=min(u[2] for u in targets);tx1=max(u[2] for u in targets)
 moves=[(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
 def h(u):return math.hypot(max(ty0-u[1],0,u[1]-ty1),max(tx0-u[2],0,u[2]-tx1))
 heap=[(h(u),0,u) for u in sources];heapq.heapify(heap);cost={u:0 for u in sources};parent={};goal=None;beg=time.monotonic()
 while heap:
  _,g,u=heapq.heappop(heap)
  if g!=cost.get(u):continue
  if u in targets:goal=u;break
  if time.monotonic()-beg>45:break
  l,y,x=u
  for dy,dx in moves:
   yy,xx=y+dy,x+dx
   if yy<0 or yy>=N or xx<0 or xx>=N or blocked[l,yy,xx]:continue
   if dy and dx and (blocked[l,y,xx] or blocked[l,yy,x]):continue
   v=(l,yy,xx);ng=g+(math.sqrt(2) if dx and dy else 1)
   if ng<cost.get(v,1e30):cost[v]=ng;parent[v]=u;heapq.heappush(heap,(ng+h(v),ng,v))
  if ((y,x) in existing_switch or not vb[y,x]) and not blocked[1-l,y,x]:
   v=(1-l,y,x);ng=g+(.1 if (y,x) in existing_switch else 24)
   if ng<cost.get(v,1e30):cost[v]=ng;parent[v]=u;heapq.heappush(heap,(ng+h(v),ng,v))
 if goal is None:
  from PIL import Image,ImageDraw
  for layer in range(2):
   im=Image.fromarray(np.where(blocked[layer],40,255).astype('uint8')).convert('RGB')
   dr=ImageDraw.Draw(im)
   for xx,yy,color in [(idx(a[0]),idx(a[1]),'red'),(idx(c[0]),idx(c[1]),'green')]:dr.ellipse((xx-3,yy-3,xx+3,yy+3),fill=color)
   for f in b.GetFootprints():
    xx,yy=xy(f.GetPosition());dr.text((idx(xx),idx(yy)),f.GetReference(),fill='blue')
   im.crop((idx(136),idx(147),idx(148),idx(158))).resize((1200,1100)).save(str(Path(__file__).resolve().parents[1]/f'reports/revb/work/RevB-grid-{layer}.png'))
  print('Search reached',len(cost),'states; debug grid saved')
  raise RuntimeError('No conservative route within 45s; placement/rip-up review needed')
 path=[goal]
 while path[-1] in parent:path.append(parent[path[-1]])
 path.reverse();short=[path[0]]
 for i in range(1,len(path)-1):
  before=tuple(path[i][j]-path[i-1][j] for j in range(3));after=tuple(path[i+1][j]-path[i][j] for j in range(3))
  if before!=after:short.append(path[i])
 short.append(path[-1])
 def pos(u):return anchors.get(u,existing_switch.get((u[1],u[2]),(u[2]*STEP+ORIGIN,u[1]*STEP+ORIGIN)))
 for u,v in zip(short,short[1:]):
  if u[0]!=v[0]:
   if (u[1],u[2]) not in existing_switch:via(b,*pos(u),net,diam=.4,drill=.2)
  else:segment(b,pos(u),pos(v),net,width,LAYERS[u[0]])
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b)
 print(net,start,end,'vertices',len(short),'length',round(cost[goal]*STEP,2),'mm incl via penalty; run ERC/DRC')

if __name__=='__main__':route(*sys.argv[1:4],float(sys.argv[4]) if len(sys.argv)>4 else .12)
