"""Verify the RECOM substitution; this is not thermal or electrical qualification."""
from pathlib import Path
import argparse,csv,hashlib,json,math,re
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline',type=Path)
args=parser.parse_args()
spec=json.loads((ROOT/'hardware/revb/FV-CTRL_RevB.design.json').read_text())
parts={x['ref']:x for x in spec['parts']}
boardpath=ROOT/'hardware/revb/FV-CTRL_RevB.kicad_pcb'
b=p.LoadBoard(str(boardpath));fs={x.GetReference():x for x in b.GetFootprints()}
errors=[]
def check(condition,message):
    if not condition:errors.append(message)
check(parts['J4']['mpn']=='R-78E5.0-1.0','Incorrect converter MPN')
check(parts['J4']['pins']=={'1':'+12V','2':'GND','3':'+5V'},'Incorrect J4 mapping')
pads={x.GetNumber():x for x in fs['J4'].Pads()}
check(set(pads)=={'1','2','3'},'J4 must have exactly three pins')
for a,z in [('1','2'),('2','3')]:
    check(abs(p.ToMM((pads[a].GetPosition()-pads[z].GetPosition()).EuclideanNorm())-2.54)<.001,'J4 pitch')
for pad in pads.values():
    check(abs(p.ToMM(pad.GetDrillSize().x)-1.0)<.001,'J4 drill')
    check(abs(p.ToMM(pad.GetSize().x)-1.9)<.001,'J4 pad size')
for ref,rail in [('C57','+12V'),('C58','+5V')]:
    check(parts[ref]['pins']=={'1':rail,'2':'GND'},ref+' pin mapping')
    check({pad.GetNumber():pad.GetNetname() for pad in fs[ref].Pads()}==parts[ref]['pins'],ref+' actual PCB nets')
budget=.8+.010+2*(5.25-1.0)/(120*.95)+(5.25-1.5)/(1500*.95)
check(budget<1.0,'5V conservative budget exceeds 1A at non-derated conditions')
def capacitance(value):
    m=re.match(r'([\d.]+)([unp])F',value)
    return float(m[1])*{'u':1,'n':.001,'p':.000001}[m[2]] if m else 0
# Deliberately over-count downstream and signal capacitors; external loads are excluded.
cap_uF=sum(capacitance(x['value']) for x in spec['parts'] if x['ref'].startswith('C') and
           x['ref'] not in ['C1','C2','C3','C4','C57'])
check(cap_uF*1.2<220,'Capacitive-load budget')
quote=list(csv.DictReader((ROOT/'docs/revb/bom/FV-CTRL_RevB-SMT-quote.csv').open(encoding='utf-8-sig')))
cpl=list(csv.DictReader((ROOT/'docs/revb/assembly/FV-CTRL_RevB-SMT-position-review.csv').open(encoding='utf-8-sig')))
check(len(parts)==151,'Unexpected BOM count')
check(len(quote)==len(cpl)==63,'SMT/CPL count')
check({x['Reference'] for x in quote}=={x['Ref'] for x in cpl},'SMT/CPL references')
baseline_result='NOT_REQUESTED'
if args.baseline:
    old=p.LoadBoard(str(args.baseline.resolve()));oldfs={x.GetReference():x for x in old.GetFootprints()}
    def fingerprint(f):
        return (f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),
                sorted((x.GetNumber(),x.GetNetname(),x.GetPosition().x,x.GetPosition().y) for x in f.Pads()))
    for ref,f in oldfs.items():
        if ref!='J4':check(ref in fs and fingerprint(f)==fingerprint(fs[ref]),'Unrelated footprint changed: '+ref)
    def critical(board):
        rows=[]
        for t in board.GetTracks():
            net=t.GetNetname()
            if net.startswith(('RF_','XTAL_','+6V')) or (net.startswith('+12V') and t.GetLayer()==p.F_Cu):
                rows.append((net,t.GetClass(),t.GetLayer(),t.GetStart().x,t.GetStart().y,
                             t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if t.GetClass()=='PCB_VIA' else t.GetWidth()))
        return sorted(rows)
    check(critical(old)==critical(b),'RF/crystal/6V/front12V routing changed')
    baseline_result='PASS' if not errors else 'FAIL'
result=dict(status='FAIL' if errors else 'PASS',errors=errors,
    converter='R-78E5.0-1.0',load_budget_A=round(budget,6),
    load_budget_is_calculated_not_measured=True,full_load_datasheet_max_ambient_C=60,
    conservative_capacitor_sum_uF=round(cap_uF,6),sum_with_20_percent_allowance_uF=round(cap_uF*1.2,6),
    datasheet_capacitive_limit_uF=220,baseline_comparison=baseline_result,
    pcb_sha256=hashlib.sha256(boardpath.read_bytes()).hexdigest(),
    limits='Does not prove hot-plug/soft-start, ripple, EMI, thermal derating, load transients or factory/incoming qualification')
(ROOT/'reports/revb/verified/RevB-RECOM-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));raise SystemExit(bool(errors))
