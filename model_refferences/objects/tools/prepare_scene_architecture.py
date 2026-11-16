"""Derive hinged, transparent architecture from unchanged Tripo downloads."""
import hashlib
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
from prepare_tripo_props import fit_camera


def clear_glass():
    mat = bpy.data.materials.new('Loca / clear lightly frosted clay glass')
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.94, .98, .96, 1)
    shader.inputs['Transmission Weight'].default_value = 1
    shader.inputs['Roughness'].default_value = .08
    shader.inputs['IOR'].default_value = 1.42
    # A mostly transparent surface also works in Eevee without ray-traced refraction.
    transparent = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    transparent.inputs['Color'].default_value = (.97, .99, .98, 1)
    mix = mat.node_tree.nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value = .97
    mat.node_tree.links.new(shader.outputs['BSDF'], mix.inputs[1])
    mat.node_tree.links.new(transparent.outputs['BSDF'], mix.inputs[2])
    output = mat.node_tree.nodes.get('Material Output')
    mat.node_tree.links.new(mix.outputs[0], output.inputs['Surface'])
    mat.surface_render_method = 'DITHERED'
    return mat


def classify_glazing(obj, aid):
    shader = obj.data.materials[0].node_tree.nodes.get('Principled BSDF')
    image = shader.inputs['Base Color'].links[0].from_node.image
    pixels = np.asarray(image.pixels[:], dtype=np.float32).reshape(image.size[1], image.size[0], 4)
    layer = obj.data.uv_layers.active.data
    uvs = np.array([sum((layer[i].uv for i in f.loop_indices), Vector((0, 0))) / len(f.loop_indices)
                    for f in obj.data.polygons])
    rgb = pixels[np.clip((uvs[:, 1] * image.size[1]).astype(int), 0, image.size[1] - 1),
                 np.clip((uvs[:, 0] * image.size[0]).astype(int), 0, image.size[0] - 1), :3]
    centres = np.array([obj.matrix_world @ f.center for f in obj.data.polygons])
    pale = (rgb.min(axis=1) > .4) & ((rgb.max(axis=1) - rgb.min(axis=1)) < .1)
    if aid == 'glazed_door':
        region = (np.abs(centres[:, 0]) < .36) & (centres[:, 2] > .63) & (centres[:, 2] < 2.07)
    else:
        region = (np.abs(centres[:, 0]) < .49) & (centres[:, 2] > .22) & (centres[:, 2] < 1.24)
    selected = pale & region
    assert selected.sum() > 3000, (aid, int(selected.sum()))
    for face, use_glass in zip(obj.data.polygons, selected):
        if use_glass:
            face.material_index = 1
    return int(selected.sum())


def object_from_bmesh(name, source, predicate, cap=False):
    bm = bmesh.new()
    bm.from_mesh(source.data)
    delete = [f for f in bm.faces if not predicate(f)]
    bmesh.ops.delete(bm, geom=delete, context='FACES')
    if cap:
        boundary = [e for e in bm.edges if e.is_boundary]
        result = bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
        for face in result.get('faces', []):
            face.material_index = 2
    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    assert len(mesh.polygons) > 0, name
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for mat in source.data.materials:
        obj.data.materials.append(mat)
    return obj


def run(aid):
    folder = P.ROOT / aid / 'tripo-generated'
    meta = json.loads((folder / 'review/metadata.json').read_text())
    source = Path(meta['source'])
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(folder / 'review/model.blend'))
    P.MATS.clear()
    old_root = next(o for o in bpy.context.scene.objects if o.get('asset_id') == aid + '_tripo')
    obj = next(o for o in old_root.children_recursive if o.type == 'MESH')
    old_matrix = obj.matrix_world.copy()
    keep = obj.data.copy()
    keep.transform(old_matrix)
    for item in list(bpy.context.scene.objects):
        if item != obj:
            bpy.data.objects.remove(item, do_unlink=True)
    obj.parent = None
    obj.matrix_world.identity()
    obj.data = keep
    obj.data.materials.append(clear_glass())
    obj.data.materials.append(P.material('sage'))
    glazing_faces = classify_glazing(obj, aid)
    depth = max(v.co.y for v in obj.data.vertices) - min(v.co.y for v in obj.data.vertices)
    wanted_depth = .18 if aid == 'glazed_door' else .20
    for vertex in obj.data.vertices:
        vertex.co.y *= wanted_depth / depth
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000003)
    if aid == 'glazed_door':
        for point, normal in [((-.465, 0, 0), (1, 0, 0)), ((.465, 0, 0), (1, 0, 0)),
                              ((0, 0, .13), (0, 0, 1)), ((0, 0, 2.17), (0, 0, 1))]:
            bmesh.ops.bisect_plane(bm, geom=[*bm.verts, *bm.edges, *bm.faces],
                                  plane_co=point, plane_no=normal, dist=.000001)
    bm.to_mesh(obj.data)
    bm.free()
    root = P.empty('Scene-ready / ' + aid)
    root['asset_id'] = aid + '_scene_ready'
    root['source_sha256'] = digest
    root['derived_geometry'] = 'UV-color glazing selection; depth calibrated; source file preserved'
    if aid == 'glazed_door':
        def leaf(face):
            centre = face.calc_center_median()
            return -.465 < centre.x < .465 and .13 < centre.z < 2.17
        jamb = object_from_bmesh('Door / fixed jamb and threshold', obj, lambda f: not leaf(f))
        panel = object_from_bmesh('Door / movable leaf and original handle', obj, lambda f: leaf(f) and f.material_index != 1)
        pane = P.block('Door / flat clear pane', (0, .012, 1.35), (.665, .009, 1.40), 'glass', .004)
        pane.data.materials.clear()
        pane.data.materials.append(clear_glass())
        pane['ghost_role'] = 'absent'
        pane['glazing'] = True
        hinge = P.empty('Door / left hinge', (-.465, .01, 0))
        hinge.parent = root
        hinge['control'] = 'Rotate local Z from 0 to +88 degrees into the room'
        hinge['max_open_angle_deg'] = 88
        for moving in [panel, pane]:
            moving.parent = hinge
            moving.location -= hinge.location
        jamb.parent = root
        parts = [jamb, panel, pane]
    else:
        frame = object_from_bmesh('Window / original clay frame and sill', obj, lambda f: f.material_index != 1)
        frame.parent = root
        parts = [frame]
        for x in [-.257, .257]:
            for z, height in [(.4825, .505), (1.01, .42)]:
                pane = P.block('Window / flat clear pane', (x, -.012, z), (.43, .009, height), 'glass', .004)
                pane.data.materials.clear()
                pane.data.materials.append(clear_glass())
                pane.parent = root
                pane['ghost_role'] = 'absent'
                pane['glazing'] = True
                parts.append(pane)
    bpy.data.objects.remove(obj, do_unlink=True)
    collection = bpy.data.collections.new('Loca scene-ready / ' + aid)
    bpy.context.scene.collection.children.link(collection)
    for item in [root, *root.children_recursive]:
        for old in list(item.users_collection):
            old.objects.unlink(item)
        collection.objects.link(item)
    collection.asset_mark()
    out = folder / 'scene-ready'
    out.mkdir(exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.data.libraries.write(str(out / 'asset.blend'), {collection}, fake_user=True, compress=True)
    scene = bpy.context.scene
    P.studio(scene)
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.view_layers[0].material_override = None
    P.lighting(Vector((0, 0, .8)), 1.4)
    P.block('Review floor', (0, .3, -.04), (5, 5, .08), 'cream', .01)
    # A colored object behind the panes makes transmission verifiable.
    P.block('Transparency diagnostic / yellow block behind', (-.2, .65, 1), (.25, .2, .3), 'yellow', .03)
    P.block('Transparency diagnostic / teal block behind', (.2, .70, 1.35), (.23, .2, .3), 'teal', .03)
    camera = fit_camera(scene, parts, (.8, -1.7, .55))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'model.blend'), compress=True)
    for state in ['closed', 'open'] if aid == 'glazed_door' else ['glazing']:
        if aid == 'glazed_door':
            hinge.rotation_euler.z = math.radians(88) if state == 'open' else 0
        scene.render.filepath = str(out / (state + '.png'))
        bpy.ops.render.render(write_still=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    report = dict(id=aid, source_sha256=digest, source_glb_preserved=True,
                  local_processing_credits=0, selected_glazing_faces=glazing_faces,
                  depth_m=wanted_depth, parts=[o.name for o in parts],
                  model='model.blend', asset='asset.blend',
                  status='derived_asset_pending_scene_validation')
    (out / 'metadata.json').write_text(json.dumps(report, indent=2) + '\n')
    print('SCENE_ARCHITECTURE_READY', aid, flush=True)


if __name__ == '__main__':
    for aid in ['glazed_door', 'window']:
        run(aid)
