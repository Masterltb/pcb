from __future__ import annotations
import argparse, csv, json
from pathlib import Path

FAIL=[]; VALID={"todo","in_progress","blocked","verified","waived","not-applicable"}
REQ=("id","title","source","priority","verification_method","status")
INT=("id","name","origin","destination","connector_and_mate","verification","status")

def fail(msg): FAIL.append(msg)
def read_rows(path, fields):
    if not path.exists(): fail("Missing "+str(path)); return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader=csv.DictReader(handle)
        if not reader.fieldnames: fail("No header in "+str(path)); return []
        for field in fields:
            if field not in reader.fieldnames: fail(str(path)+": missing "+field)
        rows=list(reader)
    seen=set()
    for line,row in enumerate(rows,2):
        ident=row.get("id","").strip()
        if not ident: fail(f"{path}:{line}: empty id")
        if ident in seen: fail(f"{path}:{line}: duplicate id {ident}")
        seen.add(ident)
        for field in fields:
            if not row.get(field,"").strip(): fail(f"{path}:{line}: empty {field}")
        if row.get("status","") not in VALID: fail(f"{path}:{line}: invalid status")
    return rows

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path("."))
    parser.add_argument("--release",action="store_true")
    args=parser.parse_args(); root=args.root.resolve(); contract=root/"pcb-agent-harness"/"contract"
    try: manifest=json.loads((contract/"project.json").read_text(encoding="utf-8"))
    except Exception as exc: fail("Invalid project.json: "+str(exc)); manifest={}
    for key in ("schema_version","project_id","phase","toolchain","sources","release"):
        if key not in manifest: fail("project.json: missing "+key)
    requirements=read_rows(contract/"requirements.csv",REQ)
    interfaces=read_rows(contract/"interfaces.csv",INT)
    try:
        active=[item for item in json.loads((contract/"work-items.json").read_text(encoding="utf-8"))["work_items"] if item.get("status")=="in_progress"]
        if len(active)>1: fail("work-items.json: WIP violation")
    except Exception as exc: fail("Invalid work-items.json: "+str(exc))
    if args.release:
        for path,rows in ((contract/"requirements.csv",requirements),(contract/"interfaces.csv",interfaces)):
            for line,row in enumerate(rows,2):
                if row.get("priority") in {"critical","high"} and row.get("status") not in {"verified","waived","not-applicable"}: fail(f"{path}:{line}: release blocked by {row.get('id')}")
                if row.get("status")=="verified" and not row.get("evidence","").strip(): fail(f"{path}:{line}: verified item lacks evidence")
        if manifest.get("release",{}).get("gerber_allowed") and not manifest["release"].get("approval_record"): fail("project.json: gerber_allowed requires approval_record")
    if FAIL:
        print("CONTRACT FAIL"); print("\n".join("- "+x for x in FAIL)); return 1
    print("CONTRACT PASS"+(" release" if args.release else "")); return 0
if __name__=="__main__": raise SystemExit(main())
