"""Builds food_truck/lineart/asset.blend, the line-art cache of the owner's Tripo food truck (approved 2026-11-16),
with the recipe of its approved candidate render: uniform scale x2.5 about the base centre (3.0 m tall), then the
renderer's scan cleanup (weld, normals, loose parts under 2% of the diagonal, decimate 0.1), then a turn about Z so
the truck faces +X with the service window facing +Y, base at Z 0, centred on X/Y. The Tripo download is only read.

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P prepare_lineart.py
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "guides/tools"))
import render_objects as R  # noqa: E402

SOURCE = HERE / "tripo/tripo-out/food-truck-51baebf5/model.glb"
CACHE = HERE / "lineart"
SCALE = 2.5
# The approved renders aimed the side view at azimuth -124.5 deg and the 3/4 front at -79.5 deg, so in plan the
# window faces 34.5 deg and the front -55.5 deg from +X; turning the truck +55.5 deg puts the front on +X.
TURN_DEG = 55.5


def points(meshes):
    out = []
    for o in meshes:
        co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", co); out.append(co.reshape(-1, 3))
    return np.concatenate(out)


def transform(meshes, fn):
    for o in meshes:
        co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", co)
        o.data.vertices.foreach_set("co", fn(co.reshape(-1, 3)).ravel()); o.data.update()


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in meshes:
    o.data.transform(o.matrix_world); o.parent = None; o.matrix_world.identity()
for o in [o for o in bpy.data.objects if o.type != "MESH"]:
    bpy.data.objects.remove(o, do_unlink=True)

p = points(meshes); lo, hi = p.min(0), p.max(0)
centre = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
transform(meshes, lambda co: (co - centre) * SCALE)
report = R.clean_scan_mesh(meshes, **R.SCAN_PREP | {"decimate": .1})

a = math.radians(TURN_DEG); rot = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
transform(meshes, lambda co: co @ rot.T)
p = points(meshes); lo, hi = p.min(0), p.max(0)
shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
transform(meshes, lambda co: co - shift)
p = points(meshes); dims = (p.max(0) - p.min(0)).round(3).tolist()
for o in meshes:
    o.data.materials.clear()

CACHE.mkdir(exist_ok=True)
bpy.data.libraries.write(str(CACHE / "asset.blend"), set(meshes), compress=True)
meta = dict(source=str(SOURCE), source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(), original_preserved=True,
            credits=30, tripo_task="51baebf5-a44b-4b95-b775-cd1a09e12372", approved="owner 2026-11-16",
            recipe=dict(uniform_scale=SCALE, scan_cleanup=report, turn_deg_about_z=TURN_DEG,
                        axes="front +X, service window +Y, up +Z, base at Z 0, centred on X/Y"),
            faces=sum(len(o.data.polygons) for o in meshes), dimensions_m=dims, built_by=Path(__file__).name)
(CACHE / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
print("CACHE", CACHE / "asset.blend", dims, meta["faces"])
