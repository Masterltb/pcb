from __future__ import annotations
import argparse,json,shutil
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--destination",required=True,type=Path)
    parser.add_argument("--project-id",required=True)
    parser.add_argument("--kicad-project",required=True)
    args=parser.parse_args(); source=Path(__file__).resolve().parents[1]; target=args.destination.resolve()/"pcb-agent-harness"
    if target.exists(): raise SystemExit("Refusing to overwrite "+str(target))
    shutil.copytree(source,target,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    path=target/"contract"/"project.json"; data=json.loads(path.read_text(encoding="utf-8"))
    data["project_id"]=args.project_id; data["sources"]["kicad_project"]=args.kicad_project
    stem=Path(args.kicad_project).stem; parent=str(Path(args.kicad_project).parent).replace("\\","/")
    data["sources"]["schematic"]=parent+"/"+stem+".kicad_sch"; data["sources"]["board"]=parent+"/"+stem+".kicad_pcb"
    for item in data.get("verification_commands",[]): item["command"]=item["command"].replace("REPLACE-ME",stem)
    path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8"); print("Created "+str(target))
if __name__=="__main__": main()
