"""Build a native KiCad engineering-review ZIP; never exports fabrication files."""
from pathlib import Path
import json,csv,hashlib,zipfile,subprocess

ROOT=Path(__file__).resolve().parents[1];PREFIX='FV-CTRL_RevB-review'
report=json.loads((ROOT/'reports/revb/verified/RevB-final-drc.json').read_text())
assert not report['violations'] and not report['unconnected_items'] and not report['schematic_parity']
assert 'ERC messages: 0  Errors 0  Warnings 0' in (ROOT/'reports/revb/verified/RevB-final-erc.rpt').read_text(encoding='utf-8')
for name in ['RevB-functional-gate.json','RevB-via-paste-check.json']:
 assert json.loads((ROOT/'reports/revb/verified'/name).read_text())['status']=='PASS'
def rows(name):
 matches=[ROOT/'docs/revb'/folder/name for folder in ['bom','assembly'] if (ROOT/'docs/revb'/folder/name).exists()]
 assert len(matches)==1,name
 return list(csv.DictReader(matches[0].open(encoding='utf-8-sig')))
quote=rows('FV-CTRL_RevB-SMT-quote.csv');positions=rows('FV-CTRL_RevB-SMT-position-review.csv')
assert len(quote)==len(positions)==63
assert json.loads((ROOT/'reports/revb/verified/RevB-RECOM-check.json').read_text())['status']=='PASS'
assert json.loads((ROOT/'reports/revb/verified/RevB-RECOM-check.json').read_text())['pcb_sha256']==hashlib.sha256((ROOT/'hardware/revb/FV-CTRL_RevB.kicad_pcb').read_bytes()).hexdigest()
assert {r['Reference'] for r in quote}=={r['Ref'] for r in positions}
assert len(rows('FV-CTRL_RevB-EP-vias.csv'))==25
assert len(list((ROOT/'hardware/revb').glob('FV-CTRL_RevB*.kicad_sch')))==10
paths=[]
for pattern in ['hardware/revb/FV-CTRL_RevB*.kicad_*','hardware/revb/FV-CTRL_RevB.design.json','hardware/revb/fp-lib-table','hardware/revb/sym-lib-table','libs/fv_revb.kicad_sym','libs/fv_reva2.pretty/*.kicad_mod','libs/fv_modules.pretty/*.kicad_mod','docs/revb/bom/*.csv','docs/revb/assembly/*.csv','docs/revb/FV-CTRL_RevB-pins.h','docs/revb/schematic/*.svg','docs/revb/schematic/*.png','docs/revb/assembly/*.svg','docs/revb/assembly/*.png']:
 paths.extend(ROOT.glob(pattern))
paths.extend(ROOT/p for p in ['README.md','PROJECT.md','AGENTS.md','docs/repository-layout.md','docs/revb/RevB-status.md','docs/revb/RevB-review-and-bringup.md','docs/revb/RevB-QFN-prechange-review.md','reports/revb/verified/RevB-final-erc.rpt','reports/revb/verified/RevB-final-drc.rpt','reports/revb/verified/RevB-final-drc.json','reports/revb/verified/RevB-functional-gate.json','reports/revb/verified/RevB-via-paste-check.json','reports/revb/verified/RevB.net.xml','tools/verify_rev_b.py','tools/verify_rev_b_via_paste.py','tools/verify_rev_b_supply.py','docs/revb/RevB-RECOM-prechange-review.md','reports/revb/verified/RevB-RECOM-check.json'])
paths=sorted(set(p for p in paths if p.is_file()))
assert not any(p.suffix.lower() in ['.gbr','.drl','.ses','.dsn'] for p in paths)
readme='''FV-CTRL RevB — NATIVE KICAD REVIEW ONLY

Chưa phát hành sản xuất; không có Gerber/drill trong gói này.
Đọc docs/revb/RevB-status.md trước. Nguồn thiết kế đã kiểm tra: commit a7dd57b.

Giải nén nguyên cấu trúc. Mở hardware/revb/FV-CTRL_RevB.kicad_pro bằng KiCad 10.
Không tách hardware/ khỏi libs/. Thư viện chuẩn KiCad 10 cần thiết khi chỉnh sửa.
Schematic gồm trang gốc và 9 trang chức năng. PNG/SVG ở docs/ để xem trước.

Mục 9 AGENTS.md yêu cầu duyệt rủi ro trước Gerber. DRC/ERC sạch không thay cho
DFM xưởng, tuning RF, kiểm tra nhiệt hoặc phép thử servo trên mẫu thật.
Đọc cả bản vẽ lắp ráp mặt trước và mặt sau. Ảnh 3D thiếu một số model, gồm U1;
không dùng ảnh 3D để duyệt cơ khí. RevB chưa được kiểm chứng import EasyEDA.

BOM/CPL chỉ để review/báo giá; tồn kho, thay thế, rotation và stencil cần xưởng duyệt.
File SMT dùng gốc phụ góc trái dưới; bản đồ EP dùng tọa độ PCB tuyệt đối.
USB DATA ONLY: cấp 12 V chính khi nạp, USB không cấp nguồn cho board.

reports/ chứa báo cáo kiểm tra và netlist. Có thể chạy lại hai verifier bằng
Python đi kèm KiCad có pcbnew sau khi xuất netlist dạng kicadxml.
SHA256SUMS.txt kiểm tra tính toàn vẹn từng file trong gói.
'''
entries={p.relative_to(ROOT).as_posix():p.read_bytes() for p in paths};entries['README.txt']=readme.encode('utf-8')
checksums=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(entries.items()))
entries['SHA256SUMS.txt']=checksums.encode('utf-8')
output=ROOT/'releases/revb/FV-CTRL_RevB-review.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
 for name,data in sorted(entries.items()):archive.writestr(PREFIX+'/'+name,data)
with zipfile.ZipFile(output) as archive:
 assert archive.testzip() is None
 for name,data in entries.items():assert archive.read(PREFIX+'/'+name)==data
branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
metadata=dict(type='engineering-review-only',layout_version=2,design_commit=subprocess.check_output(['git','log','-1','--format=%h','--','hardware/revb'],cwd=ROOT,text=True).strip(),branch=branch,native_schematic_files=10,smt_references=len(quote),thermal_ep_holes=25,erc_violations=0,drc_violations=0,unconnected=0,schematic_parity=0,gerber_exported=False,factory_approved=False,physical_qualification='NOT RUN',zip_file=output.name,zip_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),archived_files=len(entries))
(ROOT/'releases/revb/FV-CTRL_RevB-review-manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
print(json.dumps(metadata,indent=2))
