"""Native KiCad 10 Schematic & Manifest Generator for FV-CTRL Rev A.

Generates:
1. hardware/archive/reva/FV-CTRL_RevA.kicad_sch - Native KiCad 10 schematic with 100% verified pin alignments
2. hardware/archive/reva/FV-CTRL_RevA.manifest.json - Component & net manifest
3. hardware/archive/reva/FV-CTRL_RevA.net.json - Backward-compatible netlist for validators
4. docs/archive/reva/FV-CTRL_RevA-bom-draft.md - Draft BOM with MPNs and notes
"""
import json
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / "hardware/archive/reva"
DOCS = ROOT / "docs/archive/reva"
OUT_SCH = HARDWARE / "FV-CTRL_RevA.kicad_sch"
OUT_MANIFEST = HARDWARE / "FV-CTRL_RevA.manifest.json"
OUT_NETLIST = HARDWARE / "FV-CTRL_RevA.net.json"
OUT_BOM = DOCS / "FV-CTRL_RevA-bom-draft.md"

KICAD_SYM_DIR = Path("C:/Program Files/KiCad/10.0/share/kicad/symbols")


def gen_uuid():
    return str(uuid.uuid4())


def get_lib_symbol(lib_file: str, sym_name: str, target_lib_id: str) -> str:
    path = KICAD_SYM_DIR / lib_file
    if not path.exists():
        raise FileNotFoundError(f"KiCad symbol library not found at: {path}")
    content = path.read_text(encoding="utf-8", errors="ignore")
    pattern = rf'(\n  \(symbol "{re.escape(sym_name)}"[\s\S]*?\n  \))'
    m = re.search(pattern, content)
    if not m:
        pattern = rf'(\t\(symbol "{re.escape(sym_name)}"[\s\S]*?\n\t\))'
        m = re.search(pattern, content)
    if not m:
        raise ValueError(f"Symbol '{sym_name}' not found in {lib_file}")
    body = m.group(0).strip()
    short_target = target_lib_id.split(":")[-1]
    body = re.sub(rf'^\(symbol "{re.escape(sym_name)}"', f'(symbol "{target_lib_id}"', body, count=1)
    body = re.sub(rf'\(symbol "{re.escape(sym_name)}(_[0-9]+_[0-9]+)"', rf'(symbol "{short_target}\1"', body)
    return "\t\t" + body.replace("\n", "\n\t\t")


# Extract exact pin definitions for symbols from KiCad libraries
def extract_symbol_pins(lib_file: str, sym_name: str):
    path = KICAD_SYM_DIR / lib_file
    content = path.read_text(encoding="utf-8", errors="ignore")
    pattern = rf'(\n  \(symbol "{re.escape(sym_name)}"[\s\S]*?\n  \))'
    m = re.search(pattern, content)
    if not m:
        pattern = rf'(\t\(symbol "{re.escape(sym_name)}"[\s\S]*?\n\t\))'
        m = re.search(pattern, content)
    if not m:
        raise ValueError(f"Symbol {sym_name} not found in {lib_file}")
    body = m.group(0)

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
    "Device:C": extract_symbol_pins("Device.kicad_sym", "C"),
    "Device:C_Polarized": extract_symbol_pins("Device.kicad_sym", "C_Polarized"),
    "Device:Fuse": extract_symbol_pins("Device.kicad_sym", "Fuse"),
    "Device:Polyfuse": extract_symbol_pins("Device.kicad_sym", "Polyfuse"),
    "Device:D_TVS": extract_symbol_pins("Device.kicad_sym", "D_TVS"),
    "Device:LED": extract_symbol_pins("Device.kicad_sym", "LED"),
    "Device:Q_PMOS": extract_symbol_pins("Device.kicad_sym", "Q_PMOS"),
    "Device:Q_NPN": extract_symbol_pins("Device.kicad_sym", "Q_NPN"),
    "Connector_Generic:Conn_01x02": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x02"),
    "Connector_Generic:Conn_01x03": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x03"),
    "Connector_Generic:Conn_01x04": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x04"),
    "Connector_Generic:Conn_01x06": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x06"),
    "Connector_Generic:Conn_01x08": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x08"),
    "Connector_Generic:Conn_01x19": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x19"),
    "Connector:TestPoint": extract_symbol_pins("Connector.kicad_sym", "TestPoint"),
    "Switch:SW_Push": extract_symbol_pins("Switch.kicad_sym", "SW_Push"),
    "Regulator_Linear:AP1117-15": extract_symbol_pins("Regulator_Linear.kicad_sym", "AP1117-15"),
    "RF_Module:ESP32-WROOM-32": extract_symbol_pins("RF_Module.kicad_sym", "ESP32-WROOM-32"),
    "power:GND": extract_symbol_pins("power.kicad_sym", "GND"),
    "power:+12V": extract_symbol_pins("power.kicad_sym", "+12V"),
    "power:+5V": extract_symbol_pins("power.kicad_sym", "+5V"),
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


FOOTPRINT_MAP = {
    # Block 1: 12V Input & Protection
    "J1": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
    "F1": "Fuse:Fuseholder_Clip-5x20mm_Littelfuse_111_Inline_P20.00x5.00mm_D1.05mm_Horizontal",
    "Q1": "Package_TO_SOT_THT:TO-220-3_Vertical",
    "R9": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "D1": "Diode_THT:D_DO-201_P12.70mm_Horizontal",

    # Block 2: Buck Converters (XH-M401 8A Servo Buck, Aux Buck DNP, MP1584EN 5V Logic)
    "J2": "fv_modules:Converter_DCDC_XH-M401_8A",
    "J3": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    "J4": "fv_modules:Converter_DCDC_MP1584EN",

    # Block 3: Servo Protection & Headers
    "F2": "Fuse:Fuse_Bourns_MF-RG300",
    "F3": "Fuse:Fuse_Bourns_MF-RG300",
    "C1": "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm",
    "C3": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "C2": "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm",
    "C4": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "J5": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
    "J6": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
    "J7": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
    "J8": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",

    # Block 4: ESP32-WROOM-32 SMD MCU, 3.3V LDO, Programming & Expansion
    "U2": "RF_Module:ESP32-WROOM-32",
    "U3": "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
    "C11": "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",
    "C12": "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",
    "C13": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "C14": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "R10": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R11": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "SW1": "Button_Switch_THT:SW_PUSH_6mm_H5mm",
    "SW2": "Button_Switch_THT:SW_PUSH_6mm_H5mm",
    "J20": "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical",
    "J21": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    "J22": "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
    "R1": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R2": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R3": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R4": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R5": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R6": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R7": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R8": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",

    # Block 5: IR TX Driver
    "Q2": "Package_TO_SOT_THT:TO-92_Inline",
    "R13": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R14": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R15": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "J11": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    "J12": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",

    # Block 6: IR RX Headers
    "J9": "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical",
    "J10": "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical",

    # Block 7: Limit Switches (Optional DNP)
    "J13": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    "J14": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    "J15": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    "J16": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    "R16": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R17": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R18": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R19": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "C7": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "C8": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "C9": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "C10": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",

    # Block 8: Diagnostics & Rail Decoupling
    "D2": "LED_THT:LED_D3.0mm",
    "D3": "LED_THT:LED_D3.0mm",
    "D4": "LED_THT:LED_D3.0mm",
    "D5": "LED_THT:LED_D3.0mm",
    "D6": "LED_THT:LED_D3.0mm",
    "R20": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R21": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R22": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R23": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "R24": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "TP1": "TestPoint:TestPoint_Pad_D2.0mm",
    "TP2": "TestPoint:TestPoint_Pad_D2.0mm",
    "TP3": "TestPoint:TestPoint_Pad_D2.0mm",
    "TP4": "TestPoint:TestPoint_Pad_D2.0mm",
    "TP5": "TestPoint:TestPoint_Pad_D2.0mm",
    "TP6": "TestPoint:TestPoint_Pad_D2.0mm",
    "TP7": "TestPoint:TestPoint_Pad_D2.0mm",
    "TP8": "TestPoint:TestPoint_Pad_D2.0mm",
    "C5": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "C6": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "J17": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
}


class SchBuilder:
    def __init__(self):
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
        if not footprint and ref in FOOTPRINT_MAP:
            footprint = FOOTPRINT_MAP[ref]
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
        ref_id = f"#PWR{len(self.elements)+1000}"
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

    def add_no_connect(self, x: float, y: float):
        nc_uuid = gen_uuid()
        s = f"""\t(no_connect
\t\t(at {x:.4f} {y:.4f})
\t\t(uuid "{nc_uuid}")
\t)"""
        self.no_connects.append(s)

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
	(version 20250114)
	(generator "fv_native_generator")
	(generator_version "10.0")
	(uuid "{root_uuid}")
	(paper "A3")
	(title_block
		(title "FV-CTRL Rev A (Fruit Vending Controller)")
		(date "2026-10-16")
		(rev "Rev A (Engineering Draft)")
		(company "FV Project")
		(comment 1 "Code-generated native KiCad 10 schematic")
		(comment 2 "2-layer THT | Dual-column FIFO servo & IR control")
	)
	(lib_symbols
{lib_syms_str}
	)
{annotations_str}
{elements_str}
{wires_str}
{labels_str}
{no_connects_str}
{junctions_str}
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
)
"""


def generate_all():
    sb = SchBuilder()

    # Register KiCad standard library symbols
    sb.add_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x02", "Connector_Generic:Conn_01x02")
    sb.add_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x03", "Connector_Generic:Conn_01x03")
    sb.add_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x04", "Connector_Generic:Conn_01x04")
    sb.add_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x06", "Connector_Generic:Conn_01x06")
    sb.add_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x08", "Connector_Generic:Conn_01x08")
    sb.add_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x19", "Connector_Generic:Conn_01x19")
    sb.add_lib_symbol("Connector.kicad_sym", "TestPoint", "Connector:TestPoint")
    sb.add_lib_symbol("Switch.kicad_sym", "SW_Push", "Switch:SW_Push")
    sb.add_lib_symbol("Regulator_Linear.kicad_sym", "AP1117-15", "Regulator_Linear:AP1117-15")
    sb.add_lib_symbol("RF_Module.kicad_sym", "ESP32-WROOM-32", "RF_Module:ESP32-WROOM-32")
    sb.add_lib_symbol("Device.kicad_sym", "R", "Device:R")
    sb.add_lib_symbol("Device.kicad_sym", "C", "Device:C")
    sb.add_lib_symbol("Device.kicad_sym", "C_Polarized", "Device:C_Polarized")
    sb.add_lib_symbol("Device.kicad_sym", "Fuse", "Device:Fuse")
    sb.add_lib_symbol("Device.kicad_sym", "Polyfuse", "Device:Polyfuse")
    sb.add_lib_symbol("Device.kicad_sym", "D_TVS", "Device:D_TVS")
    sb.add_lib_symbol("Device.kicad_sym", "LED", "Device:LED")
    sb.add_lib_symbol("Device.kicad_sym", "Q_PMOS", "Device:Q_PMOS")
    sb.add_lib_symbol("Device.kicad_sym", "Q_NPN", "Device:Q_NPN")
    sb.add_lib_symbol("power.kicad_sym", "GND", "power:GND")
    sb.add_lib_symbol("power.kicad_sym", "+12V", "power:+12V")
    sb.add_lib_symbol("power.kicad_sym", "+5V", "power:+5V")
    sb.add_lib_symbol("power.kicad_sym", "+3V3", "power:+3V3")
    sb.add_lib_symbol("power.kicad_sym", "PWR_FLAG", "power:PWR_FLAG")

    # =========================================================================
    # BLOCK 1: 12V INPUT & PROTECTION
    # =========================================================================
    sb.add_box(20.32, 17.78, 124.46, 76.2,
               "1. POWER INPUT & 12V PROTECTION",
               "Pluggable screw terminal | 5A cartridge fuse | Reverse polarity P-MOS | 12V TVS")

    # J1: 12V_IN Terminal at (35.56, 38.1)
    sb.add_symbol("Connector_Generic:Conn_01x02", "J1", "12V_IN", 35.56, 38.1,
                  pins_count=2, footprint="",
                  desc="12V DC input pluggable screw terminal", mpn="Pluggable 2-pin 5.0mm")
    p_J1_1 = get_pin_pos("Connector_Generic:Conn_01x02", 1, 35.56, 38.1)
    p_J1_2 = get_pin_pos("Connector_Generic:Conn_01x02", 2, 35.56, 38.1)

    # J1 Pin 1 (+12V_IN) -> F1 Pin 1
    sb.add_wire(p_J1_1[0], p_J1_1[1], 25.4, p_J1_1[1])
    sb.add_wire(25.4, p_J1_1[1], 25.4, 30.48)
    sb.add_wire(25.4, 30.48, 50.8, 30.48)
    sb.add_label("+12V_IN", 25.4, p_J1_1[1])
    sb.record_net("+12V_IN", "J1.1", "power")

    # J1 Pin 2 (GND)
    sb.add_wire(p_J1_2[0], p_J1_2[1], 25.4, p_J1_2[1])
    sb.add_power_sym("power:GND", 25.4, p_J1_2[1], 0)
    sb.record_net("GND", "J1.2", "power")

    # PWR_FLAG on GND
    sb.add_wire(25.4, p_J1_2[1], 25.4, p_J1_2[1] + 5.08)
    sb.add_power_sym("power:PWR_FLAG", 25.4, p_J1_2[1] + 5.08, 0)

    # F1: 5A Fuse at (50.8, 38.1)
    sb.add_symbol("Device:Fuse", "F1", "5A 250V", 50.8, 38.1,
                  pins_count=2, footprint="",
                  desc="5A replaceable cartridge fuse in THT socket", mpn="5x20mm 5A cartridge")
    p_F1_1 = get_pin_pos("Device:Fuse", 1, 50.8, 38.1)
    p_F1_2 = get_pin_pos("Device:Fuse", 2, 50.8, 38.1)

    sb.add_wire(50.8, 30.48, p_F1_1[0], p_F1_1[1])
    sb.record_net("+12V_IN", "F1.1", "power")

    # Q1: P-MOSFET IRF9540N at (68.58, 46.99)
    sb.add_symbol("Device:Q_PMOS", "Q1", "IRF9540N", 68.58, 46.99,
                  footprint="", desc="P-MOSFET reverse polarity protection", mpn="IRF9540NPBF",
                  pin_names=["D", "G", "S"])
    p_Q1_D = get_pin_pos("Device:Q_PMOS", "D", 68.58, 46.99)
    p_Q1_G = get_pin_pos("Device:Q_PMOS", "G", 68.58, 46.99)
    p_Q1_S = get_pin_pos("Device:Q_PMOS", "S", 68.58, 46.99)

    # F1 Pin 2 to Q1 Drain
    sb.add_wire(p_F1_2[0], p_F1_2[1], p_Q1_D[0], p_F1_2[1])
    sb.add_wire(p_Q1_D[0], p_F1_2[1], p_Q1_D[0], p_Q1_D[1])
    sb.add_label("+12V_FUSED", 55.88, p_F1_2[1])
    sb.record_net("+12V_FUSED", "F1.2", "power")
    sb.record_net("+12V_FUSED", "Q1.D", "power")

    # R9: 10k Gate pull-down at (63.5, 60.96)
    sb.add_symbol("Device:R", "R9", "10k", 63.5, 60.96,
                  footprint="", desc="P-MOSFET gate-to-GND pull-down resistor", mpn="10k 1/4W 5%")
    p_R9_1 = get_pin_pos("Device:R", 1, 63.5, 60.96)
    p_R9_2 = get_pin_pos("Device:R", 2, 63.5, 60.96)

    # Q1 Gate to R9 Pin 1
    sb.add_wire(p_Q1_G[0], p_Q1_G[1], p_R9_1[0], p_Q1_G[1])
    sb.add_wire(p_R9_1[0], p_Q1_G[1], p_R9_1[0], p_R9_1[1])
    sb.record_net("NET_Q1_GATE", "Q1.G", "signal")
    sb.record_net("NET_Q1_GATE", "R9.1", "signal")

    # R9 Pin 2 to GND
    sb.add_power_sym("power:GND", p_R9_2[0], p_R9_2[1], 0)
    sb.record_net("GND", "R9.2", "power")

    # Q1 Source to +12V rail bus
    p_rail_12v_y = p_Q1_S[1]
    sb.add_wire(p_Q1_S[0], p_rail_12v_y, 88.9, p_rail_12v_y)
    sb.record_net("+12V", "Q1.S", "power")

    # D1: TVS Diode at (88.9, 60.96), rot 90
    sb.add_symbol("Device:D_TVS", "D1", "1.5KE15CA", 88.9, 60.96, rot=90,
                  footprint="", desc="12V bidirectional TVS overvoltage clamp", mpn="1.5KE15CA")
    p_D1_1 = get_pin_pos("Device:D_TVS", 1, 88.9, 60.96, rot=90)
    p_D1_2 = get_pin_pos("Device:D_TVS", 2, 88.9, 60.96, rot=90)

    sb.add_wire(88.9, p_rail_12v_y, p_D1_1[0], p_D1_1[1])
    sb.add_junction(88.9, p_rail_12v_y)
    sb.record_net("+12V", "D1.1", "power")

    sb.add_power_sym("power:GND", p_D1_2[0], p_D1_2[1], 0)
    sb.record_net("GND", "D1.2", "power")

    # Power rail +12V label & PWR_FLAG
    sb.add_wire(88.9, p_rail_12v_y, 106.68, p_rail_12v_y)
    sb.add_label("+12V", 106.68, p_rail_12v_y)
    sb.add_junction(106.68, p_rail_12v_y)
    sb.add_wire(106.68, p_rail_12v_y, 106.68, p_rail_12v_y - 5.08)
    sb.add_power_sym("power:PWR_FLAG", 106.68, p_rail_12v_y - 5.08, 0)

    # =========================================================================
    # BLOCK 2: BUCK CONVERTER MODULES (EXTERNAL BREAKOUTS)
    # =========================================================================
    sb.add_box(20.32, 83.82, 124.46, 172.72,
               "2. STEP-DOWN BUCK CONVERTERS (BREAKOUT MODULES)",
               "J2: Servo Buck XH-M401 (XL4016E1 8A, Preset 6.0V) | J4: 5V Logic (MP1584EN) | J3: Aux Buck (DNP)")

    bucks = [
        ("J2", "XH-M401 (6.0V 8A)", "+6V_SERVO", 104.14, "XH-M401 (XL4016E1 8A 200W)", False),
        ("J3", "AUX_BUCK (DNP)", "+6V_SERVO", 129.54, "Auxiliary 4-pin Header", True),
        ("J4", "MP1584EN (5V Logic)", "+5V", 154.94, "MP1584EN Mini 3A Buck", False),
    ]

    for j_ref, val, out_rail, y_pos, mpn, dnp in bucks:
        sb.add_symbol("Connector_Generic:Conn_01x04", j_ref, val, 45.72, y_pos,
                      pins_count=4, desc=f"{val} header (IN+, IN-, OUT+, OUT-)",
                      mpn=mpn, dnp=dnp)
        p1 = get_pin_pos("Connector_Generic:Conn_01x04", 1, 45.72, y_pos)
        p2 = get_pin_pos("Connector_Generic:Conn_01x04", 2, 45.72, y_pos)
        p3 = get_pin_pos("Connector_Generic:Conn_01x04", 3, 45.72, y_pos)
        p4 = get_pin_pos("Connector_Generic:Conn_01x04", 4, 45.72, y_pos)

        # Pin 1: +12V
        sb.add_wire(p1[0], p1[1], 33.02, p1[1])
        sb.add_label("+12V", 33.02, p1[1])
        sb.record_net("+12V", f"{j_ref}.1", "power")

        # Pin 2: GND
        sb.add_wire(p2[0], p2[1], 33.02, p2[1])
        sb.add_power_sym("power:GND", 33.02, p2[1], 0)
        sb.record_net("GND", f"{j_ref}.2", "power")

        # Pin 3: Output rail
        sb.add_wire(p3[0], p3[1], 60.96, p3[1])
        sb.add_label(out_rail, 60.96, p3[1])
        sb.record_net(out_rail, f"{j_ref}.3", "power")

        # If 5V buck or main servo buck, place PWR_FLAG
        if (out_rail == "+5V") or (out_rail == "+6V_SERVO" and not dnp):
            sb.add_junction(60.96, p3[1])
            sb.add_wire(60.96, p3[1], 60.96, p3[1] - 5.08)
            sb.add_power_sym("power:PWR_FLAG", 60.96, p3[1] - 5.08, 0)

        # Pin 4: GND
        sb.add_wire(p4[0], p4[1], 33.02, p4[1])
        sb.add_power_sym("power:GND", 33.02, p4[1], 0)
        sb.record_net("GND", f"{j_ref}.4", "power")

    # =========================================================================
    # BLOCK 3: SERVO POWER PROTECTION & CONNECTORS (COLUMNS 1 & 2)
    # =========================================================================
    sb.add_box(132.08, 17.78, 274.32, 109.22,
               "3. SERVO POWER PROTECTION & CONNECTORS",
               "Rail A (Col 1) & Rail B (Col 2): PTC fuse | 1000-2200uF bulk cap | 100nF | MG996R 360 Headers")

    # --- RAIL A ---
    sb.add_symbol("Device:Polyfuse", "F2", "PTC 3A", 152.4, 40.64,
                  pins_count=2, footprint="", desc="Resettable PTC fuse for Servo Rail A (~3A hold)",
                  mpn="Bourns MF-R300")
    p_F2_1 = get_pin_pos("Device:Polyfuse", 1, 152.4, 40.64)
    p_F2_2 = get_pin_pos("Device:Polyfuse", 2, 152.4, 40.64)

    sb.add_wire(p_F2_1[0], p_F2_1[1], 142.24, p_F2_1[1])
    sb.add_label("+6V_SERVO", 142.24, p_F2_1[1])
    sb.record_net("+6V_SERVO", "F2.1", "power")

    rail_a_y = p_F2_2[1]

    # C1: Bulk Electrolytic at (172.72, 53.34)
    sb.add_symbol("Device:C_Polarized", "C1", "1000-2200uF 16V", 172.72, 53.34,
                  pins_count=2, footprint="", desc="Bulk servo filter capacitor (Rail A)", mpn="1000uF 16V Radial")
    p_C1_1 = get_pin_pos("Device:C_Polarized", 1, 172.72, 53.34)
    p_C1_2 = get_pin_pos("Device:C_Polarized", 2, 172.72, 53.34)

    # C3: 100nF Ceramic at (182.88, 53.34)
    sb.add_symbol("Device:C", "C3", "100nF", 182.88, 53.34,
                  pins_count=2, footprint="", desc="High-frequency decoupling (Rail A)", mpn="100nF 50V Ceramic")
    p_C3_1 = get_pin_pos("Device:C", 1, 182.88, 53.34)
    p_C3_2 = get_pin_pos("Device:C", 2, 182.88, 53.34)

    # J5: S1_TOP Servo Header at (213.36, 44.45)
    sb.add_symbol("Connector_Generic:Conn_01x03", "J5", "S1_TOP", 213.36, 44.45,
                  pins_count=3, footprint="", desc="Column 1 Top Servo Header (GND, V+, SIG)", mpn="3-pin Header")
    p_J5_1 = get_pin_pos("Connector_Generic:Conn_01x03", 1, 213.36, 44.45)
    p_J5_2 = get_pin_pos("Connector_Generic:Conn_01x03", 2, 213.36, 44.45)
    p_J5_3 = get_pin_pos("Connector_Generic:Conn_01x03", 3, 213.36, 44.45)

    # J6: S1_BOT Servo Header at (248.92, 44.45)
    sb.add_symbol("Connector_Generic:Conn_01x03", "J6", "S1_BOT", 248.92, 44.45,
                  pins_count=3, footprint="", desc="Column 1 Bottom Servo Header (GND, V+, SIG)", mpn="3-pin Header")
    p_J6_1 = get_pin_pos("Connector_Generic:Conn_01x03", 1, 248.92, 44.45)
    p_J6_2 = get_pin_pos("Connector_Generic:Conn_01x03", 2, 248.92, 44.45)
    p_J6_3 = get_pin_pos("Connector_Generic:Conn_01x03", 3, 248.92, 44.45)

    # Segments for Rail A +6V_A
    sb.add_wire(p_F2_2[0], rail_a_y, p_C1_1[0], rail_a_y)
    sb.add_junction(p_C1_1[0], rail_a_y)
    sb.add_label("+6V_A", 160.02, rail_a_y)
    sb.record_net("+6V_A", "F2.2", "power")

    sb.add_power_sym("power:PWR_FLAG", 157.48, rail_a_y - 5.08, 0)
    sb.add_wire(157.48, rail_a_y - 5.08, 157.48, rail_a_y)
    sb.add_junction(157.48, rail_a_y)

    sb.add_wire(p_C1_1[0], rail_a_y, p_C1_1[0], p_C1_1[1])
    sb.record_net("+6V_A", "C1.1", "power")
    sb.add_power_sym("power:GND", p_C1_2[0], p_C1_2[1], 0)
    sb.record_net("GND", "C1.2", "power")

    sb.add_wire(p_C1_1[0], rail_a_y, p_C3_1[0], rail_a_y)
    sb.add_junction(p_C3_1[0], rail_a_y)
    sb.add_wire(p_C3_1[0], rail_a_y, p_C3_1[0], p_C3_1[1])
    sb.record_net("+6V_A", "C3.1", "power")
    sb.add_power_sym("power:GND", p_C3_2[0], p_C3_2[1], 0)
    sb.record_net("GND", "C3.2", "power")

    sb.add_wire(p_C3_1[0], rail_a_y, p_J5_2[0], rail_a_y)
    sb.add_junction(p_J5_2[0], rail_a_y)
    sb.record_net("+6V_A", "J5.2", "power")

    sb.add_wire(p_J5_2[0], rail_a_y, p_J6_2[0], rail_a_y)
    sb.record_net("+6V_A", "J6.2", "power")

    # J5 & J6 remaining pins
    sb.add_wire(p_J5_1[0], p_J5_1[1], 203.2, p_J5_1[1])
    sb.add_power_sym("power:GND", 203.2, p_J5_1[1], 0)
    sb.record_net("GND", "J5.1", "power")

    sb.add_wire(p_J5_3[0], p_J5_3[1], 198.12, p_J5_3[1])
    sb.add_label("S1_TOP_PWM", 198.12, p_J5_3[1])
    sb.record_net("S1_TOP_PWM", "J5.3", "signal")

    sb.add_wire(p_J6_1[0], p_J6_1[1], 238.76, p_J6_1[1])
    sb.add_power_sym("power:GND", 238.76, p_J6_1[1], 0)
    sb.record_net("GND", "J6.1", "power")

    sb.add_wire(p_J6_3[0], p_J6_3[1], 233.68, p_J6_3[1])
    sb.add_label("S1_BOT_PWM", 233.68, p_J6_3[1])
    sb.record_net("S1_BOT_PWM", "J6.3", "signal")

    # --- RAIL B ---
    sb.add_symbol("Device:Polyfuse", "F3", "PTC 3A", 152.4, 83.82,
                  pins_count=2, footprint="", desc="Resettable PTC fuse for Servo Rail B (~3A hold)",
                  mpn="Bourns MF-R300")
    p_F3_1 = get_pin_pos("Device:Polyfuse", 1, 152.4, 83.82)
    p_F3_2 = get_pin_pos("Device:Polyfuse", 2, 152.4, 83.82)

    sb.add_wire(p_F3_1[0], p_F3_1[1], 142.24, p_F3_1[1])
    sb.add_label("+6V_SERVO", 142.24, p_F3_1[1])
    sb.record_net("+6V_SERVO", "F3.1", "power")

    rail_b_y = p_F3_2[1]

    # C2: Bulk Electrolytic at (172.72, 96.52)
    sb.add_symbol("Device:C_Polarized", "C2", "1000-2200uF 16V", 172.72, 96.52,
                  pins_count=2, footprint="", desc="Bulk servo filter capacitor (Rail B)", mpn="1000uF 16V Radial")
    p_C2_1 = get_pin_pos("Device:C_Polarized", 1, 172.72, 96.52)
    p_C2_2 = get_pin_pos("Device:C_Polarized", 2, 172.72, 96.52)

    # C4: 100nF Ceramic at (182.88, 96.52)
    sb.add_symbol("Device:C", "C4", "100nF", 182.88, 96.52,
                  pins_count=2, footprint="", desc="High-frequency decoupling (Rail B)", mpn="100nF 50V Ceramic")
    p_C4_1 = get_pin_pos("Device:C", 1, 182.88, 96.52)
    p_C4_2 = get_pin_pos("Device:C", 2, 182.88, 96.52)

    # J7: S2_TOP Servo Header at (213.36, 87.63)
    sb.add_symbol("Connector_Generic:Conn_01x03", "J7", "S2_TOP", 213.36, 87.63,
                  pins_count=3, footprint="", desc="Column 2 Top Servo Header (GND, V+, SIG)", mpn="3-pin Header")
    p_J7_1 = get_pin_pos("Connector_Generic:Conn_01x03", 1, 213.36, 87.63)
    p_J7_2 = get_pin_pos("Connector_Generic:Conn_01x03", 2, 213.36, 87.63)
    p_J7_3 = get_pin_pos("Connector_Generic:Conn_01x03", 3, 213.36, 87.63)

    # J8: S2_BOT Servo Header at (248.92, 87.63)
    sb.add_symbol("Connector_Generic:Conn_01x03", "J8", "S2_BOT", 248.92, 87.63,
                  pins_count=3, footprint="", desc="Column 2 Bottom Servo Header (GND, V+, SIG)", mpn="3-pin Header")
    p_J8_1 = get_pin_pos("Connector_Generic:Conn_01x03", 1, 248.92, 87.63)
    p_J8_2 = get_pin_pos("Connector_Generic:Conn_01x03", 2, 248.92, 87.63)
    p_J8_3 = get_pin_pos("Connector_Generic:Conn_01x03", 3, 248.92, 87.63)

    # Segments for Rail B +6V_B
    sb.add_wire(p_F3_2[0], rail_b_y, p_C2_1[0], rail_b_y)
    sb.add_junction(p_C2_1[0], rail_b_y)
    sb.add_label("+6V_B", 160.02, rail_b_y)
    sb.record_net("+6V_B", "F3.2", "power")

    sb.add_power_sym("power:PWR_FLAG", 157.48, rail_b_y - 5.08, 0)
    sb.add_wire(157.48, rail_b_y - 5.08, 157.48, rail_b_y)
    sb.add_junction(157.48, rail_b_y)

    sb.add_wire(p_C2_1[0], rail_b_y, p_C2_1[0], p_C2_1[1])
    sb.record_net("+6V_B", "C2.1", "power")
    sb.add_power_sym("power:GND", p_C2_2[0], p_C2_2[1], 0)
    sb.record_net("GND", "C2.2", "power")

    sb.add_wire(p_C2_1[0], rail_b_y, p_C4_1[0], rail_b_y)
    sb.add_junction(p_C4_1[0], rail_b_y)
    sb.add_wire(p_C4_1[0], rail_b_y, p_C4_1[0], p_C4_1[1])
    sb.record_net("+6V_B", "C4.1", "power")
    sb.add_power_sym("power:GND", p_C4_2[0], p_C4_2[1], 0)
    sb.record_net("GND", "C4.2", "power")

    sb.add_wire(p_C4_1[0], rail_b_y, p_J7_2[0], rail_b_y)
    sb.add_junction(p_J7_2[0], rail_b_y)
    sb.record_net("+6V_B", "J7.2", "power")

    sb.add_wire(p_J7_2[0], rail_b_y, p_J8_2[0], rail_b_y)
    sb.record_net("+6V_B", "J8.2", "power")

    # J7 & J8 remaining pins
    sb.add_wire(p_J7_1[0], p_J7_1[1], 203.2, p_J7_1[1])
    sb.add_power_sym("power:GND", 203.2, p_J7_1[1], 0)
    sb.record_net("GND", "J7.1", "power")

    sb.add_wire(p_J7_3[0], p_J7_3[1], 198.12, p_J7_3[1])
    sb.add_label("S2_TOP_PWM", 198.12, p_J7_3[1])
    sb.record_net("S2_TOP_PWM", "J7.3", "signal")

    sb.add_wire(p_J8_1[0], p_J8_1[1], 238.76, p_J8_1[1])
    sb.add_power_sym("power:GND", 238.76, p_J8_1[1], 0)
    sb.record_net("GND", "J8.1", "power")

    sb.add_wire(p_J8_3[0], p_J8_3[1], 233.68, p_J8_3[1])
    sb.add_label("S2_BOT_PWM", 233.68, p_J8_3[1])
    sb.record_net("S2_BOT_PWM", "J8.3", "signal")

    # =========================================================================
    # BLOCK 4: ESP32-WROOM-32 SMD MCU, 3.3V LDO, RESET, BOOT & SENSOR EXPANSION
    # =========================================================================
    sb.add_box(132.08, 114.3, 274.32, 213.36,
               "4. ESP32-WROOM-32 SMD MCU, 3.3V LDO & EXPANSION",
               "ESP32-WROOM-32 SMD | AMS1117-3.3 LDO | UART0 Flash | ADC & Digital Sensor Headers")

    # 4.1. AMS1117-3.3 LDO Regulator at (152.4, 132.08)
    sb.add_symbol("Regulator_Linear:AP1117-15", "U3", "AMS1117-3.3", 152.4, 132.08,
                  footprint="", desc="3.3V 1A LDO voltage regulator (SOT-223)", mpn="AMS1117-3.3",
                  pin_names=["1", "2", "3"])
    p_u3_1 = get_pin_pos("Regulator_Linear:AP1117-15", 1, 152.4, 132.08)
    p_u3_2 = get_pin_pos("Regulator_Linear:AP1117-15", 2, 152.4, 132.08)
    p_u3_3 = get_pin_pos("Regulator_Linear:AP1117-15", 3, 152.4, 132.08)

    # U3 Pin 3 (VI) -> +5V
    sb.add_wire(p_u3_3[0], p_u3_3[1], 137.16, p_u3_3[1])
    sb.add_label("+5V", 137.16, p_u3_3[1])
    sb.record_net("+5V", "U3.3", "power")

    # U3 Pin 1 (GND) -> GND
    sb.add_power_sym("power:GND", p_u3_1[0], p_u3_1[1], 0)
    sb.record_net("GND", "U3.1", "power")

    # U3 Pin 2 (VO) -> +3V3 & PWR_FLAG
    sb.add_wire(p_u3_2[0], p_u3_2[1], 167.64, p_u3_2[1])
    sb.add_junction(167.64, p_u3_2[1])
    sb.add_label("+3V3", 167.64, p_u3_2[1])
    sb.record_net("+3V3", "U3.2", "power")

    # C11: 10uF 16V input filter at (142.24, 142.24)
    sb.add_symbol("Device:C_Polarized", "C11", "10uF 16V", 142.24, 142.24,
                  pins_count=2, footprint="", desc="LDO input bulk capacitor", mpn="10uF 16V Radial")
    p_c11_1 = get_pin_pos("Device:C_Polarized", 1, 142.24, 142.24)
    p_c11_2 = get_pin_pos("Device:C_Polarized", 2, 142.24, 142.24)
    sb.add_wire(137.16, p_u3_3[1], 142.24, p_u3_3[1])
    sb.add_junction(142.24, p_u3_3[1])
    sb.add_wire(142.24, p_u3_3[1], p_c11_1[0], p_c11_1[1])
    sb.record_net("+5V", "C11.1", "power")
    sb.add_power_sym("power:GND", p_c11_2[0], p_c11_2[1], 0)
    sb.record_net("GND", "C11.2", "power")

    # C12: 22uF 16V output filter at (162.56, 142.24)
    sb.add_symbol("Device:C_Polarized", "C12", "22uF 16V", 162.56, 142.24,
                  pins_count=2, footprint="", desc="LDO output bulk capacitor", mpn="22uF 16V Radial")
    p_c12_1 = get_pin_pos("Device:C_Polarized", 1, 162.56, 142.24)
    p_c12_2 = get_pin_pos("Device:C_Polarized", 2, 162.56, 142.24)
    sb.add_wire(167.64, p_u3_2[1], 162.56, p_u3_2[1])
    sb.add_junction(162.56, p_u3_2[1])
    sb.add_wire(162.56, p_u3_2[1], p_c12_1[0], p_c12_1[1])
    sb.record_net("+3V3", "C12.1", "power")
    sb.add_power_sym("power:GND", p_c12_2[0], p_c12_2[1], 0)
    sb.record_net("GND", "C12.2", "power")

    # C13: 100nF high-frequency ceramic at (172.72, 142.24)
    sb.add_symbol("Device:C", "C13", "100nF", 172.72, 142.24,
                  pins_count=2, footprint="", desc="LDO output high-freq decoupling", mpn="100nF 50V Ceramic")
    p_c13_1 = get_pin_pos("Device:C", 1, 172.72, 142.24)
    p_c13_2 = get_pin_pos("Device:C", 2, 172.72, 142.24)
    sb.add_wire(167.64, p_u3_2[1], 172.72, p_u3_2[1])
    sb.add_junction(172.72, p_u3_2[1])
    sb.add_wire(172.72, p_u3_2[1], p_c13_1[0], p_c13_1[1])
    sb.record_net("+3V3", "C13.1", "power")
    sb.add_power_sym("power:GND", p_c13_2[0], p_c13_2[1], 0)
    sb.record_net("GND", "C13.2", "power")

    # 4.2. ESP32-WROOM-32 SMD MCU at (195.58, 165.1)
    sb.add_symbol("RF_Module:ESP32-WROOM-32", "U2", "ESP32-WROOM-32", 195.58, 165.1,
                  pins_count=39, footprint="",
                  desc="ESP32-WROOM-32 SMD Wi-Fi/BT module", mpn="ESP32-WROOM-32E")

    p_u2 = {i: get_pin_pos("RF_Module:ESP32-WROOM-32", i, 195.58, 165.1) for i in range(1, 40)}

    # Power Pins
    sb.add_wire(p_u2[2][0], p_u2[2][1], p_u2[2][0], p_u2[2][1] - 5.08)
    sb.add_label("+3V3", p_u2[2][0], p_u2[2][1] - 5.08)
    sb.record_net("+3V3", "U2.2", "power")

    sb.add_power_sym("power:GND", p_u2[1][0], p_u2[1][1], 0)
    sb.record_net("GND", "U2.1", "power")
    sb.record_net("GND", "U2.15", "power")
    sb.record_net("GND", "U2.38", "power")
    sb.record_net("GND", "U2.39", "power")

    # Left Side Pins
    sb.add_wire(p_u2[3][0], p_u2[3][1], 175.26, p_u2[3][1])
    sb.add_label("ESP_EN", 175.26, p_u2[3][1])
    sb.record_net("ESP_EN", "U2.3", "signal")

    sb.add_wire(p_u2[4][0], p_u2[4][1], 175.26, p_u2[4][1])
    sb.add_label("ADC_VP", 175.26, p_u2[4][1])
    sb.record_net("ADC_VP", "U2.4", "signal")

    sb.add_wire(p_u2[5][0], p_u2[5][1], 175.26, p_u2[5][1])
    sb.add_label("ADC_VN", 175.26, p_u2[5][1])
    sb.record_net("ADC_VN", "U2.5", "signal")

    for p_idx in [17, 18, 19, 20, 21, 22, 32]:
        sb.add_no_connect(p_u2[p_idx][0], p_u2[p_idx][1])

    # Right Side Pins
    esp_right_signals = {
        25: ("ESP_IO0", "signal"),
        35: ("ESP_TXD0", "signal"),
        34: ("ESP_RXD0", "signal"),
        24: ("EXP_IO2", "signal"),
        26: ("EXP_IO4", "signal"),
        29: ("EXP_IO5", "signal"),
        16: ("EXP_IO13", "signal"),
        13: ("EXP_IO14", "signal"),
        27: ("ESP_S1_TOP_PWM", "signal"),
        28: ("ESP_S1_BOT_PWM", "signal"),
        30: ("ESP_S2_TOP_PWM", "signal"),
        31: ("ESP_S2_BOT_PWM", "signal"),
        33: ("I2C_SDA", "signal"),
        36: ("I2C_SCL", "signal"),
        37: ("ESP_IR_TX", "signal"),
        10: ("LS1", "signal"),
        11: ("LS2", "signal"),
        12: ("LS3", "signal"),
        8:  ("LS4", "signal"),
        9:  ("SPARE_GPIO33", "signal"),
        6:  ("IR_RX1", "signal"),
        7:  ("IR_RX2", "signal"),
    }

    sb.add_no_connect(p_u2[14][0], p_u2[14][1])
    sb.add_no_connect(p_u2[23][0], p_u2[23][1])

    for p_num, (sig_name, sig_type) in esp_right_signals.items():
        pt = p_u2[p_num]
        sb.add_wire(pt[0], pt[1], 218.44, pt[1])
        sb.add_label(sig_name, 218.44, pt[1])
        sb.record_net(sig_name, f"U2.{p_num}", sig_type)

    # 4.3. Reset Circuit (SW1, R10, C14) at (144.78, 157.48)
    sb.add_symbol("Device:R", "R10", "10k", 144.78, 157.48, rot=90,
                  footprint="", desc="EN pull-up resistor", mpn="10k 1/4W 5%")
    p_r10_1 = get_pin_pos("Device:R", 1, 144.78, 157.48, rot=90)
    p_r10_2 = get_pin_pos("Device:R", 2, 144.78, 157.48, rot=90)
    sb.add_wire(137.16, 157.48, p_r10_1[0], p_r10_1[1])
    sb.add_label("+3V3", 137.16, 157.48)
    sb.record_net("+3V3", "R10.1", "power")

    sb.add_wire(p_r10_2[0], 157.48, 154.94, 157.48)
    sb.add_junction(154.94, 157.48)
    sb.add_label("ESP_EN", 154.94, 157.48)
    sb.record_net("ESP_EN", "R10.2", "signal")

    sb.add_symbol("Device:C", "C14", "100nF", 154.94, 167.64,
                  pins_count=2, footprint="", desc="EN delay filter capacitor", mpn="100nF 50V Ceramic")
    p_c14_1 = get_pin_pos("Device:C", 1, 154.94, 167.64)
    p_c14_2 = get_pin_pos("Device:C", 2, 154.94, 167.64)
    sb.add_wire(154.94, 157.48, p_c14_1[0], p_c14_1[1])
    sb.record_net("ESP_EN", "C14.1", "signal")
    sb.add_power_sym("power:GND", p_c14_2[0], p_c14_2[1], 0)
    sb.record_net("GND", "C14.2", "power")

    sb.add_symbol("Switch:SW_Push", "SW1", "SW_EN", 167.64, 167.64,
                  pins_count=2, footprint="", desc="Tactile Reset Button", mpn="SW-PB-6mm")
    p_sw1_1 = get_pin_pos("Switch:SW_Push", 1, 167.64, 167.64)
    p_sw1_2 = get_pin_pos("Switch:SW_Push", 2, 167.64, 167.64)
    sb.add_wire(154.94, 157.48, 162.56, 157.48)
    sb.add_junction(162.56, 157.48)
    sb.add_wire(162.56, 157.48, 162.56, p_sw1_1[1])
    sb.add_wire(162.56, p_sw1_1[1], p_sw1_1[0], p_sw1_1[1])
    sb.record_net("ESP_EN", "SW1.1", "signal")
    sb.add_power_sym("power:GND", p_sw1_2[0], p_sw1_2[1], 0)
    sb.record_net("GND", "SW1.2", "power")

    # 4.4. Boot Circuit (SW2, R11) at (144.78, 180.34)
    sb.add_symbol("Device:R", "R11", "10k", 144.78, 180.34, rot=90,
                  footprint="", desc="IO0 pull-up resistor", mpn="10k 1/4W 5%")
    p_r11_1 = get_pin_pos("Device:R", 1, 144.78, 180.34, rot=90)
    p_r11_2 = get_pin_pos("Device:R", 2, 144.78, 180.34, rot=90)
    sb.add_wire(137.16, 180.34, p_r11_1[0], p_r11_1[1])
    sb.add_label("+3V3", 137.16, 180.34)
    sb.record_net("+3V3", "R11.1", "power")

    sb.add_wire(p_r11_2[0], 180.34, 154.94, 180.34)
    sb.add_junction(154.94, 180.34)
    sb.add_label("ESP_IO0", 154.94, 180.34)
    sb.record_net("ESP_IO0", "R11.2", "signal")

    sb.add_symbol("Switch:SW_Push", "SW2", "SW_BOOT", 167.64, 180.34,
                  pins_count=2, footprint="", desc="Tactile Boot Button", mpn="SW-PB-6mm")
    p_sw2_1 = get_pin_pos("Switch:SW_Push", 1, 167.64, 180.34)
    p_sw2_2 = get_pin_pos("Switch:SW_Push", 2, 167.64, 180.34)
    sb.add_wire(154.94, 180.34, p_sw2_1[0], p_sw2_1[1])
    sb.record_net("ESP_IO0", "SW2.1", "signal")
    sb.add_power_sym("power:GND", p_sw2_2[0], p_sw2_2[1], 0)
    sb.record_net("GND", "SW2.2", "power")

    # 4.5. Programming & Expansion Headers (J20, J21, J22)
    # J20: UART0 Flash/Debug Header (1x06) at (144.78, 203.2)
    sb.add_symbol("Connector_Generic:Conn_01x06", "J20", "PROG_UART0", 144.78, 203.2,
                  pins_count=6, footprint="", desc="UART0 Flashing & Serial Monitor Header", mpn="Header 1x06 2.54mm")
    uart_pins = {
        1: ("+3V3", "power"),
        2: ("ESP_TXD0", "signal"),
        3: ("ESP_RXD0", "signal"),
        4: ("GND", "power"),
        5: ("ESP_IO0", "signal"),
        6: ("ESP_EN", "signal"),
    }
    for p_num, (sig_name, sig_type) in uart_pins.items():
        pt = get_pin_pos("Connector_Generic:Conn_01x06", p_num, 144.78, 203.2)
        if sig_name == "GND":
            sb.add_wire(pt[0], pt[1], pt[0] - 5.08, pt[1])
            sb.add_power_sym("power:GND", pt[0] - 5.08, pt[1], 0)
            sb.record_net("GND", f"J20.{p_num}", "power")
        else:
            sb.add_wire(pt[0], pt[1], pt[0] - 5.08, pt[1])
            sb.add_label(sig_name, pt[0] - 5.08, pt[1])
            sb.record_net(sig_name, f"J20.{p_num}", sig_type)

    # J21: ADC Analog Sensor Header (1x04) at (167.64, 203.2)
    sb.add_symbol("Connector_Generic:Conn_01x04", "J21", "SENSOR_ADC", 167.64, 203.2,
                  pins_count=4, footprint="", desc="ADC Analog Sensor Interface (VP/VN)", mpn="Header 1x04 2.54mm")
    adc_pins = {
        1: ("+3V3", "power"),
        2: ("ADC_VP", "signal"),
        3: ("ADC_VN", "signal"),
        4: ("GND", "power"),
    }
    for p_num, (sig_name, sig_type) in adc_pins.items():
        pt = get_pin_pos("Connector_Generic:Conn_01x04", p_num, 167.64, 203.2)
        if sig_name == "GND":
            sb.add_wire(pt[0], pt[1], pt[0] - 5.08, pt[1])
            sb.add_power_sym("power:GND", pt[0] - 5.08, pt[1], 0)
            sb.record_net("GND", f"J21.{p_num}", "power")
        else:
            sb.add_wire(pt[0], pt[1], pt[0] - 5.08, pt[1])
            sb.add_label(sig_name, pt[0] - 5.08, pt[1])
            sb.record_net(sig_name, f"J21.{p_num}", sig_type)

    # J22: Digital Sensor Expansion Header (1x08) at (190.5, 203.2)
    sb.add_symbol("Connector_Generic:Conn_01x08", "J22", "SENSOR_DIGITAL", 190.5, 203.2,
                  pins_count=8, footprint="", desc="General Digital Sensor Expansion Header", mpn="Header 1x08 2.54mm")
    exp_pins = {
        1: ("+5V", "power"),
        2: ("+3V3", "power"),
        3: ("EXP_IO4", "signal"),
        4: ("EXP_IO5", "signal"),
        5: ("EXP_IO13", "signal"),
        6: ("EXP_IO14", "signal"),
        7: ("EXP_IO2", "signal"),
        8: ("GND", "power"),
    }
    for p_num, (sig_name, sig_type) in exp_pins.items():
        pt = get_pin_pos("Connector_Generic:Conn_01x08", p_num, 190.5, 203.2)
        if sig_name == "GND":
            sb.add_wire(pt[0], pt[1], pt[0] - 5.08, pt[1])
            sb.add_power_sym("power:GND", pt[0] - 5.08, pt[1], 0)
            sb.record_net("GND", f"J22.{p_num}", "power")
        else:
            sb.add_wire(pt[0], pt[1], pt[0] - 5.08, pt[1])
            sb.add_label(sig_name, pt[0] - 5.08, pt[1])
            sb.record_net(sig_name, f"J22.{p_num}", sig_type)

    # --- SERVO PWM SIGNAL CONDITIONING (R1-R8) ---
    pwms = [
        ("ESP_S1_TOP_PWM", "S1_TOP_PWM", "R1", "R5", 142.24),
        ("ESP_S1_BOT_PWM", "S1_BOT_PWM", "R2", "R6", 160.02),
        ("ESP_S2_TOP_PWM", "S2_TOP_PWM", "R3", "R7", 177.8),
        ("ESP_S2_BOT_PWM", "S2_BOT_PWM", "R4", "R8", 195.58),
    ]

    for in_net, out_net, r_series, r_pd, y_pos in pwms:
        sb.add_symbol("Device:R", r_series, "330R", 236.22, y_pos, rot=90,
                      footprint="", desc=f"330 ohm series protection for {out_net}", mpn="330R 1/4W 5%")
        p_rs_1 = get_pin_pos("Device:R", 1, 236.22, y_pos, rot=90)
        p_rs_2 = get_pin_pos("Device:R", 2, 236.22, y_pos, rot=90)

        sb.add_wire(223.52, y_pos, p_rs_1[0], p_rs_1[1])
        sb.add_label(in_net, 223.52, y_pos)
        sb.record_net(in_net, f"{r_series}.1", "signal")

        sb.add_wire(p_rs_2[0], y_pos, 248.92, y_pos)
        sb.add_junction(248.92, y_pos)
        sb.add_wire(248.92, y_pos, 259.08, y_pos)
        sb.add_label(out_net, 259.08, y_pos)
        sb.record_net(out_net, f"{r_series}.2", "signal")

        sb.add_symbol("Device:R", r_pd, "10k", 248.92, y_pos + 8.89,
                      footprint="", desc=f"10k pull-down boot protection for {out_net}", mpn="10k 1/4W 5%")
        p_rpd_1 = get_pin_pos("Device:R", 1, 248.92, y_pos + 8.89)
        p_rpd_2 = get_pin_pos("Device:R", 2, 248.92, y_pos + 8.89)

        sb.add_wire(248.92, y_pos, p_rpd_1[0], p_rpd_1[1])
        sb.record_net(out_net, f"{r_pd}.1", "signal")

        sb.add_power_sym("power:GND", p_rpd_2[0], p_rpd_2[1], 0)
        sb.record_net("GND", f"{r_pd}.2", "power")

    # =========================================================================
    # BLOCK 5: IR TRANSMIT DRIVER & HEADERS
    # =========================================================================
    sb.add_box(20.32, 180.34, 124.46, 274.32,
               "5. IR TRANSMITTER DRIVER CIRCUIT",
               "GPIO23 -> NPN Driver (S8050/2N2222) | 2x JST-XH 2-pin connectors (1 per column)")

    # R13: 1k Base Resistor at (43.18, 208.28), rot 90
    sb.add_symbol("Device:R", "R13", "1k", 43.18, 208.28, rot=90,
                  footprint="", desc="Base current limit resistor for IR driver", mpn="1k 1/4W 5%")
    p_R13_1 = get_pin_pos("Device:R", 1, 43.18, 208.28, rot=90)
    p_R13_2 = get_pin_pos("Device:R", 2, 43.18, 208.28, rot=90)

    sb.add_wire(33.02, 208.28, p_R13_1[0], p_R13_1[1])
    sb.add_label("ESP_IR_TX", 33.02, 208.28)
    sb.record_net("ESP_IR_TX", "R13.1", "signal")

    # Q2: NPN (S8050 / 2N2222) at (55.88, 208.28), rot 0
    sb.add_symbol("Device:Q_NPN", "Q2", "S8050", 55.88, 208.28,
                  footprint="", desc="NPN driver transistor for 38kHz IR burst transmitter", mpn="S8050",
                  pin_names=["B", "C", "E"])
    p_Q2_B = get_pin_pos("Device:Q_NPN", "B", 55.88, 208.28)
    p_Q2_C = get_pin_pos("Device:Q_NPN", "C", 55.88, 208.28)
    p_Q2_E = get_pin_pos("Device:Q_NPN", "E", 55.88, 208.28)

    sb.add_wire(p_R13_2[0], p_R13_2[1], p_Q2_B[0], p_Q2_B[1])
    sb.record_net("NET_Q2_BASE", "R13.2", "signal")
    sb.record_net("NET_Q2_BASE", "Q2.B", "signal")

    sb.add_power_sym("power:GND", p_Q2_E[0], p_Q2_E[1], 0)
    sb.record_net("GND", "Q2.E", "power")

    # Collector to IR_TX_RET bus
    sb.add_wire(p_Q2_C[0], p_Q2_C[1], p_Q2_C[0], 198.12)
    sb.add_wire(p_Q2_C[0], 198.12, 76.2, 198.12)
    sb.add_junction(76.2, 198.12)
    sb.add_label("IR_TX_RET", 66.04, 198.12)
    sb.record_net("IR_TX_RET", "Q2.C", "signal")

    # Channel 1: R14 (120R) + J11 (IR_TX1)
    sb.add_symbol("Device:R", "R14", "120R", 81.28, 215.9,
                  footprint="", desc="Current limiting resistor for Col 1 IR LED", mpn="120R 1/2W 5%")
    p_R14_1 = get_pin_pos("Device:R", 1, 81.28, 215.9)
    p_R14_2 = get_pin_pos("Device:R", 2, 81.28, 215.9)

    sb.add_wire(p_R14_1[0], p_R14_1[1], 71.12, p_R14_1[1])
    sb.add_label("+5V", 71.12, p_R14_1[1])
    sb.record_net("+5V", "R14.1", "power")

    # J11: IR_TX1 at (101.6, 222.25)
    sb.add_symbol("Connector_Generic:Conn_01x02", "J11", "IR_TX1 (Col 1)", 101.6, 222.25,
                  pins_count=2, footprint="",
                  desc="Col 1 IR LED Emitter JST-XH 2-pin", mpn="JST-XH 2-pin")
    p_J11_1 = get_pin_pos("Connector_Generic:Conn_01x02", 1, 101.6, 222.25)
    p_J11_2 = get_pin_pos("Connector_Generic:Conn_01x02", 2, 101.6, 222.25)

    sb.add_wire(p_R14_2[0], p_R14_2[1], p_R14_2[0], p_J11_1[1])
    sb.add_wire(p_R14_2[0], p_J11_1[1], p_J11_1[0], p_J11_1[1])
    sb.record_net("NET_IR_TX1_ANODE", "R14.2", "signal")
    sb.record_net("NET_IR_TX1_ANODE", "J11.1", "signal")

    sb.add_wire(p_J11_2[0], p_J11_2[1], 76.2, p_J11_2[1])
    sb.add_wire(76.2, p_J11_2[1], 76.2, 198.12)
    sb.record_net("IR_TX_RET", "J11.2", "signal")

    # Channel 2: R15 (120R) + J12 (IR_TX2)
    sb.add_symbol("Device:R", "R15", "120R", 81.28, 246.38,
                  footprint="", desc="Current limiting resistor for Col 2 IR LED", mpn="120R 1/2W 5%")
    p_R15_1 = get_pin_pos("Device:R", 1, 81.28, 246.38)
    p_R15_2 = get_pin_pos("Device:R", 2, 81.28, 246.38)

    sb.add_wire(p_R15_1[0], p_R15_1[1], 71.12, p_R15_1[1])
    sb.add_label("+5V", 71.12, p_R15_1[1])
    sb.record_net("+5V", "R15.1", "power")

    # J12: IR_TX2 at (101.6, 252.73)
    sb.add_symbol("Connector_Generic:Conn_01x02", "J12", "IR_TX2 (Col 2)", 101.6, 252.73,
                  pins_count=2, footprint="",
                  desc="Col 2 IR LED Emitter JST-XH 2-pin", mpn="JST-XH 2-pin")
    p_J12_1 = get_pin_pos("Connector_Generic:Conn_01x02", 1, 101.6, 252.73)
    p_J12_2 = get_pin_pos("Connector_Generic:Conn_01x02", 2, 101.6, 252.73)

    sb.add_wire(p_R15_2[0], p_R15_2[1], p_R15_2[0], p_J12_1[1])
    sb.add_wire(p_R15_2[0], p_J12_1[1], p_J12_1[0], p_J12_1[1])
    sb.record_net("NET_IR_TX2_ANODE", "R15.2", "signal")
    sb.record_net("NET_IR_TX2_ANODE", "J12.1", "signal")

    sb.add_wire(p_J12_2[0], p_J12_2[1], 76.2, p_J12_2[1])
    sb.add_wire(76.2, p_J12_2[1], 76.2, p_J11_2[1])
    sb.add_junction(76.2, p_J11_2[1])
    sb.record_net("IR_TX_RET", "J12.2", "signal")

    # =========================================================================
    # BLOCK 6: IR RECEIVER HEADERS
    # =========================================================================
    sb.add_box(132.08, 220.98, 195.58, 274.32,
               "6. IR RECEIVER HEADERS",
               "3-wire cables to satellite RX sensor boards (38kHz TSOP/VS1838B)")

    # J9: IR_RX1 at (152.4, 238.76)
    sb.add_symbol("Connector_Generic:Conn_01x03", "J9", "IR_RX1", 152.4, 238.76,
                  pins_count=3, footprint="", desc="Col 1 IR Receiver header (3V3, OUT, GND)", mpn="JST-XH 3-pin")
    p_J9_1 = get_pin_pos("Connector_Generic:Conn_01x03", 1, 152.4, 238.76)
    p_J9_2 = get_pin_pos("Connector_Generic:Conn_01x03", 2, 152.4, 238.76)
    p_J9_3 = get_pin_pos("Connector_Generic:Conn_01x03", 3, 152.4, 238.76)

    sb.add_wire(p_J9_1[0], p_J9_1[1], 137.16, p_J9_1[1])
    sb.add_label("+3V3", 137.16, p_J9_1[1])
    sb.record_net("+3V3", "J9.1", "power")

    sb.add_wire(p_J9_2[0], p_J9_2[1], 137.16, p_J9_2[1])
    sb.add_label("IR_RX1", 137.16, p_J9_2[1])
    sb.record_net("IR_RX1", "J9.2", "signal")

    sb.add_wire(p_J9_3[0], p_J9_3[1], 137.16, p_J9_3[1])
    sb.add_power_sym("power:GND", 137.16, p_J9_3[1], 0)
    sb.record_net("GND", "J9.3", "power")

    # J10: IR_RX2 at (152.4, 259.08)
    sb.add_symbol("Connector_Generic:Conn_01x03", "J10", "IR_RX2", 152.4, 259.08,
                  pins_count=3, footprint="", desc="Col 2 IR Receiver header (3V3, OUT, GND)", mpn="JST-XH 3-pin")
    p_J10_1 = get_pin_pos("Connector_Generic:Conn_01x03", 1, 152.4, 259.08)
    p_J10_2 = get_pin_pos("Connector_Generic:Conn_01x03", 2, 152.4, 259.08)
    p_J10_3 = get_pin_pos("Connector_Generic:Conn_01x03", 3, 152.4, 259.08)

    sb.add_wire(p_J10_1[0], p_J10_1[1], 137.16, p_J10_1[1])
    sb.add_label("+3V3", 137.16, p_J10_1[1])
    sb.record_net("+3V3", "J10.1", "power")

    sb.add_wire(p_J10_2[0], p_J10_2[1], 137.16, p_J10_2[1])
    sb.add_label("IR_RX2", 137.16, p_J10_2[1])
    sb.record_net("IR_RX2", "J10.2", "signal")

    sb.add_wire(p_J10_3[0], p_J10_3[1], 137.16, p_J10_3[1])
    sb.add_power_sym("power:GND", 137.16, p_J10_3[1], 0)
    sb.record_net("GND", "J10.3", "power")

    # =========================================================================
    # BLOCK 7: OPTIONAL LIMIT SWITCH INPUTS (DNP)
    # =========================================================================
    sb.add_box(200.66, 215.9, 274.32, 274.32,
               "7. LIMIT SWITCHES (OPTIONAL - DNP)",
               "4x JST-XH 2-pin | 10k pull-up to 3V3 | 100nF filter (Not populated in Rev A)")

    switches = [
        ("LS1", "J13", "R16", "C7", 228.6),
        ("LS2", "J14", "R17", "C8", 241.3),
        ("LS3", "J15", "R18", "C9", 254.0),
        ("LS4", "J16", "R19", "C10", 266.7),
    ]

    for net_name, j_ref, r_ref, c_ref, y_pos in switches:
        # Header J at (213.36, y_pos)
        sb.add_symbol("Connector_Generic:Conn_01x02", j_ref, f"{net_name} (DNP)", 213.36, y_pos,
                      pins_count=2, footprint="", desc=f"Limit switch {net_name} (DNP)",
                      dnp=True, mpn="JST-XH 2-pin")
        p_j_1 = get_pin_pos("Connector_Generic:Conn_01x02", 1, 213.36, y_pos)
        p_j_2 = get_pin_pos("Connector_Generic:Conn_01x02", 2, 213.36, y_pos)

        # Pin 1 to signal bus
        sb.add_wire(p_j_1[0], p_j_1[1], 203.2, p_j_1[1])
        sb.add_label(net_name, 203.2, p_j_1[1])
        sb.record_net(net_name, f"{j_ref}.1", "signal")

        # Pin 2 to GND
        sb.add_wire(p_j_2[0], p_j_2[1], 203.2, p_j_2[1])
        sb.add_power_sym("power:GND", 203.2, p_j_2[1], 0)
        sb.record_net("GND", f"{j_ref}.2", "power")

        # Wire from Pin 1 over to R and C
        sb.add_wire(p_j_1[0], p_j_1[1], 228.6, p_j_1[1])
        sb.add_junction(228.6, p_j_1[1])

        # Pull-up R to +3V3 at (228.6, p_j_1[1] + 6.35), rot 0
        sb.add_symbol("Device:R", r_ref, "10k (DNP)", 228.6, p_j_1[1] + 6.35,
                      footprint="", desc=f"10k pull-up for {net_name} (DNP)", dnp=True, mpn="10k 1/4W 5%")
        p_r_1 = get_pin_pos("Device:R", 1, 228.6, p_j_1[1] + 6.35)
        p_r_2 = get_pin_pos("Device:R", 2, 228.6, p_j_1[1] + 6.35)

        sb.add_wire(228.6, p_j_1[1], p_r_1[0], p_r_1[1])
        sb.record_net(net_name, f"{r_ref}.1", "signal")

        sb.add_wire(p_r_2[0], p_r_2[1], 233.68, p_r_2[1])
        sb.add_label("+3V3", 233.68, p_r_2[1])
        sb.record_net("+3V3", f"{r_ref}.2", "power")

        # Filter C to GND at (248.92, p_j_1[1] + 6.35), rot 0
        sb.add_symbol("Device:C", c_ref, "100nF (DNP)", 248.92, p_j_1[1] + 6.35,
                      footprint="", desc=f"100nF filter capacitor for {net_name} (DNP)", dnp=True, mpn="100nF 50V Ceramic")
        p_c_1 = get_pin_pos("Device:C", 1, 248.92, p_j_1[1] + 6.35)
        p_c_2 = get_pin_pos("Device:C", 2, 248.92, p_j_1[1] + 6.35)

        sb.add_wire(228.6, p_j_1[1], p_c_1[0], p_j_1[1])
        sb.add_wire(p_c_1[0], p_j_1[1], p_c_1[0], p_c_1[1])
        sb.record_net(net_name, f"{c_ref}.1", "signal")

        sb.add_power_sym("power:GND", p_c_2[0], p_c_2[1], 0)
        sb.record_net("GND", f"{c_ref}.2", "power")

    # =========================================================================
    # BLOCK 8: DIAGNOSTICS: STATUS LEDS & TEST POINTS
    # =========================================================================
    sb.add_box(281.94, 17.78, 396.24, 208.28,
               "8. DIAGNOSTICS & RAIL DECOUPLING",
               "Power LEDs and dedicated test points for all rails (+12V, +6V_A, +6V_B, +5V, +3V3, GND)")

    # Decoupling for 5V & 3.3V
    sb.add_symbol("Device:C_Polarized", "C5", "10uF 16V", 294.64, 38.1,
                  pins_count=2, footprint="", desc="5V rail bulk decoupling capacitor", mpn="10uF 16V Radial")
    p_C5_1 = get_pin_pos("Device:C_Polarized", 1, 294.64, 38.1)
    p_C5_2 = get_pin_pos("Device:C_Polarized", 2, 294.64, 38.1)
    sb.add_wire(p_C5_1[0], p_C5_1[1], 287.02, p_C5_1[1])
    sb.add_label("+5V", 287.02, p_C5_1[1])
    sb.record_net("+5V", "C5.1", "power")
    sb.add_power_sym("power:GND", p_C5_2[0], p_C5_2[1], 0)
    sb.record_net("GND", "C5.2", "power")

    sb.add_symbol("Device:C", "C6", "100nF", 307.34, 38.1,
                  pins_count=2, footprint="", desc="3.3V rail decoupling capacitor", mpn="100nF 50V Ceramic")
    p_C6_1 = get_pin_pos("Device:C", 1, 307.34, 38.1)
    p_C6_2 = get_pin_pos("Device:C", 2, 307.34, 38.1)
    sb.add_wire(p_C6_1[0], p_C6_1[1], 314.96, p_C6_1[1])
    sb.add_label("+3V3", 314.96, p_C6_1[1])
    sb.record_net("+3V3", "C6.1", "power")
    sb.add_power_sym("power:GND", p_C6_2[0], p_C6_2[1], 0)
    sb.record_net("GND", "C6.2", "power")

    # Status LEDs and series resistors (rot 90)
    led_rails = [
        ("+12V", "D2", "R20", "5.6k", 60.96),
        ("+6V_A", "D3", "R21", "2.2k", 86.36),
        ("+6V_B", "D4", "R22", "2.2k", 111.76),
        ("+5V", "D5", "R23", "1.5k", 137.16),
        ("+3V3", "D6", "R24", "1.0k", 162.56),
    ]

    for rail, d_ref, r_ref, r_val, y_pos in led_rails:
        sb.add_symbol("Device:R", r_ref, r_val, 308.61, y_pos, rot=90,
                      footprint="", desc=f"Current limiting for {rail} LED", mpn=f"{r_val} 1/4W 5%")
        p_r_1 = get_pin_pos("Device:R", 1, 308.61, y_pos, rot=90)
        p_r_2 = get_pin_pos("Device:R", 2, 308.61, y_pos, rot=90)

        sb.add_wire(294.64, y_pos, p_r_1[0], p_r_1[1])
        sb.add_label(rail, 294.64, y_pos)
        sb.record_net(rail, f"{r_ref}.1", "power")

        sb.add_symbol("Device:LED", d_ref, f"LED_{rail}", 320.04, y_pos,
                      pins_count=2, footprint="", desc=f"Green LED indicator for {rail}", mpn="3mm Green LED")
        p_d_1 = get_pin_pos("Device:LED", 1, 320.04, y_pos)
        p_d_2 = get_pin_pos("Device:LED", 2, 320.04, y_pos)

        sb.add_wire(p_r_2[0], p_r_2[1], p_d_1[0], p_d_1[1])
        sb.record_net(f"NET_{d_ref}_ANODE", f"{r_ref}.2", "signal")
        sb.record_net(f"NET_{d_ref}_ANODE", f"{d_ref}.1", "signal")

        sb.add_power_sym("power:GND", p_d_2[0], p_d_2[1], 0)
        sb.record_net("GND", f"{d_ref}.2", "power")

    # Test Points TP1..TP8
    test_points = [
        ("TP1", "+12V", 355.6, 60.96),
        ("TP2", "+6V_A", 355.6, 86.36),
        ("TP3", "+6V_B", 355.6, 111.76),
        ("TP4", "+5V", 355.6, 137.16),
        ("TP5", "+3V3", 355.6, 162.56),
        ("TP6", "GND", 355.6, 187.96),
        ("TP7", "GND", 381.0, 187.96),
        ("TP8", "SPARE_GPIO33", 381.0, 162.56),
    ]

    for tp_ref, rail, x_pos, y_pos in test_points:
        sb.add_symbol("Connector:TestPoint", tp_ref, f"TP_{rail}", x_pos, y_pos,
                      pins_count=1, footprint="", desc=f"Diagnostic Test Point for {rail}", mpn="Test Point Loop THT")
        p_tp = get_pin_pos("Connector:TestPoint", 1, x_pos, y_pos)
        if rail == "GND":
            sb.add_power_sym("power:GND", p_tp[0], p_tp[1], 0)
            sb.record_net("GND", f"{tp_ref}.1", "power")
        else:
            sb.add_wire(p_tp[0], p_tp[1], p_tp[0] - 7.62, p_tp[1])
            sb.add_label(rail, p_tp[0] - 7.62, p_tp[1])
            sb.record_net(rail, f"{tp_ref}.1", "power" if "V" in rail else "signal")

    # =========================================================================
    # BLOCK 9: SPARE I2C CONNECTOR
    # =========================================================================
    sb.add_box(281.94, 215.9, 396.24, 274.32,
               "9. AUXILIARY / I2C EXPANSION HEADER",
               "Reserved 4-pin header for optional external display, sensors or I2C expander")

    sb.add_symbol("Connector_Generic:Conn_01x04", "J17", "I2C_RESERVED", 330.2, 241.3,
                  pins_count=4, footprint="", desc="Reserved I2C 4-pin header (3V3, SDA, SCL, GND)",
                  mpn="4-pin Header 2.54mm")
    p_i2c_1 = get_pin_pos("Connector_Generic:Conn_01x04", 1, 330.2, 241.3)
    p_i2c_2 = get_pin_pos("Connector_Generic:Conn_01x04", 2, 330.2, 241.3)
    p_i2c_3 = get_pin_pos("Connector_Generic:Conn_01x04", 3, 330.2, 241.3)
    p_i2c_4 = get_pin_pos("Connector_Generic:Conn_01x04", 4, 330.2, 241.3)

    sb.add_wire(p_i2c_1[0], p_i2c_1[1], 314.96, p_i2c_1[1])
    sb.add_label("+3V3", 314.96, p_i2c_1[1])
    sb.record_net("+3V3", "J17.1", "power")

    sb.add_wire(p_i2c_2[0], p_i2c_2[1], 314.96, p_i2c_2[1])
    sb.add_label("I2C_SDA", 314.96, p_i2c_2[1])
    sb.record_net("I2C_SDA", "J17.2", "signal")

    sb.add_wire(p_i2c_3[0], p_i2c_3[1], 314.96, p_i2c_3[1])
    sb.add_label("I2C_SCL", 314.96, p_i2c_3[1])
    sb.record_net("I2C_SCL", "J17.3", "signal")

    sb.add_wire(p_i2c_4[0], p_i2c_4[1], 314.96, p_i2c_4[1])
    sb.add_power_sym("power:GND", 314.96, p_i2c_4[1], 0)
    sb.record_net("GND", "J17.4", "power")

    # =========================================================================
    # WRITE NATIVE SCHEMATIC
    # =========================================================================
    sch_content = sb.build()
    OUT_SCH.parent.mkdir(exist_ok=True, parents=True)
    OUT_SCH.write_text(sch_content, encoding="utf-8", newline="\n")
    print(f"Generated native KiCad schematic: {OUT_SCH}")

    # =========================================================================
    # WRITE COMPONENT & NET MANIFEST
    # =========================================================================
    manifest_data = {
        "project": "FV-CTRL",
        "revision": "Rev A (Engineering Draft)",
        "tool": "KiCad 10.0.7",
        "date": "2026-10-16",
        "summary": {
            "total_components": len(sb.manifest_parts),
            "total_nets": len(sb.manifest_nets),
            "power_rails": ["+12V_IN", "+12V", "+6V_A", "+6V_B", "+5V", "+3V3", "GND"]
        },
        "components": sb.manifest_parts,
        "nets": sb.manifest_nets
    }
    OUT_MANIFEST.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8", newline="\n")
    print(f"Generated component & net manifest: {OUT_MANIFEST}")

    # =========================================================================
    # UPDATE BACKWARD-COMPATIBLE FV-CTRL_RevA.net.json
    # =========================================================================
    compat_netlist = {
        "revision": "Rev A",
        "rails": ["+12V_IN", "+12V", "+6V_A", "+6V_B", "+5V", "+3V3", "GND"],
        "connectors": [
            {"ref": "J1", "value": "12V_IN", "pins": ["+12V_IN", "GND"]},
            {"ref": "J2", "value": "XL4015_A", "pins": ["+12V", "GND", "+6V_A", "GND"]},
            {"ref": "J3", "value": "XL4015_B", "pins": ["+12V", "GND", "+6V_B", "GND"]},
            {"ref": "J4", "value": "BUCK_5V", "pins": ["+12V", "GND", "+5V", "GND"]},
            {"ref": "J5", "value": "S1_TOP", "pins": ["GND", "+6V_A", "S1_TOP_PWM"]},
            {"ref": "J6", "value": "S1_BOT", "pins": ["GND", "+6V_A", "S1_BOT_PWM"]},
            {"ref": "J7", "value": "S2_TOP", "pins": ["GND", "+6V_B", "S2_TOP_PWM"]},
            {"ref": "J8", "value": "S2_BOT", "pins": ["GND", "+6V_B", "S2_BOT_PWM"]},
            {"ref": "J9", "value": "IR_RX1", "pins": ["+3V3", "IR_RX1", "GND"]},
            {"ref": "J10", "value": "IR_RX2", "pins": ["+3V3", "IR_RX2", "GND"]}
        ],
        "signals": {
            "S1_TOP_PWM": "GPIO16",
            "S1_BOT_PWM": "GPIO17",
            "S2_TOP_PWM": "GPIO18",
            "S2_BOT_PWM": "GPIO19",
            "IR_TX": "GPIO23",
            "IR_RX1": "GPIO34",
            "IR_RX2": "GPIO35",
            "LS1": "GPIO25",
            "LS2": "GPIO26",
            "LS3": "GPIO27",
            "LS4": "GPIO32"
        },
        "parts": [
            {"ref": "F1", "value": "5A replaceable fuse", "footprint": "THT Cartridge Holder 5x20mm"},
            {"ref": "Q1", "value": "P-MOSFET reverse polarity (IRF9540N)", "footprint": "TO-220-3_Vertical"},
            {"ref": "D1", "value": "12V TVS (1.5KE15CA)", "footprint": "DO-201AD_Horizontal"},
            {"ref": "F2,F3", "value": "PTC 3A per servo rail", "footprint": "Bourns_MF-RHT_THT"},
            {"ref": "R1-R4", "value": "330R PWM series", "footprint": "R_Axial_DIN0207"},
            {"ref": "R5-R8", "value": "10k PWM pull-down", "footprint": "R_Axial_DIN0207"},
            {"ref": "C1,C2", "value": "1000-2200uF 16V servo bulk", "footprint": "CP_Radial_D10.0mm"},
            {"ref": "Q2", "value": "S8050 or 2N2222 IR driver", "footprint": "TO-92"}
        ],
        "circuits": [
            {"name": "12V protection", "path": "J1.1 -> F1 -> Q1 -> +12V; D1: +12V to GND"},
            {"name": "servo rail A", "path": "J2.3 -> F2 -> +6V_A; C1: +6V_A to GND"},
            {"name": "servo rail B", "path": "J3.3 -> F3 -> +6V_B; C2: +6V_B to GND"},
            {"name": "PWM", "path": "GPIO -> 330R -> Jx.SIG; 10k from Jx.SIG to GND (x4)"},
            {"name": "IR TX", "path": "GPIO23 -> 1k -> Q2 base; Q2 collector <- 2x(LED IR + resistor) from +5V; emitter -> GND"},
            {"name": "IR RX", "path": "J9/J10: +3V3, OUT to GPIO34/35, GND; each RX board has 100R + 4.7uF supply filter"},
            {"name": "limit switches", "path": "GPIO25/26/27/32: 10k pull-up to +3V3 and 100nF to GND; DNP"}
        ]
    }
    OUT_NETLIST.write_text(json.dumps(compat_netlist, indent=2), encoding="utf-8", newline="\n")
    print(f"Updated validator netlist: {OUT_NETLIST}")

    # =========================================================================
    # WRITE DRAFT BOM DOCUMENT
    # =========================================================================
    bom_lines = [
        "# BOM Nháp FV-CTRL Rev A (Engineering Draft)\n\n",
        "| Ref | Giá trị / Mô tả | Thư viện | Footprint | DNP | MPN / Ghi chú |\n",
        "|---|---|---|---|---|---|\n"
    ]
    for p in sb.manifest_parts:
        dnp_flag = "DNP" if p["dnp"] else "No"
        bom_lines.append(f"| {p['ref']} | {p['value']} | `{p['lib_id']}` | {p['footprint']} | {dnp_flag} | {p['mpn']} |\n")

    OUT_BOM.write_text("".join(bom_lines), encoding="utf-8", newline="\n")
    print(f"Generated draft BOM: {OUT_BOM}")


if __name__ == "__main__":
    generate_all()
