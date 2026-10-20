"""Ordered MCU escape routing, reviewed in RevB-QFN-prechange-review.md.

Destructive to provisional signal routes: run only when intentionally rebuilding
the MCU escape, then ERC/DRC before routing the remaining connections.
"""
import re,json,math
from pathlib import Path
import pcbnew as p
from rev_b_layout import ROOT,FILE,STD,pt,xy,segment,via

def blocks(text,token):return list(re.finditer(r'\n\t\('+token+r'\b[\s\S]*?\n\t\)',text))

def main():
 b=p.LoadBoard(str(FILE));fs={f.GetReference():f for f in b.GetFootprints()}
 moves={'R36':(142.2,148.5,90),'U5':(135,166,0),'C56':(138,164.5,0),
        'C13':(142,162.8,270),'C17':(142.6,159.75,270),'C18':(149,150.7,0),'C19':(145.5,148.2,0),'C40':(149,156.8,0),
        'C14':(135.7,154,180),'C15':(135.5,157,180),'C21':(133,157.5,90),'L2':(133.6,155,90),
        'R40':(150.5,154.5,0),'R41':(150.5,152.5,0),'R42':(152.5,151,0),'R43':(154.5,152.5,0),'R44':(152.5,156,0),'R45':(150.5,158,0)}
 grounds=[xy(a.GetPosition()) for r in [*moves,'C23'] for a in fs[r].Pads() if a.GetNetname()=='GND']
 old_c23=fs['C23'];old_uuid=old_c23.m_Uuid.AsString();old_path=old_c23.GetPath()
 # Serialize the replacement footprint independently, preserving schematic path
 # and footprint UUID. Avoid Remove(), which invalidates SWIG objects on Windows.
 tmp=p.BOARD();new=p.FootprintLoad(str(STD/'Capacitor_SMD.pretty'),'C_0201_0603Metric');tmp.Add(new)
 new.SetReference('C23');new.SetValue('100nF');new.SetFPIDAsString('Capacitor_SMD:C_0201_0603Metric');new.SetPath(old_path);new.SetPosition(pt(140.1,150.45));new.SetOrientationDegrees(180);new.Reference().SetVisible(False);new.Value().SetVisible(False)
 for number,name in [('1','+3V3'),('2','GND')]:
  net=p.NETINFO_ITEM(tmp,name);tmp.Add(net)
  for a in new.Pads():
   if a.GetNumber()==number:a.SetNet(net)
 new_uuid=new.m_Uuid.AsString();temp=ROOT/'reports/revb/work/RevB-C23-footprint.kicad_pcb';p.SaveBoard(str(temp),tmp)
 new_block=blocks(temp.read_text(),'footprint')[0].group(0).replace(new_uuid,old_uuid)
 s=FILE.read_text()
 def keep(m):
  block=m.group(0);match=re.search(r'\(net "([^"]+)"\)',block);net=match[1] if match else ''
  if not(net.startswith(('+12V','+6V','RF_','XTAL_')) or net in ['GND','+5V','+3V3','VDD_SDIO']):return ''
  if net=='GND':
   coords=re.findall(r'\((?:start|end|at) (-?[\d.]+) (-?[\d.]+)',block)
   if any(math.hypot(float(x)-a,float(y)-c)<1.0 for x,y in coords for a,c in grounds):return ''
  if net in ['XTAL_P','XTAL_P_X']:return ''
  if net in ['+3V3','VDD_SDIO']:
   coords=re.findall(r'\((?:start|end|at) (-?[\d.]+) (-?[\d.]+)',block)
   if any(139<float(x)<(156 if net=='+3V3' else 150) and 147.5<float(y)<164.5 for x,y in coords):return ''
   if net=='+3V3' and any((137.2<float(x)<138.8 and 156.8<float(y)<158.2) or (132<float(x)<134 and 155.5<float(y)<157.0) for x,y in coords):return ''
  return block
 s=re.sub(r'\n\t\((?:segment|via)\b[\s\S]*?\n\t\)',keep,s)
 s=re.sub(r'\n\t\(footprint\b[\s\S]*?\n\t\)',lambda m:new_block if '(property "Reference" "C23"' in m.group(0) else m.group(0),s)
 FILE.write_text(s);b=p.LoadBoard(str(FILE));fs={f.GetReference():f for f in b.GetFootprints()}
 for ref,(x,y,a) in moves.items():fs[ref].SetPosition(pt(x,y));fs[ref].SetOrientationDegrees(a)
 def pad(ref,num):return next(a for a in fs[ref].Pads() if a.GetNumber()==str(num))
 def link(coords,net,w=.12):
  for a,c in zip(coords,coords[1:]):segment(b,a,c,net,w)
 def fan(pin,points,width=.12):
  a=pad('U1',pin);net=a.GetNetname();link([xy(a.GetPosition()),*points],net,width);via(b,*points[-1],net,.4,.2)
 # Bottom row: first leave the complete pad toe, then spread to a single row.
 for pin,x in [(15,140.5),(16,141.2),(18,141.9),(19,142.6),(21,143.3),(22,144.0),(23,144.7)]:
  x0,y0=xy(pad('U1',pin).GetPosition());fan(pin,[(x0,157.05),(x,158.2)])
 # Right row, top to bottom. 0.6mm via pitch with 0.4/0.2mm vias.
 for i,pin in enumerate(range(38,24,-1)):
  x0,y0=xy(pad('U1',pin).GetPosition());fan(pin,[(146.05,y0),(147.8,150.1+i*.6)])
 # Left digital pins; the RF and supply pins retain their own short paths.
 for i,pin in enumerate(range(9,15)):
  x0,y0=xy(pad('U1',pin).GetPosition());fan(pin,[(139.95,y0),(138,154+i*.7)])
 # Top digital escape keeps clear of the oscillator and the VDDA via.
 fan(42,[(143.525,151.15),(143.62,150.9),(143.8,149.8)],.10)
 fan(41,[(143.875,150.95),(144.4,149.8)])
 fan(40,[(144.225,150.95),(145,149.8)])
 fan(39,[(144.575,150.95),(145.6,149.8)])
 fan(43,[(143.175,150.95),(143.23,150.8)])
 fan(46,[(142.125,150.9),(142,150.775),(142,150)])
 fan(47,[(141.775,150.975),(141.6,150.7)])
 fan(48,[(141.425,151.125),(141,150.7)])
 link([xy(pad('U1',1).GetPosition()),xy(pad('C23',1).GetPosition())],'+3V3')
 link([xy(pad('U1',3).GetPosition()),xy(pad('U1',4).GetPosition()),(140,152.775),xy(pad('C22',1).GetPosition())],'+3V3_RF')
 link([xy(pad('U1',45).GetPosition()),(142.475,149.4),xy(pad('R36',1).GetPosition())],'XTAL_P')
 link([xy(pad('R36',2).GetPosition()),(142.2,147.8),xy(pad('Y1',1).GetPosition()),xy(pad('C24',1).GetPosition())],'XTAL_P_X',.15)
 # Reestablish short ground stitches for moved decouplers; candidate locations
 # are checked by native DRC, not assumed valid from this helper.
 gnd={'C23':(139.78,149.9),'C13':(142,164.2),'C17':(142.6,160.85),'C18':(150.1,150.7),'C19':(146.6,148.2),'C40':(150.1,156.8),
      'C14':(134.1,154),'C15':(134.1,157),'C21':(132.4,157.02),'C56':(139,164.2),'U5':(133.5,165.05)}
 for ref,pos in gnd.items():
  a=next(a for a in fs[ref].Pads() if a.GetNetname()=='GND');link([xy(a.GetPosition()),pos],'GND',.2);via(b,*pos)
 for f in fs.values():
  for a in f.Pads():
   if a.GetNetname()=='GND' and f.GetAttributes()&p.FP_SMD:a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b)
 project=FILE.with_suffix('.kicad_pro');data=json.loads(project.read_text());data['board']['design_settings']['rules']['min_via_diameter']=.4;project.write_text(json.dumps(data,indent=2))
 print('Ordered MCU escape saved; run ERC/DRC before any further routing.')

if __name__=='__main__':main()
