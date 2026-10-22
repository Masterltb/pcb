from __future__ import annotations
import argparse,datetime,json,subprocess
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path("."))
    parser.add_argument("--when",choices=["schematic","pcb","release"],required=True)
    parser.add_argument("--execute",action="store_true")
    args=parser.parse_args(); root=args.root.resolve()
    manifest=json.loads((root/"pcb-agent-harness/contract/project.json").read_text(encoding="utf-8"))
    commands=[x for x in manifest.get("verification_commands",[]) if args.when in x.get("when",[])]
    for item in commands: print(item["id"]+": "+item["command"])
    if not args.execute: print("Dry run. Add --execute after reviewing commands."); return 0
    folder=root/"reports"/"harness"; folder.mkdir(parents=True,exist_ok=True); failed=False
    for item in commands:
        run=subprocess.run(item["command"],cwd=root,shell=True,text=True,capture_output=True)
        log=folder/(item["id"]+"-"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".log")
        log.write_text(run.stdout+"\n"+run.stderr,encoding="utf-8")
        print(item["id"]+": exit="+str(run.returncode)+"; log="+str(log.relative_to(root))); failed|=bool(run.returncode)
    return int(failed)
if __name__=="__main__": raise SystemExit(main())
