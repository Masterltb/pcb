"""Place readable service labels; keep front labels outside component bodies."""
import pcbnew as p
from rev_b_layout import FILE,pt,xy,box as footprint_box,hits

def bbox(item):
 q=item.GetBoundingBox();return tuple(p.ToMM(v) for v in [q.GetX(),q.GetY(),q.GetRight(),q.GetBottom()])

def main():
 b=p.LoadBoard(str(FILE));fs={f.GetReference():f for f in b.GetFootprints()}
 for t in b.GetDrawings():
  if t.GetClass()=='PCB_TEXT' and t.GetLayer() in [p.F_SilkS,p.B_SilkS]:t.SetLayer(p.Dwgs_User)
 occupied={p.F_SilkS:[],p.B_SilkS:[]};pads={p.F_SilkS:[],p.B_SilkS:[]}
 bodies=[footprint_box(f) for f in fs.values()]
 for f in fs.values():
  f.Reference().SetVisible(False)
  for pad in f.Pads():
   for silk,cu in [(p.F_SilkS,p.F_Cu),(p.B_SilkS,p.B_Cu)]:
    if pad.IsOnLayer(cu):pads[silk].append(bbox(pad))
  for g in f.GraphicalItems():
   if g.GetLayer() in occupied:
    if g.GetClass()=='PCB_SHAPE' and g.GetWidth()<p.FromMM(.15):g.SetWidth(p.FromMM(.15))
    if g.GetClass()!='PCB_TEXT' or g.IsVisible():occupied[g.GetLayer()].append(bbox(g))
 # Avoid printing fine reference text over via holes even when tented.
 for t in b.GetTracks():
  if t.GetClass()=='PCB_VIA':
   x,y=xy(t.GetPosition());r=p.ToMM(t.GetWidth(p.F_Cu))/2
   for layer in pads:pads[layer].append((x-r,y-r,x+r,y+r))
 fallback=[]
 def place(t,pref,layers,dist,body_avoid=True):
  t.SetTextSize(pt(1,1));t.SetTextThickness(p.FromMM(.15));t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));t.SetKeepUpright(True)
  offsets=sorted((dx*dx+dy*dy,dx*.25,dy*.25) for dx in range(-int(dist*4),int(dist*4)+1) for dy in range(-int(dist*4),int(dist*4)+1))
  for layer in layers:
   t.SetLayer(layer);t.SetMirrored(layer==p.B_SilkS)
   obstacles=occupied[layer]+pads[layer]+(bodies if layer==p.F_SilkS and body_avoid else [])
   for _,dx,dy in offsets:
    t.SetPosition(pt(pref[0]+dx,pref[1]+dy));bb=bbox(t)
    if bb[0]<100.5 or bb[1]<100.5 or bb[2]>199.5 or bb[3]>199.5:continue
    if any(hits(bb,o,.22) for o in obstacles):continue
    occupied[layer].append(bb);return layer
  raise RuntimeError('No readable label position: '+t.GetText())
 annotations=[('FV-CTRL RevB',154,139.5),('2026-10-20',154,141.5),('USB DATA',143,192.5),('USB: 12V ON',154,143.5),('RESET',132,196.7),('BOOT',154,196.7),('ANT SMA',129,146.2)]
 for ref,label in [('J1','12V IN'),('J2','BUCK A'),('J3','BUCK B')]:
  f=fs[ref];bb=footprint_box(f);annotations.append((label,(bb[0]+bb[2])/2,118))
  for pad in f.Pads():
   net=pad.GetNetname();label='G' if net=='GND' else '12' if net.startswith('+12V') else '6A' if '_A' in net else '6B'
   x,y=xy(pad.GetPosition());annotations.append((label,x,115.8))
 for ref,name in [('J5','S1 TOP'),('J6','S1 BOT'),('J7','S2 TOP'),('J8','S2 BOT')]:
  x,y=xy(fs[ref].GetPosition());annotations.append((name,188,y+2.5))
  for pad in fs[ref].Pads():
   name={'1':'G','2':'6A' if ref in ['J5','J6'] else '6B','3':'S'}[pad.GetNumber()]
   annotations.append((name,198,xy(pad.GetPosition())[1]))
 for ref,name in [('J9','RX1'),('J10','RX2'),('J11','TX1'),('J12','TX2')]:
  x,y=xy(fs[ref].GetPosition());annotations.append((ref+' '+name,113,y-2))
  for pad in fs[ref].Pads():
   net=pad.GetNetname();label='G' if net=='GND' else '3V' if net=='+3V3' else 'O' if '_CABLE' in net else 'K' if net=='IR_TX_RET' else 'A'
   xx,yy=xy(pad.GetPosition());annotations.append((label,xx if ref=='J12' else 111,143.5 if ref=='J12' else yy))
 for ref in ['J13','J14','J15','J16']:
  x,y=xy(fs[ref].GetPosition());annotations.append(('LS'+str(int(ref[1:])-12)+' DNP',x,y+5))
 for pad in fs['J17'].Pads():
  x,y=xy(pad.GetPosition());annotations.append(({'1':'3V','2':'SDA','3':'SCL','4':'G'}[pad.GetNumber()],121,y))
 annotations.append(('5V LOGIC',125,142))
 for ref,f in fs.items():
  if ref.startswith('TP'):
   x,y=xy(f.GetPosition());label={'TP8':'IO33','TP9':'EN','TP10':'BOOT','TP11':'TX','TP12':'RX'}.get(ref,f.GetValue().replace('+',''));annotations.append((label,x,y+2.7))
 for value,x,y in annotations:
  t=p.PCB_TEXT(b);t.SetText(value);b.Add(t)
  layer=place(t,(x,y),[p.F_SilkS,p.B_SilkS],5)
  if layer==p.B_SilkS:fallback.append(value)
 for ref,f in sorted(fs.items()):
  if ref.startswith('FID'):continue
  t=f.Reference();t.SetVisible(True);bb=footprint_box(f);smd=f.GetAttributes()&p.FP_SMD
  place(t,xy(f.GetPosition()) if smd else ((bb[0]+bb[2])/2,bb[1]-1),[p.B_SilkS] if smd else [p.F_SilkS,p.B_SilkS],7)
 p.SaveBoard(str(FILE),b)
 print('Service labels and references >=1mm / 0.15mm. Back-side functional labels:',fallback)

if __name__=='__main__':main()
