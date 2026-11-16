"""Render close views of the doorway, table and grip for scene review."""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
import build_shared_venue as C
import prepare_creator_tripo as B
from coffee_scene_details import polish_practicals

OUT = P.BASE / 'catalog/coffee-ordering-v2'
bpy.ops.wm.open_mainfile(filepath=str(OUT / 'scene.blend'))
scene = bpy.context.scene
scene.frame_set(1)
polish_practicals(scene)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'scene.blend'), compress=True)
camera = scene.camera
camera.animation_data_clear()
camera.data.animation_data_clear()
scene.render.resolution_x = 720
scene.render.resolution_y = 960
scene.eevee.taa_render_samples = 48
door = next(o for o in scene.objects if o.get('asset_family') == 'glazed_door')
hinge = next(o for o in door.children_recursive if o.get('max_open_angle_deg'))
hinge.animation_data_clear()
hinge.rotation_euler.z = 0
for name, p, target, lens in [
    ('door-closed', (-1.30, -2.1, 1.30), (-1.30, 0, 1.12), 30),
    ('door-upper-detail', (-1.30, -1.1, 2.05), (-1.30, 0, 1.99), 55),
    ('table-lighting', (.15, .50, 1.70), (1.15, 1.55, .90), 25),
    ('table-pendant', (-.30, .30, 1.85), (1.15, 1.55, 1.85), 20),
]:
    camera.location = p
    camera.rotation_quaternion = (Vector(target)-camera.location).to_track_quat('-Z', 'Y')
    camera.data.lens = lens
    scene.render.filepath = str(OUT / (name+'.png'))
    bpy.ops.render.render(write_still=True)
print('SET_DETAIL_PROBES_READY', flush=True)
