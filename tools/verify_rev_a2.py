"""Independent checks against the actual KiCad-exported XML and optional PCB."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,sys
ROOT=Path(__file__).resolve().parents[1]
xml=ET.parse(ROOT/'reports/RevA2.net.xml').getroot()
actual={}
for net in xml.findall('nets/net'):
    for node in net.findall('node'): actual[node.attrib['ref']+'.'+node.attrib['pin']]=net.attrib['name'].removeprefix('/')
errors=[]
def require(node,net):
    if actual.get(node)!=net: errors.append(f'{node}: expected {net}, got {actual.get(node)}')
# DevKitC V4 official pinout, independent of the authoring data.
for node,net in {'J19.12':'ESP_S1_TOP_PWM','J19.11':'ESP_S1_BOT_PWM','J19.9':'ESP_S2_TOP_PWM','J19.8':'ESP_S2_BOT_PWM','J19.2':'ESP_IR_TX','J18.5':'IR_RX1','J18.6':'IR_RX2','J18.9':'LS1','J18.10':'LS2','J18.11':'LS3','J18.7':'LS4','J19.6':'I2C_SDA','J19.3':'I2C_SCL','J18.8':'SPARE_GPIO33','J18.19':'+5V_DEVKIT','J18.1':'+3V3'}.items(): require(node,net)
for node,net in {'J2.3':'+6V_A_RAW','F2.1':'+6V_A_RAW','F2.2':'+6V_A','J3.3':'+6V_B_RAW','F3.1':'+6V_B_RAW','F3.2':'+6V_B','Q1.D':'+12V_FUSED','Q1.S':'+12V','D7.1':'+12V','D7.2':'Q1_GATE','Q2.E':'GND','Q2.C':'IR_TX_RET','JP1.1':'+5V','JP1.2':'+5V_DEVKIT'}.items():require(node,net)
for i in range(2,7):require(f'D{i}.1','GND');require(f'D{i}.2',f'LED{i}_A')
for node,net in {'J4.2':'+12V','J4.3':'GND','J4.4':'GND','J4.5':'+5V'}.items():require(node,net)
if not actual.get('J4.1','').startswith('unconnected-'):errors.append('Pololu EN must be NC')
spec=json.loads((ROOT/'hardware/FV-CTRL_RevA2.design.json').read_text())
for p in spec['parts']:
    for pin,net in p['pins'].items():
        if net is not None:require(p['ref']+'.'+pin,net)
if '--pcb' in sys.argv:
    import pcbnew as pcb
    board=pcb.LoadBoard(str(ROOT/'hardware/FV-CTRL_RevA2.kicad_pcb'))
    bnodes={fp.GetReference()+'.'+pad.GetNumber():pad.GetNetname().removeprefix('/') for fp in board.GetFootprints() for pad in fp.Pads() if pad.GetNumber()}
    for node,net in actual.items():
        if bnodes.get(node)!=net:errors.append(f'PCB {node}: {bnodes.get(node)} != schematic {net}')
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetAttribute()==pcb.PAD_ATTRIB_SMD:errors.append('SMD pad '+fp.GetReference())
    pitch=pcb.ToMM(next(f for f in board.GetFootprints() if f.GetReference()=='J19').GetPosition().x-next(f for f in board.GetFootprints() if f.GetReference()=='J18').GetPosition().x)
    if abs(pitch-25.4)>.001:errors.append(f'DevKit row pitch {pitch}')
result=dict(status='FAIL' if errors else 'PASS',errors=errors,source='KiCad 10 exported XML',pcb_checked='--pcb' in sys.argv,limits='Does not prove thermal/EMC/ESD/mechanical safety or production qualification')
(ROOT/'reports/RevA2-functional-gate.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2));sys.exit(bool(errors))
