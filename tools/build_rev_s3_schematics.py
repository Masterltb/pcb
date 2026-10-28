"""
Complete Schematic & Project Builder for FreshVend Hardware Rev-S3.
Builds:
- hardware/rev_s3/FV-CTRL_RevS3.kicad_sch (Root Sheet)
- hardware/rev_s3/FV-CTRL_RevS3-01.kicad_sch (1. Power Supply)
- hardware/rev_s3/FV-CTRL_RevS3-02.kicad_sch (2. MCU ESP32-S3 & USB Type-C)
- hardware/rev_s3/FV-CTRL_RevS3-03.kicad_sch (3. Servo 4x PWM)
- hardware/rev_s3/FV-CTRL_RevS3-04.kicad_sch (4. Universal Drop Sensors)
- hardware/rev_s3/FV-CTRL_RevS3-05.kicad_sch (5. Diagnostics & Spares)
"""
import uuid
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "hardware/rev_s3"
OUT_DIR.mkdir(parents=True, exist_ok=True)
KICAD_SYM_DIR = Path("C:/Program Files/KiCad/10.0/share/kicad/symbols")

def uid():
    return str(uuid.uuid4())

def get_symbol_sexpr(content: str, sym_name: str) -> str:
    m = re.search(rf'(\n[ \t]*\(symbol "{re.escape(sym_name)}"\s)', content)
    if not m:
        m = re.search(rf'(\n[ \t]*\(symbol "{re.escape(sym_name)}"\n)', content)
    if not m:
        raise ValueError(f"Symbol {sym_name} not found")
    start_pos = m.start(1)
    open_paren = content.find('(', start_pos)
    depth = 0
    in_quote = False
    escape = False
    for i in range(open_paren, len(content)):
        char = content[i]
        if in_quote:
            if escape:
                escape = False
            elif char == '\\':
                escape = True
            elif char == '"':
                in_quote = False
        else:
            if char == '"':
                in_quote = True
            elif char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0:
                    return content[open_paren:i+1].strip()
    raise ValueError("Unmatched parenthesis")

def extract_lib_symbol(sym_file: str, sym_name: str, target_lib_id: str) -> str:
    path = KICAD_SYM_DIR / sym_file
    if not path.exists():
        path = ROOT / "libs" / sym_file
    content = path.read_text(encoding="utf-8", errors="ignore")
    body = get_symbol_sexpr(content, sym_name)
    short_target = target_lib_id.split(":")[-1]
    body = re.sub(rf'^\(symbol "{re.escape(sym_name)}"', f'(symbol "{target_lib_id}"', body, count=1)
    body = re.sub(rf'\(symbol "{re.escape(sym_name)}(_[0-9]+_[0-9]+)"', rf'(symbol "{short_target}\1"', body)
    return "\t\t" + body.replace("\n", "\n\t\t")

def extract_symbol_pins(lib_file: str, sym_name: str):
    path = KICAD_SYM_DIR / lib_file
    if not path.exists():
        path = ROOT / "libs" / lib_file
    content = path.read_text(encoding="utf-8", errors="ignore")
    body = get_symbol_sexpr(content, sym_name)

    pins = {}
    pin_matches = re.finditer(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-0-9.]+)\s+([-0-9.]+)(?:\s+[-0-9.]+)?\)', body)
    for pm in pin_matches:
        px = float(pm.group(1))
        py = float(pm.group(2))
        pin_start = pm.start()
        depth = 0
        in_quote = False
        escape = False
        pin_body = ""
        for i in range(pin_start, len(body)):
            c = body[i]
            if in_quote:
                if escape:
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == '"':
                    in_quote = False
            else:
                if c == '"':
                    in_quote = True
                elif c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        pin_body = body[pin_start:i+1]
                        break
        num_m = re.search(r'\(number\s+"([^"]+)"', pin_body)
        if num_m:
            pins[num_m.group(1)] = (px, py)
    return pins

# Build PIN_DB
PIN_DB = {
    "Device:R": extract_symbol_pins("Device.kicad_sym", "R"),
    "Device:C": extract_symbol_pins("Device.kicad_sym", "C"),
    "Device:C_Polarized": extract_symbol_pins("Device.kicad_sym", "C_Polarized"),
    "Device:Fuse": extract_symbol_pins("Device.kicad_sym", "Fuse"),
    "Device:Polyfuse": extract_symbol_pins("Device.kicad_sym", "Polyfuse"),
    "Device:D_TVS": extract_symbol_pins("Device.kicad_sym", "D_TVS"),
    "Device:D_Schottky": extract_symbol_pins("Device.kicad_sym", "D_Schottky"),
    "Device:LED": extract_symbol_pins("Device.kicad_sym", "LED"),
    "Switch:SW_Push": extract_symbol_pins("Switch.kicad_sym", "SW_Push"),
    "Connector_Generic:Conn_01x02": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x02"),
    "Connector_Generic:Conn_01x03": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x03"),
    "Connector_Generic:Conn_01x04": extract_symbol_pins("Connector_Generic.kicad_sym", "Conn_01x04"),
    "Connector:TestPoint": extract_symbol_pins("Connector.kicad_sym", "TestPoint"),
    "power:GND": extract_symbol_pins("power.kicad_sym", "GND"),
    "power:+12V": extract_symbol_pins("power.kicad_sym", "+12V"),
    "power:+5V": extract_symbol_pins("power.kicad_sym", "+5V"),
    "power:+3V3": extract_symbol_pins("power.kicad_sym", "+3V3"),
    "power:PWR_FLAG": extract_symbol_pins("power.kicad_sym", "PWR_FLAG"),
    "RF_Module:ESP32-S3-WROOM-1": extract_symbol_pins("RF_Module.kicad_sym", "ESP32-S3-WROOM-1"),
    "Connector:USB_C_Receptacle_USB2.0_16P": extract_symbol_pins("Connector.kicad_sym", "USB_C_Receptacle_USB2.0_16P"),
    "fv_revb:RECOM_R78E5V1A": extract_symbol_pins("fv_revb.kicad_sym", "RECOM_R78E5V1A"),
    "fv_revb:LD1117V33": extract_symbol_pins("fv_revb.kicad_sym", "LD1117V33"),
}

LIB_SYM_DEF = {
    "Device:R": extract_lib_symbol("Device.kicad_sym", "R", "Device:R"),
    "Device:C": extract_lib_symbol("Device.kicad_sym", "C", "Device:C"),
    "Device:C_Polarized": extract_lib_symbol("Device.kicad_sym", "C_Polarized", "Device:C_Polarized"),
    "Device:Fuse": extract_lib_symbol("Device.kicad_sym", "Fuse", "Device:Fuse"),
    "Device:Polyfuse": extract_lib_symbol("Device.kicad_sym", "Polyfuse", "Device:Polyfuse"),
    "Device:D_TVS": extract_lib_symbol("Device.kicad_sym", "D_TVS", "Device:D_TVS"),
    "Device:D_Schottky": extract_lib_symbol("Device.kicad_sym", "D_Schottky", "Device:D_Schottky"),
    "Device:LED": extract_lib_symbol("Device.kicad_sym", "LED", "Device:LED"),
    "Switch:SW_Push": extract_lib_symbol("Switch.kicad_sym", "SW_Push", "Switch:SW_Push"),
    "Connector_Generic:Conn_01x02": extract_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x02", "Connector_Generic:Conn_01x02"),
    "Connector_Generic:Conn_01x03": extract_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x03", "Connector_Generic:Conn_01x03"),
    "Connector_Generic:Conn_01x04": extract_lib_symbol("Connector_Generic.kicad_sym", "Conn_01x04", "Connector_Generic:Conn_01x04"),
    "Connector:TestPoint": extract_lib_symbol("Connector.kicad_sym", "TestPoint", "Connector:TestPoint"),
    "power:GND": extract_lib_symbol("power.kicad_sym", "GND", "power:GND"),
    "power:+12V": extract_lib_symbol("power.kicad_sym", "+12V", "power:+12V"),
    "power:+5V": extract_lib_symbol("power.kicad_sym", "+5V", "power:+5V"),
    "power:+3V3": extract_lib_symbol("power.kicad_sym", "+3V3", "power:+3V3"),
    "power:PWR_FLAG": extract_lib_symbol("power.kicad_sym", "PWR_FLAG", "power:PWR_FLAG"),
    "RF_Module:ESP32-S3-WROOM-1": extract_lib_symbol("RF_Module.kicad_sym", "ESP32-S3-WROOM-1", "RF_Module:ESP32-S3-WROOM-1"),
    "Connector:USB_C_Receptacle_USB2.0_16P": extract_lib_symbol("Connector.kicad_sym", "USB_C_Receptacle_USB2.0_16P", "Connector:USB_C_Receptacle_USB2.0_16P"),
    "fv_revb:RECOM_R78E5V1A": extract_lib_symbol("fv_revb.kicad_sym", "RECOM_R78E5V1A", "fv_revb:RECOM_R78E5V1A"),
    "fv_revb:LD1117V33": extract_lib_symbol("fv_revb.kicad_sym", "LD1117V33", "fv_revb:LD1117V33"),
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

def format_symbol_instance(lib_id, ref, val, footprint, at_x, at_y, rot=0, dnp=False):
    dnp_str = "yes" if dnp else "no"
    return f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {at_x:.4f} {at_y:.4f} {rot})
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp {dnp_str})
\t\t(uuid "{uid()}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {at_x:.4f} {at_y - 2.54:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "{val}"
\t\t\t(at {at_x:.4f} {at_y + 2.54:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "{footprint}"
\t\t\t(at {at_x:.4f} {at_y:.4f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t)
"""

def format_wire(x1, y1, x2, y2):
    return f"""\t(wire
\t\t(pts
\t\t\t(xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f})
\t\t)
\t\t(stroke (width 0) (type default))
\t\t(uuid "{uid()}")
\t)
"""

def format_no_connect(x, y):
    return f"""\t(no_connect
\t\t(at {x:.4f} {y:.4f})
\t\t(uuid "{uid()}")
\t)
"""

def format_global_label(name, x, y, rot=0, shape="passive"):
    justify = "left" if rot == 0 else "right"
    return f'\t(global_label "{name}" (shape {shape}) (at {x:.4f} {y:.4f} {rot}) (effects (font (size 1.016 1.016)) (justify {justify})) (uuid "{uid()}"))\n'

def make_sheet(title, used_syms, content):
    lib_syms_str = "\n".join(LIB_SYM_DEF[k] for k in used_syms)
    return f"""(kicad_sch
\t(version 20250114)
\t(generator "fv_native_s3_generator")
\t(generator_version "10.0")
\t(uuid "{uid()}")
\t(paper "A3")
\t(title_block
\t\t(title "{title}")
\t\t(date "2026-10-28")
\t\t(rev "Rev-S3 - PROTOTYPE")
\t\t(company "FreshVend Project")
\t\t(comment 1 "ESP32-S3-WROOM-1U | USB Type-C | Universal Drop Sensor")
\t\t(comment 2 "2-Layer 0603 DFM Standard")
\t)
\t(lib_symbols
{lib_syms_str}
\t)
{content}
)
"""

# =========================================================================
# ROOT SHEET
# =========================================================================
print("Writing Root Schematic (FV-CTRL_RevS3.kicad_sch)...")
root_content = f"""
\t(sheet (at 25.4 50.8) (size 101.6 38.1) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{uid()}")
\t\t(property "Sheetname" "1. Power Supply" (at 25.4 48.26 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
\t\t(property "Sheetfile" "FV-CTRL_RevS3-01.kicad_sch" (at 25.4 91.44 0) (effects (font (size 1.016 1.016)) (justify left top))))
\t(sheet (at 152.4 50.8) (size 101.6 38.1) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{uid()}")
\t\t(property "Sheetname" "2. MCU ESP32-S3 & USB Type-C" (at 152.4 48.26 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
\t\t(property "Sheetfile" "FV-CTRL_RevS3-02.kicad_sch" (at 152.4 91.44 0) (effects (font (size 1.016 1.016)) (justify left top))))
\t(sheet (at 279.4 50.8) (size 101.6 38.1) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{uid()}")
\t\t(property "Sheetname" "3. Servo 4x PWM" (at 279.4 48.26 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
\t\t(property "Sheetfile" "FV-CTRL_RevS3-03.kicad_sch" (at 279.4 91.44 0) (effects (font (size 1.016 1.016)) (justify left top))))
\t(sheet (at 25.4 114.3) (size 101.6 38.1) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{uid()}")
\t\t(property "Sheetname" "4. Universal Drop Sensors" (at 25.4 111.76 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
\t\t(property "Sheetfile" "FV-CTRL_RevS3-04.kicad_sch" (at 25.4 154.94 0) (effects (font (size 1.016 1.016)) (justify left top))))
\t(sheet (at 152.4 114.3) (size 101.6 38.1) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{uid()}")
\t\t(property "Sheetname" "5. Diagnostics & Spares" (at 152.4 111.76 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
\t\t(property "Sheetfile" "FV-CTRL_RevS3-05.kicad_sch" (at 152.4 154.94 0) (effects (font (size 1.016 1.016)) (justify left top))))
"""
(OUT_DIR / "FV-CTRL_RevS3.kicad_sch").write_text(make_sheet("FreshVend Rev-S3 - Index", ["power:PWR_FLAG"], root_content), encoding="utf-8")

# =========================================================================
# SHEET 1: Power Supply (FV-CTRL_RevS3-01.kicad_sch)
# =========================================================================
print("Writing Sheet 1: Power Supply...")
s1_syms = ["Connector_Generic:Conn_01x02", "Connector_Generic:Conn_01x04", "Device:Fuse", "Device:Polyfuse",
           "Device:D_TVS", "Device:D_Schottky", "Device:C", "Device:C_Polarized", "fv_revb:RECOM_R78E5V1A",
           "fv_revb:LD1117V33", "power:PWR_FLAG", "power:GND", "power:+12V", "power:+5V", "power:+3V3"]
s1_content = []

# J1: 12V In (at 50.8, 50.8)
s1_content.append(format_symbol_instance("Connector_Generic:Conn_01x02", "J1", "12V INPUT", "Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal", 50.8, 50.8))
j1_p1 = get_pin_pos("Connector_Generic:Conn_01x02", 1, 50.8, 50.8)
j1_p2 = get_pin_pos("Connector_Generic:Conn_01x02", 2, 50.8, 50.8)
s1_content.append(format_global_label("+12V_IN", j1_p1[0], j1_p1[1], 180))
s1_content.append(format_global_label("GND", j1_p2[0], j1_p2[1], 180))

# F1: Fuse 5A (at 76.2, 50.8, rot=90)
s1_content.append(format_symbol_instance("Device:Fuse", "F1", "5A 250V", "Fuse:Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open", 76.2, 50.8, 90))
f1_p1 = get_pin_pos("Device:Fuse", 1, 76.2, 50.8, 90)
f1_p2 = get_pin_pos("Device:Fuse", 2, 76.2, 50.8, 90)
s1_content.append(format_wire(f1_p1[0], f1_p1[1], f1_p1[0] - 5.08, f1_p1[1]))
s1_content.append(format_global_label("+12V_IN", f1_p1[0] - 5.08, f1_p1[1], 180))

# D1 TVS SMBJ12A (at 101.6, 63.5)
s1_content.append(format_symbol_instance("Device:D_TVS", "D1", "SMBJ12A", "Diode_SMD:D_SMB", 101.6, 63.5))
d1_p1 = get_pin_pos("Device:D_TVS", 1, 101.6, 63.5) # cathode
d1_p2 = get_pin_pos("Device:D_TVS", 2, 101.6, 63.5) # anode
s1_content.append(format_wire(f1_p2[0], f1_p2[1], d1_p1[0], f1_p2[1]))
s1_content.append(format_wire(d1_p1[0], f1_p2[1], d1_p1[0], d1_p1[1]))
s1_content.append(format_global_label("GND", d1_p2[0], d1_p2[1], 0))

# D7 Schottky SS54 (at 127.0, 50.8, rot=90)
s1_content.append(format_symbol_instance("Device:D_Schottky", "D7", "SS54", "Diode_SMD:D_SMC", 127.0, 50.8, 90))
d7_p1 = get_pin_pos("Device:D_Schottky", 1, 127.0, 50.8, 90) # cathode
d7_p2 = get_pin_pos("Device:D_Schottky", 2, 127.0, 50.8, 90) # anode
s1_content.append(format_wire(d1_p1[0], f1_p2[1], d7_p2[0], f1_p2[1]))
s1_content.append(format_wire(d7_p2[0], f1_p2[1], d7_p2[0], d7_p2[1]))
s1_content.append(format_wire(d7_p1[0], d7_p1[1], d7_p1[0] + 5.08, d7_p1[1]))
s1_content.append(format_global_label("+12V", d7_p1[0] + 5.08, d7_p1[1], 0))

# J4: RECOM R-78E5.0-1.0 (at 165.1, 50.8)
s1_content.append(format_symbol_instance("fv_revb:RECOM_R78E5V1A", "J4", "5V R-78E5.0-1.0", "fv_modules:RECOM_R78E5V1A", 165.1, 50.8))
j4_p1 = get_pin_pos("fv_revb:RECOM_R78E5V1A", 1, 165.1, 50.8) # VIN
j4_p2 = get_pin_pos("fv_revb:RECOM_R78E5V1A", 2, 165.1, 50.8) # GND
j4_p3 = get_pin_pos("fv_revb:RECOM_R78E5V1A", 3, 165.1, 50.8) # VOUT_5V
s1_content.append(format_global_label("+12V", j4_p1[0], j4_p1[1], 180))
s1_content.append(format_global_label("GND", j4_p2[0], j4_p2[1], 180))
s1_content.append(format_global_label("+5V", j4_p3[0], j4_p3[1], 180))

# C57: 10uF on 12V (at 152.4, 76.2)
s1_content.append(format_symbol_instance("Device:C_Polarized", "C57", "10uF 50V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", 152.4, 76.2))
c57_p1 = get_pin_pos("Device:C_Polarized", 1, 152.4, 76.2)
c57_p2 = get_pin_pos("Device:C_Polarized", 2, 152.4, 76.2)
s1_content.append(format_global_label("+12V", c57_p1[0], c57_p1[1], 180))
s1_content.append(format_global_label("GND", c57_p2[0], c57_p2[1], 180))

# C58: 100nF on 5V (at 177.8, 76.2)
s1_content.append(format_symbol_instance("Device:C", "C58", "100nF", "Capacitor_SMD:C_0603_1608Metric", 177.8, 76.2))
c58_p1 = get_pin_pos("Device:C", 1, 177.8, 76.2)
c58_p2 = get_pin_pos("Device:C", 2, 177.8, 76.2)
s1_content.append(format_global_label("+5V", c58_p1[0], c58_p1[1], 180))
s1_content.append(format_global_label("GND", c58_p2[0], c58_p2[1], 180))

# U3: LD1117S33 (at 215.9, 50.8)
s1_content.append(format_symbol_instance("fv_revb:LD1117V33", "U3", "LD1117S33", "Package_TO_SOT_SMD:SOT-223-3_TabPin2", 215.9, 50.8))
u3_p1 = get_pin_pos("fv_revb:LD1117V33", 1, 215.9, 50.8) # GND
u3_p2 = get_pin_pos("fv_revb:LD1117V33", 2, 215.9, 50.8) # VOUT_3V3
u3_p3 = get_pin_pos("fv_revb:LD1117V33", 3, 215.9, 50.8) # VIN_5V
s1_content.append(format_global_label("GND", u3_p1[0], u3_p1[1], 180))
s1_content.append(format_global_label("+3V3", u3_p2[0], u3_p2[1], 180))
s1_content.append(format_global_label("+5V", u3_p3[0], u3_p3[1], 0))

# C6 (10uF) & C7 (100nF) on 3.3V
s1_content.append(format_symbol_instance("Device:C", "C6", "10uF", "Capacitor_SMD:C_0603_1608Metric", 236.22, 76.2))
c6_p1 = get_pin_pos("Device:C", 1, 236.22, 76.2)
c6_p2 = get_pin_pos("Device:C", 2, 236.22, 76.2)
s1_content.append(format_global_label("+3V3", c6_p1[0], c6_p1[1], 180))
s1_content.append(format_global_label("GND", c6_p2[0], c6_p2[1], 180))

# J2 & J3: Buck A & B Terminals (at 279.4, 50.8 and 330.2, 50.8)
s1_content.append(format_symbol_instance("Connector_Generic:Conn_01x04", "J2", "XL4015 A", "Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_4-G-5,08_1x04_P5.08mm_Horizontal", 279.4, 50.8))
j2_p1 = get_pin_pos("Connector_Generic:Conn_01x04", 1, 279.4, 50.8)
j2_p2 = get_pin_pos("Connector_Generic:Conn_01x04", 2, 279.4, 50.8)
j2_p3 = get_pin_pos("Connector_Generic:Conn_01x04", 3, 279.4, 50.8)
j2_p4 = get_pin_pos("Connector_Generic:Conn_01x04", 4, 279.4, 50.8)
s1_content.append(format_global_label("+12V", j2_p1[0], j2_p1[1], 180))
s1_content.append(format_global_label("GND", j2_p2[0], j2_p2[1], 180))
s1_content.append(format_global_label("+6V_A_RAW", j2_p3[0], j2_p3[1], 180))
s1_content.append(format_global_label("GND", j2_p4[0], j2_p4[1], 180))

s1_content.append(format_symbol_instance("Connector_Generic:Conn_01x04", "J3", "XL4015 B", "Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_4-G-5,08_1x04_P5.08mm_Horizontal", 330.2, 50.8))
j3_p1 = get_pin_pos("Connector_Generic:Conn_01x04", 1, 330.2, 50.8)
j3_p2 = get_pin_pos("Connector_Generic:Conn_01x04", 2, 330.2, 50.8)
j3_p3 = get_pin_pos("Connector_Generic:Conn_01x04", 3, 330.2, 50.8)
j3_p4 = get_pin_pos("Connector_Generic:Conn_01x04", 4, 330.2, 50.8)
s1_content.append(format_global_label("+12V", j3_p1[0], j3_p1[1], 180))
s1_content.append(format_global_label("GND", j3_p2[0], j3_p2[1], 180))
s1_content.append(format_global_label("+6V_B_RAW", j3_p3[0], j3_p3[1], 180))
s1_content.append(format_global_label("GND", j3_p4[0], j3_p4[1], 180))

# F2 & F3: PTC MF-R300 (at 279.4, 88.9 and 330.2, 88.9)
s1_content.append(format_symbol_instance("Device:Polyfuse", "F2", "PTC 2.5A", "Fuse:Fuse_Bourns_MF-RHT300", 279.4, 88.9))
f2_p1 = get_pin_pos("Device:Polyfuse", 1, 279.4, 88.9)
f2_p2 = get_pin_pos("Device:Polyfuse", 2, 279.4, 88.9)
s1_content.append(format_global_label("+6V_A_RAW", f2_p1[0], f2_p1[1], 180))
s1_content.append(format_global_label("+6V_A", f2_p2[0], f2_p2[1], 180))

s1_content.append(format_symbol_instance("Device:Polyfuse", "F3", "PTC 2.5A", "Fuse:Fuse_Bourns_MF-RHT300", 330.2, 88.9))
f3_p1 = get_pin_pos("Device:Polyfuse", 1, 330.2, 88.9)
f3_p2 = get_pin_pos("Device:Polyfuse", 2, 330.2, 88.9)
s1_content.append(format_global_label("+6V_B_RAW", f3_p1[0], f3_p1[1], 180))
s1_content.append(format_global_label("+6V_B", f3_p2[0], f3_p2[1], 180))

# C1 & C2: 2200uF Bulk Caps on 6V_A & 6V_B
s1_content.append(format_symbol_instance("Device:C_Polarized", "C1", "2200uF 25V", "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm", 279.4, 114.3))
c1_p1 = get_pin_pos("Device:C_Polarized", 1, 279.4, 114.3)
c1_p2 = get_pin_pos("Device:C_Polarized", 2, 279.4, 114.3)
s1_content.append(format_global_label("+6V_A", c1_p1[0], c1_p1[1], 180))
s1_content.append(format_global_label("GND", c1_p2[0], c1_p2[1], 180))

s1_content.append(format_symbol_instance("Device:C_Polarized", "C2", "2200uF 25V", "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm", 330.2, 114.3))
c2_p1 = get_pin_pos("Device:C_Polarized", 1, 330.2, 114.3)
c2_p2 = get_pin_pos("Device:C_Polarized", 2, 330.2, 114.3)
s1_content.append(format_global_label("+6V_B", c2_p1[0], c2_p1[1], 180))
s1_content.append(format_global_label("GND", c2_p2[0], c2_p2[1], 180))

# PWR_FLAGs for Sheet 1 (Note: U3 pin 2 provides +3V3 Power Output, so +3V3 does not get PWR_FLAG)
flags = [("+12V_IN", 40.64, 40.64), ("GND", 40.64, 63.5), ("+12V", 116.84, 35.56), ("+5V", 154.94, 35.56), ("+6V_A", 279.4, 76.2), ("+6V_B", 330.2, 76.2)]
for net, fx, fy in flags:
    s1_content.append(format_symbol_instance("power:PWR_FLAG", f"#PWR_{net.replace('+', '').replace('_', '')}", "PWR_FLAG", "", fx, fy))
    pflg_p1 = get_pin_pos("power:PWR_FLAG", 1, fx, fy)
    s1_content.append(format_wire(pflg_p1[0], pflg_p1[1], pflg_p1[0] - 5.08, pflg_p1[1]))
    s1_content.append(format_global_label(net, pflg_p1[0] - 5.08, pflg_p1[1], 180))

(OUT_DIR / "FV-CTRL_RevS3-01.kicad_sch").write_text(make_sheet("1. Power Supply", s1_syms, "\n".join(s1_content)), encoding="utf-8")

# =========================================================================
# SHEET 2: MCU ESP32-S3 & USB Type-C (FV-CTRL_RevS3-02.kicad_sch)
# =========================================================================
print("Writing Sheet 2: MCU & USB Type-C...")
s2_syms = ["RF_Module:ESP32-S3-WROOM-1", "Connector:USB_C_Receptacle_USB2.0_16P", "Device:R", "Device:C",
           "Switch:SW_Push", "power:GND", "power:+3V3", "power:+5V"]
s2_content = []

# U1: ESP32-S3-WROOM-1 (at 203.2, 101.6)
s2_content.append(format_symbol_instance("RF_Module:ESP32-S3-WROOM-1", "U1", "ESP32-S3-WROOM-1U", "RF_Module:ESP32-S3-WROOM-1U", 203.2, 101.6))

# Map connected pins
s3_pins = {
    1: ("GND", 180), 2: ("+3V3", 180), 3: ("ESP_EN", 180),
    4: ("DROP_SENS1", 180), 5: ("DROP_SENS2", 180), 6: ("LIMIT_1_TOP", 180), 7: ("LIMIT_1_BOT", 180),
    9: ("S1_TOP_PWM", 180), 10: ("S1_BOT_PWM", 180), 11: ("S2_TOP_PWM", 180),
    12: ("LIMIT_2_TOP", 180), 13: ("USB_DM_S3", 180), 14: ("USB_DP_S3", 180),
    17: ("LIMIT_2_BOT", 0), 22: ("S2_BOT_PWM", 0), 23: ("DROP_TRIG", 0), 27: ("ESP_BOOT", 0),
    36: ("UART_RX_DEBUG", 0), 37: ("UART_TX_DEBUG", 0), 38: ("I2C_SCL", 0), 39: ("I2C_SDA", 0),
    40: ("GND", 0), 41: ("GND", 0)
}

# Connect active pins, add no-connect to all remaining pins
all_s3_pin_nums = [str(i) for i in range(1, 42)]
for pstr in all_s3_pin_nums:
    pnum = int(pstr)
    pos = get_pin_pos("RF_Module:ESP32-S3-WROOM-1", pnum, 203.2, 101.6)
    if pnum in s3_pins:
        net, rot = s3_pins[pnum]
        wx = pos[0] - 5.08 if rot == 180 else pos[0] + 5.08
        s2_content.append(format_wire(pos[0], pos[1], wx, pos[1]))
        s2_content.append(format_global_label(net, wx, pos[1], rot))
    else:
        # Unused pin -> mark with no_connect
        s2_content.append(format_no_connect(pos[0], pos[1]))

# USB Type-C J21 (at 63.5, 63.5)
s2_content.append(format_symbol_instance("Connector:USB_C_Receptacle_USB2.0_16P", "J21", "USB_C_16P", "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", 63.5, 63.5))
usbc_p_gnd = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "A1", 63.5, 63.5)
usbc_p_vbus = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "A4", 63.5, 63.5)
usbc_p_cc1 = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "A5", 63.5, 63.5)
usbc_p_cc2 = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "B5", 63.5, 63.5)
usbc_p_dpa = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "A6", 63.5, 63.5)
usbc_p_dpb = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "B6", 63.5, 63.5)
usbc_p_dma = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "A7", 63.5, 63.5)
usbc_p_dmb = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "B7", 63.5, 63.5)
usbc_p_sbu1 = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "A8", 63.5, 63.5)
usbc_p_sbu2 = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "B8", 63.5, 63.5)
usbc_p_shld = get_pin_pos("Connector:USB_C_Receptacle_USB2.0_16P", "SH", 63.5, 63.5)

# Connect GND, SHIELD, and mark VBUS as No Connect (FreshVend is DC powered)
s2_content.append(format_global_label("GND", usbc_p_gnd[0] - 5.08, usbc_p_gnd[1], 180))
s2_content.append(format_wire(usbc_p_gnd[0], usbc_p_gnd[1], usbc_p_gnd[0] - 5.08, usbc_p_gnd[1]))
s2_content.append(format_no_connect(usbc_p_vbus[0], usbc_p_vbus[1]))
s2_content.append(format_wire(usbc_p_shld[0], usbc_p_shld[1], usbc_p_shld[0] - 5.08, usbc_p_shld[1]))
s2_content.append(format_global_label("GND", usbc_p_shld[0] - 5.08, usbc_p_shld[1], 180))

# SBU1 and SBU2: No Connect
s2_content.append(format_no_connect(usbc_p_sbu1[0], usbc_p_sbu1[1]))
s2_content.append(format_no_connect(usbc_p_sbu2[0], usbc_p_sbu2[1]))

# Resistors for CC1 & CC2 5.1k
s2_content.append(format_symbol_instance("Device:R", "R14", "5.1k", "Resistor_SMD:R_0603_1608Metric", 43.18, 88.9))
r14_p1 = get_pin_pos("Device:R", 1, 43.18, 88.9)
r14_p2 = get_pin_pos("Device:R", 2, 43.18, 88.9)
s2_content.append(format_wire(usbc_p_cc1[0], usbc_p_cc1[1], r14_p1[0], usbc_p_cc1[1]))
s2_content.append(format_wire(r14_p1[0], usbc_p_cc1[1], r14_p1[0], r14_p1[1]))
s2_content.append(format_global_label("GND", r14_p2[0], r14_p2[1], 0))

s2_content.append(format_symbol_instance("Device:R", "R15", "5.1k", "Resistor_SMD:R_0603_1608Metric", 55.88, 88.9))
r15_p1 = get_pin_pos("Device:R", 1, 55.88, 88.9)
r15_p2 = get_pin_pos("Device:R", 2, 55.88, 88.9)
s2_content.append(format_wire(usbc_p_cc2[0], usbc_p_cc2[1], r15_p1[0], usbc_p_cc2[1]))
s2_content.append(format_wire(r15_p1[0], usbc_p_cc2[1], r15_p1[0], r15_p1[1]))
s2_content.append(format_global_label("GND", r15_p2[0], r15_p2[1], 0))

# Connect D- (A7 & B7 joined) -> R11 22R
s2_content.append(format_wire(usbc_p_dmb[0], usbc_p_dmb[1], usbc_p_dma[0], usbc_p_dmb[1]))
s2_content.append(format_wire(usbc_p_dma[0], usbc_p_dmb[1], usbc_p_dma[0], usbc_p_dma[1]))

s2_content.append(format_symbol_instance("Device:R", "R11", "22R", "Resistor_SMD:R_0603_1608Metric", 96.52, 60.96, 90))
r11_p1 = get_pin_pos("Device:R", 1, 96.52, 60.96, 90)
r11_p2 = get_pin_pos("Device:R", 2, 96.52, 60.96, 90)
s2_content.append(format_wire(usbc_p_dma[0], usbc_p_dma[1], r11_p1[0], usbc_p_dma[1]))
s2_content.append(format_wire(r11_p1[0], usbc_p_dma[1], r11_p1[0], r11_p1[1]))
s2_content.append(format_global_label("USB_DM_S3", r11_p2[0] + 5.08, r11_p2[1], 0))
s2_content.append(format_wire(r11_p2[0], r11_p2[1], r11_p2[0] + 5.08, r11_p2[1]))

# Connect D+ (A6 & B6 joined) -> R12 22R
s2_content.append(format_wire(usbc_p_dpb[0], usbc_p_dpb[1], usbc_p_dpa[0], usbc_p_dpb[1]))
s2_content.append(format_wire(usbc_p_dpa[0], usbc_p_dpb[1], usbc_p_dpa[0], usbc_p_dpa[1]))

s2_content.append(format_symbol_instance("Device:R", "R12", "22R", "Resistor_SMD:R_0603_1608Metric", 96.52, 73.66, 90))
r12_p1 = get_pin_pos("Device:R", 1, 96.52, 73.66, 90)
r12_p2 = get_pin_pos("Device:R", 2, 96.52, 73.66, 90)
s2_content.append(format_wire(usbc_p_dpa[0], usbc_p_dpa[1], r12_p1[0], usbc_p_dpa[1]))
s2_content.append(format_wire(r12_p1[0], usbc_p_dpa[1], r12_p1[0], r12_p1[1]))
s2_content.append(format_global_label("USB_DP_S3", r12_p2[0] + 5.08, r12_p2[1], 0))
s2_content.append(format_wire(r12_p2[0], r12_p2[1], r12_p2[0] + 5.08, r12_p2[1]))

# Reset SW1 (at 127.0, 114.3) & Boot SW2 (at 127.0, 144.78)
s2_content.append(format_symbol_instance("Switch:SW_Push", "SW1", "RESET", "Button_Switch_SMD:SW_Push_SPST_NO_Alps_SKRK", 127.0, 114.3))
sw1_p1 = get_pin_pos("Switch:SW_Push", 1, 127.0, 114.3)
sw1_p2 = get_pin_pos("Switch:SW_Push", 2, 127.0, 114.3)
s2_content.append(format_global_label("ESP_EN", sw1_p1[0] - 5.08, sw1_p1[1], 180))
s2_content.append(format_wire(sw1_p1[0], sw1_p1[1], sw1_p1[0] - 5.08, sw1_p1[1]))
s2_content.append(format_global_label("GND", sw1_p2[0] + 5.08, sw1_p2[1], 0))
s2_content.append(format_wire(sw1_p2[0], sw1_p2[1], sw1_p2[0] + 5.08, sw1_p2[1]))

s2_content.append(format_symbol_instance("Device:R", "R10", "10k", "Resistor_SMD:R_0603_1608Metric", 101.6, 106.68))
r10_p1 = get_pin_pos("Device:R", 1, 101.6, 106.68)
r10_p2 = get_pin_pos("Device:R", 2, 101.6, 106.68)
s2_content.append(format_global_label("+3V3", r10_p1[0], r10_p1[1], 180))
s2_content.append(format_global_label("ESP_EN", r10_p2[0], r10_p2[1], 180))

s2_content.append(format_symbol_instance("Device:C", "C10", "1uF", "Capacitor_SMD:C_0603_1608Metric", 101.6, 121.92))
c10_p1 = get_pin_pos("Device:C", 1, 101.6, 121.92)
c10_p2 = get_pin_pos("Device:C", 2, 101.6, 121.92)
s2_content.append(format_global_label("ESP_EN", c10_p1[0], c10_p1[1], 180))
s2_content.append(format_global_label("GND", c10_p2[0], c10_p2[1], 180))

# Boot SW2
s2_content.append(format_symbol_instance("Switch:SW_Push", "SW2", "BOOT", "Button_Switch_SMD:SW_Push_SPST_NO_Alps_SKRK", 127.0, 144.78))
sw2_p1 = get_pin_pos("Switch:SW_Push", 1, 127.0, 144.78)
sw2_p2 = get_pin_pos("Switch:SW_Push", 2, 127.0, 144.78)
s2_content.append(format_global_label("ESP_BOOT", sw2_p1[0] - 5.08, sw2_p1[1], 180))
s2_content.append(format_wire(sw2_p1[0], sw2_p1[1], sw2_p1[0] - 5.08, sw2_p1[1]))
s2_content.append(format_global_label("GND", sw2_p2[0] + 5.08, sw2_p2[1], 0))
s2_content.append(format_wire(sw2_p2[0], sw2_p2[1], sw2_p2[0] + 5.08, sw2_p2[1]))

(OUT_DIR / "FV-CTRL_RevS3-02.kicad_sch").write_text(make_sheet("2. MCU ESP32-S3 & USB Type-C", s2_syms, "\n".join(s2_content)), encoding="utf-8")

# =========================================================================
# SHEET 3: Servo 4x PWM (FV-CTRL_RevS3-03.kicad_sch)
# =========================================================================
print("Writing Sheet 3: Servo 4x PWM...")
s3_syms = ["Connector_Generic:Conn_01x03", "Device:R", "power:GND"]
s3_content = []

servos = [
    ("J5", "S1_TOP", "S1_TOP_PWM", "+6V_A", "R1", "R2", 63.5),
    ("J6", "S1_BOT", "S1_BOT_PWM", "+6V_A", "R3", "R4", 93.98),
    ("J7", "S2_TOP", "S2_TOP_PWM", "+6V_B", "R5", "R6", 124.46),
    ("J8", "S2_BOT", "S2_BOT_PWM", "+6V_B", "R7", "R8", 154.94)
]
for ref, name, sig_net, pwr_rail, r_ser, r_pd, y in servos:
    s3_content.append(format_symbol_instance("Connector_Generic:Conn_01x03", ref, name, "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", 127.0, y))
    p1 = get_pin_pos("Connector_Generic:Conn_01x03", 1, 127.0, y) # GND
    p2 = get_pin_pos("Connector_Generic:Conn_01x03", 2, 127.0, y) # V+
    p3 = get_pin_pos("Connector_Generic:Conn_01x03", 3, 127.0, y) # SIG
    s3_content.append(format_global_label("GND", p1[0] - 5.08, p1[1], 180))
    s3_content.append(format_wire(p1[0], p1[1], p1[0] - 5.08, p1[1]))
    s3_content.append(format_global_label(pwr_rail, p2[0] - 5.08, p2[1], 180))
    s3_content.append(format_wire(p2[0], p2[1], p2[0] - 5.08, p2[1]))

    # Series 330R (rot=90)
    s3_content.append(format_symbol_instance("Device:R", r_ser, "330R", "Resistor_SMD:R_0603_1608Metric", 88.9, y, 90))
    rs_p1 = get_pin_pos("Device:R", 1, 88.9, y, 90)
    rs_p2 = get_pin_pos("Device:R", 2, 88.9, y, 90)
    s3_content.append(format_wire(p3[0], p3[1], rs_p2[0], rs_p2[1]))
    s3_content.append(format_global_label(sig_net, rs_p1[0] - 5.08, rs_p1[1], 180))
    s3_content.append(format_wire(rs_p1[0], rs_p1[1], rs_p1[0] - 5.08, rs_p1[1]))

    # Pull-down 10k (at 63.5, y + 10.16)
    s3_content.append(format_symbol_instance("Device:R", r_pd, "10k", "Resistor_SMD:R_0603_1608Metric", 63.5, y + 10.16))
    rpd_p1 = get_pin_pos("Device:R", 1, 63.5, y + 10.16)
    rpd_p2 = get_pin_pos("Device:R", 2, 63.5, y + 10.16)
    s3_content.append(format_global_label(sig_net, rpd_p1[0], rpd_p1[1], 180))
    s3_content.append(format_global_label("GND", rpd_p2[0], rpd_p2[1], 180))

(OUT_DIR / "FV-CTRL_RevS3-03.kicad_sch").write_text(make_sheet("3. Servo 4x PWM", s3_syms, "\n".join(s3_content)), encoding="utf-8")

# =========================================================================
# SHEET 4: Universal Drop Sensors (FV-CTRL_RevS3-04.kicad_sch)
# =========================================================================
print("Writing Sheet 4: Universal Drop Sensors...")
s4_syms = ["Connector_Generic:Conn_01x04", "Device:R", "power:GND", "power:+5V"]
s4_content = []

sensors = [
    ("J11", "DROP SENSOR COL 1", "DROP_SENS1", "R16", "R17", 63.5),
    ("J12", "DROP SENSOR COL 2", "DROP_SENS2", "R18", "R19", 114.3)
]
for ref, name, out_net, r_div1, r_div2, y in sensors:
    # 4-pin header: 1=VCC(+5V), 2=TRIG, 3=RAW_SIG, 4=GND
    s4_content.append(format_symbol_instance("Connector_Generic:Conn_01x04", ref, name, "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", 76.2, y))
    p1 = get_pin_pos("Connector_Generic:Conn_01x04", 1, 76.2, y)
    p2 = get_pin_pos("Connector_Generic:Conn_01x04", 2, 76.2, y)
    p3 = get_pin_pos("Connector_Generic:Conn_01x04", 3, 76.2, y)
    p4 = get_pin_pos("Connector_Generic:Conn_01x04", 4, 76.2, y)

    s4_content.append(format_global_label("+5V", p1[0] - 5.08, p1[1], 180))
    s4_content.append(format_wire(p1[0], p1[1], p1[0] - 5.08, p1[1]))

    s4_content.append(format_global_label("DROP_TRIG", p2[0] - 5.08, p2[1], 180))
    s4_content.append(format_wire(p2[0], p2[1], p2[0] - 5.08, p2[1]))

    # Level shift / protection divider: R_div1 (1k series), R_div2 (2k pull-down)
    s4_content.append(format_symbol_instance("Device:R", r_div1, "1k", "Resistor_SMD:R_0603_1608Metric", 116.84, y, 90))
    rd1_p1 = get_pin_pos("Device:R", 1, 116.84, y, 90)
    rd1_p2 = get_pin_pos("Device:R", 2, 116.84, y, 90)
    s4_content.append(format_wire(p3[0], p3[1], rd1_p1[0], rd1_p1[1]))

    # R_div2 (rot=0)
    s4_content.append(format_symbol_instance("Device:R", r_div2, "2k", "Resistor_SMD:R_0603_1608Metric", rd1_p2[0] + 12.7, y + 10.16))
    rd2_p1 = get_pin_pos("Device:R", 1, rd1_p2[0] + 12.7, y + 10.16)
    rd2_p2 = get_pin_pos("Device:R", 2, rd1_p2[0] + 12.7, y + 10.16)

    # Wire from rd1_p2 to junction with rd2_p1 and output label
    s4_content.append(format_wire(rd1_p2[0], rd1_p2[1], rd2_p1[0], rd1_p2[1]))
    s4_content.append(format_wire(rd2_p1[0], rd1_p2[1], rd2_p1[0], rd2_p1[1]))
    s4_content.append(format_wire(rd2_p1[0], rd1_p2[1], rd2_p1[0] + 10.16, rd1_p2[1]))
    s4_content.append(format_global_label(out_net, rd2_p1[0] + 10.16, rd1_p2[1], 0))

    # GND on rd2_p2
    s4_content.append(format_wire(rd2_p2[0], rd2_p2[1], rd2_p2[0], rd2_p2[1] + 5.08))
    s4_content.append(format_global_label("GND", rd2_p2[0], rd2_p2[1] + 5.08, 0))

    # GND on p4
    s4_content.append(format_global_label("GND", p4[0] - 5.08, p4[1], 180))
    s4_content.append(format_wire(p4[0], p4[1], p4[0] - 5.08, p4[1]))

(OUT_DIR / "FV-CTRL_RevS3-04.kicad_sch").write_text(make_sheet("4. Universal Drop Sensors", s4_syms, "\n".join(s4_content)), encoding="utf-8")

# =========================================================================
# SHEET 5: Diagnostics & Spares (FV-CTRL_RevS3-05.kicad_sch)
# =========================================================================
print("Writing Sheet 5: Diagnostics & Spares...")
s5_syms = ["Device:LED", "Device:R", "Connector_Generic:Conn_01x02", "Connector_Generic:Conn_01x04",
           "Connector:TestPoint", "power:GND", "power:+12V", "power:+5V", "power:+3V3"]
s5_content = []

leds = [
    ("D2", "+12V", "+12V", "R21", "4.7k", 50.8),
    ("D3", "+6V_A", "+6V_A", "R22", "2.2k", 76.2),
    ("D4", "+6V_B", "+6V_B", "R23", "2.2k", 101.6),
    ("D5", "+5V", "+5V", "R24", "1.5k", 127.0),
    ("D6", "+3V3", "+3V3", "R25", "1k", 152.4)
]
for d_ref, d_val, rail, r_ref, r_val, y in leds:
    # LED
    s5_content.append(format_symbol_instance("Device:LED", d_ref, d_val, "LED_SMD:LED_0603_1608Metric", 76.2, y, 90))
    d_p1 = get_pin_pos("Device:LED", 1, 76.2, y, 90) # cathode
    d_p2 = get_pin_pos("Device:LED", 2, 76.2, y, 90) # anode

    # Resistor
    s5_content.append(format_symbol_instance("Device:R", r_ref, r_val, "Resistor_SMD:R_0603_1608Metric", 50.8, y, 90))
    r_p1 = get_pin_pos("Device:R", 1, 50.8, y, 90)
    r_p2 = get_pin_pos("Device:R", 2, 50.8, y, 90)

    s5_content.append(format_global_label(rail, r_p1[0] - 5.08, r_p1[1], 180))
    s5_content.append(format_wire(r_p1[0], r_p1[1], r_p1[0] - 5.08, r_p1[1]))
    s5_content.append(format_wire(r_p2[0], r_p2[1], d_p2[0], d_p2[1]))
    s5_content.append(format_global_label("GND", d_p1[0] + 5.08, d_p1[1], 0))
    s5_content.append(format_wire(d_p1[0], d_p1[1], d_p1[0] + 5.08, d_p1[1]))

# Test Points
tps = [
    ("TP1", "+12V", 139.7, 50.8), ("TP2", "+6V_A", 139.7, 66.04), ("TP3", "+6V_B", 139.7, 81.28),
    ("TP4", "+5V", 139.7, 96.52), ("TP5", "+3V3", 139.7, 111.76), ("TP6", "GND", 139.7, 127.0),
    ("TP7", "UART_TX_DEBUG", 139.7, 142.24), ("TP8", "UART_RX_DEBUG", 139.7, 157.48)
]
for tp_ref, tp_val, tx, ty in tps:
    s5_content.append(format_symbol_instance("Connector:TestPoint", tp_ref, tp_val, "TestPoint:TestPoint_Pad_D1.5mm", tx, ty))
    t_p = get_pin_pos("Connector:TestPoint", 1, tx, ty)
    s5_content.append(format_global_label(tp_val, t_p[0] - 5.08, t_p[1], 180))
    s5_content.append(format_wire(t_p[0], t_p[1], t_p[0] - 5.08, t_p[1]))

# I2C Header J9 (at 203.2, 63.5)
s5_content.append(format_symbol_instance("Connector_Generic:Conn_01x04", "J9", "I2C SPARE", "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", 203.2, 63.5))
j9_p1 = get_pin_pos("Connector_Generic:Conn_01x04", 1, 203.2, 63.5)
j9_p2 = get_pin_pos("Connector_Generic:Conn_01x04", 2, 203.2, 63.5)
j9_p3 = get_pin_pos("Connector_Generic:Conn_01x04", 3, 203.2, 63.5)
j9_p4 = get_pin_pos("Connector_Generic:Conn_01x04", 4, 203.2, 63.5)
s5_content.append(format_global_label("+3V3", j9_p1[0] - 5.08, j9_p1[1], 180))
s5_content.append(format_wire(j9_p1[0], j9_p1[1], j9_p1[0] - 5.08, j9_p1[1]))
s5_content.append(format_global_label("I2C_SDA", j9_p2[0] - 5.08, j9_p2[1], 180))
s5_content.append(format_wire(j9_p2[0], j9_p2[1], j9_p2[0] - 5.08, j9_p2[1]))
s5_content.append(format_global_label("I2C_SCL", j9_p3[0] - 5.08, j9_p3[1], 180))
s5_content.append(format_wire(j9_p3[0], j9_p3[1], j9_p3[0] - 5.08, j9_p3[1]))
s5_content.append(format_global_label("GND", j9_p4[0] - 5.08, j9_p4[1], 180))
s5_content.append(format_wire(j9_p4[0], j9_p4[1], j9_p4[0] - 5.08, j9_p4[1]))

# Limit Switches Header J10 (at 279.4, 63.5)
s5_content.append(format_symbol_instance("Connector_Generic:Conn_01x04", "J10", "LIMIT SWITCHES", "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", 279.4, 63.5))
j10_p1 = get_pin_pos("Connector_Generic:Conn_01x04", 1, 279.4, 63.5)
j10_p2 = get_pin_pos("Connector_Generic:Conn_01x04", 2, 279.4, 63.5)
j10_p3 = get_pin_pos("Connector_Generic:Conn_01x04", 3, 279.4, 63.5)
j10_p4 = get_pin_pos("Connector_Generic:Conn_01x04", 4, 279.4, 63.5)
s5_content.append(format_global_label("LIMIT_1_TOP", j10_p1[0] - 5.08, j10_p1[1], 180))
s5_content.append(format_wire(j10_p1[0], j10_p1[1], j10_p1[0] - 5.08, j10_p1[1]))
s5_content.append(format_global_label("LIMIT_1_BOT", j10_p2[0] - 5.08, j10_p2[1], 180))
s5_content.append(format_wire(j10_p2[0], j10_p2[1], j10_p2[0] - 5.08, j10_p2[1]))
s5_content.append(format_global_label("LIMIT_2_TOP", j10_p3[0] - 5.08, j10_p3[1], 180))
s5_content.append(format_wire(j10_p3[0], j10_p3[1], j10_p3[0] - 5.08, j10_p3[1]))
s5_content.append(format_global_label("LIMIT_2_BOT", j10_p4[0] - 5.08, j10_p4[1], 180))
s5_content.append(format_wire(j10_p4[0], j10_p4[1], j10_p4[0] - 5.08, j10_p4[1]))

# Pullups for I2C (R26, R27 4.7k)
s5_content.append(format_symbol_instance("Device:R", "R26", "4.7k", "Resistor_SMD:R_0603_1608Metric", 228.6, 50.8))
r26_p1 = get_pin_pos("Device:R", 1, 228.6, 50.8)
r26_p2 = get_pin_pos("Device:R", 2, 228.6, 50.8)
s5_content.append(format_global_label("+3V3", r26_p1[0], r26_p1[1], 180))
s5_content.append(format_global_label("I2C_SDA", r26_p2[0], r26_p2[1], 180))

s5_content.append(format_symbol_instance("Device:R", "R27", "4.7k", "Resistor_SMD:R_0603_1608Metric", 243.84, 50.8))
r27_p1 = get_pin_pos("Device:R", 1, 243.84, 50.8)
r27_p2 = get_pin_pos("Device:R", 2, 243.84, 50.8)
s5_content.append(format_global_label("+3V3", r27_p1[0], r27_p1[1], 180))
s5_content.append(format_global_label("I2C_SCL", r27_p2[0], r27_p2[1], 180))

(OUT_DIR / "FV-CTRL_RevS3-05.kicad_sch").write_text(make_sheet("5. Diagnostics & Spares", s5_syms, "\n".join(s5_content)), encoding="utf-8")
print("All 5 sheets + root successfully written to:", OUT_DIR)
