import subprocess, re
from pathlib import Path
import pcbnew as pn

ROOT = Path(r"F:\project\pcb")
FILE = ROOT / "hardware/revb/FV-CTRL_RevB.kicad_pcb"

b = pn.LoadBoard(str(FILE))

out = subprocess.check_output(['git', 'show', 'HEAD:hardware/revb/FV-CTRL_RevB.kicad_pcb'], encoding='utf-8')

target_nets = ['UART_RX', 'LS4', 'SPI_D', 'ESP_S2_TOP_PWM', 'ESP_S1_BOT_PWM', 'I2C_SDA']

def pt(x, y): return pn.VECTOR2I(pn.FromMM(x), pn.FromMM(y))

# Collect all segments and vias for target nets from HEAD
lines = out.splitlines()
added_tracks = 0
added_vias = 0

for net in target_nets:
    print(f"\nProcessing net: {net}")
    # Find segments
    seg_matches = re.finditer(
        r'\(segment\s+\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(end\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(width\s+([\d\.-]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+"' + re.escape(net) + r'"\)',
        out
    )
    for m in seg_matches:
        x1, y1, x2, y2, w, layer_name = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), m.group(6)
        # Upgrade width: factory rule >= 0.15mm
        new_w = max(0.15, w)
        layer = pn.F_Cu if layer_name == "F.Cu" else pn.B_Cu
        
        t = pn.PCB_TRACK(b)
        t.SetStart(pt(x1, y1))
        t.SetEnd(pt(x2, y2))
        t.SetWidth(pn.FromMM(new_w))
        t.SetLayer(layer)
        t.SetNet(b.FindNet(net))
        b.Add(t)
        added_tracks += 1
        
    # Find vias
    via_matches = re.finditer(
        r'\(via\s+\(at\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(size\s+([\d\.-]+)\)\s+\(drill\s+([\d\.-]+)\)\s+\(layers\s+"F\.Cu"\s+"B\.Cu"\)\s+\(net\s+"' + re.escape(net) + r'"\)',
        out
    )
    for m in via_matches:
        x, y, sz, dr = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
        # Ensure standard via size >= 0.4 / 0.2
        new_sz = max(0.40, sz)
        new_dr = max(0.20, dr)
        
        v = pn.PCB_VIA(b)
        v.SetPosition(pt(x, y))
        v.SetWidth(pn.FromMM(new_sz))
        v.SetDrill(pn.FromMM(new_dr))
        v.SetViaType(pn.VIATYPE_THROUGH)
        v.SetLayerPair(pn.F_Cu, pn.B_Cu)
        v.SetNet(b.FindNet(net))
        b.Add(v)
        added_vias += 1

print(f"\nAdded {added_tracks} tracks and {added_vias} vias with upgraded DFM widths >= 0.15mm.")

b.BuildConnectivity()
pn.ZONE_FILLER(b).Fill(b.Zones())
pn.SaveBoard(str(FILE), b)
print("Board saved.")
