"""Move crowded visible fields without changing symbols, UUIDs or nets."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def main():
 for suffix,refs in [('03',{'Y1':10,'J20':10,'D8':8}),('09',{'J21':14,'D9':8,'D10':8})]:
  path=ROOT/f'hardware/FV-CTRL_RevB-{suffix}.kicad_sch'
  def adjust(match):
   block=match[0];ref=re.search(r'\(property "Reference" "([^"]+)"',block)
   if not ref or ref[1] not in refs:return block
   pos=re.search(r'\(at ([\d.-]+) ([\d.-]+) [\d.-]+\)',block)
   x,y=map(float,pos.groups());dy=refs[ref[1]]
   for field,yy in [('Reference',y-dy),('Value',y+dy)]:
    block=re.sub(r'(\(property "'+field+r'" "[^"]+"\s*\(at )[^)]+',lambda m:m[1]+f'{x:.4f} {yy:.4f} 0',block,count=1)
   return block
  path.write_text(re.sub(r'\n\t\(symbol\b[\s\S]*?\n\t\)',adjust,path.read_text(encoding='utf-8')),encoding='utf-8')

if __name__=='__main__':main()
