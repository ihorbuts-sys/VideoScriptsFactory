"""Derive consistent whole and broken pastries from the approved single mesh."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
from prepare_tripo_props import fit_camera


def export(aid, root, models, source_hash, detail):
    out = P.ROOT / aid / 'approved-v2'
    out.mkdir(exist_ok=True)
    collection = bpy.data.collections.new('Loca approved pastry / ' + aid)
    bpy.context.scene.collection.children.link(collection)
    for obj in [root, *root.children_recursive]:
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        collection.objects.link(obj)
    collection.asset_mark()
    root['asset_id'] = aid + '_approved_v2'
    root['source_sha256'] = source_hash
    bpy.ops.file.pack_all()
    bpy.data.libraries.write(str(out / 'asset.blend'), {collection}, fake_user=True, compress=True)
    scene = bpy.context.scene
    P.studio(scene)
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 48
    scene.view_layers[0].material_override = None
    lo, hi = P.bounds(models)
    extent = max(hi - lo)
    P.block('Review floor', (0, 0, -.01), (1, 1, .02), 'cream', .003)
    P.lighting((lo + hi) / 2, extent)
    fit_camera(scene, models, (.65, -1.8, 1.0))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'model.blend'), compress=True)
    scene.render.filepath = str(out / 'preview.png')
    bpy.ops.render.render(write_still=True)
    (out / 'metadata.json').write_text(json.dumps(dict(id=aid, source_sha256=source_hash,
        source_geometry='Approved whole-croissant reconstruction', source_glb_preserved=True,
        local_processing_credits=0, dimensions_m=list(hi - lo), detail=detail,
        status='local_approved_shape_derivative'), indent=2) + '\n')


def main():
    source_file = P.ROOT / 'croissant/tripo-generated/review/model.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source_file))
    source_root = next(o for o in bpy.context.scene.objects if o.get('asset_id') == 'croissant_tripo')
    original = next(o for o in source_root.children_recursive if o.type == 'MESH')
    base = original.data.copy()
    base.transform(original.matrix_world)
    source_hash = source_root['source_sha256']
    # Store a neutral calibrated copy; derived geometry is kept apart from the raw download.
    for aid in ['croissant', 'croissant_oozing']:
        P.clear()
        P.MATS.clear()
        root = P.empty('Approved pastry / ' + aid)
        models = []
        halves = []
        for side in ([0] if aid == 'croissant' else [-1, 1]):
            mesh = base.copy()
            mesh.materials.clear()
            mesh.materials.append(P.material('gold'))
            mesh.materials.append(P.material('cream'))
            obj = bpy.data.objects.new('Pastry / whole' if not side else f'Pastry / half {side}', mesh)
            bpy.context.collection.objects.link(obj)
            group = P.empty('Pastry control / whole' if not side else f'Pastry control / half {side}')
            group.parent = root
            obj.parent = group
            if side:
                bm = bmesh.new()
                bm.from_mesh(mesh)
                bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000003)
                bmesh.ops.bisect_plane(bm, geom=[*bm.verts, *bm.edges, *bm.faces],
                    plane_co=(0, 0, 0), plane_no=(1, 0, 0), clear_outer=side < 0, clear_inner=side > 0)
                result = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
                for face in result.get('faces', []):
                    face.material_index = 1
                bm.normal_update()
                bm.to_mesh(mesh)
                bm.free()
                height = max(v.co.z for v in mesh.vertices)
                # A small flat filling core, flush with the cream section, no raised cream cuff.
                filling = P.ball('Filling / restrained chocolate core', (-side * .001, 0, height * .43),
                                 (.0015, .019, .0035), 'chocolate')
                filling.parent = group
                if side < 0:
                    ooze = P.tube('Filling / short attached ooze', [(.001, -.009, height * .43),
                        (.002, -.010, height * .34), (.003, -.010, height * .27)], .0017, 'chocolate')
                    ooze.parent = group
                group.location.x = side * .012
                group.rotation_euler.z = side * math.radians(35)
                halves.append(group)
            models.append(obj)
        export(aid, root, [o for o in root.children_recursive if o.type == 'MESH'], source_hash,
               'Whole crescent, matte clay palette' if aid == 'croissant' else
               'Exactly two halves of the same whole mesh; flat cream cut faces and a modest chocolate core; one short ooze')
        print('APPROVED_PASTRY_READY', aid, len(halves) if halves else 1, flush=True)


if __name__ == '__main__':
    main()
