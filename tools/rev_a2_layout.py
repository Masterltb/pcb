"""RevA2 placement and routing exchange. Input nets come from KiCad XML."""
from pathlib import Path
import json,sys,re,xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]; NAME='FV-CTRL_RevA2'
(ROOT/'reports/reva2/work').mkdir(parents=True,exist_ok=True)
spec=json.loads((ROOT/'hardware/reva2'/f'{NAME}.design.json').read_text())
STD=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def rect(board,x1,y1,x2,y2,layer,width=.12):
    for a,b in [((x1,y1),(x2,y1)),((x2,y1),(x2,y2)),((x2,y2),(x1,y2)),((x1,y2),(x1,y1))]:
        s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(pt(*a));s.SetEnd(pt(*b));s.SetLayer(layer);s.SetWidth(p.FromMM(width));board.Add(s)
def text(board,value,x,y,size=1,layer=p.F_SilkS,angle=0):
    t=p.PCB_TEXT(board);t.SetText(value);t.SetPosition(pt(x,y));t.SetTextSize(pt(size,size));t.SetTextThickness(p.FromMM(.13));t.SetLayer(layer);t.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));t.SetMirrored(layer==p.B_SilkS);board.Add(t);return t

# Placement overrides are reviewed without regenerating schematic UUIDs.
POS={
 'J1':(119,112,180),'J2':(151,112,180),'J3':(183,112,180),
 'J5':(194,153,0),'J6':(194,163,0),'J7':(194,173,0),'J8':(194,183,0),
 'R16':(110,145,0),'C7':(110,149,0),
 'R17':(110,158,0),'C8':(119,158,0),
 'R18':(110,165,0),'C9':(119,166,0),
 'R19':(110,186,0),'C10':(119,187,0),
 'D5':(116,154,0),'R23':(110,151,90),
 'C6':(120,151,0),'D6':(120,162,0),'R24':(124,158,90),
}
def pack(b):
    fixed={'J1','J2','J3','J5','J6','J7','J8','J9','J10','J11','J18','J19'}
    fps={f.GetReference():f for f in b.GetFootprints()}
    def bbox(f):
        f.BuildCourtyardCaches(); bb=f.GetCourtyard(p.F_CrtYd).BBox()
        return tuple(p.ToMM(v) for v in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()])
    def intersect(a,b,gap=.35):return a[0]<b[2]+gap and a[2]>b[0]-gap and a[1]<b[3]+gap and a[3]>b[1]-gap
    occupied=[]
    for f in fps.values():
        if f.GetReference() in fixed or f.GetReference().startswith('H'): occupied.append(bbox(f))
    occupied.append((128,136.5,158,199.5)) # complete removable module envelope
    mobile=[f for f in fps.values() if f.GetReference() not in fixed and not f.GetReference().startswith('H')]
    mobile.sort(key=lambda f:-(bbox(f)[2]-bbox(f)[0])*(bbox(f)[3]-bbox(f)[1]))
    for f in mobile:
        pref=(p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)); ref=f.GetReference()
        candidates=[]
        for angle in [0,90,180,270]:
            f.SetPosition(pt(0,0));f.SetOrientationDegrees(angle);r=bbox(f)
            for x in range(102,198):
                for y in range(103,198):
                    if ref in ['J12'] and x>110:continue
                    if ref in ['J13','J14','J15','J16'] and (x<160 or y<180):continue
                    box=(r[0]+x,r[1]+y,r[2]+x,r[3]+y)
                    if box[0]<100.5 or box[1]<100.5 or box[2]>199.5 or box[3]>199.5:continue
                    score=(x-pref[0])**2+(y-pref[1])**2 + (0 if angle in [0,180] else 2)
                    candidates.append((score,x,y,angle,box))
        candidates.sort(key=lambda t:t[0])
        for _,x,y,angle,box in candidates:
            if not any(intersect(box,o) for o in occupied):
                f.SetOrientationDegrees(angle);f.SetPosition(pt(x,y));occupied.append(box);break
        else:raise RuntimeError('No courtyard space for '+ref)
    placement={f.GetReference():[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()] for f in fps.values()}
    (ROOT/'reports/reva2/verified/RevA2-placement.json').write_text(json.dumps(placement,indent=2))
def place():
    b=p.BOARD();b.SetCopperLayerCount(2);b.SetFileName(str(ROOT/'hardware/reva2'/f'{NAME}.kicad_pcb'))
    ds=b.GetDesignSettings();ds.m_MinClearance=p.FromMM(.25);ds.m_TrackMinWidth=p.FromMM(.25);ds.m_MinThroughDrill=p.FromMM(.4);ds.m_HoleToHoleMin=p.FromMM(.25);ds.m_CopperEdgeClearance=p.FromMM(.5)
    xml=ET.parse(ROOT/'reports/reva2/verified/RevA2.net.xml').getroot();netmap={};nodemap={}
    for net in xml.findall('nets/net'):
        name=net.attrib['name'];n=p.NETINFO_ITEM(b,name);b.Add(n);netmap[name]=n
        for node in net.findall('node'):nodemap[(node.attrib['ref'],node.attrib['pin'])]=n
    comp={c.attrib['ref']:c for c in xml.findall('components/comp')}
    for part in spec['parts']:
        lib,name=part['footprint'].split(':');libpath=ROOT/'libs/fv_reva2.pretty' if lib=='fv_reva2' else STD/(lib+'.pretty')
        fp=p.FootprintLoad(str(libpath),name)
        if not fp:raise RuntimeError(part['footprint'])
        b.Add(fp);fp.SetReference(part['ref']);fp.SetValue(part['value']);fp.SetFPIDAsString(part['footprint'])
        x,y,angle=POS.get(part['ref'],part['pos']);fp.SetPosition(pt(x,y));fp.SetOrientationDegrees(angle)
        try:fp.SetPath(p.KIID_PATH('/'+comp[part['ref']].findtext('tstamps')))
        except TypeError:pass
        fp.Value().SetVisible(False)
        fp.SetAttributes(fp.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM)
        fp.Reference().SetTextSize(pt(.9,.9));fp.Reference().SetTextThickness(p.FromMM(.13))
        fp.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));fp.Reference().SetKeepUpright(True)
        if part['dnp']:fp.SetAttributes(fp.GetAttributes()|p.FP_DNP)
        for pad in fp.Pads():
            if (part['ref'],pad.GetNumber()) in nodemap:pad.SetNet(nodemap[(part['ref'],pad.GetNumber())])
    rect(b,100,100,200,200,p.Edge_Cuts,.05)
    pack(b)
    # Document module envelope, USB cable access, and antenna copper keepout.
    rect(b,128.7,142.66,156.7,197.01,p.Dwgs_User,.12)
    text(b,'DEVKITC-32E V4 / SOCKET 25.40mm',143,140,.8,p.Dwgs_User)
    text(b,'USB - KEEP ACCESS',143,199,.8,p.Dwgs_User)
    zone=p.ZONE(b);zone.SetIsRuleArea(True);zone.SetLayerSet(p.LSET.AllCuMask());zone.SetDoNotAllowTracks(True);zone.SetDoNotAllowVias(True);zone.SetDoNotAllowZoneFills(True)
    outline=zone.Outline();outline.NewOutline()
    for x,y in [(132.7,137),(152.7,137),(152.7,151),(132.7,151)]:outline.Append(int(p.FromMM(x)),int(p.FromMM(y)))
    b.Add(zone)
    text(b,'FV-CTRL RevA2 2026-10-20',147,102,1)
    text(b,'ENGINEERING REVIEW - NOT RELEASED',147,105,.8,p.B_SilkS)
    text(b,'REMOVE JP1 BEFORE USB',143,192,.8,p.B_SilkS)
    b.BuildConnectivity();p.SaveBoard(str(ROOT/'hardware/reva2'/f'{NAME}.kicad_pcb'),b)
    print('Saved placement. Run DRC before routing.')

def exchange(power_only=False):
    b=p.LoadBoard(str(ROOT/'hardware/reva2'/f'{NAME}.kicad_pcb'))
    path=ROOT/'reports/reva2/work/RevA2.dsn';assert p.ExportSpecctraDSN(b,str(path))
    s=path.read_text()
    # Explicit classes for autorouter, preserving the hand-reviewed power widths.
    # Default KiCad DSN uses um resolution.
    start=s.index('  (network');end=s.index('  (wiring',start)
    segment=s[start:end]
    # Replace default class; assigning a net twice would make its width ambiguous.
    ci=segment.find('    (class ')
    if ci>=0:segment=segment[:ci]+')\n'
    nets=[n.GetNetname() for n in b.GetNetsByNetcode().values() if n.GetNetCode()>0]
    groups={2000:[n for n in nets if n.removeprefix('/').startswith(('+12V','+6V'))],800:[n for n in nets if n.removeprefix('/') in ['+5V','+5V_DEVKIT']],500:[n for n in nets if n.removeprefix('/') in ['GND','+3V3']]}
    used={n for ns in groups.values() for n in ns};groups[300]=[n for n in nets if n not in used]
    classes=''
    for width,ns in groups.items():
        if ns:classes+=f'    (class "W{width}" '+ ' '.join('"'+n+'"' for n in ns)+f' (circuit (use_via "Via[0-1]_800:400_um")) (rule (width {width}) (clearance 250)))\n'
    # Preserve the original via's name as exported by KiCad.
    via=re.search(r'\(via\s+"?([^\s\)"]+)',s)
    if via:classes=re.sub(r'Via\[0-1\]_800:400_um',via.group(1),classes)
    segment=segment.rstrip();segment=segment[:-1]+classes+'  )\n'
    s=s[:start]+segment+s[end:]
    s=s.replace('Via[0-1]_600:300_um','Via[0-1]_800:400_um')
    s=s.replace('(padstack "Via[0-1]_800:400_um"\n      (shape (circle F.Cu 600))\n      (shape (circle B.Cu 600))','(padstack "Via[0-1]_800:400_um"\n      (shape (circle F.Cu 800))\n      (shape (circle B.Cu 800))')
    if power_only:
        def selected(m):
            return m.group(0) if re.match(r'    \(net /\+(12V|6V)',m.group(0)) else ''
        start=s.index('  (network');end=s.index('  (wiring',start)
        ns=s[start:end];ns=re.sub(r'    \(net [\s\S]*?\n    \)',selected,ns)
        ns=re.sub(r'    \(class "W(?:800|500|300)"[^\n]*\n','',ns)
        s=s[:start]+ns+s[end:];path=ROOT/'reports/reva2/work/RevA2-power.dsn'
    path.write_text(s)
    print('DSN saved with explicit power/signal classes:',path)

def session(power_only=False):
    b=p.LoadBoard(str(ROOT/'hardware/reva2'/f'{NAME}.kicad_pcb'))
    assert p.ImportSpecctraSES(b,str(ROOT/'reports/reva2/work'/('RevA2-power.ses' if power_only else 'RevA2.ses')))
    b.BuildConnectivity();p.SaveBoard(str(ROOT/'hardware/reva2'/f'{NAME}.kicad_pcb'),b)
    print('Imported routing. Run DRC and inspect power paths before proceeding.')

def finish():
    b=p.LoadBoard(str(ROOT/'hardware/reva2'/f'{NAME}.kicad_pcb'))
    # Router neck-downs must still satisfy this project's manufacturing minimum.
    for t in b.GetTracks():
        if t.GetClass()=='PCB_TRACK':
            if t.GetWidth()<p.FromMM(.25):t.SetWidth(p.FromMM(.25))
            for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
                v=getter()
                if v.y>p.FromMM(199.2):setter(p.VECTOR2I(v.x,p.FromMM(199.2)))
    # Continuous shared ground on both layers; keepout excludes antenna region.
    gnd=b.FindNet('/GND')
    for layer in [p.F_Cu,p.B_Cu]:
        zone=p.ZONE(b);zone.SetLayer(layer);zone.SetNet(gnd);zone.SetLocalClearance(p.FromMM(.3));zone.SetMinThickness(p.FromMM(.25));zone.SetThermalReliefGap(p.FromMM(.3));zone.SetThermalReliefSpokeWidth(p.FromMM(.6))
        zone.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
        outline=zone.Outline();outline.NewOutline()
        for x,y in [(100.6,100.6),(199.4,100.6),(199.4,199.4),(100.6,199.4)]:outline.Append(int(p.FromMM(x)),int(p.FromMM(y)))
        b.Add(zone)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(ROOT/'hardware/reva2'/f'{NAME}.kicad_pcb'),b)
    print('Applied min widths, edge correction, and GND pours. Run ERC/DRC.')

def silk():
    b=p.LoadBoard(str(ROOT/'hardware/reva2'/f'{NAME}.kicad_pcb'))
    for item in list(b.GetDrawings()):
        if item.GetClass()=='PCB_TEXT' and item.GetLayer() in [p.F_SilkS,p.B_SilkS]:item.SetLayer(p.Dwgs_User)
    def box(item):
        v=item.GetBoundingBox();return tuple(p.ToMM(q) for q in [v.GetX(),v.GetY(),v.GetRight(),v.GetBottom()])
    def hits(a,c,g=.16):return a[0]<c[2]+g and a[2]>c[0]-g and a[1]<c[3]+g and a[3]>c[1]-g
    pads=[box(pad) for fp in b.GetFootprints() for pad in fp.Pads()]
    fixed={layer:[] for layer in [p.F_SilkS,p.B_SilkS]}
    for fp in b.GetFootprints():
        fp.Reference().SetVisible(False)
        for item in fp.GraphicalItems():
            if item.GetLayer() in fixed and (item.GetClass()!='PCB_TEXT' or item.IsVisible()):fixed[item.GetLayer()].append(box(item))
    def settle(t,pref,maxdist=9):
        x0,y0=pref
        options=sorted([(dx*dx+dy*dy,dx/2,dy/2) for dx in range(-maxdist*2,maxdist*2+1) for dy in range(-maxdist*2,maxdist*2+1)])
        for layer in [p.F_SilkS,p.B_SilkS]:
            t.SetLayer(layer);t.SetMirrored(layer==p.B_SilkS)
            for _,dx,dy in options:
                t.SetPosition(pt(x0+dx,y0+dy));r=box(t)
                if min(r[0],r[1])<100.3 or max(r[2],r[3])>199.7:continue
                if not any(hits(r,o) for o in pads+fixed[layer]):fixed[layer].append(r);return
        raise RuntimeError('Cannot place silkscreen '+t.GetText())
    # Functional labels first; references second. All remain readable text.
    annotations=[('FV-CTRL RevA2 2026-10-20',143,134,1),('JP1 OFF BEFORE USB',143,189,.8)]
    for fp in b.GetFootprints():
        ref=fp.GetReference();x=p.ToMM(fp.GetPosition().x);y=p.ToMM(fp.GetPosition().y)
        if ref in ['J5','J6','J7','J8']:
            name={'J5':'S1-TOP','J6':'S1-BOT','J7':'S2-TOP','J8':'S2-BOT'}[ref]
            annotations.append((name,x-1,y-2.5,.8))
            for pad,label in zip(sorted(fp.Pads(),key=lambda q:q.GetNumber()),['G','6V','S']):annotations.append((label,197,p.ToMM(pad.GetPosition().y),.8))
        if ref in ['J1','J2','J3']:
            annotations.append(({'J1':'12V IN','J2':'BUCK A 12/G/6/G','J3':'BUCK B 12/G/6/G'}[ref],x-5,y+4,.8))
        if ref in ['J9','J10','J11','J12','J13','J14','J15','J16','J17']:
            annotations.append(({'J9':'RX1 3V/O/G','J10':'RX2 3V/O/G','J11':'TX1 A/K','J12':'TX2 A/K','J13':'LS1 DNP','J14':'LS2 DNP','J15':'LS3 DNP','J16':'LS4 DNP','J17':'3V/SDA/SCL/G'}[ref],x+4,y-3,.8))
        if ref.startswith('TP'):annotations.append((fp.GetValue().replace('+',''),x,y+2.6,.8))
    for value,x,y,size in annotations:
        t=text(b,value,x,y,size);settle(t,(x,y),8)
    for fp in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
        t=fp.Reference();t.SetVisible(True);t.SetTextSize(pt(.8,.8));t.SetTextThickness(p.FromMM(.12));t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));t.SetKeepUpright(True)
        settle(t,(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)),8)
    p.SaveBoard(str(ROOT/'hardware/reva2'/f'{NAME}.kicad_pcb'),b);print('Silkscreen references and pin labels placed. Run ERC/DRC.')
if __name__=='__main__':{'place':place,'dsn':exchange,'power-dsn':lambda:exchange(True),'ses':session,'power-ses':lambda:session(True),'finish':finish,'silk':silk}[sys.argv[1]]()
