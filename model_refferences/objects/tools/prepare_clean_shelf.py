"""Preserve the generated shelf and provide an unmarked clay-material variant."""
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
import build_shared_venue as C
from coffee_scene_details import clean_shelf_material
from prepare_tripo_props import fit_camera

folder = P.ROOT / 'wall_shelf/tripo-generated'
bpy.ops.wm.open_mainfile(filepath=str(folder / 'review/model.blend'))
P.MATS.clear()
root = next(o for o in bpy.context.scene.objects if o.get('asset_id') == 'wall_shelf_tripo')
clean_shelf_material(root)
collection = next(c for c in root.users_collection if c.name.startswith('Loca Tripo'))
root['asset_id'] = 'wall_shelf_unmarked'
out = folder / 'scene-ready'
out.mkdir(exist_ok=True)
bpy.ops.file.pack_all()
bpy.data.libraries.write(str(out / 'asset.blend'), {collection}, fake_user=True, compress=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 32
scene.view_layers[0].material_override = None
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'model.blend'), compress=True)
for name, direction in [('preview', (.9, -1.7, 1.05)), ('back', (0, 1, .1)), ('bottom', (0, 0, -1))]:
    for obj in scene.objects:
        if obj.name.startswith('Review floor'):
            obj.hide_render = name == 'bottom'
    fit_camera(scene, C.meshes(root), direction)
    scene.render.filepath = str(out / (name+'.png'))
    bpy.ops.render.render(write_still=True)
(out / 'metadata.json').write_text(json.dumps(dict(id='wall_shelf', source_glb_preserved=True,
    source_sha256=root['source_sha256'], local_processing_credits=0,
    changes=['Removed the baked QR marking by replacing the source texture with unmarked clay materials.',
             'Kept the generated geometry; used readable wood grain for the board and sage for the brackets.']), indent=2)+'\n')
print('UNMARKED_SHELF_READY', flush=True)
