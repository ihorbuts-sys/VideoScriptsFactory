"""Restores a catalog snapshot from scripts/versions/<version>/ to where its files came from.

Dry run by default: lists every file, whether the live copy differs and its checksum. Pass --apply to copy.
Before copying, the live files are themselves saved to scripts/versions/_replaced/<timestamp>/ (never deleted).

Run from the VideoGuides repo root:
    python3 -I scripts/versions/restore.py v2_2026-11-16            # dry run
    python3 -I scripts/versions/restore.py v2_2026-11-16 --apply    # restore
"""
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEV = Path.home() / "Documents" / "Development"  # VideoGuides is a symlink, so not HERE.parents


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def main(version, apply):
    snap = HERE / version
    manifest = json.loads((snap / "manifest.json").read_text())
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    changed = 0
    for entry in manifest["files"]:
        source, target = snap / entry["snapshot"], DEV / entry["restoreTo"]
        if sha(source) != entry["sha256"]:
            sys.exit(f"snapshot file changed since it was taken: {source}")
        same = sha(target) == entry["sha256"]
        changed += not same
        print(("same    " if same else "differs ") + entry["restoreTo"])
        if apply and not same:
            if target.exists():
                keep = HERE / "_replaced" / stamp / entry["restoreTo"]
                keep.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, keep)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    print(f"{changed} of {len(manifest['files'])} files differ" + ("; restored" if apply else "; dry run, pass --apply to restore"))
    if apply and changed:
        print(f"replaced live files saved to {HERE / '_replaced' / stamp}")
        print("then rebuild: python3 -I scripts/tools/check_scripts.py --merge and the bundle build, and republish via guide-publish")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], "--apply" in sys.argv[2:])
