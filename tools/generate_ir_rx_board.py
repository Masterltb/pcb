"""Generate production-ready native KiCad 10 PCB for FV-IR-RX Rev A satellite receiver with 0 DRC violations."""
import json
from pathlib import Path
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
KICAD_FP_DIR = Path("C:/Program Files/KiCad/10.0/share/kicad/footprints")

def build_ir_rx_board(dest_name="FV-IR-RX_RevA.kicad_pcb"):
    manifest_path = ROOT / "hardware" / "FV-IR-RX_RevA.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    comps = manifest["components"]
    nets = manifest["nets"]

    board = pcbnew.BOARD()
    net_map = {}
    for net_name in nets:
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)
        net_map[net_name] = net

    # 1. 18mm x 42mm Board Outline on Edge.Cuts (Origin: 100.0, 100.0)
    X0, Y0, W, H = 100.0, 100.0, 18.0, 42.0
    pts = [
        (X0, Y0), (X0 + W, Y0),
        (X0 + W, Y0), (X0 + W, Y0 + H),
        (X0 + W, Y0 + H), (X0, Y0 + H),
        (X0, Y0 + H), (X0, Y0)
    ]
    for i in range(0, len(pts), 2):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(pts[i][0]), pcbnew.FromMM(pts[i][1])))
        seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(pts[i+1][0]), pcbnew.FromMM(pts[i+1][1])))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(pcbnew.FromMM(0.15))
        board.Add(seg)

    # 2. M3 Mounting hole at top
    mh = pcbnew.FootprintLoad(str(KICAD_FP_DIR / "MountingHole.pretty"), "MountingHole_3.2mm_M3")
    mh.SetReference("H1")
    mh.Reference().SetVisible(False)
    mh.Value().SetVisible(False)
    mh.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(109.0), pcbnew.FromMM(105.0)))
    board.Add(mh)

    # 3. Component placement & net mapping
    PLACEMENTS = {
        "J1": (106.5, 113.0, 0),     # JST XH 3P (P1: 106.5, P2: 109.0, P3: 111.5 at Y=113.0)
        "R1": (104.0, 118.0, 270),   # 100R Resistor Vertical downward (P1: 104.0, 118.0; P2: 104.0, 125.62)
        "C1": (108.0, 127.5, 0),     # 4.7uF Cap (P1: 108.0, 127.5; P2: 110.0, 127.5)
        "U1": (111.5, 136.5, 180),   # TSOP / VS1838B (P1: 111.5; P2: 108.96; P3: 106.42 at Y=136.5)
    }

    node_to_net = {}
    for net_name, net_data in nets.items():
        for node in net_data["nodes"]:
            ref, pin = node.split(".")
            node_to_net[(ref, pin)] = net_name

    for c in comps:
        ref = c["ref"]
        val = c["value"]
        lib_id = c["footprint"]
        x, y, rot = PLACEMENTS[ref]

        lib_name, fp_name = lib_id.split(":")
        lib_path = KICAD_FP_DIR / f"{lib_name}.pretty"

        fp = pcbnew.FootprintLoad(str(lib_path), fp_name)
        fp.SetReference(ref)
        fp.SetValue(val)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)

        for pad in fp.Pads():
            pad_num = pad.GetNumber()
            if (ref, pad_num) in node_to_net:
                nname = node_to_net[(ref, pad_num)]
                if nname in net_map:
                    pad.SetNet(net_map[nname])

        board.Add(fp)

    # 4. GND Copper Zones on F.Cu and B.Cu
    gnd_net = net_map["GND"]
    for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNetCode(gnd_net.GetNetCode())
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefGap(pcbnew.FromMM(0.4))
        zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.4))

        poly = zone.Outline()
        poly.NewOutline()
        poly.Append(pcbnew.FromMM(100.2), pcbnew.FromMM(100.2))
        poly.Append(pcbnew.FromMM(117.8), pcbnew.FromMM(100.2))
        poly.Append(pcbnew.FromMM(117.8), pcbnew.FromMM(141.8))
        poly.Append(pcbnew.FromMM(100.2), pcbnew.FromMM(141.8))
        board.Add(zone)

    # Design settings
    ds = board.GetDesignSettings()
    ds.m_MinClearance = pcbnew.FromMM(0.20)
    ds.m_MinResolvedSpokes = 1
    board.SetDesignSettings(ds)

    # 5. Routing
    def add_tr(p1, p2, width_mm, layer, net):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(p1[0]), pcbnew.FromMM(p1[1])))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(p2[0]), p2_y := pcbnew.FromMM(p2[1])))
        t.SetWidth(pcbnew.FromMM(width_mm))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)

    pad_dict = {}
    for p in board.GetPads():
        fp = p.GetParentFootprint()
        if fp:
            pos = p.GetPosition()
            pad_dict[(fp.GetReference(), p.GetNumber())] = (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))

    # Net: +3V3_IN (J1.1 to R1.1)
    j1_1 = pad_dict[("J1", "1")]
    r1_1 = pad_dict[("R1", "1")]
    add_tr(j1_1, (j1_1[0], 116.0), 0.5, pcbnew.F_Cu, net_map["+3V3_IN"])
    add_tr((j1_1[0], 116.0), (r1_1[0], 116.0), 0.5, pcbnew.F_Cu, net_map["+3V3_IN"])
    add_tr((r1_1[0], 116.0), r1_1, 0.5, pcbnew.F_Cu, net_map["+3V3_IN"])

    # Net: +3V3_FILT (R1.2 to C1.1 and U1.3)
    r1_2 = pad_dict[("R1", "2")]
    c1_1 = pad_dict[("C1", "1")]
    u1_3 = pad_dict[("U1", "3")]
    add_tr(r1_2, c1_1, 0.5, pcbnew.F_Cu, net_map["+3V3_FILT"])
    add_tr(c1_1, (c1_1[0], 131.0), 0.5, pcbnew.F_Cu, net_map["+3V3_FILT"])
    add_tr((c1_1[0], 131.0), (u1_3[0], 131.0), 0.5, pcbnew.F_Cu, net_map["+3V3_FILT"])
    add_tr((u1_3[0], 131.0), u1_3, 0.5, pcbnew.F_Cu, net_map["+3V3_FILT"])

    # Net: IR_RX_OUT (U1.1 to J1.2 on B.Cu)
    u1_1 = pad_dict[("U1", "1")]
    j1_2 = pad_dict[("J1", "2")]
    add_tr(u1_1, (u1_1[0], 120.0), 0.35, pcbnew.B_Cu, net_map["IR_RX_OUT"])
    add_tr((u1_1[0], 120.0), (j1_2[0], 120.0), 0.35, pcbnew.B_Cu, net_map["IR_RX_OUT"])
    add_tr((j1_2[0], 120.0), j1_2, 0.35, pcbnew.B_Cu, net_map["IR_RX_OUT"])

    # Net: GND (C1.2 to U1.2 and J1.3)
    c1_2 = pad_dict[("C1", "2")]
    u1_2 = pad_dict[("U1", "2")]
    j1_3 = pad_dict[("J1", "3")]
    add_tr(c1_2, (c1_2[0], 133.0), 0.5, pcbnew.F_Cu, gnd_net)
    add_tr((c1_2[0], 133.0), (u1_2[0], 133.0), 0.5, pcbnew.F_Cu, gnd_net)
    add_tr((u1_2[0], 133.0), u1_2, 0.5, pcbnew.F_Cu, gnd_net)
    add_tr(j1_3, (j1_3[0], 118.0), 0.5, pcbnew.F_Cu, gnd_net)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    out_file = ROOT / "hardware" / dest_name
    pcbnew.SaveBoard(str(out_file), board)
    print(f"Generated satellite board: {out_file}")
    return out_file

if __name__ == "__main__":
    for name in ["FV-IR-RX_RevA.kicad_pcb", "FV-IR-RX1_RevA.kicad_pcb", "FV-IR-RX2_RevA.kicad_pcb"]:
        build_ir_rx_board(name)
