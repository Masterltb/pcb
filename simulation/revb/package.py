"""Package the simulator and compiled firmware, never fabrication data."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    files = [p for p in HERE.rglob("*") if p.is_file() and
             not any(s in (".pio", ".local", "__pycache__") for s in p.relative_to(HERE).parts)
             and p.suffix not in (".exe", ".vcd")]
    files += [HERE/".pio/build/esp32dev/firmware.bin", HERE/".pio/build/esp32dev/firmware.elf",
              ROOT/"docs/project/revb-simulation-task.md",
              ROOT/"reports/revb/verified/RevB-simulation-check.json"]
    for path in files:
        if not path.is_file():
            raise SystemExit(f"Missing {path}; build and verify before packaging")
    prefix = "FreshVend-RevB-simulation/"
    manifest = {
        "type": "functional simulation; NOT manufacturing or real-machine firmware",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "files": {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in files},
    }
    out = HERE/".local/FreshVend-RevB-simulation.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, prefix+str(path.relative_to(ROOT)).replace("\\", "/"))
        archive.writestr(prefix+"manifest.json", json.dumps(manifest, indent=2))
    with zipfile.ZipFile(out) as archive:
        assert archive.testzip() is None
        for name, expected in manifest["files"].items():
            assert hashlib.sha256(archive.read(prefix+name)).hexdigest() == expected
    print(out)
    print("SHA256", hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
