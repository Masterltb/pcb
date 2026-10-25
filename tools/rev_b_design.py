"""Bare ESP32 RevB engineering schematic. Never exports manufacturing files.

Preserves RevA2 as a reference. Run with KiCad's Python; run ERC immediately.
Global net labels intentionally join sheets. RF/crystal values require bench tuning.
"""
from pathlib import Path
import json,re,uuid,csv,copy
from generate_fv_schematic import SchBuilder,PIN_DB,extract_symbol_pins,get_pin_pos

ROOT=Path(__file__).resolve().parents[1]
NAME='FV-CTRL_RevB'
OLD=json.loads((ROOT/'hardware/reva2/FV-CTRL_RevA2.design.json').read_text())
PARTS=[copy.deepcopy(p) for p in OLD['parts'] if p['ref'] not in ['J18','J19','JP1']]
for p in PARTS:p['sheet']='Interfaces'
CUSTOM={}
def uid():return str(uuid.uuid4())
def sym(name,names,types=None):
    """Explicit numbered pins, two sides, 2.54mm pitch; no inheritance ambiguity."""
    lib='fv_revb:'+name; types=types or {}; n=len(names);left=(n+1)//2
    h=max(left,n-left)*2.54/2+2.54; pins=[]; coords={}
    for i,(num,pinname) in enumerate(names.items()):
        side=0 if i<left else 1; j=i if side==0 else i-left
        count=left if side==0 else n-left
        x=-22.86 if side==0 else 22.86;y=round((count-1)*1.27-j*2.54,4);a=0 if side==0 else 180
        coords[str(num)]=(x,y)
        pins.append(f'(pin {types.get(str(num),"passive")} line (at {x} {y} {a}) (length 5.08) (name "{pinname}" (effects (font (size 1.016 1.016)))) (number "{num}" (effects (font (size 1.016 1.016)))))')
    body=f'''(symbol "{lib}" (pin_names (offset 0.762)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 {h+2.54} 0) (effects (font (size 1.27 1.27))))
      (property "Value" "{name}" (at 0 {-h-2.54} 0) (effects (font (size 1.27 1.27))))
      (symbol "{name}_0_1" (rectangle (start -17.78 {h}) (end 17.78 {-h}) (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "{name}_1_1" {''.join(pins)}))'''
    CUSTOM[lib]=(body,h);PIN_DB[lib]=coords;return lib

espnames=dict(enumerate(['VDDA','LNA_IN','VDD3P3','VDD3P3','SENSOR_VP','SENSOR_CAPP','SENSOR_CAPN','SENSOR_VN','CHIP_PU','GPIO34','GPIO35','GPIO32','GPIO33','GPIO25','GPIO26','GPIO27','GPIO14','GPIO12','VDD3P3_RTC','GPIO13','GPIO15','GPIO2','GPIO0','GPIO4','GPIO16','VDD_SDIO','GPIO17','SD_DATA_2','SD_DATA_3','SD_CMD','SD_CLK','SD_DATA_0','SD_DATA_1','GPIO5','GPIO18','GPIO23','VDD3P3_CPU','GPIO19','GPIO22','U0RXD_GPIO3','U0TXD_GPIO1','GPIO21','VDDA','XTAL_N','XTAL_P','VDDA','CAP2','CAP1','EP_GND'],1))
esptype={str(i):'power_in' for i in [1,3,4,19,37,43,46,49]};esptype['26']='power_out'
for i in [5,6,7,8,9,10,11,40,45,47,48]:esptype[str(i)]='input'
esptype['41']='output';esptype['44']='output';esptype['2']='bidirectional'
for i in [12,13,14,15,16,17,18,20,21,22,23,24,25,27,28,29,30,31,32,33,34,35,36,38,39,42]:esptype[str(i)]='bidirectional'
ESP=sym('ESP32-D0WD-V3',espnames,esptype)
CP=sym('CP2102N-A02-GQFN24',dict(enumerate(['RI','GND','D+','D-','VIO','VDD','VREGIN','VBUS_SENSE','RSTb','NC','GPIO3','GPIO2','GPIO1','GPIO0','SUSPENDb','NC','SUSPEND','CTS','RTS','RXD','TXD','DSR','DTR','DCD','EP_GND'],1)),{str(i):'power_in' for i in [2,5,6,7,25]}|{str(i):'input' for i in [1,8,9,18,20,22,24]}|{str(i):'output' for i in [15,17,19,21,23]})
LDO=sym('LD1117V33',{'1':'GND','2':'VOUT_3V3','3':'VIN_5V'},{'1':'power_in','2':'power_out','3':'power_in'})
FLASH=sym('W25Q32JVSSIQ',{'1':'CS#','2':'DO_IO1','3':'WP#_IO2','4':'GND','5':'DI_IO0','6':'CLK','7':'HOLD#_IO3','8':'VCC'},{'4':'power_in','8':'power_in'})
NPN=sym('MMBT3904',{'1':'B','2':'E','3':'C'})
SUP=sym('TLV803EA30DBZR',{'1':'GND','2':'RESET_OD','3':'VDD'},{'1':'power_in','2':'open_collector','3':'power_in'})

R0402='Resistor_SMD:R_0402_1005Metric';C0402='Capacitor_SMD:C_0402_1005Metric';C0603='Capacitor_SMD:C_0603_1608Metric'
C0201='Capacitor_SMD:C_0201_0603Metric';L0201='Inductor_SMD:L_0201_0603Metric'
def add(ref,value,lib,fp,pins,sheet,mpn,notes='',pos=(143,160,0),dnp=False):
    if lib not in PIN_DB and lib not in CUSTOM:
        l,n=lib.split(':');PIN_DB[lib]=extract_symbol_pins(l+'.kicad_sym',n)
    PARTS.append(dict(ref=ref,value=value,lib_id=lib,footprint=fp,pins={str(k):v for k,v in pins.items()},sheet=sheet,mpn=mpn,notes=notes,pos=list(pos),dnp=dnp))
def r(ref,value,a,b,sheet,mpn=None,notes='',dnp=False):
    add(ref,value,'Device:R',R0402,{1:a,2:b},sheet,mpn or ('Yageo RC0402FR-07 resistance suffix: '+value),notes,dnp=dnp)
def c(ref,value,a,b,sheet,mpn,fp=C0402,notes='',dnp=False):add(ref,value,'Device:C',fp,{1:a,2:b},sheet,mpn,notes,dnp=dnp)
def tp(ref,net):add(ref,net,'Connector:TestPoint','fv_reva2:Keystone_5000_Carrier_D3',{1:net},'USB / programming','Keystone 5000')

BUCK=sym('RECOM_R78E5V1A',{'1':'VIN','2':'GND','3':'VOUT_5V'})
for part in PARTS:
    if part['ref']=='J4':
        part.update(value='5V R-78E5.0-1.0',lib_id=BUCK,footprint='fv_modules:RECOM_R78E5V1A',
                    pins={'1':'+12V','2':'GND','3':'+5V'},pos=[114.54,138,0],mpn='R-78E5.0-1.0',
                    notes='Direct THT 5V/1A; qualify load, ripple, hot-plug and thermal behavior')
add('C57','10uF 50V','Device:C_Polarized','Capacitor_THT:CP_Radial_D5.0mm_P2.00mm',
    {1:'+12V',2:'GND'},'Power','EEUFR1H100','RECOM local input reservoir',pos=(120,124.5,270))
c('C58','100nF','+5V','GND','Power','GRM155R71C104KA88D',notes='RECOM output bypass')
PARTS[-1]['pos']=[118.1,141.25,270]

espnets={i:None for i in range(1,50)}
espnets.update({1:'+3V3',2:'RF_CHIP',3:'+3V3_RF',4:'+3V3_RF',9:'ESP_EN',10:'IR_RX1',11:'IR_RX2',12:'LS4',13:'SPARE_GPIO33',14:'LS1',15:'LS2',16:'LS3',18:'STRAP_GPIO12',19:'+3V3',21:'STRAP_GPIO15',22:'STRAP_GPIO2',23:'ESP_BOOT',25:'ESP_S1_TOP_PWM',26:'VDD_SDIO',27:'ESP_S1_BOT_PWM',28:'SPI_HD',29:'SPI_WP',30:'SPI_CS',31:'SPI_CLK',32:'SPI_Q',33:'SPI_D',34:'STRAP_GPIO5',35:'ESP_S2_TOP_PWM',36:'ESP_IR_TX',37:'+3V3',38:'ESP_S2_BOT_PWM',39:'I2C_SCL',40:'UART_RX',41:'UART_TX_RAW',42:'I2C_SDA',43:'+3V3',44:'XTAL_N',45:'XTAL_P',46:'+3V3',47:'CAP2',48:'CAP1',49:'GND'})
add('U1','ESP32-D0WD-V3',ESP,'Package_DFN_QFN:QFN-48-1EP_5x5mm_P0.35mm_EP3.7x3.7mm_ThermalVias',espnets,'ESP32 core','ESP32-D0WD-V3','Bare IC; 5x5mm; 16 ground vias 0.2mm; bottom tented by mask definition; assembler review/X-ray required')
add('U3','LD1117V33',LDO,'Package_TO_SOT_THT:TO-220-3_Vertical',{1:'GND',2:'+3V3',3:'+5V'},'Power','LD1117V33','800mA; thermal qualification required at (5-3.3)*I')
add('U4','W25Q32JVSSIQ',FLASH,'Package_SO:SOIC-8_5.3x5.3mm_P1.27mm',{1:'FLASH_CS',2:'FLASH_Q',3:'FLASH_WP',4:'GND',5:'FLASH_D',6:'FLASH_CLK',7:'FLASH_HD',8:'VDD_SDIO'},'Flash','W25Q32JVSSIQ','4MB, 3.3V; firmware/QE qualification required')
for num,a,b in [(40,'SPI_CS','FLASH_CS'),(41,'SPI_CLK','FLASH_CLK'),(42,'SPI_Q','FLASH_Q'),(43,'SPI_D','FLASH_D'),(44,'SPI_WP','FLASH_WP'),(45,'SPI_HD','FLASH_HD')]:r('R'+str(num),'0R',a,b,'Flash','RC0402JR-070RL','Series tuning footprint near ESP32')
for num,net in [(47,'FLASH_CS'),(48,'FLASH_WP'),(49,'FLASH_HD')]:r('R'+str(num),'10k',net,'VDD_SDIO','Flash','RC0402FR-0710KL')
c('C40','1uF','VDD_SDIO','GND','Flash','GRM155R61A105KE15D')
c('C41','100nF','VDD_SDIO','GND','Flash','GRM155R71C104KA88D')

for num,net in [(30,'ESP_EN'),(31,'ESP_BOOT'),(34,'STRAP_GPIO5'),(35,'STRAP_GPIO15')]:r('R'+str(num),'10k',net,'+3V3','ESP32 core','RC0402FR-0710KL')
for num,net in [(32,'STRAP_GPIO2'),(33,'STRAP_GPIO12')]:r('R'+str(num),'10k',net,'GND','ESP32 core','RC0402FR-0710KL')
c('C20','1uF','ESP_EN','GND','ESP32 core','GRM155R61A105KE15D')
add('U5','TLV803EA30DBZR',SUP,'Package_TO_SOT_SMD:SOT-23',{1:'GND',2:'ESP_EN',3:'+3V3'},'ESP32 core','TLV803EA30DBZR','3.08V supervisor, 200ms nominal delay; TI pin1=GND variant')
c('C56','100nF','+3V3','GND','ESP32 core','GRM155R71C104KA88D')
for num in [11,12]:
    add('C'+str(num),'10uF 50V','Device:C_Polarized','Capacitor_THT:CP_Radial_D5.0mm_P2.00mm',{1:'+5V' if num==11 else '+3V3',2:'GND'},'Power','EEUFR1H100','LDO input/output reservoir; min 10uF per ST')
for num,net in [(13,'+3V3'),(14,'+3V3_RF'),(15,'+3V3_RF')]:c('C'+str(num),'10uF',net,'GND','ESP32 core','GRM188R60J106ME47D',C0603,'Verify effective capacitance at 3.3V')
for num in [16,17,18,19]:c('C'+str(num),'100nF','+3V3','GND','ESP32 core','GRM155R71C104KA88D')
c('C23','100nF','+3V3','GND','ESP32 core','GRM033R71C104KE14D',C0201,'Local VDDA pin1 bypass; Standard PCBA 0201')
c('C21','1uF','+3V3_RF','GND','ESP32 core','GRM155R61A105KE15D')
c('C22','100nF','+3V3_RF','GND','ESP32 core','GRM033R71C104KE14D',C0201)
add('L2','2.0nH','Device:L',L0201,{1:'+3V3',2:'+3V3_RF'},'ESP32 core','LQP03TN2N0B02D','600mA rating per Murata; RF supply filter')

add('Y1','40MHz CL10pF','Device:Crystal_GND24','Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm',{1:'XTAL_P_X',2:'GND',3:'XTAL_N',4:'GND'},'Clock / RF','ABM8-40.000MHZ-10-1-U-T','Abracon catalog CL10pF +/-10ppm tolerance/stability; -10..60C; factory sourcing needs confirmation')
r('R36','0R','XTAL_P','XTAL_P_X','Clock / RF','RC0402JR-070RL','Crystal harmonic tuning footprint')
c('C24','16pF','XTAL_P_X','GND','Clock / RF','GRM1555C1H160JA01D',notes='INITIAL: CL10pF, assumed stray2pF => C=16pF. Measure frequency and tune.')
c('C25','16pF','XTAL_N','GND','Clock / RF','GRM1555C1H160JA01D',notes='INITIAL; not measured crystal tuning')
c('C26','10nF','CAP1','GND','Clock / RF','GRM155R71C103KA01D')
c('C27','3.3nF','CAP2','CAP1','Clock / RF','GRM155R71H332KA01D')
r('R37','20k','CAP2','CAP1','Clock / RF','RC0402FR-0720KL','CAP network per chip datasheet')
c('C30','1.5pF','RF_CHIP','GND','Clock / RF','GRM0335C1H1R5BA01D',C0201,'INITIAL chip match; RF tune required')
add('L1','2.7nH','Device:L',L0201,{1:'RF_CHIP',2:'RF_50'},'Clock / RF','LQP03TN2N7B02D','INITIAL chip match; RF tune required')
c('C31','0.5pF','RF_50','GND','Clock / RF','GRM0335C1HR50BA01D',C0201,'INITIAL: D8 adds 0.9pF typ; combined nominal 1.4pF plus parasitics, RF tuning required')
add('J20','SMA 50ohm ANT','Connector:Conn_Coaxial','Connector_Coaxial:SMA_Amphenol_132134_Vertical',{1:'RF_50',2:'GND'},'Clock / RF','Amphenol 132134','Use external 2.4GHz 50ohm antenna, correct SMA gender, not RP-SMA')
add('D8','PESD5V0X1BL','Device:D_TVS','Diode_SMD:D_SOD-882',{1:'RF_50',2:'GND'},'Clock / RF','PESD5V0X1BL,315','0.9pF typical; include in RF tuning and validate ESD')

cpnets={i:None for i in range(1,26)}
cpnets.update({2:'GND',3:'USB_DP',4:'USB_DM',5:'+3V3',6:'+3V3',7:'+3V3',8:'USB_VBUS_SENSE',9:'USB_RESET',19:'USB_RTS',20:'UART_TX',21:'UART_RX',23:'USB_DTR',25:'GND'})
add('U2','CP2102N-A02-GQFN24',CP,'Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm_ThermalVias',cpnets,'USB / programming','CP2102N-A02-GQFN24','Self powered 3.3V, VREGIN=VDD=VIO; USB does NOT power board; grounded EP with vias')
add('J21','USB MICRO DATA','Connector:USB_B_Micro','Connector_USB:USB_Micro-B_Molex-105017-0001',{1:'USB_VBUS',2:'USB_DM',3:'USB_DP',4:None,5:'GND','SH':'GND'},'USB / programming','Molex 105017-0001','Board needs 12V during programming; no USB power injection')
r('R50','22.1k','USB_VBUS','USB_VBUS_SENSE','USB / programming','RC0402FR-0722K1L')
r('R51','47.5k','USB_VBUS_SENSE','GND','USB / programming','RC0402FR-0747K5L')
r('R52','1k','USB_RESET','+3V3','USB / programming','RC0402FR-071KL')
r('R53','499R','UART_TX_RAW','UART_TX','USB / programming','RC0402FR-07499RL','Place close to ESP32')
for num in [50,51,52]:c('C'+str(num),'4.7uF','+3V3','GND','USB / programming','GRM155R60J475ME87D')
for num in [53,54,55]:c('C'+str(num),'100nF','+3V3','GND','USB / programming','GRM155R71C104KA88D')
for ref,net in [('D9','USB_DP'),('D10','USB_DM')]:add(ref,'PESD5V0X1BL','Device:D_TVS','Diode_SMD:D_SOD-882',{1:net,2:'GND'},'USB / programming','PESD5V0X1BL,315','Place at USB connector; system ESD test not run')
for ref,b,e,coll in [('Q3','AUTO_EN_BASE','USB_RTS','ESP_EN'),('Q4','AUTO_BOOT_BASE','USB_DTR','ESP_BOOT')]:add(ref,'MMBT3904',NPN,'Package_TO_SOT_SMD:SOT-23',{1:b,2:e,3:coll},'USB / programming','MMBT3904LT1G','Cross coupled auto-download; verify DTR/RTS truth table and timing')
r('R54','10k','USB_DTR','AUTO_EN_BASE','USB / programming','RC0402FR-0710KL')
r('R55','10k','USB_RTS','AUTO_BOOT_BASE','USB / programming','RC0402FR-0710KL')
for ref,net in [('SW1','ESP_EN'),('SW2','ESP_BOOT')]:add(ref,'RESET' if ref=='SW1' else 'BOOT','Switch:SW_Push','Button_Switch_THT:SW_PUSH_6mm',{1:net,2:'GND'},'USB / programming','Omron B3F-1000','Manual recovery/programming')
for ref,net in [('TP9','ESP_EN'),('TP10','ESP_BOOT'),('TP11','UART_TX'),('TP12','UART_RX')]:tp(ref,net)

def assign_sheets():
    for p in PARTS:
        if p['sheet']!='Interfaces':continue
        ref=p['ref']
        if ref in ['J1','J2','J3','J4','F1','F2','F3','Q1','R9','D1','D7','C1','C2','C3','C4','C5']:p['sheet']='Power'
        elif ref in ['J5','J6','J7','J8']+[f'R{i}' for i in range(1,9)]:p['sheet']='Servo'
        elif ref in ['J9','J10','J11','J12','R13','R14','R15','R25','R26','R27','R28','R29','Q2']:p['sheet']='IR'
        elif ref in [f'J{i}' for i in range(13,17)]+[f'R{i}' for i in range(16,20)]+[f'C{i}' for i in range(7,11)]:p['sheet']='Limits DNP'
        else:p['sheet']='Diagnostics'

def global_label(sb,net,x,y,angle):
    angle=180-angle
    sb.labels.append(f'(global_label "{net}" (shape passive) (at {x:.4f} {y:.4f} {angle}) (effects (font (size 1.016 1.016)) (justify {"right" if angle==180 else "left"})) (uuid "{uid()}"))')

def schematic():
    assign_sheets();groups=['Power','ESP32 core','Clock / RF','Flash','Servo','IR','Limits DNP','Diagnostics','USB / programming']
    root=SchBuilder();root.add_box(15,15,395,270,'FV-CTRL RevB - bare ESP32 / external SMA','ENGINEERING DRAFT - NOT FOR FABRICATION')
    root.add_lib_symbol('power.kicad_sym','PWR_FLAG','power:PWR_FLAG')
    for i,net in enumerate(['+5V','+3V3_RF']):
        x=round((65+i*115)/1.27)*1.27;y=250.19
        root.add_power_sym('power:PWR_FLAG',x,y)
        root.add_wire(x,y,x-5.08,y);global_label(root,net,x-5.08,y,0)
    children=[]
    for si,title in enumerate(groups):
        parts=[p for p in PARTS if p['sheet']==title]; sb=SchBuilder()
        sb.add_box(10,10,405,275,title,'Same global net name = electrical connection across all pages')
        large=[p for p in parts if len(p['pins'])>12];small=[p for p in parts if p not in large]
        placements={}
        for idx,p in enumerate(large):placements[p['ref']]=(78.74+idx*120,106.68)
        # Remaining symbols use functional rows with readable ref/value spacing.
        for idx,p in enumerate(small):
            cols=3 if large else 4; col=idx%cols;row=idx//cols
            x=(193.04 if large else 55.88)+col*(66.04 if large else 96.52)
            y=40.64+row*27.94
            if y>255:raise RuntimeError('Page overflow '+title)
            placements[p['ref']]=(x,y)
        for part in parts:
            lib=part['lib_id'];short=lib.split(':')[1];x,y=placements[part['ref']]
            if lib in CUSTOM:sb.lib_symbols[lib]=CUSTOM[lib][0]
            else:
                sb.add_lib_symbol(lib.split(':')[0]+'.kicad_sym',short,lib)
                if lib not in PIN_DB:PIN_DB[lib]=extract_symbol_pins(lib.split(':')[0]+'.kicad_sym',short)
            sb.add_symbol(lib,part['ref'],part['value'],x,y,footprint=part['footprint'],dnp=part['dnp'],mpn=part['mpn'],pin_names=list(part['pins']))
            if lib in CUSTOM:
                h=CUSTOM[lib][1];sb.elements[-1]=sb.elements[-1].replace(f'{y-2.54:.4f} 0)',f'{y-h-5.08:.4f} 0)',1).replace(f'{y+2.54:.4f} 0)',f'{y+h+5.08:.4f} 0)',1)
            elif lib in ['Device:R','Device:C','Device:C_Polarized','Device:L','Device:D_TVS']:
                sb.elements[-1]=sb.elements[-1].replace(f'{x:.4f} {y-2.54:.4f} 0)',f'{x+8.89:.4f} {y-1.27:.4f} 0)',1).replace(f'{x:.4f} {y+2.54:.4f} 0)',f'{x+8.89:.4f} {y+1.27:.4f} 0)',1)
            seen={}
            for pin,net in part['pins'].items():
                px,py=get_pin_pos(lib,pin,x,y)
                if (px,py) in seen:
                    assert seen[px,py]==net;continue
                seen[px,py]=net
                if net is None:sb.add_no_connect(px,py);continue
                dx=-5.08 if px<=x else 5.08;end=px+dx
                sb.add_wire(px,py,end,py);global_label(sb,net,end,py,0 if dx<0 else 180)
        filename=f'{NAME}-{si+1:02}.kicad_sch'
        data=sb.build().replace('FV-CTRL Rev A (Fruit Vending Controller)',f'FV-CTRL RevB / {title}').replace('Rev A (Engineering Draft)','RevB - NOT RELEASED').replace('2026-10-16','2026-10-20').replace('2-layer THT | Dual-column FIFO servo & IR control','2-layer mixed SMT/THT | QFN bare IC | external SMA')
        (ROOT/'hardware/revb'/filename).write_text(data,encoding='utf-8')
        su=uid();sx=30+(si%3)*120;sy=45+(si//3)*65
        children.append(f'''(sheet (at {sx} {sy}) (size 105 40) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{su}")
          (property "Sheetname" "{si+1}. {title}" (at {sx} {sy-2} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
          (property "Sheetfile" "{filename}" (at {sx} {sy+42} 0) (effects (font (size 1.016 1.016)) (justify left top))))''')
    data=root.build().replace('FV-CTRL Rev A (Fruit Vending Controller)','FV-CTRL RevB - schematic index').replace('Rev A (Engineering Draft)','RevB - NOT RELEASED').replace('2026-10-16','2026-10-20').replace('2-layer THT | Dual-column FIFO servo & IR control','2-layer mixed SMT/THT | bare QFN | external SMA')
    data=data[:-2]+'\n'+ '\n'.join(children)+'\n)\n'
    (ROOT/'hardware/revb'/f'{NAME}.kicad_sch').write_text(data,encoding='utf-8')
    (ROOT/'hardware/revb'/f'{NAME}.design.json').write_text(json.dumps({'parts':PARTS},indent=2),encoding='utf-8')
    with (ROOT/'docs/revb/bom'/f'{NAME}-bom-draft.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['Reference','Value','MPN','Footprint','Population','Assembly','Qualification'])
        for p in PARTS:w.writerow([p['ref'],p['value'],p['mpn'],p['footprint'],'DNP' if p['dnp'] else 'FIT','SMT' if any(t in p['footprint'] for t in ['_SMD:','Package_SO:','Package_DFN','SOT_SMD','Crystal:','Connector_USB:']) else 'THT',p.get('notes','Incoming inspection and prototype qualification required')])
    project=json.loads((ROOT/'hardware/reva2/FV-CTRL_RevA2.kicad_pro').read_text())
    ds=project['board']['design_settings'];ds['rules'].update(min_clearance=.12,min_track_width=.10,min_hole_clearance=.24,min_through_hole_diameter=.2,min_via_diameter=.45)
    project['net_settings']['classes'][0].update(clearance=.12,track_width=.2,via_diameter=.5,via_drill=.25)
    (ROOT/'hardware/revb'/f'{NAME}.kicad_pro').write_text(json.dumps(project,indent=2),encoding='utf-8')
    library='(kicad_symbol_lib (version 20250114) (generator "fv_revb")\n'
    library+='\n'.join(body.replace(f'(symbol "{lib}"',f'(symbol "{lib.split(":")[1]}"',1) for lib,(body,_) in CUSTOM.items())+'\n)\n'
    (ROOT/'libs/fv_revb.kicad_sym').write_text(library,encoding='utf-8')
    (ROOT/'hardware/revb/sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "fv_revb") (type "KiCad") (uri "${KIPRJMOD}/../../libs/fv_revb.kicad_sym") (options "") (descr "Bare ESP32 RevB")))\n',encoding='utf-8')
    print('RevB schematic generated:',len(PARTS),'parts, 9 functional pages plus index. Run ERC before any PCB work.')

if __name__=='__main__':schematic()
