"""Conservative drill-to-SMT-paste/mask check, supplementary to KiCad DRC.

Thermal EP PTH pads are excluded and reviewed in the separate factory via map.
Bounding boxes overestimate rounded pad shapes. This is not a fab registration
or solder-wicking simulation.
"""
import math,json
import pcbnew as p
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(ROOT/'hardware/FV-CTRL_RevB.kicad_pcb'));bad=[];minimum=999;closest=None
expansion=p.ToMM(b.GetDesignSettings().m_SolderMaskExpansion)
for via in b.GetTracks():
 if via.GetClass()!='PCB_VIA':continue
 x,y=p.ToMM(via.GetPosition().x),p.ToMM(via.GetPosition().y);radius=p.ToMM(via.GetDrillValue())/2
 for f in b.GetFootprints():
  for pad in f.Pads():
   if pad.GetAttribute()!=p.PAD_ATTRIB_SMD or not pad.IsOnLayer(p.F_Paste):continue
   q=pad.GetBoundingBox();x0,y0,x1,y1=[p.ToMM(v) for v in [q.GetX(),q.GetY(),q.GetRight(),q.GetBottom()]]
   distance=math.hypot(max(x0-x,0,x-x1),max(y0-y,0,y-y1))-radius-expansion
   item=dict(reference=f.GetReference(),pad=pad.GetNumber(),via=via.m_Uuid.AsString(),x_mm=x,y_mm=y,estimated_mask_to_drill_mm=round(distance,6))
   if distance<minimum:minimum=distance;closest=item
   if distance<.05-1e-6:bad.append(item)
result=dict(status='PASS' if not bad else 'FAIL',minimum_estimated_mask_to_drill_mm=round(minimum,6),closest=closest,violations=bad,limits='Bounding-box check, 0.05mm engineering mask-to-drill guard; excludes 25 thermal EP PTH pads requiring factory approval')
(ROOT/'reports/RevB-via-paste-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2));raise SystemExit(bool(bad))
