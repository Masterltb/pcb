"""Reviewed RevA2 carrier. Never overwrites RevA or exports manufacturing files.

Run with KiCad Python. Schematic and placement share this explicit pin-level spec;
the independent gate reads KiCad's exported netlist, not the manifest.
"""
from pathlib import Path
import json, re, sys, csv
import pcbnew as pcb
from generate_fv_schematic import SchBuilder, PIN_DB, extract_symbol_pins, get_pin_pos

ROOT = Path(__file__).resolve().parents[1]
NAME = 'FV-CTRL_RevA2'
LIB = ROOT / 'libs/fv_reva2.pretty'
STD = Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
LIB.mkdir(exist_ok=True)
PARTS = []
RFP = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'
CFP = 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm'
def add(ref, value, symbol, footprint, pins, pos, mpn, dnp=False):
    PARTS.append(dict(ref=ref,value=value,lib_id=symbol,footprint=footprint,pins={str(k):v for k,v in pins.items()},pos=pos,mpn=mpn,dnp=dnp))
def resistor(ref,value,nets,pos,dnp=False):
    add(ref,value,'Device:R',RFP,dict(enumerate(nets,1)),pos,'Vishay MRS25; select resistance suffix before ordering',dnp)
def cap(ref,value,nets,pos,bulk=False,dnp=False):
    add(ref,value,'Device:C_Polarized' if bulk else 'Device:C',
        ('Capacitor_THT:CP_Radial_D12.5mm_P5.00mm' if ref in ('C1','C2') else 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm') if bulk else CFP,
        dict(enumerate(nets,1)),pos,'Panasonic EEU-FR1C222 (C1/C2); other capacitors pending exact MPN' if bulk else 'Kemet C315 series; select capacitance suffix',dnp)
def connector(ref,value,nets,pos,fp,mpn,dnp=False):
    n=len(nets)
    sym=f'Connector_Generic:Conn_01x{n:02}'
    if sym not in PIN_DB: PIN_DB[sym]=extract_symbol_pins('Connector_Generic.kicad_sym',sym.split(':')[1])
    add(ref,value,sym,fp,dict(enumerate(nets,1)),pos,mpn,dnp)
def tp(ref,net,pos):
    add(ref,net,'Connector:TestPoint','TestPoint:TestPoint_THTPad_D3.0mm_Drill1.5mm',{1:net},pos,'Keystone 5000 loop; verify lead fit before ordering')
TER='Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_{}-G-5,08_1x{:02}_P5.08mm_Horizontal'
connector('J1','12V INPUT',['+12V_IN','GND'],(108,108,180),TER.format(2,2),'Phoenix 1757242 + plug 1757019')
for ref,x,rail in [('J2',133,'A'),('J3',163,'B')]:
    connector(ref,f'XL4015 {rail}: 12/G/6/G',['+12V','GND',f'+6V_{rail}_RAW','GND'],(x,108,180),TER.format(4,4),'Phoenix 1757268 + plug 1757035')
add('F1','T5A - VERIFY I2T','Device:Fuse','Fuse:Fuseholder_Clip-5x20mm_Littelfuse_111_Inline_P20.00x5.00mm_D1.05mm_Horizontal',{1:'+12V_IN',2:'+12V_FUSED'},(108,122,0),'Littelfuse 0215005.MXP + 2x 01110001L; interrupt rating review required')
add('Q1','IRF4905PBF','Device:Q_PMOS','fv_reva2:PMOS_GDS',{ 'G':'Q1_GATE','D':'+12V_FUSED','S':'+12V'},(137,124,0),'Infineon IRF4905PBF')
resistor('R9','10k',['Q1_GATE','GND'],(137,133,0))
add('D1','1.5KE15CA','Device:D_TVS','Diode_THT:D_DO-201AD_P15.24mm_Horizontal',{1:'+12V',2:'GND'},(148,122,0),'Littelfuse 1.5KE15CA')
PIN_DB['Device:D_Zener']=extract_symbol_pins('Device.kicad_sym','D_Zener')
add('D7','BZX55C12','Device:D_Zener','Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal',{1:'+12V',2:'Q1_GATE'},(148,131,0),'Vishay BZX55C12')
for i,x,rail in [(2,168,'A'),(3,185,'B')]:
    add(f'F{i}','MF-R300','Device:Polyfuse','fv_reva2:MF_R300',{1:f'+6V_{rail}_RAW',2:f'+6V_{rail}'},(x,123,0),'Bourns MF-R300')
for i,x in [(1,168),(2,185)]:
    rail='A' if i==1 else 'B'
    cap(f'C{i}','2200uF 16V',[f'+6V_{rail}','GND'],(x,140,0),bulk=True)
    cap(f'C{i+2}','100nF',[f'+6V_{rail}','GND'],(x,150,0))
connector('J4','5V D24V25F5',[None,'+12V','GND','GND','+5V'],(113,138,0),'fv_reva2:Pololu_D24V25F5','Pololu 2850 D24V25F5; socket + male header')
connector('JP1','REMOVE BEFORE USB',['+5V','+5V_DEVKIT'],(124,193,0),'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical','Harwin M20-9990246 + M7567-05 shunt')
left=['+3V3',None,None,None,'IR_RX1','IR_RX2','LS4','SPARE_GPIO33','LS1','LS2','LS3',None,None,'GND',None,None,None,None,'+5V_DEVKIT']
right=['GND','ESP_IR_TX','I2C_SCL',None,None,'I2C_SDA','GND','ESP_S2_BOT_PWM','ESP_S2_TOP_PWM',None,'ESP_S1_BOT_PWM','ESP_S1_TOP_PWM',None,None,None,None,None,None,None]
for ref,nets,x in [('J18',left,130),('J19',right,155.4)]:
    connector(ref,'DEVKITC V4 '+('LEFT' if ref=='J18' else 'RIGHT'),nets,(x,150,0),'Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical','Samtec SSQ-119-03-G-S; DevKitC-32E separate assembly item')
cap('C5','10uF 25V',['+5V','GND'],(123,139,0),bulk=True)
cap('C6','100nF',['+3V3','GND'],(119,153,0))
servo_names=['S1_TOP','S1_BOT','S2_TOP','S2_BOT']
for i,name in enumerate(servo_names,1):
    y=157+(i-1)*10
    rail='A' if i<3 else 'B'
    connector(f'J{i+4}',name,['GND',f'+6V_{rail}',name+'_PWM'],(194,y,0),'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical','Harwin M20-9990346')
    resistor(f'R{i}','330R',['ESP_'+name+'_PWM',name+'_PWM'],(168,y,0))
    resistor(f'R{i+4}','10k',[name+'_PWM','GND'],(181,y,90))
for i,y in [(1,156),(2,168)]:
    connector(f'J{i+8}',f'IR RX{i} 3V3/OUT/G',['+3V3',f'IR_RX{i}','GND'],(106,y,270),'Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical','JST B3B-XH-A + XHP-3 + SXH-001T-P0.6')
for i,y in [(1,180),(2,191)]:
    connector(f'J{i+10}',f'IR TX{i} A/K',[f'IR_TX{i}_A','IR_TX_RET'],(106,y,270),'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical','JST B2B-XH-A + XHP-2 + SXH-001T-P0.6')
    resistor(f'R{i+13}','120R',['+5V',f'IR_TX{i}_A'],(115,y,0))
resistor('R13','330R',['ESP_IR_TX','Q2_BASE'],(114,172,0))
resistor('R25','10k',['Q2_BASE','GND'],(123,164,90))
add('Q2','P2N2222AG','Device:Q_NPN','fv_reva2:NPN_CBE',{'C':'IR_TX_RET','B':'Q2_BASE','E':'GND'},(123,174,0),'onsemi P2N2222AG; do not substitute PN2222 without pinout check')
for i,x in enumerate([162,172,182,192],1):
    connector(f'J{i+12}',f'LS{i} DNP',[f'LS{i}','GND'],(x,195,0),'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical','JST B2B-XH-A + XHP-2',True)
    # RC parts below in left-upper free area, not under removable DevKit.
    rx=107+(i-1)*12
    resistor(f'R{i+15}','10k',[f'LS{i}','+3V3'],(rx,147,90),True)
    cap(f'C{i+6}','100nF',[f'LS{i}','GND'],(rx,143,0),dnp=True)
connector('J17','I2C 3V3/SDA/SCL/G',['+3V3','I2C_SDA','I2C_SCL','GND'],(117,198,90),'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical','Harwin M20-9990446')
for idx,(rail,x,y,rval) in enumerate([('+12V',108,132,'5.6k'),('+6V_A',168,113,'2.2k'),('+6V_B',185,113,'2.2k'),('+5V',108,151,'1.5k'),('+3V3',119,158,'1k')],2):
    resistor(f'R{idx+18}',rval,[rail,f'LED{idx}_A'],(x,y,0))
    add(f'D{idx}',rail,'Device:LED','LED_THT:LED_D3.0mm',{1:'GND',2:f'LED{idx}_A'},(x+10,y,0),'Kingbright L-934GD; resistor-limited indicator')
for i,(net,x,y) in enumerate([('+12V',145,115),('+6V_A',166,154),('+6V_B',184,154),('+5V',120,132),('+3V3',124,158),('GND',128,114),('GND',190,132),('SPARE_GPIO33',124,185)],1): tp(f'TP{i}',net,(x,y,0))
for i,(x,y) in enumerate([(104,104),(196,104),(104,196),(196,196)],1):
    add('H'+str(i),'M3 MOUNT','Mechanical:MountingHole','MountingHole:MountingHole_3.2mm_M3',{},(x,y,0),'M3 nylon standoff + screw; height per enclosure')

def footprints():
    # Letter-numbered generic symbols are explicitly mapped to physical leads.
    for name,src,mapping in [('PMOS_GDS','Package_TO_SOT_THT:TO-220-3_Vertical',{'1':'G','2':'D','3':'S'}),('NPN_CBE','Package_TO_SOT_THT:TO-92_Inline_Wide',{'1':'C','2':'B','3':'E'})]:
        lib,n=src.split(':'); text=(STD/(lib+'.pretty')/(n+'.kicad_mod')).read_text(encoding='utf-8')
        text=text.replace(f'(footprint "{n}"',f'(footprint "{name}"',1)
        for k,v in mapping.items(): text=text.replace(f'(pad "{k}"',f'(pad "{v}"')
        (LIB/(name+'.kicad_mod')).write_text(text,encoding='utf-8')
    # MF-R300: 12mm body, 5.1mm nominal lead spacing, 0.81mm max lead.
    def custom(name,pads,body):
        x1,y1,x2,y2=body
        lines=[f'(footprint "{name}" (version 20260206) (generator "pcbnew") (layer "F.Cu") (attr through_hole)',
               '(property "Reference" "REF**" (at 0 -3) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
               f'(property "Value" "{name}" (at 0 3) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))']
        for layer,margin,w in [('F.Fab',0,.1),('F.CrtYd',.5,.05),('F.SilkS',.12,.12)]:
            lines.append(f'(fp_rect (start {x1-margin} {y1-margin}) (end {x2+margin} {y2+margin}) (stroke (width {w}) (type default)) (fill none) (layer "{layer}"))')
        for num,x,y,diam,drill in pads:
            lines.append(f'(pad "{num}" thru_hole {"rect" if num=="1" else "circle"} (at {x} {y}) (size {diam} {diam}) (drill {drill}) (layers "*.Cu" "*.Mask"))')
        lines.append(')'); (LIB/(name+'.kicad_mod')).write_text('\n'.join(lines),encoding='utf-8')
    custom('MF_R300',[('1',0,0,2.4,1.2),('2',5.1,0,2.4,1.2)],(-3.45,-1.5,8.55,1.5))
    # Official labeled TOP photo 0J10080: EN/VIN/GND/GND/VOUT left to right.
    # Mechanical PDF bottom view is mirrored; it is not the pinout reference.
    custom('Pololu_D24V25F5',[(str(i+1),i*2.54,0,1.9,1.0) for i in range(5)],(-5.1,-16.53,12.7,1.27))
    for parent,prefix in [(ROOT/'hardware','../'),(ROOT,'')]:
        (parent/'fp-lib-table').write_text(f'(fp_lib_table (version 7) (lib (name "fv_modules") (type "KiCad") (uri "${{KIPRJMOD}}/{prefix}libs/fv_modules.pretty") (options "") (descr "Legacy")) (lib (name "fv_reva2") (type "KiCad") (uri "${{KIPRJMOD}}/{prefix}libs/fv_reva2.pretty") (options "") (descr "Reviewed RevA2")))\n',encoding='utf-8')
    project=json.loads((ROOT/'hardware/FV-CTRL_RevA.kicad_pro').read_text())
    ds=project['board']['design_settings']; ds['drc_exclusions']=[]
    ds['rules'].update(min_clearance=.25,min_through_hole_diameter=.4,min_silk_clearance=.1)
    ds['rule_severities'].update(footprint_type_mismatch='warning',missing_courtyard='warning')
    (ROOT/'hardware'/f'{NAME}.kicad_pro').write_text(json.dumps(project,indent=2),encoding='utf-8')

def schematic():
    sb=SchBuilder()
    # Display functional groups using a stable grid with one net label per pin.
    # Each connector still has explicit NC markers on all unused pins.
    groups=[('POWER',lambda p:p['ref'] in ['J1','J2','J3','J4','F1','F2','F3','Q1','D1','D7','R9','C1','C2','C3','C4','C5','JP1']),
            ('DEVKIT AND IO',lambda p:p['ref'] in ['J18','J19','J17','TP8','C6']),
            ('SERVO PWM',lambda p:p['ref'] in ['J5','J6','J7','J8'] or p['ref'] in [f'R{i}' for i in range(1,9)]),
            ('IR',lambda p:p['ref'] in ['J9','J10','J11','J12','Q2','R13','R14','R15','R25']),
            ('LIMIT DNP / MOUNTING',lambda p:p['ref'].startswith('H') or p['ref'] in [f'J{i}' for i in range(13,17)]+[f'R{i}' for i in range(16,20)]+[f'C{i}' for i in range(7,11)]),
            ('DIAGNOSTICS',lambda p:p['ref'] in [f'R{i}' for i in range(20,25)]+[f'D{i}' for i in range(2,7)]+[f'TP{i}' for i in range(1,8)])]
    used=set()
    for gi,(title,predicate) in enumerate(groups):
        subset=[p for p in PARTS if predicate(p)]; used.update(p['ref'] for p in subset)
        # A1 landscape: six group columns, stagger components every 30 mm.
        gx=round((30+gi*130)/1.27)*1.27
        sb.add_box(gx-15,15,gx+110,535,title)
        cursor=35.56
        for p in subset:
            lib,sym=p['lib_id'].split(':'); sb.add_lib_symbol(lib+'.kicad_sym',sym,p['lib_id'])
            x=round((gx+35)/1.27)*1.27; y=cursor; cursor+=round(max(27,len(p['pins'])*2.54+15)/1.27)*1.27
            sb.add_symbol(p['lib_id'],p['ref'],p['value'],x,y,footprint=p['footprint'],dnp=p['dnp'],mpn=p['mpn'],pin_names=list(p['pins']))
            # Avoid overlapping reference/value with long 19-pin connector bodies.
            if len(p['pins'])>8:
                sb.elements[-1]=sb.elements[-1].replace(f'{y-2.54:.4f} 0)',f'{y-28:.4f} 0)',1).replace(f'{y+2.54:.4f} 0)',f'{y+28:.4f} 0)',1)
            for num,net in p['pins'].items():
                px,py=get_pin_pos(p['lib_id'],num,x,y)
                if net is None: sb.add_no_connect(px,py); continue
                dx=-5.08 if px<=x else 5.08
                sb.add_wire(px,py,px+dx,py); sb.add_label(net,px+dx,py,180 if dx>0 else 0)
                sb.record_net(net,p['ref']+'.'+num,'power' if net.startswith('+') or net=='GND' else 'signal')
    assert used=={p['ref'] for p in PARTS}, {p['ref'] for p in PARTS}-used
    text=sb.build().replace('(paper "A3")','(paper "A1")').replace('FV-CTRL Rev A (Fruit Vending Controller)','FV-CTRL RevA2 - External Dual XL4015').replace('Rev A (Engineering Draft)','RevA2 - ENGINEERING REVIEW').replace('2026-10-16','2026-10-20')
    (ROOT/'hardware'/f'{NAME}.kicad_sch').write_text(text,encoding='utf-8')
    (ROOT/'hardware'/f'{NAME}.design.json').write_text(json.dumps(dict(parts=PARTS,nets=sb.manifest_nets),indent=2),encoding='utf-8')
    with (ROOT/'docs'/f'{NAME}-bom.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f); w.writerow(['Reference','Value','MPN','Footprint','DNP','Release status'])
        for p in PARTS:w.writerow([p['ref'],p['value'],p['mpn'],p['footprint'],p['dnp'],'ENGINEERING - procurement not released'])

if __name__=='__main__':
    footprints(); schematic()
    print(f'Generated {NAME} schematic/spec, {len(PARTS)} parts. Run ERC before layout.')
