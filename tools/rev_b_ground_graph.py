"""Diagnostic graph of filled ground polygons and native connected copper."""
import math,collections
import pcbnew as p
from rev_b_layout import FILE,pt,xy

def graph(b):
 qs={z.GetLayer():z.GetFilledPolysList(z.GetLayer()) for z in b.Zones() if not z.GetIsRuleArea()}
 parent={};names={}
 def root(k):
  parent.setdefault(k,k)
  if parent[k]!=k:parent[k]=root(parent[k])
  return parent[k]
 def union(a,c):parent[root(a)]=root(c)
 def touch(x,y,l,key):
  for i in range(qs[l].OutlineCount()):
   if qs[l].Contains(pt(x,y),i):union(key,(l,i))
 items=[t for t in b.GetTracks() if t.GetNetname()=='GND']+[a for f in b.GetFootprints() for a in f.Pads() if a.GetNetname()=='GND']
 for a in items:
  k=a.m_Uuid.AsString();root(k);names[k]=a.GetClass()+(' '+a.GetParentFootprint().GetReference() if a.GetClass()=='PAD' else '')
  for n in b.GetConnectivity().GetConnectedItems(a):
   if n.GetClass() in ['PCB_TRACK','PCB_VIA','PAD']:union(k,n.m_Uuid.AsString())
  x,y=xy(a.GetPosition())
  if a.GetClass()=='PCB_TRACK':
   xx,yy=xy(a.GetEnd());dx,dy=xx-x,yy-y;count=max(1,math.ceil(math.hypot(dx,dy)/.1));coords=[(x+dx*i/count,y+dy*i/count) for i in range(count+1)]
  else:coords=[(x,y)]+[(x+.25*math.cos(i*math.pi/4),y+.25*math.sin(i*math.pi/4)) for i in range(8)]
  for l in qs:
   if a.IsOnLayer(l):
    for xx,yy in coords:touch(xx,yy,l,k)
 for l,q in qs.items():
  for i in range(q.OutlineCount()):
   k=(l,i);root(k);bb=q.COutline(i).BBox();names[k]=f'layer{l}poly{i} '+str([round(p.ToMM(v),2) for v in [bb.GetX(),bb.GetY(),bb.GetWidth(),bb.GetHeight()]])
 return parent,names,root

if __name__=='__main__':
 b=p.LoadBoard(str(FILE));parent,names,root=graph(b);groups=collections.defaultdict(list)
 for k in list(parent):groups[root(k)].append(names.get(k,str(k)))
 for vals in sorted(groups.values(),key=len):print('COMPONENT',len(vals),*vals[:20],sep='\n')
