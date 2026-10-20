"""Engineering BOM with explicit sourcing gaps; never claims a factory quote."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'hardware/revb/FV-CTRL_RevB.design.json';s=json.loads(path.read_text())
old={r['Ref']:r for r in csv.DictReader((ROOT/'docs/reva2/FV-CTRL_RevA2-bom.csv').open(encoding='utf-8-sig'))}
refs={p['ref']:p for p in s['parts']}
refs['Y1']['mpn']='ABM8-40.000MHZ-10-1-U-T'
refs['Y1']['notes']='Verified Abracon catalog: CL10pF, +/-10ppm tolerance and stability, 3225; -10..60C; sourcing/temperature range must be confirmed'
sources={
 'U1':('C967021','https://jlcpcb.com/partdetail/EspressifSystems-ESP32_D0WDV3/C967021','No pin-compatible alternate approved; preserve GPIO16/17'),
 'U2':('C1550551','https://www.lcsc.com/product-detail/C1550551.html','CP2102N-A02-GQFN24R: tape/reel ordering variant; verify exact assembly SKU'),
 'U3':('','https://www.st.com/resource/en/datasheet/ld1117.pdf','LD1117V33 TO220 only; other 1117 models require pinout/stability/thermal review'),
 'U4':('C179173','https://jlcpcb.com/partdetail/WinbondElec-W25Q32JVSSIQ/C179173','W25Q32JVSSJQ ordering variant candidate; check QE default, firmware, temp and package'),
 'U5':('','https://www.ti.com/lit/ds/symlink/tlv803e.pdf','TLV803EA30DBZR.A same ordering family; do not use R/V pinout variants'),
 'Y1':('C1986574','https://abracon.com/parametric/crystals/ABM8-40.000MHZ-10-1-U-T','Same CL10pF, 40MHz, 3225, +/-10ppm candidate only after datasheet/thermal review'),
 'J20':('','https://www.amphenolrf.com/en-us/part/132134/662/','No mechanical drop-in approved; compare all pads/holes before substitution'),
 'J21':('','https://www.molex.com/en-us/products/part-detail/1050170001','No mechanical drop-in approved; same pitch alone does not establish compatibility'),
 'L1':('','https://www.murata.com/products/productdetail?partno=LQP03TN2N7B02%23','Same-series toleranced 0201 variant only after RF retuning'),
 'L2':('','https://www.murata.com/en-us/products/productdetail?partno=LQP03TN2N0B02%23','Current>=600mA candidate; validate DCR, SRF and filter/EMC response'),
}
rows=[]
for part in s['parts']:
 ref=part['ref'];base=old.get(ref);code=''
 if base:
  source=base['Source / purchase'];alt=base['Alternative / qualification'];status=base['Status']
 elif ref in sources:code,source,alt=sources[ref];status='Selected engineering MPN; factory stock/MOQ/price not verified'
 elif ref.startswith('R'):
  source='https://www.yageo.com/en/Product/Index/rchip';alt='Same value/tolerance/power/0402 candidate requires exact MPN and footprint review';status='Selected engineering MPN; confirm Yageo ordering suffix and factory stock'
 elif ref.startswith('C'):
  source='https://www.murata.com/en-global/products/capacitor/ceramiccapacitor';alt='Same value/dielectric/voltage/size candidate; DC bias, tolerance and RF Q must be checked';status='Selected engineering MPN; verify effective capacitance and exact manufacturer lifecycle'
 elif ref in ['D8','D9','D10']:
  source='https://www.nexperia.com/product/PESD5V0X1BL';alt='PESD5V0X1BL-Q candidate; verify package and RF/ESD response';status='System ESD and RF tuning NOT RUN'
 elif ref in ['Q3','Q4']:
  source='https://www.onsemi.com/pdf/datasheet/mmbt3904lt1-d.pdf';alt='MMBT3904LT3G reel variant; verify 1B2E3C footprint';status='Selected; auto-download timing must be tested'
 elif ref.startswith('SW'):
  source='https://components.omron.com/us-en/products/switches/B3F';alt='Same B3F-1000 body/pins family variant; verify height and actuator';status='Incoming mechanical fit test required'
 elif ref.startswith('TP'):
  source='https://www.keyelco.com/category.cfm/Test-Points-color-keyed-Thru-Hole-Mount/Miniature-Style/id/747';alt='5260 matte-tin variant';status='1.0mm finished drill fit test required'
 else:raise RuntimeError('Missing sourcing row '+ref)
 smt=any(t in part['footprint'] for t in ['_SMD:','Package_SO:','Package_DFN','SOT_SMD','Crystal:','Connector_USB:'])
 row=dict(Reference=ref,Value=part['value'],MPN=part['mpn'],Footprint=part['footprint'],Population='DNP' if part['dnp'] else 'FIT',Assembly='SMT factory' if smt else 'THT manual',Candidate_LCSC=code,Source=source,Alternative=alt,Status=status,Notes=part.get('notes',''))
 rows.append(row)
path.write_text(json.dumps(s,indent=2),encoding='utf-8')
with (ROOT/'docs/revb/bom/FV-CTRL_RevB-bom-draft.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','MPN','Footprint','Population','Assembly','Qualification'])
 for r in rows:w.writerow([r['Reference'],r['Value'],r['MPN'],r['Footprint'],r['Population'],'SMT' if r['Assembly']=='SMT factory' else 'THT','; '.join(v for v in [r['Status'],r['Notes']] if v)])
for filename,subset in [('FV-CTRL_RevB-bom-review.csv',rows),('FV-CTRL_RevB-SMT-quote.csv',[r for r in rows if r['Assembly']=='SMT factory' and r['Population']=='FIT']),('FV-CTRL_RevB-THT-assembly.csv',[r for r in rows if r['Assembly']=='THT manual'])]:
 with (ROOT/'docs/revb/bom'/filename).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(subset)
print('BOM review:',len(rows),'references;',sum(r['Assembly']=='SMT factory' and r['Population']=='FIT' for r in rows),'SMT references. Catalog IDs are candidates, not stock/price confirmations.')
