"""Route a bounded set of reported opens; verify each change and roll back errors."""
from pathlib import Path
import json,re,subprocess,sys,collections
from rev_b_finish_routes import route,FILE
ROOT=FILE.parent.parent;REPORT=ROOT/'reports/RevB-routing-drc.json'

def check():
 for cmd in [ ['kicad-cli','sch','erc','--output',str(ROOT/'reports/RevB-routing-erc.rpt'),str(FILE.with_suffix('.kicad_sch'))],['kicad-cli','pcb','drc','--format','json','--schematic-parity','--output',str(REPORT),str(FILE)]]:
  subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
 return json.loads(REPORT.read_text())

def key(item):
 m=re.match(r'(?:PTH pad|Pad) ([^ ]+) \[[^]]+\] of ([^ ]+)',item['description'])
 return m[2]+':'+m[1] if m else '@'+item['uuid']

if __name__=='__main__':
 failed=set();count=0;budget=int(sys.argv[1]) if len(sys.argv)>1 else 8
 while count<budget:
  report=json.loads(REPORT.read_text());choices=[]
  for item in report['unconnected_items']:
   first,second=item['items'];net=re.search(r'\[([^]]+)\]',first['description'])[1]
   if net=='GND' or 'Zone' in first['description'] or 'Zone' in second['description']:continue
   if len(sys.argv)>2 and sys.argv[2]=='power' and net not in ['+3V3','+3V3_RF','VDD_SDIO']:continue
   pair=(net,key(first),key(second))
   if (net,*sorted(pair[1:])) in failed:continue
   dist=sum((first['pos'][a]-second['pos'][a])**2 for a in ['x','y'])**.5
   choices.append((dist,pair))
  if not choices:break
  dist,pair=min(choices);net,aa,cc=pair
  before=FILE.read_bytes();baseline=sum(a['severity']=='error' for a in report['violations'])
  width=.12 if 'U1:' in aa or 'U1:' in cc else .4 if net=='+3V3' else .3 if net in ['+3V3_RF','VDD_SDIO'] else .15
  print('ATTEMPT',pair,'distance',round(dist,2),'width',width,flush=True)
  signature=(net,*sorted(pair[1:]))
  try:route(net,aa,cc,width)
  except Exception as e:print('NO ROUTE',str(e),flush=True);failed.add(signature);continue
  after=check();errors=sum(a['severity']=='error' for a in after['violations'])
  if errors>baseline or after['schematic_parity']:
   FILE.write_bytes(before);check();failed.add(signature);print('ROLLED BACK: hard DRC/parity',flush=True);continue
  count+=1
  remaining=collections.Counter(re.search(r'\[([^]]+)\]',a['items'][0]['description'])[1] for a in after['unconnected_items'])
  print('VERIFIED route',count,'total opens',sum(remaining.values()),'power opens',{k:v for k,v in remaining.items() if k.startswith('+3V3') or k=='VDD_SDIO'},flush=True)
 print('BATCH END',count,'routes;',len(failed),'need geometric review',flush=True)
