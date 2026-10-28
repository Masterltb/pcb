"""
Remove dangling tracks reported by KiCad DRC.
"""
from pathlib import Path
import json, re, subprocess
import pcbnew as pn

ROOT = Path(__file__).resolve().parents[1]
PCB_PATH = ROOT / "hardware/rev_s3/FV-CTRL_RevS3.kicad_pcb"
DRC_JSON = ROOT / "reports/rev_s3/RevS3-routing-drc.json"
KICAD_CLI = "C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"

def run_drc():
    subprocess.run([KICAD_CLI, "pcb", "drc", "--format", "json", "--output", str(DRC_JSON), str(PCB_PATH)], check=True, stdout=subprocess.DEVNULL)
    with open(DRC_JSON, "r") as f:
        return json.load(f)

def clean():
    d = run_drc()
    dangling_uuids = set()
    for v in d.get("violations", []):
        if v.get("type") == "track_dangling":
            dangling_uuids.add(v["items"][0]["uuid"])

    print(f"Identified {len(dangling_uuids)} dangling track UUIDs.")
    if not dangling_uuids:
        return

    text = PCB_PATH.read_text(encoding="utf-8")
    for u in dangling_uuids:
        # Match segment with this UUID
        text = re.sub(rf'\n\t\(segment\b[\s\S]*?\(uuid "{u}"\)[\s\S]*?\n\t\)', '', text)
    
    PCB_PATH.write_text(text, encoding="utf-8")

    # Reload board and refill zones
    b = pn.LoadBoard(str(PCB_PATH))
    b.BuildConnectivity()
    pn.ZONE_FILLER(b).Fill(b.Zones())
    pn.SaveBoard(str(PCB_PATH), b)

    d2 = run_drc()
    print(f"DRC after clean: {len(d2.get('violations', []))} violations, {len(d2.get('unconnected_items', []))} unconnected items.")
    for vi in d2.get("violations", []):
        print(f"  V: {vi.get('type')} {vi.get('description')}")
    for it in d2.get("unconnected_items", []):
        f, s = it.get("items", [{}, {}])
        print(f"  Open: {f.get('description')} -> {s.get('description')}")

if __name__ == "__main__":
    clean()
