"""Remove reported dead ends, keeping only changes that preserve connectivity."""
import re
import pcbnew as p
from rev_b_layout import FILE
from rev_b_route_connections import check

def main():
 report=check();removed=0
 while True:
  warnings=[v for v in report['violations'] if v['type'] in ['via_dangling','track_dangling']]
  if not warnings:break
  progressed=False
  for warning in warnings:
   uuids={a['uuid'] for a in warning['items']};before=FILE.read_bytes()
   text=re.sub(r'\n\t\((?:segment|via)\b[\s\S]*?\n\t\)',lambda m:'' if any(u in m[0] for u in uuids) else m[0],before.decode('utf-8'))
   if text==before.decode('utf-8'):continue
   FILE.write_text(text,encoding='utf-8');b=p.LoadBoard(str(FILE));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(FILE),b)
   after=check()
   if any(v['severity']=='error' for v in after['violations']) or len(after['unconnected_items'])>len(report['unconnected_items']) or after['schematic_parity']:
    FILE.write_bytes(before);check();continue
   report=after;removed+=1;progressed=True
   print('Removed',warning['type'],*uuids,flush=True);break
  if not progressed:break
 print('Dead-end removals',removed,'remaining violations',len(report['violations']),'opens',len(report['unconnected_items']))

if __name__=='__main__':main()
