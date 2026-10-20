"""Rebuild engineering review files with gates at every design stage.

Run with KiCad Python. Requires locally prepared Java25/Freerouting2.5 tools.
No purchase or Gerber export. Never suppress electrical DRC errors.
"""
from pathlib import Path
import subprocess,sys,re
ROOT=Path(__file__).resolve().parents[1]
def run(*args):
    print('RUN',*args,flush=True);subprocess.run([str(a) for a in args],cwd=ROOT,check=True)
def gates(stage,unfinished=False):
    erc=ROOT/f'reports/RevA2-{stage}-erc.rpt';drc=ROOT/f'reports/RevA2-{stage}-drc.rpt'
    run('kicad-cli','sch','erc','--output',erc,'hardware/FV-CTRL_RevA2.kicad_sch')
    if not re.search(r'ERC messages: 0\s+Errors 0\s+Warnings 0',erc.read_text()):raise RuntimeError('ERC gate '+stage)
    if not (ROOT/'hardware/FV-CTRL_RevA2.kicad_pcb').exists():return
    run('kicad-cli','pcb','drc','--schematic-parity','--output',drc,'hardware/FV-CTRL_RevA2.kicad_pcb')
    t=drc.read_text();violations=re.findall(r'^\[([^]]+)\]:',t,re.M)
    permitted={'unconnected_items','silk_overlap','silk_over_copper','silk_edge_clearance','nonmirrored_text_on_back_layer'} if unfinished else set()
    if set(violations)-permitted:raise RuntimeError('DRC gate '+stage+': '+str(set(violations)-permitted))
def layout(mode):run(sys.executable,'tools/rev_a2_layout.py',mode)
def route(power):
    suffix='-power' if power else ''
    layout('power-dsn' if power else 'dsn')
    run(ROOT/'.agents/router/java25/jdk-25.0.4.1+1-jre/bin/java.exe','-jar',ROOT/'.agents/router/freerouting-2.5.0.jar','-de',f'reports/RevA2{suffix}.dsn','-do',f'reports/RevA2{suffix}.ses','--router.automatic_neckdown=false','--router.optimizer.enabled=false','-mp','20','-mt','4')
    layout('power-ses' if power else 'ses')
    gates('power' if power else 'routing',True)
if __name__=='__main__':
    run(sys.executable,'tools/rev_a2_design.py')
    # Prior board remains available for audit but intentionally differs until sync.
    run('kicad-cli','sch','erc','--output','reports/RevA2-input-erc.rpt','hardware/FV-CTRL_RevA2.kicad_sch')
    run('kicad-cli','pcb','drc','--schematic-parity','--output','reports/RevA2-before-sync-drc.rpt','hardware/FV-CTRL_RevA2.kicad_pcb')
    run('kicad-cli','sch','export','netlist','--format','kicadxml','--output','reports/RevA2.net.xml','hardware/FV-CTRL_RevA2.kicad_sch')
    run(sys.executable,'tools/verify_rev_a2.py')
    layout('place');gates('placement',True)
    route(True);route(False)
    layout('finish');gates('ground',True)
    layout('silk');gates('silk')
    run(sys.executable,'tools/rev_a2_procurement.py')
    run('kicad-cli','sch','export','netlist','--format','kicadxml','--output','reports/RevA2.net.xml','hardware/FV-CTRL_RevA2.kicad_sch')
    gates('final');run(sys.executable,'tools/verify_rev_a2.py','--pcb')
