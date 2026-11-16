"""Add measured tool anchors and a hollow cup without changing downloaded GLBs."""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
import prepare_creator_tripo as B
from prepare_tripo_props import fit_camera


def circle(points):
    xy = np.asarray([(p.x, p.y) for p in points])
    a = np.column_stack((2 * xy[:, 0], 2 * xy[:, 1], np.ones(len(xy))))
    x, y, c = np.linalg.lstsq(a, np.sum(xy * xy, axis=1), rcond=None)[0]
    radius = math.sqrt(max(.00001, c + x * x + y * y))
    return Vector((float(x), float(y), 0)), radius


def samples(obj):
    shader = obj.data.materials[0].node_tree.nodes.get('Principled BSDF')
    image = shader.inputs['Base Color'].links[0].from_node.image
    pixels = np.asarray(image.pixels[:], dtype=np.float32).reshape(image.size[1], image.size[0], 4)
    layer = obj.data.uv_layers.active.data
    uv = np.array([sum((layer[i].uv for i in f.loop_indices), Vector((0, 0))) / len(f.loop_indices) for f in obj.data.polygons])
    rgb = pixels[np.clip((uv[:, 1] * image.size[1]).astype(int), 0, image.size[1] - 1),
                 np.clip((uv[:, 0] * image.size[0]).astype(int), 0, image.size[0] - 1), :3]
    centres = np.array([obj.matrix_world @ face.center for face in obj.data.polygons])
    return centres, rgb


def run(aid):
    folder = P.ROOT / aid
    bpy.ops.wm.open_mainfile(filepath=str(folder / 'tripo-generated/review/model.blend'))
    P.MATS.clear()
    scene = bpy.context.scene
    original_root = next(o for o in scene.objects if o.get('asset_id') == aid + '_tripo')
    models = [o for o in original_root.children_recursive if o.type == 'MESH']
    keep = {original_root, *original_root.children_recursive}
    for item in list(scene.objects):
        if item not in keep:
            bpy.data.objects.remove(item, do_unlink=True)
    root = P.empty('Functional coffee / ' + aid)
    original_root.parent = root
    root['asset_id'] = aid + '_functional'
    root['source_sha256'] = original_root['source_sha256']
    lo, hi = B.bounds(models)
    h = hi.z
    vertices = [o.matrix_world @ v.co for o in models for v in o.data.vertices]
    points = np.asarray(vertices)
    centres, rgb = samples(models[0])
    anchors = {}
    if aid in ['latte_cup', 'portafilter', 'milk_pitcher']:
        top = [p for p in vertices if p.z > h * .94]
        centre, radius = circle(top)
        centre.z = h
        anchors['rim'] = list(centre)
        anchors['radius'] = radius
        if aid == 'portafilter':
            dark = centres[(rgb.max(axis=1) < .44) & (centres[:, 2] > h * .30)]
            grip = Vector(np.median(dark, axis=0).tolist())
            anchors['grip'] = list(grip)
            bottom = points[points[:, 2] < .005]
            anchors['spout'] = np.mean(bottom, axis=0).tolist()
        elif aid == 'milk_pitcher':
            yellow = centres[(rgb[:, 0] > .60) & (rgb[:, 1] > .45) & (rgb[:, 2] < .55)]
            handle = Vector(np.median(yellow, axis=0).tolist())
            direction = (handle - centre).xy.normalized()
            high_points = [p for p in vertices if p.z > h * .88]
            tip = min(high_points, key=lambda p: (p.xy - centre.xy).dot(direction))
            handle.z = h * .64
            anchors['grip'] = list(handle)
            anchors['spout'] = list(tip)
        else:
            direction = Vector((1, 0, 0))
            far = [p for p in vertices if (p.xy - centre.xy).length > radius * 1.35 and h * .25 < p.z < h * .85]
            if far:
                direction = Vector(np.mean([p - Vector((centre.x, centre.y, h * .55)) for p in far], axis=0).tolist())
                direction.z = 0
                direction.normalize()
            anchors['grip'] = list(Vector((centre.x, centre.y, h * .55)) + direction * (radius + .018))
            # Reuse the external clay cup, cut a real cavity and remove its baked coffee/heart.
            obj = models[0]
            mesh = obj.data.copy()
            mesh.transform(obj.matrix_world)
            obj.parent = root
            obj.matrix_world.identity()
            obj.data = mesh
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000003)
            bm.to_mesh(mesh)
            bm.free()
            mesh.materials.clear()
            mesh.materials.append(P.material('cream'))
            cutter = P.lathe('Temporary / cup cavity', [(0, h * .12), (radius * .50, h * .12),
                (radius * .76, h * .30), (radius * .91, h * .70), (radius * .96, h * .95),
                (radius * .96, h + .03), (0, h + .03)], (centre.x, centre.y, 0), 'cream')
            modifier = obj.modifiers.new('Functional hollow interior', 'BOOLEAN')
            modifier.operation = 'DIFFERENCE'
            modifier.solver = 'EXACT'
            modifier.object = cutter
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.data.objects.remove(cutter, do_unlink=True)
            for face in obj.data.polygons:
                face.material_index = 0
            models = [obj]
            anchors['liquid_min_z'] = h * .18
            anchors['liquid_final_z'] = h * .85
    elif aid == 'espresso_machine':
        cream = centres[(rgb.min(axis=1) > .65) & (np.abs(centres[:, 0]) < .13) &
                        (centres[:, 2] > h * .30) & (centres[:, 2] < h * .75)]
        assert len(cream) > 20
        point = np.median(cream, axis=0)
        point[2] = np.quantile(cream[:, 2], .05)
        anchors['socket'] = point.tolist()
        anchors['cup_bay'] = [float(point[0]), float(point[1]), float(h * .07)]
        anchors['start_button'] = [float(lo.x + (hi.x - lo.x) * .16), float(lo.y), float(h * .71)]
    elif aid == 'coffee_grinder':
        region = centres[(rgb.max(axis=1) < .40) & (centres[:, 2] > h * .28) & (centres[:, 2] < h * .62)]
        front = region[region[:, 1] < np.quantile(region[:, 1], .3)]
        point = np.median(front, axis=0)
        anchors['outlet'] = point.tolist()
    for name, point in anchors.items():
        if not isinstance(point, list):
            continue
        anchor = P.empty('Anchor / ' + name, point)
        anchor.parent = root
        anchor['function'] = name
        anchor.hide_render = True
    collection = bpy.data.collections.new('Loca functional coffee / ' + aid)
    scene.collection.children.link(collection)
    for item in [root, *root.children_recursive]:
        for old in list(item.users_collection):
            old.objects.unlink(item)
        collection.objects.link(item)
    collection.asset_mark()
    out = folder / 'functional'
    out.mkdir(exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.data.libraries.write(str(out / 'asset.blend'), {collection}, fake_user=True, compress=True)
    P.studio(scene)
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 32
    scene.view_layers[0].material_override = None
    extent = max(hi - lo)
    P.lighting((lo + hi) / 2, extent)
    P.block('Review floor', (0, 0, -.015), (3, 3, .03), 'cream', .005)
    fit_camera(scene, models, (.7, -1.7, 1.1))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'model.blend'), compress=True)
    scene.render.filepath = str(out / 'preview.png')
    bpy.ops.render.render(write_still=True)
    (out / 'metadata.json').write_text(json.dumps(dict(id=aid, source_sha256=root['source_sha256'],
        original_glb_preserved=True, local_processing_credits=0, anchors=anchors,
        status='functional_asset_pending_contact_validation'), indent=2) + '\n')
    print('FUNCTIONAL_COFFEE_READY', aid, json.dumps(anchors), flush=True)


if __name__ == '__main__':
    for aid in ['espresso_machine', 'portafilter', 'milk_pitcher', 'coffee_grinder', 'latte_cup']:
        run(aid)
