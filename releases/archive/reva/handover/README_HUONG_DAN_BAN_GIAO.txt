================================================================================
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
