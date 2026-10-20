"""RevB mixed-technology layout. RF and crystal are routed before autorouting."""
from pathlib import Path
import json,sys,math,re,xml.etree.ElementTree as E
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];NAME='FV-CTRL_RevB';FILE=ROOT/'hardware'/f'{NAME}.kicad_pcb'
STD=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
spec=json.loads((ROOT/'hardware'/f'{NAME}.design.json').read_text());parts={a['ref']:a for a in spec['parts']}
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def xy(v):return (p.ToMM(v.x),p.ToMM(v.y))
def box(f):
    f.BuildCourtyardCaches();a=f.GetCourtyard(p.F_CrtYd).BBox()
    if a.GetWidth()==0:a=f.GetBoundingBox(False,False)
    return tuple(p.ToMM(v) for v in [a.GetX(),a.GetY(),a.GetRight(),a.GetBottom()])
def hits(a,b,gap=.2):return a[0]<b[2]+gap and a[2]>b[0]-gap and a[1]<b[3]+gap and a[3]>b[1]-gap
def segment(b,a,c,net,width=.2,layer=p.F_Cu):
    if a==c:return
    t=p.PCB_TRACK(b);t.SetStart(pt(*a));t.SetEnd(pt(*c));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(b.FindNet(net));b.Add(t)
def via(b,x,y,net='GND',diam=.5,drill=.25):
    v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(p.FromMM(diam));v.SetDrill(p.FromMM(drill));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet(net));b.Add(v)
def polyarea(b,coords,layers,tracks=False,vias=False,copper=False):
    z=p.ZONE(b);z.SetIsRuleArea(True);ls=p.LSET()
    for l in layers:ls.AddLayer(l)
    z.SetLayerSet(ls);z.SetDoNotAllowTracks(tracks);z.SetDoNotAllowVias(vias);z.SetDoNotAllowZoneFills(copper);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
    o=z.Outline();o.NewOutline()
    for x,y in coords:o.Append(p.FromMM(x),p.FromMM(y))
    b.Add(z)

def reference_areas(b):
    for x1,y1,x2,y2 in [(140.2,151.2,145.8,156.8),(128,150.9,141,153.6)]:
        polyarea(b,[(x1,y1),(x2,y1),(x2,y2),(x1,y2)],[p.B_Cu],tracks=True)
    # Keep reference under the actual crystal body and clock paths. A bounding
    # rectangle over the entire unused fanout region needlessly traps power pins.
    polyarea(b,[(140.8,143.7),(145.2,143.7),(145.2,147.3),(140.8,147.3)],[p.B_Cu],tracks=True)
    # The central area beneath the crystal body also stays free of top traces;
    # its four corner-pad connections remain outside this small central window.
    for x1,y1,x2,y2 in [(142.6,144.25,143.4,146.75),(141.4,145.25,144.6,145.75)]:
        polyarea(b,[(x1,y1),(x2,y1),(x2,y2),(x1,y2)],[p.F_Cu],tracks=True)
    for t in b.GetTracks():
        if t.GetClass()!='PCB_TRACK' or not t.GetNetname().startswith('XTAL_'):continue
        a,c=xy(t.GetStart()),xy(t.GetEnd());dx,dy=c[0]-a[0],c[1]-a[1];length=math.hypot(dx,dy)
        if not length:continue
        ux,uy=dx/length,dy/length;nx,ny=-uy*.30,ux*.30
        a=(a[0]-ux*.30,a[1]-uy*.30);c=(c[0]+ux*.30,c[1]+uy*.30)
        polyarea(b,[(a[0]+nx,a[1]+ny),(c[0]+nx,c[1]+ny),(c[0]-nx,c[1]-ny),(a[0]-nx,a[1]-ny)],[p.B_Cu],tracks=True)

FIXED={'U1':(143,154,0),'U4':(150.5,166,0),'U2':(143,185,0),'J20':(128.8,152.075,0),'J21':(143,196.5,0),
       'Y1':(143,145.5,0),'R36':(142.2,148.5,90),'C24':(139.8,146.5,90),'C25':(146.2,144.5,90),
       'C30':(139.1,151.755,90),'L1':(137.8,152.075,180),'C31':(136.6,151.755,90),'D8':(134.4,151.75,90),
       'U3':(131,176,0),'SW1':(129,189,0),'SW2':(151,189,0),'C11':(124,175,0),'C12':(132,183,0),
       'C21':(135.5,156.5,0),'C22':(139.2,153.1,180),'C41':(156.2,163.8,0),
       'C50':(137.5,183,0),'C51':(137.5,186,0),'C52':(143.4,189.4,0),
       'C53':(139.5,184.3,90),'C54':(139.5,186.4,90),'C55':(141.8,188.2,0)}
PREF={'C13':(143,159,0),'C14':(137.5,155.0,90),'C15':(137.5,157,90),'C16':(138.5,150,90),'C17':(141.5,158,0),'C18':(146,150,90),'C19':(145,149,90),'C23':(141.2,150,90),'C20':(140,161,0),'C21':(138.5,153.8,0),'C22':(139.3,153.4,90),'L2':(136,155,90),'C26':(139.5,149,90),'C27':(140,147.7,0),'R37':(138,147.5,90),
      'R40':(148,154.5,0),'R41':(148,152.5,0),'R42':(150,151,0),'R43':(152,152.7,0),'R44':(150,156,0),'R45':(148,158,0),'C40':(147,156,90),'C41':(155,164,90),'R47':(146.5,164,0),'R48':(146.5,168,0),'R49':(154,168,0),
      'R30':(139,162,0),'R31':(145,162,0),'R32':(140,165,0),'R33':(139,167,0),'R34':(143,167,0),'R35':(141,169,0),
      'C50':(139,184,90),'C51':(139,186,90),'C52':(142,181,0),'C53':(140,182,0),'C54':(144,181,0),'C55':(146,184,90),'R50':(147,195,90),'R51':(147,193,90),'R52':(138.5,188,90),'R53':(146,177,0),'R54':(148,183,0),'R55':(148,185,0),'Q3':(147,179,0),'Q4':(151,180,0),'D9':(142,195,0),'D10':(144,195,0)}

def place():
    b=p.BOARD();b.SetCopperLayerCount(2);b.SetFileName(str(FILE));ds=b.GetDesignSettings()
    ds.m_MinClearance=p.FromMM(.12);ds.m_TrackMinWidth=p.FromMM(.12);ds.m_MinThroughDrill=p.FromMM(.2);ds.m_HoleToHoleMin=p.FromMM(.25);ds.m_CopperEdgeClearance=p.FromMM(.5)
    x=E.parse(ROOT/'reports/RevB.net.xml').getroot();nodemap={}
    for n in x.findall('nets/net'):
        net=p.NETINFO_ITEM(b,n.attrib['name']);b.Add(net)
        for node in n.findall('node'):nodemap[node.attrib['ref'],node.attrib['pin']]=net
    comps={c.attrib['ref']:c for c in x.findall('components/comp')}
    old=p.LoadBoard(str(ROOT/'hardware/FV-CTRL_RevA2.kicad_pcb'));oldpos={f.GetReference():(*xy(f.GetPosition()),f.GetOrientationDegrees()) for f in old.GetFootprints()}
    for part in spec['parts']:
        lib,name=part['footprint'].split(':');path=ROOT/'libs/fv_reva2.pretty' if lib=='fv_reva2' else STD/(lib+'.pretty')
        f=p.FootprintLoad(str(path),name)
        if not f:raise RuntimeError('Missing '+part['footprint'])
        b.Add(f);ref=part['ref'];f.SetReference(ref);f.SetValue(part['value']);f.SetFPIDAsString(part['footprint']);f.SetPath(p.KIID_PATH('/'+comps[ref].findtext('tstamps')))
        x0,y0,a=FIXED.get(ref,PREF.get(ref,oldpos.get(ref,part['pos'])));f.SetPosition(pt(x0,y0));f.SetOrientationDegrees(a)
        f.Value().SetVisible(False);f.Reference().SetVisible(False)
        f.SetAttributes(f.GetAttributes()&~p.FP_EXCLUDE_FROM_BOM)
        if part['dnp']:f.SetAttributes(f.GetAttributes()|p.FP_DNP)
        for pad in f.Pads():
            if (ref,pad.GetNumber()) in nodemap:pad.SetNet(nodemap[ref,pad.GetNumber()])
    # Preserve grouped edge connector locations, and all intentionally fixed RF parts.
    fixed=set(FIXED)|{'J1','J2','J3','J5','J6','J7','J8','J9','J10','J11','J12','H1','H2','H3','H4'}
    fs={f.GetReference():f for f in b.GetFootprints()};occupied=[box(fs[r]) for r in fixed]
    occupied.extend([(xx-1.4,yy-1.4,xx+1.4,yy+1.4) for xx,yy in [(128,103),(198,135),(102,135)]])
    # THT packing avoids the entire MCU/RF/flash and USB regions, not just chip bodies.
    reserves=[(125.5,138,158.5,172),(137.3,178,149.5,199.5)]
    mobile=[f for f in fs.values() if f.GetReference() not in fixed]
    mobile.sort(key=lambda f:-(box(f)[2]-box(f)[0])*(box(f)[3]-box(f)[1]))
    for f in mobile:
        ref=f.GetReference();smd=f.GetAttributes()&p.FP_SMD;pref=xy(f.GetPosition());choices=[]
        # New SMT constrained to its functional block; large THT and testpoints outside.
        isnew=ref not in oldpos
        if smd:
            region=(126.5,139,158,172) if parts[ref]['sheet']!='USB / programming' else (136.5,176,157,197)
            step=.5
        else:region=(102,102,197,197);step=1
        for angle in [f.GetOrientationDegrees(),(f.GetOrientationDegrees()+90)%360]:
            f.SetPosition(pt(0,0));f.SetOrientationDegrees(angle);bb=box(f)
            for ix in range(round(region[0]/step),round(region[2]/step)+1):
                for iy in range(round(region[1]/step),round(region[3]/step)+1):
                    xx,yy=ix*step,iy*step;r=(bb[0]+xx,bb[1]+yy,bb[2]+xx,bb[3]+yy)
                    if r[0]<100.5 or r[1]<100.5 or r[2]>199.5 or r[3]>199.5:continue
                    if not smd and any(hits(r,z,0) for z in reserves):continue
                    score=(xx-pref[0])**2+(yy-pref[1])**2
                    choices.append((score,xx,yy,angle,r))
        choices.sort(key=lambda t:t[0])
        for _,xx,yy,a,r in choices:
            if not any(hits(r,o,.15 if smd else .25) for o in occupied):
                f.SetPosition(pt(xx,yy));f.SetOrientationDegrees(a);occupied.append(r);break
        else:raise RuntimeError('No packing space '+ref)
    for a,c in [((100,100),(200,100)),((200,100),(200,200)),((200,200),(100,200)),((100,200),(100,100))]:
        s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(pt(*a));s.SetEnd(pt(*c));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));b.Add(s)
    # Continuous reference under actual MCU, RF and crystal. Do not unnecessarily
    # prohibit fanout in the unused area beside the MCU.
    reference_areas(b)
    # Board-only optical fiducials, no electrical net.
    for idx,(xx,yy) in enumerate([(128,103),(198,135),(102,135)],1):
        f=p.FootprintLoad(str(STD/'Fiducial.pretty'),'Fiducial_1mm_Mask2mm');b.Add(f);f.SetReference('FID'+str(idx));f.SetAttributes(f.GetAttributes()|p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES);f.SetPosition(pt(xx,yy));f.Reference().SetVisible(False);f.Value().SetVisible(False)
    b.BuildConnectivity();p.SaveBoard(str(FILE),b)
    (ROOT/'reports/RevB-placement.json').write_text(json.dumps({f.GetReference():[*xy(f.GetPosition()),f.GetOrientationDegrees()] for f in b.GetFootprints()},indent=2))
    print('Placement saved. Run ERC and DRC before routing.')

def manual():
    b=p.LoadBoard(str(FILE));fs={f.GetReference():f for f in b.GetFootprints()}
    def pad(ref,num):return next(pad for pad in fs[ref].Pads() if pad.GetNumber()==str(num))
    def pos(ref,num):return xy(pad(ref,num).GetPosition())
    def link(a,c,net,width=.15,points=()):
        path=[pos(*a),*points,pos(*c)]
        for x,y in zip(path,path[1:]):segment(b,x,y,net,width)
    # Matching takes the shortest top-side path; broad 50ohm candidate section only
    # after the tiny matching/ESD pads. Final geometry is subject to fab/RF tuning.
    link(('U1',2),('C30',1),'RF_CHIP',.15)
    link(('C30',1),('L1',1),'RF_CHIP',.15)
    segment(b,pos('L1',2),(137.1,152.455),'RF_50',.15)
    segment(b,(137.1,152.455),(137.055,152.5),'RF_50',1.1)
    segment(b,(137.055,152.5),(131.5,152.5),'RF_50',1.1)
    segment(b,(131.5,152.5),pos('J20',1),'RF_50',1.1)
    for ref in ['C31','D8']:
        pp=pos(ref,1);segment(b,pp,(pp[0],152.5),'RF_50',.2)
    link(('U1',45),('R36',1),'XTAL_P',.12,[(142.475,149.4)])
    link(('R36',2),('Y1',1),'XTAL_P_X',.15,[(142.2,148.0)])
    link(('Y1',1),('C24',1),'XTAL_P_X',.15)
    link(('U1',44),('C25',1),'XTAL_N',.12,[(142.825,150.6),(143.3,150.125),(143.3,149),(147.3,145),(147.3,144.98)])
    link(('Y1',3),('C25',1),'XTAL_N',.15)
    # Stitch GND near each new SMT ground pad without placing via in its paste pad.
    blockers=[]
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetNetname()=='GND':continue
            q=a.GetBoundingBox();blockers.append(tuple(p.ToMM(v) for v in [q.GetX(),q.GetY(),q.GetRight(),q.GetBottom()]))
    for t in b.GetTracks():
        if t.GetNetname()=='GND':continue
        q=t.GetBoundingBox();blockers.append(tuple(p.ToMM(v) for v in [q.GetX(),q.GetY(),q.GetRight(),q.GetBottom()]))
    for f in b.GetFootprints():
        if f.GetReference() not in parts or not (f.GetAttributes()&p.FP_SMD):continue
        if f.GetReference() in ['U1','U2']:continue # footprint ground vias already present
        for a in f.Pads():
            if a.GetNetname()!='GND':continue
            x,y=xy(a.GetPosition())
            for dx,dy in [(0,.8),(0,-.8),(.8,0),(-.8,0),(1,1),(-1,1),(1,-1),(-1,-1)]:
                xx,yy=x+dx,y+dy;r=(xx-.25,yy-.25,xx+.25,yy+.25)
                line=(min(x,xx)-.1,min(y,yy)-.1,max(x,xx)+.1,max(y,yy)+.1)
                if not any(hits(r,z,.15) or hits(line,z,.15) for z in blockers):
                    via(b,xx,yy);segment(b,(x,y),(xx,yy),'GND',.2);break
    b.BuildConnectivity();p.SaveBoard(str(FILE),b);print('Manual RF/crystal and local ground vias saved. Run ERC/DRC.')

def ground():
    b=p.LoadBoard(str(FILE));net=b.FindNet('GND')
    for f in b.GetFootprints():
        if f.GetAttributes()&p.FP_SMD:
            for a in f.Pads():
                if a.GetNetname()=='GND':a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    for layer in [p.F_Cu,p.B_Cu]:
        z=p.ZONE(b);z.SetLayer(layer);z.SetNet(net);z.SetLocalClearance(p.FromMM(.2));z.SetMinThickness(p.FromMM(.12));z.SetThermalReliefGap(p.FromMM(.3));z.SetThermalReliefSpokeWidth(p.FromMM(.6));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
        o=z.Outline();o.NewOutline()
        for x,y in [(100.6,100.6),(199.4,100.6),(199.4,199.4),(100.6,199.4)]:o.Append(p.FromMM(x),p.FromMM(y))
        b.Add(z)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b);print('Ground pours and direct SMT ground connections saved. Run ERC/DRC.')

def strip_blocks(s,token):
    # S-expression scanning, respecting quoted identifiers.
    starts=list(re.finditer(r'\('+re.escape(token)+r'\s',s))
    for m in reversed(starts):
        start=m.start();depth=0;quoted=False;escape=False
        for i in range(start,len(s)):
            ch=s[i]
            if escape:escape=False;continue
            if quoted and ch=='\\':escape=True;continue
            if ch=='"':quoted=not quoted
            if quoted:continue
            if ch=='(':depth+=1
            if ch==')':
                depth-=1
                if depth==0:s=s[:start]+s[i+1:];break
    return s

def exchange(power=False,protect_all=False):
    b=p.LoadBoard(str(FILE));path=ROOT/'reports/RevB.dsn';assert p.ExportSpecctraDSN(b,str(path));s=path.read_text()
    (ROOT/'reports/RevB-protected-copper.kicad_pcb').write_text(FILE.read_text())
    # Preserve GND planes. Freerouting plane_as_obstacle=false permits signal
    # routing through a pour while avoiding pointless pad-to-pad GND routing.
    # KiCad must refill and verify real island connectivity after SES import.
    start=s.index('  (network');end=s.index('  (wiring',start);ns=s[start:end]
    ci=ns.find('    (class ')
    if ci>=0:ns=ns[:ci]+')\n'
    nets=[n.GetNetname() for n in b.GetNetsByNetcode().values() if n.GetNetCode()>0]
    # Fine-pitch supply escape first; the main 3.3V distribution must receive
    # a separate copper/voltage-drop review after connectivity is complete.
    widths={2000:[n for n in nets if n.startswith(('+12V','+6V'))],800:[n for n in nets if n=='+5V'],150:[n for n in nets if n in ['+3V3','+3V3_RF','VDD_SDIO']]}
    used={n for nn in widths.values() for n in nn};widths[150]+=[n for n in nets if n not in used]
    via_name=re.search(r'\(via\s+"?([^\s\)"]+)',s).group(1)
    classes=''
    for width,nn in widths.items():
        if nn:classes+='    (class "W'+str(width)+'" '+' '.join('"'+n+'"' for n in nn)+f' (circuit (use_via "{via_name}")) (rule (width {width}) (clearance {250 if width>=800 else 120})))\n'
    ns=ns.rstrip()[:-1]+classes+'  )\n'
    if power:
        # All existing manual nets must remain present so their protected wires
        # and vias are meaningful. Other signal nets are withheld in pass one.
        keep={n for n in nets if n.startswith(('+12V','+6V','RF_','XTAL_')) or n=='GND'}
        def select(m):
            n=re.match(r'    \(net ("[^"]+"|[^\s]+)',m.group(0)).group(1).strip('"')
            return m.group(0) if n in keep else ''
        ns=re.sub(r'    \(net [\s\S]*?\n    \)',select,ns)
        # Classes may only reference nets included in this pass.
        ns=re.sub(r'    \(class [^\n]+\n','',ns)
        for width,nn in [(2000,[n for n in nets if n in keep and n.startswith(('+12V','+6V'))]),(150,[n for n in nets if n in keep and not n.startswith(('+12V','+6V'))])]:
            if nn:ns=ns.rstrip()[:-1]+f'    (class "W{width}" '+' '.join('"'+n+'"' for n in nn)+f' (circuit (use_via "{via_name}")) (rule (width {width}) (clearance {250 if width==2000 else 120})))\n  )\n'
        path=ROOT/'reports/RevB-power.dsn'
    s=s[:start]+ns+s[end:]
    # Prevent autorouter from changing hand-routed RF/crystal and the completed
    # power pass. A later routing pass must preserve these exact copper paths.
    def protect_critical(m):
        block=m.group(0)
        net=re.search(r'\(net\s+("[^"]+"|[^\s)]+)\)',block)
        name=net.group(1).strip('"') if net else ''
        return block.replace('(type route)','(type protect)') if protect_all or name.startswith(('+12V','+6V','RF_','XTAL_')) or name in ['GND','+3V3','+3V3_RF','VDD_SDIO'] else block
    # A wire ends immediately after its net/type fields; vias are single-line.
    s=re.sub(r'    \((?:wire|via)[^\n]+',protect_critical,s)
    path.write_text(s);print('Exported',path)

def session(power=False):
    b=p.LoadBoard(str(FILE));ses=ROOT/'reports'/('RevB-power.ses' if power else 'RevB.ses');assert p.ImportSpecctraSES(b,str(ses))
    p.SaveBoard(str(FILE),b)
    snapshot=ROOT/'reports/RevB-protected-copper.kicad_pcb'
    if snapshot.exists():
        def critical(block):
            m=re.search(r'\(net "([^"]+)"\)',block);n=m[1] if m else ''
            return n.startswith(('+12V','+6V','RF_','XTAL_')) or n in ['GND','+3V3','+3V3_RF','VDD_SDIO']
        pattern=r'\n\t\((?:segment|via)\b[\s\S]*?\n\t\)'
        saved=[m.group(0) for m in re.finditer(pattern,snapshot.read_text()) if critical(m.group(0))]
        text=re.sub(pattern,lambda m:'' if critical(m.group(0)) else m.group(0),FILE.read_text())
        at=text.rfind(')');FILE.write_text(text[:at]+''.join(saved)+'\n'+text[at:])
        b=p.LoadBoard(str(FILE))
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b);print('SES imported; protected copper restored exactly and pours refilled. Run ERC/DRC.')

def fused():
    """Route this PTH-to-PTH power branch on B.Cu at full 2mm width.

    Grid obstacles conservatively expand all physical pads/tracks by the new
    trace radius plus clearance. KiCad DRC remains the authority afterwards.
    """
    import heapq
    project_file=FILE.with_suffix('.kicad_pro');project_bytes=project_file.read_bytes()
    b=p.LoadBoard(str(FILE));net='+12V_FUSED';step=.25;low=406;high=794
    fs={f.GetReference():f for f in b.GetFootprints()}
    start=xy(next(a for a in fs['F1'].Pads() if a.GetNumber()=='2').GetPosition())
    goal=xy(next(a for a in fs['Q1'].Pads() if a.GetNumber()=='D').GetPosition())
    blocked=set()
    def rect_block(bb):
        x1,y1,x2,y2=bb
        for ix in range(max(low,math.ceil(x1/step)),min(high,math.floor(x2/step))+1):
            for iy in range(max(low,math.ceil(y1/step)),min(high,math.floor(y2/step))+1):blocked.add((ix,iy))
    margin=1.25
    for f in b.GetFootprints():
        for a in f.Pads():
            if not a.IsOnLayer(p.B_Cu) or a.GetNetname()==net:continue
            q=a.GetBoundingBox();bb=tuple(p.ToMM(v) for v in [q.GetX(),q.GetY(),q.GetRight(),q.GetBottom()]);rect_block((bb[0]-margin,bb[1]-margin,bb[2]+margin,bb[3]+margin))
    for t in b.GetTracks():
        if t.GetNetname()==net:continue
        if not t.IsOnLayer(p.B_Cu):continue
        if t.GetClass()=='PCB_VIA':
            xx,yy=xy(t.GetPosition());r=p.ToMM(t.GetWidth(p.B_Cu))/2+margin;rect_block((xx-r,yy-r,xx+r,yy+r));continue
        a=xy(t.GetStart());c=xy(t.GetEnd());rad=p.ToMM(t.GetWidth())/2+margin
        vx,vy=c[0]-a[0],c[1]-a[1];den=vx*vx+vy*vy
        for ix in range(max(low,math.ceil((min(a[0],c[0])-rad)/step)),min(high,math.floor((max(a[0],c[0])+rad)/step))+1):
            for iy in range(max(low,math.ceil((min(a[1],c[1])-rad)/step)),min(high,math.floor((max(a[1],c[1])+rad)/step))+1):
                xx,yy=ix*step,iy*step;u=max(0,min(1,((xx-a[0])*vx+(yy-a[1])*vy)/den)) if den else 0
                if (xx-a[0]-u*vx)**2+(yy-a[1]-u*vy)**2<rad*rad:blocked.add((ix,iy))
    rect_block((124.75,138.75,148.25,159.25)) # expanded B.Cu reference keepout
    src=tuple(round(v/step) for v in start);dst=tuple(round(v/step) for v in goal)
    if src in blocked or dst in blocked:raise RuntimeError('Power endpoint blocked '+str((src in blocked,dst in blocked)))
    queue=[(0,src)];cost={src:0};parent={};done=False
    while queue:
        _,u=heapq.heappop(queue)
        if u==dst:done=True;break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            v=(u[0]+dx,u[1]+dy)
            if not(low<=v[0]<=high and low<=v[1]<=high) or v in blocked:continue
            if dx and dy and ((u[0]+dx,u[1]) in blocked or (u[0],u[1]+dy) in blocked):continue
            new=cost[u]+(math.sqrt(2) if dx and dy else 1)
            if new<cost.get(v,1e30):cost[v]=new;parent[v]=u;heapq.heappush(queue,(new+math.hypot(v[0]-dst[0],v[1]-dst[1]),v))
    if not done:raise RuntimeError('No full-width fused path')
    path=[dst]
    while path[-1]!=src:path.append(parent[path[-1]])
    path.reverse();compressed=[path[0]]
    for i in range(1,len(path)-1):
        if (path[i][0]-path[i-1][0],path[i][1]-path[i-1][1])!=(path[i+1][0]-path[i][0],path[i+1][1]-path[i][1]):compressed.append(path[i])
    compressed.append(path[-1]);coords=[start]+[(x*step,y*step) for x,y in compressed]+[goal]
    pads=[xy(a.GetPosition()) for a in fs['F1'].Pads() if a.GetNumber()=='2']
    # Avoid pcbnew Remove(): this Windows SWIG build invalidates borrowed
    # footprint wrappers after track deletion. Filter serialized segment blocks.
    text=FILE.read_text();text=re.sub(r'\n\t\(segment\b[\s\S]*?\n\t\)',lambda m:'' if '(net "+12V_FUSED")' in m.group(0) else m.group(0),text)
    tmp=ROOT/'reports/RevB-without-fused.kicad_pcb';tmp.write_text(text)
    oldb=b;b=p.LoadBoard(str(tmp));b.SetFileName(str(FILE))
    for a,c in zip(coords,coords[1:]):segment(b,a,c,net,2,p.B_Cu)
    segment(b,pads[0],pads[1],net,2,p.B_Cu)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b)
    project_file.write_bytes(project_bytes)
    print('Full width fused branch saved:',len(coords),'vertices. Run ERC/DRC.')

def core_reference():
    # Change only the reference keepout and repair below-process-minimum necks.
    # Never waive shorts/clearance errors. JLCPCB 1oz publishes 0.10/0.10mm;
    # use 0.12mm spacing, 0.10mm absolute width floor for QFN escape.
    project=FILE.with_suffix('.kicad_pro');data=json.loads(project.read_text())
    data['board']['design_settings']['rules'].update(min_clearance=.12,min_track_width=.10,min_hole_clearance=.24)
    data['net_settings']['classes'][0].update(clearance=.12)
    project.write_text(json.dumps(data,indent=2))
    text=FILE.read_text();text=re.sub(r'\n\t\(zone\b[\s\S]*?\n\t\)',lambda m:'' if '(keepout' in m.group(0) else m.group(0),text);FILE.write_text(text)
    b=p.LoadBoard(str(FILE))
    reference_areas(b)
    for t in b.GetTracks():
        if t.GetClass()=='PCB_TRACK' and t.GetWidth()<p.FromMM(.1):t.SetWidth(p.FromMM(.1))
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b);print('Reference keepouts and 1oz manufacturing floors updated. Run ERC/DRC.')

if __name__=='__main__':{'place':place,'manual':manual,'ground':ground,'dsn':exchange,'fanout-dsn':lambda:exchange(False,True),'power-dsn':lambda:exchange(True),'ses':session,'power-ses':lambda:session(True),'fused':fused,'core-reference':core_reference}[sys.argv[1]]()
