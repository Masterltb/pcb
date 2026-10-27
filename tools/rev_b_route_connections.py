"""Route a bounded set of reported opens; verify each change and roll back errors."""
from pathlib import Path
import json,re,subprocess,sys,collections
from rev_b_finish_routes import route,FILE
ROOT=Path(__file__).resolve().parents[1];REPORT=ROOT/'reports/revb/work/RevB-routing-drc.json'

def check():
 for cmd in [ ['kicad-cli','sch','erc','--output',str(ROOT/'reports/revb/work/RevB-routing-erc.rpt'),str(FILE.with_suffix('.kicad_sch'))],['kicad-cli','pcb','drc','--format','json','--schematic-parity','--output',str(REPORT),str(FILE)]]:
  subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
 return json.loads(REPORT.read_text())

def key(item):
 return '@'+item['uuid']

if __name__=='__main__':
 failed=set();count=0;budget=int(sys.argv[1]) if len(sys.argv)>1 else 8
 while count<budget:
  report=json.loads(REPORT.read_text());choices=[]
  if any(a['severity']=='error' for a in report['violations']):
   raise RuntimeError('Repair existing physical DRC errors before adding another connection')
  for item in report['unconnected_items']:
   first,second=item['items'];net=re.search(r'\[([^]]+)\]',first['description'])[1]
   if first['uuid']==second['uuid'] or net=='GND' or 'Zone' in first['description'] or 'Zone' in second['description']:continue
   if len(sys.argv)>3 and net in sys.argv[3].split(','):continue
   if len(sys.argv)>2 and sys.argv[2]=='power' and net not in ['+3V3','+3V3_RF','VDD_SDIO']:continue
   if len(sys.argv)>2 and sys.argv[2]=='caps' and net not in ['CAP1','CAP2']:continue
   pair=(net,key(first),key(second))
   if (net,*sorted(pair[1:])) in failed:continue
   dist=sum((first['pos'][a]-second['pos'][a])**2 for a in ['x','y'])**.5
   choices.append((dist,pair,first,second))
  if not choices:break
  dist,pair,first,second=min(choices,key=lambda x:x[0]);net,aa,cc=pair
  before=FILE.read_bytes();baseline=sum(a['severity']=='error' for a in report['violations'])
  (ROOT/'reports/revb/work/RevB-route-checkpoint.kicad_pcb').write_bytes(before)
  is_u1 = 'U1' in first['description'] or 'U1' in second['description']
  width=.15 if is_u1 else .4 if net=='+3V3' else .3 if net in ['+3V3_RF','VDD_SDIO'] else .20
  print('ATTEMPT',pair,'distance',round(dist,2),'width',width,flush=True)
  signature=(net,*sorted(pair[1:]))
  try:route(net,aa,cc,width)
  except Exception as e:
   if net in ['+3V3','+3V3_RF','VDD_SDIO'] and width>.15:
    print('Retry constrained power escape at 0.15mm; distribution widening is a separate check',flush=True)
    try:route(net,aa,cc,.15)
    except Exception as second_err:print('NO ROUTE',str(second_err),flush=True);failed.add(signature);continue
   else:print('NO ROUTE',str(e),flush=True);failed.add(signature);continue
  after=check();errors=sum(a['severity']=='error' for a in after['violations'])
  if (errors>baseline or after['schematic_parity']) and width>.20:
   print('Retry constrained route at 0.20mm',flush=True)
   FILE.write_bytes(before)
   try:
    route(net,aa,cc,.20)
    after=check();errors=sum(a['severity']=='error' for a in after['violations'])
   except Exception as retry_err:
    print('NO RETRY ROUTE',str(retry_err),flush=True)
  if errors>baseline or after['schematic_parity']:
   FILE.write_bytes(before);check();failed.add(signature);print('ROLLED BACK: hard DRC/parity',flush=True);continue
  count+=1
  remaining=collections.Counter(re.search(r'\[([^]]+)\]',a['items'][0]['description'])[1] for a in after['unconnected_items'])
  print('VERIFIED route',count,'total opens',sum(remaining.values()),'power opens',{k:v for k,v in remaining.items() if k.startswith('+3V3') or k=='VDD_SDIO'},flush=True)
 print('BATCH END',count,'routes;',len(failed),'need geometric review',flush=True)
