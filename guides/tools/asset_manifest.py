#!/usr/bin/env python3
"""Pins the active binary assets that git does not track (renders, scenes' models, the creator, hands, step pictures)
by sha256 in assets/manifest.json, and checks the disk against it.

    python3 guides/tools/asset_manifest.py write     # after an approved render, publish or new model
    python3 guides/tools/asset_manifest.py verify    # exit 1 and list what is missing or changed
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "assets" / "manifest.json"
# The active P0 set: the published guide files and every model the P0 scene builders load.
ACTIVE = [
    "guides/p0/renders/*.png",
    "model_refferences/creator/lineart/asset.blend",
    "guides/blender_motion/vendor/para-fps-arms/hand-poses.blend",
    "model_refferences/objects/milk_pitcher/functional/asset.blend",
    "model_refferences/objects/kettle/tripo-generated/review/asset.blend",
    "model_refferences/objects/pizza/tripo-generated/review/asset.blend",
    "model_refferences/objects/salad_portion/tripo-generated/review/asset.blend",
    "previews/clay-3d/p0/assets/*",
    # Approved in P0 line art by the owner 2026-11-16 (OBJECTS.md "Owner review 2026-11-16").
    "model_refferences/objects/burger/tripo-generated/review/asset.blend",
    "model_refferences/objects/cake_slice/tripo-generated/review/asset.blend",
    "model_refferences/objects/serving_bowl/tripo-generated/review/asset.blend",
    "model_refferences/objects/salon_chair/tripo-generated/review/asset.blend",
    "model_refferences/objects/wall_shelf/tripo-generated/review/asset.blend",
    "model_refferences/objects/display_case/tripo-generated/review/asset.blend",
    "model_refferences/objects/serving_tray/tripo-generated/review/asset.blend",
    "model_refferences/objects/hair_clipper/tripo-generated/review/asset.blend",
    "model_refferences/objects/dumbbell/tripo-generated/review/asset.blend",
    "model_refferences/objects/takeaway_cup/tripo-generated/review/asset.blend",
    "model_refferences/objects/laptop/tripo-generated/review/asset.blend",
    "model_refferences/objects/treatment_bed/one-face-hole-v1/asset.blend",
    "model_refferences/objects/food_truck/lineart/asset.blend",
    "model_refferences/objects/food_truck/tripo/tripo-out/food-truck-51baebf5/model.glb",
]


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def scan():
    files = sorted({p for pattern in ACTIVE for p in ROOT.glob(pattern) if p.is_file()})
    return {str(p.relative_to(ROOT)): {"sha256": digest(p), "bytes": p.stat().st_size} for p in files}


def main(argv):
    if argv[:1] == ["write"]:
        files = scan()
        MANIFEST.parent.mkdir(exist_ok=True)
        MANIFEST.write_text(json.dumps({"patterns": ACTIVE, "files": files}, indent=1) + "\n")
        print(f"{len(files)} files, {sum(f['bytes'] for f in files.values()) / 2**20:.0f} MB pinned")
        return 0
    if argv[:1] == ["verify"]:
        pinned = json.loads(MANIFEST.read_text())["files"]
        current = scan()
        missing = sorted(set(pinned) - set(current))
        changed = sorted(p for p in pinned if p in current and current[p]["sha256"] != pinned[p]["sha256"])
        unpinned = sorted(set(current) - set(pinned))
        for label, items in (("missing", missing), ("changed", changed), ("not pinned", unpinned)):
            for item in items:
                print(f"{label}: {item}")
        print(f"{len(pinned)} pinned, {len(missing)} missing, {len(changed)} changed, {len(unpinned)} not pinned")
        return 1 if missing or changed else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
