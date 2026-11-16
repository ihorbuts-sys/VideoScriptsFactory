"""Inspect actual geometry before assembling the coffee scene."""
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_shared_venue as C
import build_assets as P
import prepare_creator_tripo as B

P.clear()
P.MATS.clear()
counter = C.load('bar_counter', (0, 4.55, 0))
counter.scale.z = .68
bpy.context.view_layer.update()
print('COUNTER_BOUNDS', [list(p) for p in B.bounds(C.meshes(counter))], flush=True)
for x in [-1, -.8, 0, .8]:
    for y in [4.1, 4.3, 4.5, 4.8]:
        try:
            print('SURFACE', x, y, C.surface(counter, x, y), flush=True)
        except AssertionError:
            pass
bpy.ops.wm.open_mainfile(filepath=str(P.ROOT.parent / 'barista/tripo-rigged/review/model.blend'))
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
print('BONES', json.dumps([dict(name=b.name, head=list(arm.matrix_world @ b.head),
    tail=list(arm.matrix_world @ b.tail)) for b in arm.pose.bones if 'Right' in b.name]), flush=True)
