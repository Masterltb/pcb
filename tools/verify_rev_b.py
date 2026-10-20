"""Independent check of KiCad-exported RevB nodes, optionally actual PCB pads."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,sys
ROOT=Path(__file__).resolve().parents[1]
x=ET.parse(ROOT/'reports/revb/verified/RevB.net.xml').getroot();actual={};errors=[]
for n in x.findall('nets/net'):
    for node in n.findall('node'):actual[node.attrib['ref'],node.attrib['pin']]=n.attrib['name']
def expect(ref,pins):
    for pin,net in pins.items():
        found=actual.get((ref,str(pin)))
        if found!=net:errors.append(f'{ref}.{pin}: {found} != {net}')
expect('U1',{1:'+3V3',2:'RF_CHIP',3:'+3V3_RF',4:'+3V3_RF',9:'ESP_EN',10:'IR_RX1',11:'IR_RX2',12:'LS4',13:'SPARE_GPIO33',14:'LS1',15:'LS2',16:'LS3',18:'STRAP_GPIO12',19:'+3V3',21:'STRAP_GPIO15',22:'STRAP_GPIO2',23:'ESP_BOOT',25:'ESP_S1_TOP_PWM',26:'VDD_SDIO',27:'ESP_S1_BOT_PWM',28:'SPI_HD',29:'SPI_WP',30:'SPI_CS',31:'SPI_CLK',32:'SPI_Q',33:'SPI_D',34:'STRAP_GPIO5',35:'ESP_S2_TOP_PWM',36:'ESP_IR_TX',37:'+3V3',38:'ESP_S2_BOT_PWM',39:'I2C_SCL',40:'UART_RX',41:'UART_TX_RAW',42:'I2C_SDA',43:'+3V3',44:'XTAL_N',45:'XTAL_P',46:'+3V3',47:'CAP2',48:'CAP1',49:'GND'})
expect('U3',{1:'GND',2:'+3V3',3:'+5V'})
expect('U5',{1:'GND',2:'ESP_EN',3:'+3V3'})
expect('U4',{1:'FLASH_CS',2:'FLASH_Q',3:'FLASH_WP',4:'GND',5:'FLASH_D',6:'FLASH_CLK',7:'FLASH_HD',8:'VDD_SDIO'})
expect('U2',{2:'GND',3:'USB_DP',4:'USB_DM',5:'+3V3',6:'+3V3',7:'+3V3',8:'USB_VBUS_SENSE',9:'USB_RESET',19:'USB_RTS',20:'UART_TX',21:'UART_RX',23:'USB_DTR',25:'GND'})
expect('J21',{1:'USB_VBUS',2:'USB_DM',3:'USB_DP',5:'GND','SH':'GND'})
expect('Q3',{1:'AUTO_EN_BASE',2:'USB_RTS',3:'ESP_EN'});expect('Q4',{1:'AUTO_BOOT_BASE',2:'USB_DTR',3:'ESP_BOOT'})
expect('R50',{1:'USB_VBUS',2:'USB_VBUS_SENSE'});expect('R51',{1:'USB_VBUS_SENSE',2:'GND'})
expect('R33',{1:'STRAP_GPIO12',2:'GND'});expect('R32',{1:'STRAP_GPIO2',2:'GND'})
expect('R31',{1:'ESP_BOOT',2:'+3V3'});expect('C26',{1:'CAP1',2:'GND'});expect('C27',{1:'CAP2',2:'CAP1'});expect('R37',{1:'CAP2',2:'CAP1'})
expect('J2',{1:'+12V',2:'GND',3:'+6V_A_RAW',4:'GND'});expect('J3',{1:'+12V',2:'GND',3:'+6V_B_RAW',4:'GND'})
expect('F2',{1:'+6V_A_RAW',2:'+6V_A'});expect('F3',{1:'+6V_B_RAW',2:'+6V_B'})
for ref,rail,sig in [('J5','A','S1_TOP_PWM'),('J6','A','S1_BOT_PWM'),('J7','B','S2_TOP_PWM'),('J8','B','S2_BOT_PWM')]:expect(ref,{1:'GND',2:'+6V_'+rail,3:sig})
for ref,net in [('D2','LED2_A'),('D3','LED3_A'),('D4','LED4_A'),('D5','LED5_A'),('D6','LED6_A')]:expect(ref,{1:'GND',2:net})
spec=json.loads((ROOT/'hardware/revb/FV-CTRL_RevB.design.json').read_text())
for part in spec['parts']:
    for pin,net in part['pins'].items():
        if net is not None:expect(part['ref'],{pin:net})
components=x.findall('components/comp')
if len(components)!=len(spec['parts']):errors.append('Component count mismatch')
if '--pcb' in sys.argv:
    import pcbnew as p
    b=p.LoadBoard(str(ROOT/'hardware/revb/FV-CTRL_RevB.kicad_pcb'));bnodes={}
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            k=(fp.GetReference(),pad.GetNumber())
            if k in bnodes and bnodes[k]!=pad.GetNetname():errors.append('Conflicting multi-pad net '+str(k))
            bnodes[k]=pad.GetNetname()
    for k,net in actual.items():
        if bnodes.get(k)!=net:errors.append('PCB mismatch '+str(k))
    if any(fp.GetReference() in ['J18','J19'] for fp in b.GetFootprints()):errors.append('DevKit sockets remain')
    if b.GetCopperLayerCount()!=2:errors.append('Layer count')
    for t in b.GetTracks():
        if t.GetClass()=='PCB_TRACK' and t.GetNetname().startswith(('+12V','+6V')) and p.ToMM(t.GetWidth())<2:errors.append('Power below2mm '+t.GetNetname())
result=dict(status='FAIL' if errors else 'PASS',errors=errors,pcb_checked='--pcb' in sys.argv,limits='Does not prove RF tuning, impedance, thermals, EMC/ESD, crystal accuracy, mechanical function or production qualification')
(ROOT/'reports/revb/verified/RevB-functional-gate.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));sys.exit(bool(errors))
