import pcbnew as pn

ROOT_FILE = 'hardware/revb/FV-CTRL_RevB.kicad_pcb'
b = pn.LoadBoard(ROOT_FILE)

def pt(x, y): return pn.VECTOR2I(pn.FromMM(x), pn.FromMM(y))

def add_escape(b, netname, x1, y1, x2, y2):
    t = pn.PCB_TRACK(b)
    t.SetStart(pt(x1, y1))
    t.SetEnd(pt(x2, y2))
    t.SetWidth(pn.FromMM(0.15))
    t.SetLayer(pn.F_Cu)
    t.SetNet(b.FindNet(netname))
    b.Add(t)
    print(f"Added escape for {netname}: ({x1}, {y1}) -> ({x2}, {y2})")

# Add straight perpendicular escapes for the 4 pins
add_escape(b, 'SPI_D', 145.450, 153.475, 146.450, 153.475)
add_escape(b, 'ESP_S2_TOP_PWM', 145.450, 152.775, 146.450, 152.775)
add_escape(b, 'ESP_S1_BOT_PWM', 145.450, 155.575, 146.450, 155.575)
add_escape(b, 'LS4', 140.550, 155.575, 139.550, 155.575)

b.BuildConnectivity()
pn.ZONE_FILLER(b).Fill(b.Zones())
pn.SaveBoard(ROOT_FILE, b)
print("Escapes saved.")
