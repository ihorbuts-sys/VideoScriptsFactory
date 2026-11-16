"""Reuse the approved sculpted window as floor-to-ceiling glazing, without API cost."""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
from prepare_tripo_props import fit_camera


def height(z):
    old = [0, .18, .23, .735, .80, 1.22, 1.445031]
    new = [0, .06, .12, 1.35, 1.42, 2.65, 2.8]
    if z <= 0:
        return 0
    for index in range(len(old) - 1):
        if z <= old[index + 1]:
            u = (z - old[index]) / (old[index + 1] - old[index])
            return new[index] * (1 - u) + new[index + 1] * u
    return 2.8


def run():
    folder = P.ROOT / 'window'
    source = folder / 'tripo-generated/scene-ready/model.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source))
    P.MATS.clear()
    scene = bpy.context.scene
    root = next(o for o in scene.objects if o.get('asset_id') == 'window_scene_ready')
    keep = {root, *root.children_recursive}
    for obj in list(scene.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj, do_unlink=True)
    meshes = [o for o in root.children_recursive if o.type == 'MESH']
    for obj in meshes:
        obj.data = obj.data.copy()
        matrix = obj.matrix_world.copy()
        inverse = matrix.inverted()
        for vertex in obj.data.vertices:
            point = matrix @ vertex.co
            point.z = height(point.z)
            vertex.co = inverse @ point
        obj.data.update()
        if not obj.get('glazing'):
            obj.data.materials.clear()
            obj.data.materials.append(P.material('sage'))
            obj.data.materials.append(P.material('cream'))
            for face in obj.data.polygons:
                face.material_index = 1 if (matrix @ face.center).z < .075 else 0
        else:
            for material in obj.data.materials:
                material.surface_render_method = 'BLENDED'
    root['asset_id'] = 'window_full_height'
    root['local_adaptation'] = 'Long vertical panes; crossbar retained near 1.4m; shallow floor sill; same sculpted frame'
    root['generation_credits'] = 0
    lo, hi = P.bounds(meshes)
    assert abs(lo.z) < .001 and abs(hi.z - 2.8) < .001, (lo.z, hi.z)
    collection = next(c for c in root.users_collection if c.name.startswith('Loca scene-ready'))
    out = folder / 'full-height'
    out.mkdir(exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.data.libraries.write(str(out / 'asset.blend'), {collection}, fake_user=True, compress=True)
    P.studio(scene)
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 32
    scene.render.resolution_x = 640
    scene.render.resolution_y = 960
    scene.view_layers[0].material_override = None
    P.lighting(Vector((0, 0, 1.4)), 1.8)
    P.block('Review floor', (0, 0, -.04), (5, 5, .08), 'cream', .01)
    P.block('Glazing diagnostic / yellow object behind', (-.2, .65, 1.2), (.3, .2, .3), 'yellow', .03)
    fit_camera(scene, meshes, (.6, -1.7, .2))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'model.blend'), compress=True)
    scene.render.filepath = str(out / 'preview.png')
    bpy.ops.render.render(write_still=True)
    (out / 'metadata.json').write_text(json.dumps(dict(id='window_full_height', height_m=2.8,
        dimensions_m=list(hi - lo), source=str(source.relative_to(P.BASE)), local_processing_credits=0,
        original_assets_preserved=True, status='native_full_height_window_ready'), indent=2) + '\n')
    print('FULL_HEIGHT_WINDOW_READY', list(hi - lo), flush=True)


if __name__ == '__main__':
    run()
