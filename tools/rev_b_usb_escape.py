"""Reviewed local escape repair; intentionally removes provisional USB power paths.

Run only once on the pre-repair layout, then ERC/DRC before reconnecting nets.
"""
import re
import pcbnew as p
from rev_b_layout import FILE,ROOT,pt,xy,segment,via

def main():
 s=FILE.read_text();(ROOT/'reports/revb/work/RevB-before-USB-escape.kicad_pcb').write_text(s)
 cap2_keep=['43e267d2-e1e9-4f5a-8644-5fc12a89d0c9','771397d6-65fc-4e49-bdae-1daa5cb9a885','6e608c19-5160-4d24-b8ba-57d2f0132eeb']
 def keep(m):
  block=m[0]
  if '(net "CAP2")' in block and not any(u in block for u in cap2_keep):return ''
  if '(net "+3V3")' in block:
   coords=re.findall(r'\((?:start|end|at) ([\d.-]+) ([\d.-]+)',block)
   if any(138<float(x)<146 and 183<float(y)<190 for x,y in coords):return ''
  if '(net "GND")' in block:
   coords=re.findall(r'\((?:start|end|at) ([\d.-]+) ([\d.-]+)',block)
   if any(abs(float(x)-139.5)<.01 and any(abs(float(y)-yy)<.01 for yy in [183.15,183.82]) for x,y in coords):return ''
  return block
 FILE.write_text(re.sub(r'\n\t\((?:segment|via)\b[\s\S]*?\n\t\)',keep,s))
 b=p.LoadBoard(str(FILE));fs={f.GetReference():f for f in b.GetFootprints()}
 fs['C27'].SetPosition(pt(137,146));fs['C27'].SetOrientationDegrees(0)
 fs['C53'].SetPosition(pt(139.5,183.8));fs['C55'].SetPosition(pt(141.8,188.4))
 def pad(ref,num):return next(a for a in fs[ref].Pads() if a.GetNumber()==str(num))
 def fan(pin,coords):
  a=pad('U2',pin);net=a.GetNetname();points=[xy(a.GetPosition()),*coords]
  for aa,cc in zip(points,points[1:]):segment(b,aa,cc,net,.12)
  via(b,*coords[-1],net,.4,.2)
 fan(4,[(139.7,185.25)])
 fan(8,[(142.25,187.6)])
 fan(5,[(140.8,185.75),(140.8,186.75),(140.7,186.9)])
 a=pad('U2',6);segment(b,xy(a.GetPosition()),(140.8,186.25),'+3V3',.12)
 fan(7,[(141.75,187.2),(141.45,187.6)])
 segment(b,xy(pad('C55',1).GetPosition()),(141.45,187.6),'+3V3',.15)
 segment(b,xy(pad('C53',2).GetPosition()),(139.5,182.65),'GND',.2);via(b,139.5,182.65)
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b)
 print('USB signal escapes and local power stubs saved. Run ERC/DRC.')

if __name__=='__main__':main()
