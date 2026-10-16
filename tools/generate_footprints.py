"""Generate verified custom footprints for FV-CTRL modules and configure fp-lib-table."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBS = ROOT / "libs" / "fv_modules.pretty"
HARDWARE = ROOT / "hardware"
LIBS.mkdir(parents=True, exist_ok=True)


def gen_xh_m401():
    """Footprint for XH-M401 (XL4016E1 8A 200W DC-DC Buck Module).
    Module size: 61mm x 41mm.
    4x M3 mounting holes: 58mm x 26mm pitch.
    4 connection pads: IN+, IN- (GND), OUT+ (6V), OUT- (GND) with 5.08mm KF301 terminal pitch.
    """
    fp = """(footprint "Converter_DCDC_XH-M401_8A"
	(version 20240108)
	(generator "fv_pcb_tools")
	(layer "F.Cu")
	(descr "XH-M401 XL4016E1 8A 200W DC-DC Step-Down Buck Converter Module (61x41mm, 4x M3 holes)")
	(tags "DC-DC Buck Converter XL4016 8A XH-M401")
	(property "Reference" "REF**"
		(at 0 -22.5 0)
		(layer "F.SilkS")
		(effects (font (size 1.2 1.2) (thickness 0.15)))
	)
	(property "Value" "Converter_DCDC_XH-M401_8A"
		(at 0 22.5 0)
		(layer "F.Fab")
		(effects (font (size 1.2 1.2) (thickness 0.15)))
	)
	(fp_line (start -30.5 -20.5) (end 30.5 -20.5) (layer "F.Fab") (width 0.15))
	(fp_line (start 30.5 -20.5) (end 30.5 20.5) (layer "F.Fab") (width 0.15))
	(fp_line (start 30.5 20.5) (end -30.5 20.5) (layer "F.Fab") (width 0.15))
	(fp_line (start -30.5 20.5) (end -30.5 -20.5) (layer "F.Fab") (width 0.15))
	(fp_line (start -18.0 -12.0) (end 18.0 -12.0) (layer "F.Fab") (width 0.15))
	(fp_line (start 18.0 -12.0) (end 18.0 12.0) (layer "F.Fab") (width 0.15))
	(fp_line (start 18.0 12.0) (end -18.0 12.0) (layer "F.Fab") (width 0.15))
	(fp_line (start -18.0 12.0) (end -18.0 -12.0) (layer "F.Fab") (width 0.15))
	(fp_text user "HEATSINK & TOROID INDUCTOR" (at 0 0 0) (layer "F.Fab") (effects (font (size 0.9 0.9) (thickness 0.12))))
	(pad "" np_thru_hole circle (at -29.0 -13.0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))
	(pad "" np_thru_hole circle (at 29.0 -13.0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))
	(pad "" np_thru_hole circle (at -29.0 13.0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))
	(pad "" np_thru_hole circle (at 29.0 13.0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))
	(pad "1" thru_hole rect (at -27.0 -2.54 0) (size 3.0 3.0) (drill 1.5) (layers "*.Cu" "*.Mask"))
	(pad "2" thru_hole circle (at -27.0 2.54 0) (size 3.0 3.0) (drill 1.5) (layers "*.Cu" "*.Mask"))
	(pad "3" thru_hole rect (at 27.0 -2.54 0) (size 3.0 3.0) (drill 1.5) (layers "*.Cu" "*.Mask"))
	(pad "4" thru_hole circle (at 27.0 2.54 0) (size 3.0 3.0) (drill 1.5) (layers "*.Cu" "*.Mask"))
	(fp_text user "IN+" (at -27.0 -6.0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) bold)))
	(fp_text user "IN-" (at -27.0 6.0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) bold)))
	(fp_text user "OUT+" (at 27.0 -6.0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) bold)))
	(fp_text user "OUT-" (at 27.0 6.0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) bold)))
)
"""
    (LIBS / "Converter_DCDC_XH-M401_8A.kicad_mod").write_text(fp, encoding="utf-8")
    print(f"Generated footprint: {LIBS / 'Converter_DCDC_XH-M401_8A.kicad_mod'}")


def gen_mp1584en():
    """Footprint for MP1584EN (3A DC-DC Buck Converter Module 22.1x16.8mm).
    Standard 2.54mm socket header pads with dual-pin solder options per corner.
    """
    fp = """(footprint "Converter_DCDC_MP1584EN"
	(version 20240108)
	(generator "fv_pcb_tools")
	(layer "F.Cu")
	(descr "MP1584EN Mini 3A DC-DC Buck Converter Module (22.1x16.8mm, 2.54mm header interface)")
	(tags "DC-DC Buck Converter MP1584EN 5V Logic")
	(property "Reference" "REF**"
		(at 0 -10.0 0)
		(layer "F.SilkS")
		(effects (font (size 1.0 1.0) (thickness 0.15)))
	)
	(property "Value" "Converter_DCDC_MP1584EN"
		(at 0 10.0 0)
		(layer "F.Fab")
		(effects (font (size 1.0 1.0) (thickness 0.15)))
	)
	(fp_line (start -11.05 -8.4) (end 11.05 -8.4) (layer "F.Fab") (width 0.15))
	(fp_line (start 11.05 -8.4) (end 11.05 8.4) (layer "F.Fab") (width 0.15))
	(fp_line (start 11.05 8.4) (end -11.05 8.4) (layer "F.Fab") (width 0.15))
	(fp_line (start -11.05 8.4) (end -11.05 -8.4) (layer "F.Fab") (width 0.15))
	(fp_line (start 3.0 -6.5) (end 8.5 -6.5) (layer "F.Fab") (width 0.12))
	(fp_line (start 8.5 -6.5) (end 8.5 -2.0) (layer "F.Fab") (width 0.12))
	(fp_line (start 8.5 -2.0) (end 3.0 -2.0) (layer "F.Fab") (width 0.12))
	(fp_line (start 3.0 -2.0) (end 3.0 -6.5) (layer "F.Fab") (width 0.12))
	(fp_text user "ADJ" (at 5.75 -4.25 0) (layer "F.Fab") (effects (font (size 0.7 0.7) (thickness 0.1))))
	(pad "1" thru_hole rect (at -9.27 -5.08 0) (size 1.9 1.9) (drill 1.0) (layers "*.Cu" "*.Mask"))
	(pad "1" thru_hole circle (at -9.27 -2.54 0) (size 1.9 1.9) (drill 1.0) (layers "*.Cu" "*.Mask"))
	(pad "2" thru_hole circle (at -9.27 2.54 0) (size 1.9 1.9) (drill 1.0) (layers "*.Cu" "*.Mask"))
	(pad "2" thru_hole circle (at -9.27 5.08 0) (size 1.9 1.9) (drill 1.0) (layers "*.Cu" "*.Mask"))
	(pad "3" thru_hole rect (at 9.27 -5.08 0) (size 1.9 1.9) (drill 1.0) (layers "*.Cu" "*.Mask"))
	(pad "3" thru_hole circle (at 9.27 -2.54 0) (size 1.9 1.9) (drill 1.0) (layers "*.Cu" "*.Mask"))
	(pad "4" thru_hole circle (at 9.27 2.54 0) (size 1.9 1.9) (drill 1.0) (layers "*.Cu" "*.Mask"))
	(pad "4" thru_hole circle (at 9.27 5.08 0) (size 1.9 1.9) (drill 1.0) (layers "*.Cu" "*.Mask"))
	(fp_text user "IN+" (at -6.0 -3.81 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) bold)))
	(fp_text user "GND" (at -6.0 3.81 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) bold)))
	(fp_text user "+5V" (at 6.0 -3.81 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) bold)))
	(fp_text user "GND" (at 6.0 3.81 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) bold)))
)
"""
    (LIBS / "Converter_DCDC_MP1584EN.kicad_mod").write_text(fp, encoding="utf-8")
    print(f"Generated footprint: {LIBS / 'Converter_DCDC_MP1584EN.kicad_mod'}")


def gen_fp_lib_table():
    """Register libs/fv_modules.pretty in hardware/fp-lib-table."""
    content = """(fp_lib_table
  (version 7)
  (lib (name "fv_modules")(type "KiCad")(uri "${KIPRJMOD}/../libs/fv_modules.pretty")(options "")(descr "Custom breakout modules for FV-CTRL project"))
)
"""
    tbl = HARDWARE / "fp-lib-table"
    tbl.write_text(content, encoding="utf-8")
    print(f"Created fp-lib-table: {tbl}")


if __name__ == "__main__":
    gen_xh_m401()
    gen_mp1584en()
    gen_fp_lib_table()
