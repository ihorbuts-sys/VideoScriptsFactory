"""Local corrections to venue candidates; never resubmit their paid tasks."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector, Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
from prepare_tripo_props import fit_camera
from prepare_scene_architecture import clear_glass


def component_sets(bm):
    seen = set()
    result = []
    for vertex in bm.verts:
        if vertex in seen:
            continue
        stack = [vertex]
        seen.add(vertex)
        group = set()
        while stack:
            current = stack.pop()
            group.add(current)
            for edge in current.link_edges:
                other = edge.other_vert(current)
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        if len(group) > 100:
            result.append(group)
    return result


def run(aid):
    folder = P.ROOT / aid / 'tripo-generated'
    metadata = json.loads((folder / 'review/metadata.json').read_text())
    source = Path(metadata['source'])
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(folder / 'review/model.blend'))
    P.MATS.clear()
    old = next(o for o in bpy.context.scene.objects if o.get('asset_id') == aid + '_tripo')
    raw = next(o for o in old.children_recursive if o.type == 'MESH')
    mesh = raw.data.copy()
    mesh.transform(raw.matrix_world)
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    root = P.empty('Scene-ready / ' + aid)
    root['asset_id'] = aid + '_scene_ready'
    root['source_sha256'] = digest
    changes = []
    objects = []
    if aid == 'croissant_oozing':
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000003)
        layer = bm.verts.layers.int.new('selected_half')
        groups = component_sets(bm)
        assert len(groups) == 4, len(groups)
        keep = sorted([group for group in groups if sum(v.co.y for v in group) / len(group) < 0],
                      key=lambda group: sum(v.co.x for v in group) / len(group))
        assert len(keep) == 2
        for i, group in enumerate(keep):
            for vertex in group:
                vertex[layer] = i + 1
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v[layer] == 0], context='VERTS')
        low_y = min(v.co.y for v in bm.verts)
        high_y = max(v.co.y for v in bm.verts)
        for vertex in bm.verts:
            vertex.co.y -= (low_y + high_y) / 2
            vertex.co = Matrix.Rotation(math.pi, 4, 'Z') @ vertex.co
        for half in [1, 2]:
            copy = bm.copy()
            tag = copy.verts.layers.int.get('selected_half')
            bmesh.ops.delete(copy, geom=[v for v in copy.verts if v[tag] != half], context='VERTS')
            data = bpy.data.meshes.new('Pastry / equal half ' + str(half))
            copy.to_mesh(data)
            copy.free()
            for material in mesh.materials:
                data.materials.append(material)
            obj = bpy.data.objects.new(data.name, data)
            bpy.context.collection.objects.link(obj)
            obj.parent = root
            obj['pastry_half'] = half
            objects.append(obj)
        bm.free()
        changes.append('Removed two duplicated rear islands; retained exactly two natural front halves and filling, with original UVs.')
    else:
        obj = bpy.data.objects.new(aid + ' / cleaned mesh', mesh)
        bpy.context.collection.objects.link(obj)
        obj.parent = root
        objects.append(obj)
        if aid == 'bar_stool':
            high = max(v.co.z for v in mesh.vertices)
            upper = [v.co for v in mesh.vertices if v.co.z > high * .78]
            centre_y = sum(v.y for v in upper) / len(upper)
            if centre_y < 0:
                mesh.transform(Matrix.Rotation(math.pi, 4, 'Z'))
                centre_y = -centre_y
                changes.append('Rotated stool to canonical front -Y; backrest lies behind the seat at +Y.')
            assert centre_y > .03
        elif aid == 'drinking_glass':
            high = max(v.co.z for v in mesh.vertices)
            radii = sorted(math.hypot(v.co.x, v.co.y) for v in mesh.vertices if high * .2 < v.co.z < high * .6)
            radius = radii[len(radii) // 2]
            bpy.data.objects.remove(obj, do_unlink=True)
            body = P.lathe('Glass / cleaned rotational contour', [(0, 0), (.85 * radius, 0),
                (radius, .004), (1.01 * radius, high * .90), (radius, high * .98),
                (.94 * radius, high), (.88 * radius, high * .97),
                (.87 * radius, high * .20), (.74 * radius, high * .12), (0, high * .12)], c='glass')
            body.data.materials.clear()
            body.data.materials.append(clear_glass())
            fill = P.lathe('Glass / separate amber liquid', [(0, high * .13), (.84 * radius, high * .13),
                (.855 * radius, high * .72), (0, high * .72)], c='coffee')
            body.parent = root
            fill.parent = root
            objects = [body, fill]
            changes.append('Rebuilt a clean rotational contour from the generated tumbler height and median side-wall radius, removing invented label geometry and texture. Separate clear shell and amber liquid; no paid regeneration.')
    collection = bpy.data.collections.new('Loca scene-ready / ' + aid)
    bpy.context.scene.collection.children.link(collection)
    for obj in [root, *root.children_recursive]:
        for old_collection in list(obj.users_collection):
            old_collection.objects.unlink(obj)
        collection.objects.link(obj)
    collection.asset_mark()
    out = folder / 'scene-ready'
    out.mkdir(exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.data.libraries.write(str(out / 'asset.blend'), {collection}, fake_user=True, compress=True)
    scene = bpy.context.scene
    P.studio(scene)
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 48
    scene.view_layers[0].material_override = None
    lo, hi = P.bounds(objects)
    P.lighting((lo + hi) / 2, max(hi - lo))
    extent = max(hi - lo)
    P.block('Review floor', (0, 0, -extent * .02), (extent * 5, extent * 5, extent * .04), 'cream', extent * .005)
    camera = fit_camera(scene, objects, (.9, -1.7, 1.05))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'model.blend'), compress=True)
    scene.render.filepath = str(out / 'preview.png')
    bpy.ops.render.render(write_still=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    report = dict(id=aid, status='locally_corrected_scene_candidate', source_sha256=digest,
                  source_glb_preserved=True, extra_api_credits=0, changes=changes,
                  parts=[o.name for o in objects], bounds_min=list(lo), bounds_max=list(hi))
    (out / 'metadata.json').write_text(json.dumps(report, indent=2) + '\n')
    print('VENUE_CLEANUP_READY', aid, flush=True)


if __name__ == '__main__':
    for aid in ['croissant_oozing', 'bar_stool', 'drinking_glass']:
        run(aid)
