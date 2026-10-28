"""
Generator for FreshVend Hardware Rev-S3:
- ESP32-S3-WROOM-1U
- USB Type-C 16-pin Native (CC1/CC2 5.1k, D+/D- 22R)
- Dual Universal 4-Pin Drop Sensor Ports (Column 1 & 2)
- Industrial Power: RECOM R-78E5.0-1.0, LD1117S33, Dual XL4015 Servo 6V Rails, PTCs, Bulk Caps
- Clean Hierarchical KiCad 10 Schematic
"""
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "hardware/rev_s3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def gen_uuid():
    return str(uuid.uuid4())

def make_header(title, date="2026-10-28", rev="Rev-S3 - PROTOTYPE"):
    return f"""(kicad_sch
\t(version 20250114)
\t(generator "fv_native_s3_generator")
\t(generator_version "10.0")
\t(uuid "{gen_uuid()}")
\t(paper "A3")
\t(title_block
\t\t(title "{title}")
\t\t(date "{date}")
\t\t(rev "{rev}")
\t\t(company "FreshVend Project")
\t\t(comment 1 "ESP32-S3-WROOM-1U | USB Type-C | Universal Drop Sensor")
\t\t(comment 2 "2-Layer 0603 DFM Standard")
\t)
"""

print("Writing Rev-S3 generator...")
