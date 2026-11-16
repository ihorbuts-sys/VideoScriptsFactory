"""Preserve Tripo rigs, calibrate the cast, and supply local deformation proofs."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
import prepare_creator_tripo as B


def named(armature, suffix):
    return next(bone for bone in armature.pose.bones if bone.name.split(':')[-1] == suffix)


def run(aid):
    refs = P.ROOT.parent
    result = json.loads((refs / 'tripo-cli' / (aid + '-rig-result.json')).read_text())
    assert result['status'] == 'success' and result['credits_consumed'] == 25
    source = Path(result['model_file'])
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    P.clear()
    P.MATS.clear()
    scene = bpy.context.scene
    P.studio(scene)
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 32
    scene.view_layers[0].material_override = None
    scene.render.resolution_x = 640
    scene.render.resolution_y = 900
    before = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = set(scene.objects) - before
    armature = next(o for o in imported if o.type == 'ARMATURE')
    helpers = {bone.custom_shape for bone in armature.pose.bones if bone.custom_shape}
    for helper in helpers:
        helper.hide_render = True
        helper.hide_set(True)
    imported -= helpers
    root = P.empty('Rigged cast / ' + aid)
    for obj in imported:
        if obj.parent not in imported:
            obj.parent = root
    models = [o for o in imported if o.type == 'MESH']
    bpy.context.view_layer.update()
    forward = sum((armature.matrix_world @ named(armature, side + 'ToeBase').head -
                   armature.matrix_world @ named(armature, side + 'Foot').head for side in ['Left', 'Right']), Vector())
    forward.z = 0
    assert forward.length > .005
    root.rotation_euler.z = -math.pi / 2 - math.atan2(forward.y, forward.x)
    lo, hi = B.bounds(models)
    scale = 1.72 / (hi.z - lo.z)
    root.scale = (scale,) * 3
    lo, hi = B.bounds(models)
    root.location -= Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    bpy.context.view_layer.update()
    root['asset_id'] = aid + '_rigged'
    root['canonical_front'] = '-Y'
    root['source_sha256'] = digest
    root['source_geometry_preserved'] = True
    root['facial_rig_status'] = 'Not supplied; local facial preparation still required'
    collection = bpy.data.collections.new('Loca rigged cast / ' + aid)
    scene.collection.children.link(collection)
    for obj in [root, *root.children_recursive]:
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        collection.objects.link(obj)
    collection.asset_mark()
    out = refs / aid / 'tripo-rigged/review'
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.file.pack_all()
    # The appendable asset is neutral; the demonstration belongs only to model.blend.
    bpy.data.libraries.write(str(out / 'asset.blend'), {collection}, fake_user=True, compress=True)
    scene.render.fps = 15
    scene.frame_start = 1
    scene.frame_end = 90
    head = named(armature, 'Head')
    forearm = named(armature, 'RightForeArm')
    world_forearm = armature.matrix_world.to_3x3() @ (forearm.tail - forearm.head)
    elbow_axis = world_forearm.cross(Vector((0, -1, 0))).normalized()
    elbow_basis = (armature.matrix_world @ forearm.bone.matrix_local).to_3x3()
    local_elbow_axis = elbow_basis.inverted() @ elbow_axis
    head_basis = (armature.matrix_world @ head.bone.matrix_local).to_3x3()
    local_head_axis = head_basis.inverted() @ Vector((0, 0, 1))
    neutral_hand = armature.matrix_world @ named(armature, 'RightHand').head
    for frame in range(1, 91):
        u = (frame - 1) / 89
        amount = math.sin(math.pi * u) ** 2
        forearm.rotation_mode = 'QUATERNION'
        forearm.rotation_quaternion = Quaternion(local_elbow_axis, math.radians(28) * amount)
        forearm.keyframe_insert('rotation_quaternion', frame=frame)
        head.rotation_mode = 'QUATERNION'
        head.rotation_quaternion = Quaternion(local_head_axis, math.radians(10) * math.sin(u * math.tau))
        head.keyframe_insert('rotation_quaternion', frame=frame)
    scene.frame_set(46)
    bpy.context.view_layer.update()
    posed_hand = armature.matrix_world @ named(armature, 'RightHand').head
    displacement = (posed_hand - neutral_hand).length
    assert displacement > .03, (aid, displacement)
    P.block('Review floor', (0, 0, -.02), (5, 5, .04), 'cream', .01)
    P.lighting(Vector((0, 0, .9)), 1.3)
    camera = B.camera(scene, (0, 0, .86), (.7, -1.8, .16), 2.06)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
                area.spaces.active.shading.type = 'MATERIAL'
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'model.blend'), compress=True)
    for name, frame in [('neutral', 1), ('elbow-proof', 46)]:
        scene.frame_set(frame)
        scene.render.filepath = str(out / (name + '.png'))
        bpy.ops.render.render(write_still=True)
    scene.frame_set(1)
    camera.location = (1.8, 0, .86)
    camera.rotation_euler = (Vector((0, 0, .86)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(out / 'side.png')
    bpy.ops.render.render(write_still=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    rows = [dict(name=b.name, parent=b.parent.name if b.parent else None,
                 head=list(armature.matrix_world @ b.head), tail=list(armature.matrix_world @ b.tail))
            for b in armature.pose.bones]
    lo, hi = B.bounds(models)
    report = dict(id=aid, status='rigged_local_deformation_proof_ready', source=str(source),
        source_sha256=digest, source_glb_preserved=True, meshes=len(models), bones=len(rows),
        triangles=sum(len(f.vertices) - 2 for o in models for f in o.data.polygons),
        dimensions_m=list(hi - lo), right_hand_displacement_m=displacement,
        credits_consumed=25, local_animation_credits=0, demonstration_frames=90,
        demonstration='Small elbow flex and head turn; not a production grip or facial animation',
        bones_metadata=rows, limitations=['Finger/object contact still requires scene-specific posing.',
            'No facial shape keys or lip sync were added by this body-rig operation.'])
    (out / 'metadata.json').write_text(json.dumps(report, indent=2) + '\n')
    print('RIGGED_CAST_READY', aid, len(rows), displacement, flush=True)


if __name__ == '__main__':
    ids = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['barista', 'creator', 'friend_locs']
    for aid in ids:
        run(aid)
