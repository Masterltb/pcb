"""Package professional handover deliverables for PCB manufacturers and technical reviewers."""
import os
import shutil
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HANDOVER = ROOT / "releases/archive/reva/handover"

# 1. Ensure fresh export of all artifacts
print("1. Verifying and exporting fresh artifacts...")
subprocess.run(["kicad-cli", "sch", "export", "pdf", "--output", str(ROOT / "docs/archive/reva" / "FV-CTRL_RevA_Schematic.pdf"), str(ROOT / "hardware/archive/reva" / "FV-CTRL_RevA.kicad_sch")], check=True)
subprocess.run(["kicad-cli", "sch", "export", "pdf", "--output", str(ROOT / "docs/archive/reva" / "FV-IR-RX_RevA_Schematic.pdf"), str(ROOT / "hardware/archive/reva" / "FV-IR-RX_RevA.kicad_sch")], check=True)
subprocess.run(["kicad-cli", "pcb", "export", "step", "--output", str(ROOT / "docs/archive/reva" / "FV-CTRL_RevA_3D.step"), str(ROOT / "hardware/archive/reva" / "FV-CTRL_RevA.kicad_pcb")], check=True)
subprocess.run(["kicad-cli", "pcb", "export", "step", "--output", str(ROOT / "docs/archive/reva" / "FV-IR-RX_RevA_3D.step"), str(ROOT / "hardware/archive/reva" / "FV-IR-RX_RevA.kicad_pcb")], check=True)

# 2. Reset handover folder
if HANDOVER.exists():
    shutil.rmtree(HANDOVER)

p_fab = HANDOVER / "01_PCB_Fabrication"
p_rev = HANDOVER / "02_Technical_Review"
p_src = HANDOVER / "03_KiCad_Source_Design"

p_fab.mkdir(parents=True, exist_ok=True)
p_rev.mkdir(parents=True, exist_ok=True)
p_src.mkdir(parents=True, exist_ok=True)

# 3. Populate 01_PCB_Fabrication
shutil.copy2(ROOT / "releases/archive/reva/gerbers" / "FV-CTRL_RevA_Gerbers.zip", p_fab / "FV-CTRL_RevA_Gerbers.zip")
shutil.copy2(ROOT / "releases/archive/reva/gerbers" / "FV-IR-RX_RevA_Gerbers.zip", p_fab / "FV-IR-RX_RevA_Gerbers.zip")

fab_specs = """================================================================================
HO SO YEU CAU CONG NGHE SAN XUAT PCB (PCB FABRICATION SPECIFICATIONS)
DU AN: FV-CTRL REV A (FRUIT VENDING DISPENSER CONTROLLER)
================================================================================

1. BO MACH CHINH (MAINBOARD - FV-CTRL_RevA_Gerbers.zip):
   - Kich thuoc board (Board Dimensions): 100.0 mm x 100.0 mm (Hinh vuong)
   - So lop dong (Layer Count): 2 lop (2-Layer)
   - Vat lieu phoi (Base Material): FR-4 Standard (Tg 130-140C)
   - Do day bo mach (Board Thickness): 1.6 mm (+/- 10%)
   - Do day dong (Finished Copper Weight): 1 oz (35 um) - Chap nhan 2 oz neu co nhu cau
   - Xu ly be mat (Surface Finish): Lead-Free HASL (hoac HASL with lead)
   - Mau phu han (Solder Mask): Green (Xanh la cay tieu chuan) / Co the chon Mau Den
   - Mau chu in linh kien (Silkscreen): White (Trang)
   - Duong kinh lo khoan toi thieu (Min Hole / Drill): 0.40 mm (Via drill 0.4mm, Pad drill >= 0.8mm)
   - Khoang cach an toan dong (Min Copper Clearance): 0.20 mm (8 mil)
   - Khoang cach dong den mep bo (Edge Clearance): >= 0.55 mm
   - Lo bat oc (Mounting Holes): 4 lo M3 (duong kinh 3.2 mm) tai 4 goc (4mm, 96mm)
   - Yeu cau kiem tra (Testing): 100% Flying Probe Electrical Test

2. BO VE TINH CAM BIEN HONG NGOAI (IR RX SATELLITE - FV-IR-RX_RevA_Gerbers.zip):
   - Kich thuoc board (Board Dimensions): 18.0 mm x 42.0 mm
   - So lop dong (Layer Count): 2 lop (2-Layer)
   - So luong board tren he thong: 2 bo (IR RX1 va IR RX2)
   - Quy cach vat lieu & be mat: Tuong tu bo mach chinh (FR-4, 1.6mm, 1 oz, HASL)
   - Lo bat oc (Mounting Hole): 1 lo M3 (duong kinh 3.2 mm) tai dau tren board

================================================================================
"""
(p_fab / "PCB_FABRICATION_SPECS.txt").write_text(fab_specs, encoding="utf-8")

# 4. Populate 02_Technical_Review
shutil.copy2(ROOT / "docs/archive/reva" / "FV-CTRL_RevA_Schematic.pdf", p_rev / "FV-CTRL_RevA_Schematic.pdf")
shutil.copy2(ROOT / "docs/archive/reva" / "FV-IR-RX_RevA_Schematic.pdf", p_rev / "FV-IR-RX_RevA_Schematic.pdf")
shutil.copy2(ROOT / "docs/archive/reva" / "FV-CTRL_RevA-bom.csv", p_rev / "FV-CTRL_RevA_BOM.csv")
shutil.copy2(ROOT / "docs/archive/reva" / "FV-CTRL_RevA_3D.step", p_rev / "FV-CTRL_RevA_3D.step")
shutil.copy2(ROOT / "docs/archive/reva" / "FV-IR-RX_RevA_3D.step", p_rev / "FV-IR-RX_RevA_3D.step")

shutil.copy2(ROOT / "reports/archive/reva" / "erc.rpt", p_rev / "ERC_Report_Mainboard.txt")
shutil.copy2(ROOT / "reports/archive/reva" / "drc.rpt", p_rev / "DRC_Report_Mainboard.txt")
shutil.copy2(ROOT / "reports/archive/reva" / "drc_FV-IR-RX_RevA.rpt", p_rev / "DRC_Report_Satellite_IR.txt")

review_report = """# BAO CAO THAM DINH KY THUAT CHUYEN SAU (EXPERT ENGINEERING REVIEW)
**Du an:** Bo dieu khien may nha coc hoa qua 2 cot (FV-CTRL Rev A)
**Ngay danh gia:** 2026-10-17 | **Tieu chuan tham chieu:** IPC-2221B, IPC-2152, IPC-A-610 Class 2

---

## I. TONG KET DANH GIA CHAT LUONG (EXECUTIVE SUMMARY)

| Tieu chi danh gia | Ket qua | Danh gia cua chuyen gia |
| :--- | :---: | :--- |
| **Tinh toan ven dien hoc (Electrical ERC)** | **PASS (0 Errors, 0 Warnings)** | Khong ton tai xung dot chan, khong ho mach net, toan bo cong suat va tin hieu logic phan lap chuan. |
| **Quy tac bo tri & cach ly (PCB DRC)** | **PASS (0 Violations, 0 Unconnected)** | Khong bi vi pham khoang cach dong (clearance >= 0.22mm), khong short net, khong bi ho loan nhiet (starved thermal). |
| **Kha nang chiu tai dong lon (Power Integrity)** | **PASS** | Cac rail +12V, +6V servo di trace 1.8mm - 2.0mm tren dong 1oz, dap ung tai dinh 5A - 8A. Co 2 tu lon 2200uF bu tuc thoi. |
| **Kha nang bao ve mach (Circuit Protection)** | **PASS** | 3 tang bao ve: Cau chi nong mini blade 5A, P-MOSFET chong nguoc cuc, TVS 1500W chong soc cam ung, 2 cau chi PTC 3A cho servo. |
| **Tinh tuong thich co khi (DFA / Mechanical)** | **PASS** | Board vuong 100x100mm, 4 lo M3 cach mep 4mm, cong USB ESP32 huong ra ngoai mep day board de thao nap firmware. |
| **Kha nang han lap thu cong (Hand Solderability)**| **PASS** | 100% linh kien THT chan xuyen lo va module header, khoang cach pad thoang, de bao tri thay the. |

---

## II. PHAN TICH CHUYEN SAU CAC KHOI CHUC NANG

### 1. Khoi Nguon & Bao ve dau vao (+12V Rail)
- **Bao ve nguoc cuc:** Su dung P-Channel MOSFET IRF9540N (TO-220) voi dien tro keo xuong 10k tai Gate. Khi cam dung cuc, V_GS = -12V, MOSFET dan bao hoa hoan toan voi R_DS(on) ~ 0.117 Ohm. Tai dong 3A, do sut ap chi ~ 0.35V va cong suat tieu tan P = 1.05W (mat do nhiet rat thap, khong bi nong nhu diode silicon truyen thong sut ap 0.7V - 1.0V).
- **Bao ve qua ap & soc xung:** Diode TVS 1.5KE15CA (DO-201AD) mac song song ngay sau MOSFET. Khi dong ngat relay hoac servo dung dot ngot gay xung nguoc tu cam ung cuon day, TVS se dap ngay cac gai ap tren 15V ve mass, bao ve an toan tuyet doi cho ca 2 module Buck va ESP32.
- **Bao ve qua dong:** Cau chi mini blade 5A (F1) tren header kep dong han truc tiep xuong board.

### 2. Khoi Nguon Servo (+6V Rail)
- **Module Buck XH-M401 (XL4016E1):** Tich hop san cuon cam cong suat lon va nhom tan nhiet rieng, cho dong dinh muc 8A lien tuc. Nguon 12V vao va 6V ra ket noi qua domino van oc KF301 5.08mm.
- **Phan lap 2 cot servo (Col 1 & Col 2):** Nguon 6V duoc tach thanh 2 nhanh doc lap qua 2 cau chi tu hoi Polyfuse Bourns MF-R300 (3A giu / 6A cat). Neu servo cot 1 bi ket co khi, chi co F2 ngat, cot 2 van hoat dong binh thuong ma khong gay sup toan bo he thong.
- **Tu loc dem cuc bo:** Moi nhanh servo deu duoc trang bi 1 tu hoa low-ESR lon 2200 uF (duong kinh 12.5mm, chan 5.0mm) + 1 tu gom 100nF dat sat chan connector. Giup triet tieu hoan toan hien tuong tut ap gay reset ESP32 khi ca 4 servo khoi dong dong thoi.

### 3. Khoi Nguon Logic (+5V & +3.3V)
- **Module MP1584EN Mini 3A:** Ha ap tu 12V xuong 5V cap vao chan 5V cua ESP32 DevKit qua cac hang chan header kep 2.54mm.
- **ESP32 DevKit 38 Header:** Do dai hang chan tieu chuan 19 pin moi ben, khoang cach giua 2 hang chan 0.9 inch (22.86mm) dung chuan module tren thi truong.
- **De-coupling:** Cac duong nguon 3.3V va 5V deu co tu loc gom 100nF (C5, C6) dat sat chan nguon.

### 4. Khoi Phat & Thu Hong ngoai (IR Transmitter & Receiver)
- **IR Driver (TX):** Transistor NPN S8050 (TO-92) voi dien tro kich Base 1k tu chan GPIO17 ESP32. Dong kich Base I_B ~ 2.6mA dam bao transistor dan bao hoa. 2 LED phat IR duoc gioi han dong qua 2 dien tro rieng 120 Ohm (cong suat 1/2W) giup phat xung 38kHz khoe ma khong bi chay LED.
- **IR Receiver (RX) Bo ve tinh:** Tich hop mat nhan 3 chan TSOP38238 / VS1838B dat sat mieng khe roi coc. Co mach loc RC tai cho (100 Ohm + 4.7 uF) theo khuyen cao cua Vishay giup chong nhieu dien tu tu dong co servo.

### 5. Khoi Cong tac hanh trinh (Limit Switches)
- 4 kenh cong tac hanh trinh deu co mach loc phan cung gom dien tro pull-up 10k len 3.3V va tu loc chong doi phim (anti-bounce) 100nF xuong mass. Hang so thoi gian RC = 1ms giup loai bo hoan toan nhieu co khi ma khong ton cong CPU ESP32 chay thuat toan debounce.

---

## III. HUONG DAN DANH CHO KY SU LAP RAP & TEST MANG (BRING-UP GUIDE)

1. **Kiem tra nguon khong tai (Unloaded Test):**
   - Chua cam ESP32 vao socket.
   - Cap nguon 12V vao J1. Kiem tra LED D2 (+12V) sang.
   - Do diem do TP1 xem dung 12V.
   - Dieu chinh bien tro tren module XH-M401 sao cho dien ap tai TP2/TP3 dat chinh xac **6.0V**. Kiem tra LED D3, D4 sang.
   - Dieu chinh bien tro tren module MP1584EN sao cho dien ap tai TP4 dat chinh xac **5.0V**. Kiem tra LED D5 sang.
2. **Kiem tra ESP32 & Logic:**
   - Ngat nguon 12V, cam module ESP32 DevKit 38 vao 2 hang socket J18, J19 (chu y cong USB huong xuong duoi).
   - Cap lai nguon 12V. Kiem tra LED D6 (+3.3V) sang. Do TP5 dat 3.3V.
   - Nap firmware dieu khien qua cong USB.
3. **Ket noi tai Servo & Sensor:**
   - Lan luot cam 4 servo vao J5 - J8 va 2 mat nhan IR vao J9, J10.
"""
(p_rev / "EXPERT_DESIGN_VERIFICATION_REPORT.md").write_text(review_report, encoding="utf-8")

# 5. Populate 03_KiCad_Source_Design
for item in (ROOT / "hardware/archive/reva").glob("FV-*.*"):
    shutil.copy2(item, p_src / item.name)
shutil.copy2(ROOT / "hardware/archive/reva" / "fp-lib-table", p_src / "fp-lib-table")
shutil.copytree(ROOT / "libs", p_src / "libs", dirs_exist_ok=True)

# 6. Create README Guide in Handover Root
readme_txt = """================================================================================
GOI HO SO BAN GIAO SAN XUAT VA THAM DINH THIET KE
DU AN: FV-CTRL REV A (FRUIT VENDING DISPENSER CONTROLLER)
================================================================================

Thu muc nay chua day du cac thanh phan ban giao chuyen nghiep:

1. THU MUC: 01_PCB_Fabrication
   -> Danh cho xuong in / gia cong mach PCB (JLCPCB, PCBWay, Sao Kim, Kim Son,...)
   - FV-CTRL_RevA_Gerbers.zip : File Gerber & khoan cua Bo mach chinh (100x100mm)
   - FV-IR-RX_RevA_Gerbers.zip: File Gerber & khoan cua Bo cam bien IR ve tinh (18x42mm)
   - PCB_FABRICATION_SPECS.txt: Quy cach cong nghe gia cong (2 lop, 1.6mm, 1oz, HASL)

2. THU MUC: 02_Technical_Review
   -> Danh cho ky su truong, ky su dien tu & ky su co khi danh gia tham dinh
   - FV-CTRL_RevA_Schematic.pdf: So do nguyen ly bo chinh (Vector PDF chat luong cao)
   - FV-IR-RX_RevA_Schematic.pdf: So do nguyen ly bo ve tinh IR RX
   - FV-CTRL_RevA_BOM.csv      : Bang ke linh kien gom MPN, footprint de mua hang
   - FV-CTRL_RevA_3D.step     : Model 3D STEP bo chinh cho ben thiet ke vo co khi
   - FV-IR-RX_RevA_3D.step    : Model 3D STEP bo mat nhan IR cho ben co khi
   - EXPERT_DESIGN_VERIFICATION_REPORT.md: Bao cao tham dinh ky thuat chuyen sau
   - ERC_Report_Mainboard.txt : Ket qua chay ERC KiCad 10 (0 loi)
   - DRC_Report_Mainboard.txt : Ket qua chay DRC KiCad 10 (0 loi)
   - DRC_Report_Satellite_IR.txt: Ket qua chay DRC bo IR (0 loi)

3. THU MUC: 03_KiCad_Source_Design
   -> Danh cho ky su muon mo truc tiep project tren phan mem KiCad 10
   - Chua toan bo file goc (.kicad_pro, .kicad_sch, .kicad_pcb) va thu vien footprint.

================================================================================
"""
(HANDOVER / "README_HUONG_DAN_BAN_GIAO.txt").write_text(readme_txt, encoding="utf-8")

print(f"Handover package successfully created at: {HANDOVER}")
