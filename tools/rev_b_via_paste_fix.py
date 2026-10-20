"""Apply reviewed drill/paste separation fixes; run ERC/DRC afterwards."""
import pcbnew as p
from rev_b_layout import FILE,pt

b=p.LoadBoard(str(FILE))
moves={'fad98528-e6cb-48fd-97ca-d9befcc89520':(134,164.3),'a25e91c0-467b-4851-bbac-3b5eac361d1b':(145,195.838)}
for v in b.GetTracks():
 if v.GetClass()!='PCB_VIA':continue
 x,y=p.ToMM(v.GetPosition().x),p.ToMM(v.GetPosition().y)
 if v.GetNetname()=='GND' and abs(y-198.538)<.001 and (abs(x-142)<.001 or abs(x-144)<.001):moves[v.m_Uuid.AsString()]=(x,199.2)
 if v.m_Uuid.AsString() in moves:
  old=v.GetPosition();dest=pt(*moves[v.m_Uuid.AsString()])
  for t in b.GetTracks():
   if t.GetClass()=='PCB_TRACK' and t.GetNetname()==v.GetNetname():
    if t.GetStart()==old:t.SetStart(dest)
    if t.GetEnd()==old:t.SetEnd(dest)
  v.SetPosition(dest)
 if v.m_Uuid.AsString() in ['48b73304-ae0b-4db8-93c0-857d7a69d429','7f0f7da2-1513-4324-9af0-f4473c640e33']:
  v.SetWidth(p.FromMM(.4));v.SetDrill(p.FromMM(.2))
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b)
