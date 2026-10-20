"""Attach sourced part choices, alternatives and explicit qualification status.

Updates metadata and a smaller test-point drill; preserves schematic UUIDs.
No Gerber export, purchase, or claim of tested production qualification.
"""
from pathlib import Path
import json,csv
import pcbnew as pcb
ROOT=Path(__file__).resolve().parents[1]
specpath=ROOT/'hardware/FV-CTRL_RevA2.design.json'
spec=json.loads(specpath.read_text())
rows=[]
for part in spec['parts']:
    ref=part['ref'];val=part['value'].split()[0]; status='Selected; incoming inspection and first article required'
    alt='Same specification from an authorized source; engineering requalification required'
    source='docs/RevA2-review-and-bringup.md'
    if ref.startswith('R'):
        code={'330R':'330R','10k':'10K','120R':'120R','5.6k':'5K6','2.2k':'2K2','1.5k':'1K5','1k':'1K'}[val]
        mpn='CFR-25JR-52-'+code;alt='MFR-25FBF52-'+code+' (candidate; confirm body/lead dimensions)'
        source='https://yageogroup.com/content/datasheet/asset/file/YAGEO-CFR_DATASHEET'
    elif ref in ['C1','C2']:
        mpn='EEUFR1C222';alt='UPW1C222MHD (candidate; verify height, impedance and ripple)'
        source='https://industrial.panasonic.com/kr/products/pt/aluminum-cap-lead/models/EEUFR1C222'
    elif ref=='C5':
        mpn='EEUFR1H100';alt='50YXJ10M5X11 (candidate; confirm availability/dimensions)'
        part['value']='10uF 50V'
        source='https://industrial.panasonic.com/kr/products/pt/aluminum-cap-lead/models/EEUFR1H100'
    elif ref.startswith('C'):
        mpn='K104K15X7RF53H5';alt='K104K10X7RF53H5 (same 100nF/50V/X7R/5mm; verify envelope)'
        source='https://www.vishay.com/doc/?45171='
    elif ref.startswith('TP'):
        mpn='5001' if part['pins']['1']=='GND' else '5000';alt='5261' if mpn=='5001' else '5260'
        part['footprint']='fv_reva2:Keystone_5000_Carrier_D3'
        source='https://www.keyelco.com/category.cfm/Test-Points-color-keyed-Thru-Hole-Mount/Miniature-Style/id/747'
    elif ref=='F1':
        mpn='SCHURTER 0001.2511 + 2x Littelfuse 01110001L';alt='0477005.MXP cartridge; compare I2t/inrush and verify holder separately'
        source='https://www.schurter.com/en/part/0001.2511';status='5A time-lag DC-rated choice; coordination with PSU/harness must be tested'
    elif ref in ['F2','F3']:
        mpn='MF-R300';alt='RUEF300 (candidate; verify pitch, trip curve, temperature derating)'
        source='https://bourns.com/docs/product-datasheets/mf-r.pdf';status='Selected; hot-enclosure hold current and stall coordination untested'
    elif ref=='Q1':
        mpn='IRF4905PBF';alt='SiHF4905-GE3 (candidate; verify G/D/S, SOA and thermal)';source='https://www.infineon.com/part/IRF4905'
    elif ref=='Q2':
        mpn='P2N2222AG';alt='P2N2222ARL1G (same device, formed/taped leads; check lead forming)';source='https://www.onsemi.com/pdf/datasheet/p2n2222a-d.pdf'
    elif ref=='D1':
        mpn='Littelfuse 1.5KE15CA';alt='Vishay 1.5KE15CA-E3/54 (candidate; verify lead/package dimensions)';source='https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_1_5ke_datasheet.pdf.pdf'
    elif ref=='D7':
        mpn='BZX55C12';alt='BZX55C12-TR packaging variant; verify order suffix';source='https://www.vishay.com/docs/85604/bzx55.pdf'
    elif ref.startswith('D'):
        mpn='WP710A10GD';alt='WP710A10GT (clear lens variant; verify visibility)';source='https://www.kingbrightusa.com/images/catalog/spec/wp710a10gd.pdf'
    elif ref=='J1':
        mpn='1757242 + mating 1757019';alt='1923869 HC variant (candidate; verify mating coding/drawing)';source='https://www.phoenixcontact.com/en-us/products/pcb-header-mstba-25-2-g-508-1757242'
    elif ref in ['J2','J3']:
        mpn='1757268 + mating 1757035';alt='1923885 HC variant (candidate; verify same footprint/mate)';source='https://www.phoenixcontact.com/en-us/products/pcb-header-mstba-25-4-g-508-1757268'
    elif ref=='J4':
        mpn='Pololu 2850 D24V25F5 + 1x05 female socket';alt='D24V50F5 (electrically pin-compatible; larger body requires layout review)';source='https://www.pololu.com/product/2850'
    elif ref in ['J18','J19']:
        mpn='SSQ-119-03-G-S';alt='SSQ-119-03-T-S (same geometry, tin plating)';source='https://www.samtec.com/products/ssq-119-03-g-s'
    elif ref in ['J5','J6','J7','J8','J17','JP1']:
        count=2 if ref=='JP1' else 4 if ref=='J17' else 3
        mpn=f'M20-9990{count}46'+(' + M7567-05 shunt' if ref=='JP1' else '')
        alt=f'TSW-10{count}-07-G-S (candidate; verify lead length/body/current)';source='https://www.harwin.com/products/M20-9990346'
    elif ref.startswith('J'):
        count=3 if ref in ['J9','J10'] else 2
        mpn=f'B{count}B-XH-A + XHP-{count} + SXH-001T-P0.6'
        alt=f'B{count}B-XH-A(LF)(SN) ordering variant; check exact housing/terminal';source='https://www.jst-mfg.com/product/pdf/eng/eXH.pdf'
    elif ref.startswith('H'):
        mpn='M3 nylon spacer/screw set, enclosure dependent';alt='M3 metal hardware with insulating washers, verify copper keepout';status='Mechanical procurement pending enclosure';source='PROJECT.md section 12'
    else:raise ValueError(ref)
    part['mpn']=mpn
    rows.append([ref,part['value'],mpn,alt,part['footprint'],'DNP' if part['dnp'] else 'FIT',source,status])
specpath.write_text(json.dumps(spec,indent=2),encoding='utf-8')
with (ROOT/'docs/FV-CTRL_RevA2-bom.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Ref','Value','Primary MPN','Alternative / qualification','Footprint','Population','Source / purchase','Status']);w.writerows(rows)
schpath=ROOT/'hardware/FV-CTRL_RevA2.kicad_sch'
s=schpath.read_text(encoding='utf-8').replace('TestPoint:TestPoint_THTPad_D3.0mm_Drill1.5mm','fv_reva2:Keystone_5000_Carrier_D3').replace('10uF 25V','10uF 50V')
schpath.write_text(s,encoding='utf-8')
b=pcb.LoadBoard(str(ROOT/'hardware/FV-CTRL_RevA2.kicad_pcb'))
for fp in b.GetFootprints():
    if fp.GetReference()=='C5':fp.SetValue('10uF 50V')
    if fp.GetReference().startswith('TP'):
        fp.SetFPIDAsString('fv_reva2:Keystone_5000_Carrier_D3')
        for pad in fp.Pads():pad.SetDrillSize(pcb.VECTOR2I(pcb.FromMM(1),pcb.FromMM(1)))
b.BuildConnectivity();pcb.ZONE_FILLER(b).Fill(b.Zones());pcb.SaveBoard(str(ROOT/'hardware/FV-CTRL_RevA2.kicad_pcb'),b)
print('Updated sourced BOM and 1.0mm test-point drills. Run ERC, XML export, DRC and parity.')
