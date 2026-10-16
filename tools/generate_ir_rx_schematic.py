"""Native KiCad 10 Schematic Generator for FV-IR-RX Satellite Boards.

Generates:
1. hardware/FV-IR-RX_RevA.kicad_sch - Standard satellite IR RX board schematic
2. hardware/FV-IR-RX_RevA.manifest.json - Manifest of components and nets
3. Optionally per-column specific schematics:
   - hardware/FV-IR-RX1_RevA.kicad_sch (Column 1 satellite)
   - hardware/FV-IR-RX2_RevA.kicad_sch (Column 2 satellite)
"""
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / "hardware"
REPORTS = ROOT / "reports"
KICAD_SYM_DIR = Path("C:/Program Files/KiCad/10.0/share/kicad/symbols")


def gen_uuid():
    return str(uuid.uuid4())


def extract_sexpr(content: str, start_str: str) -> str:
    idx = content.find(start_str)
    if idx == -1:
        raise ValueError(f"Start string '{start_str}' not found")
    depth = 0
    in_string = False
    escape = False
    for i in range(idx, len(content)):
        ch = content[i]
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    return content[idx:i+1]
    raise ValueError(f"Unmatched S-expression starting at {start_str}")


def get_lib_symbol(lib_file: str, sym_name: str, target_lib_id: str) -> str:
    path = KICAD_SYM_DIR / lib_file
    if not path.exists():
        raise FileNotFoundError(f"KiCad symbol library not found at: {path}")
    content = path.read_text(encoding="utf-8", errors="ignore")
    body = extract_sexpr(content, f'(symbol "{sym_name}"')
    short_target = target_lib_id.split(":")[-1]
    body = re.sub(rf'^\(symbol "{re.escape(sym_name)}"', f'(symbol "{target_lib_id}"', body, count=1)
    body = re.sub(rf'\(symbol "{re.escape(sym_name)}(_[0-9]+_[0-9]+)"', rf'(symbol "{short_target}\1"', body)
    return "\t\t" + body.replace("\n", "\n\t\t")


def extract_symbol_pins(lib_file: str, sym_name: str):
    path = KICAD_SYM_DIR / lib_file
    content = path.read_text(encoding="utf-8", errors="ignore")
    body = extract_sexpr(content, f'(symbol "{sym_name}"')

    pins = {}
    lines = body.splitlines()
    curr_at = None
    for line in lines:
        l = line.strip()
        if l.startswith("(at ") and ("(number " not in l) and ("(name " not in l):
            parts = l[4:-1].split()
            if len(parts) >= 2:
                try:
                    curr_at = (float(parts[0]), float(parts[1]))
                except ValueError:
                    pass
        elif l.startswith('(number "'):
            num = l.split('"')[1]
            if curr_at is not None:
                pins[num] = curr_at
                curr_at = None
    return pins


PIN_DB = {
    "Device:R": extract_symbol_pins("Device.kicad_sym", "R"),
    "Device:C_Polarized": extract_symbol_pins("Device.kicad_sym", "C_Polarized"),
    "Connector_Generic:Conn_01x03": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x03"),
    "Interface_Optical:TSOP581xx": extract_symbol_pins("Interface_Optical.kicad_sym", "TSOP581xx"),
    "power:GND": extract_symbol_pins("power.kicad_sym", "GND"),
    "power:+3V3": extract_symbol_pins("power.kicad_sym", "+3V3"),
    "power:PWR_FLAG": extract_symbol_pins("power.kicad_sym", "PWR_FLAG"),
}


def get_pin_pos(lib_id: str, pin_num: str | int, sx: float, sy: float, rot: int = 0) -> tuple[float, float]:
    px, py = PIN_DB[lib_id][str(pin_num)]
    if rot == 0:
        return round(sx + px, 4), round(sy - py, 4)
    elif rot == 90:
        return round(sx - py, 4), round(sy - px, 4)
    elif rot == 180:
        return round(sx - px, 4), round(sy + py, 4)
    elif rot == 270:
        return round(sx + py, 4), round(sy + px, 4)
    else:
        raise ValueError(f"Unsupported rotation: {rot}")


class IrRxSchBuilder:
    def __init__(self, title: str, subtitle: str, rev: str = "Rev A"):
        self.title = title
        self.subtitle = subtitle
        self.rev = rev
        self.lib_symbols = {}
        self.elements = []
        self.wires = []
        self.labels = []
        self.no_connects = []
        self.junctions = []
        self.annotations = []
        self.manifest_parts = []
        self.manifest_nets = {}

    def add_lib_symbol(self, lib_file: str, sym_name: str, target_lib_id: str):
        if target_lib_id not in self.lib_symbols:
            self.lib_symbols[target_lib_id] = get_lib_symbol(lib_file, sym_name, target_lib_id)

    def add_symbol(self, lib_id: str, ref: str, val: str, x: float, y: float, rot: int = 0,
                   pins_count: int = 2, footprint: str = "", desc: str = "", dnp: bool = False,
                   mpn: str = "TBD", pin_names: list = None):
        sym_uuid = gen_uuid()
        dnp_str = "yes" if dnp else "no"
        pin_blocks = []
        if pin_names:
            for p in pin_names:
                pin_blocks.append(f'\t\t(pin "{p}" (uuid "{gen_uuid()}"))')
        else:
            for i in range(1, pins_count + 1):
                pin_blocks.append(f'\t\t(pin "{i}" (uuid "{gen_uuid()}"))')
        pin_block_str = "\n".join(pin_blocks)

        s = f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x:.4f} {y:.4f} {rot})
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp {dnp_str})
\t\t(uuid "{sym_uuid}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x:.4f} {y - 2.54:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "{val}"
\t\t\t(at {x:.4f} {y + 2.54:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "{footprint}"
\t\t\t(at {x:.4f} {y:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at {x:.4f} {y:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Description" "{desc}"
\t\t\t(at {x:.4f} {y:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
{pin_block_str}
\t)"""
        self.elements.append(s)
        self.manifest_parts.append({
            "ref": ref,
            "value": val,
            "lib_id": lib_id,
            "footprint": footprint if footprint else "TBD",
            "dnp": dnp,
            "description": desc,
            "mpn": mpn
        })

    def add_power_sym(self, sym_name: str, x: float, y: float, rot: int = 0):
        p_uuid = gen_uuid()
        ref_id = f"#PWR{len(self.elements)+2000}"
        s = f"""\t(symbol
\t\t(lib_id "{sym_name}")
\t\t(at {x:.4f} {y:.4f} {rot})
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{p_uuid}")
\t\t(property "Reference" "{ref_id}"
\t\t\t(at {x:.4f} {y - 2.54:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Value" "{sym_name.split(':')[-1]}"
\t\t\t(at {x:.4f} {y - 2.54:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at {x:.4f} {y:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t)"""
        self.elements.append(s)

    def add_wire(self, x1: float, y1: float, x2: float, y2: float):
        w_uuid = gen_uuid()
        s = f"""\t(wire
\t\t(pts
\t\t\t(xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f})
\t\t)
\t\t(stroke (width 0) (type default))
\t\t(uuid "{w_uuid}")
\t)"""
        self.wires.append(s)

    def add_label(self, name: str, x: float, y: float, rot: int = 0):
        l_uuid = gen_uuid()
        s = f"""\t(label "{name}"
\t\t(at {x:.4f} {y:.4f} {rot})
\t\t(effects (font (size 1.27 1.27)))
\t\t(uuid "{l_uuid}")
\t)"""
        self.labels.append(s)

    def add_junction(self, x: float, y: float):
        j_uuid = gen_uuid()
        s = f"""\t(junction
\t\t(at {x:.4f} {y:.4f})
\t\t(diameter 1.016)
\t\t(color 0 0 0 0)
\t\t(uuid "{j_uuid}")
\t)"""
        self.junctions.append(s)

    def add_box(self, x1: float, y1: float, x2: float, y2: float, title: str, subtitle: str = ""):
        rect_uuid = gen_uuid()
        t1_uuid = gen_uuid()
        t2_uuid = gen_uuid()
        self.annotations.append(f"""\t(rectangle
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(stroke (width 0.254) (type dash))
\t\t(fill (type none))
\t\t(uuid "{rect_uuid}")
\t)""")
        self.annotations.append(f"""\t(text "{title}"
\t\t(exclude_from_sim no)
\t\t(at {x1 + 3.81:.4f} {y1 + 5.08:.4f} 0)
\t\t(effects (font (size 2.0 2.0) bold) (justify left bottom))
\t\t(uuid "{t1_uuid}")
\t)""")
        if subtitle:
            self.annotations.append(f"""\t(text "{subtitle}"
\t\t(exclude_from_sim no)
\t\t(at {x1 + 3.81:.4f} {y1 + 9.5:.4f} 0)
\t\t(effects (font (size 1.27 1.27) italic) (justify left bottom))
\t\t(uuid "{t2_uuid}")
\t)""")

    def record_net(self, net_name: str, node: str, net_type: str = "signal"):
        if net_name not in self.manifest_nets:
            self.manifest_nets[net_name] = {"type": net_type, "nodes": []}
        if node not in self.manifest_nets[net_name]["nodes"]:
            self.manifest_nets[net_name]["nodes"].append(node)

    def build(self) -> str:
        root_uuid = gen_uuid()
        lib_syms_str = "\n".join(self.lib_symbols.values())
        elements_str = "\n".join(self.elements)
        wires_str = "\n".join(self.wires)
        labels_str = "\n".join(self.labels)
        no_connects_str = "\n".join(self.no_connects)
        junctions_str = "\n".join(self.junctions)
        annotations_str = "\n".join(self.annotations)

        return f"""(kicad_sch
\t(version 20250114)
\t(generator "fv_ir_rx_generator")
\t(generator_version "10.0")
\t(uuid "{root_uuid}")
\t(paper "A4")
\t(title_block
\t\t(title "{self.title}")
\t\t(date "2026-10-16")
\t\t(rev "{self.rev}")
\t\t(company "FV Project")
\t\t(comment 1 "{self.subtitle}")
\t\t(comment 2 "2-layer THT | 3-wire JST-XH cable interface to FV-CTRL Mainboard")
\t)
\t(lib_symbols
{lib_syms_str}
\t)
{annotations_str}
{elements_str}
{wires_str}
{labels_str}
{no_connects_str}
{junctions_str}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
)
"""


def generate_satellite_schematic(title: str, subtitle: str, signal_name: str = "IR_RX",
                                 target_file: Path = HARDWARE / "FV-IR-RX_RevA.kicad_sch"):
    sb = IrRxSchBuilder(title=title, subtitle=subtitle)

    # 1. Embed Required Symbols from KiCad Standard Libraries
    sb.add_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x03", "Connector_Generic:Conn_01x03")
    sb.add_lib_symbol("Device.kicad_sym", "R", "Device:R")
    sb.add_lib_symbol("Device.kicad_sym", "C_Polarized", "Device:C_Polarized")
    sb.add_lib_symbol("Interface_Optical.kicad_sym", "TSOP581xx", "Interface_Optical:TSOP581xx")
    sb.add_power_sym("power:GND", 45.72, 147.32, 0)
    sb.add_lib_symbol("power.kicad_sym", "GND", "power:GND")
    sb.add_lib_symbol("power.kicad_sym", "+3V3", "power:+3V3")
    sb.add_lib_symbol("power.kicad_sym", "PWR_FLAG", "power:PWR_FLAG")

    # Decorative functional bounding box
    sb.add_box(30.48, 30.48, 260.0, 165.0,
               f"{title.upper()}",
               "TSOP38238 / VS1838B (38kHz) Receiver with RC Decoupling Filter (100R + 4.7uF)")

    # -------------------------------------------------------------------------
    # COMPONENT PLACEMENT
    # -------------------------------------------------------------------------
    # J1: JST-XH 3-pin connector at (60.96, 76.2)
    # Pin 1: +3.3V (VCC from mainboard)
    # Pin 2: IR_RX (Demodulated active-low output to mainboard)
    # Pin 3: GND (Common ground)
    sb.add_symbol("Connector_Generic:Conn_01x03", "J1", "JST_XH_3P", 60.96, 76.2,
                  pins_count=3, footprint="Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical",
                  desc="3-wire interface to mainboard (1:+3V3, 2:OUT, 3:GND)", mpn="JST B3B-XH-A")

    p_J1_1 = get_pin_pos("Connector_Generic:Conn_01x03", 1, 60.96, 76.2) # (55.88, 73.66)
    p_J1_2 = get_pin_pos("Connector_Generic:Conn_01x03", 2, 60.96, 76.2) # (55.88, 76.20)
    p_J1_3 = get_pin_pos("Connector_Generic:Conn_01x03", 3, 60.96, 76.2) # (55.88, 78.74)

    # R1: 100R Decoupling Resistor (horizontal, rot=90) at (106.68, 60.96)
    # Pin 1: (102.87, 60.96), Pin 2: (110.49, 60.96)
    sb.add_symbol("Device:R", "R1", "100R", 106.68, 60.96, rot=90,
                  pins_count=2, footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
                  desc="100 Ohm 1/4W RC power filter resistor", mpn="CF1/4W-100R")
    p_R1_1 = get_pin_pos("Device:R", 1, 106.68, 60.96, rot=90)
    p_R1_2 = get_pin_pos("Device:R", 2, 106.68, 60.96, rot=90)

    # C1: 4.7uF Polarized Decoupling Capacitor (vertical, rot=0) at (142.24, 86.36)
    # Pin 1 (+): (142.24, 82.55), Pin 2 (-): (142.24, 90.17)
    sb.add_symbol("Device:C_Polarized", "C1", "4.7uF", 142.24, 86.36, rot=0,
                  pins_count=2, footprint="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",
                  desc="4.7uF 16V electrolytic RC filter capacitor", mpn="Radial-4.7uF-16V")
    p_C1_1 = get_pin_pos("Device:C_Polarized", 1, 142.24, 86.36, rot=0)
    p_C1_2 = get_pin_pos("Device:C_Polarized", 2, 142.24, 86.36, rot=0)

    # U1: TSOP581xx (TSOP38238 / VS1838B compatible) IR Receiver module at (190.5, 96.52)
    # Pin 1 (OUT): (200.66, 96.52)
    # Pin 2 (GND): (200.66, 101.60)
    # Pin 3 (Vs):  (200.66, 91.44)
    sb.add_symbol("Interface_Optical:TSOP581xx", "U1", "TSOP38238 / VS1838B", 190.5, 96.52, rot=0,
                  pins_count=3, footprint="OptoDevice:Vishay_MINICAST-3Pin",
                  desc="38kHz IR Receiver Module (TSOP38238 or VS1838B)", mpn="TSOP38238 / VS1838B")
    p_U1_1 = get_pin_pos("Interface_Optical:TSOP581xx", 1, 190.5, 96.52, rot=0)
    p_U1_2 = get_pin_pos("Interface_Optical:TSOP581xx", 2, 190.5, 96.52, rot=0)
    p_U1_3 = get_pin_pos("Interface_Optical:TSOP581xx", 3, 190.5, 96.52, rot=0)

    # -------------------------------------------------------------------------
    # WIRING & NETS
    # -------------------------------------------------------------------------

    # 1. NET: +3V3_IN (Incoming power from mainboard via J1.1)
    sb.add_wire(p_J1_1[0], p_J1_1[1], 45.72, p_J1_1[1])
    sb.add_wire(45.72, p_J1_1[1], 45.72, 60.96)
    sb.add_wire(45.72, 60.96, p_R1_1[0], p_R1_1[1])
    sb.add_power_sym("power:+3V3", 45.72, 60.96, 0)
    sb.add_power_sym("power:PWR_FLAG", 40.64, 60.96, 0)
    sb.add_wire(40.64, 60.96, 45.72, 60.96)
    sb.add_junction(45.72, 60.96)
    sb.record_net("+3V3_IN", "J1.1", "power")
    sb.record_net("+3V3_IN", "R1.1", "power")

    # 2. NET: +3V3_FILT (Filtered power rail from R1.2 -> C1.1 -> U1.3)
    sb.add_wire(p_R1_2[0], p_R1_2[1], 142.24, 60.96)
    sb.add_wire(142.24, 60.96, p_C1_1[0], p_C1_1[1]) # connects to C1 pin 1
    sb.add_junction(142.24, 60.96)

    # Run wire from filtered rail to U1 pin 3 (Vs at y=91.44)
    sb.add_wire(142.24, 60.96, 218.44, 60.96)
    sb.add_wire(218.44, 60.96, 218.44, p_U1_3[1])
    sb.add_wire(218.44, p_U1_3[1], p_U1_3[0], p_U1_3[1])
    sb.add_label("+3V3_FILT", 147.32, 60.96)
    # Add PWR_FLAG for +3V3_FILT so KiCad ERC verifies that passive filter feeds power_in pin
    sb.add_power_sym("power:PWR_FLAG", 157.48, 55.88, 0)
    sb.add_wire(157.48, 55.88, 157.48, 60.96)
    sb.add_junction(157.48, 60.96)
    sb.record_net("+3V3_FILT", "R1.2", "power")
    sb.record_net("+3V3_FILT", "C1.1", "power")
    sb.record_net("+3V3_FILT", "U1.3", "power")

    # 3. NET: IR_OUT (Active-low output from U1 pin 1 -> J1 pin 2)
    sb.add_wire(p_U1_1[0], p_U1_1[1], 213.36, p_U1_1[1])
    sb.add_wire(213.36, p_U1_1[1], 213.36, 127.0)
    sb.add_wire(213.36, 127.0, 50.8, 127.0)
    sb.add_wire(50.8, 127.0, 50.8, p_J1_2[1])
    sb.add_wire(50.8, p_J1_2[1], p_J1_2[0], p_J1_2[1])
    sb.add_label(signal_name, 114.3, 127.0)
    sb.record_net(signal_name, "U1.1", "signal")
    sb.record_net(signal_name, "J1.2", "signal")

    # 4. NET: GND (Ground return via J1 pin 3, C1 pin 2, U1 pin 2)
    sb.add_wire(p_J1_3[0], p_J1_3[1], 45.72, p_J1_3[1])
    sb.add_wire(45.72, p_J1_3[1], 45.72, 147.32)
    sb.add_wire(45.72, 147.32, 223.52, 147.32)
    sb.add_power_sym("power:GND", 45.72, 147.32, 0)
    sb.add_power_sym("power:PWR_FLAG", 38.1, 147.32, 0)
    sb.add_wire(38.1, 147.32, 45.72, 147.32)
    sb.add_junction(45.72, 147.32)

    # C1.2 connection to GND bus
    sb.add_wire(p_C1_2[0], p_C1_2[1], 142.24, 147.32)
    sb.add_junction(142.24, 147.32)

    # U1.2 connection to GND bus
    sb.add_wire(p_U1_2[0], p_U1_2[1], 223.52, p_U1_2[1])
    sb.add_wire(223.52, p_U1_2[1], 223.52, 147.32)
    sb.record_net("GND", "J1.3", "power")
    sb.record_net("GND", "C1.2", "power")
    sb.record_net("GND", "U1.2", "power")

    # Write file
    target_file.parent.mkdir(parents=True, exist_ok=True)
    content = sb.build()
    target_file.write_text(content, encoding="utf-8")
    print(f"Generated IR RX schematic: {target_file}")

    manifest = {
        "title": title,
        "components": sb.manifest_parts,
        "nets": sb.manifest_nets
    }
    manifest_path = target_file.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated IR RX manifest: {manifest_path}")

    return target_file, manifest_path


def generate_all_rx():
    # 1. Canonical Satellite Board (Used for both Column 1 and Column 2 production)
    gen_sch, _ = generate_satellite_schematic(
        title="FV-IR-RX Rev A (Satellite IR Receiver Board)",
        subtitle="Universal 38kHz IR Receiver Board for Fruit Vending Cup Detection",
        signal_name="IR_RX_OUT",
        target_file=HARDWARE / "FV-IR-RX_RevA.kicad_sch"
    )

    # 2. Column 1 Satellite Board Variant
    generate_satellite_schematic(
        title="FV-IR-RX1 Rev A (Column 1 Satellite IR Receiver)",
        subtitle="Column 1 38kHz IR Receiver Board (Cables to Mainboard J9)",
        signal_name="IR_RX1",
        target_file=HARDWARE / "FV-IR-RX1_RevA.kicad_sch"
    )

    # 3. Column 2 Satellite Board Variant
    generate_satellite_schematic(
        title="FV-IR-RX2 Rev A (Column 2 Satellite IR Receiver)",
        subtitle="Column 2 38kHz IR Receiver Board (Cables to Mainboard J10)",
        signal_name="IR_RX2",
        target_file=HARDWARE / "FV-IR-RX2_RevA.kicad_sch"
    )

    # Run KiCad ERC check on all three
    for sch in [HARDWARE / "FV-IR-RX_RevA.kicad_sch",
                HARDWARE / "FV-IR-RX1_RevA.kicad_sch",
                HARDWARE / "FV-IR-RX2_RevA.kicad_sch"]:
        rpt = REPORTS / f"erc_{sch.stem}.rpt"
        cmd = [
            "kicad-cli", "sch", "erc",
            "--severity-all",
            "--format", "report",
            "--output", str(rpt),
            str(sch)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"ERC failed for {sch.name}:\n{res.stdout}\n{res.stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"ERC PASS for {sch.name} -> {rpt}")


if __name__ == "__main__":
    generate_all_rx()
