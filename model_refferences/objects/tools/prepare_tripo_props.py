"""Preserve downloaded Tripo props and prepare grounded, fitted review assets."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
import prepare_creator_tripo as C
from catalog import ASSETS

ASSETS = {**ASSETS,
    'milk_pitcher': ('equipment', 'Open sage barista pitcher with a clear pouring lip and an open rear handle.', (.19, .13, .16)),
    'coffee_grinder': ('equipment', 'Rounded espresso grinder with a downward dosing outlet and an empty clearance bay.', (.18, .25, .40)),
    'portafilter': ('equipment', 'Empty detachable espresso basket with locking ears, a single spout and a charcoal handle.', (.22, .075, .075)),
    'takeaway_cup': ('packaging', 'Closed cream takeaway coffee cup with a charcoal lid and yellow sleeve.', (.09, .09, .16)),
    'coffee_tamper': ('equipment', 'Yellow-handled espresso tamper with a flat charcoal base.', (.058, .058, .09)),
    'knock_box': ('equipment', 'Empty sage espresso knock box with a securely seated charcoal bar.', (.18, .16, .12)),
}

VIEWS = {
    'front': (0, -1, 0), 'back': (0, 1, 0),
    'left': (1, 0, 0), 'right': (-1, 0, 0),
    'top': (0, 0, 1), 'bottom': (0, 0, -1),
    'preview': (.9, -1.7, 1.05),
}


def fit_camera(scene, meshes, direction):
    lo, hi = C.bounds(meshes)
    target = (lo + hi) / 2
    extent = max(hi - lo)
    cam = C.camera(scene, target, direction, extent * 1.3)
    # Update first: an unapplied camera matrix gives misleading projected bounds.
    bpy.context.view_layer.update()
    inverse = cam.matrix_world.inverted()
    points = [inverse @ (o.matrix_world @ v.co) for o in meshes for v in o.data.vertices]
    span_x = max(p.x for p in points) - min(p.x for p in points)
    span_y = max(p.y for p in points) - min(p.y for p in points)
    aspect = scene.render.resolution_x / scene.render.resolution_y
    cam.data.ortho_scale = max(span_y, span_x / aspect) / .86
    centre = Vector(((max(p.x for p in points) + min(p.x for p in points)) / 2,
                     (max(p.y for p in points) + min(p.y for p in points)) / 2, 0))
    cam.location += cam.matrix_world.to_3x3() @ centre
    bpy.context.view_layer.update()
    return cam


def run(asset, yaw, eevee=False, render_views=True):
    folder = P.ROOT / asset / 'tripo-generated'
    sources = list((folder / 'tripo-out').glob('*/model.glb'))
    assert len(sources) == 1, sources
    source = sources[0]
    task = json.loads((source.parent / 'task.json').read_text())
    assert task['status'] == 'success'
    out = folder / 'review'
    out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    P.clear()
    scene = bpy.context.scene
    P.studio(scene)
    if eevee:
        scene.render.engine = 'BLENDER_EEVEE'
        scene.eevee.taa_render_samples = 32
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.view_layers[0].material_override = None
    before = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = set(scene.objects) - before
    root = P.empty('Loca Tripo / ' + asset)
    for obj in imported:
        if obj.parent not in imported:
            obj.parent = root
    root.rotation_euler.z = math.radians(yaw)
    if asset == 'kitchen_tongs':
        root.rotation_euler.x = math.pi / 2
    meshes = [o for o in root.children_recursive if o.type == 'MESH']
    lo, hi = C.bounds(meshes)
    scale = max(ASSETS[asset][2]) / max(hi - lo)
    root.scale = (scale,) * 3
    lo, hi = C.bounds(meshes)
    root.location -= Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    bpy.context.view_layer.update()
    points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    low = min(points, key=lambda p: p.z)
    support = P.empty('Anchor / actual lowest support vertex', low)
    support.parent = root
    support.matrix_parent_inverse = root.matrix_world.inverted()
    support.hide_render = True
    support['measurement'] = 'Actual mesh vertex, not bounding-box bottom'
    root['source_sha256'] = digest
    root['asset_id'] = asset + '_tripo'
    root['source_geometry_unmodified'] = True
    root['placement'] = 'Uniform scale, yaw and actual-vertex grounding only'
    collection = bpy.data.collections.new('Loca Tripo / ' + asset)
    scene.collection.children.link(collection)
    for obj in [root, *root.children_recursive]:
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        collection.objects.link(obj)
    collection.asset_mark()
    collection.asset_data.description = ASSETS[asset][1] + ' Tripo review candidate.'
    lo, hi = C.bounds(meshes)
    extent = max(hi - lo)
    surface = None
    if asset == 'dining_table':
        hit, point, normal, face, obj, matrix = scene.ray_cast(
            bpy.context.evaluated_depsgraph_get(), Vector((0, 0, hi.z + extent)), Vector((0, 0, -1)))
        assert hit and obj in meshes and normal.z > .5
        marker = P.empty('Anchor / actual centre tabletop surface', point)
        marker.parent = root
        marker.matrix_parent_inverse = root.matrix_world.inverted()
        marker.hide_render = True
        for old in list(marker.users_collection):
            old.objects.unlink(marker)
        collection.objects.link(marker)
        surface = list(point)
    bpy.ops.file.pack_all()
    bpy.data.libraries.write(str(out / 'asset.blend'), {collection}, fake_user=True, compress=True)
    P.block('Review floor', (0, 0, -extent * .015), (extent * 7, extent * 7, extent * .03), 'cream', extent * .005)
    floor = next(o for o in scene.objects if o.name.startswith('Review floor'))
    P.lighting((lo + hi) / 2, extent)
    cam = fit_camera(scene, meshes, VIEWS['preview'])
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
                area.spaces.active.shading.type = 'MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'model.blend'), compress=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    for mode in ['rendered', 'shape'] if render_views else []:
        (out / mode).mkdir(exist_ok=True)
        scene.view_layers[0].material_override = P.material('cream') if mode == 'shape' else None
        for name, direction in VIEWS.items():
            floor.hide_render = name == 'bottom'
            cam = fit_camera(scene, meshes, direction)
            scene.render.filepath = str(out / mode / (name + '.png'))
            bpy.ops.render.render(write_still=True)
            bpy.data.objects.remove(cam, do_unlink=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    texture_images = {n.image for o in meshes for m in o.data.materials if m and m.use_nodes
                      for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image}
    meta = dict(id=asset, provider='Tripo H3.1', source=str(source), source_sha256=digest,
                task_id=task['task_id'], credits_consumed=task['credits_consumed'],
                status='review_candidate', source_geometry_unmodified=True,
                dimensions_m=list(hi - lo), root_yaw_deg=yaw, uniform_scale_factor=scale,
                lowest_vertex_z=low.z, actual_tabletop_surface=surface,
                triangles=sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons),
                mesh_parts=len(meshes), textures=[dict(name=i.name, resolution=list(i.size), packed=bool(i.packed_file))
                                                for i in texture_images],
                limitations=['Longest dimension calibrated to planned size; other proportions come from generation.',
                             'No articulation, contact patch or scene usability approval.',
                             'Stored support vertex and tabletop surface do not replace placement review.'])
    (out / 'metadata.json').write_text(json.dumps(meta, indent=2) + '\n')
    print('TRIPO_PROP_REVIEW_READY', asset, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('assets', nargs='+', choices=list(ASSETS))
    parser.add_argument('--yaw', type=float)
    parser.add_argument('--eevee', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    for asset in args.assets:
        yaw = args.yaw if args.yaw is not None else (0 if asset in ['kettle', 'kitchen_tongs'] else -90)
        run(asset, yaw, args.eevee)
